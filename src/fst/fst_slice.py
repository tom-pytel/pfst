"""Get and put slice.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

import re
from ast import *
from typing import Any, Callable, Literal, Union

from . import fst

from .astutil import *
from .astutil import re_identifier, TypeAlias, TryStar, TemplateStr, is_valid_target

from .misc import (
    PYLT11, PYGE14,
    Self, Code, NodeError, astfield, fstloc,
    re_empty_line_start, re_empty_line, re_line_trailing_space, re_empty_space, re_line_end_cont_or_comment,
    _next_src, _prev_find, _next_find, _next_find_re, _fixup_slice_indices,
    _leading_trivia, _trailing_trivia,
)

from .fst_parse import _code_as_expr, _code_as_pattern
from .fst_slice_old import _get_slice_stmtish, _put_slice_stmtish

_re_one_space            = re.compile(r'\s')
_re_close_delim_or_end   = re.compile(r'[)}\]]|$')
_re_sep_line_nonexpr_end = {  # empty line with optional separator and line continuation or a pure comment line
    ',': re.compile(r'\s*(?:,\s*)?(?:\\|#.*)?$'),
    '|': re.compile(r'\s*(?:\|\s*)?(?:\\|#.*)?$'),
}


# * Keep src same.
# * Use normal AST and src where possible.
# * Delimiters where would match ast.unparse().
# * Special unparse where needed.


# (N)ormal container, (S)equence container
# | Separator (trailing)
# | |  Prefix (leaading)
# | |  |  Delimiters
# | |  |  |   Unparse special
# | |  |  |   |
#                                                                            .
# N ,     ()      (Tuple, 'elts')                         # expr*            -> Tuple                  _parse_expr_sliceelts
# N ,     []      (List, 'elts')                          # expr*            -> List                   _parse_expr / restrict seq
# N ,     {}      (Set, 'elts')                           # expr*            -> Set                    _parse_expr / restrict seq
#                                                                            .
# N ,     {}      (Dict, 'keys':'values')                 # expr:expr*       -> Dict                   _parse_expr / restrict dict
#                                                                            .
# N ,     []      (MatchSequence, 'patterns'):            # pattern*         -> MatchSequence          _parse_pattern / restrict MatchSequence
# N ,     {}      (MatchMapping, 'keys':'patterns'):      # expr:pattern*    -> MatchMapping           _parse_pattern / restrict MatchMapping
#                                                                            .
# N |             (MatchOr, 'patterns'):                  # pattern*         -> MatchOr                _parse_pattern / restrict MatchOr
#                                                                            .
#                                                                            .
#                                                                            .
# S ,             (ClassDef, 'bases'):                    # expr*            -> Tuple[expr_callarg]    _parse_expr_callargs
# S ,             (Call, 'args'):                         # expr*            -> Tuple[expr_callarg]    _parse_expr_callargs
#
# S ,             (Delete, 'targets'):                    # expr*            -> Tuple[target]          _parse_expr / restrict targets
# S ,             (Assign, 'targets'):                    # expr*            -> Tuple[target]          _parse_expr / restrict targets
#                                                                            .
#                                                                            .
#                                                                            .
# S ,             (MatchClass, 'patterns'):               # pattern*         -> Tuple[pattern]         _parse_pattern / restrict MatchSequence
#                                                                            .
# S ,             (ClassDef, 'keywords'):                 # keyword*         -> Tuple[keyword]         _parse_keywords
# S ,             (Call, 'keywords'):                     # keyword*         -> Tuple[keyword]         _parse_keywords
#                                                                            .
# S ,             (FunctionDef, 'type_params'):           # type_param*      -> Tuple[type_param]      _parse_type_params
# S ,             (AsyncFunctionDef, 'type_params'):      # type_param*      -> Tuple[type_param]      _parse_type_params
# S ,             (ClassDef, 'type_params'):              # type_param*      -> Tuple[type_param]      _parse_type_params
# S ,             (TypeAlias, 'type_params'):             # type_param*      -> Tuple[type_param]      _parse_type_params
#                                                                            .
# S ,             (With, 'items'):                        # withitem*        -> Tuple[withitem]        _parse_withitems               - no trailing commas
# S ,             (AsyncWith, 'items'):                   # withitem*        -> Tuple[withitem]        _parse_withitems               - no trailing commas
#                                                                            .
# S ,             (Import, 'names'):                      # alias*           -> Tuple[alias]           _parse_aliases_dotted          - no trailing commas
# S ,             (ImportFrom, 'names'):                  # alias*           -> Tuple[alias]           _parse_aliases_star            - no trailing commas
#                                                                            .
#                                                                            .
#                                                                            .
# S ,             (Global, 'names'):                      # identifier*,     -> Tuple[Name]            _parse_expr / restrict Names   - no trailing commas, unparenthesized
# S ,             (Nonlocal, 'names'):                    # identifier*,     -> Tuple[Name]            _parse_expr / restrict Names   - no trailing commas, unparenthesized
#                                                                            .
#                                                                            .
#                                                                            .
# S    @      U   (FunctionDef, 'decorator_list'):        # expr*            -> Tuple[expr]            _parse_decorator_list  - can figure out from '@' first expr prefix
# S    @      U   (AsyncFunctionDef, 'decorator_list'):   # expr*            -> Tuple[expr]            _parse_decorator_list
# S    @      U   (ClassDef, 'decorator_list'):           # expr*            -> Tuple[expr]            _parse_decorator_list
#                                                                            .
# S           U   (ListComp, 'generators'):               # comprehension*   -> Tuple[comprehension]   _parse_comprehensions
# S           U   (SetComp, 'generators'):                # comprehension*   -> Tuple[comprehension]   _parse_comprehensions
# S           U   (DictComp, 'generators'):               # comprehension*   -> Tuple[comprehension]   _parse_comprehensions
# S           U   (GeneratorExp, 'generators'):           # comprehension*   -> Tuple[comprehension]   _parse_comprehensions
#                                                                            .
# S    if     U   (comprehension, 'ifs'):                 # expr*            -> Tuple[expr]            _parse_comprehension_ifs  - can figure out from 'if' first expr prefix
#                                                                            .
#                                                                            .
#                                                                            .
# N co            (Compare, 'ops':'comparators'):         # cmpop:expr*      -> expr or Compare        _parse_expr / restrict expr or Compare
#                                                                            .
# N ao            (BoolOp, 'values'):                     # expr*            -> BoolOp                 _parse_expr / restrict BoolOp  - interchangeable between and / or
#
#
#
#                 (JoinedStr, 'values'):                  # Constant|FormattedValue*  -> JoinedStr
#                 (TemplateStr, 'values'):                # Constant|Interpolation*   -> TemplateStr


# Tuple[expr]            _parse_expr_sliceelts
# Tuple[expr]            _parse_expr_callargs
# Tuple[keyword]         _parse_keywords
# Tuple[type_param]      _parse_type_params
# Tuple[withitem]        _parse_withitems
# Tuple[alias]           _parse_aliases_dotted
# Tuple[alias]           _parse_aliases_star


# --- NOT CONTIGUOUS! -------------------------------

# (arguments, 'posonlyargs'):           # arg*
# (arguments, 'args'):                  # arg*
# (arguments, 'kwonlyargs'):            # arg*

# (MatchClass, 'kwd_attrs'):            # identifier*
# (MatchClass, 'kwd_patterns'):         # pattern*     - maybe do as a two-element?


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

    lines  = self.root._lines
    single = loc_last is loc_first

    first_ln, first_col, last_end_ln, last_end_col = loc_first

    if not single:
        _, _, last_end_ln, last_end_col = loc_last

    if (sep and (code := _next_src(lines, last_end_ln, last_end_col, bound_end_ln, bound_end_col)) and
        code.src.startswith(sep)
    ):  # if separator present then set end of element to just past it
        sep_end_pos = end_pos = (last_end_ln := code.ln, last_end_col := code.col + len(sep))

    else:
        sep_end_pos = None
        end_pos     = (last_end_ln, last_end_col)

    # if is_first and is_last:
    #     return ((l := fstloc(bound_ln, bound_col, bound_end_ln, bound_end_col)), l, None, sep_end_pos)  # case 0

    ld_comms, ld_space, ld_neg, tr_comms, tr_space, tr_neg = fst.FST._get_trivia_params(trivia, neg)

    ld_text_pos, ld_space_pos, indent = _leading_trivia(lines, bound_ln, bound_col,  # start of text / space
                                                        first_ln, first_col, ld_comms, ld_space)
    tr_text_pos, tr_space_pos, _      = _trailing_trivia(lines, bound_end_ln, bound_end_col,  # END of text / space
                                                         last_end_ln, last_end_col, tr_comms, tr_space)

    def calc_locs(ld_ln: int, ld_col: int, tr_ln: int, tr_col: int):
        if indent is None:  # does not start line, no preceding trivia
            del_col = re_line_trailing_space.match(lines[first_ln], 0 if first_ln > bound_ln else bound_col,
                                                   first_col).start(1)

            if tr_ln == last_end_ln:  # does not extend past end of line (different from _trailing_trivia() 'ends_line')
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

        if tr_ln == last_end_ln:  # does not extend past end of line (different from _trailing_trivia() 'ends_line')
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
            ld_ln  = ld_text_pos[0]  # this is where space would have been without negative
            ld_col = 0

    if tr_different := tr_space_pos and tr_neg and tr_space:
        if tr_text_pos[0] == tr_ln:  # if on same line then space was on line of element and there should be no difference
            tr_different = False

        else:  # text pos could still be at end of element line or beginning of new line, need to handle differently
            tr_ln, tr_col = tr_text_pos

            if tr_col:
                tr_ln  += 1
                tr_col  = 0

    if not (ld_different or tr_different):  # if negative space offsets would not affect locations then we are done
        return cut_locs  # really copy_locs here

    copy_locs = calc_locs(ld_ln, ld_col, tr_ln, tr_col)

    return copy_locs[:1] + cut_locs[1:]  # copy location from copy_locs and delete location and indent from cut_locs


def _locs_first_and_last(self: fst.FST, start: int, stop: int, body: list[AST], body2: list[AST],
                         ) -> tuple[fstloc, fstloc]:
    stop_1 = stop - 1

    if body2 is body:
        loc_first = body[start].f.pars()
        loc_last  = loc_first if start == stop_1 else body[stop_1].f.pars()

    else:
        ln, col, _, _         = self._loc_maybe_dict_key(start, True, body)
        _, _, end_ln, end_col = body2[start].f.pars()
        loc_first             = fstloc(ln, col, end_ln, end_col)

        if start == stop_1:
            loc_last = loc_first

        else:
            ln, col, _, _         = self._loc_maybe_dict_key(stop_1, True, body)
            _, _, end_ln, end_col = body2[stop_1].f.pars()
            loc_last              = fstloc(ln, col, end_ln, end_col)

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
    `self_tail_sep=False`. Will ADD trailing separator to sequence if `self_tail_sep=False` if it is not there because
    this is a case for singleton tuples that may be left (even though that is detected here, allow override to force
    it).

    **WARNING!** (`bound_ln`, `bound_col`) is expected to be exactly the end of the previous element (past any closing
    pars) or the start of the container (past any opening delimiters) if no previous element. (`bound_end_ln`,
    `bound_end_col`) must be end of container just before closing delimiters.

    **Parameters:**
    - `start`, `stop`, `len_body`: Slice parameters, `len_body` being current length of field.
    - `ast`: The already build new `AST` that is being gotten. The elements being gotten must be in this with their
        current locations in the `self`.
    - `ast_last`: The `AST` of the last element copied or cut, not assumend to have `.f` `FST` attribute.
    - `loc_first`: The full location of the first element copied or cut, parentheses included.
    - `loc_last`: The full location of the last element copied or cut, parentheses included.
    - (`bound_ln`, `bound_col`): End of previous element (past pars) or start of container (just past
        delimiters) if no previous element. DIFFERENT FROM _put_slice_seq()!!!
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
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

    lines           = self.root._lines
    is_first        = not start
    is_last         = stop == len_body
    len_self_suffix = self.end_col - bound_end_col  # will be 1 or 0 depending on if enclosed container or unparenthesized tuple

    if ret_tail_sep and ret_tail_sep is not True and (stop - start) != 1:  # if ret_tail_sel == 1 and length will not be 1 then remove
        ret_tail_sep = 0

    if not cut:
        self_tail_sep = None
    else:
        self_tail_sep = _fixup_self_tail_sep_del(self, self_tail_sep, start, stop, len_body)

    # get locations and adjust for trailing separator keep or delete if possible to optimize

    copy_loc, del_loc, del_indent, sep_end_pos = _locs_slice_seq(self, is_first, is_last, loc_first, loc_last,
        bound_ln, bound_col, bound_end_ln, bound_end_col, trivia, sep, cut,
    )

    copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

    if not ret_tail_sep and sep_end_pos:
        if is_last and ret_tail_sep is not False:  # if is last element and already had trailing separator then keep it but not if explicitly forcing no tail sep
            ret_tail_sep = True  # this along with sep_end_pos != None will turn the ret_tail_sep checks below into noop

        elif sep_end_pos[0] == copy_end_ln == loc_last.end_ln and sep_end_pos[1] == copy_end_col:  # optimization common case, we can get rid of unneeded trailing separator in copy by just not copying it if it is at end of copy range on same line as end of element
            copy_loc     = fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col := loc_last.end_col)
            ret_tail_sep = True

    if self_tail_sep == 0:  # (or False), optimization common case, we can get rid of unneeded trailing separator in self by adding it to the delete block if del block starts on same line as previous element ends and there is not a comment on the line
        del_ln, _, del_end_ln, del_end_col = del_loc

        if del_ln == bound_ln and (del_end_ln != bound_ln or not lines[bound_ln].startswith('#', del_end_col)):
            del_loc       = fstloc(bound_ln, bound_col, del_end_ln, del_end_col)  # there can be nothing but a separator and whitespace between these locations
            self_tail_sep = None

    # set location of root node and make the actual FST

    ast.lineno         = copy_ln + 1
    ast.col_offset     = lines[copy_ln].c2b(copy_col)
    ast.end_lineno     = copy_end_ln + 1
    ast.end_col_offset = lines[copy_end_ln].c2b(copy_end_col)

    fst_ = self._make_fst_and_dedent(self, ast, copy_loc, prefix, suffix,
                                     del_loc if cut else None, [del_indent] if del_indent and del_loc.end_col else None)

    ast.col_offset     = 0  # before prefix
    ast.end_col_offset = fst_._lines[-1].lenbytes  # after suffix

    fst_._touch()

    # add / remove trailing separators as needed

    if not ret_tail_sep:  # don't need or want return trailing separator
        if sep_end_pos:  # but have it
            _, _, last_end_ln, last_end_col = ast_last.f.loc  # this will now definitely have the .f attribute and FST, we don't use _poss_end() because field may not be the same
            _, _, fst_end_ln,  fst_end_col  = fst_.loc

            fst_._maybe_del_separator(last_end_ln, last_end_col, ret_tail_sep is False,
                                      fst_end_ln, fst_end_col - len(suffix), sep)

    elif not sep_end_pos:  # need return trailing separator and don't have it
        _, _, last_end_ln, last_end_col = ast_last.f.loc
        _, _, fst_end_ln,  fst_end_col  = fst_.loc

        fst_._maybe_ins_separator(last_end_ln, last_end_col, False, fst_end_ln, fst_end_col - len(suffix), sep)

    if self_tail_sep:  # last element needs a trailing separator (singleton tuple maybe, requested by user)
        last_end_ln, last_end_col, self_end_ln, self_end_col = _poss_end(self, field, len_self_suffix)

        self._maybe_ins_separator(last_end_ln, last_end_col, False, self_end_ln, self_end_col, sep)

    elif self_tail_sep is not None:  # removed tail element(s) and what is left doesn't need its trailing separator
        last_end_ln, last_end_col, self_end_ln, self_end_col = _poss_end(self, field, len_self_suffix)  # will work without len_self_suffix, but consistency

        self._maybe_del_separator(last_end_ln, last_end_col, self_tail_sep is False, self_end_ln, self_end_col, sep)

    return fst_


def _poss_end(self: fst.FST, field: str, len_suffix: int):
    """Get position of end of self minus length of delimiter suffix and position of last element past pars, assumed to
    exist."""

    _, _, end_ln, end_col  = self.loc
    end_col               -= len_suffix

    if not isinstance(last := getattr(self.a, field)[-1], AST):  # Globals or Locals names
        return end_ln, end_col, end_ln, end_col

    _, _, last_end_ln, last_end_col = last.f.loc

    return last_end_ln, last_end_col, end_ln, end_col


def _locs_and_bound_get(self, start: int, stop: int, body: list[AST], body2: list[AST], off: int,
                        ) -> tuple[fstloc, fstloc, int, int, int, int]:
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
        asts  = [copy_ast(body[i]) for i in range(start, stop)]
        asts2 = [copy_ast(body2[i]) for i in range(start, stop)]

    else:
        asts  = body[start : stop]
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
                                   cut: bool, **options) -> fst.FST:
    raise NotImplementedError('this is not implemented yet')


def _get_slice_Dict(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                    **options) -> fst.FST:
    len_body    = len(body := (ast := self.a).keys)
    body2       = ast.values
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_dict(from_=self)

    locs        = _locs_and_bound_get(self, start, stop, body, body2, 1)
    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'values', cut, body, body2)
    ret_ast     = Dict(keys=asts, values=asts2)

    return _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
                          options.get('trivia'), 'values', '{', '}', ',', 0, 0)


def _get_slice_Tuple_elts(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                          **options) -> fst.FST:
    len_body    = len(body := (ast := self.a).elts)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_tuple(from_=self)

    is_par  = self._is_delimited_seq()
    locs    = _locs_and_bound_get(self, start, stop, body, body, is_par)
    asts    = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx     = ast.ctx.__class__
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
                         **options) -> fst.FST:
    len_body    = len(body := (ast := self.a).elts)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_list(from_=self)

    locs    = _locs_and_bound_get(self, start, stop, body, body, 1)
    asts    = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx     = ast.ctx.__class__
    ret_ast = List(elts=asts, ctx=ctx())

    if not issubclass(ctx, Load):  # new List root object must have ctx=Load
        set_ctx(ret_ast, Load)

    return _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'elts', '[', ']', ',', 0, 0)


def _get_slice_Set_elts(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                         **options) -> fst.FST:
    len_body    = len(body := self.a.elts)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return (
            fst.FST._new_empty_set_curlies() if not (set_get := self.get_option('set_get', options)) else
            fst.FST._new_empty_set_call() if set_get == 'call' else
            fst.FST._new_empty_tuple() if set_get == 'tuple' else
            fst.FST._new_empty_set_star()  # True, 'star'
        )

    locs    = _locs_and_bound_get(self, start, stop, body, body, 1)
    asts    = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ret_ast = Set(elts=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'elts', '{', '}', ',', 0, 0)

    self._maybe_fix_set(self.get_option('set_del', options))

    return fst_


def _get_slice_MatchSequence_patterns(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                      cut: bool, **options) -> fst.FST:
    len_body    = len(body := self.a.patterns)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_matchseq(from_=self)

    delims  = self.get_matchseq_delimiters()
    locs    = _locs_and_bound_get(self, start, stop, body, body, bool(delims))
    asts    = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchSequence(patterns=asts)

    if delims:
        prefix, suffix = delims
        tail_sep       = 1 if delims == '()' else 0

    else:
        prefix   = suffix = delims = ''
        tail_sep = 1

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'patterns', prefix, suffix, ',', tail_sep, tail_sep)

    if not delims:
        fst_._maybe_fix_matchseq('')

    self._maybe_fix_matchseq(delims)

    return fst_


def _get_slice_MatchMapping(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                            **options) -> fst.FST:
    len_body    = len(body := (ast := self.a).keys)
    body2       = ast.patterns
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST._new_empty_matchmap(from_=self)

    locs        = _locs_and_bound_get(self, start, stop, body, body2, 1)
    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'patterns', cut, body, body2)
    ret_ast     = MatchMapping(keys=asts, patterns=asts2, rest=None)

    # locs          = _locs_and_bound_get(self, start, stop, body, body2, 1)
    # asts, asts2   = _cut_or_copy_asts2(start, stop, 'keys', 'patterns', cut, body, body2)
    # ret_ast       = MatchMapping(keys=asts, patterns=asts2, rest=None)
    # have_rest     = ast.rest is not None
    # self_tail_sep = (have_rest and cut) or None
    # ret_tail_sep  = False if have_rest and stop == len_body else None

    # fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
    #                       options.get('trivia'), 'patterns', '{', '}', ',', self_tail_sep, ret_tail_sep)

    # if self_tail_sep and start and stop == len_body:  # if there is a **rest and we removed tail element so here we make sure there is a space between comma of the new last element and the **rest
    #     self._maybe_ins_separator(*body2[-1].f.loc[2:], True)  # this will only maybe add a space, comma is already there

    # return fst_

    if ast.rest is None or stop < len_body:
        fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
                              options.get('trivia'), 'patterns', '{', '}', ',', None, None)

    else:  # HACK to get trailing comma behavior same as if it was a longer list (because the **rest looks like its part of the list but is not)
        cut_and_start = cut and start

        fst_ = _get_slice_seq(self, start, stop, len_body + 1, cut, ret_ast, asts2[-1], *locs,
                              options.get('trivia'), 'patterns', '{', '}', ',', True if cut_and_start else None, None)

        if cut_and_start and stop == len_body:  # if there is a **rest and we removed tail element so here we make sure there is a space between comma of the new last element and the **rest
            self._maybe_ins_separator(*body2[-1].f.loc[2:], True)  # this will only maybe add a space, comma is already there

    return fst_


def _get_slice_MatchOr_patterns(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                cut: bool, **options) -> fst.FST:
    len_body    = len(body := self.a.patterns)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice   = stop - start
    matchor_get = self.get_option('matchor_get', options)
    matchor_del = self.get_option('matchor_del', options)

    if not len_slice:
        if matchor_get:
            raise NodeError("cannot get empty slice from MatchOr without matchor_get=False")

        return fst.FST._new_empty_matchor(from_=self)

    if len_slice == 1 and matchor_get == 'strict':
        raise NodeError("cannot get length 1 slice from MatchOr with matchor_get='strict'")

    if cut:
        if not (len_left := len_body - len_slice):
            if matchor_del:
                raise NodeError("cannot cut MatchOr to empty without matchor_get=False")

        elif len_left == 1 and matchor_del == 'strict':
            raise NodeError("cannot cut MatchOr to length 1 with matchor_get='strict'")

    locs    = _locs_and_bound_get(self, start, stop, body, body, 0)
    asts    = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchOr(patterns=asts)

    fst_ = _get_slice_seq(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                          options.get('trivia'), 'patterns', '', '', '|', False, False)

    fst_._maybe_fix_matchor(bool(matchor_get))
    self._maybe_fix_matchor(bool(matchor_del))

    return fst_


# TODO: handle trailing line continuation backslashes
def _get_slice_Import_names(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                            **options) -> fst.FST:
    len_body    = len(body := self.a.names)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return self._new_empty_tuple(from_=self)
    if cut and not start and stop == len_body:
        raise ValueError('cannot cut all Import.names')

    _, _, bound_end_ln, bound_end_col = body[-1].f.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln, bound_col, _, _ = body[0].f.loc

    ln, col, end_ln, end_col = body[start].f.loc

    if (last := stop - 1) != start:
        _, _, end_ln, end_col = body[last].f.loc

    asts    = _cut_or_copy_asts(start, stop, 'names', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    return _get_slice_seq(self, start, stop, len_body, cut, ret_ast,
                          bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col,
                          options.get('trivia'), 'names', '', '', ',', False, False)


# TODO: handle trailing line continuation backslashes
def _get_slice_Global_Local_names(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                  cut: bool, **options) -> fst.FST:
    len_body    = len((ast := self.a).names)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return self._new_empty_tuple(from_=self)
    if cut and not start and stop == len_body:
        raise ValueError(f'cannot cut all {ast.__class__.__name__}.names')

    ln, col, end_ln, end_col = self.loc

    col      += 6 if isinstance(ast, Global) else 8
    lines     = self.root._lines
    ret_elts  = []
    ret_ast   = Tuple(elts=ret_elts, ctx=Load())

    for _ in range(start):
        ln, col  = _next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col     += 1

    for i in range(stop - start):  # create tuple of Names from identifiers
        ln, col, src = _next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there
        lineno       = ln + 1
        end_col      = col + len(src)

        if not i:  # TODO: is this right???
            bound_ln  = ln
            bound_col = col

        ret_elts.append(Name(id=src, ctx=Load(), lineno=lineno, col_offset=(l := lines[ln]).c2b(col), end_lineno=lineno,
                             end_col_offset=l.c2b(end_col)))

        col = end_col + 1  # + 1 probably skip comma

    bound_end_ln  = ln
    bound_end_col = col

    return _get_slice_seq(self, start, stop, len_body, cut, ret_ast,
                          bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col,
                          options.get('trivia'), 'names', '', '', ',', False, False)


# ......................................................................................................................

def _get_slice(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
               **options) -> fst.FST:
    """Get a slice of child nodes from `self`."""

    if not (handler := _GET_SLICE_HANDLERS.get((self.a.__class__, field))):
        raise ValueError(f"cannot get slice from {self.a.__class__.__name__}{f'.{field}' if field else ''}")

    return handler(self, start, stop, field, cut, **options)


_GET_SLICE_HANDLERS = {
    (Module, 'body'):                     _get_slice_stmtish,  # stmt*
    (Interactive, 'body'):                _get_slice_stmtish,  # stmt*
    (FunctionDef, 'body'):                _get_slice_stmtish,  # stmt*
    (AsyncFunctionDef, 'body'):           _get_slice_stmtish,  # stmt*
    (ClassDef, 'body'):                   _get_slice_stmtish,  # stmt*
    (For, 'body'):                        _get_slice_stmtish,  # stmt*
    (For, 'orelse'):                      _get_slice_stmtish,  # stmt*
    (AsyncFor, 'body'):                   _get_slice_stmtish,  # stmt*
    (AsyncFor, 'orelse'):                 _get_slice_stmtish,  # stmt*
    (While, 'body'):                      _get_slice_stmtish,  # stmt*
    (While, 'orelse'):                    _get_slice_stmtish,  # stmt*
    (If, 'body'):                         _get_slice_stmtish,  # stmt*
    (If, 'orelse'):                       _get_slice_stmtish,  # stmt*
    (With, 'body'):                       _get_slice_stmtish,  # stmt*
    (AsyncWith, 'body'):                  _get_slice_stmtish,  # stmt*
    (Try, 'body'):                        _get_slice_stmtish,  # stmt*
    (Try, 'orelse'):                      _get_slice_stmtish,  # stmt*
    (Try, 'finalbody'):                   _get_slice_stmtish,  # stmt*
    (TryStar, 'body'):                    _get_slice_stmtish,  # stmt*
    (TryStar, 'orelse'):                  _get_slice_stmtish,  # stmt*
    (TryStar, 'finalbody'):               _get_slice_stmtish,  # stmt*
    (ExceptHandler, 'body'):              _get_slice_stmtish,  # stmt*
    (match_case, 'body'):                 _get_slice_stmtish,  # stmt*

    (Match, 'cases'):                     _get_slice_stmtish,  # match_case*
    (Try, 'handlers'):                    _get_slice_stmtish,  # excepthandler*
    (TryStar, 'handlers'):                _get_slice_stmtish,  # excepthandlerstar*

    (Dict, ''):                           _get_slice_Dict,  # key:value*

    (Set, 'elts'):                        _get_slice_Set_elts,  # expr*
    (List, 'elts'):                       _get_slice_List_elts,  # expr*
    (Tuple, 'elts'):                      _get_slice_Tuple_elts,  # expr*

    (FunctionDef, 'decorator_list'):      _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (AsyncFunctionDef, 'decorator_list'): _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (ClassDef, 'decorator_list'):         _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (ClassDef, 'bases'):                  _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Delete, 'targets'):                  _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Assign, 'targets'):                  _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (BoolOp, 'values'):                   _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Compare, ''):                        _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Call, 'args'):                       _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (comprehension, 'ifs'):               _get_slice_NOT_IMPLEMENTED_YET,  # expr*

    (ListComp, 'generators'):             _get_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (SetComp, 'generators'):              _get_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (DictComp, 'generators'):             _get_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (GeneratorExp, 'generators'):         _get_slice_NOT_IMPLEMENTED_YET,  # comprehension*

    (ClassDef, 'keywords'):               _get_slice_NOT_IMPLEMENTED_YET,  # keyword*
    (Call, 'keywords'):                   _get_slice_NOT_IMPLEMENTED_YET,  # keyword*

    (Import, 'names'):                    _get_slice_NOT_IMPLEMENTED_YET,  # alias*
    (ImportFrom, 'names'):                _get_slice_NOT_IMPLEMENTED_YET,  # alias*

    (With, 'items'):                      _get_slice_NOT_IMPLEMENTED_YET,  # withitem*
    (AsyncWith, 'items'):                 _get_slice_NOT_IMPLEMENTED_YET,  # withitem*

    (MatchSequence, 'patterns'):          _get_slice_MatchSequence_patterns,  # pattern*
    (MatchMapping, ''):                   _get_slice_MatchMapping,  # key:pattern*
    (MatchClass, 'patterns'):             _get_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchOr, 'patterns'):                _get_slice_MatchOr_patterns,  # pattern*

    (FunctionDef, 'type_params'):         _get_slice_NOT_IMPLEMENTED_YET,  # type_param*
    (AsyncFunctionDef, 'type_params'):    _get_slice_NOT_IMPLEMENTED_YET,  # type_param*
    (ClassDef, 'type_params'):            _get_slice_NOT_IMPLEMENTED_YET,  # type_param*
    (TypeAlias, 'type_params'):           _get_slice_NOT_IMPLEMENTED_YET,  # type_param*

    (Global, 'names'):                    _get_slice_NOT_IMPLEMENTED_YET,  # identifier*
    (Nonlocal, 'names'):                  _get_slice_NOT_IMPLEMENTED_YET,  # identifier*

    (JoinedStr, 'values'):                _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (TemplateStr, 'values'):              _get_slice_NOT_IMPLEMENTED_YET,  # expr*
}


# ----------------------------------------------------------------------------------------------------------------------
# put

def _put_slice_seq(self: fst.FST, start: int, stop: int, fst_: fst.FST | None,
                   fst_first: fst.FST | fstloc | None, fst_last: fst.FST | None, len_fst: int,
                   bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                   trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None,
                   ins_ln: int | None = None,
                   field: str = 'elts', field2: str | None = None, sep: str = ',',
                   self_tail_sep: bool | Literal[0, 1] | None = None,
                   ):
    r"""Indent a sequence source and put it to a location in existing sequence `self`. If `fst_` is `None` then will
    just delete in the same way that a cut operation would. Trailing separators will be added / removed as needed and
    according to if they are in normal positions. If delete from `self` leaves an empty unparenthesized tuple then
    parentheses will NOT be added here.

    If an empty slice was going to be put we expect that it will be converted to a put `None` delete of existing
    elements. If an `fst_` is provided then it is assumed it has at least one element. No empty put to empty location,
    likewise no delete from empty location.

    BE WARNED! Here there be dragons!

    **Parameters:**
    - `start`, `stop`: Slice parameters.
    - `fst_`: The slice being put to `self` with delimiters stripped, or `None` for delete.
    - `fst_first`: The first element of the slice `FST` being put, or `None` if delete. Must be an `fstloc` for `Dict`
        key which is `None`.
    - `fst_last`: The last element of the slice `FST` being put, or `None` if delete.
    - (`bound_ln`, `bound_col`): Start of container (just past delimiters). DIFFERENT FROM _get_slice_seq()!!!
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
    - `trivia`: Standard option on how to handle leading and trailing comments and space, `None` means global default.
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
    """

    lines           = self.root._lines
    body            = getattr(self.a, field)
    body2           = body if field2 is None else getattr(self.a, field2)
    len_body        = len(body)
    is_first        = not start
    is_last         = stop == len_body
    is_del          = fst_ is None
    is_ins          = start == stop  # will never be true if fst_ is None
    is_ins_ln       = False
    last            = None  # means body[-1]
    len_self_suffix = self.end_col - bound_end_col  # will be 1 or 0 depending on if enclosed container or unparenthesized tuple
    self_indent     = self.get_indent()

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
                    ln  = bound_end_ln
                    col = bound_end_col

                if ins_ln >= ln:
                    loc_first = fstloc(ln, col, ln, col)

                else:  # TODO: this part changes if we do alignment of fst_ to self element indentation
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
            ln, col, _, _        = self._loc_maybe_dict_key(stop, True, body)
            loc_first = fstloc(ln, col, ln, col)

        else:  # just past previous element or at start of bound
            loc_first = fstloc(bound_ln, bound_col, bound_ln, bound_col)

        loc_last = loc_first

    copy_loc, del_loc, del_indent, _ = _locs_slice_seq(self, is_first, is_last, loc_first, loc_last,
        bound_ln, bound_col, bound_end_ln, bound_end_col,
        trivia, sep, is_del,
    )

    put_ln, put_col, put_end_ln, put_end_col = del_loc

    # delete

    if is_del:
        put_lines     = [del_indent] if del_indent and put_end_col else None
        self_tail_sep = _fixup_self_tail_sep_del(self, self_tail_sep, start, stop, len_body)

        if self_tail_sep == 0:  # (or False), optimization, we can get rid of unneeded trailing separator in self by adding it to the delete block if del block starts on same line as previous element ends and there is not a comment on the line
            if put_ln == bound_ln and (put_end_ln != bound_ln or not lines[bound_ln].startswith('#', put_end_col)):
                put_ln        = bound_ln  # there can be nothing but a separator and whitespace between these locations
                put_col       = bound_col
                self_tail_sep = None

            elif is_last:
                last = body2[start - 1].f  # if deleted tail then new last element is this

    # insert or replace

    else:
        copy_ln, copy_col, _, _ = copy_loc

        put_lines   = fst_._lines
        skip        = 1
        post_indent = None  # this is a FULL indent in self, not a partial indent in fst_

        if re_line_end_cont_or_comment.match(put_lines[l := len(put_lines) - 1],  # if last line of fst_ is a comment or line continuation without a newline then add one (don't need to check pars for last line)
                                             0 if l > fst_last.end_ln else fst_last.end_col).group(1):
            put_lines.append(bistr(''))

        # newlines and indentation

        if fst_starts_nl := not put_lines[0]:  # slice to put start with pure newline?
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
                    elif (post_indent := _get_element_indent(self, body, body2, start)) is not None:  # indentation from other elements in self
                        pass  # noop
                    elif fst_starts_nl:  # match indentation of first fst_ element on new line
                        post_indent = (self_indent +
                                       put_lines[(l := fst_first.pars() if fst_first.is_FST else fst_first).ln]
                                                [:l.col])
                    elif body:  # match indentation of our own first element
                        post_indent = self_indent + ' ' * (self._loc_maybe_dict_key(0, True, body).col -
                                                           len(self_indent))
                    else:
                        post_indent = self_indent + self.root.indent  # default

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

        elif (not _re_one_space.match(put_lines[-1][-1]) and   # putting something that ends with non-space to something that starts with not a closing delimiter, put space between
              not _re_close_delim_or_end.match(lines[put_end_ln], put_end_col) and
              (put_end_ln < self.end_ln or put_end_col < self.end_col)  # but not at the very end of self
        ):
            put_lines[-1] = bistr(put_lines[-1] + ' ')

        # trailing separator

        if is_last:
            last = fst_last

            if self_tail_sep is None:
                if pos := _next_find(put_lines, fst_last.end_ln, fst_last.end_col, fst_.end_ln, fst_.end_col, sep):  # only remove if slice being put actually has trailing separator
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

        fst_._lines = lines  # SPECIAL! for potential fst_ last element .loc access below when adjusting trailing separator, this must be done after the fst_ modifications just above because those need the actual fst_ lines

    # put source

    self_ln, self_col, _, _ = self.loc

    if put_col == self_col and put_ln == self_ln:  # put at beginning of unenclosed sequence
        self._offset(
            *self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, is_last, False, self),
            True, True, self_=False)

    elif not is_last:
        self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, False)
    else:
        self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, True, self)  # because of insertion at end and maybe unenclosed sequence

    # put / del trailing and internal separators

    if self_tail_sep is not None:  # trailing
        _, _, last_end_ln, last_end_col  = (last or body2[-1].f).loc
        _, _, self_end_ln, self_end_col  = self.loc
        self_end_col                    -= len_self_suffix

        if self_tail_sep:
            self._maybe_ins_separator(last_end_ln, last_end_col, False, self_end_ln, self_end_col, sep)
        else:
            self._maybe_del_separator(last_end_ln, last_end_col, self_tail_sep is False, self_end_ln, self_end_col, sep)

    if not is_del:  # internal, this is messy because the source has been put but the ASTs have not, so locations have to be gotten from and updated in two trees
        if not is_last:  # past the newly put slice
            _, _, fst_last_end_ln, fst_last_end_col = fst_last.pars()

            if a := body[stop]:  # explicit _loc_maybe_dict_key() logic because self AST tree is not complete
                stop_ln, stop_col, _, _ = a.f.loc
            else:
                stop_ln, stop_col = _prev_find(lines, fst_last_end_ln, fst_last_end_col,
                                               (l := body2[stop].f.loc).end_ln, l.end_col, '**')  # '**' must be there

            self._maybe_ins_separator(fst_last_end_ln, fst_last_end_col, True, stop_ln, stop_col, sep, None)  # last False is because elements of self are now past comma point so will need to be offset

        if is_ins and not is_first:  # before newly appended slice at end
            _, _, stop_end_ln, stop_end_col = (f := body2[stop - 1].f).pars()

            if not fst_first.is_FST:  # special case, should only happend for Dict None key, don't like this is messy
                fst_first = fst_._loc_maybe_dict_key(0)

            if is_last:
                exclude         = ...
                offset_excluded = True

            else:  # need to exclude this specifically because otherwise would extend its end to include the separator
                exclude         = f
                offset_excluded = False

            if code := self._maybe_ins_separator(stop_end_ln, stop_end_col, True, fst_first.ln, fst_first.col, sep,
                                                 exclude, offset_excluded):  # if something was put (separator and / or space) then we need to explicitly offset the fst_ elements as well since they don't live in self yet but in fst_
                ln, col, src = code

                fst_._offset(ln, col, 0, len(src))


def _get_element_indent(self: fst.FST, body: list[AST], body2: list[AST], start: int) -> str | None:
    """Get first exprish element indentation found for an element which starts its own line.

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
                    if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                        return l[:loc.col]

                loc = prev_loc

            if loc.ln != self.ln:  # only consider element 0 if it is not on same line as self starts
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

            loc = start_prev_loc

        else:
            loc = fstloc(-1, -1, -1, -1)  # dummy

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
            loc = fstloc(-1, -1, -1, -1)  # dummy

        for i in range(start, len(body)):  # now search forward
            if (loc := self._loc_maybe_dict_key(i, True, body)).ln != body2[i - 1].f.pars().end_ln:  # only consider elements which start on a different line than the previous element ends on
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

    return None


def _trim_delimiters(self: fst.FST):
    lines                     = self._lines
    ast                       = self.a
    ln, col, end_ln, end_col  = self.loc
    col                      += 1
    end_col                  -= 1
    ast.col_offset           += 1
    ast.end_col_offset       -= 1

    self._offset(ln, col, -ln, -lines[ln].c2b(col))

    lines[end_ln] = bistr(lines[end_ln][:end_col])
    lines[ln]     = bistr(lines[ln][col:])

    del lines[end_ln + 1:], lines[:ln]


def _set_loc_whole(self: fst.FST):
    ast                = self.a
    ast.lineno         = 1
    ast.col_offset     = 0
    ast.end_lineno     = len(ls := self._lines)
    ast.end_col_offset = ls[-1].lenbytes

    self._touch()


def _code_to_slice_seq(self: fst.FST, code: Code | None, one: bool, options: dict[str, Any]) -> fst.FST | None:
    if code is None:
        return None

    fst_ = _code_as_expr(code, self.root.parse_params, sanitize=False)

    if one:
        if fst_.is_parenthesized_tuple() is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
            fst_._delimit_node()

        elif isinstance(a := fst_.a, Set):
            if (empty := self.get_option('set_del', options)):  # putting an invalid empty Set as one, make it valid according to options
                fst_._maybe_fix_set(empty)

        elif isinstance(a, NamedExpr):  # this needs to be parenthesized if being put to unparenthesized tuple
            if not fst_.pars().n and self.is_parenthesized_tuple() is False:
                fst_._parenthesize_grouping()

        elif isinstance(a, (Yield, YieldFrom)):  # these need to be parenthesized definitely
            if not fst_.pars().n:
                fst_._parenthesize_grouping()

        ls  = fst_._lines
        ast = List(elts=[fst_.a], ctx=Load(),
                   lineno=1, col_offset=0, end_lineno=len(ls), end_col_offset=ls[-1].lenbytes)  # because List is valid target if checked in validate

        return fst.FST(ast, ls, from_=fst_, lcopy=False)

    if set_put := self.get_option('set_put', options):
        if (fst_.is_empty_set_star() if set_put == 'star' else
            fst_.is_empty_set_call() if set_put == 'call' else
            fst_.is_empty_set_star() or fst_.is_empty_set_call()  # True or 'both'
        ):
            return None

    ast_ = fst_.a

    if not isinstance(ast_, (Tuple, List, Set)):
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} "
                        f"must be a Tuple, List or Set, not a {ast_.__class__.__name__}")

    if not ast_.elts:  # put empty sequence is same as delete
        return None

    if fst_.is_parenthesized_tuple() is not False:  # anything that is not an unparenthesize tuple is restricted to the inside of the delimiters, which are removed
        _trim_delimiters(fst_)
    else:  # if unparenthesized tuple then use whole source, including leading and trailing trivia not included
        _set_loc_whole(fst_)

    return fst_


def _code_to_slice_seq2(self: fst.FST, code: Code | None, one: bool, options: dict[str, Any], code_as: Callable,
                        ) -> fst.FST | None:
    if code is None:
        return None

    if one:
        raise ValueError(f"cannot put as 'one' item to a {self.a.__class__.__name__} slice")

    fst_ = code_as(code, self.root.parse_params, sanitize=False)
    ast_ = fst_.a

    if ast_.__class__ is not self.a.__class__:
        raise ValueError(f"slice being assigned to a {self.a.__class__.__name__} must be a {self.a.__class__.__name__}"
                         f", not a {ast_.__class__.__name__}")

    if not ast_.keys:  # put empty sequence is same as delete
        return None

    _trim_delimiters(fst_)

    return fst_


def _code_to_slice_MatchSequence(self: fst.FST, code: Code | None, one: bool, options: dict[str, Any],
                                 ) -> fst.FST | None:
    if code is None:
        return None

    fst_ = _code_as_pattern(code, self.root.parse_params, sanitize=False)

    if one:
        if fst_.get_matchseq_delimiters() == '':
            fst_._delimit_node(delims='[]')

        ls  = fst_._lines
        ast = MatchSequence(patterns=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls),
                            end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast, ls, from_=self, lcopy=False)

    ast_ = fst_.a

    if not isinstance(ast_, MatchSequence):
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} "
                        f"must be a MatchSequence, not a {ast_.__class__.__name__}")

    if not ast_.patterns:  # put empty sequence is same as delete
        return None

    if fst_.get_matchseq_delimiters():  # delimited is restricted to the inside of the delimiters, which are removed
        _trim_delimiters(fst_)
    else:  # if undelimited then use whole source, including leading and trailing trivia not included
        _set_loc_whole(fst_)

    return fst_


def _code_to_slice_MatchOr(self: fst.FST, code: Code | None, one: bool, options: dict[str, Any]) -> fst.FST | None:
    if code is None:
        return None

    try:
        fst_ = _code_as_pattern(code, self.root.parse_params, sanitize=False)

    except (NodeError, SyntaxError):
        if (not (isinstance(code, list) or (isinstance(code, str) and (code := code.split('\n')))) or
            not _next_src(code, 0, 0, len(code) - 1, len(code[-1]))
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
        if not one and not self.get_option('matchor_put', options):
            raise NodeError(f"slice being assigned to a MatchOr "
                            f"must be a MatchOr with matchor_put=False, not a {ast_.__class__.__name__}")

        if isinstance(ast_, MatchAs):
            if ast_.pattern is not None and not fst_.pars().n:
                fst_._parenthesize_grouping()

        elif isinstance(ast_, MatchSequence):
            if not fst_.get_matchseq_delimiters():
                fst_._delimit_node(delims='[]')

    ls   = fst_._lines
    ast_ = MatchOr(patterns=[ast_], lineno=1, col_offset=0, end_lineno=len(ls), end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, from_=fst_, lcopy=False)


def _validate_put_seq(self: fst.FST, fst_: fst.FST, non_slice: str, *, check_target: bool = False):
    if not fst_:
        return

    ast  = self.a
    ast_ = fst_.a

    if non_slice and isinstance(ast_, Tuple) and any(isinstance(e, Slice) for e in ast_.elts):
        raise ValueError(f'cannot put Slice into a {non_slice}')

    if check_target and not isinstance(ctx := ast.ctx, Load) and not is_valid_target(ast_.elts[:]):
        raise ValueError(f'invalid slice for {ast.__class__.__name__} {ctx.__class__.__name__} target')


# ......................................................................................................................

def _put_slice_NOT_IMPLEMENTED_YET(self: fst.FST, code: Code | None, start: int | Literal['end'] | None,
                                   stop: int | None, field: str, one: bool = False, **options,
                                   ):
    raise NotImplementedError("not implemented yet, try with option raw='auto'")


def _put_slice_Dict(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                    field: str, one: bool = False, **options):
    fst_        = _code_to_slice_seq2(self, code, one, options, _code_as_expr)
    body        = (ast := self.a).keys
    body2       = ast.values
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col     += 1
    bound_end_col -= 1

    if not fst_:
        _put_slice_seq(self, start, stop, None, None, None, 0,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'), 'keys', 'values')

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])

        del body[start : stop]
        del body2[start : stop]

        len_fst_body = 0

    else:
        ast_         = fst_.a
        fst_body     = ast_.keys
        fst_body2    = ast_.values
        len_fst_body = len(fst_body)
        fst_first    = a.f if (a := fst_body[0]) else fst_._loc_maybe_dict_key(0)

        _put_slice_seq(self, start, stop, fst_, fst_first, fst_body2[-1].f, len_fst_body,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'), 'keys', 'values')

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop]  = fst_body
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


def _put_slice_Tuple_elts(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                          field: str, one: bool = False, **options):
    fst_        = _code_to_slice_seq(self, code, one, options)
    body        = (ast := self.a).elts
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    is_par   = self._is_delimited_seq()
    is_slice = (pfield := self.pfield) and pfield.name == 'slice'
    need_par = False

    if fst_:
        len_fst_body = len(fst_body := fst_.a.elts)

        if PYLT11:
            if is_slice and not is_par and any(isinstance(e, Starred) for e in fst_body):
                if any(isinstance(e, Slice) for i, e in enumerate(body) if i < start or i >= stop):
                    raise ValueError('cannot put Starred to a slice Tuple containing Slices')

                need_par = True

        elif PYGE14:
            if not is_par and pfield == ('type', None) and any(isinstance(e, Starred) for e in fst_body):  # if putting Starred to unparenthesized ExceptHandler.type Tuple then parenthesize it
                need_par = True

    _validate_put_seq(self, fst_,
                      '' if not is_par and (not pfield or is_slice) else 'non-slice Tuple',
                      check_target=True)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if is_par:
        bound_col     += 1
        bound_end_col -= 1

    if not fst_:
        _put_slice_seq(self, start, stop, None, None, None, 0,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'), self_tail_sep=1)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        _put_slice_seq(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'), self_tail_sep=1)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST   = fst.FST
        stack = [FST(body[i], self, astfield('elts', i)) for i in range(start, start + len_fst_body)]

        if stack:
            set_ctx([f.a for f in stack], ast.ctx.__class__)

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('elts', i)

    is_par = self._maybe_fix_tuple(is_par)

    if need_par and not is_par:
        self._delimit_node()


def _put_slice_List_elts(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                         field: str, one: bool = False, **options):
    fst_        = _code_to_slice_seq(self, code, one, options)
    body        = (ast := self.a).elts
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'List', check_target=True)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col     += 1
    bound_end_col -= 1

    if not fst_:
        _put_slice_seq(self, start, stop, None, None, None, 0,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'))

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.elts)

        _put_slice_seq(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'))

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST   = fst.FST
        stack = [FST(body[i], self, astfield('elts', i)) for i in range(start, start + len_fst_body)]

        if stack:
            set_ctx([f.a for f in stack], ast.ctx.__class__)

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('elts', i)


def _put_slice_Set_elts(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                        field: str, one: bool = False, **options):
    fst_        = _code_to_slice_seq(self, code, one, options)
    body        = self.a.elts
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'Set')

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col     += 1
    bound_end_col -= 1

    if not fst_:
        _put_slice_seq(self, start, stop, None, None, None, 0,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'))

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.elts)

        _put_slice_seq(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'))

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST   = fst.FST
        stack = [FST(body[i], self, astfield('elts', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('elts', i)

    self._maybe_fix_set(self.get_option('set_del', options))


def _put_slice_MatchSequence_patterns(self: fst.FST, code: Code | None, start: int | Literal['end'] | None,
                                      stop: int | None, field: str, one: bool = False, **options):
    # NOTE: we allow multiple MatchStars to be put to the same MatchSequence
    fst_        = _code_to_slice_MatchSequence(self, code, one, options)
    body        = self.a.patterns
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if delims := self.get_matchseq_delimiters():
        bound_col     += 1
        bound_end_col -= 1

    if not fst_:
        _put_slice_seq(self, start, stop, None, None, None, 0,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'), 'patterns', None, ',', 0)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.patterns)

        _put_slice_seq(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'), 'patterns', None, ',', 0)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST   = fst.FST
        stack = [FST(body[i], self, astfield('patterns', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('patterns', i)

    self._maybe_fix_matchseq(delims)


def _put_slice_MatchMapping(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                            field: str, one: bool = False, **options):
    fst_        = _code_to_slice_seq2(self, code, one, options, _code_as_pattern)
    len_body    = len(body := (ast := self.a).keys)
    body2       = ast.patterns
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col     += 1
    bound_end_col -= 1

    if not fst_:
        tail_space = (start and stop == len_body and ast.rest is not None) or None

        _put_slice_seq(self, start, stop, None, None, None, 0,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'), 'keys', 'patterns',
                       self_tail_sep=tail_space)

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])

        del body[start : stop]
        del body2[start : stop]

        len_fst_body = 0

    else:
        ast_         = fst_.a
        fst_body     = ast_.keys
        fst_body2    = ast_.patterns
        len_fst_body = len(fst_body)
        tail_space   = False

        _put_slice_seq(self, start, stop, fst_, fst_body[0].f, fst_body2[-1].f, len_fst_body,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       options.get('trivia'), options.get('ins_ln'), 'keys', 'patterns',
                       self_tail_sep=ast.rest is not None)

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop]  = fst_body
        body2[start : stop] = fst_body2

        stack = []

        for i in range(len_fst_body):
            startplusi = start + i

            stack.append(fst.FST(body[startplusi], self, astfield('keys', startplusi)))
            stack.append(fst.FST(body2[startplusi], self, astfield('patterns', startplusi)))

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield  = astfield('keys', i)
        body2[i].f.pfield = astfield('patterns', i)

    if tail_space:  # if there is a **rest and we removed tail element so here we make sure there is a space between comma of the new last element and the **rest
        self._maybe_ins_separator(*body2[-1].f.loc[2:], True)  # this will only maybe add a space, comma is already there


def _put_slice_MatchOr_patterns(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                field: str, one: bool = False, **options):
    fst_        = _code_to_slice_MatchOr(self, code, one, options)
    len_body    = len(body := self.a.patterns)
    start, stop = _fixup_slice_indices(len_body, start, stop)
    len_slice   = stop - start
    matchor_del = self.get_option('matchor_del', options)

    if not fst_:
        if not len_slice:
            return

        if not (len_left := len_body - len_slice):
            if matchor_del:
                raise NodeError("cannot del MatchOr to empty without matchor_del=False")

        elif len_left == 1 and matchor_del == 'strict':
            raise NodeError("cannot del MatchOr to length 1 with matchor_del='strict'")

        _put_slice_seq(self, start, stop, None, None, None, 0, *self.loc,
                       options.get('trivia'), options.get('ins_ln'), 'patterns', None, '|', False)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        len_fst_body = len(fst_body := fst_.a.patterns)

        if (len_body - len_slice + len_fst_body) == 1 and matchor_del == 'strict':
            raise NodeError("cannot put MatchOr to length 1 with matchor_del='strict'")

        _put_slice_seq(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body, *self.loc,
                       options.get('trivia'), options.get('ins_ln'), 'patterns', None, '|', False)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST   = fst.FST
        stack = [FST(body[i], self, astfield('patterns', i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('patterns', i)

    self._maybe_fix_matchor(matchor_del)


# ......................................................................................................................

def _put_slice(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
               one: bool = False, **options) -> Union[Self, fst.FST, None]:  # -> Self or reparsed Self or could disappear due to raw
    """Put an a slice of child nodes to `self`."""

    if code is self.root:  # don't allow own root to be put to self
        raise NodeError('circular put detected')

    raw = fst.FST.get_option('raw', options)

    if options.get('to') is not None:
        raise ValueError("cannot put slice with 'to'")

    if raw is not True:
        try:
            if not (handler := _PUT_SLICE_HANDLERS.get((self.a.__class__, field))):  # allow raw to handle some non-contiguous list fields
                raise NodeError(f"cannot put slice to {self.a.__class__.__name__}{f'.{field}' if field else ''}")

            with self._modifying(field):
                handler(self, code, start, stop, field, one, **options)

            return self

        except (NodeError, SyntaxError, NotImplementedError):
            if not raw:
                raise

    with self._modifying(field, True):
        return _put_slice_raw(self, code, start, stop, field, one=one, **options)


_PUT_SLICE_HANDLERS = {
    (Module, 'body'):                     _put_slice_stmtish,  # stmt*
    (Interactive, 'body'):                _put_slice_stmtish,  # stmt*
    (FunctionDef, 'body'):                _put_slice_stmtish,  # stmt*
    (AsyncFunctionDef, 'body'):           _put_slice_stmtish,  # stmt*
    (ClassDef, 'body'):                   _put_slice_stmtish,  # stmt*
    (For, 'body'):                        _put_slice_stmtish,  # stmt*
    (For, 'orelse'):                      _put_slice_stmtish,  # stmt*
    (AsyncFor, 'body'):                   _put_slice_stmtish,  # stmt*
    (AsyncFor, 'orelse'):                 _put_slice_stmtish,  # stmt*
    (While, 'body'):                      _put_slice_stmtish,  # stmt*
    (While, 'orelse'):                    _put_slice_stmtish,  # stmt*
    (If, 'body'):                         _put_slice_stmtish,  # stmt*
    (If, 'orelse'):                       _put_slice_stmtish,  # stmt*
    (With, 'body'):                       _put_slice_stmtish,  # stmt*
    (AsyncWith, 'body'):                  _put_slice_stmtish,  # stmt*
    (Try, 'body'):                        _put_slice_stmtish,  # stmt*
    (Try, 'orelse'):                      _put_slice_stmtish,  # stmt*
    (Try, 'finalbody'):                   _put_slice_stmtish,  # stmt*
    (TryStar, 'body'):                    _put_slice_stmtish,  # stmt*
    (TryStar, 'orelse'):                  _put_slice_stmtish,  # stmt*
    (TryStar, 'finalbody'):               _put_slice_stmtish,  # stmt*
    (ExceptHandler, 'body'):              _put_slice_stmtish,  # stmt*
    (match_case, 'body'):                 _put_slice_stmtish,  # stmt*

    (Match, 'cases'):                     _put_slice_stmtish,  # match_case*
    (Try, 'handlers'):                    _put_slice_stmtish,  # excepthandler*
    (TryStar, 'handlers'):                _put_slice_stmtish,  # excepthandlerstar*

    (Dict, ''):                           _put_slice_Dict,  # key:value*

    (Set, 'elts'):                        _put_slice_Set_elts,  # expr*
    (List, 'elts'):                       _put_slice_List_elts,  # expr*
    (Tuple, 'elts'):                      _put_slice_Tuple_elts,  # expr*

    (FunctionDef, 'decorator_list'):      _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (AsyncFunctionDef, 'decorator_list'): _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (ClassDef, 'decorator_list'):         _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (ClassDef, 'bases'):                  _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Delete, 'targets'):                  _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Assign, 'targets'):                  _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (BoolOp, 'values'):                   _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Compare, ''):                        _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (Call, 'args'):                       _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (comprehension, 'ifs'):               _put_slice_NOT_IMPLEMENTED_YET,  # expr*

    (ListComp, 'generators'):             _put_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (SetComp, 'generators'):              _put_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (DictComp, 'generators'):             _put_slice_NOT_IMPLEMENTED_YET,  # comprehension*
    (GeneratorExp, 'generators'):         _put_slice_NOT_IMPLEMENTED_YET,  # comprehension*

    (ClassDef, 'keywords'):               _put_slice_NOT_IMPLEMENTED_YET,  # keyword*
    (Call, 'keywords'):                   _put_slice_NOT_IMPLEMENTED_YET,  # keyword*

    (Import, 'names'):                    _put_slice_NOT_IMPLEMENTED_YET,  # alias*
    (ImportFrom, 'names'):                _put_slice_NOT_IMPLEMENTED_YET,  # alias*

    (With, 'items'):                      _put_slice_NOT_IMPLEMENTED_YET,  # withitem*
    (AsyncWith, 'items'):                 _put_slice_NOT_IMPLEMENTED_YET,  # withitem*

    (MatchSequence, 'patterns'):          _put_slice_MatchSequence_patterns,  # pattern*
    (MatchMapping, ''):                   _put_slice_MatchMapping,  # key:pattern*
    (MatchClass, 'patterns'):             _put_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchOr, 'patterns'):                _put_slice_MatchOr_patterns,  # pattern*

    (FunctionDef, 'type_params'):         _put_slice_NOT_IMPLEMENTED_YET,  # type_param*
    (AsyncFunctionDef, 'type_params'):    _put_slice_NOT_IMPLEMENTED_YET,  # type_param*
    (ClassDef, 'type_params'):            _put_slice_NOT_IMPLEMENTED_YET,  # type_param*
    (TypeAlias, 'type_params'):           _put_slice_NOT_IMPLEMENTED_YET,  # type_param*

    (Global, 'names'):                    _put_slice_NOT_IMPLEMENTED_YET,  # identifier*
    (Nonlocal, 'names'):                  _put_slice_NOT_IMPLEMENTED_YET,  # identifier*

    (JoinedStr, 'values'):                _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (TemplateStr, 'values'):              _put_slice_NOT_IMPLEMENTED_YET,  # expr*
}


# ----------------------------------------------------------------------------------------------------------------------
# put raw

def _loc_slice_raw_put(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str) -> fstloc:
    """Get location of a raw slice. Sepcial cases for decorators, comprehension ifs and other weird nodes."""

    def fixup_slice_index_for_raw(len_, start, stop):
        start, stop = _fixup_slice_indices(len_, start, stop)

        if start == stop:
            raise ValueError("invalid slice for raw operation")

        return start, stop

    ast = self.a

    if isinstance(ast, Dict):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

        start, stop = fixup_slice_index_for_raw(len(values := ast.values), start, stop)
        start_loc   = self._loc_maybe_dict_key(start, True)

        return fstloc(start_loc.ln, start_loc.col, *values[stop - 1].f.pars()[2:])

    if isinstance(ast, Compare):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Compare")

        comparators  = ast.comparators  # virtual combined body of [Compare.left] + Compare.comparators
        start, stop  = fixup_slice_index_for_raw(len(comparators) + 1, start, stop)
        stop        -= 1

        return fstloc(*(comparators[start - 1] if start else ast.left).f.pars()[:2],
                      *(comparators[stop - 1] if stop else ast.left).f.pars()[2:])

    if isinstance(ast, MatchMapping):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a MatchMapping")

        keys        = ast.keys
        start, stop = fixup_slice_index_for_raw(len(keys), start, stop)

        return fstloc(*keys[start].f.loc[:2], *ast.patterns[stop - 1].f.pars()[2:])

    if isinstance(ast, comprehension):
        ifs         = ast.ifs
        start, stop = fixup_slice_index_for_raw(len(ifs), start, stop)
        ffirst      = ifs[start].f
        start_pos   = _prev_find(self.root._lines, *ffirst._prev_bound(), ffirst.ln, ffirst.col, 'if')

        return fstloc(*start_pos, *ifs[stop - 1].f.pars()[2:])

    if isinstance(ast, (Global, Nonlocal)):
        start, stop         = fixup_slice_index_for_raw(len(ast.names), start, stop)
        start_loc, stop_loc = self._loc_global_nonlocal_names(start, stop - 1)

        return fstloc(start_loc.ln, start_loc.col, stop_loc.end_ln, stop_loc.end_col)

    if field == 'decorator_list':
        decos       = ast.decorator_list
        start, stop = fixup_slice_index_for_raw(len(decos), start, stop)
        ffirst      = decos[start].f
        start_pos   = _prev_find(self.root._lines, 0, 0, ffirst.ln, ffirst.col, '@')  # we can use '0, 0' because we know "@" starts on a newline

        return fstloc(*start_pos, *decos[stop - 1].f.pars()[2:])

    body        = getattr(ast, field)  # field must be valid by here
    start, stop = fixup_slice_index_for_raw(len(body), start, stop)

    return fstloc(*body[start].f.pars(False)[:2], *body[stop - 1].f.pars(False)[2:])


def _put_slice_raw(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
                   *, one: bool = False, **options) -> Union[Self, fst.FST, None]:  # -> Self or reparsed Self
    """Put a raw slice of child nodes to `self`."""

    if code is None:
        raise NotImplementedError('raw slice delete not implemented yet')

    if isinstance(code, AST):
        if not one:
            ast = reduce_ast(code, True)

            if isinstance(ast, Tuple):  # strip delimiters because we want CONTENTS of slice for raw put, not the slice object itself
                code = fst.FST._unparse(ast)[1 : (-2 if len(ast.elts) == 1 else -1)]  # also remove singleton Tuple trailing comma
            elif isinstance(ast, (List, Dict, Set, MatchSequence, MatchMapping)):
                code = fst.FST._unparse(ast)[1 : -1]

    elif isinstance(code, fst.FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        ast  = reduce_ast(code.a, True)
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
                if comma := _next_find(code.root._lines, (l := elts[-1].f.loc).end_ln, l.end_col, code.end_ln,
                                        code.end_col, ','):  # strip trailing comma
                    ln, col = comma

                    code._put_src(None, ln, col, ln, col + 1, False)

    self._reparse_raw(code, *_loc_slice_raw_put(self, start, stop, field))

    return self.repath()


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


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [
    '_locs_slice_seq', '_get_slice_seq', '_put_slice_seq',
    '_get_slice', '_put_slice',
    '_is_slice_compatible',
]  # used by make_docs.py
