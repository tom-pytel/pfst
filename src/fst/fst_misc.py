"""Misc lower level FST methods."""

import re
from ast import *
from math import log10
from typing import Callable, Literal, Optional, Union

from .astutil import *
from .astutil import Interpolation

from .shared import (
    astfield, fstloc, nspace,
    BLOCK,
    HAS_DOCSTRING,
    _next_src, _prev_src, _next_find, _prev_find, _next_pars, _prev_pars,
)

_astfieldctx = astfield('ctx')

_re_par_open_alnums  = re.compile(r'\w[(]\w')
_re_par_close_alnums = re.compile(r'\w[)]\w')


def _make_tree_fst(ast: AST, parent: 'FST', pfield: astfield) -> 'FST':
    """Make `FST` node from `AST`, recreating possibly non-unique AST nodes."""

    if not getattr(ast, 'f', None):  # if `.f` exists then this has already been done
        if isinstance(ast, (expr_context, unaryop, operator, boolop, cmpop)):  # ast.parse() reuses simple objects, we need all objects to be unique
            pfield.set(parent.a, ast := ast.__class__())

    return FST(ast, parent, pfield)


def _out_lines(fst: 'FST', linefunc: Callable, ln: int, col: int, end_ln: int, end_col: int, eol: str = ''):
    width = int(log10(len(fst.root._lines) - 1 or 1)) + 1
    lines = fst.get_src(ln, col, end_ln, end_col, True)

    if (l := lines[-1][:end_col]).endswith(' '):
        l += '<'

    lines[-1] = l

    if (l := lines[0]).startswith(' ') and col:
        lines[0]  = f'{" " * (col - 1)}>{l}'
    else:
        lines[0]  = ' ' * col + l

    for i, l in zip(range(ln, end_ln + 1), lines):
        linefunc(f'{i:<{width}}: {l}{eol}')


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

@staticmethod
def _new_empty_module(*, from_: Optional['FST'] = None) -> 'FST':
    return FST(Module(body=[], type_ignores=[]), [''], from_=from_)


@staticmethod
def _new_empty_tuple(*, from_: Optional['FST'] = None) -> 'FST':
    ast = Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, ['()'], from_=from_)


@staticmethod
def _new_empty_list(*, from_: Optional['FST'] = None) -> 'FST':
    ast = List(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, ['[]'], from_=from_)


@staticmethod
def _new_empty_dict(*, from_: Optional['FST'] = None) -> 'FST':
    ast = Dict(keys=[], values=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, ['{}'], from_=from_)


@staticmethod
def _new_empty_set(only_ast: bool = False, lineno: int = 1, col_offset: int = 0, *,
                   from_: Optional['FST'] = None) -> Union['FST', AST]:
    ast = Set(elts=[
        Starred(value=Tuple(elts=[], ctx=Load(), lineno=lineno, col_offset=col_offset+2,
                            end_lineno=lineno, end_col_offset=col_offset+4),
                ctx=Load(), lineno=lineno, col_offset=col_offset+1, end_lineno=lineno, end_col_offset=col_offset+4)
    ], lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return ast if only_ast else FST(ast, ['{*()}'], from_=from_)


@staticmethod
def _new_empty_set_curlies(only_ast: bool = False, lineno: int = 1, col_offset: int = 0, *,
                           from_: Optional['FST'] = None) -> Union['FST', AST]:
    ast = Set(elts=[], lineno=lineno, col_offset=col_offset, end_lineno=lineno,
            end_col_offset=col_offset + 2)

    return ast if only_ast else FST(ast, ['{}'], from_=from_)


def _repr_tail(self: 'FST') -> str:
    try:
        loc = self.loc
    except Exception:  # maybe in middle of operation changing locations and lines
        loc = '????'

    self.touch(False, True, True)  # for debugging because we may have cached locs which would not have otherwise been cached during execution

    tail = ' ROOT' if self.is_root else ''

    return f'{tail} {loc[0]},{loc[1]} -> {loc[2]},{loc[3]}' if loc else tail


def _dump(self: 'FST', st: nspace, cind: str = '', prefix: str = ''):
    ast  = self.a
    tail = self._repr_tail()
    sind = ' ' * st.indent

    if not st.src:  # nop
        pass

    elif isinstance(ast, stmt):  # src = 'line' or 'node'
        if loc := self.bloc:
            if isinstance(ast, BLOCK):
                _out_lines(self, st.linefunc, loc.ln, loc.col, *self._loc_block_header_end(), st.eol)
            else:
                _out_lines(self, st.linefunc, *loc, st.eol)

    elif (st.src == 'node' and not isinstance(ast, mod) and (not (parent := self.parent) or
                                                             not isinstance(parent.a, Expr))):
        if loc := self.loc:
            _out_lines(self, st.linefunc, *loc, st.eol)

    if st.compact:
        if isinstance(ast, Name):
            st.linefunc(f'{cind}{prefix}Name {ast.id!r} {ast.ctx.__class__.__qualname__}{" .." * bool(tail)}{tail}'
                        f'{st.eol}')

            return

        if isinstance(ast, Constant):
            if ast.kind is None:
                st.linefunc(f'{cind}{prefix}Constant {ast.value!r}{" .." * bool(tail)}{tail}{st.eol}')
            else:
                st.linefunc(f'{cind}{prefix}Constant {ast.value!r} {ast.kind}{" .." * bool(tail)}{tail}{st.eol}')

            return

    st.linefunc(f'{cind}{prefix}{ast.__class__.__qualname__}{" .." * bool(tail)}{tail}{st.eol}')

    for name, child in iter_fields(ast):
        is_list = isinstance(child, list)

        if st.compact:
            if child is None and not st.full:
                continue

            if name == 'ctx':
                st.linefunc(f'{sind}{cind}.{name} '
                            f'{child.__class__.__qualname__ if isinstance(child, AST) else child}{st.eol}')

                continue

            if (name in ('type', 'id', 'attr', 'module', 'arg', 'vararg', 'kwarg', 'rest', 'format_spec',
                            'name', 'value', 'left', 'right', 'operand', 'returns', 'target',
                            'annotation', 'iter', 'test','exc', 'cause', 'msg', 'elt', 'key', 'func',
                            'slice', 'lower', 'upper', 'step', 'guard', 'context_expr', 'optional_vars',
                            'cls', 'bound', 'default_value', 'pattern', 'subject',
                            'type_comment', 'lineno', 'tag', 'op',
                            'simple', 'level', 'conversion', 'str', 'is_async', 'lineno')
                        or (not is_list and name in
                            ('body', 'orelse'))
            ):
                if isinstance(child, AST):
                    child.f._dump(st, cind + sind, f'.{name} ')
                else:
                    st.linefunc(f'{sind}{cind}.{name} {child!r}{st.eol}')

                continue

            if name == 'args' and isinstance(child, arguments):
                if child.posonlyargs or child.args or child.vararg or child.kwonlyargs or child.kwarg:
                    child.f._dump(st, cind + sind, '.args ')

                    continue

                elif not st.full:
                    continue

        if st.full or (child != []):
            st.linefunc(f'{sind}{cind}.{name}{f"[{len(child)}]" if is_list else ""}{st.eol}')

        if is_list:
            for i, ast in enumerate(child):
                if isinstance(ast, AST):
                    ast.f._dump(st, cind + sind, f'{i}] ')
                else:
                    st.linefunc(f'{sind}{cind}{i}] {ast!r}{st.eol}')

        elif isinstance(child, AST):
            child.f._dump(st, cind + sind * 2)
        else:
            st.linefunc(f'{sind}{sind}{cind}{child!r}{st.eol}')


def _make_fst_tree(self: 'FST', stack: list['FST'] | None = None):
    """Create tree of FST nodes, one for each AST node from root. Call only on root or with pre-made stack of nodes
    to walk."""

    if stack is None:
        stack = [self]

    while stack:
        for name, child in iter_fields((f := stack.pop()).a):
            if isinstance(child, AST):
                stack.append(_make_tree_fst(child, f, astfield(name)))
            elif isinstance(child, list):
                stack.extend(_make_tree_fst(a, f, astfield(name, idx))
                             for idx, a in enumerate(child) if isinstance(a, AST))


def _unmake_fst_tree(self: 'FST', stack: list[AST] | None = None):
    """Destroy a tree of FST child nodes by breaking links between AST and FST nodes. This mainly helps make sure
    destroyed FST nodes can't be reused in a way that might corrupt valid remaining trees."""

    if stack is None:
        stack = [self.a]

    while stack:  # make sure these bad ASTs can't hurt us anymore
        if a := stack.pop():  # could be `None`s in there
            a.f.a = a.f = None  # root, parent and pfield are still useful after node has been removed

            stack.extend(iter_child_nodes(a))


def _unmake_fst_parents(self: 'FST', self_: bool = False):
    """Walk up parent list unmaking each parent along the way. This does not unmake the entire parent tree, just the
    parents directly above this node (and including `self` if `self_` is `True). Meant for when you know the parents are
    just a direct succession like Expr -> Module."""

    if self_:
        self.a.f = self.a = None

    while self := self.parent:
        self.a.f = self.a = None


def _set_ast(self: 'FST', ast: AST, unmake: bool = True) -> AST:
    """Set `.a` AST node for this `FST` node and `_make_fst_tree` for `self`, also set ast node in parent AST node.
    Optionally `_unmake_fst_tree()` for with old `.a` node first. Returns old `.a` node.

    **Parameters:**
    - `unmake`: Whether to unmake the FST tree being replaced or not. Should really always unmake.
    """

    old_ast = self.a

    if unmake:
        self._unmake_fst_tree()

        if f := getattr(ast, 'f', None):
            f.a = None

    self.a = ast
    ast.f  = self

    self._make_fst_tree()

    if parent := self.parent:
        self.pfield.set(parent.a, ast)

    self._touch()

    return old_ast


def _set_ctx(self: 'FST', ctx: type[expr_context]):
    """Set `ctx` field for `self` and applicable children. Differs from `astutil.set_ctx()` by creating `FST` nodes
    directly. When the `astutil` one is used it is followed by something which creates the `FST` nodes for the new
    `ctx` fields."""

    stack = [self.a]

    while stack:
        a = stack.pop()

        if (((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute))) and not isinstance(a.ctx, ctx)
        ):
            a.ctx = child = ctx()

            _make_tree_fst(child, a.f, _astfieldctx)

            if is_seq:
                stack.extend(a.elts)
            elif is_starred:
                stack.append(a.value)


def _next_bound(self: 'FST', with_loc: bool | Literal['all', 'own'] = 'all') -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object within parent. If no siblings found after
    self then return end of parent. If no parent then return end of source."""

    if next := self.next(with_loc):
        return next.bloc[:2]
    elif parent := self.parent:
        return parent.bloc[2:]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound(self: 'FST', with_loc: bool | Literal['all', 'own'] = 'all') -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object within parent. If no siblings found before
    self then return start of parent. If no parent then return (0, 0)."""

    if prev := self.prev(with_loc):
        return prev.bloc[2:]
    elif parent := self.parent:
        return parent.bloc[:2]
    else:
        return 0, 0


def _next_bound_step(self: 'FST', with_loc: bool | Literal['all', 'own', 'allown'] = 'all') -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object using `next_step()`. This is safe to call
    for nodes that live inside nodes without their own locations if `with_loc='allown'`."""

    if next := self.next_step(with_loc, recurse_self=False):
        return next.bloc[:2]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound_step(self: 'FST', with_loc: bool | Literal['all', 'own', 'allown'] = 'all') -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object using `prev_step()`. This is safe to call for
    nodes that live inside nodes without their own locations if `with_loc='allown'`."""

    if prev := self.prev_step(with_loc, recurse_self=False):
        return prev.bloc[2:]

    return 0, 0


def _loc_block_header_end(self: 'FST', ret_bound: bool = False) -> fstloc | tuple[int, int] | None:
    """Return location of the end of the block header line(s) for block node, just past the ':', or None if `self`
    is not a block header node.

    **Parameters:**
    - `ret_bound`: If `False` then just returns the end position. `True` means return the range used for the search,
        which includes a start at the end of the last child node in the block header or beginning of the block node if
        no child nodes in header.
    """

    # assert isinstance(self.s, BLOCK)

    ln, col, end_ln, end_col = self.loc

    if child := last_block_header_child(a := self.a):
        if loc := (child := child.f).loc:  # because of empty function def arguments which won't have a .loc
            _, _, cend_ln, cend_col = loc
        elif child := child.prev():  # guaranteed to have loc if is there
            _, _, cend_ln, cend_col = child.loc

        else:
            cend_ln  = ln
            cend_col = col

    elif isinstance(a, BLOCK):
        cend_ln  = ln
        cend_col = col

    else:
        return None

    ln, col = _next_find(self.root._lines, cend_ln, cend_col, end_ln, end_col, ':')  # it must be there

    return fstloc(cend_ln, cend_col, ln, col + 1) if ret_bound else (ln, col + 1)


def _loc_operator(self: 'FST') -> fstloc | None:
    """Get location of `operator`, `unaryop` or `cmpop` from source if possible. `boolop` has no location if it has a
    parent because in this case it can be in multiple location in a `BoolOp` and we want to be consistent."""

    # assert isinstance(self.s, (operator, unaryop, cmpop))

    ast = self.a

    if not (op := OPCLS2STR.get(ast.__class__)):
        return None

    lines = self.root._lines

    if not (parent := self.parent):  # standalone
        ln, col, src = _next_src(lines, 0, 0, len(lines) - 1, 0x7fffffffffffffff)  # must be there

        if not isinstance(ast, (NotIn, IsNot)):  # simple one element operator means we are done
            assert src == op or (isinstance(ast, operator) and src == op + '=')

            return fstloc(ln, col, ln, col + len(src))

        op, op2 = op.split(' ')

        assert src == op

        end_ln, end_col, src = _next_src(lines, ln, col + len(op), len(lines) - 1, 0x7fffffffffffffff)  # must be there

        assert src == op2

        return fstloc(ln, col, end_ln, end_col + len(op2))

    # has a parent

    parenta = parent.a

    if isinstance(parenta, UnaryOp):
        ln, col, _, _ = parenta.f.loc

        return fstloc(ln, col, ln, col + len(op))

    if isinstance(parenta, Compare):  # special handling due to compound operators and array of ops and comparators
        prev = parenta.comparators[idx - 1] if (idx := self.pfield.idx) else parenta.left

        _, _, end_ln, end_col = prev.f.loc

        if has_space := isinstance(ast, (NotIn, IsNot)):  # stupid two-element operators, can be anything like "not    \\\n     in"
            op, op2 = op.split(' ')

        if pos := _next_find(lines, end_ln, end_col, end_lines := len(lines) - 1, len(lines[-1]), op):
            ln, col = pos

            if not has_space:
                return fstloc(ln, col, ln, col + len(op))

            if pos := _next_find(lines, ln, col + len(op), end_lines, len(lines[-1]), op2):
                ln2, col2 = pos

                return fstloc(ln, col, ln2, col2 + len(op2))

    elif (prev := (is_binop := getattr(parenta, 'left', None))) or (prev := getattr(parenta, 'target', None)):
        if pos := _next_find(lines, (loc := prev.f.loc).end_ln, loc.end_col, len(lines) - 1, len(lines[-1]), op):
            ln, col = pos

            return fstloc(ln, col, ln, col + len(op) + (not is_binop))  # 'not is_binop' adds AugAssign '=' len

    return None


def _loc_comprehension(self: 'FST') -> fstloc:
    """`comprehension` location from children. Called from `.loc`."""

    # assert isinstance(self.s, comprehension)

    ast   = self.a
    first = ast.target.f
    last  = ifs[-1].f if (ifs := ast.ifs) else ast.iter.f  # self.last_child(), could be .iter or last .ifs
    lines = self.root._lines

    if prev := self.prev_step('allown', recurse_self=False):  # 'allown' so it doesn't recurse into calling `.loc`
        _, _, ln, col = prev.loc
    else:
        ln = col = 0

    start_ln, start_col = _prev_find(lines, ln, col, first.ln, first.col, 'for')  # must be there

    if ast.is_async:
        start_ln, start_col = _prev_find(lines, ln, col, start_ln, start_col, 'async')  # must be there

    rpars = _next_pars(lines, last.end_ln, last.end_col, *self._next_bound_step('allown'))

    if (lrpars := len(rpars)) == 1:  # no pars, just use end of last
        end_ln, end_col = rpars[0]

    else:
        is_genexp_last = ((parent := self.parent) and isinstance(parent.a, GeneratorExp) and  # correct for parenthesized GeneratorExp
                          self.pfield.idx == len(parent.a.generators) - 1)

        if is_genexp_last and lrpars == 2:  # can't be pars on left since only par on right was close of GeneratorExp
            end_ln, end_col = rpars[0]
        else:

            end_ln, end_col = rpars[len(_prev_pars(lines, *last._prev_bound(), last.ln, last.col)) - 1]  # get rpar according to how many pars on left

    return fstloc(start_ln, start_col, end_ln, end_col)


def _loc_arguments(self: 'FST') -> fstloc | None:
    """`arguments` location from children. Called from `.loc`. Returns `None` when there are no arguments."""

    # assert isinstance(self.s, arguments)

    if not (first := self.first_child()):
        return None

    ast       = self.a
    last      = self.last_child()
    lines     = self.root._lines
    end_lines = len(lines) - 1
    rpars     = _next_pars(lines, last.end_ln, last.end_col, *self._next_bound())

    end_ln, end_col           = rpars[-1]
    start_ln, start_col, _, _ = first.loc

    if ast.posonlyargs:
        leading_stars  = None  # no leading stars
        trailing_slash = False if ast.args or ast.vararg or ast.kwonlyargs or ast.kwarg else True

    else:
        trailing_slash = False

        if ast.args:
            leading_stars = None  # no leading stars
        elif ast.vararg or ast.kwonlyargs:
            leading_stars = '*'  # leading star just before varname or bare leading star with comma following
        elif ast.kwarg:
            leading_stars = '**'  # leading double star just before varname

    if (code := _next_src(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff)) and code.src.startswith(','):  # trailing comma
        end_ln, end_col, _  = code
        end_col            += 1

    elif (parent := self.parent) and isinstance(parent.a, (FunctionDef, AsyncFunctionDef)):  # arguments enclosed in pars
        end_ln, end_col = rpars[-2]  # must be there

    if leading_stars:  # find star to the left, we know it exists so we don't check for None return
        start_ln, start_col = _prev_find(lines, *self._prev_bound(), start_ln, start_col, leading_stars)

    if trailing_slash:
        end_ln, end_col  = _next_find(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff, '/')  # must be there
        end_col         += 1

        if (code := _next_src(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff)) and code.src.startswith(','):  # silly, but, trailing comma trailing slash
            end_ln, end_col, _  = code
            end_col            += 1

    return fstloc(start_ln, start_col, end_ln, end_col)


def _loc_arguments_empty(self: 'FST') -> fstloc:
    """`arguments` location for empty arguments ONLY! DO NOT CALL FOR NONEMPTY ARGUMENTS!"""

    # assert isinstance(self.a, arguments)

    if not (parent := self.parent):
        return fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))  # parent=None means we are root

    ln, col, end_ln, end_col = parent.loc
    lines                    = self.root._lines

    if isinstance(parenta := parent.a, Lambda):
        col             += 6
        end_ln, end_col  = _next_find(lines, ln, col, end_ln, end_col, ':')

    else:
        if type_params := getattr(parenta, 'type_params', None):  # doesn't exist in py < 3.12
            _, _, ln, col = type_params[-1].f.loc

        ln, col          = _next_find(lines, ln, col, end_ln, end_col, '(')
        col             += 1
        end_ln, end_col  = _next_find(lines, ln, col, end_ln, end_col, ')')

    return fstloc(ln, col, end_ln, end_col)


def _loc_lambda_args_entire(self: 'FST') -> fstloc:
    """`Lambda` `args` entire location from just past `lambda` keyword to ':', empty or not. `self` is the `Lambda`, not
    the `arguments`."""

    # assert isinstance(self.a, Lambda)

    ln, col, end_ln, end_col  = self.loc
    col                      += 6
    lines                     = self.root._lines

    if not (args := self.a.args.f).loc:
        end_ln, end_col = _next_find(lines, ln, col, end_ln, end_col, ':')

    else:
        _, _, lln, lcol = args.last_child().loc
        end_ln, end_col = _next_find(lines, lln, lcol, end_ln, end_col, ':')

    return fstloc(ln, col, end_ln, end_col)


def _loc_withitem(self: 'FST') -> fstloc:
    """`withitem` location from children. Called from `.loc`."""

    # assert isinstance(self.s, withitem)

    ast   = self.a
    ce    = ast.context_expr.f
    lines = self.root._lines

    ce_ln, ce_col, ce_end_ln, ce_end_col = ce_loc = ce.loc

    if not (ov := ast.optional_vars):
        rpars = _next_pars(lines, ce_end_ln, ce_end_col, *self._next_bound_step('allown'))  # 'allown' so it doesn't recurse into calling `.loc`

        if (lrpars := len(rpars)) == 1:
            return ce_loc

        lpars = _prev_pars(lines, *self._prev_bound_step('allown'), ce_ln, ce_col)
        npars = min(lrpars, len(lpars)) - 1

        return fstloc(*lpars[npars], *rpars[npars])

    ov_ln, ov_col, ov_end_ln, ov_end_col = ov_loc = ov.f.loc

    rpars = _next_pars(lines, ce_end_ln, ce_end_col, ov_ln, ov_col)

    if (lrpars := len(rpars)) == 1:
        ln  = ce_ln
        col = ce_col

    else:
        lpars   = _prev_pars(lines, *self._prev_bound_step('allown'), ce_ln, ce_col)
        ln, col = lpars[min(lrpars, len(lpars)) - 1]

    lpars = _prev_pars(lines, ce_end_ln, ce_end_col, ov_ln, ov_col)

    if (llpars := len(lpars)) == 1:
        return fstloc(ln, col, ov_end_ln, ov_end_col)

    rpars           = _next_pars(lines, ov_end_ln, ov_end_col, *self._next_bound_step('allown'))
    end_ln, end_col = rpars[min(llpars, len(rpars)) - 1]

    return fstloc(ln, col, end_ln, end_col)


def _loc_match_case(self: 'FST') -> fstloc:
    """`match_case` location from children. Called from `.loc`."""

    # assert isinstance(self.a, match_case)

    ast   = self.a
    first = ast.pattern.f
    last  = self.last_child()
    lines = self.root._lines

    start = _prev_find(lines, 0, 0, first.ln, first.col, 'case')  # we can use '0, 0' because we know "case" starts on a newline

    if ast.body:
        return fstloc(*start, last.bend_ln, last.bend_col)

    end_ln, end_col = _next_find(lines, last.bend_ln, last.bend_col, len(lines) - 1, len(lines[-1]), ':')  # special case, deleted whole body, end must be set to just past the colon (which MUST follow somewhere there)

    return fstloc(*start, end_ln, end_col + 1)


def _loc_Call_pars(self: 'FST') -> fstloc:
    # assert isinstance(self.s, Call)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.func.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = _next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_Subscript_brackets(self: 'FST') -> fstloc:
    # assert isinstance(self.s, Subscript)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.value.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = _next_find(lines, ln, col, end_ln, end_col, '[')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_MatchClass_pars(self: 'FST') -> fstloc:
    # assert isinstance(self.s, MatchClass)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.cls.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = _next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _dict_key_or_mock_loc(self: 'FST', key: AST | None, value: 'FST') -> Union['FST', fstloc]:
    """Return same dictionary key `FST` if exists, otherwise return a location for the preceding '**' code."""

    if key:
        return key.f

    if idx := value.pfield.idx:
        f   = value.parent.a.values[idx - 1].f  # because of multiline strings, could be a fake comment start inside one which hides a valid '**'
        ln  = f.end_ln
        col = f.end_col

    else:
        ln  = self.ln
        col = self.col

    ln, col = _prev_find(self.root._lines, ln, col, value.ln, value.col, '**')  # '**' must be there

    return fstloc(ln, col, ln, col + 2)


def _touch(self: 'FST') -> 'FST':  # -> Self
    """AST node was modified, clear out any cached info for this node only."""

    self._cache.clear()

    return self


def _sanitize(self: 'FST') -> 'FST':  # -> Self
    """Quick check to make sure that nodes which are not `stmt`, `ExceptHandler`, `match_case` or `mod` don't have any
    extra junk in the source and that the parenthesized location matches the whole location of the source. If not then
    fix by removing the junk."""

    if not self.is_root:
        raise ValueError('can only be called on root node')

    if not (loc := self.pars()) or loc == self.whole_loc:
        return self

    ln, col, end_ln, end_col = loc
    lines                    = self._lines

    self.offset(ln, col, -ln, -lines[ln].c2b(col))

    lines[end_ln] = bistr(lines[end_ln][:end_col])
    lines[ln]     = bistr(lines[ln][col:])

    del lines[end_ln + 1:], lines[:ln]

    return self


def _set_end_pos(self: 'FST', end_lineno: int, end_col_offset: int, self_: bool = True):  # because of trailing non-AST junk in last statements
    """Walk up parent chain (starting at `self`) setting `.end_lineno` and `.end_col_offset` to `end_lineno` and
    `end_col_offset` if self is last child of parent. Initial `self` is corrected always. Used for correcting
    parents after an `offset()` which removed or modified last child statements of block parents."""

    while True:
        if not self_:
            self_ = True

        else:
            if hasattr(a := self.a, 'end_lineno'):  # because of ASTs which locations
                a.end_lineno     = end_lineno
                a.end_col_offset = end_col_offset

            self._touch()

        if not (parent := self.parent) or self.next():  # self is not parent.last_child():
            break

        self = parent


def _set_block_end_from_last_child(self: 'FST', bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int):
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
            end_lineno     = last_child.end_lineno
            end_col_offset = last_child.end_col_offset

    if end_lineno is None:
        lines = self.root._lines

        if end := _prev_find(lines, bound_ln, bound_col, bound_end_ln, bound_end_col, ':'):  # find first preceding block colon, its there unless first opened block in module
            end_ln, end_col  = end
            end_col         += 1  # just past the colon

        else:
            end_ln  = bound_ln
            end_col = bound_col

        end_lineno     = end_ln + 1
        end_col_offset = lines[end_ln].c2b(end_col)

    self._set_end_pos(end_lineno, end_col_offset)


def _maybe_add_comma(self: 'FST', ln: int, col: int, offset: bool, space: bool,
                     end_ln: int | None = None, end_col: int | None = None) -> bool:
    """Maybe add comma at start of span if not already present as first code in span. Will skip any closing
    parentheses for check and add.

    **Parameters:**
    - `ln`: Line start of span.
    - `col`: Column start of span.
    - `offset`: If `True` then will apply `offset()` to entire tree for new comma. If `False` then will just offset
        the end of self, use this when self is at top level.
    - `space`: Whether to add a space IF the span is zero length.

    **Returns:**
    - `bool`: Whether a comma was added or not (if wasn't present before or was).
    """

    root  = self.root
    lines = root._lines

    if end_ln is None:
        end_ln  = self.end_ln
        end_col = self.end_col

    while code := _next_src(lines, ln, col, end_ln, end_col):  # find comma or parens or something else
        cln, ccol, src = code

        for c in src:
            ccol += 1

            if c == ')':
                ln  = cln
                col = ccol

            elif c == ',':
                return False
            else:
                break

        else:
            continue

        break

    comma     = ', ' if space and ln == end_ln and col == end_col else ','
    lines[ln] = bistr(f'{(l := lines[ln])[:col]}{comma}{l[col:]}')

    if offset:
        root.offset(ln, col, 0, len(comma), True, exclude=self)

    elif ln == end_ln:
        self.a.end_col_offset += len(comma)

        self.touch(True)

    return True


def _maybe_add_singleton_tuple_comma(self: 'FST', offset: bool):
    """Maybe add comma to tuple if is singleton and comma not already there, parenthesization not checked or taken
    into account. `self.a` must be a `Tuple`.

    **Parameters:**
    - `offset`: If `True` then will apply `offset()` to entire tree for new comma. If `False` then will just offset
        the end of the `Tuple`, use this when `Tuple` is at top level.
    """

    # assert isinstance(self.a, Tuple)

    if (elts := self.a.elts) and len(elts) == 1:
        return self._maybe_add_comma((f := elts[0].f).end_ln, f.end_col, offset, False, self.end_ln,
                                     self.end_col - self._is_parenthesized_seq())


def _maybe_fix_tuple(self: 'FST', is_parenthesized: bool | None = None):
    # assert isinstance(self.a, Tuple)

    ast = self.a

    if is_parenthesized is None:
        is_parenthesized = self._is_parenthesized_seq()

    if ast.elts:
        self._maybe_add_singleton_tuple_comma(True)

        ln, _, end_ln, _ = self.loc

        if not is_parenthesized and end_ln != ln:  # `not self.is_atom` instead of `end_ln != ln``:  <-- TODO: this, also maybe double check for line continuations (aesthetic thing)?
            self._parenthesize_tuple()

    elif not is_parenthesized:  # if is unparenthesized tuple and empty left then need to add parentheses
        ln, col, end_ln, end_col = self.loc

        self.put_src(['()'], ln, col, end_ln, end_col, True, False)  # WARNING! `tail=True` may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized tuple starts, but haven't found a case where this can happen


def _maybe_fix_set(self: 'FST'):
    # assert isinstance(self.a, Set)

    if not self.a.elts:
        ln, col, end_ln, end_col = self.loc

        self.put_src(['{*()}'], ln, col, end_ln, end_col, True)
        self._set_ast(self._new_empty_set(True, (a := self.a).lineno, a.col_offset))


def _maybe_fix_elif(self: 'FST'):
    # assert isinstance(self.a, If)

    ln, col, _, _ = self.loc
    lines         = self.root._lines

    if lines[ln].startswith('elif', col):
        self.put_src(None, ln, col, ln, col + 2, False)


def _maybe_fix(self: 'FST', pars: bool = True):
    """Maybe fix source and `ctx` values for cut or copied nodes (to make subtrees parsable if the source is not after
    the operation). If cannot fix or ast is not parsable by itself then ast will be unchanged. Is meant to be a quick
    fix after a cut or copy operation, not full check, for that use `verify()`.

    WARNING! Only call on root node!
    """

    # assert self.is_root

    if isinstance(ast := self.a, If):
        self._maybe_fix_elif()

    elif isinstance(ast, expr):
        if not self.loc or not self.is_parsable():
            return

        self._set_ctx(Load)  # anything that is excluded by is_parsable() or does not have .loc does not need this

        if not pars:
            return

        ast        = self.a
        need_paren = None

        if is_tuple := isinstance(ast, Tuple):
            if self._is_parenthesized_seq():
                need_paren = False
            elif any(isinstance(e, NamedExpr) and not e.f.pars(True)[1] for e in ast.elts):  # unparenthesized walrus in naked tuple?
                need_paren = True

            self._maybe_add_singleton_tuple_comma(False)  # this exists because of copy lone Starred out of a Subscript.slice

        elif isinstance(ast, NamedExpr):  # naked walrus
            need_paren = True

        if need_paren is None:
            need_paren = not self.is_enclosed()

        if need_paren:
            if is_tuple:
                self._parenthesize_tuple()
            else:
                self._parenthesize_grouping()


def _is_arguments_empty(self: 'FST') -> bool:
    """Is this `arguments` node empty?"""

    # assert isinstance(self.a, arguments)

    return not ((a := self.a).posonlyargs or a.args or a.vararg or a.kwonlyargs or a.kwarg)


def _is_parenthesized_ImportFrom_names(self: 'FST') -> bool:
    # assert isinstance(self.a, ImportFrom)

    ln, col, _, _         = self.loc
    end_ln, end_col, _, _ = self.a.names[0].f.loc

    return _prev_src(self.root._lines, ln, col, end_ln, end_col).src.endswith('(')  # something is there for sure


def _is_parenthesized_With_items(self: 'FST') -> bool:
    # assert isinstance(self.a, (With, AsyncWith))

    ln, col, _, _         = self.loc
    end_ln, end_col, _, _ = self.a.items[0].f.loc  # will include any pars in child so don't need to depar

    return _prev_src(self.root._lines, ln, col, end_ln, end_col).src.endswith('(')  # something is there for sure


def _is_parenthesized_seq(self: 'FST', field: str = 'elts', lpar: str = '(', rpar: str = ')') -> bool:
    """Whether `self` is a parenthesized sequence of `field` or not. Makes sure the entire node is surrounded by a
    balanced pair of `lpar` and `rpar`. Functions as `is_parenthesized_tuple()` if already know is a Tuple. Other use is
    for `MatchSequence`, whether parenthesized or bracketed."""

    self_ln, self_col, self_end_ln, self_end_col = self.loc

    lines = self.root._lines

    if not lines[self_end_ln].startswith(rpar, self_end_col - 1):
        return False

    if not (asts := getattr(self.a, field)):
        return True  # return True if no children because assume '()' in this case

    if not lines[self_ln].startswith(lpar, self_col):
        return False

    f0_ln, f0_col, f0_end_ln, f0_end_col = asts[0].f.loc

    if f0_col == self_col and f0_ln == self_ln:
        return False

    _, _, fn_end_ln, fn_end_col = asts[-1].f.loc

    if fn_end_col == self_end_col and fn_end_ln == self_end_ln:
        return False

    # dagnabit! have to count parens

    self_end_col -= 1  # because for sure there is a comma between end of first element and end of tuple, so at worst we exclude either the tuple closing paren or a comma

    nparens = len(_next_pars(lines, self_ln, self_col, self_end_ln, self_end_col, lpar)) - 1  # yes, we use _next_pars() to count opening parens because we know conditions allow it

    if not nparens:
        return False

    nparens -= len(_next_pars(lines, f0_end_ln, f0_end_col, self_end_ln, self_end_col, rpar)) - 1

    return nparens > 0  # don't want to fiddle with checking if f0 is a parenthesized tuple


def _parenthesize_grouping(self: 'FST', whole: bool = True):
    """Parenthesize anything with non-node grouping parentheses. Just adds text parens around node adjusting parent
    locations but not the node itself.

    **Parameters:**
    - `whole`: If at root then parenthesize whole source instead of just node.
    """

    ln, col, end_ln, end_col = self.whole_loc if whole and self.is_root else self.loc

    self.put_src([')'], end_ln, end_col, end_ln, end_col, True, True, self, offset_excluded=False)
    self.offset(*self.put_src(['('], ln, col, ln, col, False, False, self, offset_excluded=False))


def _parenthesize_tuple(self: 'FST', whole: bool = True):
    """Parenthesize an unparenthesized tuple, adjusting tuple location for added parentheses.

    WARNING! No checks are done so don't call on anything other than an unparenthesized Tuple!

    **Parameters:**
    - `whole`: If at root then parenthesize whole source instead of just node.
    """

    # assert isinstance(self.a, Tuple)

    ln, col, end_ln, end_col = self.whole_loc if whole and self.is_root else self.loc

    self.put_src([')'], end_ln, end_col, end_ln, end_col, True, False, self)

    lines            = self.root._lines
    a                = self.a
    a.end_lineno     = end_ln + 1  # yes this can change
    a.end_col_offset = lines[end_ln].c2b(end_col + 1)  # can't count on this being set by put_src() because end of `whole` could be past end of tuple

    self.offset(*self.put_src(['('], ln, col, ln, col, False, False, self), self_=False)

    a.lineno     = ln + 1
    a.col_offset = lines[ln].c2b(col)  # ditto on the `whole` thing


def _unparenthesize_grouping(self: 'FST', share: bool = True) -> bool:
    """Remove grouping parentheses from anything if present. Just remove text parens around node and everything between
    them and node adjusting parent locations but not the node itself.

    **Parameters:**
    - `share`: Whether to allow merge of parentheses into share single call argument generator expression or not.

    **Returns:**
    - `bool`: Whether parentheses were removed or not (only removed if present to begin with and removable).
    """

    pars_loc, npars = self.pars(True)

    if share:
        share = self.is_solo_call_arg_genexp()

    if not npars and not share:
        return False

    ln , col,  end_ln,  end_col  = self.bloc
    pln, pcol, pend_ln, pend_col = pars_loc

    if share:  # special case merge solo argument GeneratorExp parentheses with call argument parens
        lines                    = self.root._lines
        _, _, cend_ln, cend_col  = self.parent.func.loc
        pln, pcol                = _prev_find(lines, cend_ln, cend_col, pln, pcol, '(')  # it must be there
        pend_ln, pend_col        = _next_find(lines, pend_ln, pend_col, len(lines) - 1, len(lines[-1]), ')')  # ditto
        pend_col                += 1

        self.put_src(None, end_ln, end_col, pend_ln, pend_col, True, self)
        self.put_src(None, pln, pcol, ln, col, False)

    else:  # in all other case we need to make sure par is not separating us from an alphanumeric on either side, and if so then just replace that par with a space
        lines = self.root._lines

        if pend_col >= 2 and _re_par_close_alnums.match(l := lines[pend_ln], pend_col - 2):
            lines[pend_ln] = bistr(l[:pend_col - 1] + ' ' + l[pend_col:])
        else:
            self.put_src(None, end_ln, end_col, pend_ln, pend_col, True, self)

        if pcol and _re_par_open_alnums.match(l := lines[pln], pcol - 1):
            lines[pln] = bistr(l[:pcol] + ' ' + l[pcol + 1:])
        else:
            self.put_src(None, pln, pcol, ln, col, False)

    return True


def _unparenthesize_tuple(self: 'FST') -> bool:
    """Unparenthesize a parenthesized tuple, adjusting tuple location for removed parentheses. Will not
    unparenthesize an empty tuple. Removes everything between the parentheses and the actual tuple.

    WARNING! No checks are done so don't call on anything other than a parenthesized Tuple!

    **Returns:**
    - `bool`: Whether parentheses were removed or not (they may not be for an empty tuple).
    """

    # assert isinstance(self.a, Tuple)

    if not (elts := self.a.elts):
        return False

    ln, col, end_ln, end_col = self.loc
    lines                    = self.root._lines

    if comma := _next_find(self.root._lines, en_end_ln := (en := elts[-1].f).end_ln, en_end_col := en.end_col,
                           end_ln, end_col, ','):  # need to leave trailing comma if its there
        en_end_ln, en_end_col  = comma
        en_end_col            += 1

    else:  # when no trailing comma need to make sure par is not separating us from an alphanumeric on either side, and if so then insert a space at the end before deleting the right par
        if end_col >= 2 and _re_par_close_alnums.match(lines[end_ln], end_col - 2):
            self.put_src(' ', end_ln, end_col, end_ln, end_col, False, self)

    head_alnums = col and _re_par_open_alnums.match(lines[ln], col - 1)  # if open has alnumns on both sides then insert space there too

    self.put_src(None, en_end_ln, en_end_col, end_ln, end_col, True, self)
    self.put_src(None, ln, col, (e0 := elts[0].f).ln, e0.col, False)

    if head_alnums:  # but put after delete par to keep locations same
        self.put_src(' ', ln, col, ln, col, False)

    return True


def _normalize_block(self: 'FST', field: str = 'body', *, indent: str | None = None):
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

    b0                  = block[0].f
    b0_ln, b0_col, _, _ = b0.bloc
    root                = self.root

    if not (colon := _prev_find(root._lines, *b0._prev_bound(), b0_ln, b0_col, ':', True, comment=True, lcont=None)):  # must be there
        return

    if indent is None:
        indent = b0.get_indent()

    ln, col = colon

    self.put_src(['', indent], ln, col + 1, b0_ln, b0_col, False)


def _elif_to_else_if(self: 'FST'):
    """Convert an 'elif something:\\n  ...' to 'else:\\n  if something:\\n    ...'. Make sure to only call on an
    actual `elif`, meaning the lone `If` statement in the parent's `orelse` block which is an actual `elif` and not
    an `if`."""

    indent = self.get_indent()

    self.indent_lns(skip=0)

    if not self.next():  # last child?
        self._set_end_pos((a := self.a).end_lineno, a.end_col_offset, False)

    ln, col, _, _ = self.loc

    self.put_src(['if'], ln, col, ln, col + 4, False)
    self.put_src([indent + 'else:', indent + self.root.indent], ln, 0, ln, col, False)


def _reparse_docstrings(self: 'FST', docstr: bool | Literal['strict'] | None = None):
    """Reparse docstrings in `self` and all descendants.

    **Parameters:**
    - `docstr`: Which strings to reparse. `True` means all `Expr` multiline strings. `'strict'` means only multiline
        strings in expected docstring. `False` doesn't reparse anything and just returns. `None` means use default
        (`True`).
    """

    if docstr is None:
        docstr = self.get_option('docstr')
    if not docstr:
        return

    if docstr != 'strict':  # True
        for a in walk(self.a):
            if isinstance(a, Expr) and isinstance(v := a.value, Constant) and isinstance(v.value, str):
                v.value = literal_eval((f := a.f).get_src(*f.loc))

    else:
        for a in walk(self.a):
            if isinstance(a, HAS_DOCSTRING):
                if ((body := a.body) and isinstance(b0 := body[0], Expr) and isinstance(v := b0.value, Constant) and
                    isinstance(v.value, str)
                ):
                    v.value = literal_eval((f := b0.f).get_src(*f.loc))


def _make_fst_and_dedent(self: 'FST', indent: Union['FST', str], ast: AST, copy_loc: fstloc,
                         prefix: str = '', suffix: str = '',
                         put_loc: fstloc | None = None, put_lines: list[str] | None = None, *,
                         docstr: bool | Literal['strict'] | None = None) -> 'FST':
    if not isinstance(indent, str):
        indent = indent.get_indent()

    lines = self.root._lines
    fst   = FST(ast, lines, from_=self, lcopy=False)  # we use original lines for nodes offset calc before putting new lines

    fst.offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix.encode()) - lines[copy_loc.ln].c2b(copy_loc.col))

    fst._lines = fst_lines = self.get_src(*copy_loc, True)

    if suffix:
        fst_lines[-1] = bistr(fst_lines[-1] + suffix)

    if prefix:
        fst_lines[0] = bistr(prefix + fst_lines[0])

    if indent:
        fst.dedent_lns(indent, skip=bool(copy_loc.col), docstr=docstr)  # if copy location starts at column 0 then we apply dedent to it as well (preceding comment or something)

    if put_loc:
        self.put_src(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0

    return fst


def _modifying(self: 'FST', field: str | Literal[False] = False) -> Callable[[Optional['FST']], None]:
    """Call before modifying `FST` node (even just source) to mark possible data for updates after modification. This
    function just collects information so is safe to call without ever calling the return value.

    **Parameters:**
    - `self`: Parent of or actual node being modified, depending on value of `field` (because actual child may be being
        created and may not exist yet).
    - `field`: Name of field being modified or `False` to indicate that `self` is the child, in which case the parent
        and field will be gotten from `self`.

    **Returns:**
    - `Callable` Should be called after successful modification. If no modification done or error occurred then does not
        need to be called, nothing bad happens.
    """

    # TODO: update f/t-string f"{val=}" preceding string constants for updated value with '=', evil thing

    if field is False:
        field = self.pfield

        if not (self := self.parent):
            return lambda new_self=None: None

        field = field.name

    if not isinstance(self.a, expr):
        return lambda new_self=None: None

    def modified(new_self: Optional['FST'] | Literal[False] = False):
        """Call after modifying `FST` node to apply any needed changes to parents.

        Currently only updates `TemplateStr.str` but is meant to evetually update `JoinedStr`/`TemplateStr` `f'{v=}'`
        style self-documenting string `Constants`.

        **Parameters:**
        - `new_self`: Parent node of modified field AFTER modification (may have changed or not exist anymore). Or can
            be special value `False` to indicate that `self` was definitely not changed, this is just a convenience.
        """

        if new_self is False:
            new_self = self
        elif new_self is not self:  # if parent of field changed then entire statement was reparsed and we have nothing to do
            return

        field_ = field

        while isinstance(a := new_self.a, expr):
            if field_ == 'value' and isinstance(a, Interpolation):
                ln, col, _, _         = new_self.loc
                _, _, end_ln, end_col = a.value.f.pars()
                a.str                 = new_self.get_src(ln, col + 1, end_ln, end_col)

            field_ = new_self.pfield

            if not (new_self := new_self.parent):
                break

            field_ = field_.name

    return modified


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
