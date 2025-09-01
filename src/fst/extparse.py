"""Extended AST parse.

The parse functions in this module are oriented towards parsing all valid elements which they name which may include
parsing things which are not those elements, common sense is applied liberally though. And just because an element is
parsed successfully doesn't mean it may not need parentheses if used in the way intended. Or that it needs a trailing
newline due to comment ending without an explicit trailing newline.
"""

from __future__ import annotations

import re
from ast import parse as ast_parse, unparse as ast_unparse, fix_missing_locations as ast_fix_missing_locations
from typing import Any, Callable, Literal, Mapping, get_args

from . import fst

from .asttypes import (
    AST,
    Assign,
    AugAssign,
    BinOp,
    BoolOp,
    Compare,
    Del,
    ExceptHandler,
    Expr,
    Expression,
    GeneratorExp,
    Interactive,
    ListComp,
    Load,
    MatchSequence,
    Module,
    Name,
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
    type_param,
)

from .astutil import (
    pat_alnum, bistr,
    OPCLS2STR,
    walk, reduce_ast,
)

from .misc import (
    next_frag, shortstr
)

__all__ = [
    'Mode',
    'ParseError',
    'get_special_parse_mode',
    'unparse',
    'parse',
    'parse_all',
    'parse_strict',
    'parse_Module',
    'parse_Expression',
    'parse_Interactive',
    'parse_stmt',
    'parse_stmts',
    'parse_ExceptHandler',
    'parse_ExceptHandlers',
    'parse_match_case',
    'parse_match_cases',
    'parse_expr',
    'parse_expr_all',
    'parse_expr_arglike',
    'parse_expr_slice',
    'parse_expr_sliceelt',
    'parse_Tuple',
    'parse_boolop',
    'parse_operator',
    'parse_binop',
    'parse_augop',
    'parse_unaryop',
    'parse_cmpop',
    'parse_comprehension',
    'parse_arguments',
    'parse_arguments_lambda',
    'parse_arg',
    'parse_keyword',
    'parse_alias',
    'parse_alias_dotted',
    'parse_alias_star',
    'parse_withitem',
    'parse_pattern',
    'parse_type_param',
    'parse_type_params',
    'parse_Assign_targets',
]


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

    if (not (frag := next_frag(lines, end_ln, end_col, ast.end_lineno - 3, 0x7fffffffffffffff)) or  # if nothing following then last element is ast end, -3 because end also had \n tacked on
        not frag.src.startswith(',')  # if no comma then last element is ast end
    ):
        ast.end_lineno     = e_1.end_lineno
        ast.end_col_offset = e_1.end_col_offset

    else:
        end_ln, end_col, _ = frag
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
    `parse_all()` on finding a leading identifier character or star so that is assumed to be there, which will generate
    at least one `type_param`."""

    type_params = _ast_parse1(f'type t[\n{src}\n] = None', parse_params).type_params

    ast = type_params[0]

    if len(type_params) > 1 or _has_trailing_comma(src, ast.end_lineno - 1, ast.end_col_offset):
        ast = Tuple(elts=type_params, ctx=Load(), lineno=2, col_offset=0, end_lineno=2 + src.count('\n'),
                    end_col_offset=len((src if (i := src.rfind('\n')) == -1 else src[i + 1:]).encode()))

    return _offset_linenos(ast, -1)


def _parse_all_multiple(src: str, parse_params: Mapping[str, Any], stmt: bool, rest: list[Callable]) -> AST:
    """Attempt to parse one at a time using functions from a list until one succeeds."""

    if stmt:
        try:
            return reduce_ast(parse_stmts(src, parse_params), True)
        except SyntaxError:
            pass

    for parse in rest:
        try:
            return parse(src, parse_params)
        except SyntaxError:
            pass

    raise ParseError('invalid syntax')


# ----------------------------------------------------------------------------------------------------------------------

Mode = Literal[
    'all',
    'strict',
    'exec',
    'eval',
    'single',
    'stmts',
    'stmt',
    'ExceptHandler',
    'ExceptHandlers',
    'match_case',
    'match_cases',
    'expr',
    'expr_all',
    'expr_arglike',
    'expr_slice',
    'expr_sliceelt',
    'Tuple',
    'boolop',
    'operator',
    'binop',
    'augop',
    'unaryop',
    'cmpop',
    'comprehension',
    'arguments',
    'arguments_lambda',
    'arg',
    'keyword',
    'alias',
    'alias_dotted',
    'alias_star',
    'withitem',
    'pattern',
    'type_param',
    'type_params',
    'Assign_targets',
] | type[AST]

"""Extended parse modes:
- `'all'`: Check all possible parse modes (from most likely to least). There is syntax overlap so certain types will
    never be returned, for example `TypeVar` is always shadowed by `AnnAssign`. Since this attempts many parses before
    failing it is slower to do so than other modes, though the most likely success is just as fast. Will never return an
    `Expression` or `Interactive`.
- `'strict'`: Attempt parse minumum valid parsable code. If only one statement then return the statement itself instead
    of the `Module`. If that statement is an `Expr` then return the expression instead of the statement. If nothing
    present then return empty `Module`. Doesn't attempt any of the other parse modes which would not normally be
    parsable by python, just anything that can be parsed natively by `ast.parse()`.
- `'exec'`: Parse to a `Module`. Same as passing `Module` type or `'stmts'`. Same as `ast.parse()` mode 'exec'.
- `'eval'`: Parse to an `Expression`. Same as passing `Expression` type. Same as `ast.parse()` mode 'eval'.
- `'single'`: Parse to an `Interactive`. Same as passing `Interactive` type. Same as `ast.parse()` mode 'single'.
- `'stmts'`: Parse zero or more `stmt`s returned in a `Module`. Same as passing `'exec'` or `Module`.
- `'stmt'`: Parse a single `stmt` returned as itself. Same as passing `stmt` type.
- `'ExceptHandler'`: Parse as a single `ExceptHandler` returned as itself. Same as passing `ExceptHandler` type.
- `'ExceptHandlers'`: Parse zero or more `ExceptHandler`s returned in a `Module`.
- `'match_case'`: Parse a single `match_case` returned as itself. Same as passing `match_case` type.
- `'match_cases'`: Parse zero or more `match_case`s returned in a `Module`.
- `'expr'`: "expression", parse a single `expr` returned as itself. This is differentiated from the following modes by
    the handling of slices and starred expressions. In this mode `a:b` and `*not v` are syntax errors. Same as passing
    `expr` type.
- `'expr_all'`: Parse to any kind of expression including `Slice`, `*not a` or `Tuple` of any of those combined.
- `'expr_arglike'`: Accept special syntax for `Starred` (call argument, class base definition, slice implicit tuple),
    same as `'expr'` except that in this mode `a:b` is a syntax error and `*not v` parses to a starred expression
    `*(not v)`.
- `'expr_slice'`: "slice expression", same as `'expr'` except that in this mode `a:b` parses to a `Slice` and `*not v`
    parses to a single element tuple containing a starred expression `(*(not v),)`.
- `'expr_sliceelt'`: "slice tuple element expression", same as `'expr'` except that in this mode `a:b` parses to a
    `Slice` and `*not v` parses to a starred expression `*(not v)`. `Tuples` are parsed but cannot contain `Slice`s.
- `'Tuple'`: Parse to a `Tuple` which may contain anything that a tuple can contain like multiple `Slice`s.
- `'boolop'`: Parse to a `boolop` operator.
- `'operator'`: Parse to an `operator` operator, either normal binary `'*'` or augmented `'*='`.
- `'binop'`: Parse to an `operator` only binary `'*'`, `'+'`, `'>>'`, etc...
- `'augop'`: Parse to an `operator` only augmented `'*='`, `'+='`, `'>>='`, etc...
- `'unaryop'`: Parse to a `unaryop` operator.
- `'cmpop'`: Parse to a `cmpop` compare operator.
- `'comprehension'`: Parse a single `comprehension` returned as itself. Same as passing `comprehension` type.
- `'arguments'`: Parse as `arguments` for a `FunctionDef` or `AsyncFunctionDef` returned as itself. In this mode
    type annotations are allowed for the arguments. Same as passing `arguments` type.
- `'arguments_lambda'`: Parse as `arguments` for a `Lambda` returned as itself. In this mode type annotations
    are not allowed for the arguments.
- `'arg'`: Parse as a single `arg` returned as itself. Same as passing `arg` type.
- `'keyword'`: Parse as a single `keyword` returned as itself. Same as passing `keyword` type.
- `'alias'`: Parse as a single `alias` returned as itself. Either starred or dotted versions are accepted. Same
    as passing `alias` type.
- `'alias_dotted'`: Parse as a single `alias` returned as itself, with starred version being a syntax error. This is the
    `alias` used in `Import.names`.
- `'alias_star'`: Parse as a single `alias` returned as itself, with dotted version being a syntax error. This is the
    `alias` used in `ImportFrom.names`.
- `'withitem'`: Parse as a single `withitem` returned as itself. Same as passing `withitem` type.
- `'pattern'`: Parse as a a single `pattern` returned as itself. Same as passing `pattern` type.
- `'type_param'`: Parse as a single `type_param` returned as itself, either `TypeVar`, `ParamSpec` or
    `TypeVarTuple`. Same as passing `type_param` type.
- `'type_params'`: Parse as a slice of zero or more `type_param`s returned in a `Tuple`, does not need trailing comma
    for a single element. This is our own SPECIAL SLICE use of a tuple and not valid in python.
- `'Assign_targets'`: Parse as a single or multiple targets to an `Assign` node, with `=` as separators and an optional
    trailing `=`. Returned as an `Assign` node with a `value` node which is an empty `Name` (our own SPECIAL SLICE).
- `type[AST]`: If an `AST` type is passed then will attempt to parse to this type. This can be used to narrow
    the scope of desired return, for example `Constant` will parse as an expression but fail if the expression
    is not a `Constant`. These overlap with the string specifiers to an extent but not all of them. For example
    `AST` type `ast.expr` is the same as passing `'expr'`. Not all string specified modes are can be matched, for
    example `'arguments_lambda'`. Likewise `'exec'` and `'stmts'` specify the same parse mode. `Tuple` parse also allows
    parsing `Slice`s in the `Tuple` as well as otherwise invalid star notation `*not a`.
"""


class ParseError(SyntaxError):
    """Not technically a syntax error but mostly not the code we were expecting."""


def get_special_parse_mode(ast: AST) -> str | None:
    """Quick determination to the best of ability if a special parse mode is needed for this `AST`. This is the
    extended parse mode as per `Mode`, not the `ast.parse()` mode. If a special mode applies it is returned which should
    parse the source of this `AST` back to itself. Otherwise `None` is returned. This is a just quick a check, doesn't
    verify everything.

    **WARNING!** This only gets special parse modes for where it can be inferred from the `AST` alone. This will not
    return the special parse mode of `'expr_slice'` for example for `(*st,)` single-`Starred` `Tuple` which is
    represented by the source `*st` from inside a `Subscript.slice`. That must be handled at a higher level.

    **Returns:**
    - `str`: One of the special parse modes.
    - `None`: If no special parse mode applies or can be determined.

    @private
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


def unparse(ast: AST) -> str:
    """AST unparse that handles misc case of comprehension starting with a single space by stripping it as well as
    removing parentheses from `Tuple`s with `Slice`s or special slice (our own) `Tuple`s.

    @private
    """

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


def parse(src: str, mode: Mode = 'all', parse_params: Mapping[str, Any] = {}) -> AST:
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
        See `Mode`.
    - `parse_params`: Dictionary of optional parse parameters to pass to `ast.parse()`, can contain `filename`,
        `type_comments` and `feature_version`.

    @private
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


def parse_all(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """All parse modes. Get a hint from starting source and attempt parse according to that from most probable to least
    of what it could be.

    @private
    """

    if not (first := _re_first_src.search(src)):
        return _ast_parse(src, parse_params)  # should return empty Module with src trivia

    if not (cat := _re_parse_all_category.match(first.group(2))):
        _ast_parse(src, parse_params)  # should raise SyntaxError

        raise RuntimeError('should not get here')

    groupdict = cat.groupdict()

    if groupdict['stmt_or_expr_or_pat_or_witem']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, parse_withitem, parse_Assign_targets))  # parse_expr_all because could be Slice

    if groupdict['match_type_identifier']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, parse_arguments, parse_arguments_lambda,
                                    parse_withitem, parse_arg, _parse_all_type_params, parse_Assign_targets))

    if groupdict['stmt']:
        return reduce_ast(parse_stmts(src, parse_params), True)

    if groupdict['True_False_None']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, parse_withitem))

    if groupdict['async_or_for']:
        return _parse_all_multiple(src, parse_params, not first.group(1), (parse_comprehension,))

    if groupdict['await_lambda_yield']:
        return _parse_all_multiple(src, parse_params, not first.group(1), (parse_expr_all,))

    if groupdict['if']:
        return reduce_ast(parse_stmts(src, parse_params), True)

    if groupdict['except']:
        return reduce_ast(parse_ExceptHandlers(src, parse_params), True)

    if groupdict['case']:
        try:
            return reduce_ast(parse_match_cases(src, parse_params), True)
        except SyntaxError:
            pass

        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, parse_arguments, parse_arguments_lambda,
                                    parse_withitem, parse_arg, _parse_all_type_params, parse_Assign_targets))

    if groupdict['at']:
        return reduce_ast(parse_stmts(src, parse_params), True)

    if groupdict['star']:
        ast = _parse_all_multiple(src, parse_params, not first.group(1),
                                  (parse_expr_arglike, parse_pattern, parse_arguments, parse_arguments_lambda,
                                   _parse_all_type_params, parse_operator, parse_Assign_targets))

        if isinstance(ast, Assign) and len(targets := ast.targets) == 1 and isinstance(targets[0], Starred):  # '*T = ...' validly parses to Assign statement but is invalid compile, but valid type_param so reparse as that
            return _parse_all_type_params(src, parse_params)

        return ast

    if groupdict['minus']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_pattern, parse_withitem, parse_binop))

    if groupdict['not']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_withitem, parse_unaryop, parse_cmpop))

    if groupdict['tilde']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_withitem, parse_unaryop))

    if groupdict['colon']:
        return _parse_all_multiple(src, parse_params, False, (parse_expr_all,))

    if groupdict['starstar']:
        return _parse_all_multiple(src, parse_params, False, (parse_arguments, parse_arguments_lambda,
                                                              _parse_all_type_params, parse_operator))

    if groupdict['plus']:
        return _parse_all_multiple(src, parse_params, not first.group(1),
                                   (parse_expr_all, parse_withitem, parse_binop))

    if groupdict['cmpop_w']:
        return parse_cmpop(src, parse_params)

    if groupdict['cmpop_o']:
        return parse_cmpop(src, parse_params)

    if groupdict['boolop']:
        return parse_boolop(src, parse_params)

    if groupdict['augop']:
        return parse_augop(src, parse_params)

    if groupdict['operator']:
        return parse_operator(src, parse_params)

    # groupdict['syntax_error'] or something else unrecognized

    _ast_parse(src, parse_params)  # should raise SyntaxError

    raise RuntimeError('should not get here')


def parse_strict(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Attempt to parse valid parsable statements and then reduce to a single statement or expressing if possible. Only
    parses what `ast.parse()` can, no funny stuff.

    @private
    """

    return reduce_ast(_ast_parse(src, parse_params), True)


def parse_Module(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Module`, ast.parse(mode='exec')'.

    @private
    """

    return _ast_parse(src, parse_params)


def parse_Expression(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Expression`, `ast.parse(mode='eval').

    @private
    """

    return _ast_parse(src, {**parse_params, 'mode': 'eval'})


def parse_Interactive(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse `Interactive`.

    @private
    """

    if not src.endswith('\n'):  # because otherwise error maybe
        src = src + '\n'

    return _ast_parse(src, {**parse_params, 'mode': 'single'})


def parse_stmts(src: str, parse_params: Mapping[str, Any] = {}) -> AST:  # same as parse_Module() but I want the IDE context coloring
    """Parse zero or more `stmt`s and return them in a `Module` `body` (just `ast.parse()` basically).

    @private
    """

    return _ast_parse(src, parse_params)


def parse_stmt(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `stmt` and return as itself.

    @private
    """

    mod = _ast_parse(src, parse_params)

    if len(body := mod.body) != 1:
        raise ParseError('expecting single stmt')

    return body[0]


def parse_ExceptHandler(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `ExceptHandler` and return as itself.

    @private
    """

    mod = parse_ExceptHandlers(src, parse_params)

    if len(body := mod.body) != 1:
        raise ParseError('expecting single ExceptHandler')

    return body[0]


def parse_ExceptHandlers(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `ExceptHandler`s and return them in a `Module` `body`.

    @private
    """

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


def parse_match_case(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse exactly one `match_case` and return as itself.

    @private
    """

    mod = parse_match_cases(src, parse_params)

    if len(body := mod.body) != 1:
        raise ParseError('expecting single match_case')

    return body[0]


def parse_match_cases(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `match_case`s and return them in a `Module` `body`.

    @private
    """

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


def parse_expr(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a "standard" `ast.expr`, only things which are normally valid in an `expr` location, no `Slices` or
    `Starred` expressions which are only valid as a `Call` arg (`*not a`).

    @private
    """

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

    return _offset_linenos(ast, -1)


def parse_expr_all(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to any kind of expression including `Slice`, `*not a` or `Tuple` of any of those combined. Lone `*a`
    `Starred` is returned as a `Starred` and not `Tuple` as would be in a slice.

    @private
    """

    try:
        ast = parse_expr_slice(src, parse_params)

    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11
        try:
            ast = parse_expr_arglike(src, parse_params)  # expr_arglike instead of expr because py 3.10 won't pick up `*not a` in a slice above
        except SyntaxError:
            raise SyntaxError('invalid expression (all types)') from None

    else:
        if (isinstance(ast, Tuple) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and  # check for '*starred' acting as '*starred,'
            e0.end_col_offset == ast.end_col_offset and e0.end_lineno == ast.end_lineno
        ):
            return e0

    return ast


def parse_expr_arglike(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `expr` or in the context of a `Call.args` which treats `Starred` differently.

    @private
    """

    try:
        return parse_expr(src, parse_params)
    except SyntaxError:  # stuff like '*[] or []'
        pass

    value = _ast_parse1(f'f(\n{src}\n)', parse_params).value
    args  = value.args

    if len(args) != 1 or value.keywords:
        raise ParseError('expecting single call argument expression')

    ast = args[0]

    if isinstance(ast, GeneratorExp):  # wrapped something that looks like a GeneratorExp and turned it into that, bad
        raise ParseError('expecting call argument expression, got unparenthesized GeneratorExp')

    return _offset_linenos(ast, -1)


def parse_expr_slice(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.Slice` or anything else that can go into `Subscript.slice` (`expr`), e.g. "start:stop:step" or
    "name" or even "a:b, c:d:e, g". Using this, naked `Starred` expressions parse to single element `Tuple` with the
    `Starred` as the only element.

    @private
    """

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

    return _offset_linenos(ast, -1)


def parse_expr_sliceelt(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an element of a slice `Tuple`, an `ast.expr` or `ast.Slice`. This exists because otherwise a naked
    `Starred` expression parses to an implicit single element `Tuple` and the caller of this function does not want that
    behavior. Using this, naked `Starred` expressions parse to just the `Starred` and not a `Tuple` like in
    `parse_expr_slice()`. Does not allow a `Tuple` with `Slice` in it as it is expected that this expression is already
    in a slice `Tuple` and that is not allowed in python.

    TODO: This can currently return `*not a, *a or b` as valid which are not valid normal tuples (nested as sliceelt).

    @private
    """

    try:
        ast = parse_expr_slice(src, parse_params)

    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11
        return parse_expr(src, parse_params)

    if isinstance(ast, Tuple) and any(isinstance(e, Slice) for e in ast.elts):
        raise SyntaxError('Slice not allowed in nested slice tuple')

    if (isinstance(ast, Tuple) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and  # check for '*starred' acting as '*starred,'
        e0.end_col_offset == ast.end_col_offset and e0.end_lineno == ast.end_lineno
    ):
        return e0

    return ast


def parse_Tuple(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to a `Tuple` which may or may not contain `Slice`s and otherwise invalid syntax in normal `Tuple`s like
    `*not a` (if not parenthesized).

    @private
    """

    try:
        ast        = parse_expr_slice(src, parse_params)
        from_slice = True

    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11
        try:
            ast = parse_expr(src, parse_params)
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


def parse_boolop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.boolop`.

    @private
    """

    ast = _ast_parse1(f'(a\n{src}\nb)', parse_params).value

    if not isinstance(ast, BoolOp):
        raise ParseError(f'expecting boolop, got {shortstr(src)!r}')

    return ast.op.__class__()  # parse() returns the same identical object for all instances of the same operator


def parse_operator(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.boolop`.

    @private
    """

    if '=' in src:
        try:
            return parse_augop(src, parse_params)
        except ParseError:  # maybe the '=' was in a comment, yes I know, a comment in an operator, people do strange things
            pass

    return parse_binop(src, parse_params)


def parse_binop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.operator` in the context of a `BinOp`.

    @private
    """

    ast = _ast_parse1(f'(a\n{src}\nb)', parse_params).value

    if not isinstance(ast, BinOp):
        raise ParseError(f'expecting operator, got {shortstr(src)!r}')

    return ast.op.__class__()  # parse() returns the same identical object for all instances of the same operator


def parse_augop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an augmented `ast.operator` in the context of a `AugAssign`.

    @private
    """

    ast = _ast_parse1(f'a \\\n{src} b', parse_params)

    if not isinstance(ast, AugAssign):
        raise ParseError(f'expecting augmented operator, got {shortstr(src)!r}')

    return ast.op.__class__()  # parse() returns the same identical object for all instances of the same operator


def parse_unaryop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.unaryop`.

    @private
    """

    ast = _ast_parse1(f'(\n{src}\nb)', parse_params).value

    if not isinstance(ast, UnaryOp):
        raise ParseError(f'expecting unaryop, got {shortstr(src)!r}')

    return ast.op.__class__()  # parse() returns the same identical object for all instances of the same operator


def parse_cmpop(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.cmpop`.

    @private
    """

    ast = _ast_parse1(f'(a\n{src}\nb)', parse_params).value

    if not isinstance(ast, Compare):
        raise ParseError(f'expecting cmpop, got {shortstr(src)!r}')

    if len(ops := ast.ops) != 1:
        raise ParseError('expecting single cmpop')

    return ops[0].__class__()  # parse() returns the same identical object for all instances of the same operator


def parse_comprehension(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.comprehension`, e.g. "async for i in something() if i".

    @private
    """

    ast = _ast_parse1(f'[_ \n{src}\n]', parse_params).value

    if not isinstance(ast, ListComp):
        raise ParseError('expecting comprehension')

    if len(gens := ast.generators) != 1:
        raise ParseError('expecting single comprehension')

    return _offset_linenos(gens[0], -1)


def parse_arguments(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.arguments`, e.g. "a: list[str], /, b: int = 1, *c, d=100, **e".

    @private
    """

    ast = _ast_parse1(f'def f(\n{src}\n): pass', parse_params).args

    return _offset_linenos(ast, -1)


def parse_arguments_lambda(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.arguments` for a `Lambda`, e.g. "a, /, b, *c, d=100, **e".

    @private
    """

    ast = _ast_parse1(f'(lambda \n{src}\n: None)', parse_params).value.args

    return _offset_linenos(ast, -1)


def parse_arg(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.arg`, e.g. "var: list[int]".

    @private
    """

    try:
        args = _ast_parse1(f'def f(\n{src}\n): pass', parse_params).args

    except SyntaxError:  # may be '*vararg: *starred'
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

    return _offset_linenos(ast, -1)


def parse_keyword(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.keyword`, e.g. "var=val".

    @private
    """

    keywords = _ast_parse1(f'f(\n{src}\n)', parse_params).value.keywords

    if len(keywords) != 1:
        raise ParseError('expecting single keyword')

    return _offset_linenos(keywords[0], -1)


def parse_alias(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.alias`, allowing star or dotted notation or star, e.g. "name as alias".

    @private
    """

    if '*' in src:
        try:
            return parse_alias_star(src, parse_params)
        except SyntaxError:  # '*' could have been in a comment
            pass

    return parse_alias_dotted(src, parse_params)


def parse_alias_dotted(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.alias`, allowing dotted notation but not star (not all aliases are created equal),
    e.g. "name as alias".

    @private
    """

    try:
        names = _ast_parse1(f'import \\\n{src}', parse_params).names

    except SyntaxError as first_exc:
        try:
            src   = src.replace("\n", "\\\n")
            names = _ast_parse1(f'import \\\n{src}', parse_params).names  # multiline?

        except SyntaxError:
            raise first_exc from None

    if len(names) != 1:
        raise ParseError('expecting single name')

    return _offset_linenos(names[0], -1)


def parse_alias_star(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.alias`, allowing star but not dotted.

    @private
    """

    try:
        names = _ast_parse1(f'from . import \\\n{src}', parse_params).names

    except SyntaxError as first_exc:
        try:
            src   = src.replace("\n", "\\\n")
            names = _ast_parse1(f'from . import \\\n{src}', parse_params).names  # multiline?

        except SyntaxError:
            raise first_exc from None

    if len(names) != 1:
        raise ParseError('expecting single name')

    return _offset_linenos(names[0], -1)


def parse_withitem(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.withitem`, e.g. "something() as var".

    @private
    """

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

    return _offset_linenos(items[0], -1)


def parse_pattern(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.pattern`, e.g. "{a.b: i, **rest}".

    @private
    """

    try:
        ast = _ast_parse1_case(f'match _:\n case \\\n{src}: pass', parse_params).pattern

    except SyntaxError:  # first in case needs to be enclosed
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

    return _offset_linenos(ast, -2)


def parse_type_param(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse to an `ast.type_param`, e.g. "t: Base = Subclass".

    @private
    """

    type_params = _ast_parse1(f'type t[\n{src}\n] = None', parse_params).type_params

    if len(type_params) != 1:
        raise ParseError('expecting single type_param')

    ast = type_params[0]

    if _has_trailing_comma(src, ast.end_lineno - 1, ast.end_col_offset):
        raise ParseError('expecting single type_param, has trailing comma')

    return _offset_linenos(ast, -1)


def parse_type_params(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `ast.type_param`s and return them in a `Tuple`. Will accept empty tuple parentheses as well
    as empty source for a zero-length slice.

    @private
    """

    try:
        type_params = _ast_parse1(f'type t[\n{src}\n] = None', parse_params).type_params
        ast         = None

    except SyntaxError as first_exc:  # maybe empty
        try:
            ast = _ast_parse1(f'(\n{src}\n)', parse_params).value  # parse empty as well as zero-length tuple
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

    return _offset_linenos(ast, -1)


def parse_Assign_targets(src: str, parse_params: Mapping[str, Any] = {}) -> AST:
    """Parse zero or more `Assign` targets and return them in an `Assign` with the `value` node as an empty `Name`. Takes
    `=` as separators with an optional trailing `=`.

    @private
    """

    try:
        ast = _ast_parse1(f'_=\\\n{src}  _', parse_params)  # try assuming src has trailing equals

    except SyntaxError:
        try:
            ast = _ast_parse1(f'_=\\\n{src} =_', parse_params)  # now check assuming src does not have trailing equals
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

    return _offset_linenos(ast, -1)


# ......................................................................................................................

_PARSE_MODE_FUNCS = {  # these do not all guarantee will parse ONLY to that type but that will parse ALL of those types without error, not all parsed in desired but all desired in parsed
    'all':               parse_all,
    'strict':            parse_strict,
    'exec':              parse_Module,
    'eval':              parse_Expression,
    'single':            parse_Interactive,
    'stmts':             parse_stmts,
    'stmt':              parse_stmt,
    'ExceptHandler':     parse_ExceptHandler,
    'ExceptHandlers':    parse_ExceptHandlers,
    'match_case':        parse_match_case,
    'match_cases':       parse_match_cases,
    'expr':              parse_expr,
    'expr_all':          parse_expr_all,       # `a:b:c`, `*not c`, `*st`, `a,`, `a, b`, `a:b:c,`, `a:b:c, x:y:x, *st`, `*not c`
    'expr_arglike':      parse_expr_arglike,   # `*a or b`, `*not c`
    'expr_slice':        parse_expr_slice,     # `a:b:c`, `*not c`, `a:b:c, x:y:z`, `*st` -> `*st,` (py 3.11+)
    'expr_sliceelt':     parse_expr_sliceelt,  # `a:b:c`, `*not c`, `*st`
    'Tuple':             parse_Tuple,          # `a,`, `a, b`, `a:b:c,`, `a:b:c, x:y:x, *st`
    'boolop':            parse_boolop,
    'operator':          parse_operator,
    'binop':             parse_binop,
    'augop':             parse_augop,
    'unaryop':           parse_unaryop,
    'cmpop':             parse_cmpop,
    'comprehension':     parse_comprehension,
    'arguments':         parse_arguments,
    'arguments_lambda':  parse_arguments_lambda,
    'arg':               parse_arg,
    'keyword':           parse_keyword,
    'alias':             parse_alias,
    'alias_dotted':      parse_alias_dotted,
    'alias_star':        parse_alias_star,
    'withitem':          parse_withitem,
    'pattern':           parse_pattern,
    'type_param':        parse_type_param,
    'type_params':       parse_type_params,
    'Assign_targets':    parse_Assign_targets,
    mod:                 parse_Module,    # parsing with an AST type doesn't mean it will be parsable by ast module
    Expression:          parse_Expression,
    Interactive:         parse_Interactive,
    stmt:                parse_stmt,
    ExceptHandler:       parse_ExceptHandler,
    match_case:          parse_match_case,
    expr:                parse_expr,          # not _expr_all because those cases are handled in Starred, Slice and Tuple
    Starred:             parse_expr_arglike,  # because could have form '*a or b' and we want to parse any form of Starred here
    Slice:               parse_expr_slice,    # because otherwise would be parse_expr which doesn't do slice by default, parses '*a' to '*a,' on py 3.11+
    Tuple:               parse_Tuple,         # because could have slice in it and we are parsing all forms including '*not a'
    boolop:              parse_boolop,
    operator:            parse_operator,
    unaryop:             parse_unaryop,
    cmpop:               parse_cmpop,
    comprehension:       parse_comprehension,
    arguments:           parse_arguments,
    arg:                 parse_arg,
    keyword:             parse_keyword,
    alias:               parse_alias,
    withitem:            parse_withitem,
    pattern:             parse_pattern,
    type_param:          parse_type_param,
    Load:                lambda src, parse_params = {}: Load(),  # HACKS for verify() and other similar stuff
    Store:               lambda src, parse_params = {}: Store(),
    Del:                 lambda src, parse_params = {}: Del(),
}

assert not set(get_args(get_args(Mode)[0])).symmetric_difference(k for k in _PARSE_MODE_FUNCS if isinstance(k, str)), \
    'Mode string modes do not match _PARSE_MODE_FUNCS table'
