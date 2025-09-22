"""Get and put slice. Some of the slice types are very specific, using `AST` containers in non-standard ways. Mosthly
this is to allow preservation of trivia and formatting, especially with different separators like `|` or `=`.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

import re
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
    _slice_Assign_targets,
    _slice_aliases,
    _slice_withitems,
    _slice_type_params,
)

from .astutil import (
    re_identifier, bistr, is_valid_target, is_valid_del_target, reduce_ast, set_ctx, copy_ast,
)

from .misc import (
    PYLT11, PYGE14,
    Self, NodeError, astfield, fstloc,
    re_empty_line_start, re_empty_line, re_line_trailing_space, re_empty_space, re_line_end_cont_or_comment,
    ParamsOffset,
    next_frag, prev_find, next_find, next_find_re, fixup_slice_indices,
    leading_trivia, trailing_trivia,
)

from .parsex import unparse

from .code import (
    Code,
    code_as_expr, code_as_expr_all, code_as_expr_arglike, code_as_Tuple, code_as_Assign_targets,
    code_as_alias, code_as_aliases,
    code_as_Import_name, code_as_Import_names,
    code_as_ImportFrom_name, code_as_ImportFrom_names,
    code_as_withitem, code_as_withitems,
    code_as_pattern,
    code_as_type_param, code_as_type_params,
)

from .fst_slice_old import _get_slice_stmtish, _put_slice_stmtish


_re_close_delim_or_space_or_end = re.compile(r'[)}\s\]:]|$')  # this is a very special set of terminations which are considered to not need a space before if a slice put ends with a non-space right before them

_re_sep_line_nonexpr_end = {  # empty line with optional separator and line continuation or a pure comment line
    ',': re.compile(r'\s*(?:,\s*)?(?:\\|#.*)?$'),
    '|': re.compile(r'\s*(?:\|\s*)?(?:\\|#.*)?$'),
    '=': re.compile(r'\s*(?:=\s*)?(?:\\|#.*)?$'),
}


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
#     S ,          (ClassDef, 'bases'):                    # expr*            -> Tuple[expr_arglike]        _parse_expr_arglikes  - keywords and Starred bases can mix
# *   S ,          (Call, 'args'):                         # expr*            -> Tuple[expr_arglike]        _parse_expr_arglikes  - keywords and Starred args can mix
#                                                                             .
# *   S ,          (Delete, 'targets'):                    # expr*            -> Tuple[target]              _parse_expr / restrict del_targets
# * ! N =          (Assign, 'targets'):                    # expr*            -> _slice_Assign_targets      _parse_Assign_targets
#                                                                             .
#                                                                             .
# *   S ,          (Global, 'names'):                      # identifier*,     -> Tuple[Name]                _parse_expr / restrict Names   - no trailing commas, unparenthesized
# *   S ,          (Nonlocal, 'names'):                    # identifier*,     -> Tuple[Name]                _parse_expr / restrict Names   - no trailing commas, unparenthesized
#                                                                             .
#                                                                             .
#   ! S ,          (ClassDef, 'keywords'):                 # keyword*         -> _slice_keywords            _parse_keywords  - keywords and Starred bases can mix
#   ! S ,          (Call, 'keywords'):                     # keyword*         -> _slice_keywords            _parse_keywords  - keywords and Starred args can mix
#                                                                             .
# * ! S ,          (FunctionDef, 'type_params'):           # type_param*      -> _slice_type_params         _parse_type_params
# * ! S ,          (AsyncFunctionDef, 'type_params'):      # type_param*      -> _slice_type_params         _parse_type_params
# * ! S ,          (ClassDef, 'type_params'):              # type_param*      -> _slice_type_params         _parse_type_params
# * ! S ,          (TypeAlias, 'type_params'):             # type_param*      -> _slice_type_params         _parse_type_params
#                                                                             .
# * ! S ,          (With, 'items'):                        # withitem*        -> _slice_withitems           _parse_withitems               - no trailing commas
# * ! S ,          (AsyncWith, 'items'):                   # withitem*        -> _slice_withitems           _parse_withitems               - no trailing commas
#                                                                             .
# * ! S ,          (Import, 'names'):                      # alias*           -> _slice_aliases             _parse_aliases_dotted          - no trailing commas
# * ! S ,          (ImportFrom, 'names'):                  # alias*           -> _slice_aliases             _parse_aliases_star            - no trailing commas
#                                                                             .
#                                                                             .
#   ! S            (ListComp, 'generators'):               # comprehension*   -> _slice_comprehensions      _parse_comprehensions
#   ! S            (SetComp, 'generators'):                # comprehension*   -> _slice_comprehensions      _parse_comprehensions
#   ! S            (DictComp, 'generators'):               # comprehension*   -> _slice_comprehensions      _parse_comprehensions
#   ! S            (GeneratorExp, 'generators'):           # comprehension*   -> _slice_comprehensions      _parse_comprehensions
#                                                                             .
#   ! S    if      (comprehension, 'ifs'):                 # expr*            -> _slice_comprehension_ifs   _parse_comprehension_ifs
#                                                                             .
#   ! S    @       (FunctionDef, 'decorator_list'):        # expr*            -> _slice_decorator_list      _parse_decorator_list
#   ! S    @       (AsyncFunctionDef, 'decorator_list'):   # expr*            -> _slice_decorator_list      _parse_decorator_list
#   ! S    @       (ClassDef, 'decorator_list'):           # expr*            -> _slice_decorator_list      _parse_decorator_list
#                                                                             .
#                                                                             .
#     N co         (Compare, 'ops':'comparators'):         # cmpop:expr*      -> expr or Compare            _parse_expr / restrict expr or Compare
#                                                                             .
#     N ao         (BoolOp, 'values'):                     # expr*            -> BoolOp                     _parse_expr / restrict BoolOp  - interchangeable between and / or
#                                                                             .
#                                                                             .
#                  (JoinedStr, 'values'):                  # Constant|FormattedValue*  -> JoinedStr
#                  (TemplateStr, 'values'):                # Constant|Interpolation*   -> TemplateStr


# * Tuple[target]          _parse_expr
#   Tuple[expr_arglike]    _parse_expr_arglikes
#   Tuple[keyword]         _parse_keywords
# * Tuple[type_param]      _parse_type_params
#   Tuple[withitem]        _parse_withitems
#   Tuple[comprehension]   _parse_comprehensions
# * Tuple[alias]           _parse_aliases_dotted
#   Tuple[alias]           _parse_aliases_star


# --- NOT CONTIGUOUS --------------------------------

# (arguments, 'posonlyargs'):           # arg*  - problematic because of defaults
# (arguments, 'args'):                  # arg*  - problematic because of defaults

# (arguments, 'kwonlyargs'):            # arg*  - maybe do as two-element, but is new type of two-element where the second element can be None
# (arguments, 'kw_defaults'):           # arg*

# could do argmnents slice as arguments instance (lots of logic needed on put)?

# (MatchClass, 'kwd_attrs'):            # identifier*  - maybe do as two-element
# (MatchClass, 'kwd_patterns'):         # pattern*


# ----------------------------------------------------------------------------------------------------------------------

def _locs_slice_seq(self: fst.FST, is_first: bool, is_last: bool, loc_first: fstloc, loc_last: fstloc,
                    bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                    trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None],
                    sep: str = ',', neg: bool = False,
                    ) -> tuple[fstloc, fstloc, str | None, tuple[int, int] | None]:
    r"""Slice locations for both copy and delete. Parentheses should already have been taken into account for the bounds
    and location. This function will find the separator if present and go from there for the trailing trivia. If trivia
    specifier has a `'-#'` for space in it and `neg` here is `True` then the copy location will not have extra space
    added but the delete location will.

    In the returned copy location, a leading newline means the slice wants to start on its own line and a trailing
    newline means the slice wants to end its own line. Both mean it wants to live on its own line.

    **Notes:** If `neg` is `True` (used for cut and del) and there was negative space found then the delete location
    will include the space but the copy location will not.

    **Parameters:**
    - `is_first`: Whether starts on first element.
    - `is_last`: Whether ends on last element.
    - `loc_first`: The full location of the first element, parentheses included.
    - `loc_last`: The full location of the last element, parentheses included. Must be `is` identical to `loc_first` if
        they are the same element.
    - (`bound_ln`, `bound_col`): End of previous element (past pars) or start of container (just past
        delimiters) if no previous element.
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
    - `trivia`: Standard option on how to handle leading and trailing comments and space, `None` means global default.
    - `neg`: Whether to return a different `del_loc` including negative space if `trivia` has it..

    **Returns:**
    - (`copy_loc`, `del_loc`, `del_indent`, `sep_end_pos`):
        - `copy_loc`: Where to copy.
        - `del_loc`: Where to remove (cut or delete or replace).
        - `del_indent`: String to put at start of `del_loc` after removal or `None` if original `loc_first` start
            location did not start its own line. Will be empty string if start location starts right at beginning of
            line.
        - `sep_end_pos`: Position right after separator `sep` if found after `loc_last`, else `None`.

    ```py
    '+' = copy_loc
    '-' = del_loc
    '=' = del_loc and return indent

    ... case 0 ...........................................................
    [  GET,  ]
     ++++++++
     --------
     not used

    ... case 1 ...........................................................
    [PRE, GET, POST]   [PRE, GET]   [PRE, GET,]   [PRE, GET, ]
          ++++               +++          ++++          ++++
          -----             ----         -----         ------

    ... case 2 ...........................................................
    [PRE, GET,\n   [PRE, GET, # trivia\n
          ++++           ++++
         -----          -----
     POST]          POST]
                   no comments requested

    ... case 3 ...........................................................
    [PRE, FIRST,\n   [PRE, GET,\n   [PRE, GET, # trivia\n
          ++++++++         ++++++         +++++++++++++++
         ---------        -------        --------------
     LAST,\n          # trivia\n     POST]
    ++++++++         +++++++++++
    ------           ---------
     POST]            POST]
    fallthrough
    from case 2

    ... case 4 ...........................................................
    [PRE,\n       [PRE,\n   [PRE,\n   [PRE,\n
     GET, POST]    GET]      GET,]     GET, ]
     ++++          +++       ++++      ++++
    =-----        =---      =----     =-----

    ... case 5 ...........................................................
    [PRE,\n        [PRE,\n        [PRE,\n       [PRE,\n       [PRE,\n
         ++             ++             ++            ++            ++
     FIRST,\n       # trivia\n     # trivia\n    # trivia\n    # trivia\n
    +++++++++      +++++++++++    +++++++++++   +++++++++++   +++++++++++
    =--------      -----------    -----------   -----------   -----------
     LAST, POST]    GET, POST]     GET]          GET,]         GET, ]
    ++++++         +++++          ++++          +++++         +++++
    -------        =-----         =---          =----         =-----
    fallthrough
    from case 4

    ... case 6 ...........................................................
    [PRE,\n
         ++
     GET,\n
    +++++++
    =------
     POST]
    ```
    """

    lines = self.root._lines
    single = loc_last is loc_first

    first_ln, first_col, last_end_ln, last_end_col = loc_first

    if not single:
        _, _, last_end_ln, last_end_col = loc_last

    if (sep and (frag := next_frag(lines, last_end_ln, last_end_col, bound_end_ln, bound_end_col)) and
        frag.src.startswith(sep)
    ):  # if separator present then set end of element to just past it
        sep_end_pos = end_pos = (last_end_ln := frag.ln, last_end_col := frag.col + len(sep))

    else:
        sep_end_pos = None
        end_pos = (last_end_ln, last_end_col)

    # if is_first and is_last:
    #     return ((l := fstloc(bound_ln, bound_col, bound_end_ln, bound_end_col)), l, None, sep_end_pos)  # case 0

    ld_comms, ld_space, ld_neg, tr_comms, tr_space, tr_neg = fst.FST._get_trivia_params(trivia, neg)

    ld_text_pos, ld_space_pos, indent = leading_trivia(lines, bound_ln, bound_col,  # start of text / space
                                                       first_ln, first_col, ld_comms, ld_space)
    tr_text_pos, tr_space_pos, _ = trailing_trivia(lines, bound_end_ln, bound_end_col,  # END of text / space
                                                   last_end_ln, last_end_col, tr_comms, tr_space)

    def calc_locs(ld_ln: int, ld_col: int, tr_ln: int, tr_col: int,
                  ) -> tuple[fstloc, fstloc, str | None, tuple[int, int] | None]:
        if indent is None:  # does not start line, no preceding trivia
            del_col = re_line_trailing_space.match(lines[first_ln], 0 if first_ln > bound_ln else bound_col,
                                                   first_col).start(1)

            if tr_ln == last_end_ln:  # does not extend past end of line (different from trailing_trivia() 'ends_line')
                if not is_last or lines[last_end_ln].startswith('#', tr_col):  # if there is a next element or trailing line comment then don't delete space before this element
                    del_col = first_col

                return (fstloc(first_ln, first_col, last_end_ln, last_end_col),
                        fstloc(first_ln, del_col, last_end_ln, tr_col),
                        None, sep_end_pos)  # case 1

            if tr_text_pos == end_pos and tr_ln == last_end_ln + 1:  # no comments, maybe trailing space on line, treat as if doesn't end line
                if single or not re_empty_line.match(lines[loc_last.ln], 0, loc_last.col):  # if multiple elements and last element starts its own line then fall through to next case, yes the re match can extend beyond starting bound (its fine since its just informative)
                    return (fstloc(first_ln, first_col, last_end_ln, last_end_col),
                            fstloc(first_ln, del_col, last_end_ln, last_end_col),
                            None, sep_end_pos)  # case 2

            return (fstloc(first_ln, first_col, tr_ln, tr_col),
                    fstloc(first_ln, del_col, l := tr_ln - 1, len(lines[l])),
                    None, sep_end_pos)  # case 3

        assert ld_col == 0

        if tr_ln == last_end_ln:  # does not extend past end of line (different from trailing_trivia() 'ends_line')
            if ld_ln == first_ln:  # starts on first line which is copied / deleted
                if single or not _re_sep_line_nonexpr_end[sep].match(lines[loc_first.end_ln], loc_first.end_col):  # if multiple elements and first element ends its own line then fall through to next case, yes the re match can extend beyond ending bound (its fine since its just informative)
                    return (fstloc(first_ln, first_col, last_end_ln, last_end_col),
                            fstloc(first_ln, ld_col, last_end_ln, tr_col),
                            indent, sep_end_pos)  # case 4, we do it this way to return this specific information that it starts a line but doesn't end one

            return ((fstloc((l := ld_ln - 1), len(lines[l]), last_end_ln, last_end_col)
                     if ld_ln else
                     fstloc(ld_ln, ld_col, last_end_ln, last_end_col)),
                    fstloc(ld_ln, ld_col, last_end_ln, tr_col),
                    indent, sep_end_pos)  # case 5

        return ((fstloc((l := ld_ln - 1), len(lines[l]), tr_ln, tr_col)
                 if ld_ln else
                 fstloc(ld_ln, ld_col, tr_ln, tr_col)),
                fstloc(ld_ln, ld_col, tr_ln, tr_col),
                indent, sep_end_pos)  # case 6

    ld_ln, ld_col = ld_space_pos or ld_text_pos
    tr_ln, tr_col = tr_space_pos or tr_text_pos

    cut_locs = calc_locs(ld_ln, ld_col, tr_ln, tr_col)

    # here we could just return cut_locs, the rest of the code differentiates between '-#' and '+#' locations if neg is True

    if ld_different := ld_space_pos and ld_neg and ld_space:
        if ld_text_pos[0] == ld_ln:  # if on same line then space was at start of line and there should be no difference
            ld_different = False

        else:
            ld_ln = ld_text_pos[0]  # this is where space would have been without negative
            ld_col = 0

    if tr_different := tr_space_pos and tr_neg and tr_space:
        if tr_text_pos[0] == tr_ln:  # if on same line then space was on line of element and there should be no difference
            tr_different = False

        else:  # text pos could still be at end of element line or beginning of new line, need to handle differently
            tr_ln, tr_col = tr_text_pos

            if tr_col:
                tr_ln += 1
                tr_col = 0

    if not (ld_different or tr_different):  # if negative space offsets would not affect locations then we are done
        return cut_locs  # really copy_locs here

    copy_locs = calc_locs(ld_ln, ld_col, tr_ln, tr_col)

    return copy_locs[:1] + cut_locs[1:]  # copy location from copy_locs and delete location and indent from cut_locs


def _offset_pos_by_params(self: fst.FST, ln: int, col: int, col_offset: int, parsoff: ParamsOffset) -> tuple[int, int]:
    """Position to offset `(ln, col)` with `col_offset` = `lines[ln].c2b(col)`, is assumed to be at or past the offset
    position."""

    at_ln = parsoff.ln == ln
    ln += parsoff.dln

    if at_ln:
        col = self.root._lines[ln].b2c(col_offset + parsoff.dcol_offset)

    return ln, col


def _locs_first_and_last(self: fst.FST, start: int, stop: int, body: list[AST], body2: list[AST],
                         ) -> tuple[fstloc, fstloc]:
    """Get the location of the first and last elemnts of a one or two-element sequence (assumed present)."""

    stop_1 = stop - 1

    if body2 is body:
        loc_first = body[start].f.pars()
        loc_last = loc_first if start == stop_1 else body[stop_1].f.pars()

    else:
        ln, col, _, _ = self._loc_maybe_dict_key(start, True, body)
        _, _, end_ln, end_col = body2[start].f.pars()
        loc_first = fstloc(ln, col, end_ln, end_col)

        if start == stop_1:
            loc_last = loc_first

        else:
            ln, col, _, _ = self._loc_maybe_dict_key(stop_1, True, body)
            _, _, end_ln, end_col = body2[stop_1].f.pars()
            loc_last = fstloc(ln, col, end_ln, end_col)

    return loc_first, loc_last


def _fixup_self_tail_sep_del(self: fst.FST, self_tail_sep: bool | Literal[0, 1] | None, start: int, stop: int,
                             len_body: int) -> bool | Literal[0, 1] | None:
    is_last = stop == len_body

    if self_tail_sep is None:
        return 0 if (start and is_last) else None
    elif not self_tail_sep:  # is False or == 0
        return self_tail_sep if (start and is_last) else None
    elif self_tail_sep is True:
        return None if is_last else True
    elif len_body - (stop - start) == 1:  # self_tail_sep == 1, only adds if single element remains otherwise noop
        return (None if is_last else 1)
    else:
        return (0 if is_last and start else None)


def _shorter_str(a: str, b: str) -> str:
    return a if len(a) < len(b) else b


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


def _maybe_set_end_pos(self: fst.FST, end_lineno: int, end_col_offset: int,
                       old_end_lineno: int, old_end_col_offset: int) -> None:
    """Maybe set end position if is not already at old position. If it is not then walk up parent chain setting those
    end positions to the new one but only as long as they are at an expected old end position. Used to fix end position
    which might have been offset by trailing trivia."""

    while True:
        if (co := getattr(a := self.a, 'end_col_offset', None)) is not None:  # because of ASTs which locations
            if co != old_end_col_offset or a.end_lineno != old_end_lineno:  # if parent doesn't end at expected location then we are done
                break

            a.end_lineno = end_lineno
            a.end_col_offset = end_col_offset

        self._touch()  # even if AST doesn't have location, it may be calculated and needs to be cleared out anyway

        if not (parent := self.parent) or self.next():
            break

        self = parent


def _maybe_fix_Assign_target0(self: fst.FST) -> None:
    """If `Assign` has `target`s and first target does not start at same location as `self` then delete everything in
    between so that it starts at `self`."""

    if targets := self.a.targets:
        t0_ln, t0_col, _, _ = targets[0].f.pars()
        self_ln, self_col, _, _ = self.loc

        if t0_col != self_col or t0_ln != self_ln:
            self._put_src(None, self_ln, self_col, t0_ln, t0_col, False)


# ----------------------------------------------------------------------------------------------------------------------
# get

def _get_slice_seq(self: fst.FST, start: int, stop: int, len_body: int, cut: bool, ast: AST,
                   ast_last: AST, loc_first: fstloc, loc_last: fstloc,
                   bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                   trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None = None,
                   field: str = 'elts', prefix: str = '', suffix: str = '', sep: str = ',',
                   self_tail_sep: bool | Literal[0, 1] | None = None,
                   ret_tail_sep: bool | Literal[0, 1] | None = None,
                   ) -> fst.FST:
    """Copy slice sequence source, dedent it, and create a new `FST` from that source and the new `AST` already made
    with the old locations (which will be updated). If the operation is a cut then the source in `self` will also be
    deleted. Trailing separators will be added / removed as needed and according to if they are in normal positions. If
    cut from `self` leaves an empty unparenthesized tuple then parentheses will NOT be added here.

    **Note:** Will NOT remove existing trailing separator from `self` sequence if it is not touched even if
    `self_tail_sep=False`.

    **WARNING!** (`bound_ln`, `bound_col`) is expected to be exactly the end of the previous element (past any closing
    pars) or the start of the container (past any opening delimiters) if no previous element. (`bound_end_ln`,
    `bound_end_col`) must be end of container just before closing delimiters.

    **Parameters:**
    - `start`, `stop`, `len_body`: Slice parameters, `len_body` being current length of field.
    - `ast`: The already build new `AST` that is being gotten. The elements being gotten must be in this with their
        current locations in the `self`.
    - `ast_last`: The `AST` of the last element copied or cut, not assumend to have `.f` `FST` attribute to begin with.
    - `loc_first`: The full location of the first element copied or cut, parentheses included.
    - `loc_last`: The full location of the last element copied or cut, parentheses included.
    - (`bound_ln`, `bound_col`): End of previous element (past pars) or start of container (just past
        delimiters) if no previous element. DIFFERENT FROM _put_slice_seq_begin()!!!
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters). This can be past last element of
        sequence if there are other things which follow and look like part of the sequence (like a `rest` in a
        `MatchMapping`).
    - `trivia`: Standard option on how to handle leading and trailing comments and space, `None` means global default.
    - `field`: Which field of is being gotten from. In the case of two-field sequences like `Dict` this should be the
        last field syntactically, `value` in the case of `Dict` and should always have valid entries and not `None`.
    - `prefix`, `suffix`: What delimiters to add to copied / cut span of elements (pars, brackets, curlies).
    - `sep`: The separator to use and check, comma for everything except maybe `'|'` for MatchOr.
    - `self_tail_sep`: Whether self needs a trailing separator after cut or no (including if end was not cut).
        - `None`: Leave it up to function (tuple singleton check or aesthetic decision).
        - `True`: Always add if not present.
        - `False`: Remove from remaining sequence if tail removed but not from remaining tail if it was not removed.
        - `1`: Add if not present and single element.
        - `0`: Remove if not aesthetically significant (present on same line as end of element), otherwise leave.
    - `ret_tail_sep`: Whether returned cut or copied slice needs a trailing separator or not.
        - `None`: Figure it out from length and if `ast` is `Tuple`.
        - `True`: Always add if not present.
        - `False`: Always remove if present.
        - `1`: Add if not present and single element.
        - `0`: Remove if not aesthetically significant (present on same line as end of element), otherwise leave.
    """

    lines = self.root._lines
    is_first = not start
    is_last = stop == len_body

    bound_end_col_offset = lines[bound_end_ln].c2b(bound_end_col)

    if ret_tail_sep and ret_tail_sep is not True and (stop - start) != 1:  # if ret_tail_sel == 1 and length will not be 1 then remove
        ret_tail_sep = 0

    if not cut:
        self_tail_sep = None
    else:
        self_tail_sep = _fixup_self_tail_sep_del(self, self_tail_sep, start, stop, len_body)

    # get locations and adjust for trailing separator keep or delete if possible to optimize

    copy_loc, del_loc, del_indent, sep_end_pos = _locs_slice_seq(self, is_first, is_last, loc_first, loc_last,
                                                                 bound_ln, bound_col, bound_end_ln, bound_end_col,
                                                                 trivia, sep, cut)

    copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

    if not ret_tail_sep and sep_end_pos:
        if is_last and ret_tail_sep is not False:  # if is last element and already had trailing separator then keep it but not if explicitly forcing no tail sep
            ret_tail_sep = True  # this along with sep_end_pos != None will turn the ret_tail_sep checks below into noop

        elif sep_end_pos[0] == copy_end_ln == loc_last.end_ln and sep_end_pos[1] == copy_end_col:  # optimization common case, we can get rid of unneeded trailing separator in copy by just not copying it if it is at end of copy range on same line as end of element
            copy_loc = fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col := loc_last.end_col)
            ret_tail_sep = True

    if self_tail_sep == 0:  # (or False), optimization common case, we can get rid of unneeded trailing separator in self by adding it to the delete block if del block starts on same line as previous element ends and there is not a comment on the line
        del_ln, _, del_end_ln, del_end_col = del_loc

        if del_ln == bound_ln and (del_end_ln != bound_ln or not lines[bound_ln].startswith('#', del_end_col)):
            del_loc = fstloc(bound_ln, bound_col, del_end_ln, del_end_col)  # there can be nothing but a separator and whitespace between these locations
            self_tail_sep = None

    # set location of root node and make the actual FST

    ast.lineno = copy_ln + 1
    ast.col_offset = lines[copy_ln].c2b(copy_col)
    ast.end_lineno = copy_end_ln + 1
    ast.end_col_offset = lines[copy_end_ln].c2b(copy_end_col)

    fst_, parsoff = self._make_fst_and_dedent(self, ast, copy_loc, prefix, suffix,
                                              del_loc if cut else None,
                                              [del_indent] if del_indent and del_loc.end_col else None,
                                              ret_params_offset=True)

    ast.col_offset = 0  # before prefix
    ast.end_col_offset = fst_._lines[-1].lenbytes  # after suffix

    fst_._touch()

    # add / remove trailing separators as needed

    if not ret_tail_sep:  # don't need or want return trailing separator
        if sep_end_pos:  # but have it
            _, _, last_end_ln, last_end_col = ast_last.f.loc  # this will now definitely have the .f attribute and FST, we don't use _poss_end() because field may not be the same
            _, _, fst_end_ln, fst_end_col = fst_.loc

            fst_._maybe_del_separator(last_end_ln, last_end_col, ret_tail_sep is False,
                                      fst_end_ln, fst_end_col - len(suffix), sep)

    elif not sep_end_pos:  # need return trailing separator and don't have it
        _, _, last_end_ln, last_end_col = ast_last.f.loc
        _, _, fst_end_ln, fst_end_col = fst_.loc

        fst_._maybe_ins_separator(last_end_ln, last_end_col, False, fst_end_ln, fst_end_col - len(suffix), sep)

    if self_tail_sep is not None:
        bound_end_ln, bound_end_col = _offset_pos_by_params(self, bound_end_ln, bound_end_col, bound_end_col_offset,
                                                            parsoff)

        if isinstance(last := getattr(self.a, field)[-1], AST):
            _, _, last_end_ln, last_end_col = last.f.loc

        else:  # Globals or Locals names, no last element with location so we use start of bound which is just past last untouched element which is now the last element
            last_end_ln = bound_ln
            last_end_col = bound_col

        if self_tail_sep:  # last element needs a trailing separator (singleton tuple maybe, requested by user)
            self._maybe_ins_separator(last_end_ln, last_end_col, False, bound_end_ln, bound_end_col, sep)
        else:  # removed tail element(s) and what is left doesn't need its trailing separator
            self._maybe_del_separator(last_end_ln, last_end_col, self_tail_sep is False, bound_end_ln, bound_end_col, sep)

    return fst_


def _locs_and_bound_get(self: fst.FST, start: int, stop: int, body: list[AST], body2: list[AST], off: int,
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


def _cut_or_copy_asts2(start: int, stop: int, field: str, field2: str, cut: bool, body: list[AST], body2: list[AST],
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

def _get_slice_NOT_IMPLEMENTED_YET(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                   cut: bool, options: Mapping[str, Any]) -> fst.FST:
    raise NotImplementedError('this is not implemented yet')


def _get_slice_Dict(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                    options: Mapping[str, Any]) -> fst.FST:
    """A `Dict` slice is just a normal `Dict`."""

    len_body = len(body := (ast := self.a).keys)
    body2 = ast.values
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_dict(from_=self)

    locs = _locs_and_bound_get(self, start, stop, body, body2, 1)
    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'values', cut, body, body2)
    ret_ast = Dict(keys=asts, values=asts2)

    return _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
                          options.get('trivia'), 'values', '{', '}', ',', 0, 0)


def _get_slice_Tuple_elts(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                          options: Mapping[str, Any]) -> fst.FST:
    """A `Tuple` slice is just a normal `Tuple`. It attempts to copy the parenthesization of the parent. The converse is
    not always true as a `Tuple` may serve as the container of a slice of other node types."""

    len_body = len(body := (ast := self.a).elts)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_tuple(from_=self)

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

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'elts', prefix, suffix, ',', 1, 1)

    if not is_par:
        fst_._maybe_fix_tuple(False)

    self._maybe_fix_tuple(is_par)

    return fst_


def _get_slice_List_elts(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                         options: Mapping[str, Any]) -> fst.FST:
    """A `List` slice is just a normal `List`."""

    len_body = len(body := (ast := self.a).elts)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_list(from_=self)

    locs = _locs_and_bound_get(self, start, stop, body, body, 1)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx = ast.ctx.__class__
    ret_ast = List(elts=asts, ctx=ctx())  # we set ctx() so that if it is not Load then set_ctx() below will recurse into it

    if not issubclass(ctx, Load):  # new List root object must have ctx=Load
        set_ctx(ret_ast, Load)

    return _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'elts', '[', ']', ',', 0, 0)


def _get_slice_Set_elts(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                         options: Mapping[str, Any]) -> fst.FST:
    """A `Set` slice is just a normal `Set` when it has elements. In the case of a zero-length `Set` it may be
    represented as `{*()}` or `set()` or as an invalid `AST` `Set` with curlies but no elements, according to
    options."""

    len_body = len(body := self.a.elts)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return (
            fst.FST._new_empty_set_curlies() if not (fix_set_get := self.get_option('fix_set_get', options)) else
            fst.FST._new_empty_set_call() if fix_set_get == 'call' else
            fst.FST._new_empty_tuple() if fix_set_get == 'tuple' else
            fst.FST._new_empty_set_star()  # True, 'star'
        )

    locs = _locs_and_bound_get(self, start, stop, body, body, 1)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ret_ast = Set(elts=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'elts', '{', '}', ',', 0, 0)

    self._maybe_fix_set(self.get_option('fix_set_self', options))

    return fst_


def _get_slice_Delete_targets(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                              cut: bool, options: Mapping[str, Any]) -> fst.FST:
    """The slice of `Delete.targets` is a normal unparenthesized `Tuple` contianing valid target types, which is also a
    valid python `Tuple`."""

    len_body = len(body := (ast := self.a).targets)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST._new_empty_tuple(from_=self)

    if cut and len_slice == len_body and self.get_option('fix_delete_self', options):
        raise ValueError("cannot cut all Delete.targets without fix_delete_self=False")

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bound_Delete_targets(self, start, loc_first)

    asts = _cut_or_copy_asts(start, stop, 'targets', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Del())  # we initially set to Del so that set_ctx() won't skip it

    set_ctx(ret_ast, Load)  # new Tuple root object must have ctx=Load

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                          options.get('trivia'), 'targets', '', '', ',', False, 1)

    fst_._maybe_fix_tuple(False)

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_set_end_pos(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                               ast.end_lineno, ast.end_col_offset)

        ln, col, _, _ = self.loc

        self._maybe_fix_joined_alnum(ln, col + 3)
        self._maybe_add_line_continuations()

    return fst_


def _get_slice_Assign_targets(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                              cut: bool, options: Mapping[str, Any]) -> fst.FST:
    len_body = len(body := self.a.targets)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_slice_Assign_targets(targets=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''],
                       from_=self)

    if cut and len_slice == len_body and self.get_option('fix_assign_self', options):
        raise ValueError("cannot cut all Assign.targets without fix_assign_self=False")

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bound_Assign_targets(self, start, loc_first)

    asts = _cut_or_copy_asts(start, stop, 'targets', cut, body)
    ret_ast = _slice_Assign_targets(targets=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                          options.get('trivia'), 'targets', '', '', '=', True, True)

    if cut:
        _maybe_fix_Assign_target0(self)
        self._maybe_add_line_continuations()

    return fst_


def _get_slice_With_AsyncWith_items(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                          cut: bool, options: Mapping[str, Any]) -> fst.FST:
    len_body = len(body := (ast := self.a).items)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_slice_withitems(items=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''],
                       from_=self)

    if cut and len_slice == len_body and self.get_option('fix_with_self', options):
        raise ValueError(f'cannot cut all {ast.__class__.__name__}.items without fix_with_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if stop == start else body[stop - 1].f.loc

    pars = self._loc_With_items_pars()  # may be pars or may be where pars would go from just after `with` to end of block header
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln = pars_ln
        bound_col = pars_col + pars_n

    asts = _cut_or_copy_asts(start, stop, 'items', cut, body)
    ret_ast = _slice_withitems(items=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, pars_end_ln, pars_end_col - pars_n,
                          options.get('trivia'), 'items', '', '', ',', False, False)

    if cut and not pars_n:  # only need to fix maybe if there are no parentheses
        if not self.is_enclosed_or_line(pars=False):  # if cut and no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_With_items_pars()  # will just give where pars should go (because maybe something like `async \\\n\\\n   with ...`)

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, False)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        elif not start and len_slice != len_body:  # if not adding pars then need to make sure cut didn't join new first `withitem` with the `with`
            ln, col, _, _ = pars.bound

            self._maybe_fix_joined_alnum(ln, col)

    return fst_


def _get_slice_Import_names(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                            cut: bool, options: Mapping[str, Any]) -> fst.FST:
    len_body = len(body := (ast := self.a).names)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_slice_aliases(names=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''],
                       from_=self)

    if cut and len_slice == len_body and self.get_option('fix_import_self', options):
        raise ValueError('cannot cut all Import.names without fix_import_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if stop == start else body[stop - 1].f.loc

    _, _, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln, bound_col, _, _ = loc_first

    asts = _cut_or_copy_asts(start, stop, 'names', cut, body)
    ret_ast = _slice_aliases(names=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                          options.get('trivia'), 'names', '', '', ',', False, False)

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_set_end_pos(self, (bn := body[-1]).end_lineno, bn.end_col_offset, ast.end_lineno, ast.end_col_offset)

        self._maybe_add_line_continuations()

    return fst_


def _get_slice_ImportFrom_names(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                cut: bool, options: Mapping[str, Any]) -> fst.FST:
    len_body = len(body := (ast := self.a).names)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_slice_aliases(names=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''],
                       from_=self)

    if cut and len_slice == len_body and self.get_option('fix_import_self', options):
        raise ValueError('cannot cut all ImportFrom.names without fix_import_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if stop == start else body[stop - 1].f.loc

    pars = self._loc_ImportFrom_names_pars()  # may be pars or may be where pars would go from just after `import` to end of node
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln = pars_ln
        bound_col = pars_col + pars_n

    asts = _cut_or_copy_asts(start, stop, 'names', cut, body)
    ret_ast = _slice_aliases(names=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, pars_end_ln, pars_end_col - pars_n,
                          options.get('trivia'), 'names', '', '', ',', False, False)

    if cut and not pars_n:  # only need to fix maybe if there are no parentheses
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_set_end_pos(self, (bn := body[-1]).end_lineno, bn.end_col_offset, ast.end_lineno, ast.end_col_offset)

        if not self.is_enclosed_or_line(pars=False):  # if cut and no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ImportFrom_names_pars()

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, True, False, self)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

    return fst_


def _get_slice_Global_Nonlocal_names(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                     cut: bool, options: Mapping[str, Any]) -> fst.FST:
    len_body = len((ast := self.a).names)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return self._new_empty_tuple(from_=self)

    if cut and len_slice == len_body and self.get_option('fix_global_self', options):
        raise ValueError(f'cannot cut all {ast.__class__.__name__}.names without fix_global_self=False')

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

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, ret_elts[-1],
                          loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                          options.get('trivia'), 'names', '', '', ',', False, 1)

    fst_._maybe_fix_tuple(False)  # this is in case of multiline elements to add pars, otherwise location would reparse different

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_set_end_pos(self, bound_ln + 1, lines[bound_ln].c2b(bound_col), ast.end_lineno, ast.end_col_offset)

        self._maybe_add_line_continuations()

    return fst_


def _get_slice_ClassDef_bases(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                              cut: bool, options: Mapping[str, Any]) -> fst.FST:
    """A `ClassDef.bases` slice is just a normal `Tuple`, with possibly expr_arglike elements which are invalid in a
    normal expression tuple."""

    len_body = len(body := (ast := self.a).bases)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if start == stop:
        return fst.FST._new_empty_tuple(from_=self)

    if keywords := ast.keywords:
        if (kw0_pos := keywords[0].f.loc[:2]) < body[stop - 1].f.loc[2:]:
            raise NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')

        self_tail_sep = True if body[-1].f.loc[2:] < kw0_pos else None

    else:
        self_tail_sep = None

    bound_ln, bound_col, bound_end_ln, bound_end_col = self._loc_ClassDef_bases_pars()  # definitely exist
    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    asts = _cut_or_copy_asts(start, stop, 'bases', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                          options.get('trivia'), 'bases', '(', ')', ',', self_tail_sep, len_slice == 1)

    if keywords:
        if cut and start and stop == len_body:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
            self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

    elif not body:  # everything was cut and no keywords, remove parentheses
        pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ClassDef_bases_pars()  # definitely exist

        self._put_src(None, pars_ln, pars_col, pars_end_ln, pars_end_col, False)

    return fst_


def _get_slice_Call_args(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                         options: Mapping[str, Any]) -> fst.FST:
    """A `Call.args` slice is just a normal `Tuple`, with possibly expr_arglike elements which are invalid in a normal
    expression tuple."""

    len_body = len(body := (ast := self.a).args)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if start == stop:
        return fst.FST._new_empty_tuple(from_=self)

    if keywords := ast.keywords:
        if (kw0_pos := keywords[0].f.loc[:2]) < body[stop - 1].f.loc[2:]:
            raise NodeError('cannot get this Call.args slice because it includes parts after a keyword')

        self_tail_sep = True if body[-1].f.loc[2:] < kw0_pos else None

    else:
        self_tail_sep = None

        if body and (f0 := body[0].f).is_solo_call_arg_genexp() and f0.pars(shared=False).n == -1:  # single call argument GeneratorExp shares parentheses with Call?
            f0._parenthesize_grouping()

    bound_ln, bound_col, bound_end_ln, bound_end_col = self._loc_call_pars()
    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    asts = _cut_or_copy_asts(start, stop, 'args', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                          options.get('trivia'), 'args', '(', ')', ',', self_tail_sep, len_slice == 1)

    if cut and start and keywords and stop == len_body:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
        self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

    return fst_


def _get_slice_MatchSequence_patterns(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                      cut: bool, options: Mapping[str, Any]) -> fst.FST:
    """A `MatchSequence` slice is just a normal `MatchSequence`. It attempts to copy the parenthesization of the
    parent."""

    len_body = len(body := self.a.patterns)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_matchseq(from_=self)

    delims = self.is_delimited_matchseq()
    locs = _locs_and_bound_get(self, start, stop, body, body, bool(delims))
    asts = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchSequence(patterns=asts)

    if delims:
        prefix, suffix = delims
        tail_sep = 1 if delims == '()' else 0

    else:
        prefix = suffix = delims = ''
        tail_sep = 1

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'patterns', prefix, suffix, ',', tail_sep, tail_sep)

    if not delims:
        fst_._maybe_fix_matchseq('')

    self._maybe_fix_matchseq(delims)

    return fst_


def _get_slice_MatchMapping(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                            options: Mapping[str, Any]) -> fst.FST:
    """A `MatchMapping` slice is just a normal `MatchMapping`."""

    len_body = len(body := (ast := self.a).keys)
    body2 = ast.patterns
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_matchmap(from_=self)

    locs = _locs_and_bound_get(self, start, stop, body, body2, 1)
    self_tail_sep = True if (rest := ast.rest) else 0

    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'patterns', cut, body, body2)
    ret_ast = MatchMapping(keys=asts, patterns=asts2, rest=None)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
                          options.get('trivia'), 'patterns', '{', '}', ',', self_tail_sep, False)

    if cut and start and rest and stop == len_body:  # if there is a rest element and we removed tail element we make sure there is a space between comma of the new last element and the rest
        self._maybe_ins_separator(*(f := body2[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

    return fst_


def _get_slice_MatchOr_patterns(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                cut: bool, options: Mapping[str, Any]) -> fst.FST:
    """A `MatchOr` slice is just a normal `MatchOr` when it has two elements or more. If it has one it may be returned
    as a single `pattern` or as an invalid single-element `MatchOr`. If the slice would wind up with zero elements it
    may raise and exception or return an invalid zero-element `MatchOr`, as specified by options."""

    len_body = len(body := self.a.patterns)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    fix_matchor_get = self.get_option('fix_matchor_get', options)
    fix_matchor_self = self.get_option('fix_matchor_self', options)

    if not len_slice:
        if fix_matchor_get:
            raise ValueError("cannot get empty slice from MatchOr without fix_matchor_get=False")

        return fst.FST._new_empty_matchor(from_=self)

    if len_slice == 1 and fix_matchor_get == 'strict':
        raise ValueError("cannot get length 1 slice from MatchOr with fix_matchor_get='strict'")

    if cut:
        if not (len_left := len_body - len_slice):
            if fix_matchor_self:
                raise ValueError("cannot cut all MatchOr.patterns without fix_matchor_self=False")

        elif len_left == 1 and fix_matchor_self == 'strict':
            raise ValueError("cannot cut MatchOr to length 1 with fix_matchor_self='strict'")

    locs = _locs_and_bound_get(self, start, stop, body, body, 0)
    asts = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchOr(patterns=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'patterns', '', '', '|', False, False)

    fst_._maybe_fix_matchor(bool(fix_matchor_get))
    self._maybe_fix_matchor(bool(fix_matchor_self))

    return fst_


def _get_slice_type_params(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                           options: Mapping[str, Any]) -> fst.FST:
    len_body = len(body := (ast := self.a).type_params)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(_slice_type_params([], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], from_=self)

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_func = (
        self._loc_typealias_type_params_brackets if isinstance(ast, TypeAlias) else
        self._loc_classdef_type_params_brackets if isinstance(ast, ClassDef) else
        self._loc_funcdef_type_params_brackets  # FunctionDef, AsyncFunctionDef
    )

    (bound_ln, bound_col, bound_end_ln, bound_end_col), _ = bound_func()

    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    asts = _cut_or_copy_asts(start, stop, 'type_params', cut, body)
    ret_ast = _slice_type_params(type_params=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                          options.get('trivia'), 'type_params', '', '', ',', False, False)

    if not body:  # everything was cut, need to remove brackets
        (_, _, bound_end_ln, bound_end_col), (name_ln, name_col) = bound_func()

        self._put_src(None, name_ln, name_col, bound_end_ln, bound_end_col, False)

    return fst_


def _get_slice__slice(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                      options: Mapping[str, Any]) -> fst.FST:
    """Our own general non-AST-compatible slice of some `type[AST]` list field."""

    static = _SLICE_STATICS[cls := (ast := self.a).__class__]
    len_body = len(body := getattr(ast, field))
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(cls([], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], from_=self)

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()

    asts = _cut_or_copy_asts(start, stop, field, cut, body)
    ret_ast = cls(asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1],
                          loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                          options.get('trivia'), field, '', '', static.sep, static.self_tail_sep, static.ret_tail_sep)

    return fst_

# ......................................................................................................................

def _get_slice(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
               options: Mapping[str, Any]) -> fst.FST:
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

    (_slice_Assign_targets, 'targets'):       _get_slice__slice,
    # (_slice_Assign_comprehension_ifs, 'ifs'): _get_slice__slice,
    (_slice_aliases, 'names'):                _get_slice__slice,
    (_slice_withitems, 'items'):              _get_slice__slice,
    (_slice_type_params, 'type_params'):      _get_slice__slice,
}


# ----------------------------------------------------------------------------------------------------------------------
# put

def _put_slice_seq_begin(self: fst.FST, start: int, stop: int, fst_: fst.FST | None,
                         fst_first: fst.FST | fstloc | None, fst_last: fst.FST | None, len_fst: int,
                         bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                         trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None,
                         ins_ln: int | None = None,
                         field: str = 'elts', field2: str | None = None, sep: str = ',',
                         self_tail_sep: bool | Literal[0, 1] | None = None,
                         ) -> tuple:
    r"""Indent a sequence source and put it to a location in existing sequence `self`. If `fst_` is `None` then will
    just delete in the same way that a cut operation would. Trailing separators will be added / removed as needed and
    according to if they are in normal positions, but not in this function, in `_put_slice_seq_end()`. If delete from
    `self` leaves an empty unparenthesized tuple then parentheses will NOT be added here.

    If an empty slice was going to be put we expect that it will be converted to a put `None` delete of existing
    elements. If an `fst_` is provided then it is assumed it has at least one element. No empty put to empty location,
    likewise no delete from empty location.

    This is the first in a two function sequence. After a call to this the source will be mostly put (except for maybe
    tail separator changes). The `AST` nodes being modified should be modified between this call and a call to
    `_put_slice_seq_end()`.

    **WARNING!** Here there be dragons!

    TODO: this really needs a refactor

    **Parameters:**
    - `start`, `stop`: Slice parameters.
    - `fst_`: The slice being put to `self` with delimiters stripped, or `None` for delete.
    - `fst_first`: The first element of the slice `FST` being put, or `None` if delete. Must be an `fstloc` for `Dict`
        key which is `None`.
    - `fst_last`: The last element of the slice `FST` being put, or `None` if delete.
    - `len_fst`: Number of elements in `FST` being put, or 0 if delete.
    - (`bound_ln`, `bound_col`): Start of container (just past delimiters). DIFFERENT FROM _get_slice_seq()!!!
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
    - `trivia`: Standard option on how to handle leading and trailing comments and space, `None` means global default.
    - `ins_ln`: Hint for line number where to insert if inserting, may not be honored if not possible.
    - `field`: Which field of `self` is being deleted / replaced / inserted to.
    - `field2`: If `self` is a two element sequence like `Dict` or `MatchMapping` then this should be the second field
        of each element, `values` or `patterns`.
    - `sep`: The separator to use and check, comma for everything except maybe `'|'` for MatchOr.
    - `self_tail_sep`: Whether self needs a trailing separator or no.
        - `None`: Leave it up to function (tuple singleton check or aesthetic decision).
        - `True`: Always add if not present.
        - `False`: Always remove if present.
        - `1`: Add if not present and single element.
        - `0`: Remove if not aesthetically significant (present on same line as end of element), otherwise leave.

    **Returns:**
    - `param`: A parameter to be passed to `_put_slice_seq_end(param)` to finish the put.
    """

    def get_indent_elts() -> str:
        nonlocal elts_indent_cached

        if elts_indent_cached is not ...:
            return elts_indent_cached

        if (elts_indent_cached := _get_element_indent(self, body, body2, start)) is not None:
            pass  # noop
        elif body:  # match indentation of our own first element
            elts_indent_cached = self_indent + ' ' * (self._loc_maybe_dict_key(0, True, body).col -
                                                      len(self_indent))
        else:
            elts_indent_cached = self_indent + self.root.indent  # default

        return elts_indent_cached

    lines = self.root._lines
    body = getattr(self.a, field)
    body2 = body if field2 is None else getattr(self.a, field2)
    len_body = len(body)
    is_first = not start
    is_last = stop == len_body
    is_del = fst_ is None
    is_ins = start == stop  # will never be true if fst_ is None
    is_ins_ln = False
    self_indent = self.get_indent()
    elts_indent_cached = ...  # cached value, ... means not present
    bound_end_col_offset = lines[bound_end_ln].c2b(bound_end_col)

    # maybe redent fst_ elements to match self element indentation

    if not is_del and len(fst_._lines) > 1:
        if (elts_indent := get_indent_elts()) is not None:  # we only do this if we have concrete indentation for elements of self
            ast_ = fst_.a
            fst_indent = _get_element_indent(fst_,
                                             getattr(ast_, fst_first.pfield.name if fst_first.is_FST else 'keys'),
                                             getattr(ast_, fst_last.pfield.name), 0)

            fst_._redent_lns(fst_indent or '', elts_indent[len(self_indent):])  # fst_._dedent_lns(fst_indent or ''), fst_._indent_lns(elts_indent[len(self_indent):])

    # locations

    if not is_first:  # if not first then bound start is at end of previous element
        _, _, bound_ln, bound_col = body2[start - 1].f.pars()

    if not is_ins:  # replace or delete, location is element span
        loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body2)

    else:  # insert, figure out location
        if ins_ln is not None:  # if an explicit insert line is passed then set insert location according to that
            if ins_ln <= bound_ln:
                loc_first = fstloc(bound_ln, bound_col, bound_ln, bound_col)

            else:
                if not is_last:
                    ln, col, _, _ = self._loc_maybe_dict_key(stop, True, body)

                else:
                    ln = bound_end_ln
                    col = bound_end_col

                if ins_ln >= ln:
                    loc_first = fstloc(ln, col, ln, col)

                else:
                    if not fst_._lines[0]:  # fst_ starts new line?
                        loc_first = fstloc(ins_ln, 0, ins_ln, 0)

                    else:
                        len_self_indent = len(self_indent)

                        if (ins_col := len(re_empty_line_start.match(lines[ins_ln]).group(0))) >= len_self_indent:
                            loc_first = fstloc(ins_ln, len_self_indent, ins_ln, len_self_indent)

                        else:
                            loc_first = fstloc(ins_ln, ins_col, ins_ln, ins_col)

                            fst_._put_src([' ' * (len_self_indent - ins_col)], 0, 0, 0, 0, False)

                is_ins_ln = not loc_first.col

        elif not is_last:  # just before next element
            ln, col, _, _ = self._loc_maybe_dict_key(stop, True, body)
            loc_first = fstloc(ln, col, ln, col)

        else:  # just past previous element or at start of bound
            loc_first = fstloc(bound_ln, bound_col, bound_ln, bound_col)

        loc_last = loc_first

    copy_loc, del_loc, del_indent, _ = _locs_slice_seq(self, is_first, is_last, loc_first, loc_last,
                                                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                                                       trivia, sep, is_del)

    put_ln, put_col, put_end_ln, put_end_col = del_loc

    # delete

    if is_del:
        put_lines = [del_indent] if del_indent and put_end_col else None
        self_tail_sep = _fixup_self_tail_sep_del(self, self_tail_sep, start, stop, len_body)

        if self_tail_sep == 0:  # (or False), optimization, we can get rid of unneeded trailing separator in self by adding it to the delete block if del block starts on same line as previous element ends and there is not a comment on the line
            if put_ln == bound_ln and (put_end_ln != bound_ln or not lines[bound_ln].startswith('#', put_end_col)):
                put_ln = bound_ln  # there can be nothing but a separator and whitespace between these locations
                put_col = bound_col
                self_tail_sep = None

    # insert or replace

    else:
        copy_ln, copy_col, _, _ = copy_loc

        put_lines = fst_._lines
        skip = 1
        post_indent = None  # this is a FULL indent in self, not a partial indent in fst_

        if re_line_end_cont_or_comment.match(put_lines[l := len(put_lines) - 1],  # if last line of fst_ is a comment or line continuation without a newline then add one (don't need to check pars for last line)
                                             0 if l > fst_last.end_ln else fst_last.end_col).group(1):
            put_lines.append(bistr(''))

        # newlines and indentation

        if not put_lines[0]:  # slice to put start with pure newline?
            if not put_col:  # start element being put to starts a new line?
                skip = 0

                fst_._put_src(None, 0, 0, 1, 0, False)  # delete leading pure newline in slice being put

            else:  # does not start a new line
                put_col = re_line_trailing_space.match(lines[put_ln], 0 if put_ln > bound_ln else bound_col,
                                                       put_col).start(1)  # eat whitespace before put newline

        elif not put_col:
            if del_indent:
                fst_._put_src(del_indent, 0, 0, 0, 0, False)  # add indent to start of first put line, this del_indent will not be indented by self_indent because of skip == 1

        else:  # leave the space between previous separator and self intact
            assert put_ln == copy_ln

            put_col = copy_col

        if not put_lines[-1]:  # slice put ends with pure newline?
            if not re_empty_space.match(lines[put_end_ln], put_end_col):  # something at end of put end line?
                if put_end_col:  # put doesn't end exactly on a brand new line so there is stuff to indent on line that's going to the next line
                    if is_last and put_end_ln == self.end_ln:  # just the end of the container, smaller of start of its line or open indent
                        post_indent = _shorter_str(re_empty_line_start.match(lines[put_end_ln]).group(0),
                                                   self_indent + ' ' * (self.col - len(self_indent)))
                    elif is_ins_ln and not (put_col or put_end_ln != put_ln):  # don't insert to zero-length location at exact start of line
                        put_end_col = copy_loc.end_col
                    elif del_indent is not None:  # have indent from locs function
                        post_indent = del_indent
                    else:
                        post_indent = get_indent_elts()

            else:  # nothing (or whitespace) at end of put end line
                if put_end_ln < bound_end_ln:  # only do this if we are not at end of container
                    fst_._put_src(None, l := len(put_lines) - 2, len(put_lines[l]), l + 1, 0, True)  # remove fst_ trailing newline to not duplicate and remove trailing space from self if present

                    if put_end_col != (ec := len(lines[put_end_ln])):
                        self._put_src(None, put_end_ln, put_end_col, put_end_ln, ec, True)

        elif not put_end_col and (put_col or put_end_ln != put_ln):  # we are putting slice before an element which starts a newline and slice doesn't have trailing newline (but not insert to zero-length location at exact start of line)
            if put_end_ln != put_ln:  # change put end to not delete last newline if possible
                put_end_col = len(lines[put_end_ln := put_end_ln - 1])
            else:  # otherwise add newline to slice
                put_lines.append(bistr(''))  # this doesn't need to be post_indent-ed because its just a newline, doesn't do indentation of following text

        elif (not put_lines[-1][-1].isspace() and   # putting something that ends with non-space to something that starts with not a closing delimiter or space, put space between
              not _re_close_delim_or_space_or_end.match(lines[put_end_ln], put_end_col) and
              (put_end_ln < self.end_ln or put_end_col < self.end_col)  # but not at the very end of self
        ):
            put_lines[-1] = bistr(put_lines[-1] + ' ')

        # trailing separator

        if is_last:
            if self_tail_sep is None:
                if pos := next_find(put_lines, fst_last.end_ln, fst_last.end_col, fst_.end_ln, fst_.end_col, sep):  # only remove if slice being put actually has trailing separator
                    if re_empty_space.match(put_lines[pos[0]], pos[1] + len(sep)):  # which doesn't have stuff following it
                        self_tail_sep = 0

            elif self_tail_sep == 1 and self_tail_sep is not True and (start or len_fst > 1):  # if 1 and length will not be 1 then remove
                self_tail_sep = 0

        elif self_tail_sep == 0:  # don't remove from tail if tail not touched
            self_tail_sep = None

        if self_tail_sep and self_tail_sep is not True and not (is_first and is_last and len_fst == 1):  # if want to add separator if only one element is left and not only one element is left then do nothing
            self_tail_sep = None

        # indent and offset source and FST to put

        fst_._indent_lns(self_indent, skip=skip)
        fst_._offset(0, 0, put_ln, lines[put_ln].c2b(put_col))

        if post_indent:  # we do this here like this because otherwise a completely empty line at the end of fst_ will not be indented at all in _indent_lns() which we may need to add self_indent alone
            put_lines[-1] = bistr(post_indent)

    # put source

    self_ln, self_col, self_end_ln, self_end_col = self.loc

    is_last_and_at_self_end = is_last and ((self_end_ln < put_end_ln) or
                                           (self_end_ln == put_end_ln and self_end_col <= put_end_col))

    if put_col == self_col and put_ln == self_ln:  # put at beginning of unenclosed sequence
        parsoff = self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, is_last, False, self)

        self._offset(*parsoff, True, True, self_=False)

    elif is_last_and_at_self_end:  # because of insertion at end and maybe unenclosed sequence
        parsoff = self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, True, self)
    else:  # in this case there may parts of self after so we need to recurse the offset into self
        parsoff = self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, False)

    # parameters for put / del trailing and internal separators, we return explicitly so that the ASTs can be modified so the next part doesn't get too screwy

    return (start, len_fst, body, body2, sep, self_tail_sep, bound_end_ln, bound_end_col, bound_end_col_offset, parsoff,
            is_last, is_del, is_ins)


def _put_slice_seq_end(self: fst.FST, params: tuple) -> None:
    """Finish up sequence slice put with separators. `AST` nodes are assumed to have been modified by here and general
    structure of `self` is correct, even if it is not parsable due to separators in source not being correct yet."""

    (start, len_fst, body, body2, sep, self_tail_sep, bound_end_ln, bound_end_col, bound_end_col_offset, parsoff,
     is_last, is_del, is_ins) = params

    if self_tail_sep is not None:  # trailing
        last = body2[-1].f

        _, _, last_end_ln, last_end_col = last.loc
        bound_end_ln, bound_end_col = _offset_pos_by_params(self, bound_end_ln, bound_end_col,
                                                            bound_end_col_offset, parsoff)

        if self_tail_sep:
            self._maybe_ins_separator(last_end_ln, last_end_col, False, bound_end_ln, bound_end_col, sep, last)
        else:
            self._maybe_del_separator(last_end_ln, last_end_col, self_tail_sep is False, bound_end_ln, bound_end_col,
                                      sep)

    if not is_del:  # internal
        new_stop = start + len_fst

        if not is_last:  # past the newly put slice
            put_last = body2[new_stop - 1].f

            _, _, put_last_end_ln, put_last_end_col = put_last.loc
            new_stop_ln, new_stop_col, _, _ = self._loc_maybe_dict_key(new_stop, True, body, body2).loc

            self._maybe_ins_separator(put_last_end_ln, put_last_end_col, True, new_stop_ln, new_stop_col, sep, put_last)

        if is_ins and start:  # between self split (last element of first part) or end and new slice following it
            self_split = body2[start - 1].f

            _, _, self_split_end_ln, self_split_end_col = self_split.loc
            put_first_ln, put_first_col, _, _ = self._loc_maybe_dict_key(start, True, body, body2).loc

            self._maybe_ins_separator(self_split_end_ln, self_split_end_col, True, put_first_ln, put_first_col, sep,
                                      self_split)

            return self


def _get_element_indent(self: fst.FST, body: list[AST], body2: list[AST], start: int) -> str | None:
    """Get first exprish element indentation found for an element which starts its own line. The FULL indentation, not
    the element indentation with respect to container indentation. We just return the indentation of one element instead
    of trying to figure out which indent is used most for both performance and were-just-not-gonna-deal-with-that-crap
    reasons.

    **Parameters:**
    - `start`: The index of the element to start the search with (closest to area we want to indent).

    **Returns:**
    - `str`: Indent found.
    - `None`: No explicit indent found.
    """

    lines = self.root._lines

    if body is body2:  # single element sequence
        if start >= 1:  # first search backward for an element which starts its own line (if there are elements before)
            loc = start_prev_loc = body[start - 1].f.pars()

            for i in range(start - 2, -1, -1):
                if loc.ln != (prev_loc := body[i].f.pars()).end_ln:  # only consider elements which start on a different line than the previous element ends on
                    if re_empty_line.match(l := lines[loc.ln], 0, loc.col):  # need to check regardless of different line because there may be stray separator
                        return l[:loc.col]

                loc = prev_loc

            if loc.ln != self.ln:  # only consider element 0 if it is not on same line as self starts
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

            loc = start_prev_loc

        else:
            # loc = fstloc(-1, -1, -1, -1)  # dummy, will force pattern check for element 0 because there could be anything before it
            ln, col, _, _ = self.loc
            loc = fstloc(-1, -1, ln, col)  # so we don't get indent of special first element if on same line as self starts (probably unindented intentionally)

        for i in range(start, len(body)):  # now search forward
            prev_loc = loc

            if (loc := body[i].f.pars()).ln != prev_loc.end_ln:  # only consider elements which start on a different line than the previous element ends on
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

    else:  # two-element sequence (Dict, MatchMapping)
        if start >= 1:  # first search backward for an element which starts its own line (if there are elements before)
            for i in range(start - 2, -1, -1):
                if (loc := self._loc_maybe_dict_key(i + 1, True, body)).ln != body2[i].f.pars().end_ln:  # only consider elements which start on a different line than the previous element ends on
                    if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                        return l[:loc.col]

            if (loc := self._loc_maybe_dict_key(0, True, body)).ln != self.ln:  # only consider element 0 if it is not on same line as self starts
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

        else:
            # loc = fstloc(-1, -1, -1, -1)  # dummy, will force pattern check for element 0 because there could be anything before it
            ln, col, _, _ = self.loc
            loc = fstloc(-1, -1, ln, col)  # so we don't get indent of special first element if on same line as self starts (probably unindented intentionally)

        for i in range(start, len(body)):  # now search forward
            prev_loc = loc

            if (loc := self._loc_maybe_dict_key(i, True, body)).ln != prev_loc.end_ln:  # only consider elements which start on a different line than the previous element ends on
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

            prev_loc = body2[i].f.pars()

    return None


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


def _validate_put_seq(self: fst.FST, fst_: fst.FST, non_slice: str, *,
                      check_target: Literal[False] | Callable = False) -> None:  # check_target like is_valid_target()
    if not fst_:
        return

    ast = self.a
    ast_ = fst_.a

    if non_slice and isinstance(ast_, Tuple) and any(isinstance(e, Slice) for e in ast_.elts):
        raise NodeError(f'cannot put Slice into {non_slice}')

    if check_target and not isinstance(ctx := getattr(ast, 'ctx', None), Load) and not check_target(ast_.elts):
        raise NodeError(f'invalid slice for {ast.__class__.__name__}'
                        f'{f" {ctx.__class__.__name__}" if ctx else ""} target')


# ......................................................................................................................

def _code_to_slice_seq(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any], *,
                       code_as: Callable = code_as_expr, non_seq_str_as_one: bool = False) -> fst.FST | None:
    if code is None:
        return None

    fst_ = code_as(code, self.root.parse_params, sanitize=False)
    ast_ = fst_.a

    if not one and non_seq_str_as_one and not isinstance(ast_, (Tuple, List, Set)) and isinstance(code, (str, list)):  # this exists as a convenience for allowing doing `Delete.targets = 'target'` (without trailing comma if string source)
        one = True

    if one:
        if (is_par := fst_.is_parenthesized_tuple()) is not None:
            fst_._maybe_add_singleton_tuple_comma(is_par)  # specifically for lone '*starred' without comma from slices, even though those can't be gotten alone organically

            if is_par is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
                fst_._delimit_node()

        elif isinstance(ast_, Set):
            if (empty := self.get_option('fix_set_self', options)):  # putting an invalid empty Set as one, make it valid according to options
                fst_._maybe_fix_set(empty)

        elif isinstance(ast_, NamedExpr):  # this needs to be parenthesized if being put to unparenthesized tuple
            if not fst_.pars().n and self.is_parenthesized_tuple() is False:
                fst_._parenthesize_grouping()

        elif isinstance(ast_, (Yield, YieldFrom)):  # these need to be parenthesized definitely
            if not fst_.pars().n:
                fst_._parenthesize_grouping()

        ast_ = Tuple(elts=[fst_.a], ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),  # fst_.a because may have changed in Set processing
                     end_col_offset=ls[-1].lenbytes)  # Tuple because it is valid target if checked in validate and allows is_enclosed_or_line() check without delimiters to check content

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    if fix_set_put := self.get_option('fix_set_put', options):
        if (fst_.is_empty_set_star() if fix_set_put == 'star' else
            fst_.is_empty_set_call() if fix_set_put == 'call' else
            fst_.is_empty_set_star() or fst_.is_empty_set_call()  # True or 'both'
        ):
            return None

    if not isinstance(ast_, (Tuple, List, Set)):
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} "
                        f"must be a Tuple, List or Set, not a {ast_.__class__.__name__}", rawable=True)

    if not ast_.elts:  # put empty sequence is same as delete
        return None

    if fst_.is_parenthesized_tuple() is not False:  # anything that is not an unparenthesize tuple is restricted to the inside of the delimiters, which are removed
        _trim_delimiters(fst_)
    else:  # if unparenthesized tuple then use whole source, including leading and trailing trivia not included
        _set_loc_whole(fst_)

    return fst_


def _code_to_slice_seq2(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any], code_as: Callable,
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


def _code_to_slice_Assign_targets(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any],
                                  ) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_expr(code, self.root.parse_params, sanitize=False)
        ast_ = fst_.a

        if not is_valid_target(ast_):
            raise NodeError(f'expecting one Assign target, got {fst_.a.__class__.__name__}')

        set_ctx(ast_, Store)

        ast_ = _slice_Assign_targets(targets=[ast_], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                                     end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    else:
        fst_ = code_as_Assign_targets(code, self.root.parse_params, sanitize=False)

        if not fst_.a.targets:  # put empty sequence is same as delete
            return None

    return fst_


def _code_to_slice_aliases(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any],
                           code_as_one: Callable = code_as_alias, code_as_slice: Callable = code_as_aliases,
                           ) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_one(code, self.root.parse_params, sanitize=False)
        ast_ = _slice_aliases(names=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                              end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    fst_ = code_as_slice(code, self.root.parse_params, sanitize=False)

    if not fst_.a.names:  # put empty sequence is same as delete
        return None

    return fst_


def _code_to_slice_withitems(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any],
                             ) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_withitem(code, self.root.parse_params, sanitize=False)
        ast_ = _slice_withitems(names=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                                end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    fst_ = code_as_withitems(code, self.root.parse_params, sanitize=False)

    if not fst_.a.items:  # put empty sequence is same as delete
        return None

    return fst_


def _code_to_slice_expr_arglikes(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_expr_arglike(code, self.root.parse_params, sanitize=False)

        if fst_.is_parenthesized_tuple() is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
            fst_._delimit_node()

        ast_ = Tuple(elts=[fst_.a], ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                     end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    fst_ = code_as_Tuple(code, self.root.parse_params, sanitize=False)

    if not fst_.a.elts:  # put empty sequence is same as delete
        return None

    if fst_.is_parenthesized_tuple() is not False:  # parenthesize tuple is restricted to the inside of the delimiters, which are removed
        _trim_delimiters(fst_)
    else:  # if unparenthesized tuple then use whole source, including leading and trailing trivia not included
        _set_loc_whole(fst_)

    return fst_


def _code_to_slice_MatchSequence(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any],
                                 ) -> fst.FST | None:
    if code is None:
        return None

    fst_ = code_as_pattern(code, self.root.parse_params, sanitize=False)

    if one:
        if fst_.is_delimited_matchseq() == '':
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

    if fst_.is_delimited_matchseq():  # delimited is restricted to the inside of the delimiters, which are removed
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
        if not one and not self.get_option('fix_matchor_put', options):
            raise NodeError(f"slice being assigned to a MatchOr "
                            f"must be a MatchOr with fix_matchor_put=False, not a {ast_.__class__.__name__}",
                            rawable=True)

        if isinstance(ast_, MatchAs):
            if ast_.pattern is not None and not fst_.pars().n:
                fst_._parenthesize_grouping()

        elif isinstance(ast_, MatchSequence):
            if not fst_.is_delimited_matchseq():
                fst_._delimit_node(delims='[]')

    ast_ = MatchOr(patterns=[ast_], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                   end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, from_=fst_, lcopy=False)


def _code_to_slice_type_params(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = code_as_type_param(code, self.root.parse_params, sanitize=False)
        ast_ = _slice_type_params(type_params=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                                  end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, from_=fst_, lcopy=False)

    fst_ = code_as_type_params(code, self.root.parse_params, sanitize=False)

    if not fst_.a.type_params:  # put empty sequence is same as delete
        return None

    return fst_


# ......................................................................................................................

def _put_slice_NOT_IMPLEMENTED_YET(self: fst.FST, code: Code | None, start: int | Literal['end'] | None,
                                   stop: int | None, field: str, one: bool, options: Mapping[str, Any],
                                   ) -> None:
    raise NotImplementedError("not implemented yet, try with option raw='auto'")


def _put_slice_Dict(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                    field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_seq2(self, code, one, options, code_as_expr)
    body = (ast := self.a).keys
    body2 = ast.values
    start, stop = fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'keys', 'values')

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])

        del body[start : stop]
        del body2[start : stop]

        len_fst_body = 0

    else:
        ast_ = fst_.a
        fst_body = ast_.keys
        fst_body2 = ast_.values
        len_fst_body = len(fst_body)
        fst_first = a.f if (a := fst_body[0]) else fst_._loc_maybe_dict_key(0)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_first, fst_body2[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'keys', 'values')

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body
        body2[start : stop] = fst_body2

        stack = []

        for i in range(len_fst_body):
            startplusi = start + i

            stack.append(fst.FST(body2[startplusi], self, astfield('values', startplusi)))

            if key := body[startplusi]:
                stack.append(fst.FST(key, self, astfield('keys', startplusi)))

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body2[i].f.pfield = astfield('values', i)

        if key := body[i]:  # could be None from **
            key.f.pfield = astfield('keys', i)

    _put_slice_seq_end(self, end_params)


def _put_slice_Tuple_elts(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                          field: str, one: bool, options: Mapping[str, Any]) -> None:
    """Tuple is used in many different ways in python, also for expressionish slices by us."""

    fst_ = _code_to_slice_seq(self, code, one, options, code_as=code_as_expr_all)
    body = (ast := self.a).elts
    start, stop = fixup_slice_indices(len(body), start, stop)

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

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), self_tail_sep=1)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), self_tail_sep=1)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('elts', i)) for i in range(start, start + len_fst_body)]

        if stack:
            set_ctx([f.a for f in stack], ast.ctx.__class__)

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('elts', i)

    _put_slice_seq_end(self, end_params)

    is_par = self._maybe_fix_tuple(is_par)

    if need_par and not is_par:
        self._delimit_node()


def _put_slice_List_elts(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                         field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_seq(self, code, one, options)
    body = (ast := self.a).elts
    start, stop = fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'List', check_target=is_valid_target)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'))

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.elts)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'))

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('elts', i)) for i in range(start, start + len_fst_body)]

        if stack:
            set_ctx([f.a for f in stack], ast.ctx.__class__)

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('elts', i)

    _put_slice_seq_end(self, end_params)


def _put_slice_Set_elts(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                        field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_seq(self, code, one, options)
    body = self.a.elts
    start, stop = fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'Set')

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'))

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.elts)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'))

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('elts', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('elts', i)

    _put_slice_seq_end(self, end_params)

    self._maybe_fix_set(self.get_option('fix_set_self', options))


def _put_slice_Delete_targets(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                              field: str, one: bool, options: Mapping[str, Any]) -> None:
    """Even though when getting a slice it will be returned as a `Tuple`, any sequence of valid target types is accepted
    for the put operation. If putting a non-sequence element, it will be automatically put as `one=True` to match the
    non-comma terminated syntax of `Delete` targets (a non-sequence `FST` or `AST` will not be accepted like this). This
    allows correct-appearing syntax like `delfst.targets = 'target'` to work."""

    fst_ = _code_to_slice_seq(self, code, one, options, non_seq_str_as_one=True)
    len_body = len(body := (ast := self.a).targets)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and self.get_option('fix_delete_self', options):
            raise ValueError("cannot delete all Delete.targets without fix_delete_self=False")

    _validate_put_seq(self, fst_, 'Delete', check_target=is_valid_del_target)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bound_Delete_targets(self)

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'targets', None, ',', False)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.elts)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'targets', None, ',', False)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('targets', i)) for i in range(start, start + len_fst_body)]

        if stack:
            set_ctx([f.a for f in stack], Del)

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('targets', i)

    _put_slice_seq_end(self, end_params)

    if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
        if body:
            _, _, bound_ln, bound_col = body[-1].f.pars()

        _maybe_set_end_pos(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                           ast.end_lineno, ast.end_col_offset)

    ln, col, _, _ = self.loc

    self._maybe_fix_joined_alnum(ln, col + 3)
    self._maybe_add_line_continuations()


def _put_slice_Assign_targets(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                              field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_Assign_targets(self, code, one, options)
    len_body = len(body := self.a.targets)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and self.get_option('fix_assign_self', options):
            raise ValueError("cannot cut all Assign.targets without fix_assign_self=False")

    # elif (a0 := (fst_body := fst_.a.targets)[0]).col_offset:  # if first element of slice doesn't start at column 0 then dedent it
    #     fst_._put_src(None, ln := (f := a0.f).ln, 0, ln, f.col, False)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bound_Assign_targets(self, start)

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'targets', None, '=', True)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.targets)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'targets', None, '=', True)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('targets', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('targets', i)

    _put_slice_seq_end(self, end_params)

    _maybe_fix_Assign_target0(self)
    self._maybe_add_line_continuations()


def _put_slice_With_AsyncWith_items(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                    field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_withitems(self, code, one, options)
    len_body = len(body := (ast := self.a).items)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and self.get_option('fix_with_self', options):
            raise ValueError(f'cannot delete all {ast.__class__.__name__}.items without fix_with_self=False')

    pars = self._loc_With_items_pars()  # may be pars or may be where pars would go from just after `with` to end of block header `:`
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          pars_ln, pars_col + pars_n, pars_end_ln, pars_end_col - pars_n,
                                          options.get('trivia'), options.get('ins_ln'), 'items', None, ',', False)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.items)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          pars_ln, pars_col + pars_n, pars_end_ln, pars_end_col - pars_n,
                                          options.get('trivia'), options.get('ins_ln'), 'items', None, ',', False)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('items', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('items', i)

    _put_slice_seq_end(self, end_params)

    if not pars_n:  # only need to fix maybe if there are no parentheses
        if not self.is_enclosed_or_line(pars=False):  # if no parentheses and wound up not valid for parse then adding parentheses around items should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_With_items_pars()

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, False)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        if not start:  # if not adding pars then need to make sure del or put didn't join new first `withitem` with the `with`
            ln, col, _, _ = pars.bound

            self._maybe_fix_joined_alnum(ln, col)


def _put_slice_Import_names(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                            field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_aliases(self, code, one, options, code_as_Import_name, code_as_Import_names)
    len_body = len(body := (ast := self.a).names)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and self.get_option('fix_import_self', options):
            raise ValueError('cannot delete all Import.names without fix_import_self=False')

    _, _, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    elif body:
        bound_ln, bound_col, _, _ = body[0].f.pars()
    else:
        bound_ln = bound_end_ln
        bound_col = bound_end_col

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'names', None, ',', False)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.names)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'names', None, ',', False)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('names', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('names', i)

    _put_slice_seq_end(self, end_params)

    if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
        if body:
            _maybe_set_end_pos(self, (bn := body[-1]).end_lineno, bn.end_col_offset, ast.end_lineno, ast.end_col_offset)
        else:
            _maybe_set_end_pos(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                               ast.end_lineno, ast.end_col_offset)

    self._maybe_add_line_continuations()  # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this


def _put_slice_ImportFrom_names(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_aliases(self, code, one, options, code_as_ImportFrom_name, code_as_ImportFrom_names)
    len_body = len(body := (ast := self.a).names)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    put_star = False

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and self.get_option('fix_import_self', options):
            raise ValueError('cannot delete all ImportFrom.names without fix_import_self=False')

    else:
        if put_star := fst_.a.names[0].name == '*':  # if putting star then it must overwrite everything
            if len_slice != len_body:
                raise NodeError("if putting star '*' alias it must overwrite all other aliases")

        elif body and body[0].name == '*':  # putting to star then it must be overwritten
            if start > 0 or stop < 1:
                raise NodeError("if putting over star '*' alias it must be overwritten")

    pars = self._loc_ImportFrom_names_pars()  # may be pars or may be where pars would go from just after `import` to end of node
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          pars_ln, pars_col + pars_n, pars_end_ln, pars_end_col - pars_n,
                                          options.get('trivia'), options.get('ins_ln'), 'names', None, ',', False)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.names)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          pars_ln, pars_col + pars_n, pars_end_ln, pars_end_col - pars_n,
                                          options.get('trivia'), options.get('ins_ln'), 'names', None, ',', False)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('names', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('names', i)

    _put_slice_seq_end(self, end_params)

    if not pars_n:  # only need to fix maybe if there are no parentheses
        if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
            if body:
                _maybe_set_end_pos(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                   ast.end_lineno, ast.end_col_offset)
            else:
                _maybe_set_end_pos(self, pars_ln + 1, self.root._lines[pars_ln].c2b(pars_col),
                                   ast.end_lineno, ast.end_col_offset)

        if not self.is_enclosed_or_line(pars=False):  # if no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ImportFrom_names_pars()

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, True, False, self)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this

    elif put_star:  # if put star then must remove parentheses (including any trivia inside them)
        pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ImportFrom_names_pars()
        star_ln, star_col, star_end_ln, star_end_col = body[0].f.loc

        self._put_src(None, star_end_ln, star_end_col, pars_end_ln, pars_end_col, True)
        self._put_src(None, pars_ln, pars_col, star_ln, star_col, False)


def _put_slice_Global_Nonlocal_names(self: fst.FST, code: Code | None, start: int | Literal['end'] | None,
                                     stop: int | None, field: str, one: bool, options: Mapping[str, Any]) -> None:
    """In order to do this put since `Global` and `Nonlocal` do not have child `AST` nodes but just identifiers, we
    create a temporary container which does have `Name` elements for each name and operate on that. Afterwards we get
    rid of that but the modified source identifiers remain."""

    fst_ = _code_to_slice_seq(self, code, one, options, non_seq_str_as_one=True)
    len_body = len(body := (ast := self.a).names)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and self.get_option('fix_global_self', options):
            raise ValueError(f'cannot delete all {ast.__class__.__name__}.names without fix_global_self=False')

    else:
        n = 0

        if not all(isinstance(bad := e, Name) and not (n := e.f.pars().n) for e in fst_.a.elts):
            raise NodeError(f'cannot put{" parenthesized" if n else ""} {bad.__class__.__name__} '
                            f'to {ast.__class__.__name__}.names')

        # TODO? could have some logic here to strip trailing newline from fst_ if putting at end and there is no trivia on same line as last element to not introduce a spurisous newline? seems a bit over-the-top, XXX be careful of semicolons separating statements!

    ln, end_col, bound_end_ln, bound_end_col = self.loc

    lines = self.root._lines
    tmp_elts = []
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
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'elts', None, ',', False)

        del body[start : stop]  # this is the real update

        self._unmake_fst_tree(tmp_elts[start : stop])

        del tmp_elts[start : stop]  # this is the fake temporary update

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.elts)
        fst_last = fst_body[-1].f

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_last, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'elts', None, ',', False)

        body[start : stop] = [e.id for e in fst_body]  # this is the real update

        self._unmake_fst_tree(tmp_elts[start : stop])  # lets just pretend like its has real AST children, needed for _put_slice_seq_end()
        fst_._unmake_fst_parents(True)

        tmp_elts[start : stop] = fst_body  # this is the fake temporary update

        FST = fst.FST
        stack = [FST(tmp_elts[i], self, astfield('elts', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(tmp_elts)):
        tmp_elts[i].f.pfield = astfield('elts', i)

    _put_slice_seq_end(self, end_params)

    if fst_:  # we get it here because ._set_ast() below makes this impossible
        fst_last_loc = tmp_elts[-1].f.loc

    ast.end_lineno = tmp_ast.end_lineno  # copy new end from temporary FST to self (since it was swapped out)
    ast.end_col_offset = tmp_ast.end_col_offset

    self._set_ast(ast, True)

    if stop == len_body:  # if del OR put till and something left then may need to reset end position of self due to new trailing trivia, put because could come from trailing trivia of last element of parenthesized tuple
        if fst_:
            _, _, last_end_ln, last_end_col = fst_last_loc

        _maybe_set_end_pos(self, last_end_ln + 1, lines[last_end_ln].c2b(last_end_col),
                           ast.end_lineno, ast.end_col_offset)

    self._maybe_add_line_continuations()  # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this


def _put_slice_ClassDef_bases(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                              field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_expr_arglikes(self, code, one, options)
    len_body = len(body := (ast := self.a).bases)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_ and not len_slice:
        return

    _validate_put_seq(self, fst_, 'ClassDef.bases')

    if keywords := ast.keywords:
        if body and keywords[0].f.loc[:2] < body[stop - 1].f.loc[2:] and stop:
            raise NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')

    bound_ln, bound_col, bound_end_ln, bound_end_col = bases_pars = self._loc_ClassDef_bases_pars()

    if not fst_:
        if not keywords and len_slice == len_body:  # deleting everything so remove pars
            self._put_src(None, bound_ln, bound_col, bound_end_ln, bound_end_col, False)

            end_params = None

        else:
            bound_col += 1
            bound_end_col -= 1
            self_tail_sep = (start and keywords and stop == len_body) or None

            end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                              bound_ln, bound_col, bound_end_ln, bound_end_col,
                                              options.get('trivia'), options.get('ins_ln'), 'bases', None, ',',
                                              self_tail_sep)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

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

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'bases', None, ',',
                                          self_tail_sep)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('bases', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('bases', i)

    if end_params:
        _put_slice_seq_end(self, end_params)

        if self_tail_sep:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
            self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there


def _put_slice_Call_args(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                         field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_expr_arglikes(self, code, one, options)
    len_body = len(body := (ast := self.a).args)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'Call.args')

    if keywords := ast.keywords:
        if body and keywords[0].f.loc[:2] < body[stop - 1].f.loc[2:] and stop:
            raise NodeError('cannot get this Call.args slice because it includes parts after a keyword')

    else:
        if body and (f0 := body[0].f).is_solo_call_arg_genexp() and f0.pars(shared=False).n == -1:  # single call argument GeneratorExp shares parentheses with Call?
            f0._parenthesize_grouping()

    bound_ln, bound_col, bound_end_ln, bound_end_col = self._loc_call_pars()
    bound_col += 1
    bound_end_col -= 1

    if not fst_:
        self_tail_sep = (start and keywords and stop == len_body) or None

        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'args', None, ',',
                                          self_tail_sep)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        self_tail_sep = (keywords and stop == len_body) or None
        len_fst_body = len(fst_body := fst_.a.elts)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'args', None, ',',
                                          self_tail_sep)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('args', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('args', i)

    _put_slice_seq_end(self, end_params)

    if self_tail_sep:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
        self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there


def _put_slice_MatchSequence_patterns(self: fst.FST, code: Code | None, start: int | Literal['end'] | None,
                                      stop: int | None, field: str, one: bool, options: Mapping[str, Any]) -> None:
    # NOTE: we allow multiple MatchStars to be put to the same MatchSequence
    fst_ = _code_to_slice_MatchSequence(self, code, one, options)
    body = self.a.patterns
    start, stop = fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if delims := self.is_delimited_matchseq():
        bound_col += 1
        bound_end_col -= 1

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'patterns', None, ',', 0)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.patterns)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'patterns', None, ',', 0)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('patterns', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('patterns', i)

    _put_slice_seq_end(self, end_params)

    self._maybe_fix_matchseq(delims)


def _put_slice_MatchMapping(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                            field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_seq2(self, code, one, options, code_as_pattern)
    len_body = len(body := (ast := self.a).keys)
    body2 = ast.patterns
    start, stop = fixup_slice_indices(len_body, start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    if not fst_:
        self_tail_sep = (start and ast.rest and stop == len_body) or None

        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'keys', 'patterns', ',',
                                          self_tail_sep)

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])

        del body[start : stop]
        del body2[start : stop]

        len_fst_body = 0

    else:
        ast_ = fst_.a
        fst_body = ast_.keys
        fst_body2 = ast_.patterns
        len_fst_body = len(fst_body)
        self_tail_sep = (ast.rest and stop == len_body) or None

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body2[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'keys', 'patterns', ',',
                                          self_tail_sep)

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body
        body2[start : stop] = fst_body2

        stack = []

        for i in range(len_fst_body):
            startplusi = start + i

            stack.append(fst.FST(body[startplusi], self, astfield('keys', startplusi)))
            stack.append(fst.FST(body2[startplusi], self, astfield('patterns', startplusi)))

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('keys', i)
        body2[i].f.pfield = astfield('patterns', i)

    _put_slice_seq_end(self, end_params)

    if self_tail_sep:  # if there is a **rest and we removed tail element so here we make sure there is a space between comma of the new last element and the **rest
        self._maybe_ins_separator(*body2[-1].f.loc[2:], True)  # this will only maybe add a space, comma is already there


def _put_slice_MatchOr_patterns(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                field: str, one: bool, options: Mapping[str, Any]) -> None:
    fst_ = _code_to_slice_MatchOr(self, code, one, options)
    len_body = len(body := self.a.patterns)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    fix_matchor_self = self.get_option('fix_matchor_self', options)

    if not fst_:
        if not len_slice:
            return

        if not (len_left := len_body - len_slice):
            if fix_matchor_self:
                raise ValueError("cannot delete all MatchOr.patterns without fix_matchor_self=False")

        elif len_left == 1 and fix_matchor_self == 'strict':
            raise ValueError("cannot del MatchOr to length 1 with fix_matchor_self='strict'")

        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0, *self.loc,
                                          options.get('trivia'), options.get('ins_ln'), 'patterns', None, '|', False)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.patterns)

        if (len_body - len_slice + len_fst_body) == 1 and fix_matchor_self == 'strict':
            raise NodeError("cannot put MatchOr to length 1 with fix_matchor_self='strict'")

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body, *self.loc,
                                          options.get('trivia'), options.get('ins_ln'), 'patterns', None, '|', False)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('patterns', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('patterns', i)

    _put_slice_seq_end(self, end_params)

    self._maybe_fix_matchor(fix_matchor_self)


def _put_slice_type_params(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                           field: str, one: bool, options: Mapping[str, Any]) -> None:
    """An empty `Tuple` is accepted as a zero-element `type_params` slice."""

    fst_ = _code_to_slice_type_params(self, code, one, options)
    len_body = len(body := (ast := self.a).type_params)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    bound, (name_ln, name_col) = (
        (self._loc_typealias_type_params_brackets if isinstance(ast, TypeAlias) else
         self._loc_classdef_type_params_brackets if isinstance(ast, ClassDef) else
         self._loc_funcdef_type_params_brackets)  # FunctionDef, AsyncFunctionDef
    )()

    if bound:
        bound_ln, bound_col, bound_end_ln, bound_end_col = bound

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body:  # deleting everything so remove brackets
            self._put_src(None, name_ln, name_col, bound_end_ln, bound_end_col, False)

            end_params = None

        else:
            end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                              bound_ln, bound_col + 1, bound_end_ln, bound_end_col - 1,
                                              options.get('trivia'), options.get('ins_ln'), 'type_params')

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        if not body:  # brackets don't exist, add them first
            self._put_src('[]', name_ln, name_col, name_ln, name_col, False)

            bound_ln = bound_end_ln = name_ln
            bound_col = bound_end_col = name_col + 1

        len_fst_body = len(fst_body := fst_.a.type_params)

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), 'type_params')

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield('type_params', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('type_params', i)

    if end_params:
        _put_slice_seq_end(self, end_params)


def _put_slice__slice(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                      field: str, one: bool, options: Mapping[str, Any]) -> None:
    static = _SLICE_STATICS[(ast := self.a).__class__]
    fst_ = static.code_to(self, code, one, options)
    len_body = len(body := getattr(ast, field))
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not fst_ and not len_slice:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if not fst_:
        end_params = _put_slice_seq_begin(self, start, stop, None, None, None, 0,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), field, None,
                                          static.sep, static.self_tail_sep)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := getattr(fst_.a, field))

        end_params = _put_slice_seq_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                          bound_ln, bound_col, bound_end_ln, bound_end_col,
                                          options.get('trivia'), options.get('ins_ln'), field, None,
                                          static.sep, static.self_tail_sep)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield(field, i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield(field, i)

    _put_slice_seq_end(self, end_params)

# ......................................................................................................................

def _put_slice(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
               one: bool, options: Mapping[str, Any]) -> Union[Self, fst.FST, None]:  # -> Self or reparsed Self or could disappear due to raw
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

    (_slice_Assign_targets, 'targets'):       _put_slice__slice,
    # (_slice_Assign_comprehension_ifs, 'ifs'): _put_slice__slice,
    (_slice_aliases, 'names'):                _put_slice__slice,
    (_slice_withitems, 'items'):              _put_slice__slice,
    (_slice_type_params, 'type_params'):      _put_slice__slice,
}


# ----------------------------------------------------------------------------------------------------------------------
# put raw

def _loc_slice_raw_put(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str) -> fstloc:
    """Get location of a raw slice. Sepcial cases for decorators, comprehension ifs and other weird nodes."""

    def fixup_slice_index_for_raw(len_: int, start: int, stop: int) -> tuple[int, int]:
        start, stop = fixup_slice_indices(len_, start, stop)

        if start == stop:
            raise ValueError("invalid slice for raw operation")

        return start, stop

    ast = self.a

    if isinstance(ast, Dict):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

        start, stop = fixup_slice_index_for_raw(len(values := ast.values), start, stop)
        start_loc = self._loc_maybe_dict_key(start, True)

        return fstloc(start_loc.ln, start_loc.col, *values[stop - 1].f.pars()[2:])

    if isinstance(ast, Compare):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Compare")

        comparators = ast.comparators  # virtual combined body of [Compare.left] + Compare.comparators
        start, stop = fixup_slice_index_for_raw(len(comparators) + 1, start, stop)
        stop -= 1

        return fstloc(*(comparators[start - 1] if start else ast.left).f.pars()[:2],
                      *(comparators[stop - 1] if stop else ast.left).f.pars()[2:])

    if isinstance(ast, MatchMapping):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a MatchMapping")

        keys = ast.keys
        start, stop = fixup_slice_index_for_raw(len(keys), start, stop)

        return fstloc(*keys[start].f.loc[:2], *ast.patterns[stop - 1].f.pars()[2:])

    if isinstance(ast, comprehension):
        ifs = ast.ifs
        start, stop = fixup_slice_index_for_raw(len(ifs), start, stop)
        ffirst = ifs[start].f
        start_pos = prev_find(self.root._lines, *ffirst._prev_bound(), ffirst.ln, ffirst.col, 'if')

        return fstloc(*start_pos, *ifs[stop - 1].f.pars()[2:])

    if isinstance(ast, (Global, Nonlocal)):
        start, stop = fixup_slice_index_for_raw(len(ast.names), start, stop)
        start_loc, stop_loc = self._loc_global_nonlocal_names(start, stop - 1)

        return fstloc(start_loc.ln, start_loc.col, stop_loc.end_ln, stop_loc.end_col)

    if field == 'decorator_list':
        decos = ast.decorator_list
        start, stop = fixup_slice_index_for_raw(len(decos), start, stop)
        ffirst = decos[start].f
        start_pos = prev_find(self.root._lines, 0, 0, ffirst.ln, ffirst.col, '@')  # we can use '0, 0' because we know "@" starts on a newline

        return fstloc(*start_pos, *decos[stop - 1].f.pars()[2:])

    body = getattr(ast, field)  # field must be valid by here
    start, stop = fixup_slice_index_for_raw(len(body), start, stop)

    return fstloc(*body[start].f.pars(shared=False)[:2], *body[stop - 1].f.pars(shared=False)[2:])


def _put_slice_raw(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
                   one: bool, options: Mapping[str, Any]) -> Union[Self, fst.FST, None]:  # -> Self or reparsed Self
    """Put a raw slice of child nodes to `self`."""

    if code is None:
        raise NotImplementedError('raw slice delete not implemented yet')

    if isinstance(code, AST):
        if not one:
            ast = reduce_ast(code, True)

            if isinstance(ast, Tuple):  # strip delimiters because we want CONTENTS of slice for raw put, not the slice object itself
                code = unparse(ast)[1 : (-2 if len(ast.elts) == 1 else -1)]  # also remove singleton Tuple trailing comma
            elif isinstance(ast, (List, Dict, Set, MatchSequence, MatchMapping)):
                code = unparse(ast)[1 : -1]

    elif isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        ast = reduce_ast(code.a, True)
        fst_ = ast.f

        if one:
            if (is_par_tup := fst_.is_parenthesized_tuple()) is None:  # only need to parenthesize this, others are already enclosed
                if isinstance(ast, MatchSequence) and not fst_._is_delimited_seq('patterns'):
                    fst_._parenthesize_grouping()

            elif is_par_tup is False:
                fst_._delimit_node()

        elif ((is_dict := isinstance(ast, Dict)) or
              (is_match := isinstance(ast, (MatchSequence, MatchMapping))) or
              isinstance(ast, (Tuple, List, Set))
        ):
            if not ((is_par_tup := fst_.is_parenthesized_tuple()) is False or  # don't strip nonexistent delimiters if is unparenthesized Tuple or MatchSequence
                    (is_par_tup is None and isinstance(ast, MatchSequence) and
                     not fst_._is_delimited_seq('patterns'))
            ):
                code._put_src(None, end_ln := code.end_ln, (end_col := code.end_col) - 1, end_ln, end_col, True)  # strip enclosing delimiters
                code._put_src(None, ln := code.ln, col := code.col, ln, col + 1, False)

            if elts := ast.values if is_dict else ast.patterns if is_match else ast.elts:
                if comma := next_find(code.root._lines, (l := elts[-1].f.loc).end_ln, l.end_col, code.end_ln,
                                      code.end_col, ','):  # strip trailing comma
                    ln, col = comma

                    code._put_src(None, ln, col, ln, col + 1, False)

    self._reparse_raw(code, *_loc_slice_raw_put(self, start, stop, field))

    return self.repath()


# ----------------------------------------------------------------------------------------------------------------------

class slicestatic(NamedTuple):
    field:         str
    code_to:       Callable[[fst.FST, Code, bool, dict], fst.FST]
    sep:           str
    self_tail_sep: bool | Literal[0, 1] | None
    ret_tail_sep:  bool | Literal[0, 1] | None


_SLICE_STATICS = {
    _slice_Assign_targets: slicestatic('targets', _code_to_slice_Assign_targets, '=', True, True),
    _slice_aliases:        slicestatic('names', _code_to_slice_aliases, ',', False, False),
    _slice_withitems:      slicestatic('items', _code_to_slice_withitems, ',', False, False),
    _slice_type_params:    slicestatic('type_params', _code_to_slice_type_params, ',', False, False),
}


# ----------------------------------------------------------------------------------------------------------------------

@staticmethod
def _is_slice_compatible(sig1: tuple[type[AST], str], sig2: tuple[type[AST], str]) -> bool:  # sig = (AST type, field)
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
