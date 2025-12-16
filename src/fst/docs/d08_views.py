r"""
# `FST` slice indexing

To be able to execute the examples, import this.

>>> from fst import *

## How to get

An `fstview` is a lightweight object meant to facilitate access to lists of child objects like a block statement `body`
or `Tuple` / `List` / `Set` `elts` field. Any field which is a list of other objects (or even strings in the case of
`Global` or `Nonlocal`) will make use of an `fstview` when accessed through the field name on the parent `FST` object.

>>> view = FST('[1, 2, 3]').elts

>>> type(view)
<class 'fst.view.fstview'>

>>> print(str(view)[:88])
<<List ROOT 0,0..0,9>.elts [<Constant 0,1..0,2>, <Constant 0,4..0,5>, <Constant 0,7..0,8

>>> view.base, view.field, view.start, view.stop
(<List ROOT 0,0..0,9>, 'elts', 0, 3)

An `fstview` is not normally intended to be accessed by assigning it to a name and using it through that. An `fstview`
basically exists to facilitate direct access to slices of children for immediate operations.

>>> f = FST('[1, 2]')

>>> _ = f.elts.append('3')  # _ just shuts up output

>>> print(f.src)
[1, 2, 3]

>>> del f.elts[1]

>>> print(f.src)
[1, 3]

>>> print(f.elts.insert('4', 1).base.src)
[1, 4, 3]

>>> del f.elts[:2]

>>> print(f.src)
[3]

## Indexing

You can copy or cut slices from an `FST` using a view.

>>> f = FST('''
... i = 1
... j = 2
... k = 3
... l = 4
... '''.strip())

>>> print(f.body[1:3].copy().src)
j = 2
k = 3

>>> print(f.body[:2].cut().src)
i = 1
j = 2

>>> print(f.src)
k = 3
l = 4

You can assign slices to a view.

>>> f = FST('[a, b]')

>>> f.elts[1:1] = '{x, y}'

>>> print(f.src)
[a, x, y, b]

>>> f.elts[2:] = f.elts.copy()

>>> print(f.src)
[a, x, a, x, y, b]

>>> f.elts[:] = Tuple(elts=[])

>>> print(f.src)
[]

Non-slice indexing also works as expected, including getting and putting a single element and not a slice, even if a
slice is the source.

>>> f = FST('[x, y, z]')

>>> print(f.elts[1].copy().src)
y

>>> f.elts[2] = '[a, b]'

>>> print(f.src)
[x, y, [a, b]]

If you want to assign the element as a slice, you must use slice indexing.

>>> f.elts[3:3] = '[c, d]'

>>> print(f.src)
[x, y, [a, b], c, d]

Or assign directly to the field name, replacing the entire slice, but this is not a view operation but rather a property
setter of the `FST` class itself.

>>> f.elts = 't, u, v'

>>> print(f.src)
[t, u, v]

It is safe to modify the underlying object outside of the view as the view validates its indices every time they are
used and truncates them to the actual size of the target field.

>>> f = FST('[a, b, c, d, e]')

>>> view = f.elts[1:3]

>>> view
<<List ROOT 0,0..0,15>.elts[1:3] [<Name 0,4..0,5>, <Name 0,7..0,8>]>

>>> _ = f.put_slice(None, 2, 5)

>>> view
<<List ROOT 0,0..0,6>.elts[1:2] [<Name 0,4..0,5>]>

>>> _ = f.put_slice(None, 0, 2)

>>> view
<<List ROOT 0,0..0,2>.elts[:0] []>

## Other operations

With the exception if `insert()`, these operations don't take indices but rather are meant to be executed on a
particular indexed view which selects their range in the list.

>>> print(FST('[a, b, c]').elts.replace('[x, y]').base.src)
[[x, y]]

>>> print(FST('[a, b, c]').elts.replace('[x, y]', one=False).base.src)
[x, y]

>>> print(FST('[a, b, c]').elts.remove().base.src)
[]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 1).base.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts[1:1].insert('[x, y]').base.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 1, one=False).base.src)
[a, x, y, b, c]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 'end', one=False).base.src)
[a, b, c, x, y]

>>> print(FST('[a, b, c]').elts.append('[x, y]').base.src)
[a, b, c, [x, y]]

>>> print(FST('[a, b, c]').elts.extend('[x, y]').base.src)
[a, b, c, x, y]

>>> print(FST('[a, b, c]').elts.prepend('[x, y]').base.src)
[[x, y], a, b, c]

>>> print(FST('[a, b, c]').elts.prextend('[x, y]').base.src)
[x, y, a, b, c]

They work on subviews as well.

>>> print(FST('[a, b, c]').elts[1:2].replace('[x, y]').base.src)
[a, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].replace('[x, y]', one=False).base.src)
[a, x, y, c]

>>> print(FST('[a, b, c]').elts[1:3].remove().base.src)
[a]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 1).base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2][1:1].insert('[x, y]').base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 1, one=False).base.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 'end', one=False).base.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].append('[x, y]').base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].extend('[x, y]').base.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].prepend('[x, y]').base.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts[1:2].prextend('[x, y]').base.src)
[a, x, y, b, c]
"""
