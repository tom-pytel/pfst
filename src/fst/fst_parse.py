"""Misc lower level FST methods."""

from ast import *
from ast import parse as ast_parse, unparse as ast_unparse
from typing import Callable

from .astutil import *
from .astutil import type_param, TypeVar, ParamSpec, TypeVarTuple

from .shared import (
    Code, NodeTypeError, _shortstr
)

_code_as_op_str2op = {
    AugAssign: OPSTR2CLS_AUG,
    BoolOp:    OPSTR2CLS_BOOL,
    BinOp:     OPSTR2CLS_BIN,
    UnaryOp:   OPSTR2CLS_UNARY,
    Compare:   OPSTR2CLS_CMP,
    None:      OPSTR2CLSWAUG,
}

_code_as_op_ops = {
    AugAssign: frozenset(OPSTR2CLS_AUG.values()),
    BoolOp:    frozenset(OPSTR2CLS_BOOL.values()),
    BinOp:     frozenset(OPSTR2CLS_BIN.values()),
    UnaryOp:   frozenset(OPSTR2CLS_UNARY.values()),
    Compare:   frozenset(OPSTR2CLS_CMP.values()),
    None:      frozenset(OPSTR2CLS.values()),
}


def _offset_linenos(ast: AST, delta: int) -> AST:
    for a in walk(ast):
        if end_lineno := getattr(a, 'end_lineno', None):
            a.end_lineno  = end_lineno + delta
            a.lineno     += delta

    return ast


def _code_as_op(self: 'FST', code: Code, ast_type: type[AST], opstr2cls: dict[str, type[AST]],
                 opcls2str: dict[type[AST], str] = OPCLS2STR) -> 'FST':
    """Convert `code` to an operation `FST` if possible."""

    if isinstance(code, FST):
        if not isinstance(code.a, ast_type):
            raise NodeTypeError(f'expecting {ast_type.__name__}, got {code.a.__class__.__name__}')

        if (src := code.get_src(*code.loc)) != (expected := opcls2str[code.a.__class__]):
            raise NodeTypeError(f'expecting {expected!r}, got {_shortstr(src)!r}')

        return code

    if isinstance(code, AST):
        if not isinstance(code, ast_type):
            raise NodeTypeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}')

        return FST(code, [opcls2str[code.__class__]], parse_params=self.root.parse_params)

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    if not (cls := opstr2cls.get(code := code.strip())):
        raise NodeTypeError(f'expecting {ast_type.__name__}, got {_shortstr(code)!r}')

    return FST(cls(), lines, parse_params=self.root.parse_params)


def _code_as(self: 'FST', code: Code, ast_type: type[AST], parse: Callable[['FST', Code], 'FST']) -> 'FST':
    if isinstance(code, FST):
        if not isinstance(code.a, ast_type):
            raise NodeTypeError(f'expecting {ast_type.__name__}, got {code.a.__class__.__name__}')

        return code

    if isinstance(code, AST):
        if not isinstance(code, ast_type):
            raise NodeTypeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(parse(code, parse_params := self.root.parse_params), lines, parse_params=parse_params)


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

@staticmethod
def _parse_stmts(src: str, parse_params: dict = {}) -> AST:
    """Parse one or more `stmt`s and return them in a `Module` `body` (just `ast.parse()` basically)."""

    return ast_parse(src, **parse_params)


@staticmethod
def _parse_expr(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.expr` or raise `SyntaxError`."""

    body = ast_parse(src, **parse_params).body

    if len(body) != 1:
        raise NodeTypeError('expecting single expression')
    elif not isinstance(ast := body[0], Expr):
        raise NodeTypeError(f'expecting expression, got {ast.__class__.__name__}')

    return ast.value


@staticmethod
def _parse_slice(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.Slice` or anything else that can go into `Subscript.slice` or raise `SyntaxError`, e.g.
    "start:stop:step" or "name" or even "a:b, c:d:e, g"."""

    return _offset_linenos(ast_parse(f'a[\n{src}]', **parse_params).body[0].value.slice, -1)


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

    return _offset_linenos(ast_parse(f'def f(\n{src}): pass', **parse_params).body[0].args.args[0], -1)


@staticmethod
def _parse_keyword(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.keyword` or raise `SyntaxError`, e.g. "var=val"."""

    return _offset_linenos(ast_parse(f'f(\n{src})', **parse_params).body[0].value.keywords[0], -1)


@staticmethod
def _parse_alias_maybe_star(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.alias` or raise `SyntaxError`, e.g. "name as alias"."""

    return _offset_linenos(ast_parse(f'from . import (\n{src})', **parse_params).body[0].names[0], -1)


@staticmethod
def _parse_alias_dotted(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.alias`, allowing dotted notation (not all aliases are created equal), or raise `SyntaxError`,
    e.g. "name as alias"."""

    return _offset_linenos(ast_parse(f'import \\\n{src}', **parse_params).body[0].names[0], -1)


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

    return _offset_linenos(ast_parse(f'match _:\n case \\\n{src}: pass', **parse_params).body[0].cases[0].pattern, -2)


@staticmethod
def _parse_type_param(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.type_param` or raise `SyntaxError`, e.g. "t: Base = Subclass"."""

    return _offset_linenos(ast_parse(f'type t[\n{src}] = None', **parse_params).body[0].type_params[0], -1)


# ......................................................................................................................

def _code_as_stmts(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to zero or more `stmt`s and return in the `body` of a `Module` `FST` if possible."""

    if isinstance(code, FST):
        codea = code.a

        if isinstance(codea, stmt):
            return FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, stmt) for a in codea.body):
                return code

            raise NodeTypeError(f'expecting zero or more stmts, got '
                                f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]')

        if isinstance(codea, Interactive):
            code._unmake_fst_parents()

            return FST(Module(body=code.body, type_ignores=[]), code._lines, from_=code, lcopy=False)

        raise NodeTypeError(f'expecting zero or more stmts, got {codea.__class__.__name__}')

    if isinstance(code, AST):
        if not isinstance(code, stmt):
            raise NodeTypeError(f'expecting zero or more stmts, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_stmts(code, parse_params := self.root.parse_params), lines, parse_params=parse_params)


def _code_as_expr(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to an expr `FST` if possible."""

    if isinstance(code, FST):
        if not isinstance(ast := reduce_ast(codea := code.a, NodeTypeError), expr):
            raise NodeTypeError(f'expecting expression, got {ast.__class__.__name__}')

        if ast is codea:
            return code

        ast.f._unmake_fst_parents()

        return FST(ast, code._lines, from_=code, lcopy=False)

    if isinstance(code, AST):
        if not isinstance(code, expr):
            raise NodeTypeError(f'expecting expression, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_expr(code, parse_params := self.root.parse_params), lines, parse_params=parse_params)


def _code_as_slice(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a Slice `FST` if possible (or anthing else that can serve in `Subscript.slice`)."""

    return _code_as(self, code, expr, _parse_slice)


def _code_as_boolop(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a `boolop` `FST` if possible."""

    return _code_as_op(self, code, boolop, OPSTR2CLS_BOOL)


def _code_as_operator(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a `operator` `FST` if possible."""

    return _code_as_op(self, code, operator, OPSTR2CLS_BIN)


def _code_as_operator_aug(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to an augmented `operator` `FST` if possible, e.g. "+="."""

    return _code_as_op(self, code, operator, OPSTR2CLS_AUG, OPCLS2STR_AUG)


def _code_as_unaryop(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a `unaryop` `FST` if possible."""

    return _code_as_op(self, code, unaryop, OPSTR2CLS_UNARY)


def _code_as_cmpop(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a `cmpop` `FST` if possible."""

    return _code_as_op(self, code, cmpop, OPSTR2CLS_CMP)


def _code_as_comprehension(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(self, code, comprehension, _parse_comprehension)


def _code_as_ExceptHandlers(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to zero or more `ExceptHandler`s and return in the `body` of a `Module` `FST` if possible."""

    if isinstance(code, FST):
        codea = code.a

        if isinstance(codea, ExceptHandler):
            return FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, ExceptHandler) for a in codea.body):
                return code

            raise NodeTypeError(f'expecting zero or more ExceptHandlers, got '
                                f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]')

        raise NodeTypeError(f'expecting zero or more ExceptHandlers, got {codea.__class__.__name__}')

    if isinstance(code, AST):
        if not isinstance(code, ExceptHandler):
            raise NodeTypeError(f'expecting zero or more ExceptHandlers, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_ExceptHandlers(code, parse_params := self.root.parse_params), lines, parse_params=parse_params)


def _code_as_arguments(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a arguments `FST` if possible."""

    return _code_as(self, code, arguments, _parse_arguments)


def _code_as_arguments_lambda(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a lambda arguments `FST` if possible (no annotations allowed)."""

    return _code_as(self, code, arguments, _parse_arguments_lambda)


def _code_as_arg(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to an arg `FST` if possible."""

    return _code_as(self, code, arg, _parse_arg)


def _code_as_keyword(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a keyword `FST` if possible."""

    return _code_as(self, code, keyword, _parse_keyword)


def _code_as_alias_maybe_star(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a alias `FST` if possible, possibly star as in `alias` for `FromImport.names`."""

    return _code_as(self, code, alias, _parse_alias_maybe_star)


def _code_as_alias_dotted(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a alias `FST` if possible, dotted as in `alias` for `Import.names`."""

    return _code_as(self, code, alias, _parse_alias_dotted)


def _code_as_withitem(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(self, code, withitem, _parse_withitem)


def _code_as_match_cases(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to zero or more `match_case`s and return in the `body` of a `Module` `FST` if possible."""

    if isinstance(code, FST):
        codea = code.a

        if isinstance(codea, match_case):
            return FST(Module(body=[codea], type_ignores=[]), code._lines, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, match_case) for a in codea.body):
                return code

            raise NodeTypeError(f'expecting zero or more match_cases, got '
                                f'[{_shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]')

        raise NodeTypeError(f'expecting zero or more match_cases, got {codea.__class__.__name__}')

    if isinstance(code, AST):
        if not isinstance(code, match_case):
            raise NodeTypeError(f'expecting zero or more match_cases, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return FST(_parse_match_cases(code, parse_params := self.root.parse_params), lines, parse_params=parse_params)


def _code_as_pattern(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a pattern `FST` if possible."""

    return _code_as(self, code, pattern, _parse_pattern)


def _code_as_type_param(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a type_param `FST` if possible."""

    return _code_as(self, code, type_param, _parse_type_param)


def _code_as_identifier(self: 'FST', code: Code) -> str:
    """Convert `Code` to valid identifier string if possible."""

    if isinstance(code, FST):
        code = code.src
    elif isinstance(code, AST):
        code = ast_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier(code):
        raise NodeTypeError(f'expecting identifier, got {_shortstr(code)!r}')

    return code


def _code_as_identifier_dotted(self: 'FST', code: Code) -> str:
    """Convert `Code` to valid dotted identifier string if possible (for Import module)."""

    if isinstance(code, FST):
        code = code.src
    elif isinstance(code, AST):
        code = ast_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_dotted(code):
        raise NodeTypeError(f'expecting dotted identifier, got {_shortstr(code)!r}')

    return code


def _code_as_identifier_maybe_star(self: 'FST', code: Code) -> str:
    """Convert `Code` to valid identifier string or star '*' if possible (for ImportFrom names)."""

    if isinstance(code, FST):
        code = code.src
    elif isinstance(code, AST):
        code = ast_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_maybe_star(code):
        raise NodeTypeError(f"expecting identifier or '*', got {_shortstr(code)!r}")

    return code


def _code_as_identifier_alias(self: 'FST', code: Code) -> str:
    """Convert `Code` to valid dotted identifier string or star '*' if possible (for any alias)."""

    if isinstance(code, FST):
        code = code.src
    elif isinstance(code, AST):
        code = ast_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    if not is_valid_identifier_alias(code):
        raise NodeTypeError(f"expecting dotted identifier or '*', got {_shortstr(code)!r}")

    return code


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]

from .fst import FST  # this imports a fake FST which is replaced in globals() on first use
