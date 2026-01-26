"""Get single node.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from ast import literal_eval
from io import BytesIO
from tokenize import tokenize as tokenize_tokenize, STRING
from typing import Any, Mapping, Union

from . import fst

from .asttypes import (
    ASTS_LEAF_FTSTR_FMT,
    AST,
    And,
    AnnAssign,
    Assert,
    Assign,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    Attribute,
    AugAssign,
    Await,
    BinOp,
    BoolOp,
    Call,
    ClassDef,
    Compare,
    Constant,
    Delete,
    Dict,
    DictComp,
    ExceptHandler,
    Expr,
    Expression,
    For,
    FormattedValue,
    FunctionDef,
    GeneratorExp,
    Global,
    If,
    IfExp,
    Import,
    ImportFrom,
    Interactive,
    JoinedStr,
    Lambda,
    List,
    ListComp,
    Match,
    MatchAs,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    MatchSingleton,
    MatchStar,
    MatchValue,
    Module,
    Name,
    NamedExpr,
    Nonlocal,
    Or,
    Raise,
    Return,
    Set,
    SetComp,
    Slice,
    Starred,
    Subscript,
    Try,
    Tuple,
    UnaryOp,
    While,
    With,
    Yield,
    YieldFrom,
    alias,
    arg,
    arguments,
    comprehension,
    keyword,
    match_case,
    withitem,
    TryStar,
    TypeAlias,
    TypeVar,
    ParamSpec,
    TypeVarTuple,
    TemplateStr,
    Interpolation,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _arglikes,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from .astutil import constant, bistr, copy_ast, merge_arglikes
from .common import FTSTRING_END_TOKENS, PYGE13, NodeError, pyver
from .fst_misc import fixup_one_index
from .slice_stmtlike import get_slice_stmtlike


_GetOneRet = Union['fst.FST', None, str, constant]

class _NoCut(BaseException):
    """Raised from a handler to indicate that not explicit cut should be done after because the handler handled it."""


def _params_Compare(self: fst.FST, idx: int | None) -> tuple[int, str, AST | list[AST]]:
    """Convert `idx` of combined Compare all `left` and `comparators` fields into parameters which access the actual
    field.

    **Returns:**
    - `(idx, field, child)`: The real index (or `None` if is `left`), field name and field value (either `AST` of `left`
        or list of `AST`s of `comparators`).
    """

    ast         = self.a
    comparators = ast.comparators
    idx         = fixup_one_index(len(comparators) + 1, idx)

    if idx:
        return idx - 1, 'comparators', comparators
    else:
        return None, 'left', ast.left


def _validate_get(
    self: fst.FST, idx: int | None, field: str, start_at: int = 0, child: AST | list[AST] | None = None
) -> tuple[AST | None, int]:
    """Check that `idx` was passed (or not) as needed. `start_at` used for `_body` virtual field. `child` override used
    for `_args` and `_bases` virtual fields."""

    if child is None:
        child = getattr(self.a, field)

    if isinstance(child, list):
        if idx is None:
            raise IndexError(f'{self.a.__class__.__name__}.{field} needs an index')

        idx = fixup_one_index(len(child), idx, start_at)

        child = child[idx]

    elif idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')

    return child, idx


# ......................................................................................................................

def _get_one_default(
    self: fst.FST,
    idx: int | None,
    field: str, cut: bool,
    options: Mapping[str, Any],
    child: AST | list[AST] | None = None,
) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field, 0, child)

    if child is None:
        return None

    childf = child.f
    loc = childf.pars() if fst.FST.get_option('pars', options) is True else childf.bloc

    if not loc:
        raise ValueError('cannot get node which does not have a location')

    ret, _ = childf._make_fst_and_dedent(childf, copy_ast(child), loc, docstr=False)

    ret._fix_copy(options)

    return ret


def _get_one_stmtlike(self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]) -> _GetOneRet:
    if field == '_body':
        field = 'body'
        start_at = self.has_docstr
    else:
        start_at = 0

    _, idx = _validate_get(self, idx, field, start_at)

    return get_slice_stmtlike(self, idx, idx + 1, field, cut, options, one=True)


def _get_one_Compare(self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]) -> _GetOneRet:
    idx, field, _ = _params_Compare(self, idx)

    return _get_one_default(self, idx, field, cut, options)


def _get_one_ctx(self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    return fst.FST(child.__class__(), [''], None, from_=self)


def _get_one_identifier(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    return child


def _get_one_constant(self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    return child


def _get_one_arguments(self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]) -> _GetOneRet:
    if not self.a.args.f.is_empty_arguments():
        return _get_one_default(self, idx, field, cut, options)

    _validate_get(self, idx, field)

    return fst.FST(arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                   [''], None, from_=self)


def _get_one_arguments__all(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    ast = self.a
    len_body = len(ast.posonlyargs) + len(ast.args) + bool(ast.vararg) + len(ast.kwonlyargs) + bool(ast.kwarg)
    idx = fixup_one_index(len_body, idx)

    raise _NoCut(self._get_slice(idx, idx + 1, '_all', cut, options))  # succeed but without doing an explicit cut delete in the caller


def _get_one_BoolOp_op(self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    return (fst.FST(And(), ['and'], None, from_=self)
            if child.__class__ is And else
            fst.FST(Or(), ['or'], None, from_=self))  # just create new ones because they can be in multiple places


def _get_one_arglike(self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]) -> _GetOneRet:
    """Get a single element from combined `expr` and `keyword` list fields of `Call.args`+`Call.keywords` or
    `ClassDef.bases`+`ClassDef.keywords`."""

    ast = self.a
    child = merge_arglikes(getattr(ast, field[1:]), ast.keywords)

    return _get_one_default(self, idx, field, cut, options, child)


def _get_one_invalid_virtual(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    raise ValueError(f'cannot get single element from {self.a.__class__.__name__}.{field}')


@pyver(lt=12, else_=_get_one_default)
def _get_one_FormattedValue_value(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    """Correct for py < 3.12 returning value unparenthesized tuple with `FormattedValue` curlies as delimiters."""

    ret = _get_one_default(self, idx, field, cut, options)

    if ret.a.__class__ is Tuple:
        ln, col, end_ln, end_col = ret.loc
        lines = ret._lines

        if lines[ln].startswith('{', col) and (l := lines[end_ln]).endswith('}', 0, end_col):  # if curlies then replace them with parentheses
            lines[end_ln] = bistr(f'{l[:end_col - 1]}){l[end_col:]}')
            lines[ln] = bistr(f'{(l := lines[ln])[:col]}({l[col + 1:]}')

    return ret


def _get_one_conversion(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    if child == -1:
        return None

    conv = chr(child)

    return fst.FST(Constant(value=conv, lineno=1, col_offset=0, end_lineno=1, end_col_offset=3),
                   [f"'{conv}'"], None, from_=self)


@pyver(lt=12)
def _get_one_format_spec(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    raise NotImplementedError('get FormattedValue.format_spec not implemented on python < 3.12')

@pyver(ge=12)
def _get_one_format_spec(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)
    childf = child.f
    loc = childf.loc
    src = childf._get_src(*loc)

    if "'" not in src:  # early out for quotes
        prefix = 'f'
        quotes = "'"

    else:  # figure out which quotes to use by process of elimination
        quotes = {"'": True, '"': True, '"""': True, "'''": True}

        if src.endswith('"'):
            del quotes['"""']

        if src.endswith("'"):
            del quotes["'''"]

        for token in tokenize_tokenize(BytesIO(src.encode()).readline):
            if (ttype := token.type) == STRING:
                if (q := token.string[-3:]) not in ('"""', "'''"):
                    q = q[-1:]

            elif ttype in FTSTRING_END_TOKENS:
                q = token.string
            else:
                continue

            try:
                del quotes[q]
            except KeyError:
                pass

        if not quotes:
            raise RuntimeError('too may quotes, cannot figure out which to use')

        quotes = next(iter(quotes))
        prefix = 'f' + quotes[2:]

    assert child.__class__ is JoinedStr

    ret, _ = childf._make_fst_and_dedent(childf, copy_ast(child), loc, prefix, quotes, docstr=False)
    reta = ret.a

    if len(quotes) == 1:
        ret_lines = ret._lines
        ret_lines[0] = bistr(f"f{quotes}" + ret_lines[0][2:])
    else:
        ret._put_src([f'f{quotes}'], 0, 0, 0, 3, False)

    reta.col_offset = 0
    reta.end_col_offset += len(quotes)

    ret._touch()

    if PYGE13:
        for a in child.values:  # see if we need to make a raw formatted string, prepend an 'r' to the string start  # TODO: optimize this into the puts above
            if a.__class__ is Constant:
                if '\\' in (v := a.value) and v != literal_eval(f'{quotes}{childf._get_src(*a.f.loc)}{quotes}'):
                    ret._put_src('r', 0, 0, 0, 0, False, False)

                    break

    return ret


@pyver(lt=12)
def _get_one_JoinedStr_TemplateStr_values(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    raise NotImplementedError('get JoinedStr.values not implemented on python < 3.12')

@pyver(ge=12)
def _get_one_JoinedStr_TemplateStr_values(
    self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]
) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)
    childf = child.f
    child_cls = child.__class__

    ln, col, _, _ = self.loc
    lines = self.root._lines
    l = lines[ln]
    prefix = l[col : col + (4 if l.startswith('"""', col + 1) or l.startswith("'''", col + 1) else 2)]

    if child_cls is Constant:
        ret = fst.FST(copy_ast(child), Constant)  # this is because of implicit string madness

        # TODO: maybe pick this up again to return source-accurate string if possible?

        # loc = childf.loc
        # prefix = prefix [1:]
        # suffix = ''

        # if idx < len(self.a.values) - 1:  # this is ugly, but so are f-strings, its in case of stupidity like: f"{a}b" "c" 'ddd'
        #     try:
        #         literal_eval(f'{prefix}{self._get_src(*loc)}')
        #     except SyntaxError:
        #         suffix = prefix

        # ret, _ = childf._make_fst_and_dedent('', copy_ast(child), loc, prefix, suffix)
        # reta = ret.a
        # reta.col_offset = 0
        # reta.end_col_offset += len(suffix)

        # ret._touch()

        # if indent := childf._get_block_indent():
        #     ret._dedent_lns(indent, skip=1, docstr=False)

    else:
        assert child_cls in ASTS_LEAF_FTSTR_FMT  # (FormattedValue, Interpolation)

        typ = 'f' if child_cls is FormattedValue else 't'
        prefix = typ + prefix[1:]
        fmt, _ = childf._make_fst_and_dedent(childf, copy_ast(child), childf.loc, prefix, prefix[1:], docstr=False)
        lprefix = len(prefix)
        ret = fst.FST((JoinedStr if typ == 'f' else TemplateStr)
                      (values=[fmt.a], lineno=fmt.lineno, col_offset=fmt.col_offset - lprefix,
                       end_lineno=fmt.end_lineno, end_col_offset=fmt.end_col_offset + lprefix - 1),
                      fmt._lines, None, from_=self, lcopy=False)

    return ret


_GET_ONE_HANDLERS = {
    (Module, 'body'):                     _get_one_stmtlike,  # stmt*
    (Interactive, 'body'):                _get_one_stmtlike,  # stmt*
    (Expression, 'body'):                 _get_one_default,  # expr
    (FunctionDef, 'decorator_list'):      _get_one_default,  # expr*
    (FunctionDef, 'name'):                _get_one_identifier,  # identifier
    (FunctionDef, 'type_params'):         _get_one_default,  # type_param*
    (FunctionDef, 'args'):                _get_one_arguments,  # arguments
    (FunctionDef, 'returns'):             _get_one_default,  # expr?
    (FunctionDef, 'body'):                _get_one_stmtlike,  # stmt*
    (AsyncFunctionDef, 'decorator_list'): _get_one_default,  # expr*
    (AsyncFunctionDef, 'name'):           _get_one_identifier,  # identifier
    (AsyncFunctionDef, 'type_params'):    _get_one_default,  # type_param*
    (AsyncFunctionDef, 'args'):           _get_one_arguments,  # arguments
    (AsyncFunctionDef, 'returns'):        _get_one_default,  # expr?
    (AsyncFunctionDef, 'body'):           _get_one_stmtlike,  # stmt*
    (ClassDef, 'decorator_list'):         _get_one_default,  # expr*
    (ClassDef, 'name'):                   _get_one_identifier,  # identifier
    (ClassDef, 'type_params'):            _get_one_default,  # type_param*
    (ClassDef, 'bases'):                  _get_one_default,  # expr*
    (ClassDef, 'keywords'):               _get_one_default,  # keyword*
    (ClassDef, 'body'):                   _get_one_stmtlike,  # stmt*
    (ClassDef, '_bases'):                 _get_one_arglike,  # (expr|keyword)*
    (Return, 'value'):                    _get_one_default,  # expr?
    (Delete, 'targets'):                  _get_one_default,  # expr*
    (Assign, 'targets'):                  _get_one_default,  # expr*
    (Assign, 'value'):                    _get_one_default,  # expr
    (TypeAlias, 'name'):                  _get_one_default,  # expr
    (TypeAlias, 'type_params'):           _get_one_default,  # type_param*
    (TypeAlias, 'value'):                 _get_one_default,  # expr
    (AugAssign, 'target'):                _get_one_default,  # expr
    (AugAssign, 'op'):                    _get_one_default,  # operator
    (AugAssign, 'value'):                 _get_one_default,  # expr
    (AnnAssign, 'target'):                _get_one_default,  # expr
    (AnnAssign, 'annotation'):            _get_one_default,  # expr
    (AnnAssign, 'value'):                 _get_one_default,  # expr?
    (AnnAssign, 'simple'):                _get_one_constant,  # int
    (For, 'target'):                      _get_one_default,  # expr
    (For, 'iter'):                        _get_one_default,  # expr
    (For, 'body'):                        _get_one_stmtlike,  # stmt*
    (For, 'orelse'):                      _get_one_stmtlike,  # stmt*
    (AsyncFor, 'target'):                 _get_one_default,  # expr
    (AsyncFor, 'iter'):                   _get_one_default,  # expr
    (AsyncFor, 'body'):                   _get_one_stmtlike,  # stmt*
    (AsyncFor, 'orelse'):                 _get_one_stmtlike,  # stmt*
    (While, 'test'):                      _get_one_default,  # expr
    (While, 'body'):                      _get_one_stmtlike,  # stmt*
    (While, 'orelse'):                    _get_one_stmtlike,  # stmt*
    (If, 'test'):                         _get_one_default,  # expr
    (If, 'body'):                         _get_one_stmtlike,  # stmt*
    (If, 'orelse'):                       _get_one_stmtlike,  # stmt*
    (With, 'items'):                      _get_one_default,  # withitem*
    (With, 'body'):                       _get_one_stmtlike,  # stmt*
    (AsyncWith, 'items'):                 _get_one_default,  # withitem*
    (AsyncWith, 'body'):                  _get_one_stmtlike,  # stmt*
    (Match, 'subject'):                   _get_one_default,  # expr
    (Match, 'cases'):                     _get_one_stmtlike,  # match_case*
    (Raise, 'exc'):                       _get_one_default,  # expr?
    (Raise, 'cause'):                     _get_one_default,  # expr?
    (Try, 'body'):                        _get_one_stmtlike,  # stmt*
    (Try, 'handlers'):                    _get_one_stmtlike,  # excepthandler*
    (Try, 'orelse'):                      _get_one_stmtlike,  # stmt*
    (Try, 'finalbody'):                   _get_one_stmtlike,  # stmt*
    (TryStar, 'body'):                    _get_one_stmtlike,  # stmt*
    (TryStar, 'handlers'):                _get_one_stmtlike,  # excepthandler*
    (TryStar, 'orelse'):                  _get_one_stmtlike,  # stmt*
    (TryStar, 'finalbody'):               _get_one_stmtlike,  # stmt*
    (Assert, 'test'):                     _get_one_default,  # expr
    (Assert, 'msg'):                      _get_one_default,  # expr?
    (Import, 'names'):                    _get_one_default,  # alias*
    (ImportFrom, 'module'):               _get_one_identifier,  # identifier? (dotted)
    (ImportFrom, 'names'):                _get_one_default,  # alias*
    (ImportFrom, 'level'):                _get_one_constant,  # int?
    (Global, 'names'):                    _get_one_identifier,  # identifier*
    (Nonlocal, 'names'):                  _get_one_identifier,  # identifier*
    (Expr, 'value'):                      _get_one_default,  # expr
    (BoolOp, 'op'):                       _get_one_BoolOp_op,  # boolop
    (BoolOp, 'values'):                   _get_one_default,  # expr*
    (NamedExpr, 'target'):                _get_one_default,  # expr
    (NamedExpr, 'value'):                 _get_one_default,  # expr
    (BinOp, 'left'):                      _get_one_default,  # expr
    (BinOp, 'op'):                        _get_one_default,  # operator
    (BinOp, 'right'):                     _get_one_default,  # expr
    (UnaryOp, 'op'):                      _get_one_default,  # unaryop
    (UnaryOp, 'operand'):                 _get_one_default,  # expr
    (Lambda, 'args'):                     _get_one_arguments,  # arguments
    (Lambda, 'body'):                     _get_one_default,  # expr
    (IfExp, 'body'):                      _get_one_default,  # expr
    (IfExp, 'test'):                      _get_one_default,  # expr
    (IfExp, 'orelse'):                    _get_one_default,  # expr
    (Dict, 'keys'):                       _get_one_default,  # expr*
    (Dict, 'values'):                     _get_one_default,  # expr*
    (Dict, '_all'):                       _get_one_invalid_virtual,  # expr*
    (Set, 'elts'):                        _get_one_default,  # expr*
    (ListComp, 'elt'):                    _get_one_default,  # expr
    (ListComp, 'generators'):             _get_one_default,  # comprehension*
    (SetComp, 'elt'):                     _get_one_default,  # expr
    (SetComp, 'generators'):              _get_one_default,  # comprehension*
    (DictComp, 'key'):                    _get_one_default,  # expr
    (DictComp, 'value'):                  _get_one_default,  # expr
    (DictComp, 'generators'):             _get_one_default,  # comprehension*
    (GeneratorExp, 'elt'):                _get_one_default,  # expr
    (GeneratorExp, 'generators'):         _get_one_default,  # comprehension*
    (Await, 'value'):                     _get_one_default,  # expr
    (Yield, 'value'):                     _get_one_default,  # expr?
    (YieldFrom, 'value'):                 _get_one_default,  # expr
    (Compare, 'left'):                    _get_one_default,  # expr
    (Compare, 'ops'):                     _get_one_default,  # cmpop*
    (Compare, 'comparators'):             _get_one_default,  # expr*
    (Compare, '_all'):                    _get_one_Compare,  # expr*
    (Call, 'func'):                       _get_one_default,  # expr
    (Call, 'args'):                       _get_one_default,  # expr*
    (Call, 'keywords'):                   _get_one_default,  # keyword*
    (Call, '_args'):                      _get_one_arglike,  # (expr|keyword)*
    (FormattedValue, 'value'):            _get_one_FormattedValue_value,  # expr
    (FormattedValue, 'conversion'):       _get_one_conversion,  # int
    (FormattedValue, 'format_spec'):      _get_one_format_spec,  # expr?  - no location on py < 3.12
    (Interpolation, 'value'):             _get_one_default,  # expr
    (Interpolation, 'str'):               _get_one_constant,  # constant
    (Interpolation, 'conversion'):        _get_one_conversion,  # int
    (Interpolation, 'format_spec'):       _get_one_format_spec,  # expr?  - no location on py < 3.12
    (JoinedStr, 'values'):                _get_one_JoinedStr_TemplateStr_values,  # expr*  - no location on py < 3.12
    (TemplateStr, 'values'):              _get_one_JoinedStr_TemplateStr_values,  # expr*  - no location on py < 3.12
    (Constant, 'value'):                  _get_one_constant,  # constant
    (Constant, 'kind'):                   _get_one_constant,  # string?
    (Attribute, 'value'):                 _get_one_default,  # expr
    (Attribute, 'attr'):                  _get_one_identifier,  # identifier
    (Attribute, 'ctx'):                   _get_one_ctx,  # expr_context
    (Subscript, 'value'):                 _get_one_default,  # expr
    (Subscript, 'slice'):                 _get_one_default,  # expr
    (Subscript, 'ctx'):                   _get_one_ctx,  # expr_context
    (Starred, 'value'):                   _get_one_default,  # expr
    (Starred, 'ctx'):                     _get_one_ctx,  # expr_context
    (Name, 'id'):                         _get_one_identifier,  # identifier
    (Name, 'ctx'):                        _get_one_ctx,  # expr_context
    (List, 'elts'):                       _get_one_default,  # expr*
    (List, 'ctx'):                        _get_one_ctx,  # expr_context
    (Tuple, 'elts'):                      _get_one_default,  # expr*
    (Tuple, 'ctx'):                       _get_one_ctx,  # expr_context
    (Slice, 'lower'):                     _get_one_default,  # expr?
    (Slice, 'upper'):                     _get_one_default,  # expr?
    (Slice, 'step'):                      _get_one_default,  # expr?
    (comprehension, 'target'):            _get_one_default,  # expr
    (comprehension, 'iter'):              _get_one_default,  # expr
    (comprehension, 'ifs'):               _get_one_default,  # expr*
    (comprehension, 'is_async'):          _get_one_constant,  # int
    (ExceptHandler, 'type'):              _get_one_default,  # expr?
    (ExceptHandler, 'name'):              _get_one_identifier,  # identifier?
    (ExceptHandler, 'body'):              _get_one_stmtlike,  # stmt*
    (arguments, 'posonlyargs'):           _get_one_default,  # arg*
    (arguments, 'args'):                  _get_one_default,  # arg*
    (arguments, 'defaults'):              _get_one_default,  # expr*
    (arguments, 'vararg'):                _get_one_default,  # arg?
    (arguments, 'kwonlyargs'):            _get_one_default,  # arg*
    (arguments, 'kw_defaults'):           _get_one_default,  # expr*
    (arguments, 'kwarg'):                 _get_one_default,  # arg?
    (arguments, '_all'):                  _get_one_arguments__all,  # arguments
    (arg, 'arg'):                         _get_one_identifier,  # identifier
    (arg, 'annotation'):                  _get_one_default,  # expr?
    (keyword, 'arg'):                     _get_one_identifier,  # identifier?
    (keyword, 'value'):                   _get_one_default,  # expr
    (alias, 'name'):                      _get_one_identifier,  # identifier
    (alias, 'asname'):                    _get_one_identifier,  # identifier?
    (withitem, 'context_expr'):           _get_one_default,  # expr
    (withitem, 'optional_vars'):          _get_one_default,  # expr?
    (match_case, 'pattern'):              _get_one_default,  # pattern
    (match_case, 'guard'):                _get_one_default,  # expr?
    (match_case, 'body'):                 _get_one_stmtlike,  # stmt*
    (MatchValue, 'value'):                _get_one_default,  # expr
    (MatchSingleton, 'value'):            _get_one_constant,  # constant
    (MatchSequence, 'patterns'):          _get_one_default,  # pattern*
    (MatchMapping, 'keys'):               _get_one_default,  # expr*
    (MatchMapping, 'patterns'):           _get_one_default,  # pattern*
    (MatchMapping, 'rest'):               _get_one_identifier,  # identifier?
    (MatchMapping, '_all'):               _get_one_invalid_virtual,  # expr*
    (MatchClass, 'cls'):                  _get_one_default,  # expr
    (MatchClass, 'patterns'):             _get_one_default,  # pattern*
    (MatchClass, 'kwd_attrs'):            _get_one_identifier,  # identifier*
    (MatchClass, 'kwd_patterns'):         _get_one_default,  # pattern*
    (MatchStar, 'name'):                  _get_one_identifier,  # identifier?
    (MatchAs, 'pattern'):                 _get_one_default,  # pattern?
    (MatchAs, 'name'):                    _get_one_identifier,  # identifier?
    (MatchOr, 'patterns'):                _get_one_default,  # pattern*
    (TypeVar, 'name'):                    _get_one_identifier,  # identifier
    (TypeVar, 'bound'):                   _get_one_default,  # expr?
    (TypeVar, 'default_value'):           _get_one_default,  # expr?
    (ParamSpec, 'name'):                  _get_one_identifier,  # identifier
    (ParamSpec, 'default_value'):         _get_one_default,  # expr?
    (TypeVarTuple, 'name'):               _get_one_identifier,  # identifier
    (TypeVarTuple, 'default_value'):      _get_one_default,  # expr?

    (Module, '_body'):                    _get_one_stmtlike,  # stmt*  - without docstr
    (Interactive, '_body'):               _get_one_stmtlike,  # stmt*
    (FunctionDef, '_body'):               _get_one_stmtlike,  # stmt*
    (AsyncFunctionDef, '_body'):          _get_one_stmtlike,  # stmt*
    (ClassDef, '_body'):                  _get_one_stmtlike,  # stmt*
    (For, '_body'):                       _get_one_stmtlike,  # stmt*
    (AsyncFor, '_body'):                  _get_one_stmtlike,  # stmt*
    (While, '_body'):                     _get_one_stmtlike,  # stmt*
    (If, '_body'):                        _get_one_stmtlike,  # stmt*
    (With, '_body'):                      _get_one_stmtlike,  # stmt*
    (AsyncWith, '_body'):                 _get_one_stmtlike,  # stmt*
    (Try, '_body'):                       _get_one_stmtlike,  # stmt*
    (TryStar, '_body'):                   _get_one_stmtlike,  # stmt*
    (ExceptHandler, '_body'):             _get_one_stmtlike,  # stmt*
    (match_case, '_body'):                _get_one_stmtlike,  # stmt*

    (_ExceptHandlers, 'handlers'):        _get_one_stmtlike,  # ExceptHandler*
    (_match_cases, 'cases'):              _get_one_stmtlike,  # match_case*
    (_Assign_targets, 'targets'):         _get_one_default,  # expr*
    (_decorator_list, 'decorator_list'):  _get_one_default,  # expr*
    (_arglikes, 'arglikes'):              _get_one_default,  # (expr|keyword)*
    (_comprehensions, 'generators'):      _get_one_default,  # comprehension*
    (_comprehension_ifs, 'ifs'):          _get_one_default,  # expr*
    (_aliases, 'names'):                  _get_one_default,  # alias*
    (_withitems, 'items'):                _get_one_default,  # withitem*
    (_type_params, 'type_params'):        _get_one_default,  # type_param*


    # NOT DONE:
    # =========

    # (Module, 'type_ignores'):             (),  # type_ignore*

    # (FunctionType, 'argtypes'):           (),  # expr*
    # (FunctionType, 'returns'):            (),  # expr
    # (TypeIgnore, 'lineno'):               (),  # int
    # (TypeIgnore, 'tag'):                  (),  # string

    # (FunctionDef, 'type_comment'):        (),  # string?
    # (AsyncFunctionDef, 'type_comment'):   (),  # string?
    # (Assign, 'type_comment'):             (),  # string?
    # (For, 'type_comment'):                (),  # string?
    # (AsyncFor, 'type_comment'):           (),  # string?
    # (With, 'type_comment'):               (),  # string?
    # (AsyncWith, 'type_comment'):          (),  # string?
    # (arg, 'type_comment'):                (),  # string?
}


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _get_one(self: fst.FST, idx: int | None, field: str, cut: bool, options: Mapping[str, Any]) -> _GetOneRet:
    """Copy or cut (if possible) a node or non-node from a field of `self`."""

    if not (handler := _GET_ONE_HANDLERS.get((self.a.__class__, field))):
        raise NodeError(f'cannot get from {self.a.__class__.__name__}.{field}')

    if handler is _get_one_stmtlike:
        if cut:  # this one does its own cut (because of evil semicolons), so maybe need _modifying()
            with self._modifying(field):
                return handler(self, idx, field, cut, options)

        return handler(self, idx, field, cut, options)

    try:
        ret = handler(self, idx, field, cut, options)

    except _NoCut as exc:
        ret = exc.args[0]

    else:
        if cut:
            self._put_one(None, idx, field, dict(options, raw=False, to=None))

    return ret
