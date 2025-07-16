"""Get and put slice.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

from ast import *
from typing import Literal, Union

from . import fst

from .astutil import *
from .astutil import re_identifier, TypeAlias, TryStar, TemplateStr

from .misc import (
    Self, Code, NodeError, astfield, fstloc,
    re_line_trailing_space,
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
# N ,             (ClassDef, 'bases'):                    # expr*            -> Tuple[expr_callarg]    _parse_expr_callargs
# N ,             (Call, 'args'):                         # expr*            -> Tuple[expr_callarg]    _parse_expr_callargs
#
# N ,             (Delete, 'targets'):                    # expr*            -> Tuple[target]          _parse_expr / restrict targets
# N ,             (Assign, 'targets'):                    # expr*            -> Tuple[target]          _parse_expr / restrict targets
#                                                                            .
# S ,             (MatchClass, 'patterns'):               # pattern*         -> Tuple[pattern]         _parse_pattern / restrict MatchSequence
#                                                                            .
#                                                                            .
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
# N ,             (Global, 'names'):                      # identifier*,     -> Tuple[Name]            _parse_expr / restrict Names   - no trailing commas, unparenthesized
# N ,             (Nonlocal, 'names'):                    # identifier*,     -> Tuple[Name]            _parse_expr / restrict Names   - no trailing commas, unparenthesized
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

@staticmethod
def _is_slice_compatible(sig1: tuple[type[AST], str], sig2: tuple[type[AST], str]) -> bool:  # sig = (AST type, field)
    """Whether slices are compatible between these type / fields."""

    return ((v := _SLICE_COMAPTIBILITY.get(sig1)) == _SLICE_COMAPTIBILITY.get(sig2) and v is not None)


# ----------------------------------------------------------------------------------------------------------------------
# get

def _locs_slice_seq_get(self: fst.FST, is_first: bool, is_last: bool,
                        bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                        ln: int, col: int, end_ln: int, end_col: int,
                        trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None,
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
    -------
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

            return (fstloc(ld_ln, ld_col, end_ln, end_col),
                    fstloc(ld_ln, ld_col, end_ln, tr_col),
                    indent, sep_end_pos)  # case 5

        return (fstloc((l := ld_ln - 1), len(lines[l]), tr_ln, tr_col) if ld_ln else fstloc(ld_ln, ld_col, tr_ln, tr_col),
                fstloc(ld_ln, ld_col, tr_ln, tr_col),
                None, sep_end_pos)  # case 6

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


def _get_slice_seq_sep_and_dedent(self: fst.FST, start: int, stop: int, len_: int, cut: bool, ast: AST,
                                  bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                                  ln: int, col: int, end_ln: int, end_col: int,
                                  trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None,
                                  field: str = 'elts', prefix: str = '', suffix: str = '', sep: str = ',',
                                  self_tail_sep: bool | Literal[0] | None = None,
                                  ret_tail_sep: bool | Literal[0] | None = None,
                                  ) -> fst.FST:
    """Copy slice comma sequence source, dedent it, and create a new `FST` from that source and the new `AST` already
    made with the old locations (which will be updated). If the operation is a cut then the source in `self` will also
    be deleted. Trailing separators will be added / removed as needed and according to if they are in normal positions.
    If cut from `self` leaves an empty unparenthesized tuple then parentheses will NOT be added here.

    **WARNING!** (`bound_ln`, `bound_col`) is expected to be exactly the end of the previous element (past any closing
    pars) or the start of the container (past any opening delimiters) if no previous element.
    (`bound_end_ln`, `bound_end_col`) must be end of container just before closing delimiters.

    **Parameters:**
    - (`bound_ln`, `bound_col`): End of previous element (past pars) or start of container (just past
        delimiters) if no previous element.
    - (`bound_end_ln`, `bound_end_col`): End of container (just before delimiters).
    - (`ln`, `col`, `end_ln`, `end_col`): Location of single or span of elements being copied or cut (including pars).
    - `trivia`: Standard option on how to handle leading and trailing comments and space.
    - `prefix`, `suffix`: What delimiters to add to copied / cut span of elements (pars, brackets, curlies).
    - `sep`: The separator to use and check, comma for everything except maybe `'|'` for MatchOr.
    - `self_tail_sep`: Whether self needs a trailing separator after cut or no (including if end was not cut).
        - `None`: Leave it up to function (aesthetic decision).
        - `True`: Always add if not present.
        - `False`: Always remove if present.
        - `0`: Remove if present on same line as end of element, otherwise leave, aesthetic misc.
    - `ret_tail_sep`: Whether returned cut or copied slice needs a trailing separator or not.
        - `None`: Figure it out from length and if `ast` is `Tuple`.
        - `True`: Always add if not present.
        - `False`: Always remove if present.
        - `0`: Remove if present on same line as end of element, otherwise leave, aesthetic misc.
    """

    lines           = self.root._lines
    is_first        = not start
    is_last         = stop == len_
    len_self_suffix = self.end_col - bound_end_col  # will be 1 or 0 depending on if enclosed container or unparenthesized tuple

    if ret_tail_sep is None:
        ret_tail_sep = ((stop - start) == 1 and isinstance(ast, Tuple)) or 0  # if would result in signleton tuple then will need trailing separator

    # action_self_sep:
    #   None: Means exactly that, do nothing, no add OR delete, will always be this if cutting everything.
    #   True: Means delete trailing separator from what is left after cut (implies something is left).
    #   False: Means add trailing separator to last element of what is left in self if it does not have one (implies something is left)

    if not cut:
        action_self_tail_sep = None
    elif self_tail_sep:
        action_self_tail_sep = False if not is_last else None
    elif self_tail_sep is not None:  # is False:
        action_self_tail_sep = True if start else None
    elif not isinstance(self.a, Tuple):
        action_self_tail_sep = (start and is_last) or None
    elif is_last:
        action_self_tail_sep = start >= 2 or None
    else:
        action_self_tail_sep = False if is_first and stop == len_ - 1 else None

    # get locations and adjust for trailing separator keep or delete if possible to optimize

    copy_loc, del_loc, del_indent, sep_end_pos = _locs_slice_seq_get(self, is_first, is_last,
        bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col, trivia, sep, cut,
    )

    copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

    if not ret_tail_sep and sep_end_pos:
        if is_last:  # if is last element and already had trailing separator then keep it
            ret_tail_sep = True  # this along with sep_end_pos != None will turn the ret_tail_sep checks below into noop

        elif sep_end_pos[0] == copy_end_ln == end_ln and sep_end_pos[1] == copy_end_col:  # optimization, we can get rid of unneeded trailing separator in copy by just not copying it if it is at end of copy range on same line as end of element
            copy_loc     = fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col := end_col)
            ret_tail_sep = True

    if action_self_tail_sep:
        del_ln, _, del_end_ln, del_end_col = del_loc

        if del_ln == bound_ln and (del_end_ln != bound_ln or not lines[bound_ln].startswith('#', del_end_col)):  # optimization, we can get rid of unneeded trailing separator in self by adding it to the delete block if del block starts on same line as previous element ends and there is not a comment on the line
            del_loc              = fstloc(bound_ln, bound_col, del_end_ln, del_end_col)  # there can be nothing but a separator and whitespace between these locations
            action_self_tail_sep = None

    # set location of root node and make the actual FST

    ast.lineno         = copy_ln + 1
    ast.col_offset     = lines[copy_ln].c2b(copy_col)
    ast.end_lineno     = copy_end_ln + 1
    ast.end_col_offset = lines[copy_end_ln].c2b(copy_end_col)

    fst_ = self._make_fst_and_dedent(self, ast, copy_loc, prefix, suffix,
                                     del_loc if cut else None, del_indent and [del_indent])

    ast.col_offset     = 0  # before prefix
    ast.end_col_offset = fst_._lines[-1].lenbytes  # after suffix

    fst_._touch()

    # add / remove trailing separators as needed

    def get_end_locs(fst_: fst.FST, pars: bool, end_col_off: int = 0):
        _, _, fst_end_ln, fst_end_col  = fst_.loc
        fst_end_col                   -= end_col_off

        if not isinstance(last := getattr(fst_.a, field)[-1], AST):  # Globals or Locals names or something like that
            return fst_end_ln, fst_end_col, fst_end_ln, fst_end_col

        _, _, last_end_ln, last_end_col = last.f.pars() if pars else last.f.loc

        return last_end_ln, last_end_col, fst_end_ln, fst_end_col

    if not ret_tail_sep:
        if sep_end_pos:
            if sep_end_pos[0] == end_ln:  # must be on end line to allow aesthetic removal, otherwise considered "artisanal" separator and left in place
                last_end_ln, last_end_col, fst_end_ln, fst_end_col = get_end_locs(fst_, True, len(suffix))

                if ret_tail_sep is False:  # this deletes separator even if there is a comment following it
                    if fst_end_ln != last_end_ln:  # if not this then there can only be separator and whitespace between end of last element and end of element container
                        fst_end_col = sep_end_pos[1] + (last_end_col - end_col)  # use delta between original and copied last element as offset for separator end position in origianl code to copied position due to dedent and copy offset

                    fst_._put_src(None, last_end_ln, last_end_col, last_end_ln, fst_end_col, True)

                elif fst_end_ln == last_end_ln:  # if same line then there can only be separator and whitespace between end of last element and end of element container
                    fst_._put_src(None, last_end_ln, last_end_col, last_end_ln, fst_end_col, True)

                else:
                    del_end_col = sep_end_pos[1] + (last_end_col - end_col)  # use delta between original and copied last element as offset for separator end position in origianl code to copied position due to dedent and copy offset
                    fst_lines   = fst_._lines

                    if not _next_src(fst_lines, last_end_ln, del_end_col, last_end_ln, 0x7fffffffffffffff, True, True):  # if anything (comment) on line after separator then don't delete separator
                        fst_._put_src(None, last_end_ln, last_end_col, last_end_ln, len(fst_lines[last_end_ln]), True)

            elif ret_tail_sep is False:  # forcing removal of separator not on same line as end of element
                last_end_ln, last_end_col, fst_end_ln, fst_end_col = get_end_locs(fst_, True, len(suffix))

                if ((code := _next_src(fst_._lines, last_end_ln, last_end_col, fst_end_ln, fst_end_col)) and  # search for separator on any line and delete if found
                    code.src.startswith(sep)
                ):
                    cln, ccol, _ = code

                    fst_._put_src(None, cln, ccol, cln, ccol + len(sep), True)  # currently we just delete it but there may be more aesthetic things that can be done

    elif not sep_end_pos:  # ret_tail_sep and don't have it
        last_end_ln, last_end_col, fst_end_ln, fst_end_col = get_end_locs(fst_, False, len(suffix))

        fst_._maybe_add_comma(last_end_ln, last_end_col, False, False, fst_end_ln, fst_end_col)

    if action_self_tail_sep is False:  # last element needs a trailing separator (singleton tuple maybe, requested by user)
        last_end_ln, last_end_col, fst_end_ln, fst_end_col = get_end_locs(self, False, len_self_suffix)

        self._maybe_add_comma(last_end_ln, last_end_col, False, False, fst_end_ln, fst_end_col)

    elif action_self_tail_sep:  # removed tail element(s) and what is left doesn't need its trailing separator
        last_end_ln, last_end_col, self_end_ln, self_end_col = get_end_locs(self, True, len_self_suffix)  # will work without len_self_suffix, but consistency

        same_end_col = self_end_col if self_end_ln == last_end_ln else 0x7fffffffffffffff

        if ((code := _next_src(lines, last_end_ln, last_end_col, last_end_ln, same_end_col)) and  # separator present on line?
              code.src.startswith(sep)
        ):
            del_end_col = code.col + len(sep)

            if self_tail_sep is False:  # force delete? could be None, but not True
                if ((code := _next_src(lines, last_end_ln, del_end_col, last_end_ln, same_end_col)) and  # if comment after separator then don't delete space between separator and comment
                    not code.src.startswith('#')
                ):
                    del_end_col = code.col

                self._put_src(None, last_end_ln, last_end_col, last_end_ln, del_end_col, True)

            else:
                if code := _next_src(lines, last_end_ln, del_end_col, last_end_ln, same_end_col, True, True):  # if comment after separator then don't delete separator
                    del_end_col = code.col

                if not code or not code.src.startswith('#'):
                    self._put_src(None, last_end_ln, last_end_col, last_end_ln, del_end_col, True)

        elif self_tail_sep is False:  # force delete of separator not on same line as end of element
            if ((code := _next_src(lines, last_end_ln, last_end_col, self_end_ln, self_end_col)) and  # search for separator on any line and delete if found
                code.src.startswith(sep)
            ):
                cln, ccol, _ = code

                self._put_src(None, cln, ccol, cln, ccol + len(sep), True)  # currently we just delete it but there may be more aesthetic things that can be done

    return fst_


def _cut_or_copy_asts(start: int, stop: int, field: str, cut: bool, body: list[AST]) -> list[AST]:
    if not cut:
        asts = [copy_ast(body[i]) for i in range(start, stop)]

    else:
        asts = body[start : stop]

        del body[start : stop]

        for i in range(start, len(body)):
            body[i].f.pfield = astfield(field, i)

    return asts


# ......................................................................................................................

def _get_slice_NOT_IMPLEMENTED_YET(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                   cut: bool, **options) -> fst.FST:
    raise NotImplementedError('this is not implemented yet')


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

    asts    = _cut_or_copy_asts(start, stop, field, cut, body)
    ctx     = ast.ctx.__class__
    ret_ast = List(elts=asts, ctx=ctx())

    if not issubclass(ctx, Load):  # new List root object must have ctx=Load
        set_ctx(ret_ast, Load)

    return _get_slice_seq_sep_and_dedent(self, start, stop, len_body, cut, ret_ast,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col,
                                         fst.FST.get_option('trivia', options), 'elts', '[', ']')


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

    asts    = _cut_or_copy_asts(start, stop, field, cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    return _get_slice_seq_sep_and_dedent(self, start, stop, len_body, cut, ret_ast,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col,
                                         fst.FST.get_option('trivia', options), 'names', '', '', ',', False, False)


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

    return _get_slice_seq_sep_and_dedent(self, start, stop, len_body, cut, ret_ast,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col, ln, col, end_ln, end_col,
                                         fst.FST.get_option('trivia', options), 'names', '', '', ',', False, False)


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

    (Dict, ''):                           _get_slice_dict,  # key:value*

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

def _loc_slice_seq_put(self: fst.FST, fst_: fst.FST, is_first: bool, is_last: bool,
                       bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                       ln: int, col: int, end_ln: int, end_col: int,
                       trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None,
                       sep: str = ',', neg: bool = False,
                       ) -> fstloc:
    pass



# def _put_slice_seq_and_indent(self: fst.FST, put_fst: fst.FST | None, seq_loc: fstloc,
#                               ffirst: fst.FST | fstloc | None, flast: fst.FST | fstloc | None,
#                               fpre: fst.FST | fstloc | None, fpost: fst.FST | fstloc | None,
#                               pfirst: fst.FST | fstloc | None, plast: fst.FST | fstloc | None,
#                               docstr: bool | Literal['strict']) -> fst.FST:
#     root = self.root

#     if not put_fst:  # delete
#         # put_ln, put_col, put_end_ln, put_end_col = (
#         #     _src_edit.put_slice_seq(self, None, '', seq_loc, ffirst, flast, fpre, fpost, None, None))
#         _, (put_ln, put_col, put_end_ln, put_end_col), _ = (
#             _src_edit.get_slice_seq(self, True, seq_loc, ffirst, flast, fpre, fpost))

#         put_lines = None

#     else:  # replace or insert
#         assert put_fst.is_root

#         indent = self.get_indent()

#         put_fst._indent_lns(indent, docstr=docstr)

#         put_ln, put_col, put_end_ln, put_end_col = (
#             _src_edit.put_slice_seq(self, put_fst, indent, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast))

#         lines           = root._lines
#         put_lines       = put_fst._lines
#         fst_dcol_offset = lines[put_ln].c2b(put_col)

#         put_fst._offset(0, 0, put_ln, fst_dcol_offset)

#     self_ln, self_col, _, _ = self.loc

#     if put_col == self_col and put_ln == self_ln:  # unenclosed sequence
#         self._offset(
#             *root._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, not fpost, False, self),
#             True, True, self_=False)

#     elif fpost:
#         root._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, False)
#     else:
#         root._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, True, self)  # because of insertion at end and unparenthesized tuple


# ......................................................................................................................

def _put_slice_NOT_IMPLEMENTED_YET(self: fst.FST, code: Code | None, start: int | Literal['end'] | None,
                                   stop: int | None, field: str, one: bool = False, **options,
                                   ) -> Union[Self, fst.FST, None]:
    raise NotImplementedError("not implemented yet, try with option raw='auto'")


def _put_slice_List_elts(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                         field: str, one: bool = False, **options) -> Union[Self, fst.FST, None]:
    pass


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

    (Dict, ''):                           _put_slice_dict,  # key:value*

    (Set, 'elts'):                        _put_slice_tuple_list_or_set,  # expr*
    (List, 'elts'):                       _put_slice_tuple_list_or_set,  # expr*
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

        if stop == start:
            raise ValueError(f"invalid slice for raw operation")

        return start, stop

    ast = self.a

    if isinstance(ast, Dict):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

        keys        = ast.keys
        values      = ast.values
        start, stop = fixup_slice_index_for_raw(len(keys), start, stop)
        start_loc   = self._dict_key_or_mock_loc(keys[start], values[start].f)

        if start_loc.is_FST:
            start_loc = start_loc.pars()

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
__all_private__ = [
    '_is_slice_compatible', '_slice_seq_locs_get',
    '_get_slice', '_put_slice',
]  # used by make_docs.py
