"""
This is rather crude documentation that hopefully can show usage through many small examples.

`fst.docs.d01_parse`: Parse and unparse from source or `AST`

`fst.docs.d02_locations`: Node locations in the source code

`fst.docs.d03_structure`: Tree structure and node traversal

`fst.docs.d04_get`: Accessing and copying nodes

`fst.docs.d05_put`: Modifying nodes

`fst.docs.d06_raw`: Raw reparse operations

`fst.docs.d07_views`: `FST` slice indexing

`fst.docs.d08_parentheses`: Parentheses handling

`fst.docs.d09_reconcile`: Edit pure AST while preserving formatting

`fst.docs.d10_options`: Options
"""

from . import (
    d01_parse,
    d02_locations,
    d03_structure,
    d04_get,
    d05_put,
    d06_raw,
    d07_views,
    d08_parentheses,
    d09_reconcile,
    d10_options,
)

__all__ = [
    'd01_parse',
    'd02_locations',
    'd03_structure',
    'd04_get',
    'd05_put',
    'd06_raw',
    'd07_views',
    'd08_parentheses',
    'd09_reconcile',
    'd10_options',
]
