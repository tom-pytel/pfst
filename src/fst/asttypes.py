"""AST types and standins (for `isinstance()` use). Also custom fst AST slice types."""

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
    '_ExceptHandlers',
    '_match_cases',
    '_Assign_targets',
    '_decorator_list',
    '_comprehensions',
    '_comprehension_ifs',
    # '_keywords',
    '_aliases',
    '_withitems',
    '_type_params',
]


ASTS_EXPRISH            = (expr, comprehension, arguments, arg, keyword)  # can be in expression chain (have expressions above)
ASTS_EXPRISH_ALL        = ASTS_EXPRISH + (expr_context, boolop, operator, unaryop, cmpop)
ASTS_STMTISH            = (stmt, ExceptHandler, match_case)  # always in lists, cannot be inside multilines
ASTS_STMTISH_OR_MOD     = ASTS_STMTISH + (mod,)
ASTS_STMTISH_OR_STMTMOD = ASTS_STMTISH + (Module, Interactive)
ASTS_BLOCK              = (FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If, With, AsyncWith, Match,
                           Try, TryStar, ExceptHandler, match_case)
ASTS_BLOCK_OR_MOD       = ASTS_BLOCK + (mod,)
ASTS_SCOPE              = (FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp, GeneratorExp)
ASTS_SCOPE_OR_MOD       = ASTS_SCOPE + (mod,)
ASTS_SCOPE_NAMED        = (FunctionDef, AsyncFunctionDef, ClassDef)
ASTS_SCOPE_NAMED_OR_MOD = ASTS_SCOPE_NAMED + (mod,)
ASTS_SCOPE_ANONYMOUS    = (Lambda, ListComp, SetComp, DictComp, GeneratorExp)

ASTS_MAYBE_DOCSTR       = ASTS_SCOPE_NAMED + (Module,)  # these may have a docstring as the first Const str Expr in the body
# ASTS_MAYBE_SINGLETON    = (expr_context, unaryop, operator, boolop, cmpop)  # the same object may be reused by ast.parse() in mutiple places in the tree


class _slice(AST):
    """General non-AST-compatible slice of some `type[AST]` list field. This is not generally usable as an `AST` and
    will not `ast.unparse()` correctly (though `FST.parsex.unparse()` will unparse correctly). Meant only to be used
    as a container with `FST` taking care of source and all operations.

    **Note:** This class has nothing to do with `ast.slice` or `ast.Slice`, those are indices, this is a slice
    CONTAINER.
    """

    _fields        = ()
    _attributes    = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')
    end_lineno     = None
    end_col_offset = None


class _ExceptHandlers(_slice):
    """Slice of `ExceptHandler`s.

    This is a special slice because we just want the handlers and no `try`."""

    _fields      = ('handlers',)
    _field_types = {'handlers': list[ExceptHandler]}

    def __init__(
        self,
        handlers: list[ExceptHandler],
        lineno: int = 1,
        col_offset: int = 0,
        end_lineno: int = 1,
        end_col_offset: int = 0,
    ) -> None:
        self.handlers = handlers
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _match_cases(_slice):
    """Slice of `match_case`s.

    This is a special slice because we just want the cases and no `match`."""

    _fields      = ('cases',)
    _field_types = {'cases': list[match_case]}

    def __init__(
        self,
        cases: list[match_case],
        lineno: int = 1,
        col_offset: int = 0,
        end_lineno: int = 1,
        end_col_offset: int = 0,
    ) -> None:
        self.cases = cases
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _Assign_targets(_slice):
    """Slice of `Assign.targets`.

    This is a special slice because separator is `=`."""

    _fields      = ('targets',)
    _field_types = {'targets': list[expr]}

    def __init__(
        self, targets: list[expr], lineno: int = 1, col_offset: int = 0, end_lineno: int = 1, end_col_offset: int = 0
    ) -> None:
        self.targets = targets
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _decorator_list(_slice):
    """Slice of `FunctionDef/AsyncFunctionDef/ClassDef.decorator_list`.

    This is a special slice because there are no separators and instead each element is prefixed with `@` which must be
    at column 0 of its line."""

    _fields      = ('decorator_list',)
    _field_types = {'decorator_list': list[expr]}

    def __init__(
        self,
        decorator_list: list[expr],
        lineno: int = 1,
        col_offset: int = 0,
        end_lineno: int = 1,
        end_col_offset: int = 0
    ) -> None:
        self.decorator_list = decorator_list
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _comprehensions(_slice):
    """Slice of `ListComp/SetComp/DictComp/GeneratorExp.generators`.

    This is a special slice because elements are `comprehension` and there are no separators and instead each
    `comprehension` is prefixed with `for` or `async for`."""

    _fields      = ('generators',)
    _field_types = {'generators': list[comprehension]}

    def __init__(
        self,
        generators: list[comprehension],
        lineno: int = 1,
        col_offset: int = 0,
        end_lineno: int = 1,
        end_col_offset: int = 0,
    ) -> None:
        self.generators = generators
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _comprehension_ifs(_slice):
    """Slice of `comprehension.ifs`.

    This is a special slice because there are no separators and instead each element is prefixed with `if` which is not
    included in each expression's location so needs special treatment."""

    _fields      = ('ifs',)
    _field_types = {'ifs': list[expr]}

    def __init__(
        self,
        ifs: list[expr],
        lineno: int = 1,
        col_offset: int = 0,
        end_lineno: int = 1,
        end_col_offset: int = 0,
    ) -> None:
        self.ifs = ifs
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


# class _keywords(_slice):
#     """Slice of `ClassDef/Call.keywords`.

#     This is a special slice because elements are `keyword`."""


class _aliases(_slice):
    """Slice of `Import/ImportFrom.names`.

    This is a special slice because elements are `alias`."""

    _fields      = ('names',)
    _field_types = {'names': list[alias]}

    def __init__(
        self, names: list[alias], lineno: int = 1, col_offset: int = 0, end_lineno: int = 1, end_col_offset: int = 0
    ) -> None:
        self.names = names
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _withitems(_slice):
    """Slice of `With/AsyncWith.items`.

    This is a special slice because elements are `withitem`."""

    _fields      = ('items',)
    _field_types = {'items': list[withitem]}

    def __init__(
        self, items: list[withitem], lineno: int = 1, col_offset: int = 0, end_lineno: int = 1, end_col_offset: int = 0
    ) -> None:
        self.items = items
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset


class _type_params(_slice):
    """Slice of `FunctionDef/AsyncFunctionDef/ClassDef/TypeAlias.type_params`.

    This is a special slice because elements are `type_param`."""

    _fields      = ('type_params',)
    _field_types = {'type_params': list[type_param]}

    def __init__(
        self,
        type_params: list[type_param],
        lineno: int = 1,
        col_offset: int = 0,
        end_lineno: int = 1,
        end_col_offset: int = 0,
    ) -> None:
        self.type_params = type_params
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset
