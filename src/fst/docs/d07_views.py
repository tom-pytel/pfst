r"""
# Slice views and virtual fields

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

>>> f.elts[1:1] = 'x, y'

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

>>> f.elts[3:3] = 'c, d'

>>> print(f.src)
[x, y, [a, b], c, d]

Or assign directly to the field name, replacing the entire slice, though this is not a view operation but rather a
property setter of the `FST` class itself.

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

With the exception of `insert()`, these operations don't take indices but rather are meant to be executed on a
particular indexed view which selects their range in the list.

>>> print(FST('[a, b, c]').elts.replace('[x, y]').base.src)
[[x, y]]

>>> print(FST('[a, b, c]').elts.replace('x, y').base.src)
[(x, y)]

>>> print(FST('[a, b, c]').elts.replace('[x, y]', one=False).base.src)
[[x, y]]

>>> print(FST('[a, b, c]').elts.replace('x, y', one=False).base.src)
[x, y]

>>> print(FST('[a, b, c]').elts.remove().base.src)
[]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 1).base.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts[1:1].insert('[x, y]').base.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 1, one=False).base.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts.insert('x, y', 1, one=False).base.src)
[a, x, y, b, c]

>>> print(FST('[a, b, c]').elts.insert('[x, y]', 'end', one=False).base.src)
[a, b, c, [x, y]]

>>> print(FST('[a, b, c]').elts.insert('x, y', 'end', one=False).base.src)
[a, b, c, x, y]

>>> print(FST('[a, b, c]').elts.append('[x, y]').base.src)
[a, b, c, [x, y]]

>>> print(FST('[a, b, c]').elts.append('x, y').base.src)
[a, b, c, (x, y)]

>>> print(FST('[a, b, c]').elts.extend('[x, y]').base.src)
[a, b, c, [x, y]]

>>> print(FST('[a, b, c]').elts.extend('x, y').base.src)
[a, b, c, x, y]

>>> print(FST('[a, b, c]').elts.prepend('[x, y]').base.src)
[[x, y], a, b, c]

>>> print(FST('[a, b, c]').elts.prepend('x, y').base.src)
[(x, y), a, b, c]

>>> print(FST('[a, b, c]').elts.prextend('[x, y]').base.src)
[[x, y], a, b, c]

>>> print(FST('[a, b, c]').elts.prextend('x, y').base.src)
[x, y, a, b, c]

They work on subviews as well.

>>> print(FST('[a, b, c]').elts[1:2].replace('[x, y]').base.src)
[a, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].replace('x, y').base.src)
[a, (x, y), c]

>>> print(FST('[a, b, c]').elts[1:2].replace('[x, y]', one=False).base.src)
[a, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].replace('x, y', one=False).base.src)
[a, x, y, c]

>>> print(FST('[a, b, c]').elts[1:3].remove().base.src)
[a]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 1).base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2][1:1].insert('[x, y]').base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2][1:1].insert('x, y').base.src)
[a, b, (x, y), c]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 1, one=False).base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].insert('x, y', 1, one=False).base.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].insert('[x, y]', 'end', one=False).base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].insert('x, y', 'end', one=False).base.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].append('[x, y]').base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].extend('[x, y]').base.src)
[a, b, [x, y], c]

>>> print(FST('[a, b, c]').elts[1:2].extend('x, y').base.src)
[a, b, x, y, c]

>>> print(FST('[a, b, c]').elts[1:2].prepend('[x, y]').base.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts[1:2].prextend('[x, y]').base.src)
[a, [x, y], b, c]

>>> print(FST('[a, b, c]').elts[1:2].prextend('x, y').base.src)
[a, x, y, b, c]


## `_all` virtual field

Standard `AST` fields are used to access and modify values where there is a one-to-one correspondence and the indexing
aligns. Virtual fields allow access to the tree structure that wouldn't be possible if just trying to access
`Dict.keys` in the case of `_all`, or provides the convenience of working with statement bodies without having to check
for docstrings in the case of `_body`.

Virtual fields can be used in put and get functions for the `field` value, they can be gotten as special slice views
and they can be accessed directly as attributes to operate on just like any other normal `AST` field (but only on the
`FST` node, if you try to access these on the `AST` node you will get an error).

The `_all` field allows slice and index access to the paired `key:value` elements of a `Dict` or `key:pattern` elements
of a `MatchMapping` (along with the `rest` if present). This way you can get and put them in a common-sense manner.

>>> f = FST('{1: a, 2: b, 3: c, 4: d}')

>>> print(f.get_slice(1, 3, '_all').src)
{2: b, 3: c}

>>> f.put_slice('{-1: x}', 1, 3, '_all')
<Dict ROOT 0,0..0,19>

>>> print(f.src)
{1: a, -1: x, 4: d}

You can delete individual elements in this way.

>>> f.put(None, 1, '_all')
<Dict ROOT 0,0..0,12>

>>> print(f.src)
{1: a, 4: d}

But not put individual elements, since there is not an `AST` which represents a `key:value` pair. If you want to replace
a single element in this way you must use slice operations.

>>> f.put('{-2: y}', 1, '_all')
Traceback (most recent call last):
...
fst.NodeError: cannot put as 'one' item to a Dict slice

>>> f.put_slice('{-2: y}', 1, 2, '_all')
<Dict ROOT 0,0..0,13>

>>> print(f.src)
{1: a, -2: y}

When using `_all` on a `MatchMapping`, the `rest` element is included in the virtual field for both get and put
operations.

>>> f = FST('{1: a, 2: b, **c}', 'MatchMapping')

>>> print(f.get_slice(1, 3, '_all').src)
{2: b, **c}

`_all` is the default field for `Dict`, `MatchMapping`, `Compare` and `arguments` so you don't need to include it as a
parameter.

>>> f.put_slice('{-1: x, -2: y, **z}', 1, 3)
<MatchMapping ROOT 0,0..0,25>

>>> print(f.src)
{1: a, -1: x, -2: y, **z}

You can only modify the `rest` element within the rules of the `MatchMapping` syntax, only one of those is permitted and
only at the end of the pattern:

>>> f.put_slice('{**BAD}', 1, 2)
Traceback (most recent call last):
...
ValueError: put slice with 'rest' element to MatchMapping must be at end

For a `Compare`, there is no problem with having to pair elements for slicing, but the rather indexing is changed to
include the `left` element as the first element of the virtual field. This applies both to single element operations as
well as slices.

>>> f = FST('a < b == c > d')

>>> print(f.get(0).src)
a

>>> print(f.get_slice(1, 3).src)
b == c

When carrying out slice operations on a `Compare` though there are extra considerations to take into account for the
operators. This is explained in more detail in the section on slices `fst.docs.d06_slices`.

`_all` is also the default field for an `arguments` node and allows access to all the different types of arguments as
if they existed in a single list.

>>> f = FST('def f(a, /, b=2, *c, d=3, **e): pass')

>>> print(f.args._all[1:-1].copy().src)
b=2, *c, d=3

Since the `_all` field is the default field for the `arguments` node type you can omit it from the indexing access.

>>> print(f.args[-2:].copy().src)
*, d=3, **e

This allows you to deal with function arguments in an intuitive way without having to deal too much with the details of
the different argument types and markers which are needed to delimit them.

>>> f.args[:1] = 'x=1, y=2'

>>> print(f.src)
def f(x=1, y=2, b=2, *c, d=3, **e): pass

>>> del f.args[3]

>>> print(f.src)
def f(x=1, y=2, b=2, *, d=3, **e): pass


## `_body` virtual field

This is a pure convenience field. It doesn't solve any problem but rather allows you to work with blocks of statements
without having to take into account the possible presence of a docstring. `_body` provides a view on the real `body`
field as if the docstring expression were not present, so the first statement after the docstring becomes index 0 and
the length is reduced by 1 in this case.

>>> f = FST('''
... def func():
...     \'\'\'docstring\'\'\'
...     a = b
...     call()
... '''.strip())

>>> len(f.body), len(f._body)
(3, 2)

>>> print(f.get_slice('body').src)
'''docstring'''
a = b
call()

>>> print(f.get_slice('_body').src)
a = b
call()

>>> print(f.get(0, '_body').src)
a = b

>>> f.put_slice(None, '_body')
<FunctionDef ROOT 0,0..1,19>

>>> print(f.src)
def func():
    '''docstring'''

If a docstring is not present, or if the `AST` node is a block statement that cannot have a docstring then the `_body`
field acts identically to the normal `body` field.

>>> print(FST('''
... if 1:
...     \'\'\'not-docstring\'\'\'
...     a = b
...     call()
... '''.strip()).get_slice('_body').src)
'''not-docstring'''
a = b
call()

Also note that `_body` is not the default field unlike `_all` is for its respective node types, you will always have to
specify it explicitly.


## `_args` virtual field

This is a field on the `Call` node which combines the `args` and `keywords` fields into one and accesses them in
syntax order (this is important as the two separate lists may have elements which are intermixed).

>>> f = FST('call(a, b=c, *d)')

>>> print([g.src for g in [*f.args, *f.keywords]])
['a', '*d', 'b=c']

>>> print([g.src for g in f._args])
['a', 'b=c', '*d']

You can operate on this field just like any other normal or virtual field.

>>> print(f.put('*new_d', 2, '_args').src)
call(a, b=c, *new_d)

>>> print(f.get_slice(0, 2).src)  # its the default field so you can omit it
a, b=c

>>> print(f._args[1:].copy().src)
b=c, *new_d

But you can't break syntax ordering rules.

>>> f._args[0] = '**nope'
Traceback (most recent call last):
...
fst.NodeError: keyword arglike unpacking cannot precede iterable arglike unpacking

>>> f.put_slice('a, b', 2, 'end')
Traceback (most recent call last):
...
fst.NodeError: positional arglike cannot follow keyword arglike


## `_bases` virtual field

This is a field on a `ClassDef` which follows basically the same syntax rules as `Call._args`, even if it doesn't always
make sense.

>>> f = FST('class cls(a, b=c, *d): pass')

>>> print([g.src for g in [*f.bases, *f.keywords]])
['a', '*d', 'b=c']

>>> print([g.src for g in f._bases])
['a', 'b=c', '*d']

Just like with `_args`, you can operate on this field again like any other normal or virtual field.

>>> print(f.put('*new_d', 2, '_bases').src)
class cls(a, b=c, *new_d): pass

`_bases` is **NOT** the default field for a `ClassDef`, so if you want to use it you must always specify it. Otherwise
the operation is on `body` which is the default field for a `ClassDef`.

>>> print(f.get_slice(0, 2, '_bases').src)
a, b=c

>>> print(f._bases[1:].copy().src)
b=c, *new_d

And you still can't break syntax ordering rules.

>>> f._bases[0] = '**nope'
Traceback (most recent call last):
...
fst.NodeError: keyword arglike unpacking cannot precede iterable arglike unpacking

>>> f.put_slice('a, b', 2, 'end', '_bases')
Traceback (most recent call last):
...
fst.NodeError: positional arglike cannot follow keyword arglike


## Virtual field attribute access

Just like normal fields, virtual fields can be accessed by their name on an `FST` class and give the same expected
results.

>>> f = FST('{1: a, 2: b, 3: c}')

>>> print(f._all[1:].copy().src)
{2: b, 3: c}

>>> f._all[:2] = '{-1: x}'

>>> print(f.src)
{-1: x, 3: c}

>>> del f._all[0]

>>> print(f.src)
{3: c}

>>> print(FST('left < comp0 < comp1')._all[-3].src)
left

>>> f = FST('''
... \'\'\'docstring\'\'\'
... a = b
... call()
... '''.strip())  # Module

>>> print(f._body.copy().src)
a = b
call()

>>> del f._body

>>> print(f.src)
'''docstring'''
"""
