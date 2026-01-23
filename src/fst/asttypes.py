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

# create standin dummy AST types if they don't exist, mostly for isinstance() checks

class _ASTStandin(AST):
    def __init__(self, *args: object, **kwargs) -> None:
        raise RuntimeError("this is a standin class for an AST type that doesn't exist in this version of python, "
                           "it should not be instantiated")  # pragma: no cover

if sys.version_info[:2] >= (3, 11):
    from ast import TryStar
else:
    class TryStar(_ASTStandin): """Standin."""  # should we try to duplicate params? opening up possible can of descent into madness there

if sys.version_info[:2] >= (3, 12):
    from ast import TypeAlias, type_param, TypeVar, ParamSpec, TypeVarTuple
else:
    class TypeAlias(_ASTStandin): """Standin."""
    class type_param(_ASTStandin): """Standin."""
    class TypeVar(_ASTStandin): """Standin."""
    class ParamSpec(_ASTStandin): """Standin."""
    class TypeVarTuple(_ASTStandin): """Standin."""

if sys.version_info[:2] >= (3, 14):
    from ast import TemplateStr, Interpolation
else:
    class TemplateStr(_ASTStandin): """Standin."""
    class Interpolation(_ASTStandin): """Standin."""

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
    '_arglikes',
    '_comprehensions',
    '_comprehension_ifs',
    '_aliases',
    '_withitems',
    '_type_params',

    'ASTS_LEAF_MOD',
    'ASTS_LEAF_STMTMOD',
    'ASTS_LEAF_STMT',
    'ASTS_LEAF_EXPR',
    'ASTS_LEAF_EXPR_STD',
    'ASTS_LEAF_EXPR_CONTEXT',
    'ASTS_LEAF_BOOLOP',
    'ASTS_LEAF_OPERATOR',
    'ASTS_LEAF_UNARYOP',
    'ASTS_LEAF_CMPOP',
    'ASTS_LEAF_PATTERN',
    'ASTS_LEAF_TYPE_PARAM',
    'ASTS_LEAF_STMT_OR_MOD',
    'ASTS_LEAF_STMT_OR_STMTMOD',
    'ASTS_LEAF_EXPR_OR_PATTERN',
    'ASTS_LEAF_EXPR_STMT_OR_MOD',
    'ASTS_LEAF_EXPR_CHAIN',
    'ASTS_LEAF_STMTLIKE',
    'ASTS_LEAF_STMTLIKE_OR_MOD',
    'ASTS_LEAF_BLOCK',
    'ASTS_LEAF_BLOCK_OR_MOD',
    'ASTS_LEAF_SCOPE',
    'ASTS_LEAF_SCOPE_OR_MOD',
    'ASTS_LEAF_SCOPE_NAMED',
    'ASTS_LEAF_SCOPE_NAMED_OR_MOD',
    'ASTS_LEAF_SCOPE_ANON',
    'ASTS_LEAF_FUNCDEF',
    'ASTS_LEAF_DEF',
    'ASTS_LEAF_DEF_OR_MOD',
    'ASTS_LEAF_FOR',
    'ASTS_LEAF_WITH',
    'ASTS_LEAF_TRY',
    'ASTS_LEAF_IMPORT',
    'ASTS_LEAF_VAR_SCOPE_DECL',
    'ASTS_LEAF_YIELD',
    'ASTS_LEAF_TUPLE_LIST_OR_SET',
    'ASTS_LEAF_TUPLE_OR_LIST',
    'ASTS_LEAF_LIST_OR_SET',
    'ASTS_LEAF_COMP',
    'ASTS_LEAF_FTSTR',
    'ASTS_LEAF_FTSTR_FMT',
    'ASTS_LEAF_FTSTR_FMT_OR_SLICE',
    'ASTS_LEAF_ARGLIKE',
    'ASTS_LEAF_DELIMITED',
    'ASTS_LEAF_OP_NON_BOOL',
    'ASTS_LEAF_OP',
    'ASTS_LEAF_CMPOP_TWO_WORD',
    'ASTS_LEAF_CMPOP_ONE_WORD',
    'ASTS_LEAF_MAYBE_DOCSTR',
    'ASTS_LEAF__SLICE',
]


# leaf node types, as set for quick checks, must be frozenset() as some code depends on this for checks

ASTS_LEAF_MOD                = frozenset([Module, Interactive, Expression])
ASTS_LEAF_STMTMOD            = frozenset([Module, Interactive])

ASTS_LEAF_STMT               = frozenset([FunctionDef, AsyncFunctionDef, ClassDef, Return, Delete, Assign, TypeAlias,
                                          AugAssign, AnnAssign, For, AsyncFor, While, If, With, AsyncWith, Match, Raise,
                                          Try, TryStar, Assert, Import, ImportFrom, Global, Nonlocal, Expr, Pass, Break,
                                          Continue])

ASTS_LEAF_EXPR               = frozenset([BoolOp, NamedExpr, BinOp, UnaryOp, Lambda, IfExp, Dict, Set, ListComp,
                                          SetComp, DictComp, GeneratorExp, Await, Yield, YieldFrom, Compare, Call,
                                          FormattedValue, Interpolation, JoinedStr, TemplateStr, Constant, Attribute,
                                          Subscript, Starred, Name, List, Tuple, Slice])

ASTS_LEAF_EXPR_STD           = ASTS_LEAF_EXPR - frozenset([FormattedValue, Interpolation, Slice])

ASTS_LEAF_EXPR_CONTEXT       = frozenset([Load, Store, Del])
ASTS_LEAF_BOOLOP             = frozenset([And, Or])
ASTS_LEAF_OPERATOR           = frozenset([Add, Sub, Mult, MatMult, Div, Mod, Pow, LShift, RShift, BitOr, BitXor, BitAnd,
                                          FloorDiv])
ASTS_LEAF_UNARYOP            = frozenset([Invert, Not, UAdd, USub])
ASTS_LEAF_CMPOP              = frozenset([Eq, NotEq, Lt, LtE, Gt, GtE, Is, IsNot, In, NotIn])
ASTS_LEAF_PATTERN            = frozenset([MatchValue, MatchSingleton, MatchSequence, MatchMapping, MatchClass,
                                          MatchStar, MatchAs, MatchOr])
ASTS_LEAF_TYPE_PARAM         = frozenset([TypeVar, ParamSpec, TypeVarTuple])

ASTS_LEAF_STMT_OR_MOD        = ASTS_LEAF_STMT | ASTS_LEAF_MOD
ASTS_LEAF_STMT_OR_STMTMOD    = ASTS_LEAF_STMT_OR_MOD - {Expression}
ASTS_LEAF_EXPR_OR_PATTERN    = ASTS_LEAF_EXPR | ASTS_LEAF_PATTERN
ASTS_LEAF_EXPR_STMT_OR_MOD   = ASTS_LEAF_EXPR | ASTS_LEAF_STMT | ASTS_LEAF_MOD
ASTS_LEAF_EXPR_CHAIN         = ASTS_LEAF_EXPR | {comprehension, arguments, arg, keyword}  # can be in expression chain (have expressions ABOVE as well as below), this excludes withitem and patterns

ASTS_LEAF_STMTLIKE           = ASTS_LEAF_STMT | {ExceptHandler, match_case}
ASTS_LEAF_STMTLIKE_OR_MOD    = ASTS_LEAF_STMTLIKE | ASTS_LEAF_MOD

ASTS_LEAF_BLOCK              = frozenset([FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If, With,
                                          AsyncWith, Match, Try, TryStar, ExceptHandler, match_case])
ASTS_LEAF_BLOCK_OR_MOD       = ASTS_LEAF_BLOCK | ASTS_LEAF_MOD

ASTS_LEAF_SCOPE              = frozenset([FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp,
                                          GeneratorExp])
ASTS_LEAF_SCOPE_OR_MOD       = ASTS_LEAF_SCOPE | ASTS_LEAF_MOD
ASTS_LEAF_SCOPE_NAMED        = frozenset([FunctionDef, AsyncFunctionDef, ClassDef])
ASTS_LEAF_SCOPE_NAMED_OR_MOD = ASTS_LEAF_SCOPE_NAMED | ASTS_LEAF_MOD
ASTS_LEAF_SCOPE_ANON         = frozenset([Lambda, ListComp, SetComp, DictComp, GeneratorExp])

ASTS_LEAF_FUNCDEF            = frozenset([FunctionDef, AsyncFunctionDef])
ASTS_LEAF_DEF                = ASTS_LEAF_FUNCDEF | {ClassDef}
ASTS_LEAF_DEF_OR_MOD         = ASTS_LEAF_DEF | ASTS_LEAF_MOD
ASTS_LEAF_FOR                = frozenset([For, AsyncFor])
ASTS_LEAF_WITH               = frozenset([With, AsyncWith])
ASTS_LEAF_TRY                = frozenset([Try, TryStar])
ASTS_LEAF_IMPORT             = frozenset([Import, ImportFrom])
ASTS_LEAF_VAR_SCOPE_DECL     = frozenset([Global, Nonlocal])

ASTS_LEAF_YIELD              = frozenset([Yield, YieldFrom])

ASTS_LEAF_TUPLE_LIST_OR_SET  = frozenset([Tuple, List, Set])
ASTS_LEAF_TUPLE_OR_LIST      = frozenset([Tuple, List])
ASTS_LEAF_LIST_OR_SET        = frozenset([List, Set])

ASTS_LEAF_COMP               = frozenset([ListComp, SetComp, DictComp, GeneratorExp])
ASTS_LEAF_FTSTR              = frozenset([JoinedStr, TemplateStr])
ASTS_LEAF_FTSTR_FMT          = frozenset([FormattedValue, Interpolation])
ASTS_LEAF_FTSTR_FMT_OR_SLICE = ASTS_LEAF_FTSTR_FMT | {Slice}

ASTS_LEAF_ARGLIKE            = ASTS_LEAF_EXPR - ASTS_LEAF_FTSTR_FMT_OR_SLICE | {keyword}
ASTS_LEAF_DELIMITED          = frozenset([Tuple, List, Set, Dict, MatchSequence, MatchMapping,
                                          ListComp, SetComp, DictComp, GeneratorExp])

ASTS_LEAF_OP_NON_BOOL        = ASTS_LEAF_OPERATOR | ASTS_LEAF_UNARYOP | ASTS_LEAF_CMPOP
ASTS_LEAF_OP                 = ASTS_LEAF_OP_NON_BOOL | ASTS_LEAF_BOOLOP
ASTS_LEAF_CMPOP_TWO_WORD     = frozenset([IsNot, NotIn])
ASTS_LEAF_CMPOP_ONE_WORD     = ASTS_LEAF_CMPOP - ASTS_LEAF_CMPOP_TWO_WORD

ASTS_LEAF_MAYBE_DOCSTR       = ASTS_LEAF_SCOPE_NAMED | {Module}  # these may have a docstring as the first Const str Expr in the body, we specifically leave out Interactive because... its not a Module?

# ASTS_LEAF_MAYBE_SINGLETON    = (ASTS_LEAF_EXPR_CONTEXT | ASTS_LEAF_BOOLOP | ASTS_LEAF_OPERATOR | ASTS_LEAF_UNARYOP
#                                 | ASTS_LEAF_CMPOP)  # the same object may be reused by ast.parse() in mutiple places in the tree


class _slice(AST):  # SPECIAL SLICE base type
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


class _arglikes(_slice):
    """Slice of arglike expressions and keywords possibly intermixed (only permitted sequences). Used for
    `Call.args+keywords` or `ClassDef.bases+keywords` as `expr_arglike` and `keyword`.

    This is a special slice because elements can be mixed `expr` (arglike) and / or `keyword`."""

    _fields      = ('arglikes',)
    _field_types = {'arglikes': list[expr | keyword]}

    def __init__(
        self,
        arglikes: list[expr | keyword],
        lineno: int = 1,
        col_offset: int = 0,
        end_lineno: int = 1,
        end_col_offset: int = 0,
    ) -> None:
        self.arglikes = arglikes
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


ASTS_LEAF__SLICE = frozenset([_ExceptHandlers, _match_cases, _Assign_targets, _decorator_list, _arglikes,
                              _comprehensions, _comprehension_ifs, _aliases, _withitems, _type_params])


# remove nonexistent nodes in lower versions of python from ASTS_LEAF_* sets

if sys.version_info[:2] < (3, 11):
    _REMOVE = {TemplateStr, Interpolation,
               TypeAlias, type_param, TypeVar, ParamSpec, TypeVarTuple,
               TryStar}

elif sys.version_info[:2] < (3, 12):
    _REMOVE = {TemplateStr, Interpolation,
               TypeAlias, type_param, TypeVar, ParamSpec, TypeVarTuple}

elif sys.version_info[:2] < (3, 14):
    _REMOVE = {TemplateStr, Interpolation}

else:
    _REMOVE = None

if _REMOVE:
    _GLOBALS = globals()

    for _n, _v in list(_GLOBALS.items()):
        if _n.startswith('ASTS_LEAF_'):
            _GLOBALS[_n] = _v - _REMOVE
