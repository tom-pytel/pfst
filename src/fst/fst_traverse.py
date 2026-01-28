"""Siblings, children and walk, all in syntactic order.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from typing import Container, Generator, Literal

from . import fst

from .asttypes import (
    ASTS_LEAF_EXPR_CONTEXT,
    ASTS_LEAF_BOOLOP,
    ASTS_LEAF_OPERATOR,
    ASTS_LEAF_UNARYOP,
    ASTS_LEAF_CMPOP,
    ASTS_LEAF_TYPE_PARAM,
    ASTS_LEAF_FUNCDEF,
    AST,
    ClassDef,
    DictComp,
    GeneratorExp,
    Lambda,
    ListComp,
    NamedExpr,
    SetComp,
    arg,
    arguments,
    comprehension,
)

from .astutil import last_block_header_child, syntax_ordered_children
from .traverse_next import NEXT_FUNCS
from .traverse_prev import PREV_FUNCS


_ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP          =  ASTS_LEAF_EXPR_CONTEXT | ASTS_LEAF_BOOLOP
_ASTS_LEAF_EXPR_CONTEXT_OR_OP_OR_ARGUMENTS = (_ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP | ASTS_LEAF_OPERATOR |
                                              ASTS_LEAF_UNARYOP | ASTS_LEAF_CMPOP | {arguments})

_ASTS_LEAF_WALK_SCOPE = ASTS_LEAF_FUNCDEF | ASTS_LEAF_TYPE_PARAM | {ClassDef, Lambda, ListComp, SetComp, DictComp,
                                                                    GeneratorExp, comprehension, arguments, arg}  # used in walk(scope=True) for a little optimization


def _check_all_param(fst_: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]]) -> bool:
    """Check 'all' parameter condition on node. Safe for low level because doesn't use `.loc` calculation machinery."""

    if all is True:
        return True

    if all is False:
        return (
            fst_.a.__class__ not in _ASTS_LEAF_EXPR_CONTEXT_OR_OP_OR_ARGUMENTS
            or ((a := fst_.a).__class__ is arguments
                and (a.args or a.vararg or a.kwonlyargs or a.kwarg or a.posonlyargs)
        ))

    if all == 'loc':
        return fst_.a.__class__ not in _ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP

    if hasattr(all, '__contains__'):
        return fst_.a.__class__ in all

    return fst_.a.__class__ is all


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
    self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False, recurse_self: bool = True
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
    """

    if recurse_self and (fst_ := self.first_child(all)):
        return fst_

    while not (fst_ := self.next(all)):
        if not (self := self.parent):
            return None

    return fst_


def step_back(
    self: fst.FST, all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False, recurse_self: bool = True
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
    """

    if recurse_self and (fst_ := self.last_child(all)):
        return fst_

    while not (fst_ := self.prev(all)):
        if not (self := self.parent):
            return None

    return fst_


def walk(
    self: fst.FST,
    all: bool | Literal['loc'] | type[AST] | Container[type[AST]] = False,
    *,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
) -> Generator[fst.FST, bool, None]:
    r"""Walk `self` and descendants in syntactic order.

    When walking, you can `send(False)` to the generator to skip recursion into the current child. `send(True)` will
    allow recursion into child if called with `recurse=False` or `scope=True` would otherwise disallow it. Can send
    multiple times, last value sent takes effect.

    The walk is defined forwards or backwards in that it returns a parent, then recurses into the children and walks
    those in the given direction, recursing into each child's children before continuing with siblings. Walking
    backwards will not generate the same sequence as `list(walk())[::-1]` due to this behavior.

    Node replacement and removal during the walk is supported with some caveats, the rules are:
    - `raw` operations can change a lot of nodes and cause the walk to miss some you thought would get walked, but they
        will not cause the walk to break.
    - The current node can always be removed, replaced or inserted before (if list field). If replaced the new children
        will be walked next unless you explicitly `send(False)` to the generator.
    - Child nodes of the current node can be replaced and they will be walked when the walk gets to them.
    - Previously walked nodes can likewise be removed, replaced or inserted before.
    - Replacing or removing a node in the current parent chain is allowed and will cause the walk to continue at its
        following siblings which were not modified.
    - Sibling nodes of either this node or any parents which have not been walked yet can be removed, replaced or
        inserted before but the new nodes will not be walked (and neither will any removed nodes).

    **Note:** About scopes, the `NamedExpr` (walrus) expression is treated specially in a Comprehension (capital 'C' to
    differentiate from the node type `comprehension`). The `target` of the operation actually belongs to the first
    non-Comprehension enclosing scope. For this reason, when a walk recurses into a Comprehension scope the walrus
    `target` nodes are still returned even though everything else belongs to the Comprehension scope and is not returned
    (except for the first `comprehension.iter`, which also belongs to the enclosing scope). This remains true for
    whatever level of nesting of Comprehensions is recursed into. One quirk, if starting a scope walk on a
    Comprehension, any walrus `target`s **WILL** be returned, the first iterator though will not. This is on purpose.

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
            `frozenset` or `dict` with the keys being the `AST` classes as those are the fastest checks. This will not
            constrain the walk, just filter which nodes are returned.
    - `self_`: If `True` then self will be returned first with the possibility to skip children with `send(False)`,
        otherwise will start directly with children.
    - `recurse`: Whether to recurse past the first level of children by default, `send(True)` for a given node will
        always override this. Meaning that if `False`, will only return `self` (if allowed to by `self_`) and the
        the immediate children of `self` and no deeper.
    - `scope`: If `True` then will walk only within the scope of `self`. Meaning if called on a `FunctionDef` then
        will only walk children which are within the function scope. Will yield children which have their own
        scopes, and the parts of them which are visible in this scope (like default argument values), but will not
        recurse into
        them unless `send(True)` is done for that child.
    - `back`: If `True` then walk every node in reverse syntactic order. This is not the same as a full forwards
        walk reversed due to recursion (parents are still returned before children, only in reverse sibling order).

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

    """

    ast = self.a

    if self_:
        if _check_all_param(self, all):
            recurse_ = 1

            while (sent := (yield self)) is not None:
                recurse_ = sent

            if not recurse_:
                return

            if not (ast := self.a):  # if deleted this node then we are done
                return

            if recurse_ is True:  # user changed their mind?!?
                recurse = True
                scope = False

    stack = None

    # if we are walking scope then we may need to exclude some parts of the top-level node

    if scope:  # some parts of functions or classes or the various comprehensions are outside their scope
        scope_args = False  # can't use None because root node may have None as a parent
        ast_cls = ast.__class__

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

            skip_iter = generators[0].iter if generators else None  # maybe the user deleted all generators

    if stack is None:  # nothing excluded so just add all children
        stack = syntax_ordered_children(ast)

        if not back:
            stack = stack[::-1]

    # loop

    while stack:
        if not (ast := stack.pop()):  # may be `None`s in there
            continue

        if not (fst_ := ast.f):  # if node was removed or replaced somewhere else then just continue walk
            continue

        if _check_all_param(fst_, all):
            recurse_ = recurse

            while (sent := (yield fst_)) is not None:
                recurse_ = 1 if sent else False

            if not recurse_:  # either send(False) or wasn't going to recurse anyways
                continue

            if not (ast := fst_.a):  # has been deleted by the player (if modified then this FST node will still exist but the .a will have changed)
                continue

            if recurse_ is not True:  # user did send(True), walk this child unconditionally
                yield from fst_.walk(all, self_=False, back=back)

                continue

        elif not recurse:
            continue

        if scope:  # if walking scope then check if we got to another scope and walk the things from that which are visible in our scope
            ast_cls = ast.__class__

            if ast_cls not in _ASTS_LEAF_WALK_SCOPE:  # early out optimization
                pass  # noop

            if ast_cls in ASTS_LEAF_FUNCDEF:
                args = ast.args

                if back:
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

                continue

            elif ast_cls is ClassDef:
                if back:
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

                continue

            elif ast_cls is Lambda:
                args = ast.args

                if back:
                    stack.extend(args.defaults)
                    stack.extend(args.kw_defaults)
                else:
                    stack.extend(args.kw_defaults[::-1])
                    stack.extend(args.defaults[::-1])

                continue

            elif ast_cls in (ListComp, SetComp, DictComp, GeneratorExp):
                comp_first_iter = ast.generators[0].iter

                gen = fst_.walk(all, self_=False, back=back)

                for f in gen:  # we want to return all NamedExpr.target and first top-level .iter, yeah, its ugly
                    a = f.a

                    if a is comp_first_iter:  # top-level iterator is in parent scope
                        subrecurse = recurse

                        while (sent := (yield f)) is not None:
                            subrecurse = 1 if sent else False

                        if subrecurse:
                            yield from f.walk(all, self_=False, scope=subrecurse is True, back=back)  # if the user did send(True) (subrecurse=1) then we want to recurse uncondintionally (scope=False), otherwise subrecurse=True and continue walking with scope=True

                        gen.send(False)  # we processed this node here so don't recurse into it

                    elif (  # all NamedExpr.targets are in parent scope
                        f.parent.a.__class__ is NamedExpr
                        and f.pfield.name == 'target'  # a.__class__ is Name
                    ):
                        subrecurse = recurse

                        while (sent := (yield f)) is not None:
                            subrecurse = sent

                        if subrecurse and _check_all_param(f := a.ctx.f, all):  # truly pedantic, but maybe the user really really really wants that .ctx?
                            while (yield f) is not None:  # eat all the user's send()s
                                pass

                        gen.send(False)  # we processed this node here so don't recurse into it

                continue

            elif ast_cls is comprehension:  # this only comes from top-level *Comp, not ones encountered in a *Comp or GeneratorExp here
                if back:
                    stack.append(ast.target)

                    if (a := ast.iter) is not skip_iter:
                        stack.append(a)

                    if a := ast.ifs:
                        stack.extend(a)

                else:
                    if a := ast.ifs:
                        stack.extend(a)

                    if (a := ast.iter) is not skip_iter:
                        stack.append(a)

                    stack.append(ast.target)

                continue

            elif ast is scope_args:  # exclude defaults and kw_defaults from walk, ast is top-level scope arguments
                if back:
                    stack.extend(ast.posonlyargs)
                    stack.extend(ast.args)

                    if vararg := ast.vararg:
                        stack.append(vararg)

                    stack.extend(ast.kwonlyargs)

                    if kwarg := ast.kwarg:
                        stack.append(ast.kwarg)

                else:
                    if kwarg := ast.kwarg:
                        stack.append(ast.kwarg)

                    stack.extend(ast.kwonlyargs[::-1])

                    if vararg := ast.vararg:
                        stack.append(vararg)

                    stack.extend(ast.args[::-1])
                    stack.extend(ast.posonlyargs[::-1])

                continue

            elif ast_cls is arg:
                if fst_.parent.a is scope_args:  # if arg part of top-level node args then don't recurse
                    continue

            elif ast_cls in ASTS_LEAF_TYPE_PARAM:
                if is_def and fst_.parent is self:  # don't recurse for type annotations and defaults in top-level node
                    continue

        if children := syntax_ordered_children(ast):
            stack.extend(children if back else children[::-1])
