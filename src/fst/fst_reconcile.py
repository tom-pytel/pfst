"""Reconcile."""

from ast import *
from typing import Optional

from .astutil import *
from .shared import NodeError, astfield


class _Reconcile:
    """The strategy is to make a copy of the original tree and then mutate it node by node according to the changes
    made."""

    work: 'FST'  ; """The `FST` tree that was operated on and will have `AST` replacements."""
    mark: 'FST'  ; """The marked `FST` tree to use as reference."""
    out:  'FST'  ; """The output `FST` tree to build up and return."""

    def __init__(self, work: 'FST', mark: 'FST'):
        self.work = work
        self.mark = mark
        self.out  = mark.copy()

    def from_fst(self, node: AST, out_parent: Optional['FST'] = None, parent: Optional['FST'] = None,
                 pfield: astfield | None = None):
        work_root     = self.work
        mark_root     = self.mark
        pfname, pfidx = pfield if pfield else (None, None)

        if not (nodef := getattr(node, 'f', None)) or nodef.root is not work_root:  # pure AST if no '.f' or FST from different tree
            if nodef:  # FST from different tree, need to verify it before using
                try:
                    nodef.verify(reparse=False)  # light verification should be enough

                    copy = nodef.copy()  # another chance for error if invalid

                except Exception:
                    pass  # verification failed, fall through to pure AST

                else:  # we trust that it is valid by here, if not then its the user's fault
                    if out_parent:
                        out_parent.put(copy, pfidx, False, pfname)
                    else:  # because can replace AST at root node which has parent=None
                        self.out.replace(copy)  # replace root FST doens't change the FST, just its contents

                    return  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements

            # pure AST

            if pfname == 'ctx':
                assert isinstance(node, expr_context)

                setattr(parent.a, 'ctx', FST(node.__class__(), parent, pfield).a)  # __class__() because could be shared instance from ast.parse()

            else:
                if out_parent:
                    out_parent = out_parent.put(node, pfidx, False, pfname)
                else:
                    self.out.replace(node)


            # TODO: recurse and maybe find things we have source for


            return

        # FST node from original tree

        markf = mark_root.child_from_path(work_root.child_path(nodef))
        marka = markf.a

        if nodef.parent is not parent or nodef.pfield != pfield:  # FST from off path, different parent or pfield, was moved around in the tree
            copy = markf.copy()  # copy from known good copy of tree

            if out_parent:
                out_parent = out_parent.put(copy, pfidx, False, pfname)
            else:
                self.out.replace(copy)

        outa = pfield.get(out_parent.a) if out_parent else self.out.a
        outf = outa.f

        try:
            for field, child in iter_fields(node):
                if field in ('ctx', 'str'):  # redundant or contradictory
                    continue

                if isinstance(child, AST):
                    child_pfield = astfield(field)

                    self.from_fst(child, outf, nodef, child_pfield)

                elif not isinstance(child, list):  # primitive, or None to delete possibly AST child
                    if child != getattr(marka, field):
                        outf.put(child, field=field)

                else:  # slice
                    for i, c in enumerate(child):
                        c_pfield = astfield(field, i)

                        self.from_fst(c, outf, nodef, c_pfield)



                    # TODO: slices PROPERLY!!!


                    # raise NotImplementedError

        except (NodeError, SyntaxError, ValueError, NotImplementedError):  # something failed below, so try replace whole ast
            if outf:
                outf.replace(node)
            else:
                parent.put(node, pfidx, field=pfname)


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
        rec.from_fst(self.a)

    return rec.out


# ----------------------------------------------------------------------------------------------------------------------

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
