"""
This is rather crude documentation that hopefully can show usage through many small examples.

`fst.docs.d01_parse`: Parse and unparse from source or `AST`

`fst.docs.d02_locations`: Node locations in the source code

`fst.docs.d03_structure`: Tree structure and node traversal

`fst.docs.d04_get`: Accessing and copying nodes

`fst.docs.d05_put`: Modifying nodes

`fst.docs.d06_slices`: Slices and trivia

`fst.docs.d07_views`: Slice views and virtual fields

`fst.docs.d08_coerce`: Coercion and slice put as `one`

`fst.docs.d09_parentheses`: Parentheses handling

`fst.docs.d10_options`: Options

`fst.docs.d11_match`: Match, search and substitute

`fst.docs.d12_raw`: Raw reparse operations

`fst.docs.d13_reconcile`: Edit pure AST while preserving formatting

`fst.docs.d14_examples`: Example recipes
"""

from . import (
    d01_parse,
    d02_locations,
    d03_structure,
    d04_get,
    d05_put,
    d06_slices,
    d07_views,
    d08_coerce,
    d09_parentheses,
    d10_options,
    d11_match,
    d12_raw,
    d13_reconcile,
    d14_examples,
)

__all__ = [
    'd01_parse',
    'd02_locations',
    'd03_structure',
    'd04_get',
    'd05_put',
    'd06_slices',
    'd07_views',
    'd08_coerce',
    'd09_parentheses',
    'd10_options',
    'd11_match',
    'd12_raw',
    'd13_reconcile',
    'd14_examples',
]


# Some helpers for maintaining the documentation readable and testable.

import sys


def pprint(src: str) -> None:
    print(src.replace('\n\n', '\n\xa0\n'))  # replace() to avoid '<BLANKLINE>'


_FILE_CACHE = {}  # {'fnm': list[str], ...}

def py_version_ok_then_exec_else_print(version: int, __file__: str, start_marker: str, stop_marker: str) -> bool:
    """If python version high enough then do nothing, otherwise print what would have been printed."""

    if sys.version_info[1] >= version:
        return True

    if (lines := _FILE_CACHE.get(__file__)) is None:
        with open(__file__) as fp:
            lines = _FILE_CACHE[__file__] = fp.readlines()

    start_marker += '\n'
    stop_marker += '\n'
    itr = iter(enumerate(lines))

    for start, line in itr:  # noqa: B007
        if line.endswith(start_marker):
            break
    else:
        raise RuntimeError(f'start marker {start_marker[:-1]} not found')

    for stop, line in itr:  # noqa: B007
        if line.endswith(stop_marker):
            break
    else:
        raise RuntimeError(f'stop marker {stop_marker[:-1]} not found')

    print(''.join(lines[start + 1 : stop])[:-1], end='')

    return False
