"""Misc lower level FST methods."""

import re
from ast import *
from typing import Any, Optional

from .astutil import *
from .astutil import TypeAlias, TryStar, type_param, TypeVar, ParamSpec, TypeVarTuple, TemplateStr, Interpolation

from .shared import Code, NodeTypeError, _next_find, _next_find_re


_re_identifier = re.compile(r'[^\d\W]\w*')


def _code_as_identifier(code: Code) -> str | None:
    if isinstance(code, str):
        return code if is_valid_identifier(code) else None
    if isinstance(code, list):
        return code if is_valid_identifier(code := ''.join(code)) else None  # join without newlines to ignore one or two extraneous ones

    if isinstance(code, FST):
        code = code.a

    return code.id if isinstance(code, Name) else None


def _to_to_slice_idx(self: 'FST', idx: int, field: str, to: Optional['FST']):
    """If a `to` parameter is passed then try to convert it to an index in the same field body list of `self`."""

    if not to:
        return idx + 1 or len(getattr(self.a, field))  # 'or' for -1 index to go to end of body

    elif to.parent is self.parent is not None and (pf := to.pfield).name == self.pfield.name:
        if (to_idx := pf.idx) < idx:
            raise ValueError("invalid 'to' node, must follow self in body")

        return to_idx + 1

    raise NodeTypeError(f"invalid 'to' node")


# _put_one_ctx ???


def _put_one_identifier(self: 'FST', code: Code | None, idx: int | None, field: str, child: Any, extra: Any, **options,
                        ) -> Optional['FST']:
    """Put a single required identifier."""

    if code is None:
        raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field}')
    if idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')
    if options.get('to'):
        raise NodeTypeError(f"cannot put with 'to' to {self.a.__class__.__name__}.{field}")
    if not (code := _code_as_identifier(code)):
        raise NodeTypeError(f"expecting identifier for {self.a.__class__.__name__}.{field}")

    ln, col, end_ln, end_col = self.loc  # specifically don't want possible decorator on func or class
    lines                    = self.root._lines

    if not extra:
        m            = _re_identifier.match(lines[ln], col, end_col)  # must be there
        col, end_col = m.span()

    else:
        ln, col      = _next_find(lines, ln, col, end_ln, end_col, extra, lcont=None)  # must be there
        ln, col, src =  _next_find_re(lines, ln, col + len(extra), end_ln, end_col, _re_identifier, lcont=None)  # must be there
        end_ln       = ln
        end_col      = col + len(src)

    self.put_src(code, ln, col, end_ln, end_col, True)

    setattr(self.a, field, code)


def _put_one_stmtish(self: 'FST', code: Code | None, idx: int | None, field: str, child: Any, extra: Any, **options,
                     ) -> Optional['FST']:
    """Put or delete a single statementish node to a list of them (body, orelse, handlers, finalbody or cases)."""

    self._put_slice_stmtish(code, idx, _to_to_slice_idx(self, idx, field, options.get('to')), field, True, **options)

    return None if code is None else getattr(self.a, field)[idx].f


def _put_one_tuple_list_or_set(self: 'FST', code: Code | None, idx: int | None, field: str, child: Any, extra: Any,
                               **options) -> Optional['FST']:
    """Put or delete a single expression to a Tuple, List or Set elts."""

    self._put_slice_tuple_list_or_set(code, idx, _to_to_slice_idx(self, idx, field, options.get('to')), field, True,
                                      **options)

    return None if code is None else getattr(self.a, field)[idx].f






def _put_one_expr(self: 'FST', code: Code | None, idx: int | None, field: str, child: Any, extra: Any, **options,
                  ) -> Optional['FST']:
    """Put a single required expression."""

    if code is None:
        raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field}')
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


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

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
            if handler_and_extra := _PUT_ONE_HANDLERS.get((ast.__class__, field)):
                handler, extra = handler_and_extra

                return handler(self, code, idx, field, child, extra, **options)

        except (SyntaxError, NodeTypeError):
            if not raw:
                raise

        else:
            if not raw:
                raise ValueError(f"cannot replace in {ast.__class__.__name__}.{field}")

    ret = child.f._reparse_raw_node(code, **options)

    return None if code is None else ret


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]

_PUT_ONE_HANDLERS = {
    (Module, 'body'):                     (_put_one_stmtish, None), # stmt*
    # (Module, 'type_ignores'):             (_put_one_default, None), # type_ignore*
    (Interactive, 'body'):                (_put_one_stmtish, None), # stmt*
    (Expression, 'body'):                 (_put_one_expr, None), # expr
    # (FunctionType, 'argtypes'):           (_put_one_default, None), # expr*
    # (FunctionType, 'returns'):            (_put_one_default, None), # expr
    # (FunctionDef, 'decorator_list'):      (_put_one_default, None), # expr*
    (FunctionDef, 'name'):                (_put_one_identifier, 'def'), # identifier
    # (FunctionDef, 'type_params'):         (_put_one_default, None), # type_param*
    # (FunctionDef, 'args'):                (_put_one_default, None), # arguments
    # (FunctionDef, 'returns'):             (_put_one_default, None), # expr?
    (FunctionDef, 'body'):                (_put_one_stmtish, None), # stmt*
    # (FunctionDef, 'type_comment'):        (_put_one_default, None), # string?
    # (AsyncFunctionDef, 'decorator_list'): (_put_one_default, None), # expr*
    (AsyncFunctionDef, 'name'):           (_put_one_identifier, 'def'), # identifier
    # (AsyncFunctionDef, 'type_params'):    (_put_one_default, None), # type_param*
    # (AsyncFunctionDef, 'args'):           (_put_one_default, None), # arguments
    # (AsyncFunctionDef, 'returns'):        (_put_one_default, None), # expr?
    (AsyncFunctionDef, 'body'):           (_put_one_stmtish, None), # stmt*
    # (AsyncFunctionDef, 'type_comment'):   (_put_one_default, None), # string?
    # (ClassDef, 'decorator_list'):         (_put_one_default, None), # expr*
    (ClassDef, 'name'):                   (_put_one_identifier, 'class'), # identifier
    # (ClassDef, 'type_params'):            (_put_one_default, None), # type_param*
    # (ClassDef, 'bases'):                  (_put_one_default, None), # expr*
    # (ClassDef, 'keywords'):               (_put_one_default, None), # keyword*
    (ClassDef, 'body'):                   (_put_one_stmtish, None), # stmt*
    # (Return, 'value'):                    (_put_one_default, None), # expr?
    # (Delete, 'targets'):                  (_put_one_default, None), # expr*
    # (Assign, 'targets'):                  (_put_one_default, None), # expr*
    (Assign, 'value'):                    (_put_one_expr, None), # expr
    # (Assign, 'type_comment'):             (_put_one_default, None), # string?
    # (TypeAlias, 'name'):                  (_put_one_default, None), # expr
    # (TypeAlias, 'type_params'):           (_put_one_default, None), # type_param*
    # (TypeAlias, 'value'):                 (_put_one_default, None), # expr
    # (AugAssign, 'target'):                (_put_one_default, None), # expr
    # (AugAssign, 'op'):                    (_put_one_default, None), # operator
    (AugAssign, 'value'):                 (_put_one_expr, None), # expr
    # (AnnAssign, 'target'):                (_put_one_default, None), # expr
    # (AnnAssign, 'annotation'):            (_put_one_default, None), # expr
    # (AnnAssign, 'value'):                 (_put_one_default, None), # expr?
    # (AnnAssign, 'simple'):                (_put_one_default, None), # int
    # (For, 'target'):                      (_put_one_default, None), # expr
    (For, 'iter'):                        (_put_one_expr, None), # expr
    (For, 'body'):                        (_put_one_stmtish, None), # stmt*
    (For, 'orelse'):                      (_put_one_stmtish, None), # stmt*
    # (For, 'type_comment'):                (_put_one_default, None), # string?
    # (AsyncFor, 'target'):                 (_put_one_default, None), # expr
    (AsyncFor, 'iter'):                   (_put_one_expr, None), # expr
    (AsyncFor, 'body'):                   (_put_one_stmtish, None), # stmt*
    (AsyncFor, 'orelse'):                 (_put_one_stmtish, None), # stmt*
    # (AsyncFor, 'type_comment'):           (_put_one_default, None), # string?
    (While, 'test'):                      (_put_one_expr, None), # expr
    (While, 'body'):                      (_put_one_stmtish, None), # stmt*
    (While, 'orelse'):                    (_put_one_stmtish, None), # stmt*
    (If, 'test'):                         (_put_one_expr, None), # expr
    (If, 'body'):                         (_put_one_stmtish, None), # stmt*
    (If, 'orelse'):                       (_put_one_stmtish, None), # stmt*
    # (With, 'items'):                      (_put_one_default, None), # withitem*
    (With, 'body'):                       (_put_one_stmtish, None), # stmt*
    # (With, 'type_comment'):               (_put_one_default, None), # string?
    # (AsyncWith, 'items'):                 (_put_one_default, None), # withitem*
    (AsyncWith, 'body'):                  (_put_one_stmtish, None), # stmt*
    # (AsyncWith, 'type_comment'):          (_put_one_default, None), # string?
    (Match, 'subject'):                   (_put_one_expr, None), # expr
    (Match, 'cases'):                     (_put_one_stmtish, None), # match_case*
    # (Raise, 'exc'):                       (_put_one_default, None), # expr?
    # (Raise, 'cause'):                     (_put_one_default, None), # expr?
    (Try, 'body'):                        (_put_one_stmtish, None), # stmt*
    (Try, 'handlers'):                    (_put_one_stmtish, None), # excepthandler*
    (Try, 'orelse'):                      (_put_one_stmtish, None), # stmt*
    (Try, 'finalbody'):                   (_put_one_stmtish, None), # stmt*
    (TryStar, 'body'):                    (_put_one_stmtish, None), # stmt*
    (TryStar, 'handlers'):                (_put_one_stmtish, None), # excepthandler*
    (TryStar, 'orelse'):                  (_put_one_stmtish, None), # stmt*
    (TryStar, 'finalbody'):               (_put_one_stmtish, None), # stmt*
    (Assert, 'test'):                     (_put_one_expr, None), # expr
    # (Assert, 'msg'):                      (_put_one_default, None), # expr?
    # (Import, 'names'):                    (_put_one_default, None), # alias*
    # (ImportFrom, 'module'):               (_put_one_default, None), # identifier?
    # (ImportFrom, 'names'):                (_put_one_default, None), # alias*
    # (ImportFrom, 'level'):                (_put_one_default, None), # int?
    # (Global, 'names'):                    (_put_one_default, None), # identifier*
    # (Nonlocal, 'names'):                  (_put_one_default, None), # identifier*
    (Expr, 'value'):                      (_put_one_expr, None), # expr
    # (BoolOp, 'op'):                       (_put_one_default, None), # boolop
    # (BoolOp, 'values'):                   (_put_one_default, None), # expr*
    # (NamedExpr, 'target'):                (_put_one_default, None), # expr
    (NamedExpr, 'value'):                 (_put_one_expr, None), # expr
    (BinOp, 'left'):                      (_put_one_expr, None), # expr
    # (BinOp, 'op'):                        (_put_one_default, None), # operator
    (BinOp, 'right'):                     (_put_one_expr, None), # expr
    # (UnaryOp, 'op'):                      (_put_one_default, None), # unaryop
    (UnaryOp, 'operand'):                 (_put_one_expr, None), # expr
    # (Lambda, 'args'):                     (_put_one_default, None), # arguments
    (Lambda, 'body'):                     (_put_one_expr, None), # expr
    (IfExp, 'body'):                      (_put_one_expr, None), # expr
    (IfExp, 'test'):                      (_put_one_expr, None), # expr
    (IfExp, 'orelse'):                    (_put_one_expr, None), # expr
    # (Dict, 'keys'):                       (_put_one_default, None), # expr*           - takes idx, handle special key=None?
    # (Dict, 'values'):                     (_put_one_default, None), # expr*           - takes idx,
    (Set, 'elts'):                        (_put_one_tuple_list_or_set, None), # expr*
    (ListComp, 'elt'):                    (_put_one_expr, None), # expr
    # (ListComp, 'generators'):             (_put_one_default, None), # comprehension*
    (SetComp, 'elt'):                     (_put_one_expr, None), # expr
    # (SetComp, 'generators'):              (_put_one_default, None), # comprehension*
    (DictComp, 'key'):                    (_put_one_expr, None), # expr
    (DictComp, 'value'):                  (_put_one_expr, None), # expr
    # (DictComp, 'generators'):             (_put_one_default, None), # comprehension*
    (GeneratorExp, 'elt'):                (_put_one_expr, None), # expr
    # (GeneratorExp, 'generators'):         (_put_one_default, None), # comprehension*
    (Await, 'value'):                     (_put_one_expr, None), # expr
    # (Yield, 'value'):                     (_put_one_default, None), # expr?
    (YieldFrom, 'value'):                 (_put_one_expr, None), # expr
    # (Compare, 'left'):                    (_put_one_default, None), # expr
    # (Compare, 'ops'):                     (_put_one_default, None), # cmpop*
    # (Compare, 'comparators'):             (_put_one_default, None), # expr*
    # (Call, 'func'):                       (_put_one_default, None), # expr            - identifier
    # (Call, 'args'):                       (_put_one_default, None), # expr*
    # (Call, 'keywords'):                   (_put_one_default, None), # keyword*
    (FormattedValue, 'value'):            (_put_one_expr, None), # expr
    # (FormattedValue, 'format_spec'):      (_put_one_default, None), # expr?
    # (FormattedValue, 'conversion'):       (_put_one_default, None), # int
    # (Interpolation, 'value'):             (_put_one_default, None), # expr            - need to change .str as well as expr
    # (Interpolation, 'constant'):          (_put_one_default, None), # str
    # (Interpolation, 'conversion'):        (_put_one_default, None), # int
    # (Interpolation, 'format_spec'):       (_put_one_default, None), # expr?
    # (JoinedStr, 'values'):                (_put_one_default, None), # expr*
    # (TemplateStr, 'values'):              (_put_one_default, None), # expr*
    # (Constant, 'value'):                  (_put_one_default, None), # constant
    # (Constant, 'kind'):                   (_put_one_default, None), # string?
    (Attribute, 'value'):                 (_put_one_expr, None), # expr
    # (Attribute, 'attr'):                  (_put_one_default, None), # identifier      - after the "value."
    # (Attribute, 'ctx'):                   (_put_one_default, None), # expr_context
    (Subscript, 'value'):                 (_put_one_expr, None), # expr
    # (Subscript, 'slice'):                 (_put_one_default, None), # expr
    # (Subscript, 'ctx'):                   (_put_one_default, None), # expr_context
    (Starred, 'value'):                   (_put_one_expr, None), # expr
    # (Starred, 'ctx'):                     (_put_one_default, None), # expr_context
    (Name, 'id'):                         (_put_one_identifier, None), # identifier
    # (Name, 'ctx'):                        (_put_one_default, None), # expr_context
    (List, 'elts'):                       (_put_one_tuple_list_or_set, None), # expr*
    # (List, 'ctx'):                        (_put_one_default, None), # expr_context
    (Tuple, 'elts'):                      (_put_one_tuple_list_or_set, None), # expr*
    # (Tuple, 'ctx'):                       (_put_one_default, None), # expr_context
    # (Slice, 'lower'):                     (_put_one_default, None), # expr?
    # (Slice, 'upper'):                     (_put_one_default, None), # expr?
    # (Slice, 'step'):                      (_put_one_default, None), # expr?
    # (comprehension, 'target'):            (_put_one_default, None), # expr            - Name or Tuple (maybe empty?)
    (comprehension, 'iter'):              (_put_one_expr, None), # expr
    # (comprehension, 'ifs'):               (_put_one_default, None), # expr*
    # (comprehension, 'is_async'):          (_put_one_default, None), # int
    # (ExceptHandler, 'type'):              (_put_one_default, None), # expr?
    # (ExceptHandler, 'name'):              (_put_one_default, None), # identifier?
    (ExceptHandler, 'body'):              (_put_one_stmtish, None), # stmt*
    # (arguments, 'posonlyargs'):           (_put_one_default, None), # arg*
    # (arguments, 'args'):                  (_put_one_default, None), # arg*
    # (arguments, 'defaults'):              (_put_one_default, None), # expr*
    # (arguments, 'vararg'):                (_put_one_default, None), # arg?
    # (arguments, 'kwonlyargs'):            (_put_one_default, None), # arg*
    # (arguments, 'kw_defaults'):           (_put_one_default, None), # expr*
    # (arguments, 'kwarg'):                 (_put_one_default, None), # arg?
    (arg, 'arg'):                         (_put_one_identifier, None), # identifier
    # (arg, 'annotation'):                  (_put_one_default, None), # expr?
    # (arg, 'type_comment'):                (_put_one_default, None), # string?
    # (keyword, 'arg'):                     (_put_one_default, None), # identifier?
    (keyword, 'value'):                   (_put_one_expr, None), # expr
    (alias, 'name'):                      (_put_one_identifier, None), # identifier
    # (alias, 'asname'):                    (_put_one_default, None), # identifier?
    (withitem, 'context_expr'):           (_put_one_expr, None), # expr
    # (withitem, 'optional_vars'):          (_put_one_default, None), # expr?
    # (match_case, 'pattern'):              (_put_one_default, None), # pattern
    # (match_case, 'guard'):                (_put_one_default, None), # expr?
    (match_case, 'body'):                 (_put_one_stmtish, None), # stmt*
    # (MatchValue, 'value'):                (_put_one_default, None), # expr            - limited values, Constant? Name becomes MatchAs
    # (MatchSingleton, 'value'):            (_put_one_default, None), # constant
    # (MatchSequence, 'patterns'):          (_put_one_default, None), # pattern*
    # (MatchMapping, 'keys'):               (_put_one_default, None), # expr*
    # (MatchMapping, 'patterns'):           (_put_one_default, None), # pattern*
    # (MatchMapping, 'rest'):               (_put_one_default, None), # identifier?
    # (MatchClass, 'cls'):                  (_put_one_default, None), # expr
    # (MatchClass, 'patterns'):             (_put_one_default, None), # pattern*
    # (MatchClass, 'kwd_attrs'):            (_put_one_default, None), # identifier*
    # (MatchClass, 'kwd_patterns'):         (_put_one_default, None), # pattern*
    # (MatchStar, 'name'):                  (_put_one_default, None), # identifier?
    # (MatchAs, 'pattern'):                 (_put_one_default, None), # pattern?
    # (MatchAs, 'name'):                    (_put_one_default, None), # identifier?
    # (MatchOr, 'patterns'):                (_put_one_default, None), # pattern*
    # (TypeIgnore, 'lineno'):               (_put_one_default, None), # int
    # (TypeIgnore, 'tag'):                  (_put_one_default, None), # string
    (TypeVar, 'name'):                    (_put_one_identifier, None), # identifier
    # (TypeVar, 'bound'):                   (_put_one_default, None), # expr?
    # (TypeVar, 'default_value'):           (_put_one_default, None), # expr?
    (ParamSpec, 'name'):                  (_put_one_identifier, '**'), # identifier
    # (ParamSpec, 'default_value'):         (_put_one_default, None), # expr?
    (TypeVarTuple, 'name'):               (_put_one_identifier, '*'), # identifier
    # (TypeVarTuple, 'default_value'):      (_put_one_default, None), # expr?
}


# TODO: finish these


from .fst import FST
