"""Misc lower level FST methods."""

from ast import *
from ast import parse as ast_parse, unparse as ast_unparse

from .astutil import *
from .astutil import type_param, TypeVar, ParamSpec, TypeVarTuple

from .shared import (
    Code, NodeTypeError,
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


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

@staticmethod
def _parse_type_param(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.type_param` or raise `SyntaxError`."""

    ast = ast_parse(f'type t[\n{src}] = None', **parse_params).body[0].type_params[0]

    for a in walk(ast):
        if end_lineno := getattr(a, 'end_lineno', None):
            a.end_lineno  = end_lineno - 1
            a.lineno     -= 1

    return ast


@staticmethod
def _parse_pattern(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.pattern` or raise `SyntaxError`."""

    ast = ast_parse(f'match _:\n case \\\n{src}: pass', **parse_params).body[0].cases[0].pattern

    for a in walk(ast):
        if end_lineno := getattr(a, 'end_lineno', None):
            a.end_lineno  = end_lineno - 2
            a.lineno     -= 2

    return ast


@staticmethod
def _parse_expr(src: str, parse_params: dict = {}) -> AST:
    """Parse to an `ast.expr` or raise `SyntaxError`."""

    body = ast_parse(src, **parse_params).body

    if len(body) != 1:
        raise NodeTypeError('expecting single expression')
    elif not isinstance(ast := body[0], Expr):
        raise NodeTypeError(f'expecting expression, got {ast.__class__.__name__}')

    return ast.value


def _code_as_identifier(self: 'FST', code: Code) -> str:
    """Convert `Code` to valid identifier string if possible."""

    if isinstance(code, list):
        if len(code) != 1:
            raise NodeTypeError(f'expecting onle line identifier, got {len(code)} lines')

        code = code[0]

    if isinstance(code, str):
        if not is_valid_identifier(code):
            raise NodeTypeError(f'expecting identifier, got {code!r}')

    else:
        if isinstance(code, FST):
            code = code.a

        if not isinstance(code, Name):
            raise NodeTypeError(f'expecting identifier (Name), got {code.__class__.__name__}')

        return code.id

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


def _code_as_type_param(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a type_param (TypeVar, ParamSpec, TypeVarTuple) `FST` if possible."""

    if isinstance(code, FST):
        if not isinstance(code.a, (TypeVar, ParamSpec, TypeVarTuple)):
            raise NodeTypeError(f'expecting type_param, got {code.a.__class__.__name__}')

        return code

    if isinstance(code, AST):
        if not isinstance(code, type_param):
            raise NodeTypeError(f'expecting type_param, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    ast = _parse_type_param(code, self.root.parse_params)

    return FST(ast, lines=lines)


def _code_as_pattern(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to a pattern `FST` if possible."""

    if isinstance(code, FST):
        if not isinstance(code.a, pattern):
            raise NodeTypeError(f'expecting pattern, got {code.a.__class__.__name__}')

        return code

    if isinstance(code, AST):
        if not isinstance(code, pattern):
            raise NodeTypeError(f'expecting pattern, got {code.__class__.__name__}')

        code  = ast_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    ast = _parse_pattern(code, self.root.parse_params)

    return FST(ast, lines=lines)


def _code_as_expr(self: 'FST', code: Code) -> 'FST':
    """Convert `code` to an expr `FST` if possible."""

    if isinstance(code, FST):
        if not isinstance(ast := reduce_ast(codea := code.a, NodeTypeError), expr):
            raise NodeTypeError(f'expecting expression, got {ast.__class__.__name__}')

        return code if ast is codea else FST(ast, lines=code._lines, from_=code)

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


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]

from .fst import FST
