"""FST matcher. Uses `AST` nodes for patterns but supplies some new `AST` types to allow creation of base types without
having to provide all the needed fields. Ellipsis is used in patterns as a wildcard and several extra functional types
are provided for setting tags, regex string matching and matching any one of several provided patterns (or).

To be completely safe and future-proofed, you may want to only use the `M*` pattern types from this submodule, but for
quick use normal `AST` types should be fine. Also you need to use the pattern types provided here if you will be using
nodes or fields which do not exist in the version of the running Python.

It should be obvious but, don't use the functional `M*` pattern types in real `AST` trees... :|
"""

# TODO: need to add proper typing here

from __future__ import annotations

import re
from re import Pattern as re_Pattern
from collections import defaultdict
from typing import Any, Mapping

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

    TryStar,

    TypeAlias,
    type_param,
    TypeVar,
    ParamSpec,
    TypeVarTuple,

    TemplateStr,
    Interpolation,

    _slice,
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
    'M_Pattern',

    'MAdd',
    'MAnd',
    'MAnnAssign',
    'MAssert',
    'MAssign',
    'MAsyncFor',
    'MAsyncFunctionDef',
    'MAsyncWith',
    'MAttribute',
    'MAugAssign',
    'MAwait',
    'MBinOp',
    'MBitAnd',
    'MBitOr',
    'MBitXor',
    'MBoolOp',
    'MBreak',
    'MCall',
    'MClassDef',
    'MCompare',
    'MConstant',
    'MContinue',
    'MDel',
    'MDelete',
    'MDict',
    'MDictComp',
    'MDiv',
    'MEq',
    'MExceptHandler',
    'MExpr',
    'MExpression',
    'MFloorDiv',
    'MFor',
    'MFormattedValue',
    'MFunctionDef',
    'MFunctionType',
    'MGeneratorExp',
    'MGlobal',
    'MGt',
    'MGtE',
    'MIf',
    'MIfExp',
    'MImport',
    'MImportFrom',
    'MIn',
    'MInteractive',
    'MInvert',
    'MIs',
    'MIsNot',
    'MJoinedStr',
    'MLShift',
    'MLambda',
    'MList',
    'MListComp',
    'MLoad',
    'MLt',
    'MLtE',
    'MMatMult',
    'MMatch',
    'MMatchAs',
    'MMatchClass',
    'MMatchMapping',
    'MMatchOr',
    'MMatchSequence',
    'MMatchSingleton',
    'MMatchStar',
    'MMatchValue',
    'MMod',
    'MModule',
    'MMult',
    'MName',
    'MNamedExpr',
    'MNonlocal',
    'MNot',
    'MNotEq',
    'MNotIn',
    'MOr',
    'MPass',
    'MPow',
    'MRShift',
    'MRaise',
    'MReturn',
    'MSet',
    'MSetComp',
    'MSlice',
    'MStarred',
    'MStore',
    'MSub',
    'MSubscript',
    'MTry',
    'MTuple',
    'MTypeIgnore',
    'MUAdd',
    'MUSub',
    'MUnaryOp',
    'MWhile',
    'MWith',
    'MYield',
    'MYieldFrom',
    'Malias',
    'Marg',
    'Marguments',
    'Mboolop',
    'Mcmpop',
    'Mcomprehension',
    'Mexcepthandler',
    'Mexpr',
    'Mexpr_context',
    'Mkeyword',
    'Mmatch_case',
    'Mmod',
    'Moperator',
    'Mpattern',
    'Mstmt',
    'Mtype_ignore',
    'Munaryop',
    'Mwithitem',

    'MTryStar',

    'MTypeAlias',
    'Mtype_param',
    'MTypeVar',
    'MParamSpec',
    'MTypeVarTuple',

    'MTemplateStr',
    'MInterpolation',

    'M_slice',
    'M_ExceptHandlers',
    'M_match_cases',
    'M_Assign_targets',
    'M_decorator_list',
    'M_arglikes',
    'M_comprehensions',
    'M_comprehension_ifs',
    'M_aliases',
    'M_withitems',
    'M_type_params',

    'MTAG',
    'MOR',
    'MRE',
]


class M_Pattern:
    _fields = ()

# ----------------------------------------------------------------------------------------------------------------------

class MModule(M_Pattern):
    ast_cls = Module

    def __init__(
        self,
        body: object = ...,
        type_ignores: object = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

        if type_ignores is not ...:
            self.type_ignores = type_ignores
            fields.append('type_ignores')

class MInteractive(M_Pattern):
    ast_cls = Interactive

    def __init__(
        self,
        body: object = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

class MExpression(M_Pattern):
    ast_cls = Expression

    def __init__(
        self,
        body: object = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

class MFunctionType(M_Pattern):
    ast_cls = FunctionType

    def __init__(
        self,
        argtypes: object = ...,
        returns: object = ...,
    ) -> None:
        self._fields = fields = []

        if argtypes is not ...:
            self.argtypes = argtypes
            fields.append('argtypes')

        if returns is not ...:
            self.returns = returns
            fields.append('returns')

class MFunctionDef(M_Pattern):
    ast_cls = FunctionDef

    def __init__(
        self,
        name: object = ...,
        args: object = ...,
        body: object = ...,
        decorator_list: object = ...,
        returns: object = ...,
        type_comment: object = ...,
        type_params: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if args is not ...:
            self.args = args
            fields.append('args')

        if body is not ...:
            self.body = body
            fields.append('body')

        if decorator_list is not ...:
            self.decorator_list = decorator_list
            fields.append('decorator_list')

        if returns is not ...:
            self.returns = returns
            fields.append('returns')

        if type_comment is not ...:
            self.type_comment = type_comment
            fields.append('type_comment')

        if type_params is not ...:
            self.type_params = type_params
            fields.append('type_params')

class MAsyncFunctionDef(M_Pattern):
    ast_cls = AsyncFunctionDef

    def __init__(
        self,
        name: object = ...,
        args: object = ...,
        body: object = ...,
        decorator_list: object = ...,
        returns: object = ...,
        type_comment: object = ...,
        type_params: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if args is not ...:
            self.args = args
            fields.append('args')

        if body is not ...:
            self.body = body
            fields.append('body')

        if decorator_list is not ...:
            self.decorator_list = decorator_list
            fields.append('decorator_list')

        if returns is not ...:
            self.returns = returns
            fields.append('returns')

        if type_comment is not ...:
            self.type_comment = type_comment
            fields.append('type_comment')

        if type_params is not ...:
            self.type_params = type_params
            fields.append('type_params')

class MClassDef(M_Pattern):
    ast_cls = ClassDef

    def __init__(
        self,
        name: object = ...,
        bases: object = ...,
        keywords: object = ...,
        body: object = ...,
        decorator_list: object = ...,
        type_params: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if bases is not ...:
            self.bases = bases
            fields.append('bases')

        if keywords is not ...:
            self.keywords = keywords
            fields.append('keywords')

        if body is not ...:
            self.body = body
            fields.append('body')

        if decorator_list is not ...:
            self.decorator_list = decorator_list
            fields.append('decorator_list')

        if type_params is not ...:
            self.type_params = type_params
            fields.append('type_params')

class MReturn(M_Pattern):
    ast_cls = Return

    def __init__(
        self,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MDelete(M_Pattern):
    ast_cls = Delete

    def __init__(
        self,
        targets: object = ...,
    ) -> None:
        self._fields = fields = []

        if targets is not ...:
            self.targets = targets
            fields.append('targets')

class MAssign(M_Pattern):
    ast_cls = Assign

    def __init__(
        self,
        targets: object = ...,
        value: object = ...,
        type_comment: object = ...,
    ) -> None:
        self._fields = fields = []

        if targets is not ...:
            self.targets = targets
            fields.append('targets')

        if value is not ...:
            self.value = value
            fields.append('value')

        if type_comment is not ...:
            self.type_comment = type_comment
            fields.append('type_comment')

class MTypeAlias(M_Pattern):
    ast_cls = TypeAlias

    def __init__(
        self,
        name: object = ...,
        type_params: object = ...,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if type_params is not ...:
            self.type_params = type_params
            fields.append('type_params')

        if value is not ...:
            self.value = value
            fields.append('value')

class MAugAssign(M_Pattern):
    ast_cls = AugAssign

    def __init__(
        self,
        target: object = ...,
        op: object = ...,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if target is not ...:
            self.target = target
            fields.append('target')

        if op is not ...:
            self.op = op
            fields.append('op')

        if value is not ...:
            self.value = value
            fields.append('value')

class MAnnAssign(M_Pattern):
    ast_cls = AnnAssign

    def __init__(
        self,
        target: object = ...,
        annotation: object = ...,
        value: object = ...,
        simple: object = ...,
    ) -> None:
        self._fields = fields = []

        if target is not ...:
            self.target = target
            fields.append('target')

        if annotation is not ...:
            self.annotation = annotation
            fields.append('annotation')

        if value is not ...:
            self.value = value
            fields.append('value')

        if simple is not ...:
            self.simple = simple
            fields.append('simple')

class MFor(M_Pattern):
    ast_cls = For

    def __init__(
        self,
        target: object = ...,
        iter: object = ...,
        body: object = ...,
        orelse: object = ...,
        type_comment: object = ...,
    ) -> None:
        self._fields = fields = []

        if target is not ...:
            self.target = target
            fields.append('target')

        if iter is not ...:
            self.iter = iter
            fields.append('iter')

        if body is not ...:
            self.body = body
            fields.append('body')

        if orelse is not ...:
            self.orelse = orelse
            fields.append('orelse')

        if type_comment is not ...:
            self.type_comment = type_comment
            fields.append('type_comment')

class MAsyncFor(M_Pattern):
    ast_cls = AsyncFor

    def __init__(
        self,
        target: object = ...,
        iter: object = ...,
        body: object = ...,
        orelse: object = ...,
        type_comment: object = ...,
    ) -> None:
        self._fields = fields = []

        if target is not ...:
            self.target = target
            fields.append('target')

        if iter is not ...:
            self.iter = iter
            fields.append('iter')

        if body is not ...:
            self.body = body
            fields.append('body')

        if orelse is not ...:
            self.orelse = orelse
            fields.append('orelse')

        if type_comment is not ...:
            self.type_comment = type_comment
            fields.append('type_comment')

class MWhile(M_Pattern):
    ast_cls = While

    def __init__(
        self,
        test: object = ...,
        body: object = ...,
        orelse: object = ...,
    ) -> None:
        self._fields = fields = []

        if test is not ...:
            self.test = test
            fields.append('test')

        if body is not ...:
            self.body = body
            fields.append('body')

        if orelse is not ...:
            self.orelse = orelse
            fields.append('orelse')

class MIf(M_Pattern):
    ast_cls = If

    def __init__(
        self,
        test: object = ...,
        body: object = ...,
        orelse: object = ...,
    ) -> None:
        self._fields = fields = []

        if test is not ...:
            self.test = test
            fields.append('test')

        if body is not ...:
            self.body = body
            fields.append('body')

        if orelse is not ...:
            self.orelse = orelse
            fields.append('orelse')

class MWith(M_Pattern):
    ast_cls = With

    def __init__(
        self,
        items: object = ...,
        body: object = ...,
        type_comment: object = ...,
    ) -> None:
        self._fields = fields = []

        if items is not ...:
            self.items = items
            fields.append('items')

        if body is not ...:
            self.body = body
            fields.append('body')

        if type_comment is not ...:
            self.type_comment = type_comment
            fields.append('type_comment')

class MAsyncWith(M_Pattern):
    ast_cls = AsyncWith

    def __init__(
        self,
        items: object = ...,
        body: object = ...,
        type_comment: object = ...,
    ) -> None:
        self._fields = fields = []

        if items is not ...:
            self.items = items
            fields.append('items')

        if body is not ...:
            self.body = body
            fields.append('body')

        if type_comment is not ...:
            self.type_comment = type_comment
            fields.append('type_comment')

class MMatch(M_Pattern):
    ast_cls = Match

    def __init__(
        self,
        subject: object = ...,
        cases: object = ...,
    ) -> None:
        self._fields = fields = []

        if subject is not ...:
            self.subject = subject
            fields.append('subject')

        if cases is not ...:
            self.cases = cases
            fields.append('cases')

class MRaise(M_Pattern):
    ast_cls = Raise

    def __init__(
        self,
        exc: object = ...,
        cause: object = ...,
    ) -> None:
        self._fields = fields = []

        if exc is not ...:
            self.exc = exc
            fields.append('exc')

        if cause is not ...:
            self.cause = cause
            fields.append('cause')

class MTry(M_Pattern):
    ast_cls = Try

    def __init__(
        self,
        body: object = ...,
        handlers: object = ...,
        orelse: object = ...,
        finalbody: object = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

        if handlers is not ...:
            self.handlers = handlers
            fields.append('handlers')

        if orelse is not ...:
            self.orelse = orelse
            fields.append('orelse')

        if finalbody is not ...:
            self.finalbody = finalbody
            fields.append('finalbody')

class MTryStar(M_Pattern):
    ast_cls = TryStar

    def __init__(
        self,
        body: object = ...,
        handlers: object = ...,
        orelse: object = ...,
        finalbody: object = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

        if handlers is not ...:
            self.handlers = handlers
            fields.append('handlers')

        if orelse is not ...:
            self.orelse = orelse
            fields.append('orelse')

        if finalbody is not ...:
            self.finalbody = finalbody
            fields.append('finalbody')

class MAssert(M_Pattern):
    ast_cls = Assert

    def __init__(
        self,
        test: object = ...,
        msg: object = ...,
    ) -> None:
        self._fields = fields = []

        if test is not ...:
            self.test = test
            fields.append('test')

        if msg is not ...:
            self.msg = msg
            fields.append('msg')

class MImport(M_Pattern):
    ast_cls = Import

    def __init__(
        self,
        names: object = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MImportFrom(M_Pattern):
    ast_cls = ImportFrom

    def __init__(
        self,
        module: object = ...,
        names: object = ...,
        level: object = ...,
    ) -> None:
        self._fields = fields = []

        if module is not ...:
            self.module = module
            fields.append('module')

        if names is not ...:
            self.names = names
            fields.append('names')

        if level is not ...:
            self.level = level
            fields.append('level')

class MGlobal(M_Pattern):
    ast_cls = Global

    def __init__(
        self,
        names: object = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MNonlocal(M_Pattern):
    ast_cls = Nonlocal

    def __init__(
        self,
        names: object = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MExpr(M_Pattern):
    ast_cls = Expr

    def __init__(
        self,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MPass(M_Pattern):
    ast_cls = Pass

class MBreak(M_Pattern):
    ast_cls = Break

class MContinue(M_Pattern):
    ast_cls = Continue

class MBoolOp(M_Pattern):
    ast_cls = BoolOp

    def __init__(
        self,
        op: object = ...,
        values: object = ...,
    ) -> None:
        self._fields = fields = []

        if op is not ...:
            self.op = op
            fields.append('op')

        if values is not ...:
            self.values = values
            fields.append('values')

class MNamedExpr(M_Pattern):
    ast_cls = NamedExpr

    def __init__(
        self,
        target: object = ...,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if target is not ...:
            self.target = target
            fields.append('target')

        if value is not ...:
            self.value = value
            fields.append('value')

class MBinOp(M_Pattern):
    ast_cls = BinOp

    def __init__(
        self,
        left: object = ...,
        op: object = ...,
        right: object = ...,
    ) -> None:
        self._fields = fields = []

        if left is not ...:
            self.left = left
            fields.append('left')

        if op is not ...:
            self.op = op
            fields.append('op')

        if right is not ...:
            self.right = right
            fields.append('right')

class MUnaryOp(M_Pattern):
    ast_cls = UnaryOp

    def __init__(
        self,
        op: object = ...,
        operand: object = ...,
    ) -> None:
        self._fields = fields = []

        if op is not ...:
            self.op = op
            fields.append('op')

        if operand is not ...:
            self.operand = operand
            fields.append('operand')

class MLambda(M_Pattern):
    ast_cls = Lambda

    def __init__(
        self,
        args: object = ...,
        body: object = ...,
    ) -> None:
        self._fields = fields = []

        if args is not ...:
            self.args = args
            fields.append('args')

        if body is not ...:
            self.body = body
            fields.append('body')

class MIfExp(M_Pattern):
    ast_cls = IfExp

    def __init__(
        self,
        test: object = ...,
        body: object = ...,
        orelse: object = ...,
    ) -> None:
        self._fields = fields = []

        if test is not ...:
            self.test = test
            fields.append('test')

        if body is not ...:
            self.body = body
            fields.append('body')

        if orelse is not ...:
            self.orelse = orelse
            fields.append('orelse')

class MDict(M_Pattern):
    ast_cls = Dict

    def __init__(
        self,
        keys: object = ...,
        values: object = ...,
    ) -> None:
        self._fields = fields = []

        if keys is not ...:
            self.keys = keys
            fields.append('keys')

        if values is not ...:
            self.values = values
            fields.append('values')

class MSet(M_Pattern):
    ast_cls = Set

    def __init__(
        self,
        elts: object = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

class MListComp(M_Pattern):
    ast_cls = ListComp

    def __init__(
        self,
        elt: object = ...,
        generators: object = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MSetComp(M_Pattern):
    ast_cls = SetComp

    def __init__(
        self,
        elt: object = ...,
        generators: object = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MDictComp(M_Pattern):
    ast_cls = DictComp

    def __init__(
        self,
        key: object = ...,
        value: object = ...,
        generators: object = ...,
    ) -> None:
        self._fields = fields = []

        if key is not ...:
            self.key = key
            fields.append('key')

        if value is not ...:
            self.value = value
            fields.append('value')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MGeneratorExp(M_Pattern):
    ast_cls = GeneratorExp

    def __init__(
        self,
        elt: object = ...,
        generators: object = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MAwait(M_Pattern):
    ast_cls = Await

    def __init__(
        self,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MYield(M_Pattern):
    ast_cls = Yield

    def __init__(
        self,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MYieldFrom(M_Pattern):
    ast_cls = YieldFrom

    def __init__(
        self,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MCompare(M_Pattern):
    ast_cls = Compare

    def __init__(
        self,
        left: object = ...,
        ops: object = ...,
        comparators: object = ...,
    ) -> None:
        self._fields = fields = []

        if left is not ...:
            self.left = left
            fields.append('left')

        if ops is not ...:
            self.ops = ops
            fields.append('ops')

        if comparators is not ...:
            self.comparators = comparators
            fields.append('comparators')

class MCall(M_Pattern):
    ast_cls = Call

    def __init__(
        self,
        func: object = ...,
        args: object = ...,
        keywords: object = ...,
    ) -> None:
        self._fields = fields = []

        if func is not ...:
            self.func = func
            fields.append('func')

        if args is not ...:
            self.args = args
            fields.append('args')

        if keywords is not ...:
            self.keywords = keywords
            fields.append('keywords')

class MFormattedValue(M_Pattern):
    ast_cls = FormattedValue

    def __init__(
        self,
        value: object = ...,
        conversion: object = ...,
        format_spec: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

        if conversion is not ...:
            self.conversion = conversion
            fields.append('conversion')

        if format_spec is not ...:
            self.format_spec = format_spec
            fields.append('format_spec')

class MInterpolation(M_Pattern):
    ast_cls = Interpolation

    def __init__(
        self,
        value: object = ...,
        str: object = ...,
        conversion: object = ...,
        format_spec: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

        if str is not ...:
            self.str = str
            fields.append('str')

        if conversion is not ...:
            self.conversion = conversion
            fields.append('conversion')

        if format_spec is not ...:
            self.format_spec = format_spec
            fields.append('format_spec')

class MJoinedStr(M_Pattern):
    ast_cls = JoinedStr

    def __init__(
        self,
        values: object = ...,
    ) -> None:
        self._fields = fields = []

        if values is not ...:
            self.values = values
            fields.append('values')

class MTemplateStr(M_Pattern):
    ast_cls = TemplateStr

    def __init__(
        self,
        values: object = ...,
    ) -> None:
        self._fields = fields = []

        if values is not ...:
            self.values = values
            fields.append('values')

class MConstant(M_Pattern):
    ast_cls = Constant

    def __init__(
        self,
        value: object,
        kind: object = ...,
    ) -> None:
        self._fields = fields = ['value']
        self.value = value

        if kind is not ...:
            self.kind = kind
            fields.append('kind')

class MAttribute(M_Pattern):
    ast_cls = Attribute

    def __init__(
        self,
        value: object = ...,
        attr: object = ...,
        ctx: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

        if attr is not ...:
            self.attr = attr
            fields.append('attr')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MSubscript(M_Pattern):
    ast_cls = Subscript

    def __init__(
        self,
        value: object = ...,
        slice: object = ...,
        ctx: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

        if slice is not ...:
            self.slice = slice
            fields.append('slice')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MStarred(M_Pattern):
    ast_cls = Starred

    def __init__(
        self,
        value: object = ...,
        ctx: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MName(M_Pattern):
    ast_cls = Name

    def __init__(
        self,
        id: object = ...,
        ctx: object = ...,
    ) -> None:
        self._fields = fields = []

        if id is not ...:
            self.id = id
            fields.append('id')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MList(M_Pattern):
    ast_cls = List

    def __init__(
        self,
        elts: object = ...,
        ctx: object = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MTuple(M_Pattern):
    ast_cls = Tuple

    def __init__(
        self,
        elts: object = ...,
        ctx: object = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MSlice(M_Pattern):
    ast_cls = Slice

    def __init__(
        self,
        lower: object = ...,
        upper: object = ...,
        step: object = ...,
    ) -> None:
        self._fields = fields = []

        if lower is not ...:
            self.lower = lower
            fields.append('lower')

        if upper is not ...:
            self.upper = upper
            fields.append('upper')

        if step is not ...:
            self.step = step
            fields.append('step')

class MLoad(M_Pattern):
    ast_cls = Load

class MStore(M_Pattern):
    ast_cls = Store

class MDel(M_Pattern):
    ast_cls = Del

class MAnd(M_Pattern):
    ast_cls = And

class MOr(M_Pattern):
    ast_cls = Or

class MAdd(M_Pattern):
    ast_cls = Add

class MSub(M_Pattern):
    ast_cls = Sub

class MMult(M_Pattern):
    ast_cls = Mult

class MMatMult(M_Pattern):
    ast_cls = MatMult

class MDiv(M_Pattern):
    ast_cls = Div

class MMod(M_Pattern):
    ast_cls = Mod

class MPow(M_Pattern):
    ast_cls = Pow

class MLShift(M_Pattern):
    ast_cls = LShift

class MRShift(M_Pattern):
    ast_cls = RShift

class MBitOr(M_Pattern):
    ast_cls = BitOr

class MBitXor(M_Pattern):
    ast_cls = BitXor

class MBitAnd(M_Pattern):
    ast_cls = BitAnd

class MFloorDiv(M_Pattern):
    ast_cls = FloorDiv

class MInvert(M_Pattern):
    ast_cls = Invert

class MNot(M_Pattern):
    ast_cls = Not

class MUAdd(M_Pattern):
    ast_cls = UAdd

class MUSub(M_Pattern):
    ast_cls = USub

class MEq(M_Pattern):
    ast_cls = Eq

class MNotEq(M_Pattern):
    ast_cls = NotEq

class MLt(M_Pattern):
    ast_cls = Lt

class MLtE(M_Pattern):
    ast_cls = LtE

class MGt(M_Pattern):
    ast_cls = Gt

class MGtE(M_Pattern):
    ast_cls = GtE

class MIs(M_Pattern):
    ast_cls = Is

class MIsNot(M_Pattern):
    ast_cls = IsNot

class MIn(M_Pattern):
    ast_cls = In

class MNotIn(M_Pattern):
    ast_cls = NotIn

class Mcomprehension(M_Pattern):
    ast_cls = comprehension

    def __init__(
        self,
        target: object = ...,
        iter: object = ...,
        ifs: object = ...,
        is_async: object = ...,
    ) -> None:
        self._fields = fields = []

        if target is not ...:
            self.target = target
            fields.append('target')

        if iter is not ...:
            self.iter = iter
            fields.append('iter')

        if ifs is not ...:
            self.ifs = ifs
            fields.append('ifs')

        if is_async is not ...:
            self.is_async = is_async
            fields.append('is_async')

class MExceptHandler(M_Pattern):
    ast_cls = ExceptHandler

    def __init__(
        self,
        type: object = ...,
        name: object = ...,
        body: object = ...,
    ) -> None:
        self._fields = fields = []

        if type is not ...:
            self.type = type
            fields.append('type')

        if name is not ...:
            self.name = name
            fields.append('name')

        if body is not ...:
            self.body = body
            fields.append('body')

class Marguments(M_Pattern):
    ast_cls = arguments

    def __init__(
        self,
        posonlyargs: object = ...,
        args: object = ...,
        vararg: object = ...,
        kwonlyargs: object = ...,
        kw_defaults: object = ...,
        kwarg: object = ...,
        defaults: object = ...,
    ) -> None:
        self._fields = fields = []

        if posonlyargs is not ...:
            self.posonlyargs = posonlyargs
            fields.append('posonlyargs')

        if args is not ...:
            self.args = args
            fields.append('args')

        if vararg is not ...:
            self.vararg = vararg
            fields.append('vararg')

        if kwonlyargs is not ...:
            self.kwonlyargs = kwonlyargs
            fields.append('kwonlyargs')

        if kw_defaults is not ...:
            self.kw_defaults = kw_defaults
            fields.append('kw_defaults')

        if kwarg is not ...:
            self.kwarg = kwarg
            fields.append('kwarg')

        if defaults is not ...:
            self.defaults = defaults
            fields.append('defaults')

class Marg(M_Pattern):
    ast_cls = arg

    def __init__(
        self,
        arg: object = ...,
        annotation: object = ...,
        type_comment: object = ...,
    ) -> None:
        self._fields = fields = []

        if arg is not ...:
            self.arg = arg
            fields.append('arg')

        if annotation is not ...:
            self.annotation = annotation
            fields.append('annotation')

        if type_comment is not ...:
            self.type_comment = type_comment
            fields.append('type_comment')

class Mkeyword(M_Pattern):
    ast_cls = keyword

    def __init__(
        self,
        arg: object = ...,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if arg is not ...:
            self.arg = arg
            fields.append('arg')

        if value is not ...:
            self.value = value
            fields.append('value')

class Malias(M_Pattern):
    ast_cls = alias

    def __init__(
        self,
        name: object = ...,
        asname: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if asname is not ...:
            self.asname = asname
            fields.append('asname')

class Mwithitem(M_Pattern):
    ast_cls = withitem

    def __init__(
        self,
        context_expr: object = ...,
        optional_vars: object = ...,
    ) -> None:
        self._fields = fields = []

        if context_expr is not ...:
            self.context_expr = context_expr
            fields.append('context_expr')

        if optional_vars is not ...:
            self.optional_vars = optional_vars
            fields.append('optional_vars')

class Mmatch_case(M_Pattern):
    ast_cls = match_case

    def __init__(
        self,
        pattern: object = ...,
        guard: object = ...,
        body: object = ...,
    ) -> None:
        self._fields = fields = []

        if pattern is not ...:
            self.pattern = pattern
            fields.append('pattern')

        if guard is not ...:
            self.guard = guard
            fields.append('guard')

        if body is not ...:
            self.body = body
            fields.append('body')

class MMatchValue(M_Pattern):
    ast_cls = MatchValue

    def __init__(
        self,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MMatchSingleton(M_Pattern):
    ast_cls = MatchSingleton

    def __init__(
        self,
        value: object = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MMatchSequence(M_Pattern):
    ast_cls = MatchSequence

    def __init__(
        self,
        patterns: object = ...,
    ) -> None:
        self._fields = fields = []

        if patterns is not ...:
            self.patterns = patterns
            fields.append('patterns')

class MMatchMapping(M_Pattern):
    ast_cls = MatchMapping

    def __init__(
        self,
        keys: object = ...,
        patterns: object = ...,
        rest: object = ...,
    ) -> None:
        self._fields = fields = []

        if keys is not ...:
            self.keys = keys
            fields.append('keys')

        if patterns is not ...:
            self.patterns = patterns
            fields.append('patterns')

        if rest is not ...:
            self.rest = rest
            fields.append('rest')

class MMatchClass(M_Pattern):
    ast_cls = MatchClass

    def __init__(
        self,
        cls: object = ...,
        patterns: object = ...,
        kwd_attrs: object = ...,
        kwd_patterns: object = ...,
    ) -> None:
        self._fields = fields = []

        if cls is not ...:
            self.cls = cls
            fields.append('cls')

        if patterns is not ...:
            self.patterns = patterns
            fields.append('patterns')

        if kwd_attrs is not ...:
            self.kwd_attrs = kwd_attrs
            fields.append('kwd_attrs')

        if kwd_patterns is not ...:
            self.kwd_patterns = kwd_patterns
            fields.append('kwd_patterns')

class MMatchStar(M_Pattern):
    ast_cls = MatchStar

    def __init__(
        self,
        name: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

class MMatchAs(M_Pattern):
    ast_cls = MatchAs

    def __init__(
        self,
        pattern: object = ...,
        name: object = ...,
    ) -> None:
        self._fields = fields = []

        if pattern is not ...:
            self.pattern = pattern
            fields.append('pattern')

        if name is not ...:
            self.name = name
            fields.append('name')

class MMatchOr(M_Pattern):
    ast_cls = MatchOr

    def __init__(
        self,
        patterns: object = ...,
    ) -> None:
        self._fields = fields = []

        if patterns is not ...:
            self.patterns = patterns
            fields.append('patterns')

class MTypeIgnore(M_Pattern):
    ast_cls = TypeIgnore

    def __init__(
        self,
        lineno: object = ...,
        tag: object = ...,
    ) -> None:
        self._fields = fields = []

        if lineno is not ...:
            self.lineno = lineno
            fields.append('lineno')

        if tag is not ...:
            self.tag = tag
            fields.append('tag')

class MTypeVar(M_Pattern):
    ast_cls = TypeVar

    def __init__(
        self,
        name: object = ...,
        bound: object = ...,
        default_value: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if bound is not ...:
            self.bound = bound
            fields.append('bound')

        if default_value is not ...:
            self.default_value = default_value
            fields.append('default_value')

class MParamSpec(M_Pattern):
    ast_cls = ParamSpec

    def __init__(
        self,
        name: object = ...,
        default_value: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if default_value is not ...:
            self.default_value = default_value
            fields.append('default_value')

class MTypeVarTuple(M_Pattern):
    ast_cls = TypeVarTuple

    def __init__(
        self,
        name: object = ...,
        default_value: object = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if default_value is not ...:
            self.default_value = default_value
            fields.append('default_value')

class M_ExceptHandlers(M_Pattern):
    ast_cls = _ExceptHandlers

    def __init__(
        self,
        handlers: object = ...,
    ) -> None:
        self._fields = fields = []

        if handlers is not ...:
            self.handlers = handlers
            fields.append('handlers')

class M_match_cases(M_Pattern):
    ast_cls = _match_cases

    def __init__(
        self,
        cases: object = ...,
    ) -> None:
        self._fields = fields = []

        if cases is not ...:
            self.cases = cases
            fields.append('cases')

class M_Assign_targets(M_Pattern):
    ast_cls = _Assign_targets

    def __init__(
        self,
        targets: object = ...,
    ) -> None:
        self._fields = fields = []

        if targets is not ...:
            self.targets = targets
            fields.append('targets')

class M_decorator_list(M_Pattern):
    ast_cls = _decorator_list

    def __init__(
        self,
        decorator_list: object = ...,
    ) -> None:
        self._fields = fields = []

        if decorator_list is not ...:
            self.decorator_list = decorator_list
            fields.append('decorator_list')

class M_arglikes(M_Pattern):
    ast_cls = _arglikes

    def __init__(
        self,
        arglikes: object = ...,
    ) -> None:
        self._fields = fields = []

        if arglikes is not ...:
            self.arglikes = arglikes
            fields.append('arglikes')

class M_comprehensions(M_Pattern):
    ast_cls = _comprehensions

    def __init__(
        self,
        generators: object = ...,
    ) -> None:
        self._fields = fields = []

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class M_comprehension_ifs(M_Pattern):
    ast_cls = _comprehension_ifs

    def __init__(
        self,
        ifs: object = ...,
    ) -> None:
        self._fields = fields = []

        if ifs is not ...:
            self.ifs = ifs
            fields.append('ifs')

class M_aliases(M_Pattern):
    ast_cls = _aliases

    def __init__(
        self,
        names: object = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class M_withitems(M_Pattern):
    ast_cls = _withitems

    def __init__(
        self,
        items: object = ...,
    ) -> None:
        self._fields = fields = []

        if items is not ...:
            self.items = items
            fields.append('items')

class M_type_params(M_Pattern):
    ast_cls = _type_params

    def __init__(
        self,
        type_params: object = ...,
    ) -> None:
        self._fields = fields = []

        if type_params is not ...:
            self.type_params = type_params
            fields.append('type_params')

class Mmod(M_Pattern):
    ast_cls = mod

class Mstmt(M_Pattern):
    ast_cls = stmt

class Mexpr(M_Pattern):
    ast_cls = expr

class Mexpr_context(M_Pattern):
    ast_cls = expr_context

class Mboolop(M_Pattern):
    ast_cls = boolop

class Moperator(M_Pattern):
    ast_cls = operator

class Munaryop(M_Pattern):
    ast_cls = unaryop

class Mcmpop(M_Pattern):
    ast_cls = cmpop

class Mexcepthandler(M_Pattern):
    ast_cls = excepthandler

class Mpattern(M_Pattern):
    ast_cls = pattern

class Mtype_ignore(M_Pattern):
    ast_cls = type_ignore

class Mtype_param(M_Pattern):
    ast_cls = type_param

class M_slice(M_Pattern):
    ast_cls = _slice


# ----------------------------------------------------------------------------------------------------------------------

_SENTINEL = object()
_EMPTY_DICT = {}


class MTAG(M_Pattern):
    """Tagging pattern container. If the given pattern matches then tags specified here will be returned in the
    `M_Match` result object. The tags can be specified with fixed values but also the matched `AST` node can be returned
    in a given tag name.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided there then the matched `AST` is not returned in tags. If this is
        missing (default `None`) then there must be at least one element in `tags` and the first key:value pair there
        will be taken to be the pattern to match and the name of the tag to use for the matched `AST`.
    - `tags`: Any fixed tags to return on a successful match.
    """

    def __init__(self, anon_pat: M_Pattern | None = None, /, **tags) -> None:
        if anon_pat:
            self.pat = anon_pat
            self.pat_tag = None
            self.tags = tags

        elif (pat_tag := next(iter(tags), None)) is None:
            raise ValueError('MTAG missing pattern')

        else:
            self.pat = tags.pop(pat_tag)
            self.pat_tag = pat_tag
            self.tags = tags

    def match(self, ast: object, match_options: Mapping[str, Any]) -> Mapping | None:
        match_ = _MATCH_FUNCS.get((p := self.pat).__class__, _match_general)(p, ast, match_options)

        if match_ is None:
            return None

        pat_tag = self.pat_tag

        if match_:
            if pat_tag:
                return {**match_, pat_tag: ast, **self.tags}

            return dict(match_, **self.tags)

        if pat_tag:
            return {pat_tag: ast, **self.tags}

        return self.tags


class MOR(M_Pattern):
    """Simple OR pattern. Matches if any of the given patterns matches.

    **Parameters:**
    - `pats`: Patterns that constitute a successful match. Only need one to match, checked in order.
    """

    def __init__(self, *pats: M_Pattern) -> None:
        if not pats:
            raise ValueError('at least one pattern required for MOR')

        self.pats = pats

    def match(self, ast: object, match_options: Mapping[str, Any]) -> Mapping | None:
        for pat in self.pats:
            match_ = _MATCH_FUNCS.get(pat.__class__, _match_general)(pat, ast, match_options)

            if match_ is not None:
                return match_

        return None


class MRE(M_Pattern):
    """Tagging regex pattern. Normal `re.Pattern` can be used and thos will just be checked using `.match()` and the
    `re.Match` object is lost. If this pattern is used instead the can specify `.match()` or `.search()` as well as
    allowing the `re.Match` object to be returned as a tag if specified."""

    def __init__(
        self, anon_re_pat: str | re_Pattern | None = None, /, flags: int = 0, search: bool = False, **tags  # can only be one tag which will be the name for the pattern, in which case anon_re_pat must be None
    ) -> None:
        if anon_re_pat is not None:
            pat_tag = None
        elif (pat_tag := next(iter(tags), None)) is None:
            raise ValueError('MRE missing pattern')
        else:
            anon_re_pat = tags.pop(pat_tag)

        if tags:
            raise ValueError('MRE does not take extra tags')

        self.re_pat = anon_re_pat if isinstance(anon_re_pat, re_Pattern) else re.compile(anon_re_pat, flags)
        self.pat_tag = pat_tag
        self.search = search

    def match(self, ast: object, match_options: Mapping[str, Any]) -> Mapping | None:
        re_pat = self.re_pat

        if not isinstance(ast, AST):
            if (isinstance(ast, str) ^ isinstance(re_pat.pattern, str)) or not (m := re_pat.match(ast)):
                return None

        else:
            m = re_pat.search(ast.f.src) if self.search else re_pat.match(ast.f.src)

            if not m:
                return None

        return {self.pat_tag: m}


# ......................................................................................................................

def _match_general(pat: object, ast: object, match_options: Mapping[str, Any]) -> Mapping | None:
    """Match the fields of any `AST` or a `str`."""

    if isinstance(pat, str):  # we do this here to account for possible subclassing of `str`
        return None if ast != pat else _EMPTY_DICT

    if not isinstance(ast, getattr(pat, 'ast_cls', None) or pat.__class__):
        return None

    tagss = []

    for field in pat._fields:
        if field == 'ctx' and not match_options['ctx']:
            continue

        pval = getattr(pat, field, ...)

        if pval is ...:
            continue

        aval = getattr(ast, field)  # this should not fail, if it does then there is a bigger problem than just a match failure

        if pval is None:
            if aval is not None:
                return None

            continue

        if isinstance(pval, list):
            if not isinstance(aval, list):
                return None

            pitr = iter(pval)
            aitr = iter(aval)

            while (pv := next(pitr, _SENTINEL)) is not _SENTINEL:
                if pv is not ...:  # need to check cocncrete match
                    if (av := next(aitr, _SENTINEL)) is _SENTINEL:  # if ast list ended before can match then fail
                        return None

                    match_ = _MATCH_FUNCS.get(pv.__class__, _match_general)(pv, av, match_options)

                    if match_ is None:  # if not match then fail as this is an expected concrete match
                        return None

                    if match_:
                        tagss.append(match_)

                    continue

                # wildcard skip

                while (pv := next(pitr, _SENTINEL)) is not _SENTINEL:
                    if pv is ...:  # eat any repeated ...
                        continue

                    break  # found concrete pattern value to match against

                else:  # ended on ..., doesn't matter what is left in the ast list
                    break

                # got concrete pv to match against, now we walk the ast list until find a match or not

                while (av := next(aitr, _SENTINEL)) is not _SENTINEL:
                    match_ = _MATCH_FUNCS.get(pv.__class__, _match_general)(pv, av, match_options)

                    if match_ is None:  # if not match then keep looking (because pv preceded by ...)
                        continue

                    if match_:
                        tagss.append(match_)

                    break

                else:  # ast list ends before being able to make concrete match to concrete pv
                    return None

                continue  # found concrete / concrete match, iterate on to next pattern value

            else:
                if next(aitr, _SENTINEL) is not _SENTINEL:  # if concrete pattern list ended without ... and there are still elements in the ast list then fail
                    return None

            continue

        if isinstance(pval, (M_Pattern, AST, re_Pattern, str)):
            match_ = _MATCH_FUNCS.get(pval.__class__, _match_general)(pval, aval, match_options)

            if match_ is None:
                return None

            if match_:
                tagss.append(match_)

            continue

        # primitive value comparison

        if aval != pval or aval.__class__ is not pval.__class__:  # the class check for bool vs. int
            return None

    # combine all tags and return

    ret = {}

    for tags in tagss:
        ret.update(tags)

    return ret

def _match_type(pat: object, ast: object, match_options: Mapping[str, Any]) -> Mapping | None:
    """Just match the `AST` type."""

    return _EMPTY_DICT if isinstance(ast, pat) else None

def _match_re_Pattern(pat: object, ast: object, match_options: Mapping[str, Any]) -> Mapping | None:
    """Regex pattern against direct `str` or `bytes` value or source if `ast` is an actual node."""

    if not isinstance(ast, AST):
        if (isinstance(ast, str) ^ isinstance(pat.pattern, str)) or not pat.match(ast):
            return None

    elif not pat.match(ast.f.src):  # match source against pattern
        return None

    return _EMPTY_DICT

def _match_Constant(pat: object, ast: object, match_options: Mapping[str, Any]) -> Mapping | None:
    """We do a special handler for `Constant` so we can check for a real `Ellipsis` instead of having that work as a
    wildcarcd. We do a standalone handler so don't have to have the check in general."""

    if (ast.__class__ is not Constant
        or ast.value != pat.value
        or ((pval := getattr(pat, 'kind', ...)) is not ... and ast.kind != pval)
    ):
        return None

    return _EMPTY_DICT

_MATCH_FUNCS = {
    type:       _match_type,
    re_Pattern: _match_re_Pattern,
    Constant:   _match_Constant,
    MConstant:  _match_Constant,
    MTAG:       MTAG.match,
    MOR:        MOR.match,
    MRE:        MRE.match,
}


class M_Match(defaultdict):
    """Successful match object. Can look up tags directly on the object."""

    class TagNotSet:  # so that we can check value of any tag without needing to check if they exist first
        __slots__ = ()
        _singleton: M_Match.TagNotSet

        def __new__(cls) -> M_Match.TagNotSet:
            return cls._singleton

        def __bool__(self) -> bool:
            return False

    TagNotSet._singleton = object.__new__(TagNotSet)

    def __init__(self, *args: object, **kwargs) -> None:
        defaultdict.__init__(self, M_Match.TagNotSet, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<fst.Match {dict.__repr__(self)}>'


# ----------------------------------------------------------------------------------------------------------------------
# public FST class methods

def match(
    self: fst.FST,
    pat: M_Pattern | AST,
    *,
    ctx: bool = False,
) -> M_Match | None:
    """

    **Parameters:**

    **Returns:**
    """

    match_ = _MATCH_FUNCS.get(pat.__class__, _match_general)(pat, self.a, dict(ctx=ctx))

    return None if match_ is None else M_Match(match_)
