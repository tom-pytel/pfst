# Overview

This module exists in order to facilitate high level quick and easy editing of Python source while preserving formatting. `fst` grew out of a frustration of not being able to just edit python source to change some bit of functionality without having to deal with the miniutae of indentation, parentheses, commas, comments, docstrings, semicolons, line continuations, precedence, else vs. elif, etc... `fst` deals with all of these for you and especially the many, many niche special cases of Python syntax.

`fst` works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provide the interface to format-preserving operations. Each operation through `fst` is a simultaneous edit of the `AST` tree and the source code and those are kept synchronized so that the source always corresponds to the current tree.

Apart from its own format-preserving operations, `fst` also allows the `AST` tree to be changed by anything else outside of its control and can then reconcile the changes with what it knows to preserve formatting where possible. The degree to which formatting is preserved depends on how many operations are executed natively through `fst` mechanisms and how well `FST.reconcile()` works for those operations which are not.

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

# Examples

Format preserving parse and unparse:

```py
>>> import ast, fst

>>> a = fst.parse('if a: b = c, d  # comment')

>>> print(fst.unparse(a))
if a: b = c, d  # comment

>>> print(ast.unparse(a))
if a:
    b = (c, d)

>>> print(ast.dump(a))  # just a normal AST
Module(
  body=[
    If(
      test=Name(id='a', ctx=Load()),
      body=[
        Assign(
          targets=[
            Name(id='b', ctx=Store())],
          value=Tuple(
            elts=[
              Name(id='c', ctx=Load()),
              Name(id='d', ctx=Load())],
            ctx=Load()))])])
```

Basic operations:

```py
>>> a.f.body[0].body.append('x = b')  # '.f' accesses FST functionality
... <<If 0,0..2,9>.body[0:2] [<Assign 1,4..1,12>, <Assign 2,4..2,9>]>

>>> print(a.f.src)  # source is always available
if a:
    b = c, d  # comment
    x = b
```

```py
>>> a.body[0].body[0].value.f.elts[1:1] = 'u,\nv'  # syntax misc handled automatically

>>> print(a.f.src)
if a:
    b = (c, u,
        v, d)  # comment
    x = b
```

```py
>>> a.f.body[0].orelse = a.f.body[0].body.copy()
>>> a.f.body[0].body = 'x = a  # blah'

>>> print(a.f.src)
if a:
    x = a  # blah
else:
    b = (c, x,
        y, d)  # comment
    x = b
```

```py
>>> del a.f.body[0].orelse[0]

>>> print(a.f.src)
if a:
    x = a  # blah
else:
    x = b
```

```py
>>> print(ast.dump(a))  # AST always matches the source
Module(
  body=[
    If(
      test=Name(id='a', ctx=Load()),
      body=[
        Assign(
          targets=[
            Name(id='x', ctx=Store())],
          value=Name(id='a', ctx=Load()))],
      orelse=[
        Assign(
          targets=[
            Name(id='x', ctx=Store())],
          value=Name(id='b', ctx=Load()))])])
```

Reconcile, edit AST outside `fst` control while preserving formatting:

```py
>>> a = fst.parse('''
... def compute(x, y):
...     # Compute the weighted sum
...     result = (
...         x * 0.6  # x gets 60%
...         + y * 0.4  # y gets 40%
...     )
... '''.strip())

>>> m = a.f.mark()

>>> # pure AST manipulation
>>> a.body[0].body[0].value.left.right = Name(id='scalar1')
>>> a.body[0].body[0].value.right.right = Name(id='scalar2')

>>> print(a.f.reconcile(m).src)
def compute(x, y):
    # Compute the weighted sum
    result = (
        x * scalar1  # x gets 60%
        + y * scalar2  # y gets 40%
    )
```

```py
>>> a = fst.parse('''
... def compute(x, y):
...     # Apply thresholding
...     if (
...         result > 10  # cap high values
...     ):
...         return result
...     else:
...         return 0
... '''.strip())

>>> m = a.f.mark()

>>> a.body[0].body[-1].orelse[0] = (
...     If(test=Compare(left=Name(id='result'),
...                     ops=[Gt()],
...                     comparators=[Constant(value=1)]),
...        body=[a.body[0].body[-1].orelse[0]],
...        orelse=[Return(value=UnaryOp(op=USub(), operand=Constant(value=1)))]
...     )
... )

>>> print(a.f.reconcile(m).src)
def compute(x, y):
    # Apply thresholding
    if (
        result > 10  # cap high values
    ):
        return result
    elif result > 1:
        return 0
    else:
        return -1
```

For more examples see the documentation in `docs/`, or if you're feeling particularly masochistic have a look at the
`fst` tests in the `tests/` directory.

## TODO

This package is not finished but functional enough that it can be useful.

* Put one (non-raw) to:
  * `FormattedValue.conversion`
  * `FormattedValue.format_spec`
  * `Interpolation.str`
  * `Interpolation.conversion`
  * `Interpolation.format_spec`

* Prescribed (non-raw) get / put slice from / to:
  * `FunctionDef.decorator_list`
  * `AsyncFunctionDef.decorator_list`
  * `ClassDef.decorator_list`
  * `ClassDef.bases`
  * `BoolOp.values`
  * `Compare`
  * `comprehension.ifs`
  * `ListComp.generators`
  * `SetComp.generators`
  * `DictComp.generators`
  * `GeneratorExp.generators`
  * `ClassDef.keywords`
  * `Call.keywords`
  * `MatchClass.patterns`
  * `JoinedStr.values`
  * `TemplateStr.values`

* Improve comment handling and get/put specification and get rid of ugly trailing newlines in statement slices.

* Lots of code cleanup.


## Trivia

The "F" in FST stands for "Fun".
