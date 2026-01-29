"""Put single node.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from itertools import takewhile
from types import FunctionType, NoneType
from typing import Any, Callable, Mapping, NamedTuple

from . import fst

from .asttypes import (
    ASTS_LEAF_EXPR,
    ASTS_LEAF_PATTERN,
    ASTS_LEAF_STMTLIKE_OR_MOD,
    ASTS_LEAF_WITH,
    ASTS_LEAF_ARGLIKE,
    AST,
    Add,
    And,
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
    Del,
    Delete,
    Dict,
    DictComp,
    ExceptHandler,
    Expr,
    Expression,
    For,
    FormattedValue,
    FunctionDef,
    GeneratorExp,
    Global,
    If,
    IfExp,
    Import,
    ImportFrom,
    In,
    Interactive,
    Is,
    IsNot,
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
    MatchStar,
    MatchValue,
    Module,
    Name,
    NamedExpr,
    Nonlocal,
    Not,
    NotIn,
    Raise,
    Return,
    Set,
    SetComp,
    Slice,
    Starred,
    Store,
    Sub,
    Subscript,
    Try,
    Tuple,
    USub,
    UnaryOp,
    While,
    With,
    Yield,
    YieldFrom,
    alias,
    arg,
    arguments,
    comprehension,
    expr_context,
    keyword,
    match_case,
    pattern,
    withitem,
    type_param,
    TryStar,
    TypeAlias,
    TypeVar,
    ParamSpec,
    TypeVarTuple,
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
    constant,
    re_alnum,
    re_alnumdot,
    re_alnumdot_alnum,
    re_identifier,
    re_identifier_dotted,
    re_identifier_alias,
    bistr,
    is_valid_target,
    is_valid_del_target,
    is_valid_MatchValue_value,
    is_valid_MatchMapping_key,
    get_field,
    set_field,
    arglike_kind,
    precedence_require_parens,
)

from .common import (
    PYLT11,
    PYGE14,
    NodeError,
    astfield,
    fstloc,
    pyver,
    next_frag,
    prev_frag,
    next_find,
    prev_find,
    next_find_re,
    prev_delims,
)

from .code import (
    Code,
    _code_as_lines,
    code_as_expr,
    code_as_expr_arglike,
    code_as_expr_slice,
    code_as_Tuple_elt,
    code_as__arglike,
    code_as_boolop,
    code_as_operator,
    code_as_unaryop,
    code_as_cmpop,
    code_as_comprehension,
    code_as_arguments,
    code_as_arguments_lambda,
    code_as_arg,
    code_as_keyword,
    code_as_alias,
    code_as_Import_name,
    code_as_ImportFrom_name,
    code_as_withitem,
    code_as_pattern,
    code_as_type_param,
    code_as_identifier,
    code_as_identifier_dotted,
    code_as_identifier_alias,
    code_as_constant,
)

from .fst_misc import fixup_one_index, validate_put_arglike
from .fst_get_one import _params_Compare


_PutOneCode = Code | str | constant | None  # yes, None is already in constant, but just to make this explicit that None may be in place of an expected AST where a constant is not expected
_Child      = AST | list[AST] | constant | None


class onestatic(NamedTuple):
    getinfo:  Callable[[fst.FST, onestatic, int | None, str], oneinfo] | None
    restrict: type[AST] | tuple[type[AST]] | list[type[AST]] | Callable[[AST], bool] | None = None
    code_as:  Callable[[Code, dict], fst.FST] = code_as_expr
    ctx_cls:  type[expr_context] = Load


class oneinfo(NamedTuple):
    prefix:     str           = ''    # prefix to add on insert
    loc_insdel: fstloc | None = None  # only present if insert (put new to nonexistent) or delete is possible and is the location for the specific mutually-exclusive operation
    loc_prim:   fstloc | None = None  # location of primitive, mostly identifier
    suffix:     str           = ''    # or ': ' for dict '**'
    delstr:     str           = ''    # or '**'


def _validate_put(
    self: fst.FST,
    code: Code | None,
    idx: int | None,
    field: str,
    child: list[AST] | AST | constant | None,
    *,
    can_del: bool = False,
) -> tuple[AST | constant | None, int]:
    """Check that `idx` was passed (or not) as needed and that not deleting if not possible."""

    if isinstance(child, list):
        if idx is None:
            raise IndexError(f'{self.a.__class__.__name__}.{field} needs an index')

        idx = fixup_one_index(len(child), idx)
        child = child[idx]  # this will always be a required child, variable size lists will have been passed on to slice processing before getting here

    elif idx is not None:
        raise IndexError(f'{self.a.__class__.__name__}.{field} does not take an index')

    if not can_del and code is None:
        raise ValueError(f'cannot delete{"" if idx is None else " from"} {self.a.__class__.__name__}.{field}')

    return child, idx


def _validate_put_ast(self: fst.FST, put_ast: AST, idx: int | None, field: str, static: onestatic) -> None:
    if restrict := static.restrict:
        if isinstance(restrict, list):  # list means these types not allowed
            if isinstance(put_ast, tuple(restrict)):
                raise NodeError(f'{self.a.__class__.__name__}.{field} cannot be {put_ast.__class__.__name__}')

        elif (res_cls := restrict.__class__) is FunctionType:
            if not restrict(put_ast):  # not "restrict" meaning is inverted here, really means "not allow"
                raise NodeError(f'invalid value for {self.a.__class__.__name__}.{field}'
                                f', got {put_ast.__class__.__name__}')

        elif res_cls is frozenset:  # ASTS_LEAF_?
            if put_ast.__class__ not in restrict:
                raise NodeError(f'{self.a.__class__.__name__}.{field} cannot be {put_ast.__class__.__name__}')

        elif not isinstance(put_ast, restrict):  # single AST type or tuple means only these allowed
            raise NodeError((f'expecting a {restrict.__name__} for {self.a.__class__.__name__}.{field}'
                              if isinstance(restrict, type) else
                              f'expecting one of ({", ".join(c.__name__ for c in restrict)}) for '
                              f'{self.a.__class__.__name__}.{field}') +
                             f', got {put_ast.__class__.__name__}')


def _validate_pattern_attr(self: fst.FST) -> Name:
    while True:
        if self.pars().n:
            raise NodeError(f'cannot put parenthesized {self.a.__class__.__name__} to pattern expression')

        ast = self.a
        ast_cls = ast.__class__

        if ast_cls is Name:
            return ast

        if ast_cls is not Attribute:
            raise NodeError(f'cannot put {ast_cls.__name__} to pattern expression')

        self = ast.value.f


def _is_valid_MatchClass_cls(ast: AST) -> bool:
    if (f := ast.f).end_ln != f.ln:
        raise NotImplementedError(f'cannot put multiline {ast.__class__.__name__} to MatchClass pattern expression')

    if _validate_pattern_attr(ast.f).id == '_':
        raise NodeError("cannot start MatchClass.cls with wildcard specifier '_'")

    return True


def _is_valid_MatchValue_value(ast: AST) -> bool:
    if not is_valid_MatchValue_value(ast):
        return False

    # if (f := ast.f).end_ln != f.ln:
    #     raise NodeError(f'cannot put multiline {ast.__class__.__name__} to pattern expression')

    if any((bad := f).pars().n for f in ast.f.walk()):
        raise NodeError(f'cannot put parenthesized {bad.a.__class__.__name__} to pattern expression')

    return True


def _is_valid_MatchMapping_key(ast: AST) -> bool:
    if not is_valid_MatchMapping_key(ast):
        return False

    if any((bad := f).pars().n for f in ast.f.walk()):
        raise NodeError(f'cannot put parenthesized {bad.a.__class__.__name__} to pattern expression')

    return True


def _maybe_par_above(above: fst.FST, below: fst.FST) -> bool:
    while (a := below.a).__class__ in (Attribute, Subscript):
        if below.pars().n:
            above._parenthesize_grouping()

            return True

        below = a.value.f

    else:
        if a.__class__ is Name and below.pars().n:
            above._parenthesize_grouping()

            return True

    return False


def _fix_With_items(self: fst.FST) -> None:
    """If `Tuple` only element in `items` then add appropriate parentheses."""

    assert self.a.__class__ in ASTS_LEAF_WITH

    if len(items := self.a.items) != 1:
        return

    if (i0a := items[0]).optional_vars:
        return

    cef = i0a.context_expr.f

    if (is_pard_tup := cef.is_parenthesized_tuple()) is None:
        return

    if not is_pard_tup:
        cef._delimit_node()

    if len(prev_delims(self.root._lines, self.ln, self.col, cef.ln, cef.col)) == 1:  # no pars between start of `with` and start of tuple?
        cef._parenthesize_grouping()  # these will wind up belonging to outer With


# ......................................................................................................................
# misc put

def _put_one_constant(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:  # child: constant
    """Put a single constant value, only Constant and MatchSingleton (and only exists because of the second one)."""

    _validate_put(self, code, idx, field, child, can_del=True)  # can_del so that None is accepted

    value = code_as_constant(code, options, self.root.parse_params)
    restrict = static.restrict

    if not isinstance(value, restrict):
        raise NodeError((f'expecting a {"constant" if restrict is constant else restrict.__name__} '
                         f'for {self.a.__class__.__name__}.{field}' if not isinstance(restrict, tuple) else
                         f'expecting one of ({", ".join(c.__name__ for c in restrict)}) for '
                         f'{self.a.__class__.__name__}') +
                        f', got {value.__class__.__name__}')

    self._put_src(repr(value), *self.loc, True)

    ast = self.a
    ast.value = value

    if hasattr(ast, 'kind'):  # reset any 'u' kind strings
        ast.kind = None

    return self  # this breaks the rule of returning the child node since it is just a primitive


def _put_one_op(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: None,
    options: Mapping[str, Any],
) -> fst.FST:  # child: type[boolop | operator | unaryop | cmpop]
    """Put a single operator, lots of rules to check."""

    root = self.root
    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, root.parse_params, sanitize=True)
    codea = code.a
    childf = child.f

    if self.parent_pattern():  # if we are in a pattern then replacements are restricted
        if child.__class__ is USub:  # indicates we are in UnaryOp
            if codea.__class__ is not USub:
                raise NodeError("cannot put anything other than '-' to a pattern UnaryOp.op")

        elif codea.__class__ not in (Add, Sub):  # otherwise MUST be BinOp
            raise NodeError("cannot put anything other than '+' or '-' to a pattern BinOp.op")

    is_alnum = codea.__class__ in (Not, Is, IsNot, In, NotIn)  # alphanumneric operators may need spaces added

    self._put_src(code._lines, *childf.loc, False)
    childf._set_ast(codea)

    ast = self.a
    ast_cls = ast.__class__

    if (is_binop := (ast_cls is BinOp)) or ast_cls is UnaryOp:  # parenthesize if precedence requires according to new operator
        if (parent := self.parent) and precedence_require_parens(ast, parent.a, *self.pfield) and not self.pars().n:
            self._parenthesize_grouping()

        if not is_binop:
            if precedence_require_parens(operand := ast.operand, ast, 'operand') and not (f := operand.f).pars().n:
                f._parenthesize_grouping()

        else:
            if precedence_require_parens(left := ast.left, ast, 'left') and not (f := left.f).pars().n:
                f._parenthesize_grouping()

            if precedence_require_parens(right := ast.right, ast, 'right') and not (f := right.f).pars().n:
                f._parenthesize_grouping()

    if is_alnum:  # we do this after parenthesization because it can remove the need for spaces
        ln, col, end_ln, end_col = get_field(ast, field, idx).f.loc
        lines = root._lines

        if re_alnum.match(lines[end_ln], end_col):  # insert space at end of operator?
            self._put_src([' '], end_ln, end_col, end_ln, end_col, False)

        if col and re_alnumdot.match(lines[ln], col - 1):  # insert space at start of operator? don't need to offset head because operator doesn't have `col_offset`
            self._put_src([' '], ln, col, ln, col, False)

    return childf


def _put_one_ctx(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: None,
    options: Mapping[str, Any],
) -> fst.FST:  # child: expr_context
    """This only exists to absorb the put and validate that it is the only value it can be."""

    child, idx = _validate_put(self, code, idx, field, child)

    if isinstance(code, fst.FST):
        code = code.a
    elif not isinstance(code, AST):
        raise ValueError(f'expecting expr_context, got {code.__class__.__name__}')

    if code.__class__ is not child.__class__:
        raise ValueError(f'invalid expr_context, can only be {child.__class__.__name__}')

    return child.f


def _put_one_AnnAssign_simple(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:  # child: int
    """Parenthesize or unparenthesize `AnnAssign.value` according to this, overkill, definitely overkill."""

    ast = self.a
    child, idx = _validate_put(self, code, idx, field, child)
    value = code_as_constant(code, options, self.root.parse_params)

    if value.__class__ is not int or not 0 <= value <= 1:
        raise ValueError('expection 0 or 1')

    if value != self.a.simple:
        is_name = (target := ast.target).__class__ is Name

        if value:
            if not is_name:
                raise ValueError('cannot make simple')

            target.f._unparenthesize_grouping(False)

        elif is_name and not target.f.pars().n:
            target.f._parenthesize_grouping()

        self.a.simple = value

    return self  # cannot return primitive


def _put_one_ImportFrom_level(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: None,
    options: Mapping[str, Any],
) -> fst.FST:  # child: int
    """Set a comprehension as async or sync."""

    ast = self.a
    root = self.root
    child, idx = _validate_put(self, code, idx, field, child)
    value = code_as_constant(code, options, root.parse_params)

    if value.__class__ is not int or value < 0:
        raise ValueError(f'expection int >= 0, got {value!r}')

    if value != child:
        if not value and self.a.module is None:
            raise ValueError('cannot set ImportFrom.level to 0 in this state (no module present)')

        lines = root._lines
        ln, col, _, _ = self.loc
        end_ln, end_col, _, _ = ast.names[0].f.loc
        ln, col, _ = next_frag(lines, ln, col + 4, end_ln, end_col)  # must be there, col + 4 is just past 'from'
        start_ln = ln
        start_col = col

        while dot := next_find(lines, ln, col, end_ln, end_col, '.'):
            ln, col = dot
            col += 1
            child -= 1

        assert not child

        self._put_src('.' * value, start_ln, start_col, ln, col, False)

        ast.level = value

    return self  # cannot return primitive


def _put_one_BoolOp_op(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: None,
    options: Mapping[str, Any],
) -> fst.FST:  # child: type[boolop]
    """Put BoolOp op to potentially multiple places."""

    root = self.root
    lines = root._lines
    child, idx = _validate_put(self, code, idx, field, child)
    childf = child.f
    code = code_as_boolop(code, options, root.parse_params)
    codea = code.a
    src = 'and' if codea.__class__ is And else 'or'
    tgt = 'and' if child.__class__ is And else 'or'
    ltgt = len(tgt)

    _, _, end_ln, end_col = self.loc

    for value in self.a.values[-2::-1]:  # reverse direction so that we don't need to refresh end_col
        _, _, ln, col = value.f.pars()
        ln, col = next_find(lines, ln, col, end_ln, end_col, tgt)  # must be there

        self._put_src(src, ln, col, ln, col + ltgt, False)

    childf._set_ast(codea)

    if src != tgt:  # if replacing with different boolop then need to parenthesize self if parent is BoolOp or children if they are BoolOps to keep structure regardless of precedence
        if (parent := self.parent) and parent.a.__class__ is BoolOp and not self.pars().n:
            self._parenthesize_grouping()

        for a in self.a.values:
            if a.__class__ is BoolOp and not (f := a.f).pars().n:
                f._parenthesize_grouping()

    return childf


def _put_one_Constant_kind(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: None,
    options: Mapping[str, Any],
) -> fst.FST:  # child: str | None
    """Set a Constant string kind to 'u' or None, this is truly unnecessary."""

    ast = self.a
    root = self.root
    child, idx = _validate_put(self, code, idx, field, child, can_del=True)
    value = code_as_constant(code, options, root.parse_params)

    if not isinstance(ast.value, str):
        raise ValueError('cannot set kind of non-str Constant')

    ln, col, _, _ = self.loc
    lines = root._lines

    if value != child:
        if value is None:
            if lines[ln].startswith('u', col):
                self._put_src(None, ln, col, ln, col + 1, False)

        elif value == 'u':
            if lines[ln][col : col + 1] in '\'"':
                self._put_src(['u'], ln, col, ln, col, False, False)

        else:
            raise ValueError(f"expecting 'u' or None, got {value!r}")

        ast.kind = value

    return self  # cannot return primitive


def _put_one_comprehension_is_async(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: None,
    options: Mapping[str, Any],
) -> fst.FST:  # child: int
    """Set a comprehension as async or sync."""

    root = self.root
    child, idx = _validate_put(self, code, idx, field, child)
    value = code_as_constant(code, options, root.parse_params)

    if value.__class__ is not int or not 0 <= value <= 1:
        raise ValueError(f'expection 0 or 1, got {value!r}')

    if value != child:
        ln, col, end_ln, end_col = self.loc

        if value:
            self._put_src(['async '], ln, col, ln, col, False, False)

        else:
            end_ln, end_col = next_find(root._lines, ln, col, end_ln, end_col, 'for')  # must be there

            self._put_src(None, ln, col, end_ln, end_col, False)

        self.a.is_async = value

    return self  # cannot return primitive


def _put_one_NOT_IMPLEMENTED_YET(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    raise NotImplementedError('this is not implemented yet')


@pyver(lt=12, else_=_put_one_NOT_IMPLEMENTED_YET)
def _put_one_NOT_IMPLEMENTED_YET_12(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    raise NotImplementedError('this will only be implemented on python version 3.12 and above')


@pyver(lt=14, else_=_put_one_NOT_IMPLEMENTED_YET)
def _put_one_NOT_IMPLEMENTED_YET_14(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    raise NotImplementedError('this will only be implemented on python version 3.14 and above')


# ......................................................................................................................
# exprlike put (expr, pattern, comprehension, etc...)

def _fix_deferred_make_exprlike_fst_par(self: fst.FST) -> None:
    """If parenthesization was deferred in `_make_exprlike_fst()` then do it here."""

    a = self.a

    while True:
        if (f := a.f).is_parenthesizable():
            if a.__class__ is Tuple:  # will be undelimited if we got here
                f._delimit_node()
            else:
                f._parenthesize_grouping()

            break

        if (a_cls := a.__class__) in ASTS_LEAF_WITH:  # With.items, if we got to this it was from the `items` because if from `body` then would have terminated before getting here
            pars_ln, pars_col, pars_end_ln, pars_end_col = f._loc_With_items_pars()

            f._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, False)
            f._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

            break

        if a_cls in ASTS_LEAF_STMTLIKE_OR_MOD:
            break

        if not (parent := f.parent):  # if this happens then nothing is parenthesized, but nothing was parenthesizable along the way so root isn't parsable standalone anyway
            break

        a = parent.a


def _make_exprlike_fst(  # TODO: this needs a refactor, cleanup and simplification
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    static: onestatic,
    options: Mapping[str, Any],
    target: fst.FST | fstloc,
    ctx_cls: type[expr_context],
    prefix: str = '',
    suffix: str = '',
    validated: int = 0,
    arglike: bool = False,
) -> tuple[fst.FST, bool]:
    """Make an expression `FST` from `Code` for a field/idx containing an existing node or creating a new one. Takes
    care of parenthesizing, indenting and offsetting.

    **Parameters:**
    - `validated`: The level to which code has already been validated and / or code_as()ed, `0`, `1` or `2`.
    - `arglike`: Whether target is a valid arglike location (`Call.args`, `ClassDef.bases` or unaprenthesized slice
        `Tuple`). Used to determine whether arglike expression needs parentheses added.
    """

    root = self.root

    if validated < 2:
        put_fst = static.code_as(code, options, root.parse_params, sanitize=True,
                                 coerce=fst.FST.get_option('coerce', options))
    else:
        put_fst = code

    put_ast = put_fst.a

    _validate_put_ast(self, put_ast, idx, field, static)

    # figure out parentheses

    pars = fst.FST.get_option('pars', options)
    put_is_star = put_ast.__class__ is Starred
    tgt_is_FST = target.is_FST
    del_tgt_pars = False
    deferred_par = False

    def need_pars(adding: bool) -> bool:
        """`adding` means looking to add pars to `put_fst`, otherwise it already has."""

        if not put_fst._is_atom(pars=False):
            if not put_is_star:
                if precedence_require_parens(put_ast, self.a, field, idx):
                    return True

            else:  # Starred gets checked against its child value because is complicated, could be a Call.args or ClassDef.bases '*a or b' or could have child already parenthesized (or worse, unparenthesized Subscript.slice Tuple)
                star_child = put_ast.value

                if (star_child.__class__ is not Tuple  # if Tuple we assume it is parenthesized because otherwise it could not come into existence without schenanigans
                    and precedence_require_parens(star_child, put_ast, 'value', arglike=arglike)
                    and (not adding or not star_child.f.pars().n)  # `not adding` to make sure we don't remove existing needed pars
                ):
                    return True

        elif (
            tgt_is_FST
            and field == 'value'
            and put_ast.__class__ is Constant
            and isinstance(put_ast.value, int)
            and (tgt_parent := target.parent)
            and tgt_parent.a.__class__ is Attribute
        ):  # veeery special case "3.__abs__()" -> "(3).__abs__()"
            return True

        if not self._is_enclosed_in_parents(field) and not put_fst._is_enclosed_or_line(check_pars=adding):
            return True

        if put_ast.__class__ is Lambda:  # Lambda inside FormattedValue/Interpolation needs pars
            s = self
            f = field

            while (s_cls := s.a.__class__) in ASTS_LEAF_EXPR:
                if s_cls in (FormattedValue, Interpolation):
                    if f == 'value':
                        return True

                    break  # will only get here when changing format_spec.values[], TODO: what needs to be done here when that is implemented?

                if s._is_atom(pars=True, always_enclosed=True):
                    break

                if not (f := s.pfield):
                    break

                s = s.parent
                f = f.name

        return False

    if pars:
        if getattr((put_ast.value.f if put_is_star else put_fst).pars(), 'n', 0):  # src has grouping pars, or src.value if src is Starred
            del_tgt_pars = True

            if pars == 'auto':
                if not need_pars(False):
                    put_fst._unparenthesize_grouping(False)

        else:  # src does not have grouping pars
            if ((tgt_has_pars := tgt_is_FST and getattr(target.pars(), 'n', 0))
                and put_fst.is_parenthesized_tuple() is False
            ):
                del_tgt_pars = True
                tgt_has_pars = False

            if tgt_has_pars:
                if not need_pars(True):
                    if pars is True or not (
                        field == 'target'
                        and (tgt_parent := target.parent)  # suuuper minor special case, don't automatically unparenthesize AnnAssign targets
                        and tgt_parent.a.__class__ is AnnAssign
                    ):
                        del_tgt_pars = True

            elif need_pars(True):  # could be parenthesizing grouping or a tuple, not a MatchSeqence because that never gets here unenclosed
                if put_fst.is_parenthesized_tuple() is False:
                    put_fst._delimit_node()
                elif put_fst.is_parenthesizable():  # put_ast.__class__ not in (arg, arguments):
                    put_fst._parenthesize_grouping()
                else:  # arguments or something like this, can't parenthesize this so defer par to parent after everything is done
                    deferred_par = True

    # figure out put target location

    if not tgt_is_FST:
        ln, col, end_ln, end_col = target

    else:
        loc = target.pars(shared=False) if del_tgt_pars else target.loc

        if not del_tgt_pars and target._is_solo_call_arg_genexp():  # need to check this otherwise might eat Call args pars
            if (loc2 := target.pars(shared=False)) > loc:
                loc = loc2

        ln, col, end_ln, end_col = loc

    # do it

    lines = root._lines
    put_lines = put_fst._lines

    merge_alnum_start = bool(col and re_alnumdot_alnum.match(lines[ln][col - 1] + (prefix or put_lines[0][:1])))  # would the start location result in a merged alphanumeric? we do this here because we need to know if to offset put_fst by one more space
    merge_alnum_end = bool(end_col < len(l := lines[end_ln]) and
                           re_alnumdot_alnum.match((suffix or put_lines[-1])[-1:] + l[end_col]))  # would end location result in merged alphanumeric?

    if prefix:
        put_fst._put_src([prefix], 0, 0, 0, 0, True)

    if suffix:
        put_lines[-1] = bistr(put_lines[-1] + suffix)  # don't need to offset anything so just tack onto the end

    put_fst._indent_lns(self._get_block_indent(), docstr=False)

    dcol_offset = lines[ln].c2b(col) + merge_alnum_start
    offset_head = self._is_any_parent_format_spec_start_pos(end_ln, end_col)  # possibly fix FormattedValue and Interpolation .format_spec location if present above self - because can follow IMMEDIATELY after modified value and thus would not have its start offset with head=False in put_src() below (which if this is not the case must be False)

    params_offset = self._put_src(put_lines, ln, col, end_ln, end_col, True, offset_head, exclude=self)

    self._offset(*params_offset, exclude=target, self_=False)  # excluding an fstloc instead of FST is harmless (if target is fstloc, will not exclude anything in that case)
    put_fst._offset(0, 0, ln, dcol_offset)
    put_fst._set_ctx(ctx_cls)

    # if put merged alphanumerics at start and / or end then insert spaces

    if merge_alnum_end:  # we do this first because merged alnum at start could change our location
        send_ln = ln + (dln := len(put_lines) - 1)
        send_col = len(put_lines[-1]) if dln else col + len(put_lines[0])

        self._put_src([' '], send_ln, send_col, send_ln, send_col, False)

    if merge_alnum_start:  # we put this after because otherwise would be included in any parents that start at element being put
        self._put_src([' '], ln, col, ln, col, False)

    return put_fst, deferred_par


def _put_one_exprlike_required(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: list[AST] | AST | None,
    static: onestatic,
    options: Mapping[str, Any],
    validated: int = 0,
    target: fstloc | None = None,
    prefix: str = '',
    arglike: bool = False,
) -> fst.FST:
    """Put a single required expression. Can be standalone or as part of sequence."""

    if not validated:
        child, idx = _validate_put(self, code, idx, field, child)

        assert child  # this is a required field so should not be None, unless at some point in the future we remove it for some special slice representation or some intermediate operationms, in which case catch this

    childf = child.f
    ctx = ctx.__class__ if (ctx := getattr(child, 'ctx', None)) else Load

    put_fst, deferred_par = _make_exprlike_fst(self, code, idx, field, static, options, target or childf, ctx, prefix,
                                               '', validated, arglike)

    childf._set_ast(put_fst.a)

    if deferred_par:  # we need to do this after the put completes to have the complete parent for the operation (With.items is the culprit)
        _fix_deferred_make_exprlike_fst_par(self)

    return childf


def _put_one_exprlike_optional(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: AST,
    static: onestatic,
    options: Mapping[str, Any],
    validated: int = 0,
) -> fst.FST | None:
    """Put new, replace or delete an optional expression."""

    if not validated:
        child, idx = _validate_put(self, code, idx, field, child, can_del=True)

    if code is None:
        if child is None:  # delete nonexistent node, noop
            return None

    elif child:  # replace existing node
        return _put_one_exprlike_required(self, code, idx, field, child, static, options, max(1, validated))

    info = static.getinfo(self, static, idx, field)
    loc = info.loc_insdel

    if code is None:  # delete existing node
        if not loc:
            raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field} in this state')

        self._put_src(info.delstr or None, *loc, True)
        set_field(self.a, None, field, idx)
        child.f._unmake_fst_tree()

        return None

    # put new node

    if not loc:
        raise ValueError(f'cannot create {self.a.__class__.__name__}.{field} in this state')

    put_fst, deferred_par = _make_exprlike_fst(self, code, idx, field, static, options, loc, static.ctx_cls,
                                               info.prefix, info.suffix, max(1, validated))
    put_fst = fst.FST(put_fst.a, self, astfield(field, idx))

    self._make_fst_tree([put_fst])
    put_fst.pfield.set(self.a, put_fst.a)

    if deferred_par:  # we need to do this after the put completes to have the complete parent for the operation (With.items is the culprit)
        _fix_deferred_make_exprlike_fst_par(self)

    return put_fst


def _put_one_FunctionDef_arguments(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Put FunctionDef.arguments. Does not have location if there are no arguments."""

    return _put_one_exprlike_required(self, code or '', idx, field, child, static, options,
                                      target=None if not (args := self.a.args.f).is_empty_arguments() else args.loc)


def _put_one_ClassDef_bases(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Can't replace Starred base with non-Starred base after keywords."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    if (child.__class__ is Starred
        and code.a.__class__ is not Starred
        and (keywords := self.a.keywords)
        and child.f.loc > keywords[0].f.loc
    ):
        raise ValueError('cannot replace Starred ClassDef.bases element '
                         'with non-Starred base at this location (after keywords)')

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2, arglike=True)


def _put_one_ClassDef_keywords(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Don't allow put of `**keyword` before `*arg`."""

    ast = self.a
    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    if code.a.arg is None and (bases := ast.bases) and bases[-1].f.loc > ast.keywords[idx].f.loc:
        raise ValueError("cannot put '**' ClassDef.keywords element at this location (non-keywords follow)")

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)


def _put_one_AnnAssign_target(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Update simple according to what was put."""

    ret = _put_one_exprlike_required(self, code, idx, field, child, static, options)

    self.a.simple = 1 if ret.a.__class__ is Name and not ret.pars().n else 0

    return ret


def _put_one_Import_names(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Don't allow parenthesize multiline alias and instead add line continuation backslashes in this case.."""

    child, idx = _validate_put(self, code, idx, field, child)
    ret = _put_one_exprlike_required(self, code, idx, field, child, static, {**options, 'pars': False}, 1)

    self.a.names[idx].f._maybe_add_line_continuations()

    return ret


def _put_one_ImportFrom_names(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Disallow put star to list of multiple names and unparenthesize if star was put to single name."""

    root = self.root
    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, root.parse_params, sanitize=True, coerce=fst.FST.get_option('coerce', options))

    if is_star := ('*' in code.a.name):  # `in` just in case some whitespace got in there somehow
        if len(self.a.names) != 1:
            raise NodeError('cannot put star alias to ImportFrom.names containing multiple aliases')

    ret = _put_one_exprlike_required(self, code, idx, field, child, static, {**options, 'pars': False}, 2)
    pars = self._loc_ImportFrom_names_pars()

    if is_star:  # for star remove parentheses (including possible trailing comma) if there
        if pars.n:
            pars_ln, pars_col, pars_end_ln, pars_end_col = pars
            star_ln, star_col, star_end_ln, star_end_col = self.a.names[0].f.loc
            _, _, end_ln, end_col = self.loc

            head = ' ' if pars_col and re_alnumdot.match(root._lines[pars_ln], pars_col - 1) else None  # make sure at least space between `from` and `*`

            self._put_src(None, star_end_ln, star_end_col, end_ln, end_col, True)
            self._put_src(head, pars_ln, pars_col, star_ln, star_col, False)

    elif not pars.n and not self._is_enclosed_or_line(check_pars=False):  # otherwise if need them then add
        pars_ln, pars_col, pars_end_ln, pars_end_col = pars

        self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, True, False, self)
        self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

    return ret


def _put_one_BinOp_left_right(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Disallow invalid constant changes in patterns."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    if self.parent_pattern():
        if field == 'right':
            if (codea := code.a).__class__ is not Constant or not isinstance(codea.value, complex):
                raise NodeError('can only put imaginary Constant to a pattern BinOp.right')

        else:  # field == 'left'
            if (codea := code.a).__class__ is UnaryOp:
                if codea.op.__class__ is USub:
                    codea = codea.operand

            if codea.__class__ is not Constant or not isinstance(codea.value, (int, float)):
                raise NodeError('can only put real Constant to a pattern BinOp.left')

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)


def _put_one_UnaryOp_operand(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Disallow invalid constant changes in patterns."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True)

    if self.parent_pattern():
        if (codea := code.a).__class__ is not Constant:
            raise NodeError('can only put Constant to a pattern UnaryOp.operand')

        if not isinstance(codea.value, (int, float) if self.parent.a.__class__ is BinOp else (int, float, complex)):
            raise NodeError('invalid Constant for pattern UnaryOp.operand')

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)


def _put_one_with_items(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    ret = _put_one_exprlike_required(self, code, idx, field, child, static, options)

    _fix_With_items(self)

    return ret


def _put_one_Lambda_arguments(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Put Lambda.arguments."""

    if code is None:
        code = ''

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))
    prefix = '' if code.is_empty_arguments() else ' '
    target = self._loc_Lambda_args_entire()

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 1, target, prefix)


def _put_one_Compare__all(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Put to combined [Compare.left, Compare.comparators] using this total indexing."""

    idx, field, child = _params_Compare(self, idx)

    return _put_one_exprlike_required(self, code, idx, field, child, static, options)  # code=None delete does not get here


def _put_one_Call_args(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Can't replace Starred arg with non-Starred arg after keywords."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    if (child.__class__ is Starred
        and code.a.__class__ is not Starred
        and (keywords := self.a.keywords)
        and child.f.loc > keywords[0].f.loc
    ):
        raise ValueError('cannot replace Starred Call.args element with non-Starred arg at this location'
                         ' (after keywords)')

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2, arglike=True)


def _put_one_Call_keywords(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Don't allow put of `**keyword` before `*arg`."""

    ast = self.a
    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    if code.a.arg is None and (args := ast.args) and args[-1].f.loc > ast.keywords[idx].f.loc:
        raise ValueError("cannot put '**' Call.keywords element at this location (non-keywords follow)")

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)


def _put_one_Constant_value(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: None,
    options: Mapping[str, Any],
) -> fst.FST:
    """Set a `Constant` value, mostly normal unless its a child of a `JoinedStr` or `TemplateStr`."""

    if not ((parent := self.parent) and parent.a.__class__ in (JoinedStr, TemplateStr)):
        return _put_one_constant(self, code, idx, field, child, static, options)

    raise NotImplementedError('put Constant.value which is in JoinedStr/TemplateStr.values')


def _put_one_Attribute_value(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """If this gets parenthesized in an `AnnAssign` then the whole `AnnAssign` target needs to be parenthesized. Also
    need to make sure only unparenthesized `Name` or `Attribute` is put to one of these in `pattern` expression."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))
    is_annass = False
    above = child.f

    while (parent := above.parent) and (pfname := above.pfield.name) in ('value', 'target', 'keys', 'cls'):
        parenta = parent.a
        parent_cls = parenta.__class__

        if parent_cls is AnnAssign:
            is_annass = pfname == 'target'

            break

        if parent_cls in ASTS_LEAF_PATTERN:
            if code.end_ln != code.ln and not above._is_enclosed_in_parents():
                raise NodeError(f'cannot put multiline {above.a.__class__.__name__} to uneclosed pattern expression')

            _validate_pattern_attr(code)

            break

        if parent_cls not in (Attribute, Subscript):  # we need to walk up both of these for the AnnAssign, won't be Subscripts in a MatchMapping.keys
            break

        above = parent

    ret = _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)

    if is_annass and not above.pars().n:
        if _maybe_par_above(above, ret):
            parenta.simple = 0

    return ret


def _put_one_Subscript_value(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """If this gets parenthesized in an AnnAssign then the whole AnnAssign target needs to be parenthesized."""

    ret = _put_one_exprlike_required(self, code, idx, field, child, static, options)
    above = ret

    while (parent := above.parent) and above.pfield.name in ('value', 'target'):
        parenta = parent.a
        parent_cls = parenta.__class__

        if parent_cls is AnnAssign:
            if not above.pars().n:
                _maybe_par_above(above, ret)

            break

        if parent_cls not in (Attribute, Subscript):
            break

        above = parent

    return ret


@pyver(lt=11, else_=_put_one_exprlike_required)
def _put_one_Subscript_slice(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,  # py < 3.11
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Don't allow put unparenthesized tuple containing Starred."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    if code.is_parenthesized_tuple() is False and any(a.__class__ is Starred for a in code.a.elts):
        raise NodeError('cannot have unparenthesized tuple containing Starred in slice')

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)


def _put_one_List_elts(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Disallow non-targetable expressions in targets."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))
    ctx_cls = self.a.ctx.__class__

    if ctx_cls is not Load:  # only allow possible expression targets into an expression target
        if not (is_valid_del_target if ctx_cls is Del else is_valid_target)(code.a):
            raise NodeError(f"invalid expression for List {ctx_cls.__name__} target")

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)


def _put_one_Tuple_elts(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Disallow non-targetable expressions in targets. If not an unparenthesized top level or slice tuple then disallow
    Slices."""

    ast = self.a
    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))
    codea = code.a
    pfield = self.pfield
    is_slice = pfield and pfield.name == 'slice'
    is_delimited = self._is_delimited_seq()

    if pfield and codea.__class__ is Slice:  # putting Slice to non-root Tuple
        if not is_slice:
            raise NodeError('cannot put Slice to non-root Tuple which is not an Subscript.slice')
        elif is_delimited:
            raise NodeError('cannot put Slice to parenthesized Subscript.slice Tuple')

    ctx_cls = ast.ctx.__class__

    if ctx_cls is not Load:  # only allow possible expression targets into an expression target
        if not (is_valid_del_target if ctx_cls is Del else is_valid_target)(codea):
            raise NodeError(f'invalid expression for Tuple {ctx_cls.__name__} target')

    if PYLT11:
        if put_star_to_unpar_slice := (is_slice and codea.__class__ is Starred and not is_delimited):
            r = (elts := ast.elts)[idx]

            if any(e.__class__ is Slice for e in elts if e is not r):
                raise NodeError('cannot put Starred to a slice Tuple containing Slices')

        ret = _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)

        if put_star_to_unpar_slice:
            self._delimit_node()

    else:
        if PYGE14 and self.pfield == ('type', None) and codea.__class__ is Starred and not is_delimited:  # if putting Starred to unparenthesized ExceptHandler.type Tuple then parenthesize it
            self._delimit_node()

        self_is_solo_star_in_slice = is_slice and len(elts := ast.elts) == 1 and elts[0].__class__ is Starred  # because of replacing the Starred in 'a[*i_am_really_a_tuple]'

        ret = _put_one_exprlike_required(self, code, idx, field, child, static, options, 2,
                                         arglike=is_slice and not is_delimited)

        if self_is_solo_star_in_slice:
            self._maybe_add_singleton_comma(is_delimited)

    return ret


def _put_one_Dict_keys(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Put optional dict key and if deleted parenthesize the value if needed."""

    ret = _put_one_exprlike_optional(self, code, idx, field, child, static, options)

    if (code is None
        and not (value := (a := self.a).values[idx].f)._is_atom()
        and precedence_require_parens(value.a, a, 'values', idx)
    ):
        value._parenthesize_grouping()

    return ret


def _put_one_arg(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Don't allow arg with Starred annotation into non-vararg args."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    if code.a.annotation.__class__ is Starred:
        raise NodeError(f'cannot put arg with Starred annotation to {self.a.__class__.__name__}.{field}')

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)


@pyver(ge=11, else_=_put_one_exprlike_optional)  # _put_one_exprlike_optional leaves the _restrict_default in the static which disallows Starred
def _put_one_arg_annotation(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,  # py >= 3.11
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Allow Starred in vararg arg annotation in py 3.11+."""

    if not self.parent or self.pfield.name == 'vararg':
        static = onestatic(_one_info_arg_annotation, _restrict_fmtval_slice)

    return _put_one_exprlike_optional(self, code, idx, field, child, static, options)


def _put_one_withitem_context_expr(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> str:
    """If put a single context_expr `Tuple` with no optional_vars then need to add grouping parentheses if not present
    otherwise the tuple will be reparsed as multiple `withitems` instead of a single `Tuple`."""

    ret = _put_one_exprlike_optional(self, code, idx, field, child, static, options)

    if (parent := self.parent) and parent.a.__class__ in ASTS_LEAF_WITH:
        _fix_With_items(parent)

    return ret


def _put_one_withitem_optional_vars(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> str:
    """If delete leaves a single parenthesized context_expr `Tuple` then need to parenthesize that, otherwise it can be
    reparsed as multiple `withitems` instead of a single `Tuple`."""

    ret = _put_one_exprlike_optional(self, code, idx, field, child, static, options)

    if (parent := self.parent) and parent.a.__class__ in ASTS_LEAF_WITH:
        _fix_With_items(parent)

    return ret


# def _put_one_MatchValue_value(self: fst.FST, code: _PutOneCode, idx: int | None, field: str, child: _Child,
#                               static: onestatic, options: Mapping[str, Any]) -> fst.FST:
#     """Put MatchValue.value. Need to do this because a standalone MatchValue does not encompass parenthesized value
#     parentheses."""

#     ret = _put_one_exprlike_required(self, code, idx, field, child, static, options)
#     a = self.a
#     v = a.value
#     a.lineno = v.lineno
#     a.col_offset = v.col_offset
#     a.end_lineno = v.end_lineno
#     a.end_col_offset = v.end_col_offset

#     return ret


def _put_one_MatchAs_pattern(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Enclose unenclosed MatchSequences being put here, if any."""

    child, idx = _validate_put(self, code, idx, field, child, can_del=True)

    if code is not None:
        code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                              coerce=fst.FST.get_option('coerce', options))

        if code.a.__class__ is MatchStar:
            raise NodeError('cannot put a MatchStar to MatchAs.pattern')

        if code.is_delimited_matchseq() == '':
            code._delimit_node(delims='[]')

    return _put_one_exprlike_optional(self, code, idx, field, child, static, options, 2)


def _put_one_pattern(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Enclose unenclosed MatchSequences being put here."""

    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    if code.a.__class__ is MatchStar:
        if self.a.__class__ is not MatchSequence:
            raise NodeError(f'cannot put a MatchStar to {self.a.__class__.__name__}.{field}')

    elif code.is_delimited_matchseq() == '':
        code._delimit_node(delims='[]')

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2)


def _put_one_arglikes(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Put a single arglike (expression or keyword) to a `ClassDef._bases` or `Call._args` virtual field with restricted
    ordering constraints."""

    arglikes = self._cached_arglikes()
    child, idx = _validate_put(self, code, idx, field, arglikes)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))
    put_kind = validate_put_arglike(arglikes, idx, idx + 1, code.a)
    child_kind = arglike_kind(child)
    child_field, idx = child.f.pfield

    ret = _put_one_exprlike_required(self, code, idx, child_field, child, static, options, 2, arglike=True)

    if put_kind >> 1 != child_kind >> 1:  # if type changed (expr vs. keyword) then we need to update lists because need to move from one to the other as our put just put it into the list that the child was in
        ast = self.a
        put_field = field[1:] if child_field == 'keywords' else 'keywords'
        child_list = getattr(ast, child_field)  # list we are moving from
        put_list = getattr(ast, put_field)  # list we are moving to

        put_list.append(child_list[idx])

        del child_list[idx]

        for i in range(idx, len(child_list)):
            child_list[i].f.pfield = astfield(child_field, i)

        put_list.sort(key=lambda a: (a.lineno, a.col_offset))  # child_list was already ordered so only need to sort this

        for i in range(len(put_list)):
            put_list[i].f.pfield = astfield(put_field, i)

    return ret


def _put_one__arglikes_arglikes(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> fst.FST:
    """Put a single arglike (expression or keyword) to an `_arglikes` SPECIAL SLICE with restricted ordering
    constraints."""

    ast = self.a
    child, idx = _validate_put(self, code, idx, field, child)
    code = static.code_as(code, options, self.root.parse_params, sanitize=True,
                          coerce=fst.FST.get_option('coerce', options))

    validate_put_arglike(ast.arglikes, idx, idx + 1, code.a)

    return _put_one_exprlike_required(self, code, idx, field, child, static, options, 2, arglike=True)


# ......................................................................................................................
# identifier put

def _put_one_identifier_required(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: str,
    static: onestatic,
    options: Mapping[str, Any],
) -> str:
    """Put a single required identifier."""

    _, idx = _validate_put(self, code, idx, field, child)

    code = static.code_as(code, options, self.root.parse_params)  # this will be an identifier code_as_() so sanitize not needed
    info = static.getinfo(self, static, idx, field)

    self._put_src(code, *info.loc_prim, True)
    set_field(self.a, code, field, idx)

    return code


def _put_one_identifier_optional(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: str | None,
    static: onestatic,
    options: Mapping[str, Any],
) -> _PutOneCode:
    """Put new, replace or delete an optional identifier."""

    child, idx = _validate_put(self, code, idx, field, child, can_del=True)

    if code is None and child is None:  # delete nonexistent identifier, noop
        return None

    info = static.getinfo(self, static, idx, field)
    loc = info.loc_insdel

    if code is None:  # delete existing identifier
        if not loc:
            raise ValueError(f'cannot delete {self.a.__class__.__name__}.{field} in this state')

        self._put_src(info.delstr or None, *loc, True)
        set_field(self.a, None, field, idx)

        return None

    code = static.code_as(code, options, self.root.parse_params)

    if child is not None:  # replace existing identifier
        self._put_src(code, *info.loc_prim, True)
        set_field(self.a, code, field, idx)

    else: # put new identifier
        if not loc:
            raise ValueError(f'cannot create {self.a.__class__.__name__}.{field} in this state')

        params_offset = self._put_src(info.prefix + code + info.suffix, *loc, True, exclude=self)

        self._offset(*params_offset, self_=False)
        set_field(self.a, code, field, idx)

    return code


def _put_one_ExceptHandler_name(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> str:  # child: str | None
    """If adding a name to an ExceptHandler with tuple of exceptions then make sure it is parenthesized."""

    ret = _put_one_identifier_optional(self, code, idx, field, child, static, options)

    if ret and (typef := self.a.type.f).is_parenthesized_tuple() is False:
        typef._delimit_node()

    return ret


def _put_one_keyword_arg(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> str:  # child: str | None
    """Don't allow delete keyword.arg if non-keywords follow."""

    if code is None and (parent := self.parent):
        parenta = parent.a
        parent_cls = parenta.__class__

        if parent_cls is Call:
            if (args := parenta.args) and args[-1].f.loc > self.loc:
                raise ValueError('cannot delete arg from Call.keywords at this location (non-keywords follow)')

        elif parent_cls is ClassDef:
            if (bases := parenta.bases) and bases[-1].f.loc > self.loc:
                raise ValueError('cannot delete arg from ClassDef.keywords at this location (non-keywords follow)')

    return _put_one_identifier_optional(self, code, idx, field, child, static, options)


def _put_one_MatchStar_name(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> str:  # child: str
    """Slightly annoying MatchStar.name. '_' really means delete."""

    if code is None:
        code = '_'

    ret = _put_one_identifier_required(self, code, idx, field, child, static, options)

    if self.a.name == '_':
        self.a.name = None

    return ret


def _put_one_MatchAs_name(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: _Child,
    static: onestatic,
    options: Mapping[str, Any],
) -> str:  # child: str
    """Very annoying MatchAs.name. '_' really means delete, which can't be done if there is a pattern, and can't be
    assigned to a pattern."""

    if code is None:
        code = '_'
    else:
        code = code_as_identifier(code, options, self.root.parse_params)

    if self.a.pattern and code == '_':
        raise ValueError("cannot change MatchAs with pattern into wildcard '_'")

    ret = _put_one_identifier_required(self, code, idx, field, child, static, options)

    if self.a.name == '_':
        self.a.name = None

    return ret


# ......................................................................................................................
# field info

_restrict_default        = [FormattedValue, Interpolation, Slice, Starred]
_restrict_fmtval_slice   = [FormattedValue, Interpolation, Slice]
_restrict_fmtval_starred = [FormattedValue, Interpolation, Starred]
_restrict_fmtval         = [FormattedValue, Interpolation]
_oneinfo_default         = oneinfo()

def _one_info_exprlike_required(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _oneinfo_default

_onestatic_expr_required             = onestatic(_one_info_exprlike_required, _restrict_default)
_onestatic_expr_required_w_starred   = onestatic(_one_info_exprlike_required, _restrict_fmtval_slice)
_onestatic_expr_required_arglike     = onestatic(_one_info_exprlike_required, _restrict_fmtval_slice, code_as=code_as_expr_arglike)
_onestatic__arglike_required         = onestatic(_one_info_exprlike_required, ASTS_LEAF_ARGLIKE, code_as=code_as__arglike)
_onestatic_comprehension_required    = onestatic(_one_info_exprlike_required, comprehension, code_as=code_as_comprehension)
_onestatic_arguments_required        = onestatic(_one_info_exprlike_required, arguments, code_as=code_as_arguments)
_onestatic_arguments_lambda_required = onestatic(_one_info_exprlike_required, arguments, code_as=code_as_arguments_lambda)
_onestatic_arg_required              = onestatic(_one_info_exprlike_required, arg, code_as=code_as_arg)
_onestatic_keyword_required          = onestatic(_one_info_exprlike_required, keyword, code_as=code_as_keyword)
_onestatic_alias_required            = onestatic(_one_info_exprlike_required, alias, code_as=code_as_alias)
_onestatic_withitem_required         = onestatic(_one_info_exprlike_required, withitem, code_as=code_as_withitem)
_onestatic_pattern_required          = onestatic(_one_info_exprlike_required, pattern, code_as=code_as_pattern)
_onestatic_type_param_required       = onestatic(_one_info_exprlike_required, type_param, code_as=code_as_type_param)
_onestatic_target_Name               = onestatic(_one_info_exprlike_required, Name, ctx_cls=Store)
_onestatic_target_single             = onestatic(_one_info_exprlike_required, (Name, Attribute, Subscript), ctx_cls=Store)
_onestatic_target                    = onestatic(_one_info_exprlike_required, is_valid_target, ctx_cls=Store)  # (Name, Attribute, Subscript, Tuple, List)
_onestatic_ctx                       = onestatic(None, expr_context)

def _one_info_identifier_required(
    self: fst.FST,
    static: onestatic,
    idx: int | None,
    field: str,  # required, cannot delete or put new
    prefix: str | None = None,
) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    lines = self.root._lines

    if not prefix:
        end_col = re_identifier.match(lines[ln], col, end_col if end_ln == ln else 0x7fffffffffffffff).end()  # must be there

    else:
        ln, col = next_find(lines, ln, col, end_ln, end_col, prefix, lcont=None)  # must be there, have to search because could be preceded by something (like 'async')
        ln, col, src = next_find_re(lines, ln, col + len(prefix), end_ln, end_col, re_identifier, lcont=None)  # must be there
        end_col = col + len(src)

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

_onestatic_identifier_required = onestatic(_one_info_identifier_required, _restrict_default, code_as=code_as_identifier)

def _one_info_identifier_alias(
    self: fst.FST, static: onestatic, idx: int | None, field: str
) -> oneinfo:  # required, cannot delete or put new
    ln, col, end_ln, end_col = self.loc
    end_col = re_identifier_alias.match(self.root._lines[ln], col,
                                        end_col if end_ln == ln else 0x7fffffffffffffff).end()  # must be there

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

def _one_info_FunctionDef_name(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, 'def')

_onestatic_FunctionDef_name = onestatic(_one_info_FunctionDef_name, _restrict_default, code_as=code_as_identifier)

def _one_info_FunctionDef_returns(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self._loc_block_header_end()
    ret_end_ln = end_ln
    ret_end_col = end_col = end_col - 1

    if returns := self.a.returns:
        returnsf = returns.f
        ln, col = prev.loc[2:] if (prev := returnsf.prev()) else self.loc[:2]
        end_ln, end_col, _, _ = returnsf.pars()

    args_end_ln, args_end_col = prev_find(self.root._lines, ln, col, end_ln, end_col, ')')  # must be there

    return oneinfo(' -> ', fstloc(args_end_ln, args_end_col + 1, ret_end_ln, ret_end_col))

_onestatic_FunctionDef_returns = onestatic(_one_info_FunctionDef_returns, _restrict_default)

def _one_info_ClassDef_name(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, 'class')

def _one_info_Return_value(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' ', fstloc((loc := self.loc).ln, loc.col + 6, loc.end_ln, loc.end_col))

def _one_info_AnnAssign_value(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' = ', fstloc((loc := self.a.annotation.f.pars()).end_ln, loc.end_col, self.end_ln, self.end_col))

def _one_info_Raise_exc(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if self.a.cause:
        return _oneinfo_default  # can not del (and exists, so can't put new)

    ln, col, end_ln, end_col = self.loc

    return oneinfo(' ', fstloc(ln, col + 5, end_ln, end_col))

def _one_info_Raise_cause(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if not (exc := self.a.exc):
        return _oneinfo_default  # can not put (or del because cause doesn't exist)

    _, _, ln, col = exc.f.pars()

    return oneinfo(' from ', fstloc(ln, col, self.end_ln, self.end_col))

def _one_info_Assert_msg(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(', ', fstloc((loc := self.a.test.f.pars()).end_ln, loc.end_col, self.end_ln, self.end_col))

def _one_info_ImportFrom_module(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    lines = self.root._lines

    if not self.a.level:  # cannot insert or delete
        ln, col, src = next_find_re(lines, ln, col + 4, end_ln, end_col, re_identifier_dotted, lcont=None)  # must be there, col+4 is for 'from'
        end_col = col + len(src)

        return oneinfo('', None, fstloc(ln, col, ln, end_col))

    self_ln, self_col, _, _ = self.loc
    ln, col = prev_find(lines, self_ln, self_col, *self.a.names[0].f.loc[:2], 'import')
    ln, col, src = prev_frag(lines, self_ln, self_col, ln, col)  # must be there, the module name with any/some/all preceding '.' level indicators
    end_col = col + len(src)
    col = end_col - len((src[4:] if col == self_col and ln == self_ln else src).lstrip('.'))  # may be special case, dot right after 'from', e.g. 'from.something import ...'

    if (lines[ln][col : end_col] or None) != self.a.module:
        raise NotImplementedError('ImportFrom.module not a contiguous string')

    return oneinfo('', loc := fstloc(ln, col, ln, end_col), loc)

def _one_info_Global_Nonlocal_names(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:

    idx = fixup_one_index(len(self.a.names), idx)

    return oneinfo('', None, self._loc_Global_Nonlocal_names(idx))

_onestatic_Global_Nonlocal_names = onestatic(_one_info_Global_Nonlocal_names, _restrict_default, code_as=code_as_identifier)

def _one_info_Dict_key(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    end_ln, end_col, _, _ = self.a.values[idx].f.pars()
    ln, col, _, _ = self._loc_maybe_key(idx)

    return oneinfo('', fstloc(ln, col, end_ln, end_col), None, ': ', '**')

def _one_info_Yield_value(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(' ', fstloc((loc := self.loc).ln, loc.col + 5, loc.end_ln, loc.end_col))

def _one_info_Attribute_attr(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col = self.a.value.f.loc
    _, _, end_ln, end_col = self.loc
    lines = self.root._lines
    ln, col = next_find(lines, ln, col, end_ln, end_col, '.')  # must be there
    ln, col, src = next_frag(lines, ln, col + 1, end_ln, end_col)  # must be there

    return oneinfo('', None, fstloc(ln, col, ln, col + len(src)))

def _one_info_Slice_lower(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc

    if lower := self.a.lower:
        end_ln, end_col = next_find(self.root._lines, (loc := lower.f.loc).end_ln, loc.end_col, end_ln, end_col, ':')  # must be there
    else:
        end_ln, end_col = next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # must be there

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

_onestatic_Slice_lower = onestatic(_one_info_Slice_lower, _restrict_default)

def _one_info_Slice_upper(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, end_ln, end_col = self.loc
    _, _, ln, col = _one_info_Slice_lower(self, _onestatic_Slice_lower, idx, field).loc_insdel
    col += 1

    if upper := self.a.upper:
        end = next_find(self.root._lines, (loc := upper.f.loc).end_ln, loc.end_col, end_ln, end_col, ':')  # may or may not be there
    else:
        end = next_find(self.root._lines, ln, col, end_ln, end_col, ':')  # may or may not be there

    if end:
        end_ln, end_col = end

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

_onestatic_Slice_upper = onestatic(_one_info_Slice_upper, _restrict_default)

def _one_info_Slice_step(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col = _one_info_Slice_upper(self, _onestatic_Slice_upper, idx, field).loc_insdel

    if self.root._lines[ln].startswith(':', col):
        col += 1
        prefix = ''
    else:
        prefix = ':'

    return oneinfo(prefix, fstloc(ln, col, self.end_ln, self.end_col))

_onestatic_Slice_step = onestatic(_one_info_Slice_step, _restrict_default)

def _one_info_ExceptHandler_type(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a

    if ast.name:
        return _oneinfo_default  # can not del (and exists, so can't put new)

    if type_ := ast.type:
        _, _, end_ln, end_col = type_.f.pars()
    else:
        _, _, end_ln, end_col = self._loc_block_header_end()  # because 'name' can not be there
        end_col -= 1

    ln, col, _, _ = self.loc
    col = col + 6  # 'except'

    if star := next_frag(self.root._lines, ln, col, end_ln, end_col):  # 'except*'?
        if star.src.startswith('*'):
            return _oneinfo_default  # can not del type from except* and can not insert because can never not exist

    return oneinfo(' ', fstloc(ln, col, end_ln, end_col))

def _one_info_ExceptHandler_name(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a

    if not (type_ := ast.type):
        return _oneinfo_default  # can not put new and does not exist

    _, _, ln, col = type_.f.pars()
    _, _, end_ln, end_col = self._loc_block_header_end()
    end_col -= 1
    loc_insdel = fstloc(ln, col, end_ln, end_col)

    if (name := ast.name) is None:
        loc_prim = None

    else:
        lines = self.root._lines
        ln, col = next_find(lines, ln, col, end_ln, end_col, 'as')  # skip the 'as'
        ln, col = next_find(lines, ln, col + 2, end_ln, end_col, name)  # must be there
        loc_prim = fstloc(ln, col, ln, col + len(name))

    return oneinfo(' as ', loc_insdel, loc_prim)

def _one_info_arguments_vararg(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a
    lines = self.root._lines

    if vararg := ast.vararg:  # delete location
        varargf = vararg.f

        if next := varargf.next():
            _, _, end_ln, end_col = varargf.pars()
        else:
            _, _, end_ln, end_col = self.loc  # there may be a trailing comma

        if prev := varargf.prev():
            delstr = ', *' if ast.kwonlyargs else ''

            if not (
                ast.posonlyargs
                and (
                    (n := prev.pfield.name) == 'posonlyargs'
                    or (n == 'defaults' and prev.prev().pfield.name == 'posonlyargs')
            )):
                _, _, ln, col = prev.pars()

                return oneinfo('', fstloc(ln, col, end_ln, end_col), delstr=delstr)

            ln, col = next_find(lines, prev.end_ln, prev.end_col, end_ln, end_col, '/')  # must be there

            return oneinfo('', fstloc(ln, col + 1, end_ln, end_col), delstr=delstr)

        if next:
            if ast.kwonlyargs and next.pfield.name == 'kwonlyargs':
                next_ln, next_col, _, _ = next.pars()

                return oneinfo('', fstloc(self.ln, self.col, next_ln, next_col), delstr='*, ')

            end_ln, end_col = next_find(lines, end_ln, end_col, next.ln, next.col, '**')  # must be there

            return oneinfo('', fstloc(self.ln, self.col, end_ln, end_col))

        if not (parent := self.parent) or parent.a.__class__ is not Lambda:
            return oneinfo('', self.loc)

        ln, col, _, _ = parent.loc

        return oneinfo('', fstloc(ln, col + 6, end_ln, end_col))

    # insert location

    if kwonlyargs := ast.kwonlyargs:
        kwonlyargf = kwonlyargs[0].f
        end_ln, end_col, _, _ = kwonlyargf.loc

        if prev := kwonlyargf.prev():
            _, _, ln, col = prev.loc
        else:
            ln, col, _, _ = self.loc

        ln, col = next_find(lines, ln, col, end_ln, end_col, '*')  # must be there
        col += 1

        return oneinfo('', fstloc(ln, col, ln, col))

    if kwarg := ast.kwarg:
        kwargf = kwarg.f
        end_ln, end_col, _, _ = kwargf.loc

        if prev := kwargf.prev():
            _, _, ln, col = prev.loc
        else:
            ln, col, _, _ = self.loc

        ln, col = next_find(lines, ln, col, end_ln, end_col, '**')  # must be there

        return oneinfo('*', fstloc(ln, col, ln, col), None, ', ')

    if ast.args:
        _, _, ln, col = self.last_child().pars()

        return oneinfo(', *', fstloc(ln, col, ln, col))

    if ast.posonlyargs:
        _, _, ln, col = self.last_child().loc

        ln, col = next_find(lines, ln, col, self.end_ln, self.end_col, '/')  # must be there
        col += 1

        return oneinfo(', *', fstloc(ln, col, ln, col))

    loc = self.loc
    prefix = ' *' if (parent := self.parent) and parent.a.__class__ is Lambda else '*'

    return oneinfo(prefix, loc)

def _one_info_arguments_kw_defaults(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    arg = self.a.kwonlyargs[idx]

    if ann := arg.annotation:
        _, _, ln, col = ann.f.pars()
        prefix = ' = '

    else:
        ln, col, _, _ = arg.f.loc
        col += len(arg.arg)
        prefix = '='

    if default := self.a.kw_defaults[idx]:
        _, _, end_ln, end_col = default.f.pars()

    else:
        end_ln = ln
        end_col = col

    return oneinfo(prefix, fstloc(ln, col, end_ln, end_col))

def _one_info_arguments_kwarg(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a

    if kwarg := ast.kwarg:  # delete location
        kwargf = kwarg.f

        if not (prev := kwargf.prev()):
            if not (parent := self.parent) or parent.a.__class__ is not Lambda:
                return oneinfo('', self.loc)

            ln, col, _, _ = parent.loc

            return oneinfo('', fstloc(ln, col + 6, self.end_ln, self.end_col))

        if not (
            ast.posonlyargs
            and (
                (n := prev.pfield.name) == 'posonlyargs'
                or (
                    n == 'defaults'
                    and prev.prev().pfield.name == 'posonlyargs'
        ))):
            _, _, ln, col = prev.pars()

        else:
            ln, col = next_find(self.root._lines, prev.end_ln, prev.end_col, kwargf.ln, kwargf.col, '/')  # must be there
            col += 1

        return oneinfo('', fstloc(ln, col, self.end_ln, self.end_col))

    # insert location

    loc = self.loc

    if self.is_empty_arguments():
        prefix = ' **' if (parent := self.parent) and parent.a.__class__ is Lambda else '**'

        return oneinfo(prefix, loc)

    _, _, end_ln, end_col = loc

    last = self.last_child()

    if not (
        ast.posonlyargs
        and (
            (n := last.pfield.name) == 'posonlyargs'
            or (
                n == 'defaults'
                and last.prev().pfield.name == 'posonlyargs'
    ))):
        _, _, ln, col = last.pars()

    else:
        ln, col = next_find(self.root._lines, last.end_ln, last.end_col, end_ln, end_col, '/')  # must be there
        col += 1

    return oneinfo(', **', fstloc(ln, col, end_ln, end_col))

def _one_info_arg_annotation(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return oneinfo(': ', fstloc((loc := self.loc).ln, loc.col + len(self.a.arg), self.end_ln, self.end_col))

def _one_info_keyword_arg(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a
    end_ln, end_col, _, _ = ast.value.f.pars()
    ln, col, _, _ = self.loc
    arg_end_col = col + 2 if ast.arg is None else re_identifier.match(self.root._lines[ln], col).end() # must be there

    return oneinfo('', fstloc(ln, col, end_ln, end_col), fstloc(ln, col, ln, arg_end_col), '=', '**')

def _one_info_alias_asname(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a
    ln, col, end_ln, end_col = self.loc
    loc_insdel = fstloc(ln, col + len(ast.name), end_ln, end_col)

    if (asname := ast.asname) is None:
        loc_prim = None

    else:
        lines = self.root._lines
        ln, col = next_find(lines, ln, col, end_ln, end_col, 'as')  # skip the 'as'
        ln, col = next_find(lines, ln, col + 2, end_ln, end_col, asname)  # must be there
        loc_prim = fstloc(ln, col, ln, col + len(asname))

    return oneinfo(' as ', loc_insdel, loc_prim)

def _one_info_withitem_optional_vars(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col = self.a.context_expr.f.pars()

    if optional_vars := self.a.optional_vars:
        _, _, end_ln, end_col = optional_vars.f.pars()
    else:
        end_ln = ln
        end_col = col

    return oneinfo(' as ', fstloc(ln, col, end_ln, end_col))

def _one_info_match_case_guard(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    _, _, ln, col = self.a.pattern.f.pars()
    _, _, end_ln, end_col = self._loc_block_header_end()

    return oneinfo(' if ', fstloc(ln, col, end_ln, end_col - 1))

def _one_info_MatchMapping_rest(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a
    ln, col, end_ln, end_col = self.loc
    end_col -= 1

    if patterns := ast.patterns:
        _, _, ln, col = patterns[-1].f.pars()
        prefix = ', **'

    else:
        col += 1
        prefix = '**'

    if (rest := ast.rest) is None:
        loc_prim = None
    else:
        rest_ln, rest_col = next_find(self.root._lines, ln, col, end_ln, end_col, rest)
        loc_prim = fstloc(rest_ln, rest_col, rest_ln, rest_col + len(rest))

    return oneinfo(prefix, fstloc(ln, col, end_ln, end_col), loc_prim)

def _one_info_MatchClass_kwd_attrs(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a
    lines = self.root._lines
    kwd_patterns = ast.kwd_patterns

    if idx % len(kwd_patterns):  # could be negative
        _, _, ln, col = kwd_patterns[idx - 1].f.loc
    elif patterns := ast.patterns:
        _, _, ln, col = patterns[-1].f.loc
    else:
        _, _, ln, col = ast.cls.f.loc

    end_ln, end_col = prev_find(lines, ln, col, *kwd_patterns[idx].f.loc[:2], '=')  # must be there
    ln, col, src = prev_frag(lines, ln, col, end_ln, end_col)  # must be there
    end_col = col + len(src)
    col = end_col - len(src.lstrip('(,'))

    return oneinfo('', None, fstloc(ln, col, ln, end_col))

def _one_info_MatchStar_name(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '*')

def _one_info_MatchAs_pattern(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a

    if (name := ast.name) is None:
        return _oneinfo_default  # cannot insert or delete because is wildcard '_'

    ln, col, end_ln, end_col = self.loc

    if (pattern := ast.pattern) is None:
        return oneinfo('', fstloc(ln, col, ln, col), None, ' as ')

    lines = self.root._lines
    as_ln, as_col = next_find(lines, *pattern.f.pars()[2:], end_ln, end_col, 'as')  # skip the 'as'
    end_ln, end_col = next_find(lines, as_ln, as_col + 2, end_ln, end_col, name)

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

def _one_info_MatchAs_name(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a
    ln, col, end_ln, end_col = self.loc

    if (pattern := ast.pattern) is None:
        prefix = ''

    else:
        prefix = 'as'
        lines = self.root._lines
        ln, col = next_find(lines, *pattern.f.pars()[2:], end_ln, end_col, 'as')  # skip the 'as'
        ln, col = next_find(lines, ln, col + 2, end_ln, end_col, ast.name or '_')

    return oneinfo(prefix, None, fstloc(ln, col, ln, end_col))

def _one_info_TypeVar_bound(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln = self.ln
    col = self.col + len(self.a.name)

    if bound := self.a.bound:
        _, _, end_ln, end_col = bound.f.pars()
    else:
        end_ln = ln
        end_col = col

    return oneinfo(': ', fstloc(ln, col, end_ln, end_col))

def _one_info_TypeVar_default_value(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if bound := self.a.bound:
        _, _, ln, col = bound.f.pars()
    else:
        ln = self.ln
        col = self.col + len(self.a.name)

    return oneinfo(' = ', fstloc(ln, col, self.end_ln, self.end_col))

def _one_info_ParamSpec_name(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '**')

def _one_info_ParamSpec_default_value(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    ln, col, src = next_find_re(self.root._lines, ln, col + 2, end_ln, end_col, re_identifier)  # + '**', identifier must be there

    return oneinfo(' = ', fstloc(ln, col + len(src), self.end_ln, self.end_col))

def _one_info_TypeVarTuple_default_value(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ln, col, end_ln, end_col = self.loc
    ln, col, src = next_find_re(self.root._lines, ln, col + 1, end_ln, end_col, re_identifier)  # + '*', identifier must be there

    return oneinfo(' = ', fstloc(ln, col + len(src), self.end_ln, self.end_col))

def _one_info_TypeVarTuple_name(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    return _one_info_identifier_required(self, static, idx, field, '*')

@pyver(lt=12)
def _one_info_format_spec(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    raise NotImplementedError('this is only implemented on python version 3.12 and above')

@pyver(ge=12)
def _one_info_format_spec(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    if fspec := self.a.format_spec:
        return oneinfo(':', fspec.f.loc)

    _, _, end_ln, end_col = self.loc
    end_col -= 1

    return oneinfo(':', fstloc(end_ln, end_col, end_ln, end_col))

@pyver(lt=12)
def _one_info_conversion(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    raise NotImplementedError('this is only implemented on python version 3.12 and above')

@pyver(ge=12)
def _one_info_conversion(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    ast = self.a

    if fspec := ast.format_spec:
        end_ln, end_col, _, _ = fspec.f.loc
    else:
        _, _, end_ln, end_col = self.loc
        end_col -= 1

    if ast.conversion == -1:
        return oneinfo('!', fstloc(end_ln, end_col, end_ln, end_col))

    _, _, ln, col = ast.value.f.loc

    if not (prev := prev_find(self.root._lines, ln, col, end_ln, end_col, '!')):  # may not be there if conversion is implicit due to =
        return oneinfo('!', fstloc(end_ln, end_col, end_ln, end_col))

    ln, col = prev

    return oneinfo('', fstloc(ln, col, end_ln, end_col))

def _one_info_loc_prim_self(self: fst.FST, static: onestatic, idx: int | None, field: str) -> oneinfo:
    """This exists so that put raw can get location for put to `Constant.value` and `MatchSingleton.value`."""

    return oneinfo('', None, self.loc)


_PUT_ONE_HANDLERS = {
    (Module, 'body'):                     (True,  None, None),  # stmt*  - all stmtlikes have sliceable True and handler None to force always use slice operation (because of evil semicolons handled there)
    (Interactive, 'body'):                (True,  None, None),  # stmt*
    (Expression, 'body'):                 (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (FunctionDef, 'decorator_list'):      (True,  _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (FunctionDef, 'name'):                (False, _put_one_identifier_required, _onestatic_FunctionDef_name),  # identifier
    (FunctionDef, 'type_params'):         (True,  _put_one_exprlike_required, _onestatic_type_param_required),  # type_param*
    (FunctionDef, 'args'):                (False, _put_one_FunctionDef_arguments, _onestatic_arguments_required),  # arguments
    (FunctionDef, 'returns'):             (False, _put_one_exprlike_optional, _onestatic_FunctionDef_returns),  # expr?
    (FunctionDef, 'body'):                (True,  None, None),  # stmt*
    (AsyncFunctionDef, 'decorator_list'): (True,  _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (AsyncFunctionDef, 'name'):           (False, _put_one_identifier_required, _onestatic_FunctionDef_name),  # identifier
    (AsyncFunctionDef, 'type_params'):    (True,  _put_one_exprlike_required, _onestatic_type_param_required),  # type_param*
    (AsyncFunctionDef, 'args'):           (False, _put_one_FunctionDef_arguments, _onestatic_arguments_required),  # arguments
    (AsyncFunctionDef, 'returns'):        (False, _put_one_exprlike_optional, _onestatic_FunctionDef_returns),  # expr?
    (AsyncFunctionDef, 'body'):           (True,  None, None),  # stmt*
    (ClassDef, 'decorator_list'):         (True,  _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (ClassDef, 'name'):                   (False, _put_one_identifier_required, onestatic(_one_info_ClassDef_name, _restrict_default, code_as=code_as_identifier)),  # identifier
    (ClassDef, 'type_params'):            (True,  _put_one_exprlike_required, _onestatic_type_param_required),  # type_param*
    (ClassDef, 'bases'):                  (True,  _put_one_ClassDef_bases, _onestatic_expr_required_arglike),  # expr*
    (ClassDef, 'keywords'):               (True,  _put_one_ClassDef_keywords, _onestatic_keyword_required),  # keyword*
    (ClassDef, 'body'):                   (True,  None, None),  # stmt*
    (ClassDef, '_bases'):                 (True,  _put_one_arglikes, _onestatic__arglike_required),  # (expr|keyword)*
    (Return, 'value'):                    (False, _put_one_exprlike_optional, onestatic(_one_info_Return_value, _restrict_fmtval_slice)),  # expr?
    (Delete, 'targets'):                  (True,  _put_one_exprlike_required, onestatic(_one_info_exprlike_required, is_valid_del_target, ctx_cls=Del)),  # expr*
    (Assign, 'targets'):                  (True,  _put_one_exprlike_required, _onestatic_target),  # expr*
    (Assign, 'value'):                    (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr  - python technically allows Starred for parse but is not compilable, should we allow it as well for consistency?
    (TypeAlias, 'name'):                  (False, _put_one_exprlike_required, _onestatic_target_Name),  # expr
    (TypeAlias, 'type_params'):           (True,  _put_one_exprlike_required, _onestatic_type_param_required),  # type_param*
    (TypeAlias, 'value'):                 (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (AugAssign, 'target'):                (False, _put_one_exprlike_required, _onestatic_target_single),  # expr
    (AugAssign, 'op'):                    (False, _put_one_op, onestatic(None, code_as=code_as_operator)),  # operator
    (AugAssign, 'value'):                 (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (AnnAssign, 'target'):                (False, _put_one_AnnAssign_target, _onestatic_target_single),  # expr
    (AnnAssign, 'annotation'):            (False, _put_one_exprlike_required, onestatic(_one_info_exprlike_required, _restrict_default)),  # expr  - exclude [Lambda, Yield, YieldFrom, Await, NamedExpr]?
    (AnnAssign, 'value'):                 (False, _put_one_exprlike_optional, onestatic(_one_info_AnnAssign_value, _restrict_fmtval_slice)),  # expr?
    (AnnAssign, 'simple'):                (False, _put_one_AnnAssign_simple, onestatic(None, int)),  # int
    (For, 'target'):                      (False, _put_one_exprlike_required, _onestatic_target),  # expr
    (For, 'iter'):                        (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (For, 'body'):                        (True,  None, None),  # stmt*
    (For, 'orelse'):                      (True,  None, None),  # stmt*
    (AsyncFor, 'target'):                 (False, _put_one_exprlike_required, _onestatic_target),  # expr
    (AsyncFor, 'iter'):                   (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (AsyncFor, 'body'):                   (True,  None, None),  # stmt*
    (AsyncFor, 'orelse'):                 (True,  None, None),  # stmt*
    (While, 'test'):                      (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (While, 'body'):                      (True,  None, None),  # stmt*
    (While, 'orelse'):                    (True,  None, None),  # stmt*
    (If, 'test'):                         (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (If, 'body'):                         (True,  None, None),  # stmt*
    (If, 'orelse'):                       (True,  None, None),  # stmt*
    (With, 'items'):                      (True,  _put_one_with_items, _onestatic_withitem_required),  # withitem*
    (With, 'body'):                       (True,  None, None),  # stmt*
    (AsyncWith, 'items'):                 (True,  _put_one_with_items, _onestatic_withitem_required),  # withitem*
    (AsyncWith, 'body'):                  (True,  None, None),  # stmt*
    (Match, 'subject'):                   (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Match, 'cases'):                     (True,  None, None),  # match_case*
    (Raise, 'exc'):                       (False, _put_one_exprlike_optional, onestatic(_one_info_Raise_exc, _restrict_default)),  # expr?
    (Raise, 'cause'):                     (False, _put_one_exprlike_optional, onestatic(_one_info_Raise_cause, _restrict_default)),  # expr?
    (Try, 'body'):                        (True,  None, None),  # stmt*
    (Try, 'handlers'):                    (True,  None, None),  # excepthandler*
    (Try, 'orelse'):                      (True,  None, None),  # stmt*
    (Try, 'finalbody'):                   (True,  None, None),  # stmt*
    (TryStar, 'body'):                    (True,  None, None),  # stmt*
    (TryStar, 'handlers'):                (True,  None, None),  # excepthandler*
    (TryStar, 'orelse'):                  (True,  None, None),  # stmt*
    (TryStar, 'finalbody'):               (True,  None, None),  # stmt*
    (Assert, 'test'):                     (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Assert, 'msg'):                      (False, _put_one_exprlike_optional, onestatic(_one_info_Assert_msg, _restrict_default)),  # expr?
    (Import, 'names'):                    (True,  _put_one_Import_names, onestatic(_one_info_exprlike_required, _restrict_default, code_as=code_as_Import_name)),  # alias*
    (ImportFrom, 'module'):               (False, _put_one_identifier_optional, onestatic(_one_info_ImportFrom_module, _restrict_default, code_as=code_as_identifier_dotted)),  # identifier? (dotted)
    (ImportFrom, 'names'):                (True,  _put_one_ImportFrom_names, onestatic(_one_info_exprlike_required, _restrict_default, code_as=code_as_ImportFrom_name)),  # alias*
    (ImportFrom, 'level'):                (False, _put_one_ImportFrom_level, None),  # int?
    (Global, 'names'):                    (True,  _put_one_identifier_required, _onestatic_Global_Nonlocal_names),  # identifier*
    (Nonlocal, 'names'):                  (True,  _put_one_identifier_required, _onestatic_Global_Nonlocal_names),  # identifier*
    (Expr, 'value'):                      (False, _put_one_exprlike_required, _onestatic_expr_required_w_starred),  # expr
    (BoolOp, 'op'):                       (False, _put_one_BoolOp_op, onestatic(None)),  # boolop  - very special case gets handled entirely in _put_one_BoolOp_op
    (BoolOp, 'values'):                   (True,  _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (NamedExpr, 'target'):                (False, _put_one_exprlike_required, _onestatic_target_Name),  # expr
    (NamedExpr, 'value'):                 (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (BinOp, 'left'):                      (False, _put_one_BinOp_left_right, _onestatic_expr_required),  # expr
    (BinOp, 'op'):                        (False, _put_one_op, onestatic(None, code_as=code_as_operator)),  # operator
    (BinOp, 'right'):                     (False, _put_one_BinOp_left_right, _onestatic_expr_required),  # expr
    (UnaryOp, 'op'):                      (False, _put_one_op, onestatic(None, code_as=code_as_unaryop)),  # unaryop
    (UnaryOp, 'operand'):                 (False, _put_one_UnaryOp_operand, _onestatic_expr_required),  # expr
    (Lambda, 'args'):                     (False, _put_one_Lambda_arguments, _onestatic_arguments_lambda_required),  # arguments
    (Lambda, 'body'):                     (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (IfExp, 'body'):                      (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (IfExp, 'test'):                      (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (IfExp, 'orelse'):                    (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Dict, 'keys'):                       (False, _put_one_Dict_keys, onestatic(_one_info_Dict_key, _restrict_default)),  # expr*
    (Dict, 'values'):                     (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (Dict, '_all'):                       (True,  None, None),  # expr*
    (Set, 'elts'):                        (True,  _put_one_exprlike_required, _onestatic_expr_required_w_starred),  # expr*
    (ListComp, 'elt'):                    (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (ListComp, 'generators'):             (True,  _put_one_exprlike_required, _onestatic_comprehension_required),  # comprehension*
    (SetComp, 'elt'):                     (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (SetComp, 'generators'):              (True,  _put_one_exprlike_required, _onestatic_comprehension_required),  # comprehension*
    (DictComp, 'key'):                    (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (DictComp, 'value'):                  (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (DictComp, 'generators'):             (True,  _put_one_exprlike_required, _onestatic_comprehension_required),  # comprehension*
    (GeneratorExp, 'elt'):                (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (GeneratorExp, 'generators'):         (True,  _put_one_exprlike_required, _onestatic_comprehension_required),  # comprehension*
    (Await, 'value'):                     (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Yield, 'value'):                     (False, _put_one_exprlike_optional, onestatic(_one_info_Yield_value, _restrict_fmtval_slice)),  # expr?
    (YieldFrom, 'value'):                 (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Compare, 'left'):                    (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Compare, 'ops'):                     (False, _put_one_op, onestatic(None, code_as=code_as_cmpop)),  # cmpop*
    (Compare, 'comparators'):             (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (Compare, '_all'):                    (True,  _put_one_Compare__all, _onestatic_expr_required),  # expr*
    (Call, 'func'):                       (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Call, 'args'):                       (True,  _put_one_Call_args, _onestatic_expr_required_arglike),  # expr*
    (Call, 'keywords'):                   (True,  _put_one_Call_keywords, _onestatic_keyword_required),  # keyword*
    (Call, '_args'):                      (True,  _put_one_arglikes, _onestatic__arglike_required),  # (expr|keyword)*
    (FormattedValue, 'value'):            (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (FormattedValue, 'conversion'):       (False, _put_one_NOT_IMPLEMENTED_YET_12, onestatic(_one_info_conversion, Constant)),  # int  # onestatic only here for info for raw put, Constant must be str
    (FormattedValue, 'format_spec'):      (False, _put_one_NOT_IMPLEMENTED_YET_12, onestatic(_one_info_format_spec, JoinedStr)),  # expr?  # onestatic only here for info for raw put
    (Interpolation, 'value'):             (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Interpolation, 'str'):               (False, _put_one_NOT_IMPLEMENTED_YET_14, onestatic(None, str)),  # constant
    (Interpolation, 'conversion'):        (False, _put_one_NOT_IMPLEMENTED_YET_14, onestatic(_one_info_conversion, Constant)),  # int  # onestatic only here for info for raw put, Constant must be str
    (Interpolation, 'format_spec'):       (False, _put_one_NOT_IMPLEMENTED_YET_14, onestatic(_one_info_format_spec, JoinedStr)),  # expr?  # onestatic only here for info for raw put
    (JoinedStr, 'values'):                (True,  _put_one_NOT_IMPLEMENTED_YET_12, None),  # expr*
    (TemplateStr, 'values'):              (True,  _put_one_NOT_IMPLEMENTED_YET_12, None),  # expr*
    (Constant, 'value'):                  (False, _put_one_Constant_value, onestatic(_one_info_loc_prim_self, constant)),  # constant
    (Constant, 'kind'):                   (False, _put_one_Constant_kind, None),  # string?
    (Attribute, 'value'):                 (False, _put_one_Attribute_value, _onestatic_expr_required),  # expr
    (Attribute, 'attr'):                  (False, _put_one_identifier_required, onestatic(_one_info_Attribute_attr, _restrict_default, code_as=code_as_identifier)),  # identifier
    (Attribute, 'ctx'):                   (False, _put_one_ctx, _onestatic_ctx),  # expr_context
    (Subscript, 'value'):                 (False, _put_one_Subscript_value, _onestatic_expr_required),  # expr
    (Subscript, 'slice'):                 (False, _put_one_Subscript_slice, onestatic(_one_info_exprlike_required, _restrict_fmtval_starred, code_as=code_as_expr_slice)),  # expr
    (Subscript, 'ctx'):                   (False, _put_one_ctx, _onestatic_ctx),  # expr_context
    (Starred, 'value'):                   (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (Starred, 'ctx'):                     (False, _put_one_ctx, _onestatic_ctx),  # expr_context
    (Name, 'id'):                         (False, _put_one_identifier_required, _onestatic_identifier_required),  # identifier
    (Name, 'ctx'):                        (False, _put_one_ctx, _onestatic_ctx),  # expr_context
    (List, 'elts'):                       (True,  _put_one_List_elts, _onestatic_expr_required_w_starred),  # expr*
    (List, 'ctx'):                        (False, _put_one_ctx, _onestatic_ctx),  # expr_context
    (Tuple, 'elts'):                      (True,  _put_one_Tuple_elts, onestatic(_one_info_exprlike_required, _restrict_fmtval, code_as=code_as_Tuple_elt)),  # expr*  - special handling because Tuples can contain Slices in an unparenthesized .slice field
    (Tuple, 'ctx'):                       (False, _put_one_ctx, _onestatic_ctx),  # expr_context
    (Slice, 'lower'):                     (False, _put_one_exprlike_optional, _onestatic_Slice_lower),  # expr?
    (Slice, 'upper'):                     (False, _put_one_exprlike_optional, _onestatic_Slice_upper),  # expr?
    (Slice, 'step'):                      (False, _put_one_exprlike_optional, _onestatic_Slice_step),  # expr?
    (comprehension, 'target'):            (False, _put_one_exprlike_required, _onestatic_target),  # expr
    (comprehension, 'iter'):              (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (comprehension, 'ifs'):               (True,  _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (comprehension, 'is_async'):          (False, _put_one_comprehension_is_async, None),  # int
    (ExceptHandler, 'type'):              (False, _put_one_exprlike_optional, onestatic(_one_info_ExceptHandler_type, _restrict_default)),  # expr?
    (ExceptHandler, 'name'):              (False, _put_one_ExceptHandler_name, onestatic(_one_info_ExceptHandler_name, _restrict_default, code_as=code_as_identifier)),  # identifier?
    (ExceptHandler, 'body'):              (True,  None, None),  # stmt*
    (arguments, 'posonlyargs'):           (False, _put_one_arg, _onestatic_arg_required),  # arg*
    (arguments, 'args'):                  (False, _put_one_arg, _onestatic_arg_required),  # arg*
    (arguments, 'defaults'):              (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (arguments, 'vararg'):                (False, _put_one_exprlike_optional, onestatic(_one_info_arguments_vararg, _restrict_default, code_as=code_as_arg)),  # arg?
    (arguments, 'kwonlyargs'):            (False, _put_one_arg, _onestatic_arg_required),  # arg*
    (arguments, 'kw_defaults'):           (False, _put_one_exprlike_optional, onestatic(_one_info_arguments_kw_defaults, _restrict_default)),  # expr*
    (arguments, 'kwarg'):                 (False, _put_one_exprlike_optional, onestatic(_one_info_arguments_kwarg, _restrict_default, code_as=code_as_arg)),  # arg?
    (arguments, '_all'):                  (True, False, False),  # arguments
    (arg, 'arg'):                         (False, _put_one_identifier_required, _onestatic_identifier_required),  # identifier
    (arg, 'annotation'):                  (False, _put_one_arg_annotation, onestatic(_one_info_arg_annotation, _restrict_default)),  # expr?  - exclude [Lambda, Yield, YieldFrom, Await, NamedExpr]?
    (keyword, 'arg'):                     (False, _put_one_keyword_arg, onestatic(_one_info_keyword_arg, _restrict_default, code_as=code_as_identifier)),  # identifier?
    (keyword, 'value'):                   (False, _put_one_exprlike_required, _onestatic_expr_required),  # expr
    (alias, 'name'):                      (False, _put_one_identifier_required, onestatic(_one_info_identifier_alias, _restrict_default, code_as=code_as_identifier_alias)),  # identifier  - alias star or dotted not valid for all uses but being general here (and lazy, don't feel like checking parent)
    (alias, 'asname'):                    (False, _put_one_identifier_optional, onestatic(_one_info_alias_asname, _restrict_default, code_as=code_as_identifier)),  # identifier?
    (withitem, 'context_expr'):           (False, _put_one_withitem_context_expr, _onestatic_expr_required),  # expr
    (withitem, 'optional_vars'):          (False, _put_one_withitem_optional_vars, onestatic(_one_info_withitem_optional_vars, (Name, Tuple, List, Attribute, Subscript), ctx_cls=Store)),  # expr?
    (match_case, 'pattern'):              (False, _put_one_pattern, _onestatic_pattern_required),  # pattern
    (match_case, 'guard'):                (False, _put_one_exprlike_optional, onestatic(_one_info_match_case_guard, _restrict_default)),  # expr?
    (match_case, 'body'):                 (True,  None, None),  # stmt*
    # (MatchValue, 'value'):                (False, _put_one_MatchValue_value, onestatic(_one_info_exprlike_required, _is_valid_MatchValue_value)),  # expr
    (MatchValue, 'value'):                (False, _put_one_exprlike_required, onestatic(_one_info_exprlike_required, _is_valid_MatchValue_value)),  # expr
    (MatchSingleton, 'value'):            (False, _put_one_constant, onestatic(_one_info_loc_prim_self, (bool, NoneType))),  # constant
    (MatchSequence, 'patterns'):          (True,  _put_one_pattern, _onestatic_pattern_required),  # pattern*
    (MatchMapping, 'keys'):               (False, _put_one_exprlike_required, onestatic(_one_info_exprlike_required, _is_valid_MatchMapping_key)),  # expr*  Ops for `-1` or `2+3j`
    (MatchMapping, 'patterns'):           (False, _put_one_pattern, _onestatic_pattern_required),  # pattern*
    (MatchMapping, 'rest'):               (False, _put_one_identifier_optional, onestatic(_one_info_MatchMapping_rest, _restrict_default, code_as=code_as_identifier)),  # identifier?
    (MatchMapping, '_all'):               (True,  None, None),  # expr*
    (MatchClass, 'cls'):                  (False, _put_one_exprlike_required, onestatic(_one_info_exprlike_required, _is_valid_MatchClass_cls)),  # expr
    (MatchClass, 'patterns'):             (True,  _put_one_pattern, _onestatic_pattern_required),  # pattern*
    (MatchClass, 'kwd_attrs'):            (False, _put_one_identifier_required, onestatic(_one_info_MatchClass_kwd_attrs, _restrict_default, code_as=code_as_identifier)),  # identifier*
    (MatchClass, 'kwd_patterns'):         (False, _put_one_pattern, _onestatic_pattern_required),  # pattern*
    (MatchStar, 'name'):                  (False, _put_one_MatchStar_name, onestatic(_one_info_MatchStar_name, _restrict_default, code_as=code_as_identifier)),  # identifier?
    (MatchAs, 'pattern'):                 (False, _put_one_MatchAs_pattern, onestatic(_one_info_MatchAs_pattern, _restrict_default, code_as=code_as_pattern)),  # pattern?
    (MatchAs, 'name'):                    (False, _put_one_MatchAs_name, onestatic(_one_info_MatchAs_name, _restrict_default, code_as=code_as_identifier)),  # identifier?
    (MatchOr, 'patterns'):                (True,  _put_one_pattern, _onestatic_pattern_required),  # pattern*
    (TypeVar, 'name'):                    (False, _put_one_identifier_required, _onestatic_identifier_required),  # identifier
    (TypeVar, 'bound'):                   (False, _put_one_exprlike_optional, onestatic(_one_info_TypeVar_bound, _restrict_default)),  # expr?
    (TypeVar, 'default_value'):           (False, _put_one_exprlike_optional, onestatic(_one_info_TypeVar_default_value, _restrict_default)),  # expr?
    (ParamSpec, 'name'):                  (False, _put_one_identifier_required, onestatic(_one_info_ParamSpec_name, _restrict_default, code_as=code_as_identifier)),  # identifier
    (ParamSpec, 'default_value'):         (False, _put_one_exprlike_optional, onestatic(_one_info_ParamSpec_default_value, _restrict_default)),  # expr?
    (TypeVarTuple, 'name'):               (False, _put_one_identifier_required, onestatic(_one_info_TypeVarTuple_name, _restrict_default, code_as=code_as_identifier)),  # identifier
    (TypeVarTuple, 'default_value'):      (False, _put_one_exprlike_optional, onestatic(_one_info_TypeVarTuple_default_value, _restrict_fmtval_slice)),  # expr?

    (Module, '_body'):                    (True, None, None),  # stmt*  - without docstr
    (Interactive, '_body'):               (True, None, None),  # stmt*
    (FunctionDef, '_body'):               (True, None, None),  # stmt*
    (AsyncFunctionDef, '_body'):          (True, None, None),  # stmt*
    (ClassDef, '_body'):                  (True, None, None),  # stmt*
    (For, '_body'):                       (True, None, None),  # stmt*
    (AsyncFor, '_body'):                  (True, None, None),  # stmt*
    (While, '_body'):                     (True, None, None),  # stmt*
    (If, '_body'):                        (True, None, None),  # stmt*
    (With, '_body'):                      (True, None, None),  # stmt*
    (AsyncWith, '_body'):                 (True, None, None),  # stmt*
    (Try, '_body'):                       (True, None, None),  # stmt*
    (TryStar, '_body'):                   (True, None, None),  # stmt*
    (ExceptHandler, '_body'):             (True, None, None),  # stmt*
    (match_case, '_body'):                (True, None, None),  # stmt*

    (_ExceptHandlers, 'handlers'):        (True, None, None),  # stmt*,  # ExceptHandler*
    (_match_cases, 'cases'):              (True, None, None),  # stmt*,  # match_case*
    (_Assign_targets, 'targets'):         (True, _put_one_exprlike_required, _onestatic_target),  # expr*
    (_decorator_list, 'decorator_list'):  (True, _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (_arglikes, 'arglikes'):              (True, _put_one__arglikes_arglikes, _onestatic__arglike_required),  # (expr|keyword)*
    (_comprehensions, 'generators'):      (True, _put_one_exprlike_required, _onestatic_comprehension_required),  # comprehension*
    (_comprehension_ifs, 'ifs'):          (True, _put_one_exprlike_required, _onestatic_expr_required),  # expr*
    (_aliases, 'names'):                  (True, _put_one_exprlike_required, _onestatic_alias_required),  # alias*
    (_withitems, 'items'):                (True, _put_one_exprlike_required, _onestatic_withitem_required),  # withitem*
    (_type_params, 'type_params'):        (True, _put_one_exprlike_required, _onestatic_type_param_required),  # type_param*


    # NOT DONE:
    # =========

    # (Module, 'type_ignores'):             (),  # type_ignore*

    # (FunctionType, 'argtypes'):           (),  # expr*
    # (FunctionType, 'returns'):            (),  # expr
    # (TypeIgnore, 'lineno'):               (),  # int
    # (TypeIgnore, 'tag'):                  (),  # string

    # (FunctionDef, 'type_comment'):        (),  # string?
    # (AsyncFunctionDef, 'type_comment'):   (),  # string?
    # (Assign, 'type_comment'):             (),  # string?
    # (For, 'type_comment'):                (),  # string?
    # (AsyncFor, 'type_comment'):           (),  # string?
    # (With, 'type_comment'):               (),  # string?
    # (AsyncWith, 'type_comment'):          (),  # string?
    # (arg, 'type_comment'):                (),  # string?
}


# ----------------------------------------------------------------------------------------------------------------------
# put raw

def _put_one_raw(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    child: AST | list[AST],
    static: onestatic | None,
    options: Mapping[str, Any],
) -> fst.FST | None:
    if code is None:
        raise ValueError('cannot delete in raw put')

    to = options.get('to')

    if to is not None and not isinstance(to, fst.FST):
        raise ValueError(f"expecting FST for 'to' option, got {to.__class__.__name__}")

    put_lines = _code_as_lines(code)

    ast = self.a
    ast_cls = ast.__class__
    root = self.root
    pars = bool(fst.FST.get_option('pars', options))
    loc = None

    if field.startswith('_'):  # special case field
        if field == '_body':
            field = 'body'
            child = ast.body
            idx = fixup_one_index(len(child), idx, self.has_docstr)

        elif ast_cls is Dict:
            static = _PUT_ONE_HANDLERS[(ast_cls, 'keys')][-1]
            field = 'keys'
            child = ast.keys
            body2 = ast.values
            idx = fixup_one_index(len(child), idx)
            loc = self._loc_maybe_key(idx, pars, child, body2)  # maybe the key is a '**'

            # if not to:  # does not currently get here without a `to` in normal operation because in that case it is handled by slice operations in _put_one()
            #     to = body2[idx].f

        elif ast_cls is Compare:
            idx, field, child = _params_Compare(self, idx)

            if not to:
                to = (child if idx is None else child[idx]).f

        elif ast_cls in (Call, ClassDef):
            child = self._cached_arglikes()
            idx = fixup_one_index(len(child), idx)

        elif ast_cls is arguments:
            child = self._cached_allargs()
            idx = fixup_one_index(len(child), idx)

            # if not to:  # does not currently get here without a `to`
            #     if (f := child.f.next()) and f.pfield.name in ('defaults', 'kw_defaults'):
            #         to = f

        elif ast_cls is MatchMapping:
            static = _PUT_ONE_HANDLERS[(ast_cls, 'keys')][-1]
            child = ast.keys
            body2 = ast.patterns
            len_child = len(child)
            idx = fixup_one_index(len_child + (1 if ast.rest else 0), idx)

            if idx < len_child:  # rest
                field = 'keys'
                loc = child[idx].f.loc  # these cannot have pars

                # if not to:  # does not currently get here without a `to`
                #     to = body2[idx].f

            else:  # rest
                ln, col, end_ln, end_col = self._loc_MatchMapping_rest()

                if idx:
                    _, _, prev_ln, prev_col = body2[idx - 1].f.loc
                else:
                    prev_ln, prev_col, _, _ = self.loc

                ln, col = prev_find(root._lines, prev_ln, prev_col, ln, col, '**')  # '**' must be there

                loc = fstloc(ln, col, end_ln, end_col)
                field = 'rest'
                child = ast.rest
                idx = None

        else:
            raise RuntimeError(f'should not get here, unknown virtual field {field!r}')  # pragma: no cover

    child, idx = _validate_put(self, code, idx, field, child)

    if child is None and loc is None:
        if field == 'keys':  # only Dict and MatchMapping have this, will not have been processed as a special field above
            loc = self._loc_maybe_key(idx, pars, ast.keys, ast.values if ast_cls is Dict else ast.patterns)
        elif ast_cls is not MatchSingleton:  # breaking convention as always, `None` in a MatchSingleton.value is a value, not the absence of a value
            raise ValueError('cannot insert in raw put')

    childf = child.f if isinstance(child, AST) else None

    if to is childf:
        to = None

    # from location (if not gotten already for Dict or MatchMapping key)

    if ast_cls is Lambda and child.__class__ is arguments and childf.is_empty_arguments():  # SUPER SPECIAL CASE, adding arguments to lambda without them, may need to prepend a space to source being put
        if not put_lines[0][:1].isspace():
            put_lines[0] =  ' ' + put_lines[0]

    if loc is None:
        if childf:
            if (loc := childf.pars(shared=False) if pars else childf.bloc) is None:
                pass  # noop
            elif not pars and childf._is_solo_call_arg_genexp() and (non_shared_loc := childf.pars(shared=False)) > loc:  # if loc includes `arguments` parentheses shared with solo GeneratorExp call arg then need to leave those in place
                loc = non_shared_loc

        elif info := (static and (getinfo := static.getinfo) and getinfo(self, static, idx, field)):  # primitive, maybe its an identifier
            loc = info.loc_prim

        if loc is None:
            raise ValueError('cannot determine location to put to')

    # to location (if different) and appropriate parent

    if not to:
        parent = self
        to_loc = loc

    else:
        if root is not to.root:
            raise ValueError("'to' must be part of same tree")

        if (to_loc := to.pars(shared=False) if pars else to.bloc) is None:
            raise ValueError("'to' node must have a location")

        if not pars and to._is_solo_call_arg_genexp() and (non_shared_loc := to.pars(shared=False)) > to_loc:  # solo GeneratorExp argument in Call which shares parentheses
            to_loc = non_shared_loc

        if to_loc[2:] < loc[:2]:  # if END of 'to' node comes before START of from node then can't do it
            raise ValueError("'to' node must follow self")

        self_path = root.child_path(self)  # technically should be root.child_path(childf)[:-1] but child may be identifier so get path directly to self which is parent and doesn't need the [:-1]
        to_path = root.child_path(to)[:-1]
        path = list(p for p, _ in takewhile(lambda st: st[0] == st[1], zip(self_path, to_path, strict=False)))
        parent = root.child_from_path(path)

    # do it

    ln, col, _, _ = loc
    _, _, end_ln, end_col = to_loc

    end_ln, end_col = parent._reparse_raw(put_lines, ln, col, end_ln, end_col)

    return root.find_in_loc(ln, col, end_ln, end_col)  # parent should stay same MOST of the time, `root` instead of `self` because some changes may propagate farther up the tree, like 'elif' -> 'else'


# ----------------------------------------------------------------------------------------------------------------------
# private FST class methods

def _put_one(
    self: fst.FST,
    code: _PutOneCode,
    idx: int | None,
    field: str,
    options: Mapping[str, Any] = {},
    ret_child: bool = True
) -> fst.FST | None:  # -> child or reparsed child or self or reparsed self or could disappear due to raw
    """Put new, replace or delete a node (or limited non-node) to a field of `self`.

    **Parameters:**
    - `code`: The code to put in the form of an `FST`, an `AST`, a string of source or a list of lines of source. If
        is `None` then will attempt to remove optional field or delete node from a mutable body list of nodes using
        slice operations.
    - `idx`: The index in the body list of the field to put, or `None` if is a standalone node.
    - `field`: The `AST` field to modify.
    - `options`: See `FST.options()`.
    - `ret_child`: If `True` then this function returns the new child node if it was replaced or `None` if deleted or
        otherwise raw repared out. If `False` then attepmts to return `self` or a new `self` if was raw reparsed
        and `None` if disappeared due to that.

    **Returns:**
    - `FST | None`: New child or `self` if reparsed (and requested via `ret_self=True`) or `None` if deleted either
        intentionally or as a side-effect of raw reparse.
    """

    if code is self.root:  # don't allow own root to be put to self
        raise ValueError('circular put detected')
    if code.__class__ is fst.FST and not code.a:
        raise ValueError('this FST has already been consumed or deleted')

    ast = self.a
    child = getattr(self.a, field, None)
    to = options.get('to')

    sliceable, handler, static = _PUT_ONE_HANDLERS.get((ast.__class__, field), (False, None, None))

    if sliceable and (not handler or code is None) and not to:  # if deleting from a sliceable field without a 'to' parameter then delegate to slice operation, also all statementlikes and virtual fields (which have handler=None) and anything that is sliceable and does not have a handler
        start_at = 0

        # TODO; convert this logic to own func

        if not (is_virtual_field := field.startswith('_')):
            len_ = len(child)

        elif field == '_body':  # block stmtlike
            is_virtual_field = False
            field = 'body'
            len_ = len(self.a.body)
            start_at = self.has_docstr

        elif (keys := getattr(ast, 'keys', None)) is not None:  # Dict, MatchMapping
            len_ = len(keys) + (1 if getattr(self.a, 'rest', None) else 0)

        elif (ast_cls := ast.__class__) is Compare:
            len_ = len(ast.comparators) + 1

        elif ast_cls in (Call, ClassDef):  # '_args' or '_bases'
            len_ = len(getattr(ast, field[1:])) + len(ast.keywords)

        elif ast_cls is arguments:  # `arguments._all`
            len_ = len(ast.posonlyargs) + len(ast.args) + bool(ast.vararg) + len(ast.kwonlyargs) + bool(ast.kwarg)

        else:
            raise RuntimeError(f'should not get here, unknown virtual field {field!r}')  # pragma: no cover

        idx = fixup_one_index(len_, idx, start_at)  # we need to fixup index here explicitly to get an error if it is out of bounds because slice index fixups don't error but just clip to [0..len(body))

        new_self = self._put_slice(code, idx, idx + 1, field, True, options)  # MAYBE new self, or just old self

        if not ret_child:
            return new_self

        if code is None or new_self is None:
            return None

        if is_virtual_field:
            if keys is not None:  # Dict or MatchMapping
                return None

            assert ast_cls is arguments  # Compare and others are only in the outer block for a delete with code=None which exited after completing just above, otherwise Compare and others have handlers

            ast = new_self.a

            return [*ast.posonlyargs, *ast.args, *([a] if (a := ast.vararg) else ()), *ast.kwonlyargs,
                    *([a] if (a := ast.kwarg) else ())][idx].f  # we return only the arg portion even though it might have a default, but it will never be called expecting a return with a default because that would be a .replace() on a single combined arg+defualt element which never exists on its own

        try:
            return getattr(new_self.a, field)[idx].f  # may not be there due to removal of last element or raw reparsing of weird *(^$
        except IndexError:
            return None

    raw = fst.FST.get_option('raw', options)
    nonraw_exc = None

    if raw is not True:
        preserved_code = code.copy() if raw and code.__class__ is fst.FST else code  # attempt at put may be destructive so need to make a copy of an FST if raw fallback is a possibility on fail

        try:
            if to:
                raise NodeError(f"cannot put with 'to' to {self.a.__class__.__name__}.{field} without 'raw'")

            if not handler:  # came from the default to _PUT_ONE_HANDLERS.get() because otherwise all (cls,field) keys in the table should be either 'sliceable' or have a  handler
                raise NodeError(f"cannot {'delete' if code is None else 'replace'} {ast.__class__.__name__}.{field}")

            with self._modifying(field):
                child = handler(self, code, idx, field, child, static, options)

                return child if ret_child else self

        except (NodeError, SyntaxError, NotImplementedError) as exc:  # SyntaxError includes ParseError
            if not raw or (isinstance(exc, NodeError) and not exc.rawable):
                raise

            nonraw_exc = exc
            code = preserved_code

    with self._modifying(field, True):  # raw put, either explicit by raw=True or fallback by raw='auto'
        try:
            child = _put_one_raw(self, code, idx, field, child, static, options)

            if ret_child:
                return child

            return self if self.a else self.repath()

        except Exception as raw_exc:
            raw_exc.__context__ = nonraw_exc

            raise raw_exc
