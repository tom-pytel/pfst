"""Structural node pattern matching. Uses `AST`-like and even `AST` nodes themselves for patterns. Ellipsis is used in
patterns as a wildcard and several extra functional types are provided for setting tags, regex string matching, logic
operations and match check callbacks.

To be completely safe and future-proofed, you may want to only use the `M*` pattern types from this submodule, but for
quick use normal `AST` types should be fine. Also you need to use the pattern types provided here if you will be using
nodes or fields which do not exist in the version of the running Python.

In the examples here you will see `AST` nodes used interchangeably with their `MAST` pattern counterparts. For the most
part this is fine and there are only a few small differences between using the two. Except if you are using a type
checker...

**Note:** Annoyingly this module breaks the convention that anything that has `FST` class methods imported into the main
`FST` class has a filename that starts with `fst_`. This is so that `from fst.match import *` and
`from fst import match as m` is cleaner.
"""

from __future__ import annotations

import re
from re import Pattern as re_Pattern
from types import EllipsisType, MappingProxyType, NoneType
from typing import Any, Callable, Generator, Iterable, Literal, Mapping, Set as tp_Set, Union

from . import fst

from .asttypes import (
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
from .view import FSTView, FSTView_Dict, FSTView_MatchMapping, FSTView_arguments
from .fst_options import check_options

__all__ = [
    'MatchError',
    'NoTag',
    'FSTMatch',
    'M_Pattern',

    'M',
    'MNOT',
    'MOR',
    'MAND',
    'MANY',
    'MOPT',
    'MRE',
    'MCB',
    'MTAG',
    'MN',
    'MSTAR',
    'MPLUS',
    'MQMARK',
    'MMIN',
    'MMAX',

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
_EMPTY_DICT = {}
_EMPTY_SET = set()
_LEN_ASTS_LEAF__ALL = len(ASTS_LEAF__ALL)
__DIRTY = 0xfc942b31  # for sub(), start at high enough number that it will probably be unique

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
        return o.__name__

    if isinstance(o, AST):
        return f'{o_cls.__name__}({", ".join(f"{f}={_rpr(getattr(o, f, None))}" for f in o._fields if f != "ctx")})'

    if isinstance(o, list):
        return f'[{", ".join(_rpr(e) for e in o)}]'

    return repr(o)


class _NoTag:
    """This exists for FSTMatch so that we can check value of any tag without needing to check if it exists first."""

    __slots__ = ()

    def __new__(cls) -> FSTMatch._NoTag:
        return NoTag

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return '<NoTag>'

NoTag = object.__new__(_NoTag)  ; """A falsey object returned if accessing a non-existent tag on the `FSTMatch` object as an attribute."""


class MatchError(RuntimeError):
    """An error during matching."""


class FSTMatch:
    """Successful match object. Can look up tags directly on this object as attributes. Nonexistent tags will not raise
    but return a falsey `NoTag`."""

    tags: Mapping[str, Any]  ; """Full match tags dictionary. Only successful matches get their tags included."""
    pattern: _Pattern  ; """The pattern used for the match. Can be any valid pattern including `AST` node, primitive values, compiled `re.Pattern`, etc..."""
    matched: _TargetsOrFST  ; """What was matched. Does not have to be a node as list and primitive matches can be tagged."""

    def __init__(self, pattern: _Pattern, matched: _TargetsOrFST, tags: Mapping[str, Any]) -> None:
        self.pattern = pattern
        self.matched = matched
        self.tags = MappingProxyType(tags)

    def __repr__(self) -> str:
        if tags := self.tags:
            return f'<FSTMatch {_rpr(self.matched)} {{{", ".join(f"{k!r}: {_rpr(v)}" for k, v in tags.items())}}}>'
        else:
            return f'<FSTMatch {_rpr(self.matched)}>'

    def __getattr__(self, name: str) -> object:
        if (v := self.tags.get(name, _SENTINEL)) is not _SENTINEL:
            return v

        if not name.startswith('__'):
            return NoTag

        raise AttributeError(name)  # nonexistence of dunders should not be masked

    def get(self, tag: str, default: object = None, /) -> object:
        """A `dict.get()` function for the match tags. Just a shortcut for `match.tags.get(tag, default)`."""

        return self.tags.get(tag, default)

_INVALID_TAGS = frozenset(dir(FSTMatch)) | set(FSTMatch.__annotations__)


class M_Pattern:
    """The base class for all non-primitive match patterns. The two main categories of patterns being `MAST` node
    matchers and the functional matchers like `MOR` and `MRE`."""

    _fields: tuple[str] = ()  # these AST attributes are here so that non-AST patterns like MOR and MF can work against ASTs, they can be overridden on a per-instance basis
    _types: type[AST] | tuple[type[AST]] = AST  # only the MANY pattern has a tuple here

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

        m = _MATCH_FUNCS.get(self.__class__, _match_default)(self, tgt, _MatchContext(is_FST, ast_ctx))

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

    >>> pat = Mstmt(body=[Expr(MConstant(str)), ...])

    >>> pat.match(FST('def f(): "docstr"; pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,23>>

    >>> pat.match(FST('class cls: "docstr"'))
    <FSTMatch <ClassDef ROOT 0,0..0,19>>

    >>> pat.match(FST('class cls: 1'))

    >>> pat.match(FST('class cls: 1; "NOTdocstr"'))

    >>> pat.match(FST('class cls: pass'))
    """

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
    """"""
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

class _MatchContext:
    """Store running tags being built up during matching, which may be queried by `MTAG`. `tagss` is the plural of
    `tags` and indicates a list of dictionaries of tags. Merged on exit from each node that builds them up as a list
    like this."""

    is_FST: bool
    ast_ctx: bool
    all_tagss: list[list[dict[str, Any]]]
    fstview_pat_cache: dict[FSTView, _Pattern]  # may need to temporarily convert FSTViews to AST patterns, specifically for MTAG match previously matched multinode item from Dict, MatchMapping or arguments

    def __init__(self, is_FST: bool, ast_ctx: bool) -> None:
        self.is_FST = is_FST
        self.ast_ctx = ast_ctx
        self.all_tagss = []
        self.fstview_pat_cache = {}

    def clear(self) -> None:
        """Clean up anything from a previous match attempt."""

        self.all_tagss = []
        self.fstview_pat_cache = {}

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

    def get_tag(self, tag: str) -> object:
        """Walk running list of dictionaries backwards checking for `tag`."""

        for tagss in reversed(self.all_tagss):
            for m in reversed(tagss):
                if (v := m.get(tag, _SENTINEL)) is not _SENTINEL:
                    return v

        return _SENTINEL

    def fstview_as_pat(self, view: FSTView) -> _Pattern:
        """Temporary concrete pattern for matching against the given `FSTView`. Created once and cached."""

        if pat := self.fstview_pat_cache.get(view):
            pass  # noop

        elif isinstance(view, FSTView_Dict):
            start, stop = view.start_and_stop
            ast = view.base.a
            pat = self.fstview_pat_cache[view] = MDict(ast.keys[start : stop], ast.values[start: stop])

        elif isinstance(view, FSTView_arguments):


            # TODO: this


            raise NotImplementedError

        elif isinstance(view, FSTView_MatchMapping):
            start, stop = view.start_and_stop
            ast = view.base.a

            if view.has_rest:
                stop -= 1
                pat = self.fstview_pat_cache[view] = MMatchMapping(ast.keys[start : stop], ast.patterns[start : stop],
                                                                   ast.rest)
            else:
                pat = self.fstview_pat_cache[view] = MMatchMapping(ast.keys[start : stop], ast.patterns[start : stop])

        else:
            raise MatchError('unsupported FSTView type')

        return pat


class M(M_Pattern):
    """Tagging pattern container. If the given pattern matches then tags specified here will be returned in the
    `FSTMatch` result object. The tags can be static values but also the matched node can be returned in a given tag if
    the pattern is passed as a keyword parameter (the first one).

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

    _requires = 'pattern'  # for printing error message

    pat: _Patterns  ; """@private"""
    pat_tag: str | None  ; """@private"""
    static_tags: Mapping[str, Any]  ; """@private"""

    def __init__(self, anon_pat: _Patterns = _SENTINEL, /, **tags) -> None:
        self._validate_tags(tags)

        if anon_pat is not _SENTINEL:
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
        name = self.__class__.__name__
        pat = self.pat
        pat_tag = self.pat_tag

        if tags := self.static_tags:
            tags = ', '.join(f'{t}={_rpr(p)}' for t, p in tags.items())

            return f'{name}({pat_tag}={_rpr(pat)}, {tags})' if pat_tag else f'{name}({_rpr(pat)}, {tags})'

        return f'{name}({pat_tag}={_rpr(pat)})' if pat_tag else f'{name}({_rpr(pat)})'

    def _match(self, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        m = _MATCH_FUNCS.get((p := self.pat).__class__, _match_default)(p, tgt, mctx)

        if m is None:
            return None

        if pat_tag := self.pat_tag:
            if mctx.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')

            if m:
                return {**m, pat_tag: tgt, **self.static_tags}

            return {pat_tag: tgt, **self.static_tags}

        if m:
            return dict(m, **self.static_tags)

        return self.static_tags

    def _leaf_asts(self) -> tp_Set[type[AST]]:
        return _LEAF_ASTS_FUNCS.get((p := self.pat).__class__, _leaf_asts_default)(p)


class MNOT(M):
    """Tagging NOT logic pattern container. If the given pattern **DOES NOT** match then tags specified here will be
    returned in the `FSTMatch` result object. The tags can be specified with static values but also the unmatched node
    can be returned in a given tag name.

    Any tags that were being propagated up from successful matches are discarded since that constitutes an unsuccessful
    match for this node. And any unsuccessful matches were not propagating any tags up anyway. So this node guarantees
    that the only tags that it returns are ones that it itself provides.

    **Parameters:**
    - `anon_pat`: If the pattern to not match is provided in this then the unmatched node is not returned in tags. If
        this is missing (default `None`) then there must be at least one element in `tags` and the first keyword there
        will be taken to be the pattern to not match and the name of the tag to use for the unmatched node.
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

    @staticmethod
    def _match(self: MNOT, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        m = _MATCH_FUNCS.get((p := self.pat).__class__, _match_default)(p, tgt, mctx)

        if m is not None:
            return None

        if pat_tag := self.pat_tag:
            if mctx.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')

            return {pat_tag: tgt, **self.static_tags}

        return self.static_tags

    def _leaf_asts(self) -> tp_Set[type[AST]]:
        leaf_asts = _LEAF_ASTS_FUNCS.get((p := self.pat).__class__, _leaf_asts_default)(p)

        if not leaf_asts:
            return ASTS_LEAF__ALL
        elif len(leaf_asts) >= _LEN_ASTS_LEAF__ALL:  # >= because maybe some extra node types got in there from the future
            return _EMPTY_SET

        return ASTS_LEAF__ALL - leaf_asts


class MOR(M_Pattern):
    """Simple OR pattern. Matches if any of the given patterns match.

    **Parameters:**
    - `anon_pats`: Patterns that constitute a successful match, only need one to match. Checked in order.
    - `tagged_pats`: Patterns that constitute a successful match, only need one to match. Checked in order. The first
        target matched with any one of these patterns will be returned in its corresponding tag (keyword name).

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

    pats:     list[_Patterns]  ; """@private"""
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

    def _match(self, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        for i, p in enumerate(self.pats):
            m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, mctx)

            if m is not None:
                if pat_tag := self.pat_tags[i]:
                    if mctx.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                        raise MatchError('match found an AST node without an FST')

                    return {**m, pat_tag: tgt}

                return m

        return None

    def _leaf_asts(self) -> tp_Set[type[AST]]:
        leaf_asts = set()

        for pat in self.pats:
            la = _LEAF_ASTS_FUNCS.get(pat.__class__, _leaf_asts_default)(pat)

            if len(la) >= _LEN_ASTS_LEAF__ALL:  # early out because we hit all possible types
                return la

            leaf_asts.update(la)

            if len(leaf_asts) >= _LEN_ASTS_LEAF__ALL:  # another early out
                return leaf_asts

        return leaf_asts


class MAND(MOR):
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

    >>> pat = MList(MAND(['a', ...], [..., 'b', ..., 'b', ...]))

    >>> pat.match(FST('[a, b, c]'))

    >>> pat.match(FST('[a, b, b, c]'))
    <FSTMatch <List ROOT 0,0..0,12>>

    >>> pat.match(FST('[d, a, b, b, c]'))

    >>> pat.match(FST('[a, x, b, y, z, b, c, b]'))
    <FSTMatch <List ROOT 0,0..0,24>>
    """

    def _match(self, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        if mctx.is_FST and isinstance(tgt, AST):
            if not (tgtf := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')
        else:
            tgtf = tgt

        tagss = mctx.new_tagss()

        for i, p in enumerate(self.pats):
            m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, mctx)

            if m is None:
                return mctx.discard_tagss()

            if pat_tag := self.pat_tags[i]:
                tagss.append({**m, pat_tag: tgtf})
            elif m:
                tagss.append(m)

        return mctx.pop_merge_tagss()

    def _leaf_asts(self) -> tp_Set[type[AST]]:
        leaf_asts = ASTS_LEAF__ALL

        for pat in self.pats:
            la = _LEAF_ASTS_FUNCS.get(pat.__class__, _leaf_asts_default)(pat)

            if not la:  # early out because everything gone
                return la

            leaf_asts = leaf_asts & la

            if not leaf_asts:  # another early out
                return leaf_asts

        return leaf_asts


class MANY(M_Pattern):
    """This pattern matches any one of the given types and arbitrary fields if present. And its "m-any" as in "any one
    of", not "many" as in "several", though that fits as well. Essentially this is an AND of whether the node type is
    one of those provided and the given fields match.

    This is essentially `MAND(MOR(*types), MAST(**fields))`. But the types must be actual types, not other patterns.

    **Note:** Since there are several fields which can be either an individual element or list of elements, matching
    a list pattern vs. a non-list and vice versa is just treated as a non-match.

    **Parameters:**
    - `types`: An iterable of `AST` or `MAST` **TYPES**, not instances. In order to match successfully the target must
        be at least one of these types (non-leaf types like `stmt` included). To match any node for type use `AST`.
    - `fields`: Field names which must be present (unless wildcard `...`) along with the patterns they need to match.

    **Examples:**

    Whether a statement type that CAN have a docstring actually has a docstring.

    >>> pat = MANY(
    ...     (ClassDef, FunctionDef, AsyncFunctionDef),
    ...     body=[Expr(MConstant(str)), ...],
    ... )

    >>> pat.match(FST('def f(): "docstr"; pass'))
    <FSTMatch <FunctionDef ROOT 0,0..0,23>>

    >>> pat.match(FST('if 1: "NOTdocstr"'))

    >>> pat.match(FST('def f(): pass; "NOTdocstr"'))

    >>> pat.match(FST('class cls: "docstr"; pass'))
    <FSTMatch <ClassDef ROOT 0,0..0,25>>
    """

    fields: Mapping[str, _Patterns]  ; """@private"""

    def __init__(self, types: Iterable[type[AST | MAST]], **fields: _Patterns) -> None:
        ts = {}

        for t in types:
            if not isinstance(t, type):
                raise ValueError('MANY types can only be AST or MAST')
            elif issubclass(t, MAST):
                t = t._types  # will be a single type, can be non-leaf
            elif not issubclass(t, AST):
                raise ValueError('MANY types can only be AST or MAST')

            ts[t] = True

        self._types = types = tuple(ts)
        self.fields = fields

        if not types:
            raise ValueError('MANY requires at least one AST type to match')

        if fields:
            self._fields = tuple(fields)

            for field, value in fields.items():
                setattr(self, field, value)

    def __repr__(self) -> str:
        name = self.__class__.__name__
        types = f'[{", ".join(_rpr(e) for e in self._types)}]'

        if fields := self.fields:
            return f'{name}({types}, {", ".join(f"{f}={_rpr(v)}" for f, v in fields.items())})'

        return f'{name}({types})'

    def _leaf_asts(self) -> tp_Set[type[AST]]:
        leaf_asts = set()

        for t in self._types:
            la = AST2ASTSLEAF[t]

            if len(la) >= _LEN_ASTS_LEAF__ALL:  # early out because we hit all possible types
                return la

            leaf_asts.update(la)

            if len(leaf_asts) >= _LEN_ASTS_LEAF__ALL:  # another early out
                return leaf_asts

        return leaf_asts


class MOPT(M):
    """This is a pattern or `None` match. It can be used to optionally match single-element fields which may or may not
    be present. That is, both a normal value which matches the pattern and a `None` value are considered a successful
    match. A non-`None` value which does NOT match the pattern is considered a failure.

    This is essentially `MOR(pattern, None)`.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern. Setting this to `...` is the same as not having it present.
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

    def _match(self, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        if tgt is None:
            if pat_tag := self.pat_tag:
                return {pat_tag: [], **self.static_tags}

            return self.static_tags

        pat = self.pat
        m = _MATCH_FUNCS.get(pat.__class__, _match_default)(pat, tgt, mctx)

        if m is None:
            return None

        if pat_tag := self.pat_tag:
            if mctx.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')

            return {pat_tag: [FSTMatch(pat, tgt, m)], **self.static_tags}

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

    >>> MRE('good|bad|ugly') .match(Name('ugly'))
    <FSTMatch Name(id='ugly')>

    >>> MRE('good|bad|ugly') .match(Name('passable'))

    Has bad in it.

    >>> MRE(tag='.*bad.*') .match(arg('this_arg_is_not_so_bad'))
    <FSTMatch arg(arg='this_arg_is_not_so_bad', annotation=None, type_comment=None) {'tag': <re.Match object; span=(0, 22), match='this_arg_is_not_so_bad'>}>

    Another way so we can get the exact location from the `re.Match` object.

    >>> MRE(tag='bad', search=True) .match(arg('this_arg_is_not_so_bad'))
    <FSTMatch arg(arg='this_arg_is_not_so_bad', annotation=None, type_comment=None) {'tag': <re.Match object; span=(19, 22), match='bad'>}>

    >>> MDict(_all=[MN(t=MRE('a: .'))]) .match(FST('{a: b, a: z}'))
    <FSTMatch <Dict ROOT 0,0..0,12> {'t': [<FSTMatch <<Dict ROOT 0,0..0,12>._all[:1]>>, <FSTMatch <<Dict ROOT 0,0..0,12>._all[1:2]>>]}>
    """

    re_pat: re_Pattern  ; """@private"""
    pat_tag: str | None  ; """@private"""
    static_tags: Mapping[str, Any]  ; """@private"""
    search: bool  ; """@private"""

    def __init__(
        self, anon_re_pat: str | re_Pattern | None = None, /, flags: int = 0, search: bool = False, **tags
    ) -> None:
        self._validate_tags(tags)

        if anon_re_pat is not None:
            pat_tag = None
        elif (pat_tag := next(iter(tags), None)) is None:
            raise ValueError('MRE requires pattern')
        else:
            anon_re_pat = tags.pop(pat_tag)

        if not isinstance(anon_re_pat, re_Pattern):
            anon_re_pat = re.compile(anon_re_pat, flags)
        elif flags:
            raise ValueError('MRE cannot take flags for already compiled re.Pattern')

        self.re_pat = anon_re_pat
        self.pat_tag = pat_tag
        self.search = search
        self.static_tags = tags

    def __repr__(self) -> str:
        name = self.__class__.__name__
        re_pat = _rpr(self.re_pat)
        pat_tag = self.pat_tag
        tags = [f'{pat_tag}={re_pat}' if pat_tag else re_pat]

        if self.search:
            tags.append('search=True')

        tags.extend(f'{t}={_rpr(p)}' for t, p in self.static_tags)

        return f'{name}({", ".join(tags)})'

    def _match(self, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        """Regex match or search pattern against direct `str` or `bytes` value or source if `tgt` is an actual node. Will
        use `FST` source from the tree and unparse a non-`FST` `AST` node for the check. Returns `re.Match` object if is
        requested."""

        re_pat = self.re_pat
        re_func = re_pat.search if self.search else re_pat.match

        if (m := _match_re_Pattern(re_pat, tgt, mctx, re_func)) is None:
            return None

        if pat_tag := self.pat_tag:
            return {pat_tag: m, **self.static_tags}

        return self.static_tags


class MCB(M):
    """Callback to check target, which can be a node (`AST` or `FST` depending on the type of tree the pattern was
    called on) or constant or a list of `AST`s or constants.

    **Parameters:**
    - `anon_callback`: The function to call on each target to check. Depending on where in the pattern structure this
        pattern is used, the function may be called with n node or a primitive, or even a list of elements. Further,
        depending on the initial target of the match, the node may be `FST` if the target was an `FST` node and `AST`
        otherwise. If the function returns a truthy value then the match is considered a success, and likewise falsey
        means failure. If this is not provided then the callback is taken from the first keyword in `tags` just like for
        the `M` pattern.
    - `tag_ret`: If this is set to `True` then the truthy return value is returned in the pattern tag instead of the
        target matched. This only applies if the callback is passed as the first keyword in `tags` instead of in
        `anon_callback`, as in that case no target tag is available to return. Also keep in mind the "truthy value" bit
        in case a successful match might want to return a falsey value, it would need to be accomodated somehow (wrapped
        in a tuple maybe). Or just provide an explicit `fail_val` to check against to determine failure.
    - `fail_val`: An explicit value to check equality against to determine if the callback failed.

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

    An explicit fail value can be provided in case you want to be able to tag falsey values directly, it is checked by
    equality.

    >>> MCB(tag=lambda f: False, tag_ret=True, fail_val=None) .match(FST('a'))
    <FSTMatch <Name ROOT 0,0..0,1> {'tag': False}>

    >>> MCB(tag=lambda f: None, tag_ret=True, fail_val=None) .match(FST('a'))

    The type of node passed to the callback depends on the type of tree that `match()` is called on.

    >>> pat = MCB(lambda n: print(type(n)))

    >>> pat.match(Name('name'))
    <class 'ast.Name'>

    >>> pat.match(FST('name'))
    <class 'fst.fst.FST'>
    """

    _requires = 'callback'  # for printing error message

    pat: Callable[[_Target], object] | Callable[[_TargetFST], object]  ; """@private"""
    tag_ret: bool  ; """@private"""
    fail_val: object  ; """@private"""

    def __init__(
        self,
        anon_callback: Callable[[_Target], object] | Callable[[_TargetFST], object] = _SENTINEL,
        /,
        tag_ret: bool = False,
        fail_val: object = _SENTINEL,
        **tags,
    ) -> None:
        M.__init__(self, anon_callback, **tags)

        if tag_ret and anon_callback is not _SENTINEL:
            raise ValueError('MCB can never tag the callback return since the callback does not have a tag')

        self.tag_ret = tag_ret
        self.fail_val = fail_val

    def _match(self, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        if not mctx.is_FST or not isinstance(tgt, AST):
            m = self.pat(tgt)
        elif tgt := getattr(tgt, 'f', None):
            m = self.pat(tgt)
        else:
            raise MatchError('match found an AST node without an FST')

        fail_val = self.fail_val

        if (not m if fail_val is _SENTINEL else m == fail_val):
            return None

        if pat_tag := self.pat_tag:
            if self.tag_ret:
                tgt = m

            return {pat_tag: tgt, **self.static_tags}

        return self.static_tags


class MTAG(M):
    """Match previously matched node. Looks through tags of current matches and if found then attempts to match against
    the value of the tag. Meant for matching previously matched nodes but can match anything which can work as a valid
    pattern in a tag however it got there.

    For the sake of sanity and efficiency, does not recurse into lists of `FSTMatch` objects that have already been
    built by quantifier patterns. Can match those tags AS they are being built though.

    **Parameters:**
    - `anon_tag`: If the source tag to match is provided in this then the new matched node is not returned in tags. If
        this is missing then there must be at least one element in `tags` and the first keyword there will be taken to
        be the source tag to match and the name of the new tag to use for the matched node.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`).

    **Examples:**

    >>> MBinOp(M(left='a'), right=MTAG('left')) .match(FST('a + a'))
    <FSTMatch <BinOp ROOT 0,0..0,5> {'left': <Name 0,0..0,1>}>

    >>> MBinOp(M(left='a'), right=MTAG('left')) .match(FST('a + b'))

    The tag must already have been matched, not be in the future.

    >>> MBinOp(MTAG('right'), right=M(right='a')) .match(FST('a + a'))

    Works just fine with quantifier patterns.

    >>> pat = MList([M(first='a'), MSTAR(st=MTAG('first'))])

    >>> pat.match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9> {'first': <Name 0,1..0,2>, 'st': [<FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>

    >>> pat.match(FST('[a, a, a, b]'))

    Can match previously matched multinode items from `Dict`, `MatchMapping` or `arguments`.

    >>> MDict(_all=[M(start=...), ..., MTAG('start')]) .match(FST('{1: a, 1: a}'))
    <FSTMatch <Dict ROOT 0,0..0,12> {'start': <<Dict ROOT 0,0..0,12>._all[:1]>}>
    """

    _requires = 'source tag'  # for printing error message

    pat: str  ; """@private"""  # this is really a source tag name here
    static_tags: Mapping[str, Any]  ; """@private"""

    def __init__(self, anon_tag: str | None = None, /, **tags) -> None:
        M.__init__(self, anon_tag or _SENTINEL, **tags)

        self._validate_tags((self.pat,))
        self._validate_tags(self.static_tags)

    def _match(self, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        if (p := mctx.get_tag(self.pat)) is _SENTINEL:
            return None

        if isinstance(p, fst.FST):
            p = p.a

        m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, mctx)

        if m is None:
            return None

        if pat_tag := self.pat_tag:
            if mctx.is_FST and isinstance(tgt, AST) and not (tgt := getattr(tgt, 'f', None)):
                raise MatchError('match found an AST node without an FST')

            if m:
                return {**m, pat_tag: tgt, **self.static_tags}

            return {pat_tag: tgt, **self.static_tags}

        if m:
            return dict(m, **self.static_tags)

        return self.static_tags


class MN(M):
    """Quantifier pattern. Can only be used on or inside list fields and matches at least `min` and at most `max`
    instances of the given pattern. Since this pattern can match an arbitrary number of actual targets, if there is a
    tag for the matched patterns they are given as a list of matches instead of just one.

    This is the base class for `MSTAR`, `MPLUS`, `MQMARK`, `MMIN` and `MMAX` and can do everything they can with the
    appropriate values for `min` and `max`. Those classes are provided regardless for cleaner pattern structuring.

    This pattern and its specific subclasses are greedy and there is no backtracking done to attempt to make a sequence
    of these match successfully. They are also not nestable, a single level is allowed for or in a list field (any
    number sequential siblings `MN(), MN(), ...`, but no `MN(MN(...))`).

    `MN()` with default `min` and `max` is the same as `MSTAR()`, so if you don't care about cleaner patterns you can
    just use this.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern. Setting this to `...` is the same as not having it present, for easier non-kw specification of
        `min` and `max`, in this case you must provide the pattern in a keyword.
    - `min`: The minimum number of pattern matches needed for a successful match.
    - `max`: The maximum number of pattern matches taken for a successful match. `None` means unbounded.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> MList([MN('a', 1, 2)]) .match(FST('[]'))

    >>> MList([MN('a', 1, 2)]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3>>

    >>> MList([MN('a', 1, 2)]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6>>

    >>> MList([MN('a', 1, 2)]) .match(FST('[a, a, a]'))

    >>> MList([MN('a', 1, 2), ...]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9>>

    >>> pat = MGlobal([..., MN(t='c', min=1, max=2), ...])

    >>> FST('global a, b, c, c, d, e') .match(pat)
    <FSTMatch <Global ROOT 0,0..0,23> {'t': [<FSTMatch 'c'>, <FSTMatch 'c'>]}>

    >>> pat = MList([..., MN(t=MRE('c|d'), min=1, max=3), ...])

    >>> FST('[a, b, c, c, d, c, e]') .match(pat)
    <FSTMatch <List ROOT 0,0..0,21> {'t': [<FSTMatch <Name 0,7..0,8>>, <FSTMatch <Name 0,10..0,11>>, <FSTMatch <Name 0,13..0,14>>]}>

    >>> [m.matched.src for m in _.t]
    ['c', 'c', 'd']
    """

    # This is mostly just a data class, the actual logic for these matches lives in `_match_default()`. The tags for the
    # individual child matches are handled according to if the pattern is passed anonymously or in a tag. The static
    # tags are added once at the end of the arbitrary-length match.

    min: int  ; """@private"""
    max: int  ; """@private"""

    _requires = 'non-wildcard pattern'

    def __init__(self, anon_pat: _Patterns = ..., /, min: int = 0, max: int | None = None, **tags) -> None:
        M.__init__(self, _SENTINEL if anon_pat is ... else anon_pat, **tags)

        if isinstance(self.pat, MN):
            raise ValueError('MN-type quantifier patterns cannot be nested directly within each other')

        if max is None:
            max = 0x7fffffffffffffff

        if min < 0:
            raise ValueError(f'{self.__class__.__qualname__} minimum cannot be negative')
        if max < 0:
            raise ValueError(f'{self.__class__.__qualname__} maximum cannot be negative')
        if max < min:
            raise ValueError(f'{self.__class__.__qualname__} maximum cannot be lower than minimum')

        self.min = min
        self.max = max

    def _match(self, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
        return None  # this should not appear alone outside of list fields


class MSTAR(MN):
    """Star quantifier pattern, zero or more. Matches any number of instances of pattern, including zero. The tagging
    works the same way as `MN` and if returning in a tag a list is still returned with either zero or more `FSTMatch`
    objects.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern. Setting this to `...` is the same as not having it present.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> MList([MSTAR(t='a')]) .match(FST('[]'))
    <FSTMatch <List ROOT 0,0..0,2> {'t': []}>

    >>> MList([MSTAR(t='a')]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> MList([MSTAR(t='a')]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> MList([MSTAR(t='a')]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>
    """

    def __init__(self, anon_pat: _Patterns = ..., /, **tags) -> None:
        MN.__init__(self, anon_pat, **tags)


class MPLUS(MN):
    """Plus quantifier pattern, one or more. Matches one or more instances of pattern. The tagging works the same way as
    `MN` and if returning in a tag a list is still returned with either zero or more `FSTMatch` objects.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern. Setting this to `...` is the same as not having it present.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> MList([MPLUS(t='a')]) .match(FST('[]'))

    >>> MList([MPLUS(t='a')]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> MList([MPLUS(t='a')]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> MList([MPLUS(t='a')]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>
    """

    def __init__(self, anon_pat: _Patterns = ..., /, **tags) -> None:
        MN.__init__(self, anon_pat, 1, **tags)


class MQMARK(MN):
    """Zero or one quantifier pattern. Matches at either zero or exactly one instance of the given pattern. The tagging
    works the same way as `MN` and if returning in a tag a list is still returned with either zero or one `FSTMatch`
    objects.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern. Setting this to `...` is the same as not having it present.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    **Examples:**

    >>> MList([MQMARK('a')]) .match(FST('[]'))
    <FSTMatch <List ROOT 0,0..0,2>>

    >>> MList([MQMARK('a')]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3>>

    >>> MList([MQMARK('a')]) .match(FST('[b]'))

    >>> MList([MQMARK('a')]) .match(FST('[a, a]'))

    >>> MList([MQMARK('a'), ...]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6>>
    """

    def __init__(self, anon_pat: _Patterns = ..., /, **tags) -> None:
        MN.__init__(self, anon_pat, 0, 1, **tags)


class MMIN(MN):
    """Minimum count quantifier pattern. Matches a minimum of `min` instances of pattern. The tagging works the same way
    as `MN` and if returning in a tag a list is still returned with either zero or more `FSTMatch` objects.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern. Setting this to `...` is the same as not having it present.
    - `min`: The minimum number of pattern matches needed for a successful match.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    >>> MList([MMIN(min=2, t='a')]) .match(FST('[]'))

    >>> MList([MMIN(min=2, t='a')]) .match(FST('[a]'))

    >>> MList([MMIN(min=2, t='a')]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> MList([MMIN(min=2, t='a')]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>, <FSTMatch <Name 0,7..0,8>>]}>
    """

    def __init__(self, anon_pat: _Patterns = ..., /, min: int = 0, **tags) -> None:
        MN.__init__(self, anon_pat, min, **tags)


class MMAX(MN):
    """Maximum count quantifier pattern. Matches a maximum of `max` instances of pattern. The tagging works the same way
    as `MN` and if returning in a tag a list is still returned with either zero or more `FSTMatch` objects.

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched nodes tags are all merged in order and
        returned as normal tags, with later match tags overriding earlier if same. If this is missing then there must be
        at least one element in `tags` and the first keyword there will be taken to be the pattern to match. In this
        case the keyword is used as a tag which is used to return a list of `FSTMatch` objects for each node matched by
        the pattern. Setting this to `...` is the same as not having it present.
    - `max`: The maximum number of pattern matches taken for a successful match. `None` means unbounded.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`). These are added AFTER all the child match tags.

    >>> MList([MMAX(max=2, t='a')]) .match(FST('[]'))
    <FSTMatch <List ROOT 0,0..0,2> {'t': []}>

    >>> MList([MMAX(max=2, t='a')]) .match(FST('[a]'))
    <FSTMatch <List ROOT 0,0..0,3> {'t': [<FSTMatch <Name 0,1..0,2>>]}>

    >>> MList([MMAX(max=2, t='a')]) .match(FST('[a, a]'))
    <FSTMatch <List ROOT 0,0..0,6> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>

    >>> MList([MMAX(max=2, t='a')]) .match(FST('[a, a, a]'))

    >>> MList([MMAX(max=2, t='a'), ...]) .match(FST('[a, a, a]'))
    <FSTMatch <List ROOT 0,0..0,9> {'t': [<FSTMatch <Name 0,1..0,2>>, <FSTMatch <Name 0,4..0,5>>]}>
    """

    def __init__(self, anon_pat: _Patterns = ..., /, max: int | None = None, **tags) -> None:
        MN.__init__(self, anon_pat, 0, max, **tags)


# ......................................................................................................................

class _StepbackListIter:
    def __init__(self, seq: list) -> None:
        self.seq = seq
        self.len = len(seq)
        self.idx = -1

    def next(self) -> object:
        if (idx := self.idx + 1) == self.len:
            return _SENTINEL

        self.idx = idx

        return self.seq[idx]

    def stepback(self, n: int = 1) -> None:
        self.idx -= n


def _match_n(
    pat: _Pattern, tgt: _Targets, mctx: _MatchContext, iter_tgt: _StepbackListIter
) -> dict[str, Any] | None:
    """Match a quantifier pattern to a section of list field. If the match fails then the iterator is stepped back the
    whole way."""

    n_max = pat.max
    np = pat.pat
    match_func = _MATCH_FUNCS.get(np.__class__, _match_default)
    tagss = mctx.new_tagss()
    tgts = []
    n = 0

    while n < n_max:
        if (t := iter_tgt.next()) is _SENTINEL:
            break

        if (m := match_func(np, t, mctx)) is None:
            iter_tgt.stepback()

            break

        tagss.append(m)
        tgts.append(t)

        n += 1

    if n < pat.min:
        iter_tgt.stepback(n)

        return mctx.discard_tagss()

    static_tags = pat.static_tags

    if pat_tag := pat.pat_tag:  # returning child match objects in list
        if mctx.is_FST and tgt and not isinstance(tgt[0], str):  # str as in `globals str`, otherwise ASTs with maybe Nones, this basically decides if we need to convert AST to FST nodes
            ms = []

            for ts, t in zip(tagss, tgts, strict=True):
                if t and not isinstance(t, FSTView) and not (t := getattr(t, 'f', None)):
                    raise MatchError('match found an AST node without an FST')  # pragma: no cover  # cannot currently happen due to how lists are handled and checked before getting here

                ms.append(FSTMatch(pat, t, ts))

            tags = {pat_tag: ms, **static_tags}  # pat_tag MUST BE FIRST TAG IN DICT!

        else:
            tags = {pat_tag: [FSTMatch(pat, t, ts) for ts, t in zip(tagss, tgts, strict=True)], **static_tags}  # non-node list field

        mctx.discard_tagss()

    else:  # merging tags from child matches
        if static_tags:
            tagss.append(static_tags)

        tags = mctx.pop_merge_tagss()

    return tags


# ......................................................................................................................

def _match_default(pat: _Patterns, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    """Match the fields of any `M_Pattern`, `AST` or a `str` (either as a primitive value or as source)."""

    if isinstance(pat, list):
        if isinstance(tgt, list):
            pass  # noop

        elif isinstance(tgt, FSTView):
            if not len(tgt):
                tgt = []
            elif isinstance(tgt[0], (str, FSTView)):  # could be Global/Nonlocal.names or multi-node items like Dict/MatchMapping/arguments
                tgt = list(tgt)
            else:
                tgt = [f.a if f else f for f in tgt]  # convert to temporary list of AST nodes

        else:
            return None

        # this is the list field matching where wildcards and quantifier patterns are handled

        tagss = mctx.new_tagss()
        iter_pat = iter(pat)
        iter_tgt = _StepbackListIter(tgt)

        while (p := next(iter_pat, _SENTINEL)) is not _SENTINEL:
            if p is not ...:  # concrete or quantifier
                if isinstance(p, MN): # quantifier
                    if (m := _match_n(p, tgt, mctx, iter_tgt)) is None:
                        return mctx.discard_tagss()

                    tagss.append(m)

                else:  # concrete
                    if (t := iter_tgt.next()) is _SENTINEL:  # if ast list ended before can match then fail
                        return mctx.discard_tagss()

                    m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, mctx)

                    if m is None:  # if not match then fail as this is an expected concrete match
                        return mctx.discard_tagss()
                    if m:
                        tagss.append(m)

                continue

            # wildcard skip

            while (p := next(iter_pat, _SENTINEL)) is not _SENTINEL:
                if p is ...:  # eat any repeated wildcards
                    continue

                break  # found pattern to match against

            else:  # ended on ..., doesn't matter what is left in the ast list, its a match
                break

            # got p to match against, now we walk the target ast list until find a match or not

            if isinstance(p, MN): # quantifier
                while (m := _match_n(p, tgt, mctx, iter_tgt)) is None:
                    if iter_tgt.next() is _SENTINEL:  # advance one unit and try again
                        return mctx.discard_tagss()

                tagss.append(m)

            else:  # concrete
                while (t := iter_tgt.next()) is not _SENTINEL:
                    m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, mctx)

                    if m is None:  # if not match then keep looking (because p preceded by ...)
                        continue
                    if m:
                        tagss.append(m)

                    break

                else:  # ast list ends before being able to make concrete match to concrete p
                    return mctx.discard_tagss()

            continue  # found concrete / concrete match, iterate on to next pattern value

        else:
            if iter_tgt.next() is not _SENTINEL:  # if concrete pattern list ended without ... and there are still elements in the ast list then fail
                return mctx.discard_tagss()

        return mctx.pop_merge_tagss()

    # maybe pattern is a previously matched multinode FSTView (Dict, MatchMapping, arguments)

    if isinstance(pat, FSTView):
        pat = mctx.fstview_as_pat(pat)

        return _MATCH_FUNCS.get(pat.__class__, _match_default)(pat, tgt, mctx)

    # got here through subclass of a primitive type

    if isinstance(pat, str):
        return _match_str(pat, tgt, mctx)

    if isinstance(pat, M_Pattern):
        raise RuntimeError('subclassing M_Pattern not supported')

    return _match_primitive(pat, tgt, mctx)

def _match_str(pat: str, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
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

def _match_primitive(pat: constant, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
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

def _match_node(pat: M_Pattern | AST, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    """`M_Pattern` or `AST` leaf node."""

    is_mpat = isinstance(pat, M_Pattern)
    types = pat._types if is_mpat else pat.__class__

    if not isinstance(tgt, types):
        return None

    tagss = mctx.new_tagss()

    for field in pat._fields:
        p = getattr(pat, field, ...)

        if p is ...:  # ellipsis handled here without dispatching for various reasons
            continue

        t = getattr(tgt, field, _SENTINEL)  # _SENTINEL for arbitrary fields, but also field may not exist in target because pattern may have fields from a greater python version than we are running

        if t is _SENTINEL:
            if not (f := getattr(tgt, 'f', None)) or not isinstance(t := getattr(f, field, None), FSTView):  # maybe its a virtual field
                return mctx.discard_tagss()

        elif mctx.is_FST and isinstance(t, list):
            t = getattr(tgt.f, field)  # get the FSTView instead (for maybe capture to tag, is converted back to list of AST for compare)

        m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, t, mctx)

        if m is None:
            return mctx.discard_tagss()
        if m:
            tagss.append(m)

    return mctx.pop_merge_tagss()

def _match_node_Dict(pat: Dict | MDict, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    """`Dict` or `MDict` leaf node. Possibly match against a single-item `FSTView_Dict`."""

    if not isinstance(tgt, FSTView_Dict):
        return _match_node(pat, tgt, mctx)

    if len(tgt) != 1:
        return None

    key = getattr(pat, 'keys', ...)

    if isinstance(key, list):
        if len(key) != 1:
            raise MatchError('matching a Dict pattern against Dict._all the pattern keys must be a single element or length-1 list')
        else:
            key = key[0]

    value = getattr(pat, 'values', ...)

    if isinstance(value, list):
        if len(value) != 1:
            raise MatchError('matching a Dict pattern against Dict._all the pattern values must be a single element or length-1 list')
        else:
            value = value[0]

    idx = tgt.start
    tgt = tgt.base.a

    if (mk := _MATCH_FUNCS.get(key.__class__, _match_default)(key, tgt.keys[idx], mctx)) is None:
        return None

    if (mv := _MATCH_FUNCS.get(value.__class__, _match_default)(value, tgt.values[idx], mctx)) is None:
        return None

    if not mk:
        return mv
    if not mv:
        return mk

    return {**mk, **mv}

def _match_node_MatchMapping(
    pat: MatchMapping | MMatchMapping, tgt: _Targets, mctx: _MatchContext
) -> Mapping[str, Any] | None:
    """`MatchMapping` or `MMatchMapping` leaf node. Possibly match against a single-item `FSTView_MatchMapping`. Need to
    do more than `Dict` here to handle possible `**rest` element."""

    if not isinstance(tgt, FSTView_MatchMapping):
        return _match_node(pat, tgt, mctx)

    if len(tgt) != 1:
        return None

    rest = getattr(pat, 'rest', None)
    key = getattr(pat, 'keys', ...)
    pattern = getattr(pat, 'patterns', ...)

    if rest is not None:  # matching against just **rest
        if not (
            (key is ... or (not key and isinstance(key, list)))
            and (pattern is ... or (not pattern and isinstance(pattern, list)))
        ):
            raise MatchError('matching a MatchMapping rest against MatchMapping._all'
                             ' the pattern keys and patterns must be ... or empty lists')

        if not tgt.has_rest:
            return None

        return _MATCH_FUNCS.get(rest.__class__, _match_default)(rest, tgt.base.a.rest, mctx)

    if isinstance(key, list):
        if len(key) != 1:
            raise MatchError('matching a MatchMapping pattern against MatchMapping._all'
                             ' the pattern keys must be a single element or length-1 list')
        else:
            key = key[0]

    if isinstance(pattern, list):
        if len(pattern) != 1:
            raise MatchError('matching a MatchMapping pattern against MatchMapping._all'
                             ' the pattern patterns must be a single element or length-1 list')
        else:
            pattern = pattern[0]

    if tgt.has_rest:  # if want to match a rest then we force user to do it explicitly on purpose since it is too different from regular nodes
        return None

    idx = tgt.start
    tgt = tgt.base.a

    if (mk := _MATCH_FUNCS.get(key.__class__, _match_default)(key, tgt.keys[idx], mctx)) is None:
        return None

    if (mp := _MATCH_FUNCS.get(pattern.__class__, _match_default)(pattern, tgt.patterns[idx], mctx)) is None:
        return None

    if not mk:
        return mp
    if not mp:
        return mk

    return {**mk, **mp}

def _match_node_arguments(pat: arguments | Marguments, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    """`arguments` or `Marguments` leaf node. Possibly match against a single-item `FSTView_arguments`. Will match a
    single argument with possibly a default to a single-argument `FSTView_arguments`. Pattern `args` argument matches
    to target `args`, `posonlyargs` or `kwonlyargs`. Other type pattern args must match exactly (`posonlyargs` only to
    `posonlyargs`, `kwonlyargs` to `kwonlyargs`, `varag` to `vararg` and `kwarg` to `kwarg` (obviously), etc...)."""

    if not isinstance(tgt, FSTView_arguments):
        return _match_node(pat, tgt, mctx)


    raise NotImplementedError

    if len(tgt) != 1:
        return None

    arg_pat = None
    dflt_pat = None
    args = getattr(pat, 'args', ...)

    if isinstance(args, list):
        if len(key) != 1:
            raise MatchError('matching a arguments pattern against arguments._all'
                             ' the pattern must be a single argument')
        else:
            key = key[0]








    key = getattr(pat, 'keys', ...)

    if isinstance(key, list):
        if len(key) != 1:
            raise MatchError('matching a arguments pattern against arguments._all the pattern keys must be a single element or length-1 list')
        else:
            key = key[0]

    value = getattr(pat, 'values', ...)

    if isinstance(value, list):
        if len(value) != 1:
            raise MatchError('matching a arguments pattern against arguments._all the pattern values must be a single element or length-1 list')
        else:
            value = value[0]

    idx = tgt.start
    tgt = tgt.base.a

    if (mk := _MATCH_FUNCS.get(key.__class__, _match_default)(key, tgt.keys[idx], mctx)) is None:
        return None

    if (mv := _MATCH_FUNCS.get(value.__class__, _match_default)(value, tgt.values[idx], mctx)) is None:
        return None

    if not mk:
        return mv
    if not mv:
        return mk

    return {**mk, **mv}

def _match_node_Constant(pat: MConstant | Constant, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    """We do a special handler for `Constant` so we can check for a real `Ellipsis` instead of having that work as a
    wildcarcd. We do a standalone handler so don't have to have the check in general."""

    if not isinstance(tgt, Constant):
        return None

    if (p := getattr(pat, 'value', _SENTINEL)) is not _SENTINEL:  # missing value acts as implicit ... wildcard, while the real ... is a concrete value here
        match_func = _match_primitive if p is ... else _MATCH_FUNCS.get(p.__class__, _match_default)

        if (mv := match_func(p, tgt.value, mctx)) is None:
            return None
    else:
        mv = None

    if (p := getattr(pat, 'kind', ...)) is not ...:
        if (mk := _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt.kind, mctx)) is None:
            return None
    else:
        return mv

    if not mv:
        return mk

    return {**mv, **mk}

def _match_node_expr_context(pat: Load | Store | Del, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    """This exists as a convenience so that an `AST` pattern `Load`, `Store` and `Del` always match each other unless
    the match option `ast_ctx=True`. `MLoad`, `MStore` and `MDel` don't get here, they always do a match check. A pattern
    `None` must also match one of these successfully for py < 3.13."""

    if not isinstance(tgt, expr_context) or (mctx.ast_ctx and tgt.__class__ is not pat.__class__):
        return None

    return _EMPTY_DICT

def _match_type(pat: type, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    """Just match the `AST` type (or equivalent `MAST` type)."""

    if issubclass(pat, M_Pattern):
        pat = pat._types

    if not isinstance(tgt, pat):
        return None

    return _EMPTY_DICT

def _match_re_Pattern(
    pat: re_Pattern, tgt: _Targets, mctx: _MatchContext, re_func: Callable | None = None
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

def _match_Ellipsis(pat: EllipsisType, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    """Always succeeds."""

    return _EMPTY_DICT

def _match_None(pat: NoneType, tgt: _Targets, mctx: _MatchContext) -> Mapping[str, Any] | None:
    if tgt is not None:
        return None

    return _EMPTY_DICT

_MATCH_FUNCS = {
    M:                   M._match,
    MNOT:                MNOT._match,
    MOR:                 MOR._match,
    MAND:                MAND._match,
    MANY:                _match_node,  # _match_node_arbitrary_fields,
    MOPT:                MOPT._match,
    MRE:                 MRE._match,
    MCB:                 MCB._match,
    MTAG:                MTAG._match,
    MN:                  MN._match,
    MSTAR:               MSTAR._match,
    MPLUS:               MPLUS._match,
    MQMARK:              MQMARK._match,
    MMIN:                MMIN._match,
    MMAX:                MMAX._match,
    AST:                 _match_node,  # _match_node_nonleaf,
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
    Dict:                _match_node_Dict,
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
    MatchMapping:        _match_node_MatchMapping,
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
    arguments:           _match_node_arguments,
    boolop:              _match_node,
    cmpop:               _match_node,
    comprehension:       _match_node,
    excepthandler:       _match_node,  # _match_node_nonleaf,
    expr:                _match_node,  # _match_node_nonleaf,
    expr_context:        _match_node,  # _match_node_nonleaf,
    keyword:             _match_node,
    match_case:          _match_node,
    mod:                 _match_node,  # _match_node_nonleaf,
    operator:            _match_node,
    pattern:             _match_node,  # _match_node_nonleaf,
    stmt:                _match_node,  # _match_node_nonleaf,
    type_ignore:         _match_node,  # _match_node_nonleaf,
    unaryop:             _match_node,
    withitem:            _match_node,
    TryStar:             _match_node,
    TypeAlias:           _match_node,
    type_param:          _match_node,  # _match_node_nonleaf,
    TypeVar:             _match_node,
    ParamSpec:           _match_node,
    TypeVarTuple:        _match_node,
    TemplateStr:         _match_node,
    Interpolation:       _match_node,
    _slice:              _match_node,  # _match_node_nonleaf,
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
    MAST:                _match_node,  # _match_node_arbitrary_fields,
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
    MDict:               _match_node_Dict,
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
    MMatchMapping:       _match_node_MatchMapping,
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
    Marguments:          _match_node_arguments,
    Mboolop:             _match_node,
    Mcmpop:              _match_node,
    Mcomprehension:      _match_node,
    Mexcepthandler:      _match_node,  # _match_node_arbitrary_fields,
    Mexpr:               _match_node,  # _match_node_arbitrary_fields,
    Mexpr_context:       _match_node,  # _match_node_arbitrary_fields,
    Mkeyword:            _match_node,
    Mmatch_case:         _match_node,
    Mmod:                _match_node,  # _match_node_arbitrary_fields,
    Moperator:           _match_node,
    Mpattern:            _match_node,  # _match_node_arbitrary_fields,
    Mstmt:               _match_node,  # _match_node_arbitrary_fields,
    Mtype_ignore:        _match_node,  # _match_node_arbitrary_fields,
    Munaryop:            _match_node,
    Mwithitem:           _match_node,
    MTryStar:            _match_node,
    MTypeAlias:          _match_node,
    Mtype_param:         _match_node,  # _match_node_arbitrary_fields,
    MTypeVar:            _match_node,
    MParamSpec:          _match_node,
    MTypeVarTuple:       _match_node,
    MTemplateStr:        _match_node,
    MInterpolation:      _match_node,
    M_slice:             _match_node,  # _match_node_arbitrary_fields,
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


# ......................................................................................................................
# get all leaf AST types that can possibly match a given _Pattern

def _leaf_asts_default(pat: _Pattern) -> tp_Set[type[AST]]:
    if isinstance(pat, M_Pattern):
        return AST2ASTSLEAF[pat._types]  # will be a single type here

    if isinstance(pat, AST):
        return AST2ASTSLEAF[pat.__class__]

    if isinstance(pat, str):  # gets here from a subclassed str
        return ASTS_LEAF__ALL

    return _EMPTY_SET  # from some subclassed primitive

def _leaf_asts_all(pat: _Pattern) -> tp_Set[type[AST]]:
    return ASTS_LEAF__ALL

def _leaf_asts_none(pat: _Pattern) -> tp_Set[type[AST]]:
    return _EMPTY_SET

def _leaf_asts_type(pat: type) -> tp_Set[type[AST]]:
    if issubclass(pat, M_Pattern):
        pat = pat._types  # guaranteed to be single element here

    return AST2ASTSLEAF[pat]

_LEAF_ASTS_FUNCS = {
    M:            M._leaf_asts,
    MNOT:         MNOT._leaf_asts,
    MOR:          MOR._leaf_asts,
    MAND:         MAND._leaf_asts,
    MANY:         MANY._leaf_asts,
    MRE:          _leaf_asts_all,
    MCB:          _leaf_asts_all,
    MTAG:         _leaf_asts_all,
    type:         _leaf_asts_type,
    re_Pattern:   _leaf_asts_all,
    EllipsisType: _leaf_asts_all,
    int:          _leaf_asts_none,
    float:        _leaf_asts_none,
    complex:      _leaf_asts_none,
    str:          _leaf_asts_all,  # because this can match source
    bytes:        _leaf_asts_none,
    bool:         _leaf_asts_none,
    NoneType:     _leaf_asts_none,
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
    fields. The `...` are wildcards.

    >>> pat = MCall(
    ...    func=Attribute(Name('logger'), 'info'),
    ...    keywords=[..., M(cid_kw=Mkeyword('cid')), ...]
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

    >>> FST('node_cls is zst.ZST') .match(pat)
    <FSTMatch <Compare ROOT 0,0..0,19> {'is_name': True, 'obj': <Name 0,0..0,8>, 'is_is': <Is 0,9..0,11>}>

    >>> FST('node_cls_bad is zst.ZST') .match(pat)
    """

    m = _MATCH_FUNCS.get(pat.__class__, _match_default)(pat, self.a, _MatchContext(True, ast_ctx))

    return None if m is None else FSTMatch(pat, self, m)


def search(
    self: fst.FST,
    pat: _Pattern,
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

    This function returns the `walk()` generator which can be interacted with in the same way as the standard one.
    Meaning you can control the recursion into children by sending `True` or `False` to this generator. Replacement and
    deletion of nodes during the walk is allowed according to the rules specified by `walk()`.

    If you do not replace, delete or `send(False)` for any given node then the search will continue into that node with
    the possibility of finding nested matches.

    **Note:** Yhe generator returned by this function does not yield the matched nodes themselves, but rather the match
    objects. You can get the matched nodes from these objects using the `fst` attribute, e.g. `match.fst`.

    **Parameters:**
    - `pat`: The pattern to search for. Must resolve to a node, not a primitive or list (node patterns, type, wildcard,
        functional patterns of these). Because you're matching against nodes, otherwise nothing will match.
    - `ast_ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
        Defaults to `False` because when creating `AST` nodes the `ctx` field may be created automatically if you
        don't specify it so may inadvertantly break matches where you don't want to take that into consideration.
        Will always check `ctx` field for `MAST` patterns because there it is well behaved and if not specified
        is set to wildcard.
    - `self_`, `recurse`, `scope`, `back`, `asts`: These are parameters for the underlying `walk()` function. See that
        function for their meanings.

    **Returns:**
    - `Generator`: This is a `walk()` generator set up for matching. You can interact with this generator in the same
        way as a normal walk generator in that you can send `True` or `False` to control recursion into child nodes.

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
    asts_leaf = _LEAF_ASTS_FUNCS.get(pat_cls, _leaf_asts_default)(pat)
    match_func = _MATCH_FUNCS.get(pat_cls, _match_default)
    mctx = _MatchContext(True, ast_ctx)

    if len(asts_leaf) == _LEN_ASTS_LEAF__ALL:  # need to check all nodes
        def all_func(f: fst.FST) -> FSTMatch | Literal[False]:
            mctx.clear()

            m = match_func(pat, f.a, mctx)

            return False if m is None else FSTMatch(pat, f, m)

    else:
        def all_func(f: fst.FST) -> FSTMatch | Literal[False]:
            if f.a.__class__ not in asts_leaf:
                return False

            mctx.clear()

            m = match_func(pat, f.a, mctx)

            return False if m is None else FSTMatch(pat, f, m)

    return self.walk(all_func, self_=self_, recurse=recurse, scope=scope, back=back, asts=asts)


def sub(
    self: fst.FST,
    pat: _Pattern,
    repl: Code | Callable[[FSTMatch], Code],
    nested: bool = False,
    *,
    ast_ctx: bool = False,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
    asts: list[AST] | None = None,
    **options,
) -> fst.FST:  # -> self
    """Substitute matching targets with a given `repl` template or dynamically generated node if `repl` is a function.
    The template substitutions can include tagged elements from a match.

    TODO: unfinished, document

    **Parameters:**
    - `pat`: The pattern to search for. Must resolve to a node, not a primitive or list (node patterns, type, wildcard,
        functional patterns of these). Because you're matching against nodes, otherwise nothing will match.
    - `repl`: Replacement template or function to generate replacement nodes.
    - `nested: Whether to allow recursion into nested substitutions or not. Allowing this can cause infinite recursion
        due to replacement with things that match the pattern, so don't use unless you are sure this can not happen.
        Regardless of this setting, when using a template `repl` this function will never recurse into full matched
        target substitutions (`__fst_`).
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
    ...    keywords=MNOT([..., Mkeyword('cid'), ...]),
    ...    _args=M(all_args=...),
    ... )

    >>> repl = '__fst_func(__fst_all_args, cid=CID)'

    >>> print(FST(src).sub(pat, repl).src)
    logger.info('Hello world...', cid=CID)  # ok
    logger.info('Already have id', cid=other_cid)  # ok
    logger.info(cid=CID)  # yes, no logger message, too bad
    (logger).info(
                  f'not a {thing}',  # this is fine
                  extra=extra,       # also this
                  cid=CID)
    """

    global __DIRTY

    check_options(options)

    gen = self.search(pat, ast_ctx=ast_ctx, self_=self_, recurse=recurse, scope=scope, back=back, asts=asts)

    if callable(repl):  # user function, very simple, just do its own loop
        for m in gen:
            tgt = m.matched  # will be FST node
            sub = repl(m)

            # TODO: user nested control, True, False or don't send anything

            if sub is not tgt:
                tgt.replace(sub, **options)

            if not nested:
                gen.send(False)

        return

    # template substitution, now it gets fun

    repl = code_as_all(repl, options, self.root.parse_params)
    paths = []  # [(tag, child_path), ...]  an empty string tag means replace with the node matched

    for f in repl.walk({Name, arg}):
        if (a := f.a).__class__ is Name:
            n = a.id
        else:  # a.__class__ is arg, it makes more sense to replace the whole arg, annotation included, rather than just the name
            n = a.arg

        if n.startswith('__fst_'):
            paths.append((n[6:], repl.child_path(f)))

    dirty = __DIRTY = (__DIRTY + 1) & 0x7fffffffffffffff
    dirties = []

    try:
        for m in gen:
            tgt = m.matched  # will be FST node

            if getattr(tgt.a, '__DIRTY', None) is dirty:
                gen.send(False)

                continue

            sub = repl.copy()

            for tag, path in paths:
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

                elif not isinstance(sub_sub, (str, AST)):
                    raise MatchError(f'match substitution must be FST, AST or str, got {sub_sub}')

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
                                        (a := f.a).__DIRTY = dirty

                                        dirties.append(a)

                        continue

                f = sub_tgt.replace(sub_sub, one=one, **options)

                if not tag and f:  # replaced with original whole matched element, mark as dirty
                    (a := f.a).__DIRTY = dirty

                    dirties.append(a)

            tgt = tgt.replace(sub, **options)

            if tgt and getattr(tgt.a, '__DIRTY', None) is dirty:  # substituted node with same node `__fst_`?
                gen.send(False)

                continue

            if not nested:
                gen.send(False)

    finally:
        for a in dirties:  # clean up after ourselves
            del a.__DIRTY

    return self
