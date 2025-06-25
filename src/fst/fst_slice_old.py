"""Old slice FST methods, need to update."""

from __future__ import annotations

from ast import *
from typing import Literal

from .astutil import *
from .astutil import TryStar

from .misc import (
    astfield, fstloc,
    Code, NodeError,
    _next_find, _prev_find,
    _fixup_slice_indices
)

from .srcedit_old import _src_edit


def _get_slice_seq_and_dedent(self: FST, get_ast: AST, cut: bool, seq_loc: fstloc,
                              ffirst: FST | fstloc, flast: FST | fstloc,
                              fpre: FST | fstloc | None, fpost: FST | fstloc | None,
                              prefix: str, suffix: str) -> FST:
    copy_loc, put_loc, put_lines = _src_edit.get_slice_seq(self, cut, seq_loc, ffirst, flast, fpre, fpost)

    copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

    if not cut:
        put_loc = None

    lines                  = self.root._lines
    get_ast.lineno         = copy_ln + 1
    get_ast.col_offset     = lines[copy_ln].c2b(copy_col)
    get_ast.end_lineno     = copy_end_ln + 1
    get_ast.end_col_offset = lines[copy_end_ln].c2b(copy_end_col)

    get_fst = self._make_fst_and_dedent(self, get_ast, copy_loc, prefix, suffix, put_loc, put_lines)

    get_ast.col_offset     = 0  # before prefix
    get_ast.end_col_offset = get_fst._lines[-1].lenbytes  # after suffix

    get_ast.f._touch()

    return get_fst


def _put_slice_seq_and_indent(self: FST, put_fst: FST | None, seq_loc: fstloc,
                              ffirst: FST | fstloc | None, flast: FST | fstloc | None,
                              fpre: FST | fstloc | None, fpost: FST | fstloc | None,
                              pfirst: FST | fstloc | None, plast: FST | fstloc | None,
                              docstr: bool | Literal['strict']) -> FST:
    root = self.root

    if not put_fst:  # delete
        # put_ln, put_col, put_end_ln, put_end_col = (
        #     _src_edit.put_slice_seq(self, None, '', seq_loc, ffirst, flast, fpre, fpost, None, None))
        _, (put_ln, put_col, put_end_ln, put_end_col), _ = (
            _src_edit.get_slice_seq(self, True, seq_loc, ffirst, flast, fpre, fpost))

        put_lines = None

    else:  # replace or insert
        assert put_fst.is_root

        indent = self.get_indent()

        put_fst._indent_lns(indent, docstr=docstr)

        put_ln, put_col, put_end_ln, put_end_col = (
            _src_edit.put_slice_seq(self, put_fst, indent, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast))

        lines           = root._lines
        put_lines       = put_fst._lines
        fst_dcol_offset = lines[put_ln].c2b(put_col)

        put_fst._offset(0, 0, put_ln, fst_dcol_offset)

    self_ln, self_col, _, _ = self.loc

    if put_col == self_col and put_ln == self_ln:  # unenclosed sequence
        self._offset(
            *root._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, not fpost, False, self),
            True, True, self_=False)

    elif fpost:
        root._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, False)
    else:
        root._put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, True, self)  # because of insertion at end and unparenthesized tuple


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

def _get_slice_tuple_list_or_set(self: FST, start: int | Literal['end'] | None, stop: int | None, field: str,
                                 cut: bool, **options) -> FST:
    if field != 'elts':
        raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

    ast         = self.a
    elts        = ast.elts
    is_set      = isinstance(ast, Set)
    is_tuple    = not is_set and isinstance(ast, Tuple)
    start, stop = _fixup_slice_indices(len(elts), start, stop)

    if start == stop:
        if is_set:
            return self._new_empty_set(from_=self)
        elif is_tuple:
            return self._new_empty_tuple(from_=self)
        else:
            return self._new_empty_list(from_=self)

    is_paren = is_tuple and self._is_parenthesized_seq()
    ffirst   = elts[start].f
    flast    = elts[stop - 1].f
    fpre     = elts[start - 1].f if start else None
    fpost    = elts[stop].f if stop < len(elts) else None

    if not cut:
        asts = [copy_ast(elts[i]) for i in range(start, stop)]

    else:
        asts = elts[start : stop]

        del elts[start : stop]

        for i in range(start, len(elts)):
            elts[i].f.pfield = astfield('elts', i)

    if is_set:
        get_ast = Set(elts=asts)  # location will be set later when span is potentially grown
        prefix  = '{'
        suffix  = '}'

    else:
        ctx     = ast.ctx.__class__
        get_ast = ast.__class__(elts=asts, ctx=ctx())

        if not issubclass(ctx, Load):
            set_ctx(get_ast, Load)

        if is_tuple:
            prefix = '('
            suffix = ')'

        else:  # list
            prefix = '['
            suffix = ']'

    if not is_tuple:
        seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

        assert self.root._lines[self.ln].startswith(prefix, self.col)
        assert self.root._lines[seq_loc.end_ln].startswith(suffix, seq_loc.end_col)

    else:
        if not is_paren:
            seq_loc = self.loc

        else:
            seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

            assert self.root._lines[seq_loc.end_ln].startswith(')', seq_loc.end_col)

    fst = _get_slice_seq_and_dedent(self, get_ast, cut, seq_loc, ffirst, flast, fpre, fpost, prefix, suffix)

    if is_set:
        self._maybe_fix_set()

    elif is_tuple:
        fst._maybe_add_singleton_tuple_comma(False)  # maybe need to add a postfix comma to copied single element tuple if is not already there
        self._maybe_fix_tuple(is_paren)

    return fst


# def _get_slice_empty_set(self: FST, start: int | Literal['end'] | None, stop: int | None, field: str,
#                          cut: bool, **options) -> FST:
#     if field is not None and field != 'elts':
#         raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

#     if stop or (start and start != 'end'):
#         raise IndexError(f"Set.{field} index out of range")

#     return self._new_empty_set(from_=self)


def _get_slice_dict(self: FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                    **options) -> FST:
    if field:
        raise ValueError(f"cannot specify a field '{field}' to slice from a Dict")

    ast         = self.a
    values      = ast.values
    start, stop = _fixup_slice_indices(len(values), start, stop)

    if start == stop:
        return self._new_empty_dict(from_=self)

    keys   = ast.keys
    ffirst = self._dict_key_or_mock_loc(keys[start], values[start].f)
    flast  = values[stop - 1].f
    fpre   = values[start - 1].f if start else None
    fpost  = self._dict_key_or_mock_loc(keys[stop], values[stop].f) if stop < len(keys) else None

    if not cut:
        akeys   = [copy_ast(keys[i]) for i in range(start, stop)]
        avalues = [copy_ast(values[i]) for i in range(start, stop)]

    else:
        akeys   = keys[start : stop]
        avalues = values[start : stop]

        del keys[start : stop]
        del values[start : stop]

        for i in range(start, len(keys)):
            values[i].f.pfield = astfield('values', i)

            if key := keys[i]:  # could be None from **
                key.f.pfield = astfield('keys', i)

    get_ast = Dict(keys=akeys, values=avalues)
    seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

    assert self.root._lines[self.ln].startswith('{', self.col)
    assert self.root._lines[seq_loc.end_ln].startswith('}', seq_loc.end_col)

    return _get_slice_seq_and_dedent(self, get_ast, cut, seq_loc, ffirst, flast, fpre, fpost, '{', '}')


def _get_slice_stmtish(self: FST, start: int | Literal['end'] | None, stop: int | None, field: str, cut: bool,
                       one: bool = False, **options) -> FST:
    ast         = self.a
    body        = getattr(ast, field)
    start, stop = _fixup_slice_indices(len(body), start, stop)

    if start == stop:
        return self._new_empty_module(from_=self)

    ffirst = body[start].f
    flast  = body[stop - 1].f
    fpre   = body[start - 1].f if start else None
    fpost  = body[stop].f if stop < len(body) else None
    indent = ffirst.get_indent()

    block_loc = fstloc(*(fpre.bloc[2:] if fpre else ffirst._prev_bound_step()),
                       *(fpost.bloc[:2] if fpost else flast._next_bound_step()))

    copy_loc, put_loc, put_lines = (
        _src_edit.get_slice_stmt(self, field, cut, block_loc, ffirst, flast, fpre, fpost, **options))

    if not cut:
        asts    = [copy_ast(body[i]) for i in range(start, stop)]
        put_loc = None

    else:
        is_last_child = not fpost and not flast.next()
        asts          = body[start : stop]

        del body[start : stop]

        for i in range(start, len(body)):
            body[i].f.pfield = astfield(field, i)

    if not one:
        get_ast = Module(body=asts, type_ignores=[])
    elif len(asts) == 1:
        get_ast = asts[0]
    else:
        raise ValueError(f'cannot specify `one=True` if getting multiple statements')

    fst = self._make_fst_and_dedent(indent, get_ast, copy_loc, '', '', put_loc, put_lines,
                                    docstr=options.get('docstr'))

    if cut and is_last_child:  # correct for removed last child nodes or last nodes past the block open colon
        self._set_block_end_from_last_child(block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)

    if len(asts) == 1 and isinstance(a := asts[0], If):
        a.f._maybe_fix_elif()

    return fst


def _put_slice_tuple_list_or_set(self: FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                 field: str, one: bool, **options):
    if field != 'elts':
        raise ValueError(f"invalid field '{field}' to assign slice to a {self.a.__class__.__name__}")

    if code is None:
        put_fst = None

    else:
        put_fst = self._code_as_expr(code, self.root.parse_params)

        if one:
            if (b := put_fst.is_parenthesized_tuple()) is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
                put_fst._parenthesize_node()
            elif b is None and precedence_require_parens(put_fst.a, self.a, 'elts', 0) and not put_fst.pars().n:
                put_fst._parenthesize_grouping()

            ls       = put_fst._lines
            put_ast  = Set(elts=[put_fst.a], lineno=1, col_offset=0, end_lineno=len(ls), end_col_offset=ls[-1].lenbytes)
            put_fst  = FST(put_ast, ls, from_=self, lcopy=False)
            is_tuple = is_set = False  # that's right, an `ast.Set` with `is_set=False` because in this case all we need is the `elts` container (without `ctx`)

        else:
            if empty_set := self.get_option('empty_set', options):
                if ((put_fst.is_empty_set_seq() or put_fst.is_empty_set_call()) if empty_set is True else
                    put_fst.is_empty_set_seq() if empty_set == 'seq' else put_fst.is_empty_set_call()  # else 'call'
                ):
                    put_fst = self._new_empty_set_curlies(from_=self)

            put_ast  = put_fst.a
            is_tuple = isinstance(put_ast, Tuple)
            is_set   = not is_tuple and isinstance(put_ast, Set)

            if not is_tuple and not is_set and not isinstance(put_ast, List):
                raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} "
                                f"must be a Tuple, List or Set, not a '{put_ast.__class__.__name__}'")

    ast         = self.a
    elts        = ast.elts
    start, stop = _fixup_slice_indices(len(elts), start, stop)
    slice_len   = stop - start

    if not slice_len and (not put_fst or not put_ast.elts):  # deleting or assigning empty seq to empty slice of seq, noop
        return

    is_self_tuple    = isinstance(ast, Tuple)
    is_self_set      = not is_self_tuple and isinstance(ast, Set)
    is_self_enclosed = not is_self_tuple or self._is_parenthesized_seq()
    fpre             = elts[start - 1].f if start else None
    fpost            = None if stop == len(elts) else elts[stop].f
    seq_loc          = fstloc(self.ln, self.col + is_self_enclosed, self.end_ln, self.end_col - is_self_enclosed)

    if not slice_len:
        ffirst = flast = None

    else:
        ffirst = elts[start].f
        flast  = elts[stop - 1].f

    if not put_fst:
        _put_slice_seq_and_indent(self, None, seq_loc, ffirst, flast, fpre, fpost, None, None, options.get('docstr'))
        self._unmake_fst_tree(elts[start : stop])

        del elts[start : stop]

        put_len = 0

    else:
        put_lines = put_fst._lines

        if one:
            pass  # noop

        elif not is_tuple:
            put_ast.end_col_offset -= 1  # strip enclosing curlies or brackets from source set or list

            put_fst._offset(0, 1, 0, -1)

            assert put_lines[0].startswith('[{'[is_set])
            assert put_lines[-1].endswith(']}'[is_set])

            put_lines[-1] = bistr(put_lines[-1][:-1])
            put_lines[0]  = bistr(put_lines[0][1:])

        elif put_fst._is_parenthesized_seq():
            put_ast.end_col_offset -= 1  # strip enclosing parentheses from source tuple

            put_fst._offset(0, 1, 0, -1)

            put_lines[-1] = bistr(put_lines[-1][:-1])
            put_lines[0]  = bistr(put_lines[0][1:])

        if not (selts := put_ast.elts):
            pfirst = plast = None

        else:
            pfirst = selts[0].f
            plast  = selts[-1].f

        _put_slice_seq_and_indent(self, put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast, options.get('docstr'))
        self._unmake_fst_tree(elts[start : stop])
        put_fst._unmake_fst_parents(True)

        elts[start : stop] = put_ast.elts

        put_len = len(put_ast.elts)
        stack   = [FST(elts[i], self, astfield('elts', i)) for i in range(start, start + put_len)]

        if stack and not is_self_set:
            set_ctx([f.a for f in stack], ast.ctx.__class__)

        self._make_fst_tree(stack)

    for i in range(start + put_len, len(elts)):
        elts[i].f.pfield = astfield('elts', i)

    if is_self_tuple:
        self._maybe_fix_tuple(is_self_enclosed)
    elif is_self_set:
        self._maybe_fix_set()


# def _put_slice_empty_set(self: FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
#                          field: str, one: bool, **options):
#     ln, col, end_ln, end_col = self.loc

#     empty   = self._new_empty_set_curlies(False, (a := self.a).lineno, a.col_offset, from_=self)
#     old_src = self.get_src(ln, col, end_ln, end_col, True)
#     old_ast = self._set_ast(empty.a)

#     self._put_src(empty._lines, ln, col, end_ln, end_col, True, True, self, offset_excluded=False)

#     try:
#         self._put_slice_tuple_list_or_set(code, start, stop, field, one, **options)

#     finally:
#         if not self.a.elts:
#             self._put_src(old_src, *self.loc, True)  # restore previous empty set representation
#             self._set_ast(old_ast)


def _put_slice_dict(self: FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                    field: str, one: bool, **options):
    if field:
        raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")
    if one and code is not None:
        raise ValueError(f'cannot put a single item to a Dict slice')

    if code is None:
        put_fst = None

    else:
        put_fst = self._code_as_expr(code, self.root.parse_params)
        put_ast = put_fst.a

        if not isinstance(put_ast, Dict):
            raise ValueError(f"slice being assigned to a Dict must be a Dict, not a '{put_ast.__class__.__name__}'")

    ast         = self.a
    values      = ast.values
    start, stop = _fixup_slice_indices(len(values), start, stop)
    slice_len   = stop - start

    if not slice_len and (not put_fst or not put_ast.keys):  # deleting or assigning empty dict to empty slice of dict, noop
        return

    keys    = ast.keys
    fpre    = values[start - 1].f if start else None
    fpost   = None if stop == len(keys) else self._dict_key_or_mock_loc(keys[stop], values[stop].f)
    seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

    if not slice_len:
        ffirst = flast = None

    else:
        ffirst = self._dict_key_or_mock_loc(keys[start], values[start].f)
        flast  = values[stop - 1].f

    if not put_fst:
        _put_slice_seq_and_indent(self, None, seq_loc, ffirst, flast, fpre, fpost, None, None, options.get('docstr'))
        self._unmake_fst_tree(keys[start : stop] + values[start : stop])

        del keys[start : stop]
        del values[start : stop]

        put_len = 0

    else:
        put_lines               = put_fst._lines
        put_ast.end_col_offset -= 1  # strip enclosing curlies from source dict

        put_fst._offset(0, 1, 0, -1)

        assert put_lines[0].startswith('{')
        assert put_lines[-1].endswith('}')

        put_lines[-1] = bistr(put_lines[-1][:-1])
        put_lines[0]  = bistr(put_lines[0][1:])

        if not (skeys := put_ast.keys):
            pfirst = plast = None

        else:
            pfirst = put_fst._dict_key_or_mock_loc(skeys[0], put_ast.values[0].f)
            plast  = put_ast.values[-1].f

        _put_slice_seq_and_indent(self, put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast, options.get('docstr'))
        self._unmake_fst_tree(keys[start : stop] + values[start : stop])
        put_fst._unmake_fst_parents(True)

        keys[start : stop]   = put_ast.keys
        values[start : stop] = put_ast.values
        put_len              = len(put_ast.keys)
        stack                = []

        for i in range(put_len):
            startplusi = start + i

            stack.append(FST(values[startplusi], self, astfield('values', startplusi)))

            if key := keys[startplusi]:
                stack.append(FST(key, self, astfield('keys', startplusi)))

        self._make_fst_tree(stack)

    for i in range(start + put_len, len(keys)):
        values[i].f.pfield = astfield('values', i)

        if key := keys[i]:  # could be None from **
            key.f.pfield = astfield('keys', i)


def _put_slice_stmtish(self: FST, code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                       field: str, one: bool, **options):
    ast  = self.a
    body = getattr(ast, field)

    if code is None:
        put_fst = None

    else:
        put_fst  = self._code_as_stmtishs(code, self.root.parse_params, is_trystar=isinstance(ast, TryStar))
        put_ast  = put_fst.a
        put_body = put_ast.body

        if one and len(put_body) != 1:
            raise ValueError('expecting a single statement')

        node_type = ExceptHandler if field == 'handlers' else match_case if field == 'cases' else stmt

        if any(not isinstance(bad_node := n, node_type) for n in put_body) and options.get('check_node_type', True):  # TODO: `check_node_type` is for some previously written tests, but really should fix those tests instead
            raise ValueError(f"cannot put {bad_node.__class__.__qualname__} node to '{field}' field")

    start, stop = _fixup_slice_indices(len(body), start, stop)
    slice_len   = stop - start

    if not slice_len and (not put_fst or (not put_body and len(ls := put_fst._lines) == 1 and not ls[0])):  # deleting empty slice or assigning empty fst to empty slice, noop
        return

    root  = self.root
    lines = root._lines
    fpre  = body[start - 1].f if start else None
    fpost = body[stop].f if stop < len(body) else None

    if put_fst:
        opener_indent = self.get_indent()

        if not body:
            block_indent = opener_indent if isinstance(self.a, mod) else opener_indent + root.indent
        elif not (b0 := body[0]).f.is_elif():
            block_indent = b0.f.get_indent()
        elif (bb := b0.body) or (bb := b0.orelse):
            block_indent = bb[0].f.get_indent()
        else:
            block_indent = opener_indent + root.indent

        if fpre or fpost:
            self._normalize_block(field, indent=block_indent)  # don't want to bother figuring out if valid to insert to statements on single block logical line

    if slice_len:  # replacement
        ffirst = body[start].f
        flast  = body[stop - 1].f

        block_loc = fstloc(*(fpre.bloc[2:] if fpre else ffirst._prev_bound_step()),
                           *(fpost.bloc[:2] if fpost else flast._next_bound_step()))

        is_last_child = not fpost and not flast.next()

    else:  # insertion
        ffirst = flast = None

        if field == 'orelse' and len(body) == 1 and (f := body[0].f).is_elif():
            f._elif_to_else_if()

        if fpre:
            block_loc     = fstloc(*fpre.bloc[2:], *(fpost.bloc[:2] if fpost else fpre._next_bound_step()))
            is_last_child = not fpost and not fpre.next()

        elif fpost:
            if isinstance(ast, mod):  # put after all header stuff in module
                ln, col, _, _ = fpost.bloc
                block_loc     = fstloc(ln, col, ln, col)

            elif field != 'handlers' or ast.body:
                block_loc = fstloc(*fpost._prev_bound_step(), *fpost.bloc[:2])

            else:  # special case because 'try:' doesn't have ASTs inside it and each 'except:' lives at the 'try:' indentation level
                end_ln, end_col = fpost.bloc[:2]
                ln, col         = _prev_find(lines, *fpost._prev_bound_step(), end_ln, end_col, ':')
                block_loc       = fstloc(ln, col + 1, end_ln, end_col)

            is_last_child = False

        else:  # insertion into empty block (or nonexistent 'else' or 'finally' block)
            if not put_body and field in ('orelse', 'finalbody'):
                raise ValueError(f"cannot insert empty statement into empty '{field}' field")

            if isinstance(ast, (FunctionDef, AsyncFunctionDef, ClassDef, With, AsyncWith, Match, ExceptHandler,
                                match_case)):  # only one block possible, 'body' or 'cases'
                block_loc     = fstloc(*self.bloc[2:], *self._next_bound_step())  # end of bloc will be just past ':'
                is_last_child = True

            elif isinstance(ast, mod):  # put after all header stuff in module
                _, _, end_ln, end_col = self.bloc

                block_loc     = fstloc(end_ln, end_col, end_ln, end_col)
                is_last_child = True

            elif isinstance(ast, (For, AsyncFor, While, If)):  # 'body' or 'orelse'
                if field == 'orelse':
                    is_last_child = True

                    if not (body_ := ast.body):
                        block_loc = fstloc(*self.bloc[2:], *self._next_bound_step())
                    else:
                        block_loc = fstloc(*body_[-1].f.bloc[2:], *self._next_bound_step())

                else:  # field == 'body':
                    if orelse := ast.orelse:
                        ln, col       = _next_find(lines, *(f := orelse[0].f).prev().bloc[2:], *f.bloc[:2], ':')  # we know its there
                        block_loc     = fstloc(ln, col + 1, *orelse[0].f.bloc[:2])
                        is_last_child = False

                    else:
                        block_loc     = fstloc(*self.bloc[2:], *self._next_bound_step())
                        is_last_child = True

            else:  # isinstance(ast, (Try, TryStar))
                assert isinstance(ast, (Try, TryStar))

                if field == 'finalbody':
                    is_last_child = True

                    if not (block := ast.orelse) and not (block := ast.handlers) and not (block := ast.body):
                        block_loc = fstloc(*self.bloc[2:], *self._next_bound_step())
                    else:
                        block_loc = fstloc(*block[-1].f.bloc[2:], *self._next_bound_step())

                elif field == 'orelse':
                    if finalbody := ast.finalbody:
                        end_ln, end_col = _prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')  # we can use bloc[:2] even if there are ASTs between that and here because 'finally' must be on its own line
                        is_last_child   = False

                    else:
                        end_ln, end_col = self._next_bound_step()
                        is_last_child   = True

                    if not (block := ast.handlers) and not (block := ast.body):
                        ln, col   = _prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                        block_loc = fstloc(ln, col + 1, end_ln, end_col)

                    else:
                        block_loc = fstloc(*block[-1].f.bloc[2:], end_ln, end_col)

                elif field == 'handlers':
                    if orelse := ast.orelse:
                        end_ln, end_col = _prev_find(lines, *self.bloc[:2], *orelse[0].f.bloc[:2], 'else')
                        is_last_child   = False

                    elif finalbody := ast.finalbody:
                        end_ln, end_col = _prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')
                        is_last_child   = False

                    else:
                        end_ln, end_col = self._next_bound_step()
                        is_last_child   = True

                    if not (body_ := ast.body):
                        ln, col   = _prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                        block_loc = fstloc(ln, col + 1, end_ln, end_col)

                    else:
                        block_loc = fstloc(*body_[-1].f.bloc[2:], end_ln, end_col)

                else:  # field == 'body'
                    if handlers := ast.handlers:
                        end_ln, end_col = handlers[0].f.bloc[:2]
                        is_last_child   = False

                    elif orelse := ast.orelse:
                        end_ln, end_col = _prev_find(lines, *self.bloc[:2], *orelse[0].f.bloc[:2], 'else')
                        is_last_child   = False

                    elif finalbody := ast.finalbody:
                        end_ln, end_col = _prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')
                        is_last_child   = False

                    else:
                        end_ln, end_col = self._next_bound_step()
                        is_last_child   = True

                    ln, col   = _prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                    block_loc = fstloc(ln, col + 1, end_ln, end_col)

    if not put_fst:
        _, put_loc, put_lines = (
            _src_edit.get_slice_stmt(self, field, True, block_loc, ffirst, flast, fpre, fpost, **options))

        if put_loc:
            self._put_src(put_lines, *put_loc, True)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        put_len = 0

    else:
        put_loc = _src_edit.put_slice_stmt(self, put_fst, field, block_loc, opener_indent, block_indent,
                                           ffirst, flast, fpre, fpost, **options)

        put_fst._offset(0, 0, put_loc.ln, 0 if put_fst.bln or put_fst.bcol else lines[put_loc.ln].c2b(put_loc.col))
        self._put_src(put_fst.lines, *put_loc, False)
        self._unmake_fst_tree(body[start : stop])
        put_fst._unmake_fst_parents(True)

        body[start : stop] = put_body

        put_len = len(put_body)
        stack   = [FST(body[i], self, astfield(field, i)) for i in range(start, start + put_len)]

        self._make_fst_tree(stack)

    for i in range(start + put_len, len(body)):
        body[i].f.pfield = astfield(field, i)

    if is_last_child:  # correct parent for modified / removed last child nodes
        if not put_fst:
            self._set_block_end_from_last_child(block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)
        elif put_body:
            self._set_end_pos((last_child := self.last_child()).end_lineno, last_child.end_col_offset)


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]  # used by make_docs.py

from .fst import FST  # this imports a fake FST which is replaced in globals() when fst.py finishes loading
