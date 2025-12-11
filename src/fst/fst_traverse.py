"""Siblings, children and walk, all in syntactic order.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from typing import Generator, Literal

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
    Call,
    ClassDef,
    Dict,
    DictComp,
    Compare,
    GeneratorExp,
    Lambda,
    ListComp,
    MatchMapping,
    NamedExpr,
    Pass,
    SetComp,
    Starred,
    arg,
    arguments,
    comprehension,
)

from .astutil import (
    AST_FIELDS,
    last_block_header_child,
    syntax_ordered_children,
)

from .common import astfield

__all__ = ['next_bound', 'prev_bound', 'next_bound_step', 'prev_bound_step']


_ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP = ASTS_LEAF_EXPR_CONTEXT | ASTS_LEAF_BOOLOP
_ASTS_LEAF_EXPR_CONTEXT_OR_OP     = (_ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP | ASTS_LEAF_OPERATOR | ASTS_LEAF_UNARYOP
                                     | ASTS_LEAF_CMPOP)

_AST_FIELDS_NEXT: dict[tuple[type[AST], str], str | None] = dict(sum((  # next field name from AST class and current field name
    [] if not fields else
    [((kls, fields[0]), None)] if len(fields) == 1 else
    [((kls, fields[i]), fields[i + 1]) for i in range(len(fields) - 1)] + [((kls, fields[-1]), None)]
    for kls, fields in AST_FIELDS.items()), start=[])
)

_AST_FIELDS_NEXT[(Dict, 'keys')]             = 0  # special cases
_AST_FIELDS_NEXT[(Dict, 'values')]           = 1
_AST_FIELDS_NEXT[(Compare, 'ops')]           = 2
_AST_FIELDS_NEXT[(Compare, 'comparators')]   = 3
_AST_FIELDS_NEXT[(Compare, 'left')]          = 'comparators'  # black magic juju
_AST_FIELDS_NEXT[(MatchMapping, 'keys')]     = 4
_AST_FIELDS_NEXT[(MatchMapping, 'patterns')] = 5
_AST_FIELDS_NEXT[(Call, 'args')]             = 6
_AST_FIELDS_NEXT[(Call, 'keywords')]         = 6
_AST_FIELDS_NEXT[(arguments, 'posonlyargs')] = 7
_AST_FIELDS_NEXT[(arguments, 'args')]        = 7
_AST_FIELDS_NEXT[(arguments, 'vararg')]      = 7
_AST_FIELDS_NEXT[(arguments, 'kwonlyargs')]  = 7
_AST_FIELDS_NEXT[(arguments, 'defaults')]    = 7
_AST_FIELDS_NEXT[(arguments, 'kw_defaults')] = 7

_AST_FIELDS_PREV: dict[tuple[type[AST], str], str | None] = dict(sum((  # previous field name from AST class and current field name
    [] if not fields else
    [((kls, fields[0]), None)] if len(fields) == 1 else
    [((kls, fields[i + 1]), fields[i]) for i in range(len(fields) - 1)] + [((kls, fields[0]), None)]
    for kls, fields in AST_FIELDS.items()), start=[])
)

_AST_FIELDS_PREV[(Dict, 'keys')]             = 0  # special cases
_AST_FIELDS_PREV[(Dict, 'values')]           = 1
_AST_FIELDS_PREV[(Compare, 'ops')]           = 2
_AST_FIELDS_PREV[(Compare, 'comparators')]   = 3
_AST_FIELDS_PREV[(MatchMapping, 'keys')]     = 4
_AST_FIELDS_PREV[(MatchMapping, 'patterns')] = 5
_AST_FIELDS_PREV[(Call, 'args')]             = 6
_AST_FIELDS_PREV[(Call, 'keywords')]         = 6
_AST_FIELDS_PREV[(arguments, 'posonlyargs')] = 7
_AST_FIELDS_PREV[(arguments, 'args')]        = 7
_AST_FIELDS_PREV[(arguments, 'vararg')]      = 7
_AST_FIELDS_PREV[(arguments, 'kwonlyargs')]  = 7
_AST_FIELDS_PREV[(arguments, 'defaults')]    = 7
_AST_FIELDS_PREV[(arguments, 'kw_defaults')] = 7
_AST_FIELDS_PREV[(arguments, 'kwarg')]       = 7


def _check_with_loc(fst_: fst.FST, with_loc: bool | Literal['all', 'own'] = True) -> bool:
    """Check location condition on node. Safe for low level because doesn't use `.loc` calculation machinery."""

    if not with_loc:
        return True

    if with_loc is True:
        a = fst_.a
        a_cls = a.__class__

        return not (
            a_cls in _ASTS_LEAF_EXPR_CONTEXT_OR_OP
            or (
                a_cls is arguments
                and not a.posonlyargs and not a.args and not a.vararg and not a.kwonlyargs and not a.kwarg
        ))

    if with_loc == 'all':
        a = fst_.a
        a_cls = a.__class__

        return not (
            a_cls in _ASTS_LEAF_EXPR_CONTEXT_OR_BOOLOP
            or (
                a_cls is arguments
                and not a.posonlyargs and not a.args and not a.vararg and not a.kwonlyargs and not a.kwarg
        ))

    return fst_.has_own_loc  # with_loc == 'own'


# ----------------------------------------------------------------------------------------------------------------------
# "Public" internal

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


# ----------------------------------------------------------------------------------------------------------------------
# FST class methods

def walk(
    self: fst.FST,
    with_loc: bool | Literal['all', 'own'] = False,
    *,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
) -> Generator[fst.FST, bool, None]:
    r"""Walk `self` and descendants in syntactic order. When walking, you can `send(False)` to the generator to skip
    recursion into the current child. `send(True)` to allow recursion into child if called with `recurse=False` or
    `scope=True` would otherwise disallow it. Can send multiple times, last value sent takes effect.

    The walk is defined forwards or backwards in that it returns a parent, then recurses into the children and walks
    those in the given direction, recursing into each child's children before continuing with siblings. Walking
    backwards will not generate the same sequence as `list(walk())[::-1]` due to this behavior.

    It is safe to `replace()` the node you get as you are walking, as well as modify all of its children or siblings
    which came before, but not parents or siblings which have not been walked yet. We are referring to the normal
    non-raw replacement, if you perform raw operations as you walk then all bets are off.

    This walk is relatively efficient but if all you need to do is just walk ALL the `AST` children without any
    bells or whistles and regardless of syntax order, from which you can get the `FST` nodes via the `.f` attribute,
    then `ast.walk()` will be faster.

    **Note:** The `NamedExpr` (walrus) expression is treated specially in a Comprehension. The `target` of the operation
    actually belongs to the first non-Comprehension enclosing scope. For this reason, when a walk recurses into a
    Comprehension scope the walrus `target` nodes are still returned even though everything else belongs to the
    Comprehension scope and is not returned (except for the first `comprehension.iter`, which also belongs to the
    enclosing scope). This remains true for whatever level of nesting of Comprehensions is recursed into.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.
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

    >>> import ast

    >>> f = FST('def f(a: list[str], /, reject: int, *c, d=100, **e): pass')

    >>> for g in (gen := f.walk(with_loc=True)):
    ...     if isinstance(g.a, ast.arg) and g.a.arg == 'reject':
    ...         _ = gen.send(False)
    ...     else:
    ...         print(f'{g!r:<30}{g.src[:50]!r}')
    <FunctionDef ROOT 0,0..0,57>  'def f(a: list[str], /, reject: int, *c, d=100, **e'
    <arguments 0,6..0,50>         'a: list[str], /, reject: int, *c, d=100, **e'
    <arg 0,6..0,18>               'a: list[str]'
    <Subscript 0,9..0,18>         'list[str]'
    <Name 0,9..0,13>              'list'
    <Name 0,14..0,17>             'str'
    <arg 0,37..0,38>              'c'
    <arg 0,40..0,41>              'd'
    <Constant 0,42..0,45>         '100'
    <arg 0,49..0,50>              'e'
    <Pass 0,53..0,57>             'pass'

    >>> f = FST('''
    ... def f():
    ...     def g(arg=1) -> int:
    ...         pass
    ...     val = [i for i in iterator]
    ... '''.strip())

    >>> for g in f.walk(True, scope=True):
    ...     print(f'{g!r:<30}{g.src[:47]!r}')
    <FunctionDef ROOT 0,0..3,31>  'def f():\n    def g(arg=1) -> int:\n        pass\n'
    <FunctionDef 1,4..2,12>       'def g(arg=1) -> int:\n        pass'
    <Constant 1,14..1,15>         '1'
    <Name 1,20..1,23>             'int'
    <Assign 3,4..3,31>            'val = [i for i in iterator]'
    <Name 3,4..3,7>               'val'
    <ListComp 3,10..3,31>         '[i for i in iterator]'
    <Name 3,22..3,30>             'iterator'

    >>> for g in f.walk(True, back=True):
    ...     print(f'{g!r:<30}{g.src[:47]!r}')
    <FunctionDef ROOT 0,0..3,31>  'def f():\n    def g(arg=1) -> int:\n        pass\n'
    <Assign 3,4..3,31>            'val = [i for i in iterator]'
    <ListComp 3,10..3,31>         '[i for i in iterator]'
    <comprehension 3,13..3,30>    'for i in iterator'
    <Name 3,22..3,30>             'iterator'
    <Name 3,17..3,18>             'i'
    <Name 3,11..3,12>             'i'
    <Name 3,4..3,7>               'val'
    <FunctionDef 1,4..2,12>       'def g(arg=1) -> int:\n        pass'
    <Pass 2,8..2,12>              'pass'
    <Name 1,20..1,23>             'int'
    <arguments 1,10..1,15>        'arg=1'
    <Constant 1,14..1,15>         '1'
    <arg 1,10..1,13>              'arg'
    """

    if self_:
        if not _check_with_loc(self, with_loc):
            return

        recurse_ = 1

        while (sent := (yield self)) is not None:
            recurse_ = sent

        if not self.a:
            self = self.repath()

        if not recurse_:
            return

        elif recurse_ is True:  # user changed their mind?!?
            recurse = True
            scope = False

    ast = self.a
    stack = None

    # if we are walking scope then we may need to exclude some parts of the top-level node

    if scope:  # some parts of functions or classes or the various comprehensions are outside their scope
        scope_args = False  # can't use None because root node may have None as a parent
        ast_cls = ast.__class__

        if (is_def := (ast_cls in ASTS_LEAF_FUNCDEF)) or ast_cls is Lambda:
            scope_args = ast.args  # will need these in the loop to exclude annotations and defailts

            if back:
                stack = []

                if type_params := getattr(ast, 'type_params', None):
                    stack.extend(type_params)

                stack.extend(scope_args.posonlyargs)
                stack.extend(scope_args.args)

                if vararg := scope_args.vararg:
                    stack.append(vararg)

                stack.extend(scope_args.kwonlyargs)

                if kwarg := scope_args.kwarg:
                    stack.append(scope_args.kwarg)

                if is_def:
                    stack.extend(ast.body)
                else:
                    stack.append(ast.body)

            else:
                stack = ast.body[::-1] if is_def else [ast.body]

                if kwarg := scope_args.kwarg:
                    stack.append(kwarg)

                stack.extend(scope_args.kwonlyargs[::-1])

                if vararg := scope_args.vararg:
                    stack.append(vararg)

                stack.extend(scope_args.args[::-1])
                stack.extend(scope_args.posonlyargs[::-1])

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
        if not (ast := stack.pop()):
            continue

        fst_ = ast.f

        if not _check_with_loc(fst_, with_loc):
            continue

        recurse_ = recurse

        while (sent := (yield fst_)) is not None:
            recurse_ = 1 if sent else False

        if not fst_.a:  # has been changed by the player
            fst_ = fst_.repath()

        ast = fst_.a  # could have just modified the ast

        if recurse_ is not True:
            if recurse_:  # user did send(True), walk this child unconditionally
                yield from fst_.walk(with_loc, self_=False, back=back)

        else:  # if walking scope then check if we got to another scope and walk the things from that which are visible in our scope
            if scope:
                recurse_ = False
                ast_cls = ast.__class__

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

                elif ast_cls is Lambda:
                    args = ast.args

                    if back:
                        stack.extend(args.defaults)
                        stack.extend(args.kw_defaults)
                    else:
                        stack.extend(args.kw_defaults[::-1])
                        stack.extend(args.defaults[::-1])

                elif ast_cls in (ListComp, SetComp, DictComp, GeneratorExp):
                    comp_first_iter = ast.generators[0].iter

                    gen = fst_.walk(with_loc, self_=False, back=back)

                    for f in gen:  # we want to return all NamedExpr.target and first top-level .iter, yeah, its ugly
                        a = f.a

                        if a is comp_first_iter:  # top-level iterator is in parent scope
                            subrecurse = recurse

                            while (sent := (yield f)) is not None:
                                subrecurse = sent

                            if subrecurse:
                                yield from f.walk(with_loc, self_=False, back=back)

                            gen.send(False)

                        elif (  # all NamedExprs are in parent scope
                            f.parent.a.__class__ is NamedExpr
                            and f.pfield.name == 'target'  # a.__class__ is Name
                        ):
                            subrecurse = recurse

                            while (sent := (yield f)) is not None:
                                subrecurse = sent

                            if not subrecurse:
                                gen.send(False)

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

                elif ast is scope_args:  # exclude defaults and kw_defaults from walk  TODO: ast is arguments
                    if back:
                        scope.extend(ast.posonlyargs)
                        scope.extend(ast.args)
                        scope.append(ast.vararg)
                        scope.extend(ast.kwonlyargs)
                        scope.append(ast.kwarg)

                    else:
                        scope.append(ast.kwarg)
                        scope.extend(ast.kwonlyargs[::-1])
                        scope.append(ast.vararg)
                        scope.extend(ast.args[::-1])
                        scope.extend(ast.posonlyargs[::-1])

                elif ast_cls is arg:
                    if fst_.parent.a is not scope_args:  # if arg not part of top-level node args then recurse normally
                        recurse_ = True

                elif ast_cls in ASTS_LEAF_TYPE_PARAM:
                    if not (is_def and fst_.parent is self):  # leave recurse off for type annotations and defaults in top-level node
                        recurse_ = True

                else:
                    recurse_ = True

            if recurse_:
                children = syntax_ordered_children(ast)

                stack.extend(children if back else children[::-1])


def next(self: fst.FST, with_loc: bool | Literal['all', 'own'] = True) -> fst.FST | None:  # TODO; redo
    """Get next sibling of `self` in syntactic order, only within parent.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.

    **Returns:**
    - `None` if last valid sibling in parent, otherwise next node.

    **Examples:**

    >>> f = FST('[[1, 2], [3, 4]]')

    >>> f.elts[0].next().src
    '[3, 4]'

    >>> print(f.elts[1].next())
    None
    """

    if not (parent := self.parent):
        return None

    aparent = parent.a
    name, idx = self.pfield

    while True:
        next = _AST_FIELDS_NEXT[(aparent.__class__, name)]

        if isinstance(next, int):  # special case?
            while True:
                match next:
                    case 0:  # from Dict.keys
                        next = 1
                        a = aparent.values[idx]

                    case 1:  # from Dict.values
                        next = 0

                        try:
                            if not (a := aparent.keys[(idx := idx + 1)]):
                                continue
                        except IndexError:
                            return None

                    case 2:  # from Compare.ops
                        next = 3
                        a = aparent.comparators[idx]

                    case 6:  # all the logic for Call.args and Call.keywords
                        if not (keywords := aparent.keywords):  # no keywords
                            try:
                                a = aparent.args[(idx := idx + 1)]
                            except IndexError:
                                return None

                        elif not (args := aparent.args):  # no args
                            try:
                                a = keywords[(idx := idx + 1)]
                            except IndexError:
                                return None

                        elif (star := args[-1]).__class__ is not Starred:  # both args and keywords but no Starred
                            if name == 'args':
                                try:
                                    a = args[(idx := idx + 1)]

                                except IndexError:
                                    name = 'keywords'
                                    a = keywords[(idx := 0)]

                            else:
                                try:
                                    a = keywords[(idx := idx + 1)]
                                except IndexError:
                                    return None

                        else:  # args, keywords AND Starred
                            if name == 'args':
                                try:
                                    a = args[(idx := idx + 1)]

                                    if (a is star
                                        and (
                                            ((kw := keywords[0]).lineno, kw.col_offset)
                                            < (star.lineno, star.col_offset)
                                    )):  # reached star and there is a keyword before it
                                        name = 'keywords'
                                        idx = 0
                                        a = kw

                                        break

                                except IndexError:  # ran off the end of args, past star, find first kw after it (if any)
                                    star_pos = (star.lineno, star.col_offset)

                                    for a in keywords:
                                        if (a.lineno, a.col_offset) > star_pos:
                                            break
                                    else:
                                        return None

                            else:  # name == 'keywords'
                                try:
                                    a = keywords[(idx := idx + 1)]

                                except IndexError:  # ran off the end of keywords, now need to check if star lives here
                                    if ((sa := self.a).lineno, sa.col_offset) < (star.lineno, star.col_offset):
                                        name = 'args'
                                        idx = len(args) - 1
                                        a = star

                                    else:
                                        return None

                                else:
                                    star_pos = (star.lineno, star.col_offset)

                                    if (((sa := self.a).lineno, sa.col_offset) < star_pos
                                        and (a.lineno, a.col_offset) > star_pos
                                    ):  # crossed star, jump back to it
                                        name = 'args'
                                        idx = len(args) - 1
                                        a = star

                    case 3:  # from Compare.comparators or Compare.left (via comparators)
                        next = 2

                        try:
                            a = aparent.ops[(idx := idx + 1)]
                        except IndexError:
                            return None

                    case 7:  # all the logic arguments
                        while True:
                            match name:
                                case 'posonlyargs':
                                    posonlyargs = aparent.posonlyargs
                                    defaults = aparent.defaults

                                    if (not defaults
                                        or (
                                            didx := (
                                                idx
                                                + (
                                                    (ldefaults := len(defaults))
                                                    - len(args := aparent.args)
                                                    - len(posonlyargs)
                                        ))) < 0
                                        or didx >= ldefaults
                                    ):
                                        try:
                                            a = posonlyargs[(idx := idx + 1)]

                                        except IndexError:
                                            name = 'args'
                                            idx = -1

                                            continue

                                    else:
                                        name = 'defaults'
                                        a = defaults[idx := didx]

                                case 'args':
                                    args = aparent.args
                                    defaults = aparent.defaults

                                    if (not defaults
                                        or (
                                            didx := (
                                                idx + ((ldefaults := len(defaults)) - len(args := aparent.args))
                                        )) < 0  # or didx >= ldefaults
                                    ):
                                        try:
                                            a = args[(idx := idx + 1)]

                                        except IndexError:
                                            name = 'vararg'

                                            if not (a := aparent.vararg):
                                                continue

                                    else:
                                        name = 'defaults'
                                        a = defaults[idx := didx]

                                case 'defaults':
                                    if idx == (ldefaults := len(aparent.defaults)) - 1:  # end of defaults
                                        name = 'vararg'

                                        if not (a := aparent.vararg):
                                            continue

                                    elif (idx := idx + len(args := aparent.args) - ldefaults + 1) >= 0:
                                        name = 'args'
                                        a = args[idx]

                                    else:
                                        name = 'posonlyargs'
                                        a = (posonlyargs := aparent.posonlyargs)[(idx := idx + len(posonlyargs))]

                                case 'vararg':
                                    if kwonlyargs := aparent.kwonlyargs:
                                        name = 'kwonlyargs'
                                        a = kwonlyargs[(idx := 0)]

                                    elif a := aparent.kwarg:
                                        name = 'kwarg'
                                    else:
                                        return None

                                case 'kwonlyargs':
                                    kwonlyargs = aparent.kwonlyargs

                                    if a := aparent.kw_defaults[idx]:
                                        name = 'kw_defaults'

                                    else:
                                        try:
                                            a = kwonlyargs[(idx := idx + 1)]

                                        except IndexError:
                                            if a := aparent.kwarg:
                                                name = 'kwarg'
                                            else:
                                                return None

                                case 'kw_defaults':
                                    try:
                                        a = aparent.kwonlyargs[(idx := idx + 1)]

                                    except IndexError:
                                        if a := aparent.kwarg:
                                            name = 'kwarg'
                                        else:
                                            return None

                                    name = 'kwonlyargs'

                                case 'kwarg':
                                    raise RuntimeError('should not get here')

                            break

                    case 4:  # from MatchMapping.keys
                        next = 5
                        a = aparent.patterns[idx]

                    case 5:  # from MatchMapping.patterns
                        next = 4

                        try:
                            if not (a := aparent.keys[(idx := idx + 1)]):  # OUR OWN SPECIAL CASE: MatchMapping.keys cannot normally be None but we make use of this temporarily in some operations
                                continue
                        except IndexError:
                            return None

                if _check_with_loc(f := a.f, with_loc):
                    return f

        elif idx is not None:
            sibling = getattr(aparent, name)

            while True:
                try:
                    if not (a := sibling[(idx := idx + 1)]):  # who knows where a `None` might pop up "next" these days... xD
                        continue

                except IndexError:
                    break

                if _check_with_loc(f := a.f, with_loc):
                    return f

        while next is not None:
            if isinstance(next, str):
                name = next

                if isinstance(sibling := getattr(aparent, next, None), AST):  # None because we know about fields from future python versions
                    if _check_with_loc(f := sibling.f, with_loc):
                        return f

                elif isinstance(sibling, list) and sibling:
                    idx = -1

                    break

                next = _AST_FIELDS_NEXT[(aparent.__class__, name)]

                continue

            # non-str next, special case

            match next:
                case 2:  # from Compare.left
                    name = 'comparators'  # will cause to get .ops[0]
                    idx = -1

                case 3:  # OUR OWN SPECIAL CASE: from empty Compare.comparators, not normally allowed
                    idx = -1

                case 6:  # from Call.func
                    idx = -1  # will cause to get .args[0]

            break

        else:
            break

        continue

    return None


def prev(self: fst.FST, with_loc: bool | Literal['all', 'own'] = True) -> fst.FST | None:  # TODO; redo
    """Get previous sibling of `self` in syntactic order, only within parent.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.

    **Returns:**
    - `None` if first valid sibling in parent, otherwise previous node.

    **Examples:**

    >>> f = FST('[[1, 2], [3, 4]]')

    >>> f.elts[1].prev().src
    '[1, 2]'

    >>> print(f.elts[0].prev())
    None
    """

    if not (parent := self.parent):
        return None

    aparent = parent.a
    name, idx = self.pfield

    while True:
        prev = _AST_FIELDS_PREV[(aparent.__class__, name)]

        if isinstance(prev, int):  # special case?
            while True:
                match prev:
                    case 0:  # from Dict.keys
                        if not idx:
                            return None

                        else:
                            prev = 1
                            a = aparent.values[(idx := idx - 1)]

                    case 1:  # from Dict.values
                        prev = 0

                        if not (a := aparent.keys[idx]):
                            continue

                    case 6:
                        if not (keywords := aparent.keywords):  # no keywords
                            if idx:
                                a = aparent.args[(idx := idx - 1)]

                            else:
                                name = 'func'
                                a = aparent.func

                        elif not (args := aparent.args):  # no args
                            if idx:
                                a = keywords[(idx := idx - 1)]

                            else:
                                name = 'func'
                                a = aparent.func

                        elif (star := args[-1]).__class__ is not Starred:  # both args and keywords but no Starred
                            if name == 'args':
                                if idx:
                                    a = aparent.args[(idx := idx - 1)]

                                else:
                                    name = 'func'
                                    a = aparent.func

                            else:
                                if idx:
                                    a = keywords[(idx := idx - 1)]

                                else:
                                    name = 'args'
                                    a = args[(idx := len(args) - 1)]

                        else:  # args, keywords AND Starred
                            if name == 'args':
                                if idx == len(args) - 1:  # is star
                                    star_pos = (star.lineno, star.col_offset)

                                    for i in range(len(keywords) - 1, -1, -1):
                                        if ((kw := keywords[i]).lineno, kw.col_offset) < star_pos:
                                            name = 'keywords'
                                            idx = i
                                            a = kw

                                            break

                                    else:
                                        if idx:
                                            a = args[(idx := idx - 1)]

                                        else:
                                            name = 'func'
                                            a = aparent.func

                                elif idx:
                                    a = args[(idx := idx - 1)]

                                else:
                                    name = 'func'
                                    a = aparent.func

                            else:  # name == 'keywords'
                                star_pos = (star.lineno, star.col_offset)

                                if not idx:
                                    name = 'args'

                                    if ((sa := self.a).lineno, sa.col_offset) > star_pos:  # all keywords above star so pass on to star
                                        idx = len(args) - 1
                                        a = star

                                    elif (largs := len(args)) < 2:  # no args left, we done here
                                        name = 'func'
                                        a = aparent.func

                                    else:  # some args left, go to those
                                        a = args[(idx := largs - 2)]

                                else:
                                    a = keywords[(idx := idx - 1)]

                                    if ((a.lineno, a.col_offset) < star_pos
                                        and ((sa := self.a).lineno, sa.col_offset) > star_pos
                                    ):  # crossed star walking back, return star
                                        name = 'args'
                                        idx = len(args) - 1
                                        a = star

                    case 2:  # from Compare.ops
                        if not idx:
                            prev = 'left'

                            break

                        else:
                            prev = 3
                            a = aparent.comparators[(idx := idx - 1)]

                    case 3:  # from Compare.comparators
                        prev = 2
                        a = aparent.ops[idx]

                    case 7:
                        while True:
                            match name:
                                case 'posonlyargs':
                                    posonlyargs = aparent.posonlyargs
                                    defaults = aparent.defaults

                                    if ((didx := idx - len(aparent.args) - len(posonlyargs) + len(defaults) - 1)
                                        >= 0
                                    ):
                                        name = 'defaults'
                                        a = defaults[(idx := didx)]

                                    elif idx > 0:
                                        a = posonlyargs[(idx := idx - 1)]
                                    else:
                                        return None

                                case 'args':
                                    args = aparent.args
                                    defaults = aparent.defaults

                                    if (didx := idx - len(args) + len(defaults) - 1) >= 0:
                                        name = 'defaults'
                                        a = defaults[(idx := didx)]

                                    elif idx > 0:
                                        a = args[(idx := idx - 1)]

                                    elif posonlyargs := aparent.posonlyargs:
                                        name = 'posonlyargs'
                                        a = posonlyargs[(idx := len(posonlyargs) - 1)]

                                    else:
                                        return None

                                case 'defaults':
                                    args = aparent.args
                                    defaults = aparent.defaults

                                    if (idx := idx + len(args) - len(defaults)) >= 0:
                                        name = 'args'
                                        a = args[idx]

                                    else:
                                        name = 'posonlyargs'
                                        a = (posonlyargs := aparent.posonlyargs)[idx + len(posonlyargs)]

                                case 'vararg':
                                    if defaults := aparent.defaults:
                                        name = 'defaults'
                                        a = defaults[(idx := len(defaults) - 1)]

                                    elif args := aparent.args:
                                        name = 'args'
                                        a = args[(idx := len(args) - 1)]

                                    elif posonlyargs := aparent.posonlyargs:
                                        name = 'posonlyargs'
                                        a = posonlyargs[(idx := len(posonlyargs) - 1)]

                                    else:
                                        return None

                                case 'kwonlyargs':
                                    if not idx:
                                        name = 'vararg'

                                        if not (a := aparent.vararg):
                                            continue

                                    elif a := aparent.kw_defaults[(idx := idx - 1)]:
                                        name = 'kw_defaults'

                                    else:
                                        a = aparent.kwonlyargs[idx]

                                case 'kw_defaults':
                                    name = 'kwonlyargs'
                                    a = aparent.kwonlyargs[idx]

                                case 'kwarg':
                                    if kw_defaults := aparent.kw_defaults:
                                        if a := kw_defaults[(idx := len(kw_defaults) - 1)]:
                                            name = 'kw_defaults'

                                        else:
                                            name = 'kwonlyargs'
                                            a = (kwonlyargs := aparent.kwonlyargs)[(idx := len(kwonlyargs) - 1)]

                                    else:
                                        name = 'vararg'

                                        if not (a := aparent.vararg):
                                            continue

                            break

                    case 4:  # from MatchMapping.keys
                        if not idx:
                            return None

                        else:
                            prev = 5
                            a = aparent.patterns[(idx := idx - 1)]

                    case 5:  # from MatchMapping.patterns
                        prev = 4

                        if not (a := aparent.keys[idx]):  # OUR OWN SPECIAL CASE: MatchMapping.keys cannot normally be None but we make use of this temporarily in some operations
                            continue

                if _check_with_loc(f := a.f, with_loc):
                    return f

        else:
            sibling = getattr(aparent, name)

            while idx:
                if not (a := sibling[(idx := idx - 1)]):
                    continue

                if _check_with_loc(f := a.f, with_loc):
                    return f

        while prev is not None:
            if isinstance(prev, str):
                name = prev

                if isinstance(sibling := getattr(aparent, prev, None), AST):  # None because could have fields from future python versions
                    if _check_with_loc(f := sibling.f, with_loc):
                        return f

                elif isinstance(sibling, list) and (idx := len(sibling)):
                    break

                prev = _AST_FIELDS_PREV[(aparent.__class__, name)]

                continue

            # non-str prev, special case

            raise RuntimeError('should not get here')  # break  # when entrable special cases from ahead appear in future py versions add them here

        else:
            break

        continue

    return None


def first_child(self: fst.FST, with_loc: bool | Literal['all', 'own'] = True) -> fst.FST | None:
    """Get first valid child in syntactic order.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.

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

    for name in AST_FIELDS[(a := self.a).__class__]:
        if child := getattr(a, name, None):
            if isinstance(child, AST):
                if _check_with_loc(f := child.f, with_loc):
                    return f

            elif isinstance(child, list):
                if (c := child[0]) and _check_with_loc(f := c.f, with_loc):
                    return f

                return fst.FST(Pass(), self, astfield(name, 0)).next(with_loc)  # Pass() is a hack just to have a simple AST node

    return None


def last_child(self: fst.FST, with_loc: bool | Literal['all', 'own'] = True) -> fst.FST | None:
    """Get last valid child in syntactic order.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.

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

    if ast_cls is Call and ast.args and (keywords := ast.keywords) and ast.args[-1].__class__ is Starred:  # super-special case Call with args and keywords and a Starred, it could be anywhere in there, including after last keyword, defer to prev() logic
        fst_ = fst.FST(f := Pass(), self, astfield('keywords', len(keywords)))
        f.lineno = 0x7fffffffffffffff
        f.col_offset = 0

        return fst_.prev(with_loc)

    for name in reversed(AST_FIELDS[ast_cls]):
        if child := getattr(ast, name, None):
            if isinstance(child, AST):
                if _check_with_loc(f := child.f, with_loc):
                    return f

            elif isinstance(child, list):
                if (c := child[-1]) and _check_with_loc(f := c.f, with_loc):
                    return f

                return fst.FST(Pass(), self, astfield(name, len(child) - 1)).prev(with_loc)  # Pass() is a hack just to have a simple AST node

    return None


def last_header_child(self: fst.FST, with_loc: bool | Literal['all', 'own'] = True) -> fst.FST | None:
    r"""Get last valid child in syntactic order in a block header (before the `:`), e.g. the `something` in
    `if something: pass`.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.

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

    if _check_with_loc(f := child.f, with_loc):
        return f

    return self.prev_child(f, with_loc)


def next_child(
    self: fst.FST, from_child: fst.FST | None, with_loc: bool | Literal['all', 'own'] = True
) -> fst.FST | None:
    """Get the next child in syntactic order, meant for simple iteration.

    This is a slower way to iterate vs. `walk()`, but will work correctly if ANYTHING in the tree is modified during
    the walk as long as the replaced node and its parent is used for the following call.

    **Parameters:**
    - `from_child`: Child node we are coming from which may or may not have location.
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.

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
    ...     if isinstance(n.a, Name):
    ...         n = n.replace(n.id[::-1])
    >>> f.src
    '[siht, _si, desraper, hcae, pets, _dna, llits, sklaw, ko]'
    """

    return self.first_child(with_loc) if from_child is None else from_child.next(with_loc)


def prev_child(
    self: fst.FST, from_child: fst.FST | None, with_loc: bool | Literal['all', 'own'] = True
) -> fst.FST | None:
    """Get the previous child in syntactic order, meant for simple iteration.

    This is a slower way to iterate vs. `walk()`, but will work correctly if ANYTHING in the tree is modified during the
    walk as long as the replaced node and its parent is used for the following call.

    **Parameters:**
    - `from_child`: Child node we are coming from which may or may not have location.
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.

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
    ...     if isinstance(n.a, Name):
    ...         n = n.replace(n.id[::-1])
    >>> f.src
    '[siht, _si, desraper, hcae, pets, _dna, llits, sklaw, ko]'
    """

    return self.last_child(with_loc) if from_child is None else from_child.prev(with_loc)


def step_fwd(
    self: fst.FST, with_loc: bool | Literal['all', 'own', 'allown'] = True, *, recurse_self: bool = True
) -> fst.FST | None:
    """Step forward in the tree in syntactic order, as if `walk()`ing forward, NOT the inverse of `step_back()`. Will
    walk up parents and down children to get the next node, returning `None` only when we are at the end of the whole
    thing.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.
        - `'allown'` Same as `'own'` but recurse into nodes with non-own locations (even though those nodes are not
            returned). This is only really meant for internal use to safely call from `.loc` location calculation.
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
    ...     if isinstance(n.a, Name):
    ...         n = n.replace(n.id[::-1])
    ...     if not (n := n.step_fwd()):
    ...         break
    >>> f.src
    '[siht, [_si, [desraper, hcae], pets, _dna, llits], sklaw, ko]'
    """

    if allown := with_loc == 'allown':
        with_loc = True

    while True:
        if not recurse_self or not (fst_ := self.first_child(with_loc)):
            recurse_self = True

            while not (fst_ := self.next(with_loc)):
                if not (self := self.parent):
                    return None

        if not allown or fst_.has_own_loc:
            break

        self = fst_

    return fst_


def step_back(
    self: fst.FST, with_loc: bool | Literal['all', 'own', 'allown'] = True, *, recurse_self: bool = True
) -> fst.FST | None:
    """Step backward in the tree in syntactic order, as if `walk()`ing backward, NOT the inverse of `step_fwd()`.
    Will walk up parents and down children to get the next node, returning `None` only when we are at the beginning
    of the whole thing.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have intrinsic `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually
            arguments present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they
            do not always have a well defined location).
        - `'own'`: Only nodes with their own intrinsic `AST` locations, same as `True` but excludes those larger
            nodes with calculated locations.
        - `'allown'` Same as `'own'` but recurse into nodes with non-own locations (even though those nodes are not
            returned). This is only really meant for internal use to safely call from `.loc` location calculation.
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
    ...     if isinstance(n.a, Name):
    ...         n = n.replace(n.id[::-1])
    ...     if not (n := n.step_back()):
    ...         break
    >>> f.src
    '[siht, [_si, [desraper, hcae], pets, _dna, llits], sklaw, ko]'
    """

    if allown := with_loc == 'allown':
        with_loc = True

    while True:
        if not recurse_self or not (fst_ := self.last_child(with_loc)):
            recurse_self = True

            while not (fst_ := self.prev(with_loc)):
                if not (self := self.parent):
                    return None

        if not allown or fst_.has_own_loc:
            break

        self = fst_

    return fst_
