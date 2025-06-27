"""Get and put single node."""

from __future__ import annotations

import sys
from ast import *
from itertools import takewhile
from types import FunctionType, NoneType
from typing import Callable, NamedTuple, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, TypeVar, ParamSpec, TypeVarTuple, TemplateStr, Interpolation

from .misc import (
    Code, NodeError, astfield, fstloc,
    _next_src, _prev_src, _next_find, _prev_find, _next_find_re, _prev_pars, _fixup_one_index,
)

from .fst_parse import (
    _code_as_expr, _code_as_slice, _code_as_sliceelt, _code_as_callarg,
    _code_as_boolop, _code_as_binop, _code_as_augop, _code_as_unaryop, _code_as_cmpop,
    _code_as_pattern, _code_as_comprehension, _code_as_arguments,
    _code_as_arguments_lambda, _code_as_arg, _code_as_keyword, _code_as_alias_dotted, _code_as_alias_star,
    _code_as_withitem, _code_as_type_param, _code_as_identifier, _code_as_identifier_dotted, _code_as_identifier_alias,
    _code_as_constant,
)

_PY_VERSION = sys.version_info[:2]
_PYLT11     = _PY_VERSION < (3, 11)
_PYLT12     = _PY_VERSION < (3, 12)
_PYLT14     = _PY_VERSION < (3, 14)

_GetOneRet       = Union['FST', None, str, constant]
_PutOneCode      = Code | str | constant | None


def _params_Compare_combined(self: FST, idx: int | None) -> tuple[int, str, AST | list[AST]]:
    ast         = self.a
    comparators = ast.comparators
    idx         = _fixup_one_index(len(comparators) + 1, idx)

    return (idx - 1, 'comparators', comparators) if idx else (None, 'left', ast.left)


# ----------------------------------------------------------------------------------------------------------------------
# get

def _validate_get(self: FST, idx: int | None, field: str) -> AST | None:
    """Check that `idx` was passed (or not) as needed."""

    child = getattr(self.a, field)

    if isinstance(child, list):
        if idx is None:
            raise IndexError(f'{self.a.__class__.__name__}.{field} needs an index')

        _fixup_one_index(len(child), idx)

        child = child[idx]

    elif idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')

    return child, idx


# ......................................................................................................................

def _get_one_default(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    child, idx = _validate_get(self, idx, field)
    childf     = child.f
    loc        = childf.pars() if self.get_option('pars', options) is True else childf.bloc

    if not loc:
        raise ValueError('cannot copy node which does not have a location')

    ret = childf._make_fst_and_dedent(childf, copy_ast(child), loc, docstr=options.get('docstr'))

    ret._maybe_fix_copy(self.get_option('pars', options))

    return ret


def _get_one_stmtish(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    _, idx = _validate_get(self, idx, field)

    return self._get_slice_stmtish(idx, idx + 1, field, cut=cut, one=True, **options)


def _get_one_ctx(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    return FST(child.__class__(), [bistr('')], from_=self, lcopy=False)


def _get_one_identifier(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    return child


def _get_one_constant(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    return child


def _get_one_arguments(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    if not self.a.args.f._is_arguments_empty():
        return _get_one_default(self, idx, field, cut, **options)

    _validate_get(self, idx, field)

    return FST(arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]), [''], from_=self)


def _get_one_BoolOp_op(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    child, _ = _validate_get(self, idx, field)

    return FST(And(), ['and'], from_=self) if isinstance(child, And) else FST(Or(), ['or'], from_=self)  # just create new ones because they can be in multiple places


def _get_one_Compare_combined(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    idx, _, child = _params_Compare_combined(self, idx)

    return child.f if idx is None else child[idx].f


def _get_one_invalid_combined(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    raise ValueError(f'cannot get single element from combined field of {self.a.__class__.__name__}')


if _PYLT12:
    def _get_one_FormattedValue_value(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
        """Correct for py < 3.12 returning value unparenthesized tuple with `FormattedValue` curlies as delimiters."""

        ret = _get_one_default(self, idx, field, cut, **options)

        if isinstance(ret.a, Tuple):
            ln, col, end_ln, end_col = ret.loc
            lines                    = ret.lines

            if lines[ln].startswith('{', col) and (l := lines[end_ln]).endswith('}', 0, end_col):  # if curlies then replace them with parentheses
                lines[end_ln] = bistr(f'{l[:end_col - 1]}){l[end_col:]}')
                lines[ln]     = bistr(f'{(l := lines[ln])[:col]}({l[col + 1:]}')

        return ret


    def _get_one_conversion(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
        raise NotImplementedError('get FormattedValue.conversion not implemented on python < 3.12')


    def _get_one_format_spec(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
        raise NotImplementedError('get FormattedValue.format_spec not implemented on python < 3.12')


    def _get_one_JoinedStr_TemplateStr_values(self: FST, idx: int | None, field: str, cut: bool, **options,
                                              ) -> _GetOneRet:
        raise NotImplementedError('get JoinedStr.values not implemented on python < 3.12')


else:
    _get_one_FormattedValue_value = _get_one_default

    def _get_one_conversion(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
        child, _ = _validate_get(self, idx, field)

        if child == -1:
            return None

        conv = chr(child)

        return FST(Constant(value=conv, lineno=1, col_offset=0, end_lineno=1, end_col_offset=3), [bistr(f"'{conv}'")],
                   from_=self, lcopy=False)


    def _get_one_format_spec(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
        child, _ = _validate_get(self, idx, field)
        childf   = child.f
        ret      = childf._make_fst_and_dedent(childf, copy_ast(child), childf.loc, "f", "'",
                                               docstr=options.get('docstr'))
        ls[0]    = bistr("f'" + (ls := ret._lines)[0][2:])

        reta                 = ret.a
        reta.col_offset      = 0
        reta.end_col_offset += 1

        ret._touch()

        return ret


    def _get_one_JoinedStr_TemplateStr_values(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
        child, _      = _validate_get(self, idx, field)
        childf        = child.f

        ln, col, _, _ = self.loc
        lines         = self.root._lines
        l             = lines[ln]
        prefix        = l[col : col + (4 if l.startswith('"""', col + 1) or l.startswith("'''", col + 1) else 2)]

        if isinstance(child, Constant):
            ret = FST(copy_ast(child), Constant)  # this is because of implicit string madness

            # TODO: maybe pick this up again to return source-accurate string if possible?

            # loc    = childf.loc
            # prefix = prefix [1:]
            # suffix = ''

            # if idx < len(self.a.values) - 1:  # this is ugly, but so are f-strings, its in case of stupidity like: f"{a}b" "c" 'ddd'
            #     try:
            #         literal_eval(f'{prefix}{self.get_src(*loc)}')
            #     except SyntaxError:
            #         suffix = prefix

            # ret                  = childf._make_fst_and_dedent('', copy_ast(child), loc, prefix, suffix)
            # reta                 = ret.a
            # reta.col_offset      = 0
            # reta.end_col_offset += len(suffix)

            # ret._touch()

            # if indent := childf.get_indent():
            #     ret._dedent_lns(indent, skip=1, docstr=options.get('docstr'))

        else:
            assert isinstance(child, (FormattedValue, Interpolation))

            typ     = 'f' if isinstance(child, FormattedValue) else 't'
            prefix  = typ + prefix[1:]
            fmt     = childf._make_fst_and_dedent(childf, copy_ast(child), childf.loc, prefix, prefix[1:],
                                                  docstr=options.get('docstr'))
            lprefix = len(prefix)
            ret     = FST((JoinedStr if typ == 'f' else TemplateStr)
                          (values=[fmt.a], lineno=fmt.lineno, col_offset=fmt.col_offset - lprefix,
                           end_lineno=fmt.end_lineno, end_col_offset=fmt.end_col_offset + lprefix - 1),
                          fmt._lines, from_=self, lcopy=False)

        return ret


# ......................................................................................................................

def _get_one(self: FST, idx: int | None, field: str, cut: bool, **options) -> _GetOneRet:
    """Copy or cut (if possible) a node or non-node from a field of `self`."""

    ast = self.a

    if not (handler := _GET_ONE_HANDLERS.get((ast.__class__, field))):
        raise NodeError(f"cannot get from {ast.__class__.__name__}{f'.{field}' if field else ''}")

    ret = handler(self, idx, field, cut, **options)

    if handler is _get_one_stmtish:  # this one does its own cut (because of evil semicolons)
        return ret

    if cut:
        options['raw'] = False
        options['to']  = None

        self._put_one(None, idx, field, **options)

    return ret


# ......................................................................................................................

_GET_ONE_HANDLERS = {
    (Module, 'body'):                     _get_one_stmtish, # stmt*
    (Interactive, 'body'):                _get_one_stmtish, # stmt*
    (Expression, 'body'):                 _get_one_default, # expr
    (FunctionDef, 'decorator_list'):      _get_one_default, # expr*
    (FunctionDef, 'name'):                _get_one_identifier, # identifier
    (FunctionDef, 'type_params'):         _get_one_default, # type_param*
    (FunctionDef, 'args'):                _get_one_arguments, # arguments
    (FunctionDef, 'returns'):             _get_one_default, # expr?
    (FunctionDef, 'body'):                _get_one_stmtish, # stmt*
    (AsyncFunctionDef, 'decorator_list'): _get_one_default, # expr*
    (AsyncFunctionDef, 'name'):           _get_one_identifier, # identifier
    (AsyncFunctionDef, 'type_params'):    _get_one_default, # type_param*
    (AsyncFunctionDef, 'args'):           _get_one_arguments, # arguments
    (AsyncFunctionDef, 'returns'):        _get_one_default, # expr?
    (AsyncFunctionDef, 'body'):           _get_one_stmtish, # stmt*
    (ClassDef, 'decorator_list'):         _get_one_default, # expr*
    (ClassDef, 'name'):                   _get_one_identifier, # identifier
    (ClassDef, 'type_params'):            _get_one_default, # type_param*
    (ClassDef, 'bases'):                  _get_one_default, # expr*
    (ClassDef, 'keywords'):               _get_one_default, # keyword*
    (ClassDef, 'body'):                   _get_one_stmtish, # stmt*
    (Return, 'value'):                    _get_one_default, # expr?
    (Delete, 'targets'):                  _get_one_default, # expr*
    (Assign, 'targets'):                  _get_one_default, # expr*
    (Assign, 'value'):                    _get_one_default, # expr
    (TypeAlias, 'name'):                  _get_one_default, # expr
    (TypeAlias, 'type_params'):           _get_one_default, # type_param*
    (TypeAlias, 'value'):                 _get_one_default, # expr
    (AugAssign, 'target'):                _get_one_default, # expr
    (AugAssign, 'op'):                    _get_one_default, # operator
    (AugAssign, 'value'):                 _get_one_default, # expr
    (AnnAssign, 'target'):                _get_one_default, # expr
    (AnnAssign, 'annotation'):            _get_one_default, # expr
    (AnnAssign, 'value'):                 _get_one_default, # expr?
    (AnnAssign, 'simple'):                _get_one_constant, # int
    (For, 'target'):                      _get_one_default, # expr
    (For, 'iter'):                        _get_one_default, # expr
    (For, 'body'):                        _get_one_stmtish, # stmt*
    (For, 'orelse'):                      _get_one_stmtish, # stmt*
    (AsyncFor, 'target'):                 _get_one_default, # expr
    (AsyncFor, 'iter'):                   _get_one_default, # expr
    (AsyncFor, 'body'):                   _get_one_stmtish, # stmt*
    (AsyncFor, 'orelse'):                 _get_one_stmtish, # stmt*
    (While, 'test'):                      _get_one_default, # expr
    (While, 'body'):                      _get_one_stmtish, # stmt*
    (While, 'orelse'):                    _get_one_stmtish, # stmt*
    (If, 'test'):                         _get_one_default, # expr
    (If, 'body'):                         _get_one_stmtish, # stmt*
    (If, 'orelse'):                       _get_one_stmtish, # stmt*
    (With, 'items'):                      _get_one_default, # withitem*
    (With, 'body'):                       _get_one_stmtish, # stmt*
    (AsyncWith, 'items'):                 _get_one_default, # withitem*
    (AsyncWith, 'body'):                  _get_one_stmtish, # stmt*
    (Match, 'subject'):                   _get_one_default, # expr
    (Match, 'cases'):                     _get_one_stmtish, # match_case*
    (Raise, 'exc'):                       _get_one_default, # expr?
    (Raise, 'cause'):                     _get_one_default, # expr?
    (Try, 'body'):                        _get_one_stmtish, # stmt*
    (Try, 'handlers'):                    _get_one_stmtish, # excepthandler*
    (Try, 'orelse'):                      _get_one_stmtish, # stmt*
    (Try, 'finalbody'):                   _get_one_stmtish, # stmt*
    (TryStar, 'body'):                    _get_one_stmtish, # stmt*
    (TryStar, 'handlers'):                _get_one_stmtish, # excepthandler*
    (TryStar, 'orelse'):                  _get_one_stmtish, # stmt*
    (TryStar, 'finalbody'):               _get_one_stmtish, # stmt*
    (Assert, 'test'):                     _get_one_default, # expr
    (Assert, 'msg'):                      _get_one_default, # expr?
    (Import, 'names'):                    _get_one_default, # alias*
    (ImportFrom, 'module'):               _get_one_identifier, # identifier? (dotted)
    (ImportFrom, 'names'):                _get_one_default, # alias*
    (ImportFrom, 'level'):                _get_one_constant, # int?
    (Global, 'names'):                    _get_one_identifier, # identifier*
    (Nonlocal, 'names'):                  _get_one_identifier, # identifier*
    (Expr, 'value'):                      _get_one_default, # expr
    (BoolOp, 'op'):                       _get_one_BoolOp_op, # boolop
    (BoolOp, 'values'):                   _get_one_default, # expr*
    (NamedExpr, 'target'):                _get_one_default, # expr
    (NamedExpr, 'value'):                 _get_one_default, # expr
    (BinOp, 'left'):                      _get_one_default, # expr
    (BinOp, 'op'):                        _get_one_default, # operator
    (BinOp, 'right'):                     _get_one_default, # expr
    (UnaryOp, 'op'):                      _get_one_default, # unaryop
    (UnaryOp, 'operand'):                 _get_one_default, # expr
    (Lambda, 'args'):                     _get_one_arguments, # arguments
    (Lambda, 'body'):                     _get_one_default, # expr
    (IfExp, 'body'):                      _get_one_default, # expr
    (IfExp, 'test'):                      _get_one_default, # expr
    (IfExp, 'orelse'):                    _get_one_default, # expr
    (Dict, 'keys'):                       _get_one_default, # expr*
    (Dict, 'values'):                     _get_one_default, # expr*
    (Dict, ''):                           _get_one_invalid_combined, # expr*
    (Set, 'elts'):                        _get_one_default, # expr*
    (ListComp, 'elt'):                    _get_one_default, # expr
    (ListComp, 'generators'):             _get_one_default, # comprehension*
    (SetComp, 'elt'):                     _get_one_default, # expr
    (SetComp, 'generators'):              _get_one_default, # comprehension*
    (DictComp, 'key'):                    _get_one_default, # expr
    (DictComp, 'value'):                  _get_one_default, # expr
    (DictComp, 'generators'):             _get_one_default, # comprehension*
    (GeneratorExp, 'elt'):                _get_one_default, # expr
    (GeneratorExp, 'generators'):         _get_one_default, # comprehension*
    (Await, 'value'):                     _get_one_default, # expr
    (Yield, 'value'):                     _get_one_default, # expr?
    (YieldFrom, 'value'):                 _get_one_default, # expr
    (Compare, 'left'):                    _get_one_default, # expr
    (Compare, 'ops'):                     _get_one_default, # cmpop*
    (Compare, 'comparators'):             _get_one_default, # expr*
    (Compare, ''):                        _get_one_Compare_combined, # expr*
    (Call, 'func'):                       _get_one_default, # expr
    (Call, 'args'):                       _get_one_default, # expr*
    (Call, 'keywords'):                   _get_one_default, # keyword*
    (FormattedValue, 'value'):            _get_one_FormattedValue_value, # expr
    (FormattedValue, 'conversion'):       _get_one_conversion, # int
    (FormattedValue, 'format_spec'):      _get_one_format_spec, # expr?  - no location on py < 3.12
    (Interpolation, 'value'):             _get_one_default, # expr
    (Interpolation, 'str'):               _get_one_constant, # constant
    (Interpolation, 'conversion'):        _get_one_conversion, # int
    (Interpolation, 'format_spec'):       _get_one_format_spec, # expr?  - no location on py < 3.12
    (JoinedStr, 'values'):                _get_one_JoinedStr_TemplateStr_values, # expr*  - no location on py < 3.12
    (TemplateStr, 'values'):              _get_one_JoinedStr_TemplateStr_values, # expr*  - no location on py < 3.12
    (Constant, 'value'):                  _get_one_constant, # constant
    (Constant, 'kind'):                   _get_one_constant, # string?
    (Attribute, 'value'):                 _get_one_default, # expr
    (Attribute, 'attr'):                  _get_one_identifier, # identifier
    (Attribute, 'ctx'):                   _get_one_ctx, # expr_context
    (Subscript, 'value'):                 _get_one_default, # expr
    (Subscript, 'slice'):                 _get_one_default, # expr
    (Subscript, 'ctx'):                   _get_one_ctx, # expr_context
    (Starred, 'value'):                   _get_one_default, # expr
    (Starred, 'ctx'):                     _get_one_ctx, # expr_context
    (Name, 'id'):                         _get_one_identifier, # identifier
    (Name, 'ctx'):                        _get_one_ctx, # expr_context
    (List, 'elts'):                       _get_one_default, # expr*
    (List, 'ctx'):                        _get_one_ctx, # expr_context
    (Tuple, 'elts'):                      _get_one_default, # expr*
    (Tuple, 'ctx'):                       _get_one_ctx, # expr_context
    (Slice, 'lower'):                     _get_one_default, # expr?
    (Slice, 'upper'):                     _get_one_default, # expr?
    (Slice, 'step'):                      _get_one_default, # expr?
    (comprehension, 'target'):            _get_one_default, # expr
    (comprehension, 'iter'):              _get_one_default, # expr
    (comprehension, 'ifs'):               _get_one_default, # expr*
    (comprehension, 'is_async'):          _get_one_constant, # int
    (ExceptHandler, 'type'):              _get_one_default, # expr?
    (ExceptHandler, 'name'):              _get_one_identifier, # identifier?
    (ExceptHandler, 'body'):              _get_one_stmtish, # stmt*
    (arguments, 'posonlyargs'):           _get_one_default, # arg*
    (arguments, 'args'):                  _get_one_default, # arg*
    (arguments, 'defaults'):              _get_one_default, # expr*
    (arguments, 'vararg'):                _get_one_default, # arg?
    (arguments, 'kwonlyargs'):            _get_one_default, # arg*
    (arguments, 'kw_defaults'):           _get_one_default, # expr*
    (arguments, 'kwarg'):                 _get_one_default, # arg?
    (arg, 'arg'):                         _get_one_identifier, # identifier
    (arg, 'annotation'):                  _get_one_default, # expr?
    (keyword, 'arg'):                     _get_one_identifier, # identifier?
    (keyword, 'value'):                   _get_one_default, # expr
    (alias, 'name'):                      _get_one_identifier, # identifier
    (alias, 'asname'):                    _get_one_identifier, # identifier?
    (withitem, 'context_expr'):           _get_one_default, # expr
    (withitem, 'optional_vars'):          _get_one_default, # expr?
    (match_case, 'pattern'):              _get_one_default, # pattern
    (match_case, 'guard'):                _get_one_default, # expr?
    (match_case, 'body'):                 _get_one_stmtish, # stmt*
    (MatchValue, 'value'):                _get_one_default, # expr
    (MatchSingleton, 'value'):            _get_one_constant, # constant
    (MatchSequence, 'patterns'):          _get_one_default, # pattern*
    (MatchMapping, 'keys'):               _get_one_default, # expr*
    (MatchMapping, 'patterns'):           _get_one_default, # pattern*
    (MatchMapping, 'rest'):               _get_one_identifier, # identifier?
    (MatchMapping, ''):                   _get_one_invalid_combined, # expr*
    (MatchClass, 'cls'):                  _get_one_default, # expr
    (MatchClass, 'patterns'):             _get_one_default, # pattern*
    (MatchClass, 'kwd_attrs'):            _get_one_identifier, # identifier*
    (MatchClass, 'kwd_patterns'):         _get_one_default, # pattern*
    (MatchStar, 'name'):                  _get_one_identifier, # identifier?
    (MatchAs, 'pattern'):                 _get_one_default, # pattern?
    (MatchAs, 'name'):                    _get_one_identifier, # identifier?
    (MatchOr, 'patterns'):                _get_one_default, # pattern*
    (TypeVar, 'name'):                    _get_one_identifier, # identifier
    (TypeVar, 'bound'):                   _get_one_default, # expr?
    (TypeVar, 'default_value'):           _get_one_default, # expr?
    (ParamSpec, 'name'):                  _get_one_identifier, # identifier
    (ParamSpec, 'default_value'):         _get_one_default, # expr?
    (TypeVarTuple, 'name'):               _get_one_identifier, # identifier
    (TypeVarTuple, 'default_value'):      _get_one_default, # expr?


    # NOT DONE:
    # =========

    # (Module, 'type_ignores'):             (), # type_ignore*

    # (FunctionType, 'argtypes'):           (), # expr*
    # (FunctionType, 'returns'):            (), # expr
    # (TypeIgnore, 'lineno'):               (), # int
    # (TypeIgnore, 'tag'):                  (), # string

    # (FunctionDef, 'type_comment'):        (), # string?
    # (AsyncFunctionDef, 'type_comment'):   (), # string?
    # (Assign, 'type_comment'):             (), # string?
    # (For, 'type_comment'):                (), # string?
    # (AsyncFor, 'type_comment'):           (), # string?
    # (With, 'type_comment'):               (), # string?
    # (AsyncWith, 'type_comment'):          (), # string?
    # (arg, 'type_comment'):                (), # string?
}

# ----------------------------------------------------------------------------------------------------------------------
# put

class onestatic(NamedTuple):
    getinfo:  Callable[[FST, onestatic, int | None, str], oneinfo] | None
    restrict: type[AST] | tuple[type[AST]] | list[type[AST]] | Callable[[AST], bool] | None = None
    code_as:  Callable[[Code, dict], FST]                                                   = _code_as_expr
    ctx:      type[expr_context]                                                            = Load


class oneinfo(NamedTuple):
    prefix:      str           = ''    # prefix to add on insert
    loc_insdel:  fstloc | None = None  # only present if insert (put new to nonexistent) or delete is possible and is the location for the specific mutually-exclusive operation
    loc_ident:   fstloc | None = None  # location of identifier
    suffix:      str           = ''    # or ': ' for dict '**'
    delstr:      str           = ''    # or '**'


def _validate_put(self: FST, code: Code | None, idx: int | None, field: str, child: list[AST] | AST | constant | None,
                  *, can_del: bool = False) -> AST | constant | None:
    """Check that `idx` was passed (or not) as needed and that not deleting if not possible."""

    if isinstance(child, list):
        if idx is None:
            raise IndexError(f'{self.a.__class__.__name__}.{field} needs an index')

        _fixup_one_index(len(child), idx)

        child = child[idx]  # this will always be a required child, variable size lists will have been passed on to slice processing before getting here

    elif idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')

    if not can_del and code is None:
        raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field}{"" if idx is None else f"[{idx}]"}')

    return child


def _validate_put_ast(self: FST, put_ast: AST, idx: int | None, field: str, static: onestatic):
    if restrict := static.restrict:
        if isinstance(restrict, list):  # list means these types not allowed
            if isinstance(put_ast, tuple(restrict)):
                raise NodeError(f'{self.a.__class__.__name__}.{field}{" " if idx is None else f"[{idx}] "}'
                                f'cannot be {put_ast.__class__.__name__}')

        elif isinstance(restrict, FunctionType):
            if not restrict(put_ast):  # not "restrict" meaning is inverted here, really means "not allow"
                raise NodeError(f'invalid value for {self.a.__class__.__name__}.{field}' +
                                ('' if idx is None else f'[{idx}]'))

        elif not isinstance(put_ast, restrict):  # single AST type or tuple means only these allowed
            raise NodeError((f'expecting a {restrict.__name__} for {self.a.__class__.__name__}.{field}'
                              if isinstance(restrict, type) else
                              f'expecting one of ({", ".join(c.__name__ for c in restrict)}) for '
                              f'{self.a.__class__.__name__}.{field}{"" if idx is None else f"[{idx}]"}') +
                             f', got {put_ast.__class__.__name__}')


def _validate_pattern_expr(self: FST):
    while True:
        if self.pars().n:
            raise NodeError(f'cannot put parenthesized {self.a.__class__.__name__} to pattern expression')

        if isinstance(a := self.a, Name):
            break

        if not isinstance(a, Attribute):
            raise NodeError(f'cannot put {self.a.__class__.__name__} to pattern expression')

        self = a.value.f


def _is_valid_MatchClass_cls(ast: AST) -> bool:
    if (f := ast.f).end_ln != f.ln:
        raise NodeError(f'cannot put multiline {ast.__class__.__name__} to MatchClass pattern expression')

    _validate_pattern_expr(ast.f)

    return True


def _is_valid_MatchValue_value(ast: AST) -> bool:
    if not is_valid_MatchValue_value(ast):
        return False

    # if (f := ast.f).end_ln != f.ln:
    #     raise NodeError(f'cannot put multiline {ast.__class__.__name__} to pattern expression')

    if any((bad := f).pars().n for f in ast.f.walk(True)):
        raise NodeError(f'cannot put parenthesized {bad.a.__class__.__name__} to pattern expression')

    return True


def _is_valid_MatchMapping_key(ast: AST) -> bool:
    if not is_valid_MatchMapping_key(ast):
        return False

    # if (f := ast.f).end_ln != f.ln:
    #     raise NodeError(f'cannot put multiline {ast.__class__.__name__} to pattern expression')

    if any((bad := f).pars().n for f in ast.f.walk(True)):
        raise NodeError(f'cannot put parenthesized {bad.a.__class__.__name__} to pattern expression')

    return True


def _maybe_par_above(above: FST, below: FST) -> bool:
    while isinstance(a := below.a, (Attribute, Subscript)):
        if below.pars().n:
            above._parenthesize_grouping()

            return True

        below = a.value.f

    else:
        if isinstance(a, Name) and below.pars().n:
            above._parenthesize_grouping()

            return True

    return False

# ......................................................................................................................
# other

def _put_one_constant(self: FST, code: _PutOneCode, idx: int | None, field: str, child: constant, static: onestatic,
                      **options) -> FST:
    """Put a single constant value, only Constant and MatchSingleton (and only exists because of the second one)."""

    _validate_put(self, code, idx, field, child, can_del=True)  # can_del so that None is accepted

    value    = _code_as_constant(code, self.root.parse_params)
    restrict = static.restrict

    if not isinstance(value, restrict):
        raise NodeError((f'expecting a {"constant" if restrict is constant else restrict.__name__} '
                         f'for {self.a.__class__.__name__}.{field}'                         if not isinstance(restrict, tuple) else
                         f'expecting one of ({", ".join(c.__name__ for c in restrict)}) for '
                         f'{self.a.__class__.__name__}') +
                        f', got {value.__class__.__name__}')

    self._put_src(repr(value), *self.loc, True)

    ast       = self.a
    ast.value = value

    if hasattr(ast, 'kind'):  # reset any 'u' kind strings
        ast.kind = None

    return self  # this breaks the rule of returning the child node since it is just a primitive


def _put_one_op(self: FST, code: _PutOneCode, idx: int | None, field: str,
                child: type[boolop] | type[operator] | type[unaryop] | type[cmpop],
                static: None, **options) -> FST:
    """Put a single operator, with or without '=' for AugAssign, lots of rules to check."""

    child  = _validate_put(self, code, idx, field, child)
    code   = static.code_as(code, self.root.parse_params)
    codea  = code.a
    childf = child.f

    if self.parent_pattern():  # if we are in a pattern then replacements are restricted
        if isinstance(child, USub):  # indicates we are in UnaryOp
            if not isinstance(codea, USub):
                raise NodeError("cannot put anything other than '-' to a pattern UnaryOp.op")

        elif not isinstance(codea, (Add, Sub)):  # otherwise MUST be BinOp
            raise NodeError("cannot put anything other than '+' or '-' to a pattern BinOp.op")

    is_alnum = isinstance(codea, (Not, Is, IsNot, In, NotIn))  # alphanumneric operators may need spaces added

    self._put_src(code._lines, *childf.loc, False)
    childf._set_ast(codea)

    ast = self.a

    if (is_bin := isinstance(ast, BinOp)) or isinstance(ast, UnaryOp):  # parenthesize if precedence requires according to new operator
        if (parent := self.parent) and precedence_require_parens(ast, parent.a, *self.pfield) and not self.pars().n:
            self._parenthesize_grouping()

        if not is_bin:
            if precedence_require_parens(operand := ast.operand, ast, 'operand') and not (f := operand.f).pars().n:
                f._parenthesize_grouping()

        else:
            if precedence_require_parens(left := ast.left, ast, 'left') and not (f := left.f).pars().n:
                f._parenthesize_grouping()

            if precedence_require_parens(right := ast.right, ast, 'right') and not (f := right.f).pars().n:
                f._parenthesize_grouping()

    if is_alnum:  # we do this after parenthesization because it can remove the need for spaces
        ln, col, end_ln, end_col = get_field(ast, field, idx).f.loc
        lines                    = self.root._lines

        if re_alnum.match(lines[end_ln], end_col):  # insert space at end of operator?
            self._put_src([' '], end_ln, end_col, end_ln, end_col, False)

        if col and re_alnum.match(lines[ln], col - 1):  # insert space at start of operator? don't need to offset head because operator doesn't have `col_offset`
            self._put_src([' '], ln, col, ln, col, False)

    return childf


def _put_one_ctx(self: FST, code: _PutOneCode, idx: int | None, field: str,
                 child: type[boolop] | type[operator] | type[unaryop] | type[cmpop],
                 static: None, **options) -> FST:
    """This only exists to absorb the put and validate that it is the only value it can be."""

    child = _validate_put(self, code, idx, field, child)

    if isinstance(code, FST):
        code = code.a
    elif not isinstance(code, AST):
        raise ValueError(f'expecting expr_context, got {code.__class__.__name__}')

    if code.__class__ is not child.__class__:
        raise ValueError(f'invalid expr_context, can only be {child.__class__.__name__}')

    return child.f


def _put_one_AnnAssign_simple(self: FST, code: _PutOneCode, idx: int | None, field: str, child: int, static: onestatic,
                              **options) -> FST:
    """Parenthesize or unparenthesize `AnnAssign.value` according to this, overkill, definitely overkill."""

    ast   = self.a
    child = _validate_put(self, code, idx, field, child)
    value = _code_as_constant(code, self.root.parse_params)

    if value.__class__ is not int or not 0 <= value <= 1:
        raise ValueError('expection 0 or 1')

    is_name = isinstance(target := ast.target, Name)

    if value:
        if not is_name:
            raise ValueError('cannot make simple')

        target.f._unparenthesize_grouping()

    elif is_name and not target.f.pars().n:
        target.f._parenthesize_grouping()

    self.a.simple = value

    return self  # cannot return primitive


def _put_one_BoolOp_op(self: FST, code: _PutOneCode, idx: int | None, field: str, child: type[boolop], static: None,
                       **options) -> FST:
    """Put BoolOp op to potentially multiple places."""

    child  = _validate_put(self, code, idx, field, child)
    code   = _code_as_boolop(code, self.root.parse_params)
    childf = child.f
    src    = 'and' if isinstance(codea := code.a, And) else 'or'
    tgt    = 'and' if isinstance(child, And) else 'or'
    ltgt   = len(tgt)
    lines  = self.root._lines

    _, _, end_ln, end_col = self.loc

    for value in self.a.values[-2::-1]:  # reverse direction so that we don't need to refresh end_col
        _, _, ln, col = value.f.pars()
        ln, col       = _next_find(lines, ln, col, end_ln, end_col, tgt)  # must be there

        self._put_src(src, ln, col, ln, col + ltgt, False)

    childf._set_ast(codea)

    if src != tgt:  # if replacing with different boolop then need to parenthesize self if parent is BoolOp or children if they are BoolOps to keep structure regardless of precedence
        if (parent := self.parent) and isinstance(parent.a, BoolOp) and not self.pars().n:
            self._parenthesize_grouping()

        for a in self.a.values:
            if isinstance(a, BoolOp) and not (f := a.f).pars().n:
                f._parenthesize_grouping()

    return childf


def _put_one_NOT_IMPLEMENTED_YET(self: FST, code: _PutOneCode, idx: int | None, field: str, child: constant,
                                 static: onestatic, **options) -> FST:
    raise NotImplementedError('this is not implemented yet')


if _PYLT12:
    def _put_one_NOT_IMPLEMENTED_YET_12(self: FST, code: _PutOneCode, idx: int | None, field: str, child: constant,
                                        static: onestatic, **options) -> FST:
        raise NotImplementedError('this will only be implemented on python version 3.12 and above')

else:
    _put_one_NOT_IMPLEMENTED_YET_12 = _put_one_NOT_IMPLEMENTED_YET


if _PYLT14:
    def _put_one_NOT_IMPLEMENTED_YET_14(self: FST, code: _PutOneCode, idx: int | None, field: str, child: constant,
                                        static: onestatic, **options) -> FST:
        raise NotImplementedError('this will only be implemented on python version 3.14 and above')

else:
    _put_one_NOT_IMPLEMENTED_YET_14 = _put_one_NOT_IMPLEMENTED_YET


# ......................................................................................................................
# exprish (expr, pattern, comprehension, etc...)

def _make_exprish_fst(self: FST, code: _PutOneCode, idx: int | None, field: str, static: onestatic,
                      target: FST | fstloc, ctx: type[expr_context], prefix: str  = '', suffix: str = '',
                      validated: int = 0, **options) -> FST:
    """Make an expression `FST` from `Code` for a field/idx containing an existing node creating a new one. Takes care
    of parenthesizing, indenting and offsetting."""

    put_fst = static.code_as(code, self.root.parse_params) if validated < 2 else code
    put_ast = put_fst.a

    _validate_put_ast(self, put_ast, idx, field, static)

    # figure out parentheses

    pars         = FST.get_option('pars', options)
    put_is_star  = isinstance(put_ast, Starred)
    tgt_is_FST   = target.is_FST
    del_tgt_pars = False

    def need_pars(adding: bool) -> bool:
        if not put_fst.is_atom(pars=False):
            if not put_is_star:
                if precedence_require_parens(put_ast, self.a, field, idx):
                    return True

            else:  # Starred gets checked against its child value in the context of being a call arg or not
                if precedence_require_parens(put_ast.value, put_ast, 'value',
                                             star_call_arg=field == 'args' and isinstance(self.a, Call)):
                    return True

        elif (tgt_is_FST and field == 'value' and isinstance(put_ast, Constant) and isinstance(put_ast.value, int) and  # veeery special case "3.__abs__()" -> "(3).__abs__()"
              (tgt_parent := target.parent) and isinstance(tgt_parent.a, Attribute)):
            return True

        if not self.is_enclosed_in_parents(field) and not put_fst.is_enclosed(pars=adding):
            return True

        if isinstance(put_ast, Lambda):  # Lambda inside FormattedValue/Interpolation needs pars
            s = self
            f = field

            while isinstance(a := s.a, expr):
                if isinstance(a, (FormattedValue, Interpolation)):
                    if f == 'value':
                        return True

                    break

                if s.is_atom(pars=True, always_enclosed=True):
                    break

                if not (f := s.pfield):
                    break

                s = s.parent
                f = f.name

        return False

    if pars:
        if getattr((put_ast.value.f if put_is_star else put_fst).pars(), 'n', 0):  # src has grouping pars, or src.value if src is Starred
            del_tgt_pars = True

            if pars == 'auto':
                if not need_pars(False):
                    put_fst._unparenthesize_grouping()

        else:  # src does not have grouping pars
            if ((tgt_has_pars := tgt_is_FST and getattr(target.pars(), 'n', 0)) and
                put_fst.is_parenthesized_tuple() is False
            ):
                del_tgt_pars = True
                tgt_has_pars = False

            if tgt_has_pars:
                if not need_pars(True):
                    if pars is True or not (field == 'target' and (tgt_parent := target.parent) and  # suuuper minor special case, don't automatically unparenthesize AnnAssign targets
                                            isinstance(tgt_parent.a, AnnAssign)):
                        del_tgt_pars = True

            elif need_pars(True):
                put_fst.par(True)  # could be parenthesizing grouping or a tuple

    # figure out put target location

    if not tgt_is_FST:
        ln, col, end_ln, end_col = target

    else:
        loc = target.pars(False) if del_tgt_pars else target.loc

        if not del_tgt_pars and target.is_solo_call_arg_genexp():  # need to check this otherwise might eat Call args pars
            if (loc2 := target.pars(False)) > loc:
                loc = loc2

        ln, col, end_ln, end_col = loc

    # do it

    lines     = self.root._lines
    put_lines = put_fst._lines

    merge_alnum_start = bool(col and re_two_alnum.match(lines[ln][col - 1] + (prefix or put_lines[0][:1])))  # would the start location result in a merged alphanumeric? we do this here because we need to know if to offset put_fst by one more space
    merge_alnum_end   = bool(end_col < len(l := lines[end_ln]) and re_two_alnum.match((suffix or put_lines[-1])[-1:] + l[end_col]))  # would end location result in merged alphanumeric?

    if prefix:
        put_fst._put_src([prefix], 0, 0, 0, 0, True)

    if suffix:
        put_lines[-1] = bistr(put_lines[-1] + suffix)  # don't need to offset anything so just tack onto the end

    put_fst._indent_lns(self.get_indent(), docstr=options.get('docstr'))

    dcol_offset    = lines[ln].c2b(col) + merge_alnum_start
    end_col_offset = lines[end_ln].c2b(end_col)

    params_offset  = self._put_src(put_lines, ln, col, end_ln, end_col, True, False, exclude=self)

    self._offset(*params_offset, exclude=target, self_=False)  # excluding an fstloc instead of FST is harmless, will not exclude anything
    put_fst._offset(0, 0, ln, dcol_offset)
    set_ctx(put_ast, ctx)

    # if put merged alphanumerics at start and / or end then insert spaces

    if merge_alnum_end:  # we do this first because merged alnum at start could change our location
        send_ln  = ln + (dln := len(put_lines) - 1)
        send_col = len(put_lines[-1]) if dln else col + len(put_lines[0])

        self._put_src([' '], send_ln, send_col, send_ln, send_col, False)

    if merge_alnum_start:  # we put this after because otherwise would be included in any parents that start at element being put
        self._put_src([' '], ln, col, ln, col, False)

    # possibly fix FormattedValue and Interpolation .format_spec location if present above self - because can follow IMMEDIATELY after modified value (which doesn't normally happen in py syntax) and thus would not have their start offset due to head=False in put_src() above

    cur = self

    while parent := cur.parent:
        if isinstance(parenta := parent.a, (FormattedValue, Interpolation)):
            if (cur.pfield.name == 'value' and (fs := parenta.format_spec) and
                fs.col_offset == end_col_offset and fs.lineno == end_ln + 1
            ):
                fs.lineno     = (a := self.a).end_lineno
                fs.col_offset = a.end_col_offset

            break

        cur = parent

    return put_fst


def _put_one_exprish_required(self: FST, code: _PutOneCode, idx: int | None, field: str,
                              child: list[AST] | AST | None, static: onestatic, validated: int = 0,
                              target: fstloc | None = None, prefix: str = '', **options) -> FST:
    """Put a single required expression. Can be standalone or as part of sequence."""

    if not validated:
        child = _validate_put(self, code, idx, field, child)

        if not child:
            raise ValueError(f'cannot replace nonexistent {self.a.__class__.__name__}.{field}' +
                             ("" if idx is None else f"[{idx}]"))

    childf  = child.f
    ctx     = ((ctx := getattr(child, 'ctx', None)) and ctx.__class__) or Load
    put_fst = _make_exprish_fst(self, code, idx, field, static, target or childf, ctx, prefix, '', validated, **options)

    childf._set_ast(put_fst.a)

    return childf


def _put_one_exprish_optional(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                              static: onestatic, validated: int = 0, **options) -> FST | None:
    """Put new, replace or delete an optional expression."""

    if not validated:
        child = _validate_put(self, code, idx, field, child, can_del=True)

    if code is None:
        if child is None:  # delete nonexistent node, noop
            return None

    elif child:  # replace existing node
        return _put_one_exprish_required(self, code, idx, field, child, static, max(1, validated), **options)

    info = static.getinfo(self, static, idx, field)
    loc  = info.loc_insdel

    if code is None:  # delete existing node
        if not loc:
            raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field} in this state')

        self._put_src(info.delstr or None, *loc, True)
        set_field(self.a, None, field, idx)
        child.f._unmake_fst_tree()

        return None

    # put new node

    if not loc:
        raise ValueError(f'cannot create {self.a.__class__.__name__}.{field} in this state')

    put_fst = _make_exprish_fst(self, code, idx, field, static, loc, static.ctx, info.prefix, info.suffix,
                                max(1, validated), **options)
    put_fst = FST(put_fst.a, self, astfield(field, idx))

    self._make_fst_tree([put_fst])
    put_fst.pfield.set(self.a, put_fst.a)

    return put_fst


def _put_one_FunctionDef_arguments(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                                   static: onestatic, **options) -> FST:
    """Put FunctionDef.arguments. Does not have location if there are no arguments."""

    return _put_one_exprish_required(self, code or '', idx, field, child, static,
                                     target=None if (args := self.a.args.f).loc else args._loc_arguments_empty(),
                                     **options)


def _put_one_ClassDef_bases(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST, static: onestatic,
                            **options) -> FST:
    """Can't replace Starred base with non-Starred base after keywords."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if (isinstance(child, Starred) and not isinstance(code.a, Starred) and (keywords := self.a.keywords) and
        child.f.loc > keywords[0].f.loc
    ):
        raise ValueError(f'cannot replace Starred ClassDef.bases[{idx}] with non-Starred base in this state (after keywords)')

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


def _put_one_ClassDef_keywords(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST, static: onestatic,
                               **options) -> FST:
    """Don't allow put of `**keyword` before `*arg`."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if code.a.arg is None and (bases := self.a.bases) and bases[-1].f.loc > self.keywords[idx].loc:
        raise ValueError(f"cannot put '**' ClassDef.keywords[{idx}] in this state (non-keywords follow)")

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


def _put_one_AnnAssign_target(self: FST, code: _PutOneCode, idx: int | None, field: str, child: int, static: onestatic,
                              **options) -> FST:
    """Update simple according to what was put."""

    ret = _put_one_exprish_required(self, code, idx, field, child, static, **options)

    self.a.simple = 1 if isinstance(ret.a, Name) and not ret.pars().n else 0

    return ret


def _put_one_ImportFrom_names(self: FST, code: _PutOneCode, idx: int | None, field: str, child: list[AST],
                              static: onestatic, **options) -> FST:
    """Disallow put star to list of multiple names and unparenthesize if star was put to single name."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if is_star := ('*' in code.a.name):
        if len(self.a.names) != 1:
            raise NodeError('cannot put star alias to ImportFrom.names containing multiple aliases')

    ret = _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)

    if is_star:  # try to remove parentheses if there
        _, _, ln, col         = (name := self.a.names[0].f).loc
        _, _, end_ln, end_col = self.loc
        lines                 = self.root._lines

        if comma := _next_find(lines, ln, col, end_ln, end_col, ','):  # if there is a trailing comma then remove it
            ln, col = comma

            self._put_src(None, ln, col, ln, col + 1, True)

        name.unpar(shared=None)

    return ret


def _put_one_BinOp_left_right(self: FST, code: _PutOneCode, idx: int | None, field: str, child: list[AST],
                              static: onestatic, **options) -> FST:
    """Disallow invalid constant changes in patterns."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if self.parent_pattern():
        if field == 'right':
            if not isinstance(codea := code.a, Constant) or not isinstance(codea.value, complex):
                raise NodeError('can only put imaginary Constant to a pattern BinOp.right')

        else:  # field == 'left'
            if isinstance(codea := code.a, UnaryOp):
                if isinstance(codea.op, USub):
                    codea = codea.operand

            if not isinstance(codea, Constant) or not isinstance(codea.value, (int, float)):
                raise NodeError('can only put real Constant to a pattern BinOp.left')

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


def _put_one_UnaryOp_operand(self: FST, code: _PutOneCode, idx: int | None, field: str, child: list[AST],
                             static: onestatic, **options) -> FST:
    """Disallow invalid constant changes in patterns."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if self.parent_pattern():
        if not isinstance(codea := code.a, Constant):
            raise NodeError('can only put Constant to a pattern UnaryOp.operand')

        if not isinstance(codea.value, (int, float) if isinstance(self.parent.a, BinOp) else (int, float, complex)):
            raise NodeError('invalid Constant for pattern UnaryOp.operand')

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


def _put_one_with_items(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST, static: onestatic,
                        **options) -> FST:
    ret = _put_one_exprish_required(self, code, idx, field, child, static, **options)

    self._maybe_fix_with_items()

    return ret


def _put_one_Lambda_arguments(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                              static: onestatic, **options) -> FST:
    """Put Lambda.arguments. Does not have location if there are no arguments."""

    if code is None:
        code = ''

    child  = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code   = static.code_as(code, self.root.parse_params)  # and we coerce here just so we can check if is empty args being put to set the prefix correctly
    prefix = ' ' if code.loc else ''  # if arguments has .loc then it is not empty
    target = self._loc_lambda_args_entire()

    return _put_one_exprish_required(self, code, idx, field, child, static, 1, target, prefix, **options)


def _put_one_Compare_combined(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                              static: onestatic, **options) -> FST:
    """Put to combined [Compare.left, Compare.comparators] using this total indexing."""

    idx, field, child = _params_Compare_combined(self, idx)

    return _put_one_exprish_required(self, code, idx, field, child, static, **options)


def _put_one_Call_args(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST, static: onestatic,
                       **options) -> FST:
    """Can't replace Starred arg with non-Starred arg after keywords."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if (isinstance(child, Starred) and not isinstance(code.a, Starred) and (keywords := self.a.keywords) and
        child.f.loc > keywords[0].f.loc
    ):
        raise ValueError(f'cannot replace Starred Call.args[{idx}] with non-Starred arg in this state (after keywords)')

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


def _put_one_Call_keywords(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST, static: onestatic,
                           **options) -> FST:
    """Don't allow put of `**keyword` before `*arg`."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if code.a.arg is None and (args := self.a.args) and args[-1].f.loc > self.keywords[idx].loc:
        raise ValueError(f"cannot put '**' Call.keywords[{idx}] in this state (non-keywords follow)")

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


def _put_one_Attribute_value(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                             static: onestatic, **options) -> FST:
    """If this gets parenthesized in an `AnnAssign` then the whole `AnnAssign` target needs to be parenthesized. Also
    need to make sure only unparenthesized `Name` or `Attribute` is put to one of these in `pattern` expression."""

    child     = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code      = static.code_as(code, self.root.parse_params)
    is_annass = False
    above     = child.f

    while (parent := above.parent) and (pfname := above.pfield.name) in ('value', 'target', 'keys', 'cls'):
        if isinstance(parenta := parent.a, AnnAssign):
            is_annass = pfname == 'target'

            break

        if isinstance(parenta, pattern):
            if code.end_ln != code.ln and not above.is_enclosed_in_parents():
                raise NodeError(f'cannot put multiline {above.a.__class__.__name__} to uneclosed pattern expression')

            _validate_pattern_expr(code)

            break

        if not isinstance(parenta, (Attribute, Subscript)):  # we need to walk up both of these for the AnnAssign, won't be Subscripts in a MatchMapping.keys
            break

        above = parent

    ret = _put_one_exprish_required(self, code, idx, field, child, static, validated=2, **options)

    if is_annass and not above.pars().n:
        if _maybe_par_above(above, ret):
            parenta.simple = 0

    return ret


def _put_one_Subscript_value(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                             static: onestatic, **options) -> FST:
    """If this gets parenthesized in an AnnAssign then the whole AnnAssign target needs to be parenthesized."""

    ret   = _put_one_exprish_required(self, code, idx, field, child, static, **options)
    above = ret

    while (parent := above.parent) and above.pfield.name in ('value', 'target'):
        if isinstance(parenta := parent.a, AnnAssign):
            if not above.pars().n:
                _maybe_par_above(above, ret)

            break

        if not isinstance(parenta, (Attribute, Subscript)):
            break

        above = parent

    return ret


def _put_one_Subscript_slice(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,  # py < 3.11
                             static: onestatic, **options) -> FST:
    """Don't allow put unparenthesized tuple containing Starred."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if code.is_parenthesized_tuple() is False and any(isinstance(a, Starred) for a in code.a.elts):
        raise NodeError('cannot have unparenthesized tuple containing Starred in slice')

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)

if not _PYLT11:
    _put_one_Subscript_slice = _put_one_exprish_required


def _put_one_List_elts(self: FST, code: _PutOneCode, idx: int | None, field: str, child: list[AST],
                       static: onestatic, **options) -> FST:
    """Disallow non-targetable expressions in targets."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if not isinstance(self.a.ctx, Load):  # only allow possible expression targets into an expression target
        if not hasattr(code.a, 'ctx'):
            raise ValueError(f"cannot put non-targetable expression to List.elts[{idx}] "
                             "in this state (target expression)")

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


def _put_one_Tuple_elts(self: FST, code: _PutOneCode, idx: int | None, field: str, child: list[AST],
                        static: onestatic, **options) -> FST:
    """Disallow non-targetable expressions in targets. If not an unparenthesized top level or slice tuple then disallow
    Slices."""

    ast   = self.a
    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if ((pf := self.pfield) and pf.name != 'slice') or self._is_parenthesized_seq():
        static = _onestatic_expr_required_starred  # default static allows slices

    if not isinstance(ast.ctx, Load):  # only allow possible expression targets into an expression target
        if not hasattr(code.a, 'ctx'):
            raise ValueError(f"cannot put non-targetable expression to Tuple.elts[{idx}] "
                             "in this state (target expression)")

    if _PYLT11:
        if isinstance(code.a, Starred) and pf == ('slice', None):
            raise NodeError('cannot put Starred to a slice Tuple.elts')

    is_starred_in_slice = (len(elts := ast.elts) == 1 and isinstance(elts[0], Starred) and
                           (pf := self.pfield) and pf.name == 'slice')  # because of replacing the Starred in 'a[*i_am_really_a_tuple]'

    ret = _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)

    if is_starred_in_slice:
        self._maybe_add_singleton_tuple_comma()

    return ret


def _put_one_Dict_keys(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                       static: onestatic, **options) -> FST:
    """Put optional dict key and if deleted parenthesize the value if needed."""

    ret = _put_one_exprish_optional(self, code, idx, field, child, static, **options)

    if (code is None and not (value := (a := self.a).values[idx].f).is_atom() and
        precedence_require_parens(value.a, a, 'values',  idx)
    ):
        value._parenthesize_grouping()

    return ret


def _put_one_arg(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST, static: onestatic, **options,
                 ) -> FST:
    """Don't allow arg with Starred annotation into non-vararg args."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if isinstance(code.a.annotation, Starred):
        raise NodeError(f'cannot put arg with Starred annotation to {self.a.__class__.__name__}.{field}')

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


def _put_one_arg_annotation(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,  # py >= 3.11
                            static: onestatic, **options) -> FST:
    """Allow Starred in vararg arg annotation in py 3.11+."""

    if not self.parent or self.pfield.name == 'vararg':
        static = onestatic(_one_info_arg_annotation, _restrict_fmtval_slice)

    return _put_one_exprish_optional(self, code, idx, field, child, static, **options)

if _PYLT11:
    _put_one_arg_annotation = _put_one_exprish_optional  # this leaves the _restrict_default in the static which disallows Starred


def _put_one_withitem_context_expr(self: FST, code: _PutOneCode, idx: int | None, field: str, child: str,
                                   static: onestatic, **options) -> str:
    """If put a single context_expr `Tuple` with no optional_vars then need to add grouping parentheses if not present
    otherwise the tuple will be reparsed as multiple `withitems` instead of a single `Tuple`."""

    ret = _put_one_exprish_optional(self, code, idx, field, child, static, **options)

    if (parent := self.parent) and isinstance(parent.a, (With, AsyncWith)):
        parent._maybe_fix_with_items()

    return ret


def _put_one_withitem_optional_vars(self: FST, code: _PutOneCode, idx: int | None, field: str, child: str,
                                    static: onestatic, **options) -> str:
    """If delete leaves a single parenthesized context_expr `Tuple` then need to parenthesize that, otherwise it can be
    reparsed as multiple `withitems` instead of a single `Tuple`."""

    ret = _put_one_exprish_optional(self, code, idx, field, child, static, **options)

    if (parent := self.parent) and isinstance(parent.a, (With, AsyncWith)):
        parent._maybe_fix_with_items()

    return ret


def _put_one_MatchValue_value(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                              static: onestatic, **options) -> FST:
    """Put MatchValue.value. Need to do this because a standalone MatchValue does not encompass parenthesized value
    parentheses."""

    ret              = _put_one_exprish_required(self, code, idx, field, child, static, **options)
    a                = self.a
    v                = a.value
    a.lineno         = v.lineno
    a.col_offset     = v.col_offset
    a.end_lineno     = v.end_lineno
    a.end_col_offset = v.end_col_offset

    return ret


def _put_one_MatchAs_pattern(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                             static: onestatic, **options) -> FST:
    """Enclose unenclosed MatchSequences being put here, if any."""

    child = _validate_put(self, code, idx, field, child, can_del=True)  # we want to do it in same order as all other puts

    if code is not None:
        code = static.code_as(code, self.root.parse_params)

        if isinstance(code.a, MatchStar):
            raise NodeError(f'cannot put a MatchStar to MatchAs.pattern')

        if code.is_enclosed_matchseq() is False:
            code._parenthesize_node(pars='[]')

    return _put_one_exprish_optional(self, code, idx, field, child, static, 2, **options)


def _put_one_pattern(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST, static: onestatic,
                      **options) -> FST:
    """Enclose unenclosed MatchSequences being put here."""

    child = _validate_put(self, code, idx, field, child)  # we want to do it in same order as all other puts
    code  = static.code_as(code, self.root.parse_params)

    if isinstance(code.a, MatchStar):
        if not isinstance(self.a, MatchSequence):
            raise NodeError(f'cannot put a MatchStar to {self.a.__class__.__name__}.{field}')

    elif code.is_enclosed_matchseq() is False:
        code._parenthesize_node(pars='[]')

    return _put_one_exprish_required(self, code, idx, field, child, static, 2, **options)


# ......................................................................................................................
# identifier

def _put_one_identifier_required(self: FST, code: _PutOneCode, idx: int | None, field: str, child: str,
                                 static: onestatic, **options) -> str:
    """Put a single required identifier."""

    _validate_put(self, code, idx, field, child)

    code = static.code_as(code, self.root.parse_params)
    info = static.getinfo(self, static, idx, field)

    self._put_src(code, *info.loc_ident, True)
    set_field(self.a, code, field, idx)

    return code


def _put_one_identifier_optional(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST,
                                 static: onestatic, **options) -> _PutOneCode:
    """Put new, replace or delete an optional identifier."""

    child = _validate_put(self, code, idx, field, child, can_del=True)

    if code is None and child is None:  # delete nonexistent identifier, noop
        return None

    info = static.getinfo(self, static, idx, field)
    loc  = info.loc_insdel

    if code is None:  # delete existing identifier
        if not loc:
            raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field} in this state')

        self._put_src(info.delstr or None, *loc, True)
        set_field(self.a, None, field, idx)

        return None

    code = static.code_as(code, self.root.parse_params)

    if child is not None:  # replace existing identifier
        self._put_src(code, *info.loc_ident, True)
        set_field(self.a, code, field, idx)

    else: # put new identifier
        if not loc:
            raise ValueError(f'cannot create {self.a.__class__.__name__}.{field} in this state')

        params_offset = self._put_src(info.prefix + code + info.suffix, *loc, True, exclude=self)

        self._offset(*params_offset, self_=False)
        set_field(self.a, code, field, idx)

    return code


def _put_one_ExceptHandler_name(self: FST, code: _PutOneCode, idx: int | None, field: str, child: str,
                                static: onestatic, **options) -> str:
    """If adding a name to an ExceptHandler with tuple of exceptions then make sure it is parenthesized."""

    ret = _put_one_identifier_optional(self, code, idx, field, child, static, **options)

    if ret and (typef := self.a.type.f).is_parenthesized_tuple() is False:
        typef._parenthesize_node()

    return ret


def _put_one_keyword_arg(self: FST, code: _PutOneCode, idx: int | None, field: str, child: str,
                         static: onestatic, **options) -> str:
    """Don't allow delete keyword.arg if non-keywords follow."""

    if code is None and (parent := self.parent):
        if isinstance(parenta := parent.a, Call):
            if (args := parenta.args) and args[-1].f.loc > self.loc:
                raise ValueError(f'cannot delete Call.keywords[{self.pfield.idx}].arg in this state (non-keywords follow)')

        elif isinstance(parenta, ClassDef):
            if (bases := parenta.bases) and bases[-1].f.loc > self.loc:
                raise ValueError(f'cannot delete ClassDef.keywords[{self.pfield.idx}].arg in this state (non-keywords follow)')

    return _put_one_identifier_optional(self, code, idx, field, child, static, **options)


def _put_one_MatchStar_name(self: FST, code: _PutOneCode, idx: int | None, field: str, child: str, static: onestatic,
                            **options) -> str:
    """Slightly annoying MatchStar.name. '_' really means delete."""

    if code is None:
        code = '_'

    ret = _put_one_identifier_required(self, code, idx, field, child, static, **options)

    if self.a.name == '_':
        self.a.name = None

    return ret


def _put_one_MatchAs_name(self: FST, code: _PutOneCode, idx: int | None, field: str, child: str, static: onestatic,
                          **options) -> str:
    """Very annoying MatchAs.name. '_' really means delete, which can't be done if there is a pattern, and can't be
    assigned to a pattern."""

    if code is None:
        code = '_'
    else:
        code = _code_as_identifier(code, self.root.parse_params)

    if self.a.pattern and code == '_':
        raise ValueError("cannot change MatchAs with pattern into wildcard '_'")

    ret = _put_one_identifier_required(self, code, idx, field, child, static, **options)

    if self.a.name == '_':
        self.a.name = None

    return ret


# ......................................................................................................................

def _put_one_raw(self: FST, code: _PutOneCode, idx: int | None, field: str, child: AST | list[AST],
                 static: onestatic | None, **options) -> FST | None:

    ast = self.a
    to  = options.get('to')

    if not field:  # special case field
        if (is_dict := (cls := ast.__class__) is Dict) or cls is MatchMapping:
            static = _PUT_ONE_HANDLERS[(cls, 'keys')][-1]
            child  = ast.keys
            field  = 'keys'
            idx    = _fixup_one_index(len(child), idx)

            if not to:
                to = self.values[idx] if is_dict else self.patterns[idx]

        elif cls is Compare:
            idx, field, child = _params_Compare_combined(self, idx)
        else:
            raise ValueError(f'cannot put single element to combined field of {ast.__class__.__name__}')

    child  = _validate_put(self, code, idx, field, child, can_del=True)
    childf = child.f if isinstance(child, AST) else None
    pars   = bool(FST.get_option('pars', options))

    if to is childf:
        to = None

    # code to appropriate lines

    if is_del := code is None:
        code     = ''
        is_empty = False

    else:
        if isinstance(code, str):
            code = code.split('\n')
        elif isinstance(code, AST):
            code = FST._unparse(code).split('\n')

        elif isinstance(code, FST):
            if not code.is_root:
                raise ValueError('expecting root node')

            code = code._lines

        is_empty = not _next_src(code, 0, 0, len(code) - 1, 0x7fffffffffffffff)  # if only comments and line continuations then is functionally empty

    is_del_or_empty = is_del or is_empty

    # from location, prefix and maybe suffix and delstr

    info = static and (getinfo := static.getinfo) and getinfo(self, static, idx, field)
    loc  = None

    if info:
        if is_del_or_empty:
            loc = info.loc_insdel or info.loc_ident

            if is_del and info.delstr and not to:  # pure delete, plop in the delstr just to be nice :)
                code = info.delstr

        else:
            loc = info.loc_ident

            if child is None:  # pure insert, add the prefix, also the suffix if there is no 'to'
                if info.prefix:
                    code[0] = info.prefix + code[0]
                if info.suffix and not to:
                    code[-1] = code[-1] + info.suffix

            elif field == 'conversion':  # another special case because f-string conversion may be implicit due to '=', the prefix is put conditionally in this case in the info() function
                code[0] = info.prefix + code[0]

    if loc is None:
        if childf:
            if isinstance(child, arguments):  # empty arguments do not have a location and lambda args need to add or remove a preceding space
                if not (loc := childf.loc):
                    loc = childf._loc_arguments_empty()

                    if not is_del_or_empty and isinstance(ast, Lambda):  # adding to nonexistent lambda pars, need to add space prefix
                        code[0] = ' ' + code[0]

                elif is_del_or_empty and isinstance(ast, Lambda):  # deleting existing lambda pars, need to eat space prefix
                    loc = self._loc_lambda_args_entire()

            else:
                loc = childf.pars(False) if pars else childf.bloc

                if (loc and not pars and childf.is_solo_call_arg_genexp() and  # if loc includes `arguments` parentheses shared with solo GeneratorExp call arg then need to leave those in place
                    (non_shared_loc := childf.pars(False)) > loc
                ):
                    loc = non_shared_loc

        if loc is None and info and not is_del_or_empty:  # identifier
            loc = info.loc_insdel

    if not loc:
        raise ValueError('cannot determine location to put to')

    # to location (if different) and appropriate parent

    if not to:
        parent = self
        to_loc = loc

    else:
        if not (to_parent := to.parent):
            raise ValueError("'to' node cannot be root")

        if (root := self.root) is not to.root:
            raise ValueError("'to' must be part of same tree")

        to_loc = None

        if is_del_or_empty:  # if deleting then see if there is a prescribed delete location
            to_field, to_idx = to.pfield
            to_static        = _PUT_ONE_HANDLERS.get((to_parent.a.__class__, to_field), (None,))[-1]

            if to_static and (to_info := (getinfo := to_static.getinfo) and getinfo(self, to_static, to_idx, to_field)):
                to_loc = to_info.loc_insdel

        if to_loc is None:  # empty arguments get special handling
            if not (to_loc := to.pars(False) if pars else to.bloc):
                if isinstance(to.a, arguments):
                    to_loc = to._loc_arguments_empty()
                else:
                    raise ValueError(f"'to' node must have a location")

            if not pars and to.is_solo_call_arg_genexp() and (non_shared_loc := to.pars(False)) > to_loc:
                to_loc = non_shared_loc

        if to_loc[:2] < loc[:2]:
            raise ValueError(f"'to' node must follow self")

        self_path = root.child_path(self)  # technically should be root.child_path(childf)[:-1] but child may be identifier so get path directly to self which is parent and doesn't need the [:-1]
        to_path   = root.child_path(to)[:-1]
        path      = list(p for p, _ in takewhile(lambda st: st[0] == st[1], zip(self_path, to_path)))
        parent    = root.child_from_path(path)

    # do it

    return parent._reparse_raw(code, loc.ln, loc.col, to_loc.end_ln, to_loc.end_col)


def _put_one(self: FST, code: _PutOneCode, idx: int | None, field: str, **options) -> FST | None:  # -> Self or reparsed Self or could disappear due to raw
    """Put new, replace or delete a node (or limited non-node) to a field of `self`.

    **Parameters:**
    - `code`: The code to put in the form of an `FST`, an `AST`, a string of source or a list of lines of source. If
        is `None` then will attempt to remove optional field or delete node from a mutable body list of nodes using
        slice operations.
    - `idx`: The index in the body list of the field to put, or `None` if is a standalone node.
    - `field`: The `AST` field to modify.
    - `options`: See `FST.get_options`.
    """

    if code is self.root:  # don't allow own root to be put to self
        raise NodeError('circular put detected')

    ast   = self.a
    child = getattr(self.a, field) if field else None
    raw   = FST.get_option('raw', options)
    to    = options.get('to')

    sliceable, handler, static = _PUT_ONE_HANDLERS.get((ast.__class__, field), (False, None, None))

    if sliceable and (not handler or code is None) and not to:  # if deleting from a sliceable field without a 'to' parameter then delegate to slice operation, also all statementishs and combined mapping fields
        idx      = _fixup_one_index(len(child if field else ast.keys), idx)  # field will be '' only for Dict and MatchMapping which both have keys, Compare is not considered sliceable for single element deletions
        new_self = self._put_slice(code, idx, idx + 1, field, True, **options)

        return None if code is None or not field else getattr(new_self.a, field)[idx].f  # guaranteed to be there if code is not None because was just replacement

    if raw is not True:
        try:
            if to:
                raise NodeError(f"cannot put with 'to' to {self.a.__class__.__name__}"
                                f"{f'.{field}' if field else ''} without 'raw'")

            if not handler:
                raise NodeError(f"cannot {'delete' if code is None else 'replace'} {ast.__class__.__name__}"
                                f"{f'.{field}' if field else ' combined fields'}")

            else:
                if _PYLT12:  # don't allow modification if inside an f-string because before 3.12 they were very fragile
                    f = child.f if isinstance(child, AST) else self

                    while not isinstance(a := f.a, (stmt, pattern, match_case, ExceptHandler)):
                        if isinstance(a, JoinedStr):
                            raise NodeError('put inside JoinedStr not implemented on python < 3.12')

                        if not (f := f.parent):
                            break

                with self._modifying(field):
                    ret = handler(self, code, idx, field, child, static, **options)

                return ret

        except (NodeError, SyntaxError, NotImplementedError):
            if not raw:
                raise

    with self._modifying(field, True):
        return _put_one_raw(self, code, idx, field, child, static, **options)


# ......................................................................................................................
# field info

_restrict_default        = [FormattedValue, Interpolation, Slice, Starred]
_restrict_fmtval_slice   = [FormattedValue, Interpolation, Slice]
_restrict_fmtval_starred = [FormattedValue, Interpolation, Starred]
_restrict_fmtval         = [FormattedValue, Interpolation]
_oneinfo_default         = oneinfo()

def _one_info_constant(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:  # only Constant and MatchSingleton
    return oneinfo('', None, self.loc)

def _one_info_exprish_required(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _oneinfo_default

_onestatic_expr_required             = onestatic(_one_info_exprish_required, _restrict_default)
_onestatic_expr_required_starred     = onestatic(_one_info_exprish_required, _restrict_fmtval_slice)
_onestatic_comprehension_required    = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_comprehension)
_onestatic_arguments_required        = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_arguments)
_onestatic_arguments_lambda_required = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_arguments_lambda)
_onestatic_arg_required              = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_arg)
_onestatic_keyword_required          = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_keyword)
_onestatic_withitem_required         = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_withitem)
_onestatic_pattern_required          = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_pattern)
_onestatic_type_param_required       = onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_type_param)
_onestatic_target_Name               = onestatic(_one_info_exprish_required, Name, ctx=Store)
_onestatic_target_single             = onestatic(_one_info_exprish_required, (Name, Attribute, Subscript), ctx=Store)
_onestatic_target                    = onestatic(_one_info_exprish_required, (Name, Attribute, Subscript, Tuple, List), ctx=Store)
_onestatic_ctx                       = onestatic(None, expr_context)

def _one_info_identifier_required(self: FST, static: onestatic, idx: int | None, field: str,  # required, cannot delete or put new
                                  prefix: str | None = None) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    lines                    = self.root._lines

    if not prefix:
        end_col = re_identifier.match(lines[ln], col, end_col if end_ln == ln else 0x7fffffffffffffff).end()  # must be there

    else:
        ln, col      = _next_find(lines, ln, col, end_ln, end_col, prefix, lcont=None)  # must be there, have to search because could be preceded by something (like 'async')
        ln, col, src =  _next_find_re(lines, ln, col + len(prefix), end_ln, end_col, re_identifier, lcont=None)  # must be there
        end_col      = col + len(src)

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

_onestatic_identifier_required = onestatic(_one_info_identifier_required, _restrict_default, code_as=_code_as_identifier)

def _one_info_identifier_alias(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:  # required, cannot delete or put new
    ln, col, end_ln, end_col = self.loc
    end_col                  = re_identifier_alias.match(self.root._lines[ln], col,
                                                         end_col if end_ln == ln else 0x7fffffffffffffff).end()  # must be there

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

def _one_info_FunctionDef_name(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, 'def')

_onestatic_FunctionDef_name = onestatic(_one_info_FunctionDef_name, _restrict_default, code_as=_code_as_identifier)

def _one_info_FunctionDef_returns(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self._loc_block_header_end(True)
    ret_end_ln               = end_ln
    ret_end_col              = end_col - 1

    if returns := self.a.returns:
        ln, col               = prev.loc[2:] if (prev := (retf := returns.f).prev()) else self.loc[:2]
        end_ln, end_col, _, _ = retf.pars()

    args_end_ln, args_end_col = _prev_find(self.root._lines, ln, col, end_ln, end_col, ')')  # must be there

    return oneinfo(' -> ', fstloc(args_end_ln, args_end_col + 1, ret_end_ln, ret_end_col))

_onestatic_FunctionDef_returns = onestatic(_one_info_FunctionDef_returns, _restrict_default)

def _one_info_ClassDef_name(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, 'class')

def _one_info_Return_value(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' ', fstloc((loc := self.loc).ln, loc.col + 6, loc.end_ln, loc.end_col))

def _one_info_AnnAssign_value(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' = ', fstloc((loc := self.a.annotation.f.pars()).end_ln, loc.end_col, self.end_ln, self.end_col))

def _one_info_Raise_exc(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if self.a.cause:
        return _oneinfo_default  # can not del (and exists, so can't put new)

    ln, col, end_ln, end_col = self.loc

    return oneinfo(' ', fstloc(ln, col + 5, end_ln, end_col))

def _one_info_Raise_cause(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if not (exc := self.a.exc):
        return _oneinfo_default  # can not put (or del because cause doesn't exist)

    _, _, ln, col = exc.f.pars()

    return oneinfo(' from ', fstloc(ln, col, self.end_ln, self.end_col))

def _one_info_Assert_msg(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(', ', fstloc((loc := self.a.test.f.pars()).end_ln, loc.end_col, self.end_ln, self.end_col))

def _one_info_ImportFrom_module(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    lines                    = self.root._lines

    if not self.a.level:  # cannot insert or delete
        ln, col, src =  _next_find_re(lines, ln, col + 4, end_ln, end_col, re_identifier_dotted, lcont=None)  # must be there, col+4 is for 'from'
        end_col      = col + len(src)

        return oneinfo('', None, fstloc(ln, col, ln, end_col))

    self_ln, self_col, _, _ = self.loc
    ln, col                 = _prev_find(self.root._lines, self_ln, self_col, *self.a.names[0].f.loc[:2], 'import')
    ln, col, src            = _prev_src(self.root._lines, self_ln, self_col, ln, col)  # must be there, the module name with any/some/all preceding '.' level indicators
    end_col                 = col + len(src)
    col                     = end_col - len(src.lstrip('.'))

    return oneinfo('', loc := fstloc(ln, col, ln, end_col), loc)

def _one_info_Global_Nonlocal_names(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:

    idx = _fixup_one_index(len(self.a.names), idx)

    return oneinfo('', None, self._loc_Global_Nonlocal_names(idx))

_onestatic_Global_Nonlocal_names = onestatic(_one_info_Global_Nonlocal_names, _restrict_default, code_as=_code_as_identifier)

def _one_info_Dict_key(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    key                   = (a := self.a).keys[idx]
    value                 = a.values[idx].f
    end_ln, end_col, _, _ = value.pars()
    ln, col, _, _         = self._dict_key_or_mock_loc(key, value) if key is None else key.f.pars()

    return oneinfo('', fstloc(ln, col, end_ln, end_col), None, ': ', '**')

def _one_info_Yield_value(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' ', fstloc((loc := self.loc).ln, loc.col + 5, loc.end_ln, loc.end_col))

def _one_info_Attribute_attr(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col         = self.a.value.f.loc
    _, _, end_ln, end_col = self.loc
    lines                 = self.root._lines
    ln, col               = _next_find(lines, ln, col, end_ln, end_col, '.')  # must be there
    ln, col, src          = _next_src(lines, ln, col + 1, end_ln, end_col)  # must be there

    return oneinfo('', None, fstloc(ln, col, ln, col + len(src)))

def _one_info_Slice_lower(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc

    if lower := self.a.lower:
        end_ln, end_col = _next_find(self.root._lines, (loc := lower.f.loc).end_ln, loc.end_col, end_ln, end_col, ':')  # must be there
    else:
        end_ln, end_col = _next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # must be there

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

_onestatic_Slice_lower = onestatic(_one_info_Slice_lower, _restrict_default)

def _one_info_Slice_upper(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln                    = (lloc := _one_info_Slice_lower(self, _onestatic_Slice_lower, idx, field).loc_insdel).end_ln
    col                   = lloc.end_col + 1
    _, _, end_ln, end_col = self.loc

    if upper := self.a.upper:
        end = _next_find(self.root._lines, (loc := upper.f.loc).end_ln, loc.end_col, end_ln, end_col, ':')  # may or may not be there
    else:
        end = _next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # may or may not be there

    if end:
        end_ln, end_col = end

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

_onestatic_Slice_upper = onestatic(_one_info_Slice_upper, _restrict_default)

def _one_info_Slice_step(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln  = (uloc := _one_info_Slice_upper(self, _onestatic_Slice_upper, idx, field).loc_insdel).end_ln
    col = uloc.end_col

    if self.root._lines[ln].startswith(':', col):
        col    += 1
        prefix  = ''
    else:
        prefix = ':'

    return oneinfo(prefix, fstloc(ln, col, self.end_ln, self.end_col))

_onestatic_Slice_step = onestatic(_one_info_Slice_step, _restrict_default)

def _one_info_ExceptHandler_type(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if (a := self.a).name:
        return _oneinfo_default  # can not del (and exists, so can't put new)

    if type_ := a.type:
        _, _, end_ln, end_col = type_.f.pars()
    else:
        end_ln, end_col  = self._loc_block_header_end()  # because 'name' can not be there
        end_col         -= 1

    ln, col, _, _ = self.loc
    col           = col + 6  # 'except'

    if star := _next_src(self.root._lines, ln, col, end_ln, end_col):  # 'except*'?
        if star.src.startswith('*'):
            return _oneinfo_default  # can not del type from except* and can not insert because can never not exist

    return oneinfo(' ', fstloc(ln, col, end_ln, end_col))

def _one_info_ExceptHandler_name(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if not (type_ := (a := self.a).type):
        return _oneinfo_default  # can not put new and does not exist

    _, _, ln, col   = type_.f.pars()
    end_ln, end_col = self._loc_block_header_end()
    loc_insdel      = fstloc(ln, col, end_ln, end_col - 1)

    if (name := a.name) is None:
        loc_ident = None

    else:
        lines     = self.root._lines
        ln, col   = _next_find(lines, ln, col, end_ln, end_col, 'as')  # skip the 'as'
        ln, col   = _next_find(lines, ln, col + 2, end_ln, end_col, name)  # must be there
        loc_ident = fstloc(ln, col, ln, col + len(name))

    return oneinfo(' as ', loc_insdel, loc_ident)

def _one_info_arguments_vararg(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if vararg := (a := self.a).vararg:  # delete location
        if next := (varargf := vararg.f).next():
            _, _, end_ln, end_col = varargf.pars()
        else:
            _, _, end_ln, end_col = self.loc  # there may be a trailing comma

        if prev := varargf.prev():
            delstr = ', *' if a.kwonlyargs else ''

            if not (a.posonlyargs and ((field := prev.pfield.name) == 'posonlyargs' or
                (field == 'defaults' and prev.prev().pfield.name == 'posonlyargs'))
            ):
                _, _, ln, col = prev.pars()

                return oneinfo('', fstloc(ln, col, end_ln, end_col), delstr=delstr)

            ln, col = _next_find(self.root._lines, prev.end_ln, prev.end_col, end_ln, end_col, '/')  # must be there

            return oneinfo('', fstloc(ln, col + 1, end_ln, end_col), delstr=delstr)

        if next:
            if a.kwonlyargs and next.pfield.name == 'kwonlyargs':
                next_ln, next_col, _, _ = next.pars()

                return oneinfo('', fstloc(self.ln, self.col, next_ln, next_col), delstr='*, ')

            end_ln, end_col = _next_find(self.root._lines, end_ln, end_col, next.ln, next.col, '**')  # must be there

            return oneinfo('', fstloc(self.ln, self.col, end_ln, end_col))

        if not (parent := self.parent) or not isinstance(parent.a, Lambda):
            return oneinfo('', self.loc)

        ln, col, _, _ = parent.loc

        return oneinfo('', fstloc(ln, col + 6, end_ln, end_col))

    # insert location

    if kwonlyargs := a.kwonlyargs:
        end_ln, end_col, _, _ = (kwonlyarg := kwonlyargs[0].f).loc

        if prev := kwonlyarg.prev():
            _, _, ln, col = prev.loc
        else:
            ln, col, _, _ = self.loc

        ln, col = _next_find(self.root._lines, ln, col, end_ln, end_col, '*')  # must be there

        return oneinfo('', fstloc(ln, (col := col + 1), ln, col))

    if kwarg := a.kwarg:
        end_ln, end_col, _, _ = (kwargf := kwarg.f).loc

        if prev := kwargf.prev():
            _, _, ln, col = prev.loc
        else:
            ln, col, _, _ = self.loc

        ln, col = _next_find(self.root._lines, ln, col, end_ln, end_col, '**')  # must be there

        return oneinfo('*', fstloc(ln, col, ln, col), None, ', ')

    if a.args:
        _, _, ln, col = self.last_child().pars()

        return oneinfo(', *', fstloc(ln, col, ln, col))

    if a.posonlyargs:
        _, _, ln, col = self.last_child().loc

        ln, col = _next_find(self.root._lines, ln, col, self.end_ln, self.end_col, '/')  # must be there

        return oneinfo(', *', fstloc(ln, (col := col + 1), ln, col))

    loc    = self._loc_arguments_empty()
    prefix = ' *' if (parent := self.parent) and isinstance(parent.a, Lambda) else '*'

    return oneinfo(prefix, loc)

def _one_info_arguments_kw_defaults(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if ann := (arg := self.a.kwonlyargs[idx]).annotation:
        _, _, ln, col = ann.f.pars()
        prefix        = ' = '

    else:
        ln     = (loc := arg.f.loc).ln
        col    = loc.col + len(arg.arg)
        prefix = '='

    if default := self.a.kw_defaults[idx]:
        _, _, end_ln, end_col = default.f.pars()

    else:
        end_ln  = ln
        end_col = col

    return oneinfo(prefix, fstloc(ln, col, end_ln, end_col))

def _one_info_arguments_kwarg(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if kwarg := (a := self.a).kwarg:  # delete location
        if not (prev := (kwargf := kwarg.f).prev()):
            if not (parent := self.parent) or not isinstance(parent.a, Lambda):
                return oneinfo('', self.loc)

            ln, col, _, _ = parent.loc

            return oneinfo('', fstloc(ln, col + 6, self.end_ln, self.end_col))

        if not (a.posonlyargs and ((field := prev.pfield.name) == 'posonlyargs' or
            (field == 'defaults' and prev.prev().pfield.name == 'posonlyargs'))
        ):
            _, _, ln, col = prev.pars()

        else:
            ln, col  = _next_find(self.root._lines, prev.end_ln, prev.end_col, kwargf.ln, kwargf.col, '/')  # must be there
            col     += 1

        return oneinfo('', fstloc(ln, col, self.end_ln, self.end_col))

    # insert location

    if not (loc := self.loc):
        loc    = self._loc_arguments_empty()
        prefix = ' **' if (parent := self.parent) and isinstance(parent.a, Lambda) else '**'

        return oneinfo(prefix, loc)

    _, _, end_ln, end_col = loc

    last = self.last_child()

    if not (a.posonlyargs and ((field := last.pfield.name) == 'posonlyargs' or
        (field == 'defaults' and last.prev().pfield.name == 'posonlyargs'))
    ):
        _, _, ln, col = last.pars()

    else:
        ln, col  = _next_find(self.root._lines, last.end_ln, last.end_col, end_ln, end_col, '/')  # must be there
        col     += 1

    return oneinfo(', **', fstloc(ln, col, end_ln, end_col))

def _one_info_arg_annotation(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(': ', fstloc((loc := self.loc).ln, loc.col + len(self.a.arg), self.end_ln, self.end_col))

def _one_info_keyword_arg(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    end_ln, end_col, _, _ = (a := self.a).value.f.pars()
    ln, col, _, _         = self.loc
    arg_end_col           = col + 2 if a.arg is None else re_identifier.match(self.root._lines[ln], col).end() # must be there

    return oneinfo('', fstloc(ln, col, end_ln, end_col), fstloc(ln, col, ln, arg_end_col), '=', '**')

def _one_info_alias_asname(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col  = self.loc
    loc_insdel                = fstloc(ln, col + len((a := self.a).name), end_ln, end_col)

    if (asname := a.asname) is None:
        loc_ident = None

    else:
        lines     = self.root._lines
        ln, col   = _next_find(lines, ln, col, end_ln, end_col, 'as')  # skip the 'as'
        ln, col   = _next_find(lines, ln, col + 2, end_ln, end_col, asname)  # must be there
        loc_ident = fstloc(ln, col, ln, col + len(asname))

    return oneinfo(' as ', loc_insdel, loc_ident)

def _one_info_withitem_optional_vars(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col = self.a.context_expr.f.pars()

    if optional_vars := self.a.optional_vars:
        _, _, end_ln, end_col = optional_vars.f.pars()
    else:
        end_ln  = ln
        end_col = col

    return oneinfo(' as ', fstloc(ln, col, end_ln, end_col))

def _one_info_match_case_guard(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col          = self.a.pattern.f.pars()
    _, _, end_ln, end_col  = self._loc_block_header_end(True)
    end_col               -= 1

    return oneinfo(' if ', fstloc(ln, col, end_ln, end_col))

def _one_info_MatchMapping_rest(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col  = self.loc
    end_col                  -= 1

    if patterns := (a := self.a).patterns:
        _, _, ln, col = patterns[-1].f.pars()
        prefix        = ', **'

    else:
        col    += 1
        prefix  = '**'

    if (rest := a.rest) is None:
        loc_ident = None
    else:
        rest_ln, rest_col = _next_find(self.root._lines, ln, col, end_ln, end_col, rest)
        loc_ident         = fstloc(rest_ln, rest_col, rest_ln, rest_col + len(rest))

    return oneinfo(prefix, fstloc(ln, col, end_ln, end_col), loc_ident)

def _one_info_MatchClass_kwd_attrs(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast          = self.a
    lines        = self.root._lines
    kwd_patterns = ast.kwd_patterns

    if idx % len(kwd_patterns):  # could be negative
        _, _, ln, col = kwd_patterns[idx - 1].f.loc
    elif patterns := ast.patterns:
        _, _, ln, col = patterns[-1].f.loc
    else:
        _, _, ln, col = ast.cls.f.loc

    end_ln, end_col = _prev_find(lines, ln, col, *kwd_patterns[idx].f.loc[:2], '=')  # must be there
    ln, col, src    = _prev_src(lines, ln, col, end_ln, end_col)  # must be there
    end_col         = col + len(src)
    col             = end_col - len(src.lstrip('(,'))

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

def _one_info_MatchStar_name(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '*')

def _one_info_MatchAs_pattern(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if (name := (a := self.a).name) is None:
        return _oneinfo_default  # cannot insert or delete because is wildcard '_'

    ln, col, end_ln, end_col = self.loc

    if (pattern := a.pattern) is None:
        return oneinfo('', fstloc(ln, col, ln, col), None, ' as ')

    lines           = self.root._lines
    as_ln, as_col   = _next_find(lines, *pattern.f.pars()[2:], end_ln, end_col, 'as')  # skip the 'as'
    end_ln, end_col = _next_find(lines, as_ln, as_col + 2, end_ln, end_col, name)

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

def _one_info_MatchAs_name(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc

    if (pattern := (a := self.a).pattern) is None:
        prefix  = ''

    else:
        prefix  = 'as'
        lines   = self.root._lines
        ln, col = _next_find(lines, *pattern.f.pars()[2:], end_ln, end_col, 'as')  # skip the 'as'
        ln, col = _next_find(lines, ln, col + 2, end_ln, end_col, a.name or '_')

    return oneinfo(prefix, None, fstloc(ln, col, ln, end_col))

def _one_info_TypeVar_bound(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln  = self.ln
    col = self.col + len(self.a.name)

    if bound := self.a.bound:
        _, _, end_ln, end_col = bound.f.pars()
    else:
        end_ln  = ln
        end_col = col

    return oneinfo(': ', fstloc(ln, col, end_ln, end_col))

def _one_info_TypeVar_default_value(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if bound := self.a.bound:
        _, _, ln, col = bound.f.pars()
    else:
        ln  = self.ln
        col = self.col + len(self.a.name)

    return oneinfo(' = ', fstloc(ln, col, self.end_ln, self.end_col))

def _one_info_ParamSpec_name(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '**')

def _one_info_ParamSpec_default_value(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    ln, col, src             = _next_find_re(self.root._lines, ln, col + 2, end_ln, end_col, re_identifier)  # + '**', identifier must be there

    return oneinfo(' = ', fstloc(ln, col + len(src), self.end_ln, self.end_col))

def _one_info_TypeVarTuple_default_value(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    ln, col, src             = _next_find_re(self.root._lines, ln, col + 1, end_ln, end_col, re_identifier)  # + '*', identifier must be there

    return oneinfo(' = ', fstloc(ln, col + len(src), self.end_ln, self.end_col))

def _one_info_TypeVarTuple_name(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '*')

if _PYLT12:
    def _one_info_format_spec(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
        raise NotImplementedError('this is only implemented on python version 3.12 and above')

    def _one_info_conversion(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
        raise NotImplementedError('this is only implemented on python version 3.12 and above')

else:
    def _one_info_format_spec(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
        if fspec := self.a.format_spec:
            return oneinfo(':', fspec.f.loc)

        _, _, end_ln, end_col  = self.loc
        end_col               -= 1

        return oneinfo(':', fstloc(end_ln, end_col, end_ln, end_col))

    def _one_info_conversion(self: FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
        if fspec := (a := self.a).format_spec:
            end_ln, end_col, _, _  = fspec.f.loc
        else:
            _, _, end_ln, end_col  = self.loc
            end_col               -= 1

        if a.conversion == -1:
            return oneinfo('!', fstloc(end_ln, end_col, end_ln, end_col))

        _, _, ln, col = a.value.f.loc

        if not (prev := _prev_find(self.root._lines, ln, col, end_ln, end_col, '!')):  # may not be there if conversion is implicit due to =
            return oneinfo('!', fstloc(end_ln, end_col, end_ln, end_col))

        ln, col = prev

        return oneinfo('', fstloc(ln, col, end_ln, end_col))


_PUT_ONE_HANDLERS = {
    (Module, 'body'):                     (True,  None, None), # stmt*  - all stmtishs have sliceable True and handler None to force always use slice operation (because of evil semicolons handled there)
    (Interactive, 'body'):                (True,  None, None), # stmt*
    (Expression, 'body'):                 (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (FunctionDef, 'decorator_list'):      (True,  _put_one_exprish_required, _onestatic_expr_required), # expr*
    (FunctionDef, 'name'):                (False, _put_one_identifier_required, _onestatic_FunctionDef_name), # identifier
    (FunctionDef, 'type_params'):         (True,  _put_one_exprish_required, _onestatic_type_param_required), # type_param*
    (FunctionDef, 'args'):                (False, _put_one_FunctionDef_arguments, _onestatic_arguments_required), # arguments
    (FunctionDef, 'returns'):             (False, _put_one_exprish_optional, _onestatic_FunctionDef_returns), # expr?
    (FunctionDef, 'body'):                (True,  None, None), # stmt*
    (AsyncFunctionDef, 'decorator_list'): (True,  _put_one_exprish_required, _onestatic_expr_required), # expr*
    (AsyncFunctionDef, 'name'):           (False, _put_one_identifier_required, _onestatic_FunctionDef_name), # identifier
    (AsyncFunctionDef, 'type_params'):    (True,  _put_one_exprish_required, _onestatic_type_param_required), # type_param*
    (AsyncFunctionDef, 'args'):           (False, _put_one_FunctionDef_arguments, _onestatic_arguments_required), # arguments
    (AsyncFunctionDef, 'returns'):        (False, _put_one_exprish_optional, _onestatic_FunctionDef_returns), # expr?
    (AsyncFunctionDef, 'body'):           (True,  None, None), # stmt*
    (ClassDef, 'decorator_list'):         (True,  _put_one_exprish_required, _onestatic_expr_required), # expr*
    (ClassDef, 'name'):                   (False, _put_one_identifier_required, onestatic(_one_info_ClassDef_name, _restrict_default, code_as=_code_as_identifier)), # identifier
    (ClassDef, 'type_params'):            (True,  _put_one_exprish_required, _onestatic_type_param_required), # type_param*
    (ClassDef, 'bases'):                  (True,  _put_one_ClassDef_bases, _onestatic_expr_required_starred), # expr*
    (ClassDef, 'keywords'):               (True,  _put_one_ClassDef_keywords, _onestatic_keyword_required), # keyword*
    (ClassDef, 'body'):                   (True,  None, None), # stmt*
    (Return, 'value'):                    (False, _put_one_exprish_optional, onestatic(_one_info_Return_value, _restrict_default)), # expr?
    (Delete, 'targets'):                  (True,  _put_one_exprish_required, _onestatic_target), # expr*
    (Assign, 'targets'):                  (True,  _put_one_exprish_required, _onestatic_target), # expr*
    (Assign, 'value'):                    (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (TypeAlias, 'name'):                  (False, _put_one_exprish_required, _onestatic_target_Name), # expr
    (TypeAlias, 'type_params'):           (True,  _put_one_exprish_required, _onestatic_type_param_required), # type_param*
    (TypeAlias, 'value'):                 (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (AugAssign, 'target'):                (False, _put_one_exprish_required, _onestatic_target_single), # expr
    (AugAssign, 'op'):                    (False, _put_one_op, onestatic(None, code_as=_code_as_augop)), # operator
    (AugAssign, 'value'):                 (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (AnnAssign, 'target'):                (False, _put_one_AnnAssign_target, _onestatic_target_single), # expr
    (AnnAssign, 'annotation'):            (False, _put_one_exprish_required, onestatic(_one_info_exprish_required, _restrict_default)), # expr  - exclude [Lambda, Yield, YieldFrom, Await, NamedExpr]?
    (AnnAssign, 'value'):                 (False, _put_one_exprish_optional, onestatic(_one_info_AnnAssign_value, _restrict_default)), # expr?
    (AnnAssign, 'simple'):                (False, _put_one_AnnAssign_simple, onestatic(None, int)), # int
    (For, 'target'):                      (False, _put_one_exprish_required, _onestatic_target), # expr
    (For, 'iter'):                        (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (For, 'body'):                        (True,  None, None), # stmt*
    (For, 'orelse'):                      (True,  None, None), # stmt*
    (AsyncFor, 'target'):                 (False, _put_one_exprish_required, _onestatic_target), # expr
    (AsyncFor, 'iter'):                   (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (AsyncFor, 'body'):                   (True,  None, None), # stmt*
    (AsyncFor, 'orelse'):                 (True,  None, None), # stmt*
    (While, 'test'):                      (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (While, 'body'):                      (True,  None, None), # stmt*
    (While, 'orelse'):                    (True,  None, None), # stmt*
    (If, 'test'):                         (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (If, 'body'):                         (True,  None, None), # stmt*
    (If, 'orelse'):                       (True,  None, None), # stmt*
    (With, 'items'):                      (True,  _put_one_with_items, _onestatic_withitem_required), # withitem*
    (With, 'body'):                       (True,  None, None), # stmt*
    (AsyncWith, 'items'):                 (True,  _put_one_exprish_required, _onestatic_withitem_required), # withitem*
    (AsyncWith, 'body'):                  (True,  None, None), # stmt*
    (Match, 'subject'):                   (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Match, 'cases'):                     (True,  None, None), # match_case*
    (Raise, 'exc'):                       (False, _put_one_exprish_optional, onestatic(_one_info_Raise_exc, _restrict_default)), # expr?
    (Raise, 'cause'):                     (False, _put_one_exprish_optional, onestatic(_one_info_Raise_cause, _restrict_default)), # expr?
    (Try, 'body'):                        (True,  None, None), # stmt*
    (Try, 'handlers'):                    (True,  None, None), # excepthandler*
    (Try, 'orelse'):                      (True,  None, None), # stmt*
    (Try, 'finalbody'):                   (True,  None, None), # stmt*
    (TryStar, 'body'):                    (True,  None, None), # stmt*
    (TryStar, 'handlers'):                (True,  None, None), # excepthandler*
    (TryStar, 'orelse'):                  (True,  None, None), # stmt*
    (TryStar, 'finalbody'):               (True,  None, None), # stmt*
    (Assert, 'test'):                     (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Assert, 'msg'):                      (False, _put_one_exprish_optional, onestatic(_one_info_Assert_msg, _restrict_default)), # expr?
    (Import, 'names'):                    (True,  _put_one_exprish_required, onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_alias_dotted)), # alias*
    (ImportFrom, 'module'):               (False, _put_one_identifier_optional, onestatic(_one_info_ImportFrom_module, _restrict_default, code_as=_code_as_identifier_dotted)), # identifier? (dotted)
    (ImportFrom, 'names'):                (True,  _put_one_ImportFrom_names, onestatic(_one_info_exprish_required, _restrict_default, code_as=_code_as_alias_star)), # alias*
    (ImportFrom, 'level'):                (False, _put_one_NOT_IMPLEMENTED_YET, None), # int?
    (Global, 'names'):                    (True,  _put_one_identifier_required, _onestatic_Global_Nonlocal_names), # identifier*
    (Nonlocal, 'names'):                  (True,  _put_one_identifier_required, _onestatic_Global_Nonlocal_names), # identifier*
    (Expr, 'value'):                      (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (BoolOp, 'op'):                       (False, _put_one_BoolOp_op, onestatic(None)), # boolop  - very special case gets handled entirely in _put_one_BoolOp_op
    (BoolOp, 'values'):                   (True,  _put_one_exprish_required, _onestatic_expr_required), # expr*
    (NamedExpr, 'target'):                (False, _put_one_exprish_required, _onestatic_target_Name), # expr
    (NamedExpr, 'value'):                 (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (BinOp, 'left'):                      (False, _put_one_BinOp_left_right, _onestatic_expr_required), # expr
    (BinOp, 'op'):                        (False, _put_one_op, onestatic(None, code_as=_code_as_binop)), # operator
    (BinOp, 'right'):                     (False, _put_one_BinOp_left_right, _onestatic_expr_required), # expr
    (UnaryOp, 'op'):                      (False, _put_one_op, onestatic(None, code_as=_code_as_unaryop)), # unaryop
    (UnaryOp, 'operand'):                 (False, _put_one_UnaryOp_operand, _onestatic_expr_required), # expr
    (Lambda, 'args'):                     (False, _put_one_Lambda_arguments, _onestatic_arguments_lambda_required), # arguments
    (Lambda, 'body'):                     (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (IfExp, 'body'):                      (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (IfExp, 'test'):                      (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (IfExp, 'orelse'):                    (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Dict, 'keys'):                       (False, _put_one_Dict_keys, onestatic(_one_info_Dict_key, _restrict_default)), # expr*
    (Dict, 'values'):                     (False, _put_one_exprish_required, _onestatic_expr_required), # expr*
    (Dict, ''):                           (True,  None, None), # expr*
    (Set, 'elts'):                        (True,  _put_one_exprish_required, _onestatic_expr_required_starred), # expr*
    (ListComp, 'elt'):                    (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (ListComp, 'generators'):             (True,  _put_one_exprish_required, _onestatic_comprehension_required), # comprehension*
    (SetComp, 'elt'):                     (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (SetComp, 'generators'):              (True,  _put_one_exprish_required, _onestatic_comprehension_required), # comprehension*
    (DictComp, 'key'):                    (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (DictComp, 'value'):                  (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (DictComp, 'generators'):             (True,  _put_one_exprish_required, _onestatic_comprehension_required), # comprehension*
    (GeneratorExp, 'elt'):                (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (GeneratorExp, 'generators'):         (True,  _put_one_exprish_required, _onestatic_comprehension_required), # comprehension*
    (Await, 'value'):                     (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Yield, 'value'):                     (False, _put_one_exprish_optional, onestatic(_one_info_Yield_value, _restrict_default)), # expr?
    (YieldFrom, 'value'):                 (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Compare, 'left'):                    (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Compare, 'ops'):                     (False, _put_one_op, onestatic(None, code_as=_code_as_cmpop)), # cmpop*
    (Compare, 'comparators'):             (False, _put_one_exprish_required, _onestatic_expr_required), # expr*
    (Compare, ''):                        (True,  _put_one_Compare_combined, _onestatic_expr_required), # expr*
    (Call, 'func'):                       (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Call, 'args'):                       (True,  _put_one_Call_args, onestatic(_one_info_exprish_required, _restrict_fmtval_slice, code_as=_code_as_callarg)), # expr*
    (Call, 'keywords'):                   (True,  _put_one_Call_keywords, _onestatic_keyword_required), # keyword*
    (FormattedValue, 'value'):            (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (FormattedValue, 'conversion'):       (False, _put_one_NOT_IMPLEMENTED_YET_12, onestatic(_one_info_conversion, Constant)), # int  # onestatic only here for info for raw put, Constant must be str
    (FormattedValue, 'format_spec'):      (False, _put_one_NOT_IMPLEMENTED_YET_12, onestatic(_one_info_format_spec, JoinedStr)), # expr?  # onestatic only here for info for raw put
    (Interpolation, 'value'):             (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Interpolation, 'str'):               (False, _put_one_NOT_IMPLEMENTED_YET_14, onestatic(None, str)), # constant
    (Interpolation, 'conversion'):        (False, _put_one_NOT_IMPLEMENTED_YET_14, onestatic(_one_info_conversion, Constant)), # int  # onestatic only here for info for raw put, Constant must be str
    (Interpolation, 'format_spec'):       (False, _put_one_NOT_IMPLEMENTED_YET_14, onestatic(_one_info_format_spec, JoinedStr)), # expr?  # onestatic only here for info for raw put
    (JoinedStr, 'values'):                (True,  _put_one_NOT_IMPLEMENTED_YET_12, None), # expr*
    (TemplateStr, 'values'):              (True,  _put_one_NOT_IMPLEMENTED_YET_12, None), # expr*
    (Constant, 'value'):                  (False, _put_one_constant, onestatic(None, constant)), # constant
    (Constant, 'kind'):                   (False, _put_one_NOT_IMPLEMENTED_YET, None), # string?
    (Attribute, 'value'):                 (False, _put_one_Attribute_value, _onestatic_expr_required), # expr
    (Attribute, 'attr'):                  (False, _put_one_identifier_required, onestatic(_one_info_Attribute_attr, _restrict_default, code_as=_code_as_identifier)), # identifier
    (Attribute, 'ctx'):                   (False, _put_one_ctx, _onestatic_ctx), # expr_context
    (Subscript, 'value'):                 (False, _put_one_Subscript_value, _onestatic_expr_required), # expr
    (Subscript, 'slice'):                 (False, _put_one_Subscript_slice, onestatic(_one_info_exprish_required, _restrict_fmtval_starred, code_as=_code_as_slice)), # expr
    (Subscript, 'ctx'):                   (False, _put_one_ctx, _onestatic_ctx), # expr_context
    (Starred, 'value'):                   (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (Starred, 'ctx'):                     (False, _put_one_ctx, _onestatic_ctx), # expr_context
    (Name, 'id'):                         (False, _put_one_identifier_required, _onestatic_identifier_required), # identifier
    (Name, 'ctx'):                        (False, _put_one_ctx, _onestatic_ctx), # expr_context
    (List, 'elts'):                       (True,  _put_one_List_elts, _onestatic_expr_required_starred), # expr*
    (List, 'ctx'):                        (False, _put_one_ctx, _onestatic_ctx), # expr_context
    (Tuple, 'elts'):                      (True,  _put_one_Tuple_elts, onestatic(_one_info_exprish_required, _restrict_fmtval, code_as=_code_as_sliceelt)), # expr*  - special handling because Tuples can contain Slices in an unparenthesized .slice field
    (Tuple, 'ctx'):                       (False, _put_one_ctx, _onestatic_ctx), # expr_context
    (Slice, 'lower'):                     (False, _put_one_exprish_optional, _onestatic_Slice_lower), # expr?
    (Slice, 'upper'):                     (False, _put_one_exprish_optional, _onestatic_Slice_upper), # expr?
    (Slice, 'step'):                      (False, _put_one_exprish_optional, _onestatic_Slice_step), # expr?
    (comprehension, 'target'):            (False, _put_one_exprish_required, _onestatic_target), # expr
    (comprehension, 'iter'):              (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (comprehension, 'ifs'):               (True,  _put_one_exprish_required, _onestatic_expr_required), # expr*
    (comprehension, 'is_async'):          (False, _put_one_NOT_IMPLEMENTED_YET, None), # int
    (ExceptHandler, 'type'):              (False, _put_one_exprish_optional, onestatic(_one_info_ExceptHandler_type, _restrict_default)), # expr?
    (ExceptHandler, 'name'):              (False, _put_one_ExceptHandler_name, onestatic(_one_info_ExceptHandler_name, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (ExceptHandler, 'body'):              (True,  None, None), # stmt*
    (arguments, 'posonlyargs'):           (False, _put_one_arg, _onestatic_arg_required), # arg*
    (arguments, 'args'):                  (False, _put_one_arg, _onestatic_arg_required), # arg*
    (arguments, 'defaults'):              (False, _put_one_exprish_required, _onestatic_expr_required), # expr*
    (arguments, 'vararg'):                (False, _put_one_exprish_optional, onestatic(_one_info_arguments_vararg, _restrict_default, code_as=_code_as_arg)), # arg?
    (arguments, 'kwonlyargs'):            (False, _put_one_arg, _onestatic_arg_required), # arg*
    (arguments, 'kw_defaults'):           (False, _put_one_exprish_optional, onestatic(_one_info_arguments_kw_defaults, _restrict_default)), # expr*
    (arguments, 'kwarg'):                 (False, _put_one_exprish_optional, onestatic(_one_info_arguments_kwarg, _restrict_default, code_as=_code_as_arg)), # arg?
    (arg, 'arg'):                         (False, _put_one_identifier_required, _onestatic_identifier_required), # identifier
    (arg, 'annotation'):                  (False, _put_one_arg_annotation, onestatic(_one_info_arg_annotation, _restrict_default)), # expr?  - exclude [Lambda, Yield, YieldFrom, Await, NamedExpr]?
    (keyword, 'arg'):                     (False, _put_one_keyword_arg, onestatic(_one_info_keyword_arg, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (keyword, 'value'):                   (False, _put_one_exprish_required, _onestatic_expr_required), # expr
    (alias, 'name'):                      (False, _put_one_identifier_required, onestatic(_one_info_identifier_alias, _restrict_default, code_as=_code_as_identifier_alias)), # identifier  - alias star or dotted not valid for all uses but being general here (and lazy, don't feel like checking parent)
    (alias, 'asname'):                    (False, _put_one_identifier_optional, onestatic(_one_info_alias_asname, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (withitem, 'context_expr'):           (False, _put_one_withitem_context_expr, _onestatic_expr_required), # expr
    (withitem, 'optional_vars'):          (False, _put_one_withitem_optional_vars, onestatic(_one_info_withitem_optional_vars, (Name, Tuple, List, Attribute, Subscript), ctx=Store)), # expr?
    (match_case, 'pattern'):              (False, _put_one_pattern, _onestatic_pattern_required), # pattern
    (match_case, 'guard'):                (False, _put_one_exprish_optional, onestatic(_one_info_match_case_guard, _restrict_default)), # expr?
    (match_case, 'body'):                 (True,  None, None), # stmt*
    (MatchValue, 'value'):                (False, _put_one_MatchValue_value, onestatic(_one_info_exprish_required, _is_valid_MatchValue_value)), # expr
    (MatchSingleton, 'value'):            (False, _put_one_constant, onestatic(None, (bool, NoneType))), # constant
    (MatchSequence, 'patterns'):          (True,  _put_one_pattern, _onestatic_pattern_required), # pattern*
    (MatchMapping, 'keys'):               (False, _put_one_exprish_required, onestatic(_one_info_exprish_required, _is_valid_MatchMapping_key)), # expr*  Ops for `-1` or `2+3j`
    (MatchMapping, 'patterns'):           (False, _put_one_pattern, _onestatic_pattern_required), # pattern*
    (MatchMapping, 'rest'):               (False, _put_one_identifier_optional, onestatic(_one_info_MatchMapping_rest, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (MatchMapping, ''):                   (True,  None, None), # expr*
    (MatchClass, 'cls'):                  (False, _put_one_exprish_required, onestatic(_one_info_exprish_required, _is_valid_MatchClass_cls)), # expr
    (MatchClass, 'patterns'):             (True,  _put_one_pattern, _onestatic_pattern_required), # pattern*
    (MatchClass, 'kwd_attrs'):            (False, _put_one_identifier_required, onestatic(_one_info_MatchClass_kwd_attrs, _restrict_default, code_as=_code_as_identifier)), # identifier*
    (MatchClass, 'kwd_patterns'):         (False, _put_one_pattern, _onestatic_pattern_required), # pattern*
    (MatchStar, 'name'):                  (False, _put_one_MatchStar_name, onestatic(_one_info_MatchStar_name, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (MatchAs, 'pattern'):                 (False, _put_one_MatchAs_pattern, onestatic(_one_info_MatchAs_pattern, _restrict_default, code_as=_code_as_pattern)), # pattern?
    (MatchAs, 'name'):                    (False, _put_one_MatchAs_name, onestatic(_one_info_MatchAs_name, _restrict_default, code_as=_code_as_identifier)), # identifier?
    (MatchOr, 'patterns'):                (True,  _put_one_pattern, _onestatic_pattern_required), # pattern*
    (TypeVar, 'name'):                    (False, _put_one_identifier_required, _onestatic_identifier_required), # identifier
    (TypeVar, 'bound'):                   (False, _put_one_exprish_optional, onestatic(_one_info_TypeVar_bound, _restrict_default)), # expr?
    (TypeVar, 'default_value'):           (False, _put_one_exprish_optional, onestatic(_one_info_TypeVar_default_value, _restrict_default)), # expr?
    (ParamSpec, 'name'):                  (False, _put_one_identifier_required, onestatic(_one_info_ParamSpec_name, _restrict_default, code_as=_code_as_identifier)), # identifier
    (ParamSpec, 'default_value'):         (False, _put_one_exprish_optional, onestatic(_one_info_ParamSpec_default_value, _restrict_default)), # expr?
    (TypeVarTuple, 'name'):               (False, _put_one_identifier_required, onestatic(_one_info_TypeVarTuple_name, _restrict_default, code_as=_code_as_identifier)), # identifier
    (TypeVarTuple, 'default_value'):      (False, _put_one_exprish_optional, onestatic(_one_info_TypeVarTuple_default_value, _restrict_default)), # expr?


    # NOT DONE:
    # =========

    # (Module, 'type_ignores'):             (), # type_ignore*

    # (FunctionType, 'argtypes'):           (), # expr*
    # (FunctionType, 'returns'):            (), # expr
    # (TypeIgnore, 'lineno'):               (), # int
    # (TypeIgnore, 'tag'):                  (), # string

    # (FunctionDef, 'type_comment'):        (), # string?
    # (AsyncFunctionDef, 'type_comment'):   (), # string?
    # (Assign, 'type_comment'):             (), # string?
    # (For, 'type_comment'):                (), # string?
    # (AsyncFor, 'type_comment'):           (), # string?
    # (With, 'type_comment'):               (), # string?
    # (AsyncWith, 'type_comment'):          (), # string?
    # (arg, 'type_comment'):                (), # string?

    # MAYBE DO:
    # =========

    # (ImportFrom, 'level'):                (), # int?
    # (Constant, 'kind'):                   (), # string?
    # (comprehension, 'is_async'):          (), # int
}

# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = ['_get_one', '_put_one']  # used by make_docs.py

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
