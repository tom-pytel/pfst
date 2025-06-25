"""Siblings, children and walk, all in syntactic order."""

from __future__ import annotations

from ast import *
from typing import Generator, Literal

from .astutil import *

from .misc import astfield

_AST_FIELDS_NEXT: dict[tuple[type[AST], str], str | None] = dict(sum((  # next field name from AST class and current field name
    [] if not fields else
    [((cls, fields[0]), None)] if len(fields) == 1 else
    [((cls, fields[i]), fields[i + 1]) for i in range(len(fields) - 1)] + [((cls, fields[-1]), None)]
    for cls, fields in AST_FIELDS.items()), start=[])
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
    [((cls, fields[0]), None)] if len(fields) == 1 else
    [((cls, fields[i + 1]), fields[i]) for i in range(len(fields) - 1)] + [((cls, fields[0]), None)]
    for cls, fields in AST_FIELDS.items()), start=[])
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


def _with_loc(fst: FST, with_loc: bool | Literal['all', 'own'] = True) -> bool:
    """Check location condition on node. Safe for low level because doesn't use `.loc` calculation machinery."""

    if not with_loc:
        return True

    if with_loc is True:
        return not (isinstance(a := fst.a, (expr_context, boolop, operator, unaryop, cmpop)) or
                    (isinstance(a, arguments) and not a.posonlyargs and not a.args and not a.vararg and
                    not a.kwonlyargs and not a.kwarg))

    if with_loc == 'all':
        return not (isinstance(a := fst.a, (expr_context, boolop)) or
                    (isinstance(a, arguments) and not a.posonlyargs and not a.args and not a.vararg and
                    not a.kwonlyargs and not a.kwarg))

    return fst.has_own_loc  # with_loc == 'own'


# ----------------------------------------------------------------------------------------------------------------------

def next(self: FST, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:  # TODO: refactor
    """Get next sibling of `self` in syntactic order, only within parent.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.

    **Returns:**
    - `None` if last valid sibling in parent, otherwise next node.

    **Examples:**
    ```py
    >>> f = FST('[[1, 2], [3, 4]]')
    >>> f.elts[0].next().src
    '[3, 4]'

    >>> print(f.elts[1].next())
    None
    ```
    """

    if not (parent := self.parent):
        return None

    aparent   = parent.a
    name, idx = self.pfield

    while True:
        next = _AST_FIELDS_NEXT[(aparent.__class__, name)]

        if isinstance(next, int):  # special case?
            while True:
                match next:
                    case 0:  # from Dict.keys
                        next = 1
                        a    = aparent.values[idx]

                    case 1:  # from Dict.values
                        next = 0

                        try:
                            if not (a := aparent.keys[(idx := idx + 1)]):
                                continue
                        except IndexError:
                            return None

                    case 2:  # from Compare.ops
                        next = 3
                        a    = aparent.comparators[idx]

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

                        elif not isinstance(star := args[-1], Starred):  # both args and keywords but no Starred
                            if name == 'args':
                                try:
                                    a = args[(idx := idx + 1)]

                                except IndexError:
                                    name = 'keywords'
                                    a    = keywords[(idx := 0)]

                            else:
                                try:
                                    a = keywords[(idx := idx + 1)]
                                except IndexError:
                                    return None

                        else:  # args, keywords AND Starred
                            if name == 'args':
                                try:
                                    a = args[(idx := idx + 1)]

                                    if (a is star and ((kw := keywords[0]).lineno, kw.col_offset) <
                                        (star.lineno, star.col_offset)
                                    ):  # reached star and there is a keyword before it
                                        name = 'keywords'
                                        idx  = 0
                                        a    = kw

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
                                        idx  = len(args) - 1
                                        a    = star

                                    else:
                                        return None

                                else:
                                    star_pos = (star.lineno, star.col_offset)

                                    if (((sa := self.a).lineno, sa.col_offset) < star_pos and
                                        (a.lineno, a.col_offset) > star_pos
                                    ):  # crossed star, jump back to it
                                        name = 'args'
                                        idx  = len(args) - 1
                                        a    = star

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
                                    defaults    = aparent.defaults

                                    if (not defaults or (didx := (idx + ((ldefaults := len(defaults)) -
                                        len(args := aparent.args) - len(posonlyargs)))) < 0 or didx >= ldefaults
                                    ):
                                        try:
                                            a = posonlyargs[(idx := idx + 1)]

                                        except IndexError:
                                            name = 'args'
                                            idx  = -1

                                            continue

                                    else:
                                        name = 'defaults'
                                        a    = defaults[idx := didx]

                                case 'args':
                                    args     = aparent.args
                                    defaults = aparent.defaults

                                    if (not defaults or (didx := (idx + ((ldefaults := len(defaults)) -
                                        len(args := aparent.args)))) < 0  # or didx >= ldefaults
                                    ):
                                        try:
                                            a = args[(idx := idx + 1)]

                                        except IndexError:
                                            name = 'vararg'

                                            if not (a := aparent.vararg):
                                                continue

                                    else:
                                        name = 'defaults'
                                        a    = defaults[idx := didx]

                                case 'defaults':
                                    if idx == (ldefaults := len(aparent.defaults)) - 1:  # end of defaults
                                        name = 'vararg'

                                        if not (a := aparent.vararg):
                                            continue

                                    elif (idx := idx + len(args := aparent.args) - ldefaults + 1) >= 0:
                                        name = 'args'
                                        a    = args[idx]

                                    else:
                                        name = 'posonlyargs'
                                        a    = (posonlyargs := aparent.posonlyargs)[(idx := idx + len(posonlyargs))]

                                case 'vararg':
                                    if kwonlyargs := aparent.kwonlyargs:
                                        name = 'kwonlyargs'
                                        a    = kwonlyargs[(idx := 0)]

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
                        a    = aparent.patterns[idx]

                    case 5:  # from MatchMapping.patterns
                        next = 4

                        try:
                            a = aparent.keys[(idx := idx + 1)]
                        except IndexError:
                            return None

                if _with_loc(f := a.f, with_loc):
                    return f

        elif idx is not None:
            sibling = getattr(aparent, name)

            while True:
                try:
                    if not (a := sibling[(idx := idx + 1)]):  # who knows where a `None` might pop up "next" these days... xD
                        continue

                except IndexError:
                    break

                if _with_loc(f := a.f, with_loc):
                    return f

        while next is not None:
            if isinstance(next, str):
                name = next

                if isinstance(sibling := getattr(aparent, next, None), AST):  # None because we know about fields from future python versions
                    if _with_loc(f := sibling.f, with_loc):
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
                    idx  = -1

                case 6:  # from Call.func
                    idx  = -1  # will cause to get .args[0]

            break

        else:
            break

        continue

    return None


def prev(self: FST, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:  # TODO: refactor
    """Get previous sibling of `self` in syntactic order, only within parent.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.

    **Returns:**
    - `None` if first valid sibling in parent, otherwise previous node.

    **Examples:**
    ```py
    >>> f = FST('[[1, 2], [3, 4]]')
    >>> f.elts[1].prev().src
    '[1, 2]'

    >>> print(f.elts[0].prev())
    None
    ```
    """

    if not (parent := self.parent):
        return None

    aparent   = parent.a
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
                            a    = aparent.values[(idx := idx - 1)]

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
                                a    = aparent.func

                        elif not (args := aparent.args):  # no args
                            if idx:
                                a = keywords[(idx := idx - 1)]

                            else:
                                name = 'func'
                                a    = aparent.func

                        elif not isinstance(star := args[-1], Starred):  # both args and keywords but no Starred
                            if name == 'args':
                                if idx:
                                    a = aparent.args[(idx := idx - 1)]

                                else:
                                    name = 'func'
                                    a    = aparent.func

                            else:
                                if idx:
                                    a = keywords[(idx := idx - 1)]

                                else:
                                    name = 'args'
                                    a    = args[(idx := len(args) - 1)]

                        else:  # args, keywords AND Starred
                            if name == 'args':
                                if idx == len(args) - 1:  # is star
                                    star_pos = (star.lineno, star.col_offset)

                                    for i in range(len(keywords) - 1, -1, -1):
                                        if ((kw := keywords[i]).lineno, kw.col_offset) < star_pos:
                                            name = 'keywords'
                                            idx  = i
                                            a    = kw

                                            break

                                    else:
                                        if idx:
                                            a = args[(idx := idx - 1)]

                                        else:
                                            name = 'func'
                                            a    = aparent.func

                                elif idx:
                                    a = args[(idx := idx - 1)]

                                else:
                                    name = 'func'
                                    a    = aparent.func

                            else:  # name == 'keywords'
                                star_pos = (star.lineno, star.col_offset)

                                if not idx:
                                    name = 'args'

                                    if ((sa := self.a).lineno, sa.col_offset) > star_pos:  # all keywords above star so pass on to star
                                        idx  = len(args) - 1
                                        a    = star

                                    elif (largs := len(args)) < 2:  # no args left, we done here
                                        name = 'func'
                                        a    = aparent.func

                                    else:  # some args left, go to those
                                        a = args[(idx := largs - 2)]

                                else:
                                    a = keywords[(idx := idx - 1)]

                                    if ((a.lineno, a.col_offset) < star_pos and
                                        ((sa := self.a).lineno, sa.col_offset) > star_pos
                                    ):  # crossed star walking back, return star
                                        name = 'args'
                                        idx  = len(args) - 1
                                        a    = star

                    case 2:  # from Compare.ops
                        if not idx:
                            prev = 'left'

                            break

                        else:
                            prev = 3
                            a    = aparent.comparators[(idx := idx - 1)]

                    case 3:  # from Compare.comparators
                        prev = 2
                        a    = aparent.ops[idx]

                    case 7:
                        while True:
                            match name:
                                case 'posonlyargs':
                                    posonlyargs = aparent.posonlyargs
                                    defaults    = aparent.defaults

                                    if ((didx := idx - len(aparent.args) - len(posonlyargs) + len(defaults) - 1) >=
                                        0
                                    ):
                                        name = 'defaults'
                                        a    = defaults[(idx := didx)]

                                    elif idx > 0:
                                        a = posonlyargs[(idx := idx - 1)]
                                    else:
                                        return None

                                case 'args':
                                    args     = aparent.args
                                    defaults = aparent.defaults

                                    if (didx := idx - len(args) + len(defaults) - 1) >= 0:
                                        name = 'defaults'
                                        a    = defaults[(idx := didx)]

                                    elif idx > 0:
                                        a = args[(idx := idx - 1)]

                                    elif posonlyargs := aparent.posonlyargs:
                                        name = 'posonlyargs'
                                        a    = posonlyargs[(idx := len(posonlyargs) - 1)]

                                    else:
                                        return None

                                case 'defaults':
                                    args     = aparent.args
                                    defaults = aparent.defaults

                                    if (idx := idx + len(args) - len(defaults)) >= 0:
                                        name = 'args'
                                        a    = args[idx]

                                    else:
                                        name = 'posonlyargs'
                                        a    = (posonlyargs := aparent.posonlyargs)[idx + len(posonlyargs)]

                                case 'vararg':
                                    if defaults := aparent.defaults:
                                        name = 'defaults'
                                        a    = defaults[(idx := len(defaults) - 1)]

                                    elif args := aparent.args:
                                        name = 'args'
                                        a    = args[(idx := len(args) - 1)]

                                    elif posonlyargs := aparent.posonlyargs:
                                        name = 'posonlyargs'
                                        a    = posonlyargs[(idx := len(posonlyargs) - 1)]

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
                                    a    = aparent.kwonlyargs[idx]

                                case 'kwarg':
                                    if kw_defaults := aparent.kw_defaults:
                                        if a := kw_defaults[(idx := len(kw_defaults) - 1)]:
                                            name = 'kw_defaults'

                                        else:
                                            name = 'kwonlyargs'
                                            a    = (kwonlyargs := aparent.kwonlyargs)[(idx := len(kwonlyargs) - 1)]

                                    else:
                                        name = 'vararg'

                                        if not (a := aparent.vararg):
                                            continue

                            break

                    case 4:  # from Keys.keys
                        if not idx:
                            return None

                        else:
                            prev = 5
                            a    = aparent.patterns[(idx := idx - 1)]

                    case 5:  # from Keys.patterns
                        prev = 4
                        a    = aparent.keys[idx]

                if _with_loc(f := a.f, with_loc):
                    return f

        else:
            sibling = getattr(aparent, name)

            while idx:
                if not (a := sibling[(idx := idx - 1)]):
                    continue

                if _with_loc(f := a.f, with_loc):
                    return f

        while prev is not None:
            if isinstance(prev, str):
                name = prev

                if isinstance(sibling := getattr(aparent, prev, None), AST):  # None because could have fields from future python versions
                    if _with_loc(f := sibling.f, with_loc):
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


def first_child(self: FST, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:
    """Get first valid child in syntactic order.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.

    **Returns:**
    - `None` if no valid children, otherwise first valid child.

    **Examples:**
    ```py
    >>> f = FST('def f(a: list[str], /, reject: int, *c, d=100, **e): pass')
    >>> f.first_child().src
    'a: list[str], /, reject: int, *c, d=100, **e'

    >>> f.args.first_child().src
    'a: list[str]'

    >>> f.args.first_child().first_child().src
    'list[str]'
    ```
    """

    for name in AST_FIELDS[(a := self.a).__class__]:
        if (child := getattr(a, name, None)):
            if isinstance(child, AST):
                if _with_loc(f := child.f, with_loc):
                    return f

            elif isinstance(child, list):
                if (c := child[0]) and _with_loc(f := c.f, with_loc):
                    return f

                return FST(Pass(), self, astfield(name, 0)).next(with_loc)  # Pass() is a hack just to have a simple AST node

    return None


def last_child(self: FST, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:
    """Get last valid child in syntactic order.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.

    **Returns:**
    - `None` if no valid children, otherwise last valid child.

    **Examples:**
    ```py
    >>> f = FST('def f(a: list[str], /, reject: int, *c, d=100, **e): pass')
    >>> f.last_child().src
    'pass'

    >>> f.args.last_child().src
    'e'
    ```
    """

    if (isinstance(a := self.a, Call)) and a.args and (keywords := a.keywords) and isinstance(a.args[-1], Starred):  # super-special case Call with args and keywords and a Starred, it could be anywhere in there, including after last keyword, defer to prev() logic
        fst          = FST(f := Pass(), self, astfield('keywords', len(keywords)))
        f.lineno     = 0x7fffffffffffffff
        f.col_offset = 0

        return fst.prev(with_loc)

    for name in reversed(AST_FIELDS[(a := self.a).__class__]):
        if (child := getattr(a, name, None)):
            if isinstance(child, AST):
                if _with_loc(f := child.f, with_loc):
                    return f

            elif isinstance(child, list):
                if (c := child[-1]) and _with_loc(f := c.f, with_loc):
                    return f

                return FST(Pass(), self, astfield(name, len(child) - 1)).prev(with_loc)  # Pass() is a hack just to have a simple AST node

    return None


def last_header_child(self: FST, with_loc: bool | Literal['all', 'own'] = True) -> FST | None:
    r"""Get last valid child in syntactic order in a block header (before the `:`), e.g. the `something` in
    `if something: pass`.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.

    **Returns:**
    - `None` if no valid children or if `self` is not a block statement, otherwise last valid child in the block header.

    **Examples:**
    ```py
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
    ```
    """

    if not (child := last_block_header_child(self.a)):
        return None

    if _with_loc(f := child.f, with_loc):
        return f

    return self.prev_child(f, with_loc)


def next_child(self: FST, from_child: FST | None, with_loc: bool | Literal['all', 'own'] = True
               ) -> FST | None:
    """Get the next child in syntactic order, meant for simple iteration.

    This is a slower way to iterate vs. `walk()`, but will work correctly if ANYTHING in the tree is modified during the
    walk as long as the replaced node and its parent is used for the following call.

    **Parameters:**
    - `from_child`: Child node we are coming from which may or may not have location.
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.

    **Returns:**
    - `None` if last valid child in `self`, otherwise next child node.

    **Examples:**
    ```py
    >>> f = FST('[[1, 2], [3, 4]]')
    >>> f.next_child(f.elts[0]).src
    '[3, 4]'

    >>> print(f.next_child(f.elts[1]))
    None

    >>> f = FST('[this, is_, reparsed, each, step, and_, still, walks, ok]')
    >>> n = None
    >>> while n := f.next_child(n):
    ...     if isinstance(n.a, Name):
    ...         n = n.replace(n.id[::-1], raw=True)  # raw here reparses all nodes
    >>> f.src
    '[siht, _si, desraper, hcae, pets, _dna, llits, sklaw, ko]'
    ```
    """

    return self.first_child(with_loc) if from_child is None else from_child.next(with_loc)


def prev_child(self: FST, from_child: FST | None, with_loc: bool | Literal['all', 'own'] = True
               ) -> FST | None:
    """Get the previous child in syntactic order, meant for simple iteration.

    This is a slower way to iterate vs. `walk()`, but will work correctly if ANYTHING in the tree is modified during the
    walk as long as the replaced node and its parent is used for the following call.

    **Parameters:**
    - `from_child`: Child node we are coming from which may or may not have location.
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.

    **Returns:**
    - `None` if first valid child in `self`, otherwise previous child node.

    **Examples:**
    ```py
    >>> f = FST('[[1, 2], [3, 4]]')
    >>> f.prev_child(f.elts[1]).src
    '[1, 2]'

    >>> print(f.prev_child(f.elts[0]))
    None

    >>> f = FST('[this, is_, reparsed, each, step, and_, still, walks, ok]')
    >>> n = None
    >>> while n := f.prev_child(n):
    ...     if isinstance(n.a, Name):
    ...         n = n.replace(n.id[::-1], raw=True)  # raw here reparses all nodes
    >>> f.src
    '[siht, _si, desraper, hcae, pets, _dna, llits, sklaw, ko]'
    ```
    """

    return self.last_child(with_loc) if from_child is None else from_child.prev(with_loc)


def step_fwd(self: FST, with_loc: bool | Literal['all', 'own', 'allown'] = True, *, recurse_self: bool = True,
             ) -> FST | None:
    """Step forward in the tree in syntactic order, as if `walk()`ing forward, NOT the inverse of `step_back()`. Will
    walk up parents and down children to get the next node, returning `None` only when we are at the end of the whole
    thing.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.
        - `'allown'` Same as `'own'` but recurse into nodes with non-own locations (even though those nodes are not
            returned). This is only really meant for internal use to safely call from `.loc` location calculation.
    - `recurse_self`: Whether to allow recursion into `self` to return children or move directly to next nodes of `self`
        on start.

    **Returns:**
    - `None` if last valid node in tree, otherwise next node in order.

    **Examples:**
    ```py
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
    ...         n = n.replace(n.id[::-1], raw=True)  # raw here reparses all nodes
    ...     if not (n := n.step_fwd()):
    ...         break
    >>> f.src
    '[siht, [_si, [desraper, hcae], pets, _dna, llits], sklaw, ko]'
    ```
    """

    if allown := with_loc == 'allown':
        with_loc = True

    while True:
        if not recurse_self or not (fst := self.first_child(with_loc)):
            recurse_self = True

            while not (fst := self.next(with_loc)):
                if not (self := self.parent):
                    return None

        if not allown or fst.has_own_loc:
            break

        self = fst

    return fst


def step_back(self: FST, with_loc: bool | Literal['all', 'own', 'allown'] = True, *, recurse_self: bool = True,
              ) -> FST | None:
    """Step backward in the tree in syntactic order, as if `walk()`ing backward, NOT the inverse of `step_fwd()`. Will
    walk up parents and down children to get the next node, returning `None` only when we are at the beginning of the
    whole thing.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.
        - `'allown'` Same as `'own'` but recurse into nodes with non-own locations (even though those nodes are not
            returned). This is only really meant for internal use to safely call from `.loc` location calculation.
    - `recurse_self`: Whether to allow recursion into `self` to return children or move directly to previous nodes of
        `self` on start.

    **Returns:**
    - `None` if first valid node in tree, otherwise previous node in order.

    **Examples:**
    ```py
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
    ...         n = n.replace(n.id[::-1], raw=True)  # raw here reparses all nodes
    ...     if not (n := n.step_back()):
    ...         break
    >>> f.src
    '[siht, [_si, [desraper, hcae], pets, _dna, llits], sklaw, ko]'
    ```
    """

    if allown := with_loc == 'allown':
        with_loc = True

    while True:
        if not recurse_self or not (fst := self.last_child(with_loc)):
            recurse_self = True

            while not (fst := self.prev(with_loc)):
                if not (self := self.parent):
                    return None

        if not allown or fst.has_own_loc:
            break

        self = fst

    return fst


def walk(self: FST, with_loc: bool | Literal['all', 'own'] = False, *, self_: bool = True, recurse: bool = True,
         scope: bool = False, back: bool = False) -> Generator[FST, bool, None]:
    r"""Walk `self` and descendants in syntactic order. When walking, you can `send(False)` to the generator to skip
    recursion into the current child. `send(True)` to allow recursion into child if called with `recurse=False` or
    `scope=True` would otherwise disallow it. Can send multiple times, last value sent takes effect.

    The walk is defined forwards or backwards in that it returns a parent, then recurses into the children and walks
    those in the given direction, recursing into each child's children before continuing with siblings. Walking
    backwards will not generate the same sequence as `list(walk())[::-1]` due to this behavior.

    It is safe to modify the nodes (or previous nodes) as they are being walked as long as those modifications don't
    touch the parent or following nodes. This means normal `.replace()` is fine as long as `raw=False`.

    The walk is relatively efficient but if all you need to do is just walk ALL the `AST` children without any bells or
    whistles then `ast.walk()` will be a bit faster.

    **Parameters:**
    - `with_loc`: Return nodes depending on their location information.
        - `False`: All nodes with or without location.
        - `True`: Only nodes which have implicit `AST` locations and also larger computed location nodes like
            `comprehension`, `withitem`, `match_case` and `arguments` (the last one only if there are actually arguments
            present).
        - `'all'`: Same as `True` but also operators with calculated locations (excluding `and` and `or` since they do
            not always have a well defined location).
        - `'own'`: Only nodes with their own implicit `AST` locations, same as `True` but excludes those larger nodes
            with calculated locations.
    - `self_`: If `True` then self will be returned first with the possibility to skip children with `send(False)`,
        otherwise will start directly with children.
    - `recurse`: Whether to recurse into children by default, `send(True)` for a given node will always override this.
    - `scope`: If `True` then will walk only within the scope of `self`. Meaning if called on a `FunctionDef` then
        will only walk children which are within the function scope. Will yield children which have their own scopes,
        and the parts of them which are visible in this scope (like default argument values), but will not recurse into
        them unless `send(True)` is done for that child.
    - `back`: If `True` then walk every node in reverse syntactic order. This is not the same as a full forwards
        walk reversed due to recursion (parents are still returned before children, only in reverse sibling order).

    **Examples:**
    ```py
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
    ```
    """

    if self_:
        if not _with_loc(self, with_loc):
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
            scope   = False

    stack = None
    ast   = self.a

    if scope:  # some parts of a FunctionDef or ClassDef are outside its scope
        if isinstance(ast, list):
            stack = ast[:] if back else ast[::-1]

        elif isinstance(ast, (ClassDef, Module, Interactive)):
            if back:
                stack = []

                if type_params := getattr(ast, 'type_params', None):
                    stack.extend(type_params)

                stack.extend(ast.body)

            else:
                stack = ast.body[::-1]

                if type_params := getattr(ast, 'type_params', None):
                    stack.extend(type_params[::-1])

        elif (is_func := isinstance(ast, (FunctionDef, AsyncFunctionDef))) or isinstance(ast, Lambda):
            if back:
                stack = []

                if type_params := getattr(ast, 'type_params', None):
                    stack.extend(type_params)

                stack.append(ast.args)

                if is_func:
                    stack.extend(ast.body)
                else:
                    stack.append(ast.body)

            else:
                stack = ast.body[::-1] if is_func else [ast.body]

                stack.append(ast.args)

                if type_params := getattr(ast, 'type_params', None):
                    stack.extend(type_params[::-1])

        elif (is_elt := isinstance(ast, (ListComp, SetComp, GeneratorExp))) or isinstance(ast, DictComp):
            if back:
                stack = ([ast.elt] if is_elt else [ast.key, ast.value]) + (generators := ast.generators)
            else:
                stack = (generators := ast.generators)[::-1] + ([ast.elt] if is_elt else [ast.value, ast.key])

            skip_iter = generators[0].iter

        elif isinstance(ast, Expression):
            stack = [ast.body]

    if stack is None:
        stack = syntax_ordered_children(ast)

        if not back:
            stack = stack[::-1]

    while stack:
        if not (ast := stack.pop()):
            continue

        fst = ast.f

        if not _with_loc(fst, with_loc):
            continue

        recurse_ = recurse

        while (sent := (yield fst)) is not None:
            recurse_ = 1 if sent else False

        if not fst.a:  # has been changed by the player
            fst = fst.repath()

        ast = fst.a  # could have just modified the ast

        if recurse_ is not True:
            if recurse_:  # user did send(True), walk this child unconditionally
                yield from fst.walk(with_loc, self_=False, back=back)

        else:
            if scope:
                recurse_ = False

                if isinstance(ast, ClassDef):
                    if back:
                        stack.extend(ast.decorator_list)
                        stack.extend(ast.bases)
                        stack.extend(ast.keywords)

                    else:
                        stack.extend(ast.keywords[::-1])
                        stack.extend(ast.bases[::-1])
                        stack.extend(ast.decorator_list[::-1])

                elif isinstance(ast, (FunctionDef, AsyncFunctionDef)):
                    if back:
                        stack.extend(ast.decorator_list)
                        stack.extend(ast.args.defaults)
                        stack.extend(ast.args.kw_defaults)

                    else:
                        stack.extend(ast.args.kw_defaults[::-1])
                        stack.extend(ast.args.defaults[::-1])
                        stack.extend(ast.decorator_list[::-1])

                elif isinstance(ast, Lambda):
                    if back:
                        stack.extend(ast.args.defaults)
                        stack.extend(ast.args.kw_defaults)
                    else:
                        stack.extend(ast.args.kw_defaults[::-1])
                        stack.extend(ast.args.defaults[::-1])

                elif isinstance(ast, (ListComp, SetComp, DictComp, GeneratorExp)):
                    comp_first_iter = ast.generators[0].iter
                    gen             = fst.walk(with_loc, self_=False, back=back)

                    for f in gen:  # all NamedExpr assignments below are visible here, yeah, its ugly
                        if (a := f.a) is comp_first_iter or (f.pfield.name == 'target' and isinstance(a, Name) and
                                                             isinstance(f.parent.a, NamedExpr)):
                            subrecurse = recurse

                            while (sent := (yield f)) is not None:
                                subrecurse = sent

                            if not subrecurse:
                                gen.send(False)

                elif isinstance(ast, comprehension):  # this only comes from top level comprehension, not ones encountered here
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

                else:
                    recurse_ = True

            if recurse_:
                children = syntax_ordered_children(ast)

                stack.extend(children if back else children[::-1])


# ----------------------------------------------------------------------------------------------------------------------

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
