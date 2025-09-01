"""
Version {{VERSION}}

# Overview

This module exists in order to facilitate quick and easy editing of Python source while preserving formatting. It
automatically deals with all the silly nonsense like indentation, parentheses, commas, comments, docstrings, semicolons,
line continuations, precedence, else vs. elif, etc... And especially the many, many niche special cases of Python
syntax.

`fst` provides its own format-preserving operations for `AST` trees, but also allows the `AST` tree to be changed by
anything else outside of its control and can then reconcile the changes with what it knows to preserve formatting where
possible. It works by adding `FST` nodes to existing `AST` nodes as an `.f` attribute which keep extra structure
information, the original source, and provide the interface to the format-preserving operations.

The fact that it just extends existing `AST` nodes means that the `AST` tree can be used (and edited) as normal anywhere
that `AST` is used, and later `unparse()` with formatting preserved where it can be. The degree to which formatting is
preserved depends on how many operations are executed natively through `fst` mechanisms and how well `FST.reconcile()`
works for those operations which are not.

# Index

- `fst.docs`: Documentation and examples.
- `fst.fst`: API reference.

# Links

- [Repository](https://github.com/tom-pytel/pfst)
- [Documentation](https://tom-pytel.github.io/pfst/)
- [PyPI](https://pypi.org/project/pfst/)

# Details

Disclaimer: The intended use of this module is if you just want to change code functionality without having to deal with
miniutae, not lint or format, there are better options for that.

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

Format preserving native operations exist in two flavors (see the documentation on how to use either):

* Prescribed put operations which do specific things for each type of node being put, including precedence and syntax
parenthesization. `fst.docs.d05_put`.

* Raw mode put operations which just put the raw source you want to replace and then attempt to reparse a small part of
the full source around the changes (at least statement level). `fst.docs.d06_raw`, `fst.fst.FST.put_src()`.

There is also a mechanism for allowing outside editing of the `AST` tree and then reconciling with a marked snapshot
to preserve formatting where possible. This is intended for existing code or third-party libraries which don't know
anything about `fst` to maybe gain the ability to preserve some existing formatting when editing a tree.
`fst.docs.d09_reconcile`.
"""

import ast  # noqa: F401
from ast import *  # noqa: F403
from .fst import parse, unparse, dump, FST  # noqa: F401
from .misc import NodeError  # noqa: F401
from .extparse import ParseError  # noqa: F401
from .asttypes import *  # noqa: F403
