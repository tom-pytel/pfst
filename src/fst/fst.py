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
    """AST formatting information and easy manipulation."""

    ast:    AST
    parent: Optional['FST']
    pfield: astfield | None
    root:   'FST'
    _lines: list[aststr]  # MAY NOT EXIST!
    _pos:   tuple[int, int, int, int] | None  # MAY NOT EXIST!

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
        return '\n'.join(self.lines)

    @property
    def pos(self) -> tuple[int, int, int, int] | None:
        try:
            return self._pos
        except AttributeError:
            pass

        try:
            anode   = self.ast
            ln      = anode.lineno - 1
            col     = self.root._lines[ln].b2c(anode.col_offset)
            end_ln  = anode.end_lineno - 1
            end_col = self.root._lines[end_ln].b2c(anode.end_col_offset)
            pos     = (ln, col, end_ln, end_col)

        except AttributeError:
            pos = None

        self._pos = pos

        return pos

    @property
    def ln(self) -> int:
        return (p := self.pos) and p[0]

    @property
    def col(self) -> int:
        return (p := self.pos) and p[1]

    @property
    def end_ln(self) -> int:
        return (p := self.pos) and p[2]

    @property
    def end_col(self) -> int:
        return (p := self.pos) and p[3]

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

    def _repr_tail(self) -> str:
        tail = ' ROOT' if self.is_root else ''
        pos  = self.pos

        return tail + f'; {pos[0]},{pos[1]} -> {pos[2]},{pos[3]}' if pos else tail

    def __repr__(self) -> str:
        tail = self._repr_tail()
        rast = repr(self.ast)

        return f'<fst{rast[4 : -1]}{tail}>' if rast.startswith('<') else f'fst.{rast[:-1]}{tail})'

    def __init__(self, anode: AST, parent: Optional['FST'] = None, pfield: astfield | None = None, *,
                 lines: list[str] | None = None):
        self.ast    = anode
        self.parent = parent
        self.pfield = pfield
        anode.f     = self

        if parent is not None:
            self.root = parent.root

        else:
            self.root   = self
            self._lines = [aststr(s) for s in lines]

            self._make_ftree()

    @staticmethod
    def from_ast(anode: AST) -> 'FST':
        raise NotImplementedError  # TODO: fill in location info, unparse and create FST

    @staticmethod
    def parse(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs) -> 'FST':
        anode = ast.parse(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs)

        FST(anode, lines=source.split('\n'))

        return anode

    @staticmethod
    def unparse(ast_obj) -> str:
        return ast_obj.f.str

    def dump(self, indent: str = '', full: bool = False, prefix: str = ''):
        print(f'{indent}{prefix}<{self.ast.__class__.__qualname__}{self._repr_tail()}>')

        for field in self.ast._fields:
            child = getattr(self.ast, field)

            if full or (child != []):
                print(f'  {indent}.{field}:')

            if isinstance(child, list):
                for i, anode in enumerate(child):
                    if isinstance(anode, ast.AST):
                        anode.f.dump(indent + '    ', full, f'{i}: ')
                    else:
                        print(f'    {indent}{i}: {anode!r}')

            elif isinstance(child, ast.AST):
                child.f.dump(indent + '    ', full)
            else:
                print(f'    {indent}{child!r}')








    # mutate()
    # ^^^^^^^^
    # copy()
    # cut()
    # remove()
    # append()
    # insert()
    # replace()





parse   = FST.parse
unparse = FST.unparse
