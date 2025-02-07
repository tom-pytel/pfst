"""Most of the code in this module deals with line continuations via backslash."""

__all_other__ = None
__all_other__ = set(globals())
from ast import *
__all_other__ = set(globals()) - __all_other__

import ast as ast_
import functools
import re
from typing import Any, Callable, Literal, NamedTuple, Optional, Union

from .util import *
from .util import TypeVar, ParamSpec, TypeVarTuple  # for py < 3.12

__all__ = list(__all_other__ | {
    'TypeVar', 'ParamSpec', 'TypeVarTuple',
    'FST', 'parse', 'unparse',
})

_STATEMENTISH = (mod, stmt, ExceptHandler, match_case)  # except for mod: always in lists, part of blocks can not be in multiline and statementish start lines

# _re_line_continuation = re.compile(r'^.*\\$')    # line continuation with backslash
_re_empty_line_start  = re.compile(r'^[ \t]*')    # start of completely empty or space-filled line
_re_empty_line        = re.compile(r'^[ \t]*$')   # completely empty or space-filled line
_re_line_continuation = re.compile(r'^[^#]*\\$')  # line continuation with backslash not following a comment start '#' (assumed no asts contained in line)


def only_root(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not args[0].is_root:
            raise RuntimeError(f"'{func.__qualname__}' can only be called on the root node")

        return func(*args, **kwargs)

    return wrapper


def parse(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs):
    return FST.from_src(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs).a


def unparse(ast_obj):
    return f.text if (f := getattr(ast_obj, 'f', None)) else ast_.unparse(ast_obj)


class fstloc(NamedTuple):
    ln:      int
    col:     int
    end_ln:  int
    end_col: int


class FST:
    """AST formatting information and easy manipulation."""

    a:             AST
    parent:        Optional['FST']  # None in root node
    pfield:        astfield | None  # None in root node
    root:          'FST'            # self in root node
    _loc:          fstloc | None    # MAY NOT EXIST!
    _bloc:         fstloc | None    # MAY NOT EXIST! bounding location, including preceding decorators

    indent:        str              # ROOT ONLY! default indentation to use when unknown
    _lines:        list[bistr]      # ROOT ONLY!
    _parse_params: dict[str, Any]   # ROOT ONLY!

    @property
    def is_root(self) -> bool:
        return self.parent is None

    @property
    def lines(self) -> list[str]:
        if self.is_root:
            return self._lines
        elif self.ln is not None:
            return self.root._lines[self.ln : self.end_ln + 1]
        else:
            return self.parent.lines

    @property
    def text(self) -> str:
        return '\n'.join(self.lines)

    @property
    def loc(self) -> fstloc | None:
        try:
            return self._loc
        except AttributeError:
            pass

        ast = self.a

        try:
            ln             = ast.lineno - 1
            col_offset     = ast.col_offset
            end_ln         = ast.end_lineno - 1
            end_col_offset = ast.end_col_offset

        except AttributeError:
            max_ln = max_col = -(min_ln := (min_col := (inf := float('inf'))))

            for _, child in iter_fields(ast):
                if isinstance(child, AST):
                    if not (start := (end := child.f.bloc)):
                        continue

                elif not isinstance(child, list):
                    continue

                else:
                    for c in child:
                        if isinstance(c, AST) and (start := c.f.bloc):
                            break
                    else:
                        continue

                    for c in reversed(child):
                        if isinstance(c, AST) and (end := c.f.bloc):
                            break

                if start.ln < min_ln:
                    min_ln  = start.ln
                    min_col = start.col

                elif start.ln == min_ln:
                    if start.col < min_col:
                        min_col = start.col

                if end.end_ln > max_ln:
                    max_ln  = end.end_ln
                    max_col = end.end_col

                elif end.end_ln == max_ln:
                    if end.end_col > max_col:
                        max_col = end.end_col

            if min_ln != inf:
                loc = fstloc(min_ln, min_col, max_ln, max_col)
            elif self.is_root:
                loc = fstloc(0, 0, 0, 0)  # root must have location
            else:
                loc = None

        else:
            col     = self.root._lines[ln].b2c(col_offset)
            end_col = self.root._lines[end_ln].b2c(end_col_offset)
            loc     = fstloc(ln, col, end_ln, end_col)

        self._loc = loc

        return loc

    @property
    def bloc(self) -> fstloc:
        try:
            return self._bloc
        except AttributeError:
            pass

        if not (loc := self.loc):
            bloc = None
        elif not (decos := getattr(self.a, 'decorator_list', None)):
            bloc = loc
        else:
            bloc = fstloc(decos[0].f.ln, loc[1], loc[2], loc[3])  # column of deco '@' will be same as our column

        self._bloc = bloc

        return bloc

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
    def bln(self) -> int:  # bounding location including @decorators
        return (l := self.bloc) and l[0]

    bcol     = col
    bend_ln  = end_ln
    bend_col = end_col

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

    def _repr_tail(self) -> str:
        tail = ' ROOT' if self.is_root else ''
        loc  = self.loc

        return tail + f' {loc[0]},{loc[1]} -> {loc[2]},{loc[3]}' if loc else tail

    def _make_fst_tree(self):
        """Create tree of FST nodes for each AST node from root. Call only on root."""

        stack = [self]

        while stack:
            fst = stack.pop()
            ast = fst.a

            for name, child in iter_fields(ast):
                if isinstance(child, AST):
                    stack.append(FST(child, fst, astfield(name)))
                elif isinstance(child, list):
                    stack.extend(FST(ast, fst, astfield(name, idx))
                                 for idx, ast in enumerate(child) if isinstance(ast, AST))

    def _get_preceding_lineends(self, ln: int) -> list[int]:
        """Get line positions past all asts on line (for comment and line continuation checking). Positions may include
        parts of statements (like a simple class def), but not '#' or '\' chars."""

        lines    = self.root._lines
        lineends = [0] * ln

        if self.root.bloc is None:
            return lineends

        stack = [self.root.a, *decos] if (decos := getattr(self, 'decorator_list', None)) else [self.root.a]

        while stack:
            if (end_ln := (a := stack.pop()).f.bend_ln) < ln:  # we know is not None
                lineends[end_ln] = max(lineends[end_ln], a.f.bend_col)

            if isinstance(a, Constant):
                if isinstance(a.value, (str, bytes)):  # multiline str?
                    for i in range(a.f.ln, a.f.end_ln):  # specifically leave out last line
                        lineends[i] = len(lines[i])

                continue

            for _, child in iter_fields(a):
                if isinstance(child, AST):
                    if child is not self and (cln := child.f.bln) is not None and cln < ln:
                        stack.append(child)

                elif isinstance(child, list):
                    for c in child:
                        if c is self:
                            break
                        if not isinstance(c, AST) or (cln := c.f.bln) is None:
                            continue
                        if cln >= ln:
                            break

                        stack.append(c)

        return lineends

    # ------------------------------------------------------------------------------------------------------------------

    def __repr__(self) -> str:
        tail = self._repr_tail()
        rast = repr(self.a)

        return f'<fst{rast[4 : -1]}{tail}>' if rast.startswith('<') else f'fst.{rast[:-1]}{tail})'

    def __init__(self, ast: AST, parent: Optional['FST'] = None, pfield: astfield | None = None, **root_params):
        self.a      = ast
        self.parent = parent
        self.pfield = pfield
        ast.f       = self

        if parent is not None:
            self.root = parent.root

            return

        # ROOT

        self.root   = self
        self._lines = [bistr(s) for s in root_params['lines']]

        if from_ := root_params.get('from_'):  # copy params from source tree
            root               = from_.root
            self.indent        = root.indent
            self._parse_params = root._parse_params

        self.indent        = root_params.get('indent', getattr(self, 'indent', '    '))
        self._parse_params = root_params.get('parse_params', getattr(self, '_parse_params', {}))

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
                if not copy_attributes(astp, ast, compare=True, type_comments=type_comments):
                    raise RuntimeError('could not reparse ast identically')

        return FST(ast, lines=lines, parse_params=parse_params)

    def verify(self, *, do_raise: bool = True) -> Union['FST', None]:  # -> Self | None:
        """Sanity check, make sure parsed source matches ast."""

        root         = self.root
        ast          = root.a
        parse_params = root._parse_params
        astp         = ast_.parse(root.text, mode=get_parse_mode(ast), **parse_params)

        if not isinstance(ast, mod):
            if isinstance(astp, Expression):
                astp = astp.body
            elif len(astp.body) != 1:
                raise ValueError('verify failed reparse')
            else:
                astp = astp.body[0]

        if not compare(astp, ast, locations=True, type_comments=parse_params['type_comments'], do_raise=do_raise):
            return None

        return self

    def dump(self, indent: int = 2, full: bool = False, cind: str = '', prefix: str = '', linefunc: Callable = print):
        tail = self._repr_tail()
        sind = ' ' * indent

        linefunc(f'{cind}{prefix}{self.a.__class__.__qualname__}{" .." * bool(tail)}{tail}')

        for name, child in iter_fields(self.a):
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

    # ------------------------------------------------------------------------------------------------------------------

    def is_parsable(self) -> bool:
        if not self.loc or not is_parsable(self.a):
            return False

        ast = self.a

        if isinstance(ast, Tuple):  # tuple of slices used in indexing (like numpy)
            for e in ast.elts:
                if isinstance(e, Slice):
                    return False

        elif parent := self.parent:
            if isinstance(ast, JoinedStr):  # formatspec '.1f' type strings without quote delimiters
                if self.pfield.name == 'format_spec' and isinstance(parent.a, FormattedValue):
                    return False

            elif isinstance(ast, Constant):  # string parts of f-string without quote delimiters
                if self.pfield.name == 'values' and isinstance(parent.a, JoinedStr) and isinstance(ast.value, str):
                    return False

        return True

    def sniploc(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        if end_ln == ln:
            return [bistr(self.root._lines[ln][col : end_col])]
        else:
            return [bistr((l := self.root._lines)[ln][col:])] + l[ln + 1 : end_ln] + [bistr(l[end_ln][:end_col])]

    def sniploc_text(self, ln: int, col: int, end_ln: int, end_col: int) -> str:
        return '\n'.join(self.sniploc(ln, col, end_ln, end_col))

    def snip(self) -> list[str]:
        return self.root.sniploc(*self.loc)

    def snip_text(self) -> str:
        return '\n'.join(self.snip())

    def get_indentable_lns(self) -> set[int]:
        """Get set of indentable lines (past the first one usually because that is normally handled specially)."""

        lns = set(range(self.bln + 1, self.bend_ln + 1))

        while (parent := self.parent) and not isinstance(self.a, _STATEMENTISH):
            self = parent

        for a in walk(self.a):  # find multiline strings and exclude their unindentable lines
            if isinstance(a, Constant) and (isinstance(a.value, (str, bytes))):
                lns -= set(range(a.lineno, a.end_lineno))  # specifically leave first line of multiline string because that is indentable

        return lns

    def get_indent(self) -> str:
        """Determine proper indentation of node at `stmt` (or other similar) level at or above self, otherwise at root
        node. Even if it is a continuation or on same line as block statement."""

        f = self

        while (parent := f.parent) and not isinstance(f.a, _STATEMENTISH):
            f = parent

        lines        = (root := f.root)._lines
        lineends     = None
        extra_indent = ''  # may result from unknown indent in single line "if something: whats_my_stmt_indentation?"

        while parent:
            a = getattr(parent.a, (pfield := f.pfield).name)

            if pfield.idx is not None:
                f = a[0].f  # we specifically want first statment / exception handler / match case in list

            if _re_empty_line.match(line_start := lines[(ln := f.ln)][:f.col]):
                if not ln or not (last_line := lines[(last_ln := ln - 1)]).endswith('\\'):
                    return line_start + extra_indent

                if not lineends:
                    lineends = f._get_preceding_lineends(ln)

                if not _re_line_continuation.match(last_line[lineends[last_ln]:]):
                    return line_start + extra_indent

            extra_indent += root.indent
            f             = parent
            parent        = f.parent

        # TODO: handle possibility of syntactically incorrect but indented root node

        return extra_indent

    # ------------------------------------------------------------------------------------------------------------------

    def touch(self, recurse: bool = False) -> 'FST':  # -> Self:
        """AST node was modified, clear out any cached info."""

        if not recurse:
            try:
                del self._loc, self._bloc  # _bloc only exists if _loc does
            except AttributeError:
                pass

        else:
            for a in walk(self.a):
                try:
                    del a.f._loc, a.f._bloc
                except AttributeError:
                    pass

        return self

    def offset(self, ln: int, col: int, dln: int, dcol_offset: int, inc: bool = False) -> 'FST':  # -> Self
        """Offset ast node positions in the tree on or after ln / col by delta line / col_offset (col byte offset).

        This only offsets the positions in the AST nodes, doesn't change any text, so make sure that is correct before
        getting any FST locations from affected nodes otherwise they will be wrong.

        Other nodes outside this tree might need offsetting so use only on root unless special circumstances.

        Args:
            ln: Line of offset point.
            col: Column of offset point (char index).
            dln: Number of lines to offset everything on or after offset point, can be 0.
            dcol_offset: Column offset to apply to everything ON the offset point line (in bytes). Columns on lines
                AFTER the offset line will not be changed.
            inc: Whether to offset endpoint if it falls exactly at ln / col or not (inclusive).
        """

        for a in walk(self.a):
            f = a.f

            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                if (fend_ln := f.end_ln) > ln:
                    a.end_lineno += dln

                elif fend_ln == ln and (f.end_col >= col if inc else f.end_col > col):
                    a.end_lineno     += dln
                    a.end_col_offset  = end_col_offset + dcol_offset

                else:
                    continue

                if (fln := f.ln) > ln:
                    a.lineno += dln

                elif fln == ln and f.col >= col:
                    a.lineno     += dln
                    a.col_offset += dcol_offset

            f.touch()

        return self

    def offset_cols(self, dcol_offset: int, lns: set[int]) -> set[int]:
        """Offset ast col byte offsets in `lns` by a delta and return same set of indentable lines.

        Only modifies ast.
        """

        if dcol_offset:
            for a in walk(self.a):  # now offset columns where it is allowed
                if (end_col_offset := getattr(a, 'end_col_offset', None)) is None:
                    a.f.touch()  # just in case

                else:
                    if t1 := a.lineno - 1 in lns:
                        a.col_offset += dcol_offset

                    if t2 := a.end_lineno - 1 in lns:
                        a.end_col_offset = end_col_offset + dcol_offset

                    if t1 or t2:
                        a.f.touch()

        return lns

    def offset_cols_mapped(self, dcol_offsets: dict[int, int]) -> dict[int, int]:
        """Offset ast col byte offsets by a specific delta per line and return same dict of indentable lines.

        Only modifies ast.
        """

        for a in walk(self.a):  # now offset columns where it is allowed
            if (end_col_offset := getattr(a, 'end_col_offset', None)) is None:
                a.f.touch()  # just in case

            else:
                if t1 := (dcol_offset := dcol_offsets.get(a.lineno - 1)) is not None:
                    a.col_offset += dcol_offset

                if t2 := (dcol_offset := dcol_offsets.get(a.end_lineno - 1)) is not None:
                    a.end_col_offset = end_col_offset + dcol_offset

                if t1 or t2:
                    a.f.touch()

        return dcol_offsets

    def indent_tail(self, indent: str) -> set[int]:
        """Indent all indentable lines past the first one according with `indent` and adjust node locations accordingly.
        Does not modify node columns on first line."""

        if not (lns := self.offset_cols(len(indent.encode()), self.get_indentable_lns())) or not indent:
            return lns

        lines = self.root._lines

        for ln in lns:
            if l := lines[ln]:  # only indent non-empty lines
                lines[ln] = bistr(indent + l)

        return lns

    def dedent_tail(self, indent: str) -> set[int]:
        """Dedent all indentable lines past the first one by removing `indent` prefix and adjust node locations
        accordingly. Does not modify columns on first line. If cannot dedent entire amount will dedent as much as
        possible.
        """

        if not (lns := self.get_indentable_lns()) or not indent:
            return lns

        lines        = self.root._lines
        lindent      = len(indent)
        dcol_offsets = None
        newlines     = []

        def dedent(l, lindent):
            if dcol_offsets is not None:
                dcol_offsets[ln] = -lindent

            return bistr(l[lindent:])

        lns_seq = list(lns)

        for ln in lns_seq:
            if l := lines[ln]:  # only dedent non-empty lines
                if l.startswith(indent) or (lempty_start := _re_empty_line_start.match(l).end()) >= lindent:
                    l = dedent(l, lindent)

                else:
                    if not dcol_offsets:
                        dcol_offsets = {}

                        for ln2 in lns_seq:
                            if ln2 is ln:
                                break

                            dcol_offsets[ln2] = -lindent

                    l = dedent(l, lempty_start)

            newlines.append(l)

        for ln, l in zip(lns_seq, newlines):
            lines[ln] = l

        if dcol_offsets:
            self.offset_cols_mapped(dcol_offsets)
        else:
            self.offset_cols(-lindent, lns)

        return lns

    @only_root
    def safe(self, *, assign: bool = True, do_raise: bool = True) -> Union['FST', None]:  # -> Self | None
        """Make safe to parse (to make cut or copied subtrees parsable if the source is not by itself). Possibly
        reparses which may change type of ast, e.g. `keyword` "i=1" to `Assign` "i=1".

        If make safe fails the ast may be left changed.

        Args:
            assign: Whether to allow conversion to Assign or AnnAssign statement.
            do_raise: Whether to raise on failure to make safe (default: True) or return None (False).
        """

        ast   = self.a
        lines = self.lines

        ln, col, end_ln, end_col = self.loc

        if isinstance(ast, If):
            if lines[ln][col : col + 4] == 'elif':  # elif -> if
                self.offset(ln, col + 2, 0, -2)

                lines[ln] = bistr((l := lines[ln])[:col] + l[col + 2:])

        elif isinstance(ast, MatchStar):
            pass  # ast.pattern that can't be converted to expression

        elif (isinstance(ast, (expr, pattern)) or
            (isinstance(ast, arg) and not ast.annotation) or
            (isinstance(ast, TypeVar) and not ast.bound and not ast.default_value
        )):
            try:
                a = ast_.parse(text := self.text, mode='eval', **self._parse_params)

            except SyntaxError:  # if expression not parsing then try parenthesize
                try:
                    tail = (',)' if isinstance(ast, Tuple) and len(ast.elts) == 1 and
                            lines[self.end_ln][self.end_col - 1] != ',' else ')')
                    a    = ast_.parse(f'({text}{tail}', mode='eval', **self._parse_params)

                except SyntaxError:
                    if do_raise:
                        raise

                    return None

                lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col]}{tail}{l[end_col:]}')
                lines[ln]     = bistr(f'{(l := lines[ln])[:col]}({l[col:]}')

            self.a   = a.body
            self.a.f = self

            self.touch()
            self._make_fst_tree()

        elif assign and (
            (is_keyword := isinstance(ast, keyword)) or
            ((is_arg := isinstance(ast, arg)) and ast.annotation) or
            (isinstance(ast, TypeVar) and (ast.bound or ast.default_value)
        )):
            try:
                a = ast_.parse(self.text, mode='exec', **self._parse_params)

            except SyntaxError:  # if assign not parsing then try sanitize it
                newlines = lines[:]

                def maybe_replace(text, ln, col, end_ln, end_col):
                    if end_ln != ln:
                        newlines[ln] = newlines[ln][:col] + text + newlines[end_ln][end_col:]

                        del newlines[ln + 1 : end_ln + 1]

                if is_keyword:
                    maybe_replace(' = ', self.ln, self.col + len(ast.arg), (v := ast.value.f).ln, v.col)
                elif is_arg:
                    maybe_replace(': ', self.ln, self.col + len(ast.arg), (an := ast.annotation.f).ln, an.col)

                else:  # is_typevar
                    b = ast.bound

                    if (dv := ast.default_value):
                        if b:
                            maybe_replace(' = ', b.f.end_ln, b.f.end_col, dv.f.ln, dv.f.col)
                            maybe_replace(': ', self.ln, self.col + len(ast.name), b.f.ln, b.f.col)

                        else:
                            maybe_replace(' = ', self.ln, self.col + len(ast.name), dv.f.ln, dv.f.col)

                    else:  # b must be present
                        maybe_replace(': ', self.ln, self.col + len(ast.name), b.f.ln, b.f.col)

                try:
                    a = ast_.parse('\n'.join(newlines), mode='exec', **self._parse_params)

                except SyntaxError:
                    if do_raise:
                        raise

                    return None

                self._lines = [bistr(s) for s in newlines]

            self.a   = a.body[0]
            self.a.f = self

            self.touch()
            self._make_fst_tree()

        if not self.is_parsable():
            if do_raise:
                raise ValueError('ast could not be made safe to parse')

            return None

        return self

    def copy(self, *, decorators: bool = True, safe: bool = False, do_raise: bool = True) -> 'FST':
        if not (loc := self.bloc if decorators else self.loc):
            raise ValueError('cannot copy ast without location')

        lines  = self.root._lines
        indent = self.get_indent()
        ast    = copy(self.a)

        if not decorators and hasattr(ast, 'decorator_list'):
            ast.decorator_list.clear()

        fst = FST(ast, lines=lines, from_=self)  # we use original lines for nodes offset calc before putting new lines

        fst.offset(loc.ln, loc.col, -loc.ln, -lines[loc.ln].c2b(loc.col))

        fst._lines = self.sniploc(*loc)

        fst.touch(True)
        fst.dedent_tail(indent)

        return fst.safe(do_raise=do_raise) if safe else fst










    # mutate()
    # ^^^^^^^^
    # * copy()
    #   cut()
    #   remove()
    #   append()
    #   insert()
    #   replace()




