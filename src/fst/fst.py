import re
from ast import *
from ast import parse as ast_parse, unparse as ast_unparse
from typing import Any, Callable, Generator, Literal, NamedTuple, Optional, TypeAlias, Union

from .util import *

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

STATEMENTISH            = (stmt, ExceptHandler, match_case)  # always in lists, cannot be inside multilines
STATEMENTISH_OR_STMTMOD = (stmt, ExceptHandler, match_case, Module, Interactive)
HAS_DOCSTRING           = (FunctionDef, AsyncFunctionDef, ClassDef, Module)

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
        self.owner.put_slice(code, self.start + len(self.asts), field=self.field)

    def copy(self, *, fix: bool = True) -> 'FST':
        return self.owner.get_slice(start := self.start, start + len(self.asts), self.field, fix=fix, cut=False)

    def cut(self, *, fix: bool = True) -> 'FST':
        return self.owner.get_slice(start := self.start, start + len(self.asts), self.field, fix=fix, cut=True)


def parse(source, filename='<unknown>', mode='exec', *, type_comments=False, feature_version=None, **kwargs):
    """Executes `ast.parse()` and then adds `FST` nodes to the parsed tree. Drop-in replacement for `ast.parse()`. For
    parameters, see `ast.parse()`."""

    return FST.fromsrc(source, filename, mode, type_comments=type_comments, feature_version=feature_version, **kwargs).a


def unparse(ast_obj):
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


def _expr_src_edit_locs(lines: list[str], loc: fstloc, bound: fstloc) -> tuple[fstloc, fstloc]:
    """Get expression copy and delete locations. There can be commas in the bound in which case the expression is
    treated as part of a comma delimited sequence. In this case, if there is a trailing comma within bounding span then
    it is included in the delete location. Any enclosing grouping parentheses within the bounding span are included.

    **Parameters:**
    - `lines`: The lines corresponding to the expression and its `bound` location.
    - `loc`: The location of the expression, can be multiple or no expressions, just the location matters.
    - `bound`: The bounding location not to go outside of. Must entirely contain `loc` (can be same as). Must not
        contain any part of other `AST` nodes like other members of a sequence.

    **Returns:**
    - `(copy_loc, del_loc)`: The `copy_loc` is the location of source that should be used if copying the expression.
        The `del_loc` is the location which should be used if removing the expression. Both are used for a cut
        operation.
    """

    start_ln, start_col, stop_ln,      stop_col      = loc
    bound_ln, bound_col, bound_end_ln, bound_end_col = bound

    nparens          = 0
    precomma_del_col = None

    # start locations

    while True:
        if not (code := _prev_src(lines, bound_ln, bound_col, start_ln, start_col, True, True)):
            if bound_ln != start_ln:
                copy_ln  = bound_ln
                copy_col = len(lines[bound_ln])
                del_ln   = bound_ln + 1
                del_col  = 0

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
            if (ln := ln + 1) == start_ln:
                copy_ln  = del_ln  = start_ln
                copy_col = del_col = start_col

            else:
                copy_ln  = ln
                copy_col = len(lines[ln])
                del_ln   = ln + 1
                del_col  = 0

            break

        code_col  = col
        col      += len(src)

        for c in src[::-1]:
            col = col - 1

            if done := (c != '('):
                if ln != start_ln:
                    copy_ln  = bound_ln
                    copy_col = len(lines[bound_ln])
                    del_ln   = bound_ln + 1
                    del_col  = 0

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
                start_ln   = ln
                start_col  = col
                nparens   += 1

        if done:
            break

    # end locations

    have_comma = False
    cur_ln     = stop_ln
    cur_col    = stop_col

    while True:
        done = False

        if not (code := _next_src(lines, cur_ln, cur_col, bound_end_ln, bound_end_col, True, False)):
            if nparens > 0:  # != 0
                raise ValueError('unclosed parenthesis found')

            done         = True
            ln           = bound_end_ln
            col          = bound_end_col
            copy_end_ln  = stop_ln
            copy_end_col = stop_col

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
                    # if is sequence then opening parens may be inside of location so we don't check for this
                    # if not nparens:
                    #     raise ValueError('unmatched closing parenthesis found')

                    nparens  = nparens - 1
                    stop_ln  = ln
                    stop_col = col

                elif c == ',':
                    if have_comma:
                        raise ValueError('multiple commas found')

                    have_comma = True
                    stop_ln    = ln
                    stop_col   = col

                else:
                    if nparens > 0:  # != 0
                        raise ValueError('unclosed parenthesis found')

                    done          = True
                    col          -= 1
                    copy_end_ln   = stop_ln
                    copy_end_col  = stop_col

                    break

            if done:
                break

        cur_ln  = ln
        cur_col = col

    if done:  # can also come from reaching end of bound or next source
        if ln != stop_ln:
            del_end_ln  = stop_ln
            del_end_col = len(lines[del_end_ln])

        elif not stop_col:  # copy ends on end of line
            del_end_ln  = ln
            del_end_col = 0

        else:  # copy ends in line, not on end of line
            del_end_ln  = ln
            del_end_col = col

            if ln == loc.end_ln:  # does it end on same line as expression?
                copy_end_ln  = ln
                copy_end_col = loc.end_col

    if precomma_del_col is not None:  # if this true we know copy and del starts on same line as a preceding comma
        if not have_comma:  # at end of potential sequence, strip preceding comma
            del_col = precomma_del_col
        elif del_end_col == len(lines[del_end_ln]):  # delete ends on newline, adjust del start to strip trailing whitespace from comma
            del_col = precomma_del_col + 1

    return fstloc(copy_ln, copy_col, copy_end_ln, copy_end_col), fstloc(del_ln, del_col, del_end_ln, del_end_col)


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


def _fixup_bound(seq_loc: fstloc, lpre: Union['FST', fstloc, None], lpost: Union['FST', fstloc, None]) -> fstloc | None:
    if lpre:
        if lpost:
            return fstloc(lpre.end_ln, lpre.end_col, lpost.ln, lpost.col)
        else:
            return fstloc(lpre.end_ln, lpre.end_col, seq_loc.end_ln, seq_loc.end_col)

    elif lpost:
        return fstloc(seq_loc.ln, seq_loc.col, lpost.ln, lpost.col)
    else:
        return None


def _normalize_code(code: Code, expr_: bool = False) -> 'FST':
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

        rast = reduce(ast := code.a)

        return code if rast is ast else FST(rast, lines=code._lines, from_=code)

    if isinstance(code, AST):
        return FST.fromast(reduce(code))

    if isinstance(code, str):
        src   = code
        lines = code.split('\n')

    else:  # isinstance(code, list):
        src   = '\n'.join(code)
        lines = code

    ast = ast_parse(src, mode='eval').body if expr_ else ast_parse(src)

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


def _new_empty_set_call() -> 'FST':
    ast                     = Call(func=Name(id='set', ctx=Load()), args=[], keywords=[])
    fst                     = FST(ast, lines=[bistr('set()')])
    ast.lineno              = ast.end_lineno      = 1
    ast.col_offset          = 0
    ast.end_col_offset      = 5
    ast.func.lineno         = ast.func.end_lineno = 1
    ast.func.col_offset     = 0
    ast.func.end_col_offset = 3

    return fst


def _new_empty_set_curlies() -> 'FST':
    ast                = Set(elts=[])
    fst                = FST(ast, lines=[bistr('{}')])
    ast.lineno         = ast.end_lineno = 1
    ast.col_offset     = 0
    ast.end_col_offset = 2

    return fst


class FSTSrcEdit:
    """Source operation formatter."""

    def get_seq(self, src: 'FST', cut: bool, seq_loc: fstloc,
                lfirst: Union['FST', fstloc], llast: Union['FST', fstloc],
                lpre: Union['FST', fstloc, None], lpost: Union['FST', fstloc, None],
    ) -> tuple[fstloc, fstloc | None, list[str] | None]:  # (copy_loc, del/put_loc, put_lines)
        """Copy or cut from comma delimited sequence.

        The `lfirst`, `llast`, `lpre` and `lpost` parameters are only meant to pass location information so you should
        only count on their respective `.ln`, `.col`, `.end_ln` and `.end_col` being correct (within `src`).

        **Parameters:**
        - `src`: The source `FST` container that is being gotten from. No text has been changed at this point but the
            respective `AST` nodes may have been removed if case of `cut`.
        - `cut`: If `False` the operation is a copy, `True` means cut.
        - `seq_loc`: The full location of the sequence in `src`, excluding parentheses / brackets / curlies.
        - `lfirst`: The first `FST` or `fstloc` being gotten.
        - `llast`: The last `FST` or `fstloc` being gotten.
        - `lpre`: The preceding-first `FST` or `fstloc`, not being gotten, may not exist if `lfirst` is first of seq.
        - `lpost`: The after-last `FST` or `fstloc` being gotten, may not exist if `llast` is last of seq.

        **Returns:**
        - If `cut=False` then should return tuple with only the first value set, which is a location where to copy
        source from for the new slice, with the second two being `None`. If `cut=True` then should return the copy
        location, a delete location and optionally lines to replace the deleted portion (which can only be non-coding
        source).
        """

        if not (bound := _fixup_bound(seq_loc, lpre, lpost)):
            return seq_loc, seq_loc, None

        copy_loc, del_loc = _expr_src_edit_locs(src.root._lines,
                                                fstloc(lfirst.ln, lfirst.col, llast.end_ln, llast.end_col), bound)

        return copy_loc, del_loc, None

    def put_seq(self, dst: 'FST', fst: 'FST', indent: str, seq_loc: fstloc,
                lfirst: Union['FST', fstloc, None], llast: Union['FST', fstloc, None],
                lpre: Union['FST', fstloc, None], lpost: Union['FST', fstloc, None],
                sfirst: Union['FST', fstloc, None], slast: Union['FST', fstloc, None],
    ) -> fstloc:  # put_loc
        """Put to comma delimited sequence.

        The `lfirst`, `llast`, `lpre` and `lpost` parameters are only meant to pass location information so you should
        only count on their respective `.ln`, `.col`, `.end_ln` and `.end_col` being correct (within `src`).

        If `lfirst` and `llast` are `None` it means that it is a pure insertion and no elements are being removed. In
        this case use `lpre` and `lpost` to determine locations, one of which could be missing if the insertion is at
        the beginning or end of the sequence, both of which missing indicates put to empty sequence (in which case use
        `seq_loc` for location).

        The first line of `fst` is unindented and should remain so as it is concatenated with the target line at the
        point of insertion. The last line of `fst` is likewise prefixed to the line following the deleted location.

        There is always an operation if this is called, insertion, deletion, or replacement. It is never an empty
        assignment to an empty slice.

        **Parameters:**
        - `dst`: The destination `FST` container that is being put to.
        - `fst`: The sequence which is being put, guaranteed to have at least one element. Already indented, mutate this
            object to change what will be put (both source and `AST` nodes, node locations must be updated if source is
            changed).
        - `indent`: The indent string which was already applied to `fst`.
        - `seq_loc`: The full location of the sequence in `dst`, excluding parentheses / brackets / curlies.
        - `lfirst`: The first destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `llast`: The last destination `FST` or `fstloc` being replaced (if `None` then nothing being replaced).
        - `lpre`: The preceding-first destination `FST` or `fstloc`, not being replaced, may not exist if `lfirst` is
            first of seq.
        - `lpost`: The after-last destination `FST` or `fstloc` being replaced, may not exist if `llast` is last of seq.
        - `sfirst`: The first source `FST`, else `None` if is assignment from empty sequence (deletion).
        - `slast`: The last source `FST`, else `None` if is assignment from empty sequence (deletion).

        **Returns:**
        - `fstloc` source location where the potentially modified `fst` source should be put, replacing whatever is at
            the location currently.
        """

        if not sfirst:  # slast is also None, pure delete (assign empty sequence)
            if not (bound := _fixup_bound(seq_loc, lpre, lpost)):
                return seq_loc

            return _expr_src_edit_locs(dst.root._lines,
                                       fstloc(lfirst.ln, lfirst.col, llast.end_ln, llast.end_col), bound)[1]

        if lfirst:  # llast also exists, replacement
            return fstloc(lfirst.ln, lfirst.col, llast.end_ln, llast.end_col)

        if not lpre and not lpost:  # lfirst and llast are None, assign to empty sequence, just copy over whole inside
            return seq_loc



        # TODO: insertion to non-empty sequence



        raise NotImplementedError
        return fstloc(lfirst.ln, lfirst.col, llast.end_ln, llast.end_col)










class FST:
    """Preserve AST formatting information and easy manipulation.

    **Class Attributes:**
    - `src_edit`: Controls source edit formatting on copy / cut / put operations. Can also be set on class instances to
        override.

    **Attributes:**
    - `a`: The actual `AST` node.
    - `parent`: Parent `FST` node, `None` in root node.
    - `pfield`: The `astfield` location of this node in the parent, `None` in root node.
    - `root`: The root node of this tree, `self` in root node.
    - `indent`: The default indentation for this tree (not necessarily used everywhere).
    """

    a:             AST
    parent:        Optional['FST']  # None in root node
    pfield:        astfield | None  # None in root node
    root:          'FST'            # self in root node
    _loc:          fstloc | None    # cache, MAY NOT EXIST!
    _bloc:         fstloc | None    # cache, MAY NOT EXIST! bounding location, including preceding decorators

    indent:        str              # ROOT ONLY! default indentation to use when unknown
    _lines:        list[bistr]      # ROOT ONLY!
    _parse_params: dict[str, Any]   # ROOT ONLY!

    @property
    def is_root(self) -> bool:
        return self.parent is None

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
        """Location of node (may not be entire location if node has decorators). Not all nodes have locations."""

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
        """Entire location of node, including any preceding decorators. Not all nodes have locations."""

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
        raise RuntimeError("you probably think you're accessing an AST node, but you're not, you're accessing an FST node")

    src_edit = FSTSrcEdit()

    # ------------------------------------------------------------------------------------------------------------------

    def _make_fst_tree(self, stack: list['FST'] | None = None) -> 'FST':  # -> Self
        """Create tree of FST nodes for each AST node from root. Call only on root."""

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

        return self

    def _repr_tail(self) -> str:
        try:
            loc = self.loc
        except Exception:  # maybe in middle of operation changing locations and lines
            loc = '????'

        self.touchall()  # for debugging because we may have cached locs which would not have otherwise been cached during execution

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

    def _reparse_docstring(self) -> 'FST':  # -> Self
        """`self` must be something that can have a docstring in the body (function, class, module). Node and source
        lines are assumed to be correct, just the docstring value needs to be reset."""

        # assert isistance(self, HAS_DOCSTRING)

        if ((body := self.a.body) and isinstance(b0 := body[0], Expr) and isinstance(v := b0.value, Constant) and
            isinstance(v.value, str)
        ):
            v.value = literal_eval((f := b0.f).get_src(*f.loc))

        return self

    def _reparse_docstrings(self) -> 'FST':  # -> Self
        """Reparse docstrings in self and all descendants."""

        for a in walk(self.a):
            if isinstance(a, HAS_DOCSTRING):
                a.f._reparse_docstring()

    def _offset(self, ln: int, col: int, dln: int, dcol_offset: int, inc: bool = False, stop_at: Optional['FST'] = None
                ) -> 'FST':  # -> Self
        """Offset ast node positions in the tree on or after ln / col by delta line / col_offset (col byte offset).

        This only offsets the positions in the AST nodes, doesn't change any text, so make sure that is correct before
        getting any FST locations from affected nodes otherwise they will be wrong.

        Other nodes outside this tree might need offsetting so use only on root unless special circumstances.

        If offsetting a zero-length node (which can result from deleting elements of an unparenthesized tuple), both the
        start and end location will be moved if exactly at offset point if `inc` is `False`. Otherwise if `inc` is
        `True` then the start position will remain and the end position will be expanded.

        **Parameters:**
        - `ln`: Line of offset point.
        - `col`: Column of offset point (char index).
        - `dln`: Number of lines to offset everything on or after offset point, can be 0.
        - `dcol_offset`: Column offset to apply to everything ON the offset point line `ln` (in bytes). Columns not on
            this line will not be changed.
        - `inc`: Whether to offset endpoint if it falls exactly at ln / col or not (inclusive).

        **Behavior:**
        ```
              offset here:
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
            |
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

                elif fend_lno == lno and (
                        fend_colo >= colo if (inc or (fend_colo == fcolo and fend_lno == flno)) else fend_colo > colo):
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
                        fcolo > colo):
                    a.lineno     += dln
                    a.col_offset += dcol_offset

            if f is stop_at:
                gen.send(False)

            f.touch()

        self.touchup()

        return self

    def _offset_cols(self, dcol_offset: int, lns: set[int]) -> 'FST':  # -> Self
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

            self.touchup()

        return self

    def _offset_cols_mapped(self, dcol_offsets: dict[int, int]) -> 'FST':  # -> Self
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

        self.touchup()

        return self

    def _indentable_lns(self, skip: int = 0, *, docstring: bool = True) -> set[int]:
        """Get set of indentable lines."""

        def walk_multiline(cur_ln, end_ln, m, re_str_end):
            nonlocal lns, lines

            col = m.end(0)

            for ln in range(cur_ln, end_ln + 1):
                if m := re_str_end.match(lines[ln], col):
                    break

                col = 0

            else:
                raise RuntimeError('should not get here')

            lns -= set(range(cur_ln + 1, ln + 1))  # specifically leave out first line of multiline string because that is indentable

            return ln, m.end(0)

        def multiline_str(f: 'FST'):
            nonlocal lns, lines

            cur_ln, cur_col, end_ln, end_col = f.loc

            while True:
                if not (m := re_multiline_str_start.match(l := lines[cur_ln], cur_col)):
                    if m := re_oneline_str.match(l, cur_col):
                        cur_col = m.end(0)

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

        lines = self.root.lines
        lns   = set(range(self.bln + skip, self.bend_ln + 1))

        while (parent := self.parent) and not isinstance(self.a, STATEMENTISH):
            self = parent

        for f in (gen := self.walk(False)):  # find multiline strings and exclude their unindentable lines
            if f.bend_ln == f.bln:  # everything on one line, don't need to recurse
                gen.send(False)

            elif isinstance(a := f.a, Constant):
                if (  # isinstance(f.a.value, (str, bytes)) is a given if bend_ln != bln
                    not docstring or
                    not ((parent := f.parent) and  # not (is_docstring)
                         isinstance(parent.a, Expr) and (pparent := parent.parent) and parent.pfield == ('body', 0) and
                         isinstance(pparent.a, HAS_DOCSTRING)
                )):
                    multiline_str(f)

            elif isinstance(a, JoinedStr):
                multiline_fstr(f)

                gen.send(False)  # skip everything inside regardless, because it is evil

        return lns

    def _indent_tail(self, indent: str, *, docstring: bool = True) -> set[int]:
        """Indent all indentable lines past the first one according with `indent` and adjust node locations accordingly.
        Does not modify node columns on first line."""

        if not (lns := self._indentable_lns(1, docstring=docstring)) or not indent:
            return lns

        self._offset_cols(len(indent.encode()), lns)

        lines = self.root._lines

        for ln in lns:
            if l := lines[ln]:  # only indent non-empty lines
                lines[ln] = bistr(indent + l)

        if docstring:
            self._reparse_docstrings()

        return lns

    def _dedent_tail(self, indent: str, *, docstring: bool = True) -> set[int]:
        """Dedent all indentable lines past the first one by removing `indent` prefix and adjust node locations
        accordingly. Does not modify columns on first line. If cannot dedent entire amount will dedent as much as
        possible.
        """

        if not (lns := self._indentable_lns(1, docstring=docstring)) or not indent:
            return lns

        lines        = self.root._lines
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
            self._offset_cols_mapped(dcol_offsets)
        else:
            self._offset_cols(-lindent, lns)

        if docstring:
            self._reparse_docstrings()

        return lns

    def _maybe_add_singleton_tuple_comma(self, offset: bool = True) -> 'FST':  # -> Self
        """Maybe add comma to singleton tuple if not already there, parenthesization not checked or taken into account.
        `self` must be a tuple.

        **Parameters:**
        - `offset`: If `True` then will apply `_offset()` to entire tree for new comma. If `False` then will just offset
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
                    self.root._offset(ln, col, 0, 1, True, self)

                elif ln == self.end_ln:
                    self.a.end_col_offset += 1

                    self.touchup(True)

        return self

    def _maybe_fix_tuple(self, is_parenthesized: bool | None = None) -> 'FST':  # -> Self
        # assert isinstance(self.a, Tuple)

        if self.a.elts:
            self._maybe_add_singleton_tuple_comma(True)

        elif not (self.is_tuple_parenthesized() if is_parenthesized is None else is_parenthesized):  # if is unparenthesized tuple and empty left then need to add parentheses
            self.put_lines([bistr('()')], *self.loc, True)  # TODO: WARNING! `True` may not be safe if another preceding non-containing node ends EXACTLY where the unparenthesized tuple starts, does this ever happen?

        return self

    def _maybe_fix_set(self) -> 'FST':  # -> Self
        # assert isinstance(self.a, Set)


        raise NotImplementedError


        # if not self.a.elts:
        #     ln, col, end_ln, end_col = self.loc

        #     assert ln == end_ln and col == end_col - 2

        #     root      = self.root
        #     lines     = root.lines
        #     lines[ln] = bistr(f'{(l := lines[ln])[:col]}set(){l[col:]}')

        #     root._offset(ln, col, 0, 5, True)
        #     self.touchup(True)

        return self

    def _make_fst_and_dedent(self, findent: 'FST', ast: AST, copy_loc: fstloc, prefix: str = '', suffix: str = '',
                             put_loc: fstloc | None = None, put_lines: list[str] | None = None) -> 'FST':
        indent = findent.get_indent()
        lines  = self.root._lines
        fst    = FST(ast, lines=lines, from_=self)  # we use original lines for nodes offset calc before putting new lines

        fst._offset(copy_loc.ln, copy_loc.col, -copy_loc.ln, len(prefix) - lines[copy_loc.ln].c2b(copy_loc.col))  # WARNING! `prefix` is expected to have only 1 byte characters

        fst._lines = fst_lines = self.get_lines(*copy_loc)

        if suffix:
            fst_lines[-1] = bistr(fst_lines[-1] + suffix)

        if prefix:
            fst_lines[0] = bistr(prefix + fst_lines[0])

        if put_loc:
            self.root._offset(put_loc.end_ln, put_loc.end_col, put_loc.ln - put_loc.end_ln,
                              lines[put_loc.ln].c2b(put_loc.col) - lines[put_loc.end_ln].c2b(put_loc.end_col), True)  # True because we may have an unparenthesized tuple that shrinks to a span length of 0
            self.put_lines(put_lines, *put_loc)

        fst._dedent_tail(indent)

        return fst

    def _get_seq_and_dedent(self, ast: AST, cut: bool, seq_loc: fstloc,
                            lfirst: Union['FST', fstloc], llast: Union['FST', fstloc],
                            lpre: Union['FST', fstloc, None], lpost: Union['FST', fstloc, None],
                            prefix: str, suffix: str) -> 'FST':

        copy_loc, put_loc, put_lines = self.src_edit.get_seq(self, cut, seq_loc, lfirst, llast, lpre, lpost)

        copy_ln, copy_col, copy_end_ln, copy_end_col = copy_loc

        lines              = self.root._lines
        ast.lineno         = copy_ln + 1
        ast.col_offset     = lines[copy_ln].c2b(copy_col)
        ast.end_lineno     = copy_end_ln + 1
        ast.end_col_offset = lines[copy_end_ln].c2b(copy_end_col)

        fst = self._make_fst_and_dedent(self, ast, copy_loc, prefix, suffix, put_loc, put_lines)

        ast.col_offset     = 0  # before prefix
        ast.end_col_offset = fst._lines[-1].lenbytes  # after suffix

        ast.f.touch()

        return fst

    def _get_slice_stmt(self, start: int, stop: int, field: str | None, fix: bool, cut: bool) -> 'FST':



        if cut: raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!



        ast         = self.a
        field, body = _fixup_field_body(ast, field)
        start, stop = _fixup_slice_index(ast, body, field, start, stop)

        if start == stop:
            return FST(Module(body=[]), lines=[bistr('')], from_=self)

        afirst = body[start]
        loc    = fstloc((f := afirst.f).ln, f.col, (l := body[stop - 1].f.loc).end_ln, l.end_col)
        newast = Module(body=[copy_ast(body[i]) for i in range(start, stop)])

        if (fix and field == 'orelse' and not start and (stop - start) == 1 and afirst.col_offset == ast.col_offset and
            isinstance(ast, If) and isinstance(afirst, If)
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
        lfirst   = elts[start].f
        llast    = elts[stop - 1].f
        lpre     = elts[start - 1].f if start else None
        lpost    = None if stop == len(elts) else elts[stop].f

        if not cut:
            asts = [copy_ast(elts[i]) for i in range(start, stop)]

        else:
            asts = elts[start : stop]

            del elts[start : stop]

            for i in range(start, len(elts)):
                elts[i].f.pfield = astfield('elts', i)

        if is_set:
            newast = Set(elts=asts)  # location will be set later when span is potentially grown
            prefix = '{'
            suffix = '}'

        else:
            newast = ast.__class__(elts=asts, ctx=ctx)

            if fix and not isinstance(ast.ctx, Load):
                set_ctx(newast, Load)

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

        fst = self._get_seq_and_dedent(newast, cut, seq_loc, lfirst, llast, lpre, lpost, prefix, suffix)

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
        lfirst = self._dict_key_or_mock_loc(keys[start], values[start].f)
        llast  = values[stop - 1].f
        lpre   = values[start - 1].f if start else None
        lpost  = None if stop == len(keys) else self._dict_key_or_mock_loc(keys[stop], values[stop].f)

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

        newast  = Dict(keys=akeys, values=avalues)
        seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

        assert self.root._lines[self.ln].startswith('{', self.col)
        assert self.root._lines[seq_loc.end_ln].startswith('}', seq_loc.end_col)

        return self._get_seq_and_dedent(newast, cut, seq_loc, lfirst, llast, lpre, lpost, '{', '}')

    def _put_seq_and_indent(self, fst: 'FST', seq_loc: fstloc,
                            lfirst: Union['FST', fstloc, None], llast: Union['FST', fstloc, None],
                            lpre: Union['FST', fstloc, None], lpost: Union['FST', fstloc, None],
                            sfirst: Union['FST', fstloc, None], slast: Union['FST', fstloc, None]) -> 'FST':
        assert fst.is_root

        indent = self.get_indent()

        fst._indent_tail(indent)

        put_ln, put_col, put_end_ln, put_end_col = (
            self.src_edit.put_seq(self, fst, indent, seq_loc, lfirst, llast, lpre, lpost, sfirst, slast))

        root            = self.root
        lines           = root._lines
        fst_lines       = fst._lines
        fst_dcol_offset = lines[put_ln].c2b(put_col)

        if lpost:
            self.put_lines(fst_lines, put_ln, put_col, put_end_ln, put_end_col, False, None)
        else:
            root.put_lines(fst_lines, put_ln, put_col, put_end_ln, put_end_col, True, self)  # because of insertion at end and unparenthesized tuple

        fst._offset(0, 0, put_ln, fst_dcol_offset)

    def _put_slice_tuple_list_or_set(self, code: Code, start: int, stop: int, field: str | None = None):
        if field is not None and field != 'elts':
            raise ValueError(f"invalid field '{field}' to assign slice to a {self.a.__class__.__name__}")

        newfst = _normalize_code(code, expr_=True)

        if newfst.is_empty_set_call():
            newfst = _new_empty_set_curlies()

        newast = newfst.a

        if (not (is_tuple := isinstance(newast, Tuple)) and not (is_set := isinstance(newast, Set)) and not
            isinstance(newast, List)
        ):
            raise ValueError(f"slice being assigned to a {self.a.__class__.__name__} must be a Tuple, List or Set, not a '{newast.__class__.__name__}'")

        ast         = self.a
        elts        = ast.elts
        start, stop = _fixup_slice_index(ast, elts, 'elts', start, stop)
        dstlen      = stop - start

        if not dstlen and not newfst.elts:  # assigning empty seq to empty slice of seq, noop
            return

        newlines = newfst._lines

        if not is_tuple:
            newast.end_col_offset -= 1  # strip enclosing curlies or brackets from source set or list

            newfst._offset(0, 1, 0, -1)

            assert newlines[0].startswith('[{'[is_set])
            assert newlines[-1].endswith(']}'[is_set])

            newlines[-1] = bistr(newlines[-1][:-1])
            newlines[0]  = bistr(newlines[0][1:])

        elif newfst.is_tuple_parenthesized():
            newast.end_col_offset -= 1  # strip enclosing parentheses from source tuple

            newfst._offset(0, 1, 0, -1)

            newlines[-1] = bistr(newlines[-1][:-1])
            newlines[0]  = bistr(newlines[0][1:])

        is_self_tuple    = isinstance(ast, Tuple)
        is_self_enclosed = not is_self_tuple or self.is_tuple_parenthesized()
        lpre             = elts[start - 1].f if start else None
        lpost            = None if stop == len(elts) else elts[stop].f
        seq_loc          = fstloc(self.ln, self.col + is_self_enclosed, self.end_ln, self.end_col - is_self_enclosed)

        if not dstlen:
            lfirst = llast = None

        else:
            lfirst = elts[start].f
            llast  = elts[stop - 1].f

        if not (selts := newast.elts):
            sfirst = slast = None

        else:
            sfirst = selts[0].f
            slast  = selts[-1].f

        self._put_seq_and_indent(newfst, seq_loc, lfirst, llast, lpre, lpost, sfirst, slast)

        elts[start : stop] = newast.elts
        srclen             = len(newast.elts)
        stack              = [FST(elts[i], self, astfield('values', i)) for i in range(start, start + srclen)]

        for i in range(start + srclen, len(elts)):
            elts[i].f.pfield = astfield('values', i)

        self._make_fst_tree(stack)

        if is_self_tuple:
            self._maybe_fix_tuple(is_self_enclosed)
        elif isinstance(self, Set):
            self._maybe_fix_set()

    def _put_slice_dict(self, code: Code, start: int, stop: int, field: str | None = None):
        if field is not None:
            raise ValueError(f"cannot specify a field '{field}' to assign slice to a Dict")

        newfst = _normalize_code(code, expr_=True)
        newast = newfst.a

        if not isinstance(newast, Dict):
            raise ValueError(f"slice being assigned to a Dict must be a Dict, not a '{newast.__class__.__name__}'")

        ast         = self.a
        values      = ast.values
        start, stop = _fixup_slice_index(ast, values, 'values', start, stop)
        dstlen      = stop - start

        if not dstlen and not newfst.keys:  # assigning empty dict to empty slice of dict, noop
            return

        newlines               = newfst._lines
        newast.end_col_offset -= 1  # strip enclosing curlies from source dict

        newfst._offset(0, 1, 0, -1)

        assert newlines[0].startswith('{')
        assert newlines[-1].endswith('}')

        newlines[-1] = bistr(newlines[-1][:-1])
        newlines[0]  = bistr(newlines[0][1:])

        keys    = ast.keys
        lpre    = values[start - 1].f if start else None
        lpost   = None if stop == len(keys) else self._dict_key_or_mock_loc(keys[stop], values[stop].f)
        seq_loc = fstloc(self.ln, self.col + 1, self.end_ln, self.end_col - 1)

        if not dstlen:
            lfirst = llast = None

        else:
            lfirst = self._dict_key_or_mock_loc(keys[start], values[start].f)
            llast  = values[stop - 1].f

        if not (skeys := newast.keys):
            sfirst = slast = None

        else:
            sfirst = skeys[0].f
            slast  = newast.values[-1].f

        self._put_seq_and_indent(newfst, seq_loc, lfirst, llast, lpre, lpost, sfirst, slast)

        keys[start : stop]   = newast.keys
        values[start : stop] = newast.values
        srclen               = len(newast.keys)
        stack                = []

        for i in range(srclen):
            startplusi = start + i

            stack.append(FST(values[startplusi], self, astfield('values', startplusi)))

            if key := keys[startplusi]:
                stack.append(FST(key, self, astfield('keys', startplusi)))

        for i in range(start + srclen, len(keys)):
            values[i].f.pfield = astfield('values', i)

            if key := keys[i]:  # could be None from **
                key.f.pfield = astfield('keys', i)

        self._make_fst_tree(stack)

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
        lines       = root_params['lines']
        self._lines = lines if lines[0].__class__ is bistr else [bistr(s) for s in lines]

        if from_ := root_params.get('from_'):  # copy params from source tree
            from_root          = from_.root
            self.indent        = root_params.get('indent', from_root.indent)
            self._parse_params = root_params.get('parse_params', from_root._parse_params)

        else:
            self.indent        = root_params.get('indent', '    ')
            self._parse_params = root_params.get('parse_params', {})

        self._make_fst_tree()

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

    @staticmethod
    def fromsrc(source: str | bytes | list[str], filename: str = '<unknown>', mode: str = 'exec', *,
                type_comments: bool = False, feature_version: tuple[int, int] | None = None, **parse_params) -> 'FST':
        if isinstance(source, bytes):
            source = source.decode()

        if isinstance(source, str):
            lines  = source.split('\n')

        else:
            lines  = source
            source = '\n'.join(lines)

        parse_params = dict(parse_params, type_comments=type_comments, feature_version=feature_version)
        ast          = ast_parse(source, filename, mode, **parse_params)

        return FST(ast, lines=[bistr(s) for s in lines], parse_params=parse_params)

    @staticmethod
    def fromast(ast: AST, *, type_comments: bool | None = False, feature_version=None,
                calc_loc: bool | Literal['copy'] = True, **parse_params) -> 'FST':
        """Add `FST` to existing `AST`, optionally copying positions from reparsed `AST` (default) or whole `AST` for
        new `FST`.

        Do not set `calc_loc` to `False` unless you parsed the `AST` from a previous output of `ast.unparse()`,
        otherwise there will almost certaionly be problems!

        **Parameters:**
        - `ast`: The root `AST` node.
        - `calc_loc`: Get actual node positions by unparsing then parsing again. Use when you are not certain node
            positions are correct or even present. Updates original ast unless set to "copy", in which case a copied
            `AST` is used. Set to `False` when you know positions are correct and want to use given `AST`. Default True.
        - `type_comments`: `ast.parse()` parameter.
        - `feature_version`: `ast.parse()` parameter.
        - `parse_params`: Other parameters to `ast.parse()`.
        """

        src   = ast_unparse(ast)
        lines = src.split('\n')

        if type_comments is None:
            type_comments = has_type_comments(ast)

        parse_params = dict(parse_params, type_comments=type_comments, feature_version=feature_version)

        if calc_loc:
            mode = get_parse_mode(ast)
            astp = ast_parse(src, mode=mode, **parse_params)

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
        """Sanity check, make sure parsed source matches ast.

        **Parameters:**
        - `raise_`: Whether to raise an exception on verify failed or return `None`.

        **Returns:**
        - `None` on failure to verify, otherwise `self`.
        """

        root         = self.root
        ast          = root.a
        parse_params = root._parse_params

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

    def dump(self, full: bool = False, indent: int = 2, print: bool = True, compact: bool = False) -> list[str] | None:
        if print:
            return self._dump(full, indent, compact=compact)

        lines = []

        self._dump(full, indent, linefunc=lines.append, compact=compact)

        return lines

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
        assert isinstance(self.a, Tuple)

        return (self.root._lines[(ln := self.ln)].startswith('(', col := self.col) and
                (not (e := self.a.elts) or (ln != (f0 := e[0].f).ln or col != f0.col)))

    def is_empty_set_call(self) -> bool:
        return (isinstance(ast := self.a, Call) and not ast.args and not ast.keywords and
                isinstance(func := ast.func, Name) and func.id == 'set' and isinstance(func.ctx, Load))

    def get_indent(self) -> str:
        """Determine proper indentation of node at `stmt` (or other similar) level at or above self, otherwise at root
        node. Even if it is a continuation or on same line as block statement."""

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

    # ------------------------------------------------------------------------------------------------------------------

    def get_lines(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        if end_ln == ln:
            return [bistr(self.root._lines[ln][col : end_col])]
        else:
            return [bistr((ls := self.root._lines)[ln][col:])] + ls[ln + 1 : end_ln] + [bistr(ls[end_ln][:end_col])]

    def get_src(self, ln: int, col: int, end_ln: int, end_col: int) -> list[str]:
        return '\n'.join(self.get_lines(ln, col, end_ln, end_col))

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

            self.root._offset(end_ln, end_col, dln, dcol_offset, inc, stop_at)

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
                ls[ln + 1 : ln + 1]  = lines[1:] if lines[0].__class__ is bistr else [bistr(l) for l in lines[1:]]
                ls[ln + nnew_ln - 1] = lend

            else:  # replace multiple lines with multiple lines
                ls[ln]              = bistr(ls[ln][:col] + lines[0])
                ls[end_ln]          = bistr(lines[-1] + ls[end_ln][end_col:])
                ls[ln + 1 : end_ln] = lines[1:-1] if lines[0].__class__ is bistr else [bistr(l) for l in lines[1:-1]]

    def put_src(self, src: str | None, ln: int, col: int, end_ln: int, end_col: int,
                inc: bool = False, stop_at: Optional['FST'] = None):
        self.put_lines(None if src is None else src.split('\n'), ln, col, end_ln, end_col, inc, stop_at)

    # ------------------------------------------------------------------------------------------------------------------

    def touch(self) -> 'FST':  # -> Self:
        """AST node was modified, clear out any cached info for this node specifically, call this for each node in a
        walk with modified nodes."""

        try:
            del self._loc, self._bloc  # _bloc only exists if _loc does
        except AttributeError:
            pass

        return self

    def touchup(self, self_: bool = False) -> 'FST':  # -> Self:
        """Touch going up the tree so that all containers of modified nodes are up to date, optinally self as well."""

        if self_:
            self.touch()

        while self := self.parent:
            self.touch()

    def touchall(self, up: bool = True) -> 'FST':  # -> Self:
        """AST node and some/all children were modified, clear out any cached info for tree down from this node, and
        optionally up."""

        for a in walk(self.a):
            a.f.touch()

        if up:
            self.touchup()

        return self

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

            self._offset(ln, col + 2, 0, -2)

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
                    a = ast_parse(src := self.src, mode='eval', **self._parse_params)

                except SyntaxError:  # if expression not parsing then try parenthesize
                    tail = (',)' if is_tuple and len(ast.elts) == 1 and lines[end_ln][end_col - 1] != ',' else ')')  # TODO: WARNING! this won't work for expressions followed by comments

                    a = ast_parse(f'({src}{tail}', mode='eval', **self._parse_params)

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

                self._offset(ln, col, 0, 1)

                if is_tuple:
                    ast.col_offset     -= 1
                    ast.end_col_offset += 1

                self.touch()

                if is_tuple:
                    self._maybe_add_singleton_tuple_comma(False)

        return self

    def copy(self, *, fix: bool = True, decos: bool = True) -> 'FST':
        newast = copy_ast(self.a)

        if self.is_root:
            return FST(newast, lines=self._lines[:], from_=self)

        if not (loc := self.bloc if decos else self.loc):
            raise ValueError('cannot copy ast which does not have location')

        if not decos and hasattr(newast, 'decorator_list'):
            newast.decorator_list.clear()

        fst = self._make_fst_and_dedent(self, newast, loc)

        return fst.fix(inplace=True) if fix else fst

    def cut(self, *, fix: bool = True, decos: bool = True) -> 'FST':
        if self.is_root:
            raise ValueError('cannot cut out root node')

        return self.parent.get((pfield := self.pfield).idx, field=pfield.name, fix=fix, decos=decos)




    def get_slice(self, start: int | None = None, stop: int | None = None, field: str | None = None, *,
                  fix: bool = True, cut: bool = False) -> 'FST':
        if isinstance(self.a, STATEMENTISH_OR_STMTMOD):
            return self._get_slice_stmt(start, stop, field, fix, cut)

        if isinstance(self.a, Expression):
            self = self.a.body.f

        if isinstance(self.a, (Tuple, List, Set)):
            return self._get_slice_tuple_list_or_set(start, stop, field, fix, cut)

        if isinstance(self.a, Dict):
            return self._get_slice_dict(start, stop, field, fix, cut)

        raise ValueError(f"cannot get slice from '{self.a.__class__.__name__}'")






    def put_slice(self, code: Code, start: int | None = None, stop: int | None = None, field: str | None = None,
                  ) -> 'FST':
        if isinstance(self.a, STATEMENTISH_OR_STMTMOD):
            raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!

        if isinstance(self.a, Dict):
            return self._put_slice_dict(code, start, stop, field)

        if isinstance(self.a, (Tuple, List, Set)):
            return self._put_slice_tuple_list_or_set(code, start, stop, field)

        raise ValueError(f"cannot put slice to '{self.a.__class__.__name__}'")





    def get(self, start: int | str | None = None, stop: int | None | Literal[False] = False,
            field: str | None = None, *, fix: bool = True, cut: bool = False, decos: bool = True) -> Optional['FST']:
        raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!

    def put(self, code: Code, start: int | None = None, stop: int | None | Literal['False'] = False,
            field: str | None = None) -> Optional['FST']:  # -> Self:
        raise NotImplementedError  # TODO: THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS! THIS!





