# Overview

This module exists in order to facilitate quick and easy high level editing of Python source in the form of an `AST` tree while preserving formatting. It is meant to allow you to change Python code functionality while not having to deal with the minutiae of:

- Operator precedence and parentheses
- Indentation and line continuations
- Commas, semicolons, and tuple edge cases
- Comments and docstrings
- Various Python version–specific syntax quirks
- Lots more...

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

Formatting, comments, and layout are preserved unless explicitly modified. Unparsing is lossless by default and performs no implicit normalization or stylistic rewriting.

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
>>> print(else_if_chain_to_elifs("""
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

# Reconcile

This is intended to allow something which is not aware of `fst` to edit the `AST` tree while `fst` preserves formatting
where it can.

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

# Robustness

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
...     def func(): weird\
...  ; \
... \
... stuff()
...
...     pass
... '''.strip())
```

```py
>>> deco = f.body[0].get_slice(1, 2, 'decorator_list', cut=True, trivia=('all+', 'all+'))
```

```py
>>> deco.dump('stmt+')
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

    def func(): weird\
 ; \
\
stuff()

    pass
```

```py
>>> f.body[0].put_slice(deco, 'decorator_list', trivia=('all+', 'all+'))

>>> f.body[0].body[0] = 'good'
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

    def func():
        good
        stuff()

    pass
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

* Finish `reconcile()`. Proper comment handling, locations and deduplication. Make it use all slice operations to
preserve more formatting.

* Tree search, indentation of multiline sequences should be better, more coercion on put, different source encodings,
code cleanups, API additions for real-world use, optimization, testing, bughunting, etc...

## Trivia

The "F" in FST stands for "Fun".
