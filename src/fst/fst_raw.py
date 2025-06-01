"""Raw reparse FST methods."""

from ast import *
from itertools import takewhile
from typing import Literal, Optional

from .astutil import *
from .astutil import TryStar

from .shared import (
    NodeError, astfield, fstloc,
    PARENTHESIZABLE,
    STMTISH_FIELDS,
    Code,
    _next_find, _prev_find,
    _fixup_slice_indices, _coerce_ast,
)

_PATH_BODY          = [astfield('body', 0)]
_PATH_BODY2         = [astfield('body', 0), astfield('body', 0)]
_PATH_BODYORELSE    = [astfield('body', 0), astfield('orelse', 0)]
_PATH_BODY2ORELSE   = [astfield('body', 0), astfield('body', 0), astfield('orelse', 0)]
_PATH_BODYHANDLERS  = [astfield('body', 0), astfield('handlers', 0)]
_PATH_BODY2HANDLERS = [astfield('body', 0), astfield('body', 0), astfield('handlers', 0)]
_PATH_BODYCASES     = [astfield('body', 0), astfield('cases', 0)]


def _raw_slice_loc(self: 'FST', start: int | Literal['end'] | None, stop: int | None, field: str) -> fstloc:
    """Get location of a raw slice. Sepcial cases for decorators, comprehension ifs and other weird nodes."""

    def fixup_slice_index_for_raw(len_, start, stop):
        start, stop = _fixup_slice_indices(len_, start, stop)

        if stop == start:
            raise ValueError(f"invalid slice for raw operation")

        return start, stop

    ast = self.a

    if isinstance(ast, Dict):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

        keys        = ast.keys
        values      = ast.values
        start, stop = fixup_slice_index_for_raw(len(keys), start, stop)
        start_loc   = self._dict_key_or_mock_loc(keys[start], values[start].f)

        if start_loc.is_FST:
            start_loc = start_loc.pars()

        return fstloc(start_loc.ln, start_loc.col, *values[stop - 1].f.pars()[2:])

    if isinstance(ast, Compare):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Compare")

        comparators  = ast.comparators  # virtual combined body of [Compare.left] + Compare.comparators
        start, stop  = fixup_slice_index_for_raw(len(comparators) + 1, start, stop)
        stop        -= 1

        return fstloc(*(comparators[start - 1] if start else ast.left).f.pars()[:2],
                        *(comparators[stop - 1] if stop else ast.left).f.pars()[2:])

    if isinstance(ast, MatchMapping):
        if field:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a MatchMapping")

        keys        = ast.keys
        start, stop = fixup_slice_index_for_raw(len(keys), start, stop)

        return fstloc(*keys[start].f.loc[:2], *ast.patterns[stop - 1].f.pars()[2:])

    if isinstance(ast, comprehension):
        ifs         = ast.ifs
        start, stop = fixup_slice_index_for_raw(len(ifs), start, stop)
        ffirst      = ifs[start].f
        start_pos   = _prev_find(self.root._lines, *ffirst._prev_bound(), ffirst.ln, ffirst.col, 'if')

        return fstloc(*start_pos, *ifs[stop - 1].f.pars()[2:])

    if field == 'decorator_list':
        decos       = ast.decorator_list
        start, stop = fixup_slice_index_for_raw(len(decos), start, stop)
        ffirst      = decos[start].f
        start_pos   = _prev_find(self.root._lines, 0, 0, ffirst.ln, ffirst.col, '@')  # we can use '0, 0' because we know "@" starts on a newline

        return fstloc(*start_pos, *decos[stop - 1].f.pars()[2:])

    body        = getattr(ast, field)  # field must be valid by here
    start, stop = fixup_slice_index_for_raw(len(body), start, stop)

    return fstloc(*body[start].f.pars(shared=False)[:2],
                  *body[stop - 1].f.pars(shared=False)[2:])


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

def _reparse_raw(self: 'FST', new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
                 copy_lines: list[str], path: list[astfield] | str, set_ast: bool = True) -> 'FST':
    """Actually do the reparse."""

    copy_root = FST(Pass(), copy_lines, lcopy=False)  # we don't need the ASTs here, just the lines

    copy_root.put_src(new_lines, ln, col, end_ln, end_col)

    root      = self.root
    copy_root = FST.fromsrc(copy_root.src, mode=get_parse_mode(root.a) or 'exec', **root.parse_params)

    if path == 'root':
        self._lines = copy_root._lines
        copy        = copy_root

    else:
        copy = copy_root.child_from_path(path)

        if not copy:
            raise RuntimeError(f'could not find node after raw reparse')

        root.put_src(new_lines, ln, col, end_ln, end_col, True, self if set_ast else None)  # we do this again in our own tree to offset our nodes which aren't being moved over from the modified copy, can exclude self if setting ast because it overrides self locations

        copy.pfield.set(copy.parent.a, None)  # remove from copy tree so that copy_root unmake doesn't zero out new node
        copy_root._unmake_fst_tree()

    if set_ast:
        self._set_ast(copy.a)
        self.touch(True)

    return copy


def _reparse_raw_stmtish(self: 'FST', new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> bool:
    """Reparse only statementish or block header part of statementish containing changes."""

    if not (stmtish := self.parent_stmtish(True, False)):
        return False

    pln, pcol, pend_ln, pend_col = stmtish.bloc

    root     = self.root
    lines    = root._lines
    stmtisha = stmtish.a

    if in_blkopen := (blkopen_end := stmtish._loc_block_header_end()) and (end_ln, end_col) <= blkopen_end:  # block statement with modification limited to block header
        pend_ln, pend_col = blkopen_end

    if isinstance(stmtisha, match_case):
        copy_lines = ([bistr('')] * (pln - 1) +
                      [bistr('match a:'), bistr(' ' * pcol + lines[pln][pcol:])] +
                      lines[pln + 1 : pend_ln + 1])
        path       = _PATH_BODYCASES

    else:
        indent = stmtish.get_indent()

        if not indent:
            copy_lines = [bistr('')] * pln + lines[pln : pend_ln + 1]

        elif pln:
            copy_lines = ([bistr('if 1:')] +
                            [bistr('')] * (pln - 1) +
                            [bistr(' ' * pcol + lines[pln][pcol:])] +
                            lines[pln + 1 : pend_ln + 1])
        else:
            copy_lines = ([bistr(f"try:{' ' * (pcol - 4)}{lines[pln][pcol:]}")] +
                            lines[pln + 1 : pend_ln + 1] +
                            [bistr('finally: pass')])

        if isinstance(stmtisha, ExceptHandler):
            assert pln > bool(indent)

            copy_lines[pln - 1] = bistr(indent + 'try: pass')
            path                = _PATH_BODY2HANDLERS if indent else _PATH_BODYHANDLERS

        elif not indent:
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

        stmtish._reparse_raw(new_lines, ln, col, end_ln, end_col, copy_lines, path)

        return True

    # modifications only to block header line(s) of block statement

    if isinstance(stmtisha, Match):
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

        copy_lines.append(bistr(indent + ' case 1: pass'))

    else:
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col] + ' pass')

        if isinstance(stmtisha, (Try, TryStar)):  # this one is just silly, nothing to put there, but we cover it
            copy_lines.append(bistr(indent + 'finally: pass'))

    copy  = stmtish._reparse_raw(new_lines, ln, col, end_ln, end_col, copy_lines, path, False)
    copya = copy.a

    if not isinstance(stmtisha, match_case):  # match_case doesn't have AST location
        copya.end_lineno     = stmtisha.end_lineno
        copya.end_col_offset = stmtisha.end_col_offset

    for field in STMTISH_FIELDS:
        if (body := getattr(stmtisha, field, None)) is not None:
            setattr(copya, field, body)

    stmtish._set_ast(copya)
    stmtish.touch(True)

    return True


def _reparse_raw_loc(self: 'FST', code: Code | None, ln: int, col: int, end_ln: int, end_col: int,
                     exact: bool | None = None) -> Optional['FST']:
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
        new_lines = FST._unparse(code).split('\n')
    elif code is None:
        new_lines = [bistr('')]
    elif not code.is_root:  # isinstance(code, FST)
        raise ValueError('expecting root node')
    else:
        new_lines = code._lines

    if not self._reparse_raw_stmtish(new_lines, ln, col, end_ln, end_col):  # attempt to reparse only statement (or even only block header)
        assert self.root.is_mod  # TODO: allow with non-mod root

        root = self.root

        self._reparse_raw(new_lines, ln, col, end_ln, end_col, root._lines[:],  # fallback to reparse all source
                          'root' if self is root else root.child_path(self))

    if code is None:
        return None

    if len(new_lines) == 1:
        end_ln  = ln
        end_col = col + len(new_lines[0])

    else:
        end_ln  = ln + len(new_lines) - 1
        end_col = len(new_lines[-1])

    return (self.root.find_in_loc(ln, col, end_ln, end_col) or  # `self.root` instead of `self` because some changes may propagate farther up the tree, like 'elif' -> 'else'
            (self.root.find_loc(ln, col, end_ln, end_col, exact) if exact is not None else None))


def _reparse_raw_slice(self: 'FST', code: Code | None, start: int | Literal['end'] | None, stop: int | None, field: str,
                       *, one: bool = False, **options) -> 'FST':  # -> Self
    """Put a raw slice of child nodes to `self`."""

    if isinstance(code, AST):
        if not one:
            try:
                ast = _coerce_ast(code, 'exprish')
            except Exception:
                pass

            else:
                if isinstance(ast, Tuple):  # strip delimiters because we want CONTENTS of slice for raw put, not the slice object itself
                    code = FST._unparse(ast)[1 : (-2 if len(ast.elts) == 1 else -1)]  # also remove singleton Tuple trailing comma
                elif isinstance(ast, (List, Dict, Set, MatchSequence, MatchMapping)):
                    code = FST._unparse(ast)[1 : -1]

    elif isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root node')

        try:
            ast = _coerce_ast(code.a, 'exprish')
        except Exception:
            pass

        else:
            fst = ast.f

            if one:
                if (is_par_tup := fst.is_parenthesized_tuple()) is None:  # only need to parenthesize this, others are already enclosed
                    if isinstance(ast, MatchSequence) and not fst._is_parenthesized_seq('patterns'):
                        fst._parenthesize_grouping()

                elif is_par_tup is False:
                    fst._parenthesize_tuple()

            elif ((is_dict := isinstance(ast, Dict)) or
                    (is_match := isinstance(ast, (MatchSequence, MatchMapping))) or
                    isinstance(ast, (Tuple, List, Set))
            ):
                if not ((is_par_tup := fst.is_parenthesized_tuple()) is False or  # don't strip nonexistent delimiters if is unparenthesized Tuple or MatchSequence
                        (is_par_tup is None and isinstance(ast, MatchSequence) and
                            not fst._is_parenthesized_seq('patterns'))
                ):
                    code.put_src(None, end_ln := code.end_ln, (end_col := code.end_col) - 1, end_ln, end_col, True)  # strip enclosing delimiters
                    code.put_src(None, ln := code.ln, col := code.col, ln, col + 1, False)

                if elts := ast.values if is_dict else ast.patterns if is_match else ast.elts:
                    if comma := _next_find(code.root._lines, (l := elts[-1].f.loc).end_ln, l.end_col, code.end_ln,
                                            code.end_col, ','):  # strip trailing comma
                        ln, col = comma

                        code.put_src(None, ln, col, ln, col + 1, False)

    self._reparse_raw_loc(code, *_raw_slice_loc(self, start, stop, field))

    return self.repath()


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
