r"""
# Modifying nodes

To be able to execute the examples, import this.

>>> from fst import *

## `Code` for modifying

When modifying a node, you specify what to replace the node `AST` with. You can pass this as either source code, an
`AST` node or an `FST` root node. If an `FST` node is used then it should be considered consumed on use, whether the
modification succeeds or not. `AST` nodes are not consumed as they are unparsed and then reparsed in order to make sure
their locations are correct. Source code in the form of a string or a list of lines is also not consumed.

>>> FST.new().body.append('i = 1').root.src
'i = 1'

>>> FST.new().body.append(['i = 1']).root.src
'i = 1'

>>> FST.new().body.append(Assign(targets=[Name(id='i')],
...                              value=Constant(value=1))).root.src
'i = 1'

>>> FST.new().body.append(FST('i = 1')).root.src
'i = 1'

## `replace()` and `remove()`

`remove()` does what it says. Basically the same as `cut()` except that it doesn't return anything. Doesn't do the
processing needed for the copy before removing the node, its just a shortcut for `put(None)`. Just like `cut()`, you
cannot `remove()` the root node obviously (`fst.fst.FST.remove()`).

>>> f = FST('[1, 2, 3]')

>>> f.elts[1].remove()

>>> print(f.src)
[1, 3]

>>> f = FST('''
... i = 1
... j = 2
... k = 3
... '''.strip())

>>> f.body[1].remove()

>>> print(f.src)
i = 1
k = 3

`replace(code)` is just a `put(code)` executed in the parent normally. Except at the root node level where it allows you
to replace the root node `AST` without changing the top level `FST` so that it remains valid wherever you reference the
tree through the root node (`fst.fst.FST.replace()`).

>>> f = FST('[1, 2, 3]')

>>> f.elts[1].replace('a()')
<Call 0,4..0,7>

>>> print(f.src)
[1, a(), 3]

>>> f.elts[2].replace(Call(func=Name(id='blah'), args=[], keywords=[]))
<Call 0,9..0,15>

>>> print(f.src)
[1, a(), blah()]

>>> f.elts[0].replace(FST('j := 3'))
<NamedExpr 0,2..0,8>

Notice the parentheses added atomatically (because they are needed).

>>> print(f.src)
[(j := 3), a(), blah()]

The `replace()` function returns the new replaced node, as the actual `FST` node (regardless of the contents) can be
different from the original `FST` at this location under some circumstances (raw put). Except for the root `FST` node,
which is the only one guarenteed to never change under any circumstances.

>>> f = FST('i = 1')

>>> g = f.value

>>> g.replace('2') is g
True

>>> print(f.src)
i = 2

>>> g.replace('3', raw=True) is g
False

>>> print(f.src)
i = 3

Non-raw replace operations take into account precedence and parsability and parenthesize as needed by default.

>>> f = FST('i * j')

>>> f.right.replace('x + y')
<BinOp 0,5..0,10>

>>> print(f.src)
i * (x + y)

This can be turned off, in which case it can lead to invalid source code which does not match the tree structure.

>>> f.left.replace('a + b', pars=False)
<BinOp 0,0..0,5>

>>> print(f.src)
a + b * (x + y)

>>> bool(f.verify(raise_=False))
False

It is possible that with a raw operation a node disappears entirely and there is no new node at its previous location.
In this case, `None` is returned as the new node.

>>> f = FST('"a" + "b"')

>>> f.dump()
BinOp - ROOT 0,0..0,9
  .left Constant 'a' - 0,0..0,3
  .op Add - 0,4..0,5
  .right Constant 'b' - 0,6..0,9

>>> f.op.replace('\\\n', raw=True) is None
True

>>> f.dump('stmt')
0: "a" \
1:  "b"
Constant 'ab' - ROOT 0,0..1,4

## `put()` and `put_slice()`

Just like with `copy()` and `cut()` using `get()`, `put()` is the underlying function used by `replace()` and `remove()`.
`put()` can replace a node or delete it if `None` is passed as the replacement. It cannot put anything to a root node as
it requires a parent to operate on a node, so if you want to replace a root node you must use `replace()`. The
parameters are similar to the `get()` function except that the first parameter is always the `Code` to put or `None`
(`fst.fst.FST.put()`).

>>> f = FST('[1, 2, 3]')

>>> f.put('x', 1)
<List ROOT 0,0..0,9>

>>> print(f.src)
[1, x, 3]

Just like `get()`, `put()` can operate on single elements or slices. It can do everything that `put_slice()` can do, but
not vice versa.

>>> f.put('y', 1, 3)
<List ROOT 0,0..0,6>

>>> print(f.src)
[1, y]

Notice how it replaced two elements with a single one. This is because the normal mode of `put()` is to put as a single
element, not as a slice. You can specify slice operation via the `one` parameter, which is normally `True` for `put()`.

>>> f.put('[a, b, c]', 1, None)
<List ROOT 0,0..0,14>

>>> print(f.src)
[1, [a, b, c]]

>>> f.put('[a, b, c]', 1, None, one=False)
<List ROOT 0,0..0,12>

>>> print(f.src)
[1, a, b, c]

Putting `None` deletes and it can delete multiple elements.

>>> f.put(None, 1, 3)
<List ROOT 0,0..0,6>

>>> print(f.src)
[1, c]

Slices from compatible containers can be put to each other.

>>> s = FST('[1, 2, 3, 4]').get_slice(1, None)

>>> print(s.src)
[2, 3, 4]

>>> print(FST('{a, b, c, d}').put_slice(s, 1, 3).root.src)
{a, 2, 3, 4, d}

Either `put()` or `put_slice()` can be used to insert by setting the `start` and `stop` locations to the same thing,
possibly at the start, end or between other elements (`fst.fst.FST.put_slice()`).

>>> f.put('[x]', 1, 1, one=False)
<List ROOT 0,0..0,9>

>>> print(f.src)
[1, x, c]

`put_slice()` doesn't need `one=False` as that is the default there.

>>> f.put_slice('[y]', 2, 2)
<List ROOT 0,0..0,12>

>>> print(f.src)
[1, x, y, c]

The special `'end'` index allows you to put at the end without knowing how long the field is.

>>> f.put_slice('[4,5,6]', 'end')
<List ROOT 0,0..0,19>

>>> print(f.src)
[1, x, y, c, 4,5,6]

Just like with `get()`, a field can be specified.

>>> f = FST('''
... if 1:
...     i = 1
... else:
...     j = 2
... '''.strip())

>>> f.put('k = 3', 'end', None, 'orelse')
<If ROOT 0,0..4,9>

>>> print(f.src)
if 1:
    i = 1
else:
    j = 2
    k = 3

`put()` and `put_slice()` return the object on which they were called (the parent of the put) for the same reason that
`replace()` returns the new node. Normally the object will be unchanged, but with raw operations it can change and in
order to continue operating on the same element in the tree you need the new `FST` node.

>>> f = FST('i = [1, 2, 3]')

>>> g = f.value

>>> g.put('x', 1) is g
True

>>> print(f.src)
i = [1, x, 3]

>>> h = g.put('y', 2, raw=True)

>>> h is g
False

>>> print(f.src)
i = [1, x, y]

You can put some fields as primitives.

>>> f = FST('case True: pass')

>>> f.pattern
<MatchSingleton 0,5..0,9>

>>> f.pattern.put(False)
<MatchSingleton 0,5..0,10>

>>> print(f.src)
case False: pass

>>> f = FST('b"bytes"')

>>> f.dump()
Constant b'bytes' - ROOT 0,0..0,8

>>> f.put(2.5)
<Constant ROOT 0,0..0,3>

>>> f.dump()
Constant 2.5 - ROOT 0,0..0,3

>>> print(f.src)
2.5

## By attribute

Just like with getting, it is possible to assign directly to an `AST` field on an `FST` node and have that assignment
processed from the point of view of `FST`. This means that you can assign an `FST` node and all the proper source code
movements and `AST` setting will be done automatically. Under the hood these assignments are just carried out using
`put()` and  `put_slice()`, so results will be the same between the two methods.

>>> f = FST('i, j = [x, 2.5]')

>>> f.targets[0].elts[0] = FST('name')

>>> print(f.src)
name, j = [x, 2.5]

>>> f.targets[0] = Name(id='z')

>>> print(f.src)
z = [x, 2.5]

>>> f.value.elts[1:2] = 'a, b'  # this is a view operation, but just to give an idea

>>> print(f.src)
z = [x, a, b]

>>> f.value.elts = 'c, d, e'

>>> print(f.src)
z = [c, d, e]

You can also delete by attribute.

>>> del f.value.elts[1:]

>>> print(f.src)
z = [c]

>>> del f.value.elts

>>> print(f.src)
z = []

>>> f = FST('def f() -> int: pass')

>>> del f.returns

>>> print(f.src)
def f(): pass

## `put_src()`

Unlike `get_src()` which is a very simple function, `put_src()` (`fst.fst.FST.put_src()`) doesn't just put text to the
source code and leave it at that. Since changing the source can change the location of `AST` nodes or even the tree
structure, `put_src()` may account for this by either reparsing the part of the source which was changed or offsetting
`AST` nodes around the changes. The desired behavior is selected via the `action` parameter.

The options are:
- `'reparse'`: Attempt reparse of source around the change and modify `AST` tree accordingly.
- `'offset'`: Just offset existing nodes according to the changes. Use this only if you are sure the actual structure
    of the tree does not change.
- `None`: Do not modify the `AST` tree at all. This will almost certainly result in desynchronized source code and `AST`
    tree unless you are absolutely sure the change does not affect any `AST` locations or the tree itself (trailing
    line comment on a statement).

### `put_src(action='reparse')`

This is the default action and uses the same raw reparse mechanism to do its job as raw node operations. But unlike
those, which may modify the source put a little bit depending on circumstances, `put_src()` puts the source exactly as
you specify it.

If the changes are not valid then neither the tree nor the source is actually changed. `fst` attempts to minimize the
amount of code which is reparsed and the minimum elemenent that can be reparsed is a single statement or block statement
header. Though multiple statements or even entire blocks may be reparsed if the changes span those blocks. Whatever is
reparsed will have its `FST` nodes changed, except the root node.

The actual location for the reparse is not restricted in any way. It doesn't have to fall on node bondaries and can
extend over the entire source code if need be. Like `get_src()`, it doesn't matter what node of the tree this function
is called on in this mode, the domain is always over the entire tree.

>>> f = FST('''
... if a < b:
...     if c < d:
...         s()
...     else:
...         t()
... '''.strip())

>>> f.put_src('''
... = x:
...     if y !=
... '''.strip(), 0, 6, 1, 10)
(1, 11)

>>> print(f.src)
if a <= x:
    if y != d:
        s()
    else:
        t()

>>> f.put_src('a <', 1, 7, 1, 11)
(1, 10)

>>> print(f.src)
if a <= x:
    if a < d:
        s()
    else:
        t()

The `put_src()` function returns the position of the end of the source modification (in the new source). This position
along with the start position of the modification can be used to find any resulting changed nodes using the `find*()`
functions.

>>> f.find_loc(1, 7, 1, 10).src
'a'

We got `a` because that is the first node in the modified part. If you want the lowest level node which completely
encompasses the modification then use `find_loc_in()`.

>>> f.find_loc_in(1, 7, 1, 10).src
'a < d'

As stated above, the source you pass in is not modified in any way, including indentation, so you must make sure
everything is correct with respect to this and parentheses and everything else. Note the `elif` in the replacement
source below is not indented because it is put right at the beginning of the statement it is replacing. Likewise the
`pass` is indented twice since it starts its own line and that is the indentation level for that block of code.

>>> f.put_src('''
... elif z != e:
...         pass
... '''.strip(), 3, 4, 4, 11)
(4, 12)

>>> print(f.src)
if a <= x:
    if a < d:
        s()
    elif z != e:
        pass

### `put_src(action='offset')`

This does not do any reparsing and only offsets existing nodes according to the location of the source change and the
node that the `put_src()` function was called on. Unlike with `'reparse'`, in this mode the node you use to call the
function actually has an effect and determines which node you are modifying **INSIDE** of. All children of this node are
considered **OUTSIDE** the modification and are offset differently from the calling node and its parents.

This action will only wind up with a valid and synchronized source and tree if you use it to change essentially whitespace
and trivia. You can use it to change non-coding source like the `=` in an `Assign` node or the locations of commas, but
any changes to things which are actually stored inside `AST` nodes must be carried out in `'reparse'` mode.

Example using `'offset'` to change the spacing in a `Tuple`.

>>> f = FST('(a, b, c)')

>>> f.dump()
Tuple - ROOT 0,0..0,9
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
  .ctx Load

>>> f.put_src('  ', 0, 2, 0, 2)
(0, 4)

>>> print(f.src)
(a  , b, c)

>>> f.dump()
Tuple - ROOT 0,0..0,11
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,6..0,7
   2] Name 'c' Load - 0,9..0,10
  .ctx Load

>>> bool(f.verify())
True

Note how we did the change inside the `Tuple` but outside its children. If we had done the change for example inside
the `a` child we would be increasing the size of that and wind up with an invalid node.

>>> f = FST('(a, b, c)')

>>> f.elts[0].put_src('  ', 0, 2, 0, 2, action='offset')
(0, 4)

>>> print(f.src)
(a  , b, c)

>>> f.dump()  # note the location of the Name 'a' node is wrong
Tuple - ROOT 0,0..0,11
  .elts[3]
   0] Name 'a' Load - 0,1..0,4
   1] Name 'b' Load - 0,6..0,7
   2] Name 'c' Load - 0,9..0,10
  .ctx Load

>>> bool(f.verify(raise_=False))
False

### `put_src(action=None)`

This just doesn't touch the `AST` tree at all, or the `FST` node caches, its meant to be fast. Gun, meet foot. There is
a use for this, it is much faster than the other two modes for changing trivia, but only if you understand exactly what
is going on.

To be absolutely safe after using this mode, do a `root._touchall()` on your tree so the caches get flushed (block
statement `.bloc`s may change due to changes to tail inline comments in last child, even though `AST` locations didn't
change).

>>> f = FST('(a, b, c)')

>>> f.elts[0].put_src('  ', 0, 2, 0, 2, action=None)
(0, 4)

>>> print(f.src)
(a  , b, c)

>>> f.dump()  # note the locations of everything except 'a' are wrong
Tuple - ROOT 0,0..0,9
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
  .ctx Load

>>> bool(f.verify(raise_=False))
False
"""
