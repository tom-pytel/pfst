"""Reconcile."""

from ast import *
from typing import Optional

from .astutil import *
from .shared import NodeError, astfield


class _Reconcile:
    def __init__(self, work: 'FST', mark: 'FST'):
        self.work = work
        self.mark = mark
        self.out  = mark.copy()

    def from_original_fst(self, node: AST, marka: AST, outf: 'FST', parent: Optional['FST'] = None,
                          pfield: astfield | None = None, path: list[astfield] = []):
        work_root     = self.work
        mark_root     = self.mark
        pfname, pfidx = pfield if pfield else (None, None)

        if not (nodef := getattr(node, 'f', None)):  # if no '.f' then definitely doesn't match
            assert not isinstance(node, FunctionType)  # juuust in case

            if pfname == 'ctx':
                assert isinstance(node, expr_context)
                assert parent  # because really, an expr_context at the top level???

                setattr(parent.a, 'ctx', FST(node.__class__(), parent, pfield).a)

            else:
                outf.replace(node)


            # TODO: recurse and maybe find things we have source for


            return

        if nodef.parent is not parent or nodef.pfield != pfield:  # different parent of pfield, was moved around in the tree or is FST from somewhere else
            if nodef.root is not work_root:  # from different tree?
                outf.replace(nodef.copy())  # we trust that it is part of a valid tree, if not its the user's fault

                return  # we don't recurse because it came from unknown tree so if it had AST nodes replaced then we are in undefined territory (if even got here without exception)

            outf.replace(mark_root.child_from_path(work_root.child_path(nodef)).copy())


            # TODO: recurse


            raise NotImplementedError

        # part of original tree, we assume it matches mark

        outa = outf.a

        try:
            for field, child in iter_fields(node):
                if isinstance(child, AST):
                    child_pfield = astfield(field)

                    self.from_original_fst(child, child_pfield.get(marka), child_pfield.get(outa).f,
                                           nodef, child_pfield, path + [child_pfield])

                elif not isinstance(child, list):  # primitive
                    if field != 'str' and child != getattr(marka, field):
                        outf.put(child, field)

                else:  # slice
                    for i, c in enumerate(child):
                        c_pfield = astfield(field, i)

                        self.from_original_fst(c, c_pfield.get(marka), c_pfield.get(outa).f,
                                               nodef, c_pfield, path + [c_pfield])



                    # TODO: slices


                    # raise NotImplementedError

        except (NodeError, SyntaxError, NotImplementedError):
            outf.replace(node)  # something failed below, so try replace whole ast


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
    - `mark`: A previously marked snapshot of `self`. This object is not consumed on use, success or failure.

    **Returns:**
    - `FST`: A new valid reconciled `FST` if possible.
    """

    if not self.is_root:
        raise ValueError('can only reconcile root nodes')

    rec = _Reconcile(self, mark)

    with self.option(raw=False):
        rec.from_original_fst(self.a, mark.a, rec.out)

    return rec.out


# ----------------------------------------------------------------------------------------------------------------------

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
