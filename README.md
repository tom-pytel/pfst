# Overview

This module exists in order to facilitate quick and easy editing of Python source while preserving formatting. It automatically deals with all the silly nonsense like indentation, parentheses, commas, comments, docstrings, semicolons, line continuations, precedence, else vs. elif, etc... And especially the many, many niche special cases of Python syntax.

`fst` provides its own format-preserving operations for `AST` trees, but also allows the `AST` tree to be changed by anything else outside of its control and can then reconcile the changes with what it knows to preserve formatting where possible. It works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provide the interface to the format-preserving operations.

The fact that it just extends existing `AST` nodes means that the `AST` tree can be used (and edited) as normal anywhere that `AST` is used, and later `unparse()` with formatting preserved where it can be. The degree to which formatting is preserved depends on how many operations are executed natively through `fst` mechanisms and how well `FST.reconcile()` works for those operations which are not.

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
>>> import fst

>>> a = fst.parse('''
... if a: func()  # comment
... else:
...     i = 1  # one
...     j = 2  # two
...     k = 3  # three
... '''.strip())  # drop-in ast.parse() replacement

>>> print(dump(a)[:80])  # normal AST
Module(body=[If(test=Name(id='a', ctx=Load()), body=[Expr(value=Call(func=Name(i

>>> print(fst.unparse(a))  # drop-in ast.unparse() replacement, with formatting
if a: func()  # comment
else:
    i = 1  # one
    j = 2  # two
    k = 3  # three
```

Basic operations:

```py
>>> print(a.f.body[0].orelse[1].replace('call()  # something else').root.src)
if a: func()  # comment
else:
    i = 1  # one
    call()  # something else
    k = 3  # three

>>> print((old := a.f.body[0].orelse[1:].copy()).src)
call()  # something else
k = 3  # three

>>> a.f.body[0].put('if b:\n    pass  # noop', 'orelse')
>>> a.f.body[0].orelse[0].orelse = old

>>> print(a.f.src)
if a: func()  # comment
elif b:
    pass  # noop
else:
    call()  # something else
    k = 3  # three
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

>>> m = a.f.mark()

>>> # pure AST manipulation
>>> a.body[0].body[0].value.left.right = Name(id='scalar1')
>>> a.body[0].body[0].value.right.right = Name(id='scalar2')
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
    # Compute the weighted sum
    result = (
        x * scalar1  # x gets 60%
        + y * scalar2  # y gets 40%
    )

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
```

For more examples see the documentation in `docs/`, or if you're feeling particularly masochistic have a look at the
`fst` tests in the `tests/` directory.

## TODO

This package is not finished but functional enough that it can be useful.

* Put one (non-raw) to `FormattedValue` / `Interpolation` `conversion` and `format_spec`, `JoinedStr` / `TemplateStr` `values`.

* Prescribed (non-raw) get / put slice from / to:
  * `FunctionDef` / `AsyncFunctionDef` / `ClassDef.decorator_list`
  * `ClassDef.bases`
  * `Delete` / `Assign.targets`
  * `BoolOp.values`
  * `Call.args`
  * `comprehension.ifs`
  * `ListComp` / `SetComp` / `DictComp` / `GeneratorExp.generators`
  * `ClassDef` / `Call.keywords`
  * `Import` / `ImportFrom.names`
  * `With` / `AsyncWith.items`
  * `MatchMapping.keys` / `.patterns`
  * `MatchSequence` / `MatchClass` / `MatchOr.patterns`
  * `FunctionDef` / `AsyncFunctionDef` / `ClassDef` / `TypeAlias.type_params`
  * `Global.names` / `Nonlocal.names`
  * `JoinedStr` / `TemplateStr.values`

* Improve comment handling and get/put specification and get rid of ugly trailing newlines.

* Lots of other stuff...


## Trivia

The "F" in FST stands for "Fun".