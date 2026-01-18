"""Raw reparse FST methods.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from ast import walk

from . import fst

from .asttypes import (
    ASTS_LEAF_BLOCK,
    ASTS_LEAF_FTSTR,
    AST,
    ExceptHandler,
    Match,
    Pass,
    Slice,
    Try,
    TryStar,
    match_case,
    mod,
    _slice,
)

from .astutil import bistr

from .common import NodeError, astfield

from .parsex import Mode, parse_ExceptHandler, parse_match_case
from .code import Code, _code_as_lines


_STMTLIKE_FIELDS    = frozenset(('body', 'orelse', 'handlers', 'finalbody', 'cases'))

_PATH_BODY          = [astfield('body', 0)]
_PATH_BODY2         = [astfield('body', 0), astfield('body', 0)]
_PATH_BODYORELSE    = [astfield('body', 0), astfield('orelse', 0)]
_PATH_BODY2ORELSE   = [astfield('body', 0), astfield('body', 0), astfield('orelse', 0)]
_PATH_BODYHANDLERS  = [astfield('body', 0), astfield('handlers', 0)]
_PATH_BODY2HANDLERS = [astfield('body', 0), astfield('body', 0), astfield('handlers', 0)]
_PATH_BODYCASES     = [astfield('body', 0), astfield('cases', 0)]


def _reparse_raw_base(
    self: fst.FST,
    new_lines: list[str],
    ln: int,
    col: int,
    end_ln: int,
    end_col: int,
    copy_lines: list[str],
    path: list[astfield] | str | None,
    set_ast: bool = True,
    mode: Mode | None = None,
    first_lineno: int = 0,  # should only be non-zero if we wish to apply column delta to it
    first_line_col_delta: int = 0,
) -> fst.FST:
    """Actually do the reparse. If `mode` is `None` then will just try a normal `'exec'` parse and fail if that fails.
    Otherwise it will try this mode first, then all other parse modes as it is assumed to be a non-top-level
    statementlike thing being reparsed."""

    copy_root = fst.FST(Pass(), copy_lines, None, lcopy=False)  # we don't need the ASTs here, just the lines

    copy_root._put_src(new_lines, ln, col, end_ln, end_col)

    root = self.root

    try:
        copy_root = fst.FST.fromsrc(copy_root.src, mode or 'exec', **root.parse_params)

    except (SyntaxError, NodeError):
        if mode is None or path:  # if there is a path then we expect the top level node to parse to the same thing successfully, if it does not then it is a genuine error
            raise

        try:
            copy_root = fst.FST.fromsrc(copy_root.src, 'all', **root.parse_params)  # root, everything could have changed, try to full reparse
        except Exception as exc:
            raise exc from None

    if not path:  # root
        self._lines = copy_root._lines
        copy = copy_root

    else:
        copy = copy_root.child_from_path(path)

        if not copy:
            raise RuntimeError('could not find node after reparse')  # pragma: no cover

        root._put_src(new_lines, ln, col, end_ln, end_col, True, True, self if set_ast else None)  # we do this again in our own tree to offset our nodes which aren't being moved over from the modified copy, can exclude self if setting ast because it overrides self locations

        copy.pfield.set(copy.parent.a, None)  # remove from copy tree so that copy_root unmake doesn't zero out new node
        copy_root._unmake_fst_tree()

    if first_lineno and first_line_col_delta:  # apply column delta to first line because probably we changed multi-byte characters to single-byte spaces
        for a in walk(copy.a):
            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                if a.end_lineno == first_lineno:
                    a.end_col_offset = end_col_offset + first_line_col_delta

                if a.lineno == first_lineno:
                    a.col_offset += first_line_col_delta

    if set_ast:
        self._set_ast(copy.a, True)
        # self._touchall(True, False, False)  # self already _touch()ed in _set_ast()

    return copy


def _reparse_raw_stmtlike(self: fst.FST, new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> bool:
    """Reparse only statementlike or block header part of statementlike containing changes. We reparse minimum statement
    level due to things like f/t-string debug strings."""

    if not (stmtlike := self.parent_stmtlike(True, False)):
        return False

    if is_elif := stmtlike.is_elif():
        stmtlike = stmtlike.parent  # there must be a parent otherwise it cannot be an `elif`

    pln, pcol, pend_ln, pend_col = stmtlike.bloc

    root = self.root
    lines = root._lines
    stmtlikea = stmtlike.a
    first_lineno = 0  # this indicates not to apply the first column delta, will only be set if we need that action because we possibly erased multi-byte characters on the first line before the reparse node
    first_line_col_delta = lines[pln].c2b(pcol) - pcol

    if in_blkhead := (
        stmtlikea.__class__ in ASTS_LEAF_BLOCK
        and (blkhead_end := stmtlike._loc_block_header_end()[2:]) > (end_ln, end_col + 1)
    ):
        pend_ln, pend_col = blkhead_end

    elif stmtlike is root:  # reparse may include trailing comments which would not otherwise be included
        pend_ln = len(lines) - 1
        pend_col = len(lines[-1])

    stmtlike_cls = stmtlikea.__class__

    if (  # special positional cases
        (is_match_case := (stmtlike_cls is match_case)) and not pcol          # can't reparse match_case at column 0 using the simple method below because needs indent / dedent (no line 0 check because that implies col 0)
        or (is_ExceptHandler := (stmtlike_cls is ExceptHandler)) and not pln  # can't reparse ExceptHandler at line 0 (implies column 0) because needs offsetting
    ):
        copy_lines = ([bistr('')] * pln +
                      lines[pln : pend_ln] +
                      [bistr(lines[pend_ln][:pend_col])])

        if in_blkhead:
            copy_lines.append(bistr('    pass'))

        copy_root = fst.FST(Pass(), copy_lines, None, lcopy=False)   # we only need the FST temporarily so we can _put_src()

        copy_root._put_src(new_lines, ln, col, end_ln, end_col)
        copy_root._unmake_fst_tree()  # be nice and clean up the a <-> f

        copya = (parse_match_case if is_match_case else parse_ExceptHandler)('\n'.join(copy_lines), root.parse_params)  # copy_lines are copy_root._lines since lcopy was False

        if not in_blkhead:  # if not just head then we just put the new source to offset everything maybe around us properly
            root._put_src(new_lines, ln, col, end_ln, end_col, True, True, stmtlike)  # will copy over entire AST so don't need to offset current children of stmtlike

        else:  # if just head then we didn't reparse body so just grab the old one
            root._put_src(new_lines, ln, col, end_ln, end_col, True)  # we offset everything because we will copy over the children

            copya.body = stmtlikea.body
            stmtlikea.body = []  # misc optimization so the body .f don't get unmade since we will be reusing them, TODO: optimize so we don't remake body tree as its already valid

            if not is_match_case:  # match_case doesn't have AST location, we copy because of the replaced body which gives the whole thing a wrong position, the right position was there after the root._put_src() above
                copya.end_lineno = stmtlikea.end_lineno
                copya.end_col_offset = stmtlikea.end_col_offset

        stmtlike._set_ast(copya)
        stmtlike._touchall(True, True, False)

        return True

    # simple parse method is used, we put the source to be reparsed at the same location in an empty source with whatever headers are needed like `try`, `match` or just a generic `if` to allow for indentation

    if is_match_case:
        copy_lines = ([bistr('')] * (pln - 1) +
                      [bistr('match _:')] +
                      lines[pln : pend_ln + 1])
        path = _PATH_BODYCASES

    else:
        indent = stmtlike._get_block_indent()

        if not pcol:  # not 'not indent' because could be semicolon
            copy_lines = [bistr('')] * pln + lines[pln : pend_ln + 1]

        elif pln:
            dpcol = pcol - len(indent)  # this will be negative if the statement is compound and lives on a block header line and the actual start column is before where the extra block indent would have it
            pcol_indent = f'{indent}{" " * dpcol}' if dpcol >= 0 else indent[:dpcol]
            copy_lines = ([bistr('if _:')] +
                          [bistr('')] * (pln - 1) +
                          [bistr(f'{pcol_indent}{lines[pln][pcol:]}')] +
                          lines[pln + 1 : pend_ln + 1])
            first_lineno = pln + 1

        elif (off_after_try := pcol - 4) < 0:
            raise NotImplementedError('degenerate statement starts at (0,1), (0,2) or (0,3)')

        else:  # the `try` is just the shortest block open header, doesn't say anything about the stmt
            copy_lines = ([bistr(f"try:{' ' * off_after_try}{lines[pln][pcol:]}")] +
                          lines[pln + 1 : pend_ln + 1] +
                          [bistr('finally: pass')])
            first_lineno = 1

        if is_ExceptHandler:
            assert pln > bool(indent)

            copy_lines[pln - 1] = bistr(indent + 'try: pass')
            path = _PATH_BODY2HANDLERS if indent else _PATH_BODYHANDLERS

        elif not pcol:  # not 'not indent' because could be semicolon
            if stmtlike.is_elif():
                copy_lines[0] = bistr('if _: pass')
                path = _PATH_BODYORELSE
            else:
                path = _PATH_BODY

        else:
            if stmtlike.is_elif():
                copy_lines[1] = bistr(indent + 'if _: pass')
                path = _PATH_BODY2ORELSE
            else:
                path = _PATH_BODY2

    if not in_blkhead:  # non-block statement or modifications not limited to block header part
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

        _reparse_raw_base(stmtlike, new_lines, ln, col, end_ln, end_col, copy_lines, path, True, None,
                          first_lineno, first_line_col_delta)

        if is_elif:  # nuking a whole elif will parse but can do bad things to end positions
            stmtlike._set_end_pos((a := stmtlike.a).end_lineno, a.end_col_offset)  # setting own position to what it currently is but will also propagate up the tree

        return True

    # modifications only to block header line(s) of block statement

    if stmtlike_cls is Match:
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

        copy_lines.append(bistr(indent + ' case _: pass'))

    else:
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col] + ' pass')

        if stmtlike_cls is Try:  # this is silly, someone is changing just the `try` header, but we cover it
            copy_lines.append(bistr(indent + 'except: pass'))
        elif stmtlike_cls is TryStar:  # ditto
            copy_lines.append(bistr(indent + 'except* Exception: pass'))

    copy = _reparse_raw_base(stmtlike, new_lines, ln, col, end_ln, end_col, copy_lines, path, False, None,
                             first_lineno, first_line_col_delta)
    copya = copy.a

    if not is_match_case:  # match_case doesn't have AST location
        copya.end_lineno = stmtlikea.end_lineno
        copya.end_col_offset = stmtlikea.end_col_offset

    for field in _STMTLIKE_FIELDS:
        if (body := getattr(stmtlikea, field, None)) is not None:
            setattr(copya, field, body)

    stmtlike._set_ast(copya)  # TODO: optimize so we don't remake body trees where theyre already valid
    # stmtlike._touchall(True, False, False)  # self already _touch()ed in _set_ast()

    return True


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _reparse_raw(self: fst.FST, code: Code | None, ln: int, col: int, end_ln: int, end_col: int) -> tuple[int, int]:
    """Reparse this node which entirely contatins the span which is to be replaced with `code` source. `self` must
    be a node which entirely contains the location and is guaranteed not to be deleted. `self` and some of its
    parents going up may be replaced (root node `FST` will never change, the `AST` it points to may though). Not
    safe to use in a `walk()`.

    **Returns:**
    - `(end_ln, end_col)`: New end location of source put (all source after this was not modified).
    """

    new_lines = _code_as_lines(code)

    if not _reparse_raw_stmtlike(self, new_lines, ln, col, end_ln, end_col):  # attempt to reparse only statement (or even only block header), if fails then no statement found above
        root = self.root

        if ((mode := root.a.__class__) is not Slice
            and (base := mode.__bases__[0]) not in (AST, mod, ExceptHandler, _slice)
        ):  # first generalize a bit
            mode = base

        if self is not root and self.parent.a.__class__ in ASTS_LEAF_FTSTR:  # reparsing a direct child of one of these alone is problematic because they may create or destroy self-documenting debug Constant nodes
            self = self.parent

        _reparse_raw_base(self, new_lines, ln, col, end_ln, end_col, root._lines[:],  # fallback to reparse all source
                          None if self is root else root.child_path(self), True, mode)

    if len(new_lines) == 1:
        return ln, col + len(new_lines[0])
    else:
        return ln + len(new_lines) - 1, len(new_lines[-1])
