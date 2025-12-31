"""`FST` class predicates for checking underlying `AST` node type.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from . import fst

from .asttypes import (
    Module,
    Interactive,
    Expression,
    FunctionType,
    FunctionDef,
    AsyncFunctionDef,
    ClassDef,
    Return,
    Delete,
    Assign,
    TypeAlias,
    AugAssign,
    AnnAssign,
    For,
    AsyncFor,
    While,
    If,
    With,
    AsyncWith,
    Match,
    Raise,
    Try,
    TryStar,
    Assert,
    Import,
    ImportFrom,
    Global,
    Nonlocal,
    Expr,
    Pass,
    Break,
    Continue,
    BoolOp,
    NamedExpr,
    BinOp,
    UnaryOp,
    Lambda,
    IfExp,
    Dict,
    Set,
    ListComp,
    SetComp,
    DictComp,
    GeneratorExp,
    Await,
    Yield,
    YieldFrom,
    Compare,
    Call,
    FormattedValue,
    Interpolation,
    JoinedStr,
    TemplateStr,
    Constant,
    Attribute,
    Subscript,
    Starred,
    Name,
    List,
    Tuple,
    Slice,
    Load,
    Store,
    Del,
    And,
    Or,
    Add,
    Sub,
    Mult,
    MatMult,
    Div,
    Mod,
    Pow,
    LShift,
    RShift,
    BitOr,
    BitXor,
    BitAnd,
    FloorDiv,
    Invert,
    Not,
    UAdd,
    USub,
    Eq,
    NotEq,
    Lt,
    LtE,
    Gt,
    GtE,
    Is,
    IsNot,
    In,
    NotIn,
    comprehension,
    ExceptHandler,
    arguments,
    arg,
    keyword,
    alias,
    withitem,
    match_case,
    MatchValue,
    MatchSingleton,
    MatchSequence,
    MatchMapping,
    MatchClass,
    MatchStar,
    MatchAs,
    MatchOr,
    TypeIgnore,
    TypeVar,
    ParamSpec,
    TypeVarTuple,
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

__all__ = [
    'is_Module',
    'is_Interactive',
    'is_Expression',
    'is_FunctionType',
    'is_FunctionDef',
    'is_AsyncFunctionDef',
    'is_ClassDef',
    'is_Return',
    'is_Delete',
    'is_Assign',
    'is_TypeAlias',
    'is_AugAssign',
    'is_AnnAssign',
    'is_For',
    'is_AsyncFor',
    'is_While',
    'is_If',
    'is_With',
    'is_AsyncWith',
    'is_Match',
    'is_Raise',
    'is_Try',
    'is_TryStar',
    'is_Assert',
    'is_Import',
    'is_ImportFrom',
    'is_Global',
    'is_Nonlocal',
    'is_Expr',
    'is_Pass',
    'is_Break',
    'is_Continue',
    'is_BoolOp',
    'is_NamedExpr',
    'is_BinOp',
    'is_UnaryOp',
    'is_Lambda',
    'is_IfExp',
    'is_Dict',
    'is_Set',
    'is_ListComp',
    'is_SetComp',
    'is_DictComp',
    'is_GeneratorExp',
    'is_Await',
    'is_Yield',
    'is_YieldFrom',
    'is_Compare',
    'is_Call',
    'is_FormattedValue',
    'is_Interpolation',
    'is_JoinedStr',
    'is_TemplateStr',
    'is_Constant',
    'is_Attribute',
    'is_Subscript',
    'is_Starred',
    'is_Name',
    'is_List',
    'is_Tuple',
    'is_Slice',
    'is_Load',
    'is_Store',
    'is_Del',
    'is_And',
    'is_Or',
    'is_Add',
    'is_Sub',
    'is_Mult',
    'is_MatMult',
    'is_Div',
    'is_Mod',
    'is_Pow',
    'is_LShift',
    'is_RShift',
    'is_BitOr',
    'is_BitXor',
    'is_BitAnd',
    'is_FloorDiv',
    'is_Invert',
    'is_Not',
    'is_UAdd',
    'is_USub',
    'is_Eq',
    'is_NotEq',
    'is_Lt',
    'is_LtE',
    'is_Gt',
    'is_GtE',
    'is_Is',
    'is_IsNot',
    'is_In',
    'is_NotIn',
    'is_comprehension',
    'is_ExceptHandler',
    'is_arguments',
    'is_arg',
    'is_keyword',
    'is_alias',
    'is_withitem',
    'is_match_case',
    'is_MatchValue',
    'is_MatchSingleton',
    'is_MatchSequence',
    'is_MatchMapping',
    'is_MatchClass',
    'is_MatchStar',
    'is_MatchAs',
    'is_MatchOr',
    'is_TypeIgnore',
    'is_TypeVar',
    'is_ParamSpec',
    'is_TypeVarTuple',
    'is__ExceptHandlers',
    'is__match_cases',
    'is__Assign_targets',
    'is__decorator_list',
    'is__arglikes',
    'is__comprehensions',
    'is__comprehension_ifs',
    'is__aliases',
    'is__withitems',
    'is__type_params',
]


@property
def is_Module(self: 'fst.FST') -> bool:
    """Is a `Module` node."""

    return self.a.__class__ is Module


@property
def is_Interactive(self: 'fst.FST') -> bool:
    """Is a `Interactive` node."""

    return self.a.__class__ is Interactive


@property
def is_Expression(self: 'fst.FST') -> bool:
    """Is a `Expression` node."""

    return self.a.__class__ is Expression


@property
def is_FunctionType(self: 'fst.FST') -> bool:
    """Is a `FunctionType` node."""

    return self.a.__class__ is FunctionType


@property
def is_FunctionDef(self: 'fst.FST') -> bool:
    """Is a `FunctionDef` node."""

    return self.a.__class__ is FunctionDef


@property
def is_AsyncFunctionDef(self: 'fst.FST') -> bool:
    """Is a `AsyncFunctionDef` node."""

    return self.a.__class__ is AsyncFunctionDef


@property
def is_ClassDef(self: 'fst.FST') -> bool:
    """Is a `ClassDef` node."""

    return self.a.__class__ is ClassDef


@property
def is_Return(self: 'fst.FST') -> bool:
    """Is a `Return` node."""

    return self.a.__class__ is Return


@property
def is_Delete(self: 'fst.FST') -> bool:
    """Is a `Delete` node."""

    return self.a.__class__ is Delete


@property
def is_Assign(self: 'fst.FST') -> bool:
    """Is a `Assign` node."""

    return self.a.__class__ is Assign


@property
def is_TypeAlias(self: 'fst.FST') -> bool:
    """Is a `TypeAlias` node."""

    return self.a.__class__ is TypeAlias


@property
def is_AugAssign(self: 'fst.FST') -> bool:
    """Is a `AugAssign` node."""

    return self.a.__class__ is AugAssign


@property
def is_AnnAssign(self: 'fst.FST') -> bool:
    """Is a `AnnAssign` node."""

    return self.a.__class__ is AnnAssign


@property
def is_For(self: 'fst.FST') -> bool:
    """Is a `For` node."""

    return self.a.__class__ is For


@property
def is_AsyncFor(self: 'fst.FST') -> bool:
    """Is a `AsyncFor` node."""

    return self.a.__class__ is AsyncFor


@property
def is_While(self: 'fst.FST') -> bool:
    """Is a `While` node."""

    return self.a.__class__ is While


@property
def is_If(self: 'fst.FST') -> bool:
    """Is a `If` node."""

    return self.a.__class__ is If


@property
def is_With(self: 'fst.FST') -> bool:
    """Is a `With` node."""

    return self.a.__class__ is With


@property
def is_AsyncWith(self: 'fst.FST') -> bool:
    """Is a `AsyncWith` node."""

    return self.a.__class__ is AsyncWith


@property
def is_Match(self: 'fst.FST') -> bool:
    """Is a `Match` node."""

    return self.a.__class__ is Match


@property
def is_Raise(self: 'fst.FST') -> bool:
    """Is a `Raise` node."""

    return self.a.__class__ is Raise


@property
def is_Try(self: 'fst.FST') -> bool:
    """Is a `Try` node."""

    return self.a.__class__ is Try


@property
def is_TryStar(self: 'fst.FST') -> bool:
    """Is a `TryStar` node."""

    return self.a.__class__ is TryStar


@property
def is_Assert(self: 'fst.FST') -> bool:
    """Is a `Assert` node."""

    return self.a.__class__ is Assert


@property
def is_Import(self: 'fst.FST') -> bool:
    """Is a `Import` node."""

    return self.a.__class__ is Import


@property
def is_ImportFrom(self: 'fst.FST') -> bool:
    """Is a `ImportFrom` node."""

    return self.a.__class__ is ImportFrom


@property
def is_Global(self: 'fst.FST') -> bool:
    """Is a `Global` node."""

    return self.a.__class__ is Global


@property
def is_Nonlocal(self: 'fst.FST') -> bool:
    """Is a `Nonlocal` node."""

    return self.a.__class__ is Nonlocal


@property
def is_Expr(self: 'fst.FST') -> bool:
    """Is a `Expr` node."""

    return self.a.__class__ is Expr


@property
def is_Pass(self: 'fst.FST') -> bool:
    """Is a `Pass` node."""

    return self.a.__class__ is Pass


@property
def is_Break(self: 'fst.FST') -> bool:
    """Is a `Break` node."""

    return self.a.__class__ is Break


@property
def is_Continue(self: 'fst.FST') -> bool:
    """Is a `Continue` node."""

    return self.a.__class__ is Continue


@property
def is_BoolOp(self: 'fst.FST') -> bool:
    """Is a `BoolOp` node."""

    return self.a.__class__ is BoolOp


@property
def is_NamedExpr(self: 'fst.FST') -> bool:
    """Is a `NamedExpr` node."""

    return self.a.__class__ is NamedExpr


@property
def is_BinOp(self: 'fst.FST') -> bool:
    """Is a `BinOp` node."""

    return self.a.__class__ is BinOp


@property
def is_UnaryOp(self: 'fst.FST') -> bool:
    """Is a `UnaryOp` node."""

    return self.a.__class__ is UnaryOp


@property
def is_Lambda(self: 'fst.FST') -> bool:
    """Is a `Lambda` node."""

    return self.a.__class__ is Lambda


@property
def is_IfExp(self: 'fst.FST') -> bool:
    """Is a `IfExp` node."""

    return self.a.__class__ is IfExp


@property
def is_Dict(self: 'fst.FST') -> bool:
    """Is a `Dict` node."""

    return self.a.__class__ is Dict


@property
def is_Set(self: 'fst.FST') -> bool:
    """Is a `Set` node."""

    return self.a.__class__ is Set


@property
def is_ListComp(self: 'fst.FST') -> bool:
    """Is a `ListComp` node."""

    return self.a.__class__ is ListComp


@property
def is_SetComp(self: 'fst.FST') -> bool:
    """Is a `SetComp` node."""

    return self.a.__class__ is SetComp


@property
def is_DictComp(self: 'fst.FST') -> bool:
    """Is a `DictComp` node."""

    return self.a.__class__ is DictComp


@property
def is_GeneratorExp(self: 'fst.FST') -> bool:
    """Is a `GeneratorExp` node."""

    return self.a.__class__ is GeneratorExp


@property
def is_Await(self: 'fst.FST') -> bool:
    """Is a `Await` node."""

    return self.a.__class__ is Await


@property
def is_Yield(self: 'fst.FST') -> bool:
    """Is a `Yield` node."""

    return self.a.__class__ is Yield


@property
def is_YieldFrom(self: 'fst.FST') -> bool:
    """Is a `YieldFrom` node."""

    return self.a.__class__ is YieldFrom


@property
def is_Compare(self: 'fst.FST') -> bool:
    """Is a `Compare` node."""

    return self.a.__class__ is Compare


@property
def is_Call(self: 'fst.FST') -> bool:
    """Is a `Call` node."""

    return self.a.__class__ is Call


@property
def is_FormattedValue(self: 'fst.FST') -> bool:
    """Is a `FormattedValue` node."""

    return self.a.__class__ is FormattedValue


@property
def is_Interpolation(self: 'fst.FST') -> bool:
    """Is a `Interpolation` node."""

    return self.a.__class__ is Interpolation


@property
def is_JoinedStr(self: 'fst.FST') -> bool:
    """Is a `JoinedStr` node."""

    return self.a.__class__ is JoinedStr


@property
def is_TemplateStr(self: 'fst.FST') -> bool:
    """Is a `TemplateStr` node."""

    return self.a.__class__ is TemplateStr


@property
def is_Constant(self: 'fst.FST') -> bool:
    """Is a `Constant` node."""

    return self.a.__class__ is Constant


@property
def is_Attribute(self: 'fst.FST') -> bool:
    """Is a `Attribute` node."""

    return self.a.__class__ is Attribute


@property
def is_Subscript(self: 'fst.FST') -> bool:
    """Is a `Subscript` node."""

    return self.a.__class__ is Subscript


@property
def is_Starred(self: 'fst.FST') -> bool:
    """Is a `Starred` node."""

    return self.a.__class__ is Starred


@property
def is_Name(self: 'fst.FST') -> bool:
    """Is a `Name` node."""

    return self.a.__class__ is Name


@property
def is_List(self: 'fst.FST') -> bool:
    """Is a `List` node."""

    return self.a.__class__ is List


@property
def is_Tuple(self: 'fst.FST') -> bool:
    """Is a `Tuple` node."""

    return self.a.__class__ is Tuple


@property
def is_Slice(self: 'fst.FST') -> bool:
    """Is a `Slice` node."""

    return self.a.__class__ is Slice


@property
def is_Load(self: 'fst.FST') -> bool:
    """Is a `Load` node."""

    return self.a.__class__ is Load


@property
def is_Store(self: 'fst.FST') -> bool:
    """Is a `Store` node."""

    return self.a.__class__ is Store


@property
def is_Del(self: 'fst.FST') -> bool:
    """Is a `Del` node."""

    return self.a.__class__ is Del


@property
def is_And(self: 'fst.FST') -> bool:
    """Is a `And` node."""

    return self.a.__class__ is And


@property
def is_Or(self: 'fst.FST') -> bool:
    """Is a `Or` node."""

    return self.a.__class__ is Or


@property
def is_Add(self: 'fst.FST') -> bool:
    """Is a `Add` node."""

    return self.a.__class__ is Add


@property
def is_Sub(self: 'fst.FST') -> bool:
    """Is a `Sub` node."""

    return self.a.__class__ is Sub


@property
def is_Mult(self: 'fst.FST') -> bool:
    """Is a `Mult` node."""

    return self.a.__class__ is Mult


@property
def is_MatMult(self: 'fst.FST') -> bool:
    """Is a `MatMult` node."""

    return self.a.__class__ is MatMult


@property
def is_Div(self: 'fst.FST') -> bool:
    """Is a `Div` node."""

    return self.a.__class__ is Div


@property
def is_Mod(self: 'fst.FST') -> bool:
    """Is a `Mod` node."""

    return self.a.__class__ is Mod


@property
def is_Pow(self: 'fst.FST') -> bool:
    """Is a `Pow` node."""

    return self.a.__class__ is Pow


@property
def is_LShift(self: 'fst.FST') -> bool:
    """Is a `LShift` node."""

    return self.a.__class__ is LShift


@property
def is_RShift(self: 'fst.FST') -> bool:
    """Is a `RShift` node."""

    return self.a.__class__ is RShift


@property
def is_BitOr(self: 'fst.FST') -> bool:
    """Is a `BitOr` node."""

    return self.a.__class__ is BitOr


@property
def is_BitXor(self: 'fst.FST') -> bool:
    """Is a `BitXor` node."""

    return self.a.__class__ is BitXor


@property
def is_BitAnd(self: 'fst.FST') -> bool:
    """Is a `BitAnd` node."""

    return self.a.__class__ is BitAnd


@property
def is_FloorDiv(self: 'fst.FST') -> bool:
    """Is a `FloorDiv` node."""

    return self.a.__class__ is FloorDiv


@property
def is_Invert(self: 'fst.FST') -> bool:
    """Is a `Invert` node."""

    return self.a.__class__ is Invert


@property
def is_Not(self: 'fst.FST') -> bool:
    """Is a `Not` node."""

    return self.a.__class__ is Not


@property
def is_UAdd(self: 'fst.FST') -> bool:
    """Is a `UAdd` node."""

    return self.a.__class__ is UAdd


@property
def is_USub(self: 'fst.FST') -> bool:
    """Is a `USub` node."""

    return self.a.__class__ is USub


@property
def is_Eq(self: 'fst.FST') -> bool:
    """Is a `Eq` node."""

    return self.a.__class__ is Eq


@property
def is_NotEq(self: 'fst.FST') -> bool:
    """Is a `NotEq` node."""

    return self.a.__class__ is NotEq


@property
def is_Lt(self: 'fst.FST') -> bool:
    """Is a `Lt` node."""

    return self.a.__class__ is Lt


@property
def is_LtE(self: 'fst.FST') -> bool:
    """Is a `LtE` node."""

    return self.a.__class__ is LtE


@property
def is_Gt(self: 'fst.FST') -> bool:
    """Is a `Gt` node."""

    return self.a.__class__ is Gt


@property
def is_GtE(self: 'fst.FST') -> bool:
    """Is a `GtE` node."""

    return self.a.__class__ is GtE


@property
def is_Is(self: 'fst.FST') -> bool:
    """Is a `Is` node."""

    return self.a.__class__ is Is


@property
def is_IsNot(self: 'fst.FST') -> bool:
    """Is a `IsNot` node."""

    return self.a.__class__ is IsNot


@property
def is_In(self: 'fst.FST') -> bool:
    """Is a `In` node."""

    return self.a.__class__ is In


@property
def is_NotIn(self: 'fst.FST') -> bool:
    """Is a `NotIn` node."""

    return self.a.__class__ is NotIn


@property
def is_comprehension(self: 'fst.FST') -> bool:
    """Is a `comprehension` node."""

    return self.a.__class__ is comprehension


@property
def is_ExceptHandler(self: 'fst.FST') -> bool:
    """Is a `ExceptHandler` node."""

    return self.a.__class__ is ExceptHandler


@property
def is_arguments(self: 'fst.FST') -> bool:
    """Is a `arguments` node."""

    return self.a.__class__ is arguments


@property
def is_arg(self: 'fst.FST') -> bool:
    """Is a `arg` node."""

    return self.a.__class__ is arg


@property
def is_keyword(self: 'fst.FST') -> bool:
    """Is a `keyword` node."""

    return self.a.__class__ is keyword


@property
def is_alias(self: 'fst.FST') -> bool:
    """Is a `alias` node."""

    return self.a.__class__ is alias


@property
def is_withitem(self: 'fst.FST') -> bool:
    """Is a `withitem` node."""

    return self.a.__class__ is withitem


@property
def is_match_case(self: 'fst.FST') -> bool:
    """Is a `match_case` node."""

    return self.a.__class__ is match_case


@property
def is_MatchValue(self: 'fst.FST') -> bool:
    """Is a `MatchValue` node."""

    return self.a.__class__ is MatchValue


@property
def is_MatchSingleton(self: 'fst.FST') -> bool:
    """Is a `MatchSingleton` node."""

    return self.a.__class__ is MatchSingleton


@property
def is_MatchSequence(self: 'fst.FST') -> bool:
    """Is a `MatchSequence` node."""

    return self.a.__class__ is MatchSequence


@property
def is_MatchMapping(self: 'fst.FST') -> bool:
    """Is a `MatchMapping` node."""

    return self.a.__class__ is MatchMapping


@property
def is_MatchClass(self: 'fst.FST') -> bool:
    """Is a `MatchClass` node."""

    return self.a.__class__ is MatchClass


@property
def is_MatchStar(self: 'fst.FST') -> bool:
    """Is a `MatchStar` node."""

    return self.a.__class__ is MatchStar


@property
def is_MatchAs(self: 'fst.FST') -> bool:
    """Is a `MatchAs` node."""

    return self.a.__class__ is MatchAs


@property
def is_MatchOr(self: 'fst.FST') -> bool:
    """Is a `MatchOr` node."""

    return self.a.__class__ is MatchOr


@property
def is_TypeIgnore(self: 'fst.FST') -> bool:
    """Is a `TypeIgnore` node."""

    return self.a.__class__ is TypeIgnore


@property
def is_TypeVar(self: 'fst.FST') -> bool:
    """Is a `TypeVar` node."""

    return self.a.__class__ is TypeVar


@property
def is_ParamSpec(self: 'fst.FST') -> bool:
    """Is a `ParamSpec` node."""

    return self.a.__class__ is ParamSpec


@property
def is_TypeVarTuple(self: 'fst.FST') -> bool:
    """Is a `TypeVarTuple` node."""

    return self.a.__class__ is TypeVarTuple


@property
def is__ExceptHandlers(self: 'fst.FST') -> bool:
    """Is a `_ExceptHandlers` node."""

    return self.a.__class__ is _ExceptHandlers


@property
def is__match_cases(self: 'fst.FST') -> bool:
    """Is a `_match_cases` node."""

    return self.a.__class__ is _match_cases


@property
def is__Assign_targets(self: 'fst.FST') -> bool:
    """Is a `_Assign_targets` node."""

    return self.a.__class__ is _Assign_targets


@property
def is__decorator_list(self: 'fst.FST') -> bool:
    """Is a `_decorator_list` node."""

    return self.a.__class__ is _decorator_list


@property
def is__arglikes(self: 'fst.FST') -> bool:
    """Is a `_arglikes` node."""

    return self.a.__class__ is _arglikes


@property
def is__comprehensions(self: 'fst.FST') -> bool:
    """Is a `_comprehensions` node."""

    return self.a.__class__ is _comprehensions


@property
def is__comprehension_ifs(self: 'fst.FST') -> bool:
    """Is a `_comprehension_ifs` node."""

    return self.a.__class__ is _comprehension_ifs


@property
def is__aliases(self: 'fst.FST') -> bool:
    """Is a `_aliases` node."""

    return self.a.__class__ is _aliases


@property
def is__withitems(self: 'fst.FST') -> bool:
    """Is a `_withitems` node."""

    return self.a.__class__ is _withitems


@property
def is__type_params(self: 'fst.FST') -> bool:
    """Is a `_type_params` node."""

    return self.a.__class__ is _type_params
