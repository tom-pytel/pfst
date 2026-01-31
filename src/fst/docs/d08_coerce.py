r"""
# Coercion and slice put as `one`

To be able to execute the examples, import this.

>>> from fst import *


## Coercion

The `AST` tree structure expects specific types of nodes for specific fields. An `a = b` `Assign` node expects an
expression for its value, not for example an argument, even if the argument **LOOKS** just like a `Name` expression in
source code. In short, you cannot put an `arg` node into an assignment.

>>> FST('a = b').put(FST('x', 'arg'), 'value', coerce=False).src
Traceback (most recent call last):
...
fst.NodeError: expecting expression (standard), got arg, coerce disabled

Unless you allow `fst` to do coercion, which by default is turned on.

>>> _ = FST('a = b').put(FST('x', 'arg'), 'value').dump('S')
0: a = x
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5

Note that the value wound up as a `Name` node type and not the `arg` we passed in. This is the kind of coercion `fst`
allows. You can assign node types which are not normally valid for a given location in a tree but which **LOOK** like
they should work.


## Coercion on put

When you put a **NODE** (`AST` or `FST`), as opposed to source text, to a target, coercion has a chance to happen if the
node type does not match what is expected. The types of coercion that might occur are:

- Lifting an `arg` or `keyword` to `arguments`.

>>> (f := FST('def f(): pass')).args = FST('a: int', 'arg')

>>> _ = f.dump('S')
0: def f(a: int):
FunctionDef - ROOT 0,0..0,19
  .name 'f'
  .args arguments - 0,6..0,12
    .args[1]
     0] arg - 0,6..0,12
       .arg 'a'
       .annotation Name 'int' Load - 0,9..0,12
  .body[1]
0:                pass
   0] Pass - 0,15..0,19

>>> (f := FST('def f(): pass')).args = FST('**kw', 'keyword')

>>> _ = f.dump('S')
0: def f(**kw):
FunctionDef - ROOT 0,0..0,17
  .name 'f'
  .args arguments - 0,6..0,10
    .kwarg arg - 0,8..0,10
      .arg 'kw'
  .body[1]
0:              pass
   0] Pass - 0,13..0,17

- Or single `withitem` to a list of them.

>>> (f := FST('with a: pass')).items = FST('x as y', 'withitem')

>>> _ = f.dump('S')
0: with x as y:
With - ROOT 0,0..0,17
  .items[1]
   0] withitem - 0,5..0,11
     .context_expr Name 'x' Load - 0,5..0,6
     .optional_vars Name 'y' Store - 0,10..0,11
  .body[1]
0:              pass
   0] Pass - 0,13..0,17

Coercion generally doesn't go in the other direction, from container of elements to single element. With the exception
of containers which **ARE** the thing they contain, like a `List` being an expression.

- Converting compatible sequences like a `Tuple` to a list of `alias`es in an `Import`.

>>> (f := FST('import a, b')).names[1:] = FST('x, y', 'Tuple')

>>> _ = f.dump('S')
0: import a, x, y
Import - ROOT 0,0..0,14
  .names[3]
   0] alias - 0,7..0,8
     .name 'a'
   1] alias - 0,10..0,11
     .name 'x'
   2] alias - 0,13..0,14
     .name 'y'

The coercion can change source as well as changing the node type.

>>> (f := FST('class cls: pass')).decorator_list = FST('[deco1, deco2()]', 'List')

>>> _ = f.dump('S')
0: @deco1
1: @deco2()
2: class cls:
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
2:            pass
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'deco1' Load - 0,1..0,6
   1] Call - 1,1..1,8
     .func Name 'deco2' Load - 1,1..1,6

- Between expressions and patterns

>>> (f := FST('{a: b, c: d}'))._all[1:] = FST('{1: x, **rest}', 'MatchMapping')

>>> _ = f.dump('S')
0: {a: b, 1: x, **rest}
Dict - ROOT 0,0..0,20
  .keys[3]
   0] Name 'a' Load - 0,1..0,2
   1] Constant 1 - 0,7..0,8
   2] None
  .values[3]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'x' Load - 0,10..0,11
   2] Name 'rest' Load - 0,15..0,19

>>> (f := FST('case _: pass')).pattern = FST('cls(a, b, c=d)', 'expr')

>>> _ = f.dump('S')
0: case cls(a, b, c=d):
match_case - ROOT 0,0..0,25
  .pattern MatchClass - 0,5..0,19
    .cls Name 'cls' Load - 0,5..0,8
    .patterns[2]
     0] MatchAs - 0,9..0,10
       .name 'a'
     1] MatchAs - 0,12..0,13
       .name 'b'
    .kwd_attrs[1]
     0] 'c'
    .kwd_patterns[1]
     0] MatchAs - 0,17..0,18
       .name 'd'
  .body[1]
0:                      pass
   0] Pass - 0,21..0,25

- Various other miscellaneous convertions, more to be added.

>>> (f := FST('a = b')).targets = \
...     FST('[i for i in j if i if j]').generators[0].ifs.copy()

>>> _ = f.dump('S')
0: i = j = b
Assign - ROOT 0,0..0,9
  .targets[2]
   0] Name 'i' Store - 0,0..0,1
   1] Name 'j' Store - 0,4..0,5
  .value Name 'b' Load - 0,8..0,9

>>> (f := FST('a + b')).right = FST('call()', 'Module')

>>> _ = f.dump('S')
0: a + call()
BinOp - ROOT 0,0..0,10
  .left Name 'a' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Call - 0,4..0,10
    .func Name 'call' Load - 0,4..0,8


## Explicit coercion using `as_()`

You can try to coerce an existing `FST` node to something else without putting it to anything using the `as_()` method.

>>> _ = (f := FST('a.b', 'alias')).as_(expr).dump('S')
0: a.b
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load

>>> _ = FST('[a, b(), c(x=y)]', 'MatchSequence').as_('_decorator_list').dump('S')
0: @a
1: @b()
2: @c(x=y)
_decorator_list - ROOT 0,0..2,7
  .decorator_list[3]
   0] Name 'a' Load - 0,1..0,2
   1] Call - 1,1..1,4
     .func Name 'b' Load - 1,1..1,2
   2] Call - 2,1..2,7
     .func Name 'c' Load - 2,1..2,2
     .keywords[1]
      0] keyword - 2,3..2,6
        .arg 'x'
        .value Name 'y' Load - 2,5..2,6

The `as_()` method can be used on any node, not just a root node

>>> FST('import a.b').names[0]
<alias 0,7..0,10>

>>> FST('import a.b').names[0].as_(expr)
<Attribute ROOT 0,0..0,3>

Like most functions which can take an `FST` node as a parameter, the coercion attempt is destructive by default if the
node you are calling it on is a root node. Meaning that the original `FST` that `as_()` is called on should be
considered consumed after the call, even if the coercion fails.

>>> f = FST('a.b', 'alias')

>>> bool(f.verify(raise_=False))
True

>>> f.as_(expr)
<Attribute ROOT 0,0..0,3>

>>> bool(f.verify(raise_=False))
False

If you do not want to destroy the original node you can pass `copy=True` which will make a copy of the node and
coerce that destructively. Or just make a copy yourself and coerce that.

>>> f = FST('a.b', 'alias')

>>> bool(f.verify(raise_=False))
True

>>> f.as_(expr, copy=True)
<Attribute ROOT 0,0..0,3>

>>> bool(f.verify(raise_=False))
True

This only applies to root nodes. If you call `as_()` on a non-root node then it is always copied as a first step before
the coercion and the original is left unchanged.

If you do not pass a `mode` parameter to the `as_()` method then you will just get back the original node, or a copy if
the original was not root or `copy=True`.

>>> (f := FST('a = b')).as_() is f
True

>>> (f := FST('a = b')).as_(copy=True) is f
False

>>> (f := FST('a = b')).value.as_() is f.value
False


## Explicit coercion using `FST()`

In addition to the `as_()` method, you can coerce an `FST` node by passing it to the `FST()` constructor with a
different `mode` / type than what that `FST` currently is. This will just call `as_()` under the hood, but in this case
it defaults to non-destructive copy coercion so that the original node passed to the `FST()` constructor is not
consumed, root node or not.

>>> f = FST('a.b', 'alias')

>>> FST(f, expr)
<Attribute ROOT 0,0..0,3>

>>> bool(f.verify(raise_=False))
True

The `FST()` constructor also takes the `copy` parameter as a keyword in this case to allow you to do destructive
coercion if you want.

>>> FST(f, expr, copy=False)
<Attribute ROOT 0,0..0,3>

>>> bool(f.verify(raise_=False))
False

The advantage of using the `FST()` constructor is that it also accepts `AST` nodes for coercion. By default if you call
`FST(ast)` without a mode then all that happens is that an `FST` tree is built for the given `AST` node, no changes are
made to the type.

>>> _ = FST(alias(name='a.b')).dump('S')
0: a.b
alias - ROOT 0,0..0,3
  .name 'a.b'

However, if you provide a `mode` then coercion is attempted to the type you request.

>>> _ = FST(alias(name='a.b'), 'expr').dump('S')
0: a.b
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load

When passing an `AST` node like this, the `AST` itself is never consumed as it is always reparsed to get locations. This
applies to `AST` nodes passed to any put function and even `FST.fromast()`.


## `FST()` as a normalizer

You might notice that the coercion usage of the `FST()` constructor mirrors the usage when you pass source. If you do
not provide a `mode` then you get the best parse that `fst` can find for that source. But if you provide a mode then you
will only get that type or an error.

>>> FST('a.b')
<Attribute ROOT 0,0..0,3>

>>> FST('a.b', 'alias')
<alias ROOT 0,0..0,3>

>>> FST('a.b', 'Tuple')
Traceback (most recent call last):
...
fst.ParseError: expecting Tuple, got Attribute

This means that you can use the `FST()` constructor to ensure that you have a certain `FST` node type regardless of what
input you give it, source, `AST` or another `FST`. Or just to make sure you have an `FST` node if you leave out the
`mode` parameter.

>>> FST('name', Name)
<Name ROOT 0,0..0,4>

>>> FST(MatchAs(name='name'), Name)
<Name ROOT 0,0..0,4>

>>> FST(FST('name', 'alias'), Name)
<Name ROOT 0,0..0,4>

>>> FST(withitem(context_expr=Name(id='name')), Name)
<Name ROOT 0,0..0,4>

>>> FST(Module(body=[Expr(value=Name(id='name'))], type_ignores=[]), Name)
<Name ROOT 0,0..0,4>

>>> FST(FST('a.b', 'Attribute'), Name)
Traceback (most recent call last):
...
fst.NodeError: expecting Name, got Attribute, could not coerce

>>> FST(Set(elts=[]), Name)
Traceback (most recent call last):
...
fst.NodeError: expecting Name, got Set, could not coerce


## Slice put `one` parameter

This parameter to put functions specifies whether you want to put the node you are passing as a single element (if
applicable) or as a multi-element slice. For the `put_slice()` function this parameter defaults to `False`, which means
you want to put the node you are passing as an actual slice and not a single element.

Other functions which normally put a single element like `put()`, `replace()` and `insert()` also take this parameter
where it defaults to `True`. This allows you to use those functions as slice puts as well.

The parameter itself serves two similar purposes and overlaps a little with `coerce` (in that it can convert a single
element node to a singleton slice node for the put).

1. If passing a node which is a slice type for the target you are putting to, passing `one=False` will put that node as
the slice it is, but passing `one=True` will put that node as a single element if possible.

>>> FST('[a, b]').put_slice(FST('[x, y]'), 1, 1).src
'[a, x, y, b]'

>>> FST('[a, b]').put_slice(FST('[x, y]'), 1, 1, one=True).src
'[a, [x, y], b]'

2. If passing a node which is not a slice type for the target, but is a contained element type for that target, it is
normally converted to the slice type due to the global default `coerce=True`.

>>> FST('[a, b, c, d]').put_slice(FST('x'), 1, 3).src
'[a, x, d]'

However, if coerce is turned off then this does not happen automatically.

>>> FST('[a, b, c, d]').put_slice(FST('x'), 1, 3, coerce=False).src
Traceback (most recent call last):
...
ValueError: cannot put Name as slice to List without 'one=True' or 'coerce=True'

Unless you pass `one=True` in this case.

>>> FST('[a, b, c, d]').put_slice(FST('x'), 1, 3, coerce=False, one=True).src
'[a, x, d]'


## Node vs. source puts

`fst` put functions allow you to pass an `FST` node, an `AST` node or pure source code as the code element to put
functions. When the source node to put is an actual `FST` or `AST` node then the operation is straightforward.

If the node type is a slice type then it is put as a slice if `one=False` and a single element if possible if
`one=True`. If the code to put that you pass is text source code however, it is treated slightly differently.

If it is delimited then it is put as a single element regardless of setting `one=False`.

>>> FST('[a, b]').put_slice('[x, y]', 1, 1, one=False).src
'[a, [x, y], b]'

If you want to put source as an actual slice then it either must not have delimiters in the text.

>>> FST('[a, b]').put_slice('x, y', 1, 1, one=False).src
'[a, x, y, b]'

Or you can use the special value `one=None`.

>>> FST('[a, b]').put_slice('[x, y]', 1, 1, one=None).src
'[a, x, y, b]'

The `one=None` is a special value for expression sequences `Tuple`, `List` and `Set` only (and `Delete.targets`,
`Global.names` and `Nonlocal.names` since their slice type is a normal `Tuple`). It acts as a normal `one=False` for
all other slice targets.

>>> FST('call(a, b)').put_slice('[x, y]', 1, 1, 'args', one=False).src
'call(a, [x, y], b)'

>>> FST('call(a, b)').put_slice('[x, y]', 1, 1, 'args', one=None).src
'call(a, [x, y], b)'

>>> FST('a = b = c').put_slice('[x, y]', 1, 1, 'targets', one=False).src
'a = [x, y] = b = c'

>>> FST('a = b = c').put_slice('[x, y]', 1, 1, 'targets', one=None).src
'a = [x, y] = b = c'

Using `one=True` to allow single contained element usage as a singleton slice is unnecessary unless `coerce=False`.

>>> FST('call(a, b, c, d)') \
...     .put_slice(FST('x'), 1, 3, 'args', one=False).src
'call(a, x, d)'

>>> FST('call(a, b, c, d)') \
...     .put_slice(FST('x'), 1, 3, 'args', coerce=False, one=False).src
Traceback (most recent call last):
...
fst.NodeError: expecting Tuple, got Name, coerce disabled

>>> FST('call(a, b, c, d)') \
...     .put_slice(FST('x'), 1, 3, 'args', coerce=False, one=True).src
'call(a, x, d)'

>>> FST('a = b = c = d = e') \
...     .put_slice(FST('x'), 1, 3, 'targets', one=False).src
'a = x = d = e'

>>> FST('a = b = c = d = e') \
...     .put_slice(FST('x'), 1, 3, 'targets', coerce=False, one=False).src
Traceback (most recent call last):
...
fst.NodeError: expecting _Assign_targets, got Name, coerce disabled

>>> FST('a = b = c = d = e') \
...     .put_slice(FST('x'), 1, 3, 'targets', coerce=False, one=True).src
'a = x = d = e'

If you pass a single element as text source instead of a node for most slice targets other than `Tuple`, `List` or
`Set`, it will work without `one=True` or `coerce=True` as the parsing for those slice target types accept single
elements as singleton sequences, since those target sequences normally don't require trailing separators to indicate a
sequence.

>>> FST('call(a, b, c, d)') \
...     .put_slice('x', 1, 3, 'args', coerce=False, one=False).src
'call(a, x, d)'

>>> FST('a = b = c = d = e') \
...     .put_slice('x', 1, 3, 'targets', coerce=False, one=False).src
'a = x = d = e'


## Using `one=False` in single-element functions

As mentioned above, several normally single-element functions also take the `one` parameter which allows them to do what
they do but as a multi-element slice.

>>> FST('[a, b, c, d]').put(FST('[x, y]'), 1, 3).src
'[a, [x, y], d]'

>>> FST('[a, b, c, d]').put(FST('[x, y]'), 1, 3, one=False).src
'[a, x, y, d]'

>>> FST('[a, b]').insert(FST('[x, y]'), 1).src
'[a, [x, y], b]'

>>> FST('[a, b]').insert(FST('[x, y]'), 1, one=False).src
'[a, x, y, b]'

>>> FST('[a, b, c]').elts[1].replace(FST('[x, y]')).root.src
'[a, [x, y], c]'

>>> FST('[a, b, c]').elts[1].replace(FST('[x, y]'), one=False).root.src
'[a, x, y, c]'
"""
