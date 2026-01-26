"""Core `FST` class methods.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import re
from ast import literal_eval, iter_child_nodes, walk
from io import BytesIO
from tokenize import tokenize as tokenize_tokenize, STRING
from types import EllipsisType, TracebackType
from typing import Iterable, Literal, NamedTuple

from . import fst

from .asttypes import (
    ASTS_LEAF_EXPR_CONTEXT,
    ASTS_LEAF_EXPR_OR_PATTERN,
    ASTS_LEAF_EXPR_CHAIN,
    ASTS_LEAF_STMTLIKE,
    ASTS_LEAF_FUNCDEF,
    ASTS_LEAF_WITH,
    ASTS_LEAF_TUPLE_OR_LIST,
    ASTS_LEAF_CMPOP_TWO_WORD,
    ASTS_LEAF_CMPOP_ONE_WORD,
    ASTS_LEAF_MAYBE_DOCSTR,
    AST,
    AsyncFor,
    AsyncFunctionDef,
    Attribute,
    Call,
    ClassDef,
    Constant,
    Dict,
    DictComp,
    ExceptHandler,
    Expr,
    For,
    FormattedValue,
    FunctionDef,
    GeneratorExp,
    If,
    ImportFrom,
    Interactive,
    JoinedStr,
    List,
    ListComp,
    Match,
    MatchClass,
    MatchMapping,
    MatchSingleton,
    MatchStar,
    MatchValue,
    Module,
    Name,
    Set,
    SetComp,
    Slice,
    Starred,
    Subscript,
    Try,
    Tuple,
    While,
    alias,
    arg,
    arguments,
    boolop,
    cmpop,
    comprehension,
    expr_context,
    keyword,
    match_case,
    mod,
    operator,
    pattern,
    stmt,
    unaryop,
    withitem,
    TryStar,
    TypeAlias,
    type_ignore,
    type_param,
    TemplateStr,
    Interpolation,
    _arglikes,
    _comprehension_ifs,
)

from .astutil import bistr, syntax_ordered_children

from .common import (
    FTSTRING_START_TOKENS,
    FTSTRING_END_TOKENS,
    astfield,
    fstloc,
    nspace,
    pyver,
    re_empty_line,
    re_empty_line_start,
    re_line_continuation,
    re_line_end_cont_or_comment,
    next_find,
    prev_find,
)

from .parsex import _PARSE_MODE_FUNCS


_HAS_FSTR_COMMENT_BUG = f'{"a#b"=}' != '"a#b"=\'a#b\''  # gh-135148

_MODIFYING = {}  # {root: (fst_, count), ...} root nodes of trees being `_Modifying()`ed, to prevent multiple nested modification of different nodes on same tree, same node will be counted and allowed

_astfieldctx = astfield('ctx')

_re_line_end_cont = re.compile(r'[^#]*\\$')  # line ends with line continuation only, not comment and not empty
_re_fval_expr_equals = re.compile(r'(?:\s*(?:#.*|\\)\n)*\s*=\s*(?:(?:#.*|\\)\n\s*)*')  # format string expression tail '=' indicating self-documenting debug str


@pyver(ge=12)
def _get_fmtval_interp_strs(self: fst.FST) -> tuple[str | None, str | None, int, int] | None:
    """Get debug and value strings and location for a `FormattedValue` or `Interpolation` IF THEY ARE PRESENT.
    Meaning that if the `.value` ends with an appropriate `'='` character for debug and the value str if is
    `Interpolation`. This does not check for the presence or equivalence of the actual preceding `Constant` string.
    The returned strings are stripped of comments just like the python parser does.

    **Returns:**
    - `None`: If not a valid debug `FormattedValue` or `Interpolation`.
    - `(debug str, value str, end_ln, end_col)`: A tuple including the full string which includes the `'='`
        character (if applicable, else `None`), a string which only includes the value expression (if Interpolation,
        else `None`) and the end line and column numbers of the whole thing which will correspond to what the
        preceding Constant should have for its end line and column in the case of debug string present.
    """

    ast = self.a
    ast_cls = ast.__class__

    if not (get_val := (ast_cls is Interpolation)):
        if ast_cls is not FormattedValue:
            return None

    lines = self.root._lines
    sln, scol, send_ln, send_col = self.loc
    _, _, vend_ln, vend_col = ast.value.f.pars()

    if fspec := ast.format_spec:
        end_ln, end_col, _, _ = fspec.f.loc
    else:
        end_ln = send_ln
        end_col = send_col - 1

    if ast.conversion != -1:
        if prev := prev_find(lines, vend_ln, vend_col, end_ln, end_col, '!'):
            end_ln, end_col = prev

    src = self._get_src(vend_ln, vend_col, end_ln, end_col)  # source from end of parenthesized value to end of FormattedValue or start of conversion or format_spec
    get_dbg = src and (m := _re_fval_expr_equals.match(src)) and m.end() == len(src)

    if not get_dbg and not get_val:
        return None, None, 0, 0

    if _HAS_FSTR_COMMENT_BUG:  # '#' characters inside strings erroneously removed as if they were comments
        lines = self._get_src(sln, scol + 1, end_ln, end_col, True)

        for i, l in enumerate(lines):
            m = re_line_end_cont_or_comment.search(l)  # always matches

            if (g := m.group(1)) and g.startswith('#'):  # line ends in comment, nuke it
                lines[i] = l[:m.start(1)]

    else:
        lns = set()
        ends = {}  # the starting column of where to search for comment '#', past end of any expression on given line

        for f in (walking := ast.value.f.walk()):  # find multiline continuation line numbers
            fln, _, fend_ln, fend_col = f.loc
            ends[fend_ln] = max(fend_col, ends.get(fend_ln, 0))

            if fend_ln == fln:  # everything on one line, don't need to recurse
                walking.send(False)

            elif (a_cls := f.a.__class__) is Constant:  # isinstance(f.a.value, (str, bytes)) is a given if bend_ln != bln
                lns.update(_multiline_str_continuation_lns(lines, *f.loc))

            elif a_cls in (JoinedStr, TemplateStr):
                lns.update(_multiline_ftstr_continuation_lns(lines, *f.loc))

                walking.send(False)  # skip everything inside regardless, because it is evil

                for a in walk(f.a):  # we walk ourselves to get end-of-expression locations for lines
                    if loc := a.f.loc:
                        _, _, fend_ln, fend_col = loc
                        ends[fend_ln] = max(fend_col, ends.get(fend_ln, 0))

        off = sln + 1
        lns = {v - off for v in lns}  # these are line numbers where comments are not possible because next line is a string continuation
        lines = self._get_src(sln, scol + 1, end_ln, end_col, True)

        for i, l in enumerate(lines):
            if i not in lns:
                c = ends.get(i + sln, 0)

                if not i:  # if first line then need to remove offset of first value from first line of expression
                    c -= scol + 1

                m = re_line_end_cont_or_comment.search(l, c)  # always matches

                if (g := m.group(1)) and g.startswith('#'):  # line ends in comment, nuke it
                    lines[i] = l[:m.start(1)]

    dbg_str = '\n'.join(lines) if get_dbg else None

    if not get_val:
        val_str = None

    else:
        if not (vend_ln := vend_ln - sln):
            vend_col -= scol + 1

        del lines[vend_ln + 1:]

        lines[vend_ln] = lines[vend_ln][:vend_col]

        val_str = '\n'.join(lines).rstrip()

    return dbg_str, val_str, end_ln, end_col

@pyver(lt=12)  # override _get_fmtval_interp_strs if py too low, not used now but for completeness if it is at some point
def _get_fmtval_interp_strs(self: fst.FST) -> tuple[str | None, str | None, int, int] | None:
    """Dummy because py < 3.12 doesn't have f-string location information."""

    return None


@pyver(ge=12)
class _Modifying:
    """Modification context manager. Updates some parent stuff after a successful modification."""

    root:  fst.FST
    fst:   fst.FST | Literal[False]  # False indicates nothing to update on done()
    field: astfield
    data:  list

    def __init__(self, fst_: fst.FST, field: str | Literal[False] = False, raw: bool | None = False) -> None:
        """Call before modifying `FST` node (even just source) to mark possible data for updates after modification.
        `.success()` should be called on a successful modification. Can be used as a context manager or can just call
        `.enter()`, `.success()` and `.fail()` manually.

        It is assumed that neither the `fst_` node passed in (or its parent if `field=False`) nor its parents will be
        changed, otherwise this must be used manually and not as a context manager and the changed node must be passed
        into the `.success()` method on success. In this case currently no parents are updated as it is assumed the
        changes are due to raw reparse which goes up to the statement level and would thus include any modifications
        this class would make.

        **Parameters:**
        - `fst_`: Parent of or actual node being modified, depending on value of `field` (because actual child may be
            being created and may not exist yet).
        - `field`: Name of field being modified or `False` to indicate that `self` is the child, in which case the
            parent and field will be gotten from `self`.
        - `raw`: Whether this is going to be a raw modification or not. Special value of `None` is an override for
            python version < 3.12 to allow the modification, used for specical case of `put_src(action='offset'`).
        """

        self._params = fst_, field, raw

    def __enter__(self) -> '_Modifying':
        return self.enter()

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool:
        if exc_type is None:
            self.success()
        else:
            self.fail(exc_val)

        return False

    def enter(self) -> '_Modifying':
        """This is called on manual use and should be called immediately after creating the class to avoid the
        parameters being invalidated by some other modification."""

        fst_, field, raw = self._params
        self.root = root = fst_.root

        if (nesting := _MODIFYING.get(root)) and fst_ is not nesting[0]:
            raise RuntimeError(f'nested modification of different nodes not allowed on {root}')

        if raw:
            self.fst = False

        else:
            if field is False:
                pfield = fst_.pfield

                if fst_ := fst_.parent:
                    field = pfield.name

            if not fst_ or fst_.a.__class__ not in ASTS_LEAF_EXPR_CHAIN:
                fst_ = False

            self.fst = fst_

            if fst_:
                self.field = field
                self.data = data = []  # [(FormattedValue or Interpolation FST, len(dbg_str) or None, bool do val_str), ...]

                while fst_.a.__class__ in ASTS_LEAF_EXPR_CHAIN:
                    parent = fst_.parent
                    pfield = fst_.pfield

                    if field == 'value' and (strs := _get_fmtval_interp_strs(fst_)):  # this will never proc for py < 3.12, in case we ever make this code common
                        dbg_str, val_str, end_ln, end_col = strs

                        if (dbg_str is None
                            or not parent
                            or not (idx := pfield.idx)
                            or (prev := parent.a.values[idx - 1]).__class__ is not Constant
                            or not isinstance(v := prev.value, str)
                            or not v.endswith(dbg_str)
                            or (prevf := prev.f).end_col != end_col
                            or prevf.end_ln != end_ln
                        ):
                            if val_str is not None:
                                data.append((fst_, None, True))
                            elif not data:  # first one always gets put because needs to do other stuff
                                data.append((fst_, None, False))

                        else:
                            data.append((fst_, len(dbg_str), bool(val_str)))

                    if not parent:
                        break

                    field = pfield.name
                    fst_ = parent

        _MODIFYING[root] = (nesting[0], nesting[1] + 1) if nesting else (fst_, 1)

        return self

    def success(self, fst_: fst.FST | None | Literal[False] = False) -> None:
        """Call after modifying `FST` node to apply any needed changes to parents.

        **Parameters:**
        - `fst_`: Parent node of modified field AFTER modification (may have changed or not exist anymore). Or can be
            special value `False` to indicate that original `fst_` was definitely not replaced, with replaced
            referring to the actual `FST` node that might be replaced in a raw reparse, not whether the content
            itself was modified. This is meant for special case use outside of the context manager.
        """

        root = self.root  # should be same as fst_.root if passed in since root node never changes even with raw reparse

        if (nesting := _MODIFYING.get(root))[1] > 1:
            _MODIFYING[root] = (nesting[0], nesting[1] - 1)
        else:
            del _MODIFYING[root]

        if fst_ is False:
            if not (fst_ := self.fst):
                return

        elif fst_ is not self.fst:  # if parent of field changed then entire statement was reparsed and we have nothing to do
            return

        if data := self.data:
            lines = root._lines
            first = data[0]

            for strs in data:
                fst_, len_old_dbg_str, do_val_str = strs

                if strs is first:  # on first one check to make sure no double '{{', and if so then fix: f'{{a}}' -> f'{ {a}}'
                    ln, col, _, _ = fst_.a.value.f.loc
                    fix_const = ((parent := fst_.parent)  # parent should exist here but just in case, whether we need to reset start of debug string or not
                                 and (idx := fst_.pfield.idx)
                                 and (f := parent.a.values[idx - 1].f).col == col
                                 and f.ln == ln)

                    if lines[ln].startswith('{', col):
                        fst_._put_src([' '], ln, col, ln, col, False)

                        if fix_const:
                            f.a.col_offset -= 1

                dbg_str, val_str, end_ln, end_col = _get_fmtval_interp_strs(fst_)

                if do_val_str:
                    fst_.a.str = val_str

                if len_old_dbg_str is not None:
                    c = fst_.parent.a.values[fst_.pfield.idx - 1]
                    c.value = c.value[:-len_old_dbg_str] + dbg_str
                    c.end_lineno = end_ln + 1
                    c.end_col_offset = lines[end_ln].c2b(end_col)

    def fail(self, exc_val: BaseException | None = None) -> None:
        """Parameter `exc_val` not currently used for anything."""

        root = self.root

        if (nesting := _MODIFYING.get(root))[1] > 1:
            _MODIFYING[root] = (nesting[0], nesting[1] - 1)
        else:
            del _MODIFYING[root]


@pyver(lt=12)  # override _Modifying if py too low
class _Modifying:
    """Dummy because py < 3.12 doesn't have f-string location information and we are too lazy to do the work ourself."""

    def __init__(self, fst_: fst.FST, field: str | Literal[False] = False, raw: bool = False) -> None:
        self._params = fst_, field, raw

    def __enter__(self) -> '_Modifying':
        return self.enter()

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool:
        if exc_type is None:
            self.success()
        else:
            self.fail(exc_val)

        return False

    def enter(self) -> '_Modifying':
        fst_, _, raw = self._params
        self.root = root = fst_.root

        if (nesting := _MODIFYING.get(root)) and fst_ is not nesting[0]:
            raise RuntimeError(f'nested modification of different nodes not allowed on {root}')

        if raw is False:
            while (fst_ := fst_.parent) and not isinstance(a := fst_.a, (stmt, pattern, match_case, ExceptHandler)):  # don't allow modification if inside an f-string because before 3.12 they were very fragile
                if a.__class__ is JoinedStr:
                    raise NotImplementedError('put inside JoinedStr not implemented on python < 3.12')

        _MODIFYING[root] = (nesting[0], nesting[1] + 1) if nesting else (fst_, 1)

        return self

    def success(self, fst_: fst.FST | None | Literal[False] = False) -> None:
        root = self.root  # should be same as fst_.root if present since root node never changes

        if (nesting := _MODIFYING.get(root))[1] > 1:
            _MODIFYING[root] = (nesting[0], nesting[1] - 1)
        else:
            del _MODIFYING[root]

    def fail(self, exc_val: BaseException | None = None) -> None:
        root = self.root

        if (nesting := _MODIFYING.get(root))[1] > 1:
            _MODIFYING[root] = (nesting[0], nesting[1] - 1)
        else:
            del _MODIFYING[root]


class _ParamsOffset(NamedTuple):
    """First four parameters to `_offset()` function with the `col_offset` stored as a byte so that `_offset()` doesn't
    need to check the source. This exists in order to facilitate multipart offsetting which changing source code."""

    ln:          int  # position of offset, FST coords (starts at 0)
    col_offset:  int  # NEGATIVE position of offset in BYTES (negative to indicate byte offset but value is abs(), positive would indicate character offset)
    dln:         int  # delta lines
    dcol_offset: int  # delta bytes


def _params_offset(
    lines: list[str], put_lines: list[str], ln: int, col: int, end_ln: int, end_col: int
) -> _ParamsOffset:
    """Calculate location and delta parameters for the `_offset()` function. The `col` parameter is calculated as a byte
    offset so that the `_offset()` function does not have to access the source at all. Explicit `.encode()` is used to
    get byte offsets instead of `bistr` functions so that this function works with lists of just `str`."""

    dfst_ln = len(put_lines) - 1
    dln = dfst_ln - (end_ln - ln)
    col_offset = -len(lines[end_ln][:end_col].encode())  # negative to indicate this is a BYTE and not a CHAR offset, will be used positively
    dcol_offset = len(put_lines[-1].encode()) + col_offset

    if not dfst_ln:
        dcol_offset += len(lines[ln][:col].encode())

    return _ParamsOffset(end_ln, col_offset, dln, dcol_offset)


def _multiline_str_continuation_lns(lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> list[int]:
    """Return the line numbers of a potentially multiline string `Constant` or f or t-string continuation lines (lines
    which should not be indented because their start is part of the string value because they follow a newline inside
    triple quotes or single quoted backslash continued lines). The location passed MUST be from the `Constant`,
    `JoinedStr` or `TemplateStr` `AST` node or calculated to be the same, otherwise this function will fail."""

    lns = []

    if end_ln <= ln:
        return lns

    lines = lines[ln : end_ln + 1]  # crop to just location

    lines[-1] = lines[-1][:end_col]  # parentheses added to avoid at end: `IndentationError: unindent does not match any outer indentation level`
    lines[0] = '(' + lines[0][col:]

    lines.append(')')  # XXX gh-139516 we add this as a separate line and not to the end of the last line because it can help this bug

    tokens = tokenize_tokenize(BytesIO('\n'.join(lines).encode()).readline)

    for token in tokens:
        if (token_type := token.type) == STRING:
            lns.extend(range(token.start[0] + ln, token.end[0] + ln))

        elif token_type in FTSTRING_START_TOKENS:
            start_lineno = token.start[0]
            nesting = 1

            for token in tokens:
                if (token_type := token.type) in FTSTRING_START_TOKENS:
                    nesting += 1

                elif token_type in FTSTRING_END_TOKENS:
                    if not (nesting := nesting - 1):
                        lns.extend(range(start_lineno + ln, token.end[0] + ln))

                        break

            else:
                raise RuntimeError('f or t-string not closed, should not get here, should have gotten tokenize.TokenError')  # pragma: no cover

    return lns


_multiline_ftstr_continuation_lns = _multiline_str_continuation_lns


def _continuation_to_uncontinued_lns(
    lns: Iterable[int], ln: int, col: int, end_ln: int, end_col: int, *, include_last: bool = False
) -> set[int]:
    """Convert `Iterable` of lines which are continued from the immediately previous line into a list of lines which are
    not themselves continued below. If `lns` comes from the `_multiline_?str_*` functions then it does not include line
    continuations outside of the string and those lines will be returned as uncontinued.

    **Parameters:**
    - `include_last`: Whether to include the last line as an uncontinued line or not.

    **Returns:**
    - `set[int]`: Set of uncontinued lines in the given range.
    """

    out = set(range(ln, end_ln + include_last))

    out.difference_update(i - 1 for i in lns)

    return out


def _reparse_docstr_Constants(self: fst.FST, docstr: bool | Literal['strict'] = True) -> None:
    """Reparse docstrings in `self` and all descendants from source into their `Constant` values (because the source has
    changed).

    **Parameters:**
    - `docstr`: Which strings to reparse. `True` means all `Expr` multiline strings. `'strict'` means only multiline
        strings in standard docstring locations. `False` doesn't reparse anything and just returns.
    """

    if docstr is True:
        for a in walk(self.a):
            if a.__class__ is Expr and (v := a.value).__class__ is Constant and isinstance(v.value, str):
                v.value = literal_eval((f := a.f)._get_src(*f.loc))

    elif docstr == 'strict':
        for a in walk(self.a):
            if a.__class__ in ASTS_LEAF_MAYBE_DOCSTR:
                if ((body := a.body)
                    and (b0 := body[0]).__class__ is Expr
                    and (v := b0.value).__class__ is Constant
                    and isinstance(v.value, str)
                ):
                    v.value = literal_eval((f := b0.f)._get_src(*f.loc))


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _make_fst_tree(self: fst.FST, stack: list[fst.FST] | None = None) -> fst.FST:  # -> self
    """Create tree of `FST` nodes, one for each AST node from root. Call only on root or with pre-made stack of nodes
    to walk and make trees for individually. If the `AST`s already have `FST` nodes then those are repurposed in
    `FST()`. In this case the nodes are not removed from whatever previous parent `AST` contained them, that is up to
    the caller.

    **WARNING!** `stack` is consumed.
    """

    if stack is None:
        stack = [self]

    FST = fst.FST

    while stack:
        parent = stack.pop()
        parenta = parent.a

        for field in parenta._fields:  # unrolled iter_child_nodes(parenta) because it makes a difference here
            if child := getattr(parenta, field, None):
                if isinstance(child, AST):
                    if field in ('ctx', 'op'):  # SINGLETON instances from ast.parse() live in these fields
                        if not hasattr(child, 'f'):  # if `.f` exists and points to an FST then this has already been done
                            setattr(parenta, field, child := child.__class__())  # (expr_context, unaryop, operator, boolop, cmpop)  - the same object may be reused by ast.parse() in mutiple places in the tree, we need unique objects (cmpop done below for list field 'ops')

                        FST(child, parent, astfield(field))  # this just creates the FST and adds it to the child AST, we don't add to stack because we know child doesn't have children

                    else:
                        stack.append(FST(child, parent, astfield(field)))

                elif isinstance(child, list):
                    if field != 'ops':  # SINGLETON instances from ast.parse() live in this field
                        if not isinstance(child[0], str):
                            stack.extend(FST(c, parent, astfield(field, i))
                                         for i, c in enumerate(child) if c)  # we know c is an AST or None because only those and strings are in lists and strings were excluded above

                    else:  # field == 'ops', this is the only list field (of Compare.ops) that can contain singleton ASTs
                        for i, c in enumerate(child):
                            if not hasattr(c, 'f'):  # we know isisntance(c, cmpop)
                                child[i] = c = c.__class__()  # is singleton, create unique node

                            FST(c, parent, astfield(field, i))  # no children

    return self


def _unmake_fst_tree(self: fst.FST, stack: list[AST] | None = None) -> fst.FST:  # -> self
    """Destroy a tree of `FST` child nodes by breaking links between AST and `FST` nodes. This mainly helps make sure
    destroyed `FST` nodes can't be reused in a way that might corrupt valid remaining trees.

    Will unmake a tree with possible `.f=None` links without error.

    Unmake exists for two reasons. First it breaks links to make garbage collection easier (which is not really a big
    deal in modern python). More importantly it marks `FST` nodes as invalid.

    **WARNING!** If `stack` is passed then it is consumed.

    **Parameters:**
    - `stack`: Can unmake multiple trees by passing in this. Mostly used for deleted elements in slice operations.
    """

    if stack is None:
        stack = [self.a]

    while stack:  # make sure these bad ASTs can't hurt us anymore
        if a := stack.pop():  # could be `None`s in there
            if f := getattr(a, 'f', None):
                f.a = a.f = None  # parent and pfield are still useful after node has been removed, we want this part to error if a.f is None

            for field in a._fields:  # this is the normal path so we want it to be quick
                if child := getattr(a, field, None):
                    if isinstance(child, AST):
                        stack.append(child)
                    elif isinstance(child, list) and not isinstance(child[0], str):
                        stack.extend(child)

    return self


def _unmake_fst_parents(self: fst.FST, self_: bool = False) -> fst.FST:  # -> self
    """Unmake parent tree from `self` on up, unmaking `self` optionally as well if `self_=True`. This is only meant for
    parent chains of only children because will **NOT** unmake any siblings along the way. It does unmake any `ctx`
    nodes along the way as these are common in parent containers.

    **WARNING!** Unlike `_unmake_fst_tree()`, this function assumes the parent chain (and `self` if that is being
    unmade) are valid `FST` nodes.
    """

    if self_:
        if a := getattr(self, 'a', None):
            a.f = self.a = None

            if a := getattr(a, 'ctx', None) and (f := getattr(a, 'f', None)):
                a.f = f.a = None

    while self := self.parent:
        if a := getattr(self, 'a', None):
            a.f = self.a = None

            if a := getattr(a, 'ctx', None) and (f := getattr(a, 'f', None)):
                a.f = f.a = None

    return self


def _set_ast(self: fst.FST, ast: AST, valid_fst: bool = False, unmake: bool = True) -> fst.FST:  # -> self
    """Set `.a` AST node for this `FST` node and `_make_fst_tree` for `self` if needed (not `valid_fst`), also set ast
    node in parent AST node. Optionally `_unmake_fst_tree()` for old `.a` node according to `unmake`. Returns old `.a`
    node.

    It is the caller's responsibility to remove the `ast` passed in from any other `FST` tree it may have belonged to
    (specifically their parent `AST`), though can be root of its own.

    **WARNING!** If passing `valid_fst=True` the caller is responsible for flushing any location caches of that tree if
    locations change.

    **Parameters:**
    - `valid_fst`: Indicates that the `AST` node is a part of a valid `FST` tree already so that less processing needs
        to be done to integrate it into `self`. We just set `.parent` for all `ast` children `.f` nodes to `self` (don't
        need to set `pfield` because that already references the `ast` correctly).
    - `unmake`: Whether to unmake the `FST` tree being replaced or not. Should really always unmake.

    **Returns:**
    - `self`
    """

    if unmake:
        self._unmake_fst_tree()

        if f := getattr(ast, 'f', None):  # the ast node will be getting self as the FST node so break the link from its previous FST node if any
            f.a = None

    self.a = ast
    ast.f = self

    if not valid_fst:
        self._make_fst_tree()

    else:
        for a in iter_child_nodes(ast):  # this is the price we pay for keeping the current FST when replacing its AST, worth it? Or would be better to use AST FST node if present?
            a.f.parent = self

    if parent := self.parent:
        self.pfield.set(parent.a, ast)

    self._touch()

    return self


def _set_field(
    self: fst.FST, ast_or_list: AST | list[AST] | None, field: str, valid_fst: bool = False, unmake: bool = True
) -> fst.FST:  # -> self
    """Set the given field of this node's `.a` (not the `.a` itself) to the given `ast_or_list` node or list of `AST`
    nodes and `_make_fst_tree` for the new node(s) if needed (not `valid_fst`). Optionally `_unmake_fst_tree()` for old
    field `AST` node or list of nodes. Returns `self` for chaining.

    It is the caller's responsibility to remove the `ast_or_list` or list of `AST`s passed in from any other `FST` tree
    they may have belonged to (specifically their parent `AST`), though can be root(s) of their own. Also for setting
    the proper location for `self.a` as well as parent's obviously.

    **Note:** This does not preserve the current `FST` of a single-element field if setting that.

    **Note:** If changing a list field, the actual list object itself is replaced.

    **WARNING!** If passing `valid_fst=True` the caller is responsible for flushing any location caches of that tree if
    locations change.

    **WARNING!** Needless to say, if replacing a field, it must always be an `AST` or list of `AST`s, no primitives. It
    may contain `None` in place of optional `AST`s.

    **Parameters:**
    - `field`: The field we are replacing.
    - `valid_fst`: Indicates that the `AST` node or list of `AST` nodes is a part of a valid `FST` tree already so that
        less processing needs to be done to integrate it into `self`. We just set `ast_or_list` parent and pfield nodes
        accordingly.
    - `unmake`: Whether to unmake the `FST` tree being replaced or not. Should really always unmake.

    **Returns:**
    - `self`
    """

    ast = self.a
    body = getattr(ast, field)  # AttributeError on purpose

    if isinstance(body, list):
        if unmake:
            self._unmake_fst_tree(body)

        if valid_fst:
            for i, a in enumerate(ast_or_list):
                fst.FST(a, self, astfield(field, i))

        else:
            stack = []

            for i, a in enumerate(ast_or_list):
                if a is not None:
                    stack.append(fst.FST(a, self, astfield(field, i)))

            self._make_fst_tree(stack)

    else:
        if unmake:
            self._unmake_fst_tree([body])

        if ast_or_list is not None:  # can just be deleting a field
            f = fst.FST(ast_or_list, self, astfield(field, None))

            if not valid_fst:
                f._make_fst_tree()

    setattr(ast, field, ast_or_list)

    self._touch()

    return self


def _set_ctx(self: fst.FST, ctx_cls: type[expr_context], stack: list[AST] | None = None) -> None:
    """Set `ctx` field for `self` and children if applicable, else noop. Can be used on `FST` or pure `AST tree. For
    each replaced ctx node, if it has an `FST` node then unmake it and create a new one for the replacement ctx node,
    otherwise just the new `AST` and mark as non-singleton.

    **WARNING!** `stack` is consumed.
    """

    if stack is None:
        stack = [self.a]

    while stack:
        a = stack.pop()
        a_cls = a.__class__

        if ((is_seq := (a_cls in ASTS_LEAF_TUPLE_OR_LIST))
            or (is_single := (a_cls in (Name, Subscript, Attribute)))
            or a_cls is Starred
        ) and (ctx := a.ctx).__class__ is not ctx_cls:
            a.ctx = child = ctx_cls()

            if not (f := getattr(ctx, 'f', None)):
                child.f = None  # mark new ctx as not singleton so that _make_fst_tree() doesn't recreate the node

            else:
                f.a = ctx.f = None  # unmake

                fst.FST(child, a.f, _astfieldctx)  # this just creates the FST and adds it to the child

            if is_seq:
                stack.extend(a.elts)
            elif not is_single:
                stack.append(a.value)


def _set_start_pos(self: fst.FST, lineno: int, col_offset: int, old_lineno: int = -1, old_col_offset: int = -1) -> None:
    """Walk up parent chain setting start position as long as the node is the first child. If `old_lineno` and
    `old_col_offset` are provided then will only set end position as long as it matches this old position. This is
    used in case a child has leading trivia which should be included in the parent, or changing the size of a container
    after put."""

    check_old_pos = old_lineno != -1

    while True:
        if (co := getattr(a := self.a, 'col_offset', None)) is not None:  # maybe an empty `arguments`,
            if check_old_pos and (co != old_col_offset or a.lineno != old_lineno):  # if doesn't end at expected location then we are done
                break

            a.lineno = lineno
            a.col_offset = col_offset

        self._touch()  # even if AST doesn't have location it may be calculated and needs to be cleared out anyway

        if not (parent := self.parent) or self.prev():
            break

        self = parent


def _set_end_pos(
    self: fst.FST, end_lineno: int, end_col_offset: int, old_end_lineno: int = -1, old_end_col_offset: int = -1
) -> None:
    """Walk up parent chain setting end position as long as the node is the last child. If `old_end_lineno` and
    `old_end_col_offset` are provided then will only set end position as long as it matches this old position. This is
    used (among other things) in case a child has trailing trivia which should be included in the parent, like a
    semicolon, or changing the size of a container after put."""

    check_old_pos = old_end_lineno != -1

    while True:
        if (eco := getattr(a := self.a, 'end_col_offset', None)) is not None:  # maybe an empty `arguments`,
            if check_old_pos and (eco != old_end_col_offset or a.end_lineno != old_end_lineno):  # if doesn't end at expected location then we are done
                break

            a.end_lineno = end_lineno
            a.end_col_offset = end_col_offset

        self._touch()  # even if AST doesn't have location it may be calculated and needs to be cleared out anyway

        if not (parent := self.parent) or self.next():
            break

        self = parent


def _is_atom(
    self: fst.FST, *, pars: bool = True, always_enclosed: bool = False
) -> bool | Literal['unenclosable', 'pars']:
    r"""Whether `self` is innately atomic precedence-wise like `Name`, `Constant`, `List`, etc... Or otherwise
    optionally enclosed in parentheses so that it functions as a parsable atom and cannot be split up by precedence
    rules when reparsed.

    Node types where this doesn't normally apply like `stmt` or `alias` return `True`.

    Being atomic precedence-wise does not guarantee parsability as an otherwise atomic node could be spread across
    multiple lines without line continuations or grouping parentheses. In the case that the node is one of these
    (precedence atomic but MAY be split across lines) then `'unenclosable'` is returned (if these nodes are not
    excluded altogether with `always_enclosed=True`). Also see `_is_enclosed_or_line()`.

    If this function returns `'pars'` then `self` is enclosed due to the grouping parentheses.

    **Parameters:**
    - `pars`: Whether to check for grouping parentheses or not for node types which are not innately atomic
        (`NamedExpr`, `BinOp`, `Yield`, etc...). If `True` then `(a + b)` is considered atomic, if `False` then it
        is not.
    - `always_enclosed`: If `True` then will only consider nodes innately atomic which are always enclosed like
        `List` or parenthesized `Tuple`. Nodes which may be split up across multiple lines like `Call` or
        `Attribute` will not be considered atomic and will return `False` unless `pars=True` and grouping
        parentheses present, in which case `'pars'` is returned.

    **Returns:**
    - `True`: Is atomic and no combination of changes in the source will make it parse to a different node.
    - `'unenclosable'`: Is atomic precedence-wise but may be made non-parsable by being spread over multiple lines.
    - `'pars'`: Is atomic due to enclosing grouping parentheses and would not be otherwise, can not be returned for
        `'unenclosable'` nodes if `always_enclosed=False`.
    - `False`: Not atomic.

    **Examples:**

    >>> FST('a')._is_atom()
    True

    >>> FST('a + b')._is_atom()
    False

    >>> FST('(a + b)')._is_atom()
    'pars'

    >>> FST('(a + b)')._is_atom(pars=False)
    False

    >>> FST('a.b')._is_atom()
    'unenclosable'

    >>> FST('a.b')._is_atom(always_enclosed=True)  # because of "a\n.b"
    False

    >>> FST('(a.b)')._is_atom(always_enclosed=True)
    'pars'

    >>> FST('[]')._is_atom(always_enclosed=True)  # because List is always enclosed
    True
    """

    ast = self.a
    ast_cls = ast.__class__

    if isinstance(ast, (List, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp, Name,
                        MatchValue, MatchSingleton, MatchMapping,
                        expr_context, boolop, operator, unaryop, ExceptHandler,
                        stmt, match_case, mod, type_ignore)):
        return True

    if ast_cls in ASTS_LEAF_CMPOP_ONE_WORD:
        return True

    if not always_enclosed:
        if ast_cls is Constant:  # string can be unenclosable because can be implicit and possibly spread over multiple lines (even if not, implicit is still tricky)
            return 'unenclosable' if isinstance(ast.value, (str, bytes)) else True

        if isinstance(ast, (Call, JoinedStr, TemplateStr, Attribute, Subscript,
                            MatchClass, MatchStar,
                            cmpop, comprehension, arguments,
                            arg, keyword, alias, withitem, type_param)):
            return 'unenclosable'

    elif isinstance(ast, (comprehension, arguments, arg, keyword, alias, type_param)):  # can't be parenthesized
        return False

    elif ast_cls is Constant:
        if not isinstance(ast.value, (str, bytes)):  # str and bytes can be multiline implicit needing parentheses
            return True

    elif ast_cls is withitem:  # isn't atom on its own and can't be parenthesized directly but if only has context_expr then take on value of that if starts and ends on same lines
        return (not ast.optional_vars and self.loc[::2] == (ce := ast.context_expr.f).pars()[::2] and
                ce._is_atom(pars=pars, always_enclosed=always_enclosed))

    elif ast_cls in ASTS_LEAF_CMPOP_TWO_WORD:  # could be spread across multiple lines
        return False  # this cannot be parenthesized so just False

    if (ret := self.is_parenthesized_tuple()) is not None:  # if this is False then cannot be enclosed in grouping pars because that would reparse to a parenthesized Tuple and so is inconsistent
        return ret

    if (ret := self.is_delimited_matchseq()) is not None:  # like Tuple, cannot be enclosed in grouping pars
        return bool(ret)

    assert ast_cls in ASTS_LEAF_EXPR_OR_PATTERN

    return 'pars' if pars and self.pars().n else False


def _is_enclosed_or_line(
    self: fst.FST, *, check_pars: bool = True, whole: bool = False, out_lns: set | None = None
) -> bool | Literal['pars']:
    r"""Whether `self` lives on a single line or logical line (entirely terminated with line continuations) or is
    otherwise enclosed in some kind of delimiters `()`, `[]`, `{}` so that it can be parsed without error due to
    being spread across multiple lines. If logical line then internal enclosed elements spread over multiple lines
    without line continuations are fine. This does not mean it can't have other errors, such as a `Slice` outside of
    `Subscript.slice`.

    Node types where this doesn't or can't ever normally apply like `boolop`, `expr_context` or `Name`, etc...
    return `True`. Node types that are not enclosed but which are never used without being enclosed by a parent like
    `Slice`, `keyword` or `type_param` will also return `True`. Other node types which cannot be enclosed
    individually and are not on a single line or not parenthesized and do not have line continuations but would need
    a parent to enclose them like `arguments` (enclosable in `FunctionDef` but unenclosed in a `Lambda`) or the
    `cmpop`s `is not` or `not in` will return `False`.

    Block statements are not done and raise `NotImplementedError`, except for `With` and `AsyncWith`, which only
    check the block header up to the `:` (as common sense would indicate).

    This function does NOT check whether `self` is enclosed by some parent up the tree if it is not enclosed itself,
    for that see `_is_enclosed_in_parents()`.

    **Parameters:**
    - `check_pars`: Whether to check for grouping parentheses or not for nodes which are not enclosed or otherwise
        multiline-safe. Grouping parentheses are different from tuple parentheses which are always checked.
    - `whole`: Whether entire source should be checked and not just the lines corresponding to the node. This is
        only valid for a root node.
    - `out_lns`: If this is not `None` then it is expected to be a `Set` which will get the line numbers added of
        all the lines that would need line continuation backslashes in order to make this function `True`. Any existing
        line numbers already present in this will not be removed.

    **Returns:**
    - `True`: Node is enclosed or single logical line.
    - `'pars'` Enclosed by grouping parentheses (only if other checks fail)
    - `False`: Not enclosed or single logical line and should be parenthesized or put into an enclosed parent or
        have line continuations added for successful parse.

    **Examples:**

    >>> FST('a')._is_enclosed_or_line()
    True

    >>> FST('a + \\\n b')._is_enclosed_or_line()  # because of the line continuation
    True

    >>> FST('(a + \n b)')._is_enclosed_or_line()
    'pars'

    >>> FST('a + \n b')._is_enclosed_or_line()
    False

    >>> FST('[a + \n b]').elts[0]._is_enclosed_or_line()
    False

    >>> FST('[a + \n b]').elts[0]._is_enclosed_in_parents()
    True

    >>> FST('def f(a, b): pass').args._is_enclosed_or_line()
    True

    >>> # because the parentheses belong to the FunctionDef
    >>> FST('def f(a,\n b): pass').args._is_enclosed_or_line()
    False

    >>> FST('def f(a,\n b): pass').args._is_enclosed_in_parents()
    True

    >>> FST('(a is not b)').ops[0]._is_enclosed_or_line()
    True

    >>> FST('(a is \n not b)').ops[0]._is_enclosed_or_line()
    False
    """

    lines = self.root._lines
    ast = self.a
    loc = self.loc

    if whole:
        if not self.is_root:
            raise ValueError("'whole=True' can only be specified on root nodes")

        whole_end_ln = len(lines) - 1

        if loc and not loc.ln and loc.end_ln == whole_end_ln:  # if location spans over whole range of lines then is just normal check
            whole = False

        else:  # if something doesn't have a loc or loc doesn't span over entire range of lines then we need to check the whole source
            end_ln = whole_end_ln
            last_ln = 0
            children = [ast]  # check_pars will be carried out on this first child (self)

    if not whole:
        if not loc:
            return True

        if isinstance(ast, (List, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp,
                            FormattedValue, Interpolation, Name,
                            MatchValue, MatchSingleton, MatchMapping,
                            boolop, operator, unaryop,  # cmpop is not here because of #*^% like 'is \n not'
                            Slice, keyword, type_param,  # these can be unenclosed by themselves but are never used without being enclosed by a parent
                            expr_context, type_ignore)):
            return True

        ast_cls = ast.__class__

        if ast_cls in (Module, Interactive, FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If,
                       Match, Try, TryStar, ExceptHandler, match_case):  # With, AsyncWith not checked because they are handled
            raise NotImplementedError("we don't do block statements yet")  # TODO: this

        ln, col, end_ln, end_col = loc

        if end_ln == ln:
            return True

        if check_pars:
            if self.pars().n:
                return 'pars'

            check_pars = False

        if (is_const := (ast_cls is Constant)) or ast_cls in (JoinedStr, TemplateStr):
            if is_const:
                assert isinstance(ast.value, (str, bytes))  # other types will have end_ln == ln and will have returned above

                lns = _multiline_str_continuation_lns(lines, ln, col, end_ln, end_col)

            else:
                lns = _multiline_ftstr_continuation_lns(lines, ln, col, end_ln, end_col)

            lns = set(lns)

            for i in range(ln, end_ln):  # set any line that follows a line continuation `\` as a continuation (not normally set by _multiline_str_* functions)
                if lines[i].endswith('\\'):  # this is fine whether it is part of string or not
                    lns.add(i + 1)

            if (ret := len(lns) == end_ln - ln) or out_lns is None:
                return ret

            out_lns.update(_continuation_to_uncontinued_lns(lns, ln, col, end_ln, end_col))

            return False

        if (ret := self.is_parenthesized_tuple()) is not None:
            if ret:
                return True

        elif (ret := self.is_delimited_matchseq()) is not None:
            if ret:
                return True

        last_ln = ln
        last_col = col

        if ast_cls is Call:  # these will replace any fields which we know to be enclosed with mock FST nodes which just say the location is enclosed
            children = [ast.func,
                        nspace(f=nspace(pars=lambda: self._loc_Call_pars(),
                                        _is_enclosed_or_line=lambda **kw: True))]

        elif ast_cls is Subscript:
            children = [ast.value,
                        nspace(f=nspace(pars=lambda: self._loc_Subscript_brackets(),
                                        _is_enclosed_or_line=lambda **kw: True))]

        elif ast_cls is ImportFrom:
            pars_names = self._loc_ImportFrom_names_pars()
            children = ([nspace(f=nspace(pars=lambda: pars_names, _is_enclosed_or_line=lambda **kw: True))]
                        if pars_names.n else
                        ast.names)

        elif ast_cls in ASTS_LEAF_WITH:
            pars_items = self._loc_With_items_pars()
            end_ln = pars_items.bound.end_ln
            children = ([nspace(f=nspace(pars=lambda: pars_items, _is_enclosed_or_line=lambda **kw: True))]
                        if pars_items.n else
                        ast.items)

        elif ast_cls is MatchClass:
            children = [ast.cls,
                        nspace(f=nspace(pars=lambda: self._loc_MatchClass_pars(),
                                        _is_enclosed_or_line=lambda **kw: True))]

        else:  # we don't check always-enclosed statement fields here because statements will never get here
            children = syntax_ordered_children(ast)

    else:
        last_col = 0  # the 0 is an emergency value, should not cause any problems

    failed = False  # this is flagged for return False after process all because user may be requesting all lines which need line continuations

    for child in children:
        if not child or not (loc := (childf := child.f).pars()):
            continue

        if (child_end_ln := loc.end_ln) == last_ln:
            last_col = loc.end_col

            continue

        for ln in range(last_ln, loc.ln):
            if not _re_line_end_cont.match(lines[ln], last_col):
                if out_lns is None:
                    return False

                else:
                    failed = True

                    out_lns.add(ln)

            last_col = 0

        if not getattr(loc, 'n', 0) and not childf._is_enclosed_or_line(check_pars=check_pars, out_lns=out_lns):
            if out_lns is None:
                return False
            else:
                failed = True

        check_pars = False
        last_ln = child_end_ln
        last_col = loc.end_col

    for ln in range(last_ln, end_ln):  # tail
        if not lines[ln].endswith('\\'):
            if out_lns is None:
                return False

            else:
                failed = True

                out_lns.add(ln)

    if failed:
        return False

    return True


def _is_enclosed_in_parents(self: fst.FST, field: str | None = None) -> bool:
    """Whether `self` is enclosed by some parent up the tree. This is different from `_is_enclosed_or_line()` as it
    does not check for line continuations or anyting like that, just enclosing delimiters like from `Call` or
    `FunctionDef` arguments parentheses, `List` brackets, `FormattedValue`, parent grouping parentheses, etc...
    Statements do not generally enclose except for a few parts of things like `FunctionDef.args` or `type_params`,
    `ClassDef.bases`, etc...

    **Parameters:**
    - `field`: This is meant to allow check for nonexistent child which would go into this field of `self`. If this
        is not `None` then `self` is considered the first parent with an imaginary child being checked at `field`.

    **WARNING!** This will not pick up parentheses which belong to `self` and the rules for this can be confusing.
    E.g. in `with (x): pass` the parentheses belong to the variable `x` while `with (x as y): pass` they belong to
    the `with` because `alias`es cannot be parenthesized.

    Will pick up parentheses which belong to `self` if `field` is passed because in that case `self` is considered
    the first parent and we are really considering the node which would live at `field`, whether it exists or not.

    **Examples:**

    >>> FST('1 + 2').left._is_enclosed_in_parents()
    False

    >>> FST('(1 + 2)').left._is_enclosed_in_parents()
    True

    >>> FST('(1 + 2)')._is_enclosed_in_parents()  # because owns the parentheses
    False

    >>> FST('[1 + 2]').elts[0].left._is_enclosed_in_parents()
    True

    >>> FST('[1 + 2]').elts[0]._is_enclosed_in_parents()
    True

    >>> FST('f(1)').args[0]._is_enclosed_in_parents()
    True

    >>> FST('f"{1}"').values[0].value._is_enclosed_in_parents()
    True

    >>> FST('[]')._is_enclosed_in_parents()
    False

    >>> FST('[]')._is_enclosed_in_parents(field='elts')
    True

    >>> FST('with (x): pass').items[0]._is_enclosed_in_parents()
    False

    >>> FST('with (x as y): pass').items[0]._is_enclosed_in_parents()
    True
    """

    if field:
        if field != 'ctx':  # so that the `ctx` of a List is not considered enclosed
            self = nspace(parent=self, pfield=astfield(field))

    elif self.a.__class__ in ASTS_LEAF_EXPR_CONTEXT:  # so that the `ctx` of a List is not considered enclosed
        if not (self := self.parent):
            return False

    while parent := self.parent:
        parenta = parent.a
        parent_cls = parenta.__class__

        if parent_cls in (List, Dict, Set, ListComp, SetComp, DictComp, GeneratorExp,
                          FormattedValue, Interpolation, JoinedStr, TemplateStr,
                          MatchMapping,
                          _arglikes, _comprehension_ifs):  # _arglikes and _comprehension_ifs are considered functionally enclosed because their contents are always used enclosed
            return True

        if parent_cls in ASTS_LEAF_FUNCDEF:
            return self.pfield.name in ('type_params', 'args')

        if parent_cls is ClassDef:
            return self.pfield.name in ('type_params', 'bases', 'keywords')

        if parent_cls is TypeAlias:
            return self.pfield.name == 'type_params'

        if parent_cls is ImportFrom:
            return bool(parent._loc_ImportFrom_names_pars().n)  # we know we are in `names`

        if parent_cls in ASTS_LEAF_WITH:
            return bool(parent._loc_With_items_pars().n)  # we know we are in `items`

        if isinstance(parenta, (stmt, ExceptHandler, match_case, mod, type_ignore)):
            return False

        if parent_cls is Call:
            if self.pfield.name in ('args', 'keywords'):
                return True

        elif parent_cls is Subscript:
            if self.pfield.name == 'slice':
                return True

        elif parent_cls is MatchClass:
            if self.pfield.name in ('patterns', 'kwd_attrs', 'kwd_patterns'):
                return True

        elif (ret := parent.is_parenthesized_tuple()) is not None:
            if ret:
                return True

        elif (ret := parent.is_delimited_matchseq()) is not None:
            if ret:
                return True

        if getattr(parent.pars(), 'n', 0):  # just in case no loc
            return True

        self = parent

    return False


def _get_parse_mode(self: fst.FST) -> str | type[AST] | None:
    r"""Determine the parse mode for this node. This is the extended parse mode as per `Mode`, not the `ast.parse()`
    mode. Returns a mode which is guaranteed to reparse this element (which may be a SPECIAL SLICE) to an exact copy
    of itself. This mode is not guaranteed to be the same as was used to create the `FST`, just guaranteed to be
    able to recreate it. Mostly it just returns the `AST` class name, but in cases where that won't parse to this `FST`
    it will return a specific other parse mode. This is a quick just a check, doesn't verify everything.

    **Returns:**
    - `str`: Parse mode which will reparse source to this node.
    - `None`: If cannot be parsed.

    **Examples:**

    >>> FST('a | b')._get_parse_mode()
    'BinOp'

    >>> FST('a | b', 'pattern')._get_parse_mode()
    'MatchOr'

    >>> FST('except ValueError: pass\nexcept: pass', '_ExceptHandlers')._get_parse_mode()
    '_ExceptHandlers'
    """

    if self.parent:  # not is_root
        raise ValueError('parse mode only makes sense for root nodes')

    ast = self.a
    ast_cls = ast.__class__

    if not _PARSE_MODE_FUNCS.get(ast_cls):
        return None

    if ast_cls is Tuple and (elts := ast.elts):
        if (e0 := elts[0]).__class__ is Starred:
            if len(elts) == 1:
                _, _, ln, col = e0.f.loc
                _, _, end_ln, end_col = self.loc

                if not next_find(self.root._lines, ln, col, end_ln, end_col, ',', True):  # if lone Starred in Tuple with no comma then is expr_slice (py 3.11+), e.g. 'subscript[*THIS_IS_A_TUPLE]'
                    return 'expr_slice'

    return ast_cls.__name__  # otherwise regular parse by AST type is valid


def _get_block_indent(self: fst.FST) -> str:
    r"""Determine proper indentation of node at `stmt` (or other similar) block level at or above `self`. Even if it is
    a continuation or on same line as block header. If indentation is impossible to determine because is solo
    statement on same line as parent block then the current tree default indentation is added to the parent block
    indentation and returned.

    **Returns:**
    - `str`: Entire indentation string for the block this node lives in (not just a single level).

    **Examples:**

    >>> FST('i = 1')._get_block_indent()
    ''

    >>> FST('if 1:\n  i = 1').body[0]._get_block_indent()
    '  '

    >>> FST('if 1: i = 1').body[0]._get_block_indent()
    '    '

    >>> FST('if 1: i = 1; j = 2').body[1]._get_block_indent()
    '    '

    >>> FST('if 1:\n  i = 1\n  j = 2').body[1]._get_block_indent()
    '  '

    >>> FST('if 2:\n    if 1:\n      i = 1\n      j = 2').body[0].body[1]._get_block_indent()
    '      '

    >>> FST('if 1:\n\\\n  i = 1').body[0]._get_block_indent()
    '  '

    >>> FST('if 1:\n \\\n  i = 1').body[0]._get_block_indent()
    ' '
    """

    while (parent := self.parent) and self.a.__class__ not in ASTS_LEAF_STMTLIKE:
        self = parent

    root = self.root
    lines = root._lines
    indent = ''

    while parent:
        f = getattr(parent.a, self.pfield.name)[0].f
        ln, col, _, _ = f.loc
        prev = f.prev()  # there may not be one ("try" at start of module)
        prev_end_ln = prev.end_ln if prev else -2  # -2 so it never hits it
        good_line = ''

        while ln > prev_end_ln and re_empty_line.match(line_start := lines[ln], 0, col):
            end_col = 0 if (preceding_ln := ln - 1) != prev_end_ln else prev.end_col

            if not ln or not re_line_continuation.match((l := lines[preceding_ln]), end_col):
                return (line_start[:col] if col else good_line) + indent

            if col:  # we do this to skip backslashes at the start of line as those are just a noop
                good_line = line_start[:col]

            ln = preceding_ln
            col = len(l) - 1  # was line continuation so last char is '\' and rest should be empty

        indent += root.indent
        self = parent
        parent = self.parent

    return indent


def _get_indentable_lns(
    self: fst.FST, skip: int = 0, *, docstr: bool | Literal['strict'] = True, docstr_strict_exclude: AST | None = None
) -> set[int]:
    r"""Get set of indentable lines within this node.

    **Parameters:**
    - `skip`: The number of lines to skip from the start of this node. Useful for skipping the first line for edit
        operations (since the first line is normally joined to an existing line on add or copied directly from start
        on cut).
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in standard docstring locations are indentable.
    - `docstr_strict_exclude`: Special parameter for excluding non-first elements from `'strict'` `docstr` check even if
        they come first in a slice. Should be the `Expr` of the docstring if excluding.

    **Returns:**
    - `set[int]`: Set of line numbers (zero based) which are sytactically indentable.

    **Examples:**

    >>> FST("def f():\n    i = 1\n    j = 2")._get_indentable_lns()
    {0, 1, 2}

    >>> FST("def f():\n  '''docstr'''\n  i = 1\n  j = 2")._get_indentable_lns()
    {0, 1, 2, 3}

    >>> FST("def f():\n  '''doc\nstr'''\n  i = 1\n  j = 2")._get_indentable_lns()
    {0, 1, 2, 3, 4}

    >>> FST("def f():\n  '''doc\nstr'''\n  i = 1\n  j = 2")._get_indentable_lns(skip=2)
    {2, 3, 4}

    >>> FST("def f():\n  '''doc\nstr'''\n  i = 1\n  j = 2")._get_indentable_lns(docstr=False)
    {0, 1, 3, 4}

    >>> FST("def f():\n  '''doc\nstr'''\n  s = '''multi\nline\nstring'''\n  i = 1")._get_indentable_lns()
    {0, 1, 2, 3, 6}
    """

    strict = docstr == 'strict'
    lines = self.root._lines
    lns = set(range(skip, len(lines))) if self.is_root else set(range(self.bln + skip, self.bend_ln + 1))  # start with all lines indentable and remove multiline strings which are not docstrings

    while (parent := self.parent) and self.a.__class__ not in ASTS_LEAF_STMTLIKE:
        self = parent

    for f in (walking := self.walk()):  # find multiline strings and exclude their unindentable lines
        if f.bend_ln == f.bln:  # everything on one line, don't need to recurse
            walking.send(False)

        elif (a_cls := (a := f.a).__class__) is Constant:  # isinstance(f.a.value, (str, bytes)) is a given if bend_ln != bln
            if not (
                docstr
                and isinstance(a.value, str)  # could be bytes
                and (parent := f.parent)
                and parent.a.__class__ is Expr
                and (
                    not strict
                    or (
                        (grandparent := parent.parent)
                        and parent.pfield == ('body', 0)
                        and grandparent.a.__class__ in ASTS_LEAF_MAYBE_DOCSTR
                        and parent.a is not docstr_strict_exclude
            ))):
                lns.difference_update(_multiline_str_continuation_lns(lines, *f.loc))

        elif a_cls in (JoinedStr, TemplateStr):
            lns.difference_update(_multiline_ftstr_continuation_lns(lines, *f.loc))

            walking.send(False)  # skip everything inside regardless, because it is evil

    return lns


def _modifying(self: fst.FST, field: str | Literal[False] = False, raw: bool | None = False) -> _Modifying:
    """See `_Modifying`."""

    return _Modifying(self, field, raw)


def _touch(self: fst.FST) -> fst.FST:  # -> self
    """AST node was modified, clear out any cached info for this node only."""

    # WARNING!!! If this function is changed then search for "._touch()" in the whole source and update where necessary for changes!!!

    self._cache.clear()

    return self


def _touchall(self: fst.FST, parents: bool = True, self_: bool = True, children: bool = True) -> fst.FST:  # -> self
    """Touch self, parents and children, optionally. Flushes location cache so that changes to `AST` locations will
    get picked up."""

    if children:
        stack = [self.a] if self_ else list(iter_child_nodes(self.a))

        while stack:
            child = stack.pop()

            child.f._cache.clear()  # child.f._touch()
            stack.extend(iter_child_nodes(child))

    elif self_:
        self._cache.clear()  # self._touch()

    if parents:
        parent = self

        while parent := parent.parent:
            parent._cache.clear()  # parent._touch()

    return self


def _offset(
    self: fst.FST,
    ln: int,
    col: int,
    dln: int,
    dcol_offset: int,
    tail: bool | None = False,
    head: bool | None = True,
    exclude: fst.FST | None = None,
    *,
    offset_excluded: bool = True,
    self_: bool = True,
) -> fst.FST:  # -> self
    """Offset `AST` node positions in the tree on or after (ln, col) by (delta line, col_offset) (column byte
    offset).

    This only offsets the positions in the `AST` nodes, doesn't change any text, so make sure that is correct before
    getting any `FST` locations from affected nodes otherwise they will be wrong.

    Other nodes outside this tree might need offsetting so use only on root unless special circumstances.

    If offsetting a zero-length node (which can result from deleting elements of an unparenthesized tuple), both the
    start and end location will be moved according to `tail` and `head` rules if exactly at offset point, see
    "Behavior" below.

    **Parameters:**
    - `ln`: Line of offset point (0 based).
    - `col`: Column of offset point (char index if positive). If this is negative then is treated as a byte offset
        in the line so that the source is not used for calculations (which could be wrong if the source was already
        changed).
    - `dln`: Number of lines to offset everything on or after offset point, can be 0.
    - `dcol_offset`: Column offset to apply to everything ON the offset point line `ln` (in bytes). Columns not on
        line `ln` will not be changed.
    - `tail`: Whether to offset end endpoint if it FALLS EXACTLY AT (ln, col) or not. If `False` then tail will not
        be moved backward if at same location as head and can stop head from moving forward past it if at same
        location. If `None` then can be moved forward with head if head at same location.
    - `head`: Whether to offset start endpoint if it FALLS EXACTLY AT (ln, col) or not. If `False` then head will
        not be moved forward if at same location as tail and can stop tail from moving backward past it if at same
        location. If `None` then can be moved backward with tail if tail at same location.
    - `exclude`: `FST` node to stop recursion at and not go into its children (recursion in siblings will not be
        affected).
    - `offset_excluded`: Whether to apply offset to `exclude`d node or not.
    - `self_`: Whether to offset self or not (will recurse into children regardless unless is `self` is `exclude`).

    **Behavior:**
    ```
    start offset here
            V
        |===|
            |---|
            |        <- special zero length span which doesn't normally exist
    0123456789ABC

    +2, tail=False      -2, tail=False      +2, tail=None       -2, tail=False
        head=True           head=True           head=True           head=None
            V                   V                   V                   V
        |===|               |===|               |===|               |===|
            |---|           |---|                   |---|             |-|
            |                 |.|                     |                 |
    0123456789ABC       0123456789ABC       0123456789ABC       0123456789ABC

    +2, tail=True       -2, tail=True       +2, tail=None       -2, tail=True
        head=True           head=True           head=False          head=None
            V                   V                   V                   V
        |=====|             |=|                 |===|               |=|
            |---|           |---|                 |-----|             |-|
            |               |                     |                 |
    0123456789ABC       0123456789ABC       0123456789ABC       0123456789ABC

    +2, tail=False      -2, tail=False      +2, tail=None       -2, tail=None
        head=False          head=False          head=None           head=None
            V                   V                   V                   V
        |===|               |===|               |===|               |===|
            |-----|             |-|                 |-----|             |-|
            |                   |                   |                   |
    0123456789ABC       0123456789ABC       0123456789ABC       0123456789ABC

    +2, tail=True       -2, tail=True
        head=False          head=False
            V                   V
        |=====|             |=|
            |-----|             |-|
            |.|                 |
    0123456789ABC       0123456789ABC
    ```
    """

    # WARNING! In the inner loop of this function there are two `break` statements with a note to see this warning. This
    # is because here we assume that locations and specifically order of nodes is maintained during editing operations.
    # If that ever fails to be the case then those `break` statements can be changed to `continue` to keep this function
    # working. If they are not changed in this case then some ASTs may not be offset which should. On the other hand, if
    # this expected condition fails to be the case a whole lot of other problems probably bigger than this will pop up.

    if self_:
        stack = [self.a]
    elif self is exclude:
        return
    else:
        stack = syntax_ordered_children(self.a)

    if not dln and not dcol_offset:  # should be after the `self is exclude` early return
        self._touchall()  # this function does double duty as a cache flush in affected area, so if we not gonna walk the tree then we explicitly flush everything below

        return

    lno = ln + 1
    colo = (-col  # yes, -0 to not look up 0
            if col <= 0 else
            (l := ls[ln]).c2b(min(col, len(l)))
            if ln < len(ls := self.root._lines) else
            0x7fffffffffffffff)
    fwd = dln > 0 or (not dln and dcol_offset >= 0)

    fwd_or_head_is_not_False = fwd or head is not False
    tail_is_None_and_head_and_fwd = tail is None and head and fwd
    not_fwd_or_tail_is_not_False = not fwd or tail is not False
    head_is_None_and_tail_and_not_fwd = head is None and tail and not fwd

    stacks = [stack]

    while stacks:
        stack = stacks.pop()

        while stack:
            if not (a := stack.pop()):  # may be None
                continue

            if (f := a.f) is not exclude:
                recurse = a._fields  # this instead of True because it may be empty so no recursion needed, same check
            elif offset_excluded:
                recurse = False
            else:
                continue

            f._cache.clear()  # f._touch()

            if (fend_colo := getattr(a, 'end_col_offset', None)) is not None:
                flno = a.lineno
                fcolo = a.col_offset

                if (fend_lno := a.end_lineno) < lno:
                    break  # no need to walk into something which ends before offset point, all other ASTs assumed to be before so we don't even bother with them, SEE WARNING ABOVE!
                elif fend_lno > lno:
                    a.end_lineno = fend_lno + dln
                elif fend_colo < colo:
                    break  # SEE WARNING ABOVE!

                elif (
                    fend_colo > colo
                    or (tail and (fwd_or_head_is_not_False or fcolo != fend_colo or flno != fend_lno))  # at (ln, col), moving tail allowed and not blocked by head?
                    or (tail_is_None_and_head_and_fwd and fcolo == fend_colo and flno == fend_lno)
                ):  # allowed to be and being moved by head?
                    a.end_lineno = fend_lno + dln
                    a.end_col_offset = fend_colo + dcol_offset

                if flno > lno:
                    if not dln and (not (decos := getattr(a, 'decorator_list', None)) or decos[0].lineno > lno):
                        continue  # no need to walk into something past offset point if line change is 0, don't need to touch either could not have been changed above

                    a.lineno = flno + dln

                elif flno == lno and (
                    fcolo > colo
                    or (
                        fcolo == colo
                        and (
                            (head and (not_fwd_or_tail_is_not_False or fcolo != fend_colo or flno != fend_lno))  # at (ln, col), moving head allowed and not blocked by tail?
                            or (head_is_None_and_tail_and_not_fwd and fcolo == fend_colo and flno == fend_lno)
                ))):  # allowed to be and being moved by tail?
                    a.lineno = flno + dln
                    a.col_offset = fcolo + dcol_offset

            if recurse:
                stacks.append(stack)

                stack = syntax_ordered_children(a)

    self._touchall(True, False, False)

    return self


def _offset_lns(self: fst.FST, lns: set[int] | dict[int, int], dcol_offset: int | None = None) -> None:
    """Offset ast column byte offsets in `lns` by `dcol_offset` if present, otherwise `lns` must be a dict with an
    individual `dcol_offset` per line. Only modifies `AST`, not lines. Does not modify parent locations but
    `touch()`es parents."""

    if dcol_offset is None:  # lns is dict[int, int]
        for a in walk(self.a):
            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                if dcol_offset := lns.get(a.lineno - 1):
                    a.col_offset += dcol_offset

                if dcol_offset := lns.get(a.end_lineno - 1):
                    a.end_col_offset = end_col_offset + dcol_offset

            a.f._touch()

        self._touchall(True, False, False)

    elif dcol_offset:  # lns is set[int] OR dict[int, int] (overriding with a single dcol_offset)
        for a in walk(self.a):
            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                if a.lineno - 1 in lns:
                    a.col_offset += dcol_offset

                if a.end_lineno - 1 in lns:
                    a.end_col_offset = end_col_offset + dcol_offset

            a.f._touch()

        self._touchall(True, False, False)


def _indent_lns(
    self: fst.FST,
    indent: str | None = None,
    lns: set[int] | None = None,
    *,
    skip: int = 1,
    docstr: bool | Literal['strict'] = True,
    docstr_strict_exclude: AST | None = None,
) -> None:
    """Indent all indentable lines specified in `lns` with `indent` and adjust node locations accordingly.

    **WARNING!** This does not offset parent nodes.

    **Parameters:**
    - `indent`: The indentation string to prefix to each indentable line.
    - `lns`: A `set` of lines to apply identation to. If `None` then will be gotten from
        `_get_indentable_lns(skip=skip)`.
    - `skip`: If not providing `lns` then this value is passed to `_get_indentable_lns()`.
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in standard docstring locations are indentable.
    - `docstr_strict_exclude`: Special parameter for excluding non-first elements from `'strict'` `docstr` check even if
        they come first in a slice. Should be the `Expr` of the docstr if excluding.
    """

    if indent == '':
        return

    root = self.root

    if indent is None:
        indent = root.indent

    if lns is None:
        lns = self._get_indentable_lns(skip, docstr=docstr, docstr_strict_exclude=docstr_strict_exclude)

    if not lns:
        return

    lines = root._lines
    dont_offset = set()

    for ln in lns:
        if l := lines[ln]:  # only indent non-empty lines
            lines[ln] = bistr(indent + l)
        else:
            dont_offset.add(ln)

    self._offset_lns(lns - dont_offset if dont_offset else lns, len(indent.encode()))

    _reparse_docstr_Constants(self, docstr)


def _dedent_lns(
    self: fst.FST,
    dedent: str | None = None,
    lns: set[int] | None = None,
    *,
    skip: int = 1,
    docstr: bool | Literal['strict'] = True,
    docstr_strict_exclude: AST | None = None,
) -> None:
    """Dedent all indentable lines specified in `lns` by removing `dedent` prefix and adjust node locations accordingly.
    If cannot dedent entire amount, will dedent as much as possible.

    **WARNING!** This does not offset parent nodes.

    **Parameters:**
    - `dedent`: The indentation string to remove from the beginning of each indentable line (if possible).
    - `lns`: A `set` of lines to apply dedentation to. If `None` then will be gotten from
        `_get_indentable_lns(skip=skip)`.
    - `skip`: If not providing `lns` then this value is passed to `_get_indentable_lns()`.
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in standard docstring locations are indentable.
    - `docstr_strict_exclude`: Special parameter for excluding non-first elements from `'strict'` `docstr` check even if
        they come first in a slice. Should be the `Expr` of the docstr if excluding.
    """

    if dedent == '':
        return

    root = self.root

    if dedent is None:
        dedent = root.indent

    if lns is None:
        lns = self._get_indentable_lns(skip, docstr=docstr, docstr_strict_exclude=docstr_strict_exclude)

    if not lns:
        return

    lines = root._lines
    ldedent = len(dedent)
    dont_offset = set()
    dcol_offsets = None

    def dedented(l: str, ldedent_: int) -> None:
        if dcol_offsets is not None:
            dcol_offsets[ln] = -ldedent_

        return bistr(l[ldedent_:])

    for ln in lns:
        if not (l := lines[ln]):  # don't offset anything on an empty line, normally nothing there but during slicing empty lines may mark start and end of slices
            dont_offset.add(ln)

        else:
            if (l.startswith(dedent)
                or (lempty_start := re_empty_line_start.match(l, 0, 0x7fffffffffffffff).end()) >= ldedent
            ):  # only full dedent non-empty lines which have dedent length leading space
                l = dedented(l, ldedent)

            else:  # inconsistent dedentation, need to do line-by-line offset
                if not dcol_offsets:
                    dcol_offsets = {}

                    for ln2 in lns:
                        if ln2 is ln:
                            break

                        nlindent = -ldedent

                        if ln2 not in dont_offset:
                            dcol_offsets[ln2] = nlindent

                l = dedented(l, lempty_start)

            lines[ln] = l

    if dcol_offsets is not None:
        self._offset_lns(dcol_offsets)
    else:
        self._offset_lns(lns - dont_offset if dont_offset else lns, -ldedent)

    _reparse_docstr_Constants(self, docstr)


def _redent_lns(
    self: fst.FST,
    dedent: str | None = None,
    indent: str | None = None,
    lns: set[int] | None = None,
    *,
    skip: int = 1,
    docstr: bool | Literal['strict'] = True,
    docstr_strict_exclude: AST | None = None,
) -> None:
    """Redent all indentable lines specified in `lns` by removing `dedent` prefix then indenting by `indent` for each
    line and adjust node locations accordingly. The operation is carried out intelligently so that a dedent will not
    be truncated if the following indent would move it off the start of the line. It is also done in one pass so is more
    optimal than `_dedent_lns()` followed by `_indent_lns()`. If cannot dedent entire amount even with indent added,
    will dedent as much as possible just like `_dedent_lns()`.

    **WARNING!** This does not offset parent nodes.

    **Parameters:**
    - `dedent`: The indentation string to remove from the beginning of each indentable line (if possible).
    - `indent`: The indentation string to prefix to each indentable line.
    - `lns`: A `set` of lines to apply dedentation to. If `None` then will be gotten from
        `_get_indentable_lns(skip=skip)`.
    - `skip`: If not providing `lns` then this value is passed to `_get_indentable_lns()`.
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in standard docstring locations are indentable.
    - `docstr_strict_exclude`: Special parameter for excluding non-first elements from `'strict'` `docstr` check even if
        they come first in a slice. Should be the `Expr` of the docstr if excluding.
    """

    root = self.root

    if dedent is None:
        dedent = root.indent
    if indent is None:
        indent = root.indent

    if dedent == indent:
        return
    if not dedent:
        return self._indent_lns(indent, skip=skip, docstr=docstr, docstr_strict_exclude=docstr_strict_exclude)
    if not indent:
        return self._dedent_lns(indent, skip=skip, docstr=docstr, docstr_strict_exclude=docstr_strict_exclude)

    if lns is None:
        lns = self._get_indentable_lns(skip, docstr=docstr, docstr_strict_exclude=docstr_strict_exclude)

    if not lns:
        return

    lines = root._lines
    ldedent = len(dedent)
    lindent = len(indent)
    dredent = lindent - ldedent
    dont_offset = set()
    dcol_offsets = None

    def dedented(l: str, ldedent_: int) -> None:
        if dcol_offsets is not None:
            dcol_offsets[ln] = -ldedent_

        return bistr(l[ldedent_:])

    def redented(l: str, lindent_: int, lempty_start: int) -> None:
        if dcol_offsets is not None:
            dcol_offsets[ln] = dredent

        return bistr(indent[:lindent_] + l[lempty_start:])


    def indented(l: str) -> None:
        if dcol_offsets is not None:
            dcol_offsets[ln] = dredent

        return bistr(indent + l[ldedent:])

    for ln in lns:
        if not (l := lines[ln]):  # don't offset anything on an empty line, normally nothing there but during slicing empty lines may mark start and end of slices
            dont_offset.add(ln)

        else:
            if (l.startswith(dedent)
                or (lempty_start := re_empty_line_start.match(l, 0, 0x7fffffffffffffff).end()) >= ldedent
            ):  # only full dedent non-empty lines which have dedent length leading space
                l = indented(l)
            elif (lindent_ := dredent + lempty_start) >= 0:
                l = redented(l, lindent_, lempty_start)

            else:  # inconsistent dedentation, need to do line-by-line offset
                if not dcol_offsets:
                    dcol_offsets = {}

                    for ln2 in lns:
                        if ln2 is ln:
                            break

                        if ln2 not in dont_offset:
                            dcol_offsets[ln2] = dredent

                l = dedented(l, lempty_start)

            lines[ln] = l

    if dcol_offsets is not None:
        self._offset_lns(dcol_offsets)
    else:
        self._offset_lns(lns - dont_offset if dont_offset else lns, dredent)

    _reparse_docstr_Constants(self, docstr)


def _get_src(self: fst.FST, ln: int, col: int, end_ln: int, end_col: int, as_lines: bool = False) -> str | list[str]:
    r"""Get source at location, without dedenting or any other modification, returned as a string or individual
    lines. The first and last lines are cropped to start `col` and `end_col`.

    Can call on any node in tree to access source for the whole tree.

    **Parameters:**
    - `ln`: Start line of span to get (0 based).
    - `col`: Start column (character) on start line.
    - `end_ln`: End line of span to get (0 based, inclusive).
    - `end_col`: End column (character, exclusive) on end line.
    - `as_lines`: If `False` then source is returned as a single string with embedded newlines. If `True` then
        source is returned as a list of line strings (without newlines).

    **Returns:**
    - `str | list[str]`: A single string or a list of lines if `as_lines=True`. If lines then there are no trailing
        newlines in the individual line strings.
    ```
    """

    lines = self.root._lines

    if as_lines:
        return ([bistr(lines[ln][col : end_col])]  # no real reason for bistr, just to be consistent
                if end_ln == ln else
                [bistr(lines[ln][col:])] + lines[ln + 1 : end_ln] + [bistr(lines[end_ln][:end_col])])
    else:
        return (lines[ln][col : end_col]
                if end_ln == ln else
                '\n'.join([lines[ln][col:]] + lines[ln + 1 : end_ln] + [lines[end_ln][:end_col]]))


def _put_src(
    self: fst.FST,
    src: str | list[str] | None,
    ln: int,
    col: int,
    end_ln: int,
    end_col: int,
    tail: bool | None | EllipsisType = ...,
    head: bool | None = True,
    exclude: fst.FST | None = None,
    *,
    offset_excluded: bool = True,
) -> _ParamsOffset | None:
    """Put or delete new source to currently stored source, optionally offsetting all nodes for the change. Must
    specify `tail` as `True`, `False` or `None` to enable offset of nodes according to source put. `...` ellipsis
    value is used as sentinel for `tail` to mean don't offset. Otherwise `tail` and params which followed are passed
    to `self._offset()` with calculated offset location and deltas.

    The offset location is at the end of the span `(ln, col, end_ln, end_col)` and the `head` and `tail` rules apply to
    this location. The `tail`, `head`, `exclude` and `offset_excluded` parameters are exactly as would be passed to the
    `_offset()` function. Leaving the default `tail` value means no offset is to be done.

    **Note:** Keep in mind that unctions which call this one may count on it second effect through `_offset()` of
    flushing caches.

    **Parameters:**
    - `src`: The source to put as a string or list of lines, or `None` to specify delete.
    - `tail`: This not only specifies the offset treatment of tails which exist exactly at the offset location, but if
        left as default value specifies that no offset is to be done, just put the source.

    **Returns:**
    - `(ln: int, col: int, dln: int, dcol_offset: int) | None`: If `tail` was not `...` then the calculated
        `offset()` parameters are returned for any potential followup offsetting. The `col` parameter in this case
        is returned as a byte offset so that `offset()` doesn't attempt to calculate it from already modified
        source."""

    root = self.root
    lines = root._lines

    if is_del := not src:  # src is None or src == '' or src == [] (even though the last shouldn't be used)
        put_lines = ['']
    elif isinstance(src, str):
        put_lines = src.split('\n')
    else:  # isinstance(src, list)
        put_lines = src

    if tail is ...:
        params_offset = None

    else:
        params_offset = _params_offset(lines, put_lines, ln, col, end_ln, end_col)

        root._offset(*params_offset, tail, head, exclude, offset_excluded=offset_excluded)

    if is_del:  # delete lines
        if end_ln != ln:
            lines[ln : end_ln + 1] = (bistr(lines[ln][:col] + lines[end_ln][end_col:]),)
        elif end_col != col:
            lines[ln] = bistr((l := lines[ln])[:col] + l[end_col:])

    else:  # put lines
        if (nnew_ln := len(put_lines)) == 1:
            if end_ln == ln:  # replace in single line with single or empty line
                lines[ln] = bistr(f'{(l := lines[ln])[:col]}{put_lines[0]}{l[end_col:]}')
            else:  # replace in multiple lines with single or empty line
                lines[ln : end_ln + 1] = (bistr(f'{lines[ln][:col]}{put_lines[0]}{lines[end_ln][end_col:]}'),)

        elif end_ln == ln:  # replace in single line with multiple lines
            lend = bistr(put_lines[-1] + (l := lines[ln])[end_col:])
            lines[ln] = bistr(l[:col] + put_lines[0])
            lines[ln + 1 : ln + 1] = map(bistr, put_lines[1:])
            lines[ln + nnew_ln - 1] = lend

        else:  # replace in multiple lines with multiple lines
            lines[ln] = bistr(lines[ln][:col] + put_lines[0])
            lines[end_ln] = bistr(put_lines[-1] + lines[end_ln][end_col:])
            lines[ln + 1 : end_ln] = map(bistr, put_lines[1:-1])

    return params_offset


def _sanitize(self: fst.FST) -> fst.FST:  # -> self
    """Remove any leading or trailing junk which is not part of the location or parenthesized location of the node."""

    assert not self.parent  # self.is_root

    if not (loc := self.pars()) or loc == self.whole_loc:
        return self

    ln, col, end_ln, end_col = loc
    lines = self._lines

    lines[end_ln] = bistr(lines[end_ln][:end_col])

    del lines[end_ln + 1:]

    if ln or col:
        self._offset(ln, 0, -ln, -lines[ln].c2b(col))  # can do at ln, 0 because it doesn't really matter, we are offsetting everything anyway

        lines[ln] = bistr(lines[ln][col:])

        del lines[:ln]

    return self


def _make_fst_and_dedent(
    self: fst.FST,
    indent: fst.FST | str,
    ast: AST,
    copy_loc: fstloc,
    prefix: str | list[str] | None = None,
    suffix: str | list[str] | None = None,
    put_loc: fstloc | None = None,
    put_lines: list[str] | None = None,
    *,
    docstr: bool | Literal['strict'] = True,
    docstr_strict_exclude: AST | None = None,
) -> tuple[fst.FST, _ParamsOffset]:
    """Make an `FST` from a prepared `AST` and a location in the source of `self` to copy (or cut) from. The copied
    source is dedented and if a cut is being done (`put_loc` is not None) then `put_lines` is put to the source of
    `self`.

    **Returns:**
    - `(new FST, _ParamsOffset of delete if cut else None)`
    """

    if not isinstance(indent, str):
        indent = indent._get_block_indent()

    if suffix and isinstance(prefix, str):
        suffix = suffix.split('\n')

    if not prefix:
        prefix_extra_lns = prefix_col_offset = 0

    else:
        if isinstance(prefix, str):
            prefix = prefix.split('\n')

        prefix_extra_lns = len(prefix) - 1
        prefix_col_offset = len(prefix[-1].encode())

    lines = self.root._lines
    fst_ = fst.FST(ast, lines, None, from_=self, lcopy=False)  # we use original lines for nodes offset calc before putting new lines

    fst_._offset(copy_loc.ln, copy_loc.col,
                 prefix_extra_lns - copy_loc.ln,
                 prefix_col_offset - lines[copy_loc.ln].c2b(copy_loc.col))

    fst_._lines = fst_lines = self._get_src(*copy_loc, True)  # the full source from self has served its purpose, now replace with just the source which is to be returned in the new FST

    if suffix:
        suffix[0] = fst_lines[-1] + suffix[0]
        fst_lines[-1:] = [bistr(l) for l in suffix]

    if prefix:
        prefix[-1] += fst_lines[0]
        fst_lines[:1] = [bistr(l) for l in prefix]

    if indent:
        fst_._dedent_lns(indent, skip=bool(copy_loc.col) + prefix_extra_lns, docstr=docstr,
                         docstr_strict_exclude=docstr_strict_exclude)  # if copy location starts at column 0 then we apply dedent to it as well (preceding comment above or something)

    if put_loc:
        params_offset = self._put_src(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0
    else:
        params_offset = None

    return fst_, params_offset
