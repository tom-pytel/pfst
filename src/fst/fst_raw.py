"""Raw reparse FST methods.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

from . import fst

from .asttypes import AST, ExceptHandler, Match, Pass, Slice, Try, TryStar, match_case, mod
from .astutil import bistr

from .misc import (
    NodeError, astfield,
    STMTISH_FIELDS,
)

from .extparse import Mode, unparse
from .code import Code

_PATH_BODY          = [astfield('body', 0)]
_PATH_BODY2         = [astfield('body', 0), astfield('body', 0)]
_PATH_BODYORELSE    = [astfield('body', 0), astfield('orelse', 0)]
_PATH_BODY2ORELSE   = [astfield('body', 0), astfield('body', 0), astfield('orelse', 0)]
_PATH_BODYHANDLERS  = [astfield('body', 0), astfield('handlers', 0)]
_PATH_BODY2HANDLERS = [astfield('body', 0), astfield('body', 0), astfield('handlers', 0)]
_PATH_BODYCASES     = [astfield('body', 0), astfield('cases', 0)]


def _reparse_raw_base(self: fst.FST, new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
                      copy_lines: list[str], path: list[astfield] | str | None, set_ast: bool = True,
                      mode: Mode | None = None) -> fst.FST:
    """Actually do the reparse. If `mode` is `None` then will just try a normal `'exec'` parse and fail if that fails.
    Otherwise it will try this mode first, then all other parse modes as it is assumed to be a non-top level
    statementish thing being reparsed."""

    copy_root = fst.FST(Pass(), copy_lines, lcopy=False)  # we don't need the ASTs here, just the lines

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
        copy        = copy_root

    else:
        copy = copy_root.child_from_path(path)

        if not copy:
            raise RuntimeError('could not find node after raw reparse')

        root._put_src(new_lines, ln, col, end_ln, end_col, True, self if set_ast else None)  # we do this again in our own tree to offset our nodes which aren't being moved over from the modified copy, can exclude self if setting ast because it overrides self locations

        copy.pfield.set(copy.parent.a, None)  # remove from copy tree so that copy_root unmake doesn't zero out new node
        copy_root._unmake_fst_tree()

    if set_ast:
        self._set_ast(copy.a)
        self._touchall(True)

    return copy


def _reparse_raw_stmtish(self: fst.FST, new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> bool:
    """Reparse only statementish or block header part of statementish containing changes."""

    if not (stmtish := self.parent_stmtish(True, False)):
        return False

    pln, pcol, pend_ln, pend_col = stmtish.bloc

    root     = self.root
    lines    = root._lines
    stmtisha = stmtish.a

    if in_blkopen := (blkopen_end := stmtish._loc_block_header_end()) and (end_ln, end_col) <= blkopen_end:  # block statement with modification limited to block header
        pend_ln, pend_col = blkopen_end

    elif stmtish is root:  # reparse may include trailing comments which would not otherwise be included
        pend_ln  = len(lines) - 1
        pend_col = len(lines[-1])

    if isinstance(stmtisha, match_case):
        copy_lines = ([bistr('')] * (pln - 1) +
                      [bistr('match a:')] +
                      lines[pln : pend_ln + 1])
        path       = _PATH_BODYCASES

    else:
        indent = stmtish.get_indent()

        if not pcol:  # not 'not indent' because could be semicolon
            copy_lines = [bistr('')] * pln + lines[pln : pend_ln + 1]

        elif pln:
            copy_lines = ([bistr('if 1:')] +
                          [bistr('')] * (pln - 1) +
                          [bistr(f'{indent}{" " * (pcol - len(indent))}{lines[pln][pcol:]}')] +
                          lines[pln + 1 : pend_ln + 1])

        elif (off := pcol - 4) < 0:
            raise NotImplementedError('degenerate statement starts at (0,1), (0,2) or (0,3)')

        else:
            copy_lines = ([bistr(f"try:{' ' * off}{lines[pln][pcol:]}")] +
                          lines[pln + 1 : pend_ln + 1] +
                          [bistr('finally: pass')])

        if isinstance(stmtisha, ExceptHandler):
            assert pln > bool(indent)

            copy_lines[pln - 1] = bistr(indent + 'try: pass')
            path                = _PATH_BODY2HANDLERS if indent else _PATH_BODYHANDLERS

        elif not pcol:  # not 'not indent' because could be semicolon
            if stmtish.is_elif():
                copy_lines[0] = bistr('if 2: pass')
                path          = _PATH_BODYORELSE
            else:
                path = _PATH_BODY

        else:
            if stmtish.is_elif():
                copy_lines[1] = bistr(indent + 'if 2: pass')
                path          = _PATH_BODY2ORELSE
            else:
                path = _PATH_BODY2

    if not in_blkopen:  # non-block statement or modifications not limited to block header part
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

        _reparse_raw_base(stmtish, new_lines, ln, col, end_ln, end_col, copy_lines, path)

        return True

    # modifications only to block header line(s) of block statement

    if isinstance(stmtisha, Match):
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

        copy_lines.append(bistr(indent + ' case 1: pass'))

    else:
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col] + ' pass')

        if isinstance(stmtisha, (Try, TryStar)):  # this one is just silly, nothing to put there, but we cover it
            copy_lines.append(bistr(indent + 'finally: pass'))

    copy  = _reparse_raw_base(stmtish, new_lines, ln, col, end_ln, end_col, copy_lines, path, False)
    copya = copy.a

    if not isinstance(stmtisha, match_case):  # match_case doesn't have AST location
        copya.end_lineno     = stmtisha.end_lineno
        copya.end_col_offset = stmtisha.end_col_offset

    for field in STMTISH_FIELDS:
        if (body := getattr(stmtisha, field, None)) is not None:
            setattr(copya, field, body)

    stmtish._set_ast(copya)
    stmtish._touchall(True)

    return True


# ----------------------------------------------------------------------------------------------------------------------
# FST class private methods

def _reparse_raw(self: fst.FST, code: Code | None, ln: int, col: int, end_ln: int, end_col: int,
                 exact: bool | None = None) -> fst.FST | None:
    """Reparse this node which entirely contatins the span which is to be replaced with `code` source. `self` must
    be a node which entirely contains the location and is guaranteed not to be deleted. `self` and some of its
    parents going up may be replaced (root node `FST` will never change, the `AST` it points to may though). Not
    safe to use in a `walk()`.

    **Returns:**
    - `FST | None`: FIRST highest level node contained entirely within replacement source or `None` if no candidate.
        This could wind up being just an operator like '+' depending on the replacement. If `exact` is passed and
        not `None` then will attempt a `find_loc(..., exact)` if could not find candidate node with `find_in_loc()`.
    """

    if isinstance(code, list):
        new_lines = code
    elif isinstance(code, str):
        new_lines = code.split('\n')
    elif isinstance(code, AST):
        new_lines = unparse(code).split('\n')
    elif code is None:
        new_lines = [bistr('')]
    elif not code.is_root:  # isinstance(code, fst.FST)
        raise ValueError('expecting root node')
    else:
        new_lines = code._lines

    root = self.root

    if not _reparse_raw_stmtish(self, new_lines, ln, col, end_ln, end_col):  # attempt to reparse only statement (or even only block header), if fails then no statement found above
        if (mode := root.a.__class__) is not Slice and (base := mode.__bases__[0]) not in (AST, mod, ExceptHandler):  # first generalize a bit
            mode = base

        _reparse_raw_base(self, new_lines, ln, col, end_ln, end_col, root._lines[:],  # fallback to reparse all source
                          None if self is root else root.child_path(self), True, mode)

    if code is None:
        return None

    if len(new_lines) == 1:
        end_ln  = ln
        end_col = col + len(new_lines[0])

    else:
        end_ln  = ln + len(new_lines) - 1
        end_col = len(new_lines[-1])

    return (root.find_in_loc(ln, col, end_ln, end_col) or  # `root` instead of `self` because some changes may propagate farther up the tree, like 'elif' -> 'else'
            (root.find_loc(ln, col, end_ln, end_col, exact) if exact is not None else None))
