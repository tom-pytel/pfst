"""Siblings, children and walk, all in syntactic order.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from typing import Callable, Container, Generator, Literal

from . import fst

from .asttypes import (
    ASTS_LEAF_EXPR_CONTEXT,
    ASTS_LEAF_BOOLOP,
    ASTS_LEAF_OPERATOR,
    ASTS_LEAF_UNARYOP,
    ASTS_LEAF_CMPOP,
    ASTS_LEAF_FUNCDEF,
    ASTS_LEAF_COMP,
    AST,
    AsyncFunctionDef,
    ClassDef,
    DictComp,
    FunctionDef,
    GeneratorExp,
    Lambda,
    ListComp,
    NamedExpr,
    ParamSpec,
    SetComp,
    TypeVar,
    TypeVarTuple,
    arg,
    arguments,
    comprehension,
    expr,
)

from .astutil import last_block_header_child, syntax_ordered_children
from .traverse_next import NEXT_FUNCS
from .traverse_prev import PREV_FUNCS


_ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP          =  ASTS_LEAF_EXPR_CONTEXT | ASTS_LEAF_BOOLOP
_ASTS_LEAF_EXPR_CONTEXT_OR_OP_OR_ARGUMENTS = (_ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP | ASTS_LEAF_OPERATOR |
                                              ASTS_LEAF_UNARYOP | ASTS_LEAF_CMPOP | {arguments})


def _check_all_param(fst_: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]]) -> bool:
    """Check 'all' parameter condition on node. Safe for low level because doesn't use `.loc` calculation machinery."""

    if all is True:
        return True

    if all is False:
        return (
            fst_.a.__class__ not in _ASTS_LEAF_EXPR_CONTEXT_OR_OP_OR_ARGUMENTS
            or ((a := fst_.a).__class__ is arguments
                and (True if (a.args or a.vararg or a.kwonlyargs or a.kwarg or a.posonlyargs) else False)
        ))

    if all == 'loc':
        return fst_.a.__class__ not in _ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP

    if all.__class__ is type and issubclass(all, AST):
        return fst_.a.__class__ is all

    return fst_.a.__class__ in all


def _all_param_func(
    all: bool | Literal['loc'] | type[AST] | Container[type[AST]] | Callable[[fst.FST], object]
) -> Callable[[fst.FST], object]:
    """Create a standalone function to check an `FST` against the given value of `all` parameter. Unlike
    `_check_all_param()` this can also accept a `Callable` for an external checker, which is returned unchanged in
    case `all` is one of these."""

    if all is True:
        return lambda fst_: True

    if all is False:
        return lambda fst_: (
            fst_.a.__class__ not in _ASTS_LEAF_EXPR_CONTEXT_OR_OP_OR_ARGUMENTS
            or ((a := fst_.a).__class__ is arguments
                and (True if (a.args or a.vararg or a.kwonlyargs or a.kwarg or a.posonlyargs) else False)
        ))

    if all == 'loc':
        return lambda fst_: fst_.a.__class__ not in _ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP

    if all.__class__ is type and issubclass(all, AST):
        return lambda fst_: fst_.a.__class__ is all

    if not callable(all):
        return lambda fst_: fst_.a.__class__ in all

    return all


# ......................................................................................................................

class _ScopeContext:
    walk_root: fst.FST
    all: bool | Literal['loc'] | type[AST] | Container[type[AST]] | Callable[[fst.FST], object]
    back: bool
    check_all_param: Callable[[fst.FST], object]

    is_def: bool  ; """Scope is a `FunctionDef`, `AsyncFunctionDef` or `ClassDef`."""
    scope_args: arguments | None  ; """Scope arguments node from a funcdef."""
    scope_first_iter: expr | None  ; """Scope first generator iterator node from a Comp."""

    stack: list[AST]

    def __init__(
        self,
        walk_root: fst.FST,
        all: bool | Literal['loc'] | type[AST] | Container[type[AST]] | Callable[[fst.FST], object],
        back: bool,
        check_all_param: Callable[[fst.FST], object],
        is_def: bool = False,
        scope_args: arguments | None = None,
        scope_first_iter: expr | None = None,
    ) -> None:
        self.walk_root = walk_root
        self.all = all
        self.back = back
        self.check_all_param = check_all_param
        self.is_def = is_def
        self.scope_args = scope_args
        self.scope_first_iter = scope_first_iter

    @staticmethod
    def create(
        walk_root: fst.FST,
        all: bool | Literal['loc'] | type[AST] | Container[type[AST]] | Callable[[fst.FST], object],
        back: bool,
        check_all_param: Callable[[fst.FST], object],
        ast: AST,
    ) -> tuple[_ScopeContext, list[AST] | None]:
        """Create top level scope context data from top level node. Will return initial list of `AST` nodes to walk or
        `None` if should be created normally."""

        ast_cls = ast.__class__
        stack = None
        scope_args = None
        scope_first_iter = None

        if (is_def := (ast_cls in ASTS_LEAF_FUNCDEF)) or ast_cls is Lambda:
            scope_args = ast.args  # will need these in the loop to exclude annotations and defaults

            if back:
                stack = []

                if type_params := getattr(ast, 'type_params', None):
                    stack.extend(type_params)

                stack.append(scope_args)  # this is so that the arguments node is included in the scope walk, could skip it and just do the args themselves but arguments node might be useful for signaling args of scope

                if is_def:
                    stack.extend(ast.body)
                else:
                    stack.append(ast.body)

            else:
                stack = ast.body[::-1] if is_def else [ast.body]

                stack.append(scope_args)

                if type_params := getattr(ast, 'type_params', None):
                    stack.extend(type_params[::-1])

        elif ast_cls is ClassDef:
            is_def = True  # for handling exclusion of type_params annotations and default_values from this walk

            if back:
                stack = []

                if type_params := getattr(ast, 'type_params', None):  # getattr() because we may be pre py 3.12
                    stack.extend(type_params)

                stack.extend(ast.body)

            else:
                stack = ast.body[::-1]

                if type_params := getattr(ast, 'type_params', None):
                    stack.extend(type_params[::-1])

        elif (is_elt := (ast_cls in (ListComp, SetComp, GeneratorExp))) or ast_cls is DictComp:
            if back:
                stack = ([ast.elt] if is_elt else [ast.key, ast.value]) + (generators := ast.generators)
            else:
                stack = (generators := ast.generators)[::-1] + ([ast.elt] if is_elt else [ast.value, ast.key])

            scope_first_iter = generators[0].iter if generators else None  # maybe the user deleted all generators

        scope_ctx = _ScopeContext(walk_root, all, back, check_all_param, is_def, scope_args, scope_first_iter)

        return scope_ctx, stack

    def stack_funcdef(self, ast: AST, stack: list[AST]) -> bool:
        """Individual scope walk function for nodes which need special treatement during scope walk. Returns list of
        child nodes allowed to be walked or a generator which will walk them in the case of a Comp.

        **Returns:**
        - `bool`: Indicates whether the function updated the stack according to special scope rules. If this is the case
            then the main loop should not add all children to the walk stack as it does noramlly.
        """

        args = ast.args

        if self.back:
            stack.extend(ast.decorator_list)

            for tp in getattr(ast, 'type_params', ()):  # type parameters
                if a := getattr(tp, 'bound', None):
                    stack.append(a)
                if a := getattr(tp, 'default_value', None):
                    stack.append(a)

            nonkwargs = args.posonlyargs + args.args  # posonly and normal args, interleave annotations with defaults
            defaults = args.defaults[:]
            defaults[0:0] = [None] * (len(nonkwargs) - len(defaults))

            for arg_, dflt in zip(nonkwargs, defaults, strict=True):
                if ann := arg_.annotation:
                    stack.append(ann)
                if dflt:
                    stack.append(dflt)

            if (vararg := args.vararg) and (ann := vararg.annotation):
                stack.append(ann)

            for arg_, dflt in zip(args.kwonlyargs, args.kw_defaults, strict=True):  # kwonly args and defaults
                if ann := arg_.annotation:
                    stack.append(ann)
                if dflt:
                    stack.append(dflt)

            if (kwarg := args.kwarg) and (ann := kwarg.annotation):
                stack.append(ann)

            if returns := ast.returns:
                stack.append(returns)

        else:  # forward
            if returns := ast.returns:
                stack.append(returns)

            if (kwarg := args.kwarg) and (ann := kwarg.annotation):
                stack.append(ann)

            for arg_, dflt in reversed(list(zip(args.kwonlyargs, args.kw_defaults, strict=True))):  # kwonly args and defaults
                if dflt:
                    stack.append(dflt)
                if ann := arg_.annotation:
                    stack.append(ann)

            if (vararg := args.vararg) and (ann := vararg.annotation):
                stack.append(ann)

            nonkwargs = args.posonlyargs + args.args
            defaults = args.defaults[:]
            defaults[0:0] = [None] * (len(nonkwargs) - len(defaults))

            for arg_, dflt in reversed(list(zip(nonkwargs, defaults, strict=True))):  # posonly and normal args
                if dflt:
                    stack.append(dflt)
                if ann := arg_.annotation:
                    stack.append(ann)

            for tp in getattr(ast, 'type_params', ())[::-1]:  # type parameters
                if a := getattr(tp, 'default_value', None):
                    stack.append(a)
                if a := getattr(tp, 'bound', None):
                    stack.append(a)

            stack.extend(ast.decorator_list[::-1])

        return True

    def stack_ClassDef(self, ast: AST, stack: list[AST]) -> bool:
        """See `walk_funcdef()`."""

        if self.back:
            stack.extend(ast.decorator_list)

            for tp in getattr(ast, 'type_params', ()):  # type parameters
                if a := getattr(tp, 'bound', None):
                    stack.append(a)
                if a := getattr(tp, 'default_value', None):
                    stack.append(a)

            stack.extend(ast.bases)
            stack.extend(ast.keywords)

        else:  # forward
            stack.extend(ast.keywords[::-1])
            stack.extend(ast.bases[::-1])

            for tp in getattr(ast, 'type_params', ())[::-1]:  # type parameters
                if a := getattr(tp, 'default_value', None):
                    stack.append(a)
                if a := getattr(tp, 'bound', None):
                    stack.append(a)

            stack.extend(ast.decorator_list[::-1])

        return True

    def stack_Lambda(self, ast: AST, stack: list[AST], no_back: bool = False) -> bool:
        """See `walk_funcdef()`."""

        args = ast.args

        if no_back or self.back:
            stack.extend(args.defaults)
            stack.extend(args.kw_defaults)
        else:
            stack.extend(args.kw_defaults[::-1])
            stack.extend(args.defaults[::-1])

        return True

    def stack_arguments(self, ast: AST, stack: list[AST]) -> bool:
        """See `walk_funcdef()`. Exclude defaults and kw_defaults from walk, ast is top-level scope arguments."""

        if ast is not self.scope_args:
            return False

        if self.back:
            stack.extend(ast.posonlyargs)
            stack.extend(ast.args)

            if vararg := ast.vararg:
                stack.append(vararg)

            stack.extend(ast.kwonlyargs)

            if kwarg := ast.kwarg:
                stack.append(kwarg)

        else:
            if kwarg := ast.kwarg:
                stack.append(kwarg)

            stack.extend(ast.kwonlyargs[::-1])

            if vararg := ast.vararg:
                stack.append(vararg)

            stack.extend(ast.args[::-1])
            stack.extend(ast.posonlyargs[::-1])

        return True

    def stack_arg(self, ast: AST, stack: list[AST]) -> bool:
        """See `walk_funcdef()`."""

        if ast.f.parent.a is self.scope_args:  # if arg part of top-level node args then don't recurse
            return True

        return False

    def stack_type_param(self, ast: AST, stack: list[AST]) -> bool:
        """See `walk_funcdef()`."""

        if self.is_def and ast.f.parent is self.walk_root:  # don't recurse for type annotations and defaults in top-level node
            return True

        return False

    def stack_comprehension(self, ast: AST, stack: list[AST]) -> bool:
        """See `walk_funcdef()`. This only comes from `walk_root` Comp, not ones encountered in a Comp here."""

        if self.back:
            stack.append(ast.target)

            if (a := ast.iter) is not self.scope_first_iter:
                stack.append(a)

            if a := ast.ifs:
                stack.extend(a)

        else:
            if a := ast.ifs:
                stack.extend(a)

            if (a := ast.iter) is not self.scope_first_iter:
                stack.append(a)

            stack.append(ast.target)

        return True

    def walk_Comp(self, ast: AST) -> Generator[fst.FST, bool, None]:
        """See `walk_funcdef()`. This gets messy if the first generator iterator is a scope itself."""

        fst_ = ast.f
        all = self.all
        back = self.back
        check_all_param = self.check_all_param
        first_iter = ast.generators[0].iter

        gen = fst_.walk(all, self_=False, back=back)  # no scope=True here because we do it manually

        for f in gen:  # we want to return all NamedExpr.target and first top-level .iter, yeah, its ugly
            a = f.a

            if a is first_iter:  # first generator iterator is in parent scope
                subrecurse = 1  # wouldn't be here if recurse is not True, 1 to differentiate from True

                while (sent := (yield f)) is not None:
                    subrecurse = sent

                if subrecurse is True:  # user did send(True) so walk unconditionally
                    yield from f.walk(all, self_=False, back=back)  # if the user did send(True) (subrecurse=True) then we want to recurse uncondintionally (scope=False), otherwise subrecurse=1 and continue walking with scope=True

                elif subrecurse:  # user didn't send anything, still need to apply scope rules and this node could be a scope
                    a_cls = a.__class__

                    if a_cls in ASTS_LEAF_COMP:  # this is feasible to be there
                        yield from self.walk_Comp(a)  # the Comprehension is one scope down but its first iterator is one scope up from that, so same level as this Comprehension, rules are the same

                    else:
                        if a_cls is Lambda:  # silly thing to be there, but we cover it
                            self.stack_Lambda(a, asts := [], True)  # no_back=True because it will be reversed as needed in the walk over the asts
                        else:
                            asts = None

                        yield from f.walk(all, self_=False, scope=True, back=back, asts=asts)

                gen.send(False)  # we processed this node here so don't recurse into it

            elif (  # all NamedExpr.targets are in parent scope
                f.parent.a.__class__ is NamedExpr
                and f.pfield.name == 'target'  # a.__class__ is Name
            ):
                subrecurse = True

                while (sent := (yield f)) is not None:
                    subrecurse = sent

                if subrecurse and check_all_param(f := a.ctx.f):  # truly pedantic, but maybe the user really really really wants that .ctx?
                    while (yield f) is not None:  # eat all the user's send()s
                        pass

                gen.send(False)  # we processed this node here so don't recurse into it

_SCOPE_WALK_FUNCS = {  # the boolean indicates whether it is a normal function or a generator
    FunctionDef:      (_ScopeContext.stack_funcdef, False),
    AsyncFunctionDef: (_ScopeContext.stack_funcdef, False),
    ClassDef:         (_ScopeContext.stack_ClassDef, False),
    Lambda:           (_ScopeContext.stack_Lambda, False),
    arguments:        (_ScopeContext.stack_arguments, False),
    arg:              (_ScopeContext.stack_arg, False),
    TypeVar:          (_ScopeContext.stack_type_param, False),
    ParamSpec:        (_ScopeContext.stack_type_param, False),
    TypeVarTuple:     (_ScopeContext.stack_type_param, False),
    comprehension:    (_ScopeContext.stack_comprehension, False),
    ListComp:         (_ScopeContext.walk_Comp, True),
    SetComp:          (_ScopeContext.walk_Comp, True),
    DictComp:         (_ScopeContext.walk_Comp, True),
    GeneratorExp:     (_ScopeContext.walk_Comp, True),
}  # fmt: skip


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _next_bound(
    self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = 'loc'
) -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object within parent. If no siblings found after
    self then return end of parent. If no parent then return end of source."""

    if next := self.next(all):
        return next.bloc[:2]
    elif parent := self.parent:
        return parent.bloc[2:]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound(
    self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = 'loc'
) -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object within parent. If no siblings found before
    self then return start of parent. If no parent then return (0, 0)."""

    if prev := self.prev(all):
        return prev.bloc[2:]
    elif parent := self.parent:
        return parent.bloc[:2]

    return 0, 0


def _next_bound_step(
    self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = 'loc'
) -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object using `step_fwd()`."""

    if next := self.step_fwd(all, False):
        return next.bloc[:2]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def _prev_bound_step(
    self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = 'loc'
) -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object using `step_back()`."""

    if prev := self.step_back(all, False):
        return prev.bloc[2:]

    return 0, 0


# ----------------------------------------------------------------------------------------------------------------------
# public FST class methods

def next(self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False) -> fst.FST | None:
    """Get next sibling of `self` in syntactic order, only within parent.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.

    **Returns:**
    - `None` if last valid sibling in parent, otherwise next node.

    **Examples:**

    >>> f = FST('[[1, 2], [3, 4]]')

    >>> f.elts[0].next().src
    '[3, 4]'

    >>> print(f.elts[1].next())
    None
    """

    if not (parent := self.parent):  # is_root
        return None

    parenta = parent.a
    parent_cls = parenta.__class__

    while True:
        field, idx = self.pfield

        if not (self := NEXT_FUNCS[parent_cls, field](parenta, idx)):
            return None

        if _check_all_param(self, all):
            return self


def prev(self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False) -> fst.FST | None:
    """Get previous sibling of `self` in syntactic order, only within parent.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.

    **Returns:**
    - `None` if first valid sibling in parent, otherwise previous node.

    **Examples:**

    >>> f = FST('[[1, 2], [3, 4]]')

    >>> f.elts[1].prev().src
    '[1, 2]'

    >>> print(f.elts[0].prev())
    None
    """

    if not (parent := self.parent):  # is_root
        return None

    parenta = parent.a
    parent_cls = parenta.__class__

    while True:
        field, idx = self.pfield

        if not (self := PREV_FUNCS[parent_cls, field](parenta, idx)):
            return None

        if _check_all_param(self, all):
            return self


def first_child(self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False) -> fst.FST | None:
    """Get first valid child in syntactic order.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.

    **Returns:**
    - `None` if no valid children, otherwise first valid child.

    **Examples:**

    >>> f = FST('def f(a: list[str], /, reject: int, *c, d=100, **e): pass')

    >>> f.first_child().src
    'a: list[str], /, reject: int, *c, d=100, **e'

    >>> f.args.first_child().src
    'a: list[str]'

    >>> f.args.first_child().first_child().src
    'list[str]'
    """

    ast = self.a
    ast_cls = ast.__class__
    field = idx = None

    while True:
        if not (self := NEXT_FUNCS[ast_cls, field](ast, idx)):
            return None

        if _check_all_param(self, all):
            return self

        field, idx = self.pfield


def last_child(self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False) -> fst.FST | None:
    """Get last valid child in syntactic order.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.

    **Returns:**
    - `None` if no valid children, otherwise last valid child.

    **Examples:**

    >>> f = FST('def f(a: list[str], /, reject: int, *c, d=100, **e): pass')

    >>> f.last_child().src
    'pass'

    >>> f.args.last_child().src
    'e'
    """

    ast = self.a
    ast_cls = ast.__class__
    field = idx = None

    while True:
        if not (self := PREV_FUNCS[ast_cls, field](ast, idx)):
            return None

        if _check_all_param(self, all):
            return self

        field, idx = self.pfield


def last_header_child(
    self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False
) -> fst.FST | None:
    r"""Get last valid child in syntactic order in a block header (before the `:`), e.g. the `something` in
    `if something: pass`.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.

    **Returns:**
    - `None` if no valid children or if `self` is not a block statement, otherwise last valid child in the block
        header.

    **Examples:**

    >>> print(FST('if something:\n    i = 2\n    i = 3')
    ...       .last_header_child().src)
    something

    >>> print(FST('try: pass\nexcept Exception as exc: pass').handlers[0]
    ...       .last_header_child().src)
    Exception

    >>> print(FST('with a, b: pass').last_header_child().src)
    b

    >>> print(FST('try: pass\nfinally: pass').last_header_child())
    None

    >>> print(FST('i = 1').last_header_child())
    None
    """

    if not (child := last_block_header_child(self.a)):
        return None

    if _check_all_param(f := child.f, all):
        return f

    return self.prev_child(f, all)


def next_child(
    self: fst.FST, from_child: fst.FST | None, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False
) -> fst.FST | None:
    """Get the next child in syntactic order, meant for simple iteration.

    This is a slower way to iterate vs. `walk()`, but will walk any modified future sibling nodes not yet walked as long
    as the replaced node and its parent is used for the following call.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.

    **Returns:**
    - `None` if last valid child in `self`, otherwise next child node.

    **Examples:**

    >>> f = FST('[[1, 2], [3, 4]]')

    >>> f.next_child(f.elts[0]).src
    '[3, 4]'

    >>> print(f.next_child(f.elts[1]))
    None

    >>> f = FST('[this, is_, reparsed, each, step, and_, still, walks, ok]')
    >>> n = None
    >>> while n := f.next_child(n):
    ...     if n.is_Name:
    ...         n = n.replace(n.id[::-1])
    >>> f.src
    '[siht, _si, desraper, hcae, pets, _dna, llits, sklaw, ko]'
    """

    ast = self.a
    ast_cls = ast.__class__

    if from_child is None:
        field = idx = None
    else:
        field, idx = from_child.pfield

    while True:
        if not (self := NEXT_FUNCS[ast_cls, field](ast, idx)):
            return None

        if _check_all_param(self, all):
            return self

        field, idx = self.pfield


def prev_child(
    self: fst.FST, from_child: fst.FST | None, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False
) -> fst.FST | None:
    """Get the previous child in syntactic order, meant for simple iteration.

    This is a slower way to iterate vs. `walk()` but will walk any modified future sibling nodes not yet walked as long
    as the replaced node and its parent is used for the following call.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.

    **Returns:**
    - `None` if first valid child in `self`, otherwise previous child node.

    **Examples:**

    >>> f = FST('[[1, 2], [3, 4]]')

    >>> f.prev_child(f.elts[1]).src
    '[1, 2]'

    >>> print(f.prev_child(f.elts[0]))
    None

    >>> f = FST('[this, is_, reparsed, each, step, and_, still, walks, ok]')
    >>> n = None
    >>> while n := f.prev_child(n):
    ...     if n.is_Name:
    ...         n = n.replace(n.id[::-1])
    >>> f.src
    '[siht, _si, desraper, hcae, pets, _dna, llits, sklaw, ko]'
    """

    ast = self.a
    ast_cls = ast.__class__

    if from_child is None:
        field = idx = None
    else:
        field, idx = from_child.pfield

    while True:
        if not (self := PREV_FUNCS[ast_cls, field](ast, idx)):
            return None

        if _check_all_param(self, all):
            return self

        field, idx = self.pfield


def step_fwd(
    self: fst.FST,
    all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False,
    recurse_self: bool = True,
    *,
    top: fst.FST | None = None,
) -> fst.FST | None:
    """Step forward in the tree in syntactic order, as if `walk()`ing forward, **NOT** the inverse of `step_back()`. Will
    walk up parents and down children to get the next node, returning `None` only when we are at the end of the whole
    thing.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.
    - `recurse_self`: Whether to allow recursion into `self` to return children or move directly to next nodes of
        `self` on start.
    - `top`: If present, specifies the top of the container we are walking. This is checked on the way up out of
        children and not returned when encountered, rather `None` is returned. Passing this allows you to restrict a
        walk to a certain scope or container. It is checked on entry if there are no children, so you can make the first
        call on this node without problem.

    **Returns:**
    - `None` if last valid node in tree, otherwise next node in order.

    **Examples:**

    >>> f = FST('[[1, 2], [3, 4]]')

    >>> f.elts[0].src
    '[1, 2]'

    >>> f.elts[0].step_fwd().src
    '1'

    >>> f.elts[0].step_fwd(recurse_self=False).src
    '[3, 4]'

    >>> f.elts[0].elts[1].src
    '2'

    >>> f.elts[0].elts[1].step_fwd().src
    '[3, 4]'

    >>> f = FST('[this, [is_, [reparsed, each], step, and_, still], walks, ok]')
    >>> n = f.elts[0]
    >>> while True:
    ...     if n.is_Name:
    ...         n = n.replace(n.id[::-1])
    ...     if not (n := n.step_fwd()):
    ...         break
    >>> f.src
    '[siht, [_si, [desraper, hcae], pets, _dna, llits], sklaw, ko]'

    Example from `walk()` but using this method all modified nodes are walked.

    >>> f = FST('[pre_parent, [pre_self, [child], post_self], post_parent]')

    >>> g = f

    >>> while True:
    ...     print(f'{g!r:<23}{g.src[:57]}')
    ...
    ...     if g.src == '[child]':
    ...         _ = f.elts[0].replace('new_pre_parent')
    ...         _ = f.elts[2].replace('new_post_parent')
    ...         _ = f.elts[1].elts[0].replace('new_pre_self')
    ...         _ = f.elts[1].elts[2].replace('new_post_self')
    ...         _ = f.elts[1].elts[1].elts[0].replace('new_child')
    ...
    ...     if not (g := g.step_fwd()):
    ...         break
    <List ROOT 0,0..0,57>  [pre_parent, [pre_self, [child], post_self], post_parent]
    <Name 0,1..0,11>       pre_parent
    <List 0,13..0,43>      [pre_self, [child], post_self]
    <Name 0,14..0,22>      pre_self
    <List 0,24..0,31>      [child]
    <Name 0,33..0,42>      new_child
    <Name 0,45..0,58>      new_post_self
    <Name 0,61..0,76>      new_post_parent

    >>> print(f.src)
    [new_pre_parent, [new_pre_self, [new_child], new_post_self], new_post_parent]

    >>> g = f = FST('[a, [b, c], d]')

    >>> while g := g.step_fwd(Name, top=f.elts[1]):
    ...     print(g.src)
    a
    b
    c
    """

    if recurse_self:
        while fst_ := self.first_child(True):
            if _check_all_param(fst_, all):
                return fst_

            self = fst_

    if top is None:
        top = (None,)
    elif self is top:  # calling on empty Set which is top for example
        return None
    else:
        top = (top, None)

    while True:
        while not (fst_ := self.next(True)):
            if (self := self.parent) in top:
                return None

        while True:
            if _check_all_param(fst_, all):
                return fst_

            self = fst_

            if not (fst_ := self.first_child(True)):
                break


def step_back(
    self: fst.FST,
    all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False,
    recurse_self: bool = True,
    *,
    top: fst.FST | None = None,
) -> fst.FST | None:
    """Step backward in the tree in syntactic order, as if `walk()`ing backward, **NOT** the inverse of `step_fwd()`.
    Will walk up parents and down children to get the next node, returning `None` only when we are at the beginning
    of the whole thing.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated location).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks.
    - `recurse_self`: Whether to allow recursion into `self` to return children or move directly to previous nodes
        of `self` on start.
    - `top`: If present, specifies the top of the container we are walking. This is checked on the way up out of
        children and not returned when encountered, rather `None` is returned. Passing this allows you to restrict a
        walk to a certain scope or container. It is checked on entry if there are no children, so you can make the first
        call on this node without problem.

    **Returns:**
    - `None` if first valid node in tree, otherwise previous node in order.

    **Examples:**

    >>> f = FST('[[1, 2], [3, 4]]')

    >>> f.elts[1].src
    '[3, 4]'

    >>> f.elts[1].step_back().src
    '4'

    >>> f.elts[1].step_back(recurse_self=False).src
    '[1, 2]'

    >>> f.elts[1].elts[0].src
    '3'

    >>> f.elts[1].elts[0].step_back().src
    '[1, 2]'

    >>> f = FST('[this, [is_, [reparsed, each], step, and_, still], walks, ok]')
    >>> n = f.elts[-1]
    >>> while True:
    ...     if n.is_Name:
    ...         n = n.replace(n.id[::-1])
    ...     if not (n := n.step_back()):
    ...         break
    >>> f.src
    '[siht, [_si, [desraper, hcae], pets, _dna, llits], sklaw, ko]'

    >>> g = f = FST('[a, [b, c], d]')

    >>> while g := g.step_back(Name, top=f.elts[1]):
    ...     print(g.src)
    d
    c
    b
    """

    if recurse_self:
        while fst_ := self.last_child(True):
            if _check_all_param(fst_, all):
                return fst_

            self = fst_

    if top is None:
        top = (None,)
    elif self is top:  # calling on empty Set which is top for example
        return None
    else:
        top = (top, None)

    while True:
        while not (fst_ := self.prev(True)):
            if (self := self.parent) in top:
                return None

        while True:
            if _check_all_param(fst_, all):
                return fst_

            self = fst_

            if not (fst_ := self.last_child(True)):
                break


def walk(
    self: fst.FST,
    all: bool | Literal['loc'] | type[AST] | Container[type[AST]] | Callable[[fst.FST], object] = False,
    *,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
    asts: list[AST] | None = None,
) -> Generator[fst.FST, bool, None]:
    r"""Walk `self` and descendants in syntactic order.

    When walking, you can `send(False)` to the generator to skip recursion into the current child. `send(True)` will
    allow recursion into child if called with `recurse=False` or `scope=True` would otherwise disallow it. A
    `send(True)` walks the child node and **ALL** its children unconditionally, regardless of current `scope` or
    `recurse` setting. Can send multiple times, last value sent takes effect.

    The walk is defined forwards or backwards in that it returns a parent, then recurses into the children and walks
    those in the given direction, recursing into each child's children before continuing with siblings. Walking
    backwards will not generate the same sequence as `list(walk())[::-1]` due to this behavior.

    Node **REPLACEMENT** and **DELETION** of the nodes yielded during the walk is always supported. If replaced, the new
    children will be walked next unless you explicitly `send(False)` to the generator. Note that on replace the new
    children can only be walked if the replacement was of the single current node as a single item operation. If the
    replacement was with a slice operation then the children will not be walked.

    Other operations will also work and not break the walk but the new nodes may not be walked depending on the kind of
    operation.
    - Child nodes of the current node can be replaced and they will be walked when the walk gets to them.
    - Sibling nodes of either this node or any parents which have not been walked yet can be deleted, replaced or
        inserted before but the new nodes will not be walked (and neither will any deleted nodes).
    - Previously walked nodes can likewise be deleted, replaced or inserted before.
    - Replacing or deleting a node in the current parent chain is allowed and will cause the walk to continue at the
        following sibling nodes of the node which was operated on.
    - The header said replacement and deletion, so `del`, `remove()`, `replace()`, `put()`, etc... Not `.cut()` or
        `get(..., cut=True)`, with or without inserting them somewhere else. If cut, those nodes may still wind up
        being walked as part of this walk, even if transferred to a different tree. If you wish to do this kind of
        operation during a walk then either explicitly copy then delete the node(s), or defer the cut and move until
        after the walk.
    - `raw` operations can change a lot of nodes and cause the walk to miss some you thought would get walked, but they
        will not cause the walk to break.

    **Note:** About scopes, the `NamedExpr` (walrus) expression is treated specially in a Comprehension (capital 'C' to
    differentiate from the node type `comprehension`). The `target` of the operation actually belongs to the first
    non-Comprehension enclosing scope. For this reason, when a walk recurses into a Comprehension scope the walrus
    `target` nodes are still returned even though everything else belongs to the Comprehension scope and is not returned
    (except for the first `comprehension.iter`, which also belongs to the enclosing scope). This remains true for
    walrus `target`s for whatever level of nesting of Comprehensions is recursed into. One quirk, if starting a scope
    walk on a Comprehension, any walrus `target`s **WILL** be returned, the first iterator though will not. This is on
    purpose.

    **Parameters:**
    - `all`: Whether to return all nodes or only specific types.
        - `True`: All nodes will be returned.
        - `False`: Only nodes which have intrinsic `AST` locations and also larger calculated location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present). Operators are not returned (even though they have calculated locations).
        - `'loc'`: Same as `True` but always returns `arguments` even if empty (as it has a location even then). Also
            operators with calculated locations (excluding `and` and `or` since they do not always have a well defined
            location).
        - `type[AST]`: A singe **LEAF** `AST` type to return. This will not constrain the walk, just filter which nodes
            are returned.
        - `Container[type[AST]]`: A container of **LEAF** `AST` types to return. Best container type is a `set`,
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks. This will not
            constrain the walk, just filter which nodes are returned.
        - `Callable[[fst.FST], object]`: Call out to an external function for each node which should return a truthy or
            falsey object for whether to yield the node or not. THIS FUNCTION CAN ONLY BE A QUERY! It must not modify
            the tree or set any state expected for the iteration loop. NO SIDE EFFECTS ALLOWED!!!
    - `self_`: If `True` then self will be returned first with the possibility to skip children with `send(False)`,
        otherwise will start directly with children.
    - `recurse`: Whether to recurse past the **FIRST LEVEL OF CHILDREN** by default, `send(True)` for a given node will
        always override this. Meaning that if `False`, will only return `self` (if allowed to by `self_`) and the
        the direct children of `self`, but no deeper.
    - `scope`: If `True` then will walk only within the scope of `self`. Meaning if called on a `FunctionDef` then
        will only walk children which are within the function scope. Will yield children which have their own
        scopes, and the parts of them which are visible in this scope (like default argument values), but will not
        recurse into
        them unless `send(True)` is done for that child.
    - `back`: If `True` then walk every node in reverse syntactic order. This is not the same as a full forwards
        walk reversed due to recursion (parents are still returned before children, only in reverse sibling order).
    - `asts`: If this is provided as a list of `AST` nodes (from an `FST` tree) then this is used for the initial list
        of nodes to walk and recurse into (if recurse allowed). In this case `self_` is ignored and if `scope=True` then
        no top-level function elements like argument defaults are excluded for each node in `asts`, though `scope` is
        honored for not recursing into child scopes (except Comprehension `NamedExpr.target`). `recurse` and `back` are
        also honored (`back` will reverse the order of the walk for the given `asts` as expected). No syntax ordering is
        done on this list, it is walked "as-is", so it may just be a collection of different nodes to walk individually.
        It wouldn't make sense for the nodes in this list to have descendant relationships. The `asts` list is not
        consumed.

    **Returns:**
    - `Generator`: This will yield the nodes which fit the parametes. Can also `send(True)` or `send(False)` to this
        generator to explicitly indicate whether to recurse or not into the yielded node. Sending to the generator does
        not advance the iteration and can be done an arbitrary number of times before continuing with the iteration.

    **Examples:**

    Normal walk.

    >>> f = FST('[pre, [child], post]')

    >>> for g in (gen := f.walk()):
    ...     print(f'{g!r:<23}{g.src[:47]}')
    ...
    ...     if g.is_List and g.elts[0].src == 'send_False':
    ...         _ = gen.send(False)
    <List ROOT 0,0..0,20>  [pre, [child], post]
    <Name 0,1..0,4>        pre
    <List 0,6..0,13>       [child]
    <Name 0,7..0,12>       child
    <Name 0,15..0,19>      post

    Reject recursion into a child.

    >>> f = FST('[pre, [send_False], post]')

    >>> for g in (gen := f.walk()):
    ...     print(f'{g!r:<23}{g.src[:47]}')
    ...
    ...     if g.is_List and g.elts[0].src == 'send_False':
    ...         _ = gen.send(False)
    <List ROOT 0,0..0,25>  [pre, [send_False], post]
    <Name 0,1..0,4>        pre
    <List 0,6..0,18>       [send_False]
    <Name 0,20..0,24>      post

    Walk nodes that are part of a scope. We walk with `self_=False` just to not print the top level mutliline function,
    the rest of the walk over the children just goes as normal.

    >>> f = FST('''
    ... def func(func_arg=func_def) -> bool:
    ...     def sub(sub_arg=sub_def) -> int: pass
    ...     val = [i := j for j in iterator]
    ... '''.strip())

    >>> for g in f.walk(self_=False, scope=True):
    ...     print(f'{g!r:<25}{g.src[:47]}')
    <arguments 0,9..0,26>    func_arg=func_def
    <arg 0,9..0,17>          func_arg
    <FunctionDef 1,4..1,41>  def sub(sub_arg=sub_def) -> int: pass
    <Name 1,20..1,27>        sub_def
    <Name 1,32..1,35>        int
    <Assign 2,4..2,36>       val = [i := j for j in iterator]
    <Name 2,4..2,7>          val
    <ListComp 2,10..2,36>    [i := j for j in iterator]
    <Name 2,11..2,12>        i
    <Name 2,27..2,35>        iterator

    Replace all `Name` nodes.

    >>> import ast

    >>> f = FST('a * (x.y + u[v])')

    >>> for g in f.walk(all=ast.Name):
    ...     _ = g.replace('new_' + g.id)

    >>> print(f.src)
    new_a * (new_x.y + new_u[new_v])

    Replace nodes around us. The replacement doesn't have to be executed on the node being walked, it can be on any
    node. Note how replacing a node that hasn't been walked yet removes both that node **AND** the replacement node from
    the walk. After the walk though, all nodes which were replaced have their new values.

    >>> f = FST('[pre_parent, [pre_self, [child], post_self], post_parent]')

    >>> for g in f.walk():
    ...     print(f'{g!r:<23}{g.src[:57]}')
    ...
    ...     if g.src == '[child]':
    ...         _ = f.elts[0].replace('new_pre_parent')
    ...         _ = f.elts[2].replace('new_post_parent')
    ...         _ = f.elts[1].elts[0].replace('new_pre_self')
    ...         _ = f.elts[1].elts[2].replace('new_post_self')
    ...         _ = f.elts[1].elts[1].elts[0].replace('new_child')
    <List ROOT 0,0..0,57>  [pre_parent, [pre_self, [child], post_self], post_parent]
    <Name 0,1..0,11>       pre_parent
    <List 0,13..0,43>      [pre_self, [child], post_self]
    <Name 0,14..0,22>      pre_self
    <List 0,24..0,31>      [child]
    <Name 0,33..0,42>      new_child

    >>> print(f.src)
    [new_pre_parent, [new_pre_self, [new_child], new_post_self], new_post_parent]

    Replacing or removing a parent node is allowed and the walk will continue where it can.

    >>> f = FST('[pre_grand, [pre_parent, [self], post_parent], post_grand]')

    >>> for g in f.walk():
    ...     print(f'{g!r:<23}{g.src[:58]}')
    ...
    ...     if g.src == 'self':
    ...         g.parent.parent.remove()  # [pre_parent, [self], post_parent]
    <List ROOT 0,0..0,58>  [pre_grand, [pre_parent, [self], post_parent], post_grand]
    <Name 0,1..0,10>       pre_grand
    <List 0,12..0,45>      [pre_parent, [self], post_parent]
    <Name 0,13..0,23>      pre_parent
    <List 0,25..0,31>      [self]
    <Name 0,26..0,30>      self
    <Name 0,12..0,22>      post_grand

    >>> print(f.src)
    [pre_grand, post_grand]

    >>> f = FST('[0, 1, [2, 3], 4, 5]')

    >>> print(list(g.src for g in f.walk(asts=f.a.elts[1:-2])))
    ['1', '[2, 3]', '2', '3']

    >>> print(list(g.src for g in f.walk(asts=f.a.elts[1:-2], back=True)))
    ['[2, 3]', '3', '2', '1']

    """

    ast = self.a
    check_all_param = _all_param_func(all)

    if asts is not None:
        if scope:
            scope_ctx = _ScopeContext(self, all, back, check_all_param)

        stack = asts[:] if back else asts[::-1]

    else:
        if self_:
            if check_all_param(self):
                recurse_ = 1  # 1 to differentiate from True

                while (sent := (yield self)) is not None:
                    recurse_ = sent

                if not recurse_:
                    return

                if not (ast := self.a):  # if deleted this node then we are done
                    return

                if recurse_ is True:  # user changed their mind?!?
                    recurse = True
                    scope = False

        # if we are walking scope then we may need to exclude some parts of the top-level node, we do after first step of walk in case top level node is replaced or scope turned off by send(True)

        if scope:  # some parts of functions or classes or the various comprehensions are outside their scope
            scope_ctx, stack = _ScopeContext.create(self, all, back, check_all_param, ast)
        else:
            stack = None  # scope_ctx not created because not needed in this case

        if stack is None:  # nothing excluded so just add all children
            stack = syntax_ordered_children(ast)

            if not back:
                stack = stack[::-1]

        if scope:
            scope_ctx.stack = stack  # set this so it doesn't have to be passed on each call

    # loop

    while stack:
        if not (ast := stack.pop()):  # may be `None`s in there
            continue

        if not (fst_ := ast.f):  # if node was removed or replaced somewhere else then just continue walk
            continue

        if check_all_param(fst_):
            recurse_ = recurse

            while (sent := (yield fst_)) is not None:
                recurse_ = 1 if sent else False  # 1 to differentiate from True

            if not recurse_:  # either send(False) or wasn't going to recurse anyways
                continue

            if not (ast := fst_.a):  # has been deleted by the player (if replaced then this FST node will still exist but the .a will have changed)
                continue

            if recurse_ is not True:  # user did send(True), walk this child unconditionally
                yield from fst_.walk(all, self_=False, back=back)

                continue

        elif not recurse:
            continue

        if scope and (func_and_isgen := _SCOPE_WALK_FUNCS.get(ast.__class__)):  # if walking scope then check if we got to another scope and walk the things from that which are visible in our scope
            func, is_gen = func_and_isgen

            if is_gen:
                yield from func(scope_ctx, ast)

                continue

            elif func(scope_ctx, ast, stack):
                continue

        if children := syntax_ordered_children(ast):
            stack.extend(children if back else children[::-1])
