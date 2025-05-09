"""Raw reparse FST methods."""

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


def _raw_slice_loc(self: 'FST', start: int | Literal['end'] | None = None, stop: int | None = None,
                    field: str | None = None) -> fstloc:
    """Get location of a raw slice. Sepcial cases for decorators, comprehension ifs and other weird nodes."""

    def fixup_slice_index_for_raw(len_, start, stop):
        start, stop = _fixup_slice_index(len_, start, stop)

        if stop == start:
            raise ValueError(f"invalid slice for raw operation")

        return start, stop

    ast = self.a

    if isinstance(ast, Dict):
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

        keys        = ast.keys
        values      = ast.values
        start, stop = fixup_slice_index_for_raw(len(keys), start, stop)
        start_loc   = self._dict_key_or_mock_loc(keys[start], values[start].f)

        if start_loc.is_FST:
            start_loc = start_loc.pars()

        return fstloc(start_loc.ln, start_loc.col, *values[stop - 1].f.pars()[2:])

    if isinstance(ast, Compare):
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Compare")

        comparators  = ast.comparators  # virtual combined body of [Compare.left] + Compare.comparators
        start, stop  = fixup_slice_index_for_raw(len(comparators) + 1, start, stop)
        stop        -= 1

        return fstloc(*(comparators[start - 1] if start else ast.left).f.pars()[:2],
                        *(comparators[stop - 1] if stop else ast.left).f.pars()[2:])

    if isinstance(ast, MatchMapping):
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a MatchMapping")

        keys        = ast.keys
        start, stop = fixup_slice_index_for_raw(len(keys), start, stop)

        return fstloc(*keys[start].f.loc[:2], *ast.patterns[stop - 1].f.pars()[2:])

    if isinstance(ast, comprehension):
        ifs         = ast.ifs
        start, stop = fixup_slice_index_for_raw(len(ifs), start, stop)
        ffirst      = ifs[start].f
        start_pos   = _prev_find(self.root._lines, *ffirst._prev_ast_bound(), ffirst.ln, ffirst.col, 'if')

        return fstloc(*start_pos, *ifs[stop - 1].f.pars()[2:])

    if field == 'decorator_list':
        decos       = ast.decorator_list
        start, stop = fixup_slice_index_for_raw(len(decos), start, stop)
        ffirst      = decos[start].f
        start_pos   = _prev_find(self.root._lines, 0, 0, ffirst.ln, ffirst.col, '@')  # we can use '0, 0' because we know "@" starts on a newline

        return fstloc(*start_pos, *decos[stop - 1].f.pars()[2:])

    _, body     = _fixup_field_body(ast, field)
    start, stop = fixup_slice_index_for_raw(len(body), start, stop)

    return fstloc(*body[start].f.pars(exc_genexpr_solo=True)[:2],
                    *body[stop - 1].f.pars(exc_genexpr_solo=True)[2:])

def _reparse_raw(self: 'FST', new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
                        copy_lines: list[str], path: list[astfield] | str, set_ast: bool = True) -> 'FST':
    """Actually do the reparse."""

    copy_root = FST(Pass(), lines=copy_lines)  # we don't need the ASTs here, just the lines

    copy_root.put_src(new_lines, ln, col, end_ln, end_col)

    root      = self.root
    copy_root = FST.fromsrc(copy_root.src, mode=get_parse_mode(root.a) or 'exec', **root.parse_params)

    if path == 'root':
        self._lines = copy_root._lines
        copy        = copy_root

    else:
        copy = copy_root.child_from_path(path)

        if not copy:
            raise RuntimeError(f'could not find node after raw reparse')

        root.put_src(new_lines, ln, col, end_ln, end_col, True, self if set_ast else None)  # we do this again in our own tree to offset our nodes which aren't being moved over from the modified copy, can exclude self if setting ast because it overrides self locations

        copy.pfield.set(copy.parent.a, None)  # remove from copy tree so that copy_root unmake doesn't zero out new node
        copy_root._unmake_fst_tree()

    if set_ast:
        self._set_ast(copy.a)
        self.touch(True)

    return copy

def _reparse_raw_stmtish(self: 'FST', new_lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> bool:
    """Reparse only statementish or block opener part of statementish containing changes."""

    if not (stmtish := self.parent_stmtish(True, False)):
        return False

    pln, pcol, pend_ln, pend_col = stmtish.bloc

    root     = self.root
    lines    = root._lines
    stmtisha = stmtish.a

    if in_blkopen := (blkopen_end := stmtish._loc_block_opener_end()) and (end_ln, end_col) <= blkopen_end:  # block statement with modification limited to block opener
        pend_ln, pend_col = blkopen_end

    if isinstance(stmtisha, match_case):
        copy_lines = ([bistr('')] * (pln - 1) +
                        [bistr('match a:'), bistr(' ' * pcol + lines[pln][pcol:])] +
                        lines[pln + 1 : pend_ln + 1])
        path       = PATH_BODYCASES

    else:
        indent = stmtish.get_indent()

        if not indent:
            copy_lines = [bistr('')] * pln + lines[pln : pend_ln + 1]

        elif pln:
            copy_lines = ([bistr('if 1:')] +
                            [bistr('')] * (pln - 1) +
                            [bistr(' ' * pcol + lines[pln][pcol:])] +
                            lines[pln + 1 : pend_ln + 1])
        else:
            copy_lines = ([bistr(f"try:{' ' * (pcol - 4)}{lines[pln][pcol:]}")] +
                            lines[pln + 1 : pend_ln + 1] +
                            [bistr('finally: pass')])

        if isinstance(stmtisha, ExceptHandler):
            assert pln > bool(indent)

            copy_lines[pln - 1] = bistr(indent + 'try: pass')
            path                = PATH_BODY2HANDLERS if indent else PATH_BODYHANDLERS

        elif not indent:
            if stmtish.is_elif():
                copy_lines[0] = bistr('if 2: pass')
                path          = PATH_BODYORELSE
            else:
                path = PATH_BODY

        else:
            if stmtish.is_elif():
                copy_lines[1] = bistr(indent + 'if 2: pass')
                path          = PATH_BODY2ORELSE
            else:
                path = PATH_BODY2

    if not in_blkopen:  # non-block statement or modifications not limited to block opener part
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

        stmtish._reparse_raw(new_lines, ln, col, end_ln, end_col, copy_lines, path)

        return True

    # modifications only to block opener line(s) of block statement

    if isinstance(stmtisha, Match):
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col])

        copy_lines.append(bistr(indent + ' case 1: pass'))

    else:
        copy_lines[pend_ln] = bistr(copy_lines[pend_ln][:pend_col] + ' pass')

        if isinstance(stmtisha, (Try, TryStar)):  # this one is just silly, nothing to put there, but we cover it
            copy_lines.append(bistr(indent + 'finally: pass'))

    copy  = stmtish._reparse_raw(new_lines, ln, col, end_ln, end_col, copy_lines, path, False)
    copya = copy.a

    if not isinstance(stmtisha, match_case):  # match_case doesn't have AST location
        copya.end_lineno     = stmtisha.end_lineno
        copya.end_col_offset = stmtisha.end_col_offset

    for field in STATEMENTISH_FIELDS:
        if (body := getattr(stmtisha, field, None)) is not None:
            setattr(copya, field, body)

    stmtish._set_ast(copya)
    stmtish.touch(True)

    return True

def _reparse_raw_loc(self: 'FST', code: Code | None, ln: int, col: int, end_ln: int, end_col: int,
                        exact: bool | None = None) -> Optional['FST']:
    """Reparse this node which entirely contatins the span which is to be replaced with `code` source. `self` must
    be a node which entirely contains the location and is guaranteed not to be deleted. `self` and some of its
    parents going up may be replaced (root node `FST` will never change, the `AST` it points to may though). Not
    safe to use in a `walk()`.

    **Returns:**
    - `FST | None`: FIRST highest level node contained entirely within replacement source or `None` if no candidate.
        This could wind up being just an operator like '+' depending on the replacement. If `exact` is passed and
        not `None` then will attempt a `find_loc(..., exact)` if could not find candidate node with `find_in_loc()`.
    """

    if isinstance(code, str):
        new_lines = code.split('\n')
    elif isinstance(code, list):
        new_lines = code
    elif isinstance(code, AST):
        new_lines = ast_unparse(code).split('\n')
    elif code is None:
        new_lines = [bistr('')]
    elif not code.is_root:  # isinstance(code, FST)
        raise ValueError('expecting root FST')
    else:
        new_lines = code._lines

    if not self._reparse_raw_stmtish(new_lines, ln, col, end_ln, end_col):  # attempt to reparse only statement (or even only block opener)
        assert self.root.is_mod  # TODO: allow with non-mod root

        root = self.root

        self._reparse_raw(new_lines, ln, col, end_ln, end_col, root._lines[:],  # fallback to reparse all source
                            'root' if self is root else root.child_path(self))

    if code is None:
        return None

    if len(new_lines) == 1:
        end_ln  = ln
        end_col = col + len(new_lines[0])

    else:
        end_ln  = ln + len(new_lines) - 1
        end_col = len(new_lines[-1])

    return (self.root.find_in_loc(ln, col, end_ln, end_col) or  # `self.root` instead of `self` because some changes may propagate farther up the tree, like 'elif' -> 'else'
            (self.root.find_loc(ln, col, end_ln, end_col, exact) if exact is not None else None))

def _reparse_raw_node(self: 'FST', code: Code | None, to: Optional['FST'] = None, **options) -> 'FST':
    """Attempt a replacement by using str as source and attempting to parse into location of node(s) being
    replaced."""

    multi = to and to is not self
    pars  = True if multi else bool(FST.get_option('pars', options))
    loc   = self.pars(pars, exc_genexpr_solo=True)  # we don't check for unparenthesized Tuple code FST here because if it is then will just be parsed into a Tuple anyway

    if not loc:
        raise ValueError('node being reparsed must have a location')


    # TODO: allow all options for removing comments and space, not just pars


    if not multi:
        if not (parent := self.parent):  # we want parent which will not change or root node
            parent = self

        else:  # the checks below require a parent and don't make sense if there isn't one
            if isinstance(self.a, PARENTHESIZABLE):
                if isinstance(code, AST):
                    if pars and isinstance(code, PARENTHESIZABLE):
                        if not (is_atom_ := is_atom(code, tuple_as_atom=None)):
                            if precedence_require_parens(code, parent.a, *self.pfield):
                                code = ast_unparse(code) if is_atom_ is None else f'({ast_unparse(code)})'
                            elif is_atom_ is None:  # strip `unparse()` parens
                                code = ast_unparse(code)[1:-1]

                elif isinstance(code, FST):
                    if isinstance(a := code.a, (Module, Interactive)):
                        a = a.body[0] if len(a.body) == 1 else None
                    elif isinstance(a, Expression):
                        a = a.body

                    if isinstance(a, Expr):
                        a = a.value

                    if isinstance(a, PARENTHESIZABLE):
                        effpars = pars or a.f.is_parenthesized_tuple() is False
                        loc     = self.pars(effpars, exc_genexpr_solo=True)  # TODO: need to redo here with new `a`, should refactor to avoid this

                        if precedence_require_parens(a, parent.a, *self.pfield):
                            if not a.f.is_atom() and (effpars or not self.pars(ret_npars=True)[1]):
                                a.f.parenthesize()

                        elif pars:  # remove parens only if allowed to
                            a.f.unparenthesize()

                        code = code._lines

            if (pars or not self.is_solo_call_arg_genexpr() or  # if original loc included `arguments` parentheses shared with solo GeneratorExp call arg then need to leave those in place
                (to_loc := self.pars(True, exc_genexpr_solo=True))[:2] <= loc[:2]
            ):
                to_loc = loc
            else:
                loc = to_loc

        # elif pars:  # precedence parenthesizing
        #     if isinstance(code, FST):
        #         if not code.is_atom() and precedence_require_parens(code.a, parent.a, *self.pfield):
        #             code.parenthesize()

        #     elif isinstance(code, AST):
        #         if not (is_atom_ := is_atom(code, tuple_as_atom=None)):
        #             if precedence_require_parens(code, parent.a, *self.pfield):
        #                 code = ast_unparse(code) if is_atom_ is None else f'({ast_unparse(code)})'
        #             elif is_atom_ is None:  # strip `unparse()` parens
        #                 code = ast_unparse(code)[1:-1]

        if (pars or not self.is_solo_call_arg_genexpr() or  # if original loc included `arguments` parentheses shared with solo GeneratorExp call arg then need to leave those in place
            (to_loc := self.pars(True, exc_genexpr_solo=True))[:2] <= loc[:2]
        ):
            to_loc = loc
        else:
            loc = to_loc

    elif not (to_loc := to.pars(pars, exc_genexpr_solo=True)):  # pars is True here
        raise ValueError(f"'to' node must have a location")
    elif (root := self.root) is not to.root:
        raise ValueError(f"'to' node not part of same tree")
    elif to_loc[:2] < loc[:2]:
        raise ValueError(f"'to' node must follow self")

    else:
        self_path = root.child_path(self)[:-1]  # [:-1] makes sure we get parent of whatever combination of paths
        to_path   = root.child_path(to)[:-1]
        path      = list(p for p, _ in takewhile(lambda st: st[0] == st[1], zip(self_path, to_path)))
        parent    = root.child_from_path(path)

    return parent._reparse_raw_loc(code, loc.ln, loc.col, to_loc.end_ln, to_loc.end_col)


from .fst import FST
