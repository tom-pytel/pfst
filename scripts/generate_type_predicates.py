#!/usr/bin/env python

from fst import *
from fst.astutil import *
from fst.astutil import AST_FIELDS  # , AST_BASES


LEAF_AND_BASE = list(AST_FIELDS)  # + list(AST_BASES)


def make_predicates() -> None:
    type_imports = '\n'.join(f'    {ast_cls.__name__},' for ast_cls in LEAF_AND_BASE)

    print(f'''
"""`FST` class predicates for checking underlying `AST` node type.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from . import fst

from .asttypes import (
{type_imports}
)
'''.strip())

    print('\n__all__ = [')
    print('\n'.join(f"    'is_{ast_cls.__name__}'," for ast_cls in LEAF_AND_BASE))
    print(']')

    for ast_cls in AST_FIELDS:
        name = ast_cls.__name__
        func_name = f'is_{name}'

        # if not hasattr(FST, name):  # in case explicitly overridden
        print(f'''\n
@property
def {func_name}(self: 'fst.FST') -> bool:
    """@private"""

    return self.a.__class__ is {name}
'''.rstrip())
        name = f'is_{ast_cls.__name__}'

#     for ast_cls in AST_BASES:
#         name = ast_cls.__name__
#         func_name = f'is_{name}'

#         if not hasattr(FST, func_name):  # things like is_stmt() already exist
#             print(f'''\n
# @property
# def {func_name}(self: 'fst.FST') -> bool:
#     """Is a `{name}` node."""

#     return isinstance(self.a, {name})
# '''.rstrip())


if __name__ == '__main__':
    make_predicates()
