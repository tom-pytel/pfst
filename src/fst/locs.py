"""Functions which compute the locations of various node elements, or entire nodes themselves for those which don't
normally have a location."""

from __future__ import annotations

import re

from . import fst

from .asttypes import (
    AsyncFunctionDef,
    AsyncWith,
    Compare,
    FunctionDef,
    GeneratorExp,
    Global,
    IsNot,
    Lambda,
    NotIn,
    UnaryOp,
    operator,
)

from .astutil import re_identifier, OPCLS2STR, last_block_header_child

from .misc import (
    fstloc, fstlocns,
    BLOCK,
    next_frag, prev_frag, next_find, prev_find, next_delims, prev_delims, next_find_re,
)

__all__ = [
    'loc_arguments',
    'loc_comprehension',
    'loc_withitem',
    'loc_match_case',
    'loc_operator',
    'loc_block_header_end',
    'loc_arguments_empty',
    'loc_Lambda_args_entire',
    'loc_ClassDef_bases_pars',
    'loc_ImportFrom_names_pars',
    'loc_With_items_pars',
    'loc_Call_pars',
    'loc_Subscript_brackets',
    'loc_MatchClass_pars',
    'loc_FunctionDef_type_params_brackets',
    'loc_ClassDef_type_params_brackets',
    'loc_TypeAlias_type_params_brackets',
    'loc_Global_Nonlocal_names',
]


_re_keyword_import     = re.compile(r'\bimport\b')  # we end with a '\b' because we need exactly this word and there may be other similar ones between `from` and `import`
_re_keyword_with_start = re.compile(r'\bwith')  # we do not end with '\b' because the search using this may be checking source where the `with` is joined with a following `withitem` and there are no other words between `async` and `with`


def loc_arguments(self: fst.FST) -> fstloc | None:
    """`arguments` location from children. Called from `.loc`. Returns `None` when there are no arguments.

    **Note:** This function is explicitly safe to use from `FST.loc`.
    """

    # assert isinstance(self.a, arguments)

    if not (first := self.first_child()):
        return None

    ast = self.a
    last = self.last_child()
    lines = self.root._lines
    end_lines = len(lines) - 1
    rpars = next_delims(lines, last.end_ln, last.end_col, *self._next_bound())

    end_ln, end_col = rpars[-1]
    start_ln, start_col, _, _ = first.loc

    if ast.posonlyargs:
        leading_stars = None  # no leading stars
        trailing_slash = False if ast.args or ast.vararg or ast.kwonlyargs or ast.kwarg else True

    else:
        trailing_slash = False

        if ast.args:
            leading_stars = None  # no leading stars
        elif ast.vararg or ast.kwonlyargs:
            leading_stars = '*'  # leading star just before varname or bare leading star with comma following
        elif ast.kwarg:
            leading_stars = '**'  # leading double star just before varname

    if (frag := next_frag(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff)) and frag.src.startswith(','):  # trailing comma
        end_ln, end_col, _ = frag
        end_col += 1

    elif (parent := self.parent) and isinstance(parent.a, (FunctionDef, AsyncFunctionDef)):  # arguments enclosed in pars
        end_ln, end_col = rpars[-2]  # must be there

    if leading_stars:  # find star to the left, we know it exists so we don't check for None return
        start_ln, start_col = prev_find(lines, *self._prev_bound(), start_ln, start_col, leading_stars)

    if trailing_slash:
        end_ln, end_col = next_find(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff, '/')  # must be there
        end_col += 1

        if (frag := next_frag(lines, end_ln, end_col, end_lines, 0x7fffffffffffffff)) and frag.src.startswith(','):  # silly, but, trailing comma trailing slash
            end_ln, end_col, _ = frag
            end_col += 1

    return fstloc(start_ln, start_col, end_ln, end_col)


def loc_comprehension(self: fst.FST) -> fstloc:
    """`comprehension` location from children.

    **Note:** This function is explicitly safe to use from `FST.loc`.
    """

    # assert isinstance(self.a, comprehension)

    ast = self.a
    first = ast.target.f
    last = ifs[-1].f if (ifs := ast.ifs) else ast.iter.f  # self.last_child(), could be .iter or last .ifs
    lines = self.root._lines

    if prev := self.step_back('allown', recurse_self=False):  # 'allown' so it doesn't recurse into calling `.loc`
        _, _, ln, col = prev.loc
    else:
        ln = col = 0

    start_ln, start_col = prev_find(lines, ln, col, first.ln, first.col, 'for')  # must be there

    if ast.is_async:
        start_ln, start_col = prev_find(lines, ln, col, start_ln, start_col, 'async')  # must be there

    rpars = next_delims(lines, last.end_ln, last.end_col, *self._next_bound_step('allown'))

    if (lrpars := len(rpars)) == 1:  # no pars, just use end of last
        end_ln, end_col = rpars[0]

    else:
        is_genexp_last = ((parent := self.parent) and isinstance(parent.a, GeneratorExp) and  # correct for parenthesized GeneratorExp
                          self.pfield.idx == len(parent.a.generators) - 1)

        if is_genexp_last and lrpars == 2:  # can't be pars on left since only par on right was close of GeneratorExp
            end_ln, end_col = rpars[0]
        else:

            end_ln, end_col = rpars[len(prev_delims(lines, *last._prev_bound(), last.ln, last.col)) - 1]  # get rpar according to how many pars on left

    return fstloc(start_ln, start_col, end_ln, end_col)


def loc_withitem(self: fst.FST) -> fstloc:
    """`withitem` location from children.

    **Note:** This function is explicitly safe to use from `FST.loc`.
    """

    # assert isinstance(self.a, withitem)

    ast = self.a
    ce = ast.context_expr.f
    lines = self.root._lines

    ce_ln, ce_col, ce_end_ln, ce_end_col = ce_loc = ce.loc

    if not (ov := ast.optional_vars):
        rpars = next_delims(lines, ce_end_ln, ce_end_col, *self._next_bound_step('allown'))  # 'allown' so it doesn't recurse into calling `.loc`

        if (lrpars := len(rpars)) == 1:
            return ce_loc

        lpars = prev_delims(lines, *self._prev_bound_step('allown'), ce_ln, ce_col)
        npars = min(lrpars, len(lpars)) - 1

        return fstloc(*lpars[npars], *rpars[npars])

    ov_ln, ov_col, ov_end_ln, ov_end_col = ov.f.loc

    rpars = next_delims(lines, ce_end_ln, ce_end_col, ov_ln, ov_col)

    if (lrpars := len(rpars)) == 1:
        ln = ce_ln
        col = ce_col

    else:
        lpars = prev_delims(lines, *self._prev_bound_step('allown'), ce_ln, ce_col)
        ln, col = lpars[min(lrpars, len(lpars)) - 1]

    lpars = prev_delims(lines, ce_end_ln, ce_end_col, ov_ln, ov_col)

    if (llpars := len(lpars)) == 1:
        return fstloc(ln, col, ov_end_ln, ov_end_col)

    rpars = next_delims(lines, ov_end_ln, ov_end_col, *self._next_bound_step('allown'))
    end_ln, end_col = rpars[min(llpars, len(rpars)) - 1]

    return fstloc(ln, col, end_ln, end_col)


def loc_match_case(self: fst.FST) -> fstloc:
    """`match_case` location from children.

    **Note:** This function is explicitly safe to use from `FST.loc`.
    """

    # assert isinstance(self.a, match_case)

    ast = self.a
    first = ast.pattern.f
    last = self.last_child()
    lines = self.root._lines

    start = prev_find(lines, 0, 0, first.ln, first.col, 'case')  # we can use '0, 0' because we know "case" starts on a newline

    if ast.body:
        return fstloc(*start, last.bend_ln, last.bend_col)

    end_ln, end_col = next_find(lines, last.bend_ln, last.bend_col, len(lines) - 1, len(lines[-1]), ':')  # special case, deleted whole body, end must be set to just past the colon (which MUST follow somewhere there)

    return fstloc(*start, end_ln, end_col + 1)


def loc_operator(self: fst.FST) -> fstloc | None:
    """Get location of `operator`, `unaryop` or `cmpop` from source if possible. `boolop` has no location if it has a
    parent because in this case it can be in multiple location in a `BoolOp` and we want to be consistent.

    **Note:** This function is explicitly safe to call from `FST.loc`.
    """

    # assert isinstance(self.a, (operator, unaryop, cmpop))

    ast = self.a

    if not (op := OPCLS2STR.get(ast.__class__)):
        return None

    lines = self.root._lines

    if not (parent := self.parent):  # standalone
        ln, col, src = next_frag(lines, 0, 0, len(lines) - 1, 0x7fffffffffffffff)  # must be there

        if not isinstance(ast, (NotIn, IsNot)):  # simple one element operator means we are done
            assert src == op or (isinstance(ast, operator) and src == op + '=')

            return fstloc(ln, col, ln, col + len(src))

        op, op2 = op.split(' ')

        assert src == op

        end_ln, end_col, src = next_frag(lines, ln, col + len(op), len(lines) - 1, 0x7fffffffffffffff)  # must be there

        assert src == op2

        return fstloc(ln, col, end_ln, end_col + len(op2))

    # has a parent

    parenta = parent.a

    if isinstance(parenta, UnaryOp):
        ln, col, _, _ = parenta.f.loc

        return fstloc(ln, col, ln, col + len(op))

    if isinstance(parenta, Compare):  # special handling due to compound operators and array of ops and comparators
        prev = parenta.comparators[idx - 1] if (idx := self.pfield.idx) else parenta.left

        _, _, end_ln, end_col = prev.f.loc

        if has_space := isinstance(ast, (NotIn, IsNot)):  # stupid two-element operators, can be anything like "not    \\\n     in"
            op, op2 = op.split(' ')

        if pos := next_find(lines, end_ln, end_col, end_lines := len(lines) - 1, len(lines[-1]), op):
            ln, col = pos

            if not has_space:
                return fstloc(ln, col, ln, col + len(op))

            if pos := next_find(lines, ln, col + len(op), end_lines, len(lines[-1]), op2):
                ln2, col2 = pos

                return fstloc(ln, col, ln2, col2 + len(op2))

    elif (prev := (is_binop := getattr(parenta, 'left', None))) or (prev := getattr(parenta, 'target', None)):
        if pos := next_find(lines, (loc := prev.f.loc).end_ln, loc.end_col, len(lines) - 1, len(lines[-1]), op):
            ln, col = pos

            return fstloc(ln, col, ln, col + len(op) + (not is_binop))  # 'not is_binop' adds AugAssign '=' len

    return None


def loc_block_header_end(self: fst.FST, ret_bound: bool = False) -> tuple[int, int, int, int] | tuple[int, int] | None:
    """Return location of the end of the block header line(s) for block node, just BEFORE the ':', or None if `self`
    is not a block header node.

    **Parameters:**
    - `ret_bound`: If `False` then just returns the end position. `True` means return the range used for the search,
        which includes a start at the end of the last child node in the block header (without skipping any closing pars)
        or beginning of the block node if no child nodes in header.

    **Returns:**
    - `(colon ln, colon col)` or `(colon ln, colon col, last child end_ln, last child end_col)`: Returns the location
        just BEFORE the ending colon `:` of the block header. If `ret_bound=True` then also returns two other elements
        which are the end line and end column of the last child in the header or the start line and column of `self` if
        there is not last child (`Try`, `TryStar`). End location of child does NOT include any possibly closing
        parenthesis.
    """

    ln, col, end_ln, end_col = self.loc

    if child := last_block_header_child(a := self.a):
        if loc := (child := child.f).loc:  # because of empty function def arguments which won't have a .loc
            _, _, cend_ln, cend_col = loc
        elif child := child.prev():  # guaranteed to have loc if is there
            _, _, cend_ln, cend_col = child.loc

        else:
            cend_ln = ln
            cend_col = col

    elif isinstance(a, BLOCK):
        cend_ln = ln
        cend_col = col

    else:
        return None

    ln, col = next_find(self.root._lines, cend_ln, cend_col, end_ln, end_col, ':')  # must be there

    return (ln, col, cend_ln, cend_col) if ret_bound else (ln, col)


def loc_arguments_empty(self: fst.FST) -> fstloc:
    """`arguments` location for empty arguments ONLY! DO NOT CALL FOR NONEMPTY ARGUMENTS!"""

    # assert isinstance(self.a, arguments)

    if not (parent := self.parent):
        return fstloc(0, 0, len(ls := self._lines) - 1, len(ls[-1]))  # parent=None means we are root

    ln, col, end_ln, end_col = parent.loc
    lines = self.root._lines

    if isinstance(parenta := parent.a, Lambda):
        col += 6
        end_ln, end_col = next_find(lines, ln, col, end_ln, end_col, ':')

    else:
        if type_params := getattr(parenta, 'type_params', None):  # doesn't exist in py < 3.12
            _, _, ln, col = type_params[-1].f.loc

        ln, col = next_find(lines, ln, col, end_ln, end_col, '(')
        col += 1
        end_ln, end_col = next_find(lines, ln, col, end_ln, end_col, ')')

    return fstloc(ln, col, end_ln, end_col)


def loc_Lambda_args_entire(self: fst.FST) -> fstloc:
    """`Lambda` `args` entire location from just past `lambda` keyword to ':', empty or not. `self` is the `Lambda`, not
    the `arguments`."""

    # assert isinstance(self.a, Lambda)

    ln, col, end_ln, end_col = self.loc
    col += 6
    lines = self.root._lines

    if not (args := self.a.args.f).loc:
        end_ln, end_col = next_find(lines, ln, col, end_ln, end_col, ':')

    else:
        _, _, lln, lcol = args.last_child().loc
        end_ln, end_col = next_find(lines, lln, lcol, end_ln, end_col, ':')

    return fstloc(ln, col, end_ln, end_col)


def loc_ClassDef_bases_pars(self: fst.FST) -> fstlocns:
    """Location of `class cls(...)` bases AND keywords fields-enclosing parentheses, or location where they should be
    put if not present currently (from end of `name` or `type_params` to just before `:`).

    **Returns:**
    - `fstlocns(..., n = pars present or not)`: Just like from `FST.pars()`, with attribute `n=0` meaning no parentheses
        present and location is where they should go and `n=1` meaning parentheses present and location is where they
        actually are.
    """

    # assert isinstance(self.a, ClassDef)

    ast = self.a
    lines = self.root._lines
    ln, col, end_ln, end_col = self.loc

    if body := ast.body:
        end_ln, end_col, _, _ = body[0].f.bloc

    if type_params := getattr(ast, 'type_params', None):  # if type_params then end of '[T, ...]' (py < 3.12 AST.type_params doesn't exist)
        _, _, ln, col = type_params[-1].f.loc

        ln, col = next_find(lines, ln, col, end_ln, end_col, ']')  # must be there
        col += 1

    else:  # otherwise end of class name
        ln, col, src = next_find_re(lines, ln, col + 5, end_ln, end_col, re_identifier)  # must be there
        col += len(src)

    lpln, lpcol, lpsrc = next_frag(lines, ln, col, end_ln, end_col)

    if not lpsrc.startswith('('):  # no parenthesis, must be ':'
        assert lpsrc.startswith(':')

        return fstlocns(ln, col, lpln, lpcol, n=0)

    if last := last[-1].value if (last := ast.keywords) else last[-1] if (last := ast.bases) else None:
        _, _, ln, col = last.f.pars()
    else:
        ln = lpln
        col = lpcol + 1

    rpln, rpcol = next_find(lines, ln, col, end_ln, end_col, ')')  # must be there

    return fstlocns(lpln, lpcol, rpln, rpcol + 1, n=1)


def loc_ImportFrom_names_pars(self: fst.FST) -> fstlocns:
    """Location of `from ? import (...)` whole names field-enclosing parentheses, or location where they should be put
    if not present currently.

    Can handle empty `module` and `names`.

    **Returns:**
    - `fstlocns`: Just like from `FST.pars()`, with attribute `n=0` meaning no parentheses present and location is where
        they should go and `n=1` meaning parentheses present and location is where they actually are.
    """

    # assert isinstance(self.a, ImportFrom)

    lines = self.root._lines
    ln, col, end_ln, end_col = self.loc
    ln, col, _ = next_find_re(lines, ln, col, end_ln, end_col, _re_keyword_import)  # must be there (and 'import' is invalid as module or dotted component of it)
    col += 6

    if (lpar := next_frag(lines, ln, col, end_ln, end_col)) and lpar.src.startswith('('):  # opening par follows 'import'
        assert end_col and lines[end_ln][end_col - 1] == ')'  # closing par must be exactly at end

        ln, col, _ = lpar
        n = 1

    else:
        if lines[ln][col : col + 1].isspace():
            col += 1

        n = 0

    return fstlocns(ln, col, end_ln, end_col, n=n)


def loc_With_items_pars(self: fst.FST) -> fstlocns:
    """Location of `with (...)` whole items field-enclosing parentheses, or location where they should be put if not
    present currently.

    Can handle empty `items`.

    **Note:** Parenthesizing the `items` if not present where it says may still result in "unparenthesized" with as
    those parentheses may pass on to belong to the child if it is a single item with no `optional_vars`.

    **Returns:**
    - `fstlocns(..., n = pars present or not, bound = bound of search)`: Just like from `FST.pars()`, with attribute
        `n=0` meaning no parentheses present and location is where they should go and `n=1` meaning parentheses present
        and location is where they actually are. There is also a `bound` attribute which is an `fstloc` which is the
        location from just past the `with` (no space) to just before the `:`.
    """

    # assert isinstance(self.a, (With, AsyncWith))

    ast = self.a
    lines = self.root._lines
    ln, col, end_ln, end_col = self.loc

    if isinstance(ast, AsyncWith):
        ln, col, _ = next_find_re(lines, ln, col, end_ln, end_col, _re_keyword_with_start)  # must be there, skip the 'async'

    col += 4

    if items := ast.items:
        _, _, after_items_ln, after_items_col = items[-1].f.loc
    else:  # we handle temporarily empty items
        after_items_ln = ln
        after_items_col = col

    end_ln, end_col = next_find(lines, after_items_ln, after_items_col, end_ln, end_col, ':')  # must be there

    bound = fstloc(ln, col, end_ln, end_col)

    if ((lpar := next_frag(lines, ln, col, end_ln, end_col)) and lpar.src.startswith('(') and  # does opening par follow 'with'
        not (items and ((loc_i0 := items[0].f.loc).col == lpar.col and loc_i0.ln == lpar.ln))  # if there are items and first `withitem` starts at lpar found then we know that lpar belongs to it and whole `items` field doesn't have pars
    ):
        ln, col, _ = lpar

        if items:
            rpar = prev_frag(lines, after_items_ln, after_items_col, end_ln, end_col)  # closing par may not immediately precede the ':'
        else:
            rpar = prev_frag(lines, ln, col + 1, end_ln, end_col)

        assert rpar and rpar.src.endswith(')')

        end_ln, end_col, src = rpar
        end_col += len(src)
        n = 1

    else:
        if lines[ln][col : col + 1].isspace():
            col += 1

        n = 0

    return fstlocns(ln, col, end_ln, end_col, n=n, bound=bound)


def loc_Call_pars(self: fst.FST) -> fstloc:
    """Location is from just before opening par to just past closing par."""

    # assert isinstance(self.a, Call)

    ast = self.a
    lines = self.root._lines
    _, _, ln, col = ast.func.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col = next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def loc_Subscript_brackets(self: fst.FST) -> fstloc:
    # assert isinstance(self.a, Subscript)

    ast = self.a
    lines = self.root._lines
    _, _, ln, col = ast.value.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col = next_find(lines, ln, col, end_ln, end_col, '[')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def loc_MatchClass_pars(self: fst.FST) -> fstloc:
    # assert isinstance(self.a, MatchClass)

    ast = self.a
    lines = self.root._lines
    _, _, ln, col = ast.cls.f.loc
    _, _, end_ln, end_col = self.loc
    ln, col = next_find(lines, ln, col, end_ln, end_col, '(')  # must be there

    return fstloc(ln, col, end_ln, end_col)


def loc_FunctionDef_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    # assert isinstance(self.a, (FunctionDef, AsyncFunctionDef))

    ast = self.a
    lines = self.root._lines
    args = ast.args

    ln, col, end_ln, end_col = self.loc

    if ((after := args.posonlyargs) or (after := args.args) or (after := args.vararg) or (after := args.kwonlyargs) or
        (after := args.kwarg) or (after := ast.returns) or (after := ast.body)
    ):
        after_ln, after_col, _, _ = (after[0] if isinstance(after, list) else after).f.loc
    else:  # accomodate temporarily empty bodies
        after_ln = end_ln
        after_col = end_col

    if isinstance(ast, AsyncFunctionDef):
        ln, col = next_find(lines, ln, col + 5, after_ln, after_col, 'def')  # must be there

    name_end_ln, name_end_col, src = next_find_re(lines, ln, col + 3, after_ln, after_col, re_identifier)  # must be there

    name_end_col += len(src)

    if not (pos := next_find(lines, name_end_ln, name_end_col, after_ln, after_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, after_ln, after_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def loc_ClassDef_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    # assert isinstance(self.a, ClassDef)

    ast = self.a
    lines = self.root._lines

    ln, col, end_ln, end_col = self.loc

    if (after := ast.bases) or (after := ast.keywords) or (after := ast.body):
        after_ln, after_col, _, _ = after[0].f.bloc  # .bloc because body[0] might start with a decorator
    else:  # accomodate temporarily empty bodies
        after_ln = end_ln
        after_col = end_col

    name_end_ln, name_end_col, src = next_find_re(lines, ln, col + 5, after_ln, after_col, re_identifier)  # must be there

    name_end_col += len(src)

    if not (pos := next_find(lines, name_end_ln, name_end_col, after_ln, after_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, after_ln, after_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def loc_TypeAlias_type_params_brackets(self: fst.FST) -> tuple[fstloc | None, tuple[int, int]]:
    """Get location of brackets (if present) and end of name where brackets would / do NORMALLY start. This may return
    a location for brackets if they are there even if there are no type_params (for editing purposes).

    **Returns:**
    - (loc brackets | None, pos end of name)
    """

    # assert isinstance(self.a, TypeAlias)

    ast = self.a
    lines = self.root._lines

    _, _, name_end_ln, name_end_col = ast.name.f.loc
    val_ln, val_col, _, _ = ast.value.f.loc

    if not (pos := next_find(lines, name_end_ln, name_end_col, val_ln, val_col, '[')):  # MAY be there
        return None, (name_end_ln, name_end_col)

    ln, col = pos

    if type_params := ast.type_params:
        _, _, end_ln, end_col = type_params[-1].f.loc
    else:
        end_ln = ln
        end_col = col + 1

    end_ln, end_col = next_find(lines, end_ln, end_col, val_ln, val_col, ']')  # must be there

    return fstloc(ln, col, end_ln, end_col + 1), (name_end_ln, name_end_col)


def loc_Global_Nonlocal_names(self: fst.FST, first: int, last: int | None = None) -> fstloc | tuple[fstloc, fstloc]:
    """We assume `first` and optionally `last` are in [0..len(names)), no negative or out-of-bounds and `last` follows
    or equals `first` if present."""

    # assert isinstance(self.a, (Global, Nonlocal))

    ln, col, end_ln, end_col = self.loc

    col += 6 if isinstance(self.a, Global) else 8
    lines = self.root._lines
    idx = first

    while idx:  # skip the commas
        ln, col = next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col += 1
        idx -= 1

    ln, col, src = next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there
    first_loc = fstloc(ln, col, ln, col := col + len(src))

    if last is None:
        return first_loc

    if not (idx := last - first):
        return first_loc, first_loc

    while idx:
        ln, col = next_find(lines, ln, col, end_ln, end_col, ',')  # must be there
        col += 1
        idx -= 1

    ln, col, src = next_find_re(lines, ln, col, end_ln, end_col, re_identifier)  # must be there

    return first_loc, fstloc(ln, col, ln, col + len(src))
