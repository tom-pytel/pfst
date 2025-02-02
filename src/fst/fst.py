__all_other__ = None
__all_other__ = set(globals())
from ast import *
__all_other__ = set(globals()) - __all_other__

import ast as ast_
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

        anode = self.ast

        try:
            col     = self.root._lines[(ln := anode.lineno - 1)].b2c(anode.col_offset)
            end_col = self.root._lines[(end_ln := anode.end_lineno - 1)].b2c(anode.end_col_offset)
            pos     = (ln, col, end_ln, end_col)

        except AttributeError:
            max_ln = max_col = -(min_ln := (min_col := (inf := float('inf'))))

            for child in iter_child_nodes(anode):
                if child_pos := child.f.pos:
                    ln, col, end_ln, end_col = child_pos

                    if ln < min_ln:
                        min_ln  = ln
                        min_col = col

                    elif ln == min_ln:
                        if col < min_col:
                            min_col = col

                    if end_ln > max_ln:
                        max_ln  = end_ln
                        max_col = end_col

                    elif end_ln == max_ln:
                        if end_col > max_col:
                            max_col = end_col

            pos = None if min_ln == inf else (min_ln, min_col, max_ln, max_col)

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

            for field, child in iter_fields(anode):
                if isinstance(child, AST):
                    stack.append(FST(child, fnode, astfield(field)))
                elif isinstance(child, list):
                    stack.extend(FST(anode, fnode, astfield(field, idx))
                                 for idx, anode in enumerate(child) if isinstance(anode, AST))

    def _repr_tail(self) -> str:
        tail = ' ROOT' if self.is_root else ''
        pos  = self.pos

        # return tail + f' # {pos[0]},{pos[1]} -> {pos[2]},{pos[3]}' if pos else tail
        # return tail + f' ({pos[0]},{pos[1]} -> {pos[2]},{pos[3]})' if pos else tail
        return tail + f' {pos[0]},{pos[1]} -> {pos[2]},{pos[3]}' if pos else tail

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
    def from_ast(ast: AST, *, calc_pos: bool = True) -> 'FST':
        """Add FST to existing AST.

        Args:
            ast: The root AST node.
            calc_pos: Get actual node positions by unparsing then parsing again. Use when you are not certain node
                positions are correct or even present. Default True.
        """

        src   = ast_.unparse(ast)
        lines = src.split('\n')

        if calc_pos:
            ast = ast_.parse(src)


            # TODO: 'inplace' or 'copy'?


        return FST(ast, lines=lines)

    @staticmethod
    def parse(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs) -> 'FST':
        anode = ast_.parse(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs)

        FST(anode, lines=source.split('\n'))

        return anode

    @staticmethod
    def unparse(ast_obj) -> str:
        return ast_obj.f.str

    def dump(self, indent: str = '', full: bool = False, prefix: str = ''):
        tail = self._repr_tail()

        print(f'{indent}{prefix}{self.ast.__class__.__qualname__}{" .." * bool(tail)}{tail}')

        for field, child in iter_fields(self.ast):
            if full or (child != []):
                print(f'  {indent}.{field}')

            if isinstance(child, AST):
                child.f.dump(indent + '    ', full)
            elif not isinstance(child, list):
                print(f'    {indent}{child!r}')

            else:
                for i, anode in enumerate(child):
                    if isinstance(anode, AST):
                        anode.f.dump(indent + '    ', full, f'{i}: ')
                    else:
                        print(f'    {indent}{i}: {anode!r}')








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
