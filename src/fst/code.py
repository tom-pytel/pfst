"""Convert `Code` to `FST`.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Union
from unicodedata import normalize

from . import fst

from .asttypes import (
    AST,
    Assign,
    Constant,
    ExceptHandler,
    Expr,
    Expression,
    Interactive,
    IsNot,
    MatchOr,
    Module,
    Name,
    NotIn,
    Pass,
    Tuple,
    alias,
    arg,
    arguments,
    boolop,
    cmpop,
    comprehension,
    expr,
    keyword,
    match_case,
    operator,
    pattern,
    stmt,
    unaryop,
    withitem,
    TryStar,
    type_param,
)

from .astutil import (
    constant, bistr,
    OPSTR2CLS_UNARY, OPSTR2CLS_BIN, OPSTR2CLS_CMP, OPSTR2CLS_BOOL, OPSTR2CLS_AUG, OPCLS2STR_AUG, OPCLS2STR,
    is_valid_identifier, is_valid_identifier_dotted, is_valid_identifier_star, is_valid_identifier_alias,
    reduce_ast,
)

from .misc import (
    NodeError, shortstr
)

from .extparse import (
    ParseError,
    _fixing_unparse,
    unparse,
    parse,
    parse_stmts,
    parse_ExceptHandlers,
    parse_match_cases,
    parse_expr,
    parse_expr_all,
    parse_expr_arglike,
    parse_expr_slice,
    parse_expr_sliceelt,
    parse_Tuple,
    parse_boolop,
    parse_binop,
    parse_augop,
    parse_unaryop,
    parse_cmpop,
    parse_comprehension,
    parse_arguments,
    parse_arguments_lambda,
    parse_arg,
    parse_keyword,
    parse_alias,
    parse_alias_dotted,
    parse_alias_star,
    parse_withitem,
    parse_pattern,
    parse_type_param,
    parse_type_params,
    parse_Assign_targets,
)

__all__ = [
    'Code',
    'code_as_all',
    'code_as_stmts',
    'code_as_ExceptHandlers',
    'code_as_match_cases',
    'code_as_expr',
    'code_as_expr_all',
    'code_as_expr_arglike',
    'code_as_expr_slice',
    'code_as_expr_sliceelt',
    'code_as_Tuple',
    'code_as_boolop',
    'code_as_binop',
    'code_as_augop',
    'code_as_unaryop',
    'code_as_cmpop',
    'code_as_comprehension',
    'code_as_arguments',
    'code_as_arguments_lambda',
    'code_as_arg',
    'code_as_keyword',
    'code_as_alias',
    'code_as_alias_dotted',
    'code_as_alias_star',
    'code_as_withitem',
    'code_as_pattern',
    'code_as_type_param',
    'code_as_type_params',
    'code_as_Assign_targets',
    'code_as_identifier',
    'code_as_identifier_dotted',
    'code_as_identifier_star',
    'code_as_identifier_alias',
    'code_as_constant',
]


Code = Union['fst.FST', AST, list[str], str]  ; """Code types accepted for put to `FST`."""


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
                if parse_cmpop(src).__class__ is codea:  # parses to same thing so just return the canonical str for the op, otherwise it gets complicated
                    return fst.FST(codea, [bistr(expected)], from_=code, lcopy=False)

            raise NodeError(f'expecting {expected!r}, got {shortstr(src)!r}', rawable=True)

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
    except SyntaxError:
        raise ParseError(f'expecting {ast_type.__name__}, got {shortstr(code)!r}') from None


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

        src   = unparse(code)
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

def code_as_all(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to any parsable `FST` if possible. If `FST` passed then it is returned as itself."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        return code

    if isinstance(code, AST):
        mode  = code.__class__  # we do not accept invalid-AST SPECIAL SLICE ASTs on purpose, could accept them by setting `mode = _get_special_parse_mode(code) or code.__class__` but that gets complicated fast
        code  = unparse(code)
        lines = code.split('\n')

    else:
        mode = 'all'

        if isinstance(code, list):
            code = '\n'.join(lines := code)
        else:  # str
            lines = code.split('\n')

    return fst.FST(parse(code, mode), lines, parse_params=parse_params)


def code_as_stmts(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
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
                            f'[{shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]', rawable=True)

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

    return fst.FST(parse_stmts(code, parse_params), lines, parse_params=parse_params)


def code_as_ExceptHandlers(code: Code, parse_params: Mapping[str, Any] = {}, *, is_trystar: bool = False) -> fst.FST:
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
                             f'[{shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]', rawable=True)

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

    return fst.FST(parse_ExceptHandlers(code, parse_params), lines, parse_params=parse_params)


def code_as_match_cases(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
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
                             f'[{shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]', rawable=True)

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

    return fst.FST(parse_match_cases(code, parse_params), lines, parse_params=parse_params)


def code_as_expr(code: Code, parse_params: Mapping[str, Any] = {}, *,
                  parse: Callable[[Code, dict], fst.FST] = parse_expr, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `expr` or optionally `Slice` `FST` if possible."""

    def expecting() -> str:
        return ('expecting Tuple' if parse is parse_Tuple else
                'expecting expression (slice element)' if parse is parse_expr_sliceelt else
                'expecting expression (slice)' if parse is parse_expr_slice else
                'expecting expression (arglike)' if parse is parse_expr_arglike else
                'expecting expression (any)' if parse is parse_expr_all else
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

        src   = unparse(code)
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


def code_as_expr_all(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `expr` using `parse_expr_all()`."""

    return code_as_expr(code, parse_params, parse=parse_expr_all, sanitize=sanitize)


def code_as_expr_arglike(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `expr` in the context of a `Call.args` which has special parse rules for `Starred`."""

    return code_as_expr(code, parse_params, parse=parse_expr_arglike, sanitize=sanitize)


def code_as_expr_slice(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a Slice `FST` if possible (or anthing else that can serve in `Subscript.slice`, like any old
    generic `expr`)."""

    return code_as_expr(code, parse_params, parse=parse_expr_slice, sanitize=sanitize)


def code_as_expr_sliceelt(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `expr` or `Slice` `FST` if possible. This exists because of the behavior of naked `Starred`
    expressions in a `Subscript` `slice` field."""

    return code_as_expr(code, parse_params, parse=parse_expr_sliceelt, sanitize=sanitize)


def code_as_Tuple(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a `Tuple` using `parse_Tuple()`."""

    fst_ = code_as_expr(code, parse_params, parse=parse_Tuple, sanitize=sanitize)

    if fst_ is code and not isinstance(fst_.a, Tuple):  # fst_ is code only if FST passed in, in which case is passed through and we need to check that was Tuple to begin with
        raise NodeError(f'expecting Tuple, got {fst_.a.__class__.__name__}', rawable=True)

    return fst_


def code_as_boolop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to a `boolop` `FST` if possible."""

    return _code_as_op(code, boolop, parse_params, parse_boolop, OPSTR2CLS_BOOL)


def code_as_binop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to a `operator` `FST` if possible."""

    return _code_as_op(code, operator, parse_params, parse_binop, OPSTR2CLS_BIN)


def code_as_augop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to an augmented `operator` `FST` if possible, e.g. "+="."""

    return _code_as_op(code, operator, parse_params, parse_augop, OPSTR2CLS_AUG, OPCLS2STR_AUG)


def code_as_unaryop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to a `unaryop` `FST` if possible."""

    return _code_as_op(code, unaryop, parse_params, parse_unaryop, OPSTR2CLS_UNARY)


def code_as_cmpop(code: Code, parse_params: Mapping[str, Any] = {}) -> fst.FST:
    """Convert `code` to a `cmpop` `FST` if possible."""

    return _code_as_op(code, cmpop, parse_params, parse_cmpop, OPSTR2CLS_CMP)


def code_as_comprehension(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(code, comprehension, parse_params, parse_comprehension, sanitize=sanitize)


def code_as_arguments(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a arguments `FST` if possible."""

    # TODO: upcast FST and AST arg to arguments?

    return _code_as(code, arguments, parse_params, parse_arguments, sanitize=sanitize)


def code_as_arguments_lambda(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a lambda arguments `FST` if possible (no annotations allowed)."""

    # TODO: upcast FST and AST arg to arguments?

    return _code_as(code, arguments, parse_params, parse_arguments_lambda, sanitize=sanitize)


def code_as_arg(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an arg `FST` if possible."""

    return _code_as(code, arg, parse_params, parse_arg, sanitize=sanitize)


def code_as_keyword(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a keyword `FST` if possible."""

    return _code_as(code, keyword, parse_params, parse_keyword, sanitize=sanitize)


def code_as_alias(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a alias `FST` if possible, star or dotted."""

    return _code_as(code, alias, parse_params, parse_alias, sanitize=sanitize)


def code_as_alias_dotted(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a alias `FST` if possible, dotted as in `alias` for `Import.names`."""

    fst_ = _code_as(code, alias, parse_params, parse_alias_dotted, sanitize=sanitize)

    if '*' in fst_.a.name:
        raise ParseError("'*' not allowed in this alias")

    return fst_


def code_as_alias_star(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a alias `FST` if possible, possibly star as in `alias` for `FromImport.names`."""

    fst_ = _code_as(code, alias, parse_params, parse_alias_star, sanitize=sanitize)

    if '.' in fst_.a.name:
        raise ParseError("'.' not allowed in this alias")

    return fst_


def code_as_withitem(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(code, withitem, parse_params, parse_withitem, sanitize=sanitize)


def code_as_pattern(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True,
                     allow_invalid_matchor: bool = False) -> fst.FST:
    """Convert `code` to a pattern `FST` if possible."""

    fst_ = _code_as(code, pattern, parse_params, parse_pattern, sanitize=sanitize)

    if not allow_invalid_matchor and isinstance(a := fst_.a, MatchOr):  # SPECIAL SLICE, don't need to check if 'fst_ is code' because this could only have come from 'code' as FST
        if not (len_pattern := len(a.patterns)):
            raise NodeError('expecting valid pattern, got zero-length MatchOr')

        if len_pattern == 1:  # a length 1 MatchOr can just return its single element pattern
            return fst.FST(a.patterns[0], fst_._lines, from_=fst_, lcopy=False)

    return fst_


def code_as_type_param(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a type_param `FST` if possible."""

    return _code_as(code, type_param, parse_params, parse_type_param, sanitize=sanitize)


def code_as_type_params(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to a type_params slice `FST` if possible."""

    fst_ = _code_as(code, Tuple, parse_params, parse_type_params, sanitize=sanitize)

    if fst_ is code:  # this means it was not parsed (came in as FST) and we need to verify it containes only type_params
        if not all(isinstance(elt := e, type_param) for e in fst_.a.elts):
            raise NodeError(f'expecting only type_params, got {elt.__class__.__name__}', rawable=True)

    return fst_


def code_as_Assign_targets(code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = True) -> fst.FST:
    """Convert `code` to an `Assign` targets slice `FST` if possible."""

    fst_ = _code_as(code, Assign, parse_params, parse_Assign_targets, sanitize=sanitize)

    if not isinstance(name := fst_.a.value, Name) or name.id:  # SPECIAL SLICE
        raise NodeError('expecting Assign targets slice, got normal Assign', rawable=True)

    return fst_


def code_as_identifier(code: Code, parse_params: Mapping[str, Any] = {}) -> str:
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
        raise ParseError(f'expecting identifier, got {shortstr(code)!r}')

    return normalize('NFKC', code)


def code_as_identifier_dotted(code: Code, parse_params: Mapping[str, Any] = {}) -> str:
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
        raise ParseError(f'expecting dotted identifier, got {shortstr(code)!r}')

    return normalize('NFKC', code)


def code_as_identifier_star(code: Code, parse_params: Mapping[str, Any] = {}) -> str:
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
        raise ParseError(f"expecting identifier or '*', got {shortstr(code)!r}")

    return normalize('NFKC', code)


def code_as_identifier_alias(code: Code, parse_params: Mapping[str, Any] = {}) -> str:
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
        raise ParseError(f"expecting dotted identifier or '*', got {shortstr(code)!r}")

    return normalize('NFKC', code)


def code_as_constant(code: constant, parse_params: Mapping[str, Any] = {}) -> constant:
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
