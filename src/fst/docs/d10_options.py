r"""
# Options, `verify()` and `dump()`

To be able to execute the examples, import this.
```py
>>> from fst import *
```

## Individual functions

For a full list of global options see `fst.fst.FST.get_options()`.

Many of the `FST` functions have an `**options` kwarg which indicates they can take one or more keyword-only parameters
to control how the operation proceeds. Most of these options also have global defaults which can be set and which will
be used if a specific value for that option is not passed to the function.

```py
>>> print(FST('a = (b)').get(pars=False).src)
b

>>> print(FST('a = (b)').get(pars=True).src)
(b)
```

```py
>>> print(FST('{a: b}').put('**c', raw=True).root.src)
{**c}

>>> try:
...     FST('{a: b}').put('**c', raw=False)
... except Exception as exc:
...     print(exc)
cannot put as 'one' item to a Dict slice
```

```py
>>> src = '''
... if a:
...     pass
... '''.strip()

>>> add = '''
... if b:
...     return -1
... '''.strip()

>>> print(FST(src).orelse.append(add, elif_=False).root.src.rstrip())
if a:
    pass
else:
    if b:
        return -1

>>> print(FST(src).orelse.append(add, elif_=True).root.src.rstrip())
if a:
    pass
elif b:
    return -1
```

```py
>>> src = '\n'.join([  # because this example lives in a docstring already
... "class cls:",
... "    def f():",
... "        '''doc",
... "        str'''",
... ])

>>> print(FST(src).body[0].copy(docstr=False).src)
def f():
    '''doc
        str'''

>>> print(FST(src).body[0].copy(docstr=True).src)
def f():
    '''doc
    str'''
```

```py
>>> print(FST('{a, b}').put_slice('{*()}', 1, 1, fix_set_put=False).src)
{a, *(), b}

>>> print(FST('{a, b}').put_slice('{*()}', 1, 1, fix_set_put=True).src)
{a, b}
```

## Global defaults

These options can be set globally with the `set_options()` function, which returns the previous value.

```py
>>> FST.set_options(pars=False)
{'pars': 'auto'}

>>> print(FST('a = (b)').get().src)
b

>>> FST.set_options(pars=True)
{'pars': False}

>>> print(FST('a = (b)').get().src)
(b)

```

But then you have to remember to set them back, otherwise all your other examples which expect options to be in their
default state will fail.

```py
>>> FST.set_options(pars='auto')
{'pars': True}
```

For this reason there is also a context manager.

```py
>>> with FST.options(pars=False):
...     print(FST('a = (b)').get().src)
b

>>> with FST.options(pars=True):
...     print(FST('a = (b)').get().src)
(b)
```

Any given option default can also be queried.

```py
>>> FST.get_option('pars')
'auto'
```

Or get all global options.

```py
>>> from pprint import pp

>>> pp(FST.get_options())
{'pars': 'auto',
 'raw': False,
 'trivia': True,
 'elif_': True,
 'docstr': True,
 'pars_walrus': False,
 'fix_set_get': True,
 'fix_set_put': True,
 'fix_set_self': True,
 'fix_del_self': True,
 'fix_assign_self': True,
 'fix_matchor_get': True,
 'fix_matchor_put': True,
 'fix_matchor_self': True,
 'pep8space': True,
 'precomms': True,
 'postcomms': True,
 'prespace': False,
 'postspace': False}
```

## Special

There are some options which can be passed to certain functions which are contextual and don't have global defaults,
such as the `'to'` option when putting a single element in raw mode.

```py
>>> 'to' in FST.get_options()
False

>>> f = FST('[a, b, c, d, e, f]')

>>> f.elts[1].replace('zzz', to=f.elts[-2], raw=True)
<Name 0,4..0,7>

>>> print(f.src)
[a, zzz, f]
```
"""
