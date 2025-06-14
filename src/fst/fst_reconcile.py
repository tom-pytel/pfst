"""Reconcile."""

from ast import *
from typing import Optional

from .astutil import *
from .shared import NodeError, astfield


class _Reconcile:
    """The strategy is to make a copy of the original tree (mark) and then mutate it node by node according to the
    changes detected between the working tree and the marked reference tree."""

    work: 'FST'  ; """The `FST` tree that was operated on and will have `AST` replacements."""
    mark: 'FST'  ; """The marked `FST` tree to use as reference."""
    out:  'FST'  ; """The output `FST` tree to build up and return."""

    def __init__(self, work: 'FST', mark: 'FST'):
        self.work = work
        self.mark = mark
        self.out  = mark.copy()

    def recurse_ast(self, node: AST, nodef: Optional['FST'], outa: AST):
        outf = outa.f

        for field, child in iter_fields(node):
            if field in ('ctx', 'str'):  # redundant or possibly contradictory
                continue

            if isinstance(child, AST):  # AST, but out may not have anything at this position
                self.from_ast(child, outf, nodef, astfield(field))

            elif isinstance(child, list):
                for i, c in enumerate(child):
                    self.from_ast(c, outf, nodef, astfield(field, i))

    def recurse_fst(self, node: AST, outa: AST):
        outf  = outa.f
        nodef = node.f

        for field, child in iter_fields(node):
            if field in ('ctx', 'str'):  # redundant or possibly contradictory
                continue

            if isinstance(child, AST):  # AST, but out may not have anything at this position
                self.from_fst(child, outf, nodef, astfield(field))

            elif not isinstance(child, list):  # primitive, or None to delete possibly AST child
                if child != getattr(outa, field):
                    outf.put(child, field=field)

            else:  # slice


                # TODO: initial special stuff to move around blocks of slice if possible


                if len(child) != len(getattr(outa, field)):
                    raise NotImplementedError(f'different length slice field {field!r}')

                for i, c in enumerate(child):
                    self.from_fst(c, outf, nodef, astfield(field, i))


                # TODO: slices PROPERLY!!!




    def from_ast(self, node: AST, out_parent: Optional['FST'] = None, parent: Optional['FST'] = None,
                 pfield: astfield | None = None):
        """Coming from an unknown AST node."""

        work_root     = self.work
        pfname, pfidx = pfield if pfield else (None, None)

        if not (nodef := getattr(node, 'f', None)) or nodef.root is not work_root:  # pure AST if no '.f' or FST from different tree
            if nodef:  # FST from different tree, need to verify it before using
                try:
                    copy = nodef.verify(reparse=False).copy()  # light verification should be enough
                except Exception:
                    pass  # we don't put here because this node was already included in a pure AST put above, we simply failed to add formatting

                else:  # we trust that it is valid by here, if not then its the user's fault
                    out_parent.put(copy, pfidx, False, pfname)

                    return  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements

            # pure AST

            self.recurse_ast(node, nodef, pfield.get(out_parent.a))

            return

        # FST node from original tree

        copy       = self.mark.child_from_path(work_root.child_path(nodef)).copy()
        out_parent = out_parent.put(copy, pfidx, False, pfname)  # copy from known good copy of tree
        outa       = pfield.get(out_parent.a)

        try:
            self.recurse_fst(node, outa)
        except (NodeError, SyntaxError, ValueError, NotImplementedError):  # something failed below, so replace whole AST
            out_parent.put(node, pfidx, False, pfname)  # copy from known good copy of tree

    def from_fst(self, node: AST, out_parent: Optional['FST'] = None, parent: Optional['FST'] = None,
                 pfield: astfield | None = None):
        """Coming from a known FST node."""

        def replace(code):
            nonlocal out_parent

            if out_parent:
                out_parent = out_parent.put(code, pfidx, False, pfname)
            else:  # because can replace AST at root node which has out_parent=None
                self.out.replace(code)

        work_root     = self.work
        pfname, pfidx = pfield if pfield else (None, None)

        if not (nodef := getattr(node, 'f', None)) or nodef.root is not work_root:  # pure AST if no '.f' or FST from different tree
            if nodef:  # FST from different tree, need to verify it before using
                try:
                    copy = nodef.verify(reparse=False).copy()  # light verification should be enough
                except Exception:
                    pass  # verification failed, fall through to pure AST

                else:  # we trust that it is valid by here, if not then its the user's fault
                    replace(copy)

                    return  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements

            # pure AST

            replace(node)

            self.recurse_ast(node, nodef, pfield.get(out_parent.a) if out_parent else self.out.a)

            return

        # FST node from original tree

        if nodef.parent is not parent or nodef.pfield != pfield:  # FST from off path, different parent and / or pfield, was moved around in the tree
            replace(self.mark.child_from_path(work_root.child_path(nodef)).copy())  # copy from known good copy of tree

        outa = pfield.get(out_parent.a) if out_parent else self.out.a

        try:
            self.recurse_fst(node, outa)
        except (NodeError, SyntaxError, ValueError, NotImplementedError):  # something failed below, so replace whole AST
            replace(node)



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
