"""Slice FST methods."""

import ast as ast_
import inspect
import re
from ast import *
from ast import parse as ast_parse, unparse as ast_unparse
from io import TextIOBase
from itertools import takewhile
from typing import Any, Callable, Generator, Literal, NamedTuple, Optional, TextIO, TypeAlias, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, type_param, TypeVar, ParamSpec, TypeVarTuple, TemplateStr, Interpolation

from .shared import (
    astfield, fstloc, srcwpos,
    AST_FIELDS_NEXT, AST_FIELDS_PREV, AST_DEFAULT_BODY_FIELD, EXPRESSIONISH,
    STATEMENTISH, STATEMENTISH_OR_MOD, STATEMENTISH_OR_STMTMOD, BLOCK, BLOCK_OR_MOD, SCOPE, SCOPE_OR_MOD, NAMED_SCOPE,
    NAMED_SCOPE_OR_MOD, ANONYMOUS_SCOPE, PARENTHESIZABLE, HAS_DOCSTRING,
    STATEMENTISH_FIELDS,
    PATH_BODY, PATH_BODY2, PATH_BODYORELSE, PATH_BODY2ORELSE, PATH_BODYHANDLERS, PATH_BODY2HANDLERS, PATH_BODYCASES,
    DEFAULT_PARSE_PARAMS, DEFAULT_INDENT,
    DEFAULT_DOCSTR, DEFAULT_PRECOMMS, DEFAULT_POSTCOMMS, DEFAULT_PRESPACE, DEFAULT_POSTSPACE, DEFAULT_PEP8SPACE,
    DEFAULT_PARS, DEFAULT_ELIF_, DEFAULT_FIX, DEFAULT_RAW,
    re_empty_line_start, re_empty_line, re_comment_line_start, re_line_continuation, re_line_trailing_space,
    re_oneline_str, re_contline_str_start, re_contline_str_end_sq, re_contline_str_end_dq, re_multiline_str_start,
    re_multiline_str_end_sq, re_multiline_str_end_dq, re_empty_line_cont_or_comment, re_next_src,
    re_next_src_or_comment, re_next_src_or_lcont, re_next_src_or_comment_or_lcont,
    Code, NodeTypeError,
    _with_loc, _next_src, _prev_src, _next_find, _prev_find, _next_pars, _prev_pars, _params_offset, _fixup_field_body,
    _fixup_slice_index, _reduce_ast
)

from .srcedit import _src_edit


def _make_fst_and_dedent(self: 'FST', indent: Union['FST', str], ast: AST, copy_loc: fstloc,
                            prefix: str = '', suffix: str = '',
                            put_loc: fstloc | None = None, put_lines: list[str] | None = None, *,
                            docstr: bool | Literal['strict'] | None = None) -> 'FST':
    if not isinstance(indent, str):
        indent = indent.get_indent()

    lines = self.root._lines
    fst   = FST(ast, lines=lines, from_=self)  # we use original lines for nodes offset calc before putting new lines

    fst.offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix.encode()) - lines[copy_loc.ln].c2b(copy_loc.col))

    fst._lines = fst_lines = self.get_src(*copy_loc, True)

    if suffix:
        fst_lines[-1] = bistr(fst_lines[-1] + suffix)

    if prefix:
        fst_lines[0] = bistr(prefix + fst_lines[0])

    fst.dedent_lns(indent, skip=bool(copy_loc.col), docstr=docstr)  # if copy location starts at column 0 then we apply dedent to it as well (preceding comment or something)

    if put_loc:
        self.put_src(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0

    return fst

def _get_slice_seq_and_dedent(self: 'FST', get_ast: AST, cut: bool, seq_loc: fstloc,
                        ffirst: Union['FST', fstloc], flast: Union['FST', fstloc],
                        fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                        prefix: str, suffix: str) -> 'FST':
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

def _get_slice_tuple_list_or_set(self: 'FST', start: int | Literal['end'] | None, stop: int | None, field: str | None,
                                    cut: bool, **options) -> 'FST':
    if field is not None and field != 'elts':
        raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

    fix         = FST.get_option('fix', options)
    ast         = self.a
    elts        = ast.elts
    is_set      = isinstance(ast, Set)
    is_tuple    = not is_set and isinstance(ast, Tuple)
    start, stop = _fixup_slice_index(len(elts), start, stop)

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

        if fix and not issubclass(ctx, Load):
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

    fst = self._get_slice_seq_and_dedent(get_ast, cut, seq_loc, ffirst, flast, fpre, fpost, prefix, suffix)

    if fix:
        if is_set:
            self._maybe_fix_set()

        elif is_tuple:
            fst._maybe_add_singleton_tuple_comma(False)  # maybe need to add a postfix comma to copied single element tuple if is not already there
            self._maybe_fix_tuple(is_paren)

    return fst

def _get_slice_empty_set(self: 'FST', start: int | Literal['end'] | None, stop: int | None, field: str | None,
                                cut: bool, **options) -> 'FST':
    fix = FST.get_option('fix', options)

    if not fix:
        raise ValueError(f"cannot get slice from an empty Set without specifying 'fix=True'")

    if field is not None and field != 'elts':
        raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

    if stop or (start and start != 'end'):
        raise IndexError(f"Set.{field} index out of range")

    return self._new_empty_set(from_=self)

def _get_slice_dict(self: 'FST', start: int | Literal['end'] | None, stop: int | None, field: str | None, cut: bool,
                    **options) -> 'FST':
    if field is not None:
        raise ValueError(f"cannot specify a field '{field}' to slice from a Dict")

    fix         = FST.get_option('fix', options)
    ast         = self.a
    values      = ast.values
    start, stop = _fixup_slice_index(len(values), start, stop)

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

    return self._get_slice_seq_and_dedent(get_ast, cut, seq_loc, ffirst, flast, fpre, fpost, '{', '}')

def _get_slice_stmtish(self: 'FST', start: int | Literal['end'] | None, stop: int | None, field: str | None, cut: bool,
                    one: bool = False, **options) -> 'FST':
    fix         = FST.get_option('fix', options)
    ast         = self.a
    field, body = _fixup_field_body(ast, field)
    start, stop = _fixup_slice_index(len(body), start, stop)

    if start == stop:
        return self._new_empty_module(from_=self)

    ffirst = body[start].f
    flast  = body[stop - 1].f
    fpre   = body[start - 1].f if start else None
    fpost  = body[stop].f if stop < len(body) else None
    indent = ffirst.get_indent()

    block_loc = fstloc(*(fpre.bloc[2:] if fpre else ffirst._prev_ast_bound()),
                        *(fpost.bloc[:2] if fpost else flast._next_ast_bound()))

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
        self._fix_block_del_last_child(block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)

    if fix:
        if len(asts) == 1 and isinstance(a := asts[0], If):
            a.f._maybe_fix_elif()

    return fst

def _put_slice_seq_and_indent(self: 'FST', put_fst: Optional['FST'], seq_loc: fstloc,
                        ffirst: Union['FST', fstloc, None], flast: Union['FST', fstloc, None],
                        fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                        pfirst: Union['FST', fstloc, None], plast: Union['FST', fstloc, None],
                        docstr: bool | Literal['strict']) -> 'FST':
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

        put_fst.indent_lns(indent, docstr=docstr)

        put_ln, put_col, put_end_ln, put_end_col = (
            _src_edit.put_slice_seq(self, put_fst, indent, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast))

        lines           = root._lines
        put_lines       = put_fst._lines
        fst_dcol_offset = lines[put_ln].c2b(put_col)

        put_fst.offset(0, 0, put_ln, fst_dcol_offset)

    self_ln, self_col, _, _ = self.loc

    if put_col == self_col and put_ln == self_ln:  # unenclosed sequence
        self.offset(
            *root.put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, not fpost, False, self),
            True, True, self_=False)

    elif fpost:
        root.put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, False)
    else:
        root.put_src(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, True, self)  # because of insertion at end and unparenthesized tuple

def _put_slice_tuple_list_or_set(self: 'FST', code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                    field: str | None, one: bool, **options):
    if field is not None and field != 'elts':
        raise ValueError(f"invalid field '{field}' to assign slice to a {self.a.__class__.__name__}")

    fix = FST.get_option('fix', options)

    if code is None:
        put_fst = None

    else:
        put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)

        if one:
            if put_fst.is_parenthesized_tuple() is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
                put_fst._parenthesize_tuple()

            put_ast  = Set(elts=[put_fst.a], lineno=1, col_offset=0, end_lineno=len(ls := put_fst._lines),
                            end_col_offset=ls[-1].lenbytes)
            put_fst  = FST(put_ast, lines=ls)
            is_tuple = is_set = False  # that's right, an `ast.Set` with `is_set=False` because in this case all we need is the `elts` container (without `ctx`)

        else:
            if put_fst.is_empty_set_call() or put_fst.is_empty_set_seq():
                if fix:
                    put_fst = self._new_empty_set_curlies(from_=self)
                else:
                    raise ValueError(f"cannot put empty Set as a slice without specifying 'fix=True'")

            put_ast  = put_fst.a
            is_tuple = isinstance(put_ast, Tuple)
            is_set   = not is_tuple and isinstance(put_ast, Set)

            if not is_tuple and not is_set and not isinstance(put_ast, List):
                raise NodeTypeError(f"slice being assigned to a {self.a.__class__.__name__} "
                                    f"must be a Tuple, List or Set, not a '{put_ast.__class__.__name__}'")

    ast         = self.a
    elts        = ast.elts
    start, stop = _fixup_slice_index(len(elts), start, stop)
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
        self._put_slice_seq_and_indent(None, seq_loc, ffirst, flast, fpre, fpost, None, None, options.get('docstr'))
        self._unmake_fst_tree(elts[start : stop])

        del elts[start : stop]

        put_len = 0

    else:
        put_lines = put_fst._lines

        if one:
            pass  # noop

        elif not is_tuple:
            put_ast.end_col_offset -= 1  # strip enclosing curlies or brackets from source set or list

            put_fst.offset(0, 1, 0, -1)

            assert put_lines[0].startswith('[{'[is_set])
            assert put_lines[-1].endswith(']}'[is_set])

            put_lines[-1] = bistr(put_lines[-1][:-1])
            put_lines[0]  = bistr(put_lines[0][1:])

        elif put_fst._is_parenthesized_seq():
            put_ast.end_col_offset -= 1  # strip enclosing parentheses from source tuple

            put_fst.offset(0, 1, 0, -1)

            put_lines[-1] = bistr(put_lines[-1][:-1])
            put_lines[0]  = bistr(put_lines[0][1:])

        if not (selts := put_ast.elts):
            pfirst = plast = None

        else:
            pfirst = selts[0].f
            plast  = selts[-1].f

        self._put_slice_seq_and_indent(put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast, options.get('docstr'))
        self._unmake_fst_tree(elts[start : stop], put_fst)

        elts[start : stop] = put_ast.elts

        put_len = len(put_ast.elts)
        stack   = [FST(elts[i], self, astfield('elts', i)) for i in range(start, start + put_len)]

        if fix and stack and not is_set:
            set_ctx([f.a for f in stack], Load if is_self_set else ast.ctx.__class__)

        self._make_fst_tree(stack)

    for i in range(start + put_len, len(elts)):
        elts[i].f.pfield = astfield('elts', i)

    if fix:
        if is_self_tuple:
            self._maybe_fix_tuple(is_self_enclosed)
        elif is_self_set:
            self._maybe_fix_set()

def _put_slice_empty_set(self: 'FST', code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                                field: str | None, one: bool, **options):
    fix = FST.get_option('fix', options)

    if not fix:
        raise ValueError(f"cannot put slice to an empty Set without specifying 'fix=True'")

    ln, col, end_ln, end_col = self.loc

    empty   = self._new_empty_set_curlies(False, (a := self.a).lineno, a.col_offset, from_=self)
    old_src = self.get_src(ln, col, end_ln, end_col, True)
    old_ast = self._set_ast(empty.a)

    self.put_src(empty._lines, ln, col, end_ln, end_col, True, True, self, offset_excluded=False)

    try:
        self._put_slice_tuple_list_or_set(code, start, stop, field, one, **options)

    finally:
        if not self.a.elts:
            self.put_src(old_src, *self.loc, True)  # restore previous empty set representation
            self._set_ast(old_ast)

def _put_slice_dict(self: 'FST', code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                    field: str | None, one: bool, **options):
    if field is not None:
        raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")
    if one:
        raise ValueError(f'cannot put a single item to a Dict slice')

    if code is None:
        put_fst = None

    else:
        put_fst = self._normalize_code(code, 'expr', parse_params=self.root.parse_params)
        put_ast = put_fst.a

        if not isinstance(put_ast, Dict):
            raise ValueError(f"slice being assigned to a Dict must be a Dict, not a '{put_ast.__class__.__name__}'")

    ast         = self.a
    values      = ast.values
    start, stop = _fixup_slice_index(len(values), start, stop)
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
        self._put_slice_seq_and_indent(None, seq_loc, ffirst, flast, fpre, fpost, None, None, options.get('docstr'))
        self._unmake_fst_tree(keys[start : stop] + values[start : stop])

        del keys[start : stop]
        del values[start : stop]

        put_len = 0

    else:
        put_lines               = put_fst._lines
        put_ast.end_col_offset -= 1  # strip enclosing curlies from source dict

        put_fst.offset(0, 1, 0, -1)

        assert put_lines[0].startswith('{')
        assert put_lines[-1].endswith('}')

        put_lines[-1] = bistr(put_lines[-1][:-1])
        put_lines[0]  = bistr(put_lines[0][1:])

        if not (skeys := put_ast.keys):
            pfirst = plast = None

        else:
            pfirst = put_fst._dict_key_or_mock_loc(skeys[0], put_ast.values[0].f)
            plast  = put_ast.values[-1].f

        self._put_slice_seq_and_indent(put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast, options.get('docstr'))
        self._unmake_fst_tree(keys[start : stop] + values[start : stop], put_fst)

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

def _put_slice_stmtish(self: 'FST', code: Code | None, start: int | Literal['end'] | None, stop: int | None,
                    field: str | None, one: bool, **options):
    ast         = self.a
    field, body = _fixup_field_body(ast, field)

    if code is None:
        put_fst = None

    else:
        put_fst  = self._normalize_code(code, 'mod', parse_params=self.root.parse_params)
        put_ast  = put_fst.a
        put_body = put_ast.body

        if one and len(put_body) != 1:
            raise ValueError('expecting a single statement')

        node_type = ExceptHandler if field == 'handlers' else match_case if field == 'cases' else stmt

        if any(not isinstance(bad_node := n, node_type) for n in put_body) and options.get('check_node_type', True):  # TODO: `check_node_type` is for some previously written tests, but really should fix those tests instead
            raise ValueError(f"cannot put {bad_node.__class__.__qualname__} node to '{field}' field")

    start, stop = _fixup_slice_index(len(body), start, stop)
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
            block_indent = opener_indent if self.is_root else opener_indent + root.indent
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

        block_loc = fstloc(*(fpre.bloc[2:] if fpre else ffirst._prev_ast_bound()),
                            *(fpost.bloc[:2] if fpost else flast._next_ast_bound()))

        is_last_child = not fpost and not flast.next()

    else:  # insertion
        ffirst = flast = None

        if field == 'orelse' and len(body) == 1 and (f := body[0].f).is_elif():
            f._elif_to_else_if()

        if fpre:
            block_loc     = fstloc(*fpre.bloc[2:], *(fpost.bloc[:2] if fpost else fpre._next_ast_bound()))
            is_last_child = not fpost and not fpre.next()

        elif fpost:
            if isinstance(ast, mod):  # put after all header stuff in module
                ln, col, _, _ = fpost.bloc
                block_loc     = fstloc(ln, col, ln, col)

            elif field != 'handlers' or ast.body:
                block_loc = fstloc(*fpost._prev_ast_bound(), *fpost.bloc[:2])

            else:  # special case because 'try:' doesn't have ASTs inside it and each 'except:' lives at the 'try:' indentation level
                end_ln, end_col = fpost.bloc[:2]
                ln, col         = _prev_find(lines, *fpost._prev_ast_bound(), end_ln, end_col, ':')
                block_loc       = fstloc(ln, col + 1, end_ln, end_col)

            is_last_child = False

        else:  # insertion into empty block (or nonexistent 'else' or 'finally' block)
            if not put_body and field in ('orelse', 'finalbody'):
                raise ValueError(f"cannot insert empty statement into empty '{field}' field")

            if isinstance(ast, (FunctionDef, AsyncFunctionDef, ClassDef, With, AsyncWith, Match, ExceptHandler,
                                match_case)):  # only one block possible, 'body' or 'cases'
                block_loc     = fstloc(*self.bloc[2:], *self._next_ast_bound())  # end of bloc will be just past ':'
                is_last_child = True

            elif isinstance(ast, mod):  # put after all header stuff in module
                _, _, end_ln, end_col = self.bloc

                block_loc     = fstloc(end_ln, end_col, end_ln, end_col)
                is_last_child = True

            elif isinstance(ast, (For, AsyncFor, While, If)):  # 'body' or 'orelse'
                if field == 'orelse':
                    is_last_child = True

                    if not (body_ := ast.body):
                        block_loc = fstloc(*self.bloc[2:], *self._next_ast_bound())
                    else:
                        block_loc = fstloc(*body_[-1].f.bloc[2:], *self._next_ast_bound())

                else:  # field == 'body':
                    if orelse := ast.orelse:
                        ln, col       = _next_find(lines, *(f := orelse[0].f).prev().bloc[2:], *f.bloc[:2], ':')  # we know its there
                        block_loc     = fstloc(ln, col + 1, *orelse[0].f.bloc[:2])
                        is_last_child = False

                    else:
                        block_loc     = fstloc(*self.bloc[2:], *self._next_ast_bound())
                        is_last_child = True

            else:  # isinstance(ast, (Try, TryStar))
                assert isinstance(ast, (Try, TryStar))

                if field == 'finalbody':
                    is_last_child = True

                    if not (block := ast.orelse) and not (block := ast.handlers) and not (block := ast.body):
                        block_loc = fstloc(*self.bloc[2:], *self._next_ast_bound())
                    else:
                        block_loc = fstloc(*block[-1].f.bloc[2:], *self._next_ast_bound())

                elif field == 'orelse':
                    if finalbody := ast.finalbody:
                        end_ln, end_col = _prev_find(lines, *self.bloc[:2], *finalbody[0].f.bloc[:2], 'finally')  # we can use bloc[:2] even if there are ASTs between that and here because 'finally' must be on its own line
                        is_last_child   = False

                    else:
                        end_ln, end_col = self._next_ast_bound()
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
                        end_ln, end_col = self._next_ast_bound()
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
                        end_ln, end_col = self._next_ast_bound()
                        is_last_child   = True

                    ln, col   = _prev_find(lines, *self.bloc[:2], end_ln, end_col, ':')
                    block_loc = fstloc(ln, col + 1, end_ln, end_col)

    if not put_fst:
        _, put_loc, put_lines = (
            _src_edit.get_slice_stmt(self, field, True, block_loc, ffirst, flast, fpre, fpost, **options))

        if put_loc:
            self.put_src(put_lines, *put_loc, True)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        put_len = 0

    else:
        put_loc = _src_edit.put_slice_stmt(self, put_fst, field, block_loc, opener_indent, block_indent,
                                            ffirst, flast, fpre, fpost, **options)

        put_fst.offset(0, 0, put_loc.ln, 0 if put_fst.bln or put_fst.bcol else lines[put_loc.ln].c2b(put_loc.col))
        self.put_src(put_fst.lines, *put_loc, False)
        self._unmake_fst_tree(body[start : stop], put_fst)

        body[start : stop] = put_body

        put_len = len(put_body)
        stack   = [FST(body[i], self, astfield(field, i)) for i in range(start, start + put_len)]

        self._make_fst_tree(stack)

    for i in range(start + put_len, len(body)):
        body[i].f.pfield = astfield(field, i)

    if is_last_child:  # correct parent for modified / removed last child nodes
        if not put_fst:
            self._fix_block_del_last_child(block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)
        elif put_body:
            self._set_end_pos((last_child := self.last_child()).end_lineno, last_child.end_col_offset)

def _put_slice_raw(self: 'FST', code: Code | None, start: int | Literal['end'] | None = None, stop: int | None = None,
                    field: str | None = None, *, one: bool = False, **options) -> 'FST':  # -> Self
    """Put a raw slice of child nodes to `self`."""

    if isinstance(code, AST):
        if not one:
            try:
                ast = _reduce_ast(code, 'exprish')
            except Exception:
                pass

            else:
                if isinstance(ast, Tuple):  # strip delimiters because we want CONTENTS of slice for raw put, not the slice object itself
                    code = ast_unparse(ast)[1 : (-2 if len(ast.elts) == 1 else -1)]  # also remove singleton Tuple trailing comma
                elif isinstance(ast, (List, Dict, Set, MatchSequence, MatchMapping)):
                    code = ast_unparse(ast)[1 : -1]

    elif isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root FST')

        try:
            ast = _reduce_ast(code.a, 'exprish')
        except Exception:
            pass

        else:
            fst = ast.f

            if one:
                if (is_par_tup := fst.is_parenthesized_tuple()) is None:  # only need to parenthesize this, others are already enclosed
                    if isinstance(ast, MatchSequence) and not fst._is_parenthesized_seq('patterns'):
                        fst._parenthesize_grouping()

                elif is_par_tup is False:
                    fst._parenthesize_tuple()

            elif ((is_dict := isinstance(ast, Dict)) or
                    (is_match := isinstance(ast, (MatchSequence, MatchMapping))) or
                    isinstance(ast, (Tuple, List, Set))
            ):
                if not ((is_par_tup := fst.is_parenthesized_tuple()) is False or  # don't strip nonexistent delimiters if is unparenthesized Tuple or MatchSequence
                        (is_par_tup is None and isinstance(ast, MatchSequence) and
                            not fst._is_parenthesized_seq('patterns'))
                ):
                    code.put_src(None, end_ln := code.end_ln, (end_col := code.end_col) - 1, end_ln, end_col, True)  # strip enclosing delimiters
                    code.put_src(None, ln := code.ln, col := code.col, ln, col + 1, False)

                if elts := ast.values if is_dict else ast.patterns if is_match else ast.elts:
                    if comma := _next_find(code.root._lines, (l := elts[-1].f.loc).end_ln, l.end_col, code.end_ln,
                                            code.end_col, ','):  # strip trailing comma
                        ln, col = comma

                        code.put_src(None, ln, col, ln, col + 1, False)

    self._reparse_raw_loc(code, *self._raw_slice_loc(start, stop, field))

    return self.repath()


from .fst import FST
