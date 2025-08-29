from __future__ import annotations

from builtins import slice
from typing import Literal

from . import fst

from .astutil import AST, get_func_class_or_ass_by_name
from .misc import fixup_one_index, fixup_slice_indices
from .code import Code

__all__ = ['fstview']


class fstview:
    """View for a list of `AST` nodes in a body, or any other field which is a list of values (not necessarily `AST`
    nodes), of an `FST` node.

    This object acts as a list of corresponding `FST` nodes if applicable or otherwise strings (for example for a list
    of `Global.names`). It is only meant for short term convenience along the lines of `fst.body.append(...)`. Outside
    of this use, operations on the target `FST` node of the view which are not effectuated through the view may
    invalidate the `start`  and `stop` positions and even the `fst` stored in the view if they change the size of the
    list of nodes or reparse. Especially raw operations which reparse entire statements and can easily invalidate an
    `fstview` even if performed directly on it.

    Nodes can be gotten or put via indexing. Nodes which are accessed through indexing (normal or slice) are not
    automatically copied, if a copy is desired then do `fst.body[start:stop].copy()`. Slice assignments also work but
    will always assign a slice to the range. If you want to assign an individual item to this range or a subrange then
    use `fst.body[start:stop].replace(..., one=True)`.

    **WARNING!** Keep in mind that operations on NODES or even CHILD VIEWS instead of on THIS VIEW will not update this
    view. Do not hold on to views, use them and discard.

    ```py
    >>> from fst import FST

    >>> view = FST('[1, 2, 3]').elts

    >>> view[1].remove()  # operation on node

    >>> view  # notice the size of the view is 3 but there are only two elements
    <<List ROOT 0,0..0,6>.elts[0:3] [<Constant 0,1..0,2>, <Constant 0,4..0,5>]>

    >>> view = FST('[1, 2, 3]').elts

    >>> view[1:].cut()  # not an operation on this view but a child view
    <List ROOT 0,0..0,6>

    >>> view  # WRONG again
    <<List ROOT 0,0..0,3>.elts[0:3] [<Constant 0,1..0,2>]>
    ```

    This object is meant to be, and is normally created automatically by accessing `AST` list fields on an `FST` node.

    **Examples:**
    ```py
    >>> from fst import FST

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

    fst:   fst.FST  ; """The target `FST` node this view references."""
    field: str      ; """The target field this view references."""
    start: int      ; """Start position within the target field list this view references."""
    stop:  int      ; """One past the last element within the target field list this view references."""

    is_FST = False  ; """@private"""  # for quick checks vs. `FST`

    @property
    def root(self) -> fst.FST:
        """Root node of the `FST` node this view belongs to."""

        return self.fst.root

    def __init__(self, fst: fst.FST, field: str, start: int, stop: int):
        """@private"""

        self.fst   = fst
        self.field = field
        self.start = start
        self.stop  = stop

    def __repr__(self) -> str:
        return f'<{self.fst!r}.{self.field}[{self.start}:{self.stop}] {list(self)}>'

    def __len__(self) -> int:
        return self.stop - self.start

    def __getitem__(self, idx: int | slice | str) -> fstview | fst.FST | str | None:
        r"""Get a single item or a slice view from this slice view. All indices (including negative) are relative to the
        bounds of this view. This is just an access, not a cut or a copy, so if you want a copy you must explicitly do
        `.copy()` on the returned value.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when dealing with
        return values which may be `None` or may not be `FST` nodes.

        **Parameters:**
        - `idx`: The index or `slice` where to get the element(s) from. If is a single string then this it will return
            the first function, class or variable assignment to the name matching this string (if is a list of
            statements, error otherwise). This is just a convenience and will probably change / expand in the future.

        **Returns:**
        - `fstview | `: Either a single `FST` node if accessing a single item or a new `fstview` view
            according to the slice passed. `str` can also be returned from a view of `Global.names` or `None` from a
            `Dict.keys`.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1].src
        '1'

        >>> FST('[0, 1, 2, 3]').elts[:3]
        <<List ROOT 0,0..0,12>.elts[0:3] [<Constant 0,1..0,2>, <Constant 0,4..0,5>, <Constant 0,7..0,8>]>

        >>> FST('[0, 1, 2, 3]').elts[:3].copy().src
        '[0, 1, 2]'

        >>> FST('[0, 1, 2, 3]').elts[-3:]
        <<List ROOT 0,0..0,12>.elts[1:4] [<Constant 0,4..0,5>, <Constant 0,7..0,8>, <Constant 0,10..0,11>]>

        >>> FST('def fun(): pass\nclass cls: pass\nvar = val').body['cls']
        <ClassDef 1,0..1,15>

        >>> FST('global a, b, c').names
        <<Global ROOT 0,0..0,14>.names[0:3] ['a', 'b', 'c']>

        >>> FST('global a, b, c').names[1]
        'b'
        ```
        @public
        """

        if isinstance(idx, int):
            idx = fixup_one_index(self.stop - (start := self.start), idx)

            return a.f if isinstance(a := getattr(self.fst.a, self.field)[start + idx], AST) else a

        if isinstance(idx, str):
            if not (a := get_func_class_or_ass_by_name(getattr(self.fst.a, self.field)[self.start : self.stop], idx)):
                raise IndexError(f"function, class or variable '{idx}' not found")

            return a.f

        if idx.step is not None:
            raise IndexError('step slicing not supported')

        idx_start, idx_stop = fixup_slice_indices(self.stop - (start := self.start), idx.start, idx.stop)

        return fstview(self.fst, self.field, start + idx_start, start + idx_stop)

    def __setitem__(self, idx: int | slice, code: Code | None) -> None:
        """Set a single item or a slice view in this slice view. All indices (including negative) are relative to the
        bounds of this view. This is not just with a set, it is a full `FST` operation.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when assigning
        values.

        **WARNING!** Currently, for non-AST views, individual value assignment works but slices do not yet.

        **Parameters:**
        - `idx`: The index or `slice` where to put the element(s).

        **Examples:**
        ```py
        >>> from fst import FST

        >>> (f := FST('[0, 1, 2, 3]')).elts[1] = '4'; f.src
        '[0, 4, 2, 3]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[:3] = '[5]'; f.src
        '[5, 3]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[:3] = '5,'; f.src
        '[5, 3]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[-3:] = '[6]'; f.src
        '[0, 6]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[:] = '7, 8'; f.src
        '[7, 8]'

        >>> f = FST('[0, 1, 2, 3]')
        >>> f.elts[2:2] = f.elts[1:3].copy()
        >>> f.src
        '[0, 1, 1, 2, 2, 3]'
        ```
        @public
        """

        if isinstance(idx, int):
            idx        = fixup_one_index(self.stop - (start := self.start), idx)
            len_before = len(asts := getattr(self.fst.a, self.field))

            self.fst = self.fst.put(code, start + idx, field=self.field) or self.fst

            self.stop += len(asts) - len_before

        elif idx.step is not None:
            raise IndexError('step slicing not supported')

        else:
            idx_start, idx_stop = fixup_slice_indices(self.stop - (start := self.start), idx.start, idx.stop)
            len_before          = len(asts := getattr(self.fst.a, self.field))

            self.fst = self.fst.put_slice(code, start + idx_start, start + idx_stop, self.field)

            self.stop += len(asts) - len_before

    def __delitem__(self, idx: int | slice) -> None:
        """Delete a single item or a slice from this slice view. All indices (including negative) are relative to the
        bounds of this view.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when assigning
        values.

        **WARNING!** Currently, for non-AST views, deletion is not supported

        **Parameters:**
        - `idx`: The index or `slice` to delete.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> del (f := FST('[0, 1, 2, 3]')).elts[1]; f.src
        '[0, 2, 3]'

        >>> del (f := FST('[0, 1, 2, 3]')).elts[:3]; f.src
        '[3]'

        >>> del (f := FST('[0, 1, 2, 3]')).elts[-3:]; f.src
        '[0]'

        >>> del (f := FST('[0, 1, 2, 3]')).elts[:]; f.src
        '[]'
        ```
        @public
        """

        if isinstance(idx, int):
            idx = fixup_one_index((stop := self.stop) - (start := self.start), idx)

            self.fst = self.fst.put_slice(None, start + idx, start + idx + 1, field=self.field)

            self.stop = max(start, stop - 1)

        elif idx.step is not None:
            raise IndexError('step slicing not supported')

        else:
            idx_start, idx_stop = fixup_slice_indices((stop := self.stop) - (start := self.start), idx.start, idx.stop)

            self.fst = self.fst.put_slice(None, start + idx_start, start + idx_stop, self.field)

            self.stop = max(start, stop - (idx_stop - idx_start))

    def copy(self, **options) -> fst.FST:
        """Copy this slice to a new top-level tree, dedenting and fixing as necessary.

        **Parameters:**
        - `options`: See `fst.fst.FST.options()`.

        **Returns:**
        - `FST`: Copied slice.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1:3].copy().src
        '[1, 2]'
        ```
        """

        return self.fst.get_slice(self.start, self.stop, self.field, cut=False, **options)

    def cut(self, **options) -> fst.FST:
        """Cut out this slice to a new top-level tree (if possible), dedenting and fixing as necessary. Cannot cut root
        node.

        **Parameters:**
        - `options`: See `fst.fst.FST.options()`.

        **Returns:**
        - `FST`: Cut slice.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> (f := FST('[0, 1, 2, 3]')).elts[1:3].cut().src
        '[1, 2]'

        >>> f.src
        '[0, 3]'
        ```
        """

        f = self.fst.get_slice(start := self.start, self.stop, self.field, cut=True, **options)

        self.stop = start

        return f

    def replace(self, code: Code | None, one: bool = True, **options) -> fstview | None:  # -> Self or reparsed Self or could disappear due to raw
        """Replace or delete (if `code=None`) this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to put. `None` to delete this slice.
        - `one`: If `True` then will replace the range of this slice with a single item. Otherwise `False` will attempt
            a slice replacement (type must be compatible).
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1:3].replace('(4, 5)').fst.src
        '[0, (4, 5), 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].replace('(4, 5)', one=False).fst.src
        '[0, 4, 5, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst = self.fst.put_slice(code, self.start, self.stop, self.field, one=one, **options)

        self.stop += len(asts) - len_before

        return self

    def remove(self, **options) -> fstview | None:  # -> Self or reparsed Self or could disappear due to raw
        """Delete this slice, equivalent to `replace(None, ...)`

        **Parameters:**
        - `options`: See `fst.fst.FST.options()`.

        **Returns:**
        - `self`

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1:3].remove().fst.src
        '[0, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst = self.fst.put_slice(None, self.start, self.stop, self.field, one=True, **options)

        self.stop += len(asts) - len_before

        return self

    def insert(self, code: Code, idx: int | Literal['end'] = 0, one: bool = True, **options) -> fstview | None:  # -> Self or reparsed Self or could disappear due to raw
        """Insert into this slice at a specific index.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to insert.
        - `idx`: Index to insert BEFORE. Can be `'end'` to indicate add at end of slice.
        - `one`: If `True` then will insert `code` as a single item. Otherwise `False` will attempt a slice insertion
            (type must be compatible).
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 1).fst.src
        '[0, (4, 5), 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 'end', one=False).fst.src
        '[0, 1, 2, 3, 4, 5]'

        >>> # same as 'end' but 'end' is always 'end'
        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 4, one=False).fst.src
        '[0, 1, 2, 3, 4, 5]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].insert('*star').fst.src
        '[0, *star, 1, 2, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))
        idx        = (self.stop if idx == 'end' else
                      stop if idx > (l := (stop := self.stop) - (start := self.start)) else
                      start + (idx if idx >= 0 else max(0, idx + l)))

        self.fst = self.fst.put_slice(code, idx, idx, self.field, one=one, **options)

        self.stop += len(asts) - len_before

        return self

    def append(self, code: Code, **options) -> fstview | None:  # -> Self or reparsed Self or could disappear due to raw
        """Append `code` as a single element to the end of this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to append.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.append('(4, 5)').fst.src
        '[0, 1, 2, 3, (4, 5)]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].append('*star').fst.src
        '[0, 1, 2, *star, 3]'
        ```
        """

        self.fst = self.fst.put_slice(code, stop := self.stop, stop, self.field, one=True, **options)

        self.stop = stop + 1

        return self

    def extend(self, code: Code, **options) -> fstview | None:  # -> Self or reparsed Self or could disappear due to raw
        """Extend this slice with the slice in `code` (type must be compatible).

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` slice to extend.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.extend('(4, 5)').fst.src
        '[0, 1, 2, 3, 4, 5]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].extend('(4, 5)').fst.src
        '[0, 1, 2, 4, 5, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst = self.fst.put_slice(code, stop := self.stop, stop, self.field, one=False, **options)

        self.stop = stop + (len(asts) - len_before)

        return self

    def prepend(self, code: Code, **options) -> fstview | None:  # -> Self or reparsed Self or could disappear due to raw
        """prepend `code` as a single element to the beginning of this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to preappend.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.prepend('(4, 5)').fst.src
        '[(4, 5), 0, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].prepend('*star').fst.src
        '[0, *star, 1, 2, 3]'
        ```
        """

        self.fst = self.fst.put_slice(code, start := self.start, start, self.field, one=True, **options)

        self.stop += 1

        return self

    def prextend(self, code: Code, **options) -> fstview | None:  # -> Self or reparsed Self or could disappear due to raw
        """Extend the beginning of this slice with the slice in `code` (type must be compatible).

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to extend at the start.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**
        ```py
        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.prextend('(4, 5)').fst.src
        '[4, 5, 0, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].prextend('(4, 5)').fst.src
        '[0, 4, 5, 1, 2, 3]'
        ```
        """

        len_before = len(asts := getattr(self.fst.a, self.field))

        self.fst = self.fst.put_slice(code, start := self.start, start, self.field, one=False, **options)

        self.stop += len(asts) - len_before

        return self
