"""Low level common data and functions that are not part of or aware of the FST class."""

import re
import sys
from ast import parse as ast_parse
from functools import wraps
from math import log10
from typing import Callable, ForwardRef, Literal, NamedTuple, Iterable

from .asttypes import (
    AST, AnnAssign, Assert, Assign, AsyncFor, AsyncFunctionDef, AsyncWith, Attribute, AugAssign, Await, BoolOp, Call,
    ClassDef, Compare, Constant, Delete, Dict, DictComp, ExceptHandler, Expr, Expression, For, FormattedValue,
    FunctionDef, GeneratorExp, Global, If, Import, ImportFrom, Interactive, JoinedStr, Lambda, List, ListComp, Match,
    MatchAs, MatchMapping, MatchOr, MatchSequence, MatchSingleton, MatchValue, Module, Name, NamedExpr, Nonlocal, Raise,
    Return, Set, SetComp, Starred, Subscript, Try, Tuple, UnaryOp, While, With, Yield, YieldFrom, alias, arg, arguments,
    boolop, cmpop, comprehension, expr, expr_context, keyword, match_case, mod, operator, stmt, unaryop, withitem,
    TypeAlias, TryStar, TemplateStr, Interpolation,
)
from .astutil import constant, bistr


try:
    from typing import Self
except ImportError:  # for py 3.10
    Self = ForwardRef('FST')

__all__ = [
    'NodeError',
    'astfield',
    'fstloc',
    'fstlocns',
    'srcwpos',
    'nspace',
    'shortstr',
    'pyver',
    'shortstr',
    'next_frag',
    'prev_frag',
    'next_find',
    'prev_find',
    'next_find_re',
    'next_delims',
    'prev_delims',
    'leading_trivia',
    'trailing_trivia',
    'ParamsOffset',
    'params_offset',
    'swizzle_getput_params',
    'fixup_field_body',
    'fixup_one_index',
    'fixup_slice_indices',
    'multiline_str_continuation_lns',
    'multiline_fstr_continuation_lns',
    'continuation_to_uncontinued_lns',
]


PYVER  = sys.version_info[:2]
PYLT11 = PYVER < (3, 11)
PYLT12 = PYVER < (3, 12)
PYLT13 = PYVER < (3, 13)
PYLT14 = PYVER < (3, 14)
PYGE11 = PYVER >= (3, 11)
PYGE12 = PYVER >= (3, 12)
PYGE13 = PYVER >= (3, 13)
PYGE14 = PYVER >= (3, 14)

EXPRISH                  = (expr, comprehension, arguments, arg, keyword)  # can be in expression chain (have expressions above)
EXPRISH_ALL              = EXPRISH + (expr_context, boolop, operator, unaryop, cmpop)
STMTISH                  = (stmt, ExceptHandler, match_case)  # always in lists, cannot be inside multilines
STMTISH_OR_MOD           = STMTISH + (mod,)
STMTISH_OR_STMTMOD       = STMTISH + (Module, Interactive)
BLOCK                    = (FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If, With, AsyncWith, Match,
                            Try, TryStar, ExceptHandler, match_case)
BLOCK_OR_MOD             = BLOCK + (mod,)
SCOPE                    = (FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp, GeneratorExp)
SCOPE_OR_MOD             = SCOPE + (mod,)
NAMED_SCOPE              = (FunctionDef, AsyncFunctionDef, ClassDef)
NAMED_SCOPE_OR_MOD       = NAMED_SCOPE + (mod,)
ANONYMOUS_SCOPE          = (Lambda, ListComp, SetComp, DictComp, GeneratorExp)

HAS_DOCSTRING            = NAMED_SCOPE_OR_MOD

STMTISH_FIELDS           = frozenset(('body', 'orelse', 'finalbody', 'handlers', 'cases'))

re_empty_line_start      = re.compile(r'[ \t]*')     # start of completely empty or space-filled line (from start pos, start of line indentation)
re_empty_line            = re.compile(r'[ \t]*$')    # completely empty or space-filled line (from start pos, start of line indentation)
re_comment_line_start    = re.compile(r'[ \t]*#')    # empty line preceding a comment
re_line_continuation     = re.compile(r'[^#]*\\$')   # line continuation with backslash not following a comment start '#' (from start pos, assumed no asts contained in line)
re_line_trailing_space   = re.compile(r'.*?(\s*)$')  # location of trailing whitespace at the end of a line
re_empty_space           = re.compile(r'\s*$')       # completely empty or space-filled line (from start pos, start of line indentation, any space, not just line indenting space)

re_oneline_str           = re.compile(r'(?:b|r|rb|br|u|)  (?:  \'(?:\\.|[^\\\'])*?\'  |  "(?:\\.|[^\\"])*?"  )',   # I f'])*?\'ng hate these!
                                     re.VERBOSE | re.IGNORECASE)
re_contline_str_start    = re.compile(r'(?:b|r|rb|br|u|)  (\'|")', re.VERBOSE | re.IGNORECASE)
re_contline_str_end_sq   = re.compile(r'(?:\\.|[^\\\'])*?  \'', re.VERBOSE)
re_contline_str_end_dq   = re.compile(r'(?:\\.|[^\\"])*?  "', re.VERBOSE)
re_multiline_str_start   = re.compile(r'(?:b|r|rb|br|u|)  (\'\'\'|""")', re.VERBOSE | re.IGNORECASE)
re_multiline_str_end_sq  = re.compile(r'(?:\\.|[^\\])*?  \'\'\'', re.VERBOSE)
re_multiline_str_end_dq  = re.compile(r'(?:\\.|[^\\])*?  """', re.VERBOSE)

re_empty_line_or_cont           = re.compile(r'[ \t]*(\\)?$')            # empty line or line continuation
re_empty_line_cont_or_comment   = re.compile(r'[ \t]*(\\|#.*)?$')        # empty line or line continuation or a pure comment line
re_line_end_cont_or_comment     = re.compile(r'.*?(\\|#.*)?$')           # line end line continuation or a comment, the first part is mostly meant to skip closing parentheses and separators, not expression stuff

re_next_src                     = re.compile(r'\s*([^\s#\\]+)')          # next non-space non-continuation non-comment code text, don't look into strings with this!
re_next_src_or_comment          = re.compile(r'\s*([^\s#\\]+|#.*)')      # next non-space non-continuation code or comment text, don't look into strings with this!
re_next_src_or_lcont            = re.compile(r'\s*([^\s#\\]+|\\$)')      # next non-space non-comment code including logical line end, don't look into strings with this!
re_next_src_or_comment_or_lcont = re.compile(r'\s*([^\s#\\]+|#.*|\\$)')  # next non-space non-continuation code or comment text including logical line end, don't look into strings with this!

_AST_DEFAULT_BODY_FIELD  = {cls: field for field, classes in [
    ('body',         (Module, Interactive, Expression, FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If,
                      With, AsyncWith, Try, TryStar, ExceptHandler, Lambda, match_case),),
    ('cases',        (Match,)),

    ('elts',         (Tuple, List, Set)),
    ('patterns',     (MatchSequence, MatchOr)),
    ('targets',      (Delete,)),  # , Assign)),
    ('type_params',  (TypeAlias,)),
    ('names',        (Import, ImportFrom, Global, Nonlocal)),
    ('ifs',          (comprehension,)),
    ('values',       (BoolOp, JoinedStr, TemplateStr)),
    ('generators',   (ListComp, SetComp, DictComp, GeneratorExp)),
    ('args',         (Call,)),  # potential conflict of default body with put to empty 'set()'

    # ('values',       (JoinedStr, TemplateStr)),  # values don't have locations in lower version pythons for JoinedStr
    # ('items',        (With, AsyncWith)),  # 'body' takes precedence

    # special cases, field names here only for checks to succeed, otherwise all handled programatically
    ('',             (Dict,)),
    ('',             (MatchMapping,)),
    ('',             (Compare,)),

    # other single value fields
    ('value',        (Expr, Return, Assign, TypeAlias, AugAssign, AnnAssign, NamedExpr, Await, Yield, YieldFrom,
                      FormattedValue, Interpolation, Constant, Attribute, Subscript, Starred, keyword, MatchValue,
                      MatchSingleton)),
    ('exc',          (Raise,)),
    ('test',         (Assert,)),
    ('operand',      (UnaryOp,)),
    ('id',           (Name,)),
    ('arg',          (arg,)),
    ('name',         (alias,)),
    ('context_expr', (withitem,)),
    ('pattern',      (MatchAs,)),
] for cls in classes}


class NodeError(Exception):
    """General FST node error."""

    rawable: bool  ; """Whether the operation that caused this error can be retried in raw mode."""

    def __init__(self, *args: object, rawable: bool = False):
        super().__init__(*args)

        self.rawable = rawable


class astfield(NamedTuple):
    """Name and optional index indicating a field location in an `AST` (or `FST`) node."""

    name: str                ; """The actual field name, a la "body", "value", "orelse", etc..."""
    idx:  int | None = None  ; """The index if the field is a list, else `None`."""

    def __repr__(self) -> str:
        return f'astfield({self.name!r})' if (idx := self.idx) is None else f'astfield({self.name!r}, {idx})'

    def get(self, parent: AST) -> AST | constant:
        """Get child node at this field in the given `parent`."""

        return getattr(parent, self.name) if self.idx is None else getattr(parent, self.name)[self.idx]

    def get_no_raise(self, parent: AST, default: AST | constant = False) -> AST | constant:
        """Get child node at this field in the given `parent`. Return `default` if not found instead of raising
        `AttributError` or `IndexError`, `False` works well because not normally found locations where `AST` nodes can
         reside in `AST` trees."""

        return (
            getattr(parent, self.name, default) if (idx := self.idx) is None else
            default if (body := getattr(parent, self.name, False)) is False or idx >= len(body) else
            body[idx])

    def set(self, parent: AST, child: AST) -> None:
        """Set `child` node at this field in the given `parent`."""

        if self.idx is None:
            setattr(parent, self.name, child)
        else:
            getattr(parent, self.name)[self.idx] = child


class fstloc(NamedTuple):
    """Full location span."""

    ln:      int  ; """Start line number."""
    col:     int  ; """Start column."""
    end_ln:  int  ; """End line number (inclusive)."""
    end_col: int  ; """End column (exclusive)."""

    bln      = property(lambda self: self.ln)       ; """Alias for `ln`."""  # for convenience
    bcol     = property(lambda self: self.col)      ; """Alias for `col`."""
    bend_ln  = property(lambda self: self.end_ln)   ; """Alias for `end_ln`."""
    bend_col = property(lambda self: self.end_col)  ; """Alias for `end_col`."""
    loc      = property(lambda self: self)          ; """To be able to use as `FST.loc`."""
    bloc     = loc                                  ; """Alias for `loc`."""

    is_FST   = False                                ; """@private"""  # for quick checks vs. `FST`

    def __repr__(self) -> str:
        ln, col, end_ln, end_col = self

        return f'fstloc({ln}, {col}, {end_ln}, {end_col})'


class fstlocns(fstloc):
    """Version of `fstloc` with a namespace, used for `pars().n`."""

    def __repr__(self) -> str:
        ln, col, end_ln, end_col = self
        ns                       = ', '.join(f'{n}={v!r}' for n, v in self.__dict__.items())

        return (f'fstlocns({ln}, {col}, {end_ln}, {end_col}, {ns})' if ns else
                f'fstlocns({ln}, {col}, {end_ln}, {end_col})')

    def __new__(cls, ln: int, col: int, end_ln: int, end_col: int, **kwargs):
        self = fstloc.__new__(cls, ln, col, end_ln, end_col)

        for name, value in kwargs.items():
            setattr(self, name, value)

        return self


class srcwpos(NamedTuple):
    """@private"""

    ln:  int
    col: int
    src: str


class nspace:
    """Simple namespace class used for several things.
    @private"""

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)


assert sys.version_info[0] == 3, 'pyver() assumes python major version 3'

_pyver_registry = {}  # {'__module__.__qualname__': [(func, (ge, lt) | unbound +ge | unbound -lt]), ...}
_pyver          = sys.version_info[1]  # just the minor version

def pyver(func: Callable | None = None, *, ge: int | None = None, lt: int | None = None, else_: Callable | None = None,
          ) -> Callable:
    """Decorator to restrict to a range of python versions. If the version of python does not match the parameters
    passed then will return a previously registered function that does match or `None` if no matching function. Yes we
    are only comparing minor version, if python goes to major 4 then this will be the least of your incompatibilities.

    **Parameters:**
    - `func`: The function (or class) being decorated.
    - `ge`: Minimum allowed version of python for this function. `None` for unbound below `lt`.
    - `lt`: Maximum NOT allowed version of python for this function (exclusive, LESS THAN THIS). `None` for unbound
        above `ge`. Both `ge` and `lt` cannot be `None` at the same time.
    - `else_`: If the current python version does not match the specified `ge` and `lt` then use this function instead
        of a standin which raises and error.

    @private
    """

    if ge is None and lt is None:
        raise ValueError("parameters 'ge' and 'lt' cannot both be None at the same time")

    if ge is not None and lt is not None and ge >= lt:
        raise ValueError(f"invalid 'ge' / 'lt' values, {ge} is not smaller than {lt}")

    def decorator(func: Callable) -> Callable:
        key = f'{func.__module__}.{func.__qualname__}'
        ret = func

        if ge is None:
            newver = (func, -lt)

            if _pyver >= lt:
                ret = else_

        elif lt is None:
            newver = (func, ge)

            if _pyver < ge:
                ret = else_

        else:
            newver = (func, (ge, lt))

            if not ge <= _pyver < lt:
                ret = else_

        if not (vers := _pyver_registry.get(key)):
            _pyver_registry[key] = vers = [newver]

        else:
            for verfunc, ver in vers:
                if isinstance(ver, tuple):
                    if (ge is None or ge < ver[1]) and (lt is None or lt > ver[0]):
                        raise ValueError(f"overlap with previously registered version range [3.{ver[0]}, 3.{ver[1]})")

                    if ver[0] <= _pyver < ver[1]:
                        ret = verfunc

                elif ver < 0:  # unbound less than minus this version
                    ver = -ver

                    if ge is None or ge < ver:
                        raise ValueError(f"overlap with previously registered version range < 3.{ver})")

                    if _pyver < ver:
                        ret = verfunc

                else:  # unbound greater than this version
                    if lt is None or lt > ver:
                        raise ValueError(f"overlap with previously registered version range >= 3.{ver})")

                    if ver <= _pyver:
                        ret = verfunc

            vers.append(newver)

        if ret is None:
            @wraps(func)
            def ret(*args: object, **kwargs) -> None:
                raise RuntimeError(f'missing version of {key} for this python version 3.{_pyver}')

        return ret

    return decorator if func is None else decorator(func)


def shortstr(s: str, maxlen: int = 64) -> str:
    """Return string of maximum length `maxlen`, shortening if necessary to "start .. [X chars] .. end".
    @private"""

    if (l := len(s)) <= maxlen:
        return s

    t = maxlen - 16 - (int(log10(l)) + 1)

    return f'{s[:(t+1)//2]} .. [{l} chars] .. {s[-(t//2):]}'


# def cls_names(cls: type | Sequence[type], last_separator: str = ' or ') -> str:
#     if isinstance(cls, Sequence):
#         return f'{", ".join(a.__name__ for a in cls[:-1])}{last_separator}{cls[-1].__name__}'

#     return cls.__name__


def next_frag(lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
              comment: bool = False, lcont: bool | None = False) -> srcwpos | None:
    """Get next fragment of source which may or may not include comments or line continuation backslashes. May be
    restricted to bound or further restricted to not exceed logical line. Assuming start pos not inside str or comment.
    The fragment is not necessarily AST stuff, it can be commas, colons, the 'try' keyword, etc... Fragments can include
    multiple AST nodes in return str if there are no spaces between them like 'a+b'.

    **Parameters:**
    - `comment`: Whether to return comments found, which will be the whole comment.
    - `lcont`: Whether to return line continuations found (backslash at end of line) if `True`, skip over them if
        `False`, or skip over them and restrict search to logical line `None`.

    @private
    """

    re_pat = (
        (re_next_src_or_comment_or_lcont if comment else re_next_src_or_lcont)
        if lcont else
        (re_next_src_or_comment if comment else re_next_src)
    )

    if end_ln == ln:
        return srcwpos(ln, m.start(1), m.group(1)) if (m := re_pat.match(lines[ln], col, end_col)) else None

    if lcont is not None:
        for i in range(ln, end_ln):
            if m := re_pat.match(lines[i], col):
                return srcwpos(i, m.start(1), m.group(1))

            col = 0

    else:  # only match to end of logical line, regardless of (end_ln, end_col) bound
        for i in range(ln, end_ln):
            if not (m := re_next_src_or_comment_or_lcont.match(lines[i], col)):
                return None

            if (s := m.group(1)).startswith('#'):
                return srcwpos(i, m.start(1), s) if comment else None

            if s != '\\':  # line continuations are always matched alone
                return srcwpos(i, m.start(1), s)

            col = 0

    if m := re_pat.match(lines[end_ln], 0, end_col):
        return srcwpos(end_ln, m.start(1), m.group(1))

    return None


def prev_frag(lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
              comment: bool = False, lcont: bool | None = False, *,
              state: list | None = None) -> srcwpos | None:
    """Get prev fragment of source which may or may not include comments or line continuation backslashes. May be
    restricted to bound or further restricted to not exceed logical line. Assuming start pos not inside str or comment.
    The fragment is not necessarily AST stuff, it can be commas, colons, the 'try' keyword, etc... Fragments can include
    multiple AST nodes in return str if there are no spaces between them like 'a+b'.

    **WARNING:** Make sure the starting position (`ln`, `col`) is not inside a string because that could give false
    positives for comments or line continuations. To this end, when searching for non-AST stuff, make sure the start
    position does not start INSIDE OF or BEFORE any valid ASTs.

    **Parameters:**
    - `comment`: Whether to return comments found, which will be the whole comment.
    - `lcont`: Whether to return line continuations found (backslash at end of line) if `True`, skip over them if
        `False`, or skip over them and restrict search to logical line `None`.
    - `state`: Can be used to cache walk but must only be used if the walk is sequentially backwards starting each time
        at the start position of the previously returned match.

    @private
    """

    re_pat = (
        (re_next_src_or_comment_or_lcont if comment else re_next_src_or_lcont)
        if lcont else
        (re_next_src_or_comment if comment else re_next_src)
    )

    if state is None:
        state = []

    def last_match(l: str, c: int, ec: int, p: re.Pattern) -> re.Match | None:
        if state:
            return state.pop()

        while m := p.match(l, c, ec):
            s = m.group(1)

            if (not comment and s.startswith('#')) or (lcont is False and s == '\\'):
                break

            c = m.end(1)

            state.append(m)

        return state.pop() if state else None

    if end_ln == ln:
        return srcwpos(ln, m.start(1), m.group(1)) if (m := last_match(lines[ln], col, end_col, re_pat)) else None

    if lcont is not None:
        for i in range(end_ln, ln, -1):
            if m := last_match(lines[i], 0, end_col, re_pat):
                return srcwpos(i, m.start(1), m.group(1))

            end_col = 0x7fffffffffffffff

        if m := last_match(lines[ln], col, end_col, re_pat):
            return srcwpos(ln, m.start(1), m.group(1))

    else:  # only match to start of logical line, regardless of (ln, col) bound
        cont_ln = end_ln

        if not (m := last_match(lines[end_ln], 0, end_col, re_next_src_or_comment_or_lcont)):
            end_ln  -= 1
            end_col  = 0x7fffffffffffffff

        else:
            if not (s := m.group(1)).startswith('#') or comment:
                return srcwpos(end_ln, m.start(1), m.group(1))

            end_col = m.start(1)

        i = end_ln + 1

        while (i := i - 1) >= ln:
            if not (m := last_match(lines[i], 0 if i > ln else col, end_col, re_next_src_or_comment_or_lcont)):
                if i < cont_ln:  # early out
                    return None

            elif (s := m.group(1)) == '\\':
                cont_ln  = ln
                end_col  = m.start(1)  # in case state was exhausted
                i       += 1  # to search same line again, possibly from new end_col

                continue

            elif s.startswith('#') or i < cont_ln:  # a comment here started a previous line and thus not a line continuation, or just no line continuation on new previous line
                return None
            else:
                return srcwpos(i, m.start(1), m.group(1))

            end_col = 0x7fffffffffffffff  # will take effect for previous line when state empties

    return None


def next_find(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, src: str, first: bool = False, *,
              comment: bool = False, lcont: bool | None = False) -> tuple[int, int] | None:
    """Find location of a string in the bound walking forward from the start. Returns `None` if string not found.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        end of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `next_frag()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `next_frag()`. Can stop search on line continuation if `first` is `True`.

    **Returns:**
    - `fstpos | None`: Location of start of found `src` or `None` if not found with the given parameters.

    @private
    """

    if first:
        if frag := next_frag(lines, ln, col, end_ln, end_col, comment, lcont):
            cln, ccol, csrc = frag

            if csrc.startswith(src):
                return cln, ccol

    else:
        while frag := next_frag(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = frag

            if (idx := csrc.find(src)) != -1:
                return ln, col + idx

            col += len(csrc)

    return None


def prev_find(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, src: str, first: bool = False, *,
              comment: bool = False, lcont: bool | None = False, state: list | None = None) -> tuple[int, int] | None:
    """Find location of a string in the bound walking backwards from the end. Returns `None` if string not found. If
    `comment` is `True` then `src` must match the START of the src comment found, not the tail like for non-comment
     strings found in order to be considered successful.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        start of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `prev_frag()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `prev_frag()`. Can stop search on line continuation if `first` is `True`.
    - `state`: The `state` parameter to `prev_frag()`. Be careful using this here and keep in mind its line caching
        functionality if changing search parameters.

    **Returns:**
    - `fstpos | None`: Location of start of found `src` or `None` if not found with the given parameters.

    @private
    """

    if first:
        if frag := prev_frag(lines, ln, col, end_ln, end_col, comment, lcont, state=state):
            ln, col, csrc = frag

            if comment and csrc.startswith('#'):
                if csrc.startswith(src):
                    return ln, col

            elif csrc.endswith(src):
                return ln, col + len(csrc) - len(src)

    else:
        if state is None:
            state = []

        while frag := prev_frag(lines, ln, col, end_ln, end_col, comment, lcont, state=state):
            end_ln, end_col, csrc = frag

            if comment and csrc.startswith('#'):
                if csrc.startswith(src):
                    return end_ln, end_col

            elif (idx := csrc.rfind(src)) != -1:
                return end_ln, end_col + idx

    return None


def next_find_re(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, pat: re.Pattern, first: bool = False,
                 *, comment: bool = False, lcont: bool | None = False) -> srcwpos | None:
    """Find location of a regex pattern in the bound walking forward from the start. Returns `None` if string not found.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        end of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `next_frag()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `next_frag()`. Can stop search on line continuation if `first` is `True`.

    **Returns:**
    - `srcwpos | None`: Location of start of `pat` and the string matching the pattern or `None` if not found with the
        given parameters.

    @private
    """

    if first:
        if frag := next_frag(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = frag

            if m := pat.match(csrc):
                return srcwpos(ln, col, m.group())

    else:
        while frag := next_frag(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = frag

            if m := pat.search(csrc):
                return srcwpos(ln, col + m.start(), m.group())

            col += len(csrc)

    return None


def next_delims(lines: list[str], end_ln: int, end_col: int, bound_end_ln: int, bound_end_col: int,
                delim: str = ')') -> list[tuple[int, int]]:
    """Return a list of the locations of closing parentheses (or any specified delimiter or character) starting at
    (`end_ln`, `end_col`) until the end of the bound. The locations of the delimiters will be AFTER the delimiter.
    The list includes (`end_ln`, `end_col`) as the first element. The list ends if a non `delim` character is
    encountered while searching forward.

    **Returns:**
    - `[(end_ln, end_col), (ln_end_par1, col_end_par1), (ln_end_par2, col_end_par2), ...]`

    @private
    """

    delims = [(end_ln, end_col)]

    while frag := next_frag(lines, end_ln, end_col, bound_end_ln, bound_end_col):
        ln, col, src = frag

        for c in src:
            if c != delim:
                break

            end_ln  = ln
            end_col = (col := col + 1)

            delims.append((end_ln, end_col))

        else:
            continue

        break

    return delims


def prev_delims(lines: list[str], bound_ln: int, bound_col: int, ln: int, col: int, delim: str = '(',
                ) -> list[tuple[int, int]]:
    """Return a list of the locations of opening parentheses (or any specified delimiter or character) starting at
    (`ln`, `col`) going backwards until the start of the bound. The list includes (`ln`, `col`) as the first
    element. The list ends if a non `par` character is encountered while searching backward.

    **Returns:**
    - `[(ln, col), (ln_par1, col_par1), (ln_par2, col_par2), ...]`

    @private
    """

    delims = [(ln, col)]
    state  = []

    while frag := prev_frag(lines, bound_ln, bound_col, ln, col, state=state):
        ln, col, src  = frag
        col          += len(src)

        for c in src[::-1]:
            if c != delim:
                break

            ln  = ln
            col = (col := col - 1)

            delims.append((ln, col))

        else:
            continue

        break

    return delims


def leading_trivia(lines: list[str], bound_ln: int, bound_col: int, ln: int, col: int,
                   comments: Literal['none', 'all', 'block'] | int, space: bool | int,
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

    indent    = l[:col]
    is_lineno = isinstance(comments, int)
    text_pos  = (ln, col)  # start of comments or start of element
    top_ln    = bound_ln + bool(bound_col)  # topmost possible line to be considered, min return location is (top_ln, 0)
    stop_ln   = comments if is_lineno and comments > top_ln else top_ln
    start_ln  = ln

    if comments == 'all':
        comments_ln = ln

        while (ln := ln - 1) >= stop_ln:
            if not (m := re_empty_line_cont_or_comment.match(lines[ln])):
                break

            if (g := m.group(1)) and g.startswith('#'):
                comments_ln = ln

        ln           += 1
        comments_pos  = (comments_ln, 0)

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


def trailing_trivia(lines: list[str], bound_end_ln: int, bound_end_col: int, end_ln: int, end_col: int,
                    comments: Literal['none', 'all', 'block', 'line'] | int, space: bool | int,
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
        bottom_ln     = past_bound_end_ln  # two past bottommost line to be considered, max return location is bound_end_pos

    else:
        bottom_ln     = bound_end_ln  # one past bottommost line to be considered, max return location is (bottom_ln, 0)

    stop_ln  = comments + 1 if is_lineno and comments < bottom_ln else bottom_ln
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

        space_ln  = comments_ln + min(space, end_ln - comments_ln)
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


class ParamsOffset(NamedTuple):
    """@private"""

    ln:          int  # position of offset, FST coords (starts at 0)
    col_offset:  int  # position of offset, byte offset (negative to indicate but value is abs(), positive would indicate character offset)
    dln:         int  # delta lines
    dcol_offset: int  # delta bytes

def params_offset(lines: list[bistr], put_lines: list[bistr], ln: int, col: int, end_ln: int, end_col: int,
                  ) -> ParamsOffset:
    """Calculate location and delta parameters for the `_offset()` function. The `col` parameter is calculated as a byte
    offset so that the `_offset()` function does not have to access the source at all.

    @private
    """

    dfst_ln     = len(put_lines) - 1
    dln         = dfst_ln - (end_ln - ln)
    dcol_offset = put_lines[-1].lenbytes - lines[end_ln].c2b(end_col)
    col_offset  = -lines[end_ln].c2b(end_col)

    if not dfst_ln:
        dcol_offset += lines[ln].c2b(col)

    return ParamsOffset(end_ln, col_offset, dln, dcol_offset)


def swizzle_getput_params(start: int | Literal['end'] | None, stop: int | None | Literal[False], field: str | None,
                          default_stop: Literal[False] | None,
                          ) -> tuple[int | Literal['end'] | None,int | None | Literal[False], str | None]:
    """Allow passing `stop` and `field` for get/put() functions positionally.

    @private
    """

    if isinstance(start, str) and start != 'end':
        return None, default_stop, start
    if isinstance(stop, str):
        return start, default_stop, stop

    return start, stop, field


def fixup_field_body(ast: AST, field: str | None = None, only_list: bool = True) -> tuple[str, 'AST']:
    """Get `AST` member list for specified `field` or default if `field=None`.

    @private
    """

    if not field:
        if (field := _AST_DEFAULT_BODY_FIELD.get(ast.__class__, fixup_field_body)) is fixup_field_body:  # fixup_field_body serves as sentinel
            raise ValueError(f"{ast.__class__.__name__} has no default body field")

        if not field:  # special case ''
            return '', []

    if (body := getattr(ast, field, fixup_field_body)) is fixup_field_body:
        raise ValueError(f"{ast.__class__.__name__} has no field '{field}'")

    if only_list and not isinstance(body, list):
        raise ValueError(f"cannot perform slice operations non-list field "
                         f"{ast.__class__.__name__}{f'.{field}' if field else ''}")

    return field, body


def fixup_one_index(len_: int, idx: int) -> int:
    """@private"""

    if not (0 <= ((idx := idx + len_) if idx < 0 else idx) < len_):
        raise IndexError('index out of range')

    return idx


def fixup_slice_indices(len_: int, start: int, stop: int) -> tuple[int, int]:
    """@private"""

    if start is None:
        start = 0

    elif start == 'end':
        start = len_

    elif start < 0:
        if (start := start + len_) < 0:
            start = 0

    elif start > len_:
        start = len_

    if stop is None:
        stop = len_

    elif stop < 0:
        if (stop := stop + len_) < 0:
            stop = 0

    elif stop > len_:
        stop = len_

    if stop < start:
        stop = start

    return start, stop


def multiline_str_continuation_lns(lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> list[int]:
    """Return the line numbers of a potentially multiline string `Constant` continuation lines (lines which should not
    be indented because they follow a newline inside triple quotes). The location passed MUST be from the `Constant`
    `AST` node or calculated to be the same, otherwise this function will fail.

    @private
    """


    # TODO: use tokenize?


    def walk_multiline(start_ln: int, end_ln: int, m: re.Match, re_str_end: re.Pattern) -> tuple[int, re.Match]:
        nonlocal lns, lines

        col = m.end()

        for ln in range(start_ln, end_ln + 1):
            if m := re_str_end.match(lines[ln], col):
                break

            col = 0

        else:
            raise RuntimeError('should not get here')

        lns.extend(range(start_ln + 1, ln + 1))

        return ln, m.end()

    lns = []

    if end_ln <= ln:
        return lns

    while True:
        if not (m := re_multiline_str_start.match(l := lines[ln], col)):
            if m := re_oneline_str.match(l, col):
                col = m.end()

            else:  # UGH! a line continuation string, pffft...
                m          = re_contline_str_start.match(l, col)
                re_str_end = re_contline_str_end_sq if m.group(1) == "'" else re_contline_str_end_dq
                ln, col    = walk_multiline(ln, end_ln, m, re_str_end)  # find end of multiline line continuation string

        else:
            re_str_end = re_multiline_str_end_sq if m.group(1) == "'''" else re_multiline_str_end_dq
            ln, col    = walk_multiline(ln, end_ln, m, re_str_end)  # find end of multiline string

        if ln == end_ln and col == end_col:
            break

        ln, col, _ = next_frag(lines, ln, col, end_ln, end_col)  # there must be a next one

    return lns


def multiline_fstr_continuation_lns(lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> list[int]:
    """Lets try to find non-indentable lines by incrementally attempting to parse parts of multiline f-string (or
    t-string).

    @private
    """


    # TODO: p3.12+ has locations for these which should allow no use of parse, use tokenize?
    # TODO: currently returns normal fstrs contained on line but with line continuation as continuation lines (this is not what is meant by the function name)


    lns = []

    if end_ln <= ln:
        return lns

    while True:
        ls = [lines[ln][col:].lstrip()]

        for cur_ln in range(ln + 1, end_ln + 1):
            try:
                ast_parse('\n'.join(ls))

            except SyntaxError:
                lns.append(cur_ln)
                ls.append(lines[cur_ln])

            else:
                break

        if (ln := cur_ln) >= end_ln:
            assert ln == end_ln

            break

        col = 0

    return lns


def continuation_to_uncontinued_lns(lns: Iterable[int], ln: int, col: int, end_ln: int, end_col: int, *,
                                     include_last: bool = False) -> set[int]:
    """Convert `Iterable` of lines which are continued from the immediately previous line into a list of lines which are
    not themselves continued below. If `lns` comes from the `_multiline_?str_*` functions then it does not include line
    continuations outside of the string and those lines will be returned as uncontinued.

    **Parameters:**
    - `include_last`: Whether to include the last line as an uncontinues line or not.

    **Returns:**
    - `set[int]`: Set of uncontinued lines in the given range.

    @private
    """

    out = set(range(ln, end_ln + include_last))

    out.difference_update(i - 1 for i in lns)

    return out
