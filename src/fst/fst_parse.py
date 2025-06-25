"""Extended AST parse and convert `Code` to `FST`."""

from __future__ import annotations

import re
import sys
from ast import *
from ast import parse as ast_parse, unparse as ast_unparse, fix_missing_locations as ast_fix_missing_locations
from typing import Any, Callable
from unicodedata import normalize

from .astutil import *
from .astutil import TryStar, type_param

from .misc import (
    Code, Mode, NodeError, _next_src, _shortstr
)

_re_first_src = re.compile(r'^[^\S\n]*(?:[^\s\\#]|(?<!^)\\)', re.M)  # or first \ not on start of line
_re_except    = re.compile(r'except\b')
_re_case      = re.compile(r'case\b\s*(?:[*\\\w({[\'"-]|\.\d)')

_PY_VERSION = sys.version_info[:2]
_PYLT11     = _PY_VERSION < (3, 11)


def _ast_parse1(src: str, parse_params: dict = {}):
    if len(body := ast_parse(src, **parse_params).body) != 1:
        raise SyntaxError(f'expecting single element')

    return body[0]


def _ast_parse1_case(src: str, parse_params: dict = {}):
    if len(body := ast_parse(src, **parse_params).body) != 1 or len(cases := body[0].cases) != 1:
        raise SyntaxError(f'expecting single element')

    return cases[0]


def _fixing_unparse(ast: AST) -> str:
    try:
        return ast_unparse(ast)

    except AttributeError as exc:
        if not str(exc).endswith("has no attribute 'lineno'"):
            raise

    ast_fix_missing_locations(ast)

    return ast_unparse(ast)


def _validate_indent(src: str, ret: Any = None) -> Any:
    if (m := _re_first_src.search(src)) and len(m.group(0)) > 1:
        raise IndentationError('unexpected indent')

    return ret


def _offset_linenos(ast: AST, delta: int) -> AST:
    for a in walk(ast):
        if end_lineno := getattr(a, 'end_lineno', None):
            a.end_lineno  = end_lineno + delta
            a.lineno     += delta

    return ast


def _fix_unparenthesized_tuple_parsed_parenthesized(src: str, ast: AST):
    elts           = ast.elts
    ast.lineno     = (e0 := elts[0]).lineno
    ast.col_offset = e0.col_offset
    lines          = src.split('\n')
    end_ln         = (e_1 := elts[-1]).end_lineno - 2  # -2 because of extra line introduced in parse
    end_col        = len(lines[end_ln].encode()[:e_1.end_col_offset].decode())  # bistr(lines[end_ln]).b2c(e_1.end_col_offset)

    if (not (code := _next_src(lines, end_ln, end_col, ast.end_lineno - 2, 0x7fffffffffffffff)) or  # if nothing following then last element is ast end
        not code.src.startswith(',')  # if no comma then last element is ast end
    ):
        ast.end_lineno     = e_1.end_lineno
        ast.end_col_offset = e_1.end_col_offset

    else:
        end_ln, end_col, _ = code
        ast.end_lineno     = end_ln + 2
        ast.end_col_offset = len(lines[end_ln][:end_col + 1].encode())


def _code_as_op(code: Code, ast_type: type[AST], parse_params: dict, parse: Callable[[FST, Code], FST],
                opstr2cls: dict[str, type[AST]], opcls2str: dict[type[AST], str] = OPCLS2STR) -> FST:
    """Convert `code` to an operation `FST` if possible."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if not isinstance(codea, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {codea.__class__.__name__}')

        code = code._sanitize()

        if (src := code.src) != (expected := opcls2str[codea.__class__]):
            if isinstance(codea, (NotIn, IsNot)):  # super-stupid case, someone did 'is # comment \n not' or something like this?
                if _parse_cmpop(src).__class__ is codea:  # parses to same thing so just return the canonical str for the op, otherwise it gets complicated
                    return FST(codea, [bistr(expected)], from_=code, lcopy=False)

            raise NodeError(f'expecting {expected!r}, got {_shortstr(src)!r}')

        return code

    if isinstance(code, AST):
        if not isinstance(code, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}')

        return FST(code, [opcls2str[code.__class__]], parse_params=parse_params)

    if isinstance(code, list):
        code = '\n'.join(code)

    lines = (code := code.strip()).split('\n')

    if cls := opstr2cls.get(code):
        return FST(cls(), lines, parse_params=parse_params)

    try:
        return FST(parse(code, parse_params), lines, parse_params=parse_params)  # fall back to actually trying to parse the thing
    except IndentationError:
        raise
    except (SyntaxError, NodeError):
        raise NodeError(f'expecting {ast_type.__name__}, got {_shortstr(code)!r}') from None


def _code_as(code: Code, ast_type: type[AST], parse_params: dict, parse: Callable[[FST, Code], FST], *,
             strip_tup_pars: bool = False) -> FST:
    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(code.a, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.a.__class__.__name__}')

        return code._sanitize()

    if isinstance(code, AST):
        if not isinstance(code, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}')

        code  = (_fixing_unparse(code)[1:-1] if strip_tup_pars and isinstance(code, Tuple) and code.elts else
                 _unparse(code))
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(parse(code, parse_params), lines, parse_params=parse_params)._sanitize()


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

@staticmethod
def _unparse(ast: AST) -> str:
    """AST unparse that handles misc case of comprehension starting with a single space by stripping it."""

    if isinstance(ast, comprehension):  # strip prefix space from this
        return _fixing_unparse(ast).lstrip()

    if src := OPCLS2STR.get(ast.__class__):  # operators don't unparse to anything in ast
        return src

    return _fixing_unparse(ast)


@staticmethod
def _parse(src: str, mode: Mode = 'all', parse_params: dict = {}) -> AST:
    """Parse any source to an AST, including things which normal `ast.parse()` doesn't handle, like individual
    `comprehension`s. Can be given a target type to parse or else will try to various parse methods until it finds one
    that succeeds (if any).

    **WARNING!** Does not guarantee `src` can be plugged directly into a node of the type it is being parsed for without
    parentheses (especially for `Tuple`s).

    **Parameters**:
    - `src`: The source to parse.
    - `mode`: Either one of the standard `ast.parse()` modes `exec`, `eval` or `single` to parse to that type of module
        or one of our specific strings like `'stmtishs'` or an actual `AST` type to parse to. If the mode is provided
        and cannot parse to the specified target then an error is raised and no other parse types are tried. See
        `fst.misc.Mode`.
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

            raise ValueError(f'could not parse to {mode.__name__}, got {ast.__class__.__name__}')

    raise ValueError(f'cannot parse to {mode.__name__}')


@staticmethod
def _parse_all(src: str, parse_params: dict = {}) -> AST:
    """Attempt all parse modes in order from most common / probable to least."""

    for parse in _PARSE_ALL_FUNCS:
        try:
            return parse(src, parse_params)
        except IndentationError:
            raise
        except (SyntaxError, NodeError):
            pass

    raise NodeError('failed to parse in any mode')


@staticmethod
def _parse_most(src: str, parse_params: dict = {}) -> AST:
    """Attempt to parse `stmtishs` and then reduce to a single statement or expressing if possible."""

    return reduce_ast(_parse_stmtishs(src, parse_params), True)


@staticmethod
def _parse_min(src: str, parse_params: dict = {}) -> AST:
    """Attempt to parse valid parsable statements and then reduce to a single statement or expressing if possible."""

    return reduce_ast(ast_parse(src, **parse_params), True)


@staticmethod
def _parse_Module(src: str, parse_params: dict = {}) -> AST:
    """Parse `Module`, ast.parse(mode='exec')'."""

    return ast_parse(src, mode='exec', **parse_params)


@staticmethod
def _parse_Expression(src: str, parse_params: dict = {}) -> AST:
    """Parse `Expression`, `ast.parse(mode='eval')."""

    return ast_parse(src, mode='eval', **parse_params)


@staticmethod
def _parse_Interactive(src: str, parse_params: dict = {}) -> AST:
    """Parse `Interactive`."""

    if not src.endswith('\n'):  # because otherwise error maybe
        src = src + '\n'

    return ast_parse(src, mode='single', **parse_params)


@staticmethod
def _parse_stmtishs(src: str, parse_params: dict = {}) -> AST:
    """Parse zero or more `stmt`s, 'ExceptHander's or 'match_case's and return them in a `Module` `body`."""

    if firstsrc := _re_first_src.search(src):
        if len(firstsrc.group(0)) - 1:
            raise IndentationError('unexpected indent')

        if _re_except.match(src, start := firstsrc.start()):
            return _parse_ExceptHandlers(src, parse_params)

        if _re_case.match(src, start):
            try:
                return _parse_match_cases(src, parse_params)
            except IndentationError:
                raise
            except SyntaxError:  # 'case' is not a protected keyword, the regex checks most cases but not all possible so fall back to parse stmts
                pass

    return _parse_stmts(src, parse_params)


@staticmethod
def _parse_stmtish(src: str, parse_params: dict = {}) -> AST:
    """Parse exactly one `stmt`, `ExceptHandler` or `match_case` and return as itself."""

    mod = _parse_stmtishs(src, parse_params)

    if len(body := mod.body) != 1:
        raise NodeError('expecting single stmt, ExceptHandler or match_case')

    return body[0]


@staticmethod
def _parse_stmts(src: str, parse_params: dict = {}) -> AST:  # same as _parse_Module() but I want the IDE context coloring
    """Parse one or more `stmt`s and return them in a `Module` `body` (just `ast.parse()` basically)."""

    return ast_parse(src, **parse_params)


@staticmethod
def _parse_stmt(src: str, parse_params: dict = {}) -> AST:
    """Parse exactly one `stmt` and return as itself."""

    mod = _parse_stmts(src, parse_params)

    if len(body := mod.body) != 1:
        raise NodeError('expecting single stmt')

    return body[0]


@staticmethod
def _parse_ExceptHandlers(src: str, parse_params: dict = {}) -> AST:
    """Parse zero or more `ExceptHandler`s and return them in a `Module` `body`."""

    try:
        ast = _ast_parse1(f'try: pass\n{src}\nfinally: pass', parse_params)
    except IndentationError:
        raise

    except SyntaxError:
        lines = src.split('\n')  # ugly way to check for IndentationError, TODO: do this clean and quicker with a regex

        if ((firstsrc := _next_src(lines, 0, 0, len(lines) - 1, len(lines[-1]))) and
            firstsrc.col and _re_except.match(firstsrc.src)
        ):
            raise IndentationError('unexpected indent') from None

        try:
            ast = ast_parse(f'try: pass\n{src}', **parse_params)  # just reparse without our finally block to confirm if that was the error
        except SyntaxError:
            pass

        else:
            if len(ast.body) == 1:
                raise NodeError("not expecting 'finally' block") from None
            else:
                raise NodeError('expecting only exception handlers`') from None

        raise

    if ast.orelse:
        raise NodeError("not expecting 'else' block")

    return Module(body=_offset_linenos(ast, -1).handlers, type_ignores=[])


@staticmethod
def _parse_ExceptHandler(src: str, parse_params: dict = {}) -> AST:
    """Parse exactly one `ExceptHandler` and return as itself."""

    mod = _parse_ExceptHandlers(src, parse_params)

    if len(body := mod.body) != 1:
        raise NodeError('expecting single ExceptHandler')

    return body[0]


@staticmethod
def _parse_match_cases(src: str, parse_params: dict = {}) -> AST:
    """Parse zero or more `match_case`s and return them in a `Module` `body`."""

    lines = [bistr('match x:'), bistr(' case None: pass')] + [bistr(' ' + l) for l in src.split('\n')]
    ast   = _ast_parse1('\n'.join(lines), parse_params)
    fst   = FST(ast, lines, parse_params=parse_params, lcopy=False)
    lns   = fst._get_indentable_lns(2, docstr=False)

    if len(lns) != len(lines) - 2:  # if there are multiline strings then we need to dedent them and reparse, because of f-strings, TODO: optimize out second reparse if no f-strings
        strlns = set(range(2, len(lines)))

        strlns.difference_update(lns)

        for ln in strlns:
            lines[ln] = bistr(lines[ln][1:])

        ast = _ast_parse1('\n'.join(lines), parse_params)
        fst = FST(ast, lines, parse_params=parse_params, lcopy=False)

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
def _parse_match_case(src: str, parse_params: dict = {}) -> AST:
    """Parse exactly one `match_case` and return as itself."""

    mod = _parse_match_cases(src, parse_params)

    if len(body := mod.body) != 1:
        raise NodeError('expecting single match_case')

    return body[0]


@staticmethod
def _parse_expr(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.expr`, but only things which are normally valid in an `expr` location, no `Slices` or `Starred`
    expressions only valid as a `Call` arg."""

    try:
        body = ast_parse(src, **parse_params).body
    except SyntaxError:
        pass
    else:
        if len(body) == 1 and isinstance(ast := body[0], Expr):  # if parsed to single expression then done
            return ast.value

    try:
        ast = _ast_parse1(f'(\n{src})', parse_params).value  # has newlines

    except SyntaxError:
        elts = _ast_parse1(f'(\n{src},)', parse_params).value.elts  # Starred expression with newlines
        ast  = elts[0]

        assert isinstance(ast, Starred) and len(elts) == 1

    else:
        if isinstance(ast, Tuple) and ast.lineno == 1:  # tuple with newlines included grouping pars which are not in source, fix
            if not ast.elts:
                raise SyntaxError('expecting expression')

            _fix_unparenthesized_tuple_parsed_parenthesized(src, ast)  # we have to do some work to find a possible comma

    return _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_slice(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.Slice` or anything else that can go into `Subscript.slice` (`expr`), e.g. "start:stop:step" or
    "name" or even "a:b, c:d:e, g". Using this, naked `Starred` expressions parse to single element `Tuple` with the
    `Starred` as the only element."""

    try:
        ast = _ast_parse1(f'a[\n{src}]', parse_params).value.slice

    except SyntaxError:  # maybe 'yield', also could be unparenthesized 'tuple' containing 'Starred' on py 3.10
        ast = _ast_parse1(f'a[(\n{src})]', parse_params).value.slice

        if isinstance(ast, Tuple):  # only py 3.10
            raise SyntaxError('cannot have unparenthesized tuple containing Starred in slice')

    return _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_sliceelt(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.expr` or `ast.Slice`. This exists because otherwise a naked `Starred` expression parses to an
    implicit single element `Tuple` and the caller of this function does not want that behavior. Using this, naked
    `Starred` expressions parse to just the `Starred` and not a `Tuple` like in `_parse_slice()`.
    """

    try:
        ast = _parse_slice(src, parse_params)
    except IndentationError:
        raise
    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11
        return _parse_expr(src, parse_params)

    if (isinstance(ast, Tuple) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and  # check for this one stupid case
        e0.end_col_offset == ast.end_col_offset and e0.end_lineno == ast.end_lineno
    ):
        return e0

    return ast


@staticmethod
def _parse_callarg(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `expr` or in the context of a `Call.args` which treats `Starred` differently."""

    try:
        return _parse_expr(src, parse_params)
    except IndentationError:
        raise
    except (NodeError, SyntaxError):  # stuff like '*[] or []'
        pass

    args = _ast_parse1(f'f(\n{src})', parse_params).value.args

    if len(args) != 1:
        raise NodeError('expecting single call argument expression')

    return _offset_linenos(_validate_indent(src, args[0]), -1)


@staticmethod
def _parse_boolop(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.boolop`."""

    ast = _ast_parse1(f'(a\n{src} b)', parse_params).value

    if not isinstance(ast, BoolOp):
        raise NodeError(f'expecting boolop, got {_shortstr(src)!r}')

    return _validate_indent(src, ast.op.__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_operator(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.boolop`."""

    if '=' in src:
        try:
            return _parse_augop(src, parse_params)
        except NodeError:  # maybe the '=' was in a comment, yes I know, a comment in an operator, people do strange things
            pass

    return _parse_binop(src, parse_params)


@staticmethod
def _parse_binop(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.operator` in the context of a `BinOp`."""

    ast = _ast_parse1(f'(a\n{src} b)', parse_params).value

    if not isinstance(ast, BinOp):
        raise NodeError(f'expecting operator, got {_shortstr(src)!r}')

    return _validate_indent(src, ast.op.__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_augop(src: str, parse_params: dict = {}) -> AST:
    """Parse to an augmented `ast.operator` in the context of a `AugAssign`."""

    ast = _ast_parse1(f'a \\\n{src} b', parse_params)

    if not isinstance(ast, AugAssign):
        raise NodeError(f'expecting augmented operator, got {_shortstr(src)!r}')

    return _validate_indent(src, ast.op.__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_unaryop(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.unaryop`."""

    ast = _ast_parse1(f'(\n{src} b)', parse_params).value

    if not isinstance(ast, UnaryOp):
        raise NodeError(f'expecting unaryop, got {_shortstr(src)!r}')

    return _validate_indent(src, ast.op.__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_cmpop(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.cmpop`."""

    ast = _ast_parse1(f'(a\n{src} b)', parse_params).value

    if not isinstance(ast, Compare):
        raise NodeError(f'expecting cmpop, got {_shortstr(src)!r}')

    if len(ops := ast.ops) != 1:
        raise NodeError('expecting single cmpop')

    return _validate_indent(src, ops[0].__class__())  # parse() returns the same identical object for all instances of the same operator


@staticmethod
def _parse_comprehension(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.comprehension`, e.g. "async for i in something() if i"."""

    ast = _ast_parse1(f'[_ \n{src}]', parse_params).value

    if not isinstance(ast, ListComp):
        raise NodeError('expecting comprehension')

    if len(gens := ast.generators) != 1:
        raise NodeError('expecting single comprehension')

    return _offset_linenos(_validate_indent(src, gens[0]), -1)


@staticmethod
def _parse_arguments(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.arguments`, e.g. "a: list[str], /, b: int = 1, *c, d=100, **e"."""

    ast = _ast_parse1(f'def f(\n{src}): pass', parse_params).args

    return _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_arguments_lambda(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.arguments` for a `Lambda`, e.g. "a, /, b, *c, d=100, **e"."""

    ast = _ast_parse1(f'(lambda \n{src}: None)', parse_params).value.args

    return _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_arg(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.arg`, e.g. "var: list[int]"."""

    try:
        args = _ast_parse1(f'def f(\n{src}): pass', parse_params).args
    except IndentationError:
        raise

    except SyntaxError:  # may be '*vararg: *starred'
        args = _ast_parse1(f'def f(*\n{src}): pass', parse_params).args

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
        raise NodeError('expecting single argument without default')

    return _offset_linenos(_validate_indent(src, ast), -1)


@staticmethod
def _parse_keyword(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.keyword`, e.g. "var=val"."""

    keywords = _ast_parse1(f'f(\n{src})', parse_params).value.keywords

    if len(keywords) != 1:
        raise NodeError('expecting single keyword')

    return _offset_linenos(_validate_indent(src, keywords[0]), -1)


@staticmethod
def _parse_alias(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.alias`, allowing star or dotted notation, e.g. "name as alias"."""

    if '*' in src:
        try:
            return _parse_alias_star(src, parse_params)
        except IndentationError:
            raise
        except SyntaxError:
            pass

    return _parse_alias_dotted(src, parse_params)


@staticmethod
def _parse_alias_dotted(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.alias`, allowing dotted notation (not all aliases are created equal),,
    e.g. "name as alias"."""

    names = _ast_parse1(f'import \\\n{src}', parse_params).names

    if len(names) != 1:
        raise NodeError('expecting single name')

    return _offset_linenos(_validate_indent(src, names[0]), -1)


@staticmethod
def _parse_alias_star(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.alias`, allowing star,."""

    names = _ast_parse1(f'from . import \\\n{src}', parse_params).names

    if len(names) != 1:
        raise NodeError('expecting single name')

    return _offset_linenos(_validate_indent(src, names[0]), -1)


@staticmethod
def _parse_withitem(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.withitem`, e.g. "something() as var"."""

    items = _ast_parse1(f'with (\n{src}): pass', parse_params).items

    if len(items) != 1:  # unparenthesized Tuple
        if all(not i.optional_vars for i in items):
            items = _ast_parse1(f'with ((\n{src})): pass', parse_params).items

        if len(items) != 1:
            raise NodeError('expecting single withitem')

        ast = items[0].context_expr

        assert isinstance(ast, Tuple)

        _fix_unparenthesized_tuple_parsed_parenthesized(src, ast)

    return _offset_linenos(_validate_indent(src, items[0]), -1)


@staticmethod
def _parse_pattern(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.pattern`, e.g. "{a.b: i, **rest}"."""

    try:
        ast = _ast_parse1_case(f'match _:\n case \\\n{src}: pass', parse_params).pattern
    except IndentationError:
        raise

    except SyntaxError:  # first in case needs to be enclosed
        try:
            ast = _ast_parse1_case(f'match _:\n case (\\\n{src}): pass', parse_params).pattern

        except SyntaxError:  # now just the case of a lone MatchStar
            patterns = _ast_parse1_case(f'match _:\n case [\\\n{src}]: pass', parse_params).pattern.patterns

            if len(patterns) != 1:
                raise NodeError('expecting single pattern')

            ast = patterns[0]

        else:
            if ast.lineno < 3 and isinstance(ast, MatchSequence):
                if not (patterns := ast.patterns):
                    raise SyntaxError('empty pattern')

                ast.lineno         = 3  # remove our delimiters from location
                ast.col_offset     = 0
                ast.end_lineno     = (p_1 := patterns[-1]).end_lineno
                ast.end_col_offset = p_1.end_col_offset

    return _offset_linenos(_validate_indent(src, ast), -2)


@staticmethod
def _parse_type_param(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.type_param`, e.g. "t: Base = Subclass"."""

    type_params = _ast_parse1(f'type t[\n{src}] = None', parse_params).type_params

    if len(type_params) != 1:
        raise NodeError('expecting single type_param')

    return _offset_linenos(_validate_indent(src, type_params[0]), -1)


# ......................................................................................................................

@staticmethod
def _code_as_all(code: Code, parse_params: dict = {}) -> FST:  # TODO: allow 'is_trystar'?
    """Convert `code` to any parsable `FST` if possible. If `FST` passed then it is returned as itself."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        return code

    if isinstance(code, AST):
        # if (mode := code.__class__) is Module:  # override _parse_Module because that wouldn't handle slices stmtishs
        #     mode = 'stmtishs'

        mode  = code.__class__
        code  = _unparse(code)
        lines = code.split('\n')

    else:
        mode = 'all'

        if isinstance(code, list):
            code = '\n'.join(lines := code)
        else:  # str
            lines = code.split('\n')

    return FST(_parse(code, mode), lines, parse_params=parse_params)


@staticmethod
def _code_as_stmtishs(code: Code, parse_params: dict = {}, *, is_trystar: bool = False) -> FST:
    """Convert `code` to zero or more `stmtish`s and return in the `body` of a `Module` `FST` if possible. If source
    is passed then will check for presence of `except` or `case` at start to determine if are `ExceptHandler`s or
    `match_case`s or `stmt`s."""

    if is_fst := isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        ast = code.a

    elif isinstance(code, AST):
        ast = code

    else:
        if isinstance(code, list):
            code = '\n'.join(code)

        if firstsrc := _re_first_src.search(code):
            if len(firstsrc.group(0)) - 1:
                raise IndentationError('unexpected indent')

            if _re_except.match(code, start := firstsrc.start()):
                return _code_as_ExceptHandlers(code, parse_params)

            if _re_case.match(code, start):
                try:
                    return _code_as_match_cases(code, parse_params)
                except IndentationError:
                    raise
                except SyntaxError:  # 'case' is not a protected keyword, the regex checks most cases but not all possible so fall back to parse stmts
                    pass

        return _code_as_stmts(code, parse_params)

    if isinstance(ast, (stmt, expr, Expression)):
        return _code_as_stmts(code, parse_params)
    if isinstance(ast, ExceptHandler):
        return _code_as_ExceptHandlers(code, parse_params, is_trystar=is_trystar)
    if isinstance(ast, match_case):
        return _code_as_match_cases(code, parse_params)

    if not (is_mod := isinstance(ast, Module)) and not isinstance(ast, Interactive):
        raise NodeError(f'expecting zero or more stmts, ExceptHandlers or match_cases, got '
                        f'{ast.__class__.__name__}')

    if body := ast.body:
        if isinstance(b0 := body[0], stmt):
            code_type = stmt
        elif isinstance(b0, ExceptHandler):
            code_type = ExceptHandler
        elif isinstance(b0, match_case):
            code_type = match_case
        else:
            code_type = None

        if not code_type or not all(isinstance(a, code_type) for a in body):
            raise NodeError(f'expecting zero or more stmts, ExceptHandlers or match_cases, got '
                            f'[{_shortstr(", ".join(a.__class__.__name__ for a in body))}]')

    if is_fst:
        if is_mod:
            return code

        return FST(Module(body=body, type_ignores=[]), code._lines, from_=code, lcopy=False)

    if not body:
        return FST(Module(body=[], type_ignores=[]), [bistr('')], parse_params=parse_params, lcopy=False)

    if code_type is stmt:
        return _code_as_stmts(code, parse_params)
    if code_type is ExceptHandler:
        return _code_as_ExceptHandlers(code, parse_params, is_trystar=is_trystar)

    return _code_as_match_cases(code, parse_params)


@staticmethod
def _code_as_stmts(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to zero or more `stmt`s and return in the `body` of a `Module` `FST` if possible."""

    if isinstance(code, FST):
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
            return FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, stmt) for a in codea.body):
                return code

            raise NodeError(f'expecting zero or more stmts, got '
                            f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]')

        if isinstance(codea, Interactive):
            code._unmake_fst_parents()

            return FST(Module(body=code.body, type_ignores=[]), code._lines, from_=code, lcopy=False)

        raise NodeError(f'expecting zero or more stmts, got {codea.__class__.__name__}')

    if isinstance(code, AST):
        if not isinstance(code, (stmt, expr, Module, Interactive, Expression)):  # all these can be coerced into stmts
            raise NodeError(f'expecting zero or more stmts, got {code.__class__.__name__}')

        code  = _fixing_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_stmts(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_ExceptHandlers(code: Code, parse_params: dict = {}, *, is_trystar: bool = False) -> FST:
    """Convert `code` to zero or more `ExceptHandler`s and return in the `body` of a `Module` `FST` if possible.

    **Parameters:**
    - `is_trystar`: Hint used when unparsing an `AST` `code` to get the correct `except` or `except*` source.
    """

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if isinstance(codea, ExceptHandler):
            return FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, ExceptHandler) for a in codea.body):
                return code

            raise NodeError(f'expecting zero or more ExceptHandlers, got '
                            f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]')

        raise NodeError(f'expecting zero or more ExceptHandlers, got {codea.__class__.__name__}')

    if isinstance(code, AST):
        if isinstance(code, Module):  # may be slice of ExceptHandlers
            code = _fixing_unparse(code)

        else:
            if not isinstance(code, ExceptHandler):
                raise NodeError(f'expecting zero or more ExceptHandlers, got {code.__class__.__name__}')

            if is_trystar:
                code = unparse(TryStar(body=[Pass()], handlers=[code], orelse=[], finalbody=[]))
                code = code[code.index('except'):]
            else:
                code = _fixing_unparse(code)

        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_ExceptHandlers(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_match_cases(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to zero or more `match_case`s and return in the `body` of a `Module` `FST` if possible."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if isinstance(codea, match_case):
            return FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, match_case) for a in codea.body):
                return code

            raise NodeError(f'expecting zero or more match_cases, got '
                            f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]')

        raise NodeError(f'expecting zero or more match_cases, got {codea.__class__.__name__}')

    if isinstance(code, AST):
        if not isinstance(code, (match_case, Module)):
            raise NodeError(f'expecting zero or more match_cases, got {code.__class__.__name__}')

        code  = _fixing_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_match_cases(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_expr(code: Code, parse_params: dict = {}, parse: Callable[[Code, dict], FST] = _parse_expr) -> FST:
    """Convert `code` to an `expr` or optionally `Slice` `FST` if possible.

    **Parameters:**
    - `orslice`: If `True` then will try to get `expr` or `Slice`. Useful for parsing elements of `Tuple`s which could
        be used inside a `Subscript.slice`. Do not use for parsing `Subscript.slice` field itself because that behaves
        different with respect to naked `Starred` elements, for that use `_code_as_slice`.
    """

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(ast := reduce_ast(codea := code.a, NodeError), expr):
            raise NodeError('expecting ' +
                ("slice " if parse is _parse_sliceelt else "call arg " if parse is _parse_callarg else "") +
                f'expression, got {ast.__class__.__name__}')

        if ast is codea:
            return code._sanitize()

        ast.f._unmake_fst_parents()

        return FST(ast, code._lines, from_=code, lcopy=False)._sanitize()

    if isinstance(code, AST):
        if not isinstance(code, expr):
            raise NodeError('expecting ' +
                ("slice " if parse is _parse_sliceelt else "call arg " if parse is _parse_callarg else "") +
                f'expression, got {code.__class__.__name__}')

        code  = _fixing_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(parse(code, parse_params), lines, parse_params=parse_params)._sanitize()


@staticmethod
def _code_as_slice(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a Slice `FST` if possible (or anthing else that can serve in `Subscript.slice`, like any old
    generic `expr`)."""

    strip_tup_pars = not _PYLT11 or (isinstance(code, Tuple) and any(isinstance(e, Slice) for e in code.elts))

    ret = _code_as(code, expr, parse_params, _parse_slice, strip_tup_pars=strip_tup_pars)

    if isinstance(code, AST) and not isinstance(ret.a, code.__class__):  # because could reparse Starred into a single element Tuple with Starred
        raise NodeError(f'cannot reparse {code.__class__.__name__} in slice as {code.__class__.__name__}')

    return ret


@staticmethod
def _code_as_sliceelt(code: Code, parse_params: dict = {}, orslice: bool = False) -> FST:
    """Convert `code` to an `expr` or `Slice` `FST` if possible. This exists because of the behavior of naked `Starred`
    expressions in a `Subscript` `slice` field."""

    return _code_as_expr(code, parse_params, _parse_sliceelt)


@staticmethod
def _code_as_callarg(code: Code, parse_params: dict = {}, orslice: bool = False) -> FST:
    """Convert `code` to an `expr` in the context of a `Call.args` which has special parse rules for `Starred`."""

    return _code_as_expr(code, parse_params, _parse_callarg)


@staticmethod
def _code_as_boolop(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a `boolop` `FST` if possible."""

    return _code_as_op(code, boolop, parse_params, _parse_boolop, OPSTR2CLS_BOOL)


@staticmethod
def _code_as_binop(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a `operator` `FST` if possible."""

    return _code_as_op(code, operator, parse_params, _parse_binop, OPSTR2CLS_BIN)


@staticmethod
def _code_as_augop(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to an augmented `operator` `FST` if possible, e.g. "+="."""

    return _code_as_op(code, operator, parse_params, _parse_augop, OPSTR2CLS_AUG, OPCLS2STR_AUG)


@staticmethod
def _code_as_unaryop(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a `unaryop` `FST` if possible."""

    return _code_as_op(code, unaryop, parse_params, _parse_unaryop, OPSTR2CLS_UNARY)


@staticmethod
def _code_as_cmpop(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a `cmpop` `FST` if possible."""

    return _code_as_op(code, cmpop, parse_params, _parse_cmpop, OPSTR2CLS_CMP)


@staticmethod
def _code_as_comprehension(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(code, comprehension, parse_params, _parse_comprehension)


@staticmethod
def _code_as_arguments(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a arguments `FST` if possible."""

    return _code_as(code, arguments, parse_params, _parse_arguments)


@staticmethod
def _code_as_arguments_lambda(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a lambda arguments `FST` if possible (no annotations allowed)."""

    return _code_as(code, arguments, parse_params, _parse_arguments_lambda)


@staticmethod
def _code_as_arg(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to an arg `FST` if possible."""

    return _code_as(code, arg, parse_params, _parse_arg)


@staticmethod
def _code_as_keyword(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a keyword `FST` if possible."""

    return _code_as(code, keyword, parse_params, _parse_keyword)


@staticmethod
def _code_as_alias(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a alias `FST` if possible, star or dotted."""

    return _code_as(code, alias, parse_params, _parse_alias)


@staticmethod
def _code_as_alias_dotted(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a alias `FST` if possible, dotted as in `alias` for `Import.names`."""

    ret = _code_as(code, alias, parse_params, _parse_alias_dotted)

    if '*' in ret.a.name:
        raise NodeError("'*' not allowed in this alias")

    return ret


@staticmethod
def _code_as_alias_star(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a alias `FST` if possible, possibly star as in `alias` for `FromImport.names`."""

    ret = _code_as(code, alias, parse_params, _parse_alias_star)

    if '.' in ret.a.name:
        raise NodeError("'.' not allowed in this alias")

    return ret


@staticmethod
def _code_as_withitem(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(code, withitem, parse_params, _parse_withitem)


@staticmethod
def _code_as_pattern(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a pattern `FST` if possible."""

    return _code_as(code, pattern, parse_params, _parse_pattern)


@staticmethod
def _code_as_type_param(code: Code, parse_params: dict = {}) -> FST:
    """Convert `code` to a type_param `FST` if possible."""

    return _code_as(code, type_param, parse_params, _parse_type_param)


@staticmethod
def _code_as_identifier(code: Code, parse_params: dict = {}) -> str:
    """Convert `code` to valid identifier string if possible."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier(code):
        raise NodeError(f'expecting identifier, got {_shortstr(code)!r}')

    return normalize('NFKC', code)


@staticmethod
def _code_as_identifier_dotted(code: Code, parse_params: dict = {}) -> str:
    """Convert `code` to valid dotted identifier string if possible (for Import module)."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_dotted(code):
        raise NodeError(f'expecting dotted identifier, got {_shortstr(code)!r}')

    return normalize('NFKC', code)


@staticmethod
def _code_as_identifier_star(code: Code, parse_params: dict = {}) -> str:
    """Convert `code` to valid identifier string or star '*' if possible (for ImportFrom names)."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_star(code):
        raise NodeError(f"expecting identifier or '*', got {_shortstr(code)!r}")

    return normalize('NFKC', code)


@staticmethod
def _code_as_identifier_alias(code: Code, parse_params: dict = {}) -> str:
    """Convert `code` to valid dotted identifier string or star '*' if possible (for any alias)."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_alias(code):
        raise NodeError(f"expecting dotted identifier or '*', got {_shortstr(code)!r}")

    return normalize('NFKC', code)


@staticmethod
def _code_as_constant(code: constant, parse_params: dict = {}) -> constant:
    """Convert `code` to valid constant if possible. If `code` is a `str` then it is treated as the constant value and
    not as the python representation of the constant. The only `FST` or `AST` accepted is a `Constant`, whose `value` is
    returned."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.a

    if isinstance(code, AST):
        if not isinstance(code, Constant):
            raise NodeError('expecting constant')

        code = code.value

    elif isinstance(code, list):
        code = '\n'.join(code)
    elif not isinstance(code, constant):
        raise NodeError('expecting constant')

    return code


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]  # used by make_docs.py

_PARSE_ALL_FUNCS = [
    _parse_most,
    _parse_expr,     # explicitly this because _parse_most won't catch unparenthesized expressions with newlines
    _parse_pattern,
    _parse_arguments,
    _parse_arguments_lambda,
    _parse_sliceelt,
    _parse_callarg,
    _parse_comprehension,
    _parse_withitem,
    _parse_arg,      # because of 'vararg: *starred'
    _parse_operator,
    _parse_cmpop,
    _parse_boolop,
    _parse_unaryop,
]

_PARSE_MODE_FUNCS = {
    'all':               _parse_all,
    'most':              _parse_most,
    'min':               _parse_min,
    'exec':              _parse_Module,
    'eval':              _parse_Expression,
    'single':            _parse_Interactive,
    'stmtishs':          _parse_stmtishs,
    'stmtish':           _parse_stmtish,
    'stmts':             _parse_stmts,
    'stmt':              _parse_stmt,
    'ExceptHandlers':    _parse_ExceptHandlers,
    'ExceptHandler':     _parse_ExceptHandler,
    'match_cases':       _parse_match_cases,
    'match_case':        _parse_match_case,
    'expr':              _parse_expr,
    'slice':             _parse_slice,
    'sliceelt':          _parse_sliceelt,
    'callarg':           _parse_callarg,
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
    mod:                 _parse_Module,    # parsing with an AST type doesn't mean it will be parsable by ast module
    Module:              _parse_stmtishs,  # _parse_Module,
    Expression:          _parse_Expression,
    Interactive:         _parse_Interactive,
    stmt:                _parse_stmt,
    ExceptHandler:       _parse_ExceptHandler,
    match_case:          _parse_match_case,
    expr:                _parse_expr,
    Starred:             _parse_callarg,   # because could have form '*a or b' and we want to parse any form of Starred here
    Tuple:               _parse_sliceelt,  # because could have slice in it and ditto on any form here
    Slice:               _parse_slice,     # because otherwise would be _parse_expr which doesn't do slice by default
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

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
