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
>>> import ast, fst

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

Here is an example of some more advanced usage, replace lambda functions with function definitions in one line.

```py
>>> from fst.match import *
```

```py
>>> src = """
... class cls:
...     mymin = lambda a, b: a if a < b else b
...     name = lambda self: str(self)
...
...     def method(self, a, b):
...         add = lambda: a + b
...
...         return add()
... """.strip()
```

```py
>>> pattern = MAssign([M(name=Name)], MLambda(M(args=...), M(ret=...)))
```

```py
>>> repl = """
... def __FST_name(__FST_args):
...     return __FST_ret
... """.strip()
```

```py
>>> print(FST(src).sub(pattern, repl).src)
class cls:
    def mymin(a, b):
        return a if a < b else b

    def name(self):
        return str(self)

    def method(self, a, b):
        def add():
            return a + b

        return add()
```


# vs. LibCST

There is no "vs.", [LibCST](https://github.com/Instagram/LibCST) is a powerful, industrial-grade library suitable for
the most complex complex codemods.

So where does `pfst` fit?

LibCST gives you complete control over every minute element of the source, which requires you to actually manage those
elements for anything beyond basic modifications. `pfst` takes more of a "do what I mean" rather than a "do exactly what
I say" approach. The idea is that `pfst` handles the "formatting math" so you can focus on the functional content of
the code.

A useful property of `pfst` is that it works directly with `AST` trees. This means that you can process some source with
`pfst` then pass the tree directly on to other code you may have that works with `AST` nodes. `pfst` even has a
mechanism for incorporating any changes external code may make to the tree and preserving what formatting can be
preserved, see `fst.docs.d13_reconcile`.







# Notes

Disclaimer: You can reformat a large codebase with `pfst` but it won't be quite as sprightly as other libraries more apt
to the task. The main focus of `pfst` is not necessarily to be fast but rather easy and to handle all the weird cases
of python syntax correctly so that functional code always results. Use a formatter as needed afterwards.

`pfst` was written and tested on Python versions 3.10 through 3.15a.

`pfst` works by keeping a copy of the entire source at the root `FST` node of a tree and modifying this source alongside
the node tree anytime an operation is performed natively. It is meant to be a drop-in replacement for the python `ast`
module. It provides its own versions of the `parse` and `unparse` functions as well as passing through all symbols
available from `ast`. The `parse` function returns the same `AST` tree that `ast.parse()` would return except augmented
with `pfst` metadata.

`pfst` does not do any parsing of its own but rather relies on the builtin Python parser. This means you get perfect
parsing but also that it is limited to the syntax of the running Python version (many options exist for running any
specific version of Python).

`pfst` validates for parsability, not compilability. This means that for `fst`, `*a, *b = c` and `def f(a, a): pass` are
both valid even though they are uncompilable.

The aesthetics of multiline slice operation alignment are not concretized yet. The current alignment behavior basically
just aligns, not necessarily always at the place you may want, it will get more standard and controllable in the future.

If you will be playing with this module then the `FST.dump()` method will be your friend.
'''

import ast
from ast import *  # noqa: F403  - make everything from ast module available here (differs between py versions)

from .fst import FST, parse, unparse, dump, castf, gastf  # noqa: F401
from .common import NodeError, astfield, fstloc  # noqa: F401
from .parsex import ParseError
from .code import Code  # noqa: F401
from .asttypes import *  # noqa: F403  - import standins for some AST classes which may not exist in ast module and our own _slice classes
from .match import *  # noqa: F403  - match classes for each AST class

from . import asttypes

__all__ = [
    'FST', 'NodeError', 'ParseError', 'castf', 'gastf',
    *[n for n in dict.fromkeys(dir(ast) + asttypes.__all__) if not n.startswith('_')],  # parse, unparse and dump exported here as well as all AST types (including dummies) and public functions from python ast module
]
