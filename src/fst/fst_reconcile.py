"""Reconcile."""

from ast import *
from typing import Literal, Optional, Union

from .astutil import *
from .shared import NodeError, astfield


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

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

    def put_node(self, code: Union['FST', AST], out_parent: Optional['FST'] = None, pfield: astfield | None = None):
        if out_parent:
            out_parent.put(code, pfield.idx, False, pfield.name, raw=False)
        else:  # because can replace AST at root node which has out_parent=None
            self.out.replace(code, raw=False)

    def recurse_slice_fst(self, node: AST, outf: Optional['FST'], field: str, body: list[AST]):
        nodef     = node.f
        outa      = outf.a
        outa_body = getattr(outa, field)
        work_root = self.work
        len_body  = len(body)
        start     = 0
        node_sig  = (node.__class__, field)

        while start < len_body:
            if (not (childf := getattr(body[start], 'f', None)) or                                   # if child doesn't have FST
                not (child_parent := childf.parent) or                                               # or no parent
                (child_idx := (child_pfield := childf.pfield).idx) is None or                        # or no index (not part of a sliceable list)
                (
                    child_idx == start                                                               # or child is at the correct location
                    if (child_field := child_pfield.name) == field and child_parent is nodef else    # if is from same field and our own child, else
                    not FST._is_slice_compatible(node_sig, (child_parent.a.__class__, child_field))  # or child slice is not compatible
                )
            ):                                                                                       # then can't possibly slice, or it doesn't make sense to
                end = start + 1

            else:  # slice operation, even if its just one element because slice copies more formatting and comments
                child_off_idx = child_idx - start

                for end in range(start + 1, len_body):  # get length of contiguous slice
                    if (not (f := getattr(body[end], 'f', None)) or f.parent is not child_parent or  # if is not following element then done
                        f.pfield != (child_field, child_off_idx + end)
                    ):
                        break
                else:
                    end = len_body

                if childf.root is not work_root:  # from different tree, need to verify first
                    try:
                        for i in range(start, end):
                            body[i].f.verify(reparse=False)

                        slice = child_parent.get_slice(child_idx, child_idx + end - start, field)

                    except Exception:  # verification failed, need to do one AST at a time
                        pass

                    else:  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements, couldn't anyway as we don't know anything about that tree
                        outf.put_slice(slice, start, end, field)

                        start = end

                        continue

                else:
                    mark_parent = self.mark.child_from_path(self.work.child_path(child_parent))
                    slice       = mark_parent.get_slice(child_idx, child_idx + end - start, field)

                    outf.put_slice(slice, start, end, field)

            len_outa_body = len(outa_body)  # get each time because could have been modified by put_slice

            for i in range(start, end):
                n = body[i]  # this is safe to use in 'put_slice()' then 'recurse()' without duplicating because ASTs are not consumed

                if i >= len_outa_body:  # if past end then we need to slice insert AST before recursing into it
                    outf.put_slice(n, i, i, field, one=True)  # put one

                self.recurse(n, astfield(field, i), outf, nodef)

            start = end

        if start < len(outa_body):  # delete tail in output
            outf.put(None, start, None, field)





    def recurse_slice_ast(self, node: AST, outf: Optional['FST'], field: str, body: list[AST]):
        # outa      = outf.a
        # outa_body = getattr(outa, field)
        work_root = self.work
        len_body  = len(body)
        start     = 0
        node_sig  = (node.__class__, field)

        while start < len_body:
            if (not (childf := getattr(body[start], 'f', None)) or                                                        # or child doesn't have FST
                not (child_parent := childf.parent) or                                                                    # or no parent
                (child_idx := (child_pfield := childf.pfield).idx) is None or                                             # or no index (not part of a sliceable list)
                (
                    not FST._is_slice_compatible(node_sig, (child_parent.a.__class__, child_field := child_pfield.name))  # child slice is not compatible
                )
            ):                                                                                                            # then can't possibly slice, or it doesn't make sense to
                end = start + 1

            else:  # slice operation, even if its just one element because slice copies more formatting and comments
                child_off_idx = child_idx - start

                for end in range(start + 1, len_body):  # get length of contiguous slice
                    if (not (f := getattr(body[end], 'f', None)) or f.parent is not child_parent or  # if is not following element then done
                        f.pfield != (child_field, child_off_idx + end)
                    ):
                        break
                else:
                    end = len_body

                if childf.root is not work_root:  # from different tree, need to verify first
                    try:
                        for i in range(start, end):
                            body[i].f.verify(reparse=False)

                        slice = child_parent.get_slice(child_idx, child_idx + end - start, field)

                    except Exception:  # verification failed, need to do one AST at a time
                        pass

                    else:  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements, couldn't anyway as we don't know anything about that tree
                        outf.put_slice(slice, start, end, field)

                        start = end

                        continue

                else:
                    mark_parent = self.mark.child_from_path(self.work.child_path(child_parent))
                    slice       = mark_parent.get_slice(child_idx, child_idx + end - start, field)

                    outf.put_slice(slice, start, end, field)

            for i in range(start, end):  # don't need to slice insert here because we know size will be same between work and out
                self.recurse(body[i], astfield(field, i), outf, False)

            start = end




    def recurse(self, node: AST, pfield: astfield | None = None,
                out_parent: Optional['FST'] = None, node_parent: Optional['FST'] | Literal[False] = None):
        """Recurse from either an in-tree known `FST` node or from a pure `AST` put above. The two situations are
        slightly different in the following ways:

        - From in-tree `FST` means the source and nodes that is in the out tree is the same as the original parent in-tree
        `FST` and when encountering other in-tree `FST` nodes which have the same child path as the original tree with
        respect to the parent then nothing needs to be changed. Otherwise, if `FST` from same tree but at different
        location, it is copied from the marked tree and gauranteed to have original source and nodes for the branch. If
        `FST` from another tree then it is validated and if good attempted to copy with all its source and children, and
        then not recursed (since it is assumed to be unmodified if it validated). If fails validate or copy then its
        `AST` is put just like a pure `AST` would be discarding any formatting. For a new pure `AST` child, it is just
        put at the location and recursion is cuntinued with `node_parent=False` to indicate an `AST` recursion.

        - From pure `AST`, the same thing is done for an out-of-tree `FST` node as for the `FST` recursion. For a pure
        `AST`, nothing is changed as it was put with the original parent pure `AST` that recursed to here. Otherwise,
        on an in-tree `FST` node, it is copied and put with formatting from the marked tree and recursion continues
        with `node_parent` set to this node to indicate the in-tree `FST` recursion path.

        **Parameters:**
        - `node_parent`: Has the following meanings:
            - `FST`: Coming from this in-tree `FST` parent.
            - `None`: Is tree `FST` root (no parent).
            - `False`: Coming from out-of-tree `AST` parent.
        """

        if not (nodef := getattr(node, 'f', None)) or nodef.root is not self.work:  # pure AST if no '.f' or FST from different tree
            if nodef:  # FST from different tree, need to verify it before using
                try:
                    copy = nodef.verify(reparse=False).copy()

                except Exception:  # verification failed, fall through to pure AST
                    pass

                else:  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements, couldn't anyway as we don't know anything about that tree
                    self.put_node(copy, out_parent, pfield)

                    return

            # pure AST node, recurse

            if node_parent is not False:  # if coming from in-tree FST then need to put node here since it doesn't match what the in-tree node was, this will replace for all pure AST nodes
                self.put_node(node, out_parent, pfield)

            outa = pfield.get(out_parent.a) if out_parent else self.out.a
            outf = outa.f

            for field, child in iter_fields(node):
                if field in ('ctx', 'str'):  # redundant or possibly contradictory
                    continue

                if isinstance(child, AST):  # AST, but out may not have anything at this position
                    self.recurse(child, astfield(field), outf, False)

                elif isinstance(child, list):
                    if field in ('body', 'orelse', 'handlers', 'finalbody', 'cases', 'elts'):
                        self.recurse_slice_ast(node, outf, field, child)

                        continue



                    # TODO: Dict special case slices
                    # TODO: rest of slices when they are done


                    # slice fallback, one by one, sizes guaranteed same

                    for i, c in enumerate(child):  # they are guaranteed to all be in the out tree since the AST was put either directly above here (in source) or in some pure AST parent above (in tree)
                        self.recurse(c, astfield(field, i), outf, False)
            return

        # FST node from original tree, recurse

        if node_parent is False or (nodef.parent is not node_parent or nodef.pfield != pfield):  # coming from pure AST or in-tree FST from off path
            copy = self.mark.child_from_path(self.work.child_path(nodef)).copy()

            self.put_node(copy, out_parent, pfield)  # copy from known good copy of tree

        outa = pfield.get(out_parent.a) if out_parent else self.out.a
        outf = outa.f

        try:
            for field, child in iter_fields(node):
                if field in ('ctx', 'str'):  # redundant or possibly contradictory
                    continue

                if isinstance(child, AST):  # AST, but out may not have anything at this position
                    self.recurse(child, astfield(field), outf, nodef)

                elif not isinstance(child, list):  # primitive, or None to delete possibly AST child
                    if child != getattr(outa, field):
                        outf.put(child, field=field, raw=False)

                else:  # slice
                    if field in ('body', 'orelse', 'handlers', 'finalbody', 'cases', 'elts'):
                        self.recurse_slice_fst(node, outf, field, child)

                        continue


                    # TODO: Dict special case slices
                    # TODO: rest of slices when they are done


                    # slice fallback, one by one but only if sizes are same

                    if len(child) != len(getattr(outa, field)):
                        raise NotImplementedError(f'different length slice fields {field!r}')

                    for i, c in enumerate(child):
                        self.recurse(c, astfield(field, i), outf, nodef)

        except (NodeError, SyntaxError, ValueError, NotImplementedError):  # something failed below, so replace whole AST
            self.put_node(node, out_parent, pfield)


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

    rec.recurse(self.a)

    return rec.out


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]  # used by make_docs.py

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
