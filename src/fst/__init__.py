"""
Version {{VERSION}}

This module exists in order to facilitate quick and easy high level editing of Python source in the form of an `AST`
tree while preserving formatting. It is meant to allow you to change Python code functionality while not having to deal
with the miniutae of:

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

>>> print(fst.unparse(ext_ast))
if a: b = c, d  # comment
```

Operations are straightforward.

```py
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

`fst` works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information,
the original source, and provide the interface to format-preserving operations. Each operation through `fst` is a
simultaneous edit of the `AST` tree and the source code and those are kept synchronized so that the current source will
always parse to the current tree.

Formatting, comments, and layout are preserved unless explicitly modified. Unparsing is lossless by default and performs
no implicit normalization or stylistic rewriting.

# Index

- `fst.docs`: Documentation and examples.
- `fst.fst`: API reference.

# Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)

# Notes

Disclaimer: The intended use of this module is if you want to change code functionality without having to deal with
syntax details, not lint or format, there are better options for that. The main focus of `fst` is not necessarily to be
fast but rather to handle all the weird cases of python syntax correctly so that functional code always results, use a
formatter afterwards as needed.

`fst` was written and tested on Python versions 3.10 through 3.14.

`fst` works by keeping a copy of the entire source at the root `FST` node of a tree and modifying this source alongside
the node tree anytime an operation is performed natively.

`fst` does not do any parsing of its own but rather relies on the builtin Python parser and unparser. This means you
get perfect parsing but also that it is limited to the syntax of the running Python version (many options exist for
running any specific verison of Python).

`fst` validates for parsability, not compilability. This means that for `fst`, `*a, *b = c` and `def f(a, a): pass` are
both valid even though they are uncompilable.

If you will be playing with this module then the `FST.dump()` method will be your friend.

If you will be looking through the code then apologies in advance.
"""

import ast
from ast import *  # noqa: F403  - make everything from ast module available here (differs between py versions)

from .fst import FST, parse, unparse, dump  # noqa: F401
from .common import NodeError, astfield, fstloc  # noqa: F401
from .parsex import ParseError
from .asttypes import *  # noqa: F403  - import standins for some AST classes which may not exist in ast module and our own _slice classes

from . import asttypes

__all__ = [
    'ast', 'FST', 'NodeError', 'ParseError',
    *[n for n in dict.fromkeys(dir(ast) + asttypes.__all__) if not n.startswith('_')],
]
