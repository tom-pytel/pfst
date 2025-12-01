"""Convert `Code` to `FST`."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Union
from unicodedata import normalize

from . import fst

from .asttypes import (
    AST,
    Attribute,
    Constant,
    ExceptHandler,
    Expr,
    Expression,
    Interactive,
    Load,
    MatchOr,
    Module,
    Name,
    Pass,
    Slice,
    Store,
    Try,
    TryStar,
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
    type_param,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from .astutil import (
    constant,
    OPCLS2STR,
    is_valid_identifier,
    is_valid_identifier_dotted,
    is_valid_identifier_star,
    is_valid_identifier_alias,
    is_valid_target,
    reduce_ast,
    set_ctx,
)

from .common import NodeError, shortstr

from .parsex import (
    _fixing_unparse,
    ParseError,
    unparse,
    parse,
    parse_stmts,
    parse__ExceptHandlers,
    parse__match_cases,
    parse_expr,
    parse_expr_all,
    parse_expr_arglike,
    parse_expr_slice,
    parse_Tuple_elt,
    parse_Tuple,
    parse__Assign_targets,
    parse__decorator_list,
    parse_boolop,
    parse_operator,
    parse_unaryop,
    parse_cmpop,
    parse_comprehension,
    parse__comprehensions,
    parse__comprehension_ifs,
    parse_arguments,
    parse_arguments_lambda,
    parse_arg,
    parse_keyword,
    parse_alias,
    parse__aliases,
    parse_Import_name,
    parse__Import_names,
    parse_ImportFrom_name,
    parse__ImportFrom_names,
    parse_withitem,
    parse__withitems,
    parse_pattern,
    parse_type_param,
    parse__type_params,
    parse__expr_arglikes,
)

__all__ = [
    'Code',
    'code_as_lines',
    'code_as_all',
    'code_as_stmts',
    'code_as__ExceptHandlers',
    'code_as__match_cases',
    'code_as_expr',
    'code_as_expr_all',
    'code_as_expr_arglike',
    'code_as_expr_slice',
    'code_as_Tuple_elt',
    'code_as_Tuple',
    'code_as__Assign_targets',
    'code_as__decorator_list',
    'code_as_boolop',
    'code_as_operator',
    'code_as_unaryop',
    'code_as_cmpop',
    'code_as_comprehension',
    'code_as__comprehensions',
    'code_as__comprehension_ifs',
    'code_as_arguments',
    'code_as_arguments_lambda',
    'code_as_arg',
    'code_as_keyword',
    'code_as_alias',
    'code_as__aliases',
    'code_as_Import_name',
    'code_as__Import_names',
    'code_as_ImportFrom_name',
    'code_as__ImportFrom_names',
    'code_as_withitem',
    'code_as__withitems',
    'code_as_pattern',
    'code_as_type_param',
    'code_as__type_params',
    'code_as_identifier',
    'code_as_identifier_dotted',
    'code_as_identifier_star',
    'code_as_identifier_alias',
    'code_as_constant',
    'code_as__expr_arglikes',
]


Code = Union['fst.FST', AST, list[str], str]  ; """Code types accepted for put to `FST`."""
CodeAs = Callable[[Code, Mapping[str, Any]], 'fst.FST']  # + kwargs: *, sanitize: bool = False, coerce: bool = False


def _expecting(parse: Callable[[Code, Mapping[str, Any]], AST]) -> str:
    return ('expecting Tuple' if parse is parse_Tuple else
            'expecting expression (tuple element)' if parse is parse_Tuple_elt else
            'expecting expression (slice)' if parse is parse_expr_slice else
            'expecting expression (arglike)' if parse is parse_expr_arglike else
            'expecting expression (all types)' if parse is parse_expr_all else
            'expecting expression (standard)')


def _coerce_as__expr_arglikes(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_expr_arglike(code, parse_params, sanitize=sanitize)
    ast_ = fst_.a

    if fst_._is_parenthesized_tuple() is False:  # can't have unparenthesized tuple as sole element, will look like multiple elements
        fst_._delimit_node()

    ast_ = Tuple(elts=[ast_], ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                 end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _coerce_as__Assign_targets(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_expr(code, parse_params, sanitize=sanitize)
    ast_ = fst_.a

    if not is_valid_target(ast_):
        raise NodeError(f'expecting Assign target, got {fst_.a.__class__.__name__}')

    set_ctx(ast_, Store)

    ast_ = _Assign_targets(targets=[ast_], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                           end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _coerce_as__decorator_list(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_expr(code, parse_params, sanitize=sanitize)
    ln = fst_.pars().ln

    fst_._put_src('@', ln, 0, ln, 0, False)  # prepend '@' to expression on line of expression at start to make it a _decorator_list slice

    ast_ = _decorator_list(decorator_list=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                           end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _coerce_as__comprehensions(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_comprehension(code, parse_params, sanitize=sanitize)
    ast_ = _comprehensions(generators=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                           end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _coerce_as__comprehension_ifs(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_expr(code, parse_params, sanitize=sanitize)
    ln, col, _, _ = fst_.pars()

    fst_._put_src('if ', ln, col, ln, col, False)  # prepend 'if' to expression to make it a _comprehension_ifs slice, we do it before the container because the container will have to start at 0, 0

    ast_ = _comprehension_ifs(ifs=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                              end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _coerce_as_alias(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_expr(code, parse_params, sanitize=True)  # sanitize because where aliases are used then generally can't have junk, comments specifically would break Import.names aliases
    ast_ = fst_.a
    name = ''

    while isinstance(ast_, Attribute):
        name = f'.{ast_.attr}{name}'  # we build it up like this because there can be whitespace, line continuations and newlines in the source
        ast_ = ast_.value

        if ast_.f.pars().n:  # aliases can't have pars
            ast_.f._unparenthesize_grouping(False)

    if not isinstance(ast_, Name):
        raise NodeError(f'cannot coerce {ast_.__class__.__name__} to alias, must be Name or Attribute')

    if fst_.pars().n:  # aliases can't have pars
        fst_._unparenthesize_grouping(False)

    name = ast_.id + name
    ast_ = fst_.a
    ast_ = alias(name=name, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                 end_col_offset=ast_.end_col_offset)

    return fst.FST(ast_, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_as__aliases(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_alias(code, parse_params, sanitize=sanitize, coerce=True)  # coerce=True to coerce Name or Attribute to alias if necessary
    ast_ = _aliases(names=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                    end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


_coerce_as__Import_name = _coerce_as_alias


def _coerce_as__Import_names(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_Import_name(code, parse_params, sanitize=sanitize, coerce=True)  # coerce=True to coerce Name or Attribute to alias if necessary
    ast_ = _aliases(names=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                    end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _coerce_as__ImportFrom_name(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_expr(code, parse_params, sanitize=True)  # sanitize because where aliases are used then generally can't have junk, comments specifically would break Import.names aliases
    ast_ = fst_.a

    if not isinstance(ast_, Name):
        raise NodeError(f'cannot coerce {ast_.__class__.__name__} to ImportFrom.names alias, must be Name')

    if fst_.pars().n:  # aliases can't have pars
        fst_._unparenthesize_grouping(False)

    ast_ = alias(name=ast_.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                 end_col_offset=ast_.end_col_offset)

    return fst.FST(ast_, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_as__ImportFrom_names(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_ImportFrom_name(code, parse_params, sanitize=sanitize, coerce=True)  # coerce=True to coerce Name to alias if necessary
    ast_ = _aliases(names=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                    end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _coerce_as_withitem(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_expr(code, parse_params, sanitize=sanitize)
    ast_ = withitem(context_expr=fst_.a)

    return fst.FST(ast_, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_as__withitems(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_withitem(code, parse_params, sanitize=sanitize, coerce=True)  # coerce=True to coerce expr to withitem if necessary
    ast_ = _withitems(items=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                      end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _coerce_as__type_params(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    fst_ = code_as_type_param(code, parse_params, sanitize=sanitize)
    ast_ = _type_params(type_params=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                        end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _code_as(
    code: Code,
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    ast_type: type[AST],
    sanitize: bool,
    coerce_as: CodeAs | None = None,
) -> fst.FST:
    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(code.a, ast_type):
            if coerce_as:
                try:
                    return coerce_as(code, parse_params, sanitize=sanitize)
                except Exception:
                    pass

            raise NodeError(f'expecting {ast_type.__name__}, got {code.a.__class__.__name__}'
                            f'{", could not coerce" if coerce_as else ""}', rawable=True)

    else:
        if isinstance(code, AST):
            if not isinstance(code, ast_type):
                if coerce_as:
                    try:
                        return coerce_as(code, parse_params, sanitize=sanitize)
                    except Exception:
                        pass

                raise NodeError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}'
                                f'{", could not coerce" if coerce_as else ""}', rawable=True)

            src = unparse(code)
            lines = src.split('\n')

            ast = parse(src, parse_params)

            if ast.__class__ is not code.__class__:
                raise ParseError(f'could not reparse AST to {code.__class__.__name__}, got {ast.__class__.__name__}')

        else:
            if isinstance(code, list):
                src = '\n'.join(lines := code)
            else:  # str
                lines = (src := code).split('\n')

            try:
                ast = parse(src, parse_params)

            except Exception:
                if not coerce_as:
                    raise

                try:
                    fst_ = coerce_as(code, parse_params, sanitize=sanitize)
                except Exception:
                    raise ParseError(f'expecting {ast_type.__name__}, could not parse or coerce') from None

                return fst_

            if not isinstance(ast, ast_type):  # sanity check, parse func should guarantee what we want but maybe in future is used to get a specific subset of what parse func returns
                raise ParseError(f'expecting {ast_type.__name__}, got {code.__class__.__name__}')

        code = fst.FST(ast, lines, None, parse_params=parse_params)

    return code._sanitize() if sanitize else code


def _code_as_expr(
    code: Code,
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    allow_Slice: bool,
    allow_Tuple_of_Slice: bool,
    sanitize: bool,
) -> fst.FST:
    """General convert `code` to `expr`. Meant to handle any type of expression including `Slice`, `Tuple` of `Slice`s,
    `Tuple` of `Slice` elements and arglikes."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a
        ast = reduce_ast(codea)

        if not ast:
            raise NodeError(f'{_expecting(parse)}, got multiple statements', rawable=True)

        if not isinstance(ast, expr):
            raise NodeError(f'{_expecting(parse)}, got {ast.__class__.__name__}', rawable=True)

        if ast is not codea:
            ast.f._unmake_fst_parents()

            code = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

        if isinstance(ast, Slice):
            if not allow_Slice:
                raise NodeError(f'{_expecting(parse)}, got Slice', rawable=True)

        elif isinstance(ast, Tuple):
            if not allow_Tuple_of_Slice and any(isinstance(e, Slice) for e in ast.elts):
                raise NodeError(f'{_expecting(parse)}, got Tuple with a Slice in it', rawable=True)

            if parse is not parse_expr_slice:  # specifically for lone '*starred' as a `Tuple` without comma from `Subscript.slice`, even though those can't be gotten alone organically, maybe we shouldn't even bother?
                code._maybe_add_singleton_tuple_comma()

    else:
        if is_ast := isinstance(code, AST):
            if not isinstance(code, expr):
                raise NodeError(f'{_expecting(parse)}, got {code.__class__.__name__}', rawable=True)

            src = unparse(code)
            lines = src.split('\n')

        elif isinstance(code, list):
            src = '\n'.join(lines := code)
        else:  # str
            lines = (src := code).split('\n')

        ast = parse(src, parse_params)

        if is_ast and ast.__class__ is not code.__class__:
            raise ParseError(f'could not reparse AST to {code.__class__.__name__}, got {ast.__class__.__name__}')

        code = fst.FST(ast, lines, None, parse_params=parse_params)

    return code._sanitize() if sanitize else code


def _code_as_op(
    code: Code,
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    op_type: type[boolop | operator | unaryop | cmpop],  # only one of these, not subclasses
    sanitize: bool,
) -> fst.FST:
    """Convert `code` to an op `FST` if possible."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        if not isinstance(code.a, op_type):
            raise NodeError(f'expecting {op_type.__name__}, got {code.a.__class__.__name__}', rawable=True)

    elif isinstance(code, AST):
        if not isinstance(code, op_type):
            raise NodeError(f'expecting {op_type.__name__}, got {code.__class__.__name__}', rawable=True)

        return fst.FST(code.__class__(), [OPCLS2STR[code.__class__]], None, parse_params=parse_params)  # don't use same AST as was passed in

    else:
        if isinstance(code, list):
            src = '\n'.join(lines := code)
        else:  # str
            lines = (src := code).split('\n')

        code = fst.FST(parse(src, parse_params), lines, None, parse_params=parse_params)

    return code._sanitize() if sanitize else code


# ----------------------------------------------------------------------------------------------------------------------

def code_as_lines(code: Code | None) -> list[str]:
    """Get list of lines of `code` if is `FST`, unparse `AST`, split `str` or just return `list[str]` if is that.
    `code=None` is returned as `['']`."""

    if isinstance(code, str):
        return code.split('\n')
    elif code is None:
        return ['']
    elif isinstance(code, list):
        return code
    elif isinstance(code, AST):
        return unparse(code).split('\n')
    elif not code.is_root:  # isinstance(code, fst.FST)
        raise ValueError('expecting root node')
    else:
        return code._lines


def code_as_all(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to any parsable `FST` if possible. If `FST` passed then it is returned as itself."""

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

    else:
        if isinstance(code, AST):
            mode = code.__class__
            code = unparse(code)
            lines = code.split('\n')

        else:
            mode = 'all'

            if isinstance(code, list):
                code = '\n'.join(lines := code)
            else:  # str
                lines = code.split('\n')

        code = fst.FST(parse(code, mode), lines, None, parse_params=parse_params)

    return code._sanitize() if sanitize else code


def code_as_stmts(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to zero or more `stmt`s and return in the `body` of a `Module` `FST` if possible.

    **Note:** `sanitize` does nothing since the return is a `Module` which always includes the whole source.
    """

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
            return fst.FST(Module(body=[codea], type_ignores=[]), code._lines, None, from_=code, lcopy=False)

        if isinstance(codea, Module):
            if all(isinstance(a, stmt) for a in codea.body):
                return code

            raise NodeError(f'expecting zero or more stmts, got '
                            f'[{shortstr(", ".join(a.__class__.__name__ for a in codea.body))}]', rawable=True)

        if isinstance(codea, Interactive):
            code._unmake_fst_parents()

            return fst.FST(Module(body=code.body, type_ignores=[]), code._lines, None, from_=code, lcopy=False)

        raise NodeError(f'expecting zero or more stmts, got {codea.__class__.__name__}', rawable=True)

    if isinstance(code, AST):
        if not isinstance(code, (stmt, expr, Module, Interactive, Expression)):  # all these can be coerced into stmts
            raise NodeError(f'expecting zero or more stmts, got {code.__class__.__name__}', rawable=True)

        code = _fixing_unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return fst.FST(parse_stmts(code, parse_params), lines, None, parse_params=parse_params)


def code_as__ExceptHandlers(
    code: Code,
    parse_params: Mapping[str, Any] = {},
    *,
    sanitize: bool = False,
    coerce: bool = False,
    is_trystar: bool | None = None,
) -> fst.FST:
    """Convert `code` to zero or more `ExceptHandler`s and return in an `_ExceptHandlers` SPECIAL SLICE if possible.

    **Note:** `sanitize` does nothing since the return is an `_ExceptHandlers` which always includes the whole source.

    **Parameters:**
    - `is_trystar`: What kind of except handler to accept:
        - `False`: Plain only, no `except*`.
        - `True`: Star only, no plain.
        - `None`: Accept either as `FST` or source, if `AST` passed then default to plain.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if isinstance(codea, ExceptHandler):
            code = fst.FST(_ExceptHandlers(handlers=[codea], lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                           end_col_offset=ls[-1].lenbytes), ls, None, from_=code, lcopy=False)

        elif not isinstance(codea, _ExceptHandlers):
            raise NodeError(f'expecting zero or more ExceptHandlers, got {codea.__class__.__name__}')#, rawable=True)

        error = NodeError

    else:
        error = ParseError

        if isinstance(code, AST):
            if isinstance(code, ExceptHandler):
                handlers = [code]
            elif isinstance(code, _ExceptHandlers):
                handlers = code.handlers
            else:
                raise NodeError(f'expecting zero or more ExceptHandlers, got {code.__class__.__name__}')#, rawable=True)

            code = _fixing_unparse((TryStar if is_trystar else Try)(body=[Pass()],
                                                                    handlers=handlers, orelse=[], finalbody=[]))
            code = code[code.index('except'):]
            lines = code.split('\n')
            is_trystar = None  # so that unnecessary check is not done below

        elif isinstance(code, list):
            code = '\n'.join(lines := code)
        else:  # str
            lines = code.split('\n')

        code = fst.FST(parse__ExceptHandlers(code, parse_params), lines, None, parse_params=parse_params)

    if (handlers := code.a.handlers) and is_trystar is not None:
        if is_trystar != handlers[0].f._is_except_star():
            raise error("expecting star 'except*' handler, got plain 'except'" if is_trystar else
                        "expecting plain 'except' handler, got star 'except*'")

    return code


def code_as__match_cases(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to zero or more `match_case`s and return in a `_match_cases` SPECIAL SLICE if possible.

    **Note:** `sanitize` does nothing since the return is a `_match_cases` which always includes the whole source.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        codea = code.a

        if isinstance(codea, match_case):
            return fst.FST(_match_cases(cases=[codea], lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                        end_col_offset=ls[-1].lenbytes), ls, None, from_=code, lcopy=False)

        if not isinstance(codea, _match_cases):
            raise NodeError(f'expecting zero or more match_cases, got {codea.__class__.__name__}', rawable=True)

        return code

    if isinstance(code, AST):
        if not isinstance(code, (match_case, _match_cases)):
            raise NodeError(f'expecting zero or more match_cases, got {code.__class__.__name__}', rawable=True)

        code = unparse(code)
        lines = code.split('\n')

    elif isinstance(code, list):
        code = '\n'.join(lines := code)
    else:  # str
        lines = code.split('\n')

    return fst.FST(parse__match_cases(code, parse_params), lines, None, parse_params=parse_params)


def code_as_expr(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `expr` using `parse_expr()`."""

    return _code_as_expr(code, parse_params, parse_expr, False, False, sanitize)


def code_as_expr_all(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `expr` using `parse_expr_all()`."""

    return _code_as_expr(code, parse_params, parse_expr_all, True, True, sanitize)


def code_as_expr_arglike(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `expr` in the context of a `Call.args` which has special parse rules for `Starred`."""

    return _code_as_expr(code, parse_params, parse_expr_arglike, False, False, sanitize)


def code_as_expr_slice(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a any `expr` `FST` that can go into a `Subscript.slice` if possible."""

    return _code_as_expr(code, parse_params, parse_expr_slice, True, True, sanitize)


def code_as_Tuple_elt(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `expr` which can be an element of a `Tuple` anywhere, including `Slice` and arglike
    expressions like `*not a` on py 3.11+ (both in a `Tuple` in `Subscript.slice`)."""

    return _code_as_expr(code, parse_params, parse_Tuple_elt, True, False, sanitize)


def code_as_Tuple(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `Tuple` using `parse_Tuple()`. The `Tuple` can contain any other kind of expression,
    including `Slice` and arglike (if py version supports it in `Subscript.slice`)."""

    fst_ = _code_as_expr(code, parse_params, parse_Tuple, False, True, sanitize)

    if fst_ is code and not isinstance(fst_.a, Tuple):  # fst_ is code only if FST passed in, in which case is passed through and we need to check that was Tuple to begin with
        raise NodeError(f'expecting Tuple, got {fst_.a.__class__.__name__}', rawable=True)

    return fst_


def code_as__Assign_targets(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_Assign_targets` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__Assign_targets, _Assign_targets, sanitize,
                    _coerce_as__Assign_targets if coerce else None)


def code_as__decorator_list(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_decorator_list` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__decorator_list, _decorator_list, sanitize,
                    _coerce_as__decorator_list if coerce else None)


def code_as_boolop(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `boolop` `FST` if possible."""

    return _code_as_op(code, parse_params, parse_boolop, boolop, sanitize)


def code_as_operator(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `operator` `FST` if possible."""

    return _code_as_op(code, parse_params, parse_operator, operator, sanitize)


def code_as_unaryop(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `unaryop` `FST` if possible."""

    return _code_as_op(code, parse_params, parse_unaryop, unaryop, sanitize)


def code_as_cmpop(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `cmpop` `FST` if possible."""

    return _code_as_op(code, parse_params, parse_cmpop, cmpop, sanitize)


def code_as_comprehension(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(code, parse_params, parse_comprehension, comprehension, sanitize)


def code_as__comprehensions(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `_comprehensions` of `comprehensions` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__comprehensions, _comprehensions, sanitize,
                    _coerce_as__comprehensions if coerce else None)


def code_as__comprehension_ifs(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `_comprehension_ifs` of `if` prepended `expr`s SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__comprehension_ifs, _comprehension_ifs, sanitize,
                    _coerce_as__comprehension_ifs if coerce else None)


def code_as_arguments(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a arguments `FST` if possible."""

    return _code_as(code, parse_params, parse_arguments, arguments, sanitize)


def code_as_arguments_lambda(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a lambda arguments `FST` if possible (no annotations allowed)."""

    fst_ = _code_as(code, parse_params, parse_arguments_lambda, arguments, sanitize)

    if fst_ is code:  # validation if returning same FST that was passed in
        ast = fst_.a

        if (((args := ast.args) and any(a.annotation for a in args))
            or ((args := ast.kwonlyargs) and any(a.annotation for a in args))
            or ((arg := ast.vararg) and arg.annotation)
            or ((arg := ast.kwarg) and arg.annotation)
            or ((args := ast.posonlyargs) and any(a.annotation for a in args))
        ):
            raise NodeError('lambda arguments cannot have annotations')

    return fst_


def code_as_arg(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an arg `FST` if possible."""

    return _code_as(code, parse_params, parse_arg, arg, sanitize)


def code_as_keyword(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a keyword `FST` if possible."""

    return _code_as(code, parse_params, parse_keyword, keyword, sanitize)


def code_as_alias(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, star or dotted."""

    return _code_as(code, parse_params, parse_alias, alias, sanitize,
                    _coerce_as_alias if coerce else None)


def code_as__aliases(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, star or dotted."""

    return _code_as(code, parse_params, parse__aliases, _aliases, sanitize,
                    _coerce_as__aliases if coerce else None)


def code_as_Import_name(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, dotted as in `alias` for `Import.names`."""

    fst_ = _code_as(code, parse_params, parse_Import_name, alias, sanitize,
                    _coerce_as__Import_name if coerce else None)

    if fst_ is code:  # validation if returning same FST that was passed in
        if fst_.a.name == '*':
            raise NodeError("'*' star alias not allowed")

    return fst_


def code_as__Import_names(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, dotted as in `alias` for `Import.names`."""

    fst_ = _code_as(code, parse_params, parse__Import_names, _aliases, sanitize,
                    _coerce_as__Import_names if coerce else None)

    if fst_ is code:  # validation if returning same FST that was passed in
        if any(a.name == '*' for a in fst_.a.names):
            raise NodeError("'*' star alias not allowed")

    return fst_


def code_as_ImportFrom_name(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, possibly star as in `alias` for `FromImport.names`."""

    fst_ = _code_as(code, parse_params, parse_ImportFrom_name, alias, sanitize,
                    _coerce_as__ImportFrom_name if coerce else None)

    if fst_ is code:  # validation if returning same FST that was passed in
        if '.' in fst_.a.name:
            raise NodeError("'.' dotted alias not allowed")

    return fst_


def code_as__ImportFrom_names(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, possibly star as in `alias` for
    `FromImport.names`."""

    fst_ = _code_as(code, parse_params, parse__ImportFrom_names, _aliases, sanitize,
                    _coerce_as__ImportFrom_names if coerce else None)

    if fst_ is code:  # validation if returning same FST that was passed in
        for a in (names := fst_.a.names):
            if '.' in (n := a.name):
                raise NodeError("'.' dotted alias not allowed")

            if n == '*' and a is not names[0]:
                raise NodeError("'*' star can only be a single element")

        if len(names) > 1 and names[0].name == '*':
            raise NodeError("'*' star can only be a single element")

    return fst_


def code_as_withitem(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(code, parse_params, parse_withitem, withitem, sanitize,
                    _coerce_as_withitem if coerce else None)


def code_as__withitems(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `_withitems` of `withitem` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__withitems, _withitems, sanitize,
                    _coerce_as__withitems if coerce else None)


def code_as_pattern(
    code: Code,
    parse_params: Mapping[str, Any] = {},
    *,
    sanitize: bool = False,
    coerce: bool = False,
    allow_invalid_matchor: bool = False,
) -> fst.FST:
    """Convert `code` to a pattern `FST` if possible."""

    fst_ = _code_as(code, parse_params, parse_pattern, pattern, sanitize)

    if fst_ is code:  # validation if returning same FST that was passed in
        if not allow_invalid_matchor and isinstance(a := fst_.a, MatchOr):  # SPECIAL SLICE
            if not (len_pattern := len(a.patterns)):
                raise NodeError('expecting valid pattern, got zero-length MatchOr')

            if len_pattern == 1:  # a length 1 MatchOr can just return its single element pattern
                return fst.FST(a.patterns[0], fst_._lines, None, from_=fst_, lcopy=False)

    return fst_


def code_as_type_param(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a type_param `FST` if possible."""

    return _code_as(code, parse_params, parse_type_param, type_param, sanitize)


def code_as__type_params(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> fst.FST:
    """Convert `code` to a `_type_params` of `type_param` SPECIAL SLICE if possible."""

    return _code_as(code, parse_params, parse__type_params, _type_params, sanitize,
                    _coerce_as__type_params if coerce else None)


def code_as_identifier(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> str:
    """Convert `code` to valid identifier string if possible.

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier(code):
        raise ParseError(f'expecting identifier, got {shortstr(code)!r}')

    return code


def code_as_identifier_dotted(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> str:
    """Convert `code` to valid dotted identifier string if possible (for Import module).

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_dotted(code):
        raise ParseError(f'expecting dotted identifier, got {shortstr(code)!r}')

    return code


def code_as_identifier_star(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> str:
    """Convert `code` to valid identifier string or star '*' if possible (for ImportFrom names).

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_star(code):
        raise ParseError(f"expecting identifier or '*', got {shortstr(code)!r}")

    return code


def code_as_identifier_alias(
    code: Code, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> str:
    """Convert `code` to valid dotted identifier string or star '*' if possible (for any alias).

    **Note:** `sanitize` does nothing.
    """

    if isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_alias(code):
        raise ParseError(f"expecting dotted identifier or '*', got {shortstr(code)!r}")

    return code


def code_as_constant(
    code: Code | constant, parse_params: Mapping[str, Any] = {}, *, sanitize: bool = False, coerce: bool = False
) -> constant:
    """Convert `code` to valid constant if possible. If `code` is a `str` then it is treated as the constant value and
    not as the python representation of the constant. The only `FST` or `AST` accepted is a `Constant`, whose `value` is
    returned.

    **Note:** `sanitize` does nothing.
    """

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


# ......................................................................................................................
# internal stuff, not meant for direct user use

def code_as__expr_arglikes(
    code: Code,
    parse_params: Mapping[str, Any] = {},
    *,
    sanitize: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `Tuple` contianing possibly arglike expressions. Meant for putting slices to `Call.args` and
    `ClassDef.bases`. The `Tuple` will be unparenthesized and the location will be the entire source. We use a `Tuple`
    for this because unfortunately sometimes a `Tuple` is valid with arglikes in it and sometimes not.

    **WARNING!** The `Tuple` that is returned is just being used as a container and may be an invalid python `Tuple` as
    it may be an empty `Tuple` `AST` with source having no parentheses or an unparenthesized `Tuple` with incorrect
    start and stop locations (since its the whole source). Singleton `Tuple` may also not have trailing comma.
    """

    if isinstance(code, Tuple):  # strip parentheses
        code = _fixing_unparse(code)[1:-1]

    fst_ = _code_as(code, parse_params, parse__expr_arglikes, Tuple, sanitize,
                    _coerce_as__expr_arglikes if coerce else None)

    if fst_ is code:  # validation if returning same FST that was passed in
        if any(isinstance(e, Slice) for e in fst_.a.elts):
            raise NodeError('expecting non-Slice expressions (arglike), found Slice')

        if fst_._is_delimited_seq():
            fst_._trim_delimiters()

    return fst_
