"""Slice-access views on `FST` lists of children."""

from __future__ import annotations

from builtins import slice
from typing import Literal

from . import fst

from .asttypes import ASTS_LEAF_BLOCK_OR_MOD
from .astutil import AST
from .common import fstloc, fstlocn
from .code import Code
from .fst_misc import fixup_one_index, fixup_slice_indices
from .fst_options import check_options

__all__ = [
    'FSTView',
    'FSTView_Dict',
    'FSTView_MatchMapping',
    'FSTView_Compare',
    'FSTView_arguments',
    'FSTView__body',
    'FSTView_arglikes',
    'FSTView_Global_Nonlocal',
    'FSTView_dummy',
]


class FSTView:
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
    <<List ROOT 0,0..0,6>.elts>

    >>> view[1:].cut()
    <List ROOT 0,0..0,3>

    >>> view
    <<List ROOT 0,0..0,3>.elts>

    This object is meant to be, and is normally created automatically by accessing `AST` list fields on an `FST` node.

    **Examples:**

    >>> from fst import FST

    >>> f = FST('[0, 1, 2, 3]')
    >>> f
    <List ROOT 0,0..0,12>

    >>> f.elts
    <<List ROOT 0,0..0,12>.elts>

    >>> f.elts[1]
    <Constant 0,4..0,5>

    >>> f.elts[1].src
    '1'

    >>> f.elts[1:3]
    <<List ROOT 0,0..0,12>.elts[1:3]>

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

    base:   fst.FST     ; """The target `FST` node this view references (the container)."""
    field:  str         ; """The target field this view references. Can be virtual field like `_all`."""
    _start: int         ; """Start position within the target field list this view references."""
    _stop:  int | None  ; """One past the last element within the target field list this view references. `None` means 'end', pinned the end of the field whatever it may be."""

    is_FST = False  ; """Allows to quickly differentiate between actual `FST` nodes vs. views or locations."""  # for quick checks vs. `FST`
    is_deref_FST = True  ; """Whether single item indexing on this view yields an `FST` node or not. Where this is not the case are multi-node sequences like a `Dict`, `MatchMapping` and `arguments` or string sequences like `Global` and `Nonlocal`. Dereferencing these views will not give individual nodes or values but rather another `FSTView`."""

    @property
    def start(self) -> int:
        """Start position within the target field list this view references."""

        return self._base_indices()[0]

    @property
    def stop(self) -> int:
        """One past the last element within the target field list this view references."""

        return self._base_indices()[1]

    @property
    def start_and_stop(self) -> tuple[int, int]:
        """Start and stop positions within the target field list this view references."""

        return self._base_indices()[:2]

    @property
    def lines(self) -> list[str]:
        r"""Whole lines of this view from the **RAW SOURCE**, without any dedentation, may also contain parts of
        enclosing nodes. Will have indentation as it appears in the top level source if multiple lines.

        A valid list of strings is always returned, even for empty views. The lines list returned is always a copy so
        safe to modify.

        **Examples:**

        >>> from fst import *

        >>> FST('a\nb\nc\nd').body[1:3].lines
        ['b', 'c']
        """

        return self.base.root._lines[loc.ln : loc.end_ln + 1] if (loc := self.bloc) else ['']

    @property
    def src(self) -> str:
        """Source code of this view from the **RAW SOURCE** clipped out as a single string, without any dedentation.
        Will have indentation as it appears in the top level source if multiple lines.

        A string is always returned, even for empty views.

        **Examples:**

        >>> from fst import *

        >>> FST('[a, b, c, d]').elts[1:3].src
        'b, c'
        """

        return self.base._get_src(*loc) if (loc := self.bloc) else ''

    @property
    def loc(self) -> fstloc | None:
        """Zero based character indexed location of view (including parentheses and / or decorators where present)."""

        start, stop, _ = self._base_indices()

        if not (len_ := stop - start):
            return None
        if len_ == 1:
            return self._deref_one(start).f.pars()

        ln, col, _, _ = self._deref_one(start).f.pars()
        _, _, end_ln, end_col = self._deref_one(stop - 1).f.pars()

        return fstlocn(ln, col, end_ln, end_col, n=0)  # we return fstlocn for convenient sharing with pars()

    @property
    def ln(self) -> int | None:
        """Line number of the first line of this view (0 based)."""

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self._deref_one(start).f.pars().ln

    @property
    def col(self) -> int | None:  # char index
        """CHARACTER index of the start of this view (0 based)."""

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self._deref_one(start).f.pars().col

    @property
    def end_ln(self) -> int | None:  # 0 based
        """Line number of the LAST LINE of this view (0 based)."""

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self._deref_one(stop - 1).f.pars().end_ln

    @property
    def end_col(self) -> int | None:  # char index
        """CHARACTER index one past the end of this view (0 based)."""

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self._deref_one(stop - 1).f.pars().end_col

    bloc = loc
    bln = ln
    bcol = col
    bend_ln = end_ln
    bend_col = end_col

    def pars(self, *, shared: bool | None = True) -> fstlocn | None:
        """Convenience function just returns the `.loc` of this view, as it will already have parentheses included.

        **Parameters:**
        - IGNORED!

        **Returns:**
        - `fstlocn`: Full location of view from first element to last, if elements present.
        - `None`: If view is empty.

        **Examples:**

        >>> from fst import *

        >>> FST('[a, b, c, d]').elts[1:3].pars()
        fstlocn(0, 4, 0, 8, n=0)

        >>> FST('[(a), (b), (c), (d)]').elts[1:3].pars()
        fstlocn(0, 6, 0, 14, n=0)
        """

        loc = self.loc

        if not loc or hasattr(loc, 'n'):  # could be `None`
            return loc

        ln, col, end_ln, end_col = loc

        return fstlocn(ln, col, end_ln, end_col, n=0)  # pars() return must have an `n`

    def _len_field(self) -> int:
        """Length of full base `FST` field, irrespective of view `start` and `stop`."""

        return len(getattr(self.base.a, self.field))

    def _deref_one(self, idx: int) -> AST | str:
        """Return a single element from field (which may not be a contiguous list). `idx` is the real index already
        absolute (offset by any `start`) and is guaranteed to be positive and valid. NO COPY, JUST RETURN NODE. Can
        return `AST` or primitive or another `FSTView` if base field is multinode."""

        return getattr(self.base.a, self.field)[idx]

    def _base_indices(self) -> tuple[int, int, int]:
        """Refresh indices in case of field length change anywhere else and return adjusted REAL indices in REAL `base`
        field with full length of that REAL field.

        **Returns:**
        - `(start, stop, len_field)`: Good start and stop REAL indices in the REAL field and full length of that REAL
            field currently.
        """

        len_field = self._len_field()

        if (stop := self._stop) is None:
            stop = len_field
        elif stop > len_field:
            stop = self._stop = len_field

        if (start := self._start) > stop:
            start = self._start = stop

        return start, stop, len_field

    def _fixup_item_indices(self, idx: int | slice | str) -> tuple[int, int, int, int, int | None]:
        """Convert the index passed to a __???item__() function to proper index or indices depending on if individual or
        slice operation. Also handled a `str` name lookup, which can return the index in this view if is a direct child
        or the grand+ child node itself if is not. `find_def()` is used for this.

        **Parameters:**
        - `idx`: The index or `slice` where to get the element(s) from. Or a `str` for a single-element name search.

        **Returns:**
        - `(start, stop, len_field, idx_start | FST, idx_stop | None)`:
            - `start`, `stop` and `len_field`: These come from `_base_indices()`.
            - `idx_stop`: If `None` it indicates a single-element operation. Otherwise this and `idx_start` are the
                indices from a `slice` object fixed up for the bounds of this view for a slice operation, including
                converting `None` elements to the proper `int` bounds.
            - `idx_start`: If `int` then is an index for either slice or single element operation on elements of this
                view. If is an `FST` node then it was gotten from a `find_def()` on a string name search and is not
                a direct child of this view so safe to do whatever operation on it without updating `self`. If a `str`
                name search results in an element of this view then it is returned as an `int` index instead.
        """

        start, stop, len_field = self._base_indices()

        if isinstance(idx, slice):
            if idx.step is not None:
                raise IndexError('step slicing not supported')

            idx_start, idx_stop = fixup_slice_indices(stop - start, idx.start or 0,
                                                      'end' if (i := idx.stop) is None else i)

            return start, stop, len_field, idx_start, idx_stop

        if isinstance(idx, int):
            idx = fixup_one_index(stop - start, idx)

            return start, stop, len_field, idx, None

        if isinstance(idx, str):  # this is very handy so we allow search for function or class in single-element indexing
            base = self.base
            field = self.field
            ast = base.a

            if ast.__class__ not in ASTS_LEAF_BLOCK_OR_MOD or field not in ('body', '_body', 'orelse', 'finalbody'):
                raise IndexError(f'name indexing not supported on {ast.__class__.__name__}.{field}')

            if field == '_body':  # special casing a specific subclass FSTView__body behavior here to keep things simple, this is less ugly than abstracting it
                field = 'body'
                idx_off = base.has_docstr
            else:
                idx_off = 0

            asts = getattr(ast, field)[start + idx_off : stop + idx_off]
            found = base.find_def(idx, asts=asts)

            if not found:
                raise IndexError(f'name index {idx!r} not found')

            if found.parent is base:  # direct child so we return its index in the view
                return start, stop, len_field, found.pfield.idx - start - idx_off, None

            return start, stop, len_field, found, None

        raise IndexError(f'invalid index {idx!r}')

    def __init__(self, base: fst.FST, field: str, start: int = 0, stop: int | None = None) -> None:
        """@private"""

        self.base = base
        self.field = field
        self._start = start
        self._stop = stop

    def __repr__(self) -> str:
        start, stop, _ = self._base_indices()
        indices = f'[{start or ""}:{stop}]' if self._stop is not None else f'[{start}:]' if start else ''

        return f'<{self.base!r}.{self.field}{indices}>'

    def __len__(self) -> int:
        start, stop, _ = self._base_indices()

        return stop - start

    def __getitem__(self, idx: int | slice | str) -> FSTView | fst.FST | str | None:
        r"""Get a single item or a slice view from this slice view. All indices (including negative) are relative to the
        bounds of this view. This is just an access, not a cut or a copy, so if you want a copy you must explicitly do
        `.copy()` on the returned value.

        Note that `FSTView` can also hold references to non-AST lists of items, so keep this in mind when dealing with
        return values which may be `None` or may not be `FST` nodes.

        **Parameters:**
        - `idx`: The index or `slice` where to get the element(s) from. Or a `str` for a single-element name search.

        **Returns:**
        - `FSTView | FST | str | None`: Either a single `FST` node if accessing a single item or a new `FSTView` view
            according to the slice passed. `str` can also be returned from a view of `Global.names` or `None` from a
            `Dict.keys`.

        **Examples:**

        >>> from fst import FST

        >>> FST('[0, 1, 2, 3]').elts[1].src
        '1'

        >>> FST('[0, 1, 2, 3]').elts[:3]
        <<List ROOT 0,0..0,12>.elts[:3]>

        >>> FST('[0, 1, 2, 3]').elts[:3].copy().src
        '[0, 1, 2]'

        >>> FST('[0, 1, 2, 3]').elts[-3:]
        <<List ROOT 0,0..0,12>.elts[1:4]>

        >>> FST('def fun(): pass\nclass cls: pass\nvar = val').body[1]
        <ClassDef 1,0..1,15>

        >>> FST('global a, b, c').names
        <<Global ROOT 0,0..0,14>.names>

        If indexing a single element does not give an `FST` node then it will give another `FSTView`.

        >>> FST('global a, b, c').names[1]
        <<Global ROOT 0,0..0,14>.names[1:2]>

        @public
        """

        start, _, _, idx_start, idx_stop = self._fixup_item_indices(idx)

        if idx_stop is not None:  # slice
            return self.__class__(self.base, self.field, start + idx_start, start + idx_stop)

        if not isinstance(idx_start, fst.FST):  # single element child of this view
            return a.f if isinstance(a := self._deref_one(start + idx_start), AST) else a

        return idx_start  # the actual node found for the str search

    def __setitem__(self, idx: int | slice | str, code: Code | None) -> None:
        """Set a single item or a slice view in this slice view. All indices (including negative) are relative to the
        bounds of this view.

        Note that `FSTView` can also hold references to non-AST lists of items, so keep this in mind when assigning
        values.

        **Parameters:**
        - `idx`: The index or `slice` where to put the element(s). Or a `str` for a single-element name search.

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

        start, _, len_before, idx_start, idx_stop = self._fixup_item_indices(idx)

        if idx_stop is not None:  # slice
            self.base = self.base._put_slice(code, start + idx_start, start + idx_stop, self.field)

            if self._stop is not None:
                self._stop += self._len_field() - len_before

        elif not isinstance(idx_start, fst.FST):  # single element child of this view
            self.base = self.base._put_one(code, start + idx_start, self.field, ret_child=False)

            if self._stop is not None:
                self._stop += self._len_field() - len_before

        else:  # the actual node found for the str search
            idx_start.replace(code)

    def __delitem__(self, idx: int | slice | str) -> None:
        """Delete a single item or a slice from this slice view. All indices (including negative) are relative to the
        bounds of this view.

        Note that `FSTView` can also hold references to non-AST lists of items, so keep this in mind when assigning
        values.

        **Parameters:**
        - `idx`: The index or `slice` to delete. Or a `str` for a single-element name search.

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

        start, stop, _, idx_start, idx_stop = self._fixup_item_indices(idx)

        if idx_stop is not None:  # slice
            self.base = self.base._put_slice(None, start + idx_start, start + idx_stop, self.field)

            if self._stop is not None:
                self._stop = max(start, stop - (idx_stop - idx_start))

            return

        elif not isinstance(idx_start, fst.FST):  # single element child of this view
            self.base = self.base._put_slice(None, start + idx_start, start + idx_start + 1, self.field)

            if self._stop is not None:
                self._stop = max(start, stop - 1)

        else:  # the actual node found for the str search
            idx_start.remove()

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

        start, stop, _ = self._base_indices()

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

        start, stop, _ = self._base_indices()

        f = self.base._get_slice(start, stop, self.field, True, options)

        if self._stop is not None:
            self._stop = start

        return f

    def replace(self, code: Code | None, one: bool | None = True, **options) -> FSTView:  # -> self, self.base could disappear due to raw reparse
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

        start, stop, len_before = self._base_indices()

        self.base = self.base._put_slice(code, start, stop, self.field, one, options)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

        return self

    def remove(self, **options) -> FSTView:  # -> self, self.base could disappear due to raw reparse
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

        start, stop, len_before = self._base_indices()

        self.base = self.base._put_slice(None, start, stop, self.field, True, options)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

        return self

    def insert(self, code: Code, idx: int | Literal['end'] = 0, *, one: bool | None = True, **options) -> FSTView:  # -> self, self.base could disappear due to raw reparse
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

        start, stop, len_before = self._base_indices()
        len_view = stop - start

        if idx == 'end' or idx > len_view:
            idx = stop
        else:
            idx = start + (idx if idx >= 0 else max(0, idx + len_view))

        self.base = self.base._put_slice(code, idx, idx, self.field, one, options)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

        return self

    def append(self, code: Code, **options) -> FSTView:  # -> self, self.base could disappear due to raw reparse
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

        _, stop, _ = self._base_indices()

        self.base = self.base._put_slice(code, stop, stop, self.field, True, options)

        if self._stop is not None:
            self._stop = stop + 1

        return self

    def extend(self, code: Code, one: Literal[False] | None = False, **options) -> FSTView:  # -> self, self.base could disappear due to raw reparse
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

        _, stop, len_before = self._base_indices()

        self.base = self.base._put_slice(code, stop, stop, self.field, None if one is None else False, options)

        if self._stop is not None:
            self._stop = stop + (self._len_field() - len_before)

        return self

    def prepend(self, code: Code, **options) -> FSTView:  # -> self, self.base could disappear due to raw reparse
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

        start, _, _ = self._base_indices()

        self.base = self.base._put_slice(code, start, start, self.field, True, options)

        if self._stop is not None:
            self._stop += 1

        return self

    def prextend(self, code: Code, one: Literal[False] | None = False, **options) -> FSTView:  # -> self, self.base could disappear due to raw reparse
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

        start, _, len_before = self._base_indices()

        self.base = self.base._put_slice(code, start, start, self.field, None if one is None else False, options)

        if self._stop is not None:
            self._stop += self._len_field() - len_before

        return self


class FSTView_Dict(FSTView):
    """View for `Dict` combined `key:value` virtual field `_all`. @private"""

    is_deref_FST = False

    @property
    def loc(self) -> fstloc | None:
        r"""Zero based character indexed location of view (including parentheses and or decorators where present).

        **Examples:**

        >>> from fst import *

        >>> f = FST('{(a):\n(b),\n**\n (c)}')

        >>> f._all.loc
        fstlocn(0, 1, 3, 4, n=0)

        >>> f._all[0].loc
        fstlocn(0, 1, 1, 3, n=0)

        >>> f._all[1].loc
        fstlocn(2, 0, 3, 4, n=0)
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        base = self.base
        ln, col, _, _ = base._loc_maybe_key(start)
        _, _, end_ln, end_col = base.a.values[stop - 1].f.pars()

        return fstlocn(ln, col, end_ln, end_col, n=0)  # we return fstlocn for convenient sharing with pars()

    @property
    def ln(self) -> int | None:
        r"""Line number of the first line of this view (0 based).

        >>> from fst import *

        >>> f = FST('{(a):\n(b),\n**\n (c)}')

        >>> f._all[0].ln
        0

        >>> f._all[1].ln
        2
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._loc_maybe_key(start).ln

    @property
    def col(self) -> int | None:  # char index
        r"""CHARACTER index of the start of this view (0 based).

        >>> from fst import *

        >>> f = FST('{(a):\n(b),\n**\n (c)}')

        >>> f._all[0].col
        1

        >>> f._all[1].col
        0
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._loc_maybe_key(start).col

    @property
    def end_ln(self) -> int | None:  # 0 based
        r"""Line number of the LAST LINE of this view (0 based).

        >>> from fst import *

        >>> f = FST('{(a):\n(b),\n**\n (c)}')

        >>> f._all[0].end_ln
        1

        >>> f._all[1].end_ln
        3
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base.a.values[stop - 1].f.pars().end_ln

    @property
    def end_col(self) -> int | None:  # char index
        r"""CHARACTER index one past the end of this view (0 based).

        >>> from fst import *

        >>> f = FST('{(a):\n(b),\n**\n (c)}')

        >>> f._all[0].end_col
        3

        >>> f._all[1].end_col
        4
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base.a.values[stop - 1].f.pars().end_col

    bloc = loc
    bln = ln
    bcol = col
    bend_ln = end_ln
    bend_col = end_col

    def _len_field(self) -> int:
        return len(self.base.a.keys)

    def _deref_one(self, idx: int) -> AST | str:
        return FSTView_Dict(self.base, '_all', idx, idx + 1)


class FSTView_MatchMapping(FSTView):
    """View for `MatchMapping` combined `key:pattern + rest` virtual field `_all`. @private"""

    is_deref_FST = False

    @property
    def loc(self) -> fstloc | None:
        r"""Zero based character indexed location of view (including parentheses and or decorators where present).

        **Examples:**

        >>> from fst import *

        >>> f = FST('{1:\n(a),\n**\n b}', 'pattern')

        >>> f._all.loc
        fstlocn(0, 1, 3, 2, n=0)

        >>> f._all[0].loc
        fstlocn(0, 1, 1, 3, n=0)

        >>> f._all[1].loc
        fstloc(2, 0, 3, 2)
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        base = self.base
        ast = base.a
        patterns = ast.patterns

        if stop > len(patterns):  # means there is a .rest
            if stop == start + 1:
                return base._loc_MatchMapping_rest(True)

            _, _, end_ln, end_col = base._loc_MatchMapping_rest()

        else:
            _, _, end_ln, end_col = patterns[stop - 1].f.pars()

        ln, col, _, _ = ast.keys[start].f.loc

        return fstlocn(ln, col, end_ln, end_col, n=0)

    @property
    def ln(self) -> int | None:
        r"""Line number of the first line of this view (0 based).

        >>> from fst import *

        >>> f = FST('{1:\n(a),\n**\n b}', 'pattern')

        >>> f._all[0].ln
        0

        >>> f._all[1].ln
        2
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        base = self.base
        ast = base.a

        if start == len(ast.patterns):  # means starts on .rest
            return base._loc_MatchMapping_rest(True).ln

        return ast.keys[start].f.loc.ln

    @property
    def col(self) -> int | None:  # char index
        r"""CHARACTER index of the start of this view (0 based).

        >>> from fst import *

        >>> f = FST('{1:\n(a),\n**\n b}', 'pattern')

        >>> f._all[0].col
        1

        >>> f._all[1].col
        0
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        base = self.base
        ast = base.a

        if start == len(ast.patterns):  # means starts on .rest
            return base._loc_MatchMapping_rest(True).col

        return ast.keys[start].f.loc.col

    @property
    def end_ln(self) -> int | None:  # 0 based
        r"""Line number of the LAST LINE of this view (0 based).

        >>> from fst import *

        >>> f = FST('{1:\n(a),\n**\n b}', 'pattern')

        >>> f._all[0].end_ln
        1

        >>> f._all[1].end_ln
        3
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        base = self.base
        patterns = base.a.patterns

        if stop > len(patterns):  # means there is a .rest
            return base._loc_MatchMapping_rest().end_ln

        return patterns[stop - 1].f.pars().end_ln

    @property
    def end_col(self) -> int | None:  # char index
        r"""CHARACTER index one past the end of this view (0 based).

        >>> from fst import *

        >>> f = FST('{1:\n(a),\n**\n b}', 'pattern')

        >>> f._all[0].end_col
        3

        >>> f._all[1].end_col
        2
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        base = self.base
        patterns = base.a.patterns

        if stop > len(patterns):  # means there is a .rest
            return base._loc_MatchMapping_rest().end_col

        return patterns[stop - 1].f.pars().end_col

    bloc = loc
    bln = ln
    bcol = col
    bend_ln = end_ln
    bend_col = end_col

    @property
    def has_rest(self) -> bool:
        """Whether this slice contains the `rest` element or not."""

        _, stop, _ = self._base_indices()

        return stop > len(self.base.a.patterns)  # means there is a .rest

    def _len_field(self) -> int:
        return len((a := self.base.a).keys) + bool(a.rest)

    def _deref_one(self, idx: int) -> AST | str:
        return FSTView_MatchMapping(self.base, '_all', idx, idx + 1)


class FSTView_Compare(FSTView):
    """View for `Compare` combined `left + comparators` virtual field `_all`. @private"""

    def _len_field(self) -> int:
        return 1 + len(self.base.a.comparators)

    def _deref_one(self, idx: int) -> AST | str:
        return self.base.a.comparators[idx - 1] if idx else self.base.a.left


class FSTView_arguments(FSTView):
    """View for `arguments` merged `posonlyargs+args+vararg+kwonlyargs+kwarg` virtual field `_all`. This indexes on the
    `arguments` node `_cached_allargs()`. @private"""

    is_deref_FST = False

    @property
    def loc(self) -> fstloc | None:
        r"""Zero based character indexed location of view (including parentheses and or decorators where present).

        **Examples:**

        >>> from fst import *

        >>> args = FST('a=1, /,\n b=2,\n  *c: int,\n   d=3,\n    **e', 'arguments')

        >>> args._all.loc
        fstlocn(0, 0, 4, 7, n=0)

        >>> args._all[0].loc
        fstlocn(0, 0, 0, 3, n=0)

        >>> args._all[:2].loc
        fstlocn(0, 0, 1, 4, n=0)

        >>> args._all[2].loc
        fstlocn(2, 2, 2, 9, n=0)

        >>> args._all[3].loc
        fstlocn(3, 3, 3, 6, n=0)

        >>> args._all[-1].loc
        fstlocn(4, 4, 4, 7, n=0)

        >>> args._all[1:-1].loc
        fstlocn(1, 1, 3, 6, n=0)
        """

        start, stop, _ = self._base_indices()

        if not (len_ := stop - start):
            return None

        allargs = self.base._cached_allargs()

        if len_ == 1:
            ln, col, end_ln, end_col = allargs[start].f._loc_argument(True)  # we don't return this directly because it may have a `default` in it

        else:
            ln, col, _, _ = allargs[start].f._loc_argument().loc
            _, _, end_ln, end_col = allargs[stop - 1].f._loc_argument(True, False).loc

        return fstlocn(ln, col, end_ln, end_col, n=0)  # we return fstlocn for convenient sharing with pars()

    @property
    def ln(self) -> int | None:
        r"""Line number of the first line of this view (0 based).

        >>> from fst import *

        >>> args = FST('a=1, /,\n b=2,\n  *c: int,\n   d=3,\n    **e', 'arguments')

        >>> args._all[0].ln
        0

        >>> args._all[1].ln
        1

        >>> args._all[2].ln
        2

        >>> args._all[3].ln
        3

        >>> args._all[4].ln
        4
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._cached_allargs()[start].f._loc_argument().ln

    @property
    def col(self) -> int | None:  # char index
        r"""CHARACTER index of the start of this view (0 based).

        >>> from fst import *

        >>> args = FST('a=1, /,\n b=2,\n  *c: int,\n   d=3,\n    **e', 'arguments')

        >>> args._all[0].col
        0

        >>> args._all[1].col
        1

        >>> args._all[2].col
        2

        >>> args._all[3].col
        3

        >>> args._all[4].col
        4
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._cached_allargs()[start].f._loc_argument().col

    @property
    def end_ln(self) -> int | None:  # 0 based
        r"""Line number of the LAST LINE of this view (0 based).

        >>> from fst import *

        >>> args = FST('a=1, /,\n b=2,\n  *c: int,\n   d=3,\n    **e', 'arguments')

        >>> args._all[0].end_ln
        0

        >>> args._all[1].end_ln
        1

        >>> args._all[2].end_ln
        2

        >>> args._all[3].end_ln
        3

        >>> args._all[4].end_ln
        4
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._cached_allargs()[stop - 1].f._loc_argument(True, False).end_ln

    @property
    def end_col(self) -> int | None:  # char index
        r"""CHARACTER index one past the end of this view (0 based).

        >>> from fst import *

        >>> args = FST('a=1, /,\n b=2,\n  *c: int,\n   d=3,\n    **e', 'arguments')

        >>> args._all[0].end_col
        3

        >>> args._all[1].end_col
        4

        >>> args._all[2].end_col
        9

        >>> args._all[3].end_col
        6

        >>> args._all[4].end_col
        7
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._cached_allargs()[stop - 1].f._loc_argument(True, False).end_col

    bloc = loc
    bln = ln
    bcol = col
    bend_ln = end_ln
    bend_col = end_col

    def _len_field(self) -> int:
        return len(self.base._cached_allargs())

    def _deref_one(self, idx: int) -> AST | str:
        return FSTView_arguments(self.base, '_all', idx, idx + 1)


class FSTView__body(FSTView):
    """View for `_body` virtual field, only used on node types that can have a docstring. @private"""

    def _len_field(self) -> int:
        base = self.base

        return len(base.a.body) - base.has_docstr

    def _deref_one(self, idx: int) -> AST | str:
        base = self.base

        return base.a.body[idx + base.has_docstr]


class FSTView_arglikes(FSTView):
    """View for `Call` merged `args+keywords` virtual field `_args` or `ClassDef` merged `bases+keywords` virtual field
    `_bases`. This indexes on the base node `_cached_arglikes()`. @private"""

    def _len_field(self) -> int:
        ast = self.base.a

        return len(getattr(ast, self.field[1:])) + len(ast.keywords)

    def _deref_one(self, idx: int) -> AST | str:
        return self.base._cached_arglikes()[idx]


class FSTView_Global_Nonlocal(FSTView):
    """For `Global` and `Nonlocal` to handle their non-`AST` fields correctly. @private"""

    is_deref_FST = False

    def _deref_one(self, idx: int) -> AST | str:
        return FSTView_Global_Nonlocal(self.base, 'names', idx, idx + 1)

    @property
    def loc(self) -> fstloc | None:
        r"""Zero based character indexed location of view (including parentheses and or decorators where present).

        **Examples:**

        >>> from fst import *

        >>> f = FST('global\\\na,\\\n b')

        >>> f.names.loc
        fstlocn(1, 0, 2, 2, n=0)

        >>> f.names[:1].loc
        fstloc(1, 0, 1, 1)

        >>> f.names[-1:].loc
        fstloc(2, 1, 2, 2)
        """

        start, stop, _ = self._base_indices()

        if not (len_ := stop - start):
            return None
        if len_ == 1:
            return self.base._loc_Global_Nonlocal_names(start)

        (ln, col, _, _), (_, _, end_ln, end_col) = self.base._loc_Global_Nonlocal_names(start, stop - 1)

        return fstlocn(ln, col, end_ln, end_col, n=0)  # we return fstlocn for convenient sharing with pars()

    @property
    def ln(self) -> int | None:
        r"""Line number of the first line of this view (0 based).

        **Examples:**

        >>> from fst import *

        >>> f = FST('global\\\na,\\\n b')

        >>> f.names[:1].ln
        1

        >>> f.names[-1:].ln
        2
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._loc_Global_Nonlocal_names(start).ln

    @property
    def col(self) -> int | None:  # char index
        r"""CHARACTER index of the start of this view (0 based).

        **Examples:**

        >>> from fst import *

        >>> f = FST('global\\\na,\\\n b')

        >>> f.names[:1].col
        0

        >>> f.names[-1:].col
        1
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._loc_Global_Nonlocal_names(start).col

    @property
    def end_ln(self) -> int | None:  # 0 based
        r"""Line number of the LAST LINE of this view (0 based).

        **Examples:**

        >>> from fst import *

        >>> f = FST('global\\\na,\\\n b')

        >>> f.names[:1].end_ln
        1

        >>> f.names[-1:].end_ln
        2
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._loc_Global_Nonlocal_names(stop - 1).end_ln

    @property
    def end_col(self) -> int | None:  # char index
        r"""CHARACTER index one past the end of this view (0 based).

        **Examples:**

        >>> from fst import *

        >>> f = FST('global\\\na,\\\n b')

        >>> f.names[:1].end_col
        1

        >>> f.names[-1:].end_col
        2
        """

        start, stop, _ = self._base_indices()

        if stop == start:
            return None

        return self.base._loc_Global_Nonlocal_names(stop - 1).end_col

    bloc = loc
    bln = ln
    bcol = col
    bend_ln = end_ln
    bend_col = end_col


class FSTView_dummy(FSTView):
    """Dummy view for nonexistent fields (type_params on py < 3.12). @private"""

    @property
    def lines(self) -> list[str]:
        return ['']

    @property
    def src(self) -> str:
        return ''

    @property
    def loc(self) -> fstloc | None:
        return None

    @property
    def ln(self) -> int | None:
        return None

    @property
    def col(self) -> int | None:  # char index
        return None

    @property
    def end_ln(self) -> int | None:  # 0 based
        return None

    @property
    def end_col(self) -> int | None:  # char index
        return None

    bloc = loc
    bln = ln
    bcol = col
    bend_ln = end_ln
    bend_col = end_col

    def _len_field(self) -> int:
        return 0

    def __getitem__(self, idx: int | slice) -> FSTView | fst.FST | str | None:
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

    def replace(self, code: Code | None, one: bool | None = True, **options) -> FSTView:
        if code is not None:
            raise RuntimeError('cannot replace a dummy view')

        return self

    def remove(self, **options) -> FSTView:
        return self

    def insert(self, code: Code, idx: int | Literal['end'] = 0, one: bool | None = True, **options) -> FSTView:
        if code is not None:
            raise RuntimeError('cannot insert to a dummy view')

        return self

    def append(self, code: Code, **options) -> FSTView:
        if code is not None:
            raise RuntimeError('cannot append to a dummy view')

        return self

    def extend(self, code: Code, one: Literal[False] | None = False, **options) -> FSTView:
        if code is not None:
            raise RuntimeError('cannot extend a dummy view')

        return self

    def prepend(self, code: Code, **options) -> FSTView:
        if code is not None:
            raise RuntimeError('cannot prepend to a dummy view')

        return self

    def prextend(self, code: Code, one: Literal[False] | None = False, **options) -> FSTView:
        if code is not None:
            raise RuntimeError('cannot prextend a dummy view')

        return self
