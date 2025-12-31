from typing import Union

from . import fst

from .asttypes import (
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
    BitAnd,
    BitOr,
    BitXor,
    BoolOp,
    Break,
    Call,
    ClassDef,
    Compare,
    Constant,
    Continue,
    Del,
    Delete,
    Dict,
    DictComp,
    Div,
    Eq,
    ExceptHandler,
    Expr,
    Expression,
    FloorDiv,
    For,
    FormattedValue,
    FunctionDef,
    FunctionType,
    GeneratorExp,
    Global,
    Gt,
    GtE,
    If,
    IfExp,
    Import,
    ImportFrom,
    In,
    Interactive,
    Invert,
    Is,
    IsNot,
    JoinedStr,
    LShift,
    Lambda,
    List,
    ListComp,
    Load,
    Lt,
    LtE,
    MatMult,
    Match,
    MatchAs,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    MatchSingleton,
    MatchStar,
    MatchValue,
    Mod,
    Module,
    Mult,
    Name,
    NamedExpr,
    Nonlocal,
    Not,
    NotEq,
    NotIn,
    Or,
    Pass,
    Pow,
    RShift,
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
    TypeIgnore,
    UAdd,
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
    keyword,
    match_case,
    withitem,
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

__all__ = ['PREV_FUNCS']


_NextPrevRet = Union['fst.FST', None, tuple[str, int | None]]


def _prev_None(ast: AST, idx: int | None) -> _NextPrevRet:
      return None


def _prev_Module_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    return None


def _prev_Module_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    return None


def _prev_Interactive_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    return None


def _prev_Interactive_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    return None


def _prev_Expression_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.body.f


def _prev_FunctionType_END(ast: AST, idx: int | None) -> _NextPrevRet:  # pragma: no cover
    return ast.returns.f


def _prev_FunctionType_returns(ast: AST, idx: int | None) -> _NextPrevRet:  # pragma: no cover
    if a := ast.argtypes:
        return a[-1].f

    return None


def _prev_FunctionType_argtypes(ast: AST, idx: int | None) -> _NextPrevRet:  # pragma: no cover
    if (idx := idx - 1) >= 0:
        return  ast.argtypes[idx].f

    return None


def _prev_FunctionDef_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    if a := ast.returns:
        return a.f

    return ast.args.f


def _prev_FunctionDef_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    if a := ast.returns:
        return a.f

    return ast.args.f


def _prev_FunctionDef_returns(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.args.f


def _prev_FunctionDef_args(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[-1].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_FunctionDef_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:  # if we got into this function then the AST has this
        return  ast.type_params[idx].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_FunctionDef_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.decorator_list[idx].f

    return None


def _prev_ClassDef_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    if a := ast.keywords:
        kwn = a[-1]

        if (not (b := ast.bases)
            or (basen := b[-1]).__class__ is not Starred
            or (basen.lineno, basen.col_offset) < (kwn.lineno, kwn.col_offset)
        ):
            return kwn.f

        return basen.f

    if a := ast.bases:
        return a[-1].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[-1].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_ClassDef_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    if a := ast.keywords:
        kwn = a[-1]

        if (not (b := ast.bases)
            or (basen := b[-1]).__class__ is not Starred
            or (basen.lineno, basen.col_offset) < (kwn.lineno, kwn.col_offset)
        ):
            return kwn.f

        return basen.f

    if a := ast.bases:
        return a[-1].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[-1].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_ClassDef_keywords(ast: AST, idx: int | None) -> _NextPrevRet:
    kws = ast.keywords
    bases = ast.bases
    idx_ = idx - 1

    if not bases:
        if idx_ >= 0:
            return kws[idx_].f

    else:
        if (last_base := bases[-1]).__class__ is not Starred:  # if no Starred then can't be mixed with keywords, unchecked walk backward
            if idx_ >= 0:
                return kws[idx_].f

            return last_base.f

        last_base_pos = (last_base.lineno, last_base.col_offset)

        if idx_ < 0:
            if (kw_pos := ((kw := kws[0]).lineno, kw.col_offset)) > last_base_pos:
                return last_base.f

            for base in bases[-2::-1]:  # only need to find last base (if any) before first keyword
                if (base.lineno, base.col_offset) < kw_pos:
                    return base.f

        else:
            if (kw_pos := ((kw := kws[idx_]).lineno, kw.col_offset)) > last_base_pos:
                return kw.f

            if (kw_plus1_pos := ((kw_plus1 := kws[idx]).lineno, kw_plus1.col_offset)) > last_base_pos:
                return last_base.f

            for base in bases[-2::-1]:  # need to find last base (if any) between next and last keywords
                base_pos = (base.lineno, base.col_offset)

                if base_pos < kw_pos:
                    break
                if base_pos < kw_plus1_pos:
                    return base.f

            return kw.f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[-1].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_ClassDef_bases(ast: AST, idx: int | None) -> _NextPrevRet:
    bases = ast.bases
    kws = ast.keywords

    if (not kws
        or bases[-1].__class__ is not Starred  # if no kws or last base is not Starred then can't be mixed with keywords, unchecked walk backward
        or (base_pos := ((base := bases[idx]).lineno, base.col_offset))
            < (first_kw_pos := ((first_kw := kws[0]).lineno, first_kw.col_offset))  # this base before first keyword so all bases from here
    ):
        if (idx := idx - 1) >= 0:
            return bases[idx].f

        if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
            return a[-1].f

        if a := ast.decorator_list:
            return a[-1].f

        return None

    if not idx:  # no more bases, just find last kw before this base if any
        for kw in kws[1:]:  # from start likely shorter search, we already checked kws[0]
            if (kw.lineno, kw.col_offset) > base_pos:
                break

            first_kw = kw

        return first_kw.f

    prev_base = bases[idx - 1]
    prev_base_pos = (prev_base.lineno, prev_base.col_offset)

    for kw in kws[1:]:
        kw_pos = (kw.lineno, kw.col_offset)

        if kw_pos > base_pos:
            break

        first_kw = kw
        first_kw_pos = kw_pos

    return (prev_base if prev_base_pos > first_kw_pos else first_kw).f


def _prev_ClassDef_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:  # if we got into this function then the AST has this
        return  ast.type_params[idx].f

    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev_ClassDef_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.decorator_list[idx].f

    return None


def _prev_Return_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.value:
        return a.f

    return None


def _prev_Delete_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.targets:
        return a[-1].f

    return None


def _prev_Delete_targets(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.targets[idx].f

    return None


def _prev_Assign_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_Assign_value(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.targets:
        return a[-1].f

    return None


def _prev_Assign_targets(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.targets[idx].f

    return None


def _prev_TypeAlias_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_TypeAlias_value(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.type_params:
        return a[-1].f

    return ast.name.f


def _prev_TypeAlias_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.type_params[idx].f

    return ast.name.f


def _prev_AugAssign_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_AugAssign_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.op.f


def _prev_AugAssign_op(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _prev_AnnAssign_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.value:
        return a.f

    return ast.annotation.f


def _prev_AnnAssign_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.annotation.f


def _prev_AnnAssign_annotation(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _prev_For_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.orelse:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return ast.iter.f


def _prev_For_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.orelse[idx].f

    if a := ast.body:
        return a[-1].f

    return ast.iter.f


def _prev_For_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    return ast.iter.f


def _prev_For_iter(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _prev_AsyncFor_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.orelse:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return ast.iter.f


def _prev_AsyncFor_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.orelse[idx].f

    if a := ast.body:
        return a[-1].f

    return ast.iter.f


def _prev_AsyncFor_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    return ast.iter.f


def _prev_AsyncFor_iter(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _prev_While_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.orelse:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return ast.test.f


def _prev_While_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.orelse[idx].f

    if a := ast.body:
        return a[-1].f

    return ast.test.f


def _prev_While_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    return ast.test.f


def _prev_If_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.orelse:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return ast.test.f


def _prev_If_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.orelse[idx].f

    if a := ast.body:
        return a[-1].f

    return ast.test.f


def _prev_If_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    return ast.test.f


def _prev_With_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    if a := ast.items:
        return a[-1].f

    return None


def _prev_With_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    if a := ast.items:
        return a[-1].f

    return None


def _prev_With_items(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.items[idx].f

    return None


def _prev_AsyncWith_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    if a := ast.items:
        return a[-1].f

    return None


def _prev_AsyncWith_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    if a := ast.items:
        return a[-1].f

    return None


def _prev_AsyncWith_items(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.items[idx].f

    return None


def _prev_Match_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.cases:
        return a[-1].f

    return ast.subject.f


def _prev_Match_cases(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.cases[idx].f

    return ast.subject.f


def _prev_Raise_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.cause:
        return a.f

    if a := ast.exc:
        return a.f

    return None


def _prev_Raise_cause(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.exc:
        return a.f

    return None


def _prev_Try_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.finalbody:
        return a[-1].f

    if a := ast.orelse:
        return a[-1].f

    if a := ast.handlers:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return None


def _prev_Try_finalbody(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.finalbody[idx].f

    if a := ast.orelse:
        return a[-1].f

    if a := ast.handlers:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return None


def _prev_Try_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.orelse[idx].f

    if a := ast.handlers:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return None


def _prev_Try_handlers(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.handlers[idx].f

    if a := ast.body:
        return a[-1].f

    return None


def _prev_Try_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    return None


def _prev_TryStar_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.finalbody:
        return a[-1].f

    if a := ast.orelse:
        return a[-1].f

    if a := ast.handlers:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return None


def _prev_TryStar_finalbody(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.finalbody[idx].f

    if a := ast.orelse:
        return a[-1].f

    if a := ast.handlers:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return None


def _prev_TryStar_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.orelse[idx].f

    if a := ast.handlers:
        return a[-1].f

    if a := ast.body:
        return a[-1].f

    return None


def _prev_TryStar_handlers(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.handlers[idx].f

    if a := ast.body:
        return a[-1].f

    return None


def _prev_TryStar_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    return None


def _prev_Assert_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.msg:
        return a.f

    return ast.test.f


def _prev_Assert_msg(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.test.f


def _prev_Import_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.names:
        return a[-1].f

    return None


def _prev_Import_names(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.names[idx].f

    return None


def _prev_ImportFrom_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.names:
        return a[-1].f

    return None


def _prev_ImportFrom_names(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.names[idx].f

    return None


def _prev_Expr_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_BoolOp_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.values:
        return a[-1].f

    return ast.op.f


def _prev_BoolOp_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.values[idx].f

    return ast.op.f


def _prev_NamedExpr_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_NamedExpr_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _prev_BinOp_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.right.f


def _prev_BinOp_right(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.op.f


def _prev_BinOp_op(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.left.f


def _prev_UnaryOp_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.operand.f


def _prev_UnaryOp_operand(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.op.f


def _prev_Lambda_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.body.f


def _prev_Lambda_body(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.args.f


def _prev_IfExp_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.orelse.f


def _prev_IfExp_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.test.f


def _prev_IfExp_test(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.body.f


def _prev_Dict_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.values:
        return a[-1].f

    return None


def _prev_Dict_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.keys[idx]:
        return a.f

    if (idx := idx - 1) >= 0:
        return ast.values[idx].f

    return None


def _prev_Dict_keys(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return ast.values[idx].f

    return None


def _prev_Set_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.elts:
        return a[-1].f

    return None


def _prev_Set_elts(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.elts[idx].f

    return None


def _prev_ListComp_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[-1].f

    return ast.elt.f


def _prev_ListComp_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.generators[idx].f

    return ast.elt.f


def _prev_SetComp_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[-1].f

    return ast.elt.f


def _prev_SetComp_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.generators[idx].f

    return ast.elt.f


def _prev_DictComp_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[-1].f

    return ast.value.f


def _prev_DictComp_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.generators[idx].f

    return ast.value.f


def _prev_DictComp_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.key.f


def _prev_GeneratorExp_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[-1].f

    return ast.elt.f


def _prev_GeneratorExp_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.generators[idx].f

    return ast.elt.f


def _prev_Await_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_Yield_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.value:
        return a.f

    return None


def _prev_YieldFrom_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_Compare_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.comparators:
        return a[-1].f

    return ast.left.f


def _prev_Compare_comparators(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ops[idx].f


def _prev_Compare_ops(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.comparators[idx].f

    return ast.left.f


def _prev_Compare_left(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _prev_Call_END(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    kws = ast.keywords

    if not kws:
        if args:
            return args[-1].f

        return ast.func.f

    kwn = kws[-1]

    if (not args
        or (argn := args[-1]).__class__ is not Starred
        or (argn.lineno, argn.col_offset) < (kwn.lineno, kwn.col_offset)
    ):
        return kwn.f

    return argn.f


def _prev_Call_keywords(ast: AST, idx: int | None) -> _NextPrevRet:
    kws = ast.keywords
    args = ast.args
    idx_ = idx - 1

    if not args:
        if idx_ >= 0:
            return kws[idx_].f

        return ast.func.f

    if (last_arg := args[-1]).__class__ is not Starred:  # if no Starred then can't be mixed with keywords, unchecked walk backward
        if idx_ >= 0:
            return kws[idx_].f

        return last_arg.f

    last_arg_pos = (last_arg.lineno, last_arg.col_offset)

    if idx_ < 0:
        if (kw_pos := ((kw := kws[0]).lineno, kw.col_offset)) > last_arg_pos:
            return last_arg.f

        for arg in args[-2::-1]:  # only need to find last arg (if any) before first keyword
            if (arg.lineno, arg.col_offset) < kw_pos:
                return arg.f

        return ast.func.f

    if (kw_pos := ((kw := kws[idx_]).lineno, kw.col_offset)) > last_arg_pos:
        return kw.f

    if (kw_plus1_pos := ((kw_plus1 := kws[idx]).lineno, kw_plus1.col_offset)) > last_arg_pos:
        return last_arg.f

    for arg in args[-2::-1]:  # need to find last arg (if any) between next and last keywords
        arg_pos = (arg.lineno, arg.col_offset)

        if arg_pos < kw_pos:
            break
        if arg_pos < kw_plus1_pos:
            return arg.f

    return kw.f


def _prev_Call_args(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    kws = ast.keywords

    if (not kws
        or args[-1].__class__ is not Starred  # if no kws or last arg is not Starred then can't be mixed with keywords, unchecked walk backward
        or (arg_pos := ((arg := args[idx]).lineno, arg.col_offset))
            < (first_kw_pos := ((first_kw := kws[0]).lineno, first_kw.col_offset))  # this arg before first keyword so all args from here
    ):
        if (idx := idx - 1) >= 0:
            return args[idx].f

        return ast.func.f

    if not idx:  # no more args, just find last kw before this arg if any
        for kw in kws[1:]:  # from start likely shorter search, we already checked kws[0]
            if (kw.lineno, kw.col_offset) > arg_pos:
                break

            first_kw = kw

        return first_kw.f

    prev_arg = args[idx - 1]
    prev_arg_pos = (prev_arg.lineno, prev_arg.col_offset)

    for kw in kws[1:]:
        kw_pos = (kw.lineno, kw.col_offset)

        if kw_pos > arg_pos:
            break

        first_kw = kw
        first_kw_pos = kw_pos

    return (prev_arg if prev_arg_pos > first_kw_pos else first_kw).f


def _prev_Call_func(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _prev_FormattedValue_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.format_spec:
        return a.f

    return ast.value.f


def _prev_FormattedValue_format_spec(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_Interpolation_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.format_spec:
        return a.f

    return ast.value.f


def _prev_Interpolation_format_spec(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_JoinedStr_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.values:
        return a[-1].f

    return None


def _prev_JoinedStr_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.values[idx].f

    return None


def _prev_TemplateStr_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.values:
        return a[-1].f

    return None


def _prev_TemplateStr_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.values[idx].f

    return None


def _prev_Attribute_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _prev_Attribute_ctx(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_Subscript_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _prev_Subscript_ctx(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.slice.f


def _prev_Subscript_slice(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_Starred_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _prev_Starred_ctx(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_Name_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _prev_List_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _prev_List_ctx(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.elts:
        return a[-1].f

    return None


def _prev_List_elts(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.elts[idx].f

    return None


def _prev_Tuple_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _prev_Tuple_ctx(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.elts:
        return a[-1].f

    return None


def _prev_Tuple_elts(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.elts[idx].f

    return None


def _prev_Slice_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.step:
        return a.f

    if a := ast.upper:
        return a.f

    if a := ast.lower:
        return a.f

    return None


def _prev_Slice_step(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.upper:
        return a.f

    if a := ast.lower:
        return a.f

    return None


def _prev_Slice_upper(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.lower:
        return a.f

    return None


def _prev_comprehension_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.ifs:
        return a[-1].f

    return ast.iter.f


def _prev_comprehension_ifs(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.ifs[idx].f

    return ast.iter.f


def _prev_comprehension_iter(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _prev_ExceptHandler_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    if a := ast.type:
        return a.f

    return None


def _prev_ExceptHandler_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    if a := ast.type:
        return a.f

    return None


def _prev_arguments_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.kwarg:
        return a.f

    if a := ast.kw_defaults:
        if a := a[-1]:
            return a.f

    if a := ast.kwonlyargs:
        return a[-1].f

    if a := ast.vararg:
        return a.f

    if a := ast.defaults:
        return a[-1].f

    if a := ast.args:
        return a[-1].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_kwarg(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.kw_defaults:
        if a := a[-1]:
            return a.f

    if a := ast.kwonlyargs:
        return a[-1].f

    if a := ast.vararg:
        return a.f

    if a := ast.defaults:
        return a[-1].f

    if a := ast.args:
        return a[-1].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_kw_defaults(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.kwonlyargs[idx].f


def _prev_arguments_kwonlyargs(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        if a := ast.kw_defaults[idx]:
            return a.f

        return ast.kwonlyargs[idx].f

    if a := ast.vararg:
        return a.f

    if a := ast.defaults:
        return a[-1].f

    if a := ast.args:
        return a[-1].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_vararg(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.defaults:
        return a[-1].f

    if a := ast.args:
        return a[-1].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_defaults(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    iarg = len(args) - len(ast.defaults) + idx

    if iarg >= 0:
        return args[iarg].f

    return ast.posonlyargs[iarg].f


def _prev_arguments_args(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    defaults = ast.defaults
    idx -= 1

    if defaults:
        idefault = len(defaults) - len(args) + idx

        if idefault >= 0:
            return defaults[idefault].f

    if idx >= 0:
        return args[idx].f

    if a := ast.posonlyargs:
        return a[-1].f

    return None


def _prev_arguments_posonlyargs(ast: AST, idx: int | None) -> _NextPrevRet:
    posonlyargs = ast.posonlyargs
    defaults = ast.defaults
    idx -= 1

    if defaults:
        idefault = len(defaults) - len(ast.args) - len(posonlyargs) + idx

        if idefault >= 0:
            return defaults[idefault].f

    if idx >= 0:
        return posonlyargs[idx].f

    return None


def _prev_arg_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.annotation:
        return a.f

    return None


def _prev_keyword_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_withitem_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.optional_vars:
        return a.f

    return ast.context_expr.f


def _prev_withitem_optional_vars(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.context_expr.f


def _prev_match_case_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[-1].f

    if a := ast.guard:
        return a.f

    return ast.pattern.f


def _prev_match_case_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.body[idx].f

    if a := ast.guard:
        return a.f

    return ast.pattern.f


def _prev_match_case_guard(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.pattern.f


def _prev_MatchValue_END(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _prev_MatchSequence_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.patterns:
        return a[-1].f

    return None


def _prev_MatchSequence_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.patterns[idx].f

    return None


def _prev_MatchMapping_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.patterns:
        return a[-1].f

    return None


def _prev_MatchMapping_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.keys[idx]:  # OUR OWN SPECIAL CASE: MatchMapping.keys cannot normally be None but we make use of this temporarily in some operations
        return a.f

    if (idx := idx - 1) >= 0:
        return  ast.patterns[idx].f

    return None


def _prev_MatchMapping_keys(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.patterns[idx].f

    return None


def _prev_MatchClass_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.kwd_patterns:
        return a[-1].f

    if a := ast.patterns:
        return a[-1].f

    return ast.cls.f


def _prev_MatchClass_kwd_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.kwd_patterns[idx].f

    if a := ast.patterns:
        return a[-1].f

    return ast.cls.f


def _prev_MatchClass_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.patterns[idx].f

    return ast.cls.f


def _prev_MatchAs_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.pattern:
        return a.f

    return None


def _prev_MatchOr_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.patterns:
        return a[-1].f

    return None


def _prev_MatchOr_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.patterns[idx].f

    return None


def _prev_TypeVar_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    if a := ast.bound:
        return a.f

    return None


def _prev_TypeVar_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.bound:
        return a.f

    return None


def _prev_TypeVar_bound(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _prev_ParamSpec_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _prev_ParamSpec_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _prev_TypeVarTuple_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _prev_TypeVarTuple_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _prev__ExceptHandlers_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.handlers:
        return a[-1].f

    return None


def _prev__ExceptHandlers_handlers(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.handlers[idx].f

    return None


def _prev__match_cases_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.cases:
        return a[-1].f

    return None


def _prev__match_cases_cases(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.cases[idx].f

    return None


def _prev__Assign_targets_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.targets:
        return a[-1].f

    return None


def _prev__Assign_targets_targets(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.targets[idx].f

    return None


def _prev__decorator_list_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.decorator_list:
        return a[-1].f

    return None


def _prev__decorator_list_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.decorator_list[idx].f

    return None


def _prev__arglikes_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.arglikes:
        return a[-1].f

    return None


def _prev__arglikes_arglikes(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.arglikes[idx].f

    return None


def _prev__comprehensions_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[-1].f

    return None


def _prev__comprehensions_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.generators[idx].f

    return None


def _prev__comprehension_ifs_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.ifs:
        return a[-1].f

    return None


def _prev__comprehension_ifs_ifs(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.ifs[idx].f

    return None


def _prev__aliases_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.names:
        return a[-1].f

    return None


def _prev__aliases_names(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.names[idx].f

    return None


def _prev__withitems_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.items:
        return a[-1].f

    return None


def _prev__withitems_items(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.items[idx].f

    return None


def _prev__type_params_END(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.type_params:
        return a[-1].f

    return None


def _prev__type_params_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx - 1) >= 0:
        return  ast.type_params[idx].f

    return None


PREV_FUNCS = {
    (Module, None): _prev_Module_END,
    (Module, 'body'): _prev_Module_body,
    (Interactive, None): _prev_Interactive_END,
    (Interactive, 'body'): _prev_Interactive_body,
    (Expression, None): _prev_Expression_END,
    (Expression, 'body'): _prev_None,
    (FunctionType, None): _prev_FunctionType_END,
    (FunctionType, 'returns'): _prev_FunctionType_returns,
    (FunctionType, 'argtypes'): _prev_FunctionType_argtypes,
    (FunctionDef, None): _prev_FunctionDef_END,
    (FunctionDef, 'body'): _prev_FunctionDef_body,
    (FunctionDef, 'returns'): _prev_FunctionDef_returns,
    (FunctionDef, 'args'): _prev_FunctionDef_args,
    (FunctionDef, 'type_params'): _prev_FunctionDef_type_params,
    (FunctionDef, 'decorator_list'): _prev_FunctionDef_decorator_list,
    (AsyncFunctionDef, None): _prev_FunctionDef_END,
    (AsyncFunctionDef, 'body'): _prev_FunctionDef_body,
    (AsyncFunctionDef, 'returns'): _prev_FunctionDef_returns,
    (AsyncFunctionDef, 'args'): _prev_FunctionDef_args,
    (AsyncFunctionDef, 'type_params'): _prev_FunctionDef_type_params,
    (AsyncFunctionDef, 'decorator_list'): _prev_FunctionDef_decorator_list,
    (ClassDef, None): _prev_ClassDef_END,
    (ClassDef, 'body'): _prev_ClassDef_body,
    (ClassDef, 'keywords'): _prev_ClassDef_keywords,
    (ClassDef, 'bases'): _prev_ClassDef_bases,
    (ClassDef, 'type_params'): _prev_ClassDef_type_params,
    (ClassDef, 'decorator_list'): _prev_ClassDef_decorator_list,
    (Return, None): _prev_Return_END,
    (Return, 'value'): _prev_None,
    (Delete, None): _prev_Delete_END,
    (Delete, 'targets'): _prev_Delete_targets,
    (Assign, None): _prev_Assign_END,
    (Assign, 'value'): _prev_Assign_value,
    (Assign, 'targets'): _prev_Assign_targets,
    (TypeAlias, None): _prev_TypeAlias_END,
    (TypeAlias, 'value'): _prev_TypeAlias_value,
    (TypeAlias, 'type_params'): _prev_TypeAlias_type_params,
    (TypeAlias, 'name'): _prev_None,
    (AugAssign, None): _prev_AugAssign_END,
    (AugAssign, 'value'): _prev_AugAssign_value,
    (AugAssign, 'op'): _prev_AugAssign_op,
    (AugAssign, 'target'): _prev_None,
    (AnnAssign, None): _prev_AnnAssign_END,
    (AnnAssign, 'value'): _prev_AnnAssign_value,
    (AnnAssign, 'annotation'): _prev_AnnAssign_annotation,
    (AnnAssign, 'target'): _prev_None,
    (For, None): _prev_For_END,
    (For, 'orelse'): _prev_For_orelse,
    (For, 'body'): _prev_For_body,
    (For, 'iter'): _prev_For_iter,
    (For, 'target'): _prev_None,
    (AsyncFor, None): _prev_AsyncFor_END,
    (AsyncFor, 'orelse'): _prev_AsyncFor_orelse,
    (AsyncFor, 'body'): _prev_AsyncFor_body,
    (AsyncFor, 'iter'): _prev_AsyncFor_iter,
    (AsyncFor, 'target'): _prev_None,
    (While, None): _prev_While_END,
    (While, 'orelse'): _prev_While_orelse,
    (While, 'body'): _prev_While_body,
    (While, 'test'): _prev_None,
    (If, None): _prev_If_END,
    (If, 'orelse'): _prev_If_orelse,
    (If, 'body'): _prev_If_body,
    (If, 'test'): _prev_None,
    (With, None): _prev_With_END,
    (With, 'body'): _prev_With_body,
    (With, 'items'): _prev_With_items,
    (AsyncWith, None): _prev_AsyncWith_END,
    (AsyncWith, 'body'): _prev_AsyncWith_body,
    (AsyncWith, 'items'): _prev_AsyncWith_items,
    (Match, None): _prev_Match_END,
    (Match, 'cases'): _prev_Match_cases,
    (Match, 'subject'): _prev_None,
    (Raise, None): _prev_Raise_END,
    (Raise, 'cause'): _prev_Raise_cause,
    (Raise, 'exc'): _prev_None,
    (Try, None): _prev_Try_END,
    (Try, 'finalbody'): _prev_Try_finalbody,
    (Try, 'orelse'): _prev_Try_orelse,
    (Try, 'handlers'): _prev_Try_handlers,
    (Try, 'body'): _prev_Try_body,
    (TryStar, None): _prev_TryStar_END,
    (TryStar, 'finalbody'): _prev_TryStar_finalbody,
    (TryStar, 'orelse'): _prev_TryStar_orelse,
    (TryStar, 'handlers'): _prev_TryStar_handlers,
    (TryStar, 'body'): _prev_TryStar_body,
    (Assert, None): _prev_Assert_END,
    (Assert, 'msg'): _prev_Assert_msg,
    (Assert, 'test'): _prev_None,
    (Import, None): _prev_Import_END,
    (Import, 'names'): _prev_Import_names,
    (ImportFrom, None): _prev_ImportFrom_END,
    (ImportFrom, 'names'): _prev_ImportFrom_names,
    (Global, None): _prev_None,
    (Nonlocal, None): _prev_None,
    (Expr, None): _prev_Expr_END,
    (Expr, 'value'): _prev_None,
    (Pass, None): _prev_None,
    (Break, None): _prev_None,
    (Continue, None): _prev_None,
    (BoolOp, None): _prev_BoolOp_END,
    (BoolOp, 'values'): _prev_BoolOp_values,
    (BoolOp, 'op'): _prev_None,
    (NamedExpr, None): _prev_NamedExpr_END,
    (NamedExpr, 'value'): _prev_NamedExpr_value,
    (NamedExpr, 'target'): _prev_None,
    (BinOp, None): _prev_BinOp_END,
    (BinOp, 'right'): _prev_BinOp_right,
    (BinOp, 'op'): _prev_BinOp_op,
    (BinOp, 'left'): _prev_None,
    (UnaryOp, None): _prev_UnaryOp_END,
    (UnaryOp, 'operand'): _prev_UnaryOp_operand,
    (UnaryOp, 'op'): _prev_None,
    (Lambda, None): _prev_Lambda_END,
    (Lambda, 'body'): _prev_Lambda_body,
    (Lambda, 'args'): _prev_None,
    (IfExp, None): _prev_IfExp_END,
    (IfExp, 'orelse'): _prev_IfExp_orelse,
    (IfExp, 'test'): _prev_IfExp_test,
    (IfExp, 'body'): _prev_None,
    (Dict, None): _prev_Dict_END,
    (Dict, 'values'): _prev_Dict_values,
    (Dict, 'keys'): _prev_Dict_keys,
    (Set, None): _prev_Set_END,
    (Set, 'elts'): _prev_Set_elts,
    (ListComp, None): _prev_ListComp_END,
    (ListComp, 'generators'): _prev_ListComp_generators,
    (ListComp, 'elt'): _prev_None,
    (SetComp, None): _prev_SetComp_END,
    (SetComp, 'generators'): _prev_SetComp_generators,
    (SetComp, 'elt'): _prev_None,
    (DictComp, None): _prev_DictComp_END,
    (DictComp, 'generators'): _prev_DictComp_generators,
    (DictComp, 'value'): _prev_DictComp_value,
    (DictComp, 'key'): _prev_None,
    (GeneratorExp, None): _prev_GeneratorExp_END,
    (GeneratorExp, 'generators'): _prev_GeneratorExp_generators,
    (GeneratorExp, 'elt'): _prev_None,
    (Await, None): _prev_Await_END,
    (Await, 'value'): _prev_None,
    (Yield, None): _prev_Yield_END,
    (Yield, 'value'): _prev_None,
    (YieldFrom, None): _prev_YieldFrom_END,
    (YieldFrom, 'value'): _prev_None,
    (Compare, None): _prev_Compare_END,
    (Compare, 'comparators'): _prev_Compare_comparators,
    (Compare, 'ops'): _prev_Compare_ops,
    (Compare, 'left'): _prev_Compare_left,
    (Call, None): _prev_Call_END,
    (Call, 'keywords'): _prev_Call_keywords,
    (Call, 'args'): _prev_Call_args,
    (Call, 'func'): _prev_Call_func,
    (FormattedValue, None): _prev_FormattedValue_END,
    (FormattedValue, 'format_spec'): _prev_FormattedValue_format_spec,
    (FormattedValue, 'value'): _prev_None,
    (Interpolation, None): _prev_Interpolation_END,
    (Interpolation, 'format_spec'): _prev_Interpolation_format_spec,
    (Interpolation, 'value'): _prev_None,
    (JoinedStr, None): _prev_JoinedStr_END,
    (JoinedStr, 'values'): _prev_JoinedStr_values,
    (TemplateStr, None): _prev_TemplateStr_END,
    (TemplateStr, 'values'): _prev_TemplateStr_values,
    (Constant, None): _prev_None,
    (Attribute, None): _prev_Attribute_END,
    (Attribute, 'ctx'): _prev_Attribute_ctx,
    (Attribute, 'value'): _prev_None,
    (Subscript, None): _prev_Subscript_END,
    (Subscript, 'ctx'): _prev_Subscript_ctx,
    (Subscript, 'slice'): _prev_Subscript_slice,
    (Subscript, 'value'): _prev_None,
    (Starred, None): _prev_Starred_END,
    (Starred, 'ctx'): _prev_Starred_ctx,
    (Starred, 'value'): _prev_None,
    (Name, None): _prev_Name_END,
    (Name, 'ctx'): _prev_None,
    (List, None): _prev_List_END,
    (List, 'ctx'): _prev_List_ctx,
    (List, 'elts'): _prev_List_elts,
    (Tuple, None): _prev_Tuple_END,
    (Tuple, 'ctx'): _prev_Tuple_ctx,
    (Tuple, 'elts'): _prev_Tuple_elts,
    (Slice, None): _prev_Slice_END,
    (Slice, 'step'): _prev_Slice_step,
    (Slice, 'upper'): _prev_Slice_upper,
    (Slice, 'lower'): _prev_None,
    (Load, None): _prev_None,
    (Store, None): _prev_None,
    (Del, None): _prev_None,
    (And, None): _prev_None,
    (Or, None): _prev_None,
    (Add, None): _prev_None,
    (Sub, None): _prev_None,
    (Mult, None): _prev_None,
    (MatMult, None): _prev_None,
    (Div, None): _prev_None,
    (Mod, None): _prev_None,
    (Pow, None): _prev_None,
    (LShift, None): _prev_None,
    (RShift, None): _prev_None,
    (BitOr, None): _prev_None,
    (BitXor, None): _prev_None,
    (BitAnd, None): _prev_None,
    (FloorDiv, None): _prev_None,
    (Invert, None): _prev_None,
    (Not, None): _prev_None,
    (UAdd, None): _prev_None,
    (USub, None): _prev_None,
    (Eq, None): _prev_None,
    (NotEq, None): _prev_None,
    (Lt, None): _prev_None,
    (LtE, None): _prev_None,
    (Gt, None): _prev_None,
    (GtE, None): _prev_None,
    (Is, None): _prev_None,
    (IsNot, None): _prev_None,
    (In, None): _prev_None,
    (NotIn, None): _prev_None,
    (comprehension, None): _prev_comprehension_END,
    (comprehension, 'ifs'): _prev_comprehension_ifs,
    (comprehension, 'iter'): _prev_comprehension_iter,
    (comprehension, 'target'): _prev_None,
    (ExceptHandler, None): _prev_ExceptHandler_END,
    (ExceptHandler, 'body'): _prev_ExceptHandler_body,
    (ExceptHandler, 'type'): _prev_None,
    (arguments, None): _prev_arguments_END,
    (arguments, 'kwarg'): _prev_arguments_kwarg,
    (arguments, 'kw_defaults'): _prev_arguments_kw_defaults,
    (arguments, 'kwonlyargs'): _prev_arguments_kwonlyargs,
    (arguments, 'vararg'): _prev_arguments_vararg,
    (arguments, 'defaults'): _prev_arguments_defaults,
    (arguments, 'args'): _prev_arguments_args,
    (arguments, 'posonlyargs'): _prev_arguments_posonlyargs,
    (arg, None): _prev_arg_END,
    (arg, 'annotation'): _prev_None,
    (keyword, None): _prev_keyword_END,
    (keyword, 'value'): _prev_None,
    (alias, None): _prev_None,
    (withitem, None): _prev_withitem_END,
    (withitem, 'optional_vars'): _prev_withitem_optional_vars,
    (withitem, 'context_expr'): _prev_None,
    (match_case, None): _prev_match_case_END,
    (match_case, 'body'): _prev_match_case_body,
    (match_case, 'guard'): _prev_match_case_guard,
    (match_case, 'pattern'): _prev_None,
    (MatchValue, None): _prev_MatchValue_END,
    (MatchValue, 'value'): _prev_None,
    (MatchSingleton, None): _prev_None,
    (MatchSequence, None): _prev_MatchSequence_END,
    (MatchSequence, 'patterns'): _prev_MatchSequence_patterns,
    (MatchMapping, None): _prev_MatchMapping_END,
    (MatchMapping, 'patterns'): _prev_MatchMapping_patterns,
    (MatchMapping, 'keys'): _prev_MatchMapping_keys,
    (MatchClass, None): _prev_MatchClass_END,
    (MatchClass, 'kwd_patterns'): _prev_MatchClass_kwd_patterns,
    (MatchClass, 'patterns'): _prev_MatchClass_patterns,
    (MatchClass, 'cls'): _prev_None,
    (MatchStar, None): _prev_None,
    (MatchAs, None): _prev_MatchAs_END,
    (MatchAs, 'pattern'): _prev_None,
    (MatchOr, None): _prev_MatchOr_END,
    (MatchOr, 'patterns'): _prev_MatchOr_patterns,
    (TypeIgnore, None): _prev_None,
    (TypeVar, None): _prev_TypeVar_END,
    (TypeVar, 'default_value'): _prev_TypeVar_default_value,
    (TypeVar, 'bound'): _prev_TypeVar_bound,
    (ParamSpec, None): _prev_ParamSpec_END,
    (ParamSpec, 'default_value'): _prev_ParamSpec_default_value,
    (TypeVarTuple, None): _prev_TypeVarTuple_END,
    (TypeVarTuple, 'default_value'): _prev_TypeVarTuple_default_value,
    (_ExceptHandlers, None): _prev__ExceptHandlers_END,
    (_ExceptHandlers, 'handlers'): _prev__ExceptHandlers_handlers,
    (_match_cases, None): _prev__match_cases_END,
    (_match_cases, 'cases'): _prev__match_cases_cases,
    (_Assign_targets, None): _prev__Assign_targets_END,
    (_Assign_targets, 'targets'): _prev__Assign_targets_targets,
    (_decorator_list, None): _prev__decorator_list_END,
    (_decorator_list, 'decorator_list'): _prev__decorator_list_decorator_list,
    (_arglikes, None): _prev__arglikes_END,
    (_arglikes, 'arglikes'): _prev__arglikes_arglikes,
    (_comprehensions, None): _prev__comprehensions_END,
    (_comprehensions, 'generators'): _prev__comprehensions_generators,
    (_comprehension_ifs, None): _prev__comprehension_ifs_END,
    (_comprehension_ifs, 'ifs'): _prev__comprehension_ifs_ifs,
    (_aliases, None): _prev__aliases_END,
    (_aliases, 'names'): _prev__aliases_names,
    (_withitems, None): _prev__withitems_END,
    (_withitems, 'items'): _prev__withitems_items,
    (_type_params, None): _prev__type_params_END,
    (_type_params, 'type_params'): _prev__type_params_type_params,
}
