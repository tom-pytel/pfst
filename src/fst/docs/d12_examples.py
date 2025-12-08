r'''
# Example recipes

These are a few snippets which do some real-world-ish things. The comment handling blemishes are left in place and your
actual mileage with comments may vary. It depends very much of correct usage of the `trivia` option both on `get()` and
`put()`, and comment handling in general needs a bit more work (a lot more work), but they are preserved mostly.

The examples are deliberately not the most efficient but are rather meant to show off `fst` usage and features. Some of
them are somewhat linter-y, which is not the intended use of this module, but fine for demonstration purposes.

To be able to execute the examples, import this.

>>> from fst import *

And this is just a print helper function for this documentation specifically, you can ignore it.

>>> def pprint(src):  # helper
...    print(src.replace('\n\n', '\n\xa0\n'))  # replace() to avoid '<BLANKLINE>'

## `else if` chain to `elif`

`fst` has `elif` <-> `else if` code built in as its needed for statement insertions and deletions from conditional
bodies so its fairly easy to leverage to change these kinds of chains.

```py
>>> src = r"""
... def func():
...     # pre-if-a
...     if a:  # if-a
...         # pre-i
...         i = 1  # i
...         # post-i
...
...     else:  # else-a
...         # pre-if-b
...         if b:  # if-b
...             # pre-j
...             j = 2  # j
...             # post-j
...
...         else:  # else-b
...             # pre-if-c
...             if c:  # if-c
...                 # pre-k
...                 k = 3  # k
...                 # post-k
...
...             else:  # else-c
...                 # pre-l
...                 l = 4  # l
...                 # post-l
...             # post-else-c
...
...         # post-else-b
...
...     # post-else-a
... """.strip()
```

Function.

```py
>>> def else_if_chain_to_elifs(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if (f.is_elif() is False           # False means normal `if`, not an `elif`
...             and f.parent.is_If             # in a parent `if`
...             and f.pfield == ('orelse', 0)  # as first element of `.orelse` body
...             and len(f.parent.orelse) == 1  # which has only this node
...         ):
...             f.replace(  # can replace while walking
...                 f.copy(trivia=('block', 'all')),
...                 trivia=(False, 'all'),
...                 elif_=True,  # elif_=True is default, here to show usage
...             )
...
...     return fst.src
```

Original.

```py
>>> pprint(src)
def func():
    # pre-if-a
    if a:  # if-a
        # pre-i
        i = 1  # i
        # post-i
 
    else:  # else-a
        # pre-if-b
        if b:  # if-b
            # pre-j
            j = 2  # j
            # post-j
 
        else:  # else-b
            # pre-if-c
            if c:  # if-c
                # pre-k
                k = 3  # k
                # post-k
 
            else:  # else-c
                # pre-l
                l = 4  # l
                # post-l
            # post-else-c
 
        # post-else-b
 
    # post-else-a
```

Processed.

```py
>>> pprint(else_if_chain_to_elifs(src))
def func():
    # pre-if-a
    if a:  # if-a
        # pre-i
        i = 1  # i
        # post-i
 
    # pre-if-b
    elif b:  # if-b
        # pre-j
        j = 2  # j
        # post-j
 
    # pre-if-c
    elif c:  # if-c
        # pre-k
        k = 3  # k
        # post-k
 
    else:  # else-c
        # pre-l
        l = 4  # l
        # post-l
    # post-else-c
 
    # post-else-b
 
    # post-else-a
```

## `elif` chain to `else if`

This is just the inverse of the `else if` to `elif` code, just as easy.

```py
>>> src = r"""
... def func():
...     # pre-if-a
...     if a:  # if-a
...         # pre-i
...         i = 1  # i
...         # post-i
...
...     # pre-if-b
...     elif b:  # if-b
...         # pre-j
...         j = 2  # j
...         # post-j
...
...     # pre-if-c
...     elif c:  # if-c
...         # pre-k
...         k = 3  # k
...         # post-k
...
...     else:  # else-c
...         # pre-l
...         l = 4  # l
...         # post-l
...     # post-else-c
...
...     # post-else-b
...
...     # post-else-a
... """.strip()
```

Function.

```py
>>> def elif_chain_to_else_ifs(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if (f.is_elif()                    # True means `elif`
...             and f.parent.is_If             # in a parent `if`
...             and f.pfield == ('orelse', 0)  # as first element of `.orelse` body
...             and len(f.parent.orelse) == 1  # which has only this node
...         ):
...             f.replace(  # can replace while walking
...                 f.copy(trivia=('block', 'block')),
...                 trivia=('block', 'block'),
...                 elif_=False,
...             )
...
...     return fst.src
```

Original.

```py
>>> pprint(src)
def func():
    # pre-if-a
    if a:  # if-a
        # pre-i
        i = 1  # i
        # post-i
 
    # pre-if-b
    elif b:  # if-b
        # pre-j
        j = 2  # j
        # post-j
 
    # pre-if-c
    elif c:  # if-c
        # pre-k
        k = 3  # k
        # post-k
 
    else:  # else-c
        # pre-l
        l = 4  # l
        # post-l
    # post-else-c
 
    # post-else-b
 
    # post-else-a
```

Processed.

```py
>>> pprint(elif_chain_to_else_ifs(src))
def func():
    # pre-if-a
    if a:  # if-a
        # pre-i
        i = 1  # i
        # post-i
 
    else:
        # pre-if-b
        if b:  # if-b
            # pre-j
            j = 2  # j
            # post-j
 
        else:
            # pre-if-c
            if c:  # if-c
                # pre-k
                k = 3  # k
                # post-k
 
            else:  # else-c
                # pre-l
                l = 4  # l
                # post-l
            # post-else-c
 
    # post-else-b
 
    # post-else-a
```

## `lambda` to `def`

Maybe you have too many lambdas and want proper function defs for debugging or logging or other tools. Note the defs are
left in the same scope in case of nonlocals.

```py
>>> src = r"""
... # pre-lambda comment
... mymin = lambda a, b: a if a < b else b  # inline lambda comment
... # post-lambda comment
...
... class cls:
...     name = lambda self: str(self)
...
...     def method(self, a, b):
...         add = lambda: a + b
...
...         return add()
... """.strip()
```

Function.

```py
>>> def lambdas_to_defs(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if (f.is_Assign
...             and f.value.is_Lambda
...             and f.targets[0].is_Name
...             and len(f.targets) == 1   # for demo purposes just deal with this case
...         ):
...             flmb = f.value
...             fdef = FST(f"""
... def {f.targets[0].id}({flmb.args.src}):
...     return _
...             """.strip())  # template
...             fdef.body[0].value = flmb.body.copy()
...
...             f.replace(
...                 fdef,
...                 trivia=(False, 'line'),  # eat line comment but not leading
...                 pep8space=1,  # don't doublespace inserted func def (at mod scope)
...             )
...
...     return fst.src
```

Original.

```py
>>> pprint(src)
# pre-lambda comment
mymin = lambda a, b: a if a < b else b  # inline lambda comment
# post-lambda comment
 
class cls:
    name = lambda self: str(self)
 
    def method(self, a, b):
        add = lambda: a + b
 
        return add()
```

Processed.

```py
>>> pprint(lambdas_to_defs(src))
# pre-lambda comment
def mymin(a, b):
    return a if a < b else b
 
# post-lambda comment
 
class cls:
    def name(self):
        return str(self)
 
    def method(self, a, b):
        def add():
            return a + b
 
        return add()
```

## squash nested `with`s

Slice operations make this easy enough. We only do synchronous `with` here as you can't mix sync with async anyway.

```py
>>> src = r"""
... # pre-with comment
... with open(a) as f:
...     with (
...         lock1,  # first lock
...         func() as lock2,  # this doesn't get preserved
...     ):
...         with ctx():  # this does not belong to ctx()
...             # body comment
...             pass
...             # end body comment
...
... # post-with comment
... """.strip()
```

Function.

```py
>>> def squash_nested_withs(src):
...     fst = FST(src, 'exec')
...
...     for f in reversed([f for f in fst.walk() if f.is_stmt]):
...         if (f.is_With              # we are a `with`, we don't do `async with` here
...             and f.parent.is_With   # parent is another `with`
...             and f.pfield.idx == 0  # we are first child (we know we are in `.body`)
...         ):
...             f.parent.items.extend(f.items.copy())
...             f.parent.put_slice(
...                 # we cut to remove previous comments since not overwriting
...                 f.get_slice(trivia=('all+', 'block'), cut=True),
...                 trivia=(False, False),
...             )
...
...     return fst.src
```

Original.

```py
>>> pprint(src)
# pre-with comment
with open(a) as f:
    with (
        lock1,  # first lock
        func() as lock2,  # this doesn't get preserved
    ):
        with ctx():  # this does not belong to ctx()
            # body comment
            pass
            # end body comment
 
# post-with comment
```

Processed.

```py
>>> pprint(squash_nested_withs(src))
# pre-with comment
with (open(a) as f,
     lock1,  # first lock
     func() as lock2, ctx()
     ):
    # body comment
    pass
    # end body comment
 
# post-with comment
```

## comprehension to loop

We build up a body and replace the original comprehension `Assign` statement with the new statements.

```py
>>> src = r"""
... def f(k):
...     # safe comment
...     clean = [i for i in k]
...
...     # happy comment
...     messy = [
...         ( i )  # weird pars
...         for (
...             j
...         ) in k  # outer loop
...         if
...         j  # misc comment
...         and not validate(j)
...         for i in j  # inner loop
...         if i
...         if validate(i)
...     ]
...     # silly comment
...
...     return clean + messy
... """.strip()
```

Function.

```py
>>> def list_comprehensions_to_loops(src):
...     fst = FST(src, 'exec')
...
...     for f in fst.walk():
...         if (f.is_Assign
...             and f.value.is_ListComp
...             and f.targets[0].is_Name
...             and len(f.targets) == 1
...         ):
...             var = f.targets[0].id
...             fcomp = f.value
...             fcur = ftop = FST(f'{var} = []\n_', 'exec')
...             # the `_` will become first `for`
...
...             for fgen in fcomp.generators:
...                 ffor = FST('for _ in _:\n    _')  # for loop, just copy the source
...                 ffor.target = fgen.target.copy()
...                 ffor.iter = fgen.iter.copy()
...
...                 fcur = fcur.body[-1].replace(ffor)
...                 fifs = fgen.ifs
...                 nifs = len(fifs)
...
...                 if nifs:  # if no ifs then no test
...                     if nifs == 1:  # if single test then just use that
...                         ftest = fifs[0].copy()
...
...                     else:  # if multiple then join with `and`
...                         ftest = FST(' and '.join('_' * nifs))
...
...                         for i, fif in enumerate(fifs):
...                             ftest.values[i] = fif.copy()
...
...                     fifstmt = FST('if _:\n    _')
...                     fifstmt.test = ftest
...
...                     fcur = fcur.body[-1].replace(fifstmt)
...
...             # the ffor is the last one processed above (the innermost)
...             fcur.body[-1].replace(f'{var}.append({fcomp.elt.copy().src})')
...
...             f.replace(
...                 ftop,
...                 one=False,  # this allows to replace a single element with multiple
...                 trivia=(False, False)
...             )
...
...     return fst.src
```

Original.

```py
>>> pprint(src)
def f(k):
    # safe comment
    clean = [i for i in k]
 
    # happy comment
    messy = [
        ( i )  # weird pars
        for (
            j
        ) in k  # outer loop
        if
        j  # misc comment
        and not validate(j)
        for i in j  # inner loop
        if i
        if validate(i)
    ]
    # silly comment
 
    return clean + messy
```

Processed.

```py
>>> pprint(list_comprehensions_to_loops(src))
def f(k):
    # safe comment
    clean = []
    for i in k:
        clean.append(i)
 
    # happy comment
    messy = []
    for j in k:
        if (j  # misc comment
            and not validate(j)):
            for i in j:
                if i and validate(i):
                    messy.append(i)
    # silly comment
 
    return clean + messy
```




'''
