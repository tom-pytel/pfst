#!/usr/bin/env python

import sys

if sys.version_info[:2] < (3, 14):
    print('Cannot run this on Python version < 3.14!')
    sys.exit(1)

from fst.astutil import *
from fst import *
from fst.astutil import FIELDS, AST_BASES
from fst.fst_misc import FST_VIRTUAL_FIELDS


m_patterns = []

for ast_cls in AST_BASES:
    assert len(ast_cls.__bases__) == 1

    ast_base_name = ast_cls.__bases__[0].__name__
    name = ast_cls.__name__

    m_patterns.append(f'''
class M{name}(M{ast_base_name}):  # pragma: no cover
    """"""
    _types = {name}
'''.strip())

for ast_cls in FIELDS:
    assert len(ast_cls.__bases__) == 1

    ast_base_name = ast_cls.__bases__[0].__name__

    if ast_cls is Constant:
        m_patterns.append(f'''
class MConstant(M{ast_base_name}):  # pragma: no cover
    """"""
    _types = Constant

    def __init__(
        self,
        value: _Patterns,  # Ellipsis here is not a wildcard but a concrete value to match
        kind: _Patterns = ...,
    ) -> None:
        self._fields = fields = ['value']
        self.value = value

        if kind is not ...:
            self.kind = kind
            fields.append('kind')
'''.strip())

        continue

    name = ast_cls.__name__
    fields = ast_cls._fields + FST_VIRTUAL_FIELDS.get(ast_cls, ())
    args = ''.join(f'\n        {f}: _Patterns = ...,' for f in fields)
    set_ = ''.join(f'\n\n        if {f} is not ...:\n            self.{f} = {f}\n            fields.append({f!r})' for f in fields)

    if args:
        init = f'\n\n    def __init__(\n        self,{args}\n    ) -> None:\n        self._fields = fields = []{set_}'
    else:
        init = '\n\n    def __init__(self) -> None:\n        pass'

    m_patterns.append(f'''
class M{name}(M{ast_base_name}):  # pragma: no cover
    """"""
    _types = {name}{init}
'''.strip())

print('\n\n'.join(m_patterns))

    # match = M_Pattern.match  ; """@private"""
