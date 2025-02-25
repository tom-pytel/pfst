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
DEFAULT_DOCSTRING       = True

STATEMENTISH            = (stmt, ExceptHandler, match_case)  # always in lists, cannot be inside multilines
STATEMENTISH_OR_MOD     = (stmt, ExceptHandler, match_case, mod)
STATEMENTISH_OR_STMTMOD = (stmt, ExceptHandler, match_case, Module, Interactive)
NAMED_SCOPE_OR_MOD      = (FunctionDef, AsyncFunctionDef, ClassDef, mod)
SCOPE_OR_MOD            = (FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp, GeneratorExp,
                           mod)
BLOCK_OR_MOD            = (FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If, With, AsyncWith, Match,
                           Try, TryStar, ExceptHandler, match_case, mod)
HAS_DOCSTRING           = (FunctionDef, AsyncFunctionDef, ClassDef)

re_empty_line_start     = re.compile(r'[ \t]*')    # start of completely empty or space-filled line (from start pos, start of line indentation)
re_empty_line           = re.compile(r'[ \t]*$')   # completely empty or space-filled line (from start pos, start of line indentation)
re_line_continuation    = re.compile(r'[^#]*\\$')  # line continuation with backslash not following a comment start '#' (from start pos, assumed no asts contained in line)

re_oneline_str          = re.compile(r'(?:b|r|rb|br|u|)  (?:  \'(?:\\.|[^\\\'])*?\'  |  "(?:\\.|[^\\"])*?"  )', re.VERBOSE | re.IGNORECASE)  # I f^\\\'])*\'ng hate these!
re_contline_str_start   = re.compile(r'(?:b|r|rb|br|u|)  (\'|")', re.VERBOSE | re.IGNORECASE)
re_contline_str_end_sq  = re.compile(r'(?:\\.|[^\\\'])*?  \'', re.VERBOSE)
re_contline_str_end_dq  = re.compile(r'(?:\\.|[^\\"])*?  "', re.VERBOSE)
re_multiline_str_start  = re.compile(r'(?:b|r|rb|br|u|)  (\'\'\'|""")', re.VERBOSE | re.IGNORECASE)
re_multiline_str_end_sq = re.compile(r'(?:\\.|[^\\])*?  \'\'\'', re.VERBOSE)
re_multiline_str_end_dq = re.compile(r'(?:\\.|[^\\])*?  """', re.VERBOSE)

re_next_src                     = re.compile(r'\s*([^\s#\\]+)')          # next non-space non-continuation non-comment code text, don't look into strings with this!
re_next_src_or_comment          = re.compile(r'\s*([^\s#\\]+|#.*)')      # next non-space non-continuation code or comment text, don't look into strings with this!
re_next_src_or_lcont            = re.compile(r'\s*([^\s#\\]+|\\$)')      # next non-space non-comment code including logical line end, don't look into strings with this!
re_next_src_or_comment_or_lcont = re.compile(r'\s*([^\s#\\]+|#.*|\\$)')  # next non-space non-continuation code or comment text including logical line end, don't look into strings with this!

Code: TypeAlias = Union['FST', AST, list[str], str]

sentinel = object()


class astfield(NamedTuple):
    name: str
    idx:  int | None = None

    def get(self, node: AST) -> Any:
        return getattr(node, self.name) if self.idx is None else getattr(node, self.name)[self.idx]

    def set(self, node: AST, child: AST):
        if self.idx is None:
            setattr(node, self.name, child)
        else:
            getattr(node, self.name)[self.idx] = child


class fstloc(NamedTuple):
    ln:      int
    col:     int
    end_ln:  int
    end_col: int


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


def _with_loc(a: AST) -> bool:
    """Faster overall than checking `a.f.loc`."""

    return not (isinstance(a, (expr_context, boolop, operator, unaryop, cmpop)) or
                (isinstance(a, arguments) and not a.posonlyargs and not a.args and not a.vararg and not a.kwonlyargs
                 and not a.kwarg))


def _next_src(lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
              comment: bool = False, lcont: bool = False) -> srcwpos | None:
    """Get next source code which may or may not include comments or line continuation backslashes. Assuming start pos
    not inside str or comment. Code is not necessarily AST stuff, it can be commas, colons, the 'try' keyword, etc...
    Code can include multiple AST nodes in return str if there are no spaces between them like 'a+b'."""

    re_pat = (
        (re_next_src_or_comment_or_lcont if comment else re_next_src_or_lcont)
        if lcont else
        (re_next_src_or_comment if comment else re_next_src)
    )

    if end_ln == ln:
        return srcwpos(ln, m.start(1), m.group(1)) if (m := re_pat.match(lines[ln], col, end_col)) else None

    for i in range(ln, end_ln):
        if m := re_pat.match(lines[i], col):
            return srcwpos(i, m.start(1), m.group(1))

        col = 0

    if m := re_pat.match(lines[end_ln], 0, end_col):
        return srcwpos(end_ln, m.start(1), m.group(1))

    return None


def _next_src_lline(lines: list[str], ln: int, col: int, end_ln: int, end_col: int, comment: bool = False
                    ) -> srcwpos | None:
    """Same rules as `_next_src()` but do not exceed logical line during search (even if bounds exceed lline)."""

    re_pat = re_next_src_or_comment if comment else re_next_src

    if end_ln == ln:
        return srcwpos(ln, m.start(1), m.group(1)) if (m := re_pat.match(lines[ln], col, end_col)) else None

    for i in range(ln, end_ln):
        if not (m := re_next_src_or_comment_or_lcont.match(lines[i], col)):
            return None

        if (s := m.group(1)).startswith('#'):
            return srcwpos(i, m.start(1), s) if comment else None

        if not s.startswith('\\'):
            return srcwpos(i, m.start(1), s)

        col = 0

    if m := re_pat.match(lines[end_ln], 0, end_col):
        return srcwpos(end_ln, m.start(1), m.group(1))

    return None


def _prev_src(lines: list[str], ln: int, col: int, end_ln: int, end_col: int,
              comment: bool = False, lcont: bool = False) -> srcwpos | None:
    """Same rules as `_next_src()` but return the LAST occurance of code or maybe comment in the span."""

    re_pat = (
        (re_next_src_or_comment_or_lcont if comment else re_next_src_or_lcont)
        if lcont else
        (re_next_src_or_comment if comment else re_next_src)
    )

    def last_match(l, c, ec):
        ret = None

        while m := re_pat.match(l, c, ec):
            if l[(c := (ret := m).end(1)) : c + 1] in '#\\':
                break

        return ret

    if end_ln == ln:
        return srcwpos(ln, m.start(1), m.group(1)) if (m := last_match(lines[ln], col, end_col)) else None

    for i in range(end_ln, ln, -1):
        if m := last_match(lines[i], 0, end_col):
            return srcwpos(i, m.start(1), m.group(1))

        end_col = 0x7fffffffffffffff

    if m := last_match(lines[ln], col, end_col):
        return srcwpos(ln, m.start(1), m.group(1))

    return None


def _expr_src_edit_locs(lines: list[str], loc: fstloc, bound: fstloc) -> tuple[fstloc, fstloc, list[str]]:
    """Get expression copy and delete locations. There can be commas in the bound in which case the expression is
    treated as part of a comma delimited sequence. In this case, if there is a trailing comma within bounding span then
    it is included in the delete location. Any enclosing grouping parentheses within the bounding span are included.

    **Parameters:**
    - `lines`: The lines corresponding to the expression and its `bound` location.
    - `loc`: The location of the expression, can be multiple or no expressions, just the location matters.
    - `bound`: The bounding location not to go outside of. Must entirely contain `loc` (can be same as). Must not
        contain any part of other `AST` nodes like other members of a sequence.

    **Returns:**
    - `(copy_loc, del_loc, put_lines)`: The `copy_loc` is the location of source that should be used if copying the
        expression. The `del_loc` is the location which should be deleted used if removing the expression. Both are used
        for a cut operation. `put_lines` is an optional set of non-coding source (or `None`) which can be put to
        `del_loc` for prettier foramtting.
    """

    start_ln, start_col, stop_ln,      stop_col      = loc
    bound_ln, bound_col, bound_end_ln, bound_end_col = bound

    precomma_del_col = None

    # start locations

    while True:
        if not (code := _prev_src(lines, bound_ln, bound_col, start_ln, start_col, True, True)):
            if bound_ln != start_ln:
                copy_ln  = del_ln  = bound_ln
                copy_col = del_col = len(lines[bound_ln])

            else:
                copy_ln  = del_ln  = start_ln
                copy_col = del_col = start_col

            break

        ln, col, src = code

        if src.startswith('#'):
            copy_ln  = ln
            copy_col = len(lines[ln])
            del_ln   = ln + 1
            del_col  = 0

            break

        if src == '\\':  # TODO: handle these better if possible
            copy_ln  = del_ln  = ln
            copy_col = del_col = len(lines[ln])

            break

        code_col  = col
        col      += len(src)

        for c in src[::-1]:
            col = col - 1

            if done := (c != '('):  # we don't actually count and check these because there may be other parens inside the `loc` which we can not see here
                if ln != start_ln:
                    copy_ln  = del_ln  = bound_ln
                    copy_col = del_col = len(lines[bound_ln])

                else:
                    copy_ln  = del_ln  = start_ln
                    copy_col = del_col = start_col

                    if c == ',':  # if comma found on same line as start then if previous ends on same line then maybe delete up to it depending on later end conditions
                        if col != code_col:
                            precomma_del_col = col

                        elif code := _prev_src(lines, bound_ln, bound_col, start_ln, col):
                            if code.ln == start_ln:
                                precomma_del_col = code.ln + len(code.src)

                        elif bound_ln == start_ln:
                            precomma_del_col = bound_col

                break

            else:
                start_ln  = ln
                start_col = col

        if done:
            break

    # end locations

    done       = False
    have_comma = False
    cur_ln     = stop_ln
    cur_col    = stop_col

    while True:
        if not (code := _next_src(lines, cur_ln, cur_col, bound_end_ln, bound_end_col, True, False)):
            ln  = bound_end_ln
            col = bound_end_col

            break

        ln, col, src = code

        if src.startswith('#'):
            if ln == stop_ln:  # we only grab the comment on our own ending line
                stop_ln  = ln + 1
                stop_col = 0

            col += len(src)

        else:
            for c in src:
                col = col + 1

                if c == ')':
                    stop_ln  = ln
                    stop_col = col

                elif c == ',':
                    if have_comma:
                        raise ValueError('multiple commas found')

                    have_comma = True
                    stop_ln    = ln
                    stop_col   = col

                else:
                    done  = True
                    col  -= 1

                    break

            if done:
                break

        cur_ln  = ln
        cur_col = col

    if ln != stop_ln:
        if stop_ln == loc.end_ln:  # because of weird comma positioning
            del_end_ln  = stop_ln
            del_end_col = len(lines[del_end_ln])

        else:
            del_end_ln  = ln
            del_end_col = 0

        copy_end_ln  = ln
        copy_end_col = 0

    elif not stop_col:  # copy ends on end of line
        del_end_ln   = ln
        del_end_col  = 0
        copy_end_ln  = stop_ln
        copy_end_col = stop_col

    else:  # copy ends in line, not on end of line
        del_end_ln  = ln
        del_end_col = col

        if ln == loc.end_ln:  # does it end on same line as expression?
            copy_end_ln  = ln
            copy_end_col = loc.end_col

        else:
            copy_end_ln  = stop_ln
            copy_end_col = stop_col

    if precomma_del_col is not None:  # if this true we know copy and del starts on same line as a preceding comma
        if not have_comma:  # at end of potential sequence, strip preceding comma
            del_col = precomma_del_col
        elif del_end_col == len(lines[del_end_ln]):  # delete ends on newline, adjust del start to strip trailing whitespace from comma
            del_col = precomma_del_col + 1

    if not del_col and del_end_col and (m := re_empty_line_start.match(lines[del_ln])).end():  # delete from start of line to middle of line, maybe there is indentation to apply for prettification
        put_lines = [bistr(m.group())]
    else:
        put_lines = None

    return (fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col),
            fstloc(del_ln, del_col, del_end_ln, del_end_col),
            put_lines)


def _fixup_field_body(ast: AST, field: str | None = None) -> tuple[str, 'AST']:
    if field is None:
        field = AST_DEFAULT_BODY_FIELD.get(ast.__class__, 'body')

    if (body := getattr(ast, field, sentinel)) is sentinel:
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


def _fixup_bound(seq_loc: fstloc, fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None]) -> fstloc | None:
    if fpre:
        if fpost:
            return fstloc(fpre.end_ln, fpre.end_col, fpost.ln, fpost.col)
        else:
            return fstloc(fpre.end_ln, fpre.end_col, seq_loc.end_ln, seq_loc.end_col)

    elif fpost:
        return fstloc(seq_loc.ln, seq_loc.col, fpost.ln, fpost.col)
    else:
        return None  # no fpre or fpost, inform that entire seq_loc


def _normalize_code(code: Code, expr_: bool = False, *, parse_params: dict = {}) -> 'FST':
    """Normalize code to an `FST`. If an expression is required then will return an `FST` with a top level `ast.expr`
    `AST` node if possible, raise otherwise. If expression is not required then will convert to `ast.Module` if is
    `ast.Interactive` or return single expression node of `ast.Expression` or just return whatever the node currently
    is."""

    def reduce(ast):
        if isinstance(ast, Expression):
            ast = ast.body

        elif expr_:
            if isinstance(ast, (Module, Interactive)):
                if len(body := ast.body) != 1 or not isinstance(ast := body[0], Expr):
                    raise ValueError(f'expecting single expression')

                ast = ast.value

            if not isinstance(ast, expr):
                raise ValueError(f'expecting expression')

        elif isinstance(ast, Interactive):
            ast = Module(body=ast.body, type_ignores=[])

        return ast

    if isinstance(code, FST):
        if not code.is_root:
            raise ValueError('expecting root FST')

        ast  = code.a
        rast = reduce(ast)

        return code if rast is ast else FST(rast, lines=code._lines, from_=code)

    if isinstance(code, AST):
        return FST.fromast(reduce(code))

    if isinstance(code, str):
        src   = code
        lines = code.split('\n')

    else:  # isinstance(code, list):
        src   = '\n'.join(code)
        lines = code

    ast = ast_parse(src, mode='eval', **parse_params).body if expr_ else ast_parse(src, **parse_params)

    return FST(ast, lines=lines)


def _new_empty_tuple() -> 'FST':
    ast                = Tuple(elts=[], ctx=Load())
    fst                = FST(ast, lines=[bistr('()')])
    ast.lineno         = ast.end_lineno = 1
    ast.col_offset     = 0
    ast.end_col_offset = 2

    return fst


def _new_empty_list() -> 'FST':
    ast                = List(elts=[], ctx=Load())
    fst                = FST(ast, lines=[bistr('[]')])
    ast.lineno         = ast.end_lineno = 1
    ast.col_offset     = 0
    ast.end_col_offset = 2

    return fst


def _new_empty_dict() -> 'FST':
    ast                = Dict(keys=[], values=[])
    fst                = FST(ast, lines=[bistr('{}')])
    ast.lineno         = ast.end_lineno = 1
    ast.col_offset     = 0
    ast.end_col_offset = 2

    return fst


def _new_empty_set_curlies() -> 'FST':
    ast                = Set(elts=[])
    fst                = FST(ast, lines=[bistr('{}')])
    ast.lineno         = ast.end_lineno = 1
    ast.col_offset     = 0
    ast.end_col_offset = 2

    return fst


def _new_empty_set_call(ast_only: bool = False, lineno: int = 1, col_offset: int = 0) -> 'FST':
    ast                     = Call(func=Name(id='set', ctx=Load()), args=[], keywords=[])
    ast.lineno              = ast.end_lineno = lineno
    ast.col_offset          = col_offset
    ast.end_col_offset      = col_offset + 5
    ast.func.lineno         = ast.func.end_lineno = lineno
    ast.func.col_offset     = col_offset
    ast.func.end_col_offset = col_offset + 3

    return ast if ast_only else FST(ast, lines=[bistr('set()')])


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

        if idx.step is not None:
            raise ValueError('step slicing not supported')

        self.owner.put_slice(code, idx.start, idx.stop, self.field)

    def append(self, code: Code):
        self.owner.put(code, self.start + len(self.asts), field=self.field)

    def extend(self, code: Code):
        self.owner.put_slice(code, (end := self.start + len(self.asts)), end, self.field)

    def copy(self, *, fix: bool = True, decos: bool = True) -> 'FST':
        return self.owner.get_slice(start := self.start, start + len(self.asts), self.field,
                                    fix=fix, cut=False, decos=decos)

    def cut(self, *, fix: bool = True, decos: bool = True) -> 'FST':
        return self.owner.get_slice(start := self.start, start + len(self.asts), self.field,
                                    fix=fix, cut=True, decos=decos)


class FSTSrcEdit:
    """Source editing formatter."""

    def get_seq(self, fst: 'FST', cut: bool, seq_loc: fstloc,
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
        - `fpost`: The after-last `FST` or `fstloc` being gotten, may not exist if `flast` is last of seq.

        **Returns:**
        - If `cut=False` then should return tuple with only the first value set, which is a location where to copy
        source from for the new slice, with the second two being `None`. If `cut=True` then should return the copy
        location, a delete location and optionally lines to replace the deleted portion (which can only be non-coding
        source).
        """

        if not (bound := _fixup_bound(seq_loc, fpre, fpost)):
            return seq_loc, seq_loc, None

        copy_loc, put_loc, put_lines = _expr_src_edit_locs(fst.root._lines,
                                                           fstloc(ffirst.ln, ffirst.col, flast.end_ln, flast.end_col),
                                                           bound)

        return (copy_loc, put_loc, put_lines) if cut else (copy_loc, None, None)

    def put_seq(self, fst: 'FST', put_fst: Optional['FST'], indent: str, seq_loc: fstloc,
                ffirst: Union['FST', fstloc, None], flast: Union['FST', fstloc, None],
                fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                pfirst: Union['FST', fstloc, None], plast: Union['FST', fstloc, None],
    ) -> fstloc:  # put_loc
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
        - `indent`: The indent string which was already applied to `put_fst`.
        - `seq_loc`: The full location of the sequence in `fst`, excluding parentheses / brackets / curlies.
        - `ffirst`: The first destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `flast`: The last destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `fpre`: The preceding-first destination `FST` or `fstloc`, not being replaced, may not exist if `ffirst` is
            first of seq.
        - `fpost`: The after-last destination `FST` or `fstloc` being replaced, may not exist if `flast` is last of seq.
        - `pfirst`: The first source `FST`, else `None` if is assignment from empty sequence (deletion).
        - `plast`: The last source `FST`, else `None` if is assignment from empty sequence (deletion).

        **Returns:**
        - `fstloc` location where the potentially modified `fst` source should be put, replacing whatever is at the
            location currently.
        """

        if not put_fst or not pfirst:  # `pfirst` may be None and `new` not if assigning empty sequence, pure delete (assign empty sequence)
            if not (bound := _fixup_bound(seq_loc, fpre, fpost)):
                return seq_loc

            return _expr_src_edit_locs(fst.root._lines,
                                       fstloc(ffirst.ln, ffirst.col, flast.end_ln, flast.end_col), bound)[1]

        if ffirst:  # flast also exists, replacement
            return fstloc(ffirst.ln, ffirst.col, flast.end_ln, flast.end_col)

        if not fpre and not fpost:  # ffirst and flast are None, assign to empty sequence, just copy over whole inside
            return seq_loc



        # TODO: insertion to non-empty sequence



        raise NotImplementedError
        return fstloc(ffirst.ln, ffirst.col, flast.end_ln, flast.end_col)


class FST:
    """Preserve AST formatting information and easy manipulation."""

    a:            AST                       ; """The actual `AST` node."""
    parent:       Optional['FST']           ; """Parent `FST` node, `None` in root node."""
    pfield:       astfield | None           ; """The `astfield` location of this node in the parent, `None` in root node."""
    root:         'FST'                     ; """The root node of this tree, `self` in root node."""
    _loc:         fstloc | None             # cache, MAY NOT EXIST!
    _bloc:        fstloc | None             # cache, MAY NOT EXIST! bounding location, including preceding decorators

    # ROOT ONLY
    parse_params: dict[str, Any]            ; """The parameters to use for any `ast.parse()` that needs to be done (filename, type_comments, feature_version), root node only."""
    indent:       str                       ; """The default single level of block indentation string for this tree when not available from context, root node only."""
    docstring:    bool | Literal['strict']  ; """The default docstring indent / dedent behavior. `True` means allow indent of all `Expr` multiline strings, `False` means don't indent any of them and `'strict'` allows for indenting multiline strings at standard docstring locations only."""
    _lines:       list[bistr]

    @property
    def is_root(self) -> bool:
        """`True` for the root node, `False` otherwise."""

        return self.parent is None

    @property
    def parent_stmt(self) -> Optional['FST']:
        """The first parent which is a `stmt` or `mod` node (if any)."""

        while (self := self.parent) and not isinstance(self, (stmt, mod)):
            pass

        return self

    @property
    def parent_stmtish(self) -> Optional['FST']:
        """The first parent which is a `stmt`, `ExceptHandler`, `match_case` or `mod` node (if any)."""

        while (self := self.parent) and not isinstance(self, STATEMENTISH_OR_MOD):
            pass

        return self

    @property
    def parent_block(self) -> Optional['FST']:
        """The first parent which opens a block that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `For`, `AsyncFor`, `While`, `If`, `With`, `AsyncWith`, `Match`, `Try`,
        `TryStar`, `ExceptHandler`, `match_case`, and `mod`."""

        while (self := self.parent) and not isinstance(self, BLOCK_OR_MOD):
            pass
        return self

    @property
    def parent_scope(self) -> Optional['FST']:
        """The first parent which opens a scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef`, `Lambda`, `ListComp`, `SetComp`, `DictComp`, `GeneratorExp`, and `mod`."""

        while (self := self.parent) and not isinstance(self, SCOPE_OR_MOD):
            pass

        return self

    @property
    def parent_named_scope(self) -> Optional['FST']:
        """The first parent which opens a named scope that `self` lives in (if any). Types include `FunctionDef`,
        `AsyncFunctionDef`, `ClassDef` and `mod`."""

        while (self := self.parent) and not isinstance(self, NAMED_SCOPE_OR_MOD):
            pass

        return self

    @property
    def lines(self) -> list[str] | None:
        """Whole lines which contain this node, may also contain parts of enclosing nodes. All source lines at root."""

        if self.is_root:
            return self._lines
        elif loc := self.loc:
            return self.root._lines[loc.ln : loc.end_ln + 1]
        else:
            return None

    @property
    def src(self) -> str | None:
        """Source code of this node clipped out of `lines` as a single string, without any dedentation. Whole source
        at root."""

        if self.is_root:
            return '\n'.join(self._lines)
        elif loc := self.loc:
            return '\n'.join(self.get_lines(*loc))
        else:
            return None

    @property
    def loc(self) -> fstloc | None:
        """Zero based character indexed location of node (may not be entire location if node has decorators). Not all
        nodes have locations, specifically leaf nodes like operations and `expr_context`. Other nodes which normally
        don't have locations like `arguments` have this location calculated from their children."""

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
            elif first := self.first_child():
                loc = fstloc(first.bln, first.bcol, (last := self.last_child()).bend_ln, last.bend_col)
            else:
                loc = None

        else:
            col     = self.root._lines[ln].b2c(col_offset)
            end_col = self.root._lines[end_ln].b2c(end_col_offset)
            loc     = fstloc(ln, col, end_ln, end_col)

        self._loc = loc

        return loc

    @property
    def bloc(self) -> fstloc:
        """Entire location of node, including any preceding decorators. Not all nodes have locations, but any node which
        has a `.loc` will have a `.bloc`."""

        try:
            return self._bloc
        except AttributeError:
            pass

        if not (loc := self.loc):
            bloc = None
        elif not (decos := getattr(self.a, 'decorator_list', None)):
            bloc = loc
        else:
            bloc = fstloc(decos[0].f.ln, loc[1], loc[2], loc[3])  # column of deco '@' will be same as our column

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

    bcol     = col
    bend_ln  = end_ln
    bend_col = end_col  # maybe will eventually include trailing comments

    @property
    def lineno(self) -> int:  # 1 based
        """Line number of the first line of this node (1 based)."""

        return (loc := self.loc) and loc[0] + 1

    @property
    def col_offset(self) -> int:  # byte index
        """BYTE index of the start of this node (0 based)."""

        return (loc := self.loc) and self.root._lines[loc[0]].c2b(loc[1])

    @property
    def end_lineno(self) -> int:  # 1 based
        """Line number of the LAST LINE of this node (1 based)."""

        return (loc := self.loc) and loc[2] + 1

    @property
    def end_col_offset(self) -> int:  # byte index
        """CHARACTER index one past the end of this node (0 based)."""

        return (loc := self.loc) and self.root._lines[loc[2]].c2b(loc[3])

    @property
    def f(self):
        """@private"""

        raise RuntimeError("you probably think you're accessing an AST node, but you're not, you're accessing an FST node")

    src_edit: FSTSrcEdit = FSTSrcEdit()  ; """@private"""

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
        """Destroy a tree of FST nodes by breaking links. Call only on root."""

        if stack is None:
            stack = [self.a]

        while stack:  # make sure these bad ASTs can't hurt us anymore
            a   = stack.pop()
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

        tail = ' ROOT' if self.is_root else ''

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

            if full or (child != []):
                linefunc(f'{sind}{cind}.{name}{f"[{len(child)}]" if is_list else ""}')

            if is_list:
                for i, ast in enumerate(child):
                    if isinstance(ast, AST):
                        ast.f._dump(full, indent, cind + ' ' * indent, f'{i}] ', linefunc, compact)
                    else:
                        linefunc(f'{sind}{cind}{i}] {ast!r}')

            elif isinstance(child, AST):
                child.f._dump(full, indent, cind + sind * 2, '', linefunc, compact)
            else:
                linefunc(f'{sind}{sind}{cind}{child!r}')

    def _dict_key_or_mock_loc(self, key: AST | None, value: 'FST') -> Union['FST', fstloc]:
        """Return same dictionary key FST if exists else create and return a location for the preceding '**' code."""

        if key:
            return key.f

        if idx := value.pfield.idx:
            f   = value.parent.values[idx - 1]  # because of multiline strings, could be a fake comment start inside one which hides a valid **
            ln  = f.end_ln
            col = f.end_col

        else:
            ln  = self.ln
            col = self.ln

        ln, col, s = _prev_src(self.root._lines, ln, col, value.ln, value.col)
        end_col    = col + len(s)

        assert s.endswith('**')

        return fstloc(ln, end_col - 2, ln, end_col)

    def _maybe_add_singleton_tuple_comma(self, offset: bool = True):
        """Maybe add comma to singleton tuple if not already there, parenthesization not checked or taken into account.
        `self` must be a tuple.

        **Parameters:**
        - `offset`: If `True` then will apply `offset()` to entire tree for new comma. If `False` then will just offset
            the end of the Tuple, use this when sure tuple is at top level.
        """

        # assert isinstance(self.a, Tuple)

        if (elts := self.a.elts) and len(elts) == 1:
            felt  = elts[0].f
            root  = self.root
            lines = root._lines

            if (not (code := _next_src(lines, felt.end_ln, felt.end_col, self.end_ln, self.end_col)) or
                not code.src.startswith(',')
            ):
                lines[ln] = bistr(f'{(l := lines[(ln := felt.end_ln)])[:(col := felt.end_col)]},{l[col:]}')

                if offset:
                    self.root.offset(ln, col, 0, 1, True, self)

                elif ln == self.end_ln:
                    self.a.end_col_offset += 1

                    self.touchall(True, False, True)

    def _maybe_fix_tuple(self, is_parenthesized: bool | None = None):
        # assert isinstance(self.a, Tuple)

        if self.a.elts:
            self._maybe_add_singleton_tuple_comma(True)

        elif not (self.is_tuple_parenthesized() if is_parenthesized is None else is_parenthesized):  # if is unparenthesized tuple and empty left then need to add parentheses
            self.put_lines([bistr('()')], *self.loc, True)  # TODO: WARNING! `True` may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized tuple starts, does this ever happen?

    def _maybe_fix_set(self):
        # assert isinstance(self.a, Set)

        if not self.a.elts:
            ln, col, end_ln, end_col = self.loc

            self.put_lines([bistr('set()')], ln, col, end_ln, end_col, True)

            self.a = ast = _new_empty_set_call(True, ln + 1, self.root.lines[ln].c2b(col))
            ast.f  = self

            if parent := self.parent:
                self.pfield.set(parent.a, ast)

                self._make_fst_tree([FST(ast.func, self, astfield('func'))])

    def _make_fst_and_dedent(self, findent: 'FST', ast: AST, copy_loc: fstloc, prefix: str = '', suffix: str = '',
                             put_loc: fstloc | None = None, put_lines: list[str] | None = None) -> 'FST':
        indent = findent.get_indent()
        lines  = self.root._lines
        fst    = FST(ast, lines=lines, from_=self)  # we use original lines for nodes offset calc before putting new lines

        fst.offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix) - lines[copy_loc.ln].c2b(copy_loc.col))  # WARNING! `prefix` is expected to have only 1 byte characters

        fst._lines = fst_lines = self.get_lines(*copy_loc)

        if suffix:
            fst_lines[-1] = bistr(fst_lines[-1] + suffix)

        if prefix:
            fst_lines[0] = bistr(prefix + fst_lines[0])

        if put_loc:
            self.put_lines(put_lines, *put_loc, True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0

        fst.dedent_lns(indent)

        return fst

    def _get_seq_and_dedent(self, get_ast: AST, cut: bool, seq_loc: fstloc,
                            ffirst: Union['FST', fstloc], flast: Union['FST', fstloc],
                            fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                            prefix: str, suffix: str) -> 'FST':

        copy_loc, put_loc, put_lines = self.src_edit.get_seq(self, cut, seq_loc, ffirst, flast, fpre, fpost)

        copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

        lines                  = self.root._lines
        get_ast.lineno         = copy_ln + 1
        get_ast.col_offset     = lines[copy_ln].c2b(copy_col)
        get_ast.end_lineno     = copy_end_ln + 1
        get_ast.end_col_offset = lines[copy_end_ln].c2b(copy_end_col)

        put_fst = self._make_fst_and_dedent(self, get_ast, copy_loc, prefix, suffix, put_loc, put_lines)

        get_ast.col_offset     = 0  # before prefix
        get_ast.end_col_offset = put_fst._lines[-1].lenbytes  # after suffix

        get_ast.f.touch()

        return put_fst

    def _get_slice_stmt(self, start: int, stop: int, field: str | None, fix: bool, cut: bool) -> 'FST':



        if cut: raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!



        get_ast     = self.a
        field, body = _fixup_field_body(get_ast, field)
        start, stop = _fixup_slice_index(get_ast, body, field, start, stop)

        if start == stop:
            return FST(Module(body=[]), lines=[bistr('')], from_=self)

        afirst = body[start]
        loc    = fstloc((f := afirst.f).ln, f.col, (l := body[stop - 1].f.loc).end_ln, l.end_col)
        newast = Module(body=[copy_ast(body[i]) for i in range(start, stop)])

        if (fix and field == 'orelse' and not start and (stop - start) == 1 and
            afirst.col_offset == get_ast.col_offset and isinstance(get_ast, If) and isinstance(afirst, If)
        ):  # 'elif' -> 'if'
            newast.body[0].col_offset += 2
            loc                        = fstloc(loc.ln, loc.col + 2, loc.end_ln, loc.end_col)

        fst = self._make_fst_and_dedent(afirst.f, newast, loc)

        return fst

    def _get_slice_tuple_list_or_set(self, start: int, stop: int, field: str | None, fix: bool, cut: bool) -> 'FST':
        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to slice from a {self.a.__class__.__name__}")

        ast         = self.a
        elts        = ast.elts
        is_set      = isinstance(ast, Set)
        is_tuple    = not is_set and isinstance(ast, Tuple)
        ctx         = None if is_set else Load() if fix else ast.ctx.__class__()
        start, stop = _fixup_slice_index(ast, elts, 'elts', start, stop)

        if start == stop:
            if is_set:
                return _new_empty_set_call()
            elif is_tuple:
                return _new_empty_tuple()
            else:
                return _new_empty_list()

        is_paren = is_tuple and self.is_tuple_parenthesized()
        ffirst   = elts[start].f
        flast    = elts[stop - 1].f
        fpre     = elts[start - 1].f if start else None
        fpost    = None if stop == len(elts) else elts[stop].f

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
            get_ast = ast.__class__(elts=asts, ctx=ctx)

            if fix and not isinstance(ast.ctx, Load):
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

        if is_tuple:
            fst._maybe_add_singleton_tuple_comma(False)  # maybe need to add a postfix comma to copied single element tuple if is not already there
            self._maybe_fix_tuple(is_paren)

        return fst

    def _get_slice_dict(self, start: int, stop: int, field: str | None, fix: bool, cut: bool) -> 'FST':
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to slice from a Dict")

        ast         = self.a
        values      = ast.values
        start, stop = _fixup_slice_index(ast, values, 'values', start, stop)

        if start == stop:
            return _new_empty_dict()

        keys   = ast.keys
        ffirst = self._dict_key_or_mock_loc(keys[start], values[start].f)
        flast  = values[stop - 1].f
        fpre   = values[start - 1].f if start else None
        fpost  = None if stop == len(keys) else self._dict_key_or_mock_loc(keys[stop], values[stop].f)

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

    def _put_seq_and_indent(self, put_fst: Optional['FST'], seq_loc: fstloc,
                            ffirst: Union['FST', fstloc, None], flast: Union['FST', fstloc, None],
                            fpre: Union['FST', fstloc, None], fpost: Union['FST', fstloc, None],
                            pfirst: Union['FST', fstloc, None], plast: Union['FST', fstloc, None]) -> 'FST':
        root = self.root

        if not put_fst:  # delete
            put_lines = None

            put_ln, put_col, put_end_ln, put_end_col = (
                self.src_edit.put_seq(self, None, '', seq_loc, ffirst, flast, fpre, fpost, None, None))

        else:
            assert put_fst.is_root

            indent = self.get_indent()

            put_fst.indent_lns(indent)

            put_ln, put_col, put_end_ln, put_end_col = (
                self.src_edit.put_seq(self, put_fst, indent, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast))

            lines           = root._lines
            put_lines       = put_fst._lines
            fst_dcol_offset = lines[put_ln].c2b(put_col)

            put_fst.offset(0, 0, put_ln, fst_dcol_offset)

        if fpost:
            root.put_lines(put_lines, put_ln, put_col, put_end_ln, put_end_col, False, None)
        else:
            root.put_lines(put_lines, put_ln, put_col, put_end_ln, put_end_col, True, self)  # because of insertion at end and unparenthesized tuple

    def _put_slice_tuple_list_or_set(self, code: Code | None, start: int, stop: int, field: str | None = None):
        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to assign slice to a {self.a.__class__.__name__}")

        if code is None:
            put_fst = None

        else:
            put_fst = _normalize_code(code, expr_=True, parse_params=self.root.parse_params)

            if put_fst.is_empty_set_call():
                put_fst = _new_empty_set_curlies()

            put_ast = put_fst.a

            if (not (is_tuple := isinstance(put_ast, Tuple)) and not (is_set := isinstance(put_ast, Set)) and not
                isinstance(put_ast, List)
            ):
                raise ValueError(f"slice being assigned to a {self.a.__class__.__name__} must be a Tuple, List or Set, "
                                 f"not a '{put_ast.__class__.__name__}'")

        ast         = self.a
        elts        = ast.elts
        start, stop = _fixup_slice_index(ast, elts, 'elts', start, stop)
        slice_len   = stop - start

        if not slice_len and (not put_fst or not put_fst.elts):  # deleting or assigning empty seq to empty slice of seq, noop
            return

        is_self_tuple    = isinstance(ast, Tuple)
        is_self_enclosed = not is_self_tuple or self.is_tuple_parenthesized()
        fpre             = elts[start - 1].f if start else None
        fpost            = None if stop == len(elts) else elts[stop].f
        seq_loc          = fstloc(self.ln, self.col + is_self_enclosed, self.end_ln, self.end_col - is_self_enclosed)

        if not slice_len:
            ffirst = flast = None

        else:
            ffirst = elts[start].f
            flast  = elts[stop - 1].f

        if not put_fst:
            self._put_seq_and_indent(None, seq_loc, ffirst, flast, fpre, fpost, None, None)
            self._unmake_fst_tree(elts[start : stop])

            del elts[start : stop]

            put_len = 0

        else:
            put_lines = put_fst._lines

            if not is_tuple:
                put_ast.end_col_offset -= 1  # strip enclosing curlies or brackets from source set or list

                put_fst.offset(0, 1, 0, -1)

                assert put_lines[0].startswith('[{'[is_set])
                assert put_lines[-1].endswith(']}'[is_set])

                put_lines[-1] = bistr(put_lines[-1][:-1])
                put_lines[0]  = bistr(put_lines[0][1:])

            elif put_fst.is_tuple_parenthesized():
                put_ast.end_col_offset -= 1  # strip enclosing parentheses from source tuple

                put_fst.offset(0, 1, 0, -1)

                put_lines[-1] = bistr(put_lines[-1][:-1])
                put_lines[0]  = bistr(put_lines[0][1:])

            if not (selts := put_ast.elts):
                pfirst = plast = None

            else:
                pfirst = selts[0].f
                plast  = selts[-1].f

            self._put_seq_and_indent(put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast)
            self._unmake_fst_tree(elts[start : stop], put_fst)

            elts[start : stop] = put_ast.elts
            put_len            = len(put_ast.elts)
            stack              = [FST(elts[i], self, astfield('elts', i)) for i in range(start, start + put_len)]

            self._make_fst_tree(stack)

        for i in range(start + put_len, len(elts)):
            elts[i].f.pfield = astfield('elts', i)

        if is_self_tuple:
            self._maybe_fix_tuple(is_self_enclosed)
        elif isinstance(ast, Set):
            self._maybe_fix_set()

    def _put_slice_dict(self, code: Code | None, start: int, stop: int, field: str | None = None):
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

        if code is None:
            put_fst = None

        else:
            put_fst = _normalize_code(code, expr_=True, parse_params=self.root.parse_params)
            put_ast = put_fst.a

            if not isinstance(put_ast, Dict):
                raise ValueError(f"slice being assigned to a Dict must be a Dict, not a '{put_ast.__class__.__name__}'")

        ast         = self.a
        values      = ast.values
        start, stop = _fixup_slice_index(ast, values, 'values', start, stop)
        slice_len   = stop - start

        if not slice_len and (not put_fst or not put_fst.keys):  # deleting or assigning empty dict to empty slice of dict, noop
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
            self._put_seq_and_indent(None, seq_loc, ffirst, flast, fpre, fpost, None, None)
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
                pfirst = skeys[0].f
                plast  = put_ast.values[-1].f

            self._put_seq_and_indent(put_fst, seq_loc, ffirst, flast, fpre, fpost, pfirst, plast)
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
        if child := getattr(self.a, name):
            if isinstance(child, list):
                return fstlistproxy(child, self, name)
            elif isinstance(child, AST):
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
        lines       = root_params.get('lines') or [bistr('')]
        self._lines = lines if lines[0].__class__ is bistr else [bistr(s) for s in lines]

        if from_ := root_params.get('from_'):  # copy params from source tree
            from_root         = from_.root
            self.parse_params = root_params.get('parse_params', from_root.parse_params)
            self.indent       = root_params.get('indent', from_root.indent)
            self.docstring    = root_params.get('docstring', from_root.docstring)

        else:
            self.parse_params = root_params.get('parse_params', DEFAULT_PARSE_PARAMS)
            self.indent       = root_params.get('indent', DEFAULT_INDENT)
            self.docstring    = root_params.get('docstring', DEFAULT_DOCSTRING)

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
        - `AST`: The parsed tree with `.f` attributes added to each `AST` node for `FST` access.
        """

        parse_params = dict(parse_params, filename=filename, type_comments=type_comments,
                            feature_version=feature_version)

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
        - `AST`: The parsed tree with `.f` attributes added to each `AST` node for `FST` access.
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
        otherwise there will almost certaionly be problems!

        **Parameters:**
        - `ast`: The root `AST` node.
        - `filename`: `ast.parse()` parameter.
        - `mode`: `ast.parse()` parameter. Can be `exec`, `eval, `single` or `None`, in which case the appropriate mode
            is determined from the structure of the tree itself.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.
        - `calc_loc`: Get actual node positions by unparsing then parsing again. Use when you are not certain node
            positions are correct or even present. Updates original ast unless set to "copy", in which case a copied
            `AST` is used. Set to `False` when you know positions are correct and want to use given `AST`. Default True.

        **Returns:**
        - `AST`: The parsed tree with `.f` attributes added to each `AST` node for `FST` access.
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

    def verify(self, *, raise_: bool = True) -> Optional['FST']:  # -> Self | None:
        """Sanity check, make sure source text matches ast (locations and everything).

        **Parameters:**
        - `raise_`: Whether to raise an exception on verify failed or return `None`.

        **Returns:**
        - `None` on failure to verify, otherwise `self`.
        """

        root         = self.root
        ast          = root.a
        parse_params = root.parse_params

        try:
            astp = ast_parse(root.src, mode=get_parse_mode(ast), **parse_params)

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

    def dump(self, full: bool = False, indent: int = 2, linefunc: Callable = print, compact: bool = False
             ) -> list[str] | None:
        """Dump a representation of the tree to stdout or return as a list of lines."""

        if linefunc is print:
            return self._dump(full, indent, linefunc=print, compact=compact)

        if linefunc in (str, list):
            lines = []

            self._dump(full, indent, linefunc=lines.append, compact=compact)

            return lines if linefunc is list else '\n'.join(lines)

        self._dump(full, indent, linefunc=linefunc, compact=compact)

    # ------------------------------------------------------------------------------------------------------------------

    def copy(self, *, fix: bool = True, decos: bool = True) -> 'FST':
        newast = copy_ast(self.a)

        if self.is_root:
            return FST(newast, lines=self._lines[:], from_=self)

        if not (loc := self.bloc if decos else self.loc):
            raise ValueError('cannot copy node which does not have location')

        if not decos and hasattr(newast, 'decorator_list'):
            newast.decorator_list.clear()

        fst = self._make_fst_and_dedent(self, newast, loc)

        return fst.fix(inplace=True) if fix else fst

    def cut(self, *, fix: bool = True, decos: bool = True) -> 'FST':
        if self.is_root:
            raise ValueError('cannot cut root node')

        parent     = self.parent
        field, idx = self.pfield
        parenta    = parent.a

        if isinstance(parenta, STATEMENTISH_OR_STMTMOD):
            raise NotImplementedError

        if isinstance(parenta, (Tuple, List, Set)):
            fst = self.copy(fix=fix, decos=decos)

            parent._put_slice_tuple_list_or_set(None, idx, idx + 1, field)

            return fst

        raise ValueError(f"cannot cut a '{parenta.__class__.__name__}'")




    def get(self, start: int | str | None = None, stop: int | str | None | Literal[False] = False,
            field: str | None = None, *, fix: bool = True, decos: bool = True, cut: bool = False) -> Optional['FST']:

        if isinstance(start, str):
            raise NotImplementedError

        if stop is not False:
            if not isinstance(stop, str):
                return self.get_slice(start, stop, field, fix=fix, cut=cut)

            if field is not None:
                raise ValueError('cannot specify two field values')

            field = stop

        field, body = _fixup_field_body(self.a, field)

        if cut:
            return body[start].f.cut(fix=fix, decos=decos)
        else:
            return body[start].f.copy(fix=fix, decos=decos)




    def put(self, code: Code | None, start: int | None = None, stop: int | None | Literal['False'] = False,
            field: str | None = None) -> Optional['FST']:  # -> Self:

        if stop is not False:
            return self.put_slice(code, start, stop, field)

        field, body = _fixup_field_body(self.a, field)

        raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!




    def get_slice(self, start: int | None = None, stop: int | None = None, field: str | None = None, *,
                  fix: bool = True, cut: bool = False) -> 'FST':
        a = self.a

        if isinstance(a, STATEMENTISH_OR_STMTMOD):
            return self._get_slice_stmt(start, stop, field, fix, cut)

        if isinstance(a, (Tuple, List, Set)):
            return self._get_slice_tuple_list_or_set(start, stop, field, fix, cut)

        if isinstance(a, Dict):
            return self._get_slice_dict(start, stop, field, fix, cut)

        raise ValueError(f"cannot get slice from a '{a.__class__.__name__}'")






    def put_slice(self, code: Code | None, start: int | None = None, stop: int | None = None, field: str | None = None):
        a = self.a

        if isinstance(a, STATEMENTISH_OR_STMTMOD):
            raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!

        if isinstance(a, (Tuple, List, Set)):
            return self._put_slice_tuple_list_or_set(code, start, stop, field)

        if isinstance(a, Dict):
            return self._put_slice_dict(code, start, stop, field)

        raise ValueError(f"cannot put slice to a '{a.__class__.__name__}'")






    def get_lines(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        if end_ln == ln:
            return [bistr(self.root._lines[ln][col : end_col])]
        else:
            return [bistr((ls := self.root._lines)[ln][col:])] + ls[ln + 1 : end_ln] + [bistr(ls[end_ln][:end_col])]

    def put_lines(self, lines: list[str] | None, ln: int, col: int, end_ln: int, end_col: int,
                  inc: bool | None = None, stop_at: Optional['FST'] = None):
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
        return '\n'.join(self.get_lines(ln, col, end_ln, end_col))

    def put_src(self, src: str | None, ln: int, col: int, end_ln: int, end_col: int,
                inc: bool = False, stop_at: Optional['FST'] = None):
        self.put_lines(None if src is None else src.split('\n'), ln, col, end_ln, end_col, inc, stop_at)

    def fix(self, inplace: bool = True) -> Optional['FST']:  # -> Self | None
        """This is really a maybe fix source and `ctx` values for cut or copied nodes (to make subtrees parsable if the
        source is not after the operation). Possibly reparses in order to verify expression. If can not fix or ast is
        not parsable by itself then ast will be unchanged. Is meant to be a quick fix after an operation, not full
        check, for that use `verify()`. Possible source changes are `elif` to `if` and parentheses where needed and
        commas for singleton tuples.

        **Parameters:**
        - `inplace`: If `True` then changes will be made to `self`. If `False` then `self` may be returned if no changes
            made, otherwise a modified copy is returned.

        **Returns:**
        - `self` if unchanged or modified in place or a new `FST` object otherwise.
        """

        if not self.is_root:
            raise RuntimeError('can only be called on a root node')

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
                if self.is_tuple_parenthesized():
                    need_paren = False

                elif (not (elts := ast.elts) or any(isinstance(e, NamedExpr) for e in elts) or (len(elts) == 1 and (
                      not (code := _next_src_lline(lines, (f0 := elts[0].f).end_ln, f0.end_col, end_ln, end_col)) or  # if comma not on logical line then definitely need to add parens, if no comma then the parens are incidental but we want that code path for adding the comma
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
                    tail = (',)' if is_tuple and len(ast.elts) == 1 and lines[end_ln][end_col - 1] != ',' else ')')  # TODO: WARNING! this won't work for expressions followed by comments

                    a = ast_parse(f'({src}{tail}', mode='eval', **self.parse_params)

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




# ------------------------------------------------------------------------------------------------------------------

    def next(self, with_loc: bool = True) -> Optional['FST']:  # TODO: refactor
        """Get next sibling in syntactic order.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, otherwise all nodes.

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

                    if not with_loc or _with_loc(a):  # a.f.loc:
                        return a.f

            elif idx is not None:
                sibling = getattr(aparent, name)

                while True:
                    try:
                        if not (a := sibling[(idx := idx + 1)]):  # who knows where a `None` might pop up "next" these days... xD
                            continue

                    except IndexError:
                        break

                    if not with_loc or _with_loc(a):  # a.f.loc:
                        return a.f

            while next is not None:
                if isinstance(next, str):
                    name = next

                    if isinstance(sibling := getattr(aparent, next, None), AST):  # None because we know about fields from future python versions
                        if not with_loc or _with_loc(sibling):  # sibling.f.loc:
                            return sibling.f

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

    def prev(self, with_loc: bool = True) -> Optional['FST']:  # TODO: refactor
        """Get previous sibling in syntactic order.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, otherwise all nodes.

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

                    if not with_loc or _with_loc(a):  # a.f.loc:
                        return a.f

            else:
                sibling = getattr(aparent, name)

                while idx:
                    if not (a := sibling[(idx := idx - 1)]):
                        continue

                    if not with_loc or _with_loc(a):  # a.f.loc:
                        return a.f

            while prev is not None:
                if isinstance(prev, str):
                    name = prev

                    if isinstance(sibling := getattr(aparent, prev, None), AST):  # None because could have fields from future python versions
                        if not with_loc or _with_loc(sibling):  # sibling.f.loc:
                            return sibling.f

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

    def first_child(self, with_loc: bool = True) -> Optional['FST']:
        """Get first valid child in syntactic order.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, otherwise all nodes.

        **Returns:**
        - `None` if no valid children, otherwise first valid child.
        """

        for name in AST_FIELDS[(a := self.a).__class__]:
            if (child := getattr(a, name, None)):
                if isinstance(child, AST):
                    if not with_loc or _with_loc(child):  # child.f.loc:
                        return child.f

                elif isinstance(child, list):
                    # if (c := child[0]) and ((f := c.f).loc or not with_loc):
                    if (c := child[0]) and (not with_loc or _with_loc(c)):  # c.f.loc):
                        return c.f

                    return FST(Load(), self, astfield(name, 0)).next(with_loc)  # Load() is a hack just to have a simple AST node

        return None

    def last_child(self, with_loc: bool = True) -> Optional['FST']:
        """Get last valid child in syntactic order.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, otherwise all nodes.

        **Returns:**
        - `None` if no valid children, otherwise last valid child.
        """

        if (isinstance(a := self.a, Call)) and a.args and (keywords := a.keywords) and isinstance(a.args[-1], Starred):  # super-special case Call with args and keywords and a Starred, it could be anywhere in there, including after last keyword, defer to prev() logic
            fst          = FST(f := Load(), self, astfield('keywords', len(keywords)))
            f.lineno     = 0x7fffffffffffffff
            f.col_offset = 0

            return fst.prev(with_loc)

        for name in reversed(AST_FIELDS[(a := self.a).__class__]):
            if (child := getattr(a, name, None)):
                if isinstance(child, AST):
                    if not with_loc or _with_loc(child):  # child.f.loc:
                        return child.f

                elif isinstance(child, list):
                    if (c := child[-1]) and (not with_loc or _with_loc(c)):  # c.f.loc):
                        return c.f

                    return FST(Load(), self, astfield(name, len(child) - 1)).prev(with_loc)  # Load() is a hack just to have a simple AST node

        return None

    def next_child(self, from_child: Optional['FST'], with_loc: bool = True) -> Optional['FST']:
        """Get next child in syntactic order. Meant for simple iteration. This is a slower way to iterate, `walk()` is
        faster.

        **Parameters:**
        - `from_child`: Child node we are coming from which may or may not have location.
        - `with_loc`: If `True` then only nodes with locations returned, otherwise all nodes.

        **Returns:**
        - `None` if last valid child in `self`, otherwise next child node.
        """

        return self.first_child(with_loc) if from_child is None else from_child.next(with_loc)

    def prev_child(self, from_child: Optional['FST'], with_loc: bool = True) -> Optional['FST']:
        """Get previous child in syntactic order. Meant for simple iteration. This is a slower way to iterate, `walk()`
        is faster.

        **Parameters:**
        - `from_child`: Child node we are coming from which may or may not have location.
        - `with_loc`: If `True` then only nodes with locations returned, otherwise all nodes.

        **Returns:**
        - `None` if first valid child in `self`, otherwise previous child node.
        """

        return self.last_child(with_loc) if from_child is None else from_child.prev(with_loc)

    def walk(self, with_loc: bool = False, *, walk_self: bool = True, recurse: bool = True, scope: bool = False,
             back: bool = False) -> Generator['FST', bool, None]:
        """Walk self and descendants in syntactic order, `send(False)` to skip recursion into child. `send(True)` to
        allow recursion into child if called with `recurse=False` or `scope=True` would otherwise disallow it. Can send
        multiple times, last value sent takes effect.

        **Parameters:**
        - `with_loc`: If `True` then only nodes with locations returned, otherwise all nodes.
        - `walk_self`: If `True` then self will be returned first with the possibility to skip children with `send()`.
        - `recurse`: Whether to recurse into children by default, `send()` for a given node will always override this.
            Will always attempt first level of children unless walking self and `False` is sent first.
        - `scope`: If `True` then will walk only within the scope of `self`. Meaning if called on a `FunctionDef` then
            will only walk children which are within the function scope. Will yield children which have with their own
            scopes, and the parts of them which are visible in this scope (like default argument values), but will not
            recurse into them unless `send(True)` is done for that child.
        - `back`: If `True` then walk every node in reverse syntactic order. This is not the same as a full forwards
            walk reversed due to recursion.

        **Example:**
        ```py
        for node in (gen := target.walk()):
            ...
            if i_dont_like_the_node:
                gen.send(False)  # skip walking this node's children, don't use return value here, keep using for loop as normal
        ```
        """

        if walk_self:
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

            if with_loc and not _with_loc(fst.a):  # not fst.loc:
                continue

            recurse_ = recurse

            while (sent := (yield fst)) is not None:
                recurse_ = 1 if sent else False

            if recurse_ is not True:
                if recurse_:  # user did send(True), walk this child unconditionally
                    yield from fst.walk(with_loc, walk_self=False, back=back)

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
                        gen             = fst.walk(with_loc, walk_self=False, back=back)

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

    def is_tuple_parenthesized(self) -> bool:
        # assert isinstance(self.a, Tuple)

        return (self.root._lines[(ln := self.ln)].startswith('(', col := self.col) and
                (not (e := self.a.elts) or (ln != (f0 := e[0].f).ln or col != f0.col)))

    def is_empty_set_call(self) -> bool:
        return (isinstance(ast := self.a, Call) and not ast.args and not ast.keywords and
                isinstance(func := ast.func, Name) and func.id == 'set' and isinstance(func.ctx, Load))

    def get_indent(self) -> str:
        """Determine proper indentation of node at `stmt` (or other similar) level at or above self. Even if it is a
        continuation or on same line as block statement.

        **Returns:**
        - `str`: Entire indentation string for the block this node lives in (not just one level).
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

    def get_indentable_lns(self, skip: int = 0, *, docstring: bool | Literal['strict'] | None = None) -> set[int]:
        """Get set of indentable lines within this node.

        **Parameters:**
        - `skip`: The number of lines to skip from the start of this node. Useful for skipping the first line for edit
            operations (since the first line is normally joined to an existing line on add or copied directly from start
            on cut).
        - `docstring`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all
            `Expr` multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline
            strings in expected docstring positions are indentable.

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

        if docstring is None:
            docstring = self.root.docstring

        strict = docstring == 'strict'
        lines  = self.root.lines
        lns    = set(range(self.bln + skip, self.bend_ln + 1))

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
            self = parent

        for f in (gen := self.walk(False)):  # find multiline strings and exclude their unindentable lines
            if f.bend_ln == f.bln:  # everything on one line, don't need to recurse
                gen.send(False)

            elif isinstance(a := f.a, Constant):
                if (  # isinstance(f.a.value, (str, bytes)) is a given if bend_ln != bln
                    not docstring or
                    not ((parent := f.parent) and isinstance(parent.a, Expr) and
                         (not strict or ((pparent := parent.parent) and parent.pfield == ('body', 0) and
                                         isinstance(pparent.a, HAS_DOCSTRING)
                )))):
                    multiline_str(f)

            elif isinstance(a, JoinedStr):
                multiline_fstr(f)

                gen.send(False)  # skip everything inside regardless, because it is evil

        return lns

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
        colo = self.root._lines[ln].c2b(col)

        for f in (gen := self.walk(False)):
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
                    gen.send(False)  # no need to walk into something whose bounding block ends before offset point

                    continue

                if flno > lno:
                    if not dln and (not (decos := getattr(a, 'decorator_lis', None)) or decos[0].lineno > lno):
                        gen.send(False)  # no need to walk into something past offet point if line change is 0

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
                gen.send(False)

            f.touch()

        self.touchall(True, False, False)

        return self

    def offset_cols(self, dcol_offset: int, lns: set[int]):
        """Offset ast col byte offsets in `lns` by a delta and return same set of indentable lines.

        Only modifies ast, not lines.
        """

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
        """Offset ast col byte offsets by a specific delta per line and return same dict of indentable lines.

        Only modifies ast, not lines.
        """

        for a in walk(self.a):
            if (end_col_offset := getattr(a, 'end_col_offset', None)) is not None:
                if (dcol_offset := dcol_offsets.get(a.lineno - 1)) is not None:
                    a.col_offset += dcol_offset

                if (dcol_offset := dcol_offsets.get(a.end_lineno - 1)) is not None:
                    a.end_col_offset = end_col_offset + dcol_offset

            a.f.touch()

        self.touchall(True, False, False)

    def indent_lns(self, indent: str | None = None, lns: set[int] | None = None, *,
                   docstring: bool | Literal['strict'] | None = None) -> set[int]:
        """Indent all indentable lines past the first one according with `indent` and adjust node locations accordingly.
        Does not modify node columns on first line.

        **Parameters:**
        - `indent`: The indentation string to prefix to each indentable line.
        - `lns`: A `set` of lines to apply identation to. If `None` then will be gotten from `get_indentable_lns()`.
        - `docstring`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all
            `Expr` multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline
            strings in expected docstring positions are indentable.

        **Returns:**
        - `set[int]`: `lns` passed in or otherwise set of line numbers (zero based) which are sytactically indentable.
        """

        root = self.root

        if indent is None:
            indent = root.indent
        if docstring is None:
            docstring = root.docstring

        if not ((lns := self.get_indentable_lns(1, docstring=docstring)) if lns is None else lns) or not indent:
            return lns

        self.offset_cols(len(indent.encode()), lns)

        lines = root._lines

        for ln in lns:
            if l := lines[ln]:  # only indent non-empty lines
                lines[ln] = bistr(indent + l)

        self.reparse_docstrings(docstring)

        return lns

    def dedent_lns(self, indent: str | None = None, lns: set[int] | None = None, *,
                   docstring: bool | Literal['strict'] | None = None) -> set[int]:
        """Dedent all indentable lines past the first one by removing `indent` prefix and adjust node locations
        accordingly. Does not modify columns on first line. If cannot dedent entire amount will dedent as much as
        possible.

        **Parameters:**
        - `indent`: The indentation string to remove from the beginning of each indentable line (if possible).
        - `lns`: A `set` of lines to apply dedentation to. If `None` then will be gotten from `get_indentable_lns()`.
        - `docstring`: How to treat multiline string docstring lines. `False` means not indentable, `True` means all
            `Expr` multiline strings are indentable (as they serve no coding purpose). `'strict'` means only multiline
            strings in expected docstring positions are indentable.

        **Returns:**
        - `set[int]`: `lns` passed in or otherwise set of line numbers (zero based) which are sytactically indentable.
        """

        root = self.root

        if indent is None:
            indent = root.indent
        if docstring is None:
            docstring = root.docstring

        if not ((lns := self.get_indentable_lns(1, docstring=docstring)) if lns is None else lns) or not indent:
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

        self.reparse_docstrings(docstring)

        return lns

    def reparse_docstrings(self, docstring: bool | Literal['strict'] | None = None):
        """Reparse docstrings in self and all descendants."""

        if docstring is None:
            docstring = self.root.docstring

        if not docstring:
            return

        if docstring != 'strict':  # True
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
