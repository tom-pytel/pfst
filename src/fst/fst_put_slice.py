"""Put slice. Some slices can use normal `AST` types and others need special custom `fst` `AST` container classes.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from __future__ import annotations

from typing import Any, Callable, Literal, Mapping, NamedTuple

from . import fst

from .asttypes import (
    AST,
    And,
    Assign,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    BoolOp,
    Call,
    ClassDef,
    Compare,
    Del,
    Delete,
    Dict,
    DictComp,
    ExceptHandler,
    Expr,
    For,
    FunctionDef,
    GeneratorExp,
    Global,
    If,
    IfExp,
    Import,
    ImportFrom,
    Interactive,
    IsNot,
    JoinedStr,
    List,
    ListComp,
    Load,
    NotIn,
    Match,
    MatchAs,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    Module,
    Name,
    NamedExpr,
    Nonlocal,
    Not,
    Pass,
    Set,
    SetComp,
    Slice,
    Starred,
    Try,
    Tuple,
    UnaryOp,
    While,
    With,
    Yield,
    YieldFrom,
    comprehension,
    match_case,
    TryStar,
    TypeAlias,
    TemplateStr,
    cmpop,
    expr_context,
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from .astutil import re_identifier, OPCLS2STR, bistr, is_valid_target, is_valid_del_target, reduce_ast, set_ctx

from .common import (
    PYLT11,
    PYGE14,
    re_line_end_cont_or_comment,
    NodeError,
    astfield,
    fstloc,
    next_frag,
    prev_frag,
    next_find,
    prev_find,
    next_find_re,
)

from .parsex import (
    ParseError,
    unparse,
    parse_cmpop,
    parse__BoolOp_dangling_left,
    parse__BoolOp_dangling_right,
    parse__Compare_dangling_left,
    parse__Compare_dangling_right,
)

from .code import (
    Code,
    code_as_expr,
    code_as_expr_all,
    code_as__Assign_targets,
    code_as__decorator_list,
    code_as__comprehensions,
    code_as__comprehension_ifs,
    code_as__aliases,
    code_as__Import_names,
    code_as__ImportFrom_names,
    code_as__withitems,
    code_as_pattern,
    code_as__type_params,
    code_as__expr_arglikes,
    _coerce_as__expr_arglikes,
)

from .fst_misc import get_option_overridable, fixup_slice_indices
from .slice_stmtish import put_slice_stmtish
from .slice_exprish import put_slice_sep_begin, put_slice_sep_end, put_slice_nosep

from .fst_get_slice import (
    _get_option_norm,
    _get_option_op_side,
    _bounds_Delete_targets,
    _bounds_Assign_targets,
    _bounds_decorator_list,
    _bounds_generators,
    _bounds_comprehension_ifs,
    _move_Compare_left_into_comparators,
    _add_MatchMapping_rest_as_real_node,
    _remove_MatchMapping_rest_real_node,
    _maybe_fix_BoolOp,
    _maybe_fix_Compare,
    _maybe_fix_Assign_target0,
    _maybe_fix_decorator_list_trailing_newline,
    _maybe_fix_decorator_list_del,
    _maybe_fix_Set,
    _maybe_fix_MatchSequence,
    _maybe_fix_MatchOr,
    _maybe_fix_stmt_end,
)


# * Keep src same.
# * Use normal AST and src where possible.
# * Delimiters where would match ast.unparse().
# * Special unparse where needed.


#   (!) SPECIAL SLICE, (?) sometimes SPECIAL SLICE???
#   | (N)ormal container, (S)equence container
#   | | Separator (trailing)
#   | | |  Prefix (leaading)
#   | | |  |  Delimiters
#   | | |  |  |
#                                                                                  .
# *   N ,     ()   (Tuple, 'elts')                         # expr*                 -> Tuple                      _parse_Tuple_elts
# *   N ,     []   (List, 'elts')                          # expr*                 -> List                       _parse_expr / restrict seq
# * ? N ,     {}   (Set, 'elts')                           # expr*                 -> Set                        _parse_expr / restrict seq
#                                                                                  .
# *   N ,     {}   (Dict, 'keys:values')                   # expr:expr*            -> Dict                       _parse_expr / restrict dict
#                                                                                  .
# *   N ,     []   (MatchSequence, 'patterns'):            # pattern*              -> MatchSequence              _parse_pattern / restrict MatchSequence
# *   N ,     {}   (MatchMapping, 'keys:patterns,rest'):   # expr:pattern*,expr?   -> MatchMapping               _parse_pattern / restrict MatchMapping
#                                                                                  .
# * ? N |          (MatchOr, 'patterns'):                  # pattern*              -> MatchOr                    _parse_pattern / restrict MatchOr
#                                                                                  .
#     S ,          (MatchClass, 'patterns'):               # pattern*              -> MatchSequence              _parse_pattern / restrict MatchSequence  - allow empty pattern?
#                                                                                  .
#                                                                                  .
# *   S ,          (ClassDef, 'bases'):                    # expr*                 -> Tuple[expr_arglike]        _parse__expr_arglikes  - keywords and Starred bases can mix
# *   S ,          (Call, 'args'):                         # expr*                 -> Tuple[expr_arglike]        _parse__expr_arglikes  - keywords and Starred args can mix
#                                                                                  .
# *   S ,          (Delete, 'targets'):                    # expr*                 -> Tuple[target]              _parse_expr / restrict del_targets
# * ! N =          (Assign, 'targets'):                    # expr*                 -> _Assign_targets            _parse__Assign_targets
#                                                                                  .
#                                                                                  .
# *   S ,          (Global, 'names'):                      # identifier*,          -> Tuple[Name]                _parse_expr / restrict Names   - no trailing commas, unparenthesized
# *   S ,          (Nonlocal, 'names'):                    # identifier*,          -> Tuple[Name]                _parse_expr / restrict Names   - no trailing commas, unparenthesized
#                                                                                  .
#                                                                                  .
#   ! S ,          (ClassDef, 'keywords'):                 # keyword*              -> _keywords                  _parse__keywords  - keywords and Starred bases can mix
#   ! S ,          (Call, 'keywords'):                     # keyword*              -> _keywords                  _parse__keywords  - keywords and Starred args can mix
#                                                                                  .
# * ! S ,          (FunctionDef, 'type_params'):           # type_param*           -> _type_params               _parse__type_params
# * ! S ,          (AsyncFunctionDef, 'type_params'):      # type_param*           -> _type_params               _parse__type_params
# * ! S ,          (ClassDef, 'type_params'):              # type_param*           -> _type_params               _parse__type_params
# * ! S ,          (TypeAlias, 'type_params'):             # type_param*           -> _type_params               _parse__type_params
#                                                                                  .
# * ! S ,          (With, 'items'):                        # withitem*             -> _withitems                 _parse__withitems        - no trailing commas
# * ! S ,          (AsyncWith, 'items'):                   # withitem*             -> _withitems                 _parse__withitems        - no trailing commas
#                                                                                  .
# * ! S ,          (Import, 'names'):                      # alias*                -> _aliases                   _parse__aliases_dotted   - no trailing commas
# * ! S ,          (ImportFrom, 'names'):                  # alias*                -> _aliases                   _parse__aliases_star     - no trailing commas
#                                                                                  .
#                                                                                  .
# * ! S ' '        (ListComp, 'generators'):               # comprehension*        -> _comprehensions            _parse__comprehensions
# * ! S ' '        (SetComp, 'generators'):                # comprehension*        -> _comprehensions            _parse__comprehensions
# * ! S ' '        (DictComp, 'generators'):               # comprehension*        -> _comprehensions            _parse__comprehensions
# * ! S ' '        (GeneratorExp, 'generators'):           # comprehension*        -> _comprehensions            _parse__comprehensions
#                                                                                  .
# * ! S    if      (comprehension, 'ifs'):                 # expr*                 -> _comprehension_ifs         _parse__comprehension_ifs
#                                                                                  .
# * ! S    @       (FunctionDef, 'decorator_list'):        # expr*                 -> _decorator_list            _parse__decorator_list
# * ! S    @       (AsyncFunctionDef, 'decorator_list'):   # expr*                 -> _decorator_list            _parse__decorator_list
# * ! S    @       (ClassDef, 'decorator_list'):           # expr*                 -> _decorator_list            _parse__decorator_list
#                                                                                  .
#                                                                                  .
# *   N    op      (Compare, 'left,ops:comparators'):      # expr,cmpop:expr*      -> _ops_comparators           _parse_expr / restrict expr or Compare
#                                                                                  .
#     N ao         (BoolOp, 'values'):                     # expr*                 -> BoolOp                     _parse_expr / restrict BoolOp  - interchangeable between and / or
#                                                                                  .
#                                                                                  .
#                  (JoinedStr, 'values'):                  # Constant|FormattedValue*   -> JoinedStr
#                  (TemplateStr, 'values'):                # Constant|Interpolation*    -> TemplateStr


# --- NOT CONTIGUOUS --------------------------------

# (arguments, 'posonlyargs'):           # arg*  - problematic because of defaults
# (arguments, 'args'):                  # arg*  - problematic because of defaults

# (arguments, 'kwonlyargs'):            # arg*  - maybe do as two-element, but is new type of two-element where the second element can be None
# (arguments, 'kw_defaults'):           # arg*

# could do argmnents slice as arguments instance (lots of logic needed on put)?

# (MatchClass, 'kwd_attrs'):            # identifier*  - maybe do as two-element
# (MatchClass, 'kwd_patterns'):         # pattern*


class slicestatic(NamedTuple):
    code_to:       Callable[[fst.FST, Code, bool, dict], fst.FST]
    sep:           str
    self_tail_sep: bool | Literal[0, 1] | None
    ret_tail_sep:  bool | Literal[0, 1] | None


def _set_loc_whole(self: fst.FST) -> fst.FST:  # self
    """Set location of `self` (which must be root) to the location of the whole source."""

    lines = self._lines
    ast = self.a
    ast.lineno = 1
    ast.col_offset = 0
    ast.end_lineno = len(lines)
    ast.end_col_offset = lines[-1].lenbytes

    return self._touch()


def _code_to_slice_expr(
    self: fst.FST,
    code: Code | None,
    one: bool,
    options: Mapping[str, Any],
    code_as: Callable = code_as_expr,
) -> fst.FST | None:
    """Convert code to sequence of expressions slice. Will accept `Tuple`, `List` and `Set` as sequences and will coerce
    any other expressions to a singleton `Tuple` sequence for use as a slice if allowed by `one` and / or `coerce`
    options. Will apply `norm_put` to recognize empty sets as empty slices according to options."""

    if code is None:
        return None

    fst_ = code_as(code, self.root.parse_params)
    ast_ = fst_.a
    is_slice_type = isinstance(ast_, (Tuple, List, Set))
    put_norm = None  # cached

    if not one:
        if put_norm := _get_option_norm('norm_put', 'set_norm', options):  # recognize put-normalized empty set
            if (fst_._is_empty_set_star() if put_norm == 'star' else
                fst_._is_empty_set_call() if put_norm == 'call' else
                fst_._is_empty_set_star() or fst_._is_empty_set_call()  # True or 'both'
            ):
                return None

        if is_slice_type:
            if not ast_.elts:  # put empty sequence is same as delete
                return None

            if fst_._is_parenthesized_tuple() is not False:  # anything that is not an unparenthesize tuple is restricted to the inside of the delimiters, which are removed
                fst_._trim_delimiters()
            else:  # if unparenthesized tuple then use whole source, including leading and trailing trivia not included
                _set_loc_whole(fst_)

            return fst_

    # one=True or any expression which is not a slice type we can coerce to a singleton slice

    if not is_slice_type and not (one or fst.FST.get_option('coerce', options)):
        raise ValueError(f'cannot put {fst_.a.__class__.__name__} as slice to {self.a.__class__.__name__} '
                         "without 'one=True' or 'coerce=True'")

    if (is_par := fst_._is_parenthesized_tuple()) is not None:
        if is_par is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
            fst_._delimit_node()

    elif isinstance(ast_, Set):
        _maybe_fix_Set(fst_, _get_option_norm('norm_put', 'set_norm', options) if put_norm is None else put_norm)

    elif isinstance(ast_, NamedExpr):  # this needs to be parenthesized if being put to unparenthesized tuple
        if not fst_.pars().n and self._is_parenthesized_tuple() is False:
            fst_._parenthesize_grouping()

    elif isinstance(ast_, (Yield, YieldFrom)):  # these need to be parenthesized definitely
        if not fst_.pars().n:
            fst_._parenthesize_grouping()

    ast_ = Tuple(elts=[fst_.a], ctx=Load(), lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),  # fst_.a because may have changed in Set processing
                 end_col_offset=ls[-1].lenbytes)  # Tuple as temporary container because it is valid target if checked in validate and allows _is_enclosed_or_line() check without delimiters to check content

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _code_to_slice_key_and_other(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any], code_as: Callable
) -> fst.FST | None:
    """Handles `Dict` and `MatchMapping`."""

    if code is None:
        return None

    if one:
        raise ValueError(f"cannot put as 'one' item to a {self.a.__class__.__name__} slice")

    fst_ = code_as(code, self.root.parse_params)
    ast_ = fst_.a

    if ast_.__class__ is not self.a.__class__:
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} must be a {self.a.__class__.__name__}"
                        f", not a {ast_.__class__.__name__}", rawable=True)

    if not ast_.keys and not getattr(ast_, 'rest', None):  # put empty sequence is same as delete, check `rest` because in that case MatchMapping is not empty
        return None

    return fst_


def _code_to_slice_Import_names(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'names', one, options, _aliases, code_as__Import_names)


def _code_to_slice_ImportFrom_names(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'names', one, options, _aliases, code_as__ImportFrom_names)


def _code_to_slice_BoolOp_values(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    """A `BoolOp` slice can be an invalid `AST` at length 0 or 1."""

    if code is None:
        return None

    fst_ = code_as_expr(code, self.root.parse_params)
    ast_ = fst_.a
    op_type = self.a.op.__class__
    is_slice_type = isinstance(ast_, BoolOp)
    is_same_op = is_slice_type and ast_.op.__class__ is self.a.op.__class__

    if is_slice_type and is_same_op and not one:
        if not ast_.values:  # put empty sequence is same as delete
            return None

        _set_loc_whole(fst_)

        return fst_

    # one=True or any expression which is not a BoolOp type with same operator we can coerce to a BoolOp slice

    if not (one or fst.FST.get_option('coerce', options)):
        if not is_slice_type:
            raise ValueError(f'cannot put {ast_.__class__.__name__} as slice to {self.a.__class__.__name__} '
                             "without 'one=True' or 'coerce=True'")

        elif not is_same_op:
            raise ValueError(f'cannot put {ast_.op.__class__.__name__} {ast_.__class__.__name__} '
                             f'as slice to {op_type.__name__} {self.a.__class__.__name__} '
                             "without 'one=True' or 'coerce=True'")

    if (is_par := fst_._is_parenthesized_tuple()) is not None:
        if is_par is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
            fst_._delimit_node()

    elif (
        (is_slice_type and (is_same_op or op_type is And))
        or isinstance(ast_, (NamedExpr, Yield, YieldFrom, IfExp))
    ):  # these need to be parenthesized definitely
        if not fst_.pars().n:
            fst_._parenthesize_grouping()

    ast_ = BoolOp(op=op_type(), values=[ast_], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                  end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _code_to_slice_BoolOp_values_maybe_dangling(
    self: fst.FST,
    code: Code | None,
    one: bool,
    options: Mapping[str, Any],
    is_first: bool,
    is_last: bool,
    is_ins: bool,
) -> fst.FST | None:
    """Get a normal `BoolOp` slice (including invalid length) or possibly one with a dangling left or right-side
    operator in case of replace and definitely one in case of insertion. The dangling operator may come from passed in
    source in `code` or be added to it if doesn't have according to where it can go and the `op_side` option.

    **Returns:**
    - `(FST, op_side_left)`: Returns an `FST` just like normal `code_to_*()` functions and also an operator side option
        indicating whether the operator side is left or right or neither. This may be inferred from slice location,
        source passed in for the slice and operation type, or it may come from the `op_side` option if allowed on either
        side and not specified explicitly in `code` source. If is an insertion then the operator is guaranteed to be
        dangling on the correct side in the `FST` source returned.
    """

    op_side_left = _get_option_op_side(is_first, is_last, options)

    if code is None:
        return None, op_side_left

    try:  # most likely case for BoolOp is pure expr so we try getting that first before checking for dangling op versions
        fst_ = _code_to_slice_BoolOp_values(self, code, one, options)

    except SyntaxError:  # maybe a dangling op in source, if conditions allow then check for this
        if one:
            raise

        if not (is_first and is_last) and ((is_str := isinstance(code, str)) or isinstance(code, list)):  # can only be present if replacement is not of entire BoolOp from first to last
            if is_str:
                lines = (src := code).split('\n')
            else:
                src = '\n'.join(lines := code)

            parse_params = self.root.parse_params
            ast_ = None

            if not is_first:  # dangling op can be on the left
                try:
                    ast_ = parse__BoolOp_dangling_left(src, parse_params, loc_whole=True)
                    op_side_left = True

                except SyntaxError:
                    pass

            if not is_last and not ast_:  # dangling op can be on the right and hasn't already been parsed on the left
                try:
                    ast_ = parse__BoolOp_dangling_right(src, parse_params, loc_whole=True)
                    op_side_left = False

                except SyntaxError:
                    pass

            if ast_:
                if ast_.op.__class__ is not self.a.op.__class__:
                    raise ParseError('dangling BoolOp operator does not match') from None

                return fst.FST(ast_, lines, None, parse_params=parse_params), op_side_left

        raise  # reraise original _code_to_slice_BoolOp_values() exception

    # parsed successfully so post-process to add dangling op if needed

    if not fst_:
        return None, op_side_left

    if is_ins:  # if is insert then a dangling operator MUST be added, op_side_left will be either True or False here
        values = fst_.a.values

        if op_side_left:
            ln, col, _, _ = values[0].f.pars()
            op_lines = ['and '] if isinstance(self.a.op, And) else ['or ']

            fst_._put_src(op_lines, ln, col, ln, col, False)  # we don't care if we offset fst_ itself incorrectly since we will set its location to whole source anyway, we only care about the children here

        else:  # op_side_left is False
            _, _, end_ln, end_col = values[-1].f.pars()
            op_lines = [' and'] if isinstance(self.a.op, And) else [' or']

            fst_._put_src(op_lines, end_ln, end_col, end_ln, end_col)  # we offset nothing because we reset fst_ location to whole anyway

        return _set_loc_whole(fst_), op_side_left

    return fst_, None


def _code_to_slice_Compare__all(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    """A `Compare._all` slice is a normal `Compare` for two or more elements and can be a singleton with a single
    element in `Compare.left`. Zero-length `Compare` slices not supported currently."""

    if code is None:
        return None

    fst_ = code_as_expr(code, self.root.parse_params)
    ast_ = fst_.a
    is_slice_type = isinstance(ast_, Compare)

    if is_slice_type and (not one or not ast_.comparators):  # if is singleton Comparator invalid AST slice then we just return it even if putting as one=True since by fact that it was already in a Compare it doesn't need any pars added
        _set_loc_whole(fst_)

        return fst_

    # one=True or any expression which is not a Compare type we can coerce to a singleton Compare slice

    if not is_slice_type and not (one or fst.FST.get_option('coerce', options)):
        raise ValueError(f'cannot put {ast_.__class__.__name__} as slice to {self.a.__class__.__name__} '
                         "without 'one=True' or 'coerce=True'")

    if (is_par := fst_._is_parenthesized_tuple()) is not None:
        if is_par is False:  # don't put unparenthesized tuple source as one into sequence, it would merge into the sequence
            fst_._delimit_node()

    elif (
        is_slice_type
        or isinstance(ast_, (NamedExpr, Yield, YieldFrom, IfExp, BoolOp))
        or (isinstance(ast_, UnaryOp) and isinstance(ast_.op, Not))
    ):  # these need to be parenthesized definitely
        if not fst_.pars().n:
            fst_._parenthesize_grouping()

    ast_ = Compare(left=ast_, ops=[], comparators=[], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                   end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _code_to_slice_Compare__all_maybe_dangling(
    self: fst.FST,
    code: Code | None,
    one: bool,
    options: Mapping[str, Any],
    is_first: bool,
    is_last: bool,
    is_ins: bool,
) -> fst.FST | None:
    """Get a normal `Compare` slice (including invalid length) or possibly one with a dangling left or right-side
    operator in case of replace and definitely one in case of insertion. The dangling operator may come from passed in
    source in `code` or be added to it from the `op` option if doesn't have according to where it can go and the
    `op_side` option. For deletions an `op` is obviously not needed but the `op_side` is used as a hint.

    The `op` option is accepted as a `Code` so can be a `str`, `list[str]`, `AST`, `FST` as well as a direct `cmpop`
    `type[AST]` class (not instance).

    **Returns:**
    - `(FST, op_side_left)`: Returns an `FST` just like normal `code_to_*()` functions and also an operator side option
        indicating whether the operator side is left or right or neither. This may be inferred from slice location,
        source passed in for the slice and operation type, or it may come from the `op_side` option if allowed on either
        side and not specified explicitly in `code` source. If is an insertion then the operator is guaranteed to be
        dangling on the correct side in the `FST` source returned. If there is a dangling operator then either the
        `left` field or the last `comparators` will be a placeholder `AST` with a location for the start or end of the
        `Compare` expression (with the dangling operator).
    """

    op_side_left = _get_option_op_side(is_first, is_last, options)

    if code is None:
        return None, op_side_left

    try:  # most likely case for Compare is pure expr so we try getting that first before checking for dangling op versions
        fst_ = _code_to_slice_Compare__all(self, code, one, options)

    except SyntaxError:  # maybe a dangling op in source, if conditions allow then check for this
        if one:
            raise

        if not (is_first and is_last) and ((is_str := isinstance(code, str)) or isinstance(code, list)):  # can only be present if replacement is not of entire Compare from first to last
            if is_str:
                lines = (src := code).split('\n')
            else:
                src = '\n'.join(lines := code)

            parse_params = self.root.parse_params
            ast_ = None

            if not is_first:  # dangling op can be on the left
                try:
                    ast_ = parse__Compare_dangling_left(src, parse_params, loc_whole=True)
                    op_side_left = True

                except SyntaxError:
                    pass

            if not is_last and not ast_:  # dangling op can be on the right and hasn't already been parsed on the left
                try:
                    ast_ = parse__Compare_dangling_right(src, parse_params, loc_whole=True)
                    op_side_left = False

                except SyntaxError:
                    pass

            if ast_:
                return fst.FST(ast_, lines, None, parse_params=parse_params), op_side_left

        raise  # reraise original _code_to_slice_Compare__all() exception

    # parsed successfully so post-process to add dangling op if needed

    if not fst_:
        return None, op_side_left

    if op_side_left is None:
        return fst_, None

    if not (op := options.get('op')):
        if is_ins:  # if is insert then a dangling operator MUST be added from a non-global `op` option which must be present, op_side_left will be either True or False in that case
            raise ValueError("insertion to Compare requires and 'op' extra operator to insert")

        return fst_, None

    if isinstance(op, str):
        op_lines = op.split('\n')
        op_ast = parse_cmpop(op)

    elif isinstance(op, cmpop):
        op_lines = [OPCLS2STR[op_cls := op.__class__]]
        op_ast = op_cls()

    elif isinstance(op, fst.FST):
        if not op.is_root:
            raise ValueError("expecting root node for 'op' option")

        op_lines = op._lines
        op_ast = op.a  # this is fine like this and no unmake because it is just reset in FST() below

        if not isinstance(op_ast, cmpop):
            raise NodeError(f"expecting cmpop for 'op' option, got {op_ast.__class__.__name__}")

    elif isinstance(op, list):
        op_lines = op
        op_ast = parse_cmpop('\n'.join(op))

    elif isinstance(op, type):
        if issubclass(op, cmpop):
            op_lines = [OPCLS2STR[op]]
            op_ast = op()

        else:
            raise (NodeError if issubclass(op, AST) else ValueError)(
                    "expecting cmpop source, AST, FST or AST type for 'op' option, "
                    f"got {op.__qualname__}")

    else:
        raise ValueError("expecting cmpop source, AST, FST or AST type for 'op' option, "
                        f"got {op.__class__.__qualname__}")

    ast_ = fst_.a
    ops = ast_.ops
    comparators = ast_.comparators
    idx = len(ops)

    if op_side_left:
        left = ast_.left
        left_ln, left_col, _, _ = left.f.pars()

        bound_end_ln = len(op_lines) - 1
        bound_end_col = len(op_lines[-1])

        end_ln, end_col, src = next_frag(op_lines, 0, 0, bound_end_ln, bound_end_col)  # must be there

        lineno = left_ln + end_ln + 1  # these are for the placeholder left node
        col_offset = len(op_lines[end_ln][:end_col].encode())

        if not end_ln:  # if op starts on first line then it must be offset by left location because it will be on that line in fst_
            col_offset += fst_._lines[left_ln].c2b(left_col)

        if isinstance(op_ast, (IsNot, NotIn)):  # if two-part operator move on to second part
            end_ln, end_col, src = next_frag(op_lines, end_ln, end_col + len(src), bound_end_ln, bound_end_col)  # must be there

        if end_ln == bound_end_ln and end_col + len(src) == bound_end_col:  # operator right at end of lines, needs a whitespace
            op_lines[end_ln] = op_lines[end_ln] + ' '

        elif re_line_end_cont_or_comment.match(op_lines[l := len(op_lines) - 1]).group(1):  # if last line is a comment or line continuation without a newline then add one
            op_lines.append('')

        fst_._put_src(op_lines, left_ln, left_col, left_ln, left_col, False)  # we don't care if we offset fst_ itself incorrectly since we will set its location to whole source anyway, we only care about the children here

        placeholder = astfield('')
        ast_.left = fst.FST(Pass(lineno=lineno, col_offset=col_offset,
                                end_lineno=lineno, end_col_offset=col_offset),
                            fst_, placeholder).a

        ops.insert(0, fst.FST(op_ast, fst_, placeholder).a)
        comparators.insert(0, left)

        for i, (cmp, op) in enumerate(zip(comparators, ops, strict=True)):
            cmp.f.pfield = astfield('comparators', i)
            op.f.pfield = astfield('ops', i)

    else:  # op_side_left is False
        _, _, end_ln, end_col = (comparators[-1] if comparators else ast_.left).f.pars()

        if (l := op_lines[0]) and not l.isspace():  # if no whitespace before operator then insert one
            op_lines[0] = ' ' + l

        ln, col, src = prev_frag(op_lines, 0, 0, len(op_lines) - 1, 0x7fffffffffffffff)  # must be there, last part of op, can search from (0, 0) because is an op so we know there are no strings (which are the things which can screw up the searches)
        col += len(src)  # we want the end

        end_lineno = end_ln + ln + 1  # these are for the placeholder comparator node
        end_col_offset = len(op_lines[ln][:col].encode())

        if not ln:  # if op ends on first line then it must be offset by location because it will be on that line in fst_
            end_col_offset += fst_._lines[end_ln].c2b(end_col)

        fst_._put_src(op_lines, end_ln, end_col, end_ln, end_col)  # we offset nothing because we reset fst_ location to whole anyway

        ops.append(fst.FST(op_ast, fst_, astfield('ops', idx)).a)
        comparators.append(fst.FST(Pass(lineno=end_lineno, col_offset=end_col_offset,
                                        end_lineno=end_lineno, end_col_offset=end_col_offset),
                                fst_, astfield('comparators', idx)).a)  # placeholder

    return _set_loc_whole(fst_), op_side_left


def _code_to_slice_MatchSequence(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    if code is None:
        return None

    fst_ = code_as_pattern(code, self.root.parse_params)

    if one:
        if fst_._is_delimited_matchseq() == '':
            fst_._delimit_node(delims='[]')

        ast_ = MatchSequence(patterns=[fst_.a], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                             end_col_offset=ls[-1].lenbytes)

        return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)

    ast_ = fst_.a

    if not isinstance(ast_, MatchSequence):
        raise NodeError(f"slice being assigned to a {self.a.__class__.__name__} "
                        f"must be a MatchSequence, not a {ast_.__class__.__name__}", rawable=True)

    if not ast_.patterns:  # put empty sequence is same as delete
        return None

    if fst_._is_delimited_matchseq():  # delimited is restricted to the inside of the delimiters, which are removed
        fst_._trim_delimiters()
    else:  # if undelimited then use whole source, including leading and trailing trivia not included
        _set_loc_whole(fst_)

    return fst_


def _code_to_slice_MatchOr(self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]) -> fst.FST | None:
    if code is None:
        return None

    try:
        fst_ = code_as_pattern(code, self.root.parse_params, allow_invalid_matchor=True)

    except SyntaxError:
        if isinstance(code, str):
            code = code.split('\n')
        elif not isinstance(code, list):
            raise

        if next_frag(code, 0, 0, len(code) - 1, len(code[-1])):
            raise

        return None  # nothing other than maybe comments or line continuations present, empty pattern, not an error but delete

    ast_ = fst_.a

    if isinstance(ast_, MatchOr):
        if not (patterns := ast_.patterns):
            return None

        fst_pars = fst_.pars()

        if not one or len(patterns) == 1:
            if fst_pars.n:
                fst_._unparenthesize_grouping(False)

            _set_loc_whole(fst_)

            return fst_

        if not fst_pars.n:
            fst_._parenthesize_grouping()

    else:
        if not one and not _get_option_norm('norm_put', 'matchor_norm', options):
            raise NodeError(f"slice being assigned to a MatchOr "
                            f"must be a MatchOr with norm_put=False, not a {ast_.__class__.__name__}",
                            rawable=True)

        if isinstance(ast_, MatchAs):
            if ast_.pattern is not None and not fst_.pars().n:
                fst_._parenthesize_grouping()

        elif isinstance(ast_, MatchSequence):
            if not fst_._is_delimited_matchseq():
                fst_._delimit_node(delims='[]')

    ast_ = MatchOr(patterns=[ast_], lineno=1, col_offset=0, end_lineno=len(ls := fst_._lines),
                   end_col_offset=ls[-1].lenbytes)

    return fst.FST(ast_, ls, None, from_=fst_, lcopy=False)


def _code_to_slice__special(
    self: fst.FST,
    code: Code | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
    type_ast: type[AST],
    code_as: Callable,
) -> fst.FST | None:
    if code is None:
        return None

    coerce = fst.FST.get_option('coerce', options)

    if (one
        and not coerce
        and (
            isinstance(code, type_ast)
            or (
                isinstance(code, fst.FST)
                and isinstance(code.a, type_ast)
    ))):
        raise ValueError(f"cannot put {type_ast.__name__} node as 'one=True' without 'coerce=True'")

    fst_ = code_as(code, self.root.parse_params, coerce=one or coerce)

    return fst_ if getattr(fst_.a, field, None) else None  # put empty sequence is same as delete


def _code_to_slice__Assign_targets(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'targets', one, options, _Assign_targets, code_as__Assign_targets)


def _code_to_slice__decorator_list(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'decorator_list', one, options, _decorator_list, code_as__decorator_list)


def _code_to_slice__comprehensions(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'generators', one, options, _comprehensions, code_as__comprehensions)


def _code_to_slice__comprehensions_ifs(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'ifs', one, options, _comprehension_ifs, code_as__comprehension_ifs)


def _code_to_slice__aliases(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'names', one, options, _aliases, code_as__aliases)


def _code_to_slice__withitems(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'items', one, options, _withitems, code_as__withitems)


def _code_to_slice__type_params(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    return _code_to_slice__special(self, code, 'type_params', one, options, _type_params, code_as__type_params)


def _code_to_slice__expr_arglikes(
    self: fst.FST, code: Code | None, one: bool, options: Mapping[str, Any]
) -> fst.FST | None:
    if code is None:
        return None

    if one:
        fst_ = _coerce_as__expr_arglikes(code, self.root.parse_params)
    else:
        fst_ = code_as__expr_arglikes(code, self.root.parse_params, coerce=fst.FST.get_option('coerce', options))

    return fst_ if fst_.a.elts else None  # put empty sequence is same as delete


def _put_slice_asts(
    self: fst.FST,
    start: int,
    stop: int,
    field: str,
    body: list[AST],
    fst_: fst.FST | None,
    asts: list[AST] | None,
    ctx: type[expr_context] | None = None,
) -> None:
    """Put or delete the actual `AST` nodes to `self` body and create `FST` nodes for them."""

    self._unmake_fst_tree(body[start : stop])

    if not asts:
        len_asts = 0

        del body[start : stop]

    else:
        len_asts = len(asts)

        fst_._unmake_fst_parents(True)

        body[start : stop] = asts

        FST = fst.FST
        new_fsts = [FST(body[i], self, astfield(field, i)) for i in range(start, start + len_asts)]

        if new_fsts and ctx:
            set_ctx([f.a for f in new_fsts], ctx)

        self._make_fst_tree(new_fsts)

    for i in range(start + len_asts, len(body)):
        body[i].f.pfield = astfield(field, i)


def _put_slice_asts2(
    self: fst.FST,
    start: int,
    stop: int,
    field2: str,
    body: list[AST],
    body2: list[AST],
    fst_: fst.FST | None,
    asts: list[AST] | None,
    asts2: list[AST] | None,
) -> None:
    """Put or delete the actual `AST` nodes to `self` body and create `FST` nodes for them. This is the two element
    version for Dict and MatchMapping."""

    self._unmake_fst_tree(body[start : stop] + body2[start : stop])

    if not asts:
        len_asts = 0

        del body[start : stop]
        del body2[start : stop]

    else:
        len_asts = len(asts)

        fst_._unmake_fst_parents(True)

        body[start : stop] = asts
        body2[start : stop] = asts2

        FST = fst.FST
        new_fsts = []

        for i in range(len_asts):
            startplusi = start + i

            new_fsts.append(FST(body2[startplusi], self, astfield(field2, startplusi)))

            if key := body[startplusi]:
                new_fsts.append(FST(key, self, astfield('keys', startplusi)))

        self._make_fst_tree(new_fsts)

    for i in range(start + len_asts, len(body)):
        body2[i].f.pfield = astfield(field2, i)

        if key := body[i]:  # could be None from ** in Dict
            key.f.pfield = astfield('keys', i)


def _validate_put_seq(
    self: fst.FST, fst_: fst.FST, non_slice: str, *, check_target: Literal[False] | Callable = False
) -> None:  # check_target like is_valid_target()
    if not fst_:
        return

    ast = self.a
    ast_ = fst_.a

    if non_slice and isinstance(ast_, Tuple) and any(isinstance(e, Slice) for e in ast_.elts):
        raise NodeError(f'cannot put Slice into {non_slice}')

    if check_target:
        ctx = getattr(ast, 'ctx', None)

        if not isinstance(ctx, Load) and not check_target(ast_.elts):
            raise NodeError(f'invalid slice for {ast.__class__.__name__}'
                            f'{f" {ctx.__class__.__name__}" if ctx else ""} target')


def _put_slice_seq_and_asts(
    self: fst.FST,
    start: int,
    stop: int,
    field: str,
    body: list[AST],
    fst_: fst.FST | None,
    fst_field: str,
    ctx: type[expr_context] | None,
    bound_ln: int,
    bound_col: int,
    bound_end_ln: int,
    bound_end_col: int,
    sep: str,
    self_tail_sep: bool | Literal[0, 1] | None,
    options: Mapping[str, Any],
) -> None:
    """Helper for most slice put operations."""

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, field, None, sep, self_tail_sep)

        _put_slice_asts(self, start, stop, field, body, None, None)

    else:
        fst_body = getattr(fst_.a, fst_field)

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len(fst_body),
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, field, None, sep, self_tail_sep)

        _put_slice_asts(self, start, stop, field, body, fst_, fst_body, ctx)

    put_slice_sep_end(self, end_params)


_SPECIAL_SLICE_STATICS = {
    _Assign_targets: slicestatic(_code_to_slice__Assign_targets, '=', True, True),
    _aliases:        slicestatic(_code_to_slice__aliases, ',', False, False),
    _withitems:      slicestatic(_code_to_slice__withitems, ',', False, False),
    _type_params:    slicestatic(_code_to_slice__type_params, ',', False, False),
}


# ......................................................................................................................

def _put_slice_NOT_IMPLEMENTED_YET(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    raise NotImplementedError("not implemented yet, try with option raw='auto'")


def _put_slice_Tuple_elts(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """Tuple is used in many different ways in python, also for expressionish slices by us."""

    ast = self.a
    body = ast.elts
    start, stop = fixup_slice_indices(len(body), start, stop)

    fst_ = _code_to_slice_expr(self, code, one, options, code_as_expr_all)

    if not fst_ and start == stop:
        return

    # extra checks for tuple special usage

    is_par = self._is_delimited_seq()
    pfield = self.pfield
    is_slice = pfield and pfield.name == 'slice'
    need_par = False

    if fst_:
        fst_body = fst_.a.elts

        if len(fst_body) == 1 and isinstance(b0 := fst_body[0], Tuple) and any(isinstance(e, Slice) for e in b0.elts):  # putting a tuple with Slices as one
            raise NodeError('cannot put tuple with Slices to tuple')

        if PYLT11:
            if is_slice and not is_par and any(isinstance(e, Starred) for e in fst_body):
                if any(isinstance(e, Slice) for i, e in enumerate(body) if i < start or i >= stop):
                    raise NodeError('cannot put Starred to a slice Tuple containing Slices')

                need_par = True

        elif PYGE14:
            if not is_par and pfield and pfield.name == 'type' and any(isinstance(e, Starred) for e in fst_body):  # if putting Starred to unparenthesized ExceptHandler.type Tuple then parenthesize it
                need_par = True

    # normal stuff

    _validate_put_seq(self, fst_,
                      '' if not pfield or (is_slice and not is_par) else 'non-root non-unparenthesized-slice Tuple',
                      check_target=is_valid_target)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if is_par:
        bound_col += 1
        bound_end_col -= 1

    _put_slice_seq_and_asts(self, start, stop, 'elts', body, fst_, 'elts', ast.ctx.__class__,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', 1, options)

    is_par = self._maybe_fix_tuple(is_par)

    if need_par and not is_par:
        self._delimit_node()


def _put_slice_List_elts(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.elts
    start, stop = fixup_slice_indices(len(body), start, stop)

    fst_ = _code_to_slice_expr(self, code, one, options)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'List', check_target=is_valid_target)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    _put_slice_seq_and_asts(self, start, stop, 'elts', body, fst_, 'elts', ast.ctx.__class__,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', None, options)


def _put_slice_Set_elts(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    body = self.a.elts
    start, stop = fixup_slice_indices(len(body), start, stop)

    fst_ = _code_to_slice_expr(self, code, one, options)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'Set')

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    _put_slice_seq_and_asts(self, start, stop, 'elts', body, fst_, 'elts', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', None, options)

    _maybe_fix_Set(self, _get_option_norm('norm_self', 'set_norm', options))


def _put_slice_Dict__all(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.keys
    body2 = ast.values
    start, stop = fixup_slice_indices(len(body), start, stop)

    fst_ = _code_to_slice_key_and_other(self, code, one, options, code_as_expr)

    if not fst_:
        if start == stop:  # delete empty slice
            return

    else:
        fst_._trim_delimiters()

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'keys', 'values')

        _put_slice_asts2(self, start, stop, 'values', body, body2, None, None, None)

    else:
        ast_ = fst_.a
        fst_body = ast_.keys
        fst_body2 = ast_.values
        fst_first = a.f if (a := fst_body[0]) else None

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_first, fst_body2[-1].f, len(fst_body),
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'keys', 'values')

        _put_slice_asts2(self, start, stop, 'values', body, body2, fst_, fst_body, fst_body2)

    put_slice_sep_end(self, end_params)


def _put_slice_Delete_targets(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """Even though when getting a slice it will be returned as a `Tuple`, any sequence of valid target types is accepted
    for the put operation. If putting a non-sequence element, it will be automatically put as `one=True` to match the
    non-comma terminated syntax of `Delete` targets (a non-sequence `FST` or `AST` will not be accepted like this). This
    allows correct-appearing syntax like `delfst.targets = 'target'` to work."""

    ast = self.a
    body = ast.targets
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice_expr(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError("cannot delete all Delete.targets without norm_self=False")

    _validate_put_seq(self, fst_, 'Delete', check_target=is_valid_del_target)

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_Delete_targets(self)

    _put_slice_seq_and_asts(self, start, stop, 'targets', body, fst_, 'elts', Del,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', False, options)

    if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
        if body:
            _, _, bound_ln, bound_col = body[-1].f.pars()

        _maybe_fix_stmt_end(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                            ast.end_lineno, ast.end_col_offset)

    ln, col, _, _ = self.loc

    self._maybe_fix_joined_alnum(ln, col + 3)
    self._maybe_add_line_continuations()


def _put_slice_Assign_targets(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    body = self.a.targets
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice__Assign_targets(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError("cannot delete all Assign.targets without norm_self=False")

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_Assign_targets(self)

    _put_slice_seq_and_asts(self, start, stop, 'targets', body, fst_, 'targets', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, '=', True, options)

    _maybe_fix_Assign_target0(self)
    self._maybe_add_line_continuations()


def _put_slice_With_AsyncWith_items(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.items
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice__withitems(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError(f'cannot delete all {ast.__class__.__name__}.items without norm_self=False')

    pars = self._loc_With_items_pars()  # may be pars or may be where pars would go from just after `with` to end of block header `:`
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    _put_slice_seq_and_asts(self, start, stop, 'items', body, fst_, 'items', None,
                            pars_ln, pars_col + pars_n, pars_end_ln, pars_end_col - pars_n, ',', False, options)

    if not pars_n:  # only need to fix maybe if there are no parentheses
        if not self._is_enclosed_or_line(pars=False):  # if no parentheses and wound up not valid for parse then adding parentheses around items should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_With_items_pars()

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, False)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        if not start:  # if not adding pars then need to make sure del or put didn't join new first `withitem` with the `with`
            ln, col, _, _ = pars.bound

            self._maybe_fix_joined_alnum(ln, col)


def _put_slice_Import_names(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.names
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice_Import_names(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError('cannot delete all Import.names without norm_self=False')

    _, _, bound_end_ln, bound_end_col = self.loc

    if start:
        _, _, bound_ln, bound_col = body[start - 1].f.pars()
    elif body:
        bound_ln, bound_col, _, _ = body[0].f.pars()
    else:
        bound_ln = bound_end_ln
        bound_col = bound_end_col

    _put_slice_seq_and_asts(self, start, stop, 'names', body, fst_, 'names', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', False, options)

    if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
        if body:
            _maybe_fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                ast.end_lineno, ast.end_col_offset)
        else:
            _maybe_fix_stmt_end(self, bound_ln + 1, self.root._lines[bound_ln].c2b(bound_col),
                                ast.end_lineno, ast.end_col_offset)

    self._maybe_add_line_continuations()  # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this


def _put_slice_ImportFrom_names(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.names
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    put_star = False

    fst_ = _code_to_slice_ImportFrom_names(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError('cannot delete all ImportFrom.names without norm_self=False')

    else:
        if put_star := (fst_.a.names[0].name == '*'):  # if putting star then it must overwrite everything
            if len_slice != len_body:
                raise NodeError("if putting star '*' alias it must overwrite all other aliases")

        elif body and body[0].name == '*':  # putting to star then it must be overwritten
            if start > 0 or stop < 1:
                raise NodeError("if putting over star '*' alias it must be overwritten")

    pars = self._loc_ImportFrom_names_pars()  # may be pars or may be where pars would go from just after `import` to end of node
    pars_ln, pars_col, pars_end_ln, pars_end_col = pars
    pars_n = pars.n

    _put_slice_seq_and_asts(self, start, stop, 'names', body, fst_, 'names', None,
                            pars_ln, pars_col + pars_n, pars_end_ln, pars_end_col - pars_n, ',', False, options)

    if not pars_n:  # only need to fix maybe if there are no parentheses
        if stop == len_body:  # if del till and something left then may need to reset end position of self due to new trailing trivia
            if body:
                _maybe_fix_stmt_end(self, (bn := body[-1]).end_lineno, bn.end_col_offset,
                                    ast.end_lineno, ast.end_col_offset)
            else:
                _maybe_fix_stmt_end(self, pars_ln + 1, self.root._lines[pars_ln].c2b(pars_col),
                                    ast.end_lineno, ast.end_col_offset)

        if not self._is_enclosed_or_line(pars=False):  # if no parentheses and wound up not valid for parse then adding parentheses around names should fix
            pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ImportFrom_names_pars()

            self._put_src(')', pars_end_ln, pars_end_col, pars_end_ln, pars_end_col, True, False, self)
            self._put_src('(', pars_ln, pars_col, pars_ln, pars_col, False)

        # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this

    elif put_star:  # if put star then must remove parentheses (including any trivia inside them)
        pars_ln, pars_col, pars_end_ln, pars_end_col = self._loc_ImportFrom_names_pars()
        star_ln, star_col, star_end_ln, star_end_col = body[0].f.loc

        self._put_src(None, star_end_ln, star_end_col, pars_end_ln, pars_end_col, True)
        self._put_src(None, pars_ln, pars_col, star_ln, star_col, False)


def _put_slice_Global_Nonlocal_names(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """In order to do this put since `Global` and `Nonlocal` do not have child `AST` nodes but just identifiers, we
    create a temporary container which does have `Name` elements for each name and operate on that. Afterwards we get
    rid of that but the modified source identifiers remain."""

    ast = self.a
    body = ast.names
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice_expr(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
            raise ValueError(f'cannot delete all {ast.__class__.__name__}.names without norm_self=False')

    else:
        npars = 0

        if not all(isinstance(bad := e, Name) and not (npars := e.f.pars().n) for e in fst_.a.elts):
            raise NodeError(f'cannot put{" parenthesized" if npars else ""} {bad.__class__.__name__} '
                            f'to {ast.__class__.__name__}.names')

        # TODO? could have some logic here to strip trailing newline from fst_ if putting at end and there is no trivia on same line as last element to not introduce a spurisous newline? seems a bit over-the-top, XXX be careful of semicolons separating statements!

    ln, end_col, bound_end_ln, bound_end_col = self.loc

    lines = self.root._lines
    tmp_elts = []  # these will be temporary AST nodes so that we can edit the source using existing code
    end_col += 5 if isinstance(ast, Global) else 7  # will have another +1 added in search

    for _ in range(len_body):
        ln, col, src = next_find_re(lines, ln, end_col + 1, bound_end_ln, bound_end_col, re_identifier)  # must be there, + 1 probably skips comma
        lineno = ln + 1
        end_col = col + len(src)

        tmp_elts.append(Name(id=src, ctx=Load(), lineno=lineno, col_offset=(l := lines[ln]).c2b(col), end_lineno=lineno,
                             end_col_offset=l.c2b(end_col)))

    if tmp_elts:
        tmp_ast = Tuple(elts=tmp_elts, ctx=Load(), lineno=(e0 := tmp_elts[0]).lineno, col_offset=e0.col_offset,
                        end_lineno=(en := tmp_elts[-1]).end_lineno, end_col_offset=en.end_col_offset)
    else:
        tmp_ast = Tuple(elts=tmp_elts, ctx=Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=0)

    self._set_ast(tmp_ast)  # temporarily swap out Global/Nonlocal AST for temporary Tuple AST so that offsetting propagates to the parents

    if tmp_elts:
        bound_ln, bound_col, last_end_ln, last_end_col = tmp_elts[0].f.loc

        if not start:
            last_end_ln = bound_ln
            last_end_col = bound_col

        elif start != 1:
            _, _, last_end_ln, last_end_col = tmp_elts[start - 1].f.loc

    else:
        bound_ln = last_end_ln = bound_end_ln
        bound_col = last_end_col = bound_end_col

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'elts', None, ',', False)

        del body[start : stop]  # this is the real update

        _put_slice_asts(self, start, stop, 'elts', tmp_elts, None, None)  # this is the fake temporary update

    else:
        fst_body = fst_.a.elts
        fst_last = fst_body[-1].f

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_last, len(fst_body),
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'elts', None, ',', False)

        body[start : stop] = [e.id for e in fst_body]  # this is the real update

        _put_slice_asts(self, start, stop, 'elts', tmp_elts, fst_, fst_body)  # this is the fake temporary update, lets just pretend like its has real AST children, needed for put_slice_sep_end()

    put_slice_sep_end(self, end_params)

    if fst_:  # we get it here because ._set_ast() below makes this impossible
        fst_last_loc = tmp_elts[-1].f.loc

    ast.end_lineno = tmp_ast.end_lineno  # copy new end from temporary FST to self (since it was swapped out)
    ast.end_col_offset = tmp_ast.end_col_offset

    self._set_ast(ast, True)

    if stop == len_body:  # if del OR put till and something left then may need to reset end position of self due to new trailing trivia, put because could come from trailing trivia of last element of parenthesized tuple
        if fst_:
            _, _, last_end_ln, last_end_col = fst_last_loc

        _maybe_fix_stmt_end(self, last_end_ln + 1, lines[last_end_ln].c2b(last_end_col),
                            ast.end_lineno, ast.end_col_offset)

    self._maybe_add_line_continuations()  # THEORETICALLY could need to _maybe_fix_joined_alnum() but only if the user goes out of their way to F S up, so we don't bother with this


def _put_slice_ClassDef_bases(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.bases
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice__expr_arglikes(self, code, one, options)

    if not fst_ and not len_slice:
        return

    _validate_put_seq(self, fst_, 'ClassDef.bases')

    if keywords := ast.keywords:
        if body and keywords[0].f.loc[:2] < body[stop - 1].f.loc[2:] and stop:
            raise NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')

    bound_ln, bound_col, bound_end_ln, bound_end_col = bases_pars = self._loc_ClassDef_bases_pars()

    if not fst_:
        if not keywords and len_slice == len_body:  # deleting everything so remove pars
            self._put_src(None, bound_ln, bound_col, bound_end_ln, bound_end_col, False)

            end_params = None

        else:
            bound_col += 1
            bound_end_col -= 1
            self_tail_sep = (start and keywords and stop == len_body) or None

            end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                             bound_ln, bound_col, bound_end_ln, bound_end_col,
                                             options, 'bases', None, ',', self_tail_sep)

        _put_slice_asts(self, start, stop, 'bases', body, None, None)

    else:
        if bases_pars.n:
            bound_col += 1
            bound_end_col -= 1

        else:  # parentheses don't exist, add them first
            self._put_src('()', bound_ln, bound_col, bound_end_ln, bound_end_col, False)

            bound_col += 1
            bound_end_col = bound_col
            bound_end_ln = bound_ln

        self_tail_sep = (keywords and stop == len_body) or None
        fst_body = fst_.a.elts

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len(fst_body),
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'bases', None, ',', self_tail_sep)

        _put_slice_asts(self, start, stop, 'bases', body, fst_, fst_body)

    if end_params:
        put_slice_sep_end(self, end_params)

        if self_tail_sep:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
            self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there


def _put_slice_decorator_list(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """This handles `FunctionDef`, `AsyncFunctionDef`, `ClassDef` and the `_decorator_list` SPECIAL SLICE. Since a
    decorator list is a very unique slice we need to do more fixing than ususal for newlines here."""

    ast = self.a
    body = ast.decorator_list
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice__decorator_list(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

    else:  # add leading and trailing newline so that put_slice_nosep() to recognize it as requring own line(s), is fine adding if they already there because they were stripped on get so we just putting back +1 even if there are others
        ast_ = fst_.a
        ast_.end_lineno += 2  # because we will not _offset() self
        ast_.end_col_offset = 0
        fst_lines = fst_._lines

        fst_lines.insert(0, bistr(''))
        fst_lines.append(bistr(''))

        fst_._offset(0, 0, 1, 0, True, self_=False)
        fst_._touch()  # because of the self_=False in _offset()

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_decorator_list(self)

    locfunc = lambda body, idx: body[idx].f.parent._loc_decorator(idx)

    root = self.root
    lines = root._lines  # for fixes after put or del
    old_last_line = lines[-1]
    old_first_line = lines[bound_ln]

    if not fst_:
        put_slice_nosep(self, start, stop, None, None, None,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'decorator_list', locfunc)

        _put_slice_asts(self, start, stop, 'decorator_list', body, None, None)

        _maybe_fix_decorator_list_del(self, start, bound_ln, old_first_line, old_last_line)

    else:
        old_body_empty = not body  # for fixes after put
        old_loc = self.loc

        fst_body = fst_.a.decorator_list

        put_slice_nosep(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'decorator_list', locfunc, False)

        _put_slice_asts(self, start, stop, 'decorator_list', body, fst_, fst_body)

        if _maybe_fix_decorator_list_trailing_newline(self, old_last_line):
            pass  # noop

        elif old_body_empty and bound_ln == old_loc.ln:  # if inserted to nonexistent decorators right at start of node line then the node will not have been offset correctly because hierarchically the decorators are INSIDE this node even though syntactically they precede it
            ast.lineno += self.end_ln - old_loc.end_ln  # the end will have been offset correctly so we use that as the delta that we need to apply to start

            self._touch()

        elif not old_first_line and lines[bound_ln] is not old_first_line:  # bound was at end of previous line and if that line was empty string then it will been eaten and we need to put it back (whitespace string will have been handled correctly)
            lines.insert(bound_ln, bistr(''))

            root._offset(bound_ln, 0, 1, 0)


def _put_slice_generators(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """This handles `ListComp`, `SetComp`, `DictComp`, `GeneratorExp` and the `_comprehensions` SPECIAL SLICE."""

    ast = self.a
    body = ast.generators
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice__comprehensions(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

        if not isinstance(ast, _comprehensions):
            if len_slice == len_body and get_option_overridable('norm', 'norm_self', options):
                raise ValueError(f'cannot delete all {ast.__class__.__name__}.generators without norm_self=False')

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_generators(self)

    if not fst_:
        fst_body = None

        put_slice_nosep(self, start, stop, None, None, None,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'generators')

    else:
        fst_body = fst_.a.generators

        put_slice_nosep(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'generators')

    _put_slice_asts(self, start, stop, 'generators', body, fst_, fst_body)


def _put_slice_comprehension_ifs(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """This handles `comprehension` and the `_comprehension_ifs` SPECIAL SLICE."""

    ast = self.a
    body = ast.ifs
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice__comprehensions_ifs(self, code, one, options)

    if not fst_ and not len_slice:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = _bounds_comprehension_ifs(self)

    locfunc = lambda body, idx: body[idx].f.parent._loc_comprehension_if(idx)

    if isinstance(ast, comprehension):
        _, _, bound_ln, bound_col = ast.iter.f.pars()

    if not fst_:
        put_slice_nosep(self, start, stop, None, None, None,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'ifs', locfunc)

        _put_slice_asts(self, start, stop, 'ifs', body, None, None)

    else:
        fst_body = fst_.a.ifs
        is_last = stop == len_body

        put_slice_nosep(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'ifs', locfunc)

        _put_slice_asts(self, start, stop, 'ifs', body, fst_, fst_body)

        if is_last and (parent := self.parent):  # if put last `if` then need to check if joined alnums with potential following `comprehension`
            parent_body = parent.a.generators  # parent will be of the standard comprehensions (`ListComp`, etc...) or `_comprehensions`, standalone `comprehension` and `_comprehension_ifs` don't have a following `comprehension` to check against
            next_idx = self.pfield.idx + 1

            if next_idx < len(parent_body):  # only if self was not last comprehension in list
                ln, col, _, _ = parent_body[next_idx].f.loc

                self._maybe_fix_joined_alnum(ln, col)


def _put_slice_BoolOp_values(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.values
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    is_first = not start
    is_last = stop == len_body
    is_ins = not len_slice if len_body else False  # put to empty body is not considereed insert but replace for the purposes of dangling operators, could still be delete if code is None or empty BoolOp so is_del after code_to overrides this
    norm_self = get_option_overridable('norm', 'norm_self', options)

    fst_, op_side_left = (
        _code_to_slice_BoolOp_values_maybe_dangling(self, code, one, options, is_first, is_last, is_ins))

    is_del = not fst_

    if is_del:
        if not len_slice:
            return

        if len_slice == len_body and norm_self:
            raise ValueError("cannot delete all BoolOp.values without 'norm_self=False'")

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    locfunc = None

    if op_side_left is not None:  # if no dangling operator then location function is just normal location
        ast_dangling = None

        if op_side_left:  # dangling left operator, include it in first element location
            if start < len_body:  # could be insert past body
                ast_dangling = body[start]
                ln, col, _, _ = self._loc_BoolOp_op(start - 1)
                _, _, end_ln, end_col = ast_dangling.f.pars()

        else:  # op_side_left is False, dangling right operator, include it in last element location
            if stop:  # insert at 0 doesn't replace any operator
                ast_dangling = body[stop - 1]
                _, _, end_ln, end_col = self._loc_BoolOp_op(stop - 1)
                ln, col, _, _ = ast_dangling.f.pars()

        if ast_dangling:
            loc_first = fstloc(ln, col, end_ln, end_col)

            locfunc = lambda body, idx: loc_first if (a := body[idx]) is ast_dangling else a.f.pars()

    if is_del:
        fst_body = None

        put_slice_nosep(self, start, stop, None, None, None,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'values', locfunc)

    else:
        fst_body = fst_.a.values

        put_slice_nosep(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'values', locfunc)

    _put_slice_asts(self, start, stop, 'values', body, fst_, fst_body)

    _maybe_fix_BoolOp(self, start, is_del, is_last, options, norm_self)


def _put_slice_Compare__all(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """In order to carry out this operation over all the operands we temporarily add `left` to `comparators` to make
    that a contiguous list of everything since source-wise it already is. When deleting we also need to delete an extra
    operator, which defaults to the one on the left side of the comparators being deleted but can be overridden with
    `op_side='right'` (which is treated as a hint so if not possible no error is raised and other one is deleted). When
    inserting an `op_side` also determines which side of an operator the new slice is inserted. When replacing it is
    optional whether to replace a side operator or not (determined by if source with that dangling operator is passed in
    or not).
    """

    ast = self.a
    body = ast.comparators
    len_body = len(body) + 1  # +1 to include `left` element
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    is_first = not start
    is_last = stop == len_body
    is_ins = not len_slice if len_body else False  # put to empty body is not considereed insert but replace for the purposes of dangling operators, could still be delete if code is None or empty BoolOp so is_del after code_to overrides this

    fst_, op_side_left = (
        _code_to_slice_Compare__all_maybe_dangling(self, code, one, options, is_first, is_last, is_ins))

    is_del = not fst_

    if is_del:
        if not len_slice:
            return

        if len_slice == len_body:
            raise ValueError('cannot delete all Compare elements')

    elif op_side_left is not True:  # if op_side_left is True then all operands already in comparators and left is already a placeholder
        _move_Compare_left_into_comparators(fst_)

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    _move_Compare_left_into_comparators(self)  # we put everything into `comparators` for the sake of sanity (relatively speaking)

    if op_side_left is None:  # if no operator side then location function is just normal location
        locfunc = None

    elif op_side_left:
        def locfunc(body: list[AST], idx: int) -> fstloc:
            f = body[idx].f
            _, _, end_ln, end_col = f.pars()
            ln, col, _, _ = f.parent.a.ops[idx].f.loc  # comparator always has an operator on thje left

            return fstloc(ln, col, end_ln, end_col)

    else:  # op_side_left is False
        def locfunc(body: list[AST], idx: int) -> fstloc:
            f = body[idx].f
            ln, col, end_ln, end_col = f.pars()

            if (i := idx + 1) < len(body):  # comparator doesn't always have an opertator on the right
                _, _, end_ln, end_col = f.parent.a.ops[i].f.loc

            return fstloc(ln, col, end_ln, end_col)

    ops = ast.ops

    if is_del:
        fst_body = None
        start_old_right = start

        put_slice_nosep(self, start, stop, None, None, None,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'comparators', locfunc)

        # slice_ops = slice(start + (op_off := op_side_left is False), stop + op_off)
        slice_ops = slice(start + (not op_side_left), stop + (not op_side_left))  # op_side_left is never None here

        self._unmake_fst_tree(body[start : stop] + ops[slice_ops])

        del body[start : stop]
        del ops[slice_ops]

    else:
        ast_ = fst_.a
        fst_body = ast_.comparators
        fst_ops = ast_.ops

        put_slice_nosep(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f,
                        bound_ln, bound_col, bound_end_ln, bound_end_col,
                        options, 'comparators', locfunc)

        len_fst = len(fst_body)

        if op_side_left:
            ssbody = slice(start, stop)
            ssops = ssbody
            fsbody = slice(0, len_fst)
            fsops = fsbody

        elif op_side_left is False:
            ssbody = slice(start, stop)
            ssops = slice(start + 1, stop + 1)
            fsbody = slice(0, len_fst - 1)
            fsops = slice(1, len_fst)

        else:  # op_side_left is None
            ssbody = slice(start, stop)
            ssops = slice(start + 1, stop)
            fsbody = slice(0, len_fst)
            fsops = slice(1, len_fst)

        self._unmake_fst_tree(body[ssbody] + ops[ssops])

        body[ssbody] = fst_body[fsbody]
        ops[ssops] = fst_ops[fsops]

        del fst_body[fsbody]
        del fst_ops[fsops]

        fst_._unmake_fst_tree()  # be nice and clean up after ourselves

        FST = fst.FST
        new_fsts_body = [FST(body[i], self, astfield('comparators', i))
                         for i in range(ssbody.start, ssbody.start + fsbody.stop)]  # no - fsbody.start because it is always 0
        new_fsts_ops = [FST(ops[i], self, astfield('ops', i))
                        for i in range(ssops.start, ssops.start + fsops.stop - fsops.start)]

        self._make_fst_tree(new_fsts_body + new_fsts_ops)

        start_old_right = start + fsbody.stop  # because of extra comparator which is not copied in the case of op_side_left=False

    for i in range(start_old_right, len(body)):  # for fix before restoring to normal Compare structure
        body[i].f.pfield = astfield('comparators', i)
        ops[i].f.pfield = astfield('ops', i)

    _maybe_fix_Compare(self, start, is_del, is_last, options, get_option_overridable('norm', 'norm_self', options))


def _put_slice_Call_args(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.args
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)

    fst_ = _code_to_slice__expr_arglikes(self, code, one, options)

    if not fst_ and start == stop:
        return

    _validate_put_seq(self, fst_, 'Call.args')

    if keywords := ast.keywords:
        if body and keywords[0].f.loc[:2] < body[stop - 1].f.loc[2:] and stop:
            raise NodeError('cannot get this Call.args slice because it includes parts after a keyword')

    else:
        if body and (f0 := body[0].f)._is_solo_call_arg_genexp() and f0.pars(shared=False).n == -1:  # single call argument GeneratorExp shares parentheses with Call?
            f0._parenthesize_grouping()

    bound_ln, bound_col, bound_end_ln, bound_end_col = self._loc_Call_pars()
    bound_col += 1
    bound_end_col -= 1

    self_tail_sep = ((fst_ or start) and keywords and stop == len_body) or None

    _put_slice_seq_and_asts(self, start, stop, 'args', body, fst_, 'elts', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', self_tail_sep, options)

    if self_tail_sep:  # if there are keywords and we removed tail element we make sure there is a space between comma of the new last element and first keyword
        self._maybe_ins_separator(*(f := body[-1].f).loc[2:], True, exclude=f)  # this will only maybe add a space, comma is already there


def _put_slice_MatchSequence_patterns(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    # NOTE: we allow multiple MatchStars to be put to the same MatchSequence
    body = self.a.patterns
    start, stop = fixup_slice_indices(len(body), start, stop)

    fst_ = _code_to_slice_MatchSequence(self, code, one, options)

    if not fst_ and start == stop:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if delims := self._is_delimited_matchseq():
        bound_col += 1
        bound_end_col -= 1

    _put_slice_seq_and_asts(self, start, stop, 'patterns', body, fst_, 'patterns', None,
                            bound_ln, bound_col, bound_end_ln, bound_end_col, ',', 0, options)

    _maybe_fix_MatchSequence(self, delims)


def _put_slice_MatchMapping__all(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    ast = self.a
    body = ast.keys
    body2 = ast.patterns
    rest = ast.rest
    len_body = len(body)
    len_body_w_rest = len_body + bool(rest)
    start, stop = fixup_slice_indices(len_body_w_rest, start, stop)

    fst_ = _code_to_slice_key_and_other(self, code, one, options, code_as_pattern)

    if not fst_:
        if start == stop:  # delete empty slice
            return

        fst_rest = None

    else:
        if rest and start >= len_body_w_rest:
            raise ValueError("cannot put slice to MatchMapping after 'rest' element")

        ast_ = fst_.a

        if fst_rest := ast_.rest:
            if stop < len_body_w_rest:
                raise ValueError("put slice with 'rest' element to MatchMapping must be at end")

            _add_MatchMapping_rest_as_real_node(fst_)  # this needs to be done before the _trim_delimiters()

        fst_._trim_delimiters()  # didn't do it in _code_to_slice_key_and_other()

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    bound_col += 1
    bound_end_col -= 1

    if with_rest := (fst_rest or (rest and stop == len_body_w_rest)):  # either self or fst_ has a `rest` included in the put
        self_tail_sep = None

        if rest:
            _add_MatchMapping_rest_as_real_node(self)

    elif not fst_:  # no `rest` involved in put, these are sneaky hacks to get out of having to add it in self as a temporary element (which would be needed for correct separator handling at tail of put)
        self_tail_sep = (start and ast.rest and stop == len_body) or None
    else:
        self_tail_sep = (ast.rest and stop == len_body) or None

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                            bound_ln, bound_col, bound_end_ln, bound_end_col,
                                            options, 'keys', 'patterns', ',', self_tail_sep)

        _put_slice_asts2(self, start, stop, 'patterns', body, body2, None, None, None)

    else:
        fst_body = ast_.keys
        fst_body2 = ast_.patterns
        fst_first = a.f if (a := fst_body[0]) else None  # could be the temporary `rest` key of None

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_first, fst_body2[-1].f, len(fst_body),
                                            bound_ln, bound_col, bound_end_ln, bound_end_col,
                                            options, 'keys', 'patterns', ',', self_tail_sep)

        _put_slice_asts2(self, start, stop, 'patterns', body, body2, fst_, fst_body, fst_body2)

    put_slice_sep_end(self, end_params)

    if with_rest:
        if stop == len_body_w_rest:  # if this and we are here then `rest` (and the temporary node) was either deleted or replaced from slice, because otherwise we wouldn't be here
            ast.rest = fst_rest

            if fst_rest:  # if no fst_rest then our rest was deleted or overwritten with real node, otherwise need to remove temporary node from put FST
                _remove_MatchMapping_rest_real_node(self)

    else:
        if self_tail_sep:  # if there is a **rest and we removed tail element so here we make sure there is a space between comma of the new last element and the **rest
            self._maybe_ins_separator(*body2[-1].f.loc[2:], True)  # this will only maybe add a space, comma is already there


def _put_slice_MatchOr_patterns(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    body = self.a.patterns
    len_body = len(body)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start
    self_norm = _get_option_norm('norm_self', 'matchor_norm', options)

    fst_ = _code_to_slice_MatchOr(self, code, one, options)

    if not fst_:
        if not len_slice:
            return

        if not (len_left := len_body - len_slice):
            if self_norm:
                raise ValueError("cannot delete all MatchOr.patterns without norm_self=False")

        elif len_left == 1 and self_norm == 'strict':
            raise ValueError("cannot del MatchOr to length 1 with matchor_norm='strict'")

        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0, *self.loc,
                                         options, 'patterns', None, '|', False)

        _put_slice_asts(self, start, stop, 'patterns', body, None, None)

    else:
        fst_body = fst_.a.patterns
        len_fst_body = len(fst_body)

        if (len_body - len_slice + len_fst_body) == 1 and self_norm == 'strict':
            raise NodeError("cannot put MatchOr to length 1 with matchor_norm='strict'")

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                         *self.loc, options, 'patterns', None, '|', False)

        _put_slice_asts(self, start, stop, 'patterns', body, fst_, fst_body)

    put_slice_sep_end(self, end_params)

    _maybe_fix_MatchOr(self, self_norm)


def _put_slice_type_params(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    """An empty `Tuple` is accepted as a zero-element `type_params` slice."""

    len_body = len(body := (ast := self.a).type_params)
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = _code_to_slice__type_params(self, code, one, options)

    bound, (name_ln, name_col) = (
        (fst.FST._loc_TypeAlias_type_params_brackets if isinstance(ast, TypeAlias) else
         fst.FST._loc_ClassDef_type_params_brackets if isinstance(ast, ClassDef) else
         fst.FST._loc_FunctionDef_type_params_brackets)  # FunctionDef, AsyncFunctionDef
    )(self)

    if bound:
        bound_ln, bound_col, bound_end_ln, bound_end_col = bound

    if not fst_:
        if not len_slice:
            return

        if len_slice == len_body:  # deleting everything so remove brackets
            self._put_src(None, name_ln, name_col, bound_end_ln, bound_end_col, False)

            end_params = None

        else:
            end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                             bound_ln, bound_col + 1, bound_end_ln, bound_end_col - 1,
                                             options, 'type_params')

        _put_slice_asts(self, start, stop, 'type_params', body, None, None)

    else:
        if not body:  # brackets don't exist, add them first
            self._put_src('[]', name_ln, name_col, name_ln, name_col, False)

            bound_ln = bound_end_ln = name_ln
            bound_col = bound_end_col = name_col + 1

        fst_body = fst_.a.type_params

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len(fst_body),
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, 'type_params')

        _put_slice_asts(self, start, stop, 'type_params', body, fst_, fst_body)

    if end_params:
        put_slice_sep_end(self, end_params)


def _put_slice__slice(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> None:
    static = _SPECIAL_SLICE_STATICS[(ast := self.a).__class__]
    len_body = len(body := getattr(ast, field))
    start, stop = fixup_slice_indices(len_body, start, stop)
    len_slice = stop - start

    fst_ = static.code_to(self, code, one, options)

    if not fst_ and not len_slice:
        return

    bound_ln, bound_col, bound_end_ln, bound_end_col = self.loc

    if not fst_:
        end_params = put_slice_sep_begin(self, start, stop, None, None, None, 0,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, field, None, static.sep, static.self_tail_sep)

        self._unmake_fst_tree(body[start : stop])

        del body[start : stop]

        len_fst_body = 0

    else:
        fst_body = getattr(fst_.a, field)
        len_fst_body = len(fst_body)

        end_params = put_slice_sep_begin(self, start, stop, fst_, fst_body[0].f, fst_body[-1].f, len_fst_body,
                                         bound_ln, bound_col, bound_end_ln, bound_end_col,
                                         options, field, None, static.sep, static.self_tail_sep)

        self._unmake_fst_tree(body[start : stop])
        fst_._unmake_fst_parents(True)

        body[start : stop] = fst_body

        FST = fst.FST
        stack = [FST(body[i], self, astfield(field, i)) for i in range(start, start + len_fst_body)]

        self._make_fst_tree(stack)

    for i in range(start + len_fst_body, len(body)):
        body[i].f.pfield = astfield(field, i)

    put_slice_sep_end(self, end_params)


_PUT_SLICE_HANDLERS = {
    (Module, 'body'):                         put_slice_stmtish,  # stmt*
    (Interactive, 'body'):                    put_slice_stmtish,  # stmt*
    (FunctionDef, 'body'):                    put_slice_stmtish,  # stmt*
    (AsyncFunctionDef, 'body'):               put_slice_stmtish,  # stmt*
    (ClassDef, 'body'):                       put_slice_stmtish,  # stmt*
    (For, 'body'):                            put_slice_stmtish,  # stmt*
    (For, 'orelse'):                          put_slice_stmtish,  # stmt*
    (AsyncFor, 'body'):                       put_slice_stmtish,  # stmt*
    (AsyncFor, 'orelse'):                     put_slice_stmtish,  # stmt*
    (While, 'body'):                          put_slice_stmtish,  # stmt*
    (While, 'orelse'):                        put_slice_stmtish,  # stmt*
    (If, 'body'):                             put_slice_stmtish,  # stmt*
    (If, 'orelse'):                           put_slice_stmtish,  # stmt*
    (With, 'body'):                           put_slice_stmtish,  # stmt*
    (AsyncWith, 'body'):                      put_slice_stmtish,  # stmt*
    (Try, 'body'):                            put_slice_stmtish,  # stmt*
    (Try, 'orelse'):                          put_slice_stmtish,  # stmt*
    (Try, 'finalbody'):                       put_slice_stmtish,  # stmt*
    (TryStar, 'body'):                        put_slice_stmtish,  # stmt*
    (TryStar, 'orelse'):                      put_slice_stmtish,  # stmt*
    (TryStar, 'finalbody'):                   put_slice_stmtish,  # stmt*
    (ExceptHandler, 'body'):                  put_slice_stmtish,  # stmt*
    (match_case, 'body'):                     put_slice_stmtish,  # stmt*

    (Match, 'cases'):                         put_slice_stmtish,  # match_case*
    (Try, 'handlers'):                        put_slice_stmtish,  # excepthandler*
    (TryStar, 'handlers'):                    put_slice_stmtish,  # excepthandlerstar*

    (Tuple, 'elts'):                          _put_slice_Tuple_elts,  # expr*
    (List, 'elts'):                           _put_slice_List_elts,  # expr*
    (Set, 'elts'):                            _put_slice_Set_elts,  # expr*

    (Dict, '_all'):                           _put_slice_Dict__all,  # key:value*

    (FunctionDef, 'decorator_list'):          _put_slice_decorator_list,  # expr*
    (AsyncFunctionDef, 'decorator_list'):     _put_slice_decorator_list,  # expr*
    (ClassDef, 'decorator_list'):             _put_slice_decorator_list,  # expr*
    (ClassDef, 'bases'):                      _put_slice_ClassDef_bases,  # expr*
    (Delete, 'targets'):                      _put_slice_Delete_targets,  # expr*
    (Assign, 'targets'):                      _put_slice_Assign_targets,  # expr*
    (BoolOp, 'values'):                       _put_slice_BoolOp_values,  # expr*
    (Compare, '_all'):                        _put_slice_Compare__all,  # expr*
    (Call, 'args'):                           _put_slice_Call_args,  # expr*
    (comprehension, 'ifs'):                   _put_slice_comprehension_ifs,  # expr*

    (ListComp, 'generators'):                 _put_slice_generators,  # comprehension*
    (SetComp, 'generators'):                  _put_slice_generators,  # comprehension*
    (DictComp, 'generators'):                 _put_slice_generators,  # comprehension*
    (GeneratorExp, 'generators'):             _put_slice_generators,  # comprehension*

    (ClassDef, 'keywords'):                   _put_slice_NOT_IMPLEMENTED_YET,  # keyword*
    (Call, 'keywords'):                       _put_slice_NOT_IMPLEMENTED_YET,  # keyword*

    (Import, 'names'):                        _put_slice_Import_names,  # alias*
    (ImportFrom, 'names'):                    _put_slice_ImportFrom_names,  # alias*

    (With, 'items'):                          _put_slice_With_AsyncWith_items,  # withitem*
    (AsyncWith, 'items'):                     _put_slice_With_AsyncWith_items,  # withitem*

    (MatchSequence, 'patterns'):              _put_slice_MatchSequence_patterns,  # pattern*
    (MatchMapping, '_all'):                   _put_slice_MatchMapping__all,  # key:pattern*
    (MatchClass, 'patterns'):                 _put_slice_NOT_IMPLEMENTED_YET,  # pattern*
    (MatchOr, 'patterns'):                    _put_slice_MatchOr_patterns,  # pattern*

    (FunctionDef, 'type_params'):             _put_slice_type_params,  # type_param*
    (AsyncFunctionDef, 'type_params'):        _put_slice_type_params,  # type_param*
    (ClassDef, 'type_params'):                _put_slice_type_params,  # type_param*
    (TypeAlias, 'type_params'):               _put_slice_type_params,  # type_param*

    (Global, 'names'):                        _put_slice_Global_Nonlocal_names,  # identifier*
    (Nonlocal, 'names'):                      _put_slice_Global_Nonlocal_names,  # identifier*

    (JoinedStr, 'values'):                    _put_slice_NOT_IMPLEMENTED_YET,  # expr*
    (TemplateStr, 'values'):                  _put_slice_NOT_IMPLEMENTED_YET,  # expr*

    (_ExceptHandlers, 'handlers'):            put_slice_stmtish,  # ExceptHandler*
    (_match_cases, 'cases'):                  put_slice_stmtish,  # match_case*
    (_Assign_targets, 'targets'):             _put_slice__slice,  # expr*
    (_decorator_list, 'decorator_list'):      _put_slice_decorator_list,  # expr*
    (_comprehensions, 'generators'):          _put_slice_generators,  # comprehensions*
    (_comprehension_ifs, 'ifs'):              _put_slice_comprehension_ifs,  # exprs*
    (_aliases, 'names'):                      _put_slice__slice,  # alias*
    (_withitems, 'items'):                    _put_slice__slice,  # withitem*
    (_type_params, 'type_params'):            _put_slice__slice,  # type_param*
}


# ----------------------------------------------------------------------------------------------------------------------
# put raw

def _fixup_slice_index_for_raw(len_: int, start: int, stop: int) -> tuple[int, int]:
    start, stop = fixup_slice_indices(len_, start, stop)

    if start == stop:
        raise ValueError('cannot insert in raw slice put')

    return start, stop


def _loc_slice_raw_put_decorator_list(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    decorator_list = self.a.decorator_list
    start, stop = _fixup_slice_index_for_raw(len(decorator_list), start, stop)
    ln, col, _, _ = self._loc_decorator(start, False)
    _, _, end_ln, end_col = decorator_list[stop - 1].f.pars()

    return ln, col, end_ln, end_col, start, stop, decorator_list

def _loc_slice_raw_put_Global_Nonlocal_names(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    names = self.a.names
    start, stop = _fixup_slice_index_for_raw(len(names), start, stop)
    (ln, col, _, _), (_, _, end_ln, end_col) = self._loc_Global_Nonlocal_names(start, stop - 1)

    return ln, col, end_ln, end_col, start, stop, names

def _loc_slice_raw_put_Dict__all(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    values = self.a.values
    start, stop = _fixup_slice_index_for_raw(len(values), start, stop)
    ln, col, _, _ = self._loc_maybe_key(start)
    _, _, end_ln, end_col = values[stop - 1].f.pars()

    return ln, col, end_ln, end_col, start, stop, values

def _loc_slice_raw_put_Compare__all(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    ast = self.a
    comparators = ast.comparators
    start, stop = _fixup_slice_index_for_raw(len(comparators) + 1, start, stop)
    ln, col, end_ln, end_col = (comparators[start - 1] if start else ast.left).f.pars()

    if stop != start + 1:
        _, _, end_ln, end_col = comparators[stop - 2].f.pars()

    return ln, col, end_ln, end_col, start, stop, comparators

def _loc_slice_raw_put_comprehension_ifs(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    ifs = self.a.ifs
    start, stop = _fixup_slice_index_for_raw(len(ifs), start, stop)
    start_eq_stop = start == stop

    ln, col, end_ln, end_col = self._loc_comprehension_if(start, start_eq_stop)  # if start != stop then we don't need pars here because we will only use the start which will be the `if`

    if not start_eq_stop:
        _, _, end_ln, end_col = ifs[stop - 1].f.pars()

    return ln, col, end_ln, end_col, start, stop, ifs

def _loc_slice_raw_put_MatchMapping__all(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    ast = self.a
    keys = ast.keys
    patterns = ast.patterns
    rest = ast.rest
    len_keys = len(keys)
    len_keys_w_rest = len_keys + bool(rest)
    start, stop = _fixup_slice_index_for_raw(len_keys_w_rest, start, stop)

    if rest and stop == len_keys_w_rest:
        ln, col, end_ln, end_col = self._loc_MatchMapping_rest()
    else:
        _, _, end_ln, end_col = patterns[stop - 1].f.pars()

    if start < len_keys:
        ln, col, _, _ = keys[start].f.loc  # these cannot have pars

    else:  # in this case _loc_MatchMapping_rest() was gotten so (ln, col) is at the start of the `rest` identifier
        if start:
            _, _, prev_ln, prev_col = patterns[start - 1].f.loc
        else:
            prev_ln, prev_col, _, _ = self.loc

        ln, col = prev_find(self.root._lines, prev_ln, prev_col, ln, col, '**')  # '**' must be there

    return ln, col, end_ln, end_col, start, stop, patterns

def _loc_slice_raw_put_default(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    body = getattr(self.a, field, None)

    if body is None or not isinstance(body, list):
        raise ValueError(f'cannot put raw slice to {self.a.__class__.__name__}.{field}')

    start, stop = _fixup_slice_index_for_raw(len(body), start, stop)
    ln, col, _, _ = body[start].f.pars(shared=False)
    _, _, end_ln, end_col = body[stop - 1].f.pars(shared=False)

    return ln, col, end_ln, end_col, start, stop, body

def _loc_slice_raw_put(
    self: fst.FST, start: int | Literal['end'] | None, stop: int | None, field: str
) -> tuple[int, int, int, int, int, int, list[AST]]:
    """Get location of a raw slice. Sepcial cases for decorators, comprehension ifs and other nodes."""

    return _LOC_SLICE_RAW_PUT_FUNCS.get((self.a.__class__, field), _loc_slice_raw_put_default)(self, start, stop, field)

_LOC_SLICE_RAW_PUT_FUNCS = {
    (FunctionDef, 'decorator_list'):      _loc_slice_raw_put_decorator_list,
    (AsyncFunctionDef, 'decorator_list'): _loc_slice_raw_put_decorator_list,
    (ClassDef, 'decorator_list'):         _loc_slice_raw_put_decorator_list,
    (Global, 'names'):                    _loc_slice_raw_put_Global_Nonlocal_names,
    (Nonlocal, 'names'):                  _loc_slice_raw_put_Global_Nonlocal_names,
    (Dict, '_all'):                       _loc_slice_raw_put_Dict__all,
    (Compare, '_all'):                    _loc_slice_raw_put_Compare__all,
    (comprehension, 'ifs'):               _loc_slice_raw_put_comprehension_ifs,
    (MatchMapping, '_all'):               _loc_slice_raw_put_MatchMapping__all,
}


def _singleton_needs_comma(fst_: fst.FST) -> bool:
    """Whether a singleton value in this container needs a trailing comma or not."""

    return (isinstance(a := fst_.a, Tuple) or
            (isinstance(a, MatchSequence) and not fst_._is_delimited_seq('patterns', '[]')))  # MatchSequence because it can be undelimited or delimited with parentheses and in that case a singleton needs a trailing comma


def _adjust_slice_raw_ast(
    self: fst.FST,
    code: AST,
    field: str,
    one: bool,
    options: Mapping[str, Any],
    put_ln: int,
    put_col: int,
    put_end_ln: int,
    put_end_col: int,
    start: int,
    stop: int,
    body2: list[AST],
) -> tuple[AST | list[str], int, int, int, int]:
    """Adjust `code` and put location when putting raw from an `AST`. Currently just trailing comma stuff."""

    code = reduce_ast(code, True)

    if ((code_is_tuple := isinstance(code, Tuple))
        or (code_is_normal := isinstance(code, (List, Set, Dict, MatchSequence, MatchMapping)))
        or isinstance(code, (_withitems, _aliases, _type_params))
    ):  # all nodes which are separated by comma at top level
        src = unparse(code)

        if not one:  # strip delimiters and remove singleton Tuple trailing comma if present
            if code_is_tuple:
                src = src[1 : (-2 if len(code.elts) == 1 else -1)]

                len_code_body = len(getattr(code, 'elts', ()))

            elif code_is_normal:
                src = src[1 : -1]

                len_code_body = len(getattr(code, 'elts', ()) or getattr(code, 'keys', ()) or
                                    getattr(code, 'patterns', ()))

            else:
                len_code_body = len(getattr(code, 'items', ()) or getattr(code, 'names', ()) or
                                    getattr(code, 'type_params', ()))

            if not len_code_body:
                raise NodeError('cannot put raw empty slice')

        elif not code_is_tuple and not code_is_normal:
            raise NodeError('cannot put special slice as one')
        else:
            len_code_body = 1

        if stop == len(body2) and _singleton_needs_comma(self):
            comma = next_find(self.root._lines, put_end_ln, put_end_col, self.end_ln, self.end_col, ',', True)  # trailing comma

            if len_code_body != 1:
                if comma and comma[1] == put_end_col and comma[0] == put_end_ln:
                    put_end_col += 1  # overwrite trailing singleton tuple comma which follows immediately after single element

            elif not start and not comma:
                src += ','  # add trailing comma to what will be singleton tuple

        code = src

    return code, put_ln, put_col, put_end_ln, put_end_col


def _adjust_slice_raw_fst(
    self: fst.FST,
    code: fst.FST,
    field: str,
    one: bool,
    options: Mapping[str, Any],
    put_ln: int,
    put_col: int,
    put_end_ln: int,
    put_end_col: int,
    start: int,
    stop: int,
    body2: list[AST],
) -> tuple[fst.FST | list[str], int, int, int, int]:
    """Adjust `code` and put location when putting raw from an `FST`."""

    if not code.is_root:
        raise ValueError('expecting root node')

    code_ast = reduce_ast(code.a, True)

    if ((code_is_normal := isinstance(code_ast, (Tuple, List, Set, Dict, MatchSequence, MatchMapping)))
        or isinstance(code_ast, (_withitems, _aliases, _type_params))
    ):  # all nodes which are separated by comma at top level
        code_fst = code_ast.f
        code_lines = code._lines

        if not one:  # strip delimiters (if any) and everything before and after actual node
            ln, col, end_ln, end_col = code_fst.loc

            if (code_is_normal
                and not (
                    code_fst._is_parenthesized_tuple() is False
                    or code_fst._is_delimited_matchseq() == ''  # don't strip nonexistent delimiters if is unparenthesized Tuple or MatchSequence or is a special slice
            )):
                col += 1
                end_col -= 1
                col_offset = code_ast.col_offset = code_ast.col_offset + 1
                end_col_offset = code_ast.end_col_offset = code_ast.end_col_offset - 1

                if parent := code_fst.parent:  # this will be an `Expr` if present
                    parenta = parent.a
                    parenta.col_offset = col_offset
                    parenta.end_col_offset = end_col_offset

                    assert isinstance(parenta, Expr)

            code._put_src(None, end_ln, end_col, len(code_lines) - 1, len(code_lines[-1]))
            code._put_src(None, 0, 0, ln, col, False)  # we are counting on this to _touch() everything because of possible assignments above to col_offset and end_col_offset

            if code_is_normal:
                code_body2 = (getattr(code_ast, 'elts', ()) or getattr(code_ast, 'values', ()) or
                              getattr(code_ast, 'patterns', ()))
            else:
                code_body2 = (getattr(code_ast, 'items', ()) or getattr(code_ast, 'names', ()) or
                              getattr(code_ast, 'type_params', ()))

            if not (len_code_body2 := len(code_body2)):
                raise NodeError('cannot put raw empty slice')

            _, _, end_ln, end_col = code_body2[-1].f.pars()

            code_comma = next_find(code_lines, end_ln, end_col, code_fst.end_ln, code_fst.end_col, ',', True)  # trailing comma

            code_comma_is_explicit = code_comma and (  # explicit comma - not needed or not in normal position
                (len_code_body2 >= 2) or
                code_comma[1] != end_col or code_comma[0] != end_ln or
                not _singleton_needs_comma(code_fst)
            )

        elif not code_is_normal:
            raise NodeError('cannot put special slice as one')

        else:
            if code_fst._is_parenthesized_tuple() is False:  # only Tuple or MatchMapping could be naked and needs to be delimited, everything else stays as-is
                code_fst._delimit_node()
            elif code_fst._is_delimited_matchseq() == '':
                code_fst._delimit_node(delims='[]')

            code_body2 = [code_ast]
            code_comma = code_comma_is_explicit = None
            len_code_body2 = 1

        if comma := next_find(self.root._lines, put_end_ln, put_end_col, self.end_ln, self.end_col, ',', True):  # trailing comma
            if (code_comma_is_explicit
                or (
                    len_code_body2 > 1  # code has no comma because otherwise it would be explicit
                    and len(body2) == 1
                    and _singleton_needs_comma(self)  # self is singleton and singleton needs comma
                    and comma[1] == put_end_col
                    and comma[0] == put_end_ln  # that comma follows right after element and so is not explicit and can be deleted
            )):
                put_end_ln, put_end_col = comma
                put_end_col += 1

            elif code_comma:  # otherwise if code has comma we remove it and keep the comma that is already in self
                ln, col = code_comma

                code._put_src(None, ln, col, ln, col + 1, True)

        elif code_comma_is_explicit:
            pass  # noop

        elif not start and stop == len(body2) and len_code_body2 == 1 and _singleton_needs_comma(self):  # will result in singleton which needs trailing comma
            if not code_comma:
                code_lines[-1] = bistr(code_lines[-1] + ',')

        elif code_comma:
            ln, col = code_comma

            code._put_src(None, ln, col, ln, col + 1, True)

    return code, put_ln, put_col, put_end_ln, put_end_col


def _put_slice_raw(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool,
    options: Mapping[str, Any],
) -> fst.FST | None:  # -> self or reparsed self or None if deleted
    """Put a raw slice to `self`. Currently just trailing comma stuff."""

    if code is None:
        raise ValueError('cannot delete in raw slice put')

    put_ln, put_col, put_end_ln, put_end_col, start, stop, body2 = _loc_slice_raw_put(self, start, stop, field)

    if isinstance(code, AST):
        code, put_ln, put_col, put_end_ln, put_end_col = (
            _adjust_slice_raw_ast(self, code, field, one, options,
                                  put_ln, put_col, put_end_ln, put_end_col, start, stop, body2))

    elif isinstance(code, fst.FST):
        code, put_ln, put_col, put_end_ln, put_end_col = (
            _adjust_slice_raw_fst(self, code, field, one, options,
                                  put_ln, put_col, put_end_ln, put_end_col, start, stop, body2))

    self._reparse_raw(code, put_ln, put_col, put_end_ln, put_end_col)

    return self if self.a else self.repath()


# ----------------------------------------------------------------------------------------------------------------------
# FST class methods

def _put_slice(
    self: fst.FST,
    code: Code | None,
    start: int | Literal['end'] | None,
    stop: int | None,
    field: str,
    one: bool = False,
    options: Mapping[str, Any] = {},
) -> fst.FST | None:  # -> self or reparsed self or None if disappeared due to raw
    """Put an a slice of child nodes to `self`."""

    if code is self.root:  # don't allow own root to be put to self
        raise ValueError('circular put detected')

    if options.get('to') is not None:
        raise ValueError("cannot put slice with 'to' option")

    raw = fst.FST.get_option('raw', options)
    nonraw_exc = None

    if raw is not True:
        try:
            if not (handler := _PUT_SLICE_HANDLERS.get((self.a.__class__, field))):  # allow raw to handle some non-contiguous list fields
                raise NodeError(f'cannot put slice to {self.a.__class__.__name__}.{field}', rawable=True)

            with self._modifying(field):
                handler(self, code, start, stop, field, one, options)

            return self

        except (NodeError, SyntaxError, NotImplementedError) as exc:  # SyntaxError includes ParseError
            if not raw or (isinstance(exc, NodeError) and not exc.rawable):
                raise

            nonraw_exc = exc

    with self._modifying(field, True):
        try:
            return _put_slice_raw(self, code, start, stop, field, one, options)

        except Exception as raw_exc:
            raw_exc.__context__ = nonraw_exc

            raise raw_exc
