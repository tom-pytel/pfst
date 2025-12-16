#!/usr/bin/env python

from fst import *
from fst.astutil import *
from fst.astutil import FIELDS, AST_FIELDS


def make_AST_field_accessors() -> None:
    def make_AST_field_accessor(field: str, cardinality: int, astorprim: int):
        ast_names = [ac.__name__ for ac, fs in FIELDS.items() for f, _ in fs if f == field]

        print(f'\n\n# {", ".join(ast_names)}')

        if cardinality == 1:  # single required AST or a primitive
            if astorprim == 1:  # only AST
                print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """@private"""

    return self.a.{field}.f
'''.strip())
            elif astorprim == 2:  # only primitive
                print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """@private"""

    return self.a.{field}
'''.strip())
            else:  # astorprim == 3:  # AST OR primitive
                raise NotImplementedError  # currently this doesn't happen but we want to catch if it does

            print(f'''
@{field}.setter
def {field}(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, {field!r})

@{field}.deleter
def {field}(self: 'fst.FST') -> None:
    self._put_one(None, None, {field!r})
'''.rstrip())

        elif cardinality == 5:  # optional AST or primitive
            if astorprim == 1:  # only AST
                if field == 'default_value':  # SPECIAL CASE!!!
                    print(f'''
if PYGE13:
    @property
    def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
        """@private"""

        return child.f if (child := self.a.{field}) else None
else:  # HACK to safely return nonexistent field
    @property
    def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
        """@private"""

        return None
'''.strip())
                else:
                    print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """@private"""

    return child.f if (child := self.a.{field}) else None
'''.strip())

            elif astorprim == 2:  # primitive only
                print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """@private"""

    return self.a.{field}
'''.strip())
            elif astorprim == 3:  # AST or primitive
                print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """@private"""

    return child.f if isinstance(child := self.a.{field}, AST) else child
'''.strip())

            print(f'''
@{field}.setter
def {field}(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, {field!r})

@{field}.deleter
def {field}(self: 'fst.FST') -> None:
    self._put_one(None, None, {field!r})
'''.rstrip())

        elif cardinality == 2:  # is a list[AST] or list[primitive]
            if field == 'type_params':  # SPECIAL CASE!!!
                print(f'''
if PYGE12:
    @property
    def {field}(self: 'fst.FST') -> fstview:
        """@private"""

        return fstview(self, {field!r})
else:  # HACK to safely access nonexistent empty field
    @property
    def {field}(self: 'fst.FST') -> list:
        """@private"""

        return []
'''.strip())
            else:
                print(f'''
@property
def {field}(self: 'fst.FST') -> fstview:
    """@private"""

    return fstview(self, {field!r})
'''.strip())

            print(f'''
@{field}.setter
def {field}(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, None, None, {field!r})

@{field}.deleter
def {field}(self: 'fst.FST') -> None:
    self._put_slice(None, None, None, {field!r})
'''.rstrip())

        elif cardinality == 3:  # single AST or list[AST]
            assert astorprim == 1  # only AST

            print(f'''
@property
def {field}(self: 'fst.FST') -> fstview | Union['fst.FST', None, constant]:
    """@private"""

    if isinstance(child := self.a.{field}, list):
        return fstview(self, {field!r}, 0, len(child))
    elif isinstance(child, AST):
        return getattr(child, 'f', None)

    return child

@{field}.setter
def {field}(self: 'fst.FST', code: Code | None) -> None:
    if isinstance(self.a.{field}, list):
        self._put_slice(code, None, None, {field!r})
    else:
        self._put_one(code, None, {field!r})

@{field}.deleter
def {field}(self: 'fst.FST') -> None:
    if isinstance(self.a.{field}, list):
        self._put_slice(None, None, None, {field!r})
    else:
        self._put_one(None, None, {field!r})
'''.strip())

        else:  # some other cardinality mix
            raise NotImplementedError  # currently this doesn't happen but we want to catch if it does

    print(r'''
"""`FST` class accessors for underlying `AST` node fields.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from typing import Union

from . import fst

from .asttypes import AST
from .astutil import constant
from .common import PYGE12, PYGE13
from .code import Code
from .view import fstview
'''.strip())

    cardinality = {}  # {'field': 1 means single element | 2 means list (3 means can be either) | 4 if is optional (for single), ...}
    astorprim = {}  # {'field': 1 means AST | 2 means primitive (3 means can be either)}
    all = []

    for ast_cls, fields in FIELDS.items():
        for field, type_ in fields:
            if field == 'lineno':  # TypeIgnore.lineno
                continue

            cardinality[field] = cardinality.get(field, 0) | (2 if type_.endswith('*') else 5 if type_.endswith('?') else 1)
            astorprim[field] = astorprim.get(field, 0) | (1 if field in AST_FIELDS[ast_cls] else 2)

    print('\n__all__ = [')
    print('\n'.join(f'    {field!r},' for field in cardinality))
    print(']')

    for field in cardinality:
        make_AST_field_accessor(field, cardinality[field], astorprim[field])

        all.append(field)


if __name__ == '__main__':
    make_AST_field_accessors()
