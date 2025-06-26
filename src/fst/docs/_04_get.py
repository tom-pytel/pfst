r"""
# Accessing and copying nodes

To be able to execute the examples, import this.
```py
>>> from fst import *
```

## `copy()` and `cut()`

If just you access nodes directly you get the node as it lives in the parent tree, without source dedenting (except for
the first line) or isolation.

```py
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
```

This node is not a root node and can't be put to a tree.

```py
>>> g.is_root
False

>>> try:
...     f.body.append(g)
... except Exception as exc:
...     print('Exception:', exc)
Exception: expecting root node
```

In order to get this node standalone you need to `copy()` it.

```py
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

>>> print(f.src.rstrip())  # ignore the rstrip, its for prettification purposes
if i:
    if j:
        k = 1
    else:
        k = 0
    if j:
        k = 1
    else:
        k = 0
```

A copied node is its own standalone FST tree and can be gotten from and put to and otherwise used like any other FST
tree. It does not have to be valid parsable code, any node is supported as the root of a tree and only root `FST` nodes
can be put into other FST trees.

You can also cut nodes out, which will remove them from the tree. Important, the `FST` node returned by `cut()` may be,
but will not necessarily be the same `FST` node that was in the tree!

```py
>>> g = f.body[0].cut()

>>> print(f.src.rstrip())
if i:
    if j:
        k = 1
    else:
        k = 0
```

When dealing with statements you can temporarily cut out the last statement in a body, but make sure to put something
back as soon as possible because most operations will fail with a tree in this state.

```py
>>> g = f.body[0].body[0].cut()

>>> print(f.src.rstrip())
if i:
    if j:
    else:
        k = 0

>>> f.body[0].body.append(g)
<<If 1,4..4,13>.body[0:1] [<Assign 2,8..2,13>]>

>>> print(f.src.rstrip())
if i:
    if j:
        k = 1
    else:
        k = 0
```

Cutting out an optional body field like an `orelse`, `finalbody` or `handlers` (if there is a `finalbody`) will leave
the tree in a valid state.

```py
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

>>> print(f.src.rstrip())
if i:
    j = 1
```

You can copy a root node but you cannot cut one.

```py
>>> f.copy()
<If ROOT 0,0..1,9>

>>> try:
...     f.cut()
... except Exception as exc:
...     print('Exception:', exc)
Exception: cannot cut root node
```

## `get()` and `get_slice()`

`copy()` and `cut()` are basically shortcuts to `get()` (except in the case of a root node copy). The `get()` function
essentially does a `copy()` except from the point of view of the parent node. So the following two are equivalent.

```py
>>> print(FST('i = 123').value.copy().src)
123

>>> print(FST('i = 123').get('value').src)
123
```

`get()` can also function as a `cut()`.

```py
>>> f = FST('[1, 2, 3]')

>>> f.get(1, cut=True).src
'2'

>>> print(f.src)
[1, 3]
```

You can specify which field to `get()` from.

```py
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
```

If you pass two indices then `get()` returns a slice using `get_slice()`. `get()` can do everything that `get_slice()`
can do.

```py
>>> print(f.get(1, 3, 'orelse').src)
k = 3
l = 4
```

Which gets us to `get_slice()`, which ONLY gets slices.

```py
>>> print(f.get_slice(1, 3, 'orelse').src)
k = 3
l = 4
```

It can only get individual elements as slices, unlike `get()` which can get them as the element itself.

```py
>>> print(FST('[1, 2, 3]').get_slice(1, 2).src)
[2]

>>> print(FST('[1, 2, 3]').get(1).src)
2
```

Both `get()` and `get_slice()` can specify slice beginning and end points as `None`, which specifies from beginning of
the body or to the end of it.

```py
>>> print(FST('[1, 2, 3]').get_slice(1, None).src)
[2, 3]

>>> print(FST('[1, 2, 3]').get(None, 2).src)
[1, 2]
```

Many nodes have a specific common-sense default field, like `value` for a `Return`.

```py
>>> print(FST('return 123').get().src)
123
```

The node type `Dict` cannot have normal slices taken as it doesn't have a contiguous single-element list but rather
combinations of multiple field lists. For this nodes, leaving the default field of `None` gives special slicing
behavior which slices across the multiple fields and gives a new `Dict`.

```py
>>> print(FST('{1:2, 3:4, 5:6}').get_slice(1, 3).src)
{3:4, 5:6}
```

Slices being gotten or put are implemented using common sense containers, like for sequences using the same type of
sequence or for a dictionary returning / expecting a `Dict`. When there is not possible pure container for a slice of
elements, like `ExceptHandler` or `match_case`, then they are put directly into a `Module` body field. This is not a
valid `AST` object of course, but works for moving stuff around.

```py
>>> f = FST('''
... try:
...     pass
... except ValueError:
...     i = 1
... except RuntimeError:
...     j = 2
... '''.strip())

>>> s = f.get_slice(0, 2, 'handlers')

>>> print(s.src)
except ValueError:
    i = 1
except RuntimeError:
    j = 2

>>> s.dump()
Module - ROOT 0,0..3,9
  .body[2]
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
```

TODO: Prescribed slice operations are implemented for all `stmt` containers, `Tuple`, `List`, `Set`, `Dict`, exception
handler bodies containing `ExceptHandler` and match statement cases containing `match_case`. All other slice operations
must currently be carried out using raw operations which, are not as robust.

TODO: `MatchMapping` and `Compare` will also support special slicing behavior but slice operations for them are not
implemented yet (other than raw).

## Non-AST values

Using `get()` (and eventually `get_slice()`, not implemented yet) you can get non-AST primitive values from nodes. This
exists mostly to accomondate `MatchSingleton`, as it just has a primitive value instead of an expression (it is also
set this way, via primitive).

TODO: Implement `get_slice()` on `Global` and `Nonlocal` `names`.

```py
>>> f = FST('case True: pass')

>>> f.pattern.get('value')
True
```

But this also applies to any other `AST` field which is a primitive.

```py
>>> FST("b'bytes'", Constant).get('value')
b'bytes'

>>> FST('[i async for i in j]').generators[0].get('is_async')
1

>>> FST('a.b: int = 1').get('simple')
0
```

## By attribute

The `FST` class provides properties that shadow the fields of all possible `AST` classes in order to allow direct access
to those fields through the `FST` class. When accessing like this, fields which are `AST` nodes have their corresponding
`FST` node returned and fields which are lists of `AST` nodes return an `fstview` which acts as a list of corresponding
`FST` nodes. Elements which are primitive values are returned as such.

```py
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
```

Accessing in this manner does not give a copy but rather the specific element which is in the tree. If you want a
standalone element that you can put into another tree then you need to make a copy.

```py
>>> f.value
<List 0,7..0,15>

>>> f.value.copy()
<List ROOT 0,0..0,8>
```

## `get_src()`

This just gets source code from a given location. It doesn't matter what node of a tree this is called on, it always
gets from the root source and will always return the same results.

```py
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
```

As you can see the location doesn't have to start or stop on a node boundary, but you can get node source this way as an
alternative to `f.src`.

```py
>>> print(f.get_src(*f.orelse[1].loc))
k = 3
```

This can actually come in handy in the case of a root node as root node `.src` is always the entire source code assigned
to that tree, regardless of where the top node actually exists.

```py
>>> f = FST('''
... # blah
... happy = little = node
... # blah blah
... '''.strip())

>>> f
<Assign ROOT 1,0..1,21>

>>> print(f.src)
# blah
happy = little = node
# blah blah

>>> print(f.get_src(*f.loc))
happy = little = node
```
"""
