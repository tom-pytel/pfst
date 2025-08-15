r"""
# Raw reparse operations

To be able to execute the examples, import this.
```py
>>> from fst import *
```

**Note:** `fst` is eventually intended to run with the global option `raw` set to `'auto'`, but as the prescribed slice
operations are not all implemented yet it is currently set as `False`. This is because `'auto'` can lead to some raw put
attempts which can result in some confusing error messages. If you are fine with some weird syntax exceptions then do
`FST.set_options(raw='auto')` and you should get slice puts succeeding where otherwise they wouldn't.

## Basics

Raw put operations are different from the standard prescribed operations in that for the most part they do not take into
account rules like precedence and indentation for the nodes being put and replaced and just try to put the source at the
location and reparse. They exist because they allow things which are not covered or otherwise impossible with normal
node operations.

Raw mode puts can be executed on individual nodes or slices by specifying the option `raw=True`. `raw='auto'` can be
used so that the prescribed operation with rules is tried first and if that fails a raw put is attempted as a fallback.
Raw mode automatic fallback is turned off globally by default as the error messages can be confusing, but if you want
this turned on for all operations without having to specify anything then do `FST.set_options(raw='auto')`.

```py
>>> f = FST('{a: b, c: d, e: f}')

>>> try:
...     f.put('**g', 1, raw=False)
... except Exception as exc:
...     print(str(exc))
...
cannot put as 'one' item to a Dict slice

>>> f.put('**g', 1, raw=True)
<Dict ROOT 0,0..0,17>

>>> print(f.src)
{a: b, **g, e: f}
```

Unlike a prescibed single node replacement, a single node raw replacement many affect other nodes around it and
completely change their meaning and structure (invalidating any `FST` references you had to the previous nodes).

```py
>>> f = FST('i + 1')

>>> f.dump()
BinOp - ROOT 0,0..0,5
  .left Name 'i' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Constant 1 - 0,4..0,5

>>> f.op.replace('=', raw=True)

>>> print(f.src)
i = 1

>>> f.dump()
Assign - ROOT 0,0..0,5
  .targets[1]
  0] Name 'i' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
```

Raw mode node operations are available for slices as well, in which case whatever source you pass is just put at the
location spanned by the first and last elements.

```py
>>> f = FST('[1, 2, 3, 4, 5]')

>>> f.put_slice('''
... 6, # blah
...    7,8
... '''.strip(), 1, 3, raw=True)
<List ROOT 0,0..1,13>

>>> print(f.src)
[1, 6, # blah
   7,8, 4, 5]
```

And just like for individual nodes, this can completely change the structure.

```py
>>> f.put_slice('], sub[0', 2, 3, raw=True)
<Tuple ROOT 0,0..1,20>

>>> print(f.src)
[1, 6, # blah
   ], sub[0,8, 4, 5]
```

## Source and automatic modifications

You can pass `AST` and `FST` nodes to raw mode operations, in which case the `AST` is unparsed and the `FST` just has
its own source code used for the put. There may be some modifications when these are passed, like for example an `FST`
passed as a slice source to a raw mode slice put operation may have its delimiters removed for the put (since we have
the `FST` type information).

```
>>> f = FST('[1, 2, 3]')

>>> f.put_slice(FST('{x, y}'), 2, None, raw=True)
<List ROOT 0,0..0,12>

>>> print(f.src)
[1, 2, x, y]
```

The other kind of modification that can happen in node raw operations are prefixes and suffixes being added, just like
for prescribed node operations as otherwise using raw might be more annoying.

```py
>>> f = FST('def f(): pass')

>>> f.put('int', 'returns', raw=True)
<FunctionDef ROOT 0,0..0,20>

>>> print(f.src)  # notice the ' -> ' added automatically
def f() -> int: pass
```

## `to` parameter

A single element raw node operation can take an optional `to` parameter to specify what node is the end of a source code
replacement. This is different from a slice operation in that the `to` can be any node, not just a node in the same
slice container, as long as it follows syntactically in the source.

```py
>>> f = FST('''
... if f(a=1):
...     g(b)
... '''.strip())

>>> f.test.keywords[0].value.replace('''
... 3, **z):
...     h(x, y
... '''.strip(), to=f.body[0].value.args[0], raw=True)
<Constant 0,7..0,8>

>>> print(f.src)
if f(a=3, **z):
    h(x, y)
```

This only works for single element `replace()` and `put()` operations. It does not apply to slice operations as that
could get confusing with those operations also specifying an explicit end location.

```py
>>> f = FST('[1, 2, 3]')

>>> try:
...     f.put_slice('4, 5', 0, 1, raw=True, to=f.elts[2])
... except Exception as exc:
...     print(exc)
cannot put slice with 'to' option
```

## Parentheses

As stated, raw mode node operations do not take into account precedence or parenthesization and do not add any
parentheses, but they do remove them from targets.

```py
>>> f = FST('[(a), (b), (c)]')

>>> f.elts[0].replace('x', raw=True)
<Name 0,1..0,2>

>>> print(f.src)
[x, (b), (c)]
```

You can turn this behavior off for single element operations.

```py
>>> f.elts[1].replace('y', raw=True, pars=False)
<Name 0,5..0,6>

>>> print(f.src)
[x, (y), (c)]
```

But it can cause problems.

```py
>>> try:
...     f.elts[0].replace('z', raw=True, pars=False, to=f.elts[2])
... except Exception as exc:
...     print(str(exc))
invalid syntax

>>> # this failed because the source code winds up being `[z, )]`

>>> f.elts[0].replace('z', raw=True, to=f.elts[2])
<Name 0,1..0,2>

>>> print(f.src)
[z]
```

Parentheses are always removed for raw slice operations because otherwise it gets too messy.

```py
>>> f = FST('[(a), (b), (c)]')

>>> f.put_slice('x, y', 0, 2, raw=True, pars=False)
<List ROOT 0,0..0,11>

>>> print(f.src)
[x, y, (c)]
```

If you want to avoid all automatic behavior on raw puts, then use `fst.fst.FST.put_src()` directly.
"""
