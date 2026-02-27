# pfst

**High-level Python AST manipulation that preserves formatting**

[![PyPI version](https://img.shields.io/badge/pypi-0.2.6-orange.svg)](https://pypi.org/project/pfst/)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14%20%7C%203.15a-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

`pfst` (Python Formatted Syntax Tree) exists in order to allow quick and easy modification of Python source without
losing formatting or comments. The goal is simple, Pythonic, container-like access to the `AST`, with the ability to
modify any node while preserving formatting in the rest of the tree.

> Yes, we said "formatting" and "AST" in the same sentence.

Normally `AST` nodes don't store any explicit formatting, much less, comments. But `pfst` works by adding `FST` nodes to
existing Python `AST` nodes as an `.f` attribute (type-safe accessor `castf()` provided). This keeps extra structure
information, the original source, and provides the interface to format-preserving operations. Each operation through
`FST` nodes is a simultaneous edit of the `AST` tree and the source code, and those are kept synchronized so that the
current source will always parse to the current tree.

`pfst` automatically handles:

- Operator precedence and parentheses
- Indentation and line continuations
- Commas, semicolons, and tuple edge cases
- Comments and docstrings
- Various Python version-specific syntax quirks
- Lots more...

See [Example Recipes](https://tom-pytel.github.io/pfst/fst/docs/d13_examples.html) for more in-depth examples. Or go straight to the [Documentation](https://tom-pytel.github.io/pfst/fst.html).


## Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)


## Install

From PyPI:

    pip install pfst

From GitHub using pip:

    pip install git+https://github.com/tom-pytel/pfst.git

From GitHub, after cloning for development:

    pip install -e .[dev]


## Getting Started

Since `pfst` is built directly on Python's standard `AST` nodes, if you are familiar with those then you already know
the `FST` node structure. Our focus on simple Pythonic operations means you can get up to speed quickly.

1. Parse source

```py
>>> import ast, fst  # pip install pfst, import fst

>>> a = fst.parse('def func(): pass  # comment')
```

2. Modify via `.f`

```py
>>> f = a.body[0].f

>>> f.returns = ast.Name('int')  # use nodes or text
>>> f.args.append('arg: int = 0')
>>> f.body.extend('call()  # call comment\n\nreturn arg')
>>> f.put_docstr("I'm a happy\nlittle docstring")
>>> f.body[1:1] = '\n'
```

3. View formatted source

```py
>>> print(f.src)
def func(arg: int = 0) -> int:
    """I'm a happy
    little docstring"""

    pass  # comment
    call()  # call comment

    return arg
```

4. Verify AST synchronization

```py
>>> print(ast.unparse(a))
def func(arg: int=0) -> int:
    """I'm a happy
    little docstring"""
    pass
    call()
    return arg
```

Beyond basic editing, `pfst` provides syntax-ordered traversal, scope symbol analysis, structural pattern matching and
substitution, and a mechanism for reconciling external `AST` mutations with the formatted tree, preserving comments and
layout wherever the structure still permits it.


### TODO

- Prescribed get / put slice from / to:
  - `MatchClass.patterns+kwd_attrs:kwd_patterns` with `_pattern_args` special slice container class
  - `JoinedStr.values`
  - `TemplateStr.values`

- Put one to:
  - `FormattedValue.conversion`
  - `FormattedValue.format_spec`
  - `Interpolation.str`
  - `Interpolation.conversion`
  - `Interpolation.format_spec`

- Maybe allow non-slice individual expressionlike nodes to own comments (as opposed to only individual statementlikes
and expressionlike slices), allowing them to be copied and put with these nodes. More direct comment manipulation
functions.

- The aesthetics of multiline slice operation alignment are not concretized yet. The current alignment behavior
basically just aligns, not necessarily always at the expected place. It should get more standard and controllable in the
future.

- Finish `reconcile()`. Proper comment handling, locations and deduplication. Make it use all slice operations to
preserve more formatting.

- Clean up typing, other code cleanups, API additions for real-world use, optimization, testing, bughunting, etc...


### Trivia

The "F" in FST stands for "Fun".
