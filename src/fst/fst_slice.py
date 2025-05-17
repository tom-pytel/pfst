"""Misc lower level FST methods."""

from ast import *
from typing import Literal

from .astutil import *

from .shared import (
    STMTISH_OR_STMTMOD, STMTISH_FIELDS, Code, NodeTypeError,
    _fixup_field_body,
)


# ----------------------------------------------------------------------------------------------------------------------

def _get_slice(self: 'FST', start: int | Literal['end'] | None, stop: int | None, field: str | None, cut: bool,
               **options) -> 'FST':
    """Get a slice of child nodes from `self`."""

    ast       = self.a
    field_, _ = _fixup_field_body(ast, field)

    if isinstance(ast, STMTISH_OR_STMTMOD):
        if field_ in STMTISH_FIELDS:
            return self._get_slice_stmtish(start, stop, field, cut, **options)

    elif isinstance(ast, (Tuple, List, Set)):
        return self._get_slice_tuple_list_or_set(start, stop, field, cut, **options)

    elif isinstance(ast, Dict):
        return self._get_slice_dict(start, stop, field, cut, **options)

    elif self.is_empty_set_call() or self.is_empty_set_seq():
        return self._get_slice_empty_set(start, stop, field, cut, **options)


    # TODO: more individual specialized slice gets


    raise ValueError(f"cannot get slice from {ast.__class__.__name__}.{field}")


# ----------------------------------------------------------------------------------------------------------------------

def _put_slice(self: 'FST', code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str | None,
               one: bool = False, **options) -> 'FST':  # -> Self
    """Put an a slice of child nodes to `self`."""

    ast       = self.a
    raw       = FST.get_option('raw', options)
    field_, _ = _fixup_field_body(ast, field)  # TODO: remove this and pass resolved field?

    if raw is not True:
        try:
            if isinstance(ast, STMTISH_OR_STMTMOD):
                if field_ in STMTISH_FIELDS:
                    self._put_slice_stmtish(code, start, stop, field, one, **options)

                    return self

            elif isinstance(ast, (Tuple, List, Set)):
                self._put_slice_tuple_list_or_set(code, start, stop, field, one, **options)

                return self

            elif isinstance(ast, Dict):
                self._put_slice_dict(code, start, stop, field, one, **options)

                return self

            elif self.is_empty_set_call() or self.is_empty_set_seq():
                self._put_slice_empty_set(code, start, stop, field, one, **options)

                return self


            # TODO: more individual specialized slice puts


        except (SyntaxError, NodeTypeError):
            if not raw:
                raise

        else:
            if not raw:
                raise ValueError(f"cannot put slice to {ast.__class__.__name__}.{field}")

    return self._reparse_raw_slice(code, start, stop, field, one=one, **options)


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = ['_get_slice', '_put_slice']


from .fst import FST
