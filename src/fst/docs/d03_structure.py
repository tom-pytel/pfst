r"""
# Tree structure and node traversal

To be able to execute the examples, import this.
```py
>>> from fst import *
```

## Links

For an FST parsed `AST` tree, each node will have its own `FST` node. The `FST` nodes contain the tree structure missing
in the `AST` nodes, specifically a reference to the parent `FST` node and the field and index of this node in the
parent.

```py
>>> f = FST('i = 1')

>>> f.dump()
Assign - ROOT 0,0..0,5
  .targets[1]
  0] Name 'i' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5

>>> f
<Assign ROOT 0,0..0,5>

>>> f.value
<Constant 0,4..0,5>

>>> f.value.parent
<Assign ROOT 0,0..0,5>

>>> f.value.pfield
astfield('value')

>>> f.value.pfield.name
'value'
```

For indexed fields the index is present in `pfield`.

```py
>>> f = FST('[x]')

>>> f.elts[0]
<Name 0,1..0,2>

>>> f.elts[0].pfield
astfield('elts', 0)

>>> f.elts[0].pfield.name, f.elts[0].pfield.idx
('elts', 0)

>>> f.elts[0].pfield[0], f.elts[0].pfield[1]
('elts', 0)
```

Every `FST` node also has a reference directly to the root of the tree.

```py
>>> f.elts[0].root
<List ROOT 0,0..0,3>

>>> f.root
<List ROOT 0,0..0,3>
```

The linkage to children is just via the existing `AST` fields.

```py
>>> type(f.a.elts[0])
<class 'ast.Name'>

>>> # which if accessed through the `FST` node will return the corresponding `FST` node
>>> f.elts[0]
<Name 0,1..0,2>

>>> type(f.elts[0].a)
<class 'ast.Name'>
```

## Siblings

You can access each `FST` node's previous and next siblings directly.

```py
>>> f = FST('[[1, 2], [3, 4], [5, 6]]')

>>> f.elts[1].src
'[3, 4]'

>>> f.elts[1].next().src
'[5, 6]'

>>> f.elts[1].prev().src
'[1, 2]'

>>> # if there is no next or previous sibling, None is returned
>>> repr(f.elts[2].next())
'None'

>>> repr(f.elts[0].prev())
'None'
```

## Children

You can access a node's children and iterate over them.

```py
>>> f = FST('[[1, 2, 3], [4, 5, 6]]')

>>> f.elts[0].first_child().src
'1'

>>> f.elts[0].last_child().src
'3'

>>> n = None
>>> while n := f.elts[0].next_child(n):
...     print(n.src)
1
2
3

>>> n = None
>>> while n := f.elts[0].prev_child(n):
...     print(n.src)
3
2
1
```

You can get the last child in a block node header.

```py
>>> FST('if here: pass').last_header_child().src
'here'

>>> FST('if here: pass').last_child().src
'pass'
```

## Walk

There is an explicit `walk()` function with a few options.

```py
>>> f = FST('[[1, 2], [3, 4]]')

>>> for g in f.walk():
...     print(g.src, g)
[[1, 2], [3, 4]] <List ROOT 0,0..0,16>
[1, 2] <List 0,1..0,7>
1 <Constant 0,2..0,3>
2 <Constant 0,5..0,6>
None <Load>
[3, 4] <List 0,9..0,15>
3 <Constant 0,10..0,11>
4 <Constant 0,13..0,14>
None <Load>
None <Load>
```

Or without the uninteresting `ctx` fields.

```py
>>> for g in f.walk(True):
...     print(g.src)
[[1, 2], [3, 4]]
[1, 2]
1
2
[3, 4]
3
4
```

Notice the order of recursion, parents then children going forward. You can also go backward (though it is still parents
before children).

```py
>>> for g in f.walk(True, back=True):
...     print(g.src)
[[1, 2], [3, 4]]
[3, 4]
4
3
[1, 2]
2
1
```

You can exclude the top-level node.

```py
>>> for g in f.walk(True, self_=False):
...     print(g.src)
[1, 2]
1
2
[3, 4]
3
4
```

You can limit the walk to a scope.

```py
>>> f = FST('''
... def f():
...     i = 1
... def g():
...     pass
... '''.strip())

>>> for g in f.walk(True):
...     print(g)
<Module ROOT 0,0..3,8>
<FunctionDef 0,0..1,9>
<Assign 1,4..1,9>
<Name 1,4..1,5>
<Constant 1,8..1,9>
<FunctionDef 2,0..3,8>
<Pass 3,4..3,8>

>>> for g in f.walk(True, scope=True):
...     print(g)
<Module ROOT 0,0..3,8>
<FunctionDef 0,0..1,9>
<FunctionDef 2,0..3,8>
```

You can interact with the generator during the walk to decide whether to recurse into the children or not. For example
if the walk is restricted to a scope you can decide to recurse into a specific child.

```py
>>> for g in (gen := f.walk(True, scope=True)):
...     print(g)
...     if isinstance(g.a, FunctionDef) and g.a.name == 'g':
...         _ = gen.send(True)  # ignore the '_', it shuts up return in stdout
<Module ROOT 0,0..3,8>
<FunctionDef 0,0..1,9>
<FunctionDef 2,0..3,8>
<Pass 3,4..3,8>
```

If you use the `recurse=False` option of the `walk()` function then recursion is normally limited to the first level of
children. You can override this by sending to the generator.

```py
>>> for g in (gen := f.walk(True, recurse=False)):
...     print(g)
...     if isinstance(g.a, FunctionDef) and g.a.name == 'f':
...         _ = gen.send(True)
<Module ROOT 0,0..3,8>
<FunctionDef 0,0..1,9>
<Assign 1,4..1,9>
<Name 1,4..1,5>
<Constant 1,8..1,9>
<FunctionDef 2,0..3,8>
```

Or you can decide NOT to recurse into children.

```py
>>> for g in (gen := f.walk(True)):
...     print(g)
...     if isinstance(g.a, FunctionDef) and g.a.name == 'f':
...         _ = gen.send(False)
<Module ROOT 0,0..3,8>
<FunctionDef 0,0..1,9>
<FunctionDef 2,0..3,8>
<Pass 3,4..3,8>
```

When you `walk()` nodes, you can modify the node being walked as long as the change is limited to the node and its
children and not any parents or sibling nodes. Any modifications to child nodes will be walked as if they had always
been there. This is not safe to do if using "raw" operations (explained elsewhere).

```py
>>> f = FST('[[1, 2], [3, 4], name]')

>>> for g in f.walk(True):
...     print(g.src)
...     if isinstance(g.a, Constant) and g.a.value & 1:
...         _ = g.replace('x')
...     elif isinstance(g.a, Name):
...         _ = g.replace('[5, 6]')
[[1, 2], [3, 4], name]
[1, 2]
1
2
[3, 4]
3
4
name
5
6

>>> print(f.src)
[[x, 2], [x, 4], [x, 6]]
```

## Step

Unlike the `next` and `prev` functions, the `step` functions allow walking forward or backward and going up and down
parents and children automatically. Notice the order is parents before children regardless of if going forward or back,
so the two functions are not inverses unlike the `next` / `prev` functions. You can walk the entire tree just stepping
forward or back one node at a time.

```py
>>> f = FST('[[1, 2], [3, 4]]')

>>> g = f.first_child()
>>> while g:
...     print(g.src)
...     g = g.step_fwd()
[1, 2]
1
2
[3, 4]
3
4

>>> g = f.last_child()
>>> while g:
...     print(g.src)
...     g = g.step_back()
[3, 4]
4
3
[1, 2]
2
1
```

## Paths

You can get a path from any given node to any of its children.

```py
>>> f = FST('i = [a * (b + c)]')

>>> f.dump()
Assign - ROOT 0,0..0,17
  .targets[1]
  0] Name 'i' Store - 0,0..0,1
  .value List - 0,4..0,17
    .elts[1]
    0] BinOp - 0,5..0,16
      .left Name 'a' Load - 0,5..0,6
      .op Mult - 0,7..0,8
      .right BinOp - 0,10..0,15
        .left Name 'b' Load - 0,10..0,11
        .op Add - 0,12..0,13
        .right Name 'c' Load - 0,14..0,15
    .ctx Load

>>> f.child_path(f.value.elts[0].right.left)
[astfield('value'), astfield('elts', 0), astfield('right'), astfield('left')]

>>> # for the humans
>>> f.child_path(f.value.elts[0].right.left, as_str=True)
'value.elts[0].right.left'
```

You can then get the child by this path, either the `astfield` one or the string one. Useful for getting the same
relative child in a copy of a tree.

```py
>>> g = f.copy()
>>> f.value.elts[0].right.left
<Name 0,10..0,11>

>>> p = f.child_path(f.value.elts[0].right.left)
>>> g.child_from_path(p)  # different tree
<Name 0,10..0,11>

>>> p = f.child_path(f.value.elts[0].right.left, as_str=True)
>>> g.child_from_path(p)  # different tree
<Name 0,10..0,11>
```
"""
