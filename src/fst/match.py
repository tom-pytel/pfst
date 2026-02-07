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
from .view import fstview

__all__ = [
    'MatchError',
    'M_Match',
    'M_Pattern',

    'M',
    'MNOT',
    'MOR',
    'MAND',
    'MANY',
    'MRE',
    'MCB',

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

_Target = AST | constant
_Targets = fstview | list[_Target] | _Target  # `str` and `None` also have special meaning outside of constant, str is identifier and None may be a missing optional AST (or other type)

_Pattern = Union[_Target, type[Union['M_Pattern', AST]], 'M_Pattern', re_Pattern, EllipsisType]  # `str` here may also be a match for target node source, not just a primitive
_Patterns = list[_Pattern] | _Pattern


def _rpr(o: object) -> str:
    o_cls = o.__class__

    return (
        '...'
        if o is ... else
        o.__name__
        if o_cls is type and issubclass(o, (AST, M_Pattern)) else
        f'{o_cls.__name__}({", ".join(f"{f}={_rpr(getattr(o, f, None))}" for f in o._fields if f != "ctx")})'
        if isinstance(o, AST) else
        f'[{", ".join(_rpr(e) for e in o)}]'
        if isinstance(o, list) else
        repr(o)
    )


class MatchError(RuntimeError):
    """An error during matching."""


class M_Match:
    """Successful match object. Can look up tags directly on this object as attributes (as long as the name doesnt't
    collide with a name that already exists). Nonexistent tags will not raise but return a falsey `M_Match.NoTag`."""

    tags: Mapping[str, Any]  ; """Full match tags dictionary. Only successful matches get their tags included."""
    pattern: _Pattern  ; """The pattern used for the match. Can be any valid pattern including `AST` node, primitive values, compiled `re.Pattern`, etc..."""
    target: _Targets  ; """What was matched. Does not have to be a node as list and primitive matches can be tagged. Also possibly arbitrary return values from `MCB` callbacks."""
    fst: fst.FST | None  ; """If the matched target is an `AST` node and it has an `FST` node then this is it."""

    class _NoTag:  # so that we can check value of any tag without needing to check if it exists first
        __slots__ = ()

        def __new__(cls) -> M_Match._NoTag:
            return M_Match.NoTag

        def __bool__(self) -> bool:
            return False

        def __repr__(self) -> str:
            return 'M_Match.NoTag'

    NoTag = object.__new__(_NoTag)  ; """A falsey object returned if accessing a non-existent tag on the `M_Match` object as an attribute. Can check for existence of tag using `match.tag is match.NoTag`"""

    def __init__(self, tags: Mapping[str, Any], pattern: _Pattern, target: _Target) -> None:
        self.tags = MappingProxyType(tags)
        self.pattern = pattern
        self.target = target
        self.fst = f if isinstance(target, AST) and (f := getattr(target, 'f', None)) else None

    def __repr__(self) -> str:
        return f'<M_Match {{{", ".join(f"{k!r}: {_rpr(v)}" for k, v in self.tags.items())}}}>'

    def __getattr__(self, name: str) -> object:
        if (v := self.tags.get(name, _SENTINEL)) is not _SENTINEL:
            return v

        if not name.startswith('__'):
            return self.NoTag

        raise AttributeError(name)  # nonexistence of dunders should not be masked

    def get(self, tag: str, default: object = None, /) -> object:
        """A `dict.get()` function for the match tags. Just a shortcut for `match.tags.get(tag, default)`."""

        return self.tags.get(tag, default)


class M_Pattern:
    """The base class for all non-primitive match patterns. The two main classes being `MAST` node matchers and the
    functional matchers like `MOR` and `MRE`."""

    _fields: tuple[str] = ()  # these AST attributes are here so that non-AST patterns like MOR and MF can work against ASTs, they can be overridden on a per-instance basis
    _types: type[AST] | tuple[type[AST]] = AST  # only the MANY pattern has a tuple here

    def match(self, tgt: _Targets | fst.FST, *, ctx: bool = False) -> M_Match | None:
        """Match this pattern against given target. This can take `FST` nodes or `AST` (whether they are part of an
        `FST` tree or not, meaning it can match against pure `AST` trees). Can also match primitives and lists of nodes
        if the pattern is set up for that.

        **Parameters:**
        - `tgt`: The target to match. Can be an `AST` or `FST` node or constant or a list of `AST` nodes or constants.
        - `ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
            Defaults to `False` because when creating `AST` nodes the `ctx` field may be created automatically if you
            don't specify it so may inadvertantly break matches where you don't want to take that into consideration.
            Will always check `ctx` field for `MAST` patterns because there it is well behaved and if not specified
            is set to wildcard.

        **Returns:**
        - `M_Match`: The match object on successful match.
        - `None`: Did not match.
        """

        if isinstance(tgt, fst.FST):
            if not (tgt := tgt.a):
                raise ValueError(f'{self.__class__.__qualname__}.match() got a dead FST node')

        m = _MATCH_FUNCS.get(self.__class__, _match_default)(self, tgt, dict(ctx=ctx))

        return None if m is None else M_Match(m, self, tgt)


class MAST(M_Pattern):
    """This class (and its non-leaf subclasses like `Mstmt` and `Mexpr`) can be used as an arbitrary field(s) pattern.
    Can match one or more fields (list or not, without list type errors), as long as the type matches (e.g. an `Assign`
    matches an `Mstmt` but not an `Mexpr`). This arbitrary field matching behavior is unique to non-leaf `AST` types,
    concrete types like `MAssign` always have fixed fields.

    **Note:** Since there are several fields which can be either an individual element or list of elements, usage of
    arbitrary fields in this node does not raise an error on list vs. non-list mismatch and instead just considers it a
    non-match.

    **Parameters:**
    - `fields`: If provided then is an arbitrary list of fields to match. Otherwise will just match based on type.

    **Examples:**

    Will match any `AST` node which has a `value` which is a `Call`. So will match `return f()`,
    `await something(a, b, c)` and just an `Expr` `call(args)`, but not `yield x` or `*(a, b, c)`.

    >>> pat = MAST(value=Call)

    >>> pat.match(FST('return f()'))
    <M_Match {}>

    >>> pat.match(FST('await something(a, b, c)'))
    <M_Match {}>

    >>> pat.match(FST('call(args)', Expr))
    <M_Match {}>

    >>> pat.match(FST('yield x'))

    >>> pat.match(FST('*(a, b, c)'))

    Will match any statement which has a `Constant` string as the first element of its body, in other words a docstring.

    >>> pat = Mstmt(body=[Expr(MConstant(str)), ...])

    >>> pat.match(FST('def f(): "docstr"; pass'))
    <M_Match {}>

    >>> pat.match(FST('class cls: "docstr"'))
    <M_Match {}>

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

class MModule(MAST):
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

class MInteractive(MAST):
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

class MExpression(MAST):
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

class MFunctionType(MAST):
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

class MFunctionDef(MAST):
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
        _args: _Patterns = ...,
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

        if _args is not ...:
            self._args = _args
            fields.append('_args')

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MAsyncFunctionDef(MAST):
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
        _args: _Patterns = ...,
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

        if _args is not ...:
            self._args = _args
            fields.append('_args')

        if _body is not ...:
            self._body = _body
            fields.append('_body')

class MClassDef(MAST):
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

class MReturn(MAST):
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

class MDelete(MAST):
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

class MAssign(MAST):
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

class MTypeAlias(MAST):
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

class MAugAssign(MAST):
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

class MAnnAssign(MAST):
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

class MFor(MAST):
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

class MAsyncFor(MAST):
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

class MWhile(MAST):
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

class MIf(MAST):
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

class MWith(MAST):
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

class MAsyncWith(MAST):
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

class MMatch(MAST):
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

class MRaise(MAST):
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

class MTry(MAST):
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

class MTryStar(MAST):
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

class MAssert(MAST):
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

class MImport(MAST):
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

class MImportFrom(MAST):
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

class MGlobal(MAST):
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

class MNonlocal(MAST):
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

class MExpr(MAST):
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

class MPass(MAST):
    """"""
    _types = Pass

    def __init__(self) -> None:
        pass

class MBreak(MAST):
    """"""
    _types = Break

    def __init__(self) -> None:
        pass

class MContinue(MAST):
    """"""
    _types = Continue

    def __init__(self) -> None:
        pass

class MBoolOp(MAST):
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

class MNamedExpr(MAST):
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

class MBinOp(MAST):
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

class MUnaryOp(MAST):
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

class MLambda(MAST):
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

class MIfExp(MAST):
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

class MDict(MAST):
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

class MSet(MAST):
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

class MListComp(MAST):
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

class MSetComp(MAST):
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

class MDictComp(MAST):
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

class MGeneratorExp(MAST):
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

class MAwait(MAST):
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

class MYield(MAST):
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

class MYieldFrom(MAST):
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

class MCompare(MAST):
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

class MCall(MAST):
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

class MFormattedValue(MAST):
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

class MInterpolation(MAST):
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

class MJoinedStr(MAST):
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

class MTemplateStr(MAST):
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

class MConstant(MAST):
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

class MAttribute(MAST):
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

class MSubscript(MAST):
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

class MStarred(MAST):
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

class MName(MAST):
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

class MList(MAST):
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

class MTuple(MAST):
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

class MSlice(MAST):
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

class MLoad(MAST):
    """"""
    _types = Load

    def __init__(self) -> None:
        pass

class MStore(MAST):
    """"""
    _types = Store

    def __init__(self) -> None:
        pass

class MDel(MAST):
    """"""
    _types = Del

    def __init__(self) -> None:
        pass

class MAnd(MAST):
    """"""
    _types = And

    def __init__(self) -> None:
        pass

class MOr(MAST):
    """"""
    _types = Or

    def __init__(self) -> None:
        pass

class MAdd(MAST):
    """"""
    _types = Add

    def __init__(self) -> None:
        pass

class MSub(MAST):
    """"""
    _types = Sub

    def __init__(self) -> None:
        pass

class MMult(MAST):
    """"""
    _types = Mult

    def __init__(self) -> None:
        pass

class MMatMult(MAST):
    """"""
    _types = MatMult

    def __init__(self) -> None:
        pass

class MDiv(MAST):
    """"""
    _types = Div

    def __init__(self) -> None:
        pass

class MMod(MAST):
    """"""
    _types = Mod

    def __init__(self) -> None:
        pass

class MPow(MAST):
    """"""
    _types = Pow

    def __init__(self) -> None:
        pass

class MLShift(MAST):
    """"""
    _types = LShift

    def __init__(self) -> None:
        pass

class MRShift(MAST):
    """"""
    _types = RShift

    def __init__(self) -> None:
        pass

class MBitOr(MAST):
    """"""
    _types = BitOr

    def __init__(self) -> None:
        pass

class MBitXor(MAST):
    """"""
    _types = BitXor

    def __init__(self) -> None:
        pass

class MBitAnd(MAST):
    """"""
    _types = BitAnd

    def __init__(self) -> None:
        pass

class MFloorDiv(MAST):
    """"""
    _types = FloorDiv

    def __init__(self) -> None:
        pass

class MInvert(MAST):
    """"""
    _types = Invert

    def __init__(self) -> None:
        pass

class MNot(MAST):
    """"""
    _types = Not

    def __init__(self) -> None:
        pass

class MUAdd(MAST):
    """"""
    _types = UAdd

    def __init__(self) -> None:
        pass

class MUSub(MAST):
    """"""
    _types = USub

    def __init__(self) -> None:
        pass

class MEq(MAST):
    """"""
    _types = Eq

    def __init__(self) -> None:
        pass

class MNotEq(MAST):
    """"""
    _types = NotEq

    def __init__(self) -> None:
        pass

class MLt(MAST):
    """"""
    _types = Lt

    def __init__(self) -> None:
        pass

class MLtE(MAST):
    """"""
    _types = LtE

    def __init__(self) -> None:
        pass

class MGt(MAST):
    """"""
    _types = Gt

    def __init__(self) -> None:
        pass

class MGtE(MAST):
    """"""
    _types = GtE

    def __init__(self) -> None:
        pass

class MIs(MAST):
    """"""
    _types = Is

    def __init__(self) -> None:
        pass

class MIsNot(MAST):
    """"""
    _types = IsNot

    def __init__(self) -> None:
        pass

class MIn(MAST):
    """"""
    _types = In

    def __init__(self) -> None:
        pass

class MNotIn(MAST):
    """"""
    _types = NotIn

    def __init__(self) -> None:
        pass

class Mcomprehension(MAST):
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

class MExceptHandler(MAST):
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

class Marguments(MAST):
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

class Marg(MAST):
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

class Mkeyword(MAST):
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

class Malias(MAST):
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

class Mwithitem(MAST):
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

class Mmatch_case(MAST):
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

class MMatchValue(MAST):
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

class MMatchSingleton(MAST):
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

class MMatchSequence(MAST):
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

class MMatchMapping(MAST):
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

class MMatchClass(MAST):
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

class MMatchStar(MAST):
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

class MMatchAs(MAST):
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

class MMatchOr(MAST):
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

class MTypeIgnore(MAST):
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

class MTypeVar(MAST):
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

class MParamSpec(MAST):
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

class MTypeVarTuple(MAST):
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

class M_ExceptHandlers(MAST):
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

class M_match_cases(MAST):
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

class M_Assign_targets(MAST):
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

class M_decorator_list(MAST):
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

class M_arglikes(MAST):
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

class M_comprehensions(MAST):
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

class M_comprehension_ifs(MAST):
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

class M_aliases(MAST):
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

class M_withitems(MAST):
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

class M_type_params(MAST):
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

class Mmod(MAST):
    """"""
    _types = mod

class Mstmt(MAST):
    """"""
    _types = stmt

class Mexpr(MAST):
    """"""
    _types = expr

class Mexpr_context(MAST):
    """"""
    _types = expr_context

class Mboolop(MAST):
    """"""
    _types = boolop

class Moperator(MAST):
    """"""
    _types = operator

class Munaryop(MAST):
    """"""
    _types = unaryop

class Mcmpop(MAST):
    """"""
    _types = cmpop

class Mexcepthandler(MAST):
    """"""
    _types = excepthandler

class Mpattern(MAST):
    """"""
    _types = pattern

class Mtype_ignore(MAST):
    """"""
    _types = type_ignore

class Mtype_param(MAST):
    """"""
    _types = type_param

class M_slice(MAST):
    """"""
    _types = _slice


# ......................................................................................................................

class M(M_Pattern):
    """Tagging pattern container. If the given pattern matches then tags specified here will be returned in the
    `M_Match` result object. The tags can be static values but also the matched `AST` node can be returned in a given
    tag if the pattern is passed as a keyword parameter (the first one).

    **Parameters:**
    - `anon_pat`: If the pattern to match is provided in this then the matched `AST` is not returned in tags. If this is
        missing then there must be at least one element in `tags` and the first keyword there will be taken to be the
        pattern to match and the name of the tag to use for the matched `AST`.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_pat`).

    **Returns:**
    - `M_Match`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    >>> M('var') .match(Name(id='NOT_VAR'))

    >>> M('var') .match(Name(id='var'))
    <M_Match {}>

    >>> M('var', tag='static') .match(Name(id='var'))
    <M_Match {'tag': 'static'}>

    >>> M(node='var', tag='static') .match(Name(id='var'))
    <M_Match {'node': Name(id='var'), 'tag': 'static'}>

    >>> M(M(M(node='var'), add1=1), add2=2) .match(Name(id='var'))
    <M_Match {'node': Name(id='var'), 'add1': 1, 'add2': 2}>
    """

    _requires = 'pattern'  # for printing error message

    pat: _Patterns  ; """@private"""
    pat_tag: str | None  ; """@private"""
    static_tags: Mapping[str, Any]  ; """@private"""

    def __init__(self, anon_pat: _Patterns = _SENTINEL, /, **tags) -> None:
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

    @staticmethod
    def _match(self: M, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
        m = _MATCH_FUNCS.get((p := self.pat).__class__, _match_default)(p, tgt, moptions)

        if m is None:
            return None

        if pat_tag := self.pat_tag:
            if m:
                return {**m, pat_tag: tgt, **self.static_tags}

            return {pat_tag: tgt, **self.static_tags}

        if m:
            return dict(m, **self.static_tags)

        return self.static_tags

    @staticmethod
    def _leaf_asts(self: M) -> tp_Set[type[AST]]:
        return _LEAF_ASTS_FUNCS.get((p := self.pat).__class__, _leaf_asts_default)(p)


class MNOT(M):
    """Tagging NOT logic pattern container. If the given pattern **DOES NOT** match then tags specified here will be
    returned in the `M_Match` result object. The tags can be specified with static values but also the unmatched `AST`
    node can be returned in a given tag name.

    Any tags that were being propagated up from successful matches are discarded since that constitutes an unsuccessful
    match for this node. And any unsuccessful matches were not propagating any tags up anyway. So this node guarantees
    that the only tags that it returns are ones that it itself provides.

    **Parameters:**
    - `anon_pat`: If the pattern to not match is provided in this then the unmatched `AST` is not returned in tags. If
        this is missing (default `None`) then there must be at least one element in `tags` and the first keyword there
        will be taken to be the pattern to not match and the name of the tag to use for the unmatched `AST`.
    - `tags`: Any static tags to return on an unsuccessful match (including the pattern to not match as the first
        keyword if not provided in `anon_pat`).

    **Returns:**
    - `M_Match`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    >>> MNOT('var') .match(Name(id='NOT_VAR'))
    <M_Match {}>

    >>> MNOT('var') .match(Name(id='var'))

    >>> MNOT('var', tag='static') .match(Name(id='NOT_VAR'))
    <M_Match {'tag': 'static'}>

    >>> MNOT(node='var', tag='static') .match(Name(id='NOT_VAR'))
    <M_Match {'node': Name(id='NOT_VAR'), 'tag': 'static'}>

    >>> MNOT(MNOT(node='var', tag='static')) .match(Name(id='NOT_VAR'))

    >>> MNOT(MNOT(MNOT(node='var'), add1=1), add2=2) .match(Name(id='NOT_VAR'))
    <M_Match {'add2': 2}>
    """

    @staticmethod
    def _match(self: MNOT, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
        m = _MATCH_FUNCS.get((p := self.pat).__class__, _match_default)(p, tgt, moptions)

        if m is not None:
            return None

        if pat_tag := self.pat_tag:
            return {pat_tag: tgt, **self.static_tags}

        return self.static_tags

    @staticmethod
    def _leaf_asts(self: M) -> tp_Set[type[AST]]:
        leaf_asts = _LEAF_ASTS_FUNCS.get((p := self.pat).__class__, _leaf_asts_default)(p)

        if not leaf_asts:
            return ASTS_LEAF__ALL
        elif len(leaf_asts) >= _LEN_ASTS_LEAF__ALL:
            return _EMPTY_SET

        return ASTS_LEAF__ALL - leaf_asts


class MOR(M_Pattern):
    """Simple OR pattern. Matches if any of the given patterns match.

    **Parameters:**
    - `anon_pats`: Patterns that constitute a successful match, only need one to match. Checked in order.
    - `tagged_pats`: Patterns that constitute a successful match, only need one to match. Checked in order. The first
        target matched with any one of these patterns will be returned in its corresponding tag (keyword name).

    **Returns:**
    - `M_Match`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    >>> MOR('a', this='b') .match(FST('a'))
    <M_Match {}>

    >>> MOR('a', this='b') .match(FST('b'))
    <M_Match {'this': Name(id='b')}>

    >>> MOR('a', this='b') .match(FST('c'))

    Mixed pattern types and nesting.

    >>> pat = MOR(Name('good'), M(m=Call, static='tag'), st=Starred)

    >>> pat.match(FST('bad'))

    >>> pat.match(FST('good'))
    <M_Match {}>

    >>> pat.match(FST('*starred'))
    <M_Match {'st': Starred(value=Name(id='starred'))}>

    >>> pat.match(FST('call()'))
    <M_Match {'m': Call(func=Name(id='call'), args=[], keywords=[]), 'static': 'tag'}>

    >>> pat.match(FST('bin + op'))
"""

    pats:     list[_Patterns]  ; """@private"""
    pat_tags: list[str | None]  ; """@private"""

    def __init__(self, *anon_pats: _Patterns, **tagged_pats: _Patterns) -> None:
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

    @staticmethod
    def _match(self: MOR, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
        for i, p in enumerate(self.pats):
            m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, moptions)

            if m is not None:
                if pat_tag := self.pat_tags[i]:
                    return {pat_tag: tgt, **m}

                return m

        return None

    @staticmethod
    def _leaf_asts(self: MOR) -> tp_Set[type[AST]]:
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

    **Returns:**
    - `M_Match`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    The following will always fail as a node cannot be both a `Name` AND a `Call` at the same time.

    >>> MAND(Name, Call) .match(FST('name'))

    >>> MAND(Name, Call) .match(FST('call()'))

    More sensical usage below, for example that a list starts with `a` and contains at least two `b`.

    >>> pat = MList(MAND(['a', ...], [..., 'b', ..., 'b', ...]))

    >>> pat.match(FST('[a, b, c]'))

    >>> pat.match(FST('[a, b, b, c]'))
    <M_Match {}>

    >>> pat.match(FST('[d, a, b, b, c]'))

    >>> pat.match(FST('[a, x, b, y, z, b, c, b]'))
    <M_Match {}>
    """

    @staticmethod
    def _match(self: MAND, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
        tagss = []

        for i, p in enumerate(self.pats):
            m = _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt, moptions)

            if m is None:
                return None

            if pat_tag := self.pat_tags[i]:
                tagss.append({pat_tag: tgt, **m})
            elif m:
                tagss.append(m)

        # combine all tags and return

        if not tagss:
            tags = _EMPTY_DICT
        if len(tagss) == 1:
            tags = tagss[0]

        else:
            tags = {}

            for ts in tagss:
                tags.update(ts)

        return tags

    @staticmethod
    def _leaf_asts(self: MOR) -> tp_Set[type[AST]]:
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
    """This pattern matches any one of the given types and arbitrary fields if present. And its "m-any" as "in any one
    of", not "many" as in "several", though that fits as well. Essentially this is an AND of whether the node type is
    one of those provided and the given fields match.

    **Note:** Since there are several fields which can be either an individual element or list of elements, usage of
    arbitrary fields in this node does not raise an error on list vs. non-list mismatch and instead just considers it a
    non-match.

    **Parameters:**
    - `types`: An iterable of `AST` or `MAST` **TYPES**, not instances. In order to match successfully the target must
        be at least one of these types (non-leaf types like `stmt` included). To match any node for type use `AST`.
    - `fields`: Field names which must be present (unless wildcard `...`) along with the patterns they need to match.

    **Returns:**
    - `M_Match`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    Whether a statement type that CAN have a docstring actually has a docstring.

    >>> pat = MANY(
    ...     (ClassDef, FunctionDef, AsyncFunctionDef),
    ...     body=[Expr(MConstant(str)), ...],
    ... )

    >>> pat.match(FST('def f(): "docstr"; pass'))
    <M_Match {}>

    >>> pat.match(FST('if 1: "NOTdocstr"'))

    >>> pat.match(FST('def f(): pass; "NOTdocstr"'))

    >>> pat.match(FST('class cls: "docstr"; pass'))
    <M_Match {}>
    """

    fields: Mapping[str, _Patterns]  ; """@private"""

    def __init__(self, types: Iterable[type[AST | MAST]], **fields: _Patterns) -> None:
        ts = {}

        for t in types:
            if issubclass(t, MAST):
                t = t._types  # will be a single type
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

    @staticmethod
    def _leaf_asts(self: MANY) -> tp_Set[type[AST]]:
        leaf_asts = set()

        for p in self._types:
            la = _LEAF_ASTS_FUNCS.get(p.__class__, _leaf_asts_default)(p)

            if len(la) >= _LEN_ASTS_LEAF__ALL:  # early out because we hit all possible types
                return la

            leaf_asts.update(la)

            if len(leaf_asts) >= _LEN_ASTS_LEAF__ALL:  # another early out
                return leaf_asts

        return leaf_asts


class MRE(M_Pattern):
    """Tagging regex pattern. Normal `re.Pattern` can be used and that will just be checked using `re.match()` and the
    `re.Match` object is lost. If this pattern is used instead the can specify the use of `re.match()` or `re.search()`,
    as well as allowing the `re.Match` object to be returned as a tag.

    **Parameters:**
    - `anon_re_pat`: If the pattern to match is provided in this (either as a `str` to compile or an already compiled
        `re.Pattern`) then the matched `re.Match` is not returned in tags. If this is missing then there must be at
        least one element in `tags` and the first keyword there will be taken to be the pattern to match and the name of
        the tag to use for the matched `re.Match` object.
    - `flags`: If passing a `str` as the pattern then these are the `re` flags to pass to `re.compile()`. If passing an
        already compiled `re.Pattern` then this must remain `0`.
    - `tags`: Any static tags to return on a successful match (including the pattern to match as the first keyword if
        not provided in `anon_re_pat`).

    **Returns:**
    - `M_Match`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    >>> MRE('good|bad|ugly') .match(Name('ugly'))
    <M_Match {}>

    >>> MRE('good|bad|ugly') .match(Name('passable'))

    Has bad in it.

    >>> MRE(tag='.*bad.*') .match(arg('this_arg_is_not_so_bad'))
    <M_Match {'tag': <re.Match object; span=(0, 22), match='this_arg_is_not_so_bad'>}>

    Another way so we can get the exact location from the `re.Match` object.

    >>> MRE(tag='bad', search=True) .match(arg('this_arg_is_not_so_bad'))
    <M_Match {'tag': <re.Match object; span=(19, 22), match='bad'>}>
    """

    re_pat: re_Pattern  ; """@private"""
    pat_tag: str | None  ; """@private"""
    static_tags: Mapping[str, Any]  ; """@private"""
    search: bool  ; """@private"""

    def __init__(
        self, anon_re_pat: str | re_Pattern | None = None, /, flags: int = 0, search: bool = False, **tags  # can only be one tag which will be the name for the pattern, in which case anon_re_pat must be None
    ) -> None:
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

    @staticmethod
    def _match(self: MRE, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
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

        elif isinstance(tgt, list) and moptions.get('list_check', True):
            raise MatchError('MRE can never match a list field')

        else:
            return None

        if pat_tag := self.pat_tag:
            return {pat_tag: m, **self.static_tags}

        return self.static_tags


class MCB(M):
    """Callback to check target, which can be an `AST` or constant or a list of those. Can also specify that the
    callback always be called with an `FST` node. In this case this pattern can only be used in places where a node or
    `None` is expected, otherwise will raise during match.

    **Parameters:**
    - `anon_callback`: The function to call on each target to check. Depending on where in the pattern structure this
        pattern is used, the function may be called with an `AST` node or a primitive, or even a list of elements. If
        the function returns a truthy value then the match is considered a success, and likewise falsey means failure.
        If this is not provided then the callback is taken from the first keyword in `tags` just like for the `M`
        pattern.
    - `call_with_FST`: If this is set to `True` then the callback function can only be called with `FST` nodes or a
        `None` value. This restricts the use of this pattern to places where nodes are expected to be (or be missing
        with a `None` value in their place), no primitives or lists. Also obviously, restricted to `FST` trees in this
        case.
    - `tag_call_ret`: If this is set to `True` then the truthy return value is returned in the pattern tag instead of
        the target matched. This only applies if the callback is passed as the first keyword in `tags` instead of in
        `anon_callback`, as in that case no target tag is available to return. Also keep in mind the "truthy value" bit
        in case a successful match might want to return a falsey value, it would need to be accomodated somehow (wrapped
        in a tuple maybe).

    **Returns:**
    - `M_Match`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    >>> in_range = lambda x: 2 < x < 8
    >>> pat = MConstant(MCB(in_range))

    >>> pat.match(FST('1'))

    >>> pat.match(FST('3'))
    <M_Match {}>

    >>> pat.match(FST('7'))
    <M_Match {}>

    >>> pat.match(FST('10'))

    Check for only parenthesized tuples.

    >>> pat = MCB(FST.is_parenthesized_tuple, call_with_FST=True)

    >>> pat.match(FST('x, y, z'))

    >>> pat.match(FST('(x, y, z)'))
    <M_Match {}>

    >>> pat.match(FST('[x, y, z]'))

    >>> pat.match(Tuple([]))
    Traceback (most recent call last):
    ...
    fst.match.MatchError: MCB FST callback found AST node without an FST: Tuple(elts=[])

    Get node along with name in uppercase.

    >>> pat = M(node=Name(MCB(upper=str.upper, tag_call_ret=True)))

    >>> pat.match(FST('a.b'))

    >>> pat.match(FST('some_name'))
    <M_Match {'upper': 'SOME_NAME', 'node': Name(id='some_name')}>
    """

    _requires = 'callback'  # for printing error message

    pat: Callable[[AST], object] | Callable[[fst.FST], object]  ; """@private"""
    call_with_FST: bool  ; """@private"""
    tag_call_ret: bool  ; """@private"""

    def __init__(
        self,
        anon_callback: Callable[[AST], object] | Callable[[fst.FST], object] = _SENTINEL,
        /,
        call_with_FST: bool = False,
        *,
        tag_call_ret: bool = False,
        **tags,
    ) -> None:
        M.__init__(self, anon_callback, **tags)

        if tag_call_ret and anon_callback is not _SENTINEL:
            raise ValueError('MCB can never return the callback return value since the callback is not specified with keyword')

        self.call_with_FST = call_with_FST
        self.tag_call_ret = tag_call_ret

    @staticmethod
    def _match(self: MCB, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
        if not self.call_with_FST or tgt is None:
            m = self.pat(tgt)
        elif not isinstance(tgt, AST):
            raise MatchError(f'MCB FST callback needs node or None, got {_rpr(tgt)}')
        elif not (f := getattr(tgt, 'f', None)):
            raise MatchError(f'MCB FST callback found AST node without an FST: {_rpr(tgt)}')
        else:
            m = self.pat(f)

        if not m:
            return None

        if pat_tag := self.pat_tag:
            if self.tag_call_ret:
                tgt = m

            return {pat_tag: tgt, **self.static_tags}

        return self.static_tags


# ......................................................................................................................

def _match_default(pat: _Patterns, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Match the fields of any `M_Pattern`, `AST` or a `str` (either as a primitive value or as source)."""

    if isinstance(pat, list):
        if isinstance(tgt, fstview):
            if tgt.is_dictlike:
                raise MatchError('list can never match a dictlike multi-element field')

            tgt = [f.a for f in tgt]  # convert to temporary list of AST nodes

        if not isinstance(tgt, list):
            if moptions.get('list_check', True):
                raise MatchError('list can never match a non-list field')

            return None

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

        tags = {}

        for ts in tagss:
            tags.update(ts)

        return tags

    # got here through subclass of a primitive type

    if isinstance(pat, str):
        return _match_str(pat, tgt, moptions)

    return _match_primitive(pat, tgt, moptions)

def _match_str(pat: str, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
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

    elif isinstance(tgt, list) and moptions.get('list_check', True):
        raise MatchError('str can never match a list field')

    else:
        return None

    return _EMPTY_DICT

def _match_primitive(pat: constant, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
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
        if issubclass(tgt_cls, list) and moptions.get('list_check', True):
            raise MatchError(f'{pat_cls.__qualname__} can never match a list field')

        return None

    return _EMPTY_DICT

def _match_node(pat: M_Pattern | AST, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """`M_Pattern` or `AST` leaf node."""

    is_mpat = isinstance(pat, M_Pattern)
    types = pat._types if is_mpat else pat.__class__

    if not isinstance(tgt, types):
        if isinstance(tgt, list) and moptions.get('list_check', True):
            raise MatchError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    tagss = []

    for field in pat._fields:
        p = getattr(pat, field, ...)

        if p is ...:  # ellipsis handled here without dispatching for various reasons
            continue

        t = getattr(tgt, field, _SENTINEL)  # _SENTINEL for arbitrary fields, but also field may not exist in target because pattern may have fields from a greater python version than we are running

        if t is _SENTINEL:
            if not (f := getattr(tgt, 'f', None)) or not isinstance(t := getattr(f, field, None), fstview):  # maybe its a virtual field
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

    tags = {}

    for ts in tagss:
        tags.update(ts)

    return tags

def _match_node_Constant(
    pat: MConstant | Constant, tgt: _Targets, moptions: Mapping[str, Any]
) -> Mapping[str, Any] | None:
    """We do a special handler for `Constant` so we can check for a real `Ellipsis` instead of having that work as a
    wildcarcd. We do a standalone handler so don't have to have the check in general."""

    if not isinstance(tgt, Constant):
        if isinstance(tgt, list) and moptions.get('list_check', True):
            raise MatchError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    tagss = []

    if (p := getattr(pat, 'value', _SENTINEL)) is not _SENTINEL:  # missing value acts as implicit ... wildcard, while the real ... is a concrete value here
        f = _match_primitive if p is ... else _MATCH_FUNCS.get(p.__class__, _match_default)

        if (m := f(p, tgt.value, moptions)) is None:
            return None
        if m:
            tagss.append(m)

    if (p := getattr(pat, 'kind', ...)) is not ...:
        if (m := _MATCH_FUNCS.get(p.__class__, _match_default)(p, tgt.kind, moptions)) is None:
            return None
        if m:
            tagss.append(m)

    # combine all tags and return

    if not tagss:
        return _EMPTY_DICT
    if len(tagss) == 1:
        return tagss[0]

    tags = {}

    for ts in tagss:
        tags.update(ts)

    return tags

def _match_node_expr_context(
    pat: Load | Store | Del, tgt: _Targets, moptions: Mapping[str, Any]
) -> Mapping[str, Any] | None:
    """This exists as a convenience so that an `AST` pattern `Load`, `Store` and `Del` always match each other unless
    the match option `ctx=True`. `MLoad`, `MStore` and `MDel` don't get here, they always do a match check. A pattern
    `None` must also match one of these successfully for py < 3.13."""

    if not isinstance(tgt, expr_context) or (moptions.get('ctx') and tgt.__class__ is not pat.__class__):
        if isinstance(tgt, list) and moptions.get('list_check', True):
            raise MatchError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    return _EMPTY_DICT

def _match_node_arbitrary_fields(
    pat: M_Pattern | AST, tgt: _Targets, moptions: Mapping[str, Any]
) -> Mapping[str, Any] | None:
    """This just turns off list field vs. non-list field errors for nodes which do arbitrary field matches."""

    return _match_node(pat, tgt, {**moptions, 'list_check': False})

def _match_type(pat: type, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Just match the `AST` type (or equivalent `MAST` type)."""

    if issubclass(pat, M_Pattern):
        pat = pat._types

    if not isinstance(tgt, pat):
        if isinstance(tgt, list) and moptions.get('list_check', True):
            raise MatchError(f'{pat.__class__.__qualname__} can never match a list field')

        return None

    return _EMPTY_DICT

def _match_re_Pattern(pat: re_Pattern, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
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

    elif isinstance(tgt, list) and moptions.get('list_check', True):
        raise MatchError('re.Pattern can never match a list field')

    else:
        return None

    return _EMPTY_DICT

def _match_Ellipsis(pat: EllipsisType, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Always succeeds."""

    return _EMPTY_DICT

def _match_None(pat: NoneType, tgt: _Targets, moptions: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if tgt is not None:
        if isinstance(tgt, list) and moptions.get('list_check', True):
            raise MatchError('None can never match a list field')

        return None

    return _EMPTY_DICT

_MATCH_FUNCS = {
    M:                   M._match,
    MNOT:                MNOT._match,
    MOR:                 MOR._match,
    MAND:                MAND._match,
    MANY:                _match_node,
    MRE:                 MRE._match,
    MCB:                 MCB._match,
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
    MAST:                _match_node_arbitrary_fields,
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
    Mexcepthandler:      _match_node_arbitrary_fields,
    Mexpr:               _match_node_arbitrary_fields,
    Mexpr_context:       _match_node_arbitrary_fields,
    Mkeyword:            _match_node,
    Mmatch_case:         _match_node,
    Mmod:                _match_node_arbitrary_fields,
    Moperator:           _match_node,
    Mpattern:            _match_node_arbitrary_fields,
    Mstmt:               _match_node_arbitrary_fields,
    Mtype_ignore:        _match_node_arbitrary_fields,
    Munaryop:            _match_node,
    Mwithitem:           _match_node,
    MTryStar:            _match_node,
    MTypeAlias:          _match_node,
    Mtype_param:         _match_node_arbitrary_fields,
    MTypeVar:            _match_node,
    MParamSpec:          _match_node,
    MTypeVarTuple:       _match_node,
    MTemplateStr:        _match_node,
    MInterpolation:      _match_node,
    M_slice:             _match_node_arbitrary_fields,
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

    if isinstance(pat, str):
        return ASTS_LEAF__ALL

    if isinstance(pat, list):
        raise MatchError('unexpected list')

    return _EMPTY_SET

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
    ctx: bool = False,
) -> M_Match | None:
    r"""This will attempt to match this `self` against the given pattern. The pattern may be any of the `fst.match` `M*`
    patterns or it can be a pure `AST` pattern. Attempt to match against a `str` will check the source against that
    string. Likewise matching against a `re.Pattern` will check the source against the regex. Matching can also be done
    against a `type[AST]` or `type[MAST]` for a trivial type match. Trying to match lists or primitives with this will
    always fail (as `self` is an `FST`) and matching against a wildcard ellipsis `...` will always succeed.

    **Parameters:**
    - `pat`: The pattern to search for. Must resolve to a node, not a primitive or list (node patterns, type, wildcard,
        functional patterns of these). Because you're matching against a node, otherwise nothing will match.
    - `ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
        Defaults to `False` because when creating `AST` nodes the `ctx` field may be created automatically if you
        don't specify it so may inadvertantly break matches where you don't want to take that into consideration.
        Will always check `ctx` field for `MAST` patterns because there it is well behaved and if not specified
        is set to wildcard.

    **Returns:**
    - `M_Match`: The match object on successful match.
    - `None`: Did not match.

    **Examples:**

    >>> import re
    >>> from fst.match import *

    Quick and dirty use of `AST` nodes and strings and regex.

    >>> f = FST('val.attr', Attribute)

    >>> f.match(Attribute(Name('val'), 'attr'))
    <M_Match {}>

    >>> f.match(Attribute('val', 'attr'))
    <M_Match {}>

    >>> f.match('val.attr')
    <M_Match {}>

    >>> f.match(re.compile(r'.*\.attr'))
    <M_Match {}>

    Pattern for finding a `logger.info()` call that has a keyword argument named `cid`, returning that keyword in a tag
    called `cid_kw`. This one uses the pattern `MCall` and `Mkeyword` classes to avoid having to specify unused required
    fields. The `...` are wildcards.

    >>> pat = MCall(
    ...    func=Attribute(Name('logger'), 'info'),
    ...    keywords=[..., M(cid_kw=Mkeyword('cid')), ...]
    ... )

    >>> FST('logger.info("text", a=1, cid=123, b=2)') .match(pat)
    <M_Match {'cid_kw': keyword(arg='cid', value=Constant(value=123, kind=None))}>

    >>> FST('logger.warning("text", a=1, cid=123, b=2)') .match(pat)

    >>> FST('notlogger.info("text", a=1, cid=123, b=2)') .match(pat)

    >>> FST('logger.info("text", a=1, b=2)') .match(pat)

    Pattern for finding any `[*_cls | object.__class__] [is | is not] [ZST | zst.ZST]`. Will tag the initial object as
    `obj` and return whether the comparison is an `is` or `is not` in the `is_is` tag (which is missing in case of
    `IsNot` but the attribute check on the `M_Match` object returns a false value in this case.)

    >>> pat = Compare(
    ...     left=MOR(Attribute(M(obj=expr), '__class__'),
    ...              obj=M(Name(MRE(r'\w*_cls$')), is_name=True)),
    ...     ops=[MOR(IsNot, is_is=Is)],
    ...     comparators=[MOR(Name('ZST'), Attribute('zst', 'ZST'))],
    ... )

    >>> FST('a.__class__ is not ZST') .match(pat)
    <M_Match {'obj': Name(id='a')}>

    >>> bool(_.is_is)
    False

    >>> FST('a.__class__ is AST') .match(pat)

    >>> FST('node_cls is zst.ZST') .match(pat)
    <M_Match {'obj': Name(id='node_cls'), 'is_name': True, 'is_is': Is()}>

    >>> FST('node_cls_bad is zst.ZST') .match(pat)
    """

    m = _MATCH_FUNCS.get(pat.__class__, _match_default)(pat, self.a, dict(ctx=ctx))

    return None if m is None else M_Match(m, pat, self.a)


def search(
    self: fst.FST,
    pat: _Pattern,
    *,
    ctx: bool = False,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
    asts: list[AST] | None = None,
) -> Generator[M_Match, bool, None]:
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
    - `ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
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
    ...     print(m.fst.src)
    ast_cls is not zst.ZST
    code_cls is zst.ZST
    src_or_ast_or_fst.__class__ is ZST
    value.__class__ is not zst.ZST

    If you just want the first match.

    >>> print(next(f.search(pat)).fst.src)
    ast_cls is not zst.ZST
    """

    pat_cls = pat.__class__
    asts_leaf = _LEAF_ASTS_FUNCS.get(pat_cls, _leaf_asts_default)(pat)
    match_func = _MATCH_FUNCS.get(pat_cls, _match_default)
    moptions = dict(ctx=ctx)

    if len(asts_leaf) == _LEN_ASTS_LEAF__ALL:  # need to check all nodes
        def all_func(fst_: fst.FST) -> M_Match | Literal[False]:
            m = match_func(pat, fst_.a, moptions)

            return False if m is None else M_Match(m, pat, fst_.a)

    else:
        def all_func(fst_: fst.FST) -> M_Match | Literal[False]:
            if fst_.a.__class__ not in asts_leaf:
                return False

            m = match_func(pat, fst_.a, moptions)

            return False if m is None else M_Match(m, pat, fst_.a)

    return self.walk(all_func, self_=self_, recurse=recurse, scope=scope, back=back, asts=asts)


def sub(
    self: fst.FST,
    pat: _Pattern,
    repl: Code | Callable[[M_Match], Code],
    nest: bool = False,
    *,
    ctx: bool = False,
    self_: bool = True,
    recurse: bool = True,
    scope: bool = False,
    back: bool = False,
    asts: list[AST] | None = None,
    **options,
) -> int:
    """Substitute matching targets with a given `repl` template or dynamically generated node if `repl` is a function.
    The template substitutions can include tagged elements from a match.

    **Parameters:**
    - `pat`: The pattern to search for. Must resolve to a node, not a primitive or list (node patterns, type, wildcard,
        functional patterns of these). Because you're matching against nodes, otherwise nothing will match.
    - `repl`: Replacement template or function to generate replacement nodes.
    - `nest: Whether to allow recursion into nested substitutions or not. Allowing this can cause infinite recursion due
        to replacement with things that match the pattern, so don't use unless you are sure this can not happen.
    - `ctx`: Whether to match against the `ctx` field of `AST` patterns or not (as opposed to `MAST` patterns).
        Defaults to `False` because when creating `AST` nodes the `ctx` field may be created automatically if you
        don't specify it so may inadvertantly break matches where you don't want to take that into consideration.
        Will always check `ctx` field for `MAST` patterns because there it is well behaved and if not specified
        is set to wildcard.
    - `self_`, `recurse`, `scope`, `back`, `asts`: These are parameters for the underlying `walk()` function. See that
        function for their meanings.
    - `options`: The options to use for the `replace()` calls. See `options()`.

    **Returns:**
    - `int`: Number of substitutions made (by this function, user function could have done others, but that is on the
        user).

    **Examples:**

    >>> from fst.match import *




    """

    is_func = callable(repl)

    if not is_func:
        repl = code_as_all(repl, options, self.root.parse_params)
        paths = []  # [(tag, child_path), ...]  an empty string tag means replace with the node matched

        for f in repl.walk(Name):
            if (n := f.a.id).startswith('__fst_'):
                paths.append((n[6:], repl.child_path(f)))

    count = 0
    gen = self.search(pat, ctx=ctx, self_=self_, recurse=recurse, scope=scope, back=back, asts=asts)

    for m in gen:
        f = m.fst

        if is_func:
            r = repl(m)

        else:
            r = repl.copy()

            for tag, path in paths:
                if not tag:
                    g = f.copy()
                elif (g := m.tags.get(tag, _SENTINEL)) is _SENTINEL:
                    raise RuntimeError(f'{tag!r} tag not found for substitution')
                elif isinstance(h := getattr(g, 'f', None), fst.FST):
                    g = h.copy()

                r.child_from_path(path).replace(g, **options)

        if r is not f:
            f.replace(r, **options)

            count += 1

        if not nest:
            gen.send(False)

    return count
