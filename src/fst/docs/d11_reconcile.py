r"""
# Edit pure AST while preserving formatting

To be able to execute the examples, import this.

>>> from fst import *

This is just a print helper function for this documentation, you can ignore it.

>>> def pprint(src):  # helper
...     print(src.replace('\n\n', '\n\xa0\n'))  # replace() to avoid '<BLANKLINE>'


## What it does

**Disclaimer:** This functionality is still experimental and unfinished so not all comments which should be may be
preserved and others may be duplicated. In fact the underlying problem of determining which comments belong where is not
completely solvable as the function cannot guess perfectly at human intentions, but much more can be done than is being
done currently.

The idea of the `reconcile()` functionality is not to be able to put `AST` nodes to an `FST` tree under your own
control, you can do that with the `put()` functions directly. Rather it is to allow other code that may already exist to
modify the `AST` tree directly without knowing anything about `fst` and then having `fst` reconcile these changes with
what it knows about the tree to preserve formatting where it can.

>>> f = FST('''
... if i:  # 1
...   j = [f(), # 2
...        g() # 3
...       ]
... '''.strip())

>>> f.mark()
<If ROOT 0,0..3,7>

Notice all changes must happen in the `AST` tree, `f.a` is the `AST` tree.

>>> a = f.a
>>> a.body[0].value.elts[0] = Name(id='pure_ast')
>>> a.body.append(Assign(targets=[Name(id='ast_assign')], value=Constant(value=3)))

>>> f = f.reconcile()

```py
>>> print(f.src)
if i:  # 1
  j = [pure_ast, # 2
       g() # 3
      ]
  ast_assign = 3
```

You can reuse and mix nodes from the original tree.

>>> f.mark()
<If ROOT 0,0..4,16>

>>> a = f.a
>>> a.body.append(a.body[0])
>>> a.body[0].value.elts.append(Constant(value='another_ast'))

We put the same `AST` node in two different places, this is allowed for `reconcile()`.

>>> a.body[0] is a.body[2]
True

>>> f = f.reconcile()

```py
>>> print(f.src)
if i:  # 1
  j = [pure_ast, # 2
       g(), # 3
       'another_ast'
      ]
  ast_assign = 3
  j = [pure_ast, # 2
       g(), # 3
       'another_ast'
      ]
```

That same `AST` used in two places was deduplicated.

>>> f.a.body[0] is f.a.body[2]
False

You can add in `AST` nodes from other `FST` trees and they will retain their formatting, though not if you modify those
`AST`s since the only tree that has reconcile information to be able to preserve formatting if this is done is the
original tree that was marked.

>>> f.mark()
<If ROOT 0,0..9,7>

>>> a = f.a
>>> a.body.append(FST('l="formatting"  # stays').a)
>>> a.body.append(FST('m  =  "formatting"  # disappears').a)
>>> a.body[-1].value = Constant(value="not formatted")

>>> f = f.reconcile()

```py
>>> print(f.src)
if i:  # 1
  j = [pure_ast, # 2
       g(), # 3
       'another_ast'
      ]
  ast_assign = 3
  j = [pure_ast, # 2
       g(), # 3
       'another_ast'
      ]
  l="formatting"  # stays
  m = 'not formatted'
```

AST transformer example.

>>> import ast

>>> def pure_AST_operation(node: AST):
...    class Transform(ast.NodeTransformer):
...        def visit_arg(self, node):
...            return ast.arg('NEW_' + node.arg.upper(), node.annotation)
...
...        def visit_Name(self, node):
...            if node.id in 'xy':
...                return ast.Name('NEW_' + node.id.upper())
...
...            return node
...
...        def visit_Constant(self, node):
...            return Name('X_SCALE' if node.value > 0.5 else 'Y_SCALE')
...
...    Transform().visit(node)

>>> f = FST('''
... def compute(x: float,  # x position
...             y: float,  # y position
... ) -> float:
...
...     # Compute the weighted sum
...     return (
...         x * 0.6  # scale width
...         + y * 0.4  # scale height
...     )
... '''.strip())

>>> f.mark()
<FunctionDef ROOT 0,0..8,5>

>>> pure_AST_operation(f.a)

>>> f = f.reconcile()

```py
>>> pprint(f.src)
def compute(NEW_X: float,  # x position
            NEW_Y: float,  # y position
) -> float:
 
    # Compute the weighted sum
    return (
        NEW_X * X_SCALE  # scale width
        + NEW_Y * Y_SCALE  # scale height
    )
```


## How it works

`mark()` makes a copy of the tree you will reconcile later, then later `reconcile()` walks the modified tree from top to
bottom comparing to the stored tree. Anywhere there are differences it uses the `FST` editing mechanisms to put the
changed nodes as if a human being was making the changes.

Anytime an underlying operation fails or is unavailable (due to not being implemented yet), `reconcile()` simply retries
the operation at a higher level node. This does lose formatting as the `put()` in that case winds up using the `AST`
node, but at least it makes the operation possible.

This method is not particularly fast when there are a lot of nested changes as it is possible that large chunks of the
source wind up being put multiple times with minor changes. But it does a better job at preserving formatting than
walking bottom-up.
"""
