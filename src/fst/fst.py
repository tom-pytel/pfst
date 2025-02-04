__all_other__ = None
__all_other__ = set(globals())
from ast import *
__all_other__ = set(globals()) - __all_other__

import ast as ast_
import functools
import re
from typing import Any, Callable, Literal, Optional, Union

from .util import *

__all__ = list(__all_other__ | {
    'FST', 'parse', 'unparse',
})

_re_empty_line         = re.compile(r'^\s*$')     # completely empty or space-filled line
_re_line_continuation  = re.compile(r'.*\\\s*$')  # line continuation with backslash


def only_root(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not args[0].is_root:
            raise RuntimeError(f"'{func.__qualname__}' can only be called on the root node")

        return func(*args, **kwargs)

    return wrapper


def parse(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs):
    return FST.from_src(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs).ast


def unparse(ast_obj):
    return f.text if (f := getattr(ast_obj, 'f', None)) else ast_.unparse(ast_obj)


class FST:
    """AST formatting information and easy manipulation."""

    ast:           AST
    parent:        Optional['FST']                   # None in root node
    pfield:        astfield | None                   # None in root node
    root:          'FST'                             # self in root node
    indent:        str                               # ROOT ONLY!
    _loc:          tuple[int, int, int, int] | None  # MAY NOT EXIST!
    _lines:        list[bistr]                       # ROOT ONLY!
    _parse_params: dict[str, Any]                    # ROOT ONLY!

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def lines(self) -> list[str]:
        if self.is_root:
            return self._lines


        raise NotImplementedError  # TODO: snip and return those lines





    @property
    def text(self) -> str:
        return '\n'.join(self.lines)

    @property
    def loc(self) -> tuple[int, int, int, int] | None:
        try:
            return self._loc
        except AttributeError:
            pass

        ast = self.ast

        try:
            col     = self.root._lines[(ln := ast.lineno - 1)].b2c(ast.col_offset)
            end_col = self.root._lines[(end_ln := ast.end_lineno - 1)].b2c(ast.end_col_offset)
            loc     = (ln, col, end_ln, end_col)

        except AttributeError:
            max_ln = max_col = -(min_ln := (min_col := (inf := float('inf'))))

            for _, child in iter_fields(ast):
                if isinstance(child, AST):
                    child = (child,)
                elif not isinstance(child, list):
                    continue

                else:
                    # child = [c for c in child if isinstance(c, AST)]
                    for first_child in child:
                        if isinstance(first_child, AST):
                            break
                    else:
                        continue

                    for last_child in reversed(child):
                        if isinstance(last_child, AST):
                            break

                    if last_child is first_child:
                        child = (first_child,)
                    else:
                        child = (first_child, last_child)

                for child in child:
                    if child_pos := child.f.loc:
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

            loc = None if min_ln == inf else (min_ln, min_col, max_ln, max_col)

        self._loc = loc

        return loc

    @property
    def ln(self) -> int:  # 0 based
        return (l := self.loc) and l[0]

    @property
    def col(self) -> int:  # char index
        return (l := self.loc) and l[1]

    @property
    def end_ln(self) -> int:  # 0 based
        return (l := self.loc) and l[2]

    @property
    def end_col(self) -> int:  # char index
        return (l := self.loc) and l[3]

    @property
    def lineno(self) -> int:  # 1 based
        return (l := self.loc) and l[0] + 1

    @property
    def col_offset(self) -> int:  # byte index
        return (l := self.loc) and self.root._lines[l[0]].c2b(l[1])

    @property
    def end_lineno(self) -> int:  # 1 based
        return (l := self.loc) and l[2] + 1

    @property
    def end_col_offset(self) -> int:  # byte index
        return (l := self.loc) and self.root._lines[l[2]].c2b(l[3])

    def _make_fst_tree(self):
        """Create tree of FST nodes for each AST node from root. Call only on root."""

        stack = [self]

        while stack:
            fst = stack.pop()
            ast = fst.ast

            for name, child in iter_fields(ast):
                if isinstance(child, AST):
                    stack.append(FST(child, fst, astfield(name)))
                elif isinstance(child, list):
                    stack.extend(FST(ast, fst, astfield(name, idx))
                                 for idx, ast in enumerate(child) if isinstance(ast, AST))

    def _repr_tail(self) -> str:
        tail = ' ROOT' if self.is_root else ''
        loc  = self.loc

        return tail + f' {loc[0]},{loc[1]} -> {loc[2]},{loc[3]}' if loc else tail

    # ------------------------------------------------------------------------------------------------------------------

    def __repr__(self) -> str:
        tail = self._repr_tail()
        rast = repr(self.ast)

        return f'<fst{rast[4 : -1]}{tail}>' if rast.startswith('<') else f'fst.{rast[:-1]}{tail})'

    def __init__(self, ast: AST, parent: Optional['FST'] = None, pfield: astfield | None = None, **root_params):
        self.ast    = ast
        self.parent = parent
        self.pfield = pfield
        ast.f       = self

        if parent is not None:
            self.root = parent.root

            return

        # ROOT
        self.root          = self
        self.indent        = root_params.get('indent', '    ')
        self._lines        = [bistr(s) for s in root_params['lines']]
        self._parse_params = root_params.get('parse_params') or {}

        self._make_fst_tree()

    @staticmethod
    def from_src(source: str | bytes | list[str], filename: str = '<unknown>', mode: str = 'exec', *,
                 type_comments: bool = False, feature_version: tuple[int, int] | None = None, **parse_params) -> 'FST':
        if isinstance(source, bytes):
            source = source.decode()

        if isinstance(source, str):
            lines  = source.split('\n')
        else:
            lines  = source
            source = '\n'.join(lines)

        parse_params = dict(parse_params, type_comments=type_comments, feature_version=feature_version)
        ast          = ast_.parse(source, filename, mode, **parse_params)

        return FST(ast, lines=lines, parse_params=parse_params)

    @staticmethod
    def from_ast(ast: AST, *, calc_loc: bool | Literal['copy'] = True,
                 type_comments: bool | None = False, feature_version=None, **parse_params) -> 'FST':
        """Add FST to existing AST, optionally copying positions from reparsed AST (default) or whole AST for new FST.

        Do not set `calc_loc` to `False` unless you parsed the `ast` from a previous output of ast.unparse(), otherwise
        there will almost certaionly be problems!

        Args:
            ast: The root AST node.
            calc_loc: Get actual node positions by unparsing then parsing again. Use when you are not certain node
                positions are correct or even present. Updates original ast unless set to "copy", in which case a copied
                AST is used. Set to `False` when you know positions are correct and want to use given AST. Default True.
            type_comments: ast.parse() parameter.
            feature_version: ast.parse() parameter.
            parse_params: Other parameters to ast.parse().
        """

        src   = ast_.unparse(ast)
        lines = src.split('\n')

        if type_comments is None:
            type_comments = has_type_comments(ast)

        parse_params = dict(parse_params, type_comments=type_comments, feature_version=feature_version)

        if calc_loc:
            mode = get_parse_mode(ast)
            astp = ast_.parse(src, mode=mode, **parse_params)

            if astp.__class__ is not ast.__class__:
                astp = astp.body if isinstance(astp, Expression) else astp.body[0]

                if astp.__class__ is not ast.__class__:
                    raise RuntimeError('could not reproduce ast')

            if calc_loc == 'copy':
                if not compare(astp, ast, type_comments=type_comments):
                    raise RuntimeError('could not reparse ast identically')

                ast = astp

            else:
                if not copy_attributes(astp, ast, ('lineno', 'col_offset', 'end_lineno', 'end_col_offset'),
                                       compare=True, type_comments=type_comments):
                    raise RuntimeError('could not reparse ast identically')

        return FST(ast, lines=lines, parse_params=parse_params)

    @only_root
    def verify(self, *, do_raise: bool = True) -> Union['FST', None]:  # -> Self | None:
        """Sanity check, make sure parsed source matches ast."""

        ast          = self.ast
        parse_params = self._parse_params
        astp         = ast_.parse(self.text, mode=get_parse_mode(ast), **parse_params)

        if not compare(astp, ast, locations=True, type_comments=parse_params['type_comments']):
            if do_raise:
                raise RuntimeError('verify failed')
            else:
                return None

        return self

    @only_root
    def sniploc(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        if end_ln == ln:
            return [self._lines[ln][col : end_col]]
        else:
            return [(l := self._lines)[ln][col:]] + l[ln + 1 : end_ln] + [l[end_ln][:end_col]]

    # @only_root
    # def offset(self, lineno: int, col_offset: int, dlineno: int, dcol_offset: int, *, inclusive: bool = False) -> 'FST':  # -> Self
    #     """Offset all node positions on or after lineno / col_offset by delta line / col_offset (byte positions).

    #     Args:
    #         lineno: Line (1 based) of offset point.
    #         col_offset: Column of offset point (byte index).
    #         dlineno: Number of lines to offset everything on or after offset point, can be 0.
    #         dcol_offset: Column offset to apply to everything ON the offset point line (byte index). Columns on lines
    #             AFTER the offset line will not be changed.
    #         inclusive: Whether to offset endpoint if it falls exactly at lineno / col_offset or not.
    #     """

    #     for n in walk(self.ast):
    #         if not (nend_lineno := getattr(n, 'end_lineno', None)):  # will never be 0
    #             continue

    #         nend_coloffset = n.end_col_offset

    #         if nend_lineno > lineno:
    #             n.end_lineno = nend_lineno + dlineno

    #         elif nend_lineno == lineno and (nend_coloffset >= col_offset if inclusive else nend_coloffset > col_offset):
    #             n.end_lineno     = nend_lineno + dlineno
    #             n.end_col_offset = nend_coloffset + dcol_offset

    #         else:
    #             continue

    #         if (lineno := n.lineno) > lineno:
    #             n.lineno = lineno + dlineno

    #         elif lineno == lineno and (col_offset := n.col_offset) >= col_offset:
    #             n.lineno     = lineno + dlineno
    #             n.col_offset = col_offset + dcol_offset

    #         n.f.touch()

    #     return self

    @only_root
    def offset(self, ln: int, col: int, dln: int, dcol_offset: int, inc: bool = False) -> 'FST':  # -> Self
        """Offset all node positions in the tree on or after ln / col by delta line / col_offset (col byte offset).

        This only offsets the positions in the AST nodes, doesn't change any text, so make sure that is correct before
        getting any FST locations from affected nodes otherwise they will be wrong.

        Args:
            ln: Line of offset point.
            col: Column of offset point (char index).
            dln: Number of lines to offset everything on or after offset point, can be 0.
            dcol_offset: Column offset to apply to everything ON the offset point line (in bytes). Columns on lines
                AFTER the offset line will not be changed.
            inc: Whether to offset endpoint if it falls exactly at ln / col or not (inclusive).
        """

        for a in walk(self.ast):
            if (fend_ln := (f := a.f).end_ln) is None or not hasattr(a, 'end_col_offset'):
                f.touch()  # can't determine if before or after offset point or ast node doesn't have loc so touch just in case

                continue

            if fend_ln > ln:
                a.end_lineno += dln

            elif fend_ln == ln and (f.end_col >= col if inc else f.end_col > col):
                a.end_lineno     += dln
                a.end_col_offset += dcol_offset

            else:
                continue

            if (fln := f.ln) > ln:
                a.lineno += dln

            elif fln == ln and f.col >= col:
                a.lineno     += dln
                a.col_offset += dcol_offset

            f.touch()

        return self





    def dump(self, indent: int = 3, full: bool = False, cind: str = '', prefix: str = '', linefunc: Callable = print):
        tail = self._repr_tail()
        sind = ' ' * indent

        linefunc(f'{cind}{prefix}{self.ast.__class__.__qualname__}{" .." * bool(tail)}{tail}')

        for name, child in iter_fields(self.ast):
            is_list = isinstance(child, list)

            if full or (child != []):
                linefunc(f'{sind}{cind}.{name}{f"[{len(child)}]" if is_list else ""}')

            if is_list:
                for i, ast in enumerate(child):
                    if isinstance(ast, AST):
                        ast.f.dump(indent, full, cind + ' ' * indent, f'{i}: ')
                    else:
                        linefunc(f'{sind}{sind}{cind}{i}: {ast!r}')

            elif isinstance(child, AST):
                child.f.dump(indent, full, cind + sind * 2)
            else:
                linefunc(f'{sind}{sind}{cind}{child!r}')

    def touch(self) -> 'FST':  # -> Self:
        """AST node was modified, clear out any cached info (except lines)."""

        try:
            del self._loc
        except AttributeError:
            pass

        return self

    def snip(self) -> list[str]:
        return self.root.sniploc(*self.loc)

    def starts_new_line(self) -> str | None:
        """Returns line prefix text if this node starts a new line and is not a line continuation or following a
        semicolon, None otherwise."""

        if (ln := self.ln) is None:
            return None

        col  = self.col
        root = self.root

        if (_re_empty_line.match(pre := (lines := root._lines)[ln][:col]) and
            (not ln or not _re_line_continuation.match(lines[ln - 1]))):
            return pre

        return None

    def get_indent(self) -> str:
        """Determine indentation of node at `stmt` or `mod` level at or above self, otherwise at root node."""

        while (parent := self.parent) and not isinstance(self.ast, (stmt, mod)):
            self = parent

        root         = self.root
        extra_indent = ''  # may result from unknown indent in single line "if something: whats_my_stmt_indentation?"

        while parent:
            siblings = getattr(parent.ast, (pfield := self.pfield).name)

            if pfield.idx is None:
                siblings = [siblings]

            for sibling in siblings:
                if (line_start := sibling.f.starts_new_line()) is not None:
                    return line_start + extra_indent

            extra_indent += root.indent
            self          = parent
            parent        = self.parent

        return extra_indent








    # mutate()
    # ^^^^^^^^
    # copy()
    # cut()
    # remove()
    # append()
    # insert()
    # replace()




