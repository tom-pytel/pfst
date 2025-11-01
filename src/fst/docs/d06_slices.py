r"""
# Slices and trivia

To be able to execute the examples, import this.
```py
>>> from fst import *
```

## Slices

`AST` nodes may have individual `AST` children like `FunctionDef.returns` or lists of `AST` children like
`FunctionDef.body`. Any single node or a single element of a list of children can be gotten individually as one node,
but getting a sequence of nodes from a list of children requires a slice operation via `get_slice()` or `put_slice()`
(or the equivalent attribute accesses).

In many cases a slice of a list of children of a node can be returned as the same type of node. For example a slice of a
`Tuple` is a `Tuple`.

```py
>>> node = FST('(1, 2, 3, 4)')

>>> print(node)
<Tuple ROOT 0,0..0,12>

>>> slice = node.get_slice(1, 3)

>>> print(slice)
<Tuple ROOT 0,0..0,6>

>>> print(slice.src)
(2, 3)
```

This same type is used to put back to the node.

```py
>>> node.put_slice(slice, 3, 3)
<Tuple ROOT 0,0..0,18>

>>> print(node.src)
(1, 2, 3, 2, 3, 4)
```

For the three types of sequences, `Tuple`, `List` and `Set`, they will all accept any of the other sequences for a slice
put.

```py
>>> print(FST('[1, 2, 3]').put_slice('(4, 5)', 1, 2).src)
[1, 4, 5, 3]

>>> print(FST('{1, 2, 3}').put_slice('[4, 5]', 1, 2).src)
{1, 4, 5, 3}

>>> print(FST('(1, 2, 3)').put_slice('{4, 5}', 1, 2).src)
(1, 4, 5, 3)
```

But return their own type on a get.

```py
>>> FST('[1, 2, 3, 4]').get_slice(1, 3)
<List ROOT 0,0..0,6>

>>> FST('{1, 2, 3, 4}').get_slice(1, 3)
<Set ROOT 0,0..0,6>
```

Some other types of nodes may return and accept slices as `Tuple`. Generally these are nodes which have expression
children separated by commas in a syntax similar to tuples, e.g. `Delete.targets` or `Global.names`.

```py
>>> slice = FST('del a, b, c').get_slice()

>>> print(slice)
<Tuple ROOT 0,0..0,7>

>>> print(slice.src)
a, b, c
```

```py
>>> slice = FST('global a, b, c').get_slice()

>>> print(slice)
<Tuple ROOT 0,0..0,7>

>>> print(slice.src)
a, b, c
```

These will also generally accept any of the three sequence types for a slice put.

```py
>>> parent = FST('del a, b, c')

>>> parent.put_slice('[x, y]', 1, 2)
<Delete ROOT 0,0..0,14>

>>> print(parent.src)
del a, x, y, c
```

```py
>>> parent = FST('nonlocal a, b, c')

>>> parent.put_slice('{x, y}', 1, 2)
<Nonlocal ROOT 0,0..0,19>

>>> print(parent.src)
nonlocal a, x, y, c
```

If a type does not have comma separators but can be represented by a standard `AST` for its slice, that type is used.

```py
>>> slice = FST('case a | b | c | d: pass').pattern.get_slice(1, 3)

>>> print(slice)
<MatchOr ROOT 0,0..0,5>

>>> print(slice.src)
b | c
```

## Non-standard `AST` slices

Nodes which have list children which do not match tuple comma-separated syntax or `expr` child type may be returned in
custom `AST` node container. These custom types are meant to allow slice operations while preserving source format
(since we will not be adding or removing commas or other separators in order to preserve format). For example:

```py
>>> slice = FST('a = b = c = d = e').get_slice(1, 3, 'targets')

>>> print(slice)
<_Assign_targets ROOT 0,0..0,7>

>>> print(slice.src)
b = c =
```

Or for example the `Import` and `ImportFrom` `names` field. It is a comma separated list of what look like expressions
but they are actually aliases which may have an `asname`, which is not allowed in standard `Tuples`, so they are
returned in their own slice type.

```py
>>> slice = FST('import a, b as c, d').get_slice()

>>> print(slice)
<_aliases ROOT 0,0..0,12>

>>> print(slice.src)
a, b as c, d
```

These special slices can be put to and gotten from just like any other node.

```py
>>> slice = FST('import a, b as c, d').get_slice()

>>> slice.put_slice('u as v, x as y', -1)
<_aliases ROOT 0,0..0,25>

>>> print(slice)
<_aliases ROOT 0,0..0,25>

>>> print(slice.src)
a, b as c, u as v, x as y

>>> print(slice.get_slice(1, 3).src)
b as c, u as v
```

## Normalization of `Set`

For some types of `AST` nodes it is permissible to remove all children and still remain valid, for example `Tuple` or
`List`.

```py
>>> print(FST('a, b, c').put_slice(None, 0, 3).src)  # delete
()

>>> node = FST('[a, b, c]')

>>> node.get_slice(0, 3, cut=True)  # cut
<List ROOT 0,0..0,9>

>>> print(node.src)
[]
```

Note how for the unparenthesized `Tuple` parentheses were added for the empty `Tuple` to be valid. In general if
something is needed on a slice operation (or single operation for that matter) in order to result in a valid `AST` then
it is done. This can include adding delimiters, grouping parentheses, line continuations, etc...

In extreme cases, like deleting all elements from a `Set`, an element may be added to the `Set` node as a child to
maintain its parsability and validity as a `AST`.

```py
>>> node = FST('{a, b, c}')

>>> node.put_slice(None, 0, 3)
<Set ROOT 0,0..0,5>

>>> print(node.src)
{*()}
```

Likewise getting an empty slice from a `Set` will also give you a "normalized" slice.

```py
>>> print(FST('[a, b, c]').get_slice(0, 0).src)  # empty slice form a list
[]

>>> print(FST('{a, b, c}').get_slice(0, 0).src)  # empty slice from a set
{*()}
```

This may not be desirable and you may wish to use an actual empty `Set` for a bit. You can do this by passing the option
`norm=False`.

```py
>>> slice = FST('{a, b, c}').get_slice(0, 0, norm=False)

>>> print(slice)
<Set ROOT 0,0..0,2>

>>> print(slice.src)
{}
```

Note that a `Set` was returned but with zero children. This is not a valid `AST` node and if you attempt to reparse this
it will parse as an empty `Dict`. For this reason normalization should be used for intermediate objects which you may
want to operate on without having to deal with special rules and not for source code you are writing out.

The standard `norm` option applies to three cases of normalization. The normalization of the target object (what you are
putting to or cutting from), the returned object and a possible object which may be being put. The `norm` option sets
all of these to the same value, but you can set them individually as `norm_self`, `norm_get` or `norm_put`.

In general, invalid `AST` slices like the above empty `Set` are accepted and processed correctly as sources to a slice
put, but there may be cases where you need to specify whether the special rules should apply or not. For example when
putting an "empty" `Set` of the form `{*()}`, it will be treated as empty with normalization on.

```py
>>> print(FST('[a, b, c]').put_slice('{*()}', 1, 1).src)
[a, b, c]
```

If you want it to be treated literally and not interpreted as an empty `Set` then pass either `norm=False` or
`norm_put=False`.

```py
>>> print(FST('[a, b, c]').put_slice('{*()}', 1, 1, norm_put=False).src)
[a, *(), b, c]
```

To finish off the `Set` normalization, there is an option `set_norm` which may be `True`, `False`, `'star'`, `'call'` or
`'both'`. This specifies what should be used for `Set` normalization with the options allowing empty starred immediate
objects or the `set()` function call (which you may not use if it is shadowed in the code being worked on).

## Normalization of other nodes

Normalization doesn't just apply to `Set` though. For most other types of `AST` nodes it will decide whether it is
allowed to delete all the children of that node even if it is not valid to do so. For example:

```py
>>> node = FST('a = b = val')

>>> try:
...     node.put_slice(None, 'targets')  # try to delete everything
... except Exception as exc:
...     print(exc)
cannot delete all Assign.targets without norm_self=False

>>> node.put_slice(None, 'targets', norm=False)
<Assign ROOT 0,0..0,4>

>>> print(node.src)
 val
```

Note that `node` wound up as an invalid `Assign` with the source being literally `' val'`. This is not valid as it is
but can be put to normally.

```py
>>> node.put_slice('x = y =', 'targets')
<Assign ROOT 0,0..0,11>

>>> print(node.src)
x = y = val
```

## Put as `one=True`

When putting a slice the node being put is normally considered to be a slice of the type needed to put to the target
and the elements specified from `start` to `stop` will be replaced with the elements of the slice. For example:

```py
>>> print(FST('[a, b, c]').put_slice('[x, y]', 1, 2).src)
[a, x, y, c]
```

In this case the elements `x, y` replaced the element `b` in the target. If instead of replacing with the elements of the
node being put you wish to just put the node itself then specify `one=True`.

```py
>>> print(FST('[a, b, c]').put_slice('[x, y]', 1, 2, one=True).src)
[a, [x, y], c]
```

The same thing could have been accomplished just by putting the node with a normal `put()` to the second element of the
target. The reason the `one` option exists is when you want to replace or delete multiple elements with a single "one".

```py
>>> print(FST('[a, b, c]').put_slice('[x, y]', 1, 3, one=True).src)
[a, [x, y]]
```

```py
>>> print(FST('[a, b, c]').put_slice(None, 0, 2, one=True).src)
[c]
```

This is allowed anywhere where the single element being put would be allowed to replace multiple elements. For example:

```py
>>> print(FST('del a, b, c, d').put_slice('x, y', 1, 3, one=True).src)
del a, (x, y), d

>>> print(FST('case a | b | c | d: pass').pattern.put_slice('x as y', 1, 3, one=True).src)
a | (x as y) | d
```

## Trivia

"Trivia" refers to the parts of the source code which don't actually code for anything like comments and whitespace. The
whole point of the `fst` module is to preserve this stuff while editing some parts of the code. Trivia can be gotten and
put in all slice operations and single element operations on statement-ish nodes but not single operations on
expression-ish elements (for now).

Note: Statement-ish refers to statement nodes, `match_case`, `ExceptHandler` and their special slice containers and
`mod` nodes. Expression-ish is everything else.

When getting a slice or statement-ish node you can specify comments and empty lines to copy and / or cut as well as
specifying those to be overwritten on a slice or statement-ish put. The option to specify this is `trivia` and it can
specify just the leading trivia or both the leading and trailing.

Leading trivia can specify a leading comment block, all leading comments and a maximum number of empty lines before that
to copy or cut or delete.

```py
>>> pp = lambda f: print('\n'.join(repr(l) for l in f.lines))  # helper

>>> parent = FST('''
... pre_stmt
...
... # pre-comment 1a
... # pre-comment 1b
...
...
... # pre-comment 2a
... # pre-comment 2b
... target_stmt
... '''.strip())
```

`trivia=False` will just give you the individual element.

```py
>>> pp(parent.get(1, trivia=False))
'target_stmt'
```

`trivia=True` and `trivia='block'` are the same for leading trivia and will give you the immediately preceding block of
comments.

```py
>>> pp(parent.get(1, trivia=True))
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'

>>> pp(parent.get(1, trivia='block'))  # 'block' same as True for leading comments
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'
```

`trivia='all'` will give you all preceding comments including empty lines between them (up till previous statement or
start of block statement or top of module).

```py
>>> pp(parent.get(1, trivia='all'))  # 'block' same as True for leading comments
'# pre-comment 1a'
'# pre-comment 1b'
''
''
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'
```

If the operation is a cut then these lines will be removed from the target.

```py
>>> node = parent.copy()

>>> node.get(1, cut=True, trivia='block')
<Expr ROOT 2,0..2,11>

>>> pp(node)
'pre_stmt'
''
'# pre-comment 1a'
'# pre-comment 1b'
''
''
```

Likewise on a put the trivia specifies what to overwrite.

```py
>>> node = parent.copy()

>>> node.put('put_stmt', 1, trivia='all')
<Module ROOT 0,0..2,8>

>>> pp(node)
'pre_stmt'
''
'put_stmt'
```

If you wish to include empty lines to overwrite then add them to the trivia option like so:

```py
>>> node = parent.copy()

>>> node.get(1, cut=True, trivia='block-')
<Expr ROOT 2,0..2,11>

>>> pp(node)
'pre_stmt'
''
'# pre-comment 1a'
'# pre-comment 1b'
```

Note the trailing `'-'` which means delete all empty lines. You can also specify a maximum number of empty lines to
delete.

```py
>>> node = parent.copy()

>>> node.get(1, cut=True, trivia='block-1')
<Expr ROOT 2,0..2,11>

>>> pp(node)
'pre_stmt'
''
'# pre-comment 1a'
'# pre-comment 1b'
''
```

```py
>>> node = parent.copy()

>>> node.get(1, cut=True, trivia='block-2')
<Expr ROOT 2,0..2,11>

>>> pp(node)
'pre_stmt'
''
'# pre-comment 1a'
'# pre-comment 1b'
```

When getting a node and specifying empty space with the minus `'-'` then the space is cut from the source on a cut but
not returned in the gotten node.

```py
>>> node = parent.copy()

>>> pp(node.get(1, cut=True, trivia='block-1'))
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'
```

If you want the space then use a plus `'+'` instead of the minus.

```py
>>> node = parent.copy()

>>> pp(node.get(1, cut=True, trivia='block+1'))
''
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'

>>> pp(node)
'pre_stmt'
''
'# pre-comment 1a'
'# pre-comment 1b'
''
```

The plus instead of the minus only means return the empty space that was cut. In all cases the space is removed from the
target.

All of this applies to all statement-ish operations but also expression-ish slice operations as well.

```py
>>> node = FST('''[
... pre_expr,
...
... # pre-comment 1a
... # pre-comment 1b
...
...
... # pre-comment 2a
... # pre-comment 2b
... target_expr,
... ]''')

>>> pp(node.get_slice(1, 2, cut=True, trivia='block+1'))
'['
''
'# pre-comment 2a'
'# pre-comment 2b'
'target_expr,'
']'

>>> pp(node)
'['
'pre_expr'
''
'# pre-comment 1a'
'# pre-comment 1b'
''
']'
```

The default leading trivia is `'block'`.

## Trivia (trailing)

This is similar to leading trivia but has an extra option `'line'` which specifies just the trailing comment on the same
line as the element or last element of the slice, not any other comments of a following block.

Trailing trivia can be specified by passing a full tuple for leading and trailing as the `trivia` option of the form
`trivia=(leading, trailing)`. You can pass `None` for the leading element in order to use the currenly set default which
is normally `'block'` for leading trivia.

```py
>>> pp = lambda f: print('\n'.join(repr(l) for l in f.lines))  # helper

>>> parent = FST('''
... target_stmt  # line-comment
... # post-comment 1a
... # post-comment 1b
...
...
... # post-comment 2a
... # post-comment 2b
...
... post_stmt
... '''.strip())
```

The default trailing trivia is `'line'`.

```py
>>> pp(parent.get(0))
'target_stmt  # line-comment'
```

You can turn that off.

```py
>>> pp(parent.get(0, trivia=(None, False)))
'target_stmt'
```

Trailing block comment.

```py
>>> pp(parent.get(0, trivia=(None, 'block')))
'target_stmt  # line-comment'
'# post-comment 1a'
'# post-comment 1b'
```

With space.

```py
>>> pp(parent.get(0, trivia=(None, 'block+1')))
'target_stmt  # line-comment'
'# post-comment 1a'
'# post-comment 1b'
''
```

All.

```py
>>> pp(parent.get(0, trivia=(None, 'all+')))
'target_stmt  # line-comment'
'# post-comment 1a'
'# post-comment 1b'
''
''
'# post-comment 2a'
'# post-comment 2b'
''
```

The same rules apply for what is copied and what is removed or overwritten with plus and minus. You can specify how to
handle both leading and trailing trivia as one parameter, for example `trivia=('block+2', 'all+')`.
"""