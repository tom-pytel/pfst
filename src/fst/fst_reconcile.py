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

    def recurse_slice_dict(self, node: AST, outf: Optional['FST']):
        """Recurse into a combined slice of a Dict's keys and values using slice operations to copy over formatting
        where possible (if not already there). Can be recursing an in-tree FST parent or a pure AST parent."""

        keys     = node.keys
        values   = node.values
        len_body = len(keys)

        if len(values) != len_body:
            raise RuntimeError(f'Dict.keys length ({len_body}) != Dict.values length ({len(values)})')

        nodef     = getattr(node, 'f', False)  # this determines if it came from an in-tree FST or a pure AST
        outa      = outf.a
        outa_keys = getattr(outa, 'keys')
        work_root = self.work
        start     = 0

        while start < len_body:
            if (not (valf := getattr(values[start], 'f', None)) or       # if value doesn't have FST
                not (child_parent := valf.parent) or                     # or no value parent
                (val_pfield := valf.pfield).name != 'values' or          # or value field is not 'values'
                (
                    val_pfield.idx == start                              # or (value is at the correct location
                    if child_parent is nodef else                        # if is our own child, else
                    not isinstance(child_parent.a, Dict)                 # value parent is not Dict)
                ) or
                (
                    child_parent.a.keys[val_pfield.idx] is not None      # or (key associated with value is not None
                    if (keya := keys[start]) is None else                # if our key is None, else
                    (
                        not (keyf := getattr(keya, 'f', None)) or        # if key doesn't have FST
                        keyf.parent is not child_parent or               # or key parent is not same as value parent
                        keyf.pfield != ('keys', val_pfield.idx)          # or key field is not 'keys' or key idx != value idx
                    )
                )
            ):
                end = start + 1

            else:  # slice operation, even if its just one element because slice copies more formatting and comments
                child_parent_keys = child_parent.a.keys
                child_idx         = val_pfield.idx
                child_off_idx     = child_idx - start

                for end in range(start + 1, len_body):  # get length of contiguous slice
                    if (not (f := getattr(values[end], 'f', None)) or
                        f.parent is not child_parent or
                        f.pfield != ('values', i := child_off_idx + end) or
                        (
                            child_parent_keys[i] is not None  # child_parent_keys and keys COULD be the same, but not guaranteed
                            if (a := keys[end]) is None else
                            (
                                not (f := getattr(a, 'f', None)) or
                                f.parent is not child_parent or
                                f.pfield != ('keys', i)
                            )
                        )
                    ):  # if is not following element then done
                        break

                else:
                    end = len_body

                if valf.root is not work_root:  # from different tree, need to verify first
                    try:
                        for i in range(start, end):
                            if key := keys[i]:
                                key.f.verify(reparse=False)

                            values[i].f.verify(reparse=False)

                        slice = child_parent.get_slice(child_idx, child_idx - start + end, None)

                    except Exception:  # verification failed, need to do one AST at a time
                        pass

                    else:  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements, couldn't anyway as we don't know anything about that tree
                        outf.put_slice(slice, start, end, None, raw=False)

                        start = end

                        continue

                else:
                    mark_parent = self.mark.child_from_path(self.work.child_path(child_parent))
                    slice       = mark_parent.get_slice(child_idx, child_idx - start + end, None)

                    outf.put_slice(slice, start, end, None, raw=False)

            len_outa_body = len(outa_keys)  # get each time because could have been modified by put_slice, will not change if coming from AST

            for i in range(start, end):
                k = keys[i]  # these are safe to use in 'put_slice()' then 'recurse()' without duplicating because ASTs are not consumed
                v = values[i]

                if i >= len_outa_body:  # if past end then we need to slice insert AST before recursing into it, doesn't happen if coming from AST
                    outf.put_slice(Dict(keys=[k], values=[v]), i, i, None, raw=False)

                if k:
                    self.recurse_node(k, astfield('keys', i), outf, nodef)
                elif outa_keys[i] is not None:
                    outf.put(None, i, False, 'keys', raw=False)

                self.recurse_node(v, astfield('values', i), outf, nodef)  # nodef set accordingly regardless of if coming from FST or AST

            start = end

        if start < len(outa_keys):  # delete tail in output, doesn't happen if coming from AST
            outf.put_slice(None, start, None, None, raw=False)

    def recurse_slice(self, node: AST, outf: Optional['FST'], field: str, body: list[AST]):
        """Recurse into a slice of children using slice operations to copy over formatting where possible (if not
        already there). Can be recursing an in-tree FST parent or a pure AST parent."""

        nodef     = getattr(node, 'f', False)  # this determines if it came from an in-tree FST or a pure AST
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
                    child_idx == start                                                               # or (child is at the correct location
                    if (child_field := child_pfield.name) == field and child_parent is nodef else    # if is from same field and our own child, else
                    not FST._is_slice_compatible(node_sig, (child_parent.a.__class__, child_field))  # child slice is not compatible)
                )
            ):                                                                                      # then can't possibly slice, or it doesn't make sense to
                end = start + 1

            else:  # slice operation, even if its just one element because slice copies more formatting and comments
                child_off_idx = child_idx - start

                for end in range(start + 1, len_body):  # get length of contiguous slice
                    if (not (f := getattr(body[end], 'f', None)) or
                        f.parent is not child_parent or
                        f.pfield != (child_field, child_off_idx + end)
                    ):  # if is not following element then done
                        break

                else:
                    end = len_body

                if childf.root is not work_root:  # from different tree, need to verify first
                    try:
                        for i in range(start, end):
                            body[i].f.verify(reparse=False)

                        slice = child_parent.get_slice(child_idx, child_off_idx + end, child_field)

                    except Exception:  # verification failed, need to do one AST at a time
                        pass

                    else:  # no recurse because we wouldn't be at this point if it wasn't a valid full FST without AST replacements, couldn't anyway as we don't know anything about that tree
                        outf.put_slice(slice, start, end, field, raw=False)

                        start = end

                        continue

                else:
                    mark_parent = self.mark.child_from_path(self.work.child_path(child_parent))
                    slice       = mark_parent.get_slice(child_idx, child_off_idx + end, child_field)

                    outf.put_slice(slice, start, end, field, raw=False)

            len_outa_body = len(outa_body)  # get each time because could have been modified by put_slice, will not change if coming from AST

            for i in range(start, end):
                n = body[i]  # this is safe to use in 'put_slice()' then 'recurse()' without duplicating because ASTs are not consumed

                if i >= len_outa_body:  # if past end then we need to slice insert AST before recursing into it, doesn't happen if coming from AST
                    outf.put_slice(n, i, i, field, one=True, raw=False)  # put one

                self.recurse_node(n, astfield(field, i), outf, nodef)  # nodef set accordingly regardless of if coming from FST or AST

            start = end

        if start < len(outa_body):  # delete tail in output, doesn't happen if coming from AST
            outf.put_slice(None, start, None, field, raw=False)

    def recurse_children(self, node: AST, outa: AST):
        """Recurse into children of a node."""

        if not isinstance(outa, AST):  # could be None or a Constant.value
            return

        nodef = getattr(node, 'f', False)  # this determines if it came from an in-tree FST or a pure AST
        outf  = outa.f

        for field, child in iter_fields(node):
            if field in ('ctx', 'str'):  # redundant or possibly contradictory
                continue

            if isinstance(child, AST):  # AST, but out may not have anything at this position
                # TODO: Compare special case, catch it at '.left' and do slice processing

                self.recurse_node(child, astfield(field), outf, nodef)

            elif not isinstance(child, list):  # primitive, or None to delete possibly AST child
                if nodef is not False and child != getattr(outa, field):  # this SHOULDN'T happen if coming from pure AST but could if there was a contradictory value set by the user, so in case of pure AST we don't do this at all because was set correctly on our own put of the AST somewhere above
                    outf.put(child, field=field, raw=False)

            else:  # slice
                if field in ('body', 'orelse', 'handlers', 'finalbody', 'cases', 'elts'):
                    self.recurse_slice(node, outf, field, child)

                    continue

                if field == 'keys':
                    if isinstance(node, Dict):
                        self.recurse_slice_dict(node, outf)

                        break  # so that 'values' doesn't get processed

                    else:
                        assert isinstance(node, MatchMapping)

                        # TODO: this special case

                if field == 'kwd_attrs' or (field == 'names' and isinstance(node, (Global, Nonlocal))):  # list of identifier names
                    continue


                # TODO: rest of slices when they are done


                # slice fallback, one by one but only if sizes are same

                if len(child) != len(getattr(outa, field)):  # this will never happen if coming from pure AST
                    raise NotImplementedError(f'different length slice fields {field!r}')

                for i, c in enumerate(child):
                    self.recurse_node(c, astfield(field, i), outf, nodef)

    def recurse_node(self, node: AST, pfield: astfield | None = None,
                     out_parent: Optional['FST'] = None, node_parent: Optional['FST'] | Literal[False] = None):
        """Recurse from either an in-tree known `FST` node or from a pure `AST` put somewhere above. The two situations
        are slightly different in the following ways:

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

            self.recurse_children(node, outa)

            return

        # FST node from original tree, recurse

        if node_parent is False or (nodef.parent is not node_parent or nodef.pfield != pfield):  # coming from pure AST or in-tree FST from off path
            copy = self.mark.child_from_path(self.work.child_path(nodef)).copy()

            self.put_node(copy, out_parent, pfield)  # copy from known good copy of tree

        outa = pfield.get(out_parent.a) if out_parent else self.out.a

        try:
            self.recurse_children(node, outa)
        except (NodeError, SyntaxError, ValueError, NotImplementedError):  # something failed below, so replace whole AST
            self.put_node(node, out_parent, pfield)


# ----------------------------------------------------------------------------------------------------------------------

def mark(self: 'FST') -> 'FST':
    """Return something marking the current state of this `FST` tree. Used to `reconcile()` later for non-FST operation
    changes made (changing `AST` nodes directly).

    **Returns:**
    - `FST`: A marked copy of `self` with any necessary information added for a future `reconcile()`. You can `mark()`
        this marked `FST` to get a usable copy."""

    if not self.is_root:
        raise ValueError('can only mark root nodes')

    mark         = self.copy()
    mark._serial = self._serial

    return mark

def reconcile(self: 'FST', mark: 'FST') -> 'FST':
    """Reconcile `self` with a previously marked version and return a new valid `FST` tree. This is meant for allowing
    non-FST modifications to an `FST` tree and later converting it to a valid `FST` tree to preserve as much formatting
    as possible and maybe continue operating in `FST` land.

    **WARNING!** Just because this function completes successfully does NOT mean the output is syntactically correct,
    e.g. set the last keyword argument default to `None` in a `FunctionDef` when there are preceding defaults set -
    `args.kw_defaults[-1]=None`. In order to make sure the result is valid you should run `verify()` on the output.

    **Parameters:**
    - `mark`: A previously marked snapshot of `self`. This object is not consumed on use, success or failure.

    **Returns:**
    - `FST`: A new valid reconciled `FST` if possible.
    """

    # TODO: allow multiple maked trees to participate?

    if not self.is_root:
        raise ValueError('can only reconcile root nodes')

    if self._serial != mark._serial:
        raise RuntimeError('modification detected after mark(), not reconcilable')

    rec = _Reconcile(self, mark)

    rec.recurse_node(self.a)

    return rec.out


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]  # used by make_docs.py

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
