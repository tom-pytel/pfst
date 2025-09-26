"""Old slice FST methods, need to redo.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from typing import Any, Literal, Mapping

from . import fst
from . import fst_slice

from .asttypes import (
    AsyncFor, AsyncFunctionDef, AsyncWith, ClassDef, ExceptHandler, For, FunctionDef, If, Match, Module, Try, While,
    With, TryStar, match_case, mod, stmt,
)

from .astutil import copy_ast
from .misc import astfield, fstloc, next_find, prev_find
from .code import Code, code_as_stmts, code_as_ExceptHandlers, code_as_match_cases
from .traverse import prev_bound, next_bound_step, prev_bound_step
from .srcedit_old import _src_edit


def _set_end_pos(self: fst.FST, end_lineno: int, end_col_offset: int, self_: bool = True) -> None:
    """Walk up parent chain (starting at `self`) setting `.end_lineno` and `.end_col_offset` to `end_lineno` and
    `end_col_offset` if self is last child of parent. Initial `self` is corrected always. Used for correcting
    parents after an `offset()` which removed or modified last child statements of block parents, or other nodes.

    **Parameters:**
    - `(end_lineno, end_col_offset)` - Position which should be the new end.
    - `self_`: Whether to set for `self` or not, if not then will skip `self` and set for parents.

    """

    while True:
        if not self_:
            self_ = True

        else:
            if hasattr(a := self.a, 'end_lineno'):  # because of ASTs which locations
                a.end_lineno = end_lineno
                a.end_col_offset = end_col_offset

            self._touch()  # even if AST doesn't have location, it may be calculated and needs to be cleared out anyway

        if not (parent := self.parent) or self.next():  # self is not parent.last_child():
            break

        self = parent


def _set_block_end_from_last_child(self: fst.FST, bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                                   ) -> None:
    """Fix end location of a block statement after its last child (position-wise, not last existing child) has been
    cut or deleted. Will set end position of `self` and any parents who `self` is the last child of to the new last
    child if it is past the block-open colon, otherwise set end at just past the block-open colon.

    **Parameters:**
    - `bound_ln`, `bound_col`: Position before block colon but after and pre-colon `AST` node.
    - `bound_end_ln`, `bound_end_col`: Position after block colon, probably start of deleted region, only used if
        new last child is before colon.
    """

    end_lineno = None

    if last_child := self.last_child():  # easy enough when we have a new last child
        if last_child.pfield.name in ('body', 'orelse', 'handlers', 'finalbody', 'cases'):  # but make sure its past the block open colon
            end_lineno = last_child.end_lineno
            end_col_offset = last_child.end_col_offset

    if end_lineno is None:
        lines = self.root._lines

        if end := prev_find(lines, bound_ln, bound_col, bound_end_ln, bound_end_col, ':'):  # find first preceding block colon, its there unless first opened block in module
            end_ln, end_col = end
            end_col += 1  # just past the colon

        else:
            end_ln = bound_ln
            end_col = bound_col

        end_lineno = end_ln + 1
        end_col_offset = lines[end_ln].c2b(end_col)

    _set_end_pos(self, end_lineno, end_col_offset)


def _elif_to_else_if(self: fst.FST) -> None:
    """Convert an 'elif something:\\n  ...' to 'else:\\n  if something:\\n    ...'. Make sure to only call on an
    actual `elif`, meaning the lone `If` statement in the parent's `orelse` block which is an actual `elif` and not
    an `if`."""

    indent = self.get_indent()

    self._indent_lns(skip=0)

    if not self.next():  # last child?
        _set_end_pos(self, (a := self.a).end_lineno, a.end_col_offset, False)

    ln, col, _, _ = self.loc

    self._put_src(['if'], ln, col, ln, col + 4, False)
    self._put_src([indent + 'else:', indent + self.root.indent], ln, 0, ln, col, False)


def _normalize_block(self: fst.FST, field: str = 'body', *, indent: str | None = None) -> None:
    """Move statements on the same logical line as a block open to their own line, e.g:
    ```
    if a: call()
    ```
    Becomes:
    ```
    if a:
        call()
    ```

    **Parameters:**
    - `field`: Which block to normalize (`'body'`, `'orelse'`, `'handlers'`, `'finalbody'`).
    - `indent`: The indentation to use for the relocated line if already known, saves a call to `get_indent()`.
    """

    if isinstance(self.a, mod) or not (block := getattr(self.a, field)) or not isinstance(block, list):
        return

    b0 = block[0].f
    b0_ln, b0_col, _, _ = b0.bloc
    root = self.root

    if not (colon := prev_find(root._lines, *prev_bound(b0), b0_ln, b0_col, ':', True, comment=True, lcont=None)):  # must be there
        return

    if indent is None:
        indent = b0.get_indent()

    ln, col = colon

    self._put_src(['', indent], ln, col + 1, b0_ln, b0_col, False)


# ----------------------------------------------------------------------------------------------------------------------
# FST class private methods

def _get_slice_stmtish(self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                       options: Mapping[str, Any], *, one: bool = False) -> fst.FST:
    ast = self.a
    body = getattr(ast, field)
    start, stop = fst_slice._fixup_slice_indices(len(body), start, stop)

    if start == stop:
        return fst.FST(Module(body=[], type_ignores=[]), [''], from_=self, lcopy=False)

    ffirst = body[start].f
    flast = body[stop - 1].f
    fpre = body[start - 1].f if start else None
    fpost = body[stop].f if stop < len(body) else None
    indent = ffirst.get_indent()

    block_loc = fstloc(*(fpre.bloc[2:] if fpre else prev_bound_step(ffirst)),
                       *(fpost.bloc[:2] if fpost else next_bound_step(flast)))

    copy_loc, put_loc, put_lines = (
        _src_edit.get_slice_stmt(self, field, cut, block_loc, ffirst, flast, fpre, fpost, **options))

    if not cut:
        modifying = None
        asts = [copy_ast(body[i]) for i in range(start, stop)]
        put_loc = None

    else:
        modifying = self._modifying(field).enter()
        is_last_child = not fpost and not flast.next()
        asts = body[start : stop]

        del body[start : stop]

        for i in range(start, len(body)):
            body[i].f.pfield = astfield(field, i)

    if not one:
        get_ast = Module(body=asts, type_ignores=[])
    elif len(asts) == 1:
        get_ast = asts[0]
    else:
        raise ValueError('cannot specify `one=True` if getting multiple statements')

    fst_ = self._make_fst_and_dedent(indent, get_ast, copy_loc, '', '', put_loc, put_lines,
                                     docstr=options.get('docstr'))

    if cut and is_last_child:  # correct for removed last child nodes or last nodes past the block open colon
        _set_block_end_from_last_child(self, block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)

    if len(asts) == 1 and isinstance(a := asts[0], If):
        a.f._maybe_fix_elif()

    if modifying:
        modifying.success()

    return fst_


def _put_slice_stmtish(self: fst.FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                       field: str, one: bool, options: Mapping[str, Any]) -> None:
    ast = self.a
    body = getattr(ast, field)

    if code is None:
        put_fst = None

    else:
        # put_fst  = self._code_as_stmtishs(code, self.root.parse_params, is_trystar=isinstance(ast, TryStar))
        # put_ast  = put_fst.a
        # put_body = put_ast.body

        # if one and len(put_body) != 1:
        #     raise ValueError('expecting a single statement')

        # node_type = ExceptHandler if field == 'handlers' else match_case if field == 'cases' else stmt

        # if any(not isinstance(bad_node := n, node_type) for n in put_body) and options.get('check_node_type', True):  # TODO: `check_node_type` is for some previously written tests, but really should fix those tests instead
        #     raise ValueError(f"cannot put {bad_node.__class__.__qualname__} node to '{field}' field")


        if body and isinstance(ast, Module):  # check for slices
            if isinstance(b0 := body[0], stmt):
                put_fst = code_as_stmts(code, self.root.parse_params)
            elif isinstance(b0, ExceptHandler):
                put_fst = code_as_ExceptHandlers(code, self.root.parse_params,
                                                 is_trystar=b0.f.is_except_star())
            else:  # match_case
                put_fst = code_as_match_cases(code, self.root.parse_params)

        elif field == 'handlers':
            put_fst = code_as_ExceptHandlers(code, self.root.parse_params, is_trystar=isinstance(ast, TryStar))
        elif field != 'cases':  # 'body', 'orelse', 'finalbody'
            put_fst = code_as_stmts(code, self.root.parse_params)
        else:  # 'cases'
            put_fst = code_as_match_cases(code, self.root.parse_params)

        put_ast = put_fst.a
        put_body = put_ast.body

        if one and len(put_body) != 1:
            raise ValueError('expecting a single element')

    start, stop = fst_slice._fixup_slice_indices(len(body), start, stop)
    slice_len = stop - start

    if not slice_len and (not put_fst or (not put_body and len(ls := put_fst._lines) == 1 and not ls[0])):  # deleting empty slice or assigning empty fst to empty slice, noop
        return

    root = self.root
    lines = root._lines
    fpre = body[start - 1].f if start else None
    fpost = body[stop].f if stop < len(body) else None

    if put_fst:
        opener_indent = self.get_indent()

        if not body:
            block_indent = opener_indent if isinstance(self.a, mod) else opener_indent + root.indent
        elif not (b0 := body[0]).f.is_elif():
            block_indent = b0.f.get_indent()
        elif (bb := b0.body) or (bb := b0.orelse):
            block_indent = bb[0].f.get_indent()
        else:
            block_indent = opener_indent + root.indent

        if fpre or fpost:
            _normalize_block(self, field, indent=block_indent)  # don't want to bother figuring out if valid to insert to statements on single block logical line

    if slice_len:  # replacement
        ffirst = body[start].f
        flast = body[stop - 1].f

        block_loc = fstloc(*(fpre.bloc[2:] if fpre else prev_bound_step(ffirst)),
                           *(fpost.bloc[:2] if fpost else next_bound_step(flast)))

        is_last_child = not fpost and not flast.next()

    else:  # insertion
        ffirst = flast = None

        if field == 'orelse' and len(body) == 1 and (f := body[0].f).is_elif():
            _elif_to_else_if(f)

        if fpre:
            block_loc = fstloc(*fpre.bloc[2:], *(fpost.bloc[:2] if fpost else next_bound_step(fpre)))
            is_last_child = not fpost and not fpre.next()

        elif fpost:
            if isinstance(ast, mod):  # put after all header stuff in module
                ln, col, _, _ = fpost.bloc
                block_loc = fstloc(ln, col, ln, col)

            elif field != 'handlers' or ast.body:
                block_loc = fstloc(*prev_bound_step(fpost), *fpost.bloc[:2])

            else:  # special case because 'try:' doesn't have ASTs inside it and each 'except:' lives at the 'try:' indentation level
                end_ln, end_col = fpost.bloc[:2]
                ln, col = prev_find(lines, *prev_bound_step(fpost), end_ln, end_col, ':')
                block_loc = fstloc(ln, col + 1, end_ln, end_col)

            is_last_child = False

        else:  # insertion into empty block (or nonexistent 'else' or 'finally' block)
            if not put_body and field in ('orelse', 'finalbody'):
                raise ValueError(f"cannot insert empty statement into empty '{field}' field")

            if isinstance(ast, (FunctionDef, AsyncFunctionDef, ClassDef, With, AsyncWith, Match, ExceptHandler,
                                match_case)):  # only one block possible, 'body' or 'cases'
                block_loc = fstloc(*self.bloc[2:], *next_bound_step(self))  # end of bloc will be just past ':'
                is_last_child = True

            elif isinstance(ast, mod):  # put after all header stuff in module
                _, _, end_ln, end_col = self.bloc

                block_loc = fstloc(end_ln, end_col, end_ln, end_col)
                is_last_child = True

            elif isinstance(ast, (For, AsyncFor, While, If)):  # 'body' or 'orelse'
                if field == 'orelse':
                    is_last_child = True

                    if not (body_ := ast.body):
                        block_loc = fstloc(*self.bloc[2:], *next_bound_step(self))
                    else:
                        block_loc = fstloc(*body_[-1].f.bloc[2:], *next_bound_step(self))

                else:  # field == 'body':
                    if orelse := ast.orelse:
                        ln, col = next_find(lines, *(f := orelse[0].f).prev().bloc[2:], *f.bloc[:2], ':')  # we know its there
                        block_loc = fstloc(ln, col + 1, *orelse[0].f.bloc[:2])
                        is_last_child = False

                    else:
                        block_loc = fstloc(*self.bloc[2:], *next_bound_step(self))
                        is_last_child = True

            else:  # isinstance(ast, (Try, TryStar))
                assert isinstance(ast, (Try, TryStar))

                if field == 'finalbody':
                    is_last_child = True

                    if not (block := ast.orelse) and not (block := ast.handlers) and not (block := ast.body):
                        block_loc = fstloc(*self.bloc[2:], *next_bound_step(self))
                    else:
                        block_loc = fstloc(*block[-1].f.bloc[2:], *next_bound_step(self))

                elif field == 'orelse':
                    if finalbody := ast.finalbody:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')  # we can use bloc[:2] even if there are ASTs between that and here because 'finally' must be on its own line
                        is_last_child = False

                    else:
                        end_ln, end_col = next_bound_step(self)
                        is_last_child = True

                    if not (block := ast.handlers) and not (block := ast.body):
                        ln, col = prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                        block_loc = fstloc(ln, col + 1, end_ln, end_col)

                    else:
                        block_loc = fstloc(*block[-1].f.bloc[2:], end_ln, end_col)

                elif field == 'handlers':
                    if orelse := ast.orelse:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *orelse[0].f.bloc[:2], 'else')
                        is_last_child = False

                    elif finalbody := ast.finalbody:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')
                        is_last_child = False

                    else:
                        end_ln, end_col = next_bound_step(self)
                        is_last_child = True

                    if not (body_ := ast.body):
                        ln, col = prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                        block_loc = fstloc(ln, col + 1, end_ln, end_col)

                    else:
                        block_loc = fstloc(*body_[-1].f.bloc[2:], end_ln, end_col)

                else:  # field == 'body'
                    if handlers := ast.handlers:
                        end_ln, end_col = handlers[0].f.bloc[:2]
                        is_last_child = False

                    elif orelse := ast.orelse:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *orelse[0].f.bloc[:2], 'else')
                        is_last_child = False

                    elif finalbody := ast.finalbody:
                        end_ln, end_col = prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')
                        is_last_child = False

                    else:
                        end_ln, end_col = next_bound_step(self)
                        is_last_child = True

                    ln, col = prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                    block_loc = fstloc(ln, col + 1, end_ln, end_col)

    if not put_fst:
        _, put_loc, put_lines = (
            _src_edit.get_slice_stmt(self, field, True, block_loc, ffirst, flast, fpre, fpost, **options))

        if put_loc:
            self._put_src(put_lines, *put_loc, True)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        put_len = 0

    else:
        put_loc = _src_edit.put_slice_stmt(self, put_fst, field, block_loc, opener_indent, block_indent,
                                           ffirst, flast, fpre, fpost, **options)

        put_fst._offset(0, 0, put_loc.ln, 0 if put_fst.bln or put_fst.bcol else lines[put_loc.ln].c2b(put_loc.col))
        self._put_src(put_fst._lines, *put_loc, False)
        self._unmake_fst_tree(body[start : stop])
        put_fst._unmake_fst_parents(True)

        body[start : stop] = put_body

        put_len = len(put_body)
        FST = fst.FST
        stack = [FST(body[i], self, astfield(field, i)) for i in range(start, start + put_len)]

        self._make_fst_tree(stack)

    for i in range(start + put_len, len(body)):
        body[i].f.pfield = astfield(field, i)

    if is_last_child:  # correct parent for modified / removed last child nodes
        if not put_fst:
            _set_block_end_from_last_child(self, block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)
        elif put_body:
            _set_end_pos(self, (last_child := self.last_child()).end_lineno, last_child.end_col_offset)
