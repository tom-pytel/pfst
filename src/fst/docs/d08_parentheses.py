r"""
# Parentheses handling

To be able to execute the examples, import this.
```py
>>> from fst import *
```

## Types of parentheses

In Python, parentheses can exist for one of three general sometimes overlapping reasons:

1. Specifying precedence.
2. Enclosing otherwise non-parsable code, due to being spread over multiple lines without line continuations.
3. As an intrinsic part of the node, like the parentheses of a tuple or the argument parentheses of a function
definition.

All of these are handled automatically, if you want.

```py
>>> f = FST('a * b')

>>> f.left.replace('x + y')
<BinOp 0,1..0,6>

>>> print(f.src)
(x + y) * b

>>> bool(f.verify(raise_=False))
True
```

The parentheses were added above because otherwise the tree would not reparse to the same structure. This behavior can be turned off if you really want via the `pars` option.

```py
>>> f.right.replace('u + v', pars=False)
<BinOp 0,10..0,15>

>>> print(f.src)
(x + y) * u + v
```

But now the tree is incorrect.

```py
>>> bool(f.verify(raise_=False))
False
```

Parentheses for parsability are added if the given operation would wind up with non-parsable code or code which would
parse to a different structure.

```py
>>> f = FST('i = a, b')

>>> f.value.elts[1] = 'c\n+\nd'

>>> print(f.src)
i = a, (c
+
d)
```

A confusing category are parentheses which may be needed for parsability but which belong to a parent node.

```py
>>> f = FST('with a: pass')

>>> f.items[0].replace('c\nas\nd')
<withitem 0,6..2,1>

>>> print(f.src)
with (c
as
d): pass
```

These parentheses belong to the `with` node and cannot be removed by the user.

```py
>>> f.items[0].unpar()
<withitem 0,6..2,1>

>>> print(f.src)
with (c
as
d): pass
```

## Parentheses on get

When getting nodes, parentheses may be copied or not depending on the `pars` setting (normally not copied), and they may
be added after the cut or copy to the new node to make it parsable.

```py
>>> f = FST('''[a
... +
... b]''')

>>> g = f.elts[0].copy()

>>> print(g.src)
(a
+
b)
```

Parentheses are not normally copied (and not added) to expressions which do not need them alone.

```py
>>> f = FST('a * (x + y)')

>>> g = f.right.copy()

>>> print(g.src)
x + y
```

You can specify that you want parentheses copied if they are present with `pars=True`. This will not do anything if
there are no parentheses in the source and it doesn't need parentheses added.

```py
>>> g = f.right.copy(pars=True)

>>> print(g.src)
(x + y)

>>> g = f.left.copy(pars=True)

>>> print(g.src)
a
```

Named expressions copied out of other expressions which may or may not have parentheses do not normally have those
parentheses copied or added. Keep this in mind as an unparenthesized named expression is not normally parsable
standalone by Python.

```py
>>> f = FST('a, b := c, d')

>>> g = f.elts[1].copy()

>>> print(g.src)
b := c

>>> f = FST('a = (b := c)')

>>> g = f.value.copy()

>>> print(g.src)
b := c
```

This can be changed with the `pars_walrus` option (which also needs `pars` to not be `False`).

```py
>>> f = FST('a, b := c, d')

>>> g = f.elts[1].copy(pars_walrus=True)

>>> print(g.src)
(b := c)
```

## `pars` modes

The `pars` option has been mentioned above with two possible values, `True` and `False`, but its default value of
`'auto'` is somewhere in between these two and attempts to get and put parentheses where a human might do so.

```py
>>> [FST('a * (x + y)').right.copy(pars=p).root.src
...  for p in (True, False, 'auto')]
['(x + y)', 'x + y', 'x + y']

>>> [FST('a * b').right.replace('x + y', pars=p).root.src
...  for p in (True, False, 'auto')]
['a * (x + y)', 'a * x + y', 'a * (x + y)']

>>> [FST('x + y').right.replace('(a * b)', pars=p).root.src
...  for p in (True, False, 'auto')]
['x + (a * b)', 'x + (a * b)', 'x + a * b']

>>> [FST('a * b').right.replace('(x + y)', pars=p).root.src
...  for p in (True, False, 'auto')]
['a * (x + y)', 'a * (x + y)', 'a * (x + y)']
```

Notice in the examples above that the `pars=False` mode did not remove parentheses from the source before putting to
the target. This is because `pars=False` does not mean NO PARENTHESES, it means DON'T MODIFY PARENTHESES. The
`pars='auto'` mode remove parentheses from the source if they are not needed at the target while the `pars=True` mode
also leaves them in the source (but removes them from the target which `pars=False` does not do). For more information
on pars behavior, see the information on `pars` in `fst.fst.FST.get_options()`.

## Checking parentheses on a node

You can get the location and number of GROUPING parentheses on a node via the `pars()` method. Grouping parentheses are
those which fall into one of the first two categories at the top of this document. They do not include the parentheses
which are intrinsic to a node and already included in its location (like tuple parentheses), or parentheses which belong
to a parent node, either as part of the node or as grouping parentheses around that node.

The location which is returned form the `pars()` method also includes an attribute `n` which indicates the number of
enclosing parentheses found. One note of caution here, this is only valid for nodes which have location (almost all of
them). If you attempt to get `pars()` for a node which does not have a location, like `boolop`, `expr_context` or empty
`arguments`, you will get `None` back and `None` doesn't have an attribute `n` to tell you there are zero parentheses so
make sure to take this into accound where the node you are querying may not have a location.

```py
>>> (f := FST('(a + b)')).loc, f.pars()
(fstloc(0, 1, 0, 6), fstlocns(0, 0, 0, 7, n=1))

>>> (f := FST('((a + b))')).loc, f.pars()
(fstloc(0, 2, 0, 7), fstlocns(0, 0, 0, 9, n=2))

>>> (f := FST('(  ((a + b))  )')).loc, f.pars()
(fstloc(0, 5, 0, 10), fstlocns(0, 0, 0, 15, n=3))
```

If the node does not have parentheses then the node locations will be returned with `n=0`.

```py
>>> (f := FST('a + b')).loc, f.pars()
(fstloc(0, 0, 0, 5), fstlocns(0, 0, 0, 5, n=0))
```

`pars()` will not return parentheses intrinsic to a node.

```py
>>> (f := FST('(a, b)')).loc, f.pars()
(fstloc(0, 0, 0, 6), fstlocns(0, 0, 0, 6, n=0))
```

But it will return parentheses around that.

```py
>>> (f := FST('((a, b))')).loc, f.pars()
(fstloc(0, 1, 0, 7), fstlocns(0, 0, 0, 8, n=1))
```

There is a special case with a single call argument which is a generator expression, this can share its parentheses with
the call. You can explicitly exclude these shared parentheses from consideration via the `shared=False` parameter. In
this case if shared parentheses are detected, the returned `n` will be `-1`, and the location will not include the
parentheses (making the source invalid for a generator expression).

```py
>>> (f := FST('call(i for i in j)').args[0]).loc, f.pars()
(fstloc(0, 4, 0, 18), fstlocns(0, 4, 0, 18, n=0))

>>> (f := FST('call(i for i in j)').args[0]).loc, f.pars(shared=False)
(fstloc(0, 4, 0, 18), fstlocns(0, 5, 0, 17, n=-1))

>>> print(f.get_src(*f.pars(shared=False)))
i for i in j

>>> (f := FST('call((i for i in j))').args[0]).loc, f.pars(shared=False)
(fstloc(0, 5, 0, 19), fstlocns(0, 5, 0, 19, n=0))

>>> (f := FST('call(((i for i in j)))').args[0]).loc, f.pars(shared=False)
(fstloc(0, 6, 0, 20), fstlocns(0, 5, 0, 21, n=1))
```

`pars()` will also not return parentheses which technically enclose a single node but belong to the parent.

```py
>>> FST('call(a)').args[0].pars()
fstlocns(0, 5, 0, 6, n=0)

>>> FST('class cls(base): pass').bases[0].pars()
fstlocns(0, 10, 0, 14, n=0)

>>> FST('from a import (b)').names[0].pars()
fstlocns(0, 15, 0, 16, n=0)

>>> FST('with (a): pass').items[0].pars()
fstlocns(0, 5, 0, 8, n=0)
```

## Adding parentheses manually

Parentheses are normally handled automatically but you if want to add or remove them yourself there are two functions to
do that, `par()` for adding and `unpar()` for removing. Keep in mind that any parentheses you add or remove might be
automatically removed or added when you put the node unless you specify `pars=False` on use.

```py
>>> print(FST('a + b').par().src)
(a + b)

>>> print(FST('(a + b)').unpar().src)
a + b
```

`par()` can also be used to add intrinsic parentheses to nodes like `Tuple` or `MatchSequence` which do not have their
normal delimiters. Parentheses added in this way will not show up in `pars()` as they become a part of the node itself.

```py
>>> f = FST('a, b')

>>> f.par().src
'(a, b)'

>>> f.loc, f.pars()
(fstloc(0, 0, 0, 6), fstlocns(0, 0, 0, 6, n=0))

>>> f = FST('case a, b: pass')

>>> f.pattern.par().src
'[a, b]'

>>> print(f.src)
case [a, b]: pass

>>> f.pattern.loc, f.pattern.pars()
(fstloc(0, 5, 0, 11), fstlocns(0, 5, 0, 11, n=0))
```

`par()` and `unpar()` work on any node, not just root.

```py
>>> print(FST('i = a + b').value.par().root.src)
i = (a + b)
```

`par()` will not add parentheses to an atomic node normally (a node which is at the highest level of precedence or
always enclosed), or a node which already has grouping parentheses, but it can be forced.

```py
>>> print(FST('name').par().src)
name

>>> print(FST('name').par(force=True).src)
(name)

>>> print(FST('[a, b]').par().src)
[a, b]

>>> print(FST('[a, b]').par(force=True).src)
([a, b])

>>> print(FST('(a)').par().src)
(a)

>>> print(FST('(a)').par(force=True).src)
((a))
```

`par()` will add parentheses to a node which is atomic in terms of precedence but is not parsable because it is spread
over multiple lines without line continuations.

```py
>>> print(FST('a.b').par().src)
a.b

>>> print(FST(r'''
... a \
... . \
... b
... '''.strip()).par().src)
a \
. \
b

>>> print(FST('''
... a
... .
... b
... '''.strip()).par().src)
(a
.
b)
```

Even a `Constant` is not safe from this, consider an implicit string normally enclosed by a parent.

```py
>>> f = FST('''
... s = ('oh'
... 'no')
... '''.strip())

>>> g = f.value.copy(pars=False)

>>> print(g)
<Constant ROOT 0,0..1,4>

>>> print(g.src)  # this is a single string, but not parsable like this
'oh'
'no'

>>> print(g.par().src)
('oh'
'no')
```

`Starred` expressions are a special case as a `Starred` expression cannot be parenthesized syntactically speaking. If
you attempt to parenthesize or unparenthesize a `Starred` expression the operation happens on its child.

```py
>>> print(FST('*starred').par(force=True).src)
*(starred)

>>> print(FST('*(starred)').unpar().src)
*starred
```

## Removing parentheses manually

The inverse function of `par()` is `unpar()`, which unparenthesizes things. It removes all levels of grouping
parentheses at once.

```py
>>> print(FST('(a + b)').unpar().src)
a + b

>>> print(FST('(((a + b)))').unpar().src)
a + b

>>> print(FST('((x, y))').unpar().src)
(x, y)

>>> print(FST('((((x, y))))').unpar().src)
(x, y)
```

`unpar()` will not remove intrinsic parentheses normally.

```py
>>> print(FST('(x, y)').unpar().src)
(x, y)

>>> print(FST('(((x, y)))').unpar().src)
(x, y)

>>> print(FST('case [a, b]: pass').pattern.unpar().root.src)
case [a, b]: pass

>>> print(FST('case (([a, b])): pass').pattern.unpar().root.src)
case [a, b]: pass

>>> print(FST('case (((a, b))): pass').pattern.unpar().root.src)
case (a, b): pass
```

But can be forced.

```py
>>> print(FST('(x, y)').unpar(node=True).src)
x, y

>>> print(FST('(((x, y)))').unpar(node=True).src)
x, y

>>> print(FST('case [a, b]: pass').pattern.unpar(node=True).root.src)
case a, b: pass

>>> print(FST('case (([a, b])): pass').pattern.unpar(node=True).root.src)
case a, b: pass

>>> print(FST('case (((a, b))): pass').pattern.unpar(node=True).root.src)
case a, b: pass
```

`unpar()` will not remove parentheses which belong to a parent at all.

```py
>>> print(FST('call(a)').args[0].unpar().root.src)
call(a)

>>> print(FST('class cls(base): pass').bases[0].unpar().root.src)
class cls(base): pass

>>> print(FST('with (a): pass').items[0].unpar().root.src)
with (a): pass

>>> print(FST('with (((a))): pass').items[0].unpar().root.src)
with (((a))): pass
```

Sometimes this behavior can seem unintuitive like the last example above. In that case, `withitem` nodes are not
parenthesizable in the syntax so that all those grouping parentheses belong to the parent `with` if attempting to
unparenthesize a `withitem`. HOWEVER, you can remove the parentheses from the `with (a)` example above if you
unparenthesize the element INSIDE the `withitem`.

```py
>>> print(FST('with (a): pass').items[0].context_expr.unpar().root.src)
with a: pass

>>> print(FST('with (((a))): pass').items[0].context_expr.unpar().root.src)
with a: pass
```

This is not an issue as in this case there is a single element and it won't break anything. This will not work if there
is an optional variable in the `withitem`.

```py
>>> print(FST('with (a as b): pass').items[0].context_expr.unpar().root.src)
with (a as b): pass
```
"""
