"""Functions which calculate the locations of various node elements which don't have stored locations, or entire nodes
themselves for those which don't normally have a location. The only thing all these functions have in common is that
they calculate locations, there is no standard return type or conditions, read the docstrings for use.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import re
from typing import Literal

from . import fst

from .asttypes import (
    ASTS_LEAF_BLOCK,
    ASTS_LEAF_FUNCDEF,
    ASTS_LEAF_DEF,
    ASTS_LEAF_WITH,
    ASTS_LEAF_VAR_SCOPE_DECL,
    ASTS_LEAF_OP,
    ASTS_LEAF_CMPOP_TWO_WORD,
    AST,
    And,
    AsyncFunctionDef,
    AsyncWith,
    BoolOp,
    Call,
    ClassDef,
    Compare,
    GeneratorExp,
    Global,
    ImportFrom,
    Lambda,
    MatchClass,
    MatchMapping,
    Subscript,
    TypeAlias,
    UnaryOp,
    arguments,
    comprehension,
    match_case,
    withitem,
    _comprehension_ifs,
    _decorator_list,
)

from .astutil import re_identifier, OPCLS2STR, last_block_header_child
from .common import fstloc, fstlocn, next_frag, prev_frag, next_find, prev_find, next_delims, prev_delims, next_find_re


_ASTS_LEAF_DEF_OR_DECO_LIST     = ASTS_LEAF_DEF | {_decorator_list}
_ASTS_LEAF_COMPREHENSION_OR_IFS = frozenset([comprehension, _comprehension_ifs])

_re_deco_start         = re.compile(r'[ \t]*@')

_re_keyword_import     = re.compile(r'\bimport\b')  # we end with a '\b' because we need exactly this word and there may be other similar ones between `from` and `import`
_re_keyword_with_start = re.compile(r'\bwith')  # we do not end with '\b' because the search using this may be checking source where the `with` is joined with a following `withitem` and there are no other words between `async` and `with`


def _next_bound_step_own_loc(self: fst.FST) -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object using `step_fwd()`. This is safe to call
    for nodes that live inside nodes without their own locations. Recurse into nodes with non-own locations (even though
    those nodes are not returned) to find nodes with own location. This is only meant for internal use to safely call
    from `.loc` location calculation."""

    if next := self.step_fwd(True, False):
        if next.has_own_loc:
            return next.bloc[:2]

        while (next := next.step_fwd(True)):
            if next.has_own_loc:
                return next.bloc[:2]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound_step_own_loc(self: fst.FST) -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object using `step_back()`. Recurse into nodes with
    non-own locations (even though those nodes are not returned) to find nodes with own location. This is only meant for
    internal use to safely call from `.loc` location calculation."""

    if prev := self.step_back(True, False):
        if prev.has_own_loc:
            return prev.bloc[2:]

        while (prev := prev.step_back(True)):
            if prev.has_own_loc:
                return prev.bloc[2:]

    return 0, 0


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _loc_maybe_key(
    self: fst.FST, idx: int, pars: bool = True, body: list[AST] | None = None, body2: list[AST] | None = None
) -> fstloc:
    """Return location of node which may be a dictionary key even if it is `**` specified by a `None`. Optionally return
    the location of the grouping parentheses if key actually present. Can also be used to get the location
    (parenthesized or not) from any list of `AST`s which is not a `Dict.keys` if an explicit `body` and / or `body2` is
    passed in, e.g. will safely get location of `MatchMapping` keys. Will just return parenthesized or not location from
    any `body` assuming there are no `None`s to force a check from `body2` and a search back from that for a `**`.

    **WARNING:** `idx` must be non-negative.

    **Parameters:**
    - `idx`: Non-negative index of child to get location in `self` container.
    - `pars`: Whether to return location from `.pars()` if is not `**` key or not.
    - `body`: Override for `.keys` in case this is not being used on a `Dict`.
    - `body2`: Override for `.values` in case this is being used on a `MatchMapping`.
    """

    if key := (body or self.a.keys)[idx]:
        return key.f.pars() if pars else key.f.loc

    if body2 is None:
        body2 = self.a.values

    val_ln, val_col, _, _ = body2[idx].f.loc

    if idx:
        _, _, ln, col = body2[idx - 1].f.loc
    else:
        ln, col, _, _ = self.loc

    ln, col = prev_find(self.root._lines, ln, col, val_ln, val_col, '**')  # '**' must be there

    return fstloc(ln, col, ln, col + 2)


def _loc_arguments(self: fst.FST) -> fstloc | None:  # TODO: merge with _loc_arugments_empty()
    """`arguments` location. Empty `arguments` may return a zero-length location. For a `Lambda`, empty `arguments` will
    be the entire location from end of the `lambda` keyword to the `:`.

    **Note:** This function is explicitly safe to use from `FST.loc`.
    """

    assert self.a.__class__ is arguments

    if not (parent := self.parent):  # arguments at root have location of whole source, both because they are used as a slice and because root should always have a location
        return fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))

    lines = self.root._lines
    last_child = self.last_child()
    ln, col, end_ln, end_col = parent.loc
    parenta = parent.a
    parent_cls = parenta.__class__

    if parent_cls is Lambda:
        col += 6

        if last_child:
            _, _, last_ln, last_col = last_child.loc

            if lines[ln][col : col + 1].isspace():  # we only increment if there are children because otherwise if there is whitespace then probably it is being deleted
                col += 1

        else:
            last_ln = ln
            last_col = col

        end_ln, end_col = next_find(lines, last_ln, last_col, end_ln, end_col, ':')  # must be there

    else:
        assert parent_cls in ASTS_LEAF_FUNCDEF

        if type_params := getattr(parenta, 'type_params', None):  # doesn't exist in py < 3.12
            _, _, ln, col = type_params[-1].f.loc

        ln, col = next_find(lines, ln, col, end_ln, end_col, '(')  # must be there
        col += 1

        if last_child:
            _, _, last_ln, last_col = last_child.loc
        else:
            last_ln = ln
            last_col = col

        end_ln, end_col = self._next_bound()
        end_ln, end_col = prev_find(lines, last_ln, last_col, end_ln, end_col, ')')

    return fstloc(ln, col, end_ln, end_col)


def _loc_comprehension(self: fst.FST) -> fstloc:
    """`comprehension` location from children.

    **Note:** This function is explicitly safe to use from `FST.loc`.
    """

    assert self.a.__class__ is comprehension

    ast = self.a
    first = ast.target.f
    last = ifs[-1].f if (ifs := ast.ifs) else ast.iter.f  # self.last_child(), could be .iter or last .ifs
    lines = self.root._lines

    if ((prev := self.prev())
        and (
            prev.a.__class__ is not comprehension
            or (prev := prev.last_child())
    )):
        _, _, ln, col = prev.loc  # definitely has own location
    else:
        ln = col = 0

    start_ln, start_col = prev_find(lines, ln, col, first.ln, first.col, 'for')  # must be there

    if ast.is_async:
        start_ln, start_col = prev_find(lines, ln, col, start_ln, start_col, 'async')  # must be there

    rpars = next_delims(lines, last.end_ln, last.end_col, *_next_bound_step_own_loc(self))

    if (lrpars := len(rpars)) == 1:  # no pars, just use end of last
        end_ln, end_col = rpars[0]

    else:
        is_genexp_last = ((parent := self.parent)
                          and parent.a.__class__ is GeneratorExp
                          and self.pfield.idx == len(parent.a.generators) - 1)  # correct for parenthesized GeneratorExp

        if is_genexp_last and lrpars == 2:  # can't be pars on left since only par on right was close of GeneratorExp
            end_ln, end_col = rpars[0]
        else:

            end_ln, end_col = rpars[len(prev_delims(lines, *last._prev_bound(), last.ln, last.col)) - 1]  # get rpar according to how many pars on left

    return fstloc(start_ln, start_col, end_ln, end_col)


def _loc_withitem(self: fst.FST) -> fstloc:
    """`withitem` location from children.

    **Note:** This function is explicitly safe to use from `FST.loc`.
    """

    assert self.a.__class__ is withitem

    ast = self.a
    ce = ast.context_expr.f
    lines = self.root._lines

    ce_ln, ce_col, ce_end_ln, ce_end_col = ce_loc = ce.loc

    if not (ov := ast.optional_vars):
        rpars = next_delims(lines, ce_end_ln, ce_end_col, *_next_bound_step_own_loc(self))

        if (lrpars := len(rpars)) == 1:
            return ce_loc

        lpars = prev_delims(lines, *_prev_bound_step_own_loc(self), ce_ln, ce_col)
        npars = min(lrpars, len(lpars)) - 1

        return fstloc(*lpars[npars], *rpars[npars])

    ov_ln, ov_col, ov_end_ln, ov_end_col = ov.f.loc

    rpars = next_delims(lines, ce_end_ln, ce_end_col, ov_ln, ov_col)

    if (lrpars := len(rpars)) == 1:
        ln = ce_ln
        col = ce_col

    else:
        lpars = prev_delims(lines, *_prev_bound_step_own_loc(self), ce_ln, ce_col)
        ln, col = lpars[min(lrpars, len(lpars)) - 1]

    lpars = prev_delims(lines, ce_end_ln, ce_end_col, ov_ln, ov_col)

    if (llpars := len(lpars)) == 1:
        return fstloc(ln, col, ov_end_ln, ov_end_col)

    rpars = next_delims(lines, ov_end_ln, ov_end_col, *_next_bound_step_own_loc(self))
    end_ln, end_col = rpars[min(llpars, len(rpars)) - 1]

    return fstloc(ln, col, end_ln, end_col)


def _loc_match_case(self: fst.FST) -> fstloc:
    """`match_case` location from children.

    **Note:** This function is explicitly safe to use from `FST.loc`.
    """

    assert self.a.__class__ is match_case

    ast = self.a
    lines = self.root._lines
    ln, col, _, _ = ast.pattern.f.loc
    _, _, end_ln, end_col = self.last_child().loc  # .loc instead of .bloc because we don't want any trailing comment from last child for the actual match_case.loc

    ln, col = prev_find(lines, 0, 0, ln, col, 'case')  # we can use '0, 0' because we know "case" starts on a newline (internals of prev_find() go line by line)

    if not ast.body:
        end_ln, end_col = next_find(lines, end_ln, end_col, len(lines) - 1, len(lines[-1]), ':')  # special case, deleted whole body, end must be set to just past the colon (which MUST follow somewhere there)
    elif semi := next_find(lines, end_ln, end_col, len(lines) - 1, len(lines[-1]), ';', True):  # if there is a trailing semicolon to last element then include it as part of case
        end_ln, end_col = semi
    else:
        return fstloc(ln, col, end_ln, end_col)

    return fstloc(ln, col, end_ln, end_col + 1)


def _loc_op(self: fst.FST) -> fstloc | None:
    """Get location of `operator`, `unaryop`, `cmpop` or if is standalone `boolop` from source if possible. `boolop` has
    no location if it has a parent because in this case it can be in multiple location in a `BoolOp`. We want to be
    consistent so we don't even give it a location if there is only one.

    **Note:** This function is explicitly safe to call from `FST.loc`.
    """

    assert self.a.__class__ in ASTS_LEAF_OP

    ast = self.a
    ast_cls = ast.__class__
    op = OPCLS2STR[ast_cls]
    lines = self.root._lines

    if not (parent := self.parent):  # standalone
        ln, col, src = next_frag(lines, 0, 0, len(lines) - 1, 0x7fffffffffffffff)  # must be there

        if ast_cls not in ASTS_LEAF_CMPOP_TWO_WORD:  # simple one element operator means we are done
            assert src == op

            return fstloc(ln, col, ln, col + len(src))

        op, op2 = op.split(' ')

        assert src == op

        end_ln, end_col, src = next_frag(lines, ln, col + len(op), len(lines) - 1, 0x7fffffffffffffff)  # must be there

        assert src == op2

        return fstloc(ln, col, end_ln, end_col + len(op2))

    # has a parent

    parenta = parent.a
    parent_cls = parenta.__class__

    if parent_cls is UnaryOp:
        ln, col, _, _ = parenta.f.loc

        return fstloc(ln, col, ln, col + len(op))

    if parent_cls is Compare:  # special handling due to compound operators and array of ops and comparators
        prev = parenta.comparators[idx - 1] if (idx := self.pfield.idx) else parenta.left

        _, _, end_ln, end_col = prev.f.loc

        if has_space := (ast_cls in ASTS_LEAF_CMPOP_TWO_WORD):  # stupid two-element operators, can be anything like "not    \\\n     in"
            op, op2 = op.split(' ')

        last_ln = len(lines) - 1
        last_col = len(lines[-1])

        if pos := next_find(lines, end_ln, end_col, last_ln, last_col, op):
            ln, col = pos

            if not has_space:
                return fstloc(ln, col, ln, col + len(op))

            if pos := next_find(lines, ln, col + len(op), last_ln, last_col, op2):
                ln2, col2 = pos

                return fstloc(ln, col, ln2, col2 + len(op2))

    elif prev := (getattr(parenta, 'left', None) or getattr(parenta, 'target', None)):
        _, _, prev_end_ln, prev_end_col = prev.f.loc

        if pos := next_find(lines, prev_end_ln, prev_end_col, len(lines) - 1, len(lines[-1]), op):
            ln, col = pos

            return fstloc(ln, col, ln, col + len(op))

    return None


def _loc_block_header_end(
    self: fst.FST, field: Literal['body', 'orelse', 'finalbody'] = 'body'
) -> tuple[int, int, int, int] | None:
    """Return the position of the end of the given block header if it exists as well as either the end of the last child
    in the header if `field='body'` or the start of the `else` or `finally` otherwise.

    **Returns:**
    - `None`: If doesn't have the requested `field` or anything in it.
    - `(last header child end_ln, last child header end_col, after colon ln, after colon col)`:
        If `field='body'` or `field='orelse'` and the node is an `elif` returns the position of the end of the last
        child in the header (sans closing pars) and the position of the `:` of the the block statement header (just past
        it). If there is no last child (like in a `Try`, `TryStar` or maybe simple `FunctionDef`) then returns start of
        `self` for this loction.
    - `(start of block header ln, start of block header col, after colon ln, after  colon col)`:
        If `field='orelse'` or `'field='finalbody'` then returns location from start of the `else` or `finally` to just
        past the `:` of the block header.
    """

    assert self.a.__class__ in ASTS_LEAF_BLOCK

    ast = self.a
    ln, col, end_ln, end_col = self.loc

    if child := last_block_header_child(ast):
        if loc := (child := child.f).loc:  # because of empty function def arguments which won't have a .loc
            _, _, ln, col = loc
        elif child := child.prev():
            _, _, ln, col = child.loc

    colon_ln, colon_col = next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # must be there

    if field == 'body':
        return ln, col, colon_ln, colon_col + 1  # last child end location and block header end location just past the ':'

    if not (body := getattr(ast, field, None)):
        return None

    body0 = body[0].f

    if body0.is_elif():  # if child is elif then it starts BEFORE the header colon we want, so we just get the block header end of its 'body'
        return body0._loc_block_header_end('body')

    body0_ln, body0_col, _, _ = body0.bloc

    if prev := body0.prev('loc'):
        _, _, ln, col = prev.bloc
    else:
        ln, col, _, _ = self.loc

    lines = self.root._lines
    state = []

    colon_ln, colon_col = prev_find(lines, ln, col, body0_ln, body0_col, ':', True, state=state)  # must be there
    ln, col, src = prev_frag(lines, ln, col, colon_ln, colon_col, state=state)  # must be there

    assert src.startswith('else' if field == 'orelse' else 'finally')

    return ln, col, colon_ln, colon_col + 1  # block header start and end location just past the ':'


def _loc_comprehension_if(self: fst.FST, idx: int, pars: bool = True) -> fstloc:
    """Location `comprehension` or `_comprehension_ifs` expression including the leading `if` (which is not included in
    the location of the expression itself).

    **WARNING:** `idx` must be non-negative.
    """

    assert self.a.__class__ in _ASTS_LEAF_COMPREHENSION_OR_IFS

    ast = self.a
    ifs = ast.ifs

    ln, col, end_ln, end_col = ifs[idx].f.pars() if pars else ifs[idx].f.loc

    if idx:
        _, _, prev_ln, prev_col = ifs[idx - 1].f.loc
    elif ast.__class__ is comprehension:
        _, _, prev_ln, prev_col = ast.iter.f.loc
    else:  # isinstance(ast, _comprehension_ifs)
        prev_ln, prev_col, _, _ = self.loc  # should be 0, 0 but in case someone inserts some garbage before

    ln, col = next_find(self.root._lines, prev_ln, prev_col, ln, col, 'if')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_argument(self: fst.FST, default: bool = False) -> fstloc:
    """Get the location of the argument `self` including the leading `*` for a `vararg` or `**` for a `kwarg` if is one
    of those. Can return end of argument or end of default value which corresponds to this argument, but this will only
    be returned if requested with `default=True` and if `self` is actually a child of an `arguments` node.

    **Parameters:**
    - `default`: Whether to include the default value of this argument in the location or not.
        - `True`: Will return end as end of the default value for this node if present. Will also return the default
            node as a `.default` attribute of the returned location. If there is no parent or the parent is not an
            `arguments` node then this fails silently and the `.default` attribute returned will be `None` the same as
            if there was no default.
        - `False`: Will return end of this `arg` as end location and there will not be a `.default` attribute at all.

    **Returns:**
    - `fstloc | fstlocn`: Location of argument including any preceding `*` or `**` and optionally ending at the end of
        its default value. If `default=True` then there will be a `.default` attribute which will either be the node of
        the default value or `None`.
    """

    loc = self.loc

    if not (pfield := self.pfield):
        return fstlocn(*loc, default=None) if default else loc

    ln, col, end_ln, end_col = loc
    field, _ = pfield

    if (is_kwarg := field == 'kwarg') or field == 'vararg':
        lines = self.root._lines

        if prev := self.prev():
            _, _, prev_ln, prev_col = prev.loc
        else:
            prev_ln, prev_col, _, _ = self.parent.loc

        ln, col, src = prev_frag(lines, prev_ln, prev_col, ln, col)  # must be there
        col += len(src) - (2 if is_kwarg else 1)

        if default:
            return fstlocn(ln, col, end_ln, end_col, default=None)
        else:
            return fstloc(ln, col, end_ln, end_col)

    if not default:
        return loc

    default = None

    if (next := self.next()) and next.pfield.name in ('defaults', 'kw_defaults'):
        _, _, end_ln, end_col = next.pars()
        default = next

    return fstlocn(ln, col, end_ln, end_col, default=default)


def _loc_decorator(self: fst.FST, idx: int, pars: bool = True) -> fstloc:
    r"""Location of `FunctionDef`, `AsyncFunctionDef`, `ClassDef` or `_decorator_list` specific decorator expression
    including the leading `@` (which is not included in the location of the expression itself). We have a whole function
    for this because the `@` may not be on the same line as the decorator expression.

    **Note:** This function is explicitly safe to use from `FST.bloc` only with `pars=False`.

    **WARNING:** `idx` must be non-negative.

    **Examples:**
    >>> FST(r'''
    ... @deco1
    ... @ \
    ...  ( deco2 )
    ... @deco3
    ... class cls: pass
    ... '''.strip())._loc_decorator(1)
    fstloc(1, 0, 2, 10)
    """

    assert self.a.__class__ in _ASTS_LEAF_DEF_OR_DECO_LIST

    ast = self.a
    lines = self.root._lines
    decorator_list = ast.decorator_list

    ln, col, end_ln, end_col = decorator_list[idx].f.pars() if pars else decorator_list[idx].f.loc

    if m := _re_deco_start.match(lines[ln]):  # if '@' is on the line expected preceded by only space then we are done, use column of '@'
        return fstloc(ln, m.end() - 1, end_ln, end_col)  # m.end() instead of col because could come from a line continuation and '@' not be at same column as self

    ln, col = prev_find(lines, 0, 0, ln, col, '@')  # we can use start at (0, 0) because we know '@' must start a line

    return fstloc(ln, col, end_ln, end_col)


def _loc_Lambda_args_entire(self: fst.FST) -> fstloc:
    """`Lambda` `args` entire location from just past `lambda` keyword to ':', empty or not. `self` is the `Lambda`, not
    the `arguments`."""

    assert self.a.__class__ is Lambda

    ln, col, end_ln, end_col = self.loc
    col += 6
    lines = self.root._lines
    args = self.a.args.f

    if args.is_empty_arguments():
        end_ln, end_col = next_find(lines, ln, col, end_ln, end_col, ':')

    else:
        _, _, lln, lcol = args.last_child().loc
        end_ln, end_col = next_find(lines, lln, lcol, end_ln, end_col, ':')

    return fstloc(ln, col, end_ln, end_col)


def _loc_ClassDef_bases_pars(self: fst.FST) -> fstlocn:
    """Location of `class cls(...)` bases AND keywords fields-enclosing parentheses, or location where they should be
    put if not present currently (from end of `name` or `type_params` to just before `:`).

    **Returns:**
    - `fstlocn(..., n = pars present or not)`: Just like from `FST.pars()`, with attribute `n=0` meaning no parentheses
        present and location is where they should go and `n=1` meaning parentheses present and location is where they
        actually are.
    """

    assert self.a.__class__ is ClassDef

    ast = self.a
    lines = self.root._lines
    ln, col, end_ln, end_col = self.loc

    if body := ast.body:
        end_ln, end_col, _, _ = body[0].f.bloc

    if type_params := getattr(ast, 'type_params', None):  # if type_params then end of '[T, ...]' (py < 3.12 AST.type_params doesn't exist)
        _, _, ln, col = type_params[-1].f.loc

        ln, col = next_find(lines, ln, col, end_ln, end_col, ']')  # must be there
        col += 1

    else:  # otherwise end of class name
        ln, col, src = next_find_re(lines, ln, col + 5, end_ln, end_col, re_identifier)  # must be there
        col += len(src)

    lpln, lpcol, lpsrc = next_frag(lines, ln, col, end_ln, end_col)

    if not lpsrc.startswith('('):  # no parenthesis, must be ':'
        assert lpsrc.startswith(':')

        return fstlocn(ln, col, lpln, lpcol, n=0)

    if keywords := ast.keywords:
        lastkw = keywords[-1].value.f

        if (bases := ast.bases) and (lastbase := bases[-1].f).loc > lastkw.loc:
            _, _, ln, col = lastbase.pars()
        else:
            _, _, ln, col = lastkw.pars()

    elif bases := ast.bases:
        _, _, ln, col = bases[-1].f.pars()

    else:
        ln = lpln
        col = lpcol + 1

    rpln, rpcol = next_find(lines, ln, col, end_ln, end_col, ')')  # must be there

    return fstlocn(lpln, lpcol, rpln, rpcol + 1, n=1)


def _loc_ImportFrom_names_pars(self: fst.FST) -> fstlocn:
    """Location of `from ? import (...)` whole names field-enclosing parentheses, or location where they should be put
    if not present currently.

    Can handle empty `module` and `names`.

    **Returns:**
    - `fstlocn`: Just like from `FST.pars()`, with attribute `n=0` meaning no parentheses present and location is where
        they should go and `n=1` meaning parentheses present and location is where they actually are.
    """

    assert self.a.__class__ is ImportFrom

    lines = self.root._lines
    ln, col, end_ln, end_col = self.loc
    ln, col, _ = next_find_re(lines, ln, col, end_ln, end_col, _re_keyword_import)  # must be there (and 'import' is invalid as module or dotted component of it)
    col += 6

    if (lpar := next_frag(lines, ln, col, end_ln, end_col)) and lpar.src.startswith('('):  # opening par follows 'import'
        assert end_col and lines[end_ln][end_col - 1] == ')'  # closing par must be exactly at end

        ln, col, _ = lpar
        n = 1

    else:
        if lines[ln][col : col + 1].isspace():
            col += 1

        n = 0

    return fstlocn(ln, col, end_ln, end_col, n=n)


def _loc_With_items_pars(self: fst.FST) -> fstlocn:
    """Location of `with (...)` whole items field-enclosing parentheses, or location where they should be put if not
    present currently.

    Can handle empty `items`.

    **Note:** Parenthesizing the `items` if not present where it says may still result in "unparenthesized" with as
    those parentheses may pass on to belong to the child if it is a single item with no `optional_vars`.

    **Returns:**
    - `fstlocn(..., n = pars present or not, bound = bound of search)`: Just like from `FST.pars()`, with attribute
        `n=0` meaning no parentheses present and location is where they should go and `n=1` meaning parentheses present
        and location is where they actually are. There is also a `bound` attribute which is an `fstloc` which is the
        location from just past the `with` (no space) to just before the `:`.
    """

    assert self.a.__class__ in ASTS_LEAF_WITH

    ast = self.a
    lines = self.root._lines
    ln, col, end_ln, end_col = self.loc

    if ast.__class__ is AsyncWith:
        ln, col, _ = next_find_re(lines, ln, col, end_ln, end_col, _re_keyword_with_start)  # must be there, skip the 'async'

    col += 4

    if items := ast.items:
        _, _, after_items_ln, after_items_col = items[-1].f.loc
    else:  # we handle temporarily empty items
        after_items_ln = ln
        after_items_col = col

    end_ln, end_col = next_find(lines, after_items_ln, after_items_col, end_ln, end_col, ':')  # must be there

    bound = fstloc(ln, col, end_ln, end_col)

    if ((lpar := next_frag(lines, ln, col, end_ln, end_col))
        and lpar.src.startswith('(')  # does opening par follow 'with'
        and not (items and items[0].f.loc[:2] <= lpar[:2])  # if there are items and first `withitem` starts at !!! OR BEFORE !!! lpar found then we know that lpar belongs to it and whole `items` field doesn't have pars (OR BEFORE because this may be the case during operations in some places (put slice to BoolOp as of the writing of this comment))
    ):
        ln, col, _ = lpar

        if items:
            rpar = prev_frag(lines, after_items_ln, after_items_col, end_ln, end_col)  # closing par may not immediately precede the ':'
        else:
            rpar = prev_frag(lines, ln, col + 1, end_ln, end_col)

        assert rpar and rpar.src.endswith(')')

        end_ln, end_col, src = rpar
        end_col += len(src)
        n = 1

    else:
        if lines[ln][col : col + 1].isspace():
            col += 1

        n = 0

    return fstlocn(ln, col, end_ln, end_col, n=n, bound=bound)


def _loc_BoolOp_op(self: fst.FST, idx: int) -> fstloc:
    """Get location of operator in a `BoolOp` at index `idx`. The index works the same as in a `Compare.ops`, the first
    operator is between the first and second `values` and there are n-1 operators for n elements."""

    assert self.a.__class__ is BoolOp

    lines = self.root._lines
    ast = self.a
    values = ast.values
    op = 'and' if ast.op.__class__ is And else 'or'
    _, _, end_ln, end_col = values[idx].f.pars()
    ln, col, _ = next_frag(lines, end_ln, end_col, 0x7fffffffffffffff, 0x7fffffffffffffff)  # must be there

    return fstloc(ln, col, ln, col + len(op))


def _loc_Call_pars(self: fst.FST) -> fstloc:
    """Location is from just before opening par to just past closing par."""

    assert self.a.__class__ is Call

    ast = self.a
    lines = self.root._lines
    _, _, ln, col = ast.func.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col = next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_Subscript_brackets(self: fst.FST) -> fstloc:
    assert self.a.__class__ is Subscript

    ast = self.a
    lines = self.root._lines
    _, _, ln, col = ast.value.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col = next_find(lines, ln, col, end_ln, end_col, '[')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_MatchMapping_rest(self: fst.FST, stars: bool = False) -> fstloc | None:
    """Location of `rest` identifier if present, otherwise `None`.

    **Parameters:**
    - `stars`: What to return as the start.
        - `False`: The start of the identifier.
        - `True`: The start of the `**` double stars.
    """

    assert self.a.__class__ is MatchMapping

    ast = self.a

    if (rest := ast.rest) is None:
        return None

    ln, col, end_ln, end_col = self.loc
    end_col -= 1

    if patterns := ast.patterns:
        _, _, ln, col = patterns[-1].f.loc
    else:
        col += 1

    lines = self.root._lines

    if not stars:
        ln, col = next_find(lines, ln, col, end_ln, end_col, rest)

        return fstloc(ln, col, ln, col + len(rest))

    ln, col = next_find(lines, ln, col, end_ln, end_col, '**')
    end_ln, end_col, src = next_frag(lines, ln, col + 2, end_ln, end_col)  # must be there

    assert src.startswith(rest)

    return fstloc(ln, col, end_ln, end_col + len(rest))


def _loc_MatchClass_pars(self: fst.FST) -> fstloc:
    assert self.a.__class__ is MatchClass

    ast = self.a
    lines = self.root._lines
    _, _, ln, col = ast.cls.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col = next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_FunctionDef_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    assert self.a.__class__ in ASTS_LEAF_FUNCDEF

    ast = self.a
    lines = self.root._lines
    args = ast.args

    ln, col, end_ln, end_col = self.loc

    if after := (
        args.posonlyargs or args.args or args.vararg or args.kwonlyargs or args.kwarg or ast.returns or ast.body
    ):
        after_ln, after_col, _, _ = (after[0] if isinstance(after, list) else after).f.bloc
    else:  # accomodate temporarily empty bodies
        after_ln = end_ln
        after_col = end_col

    if ast.__class__ is AsyncFunctionDef:
        ln, col = next_find(lines, ln, col + 5, after_ln, after_col, 'def')  # must be there

    name_end_ln, name_end_col, src = next_find_re(lines, ln, col + 3, after_ln, after_col, re_identifier)  # must be there

    name_end_col += len(src)

    if not (pos := next_find(lines, name_end_ln, name_end_col, after_ln, after_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, after_ln, after_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def _loc_ClassDef_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    assert self.a.__class__ is ClassDef

    ast = self.a
    lines = self.root._lines

    ln, col, end_ln, end_col = self.loc

    if after := (ast.bases or ast.keywords or ast.body):
        after_ln, after_col, _, _ = after[0].f.bloc  # .bloc because body[0] might start with a decorator
    else:  # accomodate temporarily empty bodies
        after_ln = end_ln
        after_col = end_col

    name_end_ln, name_end_col, src = next_find_re(lines, ln, col + 5, after_ln, after_col, re_identifier)  # must be there

    name_end_col += len(src)

    if not (pos := next_find(lines, name_end_ln, name_end_col, after_ln, after_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, after_ln, after_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def _loc_TypeAlias_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    assert self.a.__class__ is TypeAlias

    ast = self.a
    lines = self.root._lines

    _, _, name_end_ln, name_end_col = ast.name.f.loc
    val_ln, val_col, _, _ = ast.value.f.loc

    if not (pos := next_find(lines, name_end_ln, name_end_col, val_ln, val_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, val_ln, val_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def _loc_Global_Nonlocal_names(self: fst.FST, first: int, last: int | None = None) -> fstloc | tuple[fstloc, fstloc]:
    """We assume `first` and optionally `last` are in [0..len(names)), no negative or out-of-bounds and `last` follows
    or equals `first` if present."""

    assert self.a.__class__ in ASTS_LEAF_VAR_SCOPE_DECL

    ln, col, end_ln, end_col = self.loc

    col += 6 if self.a.__class__ is Global else 8
    lines = self.root._lines
    idx = first

    while idx:  # skip the commas
        ln, col = next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col += 1
        idx -= 1

    ln, col, src = next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there
    first_loc = fstloc(ln, col, ln, col := col + len(src))

    if last is None:
        return first_loc

    if not (idx := last - first):
        return first_loc, first_loc

    while idx:
        ln, col = next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col += 1
        idx -= 1

    ln, col, src = next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there

    return first_loc, fstloc(ln, col, ln, col + len(src))
