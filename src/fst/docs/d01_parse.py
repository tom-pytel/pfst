r"""
# Parse and unparse from source or `AST`

To be able to execute the examples, import this.

>>> from fst import *

## Parse

Drop-in `ast.parse()` replacement gives normal `AST` (`fst.fst.parse()`).

>>> a = parse('if 1: i = 2  # comment')

>>> print(dump(a, indent=2))
Module(
  body=[
    If(
      test=Constant(value=1),
      body=[
        Assign(
          targets=[
            Name(id='i', ctx=Store())],
          value=Constant(value=2))],
      orelse=[])],
  type_ignores=[])

But it has an `FST` node at `.f`, we can `dump()` it to stdout (`fst.fst.FST.dump()`).

>>> a.f.dump()
Module - ROOT 0,0..0,22
  .body[1]
   0] If - 0,0..0,11
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Assign - 0,6..0,11
        .targets[1]
         0] Name 'i' Store - 0,6..0,7
        .value Constant 2 - 0,10..0,11

## Basic structure

Before anything else, some needed structure information. Every `AST` node in the tree gets an `.f` pointing to its own
`FST` node.

>>> a.body[0].body[0].f.dump()
Assign - 0,6..0,11
  .targets[1]
   0] Name 'i' Store - 0,6..0,7
  .value Constant 2 - 0,10..0,11

Correspondingly, every `FST` node has an `.a` attribute which points to the `AST` node.

>>> a.f.a is a
True

The tree can be traversed downwards either though the `AST` nodes or the `FST` nodes using `AST` field names.

>>> a.body[0].body[0].f
<Assign 0,6..0,11>

>>> a.f.body[0].body[0]
<Assign 0,6..0,11>

>>> a.body[0].f.body[0]
<Assign 0,6..0,11>

>>> type(a.body[0].body[0])
<class 'ast.Assign'>

>>> type(a.f.body[0].body[0].a)
<class 'ast.Assign'>

>>> type(a.f.body[0].a.body[0])
<class 'ast.Assign'>

Note that the `FST` field attributes mirror their respective `AST` attributes and give the corresponding `FST` node. For
more information on structure see `fst.docs.d03_structure`.

## Unparse

Drop-in `ast.unparse()` replacement outputs with formatting (`fst.fst.unparse()`).

>>> print(unparse(a))
if 1: i = 2  # comment

You can also just access the source.

>>> print(a.f.src)
if 1: i = 2  # comment

## Simpler parse

Quicker way to parse which gives the same thing but returns the `FST` node (`fst.fst.FST()`).

>>> FST('if 1: i = 2', 'exec').dump()
Module - ROOT 0,0..0,11
  .body[1]
   0] If - 0,0..0,11
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Assign - 0,6..0,11
        .targets[1]
         0] Name 'i' Store - 0,6..0,7
        .value Constant 2 - 0,10..0,11

Note the `'exec'` mode parameter above, it specifies to parse to a `Module` just like the `'exec'` value for the `mode`
parameter to `ast.parse()`. If you leave it out you will get the minimal reduced `AST` possible, which in this case is
just the `If`.

>>> FST('if 1: i = 2').dump()
If - ROOT 0,0..0,11
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 0,6..0,11
     .targets[1]
      0] Name 'i' Store - 0,6..0,7
     .value Constant 2 - 0,10..0,11

The minimal reduced `AST` does not have to be a statement.

>>> FST('i + j')
<BinOp ROOT 0,0..0,5>

You can parse things that are not normally parsable by themselves.

>>> FST('except Exception: pass')
<ExceptHandler ROOT 0,0..0,22>

Or a comprehension.

>>> print(FST('for a in b if a'))
<comprehension ROOT 0,0..0,15>

You can tell it what you are looking for, either by `AST` type or its name.

>>> print(FST('a:b', Slice))
<Slice ROOT 0,0..0,3>

>>> print(FST('a:b', 'Slice'))
<Slice ROOT 0,0..0,3>

Because maybe it is normally shadowed by something more common.

>>> print(FST('a:b'))
<AnnAssign ROOT 0,0..0,3>

In some cases you must tell it what you want (valid empty arguments).

>>> print(FST('', arguments))
<arguments ROOT>

Have you ever dreamed of being able to parse the `+` operator by itself? Well now you can!

>>> print(FST('+'))
<Add ROOT 0,0..0,1>

There are some special modes, like `'expr_arglike'`, which allow parsing some things which are not normally parsable in
their usual context. The below is not normally parsable in an expression context as it is special syntax for `Call`
starred arguments. For a full list of parse modes see `fst.parsex.Mode`.

>>> FST('*a or b', 'expr_arglike').dump()
Starred - ROOT 0,0..0,7
  .value BoolOp - 0,1..0,7
    .op Or
    .values[2]
     0] Name 'a' Load - 0,1..0,2
     1] Name 'b' Load - 0,6..0,7
  .ctx Load

## From `AST` nodes

You can also pass `AST` nodes, which are then unparsed and reparsed (because otherwise we couldn't trust the location
information in them). When used like this, the `AST` nodes are **NOT CONSUMED**.

>>> f = FST(Assign(targets=[Name(id='x')], value=Constant(value=1)))

>>> f.dump()
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'x' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5

>>> print(f.src)
x = 1

This also allows normally non-parsable nodes.

>>> FST(Slice(lower=Name(id='a'), upper=Name(id='b'), step=Name(id='c'))).dump()
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5

## Underlying functions

The `FST(...)` syntax used in the above examples is just a shortcut for the functions `fst.fst.FST.fromsrc()` and
`fst.fst.FST.fromast()`.

>>> FST.fromsrc('i = 1').dump()
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5

Except that `fromsrc()` defaults to `mode='exec'` instead of minimal node.

>>> FST.fromsrc('i = 1', 'strict').dump()
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5

`FST.fromast()` works the same as when passing an `AST` to `FST()`.

>>> FST.fromast(Slice(lower=Name(id='a'), upper=Name(id='b'), step=Name(id='c'))).dump()
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5

## Source

A note on the `.src` attribute, it gives the full valid source only if accessed at the root node. If accessed at any
node below, it will return the **INDENTED** source for the location of the node, except for the first line which will be
completely unindented. If you want full correctly unindented source for nodes which are not root, you should `copy()`
that node and get the source of that (`fst.fst.FST.copy()`). E.g.

>>> f = FST('''
... def f(a):
...     if a:
...         print(a)
...     else:
...         print(-a)
... '''.strip())

>>> print(f.body[0])
<If 1,4..4,17>

>>> print(f.src)
def f(a):
    if a:
        print(a)
    else:
        print(-a)

>>> print(f.body[0].src)
if a:
        print(a)
    else:
        print(-a)

>>> print(f.body[0].copy().src)
if a:
    print(a)
else:
    print(-a)

The `FST.dump()` method can be useful in visualizing the source along with the actual nodes it corresponds to.

>>> f.dump(src='stmt')
0: def f(a):
FunctionDef - ROOT 0,0..4,17
  .name 'f'
  .args arguments - 0,6..0,7
    .args[1]
     0] arg - 0,6..0,7
       .arg 'a'
  .body[1]
1:     if a:
   0] If - 1,4..4,17
     .test Name 'a' Load - 1,7..1,8
     .body[1]
2:         print(a)
      0] Expr - 2,8..2,16
        .value Call - 2,8..2,16
          .func Name 'print' Load - 2,8..2,13
          .args[1]
           0] Name 'a' Load - 2,14..2,15
     .orelse[1]
4:         print(-a)
      0] Expr - 4,8..4,17
        .value Call - 4,8..4,17
          .func Name 'print' Load - 4,8..4,13
          .args[1]
           0] UnaryOp - 4,14..4,16
             .op USub - 4,14..4,15
             .operand Name 'a' Load - 4,15..4,16
"""
