"""Siblings, children and walk, all in syntactic order."""

from __future__ import annotations

from typing import Literal

from . import fst

from .astutil import (
    AST,
    Dict,
    Compare,
    MatchMapping,
    Call,
    arguments,
    expr_context,
    boolop,
    operator,
    unaryop,
    cmpop,
    AST_FIELDS,
)

__all__ = [
    'AST_FIELDS_NEXT', 'AST_FIELDS_PREV',
    'next_bound', 'prev_bound', 'next_bound_step', 'prev_bound_step', 'check_with_loc',
]


AST_FIELDS_NEXT: dict[tuple[type[AST], str], str | None] = dict(sum((  # next field name from AST class and current field name
    [] if not fields else
    [((kls, fields[0]), None)] if len(fields) == 1 else
    [((kls, fields[i]), fields[i + 1]) for i in range(len(fields) - 1)] + [((kls, fields[-1]), None)]
    for kls, fields in AST_FIELDS.items()), start=[])
)

AST_FIELDS_NEXT[(Dict, 'keys')]             = 0  # special cases
AST_FIELDS_NEXT[(Dict, 'values')]           = 1
AST_FIELDS_NEXT[(Compare, 'ops')]           = 2
AST_FIELDS_NEXT[(Compare, 'comparators')]   = 3
AST_FIELDS_NEXT[(Compare, 'left')]          = 'comparators'  # black magic juju
AST_FIELDS_NEXT[(MatchMapping, 'keys')]     = 4
AST_FIELDS_NEXT[(MatchMapping, 'patterns')] = 5
AST_FIELDS_NEXT[(Call, 'args')]             = 6
AST_FIELDS_NEXT[(Call, 'keywords')]         = 6
AST_FIELDS_NEXT[(arguments, 'posonlyargs')] = 7
AST_FIELDS_NEXT[(arguments, 'args')]        = 7
AST_FIELDS_NEXT[(arguments, 'vararg')]      = 7
AST_FIELDS_NEXT[(arguments, 'kwonlyargs')]  = 7
AST_FIELDS_NEXT[(arguments, 'defaults')]    = 7
AST_FIELDS_NEXT[(arguments, 'kw_defaults')] = 7

AST_FIELDS_PREV: dict[tuple[type[AST], str], str | None] = dict(sum((  # previous field name from AST class and current field name
    [] if not fields else
    [((kls, fields[0]), None)] if len(fields) == 1 else
    [((kls, fields[i + 1]), fields[i]) for i in range(len(fields) - 1)] + [((kls, fields[0]), None)]
    for kls, fields in AST_FIELDS.items()), start=[])
)

AST_FIELDS_PREV[(Dict, 'keys')]             = 0  # special cases
AST_FIELDS_PREV[(Dict, 'values')]           = 1
AST_FIELDS_PREV[(Compare, 'ops')]           = 2
AST_FIELDS_PREV[(Compare, 'comparators')]   = 3
AST_FIELDS_PREV[(MatchMapping, 'keys')]     = 4
AST_FIELDS_PREV[(MatchMapping, 'patterns')] = 5
AST_FIELDS_PREV[(Call, 'args')]             = 6
AST_FIELDS_PREV[(Call, 'keywords')]         = 6
AST_FIELDS_PREV[(arguments, 'posonlyargs')] = 7
AST_FIELDS_PREV[(arguments, 'args')]        = 7
AST_FIELDS_PREV[(arguments, 'vararg')]      = 7
AST_FIELDS_PREV[(arguments, 'kwonlyargs')]  = 7
AST_FIELDS_PREV[(arguments, 'defaults')]    = 7
AST_FIELDS_PREV[(arguments, 'kw_defaults')] = 7
AST_FIELDS_PREV[(arguments, 'kwarg')]       = 7


def next_bound(self: fst.FST, with_loc: bool | Literal['all', 'own'] = 'all') -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object within parent. If no siblings found after
    self then return end of parent. If no parent then return end of source."""

    if next := self.next(with_loc):
        return next.bloc[:2]
    elif parent := self.parent:
        return parent.bloc[2:]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def prev_bound(self: fst.FST, with_loc: bool | Literal['all', 'own'] = 'all') -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object within parent. If no siblings found before
    self then return start of parent. If no parent then return (0, 0)."""

    if prev := self.prev(with_loc):
        return prev.bloc[2:]
    elif parent := self.parent:
        return parent.bloc[:2]
    else:
        return 0, 0


def next_bound_step(self: fst.FST, with_loc: bool | Literal['all', 'own', 'allown'] = 'all') -> tuple[int, int]:
    """Get a next bound for search before any following ASTs for this object using `step_fwd()`. This is safe to call
    for nodes that live inside nodes without their own locations if `with_loc='allown'`."""

    if next := self.step_fwd(with_loc, recurse_self=False):
        return next.bloc[:2]

    return len(ls := self.root._lines) - 1, len(ls[-1])


def prev_bound_step(self: fst.FST, with_loc: bool | Literal['all', 'own', 'allown'] = 'all') -> tuple[int, int]:
    """Get a prev bound for search after any previous ASTs for this object using `step_back()`. This is safe to call for
    nodes that live inside nodes without their own locations if `with_loc='allown'`."""

    if prev := self.step_back(with_loc, recurse_self=False):
        return prev.bloc[2:]

    return 0, 0


def check_with_loc(fst_: fst.FST, with_loc: bool | Literal['all', 'own'] = True) -> bool:
    """Check location condition on node. Safe for low level because doesn't use `.loc` calculation machinery."""

    if not with_loc:
        return True

    if with_loc is True:
        return not (isinstance(a := fst_.a, (expr_context, boolop, operator, unaryop, cmpop)) or
                    (isinstance(a, arguments) and not a.posonlyargs and not a.args and not a.vararg and
                    not a.kwonlyargs and not a.kwarg))

    if with_loc == 'all':
        return not (isinstance(a := fst_.a, (expr_context, boolop)) or
                    (isinstance(a, arguments) and not a.posonlyargs and not a.args and not a.vararg and
                    not a.kwonlyargs and not a.kwarg))

    return fst_.has_own_loc  # with_loc == 'own'
