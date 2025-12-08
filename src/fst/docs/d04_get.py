r"""
# Accessing and copying nodes

To be able to execute the examples, import this.

>>> from fst import *

## `copy()` and `cut()`

If you just access nodes directly you get the node as it lives in the parent tree, without source dedenting (except for
the first line) or isolation.

>>> f = FST('''
... if i:
...     if j:
...         k = 1
...     else:
...         k = 0
... '''.strip())

>>> g = f.body[0]

>>> print(g.src)
if j:
        k = 1
    else:
        k = 0

This node is not a root node and can't be put to a tree.

>>> g.is_root
False

>>> try:
...     f.body.append(g)
... except Exception as exc:
...     print('Exception:', exc)
Exception: expecting root node

In order to get this node standalone you need to `copy()` it (`fst.fst.FST.copy()`).

>>> g = f.body[0].copy()

>>> print(g.src)
if j:
    k = 1
else:
    k = 0
>>> g.is_root
True

>>> f.body.append(g)
<<If ROOT 0,0..8,13>.body[0:2] [<If 1,4..4,13>, <If 5,4..8,13>]>

>>> print(f.src)
if i:
    if j:
        k = 1
    else:
        k = 0
    if j:
        k = 1
    else:
        k = 0

A copied node is its own standalone `FST` tree and can be gotten from and put to and otherwise used like any other `FST`
tree. It does not have to be valid parsable code, any node is supported as the root of a tree and only root `FST` nodes
can be put into other `FST` trees.

You can also cut nodes out, which will remove them from the tree. Important, the `FST` node returned by `cut()` may be,
but will not necessarily be the same `FST` node that was in the tree! See `fst.fst.FST.cut()`.

>>> g = f.body[0].cut()

>>> print(f.src)
if i:
    if j:
        k = 1
    else:
        k = 0

When dealing with statements you can temporarily cut out the last statement in a body. This can be disabled by passing
`norm=True` or `norm_self=True` which ensure that only valid `AST` trees result from operations. If you do cut
everything from a field which normally needs something in it then make sure to put something back as soon as possible
because most operations will fail with a tree in this state.

>>> g = f.body[0].body[0].cut()

>>> print(f.src)
if i:
    if j:
    else:
        k = 0

>>> f.body[0].body.append(g)
<<If 1,4..4,13>.body[0:1] [<Assign 2,8..2,13>]>

>>> print(f.src)
if i:
    if j:
        k = 1
    else:
        k = 0

>>> try:
...     f.body[0].body[0].cut(norm=True)
... except Exception as exc:
...     print(repr(exc))
ValueError('cannot cut all elements from If.body without norm_self=False')

Cutting out an optional body field like an `orelse`, `finalbody` or `handlers` (if there is a `finalbody`) will leave
the tree in a valid state.

>>> f = FST('''
... if i:
...     j = 1
... else:
...     k = 2
... '''.strip())

>>> print(f.src)
if i:
    j = 1
else:
    k = 2

>>> f.orelse[0].cut()
<Assign ROOT 0,0..0,5>

>>> print(f.src)
if i:
    j = 1

You can copy a root node but you cannot cut one.

>>> f.copy()
<If ROOT 0,0..1,9>

>>> try:
...     f.cut()
... except Exception as exc:
...     print('Exception:', exc)
Exception: cannot cut root node

## `get()` and `get_slice()`

`copy()` and `cut()` are basically shortcuts to `get()` (except in the case of a root node copy). The `get()` function
essentially does a `copy()` except from the point of view of the parent node (`fst.fst.FST.get()`). So the following two
are equivalent.

>>> print(FST('i = 123').value.copy().src)
123

>>> print(FST('i = 123').get('value').src)
123

`get()` can also function as a `cut()`.

>>> f = FST('[1, 2, 3]')

>>> f.get(1, cut=True).src
'2'

>>> print(f.src)
[1, 3]

You can specify which field to `get()` from.

>>> f = FST('''
... if 1:
...     i = 1
... else:
...     j = 2
...     k = 3
...     l = 4
... '''.strip())

>>> print(f.get(0, 'orelse').src)
j = 2

>>> print(f.get(0, 'body').src)
i = 1

>>> print(f.get(0).src)  # 'body' is the default field
i = 1

If you pass two indices then `get()` returns a slice using `get_slice()`. `get()` can do everything that `get_slice()`
can do, but not vice-versa.

>>> print(f.get(1, 3, 'orelse').src)
k = 3
l = 4

Which gets us to `get_slice()`, which **ONLY** gets slices (`fst.fst.FST.get_slice()`).

>>> print(f.get_slice(1, 3, 'orelse').src)
k = 3
l = 4

It can only get individual elements as slices, unlike `get()` which can get them as the element itself.

>>> print(FST('[1, 2, 3]').get_slice(1, 2).src)
[2]

>>> print(FST('[1, 2, 3]').get(1).src)
2

Both `get()` and `get_slice()` can specify slice beginning and end points as `None`, which specifies from beginning of
the body or to the end of it.

>>> print(FST('[1, 2, 3]').get_slice(1, None).src)
[2, 3]

>>> print(FST('[1, 2, 3]').get(None, 2).src)
[1, 2]

Many nodes have a specific common-sense default field, like `value` for a `Return`.

>>> print(FST('return 123').get().src)
123

The node type `Dict` cannot have normal slices taken as it doesn't have a contiguous single-element list but rather
combinations of multiple field lists. For these nodes, leaving the default `field` parameter of `None` gives special
slicing behavior which slices across the multiple fields and gives a new `Dict`.

>>> print(FST('{1:2, 3:4, 5:6}').get_slice(1, 3).src)
{3:4, 5:6}

The `field=None` is just a shortcut for specifying the "virtual" field `'_all'`, which exists for `Dict`, `MatchMapping`
and `Compare` in order to allow access to combined elements which are not normally accessible by themselves as `AST`
nodes.

Note below that the first `a` in the `Compare` is normally not part of a `list` field but can be sliced as if it were
using the `'_all'` virtual field (which is the default field for `Compare` but we include it explicitly for
demonstration purposes).

>>> print(FST('a < b < c').get_slice(0, 2, field='_all').src)
a < b

Slices being gotten or put are implemented using common sense containers, like for sequences using the same type of
sequence or for a dictionary returning / expecting a `Dict`. When there is not possible pure container for a slice of
elements, like `ExceptHandler` or `match_case`, then they are put into our own special container `AST` which exists just
for this purpose. This is not a valid `AST` object of course, but works for moving stuff around.

>>> f = FST('''
... try:
...     pass
... except ValueError:
...     i = 1
... except RuntimeError:
...     j = 2
... '''.strip())

>>> s = f.get_slice(0, 2, 'handlers')

>>> s
<_ExceptHandlers ROOT 0,0..3,9>

>>> print(s.src)
except ValueError:
    i = 1
except RuntimeError:
    j = 2

>>> s.dump()
_ExceptHandlers - ROOT 0,0..3,9
  .handlers[2]
   0] ExceptHandler - 0,0..1,9
     .type Name 'ValueError' Load - 0,7..0,17
     .body[1]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
   1] ExceptHandler - 2,0..3,9
     .type Name 'RuntimeError' Load - 2,7..2,19
     .body[1]
      0] Assign - 3,4..3,9
        .targets[1]
         0] Name 'j' Store - 3,4..3,5
        .value Constant 2 - 3,8..3,9

## Non-AST values

Using `get()` and `get_slice()` you can get non-`AST` primitive values from nodes. This exists to accomondate stuff like
`MatchSingleton`, as it just has a primitive value instead of an expression (it is also set this way, via primitive).

>>> f = FST('case True: pass')

>>> f.pattern.get('value')
True

But this also applies to any other `AST` field which is a primitive.

>>> FST("b'bytes'", Constant).get('value')
b'bytes'

>>> FST('[i async for i in j]').generators[0].get('is_async')
1

>>> FST('a.b: int = 1').get('simple')
0

Getting slices from a primitive list does convert the primitives to their common-sense `AST` equivalents.

>>> f = FST('global a, b, c')

>>> f.dump()
Global - ROOT 0,0..0,14
  .names[3]
   0] 'a'
   1] 'b'
   2] 'c'

>>> g = f.get_slice()

>>> g.dump()
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'c' Load - 0,6..0,7
  .ctx Load

Put likewise expects a valid `Tuple` when putting to a list of comma-separated primitives.

>>> f.put_slice(g, 1, 2)
<Global ROOT 0,0..0,20>

>>> print(f.src)
global a, a, b, c, c

## By attribute

The `FST` class provides properties that mirror the fields of all possible `AST` classes in order to allow direct access
to those fields through the `FST` class. When accessing like this, fields which are `AST` nodes have their corresponding
`FST` node returned and fields which are lists of `AST` nodes return an `fstview` which acts as a list of corresponding
`FST` nodes. Elements which are primitive values are returned as such.

>>> f = FST('i, j = [x, 2.5]')

>>> f.targets  # this is an `fstview`
<<Assign ROOT 0,0..0,15>.targets[0:1] [<Tuple 0,0..0,4>]>

>>> f.targets[0]
<Tuple 0,0..0,4>

>>> f.value
<List 0,7..0,15>

>>> f.value.elts
<<List 0,7..0,15>.elts[0:2] [<Name 0,8..0,9>, <Constant 0,11..0,14>]>

>>> f.value.elts[0]
<Name 0,8..0,9>

>>> f.value.elts[0].id
'x'

>>> f.value.elts[1]
<Constant 0,11..0,14>

>>> f.value.elts[1].value
2.5

Accessing in this manner does not give a copy but rather the specific element which is in the tree. If you want a
standalone element that you can put into another tree then you need to make a copy.

>>> f.value
<List 0,7..0,15>

>>> f.value.copy()
<List ROOT 0,0..0,8>

## `get_src()`

This just gets source code from a given location. It doesn't matter what node of a tree this is called on, it always
gets from the root source and will always return the same results (`fst.fst.FST.get_src()`).

>>> f = FST('''
... if 1:
...     i = 1
... else:
...     j = 2
...     k = 3
...     l = 4
... '''.strip())

>>> print(f.get_src(0, 0, 2, 3))
if 1:
    i = 1
els

>>> print(f.orelse[2].value.get_src(0, 0, 2, 3))
if 1:
    i = 1
els

As you can see the location doesn't have to start or stop on a node boundary, but you can get node source this way as an
alternative to `f.src`.

>>> print(f.get_src(*f.orelse[1].loc))
k = 3

This can actually come in handy in the case of a root node as root node `.src` is always the entire source code assigned
to that tree, regardless of where the top node actually exists.

>>> f = FST('''
...  # blah
... happy = little = node
...  # blah blah
... '''[1:-1])

>>> f
<Assign ROOT 1,0..1,21>

>>> print(f.src)
 # blah
happy = little = node
 # blah blah

>>> print(f.get_src(*f.loc))
happy = little = node

**Note:** Cut is not implemented in `get_src()`. If you want to delete the source gotten then follow this up with a
`put_src(None, ...)` at the same location as changing source code has several options selectable in that function. See
the `put_src()` section in `fst.docs.d05_put`.
"""
