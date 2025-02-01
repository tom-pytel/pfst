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
    root:   'FST'
    parent: Optional['FST']

    @property
    def is_root(self) -> bool:
        return self is self.root


    @staticmethod
    def parse(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs) -> 'FST':
        node = ast.parse(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs)

        return node


    @staticmethod
    def unparse(ast_obj) -> str:
        return ast.unparse(ast_obj)






















parse   = FST.parse
unparse = FST.unparse
