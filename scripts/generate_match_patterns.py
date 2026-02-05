#!/usr/bin/env python

import sys

if sys.version_info[:2] < (3, 14):
    print('Cannot run this on Python version < 3.14!')
    sys.exit(1)

from fst.astutil import *
from fst import *
from fst.astutil import FIELDS, AST_BASES


m_patterns = []

for ast_cls in FIELDS:
    if ast_cls is Constant:
        m_patterns.append('''
class MConstant(MAST):
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
    fields = ast_cls._fields
    args = ''.join(f'\n        {f}: _Patterns = ...,' for f in fields)
    set_ = ''.join(f'\n\n        if {f} is not ...:\n            self.{f} = {f}\n            fields.append({f!r})' for f in ast_cls._fields)

    if args:
        init = f'\n\n    def __init__(\n        self,{args}\n    ) -> None:\n        self._fields = fields = []{set_}'
    else:
        init = ''

    m_patterns.append(f'''
class M{name}(MAST):
    _types = {name}{init}
'''.strip())

for ast_cls in AST_BASES:
    name = ast_cls.__name__

    m_patterns.append(f'''
class M{name}(MAST):
    _types = {name}
'''.strip())

print('\n\n'.join(m_patterns))
