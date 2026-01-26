"""Slice-access views on `FST` lists of children."""

from __future__ import annotations

from builtins import slice
from typing import Literal

from . import fst

from .astutil import OPCLS2STR, AST
from .code import Code
from .fst_misc import fixup_one_index, fixup_slice_indices
from .fst_options import check_options

__all__ = [
    'fstview',
    'fstview_Dict',
    'fstview_MatchMapping',
    'fstview_Compare',
    'fstview_arguments',
    'fstview__body',
    'fstview_arglikes',
    'fstview_dummy',
]


class fstview:
    """View for a list of `AST` nodes in a body, or any other field which is a list of values (not necessarily `AST`
    nodes), of an `FST` node.

    Nodes can be gotten or put via indexing. Nodes which are accessed through indexing (normal or slice) are not
    automatically copied, if a copy is desired then do `fst.body[start:stop].copy()`. Slice assignments also work but
    will always assign a slice to the range. If you want to assign an individual item to this range or a subrange then
    use `fst.body[start:stop].replace(..., one=True)`.

    >>> from fst import FST

    >>> view = FST('[1, 2, 3]').elts

    >>> view[1].remove()

    >>> view
    <<List ROOT 0,0..0,6>.elts [<Constant 0,1..0,2>, <Constant 0,4..0,5>]>

    >>> view[1:].cut()
    <List ROOT 0,0..0,3>

    >>> view
    <<List ROOT 0,0..0,3>.elts [<Constant 0,1..0,2>]>

    This object is meant to be, and is normally created automatically by accessing `AST` list fields on an `FST` node.

    **Examples:**

    >>> from fst import FST

    >>> f = FST('[0, 1, 2, 3]')
    >>> f
    <List ROOT 0,0..0,12>

    >>> f.elts
    <<List ROOT 0,0..0,12>.elts [<Constant 0,1..0,2>, <Constant 0,4..0,5>, <Constant 0,7..0,8>, <Constant 0,10..0,11>]>

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
    '[0, [4], 3]'

    >>> f.elts[1:2] = '4'
    >>> f.src
    '[0, 4, 3]'

    >>> del f.elts[1:]
    >>> f.src
    '[0]'

    >>> f.elts[0] = '*star'
    >>> f.src
    '[*star]'
    """

    base:   fst.FST     ; """The target `FST` node this view references."""
    field:  str         ; """The target field this view references. Can be virtual field like `_all`."""
    _start: int         ; """Start position within the target field list this view references."""
    _stop:  int | None  ; """One past the last element within the target field list this view references. `None` means 'end', pinned the end of the field whatever it may be."""

    is_FST = False  ; """Allows to quickly differentiate between actual `FST` nodes vs. views or locations."""  # for quick checks vs. `FST`

    @property
    def start(self) -> int:
        """Start position within the target field list this view references."""

        return self._get_indices()[0]

    @property
    def stop(self) -> int:
        """One past the last element within the target field list this view references."""

        return self._get_indices()[1]

    def _len_field(self) -> int:
        """Length of full base `FST` field, irrespective of view `start` and `stop`."""

        return len(getattr(self.base.a, self.field))

    def _deref_one(self, idx: int) -> AST | str:
        """Return a single element from field (which may not be a contiguous list). `idx` is the real index already
        absolute (offset by any `start`) and is guaranteed to be positive and valid. NO COPY, JUST RETURN NODE. Can
        return `AST` or primitive or another `fstview`."""

        return getattr(self.base.a, self.field)[idx]

    def _get_indices(self) -> tuple[int, int, int]:
        """Refresh indices in case of field length change anywhere else and return them along with full length of field.

        **Returns:**
        - `(start, stop, len_field)`: Good start and stop indices and full length of field currently.
        """

        len_field = self._len_field()

        if (stop := self._stop) is None:
            stop = len_field
        elif stop > len_field:
            stop = self._stop = len_field

        if (start := self._start) > stop:
            start = self._start = stop

        return start, stop, len_field

    def __init__(self, base: fst.FST, field: str, start: int = 0, stop: int | None = None) -> None:
        """@private"""

        self.base = base
        self.field = field
        self._start = start
        self._stop = stop

    def __repr__(self) -> str:
        start, stop, _ = self._get_indices()
        indices = f'[{start or ""}:{stop}]' if self._stop is not None else f'[{start}:]' if start else ''

        return f'<{self.base!r}.{self.field}{indices} {list(self)}>'

    def __len__(self) -> int:
        start, stop, _ = self._get_indices()

        return stop - start

    def __getitem__(self, idx: int | slice) -> fstview | fst.FST | str | None:
        r"""Get a single item or a slice view from this slice view. All indices (including negative) are relative to the
        bounds of this view. This is just an access, not a cut or a copy, so if you want a copy you must explicitly do
        `.copy()` on the returned value.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when dealing with
        return values which may be `None` or may not be `FST` nodes.

        **Parameters:**
        - `idx`: The index or `slice` where to get the element(s) from.

        **Returns:**
        - `fstview | FST | str | None`: Either a single `FST` node if accessing a single item or a new `fstview` view
            according to the slice passed. `str` can also be returned from a view of `Global.names` or `None` from a
            `Dict.keys`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1].src
        '1'

        >>> FST('[0, 1, 2, 3]').elts[:3]
        <<List ROOT 0,0..0,12>.elts[:3] [<Constant 0,1..0,2>, <Constant 0,4..0,5>, <Constant 0,7..0,8>]>

        >>> FST('[0, 1, 2, 3]').elts[:3].copy().src
        '[0, 1, 2]'

        >>> FST('[0, 1, 2, 3]').elts[-3:]
        <<List ROOT 0,0..0,12>.elts[1:4] [<Constant 0,4..0,5>, <Constant 0,7..0,8>, <Constant 0,10..0,11>]>

        >>> FST('def fun(): pass\nclass cls: pass\nvar = val').body[1]
        <ClassDef 1,0..1,15>

        >>> FST('global a, b, c').names
        <<Global ROOT 0,0..0,14>.names ['a', 'b', 'c']>

        >>> FST('global a, b, c').names[1]
        'b'

        @public
        """

        start, stop, _ = self._get_indices()

        if isinstance(idx, slice):
            if idx.step is not None:
                raise IndexError('step slicing not supported')

            idx_start, idx_stop = fixup_slice_indices(stop - start, idx.start or 0,
                                                      'end' if (i := idx.stop) is None else i)

            return self.__class__(self.base, self.field, start + idx_start, start + idx_stop)

        assert isinstance(idx, int)

        idx = fixup_one_index(stop - start, idx)

        return a.f if isinstance(a := self._deref_one(start + idx), AST) else a

    def __setitem__(self, idx: int | slice, code: Code | None) -> None:
        """Set a single item or a slice view in this slice view. All indices (including negative) are relative to the
        bounds of this view.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when assigning
        values.

        **Parameters:**
        - `idx`: The index or `slice` where to put the element(s).

        **Examples:**

        >>> from fst import FST

        >>> (f := FST('[0, 1, 2, 3]')).elts[1] = '4'; f.src
        '[0, 4, 2, 3]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[:3] = '[5]'; f.src
        '[[5], 3]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[:3] = '5'; f.src
        '[5, 3]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[:3] = '5,'; f.src
        '[5, 3]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[-3:] = '[6]'; f.src
        '[0, [6]]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[-3:] = '6'; f.src
        '[0, 6]'

        >>> (f := FST('[0, 1, 2, 3]')).elts[:] = '7, 8'; f.src
        '[7, 8]'

        >>> f = FST('[0, 1, 2, 3]')
        >>> f.elts[2:2] = f.elts[1:3].copy()
        >>> f.src
        '[0, 1, 1, 2, 2, 3]'

        @public
        """

        start, stop, len_before = self._get_indices()

        if isinstance(idx, slice):
            if idx.step is not None:
                raise IndexError('step slicing not supported')

            idx_start, idx_stop = fixup_slice_indices(stop - start, idx.start or 0,
                                                      'end' if (i := idx.stop) is None else i)

            self.base = self.base._put_slice(code, start + idx_start, start + idx_stop, self.field)

            if self._stop is not None:
                self._stop += self._len_field() - len_before

            return

        assert isinstance(idx, int)

        idx = fixup_one_index(stop - start, idx)

        self.base = self.base._put_one(code, start + idx, self.field, ret_child=False)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

    def __delitem__(self, idx: int | slice) -> None:
        """Delete a single item or a slice from this slice view. All indices (including negative) are relative to the
        bounds of this view.

        Note that `fstview` can also hold references to non-AST lists of items, so keep this in mind when assigning
        values.

        **Parameters:**
        - `idx`: The index or `slice` to delete.

        **Examples:**

        >>> from fst import FST

        >>> del (f := FST('[0, 1, 2, 3]')).elts[1]; f.src
        '[0, 2, 3]'

        >>> del (f := FST('[0, 1, 2, 3]')).elts[:3]; f.src
        '[3]'

        >>> del (f := FST('[0, 1, 2, 3]')).elts[-3:]; f.src
        '[0]'

        >>> del (f := FST('[0, 1, 2, 3]')).elts[:]; f.src
        '[]'

        @public
        """

        start, stop, _ = self._get_indices()

        if isinstance(idx, slice):
            if idx.step is not None:
                raise IndexError('step slicing not supported')

            idx_start, idx_stop = fixup_slice_indices(stop - start, idx.start or 0,
                                                      'end' if (i := idx.stop) is None else i)

            self.base = self.base._put_slice(None, start + idx_start, start + idx_stop, self.field)

            if self._stop is not None:
                self._stop = max(start, stop - (idx_stop - idx_start))

            return

        assert isinstance(idx, int)

        idx = fixup_one_index(stop - start, idx)

        self.base = self.base._put_slice(None, start + idx, start + idx + 1, self.field)

        if self._stop is not None:
            self._stop = max(start, stop - 1)

    def copy(self, **options) -> fst.FST:
        """Copy this slice to a new top-level tree, dedenting and fixing as necessary.

        **Parameters:**
        - `options`: See `fst.fst.FST.options()`.

        **Returns:**
        - `FST`: Copied slice.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1:3].copy().src
        '[1, 2]'
        """

        check_options(options)

        start, stop, _ = self._get_indices()

        return self.base.get_slice(start, stop, self.field, cut=False, **options)

    def cut(self, **options) -> fst.FST:
        """Cut out this slice to a new top-level tree (if possible), dedenting and fixing as necessary. Cannot cut root
        node.

        **Parameters:**
        - `options`: See `fst.fst.FST.options()`.

        **Returns:**
        - `FST`: Cut slice.

        **Examples:**

        >>> from fst import FST

        >>> (f := FST('[0, 1, 2, 3]')).elts[1:3].cut().src
        '[1, 2]'
        >>> f.src
        '[0, 3]'
        """

        check_options(options)

        start, stop, _ = self._get_indices()

        f = self.base._get_slice(start, stop, self.field, True, options)

        if self._stop is not None:
            self._stop = start

        return f

    def replace(self, code: Code | None, one: bool | None = True, **options) -> fstview:  # -> self, self.base could disappear due to raw reparse
        """Replace or delete (if `code=None`) this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to put. `None` to delete this slice.
        - `one`: If `True` then will replace the range of this slice with a single item. Otherwise `False` will attempt
            a slice replacement (type must be compatible).
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1:3].replace('(4, 5)').base.src
        '[0, (4, 5), 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].replace('4, 5').base.src
        '[0, (4, 5), 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].replace('(4, 5)', one=False).base.src
        '[0, (4, 5), 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].replace('4, 5', one=False).base.src
        '[0, 4, 5, 3]'
        """

        check_options(options)

        start, stop, len_before = self._get_indices()

        self.base = self.base._put_slice(code, start, stop, self.field, one, options)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

        return self

    def remove(self, **options) -> fstview:  # -> self, self.base could disappear due to raw reparse
        """Delete this slice, equivalent to `replace(None, ...)`

        **Parameters:**
        - `options`: See `fst.fst.FST.options()`.

        **Returns:**
        - `self`

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1:3].remove().base.src
        '[0, 3]'
        """

        check_options(options)

        start, stop, len_before = self._get_indices()

        self.base = self.base._put_slice(None, start, stop, self.field, True, options)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

        return self

    def insert(self, code: Code, idx: int | Literal['end'] = 0, *, one: bool | None = True, **options) -> fstview:  # -> self, self.base could disappear due to raw reparse
        """Insert into this slice at a specific index.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to insert.
        - `idx`: Index to insert before. Can be `'end'` to indicate add at end of slice.
        - `one`: If `True` then will insert `code` as a single item. Otherwise `False` will attempt a slice insertion
            (type must be compatible).
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.insert('4, 5', 1).base.src
        '[0, (4, 5), 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 1).base.src
        '[0, (4, 5), 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts.insert('4, 5', 'end', one=False).base.src
        '[0, 1, 2, 3, 4, 5]'

        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 'end', one=False).base.src
        '[0, 1, 2, 3, (4, 5)]'

        >>> # same as 'end' but 'end' is always 'end'
        >>> FST('[0, 1, 2, 3]').elts.insert('4, 5', 4, one=False).base.src
        '[0, 1, 2, 3, 4, 5]'

        >>> FST('[0, 1, 2, 3]').elts.insert('(4, 5)', 4, one=False).base.src
        '[0, 1, 2, 3, (4, 5)]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].insert('*star').base.src
        '[0, *star, 1, 2, 3]'
        """

        check_options(options)

        start, stop, len_before = self._get_indices()
        len_view = stop - start

        if idx == 'end' or idx > len_view:
            idx = stop
        else:
            idx = start + (idx if idx >= 0 else max(0, idx + len_view))

        self.base = self.base._put_slice(code, idx, idx, self.field, one, options)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

        return self

    def append(self, code: Code, **options) -> fstview:  # -> self, self.base could disappear due to raw reparse
        """Append `code` as a single element to the end of this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to append.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.append('(4, 5)').base.src
        '[0, 1, 2, 3, (4, 5)]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].append('*star').base.src
        '[0, 1, 2, *star, 3]'
        """

        check_options(options)

        _, stop, _ = self._get_indices()

        self.base = self.base._put_slice(code, stop, stop, self.field, True, options)

        if self._stop is not None:
            self._stop = stop + 1

        return self

    def extend(self, code: Code, one: Literal[False] | None = False, **options) -> fstview:  # -> self, self.base could disappear due to raw reparse
        """Extend this slice with the slice in `code` (type must be compatible).

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` slice to extend.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.extend('4, 5').base.src
        '[0, 1, 2, 3, 4, 5]'

        >>> FST('[0, 1, 2, 3]').elts.extend('(4, 5)').base.src
        '[0, 1, 2, 3, (4, 5)]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].extend('4, 5').base.src
        '[0, 1, 2, 4, 5, 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].extend('(4, 5)').base.src
        '[0, 1, 2, (4, 5), 3]'
        """

        check_options(options)

        _, stop, len_before = self._get_indices()

        self.base = self.base._put_slice(code, stop, stop, self.field, None if one is None else False, options)

        if self._stop is not None:
            self._stop = stop + (self._len_field() - len_before)

        return self

    def prepend(self, code: Code, **options) -> fstview:  # -> self, self.base could disappear due to raw reparse
        """prepend `code` as a single element to the beginning of this slice.

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to preappend.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.prepend('(4, 5)').base.src
        '[(4, 5), 0, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].prepend('*star').base.src
        '[0, *star, 1, 2, 3]'
        """

        check_options(options)

        start, _, _ = self._get_indices()

        self.base = self.base._put_slice(code, start, start, self.field, True, options)

        if self._stop is not None:
            self._stop += 1

        return self

    def prextend(self, code: Code, one: Literal[False] | None = False, **options) -> fstview:  # -> self, self.base could disappear due to raw reparse
        """Extend the beginning of this slice with the slice in `code` (type must be compatible).

        **Returns:**
        - `self`

        **Parameters:**
        - `code`: `FST`, `AST` or source `str` or `list[str]` to extend at the start.
        - `options`: See `fst.fst.FST.options()`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts.prextend('4, 5').base.src
        '[4, 5, 0, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts.prextend('(4, 5)').base.src
        '[(4, 5), 0, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].prextend('4, 5').base.src
        '[0, 4, 5, 1, 2, 3]'

        >>> FST('[0, 1, 2, 3]').elts[1:3].prextend('(4, 5)').base.src
        '[0, (4, 5), 1, 2, 3]'
        """

        check_options(options)

        start, _, len_before = self._get_indices()

        self.base = self.base._put_slice(code, start, start, self.field, None if one is None else False, options)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

        return self


class fstview_Dict(fstview):
    """View for `Dict` combined `key:value` virtual field `_all`. @private"""

    def _len_field(self) -> int:
        return len(self.base.a.keys)

    def _deref_one(self, idx: int) -> AST | str:
        return fstview_Dict(self.base, '_all', idx, idx + 1)

    def __repr__(self) -> str:
        start, stop, _ = self._get_indices()
        indices = f'[{start or ""}:{stop}]' if self._stop is not None else f'[{start}:]' if start else ''
        base = self.base
        ast = base.a
        keys = ast.keys[start : stop]
        values = ast.values[start : stop]

        seq = ', '.join(f'{f"{k.f}: " if k else "**"}{v.f}' for k, v in zip(keys, values, strict=True))

        return f'<{base!r}._all{indices} {{{seq}}}>'


class fstview_MatchMapping(fstview):
    """View for `MatchMapping` combined `key:pattern + rest` virtual field `_all`. @private"""

    def _len_field(self) -> int:
        return len((a := self.base.a).keys) + bool(a.rest)

    def _deref_one(self, idx: int) -> AST | str:
        return fstview_MatchMapping(self.base, '_all', idx, idx + 1)

    def __repr__(self) -> str:
        start, stop, _ = self._get_indices()
        indices = f'[{start or ""}:{stop}]' if self._stop is not None else f'[{start}:]' if start else ''
        base = self.base
        ast = base.a
        patterns = ast.patterns

        seq = [f'{k.f}: {p.f}' for k, p in zip(ast.keys[start : stop], patterns[start : stop], strict=True)]

        if (rest := ast.rest) and stop > len(patterns):
            seq.append('**' + rest)

        seq = ', '.join(seq)

        return f'<{base!r}._all{indices} {{{seq}}}>'


class fstview_Compare(fstview):
    """View for `Compare` combined `left + comparators` virtual field `_all`. @private"""

    def _len_field(self) -> int:
        return 1 + len(self.base.a.comparators)

    def _deref_one(self, idx: int) -> AST | str:
        return self.base.a.comparators[idx - 1] if idx else self.base.a.left

    def __repr__(self) -> str:
        start, stop, _ = self._get_indices()
        indices = f'[{start or ""}:{stop}]' if self._stop is not None else f'[{start}:]' if start else ''
        base = self.base
        ast = base.a
        start_1 = max(0, start - 1)
        stop_1 = max(0, stop - 1)
        comparators = ast.comparators[start_1 : stop_1]

        if start:
            left = comparators.pop(0) if comparators else None
            ops = ast.ops[start : stop_1]

        else:
            left = ast.left
            ops = ast.ops[start_1 : stop_1]

        seq = [f' {OPCLS2STR[o.__class__]} {c.f}' for o, c in zip(ops, comparators, strict=True)]

        if left:
            seq.insert(0, repr(left.f))

        return f'<{base!r}._all{indices} {"".join(seq)}>'


class fstview_arguments(fstview):
    """View for `arguments` merged `posonlyargs+args+vararg+kwonlyargs+kwarg` virtual field `_all`. @private"""

    def _len_field(self) -> int:
        return len(self.base._cached_allargs())

    def _deref_one(self, idx: int) -> AST | str:
        return fstview_arguments(self.base, '_all', idx, idx + 1)

    def __repr__(self) -> str:
        start, stop, _ = self._get_indices()
        indices = f'[{start or ""}:{stop}]' if self._stop is not None else f'[{start}:]' if start else ''
        base = self.base
        seq = []

        for a in base._cached_allargs()[start : stop]:
            if (g := (f := a.f).next()) and g.pfield.name in ('defaults', 'kw_defaults'):
                seq.append(f'{f}={g}')
            else:
                seq.append(str(f))

        return f'<{base!r}._all{indices} {", ".join(seq)}>'


class fstview__body(fstview):
    """View for `_body` virtual field, only used on node types that can have a docstring. @private"""

    def _len_field(self) -> int:
        base = self.base

        return len(base.a.body) - base.has_docstr

    def _deref_one(self, idx: int) -> AST | str:
        base = self.base

        return base.a.body[idx + base.has_docstr]


class fstview_arglikes(fstview):
    """View for `Call` merged `args+keywords` virtual field `_args` or `ClassDef` merged `bases+keywords` virtual field
    `_bases`. @private"""

    def _len_field(self) -> int:
        ast = self.base.a

        return len(getattr(ast, self.field[1:])) + len(ast.keywords)

    def _deref_one(self, idx: int) -> AST | str:
        return self.base._cached_arglikes()[idx]

    def __repr__(self) -> str:
        start, stop, _ = self._get_indices()
        indices = f'[{start or ""}:{stop}]' if self._stop is not None else f'[{start}:]' if start else ''
        base = self.base

        return f'<{base!r}._{self.field}{indices} {tuple(a.f for a in base._cached_arglikes()[start : stop])}>'


class fstview_dummy(fstview):
    """Dummy view for nonexistent fields (type_params on py < 3.12). @private"""

    def _len_field(self) -> int:
        return 0

    def __repr__(self) -> str:
        return f'<{self.base!r}.{self.field} DUMMY VIEW>'

    def __getitem__(self, idx: int | slice) -> fstview | fst.FST | str | None:
        if not isinstance(idx, slice):
            raise IndexError('cannot get items from a dummy view')

        return self

    def __setitem__(self, idx: int | slice, code: Code | None) -> None:
        if not isinstance(idx, slice):
            raise IndexError('cannot set items in a dummy view')
        if code is not None:
            raise RuntimeError('cannot set items in a dummy view')

    def __delitem__(self, idx: int | slice) -> None:
        if not isinstance(idx, slice):
            raise IndexError('index out of range on dummy view')

    def copy(self, **options) -> fst.FST:
        raise RuntimeError('cannot copy a dummy view')

    def cut(self, **options) -> fst.FST:
        raise RuntimeError('cannot cut a dummy view')

    def replace(self, code: Code | None, one: bool | None = True, **options) -> fstview:
        if code is not None:
            raise RuntimeError('cannot replace a dummy view')

        return self

    def remove(self, **options) -> fstview:
        return self

    def insert(self, code: Code, idx: int | Literal['end'] = 0, one: bool | None = True, **options) -> fstview:
        if code is not None:
            raise RuntimeError('cannot insert to a dummy view')

        return self

    def append(self, code: Code, **options) -> fstview:
        if code is not None:
            raise RuntimeError('cannot append to a dummy view')

        return self

    def extend(self, code: Code, one: Literal[False] | None = False, **options) -> fstview:
        if code is not None:
            raise RuntimeError('cannot extend a dummy view')

        return self

    def prepend(self, code: Code, **options) -> fstview:
        if code is not None:
            raise RuntimeError('cannot prepend to a dummy view')

        return self

    def prextend(self, code: Code, one: Literal[False] | None = False, **options) -> fstview:
        if code is not None:
            raise RuntimeError('cannot prextend a dummy view')

        return self
