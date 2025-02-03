__all_other__ = None
__all_other__ = set(globals())
from ast import *
__all_other__ = set(globals()) - __all_other__

import ast as ast_
from typing import Literal, Optional

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

        ast = self.ast

        try:
            col     = self.root._lines[(ln := ast.lineno - 1)].b2c(ast.col_offset)
            end_col = self.root._lines[(end_ln := ast.end_lineno - 1)].b2c(ast.end_col_offset)
            pos     = (ln, col, end_ln, end_col)

        except AttributeError:
            max_ln = max_col = -(min_ln := (min_col := (inf := float('inf'))))

            for child in iter_child_nodes(ast):
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
    def ln(self) -> int:  # 0 based
        return (p := self.pos) and p[0]

    @property
    def col(self) -> int:  # char index
        return (p := self.pos) and p[1]

    @property
    def end_ln(self) -> int:  # 0 based
        return (p := self.pos) and p[2]

    @property
    def end_col(self) -> int:  # char index
        return (p := self.pos) and p[3]

    @property
    def lineno(self) -> int:  # 1 based
        return (p := self.pos) and p[0] + 1

    @property
    def col_offset(self) -> int:  # byte index
        return (p := self.pos) and self.root._lines[p[0]].c2b(p[1])

    @property
    def end_lineno(self) -> int:  # 1 based
        return (p := self.pos) and p[2] + 1

    @property
    def end_col_offset(self) -> int:  # byte index
        return (p := self.pos) and self.root._lines[p[2]].c2b(p[3])

    def _make_fst_tree(self):
        "Create tree of FST nodes for each AST node from root. Call only on root."

        stack = [self]

        while stack:
            fst = stack.pop()
            ast = fst.ast

            for field, child in iter_fields(ast):
                if isinstance(child, AST):
                    stack.append(FST(child, fst, astfield(field)))
                elif isinstance(child, list):
                    stack.extend(FST(ast, fst, astfield(field, idx))
                                 for idx, ast in enumerate(child) if isinstance(ast, AST))

    def _repr_tail(self) -> str:
        tail = ' ROOT' if self.is_root else ''
        pos  = self.pos

        return tail + f' {pos[0]},{pos[1]} -> {pos[2]},{pos[3]}' if pos else tail

    def __repr__(self) -> str:
        tail = self._repr_tail()
        rast = repr(self.ast)

        return f'<fst{rast[4 : -1]}{tail}>' if rast.startswith('<') else f'fst.{rast[:-1]}{tail})'

    def __init__(self, ast: AST, parent: Optional['FST'] = None, pfield: astfield | None = None, *,
                 lines: list[str] | None = None):
        self.ast    = ast
        self.parent = parent
        self.pfield = pfield
        ast.f       = self

        if parent is not None:
            self.root = parent.root

        else:
            self.root   = self
            self._lines = [aststr(s) for s in lines]

            self._make_fst_tree()

    @staticmethod
    def from_src(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs) -> 'FST':
        if isinstance(source, str):
            lines  = source.split('\n')
        else:
            lines  = source
            source = '\n'.join(lines)

        ast = ast_.parse(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs)

        return FST(ast, lines=lines)

    @staticmethod
    def from_ast(ast: AST, *, calc_pos: bool | Literal['copy'] = True) -> 'FST':
        """Add FST to existing AST.

        Args:
            ast: The root AST node.
            calc_pos: Get actual node positions by unparsing then parsing again. Use when you are not certain node
                positions are correct or even present. Updates original ast unless set to "copy". Default True.
        """

        src   = ast_.unparse(ast)
        lines = src.split('\n')

        if calc_pos:
            mode = guess_parse_mode(ast)
            astp = ast_.parse(src, mode=mode, type_comments=has_type_comments(ast))

            if astp.__class__ is not ast.__class__:
                astp = astp.body if isinstance(astp, Expression) else astp.body[0]

                if astp.__class__ is not ast.__class__:
                    raise RuntimeError('could not reproduce ast')

            if not compare_asts(astp, ast, type_comments=True):
                raise RuntimeError('could not reparse ast identically')

            if calc_pos == 'copy':
                ast = astp
            else:
                copy_ast_attributes(astp, ast)

        return FST(ast, lines=lines)

    def dump(self, indent: str = '', full: bool = False, prefix: str = ''):
        tail = self._repr_tail()

        print(f'{indent}{prefix}{self.ast.__class__.__qualname__}{" .." * bool(tail)}{tail}')

        for field, child in iter_fields(self.ast):
            is_list = isinstance(child, list)

            if full or (child != []):
                print(f'  {indent}.{field}{f"[{len(child)}]" if is_list else ""}')

            if is_list:
                for i, ast in enumerate(child):
                    if isinstance(ast, AST):
                        ast.f.dump(indent + '    ', full, f'{i}: ')
                    else:
                        print(f'    {indent}{i}: {ast!r}')

            elif isinstance(child, AST):
                child.f.dump(indent + '    ', full)
            else:
                print(f'    {indent}{child!r}')

    def touch(self):  # -> Self:
        """AST node was modified, clear out any cached info."""

        try:
            del self._pos
        except AttributeError:
            pass

        return self








    # mutate()
    # ^^^^^^^^
    # copy()
    # cut()
    # remove()
    # append()
    # insert()
    # replace()





def parse(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs):
    return FST.from_src(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs).ast

def unparse(ast_obj):
    return f.str if (f := getattr(ast_obj, 'f', None)) else ast_.unparse(ast_obj)
