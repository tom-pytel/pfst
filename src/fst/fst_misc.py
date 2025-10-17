"""Misc common `FST` class and standalone methods.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

import re
from ast import iter_fields, walk
from math import log10
from typing import Any, Callable, Literal, Mapping

from . import fst

from .asttypes import (
    ASTS_BLOCK,
    AST,
    Call,
    Constant,
    Dict,
    ExceptHandler,
    Expr,
    GeneratorExp,
    If,
    List,
    Load,
    MatchClass,
    MatchSequence,
    MatchValue,
    Name,
    NamedExpr,
    Set,
    Slice,
    Starred,
    Tuple,
    arguments,
    match_case,
    mod,
    operator,
    stmt,
)

from .astutil import OPSTR2CLS_AUG, bistr, pat_alnum, re_alnumdot_alnum

from .common import (
    NodeError, srcwpos, nspace,
    re_empty_space, re_line_end_cont_or_comment,
    next_frag, next_find, prev_find, next_delims,
)

from .locations import loc_block_header_end

__all__ = [
    'new_empty_tuple', 'new_empty_set_star', 'new_empty_set_call', 'new_empty_set_curlies', 'get_trivia_params',
    'get_option_overridable',
    ]


_re_stmt_tail          = re.compile(r'\s*(?:;\s*)?')
_re_one_space_or_end   = re.compile(r'\s|$')

_re_par_open_alnums    = re.compile(rf'[{pat_alnum}.][(][{pat_alnum}]')
_re_par_close_alnums   = re.compile(rf'[{pat_alnum}.][)][{pat_alnum}]')
_re_delim_open_alnums  = re.compile(rf'[{pat_alnum}.][([][{pat_alnum}]')
_re_delim_close_alnums = re.compile(rf'[{pat_alnum}.][)\]][{pat_alnum}]')


def _dump_lines(fst_: fst.FST, linefunc: Callable, ln: int, col: int, end_ln: int, end_col: int, eol: str = '',
                is_full_stmt: bool = False) -> None:
    width = int(log10(len(fst_.root._lines) - 1 or 1)) + 1

    if is_full_stmt:
        lines = fst_._get_src(ln, col, end_ln, 0x7fffffffffffffff, True)

        if not _re_stmt_tail.match(l := lines[-1], end_col):
            l = l[:end_col]
        elif l[-1:].isspace():
            l += '<*END*'

    else:
        lines = fst_._get_src(ln, col, end_ln, end_col, True)

        if (l := lines[-1])[-1:].isspace():
            l += '<*END*'

    lines[-1] = l
    l = lines[0]

    if col:
        if l[0].isspace():
            lines[0] = f'{" " * (col - 1)}>{l}'
        else:
            lines[0] = ' ' * col + l

    for i, l in zip(range(ln, end_ln + 1), lines, strict=True):
        linefunc(f'{i:<{width}}: {l}{eol}')


# ----------------------------------------------------------------------------------------------------------------------

def new_empty_tuple(*, from_: fst.FST | None = None) -> fst.FST:
    ast = Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=2)

    return fst.FST(ast, ['()'], from_=from_)


def new_empty_set_star(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None, as_fst: bool = True,
                       ) -> fst.FST | AST:
    src = ['{*()}']
    ast = Set(elts=[Starred(value=Tuple(elts=[], ctx=Load(), lineno=lineno, col_offset=col_offset+2,
                                        end_lineno=lineno, end_col_offset=col_offset+4),
                            ctx=Load(),
                            lineno=lineno, col_offset=col_offset+1, end_lineno=lineno, end_col_offset=col_offset+4)],
              lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return fst.FST(ast, src, from_=from_) if as_fst else (ast, src)


def new_empty_set_call(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None, as_fst: bool = True,
                       ) -> fst.FST:
    src = ['set()']
    ast = Call(func=Name(id='set', ctx=Load(),
                         lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+3),
               args=[], keywords=[],
               lineno=lineno, col_offset=col_offset, end_lineno=lineno, end_col_offset=col_offset+5)

    return fst.FST(ast, src, from_=from_) if as_fst else (ast, src)


def new_empty_set_curlies(lineno: int = 1, col_offset: int = 0, *, from_: fst.FST | None = None) -> fst.FST | AST:
    ast = Set(elts=[], lineno=lineno, col_offset=col_offset, end_lineno=lineno,
              end_col_offset=col_offset + 2)

    return fst.FST(ast, ['{}'], from_=from_)


def get_trivia_params(trivia: bool | str | tuple[bool | str | int | None, bool | str | int | None] | None = None,
                      neg: bool = False,
                      ) -> tuple[Literal['none', 'all', 'block'],
                                 bool | int,
                                 bool,
                                 Literal['none', 'all', 'block', 'line'],
                                 bool | int,
                                 bool,
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
    """Get an option value which can be overridden with another option (even global as long as it is not `None`)."""

    if (o := fst.FST.get_option(override_option, options)) is not None:
        return o

    return fst.FST.get_option(overridable_option, options)


# ----------------------------------------------------------------------------------------------------------------------
# FST class methods

def _repr_tail(self: fst.FST, loc: bool = True) -> str:
    if loc:
        try:
            loc = self.loc
        except Exception:  # maybe in middle of operation changing locations and lines
            loc = '????'

    self._touchall(False, True, True)  # for debugging because we may have cached locs which would not have otherwise been cached during execution

    tail = ' ROOT' if self.is_root else ''

    return f'{tail} {loc[0]},{loc[1]}..{loc[2]},{loc[3]}' if loc else tail


def _dump(self: fst.FST, st: nspace, cind: str = '', prefix: str = '') -> None:
    ast = self.a
    tail = self._repr_tail(st.loc)
    sind = st.sind

    if not st.src:  # noop
        pass

    elif isinstance(ast, (stmt, ExceptHandler, match_case)):  # src = 'stmt' or 'all'
        loc = self.bloc

        if isinstance(ast, ASTS_BLOCK):
            ln, col, _, _ = loc
            end_ln, end_col, _, _ = loc_block_header_end(self)

            _dump_lines(self, st.linefunc, ln, col, end_ln, end_col + 1, st.eol)

        else:

            _dump_lines(self, st.linefunc, *loc, st.eol, True)

    elif not isinstance(ast, mod):
        if st.src == 'all':
            if not (parent := self.parent) or not isinstance(parent.a, Expr):
                if loc := self.loc:
                    _dump_lines(self, st.linefunc, *loc, st.eol)

        elif st.src == 'stmt' and not self.parent:  # if putting statements but root is not statement or mod then just put root src and no src below
            st.src = None

            if loc := self.loc:
                _dump_lines(self, st.linefunc, *loc, st.eol)

    if not st.expand:
        if isinstance(ast, Name):
            st.linefunc(f'{cind}{prefix}Name {ast.id!r} {ast.ctx.__class__.__qualname__}{" -" * bool(tail)}{tail}'
                        f'{st.eol}')

            return

        if isinstance(ast, Constant):
            if ast.kind is None:
                st.linefunc(f'{cind}{prefix}Constant {ast.value!r}{" -" * bool(tail)}{tail}{st.eol}')
            else:
                st.linefunc(f'{cind}{prefix}Constant {ast.value!r} kind={ast.kind!r}{" -" * bool(tail)}{tail}{st.eol}')

            return

    st.linefunc(f'{cind}{prefix}{ast.__class__.__qualname__}{" -" * bool(tail)}{tail}{st.eol}')

    for name, child in iter_fields(ast):
        is_list = isinstance(child, list)

        if not st.expand:
            if child is None and not st.full:
                continue

            if name == 'ctx':
                st.linefunc(f'{cind}{sind}.{name} '
                            f'{child.__class__.__qualname__ if isinstance(child, AST) else child}{st.eol}')

                continue

            if (name in ('type', 'id', 'attr', 'module', 'arg', 'vararg', 'kwarg', 'rest', 'format_spec',
                         'name', 'asname', 'value', 'left', 'right', 'operand', 'returns', 'target',
                         'annotation', 'iter', 'test','exc', 'cause', 'msg', 'elt', 'key', 'func',
                         'slice', 'lower', 'upper', 'step', 'guard', 'context_expr', 'optional_vars',
                         'cls', 'bound', 'default_value', 'pattern', 'subject',
                         'type_comment', 'lineno', 'tag', 'op',
                         'simple', 'level', 'conversion', 'str', 'is_async', 'lineno') or
                (not is_list and name in ('body', 'orelse'))
            ):
                if isinstance(child, AST):
                    child.f._dump(st, cind + sind, f'.{name} ')
                else:
                    st.linefunc(f'{cind}{sind}.{name} {child!r}{st.eol}')

                continue

            if name == 'args' and isinstance(child, arguments):
                if child.posonlyargs or child.args or child.vararg or child.kwonlyargs or child.kwarg:
                    child.f._dump(st, cind + sind, '.args ')

                    continue

                elif not st.full:
                    continue

        if st.full or (child != []):
            st.linefunc(f'{cind}{sind}.{name}{f"[{len(child)}]" if is_list else ""}{st.eol}')

        if is_list:
            for i, ast in enumerate(child):
                if isinstance(ast, AST):
                    ast.f._dump(st, cind + st.lind, f'{i}] ')  # ast.f._dump(st, cind + sind * 2, f'{i}] ')
                else:
                    st.linefunc(f'{cind}{st.lind}{i}] {ast!r}{st.eol}')  # st.linefunc(f'{sind}{sind}{cind}{i}] {ast!r}{st.eol}')

        elif isinstance(child, AST):
            child.f._dump(st, cind + sind * 2)
        else:
            st.linefunc(f'{cind}{sind}{sind}{child!r}{st.eol}')


def _is_parenthesized_tuple(self: fst.FST) -> bool | None:
    """Whether `self` is a parenthesized `Tuple` or not, or not a `Tuple` at all.

    **Returns:**
    - `True` if is parenthesized `Tuple`, `False` if is unparenthesized `Tuple`, `None` if is not `Tuple` at all.

    **Examples:**
    ```py
    >>> FST('1, 2')._is_parenthesized_tuple()
    False

    >>> FST('(1, 2)')._is_parenthesized_tuple()
    True

    >>> print(FST('1')._is_parenthesized_tuple())
    None
    ```
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
    ```py
    >>> FST('match a:\n  case 1, 2: pass').cases[0].pattern._is_delimited_matchseq()
    ''

    >>> FST('match a:\n  case [1, 2]: pass').cases[0].pattern._is_delimited_matchseq()
    '[]'

    >>> FST('match a:\n  case (1, 2): pass').cases[0].pattern._is_delimited_matchseq()
    '()'

    >>> print(FST('match a:\n  case 1: pass').cases[0].pattern._is_delimited_matchseq())
    None
    ```
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
    ```py
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
    ```
    """

    if not isinstance(self.a, ExceptHandler):
        return None

    ln, col, end_ln, end_col = self.loc

    return next_frag(self.root._lines, ln, col + 6, end_ln, end_col).src.startswith('*')  # something must be there


def _is_empty_set_call(self: fst.FST) -> bool:
    """Whether `self` is an empty `set()` call.

    **Examples:**
    ```py
    >>> FST('{1}')._is_empty_set_call()
    False

    >>> FST('set()')._is_empty_set_call()
    True

    >>> FST('frozenset()')._is_empty_set_call()
    False

    >>> FST('{*()}')._is_empty_set_call()
    False
    ```
    """

    return (isinstance(ast := self.a, Call) and not ast.args and not ast.keywords and
            isinstance(func := ast.func, Name) and func.id == 'set' and isinstance(func.ctx, Load))


def _is_empty_set_star(self: fst.FST) -> bool:
    """Whether `self` is an empty `Set` from an empty `Starred` `Constant` sequence, recognized are `{*()}`, `{*[]}`
    and `{*{}}`.

    **Examples:**
    ```py
    >>> FST('{1}')._is_empty_set_star()
    False

    >>> FST('{*()}')._is_empty_set_star()
    True

    >>> FST('set()')._is_empty_set_star()
    False
    ```
    """

    return (isinstance(ast := self.a, Set) and len(elts := ast.elts) == 1 and isinstance(e0 := elts[0], Starred) and
            ((isinstance(v := e0.value, (Tuple, List)) and not v.elts) or (isinstance(v, Dict) and not v.keys)))


def _is_elif(self: fst.FST) -> bool | None:
    r"""Whether `self` is an `elif` or not, or not an `If` at all.

    **Returns:**
    - `True` if is `elif` `If`, `False` if is normal `If`, `None` if is not `If` at all.

    **Examples:**
    ```py
    >>> FST('if 1: pass\nelif 2: pass').orelse[0]._is_elif()
    True

    >>> FST('if 1: pass\nelse:\n  if 2: pass').orelse[0]._is_elif()
    False

    >>> print(FST('if 1: pass\nelse:\n  i = 2').orelse[0]._is_elif())
    None
    ```
    """

    return self.root._lines[(loc := self.loc).ln].startswith('elif', loc.col) if isinstance(self.a, If) else None


def _is_solo_class_base(self: fst.FST) -> bool | None:
    """Whether `self` is a solo `ClassDef` base in list without any keywords, or not a class base at all.

    **Returns:**
    - `True` if is solo class base, `False` if is class base, but not solo and `None` if is not class base at all.

    **Examples:**
    ```py
    >>> FST('class cls(b1): pass').bases[0]._is_solo_class_base()
    True

    >>> FST('class cls(b1, b2): pass').bases[0]._is_solo_class_base()
    False

    >>> FST('class cls(b1, meta=m): pass').bases[0]._is_solo_class_base()
    False

    >>> print(FST('class cls(b1, meta=m): pass').keywords[0]._is_solo_class_base())
    None
    ```
    """

    if not (parent := self.parent) or self.pfield.name != 'bases':
        return None

    return len((parenta := parent.a).bases) == 1 and not parenta.keywords


def _is_solo_call_arg(self: fst.FST) -> bool:
    """Whether `self` is a solo `Call` non-keyword argument.

    **Examples:**
    ```py
    >>> FST('call(a)').args[0]._is_solo_call_arg()
    True

    >>> FST('call(a, b)').args[0]._is_solo_call_arg()
    False

    >>> FST('call(i for i in range(3))').args[0]._is_solo_call_arg()
    True
    ```
    """

    return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(parenta := parent.a, Call) and
            not parenta.keywords and len(parenta.args) == 1)


def _is_solo_call_arg_genexp(self: fst.FST) -> bool:
    """Whether `self` is the dreaded solo call non-keyword argument generator expression in `sum(i for i in a)`.
    This function doesn't say if it shares its parentheses or not, so it could still be `sum((i for i in a))` or
    even `sum(((i for i in a)))`. To differentiate that see `pars(shared=False)`.

    **Examples:**
    ```py
    >>> FST('call(i for i in range(3))').args[0]._is_solo_call_arg_genexp()
    True

    >>> FST('call((i for i in range(3)))').args[0]._is_solo_call_arg_genexp()
    True

    >>> FST('call((i for i in range(3)), b)').args[0]._is_solo_call_arg_genexp()
    False

    >>> FST('call(a)').args[0]._is_solo_call_arg_genexp()
    False
    ```
    """

    return ((parent := self.parent) and self.pfield.name == 'args' and isinstance(self.a, GeneratorExp) and
            isinstance(parenta := parent.a, Call) and not parenta.keywords and len(parenta.args) == 1)


def _is_solo_matchcls_pat(self: fst.FST) -> bool:
    r"""Whether `self` is a solo `MatchClass` non-keyword pattern. The solo `Constant` held by a `MatchValue`
    qualifies as `True` for this check if the `MatchValue` does.

    **Examples:**
    ```py
    >>> (FST('match a:\n  case cls(a): pass')
    ...  .cases[0].pattern.patterns[0]._is_solo_matchcls_pat())
    True

    >>> (FST('match a:\n  case cls(a, b): pass')
    ...  .cases[0].pattern.patterns[0]._is_solo_matchcls_pat())
    False
    ```
    """

    if not (parent := self.parent):
        return False

    if isinstance(parenta := parent.a, MatchValue):
        self = parent

    return ((parent := self.parent) and self.pfield.name == 'patterns' and
            isinstance(parenta := parent.a, MatchClass) and not parenta.kwd_patterns and len(parenta.patterns) == 1)


def _is_augop(self: fst.FST) -> bool | None:
    """Whether `self` is an augmented `operator` or not, or not an `operator` at all.

    **Returns:**
    - `True` if is augmented `operator`, `False` if non-augmented `operator` and `None` if is not `operator` at all.

    **Examples:**
    ```py
    >>> FST('+')._is_augop()
    False

    >>> FST('+=')._is_augop()
    True

    >>> repr(FST('~')._is_augop())
    'None'
    ```
    """

    return None if not isinstance(self.a, operator) else self._get_src(*self.loc) in OPSTR2CLS_AUG


def _has_Slice(self: fst.FST) -> bool:
    """Whether self is a `Slice` or a `Tuple` which directly contains any `Slice`.

    **Examples:**
    ```py
    >>> FST('a:b:c', 'expr_slice')._has_Slice()
    True

    >>> FST('1, d:e', 'expr_slice')._has_Slice()  # Tuple contains at least one Slice
    True

    >>> # b is in the .slice field but is not a Slice or Slice Tuple
    >>> FST('a[b]').slice._has_Slice()
    False
    ```
    """

    return isinstance(a := self.a, Slice) or (isinstance(a, Tuple) and
                                                any(isinstance(e, Slice) for e in a.elts))


def _has_Starred(self: fst.FST) -> bool:
    """Whether self is a `Starred` or a `Tuple`, `List` or `Set` which directly contains any `Starred`.

    **Examples:**
    ```py
    >>> FST('*a')._has_Starred()
    True

    >>> FST('1, *a')._has_Starred()  # Tuple contains at least one Starred
    True
    ```
    """

    return isinstance(a := self.a, Starred) or (isinstance(a, (Tuple, List, Set)) and
                                                any(isinstance(e, Starred) for e in a.elts))


def _is_arguments_empty(self: fst.FST) -> bool:
    """Is this `arguments` node empty?"""

    # assert isinstance(self.a, arguments)

    return not ((a := self.a).posonlyargs or a.args or a.vararg or a.kwonlyargs or a.kwarg)


def _is_delimited_seq(self: fst.FST, field: str = 'elts', delims: str | tuple[str, str] = '()') -> bool:
    """Whether `self` is a delimited (parenthesized or bracketed) sequence of `field` or not. Makes sure the entire
    node is surrounded by a balanced pair of delimiters. Functions as `_is_parenthesized_tuple()` if already know is a
    Tuple. Other use is for `MatchSequence`, whether parenthesized or bracketed."""

    ldelim, rdelim = delims
    lines = self.root._lines

    self_ln, self_col, self_end_ln, self_end_col = self.loc

    if not lines[self_end_ln].startswith(rdelim, self_end_col - 1):
        return False

    if not (asts := getattr(self.a, field)):
        return True  # return True if no children because assume '()' in this case

    if not lines[self_ln].startswith(ldelim, self_col):
        return False

    f0_ln, f0_col, f0_end_ln, f0_end_col = asts[0].f.loc

    if f0_col == self_col and f0_ln == self_ln:
        return False

    _, _, fn_end_ln, fn_end_col = asts[-1].f.loc

    if fn_end_col == self_end_col and fn_end_ln == self_end_ln:
        return False

    # dagnabit! have to count and balance delimiters around first element

    self_end_col -= 1  # because in case of singleton tuple for sure there is a comma between end of first element and end of tuple, so at worst we exclude either the tuple closing paren or a comma, otherwise we exclude non-tuple closing delimiter

    ldelims = len(next_delims(lines, self_ln, self_col, f0_ln, f0_col, ldelim))  # yes, we use next_delims() to count opening delimiters because we know conditions allow it
    rdelims = len(next_delims(lines, f0_end_ln, f0_end_col, self_end_ln, self_end_col, rdelim))

    return ldelims > rdelims


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

    if self._is_enclosed_or_line(whole=whole, out_lns=(lns := set())):
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


def _maybe_del_separator(self: fst.FST, ln: int, col: int, force: bool = False,
                         end_ln: int | None = None, end_col: int | None = None, sep: str = ',') -> bool:
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


def _maybe_ins_separator(self: fst.FST, ln: int, col: int, space: bool,
                         end_ln: int | None = None, end_col: int | None = None, sep: str = ',',
                         exclude: Literal[True] | fst.FST | None = True) -> srcwpos | None:
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

    if offset_excluded := exclude is True:
        exclude = self

    lines = self.root._lines

    while frag := next_frag(lines, ln, col, end_ln, end_col):  # find comma or something else, skipping close parens
        cln, ccol, src = frag

        for c in src:
            ccol += 1

            if c == ')':
                ln = cln
                col = ccol

            elif c != sep:
                break

            else:
                if space and ((cln == end_ln and ccol == end_col) or not _re_one_space_or_end.match(lines[cln], ccol)):
                    self._put_src([' '], cln, ccol, cln, ccol, True, exclude=exclude, offset_excluded=offset_excluded)

                    return srcwpos(cln, ccol, ' ')

                return None

        else:
            continue

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

    if (elts := self.a.elts) and len(elts) == 1:
        self._maybe_ins_separator((f := elts[0].f).end_ln, f.end_col, False, self.end_ln,
                                  self.end_col - (self._is_delimited_seq() if is_par is None else is_par))


def _maybe_fix_joined_alnum(self: fst.FST, ln: int, col: int, end_ln: int | None = None, end_col: int | None = None,
                            ) -> None:
    """Check if location(s) `lines[ln][col-1 : col+1]` and optionally `lines[end_ln][end_col-1 : end_col+1] is / are
    alphanumeric and if so separate them with a space. This is for operations that may inadvertantly join two distinct
    elements into a single parsable alphanumeric, e.g. `for i inb, 2: pass`."""

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
    encpar = None

    if ((end_ln != ln and not self._is_enclosed_or_line(pars=False) and
         not (encpar := self._is_enclosed_in_parents())) or  # could have line continuations
        (any(isinstance(e, NamedExpr) and not e.f.pars().n for e in body))  # yeah, this is fine in parenthesized tuples but not in naked ones, only applies to tuples and not MatchSequence obviously
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

    if fst.FST.get_option('pars', options) and fst.FST.get_option('pars_arglike', options):
        if self.is_expr_arglike:
            self.par()


def _maybe_fix_arglikes(self: fst.FST, options: Mapping[str, Any]) -> None:
    """Parenthesize any arglike expressions in `self` which is assumed to be a `Tuple` according to `options`."""

    # assert isinstance(self.a, Tuple)

    if fst.FST.get_option('pars', options) and fst.FST.get_option('pars_arglike', options):
        for e in self.a.elts:
            if (f := e.f).is_expr_arglike:
                f.value.par()  # will be a Starred so we just go for .value


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
        ast.end_col_offset = self.root._lines[end_ln].b2c(end_col) + 1

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
        self = self.value

    pars_loc = self.pars(shared=None if shared is None else True)

    if shared:
        shared = self._is_solo_call_arg_genexp()

    if not getattr(pars_loc, 'n', 0) and not shared:
        return False

    ln, col, end_ln, end_col = self.bloc
    pln, pcol, pend_ln, pend_col = pars_loc

    if shared:  # special case merge solo argument GeneratorExp parentheses with call argument parens
        lines = self.root._lines
        _, _, cend_ln, cend_col = self.parent.func.loc
        pln, pcol = prev_find(lines, cend_ln, cend_col, pln, pcol, '(')  # must be there
        pend_ln, pend_col = next_find(lines, pend_ln, pend_col, len(lines) - 1, len(lines[-1]), ')')  # ditto
        pend_col += 1

        self._put_src(None, end_ln, end_col, pend_ln, pend_col, True, self)
        self._put_src(None, pln, pcol, ln, col, False)

    else:  # in all other case we need to make sure par is not separating us from an alphanumeric on either side, and if so then just replace that par with a space
        lines = self.root._lines

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

    ln, col, end_ln, end_col = self.loc
    lines = self.root._lines

    if comma := next_find(self.root._lines, en_end_ln := (en := body[-1].f).end_ln, en_end_col := en.end_col,
                          end_ln, end_col, ','):  # need to leave trailing comma if its there
        en_end_ln, en_end_col = comma
        en_end_col += 1

    else:  # when no trailing comma need to make sure par is not separating us from an alphanumeric on either side, and if so then insert a space at the end before deleting the right par
        if end_col >= 2 and _re_delim_close_alnums.match(lines[end_ln], end_col - 2):
            self._put_src(' ', end_ln, end_col, end_ln, end_col, False, self)

    head_alnums = col and _re_delim_open_alnums.match(lines[ln], col - 1)  # if open has alnumns on both sides then insert space there too

    self._put_src(None, en_end_ln, en_end_col, end_ln, end_col, True, self)
    self._put_src(None, ln, col, (e0 := body[0].f).ln, e0.col, False)

    if head_alnums:  # but put after delete par to keep locations same
        self._put_src(' ', ln, col, ln, col, False)

    return True
