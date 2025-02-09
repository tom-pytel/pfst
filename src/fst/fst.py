"""Line continuations suck."""

__all_other__ = None
__all_other__ = set(globals())
from ast import *
from .util import TryStar, TypeVar, ParamSpec, TypeVarTuple, TypeAlias  # for py < 3.12
__all_other__ = set(globals()) - __all_other__

import ast as ast_
import functools
import re
from typing import Any, Callable, Literal, NamedTuple, Optional, Union

from .util import *

__all__ = list(__all_other__ | {
    'FST', 'parse', 'unparse',
})


AST_FIELDS_NEXT: dict[tuple[type[AST], str], str | None] = dict(sum((  # next field name from AST class and current field name
    [] if not fields else
    [((cls, fields[0]), None)] if len(fields) == 1 else
    [((cls, fields[i]), fields[i + 1]) for i in range(len(fields) - 1)] + [((cls, fields[-1]), None)]
    for cls, fields in AST_FIELDS.items()), start=[])
)

AST_FIELDS_NEXT[(Dict, 'keys')]             = 0  # special cases
AST_FIELDS_NEXT[(Dict, 'values')]           = 1
AST_FIELDS_NEXT[(Compare, 'ops')]           = 2
AST_FIELDS_NEXT[(Compare, 'comparators')]   = 3
AST_FIELDS_NEXT[(Compare, 'left')]          = 'comparators'  # black magic juju
AST_FIELDS_NEXT[(MatchMapping, 'keys')]     = 4
AST_FIELDS_NEXT[(MatchMapping, 'patterns')] = 5

AST_FIELDS_PREV: dict[tuple[type[AST], str], str | None] = dict(sum((  # previous field name from AST class and current field name
    [] if not fields else
    [((cls, fields[0]), None)] if len(fields) == 1 else
    [((cls, fields[i + 1]), fields[i]) for i in range(len(fields) - 1)] + [((cls, fields[0]), None)]
    for cls, fields in AST_FIELDS.items()), start=[])
)

AST_FIELDS_PREV[(Dict, 'keys')]             = 0  # special cases
AST_FIELDS_PREV[(Dict, 'values')]           = 1
AST_FIELDS_PREV[(Compare, 'ops')]           = 2
AST_FIELDS_PREV[(Compare, 'comparators')]   = 3
AST_FIELDS_PREV[(MatchMapping, 'keys')]     = 4
AST_FIELDS_PREV[(MatchMapping, 'patterns')] = 5

STATEMENTISH = (stmt, ExceptHandler, match_case)  # always in lists, can not be inside multilines

re_empty_line_start  = re.compile(r'^[ \t]*')    # start of completely empty or space-filled line
re_empty_line        = re.compile(r'^[ \t]*$')   # completely empty or space-filled line
re_line_continuation = re.compile(r'^[^#]*\\$')  # line continuation with backslash not following a comment start '#' (assumed no asts contained in line)


def only_root(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not args[0].is_root:
            raise RuntimeError(f"'{func.__qualname__}' can only be called on the root node")

        return func(*args, **kwargs)

    return wrapper


def parse(source, filename='<unknown>', mode='exec', *args, type_comments=False, feature_version=None, **kwargs):
    return FST.fromsrc(source, filename, mode, *args, type_comments=type_comments, feature_version=feature_version, **kwargs).a


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
    def lines(self) -> list[str] | None:
        if self.is_root:
            return self._lines
        elif loc := self.loc:
            return self.root._lines[loc.ln : loc.end_ln + 1]
        else:
            return None

    @property
    def text(self) -> str | None:
        if self.is_root:
            return '\n'.join(self._lines)
        elif loc := self.loc:
            return '\n'.join(self.sniploc(*loc))
        else:
            return None

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
            if first := self.first_child():
                loc = fstloc(first.bln, first.bcol, (last := self.last_child()).bend_ln, last.bend_col)
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
            f = stack.pop()
            a = f.a

            for name, child in iter_fields(a):
                if isinstance(child, AST):
                    stack.append(FST(child, f, astfield(name)))
                elif isinstance(child, list):
                    stack.extend(FST(a, f, astfield(name, idx))
                                 for idx, a in enumerate(child) if isinstance(a, AST))

    def _offset(self, ln: int, col: int, dln: int, dcol_offset: int, inc: bool = False) -> 'FST':  # -> Self
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

        self.touchup()

        return self

    def _offset_cols(self, dcol_offset: int, lns: set[int]) -> 'FST':  # -> Self
        """Offset ast col byte offsets in `lns` by a delta and return same set of indentable lines.

        Only modifies ast, not lines.
        """

        if dcol_offset:
            for a in walk(self.a):  # now offset columns where it is allowed
                if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                    if a.lineno - 1 in lns:
                        a.col_offset += dcol_offset

                    if a.end_lineno - 1 in lns:
                        a.end_col_offset = end_col_offset + dcol_offset

                a.f.touch()

        self.touchup()

        return self

    def _offset_cols_mapped(self, dcol_offsets: dict[int, int]) -> 'FST':  # -> Self
        """Offset ast col byte offsets by a specific delta per line and return same dict of indentable lines.

        Only modifies ast, not lines.
        """

        for a in walk(self.a):  # now offset columns where it is allowed
            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                if (dcol_offset := dcol_offsets.get(a.lineno - 1)) is not None:
                    a.col_offset += dcol_offset

                if (dcol_offset := dcol_offsets.get(a.end_lineno - 1)) is not None:
                    a.end_col_offset = end_col_offset + dcol_offset

            a.f.touch()

        self.touchup()

        return self

    def _indent_tail(self, indent: str) -> set[int]:
        """Indent all indentable lines past the first one according with `indent` and adjust node locations accordingly.
        Does not modify node columns on first line."""

        if not (lns := self.get_indentable_lns()) or not indent:
            return lns

        self._offset_cols(len(indent.encode()), lns)

        lines = self.root._lines

        for ln in lns:
            if l := lines[ln]:  # only indent non-empty lines
                lines[ln] = bistr(indent + l)

        return lns

    def _dedent_tail(self, indent: str) -> set[int]:
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
                if l.startswith(indent) or (lempty_start := re_empty_line_start.match(l).end()) >= lindent:
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
            self._offset_cols_mapped(dcol_offsets)
        else:
            self._offset_cols(-lindent, lns)

        return lns

    # ------------------------------------------------------------------------------------------------------------------

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

    def __repr__(self) -> str:
        tail = self._repr_tail()
        rast = repr(self.a)

        return f'<fst{rast[4 : -1]}{tail}>' if rast.startswith('<') else f'fst.{rast[:-1]}{tail})'

    @staticmethod
    def fromsrc(source: str | bytes | list[str], filename: str = '<unknown>', mode: str = 'exec', *,
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
    def fromast(ast: AST, *, calc_loc: bool | Literal['copy'] = True,
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

    def next(self, loc: bool = True) -> Union['FST', None]:
        """Get next sibling in syntactic order. If `loc` is `True` (default) then only ASTs with locations returned.
        Returns `None` if last valid sibling in parent.
        """

        if not (parent := self.parent):
            return None

        parenta   = parent.a
        name, idx = self.pfield

        while True:
            next = AST_FIELDS_NEXT[(parenta.__class__, name)]

            if isinstance(next, int):  # special case?
                while True:
                    match next:
                        case 0:  # from Dict.keys
                            next = 1

                            if not (a := getattr(parenta, 'values')[idx]):
                                continue

                        case 1:  # from Dict.values
                            next = 0

                            try:
                                if not (a := getattr(parenta, 'keys')[(idx := idx + 1)]):
                                    continue
                            except IndexError:
                                return None

                        case 2:  # from Compare.ops
                            next = 3

                            if not (a := getattr(parenta, 'comparators')[idx]):
                                continue

                        case 3:  # from Compare.comparators
                            next = 2

                            try:
                                if not (a := getattr(parenta, 'ops')[(idx := idx + 1)]):
                                    continue
                            except IndexError:
                                return None

                        case 4:  # from MatchMapping.keys
                            next = 5

                            if not (a := getattr(parenta, 'patterns')[idx]):
                                continue

                        case 5:  # from MatchMapping.patterns
                            next = 4

                            try:
                                if not (a := getattr(parenta, 'keys')[(idx := idx + 1)]):
                                    continue
                            except IndexError:
                                return None

                    if (f := a.f).loc or not loc:
                        return f

            elif idx is not None:
                sibling = getattr(parenta, name)

                while True:
                    try:
                        if not (a := sibling[(idx := idx + 1)]):  # who knows where a `None` might pop up "next" these days... xD
                            continue

                    except IndexError:
                        break

                    if (f := a.f).loc or not loc:
                        return f

            while next is not None:
                if isinstance(next, str):
                    name = next

                    if isinstance(sibling := getattr(parenta, next, None), AST):  # None because we know about fields from future python versions
                        if (f := sibling.f).loc or not loc:
                            return f

                    elif isinstance(sibling, list) and sibling:
                        idx = -1

                        break

                    next = AST_FIELDS_NEXT[(parenta.__class__, name)]

                    continue

                # non-str next, special case

                match next:
                    case 2:  # from Compare.left
                        name = 'comparators'  # will cause to get .ops[0]
                        idx  = -1

                break

            else:
                break

            continue

        return None

    def prev(self, loc: bool = True) -> Union['FST', None]:
        """Get previous sibling in syntactic order. If `loc` is `True` (default) then only ASTs with locations returned.
        Returns `None` if first valid sibling in parent.
        """

        if not (parent := self.parent):
            return None

        parenta   = parent.a
        name, idx = self.pfield

        while True:
            prev = AST_FIELDS_PREV[(parenta.__class__, name)]

            if isinstance(prev, int):  # special case?
                while True:
                    match prev:
                        case 0:  # from Dict.keys
                            if not idx:
                                return None

                            else:
                                prev = 1

                                if not (a := getattr(parenta, 'values')[(idx := idx - 1)]):
                                    continue

                        case 1:  # from Dict.values
                            prev = 0

                            if not (a := getattr(parenta, 'keys')[idx]):
                                continue

                        case 2:  # from Compare.ops
                            if not idx:
                                prev = 'left'

                                break

                            else:
                                prev = 3

                                if not (a := getattr(parenta, 'comparators')[(idx := idx - 1)]):
                                    continue

                        case 3:  # from Compare.comparators
                            prev = 2

                            if not (a := getattr(parenta, 'ops')[idx]):
                                continue

                        case 4:  # from Keys.keys
                            if not idx:
                                return None

                            else:
                                prev = 5

                                if not (a := getattr(parenta, 'patterns')[(idx := idx - 1)]):
                                    continue

                        case 5:  # from Keys.patterns
                            prev = 4

                            if not (a := getattr(parenta, 'keys')[idx]):
                                continue

                    if (f := a.f).loc or not loc:
                        return f

            else:
                sibling = getattr(parenta, name)

                while idx:
                    if not (a := sibling[(idx := idx - 1)]):
                        continue

                    if (f := a.f).loc or not loc:
                        return f

            while prev is not None:
                if isinstance(prev, str):
                    name = prev

                    if isinstance(sibling := getattr(parenta, prev, None), AST):  # None because could have fields from future python versions
                        if (f := sibling.f).loc or not loc:
                            return f

                    elif isinstance(sibling, list) and (idx := len(sibling)):
                        break

                    prev = AST_FIELDS_PREV[(parenta.__class__, name)]

                    continue

                # non-str prev, special case

                raise RuntimeError('should not get here')  # when entrable special cases from ahead appear in future py versions add them here

                break

            else:
                break

            continue

        return None

    def first_child(self, loc: bool = True) -> Union['FST', None]:
        """Get first child in syntactic order. If `loc` is `True` (default) then only ASTs with locations returned.
        Returns `None` if no valid children.
        """

        for name in AST_FIELDS[(a := self.a).__class__]:
            if (child := getattr(a, name, None)):
                if isinstance(child, AST) and ((f := child.f).loc or not loc):
                    return f

                if isinstance(child, list):
                    for c in child:
                        if isinstance(c, AST) and ((f := c.f).loc or not loc):
                            return f

        return None

    def last_child(self, loc: bool = True) -> Union['FST', None]:
        """Get last child in syntactic order. If `loc` is `True` (default) then only ASTs with locations returned.
        Returns `None` if no valid children.
        """

        for name in reversed(AST_FIELDS[(a := self.a).__class__]):
            if (child := getattr(a, name, None)):
                if isinstance(child, AST) and ((f := child.f).loc or not loc):
                    return f

                if isinstance(child, list):
                    for c in reversed(child):
                        if isinstance(c, AST) and ((f := c.f).loc or not loc):
                            return f

        return None

    def next_child(self, from_child: Union['FST', None], loc: bool = True) -> Union['FST', None]:
        """Meant for simple iteration."""

        return self.first_child(loc) if from_child is None else from_child.next(loc)

    def prev_child(self, from_child: Union['FST', None], loc: bool = True) -> Union['FST', None]:
        """Meant for simple iteration."""

        return self.last_child(loc) if from_child is None else from_child.prev(loc)

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
        return self.sniploc(*self.loc)

    def snip_text(self) -> str:
        return '\n'.join(self.sniploc(*self.loc))

    def get_indent(self) -> str:
        """Determine proper indentation of node at `stmt` (or other similar) level at or above self, otherwise at root
        node. Even if it is a continuation or on same line as block statement."""

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
            self = parent

        lines        = (root := self.root)._lines
        extra_indent = ''  # may result from unknown indent in single line "if something: whats_my_stmt_indentation?"

        while parent:
            siblings = getattr(parent.a, self.pfield.name)

            for i in range(1, len(siblings)):  # first try simple rules for all elements past first one
                self = siblings[i].f

                if re_empty_line.match(line_start := lines[(ln := self.ln)][:self.col]):
                    prev    = self.prev()  # there must be one
                    end_col = 0 if prev.end_ln < (preceding_ln := ln - 1) else prev.end_col

                    if not re_line_continuation.match(lines[preceding_ln][end_col:]):
                        return line_start + extra_indent

            self        = siblings[0].f  # didn't find in siblings[1:], now the special rules for the first one
            ln          = self.ln
            col         = self.col
            prev        = self.prev()  # there may not be one ("try" at start of module)
            prev_end_ln = prev.end_ln if prev else -2

            while ln > prev_end_ln and re_empty_line.match(line_start := lines[ln][:col]):
                end_col = 0 if (preceding_ln := ln - 1) != prev_end_ln else prev.end_col

                if not ln or not re_line_continuation.match((l := lines[preceding_ln])[end_col:]):
                    return line_start + extra_indent

                ln  = preceding_ln
                col = len(l) - 1  # was line continuation so last char is '\' and rest should be empty

            if isinstance(parent, mod):  # otherwise would add extra level of indentation
                break

            extra_indent += root.indent
            self          = parent
            parent        = self.parent

        # TODO: handle possibility of syntactically incorrect but indented root node?

        return extra_indent

        return (l := self.loc) and self.root._lines[l[2]].c2b(l[3])

    def get_indentable_lns(self, skip: int = 1) -> set[int]:
        """Get set of indentable lines (past the first one usually because that is normally handled specially)."""

        lns = set(range(self.bln + skip, self.bend_ln + 1))

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
            self = parent

        for a in walk(self.a):  # find multiline strings and exclude their unindentable lines
            if isinstance(a, Constant) and (isinstance(a.value, (str, bytes))):
                lns -= set(range(a.lineno, a.end_lineno))  # specifically leave first line of multiline string because that is indentable

        return lns

    def get_line_ast_ends(self) -> list[int]:
        """Map of column positions of last AST node on each given line. Useful for checking comments and '\' continuations."""

        root     = self.root
        lines    = root._lines
        lastends = [0] * (root.bend_ln + 1)
        stack    = [root.a]

        while stack:
            lastends[end_ln] = max(lastends[(end_ln := (a := stack.pop()).f.bend_ln)], a.f.bend_col)  # we know end_ln is not None

            if isinstance(a, Constant):
                if isinstance(a.value, (str, bytes)):  # multiline str?
                    for i in range(a.f.ln, a.f.end_ln):  # specifically leave out last line
                        lastends[i] = len(lines[i])

                continue

            for _, child in iter_fields(a):
                if isinstance(child, AST):
                    if child.f.bloc is not None:
                        stack.append(child)

                elif isinstance(child, list):
                    for c in child:
                        if isinstance(c, AST) and c.f.bloc is not None:
                            stack.append(c)

        return lastends

    # ------------------------------------------------------------------------------------------------------------------

    def touch(self) -> 'FST':  # -> Self:
        """AST node was modified, clear out any cached info for this node specifically, call this for each node in walk."""

        try:
            del self._loc, self._bloc  # _bloc only exists if _loc does
        except AttributeError:
            pass

        return self

    def touchall(self) -> 'FST':  # -> Self:
        """AST node and some/all children were modified, clear out any cached info for tree down from this node."""

        for a in walk(self.a):
            a.f.touch()

        return self

    def touchup(self) -> 'FST':  # -> Self:
        """Touch going up the tree so that all containers of modified nodes are up to date."""

        while self := self.parent:
            self.touch()

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
                self._offset(ln, col + 2, 0, -2)

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

        fst._offset(loc.ln, loc.col, -loc.ln, -lines[loc.ln].c2b(loc.col))

        fst._lines = self.sniploc(*loc)

        fst._dedent_tail(indent)

        return fst.safe(do_raise=do_raise) if safe else fst










    # mutate()
    # ^^^^^^^^
    # * copy()
    #   cut()
    #   remove()
    #   append()
    #   insert()
    #   replace()




