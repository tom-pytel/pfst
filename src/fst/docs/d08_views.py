r"""
# `FST` slice indexing

To be able to execute the examples, import this.
```py
>>> from fst import *
```

## How to get

An `fstview` is a lightweight short-lived object meant to facilitate access to lists of child objects like a block
statement `body` or `Tuple` / `List` / `Set` `elts` field. Any field which is a list of other objects (or even strings
in the case of `Global` or `Nonlocal`) will make use of an `fstview` when accessed through the field name on the parent
`FST` object.

```py
>>> view = FST('[1, 2, 3]').elts

>>> type(view)
<class 'fst.view.fstview'>

>>> view
<<List ROOT 0,0..0,9>.elts[0:3] [<Constant 0,1..0,2>, <Constant 0,4..0,5>, <Constant 0,7..0,8>]>

>>> view.fst, view.field, view.start, view.stop
(<List ROOT 0,0..0,9>, 'elts', 0, 3)
```

An `fstview` is not normally intended to be accessed by assigning it to a name and using it through that. An `fstview`
basically exists to facilitate direct access to slices of children for immediate operations.

```py
>>> f = FST('[1, 2]')

>>> f.elts.append('3')
<<List ROOT 0,0..0,9>.elts[0:3] [<Constant 0,1..0,2>, <Constant 0,4..0,5>, <Constant 0,7..0,8>]>

>>> print(f.src)
[1, 2, 3]

>>> del f.elts[1]

>>> print(f.src)
[1, 3]

>>> print(f.elts.insert('4', 1).fst.src)
[1, 4, 3]

>>> del f.elts[:2]

>>> print(f.src)
[3]
```

## Indexing

You can copy or cut slices from an `FST` using a view.

```py
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
```

You can assign slices to a view.

```py
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
```

Non-slice indexing also works as expected, including getting and putting a single element and not a slice, even if a
slice is the source.

```py
>>> f = FST('[x, y, z]')

>>> print(f.elts[1].copy().src)
y

>>> f.elts[2] = '[a, b]'

>>> print(f.src)
[x, y, [a, b]]
```

If you want to assign the element as a slice, you must use slice indexing.

```py
>>> f.elts[3:3] = '[c, d]'

>>> print(f.src)
[x, y, [a, b], c, d]
```

Or assign directly to the field name, replacing the entire slice, but this is not a view operation but rather a property
setter of the `FST` class itself.

```py
>>> f.elts = 't, u, v'

>>> print(f.src)
[t, u, v]
```

## Other operations

With the exception if `insert()` (since its a standard pattern) these operations don't take indices but rather are meant
to be executed on a particular indexed view which selects their range in the list.

```py
>>> print(FST('[a, b, c]').elts.replace('[x, y]').fst.src)
[[x, y]]

>>> print(FST('[a, b, c]').elts.replace('[x, y]', one=False).fst.src)
[x, y]

>>> print(FST('[a, b, c]').elts.remove().fst.src)
[]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 1).fst.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts[1:1].insert('[x, y]').fst.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 1, one=False).fst.src)
[a, x, y, b, c]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 'end', one=False).fst.src)
[a, b, c, x, y]

>>> print(FST('[a, b, c]').elts.append('[x, y]').fst.src)
[a, b, c, [x, y]]

>>> print(FST('[a, b, c]').elts.extend('[x, y]').fst.src)
[a, b, c, x, y]

>>> print(FST('[a, b, c]').elts.prepend('[x, y]').fst.src)
[[x, y], a, b, c]

>>> print(FST('[a, b, c]').elts.prextend('[x, y]').fst.src)
[x, y, a, b, c]
```

They work on subviews as well.

```py
>>> print(FST('[a, b, c]').elts[1:2].replace('[x, y]').fst.src)
[a, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].replace('[x, y]', one=False).fst.src)
[a, x, y, c]

>>> print(FST('[a, b, c]').elts[1:3].remove().fst.src)
[a]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 1).fst.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2][1:1].insert('[x, y]').fst.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 1, one=False).fst.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 'end', one=False).fst.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].append('[x, y]').fst.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].extend('[x, y]').fst.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].prepend('[x, y]').fst.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts[1:2].prextend('[x, y]').fst.src)
[a, x, y, b, c]
```

## Why ephemeral?

As stated above, views are meant for direct use and not for keeping around. The reason for this is that any operation
that changes the size of the target of a view, if it is not effectuated through the view itself, will almost certainly
invalidate the view information.

```py
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

So it is better to let a view go away after using it rather than trying to keep it around.
"""
