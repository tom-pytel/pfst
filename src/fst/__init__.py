r"""
Version {{VERSION}}

# Overview

This module exists in order to facilitate quick and easy high level editing of Python source in the form of an `AST`
tree while preserving formatting. It is meant to allow you to change Python code functionality while not having to deal
with the details of:

- Operator precedence and parentheses
- Indentation and line continuations
- Commas, semicolons, and tuple edge cases
- Comments and docstrings
- Various Python version-specific syntax quirks
- Lots more...

See [Example Recipes](https://tom-pytel.github.io/pfst/fst/docs/d12_examples.html) for more in-depth examples.

```py
>>> import fst  # pip install pfst, import fst

>>> ext_ast = fst.parse('''
... logger.info(  # just checking
...     f'not a {thing}', extra=extra,  # blah
... )'''.strip())

>>> ext_ast.f.body[0].value.insert('\nid=CID  # comment', -1, trivia=(False, False))

>>> print(fst.unparse(ext_ast))
logger.info(  # just checking
    f'not a {thing}',
    id=CID,  # comment
    extra=extra,  # blah
)
```

The tree is just normal `AST` with metadata, so if you know `AST`, you know `FST`.

```py
>>> import ast

>>> print(ast.unparse(ext_ast))
logger.info(f'not a {thing}', id=CID, extra=extra)
```

`fst` works by adding `FST` nodes to existing standard Python `AST` nodes as an `.f` attribute (type-safe accessor
`castf()` provided) which keep extra structure information, the original source, and provide the interface to
format-preserving operations. Each operation through `fst` is a simultaneous edit of the `AST` tree and the source code
and those are kept synchronized so that the current source will always parse to the current tree.

# Index

- `fst.docs`: Documentation and examples.
- `fst.fst`: API reference.

# Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)

# Notes

Disclaimer: You can reformat a large codebase with `fst` but it won't be quite as spritely as other libraries more apt
to the task. The main focus of `fst` is not necessarily to be fast but rather easy and to handle all the weird cases
of python syntax correctly so that functional code always results. Use a formatter as needed afterwards.

`fst` was written and tested on Python versions 3.10 through 3.14.

`fst` works by keeping a copy of the entire source at the root `FST` node of a tree and modifying this source alongside
the node tree anytime an operation is performed natively. It is meant to be a drop-in replacement for the python `ast`
module. It provices its own versions of the `parse` and `unparse` functions as well as passing through all symbols
available from `ast`. The `parse` function returns the same `AST` tree that `ast.parse()` would return except augmented
with `fst` metadata.

`fst` does not do any parsing of its own but rather relies on the builtin Python parser. This means you get perfect
parsing but also that it is limited to the syntax of the running Python version (many options exist for running any
specific verison of Python).

`fst` validates for parsability, not compilability. This means that for `fst`, `*a, *b = c` and `def f(a, a): pass` are
both valid even though they are uncompilable.

The aesthetics of multiline slice operation alignment are not concretized yet. The current alignment behavior basically
just aligns, not necessarily always at the place you may want, it will get more standard and controllable in the future.

If you will be playing with this module then the `FST.dump()` method will be your friend.

If you will be looking through the code then apologies in advance.
"""

import ast
from ast import *  # noqa: F403  - make everything from ast module available here (differs between py versions)

from .fst import FST, parse, unparse, dump, castf, gastf  # noqa: F401
from .common import NodeError, astfield, fstloc  # noqa: F401
from .parsex import ParseError
from .asttypes import *  # noqa: F403  - import standins for some AST classes which may not exist in ast module and our own _slice classes

from . import asttypes

__all__ = [
    'FST', 'NodeError', 'ParseError', 'castf', 'gastf',
    *[n for n in dict.fromkeys(dir(ast) + asttypes.__all__) if not n.startswith('_')],  # parse, unparse and dump exported here
]
