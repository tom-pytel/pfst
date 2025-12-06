"""Get slice. Some slices can use normal `AST` types and others need special custom `fst` `AST` container classes.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import re
from typing import Any, Literal, Mapping

import fst as fst_package  # because of circular imports

from . import fst

from .asttypes import (
    AST,
    And,
    Assign,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    BoolOp,
    Call,
    ClassDef,
    Compare,
    Del,
    Delete,
    Dict,
    DictComp,
    ExceptHandler,
    Expr,
    For,
    FunctionDef,
    GeneratorExp,
    Global,
    If,
    Import,
    ImportFrom,
    Interactive,
    JoinedStr,
    List,
    ListComp,
    Load,
    Match,
    MatchAs,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    Module,
    Name,
    Nonlocal,
    Pass,
    Set,
    SetComp,
    Try,
    Tuple,
    While,
    With,
    comprehension,
    match_case,
    TryStar,
    TypeAlias,
    TemplateStr,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from .astutil import re_identifier, bistr, set_ctx, copy_ast
from .common import NodeError, astfield, fstloc, next_frag, next_find, next_find_re

from .fst_misc import (
    new_empty_tuple,
    new_empty_set_star,
    new_empty_set_call,
    new_empty_set_curlies,
    get_option_overridable,
    fixup_slice_indices,
)

from .slice_stmtish import get_slice_stmtish
from .slice_exprish import _locs_first_and_last, get_slice_sep, get_slice_nosep


_re_empty_line_start_maybe_cont_0 = re.compile(r'[ \t]*\\?')  # empty line start with maybe continuation
_re_empty_line_start_maybe_cont_1 = re.compile(r'[ \t]+\\?')  # empty line start with maybe continuation WITH AT LEAST 1 leading whitespace


# ......................................................................................................................
# shared with fst_slice_put

def _get_option_norm(override_option: str, norm_option: str, options: Mapping[str, Any]) -> bool | str:
    set_norm = get_option_overridable('norm', override_option, options)

    return fst.FST.get_option(norm_option, options) if set_norm is True else set_norm


def _get_option_op_side(is_first: bool, is_last: bool, options: Mapping[str, Any]) -> bool | None:
    """Get concrete `op_side_left` from `op_side` option hint and actual location of slice (if at start or end).

    **Returns:**
    - `True`: If operator side is on the left.
    - `False`: If operator side is on the right.
    - `None`: If operator side is neither (slice is from start to stop so there is no other operator on either side).
    """

    if is_first:
        return None if is_last else False
    if is_last:
        return True
    else:
        return fst.FST.get_option('op_side', options) == 'left'


def _bounds_Delete_targets(
    self: fst.FST, start: int = 0, loc_first: fst.FST | None = None
) -> tuple[int, int, int, int]:
    body = self.a.targets

    _, _, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    elif body:
        bound_ln, bound_col, _, _ = loc_first or body[0].f.pars()
    else:
        bound_ln = bound_end_ln
        bound_col = bound_end_col

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _bounds_Assign_targets(
    self: fst.FST, start: int = 0, loc_first: fst.FST | None = None
) -> tuple[int, int, int, int]:
    ast = self.a
    body = ast.targets

    bound_end_ln, bound_end_col, _, _ = ast.value.f.pars()

    if bound_end_col and self.root._lines[bound_end_ln][bound_end_col - 1].isspace():  # leave space between end of bound and start of value so that we don't get stuff like 'a =b'
        bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    elif body:
        bound_ln, bound_col, _, _ = loc_first or body[0].f.pars()
    else:
        bound_ln = bound_end_ln
        bound_col = bound_end_col

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _bounds_decorator_list(self: fst.FST, start: int = 0) -> tuple[int, int, int, int]:
    """The bound for decorators of a non-`_decorator_list` node starts at the end of the previous line (if there is
    one)."""

    ast = self.a
    body = ast.decorator_list
    is_special = isinstance(ast, _decorator_list)

    if is_special:
        bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc
    else:
        bound_end_ln, bound_end_col, _, _ = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()

    elif not is_special:  # FunctionDef, AsyncFunctionDef or ClassDef
        if not body:  # no decorators currently present so just set bounds at start of function or class
            bound_ln = bound_end_ln
            bound_col = bound_end_col

        else:
            bound_ln, bound_col, _, _ = self._loc_decorator(0, False)

        if bound_ln:  # if not starting at line 0 then bound needs to start at end of line above in order for the get_slice_nosep() machinery to remove first line correctly on cut
            bound_ln -= 1
            bound_col = self.root._lines[bound_ln].lenbytes

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _bounds_generators(self: fst.FST, start: int = 0) -> tuple[int, int, int, int]:
    ast = self.a
    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if not (is_special := isinstance(ast, _comprehensions)):
        bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = ast.generators[start - 1].f.loc
    elif isinstance(ast, DictComp):
        _, _, bound_ln, bound_col = ast.value.f.pars()
    elif not is_special:  # ListComp, SetComp, GeneratorExp
        _, _, bound_ln, bound_col = ast.elt.f.pars()

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _bounds_comprehension_ifs(self: fst.FST, start: int = 0) -> tuple[int, int, int, int]:
    ast = self.a
    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if is_comprehension := isinstance(ast, comprehension):  # therefore not _comprehension_ifs
        if next := self.next():
            if next.ln > bound_end_ln:  # so that multiline ifs are handled correctly, yeah, really pedantic
                bound_end_ln += 1
                bound_end_col = 0

        elif (parent := self.parent) and not isinstance(parent.a, _comprehensions):  # we don't extend to end of `ListComp` (or one of the others) but we do set end boound to start of next line if past our end line so that multiline stuff procs correctly
            if parent.end_ln > bound_end_ln:
                bound_end_ln += 1
                bound_end_col = 0

    if start:
        _, _, bound_ln, bound_col = self._loc_comprehension_if(start - 1)
    elif is_comprehension:
        _, _, bound_ln, bound_col = ast.iter.f.pars()

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _move_Compare_left_into_comparators(self: fst.FST) -> None:
    """Move the `left` node of a `Compare` into `comparators` as the first node and insert a placeholder operator
    alignment node into `ops`. Set `left` to a temporary placeholder as well with the correct location (for operator
    location calculations). Set all `pfield`s accordingly."""

    ast = self.a
    ops = ast.ops
    comparators = ast.comparators
    left = ast.left
    lineno = ast.lineno
    col_offset = ast.col_offset
    ast.left = fst.FST(Pass(lineno=lineno, col_offset=col_offset,
                            end_lineno=lineno, end_col_offset=col_offset),  # illegal temporary use of Pass, doesn't have children, has loc and doesn't parenthesize (so no pars() overhead)
                       self, astfield('left')).a

    comparators.insert(0, left)
    ops.insert(0, fst.FST(Pass(lineno=lineno, col_offset=col_offset,
                               end_lineno=lineno, end_col_offset=col_offset),
                          self, astfield('')).a)  # this is to keep alignment between ops and comparators so that locs and pars() continue to work

    for i, (o, b) in enumerate(zip(ops, comparators, strict=True)):  # adjust all parent fields for inserted `left` and placeholder op at start
        o.f.pfield = astfield('ops', i)
        b.f.pfield = astfield('comparators', i)


def _move_Compare_first_comparator_into_left(self: fst.FST) -> None:
    """Move the first element of `comparators` into the `left` node of a `Compare` and delete the first `ops` operator
    and previous `left` placeholder. Set all `pfield`s accordingly. This undoes `_move_Compare_left_into_comparators()`.
    """

    ast = self.a
    ops = ast.ops
    comparators = ast.comparators

    ast.left.f._unmake_fst_tree()

    ast.left = left = comparators.pop(0)  # move original or new left element from start of `comparators` back to `left`
    left.f.pfield = astfield('left')

    ops[0].f._unmake_fst_tree()

    del ops[0]  # remove alignment placeholder op

    for i, (cmp, op) in enumerate(zip(comparators, ops, strict=True)):  # adjust all parent fields for inserted `left` and placeholder op at start
        cmp.f.pfield = astfield('comparators', i)
        op.f.pfield = astfield('ops', i)


def _add_MatchMapping_rest_as_real_node(self: fst.FST) -> fst.FST:
    """Add `MatchMapping.rest` temporarily as a None to `self.keys` and a `MatchAs` to `self.patterns`. No source is
    modified since the `rest` is already there so its location is just used for the new `MatchAs` node."""

    rest_ln, rest_col, rest_end_ln, rest_end_col = self._loc_MatchMapping_rest()

    assert rest_end_ln == rest_ln

    ast = self.a
    patterns = ast.patterns
    rest_line = self.root._lines[rest_ln]
    rest_ln += 1

    rest_ast = MatchAs(pattern=None, name=ast.rest, lineno=rest_ln, col_offset=rest_line.c2b(rest_col),
                       end_lineno=rest_ln, end_col_offset=rest_line.c2b(rest_end_col))
    rest_fst = fst.FST(rest_ast, self, astfield('patterns', len(patterns)), from_=self)

    ast.keys.append(None)  # this is normally illegal but we allow for it temporarily
    patterns.append(rest_ast)

    return rest_fst


def _remove_MatchMapping_rest_real_node(self: fst.FST) -> None:
    """Remove last pattern and key in `MatchMapping` which is assumed to be a previously temporarily created `rest`
    node."""

    ast = self.a
    patterns = ast.patterns

    patterns[-1].f._unmake_fst_tree()

    del patterns[-1]
    del ast.keys[-1]


def _update_loc_up_parents(self: fst.FST, lineno: int, col_offset: int, end_lineno: int, end_col_offset: int) -> None:
    """Change own location and walk up parent chain changing any start or end locations which coincide with our own old
    location to the new one."""

    ast = self.a
    old_lineno = ast.lineno
    old_col_offset = ast.col_offset
    old_end_lineno = ast.end_lineno
    old_end_col_offset = ast.end_col_offset
    ast.lineno = lineno
    ast.col_offset = col_offset
    ast.end_lineno = end_lineno
    ast.end_col_offset = end_col_offset

    self._touch()

    while self := self.parent:
        ast = self.a
        self_end_col_offset = getattr(ast, 'end_col_offset', None)

        if self_end_col_offset is None:
            break

        if at_old_end := (self_end_col_offset == old_end_col_offset and ast.end_lineno == old_end_lineno):  # only change if matches old location
            ast.end_lineno = end_lineno
            ast.end_col_offset = end_col_offset

        if ast.col_offset == old_col_offset and ast.lineno == old_lineno:
            ast.lineno = lineno
            ast.col_offset = col_offset

        elif not at_old_end:
            break

        self._touch()

    if self:
        self._touchall(True, True, False)


def _maybe_fix_naked_seq_loc(self: fst.FST, body: list[AST], is_first: bool = True, is_last: bool = True) -> None:
    """Fix the start and end positions of self and parents of a naked sequence which may have changed location to those
    of first and last child."""

    lines = self.root._lines
    ast = self.a

    if is_first:  # make sure our and parents' start position is at start of first element (before any pars)
        ln, col, end_ln, end_col = body[0].f.pars()

        self._set_start_pos(ln + 1, lines[ln].c2b(col), ast.lineno, ast.col_offset)

    if is_last:  # make sure our and parents' end position is at end of last element (after any pars)
        if not is_first or len(body) > 1:  # if not then we use end_ln and end_col from block above
            _, _, end_ln, end_col = body[-1].f.pars()

        self._set_end_pos(end_ln + 1, lines[end_ln].c2b(end_col), ast.end_lineno, ast.end_col_offset)


def _maybe_fix_naked_expr(self: fst.FST, is_del: bool, is_first: bool, options: Mapping[str, Any]) -> None:
    """Parenthesize if needed and allowed. If is first child of an `Expr` statement then may need to dedent line
    continuation to `Expr` indentation if that is the first line left, which may not start exactly at proper indentation
    level."""

    lines = self.root._lines

    if not self.is_root or (not is_del and fst.FST.get_option('pars', options)):  # if at root then this is optional and not done for a delete or disabled via 'pars=False' option otherwise
        if not self._is_enclosed_or_line() and not self._is_enclosed_in_parents():  # we may need to add pars to fix parsable
            self._parenthesize_grouping(False)

    if is_first:  # VERY SPECIAL CASE where we may have left a line continuation not exactly at proper indentation after delete at start of Expr which is our statement parent
        if (parent := self.parent_stmtish()) and isinstance(parent.a, Expr):
            ln, col, _, _ = self.loc

            if ln == parent.ln:  # if starts on same line as Expr then we may need to fix
                if col:  # if Expr starts after column 0 then is safe to just dedent any line continuation
                    line = lines[ln]

                    if m := _re_empty_line_start_maybe_cont_1.match(line):
                        if m.group().endswith('\\'):  # if is pure line continuation then can do this directly and don't need to offset anything because this won't change any actual start or end node positions
                            lines[ln] = bistr(line[:col] + '\\')

                        elif (end := m.end()) > col:  # wound up with leading whitespace before expression on same line as Expr so need to dedent to start of Expr
                            self._put_src(None, ln, col, ln, end, True)  # tail=True because maybe wound up with zero-length expression?

                else:  # a line continuation at column 0 effectively doesn't exist so if an expression on the next line is indented then it is an error, so we need to remove all line continuations which may follow and dedent any following expression
                    while m := _re_empty_line_start_maybe_cont_0.match(lines[ln]):
                        if m.group().endswith('\\'):  # if is pure line continuation then the safest thing to do is remove the line entirely because if the line continuation winds up at column 0 then it is like it doesn't exist and if the expression doesn't start at column 0 after it then it is an indentation error
                            self._put_src(None, ln, 0, ln + 1, 0, True)

                            continue

                        elif (end := m.end()) > col:
                            self._put_src(None, ln, col, ln, end, True)

                        break


def _maybe_fix_BoolOp(
    self: fst.FST,
    start: int,
    is_del: bool,
    is_last: bool,
    options: Mapping[str, Any],
    norm: bool,
) -> None:
    """Fix anything that might have been left wrong in a `BoolOp` after a cut, del or put."""

    body = self.a.values
    is_first = not start

    _maybe_fix_naked_expr(self, is_del, is_first, options)

    if body:
        _maybe_fix_naked_seq_loc(self, body, is_first, is_last)  # if everything erased then nothing to adjust to and we just leave previous location

        if not (is_first or (is_del and is_last)):  # interior possibly joined alnum due to add or delete
            ln, col, _, _ = body[start].f.loc

            self._maybe_fix_joined_alnum(ln, col)

    ln, col, end_ln, end_col = self.loc

    self._maybe_fix_joined_alnum(ln, col, end_ln, end_col)  # fix stuff like 'a and(b)if 1 else 0' -> 'aif 1 else 0' and '2 if 1 else(a)and b' -> '2 if 1 elseb'

    if norm and len(body) == 1:  # if only one element remains and normalizing then replace the BoolOp AST in self with the single `values` AST which remains
        self._set_ast(body.pop(), True)


def _maybe_fix_Compare(
    self: fst.FST,
    start: int,
    is_del: bool,
    is_last: bool,
    options: Mapping[str, Any],
    norm: bool,
) -> None:
    """Fix anything that might have been left wrong in a `Compare` after a cut, del or put. Expects `Compare` to be in
    `_move_Compare_left_into_comparators()` form."""

    body = self.a.comparators
    is_first = not start

    _maybe_fix_naked_expr(self, is_del, is_first, options)

    if body:
        _maybe_fix_naked_seq_loc(self, body, is_first, is_last)  # if everything erased then nothing to adjust to and we just leave previous location

        if not (is_first or (is_del and is_last)):  # interior possibly joined alnum due to add or delete on left
            ln, col, _, _ = body[start].f.loc

            self._maybe_fix_joined_alnum(ln, col)

        if is_del and not is_first:  # on right of start of delete
            _, _, end_ln, end_col = body[start - 1].f.loc

            self._maybe_fix_joined_alnum(end_ln, end_col)

    ln, col, end_ln, end_col = self.loc

    self._maybe_fix_joined_alnum(ln, col, end_ln, end_col)  # fix stuff like 'a and(b)if 1 else 0' -> 'aif 1 else 0' and '2 if 1 else(a)and b' -> '2 if 1 elseb'

    if len(body) == 1 and norm:  # if only one element remains and normalizing then replace the Compare AST in self with the single `comparators` AST which remains
        self._set_ast(body.pop(), True)  # this will unmake the leftmost operator fine, placeholder or op_side left or rotated right as well as `left` placeholder
    else:
        _move_Compare_first_comparator_into_left(self)


def _maybe_fix_Assign_target0(self: fst.FST) -> None:
    """If `Assign` has `target`s and first target does not start at same location as `self` then delete everything in
    between so that it starts at `self`."""

    # assert isinstance(self.a, Assign)

    if targets := self.a.targets:
        t0_ln, t0_col, _, _ = targets[0].f.pars()
        self_ln, self_col, _, _ = self.loc

        if t0_col != self_col or t0_ln != self_ln:
            self._put_src(None, self_ln, self_col, t0_ln, t0_col, False)


def _maybe_fix_decorator_list_trailing_newline(self: fst.FST, old_last_line: str) -> bool:
    """After insert new last element or delete current last element we need to see if there is a new trailing newline
    that wasn't there before, and if so then remove it.

    **Returns:**
    - `bool`: `True` if self is `_decorator_list` SPECIAL SLICE, otherwise `False`. NOT whether a fix was applied or
        not.
    """

    ast = self.a

    if not isinstance(ast, _decorator_list):
        return False

    lines = self.root._lines

    if not (l := lines[-1]) and l is not old_last_line and len(lines) > 1:  # VERY HACKY check to see if last newline is original, is a bistr so will not be interned empty string, old_last_line must be EXACTLY previous last line and not a copy
        del lines[-1]

        ast.end_lineno -= 1
        ast.end_col_offset = lines[-1].lenbytes

        self._touch()

    return True


def _maybe_fix_decorator_list_del(
        self: fst.FST, start: int, bound_ln: int, old_first_line: str, old_last_line: str
) -> None:
    """Delete from decorator list may need fixing if:
    - Deleted first decorator and an empty line before the start of the decorators was deleted in a `FunctionDef`,
        `AsyncFunctionDef` or `ClassDef`.
    - Deleted last decorator leaving a trailing newline in a `_decorator_list`.
    """

    if _maybe_fix_decorator_list_trailing_newline(self, old_last_line):
        pass  # noop

    elif not start and not old_first_line:  # if del first element and preceding was empty line ...
        root = self.root
        lines = root._lines

        if lines[bound_ln]:  # and that empty line was deleted (because of trivia) then we need to put it back
            lines.insert(bound_ln, bistr(''))

            root._offset(bound_ln, 0, 1, 0)


def _maybe_fix_Set(self: fst.FST, norm: bool | str = True) -> None:
    # assert isinstance(self.a, Set)

    ast = self.a

    if norm and not ast.elts:
        if norm == 'call':
            new_ast, new_src = new_empty_set_call(ast.lineno, ast.col_offset, as_fst=False)
        else:  # True, 'star', 'both'
            new_ast, new_src = new_empty_set_star(ast.lineno, ast.col_offset, as_fst=False)

        ln, col, end_ln, end_col = self.loc

        self._put_src(new_src, ln, col, end_ln, end_col, True)
        self._set_ast(new_ast)


def _maybe_fix_MatchSequence(self: fst.FST, delims: Literal['', '[]', '()'] | None = None) -> str:
    # assert isinstance(self.a, MatchSequence)

    if delims is None:
        delims = self._is_delimited_matchseq()

    body = self.a.patterns

    if len(body) == 1 and not delims.startswith('['):
        self._maybe_ins_separator((f := body[0].f).end_ln, f.end_col, False, self.end_ln, self.end_col - bool(delims))

    if not delims:
        return self._maybe_fix_undelimited_seq(body, '[]')

    return delims


def _maybe_fix_MatchOr(self: fst.FST, norm: bool | str = False) -> None:
    """Maybe fix a `MatchOr` object that may have the wrong location. Will do nothing to a zero-length `MatchOr` and
    will convert a length 1 `MatchOr` to just its single element if `norm` is true.

    **WARNING!** This is currently expecting to be called from slice operations with specific conditions, not guaranteed
    will work on any-old `MatchOr`.
    """

    # assert isinstance(self.a, MatchOr)

    if not (patterns := self.a.patterns):
        return

    lines = self.root._lines
    len_patterns = len(patterns)
    did_par = False

    if not (is_root := self.is_root):  # if not root then it needs ot be fixed here
        if not self._is_enclosed_or_line() and not self._is_enclosed_in_parents():
            self._parenthesize_grouping()  # we do this instead or _sanitize() to keep any trivia, and we do it first to make sure we don't introduce any unenclosed newlines

            did_par = True

    if len_patterns == 1 and norm:
        pat0 = patterns[0]

        del patterns[0]

        self._set_ast(pat0, True)

    else:
        ln, col, end_ln, end_col = patterns[0].f.pars()

        if len_patterns > 1:
            _, _, end_ln, end_col = patterns[-1].f.pars()

        col_offset = lines[ln].c2b(col)
        end_col_offset = lines[end_ln].c2b(end_col)

        _update_loc_up_parents(self, ln + 1, col_offset, end_ln + 1, end_col_offset)

    if is_root:
        if not self._is_enclosed_or_line() and not self._is_enclosed_in_parents():
            self._parenthesize_grouping(False)

            did_par = True

    if not did_par:
        self._maybe_fix_joined_alnum(*self.loc)


def _maybe_fix_stmt_end(
    self: fst.FST, end_lineno: int, end_col_offset: int, old_end_lineno: int, old_end_col_offset: int
) -> None:
    """Fix end of statement that was modified. This sets new end position in self and parents if they originally ended
    on this statement and deals with trailing semicolon issues."""

    self._set_end_pos(end_lineno, end_col_offset, old_end_lineno, old_end_col_offset)

    lines = self.root._lines

    if not (parent := self.parent):  # end bound is end of source
        bound_end_ln = len(lines) - 1
        bound_end_col = len(lines[-1])

    else:
        next_idx = self.pfield.idx + 1
        parent_body = getattr(parent.a, self.pfield.name)

        if next_idx < len(parent_body):  # end bound is beginning of next statement
            bound_end_ln, bound_end_col, _, _ = parent_body[next_idx].f.bloc
        else:  # end bound is end of parent
            _, _, bound_end_ln, bound_end_col = parent.bloc

    _, _, bound_ln, bound_col = self.bloc

    if bound_end_ln == bound_ln:  # if bound ends on same line as starts then we are done because there can not be a trailing semicolon on a different line
        return

    if not (semi := next_find(lines, bound_ln + 1, 0, bound_end_ln, bound_end_col, ';', True)):
        return

    # found a trailing semicolon on a different line, can't let that stand, technically there could be line continuations between us and it that were already there before the operation, but whatever

    # TODO: this is the quick and easy way, the better way to preserve possible comment would be to remove semicolon and adjust start position of any trailing statements, but that involves checking line continuations and possibly dealing with normalizing a block statement which is all semicoloned statements

    semi_ln, semi_col = semi
    semi_col = min(semi_col, len(self._get_indent()))  # try to preserve original space before semicolon, silly, yes

    self._put_src(None, bound_ln, bound_col, semi_ln, semi_col, False)


# ......................................................................................................................
# ours

def _locs_and_bounds_get(
    self: fst.FST, start: int, stop: int, body: list[AST], body2: list[AST], off: int
) -> tuple[fstloc, fstloc, int, int, int, int]:
    """Get the location of the first and last elemnts (assumed present) and the bounding location of a one or
    two-element sequence. The start bounding location must be past the ante-first element if present, otherwise start
    of self past any delimiters. The end bounding location must be end of self before any delimiters.

    **Returns:**
    - `(loc of first element, loc of last element, bound_ln, bound_col, bound_end_ln, bound_end_col)`
    """

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_end_col -= off

    if start:
        _, _, bound_ln, bound_col = body2[start - 1].f.pars()
    else:
        bound_col += off

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body2)

    return loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col


def _cut_or_copy_asts(start: int, stop: int, field: str, cut: bool, body: list[AST]) -> list[AST]:
    if not cut:
        asts = [copy_ast(body[i]) for i in range(start, stop)]

    else:
        asts = body[start : stop]

        del body[start : stop]

        for i in range(start, len(body)):
            body[i].f.pfield = astfield(field, i)

    return asts


def _cut_or_copy_asts2(
    start: int, stop: int, field: str, field2: str, cut: bool, body: list[AST], body2: list[AST]
) -> tuple[list[AST], list[AST]]:
    if not cut:
        asts = [copy_ast(body[i]) for i in range(start, stop)]
        asts2 = [copy_ast(body2[i]) for i in range(start, stop)]

    else:
        asts = body[start : stop]
        asts2 = body2[start : stop]

        del body[start : stop]
        del body2[start : stop]

        for i in range(start, len(body)):
            body2[i].f.pfield = astfield(field2, i)

            if ast := body[i]:  # could be None from Dict **
                ast.f.pfield = astfield(field, i)

    return asts, asts2


# ......................................................................................................................

def _get_slice_NOT_IMPLEMENTED_YET(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    raise NotImplementedError('this is not implemented yet')


def _get_slice_Tuple_elts(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Tuple` slice is just a normal `Tuple`. It attempts to copy the parenthesization of the parent. The converse is
    not always true as a `Tuple` may serve as the container of a slice of other node types."""

    ast = self.a
    body = ast.elts
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return new_empty_tuple(from_=self)

    is_par = self._is_delimited_seq()
    locs = _locs_and_bounds_get(self, start, stop, body, body, is_par)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx = ast.ctx.__class__
    ret_ast = Tuple(elts=asts, ctx=ctx())

    if not issubclass(ctx, Load):  # new Tuple root object must have ctx=Load
        set_ctx(ret_ast, Load)

    if is_par:
        prefix, suffix = '()'
    else:
        prefix = suffix = ''

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', prefix, suffix, ',', 1, 1)

    if not is_par:
        fst_._maybe_fix_tuple(False)

    fst_._maybe_fix_arglikes(options)  # parenthesize any arglike expressions (could have come from a slice)

    if cut:
        self._maybe_fix_tuple(is_par)

    return fst_


def _get_slice_List_elts(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `List` slice is just a normal `List`."""

    ast = self.a
    body = ast.elts
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(List(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['[]'], None, from_=self)

    locs = _locs_and_bounds_get(self, start, stop, body, body, 1)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx = ast.ctx.__class__
    ret_ast = List(elts=asts, ctx=ctx())  # we set ctx() so that if it is not Load then set_ctx() below will recurse into it

    if not issubclass(ctx, Load):  # new List root object must have ctx=Load
        set_ctx(ret_ast, Load)

    return get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', '[', ']', ',', 0, 0)


def _get_slice_Set_elts(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Set` slice is just a normal `Set` when it has elements. In the case of a zero-length `Set` it may be
    represented as `{*()}` or `set()` or as an invalid `AST` `Set` with curlies but no elements, according to
    options."""

    body = self.a.elts
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        get_norm = _get_option_norm('norm_get', 'set_norm', options)

        return (
            new_empty_set_curlies(from_=self) if not get_norm else
            new_empty_set_call(from_=self) if get_norm == 'call' else
            new_empty_set_star(from_=self)  # True, 'star', 'both'
        )

    locs = _locs_and_bounds_get(self, start, stop, body, body, 1)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ret_ast = Set(elts=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', '{', '}', ',', 0, 0)

    if cut:
        _maybe_fix_Set(self, _get_option_norm('norm_self', 'set_norm', options))

    return fst_


def _get_slice_Dict__all(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Dict` slice is just a normal `Dict`."""

    ast = self.a
    body = ast.keys
    len_body = len(body)
    body2 = ast.values
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(Dict(keys=[], values=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['{}'], None, from_=self)

    locs = _locs_and_bounds_get(self, start, stop, body, body2, 1)
    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'values', cut, body, body2)
    ret_ast = Dict(keys=asts, values=asts2)

    return get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
                         options, 'values', '{', '}', ',', 0, 0)


def _get_slice_Delete_targets(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """The slice of `Delete.targets` is a normal unparenthesized `Tuple` contianing valid target types, which is also a
    valid python `Tuple`."""

    ast = self.a
    body = ast.targets
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return new_empty_tuple(from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError("cannot cut all Delete.targets without norm_self=False")

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_Delete_targets(self, start, loc_first)

    asts = _cut_or_copy_asts(start, stop, 'targets', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Del())  # we initially set to Del so that set_ctx() won't skip it

    set_ctx(ret_ast, Load)  # new Tuple root object must have ctx=Load

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'targets', '', '', ',', False, 1)

    fst_._maybe_fix_tuple(False)

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_fix_stmt_end(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                                ast.end_lineno, ast.end_col_offset)

        ln, col, _, _ = self.loc

        self._maybe_fix_joined_alnum(ln, col + 3)
        self._maybe_add_line_continuations()

    return fst_


def _get_slice_Assign_targets(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    body = self.a.targets
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_Assign_targets(targets=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError("cannot cut all Assign.targets without norm_self=False")

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_Assign_targets(self, start, loc_first)

    asts = _cut_or_copy_asts(start, stop, 'targets', cut, body)
    ret_ast = _Assign_targets(targets=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'targets', '', '', '=', True, True)

    if cut:
        _maybe_fix_Assign_target0(self)
        self._maybe_add_line_continuations()

    return fst_


def _get_slice_With_AsyncWith_items(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    ast = self.a
    body = ast.items
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_withitems(items=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError(f'cannot cut all {ast.__class__.__name__}.items without norm_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if start == stop - 1 else body[stop - 1].f.loc

    pars = self._loc_With_items_pars()  # may be pars or may be where pars would go from just after `with` to end of block header
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln = pars_ln
        bound_col = pars_col + pars_n

    asts = _cut_or_copy_asts(start, stop, 'items', cut, body)
    ret_ast = _withitems(items=asts)
    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, pars_end_ln, pars_end_col - pars_n,
                         options, 'items', '', '', ',', False, False)

    if cut and not pars_n:  # only need to fix maybe if there are no parentheses
        if not self._is_enclosed_or_line(pars=False):  # if cut and no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_With_items_pars()  # will just give where pars should go (because maybe something like `async \\\n\\\n   with ...`)

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, False)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        elif not start and len_slice != len_body:  # if not adding pars then need to make sure cut didn't join new first `withitem` with the `with`
            ln, col, _, _ = pars.bound

            self._maybe_fix_joined_alnum(ln, col)

    return fst_


def _get_slice_Import_names(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    ast = self.a
    body = ast.names
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_aliases(names=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError('cannot cut all Import.names without norm_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if start == stop - 1 else body[stop - 1].f.loc

    _, _, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln, bound_col, _, _ = loc_first

    asts = _cut_or_copy_asts(start, stop, 'names', cut, body)
    ret_ast = _aliases(names=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'names', '', '', ',', False, False)

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                ast.end_lineno, ast.end_col_offset)

        self._maybe_add_line_continuations()

    return fst_


def _get_slice_ImportFrom_names(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    ast = self.a
    body = ast.names
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_aliases(names=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError('cannot cut all ImportFrom.names without norm_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if start == stop - 1 else body[stop - 1].f.loc

    pars = self._loc_ImportFrom_names_pars()  # may be pars or may be where pars would go from just after `import` to end of node
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.loc
    else:
        bound_ln = pars_ln
        bound_col = pars_col + pars_n

    asts = _cut_or_copy_asts(start, stop, 'names', cut, body)
    ret_ast = _aliases(names=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, pars_end_ln, pars_end_col - pars_n,
                         options, 'names', '', '', ',', False, False)

    if cut and not pars_n:  # only need to fix maybe if there are no parentheses
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                ast.end_lineno, ast.end_col_offset)

        if not self._is_enclosed_or_line(pars=False):  # if cut and no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ImportFrom_names_pars()

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, True, False, self)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

    return fst_


def _get_slice_Global_Nonlocal_names(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    ast = self.a
    len_body = len(ast.names)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return new_empty_tuple(from_=self)

    if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
        raise ValueError(f'cannot cut all {ast.__class__.__name__}.names without norm_self=False')

    ln, end_col, bound_end_ln, bound_end_col = self.loc

    lines = self.root._lines
    ret_elts = []
    ret_ast = Tuple(elts=ret_elts, ctx=Load())
    end_col += 5 if isinstance(ast, Global) else 7  # will have another +1 added in search

    if not start:
        bound_ln = None  # set later

    else:
        for _ in range(start - 1):
            ln, end_col = next_find(lines, ln, end_col + 1, bound_end_ln, bound_end_col, ',')  # must be there

        bound_ln, bound_col, src = next_find_re(lines, ln, end_col + 1, bound_end_ln, bound_end_col, re_identifier)  # must be there, + 1 skips comma

        bound_col += len(src)
        ln, end_col = next_find(lines, bound_ln, bound_col, bound_end_ln, bound_end_col, ',')  # must be there

    for i in range(stop - start):  # create tuple of Names from identifiers
        ln, col, src = next_find_re(lines, ln, end_col + 1, bound_end_ln, bound_end_col, re_identifier)  # must be there, + 1 probably skips comma
        lineno = ln + 1
        end_col = col + len(src)

        if not i:
            loc_first = fstloc(ln, col, ln, end_col)

            if bound_ln is None:
                bound_ln = ln
                bound_col = col

        ret_elts.append(Name(id=src, ctx=Load(), lineno=lineno, col_offset=(l := lines[ln]).c2b(col), end_lineno=lineno,
                             end_col_offset=l.c2b(end_col)))

    loc_last = fstloc(ln, col, ln, end_col)

    if cut:
        del ast.names[start : stop]

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, ret_elts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'names', '', '', ',', False, 1)

    fst_._maybe_fix_tuple(False)  # this is in case of multiline elements to add pars, otherwise location would reparse different

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _maybe_fix_stmt_end(self, bound_ln + 1, lines[bound_ln].c2b(bound_col), ast.end_lineno, ast.end_col_offset)

        self._maybe_add_line_continuations()

    return fst_


def _get_slice_ClassDef_bases(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `ClassDef.bases` slice is just a normal `Tuple`, with possibly expr_arglike elements which are invalid in a
    normal expression tuple."""

    ast = self.a
    body = ast.bases
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if start == stop:
        return new_empty_tuple(from_=self)

    if keywords := ast.keywords:
        kw0_pos = keywords[0].f.loc[:2]

        if kw0_pos < body[stop - 1].f.loc[2:]:
            raise NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')

        self_tail_sep = True if body[-1].f.loc[2:] < kw0_pos else None

    else:
        self_tail_sep = None

    bound_ln, bound_col, bound_end_ln, bound_end_col = self._loc_ClassDef_bases_pars()  # definitely exist
    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    asts = _cut_or_copy_asts(start, stop, 'bases', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'bases', '(', ')', ',', self_tail_sep, len_slice == 1)

    fst_._maybe_fix_arglikes(options)  # parenthesize any arglike expressions

    if cut:
        if keywords:
            if cut and start and stop == len_body:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
                self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

        elif not body:  # everything was cut and no keywords, remove parentheses
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ClassDef_bases_pars()  # definitely exist

            self._put_src(None, pars_ln, pars_col, pars_end_ln, pars_end_col, False)

    return fst_


def _get_slice_Boolop_values(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Here we need to deal with possibly deleting a leading or trailing operator and getting the proper trivia from
    before or after it."""

    ast = self.a
    body = ast.values
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    is_first = not start
    is_last = stop == len_body
    norm_get = get_option_overridable('norm', 'norm_get', options)
    norm_self = get_option_overridable('norm', 'norm_self', options)

    if not len_slice:
        if norm_get:
            raise ValueError("cannot get empty slice from BoolOp without 'norm_get=False'")

        return fst.FST(BoolOp(op=ast.op.__class__(), values=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    if cut and len_slice == len_body and norm_self:
        raise ValueError("cannot cut all BoolOp.values without 'norm_self=False'")

    loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col = (
        _locs_and_bounds_get(self, start, stop, body, body, 0))

    # include location of possible extra operator on either side of slice

    lines = self.root._lines
    sep = 'and' if isinstance(ast.op, And) else 'or'

    op_side_left = _get_option_op_side(is_first, is_last, options)

    if op_side_left:  # include left side operator in location of first element so that trivia search starts before it
        ln, col, end_ln, end_col = loc_first
        ln, col, src = next_frag(lines, bound_ln, bound_col, ln, col)  # must be there, op
        loc_first = fstloc(ln, col, end_ln, end_col)

        assert src.startswith(sep)

    elif op_side_left is False:  # include right side operator in location of last element so that trivia search starts past it
        ln, col, end_ln, end_col = loc_last
        end_ln, end_col, src = next_frag(lines, end_ln, end_col, bound_end_ln, bound_end_col)  # must be there, op
        loc_last = fstloc(ln, col, end_ln, end_col + len(sep))

        assert src.startswith(sep)

    # do the thing

    asts = _cut_or_copy_asts(start, stop, 'values', cut, body)
    ret_ast = BoolOp(op=ast.op.__class__(), values=asts)

    fst_ = get_slice_nosep(self, start, stop, len_body, cut, ret_ast,
                           loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col, options)

    # remove possible extra operator on either side of slice

    fst_lines = fst_._lines
    fst_body = fst_.a.values

    if op_side_left:  # remove left side leading operator
        end_ln, end_col, _, _ = fst_body[0].f.pars()
        ln, col, src = next_frag(fst_lines, 0, 0, end_ln, end_col)  # must be there, op

        if ln == end_ln:  # if on same line as first element then delete everything from start of operator to start of element
            fst_._put_src(None, ln, col, end_ln, end_col, True)
        elif not fst_lines[ln].strip():  # if operator only thing on the line (incuding comments and line continuations) then nuke the whole line
            fst_._put_src(None, ln, 0, ln, 0x7fffffffffffffff, True)
        else:  # otherwise just remove operator
            fst_._put_src(None, ln, col, ln, col + len(sep), True)

    elif op_side_left is False:  # remove right side trailing operator source
        _, _, ln, col = fst_body[-1].f.pars()
        end_ln, end_col, src = next_frag(fst_lines, ln, col, len(fst_lines) - 1, 0x7fffffffffffffff)  # must be there, op

        if end_ln == ln:  # if on same line as last element then delete everything from end of element to end of operator
            fst_._put_src(None, ln, col, end_ln, end_col + len(sep), True)
        elif not fst_lines[end_ln].strip():  # if operator only thing on the line (incuding comments and line continuations) then nuke the whole line
            fst_._put_src(None, end_ln, 0, end_ln, 0x7fffffffffffffff, True)
        else:  # otherwise just remove operator source
            fst_._put_src(None, end_ln, end_col, end_ln, end_col + len(sep), True)

    # rest of cleanups

    _maybe_fix_naked_seq_loc(fst_, fst_body)

    if len(fst_body) == 1 and norm_get:  # if only one element gotten and normalizing then replace the BoolOp AST in fst_ with the single `values` AST which it has
        fst_._set_ast(fst_body.pop(), True)

    if cut:
        _maybe_fix_BoolOp(self, start, cut, is_last, options, norm_self)

    return fst_


def _get_slice_Compare__all(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Slice from whole `Compare`, including `left` field. Can never get empty slice or leave empty self. Length 1
    `Compare` will be returned / left as a `Compare` without `ops` or `comparators` with `norm=False`, otherwise will be
    returned / left as a single `expr` with `norm=True`."""

    ast = self.a
    body = ast.comparators
    len_body = len(body) + 1  # +1 to include `left` element
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    is_first = not start
    is_last = stop == len_body
    norm_get = get_option_overridable('norm', 'norm_get', options)
    norm_self = get_option_overridable('norm', 'norm_self', options)

    if not len_slice:
        raise ValueError("cannot get empty slice from Compare")

    if cut:
        if len_slice == len_body:
            raise ValueError("cannot cut all nodes from Compare")

    _move_Compare_left_into_comparators(self)  # we put everything into `comparators` for the sake of sanity (relatively speaking)

    loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col = (
        _locs_and_bounds_get(self, start, stop, body, body, 0))

    # include location of possible extra operator on either side of slice

    lines = self.root._lines
    ops = ast.ops

    op_side_left = _get_option_op_side(is_first, is_last, options)

    if op_side_left is False:  # include right side operator in location of last element so that trivia search starts past it
        ln, col, _, _ = loc_last
        _, _, end_ln, end_col = ops[stop].f.loc
        loc_last = fstloc(ln, col, end_ln, end_col)

        fst_body = _cut_or_copy_asts(start, stop, 'comparators', cut, body)
        asts_ops = _cut_or_copy_asts(start + 1, stop + 1, 'ops', cut, ops)

        lineno = end_ln + 1
        col_offset = lines[end_ln].c2b(end_col)

        fst_body.append(Pass(lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset))  # placeholders for location calculations
        asts_ops.insert(0, Pass(lineno=1, col_offset=0, end_lineno=1, end_col_offset=0))

    else:
        if op_side_left:  # include left side operator in location of first element so that trivia search starts before it
            _, _, end_ln, end_col = loc_first
            ln, col, _, _ = ops[start].f.loc
            loc_first = fstloc(ln, col, end_ln, end_col)

        fst_body = _cut_or_copy_asts(start, stop, 'comparators', cut, body)
        asts_ops = _cut_or_copy_asts(start, stop, 'ops', cut, ops)

    # do the thing

    ret_ast = Compare(left=Pass(lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),  # left is placeholder for location calculations
                      ops=asts_ops, comparators=fst_body)

    fst_ = get_slice_nosep(self, start, stop, len_body, cut, ret_ast,
                           loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col, options)

    for op in asts_ops:  # we need to explicitly clean out ops caches because location has changed but these were not "._touch()ed" in get_slice_nosep() because that only dealt with the comparators
        op.f._touch()

    # remove possible extra operator on either side of slice

    fst_lines = fst_._lines

    if op_side_left:  # remove left side leading operator
        op0f = asts_ops[0].f
        op_ln, op_col, op_end_ln, op_end_col = op0f.loc
        left_ln, left_col, _, _ = fst_body[0].f.pars()

        if op_end_ln == left_ln:  # if op ends on same line as first element then delete everything from start of operator to start of element
            fst_._put_src(None, op_ln, op_col, left_ln, left_col, True)
        elif fst_lines[op_ln][:op_col].isspace() and fst_lines[op_end_ln][op_end_col:].isspace():  # if operator only thing on its line(s) (incuding comments and line continuations, except for anything inside ('is not', 'not in')) then nuke the whole line(s)
            fst_._put_src(None, op_ln, 0, op_end_ln, 0x7fffffffffffffff, True)
        else:  # otherwise just remove operator source
            fst_._put_src(None, op_ln, op_col, op_end_ln, op_end_col, True)

        op0f._unmake_fst_tree()  # delete left operator AST and replace with placeholder for correct location calculations

        asts_ops[0] = fst.FST(Pass(lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), fst_, astfield('ops', 0)).a

    else:
        if isinstance(op0 := asts_ops[0], Pass):  # first operator is placeholder which was not offset in get_slice_nosep() so assign temporary location here
            op0.lineno = op0.end_lineno = 1
            op0.col_offset = op0.end_col_offset = 0

        if op_side_left is False:  # remove right side trailing operator and placeholder comparator
            _, _, last_end_ln, last_end_col = fst_body[-2].f.pars()
            opnf = asts_ops.pop().f
            op_ln, op_col, op_end_ln, op_end_col = opnf.loc

            if op_ln == last_end_ln:  # if op starts on same line as last element ends then delete everything from end of element to end of operator
                fst_._put_src(None, last_end_ln, last_end_col, op_end_ln, op_end_col, True)
            elif fst_lines[op_ln][:op_col].isspace() and fst_lines[op_end_ln][op_end_col:].isspace():  # if operator only thing on its line(s) (incuding comments and line continuations, except for anything inside ('is not', 'not in')) then nuke the whole line(s)
                fst_._put_src(None, op_ln, 0, op_end_ln, 0x7fffffffffffffff, True)
            else:  # otherwise just remove operator source
                fst_._put_src(None, op_ln, op_col, op_end_ln, op_end_col, True)

            opnf._unmake_fst_tree()  # delete right operator AST and comparator placeholder AST
            fst_body.pop().f._unmake_fst_tree()

    # rest of cleanups

    _maybe_fix_naked_seq_loc(fst_, fst_body)

    if len(fst_body) == 1 and norm_get:  # if only one element gotten and normalizing then replace the Compare AST in fst_ with the single `comparators` AST which it has, don't need to unmake `left` since it is None at this point
        fst_._set_ast(fst_body.pop(), True)  # this will unmake the leftmost operator fine, placeholder or op_side left or rotated right
    else:
        _move_Compare_first_comparator_into_left(fst_)

    if cut:
        _maybe_fix_Compare(self, start, True, is_last, options, norm_self)
    else:
        _move_Compare_first_comparator_into_left(self)

    return fst_


def _get_slice_Call_args(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Call.args` slice is just a normal `Tuple`, with possibly expr_arglike elements which are invalid in a normal
    expression tuple."""

    ast = self.a
    body = ast.args
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if start == stop:
        return new_empty_tuple(from_=self)

    if keywords := ast.keywords:
        kw0_pos = keywords[0].f.loc[:2]

        if kw0_pos < body[stop - 1].f.loc[2:]:
            raise NodeError('cannot get this Call.args slice because it includes parts after a keyword')

        self_tail_sep = True if body[-1].f.loc[2:] < kw0_pos else None

    else:
        self_tail_sep = None

        if body and (f0 := body[0].f)._is_solo_call_arg_genexp() and f0.pars(shared=False).n == -1:  # single call argument GeneratorExp shares parentheses with Call?
            f0._parenthesize_grouping()

    bound_ln, bound_col, bound_end_ln, bound_end_col = self._loc_Call_pars()
    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    asts = _cut_or_copy_asts(start, stop, 'args', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'args', '(', ')', ',', self_tail_sep, len_slice == 1)

    fst_._maybe_fix_arglikes(options)  # parenthesize any arglike expressions

    if cut and start and keywords and stop == len_body:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
        self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

    return fst_


def _get_slice_decorator_list(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """This handles `FunctionDef`, `AsyncFunctionDef`, `ClassDef` and the `_decorator_list` SPECIAL SLICE. Since a
    decorator list is a very unique slice we need to do more fixing than ususal for newlines here."""

    ast = self.a
    body = ast.decorator_list
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_decorator_list(decorator_list=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    loc_first = self._loc_decorator(start)
    loc_last = loc_first if start == stop - 1 else self._loc_decorator(stop - 1)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_decorator_list(self, start)

    if cut:  # for fixes after cut
        lines = self.root._lines
        old_first_line = lines[bound_ln]
        old_last_line = lines[-1]

    asts = _cut_or_copy_asts(start, stop, 'decorator_list', cut, body)
    ret_ast = _decorator_list(decorator_list=asts)

    fst_ = get_slice_nosep(self, start, stop, len_body, cut, ret_ast,
                           loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col, options)

    fst_lines = fst_._lines  # decorators always live on their own line so strip ugly leading and trailing newline (except for decorator 0 which will not have a leading newline)

    if not fst_lines[-1]:  # last element from _decorator_list may not have trailing newline
        del fst_lines[-1]

        ast_ = fst_.a
        ast_.end_lineno -= 1
        ast_.end_col_offset = fst_lines[-1].lenbytes

        fst_._touch()

    if not fst_lines[0]:  # first element starting at line 0 will not have trailing newline
        del fst_lines[0]

        fst_._offset(1, 0, -1, 0)

    if cut:
        _maybe_fix_decorator_list_del(self, start, bound_ln, old_first_line, old_last_line)

    return fst_


def _get_slice_generators(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """This handles `ListComp`, `SetComp`, `DictComp`, `GeneratorExp` and the `_comprehensions` SPECIAL SLICE."""

    ast = self.a
    body = ast.generators
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_comprehensions(generators=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    if not isinstance(ast, _comprehensions):
        if cut and len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError(f'cannot cut all {ast.__class__.__name__}.generators without norm_self=False')

    loc_first = body[start].f.loc
    loc_last = loc_first if start == stop - 1 else body[stop - 1].f.loc

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_generators(self, start)

    asts = _cut_or_copy_asts(start, stop, 'generators', cut, body)
    ret_ast = _comprehensions(generators=asts)

    fst_ = get_slice_nosep(self, start, stop, len_body, cut, ret_ast,
                           loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col, options)

    return fst_


def _get_slice_comprehension_ifs(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """This handles `comprehension` and the `_comprehension_ifs` SPECIAL SLICE."""

    ast = self.a
    body = ast.ifs
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(_comprehension_ifs(ifs=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    loc_first = self._loc_comprehension_if(start)
    loc_last = loc_first if start == stop - 1 else self._loc_comprehension_if(stop - 1)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_comprehension_ifs(self, start)

    asts = _cut_or_copy_asts(start, stop, 'ifs', cut, body)
    ret_ast = _comprehension_ifs(ifs=asts)

    fst_ = get_slice_nosep(self, start, stop, len_body, cut, ret_ast,
                           loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col, options)

    return fst_


def _get_slice_MatchSequence_patterns(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `MatchSequence` slice is just a normal `MatchSequence`. It attempts to copy the parenthesization of the
    parent."""

    body = self.a.patterns
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(MatchSequence(patterns=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['[]'], None, from_=self)

    delims = self._is_delimited_matchseq()
    locs = _locs_and_bounds_get(self, start, stop, body, body, bool(delims))
    asts = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchSequence(patterns=asts)

    if delims:
        prefix, suffix = delims
        tail_sep = 1 if delims == '()' else 0

    else:
        prefix = suffix = delims = ''
        tail_sep = 1

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'patterns', prefix, suffix, ',', tail_sep, tail_sep)

    if not delims:
        _maybe_fix_MatchSequence(fst_, '')

    if cut:
        _maybe_fix_MatchSequence(self, delims)

    return fst_


def _get_slice_MatchMapping__all(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `MatchMapping` slice is just a normal `MatchMapping`."""

    ast = self.a
    body = ast.keys
    body2 = ast.patterns
    rest = ast.rest
    len_body = len(body) + bool(rest)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(MatchMapping(keys=[], patterns=[], rest=None, lineno=1, col_offset=0, end_lineno=1,
                                    end_col_offset=2),
                       ['{}'], None, from_=self)

    if with_rest := (rest and stop == len_body):  # if slice includes rest then add it as temporary `**rest` node so it can be processed like the rest of the sequence
        _add_MatchMapping_rest_as_real_node(self)

    locs = _locs_and_bounds_get(self, start, stop, body, body2, 1)
    asts, asts2 = _cut_or_copy_asts2(start, stop, 'keys', 'patterns', cut, body, body2)
    ret_ast = MatchMapping(keys=asts, patterns=asts2, rest=rest if with_rest else None)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts2[-1], *locs,
                        options, 'patterns', '{', '}', ',', 0, 0)

    if with_rest:
        _remove_MatchMapping_rest_real_node(fst_)  # we know this contains the temporary .rest node

        if cut:  # temporary .rest node was cut
            ast.rest = None
        else:  # otherwise remove the temporary node
            _remove_MatchMapping_rest_real_node(self)

    return fst_


def _get_slice_MatchOr_patterns(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `MatchOr` slice is just a normal `MatchOr` when it has two elements or more. If it has one it may be returned
    as a single `pattern` or as an invalid single-element `MatchOr`. If the slice would wind up with zero elements it
    may raise and exception or return an invalid zero-element `MatchOr`, as specified by options."""

    body = self.a.patterns
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    get_norm = _get_option_norm('norm_get', 'matchor_norm', options)
    self_norm = _get_option_norm('norm_self', 'matchor_norm', options)

    if not len_slice:
        if get_norm:
            raise ValueError("cannot get empty slice from MatchOr without norm_get=False")

        return fst.FST(MatchOr(patterns=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    if len_slice == 1 and get_norm == 'strict':
        raise ValueError("cannot get length 1 slice from MatchOr with norm_get='strict'")

    if cut:
        if not (len_left := len_body - len_slice):
            if self_norm:
                raise ValueError("cannot cut all MatchOr.patterns without norm_self=False")

        elif len_left == 1 and self_norm == 'strict':
            raise ValueError("cannot cut MatchOr to length 1 with norm_self='strict'")

    locs = _locs_and_bounds_get(self, start, stop, body, body, 0)
    asts = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchOr(patterns=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'patterns', '', '', '|', False, False)

    _maybe_fix_MatchOr(fst_, bool(get_norm))

    if cut:
        _maybe_fix_MatchOr(self, bool(self_norm))

    return fst_


def _get_slice_type_params(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    ast = self.a
    body = ast.type_params
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(_type_params([], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], None, from_=self)

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_func = (
        fst.FST._loc_TypeAlias_type_params_brackets if isinstance(ast, TypeAlias) else
        fst.FST._loc_ClassDef_type_params_brackets if isinstance(ast, ClassDef) else
        fst.FST._loc_FunctionDef_type_params_brackets  # FunctionDef, AsyncFunctionDef
    )

    (bound_ln, bound_col, bound_end_ln, bound_end_col), _ = bound_func(self)

    bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    else:
        bound_col += 1

    asts = _cut_or_copy_asts(start, stop, 'type_params', cut, body)
    ret_ast = _type_params(type_params=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'type_params', '', '', ',', False, False)

    if cut and not body:  # everything was cut, need to remove brackets
        (_, _, bound_end_ln, bound_end_col), (name_ln, name_col) = bound_func(self)

        self._put_src(None, name_ln, name_col, bound_end_ln, bound_end_col, False)

    return fst_


def _get_slice__slice(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Our own general non-AST-compatible slice of some `type[AST]` list field."""

    ast = self.a
    kls = ast.__class__
    static = fst_package.fst_put_slice._SPECIAL_SLICE_STATICS[kls]
    body = getattr(ast, field)
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(kls([], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], None, from_=self)

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()

    asts = _cut_or_copy_asts(start, stop, field, cut, body)
    ret_ast = kls(asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, field, '', '', static.sep, static.self_tail_sep, static.ret_tail_sep)

    return fst_


_GET_SLICE_HANDLERS = {
    (Module, 'body'):                         get_slice_stmtish,  # stmt*
    (Interactive, 'body'):                    get_slice_stmtish,  # stmt*
    (FunctionDef, 'body'):                    get_slice_stmtish,  # stmt*
    (AsyncFunctionDef, 'body'):               get_slice_stmtish,  # stmt*
    (ClassDef, 'body'):                       get_slice_stmtish,  # stmt*
    (For, 'body'):                            get_slice_stmtish,  # stmt*
    (For, 'orelse'):                          get_slice_stmtish,  # stmt*
    (AsyncFor, 'body'):                       get_slice_stmtish,  # stmt*
    (AsyncFor, 'orelse'):                     get_slice_stmtish,  # stmt*
    (While, 'body'):                          get_slice_stmtish,  # stmt*
    (While, 'orelse'):                        get_slice_stmtish,  # stmt*
    (If, 'body'):                             get_slice_stmtish,  # stmt*
    (If, 'orelse'):                           get_slice_stmtish,  # stmt*
    (With, 'body'):                           get_slice_stmtish,  # stmt*
    (AsyncWith, 'body'):                      get_slice_stmtish,  # stmt*
    (Try, 'body'):                            get_slice_stmtish,  # stmt*
    (Try, 'orelse'):                          get_slice_stmtish,  # stmt*
    (Try, 'finalbody'):                       get_slice_stmtish,  # stmt*
    (TryStar, 'body'):                        get_slice_stmtish,  # stmt*
    (TryStar, 'orelse'):                      get_slice_stmtish,  # stmt*
    (TryStar, 'finalbody'):                   get_slice_stmtish,  # stmt*
    (ExceptHandler, 'body'):                  get_slice_stmtish,  # stmt*
    (match_case, 'body'):                     get_slice_stmtish,  # stmt*

    (Match, 'cases'):                         get_slice_stmtish,  # match_case*
    (Try, 'handlers'):                        get_slice_stmtish,  # excepthandler*
    (TryStar, 'handlers'):                    get_slice_stmtish,  # excepthandler* ('except*')

    (Tuple, 'elts'):                          _get_slice_Tuple_elts,  # expr*
    (List, 'elts'):                           _get_slice_List_elts,  # expr*
    (Set, 'elts'):                            _get_slice_Set_elts,  # expr*

    (Dict, '_all'):                           _get_slice_Dict__all,  # key:value*

    (FunctionDef, 'decorator_list'):          _get_slice_decorator_list,  # expr*
    (AsyncFunctionDef, 'decorator_list'):     _get_slice_decorator_list,  # expr*
    (ClassDef, 'decorator_list'):             _get_slice_decorator_list,  # expr*
    (ClassDef, 'bases'):                      _get_slice_ClassDef_bases,  # expr*
    (Delete, 'targets'):                      _get_slice_Delete_targets,  # expr*
    (Assign, 'targets'):                      _get_slice_Assign_targets,  # expr*
    (BoolOp, 'values'):                       _get_slice_Boolop_values,  # expr*
    (Compare, '_all'):                        _get_slice_Compare__all,  # expr*
    (Call, 'args'):                           _get_slice_Call_args,  # expr*
    (comprehension, 'ifs'):                   _get_slice_comprehension_ifs,  # expr*

    (ListComp, 'generators'):                 _get_slice_generators,  # comprehension*
    (SetComp, 'generators'):                  _get_slice_generators,  # comprehension*
    (DictComp, 'generators'):                 _get_slice_generators,  # comprehension*
    (GeneratorExp, 'generators'):             _get_slice_generators,  # comprehension*

    (ClassDef, 'keywords'):                   _get_slice_NOT_IMPLEMENTED_YET,  # keyword*
    (Call, 'keywords'):                       _get_slice_NOT_IMPLEMENTED_YET,  # keyword*

    (Import, 'names'):                        _get_slice_Import_names,  # alias*
    (ImportFrom, 'names'):                    _get_slice_ImportFrom_names,  # alias*

    (With, 'items'):                          _get_slice_With_AsyncWith_items,  # withitem*
    (AsyncWith, 'items'):                     _get_slice_With_AsyncWith_items,  # withitem*

    (MatchSequence, 'patterns'):              _get_slice_MatchSequence_patterns,  # pattern*
    (MatchMapping, '_all'):                   _get_slice_MatchMapping__all,  # key:pattern*
    (MatchClass, 'patterns'):                 _get_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchOr, 'patterns'):                    _get_slice_MatchOr_patterns,  # pattern*

    (FunctionDef, 'type_params'):             _get_slice_type_params,  # type_param*
    (AsyncFunctionDef, 'type_params'):        _get_slice_type_params,  # type_param*
    (ClassDef, 'type_params'):                _get_slice_type_params,  # type_param*
    (TypeAlias, 'type_params'):               _get_slice_type_params,  # type_param*

    (Global, 'names'):                        _get_slice_Global_Nonlocal_names,  # identifier*
    (Nonlocal, 'names'):                      _get_slice_Global_Nonlocal_names,  # identifier*

    (JoinedStr, 'values'):                    _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (TemplateStr, 'values'):                  _get_slice_NOT_IMPLEMENTED_YET,  # expr*

    (_ExceptHandlers, 'handlers'):            get_slice_stmtish,  # ExceptHandler*
    (_match_cases, 'cases'):                  get_slice_stmtish,  # match_case*
    (_Assign_targets, 'targets'):             _get_slice__slice,  # expr*
    (_decorator_list, 'decorator_list'):      _get_slice_decorator_list,  # expr*
    (_comprehensions, 'generators'):          _get_slice_generators,  # comprehensions*
    (_comprehension_ifs, 'ifs'):              _get_slice_comprehension_ifs,  # exprs*
    (_aliases, 'names'):                      _get_slice__slice,  # alias*
    (_withitems, 'items'):                    _get_slice__slice,  # withitem*
    (_type_params, 'type_params'):            _get_slice__slice,  # type_param*
}


# ----------------------------------------------------------------------------------------------------------------------
# FST class methods

def _get_slice(
    self: fst.FST,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Get a slice of child nodes from `self`."""

    if not (handler := _GET_SLICE_HANDLERS.get((self.a.__class__, field))):
        raise ValueError(f'cannot get slice from {self.a.__class__.__name__}.{field}')

    if cut:
        with self._modifying(field):
            return handler(self, start, stop, field, cut, options)

    return handler(self, start, stop, field, cut, options)
