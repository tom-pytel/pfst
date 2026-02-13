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

    if ast_cls is arguments:
        m_patterns.append(f'''
class Marguments(M{ast_base_name}):  # pragma: no cover
    """This works like all the other match pattern classes except that it has an extra `_strict` parameter which
    controls how it matches against individual `arguments._all`. This parameter can also be set on a normal `AST`
    `arguments` class for the same effect.

    **Parameters:**
    - `_strict`: Set this to control matching, if not set defaults to `None`.
        - `True`: `posonlyargs` only match to `posonlyargs`, `kwonlyargs` to `kwonlyargs` and `args` only to `args`.
            Their associated defaults only match to the same type of default as well.
        - `None`: Same as `True` except that `args` in the pattern matches to `args`, `posonlyargs` or `kwonlyargs` in
            the target and `defaults` likewise can also match to `kw_defaults`. This allows the use of the standard args
            to search in all the args fields.
        - `False`: All types of args and defaults can match to each other.
    """
    _types = arguments

    def __init__(
        self,
        posonlyargs: _Patterns = ...,
        args: _Patterns = ...,
        vararg: _Patterns = ...,
        kwonlyargs: _Patterns = ...,
        kw_defaults: _Patterns = ...,
        kwarg: _Patterns = ...,
        defaults: _Patterns = ...,
        _all: _Patterns = ...,
        _strict: bool | None = None,  # `True` matches pos/arg/kw exclusively to same type, `None` allos match arg to all, `False` allows match all to all
    ) -> None:
        self._fields = fields = []
        self._strict = _strict

        if posonlyargs is not ...:
            self.posonlyargs = posonlyargs
            fields.append('posonlyargs')

        if args is not ...:
            self.args = args
            fields.append('args')

        if vararg is not ...:
            self.vararg = vararg
            fields.append('vararg')

        if kwonlyargs is not ...:
            self.kwonlyargs = kwonlyargs
            fields.append('kwonlyargs')

        if kw_defaults is not ...:
            self.kw_defaults = kw_defaults
            fields.append('kw_defaults')

        if kwarg is not ...:
            self.kwarg = kwarg
            fields.append('kwarg')

        if defaults is not ...:
            self.defaults = defaults
            fields.append('defaults')

        if _all is not ...:
            self._all = _all
            fields.append('_all')
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
