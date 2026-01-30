r"""
# Options

To be able to execute the examples, import this.

>>> from fst import *

This is just print helper stuff for this documentation, you can ignore it.

>>> from pprint import pp

>>> def plines(lines):  # helper
...     print('\n'.join(repr(l) for l in lines))


## Global defaults

For a full list of global options see `fst.fst.FST.options()`.

Many of the `FST` functions have an `**options` kwarg which indicates they can take one or more keyword-only parameters
to control how the operation behaves. Most of these options also have global defaults which can be set and which will be
used if a specific value for that option is not passed to the function.

**Note:** The global defaults are thread-local and start out with module-defined defaults for each new thread (the
values they have when you first import `fst`).

To get a list of all global options defaults do.

>>> pp(FST.get_options())
{'raw': False,
 'trivia': True,
 'coerce': True,
 'elif_': True,
 'pep8space': True,
 'docstr': True,
 'pars': 'auto',
 'pars_walrus': False,
 'pars_arglike': True,
 'norm': False,
 'norm_self': None,
 'norm_get': None,
 'set_norm': 'star',
 'op_side': 'left',
 'args_as': None}

For example the option `pars` defaults to `'auto'` which will (among other things) strip parentheses when copying from a
node which has them.

>>> print(FST('target = (value)').value.copy().src)
value

Normally you can control this by passing the option to the operation.

>>> print(FST('target = (value)').value.copy(pars=True).src)
(value)

Instead of passing the option to each operation, you can just set it globally.

>>> old = FST.set_options(pars=True)

>>> print(FST('target = (value)').value.copy().src)
(value)

The value that was returned from `set_options()` is the previous value of the option that was set (or multiple if
setting more than one at a time).

>>> old
{'pars': 'auto'}

You can reset the previous global default by passing this value back to `set_options()`.

>>> FST.set_options(**old)
{'pars': True}

The value returned this time was the default that we had set previously. The new value is now `'auto'` and we can verify
by querying this option specifically.

>>> FST.get_option('pars')
'auto'

Or just doing the operation again to check.

>>> print(FST('target = (value)').value.copy().src)
value

You can also temporarily set some options you want to use in a block with the `FST.options()` context manager.

>>> with FST.options(pars=True):
...     print(FST('target = (value)').value.copy().src)
...     print(FST.get_option('pars'))
(value)
True

And now out of the block the `pars` option is back to what it was before.

>>> FST.get_option('pars')
'auto'

A list of all the globally settable options follows below. There are a few more options like `to` and `op` which are
purely dynamic call-time options as they are context-specific to each call, those are not listed below and they cannot
be set globally.

All these options can be either set globally or passed to the functions as keyword parameters so they will mostly be
demostrated by passing them to the functions below. These examples are not meant to explain these options, the rest of the
documentation is for that, here we just show their usage.

If you want a full up-to-date list of all options with their possible values and defaults then see
`fst.fst.FST.options()`.

## `raw` option

This option specifies whether normal prescribed put operations are done (`raw=False`), raw source reparse operations are
done instead (`raw=True`), or whether raw source reparse is used as a fallback if the prescribed operation fails
(`raw='auto'`). For information on how raw operations work see `fst.docs.d11_raw`.

>>> print(FST('{a: b}').put('**c', 0, raw=False).src)  # default
Traceback (most recent call last):
...
fst.NodeError: cannot put as 'one' item to a Dict slice

>>> print(FST('{a: b}').put('**c', 0, raw=True).src)
{**c}

>>> print(FST('{a: b}').put('**c', 0, raw='auto').src)
{**c}

The reason `'auto'` is not set by default is because it can generate confusing error messages and prescribed operations
can handle most stuff anyway.


## `trivia` option

This option specifies how comments and whitespace are handled on copies, deletions and replacements. There is a small
difference on what can be set globally and what can be passed to a function in that a function can take `None` values
for the leading or trailing trivia specifier to indicate that global default should be used for that particular trivia.
For more information on trivia see `fst.docs.d06_slices`.

>>> f = FST('''
... statement1
... # after empty line
...
... # block comment
... statement2  # line comment
... # trailing block comment
... '''.strip())

>>> plines(f.get(1, trivia='all').lines)
'# after empty line'
''
'# block comment'
'statement2  # line comment'

>>> plines(f.get(1, trivia=('block+1', False)).lines)
''
'# block comment'
'statement2'

>>> plines(f.get(1, trivia=(None, 'all')).lines)
'# block comment'
'statement2  # line comment'
'# trailing block comment'


## `coerce` option

This option specifies whether coercion of similar node types should be allowed when the exact node doesn't match but is
close. This mostly applies to `AST` and `FST` nodes passed to put functions. The option exists so you can turn this
behavior **OFF** if you want strict type checking since it is on by default.

>>> f = FST('import original')

>>> print(f.put(FST('match', 'alias'), 0, coerce=False).src)  # alias matches node type
import match

>>> print(f.put(FST('mismatch', 'Name'), 0, coerce=False).src)
Traceback (most recent call last):
...
fst.NodeError: expecting alias, got Name, coerce disabled

>>> print(f.put(FST('coerced', 'Name'), 0, coerce=True).src)  # default
import coerced


## `elif_` option

This option specifies whether `elif ...` should be used if possible on a put instead of an `else: if ...`. This only
applies to put operations and not a get which is a cut.

>>> f = FST('''
... if a:
...     thing_a
... else:
...     thing_b
... '''.strip())

>>> print(f.put('if c: thing_c', 0, 'orelse', elif_=True).src)  # default
if a:
    thing_a
elif c: thing_c

>>> print(f.orelse[0].replace('if d: thing_d', elif_=False).root.src)
if a:
    thing_a
else:
    if d: thing_d


## `pep8space` option

This option specifies whether you want function and class definition spacing according to PEP8 or just single line
spacing at module scope or none.

>>> f = FST('''
... def f(): pass
... def g(): pass
... '''.strip())  # this is module scope

>>> plines(f.copy().body.insert('def h(): _', 1, pep8space=True).base.lines)  # default
'def f(): pass'
''
''
'def h(): _'
''
''
'def g(): pass'

>>> plines(f.copy().body.insert('def h(): _', 1, pep8space=1).base.lines)
'def f(): pass'
''
'def h(): _'
''
'def g(): pass'

>>> plines(f.copy().body.insert('def h(): _', 1, pep8space=False).base.lines)
'def f(): pass'
'def h(): _'
'def g(): pass'

>>> f = FST('''
... class cls:
...     def f(): pass
...     def g(): pass
... '''.strip())

Below module scope `pep8space=True` gives single line spacing.

>>> plines(f.copy().body.insert('def h(): _', 1, pep8space=True).base.lines)
'class cls:'
'    def f(): pass'
''
'    def h(): _'
''
'    def g(): pass'


## `docstr` option

This option specifies which docstrings should be in/dedented when copying code blocks.

>>> f = FST('''
... class cls:
...     def f():
...         \'\'\'Normal
...         docstring\'\'\'
...         something()
...         \'\'\'Unorthodox
...         docstring\'\'\'
... '''.strip())

>>> print(f.body[0].copy(docstr=True).src)  # default
def f():
    '''Normal
    docstring'''
    something()
    '''Unorthodox
    docstring'''

>>> print(f.body[0].copy(docstr='strict').src)
def f():
    '''Normal
    docstring'''
    something()
    '''Unorthodox
        docstring'''

>>> print(f.body[0].copy(docstr=False).src)
def f():
    '''Normal
        docstring'''
    something()
    '''Unorthodox
        docstring'''


## `pars` option

This option specifies whether parentheses are copied or added where needed or not. If you use `pars=False` you can
create invalid trees. For more information on parentheses see `fst.docs.d09_parentheses`.

>>> print(FST('a = (b)').value.copy(pars='auto').src)  # default
b
>>> print(FST('a * b').right.replace('x + y', pars='auto').root.src)
a * (x + y)

>>> print(FST('a = (b)').value.copy(pars=True).src)
(b)
>>> print(FST('a * b').right.replace('x + y', pars=True).root.src)
a * (x + y)

>>> print(FST('a = (b)').value.copy(pars=False).src)
b
>>> print(FST('a * b').right.replace('x + y', pars=False).root.src)
a * x + y


## `pars_walrus` option

This option specifies whether to mirror the python `ast` module behavior and always parenthesize `NamedExpr` walrus
expressions that are copied out to root level or not (`fst` does not need this but maybe you want `ast` parsable
expression source). This is apart from the `pars` option and any explicit `par()` or walrus expressions explicitly
created with parentheses.

>>> f = FST('b, c := d, e')

>>> print(f.elts[1].copy(pars_walrus=True, pars=True).src)  # default
(c := d)
>>> print(f.elts[1].copy(pars_walrus=True, pars=False).src)
(c := d)
>>> print(f.elts[1].copy(pars_walrus=True, pars='auto').src)
(c := d)

>>> print(f.elts[1].copy(pars_walrus=False, pars=True).src)
c := d
>>> print(f.elts[1].copy(pars_walrus=False, pars=False).src)
c := d
>>> print(f.elts[1].copy(pars_walrus=False, pars='auto').src)
c := d

>>> print(f.elts[1].copy(pars_walrus=None, pars=True).src)
(c := d)
>>> print(f.elts[1].copy(pars_walrus=None, pars=False).src)
c := d
>>> print(f.elts[1].copy(pars_walrus=None, pars='auto').src)
(c := d)


## `pars_arglike` option

This option specifies whether to parenthesize "argumentlike" expressions copied out of `Call.args`, `ClassDef.bases`
or `Subscript.slice`. The behavior is identical to the `pars_walrus` option but for these otherwise
invalid-if-not-parenthesized expressions instead of walruses.

>>> f = FST('call(*a or b)')

>>> print(f.args[0].copy(pars_arglike=True, pars=True).src)  # default
*(a or b)
>>> print(f.args[0].copy(pars_arglike=True, pars=False).src)
*(a or b)
>>> print(f.args[0].copy(pars_arglike=True, pars='auto').src)
*(a or b)

>>> print(f.args[0].copy(pars_arglike=False, pars=True).src)
*a or b
>>> print(f.args[0].copy(pars_arglike=False, pars=False).src)
*a or b
>>> print(f.args[0].copy(pars_arglike=False, pars='auto').src)
*a or b

>>> print(f.args[0].copy(pars_arglike=None, pars=True).src)
*(a or b)
>>> print(f.args[0].copy(pars_arglike=None, pars=False).src)
*a or b
>>> print(f.args[0].copy(pars_arglike=None, pars='auto').src)
*(a or b)


## `norm`, `norm_self` and `norm_get` options

These options specify whether normalization should take place for operations or not. Normalization ensures that the
resulting `AST` trees are valid. `fst` allows you to create invalid trees during editing by deleting all or most
elements from nodes which don't normally allow it for the sake of simplifying editing. For more information on
normalization see `fst.docs.d06_slices`.

>>> _ = (f := FST('{a, b}')).get_slice(0, 2, cut=True, norm_self=None, norm=True)
>>> _ = f.dump('stmt')
0: {*()}
Set - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,4
     .value Tuple - 0,2..0,4
       .ctx Load
     .ctx Load

>>> _ = (f := FST('{a, b}')).get_slice(0, 2, cut=True, norm_self=None, norm=False)
>>> _ = f.dump('stmt')  # invalid empty set
0: {}
Set - ROOT 0,0..0,2

`norm_self=None` makes it use `norm`, otherwise if specified it overrides `norm`. Now that the relationship with `norm`
has been demonstrated we can leave it out in the further examples.

>>> _ = FST('{a, b}').get_slice(1, 1, norm_get=True).dump('stmt')
0: {*()}
Set - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,4
     .value Tuple - 0,2..0,4
       .ctx Load
     .ctx Load

>>> _ = FST('{a, b}').get_slice(1, 1, norm_get=False).dump('stmt')  # invalid
0: {}
Set - ROOT 0,0..0,2

`norm_self` and `norm_get` exist for fine-grained control. `norm` exists as a convenience to set both of these at once.

When using for an operation on a `Set`, a `set_norm` option value from below can be passed directly in any of the `norm`
options as a truthy value and will override current `set_norm`.


## `set_norm` option

This options specifies what the empty set representation for the normalization should be, both to create for `self` and
return for `get`.

>>> print(FST('{a, b}').get_slice(0, 0, norm=True, set_norm='call').src)
set()

>>> print(FST('{a, b}').get_slice(0, 0, norm=True, set_norm='star').src)
{*()}

>>> _ = (f := FST('{a, b}')).get_slice(0, 2, cut=True, norm=True, set_norm='call')
>>> print(f.src)
set()


## `op_side` option

This option specifies which side of an operand an operator lives on by default. This option is a hint and if the
operation cannot be carried out with the operator on this side it will be carried out with the operator on the other or
none if no side possible.

This option currently only applies to operations on `Compare` and `BoolOp` nodes and really only needs to exist for
`Compare`, for `BoolOp` it is more of an aesthetic selection of which side operator to modify if they are even
different. For more information on this option see `fst.docs.d06_slices`.

For delete it specifies which side (of the slice being deleted) an extra operator is deleted as well.

>>> print(FST('a < b == c > d').put_slice(None, 1, 3, op_side='left').src)  # default
a > d

>>> print(FST('a < b == c > d').put_slice(None, 1, 3, op_side='right').src)
a < d

For insertion you can specify an operator to put and this will tell it which side to put it on.

>>> print(FST('a < b').put_slice('c', 1, 1, op='==', op_side='left').src)
a == c < b

>>> print(FST('a < b').put_slice('c', 1, 1, op='!=', op_side='right').src)
a < c != b


## `args_as` options

This option allows conversion of arguments between `posonlyargs`, `args` and `kwonlyargs` when doing slice operations on
an `arguments` node. When getting a slice it is applied after the get on the slice to be returned. When putting a slice
it is applied on the slice being put before the put is attempted. This option is global in order to to allow
`with FST.options(args_as=?)` usage but is really meant to be specified on a per-call basis.

>>> print(FST('a, /, b, *, c').get_slice(args_as='pos').src)
a, b, c, /

>>> print(FST('a, /, b, *, c').get_slice(args_as='arg').src)
a, b, c

>>> print(FST('a, /, b, *, c').get_slice(args_as='kw').src)
*, a, b, c

>>> print(FST('a, /, b, *c').get_slice(args_as='arg').src)
a, b, *c

>>> print(FST('a, /, b, *c').get_slice(args_as='arg_only').src)
Traceback (most recent call last):
...
fst.NodeError: cannot have vararg for args_as='arg_only'

>>> print(FST('a, /, b, *, c, **d').get_slice(args_as='kw').src)
*, a, b, c, **d

>>> print(FST('a, /, b, *, c, **d').get_slice(args_as='kw_only').src)
Traceback (most recent call last):
...
fst.NodeError: cannot have kwarg for args_as='kw_only'

>>> print(FST('a, /, b, *c, d, **e').get_slice(args_as='pos').src)
Traceback (most recent call last):
...
fst.NodeError: cannot have vararg for args_as='pos'

>>> print(FST('a, /, b, *c, d, **e').get_slice(args_as='pos_maybe').src)
a, b, /, *c, d, **e

>>> print(FST('a, /, b, *c, d, **e').get_slice(args_as='arg').src)
Traceback (most recent call last):
...
fst.NodeError: cannot have keywords following vararg for args_as='arg'

>>> print(FST('a, /, b, *c, d, **e').get_slice(args_as='arg_maybe').src)
a, b, *c, d, **e

>>> print(FST('a, /, b, *c, d, **e').get_slice(args_as='kw').src)
Traceback (most recent call last):
...
fst.NodeError: cannot have vararg for args_as='kw'

>>> print(FST('a, /, b, *c, d, **e').get_slice(args_as='kw_maybe').src)
a, b, *c, d, **e


## Non-global options

There are some options which can be passed to certain functions which are contextual and don't and can't have global
defaults, such as the `to` option when putting a single element in raw mode.

>>> 'to' in FST.get_options()
False

>>> f = FST('[a, b, c, d, e, f]')

>>> f.elts[1].replace('zzz', to=f.elts[-2], raw=True)
<Name 0,4..0,7>

>>> print(f.src)
[a, zzz, f]

Or the `op` option when doing `Compare` slice put operations and providing an operator for just that single put.

For more information on `to` see `fst.docs.d11_raw` and for `op` see `fst.docs.d06_slices`.
"""
