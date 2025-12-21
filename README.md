# Overview

This module exists in order to facilitate quick and easy high level editing of Python source in the form of an `AST` tree while preserving formatting. It is meant to allow you to change Python code functionality while not having to deal with the miniutae of:

- operator precedence and parentheses
- indentation and line continuations
- commas, semicolons, and tuple edge cases
- comments and docstrings
- various Python version–specific syntax quirks
- lots more

See [Example Recipes](https://tom-pytel.github.io/pfst/fst/docs/d12_examples.html) for more in-depth examples.

```py
>>> import fst

>>> ext_ast = fst.parse('if a: b = c, d  # comment')

>>> ext_ast.f.body[0].body[0].value.elts[1:1] = 'u,\nv  # blah'

>>> print(fst.unparse(ext_ast))
if a: b = (c, u,
          v,  # blah
          d)  # comment
```

The tree is just normal `AST` with metadata.

```py
>>> import ast

>>> print(ast.unparse(ext_ast))
if a:
    b = (c, u, v, d)
```

`fst` works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provide the interface to format-preserving operations. Each operation through `fst` is a simultaneous edit of the `AST` tree and the source code and those are kept synchronized so that the current source will always parse to the current tree.

# Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)

# Install

From PyPI:

    pip install pfst

From GitHub using pip:

    pip install git+https://github.com/tom-pytel/pfst.git

From GitHub, after cloning for development:

    pip install -e .[dev]

# Example

```py
>>> from fst import *

>>> def else_if_chain_to_elifs(src):
...     fst = FST(src)
...
...     for f in fst.walk(If):  # we will only get the `ast.If` nodes
...         if (len(f.orelse) == 1
...             and f.orelse[0].is_elif() is False  # False means normal `if`, not an `elif`
...         ):
...             f.orelse[0].replace(  # can modify while walking, reput `if` as `elif`
...                 f.orelse[0].copy(trivia=('block', 'all')),  # get old `if`
...                 trivia=(False, 'all'),  # trivia specifies how to handle comments
...                 elif_=True,  # elif_=True is default, here to show usage
...             )
...
...     return fst.src
```

```py
>>> print(else_if_chain_to_elifs(r"""
... # pre-if-a
... if a:  # if-a
...     i = 1  # i
... else:  # else-a
...     # pre-if-b
...     if b:  # if-b
...         j = 2  # j
...     else:  # else-b
...         # pre-if-c
...         if c:  # if-c
...             k = 3  # k
...         else:  # else-c
...             l = 4  # l
...         # post-else-c
...     # post-else-b
... # post-else-a
... """.strip()))
# pre-if-a
if a:  # if-a
    i = 1  # i
# pre-if-b
elif b:  # if-b
    j = 2  # j
# pre-if-c
elif c:  # if-c
    k = 3  # k
else:  # else-c
    l = 4  # l
# post-else-c
# post-else-b
# post-else-a
```

# Features

Can zero out bodies.

```py
>>> f = FST('''
... def func(self):  # comment
...     pass
... '''.strip())

>>> del func.body

>>> print(func.src)
def func(self):  # comment
```

Simple edit.

```py
>>> func.args = 'a, b'

>>> func.body.append('return a * b  # blah')

>>> print(func.src)
def func(a, b):  # comment
    return a * b  # blah
```

Precedence.

```py
>>> func.body[0].value.right = 'x + y'

>>> print(func.src)
def func(a, b):  # comment
    return a * (x + y)  # blah
```

Use native AST.

```py
>>> func.body[0:0] = ast.Assign([ast.Name('a')], func.body[-1].value.a)

>>> func.body[-1].value = ast.Name('a')

>>> print(func.src)
def func(a, b):  # comment
    a = a * (x + y)
    return a  # blah
```

Edit partial source by location.

```py
>>> print(func.body[0])
<Assign 1,4..1,19>

>>> func.put_src('a *=', 1, 4, 1, 11)

>>> print(func.src)
def func(a, b):  # comment
    a *= (x + y)
    return a  # blah
```

The tree is kept synchronized.

```py
>>> func.dump()
FunctionDef - ROOT 0,0..2,12
  .name 'func'
  .args arguments - 0,9..0,13
    .args[2]
     0] arg - 0,9..0,10
       .arg 'a'
     1] arg - 0,12..0,13
       .arg 'b'
  .body[2]
   0] AugAssign - 1,4..1,16
     .target Name 'a' Store - 1,4..1,5
     .op Mult - 1,6..1,8
     .value BinOp - 1,10..1,15
       .left Name 'x' Load - 1,10..1,11
       .op Add - 1,12..1,13
       .right Name 'y' Load - 1,14..1,15
   1] Return - 2,4..2,12
     .value Name 'a' Load - 2,11..2,12
```

Its just a normal AST.

```py
>>> print(ast.dump(func.a, indent=2))
FunctionDef(
  name='func',
  args=arguments(
    args=[
      arg(arg='a'),
      arg(arg='b')]),
  body=[
    AugAssign(
      target=Name(id='a', ctx=Store()),
      op=Mult(),
      value=BinOp(
        left=Name(id='x', ctx=Load()),
        op=Add(),
        right=Name(id='y', ctx=Load()))),
    Return(
      value=Name(id='a', ctx=Load()))])
```

# Reconcile

This is intended to allow something which is not aware of `fst` to edit the `AST` tree while allowing `fst` to preserve
formatting where it can.

```py
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
```

```py
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
```

```py
>>> f.mark()
>>> pure_AST_operation(f.a)
>>> f = f.reconcile()
```

```py
>>> print(f.src)
def compute(NEW_X: float,  # x position
            NEW_Y: float,  # y position
) -> float:

    # Compute the weighted sum
    return (
        NEW_X * X_SCALE  # scale width
        + NEW_Y * Y_SCALE  # scale height
    )
```

# Misc

Traversal is in syntactic order.

```py
>>> list(f.src for f in FST('def f[T](a, b=1) -> int: pass').walk())
['def f[T](a, b=1) -> int: pass', 'T', 'a, b=1', 'a', 'b', '1', 'int', 'pass']
```

Locations are zero based in character units, not bytes. Most nodes have a location, including ones which don't in `AST`
nodes. Nodes that don't are `expr_context`, `boolop` (because they are one-to-many locations) and empty `arguments`.

```py
>>> FST('蟒=Æ+д').dump()
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name '蟒' Store - 0,0..0,1
  .value BinOp - 0,2..0,5
    .left Name 'Æ' Load - 0,2..0,3
    .op Add - 0,3..0,4
    .right Name 'д' Load - 0,4..0,5
```

Crazy syntax is handled correctly (which is a main goal of this module).

```py
>>> f = FST(r'''
... if True:
...     @decorator1
...
...     # pre-comment
...     \
...  @ \
...   ( decorator2 )(
...         a,
...     ) \
...     # post-comment
...
...     @ \
...     decorator3()
...
...     def func(): pass
... '''.strip())
```

```py
>>> d = f.body[0].get_slice(1, 2, 'decorator_list', cut=True, trivia=('all+', 'all+'))
```

```py
>>> d.dump('stmt+')
0:
1: # pre-comment
2: \
3: @ \
4: ( decorator2 )(
5:     a,
6: ) \
7: # post-comment
8:
_decorator_list - ROOT 0,0..8,0
  .decorator_list[1]
   0] Call - 4,0..6,1
     .func Name 'decorator2' Load - 4,2..4,12
     .args[1]
      0] Name 'a' Load - 5,4..5,5
```

```py
>>> print(f.src)
if True:
    @decorator1
    @ \
    decorator3()

    def func(): pass
```

```py
>>> f.body[0].put_slice(d, 'decorator_list', trivia=('all+', 'all+'))
```

```py
>>> print(f.src)
if True:

    # pre-comment
    \
    @ \
    ( decorator2 )(
        a,
    ) \
    # post-comment

    def func(): pass
```

For more examples see the documentation in `docs/`, or if you're feeling particularly masochistic have a look at the
tests in the `tests/` directory.

## TODO

This module is not finished but functional enough that it can be useful.

* Put one to:
  * `FormattedValue.conversion`
  * `FormattedValue.format_spec`
  * `Interpolation.str`
  * `Interpolation.conversion`
  * `Interpolation.format_spec`

* Prescribed get / put slice from / to:
  * `MatchClass.patterns`
  * `FunctionsDef/AsyncFunctionDef/ClassDef.args`
  * `ClassDef.bases+keywords`
  * `Call.args+keywords`
  * `MatchClass.patterns+kwd_attrs:kwd_patterns`
  * `JoinedStr.values`
  * `TemplateStr.values`

* Improve comment and whitespace handling, especially allow get / put comments in single element non-statement
operations where it may apply (where comment may belong to expression instead of statement). Allow specification of
trivia by line number, as well as insert location. Direct comment manipulation functions.

* Finish `reconcile()`, make it use all slice operations to preserve more formatting.

* Tree search, `options` validation, indentation of multiline sequences should be better, more coercion on put,
different source encodings, code cleanups, type_ignores, API additions for real-world use, optimization, testing,
bughunting, etc...

## Trivia

The "F" in FST stands for "Fun".
