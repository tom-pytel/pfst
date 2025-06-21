# Overview

This module exists in order to facilitate quick and easy editing of Python source while preserving formatting. It automatically deals with all the silly nonsense like indentation, parentheses, commas, comments, docstrings, semicolons, line continuations, precedence, else vs. elif, etc... And especially, the many many niche special cases of Python syntax.

`pfst` provides its own format-preserving operations for AST trees, but also allows the AST tree to be changed by anything else outside of its control and can then reconcile the changes with what it knows to preserve formatting where possible. It works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information, the original source, and provide the interface to the format-preserving operations.

The fact that it just extends existing `AST` nodes means that the AST tree can be used (and edited) as normal anywhere that AST is used, and later `unparse()`d with formatting preserved where it can be. The degree to which formatting is preserved depends on how many operations are executed natively through `pfst` mechanisms and how well `FST.reconcile()` works for operations which are not.

API documentation and examples are in the `docs/` directory.

# Install

From Github, clone then:

    pip install -e .[dev]

From PyPI:

    pip install pfst

# Examples

Format preserving parse and unparse:

```py
>>> import fst, ast

>>> a = fst.parse('''
... if 1: pass  # comment
... else:
...     i = 1  # one
...     j = 2  # two
...     k = 3  # three
... '''.strip())

>>> print(ast.dump(a))  # normal AST
Module(body=[If(test=Constant(value=1), body=[Pass()], orelse=[Assign(targets=[Name(id='i', ctx=Store())], value=Constant(value=1)), Assign(targets=[Name(id='j', ctx=Store())], value=Constant(value=2)), Assign(targets=[Name(id='k', ctx=Store())], value=Constant(value=3))])], type_ignores=[])

>>> print(fst.unparse(a))  # unparse with formatting
if 1: pass  # comment
else:
    i = 1  # one
    j = 2  # two
    k = 3  # three
```

Basic operations:

```py
>>> print(a.f.body[0].orelse[1].replace('call()  # something else').root.src)
if 1: pass  # comment
else:
    i = 1  # one
    call()  # something else
    k = 3  # three

>>> print(a.f.body[0].orelse[1:].copy().src)
call()  # something else
k = 3  # three
```

Reconcile, edit AST tree directly while preserving formatting:

```py
>>> m = a.f.mark()

>>> a.body[0].orelse[0].value = ast.Set(elts=[ast.Name(id='x')])

>>> a.body.append(ast.Assign(targets=[ast.Name(id='var')], value=ast.Constant(value=6)))

>>> print(a.f.reconcile(m).src)
if 1: pass  # comment
else:
    i = {x}  # one
    call()  # something else
    k = 3  # three
var = 6
```

For more examples the documentation in `docs/` or if you're feeling particularly masochistic, have a look at the tests
in the `tests/` directory.

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
