"""Get and put slice.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

from ast import *
from typing import Any, Literal, Union

from . import fst

from .astutil import *
from .astutil import re_identifier, TypeAlias, TryStar, TemplateStr

from .misc import (
    Self, Code, NodeError, astfield, fstloc,
    re_empty_line, re_line_trailing_space, re_empty_space, re_line_end_cont_or_comment,
    _next_src, _prev_find, _next_find, _next_find_re, _fixup_slice_indices,
    _leading_trivia, _trailing_trivia,
)

from .fst_slice_old import (
    _get_slice_stmtish, _get_slice_dict, _get_slice_tuple_list_or_set,
    _put_slice_stmtish, _put_slice_dict, _put_slice_tuple_list_or_set,
)


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
# (MatchClass, 'kwd_patterns'):         # pattern*


# ----------------------------------------------------------------------------------------------------------------------

def _fixup_self_tail_sep_del(self: fst.FST, self_tail_sep: bool | Literal[0] | None, start: int, stop: int,
                             len_body: int) -> bool | Literal[0] | None:
    is_last = stop == len_body

    if self_tail_sep:
        return None if is_last else self_tail_sep  # return None if is_last or (start + (len_body - stop)) > 1 else self_tail_sep  # only adds if single element remains
    elif self_tail_sep is not None:  # is False or == 0
        return self_tail_sep if (start and is_last) else None
    elif not isinstance(self.a, Tuple):
        return 0 if (start and is_last) else None
    elif is_last:
        return 0 if start >= 2 else None
    else:
        return True if not start and stop == len_body - 1 else None


def _locs_slice_seq(self: fst.FST, is_first: bool, is_last: bool,
                    bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                    ln: int, col: int, end_ln: int, end_col: int,
                    trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None],
                    sep: str = ',', neg: bool = False,
                    ) -> tuple[fstloc, fstloc, str | None, tuple[int, int] | None]:
    r"""Slice get locations for both copy and delete after cut. Parentheses should already have been taken into account
    for the bounds and location. This function will find the separator if present and go from there for the trailing
    trivia. If trivia specifier has a `'-#'` for space in it and `neg` here is true then the copy location will not have
    extra space added but the delete location will.

    In the returned copy location, a leading newline means the slice wants to start on its own line and a trailing
    newline means the slice wants to end its own line. Both mean it wants to live on its own line.

    **Notes:** If `neg` is `True` (used for cut) and there was negative space found then the delete location will
    include the space but the copy location will not.

    **Returns:**
    - (`copy_loc`, `del_loc`, `del_indent`, `sep_end_pos`):
        - `copy_loc`: Where to copy.
        - `del_loc`: Where to remove (cut or delete or replace).
        - `del_indent`: String to put at start of `del_loc` after removal or `None` if original (`ln`, `col`) start
            location did not start its own line. Will be empty string if start location starts right at beginning of
            line.
        - `sep_end_pos`: Position right after separator `sep` if found after (`end_ln`, `end_col`), else `None`.

    ```py
    '+' = copy_loc
    '-' = del_loc
    '=' = del_loc and return indent

    ... case 0 ...........................................................
    [  GET,  ]
     ++++++++
     --------

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
    [PRE, GET,\n   [PRE, GET, # trivia\n
          ++++++         +++++++++++++++
         -------        --------------
     # trivia\n     POST]
    +++++++++++
    ---------
     POST]

    ... case 4 ...........................................................
    [PRE,\n       [PRE,\n   [PRE,\n   [PRE,\n
     GET, POST]    GET]      GET,]     GET, ]
     ++++          +++       ++++      ++++
    =-----        =---      =----     =-----

    ... case 5 ...........................................................
    [PRE,\n        [PRE,\n       [PRE,\n       [PRE,\n
         ++             ++            ++            ++
     # trivia\n     # trivia\n    # trivia\n    # trivia\n
    +++++++++++    +++++++++++   +++++++++++   +++++++++++
    -----------    -----------   -----------   -----------
     GET, POST]     GET]          GET,]         GET, ]
    +++++          ++++          +++++         +++++
    =-----         =---          =----         =-----

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

    if sep and (code := _next_src(lines, end_ln, end_col, bound_end_ln, bound_end_col)) and code.src.startswith(sep):  # if separator present then set end of element to just past it
        sep_end_pos = end_pos = (end_ln := code.ln, end_col := code.col + len(sep))

    else:
        sep_end_pos = None
        end_pos     = (end_ln, end_col)

    if is_first and is_last:
        return ((l := fstloc(bound_ln, bound_col, bound_end_ln, bound_end_col)), l, None, sep_end_pos)  # case 0

    ld_comms, ld_space, ld_neg, tr_comms, tr_space, tr_neg = fst.FST._get_trivia_params(trivia, neg)

    ld_text_pos, ld_space_pos, indent = _leading_trivia(lines, bound_ln, bound_col,
                                                        ln, col, ld_comms, ld_space)
    tr_text_pos, tr_space_pos, _      = _trailing_trivia(lines, bound_end_ln, bound_end_col,
                                                         end_ln, end_col, tr_comms, tr_space)

    def calc_locs(ld_ln: int, ld_col: int, tr_ln: int, tr_col: int):
        if indent is None:  # does not start line, no preceding trivia
            del_col = re_line_trailing_space.match(lines[ln], 0, col).start(1)

            if tr_ln == end_ln:  # does not extend past end of line (different from _trailing_trivia() 'ends_line')
                if not is_last or lines[end_ln].startswith('#', tr_col):  # if there is a next element or trailing line comment then don't delete space before this element
                    del_col = col

                return (fstloc(ln, col, end_ln, end_col),
                        fstloc(ln, del_col, end_ln, tr_col),
                        None, sep_end_pos)  # case 1

            if tr_text_pos == end_pos and tr_ln == end_ln + 1:  # no comments, maybe trailing space on line, treat as if doesn't end line
                return (fstloc(ln, col, end_ln, end_col),
                        fstloc(ln, del_col, end_ln, end_col),
                        None, sep_end_pos)  # case 2

            return (fstloc(ln, col, tr_ln, tr_col),
                    fstloc(ln, del_col, l := tr_ln - 1, len(lines[l])),
                    None, sep_end_pos)  # case 3

        assert ld_col == 0

        if tr_ln == end_ln:  # does not extend past end of line (different from _trailing_trivia() 'ends_line')
            if ld_ln == ln:  # starts on first line which is copied / deleted
                return (fstloc(ln, col, end_ln, end_col),
                        fstloc(ln, ld_col, end_ln, tr_col),
                        indent, sep_end_pos)  # case 4, we do it this way to return this specific information that it starts a line but doesn't end one

            return (fstloc((l := ld_ln - 1), len(lines[l]), end_ln, end_col) if ld_ln else fstloc(ld_ln, ld_col, end_ln, end_col),
                    fstloc(ld_ln, ld_col, end_ln, tr_col),
                    indent, sep_end_pos)  # case 5

        return (fstloc((l := ld_ln - 1), len(lines[l]), tr_ln, tr_col) if ld_ln else fstloc(ld_ln, ld_col, tr_ln, tr_col),
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


# ----------------------------------------------------------------------------------------------------------------------
# get

def _get_slice_seq(self: fst.FST, start: int, stop: int, len_body: int, cut: bool, ast: AST,
                   bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                   ln: int, col: int, end_ln: int, end_col: int,
                   trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None = None,
                   field: str = 'elts', prefix: str = '', suffix: str = '', sep: str = ',',
                   self_tail_sep: bool | Literal[0] | None = None,
                   ret_tail_sep: bool | Literal[0] | None = None,
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
    - (`bound_ln`, `bound_col`): End of previous element (past pars) or start of container (just past
        delimiters) if no previous element.
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
    - (`ln`, `col`, `end_ln`, `end_col`): Location of single or span of elements being copied or cut (including pars but
        not trailing separator).
    - `trivia`: Standard option on how to handle leading and trailing comments and space, `None` means global default.
    - `field`: Which field of is being gotten from. In the case of two-field sequences like `Dict` this should be the
        last field syntactically, `value` in the case of `Dict` and should always have valid entries and not `None`.
    - `prefix`, `suffix`: What delimiters to add to copied / cut span of elements (pars, brackets, curlies).
    - `sep`: The separator to use and check, comma for everything except maybe `'|'` for MatchOr.
    - `self_tail_sep`: Whether self needs a trailing separator after cut or no (including if end was not cut).
        - `None`: Leave it up to function (tuple singleton check or aesthetic decision).
        - `True`: Add if not present.
        - `False`: Remove from remaining sequence if tail removed but not from remaining tail if it was not removed.
        - `0`: Remove if not aesthetically significant (present on same line as end of element), otherwise leave.
    - `ret_tail_sep`: Whether returned cut or copied slice needs a trailing separator or not.
        - `None`: Figure it out from length and if `ast` is `Tuple`.
        - `True`: Always add if not present.
        - `False`: Always remove if present.
        - `0`: Remove if not aesthetically significant (present on same line as end of element), otherwise leave.
    """

    lines           = self.root._lines
    is_first        = not start
    is_last         = stop == len_body
    len_self_suffix = self.end_col - bound_end_col  # will be 1 or 0 depending on if enclosed container or unparenthesized tuple

    if ret_tail_sep is None:
        ret_tail_sep = ((stop - start) == 1 and isinstance(ast, Tuple)) or 0  # if would result in signleton tuple then will need trailing separator

    # self_tail_sep:
    #   None: Means exactly that, do nothing, no add OR delete, will always be this if cutting everything.
    #   True: Means add trailing separator to last element of what is left in self if it does not have one (implies something is left)
    #   False: Means delete trailing separator from what is left after cut (implies something is left).

    if not cut:
        self_tail_sep = None
    else:
        self_tail_sep = _fixup_self_tail_sep_del(self, self_tail_sep, start, stop, len_body)

    # get locations and adjust for trailing separator keep or delete if possible to optimize

    copy_loc, del_loc, del_indent, sep_end_pos = _locs_slice_seq(self, is_first, is_last,
        bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col, trivia, sep, cut,
    )

    copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

    if not ret_tail_sep and sep_end_pos:
        if is_last:  # if is last element and already had trailing separator then keep it
            ret_tail_sep = True  # this along with sep_end_pos != None will turn the ret_tail_sep checks below into noop

        elif sep_end_pos[0] == copy_end_ln == end_ln and sep_end_pos[1] == copy_end_col:  # optimization common case, we can get rid of unneeded trailing separator in copy by just not copying it if it is at end of copy range on same line as end of element
            copy_loc     = fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col := end_col)
            ret_tail_sep = True

    if self_tail_sep == 0:  # (or False), optimization common case, we can get rid of unneeded trailing separator in self by adding it to the delete block if del block starts on same line as previous element ends and there is not a comment on the line
        del_ln, _, del_end_ln, del_end_col = del_loc

        if del_ln == bound_ln and (del_end_ln != bound_ln or not lines[bound_ln].startswith('#', del_end_col)):
            del_loc              = fstloc(bound_ln, bound_col, del_end_ln, del_end_col)  # there can be nothing but a separator and whitespace between these locations
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
            last_end_ln, last_end_col, fst_end_ln, fst_end_col = _poss_end(fst_, field, len(suffix))

            fst_._maybe_del_separator(last_end_ln, last_end_col, ret_tail_sep is False, fst_end_ln, fst_end_col, sep)

    elif not sep_end_pos:  # need return trailing separator and don't have it
        last_end_ln, last_end_col, fst_end_ln, fst_end_col = _poss_end(fst_, field, len(suffix))

        fst_._maybe_add_comma(last_end_ln, last_end_col, False, fst_end_ln, fst_end_col)

    if self_tail_sep:  # last element needs a trailing separator (singleton tuple maybe, requested by user)
        last_end_ln, last_end_col, self_end_ln, self_end_col = _poss_end(self, field, len_self_suffix)

        self._maybe_add_comma(last_end_ln, last_end_col, False, self_end_ln, self_end_col)

    elif self_tail_sep is not None:  # removed tail element(s) and what is left doesn't need its trailing separator
        last_end_ln, last_end_col, self_end_ln, self_end_col = _poss_end(self, field, len_self_suffix)  # will work without len_self_suffix, but consistency

        self._maybe_del_separator(last_end_ln, last_end_col, self_tail_sep is False, self_end_ln, self_end_col, sep)

    return fst_


def _poss_end(self: fst.FST, field: str, len_suffix: int = 0):
    """Get position of end of self minus length of delimiter suffix and position of last element past pars, assumed to
    exist."""

    _, _, end_ln, end_col  = self.loc
    end_col               -= len_suffix

    if not isinstance(last := getattr(self.a, field)[-1], AST):  # Globals or Locals names or something like that
        return end_ln, end_col, end_ln, end_col

    _, _, last_end_ln, last_end_col = last.f.loc

    return last_end_ln, last_end_col, end_ln, end_col


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
        return self._new_empty_dict(from_=self)

    bound_ln, bound_col, bound_end_ln, bound_end_col  = self.loc
    bound_end_col                                    -= 1

    if start:
        _, _, bound_ln, bound_col = body2[start - 1].f.pars()
    else:
        bound_col += 1

    ln, col, _, _         = self._loc_maybe_dict_key(start, True)
    _, _, end_ln, end_col = body2[stop - 1].f.pars()

    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'values', cut, body, body2)
    ret_ast     = Dict(keys=asts, values=asts2)

    return _get_slice_seq(self, start, stop, len_body, cut, ret_ast,
                          bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col,
                          options.get('trivia'), 'values', '{', '}')


def _get_slice_List_elts(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                         **options) -> fst.FST:
    len_body    = len(body := (ast := self.a).elts)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return self._new_empty_list(from_=self)

    bound_ln, bound_col, bound_end_ln, bound_end_col  = self.loc
    bound_end_col                                    -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    ln, col, end_ln, end_col = body[start].f.pars()

    if (last := stop - 1) != start:
        _, _, end_ln, end_col = body[last].f.pars()

    asts    = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx     = ast.ctx.__class__
    ret_ast = List(elts=asts, ctx=ctx())

    if not issubclass(ctx, Load):  # new List root object must have ctx=Load
        set_ctx(ret_ast, Load)

    return _get_slice_seq(self, start, stop, len_body, cut, ret_ast,
                          bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col,
                          options.get('trivia'), 'elts', '[', ']')


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
        next_col     = col + len(src)
        lineno       = ln + 1

        if not i:
            bound_ln  = ln
            bound_col = col

        ret_elts.append(Name(id=src, ctx=Load(), lineno=lineno, col_offset=(l := lines[ln]).c2b(col), end_lineno=lineno,
                             end_col_offset=l.c2b(next_col)))

        col = next_col + 1  # + 1 probably skip comma

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

    (Set, 'elts'):                        _get_slice_tuple_list_or_set,  # expr*
    (List, 'elts'):                       _get_slice_List_elts,  # expr*
    (Tuple, 'elts'):                      _get_slice_tuple_list_or_set,  # expr*

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

    (MatchSequence, 'patterns'):          _get_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchMapping, ''):                   _get_slice_NOT_IMPLEMENTED_YET,  # key:pattern*
    (MatchClass, 'patterns'):             _get_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchOr, 'patterns'):                _get_slice_NOT_IMPLEMENTED_YET,  # pattern*

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

def _put_slice_seq(self: fst.FST, start: int, stop: int, len_body: int, fst_: fst.FST | None,
                   fst_first: fst.FST | fstloc | None, fst_last: fst.FST | None,
                   bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                   ln: int, col: int, end_ln: int, end_col: int,
                   trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None,
                   field: str = 'elts', field2: str | None = None, sep: str = ',',
                   self_tail_sep: bool | Literal[0] | None = None,
                   ):
    r"""Indent a sequence source and put it to a location in existing sequence `self`. If `fst_` is `None` then will
    just delete in the same way that a cut operation would. Trailing separators will be added  / removed as needed and
    according to if they are in normal positions. If delete from `self` leaves an empty unparenthesized tuple then
    parentheses will NOT be added here.

    If an empty slice was going to be put we expect that it will be converted to a put `None` delete of existing
    elements. If an `fst_` is provided then it is assumed it has at least one element. No empty put to empty location,
    likewise no delete from empty location.

    **Parameters:**
    - `start`, `stop`, `len_body`: Slice parameters, `len_body` being current length of field.
    - `fst_`: The slice being put to `self` with delimiters stripped, or `None` for delete.
    - `fst_first`: The first element of the slice `FST` being put, or `None` if delete. Can be an `fstloc` for
        two-element slices (dict `**`, or even for a normal element (pars included)).
    - `fst_last`: The last element of the slice `FST` being put, or `None` if delete.
    - (`bound_ln`, `bound_col`): End of previous element (past pars) or start of container (just past
        delimiters) if no previous element.
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
    - (`ln`, `col`, `end_ln`, `end_col`): Location of single or span of elements being replaced or deleted (including
        pars but not trailing separator). If pure insertion then `ln` and `col` are not used and (`end_ln`, `end_col`)
        is the start position of the `stop` element in `self` if there is one, otherwise same as bound end.
    - `trivia`: Standard option on how to handle leading and trailing comments and space, `None` means global default.
    - `field`: Which field of `self` is being deleted / replaced / inserted to.
    - `field2`: If `self` is a two element sequence like `Dict` or `MatchMapping` then this should be the second field
        of each element, `values` or `patterns`.
    - `sep`: The separator to use and check, comma for everything except maybe `'|'` for MatchOr.
    - `self_tail_sep`: Whether self needs a trailing separator or no.
        - `None`: Leave it up to function (tuple singleton check or aesthetic decision).
        - `True`: Always add if not present.
        - `False`: Always remove if present.
        - `0`: Remove if not aesthetically significant (present on same line as end of element), otherwise leave.
    """

    lines           = self.root._lines
    is_first        = not start
    is_last         = stop == len_body
    is_del          = fst_ is None
    is_ins          = start == stop  # will never be true if fst_ is None
    body            = getattr(self.a, field)
    body2           = body if field2 is None else getattr(self.a, field2)
    last            = None  # means body[-1]
    len_self_suffix = self.end_col - bound_end_col  # will be 1 or 0 depending on if enclosed container or unparenthesized tuple
    self_indent     = self.get_indent()

    if is_ins:  # insert, figure out location


        # TODO: ln / pos option to specify line where should insert


        if not is_last:  # just before next element
            ln  = end_ln
            col = end_col

        elif not is_first:  # just past previous element
            ln  = end_ln  = bound_ln
            col = end_col = bound_col

        else:  # whole area
            ln  = bound_ln
            col = bound_col

    copy_loc, del_loc, del_indent, _ = _locs_slice_seq(self, is_first, is_last,
        bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col, trivia, sep, is_del,
    )

    put_ln, put_col, put_end_ln, put_end_col = del_loc

    # delete

    if is_del:
        put_lines     = [del_indent] if del_indent else None
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
        post_indent = None

        if re_line_end_cont_or_comment.match(put_lines[l := len(put_lines) - 1],  # if last line of fst_ is a comment or line continuation without a newline then add one
                                             0 if l > fst_last.end_ln else fst_last.end_col).group(1):
            put_lines.append(bistr(''))

        # newlines and indentation

        if fst_starts_nl :=  not put_lines[0]:  # slice to put start with pure newline?
            if not put_col:  # start element being put to starts a new line?
                skip = 0

                fst_._put_src(None, 0, 0, 1, 0, False)  # delete leading pure newline in slice being put

            else:  # does not start a new line
                put_col = re_line_trailing_space.match(lines[put_ln], 0,  put_col).start(1)  # eat whitespace before put newline

        elif not put_col:
            fst_._put_src(del_indent, 0, 0, 0, 0, False)  # add indent to start of first put line, this del_indent will not be indented by self_indent because of skip == 1

        else:  # leave the space between previous separator and self intact
            assert put_ln == copy_ln

            put_col = copy_col

        if not put_lines[-1]:  # slice put ends with pure newline?
            if not re_empty_space.match(lines[put_end_ln], put_end_col):  # something at end of put end line?
                if put_end_col:  # put doesn't end exactly on a brand new line so there is stuff to indent on line
                    if is_last and put_end_ln == self.end_ln:  # just the end of the container, put at same indent as open
                        post_indent = self_indent + ' ' * (self.col - len(self_indent))
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

            else:  # nothing (or whitespace) at end of put end line, remove fst_ trailing newline to not duplicate and remove trailing space from self if present
                fst_._put_src(None, l := len(put_lines) - 2, len(put_lines[l]), l + 1, 0, True)

                if put_end_col != (ec := len(lines[put_end_ln])):
                    self._put_src(None, put_end_ln, put_end_col, put_end_ln, ec, True)

        # trailing separator

        if is_last:
            last = fst_last

            if self_tail_sep is None:
                if isinstance(self.a, Tuple) and is_first and fst_last is fst_first:  # if single element overwriting all elements of a tuple then make sure has trailing separator
                    self_tail_sep = True

                elif pos := _next_find(put_lines, fst_last.end_ln, fst_last.end_col, fst_.end_ln, fst_.end_col, sep):  # only remove if slice being put actually has trailing separator
                    if re_empty_space.match(put_lines[pos[0]], pos[1] + len(sep)):  # which doesn't have stuff following it
                        self_tail_sep = 0

        elif self_tail_sep == 0:  # don't remove from tail if tail not touched
            self_tail_sep = None

        # indent and offset source to put

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

    # trailing and internal separator

    if self_tail_sep is not None:  # trailing
        _, _, last_end_ln, last_end_col  = (last or body2[-1].f).loc
        _, _, self_end_ln, self_end_col  = self.loc
        self_end_col                    -= len_self_suffix

        if self_tail_sep:
            self._maybe_add_comma(last_end_ln, last_end_col, False, self_end_ln, self_end_col)
        else:
            self._maybe_del_separator(last_end_ln, last_end_col, self_tail_sep is False, self_end_ln, self_end_col, sep)

    if not is_del:  # internal
        if not is_last:  # past the newly put slice
            stop_ln, stop_col, _, _ = self._loc_maybe_dict_key(stop, False, body)

            self._maybe_add_comma(fst_last.end_ln, fst_last.end_col, True, stop_ln, stop_col, False)  # last False is because elements of self are now past comma point so will need to be offset

        elif is_ins and not is_first:  # before newly appended slice at end
            _, _, stop_end_ln, stop_end_col = body2[stop - 1].f.loc
            len_stop_end_line               = len(lines[stop_end_ln])

            if not fst_first.is_FST:  # special case, has to be None dict key, don't like this is messy
                fst_first = fst_._loc_maybe_dict_key(0)

            if self._maybe_add_comma(stop_end_ln, stop_end_col, True, fst_first.ln, fst_first.col) is not False:  # if line changed (separator and / or space) then we need to explicitly offset the fst_ elements as well since they don't live in self yet but in fst_
                fst_._offset(stop_end_ln, stop_end_col, 0, len(lines[stop_end_ln]) - len_stop_end_line)


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

            loc = start_prev_loc

        else:
            loc = fstloc(-1, -1, -1, -1)  # dummy

        for i in range(start, len(body)):  # now search forward
            if (loc := self._loc_maybe_dict_key(i, True, body)).ln != body2[i - 1].f.pars().end_ln:  # only consider elements which start on a different line than the previous element ends on
                if re_empty_line.match(l := lines[loc.ln], 0, loc.col):
                    return l[:loc.col]

    return None


def _code_as_seq(self: fst.FST, code: Code | None, one: bool, options: dict[str, Any]) -> fst.FST | None:
    if code is None:
        return None

    fst_ = self._code_as_expr(code, self.root.parse_params)

    if one:
        if (b := fst_.is_parenthesized_tuple()) is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
            fst_._parenthesize_node()
        elif b is None and precedence_require_parens(fst_.a, self.a, 'elts', 0) and not fst_.pars().n:
            fst_._parenthesize_grouping()

        ls  = fst_._lines
        ast = Set(elts=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls), end_col_offset=ls[-1].lenbytes)  # because in this case all we need is the `elts` container (without `ctx`)

        return fst.FST(ast, ls, from_=self, lcopy=False)

    if empty_set := self.get_option('empty_set', options):
        if ((fst_.is_empty_set_seq() or fst_.is_empty_set_call()) if empty_set is True else
            fst_.is_empty_set_seq() if empty_set == 'seq' else fst_.is_empty_set_call()  # else 'call'
        ):
            return None

    ast_ = fst_.a

    if not isinstance(ast_, (Tuple, List, Set)):
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} "
                        f"must be a Tuple, List or Set, not a {ast_.__class__.__name__}")

    if not ast_.elts:  # put empty sequence is same as delete
        return None

    fst_._sanitize()

    if fst_.is_parenthesized_tuple() is not False:  # strip enclosing parentheses, brackets or curlies from List, Set or parenthesized Tuple
        fst_.a.end_col_offset -= 1
        fst_lines              = fst_._lines

        fst_._offset(0, 1, 0, -1)  # guaranteed to start here because of _sanitize()

        fst_lines[-1] = bistr(fst_lines[-1][:-1])
        fst_lines[0]  = bistr(fst_lines[0][1:])

    return fst_


def _code_as_seq2(self: fst.FST, code: Code | None, one: bool, options: dict[str, Any]) -> fst.FST | None:
    if code is None:
        return None

    if one:
        raise ValueError(f'cannot put a single item to a {self.a.__class__.__name__} slice')

    fst_ = self._code_as_expr(code, self.root.parse_params)
    ast_ = fst_.a

    if ast_.__class__ is not self.a.__class__:
        raise ValueError(f"slice being assigned to a {self.a.__class__.__name__} must be a {self.a.__class__.__name__}"
                         f", not a {ast_.__class__.__name__}")

    if not ast_.keys:  # put empty sequence is same as delete
        return None

    fst_._sanitize()

    fst_.a.end_col_offset -= 1
    fst_lines              = fst_._lines

    fst_._offset(0, 1, 0, -1)  # guaranteed to start here because of _sanitize()

    fst_lines[-1] = bistr(fst_lines[-1][:-1])
    fst_lines[0]  = bistr(fst_lines[0][1:])

    return fst_


def _locs_put_seq(self, start: int, stop: int, body: list[AST]) -> tuple[int, int, int, int, int, int, int, int]:
    bound_ln, bound_col, bound_end_ln, bound_end_col  = self.loc
    bound_end_col                                    -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    if start != stop:
        ln, col, end_ln, end_col = body[start].f.pars()

        if start != stop - 1:
            _, _, end_ln, end_col = body[stop - 1].f.pars()

    else:
        ln = col = -1

        if stop < len(body):
            end_ln, end_col, _, _ = body[stop].f.pars()

        else:
            end_ln  = bound_end_ln
            end_col = bound_end_col

    return bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col


def _locs_put_seq2(self, start: int, stop: int, body: list[AST], body2: list[AST],
                   ) -> tuple[int, int, int, int, int, int, int, int]:
    bound_ln, bound_col, bound_end_ln, bound_end_col  = self.loc
    bound_end_col                                    -= 1

    if start:
        _, _, bound_ln, bound_col = body2[start - 1].f.pars()
    else:
        bound_col += 1

    if start != stop:
        ln, col, _, _         = self._loc_maybe_dict_key(start, True, body)
        _, _, end_ln, end_col = body2[stop - 1].f.pars()

    else:
        ln = col = -1

        if stop < len(body):
            end_ln, end_col, _, _ = self._loc_maybe_dict_key(stop, True, body)

        else:
            end_ln  = bound_end_ln
            end_col = bound_end_col

    return bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col


# ......................................................................................................................

def _put_slice_NOT_IMPLEMENTED_YET(self: fst.FST, code: Code | None, start: int | Literal['end'] | None,
                                   stop: int | None, field: str, one: bool = False, **options,
                                   ):
    raise NotImplementedError("not implemented yet, try with option raw='auto'")


def _put_slice_Dict(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                    field: str, one: bool = False, **options):
    fst_        = _code_as_seq2(self, code, one, options)
    len_body    = len(body := (ast := self.a).keys)
    body2       = ast.values
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if not fst_ and start == stop:  # deleting or assigning empty seq to empty slice of seq, noop
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col = _locs_put_seq2(
        self, start, stop, body, body2)

    if not fst_:
        _put_slice_seq(self, start, stop, len_body, None, None, None,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       ln, col, end_ln, end_col, options.get('trivia'), 'keys', 'values')

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])

        del body[start : stop]
        del body2[start : stop]

        len_fst_body = 0

    else:
        ast_      = fst_.a
        fst_body  = ast_.keys
        fst_body2 = ast_.values
        fst_first = a.f if (a := fst_body[0]) else fst_._loc_maybe_dict_key(0)

        _put_slice_seq(self, start, stop, len_body, fst_, fst_first, fst_body2[-1].f,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       ln, col, end_ln, end_col, options.get('trivia'), 'keys', 'values')

        self._unmake_fst_tree(body[start : stop] + body2[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop]  = fst_body
        body2[start : stop] = fst_body2

        len_fst_body = len(fst_body)
        stack        = []

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


def _put_slice_List_elts(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                         field: str, one: bool = False, **options):
    fst_        = _code_as_seq(self, code, one, options)
    len_body    = len(body := (ast := self.a).elts)
    start, stop = _fixup_slice_indices(len_body, start, stop)

    if not fst_ and start == stop:  # deleting or assigning empty seq to empty slice of seq, noop
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col = _locs_put_seq(self, start, stop, body)

    if not fst_:
        _put_slice_seq(self, start, stop, len_body, None, None, None,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       ln, col, end_ln, end_col, options.get('trivia'))

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        fst_body = fst_.a.elts

        _put_slice_seq(self, start, stop, len_body, fst_, fst_body[0].f, fst_body[-1].f,
                       bound_ln, bound_col, bound_end_ln, bound_end_col,
                       ln, col, end_ln, end_col, options.get('trivia'))

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        len_fst_body = len(fst_body)
        FST          = fst.FST
        stack        = [FST(body[i], self, astfield('elts', i)) for i in range(start, start + len_fst_body)]

        if stack:
            set_ctx([f.a for f in stack], ast.ctx.__class__)

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield('elts', i)


# ......................................................................................................................

def _put_slice(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
               one: bool = False, **options) -> Union[Self, fst.FST, None]:  # -> Self or reparsed Self or could disappear due to raw
    """Put an a slice of child nodes to `self`."""

    if code is self.root:  # don't allow own root to be put to self
        raise NodeError('circular put detected')

    raw = fst.FST.get_option('raw', options)

    if options.get('to') is not None:
        raise ValueError(f"cannot put slice with 'to'")

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

    (Set, 'elts'):                        _put_slice_tuple_list_or_set,  # expr*
    (List, 'elts'):                       _put_slice_List_elts,  # expr*
    (Tuple, 'elts'):                      _put_slice_tuple_list_or_set,  # expr*

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

    (MatchSequence, 'patterns'):          _put_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchMapping, ''):                   _put_slice_NOT_IMPLEMENTED_YET,  # key:pattern*
    (MatchClass, 'patterns'):             _put_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchOr, 'patterns'):                _put_slice_NOT_IMPLEMENTED_YET,  # pattern*

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
            raise ValueError(f"invalid slice for raw operation")

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
        start_loc, stop_loc = self._loc_Global_Nonlocal_names(start, stop - 1)

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
                if isinstance(ast, MatchSequence) and not fst_._is_parenthesized_seq('patterns'):
                    fst_._parenthesize_grouping()

            elif is_par_tup is False:
                fst_._parenthesize_node()

        elif ((is_dict := isinstance(ast, Dict)) or
                (is_match := isinstance(ast, (MatchSequence, MatchMapping))) or
                isinstance(ast, (Tuple, List, Set))
        ):
            if not ((is_par_tup := fst_.is_parenthesized_tuple()) is False or  # don't strip nonexistent delimiters if is unparenthesized Tuple or MatchSequence
                    (is_par_tup is None and isinstance(ast, MatchSequence) and
                        not fst_._is_parenthesized_seq('patterns'))
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
    # (MatchOr, 'patterns'):                'pattern*',
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
