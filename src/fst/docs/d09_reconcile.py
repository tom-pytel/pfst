r"""
# Edit pure AST while preserving formatting

To be able to execute the examples, import this.
```py
>>> from fst import *
```

## What it does

The idea of the `reconcile()` functionality is not to be able to put `AST` nodes to an `FST` tree under your own
control, this can easily be done. Rather it is to allow other code to modify `AST` trees without knowing anything about
`FST` and then having `FST` reconcile these changes with what it knows about the tree to preserve formatting where it
can.

```py
>>> f = FST('''
... if i:  # 1
...   j = [f(), # 2
...        g() # 3
...       ]
... '''.strip())

>>> m = f.mark()

>>> # notice the 'f.a', all changes must happen in the `AST` nodes
>>> f.a.body[0].value.elts[0] = Name(id='pure_ast')
>>> f.a.body.append(Assign(targets=[Name(id='k')], value=Constant(value=3)))

>>> f = f.reconcile(m)

>>> print(f.src.rstrip())
if i:  # 1
  j = [pure_ast, # 2
       g() # 3
      ]
  k = 3
```

You can reuse and mix nodes from the original tree.

```py
>>> m = f.mark()

>>> f.a.body.append(f.a.body[0])
>>> f.a.body[0].value.elts.append(Constant(value='pure_ast'))

>>> f.a.body[0] is f.a.body[2]  # we put the same AST node in two different places
True

>>> f = f.reconcile(m)

>>> print(f.src.rstrip())
if i:  # 1
  j = [pure_ast, # 2
       g(), 'pure_ast'
      ]
  k = 3
  j = [pure_ast, # 2
       g(), 'pure_ast'
      ]

>>> f.a.body[0] is f.a.body[2]  # the same AST used in two places is deduplicated
False
```

You can add in `AST` nodes from other `FST` trees and they will retain their formatting, though not if you modify those
`AST`s since the only tree that has reconcile information to be able to preserve formatting if this is done is the
original tree that was marked, for now.

```py
>>> m = f.mark()

>>> f.a.body.append(FST('l="formatting"  # stays').a)
>>> f.a.body.append(FST('m  =  "formatting"  # disappears').a)
>>> f.a.body[-1].value = Constant(value="formatting")

>>> f = f.reconcile(m)

>>> print(f.src.rstrip())
if i:  # 1
  j = [pure_ast, # 2
       g(), 'pure_ast'
      ]
  k = 3
  j = [pure_ast, # 2
       g(), 'pure_ast'
      ]
  l="formatting"  # stays
  m = 'formatting'
```

But if the goal is to change a small part of a larger program then this should work well enough.

```py
>>> f = FST('''
... from .data import (
...     scalar1,  # this is 60% for now
...     scalar2,  # the rest
... )
...
... def compute(x, y):
...     # Compute the weighted sum
...     result = (
...         x * 0.6  # x gets 60%
...         + y * 0.4  # y gets 40%
...     )
...
...     # Apply thresholding
...     if (
...         result > 10
...         # cap high values
...         and result < 100  # ignore overflow
...     ):
...         return result
...     else:
...         return 0
... '''.strip())

>>> m = f.mark()

>>> f.a.body[1].body[0].value.left.right = Name(id='scalar1')
>>> f.a.body[1].body[0].value.right.right = Name(id='scalar2')
>>> f.a.body[1].body[-1].orelse[0] = (
...     If(test=Compare(left=Name(id='result'),
...                     ops=[Gt()],
...                     comparators=[Constant(value=1)]),
...        body=[f.a.body[1].body[-1].orelse[0]],
...        orelse=[Return(value=UnaryOp(op=USub(), operand=Constant(value=1)))]
...     )
... )

>>> f = f.reconcile(m)

>>> # we print like this because of doctest
>>> print('\n'.join(l or '.' for l in f.lines))
from .data import (
    scalar1,  # this is 60% for now
    scalar2,  # the rest
)
.
def compute(x, y):
    # Compute the weighted sum
    result = (
        x * scalar1  # x gets 60%
        + y * scalar2  # y gets 40%
    )
.
    # Apply thresholding
    if (
        result > 10
        # cap high values
        and result < 100  # ignore overflow
    ):
        return result
    elif result > 1:
        return 0
    else:
        return -1
.
```

## How it works

`mark()` makes a copy of the tree you will reconcile later, then later `reconcile()` walks the modified tree from top to
bottom comparing to the stored tree. Anywhere there are differences it uses the `FST` editing mechanisms to put the
changed nodes as if a human being was making the changes.

Anytime an underlying operation fails or is unavailable (due to not being implemented yet), `reconcile()` simply retries
the operation at a higher level node. This does lose formatting as the `put()` in that case winds up using the `AST`
node, but at least it makes the operation possible.

This method is not particularly fast when there are a lot of nested changes as it is possible that large chunks of the
source wind up being put multiple times with minor deviations. But it does a better job at preserving formatting than
walking bottom-up.
"""
