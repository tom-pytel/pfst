"""Reconcile."""

from ast import *
from typing import Any, Callable

from .astutil import *


def _reconcile(self_root: 'FST', selfa: AST, markf: 'FST') -> list[Callable]:
    """Reconcile pair of nodes.

    Path from root to `selfa` must match path from root to `markf`.

    **Returns:**
    - `fixes`: List of `Callable`s to apply changes if not equal, empty list to indicate trees match.
    """

    if not (self := getattr(selfa, 'f', None)):  # if no '.f' then definitely doesn't match

        # TODO: maybe there are valid FSTs below which can be copied with source

        if not markf.is_root:
            return [lambda: markf.replace(selfa)]




    self  = self.f
    marka = mark.a

    if selfa.__class__ is not marka.__class__:
        pass

    pass


# ----------------------------------------------------------------------------------------------------------------------

def mark(self: 'FST') -> 'FST':
    """Return something marking the current state of this `FST` tree. Used to `reconcile()` later for non-FST  operation
    changes made (changing `AST` nodes directly).

    **Returns:**
    - `FST`: A marked copy of `self` with any necessary information added for a future `reconcile()`. You can `mark()`
        this marked `FST` to get a usable copy."""

    if not self.is_root:
        raise ValueError('can only mark root nodes')

    return self.copy()


def reconcile(self: 'FST', mark: 'FST') -> 'FST':
    """Reconcile `self` with a previously marked version and return a new valid `FST` tree. This is meant for allowing
    non-FST modifications to an `FST` tree and later converting it to a valid `FST` tree to preserve as much formatting
    as possible and maybe continue operating in `FST` land.

    **Parameters:**
    - `mark`: A previously marked snapshot of `self`. This object should be considered consumed on success or failure
        and not used again. If you want to have multiple of the same marked snapshot for multiple attempts, either
        `mark()` multiple times or `mark()` the marked snapshot which will give a copy with the correct information.

    **Returns:**
    - `FST`: A new valid reconciled `FST` if possible.
    """

    if not self.is_root:
        raise ValueError('can only reconcile root nodes')

    _reconcile(self, self.a, mark)

    return self


# ----------------------------------------------------------------------------------------------------------------------

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
