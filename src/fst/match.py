"""Structural node pattern matching. Uses `AST`-like and even `AST` nodes themselves for patterns. Ellipsis is used in
patterns as a wildcard and several extra functional pattern types are provided for setting tags, regex string matching,
logic operations, match check callbacks, match previously matched nodes (backreference) and greedy and non-greedy
quantifiers.

In the examples here you will see `AST` nodes used interchangeably with their `MAST` pattern counterparts. For the most
part this is fine and there are only a few small differences between using the two. Except if you are using a type
checker...

**Note:** Annoyingly this module breaks the convention that anything that has `FST` class methods imported into the main
`FST` class has a filename that starts with `fst_`. This is so that `from fst.match import *` and
`from fst import match as m` is cleaner.
"""

from __future__ import annotations

import re
from ast import walk
from re import Pattern as re_Pattern
from types import EllipsisType, MappingProxyType, NoneType
from typing import Any, Callable, Generator, Iterable, Mapping, Sequence, Set as tp_Set, Union

from . import fst

from .asttypes import (
    ASTS_LEAF_STMT,
    ASTS_LEAF_VAR_SCOPE_DECL,
    ASTS_LEAF__ALL,
    AST2ASTSLEAF,

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
from .common import astfield
from .parsex import unparse
from .code import Code, code_as_all

from .view import (
    FSTView,
    FSTView_Dict,
    FSTView_MatchMapping,
    FSTView_Compare,
    FSTView_arguments,
    FSTView__body,
    FSTView_arglikes,
    FSTView_Global_Nonlocal,
    FSTView_dummy,
)

from .fst_options import check_options

__all__ = [
    'MatchError',
    'NotSet',
    'FSTMatch',
    'M_Pattern',

    'M',
    'MNOT',
    'MOR',
    'MAND',
    'MMAYBE',
    'MTYPES',
    'MRE',
    'MCB',
    'MTAG',
    'MQ',
    'MQSTAR',
    'MQPLUS',
    'MQOPT',
    'MQMIN',
    'MQMAX',
    'MQN',

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
]

_SENTINEL = object()

_EMPTY_LIST = []
_EMPTY_SET = set()
_EMPTY_DICT = {}
_EMPTY_MAPPINGPROXY = MappingProxyType(_EMPTY_DICT)

_LEN_ASTS_LEAF__ALL = len(ASTS_LEAF__ALL)

_Target = AST | constant
_TargetFST = Union['fst.FST', constant]
_Targets = FSTView | _Target | list[_Target]  # `str` and `None` also have special meaning outside of constant, str is identifier and None may be a missing optional AST (or other type)
_TargetsOrFST = Union['fst.FST', _Targets]

_Pattern = Union['M_Pattern', AST, type[Union['M_Pattern', AST]], re_Pattern, str, EllipsisType, _Target]  # `str` here may also be a match for target node source, not just a primitive
_Patterns = _Pattern | list[_Pattern]


def _rpr(o: object) -> str:
    """Show `Ellipsis` as `...` and `AST` instances properly, among other things."""

    if o is ...:
        return '...'

    if (o_cls := o.__class__) is type and issubclass(o, (AST, M_Pattern)):
        return o.__qualname__

    if isinstance(o, AST):
        return f'{o_cls.__qualname__}({", ".join(f"{f}={_rpr(getattr(o, f, None))}" for f in o._fields if f != "ctx")})'

    if isinstance(o, list):
        return f'[{", ".join(_rpr(e) for e in o)}]'

    return repr(o)


class _NotSet:
    """This exists for FSTMatch so that we can check value of any tag without needing to check if it exists first."""

    __slots__ = ()

    def __new__(cls) -> FSTMatch._NotSet:
        return NotSet

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return '<NotSet>'

NotSet = object.__new__(_NotSet)  ; """A falsey object returned if accessing a non-existent tag on the `FSTMatch` object as an attribute."""


class MatchError(RuntimeError):
    """An error during matching or substitution."""

    __module__ = 'fst'  # so the exception shows up as 'fst.NodeError'


class FSTMatch:
    """Successful match object."""

    tags: Mapping[str, Any]  ; """Full match tags dictionary. Only successful matches get their tags included."""
    pattern: _Pattern  ; """The pattern used for the match. Can be any valid pattern including `AST` node, primitive values, compiled `re.Pattern`, etc..."""
    matched: _TargetsOrFST  ; """What was matched. Does not have to be a node as list and primitive matches can be matched. If a node is matched then this will be `AST` or `FST` depending on which type the target of the match attempt was."""

    def __init__(self, pattern: _Pattern, matched: _TargetsOrFST, tags: Mapping[str, Any]) -> None:
        self.pattern = pattern
        self.matched = matched
        self.tags = MappingProxyType(tags) if tags else _EMPTY_MAPPINGPROXY

    def __repr__(self) -> str:
        if tags := self.tags:
            return f'<FSTMatch {_rpr(self.matched)} {{{", ".join(f"{k!r}: {_rpr(v)}" for k, v in tags.items())}}}>'
        else:
            return f'<FSTMatch {_rpr(self.matched)}>'

    def __getitem__(self, name: str) -> object:
        """Get item from `tags`, returning `NotSet` on failure."""

        return self.tags.get(name, NotSet)

    def get(self, tag: str, default: object = NotSet, /) -> object:
        """A `dict.get()` function for the match tags. Just a shortcut for `FSTMatch.tags.get(tag, default)`."""

        return self.tags.get(tag, default)


class M_Pattern:
    """The base class for all non-primitive match patterns. The two main categories of patterns being `MAST` node
    matchers and the functional matchers like `MOR` and `MRE`."""

    _fields: tuple[str] = ()  # these AST attributes are here so that non-AST patterns like MOR and MF can work against ASTs, they can be overridden on a per-instance basis
    _types: type[AST] | tuple[type[AST]] = AST  # only the MTYPES pattern has a tuple here

    def match(self, target: _TargetsOrFST, *, ctx: bool = False) -> FSTMatch | None:
        """Match this pattern against given target. This can take `FST` nodes or `AST` (whether they are part of an
        `FST` tree or not, meaning it can match against pure `AST` trees). Can also match primitives and lists of nodes
        if the pattern is set up for that.

        **Parameters:**
        - `target`: The target to match. Can be an `AST` or `FST` node or constant or a list of `AST` nodes or constants.
        - `ctx`: Whether to match `expr_context` INSTANCES or not (`expr_context` types are always matched). Defaults to
            `False` to allow matching backreferences with different `ctx` values with each other, such as a `Name` as a
            target of an `Assign` with the same name later used in an expression (`Store` vs. `Load`). Also as a
            conveninence since when creating `AST` nodes for patterns the `ctx` field may be created automatically if
            you don't specify it so may inadvertantly break matches where you don't want to take that into
            consideration.

        **Returns:**
        - `FSTMatch`: The match object on successful match.
        - `None`: Did not match.
        """

        is_FST = isinstance(target, fst.FST)

        if not is_FST:
            tgt = target
        elif not (tgt := target.a):
            raise ValueError(f'{self.__class__.__qualname__}.match() called with dead FST node')

        m = _MATCH_FUNCS.get(self.__class__, _match_default)(self, tgt, _MatchState(is_FST, ctx))

        return None if m is None else FSTMatch(self, target, m)


class MAST(M_Pattern):
    """This class (and its non-leaf subclasses like `Mstmt` and `Mexpr`) can be used as an arbitrary field(s) pattern.
    Can match one or more fields (list or not, without list type errors), as long as the type matches (e.g. an `Assign`
    matches an `Mstmt` but not an `Mexpr`). This arbitrary field matching behavior is unique to non-leaf `AST` types,
    concrete types like `MAssign` always have fixed fields.

    **Note:** Since there are several fields which can be either an individual element or list of elements, matching
    a list pattern vs. a non-list and vice versa is just treated as a non-match.

    **Parameters:**
    - `fields`: If provided then is an arbitrary list of fields to match. Otherwise will just match based on type.

    **Examples:**

    Will match any `AST` node which has a `value` which is a `Call`. So will match `return f()`,
    `await something(a, b, c)` and just an `Expr` `call(args)`, but not `yield x` or `*(a, b, c)`.

    >>> pat = MAST(value=Call)

    >>> pat.match(FST('return f()'))
    <FSTMatch <Return ROOT 0,0..0,10>>

    >>> pat.match(FST('await something(a, b, c)'))
    <FSTMatch <Await ROOT 0,0..0,24>>

    >>> pat.match(FST('call(args)', Expr))
    <FSTMatch <Expr ROOT 0,0..0,10>>

    >>> pat.match(FST('yield x'))

    >>> pat.match(FST('*(a, b, c)'))

    Will match any statement which has a `Constant` string as the first element of its body, in other words a docstring.

    >>> pat = Mstmt(body=[MExpr(MConstant(str)), MQSTAR])

    >>> pat.match(FST('def f(): "docstr"; pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,23>>

    >>> pat.match(FST('class cls: "docstr"'))
    <FSTMatch <ClassDef ROOT 0,0..0,19>>

    >>> pat.match(FST('class cls: 1'))

    >>> pat.match(FST('class cls: 1; "NOTdocstr"'))

    >>> pat.match(FST('class cls: pass'))
    """

    _types: type[AST] | tuple[type[AST]] = AST  # the tuple-of-types is only used in functional pattern MTYPES

    def __init__(self, **fields: _Patterns) -> None:
        if fields:
            self._fields = fields

            for field, value in fields.items():
                setattr(self, field, value)

    def __repr__(self) -> str:
        name = self.__class__.__name__
        fields = ', '.join(f'{f}={_rpr(getattr(self, f))}' for f in self._fields)

        return f'{name}({fields})'


# ......................................................................................................................
# Generated pattern classes

class Mmod(MAST):  # pragma: no cover
    """"""
    _types = mod

class Mstmt(MAST):  # pragma: no cover
    """"""
    _types = stmt

class Mexpr(MAST):  # pragma: no cover
    """"""
    _types = expr

class Mexpr_context(MAST):  # pragma: no cover
    """"""
    _types = expr_context

class Mboolop(MAST):  # pragma: no cover
    """"""
    _types = boolop

class Moperator(MAST):  # pragma: no cover
    """"""
    _types = operator

class Munaryop(MAST):  # pragma: no cover
    """"""
    _types = unaryop

class Mcmpop(MAST):  # pragma: no cover
    """"""
    _types = cmpop

class Mexcepthandler(MAST):  # pragma: no cover
    """"""
    _types = excepthandler

class Mpattern(MAST):  # pragma: no cover
    """"""
    _types = pattern

class Mtype_ignore(MAST):  # pragma: no cover
    """"""
    _types = type_ignore

class Mtype_param(MAST):  # pragma: no cover
    """"""
    _types = type_param

class M_slice(MAST):  # pragma: no cover
    """"""
    _types = _slice

class MModule(Mmod):  # pragma: no cover
    """"""
    _types = Module

    def __init__(
        self,
        body: _Patterns = ...,
        type_ignores: _Patterns = ...,
        _body: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

        if type_ignores is not ...:
            self.type_ignores = type_ignores
            fields.append('type_ignores')

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MInteractive(Mmod):  # pragma: no cover
    """"""
    _types = Interactive

    def __init__(
        self,
        body: _Patterns = ...,
        _body: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MExpression(Mmod):  # pragma: no cover
    """"""
    _types = Expression

    def __init__(
        self,
        body: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if body is not ...:
            self.body = body
            fields.append('body')

class MFunctionType(Mmod):  # pragma: no cover
    """"""
    _types = FunctionType

    def __init__(
        self,
        argtypes: _Patterns = ...,
        returns: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if argtypes is not ...:
            self.argtypes = argtypes
            fields.append('argtypes')

        if returns is not ...:
            self.returns = returns
            fields.append('returns')

class MFunctionDef(Mstmt):  # pragma: no cover
    """"""
    _types = FunctionDef

    def __init__(
        self,
        name: _Patterns = ...,
        args: _Patterns = ...,
        body: _Patterns = ...,
        decorator_list: _Patterns = ...,
        returns: _Patterns = ...,
        type_comment: _Patterns = ...,
        type_params: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MAsyncFunctionDef(Mstmt):  # pragma: no cover
    """"""
    _types = AsyncFunctionDef

    def __init__(
        self,
        name: _Patterns = ...,
        args: _Patterns = ...,
        body: _Patterns = ...,
        decorator_list: _Patterns = ...,
        returns: _Patterns = ...,
        type_comment: _Patterns = ...,
        type_params: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MClassDef(Mstmt):  # pragma: no cover
    """"""
    _types = ClassDef

    def __init__(
        self,
        name: _Patterns = ...,
        bases: _Patterns = ...,
        keywords: _Patterns = ...,
        body: _Patterns = ...,
        decorator_list: _Patterns = ...,
        type_params: _Patterns = ...,
        _bases: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _bases is not ...:
            self._bases = _bases
            fields.append('_bases')

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MReturn(Mstmt):  # pragma: no cover
    """"""
    _types = Return

    def __init__(
        self,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MDelete(Mstmt):  # pragma: no cover
    """"""
    _types = Delete

    def __init__(
        self,
        targets: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if targets is not ...:
            self.targets = targets
            fields.append('targets')

class MAssign(Mstmt):  # pragma: no cover
    """"""
    _types = Assign

    def __init__(
        self,
        targets: _Patterns = ...,
        value: _Patterns = ...,
        type_comment: _Patterns = ...,
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

class MTypeAlias(Mstmt):  # pragma: no cover
    """"""
    _types = TypeAlias

    def __init__(
        self,
        name: _Patterns = ...,
        type_params: _Patterns = ...,
        value: _Patterns = ...,
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

class MAugAssign(Mstmt):  # pragma: no cover
    """"""
    _types = AugAssign

    def __init__(
        self,
        target: _Patterns = ...,
        op: _Patterns = ...,
        value: _Patterns = ...,
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

class MAnnAssign(Mstmt):  # pragma: no cover
    """"""
    _types = AnnAssign

    def __init__(
        self,
        target: _Patterns = ...,
        annotation: _Patterns = ...,
        value: _Patterns = ...,
        simple: _Patterns = ...,
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

class MFor(Mstmt):  # pragma: no cover
    """"""
    _types = For

    def __init__(
        self,
        target: _Patterns = ...,
        iter: _Patterns = ...,
        body: _Patterns = ...,
        orelse: _Patterns = ...,
        type_comment: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MAsyncFor(Mstmt):  # pragma: no cover
    """"""
    _types = AsyncFor

    def __init__(
        self,
        target: _Patterns = ...,
        iter: _Patterns = ...,
        body: _Patterns = ...,
        orelse: _Patterns = ...,
        type_comment: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MWhile(Mstmt):  # pragma: no cover
    """"""
    _types = While

    def __init__(
        self,
        test: _Patterns = ...,
        body: _Patterns = ...,
        orelse: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MIf(Mstmt):  # pragma: no cover
    """"""
    _types = If

    def __init__(
        self,
        test: _Patterns = ...,
        body: _Patterns = ...,
        orelse: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MWith(Mstmt):  # pragma: no cover
    """"""
    _types = With

    def __init__(
        self,
        items: _Patterns = ...,
        body: _Patterns = ...,
        type_comment: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MAsyncWith(Mstmt):  # pragma: no cover
    """"""
    _types = AsyncWith

    def __init__(
        self,
        items: _Patterns = ...,
        body: _Patterns = ...,
        type_comment: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MMatch(Mstmt):  # pragma: no cover
    """"""
    _types = Match

    def __init__(
        self,
        subject: _Patterns = ...,
        cases: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if subject is not ...:
            self.subject = subject
            fields.append('subject')

        if cases is not ...:
            self.cases = cases
            fields.append('cases')

class MRaise(Mstmt):  # pragma: no cover
    """"""
    _types = Raise

    def __init__(
        self,
        exc: _Patterns = ...,
        cause: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if exc is not ...:
            self.exc = exc
            fields.append('exc')

        if cause is not ...:
            self.cause = cause
            fields.append('cause')

class MTry(Mstmt):  # pragma: no cover
    """"""
    _types = Try

    def __init__(
        self,
        body: _Patterns = ...,
        handlers: _Patterns = ...,
        orelse: _Patterns = ...,
        finalbody: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MTryStar(Mstmt):  # pragma: no cover
    """"""
    _types = TryStar

    def __init__(
        self,
        body: _Patterns = ...,
        handlers: _Patterns = ...,
        orelse: _Patterns = ...,
        finalbody: _Patterns = ...,
        _body: _Patterns = ...,
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

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MAssert(Mstmt):  # pragma: no cover
    """"""
    _types = Assert

    def __init__(
        self,
        test: _Patterns = ...,
        msg: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if test is not ...:
            self.test = test
            fields.append('test')

        if msg is not ...:
            self.msg = msg
            fields.append('msg')

class MImport(Mstmt):  # pragma: no cover
    """"""
    _types = Import

    def __init__(
        self,
        names: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MImportFrom(Mstmt):  # pragma: no cover
    """"""
    _types = ImportFrom

    def __init__(
        self,
        module: _Patterns = ...,
        names: _Patterns = ...,
        level: _Patterns = ...,
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

class MGlobal(Mstmt):  # pragma: no cover
    """"""
    _types = Global

    def __init__(
        self,
        names: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MNonlocal(Mstmt):  # pragma: no cover
    """"""
    _types = Nonlocal

    def __init__(
        self,
        names: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class MExpr(Mstmt):  # pragma: no cover
    """"""
    _types = Expr

    def __init__(
        self,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MPass(Mstmt):  # pragma: no cover
    """"""
    _types = Pass

    def __init__(self) -> None:
        pass

class MBreak(Mstmt):  # pragma: no cover
    """"""
    _types = Break

    def __init__(self) -> None:
        pass

class MContinue(Mstmt):  # pragma: no cover
    """"""
    _types = Continue

    def __init__(self) -> None:
        pass

class MBoolOp(Mexpr):  # pragma: no cover
    """"""
    _types = BoolOp

    def __init__(
        self,
        op: _Patterns = ...,
        values: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if op is not ...:
            self.op = op
            fields.append('op')

        if values is not ...:
            self.values = values
            fields.append('values')

class MNamedExpr(Mexpr):  # pragma: no cover
    """"""
    _types = NamedExpr

    def __init__(
        self,
        target: _Patterns = ...,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if target is not ...:
            self.target = target
            fields.append('target')

        if value is not ...:
            self.value = value
            fields.append('value')

class MBinOp(Mexpr):  # pragma: no cover
    """"""
    _types = BinOp

    def __init__(
        self,
        left: _Patterns = ...,
        op: _Patterns = ...,
        right: _Patterns = ...,
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

class MUnaryOp(Mexpr):  # pragma: no cover
    """"""
    _types = UnaryOp

    def __init__(
        self,
        op: _Patterns = ...,
        operand: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if op is not ...:
            self.op = op
            fields.append('op')

        if operand is not ...:
            self.operand = operand
            fields.append('operand')

class MLambda(Mexpr):  # pragma: no cover
    """"""
    _types = Lambda

    def __init__(
        self,
        args: _Patterns = ...,
        body: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if args is not ...:
            self.args = args
            fields.append('args')

        if body is not ...:
            self.body = body
            fields.append('body')

class MIfExp(Mexpr):  # pragma: no cover
    """"""
    _types = IfExp

    def __init__(
        self,
        test: _Patterns = ...,
        body: _Patterns = ...,
        orelse: _Patterns = ...,
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

class MDict(Mexpr):  # pragma: no cover
    """"""
    _types = Dict

    def __init__(
        self,
        keys: _Patterns = ...,
        values: _Patterns = ...,
        _all: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if keys is not ...:
            self.keys = keys
            fields.append('keys')

        if values is not ...:
            self.values = values
            fields.append('values')

        if _all is not ...:
            self._all = _all
            fields.append('_all')

class MSet(Mexpr):  # pragma: no cover
    """"""
    _types = Set

    def __init__(
        self,
        elts: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

class MListComp(Mexpr):  # pragma: no cover
    """"""
    _types = ListComp

    def __init__(
        self,
        elt: _Patterns = ...,
        generators: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MSetComp(Mexpr):  # pragma: no cover
    """"""
    _types = SetComp

    def __init__(
        self,
        elt: _Patterns = ...,
        generators: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MDictComp(Mexpr):  # pragma: no cover
    """"""
    _types = DictComp

    def __init__(
        self,
        key: _Patterns = ...,
        value: _Patterns = ...,
        generators: _Patterns = ...,
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

class MGeneratorExp(Mexpr):  # pragma: no cover
    """"""
    _types = GeneratorExp

    def __init__(
        self,
        elt: _Patterns = ...,
        generators: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if elt is not ...:
            self.elt = elt
            fields.append('elt')

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class MAwait(Mexpr):  # pragma: no cover
    """"""
    _types = Await

    def __init__(
        self,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MYield(Mexpr):  # pragma: no cover
    """"""
    _types = Yield

    def __init__(
        self,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MYieldFrom(Mexpr):  # pragma: no cover
    """"""
    _types = YieldFrom

    def __init__(
        self,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MCompare(Mexpr):  # pragma: no cover
    """"""
    _types = Compare

    def __init__(
        self,
        left: _Patterns = ...,
        ops: _Patterns = ...,
        comparators: _Patterns = ...,
        _all: _Patterns = ...,
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

        if _all is not ...:
            self._all = _all
            fields.append('_all')

class MCall(Mexpr):  # pragma: no cover
    """"""
    _types = Call

    def __init__(
        self,
        func: _Patterns = ...,
        args: _Patterns = ...,
        keywords: _Patterns = ...,
        _args: _Patterns = ...,
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

        if _args is not ...:
            self._args = _args
            fields.append('_args')

class MFormattedValue(Mexpr):  # pragma: no cover
    """"""
    _types = FormattedValue

    def __init__(
        self,
        value: _Patterns = ...,
        conversion: _Patterns = ...,
        format_spec: _Patterns = ...,
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

class MInterpolation(Mexpr):  # pragma: no cover
    """"""
    _types = Interpolation

    def __init__(
        self,
        value: _Patterns = ...,
        str: _Patterns = ...,
        conversion: _Patterns = ...,
        format_spec: _Patterns = ...,
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

class MJoinedStr(Mexpr):  # pragma: no cover
    """"""
    _types = JoinedStr

    def __init__(
        self,
        values: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if values is not ...:
            self.values = values
            fields.append('values')

class MTemplateStr(Mexpr):  # pragma: no cover
    """"""
    _types = TemplateStr

    def __init__(
        self,
        values: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if values is not ...:
            self.values = values
            fields.append('values')

class MConstant(Mexpr):  # pragma: no cover
    """"""
    _types = Constant

    def __init__(
        self,
        value: _Patterns,  # Ellipsis here is not a wildcard but a concrete value to match
        kind: _Patterns = ...,
    ) -> None:
        self._fields = fields = ['value']
        self.value = value

        if kind is not ...:
            self.kind = kind
            fields.append('kind')

class MAttribute(Mexpr):  # pragma: no cover
    """"""
    _types = Attribute

    def __init__(
        self,
        value: _Patterns = ...,
        attr: _Patterns = ...,
        ctx: _Patterns = ...,
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

class MSubscript(Mexpr):  # pragma: no cover
    """"""
    _types = Subscript

    def __init__(
        self,
        value: _Patterns = ...,
        slice: _Patterns = ...,
        ctx: _Patterns = ...,
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

class MStarred(Mexpr):  # pragma: no cover
    """"""
    _types = Starred

    def __init__(
        self,
        value: _Patterns = ...,
        ctx: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MName(Mexpr):  # pragma: no cover
    """"""
    _types = Name

    def __init__(
        self,
        id: _Patterns = ...,
        ctx: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if id is not ...:
            self.id = id
            fields.append('id')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MList(Mexpr):  # pragma: no cover
    """"""
    _types = List

    def __init__(
        self,
        elts: _Patterns = ...,
        ctx: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MTuple(Mexpr):  # pragma: no cover
    """"""
    _types = Tuple

    def __init__(
        self,
        elts: _Patterns = ...,
        ctx: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if elts is not ...:
            self.elts = elts
            fields.append('elts')

        if ctx is not ...:
            self.ctx = ctx
            fields.append('ctx')

class MSlice(Mexpr):  # pragma: no cover
    """"""
    _types = Slice

    def __init__(
        self,
        lower: _Patterns = ...,
        upper: _Patterns = ...,
        step: _Patterns = ...,
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

class MLoad(Mexpr_context):  # pragma: no cover
    """"""
    _types = Load

    def __init__(self) -> None:
        pass

class MStore(Mexpr_context):  # pragma: no cover
    """"""
    _types = Store

    def __init__(self) -> None:
        pass

class MDel(Mexpr_context):  # pragma: no cover
    """"""
    _types = Del

    def __init__(self) -> None:
        pass

class MAnd(Mboolop):  # pragma: no cover
    """"""
    _types = And

    def __init__(self) -> None:
        pass

class MOr(Mboolop):  # pragma: no cover
    """"""
    _types = Or

    def __init__(self) -> None:
        pass

class MAdd(Moperator):  # pragma: no cover
    """"""
    _types = Add

    def __init__(self) -> None:
        pass

class MSub(Moperator):  # pragma: no cover
    """"""
    _types = Sub

    def __init__(self) -> None:
        pass

class MMult(Moperator):  # pragma: no cover
    """"""
    _types = Mult

    def __init__(self) -> None:
        pass

class MMatMult(Moperator):  # pragma: no cover
    """"""
    _types = MatMult

    def __init__(self) -> None:
        pass

class MDiv(Moperator):  # pragma: no cover
    """"""
    _types = Div

    def __init__(self) -> None:
        pass

class MMod(Moperator):  # pragma: no cover
    """"""
    _types = Mod

    def __init__(self) -> None:
        pass

class MPow(Moperator):  # pragma: no cover
    """"""
    _types = Pow

    def __init__(self) -> None:
        pass

class MLShift(Moperator):  # pragma: no cover
    """"""
    _types = LShift

    def __init__(self) -> None:
        pass

class MRShift(Moperator):  # pragma: no cover
    """"""
    _types = RShift

    def __init__(self) -> None:
        pass

class MBitOr(Moperator):  # pragma: no cover
    """"""
    _types = BitOr

    def __init__(self) -> None:
        pass

class MBitXor(Moperator):  # pragma: no cover
    """"""
    _types = BitXor

    def __init__(self) -> None:
        pass

class MBitAnd(Moperator):  # pragma: no cover
    """"""
    _types = BitAnd

    def __init__(self) -> None:
        pass

class MFloorDiv(Moperator):  # pragma: no cover
    """"""
    _types = FloorDiv

    def __init__(self) -> None:
        pass

class MInvert(Munaryop):  # pragma: no cover
    """"""
    _types = Invert

    def __init__(self) -> None:
        pass

class MNot(Munaryop):  # pragma: no cover
    """"""
    _types = Not

    def __init__(self) -> None:
        pass

class MUAdd(Munaryop):  # pragma: no cover
    """"""
    _types = UAdd

    def __init__(self) -> None:
        pass

class MUSub(Munaryop):  # pragma: no cover
    """"""
    _types = USub

    def __init__(self) -> None:
        pass

class MEq(Mcmpop):  # pragma: no cover
    """"""
    _types = Eq

    def __init__(self) -> None:
        pass

class MNotEq(Mcmpop):  # pragma: no cover
    """"""
    _types = NotEq

    def __init__(self) -> None:
        pass

class MLt(Mcmpop):  # pragma: no cover
    """"""
    _types = Lt

    def __init__(self) -> None:
        pass

class MLtE(Mcmpop):  # pragma: no cover
    """"""
    _types = LtE

    def __init__(self) -> None:
        pass

class MGt(Mcmpop):  # pragma: no cover
    """"""
    _types = Gt

    def __init__(self) -> None:
        pass

class MGtE(Mcmpop):  # pragma: no cover
    """"""
    _types = GtE

    def __init__(self) -> None:
        pass

class MIs(Mcmpop):  # pragma: no cover
    """"""
    _types = Is

    def __init__(self) -> None:
        pass

class MIsNot(Mcmpop):  # pragma: no cover
    """"""
    _types = IsNot

    def __init__(self) -> None:
        pass

class MIn(Mcmpop):  # pragma: no cover
    """"""
    _types = In

    def __init__(self) -> None:
        pass

class MNotIn(Mcmpop):  # pragma: no cover
    """"""
    _types = NotIn

    def __init__(self) -> None:
        pass

class Mcomprehension(MAST):  # pragma: no cover
    """"""
    _types = comprehension

    def __init__(
        self,
        target: _Patterns = ...,
        iter: _Patterns = ...,
        ifs: _Patterns = ...,
        is_async: _Patterns = ...,
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

class MExceptHandler(Mexcepthandler):  # pragma: no cover
    """"""
    _types = ExceptHandler

    def __init__(
        self,
        type: _Patterns = ...,
        name: _Patterns = ...,
        body: _Patterns = ...,
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

class Marguments(MAST):  # pragma: no cover
    """This works like all the other match pattern classes except that it has an extra `_strict` parameter which
    controls how it matches against individual `arguments._all`. This parameter can also be set on a normal `AST`
    `arguments` class for the same effect.

    **Parameters:**
    - `_strict`: Set this to control matching, if not set defaults to `False`.
        - `True`: `posonlyargs` only match to `posonlyargs`, `kwonlyargs` to `kwonlyargs` and `args` only to `args`.
            Their associated defaults only match to the same type of default as well.
        - `False`: Same as `True` except that `args` in the pattern matches to `args`, `posonlyargs` or `kwonlyargs` in
            the target and `defaults` likewise can also match to `kw_defaults`. This allows the use of the standard args
            to search in all the args fields.
        - `None`: All types of args and defaults can match to each other.
    """
    _types = arguments

    def __init__(
        self,
        posonlyargs: _Patterns = ...,
        args: _Patterns = ...,
        vararg: _Patterns = ...,
        kwonlyargs: _Patterns = ...,
        kw_defaults: _Patterns = ...,
        kwarg: _Patterns = ...,
        defaults: _Patterns = ...,
        _all: _Patterns = ...,
        _strict: bool | None = False,
    ) -> None:
        self._fields = fields = []
        self._strict = _strict

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

        if _all is not ...:
            self._all = _all
            fields.append('_all')

class Marg(MAST):  # pragma: no cover
    """"""
    _types = arg

    def __init__(
        self,
        arg: _Patterns = ...,
        annotation: _Patterns = ...,
        type_comment: _Patterns = ...,
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

class Mkeyword(MAST):  # pragma: no cover
    """"""
    _types = keyword

    def __init__(
        self,
        arg: _Patterns = ...,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if arg is not ...:
            self.arg = arg
            fields.append('arg')

        if value is not ...:
            self.value = value
            fields.append('value')

class Malias(MAST):  # pragma: no cover
    """"""
    _types = alias

    def __init__(
        self,
        name: _Patterns = ...,
        asname: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if asname is not ...:
            self.asname = asname
            fields.append('asname')

class Mwithitem(MAST):  # pragma: no cover
    """"""
    _types = withitem

    def __init__(
        self,
        context_expr: _Patterns = ...,
        optional_vars: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if context_expr is not ...:
            self.context_expr = context_expr
            fields.append('context_expr')

        if optional_vars is not ...:
            self.optional_vars = optional_vars
            fields.append('optional_vars')

class Mmatch_case(MAST):  # pragma: no cover
    """"""
    _types = match_case

    def __init__(
        self,
        pattern: _Patterns = ...,
        guard: _Patterns = ...,
        body: _Patterns = ...,
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

class MMatchValue(Mpattern):  # pragma: no cover
    """"""
    _types = MatchValue

    def __init__(
        self,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MMatchSingleton(Mpattern):  # pragma: no cover
    """"""
    _types = MatchSingleton

    def __init__(
        self,
        value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if value is not ...:
            self.value = value
            fields.append('value')

class MMatchSequence(Mpattern):  # pragma: no cover
    """"""
    _types = MatchSequence

    def __init__(
        self,
        patterns: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if patterns is not ...:
            self.patterns = patterns
            fields.append('patterns')

class MMatchMapping(Mpattern):  # pragma: no cover
    """"""
    _types = MatchMapping

    def __init__(
        self,
        keys: _Patterns = ...,
        patterns: _Patterns = ...,
        rest: _Patterns = ...,
        _all: _Patterns = ...,
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

        if _all is not ...:
            self._all = _all
            fields.append('_all')

class MMatchClass(Mpattern):  # pragma: no cover
    """"""
    _types = MatchClass

    def __init__(
        self,
        cls: _Patterns = ...,
        patterns: _Patterns = ...,
        kwd_attrs: _Patterns = ...,
        kwd_patterns: _Patterns = ...,
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

class MMatchStar(Mpattern):  # pragma: no cover
    """"""
    _types = MatchStar

    def __init__(
        self,
        name: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

class MMatchAs(Mpattern):  # pragma: no cover
    """"""
    _types = MatchAs

    def __init__(
        self,
        pattern: _Patterns = ...,
        name: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if pattern is not ...:
            self.pattern = pattern
            fields.append('pattern')

        if name is not ...:
            self.name = name
            fields.append('name')

class MMatchOr(Mpattern):  # pragma: no cover
    """"""
    _types = MatchOr

    def __init__(
        self,
        patterns: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if patterns is not ...:
            self.patterns = patterns
            fields.append('patterns')

class MTypeIgnore(Mtype_ignore):  # pragma: no cover
    """"""
    _types = TypeIgnore

    def __init__(
        self,
        lineno: _Patterns = ...,
        tag: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if lineno is not ...:
            self.lineno = lineno
            fields.append('lineno')

        if tag is not ...:
            self.tag = tag
            fields.append('tag')

class MTypeVar(Mtype_param):  # pragma: no cover
    """"""
    _types = TypeVar

    def __init__(
        self,
        name: _Patterns = ...,
        bound: _Patterns = ...,
        default_value: _Patterns = ...,
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

class MParamSpec(Mtype_param):  # pragma: no cover
    """"""
    _types = ParamSpec

    def __init__(
        self,
        name: _Patterns = ...,
        default_value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if default_value is not ...:
            self.default_value = default_value
            fields.append('default_value')

class MTypeVarTuple(Mtype_param):  # pragma: no cover
    """"""
    _types = TypeVarTuple

    def __init__(
        self,
        name: _Patterns = ...,
        default_value: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if name is not ...:
            self.name = name
            fields.append('name')

        if default_value is not ...:
            self.default_value = default_value
            fields.append('default_value')

class M_ExceptHandlers(M_slice):  # pragma: no cover
    """"""
    _types = _ExceptHandlers

    def __init__(
        self,
        handlers: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if handlers is not ...:
            self.handlers = handlers
            fields.append('handlers')

class M_match_cases(M_slice):  # pragma: no cover
    """"""
    _types = _match_cases

    def __init__(
        self,
        cases: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if cases is not ...:
            self.cases = cases
            fields.append('cases')

class M_Assign_targets(M_slice):  # pragma: no cover
    """"""
    _types = _Assign_targets

    def __init__(
        self,
        targets: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if targets is not ...:
            self.targets = targets
            fields.append('targets')

class M_decorator_list(M_slice):  # pragma: no cover
    """"""
    _types = _decorator_list

    def __init__(
        self,
        decorator_list: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if decorator_list is not ...:
            self.decorator_list = decorator_list
            fields.append('decorator_list')

class M_arglikes(M_slice):  # pragma: no cover
    """"""
    _types = _arglikes

    def __init__(
        self,
        arglikes: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if arglikes is not ...:
            self.arglikes = arglikes
            fields.append('arglikes')

class M_comprehensions(M_slice):  # pragma: no cover
    """"""
    _types = _comprehensions

    def __init__(
        self,
        generators: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if generators is not ...:
            self.generators = generators
            fields.append('generators')

class M_comprehension_ifs(M_slice):  # pragma: no cover
    """"""
    _types = _comprehension_ifs

    def __init__(
        self,
        ifs: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if ifs is not ...:
            self.ifs = ifs
            fields.append('ifs')

class M_aliases(M_slice):  # pragma: no cover
    """"""
    _types = _aliases

    def __init__(
        self,
        names: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if names is not ...:
            self.names = names
            fields.append('names')

class M_withitems(M_slice):  # pragma: no cover
    """"""
    _types = _withitems

    def __init__(
        self,
        items: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if items is not ...:
            self.items = items
            fields.append('items')

class M_type_params(M_slice):  # pragma: no cover
    """"""
    _types = _type_params

    def __init__(
        self,
        type_params: _Patterns = ...,
    ) -> None:
        self._fields = fields = []

        if type_params is not ...:
            self.type_params = type_params
            fields.append('type_params')


# ......................................................................................................................

class M_Pattern_One(M_Pattern):
    """Base class for most single-pattern classes. @private"""

    _requires = 'pattern'  # for printing error message

    pat: _Patterns  ; """@private"""
    pat_tag: str | None  ; """@private"""
    static_tags: Mapping[str, Any]  ; """@private"""

    def __init__(self, anon_pat: _Patterns | _NotSet = NotSet, /, **tags) -> None:
        # self._validate_tags(tags)

        if anon_pat is not NotSet:
            self.pat = anon_pat
            self.pat_tag = None
            self.static_tags = tags

        elif (pat_tag := next(iter(tags), _SENTINEL)) is _SENTINEL:
            raise ValueError(f'{self.__class__.__qualname__} requires {self._requires}')

        else:
            self.pat = tags.pop(pat_tag)
            self.pat_tag = pat_tag
            self.static_tags = tags

    def __repr__(self) -> str:
        tag = f'{pat_tag}={_rpr(self.pat)}' if (pat_tag := self.pat_tag) else _rpr(self.pat)
        extra = self._repr_extra()

        if static_tags := self.static_tags:
            params = [tag, *extra, ', '.join(f'{t}={_rpr(p)}' for t, p in static_tags.items())]
        else:
            params = [tag, *extra]

        return f'{self.__class__.__qualname__}({", ".join(params)})'

    def _repr_extra(self) -> list[str]:
        return _EMPTY_LIST

    def _leaf_asts(self) -> tp_Set[type[AST]] | None:
        return _LEAF_ASTS_FUNCS.get((p := self.pat).__class__, _leaf_asts_default)(p)


class M_Pattern_Many(M_Pattern):
    """Base class for multi-pattern classes `MOR` and `MAND`. @private"""

    pats: list[_Patterns]  ; """@private"""
    pat_tags: list[str | None]  ; """@private"""

    def __init__(self, *anon_pats: _Patterns, **tagged_pats: _Patterns) -> None:
        # self._validate_tags(tagged_pats)

        if anon_pats:
            pats = list(anon_pats)
            pat_tags = [None] * len(pats)

            if tagged_pats:
                pats.extend(tagged_pats.values())
                pat_tags.extend(tagged_pats.keys())

        elif tagged_pats:
            pats = list(tagged_pats.values())
            pat_tags = list(tagged_pats.keys())

        else:
            raise ValueError(f'{self.__class__.__qualname__} requires at least one pattern')

        self.pats = pats
        self.pat_tags = pat_tags

    def __repr__(self) -> str:
        name = self.__class__.__name__
        tags = ', '.join(f'{t}={_rpr(p)}' if t else _rpr(p) for t, p in zip(self.pat_tags, self.pats, strict=True))

        return f'{name}({tags})'


class M(M_Pattern_One):
    """Tagging pattern container. If the given pattern matches then tags specified here will be returned in the
    `FSTMatch` result object. The tags can be static values but also the matched node can be returned in a given tag if
    the pattern is passed as a keyword parameter (the first one). This is useful for matching subparts of a target as
    the whole match target is already returned in `FSTMatch.matched` on success.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched node is not returned in tags. If this is
        missing then there must be at least one element in `tags` and the first keyword there will be taken to be the
        pattern to match and the name of the tag to use for the matched node.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`).

    **Examples:**

    >>> M('var') .match(Name(id='NOT_VAR'))

    >>> M('var') .match(Name(id='var'))
    <FSTMatch Name(id='var')>

    >>> M('var', tag='static') .match(Name(id='var'))
    <FSTMatch Name(id='var') {'tag': 'static'}>

    >>> M(node='var', tag='static') .match(Name(id='var'))
    <FSTMatch Name(id='var') {'node': Name(id='var'), 'tag': 'static'}>

    >>> M(M(M(node='var'), add1=1), add2=2) .match(Name(id='var'))
    <FSTMatch Name(id='var') {'node': Name(id='var'), 'add1': 1, 'add2': 2}>
    """

    __init__ = M_Pattern_One.__init__  # for the documentation

    def _match(self, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        m = _MATCH_FUNCS.get((p := self.pat).__class__, _match_default)(p, tgt, mstate)

        if m is None:
            return None

        if pat_tag := self.pat_tag:
            if mstate.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')

            if m:
                return {**m, pat_tag: tgt, **self.static_tags}

            return {pat_tag: tgt, **self.static_tags}

        if m:
            return dict(m, **self.static_tags)

        return self.static_tags


class MNOT(M_Pattern_One):
    """Tagging NOT logic pattern container. If the given pattern **DOES NOT** match then tags specified here will be
    returned in the `FSTMatch` result object. The tags can be specified with static values but also the unmatched node
    can be returned in a given tag name.

    Any tags that were being propagated up from successful matches are discarded since that constitutes an unsuccessful
    match for this node. And any unsuccessful matches were not propagating any tags up anyway. So this node guarantees
    that the only tags that it returns are ones that it itself provides.

    **Parameters:**
    - `anon_pat`: If the pattern to not match is provided in this then the unmatched node is not returned in tags. If
        this is missing then there must be at least one element in `tags` and the first keyword there will be taken to
        be the pattern to not match and the name of the tag to use for the unmatched node.
    - `tags`: Any static tags to return on an unsuccessful match (including the pattern to not match as the first
        keyword if not provided in `anon_pat`).

    **Examples:**

    >>> MNOT('var') .match(Name(id='NOT_VAR'))
    <FSTMatch Name(id='NOT_VAR')>

    >>> MNOT('var') .match(Name(id='var'))

    >>> MNOT('var', tag='static') .match(Name(id='NOT_VAR'))
    <FSTMatch Name(id='NOT_VAR') {'tag': 'static'}>

    >>> MNOT(node='var', tag='static') .match(Name(id='NOT_VAR'))
    <FSTMatch Name(id='NOT_VAR') {'node': Name(id='NOT_VAR'), 'tag': 'static'}>

    >>> MNOT(MNOT(node='var', tag='static')) .match(Name(id='NOT_VAR'))

    >>> MNOT(MNOT(MNOT(node='var'), add1=1), add2=2) .match(Name(id='NOT_VAR'))
    <FSTMatch Name(id='NOT_VAR') {'add2': 2}>
    """

    __init__ = M_Pattern_One.__init__  # for the documentation

    @staticmethod
    def _match(self: MNOT, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        m = _MATCH_FUNCS.get((p := self.pat).__class__, _match_default)(p, tgt, mstate)

        if m is not None:
            return None

        if pat_tag := self.pat_tag:
            if mstate.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')

            return {pat_tag: tgt, **self.static_tags}

        return self.static_tags

    def _leaf_asts(self) -> tp_Set[type[AST]] | None:
        leaf_asts = _LEAF_ASTS_FUNCS.get((p := self.pat).__class__, _leaf_asts_default)(p)

        if not leaf_asts:
            if leaf_asts is None:
                return None

            return ASTS_LEAF__ALL

        elif len(leaf_asts) >= _LEN_ASTS_LEAF__ALL:  # >= because maybe some extra node types got in there from the future
            return _EMPTY_SET

        return ASTS_LEAF__ALL - leaf_asts


class MOR(M_Pattern_Many):
    """Simple OR pattern. Matches if any of the given patterns match.

    **Parameters:**
    - `anon_pats`: Patterns that constitute a successful match, only need one to match. Checked in order and exit on
        first successful match.
    - `tagged_pats`: Patterns that constitute a successful match, only need one to match. Checked in order and exit on
        first successful match. The first target matched with any one of these patterns will be returned in its
        corresponding tag (keyword name).

    **Examples:**

    >>> MOR('a', this='b') .match(FST('a'))
    <FSTMatch <Name ROOT 0,0..0,1>>

    >>> MOR('a', this='b') .match(FST('b'))
    <FSTMatch <Name ROOT 0,0..0,1> {'this': <Name ROOT 0,0..0,1>}>

    >>> MOR('a', this='b') .match(FST('c'))

    Mixed pattern types and nesting.

    >>> pat = MOR(Name('good'), M(m=Call, static='tag'), st=Starred)

    >>> pat.match(FST('bad'))

    >>> pat.match(FST('good'))
    <FSTMatch <Name ROOT 0,0..0,4>>

    >>> pat.match(FST('*starred'))
    <FSTMatch <Starred ROOT 0,0..0,8> {'st': <Starred ROOT 0,0..0,8>}>

    >>> pat.match(FST('call()'))
    <FSTMatch <Call ROOT 0,0..0,6> {'m': <Call ROOT 0,0..0,6>, 'static': 'tag'}>

    >>> pat.match(FST('bin + op'))
"""

    __init__ = M_Pattern_Many.__init__  # for the documentation

    def _match(self, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        for i, p in enumerate(self.pats):
            m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, mstate)

            if m is not None:
                if pat_tag := self.pat_tags[i]:
                    if mstate.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                        raise MatchError('match found an AST node without an FST')

                    return {**m, pat_tag: tgt}

                return m

        return None

    def _leaf_asts(self) -> tp_Set[type[AST]] | None:
        leaf_asts = set()

        for pat in self.pats:
            la = _LEAF_ASTS_FUNCS.get(pat.__class__, _leaf_asts_default)(pat)

            if la is None:  # indeterminate ends search immediately
                return None

            if len(la) >= _LEN_ASTS_LEAF__ALL:  # early out because we hit all possible types
                return la

            leaf_asts.update(la)

            if len(leaf_asts) >= _LEN_ASTS_LEAF__ALL:  # another early out
                return leaf_asts

        return leaf_asts


class MAND(M_Pattern_Many):
    """Simple AND pattern. Matches only if all of the given patterns match. This pattern isn't terribly useful for
    straight node matches as if you try to combine different node types using this node their types become mutually
    exclusive and will make this always fail. Where this can come in handy for example is when examining list fields
    for multiple conditions.

    **Parameters:**
    - `anon_pats`: Patterns that need to match to constitute a success. Checked in order.
    - `tagged_pats`: Patterns that need to match to constitute a success. Checked in order. All the targets matched with
        these patterns will be returned in their corresponding tags (keyword names).

    **Examples:**

    The following will always fail as a node cannot be both a `Name` AND a `Call` at the same time.

    >>> MAND(Name, Call) .match(FST('name'))

    >>> MAND(Name, Call) .match(FST('call()'))

    More sensical usage below, for example that a list starts with `a` and contains at least two `b`.

    >>> pat = MList(MAND(['a', MQSTAR], [MQSTAR, 'b', MQSTAR, 'b', MQSTAR]))

    >>> pat.match(FST('[a, b, c]'))

    >>> pat.match(FST('[a, b, b, c]'))
    <FSTMatch <List ROOT 0,0..0,12>>

    >>> pat.match(FST('[d, a, b, b, c]'))

    >>> pat.match(FST('[a, x, b, y, z, b, c, b]'))
    <FSTMatch <List ROOT 0,0..0,24>>
    """

    __init__ = M_Pattern_Many.__init__  # for the documentation

    def _match(self, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        if mstate.is_FST and isinstance(tgt, AST):
            if not (tgtf := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')
        else:
            tgtf = tgt

        tagss = mstate.new_tagss()

        for i, p in enumerate(self.pats):
            m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, mstate)

            if m is None:
                return mstate.discard_tagss()

            if pat_tag := self.pat_tags[i]:
                tagss.append({**m, pat_tag: tgtf})
            elif m:
                tagss.append(m)

        return mstate.pop_merge_tagss()

    def _leaf_asts(self) -> tp_Set[type[AST]] | None:
        leaf_asts = ASTS_LEAF__ALL

        for pat in self.pats:
            la = _LEAF_ASTS_FUNCS.get(pat.__class__, _leaf_asts_default)(pat)

            if not la:  # early out because everything gone
                if la is None:  # indeterminate ends search immediately
                    return None

                return la

            leaf_asts = leaf_asts & la

            if not leaf_asts:  # another early out
                return leaf_asts

        return leaf_asts


class MMAYBE(M_Pattern_One):
    """This is a pattern or `None` match. It can be used to optionally match single-element fields which may or may not
    be present. That is, both a normal value which matches the pattern and a `None` value are considered a successful
    match. A non-`None` value which does NOT match the pattern is a failure.

    This is essentially `MOR(pattern, None)`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched node is not returned in tags. If this is
        missing then there must be at least one element in `tags` and the first keyword there will be taken to be the
        pattern to match and the name of the tag to use for the matched node.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    Single optional nodes.

    >>> MFunctionDef(returns=MMAYBE('int')) .match(FST('def f(): pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,13>>

    >>> MFunctionDef(returns=MMAYBE('int')) .match(FST('def f() -> int: pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,20>>

    >>> MFunctionDef(returns=MMAYBE('int')) .match(FST('def f() -> str: pass'))

    Parts of multinode elements.

    >>> MDict([MMAYBE('a')], ['b']) .match(FST('{a: b}'))
    <FSTMatch <Dict ROOT 0,0..0,6>>

    >>> MDict([MMAYBE('a')], ['b']) .match(FST('{**b}'))
    <FSTMatch <Dict ROOT 0,0..0,5>>

    >>> MDict([MMAYBE('a')], ['b']) .match(FST('{x: b}'))

    Non-node primitive fields.

    >>> MExceptHandler(name=MMAYBE('n')) .match(FST('except x as n: pass'))
    <FSTMatch <ExceptHandler ROOT 0,0..0,19>>

    >>> MExceptHandler(name=MMAYBE('n')) .match(FST('except x as o: pass'))

    >>> MExceptHandler(name=MMAYBE('n')) .match(FST('except x: pass'))
    <FSTMatch <ExceptHandler ROOT 0,0..0,14>>
    """

    __init__ = M_Pattern_One.__init__  # for the documentation

    def _match(self, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        if tgt is None:
            if pat_tag := self.pat_tag:
                return {pat_tag: [], **self.static_tags}

            return self.static_tags

        pat = self.pat
        m = _MATCH_FUNCS.get(pat.__class__, _match_default)(pat, tgt, mstate)

        if m is None:
            return None

        if pat_tag := self.pat_tag:
            if mstate.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')

            if m:
                return {**m, pat_tag: tgt, **self.static_tags}

            return {pat_tag: tgt, **self.static_tags}

        if m:
            return dict(m, **self.static_tags)

        return self.static_tags


class MTYPES(M_Pattern):
    """This pattern matches any one of the given types and arbitrary fields if present. This is essentially
    `MAND(MOR(*types), MAST(**fields))`. But the types must be actual types, not other patterns.

    **Note:** Since there are several fields which can be either an individual element or list of elements, matching
    a list pattern vs. a non-list and vice versa is just treated as a non-match.

    **Parameters:**
    - `anon_types`: If the types to match are provided in this then the matched node is not returned in tags. If this is
        missing then there must be at least one element in `tags` and the first keyword there will be taken to be the
        types to match and the name of the tag to use for the matched node. The types to match are an iterable of `AST`
        or `MAST` **TYPES**, not instances. In order to match successfully the target must be at least one of these
        types (non-leaf types like `stmt` included). If you just want to match any possible `AST` type with a given set
        of fields you can use `MAST(**fields)` instead of this.
    - `fields`: Field names which must be present (unless wildcard `...`) along with the patterns they need to match.

    **Examples:**

    Whether a statement type that CAN have a docstring actually has a docstring.

    >>> pat = MTYPES(
    ...     (ClassDef, FunctionDef, AsyncFunctionDef),
    ...     body=[MExpr(MConstant(str)), MQSTAR],
    ... )

    >>> pat.match(FST('def f(): "docstr"; pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,23>>

    >>> pat.match(FST('if 1: "NOTdocstr"'))

    >>> pat.match(FST('def f(): pass; "NOTdocstr"'))

    >>> pat.match(FST('class cls: "docstr"; pass'))
    <FSTMatch <ClassDef ROOT 0,0..0,25>>

    >>> pat = MTYPES(
    ...     tag=(ClassDef, FunctionDef, AsyncFunctionDef),
    ...     body=[MExpr(MConstant(str)), MQSTAR],
    ... )

    >>> pat.match(FST('class cls: "docstr"; pass'))
    <FSTMatch <ClassDef ROOT 0,0..0,25> {'tag': <ClassDef ROOT 0,0..0,25>}>
    """

    pat_tag: str | None  ; """@private"""
    fields: Mapping[str, _Patterns]  ; """@private"""

    def __init__(self, anon_types: Iterable[type[AST | MAST]] | _NotSet = NotSet, /, **fields: _Patterns) -> None:
        if anon_types is not NotSet:
            pat_tag = None
        elif (pat_tag := next(iter(fields), None)) is None:
            raise ValueError('MTYPES requires types')
        else:
            anon_types = fields.pop(pat_tag)

        ts = {}

        for t in anon_types:
            if not isinstance(t, type):
                raise ValueError('MTYPES types can only be AST or MAST')
            elif issubclass(t, MAST):
                t = t._types  # will be a single type, can be non-leaf
            elif not issubclass(t, AST):
                raise ValueError('MTYPES types can only be AST or MAST')

            ts[t] = True

        self._types = types = tuple(ts)
        self.pat_tag = pat_tag
        self.fields = fields

        if not types:
            raise ValueError('MTYPES requires at least one AST type to match')

        if fields:
            self._fields = tuple(fields)

            for field, value in fields.items():
                setattr(self, field, value)

    def __repr__(self) -> str:
        name = self.__class__.__name__
        types = self._types
        types = f'({", ".join(_rpr(e) for e in types)}{"," if len(types) == 1 else ""})'

        if fields := self.fields:
            return f'{name}({types}, {", ".join(f"{f}={_rpr(v)}" for f, v in fields.items())})'

        return f'{name}({types})'

    def _match(self, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        if (m := _match_node(self, tgt, mstate)) is None:
            return None

        if (pat_tag := self.pat_tag) is None:
            return m

        if mstate.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
            raise MatchError('match found an AST node without an FST')

        return {**m, pat_tag: tgt}

    def _leaf_asts(self) -> tp_Set[type[AST]] | None:
        leaf_asts = set()

        for t in self._types:
            la = AST2ASTSLEAF[t]

            if len(la) >= _LEN_ASTS_LEAF__ALL:  # early out because we hit all possible types
                return la

            leaf_asts.update(la)

            if len(leaf_asts) >= _LEN_ASTS_LEAF__ALL:  # another early out
                return leaf_asts

        return leaf_asts


class MRE(M_Pattern):
    """Tagging regex pattern. Normal `re.Pattern` can be used and that will just be checked using `re.match()` and the
    `re.Match` object is lost. If this pattern is used instead then you can specify the use of `re.match()` or
    `re.search()`, as well as allowing the `re.Match` object to be returned as a tag.

    **Parameters:**
    - `anon_re_pat`: If the pattern to match is provided in this (either as a `str` to compile or an already compiled
        `re.Pattern`) then the matched `re.Match` is not returned in tags. If this is missing then there must be at
        least one element in `tags` and the first keyword there will be taken to be the pattern to match and the name of
        the tag to use for the matched `re.Match` object.
    - `flags`: If passing a `str` as the pattern then these are the `re` flags to pass to `re.compile()`. If passing an
        already compiled `re.Pattern` then this must remain `0`.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_re_pat`).

    **Examples:**

    >>> from fst.docs import ppmatch  # pretty-print FSTMatch

    >>> MRE('good|bad|ugly') .match(Name('ugly'))
    <FSTMatch Name(id='ugly')>

    >>> MRE('good|bad|ugly') .match(Name('passable'))

    Has bad in it.

    >>> ppmatch(MRE(tag='.*bad.*') .match(arg('this_arg_is_not_so_bad')))
    <FSTMatch arg(arg='this_arg_is_not_so_bad', annotation=None, type_comment=None)
      {'tag': <re.Match object; span=(0, 22), match='this_arg_is_not_so_bad'>}>

    Another way so we can get the exact location from the `re.Match` object.

    >>> ppmatch(MRE(tag='bad', search=True) .match(arg('this_arg_is_not_so_bad')))
    <FSTMatch arg(arg='this_arg_is_not_so_bad', annotation=None, type_comment=None)
      {'tag': <re.Match object; span=(19, 22), match='bad'>}>

    >>> ppmatch(MDict(_all=[MQSTAR(t=MRE('a: .'))]) .match(FST('{a: b, a: z}')))
    <FSTMatch <Dict ROOT 0,0..0,12>
      't': [
        <FSTMatch <<Dict ROOT 0,0..0,12>._all[:1]>>,
        <FSTMatch <<Dict ROOT 0,0..0,12>._all[1:2]>>,
      ],
    }>
    """

    pat: re_Pattern  ; """@private"""
    pat_tag: str | None  ; """@private"""
    static_tags: Mapping[str, Any]  ; """@private"""
    search: bool  ; """@private"""

    def __init__(
        self, anon_re_pat: str | re_Pattern | _NotSet = NotSet, /, flags: int = 0, search: bool = False, **tags
    ) -> None:
        # self._validate_tags(tags)

        if anon_re_pat is not NotSet:
            pat_tag = None
        elif (pat_tag := next(iter(tags), None)) is None:
            raise ValueError('MRE requires pattern')
        else:
            anon_re_pat = tags.pop(pat_tag)

        if not isinstance(anon_re_pat, re_Pattern):
            anon_re_pat = re.compile(anon_re_pat, flags)
        elif flags:
            raise ValueError('MRE cannot take flags for already compiled re.Pattern')

        self.pat = anon_re_pat
        self.pat_tag = pat_tag
        self.search = search
        self.static_tags = tags

    def __repr__(self) -> str:
        name = self.__class__.__name__
        pat = _rpr(self.pat)
        pat_tag = self.pat_tag
        tags = [f'{pat_tag}={pat}' if pat_tag else pat]

        if self.search:
            tags.append('search=True')

        tags.extend(f'{t}={_rpr(p)}' for t, p in self.static_tags.items())

        return f'{name}({", ".join(tags)})'

    def _match(self, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        """Regex match or search pattern against direct `str` or `bytes` value or source if `tgt` is an actual node. Will
        use `FST` source from the tree and unparse a non-`FST` `AST` node for the check. Returns `re.Match` object if is
        requested."""

        pat = self.pat
        re_func = pat.search if self.search else pat.match

        if (m := _match_re_Pattern(pat, tgt, mstate, re_func)) is None:
            return None

        if pat_tag := self.pat_tag:
            return {pat_tag: m, **self.static_tags}

        return self.static_tags


class MCB(M_Pattern_One):
    """Callback to check target, which can be a node (`AST` or `FST` depending on the type of tree the pattern was
    called on) or constant or a list of `AST`s or constants.

    **Parameters:**
    - `anon_callback`: The function to call on each target to check. Depending on where in the pattern structure this
        pattern is used, the function may be called with a node or a primitive, or even a list of elements. Further,
        depending on the initial target of the match, the node may be `FST` if the target was an `FST` node and `AST`
        otherwise. If the function returns a truthy value then the match is considered a success, and likewise falsey
        means failure. If this is not provided then the callback is taken from the first keyword in `tags` just like for
        the `M` pattern.
    - `tag_ret`: If this is set to `True` then the truthy return value is returned in the pattern tag instead of the
        target matched. This only applies if the callback is passed as the first keyword in `tags` instead of in
        `anon_callback`, as in that case no target tag is available to return. Also keep in mind the "truthy value" bit
        in case a successful match might want to return a falsey value, it would need to be accomodated somehow (wrapped
        in a tuple maybe). Or just provide an explicit `fail_obj` to check against to determine failure.
    - `fail_obj`: An explicit object to check identity against to determine if the callback failed.
    - `pass_tags`: If `False` then the normal single-object callback format is used. If `True` then will call the
        callback with an additional parameter which is a tag getter function which allows the callback to get tags which
        have been set up to this point. The tag getter works in the same way as `dict.get()` and the default for no tag
        is `fst.match.NotSet`.

    **Examples:**

    >>> in_range = lambda x: 2 < x < 8
    >>> pat = MConstant(MCB(in_range))

    >>> pat.match(FST('1'))

    >>> pat.match(FST('3'))
    <FSTMatch <Constant ROOT 0,0..0,1>>

    >>> pat.match(FST('7'))
    <FSTMatch <Constant ROOT 0,0..0,1>>

    >>> pat.match(FST('10'))

    Check for only parenthesized tuples.

    >>> pat = MCB(FST.is_parenthesized_tuple)

    >>> pat.match(FST('x, y, z'))

    >>> pat.match(FST('(x, y, z)'))
    <FSTMatch <Tuple ROOT 0,0..0,9>>

    >>> pat.match(FST('[x, y, z]'))

    Get node along with name in uppercase.

    >>> pat = M(node=Name(MCB(upper=str.upper, tag_ret=True)))

    >>> pat.match(FST('a.b'))

    >>> pat.match(FST('some_name'))
    <FSTMatch <Name ROOT 0,0..0,9> {'upper': 'SOME_NAME', 'node': <Name ROOT 0,0..0,9>}>

    An explicit fail object can be provided in case you want to be able to tag falsey values directly, it is checked by
    identity.

    >>> MCB(tag=lambda f: False, tag_ret=True, fail_obj=None) .match(FST('a'))
    <FSTMatch <Name ROOT 0,0..0,1> {'tag': False}>

    >>> MCB(tag=lambda f: None, tag_ret=True, fail_obj=None) .match(FST('a'))

    The type of node passed to the callback depends on the type of tree that `match()` is called on.

    >>> pat = MCB(lambda n: print(type(n)))

    >>> pat.match(Name('name'))
    <class 'ast.Name'>

    >>> pat.match(FST('name'))
    <class 'fst.fst.FST'>

    A tag getter function can be passed to the callback so it can request tags that have been set so far.

    >>> m = M(prev=MCB(
    ...     lambda t, g: (print(f"this: {t}, prev: {g('prev')}"),),
    ...     pass_tags=True,
    ... ))

    >>> MList([m, m, m]) .match(FST('[a, b, c]'))
    this: <Name 0,1..0,2>, prev: <NotSet>
    this: <Name 0,4..0,5>, prev: <Name 0,1..0,2>
    this: <Name 0,7..0,8>, prev: <Name 0,4..0,5>
    <FSTMatch <List ROOT 0,0..0,9> {'prev': <Name 0,7..0,8>}>
    """

    CallbackType = (
        Callable[[_Target], object] |
        Callable[[_TargetFST], object] |
        Callable[[_Target, Callable[[str, object], object]], object] |
        Callable[[_TargetFST, Callable[[str, object], object]], object]
    )
    """Depending on if the match target is an `FST` or `AST` and if the `MCB` parameter `pass_tags` is `True` or
    `False`, this callback will be one of:

    - `Callable[[[AST | constant]], object]`
    - `Callable[[[FST | constant]], object]`
    - `Callable[[[AST | constant], Callable[[str, object], object]], object]`
    - `Callable[[[FST | constant], Callable[[str, object], object]], object]`

    Where `constant` is `ellipsis | int | float | complex | str | bytes | bool | None`.
    """


    _requires = 'callback'  # for printing error message

    pat: CallbackType  ; """@private"""
    tag_ret: bool  ; """@private"""
    fail_obj: object  ; """@private"""
    pass_tags: bool  ; """@private"""

    def __init__(
        self,
        anon_callback: CallbackType | _NotSet = NotSet,
        /,
        tag_ret: bool = False,
        fail_obj: object = NotSet,
        pass_tags: bool = False,
        **tags,
    ) -> None:
        M_Pattern_One.__init__(self, anon_callback, **tags)

        if tag_ret and anon_callback is not NotSet:
            raise ValueError('MCB can never tag the callback return since the callback does not have a tag')

        self.tag_ret = tag_ret
        self.fail_obj = fail_obj
        self.pass_tags = pass_tags

    def __repr__(self) -> str:
        params =[f'{pat_tag}={self.pat.__qualname__}' if (pat_tag := self.pat_tag) else self.pat.__qualname__]

        if tag_ret := self.tag_ret:
            params.append(f'tag_ret={tag_ret}')

        if (fail_obj := self.fail_obj) is not NotSet:
            params.append(f'fail_obj={_rpr(fail_obj)}')

        if static_tags := self.static_tags:
            params.append(', '.join(f'{t}={_rpr(p)}' for t, p in static_tags.items()))

        return f'{self.__class__.__qualname__}({", ".join(params)})'

    def _match(self, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        if not mstate.is_FST or not isinstance(tgt, AST):
            m = self.pat(tgt, mstate.get_tag) if self.pass_tags else self.pat(tgt)
        elif tgt := getattr(tgt, 'f', None):
            m = self.pat(tgt, mstate.get_tag) if self.pass_tags else self.pat(tgt)
        else:
            raise MatchError('match found an AST node without an FST')

        fail_obj = self.fail_obj

        if (not m if fail_obj is NotSet else m is fail_obj):
            return None

        if pat_tag := self.pat_tag:
            if self.tag_ret:
                tgt = m

            return {pat_tag: tgt, **self.static_tags}

        return self.static_tags


class MTAG(M_Pattern_One):
    """Match previously matched node (backreference). Looks through tags of current matches and if found then attempts
    to match against the value of the tag. Meant for matching previously matched nodes but can match anything which can
    work as a valid pattern in a tag, however it got there.

    For the sake of sanity and efficiency, does not recurse into lists of `FSTMatch` objects that have already been
    built by quantifier patterns. Can match those tags if they are not being put into `FSTMatch` objects though.

    **Parameters:**
    - `anon_tag`: If the source tag to match is provided in this then the new matched node is not returned in tags. If
        this is missing then there must be at least one element in `tags` and the first keyword there will be taken to
        be the source tag to match and the name of the new tag to use for the matched node.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`).

    **Examples:**

    >>> from fst.docs import ppmatch  # pretty-print FSTMatch

    >>> MBinOp(M(left='a'), right=MTAG('left')) .match(FST('a + a'))
    <FSTMatch <BinOp ROOT 0,0..0,5> {'left': <Name 0,0..0,1>}>

    >>> MBinOp(M(left='a'), right=MTAG('left')) .match(FST('a + b'))

    The tag must already have been matched, not be in the future.

    >>> MBinOp(MTAG('right'), right=M(right='a')) .match(FST('a + a'))

    Works just fine with quantifier patterns.

    >>> pat = MList([M(first='a'), MQSTAR(st=MTAG('first'))])

    >>> ppmatch(pat.match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      'first': <Name 0,1..0,2>,
      'st': [
        <FSTMatch <Name 0,4..0,5>>,
        <FSTMatch <Name 0,7..0,8>>,
      ],
    }>

    >>> pat.match(FST('[a, a, a, b]'))

    Can match previously matched multinode items from `Dict`, `MatchMapping` or `arguments`.

    >>> MDict(_all=[M(start=...), MQSTAR, MTAG('start')]) .match(FST('{1: a, 1: a}'))
    <FSTMatch <Dict ROOT 0,0..0,12> {'start': <<Dict ROOT 0,0..0,12>._all[:1]>}>
    """

    _requires = 'source tag'  # for printing error message

    pat: str  ; """@private"""  # this is really a source tag name here

    def __init__(self, anon_tag: str | _NotSet = NotSet, /, **tags) -> None:
        M_Pattern_One.__init__(self, anon_tag, **tags)

        # self._validate_tags((self.pat,))

    def _match(self, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
        if (p := mstate.get_tag(self.pat, _SENTINEL)) is _SENTINEL:
            return None

        if isinstance(p, fst.FST):
            p = p.a

        m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, mstate)

        if m is None:
            return None

        if pat_tag := self.pat_tag:
            if mstate.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')

            if m:
                return {**m, pat_tag: tgt, **self.static_tags}

            return {pat_tag: tgt, **self.static_tags}

        if m:
            return dict(m, **self.static_tags)

        return self.static_tags


class MQ(M_Pattern_One):
    """Quantifier pattern. Matches at least `min` and at most `max` instances of the given pattern. Since this pattern
    can match an arbitrary number of actual targets, if there is a tag for the matched patterns they are given as a list
    of `FSTMatch` objects instead of just one.

    This is the base class for `MQSTAR`, `MQPLUS`, `MQOPT`, `MQMIN`, `MQMAX` and `MQN` and can do everything they can
    with the appropriate values for `min` and `max`. Those classes are provided regardless for convenience and cleaner
    pattern structuring.

    Using the wildcard pattern `...` means match anything the given number of times and is analogous to the regex dot
    `.` pattern.

    Quantifiers can **ONLY** live as **DIRECT** children of a list field, so `MList(elts=[MQSTAR])` is valid while
    `MList(elts=[M(MQSTAR)])` is not.

    Unlike other patterns, all the quantifier patterns can take a sublist of patterns as a pattern which allows matching
    an arbitrary nunmber this complete sublist sequentially in the list field the quantifier pattern is matching.

    Quantifier pattern sublists can **ONLY** live as **DIRECT** child patterns of a quantifier, so `MQSTAR([...])` is
    valid while `MQSTAR(M([...]))` is not.

    This pattern is greedy by default but has a non-greedy version child class `MQ.NG`. This pattern can be used in
    exactly the same way but will match non-greedily.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern.
    - `min`: The minimum number of pattern matches needed for a successful match.
    - `max`: The maximum number of pattern matches taken for a successful match. `None` means unbounded.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> from fst.docs import ppmatch  # pretty-print FSTMatch

    >>> MList([MQ('a', 1, 2)]) .match(FST('[]'))

    >>> MList([MQ('a', 1, 2)]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3>>

    >>> MList([MQ('a', 1, 2)]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6>>

    >>> MList([MQ('a', 1, 2)]) .match(FST('[a, a, a]'))

    >>> MList([MQ('a', 1, 2), MQSTAR]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9>>

    >>> pat = MGlobal([MQSTAR.NG, MQ(t='c', min=1, max=2), MQSTAR])

    >>> ppmatch(FST('global a, b, c, c, d, e') .match(pat))
    <FSTMatch <Global ROOT 0,0..0,23>
      't': [
        <FSTMatch <<Global ROOT 0,0..0,23>.names[2:3]>>,
        <FSTMatch <<Global ROOT 0,0..0,23>.names[3:4]>>,
      ],
    }>

    >>> pat = MList([MQSTAR.NG, MQ(t=MRE('c|d'), min=1, max=3), MQSTAR])

    >>> ppmatch(m := FST('[a, b, c, c, d, c, e]') .match(pat))
    <FSTMatch <List ROOT 0,0..0,21>
      't': [
        <FSTMatch <Name 0,7..0,8>>,
        <FSTMatch <Name 0,10..0,11>>,
        <FSTMatch <Name 0,13..0,14>>,
      ],
    }>

    >>> [mm.matched.src for mm in m['t']]
    ['c', 'c', 'd']

    Sublist matching, will match the sequence "a, b" twice in the example below.

    >>> ppmatch(MList([MQ(t=['a', 'b'], min=1, max=2)]) .match(FST('[a, b, a, b]')))
    <FSTMatch <List ROOT 0,0..0,12>
      't': [
        <FSTMatch [<Name 0,1..0,2>, <Name 0,4..0,5>]>,
        <FSTMatch [<Name 0,7..0,8>, <Name 0,10..0,11>]>,
      ],
    }>
    """

    # This is mostly just a data class, the actual logic for these matches lives in `_match__inside_list_quantifier()`.
    # The tags for the individual child matches are handled according to if the pattern is passed anonymously or in a
    # tag. The static tags are added once at the end of a valid arbitrary-length match.

    pat = ...  # for direct subclass type use as a pattern
    pat_tag = None
    static_tags = _EMPTY_DICT
    greedy = True  ; """@private"""

    min: int  ; """@private"""
    max: int | None  ; """@private"""

    _requires = 'pattern or list of patterns'

    def __init__(
        self,
        anon_pat: _Patterns | _NotSet = NotSet,
        /,
        min: int | _NotSet = NotSet,
        max: int | None | _NotSet = NotSet,
        **tags,
    ) -> None:
        M_Pattern_One.__init__(self, anon_pat, **tags)

        if min is NotSet:
            if max is NotSet:
                raise ValueError(f'{self.__class__.__qualname__} requires min and max values')

            raise ValueError(f'{self.__class__.__qualname__} requires a min value')

        elif max is NotSet:
            raise ValueError(f'{self.__class__.__qualname__} requires a max value')

        if min < 0:
            raise ValueError(f'{self.__class__.__qualname__} min cannot be negative')

        if max is not None:
            if max < 0:
                raise ValueError(f'{self.__class__.__qualname__} max cannot be negative')
            if max < min:
                raise ValueError(f'{self.__class__.__qualname__} max cannot be lower than min')

        self.min = min
        self.max = max
        pat = self.pat

        if isinstance(pat, list):  # if quantifier is unbounded and has sublist then make sure that list must match at least one item (including any sublists in that, etc...), otherwise will get infinite loop
            if max is None:
                stack = pat[:]

                while stack:
                    p = stack.pop()

                    if p in _QUANTIFIER_STANDALONES_MAYBE_0_LEN:
                        continue

                    if isinstance(p, MQ):
                        if not p.min:
                            continue

                        if isinstance(p := p.pat, list):
                            stack.extend(p)
                        else:
                            break
                    else:
                        break
                else:
                    raise ValueError(f'unbounded {self.__class__.__qualname__} with sublist cannot have'
                                     ' possible zero-length matches')

        elif pat in _QUANTIFIER_STANDALONES or isinstance(pat, MQ):
            raise ValueError(f'{self.__class__.__qualname__} cannot have another quantifier as a direct child pattern')

    def _repr_extra(self) -> list[str]:
        return [f'min={self.min}, max={self.max}']

class NG(MQ):
    """Non-greedy version of `MQ` quantifier pattern."""

    __qualname__ = 'MQ.NG'
    greedy = False

MQ.NG = NG
del NG


class MQSTAR(MQ):
    """Star quantifier pattern, zero or more. Shortcut for `MQ(anon_pat, min=0, max=None, **tags)`. Has non-greedy
    version child class `MQSTAR.NG`.

    This class type itself as well as the the non-greedy version can be used directly as a shortcut for `MQSTAR(...)`
    or `MQSTAR.NG(...)`, the equivalents of regex `.*` and `.*?`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> from fst.docs import ppmatch  # pretty-print FSTMatch

    >>> MList([MQSTAR(t='a')]) .match(FST('[]'))
    <FSTMatch <List ROOT 0,0..0,2> {'t': []}>

    >>> MList([MQSTAR(t='a')]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> ppmatch(MList([MQSTAR(t='a')]) .match(FST('[a, a]')))
    <FSTMatch <List ROOT 0,0..0,6>
      {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> ppmatch(MList([MQSTAR(t='a')]) .match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      't': [
        <FSTMatch <Name 0,1..0,2>>,
        <FSTMatch <Name 0,4..0,5>>,
        <FSTMatch <Name 0,7..0,8>>,
      ],
    }>

    >>> ppmatch(MList([MQSTAR(t='a'), MQSTAR]) .match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      't': [
        <FSTMatch <Name 0,1..0,2>>,
        <FSTMatch <Name 0,4..0,5>>,
        <FSTMatch <Name 0,7..0,8>>,
      ],
    }>

    >>> MList([MQSTAR.NG(t='a'), MQSTAR]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9> {'t': []}>
    """

    min = 0  # for direct type use
    max = None

    def __init__(self, anon_pat: _Patterns | _NotSet = NotSet, /, **tags) -> None:
        MQ.__init__(self, anon_pat, 0, None, **tags)

    def _repr_extra(self) -> list[str]:
        return _EMPTY_LIST

class NG(MQSTAR):
    """Non-greedy version of `MQSTAR` quantifier pattern."""

    __qualname__ = 'MQSTAR.NG'
    greedy = False

MQSTAR.NG = NG
del NG


class MQPLUS(MQ):
    """Plus quantifier pattern, one or more. Shortcut for `MQ(anon_pat, min=1, max=None, **tags)`. Has non-greedy
    version child class `MQPLUS.NG`.

    This class type itself as well as the the non-greedy version can be used directly as a shortcut for `MQPLUS(...)`
    or `MQPLUS.NG(...)`, the equivalents of regex `.+` and `.+?`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> from fst.docs import ppmatch  # pretty-print FSTMatch

    >>> MList([MQPLUS(t='a')]) .match(FST('[]'))

    >>> MList([MQPLUS(t='a')]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> ppmatch(MList([MQPLUS(t='a')]) .match(FST('[a, a]')))
    <FSTMatch <List ROOT 0,0..0,6>
      {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> ppmatch(MList([MQPLUS(t='a')]) .match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      't': [
        <FSTMatch <Name 0,1..0,2>>,
        <FSTMatch <Name 0,4..0,5>>,
        <FSTMatch <Name 0,7..0,8>>,
      ],
    }>

    >>> ppmatch(MList([MQPLUS(t='a'), MQSTAR]) .match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      't': [
        <FSTMatch <Name 0,1..0,2>>,
        <FSTMatch <Name 0,4..0,5>>,
        <FSTMatch <Name 0,7..0,8>>,
      ],
    }>

    >>> MList([MQPLUS.NG(t='a'), MQSTAR]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9> {'t': [<FSTMatch <Name 0,1..0,2>>]}>
    """

    min = 1  # for direct type use
    max = None

    def __init__(self, anon_pat: _Patterns | _NotSet = NotSet, /, **tags) -> None:
        MQ.__init__(self, anon_pat, 1, None, **tags)

    def _repr_extra(self) -> list[str]:
        return _EMPTY_LIST

class NG(MQPLUS):
    """Non-greedy default version of `MQPLUS` quantifier pattern."""

    __qualname__ = 'MQPLUS.NG'
    greedy = False

MQPLUS.NG = NG
del NG


class MQOPT(MQ):
    """Zero or one (optional) quantifier pattern. Shortcut for `MQ(anon_pat, min=0, max=1, **tags)`. Has non-greedy
    version child class `MQOPT.NG`.

    This class type itself as well as the the non-greedy version can be used directly as a shortcut for `MQOPT(...)` or
    `MQOPT.NG(...)`, the equivalents of regex `.?` and `.??`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched node tags are returned as normal tags.
        If this is missing then there must be at least one element in `tags` and the first keyword there will be taken
        to be the pattern to match. In this case the keyword is used as a tag which is used to return either an empty
        list or a list with a single `FSTMatch` object for the node matched by the pattern.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> MList([MQOPT(t='a')]) .match(FST('[]'))
    <FSTMatch <List ROOT 0,0..0,2> {'t': []}>

    >>> MList([MQOPT(t='a')]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> MList([MQOPT(t='a')]) .match(FST('[b]'))

    >>> MList([MQOPT(t='a')]) .match(FST('[a, a]'))

    >>> MList([MQOPT(t='a'), MQSTAR]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> MList([MQOPT.NG(t='a'), MQSTAR]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': []}>

    >>> MList([MQOPT.NG(t='a'), 'b']) .match(FST('[a, b]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': [<FSTMatch <Name 0,1..0,2>>]}>
    """

    min = 0  # for direct type use
    max = 1

    def __init__(self, anon_pat: _Patterns | _NotSet = NotSet, /, **tags) -> None:
        MQ.__init__(self, anon_pat, 0, 1, **tags)

    def _repr_extra(self) -> list[str]:
        return _EMPTY_LIST

class NG(MQOPT):
    """Non-greedy version of `MQOPT` quantifier pattern."""

    __qualname__ = 'MQOPT.NG'
    greedy = False

MQOPT.NG = NG
del NG


class MQMIN(MQ):
    """Minimum count quantifier pattern. Shortcut for `MQ(anon_pat, min=min, max=None, **tags)`. Has non-greedy version
    child class `MQMIN.NG`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern.
    - `min`: The minimum number of pattern matches needed for a successful match.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> from fst.docs import ppmatch  # pretty-print FSTMatch

    >>> MList([MQMIN(t='a', min=2)]) .match(FST('[]'))

    >>> MList([MQMIN(t='a', min=2)]) .match(FST('[a]'))

    >>> ppmatch(MList([MQMIN(t='a', min=2)]) .match(FST('[a, a]')))
    <FSTMatch <List ROOT 0,0..0,6>
      {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> ppmatch(MList([MQMIN(t='a', min=2)]) .match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      't': [
        <FSTMatch <Name 0,1..0,2>>,
        <FSTMatch <Name 0,4..0,5>>,
        <FSTMatch <Name 0,7..0,8>>,
      ],
    }>

    >>> ppmatch(MList([MQMIN(t='a', min=2), MQSTAR]) .match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      't': [
        <FSTMatch <Name 0,1..0,2>>,
        <FSTMatch <Name 0,4..0,5>>,
        <FSTMatch <Name 0,7..0,8>>,
      ],
    }>

    >>> ppmatch(MList([MQMIN.NG(t='a', min=2), MQSTAR]) .match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>
    """

    def __init__(
        self, anon_pat: _Patterns | _NotSet = NotSet, /, min: int | _NotSet = NotSet, **tags
    ) -> None:
        MQ.__init__(self, anon_pat, min, None, **tags)

    def _repr_extra(self) -> list[str]:
        return [f'min={self.min}']

class NG(MQMIN):
    """Non-greedy version of `MQMIN` quantifier pattern."""

    __qualname__ = 'MQMIN.NG'
    greedy = False

MQMIN.NG = NG
del NG


class MQMAX(MQ):
    """Maximum count quantifier pattern. Shortcut for `MQ(anon_pat, min=0, max=max, **tags)`. Has non-greedy version
    child class `MQMAX.NG`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern.
    - `max`: The maximum number of pattern matches taken for a successful match. `None` means unbounded.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> from fst.docs import ppmatch  # pretty-print FSTMatch

    >>> MList([MQMAX(t='a', max=2)]) .match(FST('[]'))
    <FSTMatch <List ROOT 0,0..0,2> {'t': []}>

    >>> MList([MQMAX(t='a', max=2)]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> ppmatch(MList([MQMAX(t='a', max=2)]) .match(FST('[a, a]')))
    <FSTMatch <List ROOT 0,0..0,6>
      {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> MList([MQMAX(t='a', max=2)]) .match(FST('[a, a, a]'))

    >>> ppmatch(MList([MQMAX(t='a', max=2), MQSTAR]) .match(FST('[a, a, a]')))
    <FSTMatch <List ROOT 0,0..0,9>
      {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> MList([MQMAX.NG(t='a', max=2), MQSTAR]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9> {'t': []}>
    """

    min = 0

    def __init__(
        self, anon_pat: _Patterns | _NotSet = NotSet, /, max: int | None | _NotSet = NotSet, **tags
    ) -> None:
        MQ.__init__(self, anon_pat, 0, max, **tags)

    def _repr_extra(self) -> list[str]:
        return [f'max={self.max}']

class NG(MQMAX):
    """Non-greedy version of `MQMAX` quantifier pattern."""

    __qualname__ = 'MQMAX.NG'
    greedy = False

MQMAX.NG = NG
del NG


class MQN(MQ):
    """Exact count quantifier pattern. Shortcut for `MQ(anon_pat, min=n, max=n, **tags)`. Does **NOT** have a non-greedy
    version child class `MQN.NG` as that would not make any sense. Instead has itself as an attribute `NG` so can still
    be used as `MQN.NG`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern.
    - `n`: The exact number of pattern matches taken for a successful match.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> MList([MQN(t='a', n=1)]) .match(FST('[]'))

    >>> MList([MQN(t='a', n=1)]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> MList([MQN(t='a', n=1)]) .match(FST('[a, a]'))

    >>> MList([MQN(t='a', n=1), MQSTAR]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>
    """

    def __init__(
        self, anon_pat: _Patterns | _NotSet = NotSet, /, n: int | _NotSet = NotSet, **tags
    ) -> None:
        if n is NotSet:
            raise ValueError(f'{self.__class__.__qualname__} requires a count value')
        if n is None or n < 0:
            raise ValueError(f'{self.__class__.__qualname__} count must be a non-negative integer')

        MQ.__init__(self, anon_pat, n, n, **tags)

    def _repr_extra(self) -> list[str]:
        return [f'n={self.min}']

MQN.NG = MQN


# ----------------------------------------------------------------------------------------------------------------------

_QUANTIFIER_STANDALONES = {MQSTAR, MQSTAR.NG, MQPLUS, MQPLUS.NG, MQOPT, MQOPT.NG}  # these classes types themselves (as opposed to instances) can be used in list fields
_QUANTIFIER_STANDALONES_MAYBE_0_LEN = {MQSTAR, MQSTAR.NG, MQOPT, MQOPT.NG}  # these can result in a zero-length match

_NODE_ARGUMENTS_ARGS_LIST_ONLY_FIELDS = {'kwonlyargs', 'posonlyargs'}
_NODE_ARGUMENTS_ARGS_LIST_FIELDS = {'kwonlyargs', 'posonlyargs', 'args'}
_NODE_ARGUMENTS_ARGS_ALL_FIELDS = {'kwonlyargs', 'posonlyargs', 'args', 'vararg', 'kwarg'}
_NODE_ARGUMENTS_DEFAULTS_FIELDS = {'defaults', 'kw_defaults'}

_FSTVIEW_NON_DEREF_FST_SINGLE_TYPE = {
    FSTView_Dict:            Dict,
    FSTView_MatchMapping:    MatchMapping,
    FSTView_arguments:       arguments,
    FSTView_Global_Nonlocal: Name,
}


class _MatchState:
    """Store running tags being built up during matching, which may be queried by `MTAG`. `tagss` is the plural of
    `tags` and indicates a list of dictionaries of tags. Merged on exit from each node that builds them up as a list
    like this."""

    is_FST: bool
    ctx: bool
    all_tagss: list[list[dict[str, Any]]]

    cache: dict
    """Stores:
    - `{FSTView: _Patterns}`: For temporary conversions of `FSTView`s to `AST` patterns. Used for matching previously
        matched `FSTView`s and for `MTAG` match previously matched multinode item from `Dict`, `MatchMapping` or
        `arguments`.
    - `(pat_arg, pat_dflt, arg_fields, dflt_fields) | False`: For validated single-argument match parameters for
        matching a single `arguments` arg against `FSTView` single argument.
    """

    def __init__(self, is_FST: bool, ctx: bool) -> None:
        self.is_FST = is_FST
        self.ctx = ctx
        self.all_tagss = []
        self.cache = {}

    def clear(self) -> None:
        """Clean up anything from a previous match attempt."""

        self.all_tagss.clear()
        self.cache.clear()

    def new_tagss(self) -> list:
        """Add new list of tags dictionaries to add to, which may be discarded in its entirety quickly if match fails
        that part, or merged and readded to the previous running list."""

        self.all_tagss.append(tagss := [])

        return tagss

    def discard_tagss(self) -> None:
        """Discard top level list of tags."""

        del self.all_tagss[-1]

        return None

    def pop_merge_tagss(self) -> dict[str, Any]:
        """Pop top level list of tags and merge into a single dictionary and return. No guarantee will be pushed back
        to running list of lists."""

        tagss = self.all_tagss.pop()

        if not tagss:
            return _EMPTY_DICT
        if len(tagss) == 1:
            return tagss[0]

        tags = {}

        for ts in tagss:
            tags.update(ts)

        return tags

    def get_tag(self, tag: str, default: object = NotSet, /) -> object:
        """Walk running list of dictionaries backwards checking for `tag`."""

        for tagss in reversed(self.all_tagss):
            if tagss:
                for m in reversed(tagss):
                    if (v := m.get(tag, _SENTINEL)) is not _SENTINEL:
                        return v

        return default


class _MatchList:
    seq: Sequence  # to be accessed directly
    len: int
    idx: int  # next item to return

    def __init__(self, seq: Sequence) -> None:
        self.seq = seq
        self.len = len(seq)
        self.idx = 0

    def next(self) -> object:
        if (idx := self.idx) == self.len:
            return _SENTINEL

        ret = self.seq[idx]
        self.idx = idx + 1

        return ret

    def at_end(self) -> bool:
        return self.idx == self.len


def _match__inside_list_quantifier(
    mstate: _MatchState, pat_iter: _MatchList, tgt_iter: _MatchList, pat: MQ, allow_partial: bool
) -> dict[str, Any] | None:
    """Match quantifier in list."""

    def match_next_q_pat() -> bool:
        """Attempt to match next element in list with the quantifier pattern and if success then add it to matches.
        Adding to matches means either adding the successful match dictionary to `tagss` or creating an `FSTMatch`
        object and adding it to a dedicated match list which is in `tagss` as its own dictionary with key `pat_tag`."""

        if is_qpat_list:
            qpat_iter.idx = 0  # reset quantifier list pattern to start since _match__inside_list() doesn't reset it on success
            tgt_idx = tgt_iter.idx

            if (m := _match__inside_list(mstate, qpat_iter, tgt_iter, True)) is None:
                return False

            t = tgt_seq[tgt_idx : tgt_iter.idx]

            if pat_tag:
                if is_FST:
                    for i, tt in enumerate(t):
                        if tt and not (tt := getattr(tt, 'f', None)):
                            raise MatchError('match found an AST node without an FST')  # pragma: no cover  # cannot currently happen due to how lists are handled and checked before getting here

                        t[i] = tt

                m = FSTMatch(q_pat, t, m)

        else:
            if (t := tgt_iter.next()) is _SENTINEL:  # end of list?
                return False

            if (m := match_func(q_pat, t, mstate)) is None:  # no match?
                tgt_iter.idx -= 1  # "put back" the target we got above because it didn't match

                return False

            if pat_tag:
                if is_FST and t and not (t := getattr(t, 'f', None)):
                    raise MatchError('match found an AST node without an FST')  # pragma: no cover

                m = FSTMatch(q_pat, t, m)

        matches.insert(matches_ins_idx, m)

        return True

    # setup

    tagss = mstate.new_tagss()

    tgt_idx_saved = tgt_iter.idx
    tgt_seq = tgt_iter.seq
    is_FST = bool(mstate.is_FST and tgt_seq and not isinstance(tgt_seq[0], (str, FSTView)))  # target lists can only contain ASTs, strings or FSTViews, we only need to check one element because all will be same
    q_pat = pat.pat
    q_min = pat.min
    q_max = pat.max
    matches_ins_idx = 0x7fffffffffffffff
    count = 0

    if q_max is None:
        q_max = 0x7fffffffffffffff

    if is_qpat_list := isinstance(q_pat, list):  # quantifiers can match a partial list
        qpat_iter = _MatchList(q_pat)
    else:
        match_func = _MATCH_FUNCS.get(q_pat.__class__, _match_default)

    if pat_tag := pat.pat_tag:
        matches = []
        tagss.append({pat_tag: matches})
    else:
        matches = tagss

    if greedy := pat.greedy:
        counts = (q_min, q_max)
        last_try_count = q_min
    else:
        counts = (q_min,)
        last_try_count = q_max

    # match quantifier pattern up to minimum or maximum allowed number of times to list according to greedy

    for count_to in counts:
        while count < count_to:
            if not match_next_q_pat():
                break

            count += 1

        else:
            if static_tags := pat.static_tags:
                tagss.append(static_tags)

                if not pat_tag:  # if no pat_tag then inserting matches directly into tagss and need to insert them before the static_tags dict
                    matches_ins_idx = -1

            continue

        if count < q_min:  # failed to meet minimum count?
            tgt_iter.idx = tgt_idx_saved  # rewind target iterator

            return mstate.discard_tagss()

        break

    # now we start trying to match rest of list and either add new quantifier matches one by one or discard them and retry depending on greedy

    if greedy:  # if greedy then we matched up to maximum and we will be discarding matches, either from tagss or the matches list under pat_tag
        matches_del_idx = -1 if pat_tag or not static_tags else -2

    while True:  # as long as we don't hit the last allowed count try to match rest of list
        m = _match__inside_list(mstate, pat_iter, tgt_iter, allow_partial)  # the allow_partial is a passthrough from a possible quantifier subsequence caller

        if m is not None:  # successful match to rest of list?
            break

        if count == last_try_count:  # if we are at end with no match then we failed
            tgt_iter.idx = tgt_idx_saved

            return mstate.discard_tagss()

        if greedy:  # if greedy then we are removing previous matches to try again one position to the left
            del matches[matches_del_idx]  # if there are static_tags then we are deleting the dictionary before those

            tgt_iter.idx -= 1  # step back 1
            count -= 1

        else:  # if non-greedy then we are attempting to match our pattern one position to the right and if successful then try match shorter list
            if not match_next_q_pat():
                tgt_iter.idx = tgt_idx_saved

                return mstate.discard_tagss()

            count += 1

    # successful match everything, merge tags

    tagss.append(m)

    return mstate.pop_merge_tagss()


def _match__inside_list(
    mstate: _MatchState, pat_iter: _MatchList, tgt_iter: _MatchList, allow_partial: bool = False
) -> dict[str, Any] | None:
    """Match list. The sequence to match in `tgt_iter` can be either `list[AST]` or `FSTView`. If match fails then
    "rewinds" the iterators to their locations on entry.

    **Parameters:**
    - `allow_partial`: Whether to allow unfinished target list at end of pattern list or not.
        - `False`: This is the normal mode of operation used for matching an entire list field.
        - `True`: This allows matching partial lists inside quantifiers.
    """

    tagss = mstate.new_tagss()

    tgt_idx_saved = tgt_iter.idx
    pat_idx_saved = pat_iter.idx

    while (p := pat_iter.next()) is not _SENTINEL:
        if p in _QUANTIFIER_STANDALONES or isinstance(p, MQ):  # quantifier
            m = _match__inside_list_quantifier(mstate, pat_iter, tgt_iter, p, allow_partial)

            if m is None:
                break  # fail
            if m:
                tagss.append(m)

            return mstate.pop_merge_tagss()  # _match__inside_list_quantifier does the rest of the list and returns a merged dict with its own tags, so we just merge into what we have

        # concrete value

        if (t := tgt_iter.next()) is _SENTINEL:  # if nothing left in target list then fail since we have a concrete pattern left to match
            break  # fail

        m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, mstate)

        if m is None:
            break  # fail
        if m:
            tagss.append(m)

    else:
        if allow_partial or tgt_iter.at_end():  # pattern sequence ended so target sequence must also be at end in order to be a success, unless we explicitly allow partial match
            return mstate.pop_merge_tagss()

    pat_iter.idx = pat_idx_saved  # rewind iterators
    tgt_iter.idx = tgt_idx_saved

    return mstate.discard_tagss()


def _match__FSTView_w__all(
    pat: MAST | AST, tgt: FSTView, mstate: _MatchState, start: int = -1, stop: int = -1
) -> Mapping[str, Any] | None:
    """Match an `AST` or `MAST` pattern against an `FSTView` which may be a fragment and is accessed by the `_all`
    virtual field."""

    if start == -1:
        start, stop = tgt.start_and_stop

    base = tgt.base
    ast = base.a

    tagss = mstate.new_tagss()

    for field in pat._fields:
        if (p := getattr(pat, field, ...)) is ...:
            continue

        if (t := getattr(ast, field, _SENTINEL)) is _SENTINEL:  # _SENTINEL means _all field because target AST nodes will have all other fields which may be present in the pattern
            t = base._all[start : stop]

        elif isinstance(t, list):
            if not isinstance(p, list):
                t = getattr(base, field)  # get the FSTView instead (for maybe capture to tag, is converted back to list of AST for compare, because was gotten as list from AST even if we are matching an FST)

            t = t[start : stop]

        if (m := _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, mstate)) is None:
            return mstate.discard_tagss()
        if m:
            tagss.append(m)

    return mstate.pop_merge_tagss()


# ......................................................................................................................

def _match_default(pat: _Patterns, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Catch and dispatch anything that is not explicitly listed in jump table by class. Mostly user-subclassed
    stuff."""

    if isinstance(pat, list):  # subclass of list
        return _match_list(pat, tgt, mstate)

    if isinstance(pat, str):  # subclass of str
        return _match_str(pat, tgt, mstate)

    if isinstance(pat, FSTView):
        raise RuntimeError(f'should not get here, FSTView type not coded {pat.__class__.__qualname__}')  # pragma: no cover

    if isinstance(pat, M_Pattern):  # user tried to subclass a pattern
        raise RuntimeError('subclassing M_Pattern not supported')

    return _match_primitive(pat, tgt, mstate)  # subclass of primitive

def _match_FSTView(pat: FSTView, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Temporary concrete pattern for matching against the given `FSTView`. Created once and cached, then pass control
    to appropriate node matcher.

    We just create a list of `AST` nodes from the `FSTView.field` of the `FSTView.base` node offset by the possible
    presence of a docstring.
    """

    if not (real_pat := mstate.cache.get(pat)):
        start, stop = pat.start_and_stop
        real_pat = mstate.cache[pat] = getattr(pat.base.a, pat.field)[start : stop]

    return _match_list(real_pat, tgt, mstate)

def _match_FSTView__body(pat: FSTView__body, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Temporary concrete pattern for matching against the given `FSTView`. Created once and cached, then pass control
    to appropriate node matcher.

    We just create a list of `AST` nodes from the `body` field of the `FSTView__body.base` node offset by the possible
    presence of a docstring.
    """

    if not (real_pat := mstate.cache.get(pat)):
        start, stop = pat.start_and_stop
        base = pat.base
        has_docstr = base.has_docstr
        real_pat = mstate.cache[pat] = base.a.body[start + has_docstr : stop + has_docstr]

    return _match_list(real_pat, tgt, mstate)

def _match_FSTView_arglikes(pat: FSTView_arglikes, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Temporary concrete pattern for matching against the given `FSTView_arglikes`. Created once and cached, then pass
    control to appropriate node matcher.

    We just create a list of `AST` nodes from the `args` or `bases` and `keywords` fields of the `FSTView_arglikes.base`
    node ordered syntactically according to their location in the source.
    """

    if not (real_pat := mstate.cache.get(pat)):
        start, stop = pat.start_and_stop
        real_pat = mstate.cache[pat] = pat.base._cached_arglikes()[start : stop]

    return _match_list(real_pat, tgt, mstate)

def _match_FSTView_Compare(pat: FSTView_Compare, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Temporary concrete pattern for matching against the given `FSTView`. Created once and cached, then pass control
    to appropriate node matcher."""

    if not (real_pat := mstate.cache.get(pat)):
        start, stop = pat.start_and_stop

        if stop == start:  # zero length Compare slice, shouldn't really be encountered in normal usage
            real_pat = MCompare(NotSet, [], [])  # NotSet doesn't hold any special value, just means empty and doesn't match anything

        else:
            ast = pat.base.a
            comparators = ast.comparators
            left = comparators[start - 1] if start else ast.left
            stop -= 1
            real_pat = MCompare(left, ast.ops[start : stop], comparators[start : stop])

        mstate.cache[pat] = real_pat

    return _match_node_Compare(real_pat, tgt, mstate)

def _match_FSTView_Dict(pat: FSTView_Dict, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Temporary concrete pattern for matching against the given `FSTView`. Created once and cached, then pass control
    to appropriate node matcher."""

    if not (real_pat := mstate.cache.get(pat)):
        start, stop = pat.start_and_stop
        ast = pat.base.a
        real_pat = mstate.cache[pat] = MDict(ast.keys[start : stop], ast.values[start: stop])

    return _match_node_Dict(real_pat, tgt, mstate)

def _match_FSTView_MatchMapping(
    pat: FSTView_MatchMapping, tgt: _Targets, mstate: _MatchState
) -> Mapping[str, Any] | None:
    """Temporary concrete pattern for matching against the given `FSTView`. Created once and cached, then pass control
    to appropriate node matcher."""

    if not (real_pat := mstate.cache.get(pat)):
        start, stop = pat.start_and_stop
        ast = pat.base.a

        if pat.has_rest:
            stop -= 1
            real_pat = MMatchMapping(ast.keys[start : stop], ast.patterns[start : stop], ast.rest)
        else:
            real_pat = MMatchMapping(ast.keys[start : stop], ast.patterns[start : stop])

        mstate.cache[pat] = real_pat

    return _match_node_MatchMapping(real_pat, tgt, mstate)

def _match_FSTView_arguments(pat: FSTView_arguments, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Temporary concrete pattern for matching against the given `FSTView`. Created once and cached, then pass control
    to appropriate node matcher."""

    if not (real_pat := mstate.cache.get(pat)):
        allargs = pat.base._cached_allargs()
        pat_args = {
            'posonlyargs': [],
            'args': [],
            'vararg': [],
            'kwonlyargs': [],
            'kw_defaults': [],
            'kwarg': [],
            'defaults': [],
        }

        for v in pat:
            a = allargs[v.start]
            f = a.f
            field = f.pfield.name

            pat_args[field].append(a)

            if (d := f.next()) and (d_field := d.pfield.name) in _NODE_ARGUMENTS_DEFAULTS_FIELDS:
                pat_args[d_field].append(d.a)
            elif field == 'kwonlyargs':
                pat_args['kw_defaults'].append(None)

        real_pat = mstate.cache[pat] = Marguments(
            posonlyargs=pat_args['posonlyargs'] or ...,
            args=pat_args['args'] or ...,
            vararg=a[0] if (a := pat_args['vararg']) else ...,
            kwonlyargs=pat_args['kwonlyargs'] or ...,
            kw_defaults=pat_args['kw_defaults'],
            kwarg=a[0] if (a := pat_args['kwarg']) else ...,
            defaults=pat_args['defaults'],
            _strict=None,  # so that any arg matches any other when matching single args (rational is that this was matched in 1v1, only takes effect for single arg vs. single arg matches)
        )

    return _match_node_arguments(real_pat, tgt, mstate)

def _match_FSTView_dummy(pat: FSTView_dummy, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Temporary concrete pattern for matching against the given `FSTView_dummy`. Created once and cached, then pass
    control to appropriate node matcher.

    An `FSTView_dummy.field` implies always empty so just use an empty list.
    """

    return _match_list([], tgt, mstate)

def _match_list(pat: type, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Match a list pattern to a target list or `FSTView`."""

    if not isinstance(tgt, list):
        if not isinstance(tgt, FSTView):
            return None

        if not len(tgt):
            tgt = _EMPTY_LIST
        elif not tgt.is_deref_FST or isinstance(tgt[0], str):  # could be Global/Nonlocal.names or MatchClass.kwd_attrs or multi-node items like Dict/MatchMapping/arguments
            tgt = list(tgt)
        else:
            tgt = [f.a if f else f for f in tgt]  # convert to temporary list of AST nodes

    if not tgt and not pat:  # early out, can't do more because quantifiers could still resolve to empty lists
        return _EMPTY_DICT

    return _match__inside_list(mstate, _MatchList(pat), _MatchList(tgt))

def _match_node(pat: M_Pattern | AST, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """`M_Pattern` or `AST` leaf node."""

    is_mpat = isinstance(pat, M_Pattern)
    types = pat._types if is_mpat else pat.__class__

    if not isinstance(tgt, types):
        return None

    is_FST = mstate.is_FST

    tagss = mstate.new_tagss()

    for field in pat._fields:
        if (p := getattr(pat, field, ...)) is ...:  # ellipsis handled here without dispatching for various reasons
            continue

        if (t := getattr(tgt, field, _SENTINEL)) is _SENTINEL:  # _SENTINEL for arbitrary fields, but also field may not exist in target because pattern may have fields from a greater python version than we are running
            if (not (f := getattr(tgt, 'f', None))
                or not isinstance(t := getattr(f, field, None), FSTView)
            ):  # maybe its a virtual field
                return mstate.discard_tagss()

        elif (is_FST
              and isinstance(t, list)
              and (not isinstance(p, list) or tgt.__class__ in ASTS_LEAF_VAR_SCOPE_DECL)  # ASTS_LEAF_VAR_SCOPE_DECL to make sure we match Global/Nonlocal.names as FSTView instead of list of strings
        ):
            t = getattr(tgt.f, field)  # get the FSTView instead (for maybe capture to tag, is converted back to list of AST for compare, because was gotten as list from AST even if we are matching an FST)

        if (m := _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, mstate)) is None:
            return mstate.discard_tagss()
        if m:
            tagss.append(m)

    return mstate.pop_merge_tagss()

def _match_node_Compare(pat: MCompare | Compare, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """`Compare` or `MCompare` leaf node. Possibly match against an `FSTView_Compare`."""

    if not isinstance(tgt, FSTView_Compare):
        return _match_node(pat, tgt, mstate)

    if getattr(pat, '_all', ...) is not ...:
        raise MatchError('matching a Compare pattern against Compare._all the pattern cannot have its own _all field')

    start, stop = tgt.start_and_stop
    tgt_len = stop - start
    left = getattr(pat, 'left', ...)

    if left is NotSet:  # this means came from empty FSTView and ops and comparators are empty as well
        return _EMPTY_DICT if not tgt_len else None  # empty Compare matches empty FSTView_Compare, else no match

    if not tgt_len:  # we have at least one element but target is empty?
        return None

    return _match__FSTView_w__all(pat, tgt, mstate, start, stop)

def _match_node_Dict(pat: MDict | Dict, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """`Dict` or `MDict` leaf node. Possibly match against a single-item `FSTView_Dict`."""

    if not isinstance(tgt, FSTView_Dict):
        return _match_node(pat, tgt, mstate)

    return _match__FSTView_w__all(pat, tgt, mstate)

def _match_node_MatchMapping(
    pat: MatchMapping | MMatchMapping, tgt: _Targets, mstate: _MatchState
) -> Mapping[str, Any] | None:
    """`MatchMapping` or `MMatchMapping` leaf node. Possibly match against a single-item `FSTView_MatchMapping`."""

    if not isinstance(tgt, FSTView_MatchMapping):
        return _match_node(pat, tgt, mstate)

    return _match__FSTView_w__all(pat, tgt, mstate)

def _match_node_arguments(pat: Marguments | arguments, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """`arguments` or `Marguments` leaf node. Possibly match against a single-item `FSTView_arguments`. Will match a
    single argument with possibly a default to a single-argument `FSTView_arguments`. Pattern `args` argument matches
    to target `args`, `posonlyargs` or `kwonlyargs`. Other type pattern args must match exactly (`posonlyargs` only to
    `posonlyargs`, `kwonlyargs` to `kwonlyargs`, `varag` to `vararg` and `kwarg` to `kwarg` (obviously), etc...).
    Standalone `defaults` matches to `defaults` or `kw_defaults` while standalone `kw_defaults` only matches to
    `kw_defaults`.

    If the conditions for matching a single argument vs. a single argument don't exist then do normal match.
    """

    if not isinstance(tgt, FSTView_arguments):
        return _match_node(pat, tgt, mstate)

    if len(tgt) != 1 or (cached := mstate.cache.get(pat)) is False:
        return _match__FSTView_w__all(pat, tgt, mstate)

    if cached:
        pat_arg, pat_dflt, arg_fields, dflt_fields = cached

    else:  # first time using this pattern, preprocess and cache
        try:  # easiest way to fail-exit preprocessing is just to raise and catch it
            strict = getattr(pat, '_strict', False)  # this controls allowing matching between the different kinds of args (pos, normal and kw)

            if strict:
                raise MatchError('matching an arguments pattern against arguments._all'
                                 'strict=True fall back to normal match')

            if getattr(pat, '_all', ...) is not ...:
                raise MatchError('matching an arguments pattern against arguments._all'
                                 ' the pattern cannot have its own _all field')

            # argument pattern (if any)

            nargs = 0
            pat_arg = ...
            arg_fields = _NODE_ARGUMENTS_ARGS_LIST_FIELDS

            if (posonlyargs := getattr(pat, 'posonlyargs', ...)) is ...:
                posonlyargs = ()
            elif not isinstance(posonlyargs, list):
                raise MatchError('matching an arguments pattern against arguments._all'
                                 ' the pattern posonlyargs must be ... or a length-1 list')
            elif posonlyargs:
                if strict is not None:
                    arg_fields = ('posonlyargs',)

                pat_arg = posonlyargs[0]
                nargs += len(posonlyargs)

            if (args := getattr(pat, 'args', ...)) is ...:
                args = ()
            elif not isinstance(args, list):
                raise MatchError('matching an arguments pattern against arguments._all'
                                 ' the pattern args must be ... or a length-1 list')
            elif args:
                # if strict:  # strict=True doesn't get here anymore, leaving for now just in case
                #     arg_fields = ('args',)

                pat_arg = args[0]
                nargs += len(args)

            if (kwonlyargs := getattr(pat, 'kwonlyargs', ...)) is ...:
                kwonlyargs = ()
            elif not isinstance(kwonlyargs, list):
                raise MatchError('matching an arguments pattern against arguments._all'
                                 ' the pattern kwonlyargs must be ... or a length-1 list')
            elif kwonlyargs:
                if strict is not None:
                    arg_fields = ('kwonlyargs',)

                pat_arg = kwonlyargs[0]
                nargs += len(kwonlyargs)

            if (vararg := getattr(pat, 'vararg', None)) is ...:
                vararg = None

            elif vararg is not None:
                arg_fields = ('vararg',)
                pat_arg = vararg
                nargs += 1

            if (kwarg := getattr(pat, 'kwarg', None)) is ...:
                kwarg = None

            elif kwarg is not None:
                arg_fields = ('kwarg',)
                pat_arg = kwarg
                nargs += 1

            if nargs > 1:
                raise MatchError('matching an arguments pattern against arguments._all'
                                 ' the pattern cannot have more than one arg')

            if nargs and pat_arg in _QUANTIFIER_STANDALONES or isinstance(pat_arg, MQ):  # quantifier
                raise MatchError('matching an arguments pattern against arguments._all'
                                 ' the pattern arg cannot contain quantifiers')

            # default pattern (if any)

            ndflts = 0
            pat_dflt = ...
            dflt_fields = _NODE_ARGUMENTS_DEFAULTS_FIELDS  # args field matches all args lists so default matches all defaults, if posonlyargs present then the 'kw_defaults' doesn't matter because will exit due to kwonlyargs before that

            if (defaults := getattr(pat, 'defaults', ...)) is not ...:
                if not isinstance(defaults, list):
                    raise MatchError('matching an arguments pattern against arguments._all'
                                     ' the pattern defaults must be ... or a length-1 list')
                if defaults:
                    if kwonlyargs or vararg or kwarg:
                        raise MatchError('matching an arguments pattern against arguments._all found invalid defaults')

                    # if strict:  # strict=True doesn't get here anymore, leaving for now just in case
                    #     dflt_fields = ('defaults',)

                    pat_dflt = defaults[0]
                    ndflts += len(defaults)

                elif args or posonlyargs:
                    pat_dflt = _SENTINEL  # this means that there must not be a default, instead of any default

            if (kw_defaults := getattr(pat, 'kw_defaults', ...)) is not ...:
                if not isinstance(kw_defaults, list):
                    raise MatchError('matching an arguments pattern against arguments._all'
                                     ' the pattern kw_defaults must be ... or a length-1 list')
                if kw_defaults:
                    if ndflts or args or posonlyargs or vararg or kwarg:
                        raise MatchError('matching an arguments pattern against arguments._all found invalid defaults')

                    if strict is not None:
                        dflt_fields = ('kw_defaults',)

                    pat_dflt = kw_defaults[0]

                    if pat_dflt is None:
                        pat_dflt = _SENTINEL
                    else:
                        ndflts += len(kw_defaults)

                elif kwonlyargs:
                    pat_dflt = _SENTINEL

            if ndflts > 1:
                raise MatchError('matching an arguments pattern against arguments._all'
                                 ' the pattern can only have a single default')

            if ndflts and pat_dflt in _QUANTIFIER_STANDALONES or isinstance(pat_dflt, MQ):  # quantifier
                raise MatchError('matching an arguments pattern against arguments._all'
                                 ' the pattern default cannot contain quantifiers')

            mstate.cache[pat] = pat_arg, pat_dflt, arg_fields, dflt_fields

        except MatchError:
            mstate.cache[pat] = False  # mark for always normal compare

            return _match__FSTView_w__all(pat, tgt, mstate)

    # we know we are matching a target 1 arg and we have at most a single argument and at most a single keyword and if there are both then they are the correct matching kinds

    base = tgt.base
    idx = tgt.start
    tgt_arg = base._cached_allargs()[idx]
    tgt_argf = tgt_arg.f
    tgt_field = tgt_argf.pfield.name
    ma = _EMPTY_DICT

    if pat_arg is not ...:
        if tgt_field not in arg_fields:
            return None

        ma = _MATCH_FUNCS.get(pat_arg.__class__, _match_default)(pat_arg, tgt_arg, mstate)

        if ma is None:
            return None

    if pat_dflt is ...:
        return ma

    tgt_dfltf = tgt_argf.next()

    if not tgt_dfltf or tgt_dfltf.pfield.name not in dflt_fields:  # this means there is no default, we assume that the target is valid so that defaults and non-defaults MUST alternate so if there is a next default it is ours
        if pat_dflt is _SENTINEL:  # if the pattern says no default instead of any default then it is a successful match
            return ma

        return None

    md = _MATCH_FUNCS.get(pat_dflt.__class__, _match_default)(pat_dflt, tgt_dfltf.a, mstate)

    if md is None:
        return None

    if not md:
        return ma
    if not ma:
        return md

    return {**ma, **md}

def _match_node_Constant(pat: MConstant | Constant, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """We do a special handler for `Constant` so we can check for a real `Ellipsis` instead of having that work as a
    wildcarcd. We do a standalone handler so don't have to have the check in general."""

    if not isinstance(tgt, Constant):
        return None

    if (p := getattr(pat, 'value', _SENTINEL)) is not _SENTINEL:  # missing value acts as implicit ... wildcard, while the real ... is a concrete value here
        match_func = _match_primitive if p is ... else _MATCH_FUNCS.get(p.__class__, _match_default)

        if (mv := match_func(p, tgt.value, mstate)) is None:
            return None
    else:
        mv = None

    if (p := getattr(pat, 'kind', ...)) is not ...:
        if (mk := _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt.kind, mstate)) is None:
            return None
    else:
        return mv

    if not mv:
        return mk

    return {**mv, **mk}

def _match_node_expr_context(pat: Load | Store | Del, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """This exists as a convenience so that an `AST` pattern `Load`, `Store` and `Del` always match each other unless
    the match option `ctx=True`. `MLoad`, `MStore` and `MDel` don't get here, they always do a match check. A pattern
    `None` must also match one of these successfully for py < 3.13."""

    if not isinstance(tgt, expr_context) or (mstate.ctx and tgt.__class__ is not pat.__class__):
        return None

    return _EMPTY_DICT

def _match_type(pat: type, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Just match the `AST` type (or equivalent `MAST` type). Special consideration is taken when matching against a
    multinode `FSTView`."""

    if issubclass(pat, M_Pattern):
        if issubclass(pat, MQ):
            raise MatchError(f'{pat.__qualname__} quantifier pattern in invalid location')

        pat = pat._types

    if t := _FSTVIEW_NON_DEREF_FST_SINGLE_TYPE.get(tgt.__class__):  # don't need to bother checking length 1
        if not issubclass(t, pat):
            return None

    elif not isinstance(tgt, pat):
        return None

    return _EMPTY_DICT

def _match_re_Pattern(
    pat: re_Pattern, tgt: _Targets, mstate: _MatchState, re_func: Callable | None = None
) -> Mapping[str, Any] | None:
    """Regex pattern against direct `str` or `bytes` value or source if `tgt` is an actual node. Will use `FST` source
    from the tree and unparse a non-`FST` `AST` node for the check.

    **Parameters:**
    - `re_func`: `None` for normal direct `re.Pattern` operation or bound `re.Pattern.match` or `re.Pattern.search` if
        calling from `MRE` for the appropriate match or search behavior and return of `re.Match` object.
    """

    _re_func = re_func if re_func else pat.match

    if isinstance(tgt, str):
        if not isinstance(pat.pattern, str) or not (m := _re_func(tgt)):
            return None

    elif isinstance(tgt, AST):
        if not isinstance(pat.pattern, str):
            return None

        if not (f := getattr(tgt, 'f', None)) or not (loc := f.loc):
            src = unparse(tgt)
        else:
            src = f._get_src(*loc)  # because at root this is whole source which may include leading and trailing trivia that is not part of the node itself

        if not (m := _re_func(src)):  # match source against pattern
            return None

    elif isinstance(tgt, FSTView):
        if not isinstance(pat.pattern, str):
            return None

        if not (m := _re_func(tgt.src)):  # match source against pattern
            return None

    elif isinstance(tgt, bytes):
        if not isinstance(pat.pattern, bytes) or not (m := _re_func(tgt)):
            return None

    else:
        return None

    return m if re_func else _EMPTY_DICT

def _match_str(pat: str, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    if isinstance(tgt, str):
        if tgt != pat:
            return None

    elif isinstance(tgt, AST):
        if not (f := getattr(tgt, 'f', None)) or not (loc := f.loc):
            src = unparse(tgt)
        else:
            src = f._get_src(*loc)  # because at root this is whole source which may include leading and trailing trivia that is not part of the node itself

        if src != pat:  # match source against exact string
            return None

    elif isinstance(tgt, FSTView):
        if tgt.src != pat:
            return None

    else:
        return None

    return _EMPTY_DICT

def _match_primitive(pat: constant, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
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
        return None

    return _EMPTY_DICT

def _match_None(pat: NoneType, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    if tgt is not None:
        return None

    return _EMPTY_DICT

def _match_Ellipsis(pat: EllipsisType, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Always succeeds."""

    return _EMPTY_DICT

def _match_quantifier_invalid_location(pat: MQ, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    raise MatchError(f'{pat.__class__.__qualname__} quantifier pattern in invalid location')

_MATCH_FUNCS = {
    M:                        M._match,
    MNOT:                     MNOT._match,
    MOR:                      MOR._match,
    MAND:                     MAND._match,
    MMAYBE:                   MMAYBE._match,
    MTYPES:                   MTYPES._match,  # _match_node_arbitrary_fields,
    MRE:                      MRE._match,
    MCB:                      MCB._match,
    MTAG:                     MTAG._match,
    MQ:                       _match_quantifier_invalid_location,
    MQ.NG:                    _match_quantifier_invalid_location,
    MQSTAR:                   _match_quantifier_invalid_location,
    MQSTAR.NG:                _match_quantifier_invalid_location,
    MQPLUS:                   _match_quantifier_invalid_location,
    MQPLUS.NG:                _match_quantifier_invalid_location,
    MQOPT:                    _match_quantifier_invalid_location,
    MQOPT.NG:                 _match_quantifier_invalid_location,
    MQMIN:                    _match_quantifier_invalid_location,
    MQMIN.NG:                 _match_quantifier_invalid_location,
    MQMAX:                    _match_quantifier_invalid_location,
    MQMAX.NG:                 _match_quantifier_invalid_location,
    MQN:                      _match_quantifier_invalid_location,
    FSTView:                  _match_FSTView,
    FSTView_Global_Nonlocal:  _match_FSTView,
    FSTView__body:            _match_FSTView__body,
    FSTView_arglikes:         _match_FSTView_arglikes,
    FSTView_Compare:          _match_FSTView_Compare,
    FSTView_Dict:             _match_FSTView_Dict,
    FSTView_MatchMapping:     _match_FSTView_MatchMapping,
    FSTView_arguments:        _match_FSTView_arguments,
    FSTView_dummy:            _match_FSTView_dummy,
    list:                     _match_list,
    type:                     _match_type,
    re_Pattern:               _match_re_Pattern,
    str:                      _match_str,
    int:                      _match_primitive,
    float:                    _match_primitive,
    complex:                  _match_primitive,
    bytes:                    _match_primitive,
    bool:                     _match_primitive,
    NoneType:                 _match_None,
    EllipsisType:             _match_Ellipsis,
    AST:                      _match_node,  # _match_node_nonleaf,
    Add:                      _match_node,
    And:                      _match_node,
    AnnAssign:                _match_node,
    Assert:                   _match_node,
    Assign:                   _match_node,
    AsyncFor:                 _match_node,
    AsyncFunctionDef:         _match_node,
    AsyncWith:                _match_node,
    Attribute:                _match_node,
    AugAssign:                _match_node,
    Await:                    _match_node,
    BinOp:                    _match_node,
    BitAnd:                   _match_node,
    BitOr:                    _match_node,
    BitXor:                   _match_node,
    BoolOp:                   _match_node,
    Break:                    _match_node,
    Call:                     _match_node,
    ClassDef:                 _match_node,
    Compare:                  _match_node_Compare,
    Constant:                 _match_node_Constant,
    Continue:                 _match_node,
    Del:                      _match_node_expr_context,
    Delete:                   _match_node,
    Dict:                     _match_node_Dict,
    DictComp:                 _match_node,
    Div:                      _match_node,
    Eq:                       _match_node,
    ExceptHandler:            _match_node,
    Expr:                     _match_node,
    Expression:               _match_node,
    FloorDiv:                 _match_node,
    For:                      _match_node,
    FormattedValue:           _match_node,
    FunctionDef:              _match_node,
    FunctionType:             _match_node,
    GeneratorExp:             _match_node,
    Global:                   _match_node,
    Gt:                       _match_node,
    GtE:                      _match_node,
    If:                       _match_node,
    IfExp:                    _match_node,
    Import:                   _match_node,
    ImportFrom:               _match_node,
    In:                       _match_node,
    Interactive:              _match_node,
    Invert:                   _match_node,
    Is:                       _match_node,
    IsNot:                    _match_node,
    JoinedStr:                _match_node,
    LShift:                   _match_node,
    Lambda:                   _match_node,
    List:                     _match_node,
    ListComp:                 _match_node,
    Load:                     _match_node_expr_context,
    Lt:                       _match_node,
    LtE:                      _match_node,
    MatMult:                  _match_node,
    Match:                    _match_node,
    MatchAs:                  _match_node,
    MatchClass:               _match_node,
    MatchMapping:             _match_node_MatchMapping,
    MatchOr:                  _match_node,
    MatchSequence:            _match_node,
    MatchSingleton:           _match_node,
    MatchStar:                _match_node,
    MatchValue:               _match_node,
    Mod:                      _match_node,
    Module:                   _match_node,
    Mult:                     _match_node,
    Name:                     _match_node,
    NamedExpr:                _match_node,
    Nonlocal:                 _match_node,
    Not:                      _match_node,
    NotEq:                    _match_node,
    NotIn:                    _match_node,
    Or:                       _match_node,
    Pass:                     _match_node,
    Pow:                      _match_node,
    RShift:                   _match_node,
    Raise:                    _match_node,
    Return:                   _match_node,
    Set:                      _match_node,
    SetComp:                  _match_node,
    Slice:                    _match_node,
    Starred:                  _match_node,
    Store:                    _match_node_expr_context,
    Sub:                      _match_node,
    Subscript:                _match_node,
    Try:                      _match_node,
    Tuple:                    _match_node,
    TypeIgnore:               _match_node,
    UAdd:                     _match_node,
    USub:                     _match_node,
    UnaryOp:                  _match_node,
    While:                    _match_node,
    With:                     _match_node,
    Yield:                    _match_node,
    YieldFrom:                _match_node,
    alias:                    _match_node,
    arg:                      _match_node,
    arguments:                _match_node_arguments,
    boolop:                   _match_node,
    cmpop:                    _match_node,
    comprehension:            _match_node,
    excepthandler:            _match_node,  # _match_node_nonleaf,
    expr:                     _match_node,  # _match_node_nonleaf,
    expr_context:             _match_node,  # _match_node_nonleaf,
    keyword:                  _match_node,
    match_case:               _match_node,
    mod:                      _match_node,  # _match_node_nonleaf,
    operator:                 _match_node,
    pattern:                  _match_node,  # _match_node_nonleaf,
    stmt:                     _match_node,  # _match_node_nonleaf,
    type_ignore:              _match_node,  # _match_node_nonleaf,
    unaryop:                  _match_node,
    withitem:                 _match_node,
    TryStar:                  _match_node,
    TypeAlias:                _match_node,
    type_param:               _match_node,  # _match_node_nonleaf,
    TypeVar:                  _match_node,
    ParamSpec:                _match_node,
    TypeVarTuple:             _match_node,
    TemplateStr:              _match_node,
    Interpolation:            _match_node,
    _slice:                   _match_node,  # _match_node_nonleaf,
    _ExceptHandlers:          _match_node,
    _match_cases:             _match_node,
    _Assign_targets:          _match_node,
    _decorator_list:          _match_node,
    _arglikes:                _match_node,
    _comprehensions:          _match_node,
    _comprehension_ifs:       _match_node,
    _aliases:                 _match_node,
    _withitems:               _match_node,
    _type_params:             _match_node,
    MAST:                     _match_node,  # _match_node_arbitrary_fields,
    MAdd:                     _match_node,
    MAnd:                     _match_node,
    MAnnAssign:               _match_node,
    MAssert:                  _match_node,
    MAssign:                  _match_node,
    MAsyncFor:                _match_node,
    MAsyncFunctionDef:        _match_node,
    MAsyncWith:               _match_node,
    MAttribute:               _match_node,
    MAugAssign:               _match_node,
    MAwait:                   _match_node,
    MBinOp:                   _match_node,
    MBitAnd:                  _match_node,
    MBitOr:                   _match_node,
    MBitXor:                  _match_node,
    MBoolOp:                  _match_node,
    MBreak:                   _match_node,
    MCall:                    _match_node,
    MClassDef:                _match_node,
    MCompare:                 _match_node_Compare,
    MConstant:                _match_node_Constant,
    MContinue:                _match_node,
    MDel:                     _match_node,
    MDelete:                  _match_node,
    MDict:                    _match_node_Dict,
    MDictComp:                _match_node,
    MDiv:                     _match_node,
    MEq:                      _match_node,
    MExceptHandler:           _match_node,
    MExpr:                    _match_node,
    MExpression:              _match_node,
    MFloorDiv:                _match_node,
    MFor:                     _match_node,
    MFormattedValue:          _match_node,
    MFunctionDef:             _match_node,
    MFunctionType:            _match_node,
    MGeneratorExp:            _match_node,
    MGlobal:                  _match_node,
    MGt:                      _match_node,
    MGtE:                     _match_node,
    MIf:                      _match_node,
    MIfExp:                   _match_node,
    MImport:                  _match_node,
    MImportFrom:              _match_node,
    MIn:                      _match_node,
    MInteractive:             _match_node,
    MInvert:                  _match_node,
    MIs:                      _match_node,
    MIsNot:                   _match_node,
    MJoinedStr:               _match_node,
    MLShift:                  _match_node,
    MLambda:                  _match_node,
    MList:                    _match_node,
    MListComp:                _match_node,
    MLoad:                    _match_node,
    MLt:                      _match_node,
    MLtE:                     _match_node,
    MMatMult:                 _match_node,
    MMatch:                   _match_node,
    MMatchAs:                 _match_node,
    MMatchClass:              _match_node,
    MMatchMapping:            _match_node_MatchMapping,
    MMatchOr:                 _match_node,
    MMatchSequence:           _match_node,
    MMatchSingleton:          _match_node,
    MMatchStar:               _match_node,
    MMatchValue:              _match_node,
    MMod:                     _match_node,
    MModule:                  _match_node,
    MMult:                    _match_node,
    MName:                    _match_node,
    MNamedExpr:               _match_node,
    MNonlocal:                _match_node,
    MNot:                     _match_node,
    MNotEq:                   _match_node,
    MNotIn:                   _match_node,
    MOr:                      _match_node,
    MPass:                    _match_node,
    MPow:                     _match_node,
    MRShift:                  _match_node,
    MRaise:                   _match_node,
    MReturn:                  _match_node,
    MSet:                     _match_node,
    MSetComp:                 _match_node,
    MSlice:                   _match_node,
    MStarred:                 _match_node,
    MStore:                   _match_node,
    MSub:                     _match_node,
    MSubscript:               _match_node,
    MTry:                     _match_node,
    MTuple:                   _match_node,
    MTypeIgnore:              _match_node,
    MUAdd:                    _match_node,
    MUSub:                    _match_node,
    MUnaryOp:                 _match_node,
    MWhile:                   _match_node,
    MWith:                    _match_node,
    MYield:                   _match_node,
    MYieldFrom:               _match_node,
    Malias:                   _match_node,
    Marg:                     _match_node,
    Marguments:               _match_node_arguments,
    Mboolop:                  _match_node,
    Mcmpop:                   _match_node,
    Mcomprehension:           _match_node,
    Mexcepthandler:           _match_node,  # _match_node_arbitrary_fields,
    Mexpr:                    _match_node,  # _match_node_arbitrary_fields,
    Mexpr_context:            _match_node,  # _match_node_arbitrary_fields,
    Mkeyword:                 _match_node,
    Mmatch_case:              _match_node,
    Mmod:                     _match_node,  # _match_node_arbitrary_fields,
    Moperator:                _match_node,
    Mpattern:                 _match_node,  # _match_node_arbitrary_fields,
    Mstmt:                    _match_node,  # _match_node_arbitrary_fields,
    Mtype_ignore:             _match_node,  # _match_node_arbitrary_fields,
    Munaryop:                 _match_node,
    Mwithitem:                _match_node,
    MTryStar:                 _match_node,
    MTypeAlias:               _match_node,
    Mtype_param:              _match_node,  # _match_node_arbitrary_fields,
    MTypeVar:                 _match_node,
    MParamSpec:               _match_node,
    MTypeVarTuple:            _match_node,
    MTemplateStr:             _match_node,
    MInterpolation:           _match_node,
    M_slice:                  _match_node,  # _match_node_arbitrary_fields,
    M_ExceptHandlers:         _match_node,
    M_match_cases:            _match_node,
    M_Assign_targets:         _match_node,
    M_decorator_list:         _match_node,
    M_arglikes:               _match_node,
    M_comprehensions:         _match_node,
    M_comprehension_ifs:      _match_node,
    M_aliases:                _match_node,
    M_withitems:              _match_node,
    M_type_params:            _match_node,
}


# ......................................................................................................................
# get all leaf AST types that can possibly match a given _Pattern, for search()

def _leaf_asts_default(pat: _Pattern) -> tp_Set[type[AST]] | None:
    if isinstance(pat, M_Pattern):
        return AST2ASTSLEAF[pat._types]  # will be a single type here

    if isinstance(pat, AST):
        return AST2ASTSLEAF[pat.__class__]

    if isinstance(pat, str):  # gets here from a subclassed str
        return None

    return _EMPTY_SET  # from quantifier or some subclassed primitive

def _leaf_asts_type(pat: type) -> tp_Set[type[AST]] | None:
    if issubclass(pat, M_Pattern):
        pat = pat._types  # guaranteed to be single element here

    return AST2ASTSLEAF[pat]

def _leaf_asts_all(pat: _Pattern) -> tp_Set[type[AST]] | None:
    return ASTS_LEAF__ALL

def _leaf_asts_none(pat: _Pattern) -> tp_Set[type[AST]] | None:
    return _EMPTY_SET

def _leaf_asts_unknown(pat: _Pattern) -> tp_Set[type[AST]] | None:
    return None

_LEAF_ASTS_FUNCS = {  # don't need quantifiers here because they can't be at a top level where they would influence the types that need to be checked in a search()
    M:            M._leaf_asts,
    MNOT:         MNOT._leaf_asts,
    MOR:          MOR._leaf_asts,
    MAND:         MAND._leaf_asts,
    MTYPES:       MTYPES._leaf_asts,
    MRE:          _leaf_asts_unknown,  # can match source
    MCB:          _leaf_asts_unknown,  # user determines match
    MTAG:         _leaf_asts_unknown,  # can match against arbitrary tags set by the user, not just previously matched nodes
    type:         _leaf_asts_type,
    re_Pattern:   _leaf_asts_unknown,  # can match source
    str:          _leaf_asts_unknown,  # can match source
    int:          _leaf_asts_none,
    float:        _leaf_asts_none,
    complex:      _leaf_asts_none,
    bytes:        _leaf_asts_none,
    bool:         _leaf_asts_none,
    NoneType:     _leaf_asts_none,
    EllipsisType: _leaf_asts_all,  # literally matches everything
}


# ......................................................................................................................
# sub() support stuff

# These calculate paths to repl teplate substitution slots in the repl template, which can be actual node like Name, arg
# or TypeVar or non-node identifier children of real nodes. This can also depend on other attributes of the node.

_PathsList = list[tuple[str, list[astfield], tuple[str, int | None] | None]]
_StrTagsList = list[tuple[str, int, int, int]]

_re_FST_tag = re.compile(r'\b__FST_(\w*)\b')  # for tags inside strings


def _sub_repl_path_name(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """These are all optionally-present identifiers."""

    if tag := fst_.a.name:
        if tag.startswith('__FST_'):
            paths.append((tag[6:], repl.child_path(fst_), ('name', None)))

    return True

def _sub_repl_path_ImportFrom(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Optionally-present identifier."""

    if tag := fst_.a.module:
        if tag.startswith('__FST_'):
            paths.append((tag[6:], repl.child_path(fst_), ('module', None)))

    return True

def _sub_repl_path_Global_Nonlocal(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """List of definitely-present identifiers."""

    path = None

    for idx, tag in enumerate(fst_.a.names):
        if tag.startswith('__FST_'):
            if path is None:
                path = repl.child_path(fst_)

            paths.append((tag[6:], path, ('names', idx)))

    return True

def _sub_repl_path_Constant(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Locations of slots inside `str` and `bytes` constants. It is possible for comment tags to be marked for
    substitution if they are between parts of inside innate strings, this is harmless."""

    value = fst_.a.value

    if isinstance(value, (str, bytes)):
        lines = repl._lines
        ln, col, end_ln, end_col = fst_.loc
        cur_end_col = 0x7fffffffffffffff

        while ln <= end_ln:
            if ln == end_ln:
                cur_end_col = end_col

            l = lines[ln]

            while m := _re_FST_tag.search(l, col, cur_end_col):
                start, col = m.span()

                str_tags.append((m.group()[6:], (ln, start, col), True))

            col = 0
            ln += 1

    return True

def _sub_repl_path_Attribute(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Definitely-present identifier."""

    if (tag := fst_.a.attr).startswith('__FST_'):
        paths.append((tag[6:], repl.child_path(fst_), ('attr', None)))

    return True

def _sub_repl_path_Name(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Definitely-present whole node."""

    if (tag := fst_.a.id).startswith('__FST_'):
        path = repl.child_path(fst_)

        if parent := fst_.parent:  # if we are a "value" of Dict and the key is a single-quoted string '...' then the substitution is of the whole key:value pair
            field, idx = fst_.pfield

            if (field == 'values'
                and (parenta := parent.a).__class__ is Dict
                and (key := parenta.keys[idx]).__class__ is Constant
                and key.value == '...'
            ):
                _, col, _, end_col = key.f.loc

                if end_col - col == 5:  # make sure it is a single-quoted non-implicit string
                    paths.append((tag[6:], path[:-1], ('_all', idx)))

                    return True

        paths.append((tag[6:], path, None))

    return True

def _sub_repl_path_comprehension(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Possibly the whole `comprehension` if format "for __FST_tag in '...'"."""

    ast = fst_.a

    if (not ast.ifs
        and not ast.is_async
        and (iter := ast.iter).__class__ is Constant
        and iter.value == '...'
        and (target := ast.target).__class__ is Name
        and (tag := target.id).startswith('__FST_')
    ):  # for __FST_tag in '...'
        _, col, _, end_col = iter.f.loc

        if end_col - col == 5:  # make sure it is a single-quoted non-implicit string
            paths.append((tag[6:], repl.child_path(fst_), None))

            return False  # tell caller not recurse into this node

    return True

def _sub_repl_path_ExceptHandler(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Just `ExceptHandler.name` or the whole thing if format "except '...': __FST_tag"."""

    ast = fst_.a

    if tag := ast.name:
        if tag.startswith('__FST_'):
            paths.append((tag[6:], repl.child_path(fst_), ('name', None)))

    elif ((type_ := ast.type).__class__ is Constant
        and type_.value == '...'
        and (body := ast.body)
        and (b0 := body[0]).__class__ is Expr
        and (name := b0.value).__class__ is Name
        and (tag := name.id).startswith('__FST_')
    ):  # except '...': __FST_tag
        _, col, _, end_col = type_.f.loc

        if end_col - col == 5:  # make sure it is a single-quoted non-implicit string
            paths.append((tag[6:], repl.child_path(fst_), None))

            return False  # tell caller not recurse into this node

    return True

def _sub_repl_path_arg(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Definitely-present whole node OR identifier, depending on presence of annotations in template."""

    ast = fst_.a

    if (tag := ast.arg).startswith('__FST_'):
        paths.append((tag[6:], repl.child_path(fst_), ('arg', None) if ast.annotation else None))

    return True

def _sub_repl_path_keyword(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Optionally-present identifier."""

    if tag := fst_.a.arg:
        if tag.startswith('__FST_'):
            paths.append((tag[6:], repl.child_path(fst_), ('arg', None)))

    return True

def _sub_repl_path_alias(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """One Definitely-present and one optionally-present identifier."""

    ast = fst_.a
    asname = ast.asname
    path = None

    if (tag := ast.name).startswith('__FST_'):
        path = repl.child_path(fst_)

        if not asname:  # if no asname then bump up to alias node level
            paths.append((tag[6:], path, None))

            return True

        paths.append((tag[6:], path, ('name', None)))

    if asname and asname.startswith('__FST_'):
        if path is None:
            path = repl.child_path(fst_)

        paths.append((asname[6:], path, ('asname', None)))

    return True

def _sub_repl_path_match_case(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Possibly the whole `match_case` if format "case '...': __FST_tag"."""

    ast = fst_.a

    if (not ast.guard
        and (pattern := ast.pattern).__class__ is MatchValue
        and (pat_value := pattern.value).__class__ is Constant
        and pat_value.value == '...'
        and (body := ast.body)
        and (b0 := body[0]).__class__ is Expr
        and (name := b0.value).__class__ is Name
        and (tag := name.id).startswith('__FST_')
    ):  # case '...': __FST_tag
        _, col, _, end_col = pat_value.f.loc

        if end_col - col == 5:  # make sure it is a single-quoted non-implicit string
            paths.append((tag[6:], repl.child_path(fst_), None))

            return False  # tell caller not recurse into this node

    return True

def _sub_repl_path_MatchMapping(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Optionally-present identifier."""

    if tag := fst_.a.rest:
        if tag.startswith('__FST_'):
            paths.append((tag[6:], repl.child_path(fst_), ('rest', None)))

    return True

def _sub_repl_path_MatchClass(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """List of definitely-present identifiers."""

    path = None

    for idx, tag in enumerate(fst_.a.kwd_attrs):
        if tag.startswith('__FST_'):
            if path is None:
                path = repl.child_path(fst_)

            paths.append((tag[6:], path, ('kwd_attrs', idx)))

    return True

def _sub_repl_path_MatchAs(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Definitely-present whole node OR identifier, depending on presence of pattern in template."""

    ast = fst_.a

    if tag := ast.name:
        if tag.startswith('__FST_'):
            path = repl.child_path(fst_)

            if ast.pattern:
                paths.append((tag[6:], path, ('name', None)))

                return True

            if parent := fst_.parent:  # if we are a "value" of MatchMapping and the key is a single-quoted string '...' then the substitution is of the whole key:pattern pair
                field, idx = fst_.pfield

                if (field == 'patterns'
                    and (parenta := parent.a).__class__ is MatchMapping
                    and (key := parenta.keys[idx]).__class__ is Constant
                    and key.value == '...'
                ):
                    _, col, _, end_col = key.f.loc

                    if end_col - col == 5:  # make sure it is a single-quoted non-implicit string
                        paths.append((tag[6:], path[:-1], ('_all', idx)))

                        return True

            paths.append((tag[6:], path, None))

    return True

def _sub_repl_path_TypeVar(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    """Definitely-present whole node OR identifier, depending on presence of bound or default_value in template."""

    ast = fst_.a

    if (tag := ast.name).startswith('__FST_'):
        child = ('name', None) if ast.bound or getattr(ast, 'default_value', False) else None  # default_value does not exist on py < 3.13

        paths.append((tag[6:], repl.child_path(fst_), child))

    return True

def _sub_repl_path_INVALID(paths: _PathsList, str_tags: _StrTagsList, repl: fst.FST, fst_: fst.FST) -> bool:
    raise RuntimeError('should not get here')  # pragma: no cover

_SUB_REPL_PATH_FUNCS = {
    FunctionDef:      _sub_repl_path_name,
    AsyncFunctionDef: _sub_repl_path_name,
    ClassDef:         _sub_repl_path_name,
    ImportFrom:       _sub_repl_path_ImportFrom,
    Global:           _sub_repl_path_Global_Nonlocal,
    Nonlocal:         _sub_repl_path_Global_Nonlocal,
    Constant:         _sub_repl_path_Constant,
    Attribute:        _sub_repl_path_Attribute,
    Name:             _sub_repl_path_Name,
    comprehension:    _sub_repl_path_comprehension,
    ExceptHandler:    _sub_repl_path_ExceptHandler,
    arg:              _sub_repl_path_arg,
    keyword:          _sub_repl_path_keyword,
    alias:            _sub_repl_path_alias,
    match_case:       _sub_repl_path_match_case,
    MatchMapping:     _sub_repl_path_MatchMapping,
    MatchClass:       _sub_repl_path_MatchClass,
    MatchStar:        _sub_repl_path_name,
    MatchAs:          _sub_repl_path_MatchAs,
    TypeVar:          _sub_repl_path_TypeVar,
    ParamSpec:        _sub_repl_path_name,
    TypeVarTuple:     _sub_repl_path_name,
}


_SUB_WITHITEM_SLICES = {Set, List, Tuple, MatchSequence, _Assign_targets, _decorator_list, _arglikes,
                        _comprehension_ifs, _aliases, _withitems, _type_params}


def _sub_quantifier_list_end_item(qlist: list, last: bool) -> tuple[fst.FST, str, int] | None:
    """Find the first (or last) element in a list of `FSTMatch` objects from a quantifier match, which can have a
    matched FST or FSTView or a sublist containing those.

    **Returns:**
    - `(FST, field, idx)`: Information on element found.
        - `FST`: The node in which the field of the sequence lives.
        - `field`: The name of the field, may be virtual field.
        - `idx`: The index (in the FST field) of the extremal element found. Start index if first element, stop index
            (last + 1) if last element.
    - `None`: No items found.
    """

    for match in (reversed(qlist) if last else qlist):
        if not isinstance(match, FSTMatch):
            raise MatchError(f'expected FSTMatch in list, got {match.__class__.__qualname__}')

        matched = match.matched

        if not isinstance(matched, list):
            break

        if matched:
            matched = matched[-1] if last else matched[0]

            break

    else:  # exhausted list so no item found
        return None

    if isinstance(matched, FSTView):  # if FSTView then should be a single element
        assert len(matched) == 1

        return matched.base, matched.field, matched.stop if last else matched.start

    if not isinstance(matched, fst.FST):  # can be None from Dict.keys or arguments.kw_defaults, these are not sliceable fields anyway so we don't even attempt to handle it
        raise MatchError(f'expected FST or FSTView, got {matched.__class__.__qualname__}')

    field, idx = matched.pfield
    parent = matched.parent
    parent_cls = parent.a.__class__

    if parent_cls is Call:
        if field in ('args', 'keywords'):
            idx = parent._cached_arglikes().index(matched.a)
            field = '_args'

    elif parent_cls is Compare:
        if field != 'ops':
            idx = 0 if field == 'left' else idx + 1
            field = '_all'

    elif parent_cls is ClassDef:
        if field in ('bases', 'keywords'):
            idx = parent._cached_arglikes().index(matched.a)
            field = '_bases'

    return parent, field, idx + 1 if last else idx


# ----------------------------------------------------------------------------------------------------------------------
# public FST class methods

def match(
    self: fst.FST,
    pat: _Pattern,
    *,
    ctx: bool = False,
) -> FSTMatch | None:
    r"""This will attempt to match this `self` against the given pattern. The pattern may be any of the `fst.match` `M*`
    patterns or it can be a pure `AST` pattern. Attempt to match against a `str` will check the source against that
    string. Likewise matching against a `re.Pattern` will check the source against the regex. Matching can also be done
    against a `type[AST]` or `type[MAST]` for a trivial type match. Trying to match lists or primitives with this will
    always fail (as `self` is an `FST`) and matching against a wildcard ellipsis `...` will always succeed.

    **Parameters:**
    - `pat`: The pattern to search for. Must resolve to a node, not a primitive or list (node patterns, type, wildcard,
        functional patterns of these). Because you're matching against a node, otherwise nothing will match.
    - `ctx`: Whether to match `expr_context` INSTANCES or not (`expr_context` types are always matched). Defaults to
        `False` to allow matching backreferences with different `ctx` values with each other, such as a `Name` as a
        target of an `Assign` with the same name later used in an expression (`Store` vs. `Load`). Also as a
        conveninence since when creating `AST` nodes for patterns the `ctx` field may be created automatically if
        you don't specify it so may inadvertantly break matches where you don't want to take that into
        consideration.

    **Returns:**
    - `FSTMatch`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    >>> import re
    >>> from fst.match import *
    >>> from fst.docs import ppmatch  # pretty-print FSTMatch

    Quick and dirty use of `AST` nodes and strings and regex.

    >>> f = FST('val.attr', Attribute)

    >>> f.match(Attribute(Name('val'), 'attr'))
    <FSTMatch <Attribute ROOT 0,0..0,8>>

    >>> f.match(Attribute('val', 'attr'))
    <FSTMatch <Attribute ROOT 0,0..0,8>>

    >>> f.match('val.attr')
    <FSTMatch <Attribute ROOT 0,0..0,8>>

    >>> f.match(re.compile(r'.*\.attr'))
    <FSTMatch <Attribute ROOT 0,0..0,8>>

    Pattern for finding a `logger.info()` call that has a keyword argument named `cid`, returning that keyword in a tag
    called `cid_kw`. This one uses the pattern `MCall` and `Mkeyword` classes to avoid having to specify unused required
    fields.

    >>> pat = MCall(
    ...    func=Attribute(Name('logger'), 'info'),
    ...    keywords=[MQSTAR, M(cid_kw=Mkeyword('cid')), MQSTAR]
    ... )

    >>> FST('logger.info("text", a=1, cid=123, b=2)') .match(pat)
    <FSTMatch <Call ROOT 0,0..0,38> {'cid_kw': <keyword 0,25..0,32>}>

    >>> FST('logger.warning("text", a=1, cid=123, b=2)') .match(pat)

    >>> FST('notlogger.info("text", a=1, cid=123, b=2)') .match(pat)

    >>> FST('logger.info("text", a=1, b=2)') .match(pat)

    Pattern for finding any `[*_cls | object.__class__] [is | is not] [ZST | zst.ZST]`. Will tag the initial object as
    `obj` and return whether the comparison is an `is` or `is not` in the `is_is` tag (which is missing in case of
    `IsNot` but the attribute check on the `FSTMatch` object returns a false value in this case.)

    >>> pat = Compare(
    ...     left=MOR(Attribute(M(obj=expr), '__class__'),
    ...              obj=M(Name(MRE(r'\w*_cls$')), is_name=True)),
    ...     ops=[MOR(IsNot, is_is=Is)],
    ...     comparators=[MOR(Name('ZST'), Attribute('zst', 'ZST'))],
    ... )

    >>> FST('a.__class__ is not ZST') .match(pat)
    <FSTMatch <Compare ROOT 0,0..0,22> {'obj': <Name 0,0..0,1>}>

    >>> bool(_['is_is'])
    False

    >>> FST('a.__class__ is AST') .match(pat)

    >>> ppmatch(FST('node_cls is zst.ZST') .match(pat))
    <FSTMatch <Compare ROOT 0,0..0,19>
      {'is_name': True, 'obj': <Name 0,0..0,8>, 'is_is': <Is 0,9..0,11>}>

    >>> FST('node_cls_bad is zst.ZST') .match(pat)
    """

    m = _MATCH_FUNCS.get(pat.__class__, _match_default)(pat, self.a, _MatchState(True, ctx))

    return None if m is None else FSTMatch(pat, self, m)


def search(
    self: fst.FST,
    pat: _Pattern,
    nested: bool = True,
    *,
    ctx: bool = False,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
    asts: list[AST] | None = None,
) -> Generator[FSTMatch, bool, None]:
    r"""This will walk the subtree of `self` looking for `pat` using `match()`. The walk is carried out using the
    standard `walk()` and the various parameters to that function are accepted here and passed on (check self_,
    recursion, scope, walk backwards, etc...).

    This function returns a generator similar to the `walk()` generator which can be interacted with in the same way as
    that one. Meaning you can control the recursion into children by sending `True` or `False` to this generator.
    Replacement and deletion of nodes during the search is allowed according to the rules specified by `walk()`.

    If you do not delete or `send(False)` for any given node then the search will continue into that node with the
    possibility of finding nested matches, unless you pass `nested=False` to the `search()` call.

    **Note:** The generator returned by this function does not yield the matched nodes themselves, but rather the
    `FSTMatch` objects. You can get the matched nodes from these objects using the `matched` attribute, e.g.
    `match.matched`.

    **Parameters:**
    - `pat`: The pattern to search for.
    - `nested`: Whether to recurse into nested matches or not.
    - `ctx`: Whether to match `expr_context` INSTANCES or not (`expr_context` types are always matched). Defaults to
        `False` to allow matching backreferences with different `ctx` values with each other, such as a `Name` as a
        target of an `Assign` with the same name later used in an expression (`Store` vs. `Load`). Also as a
        conveninence since when creating `AST` nodes for patterns the `ctx` field may be created automatically if
        you don't specify it so may inadvertantly break matches where you don't want to take that into
        consideration.
    - `self_`, `recurse`, `scope`, `back`, `asts`: These are parameters for the underlying `walk()` function. See that
        function for their meanings.

    **Returns:**
    - `Generator`: This is a `walk()` style generator which accepts `send(bool)` to decide whether to recurse into a
        node or not.

    **Examples:**

    >>> from fst.match import *

    >>> f = FST('''
    ... if is_AST := ast_cls is not zst.ZST:
    ...     ast = code.a
    ...
    ... if code_cls is keyword or (
    ...         code_cls is zst.ZST and code.a.__class__ is keyword):
    ...     return code_as_keyword(code, options, parse_params, sanitize=sanitize)
    ...
    ... if src_or_ast_or_fst.__class__ is ZST:
    ...     return src_or_ast_or_fst.as_(
    ...         mode, kwargs.get('copy', True), **filter_options(kwargs))
    ...
    ... return 'an ZST' if value.__class__ is not zst.ZST else None
    ... '''.strip())

    >>> pat = Compare(
    ...     left=MOR(MAttribute(attr='__class__'), Name(MRE(r'\w*_cls$'))),
    ...     ops=[MOR(IsNot, Is)],
    ...     comparators=[MOR(Name('ZST'), Attribute('zst', 'ZST'))],
    ... )

    >>> for m in f.search(pat):
    ...     print(m.matched.src)
    ast_cls is not zst.ZST
    code_cls is zst.ZST
    src_or_ast_or_fst.__class__ is ZST
    value.__class__ is not zst.ZST

    If you just want the first match.

    >>> print(next(f.search(pat)).matched.src)
    ast_cls is not zst.ZST
    """

    pat_cls = pat.__class__
    match_func = _MATCH_FUNCS.get(pat_cls, _match_default)
    walk_all = _LEAF_ASTS_FUNCS.get(pat_cls, _leaf_asts_default)(pat)  # which AST leaf nodes we need to actually check for match
    mstate = _MatchState(True, ctx)

    if walk_all is None or len(walk_all) == _LEN_ASTS_LEAF__ALL:  # checking all node types so don't need class check, if None then indeterminate and we need to check all nodes
        walk_all = True

    gen = self.walk(walk_all, self_=self_, recurse=recurse, scope=scope, back=back, asts=asts)

    for f in gen:
        mstate.clear()

        if (m := match_func(pat, f.a, mstate)) is None:
            continue

        match = FSTMatch(pat, f, m)

        if (sent := (yield match)) is not None:
            gen.send(sent)

            while (sent := (yield match)) is not None:
                gen.send(sent)

        elif not nested:  # if user didn't take control then we can decide not to recurse into match if user doesn't want nested matches
            gen.send(False)


def sub(
    self: fst.FST,
    pat: _Pattern,
    repl: Code,
    nested: bool = False,
    count: int = 0,
    *,
    loop: bool | int = False,
    copy_options: dict[str, Any] | None = None,
    repl_options: dict[str, Any] | None = None,
    ctx: bool = False,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
    asts: list[AST] | None = None,
    retn: list | None = None,
    **options,
) -> fst.FST:  # -> self
    r"""Substitute matching targets with a given `repl` template. The template substitutions can include tagged elements
    from a match. These are specified in the `repl` template as `__FST_<tag>` names, where the `<tag>` maps to a matched
    tag or is left empty to indicate the whole matched node. The replacement template can be passed as source or an
    `FST` or `AST` node.

    THIS IS AN IN-PLACE MUTATION!

    Individual options can be passed for each of the three phases of each substitution. The phases and their options are
    as follows:

    - `copy_options`: Copy tagged nodes from matched element of `self`.
    - `repl_options`: Put tagged nodes to `repl` template tag slots `__FST_<tag>`.
    - `options`: Put filled `repl` template back to `self` node which was matched by the pattern.

    If either `copy_options` or `repl_options` are not provided then the normal top level `options` are used for those.

    This function can handle individual node or slice substitutions, including compound patterns like `Dict` key:value
    pairs and whole `ExceptHandler` or `match_case` entries.

    **Parameters:**
    - `pat`: The pattern to search for. Must resolve to a node, not a primitive or list (node patterns, type, wildcard,
        functional patterns of these).
    - `repl`: Replacement template as an `FST`, `AST` or source.
    - `nested`: Whether to allow recursion into nested substitutions or not. In order to prevent infinite recursion,
        regardless of this parameter, none of the original nodes of the `repl` template are ever substituted, even if
        they match the pattern. If the full original match is put anywhere in the template then the top node of that is
        not considered for substitution again either (even though by definition it matches the pattern). Subparts of
        that matched template can be matched and substituted again as that cannot cause infinite recursion.
    - `count`: If this is above `0` then only this number of substitutions will be made. This only increments by 1 for
        each new substituted location in `self`, regardless of how many times that node is substituted with `loop` if
        that is being used.
    - `loop`: **WARNING!** Improper usage of this parameter can easily lead to infinite looping so the onus is on the
        user to make sure the replacement template cannot cause this. If this is not `False` then after each match is
        substituted then check if it still matches the pattern, and if so substitute again, up to `loop` number of
        times. A value of `True` or `0` (or below) means keep looping until the node doesn't match anymore.
    - `copy_options`: Options to use when copying from matched nodes from `self` for putting into the `repl` template.
        If `None` then just uses `options`.
    - `repl_options`: Options to use when putting into the `repl` template. If `None` then just uses `options`.
    - `ctx`: Whether to match `expr_context` INSTANCES or not (`expr_context` types are always matched). Defaults to
        `False` to allow matching backreferences with different `ctx` values with each other, such as a `Name` as a
        target of an `Assign` with the same name later used in an expression (`Store` vs. `Load`). Also as a
        conveninence since when creating `AST` nodes for patterns the `ctx` field may be created automatically if
        you don't specify it so may inadvertantly break matches where you don't want to take that into
        consideration.
    - `self_`, `recurse`, `scope`, `back`, `asts`: These are parameters for the underlying `walk()` function. See that
        function for their meanings.
    - `retn`: This is used internally to return the number of substitutions made for `subn()` to return.
    - `options`: The options to use when replacing matched nodes in `self` with the `repl` template. See `options()`.

    **Returns:**
    - `self`: Mutated in-place.

    **Examples:**

    >>> from fst.match import *

    Simple substitution.

    >>> FST('a + b.c').sub(Name, 'log(__FST_)').src
    'log(a) + log(b).c'

    >>> FST('a + b.c').sub(MOR(Name, Attribute), 'log(__FST_)').src
    'log(a) + log(b.c)'

    Allow nested substitutions and don't substitute target expressions.

    >>> FST('i = j.k = a + b.c').sub(Mexpr(ctx=Load), 'log(__FST_)', nested=True).src
    'i = log(j).k = log(a) + log(log(b).c)'

    Statements and optional parts of block statements are handled (like `else` or `finally`).

    >>> print(FST('''
    ... if a:
    ...     a_true()
    ... else:
    ...     a_false()
    ...     fail()
    ... '''.strip())
    ... .sub(MIf(test=M(t=...), body=M(b=...), orelse=M(e=...)), '''
    ... if not __FST_t:
    ...     __FST_e
    ... else:
    ...     __FST_b
    ... '''.strip()).src)
    if not a:
        a_false()
        fail()
    else:
        a_true()

    Multinode elements of sequences like `Dict` and `MatchMapping` can be substituted, in these two cases with the
    `'...': __FST_<tag>` template.

    >>> print(
    ... FST('{a: b, c: d, e: f}')
    ... .sub(MDict(_all=[..., M(mid=...), ...]),
    ... '{x: y, "...": __FST_mid}',
    ... ).src)
    {x: y, c: d}

    `arguments` can be substituted as well, including changing the type of argument (with some caveats, see
    the documentation).

    >>> print(
    ... FST('def f(a=1, /, b=2, *, c=3): pass')
    ... .sub(Marguments(_all=[MQSTAR, M(a=Marguments(args=['c'])), MQSTAR]),
    ... FST('__FST_a', 'arguments'),
    ... args_as='pos',
    ... ).src)
    def f(c=3, /): pass

    Entire `ExceptHandlers` and `match_cases` can be substituted using their respective templates
    `except '...': __FST_<tag>` and `case '...': __FST_<tag>`.

    >>> print(FST('''
    ... try: pass
    ... except a: a()
    ... except b: b()
    ... except c: c()
    ... except d: d()
    ... '''.strip())
    ... .sub(MTry(handlers=[..., MQSTAR(hand=...), ...]), '''
    ... try: new()
    ... except x: pass
    ... except '...': __FST_hand
    ... except y: pass
    ... '''.strip()).src)
    try: new()
    except x: pass
    except b: b()
    except c: c()
    except y: pass

    `comprehension` nodes have the template `for __FST_<tag> in '...'`.

    >>> print(
    ... FST('i = [a for a in b if a]')
    ... .sub(MListComp(generators=[M(comp=Mcomprehension)]),
    ... '{f(a) for __FST_comp in "..."}'
    ... ).src)
    i = {f(a) for a in b if a}

    Substitutions inside string constants are put as source appropriately escaped for the string.

    >>> print(FST(r'''
    ... something()
    ... if a:
    ...     while a: \
    ...         a = call(a, 'str')
    ... something_else()
    ... '''.strip())
    ... .sub(MWhile,
    ... 'used_to_be_while = "now is string: __FST_ <--"'
    ... ).src)
    something()
    if a:
        used_to_be_while = "now is string: while a: \\\n    a = call(a, \'str\') <--"
    something_else()

    `nested`, `loop`, `count` and `subn()`.

    >>> f = FST(r'''
    ... with a:
    ...     with b:
    ...         with c:
    ...             with d:
    ...                 with e:
    ...                     pass
    ... '''.strip())

    >>> pat = MWith(
    ...     items=M(outer_items=...),
    ...     body=[
    ...         MWith(
    ...             items=M(inner_items=...),
    ...             body=M(inner_body=...)
    ...         ),
    ...         MQSTAR(outer_body=...),
    ...     ],
    ... )

    >>> repl = '''
    ... with __FST_outer_items, __FST_inner_items:
    ...     __FST_inner_body
    ...     __FST_outer_body
    ... '''.strip()

    The `nested=True` parameter allows you to recurse into substituted nodes to continue substituting inside.

    >>> print(f.copy().sub(pat, repl, nested=True).src)
    with a, b:
        with c, d:
            with e:
                pass

    >>> print(f.copy().subn(pat, repl, nested=True))
    (<With ROOT 0,0..3,16>, 2, 2)

    The `count` parameter allows you to limit the number of unique substitutions made.

    >>> print(f.copy().sub(pat, repl, nested=True, count=1).src)
    with a, b:
        with c:
            with d:
                with e:
                    pass

    >>> print(f.copy().subn(pat, repl, nested=True, count=1))
    (<With ROOT 0,0..4,20>, 1, 1)

    The `loop` parameter allows you to iteratively apply substitution to the same node as long as it still matches the
    pattern.

    >>> print(f.copy().sub(pat, repl, loop=True).src)
    with a, b, c, d, e:
        pass

    >>> print(f.copy().subn(pat, repl, loop=True))
    (<With ROOT 0,0..1,8>, 1, 4)

    And the `subn()` function does the same thing as `sub()` but returns the number of unique and total substitutions
    made.

    >>> print(f.copy().sub(pat, repl, nested=True, loop=2).src)
    with a, b, c:
        with d, e:
            pass

    >>> print(f.copy().subn(pat, repl, nested=True, loop=2))
    (<With ROOT 0,0..2,12>, 2, 3)
    """

    if count < 0:
        count = 0

    if loop is True:
        loop = 0

    count_start = count  # so we can calculate unique location substitutions
    loop_start = loop  # so it can reset between different matches if used

    options = check_options(options, mark_checked=True)
    copy_options = options if copy_options is None else check_options(copy_options, mark_checked=True)
    repl_options = options if repl_options is None else check_options(repl_options, mark_checked=True)

    repl = code_as_all(repl, parse_params=self.root.parse_params)
    paths = []  # [(tag, path, (field, idx | None) | None), ...]  - paths to repl template substitution slots
    str_tags = []  # [(tag, (ln, col, end_col), True), ...]  - locations of substitution slots in strings (and bytes)

    for f in (gen := repl.walk(_SUB_REPL_PATH_FUNCS)):
        if not _SUB_REPL_PATH_FUNCS.get(f.a.__class__, _sub_repl_path_INVALID)(paths, str_tags, repl, f):
            gen.send(False)

    paths.extend(str_tags)  # these will wind up being processed first, from end to start
    paths.reverse()  # we do this because there might be deletions which will change indices which follow them, so we do higher indices first

    total_count = 0
    dirty = set()  # {AST, ...}
    gen = self.search(pat, nested, ctx=ctx, self_=self_, recurse=recurse, scope=scope, back=back, asts=asts)

    for m in gen:
        matched = m.matched  # will be FST node

        if matched.a in dirty:
            continue

        while True:  # for `loop`
            repl_ = repl.copy()  # this is duplication of repl template so no options needed

            dirty.update(walk(repl_.a))  # by default nothing from the repl template gets substituted

            for tag, path, child in paths:
                repl_slot_new_is_matched_root = False  # if the new node for the repl slot is the top level matched node (which should itself not be substituted again)
                one = True

                if not tag:  # this means we are replacing with the whole matched node
                    repl_slot_new_is_matched_root = True
                    repl_slot_new = matched.copy(**copy_options)

                elif (repl_slot_new := m.tags.get(tag, None)) is None:  # if tag not found then default to delete
                    pass  # noop

                elif isinstance(repl_slot_new, fst.FST):
                    repl_slot_new_is_matched_root = repl_slot_new is matched
                    repl_slot_new = repl_slot_new.copy(**copy_options)

                elif isinstance(repl_slot_new, FSTView):  # we get a normal single node container (which may contain multiple elements) for putting as a slice
                    repl_slot_new = repl_slot_new.copy(**copy_options)
                    one = False  # this will be a slice of some kind so make sure we put as a slice, even if it is a single arg in arguments posing as a slice it is fine to treat it as a slice, same for Dict and MatchMapping

                elif isinstance(repl_slot_new, list):  # this is from a quantifier, in which case convert it to a slice (all whole list fields come back as FSTView)
                    one = False

                    if not repl_slot_new or not (first := _sub_quantifier_list_end_item(repl_slot_new, False)):  # empty list is delete
                        repl_slot_new = None

                    else:
                        last_base, last_field, last_idx = _sub_quantifier_list_end_item(repl_slot_new, True)
                        first_base, first_field, first_idx = first

                        assert last_base is first_base
                        assert last_field == first_field
                        assert last_idx > first_idx

                        repl_slot_new = first_base._get_slice(first_idx, last_idx, first_field, False, copy_options)

                elif not isinstance(repl_slot_new, str):  # str could have come from static tag
                    raise MatchError('match substitution must be FST, None or str'
                                    f', got {repl_slot_new.__class__.__qualname__}')

                if child is True:  # this is a slot inside a string so we just replace it with escaped source of matched element
                    ln, col, end_col = path  # path is really these three coordinates

                    if not isinstance(repl_slot_new, fst.FST):  # is None or a string
                        src = repl_slot_new

                    else:  # there is an actual node
                        src = ''.join(
                            f'\\{c}'
                            if c in '"\'\\' else
                            c.encode('unicode_escape').decode('ascii')
                            if not c.isprintable() else
                            c
                            for c in repl_slot_new.src
                        )

                    repl_._put_src(src, ln, col, ln, end_col, True)

                    continue

                repl_slot = repl_.child_from_path(path)

                if child is not None:  # path includes a child field which means its not a real node but a str identifier, doesn't need to be marked dirty
                    field, idx = child

                    if one or idx is None:
                        repl_slot._put_one(repl_slot_new, idx, field, repl_options, False)
                    else:
                        repl_slot._put_slice(repl_slot_new, idx, idx + 1, field, repl_options)  # Global / Nonlocal

                    continue

                repl_options_ = repl_options

                if parent := repl_slot.parent:  # some fields are special-cased for simplicity and common-sense sake
                    parenta = parent.a
                    parenta_cls = parenta.__class__
                    field, idx = repl_slot.pfield
                    new_idx = None

                    if parenta_cls is Expr:  # Name with parent Expr, maybe replacing with single or body of statements, or maybe just an expression
                        if (not isinstance(repl_slot_new, fst.FST) or
                            (repl_slot_new_cls := repl_slot_new.a.__class__) in ASTS_LEAF_STMT
                        ):
                            repl_slot = parent

                        elif repl_slot_new_cls is Module:
                            repl_slot = parent
                            one = False

                    elif parenta_cls is Call:  # Call._args?
                        if field in ('args', 'keywords'):
                            new_field = '_args'
                            new_idx = parent._cached_arglikes().index(repl_slot.a)

                    elif parenta_cls is arguments:
                        if (field in _NODE_ARGUMENTS_ARGS_ALL_FIELDS
                            and (not repl_slot_new or repl_slot_new.a.__class__ is arguments)
                        ):
                            new_field = '_all'
                            allargs = parent._cached_allargs()
                            new_idx = allargs.index(repl_slot.a)
                            one = False

                            if repl_options_.get('args_as', _SENTINEL) is _SENTINEL:  # can pass args_as=None to disable the following behavior
                                if len(allargs) == 1:
                                    if field in _NODE_ARGUMENTS_ARGS_LIST_ONLY_FIELDS:  # if replacement slot is a posonly or kwonly and user did not explicitly specify an args_as transformation for putting to repl template then do it ourselves here as the user clearly intended for these to be this type of args :)
                                        repl_options_ = dict(repl_options_, args_as=
                                                            'kw_maybe' if field == 'kwonlyargs' else 'pos_maybe')
                                else:
                                    if field in _NODE_ARGUMENTS_ARGS_LIST_FIELDS:  # more than one args slot present so in this case if replacement slot is a posonly, kwonly OR normal arg and user did not explicitly specify an args_as transformation for putting to repl template then do it ourselves here as this solves a lot of other problems
                                        repl_options_ = dict(repl_options_, args_as=
                                                            'arg_maybe' if field == 'args' else
                                                            'kw_maybe' if field == 'kwonlyargs' else
                                                            'pos_maybe')

                    elif parenta_cls is Compare:  # maybe need to replace single element in compare with Compare slice
                        if not one:  # only if came from existing Compare slice
                            new_field = '_all'
                            new_idx = 0 if idx is None else idx + 1

                    elif parenta_cls is ClassDef:  # ClassDef._bases?
                        if field in ('bases', 'keywords'):
                            new_field = '_bases'
                            new_idx = parent._cached_arglikes().index(repl_slot.a)

                    elif parenta_cls is withitem:  # can be whole withitem with optional_vars to put as withitem or multiple _withitems
                        if field == 'context_expr' and not parenta.optional_vars:
                            if (not isinstance(repl_slot_new, fst.FST)
                                or (repl_slot_new_cls := repl_slot_new.a.__class__) in _SUB_WITHITEM_SLICES
                            ):
                                repl_slot = parent
                                one = False

                            elif repl_slot_new_cls is withitem:
                                repl_slot = parent

                    if new_idx is not None:  # replace is a special virtual field slice operation
                        if not repl_slot_new_is_matched_root:  # not replacing with whole matched node so don't need to mark anything dirty
                            parent._put_slice(repl_slot_new, new_idx, new_idx + 1, new_field, one, repl_options_)

                        else:  # need to do extra stuff to mark possibly multiple replacements as dirty
                            body = getattr(parent, new_field)
                            len_body = len(body)

                            parent._put_slice(repl_slot_new, new_idx, new_idx + 1, new_field, one, repl_options_)

                            if len(body) == len_body:  # only mark dirty if replaced exactly one element because otherwise it was a deletion or subslice
                                if f := body[new_idx]:
                                    dirty.add(f.a)

                        continue

                repl_slot_new = repl_slot.replace(repl_slot_new, one=one, **repl_options_)

                if repl_slot_new_is_matched_root:  # replaced with whole matched node, mark top node as dirty otherwise would cause infinite recursion, we know repl_slot_new exists because repl_slot_new_is_matched_root means it was a node going in
                    dirty.add(repl_slot_new.a)

            one = True

            if matched.a.__class__ in ASTS_LEAF_STMT:  # if putting potentially multiple statements to one then make it a slice replace
                if repl_.a.__class__ is Module:
                    one = False

            matched = matched.replace(repl_, one=one, **options)

            total_count += 1

            if loop is not False:
                if loop := loop - 1:
                    if m := matched.match(pat):  # if `matched` somehow winds up deleted as None, the match will just fail
                        matched = m.matched

                        continue

                loop = loop_start

            break

        if not (count := count - 1):
            break

    if retn is not None:  # return substitution counts
        retn[0] = (-count if count < 0 else count_start - count, total_count)

    return self


def subn(
    self: fst.FST,
    pat: _Pattern,
    repl: Code,
    nested: bool = False,
    count: int = 0,
    *,
    loop: bool | int = False,
    copy_options: dict[str, Any] | None = None,
    repl_options: dict[str, Any] | None = None,
    ctx: bool = False,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
    asts: list[AST] | None = None,
    **options,
) -> fst.FST:  # -> self
    """Perform the same operation as `sub()`, but return a tuple `(self, unique_number_of_subs_made,
    total_number_of_subs_made)`.

    **Parameters:**
    - See `sub()`.

    **Returns:**
    - `(self, unique_number_of_subs_made, total_number_of_subs_made)`:
        - `self`: Self-explanatory.
        - `unique_number_of_subs_made`: This is the number of locations in `self` that were substituted, not taking into
            account how many times each location may have been substituted due to `loop`, each location counts just
            once.
        - `total_number_of_subs_made`: This is the total number of times that substitution was done, which includes the
            number of times that `loop` was applied in each location.
    """

    retn = [None]  # used to return substitution counts

    self.sub(
        pat,
        repl,
        nested,
        count,
        loop=loop,
        copy_options=copy_options,
        repl_options=repl_options,
        ctx=ctx,
        self_=self_,
        recurse=recurse,
        scope=scope,
        back=back,
        asts=asts,
        retn=retn,
        **options,
    )

    return (self, *retn[0])
