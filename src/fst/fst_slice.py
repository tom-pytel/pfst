"""Misc lower level FST methods."""

from ast import *
from typing import Literal

from .astutil import *
from .astutil import TypeAlias, TemplateStr

from .shared import (
    STMTISH_OR_STMTMOD, STMTISH_FIELDS, Code, NodeError,
)


# ----------------------------------------------------------------------------------------------------------------------

def _get_slice(self: 'FST', start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
               **options) -> 'FST':
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


    raise ValueError(f"cannot get slice from {ast.__class__.__name__}.{field}")


# ----------------------------------------------------------------------------------------------------------------------

def _put_slice(self: 'FST', code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
               one: bool = False, **options) -> 'FST':  # -> Self
    """Put an a slice of child nodes to `self`."""

    ast = self.a
    raw = FST.get_option('raw', options)

    if raw is not True:
        try:
            if isinstance(ast, STMTISH_OR_STMTMOD):
                if field in STMTISH_FIELDS:
                    modified = self._modifying(field)

                    self._put_slice_stmtish(code, start, stop, field, one, **options)
                    modified()

                    return self

            elif isinstance(ast, (Tuple, List, Set)):
                modified = self._modifying(field)

                self._put_slice_tuple_list_or_set(code, start, stop, field, one, **options)
                modified()

                return self

            elif isinstance(ast, Dict):
                modified = self._modifying(field)

                self._put_slice_dict(code, start, stop, field, one, **options)
                modified()

                return self

            # elif self.is_empty_set_seq():  # or self.is_empty_set_call():
            #     self._put_slice_empty_set(code, start, stop, field, one, **options)

            #     return self


            # TODO: more individual specialized slice puts


            elif (ast.__class__, field) in [
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
                raise NodeError('not implemented yet')

        except (SyntaxError, NodeError):
            if not raw:
                raise

        else:
            if not raw:
                raise ValueError(f"cannot put slice to {ast.__class__.__name__}.{field}")

    return self._reparse_raw_slice(code, start, stop, field, one=one, **options)


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = ['_get_slice', '_put_slice']

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
