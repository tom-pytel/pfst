"""Convert `Code` to `FST`, coercion happens here."""

# TODO: some coercions need simplification
# TODO: mixed usage of _set_field() and set field=None before full FST() build may be confusing, maybe simplify to first one?

from __future__ import annotations

from math import copysign
from types import NoneType
from typing import Any, Callable, Literal, Mapping, Union
from unicodedata import normalize

from . import fst

from .asttypes import (
    ASTS_LEAF_STMT,
    ASTS_LEAF_EXPR,
    ASTS_LEAF_EXPR_CONTEXT,
    ASTS_LEAF_PATTERN,
    ASTS_LEAF_STMT_OR_STMTMOD,
    ASTS_LEAF_TUPLE_LIST_OR_SET,
    ASTS_LEAF_TUPLE_OR_LIST,
    ASTS_LEAF_LIST_OR_SET,
    ASTS_LEAF_FTSTR_FMT_OR_SLICE,
    AST,
    Add,
    Attribute,
    BinOp,
    BitOr,
    Call,
    Constant,
    Del,
    Dict,
    ExceptHandler,
    Expr,
    Expression,
    FormattedValue,
    FunctionType,
    Interactive,
    Interpolation,
    List,
    Load,
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
    ParamSpec,
    Pass,
    Set,
    Slice,
    Starred,
    Store,
    Sub,
    Try,
    TryStar,
    TypeIgnore,
    TypeVar,
    TypeVarTuple,
    Tuple,
    UAdd,
    USub,
    UnaryOp,
    alias,
    arg,
    arguments,
    boolop,
    cmpop,
    comprehension,
    expr,
    keyword,
    match_case,
    mod,
    operator,
    pattern,
    stmt,
    unaryop,
    withitem,
    type_param,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _arglikes,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _pattern_attrlikes,
    _type_params,
)

from .astutil import (
    constant,
    re_identifier,
    FIELDS,
    OPCLS2STR,
    bistr,
    is_valid_identifier,
    is_valid_identifier_dotted,
    is_valid_identifier_star,
    is_valid_identifier_alias,
    is_valid_target,
    precedence_require_parens,
)

from .common import (
    PYLT13,
    re_line_end_ws_cont_or_comment,
    NodeError,
    nspace,
    pyver,
    shortstr,
    lline_start,
    next_frag,
    prev_frag,
    next_find_re,
    next_delims,
)

from .parsex import (
    _AST_TYPE_BY_NAME_OR_TYPE,
    _fixing_unparse,
    Mode,
    ParseError,
    unparse,
    parse,
    parse_stmt,
    parse_stmts,
    parse_ExceptHandler,
    parse__ExceptHandlers,
    parse_match_case,
    parse__match_cases,
    parse_expr,
    parse_expr_all,
    parse_expr_arglike,
    parse_expr_slice,
    parse_Tuple_elt,
    parse_Tuple,
    parse_Set,
    parse_List,
    parse__Assign_targets,
    parse__decorator_list,
    parse__arglike,
    parse__arglikes,
    parse_boolop,
    parse_operator,
    parse_unaryop,
    parse_cmpop,
    parse_comprehension,
    parse__comprehensions,
    parse__comprehension_ifs,
    parse_arguments,
    parse_arguments_lambda,
    parse_arg,
    parse_keyword,
    parse_alias,
    parse__aliases,
    parse_Import_name,
    parse__Import_names,
    parse_ImportFrom_name,
    parse__ImportFrom_names,
    parse_withitem,
    parse__withitems,
    parse_pattern,
    parse__pattern_attrlikes,
    parse_type_param,
    parse__type_params,
    parse__expr_arglikes,
    parse__Dict_maybe_undelimited,
    parse__MatchMapping_maybe_undelimited,
)

__all__ = [
    'Code',
    'code_as',
    'code_as_all',
    'code_as_stmts',
    'code_as__ExceptHandlers',
    'code_as__match_cases',
    'code_as_expr',
    'code_as_expr_all',
    'code_as_expr_arglike',
    'code_as_expr_slice',
    'code_as_Tuple_elt',
    'code_as_Tuple',
    'code_as_Set',
    'code_as_List',
    'code_as__Assign_targets',
    'code_as__decorator_list',
    'code_as__arglike',
    'code_as__arglikes',
    'code_as_boolop',
    'code_as_operator',
    'code_as_unaryop',
    'code_as_cmpop',
    'code_as_comprehension',
    'code_as__comprehensions',
    'code_as__comprehension_ifs',
    'code_as_arguments',
    'code_as_arguments_lambda',
    'code_as_arg',
    'code_as_keyword',
    'code_as_alias',
    'code_as__aliases',
    'code_as_Import_name',
    'code_as__Import_names',
    'code_as_ImportFrom_name',
    'code_as__ImportFrom_names',
    'code_as_withitem',
    'code_as__withitems',
    'code_as_pattern',
    'code_as__pattern_attrlikes',
    'code_as_type_param',
    'code_as__type_params',
    'code_as_identifier',
    'code_as_identifier_dotted',
    'code_as_identifier_star',
    'code_as_identifier_alias',
    'code_as_constant',
    'code_as__expr_arglikes',
    'code_as__Dict_maybe_undelimited',
    'code_as__MatchMapping_maybe_undelimited',
]


Code = Union['fst.FST', AST, str, list[str]]  ; """Code types accepted for put to `FST`."""
CodeAs = Callable[[Code, Mapping[str, Any], Mapping[str, Any]], 'fst.FST']  # + kwargs: *, strip: bool = False, coerce: bool = False

_ASTS_LEAF_EXPRISH_SEQ = frozenset([Tuple, List, Set, arguments, MatchSequence, _Assign_targets, _decorator_list,
                                    _arglikes, _comprehension_ifs, _aliases, _withitems, _pattern_attrlikes,
                                    _type_params])

_EXPR_PARSE_FUNC_TO_NAME = {
    parse_Tuple:        'Tuple',
    parse_Tuple_elt:    'expression (tuple element)',
    parse_expr_slice:   'expression (slice)',
    parse_expr_arglike: 'expression (arglike)',
    parse_expr_all:     'expression (all types)',
    parse_expr:         'expression (standard)',
}


def _normalize_Constant_for_unparse(ast: Constant) -> tuple[AST, type[AST]]:
    """Normalize a `Constant` node that may contain negative numerical values or negative floating point 0.0 FOR UNPARSE
    AND REPARSE ONLY! Resulting `AST` node may not be valid for anything else!!!

    **Returns:**
    - `(AST, mode)`: `AST` node appropriate for unparse and the mode that it should reparse with.
    """

    mode = Constant
    value = ast.value

    if isinstance(value, int):
        if value < 0:
            mode = UnaryOp
            ast = UnaryOp(USub(), Constant(-value))

    elif isinstance(value, float):
        if value < 0:
            mode = UnaryOp
            ast = UnaryOp(USub(), Constant(-value))

        elif not value and copysign(1.0, value) == -1.0:  # normalize -0.0 because otherwise it reparses to UnaryOp(USub)
            ast = Constant(0.0)

    elif isinstance(value, complex):
        imag = value.imag

        if real := value.real:
            mode = BinOp
            op = Sub if imag < 0 else Add
            ast = BinOp(Constant(int(real) if real.is_integer() else real), op(), Constant(complex(0, abs(imag))))

        elif imag < 0:
            mode = UnaryOp
            ast = UnaryOp(USub(), Constant(complex(0.0, abs(imag))))

        elif not imag and copysign(1.0, imag) == -1.0:  # normalize -0.0j
            ast = Constant(0j)  # also normalize real -0.0 here

        elif copysign(1.0, real) == -1.0:  # need to normalize possible -0.0 real
            ast = Constant(complex(0.0, imag))

    return ast, mode


def _fix__slice_last_line(self: fst.FST, lines: list[bistr], end_ln: int, end_col: int, comment: bool = False) -> None:
    """Make sure there is no line continuation backslash on the last line of a known `_slice` SPECIAL SLICE node.
    Optionally also remove comment if there.

    **Parameters:**
    - `(end_ln, end_col)`: End location of last child, or `(0, 0)` if none (or anything really in that case).
    """

    if end_ln != len(lines) - 1:
        end_col = 0

    m = re_line_end_ws_cont_or_comment.search(l := lines[-1], end_col)

    if (g := m.group(1)) and (comment or not g.startswith('#')):
        lines[-1] = l = bistr(l[:m.start()])
        self.a.end_col_offset = l.lenbytes

        self._touch()


def _fix__aliases(self: fst.FST) -> None:
    """Fix `_aliases` SPECIAL SLICE by deleting comments except on last line. That is considered a valid `_aliases` for
    our purposes because if it is put to an `import` then line continuations will be added as needed there."""

    self._maybe_add_line_continuations(True, del_comments=True, del_comment_lines=True, add_lconts=False)


def _fix__Assign_targets(self: fst.FST) -> None:
    """Fix `_Assign_targets` SPECIAL SLICE by deleting comments except on last line. That is considered a valid
    `_Assign_targets` for our purposes because if it is put to actual `targets` then line continuations will be added as
    needed there."""

    self._maybe_add_line_continuations(True, del_comments=True, del_comment_lines=True)


def _par_if_needed(  # TODO: candidate function to move into core, possibly just the detection part and not the parenthesizing part, or selectable
    self: fst.FST, has_pars: bool | None = None, parsability: bool = True, arglike: bool = False
) -> bool:
    """Parenthesize node if needed for precedence or parsability (this one optional). We expect this to be called on
    stuff that can actually be parenthesized.

    **Parameters:**
    - `has_pars`: Whether has grouping parentheses or not. Actions for `True` and `False` are asymmetric.
        - `True`: There are grouping parentheses so the function will just return.
        - `False`: There are not grouping parentheses, but atomicity will still be checked and the function may not
            parenthesize.
        - `None`: Unknown if there are grouping parentheses or not, will be checked and action taken based on this.
    - `parsability`: Whether to parenthesize for parsability or not.
    - `arglike`: Whether `self` is in a container which allows arglike-only expressions (`Call.args`, etc...).

    **Returns:**
    - `bool`: Whether parentheses were added or not.
    """

    if has_pars:  # convenience early out
        return False

    ast_cls = self.a.__class__

    if ast_cls is Tuple:
        if has_pars := bool(self._is_delimited_seq()):
            return False

    elif ast_cls is MatchSequence:
        if has_pars := bool(self.is_delimited_matchseq()):
            return False

    elif has_pars is None:
        if has_pars := self.pars().n:
            return False

    child = self.a

    if child.__class__ is Starred:
        parent = child
        child = child.value
        field = 'value'
        idx = None

    elif parent := self.parent:
        parent = parent.a
        field, idx = self.pfield

    else:
        field = idx = None

    if parent:  # if there is a parent then we can check for precedence
        need_pars = precedence_require_parens(child, parent, field, idx, arglike=arglike)
    else:
        need_pars = False

    if not need_pars and parsability:  # if not needed for precedence then check if needed for parsability
        need_pars = not self._is_enclosed_in_parents() and not self._is_enclosed_or_line(check_pars=False, whole=False)

    if need_pars:
        if ast_cls is Tuple:
            self._delimit_node(False)  # <-- whole=False
        elif ast_cls is MatchSequence:
            self._delimit_node(False, '[]')  # <-- whole=False
        else:
            self.par(whole=False)

    return need_pars


def _coerce_error(to: str | AST | type[AST], from_: str | AST | type[AST], reason: str = '') -> Exception:
    if isinstance(to, type):
        to = to.__qualname__
    elif not isinstance(to, str):
        to = to.__class__.__qualname__

    if isinstance(from_, type):
        from_ = from_.__qualname__
    elif not isinstance(from_, str):
        from_ = from_.__class__.__qualname__

    if not reason:
        reason = ', could not coerce'
    elif reason == 'coerce disabled':
        reason = ', coerce disabled'
    elif reason:
        reason = f', could not coerce, {reason}'

    # return NodeError(f'cannot coerce to {to} from {from_}{reason}')
    return NodeError(f'expecting {to}, got {from_}{reason}')


# ......................................................................................................................
# general coerce to patterns

def _coerce_to_pattern_ast_ret_empty_str(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """These are the individual `AST` coerce functions. The returned `AST` may or may not have location information. In
    the case of `is_FST=False`. In the case of `is_FST=True`, it **MUST** have location information as the returned
    `AST` is used as the actual `AST` node for the final `FST` node.

    These individual functions ARE allowed to change `FST` source as long as it wouldn't break any recursion going on.

    If an `FST` is passed in then it will remain alive after coercion but the source may be modified to conform to the
    desired node type rules.

    **Parameters:**
    - `ast`: The `AST` node to coerce, can be part of an `FST` tree.
    - `is_FST`: Whether the `ast` node is part of an `FST` tree, meaning it has source for any possible reparse which
        should be done in that case to get the correct locations.

    **Returns:**
    - `str`: An error string indicating why a coercion could not happen. Empty string for general uncoercability.
    - `(AST, unmake_which)`:
        - `AST`: The `AST` is the new node to use, it is either a child of the original node passed in or a completely
            new node created based on the node passed in.
        - `unmake_which`: This only has meaning if the node is an `FST`. Indicates what kind of unmake should be done on
            the original tree. In reality the whole tree can always be unmade and in this case all that will happen is
            that new `FST` nodes will be created for it, but it may be more efficient to only unmake a part of the
            original tree if we know we will need the already-created `FST` node for some children, which saves some
            class instantiations.
            - `1`: Unmake just the original `FST` root node, no children.
            - `2`: Unmake the entire original `FST`.
    """

    return ''

def _coerce_to_pattern_ast_stmtmod(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if len(body := ast.body) != 1:
        return 'multiple statements'

    if (ast := body[0]).__class__ is not Expr:
        return f'uncoercible type {ast.__class__.__name__}'

    if is_FST:
        ast.f._trail_sep(sep=';', del_=True)

    ast = ast.value

    return _AST_COERCE_TO_PATTERN_FUNCS.get(
        ast.__class__, _coerce_to_pattern_ast_ret_empty_str)(ast, is_FST, options, parse_params)

def _coerce_to_pattern_ast_Expression(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    ast = ast.body

    return _AST_COERCE_TO_PATTERN_FUNCS.get(
        ast.__class__, _coerce_to_pattern_ast_ret_empty_str)(ast, is_FST, options, parse_params)

def _coerce_to_pattern_ast_Expr(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if is_FST:
        ast.f._trail_sep(sep=';', del_=True)

    ast = ast.value

    return _AST_COERCE_TO_PATTERN_FUNCS.get(
        ast.__class__, _coerce_to_pattern_ast_ret_empty_str)(ast, is_FST, options, parse_params)

def _coerce_to_pattern_ast_Constant(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    value = ast.value
    value_cls = value.__class__

    if value_cls in (bool, NoneType):
        if not is_FST:
            ret = MatchSingleton(value=value)
        else:
            ret = MatchSingleton(value=value, lineno=ast.lineno, col_offset=ast.col_offset,
                                 end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

        return ret, 2

    elif value is ...:
        return 'cannot be Ellipsis'

    if not is_FST:
        ret = MatchValue(value=ast)
    else:
        ret = MatchValue(value=ast, lineno=ast.lineno, col_offset=ast.col_offset,
                         end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_Attribute(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    value = ast

    while True:
        value = value.value
        value_cls = value.__class__

        if is_FST:
            value.f._unparenthesize_grouping(False)

        if value_cls is not Attribute:
            break

    if value_cls is not Name:
        return f'base value must be Name, not {value_cls.__name__}'
    elif value.id == '_':
        return "base Name cannot be '_'"

    if not is_FST:
        ret = MatchValue(value=ast)
    else:
        ret = MatchValue(value=ast, lineno=ast.lineno, col_offset=ast.col_offset,
                         end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_Starred(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    value = ast.value

    if value.__class__ is not Name:
        return 'value must be Name'

    if (name := value.id) == '_':
        name = None

    if not is_FST:
        ret = MatchStar(name=name)

    else:
        value.f._unparenthesize_grouping(False)

        ret = MatchStar(name=name, lineno=ast.lineno, col_offset=ast.col_offset,
                        end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_Name(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if (name := ast.id) == '_':
        name = None

    if not is_FST:
        ret = MatchAs(name=name)
    else:
        ret = MatchAs(name=name, lineno=ast.lineno, col_offset=ast.col_offset,
                      end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_arg(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if ast.annotation:
        return 'has annotation'

    if (name := ast.arg) == '_':
        name = None

    if not is_FST:
        ret = MatchAs(name=name)
    else:
        ret = MatchAs(name=name, lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                      end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_alias(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if ast.asname:
        return 'has asname'
    if (name := ast.name) == '*':
        return "is star '*'"
    if '.' in name:
        return "is dotted"

    if (name := name) == '_':
        name = None

    if not is_FST:
        ret = MatchAs(name=name)
    else:
        ret = MatchAs(name=name, lineno=ast.lineno, col_offset=ast.col_offset,
                      end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_withitem(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if ast.optional_vars:
        return 'has optional_vars'

    ast = ast.context_expr

    return _AST_COERCE_TO_PATTERN_FUNCS.get(
        ast.__class__, _coerce_to_pattern_ast_ret_empty_str)(ast, is_FST, options, parse_params)

def _coerce_to_pattern_ast_TypeVar(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if ast.bound:
        return 'has bound'
    if getattr(ast, 'default_value', None):
        return 'has default_value'

    if (name := ast.name) == '_':
        name = None

    if not is_FST:
        ret = MatchAs(name=name)
    else:
        ret = MatchAs(name=name, lineno=ast.lineno, col_offset=ast.col_offset,
                      end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_TypeVarTuple(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if getattr(ast, 'default_value', None):
        return 'has default_value'

    if (name := ast.name) == '_':
        name = None

    if not is_FST:
        ret = MatchStar(name=name)
    else:
        ret = MatchStar(name=name, lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                        end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_Dict(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    keys = []
    patterns = []
    rest = None

    for key, value in zip(ast.keys, ast.values, strict=True):
        if not key:
            if rest is not None:
                return "multiple '**' values found"
            if value.__class__ is not Name:
                return f"'**' value must be Name, not {value.__class__.__name__}"

            if (rest := value.id) == '_':
                return "'**' key cannot be '_'"

            continue

        elif rest:
            return "values cannot follow '**' key"

        if is_FST:
            key.f._unparenthesize_grouping(False)  # cannot have pars

        key_cls = key.__class__

        if key_cls is Constant:  # these can just be used as-is
            keys.append(key)

        elif key.__class__ not in (UnaryOp, BinOp, Attribute):
            return f"key must be Constant or Attribute, not {key_cls.__name__}"

        else:  # these may be invalid or have parentheses so we need to walk
            key = _AST_COERCE_TO_PATTERN_FUNCS.get(
                key_cls, _coerce_to_pattern_ast_ret_empty_str)(key, is_FST, options, parse_params)  # we call this just to validate and remove parentheses if present

            if isinstance(key, str):
                return key

            keys.append(key[0].value)  # we don't want the MatchValue pattern but its actual value expression (or Attribute)

        value = _AST_COERCE_TO_PATTERN_FUNCS.get(
            value.__class__, _coerce_to_pattern_ast_ret_empty_str)(value, is_FST, options, parse_params)  # we call this just to validate and remove parentheses if present

        if isinstance(value, str):
            return value

        patterns.append(value[0])  # here we do want the actual pattern

    if not is_FST:
        ret = MatchMapping(keys=keys, patterns=patterns, rest=rest)
    else:
        ret = MatchMapping(keys=keys, patterns=patterns, rest=rest, lineno=ast.lineno, col_offset=ast.col_offset,
                           end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_Call(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    func = ast.func
    func_cls = func.__class__

    if func_cls is Attribute:
        if is_FST:
            func.f._unparenthesize_grouping(False)  # cannot have pars

        res = _coerce_to_pattern_ast_Attribute(func, is_FST, options, parse_params)  # we call this just to validate and remove parentheses if present

        if isinstance(res, str):
            return res

    elif func_cls is not Name:
        return f"func must be Name or Attribute, not {func_cls.__name__}"
    elif func.id == '_':
        return "func Name cannot be '_'"

    patterns = []
    kwd_attrs = []
    kwd_patterns = []

    for arg in ast.args:  # noqa: F402
        if arg.__class__ is Starred:
            return 'cannot have Starred'

        pat = _AST_COERCE_TO_PATTERN_FUNCS.get(
            arg.__class__, _coerce_to_pattern_ast_ret_empty_str)(arg, is_FST, options, parse_params)

        if isinstance(pat, str):
            return pat

        patterns.append(pat[0])

    for kw in ast.keywords:
        arg = kw.arg
        value = kw.value

        if not arg:
            return "cannot have '**' keyword"

        pat = _AST_COERCE_TO_PATTERN_FUNCS.get(
            value.__class__, _coerce_to_pattern_ast_ret_empty_str)(value, is_FST, options, parse_params)

        if isinstance(pat, str):
            return pat

        kwd_attrs.append(arg)
        kwd_patterns.append(pat[0])

    if not is_FST:
        ret = MatchClass(cls=func, patterns=patterns, kwd_attrs=kwd_attrs, kwd_patterns=kwd_patterns)
    else:
        ret = MatchClass(cls=func, patterns=patterns, kwd_attrs=kwd_attrs, kwd_patterns=kwd_patterns, lineno=ast.lineno,
                         col_offset=ast.col_offset, end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_BinOp(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`.

    Either a complex number to a `MatchValue` or a `BitOr` (possibly ladder of them) to a `MatchOr`.
    """

    op_cls = ast.op.__class__

    if op_cls in (Add, Sub):  # `int +/- complex` -> MatchValue
        right = ast.right

        if (right.__class__ is not Constant
            or not isinstance(value := right.value, complex)
            or value.real
            or value.imag < 0
        ):
            return 'right value must be pure imaginary Constant >= 0j'

        left = ast.left
        left_cls = left.__class__
        operand = None

        if left_cls is Constant:
            if not isinstance(value := left.value, (int, float)) or isinstance(value, bool) or value < 0:
                return 'left Constant value must be >= 0'

        elif left_cls is UnaryOp:
            if left.op.__class__ is not USub:
                return "left UnaryOp must be '-'"

            operand = left.operand

            if (operand.__class__ is not Constant
                or not isinstance(value := operand.value, (int, float))
                or isinstance(value, bool)
                or value < 0
            ):
                return 'left UnaryOp operand must be int or float Constant >= 0'

        else:
            return 'left value must be +/- int or float'

        if is_FST:  # do after all the checks because maybe in the future we make coercion attempts non-destructive?
            left.f._unparenthesize_grouping(False)
            right.f._unparenthesize_grouping(False)

            if operand:
                operand.f._unparenthesize_grouping(False)

        if not is_FST:
            ret = MatchValue(value=ast)
        else:
            ret = MatchValue(value=ast, lineno=ast.lineno, col_offset=ast.col_offset,
                             end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

        return ret, 2

    # 'a | b' -> MatchOr

    if op_cls is not BitOr:
        return f"op must be '+', '-' or '|', not {ast.op.__class__.__name__}"

    right = ast.right

    if right.__class__ is Starred:
        return 'cannot have Starred'

    pat_right = _AST_COERCE_TO_PATTERN_FUNCS.get(
        right.__class__, _coerce_to_pattern_ast_ret_empty_str)(right, is_FST, options, parse_params)

    if isinstance(pat_right, str):
        return pat_right

    pat_right = pat_right[0]
    left = ast.left

    if left.__class__ is Starred:
        return 'cannot have Starred'

    pat_left = _AST_COERCE_TO_PATTERN_FUNCS.get(
        left.__class__, _coerce_to_pattern_ast_ret_empty_str)(left, is_FST, options, parse_params)

    if isinstance(pat_left, str):
        return pat_left

    pat_left = pat_left[0]
    pat_left_cls = pat_left.__class__

    if pat_left_cls is MatchOr and not (is_FST and left.f.pars().n):
        patterns = [*pat_left.patterns, pat_right]
    else:
        patterns = [pat_left, pat_right]

    if not is_FST:
        ret = MatchOr(patterns=patterns)
    else:
        ret = MatchOr(patterns=patterns, lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                      end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_UnaryOp(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if ast.op.__class__ is not USub:
        return f"op must be '+' or '-', not {ast.op.__class__.__name__}"

    operand = ast.operand

    if operand.__class__ is not Constant:
        return f'operand must be Constant, not {operand.__class__.__name__}'

    value = operand.value

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < 0:
            return 'operand value must be >= 0'

    elif isinstance(value, complex):
        if value.real or value.imag < 0:
            return 'complex operand must be pure imaginary >= 0j'

    else:
        return f'operand value must be int, float or complex, not {value.__class__.__name__}'

    if is_FST:
        operand.f._unparenthesize_grouping(False)

    if not is_FST:
        ret = MatchValue(value=ast)
    else:
        ret = MatchValue(value=ast, lineno=ast.lineno, col_offset=ast.col_offset,
                         end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast_seq(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    ast_cls = ast.__class__

    if is_FST:
        fst_ = ast.f
        lines = fst_.root._lines

    if ast_cls in ASTS_LEAF_TUPLE_OR_LIST:
        elts = ast.elts  # whatever delimiters and commas present they are compatible with MatchSequence

    elif ast_cls is Set:
        if is_FST:
            ln, col, end_ln, end_col = fst_.loc
            lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col - 1]}]{l[end_col:]}')
            lines[ln] = bistr(f'{(l := lines[ln])[:col]}[{l[col + 1:]}')

        elts = ast.elts

    elif ast_cls is _arglikes:
        elts = ast.arglikes

        if any(e.__class__ is keyword for e in elts):
            return 'has keyword'

        if is_FST:
            fst_._fix_undelimited_seq(elts, '[]', True)

    elif ast_cls in (_Assign_targets, _decorator_list, _comprehension_ifs):
        elts = getattr(ast, ast._fields[0])

        if is_FST:
            res = _AST_COERCE_TO_EXPR_FUNCS.get(
                ast_cls, _coerce_to_pattern_ast_ret_empty_str)(ast, is_FST, options, parse_params)  # just need to convert their special syntax to comma-delimited sequence

            if isinstance(res, str):
                return res  # pragma: no cover  # not currently returned for these types

            fst_._fix_undelimited_seq(elts, '[]', True)

    elif ast_cls in (arguments, _aliases, _withitems, _type_params):
        res = _AST_COERCE_TO_EXPR_FUNCS.get(
            ast_cls, _coerce_to_pattern_ast_ret_empty_str)(ast, is_FST, options, parse_params)  # need to convert their elements to expressions, container will be Tuple

        if isinstance(res, str):
            return res

        ast = res[0]
        elts = ast.elts

        if is_FST:
            fst_ = fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)

            fst_._fix_undelimited_seq(elts, '[]', True)  # yes its a Tuple and we are adding brackets, deal with it

    else:
        raise RuntimeError('should not get here')  # pragma: no cover

    patterns = []

    for e in elts:
        e = _AST_COERCE_TO_PATTERN_FUNCS.get(
            e.__class__, _coerce_to_pattern_ast_ret_empty_str)(e, is_FST, options, parse_params)

        if isinstance(e, str):
            return e

        patterns.append(e[0])

    if not is_FST:
        ret = MatchSequence(patterns=patterns)
    else:
        ret = MatchSequence(patterns=patterns, lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                            end_col_offset=ast.end_col_offset)

    return ret, 2

def _coerce_to_pattern_ast__pattern_attrlikes(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int] | str:
    """See `_coerce_to_pattern_ast_ret_empty_str()`."""

    if ast.kwd_patterns:
        return 'has keyword attributes'

    patterns = ast.patterns

    if not is_FST:
        ret = MatchSequence(patterns=patterns)

    else:
        ast.f._delimit_node(delims='[]')

        ret = MatchSequence(patterns=patterns, lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                            end_col_offset=ast.end_col_offset)

    return ret, 1

_AST_COERCE_TO_PATTERN_FUNCS = {
    Module:             _coerce_to_pattern_ast_stmtmod,
    Interactive:        _coerce_to_pattern_ast_stmtmod,
    Expression:         _coerce_to_pattern_ast_Expression,
    Expr:               _coerce_to_pattern_ast_Expr,
    _Assign_targets:    _coerce_to_pattern_ast_seq,
    _decorator_list:    _coerce_to_pattern_ast_seq,
    _arglikes:          _coerce_to_pattern_ast_seq,
    BinOp:              _coerce_to_pattern_ast_BinOp,  # MatchOr from BitOr, MatchValue from int+/-complex
    UnaryOp:            _coerce_to_pattern_ast_UnaryOp,  # MatchValue from -int or -complex
    Dict:               _coerce_to_pattern_ast_Dict,  # MatchMapping
    Set:                _coerce_to_pattern_ast_seq,
    Call:               _coerce_to_pattern_ast_Call,  # MatchClass
    Constant:           _coerce_to_pattern_ast_Constant,
    Attribute:          _coerce_to_pattern_ast_Attribute,
    Starred:            _coerce_to_pattern_ast_Starred,
    Name:               _coerce_to_pattern_ast_Name,
    List:               _coerce_to_pattern_ast_seq,
    Tuple:              _coerce_to_pattern_ast_seq,
    _comprehension_ifs: _coerce_to_pattern_ast_seq,
    arguments:          _coerce_to_pattern_ast_seq,
    arg:                _coerce_to_pattern_ast_arg,
    alias:              _coerce_to_pattern_ast_alias,
    _aliases:           _coerce_to_pattern_ast_seq,
    withitem:           _coerce_to_pattern_ast_withitem,
    _withitems:         _coerce_to_pattern_ast_seq,
    _pattern_attrlikes: _coerce_to_pattern_ast__pattern_attrlikes,
    TypeVar:            _coerce_to_pattern_ast_TypeVar,
    TypeVarTuple:       _coerce_to_pattern_ast_TypeVarTuple,
    _type_params:       _coerce_to_pattern_ast_seq,
}  # fmt: skip


def _coerce_to_pattern_ast(
    ast: AST,
    is_FST: bool,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    expecting: str = 'pattern',
    unmake: bool = True,
) -> AST:
    """This is not like the `_coerce_to_?()` functions below, it just tries to coerce an `AST` to an expression `AST`,
    mostly by taking a contained expression `AST` but maybe by creating a new one from a string. Parsing is a possible
    action in case of `is_FST=True`. If is not an `FST` then it is assumed the node will be unparsed and reparsed so
    node creation in that case is just targetted at the `unparse()` and may not have locations or other things a full
    node would.

    This function will unmake the source `FST` if is one if a coercion occurs.

    **WARNING!** Can not assume any `AST` nodes returned from here have valid `FST` nodes even if `is_FST=True`. They
    must always be recreated.

    **Parameters:**
    - `ast`: The `AST` node to coerce, can be part of an `FST` tree.
    - `is_FST`: Whether the `ast` node is part of an `FST` tree, meaning it has source for any possible reparse which
        should be done in that case to get the correct locations.
    - `expecting`: Text for error messages.
    - `unmake`: Whether to unmake an `FST` node or the caller will take care of it. This should be `False` for recursed
        coercion as the tree structure needs to remain valid for possible modifications like parsentheses.

    **Returns:**
    - `AST`: The coerced `AST`.
    """

    ret = _AST_COERCE_TO_PATTERN_FUNCS.get(
        ast.__class__, _coerce_to_pattern_ast_ret_empty_str)(ast, is_FST, options, parse_params)

    if isinstance(ret, str):
        raise _coerce_error(expecting, ast, ret)  # ret here is reason str

    ret, unmake_which = ret

    if is_FST and unmake:
        if unmake_which == 1:  # just the root node (pattern from _pattern_exprlikes)
            ast.f._unmake_fst_parents(True)
        elif unmake_which == 2:  # node was completely regenerated, unmake whole original (normal case for patterns from non-patterns)
            ast.f._unmake_fst_tree()

    return ret


# ......................................................................................................................
# general coerce to expression

def _coerce_to_expr_ast_ret_empty_str(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """These are the individual `AST` coerce functions. The returned `AST` may or may not have location information. In
    the case of `is_FST=False`. In the case of `is_FST=True`, it **MUST** have location information as the returned
    `AST` is used as the actual `AST` node for the final `FST` node.

    These individual functions ARE allowed to change `FST` source as long as it wouldn't break any recursion going on,
    for example a `pattern` changing source so that location of previouisly coerced `AST` in a `MatchSequence` changes.

    If an `FST` is passed in then it will remain alive after coercion but the source may be modified to conform to the
    desired node type rules.

    **Parameters:**
    - `ast`: The `AST` node to coerce, can be part of an `FST` tree.
    - `is_FST`: Whether the `ast` node is part of an `FST` tree, meaning it has source for any possible reparse which
        should be done in that case to get the correct locations.

    **Returns:**
    - `str`: An error string indicating why a coercion could not happen. Empty string for general uncoercibility.
    - `(AST, unmake_which, is_nonstandard_tuple)`:
        - `AST`: The `AST` is the new node to use. It is either a child of the original node passed in or a completely
            new node created based on the node passed in.
        - `unmake_which`: This only has meaning if the node is an `FST`. Indicates what kind of unmake should be done on
            the original tree. In reality the whole tree can always be unmade and in this case all that will happen is
            that new `FST` nodes will be created for it, but it may be more efficient to only unmake a part of the
            original tree if we know we will need the already-created `FST` node for some children, which saves some
            class instantiations.
            - `0`: Unmake the returned `AST` parents.
            - `1`: Unmake just the original `FST` root node, no children.
            - `2`: Unmake the entire original `FST`.
            - `-1`: Does not unmake.
        - `is_nonstandard_tuple`: This only has meaning if the node is an `FST`. Indicates that the `AST` it is a
            nonstandard `Tuple` which needs to be fixed with `_fix_Tuple()` for `is_FST=True` because is unparenthesized
            and may be empty and may not have trailing comma on singleton, also start and stop locations may be
            incorrect. **WARNING!** This can only be used for top-level nodes like `_arglikes` because it is not handled
            recursively.
    """

    return ''  # pragma: no cover  # can only happen if non-pattern nodes illegally present where patterns expected

def _coerce_to_expr_ast_maybe_expr(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`.

    This exists so that attempting to coerce an `expr` to an `expr` just returns the same `expr.
    """

    if ast.__class__ in ASTS_LEAF_EXPR:
        return ast, -1, False

    return ''

def _coerce_to_expr_ast_stmtmod(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if len(body := ast.body) != 1:
        return 'multiple statements'

    if (ast := body[0]).__class__ is not Expr:
        return f'uncoercible type {ast.__class__.__name__}'

    if is_FST:
        ast.f._trail_sep(sep=';', del_=True)

    return ast.value, 0, False

def _coerce_to_expr_ast_Expression(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    return ast.body, 0, False

def _coerce_to_expr_ast_Expr(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if is_FST:
        ast.f._trail_sep(sep=';', del_=True)

    return ast.value, 0, False

def _coerce_to_expr_ast__Assign_targets(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if not is_FST:
        return Tuple(elts=ast.targets), 1, False

    if targets := ast.targets:
        last_target = targets[-1]
        fst_ = ast.f
        lines = fst_._lines  # fst_ must be root

        for a in targets:
            f = a.f

            if (is_pard_tup := f.is_parenthesized_tuple()) is False:
                if is_pard_tup is False:
                    f._delimit_node()

                _, _, ln, col = f.loc

            else:  # a parenthesized tuple can still have grouping pars
                _, _, ln, col = f.pars()

            eq = next_frag(lines, ln, col, len(lines) - 1, 0x7fffffffffffffff)  # may or may not be there '=' for last target

            if not (is_last := a is last_target) or eq:
                end_ln, end_col, src = eq

                assert src.startswith('=')

                fst_._put_src(None if is_last else ',', ln, col, end_ln, end_col + 1, True)  # replace everything between end of expr and '=' with ',' or just remove for last element

            f._set_ctx(Load)

    return Tuple(elts=targets, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                 end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset), 1, True

def _coerce_to_expr_ast__decorator_list(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if not is_FST:
        return Tuple(elts=ast.decorator_list), 1, False

    if decorator_list := ast.decorator_list:
        last_deco = decorator_list[-1]
        fst_ = ast.f

        for i, a in enumerate(decorator_list):
            f = a.f
            ln, col, end_ln, end_col = f.pars()
            deco_ln, deco_col, _, _ = fst_._loc_decorator(i, False)

            if a is not last_deco:  # add comma after expression, unless last
                fst_._put_src(',', end_ln, end_col, end_ln, end_col, True, exclude=f, offset_excluded=False)

            fst_._put_src(None, deco_ln, deco_col, ln, col, True)  # remove everything from the '@' up to the start of the parenthesized decorator expression, it would be insane to try to preserve any comments between these, so will probably do it at some point

    return Tuple(elts=decorator_list, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                 end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset), 1, True

def _coerce_to_expr_ast__arglikes(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    arglikes = ast.arglikes

    if not is_FST:
        if any(a.__class__ is keyword for a in arglikes):
            return 'has keyword'

        ret = Tuple(elts=arglikes)

    else:
        pars_arglike = fst.FST._get_opt_eff_pars_arglike(options)

        for a in arglikes:
            if a.__class__ is keyword:
                return 'has keyword'

            if pars_arglike and a.f._is_expr_arglike_only():
                a.f._parenthesize_grouping()

        ret = Tuple(elts=arglikes, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                    end_col_offset=ast.end_col_offset)

    return ret, 1, True

def _coerce_to_expr_ast__comprehension_ifs(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if not is_FST:
        return Tuple(elts=ast.ifs), 1, False

    if ifs := ast.ifs:
        last_if = ifs[-1]
        fst_ = ast.f
        ifs = ast.ifs

        for i, a in enumerate(ifs):
            f = a.f
            ln, col, end_ln, end_col = f.pars()
            if_ln, if_col, _, _ = fst_._loc_comprehension_if(i, False)

            if a is not last_if:  # add comma after expression, unless last
                fst_._put_src(',', end_ln, end_col, end_ln, end_col, True, exclude=f, offset_excluded=False)

            fst_._put_src(None, if_ln, if_col, ln, col, True)  # remove everything from the 'if' up to the start of the parenthesized decorator expression, it would be insane to try to preserve any comments between these, so will probably do it at some point

    return Tuple(elts=ifs, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                 end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset), 1, True

def _coerce_to_expr_ast_List_or_Set(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`. This function is meant for inter-expression coercion from a `List` or
    `Set` to a specifically requested `Tuple`."""

    if not is_FST:
        ret = Tuple(elts=ast.elts)

    else:
        fst_ = ast.f
        lines = fst_.root._lines  # we do not know for sure we are root, could be recursed from an Expr containing a List being coerced to Tuple
        ln, col, end_ln, end_col = fst_.loc

        lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col - 1]}){l[end_col:]}')  # just replace the '[]' or '{}' delimiters with '()', any needed singleton comma will be added by the caller
        lines[ln] = bistr(f'{(l := lines[ln])[:col]}({l[col + 1:]}')

        ret = Tuple(elts=ast.elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                    end_col_offset=ast.end_col_offset)

    return ret, 1, False  # 1 will unmake the ctx as well

def _coerce_to_expr_ast_Tuple(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`. This is a very special case that will only be called for coercion from
    a `Tuple` to a `List` or `Set` (or possibly other things in the future). It exists to strip the `Tuple` elements for
    the more normal containers since a `Tuple` can contain `Slice` nodes and we also use it for arglike-only expressions
    for `Call.args` and friends."""

    elts = ast.elts

    if not is_FST:
        if any(a.__class__ is Slice for a in elts):
            return 'has Slice'

        ret = Tuple(elts=elts)

    else:
        pars_arglike = fst.FST._get_opt_eff_pars_arglike(options)

        for a in elts:
            if a.__class__ is Slice:
                return 'has Slice'

            if pars_arglike and a.f._is_expr_arglike_only():
                a.f._parenthesize_grouping()

        ret = Tuple(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                    end_col_offset=ast.end_col_offset)

    return ret, 1, False  # 1 will unmake the ctx as well

def _coerce_to_expr_ast_arguments(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    vararg = ast.vararg
    elts = []

    if ast.posonlyargs:
        return 'has posonlyargs'
    if ast.defaults or any(a for a in ast.kw_defaults):
        return 'has defaults'
    if ast.kwarg or any(a for a in ast.kw_defaults):
        return 'has kwarg'

    if vararg:
        if vararg.annotation:
            return "vararg has annotation"
    elif ast.kwonlyargs:
        return "has empty vararg '*'"

    for a in ast.args:
        if a.annotation:
            return 'arg has annotation'

        if not is_FST:
            a = Name(id=a.arg)
        else:
            a = Name(id=a.arg, ctx=Load(), lineno=a.lineno, col_offset=a.col_offset, end_lineno=a.end_lineno,
                     end_col_offset=a.end_col_offset)

        elts.append(a)

    if is_FST:
        lines = ast.f._lines

    if vararg:
        if not is_FST:
            elts.append(Starred(value=Name(id=vararg.arg)))

        else:
            lineno = vararg.lineno
            col_offset = vararg.col_offset
            end_col_offset = vararg.end_col_offset
            ln = lineno - 1
            col = lines[ln].b2c(col_offset)
            star_ln, star_col, src = prev_frag(lines, 0, 0, ln, col)  # we can use (0, 0) as start bound because we are sure there are no strings anywhere here

            assert src.endswith('*')

            star_lineno = star_ln + 1
            star_col_offset = lines[star_ln].c2b(star_col + len(src) - 1)

            elts.append(Starred(value=Name(id=vararg.arg, ctx=Load(), lineno=lineno, col_offset=col_offset,
                                           end_lineno=lineno, end_col_offset=end_col_offset),
                                ctx=Load(), lineno=star_lineno, col_offset=star_col_offset, end_lineno=lineno,
                                end_col_offset=end_col_offset))

    for a in ast.kwonlyargs:
        if a.annotation:
            return 'kwonlyarg has annotation'

        if not is_FST:
            a = Name(id=a.arg)
        else:
            a = Name(id=a.arg, ctx=Load(), lineno=a.lineno, col_offset=a.col_offset, end_lineno=a.end_lineno,
                     end_col_offset=a.end_col_offset)

        elts.append(a)

    if not is_FST:
        return Tuple(elts=elts), 2, False

    if not elts:  # if this then just return whole source as empty tuple
        return Tuple(elts=elts, ctx=Load(), lineno=1, col_offset=0, end_lineno=len(lines),
                     end_col_offset=len(lines[-1])), 2, True

    e0 = elts[0]
    _, _, end_ln, end_col = ast.f.loc  # need to do this because of possible trailing comma

    return Tuple(elts=elts, ctx=Load(), lineno=e0.lineno, col_offset=e0.col_offset, end_lineno=end_ln + 1,
                 end_col_offset=lines[end_ln].c2b(end_col)), 2, True

def _coerce_to_expr_ast_arg(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if ast.annotation:
        return 'has annotation'

    if not is_FST:
        ret = Name(id=ast.arg)
    else:
        ret = Name(id=ast.arg, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                   end_col_offset=ast.end_col_offset)

    return ret, 2, False

def _coerce_to_expr_ast_alias(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if ast.asname:
        return 'has asname'
    if ast.name == '*':
        return "is star '*'"

    if '.' not in (name := ast.name):
        if not is_FST:
            ast = Name(id=name)
        else:
            ast = Name(id=name, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                       end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    elif not is_FST:  # or (f := ast.f).end_ln != f.ln or f.end_col != f.col + len(name):  # NOTE: could calculate locations but parse_expr() is probably faster
        parts = name.split('.')[::-1]
        ast = Attribute(value=Name(id=parts.pop()), attr=parts.pop())  # no locations needed because we know this will be reparsed when not is_FST

        while parts:
            ast = Attribute(value=ast, attr=parts.pop())

    else:  # reparse is cheap and lazy for the locations, which are needed if is_FST
        try:
            ast = parse_expr(ast.f.src, parse_params)
        except Exception as exc:  # pragma: no cover  # sanity check, this shouldn't fail
            return str(exc)

        if ast.__class__ is not Attribute:
            return 'failed reparse to Attribute'  # pragma: no cover  # sanity

    return ast, 2, False

def _coerce_to_expr_ast__aliases(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    names = ast.names
    elts = []

    if names:
        for a in names:
            if a.asname:
                return 'has alias with asname'
            if a.name == '*':
                return "has star '*' alias"

        if not is_FST:
            for a in ast.names:
                res = _coerce_to_expr_ast_alias(a, is_FST, options, parse_params)

                if isinstance(res, str):
                    return res  # pragma: no cover  # this cannot currently happen

                elts.append(res[0])

        else:  # reparse is cheap and lazy for the locations if there are any Attributes, which are needed if is_FST
            try:
                ast = parse_expr(ast.f.src, parse_params)
            except Exception as exc:  # pragma: no cover  # sanity check, this shouldn't fail
                return str(exc)

            if (ast_cls := ast.__class__) is Tuple:
                elts = ast.elts
            elif ast_cls in (Name, Attribute):
                elts = [ast]
            else:
                return 'failed reparse to Attribute'  # pragma: no cover  # sanity

    if not is_FST:
        ret = Tuple(elts=elts)
    else:
        ret = Tuple(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                    end_col_offset=ast.end_col_offset)

    return ret, 2, True

def _coerce_to_expr_ast_withitem(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if ast.optional_vars:
        return 'has optional_vars'

    return ast.context_expr, 1, False  # if coerce from withitem can reuse its AST

def _coerce_to_expr_ast__withitems(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    elts = []

    for a in ast.items:
        if a.optional_vars:
            return 'has withitem with optional_vars'

        elts.append(a.context_expr)

    if not is_FST:
        ret = Tuple(elts=elts)
    else:
        ret = Tuple(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                    end_col_offset=ast.end_col_offset)

    return ret, 2, True

def _coerce_to_expr_ast_MatchValue(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    return ast.value, 0, False

def _coerce_to_expr_ast_MatchSingleton(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if not is_FST:
        ret = Constant(value=ast.value)
    else:
        ret = Constant(value=ast.value, lineno=ast.lineno, col_offset=ast.col_offset,
                       end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2, False

def _coerce_to_expr_ast_MatchStar(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    name = ast.name or '_'

    if not is_FST:
        ret = Starred(value=Name(id=name))

    else:
        lineno = ast.lineno
        end_lineno = ast.end_lineno
        col_offset = ast.col_offset
        end_col_offset = ast.end_col_offset

        ret = Starred(value=Name(id=name, ctx=Load(), lineno=end_lineno, col_offset=end_col_offset - len(name.encode()),
                                 end_lineno=end_lineno, end_col_offset=end_col_offset),
                      ctx=Load(), lineno=lineno, col_offset=col_offset, end_lineno=end_lineno,
                      end_col_offset=end_col_offset)

    return ret, 2, False

def _coerce_to_expr_ast_MatchAs(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if ast.pattern:
        return 'MatchAs has pattern'

    name = ast.name or '_'

    if not is_FST:
        ret = Name(id=name)
    else:
        ret = Name(id=name, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                   end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2, False

def _coerce_to_expr_ast_MatchSequence(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`. This coercer RECURSES!"""

    if not is_FST:
        ast_cls = List
    else:
        ast_cls = List if ast.f.is_delimited_matchseq() == '[]' else Tuple

    elts = []

    for pat in ast.patterns:
        pat = _AST_COERCE_TO_EXPR_FUNCS.get(
            pat.__class__, _coerce_to_expr_ast_ret_empty_str)(pat, is_FST, options, parse_params)

        if isinstance(pat, str):
            return pat

        elts.append(pat[0])

    if not is_FST:
        ret = ast_cls(elts=elts)
    else:
        ret = ast_cls(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                      end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2, False  # we do not unmake trees here for subpatterns because this return signals that the whole tree needs to be unmade (FST nodes will be recreated)

def _coerce_to_expr_ast_MatchMapping(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`. This coercer RECURSES!"""

    keys = []
    values = []

    for key, pat in zip(ast.keys, ast.patterns, strict=True):
        pat = _AST_COERCE_TO_EXPR_FUNCS.get(
            pat.__class__, _coerce_to_expr_ast_ret_empty_str)(pat, is_FST, options, parse_params)

        if isinstance(pat, str):
            return pat

        keys.append(key)
        values.append(pat[0])

    if rest := ast.rest:
        keys.append(None)

        if not is_FST:
            values.append(Name(id=rest))

        else:
            f = ast.f
            lines = f.root._lines  # ast may not be root here because patterns recurse
            ln, col, end_ln, end_col = f._loc_MatchMapping_rest()

            values.append(Name(id=rest, ctx=Load(), lineno=ln + 1, col_offset=lines[ln].c2b(col), end_lineno=end_ln + 1,
                               end_col_offset=lines[end_ln].c2b(end_col)))

    if not is_FST:
        ret = Dict(keys=keys, values=values)
    else:
        ret = Dict(keys=keys, values=values, lineno=ast.lineno, col_offset=ast.col_offset,
                   end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2, False  # we do not unmake trees here for subpatterns because this return signals that the whole tree needs to be unmade (FST nodes will be recreated)

def _coerce_to_expr_ast_MatchClass(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`. This coercer RECURSES!"""

    args = []
    keywords = []

    for pat in ast.patterns:
        arg = _AST_COERCE_TO_EXPR_FUNCS.get(
            pat.__class__, _coerce_to_expr_ast_ret_empty_str)(pat, is_FST, options, parse_params)

        if isinstance(arg, str):
            return arg

        args.append(arg[0])

    if is_FST:
        lines = ast.f.root._lines
        _, _, prev_end_ln, prev_end_col = pat.f.loc if args else ast.cls.f.loc

    for arg_, pat in zip(ast.kwd_attrs, ast.kwd_patterns, strict=True):
        value = _AST_COERCE_TO_EXPR_FUNCS.get(
            pat.__class__, _coerce_to_expr_ast_ret_empty_str)(pat, is_FST, options, parse_params)

        if isinstance(value, str):
            return value

        value = value[0]

        if not is_FST:
            keywords.append(keyword(arg=arg_, value=value))

        else:
            ln, col, end_ln, end_col = pat.f.pars()
            ln, col, _ = next_find_re(lines, prev_end_ln, prev_end_col, ln, col, re_identifier)  # must be there

            keywords.append(keyword(arg=arg_, value=value, lineno=ln + 1, col_offset=lines[ln].c2b(col),
                                    end_lineno=end_ln + 1, end_col_offset=lines[end_ln].c2b(end_col)))

            prev_end_ln = end_ln
            prev_end_col = end_col

    if not is_FST:
        ret = Call(func=ast.cls, args=args, keywords=keywords)
    else:
        ret = Call(func=ast.cls, args=args, keywords=keywords, lineno=ast.lineno, col_offset=ast.col_offset,
                   end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2, False  # we do not unmake trees here for subpatterns because this return signals that the whole tree needs to be unmade (FST nodes will be recreated)

def _coerce_to_expr_ast_MatchOr(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`. This coercer RECURSES!"""

    if not (patterns := ast.patterns):  # we may have done this while editing
        return 'no elements'

    pat = patterns[0]
    ret = _AST_COERCE_TO_EXPR_FUNCS.get(
        pat.__class__, _coerce_to_expr_ast_ret_empty_str)(pat, is_FST, options, parse_params)

    if len(patterns) == 1:  # this is also only doable by us editing
        return ret

    if isinstance(ret, str):
        return ret

    ret = ret[0]

    if is_FST:
        f = ast.f
        lines = f.root._lines
        _, _, ast_end_ln, ast_end_col = f.loc

    for pat in patterns[1:]:
        right = _AST_COERCE_TO_EXPR_FUNCS.get(
            pat.__class__, _coerce_to_expr_ast_ret_empty_str)(pat, is_FST, options, parse_params)

        if isinstance(right, str):
            return right

        right = right[0]

        if not is_FST:
            ret = BinOp(left=ret, op=BitOr(), right=right)

        else:  # need account for internal closing parentheses because that location info is not present in the MatchOr
            _, _, ln, col = pat.f.loc
            end_ln, end_col = next_delims(lines, ln, col, ast_end_ln, ast_end_col)[-1]

            ret = BinOp(left=ret, op=BitOr(), right=right, lineno=ret.lineno, col_offset=ret.col_offset,
                        end_lineno=end_ln + 1, end_col_offset=lines[end_ln].c2b(end_col))

    if is_FST:  # need this because of parentheses
        ret.lineno = ast.lineno
        ret.col_offset = ast.col_offset

    return ret, 2, False  # we do not unmake trees here for subpatterns because this return signals that the whole tree needs to be unmade (FST nodes will be recreated)

def _coerce_to_expr_ast__pattern_attrlikes(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`. This coercer RECURSES!"""

    if ast.kwd_patterns:
        return 'has keyword attributes'

    elts = []

    for pat in ast.patterns:
        pat = _AST_COERCE_TO_EXPR_FUNCS.get(
            pat.__class__, _coerce_to_expr_ast_ret_empty_str)(pat, is_FST, options, parse_params)

        if isinstance(pat, str):
            return pat

        elts.append(pat[0])

    if not is_FST:
        ret = Tuple(elts=elts)
    else:
        ret = Tuple(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                    end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2, True  # we do not unmake trees here for subpatterns because this return signals that the whole tree needs to be unmade (FST nodes will be recreated)

def _coerce_to_expr_ast_TypeVar(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if ast.bound:
        return 'has bound'
    if getattr(ast, 'default_value', None):
        return 'has default_value'

    if not is_FST:
        ret = Name(id=ast.name)
    else:
        ret = Name(id=ast.name, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                   end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    return ret, 2, False

def _coerce_to_expr_ast_TypeVarTuple(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    if getattr(ast, 'default_value', None):
        return 'has default_value'

    name = ast.name

    if not is_FST:
        ret = Starred(value=Name(id=name))

    else:
        lineno = ast.lineno
        end_lineno = ast.end_lineno
        col_offset = ast.col_offset
        end_col_offset = ast.end_col_offset

        ret = Starred(value=Name(id=name, ctx=Load(), lineno=end_lineno, col_offset=end_col_offset - len(name.encode()),
                                 end_lineno=end_lineno, end_col_offset=end_col_offset),
                      ctx=Load(), lineno=lineno, col_offset=col_offset, end_lineno=end_lineno,
                      end_col_offset=end_col_offset)

    return ret, 2, False

def _coerce_to_expr_ast__type_params(
    ast: AST, is_FST: bool, options: Mapping[str, Any], parse_params: Mapping[str, Any]
) -> tuple[AST, int, bool] | str:
    """See `_coerce_to_expr_ast_ret_empty_str()`."""

    elts = []

    for a in ast.type_params:
        if getattr(a, 'bound', None):
            return f'{a.__class__.__name__} has bound'
        if getattr(a, 'default_value', None):
            return f'{a.__class__.__name__} has default_value'

        ast_cls = a.__class__

        if ast_cls is TypeVar:
            if not is_FST:
                a = Name(id=a.name)
            else:
                a = Name(id=a.name, ctx=Load(), lineno=a.lineno, col_offset=a.col_offset,
                         end_lineno=a.end_lineno, end_col_offset=a.end_col_offset)

        elif ast_cls is TypeVarTuple:
            name = a.name

            if not is_FST:  # may not have location attrs
                a = Starred(value=Name(id=name))

            else:
                lineno = a.lineno
                end_lineno = a.end_lineno
                col_offset = a.col_offset
                end_col_offset = a.end_col_offset

                a = Starred(value=Name(id=name, ctx=Load(), lineno=end_lineno,
                                       col_offset=end_col_offset - len(name.encode()),
                                       end_lineno=end_lineno, end_col_offset=end_col_offset),
                            ctx=Load(), lineno=lineno, col_offset=col_offset, end_lineno=end_lineno,
                            end_col_offset=end_col_offset)

        else:
            return f'has {ast_cls.__name__}'

        elts.append(a)

    if not is_FST:
        ret = Tuple(elts=elts)
    else:
        ret = Tuple(elts=elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                    end_col_offset=ast.end_col_offset)

    return ret, 2, True

_AST_COERCE_TO_EXPR_FUNCS = {
    Module:             _coerce_to_expr_ast_stmtmod,
    Interactive:        _coerce_to_expr_ast_stmtmod,
    Expression:         _coerce_to_expr_ast_Expression,
    Expr:               _coerce_to_expr_ast_Expr,
    _Assign_targets:    _coerce_to_expr_ast__Assign_targets,
    _decorator_list:    _coerce_to_expr_ast__decorator_list,
    _arglikes:          _coerce_to_expr_ast__arglikes,
    _comprehension_ifs: _coerce_to_expr_ast__comprehension_ifs,
    Set:                _coerce_to_expr_ast_List_or_Set,  # inter-expression coerce
    List:               _coerce_to_expr_ast_List_or_Set,  # inter-expression coerce
    Tuple:              _coerce_to_expr_ast_Tuple,
    arguments:          _coerce_to_expr_ast_arguments,
    arg:                _coerce_to_expr_ast_arg,
    alias:              _coerce_to_expr_ast_alias,  # can reparse in case of FST
    _aliases:           _coerce_to_expr_ast__aliases,
    withitem:           _coerce_to_expr_ast_withitem,
    _withitems:         _coerce_to_expr_ast__withitems,
    MatchValue:         _coerce_to_expr_ast_MatchValue,
    MatchSingleton:     _coerce_to_expr_ast_MatchSingleton,
    MatchSequence:      _coerce_to_expr_ast_MatchSequence,  # recurses
    MatchMapping:       _coerce_to_expr_ast_MatchMapping,  # recurses
    MatchClass:         _coerce_to_expr_ast_MatchClass,  # recurses
    MatchStar:          _coerce_to_expr_ast_MatchStar,
    MatchAs:            _coerce_to_expr_ast_MatchAs,
    MatchOr:            _coerce_to_expr_ast_MatchOr,  # recurses
    _pattern_attrlikes: _coerce_to_expr_ast__pattern_attrlikes,  # recurses
    TypeVar:            _coerce_to_expr_ast_TypeVar,
    TypeVarTuple:       _coerce_to_expr_ast_TypeVarTuple,
    _type_params:       _coerce_to_expr_ast__type_params,
}


def _coerce_to_expr_ast(
    ast: AST,
    is_FST: bool,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    expecting: str = 'expression',
    unmake: bool = True,
    two_step: bool | type[AST] = False,
) -> tuple[AST, bool]:
    """This is not like the `_coerce_to_?()` functions below, it just tries to coerce an `AST` to an expression `AST`,
    mostly by taking a contained expression `AST` but maybe by creating a new one from a string. Parsing is a possible
    action in case of `is_FST=True`. If is not an `FST` then it is assumed the node will be unparsed and reparsed so
    node creation in that case is just targetted at the `unparse()` and may not have locations or other things a full
    node would.

    If the `ast` is a `List` or `Set` then it will be coerced to a `Tuple` on the assumption that we are coercing
    sequences. If it is another type of expression then it is returned unchanged.

    This function will unmake the source `FST` if is one if a coercion occurs (meaning if is non-seq `expr` coming in
    then will not unmake).

    **WARNING!** Can not assume any `AST` nodes returned from here have valid `FST` nodes even if `is_FST=True`. They
    must always be recreated.

    **Parameters:**
    - `ast`: The `AST` node to coerce, can be part of an `FST` tree.
    - `is_FST`: Whether the `ast` node is part of an `FST` tree, meaning it has source for any possible reparse which
        should be done in that case to get the correct locations.
    - `expecting`: Text for error messages.
    - `unmake`: Whether to unmake an `FST` node or the caller will take care of it. This should be `False` for recursed
        coercion as the tree structure needs to remain valid for possible modifications like parsentheses.
    - `two_step`: This enables two-step coercion like `Expr` -> `Set` -> `Tuple` or `MatchSequence` -> `List` ->
        `Tuple`. If this is an `AST` type instead of a bool then two-step is enabled but the target is specified by the
        type so if the first step arrives at it the second step is not taken to `Tuple`.

    **Returns:**
    - `(AST, is_nonstandard_tuple)`: The coerced `AST` and a bool indicating whether it is a nonstandard tuple, which
        means it needs to be fixed with `_fix_Tuple()` because is unparenthesized and may be empty and may not have
        trailing comma on singleton, also start and stop locations may be incorrect. Ignore nonstandard bool if is not
        `FST`.
    """

    ret = _AST_COERCE_TO_EXPR_FUNCS.get(
        ast.__class__, _coerce_to_expr_ast_maybe_expr)(ast, is_FST, options, parse_params)

    if isinstance(ret, str):
        raise _coerce_error(expecting, ast, ret)  # ret here is reason str

    ret, unmake_which, is_nonstd_tuple = ret

    if two_step and (ret_cls := ret.__class__) is not two_step and ret_cls in ASTS_LEAF_LIST_OR_SET:
        if not hasattr(ret, 'f'):  # HACK HACK HACK HAAAAAAAACK!!!
            ret.f = nspace(root=nspace(_lines=(f := ast.f)._lines), loc=f.loc)  # only for the location and lines because we KNOW thats all _coerce_to_expr_ast_List_or_Set() uses it for

        ret = _coerce_to_expr_ast_List_or_Set(ret, is_FST, options, parse_params)

        if isinstance(ret, str):
            raise _coerce_error(expecting, ast, ret)  # pragma: no cover  # can't currently happen as List and Set can always coerce to each other

        ret = ret[0]  # don't even check for is_nonstd_tuple because wasn't tuple and this one isn't either
        unmake_which = 2  # at this point its just safer and easier

    if is_FST and unmake:
        if not unmake_which:  # WARNING! make sure ast is only child of parent and whole parent chain is only-children if coerced!!!
            ret.f._unmake_fst_parents()
        elif unmake_which == 1:  # just the root node (and ctx if it has one)
            ast.f._unmake_fst_parents(True)
        elif unmake_which == 2:  # node was completely regenerated, unmake whole original (e.g. arg.arg coerced to new Name node, or complicated MatchSequence with nested stuff)
            ast.f._unmake_fst_tree()

    return ret, is_nonstd_tuple


# ......................................................................................................................
# coercion support functions

def _coerce_to_seq(
    code: Code,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST] | None,
    to_cls: type[AST],
    ret_elts: bool = False,
    allow_starred: bool = False,
) -> fst.FST | list[AST] | tuple[list[AST], bool] | None:
    """Attempt coerce of given `code` if is sequence type to list of `AST` elements. Meant for conversion to one of our
    own SPECIAL SLICE types that has commas like `_arglikes`, `_aliases`, `_withitems` or `_type_params` or other
    non-expr "sequences" like `arguments`.

    Contrary to the name, this is also used by the non-comma delimited custom `_slice` SPECIAL SLICEs `_Assign_targets`,
    `_decorator_list` and `_comprehension_ifs` as the first step of their coercion.

    We don't deal with possible arglike-only `Starred` elements here explicitly, except in the case of passing through
    `options` in case `_expr_arglikes` doesn't want them parenthesized when coming from `_arglikes`.

    **Prameters:**
    - `parse`: Can be `None` if `ret_elts=True`.
    - `ret_elts`: When to return just the elements and not make an `FST`.
        - `True`: Always return just the elements. In this case returns a tuple of `(elts, is_FST)`.
        - `False`: For an `FST` return just the elements. For an `AST` do the parse and return the parsed `FST`.

    **Returns:**
    - `FST`: Coerced tree ready for return, from an `AST` only.
    - `list[AST]`: Came from an `FST` so wasn't parsed so may need to coerce the individual elements, they are all valid
        `FST` `AST` nodes so need to unmake them if recreating nodes.
    - `(list[AST], is_FST)`: Just the individual elements, which may or may not have come from an `FST`, as well as a
        bool indicating this (if from `FST` or not).
    - `None`: Coercion doesn't apply, try others.
    """

    ast = code
    ast_cls = ast.__class__

    if is_FST := issubclass(ast_cls, fst.FST):
        ast = code.a
        ast_cls = ast.__class__

    if ast_cls not in _ASTS_LEAF_EXPRISH_SEQ:
        return None  # TODO: add coerce from Expr Tuple / List / Set?

    if ast_cls not in ASTS_LEAF_TUPLE_LIST_OR_SET:
        if is_FST and ast_cls is MatchSequence and code.is_delimited_matchseq():
            code._trim_delimiters()

        ast, _ = _coerce_to_expr_ast(ast, is_FST, options, parse_params, to_cls.__name__)

    else:
        if ast_cls is Tuple:
            if any(e.__class__ is Slice for e in ast.elts):
                raise _coerce_error(to_cls, 'Tuple', 'has Slice')

        if is_FST:
            if code.is_parenthesized_tuple() is not False:
                code._trim_delimiters()

            getattr(codea := code.a, 'ctx', codea).f._unmake_fst_parents(True)  # if there is a ctx then make sure to unmake that as well

    if not allow_starred and any(e.__class__ is Starred for e in ast.elts):
        raise _coerce_error(to_cls, ast_cls, 'has Starred')

    if ret_elts:
        return ast.elts, is_FST

    if is_FST:
        return ast.elts

    trim_end = -2 if ast.__class__ is Tuple and len(ast.elts) == 1 else -1  # singleton tuple should remove trailing comma
    src = unparse(ast)[1 : trim_end]  # need to strip Tuple or List or Set unparsed delimiters
    lines = src.split('\n')
    ast = parse(src, parse_params)

    assert ast.__class__ is to_cls  # sanity check

    return fst.FST(ast, lines, None)


def _coerce_to__aliases_common(
    code: Code,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    expecting: str,
    strip: bool,
    allow_dotted: bool,
) -> fst.FST | None:
    """Common to `_aliases`, `Import_names` and `ImportFrom_names`."""

    codea = code.a if isinstance(code, fst.FST) else None

    fst_ = _coerce_to_seq(code, options, parse_params, parse, _aliases)

    if fst_ is None:  # sequence as sequence?
        return None

    if isinstance(fst_, list):  # this means code is an FST
        elts = fst_
        ast = Tuple(elts=elts, ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                    end_col_offset=ls[-1].lenbytes)
        tmp = fst.FST(ast, ls, None, from_=code, lcopy=False)  # temporary Tuple so that we can unparenthesize everything
        names = []

        for e in elts:
            e.f._unparenthesize_grouping(False)  # names can't have pars

            if (e_cls := e.__class__) is Name:
                a = alias(name=e.id, lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                          end_col_offset=e.end_col_offset)

            elif e_cls is Attribute and allow_dotted:
                attr = e.attr
                ee = e

                while (ee_cls := (ee := ee.value).__class__) is Attribute:
                    ee.f._unparenthesize_grouping(False)

                    attr = f'{ee.attr}.{attr}'

                if ee_cls is not Name:
                    raise _coerce_error(expecting, codea, f'has {ee_cls.__qualname__}')

                ee.f._unparenthesize_grouping(False)

                a = alias(name=f'{ee.id}.{attr}', lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                          end_col_offset=e.end_col_offset)

            else:
                raise _coerce_error(expecting, codea, f'has {e_cls.__qualname__}')

            names.append(a)

        tmp._unmake_fst_tree()

        ast = _aliases(names=names, lineno=1, col_offset=0, end_lineno=tmp.end_lineno,
                       end_col_offset=tmp.end_col_offset)
        fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

        if names := fst_.a.names:  # remove trailing comma if present, not legal in Import/From names mostly (except parenthesized ImportFrom.names)
            _, _, ln, col = names[-1].f.loc
            _, _, end_ln, end_col = fst_.loc

            if (frag := next_frag(fst_._lines, ln, col, end_ln, end_col)) and frag.src.startswith(','):
                ln, col, _ = frag

                fst_._put_src(None, ln, col, ln, col + 1, True)

    return fst_.strip() if strip else fst_


def _coerce_to__arglike_ast_TypeVar(
    ast: AST,
    is_FST: bool,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    expecting: str = 'expression (arglike)',
) -> AST:
    """Quick convert `TypeVar` to either an `expr_arglike` or a `kw=val` `keyword`."""

    if ast.bound:
        raise _coerce_error(expecting, 'TypeVar', 'has bound')

    name = ast.name

    if not (value := getattr(ast, 'default_value', None)):
        if not is_FST:
            ast = Name(id=name)
        else:
            ast = Name(id=name, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset,
                       end_lineno=ast.end_lineno, end_col_offset=ast.end_col_offset)

    elif not is_FST:
        ast = keyword(arg=name, value=value)

    else:
        _, _, end_ln, end_col = value.f.pars()

        ast = keyword(arg=name, value=value, lineno=ast.lineno, col_offset=ast.col_offset,
                      end_lineno=end_ln + 1, end_col_offset=ast.f.root._lines[end_ln].c2b(end_col))  # we could make a blank keyword then _set_field() the value from the existing one but wouldn't really save much and is messier

    return ast


def _coerce_to__arglike_ast_ParamSpec(
    ast: AST,
    is_FST: bool,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    expecting: str = 'expression (arglike)',
) -> AST:
    """Quick convert `ParamSpec` a `**kw` `keyword`."""

    if getattr(ast, 'default_value', None):
        raise _coerce_error(expecting, 'ParamSpec', 'has default_value')

    name = ast.name

    if not is_FST:
        ast = keyword(arg=None, value=Name(id=name))

    else:
        end_lineno = ast.end_lineno
        end_col_offset = ast.end_col_offset

        ast = keyword(arg=None, value=Name(id=name, ctx=Load(), lineno=ast.end_lineno,
                                           col_offset=end_col_offset - len(name.encode()), end_lineno=end_lineno,
                                           end_col_offset=end_col_offset),
                      lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=end_lineno,
                      end_col_offset=end_col_offset)

    return ast


def _coerce_to_argument_ast_keyword(
    ast: AST,
    is_FST: bool,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    expecting: str = 'arguments',
) -> tuple[arg, AST] | arg:  # (arg, default) | kwarg
    """Quick convert `keyword` to either `arg` and `default` or `kwarg` suitable for `arguments`."""

    arg_ = ast.arg
    value = ast.value

    if arg_ is not None:  # arg=value
        if not is_FST:
            arg_ = arg(arg=arg_)

        else:
            lineno = ast.lineno
            col_offset = ast.col_offset

            arg_ = arg(arg=arg_, lineno=lineno, col_offset=col_offset, end_lineno=lineno,
                       end_col_offset=col_offset + len(arg_.encode()))

        return arg_, value

    # **kwarg

    if value.__class__ is not Name:
        raise _coerce_error(expecting, 'keyword', "'**' value must be Name")

    if not is_FST:
        return arg(arg=value.id)

    value.f._unparenthesize_grouping(False)  # arg name cannot be parenthesized

    return arg(arg=value.id, lineno=value.lineno, col_offset=value.col_offset, end_lineno=value.end_lineno,
               end_col_offset=value.end_col_offset)


def _coerce_to_argument_ast_Starred(
    ast: AST,
    is_FST: bool,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    expecting: str = 'arguments',
) -> AST:  # vararg
    """Quick convert `Starred` to `vararg` suitable for `arguments`."""

    value = ast.value

    if value.__class__ is not Name:
        raise _coerce_error(expecting, 'Starred', "value must be Name")

    if not is_FST:
        return arg(arg=value.id)

    ast.f._unparenthesize_grouping(False)  # vararg cannot be parenthesized

    return arg(arg=value.id, lineno=value.lineno, col_offset=value.col_offset, end_lineno=value.end_lineno,
               end_col_offset=value.end_col_offset)


def _coerce_to_argument_ast_TypeVar(
    ast: AST,
    is_FST: bool,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    expecting: str = 'arguments',
    is_lambda: bool = False,
) -> tuple[AST, AST | None]:  # (arg, default | None)
    """Quick convert `TypeVar` to `arg` and `default` suitable for `arguments`."""

    name = ast.name
    bound = ast.bound
    lineno = ast.lineno
    col_offset = ast.col_offset

    if not bound:
        if not is_FST:
            arg_ = arg(arg=name)
        else:
            arg_ = arg(arg=name, lineno=lineno, col_offset=col_offset, end_lineno=lineno,
                       end_col_offset=col_offset + len(name.encode()))

    elif is_lambda:
        raise _coerce_error(expecting, 'TypeVar', 'has bound')

    elif not is_FST:
        arg_ = arg(arg=name, annotation=bound)

    else:
        _, _, end_ln, end_col = bound.f.pars()

        arg_ = arg(arg=name, annotation=bound, lineno=lineno, col_offset=col_offset, end_lineno=end_ln + 1,
                   end_col_offset=ast.f.root._lines[end_ln].c2b(end_col))

    if default_value := getattr(ast, 'default_value', None):
        return arg_, default_value

    return arg_, None


def _coerce_to_argument_ast_TypeVarTuple_or_ParamSpec(
    ast: AST,
    is_FST: bool,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    expecting: str = 'arguments',
) -> AST:  # vararg | kwarg
    """Quick convert `TypeVarTuple` to `vararg` or `ParamSpec` to `kwarg` suitable for `arguments`."""

    if getattr(ast, 'default_value', None):
        raise _coerce_error(expecting, ast, 'has default_value')

    name = ast.name
    end_lineno = ast.end_lineno
    end_col_offset = ast.end_col_offset

    if not is_FST:
        return arg(arg=name)

    return arg(arg=name, lineno=end_lineno, col_offset=end_col_offset - len(name.encode()),
               end_lineno=end_lineno, end_col_offset=end_col_offset)


# ......................................................................................................................
# actual coercion functions used by code_as_*() functions

def _coerce_to_stmt(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = code_as_expr(code, options, parse_params, strip=strip, coerce=True)
    ast_ = fst_.a

    lines = fst_._lines
    pars = fst_.pars()
    ln, col, end_ln, end_col = pars
    new_ln, _ = lline_start(lines, 0, 0, ln, col)  # new_col will be at 0, guaranteed

    if col or new_ln != ln:
        fst_._put_src(None, new_ln, 0, ln, col, True)

        if end_ln == ln:
            end_col -= col

        end_ln -= ln - new_ln

    ast = Expr(value=None, lineno=new_ln + 1, col_offset=0, end_lineno=end_ln + 1,
               end_col_offset=lines[end_ln].c2b(end_col))
    fst_ = fst.FST(ast, lines, None, from_=fst_, lcopy=False)._set_field(ast_, 'value', True, False)

    _par_if_needed(ast_.f, bool(pars.n))

    return fst_


def _coerce_to_stmts(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    code_cls = code.__class__

    if issubclass(code_cls, fst.FST):
        codea = code.a
        codea_cls = codea.__class__

        if codea_cls in ASTS_LEAF_STMT:
            ast = Module(body=[], type_ignores=[])

            return fst.FST(ast, code.lines, None, from_=code, lcopy=False)._set_field([codea], 'body', True, False)

        if codea_cls is Interactive:
            code._unmake_fst_parents(True)

            ast = Module(body=[], type_ignores=[])

            return fst.FST(ast, code.lines, None, from_=code, lcopy=False)._set_field(codea.body, 'body', True, False)

    elif code_cls in ASTS_LEAF_STMT_OR_STMTMOD:
        ast = Module(body=code.body if code_cls is Interactive else [code], type_ignores=[])
        src = _fixing_unparse(code)
        lines = src.split('\n')

        return fst.FST(parse_stmts(src, parse_params), lines, None, parse_params=parse_params)

    fst_ = _coerce_to_stmt(code, options, parse_params, strip=strip)

    ast = Module(body=[], type_ignores=[])

    return fst.FST(ast, fst_.lines, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'body', True, False)


def _coerce_to_match_case(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if isinstance(code, fst.FST) else code

    raise _coerce_error('match_case', codea)  # if got here then is not match_case and we do not coerce down from _match_cases, so automatically fail


def _coerce_to__match_cases(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    code_cls = code.__class__

    if issubclass(code_cls, fst.FST):
        codea = code.a
        codea_cls = codea.__class__

        if codea_cls is match_case:
            return fst.FST(_match_cases(cases=[codea], lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                        end_col_offset=ls[-1].lenbytes), ls, None, from_=code, lcopy=False)

        raise _coerce_error('_match_cases', codea_cls)

    elif code_cls is match_case:
        code = _fixing_unparse(code)
        lines = code.split('\n')

        return fst.FST(parse__match_cases(code, parse_params), lines, None, parse_params=parse_params)

    raise _coerce_error('_match_cases', code_cls)


def _coerce_to_Set(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    return _coerce_to_List(code, options, parse_params, strip=strip, to_cls=Set)


def _coerce_to_List(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    to_cls: type[AST] = List,
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`.

    This function handles both `List` and `Set` which is selected by the `to_cls` parameter.
    """

    if to_cls is List:
        delims = '[]'
    else:
        delims = '{}'

        assert to_cls is Set

    if isinstance(code, fst.FST):
        codea = code.a

        ast, fix_coerced_tuple = _coerce_to_expr_ast(code.a, True, options, parse_params, to_cls.__name__,
                                                     two_step=to_cls)
        ast_cls = ast.__class__

        if ast_cls is to_cls:
            code = fst.FST(ast, code._lines, None, from_=code, lcopy=False)  # no fixes needed, already a to_cls

        elif ast_cls is not Tuple:
            raise _coerce_error(to_cls, codea)

        else:
            if to_cls is List:
                ast = List(elts=ast.elts, ctx=Load(), lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                           end_col_offset=ast.end_col_offset)
            else:
                ast = Set(elts=ast.elts, lineno=ast.lineno, col_offset=ast.col_offset, end_lineno=ast.end_lineno,
                          end_col_offset=ast.end_col_offset)

            lines = code._lines
            code = fst.FST(ast, lines, None, from_=code, lcopy=False)  # first we convert to tuple for fixes
            elts = ast.elts

            if fix_coerced_tuple:
                code._fix_undelimited_seq(elts, delims, True)
            elif not code._is_delimited_seq():
                code._delimit_node(True, delims)

            else:
                ln, col, end_ln, end_col = code.loc

                lines[end_ln] = bistr(f'{(l := lines[end_ln])[:end_col - 1]}{delims[1]}{l[end_col:]}')  # just replace the '()' delimiters
                lines[ln] = bistr(f'{(l := lines[ln])[:col]}{delims[0]}{l[col + 1:]}')

            if not elts and to_cls is Set:
                code._fix_Set(fst.FST._get_opt_eff_set_norm_get(options))

    else:  # is AST
        ast, _ = _coerce_to_expr_ast(code, False, options, parse_params, to_cls.__name__, two_step=to_cls)
        ast_cls = ast.__class__

        if ast_cls is not to_cls:
            if ast_cls is not Tuple:
                raise _coerce_error(to_cls, code)

            ast = to_cls(elts=ast.elts)

        src = unparse(ast)
        lines = src.split('\n')
        ast = (parse_List if to_cls is List else parse_Set)(src, parse_params)

        code = fst.FST(ast, lines, None, parse_params=parse_params)

    return code.strip() if strip else code


def _coerce_to_Dict(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code

    ast, _ = _coerce_to_expr_ast(codea, is_FST, options, parse_params, 'Dict')

    if ast.__class__ is not Dict:
        raise _coerce_error('Dict', codea)

    if is_FST:
        fst_ = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

        if strip:
            fst_.strip()

    else:  # is AST
        src = unparse(ast)
        lines = src.split('\n')
        ast = parse_expr(src, parse_params)

        fst_ = fst.FST(ast, lines, None, parse_params=parse_params)

    return fst_


def _coerce_to_MatchMapping(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if isinstance(code, fst.FST) else code

    fst_ = _coerce_to_pattern(code, options, parse_params, strip=strip)

    if fst_.a.__class__ is not MatchMapping:  # only this can coerce to a MatchMapping
        raise _coerce_error('MatchMapping', codea)

    return fst_


def _coerce_to__Assign_targets(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """These are coerce functions which attempt to convert to a specific type of node. For the most part and unless
    explicitly permitted, they only guarantee attempted coercion from an `AST` of `FST`, not source, even if that might
    work as a side-effect of how they coerce.

    If a coerce function can handle source (because we want to be able to parse a different source representation of the
    node than the one the default parse function for the type handles), then the attribute `allow_coerce_src=True`
    should be set on the function. Most should have not present (same as `False`) as the parse attempt should already
    have given a definitive answer. Exists for stuff like `_decorator_names` and `_comprehension_ifs` where those parse
    functions expect a prefix like `@` or `if` but we want to allow source expressions without the prefixes as well when
    `coerce=True`.
    """

    if not isinstance(code, (str, list)):  # this function accepts source so make sure is not that
        codea = code.a if isinstance(code, fst.FST) else None

        elts = _coerce_to_seq(code, options, parse_params, None, _Assign_targets, True, True)

        if elts is not None:  # sequence as sequence?
            elts, is_FST = elts

            if not is_FST:
                src = unparse(_Assign_targets(targets=elts))
                ast = parse__Assign_targets(src, parse_params)

                return fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

            # reformat expression(s) source as targets

            ast = _Assign_targets(targets=elts, lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)
            lines = fst_._lines
            last_ln = len(lines) - 1  # this never changes because the _put_src() calls are never multiline
            end_ln = end_col = 0

            for e in elts:
                if not is_valid_target(e):
                    raise _coerce_error('_Assign_targets', codea, f'{e.__class__.__name__} is not a target')

                f = e.f
                _, _, end_ln, end_col = f.pars()

                f._set_ctx(Store)

                if frag := next_frag(lines, end_ln, end_col, last_ln, 0x7fffffffffffffff):
                    comma_ln, comma_col, src = frag

                    assert src.startswith(',')

                    if comma_ln == end_ln:
                        fst_._put_src(' =', end_ln, end_col, end_ln, comma_col + 1, True)  # replace from end of expression to just past comma with ' ='
                    else:
                        fst_._put_src(None, comma_ln, comma_col, comma_ln, comma_col + 1, True)  # remove just the comma

                        frag = None

                if not frag:  # need to add equals just to end of expr because no comma or comma on different line
                    fst_._put_src(' =', end_ln, end_col, end_ln, end_col, True, exclude=f, offset_excluded=False)  # replace from end of expression to just past comma with ' ='

            _fix__Assign_targets(fst_)

            if strip:  # won't really do much after adding line continuations but we must do that first to make sure locations are good
                fst_.strip()

            _fix__slice_last_line(fst_, lines, end_ln, end_col, True)

            return fst_

    # single element as sequence

    return _code_as_one__Assign_targets(code, options, parse_params, coerce=True)

_coerce_to__Assign_targets.allow_coerce_src = True


def _code_as_one__Assign_targets(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    fst_ = code_as_expr(code, options, parse_params, strip=True, coerce=coerce)  # strip=True because Assign.targets can't have comments or other things that may break a logical line
    ast_ = fst_.a

    if not is_valid_target(ast_):
        raise _coerce_error('Assign target', ast_, '' if coerce else 'coerce disabled')

    fst_._set_ctx(Store)

    ls = fst_.lines
    ls[-1] = last_line = bistr(ls[-1] + ' =')  # add trailing '=', we know we can just add to last line because it was stripped

    ast = _Assign_targets(targets=[], lineno=1, col_offset=0, end_lineno=len(ls), end_col_offset=last_line.lenbytes)
    fst_ = fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([ast_], 'targets', True, False)  # _set_field() is alternative to putting ast_ in the ast.targets to begin with (only if it is known to be valid FST tree), this won't walk existing valid FST tree unnecessarily

    _fix__Assign_targets(fst_)

    _, _, end_ln, end_col = ast_.f.loc

    _fix__slice_last_line(fst_, fst_._lines, end_ln, end_col, True)

    return fst_


def _coerce_to__decorator_list(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`. This function can coerce source."""

    if not isinstance(code, (str, list)):  # this function accepts source so make sure is not that
        elts = _coerce_to_seq(code, options, parse_params, None, _decorator_list, True)

        if elts is not None:  # sequence as sequence?
            elts, is_FST = elts

            if not is_FST:
                src = unparse(_decorator_list(decorator_list=elts))
                ast = parse__decorator_list(src, parse_params)

                return fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

            # reformat expression(s) source as decorator_list

            ast = _decorator_list(decorator_list=elts, lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                  end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)
            lines = fst_._lines
            last_end_ln = last_end_col = 0
            last_f = None
            maybe_par = []

            for e in elts:
                f = e.f

                if f.is_parenthesized_tuple() is False:
                    f._delimit_node()

                    end_ln, end_col, _, _ = f.loc

                else:  # a parenthesized tuple can still have grouping pars
                    pars = f.pars()
                    end_ln, end_col, _, _ = pars

                    if not pars.n:
                        maybe_par.append(f)

                ln, col = lline_start(lines, last_end_ln, last_end_col, end_ln, end_col)  # start of logical line because decorators must start at start of block indent
                fst_._put_src('\n@' if col else '@', ln, col, end_ln, end_col, True,
                              exclude=last_f, offset_excluded=False)  # put element at line start right after '@', exclude pprevious element from offset because could be pegger right before this one

                last_f = f
                _, _, last_end_ln, last_end_col = f.pars()

                if frag := next_frag(lines, last_end_ln, last_end_col, len(lines) - 1, 0x7fffffffffffffff):
                    comma_ln, comma_col, src = frag

                    assert src.startswith(',')

                    fst_._put_src(None, comma_ln, comma_col, comma_ln, comma_col + 1, True)  # remove comma

            ast.col_offset = 0  # because could have been moved by first insert of '@' before first element, this is the simplest way to correct that

            fst_._touch()

            if strip:
                fst_.strip()

            for f in maybe_par:
                _par_if_needed(f, False)

            _fix__slice_last_line(fst_, lines, last_end_ln, last_end_col)

            return fst_

    # single element as sequence

    return _code_as_one__decorator_list(code, options, parse_params, strip=strip, coerce=True)

_coerce_to__decorator_list.allow_coerce_src = True


def _code_as_one__decorator_list(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    fst_ = code_as_expr(code, options, parse_params, strip=strip, coerce=coerce)
    ast_ = fst_.a

    if ast_.__class__ is Starred:
        raise NodeError('decorator cannot be Starred')

    if fst_.is_parenthesized_tuple() is False:
        fst_._delimit_node()
        ln = fst_.ln
        has_pars = True

    else:
        pars = fst_.pars()
        ln = pars.ln
        has_pars = bool(pars.n)

    fst_._put_src('@', ln, 0, ln, 0, False)  # prepend '@' to expression on line of expression at start to make it a _decorator_list slice

    ast = _decorator_list(decorator_list=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                          end_col_offset=ls[-1].lenbytes)
    fst_ = fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([ast_], 'decorator_list', True, False)

    _par_if_needed(ast_.f, has_pars)

    return fst_


def _coerce_to__arglike(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code
    codea_cls = codea.__class__
    ast = None

    if codea_cls is TypeVar:
        ast = _coerce_to__arglike_ast_TypeVar(codea, is_FST, options, parse_params)
    elif codea_cls is ParamSpec:
        ast = _coerce_to__arglike_ast_ParamSpec(codea, is_FST, options, parse_params)

    if ast is not None:
        if not is_FST:
            src = unparse(ast)
            ast = parse__arglike(src, parse_params)

            fst_ = fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

        else:
            fst_ = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

            if strip:
                fst_.strip()

        return fst_

    # fall through to exprlike coercion, TypeVarTuple is handled in this as it is expression-compatible

    fst_ = code_as_expr_arglike(code, options, parse_params, strip=strip, coerce=True)

    if fst_.is_parenthesized_tuple() is False:
        fst_._delimit_node()

    return fst_


def _coerce_to__arglikes(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code
    codea_cls = codea.__class__
    arglikes = []
    coerced = False

    # from non-expr-compatible

    if codea_cls is arguments:
        if codea.posonlyargs:
            raise _coerce_error('_arglikes', 'arguments', 'has posonlyargs')

        coerced = True
        args = codea.args
        vararg = codea.vararg
        kwonlyargs = codea.kwonlyargs
        kw_defaults = codea.kw_defaults
        kwarg = codea.kwarg
        defaults = codea.defaults

        if is_FST:
            lines = code.root._lines

        for arg_, dflt in zip(args, [None] * (len(args) - len(defaults)) + defaults, strict=True):  # arg and arg=default
            if arg_.annotation:
                raise _coerce_error('_arglikes', 'arguments', 'has annotations')

            name = arg_.arg

            if not dflt:
                if not is_FST:
                    ast = Name(id=name)
                else:
                    ast = Name(id=name, ctx=Load(), lineno=arg_.lineno, col_offset=arg_.col_offset,
                               end_lineno=arg_.end_lineno, end_col_offset=arg_.end_col_offset)

            else:
                if not is_FST:
                    ast = keyword(arg=name, value=dflt)

                else:  # if this then we need to include possible parentheses in keyword
                    _, _, end_ln, end_col = dflt.f.pars()

                    ast = keyword(arg=name, value=dflt, lineno=arg_.lineno, col_offset=arg_.col_offset,
                                  end_lineno=end_ln + 1, end_col_offset=lines[end_ln].c2b(end_col))

            arglikes.append(ast)

        if vararg:  # *vararg
            if vararg.annotation:
                raise _coerce_error('_arglikes', 'arguments', 'vararg has annotation')

            name = vararg.arg

            if not is_FST:
                ast = Starred(value=Name(id=name))

            else:
                ln, col, _, _ = vararg.f._loc_argument()

                ast = (Starred(Name(id=name, ctx=Load(), lineno=vararg.lineno, col_offset=vararg.col_offset,
                                    end_lineno=vararg.end_lineno, end_col_offset=vararg.end_col_offset),
                               ctx=Load(), lineno=ln + 1, col_offset=lines[ln].c2b(col), end_lineno=vararg.end_lineno,
                               end_col_offset=vararg.end_col_offset))

            arglikes.append(ast)

        elif kwonlyargs:  # we have a `*, ` in the arguments, not allowed without a vararg
            raise _coerce_error('_arglikes', 'arguments', "has empty vararg '*'")

        for arg_, dflt in zip(kwonlyargs, kw_defaults, strict=True):  # kwarg and kwarg=kwdefault
            if arg_.annotation:
                raise _coerce_error('_arglikes', 'arguments', 'arg has annotation')

            name = arg_.arg

            if not dflt:
                if defaults:  # call(a=1, b) is invalid
                    raise _coerce_error('_arglikes', 'arguments', 'arg without default follows arg with default')

                if not is_FST:
                    ast = Name(id=name)
                else:
                    ast = Name(id=name, ctx=Load(), lineno=arg_.lineno, col_offset=arg_.col_offset,
                               end_lineno=arg_.end_lineno, end_col_offset=arg_.end_col_offset)

            else:
                if not is_FST:
                    ast = keyword(arg=name, value=dflt)

                else:  # if this then we need to include possible parentheses in keyword
                    _, _, end_ln, end_col = dflt.f.pars()

                    ast = keyword(arg=name, value=dflt, lineno=arg_.lineno, col_offset=arg_.col_offset,
                                  end_lineno=end_ln + 1, end_col_offset=lines[end_ln].c2b(end_col))

            arglikes.append(ast)

        if kwarg:  # **kwarg
            if kwarg.annotation:
                raise _coerce_error('_arglikes', 'arguments', 'kwarg has annotation')

            name = kwarg.arg

            if not is_FST:
                ast = keyword(arg=None, value=Name(id=name))

            else:  # if this then we need to include possible parentheses in keyword
                ln, col, _, _ = kwarg.f._loc_argument()

                ast = keyword(arg=None, value=Name(id=name, ctx=Load(), lineno=kwarg.lineno,
                                                   col_offset=kwarg.col_offset, end_lineno=kwarg.end_lineno,
                                                   end_col_offset=kwarg.end_col_offset),
                              lineno=ln + 1, col_offset=lines[ln].c2b(col), end_lineno=kwarg.end_lineno,
                              end_col_offset=kwarg.end_col_offset)

            arglikes.append(ast)

    elif codea_cls is _type_params:
        coerced = True

        for a in codea.type_params:
            a_cls = a.__class__

            if a_cls is TypeVar:
                ast = _coerce_to__arglike_ast_TypeVar(a, is_FST, options, parse_params)
            elif a_cls is ParamSpec:
                ast = _coerce_to__arglike_ast_ParamSpec(a, is_FST, options, parse_params)
            elif a_cls is TypeVarTuple:
                ast, _ = _coerce_to_expr_ast(a, is_FST, options, parse_params, 'expression (arglike)', unmake=False)

            arglikes.append(ast)

    elif codea_cls is _pattern_attrlikes:
        coerced = True

        if is_FST:
            lines = code._lines

        for pat in codea.patterns:
            ast, _ = _coerce_to_expr_ast(pat, is_FST, options, parse_params, unmake=False)

            arglikes.append(ast)

        for idx, (arg_, pat) in enumerate(zip(codea.kwd_attrs, codea.kwd_patterns, strict=True)):
            ast, _ = _coerce_to_expr_ast(pat, is_FST, options, parse_params, unmake=False)

            if not is_FST:
                ast = keyword(arg=arg_, value=ast)

            else:  # if this then we need to include possible parentheses in keyword
                ln, col, _, _ = code._loc_kwd_attrs(idx)
                _, _, end_ln, end_col = pat.f.pars()

                ast = keyword(arg=arg_, value=ast, lineno=ln + 1, col_offset=lines[ln].c2b(col), end_lineno=end_ln + 1,
                              end_col_offset=lines[end_ln].c2b(end_col))

            arglikes.append(ast)

    # if coercion was done above then final put together of coerced _pattern_attrlikes

    if coerced:
        if not is_FST:
            ast = _arglikes(arglikes=arglikes)
            src = unparse(ast)
            ast = parse__arglikes(src, parse_params)

            fst_ = fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

        else:
            code._unmake_fst_tree()

            ast = _arglikes(arglikes=arglikes, lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                            end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

            if strip:  # doesn't do anything currently but maybe in future will strip inside open containers
                fst_.strip()

        return fst_

    # if coercion not done yet then standard coerce (normal expr / pattern)

    fst_ = _coerce_to_seq(code, options, parse_params, parse__arglikes, _arglikes, None, True)

    if fst_ is not None:  # sequence as sequence?
        if isinstance(fst_, list):  # this means code is an FST
            ast = _arglikes(arglikes=fst_, lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                            end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

        if strip:
            fst_.strip()

    else:  # single element as sequence
        fst_ = code_as__arglike(code, options, parse_params, strip=strip, coerce=True)

        ast = _arglikes(arglikes=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                        end_col_offset=ls[-1].lenbytes)
        fst_ = fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'arglikes', True, False)

    for a in fst_.a.arglikes:
        _par_if_needed(a.f, None, False, True)

    return fst_


def _coerce_to__comprehensions(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = code_as_comprehension(code, options, parse_params, strip=strip, coerce=True)

    ast = _comprehensions(generators=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                          end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'generators', True, False)


def _coerce_to__comprehension_ifs(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`. This function can coerce source."""

    if not isinstance(code, (str, list)):  # this function accepts source so make sure is not that
        elts = _coerce_to_seq(code, options, parse_params, None, _comprehension_ifs, True)

        if elts is not None:  # sequence as sequence?
            elts, is_FST = elts

            if not is_FST:
                src = unparse(_comprehension_ifs(ifs=elts))
                ast = parse__comprehension_ifs(src, parse_params)

                return fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

            ast = _comprehension_ifs(ifs=elts, lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                     end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)
            lines = fst_._lines
            last_ln = len(lines) - 1  # this never changes because the _put_src() calls are never multiline
            comma_ln = comma_col = -1
            maybe_par = []

            for e in elts:
                f = e.f
                pars = f.pars()
                ln, col, end_ln, end_col = pars

                if not pars.n:
                    maybe_par.append(f)

                if_src = ' if ' if col == comma_col and ln == comma_ln else 'if '  # guard against joining alphanumerics of this if with previous expression, also leave a nice space if right after a par

                if frag := next_frag(lines, end_ln, end_col, last_ln, 0x7fffffffffffffff):
                    comma_ln, comma_col, src = frag

                    assert src.startswith(',')

                    fst_._put_src(None, comma_ln, comma_col, comma_ln, comma_col + 1, True)  # remove comma

                    if comma_ln == ln:
                        comma_col += len(if_src)

                fst_._put_src(if_src, ln, col, ln, col, False)  # add if

            ast.col_offset = 0  # because could have been moved by first insert of 'if ' before first element, this is the simplest way to correct that

            fst_._touch()

            for f in maybe_par:
                _par_if_needed(f, False, False)

            return fst_.strip() if strip else fst_

    # single element as sequence

    return _code_as_one__comprehension_ifs(code, options, parse_params, strip=strip, coerce=True)

_coerce_to__comprehension_ifs.allow_coerce_src = True


def _code_as_one__comprehension_ifs(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    fst_ = code_as_expr(code, options, parse_params, strip=strip, coerce=coerce)
    ast_ = fst_.a

    if ast_.__class__ is Starred:
        raise NodeError('comprehension if cannot be Starred')

    if fst_.is_parenthesized_tuple() is False:
        fst_._delimit_node()

        ln, col, _, _ = fst_.loc
        has_pars = True

    else:
        pars = fst_.pars()
        ln, col, _, _ = pars
        has_pars = bool(pars.n)

    fst_._put_src('if ', ln, col, ln, col, False)  # prepend 'if' to expression to make it a _comprehension_ifs slice, we do it before the container because the container will have to start at 0, 0

    ast = _comprehension_ifs(ifs=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                             end_col_offset=ls[-1].lenbytes)
    fst_ = fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([ast_], 'ifs', True, False)

    _par_if_needed(ast_.f, has_pars)

    return fst_


def _coerce_to_arg(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code
    codea_cls = codea.__class__
    coerced = False

    # from non-expr-compatible

    if codea_cls is arguments:  # only singleton accepted
        coerced = True
        args = codea.args

        if codea.posonlyargs:
            raise _coerce_error('arg', 'arguments', 'has posonlyargs')
        if codea.vararg:
            raise _coerce_error('arg', 'arguments', 'has vararg')
        if codea.kwonlyargs:
            raise _coerce_error('arg', 'arguments', "has empty vararg '*'")
        if codea.kwarg:
            raise _coerce_error('arg', 'arguments', 'has kwarg')
        if codea.defaults:
            raise _coerce_error('arg', 'arguments', 'has defaults')
        if len(args) != 1:
            raise _coerce_error('arg', 'arguments', 'not single argument')

        ast = args[0]

        if not is_FST:
            src = unparse(ast)
        else:  # doesn't matter if annotation is None
            args.clear()  # misc, so doesn't get unmade and remade, safe to do because no FST ops follow

    elif codea_cls is TypeVar:  # from TypeVar: bound or without bound
        if getattr(codea, 'default_value', None):
            raise _coerce_error('arg', 'TypeVar', 'has default_value')

        coerced = True
        name = codea.name
        bound = codea.bound

        if not is_FST:
            src = unparse(arg(arg=name, annotation=bound)) if bound else name

        else:  # doesn't matter if bound is None
            ast = arg(arg=name, annotation=bound, lineno=codea.lineno, col_offset=codea.col_offset,
                      end_lineno=codea.end_lineno, end_col_offset=codea.end_col_offset)

            codea.bound = None  # misc, so doesn't get unmade and remade, safe to do because no FST ops follow

    elif codea_cls is _pattern_attrlikes:  # only singleton accepted
        coerced = True
        patterns = codea.patterns

        if codea.kwd_patterns:
            raise _coerce_error('arg', '_pattern_attrlikes', 'has keyword attrlikes')
        if len(patterns) != 1:
            raise _coerce_error('arg', '_pattern_attrlikes', 'not single pattern attrlike')

        pat = patterns[0]

        if pat.__class__ is not MatchAs:
            raise _coerce_error('arg', '_pattern_attrlikes', 'has non-MatchAs arg')
        if pat.pattern:
            raise _coerce_error('arg', '_pattern_attrlikes', 'MatchAs arg has pattern')

        name = pat.name or '_'  # None == '_'

        if not is_FST:
            ast = arg(arg=name)
            src = unparse(ast)

        else:  # may be parenthesized
            pat.f._unparenthesize_grouping(False)  # arg name cannot be parenthesized

            ast = arg(arg=name, lineno=pat.lineno, col_offset=pat.col_offset, end_lineno=pat.end_lineno,
                      end_col_offset=pat.end_col_offset)

    if coerced:
        if not is_FST:
            ast = parse_arg(src, parse_params)

            fst_ = fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

        else:
            code._unmake_fst_tree()

            fst_ = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

            if strip:
                fst_.strip()

        return fst_

    # coerce to expression first then Name -> arg

    fst_ = code_as_expr(code, options, parse_params, strip=strip, coerce=True)
    ast_ = fst_.a

    if ast_.__class__ is not Name:
        raise _coerce_error('arg', codea)

    fst_._unparenthesize_grouping(False)  # args can't have pars

    ast = arg(arg=ast_.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
              end_col_offset=ast_.end_col_offset)

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_to_keyword(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code
    codea_cls = codea.__class__

    if codea_cls is arguments:  # only singleton accepted
        args = codea.args
        kwarg = codea.kwarg
        defaults = codea.defaults

        if codea.posonlyargs:
            raise _coerce_error('keyword', 'arguments', 'has posonlyargs')
        if codea.vararg:
            raise _coerce_error('keyword', 'arguments', 'has vararg')
        if codea.kwonlyargs:
            raise _coerce_error('keyword', 'arguments', "has empty vararg '*'")
        if len(args) + bool(kwarg) != 1:
            raise _coerce_error('keyword', 'arguments', 'not single argument')

        if kwarg:
            if kwarg.annotation:
                raise _coerce_error('keyword', 'arguments', 'has annotation')

            name = kwarg.arg

            if not is_FST:
                ast = keyword(arg=None, value=Name(id=name))
                src = unparse(ast)

            else:
                ln, col, _, _ = kwarg.f._loc_argument()
                end_lineno = kwarg.end_lineno
                end_col_offset = kwarg.end_col_offset

                ast = keyword(arg=None, value=Name(id=name, ctx=Load(), lineno=end_lineno,
                                                   col_offset=end_col_offset - len(name.encode()),
                                                   end_lineno=end_lineno, end_col_offset=end_col_offset),
                              lineno=ln + 1, col_offset=code._lines[ln].c2b(col),
                              end_lineno=end_lineno, end_col_offset=end_col_offset)

        else:
            arg_ = args[0]

            if len(defaults) != 1:
                raise _coerce_error('keyword', 'arguments', 'no default')
            if arg_.annotation:
                raise _coerce_error('keyword', 'arguments', 'has annotation')

            name = arg_.arg
            dflt = defaults[0]

            if not is_FST:
                ast = keyword(arg=name, value=dflt)
                src = unparse(ast)

            else:
                _, _, end_ln, end_col = dflt.f.pars()  # if this then we need to include possible parentheses in keyword

                ast = keyword(arg=name, value=dflt,
                              lineno=arg_.lineno, col_offset=arg_.col_offset, end_lineno=end_ln + 1,
                              end_col_offset=code._lines[end_ln].c2b(end_col))

            defaults.clear()  # misc, so doesn't get unmade and remade, safe to do because no FST ops follow

    elif codea_cls is TypeVar:  # from `name=default_value`
        if codea.bound:
            raise _coerce_error('keyword', 'TypeVar', 'has bound')

        default_value = getattr(codea, 'default_value', None)

        if not default_value:
            raise _coerce_error('keyword', 'TypeVar', 'has default_value')

        if not is_FST:
            src = unparse(keyword(arg=codea.name, value=default_value))

        else:
            ast = keyword(arg=codea.name, value=default_value, lineno=codea.lineno, col_offset=codea.col_offset,
                          end_lineno=codea.end_lineno, end_col_offset=codea.end_col_offset)

            codea.value = None  # misc, so doesn't get unmade and remade, safe to do because no FST ops follow

    elif codea_cls is ParamSpec:  # from `**name`
        if getattr(codea, 'default_value', None):
            raise _coerce_error('keyword', 'ParamSpec', 'has default_value')

        name = codea.name

        if not is_FST:
            src = f'**{name}'

        else:
            end_lineno = codea.end_lineno
            end_col_offset = codea.end_col_offset

            ast = keyword(arg=None, value=Name(id=name, ctx=Load(), lineno=end_lineno,
                                               col_offset=end_col_offset - len(name.encode()), end_lineno=end_lineno,
                                               end_col_offset=end_col_offset),
                          lineno=codea.lineno, col_offset=codea.col_offset, end_lineno=codea.end_lineno,
                          end_col_offset=codea.end_col_offset)

    elif codea_cls is _pattern_attrlikes:  # only singleton accepted
        kwd_patterns = codea.kwd_patterns

        if codea.patterns:
            raise _coerce_error('keyword', '_pattern_attrlikes', 'has non-keyword attrlike')
        if len(kwd_patterns) != 1:
            raise _coerce_error('keyword', '_pattern_attrlikes', 'not single pattern attrlike')

        name = codea.kwd_attrs[0]
        value, _ = _coerce_to_expr_ast(kwd_patterns[0], is_FST, options, parse_params, unmake=False)

        if not is_FST:
            src = unparse(keyword(arg=name, value=value))

        else:
            lines = code._lines
            ln, col, end_ln, end_col = code._loc_pattern_attrlikes__attr(0)

            ast = keyword(arg=name, value=value, lineno=ln + 1, col_offset=lines[ln].c2b(col),
                          end_lineno=end_ln + 1, end_col_offset=lines[end_ln].c2b(end_col))

    else:
        raise _coerce_error('keyword', codea_cls)

    if not is_FST:
        ast = parse_keyword(src, parse_params)

        fst_ = fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

    else:
        code._unmake_fst_tree()

        fst_ = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

        if strip:  # doesn't do anything currently but maybe in future will strip inside open containers
            fst_.strip()

    return fst_


def _coerce_to_alias(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce "with a as b" items[0] -> "import a as b"? doesn't really seem as something that would ever be used

    codea = code.a if isinstance(code, fst.FST) else code

    fst_ = code_as_expr(code, options, parse_params, strip=True, coerce=True)  # strip because where aliases are used then generally can't have junk, comments specifically would break Import.names aliases
    ast_ = a = fst_.a
    name = ''

    while a.__class__ is Attribute:
        name = f'.{a.attr}{name}'  # we build it up like this because there can be whitespace, line continuations and newlines in the source
        a = a.value

        a.f._unparenthesize_grouping(False)  # aliases can't have pars

    if a.__class__ is not Name:
        raise _coerce_error('alias', codea)

    fst_._unparenthesize_grouping(False)  # aliases can't have pars

    ast = alias(name=a.id + name, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                end_col_offset=ast_.end_col_offset)

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_to__aliases(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce _withitems specially for the "a as b" format? doesn't really seem as something that would ever be used

    if not (fst_ := _coerce_to__aliases_common(code, options, parse_params,
                                               parse__aliases, '_aliases', strip, True)):  # sequence as sequence?
        fst_ = code_as_alias(code, options, parse_params, strip=strip, coerce=True)  # single element as sequence

        ast = _aliases(names=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                       end_col_offset=ls[-1].lenbytes)
        fst_ = fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'names', True, False)

    _fix__aliases(fst_)

    return fst_


_coerce_to__Import_name = _coerce_to_alias


def _coerce_to__Import_names(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce _withitems specially for the "a as b" format? doesn't really seem as something that would ever be used

    if not (fst_ := _coerce_to__aliases_common(code, options, parse_params,
                                               parse__Import_names, 'Import names', strip, True)):  # sequence as sequence?
        fst_ = code_as_Import_name(code, options, parse_params, strip=strip, coerce=True)  # single element as sequence

        ast = _aliases(names=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                    end_col_offset=ls[-1].lenbytes)
        fst_ = fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'names', True, False)

    _fix__aliases(fst_)

    return fst_


def _coerce_to__ImportFrom_name(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if isinstance(code, fst.FST) else code

    fst_ = code_as_expr(code, options, parse_params, strip=True, coerce=True)  # strip because where aliases are used then generally can't have junk, comments specifically would break Import.names aliases
    ast_ = fst_.a

    if ast_.__class__ is not Name:
        raise _coerce_error('ImportFrom.names alias', codea)

    fst_._unparenthesize_grouping(False)  # aliases can't have pars

    ast = alias(name=ast_.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                end_col_offset=ast_.end_col_offset)

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)


def _coerce_to__ImportFrom_names(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce _withitems specially for the "a as b" format? doesn't really seem as something that would ever be used

    if not (fst_ := _coerce_to__aliases_common(code, options, parse_params,
                                               parse__ImportFrom_names, 'ImportFrom names', strip, False)):  # sequence as sequence?
        fst_ = code_as_ImportFrom_name(code, options, parse_params, strip=strip, coerce=True)  # single element as sequence

        ast = _aliases(names=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                    end_col_offset=ls[-1].lenbytes)
        fst_ = fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'names', True, False)

    _fix__aliases(fst_)

    return fst_


def _coerce_to_arguments(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    parse: Callable[[Code, Mapping[str, Any]], AST] = parse_arguments,
) -> fst.FST | None:
    """See `_coerce_to__Assign_targets()`. Common to `arguments`, both normal and lambda."""

    is_lambda = parse is parse_arguments_lambda
    expecting = 'lambda arguments' if is_lambda else 'arguments'

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code
    codea_cls = codea.__class__
    posonlyargs = args = vararg = kwonlyargs = kw_defaults = kwarg = defaults = None
    coerced = False

    # from non-expr-compatible

    if codea_cls is keyword:
        coerced = True
        res = _coerce_to_argument_ast_keyword(codea, is_FST, options, parse_params, expecting)

        if isinstance(res, arg):  # kwarg
            kwarg = res

        else:  # (arg, default)
            arg_, default = res
            args = [arg_]
            defaults = [default]

    elif codea_cls is Starred:
        coerced = True
        vararg = _coerce_to_argument_ast_Starred(codea, is_FST, options, parse_params, expecting)

    elif codea_cls is _arglikes:
        coerced = True
        args = []
        defaults = []
        kwonlyargs = []
        kw_defaults = []

        for a in codea.arglikes:
            if kwarg:
                raise _coerce_error(expecting, '_arglikes', 'has args after kwarg')

            a_cls = a.__class__

            if a_cls is Name:
                if not is_FST:
                    arg_ = arg(arg=a.id)

                else:
                    a.f._unparenthesize_grouping(False)  # arg name cannot be parenthesized

                    arg_ = arg(arg=a.id, lineno=a.lineno, col_offset=a.col_offset, end_lineno=a.end_lineno,
                               end_col_offset=a.end_col_offset)

                if vararg:
                    kwonlyargs.append(arg_)
                    kw_defaults.append(None)  # can be None

                elif defaults:
                    raise _coerce_error(expecting, '_arglikes', 'arg without default follows arg with default')
                else:
                    args.append(arg_)

            elif a_cls is Starred:
                if vararg:
                    raise _coerce_error(expecting, '_arglikes', 'has multiple Starred')

                vararg = _coerce_to_argument_ast_Starred(a, is_FST, options, parse_params, expecting)

            elif a_cls is keyword:
                res = _coerce_to_argument_ast_keyword(a, is_FST, options, parse_params, expecting)

                if isinstance(res, arg):  # kwarg
                    kwarg = res

                else:  # (arg, default)
                    arg_, default = res

                    if vararg:
                        kwonlyargs.append(arg_)
                        kw_defaults.append(default)
                    else:
                        args.append(arg_)
                        defaults.append(default)

            else:  # expression
                raise _coerce_error(expecting, '_arglikes', f'has {a_cls.__name__}')

    elif codea_cls is MatchStar:
        coerced = True
        name = codea.name or '_'  # None == '_'
        end_lineno = codea.end_lineno
        end_col_offset = codea.end_col_offset

        if not is_FST:
            vararg = arg(arg=name)
        else:
            vararg = arg(arg=name, lineno=end_lineno, col_offset=end_col_offset - len(name.encode()),
                         end_lineno=end_lineno, end_col_offset=end_col_offset)

    elif codea_cls is _pattern_attrlikes:
        coerced = True
        args = []
        defaults = []

        if is_FST:
            lines = code._lines

        for pat in codea.patterns:
            if pat.__class__ is not MatchAs:
                raise _coerce_error(expecting, '_pattern_attrlikes', 'has non-MatchAs arg')
            if pat.pattern:
                raise _coerce_error(expecting, '_pattern_attrlikes', 'MatchAs arg has pattern')

            name = pat.name or '_'  # None == '_'

            if is_FST:  # may be parenthesized
                pat.f._unparenthesize_grouping(False)  # arg name cannot be parenthesized

                arg_ = arg(arg=name, lineno=pat.lineno, col_offset=pat.col_offset, end_lineno=pat.end_lineno,
                           end_col_offset=pat.end_col_offset)

            else:
                arg_ = arg(arg=name)

            args.append(arg_)

        for idx, (arg_, pat) in enumerate(zip(codea.kwd_attrs, codea.kwd_patterns, strict=True)):
            default, _ = _coerce_to_expr_ast(pat, is_FST, options, parse_params, unmake=False)

            if not is_FST:
                arg_ = arg(arg=arg_)

            else:
                ln, col, end_ln, end_col = code._loc_kwd_attrs(idx)

                arg_ = arg(arg=arg_, lineno=ln + 1, col_offset=lines[ln].c2b(col), end_lineno=end_ln + 1,
                           end_col_offset=lines[end_ln].c2b(end_col))

            args.append(arg_)
            defaults.append(default)

    elif codea_cls is TypeVar:
        coerced = True
        arg_, default = _coerce_to_argument_ast_TypeVar(codea, is_FST, options, parse_params, expecting, is_lambda)

        args = [arg_]

        if default:
            defaults = [default]

    elif codea_cls is TypeVarTuple:
        coerced = True
        vararg = _coerce_to_argument_ast_TypeVarTuple_or_ParamSpec(codea, is_FST, options, parse_params, expecting)

    elif codea_cls is ParamSpec:
        coerced = True
        kwarg = _coerce_to_argument_ast_TypeVarTuple_or_ParamSpec(codea, is_FST, options, parse_params, expecting)

    elif codea_cls is _type_params:
        coerced = True
        args = []
        defaults = []
        kwonlyargs = []
        kw_defaults = []

        for a in codea.type_params:
            if kwarg:
                raise _coerce_error(expecting, '_type_params', 'has args after kwarg')

            a_cls = a.__class__

            if a_cls is TypeVar:
                arg_, default = _coerce_to_argument_ast_TypeVar(a, is_FST, options, parse_params, expecting, is_lambda)

                if vararg:
                    kwonlyargs.append(arg_)
                    kw_defaults.append(default)  # can be None

                else:
                    args.append(arg_)

                    if default:
                        defaults.append(default)
                    elif defaults:
                        raise _coerce_error(expecting, '_type_params', 'arg without default follows arg with default')

            elif a_cls is TypeVarTuple:
                if vararg:
                    raise _coerce_error(expecting, '_type_params', 'has multiple TypeVarTuple')

                vararg = _coerce_to_argument_ast_TypeVarTuple_or_ParamSpec(a, is_FST, options, parse_params, expecting)

            elif a_cls is ParamSpec:
                kwarg = _coerce_to_argument_ast_TypeVarTuple_or_ParamSpec(a, is_FST, options, parse_params, expecting)

    # if coercion was done above then final put together of coerced _pattern_attrlikes

    if coerced:
        ast = arguments(
            posonlyargs=[] if posonlyargs is None else posonlyargs,
            args=[] if args is None else args,
            vararg=vararg,
            kwonlyargs=[] if kwonlyargs is None else kwonlyargs,
            kw_defaults=[] if kw_defaults is None else kw_defaults,
            kwarg=kwarg,
            defaults=[] if defaults is None else defaults,
        )

        if not is_FST:
            src = unparse(ast)
            ast = parse(src, parse_params)

            fst_ = fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

        else:
            code._unmake_fst_tree()

            fst_ = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

            if strip:  # doesn't do anything currently but maybe in future will strip inside open containers
                fst_.strip()

        return fst_

    # if coercion not done yet then standard coerce sequence

    elts = _coerce_to_seq(code, options, parse_params, parse, arguments, True, True)

    if elts is not None:  # sequence as sequence?
        elts, is_FST = elts

        if not is_FST:
            src = unparse(Tuple(elts=elts))[1:-1]
            ast = parse(src, parse_params)

            return fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

        ast = Tuple(elts=elts, ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                    end_col_offset=ls[-1].lenbytes)
        tmp = fst.FST(ast, ls, None, from_=code, lcopy=False)  # temporary Tuple so that we can unparenthesize everything
        args = []
        ast = arguments(posonlyargs=[], args=args, vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])

        for e in elts:
            e.f._unparenthesize_grouping(False)  # args can't have pars

            if (e_cls := e.__class__) is Name:
                args.append(arg(arg=e.id, lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                                end_col_offset=e.end_col_offset))

            elif e_cls is Starred:
                if ast.vararg:
                    raise _coerce_error(expecting, codea, 'has multiple Starred')

                if (e := e.value).__class__ is not Name:
                    raise _coerce_error(expecting, codea, 'Starred value must be Name')

                ast.vararg = arg(arg=e.id, lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                                 end_col_offset=e.end_col_offset)
                args = ast.kwonlyargs

            else:
                raise _coerce_error(expecting, codea, f'has {e_cls.__name__}')

        ast.kw_defaults = [None] * len(ast.kwonlyargs)

        tmp._unmake_fst_tree()

        fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

        return fst_.strip() if strip else fst_  # TODO; strip undelimited containerslike arguments on the inside because currently strip doesn't do anything here

    # single element as arguments

    fst_ = code_as_arg(code, options, parse_params, strip=strip, coerce=True)
    ast_ = fst_.a

    if is_lambda and ast_.annotation:
        raise _coerce_error('lambda arguments', codea_cls, 'has annotation')

    ast = arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[])

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)._set_field([ast_], 'args', True, False)


def _coerce_to_arguments_lambda(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    return _coerce_to_arguments(code, options, parse_params, strip=strip, parse=parse_arguments_lambda)


def _coerce_to_withitem(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce "import a as b" names[0] -> "with a as b"? doesn't really seem as something that would ever be used

    fst_ = code_as_expr(code, options, parse_params, strip=strip, coerce=True)
    ast_ = fst_.a

    if ast_.__class__ is Starred:
        raise NodeError('Starred not allowed in withitem')

    if fst_.is_parenthesized_tuple() is False:
        fst_._delimit_node()

    ast = withitem(context_expr=None)
    fst_ = fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)._set_field(ast_, 'context_expr', True, False)

    _par_if_needed(ast_.f, None, False)

    return fst_


def _coerce_to__withitems(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    # TODO: coerce _aliases specially for the "a as b" format? doesn't really seem as something that would ever be used

    fst_ = _coerce_to_seq(code, options, parse_params, parse__withitems, _withitems)

    if fst_ is not None:  # sequence as sequence?
        if isinstance(fst_, list):  # this means code is an FST
            items = [withitem(a) for a in fst_]
            ast = _withitems(items=items, lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                             end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

            for a in items:
                _par_if_needed(a.context_expr.f, None, False)

        if strip:
            fst_.strip()

    else: # single element as sequence
        fst_ = code_as_withitem(code, options, parse_params, strip=strip, coerce=True)

        ast = _withitems(items=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                         end_col_offset=ls[-1].lenbytes)
        fst_ = fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'items', True, False)

    for wi in fst_.a.items:
        _par_if_needed(wi.context_expr.f, None, False)

    return fst_


def _coerce_to_pattern(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`. This is essentially the pattern version of `_coerce_to_expr_ast()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code

    ast = _coerce_to_pattern_ast(codea, is_FST, options, parse_params)

    if is_FST:
        fst_ = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

        if strip:
            fst_.strip()

    else:
        src = unparse(ast)
        ret = parse_pattern(src, parse_params)

        assert ret.__class__ is ast.__class__  # sanity check

        fst_ = fst.FST(ret, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

    return fst_


def _coerce_to__pattern_attrlikes(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code
    codea_cls = original_codea_cls = codea.__class__
    patterns = []
    kwd_attrs = []
    kwd_patterns = []

    # from non-expr-compatible

    if codea_cls is keyword:
        set_patterns = False  # flag to build FST from scratch instead of _set_field()
        arg_ = codea.arg

        if arg_ is None:
            raise _coerce_error('_pattern_attrlikes', 'keyword', "is '**'")

        pat = _coerce_to_pattern_ast(codea.value, is_FST, options, parse_params, unmake=False)

        kwd_attrs.append(arg_)
        kwd_patterns.append(pat)

    elif codea_cls is _arglikes:
        set_patterns = False

        for a in codea.arglikes:
            a_cls = a.__class__

            if a_cls is Starred:
                raise _coerce_error('pattern attrlike', 'Starred')

            if a_cls is keyword:
                arg_ = a.arg
                value = a.value

                if arg_ is None:
                    raise _coerce_error('pattern attrlike', 'keyword', "is '**'")

                pat = _coerce_to_pattern_ast(value, is_FST, options, parse_params, unmake=False)

                kwd_attrs.append(arg_)
                kwd_patterns.append(pat)

            else:  # expression
                pat = _coerce_to_pattern_ast(a, is_FST, options, parse_params, unmake=False)

                patterns.append(pat)

    elif codea_cls is arguments:
        if codea.vararg:
            raise _coerce_error('_pattern_attrlikes', 'arguments', 'has vararg')
        if codea.kwarg:
            raise _coerce_error('_pattern_attrlikes', 'arguments', 'has kwarg')
        if codea.posonlyargs:
            raise _coerce_error('_pattern_attrlikes', 'arguments', 'has posonlyargs')
        if codea.kwonlyargs:
            raise _coerce_error('_pattern_attrlikes', 'arguments', 'has kwonlyargs')

        set_patterns = False
        args = codea.args
        defaults = codea.defaults

        for arg_, dflt in zip(args, [None] * (len(args) - len(defaults)) + defaults, strict=True):
            if arg_.annotation:
                raise _coerce_error('pattern attrlike', 'arg', 'has annotation')

            name = arg_.arg

            if dflt:
                pat = _coerce_to_pattern_ast(dflt, is_FST, options, parse_params, unmake=False)

                kwd_attrs.append(name)
                kwd_patterns.append(pat)

            else:
                if name == '_':
                    name = None

                if not is_FST:
                    pat = MatchAs(pattern=None, name=name)
                else:
                    pat = MatchAs(pattern=None, name=name, lineno=arg_.lineno, col_offset=arg_.col_offset,
                                  end_lineno=arg_.end_lineno, end_col_offset=arg_.end_col_offset)

                patterns.append(pat)

    elif codea_cls is TypeVar:
        if codea.bound:
            raise _coerce_error('_pattern_attrlikes', 'TypeVar', 'has bound')

        set_patterns = False
        name = codea.name

        if value := getattr(codea, 'default_value', None):
            pat = _coerce_to_pattern_ast(value, is_FST, options, parse_params, unmake=False)

            kwd_attrs.append(name)
            kwd_patterns.append(pat)

        else:
            if name == '_':
                name = None

            if not is_FST:
                pat = MatchAs(pattern=None, name=name)
            else:
                pat = MatchAs(pattern=None, name=name, lineno=codea.lineno, col_offset=codea.col_offset,
                              end_lineno=codea.end_lineno, end_col_offset=codea.end_col_offset)

            patterns.append(pat)

    elif codea_cls is _type_params:
        set_patterns = False

        for a in codea.type_params:
            a_cls = a.__class__

            if a_cls is not TypeVar:
                raise _coerce_error('pattern attrlike', a_cls)

            name = a.name

            if a.bound:
                raise _coerce_error('pattern attrlike', 'TypeVar', 'has bound')

            if value := getattr(a, 'default_value', None):
                pat = _coerce_to_pattern_ast(value, is_FST, options, parse_params, unmake=False)

                kwd_attrs.append(name)
                kwd_patterns.append(pat)

            else:
                if name == '_':
                    name = None

                if not is_FST:
                    pat = MatchAs(pattern=None, name=name)
                else:
                    pat = MatchAs(pattern=None, name=name, lineno=a.lineno, col_offset=a.col_offset,
                                  end_lineno=a.end_lineno, end_col_offset=a.end_col_offset)

                patterns.append(pat)

    # from generic pattern, with maybe coerce generic to pattern first, expr-compatible sequences come through this

    else:
        set_patterns = None
        original_codea_cls = codea_cls

        if codea_cls not in ASTS_LEAF_PATTERN:  # first lets get a pattern
            code = _coerce_to_pattern(code, options, parse_params, strip=strip)
            codea = code.a
            codea_cls = code.a.__class__
            strip = False
            is_FST = True

        if codea_cls is MatchSequence:
            if any(a.__class__ is MatchStar for a in codea.patterns):
                raise _coerce_error('_pattern_attrlikes', 'MatchSequence', 'has MatchStar')

            if not is_FST:
                src = unparse(codea)[1:-1]  # strip '[]' delimiters at ends

            else:
                if code.is_delimited_matchseq():
                    code._trim_delimiters()

                code._unmake_fst_parents(True)

                set_patterns = codea.patterns

        elif codea_cls in ASTS_LEAF_PATTERN:  # this is essentially one=True
            if codea_cls is MatchStar:
                raise _coerce_error('_pattern_attrlikes', 'MatchStar')

            if not is_FST:
                src = unparse(codea)

            else:
                if code.is_delimited_matchseq() == '':  # undelimited MatchSequence
                    code._delimit_node(delims='[]')

                set_patterns = [codea]

        else:
            raise _coerce_error('_pattern_attrlikes', original_codea_cls)

    # final put together of coerced _pattern_attrlikes

    if not is_FST:
        if set_patterns is False:
            ast = _pattern_attrlikes(patterns=patterns, kwd_attrs=kwd_attrs, kwd_patterns=kwd_patterns)
            src = unparse(ast)

        ast = parse__pattern_attrlikes(src, parse_params)

        fst_ = fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

    else:
        if set_patterns is False:
            code._unmake_fst_tree()

        ast = _pattern_attrlikes(patterns=patterns, kwd_attrs=kwd_attrs, kwd_patterns=kwd_patterns, lineno=1,
                                 col_offset=0, end_lineno=len(ls := code._lines), end_col_offset=ls[-1].lenbytes)
        fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

        if set_patterns:
            fst_._set_field(set_patterns, 'patterns', True, False)

        if strip:  # doesn't do anything currently but maybe in future will strip inside open containers
            fst_.strip()

    return fst_


@pyver(lt=12)
def _coerce_to_type_param(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    raise RuntimeError('type_params do not exist on python < 3.12')


@pyver(ge=12)
def _coerce_to_type_param(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code
    codea_cls = codea.__class__
    coerced = False

    # from non-expr-compatible

    if codea_cls is arg:  # to TypeVar, with or without bound
        coerced = True
        arg_ = codea.arg
        annotation = codea.annotation

        if is_FST:  # doesn't matter if annotation is None
            ast = TypeVar(name=arg_, bound=annotation, lineno=codea.lineno, col_offset=codea.col_offset,
                          end_lineno=codea.end_lineno, end_col_offset=codea.end_col_offset)

            codea.annotation = None  # misc, so doesn't get unmade and remade, safe to do because no FST ops follow

        elif annotation:
            src = unparse(TypeVar(name=arg_, bound=annotation))
        else:
            src = arg_

    elif codea_cls is keyword:  # to TypeVar `name=default_value` or ParamSpec `**name`
        coerced = True
        arg_ = codea.arg
        value = codea.value

        if arg_ is None:  # **kwarg -> ParamSpec
            if value.__class__ is not Name:
                raise _coerce_error('type_param', 'keyword', "'**' value must be Name")

            if not is_FST:
                src = f'**{value.id}'

            else:
                value.f._unparenthesize_grouping(False)  # type_param name cannot be parenthesized

                ast = ParamSpec(name=value.id, lineno=codea.lineno, col_offset=codea.col_offset,
                                end_lineno=value.end_lineno, end_col_offset=value.end_col_offset)

        elif PYLT13:
            raise _coerce_error('type_param', 'keyword', 'default value not allowed on Python < 3.13')

        else:  # arg=value -> TypeVar (py 3.13+)
            if not is_FST:
                src = unparse(TypeVar(name=arg_, default_value=value))

            else:
                _, _, end_ln, end_col = value.f.pars()

                ast = TypeVar(name=arg_, default_value=value, lineno=codea.lineno, col_offset=codea.col_offset,
                              end_lineno=end_ln + 1, end_col_offset=code._lines[end_ln].c2b(end_col))

                codea.value = None  # misc, so doesn't get unmade and remade, safe to do because no FST ops follow

    if coerced:
        if not is_FST:
            ast = parse_type_param(src, parse_params)

            fst_ = fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

        else:
            code._unmake_fst_tree()

            fst_ = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

            if strip:
                fst_.strip()

        return fst_

    # coerce to expression first then Name -> TypeVar or Starred -> TypeVarTuple

    fst_ = code_as_expr(code, options, parse_params, strip=strip, coerce=True)
    ast_ = fst_.a

    if ast_.__class__ is Name:
        fst_._unparenthesize_grouping(False)  # type_params can't have pars

        ast = TypeVar(name=ast_.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                      end_col_offset=ast_.end_col_offset)

    elif ast_.__class__ is Starred:
        if (value := fst_.a.value).__class__ is not Name:
            raise _coerce_error('TypeVarTuple', codea, 'value must be name')

        value.f._unparenthesize_grouping(False)  # type_params can't have pars

        ast = TypeVarTuple(name=value.id, lineno=ast_.lineno, col_offset=ast_.col_offset, end_lineno=ast_.end_lineno,
                           end_col_offset=ast_.end_col_offset)

    else:
        raise _coerce_error('type_param', codea, 'must be name or *name')

    return fst.FST(ast, fst_._lines, None, from_=fst_, lcopy=False)


@pyver(ge=12, else_=_coerce_to_type_param)
def _coerce_to__type_params(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    codea = code.a if (is_FST := isinstance(code, fst.FST)) else code
    codea_cls = codea.__class__
    type_params = []
    coerced = False

    # non expr-compatible

    if codea_cls is arguments:
        if codea.posonlyargs:
            raise _coerce_error('_type_params', 'arguments', 'has posonlyargs')

        coerced = True
        args = codea.args
        vararg = codea.vararg
        kwonlyargs = codea.kwonlyargs
        kw_defaults = codea.kw_defaults
        kwarg = codea.kwarg
        defaults = codea.defaults

        if PYLT13 and (defaults or any(kw_defaults)):
            raise _coerce_error('_type_params', 'arguments', 'default values not allowed on Python < 3.13')

        if kwonlyargs and not vararg:  # we have a `*, ` in the arguments, not allowed without a vararg
            raise _coerce_error('_type_params', 'arguments', "has empty vararg '*'")

        if is_FST:
            lines = code.root._lines

        for is_args, args_n_dflts in [
            (True, zip(args, [None] * (len(args) - len(defaults)) + defaults, strict=True)),
            (False, zip(kwonlyargs, kw_defaults, strict=True)),
        ]:  # args=defaults, kwonlyargs=kw_defaults
            for arg_, dflt in args_n_dflts:  # arg and arg=default
                name = arg_.arg
                annotation = arg_.annotation  # doesn't matter if annotation is None

                if not is_FST:
                    if dflt:
                        ast = TypeVar(name=name, bound=annotation, default_value=dflt)
                    else:
                        ast = TypeVar(name=name, bound=annotation)

                else:
                    if not dflt:
                        ast = TypeVar(name=name, bound=annotation,
                                      lineno=arg_.lineno, col_offset=arg_.col_offset,
                                      end_lineno=arg_.end_lineno, end_col_offset=arg_.end_col_offset)

                    else:  # if this then we need to include possible parentheses in TypeVar
                        _, _, end_ln, end_col = dflt.f.pars()

                        ast = TypeVar(name=name, bound=annotation, default_value=dflt,
                                      lineno=arg_.lineno, col_offset=arg_.col_offset, end_lineno=end_ln + 1,
                                      end_col_offset=lines[end_ln].c2b(end_col))

                type_params.append(ast)

            if is_args and vararg:  # *vararg -> *TypeVarTuple, only do when going from normal args to kwonlyargs
                if vararg.annotation:
                    raise _coerce_error('TypeVarTuple', 'vararg', 'has annotation')

                name = vararg.arg

                if not is_FST:
                    ast = TypeVarTuple(name=name)

                else:
                    ln, col, _, _ = vararg.f._loc_argument()

                    ast = TypeVarTuple(name=name, lineno=ln + 1, col_offset=lines[ln].c2b(col),
                                       end_lineno=vararg.end_lineno, end_col_offset=vararg.end_col_offset)

                type_params.append(ast)

        if kwarg:  # **kwarg -> **ParamSpec
            if kwarg.annotation:
                raise _coerce_error('ParamSpec', 'kwarg', 'has annotation')

            name = kwarg.arg

            if not is_FST:
                ast = ParamSpec(name=name)

            else:
                ln, col, _, _ = kwarg.f._loc_argument()

                ast = ParamSpec(name=name, lineno=ln + 1, col_offset=lines[ln].c2b(col),
                                end_lineno=kwarg.end_lineno, end_col_offset=kwarg.end_col_offset)

            type_params.append(ast)

    elif codea_cls is _arglikes:
        coerced = True

        for a in codea.arglikes:
            a_cls = a.__class__

            if a_cls is Name:
                if not is_FST:
                    ast = TypeVar(name=a.id)

                else:
                    a.f._unparenthesize_grouping(False)  # type_param name cannot be parenthesized

                    ast = TypeVar(name=a.id, lineno=a.lineno, col_offset=a.col_offset, end_lineno=a.end_lineno,
                                  end_col_offset=a.end_col_offset)

            elif a_cls is Starred:
                if (value := a.value).__class__ is not Name:
                    raise _coerce_error('TypeVarTuple', 'Starred', 'value must be Name')

                if not is_FST:
                    ast = TypeVarTuple(name=value.id)

                else:
                    value.f._unparenthesize_grouping(False)  # type_param name cannot be parenthesized

                    ast = TypeVarTuple(name=value.id, lineno=a.lineno, col_offset=a.col_offset, end_lineno=a.end_lineno,
                                       end_col_offset=a.end_col_offset)

            elif a_cls is keyword:
                arg_ = a.arg
                value = a.value

                if arg_ is None:  # **ParamSpec
                    if value.__class__ is not Name:
                        raise _coerce_error('ParamSpec', 'keyword', "'**' value must be Name")

                    if not is_FST:
                        ast = ParamSpec(name=value.id)

                    else:
                        value.f._unparenthesize_grouping(False)  # ParamSpec name cannot be parenthesized

                        ast = ParamSpec(name=value.id, lineno=a.lineno, col_offset=a.col_offset,
                                        end_lineno=value.end_lineno, end_col_offset=value.end_col_offset)

                elif PYLT13:
                    raise _coerce_error('TypeVar', 'keyword', 'default value not allowed on Python < 3.13')

                else:  # TypeVar=default_value
                    if not is_FST:
                        ast = TypeVar(name=arg_, default_value=value)

                    else:
                        ast = TypeVar(name=arg_, default_value=value, lineno=a.lineno, col_offset=a.col_offset,
                                      end_lineno=a.end_lineno, end_col_offset=a.end_col_offset)

                        a.value = None  # misc, so doesn't get unmade and remade, safe to do because no FST ops follow

            else:
                raise _coerce_error('_type_params', '_arglikes', f'has {a_cls.__name__}')

            type_params.append(ast)

    elif codea_cls is _pattern_attrlikes:
        coerced = True
        patterns = codea.patterns
        kwd_patterns = codea.kwd_patterns

        for pat in patterns:
            if pat.__class__ is not MatchAs:
                raise _coerce_error('_type_params', '_pattern_attrlikes', 'has non-MatchAs arg')
            if pat.pattern:
                raise _coerce_error('_type_params', '_pattern_attrlikes', 'MatchAs arg has pattern')

            name = pat.name or '_'  # None == '_'

            if not is_FST:
                ast = TypeVar(name=name)

            else:  # may be parenthesized
                pat.f._unparenthesize_grouping(False)  # type_param name cannot be parenthesized

                ast = TypeVar(name=name, lineno=pat.lineno, col_offset=pat.col_offset, end_lineno=pat.end_lineno,
                              end_col_offset=pat.end_col_offset)

            type_params.append(ast)

        if kwd_patterns:
            if PYLT13:
                raise _coerce_error('_type_params', '_pattern_attrlikes', 'default values not allowed on Python < 3.13')

            if is_FST:
                lines = code.lines

            for idx, (arg_, pat) in enumerate(zip(codea.kwd_attrs, kwd_patterns, strict=True), len(patterns)):
                default_value, _ = _coerce_to_expr_ast(pat, is_FST, options, parse_params, unmake=False)

                if not is_FST:
                    ast = TypeVar(name=arg_, default_value=default_value)

                else:
                    ln, col, end_ln, end_col = code._loc_pattern_attrlikes__attr(idx)

                    ast = TypeVar(name=arg_, default_value=default_value, lineno=ln + 1, col_offset=lines[ln].c2b(col),
                                  end_lineno=end_ln + 1, end_col_offset=lines[end_ln].c2b(end_col))

                type_params.append(ast)

    # if coercion was done above then final put together of coerced _type_params

    if coerced:
        if not is_FST:
            ast = _type_params(type_params=type_params)
            src = unparse(ast)
            ast = parse__type_params(src, parse_params)

            fst_ = fst.FST(ast, src.split('\n'), None, parse_params=parse_params)  # this is already stripped

        else:
            code._unmake_fst_tree()

            ast = _type_params(type_params=type_params, lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                               end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

            if strip:  # doesn't do anything currently but maybe in future will strip inside open containers
                fst_.strip()

        return fst_

    # if coercion not done yet then standard coerce sequence

    fst_ = _coerce_to_seq(code, options, parse_params, parse__type_params, _type_params, None, True)  # sequence as sequence?

    if fst_ is not None:  # sequence as sequence?
        if isinstance(fst_, list):  # this means code is an FST
            elts = fst_
            ast = Tuple(elts=elts, ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                        end_col_offset=ls[-1].lenbytes)
            tmp = fst.FST(ast, ls, None, from_=code, lcopy=False)  # temporary Tuple so that we can unparenthesize everything

            type_params = []

            for e in elts:
                e.f._unparenthesize_grouping(False)  # type_params can't have pars

                if (e_cls := e.__class__) is Name:
                    tp = TypeVar(name=e.id, lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                                 end_col_offset=e.end_col_offset)

                elif e_cls is Starred:
                    if (v := e.value).__class__ is Name:
                        tp = TypeVarTuple(name=v.id, lineno=e.lineno, col_offset=e.col_offset, end_lineno=e.end_lineno,
                                          end_col_offset=e.end_col_offset)
                    else:
                        raise _coerce_error('type_param', 'Starred', 'value must be Name')

                else:
                    raise _coerce_error('type_param', e_cls)

                type_params.append(tp)

            tmp._unmake_fst_tree()

            ast = _type_params(type_params=type_params, lineno=1, col_offset=0, end_lineno=tmp.end_lineno,
                               end_col_offset=tmp.end_col_offset)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

        return fst_.strip() if strip else fst_

    # single element as sequence

    fst_ = code_as_type_param(code, options, parse_params, strip=strip, coerce=True)

    ast = _type_params(type_params=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                       end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'type_params', True, False)


def _coerce_to__expr_arglikes(
    code: Code, options: Mapping[str, Any] = {}, parse_params: Mapping[str, Any] = {}, *, strip: bool = False
) -> fst.FST:
    """See `_coerce_to__Assign_targets()`."""

    fst_ = _coerce_to_seq(code, dict(options, pars_arglike=False),  # _expr_arglikes can handle unparenthesized arglike-only expressions (its in the name)
                          parse_params, parse__expr_arglikes, Tuple, None, True)

    if fst_ is not None:  # sequence as sequence?
        if isinstance(fst_, list):  # this means code is an FST
            ast = Tuple(elts=fst_, ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                        end_col_offset=ls[-1].lenbytes)
            fst_ = fst.FST(ast, ls, None, from_=code, lcopy=False)

        return fst_.strip() if strip else fst_

    # single element as sequence

    fst_ = code_as_expr_arglike(code, options, parse_params, strip=strip, coerce=True)

    if fst_.is_parenthesized_tuple() is False:  # this shouldn't ever happen and can't even be forced since a Tuple is already the slice type for _expr_arglikes, but juuust in case
        fst_._delimit_node()  # pragma: no cover

    ast = Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast, ls, None, from_=fst_, lcopy=False)._set_field([fst_.a], 'elts', True, False)


# ......................................................................................................................

def _code_as(
    code: Code,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    ast_type: type[AST] | tuple[type[AST], ...],
    strip: bool,
    coerce_to: CodeAs | Literal[False] | None = None,
    *,
    name: str | None = None,
) -> fst.FST:
    """Generic handler for this."""

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        codea = code.a

        if not isinstance(codea, ast_type):
            if not coerce_to:
                raise _coerce_error(name or ast_type, codea, 'coerce disabled' if coerce_to is False else '')
            try:
                return coerce_to(code, options, parse_params, strip=strip)
            except (NodeError, SyntaxError, NotImplementedError) as exc:
                raise _coerce_error(name or ast_type, codea) from exc

    else:
        if isinstance(code, AST):
            if not isinstance(code, ast_type):
                if not coerce_to:
                    raise _coerce_error(name or ast_type, code, 'coerce disabled' if coerce_to is False else '')
                try:
                    return coerce_to(code, options, parse_params, strip=strip)
                except (NodeError, SyntaxError, NotImplementedError) as exc:
                    raise _coerce_error(name or ast_type, code) from exc

            src = unparse(code)
            lines = src.split('\n')

            ast = parse(src, parse_params)

            if ast.__class__ is not code.__class__:  # sanity check
                raise ParseError(f'could not reparse AST to {code.__class__.__name__}, got {ast.__class__.__name__}')  # pragma: no cover

        else:
            if isinstance(code, list):
                src = '\n'.join(lines := code)
            else:  # str
                lines = (src := code).split('\n')

            try:
                ast = parse(src, parse_params)

            except (NodeError, SyntaxError, NotImplementedError):
                if not (coerce_to and getattr(coerce_to, 'allow_coerce_src', False)):  # if there is a coerce function and it supports coerce source (by "supports" we also mean if it makes sense)
                    raise

                try:
                    fst_ = coerce_to(code, options, parse_params, strip=strip)
                except (NodeError, SyntaxError, NotImplementedError) as exc:
                    raise ParseError(f'expecting {name or ast_type.__name__}, could not parse or coerce') from exc

                return fst_

            if not isinstance(ast, ast_type):  # sanity check, parse func should guarantee what we want but maybe in future is used to get a specific subset of what parse func returns
                raise ParseError(f'expecting {name or ast_type.__name__}, got {code.__class__.__name__}')  # pragma: no cover

        code = fst.FST(ast, lines, None, parse_params=parse_params)

    return code.strip() if strip else code


def _code_as_expr(
    code: Code,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    allow_Slice: bool,
    allow_Tuple_of_Slice: bool,
    strip: bool,
    coerce: bool,
) -> fst.FST:
    """General convert `code` to `expr`. Meant to handle any type of expression including `Slice`, `Tuple` of `Slice`s,
    `Tuple` of `Slice` elements and arglikes."""

    expecting = _EXPR_PARSE_FUNC_TO_NAME[parse]

    if to_tuple := parse is parse_Tuple:  # special handling for code as Tuple, TODO: maybe it deserves its own handler?
        no_coerce_clss = (Tuple,)
    else:
        no_coerce_clss = ASTS_LEAF_EXPR

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        ast = code.a
        ast_cls = ast.__class__
        fix_coerced_tuple = False  # coerced tuples from the likes of _arglikes FST source may not be in standard source format

        if ast_cls not in no_coerce_clss:  # if not an expr then try coerce if allowed
            if not coerce:
                raise _coerce_error(expecting, ast_cls, 'coerce disabled')

            old_ast = ast
            ast, fix_coerced_tuple = _coerce_to_expr_ast(ast, True, options, parse_params, expecting, two_step=to_tuple)
            ast_cls = ast.__class__

            if ast_cls not in no_coerce_clss:  # we do this because if no_coerce_clss restricted to one type of expr instead of all then the same expr can come back and we need to make sure it is the one we want
                raise _coerce_error(expecting, old_ast)
            elif ast_cls is Starred and parse is parse_expr_slice:
                raise _coerce_error('expression (slice)', old_ast, 'coercion to Starred must be in a sequence')

            parse = None  # this is a signal so that singleton tuples always get trailing comma, maybe review this behavior

            code = fst.FST(ast, code._lines, None, from_=code, lcopy=False)

        if ast_cls is Slice:
            if not allow_Slice:
                raise _coerce_error(expecting, 'Slice')

        elif ast_cls is Tuple:
            if not allow_Tuple_of_Slice and any(e.__class__ is Slice for e in ast.elts):
                raise _coerce_error(expecting, 'Tuple', 'has Slice')

            if fix_coerced_tuple:
                code._fix_Tuple(False)  # it is not parenthesized
            elif parse is not parse_expr_slice:  # SPECIAL CASE specifically for lone '*starred' as a `Tuple` without comma from `Subscript.slice`, doesn't happen organically but can be created with FST('*a', 'expr_slice'), should we bother? for now on the side of yes
                code._maybe_add_singleton_comma()

        elif ast_cls is Starred:  # may need to parenthesize arglike Starred
            if parse not in (parse_expr_arglike, parse_expr_all, parse_Tuple_elt):  # only if not asking something which CAN be arglike
                pars_arglike = fst.FST._get_opt_eff_pars_arglike(options)

                if pars_arglike and code._is_expr_arglike_only():
                    code._parenthesize_grouping()

    else:
        old_code = code

        if is_ast := isinstance(code, AST):
            if code.__class__ not in no_coerce_clss:  # if not an expr then try coerce if allowed
                if not coerce:
                    raise _coerce_error(expecting, code, 'coerce disabled')

                code, _ = _coerce_to_expr_ast(code, False, options, parse_params, expecting, two_step=to_tuple)

                if code.__class__ not in no_coerce_clss:
                    raise _coerce_error(expecting, old_code)

            src = unparse(code)
            lines = src.split('\n')

        elif isinstance(code, list):
            src = '\n'.join(lines := code)
        else:  # str
            lines = (src := code).split('\n')

        ast = parse(src, parse_params)

        if is_ast:
            ast_cls = ast.__class__
            code_cls = code.__class__

            if ast_cls is not code_cls:  # sanity check, could have tried with a FormattedValue
                if parse is parse_expr_slice and ast_cls is Tuple and code_cls is Starred:  # SPECIAL CASE specifically for lone '*starred' being parsed as a `Tuple`
                    if code is old_code:
                        raise _coerce_error('expression (slice)', 'Starred', 'must be in a sequence')  # pragma: no cover  # this currently gets rejected in code_as_expr_slice() so will not get here
                    else:
                        raise _coerce_error('expression (slice)', old_code, 'coercion to Starred must be in a sequence')

                else:
                    raise ParseError(f'could not reparse AST to {old_code.__class__.__name__}'
                                     f', got {ast_cls.__name__}')

        code = fst.FST(ast, lines, None, parse_params=parse_params)

    return code.strip() if strip else code


def _code_as_op(
    code: Code,
    options: Mapping[str, Any],
    parse_params: Mapping[str, Any],
    parse: Callable[[Code, Mapping[str, Any]], AST],
    op_type: type[boolop | operator | unaryop | cmpop],  # only one of these, not subclasses
    strip: bool,
) -> fst.FST:
    """Convert `code` to an op `FST` if possible."""

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        if not isinstance(code.a, op_type):
            raise _coerce_error(op_type, code.a)

    elif isinstance(code, AST):
        if not isinstance(code, op_type):
            raise _coerce_error(op_type, code)

        code_cls = code.__class__

        return fst.FST(code_cls(), [OPCLS2STR[code_cls]], None, parse_params=parse_params)  # don't use same AST as was passed in

    else:
        if isinstance(code, list):
            src = '\n'.join(lines := code)
        else:  # str
            lines = (src := code).split('\n')

        code = fst.FST(parse(src, parse_params), lines, None, parse_params=parse_params)

    return code.strip() if strip else code


def _code_as_lines(code: Code | None) -> list[str]:  # This is meant for export but it doesn't deserve a non-underscore start, so its here
    """Get list of lines of `code` if is `FST`, unparse `AST`, split `str` or just return `list[str]` if is that.
    `code=None` is returned as `['']`."""

    if isinstance(code, str):
        return code.split('\n')
    elif code is None:
        return ['']
    elif isinstance(code, list):
        return code
    elif isinstance(code, AST):
        return unparse(code).split('\n')
    elif code.parent:  # not code.is_root:  # isinstance(code, fst.FST
        raise ValueError('expecting root node')
    else:
        return code._lines


# ----------------------------------------------------------------------------------------------------------------------

def code_as(
    code: Code,
    mode: Mode | None = None,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to any specified parsable `FST` if possible. If `FST` passed matches then it is returned as
    itself, otherwise may be coerced if that is allowed.

    **Parameters:**
    - `mode`: If this is `None` then it is set to `'all'` and this function is free to do some normalization.
    """

    if mode is None:
        if not isinstance(code, AST):
            mode = 'all'
        elif (mode := code.__class__) is Constant:  # Constants with negative values get normalized in parse to UnaryOp (set to expect that), -0.0 primitive values at the top level need to be normalized here otherwise these may be reparsed to BinOp
            code, mode = _normalize_Constant_for_unparse(code)

    if code_as := _CODE_AS_MODE_FUNCS.get(mode):
        fst_ = code_as(code, options, parse_params, strip=strip, coerce=coerce)

        mode_type = _AST_TYPE_BY_NAME_OR_TYPE.get(mode)  # `expr` or expr -> expr, etc...

        if mode_type and not isinstance(fst_.a, mode_type):
            raise _coerce_error(mode_type, fst_.a, '' if coerce else 'coerce disabled')  # pragma: no cover  # can't think of a case where this would happen

        return fst_

    if not isinstance(mode, type) or not issubclass(mode, AST):
        raise ValueError(f'invalid mode {mode!r}')

    raise NodeError(f'cannot get code as {mode.__name__}')


def code_as_all(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to any parsable `FST` if possible. If `FST` passed then it is returned as itself."""

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

    else:
        if isinstance(code, AST):
            mode = code.__class__
            code = unparse(code)
            lines = code.split('\n')

        else:
            mode = 'all'

            if isinstance(code, list):
                code = '\n'.join(lines := code)
            else:  # str
                lines = code.split('\n')

        code = fst.FST(parse(code, mode), lines, None, parse_params=parse_params)

    return code.strip() if strip else code


def code_as_stmt(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a single more `stmt` `FST` if possible."""

    return _code_as(code, options, parse_params, parse_stmt, stmt, strip, _coerce_to_stmt if coerce else False)


def code_as_stmts(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to zero or more `stmt`s and return in the `body` of a `Module` `FST` if possible.

    **Note:** `strip` does nothing since the return is a `Module` which always includes the whole source.
    """

    return _code_as(code, options, parse_params, parse_stmts, Module, strip, _coerce_to_stmts if coerce else False,
                    name='zero or more stmts')


def code_as_ExceptHandler(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
    star: bool | None = None,
) -> fst.FST:
    """Convert `code` a single `ExceptHandler`s if possible.

    **Note:** `coerce` does nothing since nothing can coerce to a single `ExceptHandler`.

    **Parameters:**
    - `star`: What kind of except handler to accept:
        - `False`: Plain only, no `except*`.
        - `True`: Star only, no plain.
        - `None`: Accept either as `FST` or source, if `AST` passed then default to plain.
    """

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        if code.a.__class__ is not ExceptHandler:
            raise _coerce_error('ExceptHandler', code.a)

        error = NodeError

    else:
        if isinstance(code, AST):
            code_cls = code.__class__

            if code_cls is not ExceptHandler:
                raise _coerce_error('ExceptHandler', code_cls)

            code = _fixing_unparse((TryStar if star else Try)(body=[Pass()],
                                                              handlers=[code], orelse=[], finalbody=[]))
            code = code[code.index('except'):]
            lines = code.split('\n')
            star = None  # so that unnecessary check is not done below

        elif isinstance(code, list):
            code = '\n'.join(lines := code)
        else:  # str
            lines = code.split('\n')

        code = fst.FST(parse_ExceptHandler(code, parse_params), lines, None, parse_params=parse_params)

        error = ParseError

    if star is not None:
        if star != code.is_except_star():
            raise error("expecting star 'except*' handler, got plain 'except'"
                        if star else
                        "expecting plain 'except' handler, got star 'except*'")

    return code


def code_as__ExceptHandlers(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
    star: bool | None = None,
) -> fst.FST:
    """Convert `code` to zero or more `ExceptHandler`s and return in an `_ExceptHandlers` SPECIAL SLICE if possible.

    **Note:** `strip` does nothing since the return is an `_ExceptHandlers` which always includes the whole source.

    **Parameters:**
    - `star`: What kind of except handlers to accept:
        - `False`: Plain only, no `except*`.
        - `True`: Star only, no plain.
        - `None`: Accept either as `FST` or source, if `AST` passed then default to plain.
    """

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        codea = code.a
        codea_cls = codea.__class__

        if codea_cls is ExceptHandler:
            if not coerce:
                raise _coerce_error('_ExceptHandlers', 'ExceptHandler', 'coerce disabled')

            code = fst.FST(_ExceptHandlers(handlers=[codea], lineno=1, col_offset=0, end_lineno=len(ls := code._lines),
                                           end_col_offset=ls[-1].lenbytes), ls, None, from_=code, lcopy=False)

        elif codea_cls is not _ExceptHandlers:
            raise _coerce_error('_ExceptHandlers', codea_cls)

        error = NodeError

    else:
        if isinstance(code, AST):
            code_cls = code.__class__

            if code_cls is ExceptHandler:
                if not coerce:
                    raise _coerce_error('_ExceptHandlers', 'ExceptHandler', 'coerce disabled')

                handlers = [code]

            elif code_cls is _ExceptHandlers:
                if not (handlers := code.handlers):
                    return fst.FST(_ExceptHandlers(handlers=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=0),
                                   [''], None, parse_params=parse_params)

            else:
                raise _coerce_error('_ExceptHandlers', code_cls)

            code = _fixing_unparse((TryStar if star else Try)(body=[Pass()],
                                                              handlers=handlers, orelse=[], finalbody=[]))
            code = code[code.index('except'):]
            lines = code.split('\n')
            star = None  # so that unnecessary check is not done below

        elif isinstance(code, list):
            code = '\n'.join(lines := code)
        else:  # str
            lines = code.split('\n')

        code = fst.FST(parse__ExceptHandlers(code, parse_params), lines, None, parse_params=parse_params)

        error = ParseError

    if (handlers := code.a.handlers) and star is not None:
        if star != handlers[0].f.is_except_star():
            raise error("expecting star 'except*' handler(s), got plain 'except'"
                        if star else
                        "expecting plain 'except' handler(s), got star 'except*'")

    return code


def code_as_match_case(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a single `match_case` if possible.

    **Note:** `coerce` does nothing since nothing can coerce to a single `match_case`.
    """

    return _code_as(code, options, parse_params, parse_match_case, match_case, strip,
                    _coerce_to_match_case if coerce else False)


def code_as__match_cases(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to zero or more `match_case`s and return in a `_match_cases` SPECIAL SLICE if possible.

    **Note:** `strip` does nothing since the return is a `_match_cases` which always includes the whole source.
    """

    return _code_as(code, options, parse_params, parse__match_cases, _match_cases, strip,
                    _coerce_to__match_cases if coerce else False)


def code_as_expr(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `expr` using `parse_expr()`."""

    return _code_as_expr(code, options, parse_params, parse_expr, False, False, strip, coerce)


def code_as_expr_all(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `expr` using `parse_expr_all()`."""

    return _code_as_expr(code, options, parse_params, parse_expr_all, True, True, strip, coerce)


def code_as_expr_arglike(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `expr` in the context of a `Call.args` which has special parse rules for `Starred`."""

    return _code_as_expr(code, options, parse_params, parse_expr_arglike, False, False, strip, coerce)


def code_as_expr_slice(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a any `expr` `FST` that can go into a `Subscript.slice` if possible."""

    codea = code.a if isinstance(code, fst.FST) else code

    if codea.__class__ is Starred:  # Starred cannot be a direct slice
        raise _coerce_error('expression (slice)', 'Starred', 'must be in sequence')

    return _code_as_expr(code, options, parse_params, parse_expr_slice, True, True, strip, coerce)


def code_as_Tuple_elt(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `expr` which can be an element of a `Tuple` anywhere, including `Slice` and arglike
    expressions like `*not a` on py 3.11+ (both in a `Tuple` in `Subscript.slice`)."""

    return _code_as_expr(code, options, parse_params, parse_Tuple_elt, True, False, strip, coerce)


def code_as_Tuple(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `Tuple` using `parse_Tuple()`. The `Tuple` can contain any other kind of expression,
    including `Slice` and arglike (if py version supports it in `Subscript.slice`)."""

    fst_ = _code_as_expr(code, options, parse_params, parse_Tuple, False, True, strip, coerce)

    # if fst_ is code and fst_.a.__class__ is not Tuple:  # CURRENTLY HANDLED in _code_as_expr()  # fst_ is code only if FST passed in, in which case is passed through and we need to check that was Tuple to begin with
    #     raise NodeError(f'expecting Tuple, got {fst_.a.__class__.__name__}')

    return fst_


def code_as_Set(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `Set` using `parse_Set()`"""

    return _code_as(code, options, parse_params, parse_Set, Set, strip, _coerce_to_Set if coerce else False)


def code_as_List(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `List` using `parse_List()`"""

    return _code_as(code, options, parse_params, parse_List, List, strip, _coerce_to_List if coerce else False)


def code_as__Assign_targets(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `_Assign_targets` SPECIAL SLICE if possible."""

    return _code_as(code, options, parse_params, parse__Assign_targets, _Assign_targets, strip,
                    _coerce_to__Assign_targets if coerce else False)


def code_as__decorator_list(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `_decorator_list` SPECIAL SLICE if possible."""

    return _code_as(code, options, parse_params, parse__decorator_list, _decorator_list, strip,
                    _coerce_to__decorator_list if coerce else False)


def code_as__arglike(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a single `expr_arglike` or `keyword` if possible."""

    fst_ = _code_as(code, options, parse_params, parse__arglike, (expr, keyword), strip,
                    _coerce_to__arglike if coerce else False,
                    name='expression (arglike)')

    if isinstance(code, fst.FST):  # if anything else then these conditions will have been rejected by parse__arglike
        ast_ = fst_.a
        ast_cls = ast_.__class__

        if ast_cls in ASTS_LEAF_FTSTR_FMT_OR_SLICE:  # need to check coercions as well as origina fst_
            raise _coerce_error('expression (arglike)', fst_.a)
        elif ast_cls is Tuple and any(e.__class__ is Slice for e in ast_.elts):
            raise _coerce_error('expression (arglike)', 'Tuple', 'has Slice')

    return fst_


def code_as__arglikes(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `_arglikes` of `expr`s and `keyword`s SPECIAL SLICE if possible."""

    return _code_as(code, options, parse_params, parse__arglikes, _arglikes, strip,
                    _coerce_to__arglikes if coerce else False)


def code_as_boolop(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `boolop` `FST` if possible."""

    return _code_as_op(code, options, parse_params, parse_boolop, boolop, strip)


def code_as_operator(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `operator` `FST` if possible."""

    return _code_as_op(code, options, parse_params, parse_operator, operator, strip)


def code_as_unaryop(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `unaryop` `FST` if possible."""

    return _code_as_op(code, options, parse_params, parse_unaryop, unaryop, strip)


def code_as_cmpop(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `cmpop` `FST` if possible."""

    return _code_as_op(code, options, parse_params, parse_cmpop, cmpop, strip)


def code_as_comprehension(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a comprehension `FST` if possible."""

    return _code_as(code, options, parse_params, parse_comprehension, comprehension, strip)


def code_as__comprehensions(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `_comprehensions` of `comprehensions` SPECIAL SLICE if possible."""

    return _code_as(code, options, parse_params, parse__comprehensions, _comprehensions, strip,
                    _coerce_to__comprehensions if coerce else False)


def code_as__comprehension_ifs(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `_comprehension_ifs` of `if` prepended `expr`s SPECIAL SLICE if possible."""

    return _code_as(code, options, parse_params, parse__comprehension_ifs, _comprehension_ifs, strip,
                    _coerce_to__comprehension_ifs if coerce else False)


def code_as_arguments(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a arguments `FST` if possible."""

    return _code_as(code, options, parse_params, parse_arguments, arguments, strip,
                    _coerce_to_arguments if coerce else False)


def code_as_arguments_lambda(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a lambda arguments `FST` if possible (no annotations allowed)."""

    fst_ = _code_as(code, options, parse_params, parse_arguments_lambda, arguments, strip,
                    _coerce_to_arguments_lambda if coerce else False,
                    name='lambda arguments')

    if fst_ is code:  # validation if returning same FST that was passed in
        ast = fst_.a

        if (((args := ast.args) and any(a.annotation for a in args))
            or ((args := ast.kwonlyargs) and any(a.annotation for a in args))
            or ((arg := ast.vararg) and arg.annotation)
            or ((arg := ast.kwarg) and arg.annotation)
            or ((args := ast.posonlyargs) and any(a.annotation for a in args))
        ):
            raise NodeError('lambda arguments cannot have annotations')

    return fst_


def code_as_arg(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an arg `FST` if possible."""

    return _code_as(code, options, parse_params, parse_arg, arg, strip, _coerce_to_arg if coerce else False)


def code_as_keyword(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a keyword `FST` if possible."""

    return _code_as(code, options, parse_params, parse_keyword, keyword, strip, _coerce_to_keyword if coerce else False)


def code_as_alias(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, star or dotted."""

    return _code_as(code, options, parse_params, parse_alias, alias, strip, _coerce_to_alias if coerce else False)


def code_as__aliases(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, star or dotted."""

    return _code_as(code, options, parse_params, parse__aliases, _aliases, strip,
                    _coerce_to__aliases if coerce else False)


def code_as_Import_name(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, dotted as in `alias` for `Import.names`."""

    fst_ = _code_as(code, options, parse_params, parse_Import_name, alias, strip,
                    _coerce_to__Import_name if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if fst_.a.name == '*':
            raise NodeError("'*' star alias not allowed")

    return fst_


def code_as__Import_names(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, dotted as in `alias` for `Import.names`."""

    fst_ = _code_as(code, options, parse_params, parse__Import_names, _aliases, strip,
                    _coerce_to__Import_names if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if any(a.name == '*' for a in fst_.a.names):
            raise NodeError("'*' star alias not allowed")

    return fst_


def code_as_ImportFrom_name(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `alias` `FST` if possible, possibly star as in `alias` for `FromImport.names`."""

    fst_ = _code_as(code, options, parse_params, parse_ImportFrom_name, alias, strip,
                    _coerce_to__ImportFrom_name if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if '.' in fst_.a.name:
            raise NodeError("'.' dotted alias not allowed")

    return fst_


def code_as__ImportFrom_names(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to an `_aliases` of `alias` SPECIAL SLICE if possible, possibly star as in `alias` for
    `FromImport.names`."""

    fst_ = _code_as(code, options, parse_params, parse__ImportFrom_names, _aliases, strip,
                    _coerce_to__ImportFrom_names if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        for a in (names := fst_.a.names):
            if '.' in (n := a.name):
                raise NodeError("'.' dotted alias not allowed")

            if n == '*' and a is not names[0]:
                raise NodeError("'*' star can only be a single element")

        if len(names) > 1 and names[0].name == '*':  # someone really wanted to get a star in there...
            raise NodeError("'*' star can only be a single element")

    return fst_


def code_as_withitem(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a withitem `FST` if possible."""

    return _code_as(code, options, parse_params, parse_withitem, withitem, strip,
                    _coerce_to_withitem if coerce else False)


def code_as__withitems(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `_withitems` of `withitem` SPECIAL SLICE if possible."""

    return _code_as(code, options, parse_params, parse__withitems, _withitems, strip,
                    _coerce_to__withitems if coerce else False)


def code_as_pattern(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
    allow_invalid_matchor: bool = False,
) -> fst.FST:
    """Convert `code` to a pattern `FST` if possible."""

    fst_ = _code_as(code, options, parse_params, parse_pattern, pattern, strip,
                    _coerce_to_pattern if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if not allow_invalid_matchor and (a := fst_.a).__class__ is MatchOr:  # SPECIAL SLICE
            if not (len_pattern := len(a.patterns)):
                raise _coerce_error('pattern', 'zero-length MatchOr')

            if len_pattern == 1:  # a length 1 MatchOr can just return its single element pattern
                fst_._unmake_fst_parents(True)

                return fst.FST(a.patterns[0], fst_._lines, None, from_=fst_, lcopy=False)

    return fst_


def code_as__pattern_attrlikes(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a pattern `FST` if possible."""

    fst_ = _code_as(code, options, parse_params, parse__pattern_attrlikes, _pattern_attrlikes, strip,
                    _coerce_to__pattern_attrlikes if coerce else False)

    return fst_


def code_as_type_param(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a type_param `FST` if possible."""

    return _code_as(code, options, parse_params, parse_type_param, type_param, strip,
                    _coerce_to_type_param if coerce else False)


def code_as__type_params(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `_type_params` of `type_param` SPECIAL SLICE if possible."""

    return _code_as(code, options, parse_params, parse__type_params, _type_params, strip,
                    _coerce_to__type_params if coerce else False)


def code_as_Load(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
    as_cls: type[AST] = Load,
) -> fst.FST:
    """Convert `code` to an `expr_context`. Accepts any source and creates the `FST` for one of these. "coercion" is
    allowed between the three. This exists as a convenience."""

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        codea = code.a
        codea_cls = codea.__class__

        if codea_cls is not as_cls:
            if not coerce:
                raise _coerce_error(as_cls, codea_cls, 'coerce disabled')
            if codea_cls not in ASTS_LEAF_EXPR_CONTEXT:
                raise _coerce_error(as_cls, codea_cls)

            code = fst.FST(as_cls(), code._lines, None, from_=code, lcopy=False)

        return code.strip() if strip else code

    if isinstance(code, AST):
        code_cls = code.__class__

        if code_cls is not as_cls:
            if not coerce:
                raise _coerce_error(as_cls, code_cls, 'coerce disabled')
            if code_cls not in ASTS_LEAF_EXPR_CONTEXT:
                raise _coerce_error(as_cls, code_cls)

        code = ['']

    elif isinstance(code, str):
        code = code.split('\n')

    return fst.FST(as_cls(), code, None, parse_params=parse_params)


def code_as_Store(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """See `code_as_Load()`."""

    return code_as_Load(code, options, parse_params, strip=strip, coerce=coerce, as_cls=Store)


def code_as_Del(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """See `code_as_Load()`."""

    return code_as_Load(code, options, parse_params, strip=strip, coerce=coerce, as_cls=Del)


def code_as_identifier(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> str:
    """Convert `code` to valid identifier string if possible.

    **Note:** `strip` does nothing.
    """

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier(code):
        raise ParseError(f'expecting identifier, got {shortstr(code)!r}')

    return code


def code_as_identifier_dotted(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> str:
    """Convert `code` to valid dotted identifier string if possible (for Import module, star not allowed).

    **Note:** `strip` does nothing.
    """

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_dotted(code):
        raise ParseError(f'expecting dotted identifier, got {shortstr(code)!r}')

    return code


def code_as_identifier_star(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> str:
    """Convert `code` to valid identifier string or star '*' if possible (for ImportFrom names, dotted not allowed).

    **Note:** `strip` does nothing.
    """

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_star(code):
        raise ParseError(f"expecting identifier or '*', got {shortstr(code)!r}")

    return code


def code_as_identifier_alias(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> str:
    """Convert `code` to valid dotted identifier string or star '*' if possible (for any alias).

    **Note:** `strip` does nothing.
    """

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        code = code._get_src(*loc) if (loc := code.loc) else code.src  # just in case strip junk

    elif isinstance(code, AST):
        code = _fixing_unparse(code)
    elif isinstance(code, list):
        code = '\n'.join(code)

    code = normalize('NFKC', code)

    if not is_valid_identifier_alias(code):
        raise ParseError(f"expecting dotted identifier or '*', got {shortstr(code)!r}")

    return code


def code_as_constant(
    code: Code | constant,  # yes this breaks convention, its for documentation purposes and there is no static analyzer to complain
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> constant:
    """Convert `code` to valid constant if possible. If `code` is a `str` then it is treated as the constant value and
    not as the Python representation of the constant. The only `FST` or `AST` accepted is a `Constant` or chain of
    negating `UnaryOp` which leads to a `Constant`, whose `value` is returned (possibly negated due to any `UnaryOp`).

    We normalize any -0.0 or -0.0j to positive. We do not accept imaginary constants with real parts.

    **Note:** `strip` does nothing.
    """

    if isinstance(code, fst.FST):
        if code.parent:  # not code.is_root
            raise ValueError('expecting root node')

        code = code.a

    if isinstance(code, AST):
        neg = False

        while code.__class__ is UnaryOp:
            if (unary_op_cls := code.op.__class__) is USub:
                neg = not neg

            elif unary_op_cls is not UAdd:
                raise NodeError("unary operators on Constant can only be '-' or '+',"
                                f" got {unary_op_cls.__class__.__name__}")

            code = code.operand

        if code.__class__ is not Constant:
            raise _coerce_error('Constant', code)

        code = -code.value if neg else code.value

        if isinstance(code, float):
            if not code:  # normalize -0.0
                code = 0.0

        elif isinstance(code, complex):
            if code.real:
                raise NodeError('imaginary Constants cannot have real componenets')

            code = complex(0.0, code.imag or 0.0)  # normalize -0.0 in real or imag

    elif isinstance(code, list):
        code = '\n'.join(code)
    elif not isinstance(code, constant):
        raise _coerce_error('Constant', code.__class__.__qualname__)

    return code


# ......................................................................................................................
# internal stuff, not meant for direct user use

def code_as__expr_arglikes(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
    one: bool = False,  # HACK, if we use more often then standardize
) -> fst.FST:
    """Convert `code` to a `Tuple` contianing possibly arglike expressions. Meant for putting slices to `Call.args` and
    `ClassDef.bases`. The `Tuple` will be unparenthesized and the location will be the entire source. We use a `Tuple`
    for this because unfortunately sometimes a `Tuple` is valid with arglikes in it and sometimes not.

    **WARNING!** The `Tuple` that is returned is just being used as a container and may be an invalid python `Tuple` as
    it may be an empty `Tuple` `AST` with source having no parentheses or an unparenthesized `Tuple` with incorrect
    start and stop locations (since its the whole source). Singleton `Tuple` may also not have trailing comma. Meant for
    internal use only! May fail `verify()`.
    """

    codea = code.a if isinstance(code, fst.FST) else code

    if not one and code.__class__ is Tuple:  # strip parentheses
        code = _fixing_unparse(code)[1:-1]

    fst_ = _code_as(code, options, parse_params, parse__expr_arglikes, Tuple, strip,
                    _coerce_to__expr_arglikes if coerce else False)

    if fst_ is code:  # validation if returning same FST that was passed in
        if any(e.__class__ is Slice for e in fst_.a.elts):
            raise _coerce_error('expression(s) (arglike)', codea, 'has Slice')

        if fst_._is_delimited_seq():
            fst_._trim_delimiters()

    return fst_


def code_as__Dict_maybe_undelimited(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `Dict`, possibly undelimited. If undelimited and empty then the location is the whole source.
    """

    return _code_as(code, options, parse_params, parse__Dict_maybe_undelimited, Dict, strip,
                    _coerce_to_Dict if coerce else False)


def code_as__MatchMapping_maybe_undelimited(
    code: Code,
    options: Mapping[str, Any] = {},
    parse_params: Mapping[str, Any] = {},
    *,
    strip: bool = False,
    coerce: bool = False,
) -> fst.FST:
    """Convert `code` to a `MatchMapping`, possibly undelimited. If undelimited and empty then the location is the whole
    source."""

    return _code_as(code, options, parse_params, parse__MatchMapping_maybe_undelimited, MatchMapping, strip,
                    _coerce_to_MatchMapping if coerce else False)


# ......................................................................................................................

_CODE_AS_MODE_FUNCS = {
    'all':                    code_as_all,
    'strict':                 code_as_stmts,
    'exec':                   code_as_stmts,
    'eval':                   None,  # why do we even support these at all?
    'single':                 None,
    'stmt':                   code_as_stmt,
    'stmts':                  code_as_stmts,
    'ExceptHandler':          code_as_ExceptHandler,
    '_ExceptHandlers':        code_as__ExceptHandlers,
    'match_case':             code_as_match_case,
    '_match_cases':           code_as__match_cases,
    'expr':                   code_as_expr,
    'expr_all':               code_as_expr_all,
    'expr_arglike':           code_as_expr_arglike,
    'expr_slice':             code_as_expr_slice,
    'Tuple_elt':              code_as_Tuple_elt,
    'Tuple':                  code_as_Tuple,
    '_Assign_targets':        code_as__Assign_targets,
    '_decorator_list':        code_as__decorator_list,
    '_arglike':               code_as__arglike,
    '_arglikes':              code_as__arglikes,
    'boolop':                 code_as_boolop,
    'operator':               code_as_operator,
    'unaryop':                code_as_unaryop,
    'cmpop':                  code_as_cmpop,
    'comprehension':          code_as_comprehension,
    '_comprehensions':        code_as__comprehensions,
    '_comprehension_ifs':     code_as__comprehension_ifs,
    'arguments':              code_as_arguments,
    'arguments_lambda':       code_as_arguments_lambda,
    'arg':                    code_as_arg,
    'keyword':                code_as_keyword,
    'alias':                  code_as_alias,
    '_aliases':               code_as__aliases,
    'Import_name':            code_as_Import_name,
    '_Import_names':          code_as__Import_names,
    'ImportFrom_name':        code_as_ImportFrom_name,
    '_ImportFrom_names':      code_as__ImportFrom_names,
    'withitem':               code_as_withitem,
    '_withitems':             code_as__withitems,
    'pattern':                code_as_pattern,
    '_pattern_attrlikes':     code_as__pattern_attrlikes,
    'type_param':             code_as_type_param,
    '_type_params':           code_as__type_params,
    mod:                      code_as_stmts,
    Expression:               None,
    Interactive:              None,
    stmt:                     code_as_stmt,
    ExceptHandler:            code_as_ExceptHandler,
    match_case:               code_as_match_case,
    expr:                     code_as_expr,
    Starred:                  code_as_expr_arglike,
    Slice:                    code_as_expr_slice,
    Tuple:                    code_as_Tuple,
    Set:                      code_as_Set,
    List:                     code_as_List,
    boolop:                   code_as_boolop,
    operator:                 code_as_operator,
    unaryop:                  code_as_unaryop,
    cmpop:                    code_as_cmpop,
    comprehension:            code_as_comprehension,
    arguments:                code_as_arguments,
    arg:                      code_as_arg,
    keyword:                  code_as_keyword,
    alias:                    code_as_alias,
    withitem:                 code_as_withitem,
    pattern:                  code_as_pattern,
    type_param:               code_as_type_param,
    Load:                     code_as_Load,
    Store:                    code_as_Store,
    Del:                      code_as_Del,
    FunctionType:             None,  # explicitly prohibit from parse
    FormattedValue:           None,
    Interpolation:            None,
    TypeIgnore:               None,
    _ExceptHandlers:          code_as__ExceptHandlers,
    _match_cases:             code_as__match_cases,
    _Assign_targets:          code_as__Assign_targets,
    _decorator_list:          code_as__decorator_list,
    _arglikes:                code_as__arglikes,
    _comprehensions:          code_as__comprehensions,
    _comprehension_ifs:       code_as__comprehension_ifs,
    _aliases:                 code_as__aliases,
    _withitems:               code_as__withitems,
    _pattern_attrlikes:       code_as__pattern_attrlikes,
    _type_params:             code_as__type_params,
    '_expr_arglikes':         code_as__expr_arglikes,
}  # fmt: skip  # automatically filled out with all AST types and their names derived from these


for ast_cls in FIELDS:  # fill out _CODE_AS_MODE_FUNCS with all supported AST types and their class names as parse modes
    ast_name = ast_cls.__name__

    if (parse_func := _CODE_AS_MODE_FUNCS.get(ast_cls, ...)) is not ...:
        if ast_name not in _CODE_AS_MODE_FUNCS:  # for top level types already in table name is probably in table as well (and may be different in future?)
            _CODE_AS_MODE_FUNCS[ast_name] = parse_func

    else:
        base = ast_cls

        while (base := base.__bases__[0]) is not AST:
            if parse_func := _CODE_AS_MODE_FUNCS.get(base):
                _CODE_AS_MODE_FUNCS[ast_cls] = _CODE_AS_MODE_FUNCS[ast_name] = parse_func  # base ASTs not in table will not have name in table either

                break
