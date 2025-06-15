"""Reconcile."""

from ast import *
from typing import Literal, Optional, Union

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

    def replace(self, code: Union['FST', AST], out_parent: Optional['FST'] = None, pfield: astfield | None = None):
        if out_parent:
            out_parent.put(code, pfield.idx, False, pfield.name)
        else:  # because can replace AST at root node which has out_parent=None
            self.out.replace(code)

    def recurse_ast(self, node: AST, nodef: Optional['FST'], outa: AST):
        outf = outa.f

        for field, child in iter_fields(node):
            if field in ('ctx', 'str'):  # redundant or possibly contradictory
                continue

            if isinstance(child, AST):  # AST, but out may not have anything at this position
                self.recurse(child, astfield(field), outf, nodef)

            elif isinstance(child, list):
                for i, c in enumerate(child):
                    self.recurse(c, astfield(field, i), outf, nodef)

    def recurse_fst(self, node: AST, outa: AST, out_parent: Optional['FST'] = None, pfield: astfield | None = None):
        try:
            outf  = outa.f
            nodef = node.f

            for field, child in iter_fields(node):
                if field in ('ctx', 'str'):  # redundant or possibly contradictory
                    continue

                if isinstance(child, AST):  # AST, but out may not have anything at this position
                    self.recurse(child, astfield(field), outf, nodef)

                elif not isinstance(child, list):  # primitive, or None to delete possibly AST child
                    if child != getattr(outa, field):
                        outf.put(child, field=field)

                else:  # slice


                    # TODO: initial special stuff to move around blocks of slice if possible


                    if len(child) != len(getattr(outa, field)):
                        raise NotImplementedError(f'different length slice field {field!r}')

                    for i, c in enumerate(child):
                        self.recurse(c, astfield(field, i), outf, nodef)


                    # TODO: slices PROPERLY!!!



        except (NodeError, SyntaxError, ValueError, NotImplementedError):  # something failed below, so replace whole AST
            self.replace(node, out_parent, pfield)



    # def from_ast(self, node: AST, out_parent: Optional['FST'] = None, parent: Optional['FST'] = None,  # <-- USE `parent``, (change to `node_parent`) as signal if is from_fst or from_ast
    #              pfield: astfield | None = None):
    #     """Coming from an unknown AST node."""

    #     if not (nodef := getattr(node, 'f', None)) or nodef.root is not self.work:  # pure AST if no '.f' or FST from different tree
    #         if nodef:  # FST from different tree, need to verify it before using
    #             try:
    #                 copy = nodef.verify(reparse=False).copy()

    #             except Exception:
    #                 pass  # we don't put here because this node was already included in a pure AST put above, we simply failed to add formatting

    #             else:  # we trust that it is valid by here, if not then its the user's fault
    #                 self.replace(copy, out_parent, pfield)

    #                 return  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements

    #         # pure AST node

    #         self.recurse_ast(node, nodef, pfield.get(out_parent.a))

    #         return

    #     # FST node from original tree

    #     copy = self.mark.child_from_path(self.work.child_path(nodef)).copy()

    #     self.replace(copy, out_parent, pfield)  # copy from known good copy of tree

    #     outa = pfield.get(out_parent.a)

    #     self.recurse_fst(node, outa, out_parent, pfield)

    # def from_fst(self, node: AST, out_parent: Optional['FST'] = None, parent: Optional['FST'] = None,
    #              pfield: astfield | None = None):
    #     """Coming from a known FST node."""

    #     if not (nodef := getattr(node, 'f', None)) or nodef.root is not self.work:  # pure AST if no '.f' or FST from different tree
    #         if nodef:  # FST from different tree, need to verify it before using
    #             try:
    #                 copy = nodef.verify(reparse=False).copy()

    #             except Exception:
    #                 pass  # verification failed, fall through to pure AST

    #             else:  # we trust that it is valid by here, if not then its the user's fault
    #                 self.replace(copy, out_parent, pfield)

    #                 return  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements

    #         # pure AST node

    #         self.replace(node, out_parent, pfield)
    #         self.recurse_ast(node, nodef, pfield.get(out_parent.a) if out_parent else self.out.a)

    #         return

    #     # FST node from original tree

    #     if nodef.parent is not parent or nodef.pfield != pfield:  # FST from off path, different parent and / or pfield, was moved around in the tree
    #         copy = self.mark.child_from_path(self.work.child_path(nodef)).copy()
    #         self.replace(copy, out_parent, pfield)  # copy from known good copy of tree

    #     outa = pfield.get(out_parent.a) if out_parent else self.out.a

    #     self.recurse_fst(node, outa, out_parent, pfield)



    def recurse(self, node: AST, pfield: astfield | None = None,
                out_parent: Optional['FST'] = None, node_parent: Optional['FST'] | Literal[False] = None):
        """Coming from a known FST node. `node_parent=False` means recursing from written `AST` while if it is not
        `False` then the recursion is coming from an in-tree `FST`."""

        if not (nodef := getattr(node, 'f', None)) or nodef.root is not self.work:  # pure AST if no '.f' or FST from different tree
            if nodef:  # FST from different tree, need to verify it before using
                try:
                    copy = nodef.verify(reparse=False).copy()

                except Exception:
                    # if recursing from pure AST, we don't replace here because this node was already included in a pure AST replace above, we simply failed to add formatting
                    # if recursing from in-tree FST then node AST will be put after because `node_parent != False`, so we don't put here
                    pass  # verification failed, fall through to pure AST

                else:
                    self.replace(copy, out_parent, pfield)

                    return  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements

            # pure AST node

            if node_parent is not False:
                self.replace(node, out_parent, pfield)

            self.recurse_ast(node, nodef, pfield.get(out_parent.a) if out_parent else self.out.a)

            return

        # FST node from original tree

        if node_parent is False or (nodef.parent is not node_parent or nodef.pfield != pfield):  # FST from off path, different parent and / or pfield, was moved around in the tree
            copy = self.mark.child_from_path(self.work.child_path(nodef)).copy()

            self.replace(copy, out_parent, pfield)  # copy from known good copy of tree

        outa = pfield.get(out_parent.a) if out_parent else self.out.a

        self.recurse_fst(node, outa, out_parent, pfield)


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
        rec.recurse(self.a)

    return rec.out


# ----------------------------------------------------------------------------------------------------------------------

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
