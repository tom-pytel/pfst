from ast import *
from builtins import slice
from typing import Any, Literal

from .astutil import *
from .shared import Self, Code, _fixup_one_index, _fixup_slice_indices


class fstlist:
    """View for a list of `AST` nodes in a body, or any other field which is a list of `AST` nodes, of an `FST` node.
    This object acts as a list of corresponding `FST` nodes. Is only meant for short term convenience use as operations
    on the target `FST` node which are not effectuated through this view may invalidate the `start` and `stop` positions
    and even the `fst` stored here if they change the size of the list of nodes or reparse. Especially raw operations
    which reparse entire statements and can easily invalidate an `fstlist` even if performed directly on it.

    Nodes can be gotten or put via indexing. Nodes which are gotten are not automatically copied, if a copy is desired
    then do `fstlist[start:stop].copy()`. Slice assignments also work but will always assign a slice to the range. If
    you want to assign an individual item then use the `replace()` method.

    This object is meant to be, and is normally created automatically by accessing `AST` list fields on an `FST` node.

    **Example:**
    ```py
    >>> f = FST('[0, 1, 2, 3]')
    >>> f
    <List ROOT 0,0..0,12>
    >>> f.elts
    <<List ROOT 0,0..0,12>.elts[0:4] [<Constant 0,1..0,2>, <Constant 0,4..0,5>, <Constant 0,7..0,8>, <Constant 0,10..0,11>]>
    >>> f.elts[1]
    <Constant 0,4..0,5>
    >>> f.elts[1].src
    '1'
    >>> f.elts[1:3]
    <<List ROOT 0,0..0,12>.elts[1:3] [<Constant 0,4..0,5>, <Constant 0,7..0,8>]>
    >>> f.elts[1:3].copy()
    <List ROOT 0,0..0,6>
    >>> _.src
    '[1, 2]'
    >>> f.elts[1:3] = '[4]'
    >>> f.src
    '[0, 4, 3]'
    >>> del f.elts[1:]
    >>> f.src
    '[0]'
    >>> f.elts[0] = '*star'
    >>> f.src
    '[*star]'
    ```
    """

    fst:   'FST'  ; """`FST` node parent of this list."""
    field: str    ; """The target field of `AST` node being referenced."""
    start: int    ; """Start position within the target field list of this view."""
    stop:  int    ; """One past the last element within the target field list of this view."""

    is_FST = False  ; """@private"""  # for quick checks vs. `FST`

    def __init__(self, fst: 'FST', field: str, start: int, stop: int):
        self.fst   = fst
        self.field = field
        self.start = start
        self.stop  = stop

    def __repr__(self) -> str:
        return f'<{self.fst!r}.{self.field}[{self.start}:{self.stop}] {list(self)}>'

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
            idx_start, idx_stop = _fixup_slice_indices((stop := self.stop) - (start := self.start), idx.start, idx.stop)

            self.fst.put_slice(None, start + idx_start, start + idx_stop, self.field)

            self.stop = max(start, stop - (idx_stop - idx_start))

    def copy(self, **options) -> 'FST':
        """Copy this slice to a new top-level tree, dedenting and fixing as necessary.

        **Parameters:**
        - `options`: See `fst.fst.FST.set_option`.

        **Returns:**
        - `FST`: Copied slice.

        **Example:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts[1:3].copy().src
        '[1, 2]'
        ```
        """

        return self.fst.get_slice(self.start, self.stop, self.field, cut=False, **options)

    def cut(self, **options) -> 'FST':
        """Cut out this slice to a new top-level tree (if possible), dedenting and fixing as necessary. Cannot cut root
        node.

        **Parameters:**
        - `options`: See `fst.fst.FST.set_option`.

        **Returns:**
        - `FST`: Cut slice.

        **Example:**
        ```py
        >>> (f := FST('[0, 1, 2, 3]')).elts[1:3].cut().src
        '[1, 2]'
        >>> f.src
        '[0, 3]'
        ```
        """

        f         = self.fst.get_slice(start := self.start, self.stop, self.field, cut=True, **options)
        self.stop = start

        return f

    def replace(self, code: Code | None, one: bool = True, **options) -> Self:
        """Replace or delete (if `code=None`) this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to put. `None` to delete this slice.
        - `one`: If `True` then will replace the range of this slice with a single item. Otherwise `False` will attempt
            a slice replacement (type must be compatible).
        - `options`: See `get_options()`.

        **Example:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts[1:3].replace('(4, 5)').fst.src
        '[0, (4, 5), 3]'
        >>> FST('[0, 1, 2, 3]').elts[1:3].replace('(4, 5)', one=False).fst.src
        '[0, 4, 5, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst.put_slice(code, self.start, self.stop, self.field, one=one, **options)

        self.stop += len(asts) - len_before

        return self

    def remove(self, **options) -> Self:
        """Delete this slice, equivalent to `replace(None, ...)`

        **Parameters:**
        - `options`: See `get_options()`.

        **Returns:**
        - `self`

        **Example:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts[1:3].remove().fst.src
        '[0, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst.put_slice(None, self.start, self.stop, self.field, one=True, **options)

        self.stop += len(asts) - len_before

        return self

    def insert(self, code: Code, idx: int | Literal['end'] = 0, one: bool = True, **options) -> Self:
        """Insert into this slice at a specific index.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to insert.
        - `idx`: Index to insert BEFORE. Can be `'end'` to indicate add at end of slice.
        - `one`: If `True` then will insert `code` as a single item. Otherwise `False` will attempt a slice insertion
            (type must be compatible).
        - `options`: See `get_options()`.

        **Example:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 1).fst.src
        '[0, (4, 5), 1, 2, 3]'
        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 'end', one=False).fst.src
        '[0, 1, 2, 3, 4, 5]'
        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 4, one=False).fst.src  # same as 'end' but 'end' is always 'end'
        '[0, 1, 2, 3, 4, 5]'
        >>> FST('[0, 1, 2, 3]').elts[1:3].insert('*star').fst.src
        '[0, *star, 1, 2, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))
        idx        = (self.stop if idx == 'end' else
                      stop      if idx > (l := (stop := self.stop) - (start := self.start)) else
                      start + (idx if idx >= 0 else max(0, idx + l)))

        self.fst.put_slice(code, idx, idx, self.field, one=one, **options)

        self.stop += len(asts) - len_before

        return self

    def append(self, code: Code, **options) -> 'FST':  # -> Self
        """Append `code` as a single element to the end of this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to append.
        - `options`: See `get_options()`.

        **Example:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts.append('(4, 5)').fst.src
        '[0, 1, 2, 3, (4, 5)]'
        >>> FST('[0, 1, 2, 3]').elts[1:3].append('*star').fst.src
        '[0, 1, 2, *star, 3]'
        ```
        """

        self.fst.put_slice(code, stop := self.stop, stop, self.field, one=True, **options)

        self.stop = stop + 1

        return self

    def extend(self, code: Code, **options) -> 'FST':  # -> Self
        """Extend this slice with the slice in `code` (type must be compatible).

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` slice to extend.
        - `options`: See `get_options()`.

        **Example:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts.extend('(4, 5)').fst.src
        '[0, 1, 2, 3, 4, 5]'
        >>> FST('[0, 1, 2, 3]').elts[1:3].extend('(4, 5)').fst.src
        '[0, 1, 2, 4, 5, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst.put_slice(code, stop := self.stop, stop, self.field, one=False, **options)

        self.stop = stop + (len(asts) - len_before)

        return self

    def prepend(self, code: Code, **options) -> 'FST':  # -> Self
        """prepend `code` as a single element to the beginning of this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to preappend.
        - `options`: See `get_options()`.

        **Example:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts.prepend('(4, 5)').fst.src
        '[(4, 5), 0, 1, 2, 3]'
        >>> FST('[0, 1, 2, 3]').elts[1:3].prepend('*star').fst.src
        '[0, *star, 1, 2, 3]'
        ```
        """

        self.fst.put_slice(code, start := self.start, start, self.field, one=True, **options)

        self.stop += 1

        return self

    def prextend(self, code: Code, **options) -> 'FST':  # -> Self
        """Extend the beginning of this slice with the slice in `code` (type must be compatible).

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to extend at the start.
        - `options`: See `get_options()`.

        **Example:**
        ```py
        >>> FST('[0, 1, 2, 3]').elts.prextend('(4, 5)').fst.src
        '[4, 5, 0, 1, 2, 3]'
        >>> FST('[0, 1, 2, 3]').elts[1:3].prextend('(4, 5)').fst.src
        '[0, 4, 5, 1, 2, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst.put_slice(code, start := self.start, start, self.field, one=False, **options)

        self.stop += len(asts) - len_before

        return self


# ----------------------------------------------------------------------------------------------------------------------
__all__ = ['fstlist']

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
