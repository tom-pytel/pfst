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

>>> _ = a.f.dump()
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

>>> _ = a.body[0].body[0].f.dump()
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

>>> _ = FST('if 1: i = 2', 'exec').dump()
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

>>> _ = FST('if 1: i = 2').dump()
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
<arguments ROOT 0,0..0,0>

Have you ever dreamed of being able to parse the `+` operator by itself? Well now you can!

>>> print(FST('+'))
<Add ROOT 0,0..0,1>

There are some special modes, like `'expr_arglike'`, which allow parsing some things which are not normally parsable in
their usual context. The below is not normally parsable in an expression context as it is special syntax for `Call`
starred arguments. For a full list of parse modes see `fst.parsex.Mode`.

>>> _ = FST('*a or b', 'expr_arglike').dump()
Starred - ROOT 0,0..0,7
  .value BoolOp - 0,1..0,7
    .op Or
    .values[2]
     0] Name 'a' Load - 0,1..0,2
     1] Name 'b' Load - 0,6..0,7
  .ctx Load


## From `AST` nodes

You can also pass `AST` nodes, which are then unparsed (to get the source) and reparsed (because otherwise we couldn't
trust the location information in them). When used like this, the `AST` nodes are **NOT CONSUMED**.

>>> f = FST(Assign(targets=[Name(id='x')], value=Constant(value=1)))

>>> _ = f.dump()
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'x' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5

>>> print(f.src)
x = 1

This also allows normally non-parsable nodes.

>>> _ = FST(Slice(lower=Name(id='a'), upper=Name(id='b'), step=Name(id='c'))).dump('S')
0: a:b:c
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5

If you just pass an `AST` node and no `mode` parameter then the `AST` node is just converted into `FST`. You can however
pass a `mode` parameter to either restrict the context for the `AST` node, such as a standard expression which should
not be a `Slice`.

>>> _ = FST(Slice(lower=Name(id='a'), upper=Name(id='b'), step=Name(id='c')), 'expr')
Traceback (most recent call last):
...
SyntaxError: invalid syntax

If you want to allow this, the mode is `'expr_slice'`.

>>> FST(Slice(lower=Name(id='a'), upper=Name(id='b'), step=Name(id='c')), 'expr_slice')
<Slice ROOT 0,0..0,5>

Or if coercion is possible to a different type of node then this can be done.

>>> _ = FST(Name(id='name'), 'arg').dump('S')
0: name
arg - ROOT 0,0..0,4
  .arg 'name'


## From `FST` nodes

You can pass existing `FST` nodes to `FST()` and it will try to convert the node to the type you request via the `mode`
parameter. If you omit the `mode` parameter, you will just get a copy of the `FST` passed in.

>>> _ = FST(FST('(1, 2)')).dump('s')
0: (1, 2)
Tuple - ROOT 0,0..0,6
  .elts[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,4..0,5
  .ctx Load

>>> _ = FST(FST('(1, 2)'), '_comprehension_ifs').dump('s')
0: if 1 if 2
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[2]
   0] Constant 1 - 0,3..0,4
   1] Constant 2 - 0,8..0,9

These three modes allow the `FST()` constructor to act like the Python `list()` object in that it will convert whatever
you pass in to either the type of `FST` tree it already is or should be in the case of source, or to something else you
specify via the `mode` parameter (if possible).

In the case of `FST` nodes passed in, the conversion or returned node is a copy and the original node is not modified,
so you can be certain of the safety of using `FST()` to try to get the kind of node you are expecting.


## Underlying functions

The `FST(...)` syntax used in the above examples is just a shortcut for the functions `fst.fst.FST.fromsrc()`,
`fst.fst.FST.fromast()` and `fst.fst.FST.as_()`.

>>> _ = FST.fromsrc('i = 1').dump()
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5

Except that `fromsrc()` defaults to `mode='exec'` as shown above instead of minimal node. If you want minimal node
representation then you should pass one of the other modes.

>>> _ = FST.fromsrc('i = 1', 'strict').dump()
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5

`FST.fromast()` works the same as when passing an `AST` to `FST()`.

>>> _ = FST.fromast(Slice(lower=Name(id='a'), upper=Name(id='b'))).dump('s')
0: a:b
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3

The last of these is a coercion function which is more fully explained in`fst.docs.d08_coerce`. It allows conversion
from one type of `FST` to another, if possible.

>>> _ = FST('{a, b, c}').as_(List).dump('s')
0: [a, b, c]
List - ROOT 0,0..0,9
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
  .ctx Load


## Source

A note on the `.src` attribute, it gives the full valid source only if accessed at the root node. If accessed at any
node below, it will return the **INDENTED** source for the location of the node, except for the first line which will be
completely unindented. You can also wind up with unparsable source if you get for example a string `Constant` from the
`values` field of a `JoinedStr`.

If you want unindented source for nodes which are not root, you should use `own_src()`. Or `copy()` that node and get
the source of that (`fst.fst.FST.copy()`), which does even more format fixing. The difference between the `own_src()`
and the `copy().src` is that the former executes much faster (and you don't get a copied node).

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

>>> print(f.body[0].own_src())
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

>>> _ = f.dump(src='stmt')
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
3:     else:
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
