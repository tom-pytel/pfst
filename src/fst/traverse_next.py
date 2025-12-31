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

__all__ = ['NEXT_FUNCS']


_NextPrevRet = Union['fst.FST', None, tuple[str, int | None]]


def _next_None(ast: AST, idx: int | None) -> _NextPrevRet:
      return None


def _next_Module_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    return None


def _next_Module_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None


def _next_Interactive_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    return None


def _next_Interactive_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None


def _next_Expression_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.body.f


def _next_FunctionType_START(ast: AST, idx: int | None) -> _NextPrevRet:  # pragma: no cover
    if a := ast.argtypes:
        return a[0].f

    return ast.returns.f


def _next_FunctionType_argtypes(ast: AST, idx: int | None) -> _NextPrevRet:  # pragma: no cover
    if (idx := idx + 1) < len(a := ast.argtypes):
        return a[idx].f

    return ast.returns.f


def _next_FunctionDef_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.decorator_list:
        return a[0].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[0].f

    return ast.args.f


def _next_FunctionDef_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.decorator_list):
        return a[idx].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[0].f

    return ast.args.f


def _next_FunctionDef_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.type_params):  # if we got into this function then the AST has this
        return a[idx].f

    return ast.args.f


def _next_FunctionDef_args(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.returns:
        return a.f

    if a := ast.body:
        return a[0].f

    return None


def _next_FunctionDef_returns(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    return None


def _next_FunctionDef_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None


def _next_ClassDef_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.decorator_list:
        return a[0].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[0].f

    return _next_ClassDef_bases_or_keywords_start(ast)


def _next_ClassDef_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.decorator_list):
        return a[idx].f

    if a := getattr(ast, 'type_params', False):  # for py < 3.12 which doesn't have type_params
        return a[0].f

    return _next_ClassDef_bases_or_keywords_start(ast)


def _next_ClassDef_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.type_params):  # if we got into this function then the AST has this
        return a[idx].f

    return _next_ClassDef_bases_or_keywords_start(ast)


def _next_ClassDef_bases_or_keywords_start(ast: AST) -> _NextPrevRet:  # SPECIAL
    bases = ast.bases
    kws = ast.keywords

    if not kws:
        if bases:
            return bases[0].f

        if a := ast.body:
            return a[0].f

        return None

    if (not bases
        or (
            (base0 := bases[0]).__class__ is Starred
            and (base0.lineno, base0.col_offset) > ((kw0 := kws[0]).lineno, kw0.col_offset)
    )):
        return kws[0].f

    return base0.f


def _next_ClassDef_bases(ast: AST, idx: int | None) -> _NextPrevRet:
    bases = ast.bases
    last = bases[-1]  # we know there is at least one .bases because otherwise we wouldn't be in this function

    if last.__class__ is not Starred:  # if no Starred then can't be mixed with keywords, unchecked walk forward
        if (idx := idx + 1) < len(bases):
            return bases[idx].f

        if a := ast.keywords:
            return a[0].f

        if a := ast.body:
            return a[0].f

        return None

    base = bases[idx]
    base_pos = (base.lineno, base.col_offset)

    if base is last:  # only need to find first keyword after this base
        for kw in ast.keywords:
            if (kw.lineno, kw.col_offset) > base_pos:
                return kw.f

        if a := ast.body:
            return a[0].f

        return None

    next_base = bases[idx + 1]
    next_base_pos = (next_base.lineno, next_base.col_offset)

    for kw in ast.keywords:
        kw_pos = (kw.lineno, kw.col_offset)

        if kw_pos > next_base_pos:
            return next_base.f
        if kw_pos > base_pos:
            return kw.f

    return next_base.f


def _next_ClassDef_keywords(ast: AST, idx: int | None) -> _NextPrevRet:
    bases = ast.bases
    kws = ast.keywords

    if (not bases
        or (last_base := bases[-1]).__class__ is not Starred  # if no bases or no Starred then can't be mixed with keywords, unchecked walk forward
        or (last_base_pos := (last_base.lineno, last_base.col_offset))
            < (kw_pos := ((kw := kws[idx]).lineno, kw.col_offset))  # last Starred base before this kw (likely case)
    ):
        if (idx := idx + 1) < len(kws):
            return kws[idx].f

        if a := ast.body:
            return a[0].f

        return None

    if kw is kws[-1]:  # no more kws, just find first base past this kw if any (will be Starred)
        for base in bases[-2::-1]:  # we search backwards because more likely to be shorter search
            if (base.lineno, base.col_offset) < kw_pos:
                break

            last_base = base

        return last_base.f

    next_kw = kws[idx + 1]
    next_kw_pos = (next_kw.lineno, next_kw.col_offset)

    for base in bases[-2::-1]:
        base_pos = (base.lineno, base.col_offset)

        if base_pos < kw_pos:
            break

        last_base = base
        last_base_pos = base_pos

    return (next_kw if next_kw_pos < last_base_pos else last_base).f


def _next_ClassDef_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None


def _next_Return_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.value:
        return a.f

    return None


def _next_Delete_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.targets:
        return a[0].f

    return None


def _next_Delete_targets(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.targets):
        return a[idx].f

    return None


def _next_Assign_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.targets:
        return a[0].f

    return ast.value.f


def _next_Assign_targets(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.targets):
        return a[idx].f

    return ast.value.f


def _next_TypeAlias_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.name.f


def _next_TypeAlias_name(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.type_params:
        return a[0].f

    return ast.value.f


def _next_TypeAlias_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.type_params):
        return a[idx].f

    return ast.value.f


def _next_AugAssign_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _next_AugAssign_target(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.op.f


def _next_AugAssign_op(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_AnnAssign_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _next_AnnAssign_target(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.annotation.f


def _next_AnnAssign_annotation(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.value:
        return a.f

    return None


def _next_For_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _next_For_target(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.iter.f


def _next_For_iter(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    if a := ast.orelse:
        return a[0].f

    return None


def _next_For_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    if a := ast.orelse:
        return a[0].f

    return None


def _next_For_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.orelse):
        return a[idx].f

    return None


def _next_AsyncFor_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _next_AsyncFor_target(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.iter.f


def _next_AsyncFor_iter(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    if a := ast.orelse:
        return a[0].f

    return None


def _next_AsyncFor_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    if a := ast.orelse:
        return a[0].f

    return None


def _next_AsyncFor_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.orelse):
        return a[idx].f

    return None


def _next_While_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.test.f


def _next_While_test(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    if a := ast.orelse:
        return a[0].f

    return None


def _next_While_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    if a := ast.orelse:
        return a[0].f

    return None


def _next_While_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.orelse):
        return a[idx].f

    return None


def _next_If_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.test.f


def _next_If_test(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    if a := ast.orelse:
        return a[0].f

    return None


def _next_If_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    if a := ast.orelse:
        return a[0].f

    return None


def _next_If_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.orelse):
        return a[idx].f

    return None


def _next_With_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.items:
        return a[0].f

    if a := ast.body:
        return a[0].f

    return None


def _next_With_items(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.items):
        return a[idx].f

    if a := ast.body:
        return a[0].f

    return None


def _next_With_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None


def _next_AsyncWith_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.items:
        return a[0].f

    if a := ast.body:
        return a[0].f

    return None


def _next_AsyncWith_items(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.items):
        return a[idx].f

    if a := ast.body:
        return a[0].f

    return None


def _next_AsyncWith_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None


def _next_Match_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.subject.f


def _next_Match_subject(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.cases:
        return a[0].f

    return None


def _next_Match_cases(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.cases):
        return a[idx].f

    return None


def _next_Raise_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.exc:
        return a.f

    if a := ast.cause:
        return a.f

    return None


def _next_Raise_exc(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.cause:
        return a.f

    return None


def _next_Try_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    if a := ast.handlers:
        return a[0].f

    if a := ast.orelse:
        return a[0].f

    if a := ast.finalbody:
        return a[0].f

    return None


def _next_Try_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    if a := ast.handlers:
        return a[0].f

    if a := ast.orelse:
        return a[0].f

    if a := ast.finalbody:
        return a[0].f

    return None


def _next_Try_handlers(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.handlers):
        return a[idx].f

    if a := ast.orelse:
        return a[0].f

    if a := ast.finalbody:
        return a[0].f

    return None


def _next_Try_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.orelse):
        return a[idx].f

    if a := ast.finalbody:
        return a[0].f

    return None


def _next_Try_finalbody(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.finalbody):
        return a[idx].f

    return None


def _next_TryStar_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    if a := ast.handlers:
        return a[0].f

    if a := ast.orelse:
        return a[0].f

    if a := ast.finalbody:
        return a[0].f

    return None


def _next_TryStar_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    if a := ast.handlers:
        return a[0].f

    if a := ast.orelse:
        return a[0].f

    if a := ast.finalbody:
        return a[0].f

    return None


def _next_TryStar_handlers(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.handlers):
        return a[idx].f

    if a := ast.orelse:
        return a[0].f

    if a := ast.finalbody:
        return a[0].f

    return None


def _next_TryStar_orelse(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.orelse):
        return a[idx].f

    if a := ast.finalbody:
        return a[0].f

    return None


def _next_TryStar_finalbody(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.finalbody):
        return a[idx].f

    return None


def _next_Assert_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.test.f


def _next_Assert_test(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.msg:
        return a.f

    return None


def _next_Import_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.names:
        return a[0].f

    return None


def _next_Import_names(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.names):
        return a[idx].f

    return None


def _next_ImportFrom_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.names:
        return a[0].f

    return None


def _next_ImportFrom_names(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.names):
        return a[idx].f

    return None


def _next_Expr_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_BoolOp_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.op.f


def _next_BoolOp_op(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.values:
        return a[0].f

    return None


def _next_BoolOp_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.values):
        return a[idx].f

    return None


def _next_NamedExpr_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _next_NamedExpr_target(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_BinOp_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.left.f


def _next_BinOp_left(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.op.f


def _next_BinOp_op(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.right.f


def _next_UnaryOp_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.op.f


def _next_UnaryOp_op(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.operand.f


def _next_Lambda_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.args.f


def _next_Lambda_args(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.body.f


def _next_IfExp_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.body.f


def _next_IfExp_body(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.test.f


def _next_IfExp_test(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.orelse.f


def _next_Dict_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.keys:
        if a := a[0]:  # key may be None
            return a.f

        return ast.values[0].f

    return None


def _next_Dict_keys(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.values[idx].f


def _next_Dict_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.keys):
        if a := a[idx]:  # key may be None
            return a.f

        return ast.values[idx].f

    return None


def _next_Set_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.elts:
        return a[0].f

    return None


def _next_Set_elts(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.elts):
        return a[idx].f

    return None


def _next_ListComp_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.elt.f


def _next_ListComp_elt(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[0].f

    return None


def _next_ListComp_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.generators):
        return a[idx].f

    return None


def _next_SetComp_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.elt.f


def _next_SetComp_elt(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[0].f

    return None


def _next_SetComp_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.generators):
        return a[idx].f

    return None


def _next_DictComp_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.key.f


def _next_DictComp_key(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_DictComp_value(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[0].f

    return None


def _next_DictComp_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.generators):
        return a[idx].f

    return None


def _next_GeneratorExp_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.elt.f


def _next_GeneratorExp_elt(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[0].f

    return None


def _next_GeneratorExp_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.generators):
        return a[idx].f

    return None


def _next_Await_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_Yield_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.value:
        return a.f

    return None


def _next_YieldFrom_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_Compare_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.left.f


def _next_Compare_left(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.ops:
        return a[0].f

    return None


def _next_Compare_ops(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.comparators[idx].f


def _next_Compare_comparators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.ops):
        return a[idx].f

    return None


def _next_Call_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.func.f


def _next_Call_func(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    kws = ast.keywords

    if not kws:
        if args:
            return args[0].f

        return None

    kw0 = kws[0]

    if (not args
        or (
            (arg0 := args[0]).__class__ is Starred
            and (arg0.lineno, arg0.col_offset) > (kw0.lineno, kw0.col_offset)
    )):
        return kw0.f

    return arg0.f


def _next_Call_args(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    last_arg = args[-1]  # we know there is at least one .args because otherwise we wouldn't be in this function

    if last_arg.__class__ is not Starred:  # if no Starred then can't be mixed with keywords, unchecked walk forward
        if (idx := idx + 1) < len(args):
            return args[idx].f

        if a := ast.keywords:
            return a[0].f

        return None

    arg = args[idx]
    arg_pos = (arg.lineno, arg.col_offset)

    if arg is last_arg:  # only need to find first keyword after this arg
        for kw in ast.keywords:
            if (kw.lineno, kw.col_offset) > arg_pos:
                return kw.f

        return None

    next_arg = args[idx + 1]
    next_arg_pos = (next_arg.lineno, next_arg.col_offset)

    for kw in ast.keywords:
        kw_pos = (kw.lineno, kw.col_offset)

        if kw_pos > next_arg_pos:
            return next_arg.f
        if kw_pos > arg_pos:
            return kw.f

    return next_arg.f


def _next_Call_keywords(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    kws = ast.keywords

    if (not args
        or (last_arg := args[-1]).__class__ is not Starred  # if no args or no Starred then can't be mixed with keywords, unchecked walk forward
        or (last_arg_pos := (last_arg.lineno, last_arg.col_offset))
            < (kw_pos := ((kw := kws[idx]).lineno, kw.col_offset))  # last Starred arg before this kw (likely case)
    ):
        if (idx := idx + 1) < len(kws):
            return kws[idx].f

        return None

    if kw is kws[-1]:  # no more kws, just find first arg past this kw if any (will be Starred)
        for arg in args[-2::-1]:  # we search backwards because more likely to be shorter search
            if (arg.lineno, arg.col_offset) < kw_pos:
                break

            last_arg = arg

        return last_arg.f

    next_kw = kws[idx + 1]
    next_kw_pos = (next_kw.lineno, next_kw.col_offset)

    for arg in args[-2::-1]:
        arg_pos = (arg.lineno, arg.col_offset)

        if arg_pos < kw_pos:
            break

        last_arg = arg
        last_arg_pos = arg_pos

    return (next_kw if next_kw_pos < last_arg_pos else last_arg).f


def _next_FormattedValue_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_FormattedValue_value(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.format_spec:
        return a.f

    return None


def _next_Interpolation_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_Interpolation_value(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.format_spec:
        return a.f

    return None


def _next_JoinedStr_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.values:
        return a[0].f

    return None


def _next_JoinedStr_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.values):
        return a[idx].f

    return None


def _next_TemplateStr_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.values:
        return a[0].f

    return None


def _next_TemplateStr_values(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.values):
        return a[idx].f

    return None


def _next_Attribute_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_Attribute_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _next_Subscript_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_Subscript_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.slice.f


def _next_Subscript_slice(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _next_Starred_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_Starred_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _next_Name_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.ctx.f


def _next_List_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.elts:
        return a[0].f

    return ast.ctx.f


def _next_List_elts(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.elts):
        return a[idx].f

    return ast.ctx.f


def _next_Tuple_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.elts:
        return a[0].f

    return ast.ctx.f


def _next_Tuple_elts(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.elts):
        return a[idx].f

    return ast.ctx.f


def _next_Slice_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.lower:
        return a.f

    if a := ast.upper:
        return a.f

    if a := ast.step:
        return a.f

    return None


def _next_Slice_lower(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.upper:
        return a.f

    if a := ast.step:
        return a.f

    return None


def _next_Slice_upper(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.step:
        return a.f

    return None


def _next_comprehension_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.target.f


def _next_comprehension_target(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.iter.f


def _next_comprehension_iter(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.ifs:
        return a[0].f

    return None


def _next_comprehension_ifs(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.ifs):
        return a[idx].f

    return None


def _next_ExceptHandler_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.type:
        return a.f

    if a := ast.body:
        return a[0].f

    return None


def _next_ExceptHandler_type(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    return None


def _next_ExceptHandler_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None


def _next_arguments_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.posonlyargs:
        return a[0].f
    if a := ast.args:
        return a[0].f
    if a := ast.vararg:
        return a.f
    if a := ast.kwonlyargs:
        return a[0].f
    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_posonlyargs(ast: AST, idx: int | None) -> _NextPrevRet:
    posonlyargs = ast.posonlyargs
    nposonlyargs = len(posonlyargs)
    defaults = ast.defaults

    if defaults:
        idefault = len(defaults) - nposonlyargs - len(ast.args) + idx

        if idefault >= 0:
            return defaults[idefault].f

    if (idx := idx + 1) < nposonlyargs:
        return posonlyargs[idx].f

    if a := ast.args:
        return a[0].f
    if a := ast.vararg:
        return a.f
    if a := ast.kwonlyargs:
        return a[0].f
    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_args(ast: AST, idx: int | None) -> _NextPrevRet:
    args = ast.args
    nargs = len(args)
    defaults = ast.defaults

    if defaults:
        idefault = len(defaults) - nargs + idx

        if idefault >= 0:
            return defaults[idefault].f

    if (idx := idx + 1) < nargs:
        return args[idx].f

    if a := ast.vararg:
        return a.f
    if a := ast.kwonlyargs:
        return a[0].f
    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_defaults(ast: AST, idx: int | None) -> _NextPrevRet:
    ndefaults = len(ast.defaults)
    idx += 1

    if idx == ndefaults:  # end of defaults
        if a := ast.vararg:
            return a.f
        if a := ast.kwonlyargs:
            return a[0].f
        if a := ast.kwarg:
            return a.f

        return None

    args = ast.args
    iarg = len(args) - ndefaults + idx

    if iarg >= 0:
        return args[iarg].f

    return ast.posonlyargs[iarg].f


def _next_arguments_vararg(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.kwonlyargs:
        return a[0].f
    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_kwonlyargs(ast: AST, idx: int | None) -> _NextPrevRet:
    kw_default = ast.kw_defaults[idx]

    if kw_default:
        return kw_default.f

    if (idx := idx + 1) < len(a := ast.kwonlyargs):
        return a[idx].f

    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_kw_defaults(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.kwonlyargs):
        return a[idx].f

    if a := ast.kwarg:
        return a.f

    return None


def _next_arguments_kwarg(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _next_arg_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.annotation:
        return a.f

    return None


def _next_keyword_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_withitem_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.context_expr.f


def _next_withitem_context_expr(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.optional_vars:
        return a.f

    return None


def _next_match_case_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.pattern.f


def _next_match_case_pattern(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.guard:
        return a.f

    if a := ast.body:
        return a[0].f

    return None


def _next_match_case_guard(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.body:
        return a[0].f

    return None


def _next_match_case_body(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.body):
        return a[idx].f

    return None


def _next_MatchValue_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.value.f


def _next_MatchSequence_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.patterns:
        return a[0].f

    return None


def _next_MatchSequence_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.patterns):
        return a[idx].f

    return None


def _next_MatchMapping_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.keys:
        return a[0].f

    return None


def _next_MatchMapping_keys(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.patterns[idx].f


def _next_MatchMapping_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.keys):
        if a := a[idx]:  # OUR OWN SPECIAL CASE: MatchMapping.keys cannot normally be None but we make use of this temporarily in some operations
            return a.f

        return ast.patterns[idx].f

    return None


def _next_MatchClass_START(ast: AST, idx: int | None) -> _NextPrevRet:
    return ast.cls.f


def _next_MatchClass_cls(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.patterns:
        return a[0].f

    if a := ast.kwd_patterns:
        return a[0].f

    return None


def _next_MatchClass_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.patterns):
        return a[idx].f

    if a := ast.kwd_patterns:
        return a[0].f

    return None


def _next_MatchClass_kwd_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.kwd_patterns):
        return a[idx].f

    return None


def _next_MatchAs_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.pattern:
        return a.f

    return None


def _next_MatchOr_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.patterns:
        return a[0].f

    return None


def _next_MatchOr_patterns(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.patterns):
        return a[idx].f

    return None


def _next_TypeVar_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.bound:
        return a.f

    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _next_TypeVar_bound(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _next_TypeVar_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _next_ParamSpec_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _next_ParamSpec_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _next_TypeVarTuple_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := getattr(ast, 'default_value', None):  # for py < 3.13 which doesn't have default_value
        return a.f

    return None


def _next_TypeVarTuple_default_value(ast: AST, idx: int | None) -> _NextPrevRet:
    return None


def _next__ExceptHandlers_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.handlers:
        return a[0].f

    return None


def _next__ExceptHandlers_handlers(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.handlers):
        return a[idx].f

    return None


def _next__match_cases_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.cases:
        return a[0].f

    return None


def _next__match_cases_cases(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.cases):
        return a[idx].f

    return None


def _next__Assign_targets_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.targets:
        return a[0].f

    return None


def _next__Assign_targets_targets(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.targets):
        return a[idx].f

    return None


def _next__decorator_list_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.decorator_list:
        return a[0].f

    return None


def _next__decorator_list_decorator_list(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.decorator_list):
        return a[idx].f

    return None


def _next__arglikes_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.arglikes:
        return a[0].f

    return None


def _next__arglikes_arglikes(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.arglikes):
        return a[idx].f

    return None


def _next__comprehensions_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.generators:
        return a[0].f

    return None


def _next__comprehensions_generators(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.generators):
        return a[idx].f

    return None


def _next__comprehension_ifs_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.ifs:
        return a[0].f

    return None


def _next__comprehension_ifs_ifs(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.ifs):
        return a[idx].f

    return None


def _next__aliases_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.names:
        return a[0].f

    return None


def _next__aliases_names(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.names):
        return a[idx].f

    return None


def _next__withitems_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.items:
        return a[0].f

    return None


def _next__withitems_items(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.items):
        return a[idx].f

    return None


def _next__type_params_START(ast: AST, idx: int | None) -> _NextPrevRet:
    if a := ast.type_params:
        return a[0].f

    return None


def _next__type_params_type_params(ast: AST, idx: int | None) -> _NextPrevRet:
    if (idx := idx + 1) < len(a := ast.type_params):
        return a[idx].f

    return None


NEXT_FUNCS = {
    (Module, None): _next_Module_START,
    (Module, 'body'): _next_Module_body,
    (Interactive, None): _next_Interactive_START,
    (Interactive, 'body'): _next_Interactive_body,
    (Expression, None): _next_Expression_START,
    (Expression, 'body'): _next_None,
    (FunctionType, None): _next_FunctionType_START,
    (FunctionType, 'argtypes'): _next_FunctionType_argtypes,
    (FunctionType, 'returns'): _next_None,
    (FunctionDef, None): _next_FunctionDef_START,
    (FunctionDef, 'decorator_list'): _next_FunctionDef_decorator_list,
    (FunctionDef, 'type_params'): _next_FunctionDef_type_params,
    (FunctionDef, 'args'): _next_FunctionDef_args,
    (FunctionDef, 'returns'): _next_FunctionDef_returns,
    (FunctionDef, 'body'): _next_FunctionDef_body,
    (AsyncFunctionDef, None): _next_FunctionDef_START,
    (AsyncFunctionDef, 'decorator_list'): _next_FunctionDef_decorator_list,
    (AsyncFunctionDef, 'type_params'): _next_FunctionDef_type_params,
    (AsyncFunctionDef, 'args'): _next_FunctionDef_args,
    (AsyncFunctionDef, 'returns'): _next_FunctionDef_returns,
    (AsyncFunctionDef, 'body'): _next_FunctionDef_body,
    (ClassDef, None): _next_ClassDef_START,
    (ClassDef, 'decorator_list'): _next_ClassDef_decorator_list,
    (ClassDef, 'type_params'): _next_ClassDef_type_params,
    (ClassDef, 'bases'): _next_ClassDef_bases,
    (ClassDef, 'keywords'): _next_ClassDef_keywords,
    (ClassDef, 'body'): _next_ClassDef_body,
    (Return, None): _next_Return_START,
    (Return, 'value'): _next_None,
    (Delete, None): _next_Delete_START,
    (Delete, 'targets'): _next_Delete_targets,
    (Assign, None): _next_Assign_START,
    (Assign, 'targets'): _next_Assign_targets,
    (Assign, 'value'): _next_None,
    (TypeAlias, None): _next_TypeAlias_START,
    (TypeAlias, 'name'): _next_TypeAlias_name,
    (TypeAlias, 'type_params'): _next_TypeAlias_type_params,
    (TypeAlias, 'value'): _next_None,
    (AugAssign, None): _next_AugAssign_START,
    (AugAssign, 'target'): _next_AugAssign_target,
    (AugAssign, 'op'): _next_AugAssign_op,
    (AugAssign, 'value'): _next_None,
    (AnnAssign, None): _next_AnnAssign_START,
    (AnnAssign, 'target'): _next_AnnAssign_target,
    (AnnAssign, 'annotation'): _next_AnnAssign_annotation,
    (AnnAssign, 'value'): _next_None,
    (For, None): _next_For_START,
    (For, 'target'): _next_For_target,
    (For, 'iter'): _next_For_iter,
    (For, 'body'): _next_For_body,
    (For, 'orelse'): _next_For_orelse,
    (AsyncFor, None): _next_AsyncFor_START,
    (AsyncFor, 'target'): _next_AsyncFor_target,
    (AsyncFor, 'iter'): _next_AsyncFor_iter,
    (AsyncFor, 'body'): _next_AsyncFor_body,
    (AsyncFor, 'orelse'): _next_AsyncFor_orelse,
    (While, None): _next_While_START,
    (While, 'test'): _next_While_test,
    (While, 'body'): _next_While_body,
    (While, 'orelse'): _next_While_orelse,
    (If, None): _next_If_START,
    (If, 'test'): _next_If_test,
    (If, 'body'): _next_If_body,
    (If, 'orelse'): _next_If_orelse,
    (With, None): _next_With_START,
    (With, 'items'): _next_With_items,
    (With, 'body'): _next_With_body,
    (AsyncWith, None): _next_AsyncWith_START,
    (AsyncWith, 'items'): _next_AsyncWith_items,
    (AsyncWith, 'body'): _next_AsyncWith_body,
    (Match, None): _next_Match_START,
    (Match, 'subject'): _next_Match_subject,
    (Match, 'cases'): _next_Match_cases,
    (Raise, None): _next_Raise_START,
    (Raise, 'exc'): _next_Raise_exc,
    (Raise, 'cause'): _next_None,
    (Try, None): _next_Try_START,
    (Try, 'body'): _next_Try_body,
    (Try, 'handlers'): _next_Try_handlers,
    (Try, 'orelse'): _next_Try_orelse,
    (Try, 'finalbody'): _next_Try_finalbody,
    (TryStar, None): _next_TryStar_START,
    (TryStar, 'body'): _next_TryStar_body,
    (TryStar, 'handlers'): _next_TryStar_handlers,
    (TryStar, 'orelse'): _next_TryStar_orelse,
    (TryStar, 'finalbody'): _next_TryStar_finalbody,
    (Assert, None): _next_Assert_START,
    (Assert, 'test'): _next_Assert_test,
    (Assert, 'msg'): _next_None,
    (Import, None): _next_Import_START,
    (Import, 'names'): _next_Import_names,
    (ImportFrom, None): _next_ImportFrom_START,
    (ImportFrom, 'names'): _next_ImportFrom_names,
    (Global, None): _next_None,
    (Nonlocal, None): _next_None,
    (Expr, None): _next_Expr_START,
    (Expr, 'value'): _next_None,
    (Pass, None): _next_None,
    (Break, None): _next_None,
    (Continue, None): _next_None,
    (BoolOp, None): _next_BoolOp_START,
    (BoolOp, 'op'): _next_BoolOp_op,
    (BoolOp, 'values'): _next_BoolOp_values,
    (NamedExpr, None): _next_NamedExpr_START,
    (NamedExpr, 'target'): _next_NamedExpr_target,
    (NamedExpr, 'value'): _next_None,
    (BinOp, None): _next_BinOp_START,
    (BinOp, 'left'): _next_BinOp_left,
    (BinOp, 'op'): _next_BinOp_op,
    (BinOp, 'right'): _next_None,
    (UnaryOp, None): _next_UnaryOp_START,
    (UnaryOp, 'op'): _next_UnaryOp_op,
    (UnaryOp, 'operand'): _next_None,
    (Lambda, None): _next_Lambda_START,
    (Lambda, 'args'): _next_Lambda_args,
    (Lambda, 'body'): _next_None,
    (IfExp, None): _next_IfExp_START,
    (IfExp, 'body'): _next_IfExp_body,
    (IfExp, 'test'): _next_IfExp_test,
    (IfExp, 'orelse'): _next_None,
    (Dict, None): _next_Dict_START,
    (Dict, 'keys'): _next_Dict_keys,
    (Dict, 'values'): _next_Dict_values,
    (Set, None): _next_Set_START,
    (Set, 'elts'): _next_Set_elts,
    (ListComp, None): _next_ListComp_START,
    (ListComp, 'elt'): _next_ListComp_elt,
    (ListComp, 'generators'): _next_ListComp_generators,
    (SetComp, None): _next_SetComp_START,
    (SetComp, 'elt'): _next_SetComp_elt,
    (SetComp, 'generators'): _next_SetComp_generators,
    (DictComp, None): _next_DictComp_START,
    (DictComp, 'key'): _next_DictComp_key,
    (DictComp, 'value'): _next_DictComp_value,
    (DictComp, 'generators'): _next_DictComp_generators,
    (GeneratorExp, None): _next_GeneratorExp_START,
    (GeneratorExp, 'elt'): _next_GeneratorExp_elt,
    (GeneratorExp, 'generators'): _next_GeneratorExp_generators,
    (Await, None): _next_Await_START,
    (Await, 'value'): _next_None,
    (Yield, None): _next_Yield_START,
    (Yield, 'value'): _next_None,
    (YieldFrom, None): _next_YieldFrom_START,
    (YieldFrom, 'value'): _next_None,
    (Compare, None): _next_Compare_START,
    (Compare, 'left'): _next_Compare_left,
    (Compare, 'ops'): _next_Compare_ops,
    (Compare, 'comparators'): _next_Compare_comparators,
    (Call, None): _next_Call_START,
    (Call, 'func'): _next_Call_func,
    (Call, 'args'): _next_Call_args,
    (Call, 'keywords'): _next_Call_keywords,
    (FormattedValue, None): _next_FormattedValue_START,
    (FormattedValue, 'value'): _next_FormattedValue_value,
    (FormattedValue, 'format_spec'): _next_None,
    (Interpolation, None): _next_Interpolation_START,
    (Interpolation, 'value'): _next_Interpolation_value,
    (Interpolation, 'format_spec'): _next_None,
    (JoinedStr, None): _next_JoinedStr_START,
    (JoinedStr, 'values'): _next_JoinedStr_values,
    (TemplateStr, None): _next_TemplateStr_START,
    (TemplateStr, 'values'): _next_TemplateStr_values,
    (Constant, None): _next_None,
    (Attribute, None): _next_Attribute_START,
    (Attribute, 'value'): _next_Attribute_value,
    (Attribute, 'ctx'): _next_None,
    (Subscript, None): _next_Subscript_START,
    (Subscript, 'value'): _next_Subscript_value,
    (Subscript, 'slice'): _next_Subscript_slice,
    (Subscript, 'ctx'): _next_None,
    (Starred, None): _next_Starred_START,
    (Starred, 'value'): _next_Starred_value,
    (Starred, 'ctx'): _next_None,
    (Name, None): _next_Name_START,
    (Name, 'ctx'): _next_None,
    (List, None): _next_List_START,
    (List, 'elts'): _next_List_elts,
    (List, 'ctx'): _next_None,
    (Tuple, None): _next_Tuple_START,
    (Tuple, 'elts'): _next_Tuple_elts,
    (Tuple, 'ctx'): _next_None,
    (Slice, None): _next_Slice_START,
    (Slice, 'lower'): _next_Slice_lower,
    (Slice, 'upper'): _next_Slice_upper,
    (Slice, 'step'): _next_None,
    (Load, None): _next_None,
    (Store, None): _next_None,
    (Del, None): _next_None,
    (And, None): _next_None,
    (Or, None): _next_None,
    (Add, None): _next_None,
    (Sub, None): _next_None,
    (Mult, None): _next_None,
    (MatMult, None): _next_None,
    (Div, None): _next_None,
    (Mod, None): _next_None,
    (Pow, None): _next_None,
    (LShift, None): _next_None,
    (RShift, None): _next_None,
    (BitOr, None): _next_None,
    (BitXor, None): _next_None,
    (BitAnd, None): _next_None,
    (FloorDiv, None): _next_None,
    (Invert, None): _next_None,
    (Not, None): _next_None,
    (UAdd, None): _next_None,
    (USub, None): _next_None,
    (Eq, None): _next_None,
    (NotEq, None): _next_None,
    (Lt, None): _next_None,
    (LtE, None): _next_None,
    (Gt, None): _next_None,
    (GtE, None): _next_None,
    (Is, None): _next_None,
    (IsNot, None): _next_None,
    (In, None): _next_None,
    (NotIn, None): _next_None,
    (comprehension, None): _next_comprehension_START,
    (comprehension, 'target'): _next_comprehension_target,
    (comprehension, 'iter'): _next_comprehension_iter,
    (comprehension, 'ifs'): _next_comprehension_ifs,
    (ExceptHandler, None): _next_ExceptHandler_START,
    (ExceptHandler, 'type'): _next_ExceptHandler_type,
    (ExceptHandler, 'body'): _next_ExceptHandler_body,
    (arguments, None): _next_arguments_START,
    (arguments, 'posonlyargs'): _next_arguments_posonlyargs,
    (arguments, 'args'): _next_arguments_args,
    (arguments, 'defaults'): _next_arguments_defaults,
    (arguments, 'vararg'): _next_arguments_vararg,
    (arguments, 'kwonlyargs'): _next_arguments_kwonlyargs,
    (arguments, 'kw_defaults'): _next_arguments_kw_defaults,
    (arguments, 'kwarg'): _next_arguments_kwarg,
    (arg, None): _next_arg_START,
    (arg, 'annotation'): _next_None,
    (keyword, None): _next_keyword_START,
    (keyword, 'value'): _next_None,
    (alias, None): _next_None,
    (withitem, None): _next_withitem_START,
    (withitem, 'context_expr'): _next_withitem_context_expr,
    (withitem, 'optional_vars'): _next_None,
    (match_case, None): _next_match_case_START,
    (match_case, 'pattern'): _next_match_case_pattern,
    (match_case, 'guard'): _next_match_case_guard,
    (match_case, 'body'): _next_match_case_body,
    (MatchValue, None): _next_MatchValue_START,
    (MatchValue, 'value'): _next_None,
    (MatchSingleton, None): _next_None,
    (MatchSequence, None): _next_MatchSequence_START,
    (MatchSequence, 'patterns'): _next_MatchSequence_patterns,
    (MatchMapping, None): _next_MatchMapping_START,
    (MatchMapping, 'keys'): _next_MatchMapping_keys,
    (MatchMapping, 'patterns'): _next_MatchMapping_patterns,
    (MatchClass, None): _next_MatchClass_START,
    (MatchClass, 'cls'): _next_MatchClass_cls,
    (MatchClass, 'patterns'): _next_MatchClass_patterns,
    (MatchClass, 'kwd_patterns'): _next_MatchClass_kwd_patterns,
    (MatchStar, None): _next_None,
    (MatchAs, None): _next_MatchAs_START,
    (MatchAs, 'pattern'): _next_None,
    (MatchOr, None): _next_MatchOr_START,
    (MatchOr, 'patterns'): _next_MatchOr_patterns,
    (TypeIgnore, None): _next_None,
    (TypeVar, None): _next_TypeVar_START,
    (TypeVar, 'bound'): _next_TypeVar_bound,
    (TypeVar, 'default_value'): _next_TypeVar_default_value,
    (ParamSpec, None): _next_ParamSpec_START,
    (ParamSpec, 'default_value'): _next_ParamSpec_default_value,
    (TypeVarTuple, None): _next_TypeVarTuple_START,
    (TypeVarTuple, 'default_value'): _next_TypeVarTuple_default_value,
    (_ExceptHandlers, None): _next__ExceptHandlers_START,
    (_ExceptHandlers, 'handlers'): _next__ExceptHandlers_handlers,
    (_match_cases, None): _next__match_cases_START,
    (_match_cases, 'cases'): _next__match_cases_cases,
    (_Assign_targets, None): _next__Assign_targets_START,
    (_Assign_targets, 'targets'): _next__Assign_targets_targets,
    (_decorator_list, None): _next__decorator_list_START,
    (_decorator_list, 'decorator_list'): _next__decorator_list_decorator_list,
    (_arglikes, None): _next__arglikes_START,
    (_arglikes, 'arglikes'): _next__arglikes_arglikes,
    (_comprehensions, None): _next__comprehensions_START,
    (_comprehensions, 'generators'): _next__comprehensions_generators,
    (_comprehension_ifs, None): _next__comprehension_ifs_START,
    (_comprehension_ifs, 'ifs'): _next__comprehension_ifs_ifs,
    (_aliases, None): _next__aliases_START,
    (_aliases, 'names'): _next__aliases_names,
    (_withitems, None): _next__withitems_START,
    (_withitems, 'items'): _next__withitems_items,
    (_type_params, None): _next__type_params_START,
    (_type_params, 'type_params'): _next__type_params_type_params,
}
