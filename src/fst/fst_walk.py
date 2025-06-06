"""Next and previous children in syntactic order and walk."""

from ast import *
from typing import Generator, Literal, Optional

from .astutil import *

from .shared import astfield

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


def _with_loc(fst: 'FST', with_loc: bool | Literal['all', 'own'] = True) -> bool:
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

def next(self: 'FST', with_loc: bool | Literal['all', 'own'] = True) -> Optional['FST']:  # TODO: refactor
    """Get next sibling in syntactic order, only within parent.

    **Parameters:**
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).

    **Returns:**
    - `None` if last valid sibling in parent, otherwise next node.
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


def prev(self: 'FST', with_loc: bool | Literal['all', 'own'] = True) -> Optional['FST']:  # TODO: refactor
    """Get previous sibling in syntactic order, only within parent.

    **Parameters:**
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).

    **Returns:**
    - `None` if first valid sibling in parent, otherwise previous node.
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


def first_child(self: 'FST', with_loc: bool | Literal['all', 'own'] = True) -> Optional['FST']:
    """Get first valid child in syntactic order.

    **Parameters:**
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).

    **Returns:**
    - `None` if no valid children, otherwise first valid child.
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


def last_child(self: 'FST', with_loc: bool | Literal['all', 'own'] = True) -> Optional['FST']:
    """Get last valid child in syntactic order.

    **Parameters:**
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).

    **Returns:**
    - `None` if no valid children, otherwise last valid child.
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


def next_child(self: 'FST', from_child: Optional['FST'], with_loc: bool | Literal['all', 'own'] = True
               ) -> Optional['FST']:
    """Get next child in syntactic order. Meant for simple iteration. This is a slower way to iterate, `walk()` is
    faster.

    **Parameters:**
    - `from_child`: Child node we are coming from which may or may not have location.
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).

    **Returns:**
    - `None` if last valid child in `self`, otherwise next child node.
    """

    return self.first_child(with_loc) if from_child is None else from_child.next(with_loc)


def prev_child(self: 'FST', from_child: Optional['FST'], with_loc: bool | Literal['all', 'own'] = True
               ) -> Optional['FST']:
    """Get previous child in syntactic order. Meant for simple iteration. This is a slower way to iterate, `walk()`
    is faster.

    **Parameters:**
    - `from_child`: Child node we are coming from which may or may not have location.
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).

    **Returns:**
    - `None` if first valid child in `self`, otherwise previous child node.
    """

    return self.last_child(with_loc) if from_child is None else from_child.prev(with_loc)


def next_step(self: 'FST', with_loc: bool | Literal['all', 'own', 'allown'] = True, *,
              recurse_self: bool = True) -> Optional['FST']:
    """Get next node in syntactic order over entire tree. Will walk up parents and down children to get the next
    node, returning `None` only when we are at the end of the whole thing.

    **Parameters:**
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).
        - `'allown'` Same as `'own'` but recurse into nodes with non-own locations.
    - `recurse_self`: Whether to allow recursion into `self` to return children or move directly to next nodes.

    **Returns:**
    - `None` if last valid node in tree, otherwise next node in order.
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


def prev_step(self: 'FST', with_loc: bool | Literal['all', 'own', 'allown'] = True, *,
              recurse_self: bool = True) -> Optional['FST']:
    """Get prev node in syntactic order over entire tree. Will walk up parents and down children to get the next
    node, returning `None` only when we are at the beginning of the whole thing.

    **Parameters:**
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).
        - `'allown'` Same as `'own'` but recurse into nodes with non-own locations.
    - `recurse_self`: Whether to allow recursion into `self` to return children or move directly to prev nodes.

    **Returns:**
    - `None` if first valid node in tree, otherwise prev node in order.
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


def walk(self: 'FST', with_loc: bool | Literal['all', 'own'] = False, *, self_: bool = True,
         recurse: bool = True, scope: bool = False, back: bool = False) -> Generator['FST', bool, None]:
    """Walk self and descendants in syntactic order, `send(False)` to skip recursion into child. `send(True)` to
    allow recursion into child if called with `recurse=False` or `scope=True` would otherwise disallow it. Can send
    multiple times, last value sent takes effect.

    The walk is defined forwards or backwards in that it returns a parent then recurses into the children and walks
    those in the given direction, recursing into each child's children before continuing with siblings. Walking
    backwards will not generate the same sequence as `list(walk())[::-1]` due to this behavior.

    The walk is relatively efficient but if all you need to do is just walk ALL the `AST` children without any bells or
    whistles then `ast.walk()` will be a bit faster.

    It is safe to modify the nodes (or previous nodes) as they are being walked as long as those modifications don't
    touch the parent or following nodes. This means normal `.replace()` is fine as long as `raw=False`.

    **Parameters:**
    - `with_loc`: Return nodes depending on if they have a location or not.
        - `False`: All nodes with or without location.
        - `True`: Only nodes with `AST` locations returned but also larger computed location nodes like `comprehension`,
            `withitem`, `match_case` and `arguments` (but only if there actually are arguments present).
        - `'all'`: Same as `True` but also operators (excluding `and` and `or`) with calculated locations.
        - `'own'`: Only nodes with own location (does not recurse into non-own nodes).
    - `self_`: If `True` then self will be returned first with the possibility to skip children with `send()`.
    - `recurse`: Whether to recurse into children by default, `send()` for a given node will always override this.
        Will always attempt first level of children unless walking self and `False` is sent first.
    - `scope`: If `True` then will walk only within the scope of `self`. Meaning if called on a `FunctionDef` then
        will only walk children which are within the function scope. Will yield children which have with their own
        scopes, and the parts of them which are visible in this scope (like default argument values), but will not
        recurse into them unless `send(True)` is done for that child.
    - `back`: If `True` then walk every node in reverse syntactic order. This is not the same as a full forwards
        walk reversed due to recursion (parents are still returned before children, only in reverse sibling order).

    **Examples:**
    ```py
    for node in (walking := target.walk()):
        ...
        if i_dont_like_the_node:
            walking.send(False)  # skip walking this node's children, don't use return value from send() here
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
