"""Low level get and put slice expression-ish slices."""

# TODO: High level. On first create it was assumed the simpler needs and interface of `get_slice_sep()` compared with
# `put_slice_sep()` would make things easier for slice gets. It did, but since the work had do be done for
# `put_slice_sep()` anyway should make the interface and location getting and everything consistent with that.

from __future__ import annotations

import re
from typing import Any, Callable, Literal, Mapping

from . import fst

from .asttypes import AST
from .astutil import bistr

from .common import (
    re_empty_line_start,
    re_empty_line,
    re_empty_space,
    re_line_end_cont_or_comment,
    fstloc,
    next_frag,
    next_find,
)

from .fst_core import _ParamsOffset
from .fst_misc import leading_trivia, trailing_trivia, get_trivia_params

__all__ = [
    'get_slice_sep', 'put_slice_sep_begin', 'put_slice_sep_end',
    'get_slice_nosep', 'put_slice_nosep',
]


_LocFunc = Callable[[list[AST], int], fstloc]  # location function for child with first param being container (of ASTs which belong to FSTs) and second index in that container, e.g. Dict.keys[idx] (because can be `**`) or comprehension.ifs which includes the `if`

_re_open_delim_or_space = re.compile(r'[({\s[]')  # this is a special set of delimiter openers which are considered to not need an aesthetic space after
_re_close_delim_or_space_or_end = re.compile(r'[)}\s\]:]|$')  # this is a special set of terminations which are considered to not need an aesthetic space before if a slice put ends with a non-space right before them

# _re_sep_starts = {  # match separator at start of fragment, needs to be a pattern to recognize 'and\b' and 'or\b' so they are not recognized as part of an identifier like 'origin'
#     ',':   re.compile(r','),
#     '|':   re.compile(r'\|'),  # this doesn't need a check against '|='
#     '=':   re.compile(r'='),  # this doesn't need a check against '=='
#     'and': re.compile(r'and\b'),
#     'or':  re.compile(r'or\b'),
# }

_re_sep_line_nonexpr_end = {  # empty line with optional separator and line continuation or a pure comment line
    ',':   re.compile(r'\s*  (?:,\s*)?    (?:\\|\#.*)?  $', re.VERBOSE),
    '|':   re.compile(r'\s*  (?:\|\s*)?   (?:\\|\#.*)?  $', re.VERBOSE),
    '=':   re.compile(r'\s*  (?:=\s*)?    (?:\\|\#.*)?  $', re.VERBOSE),
    # 'and': re.compile(r'\s*  (?:and\s*)?  (?:\\|\#.*)?  $', re.VERBOSE),
    # 'or':  re.compile(r'\s*  (?:or\s*)?   (?:\\|\#.*)?  $', re.VERBOSE),
    '':    re.compile(r'\s*               (?:\\|\#.*)?  $', re.VERBOSE),
}

_shorter = lambda a, b: a if len(a) < len(b) else b


# ----------------------------------------------------------------------------------------------------------------------

def _locs_first_and_last(
    self: fst.FST, start: int, stop: int, body: list[AST], body2: list[AST], locfunc: _LocFunc | None = None,
) -> tuple[fstloc, fstloc]:
    """Get the location of the first and last elemnts of a one or two-element sequence (assumed present)."""

    stop_1 = stop - 1

    if body2 is body:
        if locfunc:
            loc_first = locfunc(body, start)
            loc_last = loc_first if start == stop_1 else locfunc(body, stop_1)

        else:
            loc_first = body[start].f.pars()
            loc_last = loc_first if start == stop_1 else body[stop_1].f.pars()

    else:
        ln, col, _, _ = self._loc_maybe_key(start, True, body, body2)
        _, _, end_ln, end_col = body2[start].f.pars()
        loc_first = fstloc(ln, col, end_ln, end_col)

        if start == stop_1:
            loc_last = loc_first

        else:
            ln, col, _, _ = self._loc_maybe_key(stop_1, True, body, body2)
            _, _, end_ln, end_col = body2[stop_1].f.pars()
            loc_last = fstloc(ln, col, end_ln, end_col)

    return loc_first, loc_last


def _fixup_self_tail_sep_del(
    self: fst.FST, self_tail_sep: bool | Literal[0, 1] | None, start: int, stop: int, len_body: int
) -> bool | Literal[0, 1] | None:
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


def _get_element_indent(self: fst.FST, body: list[AST], body2: list[AST], start: int, locfunc: _LocFunc) -> str | None:
    """Get first exprish element indentation found for an element which starts its own line. The FULL indentation, not
    the element indentation with respect to container indentation. We just return the indentation of one element instead
    of trying to figure out which indent is used most for both performance and were-just-not-gonna-deal-with-that-crap
    reasons.

    **Parameters:**
    - `start`: The index of the element to start the search with (closest to area we want to indent).
    - `locfunc`: MUST be passed as either original `_LocFunc` or a lambda which evaluates to `body[idx].f.pars()`. Only
        used for one-element sequence.

    **Returns:**
    - `str`: Indent found.
    - `None`: No explicit indent found.
    """

    lines = self.root._lines

    if body is body2:  # single element sequence
        if start >= 1:  # first search backward for an element which starts its own line (if there are elements before)
            loc = start_prev_loc = locfunc(body, start - 1)

            for i in range(start - 2, -1, -1):
                if (prev_loc := locfunc(body, i)).end_ln != loc.ln:  # only consider elements which start on a different line than the previous element ends on
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

            if (loc := locfunc(body, i)).ln != prev_loc.end_ln:  # only consider elements which start on a different line than the previous element ends on
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

    else:  # two-element sequence (Dict, MatchMapping)
        if start >= 1:  # first search backward for an element which starts its own line (if there are elements before)
            for i in range(start - 2, -1, -1):
                if (loc := self._loc_maybe_key(i + 1, True, body)).ln != body2[i].f.pars().end_ln:  # only consider elements which start on a different line than the previous element ends on
                    if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                        return l[:loc.col]

            if (loc := self._loc_maybe_key(0, True, body)).ln != self.ln:  # only consider element 0 if it is not on same line as self starts
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

        else:
            # loc = fstloc(-1, -1, -1, -1)  # dummy, will force pattern check for element 0 because there could be anything before it
            ln, col, _, _ = self.loc
            loc = fstloc(-1, -1, ln, col)  # so we don't get indent of special first element if on same line as self starts (probably unindented intentionally)

        for i in range(start, len(body)):  # now search forward
            prev_loc = loc

            if (loc := self._loc_maybe_key(i, True, body)).ln != prev_loc.end_ln:  # only consider elements which start on a different line than the previous element ends on
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

            prev_loc = body2[i].f.pars()

    return None


def _offset_pos_by_params(
    self: fst.FST, ln: int, col: int, col_offset: int, params_offset: _ParamsOffset
) -> tuple[int, int]:
    """Position to offset `(ln, col)` with `col_offset` = `lines[ln].c2b(col)`, is assumed to be at or past the offset
    position."""

    at_ln = params_offset.ln == ln
    ln += params_offset.dln

    if at_ln:
        col = self.root._lines[ln].b2c(col_offset + params_offset.dcol_offset)

    return ln, col


def _locs_slice(
    lines: list[str],
    is_first: bool,
    is_last: bool,
    loc_first: fstloc,
    loc_last: fstloc,
    bound_ln: int,
    bound_col: int,
    bound_end_ln: int,
    bound_end_col: int,
    trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None],
    sep: str = ',',
    neg: bool = False,
) -> tuple[fstloc, fstloc, str | None, tuple[int, int] | None]:
    r"""Slice locations for both copy and delete. Parentheses should already have been taken into account for the bounds
    and location. This function will find the separator if present and go from there for the trailing trivia. If trivia
    specifier has a `'-#'` for space in it and `neg` here is `True` then the copy location will not have extra space
    added but the delete location will.

    In the returned copy location, a leading newline means the slice wants to start on its own line and a trailing
    newline means the slice wants to end its own line. Both mean it wants to live on its own line.

    **Notes:** If `neg` is `True` and there was negative space found then the delete location will include the space but
    the copy location will not.

    **Parameters:**
    - `lines`: Lines of source (e.g. `f.root._lines`).
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

    ```
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

    single = loc_last is loc_first

    first_ln, first_col, last_end_ln, last_end_col = loc_first

    if not single:
        _, _, last_end_ln, last_end_col = loc_last

    if (sep
        and (frag := next_frag(lines, last_end_ln, last_end_col, bound_end_ln, bound_end_col))
        and frag.src.startswith(sep)  # _re_sep_starts[sep].match(frag.src)
    ):  # if separator present then set end of element to just past it
        last_end_ln = frag.ln
        last_end_col = frag.col + len(sep)
        sep_end_pos = end_pos = (last_end_ln, last_end_col)

    else:
        sep_end_pos = None
        end_pos = (last_end_ln, last_end_col)

    # if is_first and is_last:
    #     return ((l := fstloc(bound_ln, bound_col, bound_end_ln, bound_end_col)), l, None, sep_end_pos)  # case 0

    ld_comms, ld_space, ld_neg, tr_comms, tr_space, tr_neg = get_trivia_params(trivia, neg)

    ld_text_pos, ld_space_pos, indent = leading_trivia(lines, bound_ln, bound_col,  # start of text / space
                                                       first_ln, first_col, ld_comms, ld_space)
    tr_text_pos, tr_space_pos, _ = trailing_trivia(lines, bound_end_ln, bound_end_col,  # END of text / space
                                                   last_end_ln, last_end_col, tr_comms, tr_space)

    def calc_locs(
        ld_ln: int, ld_col: int, tr_ln: int, tr_col: int
    ) -> tuple[fstloc, fstloc, str | None, tuple[int, int] | None]:  # (copy_loc, del_loc, indent, sep_end_pos)
        if indent is None:  # does not start line, no preceding trivia
            del_col = re_empty_space.search(lines[first_ln], 0 if first_ln > bound_ln else bound_col, first_col).start()

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

    if ld_different := (ld_space_pos and ld_neg and ld_space):
        if ld_text_pos[0] == ld_ln:  # if on same line then space was at start of line and there should be no difference
            ld_different = False

        else:
            ld_ln = ld_text_pos[0]  # this is where space would have been without negative
            ld_col = 0

    if tr_different := (tr_space_pos and tr_neg and tr_space):
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


# ----------------------------------------------------------------------------------------------------------------------
# get and put with separator (most slices)

def get_slice_sep(
    self: fst.FST,
    start: int,
    stop: int,
    len_body: int,
    cut: bool,
    ast: AST,
    ast_last: AST | None,
    loc_first: fstloc,
    loc_last: fstloc,
    bound_ln: int,
    bound_col: int,
    bound_end_ln: int,
    bound_end_col: int,
    options: Mapping[str, Any],
    field: str = 'elts',
    prefix: str = '',
    suffix: str = '',
    sep: str = ',',
    self_tail_sep: bool | Literal[0, 1] | None = None,
    ret_tail_sep: bool | Literal[0, 1] | None = None,
) -> fst.FST:
    """Copy slice sequence source, dedent it, and create a new `FST` from that source and the new `AST` already made
    with the old locations (which will be updated). If the operation is a cut then the source in `self` will also be
    deleted.

    If doing with separators then trailing separators will be added / removed as needed and according to if they are in
    normal positions. If cut from `self` leaves an empty unparenthesized tuple then parentheses will NOT be added here.

    **Note:** Will NOT remove existing trailing separator from `self` sequence if it is not touched even if
    `self_tail_sep=False`.

    **WARNING!** (`bound_ln`, `bound_col`) is expected to be exactly the end of the previous element (past any closing
    pars) or the start of the container (past any opening delimiters) if no previous element. (`bound_end_ln`,
    `bound_end_col`) must be end of container just before closing delimiters.

    **Parameters:**
    - `start`, `stop`, `len_body`: Slice parameters, `len_body` being current length of field.
    - `ast`: The already built new `AST` that is being gotten. The elements being gotten must be in this with their
        current locations in the `self`. The insides of this are not accessed, just the location is set.
    - `ast_last`: The `AST` of the last element copied or cut, not assumend to have `.f` `FST` attribute to begin with.
        Can be `None` if not doing separators.
    - `loc_first`: The full location of the first element copied or cut, parentheses included.
    - `loc_last`: The full location of the last element copied or cut, parentheses included. Must be `is` identical to
        `loc_first` if they are the same element.
    - (`bound_ln`, `bound_col`): End of previous element (past pars) or start of container (just past
        delimiters) if no previous element. DIFFERENT FROM put_slice_sep_begin()!!!
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters). This can be past last element of
        sequence if there are other things which follow and look like part of the sequence (like a `rest` in a
        `MatchMapping`).
    - `options`: The dictionary of options passed to the put function. Options used are `trivia`.
    - `field`: Which field of is being gotten from. In the case of two-field sequences like `Dict` this should be the
        last field syntactically, `value` in the case of `Dict` and should always have valid entries and not `None`.
    - `prefix`, `suffix`: What delimiters to add to copied / cut span of elements (pars, brackets, curlies).
    - `sep`: The separator to use and check, comma for everything except maybe `'|'` for MatchOr. If this is false
        (empty string) then no separator stuff is done and `ast_last`, `field`, `self_tail_sep` and `ret_tail_sep` are
        not used.
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

    if sep:
        if ret_tail_sep and ret_tail_sep is not True and (stop - start) != 1:  # if ret_tail_sel == 1 and length will not be 1 then remove
            ret_tail_sep = 0

        if not cut:
            self_tail_sep = None
        else:
            self_tail_sep = _fixup_self_tail_sep_del(self, self_tail_sep, start, stop, len_body)

    # get locations and adjust for trailing separator keep or delete if possible to optimize

    copy_loc, del_loc, del_indent, sep_end_pos = _locs_slice(lines, is_first, is_last, loc_first, loc_last,
                                                             bound_ln, bound_col, bound_end_ln, bound_end_col,
                                                             options.get('trivia'), sep, cut)

    copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

    if sep:
        if not ret_tail_sep and sep_end_pos:
            if is_last and ret_tail_sep is not False:  # if is last element and already had trailing separator then keep it but not if explicitly forcing no tail sep
                ret_tail_sep = True  # this along with sep_end_pos != None will turn the ret_tail_sep checks below into noop

            elif sep_end_pos[0] == copy_end_ln == loc_last.end_ln and sep_end_pos[1] == copy_end_col:  # optimization common case, we can get rid of unneeded trailing separator in copy by just not copying it if it is at end of copy range on same line as end of element
                copy_end_col = loc_last.end_col
                copy_loc = fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col)
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

    fst_, params_offset = self._make_fst_and_dedent(self, ast, copy_loc, prefix, suffix,
                                                    del_loc if cut else None,
                                                    [del_indent] if del_indent and del_loc.end_col else None,
                                                    docstr=False)  # docstr False because none of the things handled by this function can have any form of docstring

    ast.col_offset = 0  # before prefix
    ast.end_col_offset = fst_._lines[-1].lenbytes  # after suffix

    fst_._touch()

    # add / remove trailing separators as needed

    if sep:
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
                                                                params_offset)

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


def put_slice_sep_begin(  # **WARNING!** Here there be dragons! TODO: this really needs a refactor
    self: fst.FST,
    start: int,
    stop: int,
    fst_: fst.FST | None,
    fst_first: fst.FST | None,
    fst_last: fst.FST | None,
    len_fst: int,
    bound_ln: int,
    bound_col: int,
    bound_end_ln: int,
    bound_end_col: int,
    options: Mapping[str, Any],
    field: str = 'elts',
    field2: str | None = None,
    sep: str = ',',
    self_tail_sep: bool | Literal[0, 1] | None = None,
    locfunc: _LocFunc | None = None,
    allow_redent: bool = True,
) -> tuple:
    r"""Indent a sequence source and put it to a location in existing sequence `self`. If `fst_` is `None` then will
    just delete in the same way that a cut operation would.

    If doing with separators then trailing separators will be added / removed as needed and according to if they are in
    normal positions, but not in this function, in `put_slice_sep_end()`. If delete from `self` leaves an empty
    unparenthesized tuple then parentheses will NOT be added here.

    If an empty slice was going to be put we expect that it will be converted to a put `None` delete of existing
    elements. If an `fst_` is provided then it is assumed it has at least one element. No empty put to empty location,
    likewise no delete from empty location.

    This is the first in a two function sequence if doing with separators. After a call to this the source will be
    mostly put (except for maybe tail separator changes). The `AST` nodes being modified should be modified between this
    call and a call to `put_slice_sep_end()`. If not doing separators then the `put_slice_sep_end()` should not be
    called.

    **Parameters:**
    - `start`, `stop`: Slice parameters.
    - `fst_`: The slice being put to `self` with delimiters stripped, or `None` for delete.
    - `fst_first`: The first element of the slice `FST` being put, or `None` if delete or possibly is an actual `None`
        value because is a `**` key in a `Dict`.
    - `fst_last`: The last element of the slice `FST` being put, or `None` if delete.
    - `len_fst`: Number of elements in `FST` being put, or 0 if delete.
    - (`bound_ln`, `bound_col`): Start of container (just past delimiters). DIFFERENT FROM get_slice_sep()!!!
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
    - `options`: The dictionary of options passed to the put function. Options used are `trivia` and `ins_ln`.
    - `field`: Which field of `self` is being deleted / replaced / inserted to.
    - `field2`: If `self` is a two element sequence like `Dict` or `MatchMapping` then this should be the second field
        of each element, `values` or `patterns`.
    - `sep`: The separator to use and check, comma for everything except maybe `'|'` for MatchOr. If this is false
        (empty string) then no separator stuff is done and `len_fst` and `self_tail_sep` are not used.
    - `self_tail_sep`: Whether self needs a trailing separator or no.
        - `None`: Leave it up to function (tuple singleton check or aesthetic decision).
        - `True`: Always add if not present.
        - `False`: Always remove if present.
        - `1`: Add if not present and single element.
        - `0`: Remove if not aesthetically significant (present on same line as end of element), otherwise leave.
    - `locfunc`: Location function ONLY for single-element non-`sep` sequence. Used to provide full location for
        elements of `comprehension.ifs` to include the leading `if` which is not part of the expression location. If
        `None` then standard location is used.
    - `allow_redent`: Whether to allow re-indentation of multiline elements to current indentation of multiline elements
        or another indentation level if that cannot be determined. Meant to allow avoid redent for decorators.
    **Returns:**
    - `param`: A parameter to be passed to `put_slice_sep_end(param)` to finish the put.
    """

    def get_indent_elts() -> str:
        nonlocal elts_indent_cached

        if elts_indent_cached is not ...:
            return elts_indent_cached

        if (elts_indent_cached := _get_element_indent(self, body, body2, start, locfunc)) is not None:
            pass  # noop
        elif body:  # match indentation of our own first element
            elts_indent_cached = self_indent + ' ' * (locfunc_maybe_key(body, 0).col - len(self_indent))  # (self._loc_maybe_key(0, True, body).col - len(self_indent))
        else:
            elts_indent_cached = self_indent + root.indent  # default

        return elts_indent_cached

    trivia = options.get('trivia')  # finalized with global option in lower level functions
    ins_ln = fst.FST.get_option('ins_ln', options)
    root = self.root
    lines = root._lines
    body = getattr(self.a, field)
    body2 = body if field2 is None else getattr(self.a, field2)
    len_body = len(body)
    is_first = not start
    is_last = stop == len_body
    is_del = fst_ is None
    is_ins = start == stop  # will never be true if fst_ is None
    is_ins_ln = False
    self_indent = self._get_indent()
    elts_indent_cached = ...  # cached value, ... means not present
    bound_end_col_offset = lines[bound_end_ln].c2b(bound_end_col)

    if locfunc:
        locfunc_maybe_key = locfunc  # locfunc will never be provided for a two-element sequence so no keys means loc_maybe_key is just normal locfunc
    else:
        locfunc = lambda body, idx: body[idx].f.pars()
        locfunc_maybe_key = lambda body, idx: self._loc_maybe_key(idx, True, body)

    # maybe redent fst_ elements to match self element indentation

    if not is_del and len(fst_._lines) > 1 and allow_redent:
        if (elts_indent := get_indent_elts()) is not None:  # we only do this if we have concrete indentation for elements of self
            ast_ = fst_.a
            fst_indent = _get_element_indent(fst_,
                                             getattr(ast_, fst_first.pfield.name if fst_first else 'keys'),
                                             getattr(ast_, fst_last.pfield.name),
                                             0, locfunc)

            fst_._redent_lns(fst_indent or '', elts_indent[len(self_indent):], docstr=False)  # docstr False because none of the things handled by this function can have any form of docstring  # fst_._dedent_lns(fst_indent or ''), fst_._indent_lns(elts_indent[len(self_indent):])

    # locations

    if not is_first:  # if not first then bound start is at end of previous element
        _, _, bound_ln, bound_col = body2[start - 1].f.pars()  # we don't use locfunc(body2, start - 1) because currenly that only returns a different BEGINNING location and end_ln and end_col are same as this

    if not is_ins:  # replace or delete, location is element span
        loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body2, locfunc)

    else:  # insert, figure out location, TODO: the `ins_ln` part is still under constrnction
        if ins_ln is not None:  # if an explicit insert line is passed then set insert location according to that
            if ins_ln <= bound_ln:
                loc_first = fstloc(bound_ln, bound_col, bound_ln, bound_col)

            else:
                if not is_last:
                    ln, col, _, _ = locfunc_maybe_key(body, stop)  # self._loc_maybe_key(stop, True, body)

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
            ln, col, _, _ = locfunc_maybe_key(body, stop)  # self._loc_maybe_key(stop, True, body)
            loc_first = fstloc(ln, col, ln, col)

        else:  # just past previous element or at start of bound
            loc_first = fstloc(bound_ln, bound_col, bound_ln, bound_col)

        loc_last = loc_first

    copy_loc, del_loc, del_indent, _ = _locs_slice(lines, is_first, is_last, loc_first, loc_last,
                                                   bound_ln, bound_col, bound_end_ln, bound_end_col,
                                                   trivia, sep, True)  # is_del)

    put_ln, put_col, put_end_ln, put_end_col = del_loc

    # delete

    if is_del:
        put_lines = [del_indent] if del_indent and put_end_col else None

        if sep:
            self_tail_sep = _fixup_self_tail_sep_del(self, self_tail_sep, start, stop, len_body)

            if self_tail_sep == 0:  # (or False), optimization, we can get rid of unneeded trailing separator in self by adding it to the delete block if del block starts on same line as previous element ends and there is not a comment on the line
                if put_ln == bound_ln and (put_end_ln != bound_ln or not lines[bound_ln].startswith('#', put_end_col)):
                    put_ln = bound_ln  # there can be nothing but a separator and whitespace between these locations
                    put_col = bound_col
                    self_tail_sep = None

    # insert or replace, this is the bit that deals with tricky leading and trailing newlines and indentation

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
                put_col = re_empty_space.search(lines[put_ln], 0 if put_ln > bound_ln else bound_col, put_col).start()  # eat whitespace before put newline

        elif not put_col:  # slice being put to start of new line
            if del_indent:
                fst_._put_src(del_indent, 0, 0, 0, 0, False)  # add indent to start of first put line, this del_indent will not be indented by self_indent because of skip == 1

        else:
            assert put_ln == copy_ln

            put_col = copy_col  # maybe leave the space between previous separator or element and self intact

            if not sep and not _re_open_delim_or_space.match(lines[put_ln], put_col - 1):  # if not doing separator and immediately follows non-space-non-delimiter open there will be no end pass to separate these if there is no space between these so we need to insert space here
                fst_._put_src(' ', 0, 0, 0, 0, False)

        if not put_lines[-1]:  # slice put ends with pure newline?
            line_put_end = lines[put_end_ln]

            if not re_empty_space.match(line_put_end, put_end_col):  # something at end of put end line?
                if put_end_col:  # put doesn't end exactly on a brand new line so there is stuff to indent on line that's going to the next line
                    if is_last and put_end_ln == self.end_ln:  # just the end of the container, smaller of start of its line or open indent
                        post_indent = _shorter(re_empty_line_start.match(line_put_end).group(0),
                                               self_indent + ' ' * (self.col - len(self_indent)))
                    elif is_ins_ln and not (put_col or put_end_ln != put_ln):  # don't insert to zero-length location at exact start of line
                        put_end_col = copy_loc.end_col
                    elif del_indent is not None:  # have indent from locs function
                        post_indent = del_indent
                    else:
                        post_indent = get_indent_elts()

            elif put_end_ln < bound_end_ln:  # nothing (or whitespace) at end of put end line, only do this if we are not at end line of container
                if put_end_col or not re_empty_space.match(line_put_end):  # end of put not start of next line or next line not empty
                    fst_._put_src(None, l := len(put_lines) - 2, len(put_lines[l]), l + 1, 0, True)  # remove fst_ trailing newline to not duplicate and remove trailing space from self if present

                    if put_end_col != (ec := len(line_put_end)):
                        self._put_src(None, put_end_ln, put_end_col, put_end_ln, ec, True)

        elif not put_end_col and (put_col or put_end_ln != put_ln):  # we are putting slice before an element which starts a newline and slice doesn't have trailing newline (but not insert to zero-length location at exact start of line)
            if put_end_ln != put_ln:  # change put end to not delete last newline if possible
                put_end_ln = put_end_ln - 1
                put_end_col = len(lines[put_end_ln])

            else:  # otherwise add newline to slice
                put_lines.append(bistr(''))  # this doesn't need to be post_indent-ed because its just a newline, doesn't do indentation of following text

        elif (
            not put_lines[-1][-1].isspace()  # putting something that ends with non-space to something that starts with not a closing delimiter or space, put space between
            and not _re_close_delim_or_space_or_end.match(lines[put_end_ln], put_end_col)
            and (put_end_ln < self.end_ln or put_end_col < self.end_col)  # but not at the very end of self
        ):
            put_lines[-1] = bistr(put_lines[-1] + ' ')

        # trailing separator

        if sep:
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

        fst_._indent_lns(self_indent, skip=skip, docstr=False)
        fst_._offset(0, 0, put_ln, lines[put_ln].c2b(put_col))

        if post_indent:  # we do this here like this because otherwise a completely empty line at the end of fst_ will not be indented at all in _indent_lns() which we may need to add self_indent alone
            put_lines[-1] = bistr(post_indent)

    # put source

    self_ln, self_col, self_end_ln, self_end_col = self.loc

    is_last_and_at_self_end = is_last and ((self_end_ln < put_end_ln) or
                                           (self_end_ln == put_end_ln and self_end_col <= put_end_col))

    if put_col == self_col and put_ln == self_ln:  # put at beginning of unenclosed sequence
        offset_head = self._is_any_parent_format_spec_start_pos(put_end_ln, put_end_col)  # if also putting at end of sequence then may need to offset with head=True if FormattedValue/Interpolation .format_spec starts at exactly same position as put ends

        params_offset = self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, is_last, offset_head, self)

        self._offset(*params_offset, True, True, self_=False)

    elif is_last_and_at_self_end:  # because of insertion at end and maybe unenclosed sequence
        params_offset = self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, True, self)
    else:  # in this case there may parts of self after so we need to recurse the offset into self
        params_offset = self._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, False)

    # parameters for put / del trailing and internal separators, we return explicitly so that the ASTs can be modified so the next part doesn't get too screwy

    return (start, len_fst, body, body2, sep, self_tail_sep, bound_end_ln, bound_end_col, bound_end_col_offset,
            params_offset, is_last, is_del, is_ins)


def put_slice_sep_end(self: fst.FST, params: tuple) -> None:
    """Finish up sequence slice put with separators. `AST` nodes are assumed to have been modified by here and general
    structure of `self` is correct, even if it is not parsable due to separators in source not being correct yet. Should
    not be called for slices which do not use separators.

    **WARNING:** `locfunc` is not used here because currently it only applies to non-`sep` sequences.
    """

    (start, len_fst, body, body2, sep, self_tail_sep, bound_end_ln, bound_end_col, bound_end_col_offset, params_offset,
     is_last, is_del, is_ins) = params

    if self_tail_sep is not None:  # trailing separator
        last = body2[-1].f

        _, _, last_end_ln, last_end_col = last.loc
        bound_end_ln, bound_end_col = _offset_pos_by_params(self, bound_end_ln, bound_end_col,
                                                            bound_end_col_offset, params_offset)

        if self_tail_sep:
            self._maybe_ins_separator(last_end_ln, last_end_col, False, bound_end_ln, bound_end_col, sep, last)
        else:
            self._maybe_del_separator(last_end_ln, last_end_col, self_tail_sep is False, bound_end_ln, bound_end_col,
                                      sep)

    if not is_del:  # internal separator
        new_stop = start + len_fst

        if not is_last:  # past the newly put slice
            put_last = body2[new_stop - 1].f

            _, _, put_last_end_ln, put_last_end_col = put_last.loc
            new_stop_ln, new_stop_col, _, _ = self._loc_maybe_key(new_stop, True, body, body2).loc

            self._maybe_ins_separator(put_last_end_ln, put_last_end_col, True, new_stop_ln, new_stop_col, sep, put_last)

        if is_ins and start:  # between self split (last element of first part) or end and new slice following it
            self_split = body2[start - 1].f

            _, _, self_split_end_ln, self_split_end_col = self_split.loc
            put_first_ln, put_first_col, _, _ = self._loc_maybe_key(start, True, body, body2).loc

            self._maybe_ins_separator(self_split_end_ln, self_split_end_col, True, put_first_ln, put_first_col, sep,
                                      self_split)

            return self


# ----------------------------------------------------------------------------------------------------------------------
# get and put without separator (comprehension, comprehension.ifs, decorator_list)

def get_slice_nosep(
    self: fst.FST,
    start: int,
    stop: int,
    len_body: int,
    cut: bool,
    ast: AST,
    loc_first: fstloc,
    loc_last: fstloc,
    bound_ln: int,
    bound_col: int,
    bound_end_ln: int,
    bound_end_col: int,
    options: Mapping[str, Any],
) -> fst.FST:
    """Copy slice sequence source without separators, dedent it, and create a new `FST` from that source and the new
    `AST` already made with the old locations (which will be updated). If the operation is a cut then the source in
    `self` will also be deleted.

    **WARNING!** (`bound_ln`, `bound_col`) is expected to be exactly the end of the previous element (past any closing
    pars), "previous element" including element which is not part of this entire slice (`ListComp.elt`,
    `comprehension.iter`). (`bound_end_ln`, `bound_end_col`) must be end of container just before closing delimiters or
    end of last element of this possible slice area if there is another non-slice element following (before the space).

    **Parameters:**
    - `start`, `stop`, `len_body`: Slice parameters, `len_body` being current length of field.
    - `ast`: The already built new `AST` that is being gotten. The elements being gotten must be in this with their
        current locations in the `self`.
    - `loc_first`: The full location of the first element copied or cut, parentheses and possible prefix included.
    - `loc_last`: The full location of the last element copied or cut, parentheses and possible prefix included.
    - (`bound_ln`, `bound_col`): End of previous element (past pars, even if not part of this sequence, e.g.
        `ListComp.elt`, `comprehension.iter` for `comprehension.ifs` sequence). DIFFERENT FROM put_slice_nosep()!!!
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters) or just before space before next
        element which is not part of this sequence.
    - `options`: The dictionary of options passed to the put function. Options used are `trivia`.
    """

    return get_slice_sep(self, start, stop, len_body, cut, ast, None, loc_first, loc_last,
                         bound_ln, bound_col, bound_end_ln, bound_end_col, options, '', '', '', '', None, None)


def put_slice_nosep(
    self: fst.FST,
    start: int,
    stop: int,
    fst_: fst.FST | None,
    fst_first: fst.FST | None,
    fst_last: fst.FST | None,
    bound_ln: int,
    bound_col: int,
    bound_end_ln: int,
    bound_end_col: int,
    options: Mapping[str, Any],
    field: str,
    locfunc: _LocFunc | None = None,
    allow_redent: bool = True,
) -> None:
    r"""Indent a sequence source without separators and put it to a location in existing sequence `self`. If `fst_` is
    `None` then will just delete in the same way that a cut operation would.

    If an empty slice was going to be put we expect that it will be converted to a put `None` delete of existing
    elements. If an `fst_` is provided then it is assumed it has at least one element. No empty put to empty location,
    likewise no delete from empty location.

    **Parameters:**
    - `start`, `stop`: Slice parameters.
    - `fst_`: The slice being put to `self` with delimiters stripped, or `None` for delete.
    - `fst_first`: The first element of the slice `FST` being put, or `None` if delete.
    - `fst_last`: The last element of the slice `FST` being put, or `None` if delete.
    - (`bound_ln`, `bound_col`): End of previous element which is not part of this sequence (past pars, e.g.
        `ListComp.elt` for `comprehension` sequence, `comprehension.iter` for `comprehension.ifs`). DIFFERENT FROM
        get_slice_nosep()!!!
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
    - `options`: The dictionary of options passed to the put function. Options used are `trivia` and `ins_ln`.
    - `field`: Which field of `self` is being deleted / replaced / inserted to.
    - `locfunc`: Location function ONLY for single-element non-`sep` sequence. Used to provide full location for
        elements of `comprehension.ifs` to include the leading `if` which is not part of the expression location. If
        `None` then standard location is used.
    - `allow_redent`: Whether to allow re-indentation of multiline elements to current indentation of multiline elements
        or another indentation level if that cannot be determined. Meant to allow avoid redent for decorators.
    """

    put_slice_sep_begin(self, start, stop, fst_, fst_first, fst_last, -1,
                        bound_ln, bound_col, bound_end_ln, bound_end_col, options, field, None, '', None,
                        locfunc, allow_redent)
