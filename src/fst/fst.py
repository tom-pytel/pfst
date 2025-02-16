__all_other__ = None
__all_other__ = set(globals())
from ast import *
__all_other__ = set(globals()) - __all_other__

import ast as ast_
import functools
import re
from typing import Any, Callable, Generator, Literal, NamedTuple, Optional, Union

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

STATEMENTISH            = (stmt, ExceptHandler, match_case)  # always in lists, cannot be inside multilines
STATEMENTISH_OR_STMTMOD = (stmt, ExceptHandler, match_case, Module, Interactive)

re_empty_line_start     = re.compile(r'[ \t]*')    # start of completely empty or space-filled line (from start pos, start of line indentation)
re_empty_line           = re.compile(r'[ \t]*$')   # completely empty or space-filled line (from start pos, start of line indentation)
re_line_continuation    = re.compile(r'[^#]*\\$')  # line continuation with backslash not following a comment start '#' (from start pos, assumed no asts contained in line)

re_oneline_str          = re.compile(r'(?:b|r|rb|br|u|)  (?:  \'(?:\\.|[^\\\'])*?\'  |  "(?:\\.|[^\\"])*?"  )', re.VERBOSE | re.IGNORECASE)  # I f^\\\'])*\'ng hate these!
re_contline_str_start   = re.compile(r'(?:b|r|rb|br|u|)  (\'|")', re.VERBOSE | re.IGNORECASE)
re_contline_str_end_sq  = re.compile(r'(?:\\.|[^\\\'])*?  \'', re.VERBOSE)
re_contline_str_end_dq  = re.compile(r'(?:\\.|[^\\"])*?  "', re.VERBOSE)
re_multiline_str_start  = re.compile(r'(?:b|r|rb|br|u|)  (\'\'\'|""")', re.VERBOSE | re.IGNORECASE)
re_multiline_str_end_sq = re.compile(r'(?:\\.|[^\\])*?  \'\'\'', re.VERBOSE)
re_multiline_str_end_dq = re.compile(r'(?:\\.|[^\\])*?  """', re.VERBOSE)

re_next_code                     = re.compile(r'\s*([^\s#\\]+)')          # next non-space non-continuation non-comment code text, don't look into strings with this!
re_next_code_or_comment          = re.compile(r'\s*([^\s#\\]+|#.*)')      # next non-space non-continuation code or comment text, don't look into strings with this!
re_next_code_or_comment_or_lcont = re.compile(r'\s*([^\s#\\]+|#.*|\\$)')  # next non-space non-continuation code or comment text including logical line end, don't look into strings with this!


class astfield(NamedTuple):
    name: str
    idx:  int | None = None

    def get(self, node: AST) -> Any:
        return getattr(node, self.name) if self.idx is None else getattr(node, self.name)[self.idx]


class fstloc(NamedTuple):
    ln:      int
    col:     int
    end_ln:  int
    end_col: int


class srccode(NamedTuple):
    ln:  int
    col: int
    src: str


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
    if (f := getattr(ast_obj, 'f', None)) and isinstance(f, FST) and f.loc:
        if f.is_root:
            return f.src

        try:
            return f.copy().src
        except Exception:
            pass

    return ast_.unparse(ast_obj)


def _next_code(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, comment: bool = False
               ) -> srccode | None:
    """Get next non-space non-continuation maybe non-comment position. Assuming start pos not inside str or comment.
    Code is not necessarily AST stuff, it can be commas, colons, the 'try' keyword, etc... Code can include multiple
    AST nodes in return str if there are no spaces between them like 'a+b'."""

    re_pat = re_next_code_or_comment if comment else re_next_code

    if end_ln == ln:
        return srccode(ln, m.start(1), m.group(1)) if (m := re_pat.match(lines[ln], col, end_col)) else None

    for i in range(ln, end_ln):
        if m := re_pat.match(lines[i], col):
            return srccode(i, m.start(1), m.group(1))

        col = 0

    if m := re_pat.match(lines[end_ln], 0, end_col):
        return srccode(end_ln, m.start(1), m.group(1))

    return None


def _next_code_lline(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, comment: bool = False
                     ) -> srccode | None:
    """Same rules as `_next_code()` but do not exceed logical line during search."""

    re_pat = re_next_code_or_comment if comment else re_next_code

    if end_ln == ln:
        return srccode(ln, m.start(1), m.group(1)) if (m := re_pat.match(lines[ln], col, end_col)) else None

    for i in range(ln, end_ln):
        if not (m := re_next_code_or_comment_or_lcont.match(lines[i], col)):
            return None

        if (s := m.group(1)).startswith('#'):
            return srccode(i, m.start(1), s) if comment else None

        if not s.startswith('\\'):
            return srccode(i, m.start(1), s)

        col = 0

    if m := re_pat.match(lines[end_ln], 0, end_col):
        return srccode(end_ln, m.start(1), m.group(1))

    return None


def _prev_code(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, comment: bool = False
               ) -> srccode | None:
    """Same rules as `_next_code()` but return the LAST occurance of code or maybe comment in the span."""

    re_pat = re_next_code_or_comment if comment else re_next_code

    def last_match(l, c, ec):
        ret = None

        while m := re_pat.match(l, c, ec):
            if l[(c := (ret := m).end(1)) : c + 1] in '#\\':
                break

        return ret

    if end_ln == ln:
        return srccode(ln, m.start(1), m.group(1)) if (m := last_match(lines[ln], col, end_col)) else None

    for i in range(end_ln, ln, -1):
        if m := last_match(lines[i], 0, end_col):
            return srccode(i, m.start(1), m.group(1))

        end_col = 0x7fffffffffffffff

    if m := last_match(lines[ln], col, end_col):
        return srccode(ln, m.start(1), m.group(1))

    return None


def _slice_fixup_index(ast, body, field, start, stop) -> tuple[int, int]:
    len_body = len(body)

    if start is None:
        start = 0
    elif start < 0:
        start += len_body

    if stop is None:
        stop = len_body
    elif stop < 0:
        stop += len_body

    if start < 0 or start > len_body or stop < 0 or stop > len_body:
        raise IndexError(f"{ast.__class__.__name__}.{field} index out of range")

    return start, stop



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
    def src(self) -> str | None:
        if self.is_root:
            return '\n'.join(self._lines)
        elif loc := self.loc:
            return self.copyl_src(*loc)
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
        return (loc := self.loc) and loc[0] + 1

    @property
    def col_offset(self) -> int:  # byte index
        return (loc := self.loc) and self.root._lines[loc[0]].c2b(loc[1])

    @property
    def end_lineno(self) -> int:  # 1 based
        return (loc := self.loc) and loc[2] + 1

    @property
    def end_col_offset(self) -> int:  # byte index
        return (loc := self.loc) and self.root._lines[loc[2]].c2b(loc[3])

    # ------------------------------------------------------------------------------------------------------------------

    def _make_fst_tree(self) -> 'FST':  # -> Self
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

        return self

    def _repr_tail(self) -> str:
        tail = ' ROOT' if self.is_root else ''
        loc  = self.loc

        return tail + f' {loc[0]},{loc[1]} -> {loc[2]},{loc[3]}' if loc else tail

    def _dump(self, full: bool = False, indent: int = 2, cind: str = '', prefix: str = '', linefunc: Callable = print):
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
                        ast.f._dump(full, indent, cind + ' ' * indent, f'{i}] ', linefunc)
                    else:
                        linefunc(f'{sind}{sind}{cind}{i}] {ast!r}')

            elif isinstance(child, AST):
                child.f._dump(full, indent, cind + sind * 2, '', linefunc)
            else:
                linefunc(f'{sind}{sind}{cind}{child!r}')

    def _dict_key_or_mock_loc(self, key: AST | None, value: 'FST') -> Union['FST', fstloc]:
        """Return same dictionary key FST if exists else create and return a location for the preceding '**' code."""

        if key:
            return key.f

        ln, col, s = _prev_code(self.root._lines, self.ln, self.col, value.ln, value.col)

        assert s.endswith('**')

        return fstloc(ln, col, ln, col + len(s))

    def _maybe_add_singleton_tuple_comma(self) -> 'FST':  # -> Self
        """Maybe add comma to singleton tuple if not already there, parenthesization not checked or taken into account.
        `self` must be a tuple."""

        # assert isinstance(self.a, Tuple)

        if (elts := self.a.elts) and len(elts) == 1:
            felt  = elts[0].f
            root  = self.root
            lines = root._lines

            if (not (code := _next_code(lines, felt.end_ln, felt.end_col, self.end_ln, self.end_col)) or
                not code.src.startswith(',')
            ):
                lines[end_ln]          = bistr(f'{(l := lines[(end_ln := felt.end_ln)])[:(c := felt.end_col)]},{l[c:]}')
                self.a.end_col_offset += 1

                self.touchup(True)

        return self

    def _reparse_docstring(self) -> 'FST':  # -> Self
        """`self` must be something that can have a docstring in the body (function, class, module). Node and source
        lines are assumed to be correct, just the docstring value needs to be reset."""

        # assert isistance(self, (FunctionDef, AsyncFunctionDef, ClassDef, Module))

        if ((body := self.a.body) and isinstance(b0 := body[0], Expr) and isinstance(v := b0.value, Constant) and
            isinstance(v.value, str)
        ):
            v.value = literal_eval(b0.f.copy_src())

        return self

    def _reparse_docstrings(self) -> 'FST':  # -> Self
        """Reparse docstrings in self and all descendants."""

        for a in walk(self.a):
            if isinstance(a, (FunctionDef, AsyncFunctionDef, ClassDef, Module)):
                a.f._reparse_docstring()

    def _offset(self, ln: int, col: int, dln: int, dcol_offset: int, inc: bool = False) -> 'FST':  # -> Self
        """Offset ast node positions in the tree on or after ln / col by delta line / col_offset (col byte offset).

        This only offsets the positions in the AST nodes, doesn't change any text, so make sure that is correct before
        getting any FST locations from affected nodes otherwise they will be wrong.

        Other nodes outside this tree might need offsetting so use only on root unless special circumstances.

        If offsetting a zero-length node (which can result from deleting elements of an unparenthesized tuple), both the
        start and end location will be moved if exactly at offset point if `inc` is `False`. Otherwise if `inc` is
        `True` then the start position will remain and the end position will be expanded.

        Args:
            ln: Line of offset point.
            col: Column of offset point (char index).
            dln: Number of lines to offset everything on or after offset point, can be 0.
            dcol_offset: Column offset to apply to everything ON the offset point line `ln` (in bytes). Columns not on
                this line will not be changed.
            inc: Whether to offset endpoint if it falls exactly at ln / col or not (inclusive).
        """

        for a in walk(self.a):  # TODO: optimize this (don't touch stuff that wasn't moved)
            f = a.f

            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                fln, fcol, fend_ln, fend_col = f.loc

                if fend_ln > ln:
                    a.end_lineno += dln

                elif fend_ln == ln and (
                        fend_col >= col if (inc or (fend_col == fcol and fend_ln == fln)) else fend_col > col):
                    a.end_lineno     += dln
                    a.end_col_offset  = end_col_offset + dcol_offset

                else:
                    continue

                if fln > ln:
                    a.lineno += dln

                elif fln == ln and (
                        fcol >= col if (not (inc or (fend_col == fcol and fend_ln == fln)) or
                                        dln < 0 or (not dln and dcol_offset < 0)) else fcol > col):
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

    def _indentable_lns(self, skip: int = 0, *, docstring: bool = True) -> set[int]:
        """Get set of indentable lines."""

        def walk_multiline(cur_ln, end_ln, m, re_str_end):
            nonlocal lns, lines

            col = m.end(0)

            for ln in range(cur_ln, end_ln + 1):
                if m := re_str_end.match(lines[ln], col):
                    break

                col = 0

            else:
                raise RuntimeError('this should not happen')

            lns -= set(range(cur_ln + 1, ln + 1))  # specifically leave out first line of multiline string because that is indentable

            return ln, m.end(0)

        def multiline_str(f: 'FST'):
            nonlocal lns, lines

            cur_ln, cur_col, end_ln, end_col = f.loc

            while True:
                if not (m := re_multiline_str_start.match(l := lines[cur_ln], cur_col)):
                    if m := re_oneline_str.match(l, cur_col):
                        cur_col = m.end(0)

                    else:  # UGH! a line continuation string, pffft...
                        m               = re_contline_str_start.match(l, cur_col)
                        re_str_end      = re_contline_str_end_sq if m.group(1) == "'" else re_contline_str_end_dq
                        cur_ln, cur_col = walk_multiline(cur_ln, end_ln, m, re_str_end)  # find end of multiline line continuation string

                else:
                    re_str_end      = re_multiline_str_end_sq if m.group(1) == "'''" else re_multiline_str_end_dq
                    cur_ln, cur_col = walk_multiline(cur_ln, end_ln, m, re_str_end)  # find end of multiline string

                if cur_ln == end_ln and cur_col == end_col:
                    break

                cur_ln, cur_col, _ = _next_code(lines, cur_ln, cur_col, end_ln, end_col)  # there must be a next one

        lines = self.root.lines
        lns   = set(range(self.bln + skip, self.bend_ln + 1))

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
            self = parent

        for f in (gen := self.walk()):  # find multiline strings and exclude their unindentable lines
            if isinstance(a := f.a, JoinedStr):  # f-string  TODO: deal with this promordial evil properly at some point, for now just mark all unindentable
                if f.end_ln != f.ln:
                    lns -= set(range(a.lineno, a.end_lineno))

                gen.send(False)  # skip everything inside regardless, because it is evil

            elif isinstance(a, Constant):
                if (f.end_ln != f.ln and (  # and isinstance(f.a.value, (str, bytes)) is a given if end_ln != ln
                    not docstring or
                    not ((parent := f.parent) and  # not (is docstring)
                         isinstance(parent.a, Expr) and (pparent := parent.parent) and parent.pfield == ('body', 0) and
                         isinstance(pparent.a, (FunctionDef, AsyncFunctionDef, ClassDef, Module))
                ))):
                    multiline_str(f)

            elif f.bend_ln == f.bln:
                gen.send(False)  # everything on one line, don't need to recurse

        return lns

    def _indent_tail(self, indent: str, *, docstring: bool = True) -> set[int]:
        """Indent all indentable lines past the first one according with `indent` and adjust node locations accordingly.
        Does not modify node columns on first line."""

        if not (lns := self._indentable_lns(1, docstring=docstring)) or not indent:
            return lns

        self._offset_cols(len(indent.encode()), lns)

        lines = self.root._lines

        for ln in lns:
            if l := lines[ln]:  # only indent non-empty lines
                lines[ln] = bistr(indent + l)

        if docstring:
            self._reparse_docstrings()

        return lns

    def _dedent_tail(self, indent: str, *, docstring: bool = True) -> set[int]:
        """Dedent all indentable lines past the first one by removing `indent` prefix and adjust node locations
        accordingly. Does not modify columns on first line. If cannot dedent entire amount will dedent as much as
        possible.
        """

        if not (lns := self._indentable_lns(1, docstring=docstring)) or not indent:
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

        if docstring:
            self._reparse_docstrings()

        return lns

    def _make_fst_and_dedent(self, findent: 'FST', newast: AST, copy_loc: fstloc, del_loc: fstloc | None = None,
                             prefix: str = '', suffix: str = '') -> 'FST':
        indent = findent.get_indent()
        lines  = self.root._lines
        fst    = FST(newast, lines=lines, from_=self)  # we use original lines for nodes offset calc before putting new lines

        fst._offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix) - lines[copy_loc.ln].c2b(copy_loc.col))  # WARNING! `prefix` is expected to have only 1byte characters

        fst._lines = fst_lines = self.copyl_lines(*copy_loc)

        if suffix:
            fst_lines[-1] = bistr(fst_lines[-1] + suffix)

        if prefix:
            fst_lines[0] = bistr(prefix + fst_lines[0])

        if del_loc:
            self.root._offset(del_loc.end_ln, del_loc.end_col, del_loc.ln - del_loc.end_ln,
                              lines[del_loc.ln].c2b(del_loc.col) - lines[del_loc.end_ln].c2b(del_loc.end_col), True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0
            self.dell_lines(*del_loc)

        fst._dedent_tail(indent)

        return fst

    def _make_Expression_seq_copy_and_dedent(self, newast: AST, cut: bool, lfirst: 'FST', llast: 'FST',
                                             lpre: Union['FST', None], lpost: Union['FST', None],
                                             seq_loc: fstloc, prefix: str, suffix: str) -> 'FST':

        # start of special sauce  # TODO: make this specialer? (specifiable behavior options, prettier multiline handling, etc...)

        lines = self.root._lines

        if not lpre:  # first element in sequence
            copy_ln  = del_ln  = seq_loc.ln
            copy_col = del_col = seq_loc.col

        else:  # not first element in sequence
            copy_ln  = del_ln  = lfirst.ln
            copy_col = del_col = lfirst.col

            if re_empty_line.match(lines[copy_ln], 0, copy_col):
                copy_col = len(lines[(copy_ln := copy_ln - 1)])  # include previous newline as prefix

        if not lpost:  # last element in sequence
            copy_end_ln  = del_end_ln  = seq_loc.end_ln
            copy_end_col = del_end_col = seq_loc.end_col

            if lpre:
                if lfirst.ln == lpre.end_ln:  # only comma between them
                    del_col = lpre.end_col
                if (ln := lfirst.ln) != del_end_ln and re_empty_line.match(lines[ln], 0, lfirst.col):  # expand del_col for better alignment of multiline closing suffix, NOT SURE ABOUT THIS?!?
                    del_col = min(del_col, del_end_col)

        else:  # not last element in sequence
            del_end_ln  = lpost.ln
            del_end_col = lpost.col

            if llast.end_ln == lpost.ln:  # only comma between them
                copy_end_ln  = llast.end_ln
                copy_end_col = llast.end_col

            else:  # preserve formatting newlines and comments
                ln, col, s = _next_code(lines, llast.end_ln, llast.end_col, copy_end_ln := lpost.ln, lpost.col)

                assert s.endswith(',')  # can be preceded by closing non-tuple parentheses

                if ln != copy_end_ln:
                    copy_end_col = re_empty_line_start.match(lines[seq_loc.end_ln], 0, lpost.col).end(0)  # maybe dedent from multiline elements depending on what last line of whole expr does, NOT SURE ABOUT THIS?!?
                else:
                    copy_end_col = col + len(s)  # comma not on last element line but on same line as next past last element, preserve its position

        copy_loc = fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col)

        if not cut:
            del_loc = None
        else:
            del_loc = fstloc(del_ln, del_col, del_end_ln, del_end_col)

        # end of special sauce

        newast.lineno         = copy_ln + 1
        newast.col_offset     = lines[copy_ln].c2b(copy_col)
        newast.end_lineno     = copy_end_ln + 1
        newast.end_col_offset = lines[copy_end_ln].c2b(copy_end_col)

        fst = self._make_fst_and_dedent(self, Expression(body=newast), copy_loc, del_loc, prefix, suffix)

        newast.col_offset     = 0  # before prefix
        newast.end_col_offset = fst._lines[-1].lenbytes  # after suffix

        newast.f.touchup(True)

        return fst

    def _slice_stmt(self, start, stop, field, fix, cut) -> 'FST':
        if cut: raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!

        ast = self.a

        if field is not None:
            if not isinstance(body := getattr(ast, field, None), list):
                raise ValueError(f"invalid {ast.__class__.__name__} field '{field}'")

        elif isinstance(ast, Match):
            field = 'cases'
            body  = ast.cases

        elif (body := getattr(ast, field := 'body', None)) is None or not isinstance(body, list):
            raise ValueError(f"{ast.__class__.__name__} has no 'body' list to slice")

        start, stop = _slice_fixup_index(ast, body, field, start, stop)

        if start == stop:
            return FST(Module(body=[]), lines=[bistr('')], from_=self)

        afirst = body[start]
        loc    = fstloc((f := afirst.f).ln, f.col, (l := body[stop - 1].f.loc).end_ln, l.end_col)
        newast = Module(body=[copy(body[i]) for i in range(start, stop)])

        if (fix and field == 'orelse' and not start and (stop - start) == 1 and afirst.col_offset == ast.col_offset and
            isinstance(ast, If) and isinstance(afirst, If)
        ):  # 'elif' -> 'if'
            newast.body[0].col_offset += 2
            loc                        = fstloc(loc.ln, loc.col + 2, loc.end_ln, loc.end_col)

        fst = self._make_fst_and_dedent(afirst.f, newast, loc)

        return fst

    def _slice_tuple_list_or_set(self, start, stop, fix, cut) -> 'FST':
        ast         = self.a
        elts        = ast.elts
        is_set      = isinstance(ast, Set)
        is_tuple    = not is_set and isinstance(ast, Tuple)
        ctx         = None if is_set else Load() if fix else ast.ctx.__class__()
        start, stop = _slice_fixup_index(ast, elts, 'elts', start, stop)

        if start == stop:
            if is_set:
                return FST(Expression(body=Call(
                    func=Name(id='set', ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=3),
                    args=[], keywords=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=5
                )), lines=[bistr('set()')], from_=self)

            elif is_tuple:
                return FST(Expression(body=Tuple(elts=[], ctx=ctx, lineno=1, col_offset=0, end_lineno=1, end_col_offset=2
                                                 )), lines=[bistr('()')], from_=self)
            else:  # list
                return FST(Expression(body=List(elts=[], ctx=ctx, lineno=1, col_offset=0, end_lineno=1, end_col_offset=2
                                                 )), lines=[bistr('[]')], from_=self)

        is_paren = is_tuple and self.is_tuple_parenthesized()
        lfirst   = elts[start].f
        llast    = elts[stop - 1].f
        lpre     = elts[start - 1].f if start else None
        lpost    = None if stop == len(elts) else elts[stop].f

        if not cut:
            asts = [copy(elts[i]) for i in range(start, stop)]

        else:
            asts = elts[start : stop]

            del elts[start : stop]

            for i in range(start, len(elts)):
                elts[i].f.pfield = astfield('elts', i)

        if is_set:
            newast = Set(elts=asts)  # location will be set later when span is potentially grown
            prefix = '{'
            suffix = '}'

        else:
            newast = ast.__class__(elts=asts, ctx=ctx)

            if fix and not isinstance(ast.ctx, Load):
                set_ctx(newast, Load)

            if is_tuple:
                prefix = '('
                suffix = ')'

            else:  # list
                prefix = '['
                suffix = ']'

        if not is_tuple:
            seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

            assert self.root._lines[self.ln].startswith(prefix, self.col)
            assert self.root._lines[seq_loc.end_ln].startswith(suffix, seq_loc.end_col)

        else:
            if not is_paren:
                seq_loc = self.loc

            else:
                seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

                assert self.root._lines[seq_loc.end_ln].startswith(')', seq_loc.end_col)

        fst = self._make_Expression_seq_copy_and_dedent(newast, cut, lfirst, llast, lpre, lpost, seq_loc, prefix, suffix)

        if is_tuple:
            fst.a.body.f._maybe_add_singleton_tuple_comma()  # maybe need to add a postfix comma to copied single element tuple if is not already there

            if elts:
                self._maybe_add_singleton_tuple_comma()

            else:  # if is unparenthesized tuple and nothing left then need to add parentheses
                if not is_paren:
                    ln, col, end_ln, end_col = self.loc

                    assert ln == end_ln and col == end_col

                    root  = self.root
                    lines = root.lines

                    root._offset(ln, col, 0, 2, True)  # TODO: WARNING! This may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized tuple starts, does this ever happen?
                    self.touchup(True)

                    lines[ln] = bistr(f'{(l := lines[ln])[:col]}(){l[col:]}')

        return fst

    def _slice_dict(self, start, stop, fix, cut) -> 'FST':
        ast         = self.a
        values      = ast.values
        start, stop = _slice_fixup_index(ast, values, 'values', start, stop)

        if start == stop:
            return FST(Expression(body=Dict(keys=[], values=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2
                                            )), lines=[bistr('{}')], from_=self)

        keys   = ast.keys
        lfirst = self._dict_key_or_mock_loc(keys[start], values[start].f)
        llast  = values[stop - 1].f
        lpre   = values[start - 1].f if start else None
        lpost  = None if stop == len(keys) else self._dict_key_or_mock_loc(keys[stop], values[stop].f)

        if not cut:
            akeys   = [copy(keys[i]) for i in range(start, stop)]
            avalues = [copy(values[i]) for i in range(start, stop)]

        else:
            akeys   = keys[start : stop]
            avalues = values[start : stop]

            del keys[start : stop]
            del values[start : stop]

        newast  = Dict(keys=akeys, values=avalues)
        seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

        assert self.root._lines[self.ln].startswith('{', self.col)
        assert self.root._lines[seq_loc.end_ln].startswith('}', seq_loc.end_col)

        return self._make_Expression_seq_copy_and_dedent(newast, cut, lfirst, llast, lpre, lpost, seq_loc, '{', '}')

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
        self._lines = root_params['lines']

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

        return FST(ast, lines=[bistr(s) for s in lines], parse_params=parse_params)

    @staticmethod
    def fromast(ast: AST, *, calc_loc: bool | Literal['copy'] = True,
                type_comments: bool | None = False, feature_version=None, **parse_params) -> 'FST':
        """Add FST to existing AST, optionally copying positions from reparsed AST (default) or whole AST for new FST.

        Do not set `calc_loc` to `False` unless you parsed the `ast` from a previous output of `ast.unparse()`,
        otherwise there will almost certaionly be problems!

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

        return FST(ast, lines=[bistr(s) for s in lines], parse_params=parse_params)

    def verify(self, *, raise_: bool = True) -> Union['FST', None]:  # -> Self | None:
        """Sanity check, make sure parsed source matches ast."""

        root         = self.root
        ast          = root.a
        parse_params = root._parse_params
        astp         = ast_.parse(root.src, mode=get_parse_mode(ast), **parse_params)

        if not isinstance(ast, mod):
            if isinstance(astp, Expression):
                astp = astp.body
            elif len(astp.body) != 1:
                raise ValueError('verify failed reparse')
            else:
                astp = astp.body[0]

        if not compare(astp, ast, locs=True, type_comments=parse_params['type_comments'], raise_=raise_):
            return None

        return self

    def dump(self, full: bool = False, indent: int = 2, print: bool = True) -> list[str] | None:
        if print:
            return self._dump(full, indent)

        lines = []

        self._dump(full, indent, linefunc=lines.append)

        return lines

    # ------------------------------------------------------------------------------------------------------------------

    def next(self, only_with_loc: bool = True) -> Union['FST', None]:
        """Get next sibling in syntactic order. If `only_with_loc` is `True` (default) then only ASTs with locations
        returned. Returns `None` if last valid sibling in parent.
        """

        if not (parent := self.parent):
            return None

        aparent   = parent.a
        name, idx = self.pfield

        while True:
            next = AST_FIELDS_NEXT[(aparent.__class__, name)]

            if isinstance(next, int):  # special case?
                while True:
                    match next:
                        case 0:  # from Dict.keys
                            next = 1

                            if not (a := getattr(aparent, 'values')[idx]):
                                continue

                        case 1:  # from Dict.values
                            next = 0

                            try:
                                if not (a := getattr(aparent, 'keys')[(idx := idx + 1)]):
                                    continue
                            except IndexError:
                                return None

                        case 2:  # from Compare.ops
                            next = 3

                            if not (a := getattr(aparent, 'comparators')[idx]):
                                continue

                        case 3:  # from Compare.comparators
                            next = 2

                            try:
                                if not (a := getattr(aparent, 'ops')[(idx := idx + 1)]):
                                    continue
                            except IndexError:
                                return None

                        case 4:  # from MatchMapping.keys
                            next = 5

                            if not (a := getattr(aparent, 'patterns')[idx]):
                                continue

                        case 5:  # from MatchMapping.patterns
                            next = 4

                            try:
                                if not (a := getattr(aparent, 'keys')[(idx := idx + 1)]):
                                    continue
                            except IndexError:
                                return None

                    if (f := a.f).loc or not only_with_loc:
                        return f

            elif idx is not None:
                sibling = getattr(aparent, name)

                while True:
                    try:
                        if not (a := sibling[(idx := idx + 1)]):  # who knows where a `None` might pop up "next" these days... xD
                            continue

                    except IndexError:
                        break

                    if (f := a.f).loc or not only_with_loc:
                        return f

            while next is not None:
                if isinstance(next, str):
                    name = next

                    if isinstance(sibling := getattr(aparent, next, None), AST):  # None because we know about fields from future python versions
                        if (f := sibling.f).loc or not only_with_loc:
                            return f

                    elif isinstance(sibling, list) and sibling:
                        idx = -1

                        break

                    next = AST_FIELDS_NEXT[(aparent.__class__, name)]

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

    def prev(self, only_with_loc: bool = True) -> Union['FST', None]:
        """Get previous sibling in syntactic order. If `only_with_loc` is `True` (default) then only ASTs with locations
        returned. Returns `None` if first valid sibling in parent.
        """

        if not (parent := self.parent):
            return None

        aparent   = parent.a
        name, idx = self.pfield

        while True:
            prev = AST_FIELDS_PREV[(aparent.__class__, name)]

            if isinstance(prev, int):  # special case?
                while True:
                    match prev:
                        case 0:  # from Dict.keys
                            if not idx:
                                return None

                            else:
                                prev = 1

                                if not (a := getattr(aparent, 'values')[(idx := idx - 1)]):
                                    continue

                        case 1:  # from Dict.values
                            prev = 0

                            if not (a := getattr(aparent, 'keys')[idx]):
                                continue

                        case 2:  # from Compare.ops
                            if not idx:
                                prev = 'left'

                                break

                            else:
                                prev = 3

                                if not (a := getattr(aparent, 'comparators')[(idx := idx - 1)]):
                                    continue

                        case 3:  # from Compare.comparators
                            prev = 2

                            if not (a := getattr(aparent, 'ops')[idx]):
                                continue

                        case 4:  # from Keys.keys
                            if not idx:
                                return None

                            else:
                                prev = 5

                                if not (a := getattr(aparent, 'patterns')[(idx := idx - 1)]):
                                    continue

                        case 5:  # from Keys.patterns
                            prev = 4

                            if not (a := getattr(aparent, 'keys')[idx]):
                                continue

                    if (f := a.f).loc or not only_with_loc:
                        return f

            else:
                sibling = getattr(aparent, name)

                while idx:
                    if not (a := sibling[(idx := idx - 1)]):
                        continue

                    if (f := a.f).loc or not only_with_loc:
                        return f

            while prev is not None:
                if isinstance(prev, str):
                    name = prev

                    if isinstance(sibling := getattr(aparent, prev, None), AST):  # None because could have fields from future python versions
                        if (f := sibling.f).loc or not only_with_loc:
                            return f

                    elif isinstance(sibling, list) and (idx := len(sibling)):
                        break

                    prev = AST_FIELDS_PREV[(aparent.__class__, name)]

                    continue

                # non-str prev, special case

                raise RuntimeError('should not get here')  # when entrable special cases from ahead appear in future py versions add them here

                break

            else:
                break

            continue

        return None

    def first_child(self, only_with_loc: bool = True) -> Union['FST', None]:
        """Get first child in syntactic order. If `only_with_loc` is `True` (default) then only ASTs with locations returned.
        Returns `None` if no valid children.
        """

        for name in AST_FIELDS[(a := self.a).__class__]:
            if (child := getattr(a, name, None)):
                if isinstance(child, AST) and ((f := child.f).loc or not only_with_loc):
                    return f

                if isinstance(child, list):
                    for c in child:
                        if isinstance(c, AST) and ((f := c.f).loc or not only_with_loc):
                            return f

        return None

    def last_child(self, only_with_loc: bool = True) -> Union['FST', None]:
        """Get last child in syntactic order. If `only_with_loc` is `True` (default) then only ASTs with locations returned.
        Returns `None` if no valid children.
        """

        for name in reversed(AST_FIELDS[(a := self.a).__class__]):
            if (child := getattr(a, name, None)):
                if isinstance(child, AST) and ((f := child.f).loc or not only_with_loc):
                    return f

                if isinstance(child, list):
                    for c in reversed(child):
                        if isinstance(c, AST) and ((f := c.f).loc or not only_with_loc):
                            return f

        return None

    def next_child(self, from_child: Union['FST', None], only_with_loc: bool = True) -> Union['FST', None]:
        """Meant for simple iteration."""

        return self.first_child(only_with_loc) if from_child is None else from_child.next(only_with_loc)

    def prev_child(self, from_child: Union['FST', None], only_with_loc: bool = True) -> Union['FST', None]:
        """Meant for simple iteration."""

        return self.last_child(only_with_loc) if from_child is None else from_child.prev(only_with_loc)

    def walk_children(self, only_with_loc: bool = True) -> Generator['FST', bool, None]:
        """Walk descendants in syntactic order, send() `True` to skip recursion into child."""

        child = None

        while child := self.next_child(child, only_with_loc):
            recurse = True

            while (sent := (yield child)) is not None:
                recurse = sent

            if recurse:
                yield from child.walk_children(only_with_loc)

    def walk(self, only_with_loc: bool = True) -> Generator['FST', bool, None]:
        """Walk self and descendants in syntactic order, send() `True` to skip recursion into child."""

        recurse = True

        while (sent := (yield self)) is not None:
            recurse = sent

        if recurse:
            yield from self.walk_children(only_with_loc)

    def is_parsable(self) -> bool:
        """Really means the AST is `unparse()`able and then re`parse()`able which will get it to this top level AST node
        surrounded by the appropriate `ast.mod`. The source may change a bit though, parentheses, 'if' <-> 'elif'."""

        if not self.loc or not is_parsable(self.a):
            return False

        ast    = self.a
        parent = self.parent

        if isinstance(ast, Tuple):  # tuple of slices used in indexing (like numpy)
            for e in ast.elts:
                if isinstance(e, Slice):
                    return False

        elif parent:
            if isinstance(ast, JoinedStr):  # formatspec '.1f' type strings without quote delimiters
                if self.pfield.name == 'format_spec' and isinstance(parent.a, FormattedValue):
                    return False

            elif isinstance(ast, Constant):  # string parts of f-string without quote delimiters
                if self.pfield.name == 'values' and isinstance(parent.a, JoinedStr) and isinstance(ast.value, str):
                    return False

        return True

    def is_parenthesized(self, from_ln: int = 0, from_col: int = 0) -> bool:
        return ((code := _prev_code(self.root._lines, from_ln, from_col, self.ln, self.col)) and code.src.endswith('('))

    def is_tuple_parenthesized(self) -> bool:
        # assert isinstance(self.a, Tuple)

        return (self.root._lines[(ln := self.ln)].startswith('(', col := self.col) and
                (not (e := self.a.elts) or (ln != (f0 := e[0].f).ln or col != f0.col)))

    def copyl_lines(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        if end_ln == ln:
            return [bistr(self.root._lines[ln][col : end_col])]
        else:
            return [bistr((ls := self.root._lines)[ln][col:])] + ls[ln + 1 : end_ln] + [bistr(ls[end_ln][:end_col])]

    def copy_lines(self) -> list[str]:
        return self.copyl_lines(*self.loc)

    def copyl_src(self, ln: int, col: int, end_ln: int, end_col: int) -> str:
        return '\n'.join(self.copyl_lines(ln, col, end_ln, end_col))

    def copy_src(self) -> str:
        return '\n'.join(self.copyl_lines(*self.loc))

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

                if re_empty_line.match(line_start := lines[(ln := self.ln)], 0, col := self.col):
                    prev    = self.prev(True)  # there must be one
                    end_col = 0 if prev.end_ln < (preceding_ln := ln - 1) else prev.end_col

                    if not re_line_continuation.match(lines[preceding_ln], end_col):
                        return line_start[:col] + extra_indent

            self        = siblings[0].f  # didn't find in siblings[1:], now the special rules for the first one
            ln          = self.ln
            col         = self.col
            prev        = self.prev(True)  # there may not be one ("try" at start of module)
            prev_end_ln = prev.end_ln if prev else -2

            while ln > prev_end_ln and re_empty_line.match(line_start := lines[ln], 0, col):
                end_col = 0 if (preceding_ln := ln - 1) != prev_end_ln else prev.end_col

                if not ln or not re_line_continuation.match((l := lines[preceding_ln]), end_col):
                    return line_start[:col] + extra_indent

                ln  = preceding_ln
                col = len(l) - 1  # was line continuation so last char is '\' and rest should be empty

            if isinstance(parent, mod):  # otherwise would add extra level of indentation
                break

            extra_indent += root.indent
            self          = parent
            parent        = self.parent

        # TODO: handle possibility of syntactically incorrect but indented root node?

        return extra_indent

    # ------------------------------------------------------------------------------------------------------------------

    def touch(self) -> 'FST':  # -> Self:
        """AST node was modified, clear out any cached info for this node specifically, call this for each node in walk."""

        try:
            del self._loc, self._bloc  # _bloc only exists if _loc does
        except AttributeError:
            pass

        return self

    def touchup(self, touch_self: bool = False) -> 'FST':  # -> Self:
        """Touch going up the tree so that all containers of modified nodes are up to date."""

        if touch_self:
            self.touch()

        while self := self.parent:
            self.touch()

    def touchall(self, touch_up: bool = True) -> 'FST':  # -> Self:
        """AST node and some/all children were modified, clear out any cached info for tree down from this node."""

        for a in walk(self.a):
            a.f.touch()

        if touch_up:
            self.touchup()

        return self

    def dell_lines(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        ls = self.root._lines

        if end_ln == ln:
            ls[ln] = bistr((l := ls[ln])[:col] + l[end_col:])

        else:
            ls[end_ln] = bistr(ls[ln][:col] + ls[end_ln][end_col:])

            del ls[ln : end_ln]

    def del_lines(self) -> list[str]:
        return self.dell_lines(*self.loc)

    def cutl_lines(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        ls = self.root._lines

        if end_ln == ln:
            ret    = [bistr((l := ls[ln])[col : end_col])]
            ls[ln] = bistr(l[:col] + l[end_col:])

        else:
            ret        = [bistr((l := ls[ln])[col:])] + ls[ln + 1 : end_ln] + [bistr((le := ls[end_ln])[:end_col])]
            ls[end_ln] = bistr(l[:col]) + bistr(le[end_col:])

            del ls[ln : end_ln]

        return ret

    def cut_lines(self) -> list[str]:
        return self.cutl_lines(*self.loc)

    def cutl_src(self, ln: int, col: int, end_ln: int, end_col: int) -> str:
        return '\n'.join(self.cutl_lines(ln, col, end_ln, end_col))

    def cut_src(self) -> str:
        return '\n'.join(self.cutl_lines(*self.loc))

    @only_root
    def fix(self, *, inplace: bool = False) -> Union['FST', None]:  # -> Self | None
        """Correct certain basic changes on cut or copy AST (to make subtrees parsable if the source is not by itself).
        Possibly reparses in order to verify expression. If fails the ast will be unchanged. Is meant to be a quick fix
        after an operation, not full check, for that use `.verify()`. Basically just fixes everything that succeeds
        `.is_parsable()` and set `ctx` to `Load` for expressions.

        Args:
            inplace: If `True` then changes will be made to self. If `False` then self may be returned if no changes
                made otherwise a modified copy is returned.
        """

        if not (loc := self.loc):
            return self

        ln, col, end_ln, end_col = loc

        ast   = self.a
        lines = self._lines

        # if / elif statement

        if isinstance(ast, If):
            if (l := lines[ln]).startswith('if', col):
                return self
            if not l.startswith('elif', col):
                raise ValueError(f'unexpected start of If statement: {l[col:]!r}')

            if not inplace:
                self = FST(copy(ast), lines=(lines := lines[:]), from_=self)

            self._offset(ln, col + 2, 0, -2)

            lines[ln] = bistr((l := lines[ln])[:col] + l[col + 2:])

        # expression maybe parenthesize and proper ctx (Load)

        elif (isinstance(ast, expr)):
            if not self.is_parsable():  # may be Slice or Starred
                return self

            need_paren = None

            if is_tuple := isinstance(ast, Tuple):
                if self.is_tuple_parenthesized():
                    need_paren = False

                elif (not (elts := ast.elts) or any(isinstance(e, NamedExpr) for e in elts) or (len(elts) == 1 and (
                      not (code := _next_code_lline(lines, (f0 := elts[0].f).end_ln, f0.end_col, end_ln, end_col)) or  # if comma not on logical line then definitely need to add parens, if no comma then the parens are incidental but we want that code path
                      not code.src.startswith(',')))):
                    need_paren = True

            elif (isinstance(ast, (Name, List, Set, Dict, ListComp, SetComp, DictComp, GeneratorExp)) or
                  self.is_parenthesized()):
                need_paren = False

            elif isinstance(ast, (NamedExpr, Yield, YieldFrom)):
                need_paren = True

            elif end_ln == ln:
                need_paren = False

            if need_paren is None:
                try:
                    a = ast_.parse(src := self.src, mode='eval', **self._parse_params)

                except SyntaxError:  # if expression not parsing then try parenthesize
                    tail = (',)' if is_tuple and len(ast.elts) == 1 and lines[end_ln][end_col - 1] != ',' else ')')  # TODO: WARNING! this won't work for expressions followed by comments

                    a = ast_.parse(f'({src}{tail}', mode='eval', **self._parse_params)

                    if not inplace:
                        lines = lines[:]

                    lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col]}{tail}{l[end_col:]}')
                    lines[ln]     = bistr(f'{(l := lines[ln])[:col]}({l[col:]}')

                else:
                    if compare(a.body, ast, locs=True, type_comments=True, recurse=False):  # only top level compare needed for `ctx` and structure check
                        return self

                    if not inplace:
                        lines = lines[:]

                a = a.body  # we know parsed to an Expression but original was not an Expression

                if not inplace:
                    return FST(a, lines=lines, from_=self)

                self.a = a
                a.f    = self

                self.touch()
                self._make_fst_tree()

                return self

            need_ctx = set_ctx(ast, Load, doit=False)

            if (need_ctx or need_paren) and not inplace:
                ast   = copy(ast)
                lines = lines[:]
                self  = FST(ast, lines=lines, from_=self)

            if need_ctx:
                set_ctx(ast, Load)

            if need_paren:
                lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col]}){l[end_col:]}')
                lines[ln]     = bistr(f'{(l := lines[ln])[:col]}({l[col:]}')

                self._offset(ln, col, 0, 1)

                if is_tuple:
                    ast.col_offset     -= 1
                    ast.end_col_offset += 1

                self.touch()

                if is_tuple:
                    self._maybe_add_singleton_tuple_comma()

        return self

    def copy(self, *, decorators: bool = True, fix: bool = True) -> 'FST':
        newast = copy(self.a)

        if self.is_root:
            return FST(newast, lines=self._lines[:], from_=self)

        if not (loc := self.bloc if decorators else self.loc):
            raise ValueError('cannot copy ast which does not have location')

        if not decorators and hasattr(newast, 'decorator_list'):
            newast.decorator_list.clear()

        fst = self._make_fst_and_dedent(self, newast, loc)

        return fst.fix(inplace=True) if fix else fst

    def slice(self, start: int | None = None, stop: int | None = None, *, field: str | None = None,
              fix: bool | Literal['mutate'] = True, cut: bool = False) -> 'FST':
        if isinstance(self.a, STATEMENTISH_OR_STMTMOD):
            return self._slice_stmt(start, stop, field, fix, cut)

        if isinstance(self.a, Expression):
            self = self.a.body.f

        if isinstance(self.a, (Tuple, List, Set)):
            return self._slice_tuple_list_or_set(start, stop, fix, cut)

        if isinstance(self.a, Dict):
            return self._slice_dict(start, stop, fix, cut)

        raise ValueError(f"cannot slice a '{self.a.__class__.__name__}'")














    # + copy()
    #   cut()
    # + slice()
    #   remove()
    #   append()
    #   insert()
    #   replace()




