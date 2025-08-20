"""Extended AST parse and convert `Code` to `FST`.

The parse functions in this module are oriented towards parsing all valid elements which they name which may include
parsing things which are not those elements, common sense is applied liberally though. And just because an element is
parsed successfully doesn't mean it may not need parentheses if used in the way intended. Or that it needs a trailing
newline due to comment ending without an explicit trailing newline.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

import re
from ast import parse as ast_parse, unparse as ast_unparse, fix_missing_locations as ast_fix_missing_locations
from typing import Any, Callable, Mapping, get_args
from unicodedata import normalize

from . import fst

from .asttypes import (
    AST,
    Assign,
    AugAssign,
    BinOp,
    BoolOp,
    Compare,
    Constant,
    Del,
    ExceptHandler,
    Expr,
    Expression,
    GeneratorExp,
    Interactive,
    IsNot,
    ListComp,
    Load,
    MatchOr,
    MatchSequence,
    Module,
    Name,
    NotIn,
    Pass,
    Slice,
    Starred,
    Store,
    Tuple,
    UnaryOp,
    alias,
    arg,
    arguments,
    boolop,
    cmpop,
    comprehension,
    expr,
    keyword,
    match_case,
    mod,
    operator,
    pattern,
    stmt,
    unaryop,
    withitem,
    TryStar,
    type_param,
)

from .astutil import (
    constant, pat_alnum, bistr,
    OPSTR2CLS_UNARY, OPSTR2CLS_BIN, OPSTR2CLS_CMP, OPSTR2CLS_BOOL, OPSTR2CLS_AUG, OPCLS2STR_AUG, OPCLS2STR,
    is_valid_identifier, is_valid_identifier_dotted, is_valid_identifier_star, is_valid_identifier_alias,
    walk, reduce_ast,
)

from .misc import (
    Code, Mode, NodeError, _next_src, _shortstr
)


class ParseError(SyntaxError):
    """Not technically a syntax error but mostly not the code we were expecting."""


_re_trailing_comma     = re.compile(r'(?: [)\s]* (?: (?: \\ | \#[^\n]* ) \n )? )* ,', re.VERBOSE)  # trailing comma search ignoring comments and line continuation backslashes

_re_first_src          = re.compile(r'^([^\S\n]*)([^\s\\#]+)', re.MULTILINE)  # search for first non-comment non-linecont source code
_re_parse_all_category = re.compile(r'''
    (?P<stmt>                          (?: assert | break | class | continue | def | del | from | global | import | nonlocal | pass | raise | return | try | while | with ) \b ) |
    (?P<await_lambda_yield>            (?: await | lambda | yield ) \b ) |
    (?P<True_False_None>               (?: True | False | None ) \b ) |
    (?P<async_or_for>                  (?: async | for ) \b ) |
    (?P<if>                            (?: if ) \b ) |
    (?P<except>                        (?: except ) \b ) |
    (?P<case>                          (?: case ) \b ) |
    (?P<not>                           (?: not ) \b ) |
    (?P<boolop>                        (?: and | or ) \b ) |
    (?P<cmpop_w>                       (?: is | in ) \b ) |
    (?P<syntax_error>                  (?: elif | else | finally | as ) \b ) |
    (?P<match_type_identifier>         (?: match | type | [^\d\W][''' + pat_alnum + r''']* ) \b ) |
    (?P<stmt_or_expr_or_pat_or_witem>  (?: [(\[{"'.\d] ) ) |
    (?P<augop>                         (?: \+= | -= | @= | \*= | /= | %= | <<= | >>= | \|= | \^= | &= | //= | \*\*= ) ) |
    (?P<minus>                         (?: - ) ) |
    (?P<starstar>                      (?: \*\* ) ) |
    (?P<star>                          (?: \* ) ) |
    (?P<at>                            (?: @ ) ) |
    (?P<operator>                      (?: // | / | % | << | >> | \| | \^ | & ) ) |
    (?P<plus>                          (?: \+ ) ) |
    (?P<colon>                         (?: : ) ) |
    (?P<cmpop_o>                       (?: == | != | <= | < | >= | > ) ) |
    (?P<tilde>                         (?: ~ ) )
''', re.MULTILINE | re.VERBOSE)


def _ast_parse(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Python craps out with unexpected EOF if you only have a single newline after a line continuation backslash."""

    return ast_parse(src + '\n' if src.endswith('\\\n') else src, **parse_params)


def _ast_parse1(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    if len(body := ast_parse(src + '\n' if src.endswith('\\\n') else src, **parse_params).body) != 1:
        raise SyntaxError('expecting single element')

    return body[0]


def _ast_parse1_case(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    if (len(body := ast_parse(src + '\n' if src.endswith('\\\n') else src, **parse_params).body) != 1 or
        len(cases := body[0].cases) != 1
    ):
        raise SyntaxError('expecting single element')

    return cases[0]


def _fixing_unparse(ast: AST) -> str:
    try:
        return ast_unparse(ast)

    except AttributeError as exc:
        if not str(exc).endswith("has no attribute 'lineno'"):
            raise

    ast_fix_missing_locations(ast)

    return ast_unparse(ast)


# def _validate_indent(src: str, ret: Any = None) -> Any:
#     if (m := _re_first_src_or_lcont.search(src)) and len(m.group(0)) > 1:
#         raise IndentationError('unexpected indent')

#     return ret


def _offset_linenos(ast: AST, delta: int) -> AST:
    for a in walk(ast):
        if end_lineno := getattr(a, 'end_lineno', None):
            a.end_lineno  = end_lineno + delta
            a.lineno     += delta

    return ast


def _fix_unparenthesized_tuple_parsed_parenthesized(src: str, ast: AST) -> None:
    elts           = ast.elts
    ast.lineno     = (e0 := elts[0]).lineno
    ast.col_offset = e0.col_offset
    lines          = src.split('\n')
    end_ln         = (e_1 := elts[-1]).end_lineno - 2  # -2 because of extra line introduced in parse
    end_col        = len(lines[end_ln].encode()[:e_1.end_col_offset].decode())  # bistr(lines[end_ln]).b2c(e_1.end_col_offset)

    if (not (code := _next_src(lines, end_ln, end_col, ast.end_lineno - 3, 0x7fffffffffffffff)) or  # if nothing following then last element is ast end, -3 because end also had \n tacked on
        not code.src.startswith(',')  # if no comma then last element is ast end
    ):
        ast.end_lineno     = e_1.end_lineno
        ast.end_col_offset = e_1.end_col_offset

    else:
        end_ln, end_col, _ = code
        ast.end_lineno     = end_ln + 2
        ast.end_col_offset = len(lines[end_ln][:end_col + 1].encode())


def _has_trailing_comma(src: str, end_lineno: int, end_col_offset: int) -> bool:
    pos = 0

    for _ in range(end_lineno - 1):
        pos = src.find('\n', pos) + 1  # assumed to all be there

    pos += len(src[pos : pos + end_col_offset].encode()[:end_col_offset].decode())

    return bool(_re_trailing_comma.match(src, pos))


def _parse_all_type_params(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse either a single `type_param` preferentially or multiple `type_param`s returned in `Tuple`. Called from
    `_parse_all()` on finding a leading identifier character or star so that is assumed to be there, which will generate
    at least one `type_param`."""

    type_params = _ast_parse1(f'type t[\n{src}\n] = None', parse_params).type_params

    ast = type_params[0]

    if len(type_params) > 1 or _has_trailing_comma(src, ast.end_lineno - 1, ast.end_col_offset):
        ast = Tuple(elts=type_params, ctx=Load(), lineno=2, col_offset=0, end_lineno=2 + src.count('\n'),
                    end_col_offset=len((src if (i := src.rfind('\n')) == -1 else src[i + 1:]).encode()))

    return _offset_linenos(ast, -1)  # _offset_linenos(_validate_indent(src, ast), -1)


def _parse_all_multiple(src: str, parse_params: Mapping[str, Any], stmt: bool, rest: list[Callable]) -> AST:
    """Attempt to parse one at a time using functions from a list until one succeeds."""

    if stmt:
        try:
            return reduce_ast(_parse_stmts(src, parse_params), True)
        except SyntaxError:  # except IndentationError: raise  # before if checking that
            pass

    for parse in rest:
        try:
            return parse(src, parse_params)
        except SyntaxError:  # except IndentationError: raise  # before if checking that
            pass

    raise ParseError('invalid syntax')


def _code_as_op(code: Code, ast_type: type[AST], parse_params: Mapping[str, Any],
                parse: Callable[[fst.FST, Code], fst.FST],
                opstr2cls: dict[str, type[AST]], opcls2str: dict[type[AST], str] = OPCLS2STR) -> fst.FST:
    """Convert `code` to an operation `FST` if possible."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if not isinstance(codea, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {codea.__class__.__name__}', rawable=True)

        code = code._sanitize()

        if (src := code.src) != (expected := opcls2str[codea.__class__]):
            if isinstance(codea, (NotIn, IsNot)):  # super-stupid case, someone did 'is # comment \n not' or something like this?
                if _parse_cmpop(src).__class__ is codea:  # parses to same thing so just return the canonical str for the op, otherwise it gets complicated
                    return fst.FST(codea, [bistr(expected)], from_=code, lcopy=False)

            raise NodeError(f'expecting {expected!r}, got {_shortstr(src)!r}', rawable=True)

        return code

    if isinstance(code, AST):
        if not isinstance(code, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}', rawable=True)

        return fst.FST(code, [opcls2str[code.__class__]], parse_params=parse_params)

    if isinstance(code, list):
        code = '\n'.join(code)

    lines = (code := code.strip()).split('\n')

    if cls := opstr2cls.get(code):
        return fst.FST(cls(), lines, parse_params=parse_params)

    try:
        return fst.FST(parse(code, parse_params), lines, parse_params=parse_params)  # fall back to actually trying to parse the thing
    except SyntaxError:  # except IndentationError: raise  # before if checking that
        raise ParseError(f'expecting {ast_type.__name__}, got {_shortstr(code)!r}') from None


def _code_as(code: Code, ast_type: type[AST], parse_params: Mapping[str, Any],
             parse: Callable[[fst.FST, Code], fst.FST], *, sanitize: bool = True) -> fst.FST:
    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(code.a, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.a.__class__.__name__}', rawable=True)

        return code._sanitize() if sanitize else code

    if is_ast := isinstance(code, AST):
        if not isinstance(code, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}', rawable=True)

        src   = _unparse(code)
        lines = src.split('\n')

    elif isinstance(code, list):
        src = '\n'.join(lines := code)
    else:  # str
        lines = (src := code).split('\n')

    ast = parse(src, parse_params)

    if is_ast:
        if ast.__class__ is not code.__class__:
            raise ParseError(f'could not reparse AST to {code.__class__.__name__}, got {ast.__class__.__name__}')

    elif not isinstance(ast, ast_type):  # sanity check, parse func should guarantee what we want but maybe in future is used to get a specific subset of what parse func returns
        raise ParseError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}')

    fst_ = fst.FST(ast, lines, parse_params=parse_params)

    return fst_._sanitize() if sanitize else fst_


# ----------------------------------------------------------------------------------------------------------------------
# FST class private methods

@staticmethod
def _get_special_parse_mode(ast: AST) -> str | None:
    r"""Quick determination to the best of ability if a special parse mode is needed for this `AST`. This is the
    extended parse mode as per `Mode`, not the `ast.parse()` mode. If a special mode applies it is returned which should
    parse the source of this `AST` back to itself. Otherwise `None` is returned. This is a just quick a check, doesn't
    verify everything.

    **WARNING!** This only gets special parse modes for where it can be inferred from the `AST` alone. This will not
    return the special parse mode of `'expr_slice'` for example for `(*st,)` single-`Starred` `Tuple` which is
    represented by the source `*st` from inside a `Subscript.slice`. That must be handled at a higher level.

    **Returns:**
    - `str`: One of the special parse modes.
    - `None`: If no special parse mode applies or can be determined.
    """

    # SPECIAL SLICES

    if isinstance(ast, Module):
        if body := ast.body:
            if isinstance(b0 := body[0], ExceptHandler):
                return 'ExceptHandlers'
            elif isinstance(b0, match_case):
                return 'match_cases'

    elif isinstance(ast, Tuple):
        if elts := ast.elts:
            if isinstance(elts[0], type_param):
                return 'type_params'

    elif isinstance(ast, Assign):
        if isinstance(v := ast.value, Name) and not v.id:
            return 'Assign_targets'

    return None


@staticmethod
def _unparse(ast: AST) -> str:
    """AST unparse that handles misc case of comprehension starting with a single space by stripping it as well as
    removing parentheses from `Tuple`s with `Slice`s or special slice (our own) `Tuple`s."""

    src = _fixing_unparse(ast)

    if not src:
        if s := OPCLS2STR.get(ast.__class__):  # operators don't unparse to anything in ast
            return s

    if isinstance(ast, Tuple):
        if any(isinstance(e, Slice) or not isinstance(e, expr) for e in ast.elts):  # tuples with Slices cannot have parentheses, and neither can our own SPECIAL SLICES
            return src[1:-1]

    elif isinstance(ast, comprehension):  # strip prefix space from this
        return src.lstrip()

    return src


@staticmethod
def _parse(src: str, mode: Mode = 'all', parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse any source to an AST, including things which normal `ast.parse()` doesn't handle, like individual
    `comprehension`s. Can be given a target type to parse or else will try to various parse methods until it finds one
    that succeeds (if any).

    **WARNING!** Does not guarantee `src` can be plugged directly into a node of the type it is being parsed for without
    parentheses (especially for `Tuple`s).

    **Parameters**:
    - `src`: The source to parse.
    - `mode`: Either one of the standard `ast.parse()` modes `exec`, `eval` or `single` to parse to that type of module
        or one of our specific strings like `'ExceptHandlers'` or an actual `AST` type to parse to. If the mode is
        provided and cannot parse to the specified target then an error is raised and no other parse types are tried.
        See `fst.misc.Mode`.
    - `parse_params`: Dictionary of optional parse parameters to pass to `ast.parse()`, can contain `filename`,
        `type_comments` and `feature_version`.
    """

    if parse := _PARSE_MODE_FUNCS.get(mode):
        return parse(src, parse_params)

    if not isinstance(mode, type) or not issubclass(mode, AST):
        raise ValueError(f'invalid parse mode {mode!r}')

    mode_ = mode

    while (mode_ := mode_.__bases__[0]) is not AST:
        if parse := _PARSE_MODE_FUNCS.get(mode_):
            if isinstance(ast := parse(src, parse_params), mode):
                return ast

            raise ParseError(f'could not parse to {mode.__name__}, got {ast.__class__.__name__}')

    raise ParseError(f'could not parse to {mode.__name__}')


@staticmethod
def _parse_all(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """All parse modes. Get a hint from starting source and attempt parse according to that from most probable to least
    of what it could be."""

    if not (first := _re_first_src.search(src)):
        return _ast_parse(src, parse_params)  # should return empty Module with src trivia

    if not (cat := _re_parse_all_category.match(first.group(2))):
        _ast_parse(src, parse_params)  # should raise SyntaxError

        raise RuntimeError('should not get here')

    groupdict = cat.groupdict()

    if groupdict['stmt_or_expr_or_pat_or_witem']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (_parse_expr_all, _parse_pattern, _parse_withitem, _parse_Assign_targets))  # _parse_expr_all because could be Slice

    if groupdict['match_type_identifier']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (_parse_expr_all, _parse_pattern, _parse_arguments, _parse_arguments_lambda,
                                    _parse_withitem, _parse_arg, _parse_all_type_params, _parse_Assign_targets))

    if groupdict['stmt']:
        return reduce_ast(_parse_stmts(src, parse_params), True)

    if groupdict['True_False_None']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (_parse_expr_all, _parse_pattern, _parse_withitem))

    if groupdict['async_or_for']:
        return _parse_all_multiple(src, parse_params, not first.group(1), (_parse_comprehension,))

    if groupdict['await_lambda_yield']:
        return _parse_all_multiple(src, parse_params, not first.group(1), (_parse_expr_all,))

    if groupdict['if']:
        return reduce_ast(_parse_stmts(src, parse_params), True)

    if groupdict['except']:
        return reduce_ast(_parse_ExceptHandlers(src, parse_params), True)

    if groupdict['case']:
        try:
            return reduce_ast(_parse_match_cases(src, parse_params), True)
        except SyntaxError:  # except IndentationError: raise  # before if checking that
            pass

        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (_parse_expr_all, _parse_pattern, _parse_arguments, _parse_arguments_lambda,
                                    _parse_withitem, _parse_arg, _parse_all_type_params, _parse_Assign_targets))

    if groupdict['at']:
        return reduce_ast(_parse_stmts(src, parse_params), True)

    if groupdict['star']:
        ast = _parse_all_multiple(src, parse_params, not first.group(1),
                                  (_parse_expr_arglike, _parse_pattern, _parse_arguments, _parse_arguments_lambda,
                                   _parse_all_type_params, _parse_operator, _parse_Assign_targets))

        if isinstance(ast, Assign) and len(targets := ast.targets) == 1 and isinstance(targets[0], Starred):  # '*T = ...' validly parses to Assign statement but is invalid compile, but valid type_param so reparse as that
            return _parse_all_type_params(src, parse_params)

        return ast

    if groupdict['minus']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (_parse_expr_all, _parse_pattern, _parse_withitem, _parse_binop))

    if groupdict['not']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (_parse_expr_all, _parse_withitem, _parse_unaryop, _parse_cmpop))

    if groupdict['tilde']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (_parse_expr_all, _parse_withitem, _parse_unaryop))

    if groupdict['colon']:
        return _parse_all_multiple(src, parse_params, False, (_parse_expr_all,))

    if groupdict['starstar']:
        return _parse_all_multiple(src, parse_params, False, (_parse_arguments, _parse_arguments_lambda,
                                                              _parse_all_type_params, _parse_operator))

    if groupdict['plus']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (_parse_expr_all, _parse_withitem, _parse_binop))

    if groupdict['cmpop_w']:
        return _parse_cmpop(src, parse_params)

    if groupdict['cmpop_o']:
        return _parse_cmpop(src, parse_params)

    if groupdict['boolop']:
        return _parse_boolop(src, parse_params)

    if groupdict['augop']:
        return _parse_augop(src, parse_params)

    if groupdict['operator']:
        return _parse_operator(src, parse_params)

    # groupdict['syntax_error'] or something else unrecognized

    _ast_parse(src, parse_params)  # should raise SyntaxError

    raise RuntimeError('should not get here')


@staticmethod
def _parse_strict(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Attempt to parse valid parsable statements and then reduce to a single statement or expressing if possible. Only
    parses what `ast.parse()` can, no funny stuff."""

    return reduce_ast(_ast_parse(src, parse_params), True)


@staticmethod
def _parse_Module(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Module`, ast.parse(mode='exec')'."""

    return _ast_parse(src, parse_params)


@staticmethod
def _parse_Expression(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Expression`, `ast.parse(mode='eval')."""

    return _ast_parse(src, {**parse_params, 'mode': 'eval'})


@staticmethod
def _parse_Interactive(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Interactive`."""

    if not src.endswith('\n'):  # because otherwise error maybe
        src = src + '\n'

    return _ast_parse(src, {**parse_params, 'mode': 'single'})


@staticmethod
def _parse_stmts(src: str, parse_params: Mapping[str, Any] = {}) -> AST:  # same as _parse_Module() but I want the IDE context coloring
    """Parse zero or more `stmt`s and return them in a `Module` `body` (just `ast.parse()` basically)."""

    return _ast_parse(src, parse_params)


@staticmethod
def _parse_stmt(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `stmt` and return as itself."""

    mod = _ast_parse(src, parse_params)

    if len(body := mod.body) != 1:
        raise ParseError('expecting single stmt')

    return body[0]


@staticmethod
def _parse_ExceptHandler(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `ExceptHandler` and return as itself."""

    mod = _parse_ExceptHandlers(src, parse_params)

    if len(body := mod.body) != 1:
        raise ParseError('expecting single ExceptHandler')

    return body[0]


@staticmethod
def _parse_ExceptHandlers(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `ExceptHandler`s and return them in a `Module` `body`."""

    try:
        ast = _ast_parse1(f'try: pass\n{src}\nfinally: pass', parse_params)
    except IndentationError:
        raise

    except SyntaxError:
        if (m := _re_first_src.search(src)) and m.group(1):
            raise IndentationError('unexpected indent') from None

        try:
            ast = _ast_parse(f'try: pass\n{src}', parse_params)  # just reparse without our finally block to confirm if that was the error
        except SyntaxError:
            pass

        else:
            if len(ast.body) == 1:
                raise ParseError("not expecting 'finally' block") from None
            else:
                raise ParseError('expecting only exception handlers`') from None

        raise

    if ast.orelse:
        raise ParseError("not expecting 'else' block")

    return Module(body=_offset_linenos(ast, -1).handlers, type_ignores=[])


@staticmethod
def _parse_match_case(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `match_case` and return as itself."""

    mod = _parse_match_cases(src, parse_params)

    if len(body := mod.body) != 1:
        raise ParseError('expecting single match_case')

    return body[0]


@staticmethod
def _parse_match_cases(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `match_case`s and return them in a `Module` `body`."""

    lines = [bistr('match x:'), bistr(' case None: pass')] + [bistr(' ' + l) for l in src.split('\n')]
    ast   = _ast_parse1('\n'.join(lines), parse_params)
    fst_  = fst.FST(ast, lines, parse_params=parse_params, lcopy=False)
    lns   = fst_._get_indentable_lns(2, docstr=False)

    if len(lns) != len(lines) - 2:  # if there are multiline strings then we need to dedent them and reparse, because of f-strings, TODO: optimize out second reparse if no f-strings
        strlns = set(range(2, len(lines)))

        strlns.difference_update(lns)

        for ln in strlns:
            lines[ln] = bistr(lines[ln][1:])

        ast  = _ast_parse1('\n'.join(lines), parse_params)
        fst_ = fst.FST(ast, lines, parse_params=parse_params, lcopy=False)

    lns_ = set()

    for ln in lns:
        lines[ln] = bistr(lines[ln][1:])

        lns_.add(ln - 1)

    for a in walk(ast):
        del a.f  # remove all trace of FST

        if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
            a.lineno     = lineno     = a.lineno - 2
            a.end_lineno = end_lineno = a.end_lineno - 2

            if lineno in lns_:
                a.col_offset -= 1

            if end_lineno in lns_:
                a.end_col_offset = end_col_offset - 1

    return Module(body=ast.cases[1:], type_ignores=[])


@staticmethod
def _parse_expr(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a "standard" `ast.expr`, only things which are normally valid in an `expr` location, no `Slices` or
    `Starred` expressions which are only valid as a `Call` arg (`*not a`)."""

    try:
        body = _ast_parse(src, parse_params).body
    except SyntaxError:
        pass
    else:
        if len(body) == 1 and isinstance(ast := body[0], Expr):  # if parsed to single expression then done
            return ast.value

    try:
        ast = _ast_parse1(f'(\n{src}\n)', parse_params).value  # has newlines or indentation

    except SyntaxError:
        try:
            elts = _ast_parse1(f'(\n{src}\n,)', parse_params).value.elts  # Starred expression with newlines or indentation
        except SyntaxError:
            raise SyntaxError('invalid expression') from None

        ast = elts[0]

        assert isinstance(ast, Starred) and len(elts) == 1

    else:
        if isinstance(ast, GeneratorExp) and ast.lineno == 1 and ast.col_offset == 0:  # wrapped something that looks like a GeneratorExp and turned it into that, bad
            raise SyntaxError('expecting expression, got unparenthesized GeneratorExp')

        if isinstance(ast, Tuple) and ast.lineno == 1:  # tuple with newlines included grouping pars which are not in source, fix
            if not ast.elts:
                raise SyntaxError('expecting expression')

            _fix_unparenthesized_tuple_parsed_parenthesized(src, ast)  # we have to do some work to find a possible comma

    return _offset_linenos(ast, -1) # _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_expr_all(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to any kind of expression including `Slice`, `*not a` or `Tuple` of any of those combined. Lone `*a`
    `Starred` is returned as a `Starred` and not `Tuple` as would be in a slice."""

    try:
        ast = _parse_expr_slice(src, parse_params)

    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11  # except IndentationError: raise  # before if checking that
        try:
            ast = _parse_expr_arglike(src, parse_params)  # expr_arglike instead of expr because py 3.10 won't pick up `*not a` in a slice above
        except SyntaxError:
            raise SyntaxError('invalid expression (all types)') from None

    else:
        if (isinstance(ast, Tuple) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and  # check for '*starred' acting as '*starred,'
            e0.end_col_offset == ast.end_col_offset and e0.end_lineno == ast.end_lineno
        ):
            return e0

    return ast


@staticmethod
def _parse_expr_arglike(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `expr` or in the context of a `Call.args` which treats `Starred` differently."""

    try:
        return _parse_expr(src, parse_params)
    except SyntaxError:  # stuff like '*[] or []'  # except IndentationError: raise  # before if checking that
        pass

    value = _ast_parse1(f'f(\n{src}\n)', parse_params).value
    args  = value.args

    if len(args) != 1 or value.keywords:
        raise ParseError('expecting single call argument expression')

    ast = args[0]

    if isinstance(ast, GeneratorExp):  # wrapped something that looks like a GeneratorExp and turned it into that, bad
        raise ParseError('expecting call argument expression, got unparenthesized GeneratorExp')

    return _offset_linenos(ast, -1) # _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_expr_slice(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.Slice` or anything else that can go into `Subscript.slice` (`expr`), e.g. "start:stop:step" or
    "name" or even "a:b, c:d:e, g". Using this, naked `Starred` expressions parse to single element `Tuple` with the
    `Starred` as the only element."""

    try:
        ast = _ast_parse1(f'a[\n{src}\n]', parse_params).value.slice

    except SyntaxError:  # maybe 'yield', also could be unparenthesized 'tuple' containing 'Starred' on py 3.10
        try:
            ast = _ast_parse1(f'a[(\n{src}\n)]', parse_params).value.slice
        except SyntaxError:
            raise SyntaxError('invalid slice expression') from None

        if isinstance(ast, GeneratorExp):  # wrapped something that looks like a GeneratorExp and turned it into that, bad
            raise SyntaxError('expecting slice expression, got unparenthesized GeneratorExp') from None

        if isinstance(ast, Tuple):  # only py 3.10 because otherwise the parse above would have gotten it
            if ast.elts:
                raise SyntaxError('cannot have unparenthesized tuple containing Starred in slice') from None

            raise SyntaxError('expecting slice expression') from None

    return _offset_linenos(ast, -1) # _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_expr_sliceelt(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an element of a slice `Tuple`, an `ast.expr` or `ast.Slice`. This exists because otherwise a naked
    `Starred` expression parses to an implicit single element `Tuple` and the caller of this function does not want that
    behavior. Using this, naked `Starred` expressions parse to just the `Starred` and not a `Tuple` like in
    `_parse_expr_slice()`. Does not allow a `Tuple` with `Slice` in it as it is expected that this expression is already
    in a slice `Tuple` and that is not allowed in python.

    TODO: This can currently return `*not a, *a or b` as valid which are not valid normal tuples (nested as sliceelt).
    """

    try:
        ast = _parse_expr_slice(src, parse_params)

    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11  # except IndentationError: raise  # before if checking that
        return _parse_expr(src, parse_params)

    if isinstance(ast, Tuple) and any(isinstance(e, Slice) for e in ast.elts):
        raise SyntaxError('Slice not allowed in nested slice tuple')

    if (isinstance(ast, Tuple) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and  # check for '*starred' acting as '*starred,'
        e0.end_col_offset == ast.end_col_offset and e0.end_lineno == ast.end_lineno
    ):
        return e0

    return ast


@staticmethod
def _parse_Tuple(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `Tuple` which may or may not contain `Slice`s and otherwise invalid syntax in normal `Tuple`s like
    `*not a` (if not parenthesized)."""

    try:
        ast        = _parse_expr_slice(src, parse_params)
        from_slice = True

    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11  # except IndentationError: raise  # before if checking that
        try:
            ast = _parse_expr(src, parse_params)
        except SyntaxError:
            raise SyntaxError('invalid tuple') from None

        from_slice = False

    if not isinstance(ast, Tuple):
        raise ParseError(f'expecting Tuple, got {ast.__class__.__name__}')

    if (from_slice and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and  # check for '*starred' acting as '*starred,'
        e0.end_col_offset == ast.end_col_offset and e0.end_lineno == ast.end_lineno
    ):
        raise ParseError('expecting Tuple, got Starred')

    return ast


@staticmethod
def _parse_boolop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.boolop`."""

    ast = _ast_parse1(f'(a\n{src}\nb)', parse_params).value

    if not isinstance(ast, BoolOp):
        raise ParseError(f'expecting boolop, got {_shortstr(src)!r}')

    return ast.op.__class__()  # _validate_indent(src, ast.op.__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_operator(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.boolop`."""

    if '=' in src:
        try:
            return _parse_augop(src, parse_params)
        except ParseError:  # maybe the '=' was in a comment, yes I know, a comment in an operator, people do strange things
            pass

    return _parse_binop(src, parse_params)


@staticmethod
def _parse_binop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.operator` in the context of a `BinOp`."""

    ast = _ast_parse1(f'(a\n{src}\nb)', parse_params).value

    if not isinstance(ast, BinOp):
        raise ParseError(f'expecting operator, got {_shortstr(src)!r}')

    return ast.op.__class__()  # _validate_indent(src, ast.op.__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_augop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an augmented `ast.operator` in the context of a `AugAssign`."""

    ast = _ast_parse1(f'a \\\n{src} b', parse_params)

    if not isinstance(ast, AugAssign):
        raise ParseError(f'expecting augmented operator, got {_shortstr(src)!r}')

    return ast.op.__class__()  # _validate_indent(src, ast.op.__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_unaryop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.unaryop`."""

    ast = _ast_parse1(f'(\n{src}\nb)', parse_params).value

    if not isinstance(ast, UnaryOp):
        raise ParseError(f'expecting unaryop, got {_shortstr(src)!r}')

    return ast.op.__class__()  # _validate_indent(src, ast.op.__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_cmpop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.cmpop`."""

    ast = _ast_parse1(f'(a\n{src}\nb)', parse_params).value

    if not isinstance(ast, Compare):
        raise ParseError(f'expecting cmpop, got {_shortstr(src)!r}')

    if len(ops := ast.ops) != 1:
        raise ParseError('expecting single cmpop')

    return ops[0].__class__()  # _validate_indent(src, ops[0].__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_comprehension(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.comprehension`, e.g. "async for i in something() if i"."""

    ast = _ast_parse1(f'[_ \n{src}\n]', parse_params).value

    if not isinstance(ast, ListComp):
        raise ParseError('expecting comprehension')

    if len(gens := ast.generators) != 1:
        raise ParseError('expecting single comprehension')

    return _offset_linenos(gens[0], -1)  # _offset_linenos(_validate_indent(src, gens[0]), -1)


@staticmethod
def _parse_arguments(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.arguments`, e.g. "a: list[str], /, b: int = 1, *c, d=100, **e"."""

    ast = _ast_parse1(f'def f(\n{src}\n): pass', parse_params).args

    return _offset_linenos(ast, -1) # _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_arguments_lambda(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.arguments` for a `Lambda`, e.g. "a, /, b, *c, d=100, **e"."""

    ast = _ast_parse1(f'(lambda \n{src}\n: None)', parse_params).value.args

    return _offset_linenos(ast, -1) # _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_arg(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.arg`, e.g. "var: list[int]"."""

    try:
        args = _ast_parse1(f'def f(\n{src}\n): pass', parse_params).args

    except SyntaxError:  # may be '*vararg: *starred'  # except IndentationError: raise  # before if checking that
        try:
            args = _ast_parse1(f'def f(*\n{src}\n): pass', parse_params).args
        except SyntaxError:
            raise SyntaxError('invalid arg') from None

        if args.posonlyargs or args.args or args.kwonlyargs or args.defaults or args.kw_defaults or args.kwarg:
            ast = None
        else:
            ast = args.vararg

    else:
        if (args.posonlyargs or args.vararg or args.kwonlyargs or args.defaults or args.kw_defaults or args.kwarg or
            len(args := args.args) != 1
        ):
            ast = None
        else:
            ast = args[0]

    if ast is None:
        raise ParseError('expecting single argument without default')

    return _offset_linenos(ast, -1) # _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_keyword(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.keyword`, e.g. "var=val"."""

    keywords = _ast_parse1(f'f(\n{src}\n)', parse_params).value.keywords

    if len(keywords) != 1:
        raise ParseError('expecting single keyword')

    return _offset_linenos(keywords[0], -1)  # _offset_linenos(_validate_indent(src, keywords[0]), -1)


@staticmethod
def _parse_alias(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.alias`, allowing star or dotted notation, e.g. "name as alias"."""

    if '*' in src:
        try:
            return _parse_alias_star(src, parse_params)
        except SyntaxError:  # except IndentationError: raise  # before if checking that
            pass

    return _parse_alias_dotted(src, parse_params)


@staticmethod
def _parse_alias_dotted(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.alias`, allowing dotted notation (not all aliases are created equal),,
    e.g. "name as alias"."""

    names = _ast_parse1(f'import \\\n{src}', parse_params).names

    if len(names) != 1:
        raise ParseError('expecting single name')

    return _offset_linenos(names[0], -1)  # _offset_linenos(_validate_indent(src, names[0]), -1)


@staticmethod
def _parse_alias_star(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.alias`, allowing star,."""

    names = _ast_parse1(f'from . import \\\n{src}', parse_params).names

    if len(names) != 1:
        raise ParseError('expecting single name')

    return _offset_linenos(names[0], -1)  # _offset_linenos(_validate_indent(src, names[0]), -1)


@staticmethod
def _parse_withitem(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.withitem`, e.g. "something() as var"."""

    items = _ast_parse1(f'with (\n{src}\n): pass', parse_params).items

    if len(items) == 1:
        ast = items[0].context_expr

        if isinstance(ast, GeneratorExp):  # wrapped something that looks like a GeneratorExp and turned it into that, bad
            raise SyntaxError('expecting withitem, got unparenthesized GeneratorExp')

        if isinstance(ast, Tuple) and not ast.elts:
            raise SyntaxError('expecting withitem')

    else:  # unparenthesized Tuple
        if all(not i.optional_vars for i in items):
            items = _ast_parse1(f'with ((\n{src}\n)): pass', parse_params).items

        if len(items) != 1:
            raise ParseError('expecting single withitem')

        ast = items[0].context_expr

        assert isinstance(ast, Tuple)

        _fix_unparenthesized_tuple_parsed_parenthesized(src, ast)

    return _offset_linenos(items[0], -1)  # _offset_linenos(_validate_indent(src, items[0]), -1)


@staticmethod
def _parse_pattern(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.pattern`, e.g. "{a.b: i, **rest}"."""

    try:
        ast = _ast_parse1_case(f'match _:\n case \\\n{src}: pass', parse_params).pattern

    except SyntaxError:  # first in case needs to be enclosed  # except IndentationError: raise  # before if checking that
        try:
            ast = _ast_parse1_case(f'match _:\n case (\\\n{src}\n): pass', parse_params).pattern

        except SyntaxError:  # now just the case of a lone MatchStar
            try:
                patterns = _ast_parse1_case(f'match _:\n case [\\\n{src}\n]: pass', parse_params).pattern.patterns
            except SyntaxError:
                raise SyntaxError('invalid pattern') from None

            if len(patterns) != 1:
                raise ParseError('expecting single pattern') from None

            ast = patterns[0]

        else:
            if ast.lineno < 3 and isinstance(ast, MatchSequence):
                if not (patterns := ast.patterns):
                    raise SyntaxError('empty pattern') from None

                ast.lineno         = 3  # remove our delimiters from location
                ast.col_offset     = 0
                ast.end_lineno     = (p_1 := patterns[-1]).end_lineno
                ast.end_col_offset = p_1.end_col_offset

    return _offset_linenos(ast, -2)  # _offset_linenos(_validate_indent(src, ast), -2)


@staticmethod
def _parse_type_param(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.type_param`, e.g. "t: Base = Subclass"."""

    type_params = _ast_parse1(f'type t[\n{src}\n] = None', parse_params).type_params

    if len(type_params) != 1:
        raise ParseError('expecting single type_param')

    ast = type_params[0]

    if _has_trailing_comma(src, ast.end_lineno - 1, ast.end_col_offset):
        raise ParseError('expecting single type_param, has trailing comma')

    return _offset_linenos(ast, -1)  # _offset_linenos(_validate_indent(src, type_params[0]), -1)


@staticmethod
def _parse_type_params(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `ast.type_param`s and return them in a `Tuple`. Will accept empty tuple parentheses as well
    as empty source for a zero-length slice."""

    try:
        type_params = _ast_parse1(f'type t[\n{src}\n] = None', parse_params).type_params
        ast         = None

    except SyntaxError as first_exc:  # maybe empty
        try:
            ast = _ast_parse1(f'(\n{src}\n)').value  # parse empty as well as zero-length tuple
        except SyntaxError:
            raise first_exc from None

        if not isinstance(ast, Tuple) or ast.elts:
            raise SyntaxError('invalid type_params slice') from None

        if ast.lineno == 1:
            ast = None

        type_params = []

    if not ast:
        ast = Tuple(elts=type_params, ctx=Load(), lineno=2, col_offset=0, end_lineno=2 + src.count('\n'),
                    end_col_offset=len((src if (i := src.rfind('\n')) == -1 else src[i + 1:]).encode()))

    return _offset_linenos(ast, -1)  # _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_Assign_targets(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `Assign` targets and return them in an `Assign` with the `value` node as an empty `Name`. Takes
    `=` as separators with an optional trailing `=`."""

    try:
        ast = _ast_parse1(f'_=\\\n{src}  _')  # try assuming src has trailing equals

    except SyntaxError:
        try:
            ast = _ast_parse1(f'_=\\\n{src} =_')  # now check assuming src does not have trailing equals
        except SyntaxError:
            raise SyntaxError('invalid Assign targets slice') from None

    if not isinstance(ast, Assign):
        raise ParseError(f'expecting Assign targets, got {ast.__class__.__name__}')

    if not isinstance(name := ast.value, Name):
        raise ParseError(f'unexpected value type parsing Assign targets, {name.__class__.__name__}')
    elif name.id != '_':
        raise ParseError(f'unexpected value id parsing Assign targets, {name.value!r}')

    del (targets := ast.targets)[0]  # remove syntax check dummy target

    if targets:
        if col_offset := (t0 := targets[0]).col_offset:
            raise IndentationError('unexpected indent')

        ast.col_offset = col_offset  # set Assign to start at new first element
        ast.lineno     = t0.lineno

    else:
        ast.col_offset = 0
        ast.lineno     = 2

    name.id         = ''  # mark as slice
    name.col_offset = name.end_col_offset = ast.end_col_offset = ast.end_col_offset - 3

    return _offset_linenos(ast, -1)  # _offset_linenos(_validate_indent(src, ast), -1)


# ......................................................................................................................

@staticmethod
def _code_as_all(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to any parsable `FST` if possible. If `FST` passed then it is returned as itself."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        return code

    if isinstance(code, AST):
        mode  = code.__class__  # we do not accept invalid-AST SPECIAL SLICE ASTs on purpose, could accept them by setting `mode = _get_special_parse_mode(code) or code.__class__` but that gets complicated fast
        code  = _unparse(code)
        lines = code.split('\n')

    else:
        mode = 'all'

        if isinstance(code, list):
            code = '\n'.join(lines := code)
        else:  # str
            lines = code.split('\n')

    return fst.FST(_parse(code, mode), lines, parse_params=parse_params)


@staticmethod
def _code_as_stmts(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to zero or more `stmt`s and return in the `body` of a `Module` `FST` if possible."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if isinstance(codea, Expression):  # coerce Expression to expr
            code._unmake_fst_parents()

            codea = codea.body

        if isinstance(codea, expr):  # coerce expr to Expr stmt
            codea = Expr(value=codea, lineno=codea.lineno, col_offset=codea.col_offset,
                         end_lineno=codea.end_lineno, end_col_offset=codea.end_col_offset)

        if isinstance(codea, stmt):
            return fst.FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, stmt) for a in codea.body):
                return code

            raise NodeError(f'expecting zero or more stmts, got '
                            f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]', rawable=True)

        if isinstance(codea, Interactive):
            code._unmake_fst_parents()

            return fst.FST(Module(body=code.body, type_ignores=[]), code._lines, from_=code, lcopy=False)

        raise NodeError(f'expecting zero or more stmts, got {codea.__class__.__name__}', rawable=True)

    if isinstance(code, AST):
        if not isinstance(code, (stmt, expr, Module, Interactive, Expression)):  # all these can be coerced into stmts
            raise NodeError(f'expecting zero or more stmts, got {code.__class__.__name__}', rawable=True)

        code  = _fixing_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return fst.FST(_parse_stmts(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_ExceptHandlers(code: Code, parse_params: Mapping[str, Any] = {}, *, is_trystar: bool = False) -> fst.FST:
    """Convert `code` to zero or more `ExceptHandler`s and return in the `body` of a `Module` `FST` if possible.

    **Parameters:**
    - `is_trystar`: Hint used when unparsing an `AST` `code` to get the correct `except` or `except*` source.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if isinstance(codea, ExceptHandler):
            return fst.FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, ExceptHandler) for a in codea.body):
                return code

            raise NodeError(f'expecting zero or more ExceptHandlers, got '
                             f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]', rawable=True)

        raise NodeError(f'expecting zero or more ExceptHandlers, got {codea.__class__.__name__}', rawable=True)

    if isinstance(code, AST):
        if isinstance(code, Module):  # may be slice of ExceptHandlers
            code = _fixing_unparse(code)

        else:
            if not isinstance(code, ExceptHandler):
                raise NodeError(f'expecting zero or more ExceptHandlers, got {code.__class__.__name__}', rawable=True)

            if is_trystar:
                code = _fixing_unparse(TryStar(body=[Pass()], handlers=[code], orelse=[], finalbody=[]))
                code = code[code.index('except'):]
            else:
                code = _fixing_unparse(code)

        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return fst.FST(_parse_ExceptHandlers(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_match_cases(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to zero or more `match_case`s and return in the `body` of a `Module` `FST` if possible."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if isinstance(codea, match_case):
            return fst.FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, match_case) for a in codea.body):
                return code

            raise NodeError(f'expecting zero or more match_cases, got '
                             f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]', rawable=True)

        raise NodeError(f'expecting zero or more match_cases, got {codea.__class__.__name__}', rawable=True)

    if isinstance(code, AST):
        if not isinstance(code, (match_case, Module)):
            raise NodeError(f'expecting zero or more match_cases, got {code.__class__.__name__}', rawable=True)

        code  = _fixing_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return fst.FST(_parse_match_cases(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_expr(code: Code, parse_params: Mapping[str, Any] = {}, *,
                  parse: Callable[[Code, dict], fst.FST] = _parse_expr, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `expr` or optionally `Slice` `FST` if possible."""

    def expecting() -> str:
        return ('expecting Tuple' if parse is _parse_Tuple else
                'expecting expression (slice element)' if parse is _parse_expr_sliceelt else
                'expecting expression (slice)' if parse is _parse_expr_slice else
                'expecting expression (arglike)' if parse is _parse_expr_arglike else
                'expecting expression (any)' if parse is _parse_expr_all else
                'expecting expression (standard)')

    def validate(ast: AST) -> None:
        if not isinstance(ast, expr):
            raise NodeError(f'{expecting()}, got {ast.__class__.__name__}', rawable=True)

        if isinstance(ast, Tuple) and (elts := ast.elts) and not all(isinstance(elt := e, expr) for e in elts):  # SPECIAL SLICE!
            raise NodeError(f'{expecting()}, got Tuple containing {elt.__class__.__name__}', rawable=True)

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not (ast := reduce_ast(codea := code.a)):
            raise NodeError(f'{expecting()}, got multiple statements', rawable=True)

        validate(ast)

        if ast is codea:
            return code._sanitize() if sanitize else code

        ast.f._unmake_fst_parents()

        code = fst.FST(ast, code._lines, from_=code, lcopy=False)

        return code._sanitize() if sanitize else code

    if is_ast := isinstance(code, AST):
        validate(code)

        src   = _unparse(code)
        lines = src.split('\n')

    elif isinstance(code, list):
        src = '\n'.join(lines := code)
    else:  # str
        lines = (src := code).split('\n')

    ast = parse(src, parse_params)

    if is_ast and ast.__class__ is not code.__class__:
        raise ParseError(f'could not reparse AST to {code.__class__.__name__}, got {ast.__class__.__name__}')

    fst_ = fst.FST(ast, lines, parse_params=parse_params)

    return fst_._sanitize() if sanitize else fst_


@staticmethod
def _code_as_expr_all(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `expr` using `_parse_expr_all()`."""

    return _code_as_expr(code, parse_params, parse=_parse_expr_all, sanitize=sanitize)


@staticmethod
def _code_as_expr_arglike(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `expr` in the context of a `Call.args` which has special parse rules for `Starred`."""

    return _code_as_expr(code, parse_params, parse=_parse_expr_arglike, sanitize=sanitize)


@staticmethod
def _code_as_expr_slice(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a Slice `FST` if possible (or anthing else that can serve in `Subscript.slice`, like any old
    generic `expr`)."""

    return _code_as_expr(code, parse_params, parse=_parse_expr_slice, sanitize=sanitize)


@staticmethod
def _code_as_expr_sliceelt(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `expr` or `Slice` `FST` if possible. This exists because of the behavior of naked `Starred`
    expressions in a `Subscript` `slice` field."""

    return _code_as_expr(code, parse_params, parse=_parse_expr_sliceelt, sanitize=sanitize)


@staticmethod
def _code_as_Tuple(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a `Tuple` using `_parse_Tuple()`."""

    fst_ = _code_as_expr(code, parse_params, parse=_parse_Tuple, sanitize=sanitize)

    if fst_ is code and not isinstance(fst_.a, Tuple):  # fst_ is code only if FST passed in, in which case is passed through and we need to check that was Tuple to begin with
        raise NodeError(f'expecting Tuple, got {fst_.a.__class__.__name__}', rawable=True)

    return fst_


@staticmethod
def _code_as_boolop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to a `boolop` `FST` if possible."""

    return _code_as_op(code, boolop, parse_params, _parse_boolop, OPSTR2CLS_BOOL)


@staticmethod
def _code_as_binop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to a `operator` `FST` if possible."""

    return _code_as_op(code, operator, parse_params, _parse_binop, OPSTR2CLS_BIN)


@staticmethod
def _code_as_augop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to an augmented `operator` `FST` if possible, e.g. "+="."""

    return _code_as_op(code, operator, parse_params, _parse_augop, OPSTR2CLS_AUG, OPCLS2STR_AUG)


@staticmethod
def _code_as_unaryop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to a `unaryop` `FST` if possible."""

    return _code_as_op(code, unaryop, parse_params, _parse_unaryop, OPSTR2CLS_UNARY)


@staticmethod
def _code_as_cmpop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to a `cmpop` `FST` if possible."""

    return _code_as_op(code, cmpop, parse_params, _parse_cmpop, OPSTR2CLS_CMP)


@staticmethod
def _code_as_comprehension(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(code, comprehension, parse_params, _parse_comprehension, sanitize=sanitize)


@staticmethod
def _code_as_arguments(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a arguments `FST` if possible."""

    # TODO: upcast FST and AST arg to arguments?

    return _code_as(code, arguments, parse_params, _parse_arguments, sanitize=sanitize)


@staticmethod
def _code_as_arguments_lambda(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a lambda arguments `FST` if possible (no annotations allowed)."""

    # TODO: upcast FST and AST arg to arguments?

    return _code_as(code, arguments, parse_params, _parse_arguments_lambda, sanitize=sanitize)


@staticmethod
def _code_as_arg(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an arg `FST` if possible."""

    return _code_as(code, arg, parse_params, _parse_arg, sanitize=sanitize)


@staticmethod
def _code_as_keyword(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a keyword `FST` if possible."""

    return _code_as(code, keyword, parse_params, _parse_keyword, sanitize=sanitize)


@staticmethod
def _code_as_alias(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a alias `FST` if possible, star or dotted."""

    return _code_as(code, alias, parse_params, _parse_alias, sanitize=sanitize)


@staticmethod
def _code_as_alias_dotted(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a alias `FST` if possible, dotted as in `alias` for `Import.names`."""

    fst_ = _code_as(code, alias, parse_params, _parse_alias_dotted, sanitize=sanitize)

    if '*' in fst_.a.name:
        raise ParseError("'*' not allowed in this alias")

    return fst_


@staticmethod
def _code_as_alias_star(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a alias `FST` if possible, possibly star as in `alias` for `FromImport.names`."""

    fst_ = _code_as(code, alias, parse_params, _parse_alias_star, sanitize=sanitize)

    if '.' in fst_.a.name:
        raise ParseError("'.' not allowed in this alias")

    return fst_


@staticmethod
def _code_as_withitem(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(code, withitem, parse_params, _parse_withitem, sanitize=sanitize)


@staticmethod
def _code_as_pattern(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True,
                     allow_invalid_matchor: bool = False) -> fst.FST:
    """Convert `code` to a pattern `FST` if possible."""

    fst_ = _code_as(code, pattern, parse_params, _parse_pattern, sanitize=sanitize)

    if not allow_invalid_matchor and isinstance(a := fst_.a, MatchOr):  # SPECIAL SLICE, don't need to check if 'fst_ is code' because this could only have come from 'code' as FST
        if not (len_pattern := len(a.patterns)):
            raise NodeError('expecting valid pattern, got zero-length MatchOr')

        if len_pattern == 1:  # a length 1 MatchOr can just return its single element pattern
            return fst.FST(a.patterns[0], fst_._lines, from_=fst_, lcopy=False)

    return fst_


@staticmethod
def _code_as_type_param(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a type_param `FST` if possible."""

    return _code_as(code, type_param, parse_params, _parse_type_param, sanitize=sanitize)


@staticmethod
def _code_as_type_params(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a type_params slice `FST` if possible."""

    fst_ = _code_as(code, Tuple, parse_params, _parse_type_params, sanitize=sanitize)

    if fst_ is code:  # this means it was not parsed (came in as FST) and we need to verify it containes only type_params
        if not all(isinstance(elt := e, type_param) for e in fst_.a.elts):
            raise NodeError(f'expecting only type_params, got {elt.__class__.__name__}', rawable=True)

    return fst_


@staticmethod
def _code_as_Assign_targets(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `Assign` targets slice `FST` if possible."""

    fst_ = _code_as(code, Assign, parse_params, _parse_Assign_targets, sanitize=sanitize)

    if not isinstance(name := fst_.a.value, Name) or name.id:  # SPECIAL SLICE
        raise NodeError('expecting Assign targets slice, got normal Assign', rawable=True)

    return fst_


@staticmethod
def _code_as_identifier(code: Code, parse_params: Mapping[str, Any] = {}) -> str:
    """Convert `code` to valid identifier string if possible."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier(code):
        raise ParseError(f'expecting identifier, got {_shortstr(code)!r}')

    return normalize('NFKC', code)


@staticmethod
def _code_as_identifier_dotted(code: Code, parse_params: Mapping[str, Any] = {}) -> str:
    """Convert `code` to valid dotted identifier string if possible (for Import module)."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_dotted(code):
        raise ParseError(f'expecting dotted identifier, got {_shortstr(code)!r}')

    return normalize('NFKC', code)


@staticmethod
def _code_as_identifier_star(code: Code, parse_params: Mapping[str, Any] = {}) -> str:
    """Convert `code` to valid identifier string or star '*' if possible (for ImportFrom names)."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_star(code):
        raise ParseError(f"expecting identifier or '*', got {_shortstr(code)!r}")

    return normalize('NFKC', code)


@staticmethod
def _code_as_identifier_alias(code: Code, parse_params: Mapping[str, Any] = {}) -> str:
    """Convert `code` to valid dotted identifier string or star '*' if possible (for any alias)."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_alias(code):
        raise ParseError(f"expecting dotted identifier or '*', got {_shortstr(code)!r}")

    return normalize('NFKC', code)


@staticmethod
def _code_as_constant(code: constant, parse_params: Mapping[str, Any] = {}) -> constant:
    """Convert `code` to valid constant if possible. If `code` is a `str` then it is treated as the constant value and
    not as the python representation of the constant. The only `FST` or `AST` accepted is a `Constant`, whose `value` is
    returned."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.a

    if isinstance(code, AST):
        if not isinstance(code, Constant):
            raise NodeError('expecting constant', rawable=True)

        code = code.value

        if isinstance(code, (int, float)):
            if code < 0:
                raise NodeError('constants cannot be negative', rawable=True)

        elif isinstance(code, complex):
            if code.real:
                raise NodeError('imaginary constants cannot have real componenets', rawable=True)
            if code.imag < 0:
                raise NodeError('imaginary constants cannot be negative', rawable=True)

    elif isinstance(code, list):
        code = '\n'.join(code)
    elif not isinstance(code, constant):
        raise NodeError('expecting constant', rawable=True)

    return code


# ----------------------------------------------------------------------------------------------------------------------

_PARSE_MODE_FUNCS = {  # these do not all guarantee will parse ONLY to that type but that will parse ALL of those types without error, not all parsed in desired but all desired in parsed
    'all':               _parse_all,
    'strict':            _parse_strict,
    'exec':              _parse_Module,
    'eval':              _parse_Expression,
    'single':            _parse_Interactive,
    'stmts':             _parse_stmts,
    'stmt':              _parse_stmt,
    'ExceptHandler':     _parse_ExceptHandler,
    'ExceptHandlers':    _parse_ExceptHandlers,
    'match_case':        _parse_match_case,
    'match_cases':       _parse_match_cases,
    'expr':              _parse_expr,
    'expr_all':          _parse_expr_all,       # `a:b:c`, `*not c`, `*st`, `a,`, `a, b`, `a:b:c,`, `a:b:c, x:y:x, *st`, `*not c`
    'expr_arglike':      _parse_expr_arglike,   # `*a or b`, `*not c`
    'expr_slice':        _parse_expr_slice,     # `a:b:c`, `*not c`, `a:b:c, x:y:z`, `*st` -> `*st,` (py 3.11+)
    'expr_sliceelt':     _parse_expr_sliceelt,  # `a:b:c`, `*not c`, `*st`
    'Tuple':             _parse_Tuple,          # `a,`, `a, b`, `a:b:c,`, `a:b:c, x:y:x, *st`
    'boolop':            _parse_boolop,
    'operator':          _parse_operator,
    'binop':             _parse_binop,
    'augop':             _parse_augop,
    'unaryop':           _parse_unaryop,
    'cmpop':             _parse_cmpop,
    'comprehension':     _parse_comprehension,
    'arguments':         _parse_arguments,
    'arguments_lambda':  _parse_arguments_lambda,
    'arg':               _parse_arg,
    'keyword':           _parse_keyword,
    'alias':             _parse_alias,
    'alias_dotted':      _parse_alias_dotted,
    'alias_star':        _parse_alias_star,
    'withitem':          _parse_withitem,
    'pattern':           _parse_pattern,
    'type_param':        _parse_type_param,
    'type_params':       _parse_type_params,
    'Assign_targets':    _parse_Assign_targets,
    mod:                 _parse_Module,    # parsing with an AST type doesn't mean it will be parsable by ast module
    Expression:          _parse_Expression,
    Interactive:         _parse_Interactive,
    stmt:                _parse_stmt,
    ExceptHandler:       _parse_ExceptHandler,
    match_case:          _parse_match_case,
    expr:                _parse_expr,          # not _expr_all because those cases are handled in Starred, Slice and Tuple
    Starred:             _parse_expr_arglike,  # because could have form '*a or b' and we want to parse any form of Starred here
    Slice:               _parse_expr_slice,    # because otherwise would be _parse_expr which doesn't do slice by default, parses '*a' to '*a,' on py 3.11+
    Tuple:               _parse_Tuple,         # because could have slice in it and we are parsing all forms including '*not a'
    boolop:              _parse_boolop,
    operator:            _parse_operator,
    unaryop:             _parse_unaryop,
    cmpop:               _parse_cmpop,
    comprehension:       _parse_comprehension,
    arguments:           _parse_arguments,
    arg:                 _parse_arg,
    keyword:             _parse_keyword,
    alias:               _parse_alias,
    withitem:            _parse_withitem,
    pattern:             _parse_pattern,
    type_param:          _parse_type_param,
    Load:                lambda src, parse_params = {}: Load(),  # HACKS for verify() and other similar stuff
    Store:               lambda src, parse_params = {}: Store(),
    Del:                 lambda src, parse_params = {}: Del(),
}

assert not set(get_args(get_args(Mode)[0])).symmetric_difference(k for k in _PARSE_MODE_FUNCS if isinstance(k, str)), \
    'Mode string modes do not match _PARSE_MODE_FUNCS table'
