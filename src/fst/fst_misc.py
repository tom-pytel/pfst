"""Misc common `FST` class and standalone methods.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import re
from ast import iter_fields, walk
from math import log10
from pprint import pformat
from typing import Any, Literal, Mapping

from . import fst

from .asttypes import (
    ASTS_BLOCK,
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
    expr,
    keyword,
    match_case,
    mod,
    pattern,
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
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from .astutil import pat_alnum, constant, re_alnumdot_alnum, bistr, precedence_require_parens_by_type

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
    next_frag,
    next_find,
    prev_find,
    next_delims,
)

__all__ = [
    'new_empty_tuple',
    'new_empty_set_star',
    'new_empty_set_call',
    'new_empty_set_curlies',
    'leading_trivia',
    'trailing_trivia',
    'get_trivia_params',
    'get_option_overridable',
    'clip_src_loc',
    'fixup_one_index',
    'fixup_slice_indices',
    'fixup_field_body',
]


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

_DEFAULT_AST_FIELD = {kls: field for field, classes in [  # builds to {Module: 'body', Interactive: 'body', ..., Match: 'cases', ..., MatchAs: 'pattern'}
    # list fields of multiple children
    ('body',                  (Module, Interactive, Expression, FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While,
                               If, With, AsyncWith, Try, TryStar, ExceptHandler, Lambda, match_case),),
    ('handlers',              (_ExceptHandlers,)),
    ('cases',                 (Match, _match_cases)),

    ('elts',                  (Tuple, List, Set)),
    ('targets',               (Delete, _Assign_targets)),
    ('decorator_list',        (_decorator_list,)),
    ('patterns',              (MatchSequence, MatchOr, MatchClass)),
    ('type_params',           (TypeAlias, _type_params)),
    ('names',                 (Import, ImportFrom, Global, Nonlocal, _aliases)),
    ('items',                 (_withitems,)),
    ('values',                (BoolOp, JoinedStr, TemplateStr)),
    ('generators',            (_comprehensions,)),
    ('ifs',                   (_comprehension_ifs,)),
    ('args',                  (Call,)),  # potential conflict of default body with put to empty 'set()'

    # special case fields
    ('_all',                  (Dict,)),          # key:value
    ('_all',                  (MatchMapping,)),  # key:pattern,rest?
    ('_all',                  (Compare,)),       # left,op:comparator

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

_re_stmt_tail          = re.compile(r'\s*(;(?:\s*#.*)?|#.*)')
_re_one_space_or_end   = re.compile(r'\s|$')

_re_par_open_alnums    = re.compile(rf'[{pat_alnum}.][(][{pat_alnum}]')
_re_par_close_alnums   = re.compile(rf'[{pat_alnum}.][)][{pat_alnum}]')
_re_delim_open_alnums  = re.compile(rf'[{pat_alnum}.][([][{pat_alnum}]')
_re_delim_close_alnums = re.compile(rf'[{pat_alnum}.][)\]][{pat_alnum}]')


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

                linefunc(f'{c.clr_loc}{cln:<{width}}:{c.end_loc} {c.clr_src}{lines[cln]}{c.end_src}{e}{eol}')

        st.src_ln = end_ln + 1

    if not is_stmt:
        if is_stmt is None:  # we just wanted to put trailing lines so we are done
            return

        lines = fst_._get_src(ln, col, end_ln, end_col, True)

    else:
        lines = fst_._get_src(ln, col, end_ln, 0x7fffffffffffffff, True)

        ec = end_col if end_ln != ln else end_col - col

        if m := _re_stmt_tail.match(l := lines[-1], ec):
            lines[-1] = l[:m.end(1)]
        else:
            lines[-1] = l[:ec]

    end = f'{c.clr_loc}<*END*{c.end_loc}'
    iter_lines = iter(lines)
    l = next(iter_lines)
    e = end if l[-1:].isspace() else ''

    if not col:
        l = f'{c.end_loc}{c.clr_src}{l}{c.end_src}'
    elif l[:1].isspace():
        l = f'{" " * (col - 1)}>{c.end_loc}{c.clr_src}{l}{c.end_src}'
    else:
        l = f'{" " * col}{c.end_loc}{c.clr_src}{l}{c.end_src}'

    linefunc(f'{c.clr_loc}{ln:<{width}}: {l}{e}{eol}')

    for cln, l in zip(range(ln + 1, end_ln + 1), iter_lines, strict=True):
        e = end if l[-1:].isspace() else ''

        linefunc(f'{c.clr_loc}{cln:<{width}}:{c.end_loc} {c.clr_src}{l}{c.end_src}{e}{eol}')


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
    sind = st.sind
    c = st.color
    tail = self._repr_tail(st.loc)
    tail = f' {c.clr_loc}-{tail}{c.end_loc}' if tail else ''

    if not st.src:  # noop
        pass

    elif isinstance(ast, (stmt, ExceptHandler, match_case)):  # src = 'stmt' or 'node'
        loc = self.bloc

        if isinstance(ast, ASTS_BLOCK):
            ln, col, _, _ = loc
            end_ln, end_col, _, _ = self._loc_block_header_end()

            _dump_lines(self, st, ln, col, end_ln, end_col + 1, True)

        else:
            _dump_lines(self, st, *loc, True)

    elif not isinstance(ast, (mod, _ExceptHandlers, _match_cases)):
        if st.src == 'node':
            if not (parent := self.parent) or not isinstance(parent.a, Expr):
                if loc := self.loc:
                    _dump_lines(self, st, *loc, False)

        elif st.src == 'stmt' and not self.parent:  # if putting statements but root is not statement or mod then just put root src and no src below
            st.src = None

            if loc := self.loc:
                _dump_lines(self, st, *loc, False)

    if not st.expand:
        if isinstance(ast, Name):
            st.linefunc(f'{cind}{prefix}{c.clr_ast}Name{c.end_ast} {_dump_prim(ast.id, c)} '
                        f'{c.clr_ast}{ast.ctx.__class__.__name__}{c.end_ast}{tail}{st.eol}')

            return

        if isinstance(ast, Constant):
            kind = '' if ast.kind is None else f' {c.clr_field}.kind{c.end_field} {_dump_prim(ast.kind, c)}'
            prim = _dump_prim_long(ast.value, st, cind + sind)

            if prim.startswith('\n'):
                st.linefunc(f'{cind}{prefix}{c.clr_ast}Constant{c.end_ast}{kind}{tail}{prim}{st.eol}')
            else:
                st.linefunc(f'{cind}{prefix}{c.clr_ast}Constant{c.end_ast} {prim}{kind}{tail}{st.eol}')

            return

        if isinstance(ast, MatchSingleton):
            st.linefunc(f'{cind}{prefix}{c.clr_ast}MatchSingleton{c.end_ast} {_dump_prim(ast.value, c)}'
                        f'{tail}{st.eol}')

            return

    st.linefunc(f'{cind}{prefix}{c.clr_ast}{ast.__class__.__name__}{c.end_ast}{tail}{st.eol}')

    for name, child in iter_fields(ast):
        is_list = isinstance(child, list)

        if not st.expand:
            if not st.full and child is None and not isinstance(ast, MatchSingleton):
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

            if name == 'args' and isinstance(child, arguments):
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
                        and isinstance(ast, (Constant, MatchSingleton)))))):
            continue

        if not is_list:
            st.linefunc(f'{cind}{sind}{c.clr_field}.{name}{c.end_field}{st.eol}')

            if isinstance(child, AST):
                _dump_node(child.f, st, cind + sind * 2, '')

            else:
                ind = f'{cind}{sind * 2}'

                st.linefunc(f'{ind}{_dump_prim_long(child, st, ind)}{st.eol}')

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
                    st.linefunc(f'{cind}{st.lind}{c.clr_field}{i}]{c.end_field} {ast!r}{st.eol}')


# ----------------------------------------------------------------------------------------------------------------------

def new_empty_tuple(*, from_: fst.FST | None = None) -> fst.FST:
    ast = Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return fst.FST(ast, ['()'], None, from_=from_)


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
        if not frag.src.startswith('#') or (not is_lineno and comments == 'none'):
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


def get_trivia_params(
    trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None = None, neg: bool = False
) -> tuple[
    Literal['none', 'all', 'block'], bool | int, bool, Literal['none', 'all', 'block', 'line'], bool | int, bool
]:
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


def get_option_overridable(overridable_option: str, override_option: str, options: Mapping[str, Any] = {}) -> object:
    """Get an option value which can be overridden with another option, unless that option is `None`.

    This is a bit tricky because in this case if `override_option` is explicitly passed in `options` with a value of
    `None` then its value will NOT be gotten from the globals options and instead `overridable_option` will be returned
    from `options` or global. If it is not present but `None` in global options then `overridable_option` is returned
    again.
    """

    if (o := options.get(override_option, get_option_overridable)) is not None:  # get_option_overridable is sentinel
        if o is not get_option_overridable:
            return o

        if (o := fst.FST.get_option(override_option)) is not None:
            return o

    return fst.FST.get_option(overridable_option, options)


def clip_src_loc(self: fst.FST, ln: int, col: int, end_ln: int, end_col: int) -> tuple[int, int, int, int]:
    """Clip location to valid source coordinates and verify that the end does not precede the start."""

    lines = self.root._lines
    last_ln = len(lines) - 1

    if ln > end_ln or ((end_ln == ln) and col > end_col):  # we do this before clip so that out-of-bounds coordinates are still validated wrt common sense as wrong order may indicate other bugs
        raise ValueError('end location cannot precede start location')

    if ln < 0:
        ln = 0
    elif ln > last_ln:
        ln = last_ln

    if col < 0:
        col = 0
    elif col > (len_line := len(lines[ln])):
        col = len_line

    if end_ln < 0:
        end_ln = 0
    elif end_ln > last_ln:
        end_ln = last_ln

    if end_col < 0:
        end_col = 0
    elif end_col > (len_line := len(lines[end_ln])):
        end_col = len_line

    return ln, col, end_ln, end_col


def fixup_one_index(len_: int, idx: int) -> int:
    """Convert negative indices in range to len()+idx and verify index in range."""

    if idx < 0:
        idx += len_

    if not (0 <= idx < len_):
        raise IndexError('index out of range')

    return idx


def fixup_slice_indices(len_: int, start: int | Literal['end'] | None, stop: int | None) -> tuple[int, int]:
    """Clip slice indices to slice range allowing first negative range to map into positive range. Greater negative
    indices clip to 0."""

    if start is None:
        start = 0
    elif start == 'end' or start > len_:
        start = len_
    elif start < 0:
        start = max(0, start + len_)

    if stop is None or stop > len_:
        stop = len_
    elif stop < 0:
        stop = max(0, stop + len_)

    if stop < start:
        raise ValueError('start index must precede stop index')

    return start, stop


def fixup_field_body(ast: AST, field: str | None, only_list: bool) -> tuple[str, 'AST']:
    """Get `AST` member list for specified `field` or default if `field=None`."""

    if field is None:
        if (field := _DEFAULT_AST_FIELD.get(ast.__class__, fixup_field_body)) is fixup_field_body:  # fixup_field_body is sentinel
            raise ValueError(f"{ast.__class__.__name__} has no default body field")

    if field.startswith('_'):  # virtual field like Dict._all
        return field, []

    if (body := getattr(ast, field, fixup_field_body)) is fixup_field_body:
        raise ValueError(f"{ast.__class__.__name__} has no field '{field}'")

    if only_list and not isinstance(body, list):
        raise ValueError(f'expecting a list field {ast.__class__.__name__}.{field}')

    return field, body


# ----------------------------------------------------------------------------------------------------------------------
# FST class methods

def _repr_tail(self: fst.FST, loc: bool = True) -> str:
    if loc:
        try:
            loc = self.loc
        except Exception:  # maybe in middle of operation changing locations and lines
            loc = '????'

        # self._touchall(False, True, True)  # for debugging because we may have cached locs which would not have otherwise been cached during execution

    tail = ' ROOT' if self.is_root else ''

    return f'{tail} {loc[0]},{loc[1]}..{loc[2]},{loc[3]}' if loc else tail


def _dump(self: fst.FST, st: nspace, src_plus: bool = False) -> None:
    if not src_plus:
        st.src_ln = 0x7fffffffffffffff
    elif is_root := self.is_root:
        st.src_ln = 0
    else:
        st.src_ln = self.ln or 0  # if self doesn't have a location then we put everything since its a low level node anyway

    _dump_node(self, st, '', '')

    if src_plus and is_root:  # put any trailing lines if putting at root
        _dump_lines(self, st, len(self.root._lines), 0, 0, 0, None)


def _is_parenthesizable(self: fst.FST) -> bool:
    """Whether `self` is parenthesizable with grouping parentheses or not. All `pattern`s and almost all `expr`s which
    are not themselves inside `pattern`s and are not themselves `Slice`, `FormattedValue` or `Interpolation`.

    **Note:** `Starred` returns `True` even though the `Starred` itself is not parenthesizable but rather its child.

    **Returns:**
    - `bool`: Whether is syntactically legal to add grouping parentheses or not. Can always be forced.

    **Examples:**

    >>> FST('i + j')._is_parenthesizable()  # expr
    True

    >>> FST('{a.b: c, **d}', 'pattern')._is_parenthesizable()
    True

    >>> FST('a:b:c')._is_parenthesizable()  # Slice
    False

    >>> FST('for i in j')._is_parenthesizable()  # comprehension
    False

    >>> FST('a: int, b=2')._is_parenthesizable()  # arguments
    False

    >>> FST('a: int', 'arg')._is_parenthesizable()
    False

    >>> FST('key="word"', 'keyword')._is_parenthesizable()
    False

    >>> FST('a as b', 'alias')._is_parenthesizable()
    False

    >>> FST('a as b', 'withitem')._is_parenthesizable()
    False
    """

    if not isinstance(a := self.a, expr):
        return isinstance(a, pattern)

    if isinstance(a, (Slice, FormattedValue, Interpolation)):
        return False

    while self := self.parent:
        if not isinstance(a := self.a, expr):
            if isinstance(a, pattern):
                return False

            break

    return True


def _is_parenthesized_tuple(self: fst.FST) -> bool | None:
    """Whether `self` is a parenthesized `Tuple` or not, or not a `Tuple` at all.

    **Returns:**
    - `True` if is parenthesized `Tuple`, `False` if is unparenthesized `Tuple`, `None` if is not `Tuple` at all.

    **Examples:**

    >>> FST('1, 2')._is_parenthesized_tuple()
    False

    >>> FST('(1, 2)')._is_parenthesized_tuple()
    True

    >>> print(FST('1')._is_parenthesized_tuple())
    None
    """

    return self._is_delimited_seq() if isinstance(self.a, Tuple) else None


def _is_delimited_matchseq(self: fst.FST) -> Literal['', '[]', '()'] | None:
    r"""Whether `self` is a delimited `MatchSequence` or not (parenthesized or bracketed), or not a `MatchSequence`
    at all.

    **Returns:**
    - `None`: If is not `MatchSequence` at all.
    - `''`: If is undelimited `MatchSequence`.
    - `'()'` or `'[]'`: Is delimited with these delimiters.

    **Examples:**

    >>> FST('match a:\n  case 1, 2: pass').cases[0].pattern._is_delimited_matchseq()
    ''

    >>> FST('match a:\n  case [1, 2]: pass').cases[0].pattern._is_delimited_matchseq()
    '[]'

    >>> FST('match a:\n  case (1, 2): pass').cases[0].pattern._is_delimited_matchseq()
    '()'

    >>> print(FST('match a:\n  case 1: pass').cases[0].pattern._is_delimited_matchseq())
    None
    """

    if not isinstance(self.a, MatchSequence):
        return None

    ln, col, _, _ = self.loc
    lpar = self.root._lines[ln][col : col + 1]  # could be end of line

    if lpar == '(':
        return '()' if self._is_delimited_seq('patterns', '()') else ''
    if lpar == '[':
        return '[]' if self._is_delimited_seq('patterns', '[]') else ''

    return ''


def _is_except_star(self: fst.FST) -> bool | None:
    """Whether `self` is an `except*` `ExceptHandler` or a normal `ExceptHandler`, or not and `ExceptHandler` at
    all.

    **Returns:**
    - `True` if is `except*` `ExceptHandler`, `False` if is normal `ExceptHandler`, `None` if is not `ExceptHandler`
    at all.

    **Examples:**

    >>> import sys

    >>> if sys.version_info[:2] >= (3, 11):
    ...     print(FST('try: pass\\nexcept* Exception: pass').handlers[0]._is_except_star())
    ... else:
    ...     print(True)
    True

    >>> if sys.version_info[:2] >= (3, 11):
    ...     print(FST('try: pass\\nexcept Exception: pass').handlers[0]._is_except_star())
    ... else:
    ...     print(False)
    False

    >>> print(FST('i = 1')._is_except_star())
    None
    """

    if not isinstance(self.a, ExceptHandler):
        return None

    ln, col, end_ln, end_col = self.loc

    return next_frag(self.root._lines, ln, col + 6, end_ln, end_col).src.startswith('*')  # something must be there


def _is_expr_arglike(self: fst.FST) -> bool | None:
    """Is an argument-like expression which can only appear in a `Call.args` or `ClassDef.bases` (or a `.slice`
    `Tuple.elts` in py 3.11+) list, e.g. `*not a`, `*a or b`.

    **Returns:**
    - `True`: Is an unparenthesized arglike expression, `*not a`, `*a or b`.
    - `None`: Is a parenthesized arglike expression, `*(not a)`, `*(a or b)`.
    - `False`: Is a not an arglike expression, `*x`, `y`, `i = 1`, etc...
    """

    if not isinstance(ast := self.a, Starred) or isinstance(child := ast.value, Tuple):  # we assume any Tuple child of a Starred is intrinsically parenthesized, otherwise it is invalid
        return False

    child_type = child.op.__class__ if (child_cls := child.__class__) in (BoolOp, BinOp, UnaryOp) else child_cls

    if not precedence_require_parens_by_type(child_type, Starred, 'value'):
        return False

    return None if child.f.pars().n else True


def _is_empty_set_call(self: fst.FST) -> bool:
    """Whether `self` is an empty `set()` call.

    **Examples:**

    >>> FST('{1}')._is_empty_set_call()
    False

    >>> FST('set()')._is_empty_set_call()
    True

    >>> FST('frozenset()')._is_empty_set_call()
    False

    >>> FST('{*()}')._is_empty_set_call()
    False
    """

    return (isinstance(ast := self.a, Call) and not ast.args and not ast.keywords and
            isinstance(func := ast.func, Name) and func.id == 'set' and isinstance(func.ctx, Load))


def _is_empty_set_star(self: fst.FST) -> bool:
    """Whether `self` is an empty `Set` from an empty `Starred` `Constant` sequence, recognized are `{*()}`, `{*[]}`
    and `{*{}}`.

    **Examples:**

    >>> FST('{1}')._is_empty_set_star()
    False

    >>> FST('{*()}')._is_empty_set_star()
    True

    >>> FST('set()')._is_empty_set_star()
    False
    """

    return (isinstance(ast := self.a, Set) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and
            ((isinstance(v := e0.value, (Tuple, List)) and not v.elts) or (isinstance(v, Dict) and not v.keys)))


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

    return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(parenta := parent.a, Call) and
            not parenta.keywords and len(parenta.args) == 1)


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

    return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(self.a, GeneratorExp) and
            isinstance(parenta := parent.a, Call) and not parenta.keywords and len(parenta.args) == 1)


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
    """

    if not (parent := self.parent):
        return False

    if isinstance(parenta := parent.a, MatchValue):
        self = parent

    return ((parent := self.parent) and self.pfield.name == 'patterns' and
            isinstance(parenta := parent.a, MatchClass) and not parenta.kwd_patterns and len(parenta.patterns) == 1)


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

        if isinstance(parenta := parent.a, (FormattedValue, Interpolation)):
            return (self.pfield.name == 'value' and
                    (fs := parenta.format_spec) and fs.col_offset == col_offset and fs.lineno == lineno)

        self = parent

    return False


def _is_arguments_empty(self: fst.FST) -> bool:
    """Is this `arguments` node empty?"""

    # assert isinstance(self.a, arguments)

    return not ((a := self.a).posonlyargs or a.args or a.vararg or a.kwonlyargs or a.kwarg)


def _is_delimited_seq(self: fst.FST, field: str = 'elts', delims: str | tuple[str, str] = '()') -> bool:
    """Whether `self` is a delimited (parenthesized or bracketed) sequence of `field` or not. Makes sure the entire
    node is surrounded by a balanced pair of delimiters. Functions as `_is_parenthesized_tuple()` if already know is a
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

    return isinstance(a := self.a, Slice) or (isinstance(a, Tuple) and
                                                any(isinstance(e, Slice) for e in a.elts))


def _has_Starred(self: fst.FST) -> bool:
    """Whether self is a `Starred` or a `Tuple`, `List` or `Set` which directly contains any `Starred`.

    **Examples:**

    >>> FST('*a')._has_Starred()
    True

    >>> FST('1, *a')._has_Starred()  # Tuple contains at least one Starred
    True
    """

    return isinstance(a := self.a, Starred) or (isinstance(a, (Tuple, List, Set)) and
                                                any(isinstance(e, Starred) for e in a.elts))


def _maybe_add_line_continuations(self: fst.FST, whole: bool = False, del_comments: bool = True) -> bool:
    """Check if `self` needs them and if so add line continuations to make parsable.

    **Parameters:**
    - `whole`: Whether to check whole source (and add line continuations to, only if at root). Otherwise will just
        check and modify lines that this node lives on.
    - `del_comments`: If `True` then will delete comments which prevent line continuations from making the source
        parsable. If `False` then will raise an error if this is encountered.

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

    for ln in lns:
        m = re_line_end_cont_or_comment.match(l := lines[ln], end_cols.get(ln, 0))

        if not (g := m.group(1)):
            lines[ln] = bistr(l + ('\\' if not l or l[-1:].isspace() else ' \\'))

        elif g.startswith('#'):
            if not del_comments:
                raise NodeError('cannot add line continuation to line that ends with comment')

            # maybe just delete line if contains only comment?

            c = c + 1 if (c := re_empty_space.search(l, 0, cc := m.start(1)).start()) else cc
            lines[ln] = bistr(l[:c] + '\\')

    return True


def _maybe_del_separator(
    self: fst.FST,
    ln: int,
    col: int,
    force: bool = False,
    end_ln: int | None = None,
    end_col: int | None = None,
    sep: str = ',',
) -> bool:
    """Maybe delete a separator if present. Can be always deleted or allow function to decide aeshtetically. We
    specifically don't use `pars()` here because is meant to be used where the element is being modified and may not be
    valid for that. This is meant to work with potential closing parentheses present after (`ln`, `col`) and expects
    that if the separator is present in the span that it is the valid separator we are looking for. If no separator
    found then nothing is deleted.

    **Parameters:**
    - (`ln`, `col`): Location of start of span.
    - `force`: Whether to always delete a separator if it is present or maybe leave based on aesthetics.
    - (`end_ln`, `end_col`): Location of end of span, otherwise gotten from end of `self`.
    - `sep`: Separator to delete, usually comma.

    **Returns:**
    - `bool`: Whether a separator was deleted or not
    """

    if end_ln is None:
        _, _, end_ln, end_col = self.loc

    lines = self.root._lines

    if not (pos := next_find(lines, ln, col, end_ln, end_col, sep)):
        return False

    sep_ln, sep_col = pos
    sep_end_col = sep_col + len(sep)
    sep_on_end_ln = sep_ln == end_ln
    line_sep = lines[sep_ln]

    if not (frag := next_frag(lines, sep_ln, sep_end_col, sep_ln, end_col if sep_on_end_ln else 0x7fffffffffffffff,
                              True, True)):  # nothing on rest of line after separator?
        sep_end_col = end_col if sep_on_end_ln else len(line_sep)

    elif frag.src[0] not in '#\\':  # not a comment or line continuation, closing delimiter or next element if being used that way
        sep_end_col = frag.col

    elif not force:  # comment or line continuation follows, leave separator for aesthetic reasons if allowed
        return False

    del_col = re_empty_space.search(line_sep, col if sep_ln == ln else 0, sep_col).start()

    self._put_src(None, sep_ln, del_col or sep_col, sep_ln, sep_end_col, True)

    return True


def _maybe_ins_separator(
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

        while src.startswith(')'):
            ln = cln
            col = ccol = ccol + 1
            src = src[1:]

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


def _maybe_add_singleton_tuple_comma(self: fst.FST, is_par: bool | None = None) -> None:
    """Maybe add comma to tuple if is singleton and comma not already there, parenthesization not checked or taken
    into account. `self.a` must be a `Tuple`."""

    # assert isinstance(self.a, Tuple)

    if len(elts := self.a.elts) == 1:
        self._maybe_ins_separator((f := elts[0].f).end_ln, f.end_col, False, self.end_ln,
                                  self.end_col - (self._is_delimited_seq() if is_par is None else is_par))


def _maybe_fix_joined_alnum(
    self: fst.FST, ln: int, col: int, end_ln: int | None = None, end_col: int | None = None
) -> None:
    """Check if location(s) `lines[ln][col-1 : col+1]` and optionally `lines[end_ln][end_col-1 : end_col+1] is / are
    alphanumeric and if so separate them with a space. This is for operations that may inadvertantly join two distinct
    elements into a single parsable alphanumeric, e.g. `for i inb, 2: pass`.

    `self` doesn't matter, call on any node in tree.
    """

    lines = self.root._lines

    if end_ln is not None:
        if end_col and re_alnumdot_alnum.match(lines[end_ln], end_col - 1):  # make sure last element didn't wind up joining two alphanumerics, and if so separate
            self._put_src([' '], end_ln, end_col, end_ln, end_col, False)

    if col and re_alnumdot_alnum.match(lines[ln], col - 1):  # make sure first element didn't wind up joining two alphanumerics, and if so separate
        self._put_src([' '], ln, col, ln, col, False)


def _maybe_fix_undelimited_seq(self: fst.FST, body: list[AST], delims: str = '()') -> bool:
    """Fix undelimited `Tuple` or `MatchSequence` if needed. Don't call on delimited sequence."""

    # assert isinstance(self.a, (Tuple, MatchSequence))

    if not body:  # if is empty then just need to delimit
        lines = self.root._lines
        ln, col, end_ln, end_col = self.loc

        if not next_frag(lines, ln, col, end_ln, end_col, True):  # if no comments in tuple area then just replace with '()'
            self._put_src([delims], ln, col, end_ln, end_col, True, False)  # WARNING! `tail=True` may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized tuple starts, but haven't found a case where this can happen

        else:  # otherwise preserve comments by parenthesizing whole area
            ldelim, rdelim = delims

            if end_col and (l := lines[end_ln]).endswith(' ', 0, end_col):
                lines[end_ln] = bistr(f'{l[:end_col - 1]}{rdelim}{l[end_col:]}')
            else:
                self._put_src([rdelim], end_ln, end_col, end_ln, end_col, True)

            if (l := lines[ln]).startswith(' ', col):
                lines[ln] = bistr(f'{l[:col]}{ldelim}{l[col + 1:]}')
            else:
                self._put_src([ldelim], ln, col, ln, col, False, False)

        return True

    ln, col, end_ln, end_col = self.loc
    encpar = None  # cached call to self._is_enclosed_in_parents()

    if ((end_ln != ln
         and not self._is_enclosed_or_line(pars=False)
         and not (encpar := self._is_enclosed_in_parents())
        )  # could have line continuations
        or (any(isinstance(e, NamedExpr) and not e.f.pars().n for e in body))  # yeah, this is fine in parenthesized tuples but not in naked ones, only applies to tuples and not MatchSequence obviously
    ):
        self._delimit_node(delims=delims)

        return True

    eln, ecol, _, _ = body[0].f.pars()
    lines = self.root._lines

    if ecol != col or eln != ln:  # to be super safe we enforce that an undelimited node must start at the first element
        self._put_src(None, ln, col, eln, ecol, False)

        ln, col, end_ln, end_col = self.loc

    _, _, eend_ln, eend_col = body[-1].f.pars()

    if comma := next_find(lines, eend_ln, eend_col, end_ln, end_col, ','):  # could be closing grouping pars before comma
        eend_ln, eend_col = comma
        eend_col += 1

    if end_col != eend_col or end_ln != eend_ln:  # need to update end position because it had some whitespace after which will not be enclosed by delimiters
        if not (encpar or self._is_enclosed_in_parents()):
            self._put_src(None, eend_ln, eend_col, end_ln, end_col, True)  # be safe, nuke everything after last element since we won't have delimiters or parent to delimit it

        else:  # enclosed in parents so we can leave crap at the end
            a = self.a
            cur_end_lineno = a.end_lineno
            cur_end_col_offset = a.end_col_offset
            end_lineno = a.end_lineno = eend_ln + 1
            end_col_offset = a.end_col_offset = lines[eend_ln].c2b(eend_col)

            self._touch()

            while ((self := self.parent) and
                    getattr(a := self.a, 'end_col_offset', -1) == cur_end_col_offset and
                    a.end_lineno == cur_end_lineno
            ):  # update parents, only as long as they end exactly where we end
                a.end_lineno = end_lineno
                a.end_col_offset = end_col_offset

                self._touch()

            else:
                if self:
                    self._touchall(True, True, False)

        _, _, end_ln, end_col = self.loc

    self._maybe_fix_joined_alnum(ln, col, end_ln, end_col)

    return False


def _maybe_fix_tuple(self: fst.FST, is_par: bool | None = None) -> bool:
    """
    **Returns:**
    - `bool`: Whether the tuple is parenthesized or not (after the fix, regardless of if fix was done or not).
    """

    # assert isinstance(self.a, Tuple)

    if is_par is None:
        is_par = self._is_delimited_seq()

    if body := self.a.elts:
        self._maybe_add_singleton_tuple_comma(is_par)

    if not is_par:
        return self._maybe_fix_undelimited_seq(body)

    return is_par


def _maybe_fix_arglike(self: fst.FST, options: Mapping[str, Any]) -> None:
    """Parenthesize `self` if is arglike expression according to `options`."""

    if get_option_overridable('pars', 'pars_arglike', options) and self._is_expr_arglike():
        self._parenthesize_grouping()


def _maybe_fix_arglikes(self: fst.FST, options: Mapping[str, Any]) -> None:
    """Parenthesize any arglike expressions in `self` which is assumed to be a `Tuple` according to `options`."""

    # assert isinstance(self.a, Tuple)

    if get_option_overridable('pars', 'pars_arglike', options):
        for e in self.a.elts:
            if (f := e.f)._is_expr_arglike():
                f._parenthesize_grouping()


def _maybe_fix_elif(self: fst.FST) -> None:
    """If source at self is an `elif` instead of an `if` then convert it to `if`."""

    # assert isinstance(self.a, If)

    lines = self.root._lines
    ln, col, _, _ = self.loc

    if lines[ln].startswith('elif', col):
        self._put_src(None, ln, col, ln, col + 2, False)


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

    ast = self.a

    ln, col, end_ln, end_col = self.whole_loc if whole and self.is_root else self.loc

    if is_star_child := isinstance(ast, Starred) and star_child:
        ln, col, _, _ = self.loc
        col += 1
        self = ast.value.f

    self._put_src([')'], end_ln, end_col, end_ln, end_col, True, True, self, offset_excluded=False)

    if is_star_child:  # because of maybe `whole`, otherwise could just do it using _put_src(..., offset_excluded=is_star_child) above
        ast.end_lineno = end_ln + 1
        ast.end_col_offset = self.root._lines[end_ln].c2b(end_col) + 1

    self._offset(*self._put_src(['('], ln, col, ln, col, False, False, self, offset_excluded=False))


def _unparenthesize_grouping(self: fst.FST, shared: bool | None = True, *, star_child: bool = True) -> bool:
    """Remove grouping parentheses from anything if present. Just remove text parens around node and everything between
    them and node adjusting parent locations but not the node itself.

    **Parameters:**
    - `shared`: Whether to allow merge of parentheses into shared single call argument generator expression or not. If
        `None` then will attempt to unparenthesize any enclosing parentheses, whether they belong to this node or not
        (meant for internal use).
    - `star_child`: `Starred` expressions cannot be parenthesized, so when this is `True` the parentheses are removed
        from the `value` child.

    **Returns:**
    - `bool`: Whether parentheses were removed or not (only removed if present to begin with and removable).
    """

    if isinstance(self.a, Starred) and star_child:
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
    delimiters which are passed in and extend the range of the node to include those delimiters.

    **WARNING!** No checks are done so make sure to call where it is appropriate!

    **Parameters:**
    - `whole`: If at root then delimit whole source instead of just node.
    """

    # assert isinstance(self.a, Tuple)

    ln, col, end_ln, end_col = self.whole_loc if whole and self.is_root else self.loc

    self._put_src([delims[1]], end_ln, end_col, end_ln, end_col, True, False, self)

    lines = self.root._lines
    a = self.a
    a.end_lineno = end_ln + 1  # yes this can change
    a.end_col_offset = lines[end_ln].c2b(end_col + 1)  # can't count on this being set by put_src() because end of `whole` could be past end of tuple

    self._offset(*self._put_src([delims[0]], ln, col, ln, col, False, False, self), self_=False)

    a.lineno = ln + 1
    a.col_offset = lines[ln].c2b(col)  # ditto on the `whole` thing


def _undelimit_node(self: fst.FST, field: str = 'elts') -> bool:
    """Unparenthesize or unbracketize a parenthesized / bracketed `Tuple` or `MatchSequence`, shrinking node location
    for the removed delimiters. Will not undelimit an empty `Tuple` or `MatchSequence`. Removes everything between the
    delimiters and the actual sequence, e.g. `(  1, 2  # yay \\n)` -> `1, 2`.

    **WARNING!** No checks are done so make sure to call where it is appropriate! Does not check to see if node is
    properly paren/bracketized so make sure of this before calling!

    **Returns:**
    - `bool`: Whether delimiters were removed or not (they may not be for an empty tuple).
    """

    # assert isinstance(self.a, Tuple)

    if not (body := getattr(self.a, field, None)):
        return False

    lines = self.root._lines
    ln, col, end_ln, end_col = self.loc
    _, _, bn_end_ln, bn_end_col = body[-1].f.loc

    if comma := next_find(lines, bn_end_ln, bn_end_col, end_ln, end_col, ','):  # need to leave trailing comma if its there
        bn_end_ln, bn_end_col = comma
        bn_end_col += 1

    else:  # when no trailing comma need to make sure par is not separating us from an alphanumeric on either side, and if so then insert a space at the end before deleting the right par
        if end_col >= 2 and _re_delim_close_alnums.match(lines[end_ln], end_col - 2):
            self._put_src(' ', end_ln, end_col, end_ln, end_col, False, self)

    head_alnums = col and _re_delim_open_alnums.match(lines[ln], col - 1)  # if open has alnumns on both sides then insert space there too

    self._put_src(None, bn_end_ln, bn_end_col, end_ln, end_col, True, self)
    self._put_src(None, ln, col, (e0 := body[0].f).ln, e0.col, False)

    if head_alnums:  # but put after delete par to keep locations same
        self._put_src(' ', ln, col, ln, col, False)

    return True


def _trim_delimiters(self: fst.FST) -> None:
    """Remove the delimiters of `self` and everything before and after them. `self` must be a container with single
    character delimiters like a parenthesized `Tuple`, `List`, `Set`, `Dict`, `MatchSequence` or `MatchMapping`."""

    # assert self.is_root

    lines = self._lines
    ast = self.a
    ln, col, end_ln, end_col = self.loc
    col += 1
    end_col -= 1
    ast.col_offset += 1
    ast.end_col_offset -= 1

    self._offset(ln, col, -ln, -lines[ln].c2b(col))

    lines[end_ln] = bistr(lines[end_ln][:end_col])
    lines[ln] = bistr(lines[ln][col:])

    del lines[end_ln + 1:], lines[:ln]
