from ast import *
from typing import Any, Literal

from .astutil import *
from .shared import Code, _fixup_one_index, _fixup_slice_indices


class fstlist:
    """Proxy for list of AST nodes in a body (or any other list of AST nodes) which acts as a list of FST nodes. Is only
    meant for short term convenience use as operations on the target FST node which are not effectuated through this
    proxy will invalidate the start and stop positions stored here if they change the size of the list of nodes."""

    fst:   'FST'
    field: str
    start: int
    stop:  int

    def __init__(self, fst: 'FST', field: str, start: int, stop: int):
        self.fst   = fst
        self.field = field
        self.start = start
        self.stop  = stop

    def __repr__(self) -> str:
        return f'<fstlist {self.fst!r}.{self.field}[{self.start}:{self.stop}] {list(self)}>'

    def __len__(self) -> int:
        return self.stop - self.start

    def __getitem__(self, idx: int | slice | str) -> Any:
        if isinstance(idx, int):
            idx = _fixup_one_index(self.stop - (start := self.start), idx)

            return a.f if isinstance(a := getattr(self.fst.a, self.field)[start + idx], AST) else a

        if isinstance(idx, str):
            if not (a := get_func_class_or_ass_by_name(getattr(self.fst.a, self.field)[self.start : self.stop],
                                                       idx, False)):
                raise IndexError(f"function or class '{idx}' not found")

            return a.f

        if idx.step is not None:
            raise IndexError('step slicing not supported')

        idx_start, idx_stop = _fixup_slice_indices(self.stop - (start := self.start), idx.start, idx.stop)

        return fstlist(self.fst, self.field, start + idx_start, start + idx_stop)

    def __setitem__(self, idx: int | slice, code: Code | None):
        if isinstance(idx, int):
            idx = _fixup_one_index(self.stop - (start := self.start), idx)

            self.fst.put(code, start + idx, field=self.field)

        elif idx.step is not None:
            raise IndexError('step slicing not supported')

        else:
            idx_start, idx_stop = _fixup_slice_indices(self.stop - (start := self.start), idx.start, idx.stop)

            self.fst.put_slice(code, start + idx_start, start + idx_stop, self.field)

    def __delitem__(self, idx: int | slice):
        if isinstance(idx, int):
            idx = _fixup_one_index((stop := self.stop) - (start := self.start), idx)

            self.fst.put_slice(None, start + idx, start + idx + 1, field=self.field)

            self.stop = max(start, stop - 1)

        elif idx.step is not None:
            raise IndexError('step slicing not supported')

        else:
            idx_start, idx_stop = _fixup_slice_indices(self.stop - (start := self.start), idx.start, idx.stop)

            self.fst.put_slice(None, start + idx_start, start + idx_stop, self.field)

            self.stop = max(start, stop - (idx_stop - idx_start))

    def copy(self, **options) -> 'FST':
        return self.fst.get_slice(self.start, self.stop, self.field, cut=False, **options)

    def cut(self, **options) -> 'FST':
        f         = self.fst.get_slice(start := self.start, self.stop, self.field, cut=True, **options)
        self.stop = start

        return f

    def replace(self, code: Code | None, one: bool = True, **options):  # -> Self
        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst.put_slice(code, self.start, self.stop, self.field, one=one, **options)

        self.stop += len(asts) - len_before

        return self

    def insert(self, code: Code, idx: int | Literal['end'] = 0, *, one: bool = True, **options) -> 'FST':  # -> Self
        len_before = len(asts := getattr(self.fst.a, self.field))
        idx        = (self.stop if idx == 'end' else
                      stop      if idx > (l := (stop := self.stop) - (start := self.start)) else
                      start + (idx if idx >= 0 else max(0, idx + l)))

        self.fst.put_slice(code, idx, idx, self.field, one=one, **options)

        self.stop += len(asts) - len_before

        return self

    def append(self, code: Code, **options) -> 'FST':  # -> Self
        self.fst.put_slice(code, stop := self.stop, stop, self.field, one=True, **options)

        self.stop = stop + 1

        return self

    def extend(self, code: Code, **options) -> 'FST':  # -> Self
        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst.put_slice(code, stop := self.stop, stop, self.field, one=False, **options)

        self.stop = stop + (len(asts) - len_before)

        return self

    def prepend(self, code: Code, **options) -> 'FST':  # -> Self
        self.fst.put_slice(code, start := self.start, start, self.field, one=True, **options)

        self.stop += 1

        return self

    def prextend(self, code: Code, **options) -> 'FST':  # -> Self
        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst.put_slice(code, start := self.start, start, self.field, one=False, **options)

        self.stop += len(asts) - len_before

        return self


__all__ = ['fstlist']

from .fst import FST
