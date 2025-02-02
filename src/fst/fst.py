__all_other__ = None
__all_other__ = set(globals())
from ast import *
__all_other__ = set(globals()) - __all_other__

import ast
from typing import Optional

from .util import *

__all__ = list(__all_other__ | {
    'FST', 'parse', 'unparse',
})


class FST:
    ast:    AST
    parent: Optional['FST']
    pfield: astfield | None
    root:   'FST'
    _lines: list[aststr] | None

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def lines(self) -> list[str]:
        if self.is_root:
            return self._lines

        raise NotImplementedError  # TODO: snip and return those lines

    @property
    def str(self) -> str:
        if self.is_root:
            return '\n'.join(self._lines)

        raise NotImplementedError  # TODO: snip and return that src

    def _make_ftree(self):
        "Create tree of FST nodes for each AST node from root. Call only on root."

        stack = [self]

        while stack:
            fnode = stack.pop()
            anode = fnode.ast

            for field in anode._fields:
                if isinstance(child := getattr(anode, field, None), list):
                    stack.extend(FST(anode, fnode, astfield(field, idx))
                                 for idx, anode in enumerate(child) if isinstance(anode, ast.AST))
                elif isinstance(child, ast.AST):
                    stack.append(FST(child, fnode, astfield(field)))

    def __repr__(self):
        return ('<FST root ' if self.is_root else '<FST ') + repr(self.ast)[1:]

    def __init__(self, anode: AST, parent: Optional['FST'] = None, pfield: astfield | None = None, *,
                 lines: list[str] | None = None):
        self.ast    = anode
        self.parent = parent
        self.pfield = pfield
        anode.f     = self

        if parent is not None:
            self.root   = parent.root
            self._lines = None

        else:
            self.root   = self
            self._lines = [aststr(s) for s in lines]

            self._make_ftree()

    @classmethod
    def fromast(cls, anode: AST) -> 'FST':
        raise NotImplementedError  # TODO: fill in location info, unparse and create FST

    @staticmethod
    def parse(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs) -> 'FST':
        anode = ast.parse(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs)

        FST(anode, lines=source.split('\n'))

        return anode

    @staticmethod
    def unparse(ast_obj) -> str:
        return ast_obj.f.str

















parse   = FST.parse
unparse = FST.unparse
