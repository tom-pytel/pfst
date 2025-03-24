import re
from ast import *
from ast import parse as ast_parse, unparse as ast_unparse
from typing import Any, Callable, Generator, Literal, NamedTuple, Optional, TypeAlias, Union

from .util import *
from .util import TryStar

__all__ = [
    'parse', 'unparse', 'FST', 'FSTSrcEdit',
    'fstlistproxy', 'fstloc', 'srcwpos', 'astfield',
]


REPR_SRC_LINES = 0  # for debugging

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
    ('elts',     (Tuple, List, Set)),
    ('cases',    (Match,)),
    ('patterns', (MatchSequence, MatchOr)),
    ('values',   (JoinedStr,)),
    # ('value',    (Expr, Return, Await, Yield, YieldFrom, Constant, Starred, MatchValue, MatchSingleton)),  # maybe obvious single bodies in future?
    # ('pattern',  (MatchAs,)),
] for cls in classes}

DEFAULT_PARSE_PARAMS    = dict(filename='<unknown>', type_comments=False, feature_version=None)
DEFAULT_INDENT          = '    '
DEFAULT_DOCSTR          = True
DEFAULT_SRC_EDIT_FMT    = frozenset(('pep8', 'pre', 'post'))
DEFAULT_COMMS_FMT       = frozenset(('pre', 'post'))

PARENTHESIZABLE         = (expr, pattern)
STATEMENTISH            = (stmt, ExceptHandler, match_case)  # always in lists, cannot be inside multilines
STATEMENTISH_OR_MOD     = (stmt, ExceptHandler, match_case, mod)
STATEMENTISH_OR_STMTMOD = (stmt, ExceptHandler, match_case, Module, Interactive)
BLOCK_OR_MOD            = (FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If, With, AsyncWith, Match,
                           Try, TryStar, ExceptHandler, match_case, mod)
SCOPE_OR_MOD            = (FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp, GeneratorExp,
                           mod)
NAMED_SCOPE_OR_MOD      = (FunctionDef, AsyncFunctionDef, ClassDef, mod)
NAMED_SCOPE             = (FunctionDef, AsyncFunctionDef, ClassDef)
ANONYMOUS_SCOPE         = (Lambda, ListComp, SetComp, DictComp, GeneratorExp)
HAS_DOCSTRING           = NAMED_SCOPE_OR_MOD

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

Code: TypeAlias = Union['FST', AST, list[str], str]
Fmt:  TypeAlias = Union[str, set, frozenset]


class astfield(NamedTuple):
    name: str
    idx:  int | None = None

    def get(self, parent: AST) -> Any:
        """Get child node at this field in the given `parent`."""

        return getattr(parent, self.name) if self.idx is None else getattr(parent, self.name)[self.idx]

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


def parse(source, filename='<unknown>', mode='exec', *, type_comments=False, feature_version=None, **kwargs) -> AST:
    """Executes `ast.parse()` and then adds `FST` nodes to the parsed tree. Drop-in replacement for `ast.parse()`. For
    parameters, see `ast.parse()`. Returned `AST` tree has added `.f` attribute at each node which accesses the parallel
    `FST` tree."""

    return FST.fromsrc(source, filename, mode, type_comments=type_comments, feature_version=feature_version, **kwargs).a


def unparse(ast_obj) -> str:
    """Returns the formatted source that is kept for this tree. Drop-in replacement for `ast.unparse()`."""

    if (f := getattr(ast_obj, 'f', None)) and isinstance(f, FST) and f.loc:
        if f.is_root:
            return f.src

        try:
            return f.copy().src
        except Exception:
            pass

    return ast_unparse(ast_obj)


def _with_loc(fst: 'FST', with_loc: bool | Literal['own'] = True) -> bool:
    """Check location condition on node. Safe for low level because doesn't use `.loc` calculation machinery and faster
    overall than checking `ast.f.loc`."""

    if not with_loc:
        return True

    if with_loc is True:
        return not (isinstance(a := fst.a, (expr_context, boolop, operator, unaryop, cmpop)) or
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
    position does not start INSODE OF or BEFORE any valid ASTs.

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
            c = m.end(1)

            if (not comment and l.startswith('#', c)) or (not lcont and l.startswith('\\', c)):
                break

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


def _fixup_field_body(ast: AST, field: str | None = None) -> tuple[str, 'AST']:
    if field is None:
        field = AST_DEFAULT_BODY_FIELD.get(ast.__class__, 'body')

    if (body := getattr(ast, field, _fixup_field_body)) is _fixup_field_body:  # _fixup_field_body is sentinel
        raise ValueError(f"{ast.__class__.__name__} has no field '{field}'")

    if not isinstance(body, list):
        raise ValueError(f"invalid {ast.__class__.__name__} field '{field}', must be a list")

    return field, body


def _fixup_slice_index(ast, body, field, start, stop) -> tuple[int, int]:
    len_body = len(body)

    if start is None:
        start = 0
    elif start < 0:
        start += len_body

    if stop is None:
        stop = len_body
    elif stop < 0:
        stop += len_body

    if start < 0 or start > len_body or stop < 0 or stop > len_body:
        raise IndexError(f"{ast.__class__.__name__}.{field} index out of range")

    return start, stop


def _normalize_code(code: Code, coerce: Literal['expr'] | Literal['mod'] | None = None, *, parse_params: dict = {},
                    ) -> 'FST':
    """Normalize code to an `FST` and coerce to a desired format if possible.

    If neither of these is requested then will convert to `ast.Module` if is `ast.Interactive` or return single
    expression node of `ast.Expression` or just return whatever the node currently is.


    **Parameters:**
    - `coerce`: What kind of coercion to apply (if any):
        - `'expr'`: Will return an `FST` with a top level `ast.expr` `AST` node if possible, raise otherwise.
        - `'mod'`: Will return an `FST` with a top level `ast.Module` `AST` node of the single statement or a wrapped
            expression in an `ast.Expr` node. `ExceptHandler` and `match_case` nodes are considered statements here.
        - `None`: Will pull expression out of `ast.Expression` and convert `ast.Interactive` to `ast.Module`, otherwise
            will return node as is, or as is parsed to `Module`.

    **Returns:**
    - `FST`: Compiled or coerced or just fixed up.
    """

    def reduce(ast):
        if isinstance(ast, Expression):
            ast = ast.body

        elif coerce == 'expr':
            if isinstance(ast, (Module, Interactive)):
                if len(body := ast.body) != 1 or not isinstance(ast := body[0], Expr):
                    raise ValueError(f'expecting single expression')

                ast = ast.value

            if not isinstance(ast, expr):
                raise ValueError(f'expecting expression')

            return ast

        elif isinstance(ast, Interactive):
            return Module(body=ast.body, type_ignores=[])

        if coerce == 'mod' and not isinstance(ast, Module):
            if isinstance(ast, expr):
                ast = Expr(value=ast, lineno=ast.lineno, col_offset=ast.col_offset,
                           end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

            ast = Module(body=[ast], type_ignores=[])

        return ast

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root FST')

        ast  = code.a
        rast = reduce(ast)

        return code if rast is ast else FST(rast, lines=code._lines, from_=code)

    if isinstance(code, AST):
        return FST.fromast(reduce(code))  # WARNING! will not handle pure AST ExceptHandler or match_case

    if isinstance(code, str):
        src   = code
        lines = code.split('\n')

    else:  # isinstance(code, list):
        src   = '\n'.join(code)
        lines = code

    ast = (ast_parse(src, mode='eval', **parse_params).body
           if coerce == 'expr' else
           ast_parse(src, mode='exec', **parse_params))

    return FST(ast, lines=lines)


def _new_empty_module(*, from_: Optional['FST'] = None) -> 'FST':
    return FST(Module(body=[], type_ignores=[]), lines=[bistr('')], from_=from_)


def _new_empty_tuple(*, from_: Optional['FST'] = None) -> 'FST':
    ast                = Tuple(elts=[], ctx=Load())
    fst                = FST(ast, lines=[bistr('()')], from_=from_)
    ast.lineno         = ast.end_lineno = 1
    ast.col_offset     = 0
    ast.end_col_offset = 2

    return fst


def _new_empty_list(*, from_: Optional['FST'] = None) -> 'FST':
    ast                = List(elts=[], ctx=Load())
    fst                = FST(ast, lines=[bistr('[]')], from_=from_)
    ast.lineno         = ast.end_lineno = 1
    ast.col_offset     = 0
    ast.end_col_offset = 2

    return fst


def _new_empty_dict(*, from_: Optional['FST'] = None) -> 'FST':
    ast                = Dict(keys=[], values=[])
    fst                = FST(ast, lines=[bistr('{}')], from_=from_)
    ast.lineno         = ast.end_lineno = 1
    ast.col_offset     = 0
    ast.end_col_offset = 2

    return fst


def _new_empty_set_curlies(ast_only: bool = False, lineno: int = 1, col_offset: int = 0, *,
                           from_: Optional['FST'] = None) -> 'FST':
    ast                = Set(elts=[])
    ast.lineno         = ast.end_lineno = lineno
    ast.col_offset     = col_offset
    ast.end_col_offset = col_offset + 2

    return ast if ast_only else FST(ast, lines=[bistr('{}')], from_=from_)


def _new_empty_set_call(ast_only: bool = False, lineno: int = 1, col_offset: int = 0, *,
                        from_: Optional['FST'] = None) -> 'FST':
    ast                     = Call(func=Name(id='set', ctx=Load()), args=[], keywords=[])
    ast.lineno              = ast.end_lineno = lineno
    ast.col_offset          = col_offset
    ast.end_col_offset      = col_offset + 5
    ast.func.lineno         = ast.func.end_lineno = lineno
    ast.func.col_offset     = col_offset
    ast.func.end_col_offset = col_offset + 3

    return ast if ast_only else FST(ast, lines=[bistr('set()')], from_=from_)


class fstlistproxy:
    def __init__(self, asts: list[AST], owner: 'FST', field: str, start: int = 0):
        self.asts  = asts
        self.owner = owner
        self.field = field
        self.start = start

    def __repr__(self) -> str:
        return f'f{list(self)}'

    def __getitem__(self, idx: int | str | slice) -> Any:
        if isinstance(idx, int):
            return a.f if isinstance(a := self.asts[idx], AST) else a

        if isinstance(idx, str):
            if not (a := get_func_class_or_ass_by_name(self.asts, idx)):
                raise IndexError(f"function, class or variable '{idx}' not found")

            return a.f

        return fstlistproxy((asts := self.asts)[idx], self.owner, self.field,
                            start if (start := idx.start) >= 0 else start + len(asts))

    def __setitem__(self, idx: int | slice, code: Code):
        if isinstance(idx, int):
            self.owner.put(code, idx, field=self.field)
        elif idx.step is not None:
            raise ValueError('step slicing not supported')
        else:
            self.owner.put_slice(code, idx.start, idx.stop, self.field)

    def __delitem__(self, idx: int | slice):
        if isinstance(idx, int):
            self.owner.put_slice(None, idx, idx + 1, field=self.field)
        elif idx.step is not None:
            raise ValueError('step slicing not supported')
        else:
            self.owner.put_slice(None, idx.start, idx.stop, self.field)

    def copy(self, *, fix: bool = True, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':
        return self.owner.get_slice(i := self.start, i + len(self.asts), self.field, fix=fix, cut=False,
                                    fmt=fmt, docstr=docstr)

    def cut(self, *, fix: bool = True, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':
        return self.owner.get_slice(i := self.start, i + len(self.asts), self.field, fix=fix, cut=True,
                                    fmt=fmt, docstr=docstr)

    def put(self, code: Code, *, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':  # -> Self:
        self.owner.put_slice(code, i := self.start, i + len(self.asts), self.field, True, fmt=fmt, docstr=docstr)

        return self

    def append(self, code: Code, *, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':  # -> Self:
        self.owner.put_slice(code, i := self.start + len(self.asts), i, self.field, True, fmt=fmt, docstr=docstr)

        return self

    def extend(self, code: Code, *, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':  # -> Self:
        self.owner.put_slice(code, i := self.start + len(self.asts), i, self.field, False, fmt=fmt, docstr=docstr)

        return self

    def prepend(self, code: Code, *, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':  # -> Self:
        self.owner.put_slice(code, i := self.start, i, self.field, True, fmt=fmt, docstr=docstr)

        return self

    def prextend(self, code: Code, *, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':  # -> Self:
        self.owner.put_slice(code, i := self.start, i, self.field, False, fmt=fmt, docstr=docstr)

        return self


class FSTSrcEdit:
    """This class controls most source editing behavior."""

    def _fixup_expr_seq_bound(self, lines: list[str], seq_loc: fstloc,
                            fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                            flast: Union['FST', fstloc, None],
                            ) -> tuple[fstloc, Union['FST', fstloc, None], Union['FST', fstloc, None]] | None:
        """Depending on existence preceding or following expressions and a full sequence location, return a bound
        `fstloc` that represents a search space in the source for commas and parenteses and the like. Will exclude any
        closing parentheses belonging to `fpre` and any opening parenthese belonging to `fpost` from the bound."""

        if not fpre:
            if not fpost:
                return None

            start_ln  = seq_loc.ln
            start_col = seq_loc.col

        else:
            start_ln, start_col, _, _, npars = (
                _next_pars(lines, fpre.end_ln, fpre.end_col, seq_loc.end_ln, seq_loc.end_col))

            if npars:
                fpre = fstloc(fpre.ln, fpre.col, start_ln, start_col)

        if not fpost:
            stop_ln  = seq_loc.end_ln
            stop_col = seq_loc.end_col

        else:
            if flast:  # make sure there are no ASTs where we will be searching because their strings can screw up _prev_src()
                from_ln  = flast.end_ln
                from_col = flast.end_col

            elif fpre:
                from_ln  = start_ln
                from_col = start_col

            else:
                from_ln  = seq_loc.ln
                from_col = seq_loc.col

            stop_ln, stop_col, _, _, npars = _prev_pars(lines, from_ln, from_col, fpost.ln, fpost.col)

            if npars:
                fpost = fstloc(stop_ln, stop_col, fpost.end_ln, fpost.end_col)

        return fstloc(start_ln, start_col, stop_ln, stop_col), fpre, fpost

    def _expr_src_edit_locs(self, lines: list[bistr], loc: fstloc, bound: fstloc, at_end: bool = False,
                            ) -> tuple[fstloc, fstloc, list[str]]:
        """Get expression copy and delete locations. There can be commas in the bound in which case the expression is
        treated as part of a comma delimited sequence. In this case, if there is a trailing comma within bounding span then
        it is included in the delete location. Any enclosing grouping parentheses within the bounding span are included. Any
        closing parentheses after the start of or opening parentheses before the end of `bound` are also handled correctly.

        **Parameters:**
        - `lines`: The lines corresponding to the expression and its `bound` location.
        - `loc`: The location of the expression, can be multiple or no expressions, just the location matters.
        - `bound`: The bounding location not to go outside of. Must entirely contain `loc` (can be same as). Must not
            contain any part of other `AST` nodes like other members of a sequence. Can contain any number of open and close
            parentheses for the expression itself and closing and opening parentheses belonging to expressions from outside
            the bound.
        - `at_end`: Whether `loc` is at the end of a sequence, used to remove trailing whitespace from preceding comma.

        **Returns:**
        - `(copy_loc, del_loc)`: `copy_loc` is the location of source that should be used if copying the expression.
            `del_loc` is the location which should be deleted used if removing the expression. Both are used
            for a cut operation.
        """

        copy_ln,  copy_col,  copy_end_ln,  copy_end_col  = loc
        bound_ln, bound_col, bound_end_ln, bound_end_col = bound

        precomma_end_ln = None
        state           = []

        while True:
            if not (code := _prev_src(lines, bound_ln, bound_col, copy_ln, copy_col, state=state)):
                if bound_ln != copy_ln:
                    copy_col = 0

                break

            ln, col, src  = code
            col          += len(src)

            for c in src[::-1]:
                if c == ',':
                    precomma_end_ln  = ln
                    precomma_end_col = col

                    if ln != copy_ln:
                        copy_col = 0

                    break

                elif c != '(':  # we don't actually count and check these because there may be other parens inside the `loc` which we can not see here
                    raise ValueError(f"expecting leading comma or open parenthesis, got '{c}'")

                col      -= 1
                copy_ln   = ln
                copy_col  = col

            if precomma_end_ln is not None:
                break

        loc_end_ln     = copy_end_ln
        loc_end_col    = copy_end_col
        postcomma_have = None

        while True:
            if not (code := _next_src(lines, copy_end_ln, copy_end_col, bound_end_ln, bound_end_col)):
                if bound_end_ln != copy_end_ln:
                    copy_end_ln  = bound_end_ln
                    copy_end_col = 0

                break

            ln, col, src = code

            for c in src:
                if c == '(':  # may not have been excluded from bounds as is not part of expressions, if so then adjust end bound and done
                    bound_end_ln  = ln
                    bound_end_col = col

                    break

                col += 1

                if c == ',':
                    if postcomma_have:
                        raise ValueError('multiple trailing commas found')

                    postcomma_have = True

                elif c != ')':
                    raise ValueError(f"not expecting code, got '{src}'"
                                    if postcomma_have else
                                    f"expecting close parenthesis or trailing comma, got '{src}'")

                else:  # c == ')'
                    if postcomma_have:
                        raise ValueError('found close parenthesis after trailing comma')

                    loc_end_ln  = ln  # we update loc because end parens are definitive end of loc, and may not have been checked before calling this function
                    loc_end_col = col

                copy_end_ln  = ln
                copy_end_col = col

            else:
                continue

            break  # this happens if we found an open parenthesis

        # special sauce, can probably be simplified

        del_end_ln = copy_end_ln

        if not copy_end_col and precomma_end_ln is not None:  # ends on newline and there is something before
            del_end_col = 0

        else:
            del_end_col = bound_end_col

            if postcomma_have and copy_end_ln == loc_end_ln:  # end comma on same line as end of expr, don't copy it
                copy_end_col = loc_end_col

        del_ln  = copy_ln
        del_col = copy_col

        if not copy_col and copy_ln != bound_ln:  # starts on newline
            copy_ln  = copy_ln - 1
            copy_col = len(lines[copy_ln])

        elif copy_ln == precomma_end_ln:  # copy start on same line as preceding comma
            if postcomma_have:  # other items follow or explicit trailing comma at end of sequence, delete up to end (including postcomma)
                del_end_col = bound_end_col

                if at_end:  # definitively at end, delete whitespace at end of precomma
                    del_col = precomma_end_col

            elif precomma_end_ln == bound_ln:  # no items following, previous item, delete up to end of item past precomma
                del_col = bound_col
            else:  # previous comma not on same line as previous item, preserve its unique and special formatting as a trailing comma at end of sequence
                del_col = precomma_end_col

        if not del_col and del_end_col and (col := re_empty_line_start.match(lines[del_ln]).end()):  # delete from start of line to middle of line, maybe there is indentation to leave in place
            del_col = col

        # end of special sauce

        return fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col), fstloc(del_ln, del_col, del_end_ln, del_end_col)

    def pre_comments(self, lines: list[bistr], bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                     fmt: set[str] | frozenset[str] = {'pre'}) -> tuple[int, int] | None:
        """Return the position of the start of any preceding comments to the element which is assumed to live just past
        (`f.bln`, `f.bcol`). Returns `None` if no preceding comment. If preceding entire line comments exist then the
        returned position column should be 0 (the start of the line) to indicate that it is a full line comment. Only
        preceding entire line comments start comment should be returned. This particular implementation will return any
        full line comments directly preceding the element if it starts its own line. An empty line ends the preceding
        comments even if there are more comments before it, unless the format includes `'allpre'`.

        **Parameters:**
        - `fmt`: Set of string formatting flags. Unrecognized and inapplicable flags are ignored, recognized flags are:
            - `'pre'`: Contiguous comment block immediately preceding position.
            - `'allpre'`: Comment blocks (possibly separated by empty lines) preceding position.
        """

        if not (allpre := 'allpre' in fmt) and 'pre' not in fmt:
            return None

        if bound_ln == bound_end_ln or (bound_end_col and
                                        not re_empty_line.match(lines[bound_end_ln], 0, bound_end_col)):
            return None

        pre_ln = None
        re_pat = re_empty_line_cont_or_comment if allpre else re_comment_line_start

        for ln in range(bound_end_ln - 1, bound_ln - (not bound_col), -1):  # only consider whole lines
            if not (m := re_pat.match(lines[ln])):
                break

            if not allpre or (g := m.group(1)) and g.startswith('#'):
                pre_ln  = ln
                pre_col = 0

        return None if pre_ln is None else (pre_ln, pre_col)

    def post_comments(self, lines: list[bistr], bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int,
                      fmt: set[str] | frozenset[str] = {'post'}) -> tuple[int, int] | None:
        """Return the position of the end of any trailing comments to the element which is assumed to live just before
        (`f.bend_ln`, `f.bend_col`). Returns `None` if no trailing comment. Should return the location at the start of
        the next line if comment present because a comment should never be on the last line, but if a comment ends the
        bound should return the end of the bound. This particular implementation will return any comment which lives on
        the same line as `bound_ln`, no other comments past it on following lines.

        **Parameters:**
        - `fmt`: Set of string formatting flags. Unrecognized and inapplicable flags are ignored, recognized flags are:
            - `'post'`: Only comment trailing on line of position, nothing past that on its own lines.
            - `'blkpost'`: Single contiguous comment block following position.
            - `'allpost'`: Comment blocks (possibly separated by empty lines) following position.
        """

        if not (blkpost := (allpost := 'allpost' in fmt)) and not (blkpost := 'blkpost' in fmt) and 'post' not in fmt:
            return None

        if single_ln := bound_end_ln == bound_ln:
            code = _next_src(lines, bound_ln, bound_col, bound_ln, bound_end_col, True)
        else:
            code = _next_src(lines, bound_ln, bound_col, bound_ln, 0x7fffffffffffffff, True)

        if code:
            if not code.src.startswith('#'):
                return None

            if not blkpost:
                return (bound_ln, bound_end_col) if single_ln else (bound_ln + 1, 0)

        elif not blkpost or single_ln:
            return None

        for ln in range(bound_ln + 1, bound_end_ln + 1):
            if not (m := re_empty_line_cont_or_comment.match(lines[ln])):
                break

            if g := m.group(1):
                if g.startswith('#'):
                    bound_ln = ln

            elif not allpost:
                break

        return (bound_ln, bound_end_col) if bound_ln == bound_end_ln else (bound_ln + 1, 0)

    def get_slice_seq(self, fst: 'FST', cut: bool, seq_loc: fstloc,
                      ffirst: Union['FST', fstloc], flast: Union['FST', fstloc],
                      fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
    ) -> tuple[fstloc, fstloc | None, list[str] | None]:  # (copy_loc, del/put_loc, put_lines)
        """Copy or cut from comma delimited sequence.

        The `ffirst`, `flast`, `fpre` and `fpost` parameters are only meant to pass location information so you should
        only count on their respective `.ln`, `.col`, `.end_ln` and `.end_col` being correct (within `fst`).

        **Parameters:**
        - `fst`: The source `FST` container that is being gotten from. No text has been changed at this point but the
            respective `AST` nodes may have been removed in case of `cut`.
        - `cut`: If `False` the operation is a copy, `True` means cut.
        - `seq_loc`: The full location of the sequence in `fst`, excluding parentheses / brackets / curlies.
        - `ffirst`: The first `FST` or `fstloc` being gotten.
        - `flast`: The last `FST` or `fstloc` being gotten.
        - `fpre`: The preceding-first `FST` or `fstloc`, not being gotten, may not exist if `ffirst` is first of seq.
        - `fpost`: The after-last `FST` or `fstloc` not being gotten, may not exist if `flast` is last of seq.

        **Returns:**
        - If `cut=False` then only the first element of the return tuple is used for the copy and the other two are
            ignored so they don't need to be calculated. If `cut=True` then should return the copy location, a delete
            location and optionally lines to replace the deleted portion (which can only be non-coding source).
        """

        lines = fst.root._lines

        if not (bound_pre_post := self._fixup_expr_seq_bound(lines, seq_loc, fpre, fpost, flast)):
            return seq_loc, seq_loc, None

        bound, _, _       = bound_pre_post
        copy_loc, del_loc = self._expr_src_edit_locs(
            lines, fstloc(ffirst.ln, ffirst.col, flast.end_ln, flast.end_col), bound)

        if not fpost:
            del_ln, del_col, del_end_ln, del_end_col = del_loc

            if (new_del_col := re_line_trailing_space.match(lines[del_ln],
                                                            bound.col if del_ln == bound.ln else 0,
                                                            del_col := del_col).start(1)) < del_col:  # move del start to beginning of any trailing whitespace from del location before end of sequence
                del_loc = fstloc(del_ln, new_del_col, del_end_ln, del_end_col)

        return copy_loc, del_loc, None

    def put_slice_seq(self, fst: 'FST', put_fst: Optional['FST'], indent: str, seq_loc: fstloc,
                      ffirst: Union['FST', fstloc, None], flast: Union['FST', fstloc, None],
                      fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                      pfirst: Union['FST', fstloc, None], plast: Union['FST', fstloc, None],
    ) -> fstloc:  # del_loc
        """Put to comma delimited sequence.

        The `ffirst`, `flast`, `fpre` and `fpost` parameters are only meant to pass location information so you should
        only count on their respective `.ln`, `.col`, `.end_ln` and `.end_col` being correct (within `src`).

        If `ffirst` and `flast` are `None` it means that it is a pure insertion and no elements are being removed. In
        this case use `fpre` and `fpost` to determine locations, one of which could be missing if the insertion is at
        the beginning or end of the sequence, both of which missing indicates put to empty sequence (in which case use
        `seq_loc` for location).

        The first line of `put_fst` is unindented and should remain so as it is concatenated with the target line at the
        point of insertion. The last line of `put_fst` is likewise prefixed to the line following the deleted location.

        There is always an operation if this is called, insertion, deletion, or replacement. It is never an empty
        assignment to an empty slice.

        **Parameters:**
        - `fst`: The destination `FST` container that is being put to.
        - `put_fst`: The sequence which is being put, may be `None` in case of deletion. Already indented, mutate this
            object to change what will be put (both source and `AST` nodes, node locations must be offset if source is
            changed).
        - `indent`: The indent string which was applied to `put_fst`.
        - `seq_loc`: The full location of the sequence in `fst`, excluding parentheses / brackets / curlies.
        - `ffirst`: The first destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `flast`: The last destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `fpre`: The preceding-first destination `FST` or `fstloc`, not being replaced, may not exist if `ffirst` is
            first of seq.
        - `fpost`: The after-last destination `FST` or `fstloc` not being replaced, may not exist if `flast` is last of
            seq.
        - `pfirst`: The first source `FST`, else `None` if is assignment from empty sequence or deletion.
        - `plast`: The last source `FST`, else `None` if is assignment from empty sequence or deletion.

        **Returns:**
        - `fstloc`: location where the potentially modified `fst` source should be put, replacing whatever is at the
            location currently.
        """

        lines = fst.root._lines

        if not (bound_pre_post := self._fixup_expr_seq_bound(lines, seq_loc, fpre, fpost, flast)):  # if operating on whole sequence then just use the whole sequence location, if this doesn't return then one of `fpre` or `fpost` exists
            return seq_loc

        bound, fpre, fpost = bound_pre_post

        if not put_fst or not pfirst:  # `pfirst` may be None and `put_fst` not if assigning empty sequence, regardless, pure delete (or assign empty sequence, same), fflrst/last guaranteed to exist
            return self._expr_src_edit_locs(fst.root._lines,
                                            fstloc(ffirst.ln, ffirst.col, flast.end_ln, flast.end_col),
                                            bound, not fpost)[1]

        if ffirst:  # flast also exists, replacement
            put_ln      = ffirst.ln
            put_col     = ffirst.col
            put_end_ln  = flast.end_ln
            put_end_col = flast.end_col

        elif fpost:  # insertion
            put_end_ln  = put_ln  = fpost.ln
            put_end_col = put_col = fpost.col

        else:  # fpre guaranteed to exist, insertion
            put_end_ln  = put_ln  = fpre.end_ln
            put_end_col = put_col = fpre.end_col

        put_lines = put_fst._lines
        del_loc   = self._expr_src_edit_locs(fst.root._lines,
                                             fstloc(put_ln, put_col, put_end_ln, put_end_col), bound)[1]

        if not put_lines[0]:
            if re_empty_line.match(l := lines[put_ln], 0, put_col):  # strip leading newline from `put_fst` if location being put already has one - NOTE: could also check re_empty_line.match(put_lines[0]) instead of just put_lines[0]
                put_fst.put_lines(None, 0, 0, 1, re_empty_line_start.match(put_lines[1]).end(), False)

            elif (new_del_col := re_line_trailing_space.match(l,
                                                              bound.col if put_ln == bound.ln else 0,
                                                              del_col := del_loc.col).start(1)) < del_col:  # move del start to beginning of any trailing whitespace from put location before newline
                del_loc = fstloc(del_loc.ln, new_del_col, del_loc.end_ln, del_loc.end_col)

        if not put_lines[-1] and not re_empty_line.match(lines[(end_ln := del_loc.end_ln)], del_loc.end_col,  # add indentation to trailing newline in `put_fst` if there is stuff on the starting line of `put_loc` past the start point
            seq_loc.end_col if seq_loc.end_ln == end_ln else 0x7fffffffffffffff
        ):
            put_fst.put_lines([bistr(re_empty_line_start.match(lines[put_ln]).group())], ln := put_fst.end_ln, 0, ln, 0,
                              True, put_fst)

        if fpre:
            if (not (code := _next_src(lines, fpre.end_ln, fpre.end_col, del_loc.ln, del_loc.col)) or
                not code.src.startswith(',')
            ):
                put_fst.put_lines([bistr(', ' if put_lines[0] else ',')], 0, 0, 0, 0, False)

        if fpost:
            if not put_fst._maybe_add_comma(plast.end_ln, plast.end_col, False, True):
                if put_lines[-1].endswith(',', -1):  # slice being put ends on comma without a space, add one
                    put_fst.put_lines([bistr(' ')], ln := put_fst.end_ln, col := put_fst.end_col, ln, col, True,
                                      put_fst)

        return del_loc

    def get_slice_stmt(self, fst: 'FST', field: str, cut: bool, fmt: set[str] | frozenset[str], block_loc: fstloc,
                       ffirst: 'FST', flast: 'FST', fpre: Optional['FST'], fpost: Optional['FST'], *,
                       del_else_and_fin: bool = True, ret_all: bool = False,
    ) -> tuple[fstloc, fstloc | None, list[str] | None]:  # (copy_loc, del/put_loc, put_lines)
        """Copy or cut from block of statements. If cutting all elements from a deletable field like 'orelse' or
        'finalbody' then the corresponding 'else:' or 'finally:' will also be removed from the source (though not
        copied), and the formatting flags will apply to deleting any preceding comments and/or space. If you wish to
        apply different format flags to the copy and delete then copy what you want first then cut with different flags.

        **Parameters:**
        - `fst`: The source `FST` container that is being gotten from. No text has been changed at this point but the
            respective `AST` nodes may have been removed in case of `cut`.
        - `field`: The name of the field being gotten from, e.g. `'body'`, `'orelse'`, etc...
        - `cut`: If `False` the operation is a copy, `True` means cut.
        - `fmt`: Set of string formatting flags. Unrecognized and inapplicable flags are ignored, recognized flags are:
            - `'pre'`: Copy and delete contiguous comment block immediately preceding statement(s).
            - `'allpre'`: Copy and delete all comment blocks (possibly separated by empty lines) immediately preceding
                statement(s).
            - `'post'`: Copy and delete comment trailing on last line. Keep in mind this is the comment on the last
                statement of a body if last element of copy is a block element.
            - `'blkpost'`: Copy and delete single contiguous comment block following statement(s).
            - `'allpost'`: Copy and delete all comment blocks (possibly separated by empty lines) following
                statement(s).
            - `'pep8'`: Does not actually reformat code according to PEP 8, just deletes up one or two empty lines
                before functions and classes according to if they are at top level scope or not, but does not copy them.
            - `'pep81'`: Same as `'pep8'` except deletes only 1 empty line even at top level.
            - `'space*'`: Can be only `'space'` or with a number `'space3'`. Indicates that up to this many preceding
                empty lines should be deleted on a cut operation. If no count specified then it means all empty lines.
                Empty line continuations are considered empty lines. `'pep8'` can override `'space1'` for two lines at
                top level functions and classes.
            - `'postspace*'`: Same as `'space*'` except for trailing empty lines.
        - `block_loc`: A rough location suitable for checking comments outside of ASTS if `fpre` / `fpost` not
            available. Should include trailing newline after `flast` if one is present, but NO PARTS OF ASTS.
        - `ffirst`: The first `FST` being gotten.
        - `flast`: The last `FST` being gotten.
        - `fpre`: The preceding-first `FST`, not being gotten, may not exist if `ffirst` is first of seq.
        - `fpost`: The after-last `FST` not being gotten, may not exist if `flast` is last of seq.

        **Returns:**
        - If `cut=False` then only the first element of the return tuple is used for the copy and the other two are
            ignored so they don't need to be calculated. If `cut=True` then should return the copy location, a delete
            location and optionally lines to replace the deleted portion (which can only be non-coding source).
        """

        bound_ln, bound_col         = fpre.bloc[2:] if fpre else block_loc[:2]
        bound_end_ln, bound_end_col = fpost.bloc[:2] if fpost else block_loc[2:]

        lines      = fst.root._lines
        put_lines  = None
        pre_comms  = self.pre_comments(lines, bound_ln, bound_col, ffirst.bln, ffirst.bcol, fmt)
        post_comms = self.post_comments(lines, flast.bend_ln, flast.bend_col, bound_end_ln, bound_end_col, fmt)
        pre_semi   = not pre_comms and _prev_find(lines, bound_ln, bound_col, ffirst.ln, ffirst.col, ';',
                                                  True, comment=True, lcont=None)
        post_semi  = not post_comms and _next_find(lines, flast.end_ln, flast.end_col, bound_end_ln, bound_end_col, ';',
                                                   True, comment=True, lcont=None)
        copy_loc   = fstloc(*(pre_comms or ffirst.bloc[:2]), *(post_comms or flast.bloc[2:]))

        if fpre:  # set block start to just past prev statement or block open (colon)
            block_ln, block_col = fpre.bloc[2:]

        elif code := _prev_src(lines, bound_ln, bound_col, copy_loc.ln, copy_loc.col, False, False):
            block_ln, block_col, src  = code
            block_col                += len(src)

        else:
            block_ln  = bound_ln
            block_col = bound_col

        # get copy and delete locations according to possible combinations of preceding and trailing comments, semicolons and line continuation backslashes

        if pre_comms:
            if post_comms:
                del_loc = copy_loc

            else:
                if not post_semi:
                    end_ln, end_col = copy_loc[2:]

                else:
                    end_ln, end_col  = post_semi
                    end_col         += 1

                at_bound_end_ln = end_ln == bound_end_ln

                if code := _next_src(lines, end_ln, end_col, end_ln,
                                     bound_end_col if at_bound_end_ln else 0x7ffffffffffffff, True, True):
                    ln, col = copy_loc[:2]

                    if code.src.startswith('#'):
                        del_loc = fstloc(ln, col, end_ln, code.col)

                        if fpost:
                            put_lines = [re_empty_line_start.match(lines[copy_loc.ln]).group(0)]  # we know it starts a line because pre_comms exists

                    else:  # HACK FIX! TODO: do this properly, only here because '\\\n stmt' does not work at module level even though it works inside indented blocks, otherwise `del_loc` above would be sufficient unconditionally
                        del_loc = fstloc(ln, 0, bound_end_ln, bound_end_col)

                        if fpost:
                            put_lines = [ffirst.get_indent()]

                elif not at_bound_end_ln:
                    del_loc = fstloc(*pre_comms, end_ln + 1, 0)

                else:
                    del_loc = fstloc(*pre_comms, bound_end_ln, bound_end_col)

                    if fpost:  # ends at next statement, otherwise if fpost doesn't exist then was empty line after a useless trailing ';'
                        put_lines = [re_empty_line_start.match(lines[copy_loc.ln]).group(0)]  # we know it starts a line because pre_comms exists

        elif post_comms:
            if pre_semi:
                ln, col = post_comms
                del_loc = fstloc(*fpre.bloc[2:], ln := ln - (not col), len(lines[ln]))  # we know fpre exists because of pre_semi, leave trailing newline

            else:
                ln, col = copy_loc[:2]
                del_col = 0 if ln != block_ln else block_col
                del_loc = fstloc(ln, del_col, *post_comms)

        elif pre_semi:
            if post_semi:
                del_loc = fstloc(*pre_semi, *post_semi)

            else:
                end_ln, end_col = copy_loc[2:]
                at_bound_end_ln = end_ln == bound_end_ln

                if _next_src(lines, end_ln, end_col, end_ln,
                             bound_end_col if at_bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                    del_loc = fstloc(*fpre.bloc[2:], end_ln, end_col)
                else:
                    del_loc = fstloc(*fpre.bloc[2:], end_ln, len(lines[end_ln]))

        elif post_semi:
            ln, col          = copy_loc[:2]
            end_ln, end_col  = post_semi
            end_col         += 1
            at_bound_end_ln  = end_ln == bound_end_ln

            if code := _next_src(lines, end_ln, end_col, end_ln,
                                 bound_end_col if at_bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                if code.src.startswith('#'):
                    del_loc = fstloc(ln, col, end_ln, code.col)

                else:  # HACK FIX! TODO: do this properly, only here because '\\\n stmt' does not work at module level even though it works inside indented blocks, otherwise `del_loc` above would be sufficient unconditionally
                    del_loc = fstloc(ln, 0, bound_end_ln, bound_end_col)

                    if fpost:
                        put_lines = [ffirst.get_indent()]  # SHOULDN'T DO THIS HERE!!!

            else:
                del_col = 0 if ln != block_ln else block_col

                if not at_bound_end_ln:
                    del_loc = fstloc(ln, del_col, end_ln + 1, 0)
                else:
                    del_loc = fstloc(ln, col if fpost else del_col, bound_end_ln, bound_end_col)

        else:
            ln, col, end_ln, end_col = copy_loc
            at_bound_end_ln          = end_ln == bound_end_ln

            if code := _next_src(lines, end_ln, end_col, end_ln,
                                 bound_end_col if at_bound_end_ln else 0x7ffffffffffffff, True, True):  # comment or backslash
                del_loc = fstloc(ln, col, end_ln, code.col)

            else:
                del_col = 0 if ln != block_ln else block_col

                if not at_bound_end_ln:
                    del_loc = fstloc(ln, del_col, end_ln + 1, 0)
                else:
                    del_loc = fstloc(ln, del_col, bound_end_ln, bound_end_col)

        # special case of deleting everything from a block

        if not fpre and not fpost:
            if del_else_and_fin and ((is_finally := field == 'finalbody') or  # remove 'else:' or 'finally:' (but not 'elif ...:' as that lives in first cut statement)
                (field == 'orelse' and not lines[ffirst.bln].startswith('elif', ffirst.bcol))
            ):
                del_ln, del_col, del_end_ln, del_end_col = del_loc

                del_ln, del_col = _prev_find(lines, bound_ln, bound_col, del_ln, del_col,
                                             'finally' if is_finally else 'else', False, comment=False, lcont=False)  # `first=False` because have to skip over ':'

                if put_lines:
                    put_lines[0] = lines[del_ln][:del_col] + put_lines[0]  # prepend block start indentation to existing indentation, silly but whatever

                if pre_pre_comms := self.pre_comments(lines, bound_ln, bound_col, del_ln, 0, fmt):
                    del_ln, _ = pre_pre_comms

                del_loc = fstloc(del_ln, 0, del_end_ln, del_end_col)

            elif flast is ffirst:  # avoid deleting trailing newline of only statement just past block open
                del_ln, del_col, del_end_ln, del_end_col = del_loc

                if not del_end_col and del_ln == block_ln:
                    del_loc = fstloc(del_ln, del_col, (ln := del_end_ln - 1), len(lines[ln]))

        # delete preceding and trailing empty lines according to 'pep8' and 'space' format flags

        space     = any((s := f).startswith('space') for f in fmt) and (float('inf') if s == 'space' else int(s[5:]))
        postspace = any((s := f).startswith('postspace') for f in fmt) and (
                        float('inf') if s == 'postspace' else int(s[9:]))

        if (is_pep8 := 'pep8' in fmt) or 'pep81' in fmt:
            pep8space = 2 if is_pep8 and isinstance(fst.a, mod) else 1

            if fpre and isinstance(ffirst.a, NAMED_SCOPE) and (fpre.pfield.idx or
                                                               not isinstance(a := fpre.a, Expr) or
                                                               not isinstance(v := a.value, Constant) or
                                                               not isinstance(v.value, str)):
                space = max(space, pep8space)

            elif fpost and isinstance(flast.a, NAMED_SCOPE):
                postspace = max(postspace, pep8space)

        del_ln, del_col, del_end_ln, del_end_col = del_loc

        if space:
            new_del_ln = max(bound_ln + bool(bound_col), del_ln - space)  # first possible full empty line to delete to

            if del_ln > new_del_ln and (not del_col or re_empty_line.match(lines[del_ln], 0, del_col)):
                if code := _prev_src(lines, new_del_ln, 0, del_ln, 0, True, False):
                    new_del_ln = code.ln + 1

                if new_del_ln < del_ln:
                    indent    = lines[del_ln][:del_col]
                    put_lines = [indent + put_lines[0], *put_lines[1:]] if put_lines else [indent]
                    del_ln    = new_del_ln
                    del_col   = 0

        if postspace:
            if not del_end_col:
                new_del_end_ln = min(bound_end_ln, del_end_ln + postspace)  # last possible end line to delete to
                del_end_ln     = (code.ln
                                  if (code := _next_src(lines, del_end_ln, 0, new_del_end_ln, 0, True, True)) else
                                  new_del_end_ln)

            elif del_end_col == len(lines[del_end_ln]):
                new_del_end_ln = min(bound_end_ln, del_end_ln + postspace + 1)  # account for not ending on newline
                del_end_ln     = (code.ln - 1
                                  if (code := _next_src(lines, del_end_ln, del_end_col, new_del_end_ln, 0, True, True)) else
                                  new_del_end_ln - 1)
                del_end_col    = len(lines[del_end_ln])

        del_loc = fstloc(del_ln, del_col, del_end_ln, del_end_col)

        # remove possible line continuation preceding delete start position because could link to invalid following block statement

        del_ln, del_col, del_end_ln, del_end_col = del_loc

        if (del_ln > bound_ln and (not del_col or re_empty_line.match(lines[del_ln], 0, del_col)) and
            lines[del_ln - 1].endswith('\\')  # the endswith() is not definitive because of comments
        ):
            new_del_ln  = del_ln - 1
            new_del_col = 0 if new_del_ln != bound_ln else bound_col

            if code := _prev_src(lines, new_del_ln, new_del_col, new_del_ln, 0x7fffffffffffffff, True, False):  # skip over lcont but not comment if is there because that invalidates quick '\\' check above
                new_del_col = None if (src := code.src).startswith('#') else code.col + len(src)

            if new_del_col is not None:
                del_loc   = fstloc(new_del_ln, new_del_col, del_end_ln, del_end_col)
                indent    = lines[del_ln][:del_col]
                put_lines = ['', indent + put_lines[0], *put_lines[1:]] if put_lines else ['', indent]

        # finally done

        if ret_all:
            return (copy_loc, del_loc, put_lines, fstloc(bound_ln, bound_col, bound_end_ln, bound_end_col),
                    pre_comms, post_comms, pre_semi, post_semi, (block_ln, block_col))

        return copy_loc, del_loc, put_lines

    def _format_ends(self, fst: 'FST', put_fst: 'FST', fmt: set[str] | frozenset[str],
                     block_loc: fstloc, put_loc: fstloc, fpre: Optional['FST'], fpost: Optional['FST'],
                     del_lines: list[str] | None):
        """Add preceding and trailing newlines as needed. We always insert statements (or blocks of them) as their own
        lines but may also add newlines according to PEP8."""

        lines     = fst.root._lines
        put_lines = put_fst._lines
        put_body  = put_fst.a.body

        if is_pep8 := bool(put_body) and ((is_pep81 := 'pep81' in fmt) or 'pep8' in fmt):  # no pep8 checks if only text being put (no AST body)
            pep8space = 2 if not is_pep81 and isinstance(fst.a, mod) else 1

        # prepend = 2 if not fst.is_root or put_loc.col else 0  # don't put initial empty line if putting on a first AST line at root
        prepend = 2 if put_loc.col else 0  # don't put initial empty line if putting on a first AST line at root

        if is_pep8 and fpre and (isinstance(a := fpre.a, NAMED_SCOPE) or isinstance(put_body[0], NAMED_SCOPE)):  # preceding space
            if pep8space == 1 or (not fpre.pfield.idx and isinstance(a, Expr) and   # docstring
                                    isinstance(v := a.value, Constant) and isinstance(v.value, str)):
                want = 1
            else:
                want = pep8space

            if need := (want if not re_empty_line.match(put_lines[0]) else 1 if want == 2 and (  # how many empty lines at start of put_fst?
                        len(put_lines) < 2 or not re_empty_line.match(put_lines[1])) else 0):
                bound_ln = block_loc.ln
                ln       = put_loc.ln

                if not (put_col := put_loc.col):
                    need += 2

                if ln > bound_ln and re_empty_line.match(lines[ln], 0, put_col):  # reduce need by leading empty lines present in destination
                    if need := need - 1:
                        if (ln := ln - 1) > bound_ln and re_empty_line.match(lines[ln]):
                            need = 0

                prepend += need

        if not (is_pep8 and fpost and (isinstance(put_body[-1], NAMED_SCOPE) or isinstance(fpost.a, NAMED_SCOPE))):  # trailing space
            postpend = bool((l := put_lines[-1]) and not re_empty_line.match(l))

        else:
            postpend = pep8space + 1
            ln       = len(put_lines) - 1

            while postpend:  # how many empty lines at end of put_fst?
                if (l := put_lines[ln]) and  not re_empty_line.match(l):
                    break

                postpend -= 1

                if (ln := ln - 1) < 0:
                    break

            if postpend:  # reduce needed postpend by trailing empty lines present in destination
                _, _, end_ln, end_col = put_loc
                end_lines             = len(lines)

                while postpend and re_empty_line.match(lines[end_ln], end_col):
                    postpend -= 1
                    end_col   = 0

                    if (end_ln := end_ln + 1) >= end_lines:
                        break

                postpend += not postpend

        if prepend:
            put_fst.put_lines([''] * prepend, 0, 0, 0, 0, False)

        if postpend:
            put_lines.extend([bistr('')] * postpend)

        if del_lines:
            put_lines[-1] = bistr(put_lines[-1] + del_lines[0])

            put_lines.extend(bistr(s) for s in del_lines[1:])

        put_fst.touch()

    def put_slice_stmt(self, fst: 'FST', put_fst: 'FST', field: str, fmt: set[str] | frozenset[str], docstr: bool | str,
                       block_loc: fstloc, opener_indent: str, block_indent: str,
                       ffirst: 'FST', flast: 'FST', fpre: Optional['FST'], fpost: Optional['FST'],
    ) -> fstloc:  # put_loc
        """Put to block of statements(ish). Calculates put location and modifies `put_fst` as necessary to create proper
        code. The "ish" in statemnents means this can be used to put `ExceptHandler`s to a 'handlers' field or
        `match_case`s to a 'cases' field.

        If `ffirst` and `flast` are `None` it means that it is a pure insertion and no elements are being removed. In
        this case use `fpre` and `fpost` to determine locations, one of which could be missing if the insertion is at
        the beginning or end of the sequence. If all of these are `None` then this indicates a put to empty block, in
        which case use `fst`, `field` and/or `block_loc` for location.

        The first line of `put_fst` is unindented and should remain so as it is concatenated with the target line at the
        point of insertion. The last line of `put_fst` is likewise prefixed to the line following the deleted location.

        There is always an insertion or replacement operation if this is called, it is never just a delete or an empty
        assignment to an empty slice.

        If assigning to non-existent `orelse` or `finalbody` fields then the appropriate `else:` or `finally:` is
        prepended to `put_fst` for the final put. If replacing whole body of 'orelse' or 'finalbody' then the original
        'else:' or 'finally:' is not deleted (along with any preceding comments or spaces).

        Block being inserted into assumed to be normalized (no statement or multiple statements on block opener logical
        line).

        **Parameters:**
        - `fst`: The destination `FST` container that is being put to.
        - `put_fst`: The block which is being put. Must be a `Module` with a `body` of one or multiple statmentish
            nodes. Not indented, indent and mutate this object to set what will be put at `put_loc`.
        - `field`: The name of the field being gotten from, e.g. `'body'`, `'orelse'`, etc...
        - `cut`: If `False` the operation is a copy, `True` means cut.
        - `fmt`: Set of string formatting flags. Unrecognized and inapplicable flags are ignored, recognized flags are:
            - `'pre'`: Replace contiguous comment block immediately preceding statement(s).
            - `'allpre'`: Replace all comment blocks (possibly separated by empty lines) immediately preceding
                statement(s).
            - `'post'`: replace comment trailing on last line. Keep in mind this is the comment on the last
                statement of a body if last element of copy is a block element.
            - `'blkpost'`: Replace single contiguous comment block following statement(s).
            - `'allpost'`: Replace all comment blocks (possibly separated by empty lines) following statement(s).
            - `'pep8'`: Does not actually reformat code according to PEP 8, just inserts up one or two empty lines
                before non-first function or class being put according to destination if is top level scope or not. Also
                removes this number of spaces if replacing a function or class so balances out in that case. In the
                future may specify additional PEP 8 behavior.
            - `'space*'`: Can be only `'space'` or with a number `'space3'`. Indicates that up to this many preceding
                empty lines should be replaced. If no count specified then it means all empty lines. Empty line
                continuations are considered empty lines. `'pep8'` applies after `'space'` to add preceding lines.
            - `'elif'`: If putting a single `If` statement to an `orelse` field of a parent `If` statement then put it
                as an `elif`.
        - `opener_indent`: The indent string of the block opener being put to (`if`, `with`, `class`, etc...), not the
            statements in the block.
        - `block_indent`: The indent string to be applied to `put_fst` statements in the block, which is the total
            indentation (including `opener_indent`) of the statements in the block.
        - `block_loc`: A rough location ancompassing the block part being edited outside of ASTS, used mostly if `fpre`
            / `fpost` not available. Always after `fpre` if present and before `fpost` if present. May include comments,
            line continuation backslashes and non-AST coding source like 'else:', but NO PARTS OF ASTS. May start before
            start or just past the block open colon.
        - `ffirst`: The first destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `flast`: The last destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `fpre`: The preceding-first destination `FST` or `fstloc`, not being replaced, may not exist if `ffirst` is
            first of seq.
        - `fpost`: The after-last destination `FST` or `fstloc` not being replaced, may not exist if `flast` is last of
            seq.

        **Returns:**
        - `fstloc`: location where the potentially modified `fst` source should be put, replacing whatever is at the
            location currently.
        """

        lines      = fst.root._lines
        put_lines  = put_fst._lines
        put_body   = put_fst.a.body
        is_handler = field == 'handlers'
        is_orelse  = field == 'orelse'

        if not ffirst:  # pure insertion
            is_elif = (not fpre and not fpost and is_orelse and 'elif' in fmt and len(b := put_body) == 1 and
                       isinstance(b[0], If) and isinstance(fst.a, If))

            put_fst.indent_lns(opener_indent if is_handler or is_elif else block_indent, docstr=docstr, skip=0)

            if fpre:  # with preceding statement, maybe trailing statement
                ln, col, end_ln, end_col = block_loc

                while ln < end_ln:
                    if not (code := _next_src(lines, ln, col, ln, 0x7fffffffffffffff, True, True)):
                        put_loc = fstloc(ln, col, ln + 1, 0)

                        break

                    cln, ccol, csrc = code

                    if csrc.startswith('#'):
                        if cln < end_ln:
                            put_loc = fstloc(cln, ccol + len(csrc), cln + 1, 0)
                        else:
                            put_loc = fstloc(cln, ccol + len(csrc), cln, end_col)

                        break

                    if csrc == ';':
                        col = ccol + 1

                    else:
                        assert csrc == '\\'

                        ln  += 1
                        col  = 0

                else:
                    if fpost:  # next statement on semicolon separated line continuation
                        indent  = bistr(block_indent)
                        put_loc = block_loc

                    else:
                        indent  = bistr('')
                        put_loc = fstloc(end_ln, re_line_trailing_space.match(lines[end_ln], col).start(1),
                                         end_ln, end_col)

                    if (l := put_lines[-1]) and not re_empty_line.match(l):
                        put_lines.append(indent)
                    else:
                        put_lines[-1] = indent

                    put_fst.touch()

            elif fpost:  # no preceding statement, only trailing
                if is_handler or fst.is_root:  # special case, start will be after last statement or just after 'try:' colon or if is mod then there is no colon
                    ln, col = block_loc[:2]

                else:
                    ln, col  = _prev_find(lines, *block_loc, ':', True)
                    col     += 1

                if code := _next_src(lines, ln, col, *block_loc[2:], True, None):
                    ln, col, src  = code
                    col          += len(src)

                    assert ln < block_loc.end_ln

                if block_loc.end_ln > ln:
                    put_loc = fstloc(ln, col, ln + 1, 0)
                else:
                    put_loc = fstloc(ln, col, ln, block_loc.end_col)

                if (l := put_lines[-1]) and not re_empty_line.match(l):
                    put_lines.append(bistr(''))
                else:
                    put_lines[-1] = bistr('')

                put_fst.touch()

            else:  # insertion into empty block
                if is_elif:
                    ln, col, end_ln, end_col = put_body[0].f.bloc

                    put_fst.put_lines(['elif'], ln, col, ln, col + 2, False)  # replace 'if' with 'elif'

                elif is_orelse:  # need to create these because they not there if body empty
                    put_fst.put_lines([opener_indent + 'else:', ''], 0, 0, 0, 0, False)
                elif field == 'finalbody':
                    put_fst.put_lines([opener_indent + 'finally:', ''], 0, 0, 0, 0, False)

                ln, col, end_ln, end_col = block_loc

                single_ln = ln == end_ln

                if code := _next_src(lines, ln, col, ln, end_ln if single_ln else 0x7fffffffffffffff, True, False):
                    assert code.src.startswith('#')  # not expecting anything else after colon in empty block, '\\' is ignored in search

                    col = code.col + len(code.src)  # we want to put after any post-comments

                if single_ln:
                    put_loc = fstloc(ln, col, ln, end_col)
                else:
                    put_loc = fstloc(ln, col, ln + 1, 0)

            self._format_ends(fst, put_fst, fmt, block_loc, put_loc, fpre, fpost, None)

            return put_loc

        # replacement

        put_fst.indent_lns(opener_indent if is_handler else block_indent, docstr=docstr, skip=0)

        copy_loc, put_loc, del_lines, bound, pre_comms, post_comms, pre_semi, post_semi, block_start = (
            self.get_slice_stmt(fst, field, True, fmt, block_loc, ffirst, flast, fpre, fpost,
                                del_else_and_fin=False, ret_all=True))

        # print(f'{copy_loc=}\n{put_loc=}\n{del_lines=}')  # DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG! DEBUG!

        if pre_semi:
            if post_semi:
                raise NotImplementedError

            else:
                pass

        elif post_semi:
            pass

        else:
            pass

        if put_loc.col:
            put_ln, put_col, put_end_ln, put_end_col = put_loc

            if re_empty_line.match(l := lines[put_ln][:put_col]):
                put_loc = fstloc(put_ln, 0, put_end_ln, put_end_col)

                if del_lines:
                    del_lines[-1] = del_lines[-1] + l
                else:
                    del_lines = [l]

            elif del_lines and not del_lines[0]:
                del del_lines[0]

        self._format_ends(fst, put_fst, fmt, block_loc, put_loc, fpre, fpost, del_lines)

        return put_loc


class FST:
    """Preserve AST formatting information and easy manipulation."""

    a:            AST                        ; """The actual `AST` node."""
    parent:       Optional['FST']            ; """Parent `FST` node, `None` in root node."""
    pfield:       astfield | None            ; """The `astfield` location of this node in the parent, `None` in root node."""
    root:         'FST'                      ; """The root node of this tree, `self` in root node."""
    _loc:         fstloc | None              # cache, MAY NOT EXIST!
    _bloc:        fstloc | None              # cache, MAY NOT EXIST! bounding location, including preceding decorators

    # ROOT ONLY
    parse_params: dict[str, Any]             ; """The parameters to use for any `ast.parse()` that needs to be done (filename, type_comments, feature_version), root node only."""
    indent:       str                        ; """The default single level of block indentation string for this tree when not available from context, root node only."""
    _lines:       list[bistr]

    # class attributes
    src_edit:     FSTSrcEdit = FSTSrcEdit()  ; """@private"""
    is_FST:       bool       = True          ; """@private"""  # for quick checks vs. `fstloc`

    @property
    def is_root(self) -> bool:
        """`True` for the root node, `False` otherwise."""

        return self.parent is None

    @property
    def is_stmt(self) -> bool:
        """Is a `stmt` or `mod` node."""

        return isinstance(self.a, (stmt, mod))

    @property
    def is_stmtish(self) -> bool:
        """Is a `stmt`, `ExceptHandler`, `match_case` or `mod` node."""

        return isinstance(self.a, STATEMENTISH_OR_MOD)

    @property
    def is_block(self) -> bool:
        """Is a node which opens a block. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `For`,
        `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`, `TryStar`, `ExceptHandler`, `match_case`, and
        `mod`."""

        return isinstance(self.a, BLOCK_OR_MOD)

    @property
    def is_scope(self) -> bool:
        """Is a node which opens a scope. Types include `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Lambda`,
        `ListComp`, `SetComp`, `DictComp`, `GeneratorExp`, and `mod`."""

        return isinstance(self.a, SCOPE_OR_MOD)

    @property
    def is_named_scope(self) -> bool:
        """Is a node which opens a named scope. Types include `FunctionDef`, `AsyncFunctionDef`,  `ClassDef` and
        `mod`."""

        return isinstance(self.a, NAMED_SCOPE_OR_MOD)

    @property
    def is_anon_scope(self) -> bool:
        """Is a node which opens an anonymous scope. Types include `Lambda`, `ListComp`, `SetComp`, `DictComp` and
        `GeneratorExp`."""

        return isinstance(self.a, ANONYMOUS_SCOPE)

    @property
    def parent_stmt(self) -> Optional['FST']:
        """The first parent which is a `stmt` or `mod` node (if any)."""

        while (self := self.parent) and not isinstance(self.a, (stmt, mod)):
            pass

        return self

    @property
    def parent_stmtish(self) -> Optional['FST']:
        """The first parent which is a `stmt`, `ExceptHandler`, `match_case` or `mod` node (if any)."""

        while (self := self.parent) and not isinstance(self.a, STATEMENTISH_OR_MOD):
            pass

        return self

    @property
    def parent_block(self) -> Optional['FST']:
        """The first parent which opens a block that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `For`, `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`,
        `TryStar`, `ExceptHandler`, `match_case`, and `mod`."""

        while (self := self.parent) and not isinstance(self.a, BLOCK_OR_MOD):
            pass
        return self

    @property
    def parent_scope(self) -> Optional['FST']:
        """The first parent which opens a scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `Lambda`, `ListComp`, `SetComp`, `DictComp`, `GeneratorExp`, and `mod`."""

        while (self := self.parent) and not isinstance(self.a, SCOPE_OR_MOD):
            pass

        return self

    @property
    def parent_named_scope(self) -> Optional['FST']:
        """The first parent which opens a named scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef` and `mod`."""

        while (self := self.parent) and not isinstance(self.a, NAMED_SCOPE_OR_MOD):
            pass

        return self

    @property
    def lines(self) -> list[str] | None:
        """Whole lines which contain this node, may also contain parts of enclosing nodes. All source lines at root."""

        if self.is_root:
            return self._lines
        elif loc := self.bloc:
            return self.root._lines[loc.ln : loc.end_ln + 1]
        else:
            return None

    @property
    def src(self) -> str | None:
        """Source code of this node clipped out of `lines` as a single string, without any dedentation. Whole source
        at root."""

        if self.is_root:
            return '\n'.join(self._lines)
        elif loc := self.bloc:
            return '\n'.join(self.get_lines(*loc))
        else:
            return None

    @property
    def has_own_loc(self) -> bool:
        """`True` when the node has its own `loc` otherwise `False` if no `loc` or `loc` is calculated from children."""

        return hasattr(self.a, 'end_col_offset')

    @property
    def loc(self) -> fstloc | None:
        """Zero based character indexed location of node (may not be entire location if node has decorators). Not all
        nodes have locations, specifically leaf nodes like operations and `expr_context`. Other nodes which normally
        don't have locations like `arguments` have this location calculated from their children or source."""

        try:
            return self._loc
        except AttributeError:
            pass

        ast = self.a

        try:
            ln             = ast.lineno - 1
            col_offset     = ast.col_offset
            end_ln         = ast.end_lineno - 1
            end_col_offset = ast.end_col_offset

        except AttributeError:
            if not self.parent:
                loc = fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))
            else:
                loc = self._loc_from_children()

        else:
            col     = self.root._lines[ln].b2c(col_offset)
            end_col = self.root._lines[end_ln].b2c(end_col_offset)
            loc     = fstloc(ln, col, end_ln, end_col)

        self._loc = loc

        return loc

    @property
    def bloc(self) -> fstloc:
        """Entire location of node, including any preceding decorators. Not all nodes have locations but any node which
        has a `.loc` will have a `.bloc`."""

        try:
            return self._bloc
        except AttributeError:
            pass

        if not (loc := self.loc):
            bloc = None
        elif decos := getattr(self.a, 'decorator_list', None):
            bloc = fstloc(decos[0].f.ln, loc[1], loc[2], loc[3])  # column of deco '@' will be same as our column
        else:
            bloc = loc

        self._bloc = bloc

        return bloc

    @property
    def ln(self) -> int:
        """Line number of the first line of this node (0 based)."""

        return (l := self.loc) and l[0]

    @property
    def col(self) -> int:  # char index
        """CHARACTER index of the start of this node (0 based)."""

        return (l := self.loc) and l[1]

    @property
    def end_ln(self) -> int:  # 0 based
        """Line number of the LAST LINE of this node (0 based)."""

        return (l := self.loc) and l[2]

    @property
    def end_col(self) -> int:  # char index
        """CHARACTER index one past the end of this node (0 based)."""

        return (l := self.loc) and l[3]

    @property
    def bln(self) -> int:  # bounding location including @decorators
        """Line number of the first line of this node or the first preceding decorator (0 based)."""

        return (l := self.bloc) and l[0]

    bcol     = col  # for symmetry, also may eventually be distinct
    bend_ln  = end_ln
    bend_col = end_col

    @property
    def lineno(self) -> int:  # 1 based
        """Line number of the first line of this node (1 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and loc[0] + 1

    @property
    def col_offset(self) -> int:  # byte index
        """BYTE index of the start of this node (0 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and self.root._lines[loc[0]].c2b(loc[1])

    @property
    def end_lineno(self) -> int:  # 1 based
        """Line number of the LAST LINE of this node (1 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and loc[2] + 1

    @property
    def end_col_offset(self) -> int:  # byte index
        """CHARACTER index one past the end of this node (0 based), available for all nodes which have `loc`."""

        return (loc := self.loc) and self.root._lines[loc[2]].c2b(loc[3])

    @property
    def is_mock(self) -> bool:
        """`True` if is a `locmock()` for another node."""

        return self.a.f is not self

    @property
    def f(self):
        """@private"""

        raise RuntimeError("you probably think you're accessing an AST node, but you're not, "
                           "you're accessing an FST node")

    # ------------------------------------------------------------------------------------------------------------------

    def _make_fst_tree(self, stack: list['FST'] | None = None):
        """Create tree of FST nodes, one for each AST node from root. Call only on root."""

        if stack is None:
            stack = [self]

        while stack:
            f = stack.pop()
            a = f.a

            if isinstance(a, (expr_context, unaryop, operator, boolop, cmpop)) and (parent := f.parent):  # ast.parse() reuses simple objects, we need all objects to be unique
                f.a = a = a.__class__()
                a.f = f

                f.pfield.set(parent.a, a)

            else:
                for name, child in iter_fields(a):
                    if isinstance(child, AST):
                        stack.append(FST(child, f, astfield(name)))
                    elif isinstance(child, list):
                        stack.extend(FST(a, f, astfield(name, idx))
                                     for idx, a in enumerate(child) if isinstance(a, AST))

    def _unmake_fst_tree(self, stack: list[AST] | None = None, root: Optional['FST'] = None):
        """Destroy a tree of FST nodes by breaking links."""

        if stack is None:
            stack = [self.a]

        while stack:  # make sure these bad ASTs can't hurt us anymore
            if a := stack.pop():  # could be `None`s in there
                f   = a.f
                f.a = a.f = f.root = f.parent = None

                stack.extend(iter_child_nodes(a))

        if root:
            root.a.f = root.a = root.root = root.parent = None

    def _repr_tail(self) -> str:
        try:
            loc = self.loc
        except Exception:  # maybe in middle of operation changing locations and lines
            loc = '????'

        self.touchall(False)  # for debugging because we may have cached locs which would not have otherwise been cached during execution

        tail = (' MOCK ROOT' if self.is_root else ' MOCK') if self.is_mock else (' ROOT' if self.is_root else '')

        return f'{tail} {loc[0]},{loc[1]} -> {loc[2]},{loc[3]}' if loc else tail

    def _dump(self, full: bool = False, indent: int = 2, cind: str = '', prefix: str = '', linefunc: Callable = print,
              compact: bool = False):
        tail = self._repr_tail()
        sind = ' ' * indent
        ast  = self.a

        if compact:
            if isinstance(ast, Name):
                linefunc(f'{cind}{prefix}Name {ast.id!r} {ast.ctx.__class__.__qualname__}{" .." * bool(tail)}{tail}')

                return

            if isinstance(ast, Constant):
                if ast.kind is None:
                    linefunc(f'{cind}{prefix}Constant {ast.value!r}{" .." * bool(tail)}{tail}')
                else:
                    linefunc(f'{cind}{prefix}Constant {ast.value!r} {ast.kind}{" .." * bool(tail)}{tail}')

                return

        linefunc(f'{cind}{prefix}{ast.__class__.__qualname__}{" .." * bool(tail)}{tail}')

        for name, child in iter_fields(ast):
            is_list = isinstance(child, list)

            if compact:
                if child is None:
                    continue

                if name in ('ctx', 'op'):
                    linefunc(f'{sind}{cind}.{name} {child.__class__.__qualname__ if isinstance(child, AST) else child}')

                    continue

                if (name in ('type', 'id', 'attr', 'module', 'arg', 'vararg', 'kwarg', 'rest', 'format_spec',
                             'name', 'value', 'left', 'right', 'operand', 'returns', 'target',
                             'annotation', 'iter', 'test','exc', 'cause', 'msg', 'elt', 'key', 'func',
                             'slice', 'lower', 'upper', 'step', 'guard', 'optional_vars',
                             'cls', 'bound', 'default_value',
                             'type_comment', 'lineno', 'tag',)
                            or (not is_list and name in
                             ('body', 'orelse'))
                ):
                    if isinstance(child, AST):
                        child.f._dump(full, indent, cind + sind, f'.{name} ', linefunc, compact)
                    else:
                        linefunc(f'{sind}{cind}.{name} {child!r}')

                    continue

                if not full and (isinstance(child, arguments) and not child.posonlyargs and not child.args and not child.vararg
                        and not child.kwonlyargs and not child.kwarg):
                    continue

            if full or (child != []):
                linefunc(f'{sind}{cind}.{name}{f"[{len(child)}]" if is_list else ""}')

            if is_list:
                for i, ast in enumerate(child):
                    if isinstance(ast, AST):
                        ast.f._dump(full, indent, cind + sind, f'{i}] ', linefunc, compact)
                    else:
                        linefunc(f'{sind}{cind}{i}] {ast!r}')

            elif isinstance(child, AST):
                child.f._dump(full, indent, cind + sind * 2, '', linefunc, compact)
            else:
                linefunc(f'{sind}{sind}{cind}{child!r}')

    def _prev_ast_bound(self, with_loc: bool | Literal['own'] | Literal['allown'] = True) -> tuple[int, int]:
        """Get a prev bound for search after any ASTs for this object. This is safe to call for nodes that live inside
        nodes without their own locations if `with_loc='allown'`."""

        if prev := self.prev_step(with_loc, recurse_self=False):
            return prev.bloc[2:]

        return 0, 0

    def _next_ast_bound(self, with_loc: bool | Literal['own'] | Literal['allown'] = True) -> tuple[int, int]:
        """Get a next bound for search before any ASTs for this object. This is safe to call for nodes that live inside
        nodes without their own locations if `with_loc='allown'`."""

        if next := self.next_step(with_loc, recurse_self=False):
            return next.bloc[:2]

        return len(lines := self.root._lines) - 1, len(lines[-1])

    def _lpars(self, with_loc: bool | Literal['own'] | Literal['allown'] = True) -> tuple[int, int, int, int, int]:
        """Return the `ln` and `col` of the leftmost and ante-leftmost opening parentheses and the total number of
        opening parentheses. Doesn't take into account anything like enclosing argument parentheses, just counts. The
        leftmost bound used is the end of the previous sibling, or the start of that parent if there isn't one, or (0,0)
        if no parent.

        **Parameters:**
        - `with_loc`: Parameter to use for AST bound search. `True` normally or `'allown'` in special cases like
            searching for parentheses to figure out node location from children.

        **Returns:**
        - `(ln, col, ante_ln, ante_col, npars)`: The leftmost and ante-leftmost positions and total count of opening
            parentheses encountered.
        """

        return _prev_pars(self.root._lines, *self._prev_ast_bound(with_loc), *self.bloc[:2])

    def _rpars(self, with_loc: bool | Literal['own'] | Literal['allown'] = True) -> tuple[int, int, int, int, int]:
        """Return the `end_ln` and `end_col` of the rightmost and ante-rightmost closing parentheses and the total
        number of closing parentheses. Doesn't take into account anything like enclosing argument parentheses, just
        counts. The rightmost bound used is the start of the next sibling, or the end of that parent if there isn't one,
        or the end of `self.root._lines`.

        **Parameters:**
        - `with_loc`: Parameter to use for AST bound search. `True` normally or `'allown'` in special cases like
            searching for parentheses to figure out node location from children.

        **Returns:**
        - `(end_ln, end_col, ante_end_ln, ante_end_col, npars)`: The rightmost and ante-rightmost positions and total
            count of closing parentheses encountered.
        """

        return _next_pars(self.root._lines, *self.bloc[2:], *self._next_ast_bound(with_loc))

    def _loc_from_children(self) -> fstloc | None:
        """Meant to handle figuring out `loc` for `arguments`, `withitem`, `match_case` and `comprehension`. Use on
        other types of nodes may or may not work correctly, especially not on `Tuple`."""

        if not (first := self.first_child(True)):
            return None

        ast   = self.a
        last  = self.last_child(True)
        lines = self.root._lines

        if isinstance(ast, match_case):
            start = _prev_find(lines, 0, 0, first.ln, first.col, 'case')  # we can use (0,0) because we know "case" starts on a newline

            if ast.body:
                return fstloc(*start, last.bend_ln, last.bend_col)

            end_ln, end_col = _next_find(lines, last.bend_ln, last.bend_col, len(lines) - 1, len(lines[-1]), ':')  # special case, deleted whole body, end must be set to just past the colon (which MUST follow somewhere there)

            return fstloc(*start, end_ln, end_col + 1)

        start_ln, start_col, ante_start_ln, ante_start_col, nlpars = first._lpars('allown')

        if not nlpars:  # not really needed, but juuust in case
            start_ln  = first.bln
            start_col = first.bcol

        end_ln, end_col, ante_end_ln, ante_end_col, nrpars = last._rpars('allown')

        if not nrpars:
            end_ln  = last.bend_ln
            end_col = last.bend_col

        elif isinstance(ast, comprehension):
            if ((parent := self.parent) and isinstance(parent.a, GeneratorExp) and  # correct for parenthesized GeneratorExp
                self.pfield.idx == len(parent.a.generators) - 1
            ):
                end_ln  = ante_end_ln
                end_col = ante_end_col

        if isinstance(ast, arguments):
            if ast.posonlyargs or ast.args:
                leading_stars = None  # no leading stars
            elif ast.vararg or ast.kwonlyargs:
                leading_stars = '*'  # leading star just before varname or bare leading star with comma following
            elif ast.kwarg:
                leading_stars = '**'  # leading double star just before varname

            if ((code := _next_src(lines, end_ln, end_col, len(lines) - 1, len(lines[-1])))  # trailing comma
                and code.src.startswith(',')
            ):
                end_ln, end_col, _  = code
                end_col            += 1

            elif (parent := self.parent) and isinstance(parent.a, (FunctionDef, AsyncFunctionDef)):
                end_ln  = ante_end_ln
                end_col = ante_end_col

                if not leading_stars:
                    start_ln  = ante_start_ln
                    start_col = ante_start_col

            if leading_stars:  # find star to the left, we know it exists so we don't check for None return
                start_ln, start_col = _prev_find(lines, *first._prev_ast_bound('allown'), start_ln, start_col,
                                                 leading_stars)

        return fstloc(start_ln, start_col, end_ln, end_col)

    def _dict_key_or_mock_loc(self, key: AST | None, value: 'FST') -> Union['FST', fstloc]:
        """Return same dictionary key FST if exists else create and return a location for the preceding '**' code."""

        if key:
            return key.f

        if idx := value.pfield.idx:
            f   = value.parent.values[idx - 1]  # because of multiline strings, could be a fake comment start inside one which hides a valid '**'
            ln  = f.end_ln
            col = f.end_col

        else:
            ln  = self.ln
            col = self.col

        ln, col, s = _prev_src(self.root._lines, ln, col, value.ln, value.col)  # '**' must be there
        end_col    = col + len(s)

        assert s.endswith('**')

        return fstloc(ln, end_col - 2, ln, end_col)

    def _floor_start_pos(self, lineno: int, col_offset: int, self_: bool = True):  # because of zero-length spans like evil unparenthesized zero-length tuples
        """Walk up parent chain (starting at `self`) setting `.lineno` and `.col_offset` to `lineno` and `col_offset` if
        they are past it. Used for correcting parents after an `offset()` which could not avoid modifying the start
        position."""

        if not self_:
            self = self.parent

        while self:
            if (lno := getattr(a := self.a, 'lineno', -1)) > lineno or (lno == lineno and a.col_offset > col_offset):
                a.lineno     = lineno
                a.col_offset = col_offset

                self.touch()

            self = self.parent

    def _set_end_pos(self, end_lineno: int, end_col_offset: int, self_: bool = True):  # because of trailing non-AST junk in last statements
        """Walk up parent chain (starting at `self`) setting `.end_lineno` and `.end_col_offset` to `end_lineno` and
        `end_col_offset` if self is last child of parent. Initial `self` is corrected always. Used for correcting
        parents after an `offset()` which removed or modified last child statements of block parents."""

        while True:
            if not self_:
                self_ = True

            else:
                if hasattr(a := self.a, 'end_lineno'):  # because of ASTs which locations
                    a.end_lineno     = end_lineno
                    a.end_col_offset = end_col_offset

                self.touch()

            if not (parent := self.parent) or self.next():  # self is not parent.last_child():
                break

            self = parent

    def _maybe_add_comma(self, ln: int, col: int, offset: bool, space: bool,
                         end_ln: int | None = None, end_col: int | None = None) -> bool:
        """Maybe add comma at start of span if not already present as first code in span. Will skip any closing
        parentheses for check and add.

        **Parameters:**
        - `ln`: Line start of span.
        - `col`: Column start of span.
        - `offset`: If `True` then will apply `offset()` to entire tree for new comma. If `False` then will just offset
            the end of self, use this when self is at top level.
        - `space`: Whether to add a space IF the span is zero length.

        **Returns:**
        - `bool`: Whether a comma was added or not (if wasn't present before or was).
        """

        root  = self.root
        lines = root._lines

        if end_ln is None:
            end_ln  = self.end_ln
            end_col = self.end_col

        while code := _next_src(lines, ln, col, end_ln, end_col):  # find comma or parens or something else
            cln, ccol, src = code

            for c in src:
                ccol += 1

                if c == ')':
                    ln  = cln
                    col = ccol

                elif c == ',':
                    return False
                else:
                    break

            else:
                continue

            break

        comma     = ', ' if space and ln == end_ln and col == end_col else ','
        lines[ln] = bistr(f'{(l := lines[ln])[:col]}{comma}{l[col:]}')

        if offset:
            self.root.offset(ln, col, 0, len(comma), True, self)

        elif ln == end_ln:
            self.a.end_col_offset += len(comma)

            self.touchall(True, False, True)

        return True

    def _maybe_add_singleton_tuple_comma(self, offset: bool):
        """Maybe add comma to tuple if is singleton and comma not already there, parenthesization not checked or taken
        into account. `self.a` must be a `Tuple`.

        **Parameters:**
        - `offset`: If `True` then will apply `offset()` to entire tree for new comma. If `False` then will just offset
            the end of the `Tuple`, use this when `Tuple` is at top level.
        """

        # assert isinstance(self.a, Tuple)

        if (elts := self.a.elts) and len(elts) == 1:
            return self._maybe_add_comma((f := elts[0].f).end_ln, f.end_col, offset, False, self.end_ln,
                                         self.end_col - self.is_parenthesized_tuple())

    def _maybe_fix_tuple(self, is_parenthesized: bool | None = None):
        # assert isinstance(self.a, Tuple)

        ast = self.a

        if is_parenthesized is None:
            is_parenthesized = self.is_parenthesized_tuple()

        if ast.elts:
            self._maybe_add_singleton_tuple_comma(True)

            ln, col, end_ln, end_col = self.loc

            if not is_parenthesized and end_ln != ln:  # and not self.is_enclosed:  <-- TODO: this, also maybe double check for line continuations?
                self.put_lines([bistr(')')], end_ln, end_col, end_ln, end_col, True, self)
                self.put_lines([bistr('(')], ln, col, ln, col, False)

                self._floor_start_pos(ast.lineno, ast.col_offset - 1)

        elif not is_parenthesized:  # if is unparenthesized tuple and empty left then need to add parentheses
            ln, col, end_ln, end_col = self.loc

            self.put_lines([bistr('()')], ln, col, end_ln, end_col, True)  # WARNING! `True` may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized tuple starts, but haven't found a case where this can happen

            if end_col == col and end_ln == ln:  # this is tricky because zero length tuple can be at the start of a parent so now we have to correct offset that was applied to all parents start positions
                self._floor_start_pos(ast.lineno, ast.col_offset, False)  # self will not have the start point moved because of `put_lines(..., True)`

    def _maybe_fix_set(self):
        # assert isinstance(self.a, Set)

        if not self.a.elts:
            ln, col, end_ln, end_col = self.loc

            self.put_lines([bistr('set()')], ln, col, end_ln, end_col, True)

            ast    = self.a
            self.a = ast = _new_empty_set_call(True, ast.lineno, ast.col_offset, from_=self)
            ast.f  = self

            if parent := self.parent:
                self.pfield.set(parent.a, ast)

            self._make_fst_tree([FST(ast.func, self, astfield('func'))])

    def _maybe_fix_if(self):
        # assert isinstance(self.a, If)

        ln, col, _, _ = self.loc
        lines         = self.root._lines

        if lines[ln].startswith('elif', col) and (not (parent := self.parent) or not
            (isinstance(parenta := parent.a, If) and self.pfield == ('orelse', 0) and len(parenta.orelse) == 1 and
             self.a.col_offset == parenta.col_offset)
        ):
            self.put_lines(None, ln, col, ln, col + 2, False)

    def _fix_block_del_last_child(self, bound_ln: int, bound_col: int, bound_end_ln: int, bound_end_col: int):
        """Fix end location of a block statement after its last child (position-wise, not last existing child) has been
        cut or deleted. Will set end position of `self` and any parents who `self` is the last child of to the new last
        child if it is past the block-open colon, otherwise set end at just past the block-open colon.

        **Parameters:**
        - `bound_ln`, `bound_col`: Position before block colon but after and pre-colon `AST` node.
        - `bound_end_ln`, `bound_end_col`: Position after block colon, probably start of deleted region, only used if
            new last child is before colon.
        """

        end_lineno = None

        if last_child := self.last_child(True):  # easy enough when we have a new last child
            if last_child.pfield.name in ('body', 'orelse', 'handlers', 'finalbody', 'cases'):  # but make sure its past the block open colon
                end_lineno     = last_child.end_lineno
                end_col_offset = last_child.end_col_offset

        if end_lineno is None:
            lines = self.root._lines

            if end := _prev_find(lines, bound_ln, bound_col, bound_end_ln, bound_end_col, ':'):  # find first preceding block colon, its there unless first opened block in module
                end_ln, end_col  = end
                end_col         += 1  # just past the colon

            else:
                end_ln  = bound_ln
                end_col = bound_col

            end_lineno     = end_ln + 1
            end_col_offset = lines[end_ln].c2b(end_col)

        self._set_end_pos(end_lineno, end_col_offset)

    def _normalize_block(self, field: str = 'body', *, indent: str | None = None):
        """Move statements on the same logical line as a block open to their own line, e.g:
        ```
        if a: call()
        ```
        Becomes:
        ```
        if a:
            call()
        ```

        **Parameters:**
        - `field`: Which block to normalize (`'body'`, `'orelse'`, `'handlers'`, `'finalbody'`).
        - `indent`: The indentation to use for the relocated line if already known, saves a call to `get_indent()`.
        """

        if isinstance(self.a, mod) or not (block := getattr(self.a, field)) or not isinstance(block, list):
            return

        b0                  = block[0].f
        b0_ln, b0_col, _, _ = b0.bloc
        root                = self.root

        if not (colon := _prev_find(root._lines, *b0._prev_ast_bound(), b0_ln, b0_col, ':', True,
                                    comment=True, lcont=None)):
            return

        if indent is None:
            indent = b0.get_indent()

        ln, col = colon

        self.put_lines(['', indent], ln, col + 1, b0_ln, b0_col, False)

    def _elif_to_else_if(self):
        """Covnert an 'elif something:\\n  ...' to 'else:\\n  if something:\\n    ...'. Make sure to only call on an
        actual `elif`, meaning the lone `If` statement in the parent's `orelse` block which is an actual `elif` and not
        an `if`."""

        indent = self.get_indent()

        self.indent_lns(skip=0)

        if not self.next():  # last child?
            self._set_end_pos((a := self.a).end_lineno, a.end_col_offset, False)

        ln, col, _, _ = self.loc

        self.put_lines(['if'], ln, col, ln, col + 4, False)
        self.put_lines([indent + 'else:', indent + self.root.indent], ln, 0, ln, col, False)

    def _make_fst_and_dedent(self, indent: Union['FST', str], ast: AST, copy_loc: fstloc,
                             prefix: str = '', suffix: str = '',
                             put_loc: fstloc | None = None, put_lines: list[str] | None = None, *,
                             docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':

        if not isinstance(indent, str):
            indent = indent.get_indent()

        lines = self.root._lines
        fst   = FST(ast, lines=lines, from_=self)  # we use original lines for nodes offset calc before putting new lines

        fst.offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix.encode()) - lines[copy_loc.ln].c2b(copy_loc.col))

        fst._lines = fst_lines = self.get_lines(*copy_loc)

        if suffix:
            fst_lines[-1] = bistr(fst_lines[-1] + suffix)

        if prefix:
            fst_lines[0] = bistr(prefix + fst_lines[0])

        fst.dedent_lns(indent, skip=bool(copy_loc.col), docstr=docstr)  # if copy location starts at column 0 then we apply dedent to it as well (preceding comment or something)

        if put_loc:
            self.put_lines(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0

        return fst

    def _get_seq_and_dedent(self, get_ast: AST, cut: bool, seq_loc: fstloc,
                            ffirst: Union['FST', fstloc], flast: Union['FST', fstloc],
                            fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                            prefix: str, suffix: str) -> 'FST':

        copy_loc, put_loc, put_lines = self.src_edit.get_slice_seq(self, cut, seq_loc, ffirst, flast, fpre, fpost)

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

        get_ast.f.touch()

        return get_fst

    def _get_slice_tuple_list_or_set(self, start: int | None, stop: int | None, field: str | None, fix: bool, cut: bool,
                                     fmt: Fmt, docstr: bool | str) -> 'FST':
        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

        ast         = self.a
        elts        = ast.elts
        is_set      = isinstance(ast, Set)
        is_tuple    = not is_set and isinstance(ast, Tuple)
        start, stop = _fixup_slice_index(ast, elts, 'elts', start, stop)

        if start == stop:
            if is_set:
                return _new_empty_set_call(from_=self) if fix else _new_empty_set_curlies(from_=self)
            elif is_tuple:
                return _new_empty_tuple(from_=self)
            else:
                return _new_empty_list(from_=self)

        is_paren = is_tuple and self.is_parenthesized_tuple()
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

        fst = self._get_seq_and_dedent(get_ast, cut, seq_loc, ffirst, flast, fpre, fpost, prefix, suffix)

        if fix:
            if is_set:
                self._maybe_fix_set()

            elif is_tuple:
                fst._maybe_add_singleton_tuple_comma(False)  # maybe need to add a postfix comma to copied single element tuple if is not already there
                self._maybe_fix_tuple(is_paren)

        return fst

    def _get_slice_empty_set_call(self, start: int | None, stop: int | None, field: str | None, fix: bool, cut: bool,
                                  fmt: Fmt, docstr: bool | str) -> 'FST':
        if not fix:
            raise ValueError(f"cannot get slice from a 'set()' without specifying 'fix=True'")

        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

        if start or stop:
            raise IndexError(f"Set.{field} index out of range")

        return _new_empty_set_call(from_=self) if fix else _new_empty_set_curlies(from_=self)

    def _get_slice_dict(self, start: int | None, stop: int | None, field: str | None, fix: bool, cut: bool,
                        fmt: Fmt, docstr: bool | str) -> 'FST':
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to slice from a Dict")

        ast         = self.a
        values      = ast.values
        start, stop = _fixup_slice_index(ast, values, 'values', start, stop)

        if start == stop:
            return _new_empty_dict(from_=self)

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

        return self._get_seq_and_dedent(get_ast, cut, seq_loc, ffirst, flast, fpre, fpost, '{', '}')

    def _get_slice_stmt(self, start: int | None, stop: int | None, field: str | None, fix: bool, cut: bool,
                        fmt: Fmt, docstr: bool | str, *, single: bool = False) -> 'FST':
        ast         = self.a
        field, body = _fixup_field_body(ast, field)
        start, stop = _fixup_slice_index(ast, body, field, start, stop)

        if start == stop:
            return _new_empty_module(from_=self)

        ffirst = body[start].f
        flast  = body[stop - 1].f
        fpre   = body[start - 1].f if start else None
        fpost  = body[stop].f if stop < len(body) else None
        indent = ffirst.get_indent()

        block_loc = fstloc(*(fpre.bloc[2:] if fpre else ffirst._prev_ast_bound()),
                           *(fpost.bloc[:2] if fpost else flast._next_ast_bound()))

        if isinstance(fmt, str):
            fmt = frozenset(t for s in fmt.split(',') if (t := s.strip()))

        copy_loc, put_loc, put_lines = (
            self.src_edit.get_slice_stmt(self, field, cut, fmt, block_loc, ffirst, flast, fpre, fpost))

        if not cut:
            asts    = [copy_ast(body[i]) for i in range(start, stop)]
            put_loc = None

        else:
            is_last_child = not fpost and not flast.next()
            asts          = body[start : stop]

            del body[start : stop]

            for i in range(start, len(body)):
                body[i].f.pfield = astfield(field, i)

        if not single:
            get_ast = Module(body=asts, type_ignores=[])
        elif len(asts) == 1:
            get_ast = asts[0]
        else:
            raise ValueError(f'cannot specify `single` for multiple statements')

        # copy_loc, put_loc, put_lines = (
        #     self.src_edit.get_slice_stmt(self, field, cut, fmt, block_loc, ffirst, flast, fpre, fpost))

        # if not cut:
        #     put_loc = None

        fst = self._make_fst_and_dedent(indent, get_ast, copy_loc, '', '', put_loc, put_lines, docstr=docstr)

        if cut and is_last_child:  # correct for removed last child nodes or last nodes past the block open colon
            self._fix_block_del_last_child(block_loc.ln, block_loc.col, put_loc.ln, put_loc.col)

        if fix:
            if len(asts) == 1 and isinstance(a := asts[0], If):
                a.f._maybe_fix_if()

        return fst

    def _put_seq_and_indent(self, put_fst: Optional['FST'], seq_loc: fstloc,
                            ffirst: Union['FST', fstloc, None], flast: Union['FST', fstloc, None],
                            fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                            pfirst: Union['FST', fstloc, None], plast: Union['FST', fstloc, None],
                            docstr: bool | str) -> 'FST':
        root = self.root

        if not put_fst:  # delete
            put_ln, put_col, put_end_ln, put_end_col = (
                self.src_edit.put_slice_seq(self, None, '', seq_loc, ffirst, flast, fpre, fpost, None, None))

            put_lines = None

        else:
            assert put_fst.is_root

            indent = self.get_indent()

            put_fst.indent_lns(indent, docstr=docstr)

            put_ln, put_col, put_end_ln, put_end_col = (
                self.src_edit.put_slice_seq(self, put_fst, indent, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast))

            lines           = root._lines
            put_lines       = put_fst._lines
            fst_dcol_offset = lines[put_ln].c2b(put_col)

            put_fst.offset(0, 0, put_ln, fst_dcol_offset)

        self_ln, self_col, _, _ = self.loc

        if is_unparen_tuple := put_col == self_col and put_ln == self_ln:  # beginning of stupid evil unparenthesized tuple
            ast        = self.a
            lineno     = ast.lineno
            col_offset = ast.col_offset

        if fpost:
            root.put_lines(put_lines, put_ln, put_col, put_end_ln, put_end_col, False, None)
        else:
            root.put_lines(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, self)  # because of insertion at end and unparenthesized tuple

        if is_unparen_tuple:
            self._floor_start_pos(lineno, col_offset)  # because of insertion at beginning of unparenthesized tuple, pattern beginning to emerge

    def _put_slice_tuple_list_or_set(self, code: Code | None, start: int | None, stop: int | None, field: str | None,
                                     single: bool, fix: bool, fmt: Fmt, docstr: bool | str):
        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to assign slice to a {self.a.__class__.__name__}")

        if code is None:
            put_fst = None

        else:
            put_fst = _normalize_code(code, 'expr', parse_params=self.root.parse_params)

            if single:
                a        = put_fst.a
                put_ast  = Set(elts=[a], lineno=a.lineno, col_offset=a.col_offset, end_lineno=a.end_lineno,
                               end_col_offset=a.end_col_offset)
                put_fst  = FST(put_ast, lines=put_fst._lines)
                is_tuple = False
                is_set   = True

            else:
                if put_fst.is_empty_set_call():
                    if fix:
                        put_fst = _new_empty_set_curlies(from_=self)
                    else:
                        raise ValueError(f"cannot put 'set()' as a slice without specifying 'fix=True'")

                put_ast  = put_fst.a
                is_tuple = isinstance(put_ast, Tuple)
                is_set   = not is_tuple and isinstance(put_ast, Set)

                if not is_tuple and not is_set and not isinstance(put_ast, List):
                    raise ValueError(f"slice being assigned to a {self.a.__class__.__name__} "
                                     f"must be a Tuple, List or Set, not a '{put_ast.__class__.__name__}'")

        ast         = self.a
        elts        = ast.elts
        start, stop = _fixup_slice_index(ast, elts, 'elts', start, stop)
        slice_len   = stop - start

        if not slice_len and (not put_fst or not put_ast.elts):  # deleting or assigning empty seq to empty slice of seq, noop
            return

        is_self_tuple    = isinstance(ast, Tuple)
        is_self_set      = not is_self_tuple and isinstance(ast, Set)
        is_self_enclosed = not is_self_tuple or self.is_parenthesized_tuple()
        fpre             = elts[start - 1].f if start else None
        fpost            = None if stop == len(elts) else elts[stop].f
        seq_loc          = fstloc(self.ln, self.col + is_self_enclosed, self.end_ln, self.end_col - is_self_enclosed)

        if not slice_len:
            ffirst = flast = None

        else:
            ffirst = elts[start].f
            flast  = elts[stop - 1].f

        if not put_fst:
            self._put_seq_and_indent(None, seq_loc, ffirst, flast, fpre, fpost, None, None, docstr)
            self._unmake_fst_tree(elts[start : stop])

            del elts[start : stop]

            put_len = 0

        else:
            put_lines = put_fst._lines

            if single:
                pass  # noop

            elif not is_tuple:
                put_ast.end_col_offset -= 1  # strip enclosing curlies or brackets from source set or list

                put_fst.offset(0, 1, 0, -1)

                assert put_lines[0].startswith('[{'[is_set])
                assert put_lines[-1].endswith(']}'[is_set])

                put_lines[-1] = bistr(put_lines[-1][:-1])
                put_lines[0]  = bistr(put_lines[0][1:])

            elif put_fst.is_parenthesized_tuple():
                put_ast.end_col_offset -= 1  # strip enclosing parentheses from source tuple

                put_fst.offset(0, 1, 0, -1)

                put_lines[-1] = bistr(put_lines[-1][:-1])
                put_lines[0]  = bistr(put_lines[0][1:])

            if not (selts := put_ast.elts):
                pfirst = plast = None

            else:
                pfirst = selts[0].f
                plast  = selts[-1].f

            self._put_seq_and_indent(put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast, docstr)
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

    def _put_slice_empty_set_call(self, code: Code | None, start: int | None, stop: int | None, field: str | None,
                                  single: bool, fix: bool, fmt: Fmt, docstr: bool | str):
        if not fix:
            raise ValueError(f"cannot put slice to a 'set()' without specifying 'fix=True'")

        ln, col, end_ln, end_col = self.loc

        self.put_lines([bistr('{}')], ln, col, end_ln, end_col, True)

        ast    = self.a
        self.a = ast = _new_empty_set_curlies(True, ast.lineno, ast.col_offset, from_=self)
        ast.f  = self

        if parent := self.parent:
            self.pfield.set(parent.a, ast)

        try:
            self._put_slice_tuple_list_or_set(code, start, stop, field, single, fix, fmt, docstr)

        finally:
            if not self.a.elts:
                self._maybe_fix_set()  # restore 'set()'

    def _put_slice_dict(self, code: Code | None, start: int | None, stop: int | None, field: str | None,
                        single: bool, fix: bool, fmt: Fmt, docstr: bool | str):
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

        if code is None:
            put_fst = None

        else:
            put_fst = _normalize_code(code, 'expr', parse_params=self.root.parse_params)
            put_ast = put_fst.a

            if not isinstance(put_ast, Dict):
                raise ValueError(f"slice being assigned to a Dict must be a Dict, not a '{put_ast.__class__.__name__}'")

        ast         = self.a
        values      = ast.values
        start, stop = _fixup_slice_index(ast, values, 'values', start, stop)
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
            self._put_seq_and_indent(None, seq_loc, ffirst, flast, fpre, fpost, None, None, docstr)
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

            self._put_seq_and_indent(put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast, docstr)
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

    def _put_slice_stmt(self, code: Code | None, start: int | None, stop: int | None, field: str | None,
                        single: bool, fix: bool, fmt: Fmt, docstr: bool | str, *, force: bool = False):  # TODO: `force` is for some previously written tests, but really should fix those tests instead
        ast         = self.a
        field, body = _fixup_field_body(ast, field)

        if code is None:
            put_fst = None

        else:
            put_fst  = _normalize_code(code, 'mod', parse_params=self.root.parse_params)
            put_ast  = put_fst.a
            put_body = put_ast.body

            if single and len(put_body) != 1:
                raise ValueError('expecting a single statement')

            node_type = ExceptHandler if field == 'handlers' else match_case if field == 'cases' else stmt

            if not force and any(not isinstance(bad_node := n, node_type) for n in put_body):
                raise ValueError(f"cannot put {bad_node.__class__.__qualname__} node to '{field}' field")

        start, stop = _fixup_slice_index(ast, body, field, start, stop)
        slice_len   = stop - start

        if not slice_len and (not put_fst or (not put_body and len(ls := put_fst._lines) == 1 and not ls[0])):  # deleting empty slice or assigning empty fst to empty slice, noop
            return

        root  = self.root
        lines = root._lines
        fpre  = body[start - 1].f if start else None
        fpost = body[stop].f if stop < len(body) else None

        if put_fst:
            opener_indent = self.get_indent()
            block_indent  = opener_indent if self.is_root else opener_indent + root.indent

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

        if isinstance(fmt, str):
            fmt = frozenset(t for s in fmt.split(',') if (t := s.strip()))

        if not put_fst:
            _, put_loc, put_lines = (
                self.src_edit.get_slice_stmt(self, field, True, fmt, block_loc, ffirst, flast, fpre, fpost))

            if put_loc:
                self.put_lines(put_lines, *put_loc, True)

            self._unmake_fst_tree(body[start : stop])

            del body[start : stop]

            put_len = 0

        else:
            if body:
                block_indent = body[0].f.get_indent()  # override default unknown indent

            put_loc = self.src_edit.put_slice_stmt(self, put_fst, field, fmt, docstr,
                                                   block_loc, opener_indent, block_indent,
                                                   ffirst, flast, fpre, fpost)

            put_fst.offset(0, 0, put_loc.ln, 0 if put_fst.bln or put_fst.bcol else lines[put_loc.ln].c2b(put_loc.col))
            self.put_lines(put_fst.lines, *put_loc, False)
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

    # ------------------------------------------------------------------------------------------------------------------

    def __repr__(self) -> str:
        tail = self._repr_tail()
        head = f'<fst.{(a := self.a).__class__.__name__} 0x{id(a):x}{tail}>'

        if not REPR_SRC_LINES:
            return head

        try:
            ln, col, end_ln, end_col = self.loc

            if end_ln - ln + 1 <= REPR_SRC_LINES:
                ls = self.root._lines[ln : end_ln + 1]
            else:
                ls = (self.root._lines[ln : ln + ((REPR_SRC_LINES + 1) // 2)] + ['...'] +
                      self.root._lines[end_ln - ((REPR_SRC_LINES - 2) // 2) : end_ln + 1])

            ls[-1] = ls[-1][:end_col]
            ls[0]  = ' ' * col + ls[0][col:]

            return '\n'.join([head] + ls)

        except Exception:
            pass

        return head + '\n???'

    def __getattr__(self, name) -> Any:
        if isinstance(child := getattr(self.a, name), list):
            return fstlistproxy(child, self, name)
        elif child and isinstance(child, AST):
            return child.f

        return child

    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, ast: AST, parent: Optional['FST'] = None, pfield: astfield | None = None, **root_params):
        self.a      = ast
        self.parent = parent
        self.pfield = pfield
        ast.f       = self

        if parent is not None:
            self.root = parent.root

            return

        # ROOT

        self.root   = self
        self._lines = ((lines if lines[0].__class__ is bistr else [bistr(s) for s in lines])
                       if (lines := root_params.get('lines')) else
                       [bistr('')])

        if from_ := root_params.get('from_'):  # copy params from source tree
            from_root         = from_.root
            self.parse_params = root_params.get('parse_params', from_root.parse_params)
            self.indent       = root_params.get('indent', from_root.indent)

        else:
            self.parse_params = root_params.get('parse_params', DEFAULT_PARSE_PARAMS)
            self.indent       = root_params.get('indent', DEFAULT_INDENT)

        self._make_fst_tree()

    @staticmethod
    def new(filename: str = '<unknown>', mode: str = 'exec', *,
            type_comments: bool = False, feature_version: tuple[int, int] | None = None) -> 'FST':
        """Create a new empty `FST` tree with the top level node dictated by the `mode` parameter.

        **Parameters:**
        - `filename`: `ast.parse()` parameter.
        - `mode`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.

        **Returns:**
        - `FST`: The new empty top level `FST` node.
        """

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)

        if mode == 'exec':
            ast = Module(body=[], type_ignores=[])
        elif mode == 'eval':
            ast = Expression(body=None)
        elif mode == 'single':
            ast = Interactive(body=[])
        else:
            raise ValueError(f"invalid mode '{mode}'")

        return FST(ast, parse_params=parse_params)

    @staticmethod
    def fromsrc(source: str | bytes | list[str], filename: str = '<unknown>', mode: str = 'exec', *,
                type_comments: bool = False, feature_version: tuple[int, int] | None = None) -> 'FST':
        """Parse and create a new `FST` tree from source, preserving the original source and locations.

        **Parameters:**
        - `source`: The source to parse as a single `str`, `bytes` or list of individual line strings (without
            newlines).
        - `filename`: `ast.parse()` parameter.
        - `mode`: `ast.parse()` parameter.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.

        **Returns:**
        - `FST`: The parsed tree with `.f` attributes added to each `AST` node for `FST` access.
        """

        if isinstance(source, bytes):
            source = source.decode()

        if isinstance(source, str):
            lines  = source.split('\n')

        else:
            lines  = source
            source = '\n'.join(lines)

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)
        ast          = ast_parse(source, mode=mode, **parse_params)

        return FST(ast, lines=[bistr(s) for s in lines], parse_params=parse_params)

    @staticmethod
    def fromast(ast: AST, filename: str = '<unknown>', mode: str | None = None, *,
                type_comments: bool | None = False, feature_version=None,
                calc_loc: bool | Literal['copy'] = True) -> 'FST':
        """Add `FST` to existing `AST` tree, optionally copying positions from reparsed `AST` (default) or whole `AST`
        for new `FST`.

        Do not set `calc_loc` to `False` unless you parsed the `AST` from a previous output of `ast.unparse()`,
        otherwise there will almost certainly be problems!

        **Parameters:**
        - `ast`: The root `AST` node.
        - `filename`: `ast.parse()` parameter.
        - `mode`: `ast.parse()` parameter. Can be `exec`, `eval, `single` or `None`, in which case the appropriate mode
            is determined from the structure of the tree itself.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.
        - `calc_loc`: Get actual node positions by unparsing then parsing again. Use when you are not certain node
            positions are correct or even present. Updates original ast unless set to "copy", in which case a copied
            `AST` is used. Set to `False` when you know positions are correct and want to use given `AST`. Default
            `True`.

        **Returns:**
        - `FST`: The augmented tree with `.f` attributes added to each `AST` node for `FST` access.
        """

        src   = ast_unparse(ast)
        lines = src.split('\n')

        if type_comments is None:
            type_comments = has_type_comments(ast)

        parse_params = dict(filename=filename, type_comments=type_comments, feature_version=feature_version)

        if calc_loc:
            astp = ast_parse(src, mode=get_parse_mode(ast) if mode is None else mode, **parse_params)

            if astp.__class__ is not ast.__class__:
                astp = astp.body if isinstance(astp, Expression) else astp.body[0]

                if astp.__class__ is not ast.__class__:
                    raise RuntimeError('could not reproduce ast')

            if calc_loc == 'copy':
                if not compare_asts(astp, ast, type_comments=type_comments, raise_=False):
                    raise RuntimeError('could not reparse ast identically')

                ast = astp

            elif not copy_attributes(astp, ast, compare=True, type_comments=type_comments, raise_=False):
                raise RuntimeError('could not reparse ast identically')

        return FST(ast, lines=[bistr(s) for s in lines], parse_params=parse_params)

    def verify(self, raise_: bool = True) -> Optional['FST']:  # -> Self | None:
        """Sanity check, reparse source and make sure parsed tree matches currently stored tree (locations and
        everything).

        **Parameters:**
        - `raise_`: Whether to raise an exception on verify failed or return `None`.

        **Returns:**
        - `None` on failure to verify (if not `raise_`), otherwise `self`.
        """

        if not self.is_root:
            raise RuntimeError('can only be called on root node')

        ast          = self.a
        parse_params = self.parse_params

        try:
            astp = ast_parse(self.src, mode=get_parse_mode(ast), **parse_params)

        except SyntaxError:
            if raise_:
                raise

            return None

        if not isinstance(ast, mod):
            if isinstance(astp, Expression):
                astp = astp.body
            elif len(astp.body) == 1:
                astp = astp.body[0]
            elif raise_:
                raise ValueError('verify failed reparse')
            else:
                return None

        if not compare_asts(astp, ast, locs=True, type_comments=parse_params['type_comments'], raise_=raise_):
            return None

        return self

    def dump(self, linefunc: Callable = print, *, full: bool = False, indent: int = 2, compact: bool = False,
             ) -> list[str] | None:
        """Dump a representation of the tree to stdout or return as a list of lines.

        **Parameters:**
        - `linefunc`: `print` means print to stdout, `list` returns a list of lines and `str` returns a whole string.
            Otherwise a `Callable[[str], None]` which is called for each line of output individually.
        - `full`: If `True` then will list all fields in nodes including empty ones, otherwise will exclude most empty
            fields.
        - `indent`: The average airspeed of an unladen swallow.
        - `compact`: If `True` then the dump is compacted a bit by listing `Name` and `Constant` nodes on a single
            line.
        """

        if linefunc is print:
            return self._dump(full, indent, linefunc=print, compact=compact)

        if linefunc in (str, list):
            lines = []

            self._dump(full, indent, linefunc=lines.append, compact=compact)

            return lines if linefunc is list else '\n'.join(lines)

        self._dump(full, indent, linefunc=linefunc, compact=compact)

    # ------------------------------------------------------------------------------------------------------------------

    def fix(self, inplace: bool = True) -> 'FST':
        """This is really a maybe fix source and `ctx` values for cut or copied nodes (to make subtrees parsable if the
        source is not after the operation). Normally this is called by default on newly cut / copied individual nodes.
        Possibly reparses in order to verify expressions. If can not fix or ast is not parsable by itself then ast will
        be unchanged. Is meant to be a quick fix after a cut or copy operation, not full check, for that use
        `is_parsable()` or `verify()` depending on need. Possible source changes are `elif` to `if` and parentheses
        where needed and commas for singleton tuples.

        **Parameters:**
        - `inplace`: If `True` then changes will be made to `self`. If `False` then `self` may be returned if no changes
            made, otherwise a modified copy is returned.

        **Returns:**
        - `self` if unchanged or modified in place or a new `FST` object otherwise.
        """

        if not self.is_root:
            raise RuntimeError('can only be called on root node')

        if not (loc := self.loc):
            return self

        ln, col, end_ln, end_col = loc

        ast   = self.a
        lines = self._lines

        # if / elif statement

        if isinstance(ast, If):
            if (l := lines[ln]).startswith('if', col):
                return self

            assert l.startswith('elif', col)

            if not inplace:
                self = FST(copy_ast(ast), lines=(lines := lines[:]), from_=self)

            self.offset(ln, col + 2, 0, -2)

            lines[ln] = bistr((l := lines[ln])[:col] + l[col + 2:])

        # expression maybe parenthesize and proper ctx (Load)

        elif (isinstance(ast, expr)):
            if not self.is_parsable():  # may be Slice or Starred
                return self

            need_paren = None

            if is_tuple := isinstance(ast, Tuple):
                if self.is_parenthesized_tuple():
                    need_paren = False

                elif (not (elts := ast.elts) or any(isinstance(e, NamedExpr) for e in elts) or (len(elts) == 1 and (
                      not (code := _next_src(lines, (f0 := elts[0].f).end_ln, f0.end_col, end_ln, end_col, False, None))
                      or  # if comma not on logical line then definitely need to add parens, if no comma then the parens are incidental but we want that code path for adding the singleton comma
                      not code.src.startswith(',')))):
                    need_paren = True

            elif (isinstance(ast, (Name, List, Set, Dict, ListComp, SetComp, DictComp, GeneratorExp)) or
                  ((code := _prev_src(self.root._lines, 0, 0, self.ln, self.col)) and code.src.endswith('('))):  # is parenthesized?
                need_paren = False

            elif isinstance(ast, (NamedExpr, Yield, YieldFrom)):
                need_paren = True

            elif end_ln == ln:
                need_paren = False

            if need_paren is None:
                try:
                    a = ast_parse(src := self.src, mode='eval', **self.parse_params)

                except SyntaxError:  # if expression not parsing then try parenthesize
                    tail = (',)' if is_tuple and len(ast.elts) == 1 and lines[end_ln][end_col - 1] != ',' else ')')  # WARNING! this won't work for expressions followed by comments, but all comments should be followed by a newline in normal operation

                    try:
                        a = ast_parse(f'({src}{tail}', mode='eval', **self.parse_params)
                    except SyntaxError:
                        return self

                    if not inplace:
                        lines = lines[:]

                    lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col]}{tail}{l[end_col:]}')
                    lines[ln]     = bistr(f'{(l := lines[ln])[:col]}({l[col:]}')

                else:
                    if compare_asts(a.body, ast, locs=True, type_comments=True, recurse=False):  # only top level compare needed for `ctx` and structure check
                        return self

                    if not inplace:
                        lines = lines[:]

                a = a.body  # we know parsed to an Expression but original was not an Expression

                if not inplace:
                    return FST(a, lines=lines, from_=self)

                self.a = a
                a.f    = self

                self.touch()
                self._make_fst_tree()

                return self

            need_ctx = set_ctx(ast, Load, doit=False)

            if (need_ctx or need_paren) and not inplace:
                ast   = copy_ast(ast)
                lines = lines[:]
                self  = FST(ast, lines=lines, from_=self)

            if need_ctx:
                set_ctx(ast, Load)

            if need_paren:
                lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col]}){l[end_col:]}')
                lines[ln]     = bistr(f'{(l := lines[ln])[:col]}({l[col:]}')

                self.offset(ln, col, 0, 1)

                if is_tuple:
                    ast.col_offset     -= 1
                    ast.end_col_offset += 1

                self.touch()

                if is_tuple:
                    self._maybe_add_singleton_tuple_comma(False)

        return self

    def copy(self, *, fix: bool = True, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':
        """Copy an individual node to a top level tree, dedenting and fixing as necessary."""

        ast    = self.a
        newast = copy_ast(ast)

        if self.is_root:
            return FST(newast, lines=self._lines[:], from_=self)

        if isinstance(ast, STATEMENTISH):
            loc = self.comms(False, fmt)
        elif isinstance(ast, PARENTHESIZABLE):
            loc = (self.pars(False) if 'pars' in
                   ((t for s in fmt.split(',') if (t := s.strip())) if isinstance(fmt, str) else fmt)
                   else self.bloc)
        else:
            loc = self.bloc

        if not loc:
            raise ValueError('cannot copy node which does not have location')

        fst = self._make_fst_and_dedent(self, newast, loc, docstr=docstr)

        return fst.fix(inplace=True) if fix else fst

    def cut(self, *, fix: bool = True, fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':
        """Cut out an individual node to a top level tree (if possible), dedenting and fixing as necessary."""

        if self.is_root:
            raise ValueError('cannot cut root node')

        ast        = self.a
        parent     = self.parent
        field, idx = self.pfield
        parenta    = parent.a

        if isinstance(ast, STATEMENTISH_OR_STMTMOD):
            return parent._get_slice_stmt(idx, idx + 1, field, fix=fix, cut=True, fmt=fmt, docstr=docstr, single=True)

        if isinstance(parenta, (Tuple, List, Set)):
            fst = self.copy(fix=fix, fmt=fmt, docstr=docstr)

            parent._put_slice_tuple_list_or_set(None, idx, idx + 1, field, False, fix, fmt, docstr)

            return fst

        # TODO: individual nodes
        # TODO: other sequences?

        raise ValueError(f"cannot cut a '{parenta.__class__.__name__}'")




    def get(self, start: int | None = None, stop: int | None | Literal[False] = False, field: str | None = None, *,
            fix: bool = True, cut: bool = False,
            fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> Optional['FST']:
        """Get an individual child node or a slice of child nodes from `self`."""

        if stop is not False:
            return self.get_slice(start, stop, field, fix=fix, cut=cut, fmt=fmt, docstr=docstr)

        field, body = _fixup_field_body(self.a, field)

        if cut:
            return body[start].f.cut(fix=fix, fmt=fmt, docstr=docstr)
        else:
            return body[start].f.copy(fix=fix, fmt=fmt, docstr=docstr)




    def put(self, code: Code | None, start: int | None = None, stop: int | None | Literal['False'] = False,
            field: str | None = None, *, fix: bool = True,
            fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':  # -> Self:
        """Put an individual child node or a slice of child nodes to `self`.

        If the `code` being put is an `AST` or `FST` then it is consumed and should not be considered valid after this
        call whether it succeeds or fails.
        """

        if stop is not False:
            return self.put_slice(code, start, stop, field, True, fix=fix, fmt=fmt, docstr=docstr)

        field, body = _fixup_field_body(self.a, field)

        # TODO: individual nodes

        raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!




    def get_slice(self, start: int | None = None, stop: int | None = None, field: str | None = None, *,
                  fix: bool = True, cut: bool = False,
                  fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':
        """Get a slice of child nodes from `self`."""

        ast = self.a

        if isinstance(ast, STATEMENTISH_OR_STMTMOD):
            return self._get_slice_stmt(start, stop, field, fix, cut, fmt, docstr)

        if isinstance(ast, (Tuple, List, Set)):
            return self._get_slice_tuple_list_or_set(start, stop, field, fix, cut, fmt, docstr)

        if isinstance(ast, Dict):
            return self._get_slice_dict(start, stop, field, fix, cut, fmt, docstr)

        if self.is_empty_set_call():
            return self._get_slice_empty_set_call(start, stop, field, fix, cut, fmt, docstr)

        raise ValueError(f"cannot get slice from a '{ast.__class__.__name__}'")






    def put_slice(self, code: Code | None, start: int | None = None, stop: int | None = None,
                  field: str | None = None, single: bool = False, *, fix: bool = True,
                  fmt: Fmt = DEFAULT_SRC_EDIT_FMT, docstr: bool | str = DEFAULT_DOCSTR) -> 'FST':  # -> Self:
        """Put an a slice of child nodes to `self`.

        If the `code` being put is an `AST` or `FST` then it is consumed and should not be considered valid after this
        call whether it succeeds or fails.
        """

        ast = self.a

        if isinstance(ast, STATEMENTISH_OR_STMTMOD):
            self._put_slice_stmt(code, start, stop, field, single, fix, fmt, docstr)

        elif isinstance(ast, (Tuple, List, Set)):
            self._put_slice_tuple_list_or_set(code, start, stop, field, single, fix, fmt, docstr)

        elif isinstance(ast, Dict):
            self._put_slice_dict(code, start, stop, field, single, fix, fmt, docstr)

        elif self.is_empty_set_call():
            self._put_slice_empty_set_call(code, start, stop, field, single, fix, fmt, docstr)

        else:
            raise ValueError(f"cannot put slice to a '{ast.__class__.__name__}'")

        return self








    def get_lines(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        """Get lines from currently stored source. The first and last lines are cropped to start `col` and `end_col`."""

        if end_ln == ln:
            return [bistr(self.root._lines[ln][col : end_col])]
        else:
            return [bistr((ls := self.root._lines)[ln][col:])] + ls[ln + 1 : end_ln] + [bistr(ls[end_ln][:end_col])]

    def put_lines(self, lines: list[str] | None, ln: int, col: int, end_ln: int, end_col: int,
                  inc: bool | None = None, stop_at: Optional['FST'] = None):
        """Put or delete lines to currently stored source, optionally offsetting all nodes for the change. Must specify
        `inc` as not `None` to enable offset of nodes according to lines put."""

        ls = self.root._lines

        if is_del := not lines:
            lines = [bistr('')]
        elif not lines[0].__class__ is bistr:
            lines = [bistr(s) for s in lines]

        # possibly offset nodes

        if inc is not None:
            dfst_ln     = len(lines) - 1
            dln         = dfst_ln - (end_ln - ln)
            dcol_offset = lines[-1].lenbytes - ls[end_ln].c2b(end_col)

            if not dfst_ln:
                dcol_offset += ls[ln].c2b(col)

            self.root.offset(end_ln, end_col, dln, dcol_offset, inc, stop_at)

        # put the actual lines (or just delete)

        if is_del:
            if end_ln == ln:
                ls[ln] = bistr((l := ls[ln])[:col] + l[end_col:])

            else:
                ls[end_ln] = bistr(ls[ln][:col] + ls[end_ln][end_col:])

                del ls[ln : end_ln]

        else:
            dln = end_ln - ln

            if (nnew_ln := len(lines)) <= 1:
                s = lines[0] if nnew_ln else ''

                if not dln:  # replace single line with single or no line
                    ls[ln] = bistr(f'{(l := ls[ln])[:col]}{s}{l[end_col:]}')

                else:  # replace multiple lines with single or no line
                    ls[ln] = bistr(f'{ls[ln][:col]}{s}{ls[end_ln][end_col:]}')

                    del ls[ln + 1 : end_ln + 1]

            elif not dln:  # replace single line with multiple lines
                lend                 = bistr(lines[-1] + (l := ls[ln])[end_col:])
                ls[ln]               = bistr(l[:col] + lines[0])
                ls[ln + 1 : ln + 1]  = lines[1:]
                ls[ln + nnew_ln - 1] = lend

            else:  # replace multiple lines with multiple lines
                ls[ln]              = bistr(ls[ln][:col] + lines[0])
                ls[end_ln]          = bistr(lines[-1] + ls[end_ln][end_col:])
                ls[ln + 1 : end_ln] = lines[1:-1]

    def get_src(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        """'\\n'.join(self.get_lines(...))'"""

        return '\n'.join(self.get_lines(ln, col, end_ln, end_col))

    def put_src(self, src: str | None, ln: int, col: int, end_ln: int, end_col: int,
                inc: bool = False, stop_at: Optional['FST'] = None):
        """self.put_lines(src.split('\\n'), ...)'."""

        self.put_lines(None if src is None else src.split('\n'), ln, col, end_ln, end_col, inc, stop_at)

# ------------------------------------------------------------------------------------------------------------------

    def next(self, with_loc: bool | Literal['own'] = True) -> Optional['FST']:  # TODO: refactor maybe
        """Get next sibling in syntactic order, only within parent.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location,
            otherwise all nodes.

        **Returns:**
        - `None` if last valid sibling in parent, otherwise next node.
        """

        if not (parent := self.parent):
            return None

        aparent   = parent.a
        name, idx = self.pfield

        while True:
            next = AST_FIELDS_NEXT[(aparent.__class__, name)]

            if isinstance(next, int):  # special case?
                while True:
                    match next:
                        case 0:  # from Dict.keys
                            next = 1
                            a    = aparent.values[idx]

                        case 1:  # from Dict.values
                            next = 0

                            try:
                                if not (a := aparent.keys[(idx := idx + 1)]):
                                    continue
                            except IndexError:
                                return None

                        case 2:  # from Compare.ops
                            next = 3
                            a    = aparent.comparators[idx]

                        case 6:  # all the logic for Call.args and Call.keywords
                            if not (keywords := aparent.keywords):  # no keywords
                                try:
                                    a = aparent.args[(idx := idx + 1)]
                                except IndexError:
                                    return None

                            elif not (args := aparent.args):  # no args
                                try:
                                    a = keywords[(idx := idx + 1)]
                                except IndexError:
                                    return None

                            elif not isinstance(star := args[-1], Starred):  # both args and keywords but no Starred
                                if name == 'args':
                                    try:
                                        a = args[(idx := idx + 1)]

                                    except IndexError:
                                        name = 'keywords'
                                        a    = keywords[(idx := 0)]

                                else:
                                    try:
                                        a = keywords[(idx := idx + 1)]
                                    except IndexError:
                                        return None

                            else:  # args, keywords AND Starred
                                if name == 'args':
                                    try:
                                        a = args[(idx := idx + 1)]

                                        if (a is star and ((kw := keywords[0]).lineno, kw.col_offset) <
                                            (star.lineno, star.col_offset)
                                        ):  # reached star and there is a keyword before it
                                            name = 'keywords'
                                            idx  = 0
                                            a    = kw

                                            break

                                    except IndexError:  # ran off the end of args, past star, find first kw after it (if any)
                                        star_pos = (star.lineno, star.col_offset)

                                        for a in keywords:
                                            if (a.lineno, a.col_offset) > star_pos:
                                                break
                                        else:
                                            return None

                                else:  # name == 'keywords'
                                    try:
                                        a = keywords[(idx := idx + 1)]

                                    except IndexError:  # ran off the end of keywords, now need to check if star lives here
                                        if ((sa := self.a).lineno, sa.col_offset) < (star.lineno, star.col_offset):
                                            name = 'args'
                                            idx  = len(args) - 1
                                            a    = star

                                        else:
                                            return None

                                    else:
                                        star_pos = (star.lineno, star.col_offset)

                                        if (((sa := self.a).lineno, sa.col_offset) < star_pos and
                                            (a.lineno, a.col_offset) > star_pos
                                        ):  # crossed star, jump back to it
                                            name = 'args'
                                            idx  = len(args) - 1
                                            a    = star

                        case 3:  # from Compare.comparators or Compare.left (via comparators)
                            next = 2

                            try:
                                a = aparent.ops[(idx := idx + 1)]
                            except IndexError:
                                return None

                        case 7:  # all the logic arguments
                            while True:
                                match name:
                                    case 'posonlyargs':
                                        posonlyargs = aparent.posonlyargs
                                        defaults    = aparent.defaults

                                        if (not defaults or (didx := (idx + ((ldefaults := len(defaults)) -
                                            len(args := aparent.args) - len(posonlyargs)))) < 0 or didx >= ldefaults
                                        ):
                                            try:
                                                a = posonlyargs[(idx := idx + 1)]

                                            except IndexError:
                                                name = 'args'
                                                idx  = -1

                                                continue

                                        else:
                                            name = 'defaults'
                                            a    = defaults[idx := didx]

                                    case 'args':
                                        args     = aparent.args
                                        defaults = aparent.defaults

                                        if (not defaults or (didx := (idx + ((ldefaults := len(defaults)) -
                                            len(args := aparent.args)))) < 0  # or didx >= ldefaults
                                        ):
                                            try:
                                                a = args[(idx := idx + 1)]

                                            except IndexError:
                                                name = 'vararg'

                                                if not (a := aparent.vararg):
                                                    continue

                                        else:
                                            name = 'defaults'
                                            a    = defaults[idx := didx]

                                    case 'defaults':
                                        if idx == (ldefaults := len(aparent.defaults)) - 1:  # end of defaults
                                            name = 'vararg'

                                            if not (a := aparent.vararg):
                                                continue

                                        elif (idx := idx + len(args := aparent.args) - ldefaults + 1) >= 0:
                                            name = 'args'
                                            a    = args[idx]

                                        else:
                                            name = 'posonlyargs'
                                            a    = (posonlyargs := aparent.posonlyargs)[(idx := idx + len(posonlyargs))]

                                    case 'vararg':
                                        if kwonlyargs := aparent.kwonlyargs:
                                            name = 'kwonlyargs'
                                            a    = kwonlyargs[(idx := 0)]

                                        elif a := aparent.kwarg:
                                            name = 'kwarg'
                                        else:
                                            return None

                                    case 'kwonlyargs':
                                        kwonlyargs = aparent.kwonlyargs

                                        if a := aparent.kw_defaults[idx]:
                                            name = 'kw_defaults'

                                        else:
                                            try:
                                                a = kwonlyargs[(idx := idx + 1)]

                                            except IndexError:
                                                if a := aparent.kwarg:
                                                    name = 'kwarg'
                                                else:
                                                    return None

                                    case 'kw_defaults':
                                        try:
                                            a = aparent.kwonlyargs[(idx := idx + 1)]

                                        except IndexError:
                                            if a := aparent.kwarg:
                                                name = 'kwarg'
                                            else:
                                                return None

                                        name = 'kwonlyargs'

                                    case 'kwarg':
                                        raise RuntimeError('should not get here')

                                break

                        case 4:  # from MatchMapping.keys
                            next = 5
                            a    = aparent.patterns[idx]

                        case 5:  # from MatchMapping.patterns
                            next = 4

                            try:
                                a = aparent.keys[(idx := idx + 1)]
                            except IndexError:
                                return None

                    if _with_loc(f := a.f, with_loc):
                        return f

            elif idx is not None:
                sibling = getattr(aparent, name)

                while True:
                    try:
                        if not (a := sibling[(idx := idx + 1)]):  # who knows where a `None` might pop up "next" these days... xD
                            continue

                    except IndexError:
                        break

                    if _with_loc(f := a.f, with_loc):
                        return f

            while next is not None:
                if isinstance(next, str):
                    name = next

                    if isinstance(sibling := getattr(aparent, next, None), AST):  # None because we know about fields from future python versions
                        if _with_loc(f := sibling.f, with_loc):
                            return f

                    elif isinstance(sibling, list) and sibling:
                        idx = -1

                        break

                    next = AST_FIELDS_NEXT[(aparent.__class__, name)]

                    continue

                # non-str next, special case

                match next:
                    case 2:  # from Compare.left
                        name = 'comparators'  # will cause to get .ops[0]
                        idx  = -1

                    case 6:  # from Call.func
                        idx  = -1  # will cause to get .args[0]

                break

            else:
                break

            continue

        return None

    def prev(self, with_loc: bool | Literal['own'] = True) -> Optional['FST']:  # TODO: refactor maybe
        """Get previous sibling in syntactic order, only within parent.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location,
            otherwise all nodes.

        **Returns:**
        - `None` if first valid sibling in parent, otherwise previous node.
        """

        if not (parent := self.parent):
            return None

        aparent   = parent.a
        name, idx = self.pfield

        while True:
            prev = AST_FIELDS_PREV[(aparent.__class__, name)]

            if isinstance(prev, int):  # special case?
                while True:
                    match prev:
                        case 0:  # from Dict.keys
                            if not idx:
                                return None

                            else:
                                prev = 1
                                a    = aparent.values[(idx := idx - 1)]

                        case 1:  # from Dict.values
                            prev = 0

                            if not (a := aparent.keys[idx]):
                                continue

                        case 6:
                            if not (keywords := aparent.keywords):  # no keywords
                                if idx:
                                    a = aparent.args[(idx := idx - 1)]

                                else:
                                    name = 'func'
                                    a    = aparent.func

                            elif not (args := aparent.args):  # no args
                                if idx:
                                    a = keywords[(idx := idx - 1)]

                                else:
                                    name = 'func'
                                    a    = aparent.func

                            elif not isinstance(star := args[-1], Starred):  # both args and keywords but no Starred
                                if name == 'args':
                                    if idx:
                                        a = aparent.args[(idx := idx - 1)]

                                    else:
                                        name = 'func'
                                        a    = aparent.func

                                else:
                                    if idx:
                                        a = keywords[(idx := idx - 1)]

                                    else:
                                        name = 'args'
                                        a    = args[(idx := len(args) - 1)]

                            else:  # args, keywords AND Starred
                                if name == 'args':
                                    if idx == len(args) - 1:  # is star
                                        star_pos = (star.lineno, star.col_offset)

                                        for i in range(len(keywords) - 1, -1, -1):
                                            if ((kw := keywords[i]).lineno, kw.col_offset) < star_pos:
                                                name = 'keywords'
                                                idx  = i
                                                a    = kw

                                                break

                                        else:
                                            if idx:
                                                a = args[(idx := idx - 1)]

                                            else:
                                                name = 'func'
                                                a    = aparent.func

                                    elif idx:
                                        a = args[(idx := idx - 1)]

                                    else:
                                        name = 'func'
                                        a    = aparent.func

                                else:  # name == 'keywords'
                                    star_pos = (star.lineno, star.col_offset)

                                    if not idx:
                                        name = 'args'

                                        if ((sa := self.a).lineno, sa.col_offset) > star_pos:  # all keywords above star so pass on to star
                                            idx  = len(args) - 1
                                            a    = star

                                        elif (largs := len(args)) < 2:  # no args left, we done here
                                            name = 'func'
                                            a    = aparent.func

                                        else:  # some args left, go to those
                                            a = args[(idx := largs - 2)]

                                    else:
                                        a = keywords[(idx := idx - 1)]

                                        if ((a.lineno, a.col_offset) < star_pos and
                                            ((sa := self.a).lineno, sa.col_offset) > star_pos
                                        ):  # crossed star walking back, return star
                                            name = 'args'
                                            idx  = len(args) - 1
                                            a    = star

                        case 2:  # from Compare.ops
                            if not idx:
                                prev = 'left'

                                break

                            else:
                                prev = 3
                                a    = aparent.comparators[(idx := idx - 1)]

                        case 3:  # from Compare.comparators
                            prev = 2
                            a    = aparent.ops[idx]

                        case 7:
                            while True:
                                match name:
                                    case 'posonlyargs':
                                        posonlyargs = aparent.posonlyargs
                                        defaults    = aparent.defaults

                                        if ((didx := idx - len(aparent.args) - len(posonlyargs) + len(defaults) - 1) >=
                                            0
                                        ):
                                            name = 'defaults'
                                            a    = defaults[(idx := didx)]

                                        elif idx > 0:
                                            a = posonlyargs[(idx := idx - 1)]
                                        else:
                                            return None

                                    case 'args':
                                        args     = aparent.args
                                        defaults = aparent.defaults

                                        if (didx := idx - len(args) + len(defaults) - 1) >= 0:
                                            name = 'defaults'
                                            a    = defaults[(idx := didx)]

                                        elif idx > 0:
                                            a = args[(idx := idx - 1)]

                                        elif posonlyargs := aparent.posonlyargs:
                                            name = 'posonlyargs'
                                            a    = posonlyargs[(idx := len(posonlyargs) - 1)]

                                        else:
                                            return None

                                    case 'defaults':
                                        args     = aparent.args
                                        defaults = aparent.defaults

                                        if (idx := idx + len(args) - len(defaults)) >= 0:
                                            name = 'args'
                                            a    = args[idx]

                                        else:
                                            name = 'posonlyargs'
                                            a    = (posonlyargs := aparent.posonlyargs)[idx + len(posonlyargs)]

                                    case 'vararg':
                                        if defaults := aparent.defaults:
                                            name = 'defaults'
                                            a    = defaults[(idx := len(defaults) - 1)]

                                        elif args := aparent.args:
                                            name = 'args'
                                            a    = args[(idx := len(args) - 1)]

                                        elif posonlyargs := aparent.posonlyargs:
                                            name = 'posonlyargs'
                                            a    = posonlyargs[(idx := len(posonlyargs) - 1)]

                                        else:
                                            return None

                                    case 'kwonlyargs':
                                        if not idx:
                                            name = 'vararg'

                                            if not (a := aparent.vararg):
                                                continue

                                        elif a := aparent.kw_defaults[(idx := idx - 1)]:
                                            name = 'kw_defaults'

                                        else:
                                            a = aparent.kwonlyargs[idx]

                                    case 'kw_defaults':
                                        name = 'kwonlyargs'
                                        a    = aparent.kwonlyargs[idx]

                                    case 'kwarg':
                                        if kw_defaults := aparent.kw_defaults:
                                            if a := kw_defaults[(idx := len(kw_defaults) - 1)]:
                                                name = 'kw_defaults'

                                            else:
                                                name = 'kwonlyargs'
                                                a    = (kwonlyargs := aparent.kwonlyargs)[(idx := len(kwonlyargs) - 1)]

                                        else:
                                            name = 'vararg'

                                            if not (a := aparent.vararg):
                                                continue

                                break

                        case 4:  # from Keys.keys
                            if not idx:
                                return None

                            else:
                                prev = 5
                                a    = aparent.patterns[(idx := idx - 1)]

                        case 5:  # from Keys.patterns
                            prev = 4
                            a    = aparent.keys[idx]

                    if _with_loc(f := a.f, with_loc):
                        return f

            else:
                sibling = getattr(aparent, name)

                while idx:
                    if not (a := sibling[(idx := idx - 1)]):
                        continue

                    if _with_loc(f := a.f, with_loc):
                        return f

            while prev is not None:
                if isinstance(prev, str):
                    name = prev

                    if isinstance(sibling := getattr(aparent, prev, None), AST):  # None because could have fields from future python versions
                        if _with_loc(f := sibling.f, with_loc):
                            return f

                    elif isinstance(sibling, list) and (idx := len(sibling)):
                        break

                    prev = AST_FIELDS_PREV[(aparent.__class__, name)]

                    continue

                # non-str prev, special case

                raise RuntimeError('should not get here')  # break  # when entrable special cases from ahead appear in future py versions add them here

            else:
                break

            continue

        return None

    def first_child(self, with_loc: bool | Literal['own'] = True) -> Optional['FST']:
        """Get first valid child in syntactic order.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location,
            otherwise all nodes.

        **Returns:**
        - `None` if no valid children, otherwise first valid child.
        """

        for name in AST_FIELDS[(a := self.a).__class__]:
            if (child := getattr(a, name, None)):
                if isinstance(child, AST):
                    if _with_loc(f := child.f, with_loc):
                        return f

                elif isinstance(child, list):
                    if (c := child[0]) and _with_loc(f := c.f, with_loc):
                        return f

                    return FST(Pass(), self, astfield(name, 0)).next(with_loc)  # Pass() is a hack just to have a simple AST node

        return None

    def last_child(self, with_loc: bool | Literal['own'] = True) -> Optional['FST']:
        """Get last valid child in syntactic order.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location,
            otherwise all nodes.

        **Returns:**
        - `None` if no valid children, otherwise last valid child.
        """

        if (isinstance(a := self.a, Call)) and a.args and (keywords := a.keywords) and isinstance(a.args[-1], Starred):  # super-special case Call with args and keywords and a Starred, it could be anywhere in there, including after last keyword, defer to prev() logic
            fst          = FST(f := Pass(), self, astfield('keywords', len(keywords)))
            f.lineno     = 0x7fffffffffffffff
            f.col_offset = 0

            return fst.prev(with_loc)

        for name in reversed(AST_FIELDS[(a := self.a).__class__]):
            if (child := getattr(a, name, None)):
                if isinstance(child, AST):
                    if _with_loc(f := child.f, with_loc):
                        return f

                elif isinstance(child, list):
                    if (c := child[-1]) and _with_loc(f := c.f, with_loc):
                        return f

                    return FST(Pass(), self, astfield(name, len(child) - 1)).prev(with_loc)  # Pass() is a hack just to have a simple AST node

        return None

    def next_child(self, from_child: Optional['FST'], with_loc: bool | Literal['own'] = True) -> Optional['FST']:
        """Get next child in syntactic order. Meant for simple iteration. This is a slower way to iterate, `walk()` is
        faster.

        **Parameters:**
        - `from_child`: Child node we are coming from which may or may not have location.
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location,
            otherwise all nodes.

        **Returns:**
        - `None` if last valid child in `self`, otherwise next child node.
        """

        return self.first_child(with_loc) if from_child is None else from_child.next(with_loc)

    def prev_child(self, from_child: Optional['FST'], with_loc: bool | Literal['own'] = True) -> Optional['FST']:
        """Get previous child in syntactic order. Meant for simple iteration. This is a slower way to iterate, `walk()`
        is faster.

        **Parameters:**
        - `from_child`: Child node we are coming from which may or may not have location.
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location,
            otherwise all nodes.

        **Returns:**
        - `None` if first valid child in `self`, otherwise previous child node.
        """

        return self.last_child(with_loc) if from_child is None else from_child.prev(with_loc)

    def next_step(self, with_loc: bool | Literal['own'] | Literal['allown'] = True, *,
                  recurse_self: bool = True) -> Optional['FST']:
        """Get next node in syntactic order over entire tree. Will walk up parents and down children to get the next
        node, returning `None` only when we are at the end of the whole thing.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location
            (does not recurse into non-own nodes), `'allown'` means return `'own'` nodes but recurse into nodes with
            non-own locations, otherwise all nodes.
        - `recurse_self`: Whether to allow recursion of `self` to return children or move directly to next nodes.

        **Returns:**
        - `None` if last valid node in tree, otherwise next node in order.
        """

        if allown := with_loc == 'allown':
            with_loc = True

        while True:
            if not recurse_self or not (fst := self.first_child(with_loc)):
                recurse_self = True

                while not (fst := self.next(with_loc)):
                    if not (self := self.parent):
                        return None

            if not allown or fst.has_own_loc:
                break

            self = fst

        return fst

    def prev_step(self, with_loc: bool | Literal['own'] | Literal['allown'] = True, *,
                  recurse_self: bool = True) -> Optional['FST']:
        """Get prev node in syntactic order over entire tree. Will walk up parents and down children to get the next
        node, returning `None` only when we are at the beginning of the whole thing.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location
            (does not recurse into non-own nodes), `'allown'` means return `'own'` nodes but recurse into nodes with
            non-own locations, otherwise all nodes.
        - `recurse_self`: Whether to allow recursion of `self` to return children or move directly to prev nodes.

        **Returns:**
        - `None` if first valid node in tree, otherwise prev node in order.
        """

        if allown := with_loc == 'allown':
            with_loc = True

        while True:
            if not recurse_self or not (fst := self.last_child(with_loc)):
                recurse_self = True

                while not (fst := self.prev(with_loc)):
                    if not (self := self.parent):
                        return None

            if not allown or fst.has_own_loc:
                break

            self = fst

        return fst

    def walk(self, with_loc: bool | Literal['own'] = False, *, self_: bool = True, recurse: bool = True,
             scope: bool = False, back: bool = False) -> Generator['FST', bool, None]:
        """Walk self and descendants in syntactic order, `send(False)` to skip recursion into child. `send(True)` to
        allow recursion into child if called with `recurse=False` or `scope=True` would otherwise disallow it. Can send
        multiple times, last value sent takes effect. The walk is defined forwards or backwards in that it returns a
        parent then recurses into the children and walks those in the given direction, recursing into each child's
        children before continuing with siblings.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, `'own'` means only nodes with own location
            (does not recurse into non-own nodes), otherwise all nodes.
        - `self_`: If `True` then self will be returned first with the possibility to skip children with `send()`.
        - `recurse`: Whether to recurse into children by default, `send()` for a given node will always override this.
            Will always attempt first level of children unless walking self and `False` is sent first.
        - `scope`: If `True` then will walk only within the scope of `self`. Meaning if called on a `FunctionDef` then
            will only walk children which are within the function scope. Will yield children which have with their own
            scopes, and the parts of them which are visible in this scope (like default argument values), but will not
            recurse into them unless `send(True)` is done for that child.
        - `back`: If `True` then walk every node in reverse syntactic order. This is not the same as a full forwards
            walk reversed due to recursion (parents are still returned before children, only in reverse sibling order).

        **Example:**
        ```py
        for node in (walking := target.walk()):
            ...
            if i_dont_like_the_node:
                walking.send(False)  # skip walking this node's children, don't use return value here, keep using for loop as normal
        ```
        """

        if self_:
            if not _with_loc(self, with_loc):
                return

            recurse_ = 1

            while (sent := (yield self)) is not None:
                recurse_ = sent

            if not recurse_:
                return

            elif recurse_ is True:  # user changed their mind?!?
                recurse = True
                scope   = False

        stack = None
        ast   = self.a

        if scope:  # some parts of a FunctionDef or ClassDef are outside its scope
            if isinstance(ast, list):
                stack = ast[:] if back else ast[::-1]

            elif isinstance(ast, (ClassDef, Module, Interactive)):
                if back:
                    stack = []

                    if type_params := getattr(ast, 'type_params', None):
                        stack.extend(type_params)

                    stack.extend(ast.body)

                else:
                    stack = ast.body[::-1]

                    if type_params := getattr(ast, 'type_params', None):
                        stack.extend(type_params[::-1])

            elif (is_func := isinstance(ast, (FunctionDef, AsyncFunctionDef))) or isinstance(ast, Lambda):
                if back:
                    stack = []

                    if type_params := getattr(ast, 'type_params', None):
                        stack.extend(type_params)

                    stack.append(ast.args)

                    if is_func:
                        stack.extend(ast.body)
                    else:
                        stack.append(ast.body)

                else:
                    stack = ast.body[::-1] if is_func else [ast.body]

                    stack.append(ast.args)

                    if type_params := getattr(ast, 'type_params', None):
                        stack.extend(type_params[::-1])

            elif (is_elt := isinstance(ast, (ListComp, SetComp, GeneratorExp))) or isinstance(ast, DictComp):
                if back:
                    stack = ([ast.elt] if is_elt else [ast.key, ast.value]) + (generators := ast.generators)
                else:
                    stack = (generators := ast.generators)[::-1] + ([ast.elt] if is_elt else [ast.value, ast.key])

                skip_iter = generators[0].iter

            elif isinstance(ast, Expression):
                stack = [ast.body]

        if stack is None:
            stack = syntax_ordered_children(ast)

            if not back:
                stack = stack[::-1]

        while stack:
            if not (ast := stack.pop()):
                continue

            fst = ast.f

            if not _with_loc(fst, with_loc):
                continue

            recurse_ = recurse

            while (sent := (yield fst)) is not None:
                recurse_ = 1 if sent else False

            if recurse_ is not True:
                if recurse_:  # user did send(True), walk this child unconditionally
                    yield from fst.walk(with_loc, self_=False, back=back)

            else:
                if scope:
                    recurse_ = False

                    if isinstance(ast, ClassDef):
                        if back:
                            stack.extend(ast.decorator_list)
                            stack.extend(ast.bases)
                            stack.extend(ast.keywords)

                        else:
                            stack.extend(ast.keywords[::-1])
                            stack.extend(ast.bases[::-1])
                            stack.extend(ast.decorator_list[::-1])

                    elif isinstance(ast, (FunctionDef, AsyncFunctionDef)):
                        if back:
                            stack.extend(ast.decorator_list)
                            stack.extend(ast.args.defaults)
                            stack.extend(ast.args.kw_defaults)

                        else:
                            stack.extend(ast.args.kw_defaults[::-1])
                            stack.extend(ast.args.defaults[::-1])
                            stack.extend(ast.decorator_list[::-1])

                    elif isinstance(ast, Lambda):
                        if back:
                            stack.extend(ast.args.defaults)
                            stack.extend(ast.args.kw_defaults)
                        else:
                            stack.extend(ast.args.kw_defaults[::-1])
                            stack.extend(ast.args.defaults[::-1])

                    elif isinstance(ast, (ListComp, SetComp, DictComp, GeneratorExp)):
                        comp_first_iter = ast.generators[0].iter
                        gen             = fst.walk(with_loc, self_=False, back=back)

                        for f in gen:  # all NamedExpr assignments below are visible here, yeah, its ugly
                            if (a := f.a) is comp_first_iter or (f.pfield.name == 'target' and isinstance(a, Name) and
                                                                 isinstance(f.parent.a, NamedExpr)):
                                subrecurse = recurse

                                while (sent := (yield f)) is not None:
                                    subrecurse = sent

                                if not subrecurse:
                                    gen.send(False)

                    elif isinstance(ast, comprehension):  # this only comes from top level comprehension, not ones encountered here
                        if back:
                            stack.append(ast.target)

                            if (a := ast.iter) is not skip_iter:
                                stack.append(a)

                            if a := ast.ifs:
                                stack.extend(a)

                        else:
                            if a := ast.ifs:
                                stack.extend(a)

                            if (a := ast.iter) is not skip_iter:
                                stack.append(a)

                            stack.append(ast.target)

                    else:
                        recurse_ = True

                if recurse_:
                    children = syntax_ordered_children(ast)

                    stack.extend(children if back else children[::-1])

    def is_parsable(self) -> bool:
        """Really means the AST is `unparse()`able and then re`parse()`able which will get it to this top level AST node
        surrounded by the appropriate `ast.mod`. The source may change a bit though, parentheses, 'if' <-> 'elif'."""

        if not is_parsable(self.a) or not self.loc:
            return False

        ast    = self.a
        parent = self.parent

        if isinstance(ast, Tuple):  # tuple of slices used in indexing (like numpy)
            for e in ast.elts:
                if isinstance(e, Slice):
                    return False

        elif parent:
            if isinstance(ast, JoinedStr):  # formatspec '.1f' type strings without quote delimiters
                if self.pfield.name == 'format_spec' and isinstance(parent.a, FormattedValue):
                    return False

            elif isinstance(ast, Constant):  # string parts of f-string without quote delimiters
                if self.pfield.name == 'values' and isinstance(parent.a, JoinedStr) and isinstance(ast.value, str):
                    return False

        return True

    def is_parenthesized_tuple(self) -> bool | None:
        """Whether `self` is a parenthesized `Tuple` or not, or not a `Tuple` at all.

        **Returns:**
        - `True` if is parenthesized `Tuple`, `False` if is unparenthesized `Tuple`, `None` if is not `Tuple`."""

        if not isinstance(self.a, Tuple):
            return None

        self_ln, self_col, self_end_ln, self_end_col = self.loc

        lines = self.root._lines

        if not lines[self_end_ln].startswith(')', self_end_col - 1):
            return False

        if not (elts := self.a.elts):
            return True

        if not lines[self_ln].startswith('(', self_col):
            return False

        f0_ln, f0_col, f0_end_ln, f0_end_col = elts[0].f.loc

        if f0_col == self_col and f0_ln == self_ln:
            return False

        _, _, fn_end_ln, fn_end_col = elts[-1].f.loc

        if fn_end_col == self_end_col and fn_end_ln == self_end_ln:
            return False

        # dagnabit! have to count parens

        self_end_col -= 1  # because for sure there is a comma between end of first element and end of tuple, so at worst we exclude either the tuple closing paren or a comma

        nparens = _next_pars(lines, self_ln, self_col, self_end_ln, self_end_col, '(')[-1]  # yes, we use _next_pars() to count opening parens because we know conditions allow it

        if not nparens:
            return False

        nparens -= _next_pars(lines, f0_end_ln, f0_end_col, self_end_ln, self_end_col)[-1]

        return nparens > 0  # don't want to fiddle with checking if f0 is a parenthesized tuple

    def is_empty_set_call(self) -> bool:
        """Whether `self` is an empty `set()` call."""

        return (isinstance(ast := self.a, Call) and not ast.args and not ast.keywords and
                isinstance(func := ast.func, Name) and func.id == 'set' and isinstance(func.ctx, Load))

    def is_elif(self) -> bool:
        """Whether `self` is an `elif`."""

        return isinstance(self.a, If) and self.root._lines[(loc := self.loc).ln].startswith('elif', loc.col)

    def get_indent(self) -> str:
        """Determine proper indentation of node at `stmt` (or other similar) level at or above `self`. Even if it is a
        continuation or on same line as block statement. If indentation is impossible to determine because is solo
        statement on same line as parent block, then the current tree default indentation is added to the  parent block
        indentation and returned.

        **Returns:**
        - `str`: Entire indentation string for the block this node lives in (not just a single level).
        """

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
            self = parent

        lines        = (root := self.root)._lines
        extra_indent = ''  # may result from unknown indent in single line "if something: whats_my_stmt_indentation?"

        while parent:
            siblings = getattr(parent.a, self.pfield.name)

            for i in range(1, len(siblings)):  # first try simple rules for all elements past first one
                self = siblings[i].f

                if re_empty_line.match(line_start := lines[(ln := self.ln)], 0, col := self.col):
                    prev    = self.prev(True)  # there must be one
                    end_col = 0 if prev.end_ln < (preceding_ln := ln - 1) else prev.end_col

                    if not re_line_continuation.match(lines[preceding_ln], end_col):
                        return line_start[:col] + extra_indent

            self        = siblings[0].f  # didn't find in siblings[1:], now the special rules for the first one
            ln          = self.ln
            col         = self.col
            prev        = self.prev(True)  # there may not be one ("try" at start of module)
            prev_end_ln = prev.end_ln if prev else -2

            while ln > prev_end_ln and re_empty_line.match(line_start := lines[ln], 0, col):
                end_col = 0 if (preceding_ln := ln - 1) != prev_end_ln else prev.end_col

                if not ln or not re_line_continuation.match((l := lines[preceding_ln]), end_col):
                    return line_start[:col] + extra_indent

                ln  = preceding_ln
                col = len(l) - 1  # was line continuation so last char is '\' and rest should be empty

            if isinstance(parent, mod):  # otherwise would add extra level of indentation
                break

            extra_indent += root.indent
            self          = parent
            parent        = self.parent

        # TODO: handle possibility of syntactically incorrect but indented root node?

        return extra_indent

    def get_indentable_lns(self, skip: int = 0, *, docstr: bool | str = DEFAULT_DOCSTR) -> set[int]:
        """Get set of indentable lines within this node.

        **Parameters:**
        - `skip`: The number of lines to skip from the start of this node. Useful for skipping the first line for edit
            operations (since the first line is normally joined to an existing line on add or copied directly from start
            on cut).
        - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
            multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
            in expected docstring positions are indentable.

        **Returns:**
        - `set[int]`: Set of line numbers (zero based) which are sytactically indentable.
        """

        def walk_multiline(cur_ln, end_ln, m, re_str_end):
            nonlocal lns, lines

            col = m.end()

            for ln in range(cur_ln, end_ln + 1):
                if m := re_str_end.match(lines[ln], col):
                    break

                col = 0

            else:
                raise RuntimeError('should not get here')

            lns -= set(range(cur_ln + 1, ln + 1))  # specifically leave out first line of multiline string because that is indentable

            return ln, m.end()

        def multiline_str(f: 'FST'):
            nonlocal lns, lines

            cur_ln, cur_col, end_ln, end_col = f.loc

            while True:
                if not (m := re_multiline_str_start.match(l := lines[cur_ln], cur_col)):
                    if m := re_oneline_str.match(l, cur_col):
                        cur_col = m.end()

                    else:  # UGH! a line continuation string, pffft...
                        m               = re_contline_str_start.match(l, cur_col)
                        re_str_end      = re_contline_str_end_sq if m.group(1) == "'" else re_contline_str_end_dq
                        cur_ln, cur_col = walk_multiline(cur_ln, end_ln, m, re_str_end)  # find end of multiline line continuation string

                else:
                    re_str_end      = re_multiline_str_end_sq if m.group(1) == "'''" else re_multiline_str_end_dq
                    cur_ln, cur_col = walk_multiline(cur_ln, end_ln, m, re_str_end)  # find end of multiline string

                if cur_ln == end_ln and cur_col == end_col:
                    break

                cur_ln, cur_col, _ = _next_src(lines, cur_ln, cur_col, end_ln, end_col)  # there must be a next one

        def multiline_fstr(f: 'FST'):
            """Lets try to find indentable lines by incrementally attempting to parse parts of multiline f-string."""

            nonlocal lns, lines

            cur_ln, cur_col, end_ln, _ = f.loc

            while True:
                ls = [lines[cur_ln][cur_col:].lstrip()]

                for ln in range(cur_ln + 1, end_ln + 1):
                    try:
                        ast_parse('\n'.join(ls))

                    except SyntaxError:
                        lns.remove(ln)
                        ls.append(lines[ln])

                    else:
                        break

                if (cur_ln := ln) >= end_ln:
                    assert cur_ln == end_ln

                    break

                cur_col = 0

        # if docstr is None:
        #     docstr = self.root.default_docstr

        strict = docstr == 'strict'
        lines  = self.root.lines
        lns    = set(range(skip, len(self._lines))) if self.is_root else set(range(self.bln + skip, self.bend_ln + 1))

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
            self = parent

        for f in (walking := self.walk(False)):  # find multiline strings and exclude their unindentable lines
            if f.bend_ln == f.bln:  # everything on one line, don't need to recurse
                walking.send(False)

            elif isinstance(a := f.a, Constant):
                if (  # isinstance(f.a.value, (str, bytes)) is a given if bend_ln != bln
                    not docstr or
                    not ((parent := f.parent) and isinstance(parent.a, Expr) and
                         (not strict or ((pparent := parent.parent) and parent.pfield == ('body', 0) and
                                         isinstance(pparent.a, HAS_DOCSTRING)
                )))):
                    multiline_str(f)

            elif isinstance(a, JoinedStr):
                multiline_fstr(f)

                walking.send(False)  # skip everything inside regardless, because it is evil

        return lns

    def locmock(self, loc: fstloc) -> 'FST':
        """Create a "location mockup" to this object with an explicit location. This can be used to override the
        location of an object for certain operations, but is not very robust. The `FST` returned is its own object and
        points up the tree and to the `AST` like the original, but the `AST` does not point back to it and so in not a
        fully valid node. Both `loc` and `bloc` are set to the input parameter `loc` value. You can make a `locmock` of
        a `locmock`. EXPERIMENTAL!"""

        ast      = self.a
        fst      = FST(ast, self.parent, self.pfield)
        ast.f    = self
        fst._loc = fst._bloc = loc

        return fst

    def pars(self, ret_fst: bool | None = True) -> Union['FST', fstloc, None]:
        """Return the location of enclosing parentheses either as an `fstloc` or an `FST`. If requesting an `FST` then
        the return value can be `self` or a clone `FST` of `self` with modified `loc` which should only be used for a
        limited number of things. Will balance parentheses if `self` is an element of a tuple and not return the
        parentheses of the tuple. Likwise will not return the parentheses of an enclosing `arguments` parent. Only
        works on (and makes sense for) `expr` or `pattern` nodes, otherwise returns `self` or `self.bloc`.

        **Parameters:**
        - `ret_fst`: If `True` then always return an `FST` (`self` or clone), `False` will always return an `fstloc`
            (which could be `self.bloc`) and `None` can return an `fstloc` or `self` if no parentheses found.

        **Returns:**
        - `fstloc | FST | None`: If `ret_fst` is `None` and no parentheses found then just returns `self`. A `None` can
            be returned if `ret_fst` is `False` and there are no enclosing parentheses and `self` does not have a `loc`.
        """

        if not isinstance(self.a, PARENTHESIZABLE):
            return self.bloc if ret_fst is False else self

        pars_end_ln, pars_end_col, ante_end_ln, ante_end_col, nrpars = self._rpars()

        if not nrpars:
            return self.bloc if ret_fst is False else self

        pars_ln, pars_col, ante_ln, ante_col, nlpars = self._lpars()

        if not nlpars:
            return self.bloc if ret_fst is False else self

        dpars = nlpars - nrpars

        if dpars == 1:  # unbalanced due to enclosing tuple, will always be unbalanced if at ends of parenthesized tuple (even if solo element) due to commas
            pars_ln  = ante_ln
            pars_col = ante_col

        elif dpars == -1:
            pars_end_ln  = ante_end_ln
            pars_end_col = ante_end_col

        elif dpars:
            raise RuntimeError('should not get here')

        loc = fstloc(pars_ln, pars_col, pars_end_ln, pars_end_col)

        return self.locmock(loc) if ret_fst else loc

    def comms(self, ret_fst: bool | None = True, fmt: bool | Fmt = True) -> Union['FST', fstloc, None]:
        """Return the location of preceding and trailing comments (if present and requested). If requesting an `FST`
        then the return value can be `self` or a clone `FST` of `self` with modified `loc` (and `bloc`)  which should
        only be used for a limited number of things. Only works on (and makes sense for) `stmt`, 'ExceptHandler' or
        `match_case` nodes, otherwise returns `self` or `self.bloc`.

        **Parameters:**
        - `ret_fst`: If `True` then always return an `FST` (`self` or clone), `False` will always return an `fstloc`
            (which could be `self.bloc`) and `None` can return an `fstloc` or `self` if no comments found.
        - `fmt': Which comments to include, can be comma delimited string or a set of flags. `True` means `'pre,post'`,
            `False` means no comments, recognized flags are:
            - `'pre'`: Contiguous comment block immediately preceding statement(s).
            - `'allpre'`: Comment blocks (possibly separated by empty lines) preceding statement(s).
            - `'post'`: Comment trailing on last line. Keep in mind this is the comment on the last statement of a body
                if last element of copy is a block element.
            - `'blkpost'`: Contiguous comment block following statement(s).
            - `'allpost'`: Comment blocks (possibly separated by empty lines) following statement(s).

        **Returns:**
        - `fstloc | FST | None`: If `ret_fst` is `None` and no comments found then just returns `self`. A `None` can
            be returned if `ret_fst` is `False` and there are no comments and `self` does not have a `loc`.
        """

        if fmt is True:
            fmt = DEFAULT_COMMS_FMT
        elif isinstance(fmt, str):
            fmt = frozenset(t for s in fmt.split(',') if (t := s.strip()))

        if not fmt or not isinstance(self.a, STATEMENTISH):
            return self.bloc if ret_fst is False else self

        src_edit = self.src_edit
        lines    = self.root._lines
        loc      = self.bloc

        comms_loc = fstloc(
            *(src_edit.pre_comments(lines, *self._prev_ast_bound(), loc.ln, loc.col, fmt) or loc[:2]),
            *(src_edit.post_comments(lines, loc.end_ln, loc.end_col, *self._next_ast_bound(), fmt) or loc[2:]),
        )

        if ret_fst is False:
            return comms_loc

        if comms_loc == self.loc:  # only if self.bloc == self.loc, because otherwise returned .loc should be bloc
            return self

        if not ret_fst:
            return comms_loc

        return self.locmock(comms_loc)

    # ------------------------------------------------------------------------------------------------------------------

    def touch(self) -> 'FST':  # -> Self:
        """AST node was modified, clear out any cached info for this node specifically, call this for each node in a
        walk with modified nodes."""

        try:
            del self._loc, self._bloc  # _bloc only exists if _loc does
        except AttributeError:
            pass

        return self

    def touchall(self, parents: bool = True, children: bool = True, self_: bool = True) -> 'FST':  # -> Self:
        """Touch self, parents and all children, optionally."""

        if children:
            stack = [self.a] if self_ else list(iter_child_nodes(self.a))

            while stack:
                child = stack.pop()

                child.f.touch()
                stack.extend(iter_child_nodes(child))

        elif self_:
            self.touch()

        if parents:
            parent = self

            while parent := parent.parent:
                parent.touch()

        return self

    def offset(self, ln: int, col: int, dln: int, dcol_offset: int, inc: bool = False, stop_at: Optional['FST'] = None
               ) -> 'FST':  # -> Self
        """Offset ast node positions in the tree on or after ln / col by delta line / col_offset (column byte offset).

        This only offsets the positions in the `AST` nodes, doesn't change any text, so make sure that is correct before
        getting any `FST` locations from affected nodes otherwise they will be wrong.

        Other nodes outside this tree might need offsetting so use only on root unless special circumstances.

        If offsetting a zero-length node (which can result from deleting elements of an unparenthesized tuple), both the
        start and end location will be moved if exactly at offset point if `inc` is `False`. Otherwise if `inc` is
        `True` then the start position will remain and the end position will be expanded.

        **Parameters:**
        - `ln`: Line of offset point.
        - `col`: Column of offset point (char index).
        - `dln`: Number of lines to offset everything on or after offset point, can be 0.
        - `dcol_offset`: Column offset to apply to everything ON the offset point line `ln` (in bytes). Columns not on
            line `ln` will not be changed.
        - `inc`: Whether to offset endpoint if it falls exactly at ln / col or not (inclusive).

        **Behavior:**
        ```
              offset here
              V
          |===|
              |---|
              |        <- special zero length span
        0123456789ABC

        +2, inc=False
              V
          |===|
                |---|
                |
        0123456789ABC

        +2, inc=True
              V
          |=====|
                |---|
              |.|
        0123456789ABC

        -2, inc=False
              V
          |===|
            |---|
            |.|
        0123456789ABC

        -2, inc=True
              V
          |=|
            |---|
            |
        0123456789ABC
        ```
        """

        lno  = ln + 1
        colo = (l := ls[ln]).c2b(min(col, len(l))) if ln < len(ls := self.root._lines) else 0x7fffffffffffffff

        for f in (walking := self.walk(False)):
            a = f.a

            if (fend_colo := getattr(a, 'end_col_offset', None)) is not None:
                flno  = a.lineno
                fcolo = a.col_offset

                if (fend_lno := a.end_lineno) > lno:
                    a.end_lineno += dln

                elif fend_lno == lno:
                    if (fend_colo >= colo if (inc or (fend_colo == fcolo and fend_lno == flno and
                                                      (dln > 0 or (not dln and dcol_offset > 0)))) else
                        fend_colo > colo
                    ):
                        a.end_lineno     += dln
                        a.end_col_offset  = fend_colo + dcol_offset

                else:
                    walking.send(False)  # no need to walk into something whose bounding block ends before offset point

                    continue

                if flno > lno:
                    if not dln and (not (decos := getattr(a, 'decorator_list', None)) or decos[0].lineno > lno):
                        walking.send(False)  # no need to walk into something past offet point if line change is 0

                        continue

                    a.lineno += dln

                elif flno == lno and (
                        fcolo >= colo if (not (inc and (fend_colo == fcolo and fend_lno == flno)) or
                                          dln < 0 or (not dln and dcol_offset < 0)) else
                        fcolo > colo
                ):
                    a.lineno     += dln
                    a.col_offset += dcol_offset

            if f is stop_at:
                walking.send(False)

            f.touch()

        self.touchall(True, False, False)

        return self

    def offset_cols(self, dcol_offset: int, lns: set[int]):
        """Offset ast col byte offsets in `lns` by `dcol_offset`. Only modifies ast, not lines. Does not modify parent
        locations."""

        if dcol_offset:
            for a in walk(self.a):
                if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                    if a.lineno - 1 in lns:
                        a.col_offset += dcol_offset

                    if a.end_lineno - 1 in lns:
                        a.end_col_offset = end_col_offset + dcol_offset

                a.f.touch()

            self.touchall(True, False, False)

    def offset_cols_mapped(self, dcol_offsets: dict[int, int]):
        """Offset ast col byte offsets by a specific `dcol_offset` per line. Only modifies ast, not lines. Does not
        modify parent locations."""

        for a in walk(self.a):
            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                if (dcol_offset := dcol_offsets.get(a.lineno - 1)) is not None:
                    a.col_offset += dcol_offset

                if (dcol_offset := dcol_offsets.get(a.end_lineno - 1)) is not None:
                    a.end_col_offset = end_col_offset + dcol_offset

            a.f.touch()

        self.touchall(True, False, False)

    def indent_lns(self, indent: str | None = None, lns: set[int] | None = None, *,
                   docstr: bool | str = DEFAULT_DOCSTR, skip: int = 1) -> set[int]:
        """Indent all indentable lines specified in `lns` with `indent` and adjust node locations accordingly.

        WARNING! This does not offset parent nodes.

        **Parameters:**
        - `indent`: The indentation string to prefix to each indentable line.
        - `lns`: A `set` of lines to apply identation to. If `None` then will be gotten from
            `get_indentable_lns(skip=skip)`.
        - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
            multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
            in expected docstring positions are indentable.
        - `skip`: If not providing `lns` then this value is passed to `get_indentable_lns()`.

        **Returns:**
        - `set[int]`: `lns` passed in or otherwise set of line numbers (zero based) which are sytactically indentable.
        """

        root = self.root

        if indent is None:
            indent = root.indent
        # if docstr is None:
        #     docstr = root.default_docstr

        if not ((lns := self.get_indentable_lns(skip, docstr=docstr)) if lns is None else lns) or not indent:
            return lns

        self.offset_cols(len(indent.encode()), lns)

        lines = root._lines

        for ln in lns:
            if l := lines[ln]:  # only indent non-empty lines
                lines[ln] = bistr(indent + l)

        self.reparse_docstrings(docstr)

        return lns

    def dedent_lns(self, indent: str | None = None, lns: set[int] | None = None, *,
                   docstr: bool | str = DEFAULT_DOCSTR, skip: int = 1) -> set[int]:
        """Dedent all indentable lines specified in `lns` by removing `indent` prefix and adjust node locations
        accordingly. If cannot dedent entire amount will dedent as much as possible.

        WARNING! This does not offset parent nodes.

        **Parameters:**
        - `indent`: The indentation string to remove from the beginning of each indentable line (if possible).
        - `lns`: A `set` of lines to apply dedentation to. If `None` then will be gotten from
            `get_indentable_lns(skip=skip)`.
        - `docstr`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all `Expr`
            multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline strings
            in expected docstring positions are indentable.
        - `skip`: If not providing `lns` then this value is passed to `get_indentable_lns()`.

        **Returns:**
        - `set[int]`: `lns` passed in or otherwise set of line numbers (zero based) which are sytactically indentable.
        """

        root = self.root

        if indent is None:
            indent = root.indent
        # if docstr is None:
        #     docstr = root.default_docstr

        if not ((lns := self.get_indentable_lns(skip, docstr=docstr)) if lns is None else lns) or not indent:
            return lns

        lines        = root._lines
        lindent      = len(indent)
        dcol_offsets = None
        newlines     = []

        def dedent(l, lindent):
            if dcol_offsets is not None:
                dcol_offsets[ln] = -lindent

            return bistr(l[lindent:])

        lns_seq = list(lns)

        for ln in lns_seq:
            if l := lines[ln]:  # only dedent non-empty lines
                if l.startswith(indent) or (lempty_start := re_empty_line_start.match(l).end()) >= lindent:
                    l = dedent(l, lindent)

                else:
                    if not dcol_offsets:
                        dcol_offsets = {}

                        for ln2 in lns_seq:
                            if ln2 is ln:
                                break

                            dcol_offsets[ln2] = -lindent

                    l = dedent(l, lempty_start)

            newlines.append(l)

        for ln, l in zip(lns_seq, newlines):
            lines[ln] = l

        if dcol_offsets:
            self.offset_cols_mapped(dcol_offsets)
        else:
            self.offset_cols(-lindent, lns)

        self.reparse_docstrings(docstr)

        return lns

    def reparse_docstrings(self, docstr: bool | str = DEFAULT_DOCSTR):
        """Reparse docstrings in `self` and all descendants.

        **Parameters:**
        - `docstr`: Which strings to reparse. `True` means all `Expr` multiline strings. `'strict'` means only multiline
            strings in expected docstring. `False` doesn't reparse anything and just returns.
        """

        # if docstr is None:
        #     docstr = self.root.default_docstr

        if not docstr:
            return

        if docstr != 'strict':  # True
            for a in walk(self.a):
                if isinstance(a, Expr) and isinstance(v := a.value, Constant) and isinstance(v.value, str):
                    v.value = literal_eval((f := a.f).get_src(*f.loc))

        else:
            for a in walk(self.a):
                if isinstance(a, HAS_DOCSTRING):
                    if ((body := a.body) and isinstance(b0 := body[0], Expr) and isinstance(v := b0.value, Constant) and
                        isinstance(v.value, str)
                    ):
                        v.value = literal_eval((f := b0.f).get_src(*f.loc))
