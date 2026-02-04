"""FST matcher. Uses `AST` nodes for patterns but supplies some new `AST` types to allow creation of base types without
having to provide all the needed fields. Ellipsis is used in patterns as a wildcard and several extra functional types
are provided for setting tags, regex string matching and matching any one of several provided patterns (or).

To be completely safe and future-proofed, you may want to only use the `M*` pattern types from this submodule, but for
quick use normal `AST` types should be fine. Also you need to use the pattern types provided here if you will be using
nodes or fields which do not exist in the version of the running Python.

It should be obvious but, don't use the functional `M*` pattern types in real `AST` trees... %|
"""

from __future__ import annotations

import re
from re import Pattern as re_Pattern
from collections import defaultdict
from types import EllipsisType, NoneType
from typing import Any, Mapping, Union

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

from .astutil import constant
from .parsex import unparse

__all__ = [
    'M_Pattern',
    'MAST',

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


_TargetElement = AST | constant
_Target = list[_TargetElement] | _TargetElement  # `str` and `None` also have special meaning outside of constant, str is identifier and None may be a missing optional AST (or other type)

_PatternElement = Union[_TargetElement, type[Union['M_Pattern', AST]], 'M_Pattern', re_Pattern, EllipsisType]  # `str` here may also be a match for target node source, not just a primitive
_Pattern = list[_PatternElement] | _PatternElement


class M_Match(defaultdict):
    """Successful match object. Can look up tags directly on this object. Nonexistent tags will not raise but return a
    falsey `M_Match.NotSet`."""

    class _NotSet:  # so that we can check value of any tag without needing to check if they exist first
        __slots__ = ()

        def __new__(cls) -> M_Match._NotSet:
            return M_Match.NotSet

        def __bool__(self) -> bool:
            return False

    NotSet = object.__new__(_NotSet)

    def __init__(self, *args: object, **kwargs) -> None:
        defaultdict.__init__(self, M_Match._NotSet, *args, **kwargs)

    def __bool__(self) -> bool:  # so that even an empty dict evaluates to true for easier return checking
        return True

    def __repr__(self) -> str:
        return f'<fst.Match {dict.__repr__(self)}>'


class M_Pattern:
    _fields = ()

    def match(self, tgt: _Target, *, ctx: bool = False) -> M_Match | None:
        """TODO: document

        **Parameters:**
        - `ctx`: Whether to match against the `ctx` field of `AST` patterns or not. Defaults to `False` because when
            creating `AST` nodes the `ctx` field may be created automatically if you don't specify it so may
            inadvertantly break any matches. Will always check `ctx` field for `M_Pattern` patterns because there it is
            well behaved and if not specified is set to wildcard.

        **Returns:**
        - `M_Match`: Successful match, the match object can be indexed directly with tag names.
        - `None`: Did not match.
        """

        m = _MATCH_FUNCS.get(self.__class__, _match_default)(self, tgt, dict(ctx=ctx))

        return None if m is None else M_Match(m)


class MAST(M_Pattern):
    ast_cls = AST


# ----------------------------------------------------------------------------------------------------------------------
# Generated pattern classes

class MModule(MAST):
    ast_cls = Module

    def __init__(
        self,
        body: _Pattern = ...,
        type_ignores: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

        if type_ignores is not ...:
            self.type_ignores = type_ignores
            fields.append('type_ignores')

class MInteractive(MAST):
    ast_cls = Interactive

    def __init__(
        self,
        body: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

class MExpression(MAST):
    ast_cls = Expression

    def __init__(
        self,
        body: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

class MFunctionType(MAST):
    ast_cls = FunctionType

    def __init__(
        self,
        argtypes: _Pattern = ...,
        returns: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if argtypes is not ...:
            self.argtypes = argtypes
            fields.append('argtypes')

        if returns is not ...:
            self.returns = returns
            fields.append('returns')

class MFunctionDef(MAST):
    ast_cls = FunctionDef

    def __init__(
        self,
        name: _Pattern = ...,
        args: _Pattern = ...,
        body: _Pattern = ...,
        decorator_list: _Pattern = ...,
        returns: _Pattern = ...,
        type_comment: _Pattern = ...,
        type_params: _Pattern = ...,
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

class MAsyncFunctionDef(MAST):
    ast_cls = AsyncFunctionDef

    def __init__(
        self,
        name: _Pattern = ...,
        args: _Pattern = ...,
        body: _Pattern = ...,
        decorator_list: _Pattern = ...,
        returns: _Pattern = ...,
        type_comment: _Pattern = ...,
        type_params: _Pattern = ...,
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

class MClassDef(MAST):
    ast_cls = ClassDef

    def __init__(
        self,
        name: _Pattern = ...,
        bases: _Pattern = ...,
        keywords: _Pattern = ...,
        body: _Pattern = ...,
        decorator_list: _Pattern = ...,
        type_params: _Pattern = ...,
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

class MReturn(MAST):
    ast_cls = Return

    def __init__(
        self,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MDelete(MAST):
    ast_cls = Delete

    def __init__(
        self,
        targets: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if targets is not ...:
            self.targets = targets
            fields.append('targets')

class MAssign(MAST):
    ast_cls = Assign

    def __init__(
        self,
        targets: _Pattern = ...,
        value: _Pattern = ...,
        type_comment: _Pattern = ...,
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

class MTypeAlias(MAST):
    ast_cls = TypeAlias

    def __init__(
        self,
        name: _Pattern = ...,
        type_params: _Pattern = ...,
        value: _Pattern = ...,
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

class MAugAssign(MAST):
    ast_cls = AugAssign

    def __init__(
        self,
        target: _Pattern = ...,
        op: _Pattern = ...,
        value: _Pattern = ...,
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

class MAnnAssign(MAST):
    ast_cls = AnnAssign

    def __init__(
        self,
        target: _Pattern = ...,
        annotation: _Pattern = ...,
        value: _Pattern = ...,
        simple: _Pattern = ...,
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

class MFor(MAST):
    ast_cls = For

    def __init__(
        self,
        target: _Pattern = ...,
        iter: _Pattern = ...,
        body: _Pattern = ...,
        orelse: _Pattern = ...,
        type_comment: _Pattern = ...,
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

class MAsyncFor(MAST):
    ast_cls = AsyncFor

    def __init__(
        self,
        target: _Pattern = ...,
        iter: _Pattern = ...,
        body: _Pattern = ...,
        orelse: _Pattern = ...,
        type_comment: _Pattern = ...,
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

class MWhile(MAST):
    ast_cls = While

    def __init__(
        self,
        test: _Pattern = ...,
        body: _Pattern = ...,
        orelse: _Pattern = ...,
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

class MIf(MAST):
    ast_cls = If

    def __init__(
        self,
        test: _Pattern = ...,
        body: _Pattern = ...,
        orelse: _Pattern = ...,
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

class MWith(MAST):
    ast_cls = With

    def __init__(
        self,
        items: _Pattern = ...,
        body: _Pattern = ...,
        type_comment: _Pattern = ...,
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

class MAsyncWith(MAST):
    ast_cls = AsyncWith

    def __init__(
        self,
        items: _Pattern = ...,
        body: _Pattern = ...,
        type_comment: _Pattern = ...,
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

class MMatch(MAST):
    ast_cls = Match

    def __init__(
        self,
        subject: _Pattern = ...,
        cases: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if subject is not ...:
            self.subject = subject
            fields.append('subject')

        if cases is not ...:
            self.cases = cases
            fields.append('cases')

class MRaise(MAST):
    ast_cls = Raise

    def __init__(
        self,
        exc: _Pattern = ...,
        cause: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if exc is not ...:
            self.exc = exc
            fields.append('exc')

        if cause is not ...:
            self.cause = cause
            fields.append('cause')

class MTry(MAST):
    ast_cls = Try

    def __init__(
        self,
        body: _Pattern = ...,
        handlers: _Pattern = ...,
        orelse: _Pattern = ...,
        finalbody: _Pattern = ...,
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

class MTryStar(MAST):
    ast_cls = TryStar

    def __init__(
        self,
        body: _Pattern = ...,
        handlers: _Pattern = ...,
        orelse: _Pattern = ...,
        finalbody: _Pattern = ...,
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

class MAssert(MAST):
    ast_cls = Assert

    def __init__(
        self,
        test: _Pattern = ...,
        msg: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if test is not ...:
            self.test = test
            fields.append('test')

        if msg is not ...:
            self.msg = msg
            fields.append('msg')

class MImport(MAST):
    ast_cls = Import

    def __init__(
        self,
        names: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MImportFrom(MAST):
    ast_cls = ImportFrom

    def __init__(
        self,
        module: _Pattern = ...,
        names: _Pattern = ...,
        level: _Pattern = ...,
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

class MGlobal(MAST):
    ast_cls = Global

    def __init__(
        self,
        names: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MNonlocal(MAST):
    ast_cls = Nonlocal

    def __init__(
        self,
        names: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MExpr(MAST):
    ast_cls = Expr

    def __init__(
        self,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MPass(MAST):
    ast_cls = Pass

class MBreak(MAST):
    ast_cls = Break

class MContinue(MAST):
    ast_cls = Continue

class MBoolOp(MAST):
    ast_cls = BoolOp

    def __init__(
        self,
        op: _Pattern = ...,
        values: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if op is not ...:
            self.op = op
            fields.append('op')

        if values is not ...:
            self.values = values
            fields.append('values')

class MNamedExpr(MAST):
    ast_cls = NamedExpr

    def __init__(
        self,
        target: _Pattern = ...,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if target is not ...:
            self.target = target
            fields.append('target')

        if value is not ...:
            self.value = value
            fields.append('value')

class MBinOp(MAST):
    ast_cls = BinOp

    def __init__(
        self,
        left: _Pattern = ...,
        op: _Pattern = ...,
        right: _Pattern = ...,
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

class MUnaryOp(MAST):
    ast_cls = UnaryOp

    def __init__(
        self,
        op: _Pattern = ...,
        operand: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if op is not ...:
            self.op = op
            fields.append('op')

        if operand is not ...:
            self.operand = operand
            fields.append('operand')

class MLambda(MAST):
    ast_cls = Lambda

    def __init__(
        self,
        args: _Pattern = ...,
        body: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if args is not ...:
            self.args = args
            fields.append('args')

        if body is not ...:
            self.body = body
            fields.append('body')

class MIfExp(MAST):
    ast_cls = IfExp

    def __init__(
        self,
        test: _Pattern = ...,
        body: _Pattern = ...,
        orelse: _Pattern = ...,
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

class MDict(MAST):
    ast_cls = Dict

    def __init__(
        self,
        keys: _Pattern = ...,
        values: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if keys is not ...:
            self.keys = keys
            fields.append('keys')

        if values is not ...:
            self.values = values
            fields.append('values')

class MSet(MAST):
    ast_cls = Set

    def __init__(
        self,
        elts: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

class MListComp(MAST):
    ast_cls = ListComp

    def __init__(
        self,
        elt: _Pattern = ...,
        generators: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MSetComp(MAST):
    ast_cls = SetComp

    def __init__(
        self,
        elt: _Pattern = ...,
        generators: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MDictComp(MAST):
    ast_cls = DictComp

    def __init__(
        self,
        key: _Pattern = ...,
        value: _Pattern = ...,
        generators: _Pattern = ...,
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

class MGeneratorExp(MAST):
    ast_cls = GeneratorExp

    def __init__(
        self,
        elt: _Pattern = ...,
        generators: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MAwait(MAST):
    ast_cls = Await

    def __init__(
        self,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MYield(MAST):
    ast_cls = Yield

    def __init__(
        self,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MYieldFrom(MAST):
    ast_cls = YieldFrom

    def __init__(
        self,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MCompare(MAST):
    ast_cls = Compare

    def __init__(
        self,
        left: _Pattern = ...,
        ops: _Pattern = ...,
        comparators: _Pattern = ...,
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

class MCall(MAST):
    ast_cls = Call

    def __init__(
        self,
        func: _Pattern = ...,
        args: _Pattern = ...,
        keywords: _Pattern = ...,
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

class MFormattedValue(MAST):
    ast_cls = FormattedValue

    def __init__(
        self,
        value: _Pattern = ...,
        conversion: _Pattern = ...,
        format_spec: _Pattern = ...,
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

class MInterpolation(MAST):
    ast_cls = Interpolation

    def __init__(
        self,
        value: _Pattern = ...,
        str: _Pattern = ...,
        conversion: _Pattern = ...,
        format_spec: _Pattern = ...,
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

class MJoinedStr(MAST):
    ast_cls = JoinedStr

    def __init__(
        self,
        values: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if values is not ...:
            self.values = values
            fields.append('values')

class MTemplateStr(MAST):
    ast_cls = TemplateStr

    def __init__(
        self,
        values: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if values is not ...:
            self.values = values
            fields.append('values')

class MConstant(MAST):
    ast_cls = Constant

    def __init__(
        self,
        value: _Pattern,  # Ellipsis here is not a wildcard but a concrete value to match
        kind: _Pattern = ...,
    ) -> None:
        self._fields = fields = ['value']
        self.value = value

        if kind is not ...:
            self.kind = kind
            fields.append('kind')

class MAttribute(MAST):
    ast_cls = Attribute

    def __init__(
        self,
        value: _Pattern = ...,
        attr: _Pattern = ...,
        ctx: _Pattern = ...,
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

class MSubscript(MAST):
    ast_cls = Subscript

    def __init__(
        self,
        value: _Pattern = ...,
        slice: _Pattern = ...,
        ctx: _Pattern = ...,
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

class MStarred(MAST):
    ast_cls = Starred

    def __init__(
        self,
        value: _Pattern = ...,
        ctx: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MName(MAST):
    ast_cls = Name

    def __init__(
        self,
        id: _Pattern = ...,
        ctx: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if id is not ...:
            self.id = id
            fields.append('id')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MList(MAST):
    ast_cls = List

    def __init__(
        self,
        elts: _Pattern = ...,
        ctx: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MTuple(MAST):
    ast_cls = Tuple

    def __init__(
        self,
        elts: _Pattern = ...,
        ctx: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MSlice(MAST):
    ast_cls = Slice

    def __init__(
        self,
        lower: _Pattern = ...,
        upper: _Pattern = ...,
        step: _Pattern = ...,
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

class MLoad(MAST):
    ast_cls = Load

class MStore(MAST):
    ast_cls = Store

class MDel(MAST):
    ast_cls = Del

class MAnd(MAST):
    ast_cls = And

class MOr(MAST):
    ast_cls = Or

class MAdd(MAST):
    ast_cls = Add

class MSub(MAST):
    ast_cls = Sub

class MMult(MAST):
    ast_cls = Mult

class MMatMult(MAST):
    ast_cls = MatMult

class MDiv(MAST):
    ast_cls = Div

class MMod(MAST):
    ast_cls = Mod

class MPow(MAST):
    ast_cls = Pow

class MLShift(MAST):
    ast_cls = LShift

class MRShift(MAST):
    ast_cls = RShift

class MBitOr(MAST):
    ast_cls = BitOr

class MBitXor(MAST):
    ast_cls = BitXor

class MBitAnd(MAST):
    ast_cls = BitAnd

class MFloorDiv(MAST):
    ast_cls = FloorDiv

class MInvert(MAST):
    ast_cls = Invert

class MNot(MAST):
    ast_cls = Not

class MUAdd(MAST):
    ast_cls = UAdd

class MUSub(MAST):
    ast_cls = USub

class MEq(MAST):
    ast_cls = Eq

class MNotEq(MAST):
    ast_cls = NotEq

class MLt(MAST):
    ast_cls = Lt

class MLtE(MAST):
    ast_cls = LtE

class MGt(MAST):
    ast_cls = Gt

class MGtE(MAST):
    ast_cls = GtE

class MIs(MAST):
    ast_cls = Is

class MIsNot(MAST):
    ast_cls = IsNot

class MIn(MAST):
    ast_cls = In

class MNotIn(MAST):
    ast_cls = NotIn

class Mcomprehension(MAST):
    ast_cls = comprehension

    def __init__(
        self,
        target: _Pattern = ...,
        iter: _Pattern = ...,
        ifs: _Pattern = ...,
        is_async: _Pattern = ...,
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

class MExceptHandler(MAST):
    ast_cls = ExceptHandler

    def __init__(
        self,
        type: _Pattern = ...,
        name: _Pattern = ...,
        body: _Pattern = ...,
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

class Marguments(MAST):
    ast_cls = arguments

    def __init__(
        self,
        posonlyargs: _Pattern = ...,
        args: _Pattern = ...,
        vararg: _Pattern = ...,
        kwonlyargs: _Pattern = ...,
        kw_defaults: _Pattern = ...,
        kwarg: _Pattern = ...,
        defaults: _Pattern = ...,
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

class Marg(MAST):
    ast_cls = arg

    def __init__(
        self,
        arg: _Pattern = ...,
        annotation: _Pattern = ...,
        type_comment: _Pattern = ...,
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

class Mkeyword(MAST):
    ast_cls = keyword

    def __init__(
        self,
        arg: _Pattern = ...,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if arg is not ...:
            self.arg = arg
            fields.append('arg')

        if value is not ...:
            self.value = value
            fields.append('value')

class Malias(MAST):
    ast_cls = alias

    def __init__(
        self,
        name: _Pattern = ...,
        asname: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if asname is not ...:
            self.asname = asname
            fields.append('asname')

class Mwithitem(MAST):
    ast_cls = withitem

    def __init__(
        self,
        context_expr: _Pattern = ...,
        optional_vars: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if context_expr is not ...:
            self.context_expr = context_expr
            fields.append('context_expr')

        if optional_vars is not ...:
            self.optional_vars = optional_vars
            fields.append('optional_vars')

class Mmatch_case(MAST):
    ast_cls = match_case

    def __init__(
        self,
        pattern: _Pattern = ...,
        guard: _Pattern = ...,
        body: _Pattern = ...,
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

class MMatchValue(MAST):
    ast_cls = MatchValue

    def __init__(
        self,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MMatchSingleton(MAST):
    ast_cls = MatchSingleton

    def __init__(
        self,
        value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MMatchSequence(MAST):
    ast_cls = MatchSequence

    def __init__(
        self,
        patterns: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if patterns is not ...:
            self.patterns = patterns
            fields.append('patterns')

class MMatchMapping(MAST):
    ast_cls = MatchMapping

    def __init__(
        self,
        keys: _Pattern = ...,
        patterns: _Pattern = ...,
        rest: _Pattern = ...,
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

class MMatchClass(MAST):
    ast_cls = MatchClass

    def __init__(
        self,
        cls: _Pattern = ...,
        patterns: _Pattern = ...,
        kwd_attrs: _Pattern = ...,
        kwd_patterns: _Pattern = ...,
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

class MMatchStar(MAST):
    ast_cls = MatchStar

    def __init__(
        self,
        name: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

class MMatchAs(MAST):
    ast_cls = MatchAs

    def __init__(
        self,
        pattern: _Pattern = ...,
        name: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if pattern is not ...:
            self.pattern = pattern
            fields.append('pattern')

        if name is not ...:
            self.name = name
            fields.append('name')

class MMatchOr(MAST):
    ast_cls = MatchOr

    def __init__(
        self,
        patterns: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if patterns is not ...:
            self.patterns = patterns
            fields.append('patterns')

class MTypeIgnore(MAST):
    ast_cls = TypeIgnore

    def __init__(
        self,
        lineno: _Pattern = ...,
        tag: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if lineno is not ...:
            self.lineno = lineno
            fields.append('lineno')

        if tag is not ...:
            self.tag = tag
            fields.append('tag')

class MTypeVar(MAST):
    ast_cls = TypeVar

    def __init__(
        self,
        name: _Pattern = ...,
        bound: _Pattern = ...,
        default_value: _Pattern = ...,
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

class MParamSpec(MAST):
    ast_cls = ParamSpec

    def __init__(
        self,
        name: _Pattern = ...,
        default_value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if default_value is not ...:
            self.default_value = default_value
            fields.append('default_value')

class MTypeVarTuple(MAST):
    ast_cls = TypeVarTuple

    def __init__(
        self,
        name: _Pattern = ...,
        default_value: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if default_value is not ...:
            self.default_value = default_value
            fields.append('default_value')

class M_ExceptHandlers(MAST):
    ast_cls = _ExceptHandlers

    def __init__(
        self,
        handlers: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if handlers is not ...:
            self.handlers = handlers
            fields.append('handlers')

class M_match_cases(MAST):
    ast_cls = _match_cases

    def __init__(
        self,
        cases: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if cases is not ...:
            self.cases = cases
            fields.append('cases')

class M_Assign_targets(MAST):
    ast_cls = _Assign_targets

    def __init__(
        self,
        targets: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if targets is not ...:
            self.targets = targets
            fields.append('targets')

class M_decorator_list(MAST):
    ast_cls = _decorator_list

    def __init__(
        self,
        decorator_list: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if decorator_list is not ...:
            self.decorator_list = decorator_list
            fields.append('decorator_list')

class M_arglikes(MAST):
    ast_cls = _arglikes

    def __init__(
        self,
        arglikes: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if arglikes is not ...:
            self.arglikes = arglikes
            fields.append('arglikes')

class M_comprehensions(MAST):
    ast_cls = _comprehensions

    def __init__(
        self,
        generators: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class M_comprehension_ifs(MAST):
    ast_cls = _comprehension_ifs

    def __init__(
        self,
        ifs: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if ifs is not ...:
            self.ifs = ifs
            fields.append('ifs')

class M_aliases(MAST):
    ast_cls = _aliases

    def __init__(
        self,
        names: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class M_withitems(MAST):
    ast_cls = _withitems

    def __init__(
        self,
        items: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if items is not ...:
            self.items = items
            fields.append('items')

class M_type_params(MAST):
    ast_cls = _type_params

    def __init__(
        self,
        type_params: _Pattern = ...,
    ) -> None:
        self._fields = fields = []

        if type_params is not ...:
            self.type_params = type_params
            fields.append('type_params')

class Mmod(MAST):
    ast_cls = mod

class Mstmt(MAST):
    ast_cls = stmt

class Mexpr(MAST):
    ast_cls = expr

class Mexpr_context(MAST):
    ast_cls = expr_context

class Mboolop(MAST):
    ast_cls = boolop

class Moperator(MAST):
    ast_cls = operator

class Munaryop(MAST):
    ast_cls = unaryop

class Mcmpop(MAST):
    ast_cls = cmpop

class Mexcepthandler(MAST):
    ast_cls = excepthandler

class Mpattern(MAST):
    ast_cls = pattern

class Mtype_ignore(MAST):
    ast_cls = type_ignore

class Mtype_param(MAST):
    ast_cls = type_param

class M_slice(MAST):
    ast_cls = _slice


# ----------------------------------------------------------------------------------------------------------------------

_SENTINEL = object()
_EMPTY_DICT = {}


class MTAG(M_Pattern):
    """Tagging pattern container. If the given pattern matches then tags specified here will be returned in the
    `M_Match` result object. The tags can be specified with fixed values but also the matched `AST` node can be returned
    in a given tag name.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched `AST` is not returned in tags. If this is
        missing (default `None`) then there must be at least one element in `tags` and the first key:value pair there
        will be taken to be the pattern to match and the name of the tag to use for the matched `AST`.
    - `tags`: Any fixed tags to return on a successful match.
    """

    def __init__(self, anon_pat: _Pattern = None, /, **tags) -> None:
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

    @staticmethod
    def _match(self: MTAG, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
        m = _MATCH_FUNCS.get((p := self.pat).__class__, _match_default)(p, tgt, moptions)

        if m is None:
            return None

        pat_tag = self.pat_tag

        if m:
            if pat_tag:
                return {**m, pat_tag: tgt, **self.tags}

            return dict(m, **self.tags)

        if pat_tag:
            return {pat_tag: tgt, **self.tags}

        return self.tags


class MOR(M_Pattern):
    """Simple OR pattern. Matches if any of the given patterns matches.

    **Parameters:**
    - `pats`: Patterns that constitute a successful match. Only need one to match, checked in order.
    """

    def __init__(self, *pats: _Pattern) -> None:
        if not pats:
            raise ValueError('at least one pattern required for MOR')

        self.pats = pats

    @staticmethod
    def _match(self: MOR, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
        for p in self.pats:
            m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, moptions)

            if m is not None:
                return m

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

    @staticmethod
    def _match(self: MRE, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
        """Regex match or search pattern against direct `str` or `bytes` value or source if `tgt` is an actual node. Will
        use `FST` source from the tree and unparse a non-`FST` `AST` node for the check. Returns `re.Match` object if is
        requested."""

        re_pat = self.re_pat
        func = re_pat.search if self.search else re_pat.match

        if isinstance(tgt, str):
            if not isinstance(re_pat.pattern, str) or not (m := func(tgt)):
                return None

        elif isinstance(tgt, AST):
            if not isinstance(re_pat.pattern, str):
                return None

            if not (f := getattr(tgt, 'f', None)) or not (loc := f.loc):
                src = unparse(tgt)
            else:
                src = f._get_src(*loc)

            if not (m := func(src)):  # match source against pattern
                return None

        elif isinstance(tgt, bytes):
            if not isinstance(re_pat.pattern, bytes) or not (m := func(tgt)):
                return None

        elif isinstance(tgt, list):
            raise ValueError('MRE can never match a list field')

        else:
            return None

        return _EMPTY_DICT if (tag := self.pat_tag) is None else {tag: m}


# ......................................................................................................................

def _match_default(pat: _Pattern, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """Match the fields of any `M_Pattern`, `AST` or a `str` (either as a primitive value or as source)."""

    if isinstance(pat, list):
        if not isinstance(tgt, list):
            raise ValueError('list can never match a non-list field')

        tagss = []
        iter_pat = iter(pat)
        iter_tgt = iter(tgt)

        while (p := next(iter_pat, _SENTINEL)) is not _SENTINEL:
            if p is not ...:  # need to check cocncrete match
                if (t := next(iter_tgt, _SENTINEL)) is _SENTINEL:  # if ast list ended before can match then fail
                    return None

                m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, moptions)

                if m is None:  # if not match then fail as this is an expected concrete match
                    return None

                if m:
                    tagss.append(m)

                continue

            # wildcard skip

            while (p := next(iter_pat, _SENTINEL)) is not _SENTINEL:
                if p is ...:  # eat any repeated ...
                    continue

                break  # found concrete pattern value to match against

            else:  # ended on ..., doesn't matter what is left in the ast list
                break

            # got concrete p to match against, now we walk the ast list until find a match or not

            while (t := next(iter_tgt, _SENTINEL)) is not _SENTINEL:
                m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, moptions)

                if m is None:  # if not match then keep looking (because p preceded by ...)
                    continue

                if m:
                    tagss.append(m)

                break

            else:  # ast list ends before being able to make concrete match to concrete p
                return None

            continue  # found concrete / concrete match, iterate on to next pattern value

        else:
            if next(iter_tgt, _SENTINEL) is not _SENTINEL:  # if concrete pattern list ended without ... and there are still elements in the ast list then fail
                return None

        # combine all tags and return

        if not tagss:
            return _EMPTY_DICT
        if len(tagss) == 1:
            return tagss[0]

        ret = {}

        for tags in tagss:
            ret.update(tags)

        return ret

    # got here through subclass of a primitive type

    if isinstance(pat, str):
        return _match_str(pat, tgt, moptions)

    return _match_primitive(pat, tgt, moptions)

def _match_str(pat: constant, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    if isinstance(tgt, str):
        if tgt != pat:
            return None

    elif isinstance(tgt, AST):
        if not (f := getattr(tgt, 'f', None)) or not (loc := f.loc):
            src = unparse(tgt)
        else:
            src = f._get_src(*loc)

        if src != pat:  # match source against exact string
            return None

    elif isinstance(tgt, list):
        raise ValueError('str can never match a list field')

    else:
        return None

    return _EMPTY_DICT

def _match_primitive(pat: constant, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """Primitive value comparison. We explicitly disallow equality of different types so 0 != 0.0 != 0j != False. We do
    all this to account for the possibility of subclassed primary types. This will not compare a `str` pattern against
    source."""

    if tgt is pat:
        return _EMPTY_DICT

    tgt_cls = tgt.__class__
    pat_cls = pat.__class__

    if tgt_cls is bool or pat_cls is bool:
        return None

    if issubclass(tgt_cls, int):
        if not issubclass(pat_cls, int) or tgt != pat:
            return None

    elif issubclass(tgt_cls, float):
        if not issubclass(pat_cls, float) or tgt != pat:
            return None

    elif issubclass(tgt_cls, complex):
        if not issubclass(pat_cls, complex) or tgt != pat:
            return None

    elif tgt != pat:
        if issubclass(tgt_cls, list):
            raise ValueError(f'{pat_cls.__qualname__} can never match a list field')

        return None

    return _EMPTY_DICT

def _match_node(pat: M_Pattern | AST, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """`M_Pattern` or `AST` leaf node."""

    ast_cls = pat.ast_cls if isinstance(pat, M_Pattern) else pat.__class__

    if not isinstance(tgt, ast_cls):
        if isinstance(tgt, list):
            raise ValueError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    tagss = []

    for field in pat._fields:
        p = getattr(pat, field, ...)

        if p is ...:  # ellipsis handled here without dispatching for various reasons
            continue

        t = getattr(tgt, field,_SENTINEL)  # field may not exist in target because pattern may have fields from a greater python version than we are running

        if t is _SENTINEL:
            return None

        m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, moptions)

        if m is None:
            return None
        if m:
            tagss.append(m)

    # combine all tags and return

    if not tagss:
        return _EMPTY_DICT
    if len(tagss) == 1:
        return tagss[0]

    ret = {}

    for tags in tagss:
        ret.update(tags)

    return ret

def _match_node_Constant(pat: MConstant | Constant, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """We do a special handler for `Constant` so we can check for a real `Ellipsis` instead of having that work as a
    wildcarcd. We do a standalone handler so don't have to have the check in general."""

    if (tgt.__class__ is not Constant
        or (t := tgt.value) != (p := pat.value)  # this is just an early out of the value comparison even if equal they can still be unequal
        or ((kind := getattr(pat, 'kind', ...)) is not ... and tgt.kind != kind)
    ):
        if isinstance(tgt, list):
            raise ValueError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    return _match_primitive(p, t, moptions)

def _match_node_expr_context(pat: Load | Store | Del, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """This exists as a convenience so that an `AST` pattern `Load`, `Store` and `Del` always match each other unless
    the match option `ctx=True`. `MLoad`, `MStore` and `MDel` don't get here, they always do a match check. A pattern
    `None` must also match one of these successfully for py < 3.13."""

    if not isinstance(tgt, expr_context) or (moptions.get('ctx') and tgt.__class__ is not pat.__class__):
        if isinstance(tgt, list):
            raise ValueError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    return _EMPTY_DICT

def _match_node_nonleaf(pat: M_Pattern | AST, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """`AST` non-leaf node (actual instance of something like `stmt()`, etc..., whatever, we take it). We just check
    that the type is correct."""

    ast_cls = pat.ast_cls if isinstance(pat, M_Pattern) else pat.__class__

    if not isinstance(tgt, ast_cls):
        if isinstance(tgt, list):
            raise ValueError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    return _EMPTY_DICT

def _match_type(pat: type, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """Just match the `AST` type (or equivalent `MAST` type)."""

    if issubclass(pat, M_Pattern):
        pat = pat.ast_cls

    if not isinstance(tgt, pat):
        if isinstance(tgt, list):
            raise ValueError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    return _EMPTY_DICT

def _match_re_Pattern(pat: re_Pattern, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """Regex pattern against direct `str` or `bytes` value or source if `tgt` is an actual node. Will use `FST` source
    from the tree and unparse a non-`FST` `AST` node for the check."""

    if isinstance(tgt, str):
        if not isinstance(pat.pattern, str) or not pat.match(tgt):
            return None

    elif isinstance(tgt, AST):
        if not isinstance(pat.pattern, str):
            return None

        if not (f := getattr(tgt, 'f', None)) or not (loc := f.loc):
            src = unparse(tgt)
        else:
            src = f._get_src(*loc)

        if not pat.match(src):  # match source against pattern
            return None

    elif isinstance(tgt, bytes):
        if not isinstance(pat.pattern, bytes) or not pat.match(tgt):
            return None

    elif isinstance(tgt, list):
        raise ValueError('re.Pattern can never match a list field')

    else:
        return None

    return _EMPTY_DICT

def _match_Ellipsis(pat: EllipsisType, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    """Always succeeds."""

    return _EMPTY_DICT

def _match_None(pat: NoneType, tgt: _Target, moptions: Mapping[str, Any]) -> Mapping | None:
    if tgt is not None:
        if isinstance(tgt, list):
            raise ValueError('None can never match a list field')

        return None

    return _EMPTY_DICT

_MATCH_FUNCS = {
    MTAG:                MTAG._match,
    MOR:                 MOR._match,
    MRE:                 MRE._match,
    AST:                 _match_node,
    Add:                 _match_node,
    And:                 _match_node,
    AnnAssign:           _match_node,
    Assert:              _match_node,
    Assign:              _match_node,
    AsyncFor:            _match_node,
    AsyncFunctionDef:    _match_node,
    AsyncWith:           _match_node,
    Attribute:           _match_node,
    AugAssign:           _match_node,
    Await:               _match_node,
    BinOp:               _match_node,
    BitAnd:              _match_node,
    BitOr:               _match_node,
    BitXor:              _match_node,
    BoolOp:              _match_node,
    Break:               _match_node,
    Call:                _match_node,
    ClassDef:            _match_node,
    Compare:             _match_node,
    Constant:            _match_node_Constant,
    Continue:            _match_node,
    Del:                 _match_node_expr_context,
    Delete:              _match_node,
    Dict:                _match_node,
    DictComp:            _match_node,
    Div:                 _match_node,
    Eq:                  _match_node,
    ExceptHandler:       _match_node,
    Expr:                _match_node,
    Expression:          _match_node,
    FloorDiv:            _match_node,
    For:                 _match_node,
    FormattedValue:      _match_node,
    FunctionDef:         _match_node,
    FunctionType:        _match_node,
    GeneratorExp:        _match_node,
    Global:              _match_node,
    Gt:                  _match_node,
    GtE:                 _match_node,
    If:                  _match_node,
    IfExp:               _match_node,
    Import:              _match_node,
    ImportFrom:          _match_node,
    In:                  _match_node,
    Interactive:         _match_node,
    Invert:              _match_node,
    Is:                  _match_node,
    IsNot:               _match_node,
    JoinedStr:           _match_node,
    LShift:              _match_node,
    Lambda:              _match_node,
    List:                _match_node,
    ListComp:            _match_node,
    Load:                _match_node_expr_context,
    Lt:                  _match_node,
    LtE:                 _match_node,
    MatMult:             _match_node,
    Match:               _match_node,
    MatchAs:             _match_node,
    MatchClass:          _match_node,
    MatchMapping:        _match_node,
    MatchOr:             _match_node,
    MatchSequence:       _match_node,
    MatchSingleton:      _match_node,
    MatchStar:           _match_node,
    MatchValue:          _match_node,
    Mod:                 _match_node,
    Module:              _match_node,
    Mult:                _match_node,
    Name:                _match_node,
    NamedExpr:           _match_node,
    Nonlocal:            _match_node,
    Not:                 _match_node,
    NotEq:               _match_node,
    NotIn:               _match_node,
    Or:                  _match_node,
    Pass:                _match_node,
    Pow:                 _match_node,
    RShift:              _match_node,
    Raise:               _match_node,
    Return:              _match_node,
    Set:                 _match_node,
    SetComp:             _match_node,
    Slice:               _match_node,
    Starred:             _match_node,
    Store:               _match_node_expr_context,
    Sub:                 _match_node,
    Subscript:           _match_node,
    Try:                 _match_node,
    Tuple:               _match_node,
    TypeIgnore:          _match_node,
    UAdd:                _match_node,
    USub:                _match_node,
    UnaryOp:             _match_node,
    While:               _match_node,
    With:                _match_node,
    Yield:               _match_node,
    YieldFrom:           _match_node,
    alias:               _match_node,
    arg:                 _match_node,
    arguments:           _match_node,
    boolop:              _match_node,
    cmpop:               _match_node,
    comprehension:       _match_node,
    excepthandler:       _match_node_nonleaf,
    expr:                _match_node_nonleaf,
    expr_context:        _match_node_nonleaf,
    keyword:             _match_node,
    match_case:          _match_node,
    mod:                 _match_node_nonleaf,
    operator:            _match_node,
    pattern:             _match_node_nonleaf,
    stmt:                _match_node_nonleaf,
    type_ignore:         _match_node_nonleaf,
    unaryop:             _match_node,
    withitem:            _match_node,
    TryStar:             _match_node,
    TypeAlias:           _match_node,
    type_param:          _match_node_nonleaf,
    TypeVar:             _match_node,
    ParamSpec:           _match_node,
    TypeVarTuple:        _match_node,
    TemplateStr:         _match_node,
    Interpolation:       _match_node,
    _slice:              _match_node_nonleaf,
    _ExceptHandlers:     _match_node,
    _match_cases:        _match_node,
    _Assign_targets:     _match_node,
    _decorator_list:     _match_node,
    _arglikes:           _match_node,
    _comprehensions:     _match_node,
    _comprehension_ifs:  _match_node,
    _aliases:            _match_node,
    _withitems:          _match_node,
    _type_params:        _match_node,
    MAdd:                _match_node,
    MAnd:                _match_node,
    MAnnAssign:          _match_node,
    MAssert:             _match_node,
    MAssign:             _match_node,
    MAsyncFor:           _match_node,
    MAsyncFunctionDef:   _match_node,
    MAsyncWith:          _match_node,
    MAttribute:          _match_node,
    MAugAssign:          _match_node,
    MAwait:              _match_node,
    MBinOp:              _match_node,
    MBitAnd:             _match_node,
    MBitOr:              _match_node,
    MBitXor:             _match_node,
    MBoolOp:             _match_node,
    MBreak:              _match_node,
    MCall:               _match_node,
    MClassDef:           _match_node,
    MCompare:            _match_node,
    MConstant:           _match_node_Constant,
    MContinue:           _match_node,
    MDel:                _match_node,
    MDelete:             _match_node,
    MDict:               _match_node,
    MDictComp:           _match_node,
    MDiv:                _match_node,
    MEq:                 _match_node,
    MExceptHandler:      _match_node,
    MExpr:               _match_node,
    MExpression:         _match_node,
    MFloorDiv:           _match_node,
    MFor:                _match_node,
    MFormattedValue:     _match_node,
    MFunctionDef:        _match_node,
    MFunctionType:       _match_node,
    MGeneratorExp:       _match_node,
    MGlobal:             _match_node,
    MGt:                 _match_node,
    MGtE:                _match_node,
    MIf:                 _match_node,
    MIfExp:              _match_node,
    MImport:             _match_node,
    MImportFrom:         _match_node,
    MIn:                 _match_node,
    MInteractive:        _match_node,
    MInvert:             _match_node,
    MIs:                 _match_node,
    MIsNot:              _match_node,
    MJoinedStr:          _match_node,
    MLShift:             _match_node,
    MLambda:             _match_node,
    MList:               _match_node,
    MListComp:           _match_node,
    MLoad:               _match_node,
    MLt:                 _match_node,
    MLtE:                _match_node,
    MMatMult:            _match_node,
    MMatch:              _match_node,
    MMatchAs:            _match_node,
    MMatchClass:         _match_node,
    MMatchMapping:       _match_node,
    MMatchOr:            _match_node,
    MMatchSequence:      _match_node,
    MMatchSingleton:     _match_node,
    MMatchStar:          _match_node,
    MMatchValue:         _match_node,
    MMod:                _match_node,
    MModule:             _match_node,
    MMult:               _match_node,
    MName:               _match_node,
    MNamedExpr:          _match_node,
    MNonlocal:           _match_node,
    MNot:                _match_node,
    MNotEq:              _match_node,
    MNotIn:              _match_node,
    MOr:                 _match_node,
    MPass:               _match_node,
    MPow:                _match_node,
    MRShift:             _match_node,
    MRaise:              _match_node,
    MReturn:             _match_node,
    MSet:                _match_node,
    MSetComp:            _match_node,
    MSlice:              _match_node,
    MStarred:            _match_node,
    MStore:              _match_node,
    MSub:                _match_node,
    MSubscript:          _match_node,
    MTry:                _match_node,
    MTuple:              _match_node,
    MTypeIgnore:         _match_node,
    MUAdd:               _match_node,
    MUSub:               _match_node,
    MUnaryOp:            _match_node,
    MWhile:              _match_node,
    MWith:               _match_node,
    MYield:              _match_node,
    MYieldFrom:          _match_node,
    Malias:              _match_node,
    Marg:                _match_node,
    Marguments:          _match_node,
    Mboolop:             _match_node,
    Mcmpop:              _match_node,
    Mcomprehension:      _match_node,
    Mexcepthandler:      _match_node_nonleaf,
    Mexpr:               _match_node_nonleaf,
    Mexpr_context:       _match_node_nonleaf,
    Mkeyword:            _match_node,
    Mmatch_case:         _match_node,
    Mmod:                _match_node_nonleaf,
    Moperator:           _match_node,
    Mpattern:            _match_node_nonleaf,
    Mstmt:               _match_node_nonleaf,
    Mtype_ignore:        _match_node_nonleaf,
    Munaryop:            _match_node,
    Mwithitem:           _match_node,
    MTryStar:            _match_node,
    MTypeAlias:          _match_node,
    Mtype_param:         _match_node_nonleaf,
    MTypeVar:            _match_node,
    MParamSpec:          _match_node,
    MTypeVarTuple:       _match_node,
    MTemplateStr:        _match_node,
    MInterpolation:      _match_node,
    M_slice:             _match_node_nonleaf,
    M_ExceptHandlers:    _match_node,
    M_match_cases:       _match_node,
    M_Assign_targets:    _match_node,
    M_decorator_list:    _match_node,
    M_arglikes:          _match_node,
    M_comprehensions:    _match_node,
    M_comprehension_ifs: _match_node,
    M_aliases:           _match_node,
    M_withitems:         _match_node,
    M_type_params:       _match_node,
    type:                _match_type,
    re_Pattern:          _match_re_Pattern,
    EllipsisType:        _match_Ellipsis,
    int:                 _match_primitive,
    float:               _match_primitive,
    complex:             _match_primitive,
    str:                 _match_str,
    bytes:               _match_primitive,
    bool:                _match_primitive,
    NoneType:            _match_None,
}


# ----------------------------------------------------------------------------------------------------------------------
# public FST class methods

def match(
    self: fst.FST,
    pat: _Pattern,
    *,
    ctx: bool = False,
) -> M_Match | None:
    """TODO: document

    **Parameters:**
    - `ctx`: Whether to match against the `ctx` field of `AST` patterns or not. Defaults to `False` because when
        creating `AST` nodes the `ctx` field may be created automatically if you don't specify it so may
        inadvertantly break any matches. Will always check `ctx` field for `M_Pattern` patterns because there it is
        well behaved and if not specified is set to wildcard.

    **Returns:**
    - `M_Match`: Successful match, the match object can be indexed directly with tag names.
    - `None`: Did not match.
    """

    m = _MATCH_FUNCS.get(pat.__class__, _match_default)(pat, self.a, dict(ctx=ctx))

    return None if m is None else M_Match(m)
