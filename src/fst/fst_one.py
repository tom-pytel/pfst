"""Misc lower level FST methods."""

from ast import *
from typing import Any, Optional

from .astutil import *
from .astutil import TryStar

from .shared import (
    Code, NodeTypeError,
)


def _to_to_slice_idx(self: 'FST', idx: int, field: str, to: Optional['FST']):
    """If a `to` parameter is passed then try to convert it to an index in the same body list as `self`."""

    if not to:
        return idx + 1 or len(getattr(self.a, field))  # or for negative indices

    elif to.parent is self.parent is not None and (pf := to.pfield).name == self.pfield.name:
        if (to_idx := pf.idx) < idx:
            raise ValueError("invalid 'to' node, must follow self in body")

        return to_idx + 1

    raise NodeTypeError(f"invalid 'to' node")

def _put_one_stmtish(self: 'FST', code: Code | None, idx: int | None, field: str, child: Any, **options,
                        ) -> Optional['FST']:
    """Put or delete a single statementish node to a list of them (body, orelse, handlers, finalbody or cases)."""

    self._put_slice_stmtish(code, idx, self._to_to_slice_idx(idx, field, options.get('to')), field, True, **options)

    return None if code is None else getattr(self.a, field)[idx].f

def _put_one_tuple_list_or_set(self: 'FST', code: Code | None, idx: int | None, field: str, child: Any, **options,
                                ) -> Optional['FST']:
    """Put or delete a single expression to a Tuple, List or Set elts."""

    self._put_slice_tuple_list_or_set(code, idx, self._to_to_slice_idx(idx, field, options.get('to')), field, True,
                                        **options)

    return None if code is None else getattr(self.a, field)[idx].f

def _put_one_expr_required(self: 'FST', code: Code | None, idx: int | None, field: str, child: Any, **options,
                            ) -> Optional['FST']:
    """Put a single required expression node."""

    if code is None:
        raise ValueError(f'cannot delete a {self.a.__class__.__name__}.{field}')
    if idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')
    if options.get('to'):
        raise NodeTypeError(f"cannot put with 'to' to {self.a.__class__.__name__}.{field}")

    ast     = self.a
    put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)
    put_ast = put_fst.a
    childf  = child.f
    pars    = bool(FST.get_option('pars', options))
    effpars = pars or put_fst.is_parenthesized_tuple() is False  # need tuple check because otherwise location would be wrong after
    loc     = childf.pars(effpars)  # don't need exc_genexpr_solo=True here because guaranteed not to be this

    if precedence_require_parens(put_ast, ast, field, None):
        if not put_fst.is_atom() and (effpars or not childf.pars(ret_npars=True)[1]):
            put_fst.parenthesize()

    elif pars:  # remove parens only if allowed to
        put_fst.unparenthesize()

    put_fst.indent_lns(childf.get_indent(), docstr=options.get('docstr'))

    ln, col, end_ln, end_col = loc

    lines       = self.root._lines
    put_lines   = put_fst._lines
    dcol_offset = lines[ln].c2b(col)

    put_fst.offset(0, 0, ln, dcol_offset)
    self.put_src(put_lines, ln, col, end_ln, end_col, True)
    childf._set_ast(put_ast)

    return put_ast.f

def _put_one(self: 'FST', code: Code | None, idx: int | None, field: str, **options) -> Optional['FST']:
    """Put new, replace or delete a node (or limited non-node) to a field of `self`."""

    if isinstance(child := getattr(self.a, field), list):
        child = child[idx]

    ast = self.a
    raw = FST.get_option('raw', options)

    if raw is not True:
        if raw and raw != 'auto':
            raise ValueError(f"invalid value for raw parameter '{raw}'")

        try:
            if handler := _PUT_ONE_HANDLERS.get((ast.__class__, field)):
                return handler(self, code, idx, field, child, **options)

        except (SyntaxError, NodeTypeError):
            if not raw:
                raise

        else:
            if not raw:
                raise ValueError(f"cannot replace in {ast.__class__.__name__}.{field}")

    ret = child.f._reparse_raw_node(code, **options)

    return None if code is None else ret


# TODO: finish these


_PUT_ONE_HANDLERS = {
    (Module, 'body'):                     _put_one_stmtish, # stmt*
    # (Module, 'type_ignores'):             _put_one_default, # type_ignore*
    (Interactive, 'body'):                _put_one_stmtish, # stmt*
    (Expression, 'body'):                 _put_one_expr_required, # expr
    # (FunctionType, 'argtypes'):           _put_one_default, # expr*
    # (FunctionType, 'returns'):            _put_one_default, # expr
    # (FunctionDef, 'decorator_list'):      _put_one_default, # expr*
    # (FunctionDef, 'name'):                _put_one_default, # identifier
    # (FunctionDef, 'type_params'):         _put_one_default, # type_param*
    # (FunctionDef, 'args'):                _put_one_default, # arguments
    # (FunctionDef, 'returns'):             _put_one_default, # expr?
    (FunctionDef, 'body'):                _put_one_stmtish, # stmt*
    # (FunctionDef, 'type_comment'):        _put_one_default, # string?
    # (AsyncFunctionDef, 'decorator_list'): _put_one_default, # expr*
    # (AsyncFunctionDef, 'name'):           _put_one_default, # identifier
    # (AsyncFunctionDef, 'type_params'):    _put_one_default, # type_param*
    # (AsyncFunctionDef, 'args'):           _put_one_default, # arguments
    # (AsyncFunctionDef, 'returns'):        _put_one_default, # expr?
    (AsyncFunctionDef, 'body'):           _put_one_stmtish, # stmt*
    # (AsyncFunctionDef, 'type_comment'):   _put_one_default, # string?
    # (ClassDef, 'decorator_list'):         _put_one_default, # expr*
    # (ClassDef, 'name'):                   _put_one_default, # identifier
    # (ClassDef, 'type_params'):            _put_one_default, # type_param*
    # (ClassDef, 'bases'):                  _put_one_default, # expr*
    # (ClassDef, 'keywords'):               _put_one_default, # keyword*
    (ClassDef, 'body'):                   _put_one_stmtish, # stmt*
    # (Return, 'value'):                    _put_one_default, # expr?
    # (Delete, 'targets'):                  _put_one_default, # expr*
    # (Assign, 'targets'):                  _put_one_default, # expr*
    (Assign, 'value'):                    _put_one_expr_required, # expr
    # (Assign, 'type_comment'):             _put_one_default, # string?
    # (TypeAlias, 'name'):                  _put_one_default, # expr
    # (TypeAlias, 'type_params'):           _put_one_default, # type_param*
    # (TypeAlias, 'value'):                 _put_one_default, # expr
    # (AugAssign, 'target'):                _put_one_default, # expr
    # (AugAssign, 'op'):                    _put_one_default, # operator
    (AugAssign, 'value'):                 _put_one_expr_required, # expr
    # (AnnAssign, 'target'):                _put_one_default, # expr
    # (AnnAssign, 'annotation'):            _put_one_default, # expr
    # (AnnAssign, 'value'):                 _put_one_default, # expr?
    # (AnnAssign, 'simple'):                _put_one_default, # int
    # (For, 'target'):                      _put_one_default, # expr
    (For, 'iter'):                        _put_one_expr_required, # expr
    (For, 'body'):                        _put_one_stmtish, # stmt*
    (For, 'orelse'):                      _put_one_stmtish, # stmt*
    # (For, 'type_comment'):                _put_one_default, # string?
    # (AsyncFor, 'target'):                 _put_one_default, # expr
    (AsyncFor, 'iter'):                   _put_one_expr_required, # expr
    (AsyncFor, 'body'):                   _put_one_stmtish, # stmt*
    (AsyncFor, 'orelse'):                 _put_one_stmtish, # stmt*
    # (AsyncFor, 'type_comment'):           _put_one_default, # string?
    (While, 'test'):                      _put_one_expr_required, # expr
    (While, 'body'):                      _put_one_stmtish, # stmt*
    (While, 'orelse'):                    _put_one_stmtish, # stmt*
    (If, 'test'):                         _put_one_expr_required, # expr
    (If, 'body'):                         _put_one_stmtish, # stmt*
    (If, 'orelse'):                       _put_one_stmtish, # stmt*
    # (With, 'items'):                      _put_one_default, # withitem*
    (With, 'body'):                       _put_one_stmtish, # stmt*
    # (With, 'type_comment'):               _put_one_default, # string?
    # (AsyncWith, 'items'):                 _put_one_default, # withitem*
    (AsyncWith, 'body'):                  _put_one_stmtish, # stmt*
    # (AsyncWith, 'type_comment'):          _put_one_default, # string?
    (Match, 'subject'):                   _put_one_expr_required, # expr
    (Match, 'cases'):                     _put_one_stmtish, # match_case*
    # (Raise, 'exc'):                       _put_one_default, # expr?
    # (Raise, 'cause'):                     _put_one_default, # expr?
    (Try, 'body'):                        _put_one_stmtish, # stmt*
    (Try, 'handlers'):                    _put_one_stmtish, # excepthandler*
    (Try, 'orelse'):                      _put_one_stmtish, # stmt*
    (Try, 'finalbody'):                   _put_one_stmtish, # stmt*
    (TryStar, 'body'):                    _put_one_stmtish, # stmt*
    (TryStar, 'handlers'):                _put_one_stmtish, # excepthandler*
    (TryStar, 'orelse'):                  _put_one_stmtish, # stmt*
    (TryStar, 'finalbody'):               _put_one_stmtish, # stmt*
    (Assert, 'test'):                     _put_one_expr_required, # expr
    # (Assert, 'msg'):                      _put_one_default, # expr?
    # (Import, 'names'):                    _put_one_default, # alias*
    # (ImportFrom, 'module'):               _put_one_default, # identifier?
    # (ImportFrom, 'names'):                _put_one_default, # alias*
    # (ImportFrom, 'level'):                _put_one_default, # int?
    # (Global, 'names'):                    _put_one_default, # identifier*
    # (Nonlocal, 'names'):                  _put_one_default, # identifier*
    (Expr, 'value'):                      _put_one_expr_required, # expr
    # (BoolOp, 'op'):                       _put_one_default, # boolop
    # (BoolOp, 'values'):                   _put_one_default, # expr*
    # (NamedExpr, 'target'):                _put_one_default, # expr
    (NamedExpr, 'value'):                 _put_one_expr_required, # expr
    (BinOp, 'left'):                      _put_one_expr_required, # expr
    # (BinOp, 'op'):                        _put_one_default, # operator
    (BinOp, 'right'):                     _put_one_expr_required, # expr
    # (UnaryOp, 'op'):                      _put_one_default, # unaryop
    (UnaryOp, 'operand'):                 _put_one_expr_required, # expr
    # (Lambda, 'args'):                     _put_one_default, # arguments
    (Lambda, 'body'):                     _put_one_expr_required, # expr
    (IfExp, 'body'):                      _put_one_expr_required, # expr
    (IfExp, 'test'):                      _put_one_expr_required, # expr
    (IfExp, 'orelse'):                    _put_one_expr_required, # expr
    # (Dict, 'keys'):                       _put_one_default, # expr*           - takes idx, handle special key=None?
    # (Dict, 'values'):                     _put_one_default, # expr*           - takes idx,
    (Set, 'elts'):                        _put_one_tuple_list_or_set, # expr*
    (ListComp, 'elt'):                    _put_one_expr_required, # expr
    # (ListComp, 'generators'):             _put_one_default, # comprehension*
    (SetComp, 'elt'):                     _put_one_expr_required, # expr
    # (SetComp, 'generators'):              _put_one_default, # comprehension*
    (DictComp, 'key'):                    _put_one_expr_required, # expr
    (DictComp, 'value'):                  _put_one_expr_required, # expr
    # (DictComp, 'generators'):             _put_one_default, # comprehension*
    (GeneratorExp, 'elt'):                _put_one_expr_required, # expr
    # (GeneratorExp, 'generators'):         _put_one_default, # comprehension*
    (Await, 'value'):                     _put_one_expr_required, # expr
    # (Yield, 'value'):                     _put_one_default, # expr?
    (YieldFrom, 'value'):                 _put_one_expr_required, # expr
    # (Compare, 'left'):                    _put_one_default, # expr
    # (Compare, 'ops'):                     _put_one_default, # cmpop*
    # (Compare, 'comparators'):             _put_one_default, # expr*
    # (Call, 'func'):                       _put_one_default, # expr            - identifier
    # (Call, 'args'):                       _put_one_default, # expr*
    # (Call, 'keywords'):                   _put_one_default, # keyword*
    (FormattedValue, 'value'):            _put_one_expr_required, # expr
    # (FormattedValue, 'format_spec'):      _put_one_default, # expr?
    # (FormattedValue, 'conversion'):       _put_one_default, # int
    # (Interpolation, 'value'):             _put_one_default, # expr            - need to change .str as well as expr
    # (Interpolation, 'constant'):          _put_one_default, # str
    # (Interpolation, 'conversion'):        _put_one_default, # int
    # (Interpolation, 'format_spec'):       _put_one_default, # expr?
    # (JoinedStr, 'values'):                _put_one_default, # expr*
    # (TemplateStr, 'values'):              _put_one_default, # expr*
    # (Constant, 'value'):                  _put_one_default, # constant
    # (Constant, 'kind'):                   _put_one_default, # string?
    (Attribute, 'value'):                 _put_one_expr_required, # expr
    # (Attribute, 'attr'):                  _put_one_default, # identifier
    # (Attribute, 'ctx'):                   _put_one_default, # expr_context
    (Subscript, 'value'):                 _put_one_expr_required, # expr
    # (Subscript, 'slice'):                 _put_one_default, # expr
    # (Subscript, 'ctx'):                   _put_one_default, # expr_context
    (Starred, 'value'):                   _put_one_expr_required, # expr
    # (Starred, 'ctx'):                     _put_one_default, # expr_context
    # (Name, 'id'):                         _put_one_default, # identifier
    # (Name, 'ctx'):                        _put_one_default, # expr_context
    (List, 'elts'):                       _put_one_tuple_list_or_set, # expr*
    # (List, 'ctx'):                        _put_one_default, # expr_context
    (Tuple, 'elts'):                      _put_one_tuple_list_or_set, # expr*
    # (Tuple, 'ctx'):                       _put_one_default, # expr_context
    # (Slice, 'lower'):                     _put_one_default, # expr?
    # (Slice, 'upper'):                     _put_one_default, # expr?
    # (Slice, 'step'):                      _put_one_default, # expr?
    # (comprehension, 'target'):            _put_one_default, # expr            - Name or Tuple (maybe empty?)
    (comprehension, 'iter'):              _put_one_expr_required, # expr
    # (comprehension, 'ifs'):               _put_one_default, # expr*
    # (comprehension, 'is_async'):          _put_one_default, # int
    # (ExceptHandler, 'type'):              _put_one_default, # expr?
    # (ExceptHandler, 'name'):              _put_one_default, # identifier?
    (ExceptHandler, 'body'):              _put_one_stmtish, # stmt*
    # (arguments, 'posonlyargs'):           _put_one_default, # arg*
    # (arguments, 'args'):                  _put_one_default, # arg*
    # (arguments, 'defaults'):              _put_one_default, # expr*
    # (arguments, 'vararg'):                _put_one_default, # arg?
    # (arguments, 'kwonlyargs'):            _put_one_default, # arg*
    # (arguments, 'kw_defaults'):           _put_one_default, # expr*
    # (arguments, 'kwarg'):                 _put_one_default, # arg?
    # (arg, 'arg'):                         _put_one_default, # identifier
    # (arg, 'annotation'):                  _put_one_default, # expr?
    # (arg, 'type_comment'):                _put_one_default, # string?
    # (keyword, 'arg'):                     _put_one_default, # identifier?
    (keyword, 'value'):                   _put_one_expr_required, # expr
    # (alias, 'name'):                      _put_one_default, # identifier
    # (alias, 'asname'):                    _put_one_default, # identifier?
    (withitem, 'context_expr'):           _put_one_expr_required, # expr
    # (withitem, 'optional_vars'):          _put_one_default, # expr?
    # (match_case, 'pattern'):              _put_one_default, # pattern
    # (match_case, 'guard'):                _put_one_default, # expr?
    (match_case, 'body'):                 _put_one_stmtish, # stmt*
    # (MatchValue, 'value'):                _put_one_default, # expr            - limited values, Constant? Name becomes MatchAs
    # (MatchSingleton, 'value'):            _put_one_default, # constant
    # (MatchSequence, 'patterns'):          _put_one_default, # pattern*
    # (MatchMapping, 'keys'):               _put_one_default, # expr*
    # (MatchMapping, 'patterns'):           _put_one_default, # pattern*
    # (MatchMapping, 'rest'):               _put_one_default, # identifier?
    # (MatchClass, 'cls'):                  _put_one_default, # expr
    # (MatchClass, 'patterns'):             _put_one_default, # pattern*
    # (MatchClass, 'kwd_attrs'):            _put_one_default, # identifier*
    # (MatchClass, 'kwd_patterns'):         _put_one_default, # pattern*
    # (MatchStar, 'name'):                  _put_one_default, # identifier?
    # (MatchAs, 'pattern'):                 _put_one_default, # pattern?
    # (MatchAs, 'name'):                    _put_one_default, # identifier?
    # (MatchOr, 'patterns'):                _put_one_default, # pattern*
    # (TypeIgnore, 'lineno'):               _put_one_default, # int
    # (TypeIgnore, 'tag'):                  _put_one_default, # string
    # (TypeVar, 'name'):                    _put_one_default, # identifier
    # (TypeVar, 'bound'):                   _put_one_default, # expr?
    # (TypeVar, 'default_value'):           _put_one_default, # expr?
    # (ParamSpec, 'name'):                  _put_one_default, # identifier
    # (ParamSpec, 'default_value'):         _put_one_default, # expr?
    # (TypeVarTuple, 'name'):               _put_one_default, # identifier
    # (TypeVarTuple, 'default_value'):      _put_one_default, # expr?
}


from .fst import FST
