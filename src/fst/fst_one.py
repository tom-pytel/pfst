"""Misc lower level FST methods."""

import re
from ast import *
from typing import Any, Callable, Optional, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, type_param, TypeVar, ParamSpec, TypeVarTuple, TemplateStr, Interpolation

from .shared import STMTISH, Code, NodeTypeError, astfield, fstloc, srcwpos, _fixup_one_index, _next_find, _next_find_re


def _slice_indices(self: 'FST', idx: int, field: str, body: list[AST], to: Optional['FST']):
    """If a `to` parameter is passed then try to convert it to an index in the same field body list of `self`."""

    idx = _fixup_one_index(len(body), idx)

    if not to:
        return idx, idx + 1

    elif to.parent is self is not None and (pf := to.pfield).name == field:
        if (to_idx := pf.idx) < idx:
            raise ValueError("invalid 'to' node, must follow self in body")

        return idx, to_idx + 1

    raise NodeTypeError(f"invalid 'to' node")


# ----------------------------------------------------------------------------------------------------------------------
# get

def _get_one(self: 'FST', idx: int | None, field: str, cut: bool, **options) -> Optional['FST']:
    """Copy or cut (if possible) a node or non-node from a field of `self`."""

    ast    = self.a
    child  = getattr(ast, field)
    childa = child if idx is None else child[idx]

    if isinstance(childa, STMTISH):
        return self._get_slice_stmtish(*_slice_indices(self, idx, field, child, None), field, cut=cut, one=True,
                                       **options)

    childf = childa.f
    loc    = childf.pars(options.get('pars') is True)

    if not loc:
        raise ValueError('cannot copy node which does not have a location')

    fst = childf._make_fst_and_dedent(childf, copy_ast(childa), loc, docstr=options.get('docstr'))

    if cut:
        options['to'] = None

        self._put_one(None, idx, field, **options)

    if FST.get_option('fix', options):
        fst = fst._fix(inplace=True)

    return fst


# ----------------------------------------------------------------------------------------------------------------------
# put

_re_identifier = re.compile(r'[^\d\W]\w*')


def _code_as_identifier(code: Code) -> str | None:
    if isinstance(code, str):
        return code if is_valid_identifier(code) else None
    if isinstance(code, list):
        return code if len(code) == 1 and is_valid_identifier(code := code[0]) else None  # join without newlines to ignore one or two extraneous ones

    if isinstance(code, FST):
        code = code.a

    return code.id if isinstance(code, Name) else None


def _start_prefix_Return_value(self: 'FST') -> srcwpos:
    """The start position (right after 'return') and prefix src ('') for a value node for a Return."""

    return srcwpos((loc := self.loc).ln, loc.col + 6, '')


def _make_expr_fst(self: 'FST', code: Code | None, idx: int | None, field: str,
                   extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                   target: Union['FST', fstloc], ctx: type[expr_context], prefix: str  = '',
                   **options) -> tuple['FST', fstloc]:
    """Make an expression `FST` from `Code` for a field/idx containing an existing node creating a new one. Takes care
    of parenthesizing, indenting and offsetting."""

    put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)
    put_ast = put_fst.a

    if extra:
        if isinstance(extra, list):  # list means these types not allowed
            if isinstance(put_ast, tuple(extra)):
                raise NodeTypeError((f'cannot be one of ({", ".join(c.__name__ for c in extra)}) for '
                                     f'{self.a.__class__.__name__}.{field}{f"[{idx}]" if idx else ""}') +
                                    f', got {put_ast.__class__.__name__}')

        elif not isinstance(put_ast, extra):  # single AST type or tuple means only these allowed
            raise NodeTypeError((f'expecting a {extra.__name__} for {self.a.__class__.__name__}.{field}'
                                 if isinstance(extra, type) else
                                 f'expecting one of ({", ".join(c.__name__ for c in extra)}) for '
                                 f'{self.a.__class__.__name__}.{field}{f"[{idx}]" if idx else ""}') +
                                f', got {put_ast.__class__.__name__}')

    pars    = bool(FST.get_option('pars', options))
    delpars = pars or put_fst.is_parenthesized_tuple() is False  # need tuple check because otherwise location would be wrong after
    is_FST  = target.is_FST

    if precedence_require_parens(put_ast, self.a, field, idx):
        if not put_fst.is_atom() and (delpars or not is_FST or not target.pars(ret_npars=True)[1]):
            put_fst.parenthesize()

    elif pars:  # remove parens only if allowed to
        put_fst.unparenthesize()

    if prefix:
        put_fst.put_src([prefix], 0, 0, 0, 0, True)

    put_fst.indent_lns(self.get_indent(), docstr=options.get('docstr'))

    ln, col, _, _ = loc = target.pars(delpars) if target.is_FST else target
    dcol_offset   = self.root._lines[ln].c2b(col)

    put_fst.offset(0, 0, ln, dcol_offset)
    # self.put_src(put_lines, ln, col, end_ln, end_col, True, exclude=target)  # excluding an fstloc will do nothing
    set_ctx(put_ast, ctx)

    return put_fst, loc


def _put_one_expr_required(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST] | AST | None,
                           extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                           **options) -> Optional['FST']:
    """Put a single required expression. Can be standalone or as part of sequence."""

    if isinstance(child, list):
        if idx is None:
            raise IndexError(f'{self.a.__class__.__name__}.{field} needs an index')

        child = child[idx]

    elif idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')

    if code is None:
        raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field}{f"[{idx}]" if idx else ""}')
    if options.get('to'):
        raise NodeTypeError(f"cannot put with 'to' to {self.a.__class__.__name__}.{field}")

    if not child:
        raise ValueError(f'cannot replace nonexistent {self.a.__class__.__name__}.{field}{f"[{idx}]" if idx else ""}')



    childf = child.f
    ctx    = ((ctx := getattr(child, 'ctx', None)) and ctx.__class__) or Load

    put_fst, (ln, col, end_ln, end_col) = _make_expr_fst(self, code, idx, field, extra, childf, ctx, **options)

    self.put_src(put_fst._lines, ln, col, end_ln, end_col, True, exclude=childf)
    childf._set_ast(put_fst.a)

    return childf



    # put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)
    # put_ast = put_fst.a

    # if extra:
    #     if isinstance(extra, list):  # list means these types not allowed
    #         if isinstance(put_ast, tuple(extra)):
    #             raise NodeTypeError((f'cannot be one of ({", ".join(c.__name__ for c in extra)}) for '
    #                                  f'{self.a.__class__.__name__}.{field}{f"[{idx}]" if idx else ""}') +
    #                                 f', got {put_ast.__class__.__name__}')

    #     elif not isinstance(put_ast, extra):  # single AST type or tuple means only these allowed
    #         raise NodeTypeError((f'expecting a {extra.__name__} for {self.a.__class__.__name__}.{field}'
    #                              if isinstance(extra, type) else
    #                              f'expecting one of ({", ".join(c.__name__ for c in extra)}) for '
    #                              f'{self.a.__class__.__name__}.{field}{f"[{idx}]" if idx else ""}') +
    #                             f', got {put_ast.__class__.__name__}')

    # ast     = self.a
    # childf  = child.f
    # pars    = bool(FST.get_option('pars', options))
    # delpars = pars or put_fst.is_parenthesized_tuple() is False  # need tuple check because otherwise location would be wrong after
    # loc     = childf.pars(delpars)  # don't need exc_genexpr_solo=True here because guaranteed not to be this

    # if precedence_require_parens(put_ast, ast, field, idx):
    #     if not put_fst.is_atom() and (delpars or not childf.pars(ret_npars=True)[1]):
    #         put_fst.parenthesize()

    # elif pars:  # remove parens only if allowed to
    #     put_fst.unparenthesize()

    # put_fst.indent_lns(childf.get_indent(), docstr=options.get('docstr'))

    # ln, col, end_ln, end_col = loc

    # lines       = self.root._lines
    # put_lines   = put_fst._lines
    # dcol_offset = lines[ln].c2b(col)

    # put_fst.offset(0, 0, ln, dcol_offset)
    # self.put_src(put_lines, ln, col, end_ln, end_col, True, exclude=childf)
    # set_ctx(put_ast, ((ctx := getattr(child, 'ctx', None)) and ctx.__class__) or Load)
    # childf._set_ast(put_ast)

    # return put_ast.f


def _put_one_expr_optional(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                           extra: tuple[
                               Callable[['FST'], srcwpos],
                               tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                           ], **options) -> Optional['FST']:
    """Put new, replace or delete an optional expression. Only standalone"""

    if idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')
    if options.get('to'):
        raise NodeTypeError(f"cannot put with 'to' to {self.a.__class__.__name__}.{field}")

    start_prefix, required_extra = extra

    if code is None:
        if not child:  # delete nonexistent node, noop
            return None

    elif child:  # replace existing node
        return _put_one_expr_required(self, code, idx, field, child, required_extra, **options)

    ln, col, prefix = start_prefix(self)

    if code is None:  # delete existing node
        childf = child.f

        self.put_src(None, ln, col, childf.end_ln, childf.end_col, True)
        setattr(self.a, field, None)
        childf._unmake_fst_tree()

        return None

    # put new node

    prefix = f' {prefix} ' if prefix else ' '
    loc    = fstloc(ln, col, self.end_ln, self.end_col)

    put_fst, (ln, col, end_ln, end_col) = _make_expr_fst(self, code, idx, field, required_extra, loc, Load, prefix,
                                                         **options)

    self.put_src(put_fst._lines, ln, col, end_ln, end_col, True)
    self._make_fst_tree([put_fst := FST(put_fst.a, self, astfield(field))])
    put_fst.pfield.set(self.a, put_fst.a)

    return put_fst




    raise NotImplementedError



def _put_one_Dict_key(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST],
                      extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                      **options) -> Optional['FST']:
    """Allow for deleting or adding a `Dict` key value to change between `a: b` and `**b`."""

    return _put_one_expr_required(self, code, idx, field, child, extra, **options)


    # TODO: this


def _put_one_Compare_None(self: 'FST', code: Code | None, idx: int | None, field: str, child: None,
                          extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                          **options) -> Optional['FST']:

    """Put to combined [Compare.left, Compare.comparators] using this total indexing."""

    ast         = self.a
    comparators = ast.comparators
    idx         = _fixup_one_index(len(comparators) + 1, idx)

    if idx:
        field = 'comparators'
        idx   = idx - 1
        child = comparators

    else:
        field = 'left'
        idx   = None
        child = ast.left

    return _put_one_expr_required(self, code, idx, field, child, extra, **options)


def _put_one_Interpolation_value(self: 'FST', code: Code | None, idx: int | None, field: str, child: AST,
                                 extra: tuple[type[AST]] | list[type[AST]] | type[AST] | None,
                                 **options) -> Optional['FST']:
    """Put Interpolation.value. Do normal expr put and if successful copy source to `.str` attribute."""

    ret        = _put_one_expr_required(self, code, idx, field, child, extra, **options)
    self.a.str = self.get_src(*ret.loc)

    return ret


def _put_one_stmtish(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST], extra: None,
                     **options) -> Optional['FST']:
    """Put or delete a single statementish node to a list of them (body, orelse, handlers, finalbody or cases)."""

    self._put_slice_stmtish(code, *_slice_indices(self, idx, field, child, options.get('to')), field, True, **options)

    return None if code is None else getattr(self.a, field)[idx].f


def _put_one_tuple_list_or_set(self: 'FST', code: Code | None, idx: int | None, field: str, child: list[AST],
                               extra: None, **options) -> Optional['FST']:
    """Put or delete a single expression to a Tuple, List or Set elts."""

    self._put_slice_tuple_list_or_set(code, *_slice_indices(self, idx, field, child, options.get('to')), field, True,
                                      **options)

    return None if code is None else getattr(self.a, field)[idx].f


def _put_one_identifier_required(self: 'FST', code: Code | None, idx: int | None, field: str, child: str,
                                 extra: str | None, **options) -> str:
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

    return code


def _put_one(self: 'FST', code: Code | None, idx: int | None, field: str | None, **options) -> Optional['FST']:
    """Put new, replace or delete a node (or limited non-node) to a field of `self`."""

    ast   = self.a
    child = getattr(self.a, field) if field else None
    raw   = FST.get_option('raw', options)

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
                raise ValueError(f'cannot {"delete" if code is None else "replace"} {ast.__class__.__name__}.{field}')

    if isinstance(child, list):
        child = child[idx]

    # special raw cases, TODO: move into dedicated _put_raw or do via _PUT_ONE_RAW_HANDLERS

    is_dict = isinstance(ast, Dict)

    if field is None:  # maybe putting to special case field?
        if is_dict or isinstance(ast, MatchMapping):
            key = key.f if (key := ast.keys[idx]) else self._dict_key_or_mock_loc(key, ast.values[idx].f)
            end = (ast.values if is_dict else ast.patterns)[idx].f

            self._reparse_raw_loc(code, key.ln, key.col, end.end_ln, end.end_col)

            return self.repath()

        if isinstance(ast, Compare):
            idx   = _fixup_one_index(len(ast.comparators) + 1, idx)  # need to do this because of compound body including 'left'
            child = ast.comparators[idx - 1] if idx else ast.left
            # field_, idx = ('comparators', idx - 1) if idx else ('left', None)

    if is_dict and field == 'keys' and (keys := ast.keys)[idx] is None:  # '{**d}' with key=None
        start_loc = self._dict_key_or_mock_loc(keys[idx], ast.values[idx].f)

        ln, col, end_ln, end_col = start_loc.loc

        self.put_src([': '], ln, col, end_ln, end_col)
        self._reparse_raw_loc(code, ln, col, ln, col)

        return self.repath()

    ret = child.f._reparse_raw_node(code, **options)

    return None if code is None else ret


# TODO: finish these

_PUT_ONE_HANDLERS = {
    (Module, 'body'):                     (_put_one_stmtish, None), # stmt*
    (Interactive, 'body'):                (_put_one_stmtish, None), # stmt*
    (Expression, 'body'):                 (_put_one_expr_required, None), # expr
    # (FunctionDef, 'decorator_list'):      (_put_one_default, None), # expr*                                           - slice
    (FunctionDef, 'name'):                (_put_one_identifier_required, 'def'), # identifier
    # (FunctionDef, 'type_params'):         (_put_one_default, None), # type_param*                                     - slice
    # (FunctionDef, 'args'):                (_put_one_default, None), # arguments                                       - need special parse
    # (FunctionDef, 'returns'):             (_put_one_default, None), # expr?                                           - SPECIAL LOCATION OPTIONAL TAIL: '->'                                           - SPECIAL LOCATION CASE!
    (FunctionDef, 'body'):                (_put_one_stmtish, None), # stmt*
    # (AsyncFunctionDef, 'decorator_list'): (_put_one_default, None), # expr*                                           - slice
    (AsyncFunctionDef, 'name'):           (_put_one_identifier_required, 'def'), # identifier
    # (AsyncFunctionDef, 'type_params'):    (_put_one_default, None), # type_param*                                     - slice
    # (AsyncFunctionDef, 'args'):           (_put_one_default, None), # arguments                                       - need special parse
    # (AsyncFunctionDef, 'returns'):        (_put_one_default, None), # expr?                                           - SPECIAL LOCATION OPTIONAL TAIL: '->'
    (AsyncFunctionDef, 'body'):           (_put_one_stmtish, None), # stmt*
    # (ClassDef, 'decorator_list'):         (_put_one_default, None), # expr*                                           - slice
    (ClassDef, 'name'):                   (_put_one_identifier_required, 'class'), # identifier
    # (ClassDef, 'type_params'):            (_put_one_default, None), # type_param*                                     - slice
    # (ClassDef, 'bases'):                  (_put_one_default, None), # expr*                                           - slice
    # (ClassDef, 'keywords'):               (_put_one_default, None), # keyword*
    (ClassDef, 'body'):                   (_put_one_stmtish, None), # stmt*
    (Return, 'value'):                    (_put_one_expr_optional, (_start_prefix_Return_value, None)), # expr?         - OPTIONAL TAIL: ''
    # (Delete, 'targets'):                  (_put_one_default, None), # expr*                                           - slice
    # (Assign, 'targets'):                  (_put_one_default, None), # expr*                                           - slice
    (Assign, 'value'):                    (_put_one_expr_required, None), # expr
    (TypeAlias, 'name'):                  (_put_one_expr_required, Name), # expr
    # (TypeAlias, 'type_params'):           (_put_one_default, None), # type_param*                                     - slice
    (TypeAlias, 'value'):                 (_put_one_expr_required, None), # expr
    (AugAssign, 'target'):                (_put_one_expr_required, (Name, Attribute, Subscript)), # expr
    # (AugAssign, 'op'):                    (_put_one_default, None), # operator
    (AugAssign, 'value'):                 (_put_one_expr_required, None), # expr
    (AnnAssign, 'target'):                (_put_one_expr_required, (Name, Attribute, Subscript)), # expr
    (AnnAssign, 'annotation'):            (_put_one_expr_required, [Lambda, Yield, YieldFrom, Await, NamedExpr]), # expr
    # (AnnAssign, 'value'):                 (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: '='
    # (AnnAssign, 'simple'):                (_put_one_default, None), # int
    (For, 'target'):                      (_put_one_expr_required, (Name, Tuple, List)), # expr
    (For, 'iter'):                        (_put_one_expr_required, None), # expr
    (For, 'body'):                        (_put_one_stmtish, None), # stmt*
    (For, 'orelse'):                      (_put_one_stmtish, None), # stmt*
    (AsyncFor, 'target'):                 (_put_one_expr_required, (Name, Tuple, List)), # expr
    (AsyncFor, 'iter'):                   (_put_one_expr_required, None), # expr
    (AsyncFor, 'body'):                   (_put_one_stmtish, None), # stmt*
    (AsyncFor, 'orelse'):                 (_put_one_stmtish, None), # stmt*
    (While, 'test'):                      (_put_one_expr_required, None), # expr
    (While, 'body'):                      (_put_one_stmtish, None), # stmt*
    (While, 'orelse'):                    (_put_one_stmtish, None), # stmt*
    (If, 'test'):                         (_put_one_expr_required, None), # expr
    (If, 'body'):                         (_put_one_stmtish, None), # stmt*
    (If, 'orelse'):                       (_put_one_stmtish, None), # stmt*
    # (With, 'items'):                      (_put_one_default, None), # withitem*
    (With, 'body'):                       (_put_one_stmtish, None), # stmt*
    # (AsyncWith, 'items'):                 (_put_one_default, None), # withitem*
    (AsyncWith, 'body'):                  (_put_one_stmtish, None), # stmt*
    (Match, 'subject'):                   (_put_one_expr_required, None), # expr
    (Match, 'cases'):                     (_put_one_stmtish, None), # match_case*
    # (Raise, 'exc'):                       (_put_one_default, None), # expr?                                           - CONTINGENT OPTIONAL MIDDLE: ''
    # (Raise, 'cause'):                     (_put_one_default, None), # expr?                                           - CONTINGENT OPTIONAL TAIL: 'from'
    (Try, 'body'):                        (_put_one_stmtish, None), # stmt*
    (Try, 'handlers'):                    (_put_one_stmtish, None), # excepthandler*
    (Try, 'orelse'):                      (_put_one_stmtish, None), # stmt*
    (Try, 'finalbody'):                   (_put_one_stmtish, None), # stmt*
    (TryStar, 'body'):                    (_put_one_stmtish, None), # stmt*
    (TryStar, 'handlers'):                (_put_one_stmtish, None), # excepthandler*
    (TryStar, 'orelse'):                  (_put_one_stmtish, None), # stmt*
    (TryStar, 'finalbody'):               (_put_one_stmtish, None), # stmt*
    (Assert, 'test'):                     (_put_one_expr_required, None), # expr
    # (Assert, 'msg'):                      (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: ''
    # (Import, 'names'):                    (_put_one_default, None), # alias*
    # (ImportFrom, 'module'):               (_put_one_default, None), # identifier?
    # (ImportFrom, 'names'):                (_put_one_default, None), # alias*
    # (ImportFrom, 'level'):                (_put_one_default, None), # int?
    # (Global, 'names'):                    (_put_one_default, None), # identifier*
    # (Nonlocal, 'names'):                  (_put_one_default, None), # identifier*
    (Expr, 'value'):                      (_put_one_expr_required, None), # expr
    # (BoolOp, 'op'):                       (_put_one_default, None), # boolop
    # (BoolOp, 'values'):                   (_put_one_default, None), # expr*                                           - slice
    (NamedExpr, 'target'):                (_put_one_expr_required, Name), # expr
    (NamedExpr, 'value'):                 (_put_one_expr_required, None), # expr
    (BinOp, 'left'):                      (_put_one_expr_required, None), # expr
    # (BinOp, 'op'):                        (_put_one_default, None), # operator
    (BinOp, 'right'):                     (_put_one_expr_required, None), # expr
    # (UnaryOp, 'op'):                      (_put_one_default, None), # unaryop
    (UnaryOp, 'operand'):                 (_put_one_expr_required, None), # expr
    # (Lambda, 'args'):                     (_put_one_default, None), # arguments                                       - need special parse
    (Lambda, 'body'):                     (_put_one_expr_required, None), # expr
    (IfExp, 'body'):                      (_put_one_expr_required, None), # expr
    (IfExp, 'test'):                      (_put_one_expr_required, None), # expr
    (IfExp, 'orelse'):                    (_put_one_expr_required, None), # expr
    (Dict, 'keys'):                       (_put_one_expr_required, None), # expr*                                       - handle special key=None?
    (Dict, 'values'):                     (_put_one_expr_required, None), # expr*
    (Set, 'elts'):                        (_put_one_tuple_list_or_set, None), # expr*
    (ListComp, 'elt'):                    (_put_one_expr_required, None), # expr
    # (ListComp, 'generators'):             (_put_one_default, None), # comprehension*
    (SetComp, 'elt'):                     (_put_one_expr_required, None), # expr
    # (SetComp, 'generators'):              (_put_one_default, None), # comprehension*
    (DictComp, 'key'):                    (_put_one_Dict_key, None), # expr                                             TODO: this!
    (DictComp, 'value'):                  (_put_one_expr_required, None), # expr
    # (DictComp, 'generators'):             (_put_one_default, None), # comprehension*
    (GeneratorExp, 'elt'):                (_put_one_expr_required, None), # expr
    # (GeneratorExp, 'generators'):         (_put_one_default, None), # comprehension*
    (Await, 'value'):                     (_put_one_expr_required, None), # expr
    # (Yield, 'value'):                     (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: ''
    (YieldFrom, 'value'):                 (_put_one_expr_required, None), # expr
    (Compare, 'left'):                    (_put_one_expr_required, None), # expr
    # (Compare, 'ops'):                     (_put_one_default, None), # cmpop*
    (Compare, 'comparators'):             (_put_one_expr_required, None), # expr*
    (Compare, None):                      (_put_one_Compare_None, None), # expr*
    (Call, 'func'):                       (_put_one_expr_required, None), # expr
    # (Call, 'args'):                       (_put_one_default, None), # expr*                                           - slice
    # (Call, 'keywords'):                   (_put_one_default, None), # keyword*                                        - slice
    (FormattedValue, 'value'):            (_put_one_expr_required, None), # expr
    # (FormattedValue, 'format_spec'):      (_put_one_default, None), # expr?
    # (FormattedValue, 'conversion'):       (_put_one_default, None), # int
    (Interpolation, 'value'):             (_put_one_Interpolation_value, None), # expr
    # (Interpolation, 'constant'):          (_put_one_default, None), # str
    # (Interpolation, 'conversion'):        (_put_one_default, None), # int
    # (Interpolation, 'format_spec'):       (_put_one_default, None), # expr?
    # (JoinedStr, 'values'):                (_put_one_default, None), # expr*                                           - ??? no location on py < 3.12
    # (TemplateStr, 'values'):              (_put_one_default, None), # expr*                                           - ??? no location on py < 3.12
    # (Constant, 'value'):                  (_put_one_default, None), # constant                                        - can do via restricted expr Constant
    # (Constant, 'kind'):                   (_put_one_default, None), # string?
    (Attribute, 'value'):                 (_put_one_expr_required, None), # expr
    # (Attribute, 'attr'):                  (_put_one_default, None), # identifier                                      - after the "value."
    (Subscript, 'value'):                 (_put_one_expr_required, None), # expr
    # (Subscript, 'slice'):                 (_put_one_default, None), # expr
    (Starred, 'value'):                   (_put_one_expr_required, None), # expr
    (Name, 'id'):                         (_put_one_identifier_required, None), # identifier
    (List, 'elts'):                       (_put_one_tuple_list_or_set, None), # expr*
    (Tuple, 'elts'):                      (_put_one_tuple_list_or_set, None), # expr*
    # (Slice, 'lower'):                     (_put_one_default, None), # expr?
    # (Slice, 'upper'):                     (_put_one_default, None), # expr?
    # (Slice, 'step'):                      (_put_one_default, None), # expr?
    (comprehension, 'target'):            (_put_one_expr_required, (Name, Tuple, List)), # expr
    (comprehension, 'iter'):              (_put_one_expr_required, None), # expr
    # (comprehension, 'ifs'):               (_put_one_default, None), # expr*                                           - slice
    # (comprehension, 'is_async'):          (_put_one_default, None), # int
    # (ExceptHandler, 'type'):              (_put_one_default, None), # expr?
    # (ExceptHandler, 'name'):              (_put_one_default, None), # identifier?
    (ExceptHandler, 'body'):              (_put_one_stmtish, None), # stmt*
    # (arguments, 'posonlyargs'):           (_put_one_default, None), # arg*
    # (arguments, 'args'):                  (_put_one_default, None), # arg*
    (arguments, 'defaults'):              (_put_one_expr_required, None), # expr*
    # (arguments, 'vararg'):                (_put_one_default, None), # arg?
    # (arguments, 'kwonlyargs'):            (_put_one_default, None), # arg*
    # (arguments, 'kw_defaults'):           (_put_one_default, None), # expr*                                           - can have None with special rules
    # (arguments, 'kwarg'):                 (_put_one_default, None), # arg?
    (arg, 'arg'):                         (_put_one_identifier_required, None), # identifier
    # (arg, 'annotation'):                  (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: ':' - [Lambda, Yield, YieldFrom, Await, NamedExpr]
    # (keyword, 'arg'):                     (_put_one_default, None), # identifier?
    (keyword, 'value'):                   (_put_one_expr_required, None), # expr
    (alias, 'name'):                      (_put_one_identifier_required, None), # identifier
    # (alias, 'asname'):                    (_put_one_default, None), # identifier?
    (withitem, 'context_expr'):           (_put_one_expr_required, None), # expr
    # (withitem, 'optional_vars'):          (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: 'as' - Name
    # (match_case, 'pattern'):              (_put_one_default, None), # pattern
    # (match_case, 'guard'):                (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: 'if'
    (match_case, 'body'):                 (_put_one_stmtish, None), # stmt*
    # (MatchValue, 'value'):                (_put_one_default, None), # expr                                            - limited values, Constant? Name becomes MatchAs
    # (MatchSingleton, 'value'):            (_put_one_default, None), # constant
    # (MatchSequence, 'patterns'):          (_put_one_default, None), # pattern*
    (MatchMapping, 'keys'):               (_put_one_expr_required, (Constant, Attribute)), # expr*                      TODO: XXX are there any others allowed?
    # (MatchMapping, 'patterns'):           (_put_one_default, None), # pattern*
    # (MatchMapping, 'rest'):               (_put_one_default, None), # identifier?
    (MatchClass, 'cls'):                  (_put_one_expr_required, (Name, Attribute)), # expr
    # (MatchClass, 'patterns'):             (_put_one_default, None), # pattern*
    # (MatchClass, 'kwd_attrs'):            (_put_one_default, None), # identifier*
    # (MatchClass, 'kwd_patterns'):         (_put_one_default, None), # pattern*
    # (MatchStar, 'name'):                  (_put_one_default, None), # identifier?
    # (MatchAs, 'pattern'):                 (_put_one_default, None), # pattern?
    # (MatchAs, 'name'):                    (_put_one_default, None), # identifier?
    # (MatchOr, 'patterns'):                (_put_one_default, None), # pattern*
    (TypeVar, 'name'):                    (_put_one_identifier_required, None), # identifier
    # (TypeVar, 'bound'):                   (_put_one_default, None), # expr?                                           - OPTIONAL MIDDLE: ':'
    # (TypeVar, 'default_value'):           (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: '='
    (ParamSpec, 'name'):                  (_put_one_identifier_required, '**'), # identifier
    # (ParamSpec, 'default_value'):         (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: '='
    (TypeVarTuple, 'name'):               (_put_one_identifier_required, '*'), # identifier
    # (TypeVarTuple, 'default_value'):      (_put_one_default, None), # expr?                                           - OPTIONAL TAIL: '='


    # NOT DONE:
    # =========
    # (Module, 'type_ignores'):             (_put_one_default, None), # type_ignore*

    # (FunctionType, 'argtypes'):           (_put_one_default, None), # expr*
    # (FunctionType, 'returns'):            (_put_one_default, None), # expr

    # (FunctionDef, 'type_comment'):        (_put_one_default, None), # string?
    # (AsyncFunctionDef, 'type_comment'):   (_put_one_default, None), # string?
    # (Assign, 'type_comment'):             (_put_one_default, None), # string?
    # (For, 'type_comment'):                (_put_one_default, None), # string?
    # (AsyncFor, 'type_comment'):           (_put_one_default, None), # string?
    # (With, 'type_comment'):               (_put_one_default, None), # string?
    # (AsyncWith, 'type_comment'):          (_put_one_default, None), # string?
    # (arg, 'type_comment'):                (_put_one_default, None), # string?

    # (Attribute, 'ctx'):                   (_put_one_default, None), # expr_context
    # (Subscript, 'ctx'):                   (_put_one_default, None), # expr_context
    # (Starred, 'ctx'):                     (_put_one_default, None), # expr_context
    # (Name, 'ctx'):                        (_put_one_default, None), # expr_context
    # (List, 'ctx'):                        (_put_one_default, None), # expr_context
    # (Tuple, 'ctx'):                       (_put_one_default, None), # expr_context

    # (TypeIgnore, 'lineno'):               (_put_one_default, None), # int
    # (TypeIgnore, 'tag'):                  (_put_one_default, None), # string
}

# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = ['_get_one', '_put_one']


from .fst import FST
