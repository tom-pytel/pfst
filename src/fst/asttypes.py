"""AST types and standins (for `isinstance()` use)."""

import sys

from ast import (
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
    boolop,
    cmpop,
    comprehension,
    excepthandler,
    expr,
    expr_context,
    keyword,
    match_case,
    mod,
    operator,
    pattern,
    stmt,
    type_ignore,
    unaryop,
    withitem,
)

if sys.version_info[:2] >= (3, 11):  # for isinstance() checks
    from ast import TryStar

else:
    class TryStar(AST): """Standin."""  # should we try to duplicate params? opening up possible can of descent into madness there

if sys.version_info[:2] >= (3, 12):
    from ast import TypeAlias, type_param, TypeVar, ParamSpec, TypeVarTuple

else:
    class TypeAlias(AST): """Standin."""
    class type_param(AST): """Standin."""
    class TypeVar(AST): """Standin."""
    class ParamSpec(AST): """Standin."""
    class TypeVarTuple(AST): """Standin."""

if sys.version_info[:2] >= (3, 14):
    from ast import TemplateStr, Interpolation

else:
    class TemplateStr(AST): """Standin."""
    class Interpolation(AST): """Standin."""

__all__ = [
    'AST',
    'Add',
    'And',
    'AnnAssign',
    'Assert',
    'Assign',
    'AsyncFor',
    'AsyncFunctionDef',
    'AsyncWith',
    'Attribute',
    'AugAssign',
    'Await',
    'BinOp',
    'BitAnd',
    'BitOr',
    'BitXor',
    'BoolOp',
    'Break',
    'Call',
    'ClassDef',
    'Compare',
    'Constant',
    'Continue',
    'Del',
    'Delete',
    'Dict',
    'DictComp',
    'Div',
    'Eq',
    'ExceptHandler',
    'Expr',
    'Expression',
    'FloorDiv',
    'For',
    'FormattedValue',
    'FunctionDef',
    'FunctionType',
    'GeneratorExp',
    'Global',
    'Gt',
    'GtE',
    'If',
    'IfExp',
    'Import',
    'ImportFrom',
    'In',
    'Interactive',
    'Invert',
    'Is',
    'IsNot',
    'JoinedStr',
    'LShift',
    'Lambda',
    'List',
    'ListComp',
    'Load',
    'Lt',
    'LtE',
    'MatMult',
    'Match',
    'MatchAs',
    'MatchClass',
    'MatchMapping',
    'MatchOr',
    'MatchSequence',
    'MatchSingleton',
    'MatchStar',
    'MatchValue',
    'Mod',
    'Module',
    'Mult',
    'Name',
    'NamedExpr',
    'Nonlocal',
    'Not',
    'NotEq',
    'NotIn',
    'Or',
    'Pass',
    'Pow',
    'RShift',
    'Raise',
    'Return',
    'Set',
    'SetComp',
    'Slice',
    'Starred',
    'Store',
    'Sub',
    'Subscript',
    'Try',
    'Tuple',
    'TypeIgnore',
    'UAdd',
    'USub',
    'UnaryOp',
    'While',
    'With',
    'Yield',
    'YieldFrom',
    'alias',
    'arg',
    'arguments',
    'boolop',
    'cmpop',
    'comprehension',
    'excepthandler',
    'expr',
    'expr_context',
    'keyword',
    'match_case',
    'mod',
    'operator',
    'pattern',
    'stmt',
    'type_ignore',
    'unaryop',
    'withitem',

    'TryStar',

    'TypeAlias',
    'type_param',
    'TypeVar',
    'ParamSpec',
    'TypeVarTuple',

    'TemplateStr',
    'Interpolation',

    '_slice',
    # '_slice_ExceptHandlers',
    # '_slice_match_cases',
    '_slice_Assign_targets',
    # '_slice_decorator_list',
    # '_slice_comprehensions',
    # '_slice_comprehension_ifs',
    # '_slice_keywords',
    '_slice_aliases',
    '_slice_withitems',
    '_slice_type_params',
]


class _slice(AST):
    """General non-AST-compatible slice of some `type[AST]` list field. This is not generally usable as an `AST` and
    will not `ast.unparse()` correctly (though `FST.parsex.unparse()` will unparse correctly). Meant only to be used
    as a container with `FST` taking care of source and all operations.

    **Note:** This class has nothing to do with `ast.slice` or `ast.Slice`, thise are indices, this is a slice
    CONTAINER.
    """

    _fields        = ()
    _attributes    = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')
    end_lineno     = None
    end_col_offset = None


class _slice_Assign_targets(_slice):
    """Slice of `Assign.targets`.

    This is a special slice because separator is `=`."""

    _fields      = ('targets',)
    _field_types = {'targets': list[expr]}

    def __init__(self, targets: list[expr], lineno: int = 1, col_offset: int = 0, end_lineno: int = 1,
                 end_col_offset: int = 0):
        self.targets = targets or []
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


# class _slice_decorator_list(_slice):
#     """Slice of `FunctionDef/AsyncFunctionDef/ClassDef.decorator_list`.

#     This is a special slice because there are no separators and instead each element is prefixed with `@` which must be
#     at column 0 of its line."""


# class _slice_comprehensions(_slice):
#     """Slice of `ListComp/SetComp/DictComp/GeneratorExp.generators`.

#     This is a special slice because elements are `comprehension` and there are no separators and instead each
#     `comprehension` is prefixed with `for` or `async for`."""


# class _slice_comprehension_ifs(_slice):
#     """Slice of `comprehension.ifs`.

#     This is a special slice because there are no separators and instead each element is prefixed with `if`."""


# class _slice_keywords(_slice):
#     """Slice of `ClassDef/Call.keywords`.

#     This is a special slice because elements are `keyword`."""


class _slice_aliases(_slice):
    """Slice of `Import/ImportFrom.names`.

    This is a special slice because elements are `alias`."""

    _fields      = ('names',)
    _field_types = {'names': list[alias]}

    def __init__(self, names: list[alias], lineno: int = 1, col_offset: int = 0, end_lineno: int = 1,
                 end_col_offset: int = 0):
        self.names = names or []
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _slice_withitems(_slice):
    """Slice of `With/AsyncWith.items`.

    This is a special slice because elements are `withitem`."""

    _fields      = ('items',)
    _field_types = {'items': list[withitem]}

    def __init__(self, items: list[withitem], lineno: int = 1, col_offset: int = 0, end_lineno: int = 1,
                 end_col_offset: int = 0):
        self.items = items or []
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _slice_type_params(_slice):
    """Slice of `FunctionDef/AsyncFunctionDef/ClassDef/TypeAlias.type_params`.

    This is a special slice because elements are `type_param`."""

    _fields      = ('type_params',)
    _field_types = {'type_params': list[type_param]}

    def __init__(self, type_params: list[type_param], lineno: int = 1, col_offset: int = 0, end_lineno: int = 1,
                 end_col_offset: int = 0):
        self.type_params = type_params or []
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset
