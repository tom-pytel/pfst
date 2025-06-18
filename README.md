# Overview

This module exists in order to facilitate quick and easy editing of Python source while preserving formatting. It automatically deals with all the silly nonsense like indentation, parentheses, commas, comments, docstrings, semicolons, line continuations, precedence, decorator @ signs, else vs. elif and lots and lots of the niche special cases of Python syntax.

`pfst` provides its own format-preserving operations for AST trees, but also allows the AST tree to be changed by anything else outside of its control and can then reconcile the changes with what it knows to preserve formatting where possible. It works by adding FST nodes to existing AST nodes as an `.f` attribute which keep extra structure information, the original source, and provides the interface to the source-preserving operations.

The fact that it just extends existing AST nodes means that the AST tree can be used (and edited) as normal anywhere that AST is used, and later `unparse()`d with formatting preserved where it can be. The degree to which formatting is preserved depends on how many operations are executed natively through `pfst` mechanisms and how well `FST.reconcile()` works for operations which are not.

API documentation is in the `docs/` directory.

Lots of examples are in the `examples/` directory.

# Install

From Github, clone, then make appropriate virtual environment, then in the top directory with the `Makefile`:

    make install

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

>>> print(fst.unparse(a))  # unparse with formatting
if 1: pass  # comment
else:
    i = 1  # one
    j = 2  # two
    k = 3  # three

>>> print(ast.unparse(a))  # is normal AST
if 1:
    pass
else:
    i = 1
    j = 2
    k = 3
```

The FST part:

```py
>>> a.f
<Module ROOT 0,0..4,9>

>>> a.f.dump()
Module - ROOT 0,0..4,9
  .body[1]
  0] If - 0,0..4,9
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Pass - 0,6..0,10
    .orelse[3]
    0] Assign - 2,4..2,9
      .targets[1]
      0] Name 'i' Store - 2,4..2,5
      .value Constant 1 - 2,8..2,9
    1] Assign - 3,4..3,9
      .targets[1]
      0] Name 'j' Store - 3,4..3,5
      .value Constant 2 - 3,8..3,9
    2] Assign - 4,4..4,9
      .targets[1]
      0] Name 'k' Store - 4,4..4,5
      .value Constant 3 - 4,8..4,9

>>> a.body[0].orelse[2].targets[0].f
<Name 4,4..4,5>
```

Basic operations:

```py
>>> a.f.body[0].orelse[1].replace('call()  # something else')
<Expr 3,4..3,10>

>>> print(a.f.src)
if 1: pass  # comment
else:
    i = 1  # one
    call()  # something else
    k = 3  # three

>>> print(a.f.body[0].get_slice(1, 3, 'orelse').src)
call()  # something else
k = 3  # three
```

Edit AST while preserving format:

```py
>>> from ast import *
>>> m = a.f.mark()
>>> a.body.append(Assign(targets=[Name(id='var')], value=Constant(value=6)))
>>> a.body[0].orelse[0].value = Set(elts=[Name(id='x')])
>>> f = a.f.reconcile(m)
>>> print(f.src)
if 1: pass  # comment
else:
    i = {x}  # one
    call()  # something else
    k = 3  # three
var = 6

>>> print(ast.unparse(f.a))
if 1:
    pass
else:
    i = {x}
    call()
    k = 3
var = 6
```

For more examples see the `examples/` directory, the API documentation has examples for most functions in `docs/` or
have a look at the tests in the `tests/` directory.

# More detail

`pfst` was written and tested on Python versions 3.10 through 3.14.

`pfst` does not do any parsing of its own but rather relies on the builtin Python parser and unparser. This means you get perfect parsing but also that it is limited to the syntax of the running Python version, but many options exist for running any specific verion of Python. `pfst` does use standard Python parsing to parse things that can not normally be parsed, like individual exception handlers or match cases by wrapping them in corresponding code then pulling out and adjusting the locations of the parsed `AST`s.

`pfst` does basic validation but will not prevent you from burning yourself if you really want to. For example, it won't let you add a `Slice` to a `Tuple` which is not at the top level or already in a `Subscript.slice` field, but you can take a `Tuple` with a `Slice` in it already and put it somewhere else where it doesn't belong.

Format preserving operations exist in two flavors (see the examples how to use either):
  * Prescribed put operations which do specific things for each type of node being put, including precedence and syntax
  parenthesization.
  * Raw mode put operations which just put the raw source you want to replace and then attempt to reparse a small part of the full source around the changes (at least statement level).

## TODO

This package is not finished but functional enough that it can be useful. Once full slice support is done for everything should improve much, especially `reconcile()`.

* Put one to `FormattedValue` / `Interpolation` `conversion` and `format_spec`, `JoinedStr` / `TemplateStr` `values`.

* Prescribed (non-raw) get / put slice from / to:
  * `FunctionDef.decorator_list`
  * `AsyncFunctionDef.decorator_list`
  * `ClassDef.decorator_list`
  * `ClassDef.bases`
  * `Delete.targets`
  * `Assign.targets`
  * `BoolOp.values`
  * `Call.args`
  * `comprehension.ifs`
  * `ListComp.generators`
  * `SetComp.generators`
  * `DictComp.generators`
  * `GeneratorExp.generators`
  * `ClassDef.keywords`
  * `Call.keywords`
  * `Import.names`
  * `ImportFrom.names`
  * `With.items`
  * `AsyncWith.items`
  * `MatchSequence.patterns`
  * `MatchMapping.patterns`
  * `MatchClass.patterns`
  * `MatchOr.patterns`
  * `FunctionDef.type_params`
  * `AsyncFunctionDef.type_params`
  * `ClassDef.type_params`
  * `TypeAlias.type_params`
  * `Global.names`
  * `Nonlocal.names`
  * `JoinedStr.values`
  * `TemplateStr.values`

* Redo comment handling, where to `put()` wrt comments, interface for modifying just those.

* Fix trailing newlines in statement slices. They were originally intentional but are too ugly.

* Lots of other stuff...


## Trivia

The "F" in FST stands for "Fun".
