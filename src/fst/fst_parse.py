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

    return FST(parse(code, self.root.parse_params), lines=lines)


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

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
    "start:stop:step"."""

    return _offset_linenos(ast_parse(f'a[\n{src}]', **parse_params).body[0].value.slice, -1)


@staticmethod
def _parse_comprehension(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.comprehension` or raise `SyntaxError`, e.g. "async for i in something() if i"."""

    return _offset_linenos(ast_parse(f'[_ \n{src}]', **parse_params).body[0].value.generators[0], -1)


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
def _parse_alias(src: str, parse_params: dict = {}) -> AST:
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
def _parse_pattern(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.pattern` or raise `SyntaxError`, e.g. "{a.b: i, **rest}"."""

    return _offset_linenos(ast_parse(f'match _:\n case \\\n{src}: pass', **parse_params).body[0].cases[0].pattern, -2)


@staticmethod
def _parse_type_param(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.type_param` or raise `SyntaxError`, e.g. "t: Base = Subclass"."""

    return _offset_linenos(ast_parse(f'type t[\n{src}] = None', **parse_params).body[0].type_params[0], -1)


# ......................................................................................................................

def _code_as_expr(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to an expr `FST` if possible."""

    if isinstance(code, FST):
        if not isinstance(ast := reduce_ast(codea := code.a, NodeTypeError), expr):
            raise NodeTypeError(f'expecting expression, got {ast.__class__.__name__}')

        if ast is codea:
            return code

        ast.f._unmake_fst_parents()

        return FST(ast, lines=code._lines, from_=code)

    if isinstance(code, AST):
        if not isinstance(code, expr):
            raise NodeTypeError(f'expecting expression, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    ast = _parse_expr(code, self.root.parse_params)

    return FST(ast, lines=lines)


def _code_as_slice(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a Slice `FST` if possible (or anthing else that can serve in `Subscript.slice`)."""

    return _code_as(self, code, expr, _parse_slice)


def _code_as_comprehension(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(self, code, comprehension, _parse_comprehension)


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


def _code_as_alias(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a alias `FST` if possible."""

    return _code_as(self, code, alias, _parse_alias)


def _code_as_alias_dotted(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a alias `FST` if possible."""

    return _code_as(self, code, alias, _parse_alias_dotted)


def _code_as_withitem(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(self, code, withitem, _parse_withitem)


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

    if not is_valid_identifier_dotted(code):
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


def _code_as_op(self: 'FST', code: Code,
                target: type[AugAssign] | type[BoolOp] | type[BinOp] | type[UnaryOp] | type[Compare] | None = None,
                ) -> 'FST':
    """Convert `code` to an operator `FST` for the given target if possible."""

    if isinstance(code, FST):
        if (src := code.get_src(*code.loc)) not in _code_as_op_str2op[target]:
            raise NodeTypeError(f'bad operator {src!r}')

    elif isinstance(code, AST):
        code = FST(code, lines=[(OPCLS2STR_AUG if target is AugAssign else OPCLS2STR).get(code.__class__, '')])

    else:
        if isinstance(code, list):
            code = '\n'.join(lines := code)
        else:
            lines = code.split('\n')

        if not (cls := _code_as_op_str2op[target].get(code)):
            raise NodeTypeError(f'bad operator {code!r}')

        code = FST(cls(), lines=lines)

    if code.a.__class__ not in _code_as_op_ops[target]:
        raise NodeTypeError(f'expecting operator{f" for {target.__name__}" if target else ""}'
                            f', got {code.a.__class__.__name__}')

    return code


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]

from .fst import FST
