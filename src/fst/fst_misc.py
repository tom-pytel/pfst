"""Misc lower level FST methods."""

from __future__ import annotations

import re
import sys
from ast import *
from math import log10
from typing import Callable, Literal

from .astutil import *
from .astutil import Interpolation, TemplateStr

from .misc import (
    Self, astfield, fstloc, nspace,
    EXPRISH, STMTISH, BLOCK, HAS_DOCSTRING,
    re_empty_line_start, re_line_end_cont_or_comment,
    _next_src, _prev_src, _next_find, _prev_find, _next_pars, _prev_pars, _next_find_re,
    _params_offset, _multiline_str_continuation_lns, _multiline_fstr_continuation_lns,
)

_PY_VERSION           = sys.version_info[:2]
_HAS_FSTR_COMMENT_BUG = f'{"a#b"=}' != '"a#b"=\'a#b\''

_astfieldctx = astfield('ctx')

_re_fval_expr_equals   = re.compile(r'(?:\s*(?:#.*|\\)\n)*\s*=\s*(?:(?:#.*|\\)\n\s*)*')  # format string expression tail '=' indicating self-documentation

_re_par_open_alnums    = re.compile(r'\w[(]\w')
_re_par_close_alnums   = re.compile(r'\w[)]\w')
_re_delim_open_alnums  = re.compile(r'\w[([]\w')
_re_delim_close_alnums = re.compile(r'\w[)\]]\w')


def _make_tree_fst(ast: AST, parent: FST, pfield: astfield) -> FST:
    """Make `FST` node from `AST`, recreating possibly non-unique AST nodes."""

    if not getattr(ast, 'f', None):  # if `.f` exists then this has already been done
        if isinstance(ast, (expr_context, unaryop, operator, boolop, cmpop)):  # ast.parse() reuses simple objects, we need all objects to be unique
            pfield.set(parent.a, ast := ast.__class__())

    return FST(ast, parent, pfield)


def _out_lines(fst: FST, linefunc: Callable, ln: int, col: int, end_ln: int, end_col: int, eol: str = ''):
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

if _PY_VERSION >= (3, 12):
    class _Modifying:
        root:  FST          # for updating _serial
        fst:   FST | False  # False indicates nothing to update on done()
        field: astfield
        data:  list

        def __init__(self, fst: FST, field: str | Literal[False] = False, raw: bool = False):
            """Call before modifying `FST` node (even just source) to mark possible data for updates after modification.
            This function just collects information when it enters so is safe to call without ever explicitly exiting.
            Though it should be called on a successful modification because it increments the modification cound
            `_serial`. Can be used as a context manager or can just call `.enter()` and `.done()` manually.

            It is assumed that neither the `fst` node passed in or its parents will not be changed, otherwise this must
            be used manually and not as a context manager and the changed node must be passed into the `.done()` method
            on success. In this case currently no parents are updated as it is assumed the changes are due to raw
            reparse which goes up to the statement level and would thus include any modifications this class would make.

            **Parameters:**
            - `fst`: Parent of or actual node being modified, depending on value of `field` (because actual child may be
                being created and may not exist yet).
            - `field`: Name of field being modified or `False` to indicate that `self` is the child, in which case the
                parent and field will be gotten from `self`.
            - `raw`: Whether this is going to be a raw modification or not.
            """

            self.root = fst.root

            if raw:
                self.fst = False

                return

            if field is False:
                pfield = fst.pfield

                if fst := fst.parent:
                    field = pfield.name

            self.fst = fst if fst and isinstance(fst.a, expr) else False

            if self.fst:
                self.field = field
                self.data  = data = []  # [(FormattedValue or Interpolation FST, len(dbg_str) or None, bool do val_str), ...]

                while isinstance(fst.a, EXPRISH):
                    parent = fst.parent
                    pfield = fst.pfield

                    if field == 'value' and (strs := fst._get_fmtval_interp_strs()):  # this will never proc for py < 3.12
                        dbg_str, val_str, end_ln, end_col = strs

                        if (dbg_str is None or not parent or not (idx := pfield.idx) or
                            not isinstance(prev := parent.a.values[idx - 1], Constant) or
                            not isinstance(v := prev.value, str) or not v.endswith(dbg_str) or
                            (prevf := prev.f).end_col != end_col or prevf.end_ln != end_ln
                        ):
                            if val_str is not None:
                                data.append((fst, None, True))
                            elif not data:  # first one always gets put because needs to do other stuff
                                data.append((fst, None, False))

                        else:
                            data.append((fst, len(dbg_str), bool(val_str)))

                    if not parent:
                        break

                    field = pfield.name
                    fst   = parent

        def __enter__(self):
            return self.enter()

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                self.done()

        def enter(self):
            return self

        def done(self, fst: FST | None | Literal[False] = False):
            """Call after modifying `FST` node to apply any needed changes to parents.

            **Parameters:**
            - `fst`: Parent node of modified field AFTER modification (may have changed or not exist anymore). Or can be
                special value `False` to indicate that original `fst` was definitely not replaced, with replaced
                referring to the actual `FST` node that might be replaced in a raw reparse, not whether the content
                itself was modified. This is meant for special case use outside of the context manager.
            """

            self.root._serial += 1

            if fst is False:
                if not (fst := self.fst):
                    return

            elif fst is not self.fst:  # if parent of field changed then entire statement was reparsed and we have nothing to do
                return


            # TODO: 'for in' check


            if data := self.data:
                first = data[0]

                for strs in data:
                    fst, len_old_dbg_str, do_val_str  = strs

                    if strs is first:  # on first one check to make sure no double '{{', and if so then fix: f'{{a}}' -> f'{ {a}}'
                        ln, col, _, _ = fst.a.value.f.loc
                        fix_const     = ((parent := fst.parent) and (idx := fst.pfield.idx) and   # parent should exist here but just in case, whether we need to reset start of debug string or not
                            (f := parent.a.values[idx - 1].f).col == col and f.ln == ln)

                        if fst.root._lines[ln].startswith('{', col):
                            fst._put_src([' '], ln, col, ln, col, False)

                            if fix_const:
                                f.a.col_offset -= 1

                    dbg_str, val_str, end_ln, end_col = fst._get_fmtval_interp_strs()

                    if do_val_str:
                        fst.a.str = val_str

                    if len_old_dbg_str is not None:
                        lines            = fst.root._lines
                        c                = fst.parent.a.values[fst.pfield.idx - 1]
                        c.value          = c.value[:-len_old_dbg_str] + dbg_str
                        c.end_lineno     = end_ln + 1
                        c.end_col_offset = lines[end_ln].c2b(end_col)

else: # override _Modifying if py too low
    class _Modifying:
        """Dummy because py < 3.12 doesn't have f-string location information."""

        def __init__(self, fst: FST, field: str | Literal[False] = False, raw: bool = False):
            self.root = fst.root

        def __enter__(self):
            return self.enter()

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                self.done()

        def enter(self):
            return self

        def done(self, fst: FST | None | Literal[False] = False):
            self.root._serial += 1


@staticmethod
def _new_empty_module(*, from_: FST | None = None) -> FST:
    return FST(Module(body=[], type_ignores=[]), [''], from_=from_)


@staticmethod
def _new_empty_tuple(*, from_: FST | None = None) -> FST:
    ast = Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, ['()'], from_=from_)


@staticmethod
def _new_empty_list(*, from_: FST | None = None) -> FST:
    ast = List(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, ['[]'], from_=from_)


@staticmethod
def _new_empty_dict(*, from_: FST | None = None) -> FST:
    ast = Dict(keys=[], values=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, ['{}'], from_=from_)


@staticmethod
def _new_empty_set(only_ast: bool = False, lineno: int = 1, col_offset: int = 0, *,
                   from_: FST | None = None) -> FST | AST:
    ast = Set(elts=[
        Starred(value=Tuple(elts=[], ctx=Load(), lineno=lineno, col_offset=col_offset+2,
                            end_lineno=lineno, end_col_offset=col_offset+4),
                ctx=Load(), lineno=lineno, col_offset=col_offset+1, end_lineno=lineno, end_col_offset=col_offset+4)
    ], lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return ast if only_ast else FST(ast, ['{*()}'], from_=from_)


@staticmethod
def _new_empty_set_curlies(only_ast: bool = False, lineno: int = 1, col_offset: int = 0, *,
                           from_: FST | None = None) -> FST | AST:
    ast = Set(elts=[], lineno=lineno, col_offset=col_offset, end_lineno=lineno,
            end_col_offset=col_offset + 2)

    return ast if only_ast else FST(ast, ['{}'], from_=from_)


def _repr_tail(self: FST) -> str:
    try:
        loc = self.loc
    except Exception:  # maybe in middle of operation changing locations and lines
        loc = '????'

    self._touchall(False, True, True)  # for debugging because we may have cached locs which would not have otherwise been cached during execution

    tail = ' ROOT' if self.is_root else ''

    return f'{tail} {loc[0]},{loc[1]}..{loc[2]},{loc[3]}' if loc else tail


def _dump(self: FST, st: nspace, cind: str = '', prefix: str = ''):
    ast  = self.a
    tail = self._repr_tail()
    sind = ' ' * st.indent

    if not st.src:  # nop
        pass

    elif isinstance(ast, (stmt, ExceptHandler, match_case)):  # src = 'stmt' or 'all'
        if loc := self.bloc:
            if isinstance(ast, BLOCK):
                _out_lines(self, st.linefunc, loc.ln, loc.col, *self._loc_block_header_end(), st.eol)
            else:
                _out_lines(self, st.linefunc, *loc, st.eol)

    elif (st.src == 'all' and not isinstance(ast, mod) and (not (parent := self.parent) or
                                                            not isinstance(parent.a, Expr))):
        if loc := self.loc:
            _out_lines(self, st.linefunc, *loc, st.eol)

    if not st.expand:
        if isinstance(ast, Name):
            st.linefunc(f'{cind}{prefix}Name {ast.id!r} {ast.ctx.__class__.__qualname__}{" -" * bool(tail)}{tail}'
                        f'{st.eol}')

            return

        if isinstance(ast, Constant):
            if ast.kind is None:
                st.linefunc(f'{cind}{prefix}Constant {ast.value!r}{" -" * bool(tail)}{tail}{st.eol}')
            else:
                st.linefunc(f'{cind}{prefix}Constant {ast.value!r} kind={ast.kind!r}{" -" * bool(tail)}{tail}{st.eol}')

            return

    st.linefunc(f'{cind}{prefix}{ast.__class__.__qualname__}{" -" * bool(tail)}{tail}{st.eol}')

    for name, child in iter_fields(ast):
        is_list = isinstance(child, list)

        if not st.expand:
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


def _make_fst_tree(self: FST, stack: list[FST] | None = None):
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


def _unmake_fst_tree(self: FST, stack: list[AST] | None = None):
    """Destroy a tree of FST child nodes by breaking links between AST and FST nodes. This mainly helps make sure
    destroyed FST nodes can't be reused in a way that might corrupt valid remaining trees."""

    if stack is None:
        stack = [self.a]

    while stack:  # make sure these bad ASTs can't hurt us anymore
        if a := stack.pop():  # could be `None`s in there
            a.f.a = a.f = None  # root, parent and pfield are still useful after node has been removed

            stack.extend(iter_child_nodes(a))


def _unmake_fst_parents(self: FST, self_: bool = False):
    """Walk up parent list unmaking each parent along the way. This does not unmake the entire parent tree, just the
    parents directly above this node (and including `self` if `self_` is `True). Meant for when you know the parents are
    just a direct succession like Expr -> Module."""

    if self_:
        self.a.f = self.a = None

    while self := self.parent:
        self.a.f = self.a = None


def _set_ast(self: FST, ast: AST, valid_fst: bool = False, unmake: bool = True) -> AST:
    """Set `.a` AST node for this `FST` node and `_make_fst_tree` for `self`, also set ast node in parent AST node.
    Optionally `_unmake_fst_tree()` for with old `.a` node first. Returns old `.a` node.

    **Parameters:**
    - `valid_fst`: Indicates that the `AST` node is a part of a valid `FST` tree already so that less processing needs
        to be done to integrate it into `self`.
    - `unmake`: Whether to unmake the FST tree being replaced or not. Should really always unmake.
    """

    old_ast = self.a

    if unmake:
        self._unmake_fst_tree()

        if f := getattr(ast, 'f', None):
            f.a = None

    self.a = ast
    ast.f  = self

    if not valid_fst:
        self._make_fst_tree()

    else:
        root = self.root

        for a in walk(ast):
            a.f.root = root

        for a in iter_child_nodes(ast):
            a.f.parent = self

    if parent := self.parent:
        self.pfield.set(parent.a, ast)

    self._touch()

    return old_ast


def _set_ctx(self: FST, ctx: type[expr_context]):
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


def _next_bound(self: FST, with_loc: bool | Literal['all', 'own'] = 'all') -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object within parent. If no siblings found after
    self then return end of parent. If no parent then return end of source."""

    if next := self.next(with_loc):
        return next.bloc[:2]
    elif parent := self.parent:
        return parent.bloc[2:]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound(self: FST, with_loc: bool | Literal['all', 'own'] = 'all') -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object within parent. If no siblings found before
    self then return start of parent. If no parent then return (0, 0)."""

    if prev := self.prev(with_loc):
        return prev.bloc[2:]
    elif parent := self.parent:
        return parent.bloc[:2]
    else:
        return 0, 0


def _next_bound_step(self: FST, with_loc: bool | Literal['all', 'own', 'allown'] = 'all') -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object using `step_fwd()`. This is safe to call
    for nodes that live inside nodes without their own locations if `with_loc='allown'`."""

    if next := self.step_fwd(with_loc, recurse_self=False):
        return next.bloc[:2]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound_step(self: FST, with_loc: bool | Literal['all', 'own', 'allown'] = 'all') -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object using `step_back()`. This is safe to call for
    nodes that live inside nodes without their own locations if `with_loc='allown'`."""

    if prev := self.step_back(with_loc, recurse_self=False):
        return prev.bloc[2:]

    return 0, 0


def _loc_block_header_end(self: FST, ret_bound: bool = False) -> fstloc | tuple[int, int] | None:
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


def _loc_operator(self: FST) -> fstloc | None:
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


def _loc_comprehension(self: FST) -> fstloc:
    """`comprehension` location from children. Called from `.loc`."""

    # assert isinstance(self.s, comprehension)

    ast   = self.a
    first = ast.target.f
    last  = ifs[-1].f if (ifs := ast.ifs) else ast.iter.f  # self.last_child(), could be .iter or last .ifs
    lines = self.root._lines

    if prev := self.step_back('allown', recurse_self=False):  # 'allown' so it doesn't recurse into calling `.loc`
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


def _loc_arguments(self: FST) -> fstloc | None:
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


def _loc_arguments_empty(self: FST) -> fstloc:
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


def _loc_lambda_args_entire(self: FST) -> fstloc:
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


def _loc_withitem(self: FST) -> fstloc:
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


def _loc_match_case(self: FST) -> fstloc:
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


def _loc_Call_pars(self: FST) -> fstloc:
    # assert isinstance(self.s, Call)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.func.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = _next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_Subscript_brackets(self: FST) -> fstloc:
    # assert isinstance(self.s, Subscript)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.value.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = _next_find(lines, ln, col, end_ln, end_col, '[')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_MatchClass_pars(self: FST) -> fstloc:
    # assert isinstance(self.s, MatchClass)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.cls.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = _next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_Global_Nonlocal_names(self: FST, first: int, last: int | None = None) -> fstloc | tuple[fstloc, fstloc]:
    """We assume `first` and optionally `last` are in [0..len(names)), no negative or out-of-bounds and `last` follows
    or equals `first` if present."""

    # assert isinstance(self.a, (Global, Nonlocal))

    ln, col, end_ln, end_col = self.loc

    col   += 6 if isinstance(self.a, Global) else 8
    lines  = self.root._lines
    idx    = first

    while idx:  # skip the commas
        ln, col  = _next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col     += 1
        idx     -= 1

    ln, col, src = _next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there
    first_loc    = fstloc(ln, col, ln, col := col + len(src))

    if last is None:
        return first_loc

    if not (idx := last - first):
        return first_loc, first_loc

    while idx:
        ln, col  = _next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col     += 1
        idx     -= 1

    ln, col, src = _next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there

    return first_loc, fstloc(ln, col, ln, col + len(src))


def _is_arguments_empty(self: FST) -> bool:
    """Is this `arguments` node empty?"""

    # assert isinstance(self.a, arguments)

    return not ((a := self.a).posonlyargs or a.args or a.vararg or a.kwonlyargs or a.kwarg)


def _is_parenthesized_ImportFrom_names(self: FST) -> bool:
    # assert isinstance(self.a, ImportFrom)

    ln, col, _, _         = self.loc
    end_ln, end_col, _, _ = self.a.names[0].f.loc

    return _prev_src(self.root._lines, ln, col, end_ln, end_col).src.endswith('(')  # something is there for sure


def _is_parenthesized_With_items(self: FST) -> bool:
    # assert isinstance(self.a, (With, AsyncWith))

    ln, col, _, _         = self.loc
    end_ln, end_col, _, _ = self.a.items[0].f.loc  # will include any pars in child so don't need to depar

    return _prev_src(self.root._lines, ln, col, end_ln, end_col).src.endswith('(')  # something is there for sure


def _is_parenthesized_seq(self: FST, field: str = 'elts', lpar: str = '(', rpar: str = ')') -> bool:
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


def _dict_key_or_mock_loc(self: FST, key: AST | None, value: FST) -> FST | fstloc:
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


def _set_end_pos(self: FST, end_lineno: int, end_col_offset: int, self_: bool = True):  # because of trailing non-AST junk in last statements
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


def _set_block_end_from_last_child(self: FST, bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int):
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


def _maybe_add_comma(self: FST, ln: int, col: int, offset: bool, space: bool,
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
        root._offset(ln, col, 0, len(comma), True, exclude=self)

    elif ln == end_ln:
        self.a.end_col_offset += len(comma)

        self._touchall(True)

    return True


def _maybe_add_singleton_tuple_comma(self: FST, offset: bool = True):
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


def _maybe_fix_tuple(self: FST, is_parenthesized: bool | None = None):
    # assert isinstance(self.a, Tuple)

    ast = self.a

    if is_parenthesized is None:
        is_parenthesized = self._is_parenthesized_seq()

    if elts := ast.elts:
        self._maybe_add_singleton_tuple_comma(True)

        lines                    = self.root._lines
        ln, col, end_ln, end_col = self.loc

        if not is_parenthesized:
            encpar = None

            if ((end_ln != ln and not self.is_enclosed(pars=False) and not (encpar := self.is_enclosed_in_parents())) or  # could have line continuations
                (any(isinstance(e, NamedExpr) and not e.f.pars().n for e in elts))  # yeah, this is fine in parenthesized tuples but not in naked ones
            ):
                self._parenthesize_node()

            else:
                eln, ecol, _, _ = elts[0].f.pars()

                if ecol != col or eln != ln:  # to be super safe we enforce that an unparenthesized tuple must start at the first element
                    self._put_src(None, ln, col, eln, ecol, False)

                    ln, col, end_ln, end_col = self.loc

                _, _, eend_ln, eend_col = elts[-1].f.pars()

                if comma := _next_find(lines, eend_ln, eend_col, end_ln, end_col, ','):  # could be closing grouping pars before comma
                    eend_ln, eend_col  = comma
                    eend_col          += 1

                if end_col != eend_col or end_ln != eend_ln:  # need to update end position because it had some whitespace after which will not be enclosed by parentheses
                    # self._put_src(None, eend_ln, eend_col, end_ln, end_col, True)  # be safe, nuke everything after last element since we won't have parentheses or parent to delimit it

                    if not (encpar or self.is_enclosed_in_parents()):
                        self._put_src(None, eend_ln, eend_col, end_ln, end_col, True)  # be safe, nuke everything after last element since we won't have parentheses or parent to delimit it

                    else:  # enclosed in parents so we can leave crap at the end
                        a                  = self.a
                        cur_end_lineno     = a.end_lineno
                        cur_end_col_offset = a.end_col_offset
                        end_lineno         = a.end_lineno     = eend_ln + 1
                        end_col_offset     = a.end_col_offset = lines[eend_ln].c2b(eend_col)

                        self._touch()

                        while ((self := self.parent) and getattr(a := self.a, 'end_col_offset', -1) == cur_end_col_offset and  # update parents, only as long as they end exactly where we end
                            a.end_lineno == cur_end_lineno
                        ):
                            a.end_lineno     = end_lineno
                            a.end_col_offset = end_col_offset

                            self._touch()

                        else:
                            if self:
                                self._touchall(True)

    elif not is_parenthesized:  # if is unparenthesized tuple and empty left then need to add parentheses
        ln, col, end_ln, end_col = self.loc

        self._put_src(['()'], ln, col, end_ln, end_col, True, False)  # WARNING! `tail=True` may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized tuple starts, but haven't found a case where this can happen


def _maybe_fix_set(self: FST):
    # assert isinstance(self.a, Set)

    if not self.a.elts:
        ln, col, end_ln, end_col = self.loc

        self._put_src(['{*()}'], ln, col, end_ln, end_col, True)
        self._set_ast(self._new_empty_set(True, (a := self.a).lineno, a.col_offset))


def _maybe_fix_elif(self: FST):
    # assert isinstance(self.a, If)

    ln, col, _, _ = self.loc
    lines         = self.root._lines

    if lines[ln].startswith('elif', col):
        self._put_src(None, ln, col, ln, col + 2, False)


def _maybe_fix_with_items(self: FST):
    """If `Tuple` only element in `items` then add appropriate parentheses."""

    # assert isinstance(self.a, (With, AsyncWith))

    if (len(items := self.items) == 1 and
        not (i0a := items[0].a).optional_vars and
        (is_par := (cef := i0a.context_expr.f).is_parenthesized_tuple()) is not None
    ):
        if not is_par:
            cef._parenthesize_node()

        if len(_prev_pars(self.root._lines, self.ln, self.col, cef.ln, cef.col)) == 1:  # no pars between start of `with` and start of tuple?
            cef._parenthesize_grouping()  # these will wind up belonging to outer With


def _maybe_fix_copy(self: FST, pars: bool = True):
    """Maybe fix source and `ctx` values for cut or copied nodes (to make subtrees parsable if the source is not after
    the operation). If cannot fix or ast is not parsable by itself then ast will be unchanged. Is meant to be a quick
    fix after a cut or copy operation, not full check, for that use `verify()`.

    **WARNING!** Only call on root node!
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
            elif any(isinstance(e, NamedExpr) and not e.f.pars().n for e in ast.elts):  # unparenthesized walrus in naked tuple?
                need_paren = True

            self._maybe_add_singleton_tuple_comma(False)  # this exists because of copy lone Starred out of a Subscript.slice

        elif isinstance(ast, NamedExpr):  # naked walrus
            need_paren = True

        if need_paren is None:
            need_paren = not self.is_enclosed()

        if need_paren:
            if is_tuple:
                self._parenthesize_node()
            else:
                self._parenthesize_grouping()


def _touch(self: FST) -> Self:
    """AST node was modified, clear out any cached info for this node only."""

    self._cache.clear()

    return self


def _sanitize(self: FST) -> Self:
    """Quick check to make sure that nodes which are not `stmt`, `ExceptHandler`, `match_case` or `mod` don't have any
    extra junk in the source and that the parenthesized location matches the whole location of the source. If not then
    fix by removing the junk."""

    if not self.is_root:
        raise ValueError('can only be called on root node')

    if not (loc := self.pars()) or loc == self.whole_loc:
        return self

    ln, col, end_ln, end_col = loc
    lines                    = self._lines

    self._offset(ln, col, -ln, -lines[ln].c2b(col))

    lines[end_ln] = bistr(lines[end_ln][:end_col])
    lines[ln]     = bistr(lines[ln][col:])

    del lines[end_ln + 1:], lines[:ln]

    return self


def _parenthesize_grouping(self: FST, whole: bool = True, *, star_child: bool = True):
    """Parenthesize anything with non-node grouping parentheses. Just adds text parens around node adjusting parent
    locations but not the node itself.

    **Parameters:**
    - `whole`: If at root then parenthesize whole source instead of just node.
    - `star_child`: `Starred` expressions cannot be parenthesized, so when this is `True` the parentheses are applied to
        the `value` child and the opening par is put right after the `*` to resolve any enclosure issues. This overrides
        `whole` for the opening par.
    """

    ln, col, end_ln, end_col = self.whole_loc if whole and self.is_root else self.loc

    if isinstance(self.a, Starred) and star_child:
        ln, col, _, _  = self.loc
        col           += 1
        self           = self.a.value.f

    self._put_src([')'], end_ln, end_col, end_ln, end_col, True, True, self, offset_excluded=False)
    self._offset(*self._put_src(['('], ln, col, ln, col, False, False, self, offset_excluded=False))


def _parenthesize_node(self: FST, whole: bool = True, pars: str = '()'):
    """Parenthesize (delimit) a node (`Tuple` or `MatchSequence`, but could be others) with appropriate delimiters which
    are passed in and extend the range of the node to include those delimiters.

    **WARNING!** No checks are done so make sure to call where it is appropriate!

    **Parameters:**
    - `whole`: If at root then parenthesize whole source instead of just node.
    """

    # assert isinstance(self.a, Tuple)

    ln, col, end_ln, end_col = self.whole_loc if whole and self.is_root else self.loc

    self._put_src([pars[1]], end_ln, end_col, end_ln, end_col, True, False, self)

    lines            = self.root._lines
    a                = self.a
    a.end_lineno     = end_ln + 1  # yes this can change
    a.end_col_offset = lines[end_ln].c2b(end_col + 1)  # can't count on this being set by put_src() because end of `whole` could be past end of tuple

    self._offset(*self._put_src([pars[0]], ln, col, ln, col, False, False, self), self_=False)

    a.lineno     = ln + 1
    a.col_offset = lines[ln].c2b(col)  # ditto on the `whole` thing


def _unparenthesize_grouping(self: FST, shared: bool | None = True, *, star_child: bool = True) -> bool:
    """Remove grouping parentheses from anything if present. Just remove text parens around node and everything between
    them and node adjusting parent locations but not the node itself.

    **Parameters:**
    - `shared`: Whether to allow merge of parentheses into shared single call argument generator expression or not. If
        `None` then will attempt to unparenthesize any enclosing parentheses, whether they belong to this node or not
        (meant for internal use).
    - `star_child`: `Starred` expressions cannot be parenthesized, so when this is `True` the parentheses are removed
        from the `value` child.

    **Returns:**
    - `bool`: Whether parentheses were removed or not (only removed if present to begin with and removable).
    """

    if isinstance(self.a, Starred) and star_child:
        self = self.value

    pars_loc = self.pars(None if shared is None else True)

    if shared:
        shared = self.is_solo_call_arg_genexp()

    if not getattr(pars_loc, 'n', 0) and not shared:
        return False

    ln , col,  end_ln,  end_col  = self.bloc
    pln, pcol, pend_ln, pend_col = pars_loc

    if shared:  # special case merge solo argument GeneratorExp parentheses with call argument parens
        lines                    = self.root._lines
        _, _, cend_ln, cend_col  = self.parent.func.loc
        pln, pcol                = _prev_find(lines, cend_ln, cend_col, pln, pcol, '(')  # it must be there
        pend_ln, pend_col        = _next_find(lines, pend_ln, pend_col, len(lines) - 1, len(lines[-1]), ')')  # ditto
        pend_col                += 1

        self._put_src(None, end_ln, end_col, pend_ln, pend_col, True, self)
        self._put_src(None, pln, pcol, ln, col, False)

    else:  # in all other case we need to make sure par is not separating us from an alphanumeric on either side, and if so then just replace that par with a space
        lines = self.root._lines

        if pend_col >= 2 and _re_par_close_alnums.match(l := lines[pend_ln], pend_col - 2):
            lines[pend_ln] = bistr(l[:pend_col - 1] + ' ' + l[pend_col:])
        else:
            self._put_src(None, end_ln, end_col, pend_ln, pend_col, True, self)

        if pcol and _re_par_open_alnums.match(l := lines[pln], pcol - 1):
            lines[pln] = bistr(l[:pcol] + ' ' + l[pcol + 1:])
        else:
            self._put_src(None, pln, pcol, ln, col, False)

    return True


def _unparenthesize_node(self: FST, field: str = 'elts') -> bool:
    """Unparenthesize a parenthesized `Tuple` or `MatchSequence` or unbracketize the latter if is that, shrinking node
    location for the removed delimiters. Will not unparenthesize an empty `Tuple` or `MatchSequence`. Removes everything
    between the parentheses and the actual tuple, e.g. `(  1, 2  # yay \\n)` -> `1, 2`.

    **WARNING!** No checks are done so make sure to call where it is appropriate! Does not check to see if node is
    properly paren/bracketized so make sure of this before calling!

    **Returns:**
    - `bool`: Whether parentheses (or brackets) were removed or not (they may not be for an empty tuple).
    """

    # assert isinstance(self.a, Tuple)

    if not (elts := getattr(self.a, field, None)):
        return False

    ln, col, end_ln, end_col = self.loc
    lines                    = self.root._lines

    if comma := _next_find(self.root._lines, en_end_ln := (en := elts[-1].f).end_ln, en_end_col := en.end_col,
                           end_ln, end_col, ','):  # need to leave trailing comma if its there
        en_end_ln, en_end_col  = comma
        en_end_col            += 1

    else:  # when no trailing comma need to make sure par is not separating us from an alphanumeric on either side, and if so then insert a space at the end before deleting the right par
        if end_col >= 2 and _re_delim_close_alnums.match(lines[end_ln], end_col - 2):
            self._put_src(' ', end_ln, end_col, end_ln, end_col, False, self)

    head_alnums = col and _re_delim_open_alnums.match(lines[ln], col - 1)  # if open has alnumns on both sides then insert space there too

    self._put_src(None, en_end_ln, en_end_col, end_ln, end_col, True, self)
    self._put_src(None, ln, col, (e0 := elts[0].f).ln, e0.col, False)

    if head_alnums:  # but put after delete par to keep locations same
        self._put_src(' ', ln, col, ln, col, False)

    return True


def _normalize_block(self: FST, field: str = 'body', *, indent: str | None = None):
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

    self._put_src(['', indent], ln, col + 1, b0_ln, b0_col, False)


def _elif_to_else_if(self: FST):
    """Convert an 'elif something:\\n  ...' to 'else:\\n  if something:\\n    ...'. Make sure to only call on an
    actual `elif`, meaning the lone `If` statement in the parent's `orelse` block which is an actual `elif` and not
    an `if`."""

    indent = self.get_indent()

    self._indent_lns(skip=0)

    if not self.next():  # last child?
        self._set_end_pos((a := self.a).end_lineno, a.end_col_offset, False)

    ln, col, _, _ = self.loc

    self._put_src(['if'], ln, col, ln, col + 4, False)
    self._put_src([indent + 'else:', indent + self.root.indent], ln, 0, ln, col, False)


def _reparse_docstrings(self: FST, docstr: bool | Literal['strict'] | None = None):
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


def _make_fst_and_dedent(self: FST, indent: FST | str, ast: AST, copy_loc: fstloc,
                         prefix: str = '', suffix: str = '',
                         put_loc: fstloc | None = None, put_lines: list[str] | None = None, *,
                         docstr: bool | Literal['strict'] | None = None) -> FST:
    if not isinstance(indent, str):
        indent = indent.get_indent()

    lines = self.root._lines
    fst   = FST(ast, lines, from_=self, lcopy=False)  # we use original lines for nodes offset calc before putting new lines

    fst._offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix.encode()) - lines[copy_loc.ln].c2b(copy_loc.col))

    fst._lines = fst_lines = self.get_src(*copy_loc, True)

    if suffix:
        fst_lines[-1] = bistr(fst_lines[-1] + suffix)

    if prefix:
        fst_lines[0] = bistr(prefix + fst_lines[0])

    if indent:
        fst._dedent_lns(indent, skip=bool(copy_loc.col), docstr=docstr)  # if copy location starts at column 0 then we apply dedent to it as well (preceding comment or something)

    if put_loc:
        self._put_src(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0

    return fst


def _get_fmtval_interp_strs(self: FST) -> tuple[str | None, str | None, int, int] | None:
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

    if not (get_val := isinstance(ast, Interpolation)):
        if not isinstance(ast, FormattedValue):
            return None

    lines                        = self.root._lines
    sln, scol, send_ln, send_col = self.loc
    _, _, vend_ln, vend_col      = ast.value.f.pars()

    if fspec := ast.format_spec:
        end_ln, end_col, _, _ = fspec.f.loc
    else:
        end_ln  = send_ln
        end_col = send_col - 1

    if ast.conversion != -1:
        if prev := _prev_find(lines, vend_ln, vend_col, end_ln, end_col, '!'):
            end_ln, end_col = prev

    src     = self.get_src(vend_ln, vend_col, end_ln, end_col)  # source from end of parenthesized value to end of FormattedValue or start of conversion or format_spec
    get_dbg = src and (m := _re_fval_expr_equals.match(src)) and m.end() == len(src)

    if not get_dbg and not get_val:
        return None, None, 0, 0

    if _HAS_FSTR_COMMENT_BUG:  # '#' characters inside strings erroneously removed as if they were comments
        lines = self.get_src(sln, scol + 1, end_ln, end_col, True)

        for i, l in enumerate(lines):
            if (m := re_line_end_cont_or_comment.match(l)) and (g := m.group(1)) and g.startswith('#'):  # line ends in comment, nuke it
                lines[i] = l[:m.start(1)]

    else:
        lns  = set()
        ends = {}  # the starting column of where to search for comment '#', past end of any expression on given line

        for f in (walking := ast.value.f.walk(True)):  # find multiline continuation line numbers
            fln, _, fend_ln, fend_col = f.loc
            ends[fend_ln]             = max(fend_col, ends.get(fend_ln, 0))

            if fend_ln == fln:  # everything on one line, don't need to recurse
                walking.send(False)

            elif isinstance(a := f.a, Constant):  # isinstance(f.a.value, (str, bytes)) is a given if bend_ln != bln
                lns.update(_multiline_str_continuation_lns(lines, *f.loc))

            elif isinstance(a, (JoinedStr, TemplateStr)):
                lns.update(_multiline_fstr_continuation_lns(lines, *f.loc))

                walking.send(False)  # skip everything inside regardless, because it is evil

                for a in walk(f.a):  # we walk ourselves to get end-of-expression locations for lines
                    if loc := a.f.loc:
                        _, _, fend_ln, fend_col = loc
                        ends[fend_ln]           = max(fend_col, ends.get(fend_ln, 0))

        off   = sln + 1
        lns   = {v - off for v in lns}  # these are line numbers where comments are not possible because next line is a string continuation
        lines = self.get_src(sln, scol + 1, end_ln, end_col, True)

        for i, l in enumerate(lines):
            if i not in lns:
                c = ends.get(i + sln, 0)

                if not i:  # if first line then need to remove offset of first value from first line of expression
                    c -= scol + 1

                if (m := re_line_end_cont_or_comment.match(l, c)) and (g := m.group(1)) and g.startswith('#'):  # line ends in comment, nuke it
                    lines[i] = l[:m.start(1)]

        print()

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

if _PY_VERSION < (3, 12):  # override _get_fmtval_interp_strs if py too low
    def _get_fmtval_interp_strs(self: FST) -> tuple[str, str, int, int] | None:
        """Dummy because py < 3.12 doesn't have f-string location information."""

        return None


def _get_indentable_lns(self, skip: int = 0, *, docstr: bool | Literal['strict'] | None = None) -> set[int]:
    r"""Get set of indentable lines within this node.

    **Parameters:**
    - `skip`: The number of lines to skip from the start of this node. Useful for skipping the first line for edit
        operations (since the first line is normally joined to an existing line on add or copied directly from start
        on cut).
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in expected docstring positions are indentable. `None` means use default.

    **Returns:**
    - `set[int]`: Set of line numbers (zero based) which are sytactically indentable.

    **Examples:**
    ```py
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
    ```
    """

    if docstr is None:
        docstr = self.get_option('docstr')

    strict = docstr == 'strict'
    lines  = self.root._lines
    lns    = set(range(skip, len(lines))) if self.is_root else set(range(self.bln + skip, self.bend_ln + 1))

    while (parent := self.parent) and not isinstance(self.a, STMTISH):
        self = parent

    for f in (walking := self.walk(False)):  # find multiline strings and exclude their unindentable lines
        if f.bend_ln == f.bln:  # everything on one line, don't need to recurse
            walking.send(False)

        elif isinstance(a := f.a, Constant):
            if (  # isinstance(f.a.value, (str, bytes)) is a given if bend_ln != bln
                not docstr or
                not ((parent := f.parent) and isinstance(parent.a, Expr) and
                        (not strict or ((pparent := parent.parent) and parent.pfield == ('body', 0) and
                                        isinstance(pparent.a, HAS_DOCSTRING)
            )))):
                lns.difference_update(_multiline_str_continuation_lns(lines, *f.loc))

        elif isinstance(a, (JoinedStr, TemplateStr)):
            lns.difference_update(_multiline_fstr_continuation_lns(lines, *f.loc))

            walking.send(False)  # skip everything inside regardless, because it is evil

    return lns


def _modifying(self: FST, field: str | Literal[False] = False, raw: bool = False) -> _Modifying:
    """Call before modifying `FST` node (even just source) to mark possible data for updates after modification. This
    function just collects information so is safe to call without ever calling `.done()` method of the return value in
    case of failure, though it should be called on success. In fact, this method is not called if the return is used as
    a context manager and is exited with an exception.

    **Parameters:**
    - `self`: Parent of or actual node being modified, depending on value of `field` (because actual child may be being
        created and may not exist yet).
    - `field`: Name of field being modified or `False` to indicate that `self` is the child, in which case the parent
        and field will be gotten from `self`.
    - `raw`: Whether this is going to be a raw modification or not.

    **Returns:**
    - `_Modifying`: Can be used as a context manager or `.enter()`ed manually, in which case `.done()` should be called
        on success, and nothing if no modification was performed.
    """

    return _Modifying(self, field, raw)


def _touchall(self: FST, parents: bool = False, self_: bool = True, children: bool = False) -> Self:
    """Touch self, parents and children, optionally. Flushes location cache so that changes to `AST` locations will
    get picked up."""

    if children:
        stack = [self.a] if self_ else list(iter_child_nodes(self.a))

        while stack:
            child = stack.pop()

            child.f._touch()
            stack.extend(iter_child_nodes(child))

    elif self_:
        self._touch()

    if parents:
        parent = self

        while parent := parent.parent:
            parent._touch()

    return self


def _put_src(self, src: str | list[str] | None, ln: int, col: int, end_ln: int, end_col: int,
             tail: bool | None = ..., head: bool | None = True, exclude: FST | None = None, *,
             offset_excluded: bool = True) -> tuple[int, int, int, int] | None:
    """Put or delete new source to currently stored source, optionally offsetting all nodes for the change. Must
    specify `tail` as `True`, `False` or `None` to enable offset of nodes according to source put. `...` ellipsis
    value is used as sentinel for `tail` to mean don't offset. Otherwise `tail` and params which followed are passed
    to `self._offset()` with calculated offset location and deltas.

    **Returns:**
    - `(ln: int, col: int, dln: int, dcol_offset: int) | None`: If `tail` was not `...` then the calculated
        `offset()` parameters are returned for any potential followup offsetting. The `col` parameter in this case
        is returned as a byte offset so that `offset()` doesn't attempt to calculate it from already modified
        source."""

    ret = None
    ls  = self.root._lines

    if is_del := src is None:
        lines = [bistr('')]
    elif isinstance(src, str):
        lines = [bistr(s) for s in src.split('\n')]
    elif not isinstance(src[0], bistr):  # lines is list[str]
        lines = [bistr(s) for s in src]
    else:
        lines = src

    if tail is not ...:  # possibly offset nodes
        ret = _params_offset(ls, lines, ln, col, end_ln, end_col)

        self.root._offset(*ret, tail, head, exclude, offset_excluded=offset_excluded)

    if is_del:  # delete lines
        if end_ln == ln:
            ls[ln] = bistr((l := ls[ln])[:col] + l[end_col:])

        else:
            ls[end_ln] = bistr(ls[ln][:col] + ls[end_ln][end_col:])

            del ls[ln : end_ln]

    else:  # put lines
        dln = end_ln - ln

        if (nnew_ln := len(lines)) <= 1:
            s = lines[0] if nnew_ln else ''

            if not dln:  # replace single line with single or no line
                ls[ln] = bistr(f'{(l := ls[ln])[:col]}{s}{l[end_col:]}')

            else:  # replace multiple lines with single or no line
                ls[ln] = bistr(f'{ls[ln][:col]}{s}{ls[end_ln][end_col:]}')

                del ls[ln + 1 : end_ln + 1]

        elif not dln:  # replace single line with multiple lines
            lend                 = bistr(lines[-1] + (l := ls[ln])[end_col:])
            ls[ln]               = bistr(l[:col] + lines[0])
            ls[ln + 1 : ln + 1]  = lines[1:]
            ls[ln + nnew_ln - 1] = lend

        else:  # replace multiple lines with multiple lines
            ls[ln]              = bistr(ls[ln][:col] + lines[0])
            ls[end_ln]          = bistr(lines[-1] + ls[end_ln][end_col:])
            ls[ln + 1 : end_ln] = lines[1:-1]

    return ret


def _offset(self: FST, ln: int, col: int, dln: int, dcol_offset: int,
            tail: bool | None = False, head: bool | None = True, exclude: FST | None = None, *,
            offset_excluded: bool = True, self_: bool = True,
            ) -> Self:
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

    if self_:
        stack = [self.a]
    elif self is exclude:
        return
    else:
        stack = list(iter_child_nodes(self.a))

    lno  = ln + 1
    colo = (-col if col <= 0 else  # yes, -0 to not look up 0
            (l := ls[ln]).c2b(min(col, len(l))) if ln < len(ls := self.root._lines) else 0x7fffffffffffffff)
    fwd  = dln > 0 or (not dln and dcol_offset >= 0)

    while stack:
        a = stack.pop()
        f = a.f

        if f is not exclude:
            children = iter_child_nodes(a)
        elif offset_excluded:
            children = ()
        else:
            continue

        f._touch()

        if (fend_colo := getattr(a, 'end_col_offset', None)) is not None:
            flno  = a.lineno
            fcolo = a.col_offset

            if (fend_lno := a.end_lineno) < lno:
                continue  # no need to walk into something which ends before offset point
            elif fend_lno > lno:
                a.end_lineno = fend_lno + dln
            elif fend_colo < colo:
                continue

            elif (fend_colo > colo or
                    (tail and (fwd or head is not False or fcolo != fend_colo or flno != fend_lno)) or  # at (ln, col), moving tail allowed and not blocked by head?
                    (tail is None and head and fwd and fcolo == fend_colo and flno == fend_lno)):  # allowed to be and being moved by head?
                a.end_lineno     = fend_lno + dln
                a.end_col_offset = fend_colo + dcol_offset

            if flno > lno:
                if not dln and (not (decos := getattr(a, 'decorator_list', None)) or decos[0].lineno > lno):
                    continue  # no need to walk into something past offset point if line change is 0, don't need to touch either could not have been changed above

                a.lineno = flno + dln

            elif (flno == lno and (fcolo > colo or (fcolo == colo and (
                    (head and (not fwd or tail is not False or fcolo != fend_colo or flno != fend_lno)) or  # at (ln, col), moving head allowed and not blocked by tail?
                    (head is None and tail and not fwd and fcolo == fend_colo and flno == fend_lno))))):  # allowed to be and being moved by tail?
                a.lineno     = flno + dln
                a.col_offset = fcolo + dcol_offset

        stack.extend(children)

    self._touchall(True, False)

    return self


def _offset_lns(self: FST, lns: set[int] | dict[int, int], dcol_offset: int | None = None):
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

        self._touchall(True, False)

    elif dcol_offset:  # lns is set[int] OR dict[int, int] (overriding with a single dcol_offset)
        for a in walk(self.a):
            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                if a.lineno - 1 in lns:
                    a.col_offset += dcol_offset

                if a.end_lineno - 1 in lns:
                    a.end_col_offset = end_col_offset + dcol_offset

            a.f._touch()

        self._touchall(True, False)


def _indent_lns(self: FST, indent: str | None = None, lns: set[int] | None = None, *,
                skip: int = 1, docstr: bool | Literal['strict'] | None = None) -> set[int]:
    """Indent all indentable lines specified in `lns` with `indent` and adjust node locations accordingly.

    **WARNING!** This does not offset parent nodes.

    **Parameters:**
    - `indent`: The indentation string to prefix to each indentable line.
    - `lns`: A `set` of lines to apply identation to. If `None` then will be gotten from
        `_get_indentable_lns(skip=skip)`.
    - `skip`: If not providing `lns` then this value is passed to `_get_indentable_lns()`.
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in expected docstring positions are indentable. `None` means use default.

    **Returns:**
    - `set[int]`: `lns` passed in or otherwise set of line numbers (zero based) which are sytactically indentable.
    """

    root = self.root

    if indent is None:
        indent = root.indent
    if docstr is None:
        docstr = self.get_option('docstr')

    if not ((lns := self._get_indentable_lns(skip, docstr=docstr)) if lns is None else lns) or not indent:
        return lns

    self._offset_lns(lns, len(indent.encode()))

    lines = root._lines

    for ln in lns:
        if l := lines[ln]:  # only indent non-empty lines
            lines[ln] = bistr(indent + l)

    self._reparse_docstrings(docstr)

    return lns


def _dedent_lns(self: FST, indent: str | None = None, lns: set[int] | None = None, *,
                skip: int = 1, docstr: bool | Literal['strict'] | None = None) -> set[int]:
    """Dedent all indentable lines specified in `lns` by removing `indent` prefix and adjust node locations
    accordingly. If cannot dedent entire amount, will dedent as much as possible.

    **WARNING!** This does not offset parent nodes.

    **Parameters:**
    - `indent`: The indentation string to remove from the beginning of each indentable line (if possible).
    - `lns`: A `set` of lines to apply dedentation to. If `None` then will be gotten from
        `_get_indentable_lns(skip=skip)`.
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in expected docstring positions are indentable. `None` means use default.
    - `skip`: If not providing `lns` then this value is passed to `_get_indentable_lns()`.

    **Returns:**
    - `set[int]`: `lns` passed in or otherwise set of line numbers (zero based) which are sytactically indentable.
    """

    root = self.root

    if indent is None:
        indent = root.indent
    if docstr is None:
        docstr = self.get_option('docstr')

    if not ((lns := self._get_indentable_lns(skip, docstr=docstr)) if lns is None else lns) or not indent:
        return lns

    lines        = root._lines
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
        self._offset_lns(dcol_offsets)
    else:
        self._offset_lns(lns, -lindent)

    self._reparse_docstrings(docstr)

    return lns


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]  # used by make_docs.py

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
