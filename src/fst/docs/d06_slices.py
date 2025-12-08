r"""
# Slices and trivia

To be able to execute the examples, import this.

>>> from fst import *

## Slices

`AST` nodes may have individual `AST` children like `FunctionDef.returns` or lists of `AST` children like
`FunctionDef.body`. Any single node or a single element of a list of children can be gotten individually as one node,
but getting a sequence of nodes from a list of children requires a slice operation via `get_slice()` or `put_slice()`
(or the equivalent attribute accesses). (`fst.fst.FST.get_slice()`, `fst.fst.FST.put_slice()`)

In many cases a slice of a list of children of a node can be returned as the same type of node. For example a slice of a
`Tuple` is a `Tuple`.

>>> node = FST('(1, 2, 3, 4)')

>>> print(node)
<Tuple ROOT 0,0..0,12>

>>> slc = node.get_slice(1, 3)

>>> print(slc)
<Tuple ROOT 0,0..0,6>

>>> print(slc.src)
(2, 3)

This same type is used to put back to the node.

>>> node.put_slice(slc, 3, 3)
<Tuple ROOT 0,0..0,18>

>>> print(node.src)
(1, 2, 3, 2, 3, 4)

For the three types of sequences, `Tuple`, `List` and `Set`, they will all accept any of the other sequences for a slice
put.

>>> print(FST('[1, 2, 3]').put_slice('(4, 5)', 1, 2).src)
[1, 4, 5, 3]

>>> print(FST('{1, 2, 3}').put_slice('[4, 5]', 1, 2).src)
{1, 4, 5, 3}

>>> print(FST('(1, 2, 3)').put_slice('{4, 5}', 1, 2).src)
(1, 4, 5, 3)

But return their own type on a get.

>>> FST('[1, 2, 3, 4]').get_slice(1, 3)
<List ROOT 0,0..0,6>

>>> FST('{1, 2, 3, 4}').get_slice(1, 3)
<Set ROOT 0,0..0,6>

Some other types of nodes may return and accept slices as `Tuple`. Generally these are nodes which have expression
children separated by commas in a syntax similar to tuples, e.g. `Delete.targets` or `Global.names`.

>>> slc = FST('del a, b, c').get_slice()

>>> print(slc)
<Tuple ROOT 0,0..0,7>

>>> print(slc.src)
a, b, c

Note that a `Global` node stores its names as primitive strings. The slice operations coerce these to and from `Name`
`AST` nodes.

>>> slc = FST('global a, b, c').get_slice()

>>> print(slc)
<Tuple ROOT 0,0..0,7>

>>> print(slc.src)
a, b, c

These will also generally accept any of the three sequence types for a slice put.

>>> parent = FST('del a, b, c')

>>> parent.put_slice('[x, y]', 1, 2)
<Delete ROOT 0,0..0,14>

>>> print(parent.src)
del a, x, y, c

>>> parent = FST('nonlocal a, b, c')

>>> parent.put_slice('{x, y}', 1, 2)
<Nonlocal ROOT 0,0..0,19>

>>> print(parent.src)
nonlocal a, x, y, c

If a type does not have comma separators but can be represented by a standard `AST` for its slice, that type is used.

>>> slc = FST('case a | b | c | d: pass').pattern.get_slice(1, 3)

>>> print(slc)
<MatchOr ROOT 0,0..0,5>

>>> print(slc.src)
b | c

## Non-standard `AST` slices

Nodes which have list children which do not match tuple comma-separated syntax or `expr` child type may be returned in
custom `AST` node container. These custom types are meant to allow slice operations while preserving source format
(since we will not be adding or removing commas or other separators in order to preserve format).

For example, `Assign.targets`:

>>> slc = FST('a = b = c = d = e').get_slice(1, 3, 'targets')

>>> print(slc)
<_Assign_targets ROOT 0,0..0,7>

>>> print(slc.src)
b = c =

`ListComp.generators` (and other comprehensions):

>>> slc = FST('[i for k in l for j in k for i in j]').get_slice('generators')

>>> print(slc)
<_comprehensions ROOT 0,0..0,32>

>>> print(slc.src)
for k in l for j in k for i in j

`comprehension.ifs`:

>>> slc = FST('[i for a, b, c in j if a if b if c]').generators[0].get_slice('ifs')

>>> print(slc)
<_comprehension_ifs ROOT 0,0..0,14>

>>> print(slc.src)
if a if b if c

`FunctionDef.decorator_list` (and other defs):

>>> slc = FST('''
... @deco_a
... @deco_b()
... @deco_c  # comment
... def f(): pass
... '''.strip()).get_slice('decorator_list')

>>> print(slc)
<_decorator_list ROOT 0,0..2,18>

>>> print(slc.src)
@deco_a
@deco_b()
@deco_c  # comment

The `Import` and `ImportFrom` `names` field is a comma separated list of what look like expressions but they are
actually aliases. They have an `asname`, which is not allowed in standard `Tuples`, so they are returned in their own
slice type `_aliases`.

>>> slc = FST('import a, b as c, d').get_slice()

>>> print(slc)
<_aliases ROOT 0,0..0,12>

>>> print(slc.src)
a, b as c, d

You can get and put to these non-standard slices just like normal nodes.

>>> slc = FST('import a, b as c, d').get_slice()

>>> slc.put_slice('u as v, x as y', -1)
<_aliases ROOT 0,0..0,25>

>>> print(slc)
<_aliases ROOT 0,0..0,25>

>>> print(slc.src)
a, b as c, u as v, x as y

>>> print(slc.get_slice(1, 3).src)
b as c, u as v

Or.

>>> slc = FST('[i for a, b, c in j if a if b if c]').generators[0].get_slice('ifs')

>>> slc.dump()
_comprehension_ifs - ROOT 0,0..0,14
  .ifs[3]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'b' Load - 0,8..0,9
   2] Name 'c' Load - 0,13..0,14

>>> slc.get_slice(1, 3).dump()
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[2]
   0] Name 'b' Load - 0,3..0,4
   1] Name 'c' Load - 0,8..0,9

>>> slc.put_slice('if x if y', 1, 2).dump()
_comprehension_ifs - ROOT 0,0..0,19
  .ifs[4]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'x' Load - 0,8..0,9
   2] Name 'y' Load - 0,13..0,14
   3] Name 'c' Load - 0,18..0,19

>>> print(slc.src)
if a if x if y if c

## BoolOp and Compare "slices"

You can also slice these node types as they contain lists of child nodes, though there are some extra parameters since
the children are separated by operators (same operator in the case of `BoolOp` and possibly different ones for
`Compare`). The "slices" in this case are just the same kind of node as is being sliced.

>>> f = FST('a and b and c and d')

>>> print(f.get_slice(1, 3).src)
b and c

>>> print(f.put_slice('x and y', 0, 3).src)
x and y and d

>>> f = FST('a < b == c > d')

>>> print(f.get_slice(1, 3).src)
b == c

>>> print(f.put_slice('x != y', 0, 3).src)
x != y > d

The first new parameter which applies to these two node types is `op_side` which determines what side of a slice any
extra operator is to be found when we need to delete or insert an extra. The possible values are `'left'` and `'right'`
which mean exactly that.

When deleting a slice from one of these nodes an extra operator will need to be deleted (otherwise you would wind up
with something like `a and and d`) and this option determines which side it is removed from.

This does actually matter for a `BoolOp` regardless of the fact that all the operators are the same because of
placement.

>>> print(FST('''
... a
... and  # left
... b
... and  # right
... c
... '''.strip()).put_slice(None, 1, 2, op_side='left').src)
a
and  # right
c

>>> print(FST('''
... a
... and  # left
... b
... and  # right
... c
... '''.strip()).put_slice(None, 1, 2, op_side='right').src)
a
and  # left
c

And in the case of a `Compare` it really matters as the operators can all be different.

>>> print(FST('a < b > c').put_slice(None, 1, 2, op_side='left').src)
a > c

>>> print(FST('a < b > c').put_slice(None, 1, 2, op_side='right').src)
a < c

The `op_side` option is a conisdered a hint and it may be overridden without error by the location of the slice being
deleted or inserted.

If inserting to a `Compare` an extra operator **MUST** be added and the operator must be specified either in the source
being put to the compare or as a separate `op` option.

>>> print(FST('a < b').put_slice('== x', 1, 1).src)
a == x < b

>>> print(FST('a < b').put_slice('x ==', 1, 1).src)
a < x == b

>>> print(FST('a < b').put_slice('x', 1, 1, op_side='left', op='==').src)
a == x < b

>>> print(FST('a < b').put_slice('x', 1, 1, op_side='right', op='==').src)
a < x == b

>>> try:  # no extra op in source or `op` option
...     print(FST('a < b').put_slice('x', 1, 1).src)
... except Exception as exc:
...     print(repr(exc))
ValueError("insertion to Compare requires and 'op' extra operator to insert")

If replacing then this is optional.

>>> print(FST('a < b > c').put_slice('x', 1, 2).src)
a < x > c

>>> print(FST('a < b > c').put_slice('== x', 1, 2).src)
a == x > c

>>> print(FST('a < b > c').put_slice('x ==', 1, 2).src)
a < x == c

>>> print(FST('a < b > c').put_slice('x', 1, 2, op_side='left', op='==').src)
a == x > c

>>> print(FST('a < b > c').put_slice('x', 1, 2, op_side='right', op='==').src)
a < x == c

## Normalization

For some types of `AST` nodes it is permissible to remove all children and still remain valid, for example `Tuple` or
`List`.

>>> print(FST('a, b, c').put_slice(None, 0, 3).src)  # delete
()

>>> node = FST('[a, b, c]')

>>> node.get_slice(0, 3, cut=True)  # cut
<List ROOT 0,0..0,9>

>>> print(node.src)
[]

Note how for the unparenthesized `Tuple` parentheses were added for the empty `Tuple` to be valid. However deleting all
field elements from a node does not always result in a valid `AST`. `fst` allows you to delete all the elements in these
cases for editing purposes and it is on you to ensure that something is put there before writing the code out for use.

You can delete all the statements from bodies (or `orelse` or `handlers` or `finalbody` or `Match.cases`).

>>> node = FST('''
... if 1:
...     pass
... '''.strip())

>>> del node.body[0]

>>> print(node.src)
if 1:

Or from individual statements which normally can't have empty child lists.

>>> node = FST('del a, b, c')

>>> node.put_slice(None, 0, 3)
<Delete ROOT 0,0..0,4>

>>> print(repr(node.src))
'del '

>>> node = FST('a = b = c = val')

>>> node.put_slice(None, 'targets')
<Assign ROOT 0,0..0,4>

>>> print(repr(node.src))
' val'

Doing this with a `Set` winds up with empty curlies which look like a `Dict` (but can still be used normally for editing
as a `Set`).

>>> node = FST('{a, b, c}')

>>> node.put_slice(None, 0, 3)
<Set ROOT 0,0..0,2>

>>> print(node.src)
{}

In all cases these result in invalid `AST` nodes but is allowed with the understanding that valid data will be replaced
eventually, preferably sooner rather than later as not all operations are valid on invalid `AST` nodes.

>>> node.put_slice('x, y')
<Set ROOT 0,0..0,6>

>>> print(node.src)
{x, y}

If you wish to avoid invalid `AST` nodes completely then you can pass the `norm=True` option. For most nodes this will
simply disallow operations which would leave an invalid node. However there are some `AST` types which have special
handling.

## Normalization of `Set`

In extreme cases, like deleting all elements from a `Set`, you can use the `norm=True` option to maintain its
parsability and validity as a `AST`.

>>> node = FST('{a, b, c}')

>>> node.put_slice(None, 0, 3, norm=True)
<Set ROOT 0,0..0,5>

>>> print(node.src)
{*()}

Likewise getting an empty slice from a `Set` will also give you a "normalized" slice.

>>> print(FST('[a, b, c]').get_slice(0, 0).src)  # empty slice form a list
[]

>>> print(FST('{a, b, c}').get_slice(0, 0, norm=True).src)  # empty slice from a set
{*()}

The standard `norm` option applies to three cases of normalization. The normalization of the target object (what you are
putting to or cutting from), the returned object and a possible object which may be being put. The `norm` option sets
all of these to the same value, but you can set them individually as `norm_self`, `norm_get` or `norm_put`.

In general, invalid `AST` slices like an empty `Set` from `norm=False` are accepted and processed correctly as sources
to a slice put. But for "normalized" slices there may be cases where you need to specify whether the special rules
should apply or not. When putting an "empty" `Set` of the form `{*()}`, it will be treated as empty with normalization
on.

>>> print(FST('[a, b, c]').put_slice('{*()}', 1, 1, norm=True).src)
[a, b, c]

If you want it to be treated literally and not interpreted as an empty `Set` then pass either `norm=False` or
`norm_put=False` (`norm=False` is the default if not passing `norm` at all).

>>> print(FST('[a, b, c]').put_slice('{*()}', 1, 1).src)
[a, *(), b, c]

To finish off the `Set` normalization, there is an option `set_norm` which may be `True`, `False`, `'star'`, `'call'` or
`'both'`. This specifies what should be used for `Set` normalization with the options allowing empty starred immediate
objects `*()`, `*[]`, `*{}` or the `set()` function call (which you may not use if it is shadowed in the code being
worked on).

## Normalization of other nodes

Normalization doesn't just apply to `Set` though. For most other types of `AST` nodes it will decide whether it is
allowed to delete all the children of that node even if it is not valid to do so. For example:

>>> node = FST('a = b = val')

>>> try:
...     node.put_slice(None, 'targets', norm=True)  # try to delete everything
... except Exception as exc:
...     print(exc)
cannot delete all Assign.targets without norm_self=False

>>> node.put_slice(None, 'targets', norm=False)
<Assign ROOT 0,0..0,4>

>>> print(repr(node.src))
' val'

Note that `node` wound up as an invalid `Assign` with the source being literally `' val'`. This is not valid as it is
but can be put to normally.

>>> node.put_slice('x = y =', 'targets')
<Assign ROOT 0,0..0,11>

>>> print(node.src)
x = y = val

For a `BoolOp` or `Compare` normalization will convert a single element "slice" to just the element that was left.

>>> FST('a or b').get_slice(0, 1).dump()  # invalid
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1

>>> FST('a or b').get_slice(0, 1, norm=True).dump()  # valid
Name 'a' Load - ROOT 0,0..0,1

>>> FST('a < b').get_slice(0, 1).dump()  # invalid
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1

>>> FST('a < b').get_slice(0, 1, norm=True).dump()  # valid
Name 'a' Load - ROOT 0,0..0,1


## Put as `one=True`

When putting a slice, the node being put is normally considered to be a slice of the type needed to put to the target
and the elements specified from `start` to `stop` will be replaced with the elements of the slice. For example:

>>> print(FST('[a, b, c]').put_slice('[x, y]', 1, 2).src)
[a, x, y, c]

In this case the elements `x, y` replaced the element `b` in the target. If instead of replacing with the elements of
the node being put you wish to just put the node itself then specify `one=True`.

>>> print(FST('[a, b, c]').put_slice('[x, y]', 1, 2, one=True).src)
[a, [x, y], c]

The same thing could have been accomplished just by putting the node with a normal `put()` to the second element of the
target. The reason the `one` option exists is when you want to replace multiple elements with a single "one" instead of
using that one as a slice.

>>> print(FST('[a, b, c]').put_slice('[x, y]', 1, 3, one=True).src)
[a, [x, y]]

This is allowed anywhere where the single element being put would be allowed to replace multiple elements.

>>> print(FST('del a, b, c, d').put_slice('x, y', 1, 3, one=True).src)
del a, (x, y), d

It also allows putting things which are not slices of the given type to a slice range withing the target.

>>> f = FST('case a | b | c | d: pass')

>>> print(f.pattern.put_slice('x as y', 1, 3, one=True).src)
a | (x as y) | d

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

`trivia=False` will just give you the individual element.

>>> pp(parent.get(1, trivia=False))
'target_stmt'

`trivia=True` and `trivia='block'` are the same for leading trivia and will give you the immediately preceding block of
comments.

>>> pp(parent.get(1, trivia=True))
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'

>>> pp(parent.get(1, trivia='block'))  # 'block' same as True for leading comments
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'

`trivia='all'` will give you all preceding comments including empty lines between them (up till previous statement or
start of block statement or top of module).

>>> pp(parent.get(1, trivia='all'))  # 'block' same as True for leading comments
'# pre-comment 1a'
'# pre-comment 1b'
''
''
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'

If the operation is a cut then these lines will be removed from the target.

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

Likewise on a put the trivia specifies what to overwrite.

>>> node = parent.copy()

>>> node.put('put_stmt', 1, trivia='all')
<Module ROOT 0,0..2,8>

>>> pp(node)
'pre_stmt'
''
'put_stmt'

If you wish to include empty lines to overwrite then add them to the trivia option like so:

>>> node = parent.copy()

>>> node.get(1, cut=True, trivia='block-')
<Expr ROOT 2,0..2,11>

>>> pp(node)
'pre_stmt'
''
'# pre-comment 1a'
'# pre-comment 1b'

Note the trailing `'-'` which means delete all empty lines. You can also specify a maximum number of empty lines to
delete.

>>> node = parent.copy()

>>> node.get(1, cut=True, trivia='block-1')
<Expr ROOT 2,0..2,11>

>>> pp(node)
'pre_stmt'
''
'# pre-comment 1a'
'# pre-comment 1b'
''

>>> node = parent.copy()

>>> node.get(1, cut=True, trivia='block-2')
<Expr ROOT 2,0..2,11>

>>> pp(node)
'pre_stmt'
''
'# pre-comment 1a'
'# pre-comment 1b'

When getting a node and specifying empty space with the minus `'-'` then the space is cut from the source on a cut but
not returned in the gotten node.

>>> node = parent.copy()

>>> pp(node.get(1, cut=True, trivia='block-1'))
'# pre-comment 2a'
'# pre-comment 2b'
'target_stmt'

If you want the space then use a plus `'+'` instead of the minus `'+'`.

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

The plus instead of the minus only means return the empty space that was cut. In all cases the space is removed from the
target.

All of this applies to all statement-ish operations but also expression-ish slice operations as well.

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

The default leading trivia is `'block'`.

## Trivia (trailing)

This is similar to leading trivia but has an extra option `'line'` which specifies just the trailing comment on the same
line as the element or last element of the slice, not any other comments of a following block.

Trailing trivia can be specified by passing a full tuple for leading and trailing as the `trivia` option of the form
`trivia=(leading, trailing)`. You can pass `None` for the leading element in order to use the currenly set default which
is normally `'block'` for leading trivia.

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

The default trailing trivia is `'line'`.

>>> pp(parent.get(0))
'target_stmt  # line-comment'

You can turn that off.

>>> pp(parent.get(0, trivia=(None, False)))
'target_stmt'

Trailing block comment.

>>> pp(parent.get(0, trivia=(None, 'block')))
'target_stmt  # line-comment'
'# post-comment 1a'
'# post-comment 1b'

With space.

>>> pp(parent.get(0, trivia=(None, 'block+1')))
'target_stmt  # line-comment'
'# post-comment 1a'
'# post-comment 1b'
''

All.

>>> pp(parent.get(0, trivia=(None, 'all+')))
'target_stmt  # line-comment'
'# post-comment 1a'
'# post-comment 1b'
''
''
'# post-comment 2a'
'# post-comment 2b'
''

The same rules apply for what is copied and what is removed or overwritten with plus and minus. You can specify how to
handle both leading and trailing trivia as one parameter, for example `trivia=('block+2', 'all+')`.
"""