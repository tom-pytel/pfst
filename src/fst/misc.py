"""Low level common data and functions that are not part of the FST class."""

import re
from ast import *
from math import log10
from typing import Any, ForwardRef, Literal, NamedTuple, TypeAlias, Union

try:
    from typing import Self
except ImportError:
    Self = ForwardRef('FST')

from .astutil import *
from .astutil import TypeAlias, TryStar, TemplateStr, type_param, Interpolation

__all__ = ['Code', 'Mode', 'NodeError', 'astfield', 'fstloc']


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

re_oneline_str           = re.compile(r'(?:b|r|rb|br|u|)  (?:  \'(?:\\.|[^\\\'])*?\'  |  "(?:\\.|[^\\"])*?"  )',   # I f'])*?\'ng hate these!
                                     re.VERBOSE | re.IGNORECASE)
re_contline_str_start    = re.compile(r'(?:b|r|rb|br|u|)  (\'|")', re.VERBOSE | re.IGNORECASE)
re_contline_str_end_sq   = re.compile(r'(?:\\.|[^\\\'])*?  \'', re.VERBOSE)
re_contline_str_end_dq   = re.compile(r'(?:\\.|[^\\"])*?  "', re.VERBOSE)
re_multiline_str_start   = re.compile(r'(?:b|r|rb|br|u|)  (\'\'\'|""")', re.VERBOSE | re.IGNORECASE)
re_multiline_str_end_sq  = re.compile(r'(?:\\.|[^\\])*?  \'\'\'', re.VERBOSE)
re_multiline_str_end_dq  = re.compile(r'(?:\\.|[^\\])*?  """', re.VERBOSE)
re_any_str_or_fstr_start = re.compile(r'(?:b|r|rb|br|u|f|t|)  (\'\'\'|\'|"""|")', re.VERBOSE | re.IGNORECASE)

re_empty_line_cont_or_comment   = re.compile(r'[ \t]*(\\|#.*)?$')        # empty line or line continuation or a pure comment line
re_line_end_cont_or_comment     = re.compile(r'.*?(\\|#.*)?$')           # line end line continuation or a comment

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


_GLOBALS = globals() | {'_GLOBALS': None}
# ----------------------------------------------------------------------------------------------------------------------

Code = Union['FST', AST, list[str], str]  ; """Code types accepted for put to `FST`."""

Mode = Literal[
    'all',
    'most',
    'min',
    'exec',
    'eval',
    'single',
    'stmtishs',
    'stmtish',
    'stmts',
    'stmt',
    'ExceptHandlers',
    'ExceptHandler',
    'match_cases',
    'match_case',
    'expr',
    'slice',
    'sliceelt',
    'callarg',
    'boolop',
    'operator',
    'binop',
    'augop',
    'unaryop',
    'cmpop',
    'comprehension',
    'arguments',
    'arguments_lambda',
    'arg',
    'keyword',
    'alias',
    'alias_dotted',
    'alias_star',
    'withitem',
    'pattern',
    'type_param',
] | type[AST]

"""Parse modes:

- `'all'`: Check all possible parse modes (from most likely to least). There is syntax overlap so certain types will
    never be returned, for example `TypeVar` is always shadowed by `AnnAssign`. Since this attempts many parses before
    failing it is slower to do so than other modes, though the most likely success is just as fast. Will never return an
    `Expression` or `Interactive`.
- `'most'`: This is mostly meant for use as the first step when parsing `'all'`. Attempt parse `stmtishs`. If only one
    element then return the element itself instead of the `Module`. If that element is an `Expr` then return the
    expression instead of the statement. If nothing present then return empty `Module`. Doesn't attempt any of the other
    parse modes to keep things quick, though will parse anything that can be parsed natively by `ast.parse()` (plus
    `ExpressionHandler` and `match_case`). If you want exhaustive attempts that will parse any `AST` source node the
    mode for that is `'all'`. Will never return an `Expression` or `Interactive`.
- `'min'`: Attempt parse minumum valid parsable code. If only one statement then return the statement itself instead of
    the `Module`. If that statement is an `Expr` then return the expression instead of the statement. If nothing present
    then return empty `Module`. Doesn't attempt any of the other parse modes which would not normally be parsable by
    python, just anything that can be parsed natively by `ast.parse()`.
- `'exec'`: Parse to a `Module`. Mostly same as passing `Module` type except that `Module` also parses anything that
    `FST` puts into `Module`s, like slices of normally non-parsable stuff.
- `'eval'`: Parse to an `Expression`. Same as passing `Expression` type.
- `'single'`: Parse to an `Interactive`. Same as passing `Interactive` type.
- `'stmtishs'`: Parse as zero or more of either `stmt`, `ExceptHandler` or `match_case` returned in a `Module`.
- `'stmtish'`: Parse as a single `stmt`, `ExceptHandler` or `match_case` returned as itself.
- `'stmts'`: Parse zero or more `stmt`s returned in a `Module`. Same as passing `'exec'`, but not `Module` as that can
    parse `FST` slices.
- `'stmt'`: Parse a single `stmt` returned as itself. Same as passing `stmt` type.
- `'ExceptHandlers'`: Parse zero or more `ExceptHandler`s returned in a `Module`.
- `'ExceptHandler'`: Parse as a single `ExceptHandler` returned as itself. Same as passing `ExceptHandler` type.
- `'match_cases'`: Parse zero or more `match_case`s returned in a `Module`.
- `'match_case'`: Parse a single `match_case` returned as itself. Same as passing `match_case` type.
- `'expr'`: "expression", parse a single `expr` returned as itself. This is differentiated from the following three
    modes by the handling of slices and starred expressions. In this mode `a:b` and `*not v` are syntax errors. Same as
    passing `expr` type.
- `'slice'`: "slice expression", same as `'expr'` except that in this mode `a:b` parses to a `Slice` and `*not v` parses
    to a single element tuple containing a starred expression `(*(not v),)`.
- `'sliceelt'`: "slice tuple element expression", same as `'expr'` except that in this mode `a:b` parses to a `Slice`
    and `*not v` parses to a starred expression `*(not v)`.
- `'callarg'`: "call argument expression", same as `'expr'` except that in this mode `a:b` is a syntax error and
    `*not v` parses to a starred expression `*(not v)`.
- `'boolop'`: Parse to a `boolop` operator.
- `'operator'`: Parse to an `operator` operator, either normal binary `'*'` or augmented `'*='`.
- `'binop'`: Parse to an `operator` only binary `'*'`, `'+'`, `'>>'`, etc...
- `'augop'`: Parse to an `operator` only augmented `'*='`, `'+='`, `'>>='`, etc...
- `'unaryop'`: Parse to a `unaryop` operator.
- `'cmpop'`: Parse to a `cmpop` compare operator.
- `'comprehension'`: Parse a single `comprehension` returned as itself. Same as passing `comprehension` type.
- `'arguments'`: Parse as `arguments` for a `FunctionDef` or `AsyncFunctionDef` returned as itself. In this mode
    type annotations are allowed for the arguments. Same as passing `arguments` type.
- `'arguments_lambda'`: Parse as `arguments` for a `Lambda` returned as itself. In this mode type annotations
    are not allowed for the arguments.
- `'arg'`: Parse as a single `arg` returned as itself. Same as passing `arg` type.
- `'keyword'`: Parse as a single `keyword` returned as itself. Same as passing `keyword` type.
- `'alias'`: Parse as a single `alias` returned as itself. Either starred or dotted versions are accepted. Same
    as passing `alias` type.
- `'alias_dotted'`: Parse as a single `alias` returned as itself, with starred version being a syntax error.
- `'alias_star'`: Parse as a single `alias` returned as itself, with dotted version being a syntax error.
- `'withitem'`: Parse as a single `withitem` returned as itself. Same as passing `withitem` type.
- `'pattern'`: Parse as a a single `pattern` returned as itself. Same as passing `pattern` type.
- `'type_param'`: Parse as a single `type_param` returned as itself, either `TypeVar`, `ParamSpec` or
    `TypeVarTuple`. Same as passing `type_param` type.
- `type[AST]`: If an `AST` type is passed then will attempt to parse to this type. This can be used to narrow
    the scope of desired return, for example `Constant` will parse as an expression but fail if the expression
    is not a `Constant`. These overlap with the string specifiers to an extent but not all of them. For example
    `AST` type `ast.expr` is the same as passing `'expr'`. Not all string specified modes are can be matched, for
    example `'arguments_lambda'`. Likewise `'exec'` and `'stmts'` specify the same parse mode, but not the same as
    `Module` since that is used as a general purpose slice container. `Tuple` parse also allows parsing `Slice`s in the
    `Tuple`.
"""


class NodeError(ValueError):
    """General FST node error. Used and caught when a raw reparse is possible to fall back to the reparse if allowed."""


class astfield(NamedTuple):
    """Name and optional index indicating a field location in an `AST` (or `FST`) node."""

    name: str                ; """The actual field name, a la "body", "value", "orelse", etc..."""
    idx:  int | None = None  ; """The index if the field is a list, else `None`."""

    def __repr__(self) -> str:
        return f'astfield({self.name!r})' if (idx := self.idx) is None else f'astfield({self.name!r}, {idx})'

    def get(self, parent: AST) -> Any:
        """Get child node at this field in the given `parent`."""

        return getattr(parent, self.name) if self.idx is None else getattr(parent, self.name)[self.idx]

    def get_no_raise(self, parent: AST, default: Any = False) -> Any:
        """Get child node at this field in the given `parent`. Return `default` if not found instead of raising
        `AttributError` or `IndexError`, `False` works well because not normally found locations where `AST` nodes can
         reside in `AST` trees."""

        return (
            getattr(parent, self.name, default) if (idx := self.idx) is None else
            default if (body := getattr(parent, self.name, False)) is False or idx >= len(body) else
            body[idx])

    def set(self, parent: AST, child: AST):
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
        ns                       = ', '.join(f'{n}={v}' for n, v in self.__dict__.items())

        return (f'fstlocns({ln}, {col}, {end_ln}, {end_col}, {ns})' if ns else
                f'fstlocns({ln}, {col}, {end_ln}, {end_col})')

    def __new__(cls, ln: int, col: int, end_ln: int, end_col: int, **kwargs):
        self = fstloc.__new__(cls, ln, col, end_ln, end_col)

        for name, value in kwargs.items():
            setattr(self, name, value)

        return self


class srcwpos(NamedTuple):
    ln:  int
    col: int
    src: str


class nspace:
    """Simple namespace class used for several things."""

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)


def _shortstr(s: str, maxlen: int = 64) -> str:
    """Return string of maximum length `maxlen`, shortening if necessary to "start .. [X chars] .. end"."""

    if (l := len(s)) <= maxlen:
        return s

    t = maxlen - 16 - (int(log10(l)) + 1)

    return f'{s[:(t+1)//2]} .. [{l} chars] .. {s[-(t//2):]}'


def _next_src(lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
              comment: bool = False, lcont: bool | None = False) -> srcwpos | None:
    """Get next source code which may or may not include comments or line continuation backslashes. May be restricted
    to bound or further restricted to not exceed logical line. Assuming start pos not inside str or comment. Code is not
    necessarily AST stuff, it can be commas, colons, the 'try' keyword, etc... Code can include multiple AST nodes in
    return str if there are no spaces between them like 'a+b'.

    **Parameters:**
    - `comment`: Whether to return comments found, which will be the whole comment.
    - `lcont`: Whether to return line continuations found (backslash at end of line) if `True`, skip over them if
        `False`, or skip over them and restrict search to logical line `None`.
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


def _prev_src(lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
              comment: bool = False, lcont: bool | None = False, *,
              state: list | None = None) -> srcwpos | None:
    """Get prev source code which may or may not include comments or line continuation backslashes. May be restricted
    to bound or further restricted to not exceed logical line. Assuming start pos not inside str or comment. Code is not
    necessarily AST stuff, it can be commas, colons, the 'try' keyword, etc... Code can include multiple AST nodes in
    return str if there are no spaces between them like 'a+b'.

    **WARNING:** Make sure the starting position (`ln`, `col`) is not inside a string because that could give false
    positives for comments or line continuations. To this end, when searching for non-AST stuff, make sure the start
    position does not start INSIDE OF or BEFORE any valid ASTs.

    **Parameters:**
    - `comment`: Whether to return comments found, which will be the whole comment.
    - `lcont`: Whether to return line continuations found (backslash at end of line) if `True`, skip over them if
        `False`, or skip over them and restrict search to logical line `None`.
    - `state`: Can be used to cache walk but must only be used if the walk is sequentially backwards starting each time
        at the start position of the previously returned match.
    """

    re_pat = (
        (re_next_src_or_comment_or_lcont if comment else re_next_src_or_lcont)
        if lcont else
        (re_next_src_or_comment if comment else re_next_src)
    )

    if state is None:
        state = []

    def last_match(l, c, ec, p):
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


def _next_find(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, src: str, first: bool = False, *,
               comment: bool = False, lcont: bool | None = False) -> tuple[int, int] | None:
    """Find location of a string in the bound walking forward from the start. Returns `None` if string not found.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        end of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `_next_src()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `_next_src()`. Can stop search on line continuation if `first` is `True`.

    **Returns:**
    - `fstpos | None`: Location of start of found `src` or `None` if not found with the given parameters.
    """

    if first:
        if code := _next_src(lines, ln, col, end_ln, end_col, comment, lcont):
            cln, ccol, csrc = code

            if csrc.startswith(src):
                return cln, ccol

    else:
        while code := _next_src(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = code

            if (idx := csrc.find(src)) != -1:
                return ln, col + idx

            col += len(csrc)

    return None


def _prev_find(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, src: str, first: bool = False, *,
               comment: bool = False, lcont: bool | None = False, state: list | None = None) -> tuple[int, int] | None:
    """Find location of a string in the bound walking backwards from the end. Returns `None` if string not found. If
    `comment` is `True` then `src` must match the START of the src comment found, not the tail like for non-comment
     strings found in order to be considered successful.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        start of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `_prev_src()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `_prev_src()`. Can stop search on line continuation if `first` is `True`.
    - `state`: The `state` parameter to `_prev_src()`. Be careful using this here and keep in mind its line caching
        functionality if changing search parameters.

    **Returns:**
    - `fstpos | None`: Location of start of found `src` or `None` if not found with the given parameters.
    """

    if first:
        if code := _prev_src(lines, ln, col, end_ln, end_col, comment, lcont, state=state):
            ln, col, csrc = code

            if comment and csrc.startswith('#'):
                if csrc.startswith(src):
                    return ln, col

            elif csrc.endswith(src):
                return ln, col + len(csrc) - len(src)

    else:
        if state is None:
            state = []

        while code := _prev_src(lines, ln, col, end_ln, end_col, comment, lcont, state=state):
            end_ln, end_col, csrc = code

            if comment and csrc.startswith('#'):
                if csrc.startswith(src):
                    return end_ln, end_col

            elif (idx := csrc.rfind(src)) != -1:
                return end_ln, end_col + idx

    return None


def _next_find_re(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, pat: re.Pattern, first: bool = False,
                  *, comment: bool = False, lcont: bool | None = False) -> srcwpos | None:
    """Find location of a regex pattern in the bound walking forward from the start. Returns `None` if string not found.

    **Parameters:**
    - `first`: If `False` then will skip over anything else which is not the string and keep looking until it hits the
        end of the bound. If `True` then will only succeed if `src` is the first thing found.
    - `comment`: The `comment` parameter to `_next_src()`, can stop search on comments if `first` is `True`.
    - `lcont`: The `lcont` parameter to `_next_src()`. Can stop search on line continuation if `first` is `True`.

    **Returns:**
    - `srcwpos | None`: Location of start of `pat` and the string matching the pattern or `None` if not found with the
        given parameters.
    """

    if first:
        if code := _next_src(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = code

            if m := pat.match(csrc):
                return srcwpos(ln, col, m.group())

    else:
        while code := _next_src(lines, ln, col, end_ln, end_col, comment, lcont):
            ln, col, csrc = code

            if m := pat.search(csrc):
                return srcwpos(ln, col + m.start(), m.group())

            col += len(csrc)

    return None


def _next_pars(lines: list[str], pars_end_ln: int, pars_end_col: int, bound_end_ln: int, bound_end_col: int,
               par: str = ')') -> list[tuple[int, int]]:
        """Return a list of the locations of closing parentheses (just past, or any specified character) starting at
        (`pars_end_ln`, `pars_end_col`) until the end of the bound. The list includes (`pars_end_ln`, `pars_end_col`) as
        the first element. The list ends if a non `par` character is encountered while searching forward.

        **Returns:**
        - `[(pars_end_ln, pars_end_col), (ln_end_par1, col_end_par1), (ln_end_par2, col_end_par2), ...]`
        """

        pars = [(pars_end_ln, pars_end_col)]

        while code := _next_src(lines, pars_end_ln, pars_end_col, bound_end_ln, bound_end_col):
            ln, col, src = code

            for c in src:
                if c != par:
                    break

                pars_end_ln  = ln
                pars_end_col = (col := col + 1)

                pars.append((pars_end_ln, pars_end_col))

            else:
                continue

            break

        return pars


def _prev_pars(lines: list[str], bound_ln: int, bound_col: int, pars_ln: int, pars_col: int, par: str = '(',
               ) -> list[tuple[int, int]]:
        """Return a list of the locations of opening parentheses (or any specified character) starting at (`pars_ln`,
        `pars_col`) until the start of the bound. The list includes (`pars_ln`, `pars_col`) as the first element. The
        list ends if a non `par` character is encountered while searching backward.

        **Returns:**
        - `[(pars_ln, pars_col), (ln_par1, col_par1), (ln_par2, col_par2), ...]`
        """

        pars  = [(pars_ln, pars_col)]
        state = []

        while code := _prev_src(lines, bound_ln, bound_col, pars_ln, pars_col, state=state):
            ln, col, src  = code
            col          += len(src)

            for c in src[::-1]:
                if c != par:
                    break

                pars_ln  = ln
                pars_col = (col := col - 1)

                pars.append((pars_ln, pars_col))

            else:
                continue

            break

        return pars


def _params_offset(lines: list[bistr], put_lines: list[bistr], ln: int, col: int, end_ln: int, end_col: int,
                   ) -> tuple[int, int, int, int]:
    """Calculate location and delta parameters for the `offset()` function. The `col` parameter is calculated as a byte
    offset so that the `offset()` function does not have to access the source at all."""

    dfst_ln     = len(put_lines) - 1
    dln         = dfst_ln - (end_ln - ln)
    dcol_offset = put_lines[-1].lenbytes - lines[end_ln].c2b(end_col)
    col_offset  = -lines[end_ln].c2b(end_col)

    if not dfst_ln:
        dcol_offset += lines[ln].c2b(col)

    return end_ln, col_offset, dln, dcol_offset


def _fixup_field_body(ast: AST, field: str | None = None, only_list: bool = True) -> tuple[str, 'AST']:
    """Get `AST` member list for specified `field` or default if `field=None`."""

    if not field:
        if (field := _AST_DEFAULT_BODY_FIELD.get(ast.__class__, _fixup_field_body)) is _fixup_field_body:  # _fixup_field_body serves as sentinel
            raise ValueError(f"{ast.__class__.__name__} has no default body field")

        if not field:  # special case ''
            return '', []

    if (body := getattr(ast, field, _fixup_field_body)) is _fixup_field_body:
        raise ValueError(f"{ast.__class__.__name__} has no field '{field}'")

    if only_list and not isinstance(body, list):
        raise ValueError(f"invalid {ast.__class__.__name__} field '{field}', must be a list")

    return field, body


def _fixup_one_index(len_, idx) -> int:
    if not (0 <= ((idx := idx + len_) if idx < 0 else idx) < len_):
        raise IndexError('index out of range')

    return idx


def _fixup_slice_indices(len_, start, stop) -> tuple[int, int]:
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


def _coerce_ast(ast, coerce: Literal['expr', 'exprish', 'mod'] | None = None) -> AST:
    """Reduce an AST to a simplest representation based on coercion rule.

    **Parameters:**
    - `coerce`: What kind of coercion to apply (if any):
        - `'expr'`: Want `ast.expr` if possible. Returns `Expression.body` or `Module|Interactive.body[0].value` or
            `ast` if is `ast.expr`.
        - `'exprish'`: Same as `'expr'` but also some other expression-like nodes (for raw).
        - `'mod'`: Want `ast.Module`, expressions are wrapped in `Expr` and put into this and all other types are put
            directly into this.
        - `None`: Will pull expression out of `Expression` and convert `Interactive` to `Module`, otherwise will return
            node as is.

    **Returns:**
    - `AST`: Reduced node.
    """

    if isinstance(ast, Expression):
        ast = ast.body

    elif coerce in ('expr', 'exprish'):
        if isinstance(ast, (Module, Interactive)):
            if len(body := ast.body) != 1 or not isinstance(ast := body[0], Expr):
                raise NodeError(f'expecting single expression')

            ast = ast.value

        if not isinstance(ast, expr if (is_expr := coerce == 'expr') else
                          (expr, arg, alias, withitem, pattern, type_param)):
            raise NodeError('expecting expression' if is_expr else 'expecting expressionish node')

        return ast

    elif isinstance(ast, Interactive):
        return Module(body=ast.body, type_ignores=[])

    if coerce == 'mod' and not isinstance(ast, Module):
        if isinstance(ast, expr):
            ast = Expr(value=ast, lineno=ast.lineno, col_offset=ast.col_offset,
                       end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

        ast = Module(body=[ast], type_ignores=[])

    return ast


def _multiline_str_continuation_lns(lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> list[int]:
    """Return the line numbers of a potentially multiline string `Constant`. The location passed MUST be from the
    `Constant` `AST` node or calculated to be the same, otherwise this function will fail."""

    def walk_multiline(start_ln, end_ln, m, re_str_end):
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

        ln, col, _ = _next_src(lines, ln, col, end_ln, end_col)  # there must be a next one

    return lns


def _multiline_fstr_continuation_lns(lines: list[str], ln: int, col: int, end_ln: int, end_col: int) -> list[int]:
    """Lets try to find indentable lines by incrementally attempting to parse parts of multiline f-string (or t-)."""


    # TODO: p3.12+ has locations for these which should allow no use of parse


    lns = []

    if end_ln <= ln:
        return lns

    while True:
        ls = [lines[ln][col:].lstrip()]

        for cur_ln in range(ln + 1, end_ln + 1):
            try:
                parse('\n'.join(ls))

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


# ----------------------------------------------------------------------------------------------------------------------
__all_private__ = [n for n in globals() if n not in _GLOBALS]  # used by make_docs.py
