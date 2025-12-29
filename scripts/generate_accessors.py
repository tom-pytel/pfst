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
    """`FST` accessor for `AST` field `{field}`."""

    return self.a.{field}.f
'''.strip())
            elif astorprim == 2:  # only primitive
                print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `{field}`."""

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
            if field == 'default_value':  # SPECIAL CASE!!!
                print(f'''
if PYGE13:
    @property
    def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
        """`FST` accessor for `AST` field `{field}`."""

        return child.f if (child := self.a.{field}) else None

    @{field}.setter
    def {field}(self: 'fst.FST', code: Code | constant | None) -> None:
        self._put_one(code, None, {field!r})

    @{field}.deleter
    def {field}(self: 'fst.FST') -> None:
        self._put_one(None, None, {field!r})

else:  # safely access nonexistent field
    @property
    def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
        """`FST` accessor for `AST` field `{field}`."""

        return None

    @{field}.setter
    def {field}(self: 'fst.FST', code: Code | constant | None) -> None:
        if code is not None:  # maybe fail successfully
            raise RuntimeError("field 'default_value' does not exist on python < 3.13")

    @{field}.deleter
    def {field}(self: 'fst.FST') -> None:
        pass
'''.strip())

            elif astorprim == 1:  # only AST
                print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `{field}`."""

    return child.f if (child := self.a.{field}) else None
'''.strip())

            elif astorprim == 2:  # primitive only
                print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `{field}`."""

    return self.a.{field}
'''.strip())
            elif astorprim == 3:  # AST or primitive
                print(f'''
@property
def {field}(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `{field}`."""

    return child.f if isinstance(child := self.a.{field}, AST) else child
'''.strip())

            if field != 'default_value':  # if not printed in SPECIAL CASE!!!
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
        """`FST` accessor for `AST` field `{field}`."""

        self.a.{field}  # noqa: B018

        return fstview(self, {field!r})

    @{field}.setter
    def {field}(self: 'fst.FST', code: Code | None) -> None:
        self._put_slice(code, 0, 'end', {field!r})

    @{field}.deleter
    def {field}(self: 'fst.FST') -> None:
        self._put_slice(None, 0, 'end', {field!r})

else:  # safely access nonexistent empty field
    @property
    def {field}(self: 'fst.FST') -> list:
        """`FST` accessor for `AST` field `{field}`."""

        if self.a.__class__ in (FunctionDef, AsyncFunctionDef, ClassDef, TypeAlias):
            return fstview_dummy(self, '{field}')

        self.a.{field}  # noqa: B018, AttributeError

    @{field}.setter
    def {field}(self: 'fst.FST', code: Code | None) -> None:
        if code is not None:  # maybe fail successfully
            raise RuntimeError("field '{field}' does not exist on python < 3.12")

    @{field}.deleter
    def {field}(self: 'fst.FST') -> None:
        pass
'''.strip())
            else:
                print(f'''
@property
def {field}(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `{field}`."""

    self.a.{field}  # noqa: B018

    return fstview(self, {field!r})

@{field}.setter
def {field}(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', {field!r})

@{field}.deleter
def {field}(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', {field!r})
'''.strip())

        elif cardinality == 3:  # single AST or list[AST]
            assert astorprim == 1  # only AST

            print(f'''
@property
def {field}(self: 'fst.FST') -> fstview | Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `{field}`."""

    if isinstance(child := self.a.{field}, list):
        return fstview(self, {field!r})

    return child.f

@{field}.setter
def {field}(self: 'fst.FST', code: Code | None) -> None:
    if isinstance(self.a.{field}, list):
        self._put_slice(code, 0, 'end', {field!r})
    else:
        self._put_one(code, None, {field!r})

@{field}.deleter
def {field}(self: 'fst.FST') -> None:
    if isinstance(self.a.{field}, list):
        self._put_slice(None, 0, 'end', {field!r})
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

from .asttypes import AST, FunctionDef, AsyncFunctionDef, ClassDef, TypeAlias
from .astutil import constant
from .common import PYGE12, PYGE13
from .code import Code
from .view import fstview, fstview_dummy
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
