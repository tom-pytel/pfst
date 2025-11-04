"""Get and put slice. Some slices can use normal AST types and others need special custom fst AST container classes.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from typing import Any, Callable, Literal, Mapping, NamedTuple, Union

from . import fst

from .asttypes import (
    AST,
    Assign,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    BoolOp,
    Call,
    ClassDef,
    Compare,
    Del,
    Delete,
    Dict,
    DictComp,
    ExceptHandler,
    Expr,
    For,
    FunctionDef,
    GeneratorExp,
    Global,
    If,
    Import,
    ImportFrom,
    Interactive,
    JoinedStr,
    List,
    ListComp,
    Load,
    Match,
    MatchAs,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    Module,
    Name,
    NamedExpr,
    Nonlocal,
    Set,
    SetComp,
    Slice,
    Starred,
    Store,
    Try,
    Tuple,
    While,
    With,
    Yield,
    YieldFrom,
    comprehension,
    match_case,
    TryStar,
    TypeAlias,
    TemplateStr,
    expr_context,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _aliases,
    _withitems,
    _type_params,
)

from .astutil import re_identifier, bistr, is_valid_target, is_valid_del_target, reduce_ast, set_ctx, copy_ast

from .common import (
    PYLT11,
    PYGE14,
    Self,
    NodeError,
    astfield,
    fstloc,
    next_frag,
    prev_find,
    next_find,
    next_find_re,
)

from .parsex import unparse

from .code import (
    Code,
    code_as_expr,
    code_as_expr_all,
    code_as_expr_arglike,
    code_as_Assign_targets,
    code_as_alias,
    code_as_aliases,
    code_as_Import_name,
    code_as_Import_names,
    code_as_ImportFrom_name,
    code_as_ImportFrom_names,
    code_as_withitem,
    code_as_withitems,
    code_as_pattern,
    code_as_type_param,
    code_as_type_params,
    code_as__expr_arglikes,
)

from .traverse import prev_bound

from .locations import (
    loc_With_items_pars,
    loc_ImportFrom_names_pars,
    loc_ClassDef_bases_pars,
    loc_Call_pars,
    loc_TypeAlias_type_params_brackets,
    loc_ClassDef_type_params_brackets,
    loc_FunctionDef_type_params_brackets,
    loc_Global_Nonlocal_names,
)

from .fst_misc import (
    new_empty_tuple,
    new_empty_set_star,
    new_empty_set_call,
    new_empty_set_curlies,
    get_option_overridable,
)

from .fst_slice_old import _get_slice_stmtish, _put_slice_stmtish
from .slice import get_slice_sep, put_slice_sep_begin, put_slice_sep_end, _locs_first_and_last

__all__ = ['_get_slice', '_put_slice', 'is_slice_compatible']


# * Keep src same.
# * Use normal AST and src where possible.
# * Delimiters where would match ast.unparse().
# * Special unparse where needed.


#   (!) SPECIAL SLICE, (?) sometimes SPECIAL SLICE???
#   | (N)ormal container, (S)equence container
#   | | Separator (trailing)
#   | | |  Prefix (leaading)
#   | | |  |  Delimiters
#   | | |  |  |
#                                                                             .
# *   N ,     ()   (Tuple, 'elts')                         # expr*            -> Tuple                      _parse_expr_sliceelts
# *   N ,     []   (List, 'elts')                          # expr*            -> List                       _parse_expr / restrict seq
# * ? N ,     {}   (Set, 'elts')                           # expr*            -> Set                        _parse_expr / restrict seq
#                                                                             .
# *   N ,     {}   (Dict, 'keys':'values')                 # expr:expr*       -> Dict                       _parse_expr / restrict dict
#                                                                             .
# *   N ,     []   (MatchSequence, 'patterns'):            # pattern*         -> MatchSequence              _parse_pattern / restrict MatchSequence
# *   N ,     {}   (MatchMapping, 'keys':'patterns'):      # expr:pattern*    -> MatchMapping               _parse_pattern / restrict MatchMapping
#                                                                             .
# * ? N |          (MatchOr, 'patterns'):                  # pattern*         -> MatchOr                    _parse_pattern / restrict MatchOr
#                                                                             .
#     S ,          (MatchClass, 'patterns'):               # pattern*         -> MatchSequence              _parse_pattern / restrict MatchSequence  - allow empty pattern?
#                                                                             .
#                                                                             .
# *   S ,          (ClassDef, 'bases'):                    # expr*            -> Tuple[expr_arglike]        _parse__expr_arglikes  - keywords and Starred bases can mix
# *   S ,          (Call, 'args'):                         # expr*            -> Tuple[expr_arglike]        _parse__expr_arglikes  - keywords and Starred args can mix
#                                                                             .
# *   S ,          (Delete, 'targets'):                    # expr*            -> Tuple[target]              _parse_expr / restrict del_targets
# * ! N =          (Assign, 'targets'):                    # expr*            -> _Assign_targets            _parse__Assign_targets
#                                                                             .
#                                                                             .
# *   S ,          (Global, 'names'):                      # identifier*,     -> Tuple[Name]                _parse_expr / restrict Names   - no trailing commas, unparenthesized
# *   S ,          (Nonlocal, 'names'):                    # identifier*,     -> Tuple[Name]                _parse_expr / restrict Names   - no trailing commas, unparenthesized
#                                                                             .
#                                                                             .
#   ! S ,          (ClassDef, 'keywords'):                 # keyword*         -> _keywords                  _parse__keywords  - keywords and Starred bases can mix
#   ! S ,          (Call, 'keywords'):                     # keyword*         -> _keywords                  _parse__keywords  - keywords and Starred args can mix
#                                                                             .
# * ! S ,          (FunctionDef, 'type_params'):           # type_param*      -> _type_params               _parse__type_params
# * ! S ,          (AsyncFunctionDef, 'type_params'):      # type_param*      -> _type_params               _parse__type_params
# * ! S ,          (ClassDef, 'type_params'):              # type_param*      -> _type_params               _parse__type_params
# * ! S ,          (TypeAlias, 'type_params'):             # type_param*      -> _type_params               _parse__type_params
#                                                                             .
# * ! S ,          (With, 'items'):                        # withitem*        -> _withitems                 _parse__withitems               - no trailing commas
# * ! S ,          (AsyncWith, 'items'):                   # withitem*        -> _withitems                 _parse__withitems               - no trailing commas
#                                                                             .
# * ! S ,          (Import, 'names'):                      # alias*           -> _aliases                   _parse__aliases_dotted          - no trailing commas
# * ! S ,          (ImportFrom, 'names'):                  # alias*           -> _aliases                   _parse__aliases_star            - no trailing commas
#                                                                             .
#                                                                             .
#   ! S ' '        (ListComp, 'generators'):               # comprehension*   -> _comprehensions            _parse__comprehensions
#   ! S ' '        (SetComp, 'generators'):                # comprehension*   -> _comprehensions            _parse__comprehensions
#   ! S ' '        (DictComp, 'generators'):               # comprehension*   -> _comprehensions            _parse__comprehensions
#   ! S ' '        (GeneratorExp, 'generators'):           # comprehension*   -> _comprehensions            _parse__comprehensions
#                                                                             .
#   ! S    if      (comprehension, 'ifs'):                 # expr*            -> _comprehension_ifs         _parse__comprehension_ifs
#                                                                             .
#   ! S    @       (FunctionDef, 'decorator_list'):        # expr*            -> _decorator_list            _parse__decorator_list
#   ! S    @       (AsyncFunctionDef, 'decorator_list'):   # expr*            -> _decorator_list            _parse__decorator_list
#   ! S    @       (ClassDef, 'decorator_list'):           # expr*            -> _decorator_list            _parse__decorator_list
#                                                                             .
#                                                                             .
#     N    op      (Compare, 'ops':'comparators'):         # cmpop:expr*      -> _ops_comparators           _parse__ops_comparators / restrict expr or Compare
#                                                                             .
#     N ao         (BoolOp, 'values'):                     # expr*            -> BoolOp                     _parse_expr / restrict BoolOp  - interchangeable between and / or
#                                                                             .
#                                                                             .
#                  (JoinedStr, 'values'):                  # Constant|FormattedValue*  -> JoinedStr
#                  (TemplateStr, 'values'):                # Constant|Interpolation*   -> TemplateStr


# --- NOT CONTIGUOUS --------------------------------

# (arguments, 'posonlyargs'):           # arg*  - problematic because of defaults
# (arguments, 'args'):                  # arg*  - problematic because of defaults

# (arguments, 'kwonlyargs'):            # arg*  - maybe do as two-element, but is new type of two-element where the second element can be None
# (arguments, 'kw_defaults'):           # arg*

# could do argmnents slice as arguments instance (lots of logic needed on put)?

# (MatchClass, 'kwd_attrs'):            # identifier*  - maybe do as two-element
# (MatchClass, 'kwd_patterns'):         # pattern*


# ----------------------------------------------------------------------------------------------------------------------

def _fixup_slice_indices(len_: int, start: int, stop: int) -> tuple[int, int]:
    """Clip slice indices to slice range allowing first negative range to map into positive range. Greater negative
    indices clip to 0."""

    if start is None:
        start = 0
    elif start == 'end':
        start = len_
    elif start < 0:
        start = max(0, start + len_)
    elif start > len_:
        start = len_

    if stop is None:
        stop = len_
    elif stop < 0:
        stop = max(0, stop + len_)
    elif stop > len_:
        stop = len_

    if stop < start:
        raise ValueError('start index must precede stop index')

    return start, stop


def _get_norm_option(override_option: str, norm_option: str, options: Mapping[str, Any]) -> bool | str:
    if (set_norm := get_option_overridable('norm', override_option, options)) is not True:
        return set_norm

    return fst.FST.get_option(norm_option, options)


def _bound_Delete_targets(self: fst.FST, start: int = 0, loc_first: fst.FST | None = None) -> tuple[int, int, int, int]:
    body = self.a.targets

    _, _, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    elif body:
        bound_ln, bound_col, _, _ = loc_first or body[0].f.pars()
    else:
        bound_ln = bound_end_ln
        bound_col = bound_end_col

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _bound_Assign_targets(self: fst.FST, start: int = 0, loc_first: fst.FST | None = None) -> tuple[int, int, int, int]:
    body = (ast := self.a).targets

    bound_end_ln, bound_end_col, _, _ = ast.value.f.pars()

    if bound_end_col and self.root._lines[bound_end_ln][bound_end_col - 1].isspace():  # leave space between end of bound and start of value so that we don't get stuff like 'a =b'
        bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    elif body:
        bound_ln, bound_col, _, _ = loc_first or body[0].f.pars()
    else:
        bound_ln = bound_end_ln
        bound_col = bound_end_col

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _maybe_fix_Assign_target0(self: fst.FST) -> None:
    """If `Assign` has `target`s and first target does not start at same location as `self` then delete everything in
    between so that it starts at `self`."""

    if targets := self.a.targets:
        t0_ln, t0_col, _, _ = targets[0].f.pars()
        self_ln, self_col, _, _ = self.loc

        if t0_col != self_col or t0_ln != self_ln:
            self._put_src(None, self_ln, self_col, t0_ln, t0_col, False)


def _maybe_fix_Set(self: fst.FST, norm: bool | str = True) -> None:
    # assert isinstance(self.a, Set)

    if norm and not (a := self.a).elts:
        if norm == 'call':
            ast, src = new_empty_set_call(a.lineno, a.col_offset, as_fst=False)
        else:  # True, 'star', 'both'
            ast, src = new_empty_set_star(a.lineno, a.col_offset, as_fst=False)

        ln, col, end_ln, end_col = self.loc

        self._put_src(src, ln, col, end_ln, end_col, True)
        self._set_ast(ast)


def _maybe_fix_MatchSequence(self: fst.FST, delims: Literal['', '[]', '()'] | None = None) -> str:
    # assert isinstance(self.a, MatchSequence)

    if delims is None:
        delims = self._is_delimited_matchseq()

    if len(body := self.a.patterns) == 1 and not delims.startswith('['):
        self._maybe_ins_separator((f := body[0].f).end_ln, f.end_col, False, self.end_ln, self.end_col - bool(delims))

    if not delims:
        return self._maybe_fix_undelimited_seq(body, '[]')

    return delims


def _update_loc_up_parents(self: fst.FST, lineno: int, col_offset: int, end_lineno: int, end_col_offset: int) -> None:
    """Change own location and walk up parent chain changing any start or end locations which coincide with our own old
    location to the new one."""

    ast = self.a
    old_lineno = ast.lineno
    old_col_offset = ast.col_offset
    old_end_lineno = ast.end_lineno
    old_end_col_offset = ast.end_col_offset
    ast.lineno = lineno
    ast.col_offset = col_offset
    ast.end_lineno = end_lineno
    ast.end_col_offset = end_col_offset

    self._touch()

    while self := self.parent:
        if (self_end_col_offset := getattr(a := self.a, 'end_col_offset', None)) is None:
            break

        if n := self_end_col_offset == old_end_col_offset and a.end_lineno == old_end_lineno:  # only change if matches old location
            a.end_lineno = end_lineno
            a.end_col_offset = end_col_offset

        if a.col_offset == old_col_offset and a.lineno == old_lineno:
            a.lineno = lineno
            a.col_offset = col_offset

        elif not n:
            break

        self._touch()

    if self:
        self._touchall(True, True, False)


def _maybe_fix_MatchOr(self: fst.FST, norm: bool | str = False) -> None:
    """Maybe fix a `MatchOr` object that may have the wrong location. Will do nothing to a zero-length `MatchOr` and
    will convert a length 1 `MatchOr` to just its single element if `norm` is true.

    **WARNING!** This is currently expecting to be called from slice operations with specific conditions, not guaranteed
    will work on any-old `MatchOr`.
    """

    # assert isinstance(self.a, MatchOr)

    if not (patterns := self.a.patterns):
        return

    lines = self.root._lines
    did_par = False

    if not (is_root := self.is_root):  # if not root then it needs ot be fixed here
        if not self._is_enclosed_or_line() and not self._is_enclosed_in_parents():
            self._parenthesize_grouping()  # we do this instead or _sanitize() to keep any trivia, and we do it first to make sure we don't introduce any unenclosed newlines

            did_par = True

    if (len_patterns := len(patterns)) == 1 and norm:
        pat0 = patterns[0]

        del patterns[0]

        self._set_ast(pat0, True)

    else:
        ln, col, end_ln, end_col = patterns[0].f.pars()

        if len_patterns > 1:
            _, _, end_ln, end_col = patterns[-1].f.pars()

        col_offset = lines[ln].c2b(col)
        end_col_offset = lines[end_ln].c2b(end_col)

        _update_loc_up_parents(self, ln + 1, col_offset, end_ln + 1, end_col_offset)

    if is_root:
        if not self._is_enclosed_or_line() and not self._is_enclosed_in_parents():
            self._parenthesize_grouping(False)

            did_par = True

    if not did_par:
        self._maybe_fix_joined_alnum(*self.loc)


def _maybe_fix_stmt_end(
    self: fst.FST, end_lineno: int, end_col_offset: int, old_end_lineno: int, old_end_col_offset: int
) -> None:
    """Fix end of statement that was modified. This sets new end position in self and parents if they originally ended
    on this statement and deals with trailing semicolon issues."""

    self._set_end_pos(end_lineno, end_col_offset, old_end_lineno, old_end_col_offset)

    lines = self.root._lines

    if not (parent := self.parent):  # end bound is end of source
        bound_end_ln = len(lines) - 1
        bound_end_col = len(lines[-1])

    elif (next_idx := (pfield := self.pfield).idx + 1) < len(parent_body := getattr(parent.a, pfield.name)):  # end bound is beginning of next statement
        bound_end_ln, bound_end_col, _, _ = parent_body[next_idx].f.bloc
    else:  # end bound is end of parent
        _, _, bound_end_ln, bound_end_col = parent.bloc

    _, _, bound_ln, bound_col = self.bloc

    if bound_end_ln == bound_ln:  # if bound ends on same line as starts then we are done because there can not be a trailing semicolon on a different line
        return

    if not (semi := next_find(lines, bound_ln + 1, 0, bound_end_ln, bound_end_col, ';', True)):
        return

    # found a trailing semicolon on a different line, can't let that stand, technically there could be line continuations between us and it that were already there before the operation, but whatever

    # TODO: this is the quick and easy way, the better way to preserve possible comment would be to remove semicolon and adjust start position of any trailing statements, but that involves checking line continuations and possibly dealing with normalizing a block statement which is all semicoloned statements

    semi_ln, semi_col = semi
    semi_col = min(semi_col, len(self._get_indent()))  # try to preserve original space before semicolon, silly, yes

    self._put_src(None, bound_ln, bound_col, semi_ln, semi_col, False)


# ----------------------------------------------------------------------------------------------------------------------
# get

def _locs_and_bound_get(
    self: fst.FST, start: int, stop: int, body: list[AST], body2: list[AST], off: int
) -> tuple[fstloc, fstloc, int, int, int, int]:
    """Get the location of the first and last elemnts (assumed present) and the bounding location of a one or
    two-element sequence. The start bounding location must be past the ante-first element if present, otherwise start
    of self past any delimiters. The end bounding location must be end of self before any delimiters.

    **Returns:**
    - `(loc of first element, loc of last element, bound_ln, bound_col, bound_end_ln, bound_end_col)`
    """

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_end_col -= off

    if start:
        _, _, bound_ln, bound_col = body2[start - 1].f.pars()
    else:
        bound_col += off

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body2)

    return loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col


def _cut_or_copy_asts(start: int, stop: int, field: str, cut: bool, body: list[AST]) -> list[AST]:
    if not cut:
        asts = [copy_ast(body[i]) for i in range(start, stop)]

    else:
        asts = body[start : stop]

        del body[start : stop]

        for i in range(start, len(body)):
            body[i].f.pfield = astfield(field, i)

    return asts


def _cut_or_copy_asts2(
    start: int, stop: int, field: str, field2: str, cut: bool, body: list[AST], body2: list[AST]
) -> tuple[list[AST], list[AST]]:
    if not cut:
        asts = [copy_ast(body[i]) for i in range(start, stop)]
        asts2 = [copy_ast(body2[i]) for i in range(start, stop)]

    else:
        asts = body[start : stop]
        asts2 = body2[start : stop]

        del body[start : stop]
        del body2[start : stop]

        for i in range(start, len(body)):
            body2[i].f.pfield = astfield(field2, i)

            if ast := body[i]:  # could be None from Dict **
                ast.f.pfield = astfield(field, i)

    return asts, asts2


# ......................................................................................................................

def _get_slice_NOT_IMPLEMENTED_YET(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    raise NotImplementedError('this is not implemented yet')


def _get_slice_Dict(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Dict` slice is just a normal `Dict`."""

    len_body = len(body := (ast := self.a).keys)
    body2 = ast.values
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(Dict(keys=[], values=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['{}'], from_=self)

    locs = _locs_and_bound_get(self, start, stop, body, body2, 1)
    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'values', cut, body, body2)
    ret_ast = Dict(keys=asts, values=asts2)

    return get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
                         options, 'values', '{', '}', ',', 0, 0)


def _get_slice_Tuple_elts(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Tuple` slice is just a normal `Tuple`. It attempts to copy the parenthesization of the parent. The converse is
    not always true as a `Tuple` may serve as the container of a slice of other node types."""

    len_body = len(body := (ast := self.a).elts)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return new_empty_tuple(from_=self)

    is_par = self._is_delimited_seq()
    locs = _locs_and_bound_get(self, start, stop, body, body, is_par)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx = ast.ctx.__class__
    ret_ast = Tuple(elts=asts, ctx=ctx())

    if not issubclass(ctx, Load):  # new Tuple root object must have ctx=Load
        set_ctx(ret_ast, Load)

    if is_par:
        prefix, suffix = '()'
    else:
        prefix = suffix = ''

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', prefix, suffix, ',', 1, 1)

    if not is_par:
        fst_._maybe_fix_tuple(False)

    fst_._maybe_fix_arglikes(options)  # parenthesize any arglike expressions (could have come from a slice)

    if cut:
        self._maybe_fix_tuple(is_par)

    return fst_


def _get_slice_List_elts(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `List` slice is just a normal `List`."""

    len_body = len(body := (ast := self.a).elts)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(List(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['[]'], from_=self)

    locs = _locs_and_bound_get(self, start, stop, body, body, 1)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx = ast.ctx.__class__
    ret_ast = List(elts=asts, ctx=ctx())  # we set ctx() so that if it is not Load then set_ctx() below will recurse into it

    if not issubclass(ctx, Load):  # new List root object must have ctx=Load
        set_ctx(ret_ast, Load)

    return get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', '[', ']', ',', 0, 0)


def _get_slice_Set_elts(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Set` slice is just a normal `Set` when it has elements. In the case of a zero-length `Set` it may be
    represented as `{*()}` or `set()` or as an invalid `AST` `Set` with curlies but no elements, according to
    options."""

    len_body = len(body := self.a.elts)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        get_norm = _get_norm_option('norm_get', 'set_norm', options)

        return (
            new_empty_set_curlies(from_=self) if not get_norm else
            new_empty_set_call(from_=self) if get_norm == 'call' else
            new_empty_set_star(from_=self)  # True, 'star', 'both'
        )

    locs = _locs_and_bound_get(self, start, stop, body, body, 1)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ret_ast = Set(elts=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', '{', '}', ',', 0, 0)

    if cut:
        _maybe_fix_Set(self, _get_norm_option('norm_self', 'set_norm', options))

    return fst_


def _get_slice_Delete_targets(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """The slice of `Delete.targets` is a normal unparenthesized `Tuple` contianing valid target types, which is also a
    valid python `Tuple`."""

    len_body = len(body := (ast := self.a).targets)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return new_empty_tuple(from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError("cannot cut all Delete.targets without norm_self=False")

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bound_Delete_targets(self, start, loc_first)

    asts = _cut_or_copy_asts(start, stop, 'targets', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Del())  # we initially set to Del so that set_ctx() won't skip it

    set_ctx(ret_ast, Load)  # new Tuple root object must have ctx=Load

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'targets', '', '', ',', False, 1)

    fst_._maybe_fix_tuple(False)

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_fix_stmt_end(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                                ast.end_lineno, ast.end_col_offset)

        ln, col, _, _ = self.loc

        self._maybe_fix_joined_alnum(ln, col + 3)
        self._maybe_add_line_continuations()

    return fst_


def _get_slice_Assign_targets(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    len_body = len(body := self.a.targets)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_Assign_targets(targets=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''],
                       from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError("cannot cut all Assign.targets without norm_self=False")

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bound_Assign_targets(self, start, loc_first)

    asts = _cut_or_copy_asts(start, stop, 'targets', cut, body)
    ret_ast = _Assign_targets(targets=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'targets', '', '', '=', True, True)

    if cut:
        _maybe_fix_Assign_target0(self)
        self._maybe_add_line_continuations()

    return fst_


def _get_slice_With_AsyncWith_items(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    len_body = len(body := (ast := self.a).items)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_withitems(items=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError(f'cannot cut all {ast.__class__.__name__}.items without norm_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if stop == start else body[stop - 1].f.loc

    pars = loc_With_items_pars(self)  # may be pars or may be where pars would go from just after `with` to end of block header
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln = pars_ln
        bound_col = pars_col + pars_n

    asts = _cut_or_copy_asts(start, stop, 'items', cut, body)
    ret_ast = _withitems(items=asts)
    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, pars_end_ln, pars_end_col - pars_n,
                         options, 'items', '', '', ',', False, False)

    if cut and not pars_n:  # only need to fix maybe if there are no parentheses
        if not self._is_enclosed_or_line(pars=False):  # if cut and no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = loc_With_items_pars(self)  # will just give where pars should go (because maybe something like `async \\\n\\\n   with ...`)

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, False)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        elif not start and len_slice != len_body:  # if not adding pars then need to make sure cut didn't join new first `withitem` with the `with`
            ln, col, _, _ = pars.bound

            self._maybe_fix_joined_alnum(ln, col)

    return fst_


def _get_slice_Import_names(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    len_body = len(body := (ast := self.a).names)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_aliases(names=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError('cannot cut all Import.names without norm_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if stop == start else body[stop - 1].f.loc

    _, _, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln, bound_col, _, _ = loc_first

    asts = _cut_or_copy_asts(start, stop, 'names', cut, body)
    ret_ast = _aliases(names=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'names', '', '', ',', False, False)

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                ast.end_lineno, ast.end_col_offset)

        self._maybe_add_line_continuations()

    return fst_


def _get_slice_ImportFrom_names(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    len_body = len(body := (ast := self.a).names)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_aliases(names=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError('cannot cut all ImportFrom.names without norm_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if stop == start else body[stop - 1].f.loc

    pars = loc_ImportFrom_names_pars(self)  # may be pars or may be where pars would go from just after `import` to end of node
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln = pars_ln
        bound_col = pars_col + pars_n

    asts = _cut_or_copy_asts(start, stop, 'names', cut, body)
    ret_ast = _aliases(names=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, pars_end_ln, pars_end_col - pars_n,
                         options, 'names', '', '', ',', False, False)

    if cut and not pars_n:  # only need to fix maybe if there are no parentheses
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                ast.end_lineno, ast.end_col_offset)

        if not self._is_enclosed_or_line(pars=False):  # if cut and no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = loc_ImportFrom_names_pars(self)

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, True, False, self)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

    return fst_


def _get_slice_Global_Nonlocal_names(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    len_body = len((ast := self.a).names)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return new_empty_tuple(from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError(f'cannot cut all {ast.__class__.__name__}.names without norm_self=False')

    ln, end_col, bound_end_ln, bound_end_col = self.loc

    lines = self.root._lines
    ret_elts = []
    ret_ast = Tuple(elts=ret_elts, ctx=Load())
    end_col += 5 if isinstance(ast, Global) else 7  # will have another +1 added in search

    if not start:
        bound_ln = None  # set later

    else:
        for _ in range(start - 1):
            ln, end_col = next_find(lines, ln, end_col + 1, bound_end_ln, bound_end_col, ',')  # must be there

        bound_ln, bound_col, src = next_find_re(lines, ln, end_col + 1, bound_end_ln, bound_end_col, re_identifier)  # must be there, + 1 skips comma

        bound_col += len(src)
        ln, end_col = next_find(lines, bound_ln, bound_col, bound_end_ln, bound_end_col, ',')  # must be there

    for i in range(stop - start):  # create tuple of Names from identifiers
        ln, col, src = next_find_re(lines, ln, end_col + 1, bound_end_ln, bound_end_col, re_identifier)  # must be there, + 1 probably skips comma
        lineno = ln + 1
        end_col = col + len(src)

        if not i:
            loc_first = fstloc(ln, col, ln, end_col)

            if bound_ln is None:
                bound_ln = ln
                bound_col = col

        ret_elts.append(Name(id=src, ctx=Load(), lineno=lineno, col_offset=(l := lines[ln]).c2b(col), end_lineno=lineno,
                             end_col_offset=l.c2b(end_col)))

    loc_last = fstloc(ln, col, ln, end_col)

    if cut:
        del ast.names[start : stop]

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, ret_elts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'names', '', '', ',', False, 1)

    fst_._maybe_fix_tuple(False)  # this is in case of multiline elements to add pars, otherwise location would reparse different

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_fix_stmt_end(self, bound_ln + 1, lines[bound_ln].c2b(bound_col), ast.end_lineno, ast.end_col_offset)

        self._maybe_add_line_continuations()

    return fst_


def _get_slice_ClassDef_bases(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `ClassDef.bases` slice is just a normal `Tuple`, with possibly expr_arglike elements which are invalid in a
    normal expression tuple."""

    len_body = len(body := (ast := self.a).bases)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if start == stop:
        return new_empty_tuple(from_=self)

    if keywords := ast.keywords:
        if (kw0_pos := keywords[0].f.loc[:2]) < body[stop - 1].f.loc[2:]:
            raise NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')

        self_tail_sep = True if body[-1].f.loc[2:] < kw0_pos else None

    else:
        self_tail_sep = None

    bound_ln, bound_col, bound_end_ln, bound_end_col = loc_ClassDef_bases_pars(self)  # definitely exist
    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    asts = _cut_or_copy_asts(start, stop, 'bases', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'bases', '(', ')', ',', self_tail_sep, len_slice == 1)

    fst_._maybe_fix_arglikes(options)  # parenthesize any arglike expressions

    if cut:
        if keywords:
            if cut and start and stop == len_body:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
                self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

        elif not body:  # everything was cut and no keywords, remove parentheses
            pars_ln, pars_col, pars_end_ln, pars_end_col = loc_ClassDef_bases_pars(self)  # definitely exist

            self._put_src(None, pars_ln, pars_col, pars_end_ln, pars_end_col, False)

    return fst_


def _get_slice_Call_args(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Call.args` slice is just a normal `Tuple`, with possibly expr_arglike elements which are invalid in a normal
    expression tuple."""

    len_body = len(body := (ast := self.a).args)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if start == stop:
        return new_empty_tuple(from_=self)

    if keywords := ast.keywords:
        if (kw0_pos := keywords[0].f.loc[:2]) < body[stop - 1].f.loc[2:]:
            raise NodeError('cannot get this Call.args slice because it includes parts after a keyword')

        self_tail_sep = True if body[-1].f.loc[2:] < kw0_pos else None

    else:
        self_tail_sep = None

        if body and (f0 := body[0].f)._is_solo_call_arg_genexp() and f0.pars(shared=False).n == -1:  # single call argument GeneratorExp shares parentheses with Call?
            f0._parenthesize_grouping()

    bound_ln, bound_col, bound_end_ln, bound_end_col = loc_Call_pars(self)
    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    asts = _cut_or_copy_asts(start, stop, 'args', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'args', '(', ')', ',', self_tail_sep, len_slice == 1)

    fst_._maybe_fix_arglikes(options)  # parenthesize any arglike expressions

    if cut and start and keywords and stop == len_body:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
        self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

    return fst_


def _get_slice_MatchSequence_patterns(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `MatchSequence` slice is just a normal `MatchSequence`. It attempts to copy the parenthesization of the
    parent."""

    len_body = len(body := self.a.patterns)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(MatchSequence(patterns=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['[]'], from_=self)

    delims = self._is_delimited_matchseq()
    locs = _locs_and_bound_get(self, start, stop, body, body, bool(delims))
    asts = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchSequence(patterns=asts)

    if delims:
        prefix, suffix = delims
        tail_sep = 1 if delims == '()' else 0

    else:
        prefix = suffix = delims = ''
        tail_sep = 1

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'patterns', prefix, suffix, ',', tail_sep, tail_sep)

    if not delims:
        _maybe_fix_MatchSequence(fst_, '')

    if cut:
        _maybe_fix_MatchSequence(self, delims)

    return fst_


def _get_slice_MatchMapping(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `MatchMapping` slice is just a normal `MatchMapping`."""

    len_body = len(body := (ast := self.a).keys)
    body2 = ast.patterns
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(MatchMapping(keys=[], patterns=[], rest=None, lineno=1, col_offset=0, end_lineno=1,
                                    end_col_offset=2),
                       ['{}'], from_=self)

    locs = _locs_and_bound_get(self, start, stop, body, body2, 1)
    self_tail_sep = True if (rest := ast.rest) else 0

    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'patterns', cut, body, body2)
    ret_ast = MatchMapping(keys=asts, patterns=asts2, rest=None)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
                         options, 'patterns', '{', '}', ',', self_tail_sep, False)

    if cut and start and rest and stop == len_body:  # if there is a rest element and we removed tail element we make sure there is a space between comma of the new last element and the rest
        self._maybe_ins_separator(*(f := body2[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

    return fst_


def _get_slice_MatchOr_patterns(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `MatchOr` slice is just a normal `MatchOr` when it has two elements or more. If it has one it may be returned
    as a single `pattern` or as an invalid single-element `MatchOr`. If the slice would wind up with zero elements it
    may raise and exception or return an invalid zero-element `MatchOr`, as specified by options."""

    len_body = len(body := self.a.patterns)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    get_norm = _get_norm_option('norm_get', 'matchor_norm', options)
    self_norm = _get_norm_option('norm_self', 'matchor_norm', options)

    if not len_slice:
        if get_norm:
            raise ValueError("cannot get empty slice from MatchOr without norm_get=False")

        return fst.FST(MatchOr(patterns=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], from_=self)

    if len_slice == 1 and get_norm == 'strict':
        raise ValueError("cannot get length 1 slice from MatchOr with norm_get='strict'")

    if cut:
        if not (len_left := len_body - len_slice):
            if self_norm:
                raise ValueError("cannot cut all MatchOr.patterns without norm_self=False")

        elif len_left == 1 and self_norm == 'strict':
            raise ValueError("cannot cut MatchOr to length 1 with norm_self='strict'")

    locs = _locs_and_bound_get(self, start, stop, body, body, 0)
    asts = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchOr(patterns=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'patterns', '', '', '|', False, False)

    _maybe_fix_MatchOr(fst_, bool(get_norm))

    if cut:
        _maybe_fix_MatchOr(self, bool(self_norm))

    return fst_


def _get_slice_type_params(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    len_body = len(body := (ast := self.a).type_params)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(_type_params([], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], from_=self)

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_func = (
        loc_TypeAlias_type_params_brackets if isinstance(ast, TypeAlias) else
        loc_ClassDef_type_params_brackets if isinstance(ast, ClassDef) else
        loc_FunctionDef_type_params_brackets  # FunctionDef, AsyncFunctionDef
    )

    (bound_ln, bound_col, bound_end_ln, bound_end_col), _ = bound_func(self)

    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    asts = _cut_or_copy_asts(start, stop, 'type_params', cut, body)
    ret_ast = _type_params(type_params=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'type_params', '', '', ',', False, False)

    if cut and not body:  # everything was cut, need to remove brackets
        (_, _, bound_end_ln, bound_end_col), (name_ln, name_col) = bound_func(self)

        self._put_src(None, name_ln, name_col, bound_end_ln, bound_end_col, False)

    return fst_


def _get_slice__slice(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Our own general non-AST-compatible slice of some `type[AST]` list field."""

    static = _SLICE_STATICS[cls := (ast := self.a).__class__]
    len_body = len(body := getattr(ast, field))
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(cls([], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], from_=self)

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()

    asts = _cut_or_copy_asts(start, stop, field, cut, body)
    ret_ast = cls(asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, field, '', '', static.sep, static.self_tail_sep, static.ret_tail_sep)

    return fst_


# ----------------------------------------------------------------------------------------------------------------------
# put

def _put_slice_asts(
    self: fst.FST,
    start: int,
    stop: int,
    field: str,
    body: list[AST],
    fst_: fst.FST | None,
    asts: list[AST] | None,
    ctx: type[expr_context] | None = None,
) -> None:
    """Put or delete the actual `AST` nodes to `self` body and create `FST` nodes for them."""

    self._unmake_fst_tree(body[start : stop])

    if not asts:
        len_asts = 0

        del body[start : stop]

    else:
        len_asts = len(asts)

        fst_._unmake_fst_parents(True)

        body[start : stop] = asts

        FST = fst.FST
        new_fsts = [FST(body[i], self, astfield(field, i)) for i in range(start, start + len_asts)]

        if new_fsts and ctx:
            set_ctx([f.a for f in new_fsts], ctx)

        self._make_fst_tree(new_fsts)

    for i in range(start + len_asts, len(body)):
        body[i].f.pfield = astfield(field, i)


def _put_slice_seq_and_asts(
    self: fst.FST,
    start: int,
    stop: int,
    field: str,
    body: list[AST],
    fst_: fst.FST | None,
    fst_field: str,
    ctx: type[expr_context] | None,
    bound_ln: int,
    bound_col: int,
    bound_end_ln: int,
    bound_end_col: int,
    sep: str,
    self_tail_sep: bool | Literal[0, 1] | None,
    options: Mapping[str, Any],
) -> None:

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, field, None, sep, self_tail_sep)

        _put_slice_asts(self, start, stop, field, body, None, None)

    else:
        fst_body = getattr(fst_.a, fst_field)

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len(fst_body),
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, field, None, sep, self_tail_sep)

        _put_slice_asts(self, start, stop, field, body, fst_, fst_body, ctx)

    put_slice_sep_end(self, end_params)


def _put_slice_asts2(
    self: fst.FST,
    start: int,
    stop: int,
    field2: str,
    body: list[AST],
    body2: list[AST],
    fst_: fst.FST | None,
    asts: list[AST] | None,
    asts2: list[AST] | None,
) -> None:
    """Put or delete the actual `AST` nodes to `self` body and create `FST` nodes for them. This is the two element
    version for Dict and MatchMapping."""

    self._unmake_fst_tree(body[start : stop] + body2[start : stop])

    if not asts:
        len_asts = 0

        del body[start : stop]
        del body2[start : stop]

    else:
        len_asts = len(asts)

        fst_._unmake_fst_parents(True)

        body[start : stop] = asts
        body2[start : stop] = asts2

        FST = fst.FST
        new_fsts = []

        for i in range(len_asts):
            startplusi = start + i

            new_fsts.append(FST(body2[startplusi], self, astfield(field2, startplusi)))

            if key := body[startplusi]:
                new_fsts.append(FST(key, self, astfield('keys', startplusi)))

        self._make_fst_tree(new_fsts)

    for i in range(start + len_asts, len(body)):
        body2[i].f.pfield = astfield(field2, i)

        if key := body[i]:  # could be None from ** in Dict
            key.f.pfield = astfield('keys', i)


def _trim_delimiters(self: fst.FST) -> None:
    lines = self._lines
    ast = self.a
    ln, col, end_ln, end_col = self.loc
    col += 1
    end_col -= 1
    ast.col_offset += 1
    ast.end_col_offset -= 1

    self._offset(ln, col, -ln, -lines[ln].c2b(col))

    lines[end_ln] = bistr(lines[end_ln][:end_col])
    lines[ln] = bistr(lines[ln][col:])

    del lines[end_ln + 1:], lines[:ln]


def _set_loc_whole(self: fst.FST) -> None:
    ast = self.a
    ast.lineno = 1
    ast.col_offset = 0
    ast.end_lineno = len(ls := self._lines)
    ast.end_col_offset = ls[-1].lenbytes

    self._touch()


def _validate_put_seq(
    self: fst.FST, fst_: fst.FST, non_slice: str, *, check_target: Literal[False] | Callable = False
) -> None:  # check_target like is_valid_target()
    if not fst_:
        return

    ast = self.a
    ast_ = fst_.a

    if non_slice and isinstance(ast_, Tuple) and any(isinstance(e, Slice) for e in ast_.elts):
        raise NodeError(f'cannot put Slice into {non_slice}')

    if check_target and not isinstance(ctx := getattr(ast, 'ctx', None), Load) and not check_target(ast_.elts):
        raise NodeError(f'invalid slice for {ast.__class__.__name__}'
                        f'{f" {ctx.__class__.__name__}" if ctx else ""} target')


def _code_to_slice_seq(
    self: fst.FST,
    code: Code | None,
    one: bool,
    options: Mapping[str, Any],
    *,
    code_as: Callable = code_as_expr,
    non_seq_str_as_one: bool = False,
) -> fst.FST | None:
    if code is None:
        return None

    fst_ = code_as(code, self.root.parse_params, sanitize=False)
    ast_ = fst_.a

    if not one and non_seq_str_as_one and not isinstance(ast_, (Tuple, List, Set)) and isinstance(code, (str, list)):  # this exists as a convenience for allowing doing `Delete.targets = 'target'` (without trailing comma if string source)
        one = True

    put_norm = _get_norm_option('norm_put', 'set_norm', options)

    if one:
        if (is_par := fst_._is_parenthesized_tuple()) is not None:
            fst_._maybe_add_singleton_tuple_comma(is_par)  # specifically for lone '*starred' without comma from slices, even though those can't be gotten alone organically

            if is_par is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
                fst_._delimit_node()

        elif isinstance(ast_, Set):
            _maybe_fix_Set(fst_, put_norm)

        elif isinstance(ast_, NamedExpr):  # this needs to be parenthesized if being put to unparenthesized tuple
            if not fst_.pars().n and self._is_parenthesized_tuple() is False:
                fst_._parenthesize_grouping()

        elif isinstance(ast_, (Yield, YieldFrom)):  # these need to be parenthesized definitely
            if not fst_.pars().n:
                fst_._parenthesize_grouping()

        ast_ = Tuple(elts=[fst_.a], ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),  # fst_.a because may have changed in Set processing
                     end_col_offset=ls[-1].lenbytes)  # Tuple because it is valid target if checked in validate and allows _is_enclosed_or_line() check without delimiters to check content

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    if put_norm:
        if (fst_._is_empty_set_star() if put_norm == 'star' else
            fst_._is_empty_set_call() if put_norm == 'call' else
            fst_._is_empty_set_star() or fst_._is_empty_set_call()  # True or 'both'
        ):
            return None

    if not isinstance(ast_, (Tuple, List, Set)):
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} "
                        f"must be a Tuple, List or Set, not a {ast_.__class__.__name__}", rawable=True)

    if not ast_.elts:  # put empty sequence is same as delete
        return None

    if fst_._is_parenthesized_tuple() is not False:  # anything that is not an unparenthesize tuple is restricted to the inside of the delimiters, which are removed
        _trim_delimiters(fst_)
    else:  # if unparenthesized tuple then use whole source, including leading and trailing trivia not included
        _set_loc_whole(fst_)

    return fst_


def _code_to_slice_seq2(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any], code_as: Callable
) -> fst.FST | None:
    if code is None:
        return None

    if one:
        raise ValueError(f"cannot put as 'one' item to a {self.a.__class__.__name__} slice")

    fst_ = code_as(code, self.root.parse_params, sanitize=False)
    ast_ = fst_.a

    if ast_.__class__ is not self.a.__class__:
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} must be a {self.a.__class__.__name__}"
                        f", not a {ast_.__class__.__name__}", rawable=True)

    if not ast_.keys:  # put empty sequence is same as delete
        return None

    _trim_delimiters(fst_)

    return fst_


def _code_to_slice__Assign_targets(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_expr(code, self.root.parse_params, sanitize=False)
        ast_ = fst_.a

        if not is_valid_target(ast_):
            raise NodeError(f'expecting one Assign target, got {fst_.a.__class__.__name__}')

        set_ctx(ast_, Store)

        ast_ = _Assign_targets(targets=[ast_], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                               end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    else:
        fst_ = code_as_Assign_targets(code, self.root.parse_params, sanitize=False)

        if not fst_.a.targets:  # put empty sequence is same as delete
            return None

    return fst_


def _code_to_slice__aliases(
    self: fst.FST,
    code: Code | None,
    one: bool,
    options: Mapping[str, Any],
    code_as_one: Callable = code_as_alias,
    code_as_slice: Callable = code_as_aliases,
) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_one(code, self.root.parse_params, sanitize=False)
        ast_ = _aliases(names=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                        end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    fst_ = code_as_slice(code, self.root.parse_params, sanitize=False)

    if not fst_.a.names:  # put empty sequence is same as delete
        return None

    return fst_


def _code_to_slice__withitems(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_withitem(code, self.root.parse_params, sanitize=False)
        ast_ = _withitems(items=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                          end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    fst_ = code_as_withitems(code, self.root.parse_params, sanitize=False)

    if not fst_.a.items:  # put empty sequence is same as delete
        return None

    return fst_


def _code_to_slice__expr_arglikes(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_expr_arglike(code, self.root.parse_params, sanitize=False)
        ast_ = fst_.a

        if (is_par := fst_._is_parenthesized_tuple()) is not None:
            if fst_ is code and any(e.f.is_expr_arglike for e in ast_.elts):
                raise NodeError("cannot put argument-like expression(s) in a Tuple as 'one'")

            if is_par is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
                fst_._delimit_node()

        ast_ = Tuple(elts=[ast_], ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                     end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    fst_ = code_as__expr_arglikes(code, self.root.parse_params, sanitize=False)

    if not fst_.a.elts:  # put empty sequence is same as delete
        return None

    if fst_._is_parenthesized_tuple() is not False:  # parenthesize tuple is restricted to the inside of the delimiters, which are removed
        _trim_delimiters(fst_)
    else:  # if unparenthesized tuple then use whole source, including leading and trailing trivia not included
        _set_loc_whole(fst_)

    return fst_


def _code_to_slice_MatchSequence(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    if code is None:
        return None

    fst_ = code_as_pattern(code, self.root.parse_params, sanitize=False)

    if one:
        if fst_._is_delimited_matchseq() == '':
            fst_._delimit_node(delims='[]')

        ast_ = MatchSequence(patterns=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                             end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    ast_ = fst_.a

    if not isinstance(ast_, MatchSequence):
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} "
                        f"must be a MatchSequence, not a {ast_.__class__.__name__}", rawable=True)

    if not ast_.patterns:  # put empty sequence is same as delete
        return None

    if fst_._is_delimited_matchseq():  # delimited is restricted to the inside of the delimiters, which are removed
        _trim_delimiters(fst_)
    else:  # if undelimited then use whole source, including leading and trailing trivia not included
        _set_loc_whole(fst_)

    return fst_


def _code_to_slice_MatchOr(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]) -> fst.FST | None:
    if code is None:
        return None

    try:
        fst_ = code_as_pattern(code, self.root.parse_params, sanitize=False, allow_invalid_matchor=True)

    except SyntaxError:
        if (not (isinstance(code, list) or (isinstance(code, str) and (code := code.split('\n')))) or
            not next_frag(code, 0, 0, len(code) - 1, len(code[-1]))
        ):  # nothing other than maybe comments or line continuations present, empty pattern, not an error but delete
            return None

        raise

    ast_ = fst_.a

    if isinstance(ast_, MatchOr):
        if not (patterns := ast_.patterns):
            return None

        fst_pars = fst_.pars()

        if not one or len(patterns) == 1:
            if fst_pars.n:
                fst_._unparenthesize_grouping()

            _set_loc_whole(fst_)

            return fst_

        if not fst_pars.n:
            fst_._parenthesize_grouping()

    else:
        if not one and not _get_norm_option('norm_put', 'matchor_norm', options):
            raise NodeError(f"slice being assigned to a MatchOr "
                            f"must be a MatchOr with norm_put=False, not a {ast_.__class__.__name__}",
                            rawable=True)

        if isinstance(ast_, MatchAs):
            if ast_.pattern is not None and not fst_.pars().n:
                fst_._parenthesize_grouping()

        elif isinstance(ast_, MatchSequence):
            if not fst_._is_delimited_matchseq():
                fst_._delimit_node(delims='[]')

    ast_ = MatchOr(patterns=[ast_], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                   end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, from_=fst_, lcopy=False)


def _code_to_slice__type_params(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_type_param(code, self.root.parse_params, sanitize=False)
        ast_ = _type_params(type_params=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                            end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    fst_ = code_as_type_params(code, self.root.parse_params, sanitize=False)

    if not fst_.a.type_params:  # put empty sequence is same as delete
        return None

    return fst_


# ......................................................................................................................

def _put_slice_NOT_IMPLEMENTED_YET(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    raise NotImplementedError("not implemented yet, try with option raw='auto'")


def _put_slice_Dict(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice_seq2(self, code, one, options, code_as_expr)
    body = (ast := self.a).keys
    body2 = ast.values
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'keys', 'values')

        _put_slice_asts2(self, start, stop, 'values', body, body2, None, None, None)

    else:
        ast_ = fst_.a
        fst_body = ast_.keys
        fst_body2 = ast_.values
        len_fst_body = len(fst_body)
        fst_first = a.f if (a := fst_body[0]) else fst_._loc_maybe_key(0)

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_first, fst_body2[-1].f, len_fst_body,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'keys', 'values')

        _put_slice_asts2(self, start, stop, 'values', body, body2, fst_, fst_body, fst_body2)

    put_slice_sep_end(self, end_params)


def _put_slice_Tuple_elts(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """Tuple is used in many different ways in python, also for expressionish slices by us."""

    fst_ = _code_to_slice_seq(self, code, one, options, code_as=code_as_expr_all)
    body = (ast := self.a).elts
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    # extra checks for tuple special usage

    is_par = self._is_delimited_seq()
    is_slice = (pfield := self.pfield) and pfield.name == 'slice'
    need_par = False

    if fst_:
        len_fst_body = len(fst_body := fst_.a.elts)

        if len_fst_body == 1 and isinstance(e0 := fst_body[0], Tuple) and any(isinstance(e, Slice) for e in e0.elts):  # putting a tuple with Slices as one
            raise NodeError('cannot put tuple with Slices to tuple')

        if PYLT11:
            if is_slice and not is_par and any(isinstance(e, Starred) for e in fst_body):
                if any(isinstance(e, Slice) for i, e in enumerate(body) if i < start or i >= stop):
                    raise NodeError('cannot put Starred to a slice Tuple containing Slices')

                need_par = True

        elif PYGE14:
            if not is_par and pfield == ('type', None) and any(isinstance(e, Starred) for e in fst_body):  # if putting Starred to unparenthesized ExceptHandler.type Tuple then parenthesize it
                need_par = True

    # normal stuff

    _validate_put_seq(self, fst_,
                      '' if not is_par and (not pfield or is_slice) else 'non-slice Tuple',
                      check_target=is_valid_target)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if is_par:
        bound_col += 1
        bound_end_col -= 1

    _put_slice_seq_and_asts(self, start, stop, 'elts', body, fst_, 'elts', ast.ctx.__class__,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', 1, options)

    is_par = self._maybe_fix_tuple(is_par)

    if need_par and not is_par:
        self._delimit_node()


def _put_slice_List_elts(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice_seq(self, code, one, options)
    body = (ast := self.a).elts
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'List', check_target=is_valid_target)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    _put_slice_seq_and_asts(self, start, stop, 'elts', body, fst_, 'elts', ast.ctx.__class__,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', None, options)


def _put_slice_Set_elts(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice_seq(self, code, one, options)
    body = self.a.elts
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'Set')

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    _put_slice_seq_and_asts(self, start, stop, 'elts', body, fst_, 'elts', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', None, options)

    _maybe_fix_Set(self, _get_norm_option('norm_self', 'set_norm', options))


def _put_slice_Delete_targets(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """Even though when getting a slice it will be returned as a `Tuple`, any sequence of valid target types is accepted
    for the put operation. If putting a non-sequence element, it will be automatically put as `one=True` to match the
    non-comma terminated syntax of `Delete` targets (a non-sequence `FST` or `AST` will not be accepted like this). This
    allows correct-appearing syntax like `delfst.targets = 'target'` to work."""

    fst_ = _code_to_slice_seq(self, code, one, options, non_seq_str_as_one=True)
    len_body = len(body := (ast := self.a).targets)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError("cannot delete all Delete.targets without norm_self=False")

    _validate_put_seq(self, fst_, 'Delete', check_target=is_valid_del_target)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bound_Delete_targets(self)

    _put_slice_seq_and_asts(self, start, stop, 'targets', body, fst_, 'elts', Del,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', False, options)

    if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
        if body:
            _, _, bound_ln, bound_col = body[-1].f.pars()

        _maybe_fix_stmt_end(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                            ast.end_lineno, ast.end_col_offset)

    ln, col, _, _ = self.loc

    self._maybe_fix_joined_alnum(ln, col + 3)
    self._maybe_add_line_continuations()


def _put_slice_Assign_targets(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice__Assign_targets(self, code, one, options)
    len_body = len(body := self.a.targets)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError("cannot delete all Assign.targets without norm_self=False")

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bound_Assign_targets(self, start)

    _put_slice_seq_and_asts(self, start, stop, 'targets', body, fst_, 'targets', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, '=', True, options)

    _maybe_fix_Assign_target0(self)
    self._maybe_add_line_continuations()


def _put_slice_With_AsyncWith_items(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice__withitems(self, code, one, options)
    len_body = len(body := (ast := self.a).items)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError(f'cannot delete all {ast.__class__.__name__}.items without norm_self=False')

    pars = loc_With_items_pars(self)  # may be pars or may be where pars would go from just after `with` to end of block header `:`
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    _put_slice_seq_and_asts(self, start, stop, 'items', body, fst_, 'items', None,
                            pars_ln, pars_col + pars_n, pars_end_ln, pars_end_col - pars_n, ',', False, options)

    if not pars_n:  # only need to fix maybe if there are no parentheses
        if not self._is_enclosed_or_line(pars=False):  # if no parentheses and wound up not valid for parse then adding parentheses around items should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = loc_With_items_pars(self)

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, False)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        if not start:  # if not adding pars then need to make sure del or put didn't join new first `withitem` with the `with`
            ln, col, _, _ = pars.bound

            self._maybe_fix_joined_alnum(ln, col)


def _put_slice_Import_names(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice__aliases(self, code, one, options, code_as_Import_name, code_as_Import_names)
    len_body = len(body := (ast := self.a).names)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError('cannot delete all Import.names without norm_self=False')

    _, _, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    elif body:
        bound_ln, bound_col, _, _ = body[0].f.pars()
    else:
        bound_ln = bound_end_ln
        bound_col = bound_end_col

    _put_slice_seq_and_asts(self, start, stop, 'names', body, fst_, 'names', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', False, options)

    if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
        if body:
            _maybe_fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                ast.end_lineno, ast.end_col_offset)
        else:
            _maybe_fix_stmt_end(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                                ast.end_lineno, ast.end_col_offset)

    self._maybe_add_line_continuations()  # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this


def _put_slice_ImportFrom_names(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice__aliases(self, code, one, options, code_as_ImportFrom_name, code_as_ImportFrom_names)
    len_body = len(body := (ast := self.a).names)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    put_star = False

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError('cannot delete all ImportFrom.names without norm_self=False')

    else:
        if put_star := fst_.a.names[0].name == '*':  # if putting star then it must overwrite everything
            if len_slice != len_body:
                raise NodeError("if putting star '*' alias it must overwrite all other aliases")

        elif body and body[0].name == '*':  # putting to star then it must be overwritten
            if start > 0 or stop < 1:
                raise NodeError("if putting over star '*' alias it must be overwritten")

    pars = loc_ImportFrom_names_pars(self)  # may be pars or may be where pars would go from just after `import` to end of node
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    _put_slice_seq_and_asts(self, start, stop, 'names', body, fst_, 'names', None,
                            pars_ln, pars_col + pars_n, pars_end_ln, pars_end_col - pars_n, ',', False, options)

    if not pars_n:  # only need to fix maybe if there are no parentheses
        if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
            if body:
                _maybe_fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                    ast.end_lineno, ast.end_col_offset)
            else:
                _maybe_fix_stmt_end(self, pars_ln + 1, self.root._lines[pars_ln].c2b(pars_col),
                                    ast.end_lineno, ast.end_col_offset)

        if not self._is_enclosed_or_line(pars=False):  # if no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = loc_ImportFrom_names_pars(self)

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, True, False, self)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this

    elif put_star:  # if put star then must remove parentheses (including any trivia inside them)
        pars_ln, pars_col, pars_end_ln, pars_end_col = loc_ImportFrom_names_pars(self)
        star_ln, star_col, star_end_ln, star_end_col = body[0].f.loc

        self._put_src(None, star_end_ln, star_end_col, pars_end_ln, pars_end_col, True)
        self._put_src(None, pars_ln, pars_col, star_ln, star_col, False)


def _put_slice_Global_Nonlocal_names(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """In order to do this put since `Global` and `Nonlocal` do not have child `AST` nodes but just identifiers, we
    create a temporary container which does have `Name` elements for each name and operate on that. Afterwards we get
    rid of that but the modified source identifiers remain."""

    fst_ = _code_to_slice_seq(self, code, one, options, non_seq_str_as_one=True)
    len_body = len(body := (ast := self.a).names)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError(f'cannot delete all {ast.__class__.__name__}.names without norm_self=False')

    else:
        n = 0

        if not all(isinstance(bad := e, Name) and not (n := e.f.pars().n) for e in fst_.a.elts):
            raise NodeError(f'cannot put{" parenthesized" if n else ""} {bad.__class__.__name__} '
                            f'to {ast.__class__.__name__}.names')

        # TODO? could have some logic here to strip trailing newline from fst_ if putting at end and there is no trivia on same line as last element to not introduce a spurisous newline? seems a bit over-the-top, XXX be careful of semicolons separating statements!

    ln, end_col, bound_end_ln, bound_end_col = self.loc

    lines = self.root._lines
    tmp_elts = []  # these will be temporary AST nodes so that we can edit the source using existing code
    end_col += 5 if isinstance(ast, Global) else 7  # will have another +1 added in search

    for _ in range(len_body):
        ln, col, src = next_find_re(lines, ln, end_col + 1, bound_end_ln, bound_end_col, re_identifier)  # must be there, + 1 probably skips comma
        lineno = ln + 1
        end_col = col + len(src)

        tmp_elts.append(Name(id=src, ctx=Load(), lineno=lineno, col_offset=(l := lines[ln]).c2b(col), end_lineno=lineno,
                             end_col_offset=l.c2b(end_col)))

    if tmp_elts:
        tmp_ast = Tuple(elts=tmp_elts, ctx=Load(), lineno=(e0 := tmp_elts[0]).lineno, col_offset=e0.col_offset,
                        end_lineno=(en := tmp_elts[-1]).end_lineno, end_col_offset=en.end_col_offset)
    else:
        tmp_ast = Tuple(elts=tmp_elts, ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=0)

    self._set_ast(tmp_ast)  # temporarily swap out Global/Nonlocal AST for temporary Tuple AST so that offsetting propagates to the parents

    if tmp_elts:
        bound_ln, bound_col, last_end_ln, last_end_col = tmp_elts[0].f.loc

        if not start:
            last_end_ln = bound_ln
            last_end_col = bound_col

        elif start != 1:
            _, _, last_end_ln, last_end_col = tmp_elts[start - 1].f.loc

    else:
        bound_ln = last_end_ln = bound_end_ln
        bound_col = last_end_col = bound_end_col

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'elts', None, ',', False)

        del body[start : stop]  # this is the real update

        _put_slice_asts(self, start, stop, 'elts', tmp_elts, None, None)  # this is the fake temporary update

    else:
        len_fst_body = len(fst_body := fst_.a.elts)
        fst_last = fst_body[-1].f

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_last, len_fst_body,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'elts', None, ',', False)

        body[start : stop] = [e.id for e in fst_body]  # this is the real update

        _put_slice_asts(self, start, stop, 'elts', tmp_elts, fst_, fst_body)  # this is the fake temporary update, lets just pretend like its has real AST children, needed for put_slice_sep_end()

    put_slice_sep_end(self, end_params)

    if fst_:  # we get it here because ._set_ast() below makes this impossible
        fst_last_loc = tmp_elts[-1].f.loc

    ast.end_lineno = tmp_ast.end_lineno  # copy new end from temporary FST to self (since it was swapped out)
    ast.end_col_offset = tmp_ast.end_col_offset

    self._set_ast(ast, True)

    if stop == len_body:  # if del OR put till and something left then may need to reset end position of self due to new trailing trivia, put because could come from trailing trivia of last element of parenthesized tuple
        if fst_:
            _, _, last_end_ln, last_end_col = fst_last_loc

        _maybe_fix_stmt_end(self, last_end_ln + 1, lines[last_end_ln].c2b(last_end_col),
                            ast.end_lineno, ast.end_col_offset)

    self._maybe_add_line_continuations()  # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this


def _put_slice_ClassDef_bases(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice__expr_arglikes(self, code, one, options)
    len_body = len(body := (ast := self.a).bases)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_ and not len_slice:
        return

    _validate_put_seq(self, fst_, 'ClassDef.bases')

    if keywords := ast.keywords:
        if body and keywords[0].f.loc[:2] < body[stop - 1].f.loc[2:] and stop:
            raise NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')

    bound_ln, bound_col, bound_end_ln, bound_end_col = bases_pars = loc_ClassDef_bases_pars(self)

    if not fst_:
        if not keywords and len_slice == len_body:  # deleting everything so remove pars
            self._put_src(None, bound_ln, bound_col, bound_end_ln, bound_end_col, False)

            end_params = None

        else:
            bound_col += 1
            bound_end_col -= 1
            self_tail_sep = (start and keywords and stop == len_body) or None

            end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                             bound_ln, bound_col, bound_end_ln, bound_end_col,
                                             options, 'bases', None, ',', self_tail_sep)

        _put_slice_asts(self, start, stop, 'bases', body, None, None)

    else:
        if bases_pars.n:
            bound_col += 1
            bound_end_col -= 1

        else:  # parentheses don't exist, add them first
            self._put_src('()', bound_ln, bound_col, bound_end_ln, bound_end_col, False)

            bound_col += 1
            bound_end_col = bound_col
            bound_end_ln = bound_ln

        self_tail_sep = (keywords and stop == len_body) or None
        len_fst_body = len(fst_body := fst_.a.elts)

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'bases', None, ',', self_tail_sep)

        _put_slice_asts(self, start, stop, 'bases', body, fst_, fst_body)

    if end_params:
        put_slice_sep_end(self, end_params)

        if self_tail_sep:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
            self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there


def _put_slice_Call_args(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice__expr_arglikes(self, code, one, options)
    len_body = len(body := (ast := self.a).args)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'Call.args')

    if keywords := ast.keywords:
        if body and keywords[0].f.loc[:2] < body[stop - 1].f.loc[2:] and stop:
            raise NodeError('cannot get this Call.args slice because it includes parts after a keyword')

    else:
        if body and (f0 := body[0].f)._is_solo_call_arg_genexp() and f0.pars(shared=False).n == -1:  # single call argument GeneratorExp shares parentheses with Call?
            f0._parenthesize_grouping()

    bound_ln, bound_col, bound_end_ln, bound_end_col = loc_Call_pars(self)
    bound_col += 1
    bound_end_col -= 1

    self_tail_sep = ((fst_ or start) and keywords and stop == len_body) or None

    _put_slice_seq_and_asts(self, start, stop, 'args', body, fst_, 'elts', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', self_tail_sep, options)

    if self_tail_sep:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
        self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there


def _put_slice_MatchSequence_patterns(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    # NOTE: we allow multiple MatchStars to be put to the same MatchSequence
    fst_ = _code_to_slice_MatchSequence(self, code, one, options)
    body = self.a.patterns
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if delims := self._is_delimited_matchseq():
        bound_col += 1
        bound_end_col -= 1

    _put_slice_seq_and_asts(self, start, stop, 'patterns', body, fst_, 'patterns', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', 0, options)

    _maybe_fix_MatchSequence(self, delims)


def _put_slice_MatchMapping(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice_seq2(self, code, one, options, code_as_pattern)
    len_body = len(body := (ast := self.a).keys)
    body2 = ast.patterns
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    if not fst_:
        self_tail_sep = (start and ast.rest and stop == len_body) or None

        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'keys', 'patterns', ',', self_tail_sep)

        _put_slice_asts2(self, start, stop, 'patterns', body, body2, None, None, None)

    else:
        ast_ = fst_.a
        fst_body = ast_.keys
        fst_body2 = ast_.patterns
        len_fst_body = len(fst_body)
        self_tail_sep = (ast.rest and stop == len_body) or None

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body2[-1].f, len_fst_body,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'keys', 'patterns', ',', self_tail_sep)

        _put_slice_asts2(self, start, stop, 'patterns', body, body2, fst_, fst_body, fst_body2)

    put_slice_sep_end(self, end_params)

    if self_tail_sep:  # if there is a **rest and we removed tail element so here we make sure there is a space between comma of the new last element and the **rest
        self._maybe_ins_separator(*body2[-1].f.loc[2:], True)  # this will only maybe add a space, comma is already there


def _put_slice_MatchOr_patterns(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    fst_ = _code_to_slice_MatchOr(self, code, one, options)
    len_body = len(body := self.a.patterns)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    self_norm = _get_norm_option('norm_self', 'matchor_norm', options)

    if not fst_:
        if not len_slice:
            return

        if not (len_left := len_body - len_slice):
            if self_norm:
                raise ValueError("cannot delete all MatchOr.patterns without norm_self=False")

        elif len_left == 1 and self_norm == 'strict':
            raise ValueError("cannot del MatchOr to length 1 with matchor_norm='strict'")

        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0, *self.loc,
                                         options, 'patterns', None, '|', False)

        _put_slice_asts(self, start, stop, 'patterns', body, None, None)

    else:
        len_fst_body = len(fst_body := fst_.a.patterns)

        if (len_body - len_slice + len_fst_body) == 1 and self_norm == 'strict':
            raise NodeError("cannot put MatchOr to length 1 with matchor_norm='strict'")

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body, *self.loc,
                                         options, 'patterns', None, '|', False)

        _put_slice_asts(self, start, stop, 'patterns', body, fst_, fst_body)

    put_slice_sep_end(self, end_params)

    _maybe_fix_MatchOr(self, self_norm)


def _put_slice_type_params(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """An empty `Tuple` is accepted as a zero-element `type_params` slice."""

    fst_ = _code_to_slice__type_params(self, code, one, options)
    len_body = len(body := (ast := self.a).type_params)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    bound, (name_ln, name_col) = (
        (loc_TypeAlias_type_params_brackets if isinstance(ast, TypeAlias) else
         loc_ClassDef_type_params_brackets if isinstance(ast, ClassDef) else
         loc_FunctionDef_type_params_brackets)  # FunctionDef, AsyncFunctionDef
    )(self)

    if bound:
        bound_ln, bound_col, bound_end_ln, bound_end_col = bound

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body:  # deleting everything so remove brackets
            self._put_src(None, name_ln, name_col, bound_end_ln, bound_end_col, False)

            end_params = None

        else:
            end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                             bound_ln, bound_col + 1, bound_end_ln, bound_end_col - 1,
                                             options, 'type_params')

        _put_slice_asts(self, start, stop, 'type_params', body, None, None)

    else:
        if not body:  # brackets don't exist, add them first
            self._put_src('[]', name_ln, name_col, name_ln, name_col, False)

            bound_ln = bound_end_ln = name_ln
            bound_col = bound_end_col = name_col + 1

        len_fst_body = len(fst_body := fst_.a.type_params)

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'type_params')

        _put_slice_asts(self, start, stop, 'type_params', body, fst_, fst_body)

    if end_params:
        put_slice_sep_end(self, end_params)


def _put_slice__slice(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    static = _SLICE_STATICS[(ast := self.a).__class__]
    fst_ = static.code_to(self, code, one, options)
    len_body = len(body := getattr(ast, field))
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_ and not len_slice:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, field, None, static.sep, static.self_tail_sep)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := getattr(fst_.a, field))

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, field, None, static.sep, static.self_tail_sep)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield(field, i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield(field, i)

    put_slice_sep_end(self, end_params)


# ......................................................................................................................

class slicestatic(NamedTuple):
    field:         str
    code_to:       Callable[[fst.FST, Code, bool, dict], fst.FST]
    sep:           str
    self_tail_sep: bool | Literal[0, 1] | None
    ret_tail_sep:  bool | Literal[0, 1] | None


_SLICE_STATICS = {
    _Assign_targets: slicestatic('targets', _code_to_slice__Assign_targets, '=', True, True),
    _aliases:        slicestatic('names', _code_to_slice__aliases, ',', False, False),
    _withitems:      slicestatic('items', _code_to_slice__withitems, ',', False, False),
    _type_params:    slicestatic('type_params', _code_to_slice__type_params, ',', False, False),
}


# ----------------------------------------------------------------------------------------------------------------------
# put raw

def _fixup_slice_index_for_raw(len_: int, start: int, stop: int) -> tuple[int, int]:
    start, stop = _fixup_slice_indices(len_, start, stop)

    if start == stop:
        raise ValueError('cannot insert in raw slice put')

    return start, stop


def _loc_slice_raw_put_decorator_list(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    start, stop = _fixup_slice_index_for_raw(len(decos := self.a.decorator_list), start, stop)
    ln, col, _, _ = decos[start].f.loc
    ln, col = prev_find(self.root._lines, 0, 0, ln, col, '@')  # we can use '0, 0' because we know "@" starts on a newline
    _, _, end_ln, end_col = decos[stop - 1].f.pars()

    return ln, col, end_ln, end_col, start, stop, decos


def _loc_slice_raw_put_Global_Nonlocal_names(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    start, stop = _fixup_slice_index_for_raw(len(names := self.a.names), start, stop)
    (ln, col, _, _), (_, _, end_ln, end_col) = loc_Global_Nonlocal_names(self, start, stop - 1)

    return ln, col, end_ln, end_col, start, stop, names


def _loc_slice_raw_put_Dict(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    start, stop = _fixup_slice_index_for_raw(len(values := self.a.values), start, stop)
    ln, col, _, _ = self._loc_maybe_key(start, True)
    _, _, end_ln, end_col = values[stop - 1].f.pars()

    return ln, col, end_ln, end_col, start, stop, values


def _loc_slice_raw_put_Compare(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    start, stop = _fixup_slice_index_for_raw(len(ops := (ast := self.a).ops), start, stop)
    ln, col, _, _ = ops[start].f.loc
    _, _, end_ln, end_col = (comparators := ast.comparators)[stop - 1].f.pars()

    return ln, col, end_ln, end_col, start, stop, comparators


def _loc_slice_raw_put_comprehension_ifs(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    start, stop = _fixup_slice_index_for_raw(len(ifs := self.a.ifs), start, stop)
    ln, col, _, _ = (ffirst := ifs[start].f).loc
    end_ln, end_col = prev_bound(ffirst)
    ln, col = prev_find(self.root._lines, end_ln, end_col, ln, col, 'if')
    _, _, end_ln, end_col = ifs[stop - 1].f.pars()

    return ln, col, end_ln, end_col, start, stop, ifs


def _loc_slice_raw_put_MatchMapping(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    start, stop = _fixup_slice_index_for_raw(len(keys := (ast := self.a).keys), start, stop)
    ln, col, _, _ = keys[start].f.loc
    _, _, end_ln, end_col = (patterns := ast.patterns)[stop - 1].f.pars()

    return ln, col, end_ln, end_col, start, stop, patterns


def _loc_slice_raw_put_default(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    if (body := getattr(self.a, field, None)) is None or not isinstance(body, list):
        raise ValueError(f'cannot put raw slice to {self.a.__class__.__name__}.{field}')

    start, stop = _fixup_slice_index_for_raw(len(body), start, stop)
    ln, col, _, _ = body[start].f.pars(shared=False)
    _, _, end_ln, end_col = body[stop - 1].f.pars(shared=False)

    return ln, col, end_ln, end_col, start, stop, body


def _loc_slice_raw_put(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    """Get location of a raw slice. Sepcial cases for decorators, comprehension ifs and other nodes."""

    return _LOC_SLICE_RAW_PUT_FUNCS.get((self.a.__class__, field), _loc_slice_raw_put_default)(self, start, stop, field)


_LOC_SLICE_RAW_PUT_FUNCS = {
    (FunctionDef, 'decorator_list'):      _loc_slice_raw_put_decorator_list,
    (AsyncFunctionDef, 'decorator_list'): _loc_slice_raw_put_decorator_list,
    (ClassDef, 'decorator_list'):         _loc_slice_raw_put_decorator_list,
    (Global, 'names'):                    _loc_slice_raw_put_Global_Nonlocal_names,
    (Nonlocal, 'names'):                  _loc_slice_raw_put_Global_Nonlocal_names,
    (Dict, ''):                           _loc_slice_raw_put_Dict,
    (Compare, ''):                        _loc_slice_raw_put_Compare,
    (comprehension, 'ifs'):               _loc_slice_raw_put_comprehension_ifs,
    (MatchMapping, ''):                   _loc_slice_raw_put_MatchMapping,
}


def _singleton_needs_comma(fst_: fst.FST) -> bool:
    """Whether a singleton value in this container needs a trailing comma or not."""

    return (isinstance(a := fst_.a, Tuple) or
            (isinstance(a, MatchSequence) and not fst_._is_delimited_seq('patterns', '[]')))  # MatchSequence because it can be undelimited or delimited with parentheses and in that case a singleton needs a trailing comma


def _adjust_slice_raw_ast(
    self: fst.FST,
    code: AST,
    field: str,
    one: bool,
    options: Mapping[str, Any],
    put_ln: int,
    put_col: int,
    put_end_ln: int,
    put_end_col: int,
    start: int,
    stop: int,
    body2: list[AST],
) -> tuple[AST | list[str], int, int, int, int]:
    """Adjust `code` and put location when putting raw from an `AST`. Currently just trailing comma stuff."""

    lines = self.root._lines

    code = reduce_ast(code, True)

    if ((code_is_tuple := isinstance(code, Tuple)) or
        (code_is_normal := isinstance(code, (List, Set, Dict, MatchSequence, MatchMapping))) or
        isinstance(code, (_withitems, _aliases, _type_params))
    ):  # all nodes which are separated by comma at top level
        src = unparse(code)

        if not one:  # strip delimiters and remove singleton Tuple trailing comma if present
            if code_is_tuple:
                src = src[1 : (-2 if len(code.elts) == 1 else -1)]

                len_code_body = len(getattr(code, 'elts', ()))

            elif code_is_normal:
                src = src[1 : -1]

                len_code_body = len(getattr(code, 'elts', ()) or getattr(code, 'keys', ()) or
                                    getattr(code, 'patterns', ()))

            else:
                len_code_body = len(getattr(code, 'items', ()) or getattr(code, 'names', ()) or
                                    getattr(code, 'type_params', ()))

            if not len_code_body:
                raise NodeError('cannot put raw empty slice')

        elif not code_is_tuple and not code_is_normal:
            raise NodeError('cannot put special slice as one')
        else:
            len_code_body = 1

        if stop == len(body2) and _singleton_needs_comma(self):
            comma = next_find(lines, put_end_ln, put_end_col, self.end_ln, self.end_col, ',', True)  # trailing comma

            if len_code_body != 1:
                if comma and comma[1] == put_end_col and comma[0] == put_end_ln:
                    put_end_col += 1  # overwrite trailing singleton tuple comma which follows immediately after single element

            elif not start and not comma:
                src += ','  # add trailing comma to what will be singleton tuple

        code = src

    return code, put_ln, put_col, put_end_ln, put_end_col


def _adjust_slice_raw_fst(
    self: fst.FST,
    code: fst.FST,
    field: str,
    one: bool,
    options: Mapping[str, Any],
    put_ln: int,
    put_col: int,
    put_end_ln: int,
    put_end_col: int,
    start: int,
    stop: int,
    body2: list[AST],
) -> tuple[fst.FST | list[str], int, int, int, int]:
    """Adjust `code` and put location when putting raw from an `FST`."""

    lines = self.root._lines

    if not code.is_root:
        raise ValueError('expecting root node')

    code_ast = reduce_ast(code.a, True)

    if ((code_is_normal := isinstance(code_ast, (Tuple, List, Set, Dict, MatchSequence, MatchMapping))) or
        isinstance(code_ast, (_withitems, _aliases, _type_params))
    ):  # all nodes which are separated by comma at top level
        code_fst = code_ast.f
        code_lines = code._lines

        if not one:  # strip delimiters (if any) and everything before and after actual node
            ln, col, end_ln, end_col = code_fst.loc

            if (code_is_normal and
                not (code_fst._is_parenthesized_tuple() is False or code_fst._is_delimited_matchseq() == '')  # don't strip nonexistent delimiters if is unparenthesized Tuple or MatchSequence or is a special slice
            ):
                col += 1
                end_col -= 1
                col_offset = code_ast.col_offset = code_ast.col_offset + 1
                end_col_offset = code_ast.end_col_offset = code_ast.end_col_offset - 1

                if parent := code_fst.parent:  # this will be an `Expr` if present
                    parenta = parent.a
                    parenta.col_offset = col_offset
                    parenta.end_col_offset = end_col_offset

                    assert isinstance(parenta, Expr)

            code._put_src(None, end_ln, end_col, len(code_lines) - 1, len(code_lines[-1]))
            code._put_src(None, 0, 0, ln, col, False)  # we are counting on this to _touch() everything because of possible assignments above to col_offset and end_col_offset

            if code_is_normal:
                code_body2 = (getattr(code_ast, 'elts', ()) or getattr(code_ast, 'values', ()) or
                              getattr(code_ast, 'patterns', ()))
            else:
                code_body2 = (getattr(code_ast, 'items', ()) or getattr(code_ast, 'names', ()) or
                              getattr(code_ast, 'type_params', ()))

            if not (len_code_body2 := len(code_body2)):
                raise NodeError('cannot put raw empty slice')

            _, _, end_ln, end_col = code_body2[-1].f.pars()

            code_comma = next_find(code_lines, end_ln, end_col, code_fst.end_ln, code_fst.end_col, ',', True)  # trailing comma

            code_comma_is_explicit = code_comma and (  # explicit comma - not needed or not in normal position
                (len_code_body2 >= 2) or
                code_comma[1] != end_col or code_comma[0] != end_ln or
                not _singleton_needs_comma(code_fst)
            )

        elif not code_is_normal:
            raise NodeError('cannot put special slice as one')

        else:
            if code_fst._is_parenthesized_tuple() is False:  # only Tuple or MatchMapping could be naked and needs to be delimited, everything else stays as-is
                code_fst._delimit_node()
            elif code_fst._is_delimited_matchseq() == '':
                code_fst._delimit_node(delims='[]')

            code_body2 = [code_ast]
            code_comma = code_comma_is_explicit = None
            len_code_body2 = 1

        if comma := next_find(lines, put_end_ln, put_end_col, self.end_ln, self.end_col, ',', True):  # trailing comma
            if (code_comma_is_explicit or
                (len_code_body2 > 1 and  # code has no comma because otherwise it would be explicit
                 len(body2) == 1 and _singleton_needs_comma(self) and  # self is singleton and singleton needs comma
                 comma[1] == put_end_col and comma[0] == put_end_ln)  # that comma follows right after element and so is not explicit and can be deleted
            ):
                put_end_ln, put_end_col = comma
                put_end_col += 1

            elif code_comma:  # otherwise if code has comma we remove it and keep the comma that is already in self
                code._put_src(None, ln := code_comma[0], col := code_comma[1], ln, col + 1, True)

        elif code_comma_is_explicit:
            pass  # noop

        elif not start and stop == len(body2) and len_code_body2 == 1 and _singleton_needs_comma(self):  # will result in singleton which needs trailing comma
            if not code_comma:
                code_lines[-1] = bistr(code_lines[-1] + ',')

        elif code_comma:
            code._put_src(None, ln := code_comma[0], col := code_comma[1], ln, col + 1, True)

    return code, put_ln, put_col, put_end_ln, put_end_col


def _put_slice_raw(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> Union[Self, fst.FST, None]:  # -> Self or reparsed Self
    """Put a raw slice to `self`. Currently just trailing comma stuff."""

    if code is None:
        raise ValueError('cannot delete in raw slice put')

    put_ln, put_col, put_end_ln, put_end_col, start, stop, body2 = _loc_slice_raw_put(self, start, stop, field)

    if isinstance(code, AST):
        code, put_ln, put_col, put_end_ln, put_end_col = (
            _adjust_slice_raw_ast(self, code, field, one, options,
                                  put_ln, put_col, put_end_ln, put_end_col, start, stop, body2))

    elif isinstance(code, fst.FST):
        code, put_ln, put_col, put_end_ln, put_end_col = (
            _adjust_slice_raw_fst(self, code, field, one, options,
                                  put_ln, put_col, put_end_ln, put_end_col, start, stop, body2))

    self._reparse_raw(code, put_ln, put_col, put_end_ln, put_end_col)

    return self if self.a else self.repath()


# ----------------------------------------------------------------------------------------------------------------------
# "public"

def _get_slice(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Get a slice of child nodes from `self`."""

    if not (handler := _GET_SLICE_HANDLERS.get((self.a.__class__, field))):
        raise ValueError(f"cannot get slice from {self.a.__class__.__name__}{f'.{field}' if field else ''}")

    if cut:
        modifying = self._modifying(field).enter()

    ret = handler(self, start, stop, field, cut, options)

    if cut:
        modifying.success()

    return ret


_GET_SLICE_HANDLERS = {
    (Module, 'body'):                         _get_slice_stmtish,  # stmt*
    (Interactive, 'body'):                    _get_slice_stmtish,  # stmt*
    (FunctionDef, 'body'):                    _get_slice_stmtish,  # stmt*
    (AsyncFunctionDef, 'body'):               _get_slice_stmtish,  # stmt*
    (ClassDef, 'body'):                       _get_slice_stmtish,  # stmt*
    (For, 'body'):                            _get_slice_stmtish,  # stmt*
    (For, 'orelse'):                          _get_slice_stmtish,  # stmt*
    (AsyncFor, 'body'):                       _get_slice_stmtish,  # stmt*
    (AsyncFor, 'orelse'):                     _get_slice_stmtish,  # stmt*
    (While, 'body'):                          _get_slice_stmtish,  # stmt*
    (While, 'orelse'):                        _get_slice_stmtish,  # stmt*
    (If, 'body'):                             _get_slice_stmtish,  # stmt*
    (If, 'orelse'):                           _get_slice_stmtish,  # stmt*
    (With, 'body'):                           _get_slice_stmtish,  # stmt*
    (AsyncWith, 'body'):                      _get_slice_stmtish,  # stmt*
    (Try, 'body'):                            _get_slice_stmtish,  # stmt*
    (Try, 'orelse'):                          _get_slice_stmtish,  # stmt*
    (Try, 'finalbody'):                       _get_slice_stmtish,  # stmt*
    (TryStar, 'body'):                        _get_slice_stmtish,  # stmt*
    (TryStar, 'orelse'):                      _get_slice_stmtish,  # stmt*
    (TryStar, 'finalbody'):                   _get_slice_stmtish,  # stmt*
    (ExceptHandler, 'body'):                  _get_slice_stmtish,  # stmt*
    (match_case, 'body'):                     _get_slice_stmtish,  # stmt*

    (Match, 'cases'):                         _get_slice_stmtish,  # match_case*
    (Try, 'handlers'):                        _get_slice_stmtish,  # excepthandler*
    (TryStar, 'handlers'):                    _get_slice_stmtish,  # excepthandlerstar*

    (Dict, ''):                               _get_slice_Dict,  # key:value*

    (Set, 'elts'):                            _get_slice_Set_elts,  # expr*
    (List, 'elts'):                           _get_slice_List_elts,  # expr*
    (Tuple, 'elts'):                          _get_slice_Tuple_elts,  # expr*

    (FunctionDef, 'decorator_list'):          _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (AsyncFunctionDef, 'decorator_list'):     _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (ClassDef, 'decorator_list'):             _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (ClassDef, 'bases'):                      _get_slice_ClassDef_bases,  # expr*
    (Delete, 'targets'):                      _get_slice_Delete_targets,  # expr*
    (Assign, 'targets'):                      _get_slice_Assign_targets,  # expr*
    (BoolOp, 'values'):                       _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Compare, ''):                            _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Call, 'args'):                           _get_slice_Call_args,  # expr*
    (comprehension, 'ifs'):                   _get_slice_NOT_IMPLEMENTED_YET,  # expr*

    (ListComp, 'generators'):                 _get_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (SetComp, 'generators'):                  _get_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (DictComp, 'generators'):                 _get_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (GeneratorExp, 'generators'):             _get_slice_NOT_IMPLEMENTED_YET,  # comprehension*

    (ClassDef, 'keywords'):                   _get_slice_NOT_IMPLEMENTED_YET,  # keyword*
    (Call, 'keywords'):                       _get_slice_NOT_IMPLEMENTED_YET,  # keyword*

    (Import, 'names'):                        _get_slice_Import_names,  # alias*
    (ImportFrom, 'names'):                    _get_slice_ImportFrom_names,  # alias*

    (With, 'items'):                          _get_slice_With_AsyncWith_items,  # withitem*
    (AsyncWith, 'items'):                     _get_slice_With_AsyncWith_items,  # withitem*

    (MatchSequence, 'patterns'):              _get_slice_MatchSequence_patterns,  # pattern*
    (MatchMapping, ''):                       _get_slice_MatchMapping,  # key:pattern*
    (MatchClass, 'patterns'):                 _get_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchOr, 'patterns'):                    _get_slice_MatchOr_patterns,  # pattern*

    (FunctionDef, 'type_params'):             _get_slice_type_params,  # type_param*
    (AsyncFunctionDef, 'type_params'):        _get_slice_type_params,  # type_param*
    (ClassDef, 'type_params'):                _get_slice_type_params,  # type_param*
    (TypeAlias, 'type_params'):               _get_slice_type_params,  # type_param*

    (Global, 'names'):                        _get_slice_Global_Nonlocal_names,  # identifier*
    (Nonlocal, 'names'):                      _get_slice_Global_Nonlocal_names,  # identifier*

    (JoinedStr, 'values'):                    _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (TemplateStr, 'values'):                  _get_slice_NOT_IMPLEMENTED_YET,  # expr*

    (_ExceptHandlers, 'handlers'):            _get_slice_stmtish,  # ExceptHandler*
    (_match_cases, 'cases'):                  _get_slice_stmtish,  # match_case*
    (_Assign_targets, 'targets'):             _get_slice__slice,  # expr*
    # (_Assign_comprehension_ifs, 'ifs'):       _get_slice__slice,
    (_aliases, 'names'):                      _get_slice__slice,  # alias*
    (_withitems, 'items'):                    _get_slice__slice,  # withitem*
    (_type_params, 'type_params'):            _get_slice__slice,  # type_param*
}


def _put_slice(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> Union[Self, fst.FST, None]:  # -> Self or reparsed Self or could disappear due to raw
    """Put an a slice of child nodes to `self`."""

    if code is self.root:  # don't allow own root to be put to self
        raise ValueError('circular put detected')

    if options.get('to') is not None:
        raise ValueError("cannot put slice with 'to' option")

    raw = fst.FST.get_option('raw', options)
    nonraw_exc = None

    if raw is not True:
        try:
            if not (handler := _PUT_SLICE_HANDLERS.get((self.a.__class__, field))):  # allow raw to handle some non-contiguous list fields
                raise NodeError(f"cannot put slice to {self.a.__class__.__name__}{f'.{field}' if field else ''}",
                                rawable=True)

            with self._modifying(field):
                handler(self, code, start, stop, field, one, options)

            return self

        except (NodeError, SyntaxError, NotImplementedError) as exc:
            if not raw or (isinstance(exc, NodeError) and not exc.rawable):
                raise

            nonraw_exc = exc

    with self._modifying(field, True):
        try:
            return _put_slice_raw(self, code, start, stop, field, one, options)

        except Exception as raw_exc:
            raw_exc.__context__ = nonraw_exc

            raise raw_exc


_PUT_SLICE_HANDLERS = {
    (Module, 'body'):                         _put_slice_stmtish,  # stmt*
    (Interactive, 'body'):                    _put_slice_stmtish,  # stmt*
    (FunctionDef, 'body'):                    _put_slice_stmtish,  # stmt*
    (AsyncFunctionDef, 'body'):               _put_slice_stmtish,  # stmt*
    (ClassDef, 'body'):                       _put_slice_stmtish,  # stmt*
    (For, 'body'):                            _put_slice_stmtish,  # stmt*
    (For, 'orelse'):                          _put_slice_stmtish,  # stmt*
    (AsyncFor, 'body'):                       _put_slice_stmtish,  # stmt*
    (AsyncFor, 'orelse'):                     _put_slice_stmtish,  # stmt*
    (While, 'body'):                          _put_slice_stmtish,  # stmt*
    (While, 'orelse'):                        _put_slice_stmtish,  # stmt*
    (If, 'body'):                             _put_slice_stmtish,  # stmt*
    (If, 'orelse'):                           _put_slice_stmtish,  # stmt*
    (With, 'body'):                           _put_slice_stmtish,  # stmt*
    (AsyncWith, 'body'):                      _put_slice_stmtish,  # stmt*
    (Try, 'body'):                            _put_slice_stmtish,  # stmt*
    (Try, 'orelse'):                          _put_slice_stmtish,  # stmt*
    (Try, 'finalbody'):                       _put_slice_stmtish,  # stmt*
    (TryStar, 'body'):                        _put_slice_stmtish,  # stmt*
    (TryStar, 'orelse'):                      _put_slice_stmtish,  # stmt*
    (TryStar, 'finalbody'):                   _put_slice_stmtish,  # stmt*
    (ExceptHandler, 'body'):                  _put_slice_stmtish,  # stmt*
    (match_case, 'body'):                     _put_slice_stmtish,  # stmt*

    (Match, 'cases'):                         _put_slice_stmtish,  # match_case*
    (Try, 'handlers'):                        _put_slice_stmtish,  # excepthandler*
    (TryStar, 'handlers'):                    _put_slice_stmtish,  # excepthandlerstar*

    (Dict, ''):                               _put_slice_Dict,  # key:value*

    (Set, 'elts'):                            _put_slice_Set_elts,  # expr*
    (List, 'elts'):                           _put_slice_List_elts,  # expr*
    (Tuple, 'elts'):                          _put_slice_Tuple_elts,  # expr*

    (FunctionDef, 'decorator_list'):          _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (AsyncFunctionDef, 'decorator_list'):     _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (ClassDef, 'decorator_list'):             _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (ClassDef, 'bases'):                      _put_slice_ClassDef_bases,  # expr*
    (Delete, 'targets'):                      _put_slice_Delete_targets,  # expr*
    (Assign, 'targets'):                      _put_slice_Assign_targets,  # expr*
    (BoolOp, 'values'):                       _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Compare, ''):                            _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Call, 'args'):                           _put_slice_Call_args,  # expr*
    (comprehension, 'ifs'):                   _put_slice_NOT_IMPLEMENTED_YET,  # expr*

    (ListComp, 'generators'):                 _put_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (SetComp, 'generators'):                  _put_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (DictComp, 'generators'):                 _put_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (GeneratorExp, 'generators'):             _put_slice_NOT_IMPLEMENTED_YET,  # comprehension*

    (ClassDef, 'keywords'):                   _put_slice_NOT_IMPLEMENTED_YET,  # keyword*
    (Call, 'keywords'):                       _put_slice_NOT_IMPLEMENTED_YET,  # keyword*

    (Import, 'names'):                        _put_slice_Import_names,  # alias*
    (ImportFrom, 'names'):                    _put_slice_ImportFrom_names,  # alias*

    (With, 'items'):                          _put_slice_With_AsyncWith_items,  # withitem*
    (AsyncWith, 'items'):                     _put_slice_With_AsyncWith_items,  # withitem*

    (MatchSequence, 'patterns'):              _put_slice_MatchSequence_patterns,  # pattern*
    (MatchMapping, ''):                       _put_slice_MatchMapping,  # key:pattern*
    (MatchClass, 'patterns'):                 _put_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchOr, 'patterns'):                    _put_slice_MatchOr_patterns,  # pattern*

    (FunctionDef, 'type_params'):             _put_slice_type_params,  # type_param*
    (AsyncFunctionDef, 'type_params'):        _put_slice_type_params,  # type_param*
    (ClassDef, 'type_params'):                _put_slice_type_params,  # type_param*
    (TypeAlias, 'type_params'):               _put_slice_type_params,  # type_param*

    (Global, 'names'):                        _put_slice_Global_Nonlocal_names,  # identifier*
    (Nonlocal, 'names'):                      _put_slice_Global_Nonlocal_names,  # identifier*

    (JoinedStr, 'values'):                    _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (TemplateStr, 'values'):                  _put_slice_NOT_IMPLEMENTED_YET,  # expr*

    (_ExceptHandlers, 'handlers'):            _put_slice_stmtish,  # ExceptHandler*
    (_match_cases, 'cases'):                  _put_slice_stmtish,  # match_case*
    (_Assign_targets, 'targets'):             _put_slice__slice,  # expr*
    # (_Assign_comprehension_ifs, 'ifs'):       _put_slice__slice,
    (_aliases, 'names'):                      _put_slice__slice,  # alias*
    (_withitems, 'items'):                    _put_slice__slice,  # withitem*
    (_type_params, 'type_params'):            _put_slice__slice,  # type_param*
}


def is_slice_compatible(sig1: tuple[type[AST], str], sig2: tuple[type[AST], str]) -> bool:  # sig = (AST type, field)
    """Whether slices are compatible between these type / fields."""

    return ((v := _SLICE_COMAPTIBILITY.get(sig1)) == _SLICE_COMAPTIBILITY.get(sig2) and v is not None)


_SLICE_COMAPTIBILITY = {
    (Module, 'body'):                     'stmt*',
    (Interactive, 'body'):                'stmt*',
    (FunctionDef, 'body'):                'stmt*',
    (AsyncFunctionDef, 'body'):           'stmt*',
    (ClassDef, 'body'):                   'stmt*',
    (For, 'body'):                        'stmt*',
    (For, 'orelse'):                      'stmt*',
    (AsyncFor, 'body'):                   'stmt*',
    (AsyncFor, 'orelse'):                 'stmt*',
    (While, 'body'):                      'stmt*',
    (While, 'orelse'):                    'stmt*',
    (If, 'body'):                         'stmt*',
    (If, 'orelse'):                       'stmt*',
    (With, 'body'):                       'stmt*',
    (AsyncWith, 'body'):                  'stmt*',
    (Try, 'body'):                        'stmt*',
    (Try, 'orelse'):                      'stmt*',
    (Try, 'finalbody'):                   'stmt*',
    (TryStar, 'body'):                    'stmt*',
    (TryStar, 'orelse'):                  'stmt*',
    (TryStar, 'finalbody'):               'stmt*',
    (ExceptHandler, 'body'):              'stmt*',
    (match_case, 'body'):                 'stmt*',

    (Match, 'cases'):                     'match_case*',
    (Try, 'handlers'):                    'excepthandler*',
    (TryStar, 'handlers'):                'excepthandlerstar*',

    (Dict, ''):                           'expr:expr*',

    (Set, 'elts'):                        'expr*',
    (List, 'elts'):                       'expr*',
    (Tuple, 'elts'):                      'expr*',

    # (FunctionDef, 'decorator_list'):      'expr*',
    # (AsyncFunctionDef, 'decorator_list'): 'expr*',
    # (ClassDef, 'decorator_list'):         'expr*',
    # (ClassDef, 'bases'):                  'expr*',
    # (Delete, 'targets'):                  'expr*',
    # (Assign, 'targets'):                  'expr*',
    # (BoolOp, 'values'):                   'expr*',
    # (Compare, ''):                        'expr*',
    # (Call, 'args'):                       'expr*',
    # (comprehension, 'ifs'):               'expr*',

    # (ListComp, 'generators'):             'comprehension*',
    # (SetComp, 'generators'):              'comprehension*',
    # (DictComp, 'generators'):             'comprehension*',
    # (GeneratorExp, 'generators'):         'comprehension*',

    # (ClassDef, 'keywords'):               'keyword*',
    # (Call, 'keywords'):                   'keyword*',

    # (Import, 'names'):                    'alias*',
    # (ImportFrom, 'names'):                'alias*',

    # (With, 'items'):                      'withitem*',
    # (AsyncWith, 'items'):                 'withitem*',

    # (MatchSequence, 'patterns'):          'pattern*',
    # (MatchMapping, ''):                   'expr:pattern*',
    # (MatchOr, 'patterns'):                'patternor*',
    # (MatchClass, 'patterns'):             'pattern*',

    # (FunctionDef, 'type_params'):         'type_param*',
    # (AsyncFunctionDef, 'type_params'):    'type_param*',
    # (ClassDef, 'type_params'):            'type_param*',
    # (TypeAlias, 'type_params'):           'type_param*',

    # (Global, 'names'):                    'identifier*',
    # (Nonlocal, 'names'):                  'identifier*',

    # (JoinedStr, 'values'):                'expr*',
    # (TemplateStr, 'values'):              'expr*',
}
