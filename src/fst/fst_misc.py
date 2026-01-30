"""Misc common `FST` class and standalone methods.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import os
import re
import sys
from ast import iter_fields, walk
from math import log10
from pprint import pformat
from typing import Any, Literal, Mapping

from . import fst

from .asttypes import (
    ASTS_LEAF_EXPR,
    ASTS_LEAF_STMTLIKE,
    ASTS_LEAF_BLOCK,
    ASTS_LEAF_TUPLE_LIST_OR_SET,
    ASTS_LEAF_DELIMITED,
    AST,
    AnnAssign,
    Assert,
    Assign,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    Attribute,
    AugAssign,
    Await,
    BinOp,
    BoolOp,
    Call,
    ClassDef,
    Compare,
    Constant,
    Delete,
    Dict,
    ExceptHandler,
    Expr,
    Expression,
    For,
    FormattedValue,
    FunctionDef,
    GeneratorExp,
    Global,
    If,
    Import,
    ImportFrom,
    Interactive,
    JoinedStr,
    Lambda,
    List,
    ListComp,
    Load,
    Match,
    MatchAs,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    MatchSingleton,
    MatchValue,
    Module,
    Name,
    NamedExpr,
    Nonlocal,
    Raise,
    Return,
    Set,
    SetComp,
    Slice,
    Starred,
    Subscript,
    Try,
    Tuple,
    UnaryOp,
    While,
    With,
    Yield,
    YieldFrom,
    alias,
    arg,
    arguments,
    comprehension,
    keyword,
    match_case,
    mod,
    stmt,
    withitem,
    TryStar,
    TypeAlias,
    TemplateStr,
    Interpolation,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _arglikes,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from .astutil import (
    ARGLIKE_KIND_NAME,
    pat_alnum,
    constant,
    re_alnumdot_alnum,
    bistr,
    precedence_require_parens_by_type,
    arglike_kind,
    merge_arglikes,
)

from .common import (
    NodeError,
    srcwpos,
    nspace,
    re_empty_line,
    re_comment_line_start,
    re_empty_space,
    re_empty_line_or_cont,
    re_empty_line_cont_or_comment,
    re_line_end_cont_or_comment,
    re_line_end_ws_cont_or_comment,
    next_frag,
    next_find,
    prev_find,
    next_delims,
)

__all__ = [
    'new_empty_set_star',
    'new_empty_set_call',
    'new_empty_set_curlies',
    'leading_trivia',
    'trailing_trivia',
    'get_trivia_params',
    'clip_src_loc',
    'fixup_one_index',
    'fixup_slice_indices',
    'fixup_field_body',
    'validate_put_arglike',
]


try:
    from IPython import get_ipython
    IPYTHON_COLOR = getattr(get_ipython(), 'colors', 'NoColor') != 'NoColor'  # pragma: no cover
except Exception:  # pragma: no cover
    IPYTHON_COLOR = False

DEFAULT_COLOR = (
    False if os.environ.get("NO_COLOR") else
    True if os.environ.get("FORCE_COLOR") else
    False if (os.environ.get("TERM") == "dumb" or sys.platform == "win32") else
    None
)

DUMP_COLOR = nspace(
    clr_field = '\033[95m',
    clr_ast   = '\033[1;34m',
    clr_loc   = '\033[90m',
    clr_src   = '',
    end_field = '\033[0m',
    end_ast   = '\033[0m',
    end_loc   = '\033[0m',
    end_src   = '',
    type      = {
        type(...):  ('\033[1;36m', '\033[0m'),
        type(None): ('\033[1;36m', '\033[0m'),
        bool:       ('\033[1;36m', '\033[0m'),
        int:        ('\033[33m', '\033[0m'),
        float:      ('\033[33m', '\033[0m'),
        complex:    ('\033[33m', '\033[0m'),
        str:        ('\033[32m', '\033[0m'),
        bytes:      ('\033[32m', '\033[0m'),
    },
)

DUMP_NO_COLOR = nspace(
    clr_field = '',
    clr_ast   = '',
    clr_loc   = '',
    clr_src   = '',
    end_field = '',
    end_ast   = '',
    end_loc   = '',
    end_src   = '',
    type      = {
        type(...):  ('', ''),
        type(None): ('', ''),
        bool:       ('', ''),
        int:        ('', ''),
        float:      ('', ''),
        complex:    ('', ''),
        str:        ('', ''),
        bytes:      ('', ''),
    },
)

_Trivia = tuple[bool | str | int, bool | str | int]  # actual value trivia that is used, regardless of what is passed or set as global option
Trivia  = bool | str | int | tuple[bool | str | int | None, bool | str | int | None] | None  # human interface trivia parameter as passed to functions with None indicating to use global value

_DEFAULT_AST_FIELD = {kls: field for field, classes in [  # builds to {Module: 'body', Interactive: 'body', ..., Match: 'cases', ..., MatchAs: 'pattern'}
    # list fields of multiple children
    ('body',                  (Module, Interactive, Expression, FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While,
                               If, With, AsyncWith, Try, TryStar, ExceptHandler, Lambda, match_case),),
    ('handlers',              (_ExceptHandlers,)),
    ('cases',                 (Match, _match_cases)),

    ('elts',                  (Tuple, List, Set)),
    ('targets',               (Delete, _Assign_targets)),
    ('decorator_list',        (_decorator_list,)),
    ('arglikes',              (_arglikes,)),
    ('patterns',              (MatchSequence, MatchOr, MatchClass)),
    ('type_params',           (TypeAlias, _type_params)),
    ('names',                 (Import, ImportFrom, Global, Nonlocal, _aliases)),
    ('items',                 (_withitems,)),
    ('values',                (BoolOp, JoinedStr, TemplateStr)),
    ('generators',            (_comprehensions,)),
    ('ifs',                   (_comprehension_ifs,)),

    # virtual fields
    ('_all',                  (Dict,)),          # key:value
    ('_all',                  (MatchMapping,)),  # key:pattern,rest?
    ('_all',                  (Compare,)),       # left,op:comparator
    ('_args',                 (Call,)),          # args,keywords
    ('_all',                  (arguments,)),     # posonlyargs=defaults,args=defaults,vararg,kwolyargs=kw_defaults,kwarg

    # single value fields
    ('value',                 (Expr, Return, Assign, TypeAlias, AugAssign, AnnAssign, NamedExpr, Await, Yield, YieldFrom,
                               FormattedValue, Interpolation, Constant, Attribute, Subscript, Starred, keyword, MatchValue,
                               MatchSingleton)),
    ('elt',                   (GeneratorExp, ListComp, SetComp)),
    ('target',                (comprehension,)),
    ('exc',                   (Raise,)),
    ('test',                  (Assert,)),
    ('operand',               (UnaryOp,)),
    ('id',                    (Name,)),
    ('arg',                   (arg,)),
    ('name',                  (alias,)),
    ('context_expr',          (withitem,)),
    ('pattern',               (MatchAs,)),
] for kls in classes}

_ASTS_LEAF_TUPLE_OR_MATCHSEQ = frozenset([Tuple, MatchSequence])

_re_dump_line_tail     = re.compile(r'\s* ( \#.*$ | \\$ | ; (?: \s* (?: \#.*$ | \\$ ) )? )', re.VERBOSE)
_re_one_space_or_end   = re.compile(r'\s|$')

_re_par_open_alnums    = re.compile(rf'[{pat_alnum}.][(][{pat_alnum}]')
_re_par_close_alnums   = re.compile(rf'[{pat_alnum}.][)][{pat_alnum}]')
_re_delim_open_alnums  = re.compile(rf'[{pat_alnum}.][({{[][{pat_alnum}]')
_re_delim_close_alnums = re.compile(rf'[{pat_alnum}.][)}}\]][{pat_alnum}]')

_re_stmt_line_comment  = re.compile(r'(\s*;)?(\s*\#(.*)$)?')  # a line comment with optional leading whitespace and maybe a single inert semicolon before, or indicate if there is a trailing semicolon

_re_line_end_ws_maybe_cont = re.compile(r'\s*\\?$')


def _dump_lines(
    fst_: fst.FST,
    st: nspace,
    ln: int,
    col: int,
    end_ln: int,
    end_col: int,
    is_stmt: bool | None,
) -> None:
    """Dump one or more lines of source. `is_stmt=None` specifies end put of just lines, no nodes."""

    linefunc = st.linefunc
    eol = st.eol
    c = st.color
    lines = fst_.root._lines
    width = int(log10(len(lines) - 1 or 1)) + 1

    if (src_ln := st.src_ln) <= ln:  # if 'stmt+' or 'node+' putting them then put any lines after last put end line and before this put start line
        if src_ln < ln:
            for cln in range(src_ln, ln):
                l = lines[cln]
                e = f'{c.clr_loc}<*END*{c.end_loc}' if l[-1:].isspace() else ''

                if e or l:
                    linefunc(f'{c.clr_loc}{cln:<{width}}:{c.end_loc} {c.clr_src}{l}{c.end_src}{e}{eol}')
                else:
                    linefunc(f'{c.clr_loc}{cln:<{width}}:{c.end_loc}{eol}')

        st.line_tails_dumped.update(range(src_ln, end_ln))

        st.src_ln = end_ln + 1

    if is_stmt is None:  # we just wanted to put trailing lines so we are done
        return

    if not is_stmt and (src_ln >= 0x7fffffffffffffff or end_ln in st.line_tails_dumped):  # not src+ or end line tail already dumped
        lines = fst_._get_src(ln, col, end_ln, end_col, True)

    else:  # src+ and fresh line to possibly dump tail
        st.line_tails_dumped.add(end_ln)

        lines = fst_._get_src(ln, col, end_ln, 0x7fffffffffffffff, True)

        ec = end_col if end_ln != ln else end_col - col

        if m := _re_dump_line_tail.match(l := lines[-1], ec):
            lines[-1] = l[:m.end(1)]
        else:
            lines[-1] = l[:ec]

    end = f'{c.clr_loc}<*END*{c.end_loc}'
    iter_lines = iter(lines)
    l = ol = next(iter_lines)
    e = end if (not l and col) or l[-1:].isspace() else ''

    if not col:
        l = f'{c.end_loc}{c.clr_src}{l}{c.end_src}'
    elif l[:1].isspace():
        l = f'{"-" * (col - 1)}>{c.end_loc}{c.clr_src}{l}{c.end_src}'
    else:
        l = f'{" " * col}{c.end_loc}{c.clr_src}{l}{c.end_src}'

    if e or ol:
        linefunc(f'{c.clr_loc}{ln:<{width}}: {l}{e}{eol}')
    else:
        linefunc(f'{c.clr_loc}{ln:<{width}}:{eol}')

    for cln, l in zip(range(ln + 1, end_ln + 1), iter_lines, strict=True):
        e = end if l[-1:].isspace() else ''

        if e or l:
            linefunc(f'{c.clr_loc}{cln:<{width}}:{c.end_loc} {c.clr_src}{l}{c.end_src}{e}{eol}')
        else:
            linefunc(f'{c.clr_loc}{cln:<{width}}:{c.end_loc}{eol}')


def _dump_prim(prim: constant, c: nspace) -> str:
    """Dump primitive."""

    clr_type, end_type = c.type.get(prim.__class__, ('', ''))

    return f'{clr_type}{prim!r}{end_type}'


def _dump_prim_long(prim: constant, st: nspace, cind: str) -> str:
    """Dump primitive potentially long primitive (str or bytes)."""

    prim_cls = prim.__class__
    clr_type, end_type = st.color.type.get(prim_cls, ('', ''))

    if ((prim_cls is not str and prim_cls is not bytes)
        or len(prim) < 120
        or not (fmt := pformat(prim, width=120)).startswith('(')
    ):
        return f'{clr_type}{prim!r}{end_type}'

    fmt = fmt[1:-1].replace('\n ', f'\n{cind}')  # remove parentheses, dedent by opening par 1 column

    if st.expand:
        return f'{clr_type}{fmt}{end_type}'
    else:
        return f'\n{cind}{clr_type}{fmt}{end_type}'


def _dump_node(self: fst.FST, st: nspace, cind: str, prefix: str) -> None:
    ast = self.a
    ast_cls = ast.__class__
    sind = st.sind
    c = st.color
    tail = self._repr_tail(st.loc)
    tail = f' {c.clr_loc}-{tail}{c.end_loc}' if tail else ''

    if not st.src:  # noop
        pass

    elif isinstance(ast, (stmt, ExceptHandler, match_case)):  # src = 'stmt' or 'node'
        loc = self.bloc

        if ast_cls in ASTS_LEAF_BLOCK:
            ln, col, _, _ = loc
            _, _, end_ln, end_col = self._loc_block_header_end()

            _dump_lines(self, st, ln, col, end_ln, end_col, True)

        else:
            _dump_lines(self, st, *loc, True)

    elif not isinstance(ast, (mod, _ExceptHandlers, _match_cases)):
        if st.src == 'node':
            if not (parent := self.parent) or parent.a.__class__ is not Expr:
                if loc := self.loc:
                    _dump_lines(self, st, *loc, False)

        elif st.src == 'stmt' and not self.parent:  # if putting statements but root is not statement or mod then just put root src and no src below
            st.src = None

            if loc := self.loc:
                _dump_lines(self, st, *loc, False)

    if not st.expand:
        if ast_cls is Name:
            st.linefunc(f'{cind}{prefix}{c.clr_ast}Name{c.end_ast} {_dump_prim(ast.id, c)} '
                        f'{c.clr_ast}{ast.ctx.__class__.__name__}{c.end_ast}{tail}{st.eol}')

            return

        if ast_cls is Constant:
            kind = '' if ast.kind is None else f' {c.clr_field}.kind{c.end_field} {_dump_prim(ast.kind, c)}'
            prim = _dump_prim_long(ast.value, st, cind + sind)

            if prim.startswith('\n'):
                prim = f'{cind}{prefix}{c.clr_ast}Constant{c.end_ast}{kind}{tail}{prim}'
            else:
                prim = f'{cind}{prefix}{c.clr_ast}Constant{c.end_ast} {prim}{kind}{tail}'

            for l in prim.split('\n'):
                st.linefunc(f'{l}{st.eol}')

            return

        if ast_cls is MatchSingleton:
            st.linefunc(f'{cind}{prefix}{c.clr_ast}MatchSingleton{c.end_ast} {_dump_prim(ast.value, c)}'
                        f'{tail}{st.eol}')

            return

    st.linefunc(f'{cind}{prefix}{c.clr_ast}{ast_cls.__name__}{c.end_ast}{tail}{st.eol}')

    for name, child in iter_fields(ast):
        is_list = isinstance(child, list)

        if (is_list and child and st.src
            and (
                name == 'finalbody'
                or (name == 'orelse' and not child[0].f.is_elif())
        )):  # non-empty 'else' (not 'elif') or 'finally' block with source output turned on?
            ln, col, end_ln, end_col = self._loc_block_header_end(name)

            _dump_lines(self, st, ln, col, end_ln, end_col, True)  # dump 'else:' or 'finally:'

        if not st.expand:
            if not st.full and child is None and ast_cls is not MatchSingleton:
                continue

            if name == 'ctx':
                st.linefunc(f'{cind}{sind}{c.clr_field}.{name}{c.end_field} '
                            f'{c.clr_ast}{child.__class__.__name__}{c.end_ast}{st.eol}')

                continue

            if (name in ('type', 'id', 'attr', 'module', 'arg', 'vararg', 'kwarg', 'rest', 'format_spec',
                         'name', 'asname', 'value', 'left', 'right', 'operand', 'returns', 'target',
                         'annotation', 'iter', 'test', 'exc', 'cause', 'msg', 'elt', 'key', 'func',
                         'slice', 'lower', 'upper', 'step', 'guard', 'context_expr', 'optional_vars',
                         'cls', 'bound', 'default_value', 'pattern', 'subject',
                         'type_comment', 'lineno', 'tag', 'op',
                         'simple', 'level', 'conversion', 'str', 'is_async', 'lineno') or
                (not is_list and name in ('body', 'orelse'))
            ):
                if isinstance(child, AST):
                    _dump_node(child.f, st, cind + sind, f'{c.clr_field}.{name}{c.end_field} ')
                else:
                    st.linefunc(f'{cind}{sind}{c.clr_field}.{name}{c.end_field} {_dump_prim(child, c)}{st.eol}')

                continue

            if name == 'args' and child.__class__ is arguments:
                if child.posonlyargs or child.args or child.vararg or child.kwonlyargs or child.kwarg or st.full:
                    _dump_node(child.f, st, cind + sind, f'{c.clr_field}.args{c.end_field} ')

                    continue

                elif not st.full:
                    continue

        if (not st.full
            and (
                child == []
                or (
                    child is None
                    and not (
                        name == 'value'
                        and ast_cls in (Constant, MatchSingleton))))):
            continue

        if not is_list:
            st.linefunc(f'{cind}{sind}{c.clr_field}.{name}{c.end_field}{st.eol}')

            if isinstance(child, AST):
                _dump_node(child.f, st, cind + sind * 2, '')

            else:
                ind = f'{cind}{sind * 2}'
                prim = f'{ind}{_dump_prim_long(child, st, ind)}'

                for l in prim.split('\n'):
                    st.linefunc(f'{l}{st.eol}')

        # elif len(child) == 1:  # length 1 lists show element on single line
        #     if isinstance(ast := child[0], AST):
        #         _dump_node(ast.f, st, cind + sind, f'{c.clr_field}.{name}[1]{c.end_field} ')
        #     else:
        #         st.linefunc(f'{cind}{c.clr_field}.{name}[1]{c.end_field} {ast!r}{st.eol}')

        else:
            st.linefunc(f'{cind}{sind}{c.clr_field}.{name}[{len(child)}]{c.end_field}{st.eol}')

            for i, ast in enumerate(child):
                if isinstance(ast, AST):
                    _dump_node(ast.f, st, cind + st.lind, f'{c.clr_field}{i}]{c.end_field} ')
                else:
                    st.linefunc(f'{cind}{st.lind}{c.clr_field}{i}]{c.end_field} {_dump_prim(ast, c)}{st.eol}')


# ----------------------------------------------------------------------------------------------------------------------

def new_empty_set_star(
    lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None, as_fst: bool = True
) -> fst.FST | AST:
    lines = ['{*()}']
    ast = Set(elts=[Starred(value=Tuple(elts=[], ctx=Load(), lineno=lineno, col_offset=col_offset+2,
                                        end_lineno=lineno, end_col_offset=col_offset+4),
                            ctx=Load(),
                            lineno=lineno, col_offset=col_offset+1, end_lineno=lineno, end_col_offset=col_offset+4)],
              lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return fst.FST(ast, lines, None, from_=from_) if as_fst else (ast, lines)


def new_empty_set_call(
    lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None, as_fst: bool = True
) -> fst.FST:
    lines = ['set()']
    ast = Call(func=Name(id='set', ctx=Load(),
                         lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+3),
               args=[], keywords=[],
               lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return fst.FST(ast, lines, None, from_=from_) if as_fst else (ast, lines)


def new_empty_set_curlies(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None) -> fst.FST | AST:
    ast = Set(elts=[], lineno=lineno, col_offset=col_offset, end_lineno=lineno,
              end_col_offset=col_offset + 2)

    return fst.FST(ast, ['{}'], None, from_=from_)


def leading_trivia(
    lines: list[str],
    bound_ln: int,
    bound_col: int,
    ln: int,
    col: int,
    comments: Literal['none', 'all', 'block'] | int,
    space: bool | int,
) -> tuple[tuple[int, int], tuple[int, int] | None, str | None]:
    """Get locations of leading trivia starting at the given bound up to (`ln`, `col`) where the element starts. Can get
    location of a block of comments (no spaces between), all comments after start of bound (with spaces inside) and any
    leading empty lines. Also returns the indentation of the element line if it starts the line.

    Regardless of if no comments or space is requested, this function will always return whether the element starts the
    line or not and the indentation if so.

    **Parameters:**
    - `bound_ln`: Preceding bounding line, other code assumed to end just here.
    - `bound_col`: Preceding bounding column.
    - `ln`: The start line of our element from which we will search back and upwards.
    - `col`: The start column of our element.
    - `comments`: What kind of comments to check for.
        - `'none'`: No comments.
        - `'all'`: A range of not-necessarily contiguous comments between the bound and the start of the element, will
            return location of start of comments.
        - `'block'`: A single contiguous block of comments immediately above the element.
        - `int`: An integer specifies return from this line number if possible. Possible means there are only comments
            and / or empty lined between this line and the start of the element. Any extra empty space to return will be
            searched for from this location, regardless of if there is other empty space below.
    - `space`: How much preceding space to check for, will be returned as a separate location if present.
        - `int`: Integer specifies maximum number of empty lines to return.
        - `False`: Same as `0` which will not check for or return any empty space.
        - `True`: Check all the way up to start of bound and return as much empty space as possible.

    **Returns:**
    - (comment / element text start, space start, indent on element line): Leading trivia info:
        - `[0]`: The start line and column of the first block of comments or the element. The column will be 0 if this
            starts a new line.
        - `[1]`: The start line and column (always 0) of any leading block of empty lines.
        - `[2]`: The indentation of the element line if it starts its own line (and may or may not have preceding
            comments and / or empty space). An empty string indicates the element starts the line at column 0 and `None`
            indicates the element doesn't start the line.

    @private
    """

    assert bound_ln <= ln

    if (bound_ln == ln and bound_col) or not re_empty_line.match(l := lines[ln], 0, col):
        return ((ln, col), None, None)

    indent = l[:col]
    is_lineno = isinstance(comments, int)
    text_pos = (ln, col)  # start of comments or start of element
    top_ln = bound_ln + bool(bound_col)  # topmost possible line to be considered, min return location is (top_ln, 0)
    stop_ln = comments if is_lineno and comments > top_ln else top_ln
    start_ln = ln

    if comments == 'all':
        comments_ln = ln

        while (ln := ln - 1) >= stop_ln:
            if not (m := re_empty_line_cont_or_comment.match(lines[ln])):
                break

            if (g := m.group(1)) and g.startswith('#'):
                comments_ln = ln

        ln += 1
        comments_pos = (comments_ln, 0)

        if comments_ln != start_ln:
            text_pos = comments_pos

        if not space or comments_ln == ln:  # no space requested or we reached top of search or non-comment/empty line right before comment
            return (text_pos, None if comments_pos == text_pos else comments_pos, indent)

        # space requested and there are some empty lines before first comment

        if space is True:
            return (text_pos, (ln, 0), indent)  # infinite space requested so return everything we got

        return (text_pos, (comments_ln - min(space, comments_ln - ln), 0), indent)

    if comments != 'none':
        assert is_lineno or comments == 'block'

        re_pat = re_empty_line_cont_or_comment if is_lineno else re_comment_line_start

        while (ln := ln - 1) >= stop_ln:
            if not (m := re_pat.match(lines[ln])):
                break

        comments_pos = (comments_ln := ln + 1, 0)

        if comments_ln != start_ln:
            text_pos = comments_pos

    else:
        comments_pos = (comments_ln := ln, 0)

    if not space or comments_ln == top_ln:
        return (text_pos, None if comments_pos == text_pos else comments_pos, indent)

    for ln in range(comments_ln - 1, max(top_ln - 1, -1 if space is True else comments_ln - 1 - space), -1):
        if not re_empty_line_or_cont.match(lines[ln]):
            ln += 1

            break

    if ln == comments_ln:
        return (text_pos, None if comments_pos == text_pos else comments_pos, indent)

    return (text_pos, (ln, 0), indent)


def trailing_trivia(
    lines: list[str],
    bound_end_ln: int,
    bound_end_col: int,
    end_ln: int,
    end_col: int,
    comments: Literal['none', 'all', 'block', 'line'] | int,
    space: bool | int,
) -> tuple[tuple[int, int], tuple[int, int] | None, bool]:
    """Get locations of trailing trivia starting at the element up to (`end_ln`, `end_col`) where the given bound ends.
    Can get location of a block of comments (no spaces between), all comments after start of bound (with spaces inside),
    a single comment on the ending line and any trailing empty lines. Also returns whether the element ends the line or
    not.

    Regardless of if no comments or space is requested, this function will always return whether the element ends the
    line or not.

    A trailing line continuation on any line is considered empty space.

    If `bound_end_ln == end_ln` then the element can never end the line, even if the bound is at the end of the line.

    If a line number is passed for `comment` then this is the last line that will be CONSIDERED and the end location CAN
    be on the next line if this line is an allowed comment or empty.

    If the end bound is at the end of a line then that line can be considered and the location returned can be the end
    bound and even if on first line it can be marked as ending the line (even though there may be no next line at EOF).
    This may make some returned locations not start at column 0 even if it is a complete line, especially at the end of
    source without a trailing newline.

    **Parameters:**
    - `bound_end_ln`: Trailing bounding line, other code assumed to start just here.
    - `bound_end_col`: Trailing bounding column.
    - `end_ln`: The end line of our element from which we will search forward and downward.
    - `end_col`: The end column of our element.
    - `comments`: What kind of comments to check for.
        - `'none'`: No comments.
        - `'all'`: A range of not-necessarily contiguous comments between the element and the bound, will return
            location of line just past end of comments.
        - `'block'`: A single contiguous block of comments immediately below the element.
        - `'line'`: Only a possible comment on the element line. If present returns start of next line.
        - `int`: An integer specifies return to this line number if possible. Possible means there are only comments
            and / or empty lined between the end of the element and this line (inclusive). Any extra empty space to
            return will be searched for from this location, regardless of if there is other empty space above.
    - `space`: How much trailing space to check for, will be returned as a separate location if present.
        - `int`: Integer specifies maximum number of empty lines to return.
        - `False`: Same as `0` which will not check for or return any empty space.
        - `True`: Check all the way up to end of bound and return as much empty space as possible.

    **Returns:**
    - (comment / element end, space end, whether the element ends the line or not): Trailing trivia info:
        - `[0]`: The end line and column of the last block of comments or the element. The column will be 0 if this
            ends a line.
        - `[1]`: The end line and column (always 0) of any trailing block of empty lines. If the element does not end
            its then this will be on the same line as the element end and will be the end of the space after the element
            if any, otherwise `None`.
        - `[2]`: Whether the element ends its line or not, NOT whether the last line found ends ITS line. If it ends the
            line then the first location will most likely have a column 0 and the returned line number will be after the
            element `end_ln`. But not always if the end bound was at the end of a line like can happen at the end of
            source if it doesn't have a trailing newline.

    @private
    """

    assert bound_end_ln >= end_ln

    if bound_end_ln == end_ln:
        assert bound_end_col >= end_col

        len_line = len(lines[end_ln])

        if not (frag := next_frag(lines, end_ln, end_col, end_ln, bound_end_col, True)):
            space_col = min(bound_end_col, len_line)
        elif comments == 'none' or not frag.src.startswith('#'):
            space_col = frag.col
        else:
            return ((end_ln, len_line), None, True)

        return ((end_ln, end_col), None if space_col == end_col else (end_ln, space_col), space_col == len_line)

    is_lineno = isinstance(comments, int)

    if frag := next_frag(lines, end_ln, end_col, end_ln + 1, 0, True):
        if not frag.src.startswith('#') or (comments < end_ln if is_lineno else comments == 'none'):
            space_pos = None if (c := frag.col) == end_col else (end_ln, c)

            return ((end_ln, end_col), space_pos, False)

        text_pos = (end_ln + 1, 0)  # comment on line so text pos must be one past

    else:
        text_pos = (end_ln, end_col)  # no comment on line so default text pos is end of element unless other comments found

    past_bound_end_ln = bound_end_ln + 1

    if bound_end_col >= (ll := len(lines[bound_end_ln])):  # special stuff happens if bound is at EOL
        bound_end_pos = (bound_end_ln, ll)  # this is only used if bound is at EOL so doesn't need to be set if not
        bottom_ln = past_bound_end_ln  # two past bottommost line to be considered, max return location is bound_end_pos

    else:
        bottom_ln = bound_end_ln  # one past bottommost line to be considered, max return location is (bottom_ln, 0)

    stop_ln = comments + 1 if is_lineno and comments < bottom_ln else bottom_ln
    start_ln = end_ln + 1

    if comments == 'all':
        comments_ln = start_ln

        while (end_ln := end_ln + 1) < stop_ln:
            if not (m := re_empty_line_cont_or_comment.match(lines[end_ln])):
                break

            if (g := m.group(1)) and g.startswith('#'):
                comments_ln = end_ln + 1

        comments_pos = (comments_ln, 0) if comments_ln < past_bound_end_ln else bound_end_pos

        if comments_ln != start_ln:
            text_pos = comments_pos

        if not space:  # no space requested
            return (text_pos, None if comments_pos == text_pos else comments_pos, True)

        space_pos = (end_ln, 0) if end_ln < past_bound_end_ln else bound_end_pos

        if space_pos == text_pos:  # we reached end of search or non-comment/empty line right after comment
            return (text_pos, None, True)

        # space requested and there are some empty lines after last comment

        if space is True:
            return (text_pos, space_pos, True)  # infinite space requested so return everything we got

        space_ln = comments_ln + min(space, end_ln - comments_ln)
        space_pos = (space_ln, 0) if space_ln < past_bound_end_ln else bound_end_pos

        return (text_pos, space_pos, True)  # return only number of lines limited by finite requested space

    if is_lineno or comments == 'block':
        re_pat = re_empty_line_cont_or_comment if is_lineno else re_comment_line_start

        while (end_ln := end_ln + 1) < stop_ln:
            if not (m := re_pat.match(lines[end_ln])):
                break

        comments_ln = end_ln

    else:
        assert comments in ('none', 'line')

        comments_ln = end_ln + 1

    comments_pos = (comments_ln, 0) if comments_ln < past_bound_end_ln else bound_end_pos

    if comments_ln != start_ln:
        text_pos = comments_pos

    if not space or comments_ln == bottom_ln:
        return (text_pos, None if comments_pos == text_pos else comments_pos, True)

    for end_ln in range(comments_ln, bottom_ln if space is True else min(comments_ln + space, bottom_ln)):
        if not re_empty_line_or_cont.match(lines[end_ln]):
            break

    else:
        end_ln += 1

    space_pos = (end_ln, 0) if end_ln < past_bound_end_ln else bound_end_pos

    return (text_pos, None if space_pos == text_pos else space_pos, True)


def get_trivia_params(trivia: Trivia = None, neg: bool = False) -> _Trivia:
    """Convert options compact human representation to parameters usable for `_leading/trailing_trivia()`.

    This conversion is fairly loose and will accept shorthand '+/-#' for 'none+/-#'.

    **Parameters:**
    - `neg`: Whether to use `'-#'` suffix numbers or not (will still return `_neg` as `True` but `_space` will be 0).

    **Returns:**
    - (`lead_comments`, `lead_space`, `lead_neg`, `trail_comments`, `trail_space`, `trail_neg`): Two sets of parameters
        for the trivia functions along with the `_neg` indicators of whether the `_space` params came from negative
        space specifiers `'-#'` or not.
    """

    if isinstance(lead_comments := fst.FST.get_option('trivia'), tuple):
        lead_comments, trail_comments = lead_comments
    else:
        trail_comments = True

    if trivia is not None:
        if not isinstance(trivia, tuple):
            lead_comments = trivia

        else:
            if (t := trivia[0]) is not None:
                lead_comments = t
            if (t := trivia[1]) is not None:
                trail_comments = t

    lead_space = lead_neg = False

    if isinstance(lead_comments, bool):
        lead_comments = 'block' if lead_comments else 'none'

    elif isinstance(lead_comments, str):
        if (i := lead_comments.find('+')) != -1:
            lead_space = int(n) if (n := lead_comments[i + 1:]) else True
            lead_comments = lead_comments[:i] or 'none'

        elif (i := lead_comments.find('-')) != -1:
            lead_neg = True
            lead_space = (int(n) if (n := lead_comments[i + 1:]) else True) if neg else 0
            lead_comments = lead_comments[:i] or 'none'

        assert lead_comments != 'line'

    trail_space = trail_neg = False

    if isinstance(trail_comments, bool):
        trail_comments = 'line' if trail_comments else 'none'

    elif isinstance(trail_comments, str):
        if (i := trail_comments.find('+')) != -1:
            trail_space = int(n) if (n := trail_comments[i + 1:]) else True
            trail_comments = trail_comments[:i] or 'none'

        elif (i := trail_comments.find('-')) != -1:
            trail_neg = True
            trail_space = (int(n) if (n := trail_comments[i + 1:]) else True) if neg else 0
            trail_comments = trail_comments[:i] or 'none'

    return lead_comments, lead_space, lead_neg, trail_comments, trail_space, trail_neg


def clip_src_loc(
    self: fst.FST,
    ln: int | Literal['end'],
    col: int | Literal['end'],
    end_ln: int | Literal['end'],
    end_col: int | Literal['end'],
) -> tuple[int, int, int, int]:
    """Clip location to valid source coordinates and verify that the end does not precede the start."""

    lines = self.root._lines
    len_lines = len(lines)
    last_ln = len_lines - 1

    if ln == 'end':
        ln = last_ln
    elif ln < 0:
        ln += len_lines

    if end_ln == 'end':
        end_ln = last_ln
    elif end_ln < 0:
        end_ln += len_lines

    if ln > end_ln:
        raise IndexError('end line cannot precede start line')

    ln = max(0, min(last_ln, ln))
    end_ln = max(0, min(last_ln, end_ln))

    if col == 'end':
        col = len(lines[ln])
    elif col < 0:
        col = max(0, col + len(lines[ln]))
    else:
        col = min(col, len(lines[ln]))

    if end_col == 'end':
        end_col = len(lines[end_ln])
    elif end_col < 0:
        end_col = max(0, end_col + len(lines[end_ln]))
    else:
        end_col = min(end_col, len(lines[end_ln]))

    if end_ln == ln and col > end_col:
        raise IndexError('end column cannot precede start column on line')

    return ln, col, end_ln, end_col


def fixup_one_index(len_: int, idx: int | Literal['end'], start_at: int = 0) -> int:
    """Convert negative indices in range to len()+idx and verify index in range.

    If `start_at` is not 0 then the lower bounding index is this. This is meant for restricting slice ranges in a
    statement `body` (which may have a docstring) to start past that docstring. The returned index is for the real
    `body` field starting at `start_at`, not the virtual `_body` which starts at 0. The `len_` in all cases is the true
    length of the field.
    """

    if idx == 'end':
        idx = len_  # pragma: no cover  - yes, this is intended to cause the IndexError, if it ever gets here with this value
    elif idx < 0:
        idx += len_
    else:
        idx += start_at

    if not (start_at <= idx < len_):
        raise IndexError('index out of range')

    return idx


def fixup_slice_indices(
    len_: int, start: int | Literal['end'], stop: int | Literal['end'], start_at: int = 0
) -> tuple[int, int]:
    """Clip slice indices to slice range allowing first negative range to map into positive range. Greater negative
    indices clip to 0 (or `start_at` if not 0).

    If `start_at` is not 0 then the lower bounding index is this. This is meant for restricting slice ranges in a
    statement `body` (which may have a docstring) to start past that docstring. The returned indices are for the real
    `body` field starting at `start_at`, not the virtual `_body` which starts at 0. The `len_` in all cases is the true
    length of the field.
    """

    if start == 'end' or start > len_:
        start = len_
    elif start < 0:
        start = max(start_at, start + len_)
    else:
        start = min(len_, start + start_at)

    if stop == 'end' or stop > len_:
        stop = len_
    elif stop < 0:
        stop = max(start_at, stop + len_)
    else:
        stop = min(len_, stop + start_at)

    if stop < start:
        raise IndexError('start index must precede stop index')

    return start, stop


def fixup_field_body(ast: AST, field: str | None, only_list: bool) -> tuple[str, 'AST']:
    """Get `AST` member list for specified `field` or default if `field=None`."""

    if field is None:
        if (field := _DEFAULT_AST_FIELD.get(ast.__class__, fixup_field_body)) is fixup_field_body:  # fixup_field_body is just a sentinel value here
            raise ValueError(f"{ast.__class__.__name__} has no default body field")

    if field.startswith('_'):  # virtual field like Dict._all
        return field, []

    if (body := getattr(ast, field, fixup_field_body)) is fixup_field_body:
        raise ValueError(f"{ast.__class__.__name__} has no field '{field}'")

    if only_list and not isinstance(body, list):
        raise ValueError(f'{ast.__class__.__name__}.{field} is not a list field')

    return field, body


def validate_put_arglike(body: list[AST], start: int, stop: int, ast_or_list: AST | list[AST]) -> int | tuple[int, int]:
    """Make sure that a put of a single or list of arglikes doesn't violate ordering rules for these.

    **Returns:**
    - `kind`: Single arglike kind if `AST` passed in.
    - `(min kind, max kind)`: Minumum and maximum arglike kind if list passed in.
    """

    if not isinstance(ast_or_list, list):
        ret = kind_put_min = kind_put_max = arglike_kind(ast_or_list)

    else:
        kinds_put = list(map(arglike_kind, ast_or_list))
        kind_put_min = min(kinds_put)
        kind_put_max = max(kinds_put)
        ret = (kind_put_min, kind_put_max)

    if (start
        and kind_put_min < 2
        and (kind_before_max := max(map(arglike_kind, body[:start]))) > kind_put_min + 1
    ):
        raise NodeError(f'{ARGLIKE_KIND_NAME[kind_put_min]} cannot follow {ARGLIKE_KIND_NAME[kind_before_max]}')

    if (stop < len(body)
        and kind_put_max > 1
        and (kind_after_min := min(map(arglike_kind, body[stop:]))) < kind_put_max - 1
    ):
        raise NodeError(f'{ARGLIKE_KIND_NAME[kind_put_max]} cannot precede {ARGLIKE_KIND_NAME[kind_after_min]}')

    return ret


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _repr_tail(self: fst.FST, loc: bool = True) -> str:
    if loc:
        try:
            loc = self.loc
        except Exception:  # pragma: no cover  - maybe in middle of operation changing locations and lines
            loc = '????'

        # self.root._touchall()  # for debugging because we may have cached locs which would not have otherwise been cached during execution

    tail = ' ROOT' if self.is_root else ''

    return f'{tail} {loc[0]},{loc[1]}..{loc[2]},{loc[3]}' if loc else tail


def _dump(self: fst.FST, st: nspace, src_plus: bool = False) -> None:
    if not src_plus:
        st.src_ln = 0x7fffffffffffffff
    elif is_root := self.is_root:
        st.src_ln = 0
    else:
        st.src_ln = self.ln or 0  # if self doesn't have a location then we put everything since its a low level node anyway

    st.line_tails_dumped = set()

    _dump_node(self, st, '', '')

    if src_plus and is_root:  # put any trailing lines if putting at root
        _dump_lines(self, st, len(self.root._lines), 0, 0, 0, None)


def _cached_allargs(self: fst.FST) -> list[AST]:
    """Get cached merged ordered `posonlyargs+args+vararg+kwonlyargs+kwarg` arguments from `arguments`. Does not include
    `defaults` or `kw_defaults`."""

    try:
        allargs = self._cache['allargs']

    except KeyError:
        ast = self.a
        allargs = self._cache['allargs'] = [*ast.posonlyargs, *ast.args, *([a] if (a := ast.vararg) else ()),
                                            *ast.kwonlyargs, *([a] if (a := ast.kwarg) else ())]

    return allargs


def _cached_arglikes(self: fst.FST) -> list[AST]:
    """Get cached merged ordered arglikes from `Call.args+keywords` or `ClassDef.bases+keywords`."""

    try:
        arglikes = self._cache['arglikes']

    except KeyError:
        ast = self.a
        field = 'args' if ast.__class__ is Call else 'bases'
        arglikes = self._cache['arglikes'] = merge_arglikes(getattr(ast, field), ast.keywords)

    return arglikes


def _is_expr_arglike_only(self: fst.FST) -> bool | None:
    """Is an argumentlike expression which can only appear in a `Call.args` or `ClassDef.bases` (or a `.slice`
    `Tuple.elts` in py 3.11+) list because the syntax is invalid outside of that, e.g. `*not a`, `*a or b`.

    **Returns:**
    - `True`: Is an unparenthesized arglike expression, `*not a`, `*a or b`.
    - `False`: Is a parenthesized arglike expression, `*(not a)`, `*(a or b)`.
    - `None`: Is a not an arglike expression, `*x`, `*(x)`, `y`, `i = 1`, `pass`, etc...
    """

    ast = self.a

    if ast.__class__ is not Starred or (child := ast.value).__class__ is Tuple:  # we assume any Tuple child of a Starred is intrinsically parenthesized, otherwise it is invalid
        return None

    child_type = child.op.__class__ if (child_cls := child.__class__) in (BoolOp, BinOp, UnaryOp) else child_cls

    if not precedence_require_parens_by_type(child_type, Starred, 'value'):
        return None

    return not child.f.pars().n


def _is_solo_class_base(self: fst.FST) -> bool | None:
    """Whether `self` is a solo `ClassDef` base in list without any keywords, or not a class base at all.

    **Returns:**
    - `True` if is solo class base, `False` if is class base, but not solo and `None` if is not class base at all.

    **Examples:**

    >>> FST('class cls(b1): pass').bases[0]._is_solo_class_base()
    True

    >>> FST('class cls(b1, b2): pass').bases[0]._is_solo_class_base()
    False

    >>> FST('class cls(b1, meta=m): pass').bases[0]._is_solo_class_base()
    False

    >>> print(FST('class cls(b1, meta=m): pass').keywords[0]._is_solo_class_base())
    None
    """

    if not (parent := self.parent) or self.pfield.name != 'bases':
        return None

    return len((parenta := parent.a).bases) == 1 and not parenta.keywords


def _is_solo_call_arg(self: fst.FST) -> bool:
    """Whether `self` is a solo `Call` non-keyword argument.

    **Examples:**

    >>> FST('call(a)').args[0]._is_solo_call_arg()
    True

    >>> FST('call(a, b)').args[0]._is_solo_call_arg()
    False

    >>> FST('call(i for i in range(3))').args[0]._is_solo_call_arg()
    True
    """

    return (
        (parent := self.parent)
        and self.pfield.name == 'args'
        and (parenta := parent.a).__class__ is Call
        and not parenta.keywords
        and len(parenta.args) == 1
    )


def _is_solo_call_arg_genexp(self: fst.FST) -> bool:
    """Whether `self` is the dreaded solo call non-keyword argument generator expression in `sum(i for i in a)`.
    This function doesn't say if it shares its parentheses or not, so it could still be `sum((i for i in a))` or
    even `sum(((i for i in a)))`. To differentiate that see `pars(shared=False)`.

    **Examples:**

    >>> FST('call(i for i in range(3))').args[0]._is_solo_call_arg_genexp()
    True

    >>> FST('call((i for i in range(3)))').args[0]._is_solo_call_arg_genexp()
    True

    >>> FST('call((i for i in range(3)), b)').args[0]._is_solo_call_arg_genexp()
    False

    >>> FST('call(a)').args[0]._is_solo_call_arg_genexp()
    False
    """

    return (
        (parent := self.parent)
        and self.pfield.name == 'args'
        and self.a.__class__ is GeneratorExp
        and (parenta := parent.a).__class__ is Call
        and not parenta.keywords
        and len(parenta.args) == 1
    )


def _is_solo_matchcls_pat(self: fst.FST) -> bool:
    r"""Whether `self` is a solo `MatchClass` non-keyword pattern. The solo `Constant` held by a `MatchValue`
    qualifies as `True` for this check if the `MatchValue` does.

    **Examples:**

    >>> (FST('match a:\n  case cls(a): pass')
    ...  .cases[0].pattern.patterns[0]._is_solo_matchcls_pat())
    True

    >>> (FST('match a:\n  case cls(a, b): pass')
    ...  .cases[0].pattern.patterns[0]._is_solo_matchcls_pat())
    False

    >>> (FST('match a:\n  case cls(1): pass')
    ...  .cases[0].pattern.patterns[0]._is_solo_matchcls_pat())
    True

    >>> (FST('match a:\n  case cls(1): pass')
    ...  .cases[0].pattern.patterns[0].value._is_solo_matchcls_pat())
    True
    """

    if not (parent := self.parent):
        return False

    if (parenta := parent.a).__class__ is MatchValue:
        self = parent

    return (
        (parent := self.parent)
        and self.pfield.name == 'patterns'
        and (parenta := parent.a).__class__ is MatchClass
        and not parenta.kwd_patterns
        and len(parenta.patterns) == 1
    )


def _is_any_parent_format_spec_start_pos(self: fst.FST, ln: int, col: int) -> bool:
    """Whether `(ln, col)` is the start position of some parent up the chain `format_spec` field. This is used in put
    operations to decide whether to offset head or not since a `format_spec` can follow immediately after a value, which
    is normally not the case for other `AST` fields. We walk up multiple parents because multiple nodes may end at the
    same location."""

    lineno = ln + 1
    col_offset = self.root._lines[ln].c2b(col)

    while parent := self.parent:
        if (end_lineno := getattr(self.a, 'end_lineno', None)) is not None:  # if self ends past the check location then no parent .format_spec can possibly start at it
            if end_lineno > lineno or (end_lineno == lineno and self.a.end_col_offset > col_offset):
                return False

        if (parenta := parent.a).__class__ in (FormattedValue, Interpolation):
            return (self.pfield.name == 'value' and
                    (fs := parenta.format_spec) and fs.col_offset == col_offset and fs.lineno == lineno)

        self = parent

    return False


def _is_delimited_seq(self: fst.FST, field: str = 'elts', delims: str | tuple[str, str] = '()') -> bool:
    """Whether `self` is a delimited (parenthesized or bracketed) sequence of `field` or not. Makes sure the entire
    node is surrounded by a balanced pair of delimiters. Functions as `is_parenthesized_tuple()` if already know is a
    Tuple. Other use is for `MatchSequence`, whether parenthesized or bracketed.

    **Note:** Since this is such a common function it is cached.
    """

    key = f'isdelseq{field}{delims}'

    try:
        return self._cache[key]
    except KeyError:
        pass

    ldelim, rdelim = delims
    lines = self.root._lines

    self_ln, self_col, self_end_ln, self_end_col = self.loc

    if not lines[self_end_ln].startswith(rdelim, self_end_col - 1):
        is_delim = False

    elif not (asts := getattr(self.a, field)):
        is_delim = True  # return True if no children because assume '()' in this case

    elif not lines[self_ln].startswith(ldelim, self_col):
        is_delim = False

    else:
        f0_ln, f0_col, f0_end_ln, f0_end_col = asts[0].f.loc

        if f0_col == self_col and f0_ln == self_ln:
            is_delim = False

        else:
            _, _, fn_end_ln, fn_end_col = asts[-1].f.loc

            if fn_end_col == self_end_col and fn_end_ln == self_end_ln:
                is_delim = False

            else:  # dagnabit! have to count and balance delimiters around first element
                self_end_col -= 1  # because in case of singleton tuple for sure there is a comma between end of first element and end of tuple, so at worst we exclude either the tuple closing paren or a comma, otherwise we exclude non-tuple closing delimiter

                ldelims = len(next_delims(lines, self_ln, self_col, f0_ln, f0_col, ldelim))  # yes, we use next_delims() to count opening delimiters because we know conditions allow it
                rdelims = len(next_delims(lines, f0_end_ln, f0_end_col, self_end_ln, self_end_col, rdelim))

                is_delim = ldelims > rdelims

    self._cache[key] = is_delim

    return is_delim


def _has_Slice(self: fst.FST) -> bool:
    """Whether self is a `Slice` or a `Tuple` which directly contains any `Slice`.

    **Examples:**

    >>> FST('a:b:c', 'expr_slice')._has_Slice()
    True

    >>> FST('1, d:e', 'expr_slice')._has_Slice()  # Tuple contains at least one Slice
    True

    >>> # b is in the .slice field but is not a Slice or Slice Tuple
    >>> FST('a[b]').slice._has_Slice()
    False
    """

    return (
        (ast_cls := (ast := self.a).__class__) is Slice
        or (
            ast_cls is Tuple
            and any(e.__class__ is Slice for e in ast.elts)
    ))


def _has_Starred(self: fst.FST) -> bool:
    """Whether self is a `Starred` or a `Tuple`, `List` or `Set` which directly contains any `Starred`.

    **Examples:**

    >>> FST('*a')._has_Starred()
    True

    >>> FST('1, *a')._has_Starred()  # Tuple contains at least one Starred
    True
    """

    return (
        (ast_cls := (ast := self.a).__class__) is Starred
        or (
            ast_cls in ASTS_LEAF_TUPLE_LIST_OR_SET
            and any(e.__class__ is Starred for e in ast.elts)
    ))


def _trail_sep(
    self: fst.FST,
    ln: int | None = None,
    col: int | None = None,
    end_ln: int | None = None,
    end_col: int | None = None,
    sep: str = ',',
    del_: bool | None = False,
) -> tuple[int, int] | None:
    """Check and optionally delete trailing separator of `self`, meaning a separator directly following the `self` node,
    not a trailing separator in a node `self` which is a sequence. The separator may follow any number of closing
    parentheses, comments and line continuations (as long as is withing bound). If full bound provided then no locations
    are checked on `self` or parent. Does not call `pars()` so safe to use in the middle of edits.

    **Parameters:**
    - (`ln`, `col`): Location of start of span to search, otherwise gotten from end of `self`.
    - (`end_ln`, `end_col`): Location of end of span to search, otherwise gotten from end of parent. Is fine to use this
        even if there are other nodes that may follow because if we run into them then they will not be a closing par or
        a separator so will return no separator found.
    - `sep`: Separator to search for, usually comma.
    - `del_`: If a separator is found then this indicates whether to delete it or not (or delete it if not aesthetic).
        - `True`: Always delete separator if found.
        - `False`: Never delete separator if found (this is just a query function in this case).
        - `None`: Delete separator if found in not "aesthetic", which means followed by a comment or linecont.

    If a separator is deleted then any preceding whitespace is deleted as well unless there is nothing else preceding it
    on the line, in which case only the separator is deleted and the whitespace is left. If a separator is deleted then
    the returned location is where the separator was before the delete and can serve as a truthy indicator that a
    separator was in fact deleted.

    **Returns:**
    - `(ln, col)`: Location of found separator after any closing parentheses.
    - `None`: Separator does not follow, there is something else or end of bound.
    """

    lines = self.root._lines

    if end_ln is None:
        if parent := self.parent:
            _, _, end_ln, end_col = parent.loc
        else:
            end_ln = len(lines) - 1
            end_col = len(lines[-1])

    if ln is None:
        _, _, ln, col = self.loc

    while frag := next_frag(lines, ln, col, end_ln, end_col):  # find comma or something else, skipping close parens
        cln, ccol, src = frag

        if src.startswith(')'):
            old_len = len(src)
            src = src.lstrip(')')
            ln = cln
            col = ccol = ccol + old_len - len(src)

            if not src:
                continue

        if not src.startswith(sep):
            return None

        if del_ is None:  # delete if not "aesthetic"
            if (not (frag := next_frag(lines, cln, ccol + len(sep), cln,
                                       end_col if cln == end_ln else 0x7fffffffffffffff, True, True))
                or frag.src[0] not in '#\\'
            ):
                del_ = True

        if del_:
            if cln != ln:  # if not on same line as start of search then delete to start of preceding whitespace
                col = re_empty_space.search(lines[cln], 0 if cln > ln else col, ccol).start()  # `0 if cln > ln else col` to make sure we don't step backwards over starting bound, harmless if already skipped some par frags

            self._put_src(None, cln, col or ccol, cln, ccol + len(sep), True)  # if whitespace extends to start of line then don't delete that, maybe needed for alignment

        return (cln, ccol)

    return None


def _maybe_ins_sep(
    self: fst.FST,
    ln: int,
    col: int,
    space: bool,
    end_ln: int | None = None,
    end_col: int | None = None,
    sep: str = ',',
    exclude: Literal[True] | fst.FST | None = True,
) -> srcwpos | None:
    """Maybe insert separator at start of span if not already present as first code in span. Will skip any closing
    parentheses for check and add. We specifically don't use `pars()` here because is meant to be used where the element
    is being modified and may not be valid for that.

    **Parameters:**
    - (`ln`, `col`): Location of start of span.
    - (`end_ln`, `end_col`): Location of end of span, otherwise gotten from end of `self`.
    - `space`: Whether to add a space to new separator or existing separator IF the span is zero length or if following
        character exists and is not a space. Will add space before a separator being put if is not a comma. Will not
        insert space before an existing found separator if is not there.
    - `sep`: String separator to use. Any separator which is not a comma will have a space prepended to it if adding.
    - `exclude`: `True` means exclude `self`, `None` excludes nothing and any other `FST` excludes that `FST`. Should be
        `True` if separator is for sure being put past all elements of `self`. `FST` and `None` is meant for cases where
        there may be elements following separator insertion location. `FST` specifically for elements which end just
        before the search location so that their end position is not extended by the separator source put.

    **Returns:**
    - `srcwpos`: If something was put then returns location and what was put (separator, space or both).
    - `None`: Nothing was put.
    """

    if end_ln is None:
        _, _, end_ln, end_col = self.loc

    if offset_excluded := (exclude is True):
        exclude = self

    lines = self.root._lines

    while frag := next_frag(lines, ln, col, end_ln, end_col):  # find comma or something else, skipping close parens
        cln, ccol, src = frag

        if src.startswith(')'):
            old_len = len(src)
            src = src.lstrip(')')
            ln = cln
            col = ccol = ccol + old_len - len(src)

            if not src:
                continue

        if src.startswith(sep):  # TODO: maybe need to do regex check in future for separator like 'and' and 'or' to make sure they are not part of an identifier, but so far aren't checked in places where this may be the case
            ccol += len(sep)

            if space and ((cln == end_ln and ccol == end_col) or not _re_one_space_or_end.match(lines[cln], ccol)):
                self._put_src([' '], cln, ccol, cln, ccol, True, exclude=exclude, offset_excluded=offset_excluded)

                return srcwpos(cln, ccol, ' ')

            return None

        break

    if sep != ',':
        sep = ' ' + sep

    if space and ((ln == end_ln and col == end_col) or not _re_one_space_or_end.match(lines[ln], col)):
        sep = sep + ' '

    self._put_src([sep], ln, col, ln, col, True, exclude=exclude, offset_excluded=offset_excluded)

    return srcwpos(ln, col, sep)


def _maybe_add_singleton_comma(self: fst.FST, is_delimited: bool | None = None, elts: list[AST] | None = None) -> None:
    """Maybe add comma to tuple if is singleton and comma not already there, parenthesization not checked or taken
    into account. `self.a` must be a `Tuple`. Can also be used on other comma-delimited sequences."""

    # assert self.a.__class__ is Tuple

    if elts is None:
        elts = self.a.elts

    if len(elts) == 1:
        self._maybe_ins_sep((f := elts[0].f).end_ln, f.end_col, False, self.end_ln,
                            self.end_col - (self._is_delimited_seq() if is_delimited is None else is_delimited))


def _maybe_add_line_continuations(  # TODO: doing double duty, maybe rename to something like `_fix_line_endings()`?
    self: fst.FST,
    whole: bool = False,
    *,
    del_comments: bool = True,
    del_comment_lines: bool = False,
    add_lconts: bool = True
) -> bool:
    """Check if `self` needs them and if so add line continuations to make parsable. Can delete commnents which may
    prevent line continuations. Can also **JUST** delete comments (except on last line), without adding line
    continuations.

    **Parameters:**
    - `whole`: Whether to check whole source (and add line continuations to, only if at root). Otherwise will just
        check and modify lines that this node lives on.
    - `del_comments`: If `True` then will delete comments which prevent line continuations from making the source
        parsable. If `False` then will raise an error if this is encountered.
    - `del_comment_lines`: If `True` and deleting comments then if a comment is the only thing on a line then that whole
        line is deleted.
    - `add_lconts`: If `True` (the normal mode of operation) then does what this function name indicates. Can turn this
        off to only delete comments, which is useful for sanitizing some things like the `_aliases` SPECIAL SLICE.

    **Returns:**
    - `bool`: Whether modification was made or not.
    """

    lns = set()

    if self._is_enclosed_or_line(whole=whole, out_lns=lns):
        return False

    lines = self.root._lines
    end_cols = {}  # {end_ln: end_col, ...} last expression columns for lines, needed for comment checks (so we don't get false comments from inside strings)

    for a in walk(self.a):
        if (loc := a.f.loc) is not None:
            _, _, end_ln, end_col = loc

            end_cols[end_ln] = max(end_cols.get(end_ln, 0), end_col)

    if del_comment_lines:  # if deleting lines then need to go in reverse
        lns = list(lns)

        lns.sort()
        lns.reverse()

    for ln in lns:
        m = re_line_end_cont_or_comment.search(l := lines[ln], end_cols.get(ln, 0))

        if not (g := m.group(1)):
            if add_lconts:
                lines[ln] = bistr(l + ('\\' if not l or l[-1:].isspace() else ' \\'))

        elif g.startswith('#'):
            if not del_comments:
                raise NodeError('cannot add line continuation to line that ends with comment')

            # maybe just delete line if contains only comment?

            comment_start = m.start(1)
            m = re_empty_space.search(l, 0, comment_start)
            ws_start = m.start()

            if not ws_start and del_comment_lines:  # comment takes up whole line and deleteing whole comment lines?
                self._put_src(None, ln, 0, ln + 1, 0, True)
            elif not add_lconts:  # just delete comment
                lines[ln] = bistr(l[:ws_start])
            elif not ws_start:  # adding line continuations, fully empty line so put line continuation where comment started
                lines[ln] = bistr(l[:comment_start] + '\\')
            else:
                lines[ln] = bistr(l[:ws_start] + ' \\')

    return True


def _fix_joined_alnums(
    self: fst.FST,
    ln: int,
    col: int,
    end_ln: int | None = None,
    end_col: int | None = None,
    *,
    lines: list[str] | None = None,  # misc optimization so don't need to walk parent chain to get this since most likely outcome of this function doesn't have to call _put_src()
) -> None:
    """Check if location(s) `lines[ln][col-1 : col+1]` and optionally `lines[end_ln][end_col-1 : end_col+1] is / are
    alphanumeric and if so separate them with a space. This is for operations that may inadvertantly join two distinct
    elements into a single parsable alphanumeric, e.g. `for i inb, 2: pass`.

    `self` doesn't matter, call on any node in tree. `lines` is in case caller already has it to not walk up parent
    chain again to get it.
    """

    if lines is None:
        lines = self.root._lines

    if end_ln is not None:
        if end_col and re_alnumdot_alnum.match(lines[end_ln], end_col - 1):  # make sure last element didn't wind up joining two alphanumerics, and if so separate
            self._put_src([' '], end_ln, end_col, end_ln, end_col, False)

    if col and re_alnumdot_alnum.match(lines[ln], col - 1):  # make sure first element didn't wind up joining two alphanumerics, and if so separate
        self._put_src([' '], ln, col, ln, col, False)


def _fix_undelimited_seq(
    self: fst.FST, body: list[AST], delims: str = '()', delim: bool | None = None
) -> bool:
    """Fix undelimited `Tuple` or `MatchSequence` if needed. Don't call on delimited sequence. Fixes locations as well
    as delimiting. Can also be used on other comma-delimited sequences.

    **Parameters:**
    - `delim`: When to delimit **NON-EMPTY** sequences whether it is needed for parsability or not. Delimiters are
        always added to empty sequences irrespective of this parameter.
        - `False`: Never add (unless empty).
        - `None`: Only add if needed for parsability.
        - `True`: Always add.

    **Returns:**
    - `bool`: Whether the sequence was delimited or not.
    """

    # assert self.a.__class__ in _ASTS_LEAF_TUPLE_OR_MATCHSEQ

    if not body:  # if is empty then just need to delimit
        lines = self.root._lines
        ln, col, end_ln, end_col = self.loc

        if not next_frag(lines, ln, col, end_ln, end_col, True):  # if no comments in seq area then just replace with '()' (or '[]')
            self._put_src([delims], ln, col, end_ln, end_col, True, False)  # WARNING! `tail=True` may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized seq starts, but haven't found a case where this can happen

        else:  # otherwise preserve comments by parenthesizing whole area
            ldelim, rdelim = delims

            if ((m := re_line_end_ws_cont_or_comment.search(l := lines[end_ln], col if end_ln == ln else 0, end_col))
                and m.group(1)
            ):  # there is a comment or a line continuation on the last line, we need to insert a newline before the right delimiter, we are counting on this not being horribly malformed with the end of the sequence lying in the middle of a comment
                self._put_src(['', rdelim], end_ln, end_col, end_ln, end_col, True)
            elif l.endswith(' ', 0, end_col):  # if ends with a space then just replace it
                lines[end_ln] = bistr(f'{l[:end_col - 1]}{rdelim}{l[end_col:]}')
            else:  # otherwise insert
                self._put_src([rdelim], end_ln, end_col, end_ln, end_col, True)

            if (l := lines[ln]).startswith(' ', col):  # if starts with a space then replace it
                lines[ln] = bistr(f'{l[:col]}{ldelim}{l[col + 1:]}')
            else:  # otherwise insert
                self._put_src([ldelim], ln, col, ln, col, False, False)

        return True

    ln, col, end_ln, end_col = self.loc

    if (delim is True
        or (
            delim is None
            and (
                not (
                    end_ln == ln
                    or self._is_enclosed_or_line(check_pars=False)
                    or self._is_enclosed_in_parents()
                )  # could have line continuations
                or (any(e.__class__ is NamedExpr and not e.f.pars().n for e in body))  # yeah, this is fine in parenthesized tuples but not in naked ones, only applies to tuples and not MatchSequence obviously
    ))):
        self._delimit_node(delims=delims)

        return True

    lines = self.root._lines
    eln, ecol, _, _ = body[0].f.pars()

    if ecol != col or eln != ln:  # to be super safe we enforce that an undelimited node must start at the first element
        self._put_src(None, ln, col, eln, ecol, False)

        ln, col, end_ln, end_col = self.loc

    _, _, eend_ln, eend_col = body[-1].f.pars()

    if comma := next_find(lines, eend_ln, eend_col, end_ln, end_col, ','):  # could be closing grouping pars before comma
        eend_ln, eend_col = comma
        eend_col += 1

    if end_col != eend_col or end_ln != eend_ln:  # if seq doesn't end on last element or trailing comma then set that as the end and clean up some trailing newline, whitespace and / or line continuation
        self._set_end_pos(eend_ln + 1, lines[eend_ln].c2b(eend_col), (a := self.a).end_lineno, a.end_col_offset)

        # TODO: this is aesthetic stuff and could probably use some tweaking
        # TODO: change _re_line_end_ws_maybe_cont use to re_line_end_ws_cont_or_comment? current one may get false positive from backslash in comment?

        if len(end_line := lines[end_ln]) == end_col and len(lines) - 1 == end_ln:  # seq ends exactly at end of source?
            if not end_line:  # if last line is trailing newline then we can delete it and remove trailing whitespace and maybe line continuation on line before
                self._put_src(None, end_ln - 1, _re_line_end_ws_maybe_cont.search(lines[-2]).start(), end_ln, 0, True)

            elif (ws_col := _re_line_end_ws_maybe_cont.search(end_line).start()) != end_col:  # seq ends on last line, just strip whitespace
                self._put_src(None, end_ln, ws_col, end_ln, end_col, True)

        elif eend_ln == end_ln:  # otherwise if ends on its own last line
            if (ws_col := _re_line_end_ws_maybe_cont.search(end_line, eend_col, end_col).start()) != end_col:
                self._put_src(None, end_ln, ws_col, end_ln, end_col, True)

        # if end_ln == eend_ln:  # if ends on its own last line then maybe just strip trailing whitespace
        #     if (ws_col := _re_line_end_ws_maybe_cont.search(lines[end_ln], eend_col, end_col).start()) != end_col:
        #         self._put_src(None, end_ln, ws_col, end_ln, end_col, True)

        # elif re_empty_line.match(lines[end_ln]):  # last line of current end location is whitespace?
        #     if ws_col := _re_line_end_ws_maybe_cont.search(lines[end_ln - 1]).start():  # we don't need to bound by eend_col because its not whitespace so the regex will not go past it
        #         self._put_src(None, end_ln - 1, ws_col, end_ln, end_col, True)

        end_ln = eend_ln
        end_col = eend_col

    self._fix_joined_alnums(ln, col, end_ln, end_col, lines=lines)

    return False


def _fix_Tuple(self: fst.FST, is_delimited: bool | None = None, par_if_needed: bool = True) -> bool:
    """Add a missing trailing comma to a singleton tuple without one and parenthesize an empty tuple if it is not
    parenthesized or requires it for parsability (and is allowed by `pars` option).

    **Parameters:**
    - `is_delimited`: Either `True` or `False` to indicate that is or is not delimited or `None` so that we check here.
    - `par_if_needed`: Whether to parenthesize **NON-EMPTY** tuple if it needs it or not. Empty tuples are always
        parenthesized irrespective of this parameter.

    **Returns:**
    - `bool`: Whether the tuple is parenthesized or not (after the fix, regardless of if fix was done or not).
    """

    assert self.a.__class__ is Tuple

    if is_delimited is None:
        is_delimited = self._is_delimited_seq()

    if body := self.a.elts:
        self._maybe_add_singleton_comma(is_delimited)

    if not is_delimited:
        return self._fix_undelimited_seq(body, '()', par_if_needed and None)

    return is_delimited


def _fix_Set(self: fst.FST, norm: bool | Literal['star', 'call'] = True) -> None:
    """Fix `Set` if is empty to be parsable according to `norm`. If `norm` is `False` then no fix is done.

    **Parameters:**
    - `norm`: Determines if a fix is done for an empty set and if so what kind it is.
        - `False`: Don't fix, leave as invalid node.
        - `True`: Fix with `star`.
        - `'star' | 'call'`: Fix by adding a single `*()` element or changing the type of node to a call `set()`.
    """

    assert self.a.__class__ is Set

    if norm and not (ast := self.a).elts:
        if norm == 'call':
            new_ast, new_src = new_empty_set_call(ast.lineno, ast.col_offset, as_fst=False)
        else:  # True, 'star'
            new_ast, new_src = new_empty_set_star(ast.lineno, ast.col_offset, as_fst=False)

        ln, col, end_ln, end_col = self.loc

        self._put_src(new_src, ln, col, end_ln, end_col, True)
        self._set_ast(new_ast)


def _fix_arglikes(self: fst.FST, options: Mapping[str, Any] | None = None, field: str = 'elts') -> None:
    """Parenthesize any arglike expressions in `self` according to `options` if not `None`, otherwise always
    parenthesizes (NOT the `_arglikes` SPECIAL SLICE)."""

    # assert self.a.__class__ is Tuple

    if options is None or fst.FST._get_opt_eff_pars_arglike(options):
        for e in getattr(self.a, field):
            if (f := e.f)._is_expr_arglike_only():
                f._parenthesize_grouping()


def _fix_elif(self: fst.FST) -> None:
    """If source at self is an `elif` instead of an `if` then convert it to `if`."""

    assert self.a.__class__ is If

    lines = self.root._lines
    ln, col, _, _ = self.loc

    if lines[ln].startswith('elif', col):
        self._put_src(None, ln, col, ln, col + 2, False)


def _fix_copy(self: fst.FST, options: Mapping[str, Any]) -> None:
    """Maybe fix source and `ctx` values for cut or copied nodes (to make subtrees parsable if the source is not after
    the operation). If cannot fix or ast is not parsable by itself then ast will be unchanged. Is meant to be a quick
    fix after a cut or copy operation, not full check, for that use `verify()`.

    **WARNING!** Only call on root node!
    """

    assert not self.parent  # self.is_root

    ast = self.a
    ast_cls = ast.__class__

    if ast_cls not in ASTS_LEAF_EXPR or ast_cls in (Slice, FormattedValue, Interpolation):  # things that should not get pars
        return

    self._set_ctx(Load)  # noop if no ctx

    pars = fst.FST.get_option('pars', options)

    if ast_cls is Tuple:
        if (pars_arglike := options.get('pars_arglike', ...)) is ...:
            pars_arglike = fst.FST.get_option('pars_arglike')

        if pars_arglike or (pars_arglike is None and pars is True):
            need_pars = False

            for e in ast.elts:
                if (f := e.f)._is_expr_arglike_only():
                    f._parenthesize_grouping()
                elif e.__class__ is NamedExpr and not need_pars and not e.f.pars().n:
                    need_pars = True

        else:
            need_pars = None  # we don't know

        if pars:
            if is_delimited := self._is_delimited_seq():
                need_pars = False
            elif need_pars is None:  # unparenthesized walrus in naked tuple?
                need_pars = any(e.__class__ is NamedExpr and not e.f.pars().n for e in ast.elts)

            self._maybe_add_singleton_comma(is_delimited)  # specifically for lone '*starred' as a `Tuple` without comma from `Subscript.slice`, even though those can't be gotten alone organically, maybe we shouldn't even bother?

            if need_pars:
                self._delimit_node()

    elif ast_cls is NamedExpr:
        if (pars_walrus := options.get('pars_walrus', ...)) is ...:
            pars_walrus = fst.FST.get_option('pars_walrus')

        if (((pars_walrus or (pars_walrus is None and pars)) and not self.pars().n)
            or (pars and not self._is_enclosed_or_line())
        ):
            self._parenthesize_grouping()

    elif (is_expr_arglike := self._is_expr_arglike_only()) is not None:
        if (pars_arglike := options.get('pars_arglike', ...)) is ...:
            pars_arglike = fst.FST.get_option('pars_arglike')

        if (pars_arglike or (pars_arglike is None and pars)) and is_expr_arglike:
            self._parenthesize_grouping()

    elif pars and not self._is_enclosed_or_line():
        self._parenthesize_grouping()


def _parenthesize_grouping(self: fst.FST, whole: bool = True, *, star_child: bool = True) -> None:
    """Parenthesize anything with non-node grouping parentheses. Just adds text parens around node adjusting parent
    locations but not the node itself.

    **WARNING!** DO NOT parenthesize an unparenthesized `Tuple` or undelimited `MatchSequence`.

    **Parameters:**
    - `whole`: If at root then parenthesize whole source instead of just node.
    - `star_child`: `Starred` expressions cannot be parenthesized, so when this is `True` the parentheses are applied to
        the `value` child and the opening par is put right after the `*` to resolve any enclosure issues. This overrides
        `whole` for the opening par.
    """

    lines = self.root._lines
    ast = self.a
    loc = self.loc

    if whole and (whole := self.is_root):  # need to make sure last line doesn't end with a comment
        ln, col, end_ln, end_col = self.whole_loc

        if loc:
            _, _, self_end_ln, search_col = loc
        else:
            self_end_ln = search_col = 0

        is_last_line_comment = lines[end_ln].find('#', 0 if self_end_ln < end_ln else search_col) != -1

    else:
        ln, col, end_ln, end_col = loc
        is_last_line_comment = False

    if is_star_child := ast.__class__ is Starred and star_child:
        ln, col, _, _ = loc  # we specifically want as much space around child as possible, not just location of child
        col += 1
        self = ast.value.f

    put_lines = ['', ')'] if is_last_line_comment else [')']

    self._put_src(put_lines, end_ln, end_col, end_ln, end_col, True, True, self, offset_excluded=False)

    if is_star_child:  # because of maybe `whole`, otherwise could just do it using _put_src(..., offset_excluded=is_star_child) above
        if whole and is_last_line_comment:
            end_ln += 1
            end_col = 0

        ast.end_lineno = end_ln + 1
        ast.end_col_offset = lines[end_ln].c2b(end_col) + 1

    self._offset(*self._put_src(['('], ln, col, ln, col, False, False, self, offset_excluded=False))


def _unparenthesize_grouping(self: fst.FST, shared: bool | None = True, *, star_child: bool = True) -> bool:
    """Remove grouping parentheses from anything if present. Just remove text parens around node and everything between
    them and node adjusting parent locations but not the node itself. Safe to call on nodes which are not parenthesized.

    **Parameters:**
    - `shared`: Whether to allow merge of parentheses into shared single call argument generator expression or not. If
        `None` then will attempt to unparenthesize any enclosing parentheses, whether they belong to this node or not
        (meant for internal use). If sure that this cannot apply to `self` then pass `False` here for slightly more
        optimal operation.
    - `star_child`: `Starred` expressions cannot be parenthesized, so when this is `True` the parentheses are removed
        from the `value` child.

    **Returns:**
    - `bool`: Whether parentheses were removed or not (only removed if present to begin with and removable).
    """

    if self.a.__class__ is Starred and star_child:
        self = self.a.value.f

    pars_loc = self.pars(shared=None if shared is None else True)

    if shared:
        shared = self._is_solo_call_arg_genexp()

    if not getattr(pars_loc, 'n', 0) and not shared:
        return False

    ln, col, end_ln, end_col = self.bloc
    pln, pcol, pend_ln, pend_col = pars_loc
    lines = self.root._lines

    if shared:  # special case merge solo argument GeneratorExp parentheses with call argument parens
        _, _, cend_ln, cend_col = self.parent.a.func.f.loc
        pln, pcol = prev_find(lines, cend_ln, cend_col, pln, pcol, '(')  # must be there
        pend_ln, pend_col = next_find(lines, pend_ln, pend_col, len(lines) - 1, len(lines[-1]), ')')  # ditto
        pend_col += 1

        self._put_src(None, end_ln, end_col, pend_ln, pend_col, True, self)
        self._put_src(None, pln, pcol, ln, col, False)

    else:  # in all other case we need to make sure par is not separating us from an alphanumeric on either side, and if so then just replace that par with a space
        if pend_col >= 2 and _re_par_close_alnums.match(l := lines[pend_ln], pend_col - 2):
            lines[pend_ln] = bistr(l[:pend_col - 1] + ' ' + l[pend_col:])
        else:
            self._put_src(None, end_ln, end_col, pend_ln, pend_col, True, self)

        if pcol and _re_par_open_alnums.match(l := lines[pln], pcol - 1):
            lines[pln] = bistr(l[:pcol] + ' ' + l[pcol + 1:])
        else:
            self._put_src(None, pln, pcol, ln, col, False)

    return True


def _delimit_node(self: fst.FST, whole: bool = True, delims: str = '()') -> None:
    """Delimit (parenthesize or bracket) a node (`Tuple` or `MatchSequence`, but could be others) with appropriate
    delimiters which are passed in and extend the range of the node to include those delimiters. Can also be used on
    other comma-delimited sequences.

    **WARNING!** No checks are done so make sure to call where it is appropriate!

    **Parameters:**
    - `whole`: If at root then delimit whole source instead of just node.
    """

    # assert self.a.__class__ in _ASTS_LEAF_TUPLE_OR_MATCHSEQ

    lines = self.root._lines
    ast = self.a
    is_last_line_comment = False

    if not (whole and self.is_root):
        ln, col, end_ln, end_to_col = self.loc
        end_from_col = end_to_col

    else:  # need to make sure last line doesn't end with a comment or line continuation
        ln, col, end_ln, end_to_col = self.whole_loc
        end_from_col = end_to_col

        if not (last_child := self.last_child('loc')):
            search_col = 0

        else:
            _, _, child_end_ln, search_col = last_child.loc

            if child_end_ln < end_ln:
                search_col = 0

        if ((m := re_line_end_ws_cont_or_comment.search(lines[end_ln], search_col))
            and (g := m.group(1))
        ):
            if g.startswith('#'):
                is_last_line_comment = True
            else:  # g.startswith('\\'), is a line continuation, so we delete it and any preceding whitespace after end_from_col
                end_from_col = m.start(0)

    if is_last_line_comment:
        self._put_src(['', delims[1]], end_ln, end_from_col, end_ln, end_to_col, True, False, self)

        ast.end_lineno = end_ln + 2  # yes this can change
        ast.end_col_offset = 1  # can't count on this being set by put_src() because end of `whole` could be past end of sequence

    else:
        self._put_src([delims[1]], end_ln, end_from_col, end_ln, end_to_col, True, False, self)

        ast.end_lineno = end_ln + 1
        ast.end_col_offset = lines[end_ln].c2b(end_from_col + 1)

    self._offset(*self._put_src([delims[0]], ln, col, ln, col, False, False, self), self_=False)

    ast.lineno = ln + 1
    ast.col_offset = lines[ln].c2b(col)  # ditto on the `whole` thing


def _undelimit_node(self: fst.FST) -> bool:
    """Remove intrinsic delimiters from `Tuple`, `List`, `Set`, `Dict`, `MatchSequence`, `MatchMapping`, `ListComp`,
    `SetComp`, `DictComp` or `GeneratorExp`. Shrinks node location for the removed delimiters. Will not undelimit an
    empty node. Removes everything between the delimiters and the actual sequence, e.g. `(  1, 2  # yay \\n)` -> `1, 2`.

    **Returns:**
    - `bool`: Whether delimiters were removed or not (they may not be for an empty `Tuple` or other empty sequence).
    """

    ast = self.a
    ast_cls = ast.__class__

    assert ast_cls in ASTS_LEAF_DELIMITED

    if (body := getattr(ast, 'elts', None)) is not None:  # Tuple, List, Set
        if not body:
            return False

        b0 = body[0]
        bn = body[-1]

    elif (body := getattr(ast, 'patterns', None)) is not None:  # MatchSequence, MatchMapping
        if ast_cls is MatchSequence:
            if not body:
                return False

            b0 = body[0]
            bn = body[-1]

        else:  # MatchMapping, need to check for `rest`
            if ast.rest:
                bn = nspace(f=nspace(pars=lambda loc=self._loc_MatchMapping_rest(True): loc))  # noqa: B008
                b0 = ast.keys[0] if body else bn

            elif not body:
                return False

            else:
                b0 = ast.keys[0]
                bn = body[-1]

    elif ast_cls is Dict:
        if not (body := ast.values):
            return False

        bn = body[-1]

        if not (b0 := ast.keys[0]):
            b0 = nspace(f=nspace(pars=lambda loc=self._loc_maybe_key(0): loc))  # noqa: B008

    else:  # Comp or GeneratorExp
        b0 = getattr(ast, 'elt', None) or ast.key
        bn = self.last_child().a

    # got the first and last elements, now do the undelimiting

    ln, col, end_ln, end_col = self.loc
    b0_ln, b0_col, bn_end_ln, bn_end_col = b0.f.pars()

    if b0_col == col and b0_ln == ln:  # if not delimited then return
        return False

    if bn is not b0:
        _, _, bn_end_ln, bn_end_col = bn.f.pars()

    lines = self.root._lines

    if comma := next_find(lines, bn_end_ln, bn_end_col, end_ln, end_col, ','):  # need to leave trailing comma if its there
        bn_end_ln, bn_end_col = comma
        bn_end_col += 1

    else:  # when no trailing comma need to make sure par is not separating us from an alphanumeric on either side, and if so then insert a space at the end before deleting the right par
        if end_col >= 2 and _re_delim_close_alnums.match(lines[end_ln], end_col - 2):
            self._put_src(' ', end_ln, end_col, end_ln, end_col, False, self)

    head_alnums = col and _re_delim_open_alnums.match(lines[ln], col - 1)  # if open has alnumns on both sides then insert space there too

    self._put_src(None, bn_end_ln, bn_end_col, end_ln, end_col, True, self)
    self._put_src(None, ln, col, b0_ln, b0_col, False)

    if head_alnums:  # but put after delete par to keep locations same
        self._put_src(' ', ln, col, ln, col, False)

    return True


def _trim_delimiters(self: fst.FST) -> None:
    """Remove the delimiters of `self` and everything before and after them. `self` must be a container with single
    character delimiters like a parenthesized `Tuple`, `List`, `Set`, `Dict`, `MatchSequence` or `MatchMapping`."""

    assert not self.parent  # self.is_root

    lines = self._lines
    ast = self.a
    ln, col, end_ln, end_col = self.loc
    col += 1
    end_col -= 1
    ast.col_offset += 1
    ast.end_col_offset -= 1

    self._offset(ln, col, -ln, -lines[ln].c2b(col), True)  # tail=True for empty tuple '()', otherwise end would not be offset

    lines[end_ln] = bistr(lines[end_ln][:end_col])
    lines[ln] = bistr(lines[ln][col:])

    del lines[end_ln + 1:], lines[:ln]


def _normalize_block(
    self: fst.FST, field: Literal['body', 'orelse', 'finalbody'] = 'body', *, indent: str | None = None
) -> bool:
    """Move statements on the same logical line as a block open to their own line, e.g:
    ```
    if a: call()
    ```
    Becomes:
    ```
    if a:
        call()
    ```

    For convenience can call on non-block or non-statement node or node which doesn't have this field, is a noop in this
    case.

    **Parameters:**
    - `field`: Which block to normalize (`'body'`, `'orelse'`, `'finalbody'`). `'handlers'` or `'cases'` wouldn't make
        sense.
    - `indent`: The indentation to use for the relocated line if already known, saves a call to `_get_block_indent()`.

    **Returns:**
    - `bool`: Whether block was normalized or not.
    """

    ast = self.a

    if ast.__class__ not in ASTS_LEAF_BLOCK or not (body := getattr(ast, field)):  # body guaranteed to be list if there
        return False

    body0 = body[0].f
    body0_ln, body0_col, _, _ = body0.bloc

    if prev := body0.prev('loc'):
        _, _, ln, col = prev.bloc
    else:
        ln, col, _, _ = self.loc

    if not (colon := prev_find(self.root._lines, ln, col, body0_ln, body0_col, ':', True, lcont=None)):  # only found if is on same logical line as first body child, comment left as False because that breaks logical line anyway
        return False

    ln, col = colon

    if indent is None:
        indent = body0._get_block_indent()

    self._put_src(['', indent], ln, col + 1, body0_ln, body0_col, False)

    return True


def _getput_line_comment(
    self: fst.FST,
    comment: str | None | Literal[False] = False,
    field: Literal['body', 'orelse', 'finalbody'] | None = None,
    full: bool = False,
) -> str | None:
    """Get and / or put current line comment for this node.

    The line comment is the single comment at the end of the last line of the location of this node, with the exception
    of statement block nodes where the line comment lives on the last line of the header of the node (after the `:`,
    since the comment on the last line of the location belongs to the last child).

    **Parameters:**
    - `comment`: The comment operation to perform after getting the current comment.
        - `str`: Put new comment which may or may not need to have the initial `'#'` according to the `full` parameter.
        - `None`: Delete current comment (if present).
        - `False`: Do not modify current comment, just get it.
    - `field`: If `self` is a block statement then this can specify which field to operate on, only `'body'`, `'orelse'`
        and `'finalbody'` make sense to use and an error will be raised if the field is not present or there is nothing
        in it. `None` means use default `'body'` if block statement.
    - `full`:
        - `False`: The gotten comment text is returned stripped of the `'#'` and any leading and trailing whitespace. On
            put the `comment` text is put to existing comment if is present and otherwise is prepended with `'  #'` and
            a single leading whitespace after that if needed and put after the node.
        - `True`: The entire gotten comment from the end of the node to the end of the line is returned with no
            whitespace stripped, e.g. `'  # comment  '`. On put the `comment` **MUST** start with a `'#'` and possible
            leading whitespace before that and is put verbatim with no stripping, replacing any existing comment from
            the end of the node to the end of the line.

    **Returns:**
    - `str`: The current comment, before any replacement, with or without the leading whitespace and `'#'` as per the
        `full` paramenter.
    - `None`: There was no comment present.
    """

    ast = self.a
    ast_cls = ast.__class__

    # TODO: most expressionlike nodes can have line comments (sliceable ones, and even not if the are separated onto multiple lines and enclosed in parent or grouping pars)

    if ast_cls not in ASTS_LEAF_STMTLIKE:
        raise NotImplementedError('get / put line comment for non-statementlike node')

    if is_block := (ast_cls in ASTS_LEAF_BLOCK):
        if field is None:
            field = 'body'

        _, _, end_ln, end_col = self._loc_block_header_end(field)

    else:
        _, _, end_ln, end_col = self.bloc

    lines = self.root._lines
    last_stmt_line = lines[end_ln]
    m = _re_stmt_line_comment.match(last_stmt_line, end_col)  # will match anything even if empty

    if (old_comment := m.group(2)) and not full:  # if full is False then old_comment will be either None or the full comment group as it should be
        old_comment = m.group(3).strip()  # comment present and full=False, we need just the comment text

    if comment is False:  # if only get operation then we are done
        return old_comment

    # put operation

    if comment is not None:
        if '\n' in comment:
            raise ValueError('line comment cannot have newlines in it')

        if full:
            if not comment.lstrip().startswith('#'):
                raise ValueError("full line comment must start with '#'")

        elif not comment[:1].isspace():
            comment = ' ' + comment

    if old_comment is not None:  # if comment already present then any replacement is trivial
        self._put_src(comment, end_ln, m.start(2 if comment is None or full else 3), end_ln, 0x7fffffffffffffff)
        self._touchall(True, False, False)  # touch parents to clear bloc caches because comment on last child statement is included in parent bloc

        return old_comment

    if comment is None:  # if deleting comment that doesn't exist then this is even more trivial
        return old_comment

    # put comment where there was no comment before, may need to normalize block header or semicoloned statements

    with self._modifying():  # this isn't strictly needed at the time of writing, future-proofing
        before_semi_end_col = end_col

        if has_semi := m.group(1):  # if semicolon present then we start search after it
            end_col = m.end(1)

        if not full:
            comment = '  #' + comment

        if not (l := last_stmt_line[end_col:]) or l.isspace():  # no other statement or line continuation on last statement line so we can just add the comment
            pass  # noop

        elif is_block:
            if self._normalize_block(field):
                _, _, end_ln, end_col = self._loc_block_header_end(field)  # any remaining junk on header tail (maybe line continuation) is harmless to remove

        # we are past any semicolon on this line, its either another statement or a line continuation ... which may lead to another statement or the semicolon which is not on this line, or not

        elif (next_stmt := self.next()) and next_stmt.pfield.name == self.pfield.name:  # if there is a next sibiling and is part of same body then we need to process more, if not then safe to nuke rest of line
            next_ln, next_col, _, _ = next_stmt.bloc

            if ((frag := next_frag(lines, end_ln, end_col, next_ln, next_col + 1, True, None))  # search to 1 past start of next statement to be able to run into it it on logical line
                and frag.src.startswith(';')  # a semicolon?
            ):
                if has_semi:  # if already had one then error
                    raise RuntimeError('should not get here, found two semicolons without a statement between them')  # pragma: no cover

                frag = next_frag(lines, frag.ln, frag.col + 1, next_ln, next_col + 1, True, None)  # search again, it better not be another semicolon!

            if frag and not frag.src.startswith('#'):  # if its not a comment then its the next statement
                assert frag.ln == next_ln and frag.col == next_col

                indent = self._get_block_indent()

                if (parent := self.parent) and parent._normalize_block(self.pfield.name, indent=indent):  # if have parent then normalize the block because could all be on header logical line separated with semicolons
                    _, _, end_ln, before_semi_end_col = self.bloc  # locations have changed
                    next_ln, next_col, _, _ = next_stmt.bloc

                self._put_src([comment, indent], end_ln, before_semi_end_col, next_ln, next_col, False)  # now, FINALLY, we write the comment along with a newline to split up the statements, don't need to touch explicitly because offseting _put_src touches

                return old_comment

        self._put_src(comment, end_ln, end_col, end_ln, 0x7fffffffffffffff)
        self._touchall(True, False, False)

        return old_comment
