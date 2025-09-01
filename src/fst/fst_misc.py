"""Low level common data and functions that are aware of or meant to be used as part of the FST class.

This module contains functions which are imported as methods in the `FST` class.
"""

from __future__ import annotations

import re
from ast import literal_eval, iter_fields, iter_child_nodes, walk
from math import log10
from types import TracebackType
from typing import Callable, Literal

from . import fst

from .asttypes import (
    AST,
    AsyncFunctionDef,
    Attribute,
    Call,
    Compare,
    Constant,
    Dict,
    ExceptHandler,
    Expr,
    FormattedValue,
    FunctionDef,
    GeneratorExp,
    Global,
    If,
    IsNot,
    JoinedStr,
    Lambda,
    List,
    Load,
    MatchMapping,
    MatchOr,
    MatchSequence,
    Module,
    Name,
    NamedExpr,
    NotIn,
    Set,
    Slice,
    Starred,
    Subscript,
    Tuple,
    UnaryOp,
    arguments,
    boolop,
    cmpop,
    expr,
    expr_context,
    match_case,
    mod,
    operator,
    pattern,
    stmt,
    unaryop,
    TemplateStr,
    Interpolation,
)

from .astutil import bistr, re_alnumdot_alnum, re_identifier, OPCLS2STR, last_block_header_child

from .misc import (
    Self, NodeError, astfield, fstloc, fstlocns, srcwpos, nspace, pyver,
    EXPRISH, STMTISH, BLOCK, HAS_DOCSTRING,
    re_empty_line_start, re_line_trailing_space, re_line_end_cont_or_comment,
    next_frag, prev_frag, next_find, prev_find, next_delims, prev_delims, next_find_re,
    ParamsOffset, params_offset, multiline_str_continuation_lns, multiline_fstr_continuation_lns,
)

_HAS_FSTR_COMMENT_BUG  = f'{"a#b"=}' != '"a#b"=\'a#b\''

_astfieldctx           = astfield('ctx')

_re_one_space_or_end   = re.compile(r'\s|$')

_re_fval_expr_equals   = re.compile(r'(?:\s*(?:#.*|\\)\n)*\s*=\s*(?:(?:#.*|\\)\n\s*)*')  # format string expression tail '=' indicating self-documenting debug str

_re_par_open_alnums    = re.compile(r'\w[(]\w')
_re_par_close_alnums   = re.compile(r'\w[)]\w')
_re_delim_open_alnums  = re.compile(r'\w[([]\w')
_re_delim_close_alnums = re.compile(r'\w[)\]]\w')

_re_keyword_import     = re.compile(r'\bimport\b')


@pyver(ge=12)
class _Modifying:
    """Modification context manager. Updates some parent stuff after a successful modification."""

    root:  fst.FST                   # for updating _serial
    fst:   fst.FST | Literal[False]  # False indicates nothing to update on done()
    field: astfield
    data:  list

    def __init__(self, fst_: fst.FST, field: str | Literal[False] = False, raw: bool = False) -> None:
        """Call before modifying `FST` node (even just source) to mark possible data for updates after modification.
        This function just collects information when it enters so is safe to call without ever explicitly exiting.
        Though it should be called on a successful modification because it increments the modification cound
        `_serial`. Can be used as a context manager or can just call `.enter()` and `.done()` manually.

        It is assumed that neither the `fst_` node passed in or its parents will not be changed, otherwise this must
        be used manually and not as a context manager and the changed node must be passed into the `.done()` method
        on success. In this case currently no parents are updated as it is assumed the changes are due to raw
        reparse which goes up to the statement level and would thus include any modifications this class would make.

        **Parameters:**
        - `fst_`: Parent of or actual node being modified, depending on value of `field` (because actual child may be
            being created and may not exist yet).
        - `field`: Name of field being modified or `False` to indicate that `self` is the child, in which case the
            parent and field will be gotten from `self`.
        - `raw`: Whether this is going to be a raw modification or not.
        """

        self.root = fst_.root

        if raw:
            self.fst = False

            return

        if field is False:
            pfield = fst_.pfield

            if fst_ := fst_.parent:
                field = pfield.name

        self.fst = fst_ if fst_ and isinstance(fst_.a, expr) else False

        if self.fst:
            self.field = field
            self.data  = data = []  # [(FormattedValue or Interpolation FST, len(dbg_str) or None, bool do val_str), ...]

            while isinstance(fst_.a, EXPRISH):
                parent = fst_.parent
                pfield = fst_.pfield

                if field == 'value' and (strs := fst_._get_fmtval_interp_strs()):  # this will never proc for py < 3.12, in case we ever make this code common
                    dbg_str, val_str, end_ln, end_col = strs

                    if (dbg_str is None or not parent or not (idx := pfield.idx) or
                        not isinstance(prev := parent.a.values[idx - 1], Constant) or
                        not isinstance(v := prev.value, str) or not v.endswith(dbg_str) or
                        (prevf := prev.f).end_col != end_col or prevf.end_ln != end_ln
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
                fst_  = parent

    def __enter__(self) -> Self:
        return self.enter()

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> bool:
        if exc_type is None:
            self.done()

        return False

    def enter(self) -> Self:
        return self

    def done(self, fst_: fst.FST | None | Literal[False] = False) -> None:
        """Call after modifying `FST` node to apply any needed changes to parents.

        **Parameters:**
        - `fst_`: Parent node of modified field AFTER modification (may have changed or not exist anymore). Or can be
            special value `False` to indicate that original `fst_` was definitely not replaced, with replaced
            referring to the actual `FST` node that might be replaced in a raw reparse, not whether the content
            itself was modified. This is meant for special case use outside of the context manager.
        """

        self.root._serial += 1

        if fst_ is False:
            if not (fst_ := self.fst):
                return

        elif fst_ is not self.fst:  # if parent of field changed then entire statement was reparsed and we have nothing to do
            return

        if data := self.data:
            first = data[0]

            for strs in data:
                fst_, len_old_dbg_str, do_val_str = strs

                if strs is first:  # on first one check to make sure no double '{{', and if so then fix: f'{{a}}' -> f'{ {a}}'
                    ln, col, _, _ = fst_.a.value.f.loc
                    fix_const     = ((parent := fst_.parent) and (idx := fst_.pfield.idx) and   # parent should exist here but just in case, whether we need to reset start of debug string or not
                        (f := parent.a.values[idx - 1].f).col == col and f.ln == ln)

                    if fst_.root._lines[ln].startswith('{', col):
                        fst_._put_src([' '], ln, col, ln, col, False)

                        if fix_const:
                            f.a.col_offset -= 1

                dbg_str, val_str, end_ln, end_col = fst_._get_fmtval_interp_strs()

                if do_val_str:
                    fst_.a.str = val_str

                if len_old_dbg_str is not None:
                    lines            = fst_.root._lines
                    c                = fst_.parent.a.values[fst_.pfield.idx - 1]
                    c.value          = c.value[:-len_old_dbg_str] + dbg_str
                    c.end_lineno     = end_ln + 1
                    c.end_col_offset = lines[end_ln].c2b(end_col)

@pyver(lt=12)  # override _Modifying if py too low
class _Modifying:
    """Dummy because py < 3.12 doesn't have f-string location information."""

    def __init__(self, fst_: fst.FST, field: str | Literal[False] = False, raw: bool = False):
        self.root = fst_.root

        if not raw:
            while not isinstance(a := fst_.a, (stmt, pattern, match_case, ExceptHandler)):  # don't allow modification if inside an f-string because before 3.12 they were very fragile
                if isinstance(a, JoinedStr):
                    raise NotImplementedError('put inside JoinedStr not implemented on python < 3.12')

                if not (fst_ := fst_.parent):
                    break

    def __enter__(self) -> Self:
        return self.enter()

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> bool:
        if exc_type is None:
            self.done()

        return False

    def enter(self) -> Self:
        return self

    def done(self, fst_: fst.FST | None | Literal[False] = False) -> None:
        self.root._serial += 1


def _make_tree_fst(ast: AST, parent: fst.FST, pfield: astfield) -> fst.FST:
    """Make `FST` node from `AST`, recreating possibly non-unique AST nodes."""

    if not getattr(ast, 'f', None):  # if `.f` exists then this has already been done
        if isinstance(ast, (expr_context, unaryop, operator, boolop, cmpop)):  # ast.parse() reuses simple objects, we need all objects to be unique
            pfield.set(parent.a, ast := ast.__class__())

    return fst.FST(ast, parent, pfield)


def _out_lines(fst_: fst.FST, linefunc: Callable, ln: int, col: int, end_ln: int, end_col: int, eol: str = '') -> None:
    width = int(log10(len(fst_.root._lines) - 1 or 1)) + 1
    lines = fst_.get_src(ln, col, end_ln, end_col, True)

    if (l := lines[-1][:end_col]).endswith(' '):
        l += '<'

    lines[-1] = l

    if (l := lines[0]).startswith(' ') and col:
        lines[0]  = f'{" " * (col - 1)}>{l}'
    else:
        lines[0]  = ' ' * col + l

    for i, l in zip(range(ln, end_ln + 1), lines, strict=True):
        linefunc(f'{i:<{width}}: {l}{eol}')


# ----------------------------------------------------------------------------------------------------------------------
# FST class private methods

@staticmethod
def _new_empty_module(*, from_: fst.FST | None = None) -> fst.FST:
    return fst.FST(Module(body=[], type_ignores=[]), [''], from_=from_, lcopy=False)


@staticmethod
def _new_empty_tuple(*, from_: fst.FST | None = None) -> fst.FST:
    ast = Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return fst.FST(ast, ['()'], from_=from_)


@staticmethod
def _new_empty_list(*, from_: fst.FST | None = None) -> fst.FST:
    ast = List(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return fst.FST(ast, ['[]'], from_=from_)


@staticmethod
def _new_empty_dict(*, from_: fst.FST | None = None) -> fst.FST:
    ast = Dict(keys=[], values=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return fst.FST(ast, ['{}'], from_=from_)


@staticmethod
def _new_empty_set_star(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None, as_fst: bool = True,
                        ) -> fst.FST | AST:
    src = ['{*()}']
    ast = Set(elts=[Starred(value=Tuple(elts=[], ctx=Load(), lineno=lineno, col_offset=col_offset+2,
                                        end_lineno=lineno, end_col_offset=col_offset+4),
                            ctx=Load(),
                            lineno=lineno, col_offset=col_offset+1, end_lineno=lineno, end_col_offset=col_offset+4)],
              lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return fst.FST(ast, src, from_=from_) if as_fst else (ast, src)


@staticmethod
def _new_empty_set_call(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None, as_fst: bool = True,
                        ) -> fst.FST:
    src = ['set()']
    ast = Call(func=Name(id='set', ctx=Load(),
                         lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+3),
               args=[], keywords=[],
               lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return fst.FST(ast, src, from_=from_) if as_fst else (ast, src)


@staticmethod
def _new_empty_set_curlies(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None) -> fst.FST | AST:
    ast = Set(elts=[], lineno=lineno, col_offset=col_offset, end_lineno=lineno,
              end_col_offset=col_offset + 2)

    return fst.FST(ast, ['{}'], from_=from_)


@staticmethod
def _new_empty_matchseq(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None) -> fst.FST:
    return fst.FST(MatchSequence(patterns=[], lineno=lineno, col_offset=col_offset,
                                 end_lineno=lineno, end_col_offset=col_offset + 2),
                   ['[]'], from_=from_)


@staticmethod
def _new_empty_matchmap(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None) -> fst.FST:
    return fst.FST(MatchMapping(keys=[], patterns=[], rest=None, lineno=lineno, col_offset=col_offset,
                                end_lineno=lineno, end_col_offset=col_offset + 2),
                   ['{}'], from_=from_)


@staticmethod
def _new_empty_matchor(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None) -> fst.FST:
    return fst.FST(MatchOr(patterns=[], lineno=lineno, col_offset=col_offset,
                           end_lineno=lineno, end_col_offset=col_offset),
                   [''], from_=from_)


def _repr_tail(self: fst.FST) -> str:
    try:
        loc = self.loc
    except Exception:  # maybe in middle of operation changing locations and lines
        loc = '????'

    self._touchall(False, True, True)  # for debugging because we may have cached locs which would not have otherwise been cached during execution

    tail = ' ROOT' if self.is_root else ''

    return f'{tail} {loc[0]},{loc[1]}..{loc[2]},{loc[3]}' if loc else tail


def _dump(self: fst.FST, st: nspace, cind: str = '', prefix: str = '') -> None:
    ast  = self.a
    tail = self._repr_tail()
    sind = ' ' * st.indent

    if not st.src:  # noop
        pass

    elif isinstance(ast, (stmt, ExceptHandler, match_case)):  # src = 'stmt' or 'all'
        if loc := self.bloc:
            if isinstance(ast, BLOCK):
                _out_lines(self, st.linefunc, loc.ln, loc.col, *self._loc_block_header_end(), st.eol)
            else:
                _out_lines(self, st.linefunc, *loc, st.eol)

    elif not isinstance(ast, mod):
        if st.src == 'all':
            if not (parent := self.parent) or not isinstance(parent.a, Expr):
                if loc := self.loc:
                    _out_lines(self, st.linefunc, *loc, st.eol)

        elif st.src == 'stmt' and not self.parent:  # if putting statements but root is not statement or mod then just put root src and no src below
            st.src = None

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


def _make_fst_tree(self: fst.FST, stack: list[fst.FST] | None = None) -> None:
    """Create tree of `FST` nodes, one for each AST node from root. Call only on root or with pre-made stack of nodes
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


def _unmake_fst_tree(self: fst.FST, stack: list[AST] | None = None) -> None:
    """Destroy a tree of `FST` child nodes by breaking links between AST and `FST` nodes. This mainly helps make sure
    destroyed `FST` nodes can't be reused in a way that might corrupt valid remaining trees."""

    if stack is None:
        stack = [self.a]

    while stack:  # make sure these bad ASTs can't hurt us anymore
        if a := stack.pop():  # could be `None`s in there
            a.f.a = a.f = None  # root, parent and pfield are still useful after node has been removed

            stack.extend(iter_child_nodes(a))


def _unmake_fst_parents(self: fst.FST, self_: bool = False) -> None:
    """Walk up parent list unmaking each parent along the way. This does not unmake the entire parent tree, just the
    parents directly above this node (and including `self` if `self_` is `True). Meant for when you know the parents are
    just a direct succession like Expr -> Module."""

    if self_:
        self.a.f = self.a = None

    while self := self.parent:
        self.a.f = self.a = None


def _set_ast(self: fst.FST, ast: AST, valid_fst: bool = False, unmake: bool = True) -> AST:
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
        itr  = walk(ast)

        try:
            if (f := next(itr).f).root is not root:  # if tree already has same root then we don't need to do this
                f.root = root

                for a in itr:
                    a.f.root = root

        except StopIteration:  # from the next() if empty
            pass

        for a in iter_child_nodes(ast):
            a.f.parent = self

    if parent := self.parent:
        self.pfield.set(parent.a, ast)

    self._touch()

    return old_ast


def _set_ctx(self: fst.FST, ctx: type[expr_context]) -> None:
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


def _next_bound(self: fst.FST, with_loc: bool | Literal['all', 'own'] = 'all') -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object within parent. If no siblings found after
    self then return end of parent. If no parent then return end of source."""

    if next := self.next(with_loc):
        return next.bloc[:2]
    elif parent := self.parent:
        return parent.bloc[2:]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound(self: fst.FST, with_loc: bool | Literal['all', 'own'] = 'all') -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object within parent. If no siblings found before
    self then return start of parent. If no parent then return (0, 0)."""

    if prev := self.prev(with_loc):
        return prev.bloc[2:]
    elif parent := self.parent:
        return parent.bloc[:2]
    else:
        return 0, 0


def _next_bound_step(self: fst.FST, with_loc: bool | Literal['all', 'own', 'allown'] = 'all') -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object using `step_fwd()`. This is safe to call
    for nodes that live inside nodes without their own locations if `with_loc='allown'`."""

    if next := self.step_fwd(with_loc, recurse_self=False):
        return next.bloc[:2]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound_step(self: fst.FST, with_loc: bool | Literal['all', 'own', 'allown'] = 'all') -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object using `step_back()`. This is safe to call for
    nodes that live inside nodes without their own locations if `with_loc='allown'`."""

    if prev := self.step_back(with_loc, recurse_self=False):
        return prev.bloc[2:]

    return 0, 0


def _loc_block_header_end(self: fst.FST, ret_bound: bool = False) -> fstloc | tuple[int, int] | None:
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

    ln, col = next_find(self.root._lines, cend_ln, cend_col, end_ln, end_col, ':')  # it must be there

    return fstloc(cend_ln, cend_col, ln, col + 1) if ret_bound else (ln, col + 1)


def _loc_operator(self: fst.FST) -> fstloc | None:
    """Get location of `operator`, `unaryop` or `cmpop` from source if possible. `boolop` has no location if it has a
    parent because in this case it can be in multiple location in a `BoolOp` and we want to be consistent."""

    # assert isinstance(self.s, (operator, unaryop, cmpop))

    ast = self.a

    if not (op := OPCLS2STR.get(ast.__class__)):
        return None

    lines = self.root._lines

    if not (parent := self.parent):  # standalone
        ln, col, src = next_frag(lines, 0, 0, len(lines) - 1, 0x7fffffffffffffff)  # must be there

        if not isinstance(ast, (NotIn, IsNot)):  # simple one element operator means we are done
            assert src == op or (isinstance(ast, operator) and src == op + '=')

            return fstloc(ln, col, ln, col + len(src))

        op, op2 = op.split(' ')

        assert src == op

        end_ln, end_col, src = next_frag(lines, ln, col + len(op), len(lines) - 1, 0x7fffffffffffffff)  # must be there

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

        if pos := next_find(lines, end_ln, end_col, end_lines := len(lines) - 1, len(lines[-1]), op):
            ln, col = pos

            if not has_space:
                return fstloc(ln, col, ln, col + len(op))

            if pos := next_find(lines, ln, col + len(op), end_lines, len(lines[-1]), op2):
                ln2, col2 = pos

                return fstloc(ln, col, ln2, col2 + len(op2))

    elif (prev := (is_binop := getattr(parenta, 'left', None))) or (prev := getattr(parenta, 'target', None)):
        if pos := next_find(lines, (loc := prev.f.loc).end_ln, loc.end_col, len(lines) - 1, len(lines[-1]), op):
            ln, col = pos

            return fstloc(ln, col, ln, col + len(op) + (not is_binop))  # 'not is_binop' adds AugAssign '=' len

    return None


def _loc_comprehension(self: fst.FST) -> fstloc:
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

    start_ln, start_col = prev_find(lines, ln, col, first.ln, first.col, 'for')  # must be there

    if ast.is_async:
        start_ln, start_col = prev_find(lines, ln, col, start_ln, start_col, 'async')  # must be there

    rpars = next_delims(lines, last.end_ln, last.end_col, *self._next_bound_step('allown'))

    if (lrpars := len(rpars)) == 1:  # no pars, just use end of last
        end_ln, end_col = rpars[0]

    else:
        is_genexp_last = ((parent := self.parent) and isinstance(parent.a, GeneratorExp) and  # correct for parenthesized GeneratorExp
                          self.pfield.idx == len(parent.a.generators) - 1)

        if is_genexp_last and lrpars == 2:  # can't be pars on left since only par on right was close of GeneratorExp
            end_ln, end_col = rpars[0]
        else:

            end_ln, end_col = rpars[len(prev_delims(lines, *last._prev_bound(), last.ln, last.col)) - 1]  # get rpar according to how many pars on left

    return fstloc(start_ln, start_col, end_ln, end_col)


def _loc_arguments(self: fst.FST) -> fstloc | None:
    """`arguments` location from children. Called from `.loc`. Returns `None` when there are no arguments."""

    # assert isinstance(self.s, arguments)

    if not (first := self.first_child()):
        return None

    ast       = self.a
    last      = self.last_child()
    lines     = self.root._lines
    end_lines = len(lines) - 1
    rpars     = next_delims(lines, last.end_ln, last.end_col, *self._next_bound())

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

    if (frag := next_frag(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff)) and frag.src.startswith(','):  # trailing comma
        end_ln, end_col, _  = frag
        end_col            += 1

    elif (parent := self.parent) and isinstance(parent.a, (FunctionDef, AsyncFunctionDef)):  # arguments enclosed in pars
        end_ln, end_col = rpars[-2]  # must be there

    if leading_stars:  # find star to the left, we know it exists so we don't check for None return
        start_ln, start_col = prev_find(lines, *self._prev_bound(), start_ln, start_col, leading_stars)

    if trailing_slash:
        end_ln, end_col  = next_find(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff, '/')  # must be there
        end_col         += 1

        if (frag := next_frag(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff)) and frag.src.startswith(','):  # silly, but, trailing comma trailing slash
            end_ln, end_col, _  = frag
            end_col            += 1

    return fstloc(start_ln, start_col, end_ln, end_col)


def _loc_arguments_empty(self: fst.FST) -> fstloc:
    """`arguments` location for empty arguments ONLY! DO NOT CALL FOR NONEMPTY ARGUMENTS!"""

    # assert isinstance(self.a, arguments)

    if not (parent := self.parent):
        return fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))  # parent=None means we are root

    ln, col, end_ln, end_col = parent.loc
    lines                    = self.root._lines

    if isinstance(parenta := parent.a, Lambda):
        col             += 6
        end_ln, end_col  = next_find(lines, ln, col, end_ln, end_col, ':')

    else:
        if type_params := getattr(parenta, 'type_params', None):  # doesn't exist in py < 3.12
            _, _, ln, col = type_params[-1].f.loc

        ln, col          = next_find(lines, ln, col, end_ln, end_col, '(')
        col             += 1
        end_ln, end_col  = next_find(lines, ln, col, end_ln, end_col, ')')

    return fstloc(ln, col, end_ln, end_col)


def _loc_lambda_args_entire(self: fst.FST) -> fstloc:
    """`Lambda` `args` entire location from just past `lambda` keyword to ':', empty or not. `self` is the `Lambda`, not
    the `arguments`."""

    # assert isinstance(self.a, Lambda)

    ln, col, end_ln, end_col  = self.loc
    col                      += 6
    lines                     = self.root._lines

    if not (args := self.a.args.f).loc:
        end_ln, end_col = next_find(lines, ln, col, end_ln, end_col, ':')

    else:
        _, _, lln, lcol = args.last_child().loc
        end_ln, end_col = next_find(lines, lln, lcol, end_ln, end_col, ':')

    return fstloc(ln, col, end_ln, end_col)


def _loc_withitem(self: fst.FST) -> fstloc:
    """`withitem` location from children. Called from `.loc`."""

    # assert isinstance(self.s, withitem)

    ast   = self.a
    ce    = ast.context_expr.f
    lines = self.root._lines

    ce_ln, ce_col, ce_end_ln, ce_end_col = ce_loc = ce.loc

    if not (ov := ast.optional_vars):
        rpars = next_delims(lines, ce_end_ln, ce_end_col, *self._next_bound_step('allown'))  # 'allown' so it doesn't recurse into calling `.loc`

        if (lrpars := len(rpars)) == 1:
            return ce_loc

        lpars = prev_delims(lines, *self._prev_bound_step('allown'), ce_ln, ce_col)
        npars = min(lrpars, len(lpars)) - 1

        return fstloc(*lpars[npars], *rpars[npars])

    ov_ln, ov_col, ov_end_ln, ov_end_col = ov.f.loc

    rpars = next_delims(lines, ce_end_ln, ce_end_col, ov_ln, ov_col)

    if (lrpars := len(rpars)) == 1:
        ln  = ce_ln
        col = ce_col

    else:
        lpars   = prev_delims(lines, *self._prev_bound_step('allown'), ce_ln, ce_col)
        ln, col = lpars[min(lrpars, len(lpars)) - 1]

    lpars = prev_delims(lines, ce_end_ln, ce_end_col, ov_ln, ov_col)

    if (llpars := len(lpars)) == 1:
        return fstloc(ln, col, ov_end_ln, ov_end_col)

    rpars           = next_delims(lines, ov_end_ln, ov_end_col, *self._next_bound_step('allown'))
    end_ln, end_col = rpars[min(llpars, len(rpars)) - 1]

    return fstloc(ln, col, end_ln, end_col)


def _loc_match_case(self: fst.FST) -> fstloc:
    """`match_case` location from children. Called from `.loc`."""

    # assert isinstance(self.a, match_case)

    ast   = self.a
    first = ast.pattern.f
    last  = self.last_child()
    lines = self.root._lines

    start = prev_find(lines, 0, 0, first.ln, first.col, 'case')  # we can use '0, 0' because we know "case" starts on a newline

    if ast.body:
        return fstloc(*start, last.bend_ln, last.bend_col)

    end_ln, end_col = next_find(lines, last.bend_ln, last.bend_col, len(lines) - 1, len(lines[-1]), ':')  # special case, deleted whole body, end must be set to just past the colon (which MUST follow somewhere there)

    return fstloc(*start, end_ln, end_col + 1)


def _loc_ImportFrom_names_pars(self: fst.FST) -> fstlocns:
    """Location of `from ? import (...)` parentheses, or location where they should be put if adding.

    Can handle empty `module` and `names`.

    **Returns:**
    - `fstlocns`: Just like from `FST.pars()`, with attribute `n=0` meaning no parentheses present and location is where
        they should go and `n=1` meaning parentheses present and location is where they actually are.
    """

    lines                     =  self.root._lines
    ln, col, end_ln, end_col  = self.loc
    ln, col, _                = next_find_re(lines, ln, col, end_ln, end_col, _re_keyword_import)  # must be there
    col                      += 6

    if (lpar := next_frag(lines, ln, col, end_ln, end_col)) and lpar.src.startswith('('):
        ln, col, _ = lpar
        rpar       = prev_frag(lines, ln, col + 1, end_ln, end_col)

        assert rpar and rpar.src.endswith(')')

        end_ln, end_col, src = rpar

        return fstlocns(ln, col, end_ln, end_col + len(src), n=1)

    return fstlocns(ln, col + 1 if lines[ln][col : col + 1].isspace() else col, end_ln, end_col, n=0)


def _loc_call_pars(self: fst.FST) -> fstloc:
    # assert isinstance(self.s, Call)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.func.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_subscript_brackets(self: fst.FST) -> fstloc:
    # assert isinstance(self.s, Subscript)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.value.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = next_find(lines, ln, col, end_ln, end_col, '[')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_matchcls_pars(self: fst.FST) -> fstloc:
    # assert isinstance(self.a, MatchClass)

    ast                   = self.a
    lines                 = self.root._lines
    _, _, ln, col         = ast.cls.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col               = next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def _loc_funcdef_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    # assert isinstance(self.a, (FunctionDef, AsyncFunctionDef))

    ast   = self.a
    lines = self.root._lines
    args  = ast.args

    ln, col, end_ln, end_col = self.loc

    if ((after := args.posonlyargs) or (after := args.args) or (after := args.vararg) or (after := args.kwonlyargs) or
        (after := args.kwarg) or (after := ast.returns) or (after := ast.body)
    ):
        after_ln, after_col, _, _ = (after[0] if isinstance(after, list) else after).f.loc
    else:  # accomodate temporarily empty bodies
        after_ln  = end_ln
        after_col = end_col

    if isinstance(ast, AsyncFunctionDef):
        ln, col = next_find(lines, ln, col + 5, after_ln, after_col, 'def')  # must be there

    name_end_ln, name_end_col, src = next_find_re(lines, ln, col + 3, after_ln, after_col, re_identifier)  # must be there

    name_end_col += len(src)

    if not (pos := next_find(lines, name_end_ln, name_end_col, after_ln, after_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln  = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, after_ln, after_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def _loc_classdef_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    # assert isinstance(self.a, ClassDef)

    ast   = self.a
    lines = self.root._lines

    ln, col, end_ln, end_col = self.loc

    if (after := ast.bases) or (after := ast.keywords) or (after := ast.body):
        after_ln, after_col, _, _ = after[0].f.loc
    else:  # accomodate temporarily empty bodies
        after_ln  = end_ln
        after_col = end_col

    name_end_ln, name_end_col, src = next_find_re(lines, ln, col + 5, after_ln, after_col, re_identifier)  # must be there

    name_end_col += len(src)

    if not (pos := next_find(lines, name_end_ln, name_end_col, after_ln, after_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln  = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, after_ln, after_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def _loc_typealias_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    # assert isinstance(self.a, TypeAlias)

    ast   = self.a
    lines = self.root._lines

    _, _, name_end_ln, name_end_col = ast.name.f.loc
    val_ln, val_col, _, _           = ast.value.f.loc

    if not (pos := next_find(lines, name_end_ln, name_end_col, val_ln, val_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln  = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, val_ln, val_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def _loc_global_nonlocal_names(self: fst.FST, first: int, last: int | None = None) -> fstloc | tuple[fstloc, fstloc]:
    """We assume `first` and optionally `last` are in [0..len(names)), no negative or out-of-bounds and `last` follows
    or equals `first` if present."""

    # assert isinstance(self.a, (Global, Nonlocal))

    ln, col, end_ln, end_col = self.loc

    col   += 6 if isinstance(self.a, Global) else 8
    lines  = self.root._lines
    idx    = first

    while idx:  # skip the commas
        ln, col  = next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col     += 1
        idx     -= 1

    ln, col, src = next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there
    first_loc    = fstloc(ln, col, ln, col := col + len(src))

    if last is None:
        return first_loc

    if not (idx := last - first):
        return first_loc, first_loc

    while idx:
        ln, col  = next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col     += 1
        idx     -= 1

    ln, col, src = next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there

    return first_loc, fstloc(ln, col, ln, col + len(src))


def _loc_maybe_dict_key(self: fst.FST, idx: int, pars: bool = False, body: list[AST] | None = None) -> fstloc:
    """Return location of dictionary key even if it is `**` specified by a `None`. Optionally return the location of the
    grouping parentheses if key actually present. Can also be used to get the location (parenthesized or not) from any
    list of `AST`s which is not a `Dict.keys` if an explicit `body` is passed in (assuming none of the are `None`).

    **WARNING:** `idx` must be positive.
    """

    # assert isinstance(self.a, Dict)

    if key := (body or self.a.keys)[idx]:
        return key.f.pars() if pars else key.f.loc

    val_ln, val_col, _, _ = (values := self.a.values)[idx].f.loc

    if idx:
        _, _, ln, col = values[idx - 1].f.loc
    else:
        ln, col, _, _ = self.loc

    ln, col = prev_find(self.root._lines, ln, col, val_ln, val_col, '**')  # '**' must be there

    return fstloc(ln, col, ln, col + 2)


def _is_arguments_empty(self: fst.FST) -> bool:
    """Is this `arguments` node empty?"""

    # assert isinstance(self.a, arguments)

    return not ((a := self.a).posonlyargs or a.args or a.vararg or a.kwonlyargs or a.kwarg)


def _is_parenthesized_ImportFrom_names(self: fst.FST) -> bool:
    # assert isinstance(self.a, ImportFrom)

    ln, col, _, _         = self.loc
    end_ln, end_col, _, _ = self.a.names[0].f.loc

    return prev_frag(self.root._lines, ln, col, end_ln, end_col).src.endswith('(')  # something is there for sure


def _is_parenthesized_With_items(self: fst.FST) -> bool:
    # assert isinstance(self.a, (With, AsyncWith))

    ln, col, _, _         = self.loc
    end_ln, end_col, _, _ = self.a.items[0].f.loc  # will include any pars in child so don't need to depar

    return prev_frag(self.root._lines, ln, col, end_ln, end_col).src.endswith('(')  # something is there for sure


def _is_delimited_seq(self: fst.FST, field: str = 'elts', delims: str | tuple[str, str] = '()') -> bool:
    """Whether `self` is a delimited (parenthesized or bracketeed) sequence of `field` or not. Makes sure the entire
    node is surrounded by a balanced pair of delimiters. Functions as `is_parenthesized_tuple()` if already know is a
    Tuple. Other use is for `MatchSequence`, whether parenthesized or bracketed."""

    ldelim, rdelim = delims
    lines          = self.root._lines

    self_ln, self_col, self_end_ln, self_end_col = self.loc

    if not lines[self_end_ln].startswith(rdelim, self_end_col - 1):
        return False

    if not (asts := getattr(self.a, field)):
        return True  # return True if no children because assume '()' in this case

    if not lines[self_ln].startswith(ldelim, self_col):
        return False

    f0_ln, f0_col, f0_end_ln, f0_end_col = asts[0].f.loc

    if f0_col == self_col and f0_ln == self_ln:
        return False

    _, _, fn_end_ln, fn_end_col = asts[-1].f.loc

    if fn_end_col == self_end_col and fn_end_ln == self_end_ln:
        return False

    # dagnabit! have to count and balance delimiters around first element

    self_end_col -= 1  # because in case of singleton tuple for sure there is a comma between end of first element and end of tuple, so at worst we exclude either the tuple closing paren or a comma, otherwise we exclude non-tuple closing delimiter

    ldelims = len(next_delims(lines, self_ln, self_col, f0_ln, f0_col, ldelim))  # yes, we use next_delims() to count opening delimiters because we know conditions allow it
    rdelims = len(next_delims(lines, f0_end_ln, f0_end_col, self_end_ln, self_end_col, rdelim))

    return ldelims > rdelims


def _set_end_pos(self: fst.FST, end_lineno: int, end_col_offset: int, self_: bool = True) -> None:  # because of trailing non-AST junk in last statements
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
            end_lineno     = last_child.end_lineno
            end_col_offset = last_child.end_col_offset

    if end_lineno is None:
        lines = self.root._lines

        if end := prev_find(lines, bound_ln, bound_col, bound_end_ln, bound_end_col, ':'):  # find first preceding block colon, its there unless first opened block in module
            end_ln, end_col  = end
            end_col         += 1  # just past the colon

        else:
            end_ln  = bound_ln
            end_col = bound_col

        end_lineno     = end_ln + 1
        end_col_offset = lines[end_ln].c2b(end_col)

    self._set_end_pos(end_lineno, end_col_offset)


def _update_loc_up_parents(self: fst.FST, lineno: int, col_offset: int, end_lineno: int, end_col_offset: int) -> None:
    """Change own location adn walk up parent chain changing any start or end locations which coincide with our own old
    location to the new one."""

    ast                = self.a
    old_lineno         = ast.lineno
    old_col_offset     = ast.col_offset
    old_end_lineno     = ast.end_lineno
    old_end_col_offset = ast.end_col_offset
    ast.lineno         = lineno
    ast.col_offset     = col_offset
    ast.end_lineno     = end_lineno
    ast.end_col_offset = end_col_offset

    self._touch()

    while self := self.parent:
        if (self_end_col_offset := getattr(a := self.a, 'end_col_offset', None)) is None:
            break

        if n := self_end_col_offset == old_end_col_offset and a.end_lineno == old_end_lineno:  # only change if matches old location
            a.end_lineno     = end_lineno
            a.end_col_offset = end_col_offset

        if a.col_offset == old_col_offset and a.lineno == old_lineno:
            a.lineno     = lineno
            a.col_offset = col_offset

        elif not n:
            break

        self._touch()

    if self:
        self._touchall(True)


def _maybe_add_line_continuations(self: fst.FST, whole: bool = False) -> bool:
    """Check if `self` needs them and if so add line continuations to make parsable.

    **Parameters:**
    - `whole`: Whether to check whole source (and add line continuations to, only if at root). Otherwise will just
        check and modify lines that this node lives on.

    **Returns:**
    - `bool`: Whether modification was made or not.
    """

    if self.is_enclosed_or_line(whole=whole, out_lns=(lns := set())):
        return False

    lines    = self.root._lines
    end_cols = {}  # {end_ln: end_col, ...} last expression columns for lines, needed for comment checks (so we don't get false comments from inside strings)

    for a in walk(self.a):
        if (loc := a.f.loc) is not None:
            _, _, end_ln, end_col = loc

            end_cols[end_ln] = max(end_cols.get(end_ln, 0), end_col)

    for ln in lns:
        m = re_line_end_cont_or_comment.match(lines[ln], end_cols.get(ln, 0))

        if not (g := m.group(1)):
            lines[ln] = bistr((l := lines[ln]) + ('\\' if not l or l[-1:].isspace() else ' \\'))
        elif g.startswith('#'):
            raise NodeError('cannot add line continuation to line that ends with comment')

    return True


def _maybe_del_separator(self: fst.FST, ln: int, col: int, force: bool = False,
                         end_ln: int | None = None, end_col: int | None = None, sep: str = ',') -> bool:
    """Maybe delete a separator if present. Can be always deleted or allow function to decide aeshtetically. We
    specifically don't use `pars()` here because is meant to be used where the element is being modified and may not be
    valid for that. This is meant to work with potential closing parentheses present after (`ln`, `col`) and expects
    that if the separator is present in the span that it is the valid separator we are looking for. If no separator
    found then nothing is deleted.

    **Parameters:**
    - `force`: Whether to always delete a separator if it is present or maybe leave based on aesthetics.

    **Returns:**
    - `bool`: Whether a separator was deleted or not
    """

    if end_ln is None:
        _, _, end_ln, end_col = self.loc

    lines = self.root._lines

    if not (pos := next_find(lines, ln, col, end_ln, end_col, sep)):
        return False

    sep_ln, sep_col = pos
    sep_end_col     = sep_col + len(sep)
    sep_on_end_ln   = sep_ln == end_ln
    line_sep        = lines[sep_ln]

    if not (frag := next_frag(lines, sep_ln, sep_end_col, sep_ln, end_col if sep_on_end_ln else 0x7fffffffffffffff,
                             True, True)):  # nothing on rest of line after separator?
        sep_end_col = end_col if sep_on_end_ln else len(line_sep)

    elif frag.src[0] not in '#\\':  # not a comment or line continuation, closing delimiter or next element if being used that way
        sep_end_col = frag.col

    elif not force:  # comment or line continuation follows, leave separator for aesthetic reasons if allowed
        return False

    del_col = re_line_trailing_space.match(line_sep, col if sep_ln == ln else 0, sep_col).start(1)

    self._put_src(None, sep_ln, del_col or sep_col, sep_ln, sep_end_col, True)

    return True


def _maybe_ins_separator(self: fst.FST, ln: int, col: int, space: bool,
                         end_ln: int | None = None, end_col: int | None = None, sep: str = ',',
                         exclude: Literal[True] | fst.FST | None = True) -> srcwpos | None:
    """Maybe insert separator at start of span if not already present as first code in span. Will skip any closing
    parentheses for check and add. We specifically don't use `pars()` here because is meant to be used where the element
    is being modified and may not be valid for that.

    **Parameters:**
    - (`ln`, `col`): Location of start of span.
    - (`end_ln`, `end_col`): Location of end of span, otherwise gotten from end of `self`.
    - `space`: Whether to add a space to new separator or existing separator IF the span is zero length or if following
        character exists and is not a space. Will add space before a separator being put if is not a comma. Will not
        insert space before an existing found separator if is not there.
    - `sep`: String separator to use. Any separator which is not a comma will have a space prepended to it if adding.
    - `exclude`: `True` means exclude `self`, `None` excludes nothing and any other `FST` excludes that `FST`. Should be
        `True` if separator is for sure being put past all elements of `self`. `FST` and `None` is meant for cases where
        there may be elements following separator insertion location. `FST` specifically for elements which end just
        before the search location so that their end position is not extended by the separator source put.

    **Returns:**
    - `srcwpos`: If something was put then returns location and what was put (separator, space or both).
    - `None`: Nothing was put.
    """

    if end_ln is None:
        _, _, end_ln, end_col = self.loc

    if offset_excluded := exclude is True:
        exclude = self

    lines = self.root._lines

    while frag := next_frag(lines, ln, col, end_ln, end_col):  # find comma or something else, skipping close parens
        cln, ccol, src = frag

        for c in src:
            ccol += 1

            if c == ')':
                ln  = cln
                col = ccol

            elif c != sep:
                break

            else:
                if space and ((cln == end_ln and ccol == end_col) or not _re_one_space_or_end.match(lines[cln], ccol)):
                    self._put_src([' '], cln, ccol, cln, ccol, True, exclude=exclude, offset_excluded=offset_excluded)

                    return srcwpos(cln, ccol, ' ')

                return None

        else:
            continue

        break

    if sep != ',':
        sep = ' ' + sep

    if space and ((ln == end_ln and col == end_col) or not _re_one_space_or_end.match(lines[ln], col)):
        sep = sep + ' '

    self._put_src([sep], ln, col, ln, col, True, exclude=exclude, offset_excluded=offset_excluded)

    return srcwpos(ln, col, sep)


def _maybe_add_singleton_tuple_comma(self: fst.FST, is_par: bool | None = None) -> None:
    """Maybe add comma to tuple if is singleton and comma not already there, parenthesization not checked or taken
    into account. `self.a` must be a `Tuple`."""

    # assert isinstance(self.a, Tuple)

    if (elts := self.a.elts) and len(elts) == 1:
        self._maybe_ins_separator((f := elts[0].f).end_ln, f.end_col, False, self.end_ln,
                                  self.end_col - (self._is_delimited_seq() if is_par is None else is_par))


def _maybe_fix_joined_alnum(self: fst.FST, ln: int, col: int, end_ln: int | None = None, end_col: int | None = None,
                            ) -> None:
    """Check if location(s) `lines[ln][col-1 : col+1]` and optionally `lines[end_ln][end_col-1 : end_col+1] is / are
    alphanumeric and if so separate them with a space. This is for operations that may inadvertantly join two distinct
    elements into a single parsable alphanumeric, e.g. `for i inb, 2: pass`."""

    lines = self.root._lines

    if end_ln is not None:
        if end_col and re_alnumdot_alnum.match(lines[end_ln], end_col - 1):  # make sure last element didn't wind up joining two alphanumerics, and if so separate
            self._put_src([' '], end_ln, end_col, end_ln, end_col, False)

    if col and re_alnumdot_alnum.match(lines[ln], col - 1):  # make sure first element didn't wind up joining two alphanumerics, and if so separate
        self._put_src([' '], ln, col, ln, col, False)


def _maybe_fix_undelimited_seq(self: fst.FST, body: list[AST], delims: str = '()') -> bool:
    """Fix undelimited `Tuple` or `MatchSequence` if needed. Don't call on delimited sequence."""

    # assert isinstance(self.a, (Tuple, MatchSequence))

    if not body:  # if is empty then just need to delimit
        lines                    = self.root._lines
        ln, col, end_ln, end_col = self.loc

        if not next_frag(lines, ln, col, end_ln, end_col, True):  # if no comments in tuple area then just replace with '()'
            self._put_src([delims], ln, col, end_ln, end_col, True, False)  # WARNING! `tail=True` may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized tuple starts, but haven't found a case where this can happen

        else:  # otherwise preserve comments by parenthesizing whole area
            ldelim, rdelim = delims

            if end_col and (l := lines[end_ln]).endswith(' ', 0, end_col):
                lines[end_ln] = bistr(f'{l[:end_col - 1]}{rdelim}{l[end_col:]}')
            else:
                self._put_src([rdelim], end_ln, end_col, end_ln, end_col, True)

            if (l := lines[ln]).startswith(' ', col):
                lines[ln] = bistr(f'{l[:col]}{ldelim}{l[col + 1:]}')
            else:
                self._put_src([ldelim], ln, col, ln, col, False, False)

        return True

    ln, col, end_ln, end_col = self.loc
    encpar                   = None

    if ((end_ln != ln and not self.is_enclosed_or_line(pars=False) and not (encpar := self.is_enclosed_in_parents())) or  # could have line continuations
        (any(isinstance(e, NamedExpr) and not e.f.pars().n for e in body))  # yeah, this is fine in parenthesized tuples but not in naked ones, only applies to tuples and not MatchSequence obviously
    ):
        self._delimit_node(delims=delims)

        return True

    eln, ecol, _, _ = body[0].f.pars()
    lines           = self.root._lines

    if ecol != col or eln != ln:  # to be super safe we enforce that an undelimited node must start at the first element
        self._put_src(None, ln, col, eln, ecol, False)

        ln, col, end_ln, end_col = self.loc

    _, _, eend_ln, eend_col = body[-1].f.pars()

    if comma := next_find(lines, eend_ln, eend_col, end_ln, end_col, ','):  # could be closing grouping pars before comma
        eend_ln, eend_col  = comma
        eend_col          += 1

    if end_col != eend_col or end_ln != eend_ln:  # need to update end position because it had some whitespace after which will not be enclosed by delimiters
        if not (encpar or self.is_enclosed_in_parents()):
            self._put_src(None, eend_ln, eend_col, end_ln, end_col, True)  # be safe, nuke everything after last element since we won't have delimiters or parent to delimit it

        else:  # enclosed in parents so we can leave crap at the end
            a                  = self.a
            cur_end_lineno     = a.end_lineno
            cur_end_col_offset = a.end_col_offset
            end_lineno         = a.end_lineno     = eend_ln + 1
            end_col_offset     = a.end_col_offset = lines[eend_ln].c2b(eend_col)

            self._touch()

            while ((self := self.parent) and
                    getattr(a := self.a, 'end_col_offset', -1) == cur_end_col_offset and
                    a.end_lineno == cur_end_lineno
            ):  # update parents, only as long as they end exactly where we end
                a.end_lineno     = end_lineno
                a.end_col_offset = end_col_offset

                self._touch()

            else:
                if self:
                    self._touchall(True)

        _, _, end_ln, end_col = self.loc

    self._maybe_fix_joined_alnum(ln, col, end_ln, end_col)

    return False


def _maybe_fix_tuple(self: fst.FST, is_par: bool | None = None) -> bool:
    """
    **Returns:**
    - `bool`: Whether the tuple is parenthesized or not (after the fix, regardless of if fix was done or not).
    """
    # assert isinstance(self.a, Tuple)

    if is_par is None:
        is_par = self._is_delimited_seq()

    if body := self.a.elts:
        self._maybe_add_singleton_tuple_comma(is_par)

    if not is_par:
        return self._maybe_fix_undelimited_seq(body)

    return is_par


def _maybe_fix_matchseq(self: fst.FST, delims: Literal['', '[]', '()'] | None = None) -> str:
    # assert isinstance(self.a, MatchSequence)

    if delims is None:
        delims = self.is_delimited_matchseq()

    if len(body := self.a.patterns) == 1 and not delims.startswith('['):
        self._maybe_ins_separator((f := body[0].f).end_ln, f.end_col, False, self.end_ln, self.end_col - bool(delims))

    if not delims:
        return self._maybe_fix_undelimited_seq(body, '[]')

    return delims


def _maybe_fix_matchor(self: fst.FST, fix1: bool = False) -> None:
    """Maybe fix a `MatchOr` object that may have the wrong location. Will do nothing to a zero-length `MatchOr` and
    will convert a length 1 `MatchOr` to just its single element if `fix1=True`.

    **WARNING!** This is currently expecting to be called from slice operations with specific conditions, not guaranteed
    will work on any-old `MatchOr`.
    """

    # assert isinstance(self.a, MatchOr)

    if not (patterns := self.a.patterns):
        return

    lines   = self.root._lines
    did_par = False

    if not (is_root := self.is_root):  # if not root then it needs ot be fixed here
        if not self.is_enclosed_or_line() and not self.is_enclosed_in_parents():
            self._parenthesize_grouping()  # we do this instead or _sanitize() to keep any trivia, and we do it first to make sure we don't introduce any unenclosed newlines

            did_par = True

    if (len_patterns := len(patterns)) == 1 and fix1:
        pat0 = patterns[0]

        del patterns[0]

        self._set_ast(pat0, True)

    else:
        ln, col, end_ln, end_col = patterns[0].f.pars()

        if len_patterns > 1:
            _, _, end_ln, end_col = patterns[-1].f.pars()

        col_offset     = lines[ln].c2b(col)
        end_col_offset = lines[end_ln].c2b(end_col)

        self._update_loc_up_parents(ln + 1, col_offset, end_ln + 1, end_col_offset)

    if is_root:
        if not self.is_enclosed_or_line() and not self.is_enclosed_in_parents():
            self._parenthesize_grouping(False)

            did_par = True

    if not did_par:
        self._maybe_fix_joined_alnum(*self.loc)


def _maybe_fix_set(self: fst.FST, empty: bool | Literal['star', 'call'] = True) -> None:
    # assert isinstance(self.a, Set)

    if empty and not (a := self.a).elts:
        if empty == 'call':
            ast, src = _new_empty_set_call(a.lineno, a.col_offset, as_fst=False)
        else:  # True, 'star'
            ast, src = _new_empty_set_star(a.lineno, a.col_offset, as_fst=False)

        ln, col, end_ln, end_col = self.loc

        self._put_src(src, ln, col, end_ln, end_col, True)
        self._set_ast(ast)


def _maybe_fix_elif(self: fst.FST) -> None:
    # assert isinstance(self.a, If)

    ln, col, _, _ = self.loc
    lines         = self.root._lines

    if lines[ln].startswith('elif', col):
        self._put_src(None, ln, col, ln, col + 2, False)


def _maybe_fix_with_items(self: fst.FST) -> None:
    """If `Tuple` only element in `items` then add appropriate parentheses."""

    # assert isinstance(self.a, (With, AsyncWith))

    if (len(items := self.items) == 1 and
        not (i0a := items[0].a).optional_vars and
        (is_par := (cef := i0a.context_expr.f).is_parenthesized_tuple()) is not None
    ):
        if not is_par:
            cef._delimit_node()

        if len(prev_delims(self.root._lines, self.ln, self.col, cef.ln, cef.col)) == 1:  # no pars between start of `with` and start of tuple?
            cef._parenthesize_grouping()  # these will wind up belonging to outer With


def _maybe_fix_copy(self: fst.FST, pars: bool = True, pars_walrus: bool = False) -> None:
    """Maybe fix source and `ctx` values for cut or copied nodes (to make subtrees parsable if the source is not after
    the operation). If cannot fix or ast is not parsable by itself then ast will be unchanged. Is meant to be a quick
    fix after a cut or copy operation, not full check, for that use `verify()`.

    **WARNING!** Only call on root node!
    """

    # assert self.is_root

    if isinstance(ast := self.a, If):
        self._maybe_fix_elif()

    elif isinstance(ast, expr):
        if not self.is_parsable() or isinstance(ast, Slice):  # is_parsable() makes sure there is a self.loc, Slice should never get pars
            return

        self._set_ctx(Load)  # anything that is excluded by is_parsable() above (or does not have .loc) does not need this

        if not pars:
            return

        need_pars = None

        if is_tuple := isinstance(ast, Tuple):
            if is_par := self._is_delimited_seq():
                need_pars = False
            elif any(isinstance(e, NamedExpr) and not e.f.pars().n for e in ast.elts):  # unparenthesized walrus in naked tuple?
                need_pars = True

            self._maybe_add_singleton_tuple_comma(is_par)  # this exists because of copy lone Starred out of a Subscript.slice

        elif isinstance(ast, NamedExpr):  # naked walrus
            need_pars = pars_walrus

        if need_pars is None:
            need_pars = not self.is_enclosed_or_line()

        if need_pars:
            if is_tuple:
                self._delimit_node()
            else:
                self._parenthesize_grouping()


def _touch(self: fst.FST) -> Self:
    """AST node was modified, clear out any cached info for this node only."""

    self._cache.clear()

    return self


def _sanitize(self: fst.FST) -> Self:
    """Quick check to make sure that nodes which are not `stmt`, `ExceptHandler`, `match_case` or `mod` don't have any
    extra junk in the source and that the parenthesized location matches the whole location of the source. If not then
    fix by removing the junk."""

    assert self.is_root

    if not (loc := self.pars()) or loc == self.whole_loc:
        return self

    ln, col, end_ln, end_col = loc
    lines                    = self._lines

    self._offset(ln, col, -ln, -lines[ln].c2b(col))

    lines[end_ln] = bistr(lines[end_ln][:end_col])
    lines[ln]     = bistr(lines[ln][col:])

    del lines[end_ln + 1:], lines[:ln]

    return self


def _parenthesize_grouping(self: fst.FST, whole: bool = True, *, star_child: bool = True) -> None:
    """Parenthesize anything with non-node grouping parentheses. Just adds text parens around node adjusting parent
    locations but not the node itself.

    **WARNING!** DO NOT parenthesize an unparenthesized `Tuple` or undelimited `MatchSequence`.

    **Parameters:**
    - `whole`: If at root then parenthesize whole source instead of just node.
    - `star_child`: `Starred` expressions cannot be parenthesized, so when this is `True` the parentheses are applied to
        the `value` child and the opening par is put right after the `*` to resolve any enclosure issues. This overrides
        `whole` for the opening par.
    """

    ast = self.a

    ln, col, end_ln, end_col = self.whole_loc if whole and self.is_root else self.loc

    if is_star_child := isinstance(ast, Starred) and star_child:
        ln, col, _, _  = self.loc
        col           += 1
        self           = ast.value.f

    self._put_src([')'], end_ln, end_col, end_ln, end_col, True, True, self, offset_excluded=False)

    if is_star_child:  # because of maybe `whole`, otherwise could just do it using _put_src(..., offset_excluded=is_star_child) above
        ast.end_lineno     = end_ln + 1
        ast.end_col_offset = self.root._lines[end_ln].b2c(end_col) + 1

    self._offset(*self._put_src(['('], ln, col, ln, col, False, False, self, offset_excluded=False))


def _unparenthesize_grouping(self: fst.FST, shared: bool | None = True, *, star_child: bool = True) -> bool:
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
        pln, pcol                = prev_find(lines, cend_ln, cend_col, pln, pcol, '(')  # it must be there
        pend_ln, pend_col        = next_find(lines, pend_ln, pend_col, len(lines) - 1, len(lines[-1]), ')')  # ditto
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


def _delimit_node(self: fst.FST, whole: bool = True, delims: str = '()') -> None:
    """Delimit (parenthesize or bracket) a node (`Tuple` or `MatchSequence`, but could be others) with appropriate
    delimiters which are passed in and extend the range of the node to include those delimiters.

    **WARNING!** No checks are done so make sure to call where it is appropriate!

    **Parameters:**
    - `whole`: If at root then delimit whole source instead of just node.
    """

    # assert isinstance(self.a, Tuple)

    ln, col, end_ln, end_col = self.whole_loc if whole and self.is_root else self.loc

    self._put_src([delims[1]], end_ln, end_col, end_ln, end_col, True, False, self)

    lines            = self.root._lines
    a                = self.a
    a.end_lineno     = end_ln + 1  # yes this can change
    a.end_col_offset = lines[end_ln].c2b(end_col + 1)  # can't count on this being set by put_src() because end of `whole` could be past end of tuple

    self._offset(*self._put_src([delims[0]], ln, col, ln, col, False, False, self), self_=False)

    a.lineno     = ln + 1
    a.col_offset = lines[ln].c2b(col)  # ditto on the `whole` thing


def _undelimit_node(self: fst.FST, field: str = 'elts') -> bool:
    """Unparenthesize or unbracketize a parenthesized / bracketed `Tuple` or `MatchSequence`, shrinking node location
    for the removed delimiters. Will not undelimit an empty `Tuple` or `MatchSequence`. Removes everything between the
    delimiters and the actual sequence, e.g. `(  1, 2  # yay \\n)` -> `1, 2`.

    **WARNING!** No checks are done so make sure to call where it is appropriate! Does not check to see if node is
    properly paren/bracketized so make sure of this before calling!

    **Returns:**
    - `bool`: Whether delimiters were removed or not (they may not be for an empty tuple).
    """

    # assert isinstance(self.a, Tuple)

    if not (body := getattr(self.a, field, None)):
        return False

    ln, col, end_ln, end_col = self.loc
    lines                    = self.root._lines

    if comma := next_find(self.root._lines, en_end_ln := (en := body[-1].f).end_ln, en_end_col := en.end_col,
                          end_ln, end_col, ','):  # need to leave trailing comma if its there
        en_end_ln, en_end_col  = comma
        en_end_col            += 1

    else:  # when no trailing comma need to make sure par is not separating us from an alphanumeric on either side, and if so then insert a space at the end before deleting the right par
        if end_col >= 2 and _re_delim_close_alnums.match(lines[end_ln], end_col - 2):
            self._put_src(' ', end_ln, end_col, end_ln, end_col, False, self)

    head_alnums = col and _re_delim_open_alnums.match(lines[ln], col - 1)  # if open has alnumns on both sides then insert space there too

    self._put_src(None, en_end_ln, en_end_col, end_ln, end_col, True, self)
    self._put_src(None, ln, col, (e0 := body[0].f).ln, e0.col, False)

    if head_alnums:  # but put after delete par to keep locations same
        self._put_src(' ', ln, col, ln, col, False)

    return True


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

    b0                  = block[0].f
    b0_ln, b0_col, _, _ = b0.bloc
    root                = self.root

    if not (colon := prev_find(root._lines, *b0._prev_bound(), b0_ln, b0_col, ':', True, comment=True, lcont=None)):  # must be there
        return

    if indent is None:
        indent = b0.get_indent()

    ln, col = colon

    self._put_src(['', indent], ln, col + 1, b0_ln, b0_col, False)


def _elif_to_else_if(self: fst.FST) -> None:
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


def _reparse_docstrings(self: fst.FST, docstr: bool | Literal['strict'] | None = None) -> None:
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


def _make_fst_and_dedent(self: fst.FST, indent: fst.FST | str, ast: AST, copy_loc: fstloc,
                         prefix: str = '', suffix: str = '',
                         put_loc: fstloc | None = None, put_lines: list[str] | None = None, *,
                         docstr: bool | Literal['strict'] | None = None,
                         ret_params_offset: bool = False) -> fst.FST | tuple[fst.FST, ParamsOffset]:
    if not isinstance(indent, str):
        indent = indent.get_indent()

    lines = self.root._lines
    fst_  = fst.FST(ast, lines, from_=self, lcopy=False)  # we use original lines for nodes offset calc before putting new lines

    fst_._offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix.encode()) - lines[copy_loc.ln].c2b(copy_loc.col))

    fst_._lines = fst_lines = self.get_src(*copy_loc, True)

    if suffix:
        fst_lines[-1] = bistr(fst_lines[-1] + suffix)

    if prefix:
        fst_lines[0] = bistr(prefix + fst_lines[0])

    if indent:
        fst_._dedent_lns(indent, skip=bool(copy_loc.col), docstr=docstr)  # if copy location starts at column 0 then we apply dedent to it as well (preceding comment or something)

    if put_loc:
        parsoff = self._put_src(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0
    else:
        parsoff = None

    return (fst_, parsoff) if ret_params_offset else fst_


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
        if prev := prev_find(lines, vend_ln, vend_col, end_ln, end_col, '!'):
            end_ln, end_col = prev

    src     = self.get_src(vend_ln, vend_col, end_ln, end_col)  # source from end of parenthesized value to end of FormattedValue or start of conversion or format_spec
    get_dbg = src and (m := _re_fval_expr_equals.match(src)) and m.end() == len(src)

    if not get_dbg and not get_val:
        return None, None, 0, 0

    if _HAS_FSTR_COMMENT_BUG:  # '#' characters inside strings erroneously removed as if they were comments
        lines = self.get_src(sln, scol + 1, end_ln, end_col, True)

        for i, l in enumerate(lines):
            m = re_line_end_cont_or_comment.match(l)  # always matches

            if (g := m.group(1)) and g.startswith('#'):  # line ends in comment, nuke it
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
                lns.update(multiline_str_continuation_lns(lines, *f.loc))

            elif isinstance(a, (JoinedStr, TemplateStr)):
                lns.update(multiline_fstr_continuation_lns(lines, *f.loc))

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

                m = re_line_end_cont_or_comment.match(l, c)  # always matches

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

@pyver(lt=12)  # override _get_fmtval_interp_strs if py too low
def _get_fmtval_interp_strs(self: fst.FST) -> tuple[str | None, str | None, int, int] | None:
    """Dummy because py < 3.12 doesn't have f-string location information."""

    return None


def _get_indentable_lns(self: fst.FST, skip: int = 0, *, docstr: bool | Literal['strict'] | None = None) -> set[int]:
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
    >>> from fst import *

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
                lns.difference_update(multiline_str_continuation_lns(lines, *f.loc))

        elif isinstance(a, (JoinedStr, TemplateStr)):
            lns.difference_update(multiline_fstr_continuation_lns(lines, *f.loc))

            walking.send(False)  # skip everything inside regardless, because it is evil

    return lns


def _modifying(self: fst.FST, field: str | Literal[False] = False, raw: bool = False) -> _Modifying:
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


def _touchall(self: fst.FST, parents: bool = False, self_: bool = True, children: bool = False) -> Self:
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


def _put_src(self: fst.FST, src: str | list[str] | None, ln: int, col: int, end_ln: int, end_col: int,
             tail: bool | None = ..., head: bool | None = True, exclude: fst.FST | None = None, *,
             offset_excluded: bool = True) -> ParamsOffset | None:
    """Put or delete new source to currently stored source, optionally offsetting all nodes for the change. Must
    specify `tail` as `True`, `False` or `None` to enable offset of nodes according to source put. `...` ellipsis
    value is used as sentinel for `tail` to mean don't offset. Otherwise `tail` and params which followed are passed
    to `self._offset()` with calculated offset location and deltas.

    **Returns:**
    - `(ln: int, col: int, dln: int, dcol_offset: int) | None`: If `tail` was not `...` then the calculated
        `offset()` parameters are returned for any potential followup offsetting. The `col` parameter in this case
        is returned as a byte offset so that `offset()` doesn't attempt to calculate it from already modified
        source."""

    ls = self.root._lines

    if is_del := src is None:
        lines = [bistr('')]
    elif isinstance(src, str):
        lines = [bistr(s) for s in src.split('\n')]
    else:
        lines = [bistr(s) for s in src]

    if tail is ...:
        parsoff = None

    else:
        parsoff = params_offset(ls, lines, ln, col, end_ln, end_col)

        self.root._offset(*parsoff, tail, head, exclude, offset_excluded=offset_excluded)

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

    return parsoff


def _offset(self: fst.FST, ln: int, col: int, dln: int, dcol_offset: int,
            tail: bool | None = False, head: bool | None = True, exclude: fst.FST | None = None, *,
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


def _indent_lns(self: fst.FST, indent: str | None = None, lns: set[int] | None = None, *,
                skip: int = 1, docstr: bool | Literal['strict'] | None = None) -> None:
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
    """

    if indent == '':
        return

    root = self.root

    if indent is None:
        indent = root.indent
    if docstr is None:
        docstr = self.get_option('docstr')

    if not ((lns := self._get_indentable_lns(skip, docstr=docstr)) if lns is None else lns):
        return

    lines       = root._lines
    dont_offset = set()

    for ln in lns:
        if l := lines[ln]:  # only indent non-empty lines
            lines[ln] = bistr(indent + l)
        else:
            dont_offset.add(ln)

    self._offset_lns(lns - dont_offset if dont_offset else lns, len(indent.encode()))
    self._reparse_docstrings(docstr)


def _dedent_lns(self: fst.FST, dedent: str | None = None, lns: set[int] | None = None, *,
                skip: int = 1, docstr: bool | Literal['strict'] | None = None) -> None:
    """Dedent all indentable lines specified in `lns` by removing `dedent` prefix and adjust node locations
    accordingly. If cannot dedent entire amount, will dedent as much as possible.

    **WARNING!** This does not offset parent nodes.

    **Parameters:**
    - `dedent`: The indentation string to remove from the beginning of each indentable line (if possible).
    - `lns`: A `set` of lines to apply dedentation to. If `None` then will be gotten from
        `_get_indentable_lns(skip=skip)`.
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in expected docstring positions are indentable. `None` means use default.
    - `skip`: If not providing `lns` then this value is passed to `_get_indentable_lns()`.
    """

    if dedent == '':
        return

    root = self.root

    if dedent is None:
        dedent = root.indent
    if docstr is None:
        docstr = self.get_option('docstr')

    if not ((lns := self._get_indentable_lns(skip, docstr=docstr)) if lns is None else lns):
        return

    lines        = root._lines
    ldedent      = len(dedent)
    dont_offset  = set()
    dcol_offsets = None

    def dedented(l: str, ldedent_: int) -> None:
        if dcol_offsets is not None:
            dcol_offsets[ln] = -ldedent_

        return bistr(l[ldedent_:])

    for ln in lns:
        if not (l := lines[ln]):  # don't offset anything on an empty line, normally nothing there but during slicing empty lines may mark start and end of slices
            dont_offset.add(ln)

        else:
            if l.startswith(dedent) or (lempty_start := re_empty_line_start.match(l).end()) >= ldedent:  # only full dedent non-empty lines which have dedent length leading space
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

    self._reparse_docstrings(docstr)


def _redent_lns(self: fst.FST, dedent: str | None = None, indent: str | None = None, lns: set[int] | None = None, *,
                skip: int = 1, docstr: bool | Literal['strict'] | None = None) -> None:
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
    - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
        multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
        in expected docstring positions are indentable. `None` means use default.
    - `skip`: If not providing `lns` then this value is passed to `_get_indentable_lns()`.
    """

    root = self.root

    if dedent is None:
        dedent = root.indent
    if indent is None:
        indent = root.indent

    if dedent == indent:
        return
    if not dedent:
        return self._indent_lns(indent, skip=skip, docstr=docstr)
    if not indent:
        return self._dedent_lns(indent, skip=skip, docstr=docstr)

    if docstr is None:
        docstr = self.get_option('docstr')

    if not ((lns := self._get_indentable_lns(skip, docstr=docstr)) if lns is None else lns):
        return

    lines        = root._lines
    ldedent      = len(dedent)
    lindent      = len(indent)
    dredent      = lindent - ldedent
    dont_offset  = set()
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
            if l.startswith(dedent) or (lempty_start := re_empty_line_start.match(l).end()) >= ldedent:  # only full dedent non-empty lines which have dedent length leading space
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

    self._reparse_docstrings(docstr)


@staticmethod
def _get_trivia_params(trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None = None,
                       neg: bool = False,
                       ) -> tuple[Literal['none', 'all', 'block'] | int,
                                  bool | int,
                                  bool,
                                  Literal['none', 'all', 'block', 'line'] | int,
                                  bool | int,
                                  bool,
                                  ]:
    """Convert options compact human representation to parameters usable for `_leading/trailing_trivia()`.

    This conversion is fairly loose and will accept shorthand '+/-#' for 'none+/-#'.

    **Parameters:**
    - `neg`: Whether to use `'-#'` suffix numbers or not (will still return `_neg` as `True` but `_space` will be 0).

    **Returns:**
    - (`lead_comments`, `lead_space`, `lead_neg`, `trail_comments`, `trail_space`, `trail_neg`): Two sets of parameters
        for the trivia functions along with the `_neg` indicators of whether the `_space` params came from negative
        space specifiers `'-#'` or not.
    """

    if isinstance(lead_comments := fst.FST.get_option('trivia'), tuple):
        lead_comments, trail_comments = lead_comments
    else:
        trail_comments = True

    if trivia is not None:
        if not isinstance(trivia, tuple):
            lead_comments = trivia

        else:
            if (t := trivia[0]) is not None:
                lead_comments = t
            if (t := trivia[1]) is not None:
                trail_comments = t

    lead_space = lead_neg = False

    if isinstance(lead_comments, bool):
        lead_comments = 'block' if lead_comments else 'none'

    elif isinstance(lead_comments, str):
        if (i := lead_comments.find('+')) != -1:
            lead_space    = int(n) if (n := lead_comments[i + 1:]) else True
            lead_comments = lead_comments[:i] or 'none'

        elif (i := lead_comments.find('-')) != -1:
            lead_neg      = True
            lead_space    = (int(n) if (n := lead_comments[i + 1:]) else True) if neg else 0
            lead_comments = lead_comments[:i] or 'none'

        assert lead_comments != 'line'

    trail_space = trail_neg = False

    if isinstance(trail_comments, bool):
        trail_comments = 'line' if trail_comments else 'none'

    elif isinstance(trail_comments, str):
        if (i := trail_comments.find('+')) != -1:
            trail_space    = int(n) if (n := trail_comments[i + 1:]) else True
            trail_comments = trail_comments[:i] or 'none'

        elif (i := trail_comments.find('-')) != -1:
            trail_neg      = True
            trail_space    = (int(n) if (n := trail_comments[i + 1:]) else True) if neg else 0
            trail_comments = trail_comments[:i] or 'none'

    return lead_comments, lead_space, lead_neg, trail_comments, trail_space, trail_neg
