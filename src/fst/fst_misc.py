"""Misc lower level FST methods."""

from ast import *
from ast import parse as ast_parse
from typing import Callable, Literal, Optional, Union

from .astutil import *

from .shared import (
    NodeTypeError, astfield, fstloc,
    BLOCK,
    HAS_DOCSTRING,
    Code,
    _next_src, _prev_src, _next_find, _prev_find, _next_pars, _prev_pars,
    _coerce_ast
)


def _make_tree_fst(ast: AST, parent: 'FST', pfield: astfield):
    """Recreate possibly non-unique AST nodes."""

    if not getattr(ast, 'f', None):  # if `.f` exists then this has already been done
        if isinstance(ast, (expr_context, unaryop, operator, boolop, cmpop)):  # ast.parse() reuses simple objects, we need all objects to be unique
            pfield.set(parent.a, ast := ast.__class__())

    return FST(ast, parent, pfield)


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

@staticmethod
def _normalize_code(code: Code, coerce: Literal['expr', 'exprish', 'mod'] | None = None, *, parse_params: dict = {},
                    ) -> 'FST':
    """Normalize code to an `FST` and coerce to a desired format if possible.

    If neither of these is requested then will convert to `ast.Module` if is `ast.Interactive` or return single
    expression node of `ast.Expression` or just return whatever the node currently is.

    **Parameters:**
    - `coerce`: What kind of coercion to apply (if any):
        - `'expr'`: Will return an `FST` with a top level `expr` `AST` node if possible, raise otherwise.
        - `'exprish'`: Same as `'expr'` but also some other expression-like nodes (for raw).
        - `'mod'`: Will return an `FST` with a top level `Module` `AST` node of the single statement or a wrapped
            expression in an `Expr` node. `ExceptHandler` and `match_case` nodes are considered statements here.
        - `None`: Will pull expression out of `Expression` and convert `Interactive` to `Module`, otherwise will return
            node as is, or as is parsed to `Module`.

    **Returns:**
    - `FST`: Compiled or coerced or just fixed up.
    """

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root FST')

        ast  = code.a
        rast = _coerce_ast(ast, coerce)

        if rast is ast:
            return code

        if f := getattr(rast, 'f', None):
            f._unmake_fst_parents()

        return FST(rast, lines=code._lines, from_=code)

    if isinstance(code, AST):
        return FST.fromast(_coerce_ast(code, coerce))  # TODO: WARNING! will not handle pure AST ExceptHandler or match_case

    if isinstance(code, str):
        src   = code
        lines = code.split('\n')

    else:  # isinstance(code, list):
        src   = '\n'.join(code)
        lines = code

    ast = ast_parse(src, **parse_params)

    if (is_expr := coerce == 'expr') or coerce == 'exprish':
        if not (ast := reduce_ast(ast, False)) or (is_expr and not isinstance(ast, expr)):
            raise NodeTypeError(f'expecting single {"expression" if is_expr else "expressionish"}')

    return FST(ast, lines=lines)


@staticmethod
def _new_empty_module(*, from_: Optional['FST'] = None) -> 'FST':
    return FST(Module(body=[], type_ignores=[]), lines=[bistr('')], from_=from_)


@staticmethod
def _new_empty_tuple(*, from_: Optional['FST'] = None) -> 'FST':
    ast = Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, lines=[bistr('()')], from_=from_)


@staticmethod
def _new_empty_list(*, from_: Optional['FST'] = None) -> 'FST':
    ast = List(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, lines=[bistr('[]')], from_=from_)


@staticmethod
def _new_empty_dict(*, from_: Optional['FST'] = None) -> 'FST':
    ast = Dict(keys=[], values=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return FST(ast, lines=[bistr('{}')], from_=from_)


@staticmethod
def _new_empty_set(only_ast: bool = False, lineno: int = 1, col_offset: int = 0, *,
                   from_: Optional['FST'] = None) -> Union['FST', AST]:
    ast = Set(elts=[
        Starred(value=Tuple(elts=[], ctx=Load(), lineno=lineno, col_offset=col_offset+2,
                            end_lineno=lineno, end_col_offset=col_offset+4),
                ctx=Load(), lineno=lineno, col_offset=col_offset+1, end_lineno=lineno, end_col_offset=col_offset+4)
    ], lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return ast if only_ast else FST(ast, lines=[bistr('{*()}')], from_=from_)


@staticmethod
def _new_empty_set_curlies(only_ast: bool = False, lineno: int = 1, col_offset: int = 0, *,
                           from_: Optional['FST'] = None) -> Union['FST', AST]:
    ast = Set(elts=[], lineno=lineno, col_offset=col_offset, end_lineno=lineno,
            end_col_offset=col_offset + 2)

    return ast if only_ast else FST(ast, lines=[bistr('{}')], from_=from_)


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


def _repr_tail(self: 'FST') -> str:
    try:
        loc = self.loc
    except Exception:  # maybe in middle of operation changing locations and lines
        loc = '????'

    self.touch(False, True, True)  # for debugging because we may have cached locs which would not have otherwise been cached during execution

    tail = ' ROOT' if self.is_root else ''

    return f'{tail} {loc[0]},{loc[1]} -> {loc[2]},{loc[3]}' if loc else tail


def _dump(self: 'FST', full: bool = False, indent: int = 2, cind: str = '', prefix: str = '',
          linefunc: Callable = print, compact: bool = False, eol: str = ''):
    tail = self._repr_tail()
    sind = ' ' * indent
    ast  = self.a

    if compact:
        if isinstance(ast, Name):
            linefunc(f'{cind}{prefix}Name {ast.id!r} {ast.ctx.__class__.__qualname__}{" .." * bool(tail)}{tail}'
                        f'{eol}')

            return

        if isinstance(ast, Constant):
            if ast.kind is None:
                linefunc(f'{cind}{prefix}Constant {ast.value!r}{" .." * bool(tail)}{tail}{eol}')
            else:
                linefunc(f'{cind}{prefix}Constant {ast.value!r} {ast.kind}{" .." * bool(tail)}{tail}{eol}')

            return

    linefunc(f'{cind}{prefix}{ast.__class__.__qualname__}{" .." * bool(tail)}{tail}{eol}')

    for name, child in iter_fields(ast):
        is_list = isinstance(child, list)

        if compact:
            if child is None and not full:
                continue

            if name == 'ctx':
                linefunc(f'{sind}{cind}.{name} {child.__class__.__qualname__ if isinstance(child, AST) else child}'
                            f'{eol}')

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
                    child.f._dump(full, indent, cind + sind, f'.{name} ', linefunc, compact, eol)
                else:
                    linefunc(f'{sind}{cind}.{name} {child!r}{eol}')

                continue

            if name == 'args' and isinstance(child, arguments):
                if child.posonlyargs or child.args or child.vararg or child.kwonlyargs or child.kwarg:
                    child.f._dump(full, indent, cind + sind, '.args ', linefunc, compact, eol)

                    continue

                elif not full:
                    continue

        if full or (child != []):
            linefunc(f'{sind}{cind}.{name}{f"[{len(child)}]" if is_list else ""}{eol}')

        if is_list:
            for i, ast in enumerate(child):
                if isinstance(ast, AST):
                    ast.f._dump(full, indent, cind + sind, f'{i}] ', linefunc, compact, eol)
                else:
                    linefunc(f'{sind}{cind}{i}] {ast!r}{eol}')

        elif isinstance(child, AST):
            child.f._dump(full, indent, cind + sind * 2, '', linefunc, compact, eol)
        else:
            linefunc(f'{sind}{sind}{cind}{child!r}{eol}')


def _prev_ast_bound(self: 'FST', with_loc: bool | Literal['all', 'own', 'allown'] = True) -> tuple[int, int]:
    """Get a prev bound for search after any ASTs for this object. This is safe to call for nodes that live inside
    nodes without their own locations if `with_loc='allown'`."""

    if prev := self.prev_step(with_loc, recurse_self=False):
        return prev.bloc[2:]

    return 0, 0


def _next_ast_bound(self: 'FST', with_loc: bool | Literal['all', 'own', 'allown'] = True) -> tuple[int, int]:
    """Get a next bound for search before any ASTs for this object. This is safe to call for nodes that live inside
    nodes without their own locations if `with_loc='allown'`."""

    if next := self.next_step(with_loc, recurse_self=False):
        return next.bloc[:2]

    return len(lines := self.root._lines) - 1, len(lines[-1])


def _lpars(self: 'FST', with_loc: bool | Literal['all', 'own', 'allown'] = True, *, exc_genexpr_solo: bool = False,
           ) -> tuple[int, int, int, int, int]:
    """Return the `ln` and `col` of the leftmost and ante-leftmost opening parentheses and the total number of
    opening parentheses. Doesn't take into account anything like enclosing argument parentheses, just counts. The
    leftmost bound used is the end of the previous sibling, or the start of that parent if there isn't one, or (0,0)
    if no parent.

    **Parameters:**
    - `with_loc`: Parameter to use for AST bound search. `True` normally or `'allown'` in special cases like
        searching for parentheses to figure out node location from children from `.loc` itself.
    - `exc_genexpr_solo`: If `True`, then will exclude left parenthesis of a single call argument generator
        expression if it is shared with the call() arguments enclosing parentheses.

    **Returns:**
    - `(ln, col, ante_ln, ante_col, npars)`: The leftmost and ante-leftmost positions and total count of opening
        parentheses encountered.
    """

    ret = _prev_pars(self.root._lines, *self._prev_ast_bound(with_loc), *self.bloc[:2])

    if self.is_solo_call_arg():  # special case single arg in a call so we must exclude the call arguments parentheses
        pars_ln, pars_col, _, _, npars = ret

        if exc_genexpr_solo and not npars and isinstance(self.a, GeneratorExp):  # npars == 0 indicates shared parentheses
            ln, col, _, _  = self.loc
            col           += 1

            return ln, col, ln, col, -1

        ret = _prev_pars(self.root._lines, pars_ln, pars_col + 1, *self.bloc[:2])  # exclude outermost par found from search

    return ret


def _rpars(self: 'FST', with_loc: bool | Literal['all', 'own', 'allown'] = True, *, exc_genexpr_solo: bool = False,
           ) -> tuple[int, int, int, int, int]:
    """Return the `end_ln` and `end_col` of the rightmost and ante-rightmost closing parentheses and the total
    number of closing parentheses. Doesn't take into account anything like enclosing argument parentheses, just
    counts. The rightmost bound used is the start of the next sibling, or the end of that parent if there isn't one,
    or the end of `self.root._lines`.

    **Parameters:**
    - `with_loc`: Parameter to use for AST bound search. `True` normally or `'allown'` in special cases like
        searching for parentheses to figure out node location from children from `.loc` itself.
    - `exc_genexpr_solo`: If `True`, then will exclude left parenthesis of a single call argument generator
        expression if it is shared with the call() arguments enclosing parentheses.

    **Returns:**
    - `(end_ln, end_col, ante_end_ln, ante_end_col, npars)`: The rightmost and ante-rightmost positions and total
        count of closing parentheses encountered.
    """

    ret = _next_pars(self.root._lines, *self.bloc[2:], *self._next_ast_bound(with_loc))

    if self.is_solo_call_arg():  # special case single arg in a call so we must exclude the call arguments parentheses
        pars_end_ln, pars_end_col, _, _, npars = ret

        if exc_genexpr_solo and not npars and isinstance(self.a, GeneratorExp):  # npars == 0 indicates shared parentheses
            _, _, end_ln, end_col  = self.loc
            end_col               -= 1

            return end_ln, end_col, end_ln, end_col, -1

        ret = _next_pars(self.root._lines, *self.bloc[2:], pars_end_ln, pars_end_col - 1)  # exclude outermost par found from search

    return ret


def _loc_block_header_end(self: 'FST', ret_bound: bool = False) -> fstloc | tuple[int, int] | None:
    """Return location of the end of the block header line(s) for block node, just past the ':', or None if `self`
    is not a block header node.

    **Parameters:**
    - `ret_bound`: If `False` then just returns the end position. `True` means return the range used for the search,
        which includes a start at the end of the last child node in the block header or beginning of the block node if
        no child nodes in header.
    """

    ln, col, end_ln, end_col = self.loc

    if child := last_block_opener_child(a := self.a):
        if loc := child.f.loc:  # because of empty function def arguments
            _, _, cend_ln, cend_col = loc

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
    """Get location of `operator`, `unaryop` or `cmpop` from source if possible. `boolop` is not done at all because
    a single operator can be in multiple location in a `BoolOp` and we want to be consistent."""

    ast = self.a

    if not (parent := self.parent) or not (op := OPCLS2STR.get(ast.__class__)):
        return None

    lines   = self.root._lines
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


def _loc_comprehension(self: 'FST') -> fstloc | None:
    """`comprehension` location from children. Called from `.loc`."""

    ast   = self.a
    first = ast.target.f
    last  = self.last_child()
    lines = self.root._lines

    prev = prev.loc if (prev := self.prev_step('allown', recurse_self=False)) else (0, 0)

    if start := _prev_find(lines, prev[-2], prev[-1], first.ln, first.col, 'for'):  # prev.bend_ln, prev.bend_col
        start_ln, start_col = start

        if ast.is_async and (start := _prev_find(lines, prev[-2], prev[-1], start_ln, start_col, 'async')):
            start_ln, start_col = start

    else:
        start_ln, start_col, _, _, nlpars = first._lpars('allown')  # 'allown' so it doesn't recurse into calling `.loc`

        if not nlpars:  # not really needed, but juuust in case
            start_ln  = first.bln
            start_col = first.bcol

    end_ln, end_col, ante_end_ln, ante_end_col, nrpars = last._rpars('allown')

    if not nrpars:
        end_ln  = last.bend_ln
        end_col = last.bend_col

    elif ((parent := self.parent) and isinstance(parent.a, GeneratorExp) and  # correct for parenthesized GeneratorExp
        self.pfield.idx == len(parent.a.generators) - 1
    ):
        end_ln  = ante_end_ln
        end_col = ante_end_col

    return fstloc(start_ln, start_col, end_ln, end_col)


def _loc_arguments(self: 'FST') -> fstloc | None:
    """`arguments` location from children. Called from `.loc`. Returns `None` when there are no arguments."""

    if not (first := self.first_child()):
        return None

    ast   = self.a
    last  = self.last_child()
    lines = self.root._lines

    start_ln, start_col, ante_start_ln, ante_start_col, _ = first._lpars('allown')  # 'allown' so it doesn't recurse into calling `.loc`
    end_ln, end_col, ante_end_ln, ante_end_col, _         = last._rpars('allown')

    if has_args_pars := (parent := self.parent) and isinstance(parent.a, (FunctionDef, AsyncFunctionDef)):
        start_ln  = ante_start_ln
        start_col = ante_start_col

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

    if ((code := _next_src(lines, end_ln, end_col, len(lines) - 1, len(lines[-1])))  # trailing comma
        and code.src.startswith(',')
    ):
        end_ln, end_col, _  = code
        end_col            += 1

    elif has_args_pars:
        end_ln  = ante_end_ln
        end_col = ante_end_col

    if leading_stars:  # find star to the left, we know it exists so we don't check for None return
        start_ln, start_col = _prev_find(lines, *first._prev_ast_bound('allown'), start_ln, start_col, leading_stars)

    if trailing_slash:
        end_ln, end_col  = _next_find(lines, end_ln, end_col, len(lines), 0x7fffffffffffffff, '/')  # must be there
        end_col         += 1

    return fstloc(start_ln, start_col, end_ln, end_col)


def _loc_arguments_empty(self: 'FST') -> fstloc:
    """`arguments` location for empty arguments ONLY! DO NOT CALL FOR NONEMPTY ARGUMENTS!"""

    if not (parent := self.parent):
        return fstloc(0, 0, len(ls := self._lines), len(ls[-1]))  # parent=None means we are root

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


def _loc_withitem(self: 'FST') -> fstloc | None:
    """`withitem` location from children. Called from `.loc`."""

    ast    = self.a
    ce     = ast.context_expr.f
    ce_loc = ce.loc

    if not (ov := ast.optional_vars):
        return ce_loc

    ov     = ov.f
    ov_loc = ov.loc

    pars_end_ln, pars_end_col, ante_end_ln, ante_end_col, nrpars = ce._rpars('allown')  # 'allown' so it doesn't recurse into calling `.loc`

    if not nrpars:
        ln, col = ce_loc[:2]

    else:
        pars_ln, pars_col, ante_ln, ante_col, nlpars = ce._lpars('allown')

        ln, col = (pars_ln, pars_col) if nlpars == nrpars else (ante_ln, ante_col)

    pars_ln, pars_col, ante_ln, ante_col, nlpars = ov._lpars('allown')

    if not nlpars:
        end_ln, end_col = ov_loc[2:]

    else:
        pars_end_ln, pars_end_col, ante_end_ln, ante_end_col, nrpars = ov._rpars('allown')

        end_ln, end_col = (pars_end_ln, pars_end_col) if nrpars == nlpars else (ante_end_ln, ante_end_col)

    return fstloc(ln, col, end_ln, end_col)


def _loc_match_case(self: 'FST') -> fstloc | None:
    """`match_case` location from children. Called from `.loc`."""

    ast   = self.a
    first = ast.pattern.f
    last  = self.last_child()
    lines = self.root._lines

    start = _prev_find(lines, 0, 0, first.ln, first.col, 'case')  # we can use '0, 0' because we know "case" starts on a newline

    if ast.body:
        return fstloc(*start, last.bend_ln, last.bend_col)

    end_ln, end_col = _next_find(lines, last.bend_ln, last.bend_col, len(lines) - 1, len(lines[-1]), ':')  # special case, deleted whole body, end must be set to just past the colon (which MUST follow somewhere there)

    return fstloc(*start, end_ln, end_col + 1)


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

    try:
        del self._loc, self._bloc  # _bloc only exists if _loc does
    except AttributeError:
        pass

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

    if lines[ln].startswith('elif', col) and (not (parent := self.parent) or not
        (isinstance(parenta := parent.a, If) and self.pfield == ('orelse', 0) and len(parenta.orelse) == 1 and
            self.a.col_offset == parenta.col_offset)
    ):
        self.put_src(None, ln, col, ln, col + 2, False)


def _fix_block_del_last_child(self: 'FST', bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int):
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


def _fix(self: 'FST', inplace: bool = True) -> 'FST':
    """This is really a maybe fix source and `ctx` values for cut or copied nodes (to make subtrees parsable if the
    source is not after the operation). Normally this is called by default on newly cut / copied individual nodes.
    Possibly reparses in order to verify expressions. If cannot fix or ast is not parsable by itself then ast will
    be unchanged. Is meant to be a quick fix after a cut or copy operation, not full check, for that use
    `is_parsable()` or `verify()` depending on need. Possible source changes are `elif` to `if` and parentheses
    where needed and commas for singleton tuples.

    **Parameters:**
    - `inplace`: If `True` then changes will be made to `self`. If `False` then `self` may be returned if no changes
        made, otherwise a modified copy is returned.

    **Returns:**
    - `self` if unchanged or modified in place or a new `FST` object otherwise.
    """

    if not self.is_root:
        raise RuntimeError('can only be called on root node')

    if not (loc := self.loc):
        return self

    ln, col, end_ln, end_col = loc

    ast   = self.a
    lines = self._lines

    # if / elif statement

    if isinstance(ast, If):
        if (l := lines[ln]).startswith('if', col):
            return self

        assert l.startswith('elif', col)

        if not inplace:
            self = FST(copy_ast(ast), lines=(lines := lines[:]), from_=self)

        self.offset(ln, col + 2, 0, -2)

        lines[ln] = bistr((l := lines[ln])[:col] + l[col + 2:])

    # expression maybe parenthesize and proper ctx (Load)

    elif (isinstance(ast, expr)):
        if not self.is_parsable():  # may be Slice or Starred
            return self

        need_paren = None

        if is_tuple := isinstance(ast, Tuple):
            if self._is_parenthesized_seq():
                need_paren = False

            elif (not (elts := ast.elts) or any(isinstance(e, NamedExpr) for e in elts) or (len(elts) == 1 and (
                    not (code := _next_src(lines, (f0 := elts[0].f).end_ln, f0.end_col, end_ln, end_col, False, None))
                    or  # if comma not on logical line then definitely need to add parens, if no comma then the parens are incidental but we want that code path for adding the singleton comma
                    not code.src.startswith(',')))):
                need_paren = True

        elif (isinstance(ast, (Name, List, Set, Dict, ListComp, SetComp, DictComp, GeneratorExp)) or
                ((code := _prev_src(self.root._lines, 0, 0, self.ln, self.col)) and code.src.endswith('('))):  # is parenthesized?
            need_paren = False

        elif isinstance(ast, (NamedExpr, Yield, YieldFrom)):  # , Await
            need_paren = True

        elif end_ln == ln:
            need_paren = False

        if need_paren is None:
            try:
                a = ast_parse(src := self.src, mode='eval', **self.parse_params)

            except SyntaxError:  # if expression not parsing then try parenthesize
                tail = (',)' if is_tuple and len(ast.elts) == 1 and lines[end_ln][end_col - 1] != ',' else ')')  # WARNING! this won't work for expressions followed by comments, but all comments should be followed by a newline in normal operation

                try:
                    a = ast_parse(f'({src}{tail}', mode='eval', **self.parse_params)
                except SyntaxError:
                    return self

                if not inplace:
                    lines = lines[:]

                lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col]}{tail}{l[end_col:]}')
                lines[ln]     = bistr(f'{(l := lines[ln])[:col]}({l[col:]}')

            else:
                if compare_asts(a.body, ast, locs=True, type_comments=True, recurse=False):  # only top level compare needed for `ctx` and structure check
                    return self

                if not inplace:
                    lines = lines[:]

            a = a.body  # we know parsed to an Expression but original was not an Expression

            if not inplace:
                return FST(a, lines=lines, from_=self)

            self._set_ast(a)

            return self

        need_ctx = set_ctx(ast, Load, doit=False)

        if (need_ctx or need_paren) and not inplace:
            ast = copy_ast(ast)

            if need_ctx:
                set_ctx(ast, Load)

            lines = lines[:]
            self  = FST(ast, lines=lines, from_=self)

        elif need_ctx:
            set_ctx(ast, Load)

            self._make_fst_tree()  # TODO: this is quick HACK fix, redo _fix()

        if need_paren:
            lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col]}){l[end_col:]}')
            lines[ln]     = bistr(f'{(l := lines[ln])[:col]}({l[col:]}')

            self.offset(ln, col, 0, 1)

            if is_tuple:
                ast.col_offset     -= 1
                ast.end_col_offset += 1

            self._touch()

            if is_tuple:
                self._maybe_add_singleton_tuple_comma(False)

    return self


def _is_parenthesized_seq(self: 'FST', field: str = 'elts', lpar: str = '(', rpar: str = ')') -> bool | None:
    """Whether `self` is a parenthesized sequence of `field` or not. Functions as `is_parenthesized_tuple()` if
    already know is a Tuple. Other use is for `MatchSequence`, whether parenthesized or bracketed."""

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

    nparens = _next_pars(lines, self_ln, self_col, self_end_ln, self_end_col, lpar)[-1]  # yes, we use _next_pars() to count opening parens because we know conditions allow it

    if not nparens:
        return False

    nparens -= _next_pars(lines, f0_end_ln, f0_end_col, self_end_ln, self_end_col, rpar)[-1]

    return nparens > 0  # don't want to fiddle with checking if f0 is a parenthesized tuple


def _parenthesize_grouping(self: 'FST', whole: bool = True):
    """Parenthesize anything with non-node grouping parentheses. Just adds text parens around node adjusting parent
    locations but not the node itself.

    **Parameters:**
    - `whole`: If at root then parenthesize whole source instead of just node.
    """

    ln, col, end_ln, end_col = self.wbloc if whole else self.bloc

    self.put_src([')'], end_ln, end_col, end_ln, end_col, True, True, self, offset_excluded=False)
    self.offset(*self.put_src(['('], ln, col, ln, col, False, False, self, offset_excluded=False))


def _parenthesize_tuple(self: 'FST', whole: bool = True):
    """Parenthesize an unparenthesized tuple, adjusting tuple location for added parentheses.

    WARNING! No checks are done so don't call on anything other than an unparenthesized Tuple!

    **Parameters:**
    - `whole`: If at root then parenthesize whole source instead of just node.
    """

    # assert isinstance(self.a, Tuple)

    ln, col, end_ln, end_col = self.wbloc if whole else self.loc

    self.put_src([')'], end_ln, end_col, end_ln, end_col, True, False, self)

    lines            = self.root._lines
    a                = self.a
    a.end_lineno     = end_ln + 1  # yes this can change
    a.end_col_offset = lines[end_ln].c2b(end_col + 1)  # can't count on this being set by put_src() because end of `whole` could be past end of tuple

    self.offset(*self.put_src(['('], ln, col, ln, col, False, False, self), self_=False)

    a.lineno     = ln + 1
    a.col_offset = lines[ln].c2b(col)  # ditto on the `whole` thing


def _unparenthesize_grouping(self: 'FST', *, inc_genexpr_solo: bool = False) -> bool:
    """Remove grouping parentheses from anything. Just remove text parens around node and everything between them
    and node adjusting parent locations but not the node itself.

    **Returns:**
    - `bool`: Whether parentheses were removed or not (only removed if present to begin with and removable).
    """

    pars_loc, npars = self.pars(ret_npars=True)
    genexpr_solo    = inc_genexpr_solo and self.is_solo_call_arg_genexpr()

    if not npars and not genexpr_solo:
        return False

    ln , col,  end_ln,  end_col  = self.bloc
    pln, pcol, pend_ln, pend_col = pars_loc

    if genexpr_solo:  # special case merge solo argument GeneratorExp parentheses with call argument parens
        lines                    = self.root._lines
        _, _, cend_ln, cend_col  = self.parent.func.loc
        pln, pcol                = _prev_find(lines, cend_ln, cend_col, pln, pcol, '(')  # it must be there
        pend_ln, pend_col        = _next_find(lines, pend_ln, pend_col, len(lines) - 1, len(lines[-1]), ')')  # ditto
        pend_col                += 1

    self.put_src(None, end_ln, end_col, pend_ln, pend_col, True, self)
    self.put_src(None, pln, pcol, ln, col, False)

    return True


def _unparenthesize_tuple(self: 'FST') -> bool:
    """Unparenthesize a parenthesized tuple, adjusting tuple location for removed parentheses. Will not
    unparenthesize an empty tuple. Removes everything between the parentheses and the actual tuple.

    WARNING! No checks are done so don't call on anything other than a parenthesized Tuple!

    **Returns:**
    - `bool`: Whether parentheses were removed or not (they may not be for an empty tuple).
    """

    if not (elts := self.a.elts):
        return False

    ln, col, end_ln, end_col = self.loc

    if comma := _next_find(self.root._lines, en_end_ln := (en := elts[-1].f).end_ln, en_end_col := en.end_col,
                           end_ln, end_col, ','):  # need to leave trailing comma if its there
        en_end_ln, en_end_col  = comma
        en_end_col            += 1

    self.put_src(None, en_end_ln, en_end_col, end_ln, end_col, True, self)
    self.put_src(None, ln, col, (e0 := elts[0].f).ln, e0.col, False)

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

    if not (colon := _prev_find(root._lines, *b0._prev_ast_bound(), b0_ln, b0_col, ':', True,
                                comment=True, lcont=None)):
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
    fst   = FST(ast, lines=lines, from_=self)  # we use original lines for nodes offset calc before putting new lines

    fst.offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix.encode()) - lines[copy_loc.ln].c2b(copy_loc.col))

    fst._lines = fst_lines = self.get_src(*copy_loc, True)

    if suffix:
        fst_lines[-1] = bistr(fst_lines[-1] + suffix)

    if prefix:
        fst_lines[0] = bistr(prefix + fst_lines[0])

    fst.dedent_lns(indent, skip=bool(copy_loc.col), docstr=docstr)  # if copy location starts at column 0 then we apply dedent to it as well (preceding comment or something)

    if put_loc:
        self.put_src(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0

    return fst


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]

from .fst import FST
