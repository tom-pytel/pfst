"""
Version {{VERSION}}

# Overview

This module exists in order to facilitate quick and easy high level editing of Python source in the form of an `AST`
tree while preserving formatting. It is meant to allow you to change python code functionality while not having to deal
with the miniutae of precedence, indentation, parentheses, commas, comments, docstrings, semicolons, line continuations,
else vs. elif, and all the various other niche special cases of Python syntax across different versions of the language.

See [Example Recipes](https://tom-pytel.github.io/pfst/fst/docs/d12_examples.html) for more in-depth examples.

Example:

>>> import fst

>>> ext_ast = fst.parse('if a: b = c, d  # comment')

>>> print(fst.unparse(ext_ast))  # formatting is preserved
if a: b = c, d  # comment

Straightforward operations.

>>> ext_ast.f.body[0].body[0].value.elts[1:1] = 'u,\nv  # blah'

>>> print(fst.unparse(ext_ast))
if a: b = (c, u,
          v,  # blah
          d)  # comment

The tree is just normal `AST` with metadata.

>>> import ast

>>> print(ast.unparse(ext_ast))
if a:
    b = (c, u, v, d)

`fst` works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure information,
the original source, and provide the interface to format-preserving operations. Each operation through `fst` is a
simultaneous edit of the `AST` tree and the source code and those are kept synchronized so that the current source will
always parse to the current tree.

# Index

- `fst.docs`: Documentation and examples.
- `fst.fst`: API reference.

# Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)

# Notes

`fst` was written and tested on Python versions 3.10 through 3.14.

`fst` works by keeping a copy of the entire source at the root `FST` node of a tree and modifying this source alongside
the node tree anytime an operation is performed natively.

`fst` does not do any parsing of its own but rather relies on the builtin Python parser and unparser. This means you
get perfect parsing but also that it is limited to the syntax of the running Python version (many options exist for
running any specific verison of Python).

`fst` does use standard Python parsing to parse things that can not normally be parsed, like individual exception
handlers or match cases, by wrapping them in corresponding code then pulling out and adjusting the locations of the
parsed `AST`s. `fst.docs.d01_parse`.

`fst` validates for parsability, not compilability. This means that for `fst`, `*a, *b = c` and `def f(a, a): pass` are
both valid even though they are uncompilable.

Format preserving native modification operations exist in two flavors (see the documentation on how to use either):

- Prescribed put operations which do specific things for each type of node being put, including indentation, precedence
and syntax parenthesization, etc... `fst.docs.d05_put`.

- Raw mode put operations which just put the raw source you want to replace and then attempt to reparse a small part of
the full source around the changes (at least statement level). `fst.docs.d07_raw`, `fst.fst.FST.put_src()`.

There is also a mechanism for allowing outside editing of the `AST` tree and then reconciling with a marked snapshot
to preserve formatting where possible. This is intended for existing code or third-party libraries which don't know
anything about `fst` to maybe gain the ability to preserve some existing formatting when editing a tree.
`fst.docs.d10_reconcile`.

If you will be playing with this module then the `FST.dump()` method will be your friend.

Disclaimer: The intended use of this module is if you want to change code functionality without having to deal with
syntax details, not lint or format, there are better options for that. The main focus of `fst` is not necessarily to be
fast but rather to handle all the weird cases of python syntax correctly so that functional code always results, use a
formatter afterwards as needed.
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
