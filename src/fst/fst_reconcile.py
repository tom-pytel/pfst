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
            out_parent.put(code, pfield.idx, False, pfield.name, raw=False)
        else:  # because can replace AST at root node which has out_parent=None
            self.out.replace(code, raw=False)

    def recurse_slice_fst(self, node: AST, outf: Optional['FST'], field: str, body: list[AST]):
        nodef      = node.f
        outa       = outf.a
        outa_body  = getattr(outa, field)
        work_root  = self.work
        len_body   = len(body)
        len_body_1 = len_body - 1
        start      = 0
        node_sig   = (node.__class__, field)

        while start < len_body:
            if (start == len_body_1 or                                                                               # if we are at the end of the slice range
                not (childf := getattr(body[start], 'f', None)) or                                                   # or child doesn't have FST
                not (child_parent := childf.parent) or                                                               # or no parent
                (child_idx := (child_pfield := childf.pfield).idx) is None or                                        # or no index (not part of a sliceable list)
                child_idx >= len(getattr(child_parenta := child_parent.a, child_field := child_pfield.name)) - 1 or  # or is at end of sliceable list
                (
                    child_idx == start                                                                               # or child is at the correct location
                    if child_parent is nodef and child_field == field else                                           # if is our own child in same field, else
                    not FST._is_slice_compatible(node_sig, (child_parenta.__class__, child_field))                   # child slice is not compatible
                )
            ):                                                                                                       # then can't possibly slice, or it doesn't make sense to
                end = start + 1

            else:
                for end in range(start + 1, len_body):
                    if (not (f := getattr(body[end], 'f', None)) or f.parent is not child_parent or  # if is not following element then done
                        f.pfield != (child_field, child_idx + end)
                    ):
                        break

                if (len_slice := end - start) > 1:  # slice of length 1 doesn't make sense to do as a slice
                    if childf.root is not work_root:  # from different tree, need to verify first
                        try:
                            for i in range(start, end):
                                body[i].f.verify(reparse=False)

                            slice = child_parent.get_slice(child_idx, child_idx + len_slice, field)

                        except Exception:  # verification failed, need to do one AST at a time
                            pass

                        else:  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements, couldn't anyway as we don't have a mark for that tree
                            outf.put_slice(slice, start, end, field)

                            start = end

                            continue

                    else:
                        slice = child_parent.get_slice(child_idx, child_idx + len_slice, field)

                        outf.put_slice(slice, start, end, field)

            len_outa_body = len(outa_body)  # get each time because could have been modified by put_slice

            for i in range(start, end):
                n = body[i]  # this is safe to use in 'put_slice()' then 'recurse()' without duplicating

                if i >= len_outa_body:  # if past end then we need to slice insert AST before recursing into it
                    outf.put_slice(n, i, i, field, one=True)  # put one

                self.recurse(n, astfield(field, i), outf, nodef)

            start = end

        if start < len(outa_body):  # delete tail in output
            outf.put(None, start, None, field)

    def recurse(self, node: AST, pfield: astfield | None = None,
                out_parent: Optional['FST'] = None, node_parent: Optional['FST'] | Literal[False] = None):
        """Recurse from either an in-tree known FST node or from a pure AST put above. `node_parent=False` means
        recursing from `AST`, while if it is not `False` then the recursion is coming from an in-tree `FST`."""

        if not (nodef := getattr(node, 'f', None)) or nodef.root is not self.work:  # pure AST if no '.f' or FST from different tree
            if nodef:  # FST from different tree, need to verify it before using
                try:
                    copy = nodef.verify(reparse=False).copy()

                except Exception:  # verification failed, fall through to pure AST
                    pass

                else:  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements, couldn't anyway as we don't have a mark for that tree
                    self.replace(copy, out_parent, pfield)

                    return

            # pure AST node, recurse

            if node_parent is not False:  # if coming from in-tree FST then need to put node here since it doesn't match what the in-tree node was
                self.replace(node, out_parent, pfield)

            outa = pfield.get(out_parent.a) if out_parent else self.out.a
            outf = outa.f

            for field, child in iter_fields(node):
                if field in ('ctx', 'str'):  # redundant or possibly contradictory
                    continue

                if isinstance(child, AST):  # AST, but out may not have anything at this position
                    self.recurse(child, astfield(field), outf, False)

                elif isinstance(child, list):
                    for i, c in enumerate(child):  # they are guaranteed to all be in out since AST was put directly above here
                        self.recurse(c, astfield(field, i), outf, False)


                    # TODO: handle slices even though they are all in out because may have extra formatting data

                    # if len(child) != len(getattr(outa, field)):
                    #     raise NotImplementedError(f'different length slice fields {field!r}')

                    # for i, c in enumerate(child):
                    #     self.recurse(c, astfield(field, i), outf, False)


            return

        # FST node from original tree, recurse

        if node_parent is False or (nodef.parent is not node_parent or nodef.pfield != pfield):  # in-tree FST from off path or coming from pure AST put
            copy = self.mark.child_from_path(self.work.child_path(nodef)).copy()

            self.replace(copy, out_parent, pfield)  # copy from known good copy of tree

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
            self.replace(node, out_parent, pfield)


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

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
