r"""
# Raw reparse operations

To be able to execute the examples, import this.

>>> from fst import *

## Basics

Raw put operations to nodes are different from the standard prescribed operations in that for the most part they do not
take into account rules like precedence and indentation for the nodes being put and replaced and just try to put the
source at the location and reparse. They exist because they allow things which are not covered or otherwise impossible
with normal node operations.

Raw mode puts can be executed on individual nodes or slices by specifying the option `raw=True`. `raw='auto'` can be
used so that the prescribed operation with rules is tried first and if that fails a raw put is attempted as a fallback.
Raw mode automatic fallback is turned off globally by default as the error messages can be confusing, but if you want
this turned on for all operations without having to specify anything then do `FST.set_options(raw='auto')`.

Raw put operations like this, whether explicit via `raw=True` or as a fallback via `raw='auto'` cannot insert or delete
nodes, they can only change existing nodes. Existing parentheses in the target may be removed depending on the `pars`
option.

Raw node put operations can do things which are not normally possible with prescribed operations.

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

Unlike a prescibed single node replacement, a single node raw replacement many affect other nodes around it and
completely change their meaning and structure (invalidating any `FST` references you had to the previous nodes).

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

Raw mode node operations are available for slices as well, in which case whatever source you pass is just put at the
location spanned by the first and last elements.

>>> f = FST('[1, 2, 3, 4, 5]')

>>> f.put_slice('''
... 6, # blah
...    7,8
... '''.strip(), 1, 3, raw=True)
<List ROOT 0,0..1,13>

>>> print(f.src)
[1, 6, # blah
   7,8, 4, 5]

And just like for individual nodes, this can completely change the structure.

>>> f.put_slice('], sub[0', 2, 3, raw=True)
<Tuple ROOT 0,0..1,20>

>>> print(f.src)
[1, 6, # blah
   ], sub[0,8, 4, 5]

## Locations

Raw node operations use the location of the node (including grouping parentheses if `pars` is not `False`). There are
two special-case locations which are automatically provided which are not normally available for a node. For a `Dict` or
`MatchMapping` the location of a nonexistent key replaced with `**` is provided if operating on the `keys` field.

>>> f = FST('{a: b, **c, d: e}')

>>> f.put('z: ', 1, 'keys', raw=True)  # note the explicit trailing ': ' after the 'z'
<Dict ROOT 0,0..0,18>

>>> print(f.src)
{a: b, z: c, d: e}

You cannot undo this with a raw put as the location of the key ends before the `:` and so that will not be overwritten
if putting just to `keys`. If you wish to change a `a: b` key-value pair in a `Dict` or `MatchMapping` to a `**b` using
raw operations then you must operate on the virtual `_all` field (which is selected by the default field value of
`None`).

>>> f.put('**c', 1, raw=True)  # note we don't specify 'keys' field
<Dict ROOT 0,0..0,17>

>>> print(f.src)
{a: b, **c, d: e}

Also the location of empty `arguments` for a `FunctionDef` or a `Lambda` are provided at the expected location of those
`arguments` even though empty `arguments` don't normally have a `.loc`.

## Source and automatic modifications

The only single-element put special case modification which may be applied is if putting to empty `arguments` of a
`Lambda` function. The location of these in a standard empty `Lambda` is normally right after the `lambda` keyword since
the `:` normally follows right after. In order to stay consistent with puts to empty `FunctionDef` arguments always
working, in this case if the source being put does not start with a space (in any form, `AST`, `FST` or source string)
then a single space will be prepended.

>>> f = FST('lambda: None')

>>> f.put('a', 'args', raw=True)  # no leading space before the 'a'
<Lambda ROOT 0,0..0,14>

>>> print(f.src)  # one was automatically inserted
lambda a: None

Other than this, if you pass `AST` or `FST` nodes to raw mode slice operations, the `AST` is unparsed and the `FST`
just has its own source code used for the put. One of the only two modifications which may happen to this unparsed `AST`
or existing `FST` source is that if a sequence with delimiters is passed to a slice put then the delimiters are stripped
for `Tuple`, `List`, `Set`, `Dict`, `MatchSequence` and `MatchMapping`, otherwise the source is used as-is for the put.

>>> f = FST('[1, 2, 3]')

>>> f.put_slice(FST('{x, y}'), 2, None, raw=True)
<List ROOT 0,0..0,12>

>>> print(f.src)
[1, 2, x, y]

The other modification that can happen is that locations are selected for the put in order that commas are not
duplicated and that a resulting singleton `Tuple` or `MatchSequence` always has a trailing comma. If this is not
possible by selecting copy locations then a comma is inserted where needed.

>>> f = FST('(a, b)')

>>> f.put_slice(FST('[x]'), 0, 2, raw=True)
<Tuple ROOT 0,0..0,4>

>>> print(f.src)
(x,)

These modifications do not apply if putting source as a string directly.

>>> f = FST('(a, b)')

>>> f.put_slice('[x]', 0, 2, raw=True)
<List ROOT 0,1..0,4>

>>> print(f.src)
([x])

## `to` parameter

A single element raw node operation can take an optional `to` parameter to specify what node is the end of a source code
replacement. This is different from a slice operation in that the `to` can be any node, not just a node in the same
slice container, as long as it follows syntactically in the source.

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

This only works for single element `replace()` and `put()` operations. It does not apply to slice operations as that
could get confusing with those operations also specifying an explicit end location.

>>> f = FST('[1, 2, 3]')

>>> try:
...     f.put_slice('4, 5', 0, 1, raw=True, to=f.elts[2])
... except Exception as exc:
...     print(exc)
cannot put slice with 'to' option

## Parentheses

Raw mode node operations do not take into account precedence or parenthesization and do not add any parentheses, but
they do remove them from targets.

>>> f = FST('[(a), (b), (c)]')

>>> f.elts[0].replace('x', raw=True)
<Name 0,1..0,2>

>>> print(f.src)
[x, (b), (c)]

You can turn this behavior off for single element operations.

>>> f.elts[1].replace('y', raw=True, pars=False)
<Name 0,5..0,6>

>>> print(f.src)
[x, (y), (c)]

But it can cause problems.

>>> try:
...     f.elts[0].replace('z', raw=True, pars=False, to=f.elts[2])
... except Exception as exc:
...     print(str(exc))
invalid syntax

This failed because the source code winds up being `[z, )]`.

>>> f.elts[0].replace('z', raw=True, to=f.elts[2])
<Name 0,1..0,2>

>>> print(f.src)
[z]

Parentheses are always removed for raw slice operations because otherwise it gets too messy.

>>> f = FST('[(a), (b), (c)]')

>>> f.put_slice('x, y', 0, 2, raw=True, pars=False)
<List ROOT 0,0..0,11>

>>> print(f.src)
[x, y, (c)]

If you want to avoid all automatic behavior on raw puts, then use `fst.fst.FST.put_src()` directly.
"""
