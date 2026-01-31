r"""
# Tree structure and node traversal

To be able to execute the examples, import this.

>>> from fst import *


## Links

For an `fst`-parsed `AST` tree, each node will have its own `FST` node. The `FST` nodes contain the tree structure
missing in the `AST` nodes, specifically a reference to the parent `FST` node and the field and index of this node in
the parent.

>>> f = FST('i = 1')

>>> _ = f.dump()
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

For indexed fields the index is present in `pfield`.

>>> f = FST('[x]')

>>> f.elts[0]
<Name 0,1..0,2>

>>> f.elts[0].pfield
astfield('elts', 0)

>>> f.elts[0].pfield.name, f.elts[0].pfield.idx
('elts', 0)

>>> f.elts[0].pfield[0], f.elts[0].pfield[1]
('elts', 0)

Every `FST` node also has a reference directly to the root of the tree.

>>> f.elts[0].root
<List ROOT 0,0..0,3>

>>> f.root
<List ROOT 0,0..0,3>

The linkage to children is just via the existing `AST` fields.

>>> type(f.a.elts[0])
<class 'ast.Name'>

Which if accessed through the `FST` node will return the corresponding `FST` node.

>>> f.elts[0]
<Name 0,1..0,2>

>>> type(f.elts[0].a)
<class 'ast.Name'>

Here is an example for a simple `Module` with a single `Expr` which is a `Name` to demonstrate.

>>> a = parse('var')

>>> _ = a.f.dump()
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'var' Load - 0,0..0,3

This is the node layout, note that even the `.ctx` gets an `FST`, every `AST` node does. Also note that the `FST` class
type is not differentiated according to the `AST`. The `.root` link is not an actual attribute but a `@property` derived
from the `.parent` chain.

```
                                 None
                          .root   ^
                           +--+   | .parent
                           V  |   |
+--------------+    .a    +--------------+<-------------------------+
|              |<---------|              |<---------------------+   |
|  ast.Module  |          |     FST      |<-----------------+   |   |
|              |--------->|              | .pfield=None     |   |   |
+--------------+    .f    +--------------+                  |   |   |
       |                          ^                         |   |   |
       | .body[0]                 | .parent                 |   |   |
       V                          |                         |   |   |
+--------------+    .a    +--------------+       .root      |   |   |
|              |<---------|              |---------->-------+   |   |
|   ast.Expr   |          |     FST      |                      |   |
|              |--------->|              | .pfield=('body', 0)  |   |
+--------------+    .f    +--------------+                      |   |
       |                          ^                             |   |
       | .value                   | .parent                     |   |
       V                          |                             |   |
+--------------+    .a    +--------------+       .root          |   |
|              |<---------|              |---------->-----------+   |
|   ast.Name   |          |     FST      |                          |
|              |--------->|              | .pfield=('value', None)  |
+--------------+    .f    +--------------+                          |
       |                          ^                                 |
       | .ctx                     | .parent                         |
       V                          |                                 |
+--------------+    .a    +--------------+       .root              |
|              |<---------|              |---------->---------------+
|   ast.Load   |          |     FST      |
|              |--------->|              | .pfield=('ctx', None)
+--------------+    .f    +--------------+
```


## Siblings

You can access each `FST` node's next and previous siblings directly using `fst.fst.FST.next()` and
`fst.fst.FST.prev()`.

>>> f = FST('[[1, 2], [3, 4], [5, 6]]')

>>> print(f.elts[1].src)
[3, 4]

>>> print(f.elts[1].next().src)
[5, 6]

>>> print(f.elts[1].prev().src)
[1, 2]

If there is no next or previous sibling then `None` is returned.

>>> print(f.elts[2].next())
None

>>> print(f.elts[0].prev())
None


## Children

You can access a node's children and iterate over them (`fst.fst.FST.first_child()`, `fst.fst.FST.last_child()`,
`fst.fst.FST.next_child()`, `fst.fst.FST.prev_child()`).

>>> f = FST('[[1, 2, 3], [4, 5, 6]]')

>>> print(f.elts[0].first_child().src)
1

>>> print(f.elts[0].last_child().src)
3

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

You can get the last child in a block node header using `fst.fst.FST.last_header_child()`.

>>> print(FST('if here: pass').last_header_child().src)
here

>>> print(FST('if here: pass').last_child().src)
pass


## Walk

There is an explicit `walk()` function with a few options (`fst.fst.FST.walk()`). This function also doubles as a
"transform" function as you can modify the tree structure as you are walking it, more on this below.

A simple walk over all nodes (the `all=True`).

>>> f = FST('def f(): return [[1, 2], 3 + 4]')

>>> for g in f.walk(all=True):
...     print(f'{str(g):30}{g.src or None}')
<FunctionDef ROOT 0,0..0,31>  def f(): return [[1, 2], 3 + 4]
<arguments 0,6..0,6>          None
<Return 0,9..0,31>            return [[1, 2], 3 + 4]
<List 0,16..0,31>             [[1, 2], 3 + 4]
<List 0,17..0,23>             [1, 2]
<Constant 0,18..0,19>         1
<Constant 0,21..0,22>         2
<Load>                        None
<BinOp 0,25..0,30>            3 + 4
<Constant 0,25..0,26>         3
<Add 0,27..0,28>              +
<Constant 0,29..0,30>         4
<Load>                        None

Or without the uninteresting `ctx` fields. We set `all=False` (this is actually the default) which excludes usually
ignored nodes like `expr_context`, the various operators and **EMPTY** `arguments` nodes.

>>> for g in f.walk(all=False):
...     print(g.src)
def f(): return [[1, 2], 3 + 4]
return [[1, 2], 3 + 4]
[[1, 2], 3 + 4]
[1, 2]
1
2
3 + 4
3
4

Notice the order of recursion, parents then children going forward. You can also go backward (though it is still parents
before children).

>>> for g in f.walk(back=True):
...     print(g.src)
def f(): return [[1, 2], 3 + 4]
return [[1, 2], 3 + 4]
[[1, 2], 3 + 4]
3 + 4
4
3
[1, 2]
2
1

You can exclude the top-level node.

>>> for g in f.walk(self_=False):
...     print(g.src)
return [[1, 2], 3 + 4]
[[1, 2], 3 + 4]
[1, 2]
1
2
3 + 4
3
4

You can limit the walk to a scope. Which only returns the nodes that belong to that scope and not subscopes (module or
function or lambda or comprehension).

**Note:** There is a function for a common use case of this mode to get all the symbols in a given scope, see
`fst.fst.FST.scope_symbols()`.

>>> f = FST('''
... def f(): f_var = 123
... def g(): pass
... x = y
... '''.strip())

>>> for g in f.walk():
...     print(repr(g.src))
'def f(): f_var = 123\ndef g(): pass\nx = y'
'def f(): f_var = 123'
'f_var = 123'
'f_var'
'123'
'def g(): pass'
'pass'
'x = y'
'x'
'y'

>>> for g in f.walk(scope=True):
...     print(repr(g.src))
'def f(): f_var = 123\ndef g(): pass\nx = y'
'def f(): f_var = 123'
'def g(): pass'
'x = y'
'x'
'y'

You can interact with the generator during the walk to decide whether to recurse into the children or not. For example
if the walk is restricted to a scope you can decide to recurse into a specific child.

>>> for g in (gen := f.walk(scope=True)):
...     print(repr(g.src))
...     if g.is_FunctionDef and g.a.name == 'g':
...         _ = gen.send(True)  # ignore the '_', it shuts up printing the return value
'def f(): f_var = 123\ndef g(): pass\nx = y'
'def f(): f_var = 123'
'def g(): pass'
'pass'
'x = y'
'x'
'y'

If you use the `recurse=False` option then recursion is limited to the top-level node you call it on and its immediate
children (but not **THEIR** children). Note that this is not the same as `scope=True` as that recurses into children
within the scope, this does not.

>>> for g in (gen := f.walk(recurse=False)):
...     print(repr(g.src))
'def f(): f_var = 123\ndef g(): pass\nx = y'
'def f(): f_var = 123'
'def g(): pass'
'x = y'

You can override the `recurse` option by sending to the generator.

>>> for g in (gen := f.walk(recurse=False)):
...     print(repr(g.src))
...     if g.is_FunctionDef and g.a.name == 'f':
...         _ = gen.send(True)
'def f(): f_var = 123\ndef g(): pass\nx = y'
'def f(): f_var = 123'
'f_var = 123'
'f_var'
'123'
'def g(): pass'
'x = y'

For normal walks where things would normally be recursed into, you can decide **NOT** to recurse into children.

>>> for g in (gen := f.walk()):
...     print(repr(g.src))
...     if g.is_FunctionDef and g.a.name == 'f':
...         _ = gen.send(False)
'def f(): f_var = 123\ndef g(): pass\nx = y'
'def f(): f_var = 123'
'def g(): pass'
'pass'
'x = y'
'x'
'y'

You can filter the node types which are returned using the `all` parameter to pass an `AST` node type. Make sure this is
a **LEAF** type, so no `stmt` or `expr` or `mod` which are only bases.

>>> for g in f.walk(all=FunctionDef):
...     print(repr(g.src))
'def f(): f_var = 123'
'def g(): pass'

You can pass multiple types of nodes to return. But if you do this make sure to pass a `set` or `frozenset` or even
`dict` for best performance.

>>> for g in f.walk(all={FunctionDef, Constant}):
...     print(repr(g.src))
'def f(): f_var = 123'
'123'
'def g(): pass'

When you `walk()` nodes, you can modify (or remove) the node being walked. See `fst.fst.FST.walk()`.

>>> f = FST('a * (x.y + u[v])')

>>> for g in f.walk(all=Name):
...     _ = g.replace('new_' + g.id)

>>> print(f.src)
new_a * (new_x.y + new_u[new_v])

You can replace any node within the tree. The replacement doesn't have to be executed on the node being walked, it can
be any node. Note how replacing a node that hasn't been walked yet removes both that node **AND** the replacement node
from the walk. After the walk though, all nodes which were replaced have their new values.

>>> f = FST('[pre_parent, [pre_self, [child], post_self], post_parent]')

>>> for g in f.walk():
...     print(f'{g!r:<23}{g.src[:57]}')
...
...     if g.src == '[child]':
...         _ = f.elts[0].replace('new_pre_parent')
...         _ = f.elts[2].replace('new_post_parent')
...         _ = f.elts[1].elts[0].replace('new_pre_self')
...         _ = f.elts[1].elts[2].replace('new_post_self')
...         _ = f.elts[1].elts[1].elts[0].replace('new_child')
<List ROOT 0,0..0,57>  [pre_parent, [pre_self, [child], post_self], post_parent]
<Name 0,1..0,11>       pre_parent
<List 0,13..0,43>      [pre_self, [child], post_self]
<Name 0,14..0,22>      pre_self
<List 0,24..0,31>      [child]
<Name 0,33..0,42>      new_child

>>> print(f.src)
[new_pre_parent, [new_pre_self, [new_child], new_post_self], new_post_parent]

Replacing or removing a parent node is allowed and the walk will continue where it can.

>>> f = FST('[pre_grand, [pre_parent, [self], post_parent], post_grand]')

>>> for g in f.walk():
...     print(f'{g!r:<23}{g.src[:58]}')
...
...     if g.src == 'self':
...         g.parent.parent.remove()  # [pre_parent, [self], post_parent]
<List ROOT 0,0..0,58>  [pre_grand, [pre_parent, [self], post_parent], post_grand]
<Name 0,1..0,10>       pre_grand
<List 0,12..0,45>      [pre_parent, [self], post_parent]
<Name 0,13..0,23>      pre_parent
<List 0,25..0,31>      [self]
<Name 0,26..0,30>      self
<Name 0,12..0,22>      post_grand

>>> print(f.src)
[pre_grand, post_grand]


## Step

Unlike the `next` and `prev` functions, the `step` functions allow walking forward or backward and going up and down
parents and children automatically. Notice the order is parents before children regardless of if going forward or back,
so the two functions are not inverses unlike the `next` / `prev` functions. You can walk the entire tree just stepping
forward or back one node at a time. See `fst.fst.FST.step_fwd()` and `fst.fst.FST.step_back()`.

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


## Paths

You can get a path from any given node to any of its children using `fst.fst.FST.child_path()`.

>>> f = FST('i = [a * (b + c)]')

>>> _ = f.dump()
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

>>> f.child_path(f.value.elts[0].right.left, as_str=True)  # for the humans
'value.elts[0].right.left'

You can then get the child by this path, either the `astfield` one or the string one, using
`fst.fst.FST.child_from_path()`. Useful for getting the same relative child in a copy of a tree.

>>> g = f.copy()

>>> f.value.elts[0].right.left
<Name 0,10..0,11>

>>> p = f.child_path(f.value.elts[0].right.left)
>>> g.child_from_path(p)  # different tree
<Name 0,10..0,11>

>>> p = f.child_path(f.value.elts[0].right.left, as_str=True)
>>> g.child_from_path(p)  # different tree
<Name 0,10..0,11>
"""
