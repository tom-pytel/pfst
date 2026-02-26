r'''
Version {{VERSION}}


# Introduction

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

If you just want to dive into the examples then go to `fst.docs.d14_examples`.


# Index

- `fst.docs`: Documentation and examples.
- `fst.fst`: API reference.


# Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)


# Getting Started

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


# Comparison with LibCST

[LibCST](https://github.com/Instagram/LibCST) is a powerful, industrial-grade library built for precise, large-scale
codemods. It models Python as a fully concrete syntax tree, preserving every token and piece of whitespace. That gives
you complete control, but it also means you are responsible for managing formatting details when making non-trivial
changes.

`pfst` takes a different approach. Instead of requiring you to explicitly manage formatting, it treats layout as
something to preserve and reconcile automatically. You focus on structural and semantic transformations and `pfst`
handles the "formatting math" needed to keep the result clean and stable.

In short:
- LibCST: “Do exactly what I say.”
- pfst: “Do what I mean.”


# Notes

- Disclaimer: You can reformat a large codebase with `pfst` but it won't be quite as sprightly as other libraries more apt
to the task. The main focus of `pfst` is not necessarily to be fast but rather easy and to handle all the weird cases
of python syntax correctly so that functional code always results. Use a formatter as needed afterwards.

- `pfst` was written and tested on Python versions 3.10 through 3.15a.

- `pfst` does not do any parsing of its own but rather relies on the builtin Python parser. This means you get perfect
parsing but also that it is limited to the syntax of the running Python version (many options exist for running any
specific version of Python).

- `pfst` validates for parsability, not compilability. This means that `*a, *b = c` and `def f(a, a): pass` are both
considered valid even though they are uncompilable.

- The aesthetics of multiline slice operation alignment are not concretized yet. The current alignment behavior basically
just aligns, not necessarily always at the place you may want, it will get more standard and controllable in the future.

- If you will be playing with this module then the `FST.dump()` method will be your friend.
'''

import ast
from ast import *  # noqa: F403  - make everything from ast module available here (differs between py versions)

from .fst import FST, parse, unparse, dump, castf, gastf  # noqa: F401
from .common import NodeError, astfield, fstloc  # noqa: F401
from .parsex import ParseError
from .code import Code  # noqa: F401
from .match import MatchError
from .asttypes import *  # noqa: F403  - import standins for some AST classes which may not exist in ast module and our own _slice classes
from .match import *  # noqa: F403  - match classes for each AST class

from . import asttypes

__all__ = [
    'FST', 'NodeError', 'ParseError', 'MatchError', 'castf', 'gastf',
    *[n for n in dict.fromkeys(dir(ast) + asttypes.__all__) if not n.startswith('_')],  # parse, unparse and dump exported here as well as all AST types (including dummies) and public functions from python ast module
]
