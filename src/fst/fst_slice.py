"""Get and put slice.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

from ast import *
from typing import Literal, Union

from . import fst

from .astutil import *
from .astutil import TypeAlias, TryStar, TemplateStr

from .misc import (
    Self, Code, NodeError, fstloc,
    _prev_find, _next_find, _fixup_slice_indices,
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
# N ,             (ClassDef, 'bases'):                    # expr*            -> Tuple                  _parse_expr_callargs
# N ,             (Delete, 'targets'):                    # expr*            -> Tuple[target]          _parse_expr / restrict targets
# N ,             (Assign, 'targets'):                    # expr*            -> Tuple[target]          _parse_expr / restrict targets
# N ,             (Call, 'args'):                         # expr*            -> Tuple[expr_callarg]    _parse_expr_callargs
#                                                                            .
# N ,     []      (MatchSequence, 'patterns'):            # pattern*         -> MatchSequence          _parse_pattern / restrict MatchSequence
# N ,     {}      (MatchMapping, 'keys':'patterns'):      # expr:pattern*    -> MatchMapping           _parse_pattern / restrict MatchMapping
#                                                                            .
# N |             (MatchOr, 'patterns'):                  # pattern*         -> MatchOr                _parse_pattern / restrict MatchOr
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
# S ,             (With, 'items'):                        # withitem*        -> Tuple[withitem]        _parse_withitems
# S ,             (AsyncWith, 'items'):                   # withitem*        -> Tuple[withitem]        _parse_withitems
#                                                                            .
# S ,             (Import, 'names'):                      # alias*           -> Tuple[alias]           _parse_aliases_dotted
# S ,             (ImportFrom, 'names'):                  # alias*           -> Tuple[alias]           _parse_aliases_star
#                                                                            .
#                                                                            .
#                                                                            .
# N ,             (Global, 'names'):                      # identifier*,     -> Tuple[Name]            _parse_expr / restrict Names
# N ,             (Nonlocal, 'names'):                    # identifier*,     -> Tuple[Name]            _parse_expr / restrict Names
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
#                 (JoinedStr, 'values'):                  # expr*
#                 (TemplateStr, 'values'):                # expr*


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

    (Dict, ''):                           'key:value*',

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
    # (MatchMapping, ''):                   'key:pattern*',
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


def _slice_seq_locs(self: fst.FST, cut: bool,
                    trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None, as_put: bool,
                    ) -> tuple[fstloc, fstloc | None, list[str] | None]:  # (copy_loc, put_loc, put_lines)
    pass




# ----------------------------------------------------------------------------------------------------------------------
# get

def _get_slice_NOT_IMPLEMENTED_YET(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                   cut: bool, **options) -> fst.FST:
    raise NotImplementedError('this is not implemented yet')


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
    (List, 'elts'):                       _get_slice_tuple_list_or_set,  # expr*
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

def _raw_slice_loc(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str) -> fstloc:
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

    self._reparse_raw(code, *_raw_slice_loc(self, start, stop, field))

    return self.repath()


# ......................................................................................................................

def _put_slice_NOT_IMPLEMENTED_YET(self: fst.FST, code: Code | None, start: int | Literal['end'] | None,
                                   stop: int | None, field: str, one: bool = False, **options,
                                   ) -> Union[Self, fst.FST, None]:
    raise NotImplementedError("not implemented yet, try with option raw='auto'")


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
__all_private__ = ['_is_slice_compatible', '_get_slice', '_put_slice']  # used by make_docs.py
