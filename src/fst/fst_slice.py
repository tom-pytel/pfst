"""Get and put slice."""

from __future__ import annotations

from ast import *
from typing import Literal, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, TemplateStr

from .misc import (
    Self, STMTISH_OR_STMTMOD, STMTISH_FIELDS, Code, NodeError, fstloc,
    _prev_find, _next_find, _fixup_slice_indices, _coerce_ast,
)


# ----------------------------------------------------------------------------------------------------------------------

@staticmethod
def _is_slice_compatible(sig1: tuple[type[AST], str], sig2: tuple[type[AST], str]) -> bool:  # sig = (AST type, field)
    """Whether slices are compatible between these type / fields."""

    return ((v := _SLICE_COMAPTIBILITY.get(sig1)) == _SLICE_COMAPTIBILITY.get(sig2) and
            v is not None)


_SLICE_COMAPTIBILITY = {
    (Module, 'body'):                     'stmt*',
    (Interactive, 'body'):                'stmt*',
    # (FunctionDef, 'decorator_list'):      'expr*',
    # (FunctionDef, 'type_params'):         'type_param*',
    (FunctionDef, 'body'):                'stmt*',
    # (AsyncFunctionDef, 'decorator_list'): 'expr*',
    # (AsyncFunctionDef, 'type_params'):    'type_param*',
    (AsyncFunctionDef, 'body'):           'stmt*',
    # (ClassDef, 'decorator_list'):         'expr*',
    # (ClassDef, 'type_params'):            'type_param*',
    # (ClassDef, 'bases'):                  'expr*',
    # (ClassDef, 'keywords'):               'keyword*',
    (ClassDef, 'body'):                   'stmt*',
    # (Delete, 'targets'):                  'expr*',
    # (Assign, 'targets'):                  'expr*',
    # (TypeAlias, 'type_params'):           'type_param*',
    (For, 'body'):                        'stmt*',
    (For, 'orelse'):                      'stmt*',
    (AsyncFor, 'body'):                   'stmt*',
    (AsyncFor, 'orelse'):                 'stmt*',
    (While, 'body'):                      'stmt*',
    (While, 'orelse'):                    'stmt*',
    (If, 'body'):                         'stmt*',
    (If, 'orelse'):                       'stmt*',
    # (With, 'items'):                      'withitem*',
    (With, 'body'):                       'stmt*',
    # (AsyncWith, 'items'):                 'withitem*',
    (AsyncWith, 'body'):                  'stmt*',
    (Match, 'cases'):                     'match_case*',
    (Try, 'body'):                        'stmt*',
    (Try, 'handlers'):                    'excepthandler*',
    (Try, 'orelse'):                      'stmt*',
    (Try, 'finalbody'):                   'stmt*',
    (TryStar, 'body'):                    'stmt*',
    (TryStar, 'handlers'):                'excepthandlerstar*',
    (TryStar, 'orelse'):                  'stmt*',
    (TryStar, 'finalbody'):               'stmt*',
    # (Import, 'names'):                    'alias*',
    # (ImportFrom, 'names'):                'alias*',
    # (Global, 'names'):                    'identifier*',
    # (Nonlocal, 'names'):                  'identifier*',
    # (BoolOp, 'values'):                   'expr*',
    # (Dict, ''):                           'expr*',
    (Set, 'elts'):                        'expr*',
    # (ListComp, 'generators'):             'comprehension*',
    # (SetComp, 'generators'):              'comprehension*',
    # (DictComp, 'generators'):             'comprehension*',
    # (GeneratorExp, 'generators'):         'comprehension*',
    # (Compare, ''):                        'expr*',
    # (Call, 'args'):                       'expr*',
    # (Call, 'keywords'):                   'keyword*',
    # (JoinedStr, 'values'):                'expr*',
    # (TemplateStr, 'values'):              'expr*',
    (List, 'elts'):                       'expr*',
    (Tuple, 'elts'):                      'expr*',
    # (comprehension, 'ifs'):               'expr*',
    (ExceptHandler, 'body'):              'stmt*',
    (match_case, 'body'):                 'stmt*',
    # (MatchSequence, 'patterns'):          'pattern*',
    # (MatchMapping, ''):                   'expr*',
    # (MatchOr, 'patterns'):                'pattern*',
}


# ----------------------------------------------------------------------------------------------------------------------

def _get_slice(self: FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
               **options) -> FST:
    """Get a slice of child nodes from `self`."""

    ast = self.a

    if isinstance(ast, STMTISH_OR_STMTMOD):
        if field in STMTISH_FIELDS:
            return self._get_slice_stmtish(start, stop, field, cut, **options)

    elif isinstance(ast, (Tuple, List, Set)):
        return self._get_slice_tuple_list_or_set(start, stop, field, cut, **options)

    elif isinstance(ast, Dict):
        return self._get_slice_dict(start, stop, field, cut, **options)

    # elif self.is_empty_set_seq():  # or self.is_empty_set_call():
    #     return self._get_slice_empty_set(start, stop, field, cut, **options)


    # TODO: more individual specialized slice gets



    if (ast.__class__, field) in [
        (FunctionDef, 'decorator_list'),      # expr*
        (AsyncFunctionDef, 'decorator_list'), # expr*
        (ClassDef, 'decorator_list'),         # expr*
        (ClassDef, 'bases'),                  # expr*
        (Delete, 'targets'),                  # expr*
        (Assign, 'targets'),                  # expr*
        (BoolOp, 'values'),                   # expr*
        (Call, 'args'),                       # expr*
        (comprehension, 'ifs'),               # expr*

        (ListComp, 'generators'),             # comprehension*
        (SetComp, 'generators'),              # comprehension*
        (DictComp, 'generators'),             # comprehension*
        (GeneratorExp, 'generators'),         # comprehension*

        (ClassDef, 'keywords'),               # keyword*
        (Call, 'keywords'),                   # keyword*

        (Import, 'names'),                    # alias*
        (ImportFrom, 'names'),                # alias*

        (With, 'items'),                      # withitem*
        (AsyncWith, 'items'),                 # withitem*

        (MatchSequence, 'patterns'),          # pattern*
        (MatchMapping, 'patterns'),           # pattern*
        (MatchClass, 'patterns'),             # pattern*
        (MatchOr, 'patterns'),                # pattern*

        (FunctionDef, 'type_params'),         # type_param*
        (AsyncFunctionDef, 'type_params'),    # type_param*
        (ClassDef, 'type_params'),            # type_param*
        (TypeAlias, 'type_params'),           # type_param*

        (Global, 'names'),                    # identifier*
        (Nonlocal, 'names'),                  # identifier*

        (JoinedStr, 'values'),                # expr*
        (TemplateStr, 'values'),              # expr*

    ]:
        raise NotImplementedError('not implemented yet')


    raise ValueError(f"cannot get slice from {ast.__class__.__name__}.{field}")


# ----------------------------------------------------------------------------------------------------------------------

def _raw_slice_loc(self: FST, start: int | Literal['end'] | None, stop: int | None, field: str) -> fstloc:
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

    return fstloc(*body[start].f.pars(False)[:2],
                  *body[stop - 1].f.pars(False)[2:])


def _put_slice_raw(self: FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
                   *, one: bool = False, **options) -> Union[Self, None]:  # -> Self or reparsed Self
    """Put a raw slice of child nodes to `self`."""

    if code is None:
        raise NotImplementedError('raw slice delete not implemented yet')

    if isinstance(code, AST):
        if not one:
            try:
                ast = _coerce_ast(code, 'exprish')
            except Exception:
                pass

            else:
                if isinstance(ast, Tuple):  # strip delimiters because we want CONTENTS of slice for raw put, not the slice object itself
                    code = FST._unparse(ast)[1 : (-2 if len(ast.elts) == 1 else -1)]  # also remove singleton Tuple trailing comma
                elif isinstance(ast, (List, Dict, Set, MatchSequence, MatchMapping)):
                    code = FST._unparse(ast)[1 : -1]

    elif isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        try:
            ast = _coerce_ast(code.a, 'exprish')
        except Exception:
            pass

        else:
            fst = ast.f

            if one:
                if (is_par_tup := fst.is_parenthesized_tuple()) is None:  # only need to parenthesize this, others are already enclosed
                    if isinstance(ast, MatchSequence) and not fst._is_parenthesized_seq('patterns'):
                        fst._parenthesize_grouping()

                elif is_par_tup is False:
                    fst._parenthesize_node()

            elif ((is_dict := isinstance(ast, Dict)) or
                    (is_match := isinstance(ast, (MatchSequence, MatchMapping))) or
                    isinstance(ast, (Tuple, List, Set))
            ):
                if not ((is_par_tup := fst.is_parenthesized_tuple()) is False or  # don't strip nonexistent delimiters if is unparenthesized Tuple or MatchSequence
                        (is_par_tup is None and isinstance(ast, MatchSequence) and
                            not fst._is_parenthesized_seq('patterns'))
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


def _put_slice(self: FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
               one: bool = False, **options) -> Union[Self, None]:  # -> Self or reparsed Self or could disappear due to raw
    """Put an a slice of child nodes to `self`."""

    if code is self.root:  # don't allow own root to be put to self
        raise NodeError('circular put detected')

    ast = self.a
    raw = FST.get_option('raw', options)

    if options.get('to') is not None:
        raise ValueError(f"cannot put slice with 'to'")

    if raw is not True:
        try:
            if isinstance(ast, STMTISH_OR_STMTMOD):
                if field in STMTISH_FIELDS:
                    with self._modifying(field):
                        self._put_slice_stmtish(code, start, stop, field, one, **options)

                    return self

            elif isinstance(ast, (Tuple, List, Set)):
                with self._modifying(field):
                    self._put_slice_tuple_list_or_set(code, start, stop, field, one, **options)

                return self

            elif isinstance(ast, Dict):
                with self._modifying(field):
                    self._put_slice_dict(code, start, stop, field, one, **options)

                return self

            # elif self.is_empty_set_seq():  # or self.is_empty_set_call():
            #     self._put_slice_empty_set(code, start, stop, field, one, **options)

            #     return self


            # TODO: more individual specialized slice puts


            if (ast.__class__, field) in [
                (FunctionDef, 'decorator_list'),      # expr*
                (AsyncFunctionDef, 'decorator_list'), # expr*
                (ClassDef, 'decorator_list'),         # expr*
                (ClassDef, 'bases'),                  # expr*
                (Delete, 'targets'),                  # expr*
                (Assign, 'targets'),                  # expr*
                (BoolOp, 'values'),                   # expr*
                (Call, 'args'),                       # expr*
                (comprehension, 'ifs'),               # expr*

                (ListComp, 'generators'),             # comprehension*
                (SetComp, 'generators'),              # comprehension*
                (DictComp, 'generators'),             # comprehension*
                (GeneratorExp, 'generators'),         # comprehension*

                (ClassDef, 'keywords'),               # keyword*
                (Call, 'keywords'),                   # keyword*

                (Import, 'names'),                    # alias*
                (ImportFrom, 'names'),                # alias*

                (With, 'items'),                      # withitem*
                (AsyncWith, 'items'),                 # withitem*

                (MatchSequence, 'patterns'),          # pattern*
                (MatchMapping, 'patterns'),           # pattern*
                (MatchClass, 'patterns'),             # pattern*
                (MatchOr, 'patterns'),                # pattern*

                (FunctionDef, 'type_params'),         # type_param*
                (AsyncFunctionDef, 'type_params'),    # type_param*
                (ClassDef, 'type_params'),            # type_param*
                (TypeAlias, 'type_params'),           # type_param*

                (Global, 'names'),                    # identifier*
                (Nonlocal, 'names'),                  # identifier*

                (JoinedStr, 'values'),                # expr*
                (TemplateStr, 'values'),              # expr*

            ]:
                raise NotImplementedError("not implemented yet, try with option raw='auto'")

        except (NodeError, SyntaxError, NotImplementedError):
            if not raw:
                raise

        else:
            if not raw:
                raise ValueError(f"cannot put slice to {ast.__class__.__name__}.{field}")

    with self._modifying(field, True):
        return _put_slice_raw(self, code, start, stop, field, one=one, **options)


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = ['_get_slice', '_put_slice']  # used by make_docs.py

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
