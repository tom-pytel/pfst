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
    Lambda,
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
    arg,
    arguments,
    comprehension,
    keyword,
    match_case,
    TryStar,
    TypeAlias,
    TemplateStr,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _arglikes,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from .astutil import re_identifier, bistr, copy_ast

from .common import (
    re_empty_space,
    NodeError,
    astfield,
    fstloc,
    next_frag,
    next_find,
    next_find_re,
)

from .fst_misc import (
    new_empty_set_star,
    new_empty_set_call,
    new_empty_set_curlies,
    fixup_slice_indices,
)

from .slice_stmtlike import get_slice_stmtlike

from .slice_exprlike import (
    _LocationAbstract,
    get_slice_sep,
    get_slice_nosep,
    put_slice_sep_begin,
    put_slice_sep_end,
)


_re_empty_line_start_maybe_cont_0 = re.compile(r'[ \t]*\\?')  # empty line start with maybe continuation
_re_empty_line_start_maybe_cont_1 = re.compile(r'[ \t]+\\?')  # empty line start with maybe continuation WITH AT LEAST 1 leading whitespace


class _LocationAbstract_arguments(_LocationAbstract):
    """Gives the location of each `arguments` `arg` along with its default value if it has one. The tail node is always
    the default if present, otherwise the arg. The `body` here should be created using
    `_make_arguments_allargs_w_markers()`."""

    def tail_node(self, idx: int) -> AST:
        a = self.body[idx]
        f = a.f

        if a.__class__ is arg and (g := f.next()) and g.pfield.name in ('defaults', 'kw_defaults'):
            return g.a

        return a

    def loc_head(self, idx: int) -> fstloc:
        a = self.body[idx]
        f = a.f

        return f.loc if a.__class__ is Pass else f._loc_argument(True)


# ......................................................................................................................

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


def _locs_first_and_last(
    self: fst.FST, start: int, stop: int, body: list[AST], body2: list[AST]
) -> tuple[fstloc, fstloc]:
    """Get the location of the first and last elemnts of a one or two-element sequence (assumed present)."""

    stop_1 = stop - 1

    if body2 is body:
        loc_first = body[start].f.pars()
        loc_last = loc_first if start == stop_1 else body[stop_1].f.pars()

    else:
        ln, col, _, _ = self._loc_maybe_key(start, True, body, body2)
        _, _, end_ln, end_col = body2[start].f.pars()
        loc_first = fstloc(ln, col, end_ln, end_col)

        if start == stop_1:
            loc_last = loc_first

        else:
            ln, col, _, _ = self._loc_maybe_key(stop_1, True, body, body2)
            _, _, end_ln, end_col = body2[stop_1].f.pars()
            loc_last = fstloc(ln, col, end_ln, end_col)

    return loc_first, loc_last


def _locs_and_bounds_get(
    self: fst.FST, start: int, stop: int, body: list[AST], body2: list[AST], off: int, loc: fstloc | None = None
) -> tuple[fstloc, fstloc, int, int, int, int]:
    """Get the location of the first and last elemnts (assumed present) and the bounding location of a one or
    two-element sequence. The start bounding location must be past the ante-first element if present, otherwise start
    of self past any delimiters. The end bounding location must be end of self before any delimiters.

    **Parameters:**
    - `loc`: Override to standard location.

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
    is_special = ast.__class__ is _decorator_list

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
    ast_cls = ast.__class__
    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if not (is_special := (ast_cls is _comprehensions)):
        bound_end_col -= 1

    if start:
        _, _, bound_ln, bound_col = ast.generators[start - 1].f.loc
    elif ast_cls is DictComp:
        _, _, bound_ln, bound_col = ast.value.f.pars()
    elif not is_special:  # ListComp, SetComp, GeneratorExp
        _, _, bound_ln, bound_col = ast.elt.f.pars()

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _bounds_comprehension_ifs(self: fst.FST, start: int = 0) -> tuple[int, int, int, int]:
    ast = self.a
    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if is_comprehension := (ast.__class__ is comprehension):  # therefore not _comprehension_ifs
        if next := self.next():
            if next.ln > bound_end_ln:  # so that multiline ifs are handled correctly, yeah, really pedantic
                bound_end_ln += 1
                bound_end_col = 0

        elif (parent := self.parent) and parent.a.__class__ is not _comprehensions:  # we don't extend to end of `ListComp` (or one of the others) but we do set end boound to start of next line if past our end line so that multiline stuff procs correctly
            if parent.end_ln > bound_end_ln:
                bound_end_ln += 1
                bound_end_col = 0

    if start:
        _, _, bound_ln, bound_col = self._loc_comprehension_if(start - 1)
    elif is_comprehension:
        _, _, bound_ln, bound_col = ast.iter.f.pars()

    return bound_ln, bound_col, bound_end_ln, bound_end_col


def _normalize_solo_call_arg_genexp(self: fst.FST) -> object:
    """If there is a solo `Call.args` `GeneratorExp` which shares its parentheses with the `Call` then parenthesize it
    so that it has its own pars for editing.

    **Returns:**
    - `state`: Restore data to put it back into its original state via `_restore_solo_call_arg_genexp()` (if needed).
    """

    if not (
        (args := self.a.args)
        and (arg0 := args[0].f)._is_solo_call_arg_genexp()
        and arg0.pars(shared=False).n == -1
    ):  # if not single call argument GeneratorExp that shares parentheses with Call then done
        return None

    arg0._parenthesize_grouping()

    return True


def _restore_solo_call_arg_genexp(self: fst.FST, state: object) -> None:
    """Possibly restore the original source of a solo `Call.args` `GeneratorExp` which shared its parentheses with the
    `Call` and was normalized for the edit operation but was not removed so can be put back into its original state.

    **WARNING!** This should only be called if it is known that no modification was made to the args. But it does not
    have to be checked by the caller if it is a solo_call_arg_genexp, just pass the state and if a restore is needed
    then it will be done, if not the noop.
    """

    if state is None:
        return

    arg0 = self.a.args[0]
    ln, col, end_ln, end_col = arg0.f.loc

    self._put_src(None, end_ln, end_col - 1, end_ln, end_col, True)
    self._put_src(None, ln, col, ln, col + 1, True)

    arg0.col_offset -= 1  # don't need to _touch() after this because it was done in the _put_src() above
    arg0.end_col_offset += 1


def _move_arglikes_into_one_field(self: fst.FST, arglikes: list[AST]) -> tuple[str, list[AST], list[AST]]:
    """Put merged orderded `arglikes` of `Call.args+keywords` or `ClassDef.bases+keywords` into the `args` or `bases`
    field and set the `keywords` to empty in order to be able to operate on them easier. Specifically the `args` or
    `bases` and not `keywords` because those have special processing when looking for parentheses to handle single
    `expr` arguments. If a single `expr` arg was in `keywords` then `pars()` would give the wrong location possibly
    including the `Call.args` or `ClassDef.bases` enclosing pars.

    **Parameters:**
    - `arglikes`: The already merged arglikes to set. Because you will probably need them before calling this function
        anyway, get from `_cached_arglikes()`.

    **Returns:**
    - `(field, old_args_or_bases, old_keywords)`: The field name (without underscore) and the old `args/bases` list and
        old `keywords` list.
    """

    ast = self.a
    field = 'args' if ast.__class__ is Call else 'bases'
    exprs = getattr(ast, field)

    if not (keywords := ast.keywords):
        return field, exprs, keywords

    ast.keywords = []
    # arglikes = merge_arglikes(exprs, keywords)

    setattr(ast, field, arglikes)

    for i, a in enumerate(arglikes):
        a.f.pfield = astfield(field, i)

    return field, exprs, keywords


def _split_arglikes_into_two_fields(self: fst.FST, arglikes: list[AST], field: str) -> None:
    """Split merged ordered `arglikes` of `Call.args+keywords` or `ClassDef.bases+keywords` into two field, the `expr`
    field of `args` or `bases` and the `keyword` field of `keywords`. The `arglikes` are ordered so all that needs to be
    done is send the `exprs` to field 1 and the `keywords` to field 2."""

    ast = self.a
    ast.keywords = keywords = []
    exprs = []

    setattr(ast, field, exprs)

    for a in arglikes:  # separate single arglikes with hole cut out back into `args/bases` and `keywords`
        if a.__class__ is keyword:
            a.f.pfield = astfield('keywords', len(keywords))

            keywords.append(a)

        else:
            a.f.pfield = astfield(field, len(exprs))

            exprs.append(a)


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


def _make_arguments_allargs_w_markers(
    self: fst.FST,
    tag: object = None,
    start: int = -1,
    stop: int = -1,
    exp_left_into_slash: bool = False,
    exp_right_into_star: bool = False,
) -> tuple[list[AST], int | None, int | None, int, int]:
    """Make a list of all arguments with standin `/` and `*` marker nodes from an `arguments` for slicing operation
    use.

    We use the `Pass` node as marker for the standins as it doesn't have any children and doesn't normally appear
    outside of statement blocks. The markers are inserted into the actual `arguments` node as if they were `arg` nodes
    at those locations for easier processing. The `/` marker node may also get an empty `defaults` node inserted if
    would be needed for correct sequence of the `arguments` as a whole. The `kw_defaults` node for `kwonlyargs` is just
    inserted as a `None`.

    **Returns:**
    - `(allargs, idx_slash, idx_star, new_start, new_stop)`:
        - `allargs`: List of `AST` nodes which will be the original `arg` nodes from the `arguments` in order
            intersperced with optional `Name` nodes to indicate `/` or `*` markers.
        - `idx_slash`: Index of `/` marker in the list if any, `None` if not present.
        - `idx_star`: Index of `*` marker in the list if any, `None` if not present. This is only the empty star, a
            `vararg` is not considered this and in fact will cause this to be `None`.
        - `new_start`, `new_stop`: `start` and `stop` indices passed in offset according to whatever markers were
            inserted and expanded to include those markers if wound up alongside them.
        - `exp_left_into_slash`: Whether to expand start index to the left into a `/` marker or not.
        - `exp_right_into_star`: Whether to expand stop index to the right into a `*` marker or not.
    """

    lines = self.root._lines
    ast = self.a
    posonlyargs = ast.posonlyargs
    args = ast.args
    vararg = ast.vararg
    kwonlyargs = ast.kwonlyargs
    kwarg = ast.kwarg
    allargs = []
    idx_slash = None
    idx_star = None

    self_ln, self_col, self_end_ln, self_end_col = self.loc

    if posonlyargs:  # need to add '/' node
        allargs.extend(posonlyargs)

        _, _, ln, col = posonlyargs[-1].f._loc_argument(True)
        ln, col, src = next_frag(lines, ln, col, self_end_ln, self_end_col)  # must be there

        assert src.startswith(',')

        if src == ',':
            ln, col, src = next_frag(lines, ln, col + 1, self_end_ln, self_end_col)  # must be there
        else:
            col += 1
            src = src[1:]

        assert src.startswith('/')

        idx_slash = len(allargs)
        lineno = ln + 1
        col_offset = lines[ln].c2b(col)
        end_col_offset = col_offset + 1
        a = Pass(lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=end_col_offset)
        a._is_star = False
        a._tag = tag
        defaults = ast.defaults

        fst.FST(a, self, astfield('posonlyargs', idx_slash))  # throwaway standin for '/'

        posonlyargs.append(a)
        allargs.append(a)

        if (idx := len(defaults) - len(args)) > 0:  # if defaults extend into posonlyargs then need to insert an empty one of those for correctness
            a = Pass(lineno=lineno, col_offset=end_col_offset, end_lineno=lineno, end_col_offset=end_col_offset)

            fst.FST(a, self, astfield('defaults', idx))  # throwaway standin for '/' default value

            defaults.insert(idx, a)

            for i in range(idx + 1, len(defaults)):  # reset all pfields for inserted default element
                defaults[i].f.pfield = astfield('defaults', i)

    allargs.extend(args)

    if vararg:
        allargs.append(vararg)

    if kwonlyargs:
        if not vararg:  # need to add '*' node
            if not allargs:
                ln, col, src = next_frag(lines, self_ln, self_col, self_end_ln, self_end_col)  # must be there

            else:
                _, _, ln, col = a.f.loc if (a := allargs[-1]).__class__ is Pass else a.f._loc_argument(True)
                ln, col, src = next_frag(lines, ln, col, self_end_ln, self_end_col)  # must be there

                assert src.startswith(',')

                if src == ',':
                    ln, col, src = next_frag(lines, ln, col + 1, self_end_ln, self_end_col)  # must be there
                else:
                    col += 1
                    src = src[1:]

            assert src.startswith('*')

            idx_star = len(allargs)
            lineno = ln + 1
            col_offset = lines[ln].c2b(col)
            a = Pass(lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset + 1)
            a._is_star = True
            a._tag = tag
            kw_defaults = ast.kw_defaults

            fst.FST(a, self, astfield('kwonlyargs', 0))  # throwaway standin for '*'

            kw_defaults.insert(0, None)
            kwonlyargs.insert(0, a)

            for i in range(1, len(kwonlyargs)):
                kwonlyargs[i].f.pfield = astfield('kwonlyargs', i)

                if kw_defaults[i]:
                    kw_defaults[i].f.pfield = astfield('kw_defaults', i)

        allargs.extend(kwonlyargs)

    if kwarg:
        allargs.append(kwarg)

    # offset start and stop for inserted markers

    if idx_slash is not None:  # if `/` exists in self and start or stop beyond it then increment them to reflect actual idx after the `/` standin node
        if start >= idx_slash:
            start += 1
            stop += 1

        elif stop > idx_slash:
            stop += 1

    if idx_star is not None:  # if `*` exists in self and start or stop beyond it then increment them to reflect actual idx after the `*` standin node
        if start >= idx_star:
            start += 1
            stop += 1

        elif stop > idx_star:
            stop += 1

    # if start right after marker(s) or end right before then expand endpoints to include them in [start:stop]

    if idx_slash is not None:  # if put ends right before `/` then we remove it no matter what, put is either posonlyargs and has one of its own or is invalid anyway
        if stop == idx_slash:
            stop += 1

    if idx_star is not None:
        if start == idx_star + 1:  # if put starts right after `*` then we remove it no matter what, put either has another one or vararg or kwarg or is invalid
            start -= 1

        if exp_right_into_star and stop == idx_star and (vararg or kwonlyargs or kwarg):  # if put starts right before `*` and put has kwonlyargs or vararg (or kwarg, but that will be an error anyway, we let it eat the star just in case)
            stop += 1

    if exp_left_into_slash and idx_slash is not None:
        if start == idx_slash + 1 and posonlyargs:  # if put ends right after `/` and put has posonlyargs then remove the `/`
            start -= 1

    return allargs, idx_slash, idx_star, start, stop


def _remove_arguments_allargs_markers(self: fst.FST, idx_slash: int | None = -1, idx_star: int | None = 0) -> None:
    """Remove `/` and `*` markers from `arguments` `posonlyargs` and `kwonlyargs`, along with any needed default nodes
    that were added for them."""

    ast = self.a

    if idx_star is not None and (kwonlyargs := ast.kwonlyargs) and kwonlyargs[idx_star].__class__ is Pass:  # if '*' marker present then remove
        kw_defaults = ast.kw_defaults

        del kwonlyargs[idx_star]
        del kw_defaults[idx_star]

        for i in range(idx_star, len(kwonlyargs)):
            kwonlyargs[i].f.pfield = astfield('kwonlyargs', i)

            if kw_defaults[i]:
                kw_defaults[i].f.pfield = astfield('kw_defaults', i)

    if idx_slash is not None and (posonlyargs := ast.posonlyargs) and (a := posonlyargs[idx_slash]).__class__ is Pass:  # if '/' marker present then remove
        defaults = ast.defaults

        if g := a.f.next():
            field, idx = g.pfield

            if field == 'defaults':
                del defaults[idx]

                for i in range(idx, len(defaults)):  # reset all pfields for deleted default element
                    defaults[i].f.pfield = astfield('defaults', i)

        del posonlyargs[idx_slash]


def _arguments_as(
    self: fst.FST,
    args_as: Literal['pos', 'arg', 'kw', 'arg_only', 'kw_only', 'pos_maybe', 'arg_maybe', 'kw_maybe'] | None = None,
) -> None:
    """Convert arguments to the requested type. Will raise for conversion which can not be carried out unless the
    conversion is a `'maybe'`, which just converts as much as possible and doesn't raise for anything that can't be
    converted. An `args_as=None` will just return without changing anything."""

    if not args_as:
        return

    ast = self.a
    vararg = ast.vararg
    kwonlyargs = ast.kwonlyargs
    kwarg = ast.kwarg
    is_maybe = args_as.endswith('_maybe')

    # reject impossible conversions

    if vararg:
        if args_as == 'arg':
            if kwonlyargs:
                raise NodeError("cannot have keywords following vararg for args_as='arg'")

        elif not is_maybe:
            raise NodeError(f'cannot have vararg for args_as={args_as!r}')

    if kwarg and not (is_maybe or args_as == 'kw'):
        raise NodeError(f'cannot have kwarg for args_as={args_as!r}')

    # figure out which changes and marker deletions need to be made, exit early if no changes needed

    posonlyargs = ast.posonlyargs
    args = ast.args
    defaults = ast.defaults
    kw_defaults = ast.kw_defaults
    do_kw = kwonlyargs and not vararg
    del_slash = del_star = False

    if as_arg := args_as.startswith('arg'):
        if posonlyargs:
            del_slash = True
        elif not kwonlyargs:
            return

        del_star = kwonlyargs and not vararg

    elif as_pos := args_as.startswith('pos'):
        if kwonlyargs:
            del_star = not vararg
        elif not args:
            return

        del_slash = bool(posonlyargs)

    else:  # args_as.startswith('kw')
        if posonlyargs:
            del_slash = True
        elif not args:
            return

        if not vararg:
            del_star = bool(kwonlyargs)
        else:  # is_maybe
            do_kw = False
            as_arg = True

    # make sure the defaults are in an allowed state for this operation

    if do_kw:  # need to check that kw_defaults is ok to merge with defaults, going in either direction (if not blocked by vararg)
        if None not in kw_defaults:
            first_kw_default = kw_defaults[0]

        elif as_arg or as_pos:
            for a in (itr := iter(kw_defaults)):
                if a:
                    for b in itr:
                        if not b:
                            first_kw_default = False

                            break

                    else:
                        first_kw_default = a

                    break

            else:
                first_kw_default = None

            if ((not first_kw_default or not kw_defaults[0]) if defaults else first_kw_default is False):
                if not is_maybe:
                    raise NodeError(f'cannot have args with defaults following args without defaults for args_as={args_as!r}')

                do_kw = del_star = False

    # delete slash and / or star if needed

    if del_slash or del_star:
        allargs, idx_slash, idx_star, _, _ = _make_arguments_allargs_w_markers(self)
        locabst = _LocationAbstract_arguments(allargs)

        if del_star:
            end_params = put_slice_sep_begin(self, idx_star, idx_star + 1, locabst, None, None, *self.loc,
                                             {'trivia': (False, 'line')}, ',', 0)
            _remove_arguments_allargs_markers(self, idx_slash=None, idx_star=0)

            del allargs[idx_star]

            put_slice_sep_end(self, end_params)

        if del_slash:
            end_params = put_slice_sep_begin(self, idx_slash, idx_slash + 1, locabst, None, None, *self.loc,
                                             {'trivia': (False, 'line')}, ',', 0)
            _remove_arguments_allargs_markers(self, idx_slash=-1, idx_star=None)

            del allargs[idx_slash]

            put_slice_sep_end(self, end_params)

        if not del_star:  # if were added but not deleted explicitly then we need to remove them
            if idx_star is not None:
                _remove_arguments_allargs_markers(self, idx_slash=None, idx_star=0)

        elif not del_slash and idx_slash is not None:  # only either one or neither of del_star or del_slash can be False, not both
            _remove_arguments_allargs_markers(self, idx_slash=-1, idx_star=None)

    # move nodes between the different argument type lists

    if as_arg:
        if posonlyargs:
            args[0:0] = posonlyargs
            posonlyargs.clear()

            for i in range(0, len(args)):
                args[i].f.pfield = astfield('args', i)

        if do_kw:
            idx = len(args)
            idx_defaults = len(defaults)

            args.extend(kwonlyargs)
            kwonlyargs.clear()

            for i in range(idx, len(args)):
                args[i].f.pfield = astfield('args', i)

            if first_kw_default:
                defaults.extend(kw_defaults[first_kw_default.f.pfield.idx:])

                for i in range(idx_defaults, len(defaults)):
                    defaults[i].f.pfield = astfield('defaults', i)

            kw_defaults.clear()

    elif as_pos:
        if args:
            idx = len(posonlyargs)

            posonlyargs.extend(args)
            args.clear()

            for i in range(idx, len(posonlyargs)):
                posonlyargs[i].f.pfield = astfield('posonlyargs', i)

        if do_kw:
            idx = len(posonlyargs)
            idx_defaults = len(defaults)

            posonlyargs.extend(kwonlyargs)
            kwonlyargs.clear()

            for i in range(idx, len(posonlyargs)):
                posonlyargs[i].f.pfield = astfield('posonlyargs', i)

            if first_kw_default:
                defaults.extend(kw_defaults[first_kw_default.f.pfield.idx:])

                for i in range(idx_defaults, len(defaults)):
                    defaults[i].f.pfield = astfield('defaults', i)

            kw_defaults.clear()

    else:  # as_kw
        posonlyargs.extend(args)

        kwonlyargs[0:0] = posonlyargs
        kw_defaults[0:0] = [None] * (len(posonlyargs) - len(defaults)) + defaults

        posonlyargs.clear()
        args.clear()
        defaults.clear()

        for i in range(0, len(kwonlyargs)):
            kwonlyargs[i].f.pfield = astfield('kwonlyargs', i)

            if a := kw_defaults[i]:
                a.f.pfield = astfield('kw_defaults', i)

    # add any newly needed `/` or `*` and done

    _fix_arguments(self)


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


def _fix_naked_seq_loc(self: fst.FST, body: list[AST], is_first: bool = True, is_last: bool = True) -> None:
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


def _fix_naked_expr(self: fst.FST, is_del: bool, is_first: bool, options: Mapping[str, Any]) -> None:
    """Parenthesize if needed and allowed. If is first child of an `Expr` statement then may need to dedent line
    continuation to `Expr` indentation if that is the first line left, which may not start exactly at proper indentation
    level."""

    lines = self.root._lines

    if not self.is_root or (not is_del and fst.FST.get_option('pars', options)):  # if at root then this is optional and not done for a delete or disabled via 'pars=False' option otherwise
        if not self._is_enclosed_or_line() and not self._is_enclosed_in_parents():  # we may need to add pars to fix parsable
            self._parenthesize_grouping(False)

    if is_first:  # VERY SPECIAL CASE where we may have left a line continuation not exactly at proper indentation after delete at start of Expr which is our statement parent
        if (parent := self.parent_stmtlike()) and parent.a.__class__ is Expr:
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


def _fix_BoolOp(
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

    _fix_naked_expr(self, is_del, is_first, options)

    if body:
        _fix_naked_seq_loc(self, body, is_first, is_last)  # if everything erased then nothing to adjust to and we just leave previous location

        if not (is_first or (is_del and is_last)):  # interior possibly joined alnum due to add or delete
            ln, col, _, _ = body[start].f.loc

            self._fix_joined_alnums(ln, col)

    ln, col, end_ln, end_col = self.loc

    self._fix_joined_alnums(ln, col, end_ln, end_col)  # fix stuff like 'a and(b)if 1 else 0' -> 'aif 1 else 0' and '2 if 1 else(a)and b' -> '2 if 1 elseb'

    if norm and len(body) == 1:  # if only one element remains and normalizing then replace the BoolOp AST in self with the single `values` AST which remains
        self._set_ast(body.pop(), True)


def _fix_Compare(
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

    _fix_naked_expr(self, is_del, is_first, options)

    if body:
        _fix_naked_seq_loc(self, body, is_first, is_last)  # if everything erased then nothing to adjust to and we just leave previous location

        if not (is_first or (is_del and is_last)):  # interior possibly joined alnum due to add or delete on left
            ln, col, _, _ = body[start].f.loc

            self._fix_joined_alnums(ln, col)

        if is_del and not is_first:  # on right of start of delete
            _, _, end_ln, end_col = body[start - 1].f.loc

            self._fix_joined_alnums(end_ln, end_col)

    ln, col, end_ln, end_col = self.loc

    self._fix_joined_alnums(ln, col, end_ln, end_col)  # fix stuff like 'a and(b)if 1 else 0' -> 'aif 1 else 0' and '2 if 1 else(a)and b' -> '2 if 1 elseb'

    if len(body) == 1 and norm:  # if only one element remains and normalizing then replace the Compare AST in self with the single `comparators` AST which remains
        self._set_ast(body.pop(), True)  # this will unmake the leftmost operator fine, placeholder or op_side left or rotated right as well as `left` placeholder
    else:
        _move_Compare_first_comparator_into_left(self)


def _fix_Assign_target0(self: fst.FST) -> None:
    """If `Assign` has `target`s and first target does not start at same location as `self` then delete everything in
    between so that it starts at `self`."""

    assert self.a.__class__ is Assign

    if targets := self.a.targets:
        t0_ln, t0_col, _, _ = targets[0].f.pars()
        self_ln, self_col, _, _ = self.loc

        if t0_col != self_col or t0_ln != self_ln:
            self._put_src(None, self_ln, self_col, t0_ln, t0_col, False)


def _fix_decorator_list_trailing_newline(self: fst.FST, old_last_line: str) -> bool:
    """After insert new last element or delete current last element we need to see if there is a new trailing newline
    that wasn't there before, and if so then remove it.

    **Returns:**
    - `bool`: `True` if self is `_decorator_list` SPECIAL SLICE, otherwise `False`. NOT whether a fix was applied or
        not.
    """

    ast = self.a

    if ast.__class__ is not _decorator_list:
        return False

    lines = self.root._lines

    if not (l := lines[-1]) and l is not old_last_line and len(lines) > 1:  # VERY HACKY check to see if last newline is original, is a bistr so will not be interned empty string, old_last_line must be EXACTLY previous last line and not a copy
        del lines[-1]

        ast.end_lineno -= 1
        ast.end_col_offset = lines[-1].lenbytes

        self._touch()

    return True


def _fix_decorator_list_del(
        self: fst.FST, start: int, bound_ln: int, old_first_line: str, old_last_line: str
) -> None:
    """Delete from decorator list may need fixing if:
    - Deleted first decorator and an empty line before the start of the decorators was deleted in a `FunctionDef`,
        `AsyncFunctionDef` or `ClassDef`.
    - Deleted last decorator leaving a trailing newline in a `_decorator_list`.
    """

    if _fix_decorator_list_trailing_newline(self, old_last_line):
        pass  # noop

    elif not start and not old_first_line:  # if del first element and preceding was empty line ...
        root = self.root
        lines = root._lines

        if lines[bound_ln]:  # and that empty line was deleted (because of trivia) then we need to put it back
            lines.insert(bound_ln, bistr(''))

            root._offset(bound_ln, 0, 1, 0)


def _fix_arguments(self: fst.FST) -> None:
    """Fix `arguments` markers after an operation. Currently just adds missing markers because removals are handled in
    all current callers of this function."""

    lines = self.root._lines
    ast = self.a
    posonlyargs = ast.posonlyargs
    args = ast.args
    vararg = ast.vararg
    kwonlyargs = ast.kwonlyargs
    kwarg = ast.kwarg

    if not (posonlyargs or args or vararg or kwonlyargs or kwarg):  # if completely empty then just delete everything and we are done
        ln, col, end_ln, end_col = self.loc

        self._put_src(None, ln, col, end_ln, end_col, True)

        return

    self_ln, self_col, self_end_ln, self_end_col = self.loc

    # posonlyargs '/'

    if not posonlyargs:  # remove leading '/' if exists, helps that we know that there is some node following it (otherwise would be empty)
        # if (frag := next_frag(lines, self_ln, self_col, self_end_ln, self_end_col)) and frag.src.startswith('/'):
        #     ln, col, _ = frag
        #     end_ln, end_col, src = next_frag(lines, ln, col + 1, self_end_ln, self_end_col)  # must be there
        #     end_col += 1

        #     if src == ',':
        #         end_ln, end_col, src = next_frag(lines, end_ln, end_col, self_end_ln, self_end_col)  # must be there
        #     else:  # next element right after comma without space
        #         assert src.startswith(',')

        #     self._put_src(None, ln, col, end_ln, end_col, True)

        #     self_ln, self_col, self_end_ln, self_end_col = self.loc  # for the new end location
        assert not (
            (frag := next_frag(lines, self_ln, self_col, self_end_ln, self_end_col)) and frag.src.startswith('/'))  # the above should not be needed anymore because there should never be a starting '/' without posonlyargs after a delete

        aa_ln = self_ln  # aa = "after args", we may need this position for '*' processing
        aa_col = self_col

    else:  # there are posonlyargs, make sure there is a '/'
        f = posonlyargs[-1].f
        ln, col, aa_ln, aa_col = f.loc  # args can't has pars

        if (g := f.next()) and g.pfield.name == 'defaults':
            _, _, aa_ln, aa_col = g.pars()  # defaults can has pars
        else:
            g = f

        if frag := next_frag(lines, aa_ln, aa_col, self_end_ln, self_end_col):  # something after?
            aa_ln, aa_col, src = frag
            aa_col += 1

            assert src.startswith(',')  # has to be this

            if frag := next_frag(lines, aa_ln, aa_col, self_end_ln, self_end_col):  # something after?
                next_ln, next_col, src = frag

                if src.startswith('/'):
                    aa_ln = next_ln
                    aa_col = next_col + 1

                else:
                    if next_ln == aa_ln or ((l := lines[ln][:col]) and not l.isspace()):  # next element on same line as comma? or we don't start line?
                        self._put_src(' /,', aa_ln, aa_col, aa_ln, aa_col, True)

                        aa_col += 3

                    else:
                        self._put_src(f'{l}/,\n', (aa_ln := aa_ln + 1), 0, aa_ln, 0, True)

                        aa_ln += 1
                        aa_col = 0

            elif self_end_ln == aa_ln or ((l := lines[ln][:col]) and not l.isspace()):
                self._put_src(' /,', aa_ln, aa_col, aa_ln, aa_col, True)

                aa_col += 3

            else:
                self._put_src(f'{l}/,\n', (aa_ln := aa_ln + 1), 0, aa_ln, 0, True)

                aa_ln += 1
                aa_col = 0

        elif self_end_ln == aa_ln or ((l := lines[ln][:col]) and not l.isspace()):  # nothing follow, not comma or anything or we don't start line
            self._put_src(', /', aa_ln, aa_col, aa_ln, aa_col, True,
                          exclude=g, offset_excluded=False)  # we may be exactly at end of previous posonly node, make sure we don't extend its size

            aa_col += 3

        else:
            self._put_src(f',\n{l}/', aa_ln, aa_col, aa_ln, aa_col, True, exclude=g, offset_excluded=False)

            aa_ln += 2
            aa_col = 0

        self_ln, self_col, self_end_ln, self_end_col = self.loc

    # kwonlyargs '*'

    if not vararg:  # if vararg exists then we don't have to do anything about a standalone '*', otherwise need to check
        if args:
            f = args[-1].f

            if (g := f.next()) and g.pfield.name == 'defaults':
                _, _, aa_ln, aa_col = g.pars()  # defaults can has pars
            else:
                _, _, aa_ln, aa_col = f.loc  # args can't has pars

        if frag := next_frag(lines, aa_ln, aa_col, self_end_ln, self_end_col):  # find element where the '*' would be, if any
            ln, col, src = frag

            if src.startswith(','):
                aa_ln = ln
                aa_col = col + 1

                if src == ',':
                    if frag := next_frag(lines, ln, col + 1, self_end_ln, self_end_col):
                        ln, col, src = frag
                else:
                    src = src[1:]
                    col += 1

        if not kwonlyargs:  # remove '*' if exists and not needed
            # if frag and not src.startswith('**'):  # this means there is a standalone '*'
            #     if not (frag := next_frag(lines, ln, col + 1, self_end_ln, self_end_col)):
            #         end_ln = ln
            #         end_col = col + 1

            #     else:
            #         next_ln, next_col, src = frag

            #         if not src.startswith(','):
            #             end_ln = ln
            #             end_col = col + 1
            #         else:
            #             end_ln = next_ln
            #             end_col = next_col + 1

            #         if src == ',':
            #             if frag := next_frag(lines, next_ln, next_col + 1, self_end_ln, self_end_col):
            #                 next_ln, next_col, src = frag
            #         else:
            #             src = src[1:]
            #             next_col += 1

            #     if frag:  # there is a '**kwarg', just delete up to it
            #         self._put_src(None, ln, col, next_ln, next_col, False)
            #     elif aa_ln == ln:  # previous element ends on same line so just delete from its end to '*' end
            #         self._put_src(None, aa_ln, aa_col, end_ln, end_col, True)
            #     elif end_ln < self_end_ln:  # '*' does not end on last line and starts its own, delete whole line
            #         self._put_src(None, ln, 0, end_ln + 1, 0, True)

            #     else:  # ends on last line, delete from end of '*' (and comma) to start of previous line whitespace (possibly with line continuation)
            #         ln -= 1
            #         m = re_line_end_ws_cont_or_comment.search(lines[ln])
            #         col = m.end() if (g := m.group(1)) and g.startswith('#') else m.start()  # if comment then just del to end of that, otherwise to start of whitespace

            #         self._put_src(None, ln, col, end_ln, end_col, True)
            assert not frag or src.startswith('**')  # the above should not happen anymore as a standalone '*' should not be left on delete if all kwonlyargs were removed

        else:  # there are kwonlyargs, make sure there is a '*'
            if not src.startswith('*'):  # we know there is a frag and this exists because there are kwonlyargs, if not star then is first keyword
                _, _, end_ln, end_col = dflt.f.pars() if (dflt := ast.kw_defaults[0]) else kwonlyargs[0].f.loc

                if (frag := next_frag(lines, end_ln, end_col, self_end_ln, self_end_col)) and frag.src.startswith(','):  # after maybe comma
                    end_ln, end_col, _ = frag
                    end_col += 1

                if (ln > self_ln
                    and (m := re_empty_space.match(lines[ln], 0, col))
                    and not next_frag(lines, end_ln, end_col, end_ln,
                                      0x7fffffffffffffff if end_ln < self_end_ln else self_end_col)  # because could be '**\n'
                ):  # if first keyword starts own line and does not share lines with next node then we put '*' on own line too
                    self._put_src(f'*,\n{m.group()}', ln, col, ln, col, False)
                else:
                    self._put_src('*, ', ln, col, ln, col, False)


def _fix_MatchSequence(self: fst.FST, delims: Literal['', '[]', '()'] | None = None) -> str:
    assert self.a.__class__ is MatchSequence

    if delims is None:
        delims = self.is_delimited_matchseq()

    body = self.a.patterns

    if len(body) == 1 and not delims.startswith('['):  #delims.startswith('('):  #
        self._maybe_ins_sep((f := body[0].f).end_ln, f.end_col, False, self.end_ln, self.end_col - bool(delims))

    if not delims:
        return self._fix_undelimited_seq(body, '[]')

    return delims


def _fix_MatchOr(self: fst.FST, norm: bool | str = False) -> None:
    """Maybe fix a `MatchOr` object that may have the wrong location. Will do nothing to a zero-length `MatchOr` and
    will convert a length 1 `MatchOr` to just its single element if `norm` is true.

    **WARNING!** This is currently expecting to be called from slice operations with specific conditions, not guaranteed
    will work on any-old `MatchOr`.
    """

    assert self.a.__class__ is MatchOr

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
        self._fix_joined_alnums(*self.loc, lines=lines)


def _fix_stmt_end(
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
    semi_col = min(semi_col, len(self._get_block_indent()))  # try to preserve original space before semicolon, silly, yes

    self._put_src(None, bound_ln, bound_col, semi_ln, semi_col, False)


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
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    raise NotImplementedError('this is not implemented yet')


def _get_slice_Tuple_elts(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
        return fst.FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['()'], None, from_=self)

    is_delimited = self._is_delimited_seq()
    locs = _locs_and_bounds_get(self, start, stop, body, body, is_delimited)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ctx_cls = ast.ctx.__class__
    ret_ast = Tuple(elts=asts, ctx=Load())

    if ctx_cls is not Load:
        self._set_ctx(Load, asts[:])

    if is_delimited:
        prefix, suffix = '()'
    else:
        prefix = suffix = ''

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', prefix, suffix, ',', 1, 1)

    pars = fst.FST.get_option('pars', options)
    par_if_needed = pars is True if self.is_root else pars is not False

    if not is_delimited:
        fst_._fix_Tuple(False, par_if_needed)  # cutting from unparenthesized tuple defaults to different parenthesization if needed depending if cutting from root or not

    fst_._fix_arglikes(options)  # parenthesize any arglike expressions (could have come from a slice)

    if cut:
        self._fix_Tuple(is_delimited, par_if_needed)  # cutting from already unparenthesized tuple defaults to not parenthesizing it if needed for parsability

    return fst_


def _get_slice_List_elts(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
    ctx_cls = ast.ctx.__class__
    ret_ast = List(elts=asts, ctx=Load())

    if ctx_cls is not Load:
        self._set_ctx(Load, asts[:])

    return get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', '[', ']', ',', 0, 0)


def _get_slice_Set_elts(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
        get_norm = fst.FST._get_opt_eff_set_norm_get(options)

        return (
            new_empty_set_curlies(from_=self) if not get_norm else
            new_empty_set_call(from_=self) if get_norm == 'call' else
            new_empty_set_star(from_=self)  # True, 'star'
        )

    locs = _locs_and_bounds_get(self, start, stop, body, body, 1)
    asts = _cut_or_copy_asts(start, stop, 'elts', cut, body)
    ret_ast = Set(elts=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'elts', '{', '}', ',', 0, 0)

    if cut:
        self._fix_Set(fst.FST._get_opt_eff_set_norm_self(options))

    return fst_


def _get_slice_Dict__all(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
        return fst.FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['()'], None, from_=self)

    if cut and len_slice == len_body and fst.FST._get_opt_eff_norm_self(options):
        raise ValueError("cannot cut all Delete.targets without norm_self=False")

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_Delete_targets(self, start, loc_first)

    asts = _cut_or_copy_asts(start, stop, 'targets', cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    self._set_ctx(Load, asts[:])

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'targets', '', '', ',', False, 1)

    fst_._fix_Tuple(False)

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _fix_stmt_end(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                                ast.end_lineno, ast.end_col_offset)

        ln, col, _, _ = self.loc

        self._fix_joined_alnums(ln, col + 3)
        self._maybe_add_line_continuations()

    return fst_


def _get_slice_Assign_targets(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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

    if cut and len_slice == len_body and fst.FST._get_opt_eff_norm_self(options):
        raise ValueError("cannot cut all Assign.targets without norm_self=False")

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_Assign_targets(self, start, loc_first)

    asts = _cut_or_copy_asts(start, stop, 'targets', cut, body)
    ret_ast = _Assign_targets(targets=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, 'targets', '', '', '=', True, True)

    if cut:
        _fix_Assign_target0(self)
        self._maybe_add_line_continuations()

    return fst_


def _get_slice_With_AsyncWith_items(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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

    if cut and len_slice == len_body and fst.FST._get_opt_eff_norm_self(options):
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
        if not self._is_enclosed_or_line(check_pars=False):  # if cut and no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_With_items_pars()  # will just give where pars should go (because maybe something like `async \\\n\\\n   with ...`)

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, False)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        elif not start and len_slice != len_body:  # if not adding pars then need to make sure cut didn't join new first `withitem` with the `with`
            ln, col, _, _ = pars.bound

            self._fix_joined_alnums(ln, col)

    return fst_


def _get_slice_Import_names(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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

    if cut and len_slice == len_body and fst.FST._get_opt_eff_norm_self(options):
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
            _fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                ast.end_lineno, ast.end_col_offset)

        self._maybe_add_line_continuations()

    return fst_


def _get_slice_ImportFrom_names(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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

    if cut and len_slice == len_body and fst.FST._get_opt_eff_norm_self(options):
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
            _fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                ast.end_lineno, ast.end_col_offset)

        if not self._is_enclosed_or_line(check_pars=False):  # if cut and no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ImportFrom_names_pars()

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, True, False, self)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

    return fst_


def _get_slice_Global_Nonlocal_names(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    ast = self.a
    len_body = len(ast.names)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['()'], None, from_=self)


    if cut and len_slice == len_body and fst.FST._get_opt_eff_norm_self(options):
        raise ValueError(f'cannot cut all {ast.__class__.__name__}.names without norm_self=False')

    ln, end_col, bound_end_ln, bound_end_col = self.loc

    lines = self.root._lines
    ret_elts = []
    ret_ast = Tuple(elts=ret_elts, ctx=Load())
    end_col += 5 if ast.__class__ is Global else 7  # will have another +1 added in search

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

    fst_._fix_Tuple(False)  # this is in case of multiline elements to add pars, otherwise location would reparse different

    if cut:
        if start and stop == len_body:  # if cut till end and something left then may need to reset end position of self due to new trailing trivia
            _fix_stmt_end(self, bound_ln + 1, lines[bound_ln].c2b(bound_col), ast.end_lineno, ast.end_col_offset)

        self._maybe_add_line_continuations()

    return fst_


def _get_slice_Boolop_values(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
    norm_get = fst.FST._get_opt_eff_norm_get(options)
    norm_self = fst.FST._get_opt_eff_norm_self(options)

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
    op_cls = ast.op.__class__
    sep = 'and' if op_cls is And else 'or'

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
    ret_ast = BoolOp(op=op_cls(), values=asts)

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
        elif (s := (l := fst_lines[ln])[:col] + l[end_col + len(sep):]) and not s.isspace():  # operator not only thing on line, just remove operator
            fst_._put_src(None, ln, col, ln, col + len(sep), True)
        else:  # operator only thing on the line (incuding comments and line continuations), nuke the whole line (we know there is a next line)
            fst_._put_src(None, ln, 0, ln + 1, 0, True)

    elif op_side_left is False:  # remove right side trailing operator source
        last_fst_ln = len(fst_lines) - 1
        _, _, ln, col = fst_body[-1].f.pars()
        end_ln, end_col, src = next_frag(fst_lines, ln, col, last_fst_ln, 0x7fffffffffffffff)  # must be there, op

        if end_ln == ln:  # if on same line as last element then delete everything from end of element to end of operator
            fst_._put_src(None, ln, col, end_ln, end_col + len(sep), True)
        elif fst_lines[end_ln][end_col + len(sep):].strip():  # operator not only thing on line, just remove operator
            fst_._put_src(None, end_ln, end_col, end_ln, end_col + len(sep), True)
        elif end_ln < last_fst_ln:  # operator only thing on the line (incuding comments and line continuations), nuke the whole line
            fst_._put_src(None, end_ln, 0, end_ln + 1, 0, True)
        else:  # on last line so just nuke to the end of the line
            fst_._put_src(None, end_ln, 0, end_ln, 0x7fffffffffffffff, True)

    # rest of cleanups

    _fix_naked_seq_loc(fst_, fst_body)

    if len(fst_body) == 1 and norm_get:  # if only one element gotten and normalizing then replace the BoolOp AST in fst_ with the single `values` AST which it has
        fst_._set_ast(fst_body.pop(), True)

    if cut:
        _fix_BoolOp(self, start, cut, is_last, options, norm_self)

    return fst_


def _get_slice_Compare__all(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
    norm_get = fst.FST._get_opt_eff_norm_get(options)
    norm_self = fst.FST._get_opt_eff_norm_self(options)

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
        elif (
            ((s := fst_lines[op_ln][:op_col]) and not s.isspace())
            or ((s := fst_lines[op_end_ln][op_end_col:]) and not s.isspace())
        ):  # operator not only thing on its line(s), just remove operator
            fst_._put_src(None, op_ln, op_col, op_end_ln, op_end_col, True)
        else:  # operator only thing on its line(s) (incuding comments and line continuations, except for anything inside ('is not', 'not in')), nuke the whole line(s)
            fst_._put_src(None, op_ln, 0, op_end_ln + 1, 0, True)

        op0f._unmake_fst_tree()  # delete left operator AST and replace with placeholder for correct location calculations

        asts_ops[0] = fst.FST(Pass(lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), fst_, astfield('ops', 0)).a

    else:
        if (op0 := asts_ops[0]).__class__ is Pass:  # first operator is placeholder which was not offset in get_slice_nosep() so assign temporary location here
            op0.lineno = op0.end_lineno = 1
            op0.col_offset = op0.end_col_offset = 0

        if op_side_left is False:  # remove right side trailing operator and placeholder comparator
            _, _, last_end_ln, last_end_col = fst_body[-2].f.pars()
            opnf = asts_ops.pop().f
            op_ln, op_col, op_end_ln, op_end_col = opnf.loc

            if op_ln == last_end_ln:  # if op starts on same line as last element ends then delete everything from end of element to end of operator
                fst_._put_src(None, last_end_ln, last_end_col, op_end_ln, op_end_col, True)
            elif fst_lines[op_end_ln][op_end_col:].strip():  # operator not only thing on line, just remove operator
                fst_._put_src(None, op_ln, op_col, op_end_ln, op_end_col, True)
            elif op_end_ln < len(fst_lines) - 1:   # operator only thing on its line(s) (incuding comments and line continuations, except for anything inside ('is not', 'not in')) nuke the whole line(s)
                fst_._put_src(None, op_ln, 0, op_end_ln + 1, 0, True)
            else:  # on last line so just nuke to the end of the line
                fst_._put_src(None, op_ln, 0, op_end_ln, 0x7fffffffffffffff, True)

            opnf._unmake_fst_tree()  # delete right operator AST and comparator placeholder AST
            fst_body.pop().f._unmake_fst_tree()

    # rest of cleanups

    _fix_naked_seq_loc(fst_, fst_body)

    if len(fst_body) == 1 and norm_get:  # if only one element gotten and normalizing then replace the Compare AST in fst_ with the single `comparators` AST which it has, don't need to unmake `left` since it is None at this point
        fst_._set_ast(fst_body.pop(), True)  # this will unmake the leftmost operator fine, placeholder or op_side left or rotated right
    else:
        _move_Compare_first_comparator_into_left(fst_)

    if cut:
        _fix_Compare(self, start, True, is_last, options, norm_self)
    else:
        _move_Compare_first_comparator_into_left(self)

    return fst_


def _get_slice_Call_ClassDef_args_bases(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Call.args` or `ClassDef.bases` slice is just a normal `Tuple`, with possibly expr_arglike elements which are
    invalid in a normal expression tuple."""

    ast = self.a
    body = getattr(ast, field)
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    is_call = ast.__class__ is Call

    if not len_slice:
        return fst.FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['()'], None, from_=self)

    if keywords := ast.keywords:
        kw0_pos = keywords[0].f.loc

        if kw0_pos < body[stop - 1].f.loc:  # don't need to do pars()
            raise NodeError(f'cannot get {ast.__class__.__name__}.{field} slice because it includes keywords'
                            f", try the '_{field}' field")

        self_tail_sep = True if body[-1].f.loc < kw0_pos else None

    else:
        self_tail_sep = None

        if is_call:
            state = _normalize_solo_call_arg_genexp(self)

    loc = self._loc_Call_pars() if is_call else self._loc_ClassDef_bases_pars()
    locs = _locs_and_bounds_get(self, start, stop, body, body, 1, loc)
    asts = _cut_or_copy_asts(start, stop, field, cut, body)
    ret_ast = Tuple(elts=asts, ctx=Load())

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, field, '(', ')', ',', self_tail_sep, len_slice == 1)

    fst_._fix_arglikes(options)  # parenthesize any arglike expressions

    if cut:
        if keywords:
            if start and stop == len_body:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
                self._maybe_ins_sep(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

        elif not (is_call or body):  # everything was cut from a ClassDef and no keywords, remove parentheses
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ClassDef_bases_pars()  # definitely exist

            self._put_src(None, pars_ln, pars_col, pars_end_ln, pars_end_col, False)

    elif is_call and not keywords:  # only needs to be done for Call and if there were no keywords
        _restore_solo_call_arg_genexp(self, state)

    return fst_


def _get_slice_Call_ClassDef_arglikes(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Combined `Call.args+keywords` or `ClassDef.bases+keywords` slice, doesn't have to check ordering as a cut won't
    change it."""

    ast = self.a
    body = self._cached_arglikes()
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(_arglikes(arglikes=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    is_call = ast.__class__ is Call

    if is_call:
        state = _normalize_solo_call_arg_genexp(self)

    field, _, keywords = _move_arglikes_into_one_field(self, body)
    loc = self._loc_Call_pars() if is_call else self._loc_ClassDef_bases_pars()
    locs = _locs_and_bounds_get(self, start, stop, body, body, 1, loc)
    asts = _cut_or_copy_asts(start, stop, field, cut, body)
    ret_ast = _arglikes(arglikes=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, field, '', '', ',', False, False)

    if cut:
        if not (is_call or body):  # everything was cut from a ClassDef, remove parentheses
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ClassDef_bases_pars()  # definitely exist

            self._put_src(None, pars_ln, pars_col, pars_end_ln, pars_end_col, False)

    elif is_call:  # only needs to be done for a Call and only if there are no keywords
        _restore_solo_call_arg_genexp(self, state)

    if keywords:  # only need to unmerge if there were keywords to begin with
        _split_arglikes_into_two_fields(self, body, field)

    return fst_


def _get_slice_Call_ClassDef_keywords(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `Call.keywords` or `ClassDef.keywords` slice is just check to make sure the slice is all keywords then fall
    through to get arglikes."""

    ast = self.a
    body = ast.keywords
    start, stop = fixup_slice_indices(len(body), start, stop)
    exprs_field = 'args' if ast.__class__ is Call else 'bases'
    exprs = getattr(ast, exprs_field)

    if exprs and start != stop and body[start].f.loc < exprs[-1].f.loc:
        raise NodeError(f'cannot get {ast.__class__.__name__}.keywords slice because it includes {exprs_field}'
                        f", try the '_{exprs_field}' field")

    len_exprs = len(exprs)

    return _get_slice_Call_ClassDef_arglikes(self, start + len_exprs, stop + len_exprs, '_' + exprs_field, cut, options)


def _get_slice_decorator_list(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
        _fix_decorator_list_del(self, start, bound_ln, old_first_line, old_last_line)

    return fst_


def _get_slice_generators(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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

    if ast.__class__ is not _comprehensions:
        if cut and len_slice == len_body and fst.FST._get_opt_eff_norm_self(options):
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
    start: int | Literal['end'],
    stop: int | Literal['end'],
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


def _get_slice_arguments(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """The slice of `arguments` is just another `arguments`. We treat all args as part of the same sequence and fix any
    `/` and `*` indicators afterwards."""

    ast = self.a
    len_body = len(self._cached_allargs())
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                       [''], None, from_=self)

    body, _, _, start, stop = _make_arguments_allargs_w_markers(self, None, start, stop)
    len_body = len(body)
    loc_first = body[start].f._loc_argument(True)
    loc_last = loc_first if start == stop - 1 else body[stop - 1].f._loc_argument(True)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if start:
        f = body[start - 1].f

        if (g := f.next()) and g.pfield.name in ('defaults', 'kw_defaults'):
            f = g

        _, _, bound_ln, bound_col = f.pars()

    ret_ast = arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[])

    if not cut:
        for i in range(start, stop):
            a = body[i]
            f = a.f
            a = copy_ast(a)

            if (field := f.pfield.name) in ('kwarg', 'vararg'):
                setattr(ret_ast, field, a)

            else:
                getattr(ret_ast, field).append(a)

                if (f := f.next()) and (dflt_field := f.pfield.name) in ('defaults', 'kw_defaults'):
                    getattr(ret_ast, dflt_field).append(a := copy_ast(f.a))
                elif field == 'kwonlyargs':  # these always have a kw_defaults entry even if it is None
                    ret_ast.kw_defaults.append(None)

        ast_last = a
        new_last = ''

    else:  # if cutting then moving the nodes aroung is a bit tricky
        ast_last = None

        for i in range(stop - 1, start - 1, -1):  # we do in reverse because we will be removing them from their lists along the way
            a = body[i]
            f = a.f
            field, idx = f.pfield

            if field in ('kwarg', 'vararg'):
                setattr(ret_ast, field, a)
                setattr(ast, field, None)

            else:
                getattr(ret_ast, field).insert(0, a)

                if f := f.next():
                    dflt_field, dflt_idx = f.pfield

                    if dflt_field in ('defaults', 'kw_defaults'):
                        getattr(ret_ast, dflt_field).insert(0, a := f.a)

                        del getattr(ast, dflt_field)[dflt_idx]

                    else:
                        f = None

                if not f and field == 'kwonlyargs':
                    ret_ast.kw_defaults.insert(0, None)

                    del ast.kw_defaults[idx]  # can't use dflt_idx because possibly nonexistent, but idx will be same as dflt_idx should be for kw_defaults

                del getattr(ast, field)[idx]

            if ast_last is None:
                ast_last = a

        for field in ('posonlyargs', 'args', 'kwonlyargs', 'kw_defaults', 'defaults'):  # reset pfields to account for any removed nodes
            for i, a in enumerate(getattr(ast, field)):
                if a:  # because of kw_defaults None values
                    a.f.pfield = astfield(field, i)

        if not start and stop == len_body:
            new_last = ''

        else:
            new_last = body[start - 1 if stop == len_body else -1].f  # new last node in 'self' after cut

            if f := new_last.next():  # if there is a next then it is a default and that should be new_last
                new_last = f

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, ast_last,
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, new_last, '', '', ',', 0, 0, False)

    _remove_arguments_allargs_markers(fst_)
    _remove_arguments_allargs_markers(self)
    _fix_arguments(fst_)

    if cut:
        _fix_arguments(self)

        if (parent := self.parent) and parent.a.__class__ is Lambda:  # Lambda may need parenthesization
            ln, _, end_ln, _ = self.loc

            if end_ln != ln and not self._is_enclosed_in_parents():  # if we created multiline args for an unenclosed Lambda then parenthesize it
                parent._parenthesize_grouping()

    _arguments_as(fst_, fst.FST.get_option('args_as', options))

    return fst_


def _get_slice_MatchSequence_patterns(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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

    delims = self.is_delimited_matchseq()
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
        _fix_MatchSequence(fst_, '')

    if cut:
        _fix_MatchSequence(self, delims)

    return fst_


def _get_slice_MatchMapping__all(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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


def _get_slice_MatchClass_patterns(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """A `MatchClass.patterns` slice is just a normal `MatchSequence`."""

    ast = self.a
    body = ast.patterns
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    if not len_slice:
        return fst.FST(MatchSequence(patterns=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
                       ['[]'], None, from_=self)

    if ast.kwd_patterns:
        self_tail_sep = True
    else:
        self_tail_sep = None

    loc = self._loc_MatchClass_pars()
    locs = _locs_and_bounds_get(self, start, stop, body, body, 1, loc)
    asts = _cut_or_copy_asts(start, stop, field, cut, body)
    ret_ast = MatchSequence(patterns=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, field, '[', ']', ',', self_tail_sep, False)

    if cut:
        if self_tail_sep:  # means there are keywords
            if start and stop == len_body:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
                self._maybe_ins_sep(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there

    return fst_


def _get_slice_MatchOr_patterns(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
    norm_get = fst.FST._get_opt_eff_norm_get(options)
    norm_self = fst.FST._get_opt_eff_norm_self(options)

    if not len_slice:
        if norm_get:
            raise ValueError("cannot get empty slice from MatchOr without norm_get=False")

        return fst.FST(MatchOr(patterns=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                       [''], None, from_=self)

    if cut and len_slice == len_body and norm_self:
        raise ValueError("cannot cut all MatchOr.patterns without norm_self=False")

    locs = _locs_and_bounds_get(self, start, stop, body, body, 0)
    asts = _cut_or_copy_asts(start, stop, 'patterns', cut, body)
    ret_ast = MatchOr(patterns=asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1], *locs,
                         options, 'patterns', '', '', '|', False, False)

    _fix_MatchOr(fst_, norm_get)

    if cut:
        _fix_MatchOr(self, norm_self)

    return fst_


def _get_slice_type_params(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    ast = self.a
    ast_cls = ast.__class__
    body = ast.type_params
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(_type_params([], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], None, from_=self)

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_func = (
        fst.FST._loc_TypeAlias_type_params_brackets if ast_cls is TypeAlias else
        fst.FST._loc_ClassDef_type_params_brackets if ast_cls is ClassDef else
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
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Our own general non-AST-compatible slice of some `type[AST]` list field."""

    ast = self.a
    ast_cls = ast.__class__
    static = fst_package.fst_put_slice._SPECIAL_SLICE_STATICS[ast_cls]
    body = getattr(ast, field)
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    if start == stop:
        return fst.FST(ast_cls([], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0), [''], None, from_=self)

    loc_first, loc_last = _locs_first_and_last(self, start, stop, body, body)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()

    asts = _cut_or_copy_asts(start, stop, field, cut, body)
    ret_ast = ast_cls(asts)

    fst_ = get_slice_sep(self, start, stop, len_body, cut, ret_ast, asts[-1],
                         loc_first, loc_last, bound_ln, bound_col, bound_end_ln, bound_end_col,
                         options, field, '', '', static.sep, static.self_tail_sep, static.ret_tail_sep)

    return fst_


def _get_slice_stmtlike__body(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
    field: str,
    cut: bool,
    options: Mapping[str, Any],
) -> fst.FST:
    """Get a slice from a statementlike virtual `_body` field which is just a `body` as if it didn't have a docstring.
    """

    if self.has_docstr:
        start, stop = fixup_slice_indices(len(self.a.body), start, stop, 1)

    return get_slice_stmtlike(self, start, stop, 'body', cut, options)


_GET_SLICE_HANDLERS = {
    (Module, 'body'):                         get_slice_stmtlike,  # stmt*
    (Interactive, 'body'):                    get_slice_stmtlike,  # stmt*
    (FunctionDef, 'body'):                    get_slice_stmtlike,  # stmt*
    (AsyncFunctionDef, 'body'):               get_slice_stmtlike,  # stmt*
    (ClassDef, 'body'):                       get_slice_stmtlike,  # stmt*
    (For, 'body'):                            get_slice_stmtlike,  # stmt*
    (For, 'orelse'):                          get_slice_stmtlike,  # stmt*
    (AsyncFor, 'body'):                       get_slice_stmtlike,  # stmt*
    (AsyncFor, 'orelse'):                     get_slice_stmtlike,  # stmt*
    (While, 'body'):                          get_slice_stmtlike,  # stmt*
    (While, 'orelse'):                        get_slice_stmtlike,  # stmt*
    (If, 'body'):                             get_slice_stmtlike,  # stmt*
    (If, 'orelse'):                           get_slice_stmtlike,  # stmt*
    (With, 'body'):                           get_slice_stmtlike,  # stmt*
    (AsyncWith, 'body'):                      get_slice_stmtlike,  # stmt*
    (Try, 'body'):                            get_slice_stmtlike,  # stmt*
    (Try, 'orelse'):                          get_slice_stmtlike,  # stmt*
    (Try, 'finalbody'):                       get_slice_stmtlike,  # stmt*
    (TryStar, 'body'):                        get_slice_stmtlike,  # stmt*
    (TryStar, 'orelse'):                      get_slice_stmtlike,  # stmt*
    (TryStar, 'finalbody'):                   get_slice_stmtlike,  # stmt*
    (ExceptHandler, 'body'):                  get_slice_stmtlike,  # stmt*
    (match_case, 'body'):                     get_slice_stmtlike,  # stmt*

    (Match, 'cases'):                         get_slice_stmtlike,  # match_case*
    (Try, 'handlers'):                        get_slice_stmtlike,  # excepthandler*
    (TryStar, 'handlers'):                    get_slice_stmtlike,  # excepthandler* ('except*')

    (Module, '_body'):                        _get_slice_stmtlike__body,  # stmt*  - without docstr
    (Interactive, '_body'):                   _get_slice_stmtlike__body,  # stmt*
    (FunctionDef, '_body'):                   _get_slice_stmtlike__body,  # stmt*
    (AsyncFunctionDef, '_body'):              _get_slice_stmtlike__body,  # stmt*
    (ClassDef, '_body'):                      _get_slice_stmtlike__body,  # stmt*
    (For, '_body'):                           _get_slice_stmtlike__body,  # stmt*
    (AsyncFor, '_body'):                      _get_slice_stmtlike__body,  # stmt*
    (While, '_body'):                         _get_slice_stmtlike__body,  # stmt*
    (If, '_body'):                            _get_slice_stmtlike__body,  # stmt*
    (With, '_body'):                          _get_slice_stmtlike__body,  # stmt*
    (AsyncWith, '_body'):                     _get_slice_stmtlike__body,  # stmt*
    (Try, '_body'):                           _get_slice_stmtlike__body,  # stmt*
    (TryStar, '_body'):                       _get_slice_stmtlike__body,  # stmt*
    (ExceptHandler, '_body'):                 _get_slice_stmtlike__body,  # stmt*
    (match_case, '_body'):                    _get_slice_stmtlike__body,  # stmt*

    (Tuple, 'elts'):                          _get_slice_Tuple_elts,  # expr*
    (List, 'elts'):                           _get_slice_List_elts,  # expr*
    (Set, 'elts'):                            _get_slice_Set_elts,  # expr*

    (Dict, '_all'):                           _get_slice_Dict__all,  # key:value*

    (FunctionDef, 'decorator_list'):          _get_slice_decorator_list,  # expr*
    (AsyncFunctionDef, 'decorator_list'):     _get_slice_decorator_list,  # expr*
    (ClassDef, 'decorator_list'):             _get_slice_decorator_list,  # expr*
    (ClassDef, 'bases'):                      _get_slice_Call_ClassDef_args_bases,  # expr*
    (ClassDef, 'keywords'):                   _get_slice_Call_ClassDef_keywords,  # keyword*
    (ClassDef, '_bases'):                     _get_slice_Call_ClassDef_arglikes,  # (expr|keyword)*
    (Delete, 'targets'):                      _get_slice_Delete_targets,  # expr*
    (Assign, 'targets'):                      _get_slice_Assign_targets,  # expr*
    (BoolOp, 'values'):                       _get_slice_Boolop_values,  # expr*
    (Compare, '_all'):                        _get_slice_Compare__all,  # expr*
    (Call, 'args'):                           _get_slice_Call_ClassDef_args_bases,  # expr*
    (Call, 'keywords'):                       _get_slice_Call_ClassDef_keywords,  # keyword*
    (Call, '_args'):                          _get_slice_Call_ClassDef_arglikes,  # (expr|keyword)*
    (comprehension, 'ifs'):                   _get_slice_comprehension_ifs,  # expr*
    (arguments, '_all'):                      _get_slice_arguments,  # posonlyargs=defaults,args=defaults,vararg,kwolyargs=kw_defaults,kwarg

    (ListComp, 'generators'):                 _get_slice_generators,  # comprehension*
    (SetComp, 'generators'):                  _get_slice_generators,  # comprehension*
    (DictComp, 'generators'):                 _get_slice_generators,  # comprehension*
    (GeneratorExp, 'generators'):             _get_slice_generators,  # comprehension*

    (Import, 'names'):                        _get_slice_Import_names,  # alias*
    (ImportFrom, 'names'):                    _get_slice_ImportFrom_names,  # alias*

    (With, 'items'):                          _get_slice_With_AsyncWith_items,  # withitem*
    (AsyncWith, 'items'):                     _get_slice_With_AsyncWith_items,  # withitem*

    (MatchSequence, 'patterns'):              _get_slice_MatchSequence_patterns,  # pattern*
    (MatchMapping, '_all'):                   _get_slice_MatchMapping__all,  # key:pattern*
    (MatchClass, 'patterns'):                 _get_slice_MatchClass_patterns,  # pattern*
    (MatchOr, 'patterns'):                    _get_slice_MatchOr_patterns,  # pattern*

    (FunctionDef, 'type_params'):             _get_slice_type_params,  # type_param*
    (AsyncFunctionDef, 'type_params'):        _get_slice_type_params,  # type_param*
    (ClassDef, 'type_params'):                _get_slice_type_params,  # type_param*
    (TypeAlias, 'type_params'):               _get_slice_type_params,  # type_param*

    (Global, 'names'):                        _get_slice_Global_Nonlocal_names,  # identifier*
    (Nonlocal, 'names'):                      _get_slice_Global_Nonlocal_names,  # identifier*

    (JoinedStr, 'values'):                    _get_slice_NOT_IMPLEMENTED_YET,  # expr*
    (TemplateStr, 'values'):                  _get_slice_NOT_IMPLEMENTED_YET,  # expr*

    (_ExceptHandlers, 'handlers'):            get_slice_stmtlike,  # ExceptHandler*
    (_match_cases, 'cases'):                  get_slice_stmtlike,  # match_case*
    (_Assign_targets, 'targets'):             _get_slice__slice,  # expr*
    (_decorator_list, 'decorator_list'):      _get_slice_decorator_list,  # expr*
    (_arglikes, 'arglikes'):                  _get_slice__slice,  # (expr|keyword)*
    (_comprehensions, 'generators'):          _get_slice_generators,  # comprehensions*
    (_comprehension_ifs, 'ifs'):              _get_slice_comprehension_ifs,  # exprs*
    (_aliases, 'names'):                      _get_slice__slice,  # alias*
    (_withitems, 'items'):                    _get_slice__slice,  # withitem*
    (_type_params, 'type_params'):            _get_slice__slice,  # type_param*
}


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _get_slice(
    self: fst.FST,
    start: int | Literal['end'],
    stop: int | Literal['end'],
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
