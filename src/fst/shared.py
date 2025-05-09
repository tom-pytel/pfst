import re
from ast import *
from typing import Any, Literal, NamedTuple, TypeAlias, Union

from .astutil import *
from .astutil import TypeAlias, TryStar, type_param, TypeVar, ParamSpec, TypeVarTuple, TemplateStr, Interpolation

_START_GLOBALS                   = globals().copy()
_START_GLOBALS['_START_GLOBALS'] = True


class astfield(NamedTuple):
    name: str
    idx:  int | None = None

    def get(self, parent: AST) -> Any:
        """Get child node at this field in the given `parent`."""

        return getattr(parent, self.name) if self.idx is None else getattr(parent, self.name)[self.idx]

    def get_no_raise(self, parent: AST) -> Any:
        """Get child node at this field in the given `parent`. Return `False` if not found instead of raising."""

        return (
            getattr(parent, self.name, False) if (idx := self.idx) is None else
            False if (body := getattr(parent, self.name, False)) is False or idx >= len(body) else
            body[idx])

    def set(self, parent: AST, child: AST):
        """Set `child` node at this field in the given `parent`."""

        if self.idx is None:
            setattr(parent, self.name, child)
        else:
            getattr(parent, self.name)[self.idx] = child


class fstloc(NamedTuple):
    ln:      int
    col:     int
    end_ln:  int
    end_col: int

    bln      = property(lambda self: self.ln)       ; """Alias for `ln`."""  # for convenience
    bcol     = property(lambda self: self.col)      ; """Alias for `col`."""
    bend_ln  = property(lambda self: self.end_ln)   ; """Alias for `end_ln`."""
    bend_col = property(lambda self: self.end_col)  ; """Alias for `end_col`."""

    is_FST   = False                                ; """@private"""  # for quick checks vs. `FST`


class srcwpos(NamedTuple):
    ln:  int
    col: int
    src: str


AST_FIELDS_NEXT: dict[tuple[type[AST], str], str | None] = dict(sum((  # next field name from AST class and current field name
    [] if not fields else
    [((cls, fields[0]), None)] if len(fields) == 1 else
    [((cls, fields[i]), fields[i + 1]) for i in range(len(fields) - 1)] + [((cls, fields[-1]), None)]
    for cls, fields in AST_FIELDS.items()), start=[])
)

AST_FIELDS_NEXT[(Dict, 'keys')]             = 0  # special cases
AST_FIELDS_NEXT[(Dict, 'values')]           = 1
AST_FIELDS_NEXT[(Compare, 'ops')]           = 2
AST_FIELDS_NEXT[(Compare, 'comparators')]   = 3
AST_FIELDS_NEXT[(Compare, 'left')]          = 'comparators'  # black magic juju
AST_FIELDS_NEXT[(MatchMapping, 'keys')]     = 4
AST_FIELDS_NEXT[(MatchMapping, 'patterns')] = 5
AST_FIELDS_NEXT[(Call, 'args')]             = 6
AST_FIELDS_NEXT[(Call, 'keywords')]         = 6
AST_FIELDS_NEXT[(arguments, 'posonlyargs')] = 7
AST_FIELDS_NEXT[(arguments, 'args')]        = 7
AST_FIELDS_NEXT[(arguments, 'vararg')]      = 7
AST_FIELDS_NEXT[(arguments, 'kwonlyargs')]  = 7
AST_FIELDS_NEXT[(arguments, 'defaults')]    = 7
AST_FIELDS_NEXT[(arguments, 'kw_defaults')] = 7

AST_FIELDS_PREV: dict[tuple[type[AST], str], str | None] = dict(sum((  # previous field name from AST class and current field name
    [] if not fields else
    [((cls, fields[0]), None)] if len(fields) == 1 else
    [((cls, fields[i + 1]), fields[i]) for i in range(len(fields) - 1)] + [((cls, fields[0]), None)]
    for cls, fields in AST_FIELDS.items()), start=[])
)

AST_FIELDS_PREV[(Dict, 'keys')]             = 0  # special cases
AST_FIELDS_PREV[(Dict, 'values')]           = 1
AST_FIELDS_PREV[(Compare, 'ops')]           = 2
AST_FIELDS_PREV[(Compare, 'comparators')]   = 3
AST_FIELDS_PREV[(MatchMapping, 'keys')]     = 4
AST_FIELDS_PREV[(MatchMapping, 'patterns')] = 5
AST_FIELDS_PREV[(Call, 'args')]             = 6
AST_FIELDS_PREV[(Call, 'keywords')]         = 6
AST_FIELDS_PREV[(arguments, 'posonlyargs')] = 7
AST_FIELDS_PREV[(arguments, 'args')]        = 7
AST_FIELDS_PREV[(arguments, 'vararg')]      = 7
AST_FIELDS_PREV[(arguments, 'kwonlyargs')]  = 7
AST_FIELDS_PREV[(arguments, 'defaults')]    = 7
AST_FIELDS_PREV[(arguments, 'kw_defaults')] = 7
AST_FIELDS_PREV[(arguments, 'kwarg')]       = 7

AST_DEFAULT_BODY_FIELD  = {cls: field for field, classes in [
    ('body',         (Module, Interactive, Expression, FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If,
                      With, AsyncWith, Try, TryStar, ExceptHandler, Lambda, match_case),),
    ('cases',        (Match,)),

    ('elts',         (Tuple, List, Set)),
    ('patterns',     (MatchSequence, MatchOr)),
    ('targets',      (Delete,)),  # , Assign)),
    ('type_params',  (TypeAlias,)),
    ('names',        (Import, ImportFrom)),
    ('ifs',          (comprehension,)),
    ('values',       (BoolOp,)),
    ('generators',   (ListComp, SetComp, DictComp, GeneratorExp)),
    ('args',         (Call,)),

    # ('values',       (JoinedStr, TemplateStr)),  # values don't have locations in lower version pythons for JoinedStr
    # ('items',        (With, AsyncWith)),  # 'body' takes precedence

    # special cases, field names here only for checks to succeed, otherwise all handled programatically
    (None,           (Dict,)),
    (None,           (MatchMapping,)),
    (None,           (Compare,)),

    # other single value fields
    ('value',        (Expr, Return, Assign, AugAssign, NamedExpr, Await, Yield, YieldFrom, FormattedValue, Interpolation,
                      Attribute, Subscript, Starred, keyword, MatchValue)),
    ('test',         (Assert,)),
    ('operand',      (UnaryOp,)),
    # ('elt',          (ListComp, SetComp, GeneratorExp)),  # 'generators' take precedence because name is longer and more annoying to type out
    ('context_expr', (withitem,)),
    ('pattern',      (MatchAs,)),
] for cls in classes}

EXPRESSIONISH           = (expr, arg, alias, withitem, pattern, type_param)
STATEMENTISH            = (stmt, ExceptHandler, match_case)  # always in lists, cannot be inside multilines
STATEMENTISH_OR_MOD     = STATEMENTISH + (mod,)
STATEMENTISH_OR_STMTMOD = STATEMENTISH + (Module, Interactive)
BLOCK                   = (FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If, With, AsyncWith, Match,
                           Try, TryStar, ExceptHandler, match_case)
BLOCK_OR_MOD            = BLOCK + (mod,)
SCOPE                   = (FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp, GeneratorExp)
SCOPE_OR_MOD            = SCOPE + (mod,)
NAMED_SCOPE             = (FunctionDef, AsyncFunctionDef, ClassDef)
NAMED_SCOPE_OR_MOD      = NAMED_SCOPE + (mod,)
ANONYMOUS_SCOPE         = (Lambda, ListComp, SetComp, DictComp, GeneratorExp)

PARENTHESIZABLE         = (expr, alias, withitem, pattern)
HAS_DOCSTRING           = NAMED_SCOPE_OR_MOD

STATEMENTISH_FIELDS     = frozenset(('body', 'orelse', 'finalbody', 'handlers', 'cases'))

PATH_BODY               = [astfield('body', 0)]
PATH_BODY2              = [astfield('body', 0), astfield('body', 0)]
PATH_BODYORELSE         = [astfield('body', 0), astfield('orelse', 0)]
PATH_BODY2ORELSE        = [astfield('body', 0), astfield('body', 0), astfield('orelse', 0)]
PATH_BODYHANDLERS       = [astfield('body', 0), astfield('handlers', 0)]
PATH_BODY2HANDLERS      = [astfield('body', 0), astfield('body', 0), astfield('handlers', 0)]
PATH_BODYCASES          = [astfield('body', 0), astfield('cases', 0)]

DEFAULT_PARSE_PARAMS    = dict(filename='<unknown>', type_comments=False, feature_version=None)
DEFAULT_INDENT          = '    '

# TODO: remove these and just initialize in FST.OPTIONS
DEFAULT_DOCSTR          = True    # True | False | 'strict'
DEFAULT_PRECOMMS        = True    # True | False | 'all'
DEFAULT_POSTCOMMS       = True    # True | False | 'all' | 'block'
DEFAULT_PRESPACE        = False   # True | False | int
DEFAULT_POSTSPACE       = False   # True | False | int
DEFAULT_PEP8SPACE       = True    # True | False | 1
DEFAULT_PARS            = 'auto'  # True | False | 'auto'
DEFAULT_ELIF_           = False   # True | False
DEFAULT_FIX             = True    # True | False
DEFAULT_RAW             = 'auto'  # True | False | 'auto'

re_empty_line_start     = re.compile(r'[ \t]*')     # start of completely empty or space-filled line (from start pos, start of line indentation)
re_empty_line           = re.compile(r'[ \t]*$')    # completely empty or space-filled line (from start pos, start of line indentation)
re_comment_line_start   = re.compile(r'[ \t]*#')    # empty line preceding a comment
re_line_continuation    = re.compile(r'[^#]*\\$')   # line continuation with backslash not following a comment start '#' (from start pos, assumed no asts contained in line)
re_line_trailing_space  = re.compile(r'.*?(\s*)$')  # location of trailing whitespace at the end of a line

re_oneline_str          = re.compile(r'(?:b|r|rb|br|u|)  (?:  \'(?:\\.|[^\\\'])*?\'  |  "(?:\\.|[^\\"])*?"  )',   # I f'])*?\'ng hate these!
                                     re.VERBOSE | re.IGNORECASE)
re_contline_str_start   = re.compile(r'(?:b|r|rb|br|u|)  (\'|")', re.VERBOSE | re.IGNORECASE)
re_contline_str_end_sq  = re.compile(r'(?:\\.|[^\\\'])*?  \'', re.VERBOSE)
re_contline_str_end_dq  = re.compile(r'(?:\\.|[^\\"])*?  "', re.VERBOSE)
re_multiline_str_start  = re.compile(r'(?:b|r|rb|br|u|)  (\'\'\'|""")', re.VERBOSE | re.IGNORECASE)
re_multiline_str_end_sq = re.compile(r'(?:\\.|[^\\])*?  \'\'\'', re.VERBOSE)
re_multiline_str_end_dq = re.compile(r'(?:\\.|[^\\])*?  """', re.VERBOSE)

re_empty_line_cont_or_comment   = re.compile(r'[ \t]*(\\|#.*)?$')        # emmpty line or line continuation or a pure comment line

re_next_src                     = re.compile(r'\s*([^\s#\\]+)')          # next non-space non-continuation non-comment code text, don't look into strings with this!
re_next_src_or_comment          = re.compile(r'\s*([^\s#\\]+|#.*)')      # next non-space non-continuation code or comment text, don't look into strings with this!
re_next_src_or_lcont            = re.compile(r'\s*([^\s#\\]+|\\$)')      # next non-space non-comment code including logical line end, don't look into strings with this!
re_next_src_or_comment_or_lcont = re.compile(r'\s*([^\s#\\]+|#.*|\\$)')  # next non-space non-continuation code or comment text including logical line end, don't look into strings with this!

Code = Union['FST', AST, list[str], str]

class NodeTypeError(ValueError): pass


def _with_loc(fst: 'FST', with_loc: bool | Literal['all', 'own'] = True) -> bool:
    """Check location condition on node. Safe for low level because doesn't use `.loc` calculation machinery."""

    if not with_loc:
        return True

    if with_loc is True:
        return not (isinstance(a := fst.a, (expr_context, boolop, operator, unaryop, cmpop)) or
                    (isinstance(a, arguments) and not a.posonlyargs and not a.args and not a.vararg and
                    not a.kwonlyargs and not a.kwarg))

    if with_loc == 'all':
        return not (isinstance(a := fst.a, (expr_context, boolop)) or
                    (isinstance(a, arguments) and not a.posonlyargs and not a.args and not a.vararg and
                    not a.kwonlyargs and not a.kwarg))

    return fst.has_own_loc  # with_loc == 'own'


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

    **CAVEAT:** Make sure the starting position (`ln`, `col`) is not inside a string because that could give false
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
            cln, ccol, csrc = code

            if comment and csrc.startswith('#'):
                if csrc.startswith(src):
                    return cln, ccol

            elif csrc.endswith(src):
                return cln, ccol + len(csrc) - len(src)

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


def _next_pars(lines: list[str], pars_end_ln: int, pars_end_col: int, bound_end_ln: int, bound_end_col: int,
               par: str = ')') -> tuple[int, int, int, int, int]:
        """Count number of closing parenthesis (or any specified character) starting a `pars_end_ln`, `pars_end_col`
        until the end of the bound. The count ends if a non `par` character is encountered and the last and also
        ante-last ending position of a `par` is returned along with the count.

        **Returns:**
        - `(pars_end_ln, pars_end_col, ante_end_ln, ante_end_col, npars)`: The rightmost and ante-rightmost ending
            positions and total count of closing parentheses encountered. `pars_end_*` and `ante_end_*` will be same if
            no parentheses found.
        """

        ante_end_ln  = pars_end_ln
        ante_end_col = pars_end_col
        npars        = 0

        while code := _next_src(lines, pars_end_ln, pars_end_col, bound_end_ln, bound_end_col):
            ln, col, src = code

            for c in src:
                if c != par:
                    break

                ante_end_ln   = pars_end_ln
                ante_end_col  = pars_end_col
                pars_end_ln   = ln
                pars_end_col  = (col := col + 1)
                npars        += 1

            else:
                continue

            break

        return pars_end_ln, pars_end_col, ante_end_ln, ante_end_col, npars


def _prev_pars(lines: list[str], bound_ln: int, bound_col: int, pars_ln: int, pars_col: int, par: str = '(',
               ) -> tuple[int, int, int, int, int]:
        """Count number of opening parenthesis (or any specified character) starting a `pars_ln`, `pars_col` until the
        start of the bound. The count ends if a non `par` character is encountered and the last and also ante-last
        starting position of a `par` is returned along with the count.

        **Returns:**
        - `(pars_ln, pars_col, ante_ln, ante_col, npars)`: The leftmost and ante-leftmost starting positions and total
            count of opening parentheses encountered. `pars_*` and `ante_*` will be same if no parentheses found.
        """

        ante_ln  = pars_ln
        ante_col = pars_col
        npars    = 0
        state    = []

        while code := _prev_src(lines, bound_ln, bound_col, pars_ln, pars_col, state=state):
            ln, col, src  = code
            col          += len(src)

            for c in src[::-1]:
                if c != par:
                    break

                ante_ln   = pars_ln
                ante_col  = pars_col
                pars_ln   = ln
                pars_col  = (col := col - 1)
                npars    += 1

            else:
                continue

            break

        return pars_ln, pars_col, ante_ln, ante_col, npars


def _params_offset(lines: list[bistr], put_lines: list[bistr], ln: int, col: int, end_ln: int, end_col: int,
                   ) -> tuple[int, int, int, int]:
    """Calculate location and delta parameters for the `offset()` function. The `col` parameter is calculated as a byte
    offset so that the `offset()` function is does not have to access the source at all."""

    dfst_ln     = len(put_lines) - 1
    dln         = dfst_ln - (end_ln - ln)
    dcol_offset = put_lines[-1].lenbytes - lines[end_ln].c2b(end_col)
    col_offset  = -lines[end_ln].c2b(end_col)

    if not dfst_ln:
        dcol_offset += lines[ln].c2b(col)

    return end_ln, col_offset, dln, dcol_offset


def _fixup_field_body(ast: AST, field: str | None = None, only_list: bool = True) -> tuple[str, 'AST']:
    """Get `AST` member list for specified `field` or default if `field=None`."""

    if field is None:
        if (field := AST_DEFAULT_BODY_FIELD.get(ast.__class__, _fixup_field_body)) is _fixup_field_body:  # _fixup_field_body serves as sentinel
            raise ValueError(f"{ast.__class__.__name__} has no default body field")

        if field is None:  # special case
            return None, []

    if (body := getattr(ast, field, _fixup_field_body)) is _fixup_field_body:
        raise ValueError(f"{ast.__class__.__name__} has no field '{field}'")

    if only_list and not isinstance(body, list):
        raise ValueError(f"invalid {ast.__class__.__name__} field '{field}', must be a list")

    return field, body


def _fixup_slice_index(len_, start, stop) -> tuple[int, int]:
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


def _reduce_ast(ast, coerce: Literal['expr', 'exprish', 'mod'] | None = None):
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
                raise NodeTypeError(f'expecting single expression')

            ast = ast.value

        if not isinstance(ast, expr if (is_expr := coerce == 'expr') else EXPRESSIONISH):
            raise NodeTypeError('expecting expression' if is_expr else 'expecting expressionish node')

        return ast

    elif isinstance(ast, Interactive):
        return Module(body=ast.body, type_ignores=[])

    if coerce == 'mod' and not isinstance(ast, Module):
        if isinstance(ast, expr):
            ast = Expr(value=ast, lineno=ast.lineno, col_offset=ast.col_offset,
                       end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

        ast = Module(body=[ast], type_ignores=[])

    return ast


__all__ = [n for n in globals() if n not in _START_GLOBALS]
# print(__all__)
