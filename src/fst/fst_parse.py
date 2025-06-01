"""Misc lower level FST methods."""

import re
from ast import *
from ast import parse as ast_parse, unparse as ast_unparse
from typing import Callable, Literal

from .astutil import *
from .astutil import TryStar, type_param

from .shared import (
    Code, NodeError, _next_src, _shortstr
)

_re_except = re.compile(r'except\b')
_re_case   = re.compile(r'case\b\s*(?:[*\\\w({[\'"-]|\.\d)')


def _offset_linenos(ast: AST, delta: int) -> AST:
    for a in walk(ast):
        if end_lineno := getattr(a, 'end_lineno', None):
            a.end_lineno  = end_lineno + delta
            a.lineno     += delta

    return ast


def _code_as_op(code: Code, ast_type: type[AST], parse_params: dict, opstr2cls: dict[str, type[AST]],
                 opcls2str: dict[type[AST], str] = OPCLS2STR) -> 'FST':
    """Convert `code` to an operation `FST` if possible."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(code.a, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.a.__class__.__name__}')

        if (src := code.get_src(*code.loc)) != (expected := opcls2str[code.a.__class__]):
            raise NodeError(f'expecting {expected!r}, got {_shortstr(src)!r}')

        return code

    if isinstance(code, AST):
        if not isinstance(code, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}')

        return FST(code, [opcls2str[code.__class__]], parse_params=parse_params)

    if isinstance(code, list):
        code = '\n'.join(code)

    if not (cls := opstr2cls.get(code := code.strip())):
        raise NodeError(f'expecting {ast_type.__name__}, got {_shortstr(code)!r}')

    return FST(cls(), code.split('\n'), parse_params=parse_params)


def _code_as(code: Code, ast_type: type[AST], parse_params: dict, parse: Callable[['FST', Code], 'FST'], *,
             tup_pars: bool = True) -> 'FST':
    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(code.a, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.a.__class__.__name__}')

        return code._sanitize()

    if isinstance(code, AST):
        if not isinstance(code, ast_type):
            raise NodeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}')

        code  = (ast_unparse(code)[1:-1] if not tup_pars and isinstance(code, Tuple) and code.elts else
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
def _unparse(ast: AST) -> AST:
    """AST unparse that handles misc case of comprehension starting with a single space by stripping it."""

    return ast_unparse(ast).lstrip() if isinstance(ast, comprehension) else ast_unparse(ast)


@staticmethod
def _parse(src: str, mode: str | type[AST] | None = None, parse_params: dict = {}) -> AST:
    """Parse any source to an AST, including things which normal `ast.parse()` doesn't handle like individual
    `comprehension`s. Can be given a target type to parse or else will try to various parse methods until it finds one
    that succeeds (if any).

    **Parameters**:
    - `src`: The source to parse.
    - `mode`: Either one of the standard `ast.parse()` modes `exec`, `eval` or `single` to parse to that type of module
        or one of our specific strings like `'stmtishs'` or an actual `AST` type to parse to. If the mode is provided
        and cannot parse to the specified target then an error is raised and no other parse types are tried.
        Options are:
        - `'exec'`: Parse to an `Module`. Same as passing `Module` type.
        - `'eval'`: Parse to an `Expression`. Same as passing `Expression` type.
        - `'single'`: Parse to an `Interactive`. Same as passing `Interactive` type.
        - `'stmtishs'`: Parse as zero or more of either `stmt`, `ExceptHandler` or `match_case` returned in a `Module`.
        - `'stmtish'`: Parse as a single `stmt`, `ExceptHandler` or `match_case` returned as itself.
        - `'stmts'`: Parse zero or more `stmt`s returned in a `Module`. Same as passing `Module` type or `'exec'`.
        - `'stmt'`: Parse a single `stmt` returned as itself. Same as passign `stmt` type.
        - `'ExceptHandlers'`: Parse zero or more `ExceptHandler`s returned in a `Module`.
        - `'ExceptHandler'`: Parse as a single `ExceptHandler` returned as itself. Same as passing `ExceptHandler` type.
        - `'match_cases'`: Parse zero or more `match_case`s returned in a `Module`.
        - `'match_case'`: Parse a single `match_case` returned as itself. Same as passing `match_case` type.
        - `'expr'`: Parse a single `expr` returned as itself. This is differentiated from the following three modes by
            the handling of slices and starred expressions. In this mode `a:b` and `*not v` are syntax errors. Same as
            passing `expr` type.
        - `'expr_slice'`: Same as `expr` except that in this mode `a:b` parses to a `Slice` and `*not v` parses to
            a single element tuple containing a starred expression `(*(not v),)`.
        - `'expr_slice_tupelt'`: Same as `expr` except that in this mode `a:b` parses to a `Slice` and `*not v` parses
            to a starred expression `*(not v)`.
        - `'expr_callarg'`: Same as `expr` except that in this mode `a:b` is a syntax error and `*not v` parses to a
            starred expression `*(not v)`.
        - `'comprehension'`: Parse a single `comprehension` returned as itself. Same as passing `comprehension` type.
        - `'arguments'`: Parse as `arguments` for a `FunctionDef` or `AsyncFunctionDef` returned as itself. In this mode
            type annotations are allowed for the arguments. Same as passing `arguments` type.
        - `'arguments_lambda'`: Parse as `arguments` for a `Lambda` returned as itself. In this mode type annotations
            are not allowed for the arguments.
        - `'arg'`: Parse as a single `arg` returned as itself. Same as passing `arg` type.
        - `'keyword'`: Parse as a single `keyword` returned as itself. Same as passing `keyword` type.
        - `'alias'`: Parse as a single `alias` returned as itself. Either starred or dotted versions are accepted. Same
            as passing `alias` type.
        - `'alias_dotted'`: Parse as a single `alias` returned as itself, with starred version being a syntax error.
        - `'alias_star'`: Parse as a single `alias` returned as itself, with dotted version being a syntax error.
        - `'withitem'`: Parse as a single `withitem` returned as itself. Same as passing `withitem` type.
        - `'pattern'`: Parse as a a single `pattern` returned as itself. Same as passing `pattern` type.
        - `'type_param'`: Parse as a single `type_param` returned as itself, either `TypeVar`, `ParamSpec` or
            `TypeVarTuple`. Same as passing `type_param` type.
        - `type[AST]`: If an `AST` type is passed then will attempt to parse to this type. This can be used to narrow
            the scope of desired return, for example `Constant` will parse expression but fail if the expression is not
            a `Constant`. These overlap with the string specifiers to an extent but not all of them. For example `AST`
            type `ast.expr` is the same as passign `'expr'` but there is not `AST` type which will specify one of the
            other expr parse modes. Likewise `Module`, `'exec'` and `'stmts'` all specify the same thing.

    - `parse_params`: Dictionary of optional parse parameters to pass to `ast.parse()`, can contain `filename`,
        `type_comments` and `feature_version`.
    """


@staticmethod
def _parse_stmts(src: str, parse_params: dict = {}) -> AST:
    """Parse one or more `stmt`s and return them in a `Module` `body` (just `ast.parse()` basically)."""

    return ast_parse(src, **parse_params)


@staticmethod
def _parse_expr(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.expr` or raise `SyntaxError`."""

    body = ast_parse(src, **parse_params).body

    if len(body) != 1:
        raise NodeError('expecting single expression')
    elif not isinstance(ast := body[0], Expr):
        raise NodeError(f'expecting expression, got {ast.__class__.__name__}')

    return ast.value


@staticmethod
def _parse_expr_slice(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.Slice` or anything else that can go into `Subscript.slice` (`expr`) or raise `SyntaxError`, e.g.
    "start:stop:step" or "name" or even "a:b, c:d:e, g". Using this, naked `Starred` expressions parse to single element
    `Tuple` with the `Starred` as the only element."""

    return _offset_linenos(ast_parse(f'a[\n{src}]', **parse_params).body[0].value.slice, -1)


@staticmethod
def _parse_expr_slice_tupelt(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.expr` or `ast.Slice` or raise `SyntaxError`. This exists because otherwise a naked `Starred`
    expression parses to an implicit single element `Tuple` and the caller of this function does not want that behavior.
    Using this, naked `Starred` expressions parse to just the `Starred` and not a `Tuple` like in `_parse_expr_slice()`.
    """

    try:
        ast = _parse_expr_slice(src, parse_params)
    except SyntaxError:  # in case of lone naked Starred in slice in py < 3.11
        return _parse_expr(src, parse_params)

    if (isinstance(ast, Tuple) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and  # check for this one stupid case
        e0.end_col_offset == ast.end_col_offset and e0.end_lineno == ast.end_lineno
    ):
        return e0

    return ast


@staticmethod
def _parse_expr_call_arg(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `expr` or in the context of a `Call.args` which treats `Starred` differently."""

    try:
        return _parse_expr(src, parse_params)
    except SyntaxError:  # stuff like '*[] or []'
        return _offset_linenos(ast_parse(f'f(\n{src})', **parse_params).body[0].value.args[0], -1)


@staticmethod
def _parse_comprehension(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.comprehension` or raise `SyntaxError`, e.g. "async for i in something() if i"."""

    return _offset_linenos(ast_parse(f'[_ \n{src}]', **parse_params).body[0].value.generators[0], -1)


@staticmethod
def _parse_ExceptHandlers(src: str, parse_params: dict = {}) -> AST:
    """Parse one or more `ExceptHandler`s and return them in a `Module` `body` or raise `SyntaxError`."""

    ast = ast_parse(f'try: pass\n{src}', **parse_params).body[0]

    if ast.orelse or ast.finalbody:
        raise SyntaxError("not expecting 'else' or 'finally' blocks")

    return Module(body=_offset_linenos(ast, -1).handlers, type_ignores=[])


@staticmethod
def _parse_arguments(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.arguments` or raise `SyntaxError`, e.g. "a: list[str], /, b: int = 1, *c, d=100, **e"."""

    return _offset_linenos(ast_parse(f'def f(\n{src}): pass', **parse_params).body[0].args, -1)


@staticmethod
def _parse_arguments_lambda(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.arguments` for a `Lambda` or raise `SyntaxError`, e.g. "a, /, b, *c, d=100, **e"."""

    return _offset_linenos(ast_parse(f'lambda \\\n{src}: None', **parse_params).body[0].value.args, -1)


@staticmethod
def _parse_arg(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.arg` or raise `SyntaxError`, e.g. "var: list[int]"."""

    try:
        ast = ast_parse(f'def f(\n{src}): pass', **parse_params).body[0].args.args[0]
    except SyntaxError:  # may be '*vararg: *starred'
        ast = ast_parse(f'def f(*\n{src}): pass', **parse_params).body[0].args.vararg

    return _offset_linenos(ast, -1)


@staticmethod
def _parse_keyword(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.keyword` or raise `SyntaxError`, e.g. "var=val"."""

    return _offset_linenos(ast_parse(f'f(\n{src})', **parse_params).body[0].value.keywords[0], -1)


@staticmethod
def _parse_alias(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.alias` or raise `SyntaxError`, allowing star or dotted notation, e.g. "name as alias"."""

    if '*' in src:
        try:
            return _parse_alias_star(src, parse_params)
        except SyntaxError:
            pass

    return _parse_alias_dotted(src, parse_params)


@staticmethod
def _parse_alias_dotted(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.alias`, allowing dotted notation (not all aliases are created equal), or raise `SyntaxError`,
    e.g. "name as alias"."""

    return _offset_linenos(ast_parse(f'import \\\n{src}', **parse_params).body[0].names[0], -1)


@staticmethod
def _parse_alias_star(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.alias`, allowing star, or raise `SyntaxError`."""

    return _offset_linenos(ast_parse(f'from . import \\\n{src}', **parse_params).body[0].names[0], -1)


@staticmethod
def _parse_withitem(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.withitem` or raise `SyntaxError`, e.g. "something() as var"."""

    return _offset_linenos(ast_parse(f'with (\n{src}): pass', **parse_params).body[0].items[0], -1)


@staticmethod
def _parse_match_cases(src: str, parse_params: dict = {}) -> AST:
    """Parse one or more `match_case`s and return them in a `Module` `body` or raise `SyntaxError`."""

    lines = [bistr('match x:')] + [bistr(' ' + l) for l in src.split('\n')]
    ast   = ast_parse('\n'.join(lines), **parse_params)
    fst   = FST(ast, lines, parse_params=parse_params, lcopy=False)
    lns   = fst.get_indentable_lns(docstr=False)

    if len(lns) != len(lines):  # if there are multiline strings then we need to dedent them and reparse, because of f-strings, TODO: optimize out second reparse if no f-strings
        strlns = set(range(len(lines)))

        strlns.difference_update(lns)

        for ln in strlns:
            lines[ln] = bistr(lines[ln][1:])

        ast = ast_parse('\n'.join(lines), **parse_params)
        fst = FST(ast, lines, parse_params=parse_params, lcopy=False)

    for ln in lns:
        lines[ln] = bistr(lines[ln][1:])

    for a in walk(ast):
        if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
            a.lineno     = lineno     = a.lineno - 1
            a.end_lineno = end_lineno = a.end_lineno - 1

            if lineno in lns:
                a.col_offset -= 1

            if end_lineno in lns:
                a.end_col_offset = end_col_offset - 1

    return Module(body=ast.body[0].cases, type_ignores=[])


@staticmethod
def _parse_pattern(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.pattern` or raise `SyntaxError`, e.g. "{a.b: i, **rest}"."""

    try:
        ast = ast_parse(f'match _:\n case \\\n{src}: pass', **parse_params).body[0].cases[0].pattern
    except SyntaxError:  # in case of lone MatchStar, and we can't just do MatchSequence first because would mess up location of naked MatchSequence
        ast = ast_parse(f'match _:\n case [\\\n{src}]: pass', **parse_params).body[0].cases[0].pattern.patterns[0]

    return _offset_linenos(ast, -2)


@staticmethod
def _parse_type_param(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.type_param` or raise `SyntaxError`, e.g. "t: Base = Subclass"."""

    return _offset_linenos(ast_parse(f'type t[\n{src}] = None', **parse_params).body[0].type_params[0], -1)


# ......................................................................................................................

@staticmethod
def _code_as_stmts(code: Code, parse_params: dict = {}) -> 'FST':
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

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_stmts(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_expr(code: Code, parse_params: dict = {}, parse: Callable[[Code, dict], 'FST'] = _parse_expr) -> 'FST':
    """Convert `code` to an `expr` or optionally `Slice` `FST` if possible.

    **Parameters:**
    - `orslice`: If `True` then will try to get `expr` or `Slice`. Useful for parsing elements of `Tuple`s which could
        be used inside a `Subscript.slice`. Do not use for parsing `Subscript.slice` field itself because that behaves
        different with respect to naked `Starred` elements, for that use `_code_as_expr_slice`.
    """

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(ast := reduce_ast(codea := code.a, NodeError), expr):
            raise NodeError('expecting ' +
                ("slice " if parse is _parse_expr_slice_tupelt else "call arg " if parse is _parse_expr_call_arg else "") +
                f'expression, got {ast.__class__.__name__}')

        if ast is codea:
            return code._sanitize()

        ast.f._unmake_fst_parents()

        return FST(ast, code._lines, from_=code, lcopy=False)._sanitize()

    if isinstance(code, AST):
        if not isinstance(code, expr):
            raise NodeError('expecting ' +
                ("slice " if parse is _parse_expr_slice_tupelt else "call arg " if parse is _parse_expr_call_arg else "") +
                f'expression, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(parse(code, parse_params), lines, parse_params=parse_params)._sanitize()


@staticmethod
def _code_as_expr_slice(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a Slice `FST` if possible (or anthing else that can serve in `Subscript.slice`, like any old
    generic `expr`)."""

    return _code_as(code, expr, parse_params, _parse_expr_slice, tup_pars=False)


@staticmethod
def _code_as_expr_slice_tupelt(code: Code, parse_params: dict = {}, orslice: bool = False) -> 'FST':
    """Convert `code` to an `expr` or `Slice` `FST` if possible. This exists because of the behavior of naked `Starred`
    expressions in a `Subscript` `slice` field."""

    return _code_as_expr(code, parse_params, _parse_expr_slice_tupelt)


@staticmethod
def _code_as_expr_call_arg(code: Code, parse_params: dict = {}, orslice: bool = False) -> 'FST':
    """Convert `code` to an `expr` in the context of a `Call.args` which has special parse rules for `Starred`."""

    return _code_as_expr(code, parse_params, _parse_expr_call_arg)


@staticmethod
def _code_as_boolop(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a `boolop` `FST` if possible."""

    return _code_as_op(code, boolop, parse_params, OPSTR2CLS_BOOL)


@staticmethod
def _code_as_operator(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a `operator` `FST` if possible."""

    return _code_as_op(code, operator, parse_params, OPSTR2CLS_BIN)


@staticmethod
def _code_as_operator_aug(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to an augmented `operator` `FST` if possible, e.g. "+="."""

    return _code_as_op(code, operator, parse_params, OPSTR2CLS_AUG, OPCLS2STR_AUG)


@staticmethod
def _code_as_unaryop(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a `unaryop` `FST` if possible."""

    return _code_as_op(code, unaryop, parse_params, OPSTR2CLS_UNARY)


@staticmethod
def _code_as_cmpop(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a `cmpop` `FST` if possible."""

    return _code_as_op(code, cmpop, parse_params, OPSTR2CLS_CMP)


@staticmethod
def _code_as_comprehension(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(code, comprehension, parse_params, _parse_comprehension)


@staticmethod
def _code_as_ExceptHandlers(code: Code, parse_params: dict = {}, *, is_trystar: bool = False) -> 'FST':
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
        if not isinstance(code, ExceptHandler):
            raise NodeError(f'expecting zero or more ExceptHandlers, got {code.__class__.__name__}')

        if is_trystar:
            code = unparse(TryStar(body=[Pass()], handlers=[code], orelse=[], finalbody=[]))
            code = code[code.index('except'):]
        else:
            code = ast_unparse(code)

        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_ExceptHandlers(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_arguments(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a arguments `FST` if possible."""

    return _code_as(code, arguments, parse_params, _parse_arguments)


@staticmethod
def _code_as_arguments_lambda(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a lambda arguments `FST` if possible (no annotations allowed)."""

    return _code_as(code, arguments, parse_params, _parse_arguments_lambda)


@staticmethod
def _code_as_arg(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to an arg `FST` if possible."""

    return _code_as(code, arg, parse_params, _parse_arg)


@staticmethod
def _code_as_keyword(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a keyword `FST` if possible."""

    return _code_as(code, keyword, parse_params, _parse_keyword)


@staticmethod
def _code_as_alias(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a alias `FST` if possible, star or dotted."""

    return _code_as(code, alias, parse_params, _parse_alias)


@staticmethod
def _code_as_alias_dotted(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a alias `FST` if possible, dotted as in `alias` for `Import.names`."""

    return _code_as(code, alias, parse_params, _parse_alias_dotted)


@staticmethod
def _code_as_alias_star(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a alias `FST` if possible, possibly star as in `alias` for `FromImport.names`."""

    return _code_as(code, alias, parse_params, _parse_alias_star)


@staticmethod
def _code_as_withitem(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(code, withitem, parse_params, _parse_withitem)


@staticmethod
def _code_as_match_cases(code: Code, parse_params: dict = {}) -> 'FST':
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
        if not isinstance(code, match_case):
            raise NodeError(f'expecting zero or more match_cases, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_match_cases(code, parse_params), lines, parse_params=parse_params)


@staticmethod
def _code_as_pattern(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a pattern `FST` if possible."""

    return _code_as(code, pattern, parse_params, _parse_pattern)


@staticmethod
def _code_as_type_param(code: Code, parse_params: dict = {}) -> 'FST':
    """Convert `code` to a type_param `FST` if possible."""

    return _code_as(code, type_param, parse_params, _parse_type_param)


@staticmethod
def _code_as_identifier(code: Code, parse_params: dict = {}) -> str:
    """Convert `Code` to valid identifier string if possible."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = ast_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier(code):
        raise NodeError(f'expecting identifier, got {_shortstr(code)!r}')

    return code


@staticmethod
def _code_as_identifier_dotted(code: Code, parse_params: dict = {}) -> str:
    """Convert `Code` to valid dotted identifier string if possible (for Import module)."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = ast_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_dotted(code):
        raise NodeError(f'expecting dotted identifier, got {_shortstr(code)!r}')

    return code


@staticmethod
def _code_as_identifier_star(code: Code, parse_params: dict = {}) -> str:
    """Convert `Code` to valid identifier string or star '*' if possible (for ImportFrom names)."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = ast_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_star(code):
        raise NodeError(f"expecting identifier or '*', got {_shortstr(code)!r}")

    return code


@staticmethod
def _code_as_identifier_alias(code: Code, parse_params: dict = {}) -> str:
    """Convert `Code` to valid dotted identifier string or star '*' if possible (for any alias)."""

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code.src

    elif isinstance(code, AST):
        code = ast_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_alias(code):
        raise NodeError(f"expecting dotted identifier or '*', got {_shortstr(code)!r}")

    return code


@staticmethod
def _code_as_stmtishs(code: Code, parse_params: dict = {}, *, is_trystar: bool = False) -> 'FST':
    """Convert `code` to zero or more `stmtish`s and return in the `body` of a `Module` `FST` if possible. If source
    is passed then will check for presence of `except` or `case` at start to determine if are `ExceptHandler`s or
    `match_case`s or `stmt`s."""

    if is_fst := isinstance(code, FST):
        ast = code.a
    elif isinstance(code, AST):
        ast = code

    else:
        if isinstance(code, list):
            code = '\n'.join(lines := code)
        else:  # str
            lines = code.split('\n')

        if firstsrc := _next_src(lines, 0, 0, len(lines) - 1, len(lines[-1])):
            if _re_except.match(firstsrc.src):
                return _code_as_ExceptHandlers(code, parse_params)

            if _re_case.match(lines[firstsrc.ln], firstsrc.col):  # need full line because firstsrc.src is cut off at first space
                try:
                    return _code_as_match_cases(code, parse_params)
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


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
