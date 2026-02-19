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
from typing import Any, Callable, Generator, Iterable, Literal, Mapping, Sequence, Set as tp_Set, Union

from . import fst

from .asttypes import (
    ASTS_LEAF_DEF,
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
    'MTYPES',
    'MOPT',
    'MRE',
    'MCB',
    'MTAG',
    'MQ',
    'MQSTAR',
    'MQPLUS',
    'MQ01',
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
_Targets = FSTView | list[_Target] | _Target  # `str` and `None` also have special meaning outside of constant, str is identifier and None may be a missing optional AST (or other type)
_TargetsOrFST = Union[_Targets, 'fst.FST']

_Pattern = Union[_Target, type[Union['M_Pattern', AST]], 'M_Pattern', re_Pattern, EllipsisType]  # `str` here may also be a match for target node source, not just a primitive
_Patterns = list[_Pattern] | _Pattern


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
    """An error during matching."""


class FSTMatch:
    """Successful match object. Can look up tags directly on this object as attributes. Nonexistent tags will not raise
    but return a falsey `NotSet`."""

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

    def __getattr__(self, name: str) -> object:
        if (v := self.tags.get(name, _SENTINEL)) is not _SENTINEL:
            return v

        if not name.startswith('__'):
            return NotSet

        raise AttributeError(name)  # nonexistence of dunders should not be masked

    def get(self, tag: str, default: object = NotSet, /) -> object:
        """A `dict.get()` function for the match tags. Just a shortcut for `match.tags.get(tag, default)`."""

        return self.tags.get(tag, default)

_INVALID_TAGS = frozenset(dir(FSTMatch)) | set(FSTMatch.__annotations__)


class M_Pattern:
    """The base class for all non-primitive match patterns. The two main categories of patterns being `MAST` node
    matchers and the functional matchers like `MOR` and `MRE`."""

    _fields: tuple[str] = ()  # these AST attributes are here so that non-AST patterns like MOR and MF can work against ASTs, they can be overridden on a per-instance basis
    _types: type[AST] | tuple[type[AST]] = AST  # only the MTYPES pattern has a tuple here

    def _validate_tags(self, tags: Iterable[str]) -> None:
        for tag in tags:
            if tag in _INVALID_TAGS:
                raise ValueError(f'invalid tag {tag!r} shadows match class attribute')

    def match(self, target: _TargetsOrFST, *, ast_ctx: bool = False) -> FSTMatch | None:
        """Match this pattern against given target. This can take `FST` nodes or `AST` (whether they are part of an
        `FST` tree or not, meaning it can match against pure `AST` trees). Can also match primitives and lists of nodes
        if the pattern is set up for that.

        **Parameters:**
        - `target`: The target to match. Can be an `AST` or `FST` node or constant or a list of `AST` nodes or constants.
        - `ast_ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
            Defaults to `False` because when creating `AST` nodes the `ctx` field may be created automatically if you
            don't specify it so may inadvertantly break matches where you don't want to take that into consideration.
            Will always check `ctx` field for `MAST` patterns because there it is well behaved and if not specified
            is set to wildcard.

        **Returns:**
        - `FSTMatch`: The match object on successful match.
        - `None`: Did not match.
        """

        is_FST = isinstance(target, fst.FST)

        if not is_FST:
            tgt = target
        elif not (tgt := target.a):
            raise ValueError(f'{self.__class__.__qualname__}.match() called with dead FST node')

        m = _MATCH_FUNCS.get(self.__class__, _match_default)(self, tgt, _MatchState(is_FST, ast_ctx))

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

    >>> pat = Mstmt(body=[Expr(MConstant(str)), MQSTAR])

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
        self._validate_tags(tags)

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
        self._validate_tags(tagged_pats)

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


class MTYPES(M_Pattern):
    """This pattern matches any one of the given types and arbitrary fields if present. This is essentially
    `MAND(MOR(*types), MAST(**fields))`. But the types must be actual types, not other patterns.

    **Note:** Since there are several fields which can be either an individual element or list of elements, matching
    a list pattern vs. a non-list and vice versa is just treated as a non-match.

    **Parameters:**
    - `types`: An iterable of `AST` or `MAST` **TYPES**, not instances. In order to match successfully the target must
        be at least one of these types (non-leaf types like `stmt` included). If you just want to match any possible
        `AST` type with a given set of fields you can use `MAST(**fields)` instead of this.
    - `fields`: Field names which must be present (unless wildcard `...`) along with the patterns they need to match.

    **Examples:**

    Whether a statement type that CAN have a docstring actually has a docstring.

    >>> pat = MTYPES(
    ...     (ClassDef, FunctionDef, AsyncFunctionDef),
    ...     body=[Expr(MConstant(str)), MQSTAR],
    ... )

    >>> pat.match(FST('def f(): "docstr"; pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,23>>

    >>> pat.match(FST('if 1: "NOTdocstr"'))

    >>> pat.match(FST('def f(): pass; "NOTdocstr"'))

    >>> pat.match(FST('class cls: "docstr"; pass'))
    <FSTMatch <ClassDef ROOT 0,0..0,25>>
    """

    fields: Mapping[str, _Patterns]  ; """@private"""

    def __init__(self, types: Iterable[type[AST | MAST]], /, **fields: _Patterns) -> None:
        ts = {}

        for t in types:
            if not isinstance(t, type):
                raise ValueError('MTYPES types can only be AST or MAST')
            elif issubclass(t, MAST):
                t = t._types  # will be a single type, can be non-leaf
            elif not issubclass(t, AST):
                raise ValueError('MTYPES types can only be AST or MAST')

            ts[t] = True

        self._types = types = tuple(ts)
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


class MOPT(M_Pattern_One):
    """This is a pattern or `None` match. It can be used to optionally match single-element fields which may or may not
    be present. That is, both a normal value which matches the pattern and a `None` value are considered a successful
    match. A non-`None` value which does NOT match the pattern is considered a failure.

    This is essentially `MOR(pattern, None)`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> MFunctionDef(returns=MOPT('int')) .match(FST('def f(): pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,13>>

    >>> MFunctionDef(returns=MOPT('int')) .match(FST('def f() -> int: pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,20>>

    >>> MFunctionDef(returns=MOPT('int')) .match(FST('def f() -> str: pass'))

    >>> MDict([MOPT('a')], ['b']) .match(FST('{a: b}'))
    <FSTMatch <Dict ROOT 0,0..0,6>>

    >>> MDict([MOPT('a')], ['b']) .match(FST('{**b}'))
    <FSTMatch <Dict ROOT 0,0..0,5>>

    >>> MDict([MOPT('a')], ['b']) .match(FST('{x: b}'))

    >>> MMatchMapping(rest=MOPT('a')) .match(FST('{1: x, **a}', 'pattern'))
    <FSTMatch <MatchMapping ROOT 0,0..0,11>>

    >>> MMatchMapping(rest=MOPT('a')) .match(FST('{1: x, **b}', 'pattern'))

    >>> MMatchMapping(rest=MOPT('a')) .match(FST('{1: x}', 'pattern'))
    <FSTMatch <MatchMapping ROOT 0,0..0,6>>
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
        self._validate_tags(tags)

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

        self._validate_tags((self.pat,))

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

    This is the base class for `MQSTAR`, `MQPLUS`, `MQ01`, `MQMIN`, `MQMAX` and `MQN` and can do everything they can
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

    >>> FST('global a, b, c, c, d, e') .match(pat)
    <FSTMatch <Global ROOT 0,0..0,23> {'t': [<FSTMatch 'c'>, <FSTMatch 'c'>]}>

    >>> pat = MList([MQSTAR.NG, MQ(t=MRE('c|d'), min=1, max=3), MQSTAR])

    >>> ppmatch(m := FST('[a, b, c, c, d, c, e]') .match(pat))
    <FSTMatch <List ROOT 0,0..0,21>
      't': [
        <FSTMatch <Name 0,7..0,8>>,
        <FSTMatch <Name 0,10..0,11>>,
        <FSTMatch <Name 0,13..0,14>>,
      ],
    }>

    >>> [mm.matched.src for mm in m.t]
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

    # This is mostly just a data class, the actual logic for these matches lives in `_match_default()`. The tags for the
    # individual child matches are handled according to if the pattern is passed anonymously or in a tag. The static
    # tags are added once at the end of the arbitrary-length match.

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

        if min is NotSet or max is NotSet:
            raise ValueError(f'{self.__class__.__qualname__} requires both min and max values')

        if min < 0:
            raise ValueError(f'{self.__class__.__qualname__} min cannot be negative')

        if max is not None:
            if max < 0:
                raise ValueError(f'{self.__class__.__qualname__} max cannot be negative')
            if max < min:
                raise ValueError(f'{self.__class__.__qualname__} max cannot be lower than min')

        self.min = min
        self.max = max

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

    min = 0
    max = None

    def __init__(self, anon_pat: _Patterns | _NotSet = NotSet, /, **tags) -> None:
        M.__init__(self, anon_pat, **tags)

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

    min = 1
    max = None

    def __init__(self, anon_pat: _Patterns | _NotSet = NotSet, /, **tags) -> None:
        M.__init__(self, anon_pat, **tags)

    def _repr_extra(self) -> list[str]:
        return _EMPTY_LIST

class NG(MQPLUS):
    """Non-greedy default version of `MQPLUS` quantifier pattern."""

    __qualname__ = 'MQPLUS.NG'
    greedy = False

MQPLUS.NG = NG
del NG


class MQ01(MQ):
    """Zero or one quantifier pattern. Shortcut for `MQ(anon_pat, min=0, max=1, **tags)`. Has non-greedy version child
    class `MQ01.NG`.

    This class type itself as well as the the non-greedy version can be used directly as a shortcut for `MQ01(...)` or
    `MQ01.NG(...)`, the equivalents of regex `.?` and `.??`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> MList([MQ01(t='a')]) .match(FST('[]'))
    <FSTMatch <List ROOT 0,0..0,2> {'t': []}>

    >>> MList([MQ01(t='a')]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> MList([MQ01(t='a')]) .match(FST('[b]'))

    >>> MList([MQ01(t='a')]) .match(FST('[a, a]'))

    >>> MList([MQ01(t='a'), MQSTAR]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> MList([MQ01.NG(t='a'), MQSTAR]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': []}>
    """

    min = 0  # for direct type use
    max = 1

    def __init__(self, anon_pat: _Patterns | _NotSet = NotSet, /, **tags) -> None:
        M.__init__(self, anon_pat, **tags)

    def _repr_extra(self) -> list[str]:
        return _EMPTY_LIST

class NG(MQ01):
    """Non-greedy version of `MQ01` quantifier pattern."""

    __qualname__ = 'MQ01.NG'
    greedy = False

MQ01.NG = NG
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

    max = None

    def __init__(
        self, anon_pat: _Patterns | _NotSet = NotSet, /, min: int | _NotSet = NotSet, **tags
    ) -> None:
        M.__init__(self, anon_pat, **tags)

        if min is NotSet:
            raise ValueError(f'{self.__class__.__qualname__} requires a min value')
        if min < 0:
            raise ValueError(f'{self.__class__.__qualname__} min cannot be negative')

        self.min = min

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
        M.__init__(self, anon_pat, **tags)

        if max is NotSet:
            raise ValueError(f'{self.__class__.__qualname__} requires a max value')
        if max is not None and max < 0:
            raise ValueError(f'{self.__class__.__qualname__} max cannot be negative')

        self.max = max

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
        M.__init__(self, anon_pat, **tags)

        if n is NotSet:
            raise ValueError(f'{self.__class__.__qualname__} requires a count value')
        if n is not None and n < 0:
            raise ValueError(f'{self.__class__.__qualname__} count cannot be negative')

        self.min = self.max = n

    def _repr_extra(self) -> list[str]:
        return [f'n={self.min}']

MQN.NG = MQN


# ----------------------------------------------------------------------------------------------------------------------

_QUANTIFIER_STANDALONES = {MQSTAR, MQPLUS, MQ01, MQSTAR.NG, MQPLUS.NG, MQ01.NG}  # these classes types themselves (as opposed to instances) can be used in list fields

_NODE_ARGUMENTS_ARGS_FIELDS = {'args', 'kwonlyargs', 'posonlyargs'}
_NODE_ARGUMENTS_DEFAULTS_FIELDS = {'defaults', 'kw_defaults'}

_FSTVIEW_MULTINODE_SINGLE_TYPE = {
    FSTView_Dict:         Dict,
    FSTView_MatchMapping: MatchMapping,
    FSTView_arguments:    arguments,
}


class _MatchState:
    """Store running tags being built up during matching, which may be queried by `MTAG`. `tagss` is the plural of
    `tags` and indicates a list of dictionaries of tags. Merged on exit from each node that builds them up as a list
    like this."""

    is_FST: bool
    ast_ctx: bool
    all_tagss: list[list[dict[str, Any]]]

    cache: dict
    """Stores:
    - `{FSTView: _Patterns}`: For temporary conversions of `FSTView`s to `AST` patterns. Used for matching previously
        matched `FSTView`s and for `MTAG` match previously matched multinode item from `Dict`, `MatchMapping` or
        `arguments`.
    - `(pat_arg, pat_dflt, arg_fields, dflt_fields) | False`: For validated single-argument match parameters for
        matching a single `arguments` arg against `FSTView` single argument.
    """

    def __init__(self, is_FST: bool, ast_ctx: bool) -> None:
        self.is_FST = is_FST
        self.ast_ctx = ast_ctx
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
        raise MatchError(f'unsupported FSTView type {pat.__class__.__qualname__}')

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

        if stop == start:
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
        elif tgt.is_multinode or isinstance(tgt[0], str):  # could be Global/Nonlocal.names or MatchClass.kwd_attrs or multi-node items like Dict/MatchMapping/arguments
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
            if not (f := getattr(tgt, 'f', None)) or not isinstance(t := getattr(f, field, None), FSTView):  # maybe its a virtual field
                return mstate.discard_tagss()

        elif is_FST and isinstance(t, list) and not isinstance(p, list):
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
            arg_fields = _NODE_ARGUMENTS_ARGS_FIELDS

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
                if strict:
                    arg_fields = ('args',)

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

                    if strict:
                        dflt_fields = ('defaults',)

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
    the match option `ast_ctx=True`. `MLoad`, `MStore` and `MDel` don't get here, they always do a match check. A pattern
    `None` must also match one of these successfully for py < 3.13."""

    if not isinstance(tgt, expr_context) or (mstate.ast_ctx and tgt.__class__ is not pat.__class__):
        return None

    return _EMPTY_DICT

def _match_type(pat: type, tgt: _Targets, mstate: _MatchState) -> Mapping[str, Any] | None:
    """Just match the `AST` type (or equivalent `MAST` type). Special consideration is taken when matching against a
    multinode `FSTView`."""

    if issubclass(pat, M_Pattern):
        if issubclass(pat, MQ):
            raise MatchError(f'{pat.__qualname__} quantifier pattern in invalid location')

        pat = pat._types

    if t := _FSTVIEW_MULTINODE_SINGLE_TYPE.get(tgt.__class__):  # don't need to bother checking length 1
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
    MTYPES:                   _match_node,  # _match_node_arbitrary_fields,
    MOPT:                     MOPT._match,
    MRE:                      MRE._match,
    MCB:                      MCB._match,
    MTAG:                     MTAG._match,
    MQ:                       _match_quantifier_invalid_location,
    MQ.NG:                    _match_quantifier_invalid_location,
    MQSTAR:                   _match_quantifier_invalid_location,
    MQSTAR.NG:                _match_quantifier_invalid_location,
    MQPLUS:                   _match_quantifier_invalid_location,
    MQPLUS.NG:                _match_quantifier_invalid_location,
    MQ01:                     _match_quantifier_invalid_location,
    MQ01.NG:                  _match_quantifier_invalid_location,
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
# get all leaf AST types that can possibly match a given _Pattern

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


# ----------------------------------------------------------------------------------------------------------------------
# public FST class methods

def match(
    self: fst.FST,
    pat: _Pattern,
    *,
    ast_ctx: bool = False,
) -> FSTMatch | None:
    r"""This will attempt to match this `self` against the given pattern. The pattern may be any of the `fst.match` `M*`
    patterns or it can be a pure `AST` pattern. Attempt to match against a `str` will check the source against that
    string. Likewise matching against a `re.Pattern` will check the source against the regex. Matching can also be done
    against a `type[AST]` or `type[MAST]` for a trivial type match. Trying to match lists or primitives with this will
    always fail (as `self` is an `FST`) and matching against a wildcard ellipsis `...` will always succeed.

    **Parameters:**
    - `pat`: The pattern to search for. Must resolve to a node, not a primitive or list (node patterns, type, wildcard,
        functional patterns of these). Because you're matching against a node, otherwise nothing will match.
    - `ast_ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
        Defaults to `False` because when creating `AST` nodes the `ctx` field may be created automatically if you
        don't specify it so may inadvertantly break matches where you don't want to take that into consideration.
        Will always check `ctx` field for `MAST` patterns because there it is well behaved and if not specified
        is set to wildcard.

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

    >>> bool(_.is_is)
    False

    >>> FST('a.__class__ is AST') .match(pat)

    >>> ppmatch(FST('node_cls is zst.ZST') .match(pat))
    <FSTMatch <Compare ROOT 0,0..0,19>
      {'is_name': True, 'obj': <Name 0,0..0,8>, 'is_is': <Is 0,9..0,11>}>

    >>> FST('node_cls_bad is zst.ZST') .match(pat)
    """

    m = _MATCH_FUNCS.get(pat.__class__, _match_default)(pat, self.a, _MatchState(True, ast_ctx))

    return None if m is None else FSTMatch(pat, self, m)


def search(
    self: fst.FST,
    pat: _Pattern,
    nested: bool = True,
    *,
    ast_ctx: bool = False,
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
    - `ast_ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
        Defaults to `False` because when creating `AST` nodes the `ctx` field may be created automatically if you
        don't specify it so may inadvertantly break matches where you don't want to take that into consideration.
        Will always check `ctx` field for `MAST` patterns because there it is well behaved and if not specified
        is set to wildcard.
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
    asts_leaf = _LEAF_ASTS_FUNCS.get(pat_cls, _leaf_asts_default)(pat)  # which AST leaf nodes we need to actually check for match
    match_func = _MATCH_FUNCS.get(pat_cls, _match_default)
    mstate = _MatchState(True, ast_ctx)
    last_match = None  # gotten once in `all_func()` and yielded from our own generator instead of an FST node

    if asts_leaf is None or len(asts_leaf) == _LEN_ASTS_LEAF__ALL:  # checking all node types so don't need class check
        def all_func(f: fst.FST) -> bool:
            nonlocal last_match

            mstate.clear()

            if (m := match_func(pat, f.a, mstate)) is not None:
                last_match = FSTMatch(pat, f, m)

                return True

            return False

    else:
        def all_func(f: fst.FST) -> bool:
            nonlocal last_match

            if f.a.__class__ not in asts_leaf:
                return False

            mstate.clear()

            if (m := match_func(pat, f.a, mstate)) is not None:
                last_match = FSTMatch(pat, f, m)

                return True

            return False

    gen = self.walk(all_func, self_=self_, recurse=recurse, scope=scope, back=back, asts=asts)

    if nested:
        for _ in gen:
            while (sent := (yield last_match)) is not None:
                gen.send(sent)

    else:
        for _ in gen:
            if (sent := (yield last_match)) is not None:
                gen.send(sent)

                while (sent := (yield last_match)) is not None:
                    gen.send(sent)

            elif not nested:  # if user didn't take control then we can decide not to recurse into match if user doesn't want nested matches
                gen.send(False)


_SUB_IDENTIFIER_TYPES = {FunctionDef, AsyncFunctionDef, ClassDef, ImportFrom, Global, Nonlocal, Attribute, Name,
                        ExceptHandler, arg, keyword, alias, MatchMapping, MatchClass, MatchStar, MatchAs,
                        TypeVar, ParamSpec, TypeVarTuple}

def sub(
    self: fst.FST,
    pat: _Pattern,
    repl: Code,
    nested: bool | Literal['tags'] = False,
    *,
    ast_ctx: bool = False,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
    asts: list[AST] | None = None,
    **options,
) -> fst.FST:  # -> self
    """Substitute matching targets with a given `repl` template. The template substitutions can include tagged elements
    from a match, including the whole match.

    TODO: unfinished, document

    **Parameters:**
    - `pat`: The pattern to search for. Must resolve to a node, not a primitive or list (node patterns, type, wildcard,
        functional patterns of these). Because you're matching against nodes, otherwise nothing will match.
    - `repl`: Replacement template as an `FST`, `AST` or source.
    - `nested: Whether to allow recursion into nested substitutions or not. Allowing this can cause infinite recursion
        due to replacement with things that match the pattern, so don't use unless you are sure this can not happen.
        Regardless of this setting, when using a template `repl` this function will never recurse into full matched
        target substitutions (`__FST_`).  # TODO: document 'tags' mode
    - `ast_ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
        Defaults to `False` because when creating `AST` nodes the `ctx` field may be created automatically if you
        don't specify it so may inadvertantly break matches where you don't want to take that into consideration.
        Will always check `ctx` field for `MAST` patterns because there it is well behaved and if not specified
        is set to wildcard.
    - `self_`, `recurse`, `scope`, `back`, `asts`: These are parameters for the underlying `walk()` function. See that
        function for their meanings.
    - `options`: The options to use for the `replace()` calls. See `options()`.

    **Returns:**
    - `self`

    **Examples:**

    >>> from fst.match import *

    Add a 'cid=CID' keyword parameter to all `logger.info()` calls that don't have a `cid` already.

    >>> src = '''
    ... logger.info('Hello world...')  # ok
    ... logger.info('Already have id', cid=other_cid)  # ok
    ... logger.info()  # yes, no logger message, too bad
    ... (logger).info(  # just checking
    ...     f'not a {thing}',  # this is fine
    ...     extra=extra,       # also this
    ... )
    ... '''.strip()

    >>> pat = MCall(
    ...    func=M(func=MAttribute('logger', 'info')),
    ...    keywords=MNOT([MQSTAR, Mkeyword('cid'), MQSTAR]),
    ...    _args=M(all_args=...),
    ... )

    >>> repl = '__FST_func(__FST_all_args, cid=CID)'

    >>> print(FST(src).sub(pat, repl).src)
    logger.info('Hello world...', cid=CID)  # ok
    logger.info('Already have id', cid=other_cid)  # ok
    logger.info(cid=CID)  # yes, no logger message, too bad
    (logger).info(
                  f'not a {thing}',  # this is fine
                  extra=extra,       # also this
                  cid=CID)
    """

    check_options(options)

    repl = code_as_all(repl, options, self.root.parse_params)

    nested_tags = nested == 'tags'
    dirty = set()  # {AST, ...}
    paths_matched = []  # [(tag, path, (field, idx | None) | None), ...]  an empty string tag means replace with the node matched, will only be empty in this one, will never be empty in paths_tags
    paths_tag = []  # same format as paths_matched
    all_paths = (paths_matched, paths_tag)  # we have two lists because whenever we replace with whole matched target we have to mark it as dirty so we don't recurse into it again, don't need to do this for tags

    for f in repl.walk(_SUB_IDENTIFIER_TYPES):
        a = f.a
        a_cls = a.__class__

        if a_cls is Name:
            tag = a.id

        elif a_cls is arg:
            tag = a.arg

            if a.annotation:
                if tag.startswith('__FST_'):
                    paths_tag.append((tag[6:], repl.child_path(f), ('arg', None)))  # non-node replacements can all go into the tag list because they do not need to be marked as dirty

                continue

        elif a_cls is TypeVar:
            tag = a.name

            if a.bound or getattr(a, 'default_value', False):  # default_value does not exist on py < 3.13
                if tag.startswith('__FST_'):
                    paths_tag.append((tag[6:], repl.child_path(f), ('name', None)))  # non-node replacements can all go into the tag list because they do not need to be marked as dirty

                continue

        else:
            if a_cls is Attribute:
                tag = a.attr
                child = ('attr', None)

            elif a_cls in ASTS_LEAF_DEF:
                tag = a.name
                child = ('name', None)

            elif a_cls is keyword:
                if not (tag := a.arg):
                    continue

                child = ('arg', None)

            elif a_cls is alias:
                path = repl.child_path(f)
                tag = a.name

                if tag.startswith('__FST_'):
                    paths_tag.append((tag[6:], path, ('name', None)))

                if tag := a.asname:
                    if tag.startswith('__FST_'):
                        paths_tag.append((tag[6:], path, ('asname', None)))

                continue

            elif a_cls is ImportFrom:
                if not (tag := a.module):
                    continue

                child = ('module', None)

            elif a_cls in ASTS_LEAF_VAR_SCOPE_DECL:
                path = repl.child_path(f)

                for idx, tag in list(enumerate(a.names))[::-1]:
                    if tag.startswith('__FST_'):
                        paths_tag.append((tag[6:], path, ('names', idx)))

                continue

            elif a_cls is ParamSpec:
                tag = a.name
                child = ('name', None)

            elif a_cls is TypeVarTuple:
                tag = a.name
                child = ('name', None)

            elif a_cls is MatchAs:
                if not (tag := a.name):
                    continue

                child = ('name', None)

            elif a_cls is MatchMapping:
                if not (tag := a.rest):
                    continue

                child = ('rest', None)

            elif a_cls is MatchClass:
                path = repl.child_path(f)

                for idx, tag in list(enumerate(a.kwd_attrs))[::-1]:
                    if tag.startswith('__FST_'):
                        paths_tag.append((tag[6:], path, ('kwd_attrs', idx)))

                continue

            elif a_cls is MatchStar:
                if not (tag := a.name):
                    continue

                child = ('name', None)

            elif a_cls is ExceptHandler:
                if not (tag := a.name):
                    continue

                child = ('name', None)

            else:
                raise RuntimeError('should not get here')

            if tag.startswith('__FST_'):
                paths_tag.append((tag[6:], repl.child_path(f), child))  # non-node replacements can all go into the tag list because they do not need to be marked as dirty

            continue

        if tag.startswith('__FST_'):
            (paths_tag if (tag := tag[6:]) else paths_matched).append((tag, repl.child_path(f), None))

    gen = self.search(pat, nested=bool(nested), ast_ctx=ast_ctx,
                      self_=self_, recurse=recurse, scope=scope, back=back, asts=asts)

    for m in gen:
        tgt = m.matched  # will be FST node

        if tgt.a in dirty:
            continue

        sub = repl.copy()

        dirty.update(walk(sub.a))

        for paths in all_paths:
            for tag, path, child in paths:
                sub_tgt = sub.child_from_path(path)
                one = True

                if not tag:
                    sub_sub = tgt.copy()

                elif (sub_sub := m.tags.get(tag, _SENTINEL)) is _SENTINEL:
                    raise MatchError(f'{tag!r} tag not found for substitution')

                elif isinstance(sub_sub, fst.FST):
                    sub_sub = sub_sub.copy()

                elif isinstance(sub_sub, FSTView):  # we get a normal single element for putting as a slice
                    sub_sub = sub_sub.copy()
                    one = False  # this will be a slice of some kind so make sure we put as a slice

                elif not isinstance(sub_sub, (AST, str, NoneType)):
                    raise MatchError(f'match substitution must be FST, AST, str or None, got {sub_sub}')

                if child is not None:  # path includes a child field which means its not a real node but an identifier
                    field, idx = child

                    sub_tgt.put(sub_sub, idx, field, **options)

                else:
                    if parent := sub_tgt.parent:  # some fields are special-cased for simplicity and common-sense sake
                        parenta_cls = parent.a.__class__
                        field, idx = sub_tgt.pfield
                        new_idx = None

                        if parenta_cls is Expr:  # maybe replacing with single or body of statements
                            if not one and sub_sub.a.__class__ is Module and (grandparent := parent.parent):
                                field, new_idx = parent.pfield
                                parent = grandparent

                        elif parenta_cls is Call:  # Call._args?
                            if field in ('args', 'keywords'):
                                field = '_args'
                                new_idx = parent._cached_arglikes().index(sub_tgt.a)

                        elif parenta_cls is arguments:
                            if sub_sub.a.__class__ is arguments:
                                field = '_all'
                                allargs = parent._cached_allargs()
                                one = False

                                try:
                                    new_idx = allargs.index(sub_tgt.a)
                                except ValueError:
                                    raise MatchError('cannot substitute arguments for a non-arg') from None

                        elif parenta_cls is Compare:  # maybe need to replace single element in compare with Compare slice
                            if not one:  # only if came from existing Compare slice
                                field = '_all'
                                new_idx = 0 if idx is None else idx + 1

                        elif parenta_cls is ClassDef:  # ClassDef._bases?
                            if field in ('bases', 'keywords'):
                                field = '_bases'
                                new_idx = parent._cached_arglikes().index(sub_tgt.a)

                        if new_idx is not None:
                            if tag:  # not replacing with original whole node so don't need to mark dirty
                                parent._put_slice(sub_sub, new_idx, new_idx + 1, field, one, options)

                            else:  # need to do extra stuff to mark possibly multiple replacements as dirty
                                view = getattr(parent, field)
                                len_original_field = len(view)

                                parent._put_slice(sub_sub, new_idx, new_idx + 1, field, one, options)

                                if (delta := len(view) - len_original_field) >= 0:  # only if replaced or added, if length contracted then there was deletion
                                    for f in view[new_idx : new_idx + 1 + delta]:
                                        if f:
                                            dirty.add(f.a)

                            continue

                    f = sub_tgt.replace(sub_sub, one=one, **options)

                    if not tag and f:  # replaced with original whole matched element, mark as dirty
                        dirty.add(f.a)

            if nested_tags and paths is paths_matched:
                dirty.update(walk(sub.a))

        tgt = tgt.replace(sub, **options)

    return self
