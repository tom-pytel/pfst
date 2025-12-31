"""`FST` class accessors for underlying `AST` node fields.

This module contains functions which are imported as methods in the `FST` class (for now).
"""

from typing import Union

from . import fst

from .asttypes import AST, FunctionDef, AsyncFunctionDef, ClassDef, TypeAlias
from .astutil import constant
from .common import PYGE12, PYGE13
from .code import Code
from .view import fstview, fstview_dummy

__all__ = [
    'body',
    'type_ignores',
    'argtypes',
    'returns',
    'decorator_list',
    'name',
    'type_params',
    'args',
    'type_comment',
    'bases',
    'keywords',
    'value',
    'targets',
    'target',
    'op',
    'annotation',
    'simple',
    'iter',
    'orelse',
    'test',
    'items',
    'subject',
    'cases',
    'exc',
    'cause',
    'handlers',
    'finalbody',
    'msg',
    'names',
    'module',
    'level',
    'values',
    'left',
    'right',
    'operand',
    'keys',
    'elts',
    'elt',
    'generators',
    'key',
    'ops',
    'comparators',
    'func',
    'conversion',
    'format_spec',
    'str',
    'kind',
    'attr',
    'ctx',
    'slice',
    'id',
    'lower',
    'upper',
    'step',
    'ifs',
    'is_async',
    'type',
    'posonlyargs',
    'defaults',
    'vararg',
    'kwonlyargs',
    'kw_defaults',
    'kwarg',
    'arg',
    'asname',
    'context_expr',
    'optional_vars',
    'pattern',
    'guard',
    'patterns',
    'rest',
    'cls',
    'kwd_attrs',
    'kwd_patterns',
    'tag',
    'bound',
    'default_value',
    'arglikes',
]


# Module, Interactive, Expression, FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If, With, AsyncWith, Try, TryStar, Lambda, IfExp, ExceptHandler, match_case
@property
def body(self: 'fst.FST') -> fstview | Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `body`."""

    if isinstance(child := self.a.body, list):
        return fstview(self, 'body')

    return child.f

@body.setter
def body(self: 'fst.FST', code: Code | None) -> None:
    if isinstance(self.a.body, list):
        self._put_slice(code, 0, 'end', 'body')
    else:
        self._put_one(code, None, 'body')

@body.deleter
def body(self: 'fst.FST') -> None:
    if isinstance(self.a.body, list):
        self._put_slice(None, 0, 'end', 'body')
    else:
        self._put_one(None, None, 'body')


# Module
@property
def type_ignores(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `type_ignores`."""

    self.a.type_ignores  # noqa: B018

    return fstview(self, 'type_ignores')

@type_ignores.setter
def type_ignores(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'type_ignores')

@type_ignores.deleter
def type_ignores(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'type_ignores')


# FunctionType
@property
def argtypes(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `argtypes`."""

    self.a.argtypes  # noqa: B018

    return fstview(self, 'argtypes')

@argtypes.setter
def argtypes(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'argtypes')

@argtypes.deleter
def argtypes(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'argtypes')


# FunctionType, FunctionDef, AsyncFunctionDef
@property
def returns(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `returns`."""

    return child.f if (child := self.a.returns) else None

@returns.setter
def returns(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'returns')

@returns.deleter
def returns(self: 'fst.FST') -> None:
    self._put_one(None, None, 'returns')


# FunctionDef, AsyncFunctionDef, ClassDef, _decorator_list
@property
def decorator_list(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `decorator_list`."""

    self.a.decorator_list  # noqa: B018

    return fstview(self, 'decorator_list')

@decorator_list.setter
def decorator_list(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'decorator_list')

@decorator_list.deleter
def decorator_list(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'decorator_list')


# FunctionDef, AsyncFunctionDef, ClassDef, TypeAlias, ExceptHandler, alias, MatchStar, MatchAs, TypeVar, ParamSpec, TypeVarTuple
@property
def name(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `name`."""

    return child.f if isinstance(child := self.a.name, AST) else child

@name.setter
def name(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'name')

@name.deleter
def name(self: 'fst.FST') -> None:
    self._put_one(None, None, 'name')


# FunctionDef, AsyncFunctionDef, ClassDef, TypeAlias, _type_params
if PYGE12:
    @property
    def type_params(self: 'fst.FST') -> fstview:
        """`FST` accessor for `AST` field `type_params`."""

        self.a.type_params  # noqa: B018

        return fstview(self, 'type_params')

    @type_params.setter
    def type_params(self: 'fst.FST', code: Code | None) -> None:
        self._put_slice(code, 0, 'end', 'type_params')

    @type_params.deleter
    def type_params(self: 'fst.FST') -> None:
        self._put_slice(None, 0, 'end', 'type_params')

else:  # safely access nonexistent empty field
    @property
    def type_params(self: 'fst.FST') -> list:
        """`FST` accessor for `AST` field `type_params`."""

        if self.a.__class__ in (FunctionDef, AsyncFunctionDef, ClassDef, TypeAlias):
            return fstview_dummy(self, 'type_params')

        self.a.type_params  # noqa: B018, AttributeError

    @type_params.setter
    def type_params(self: 'fst.FST', code: Code | None) -> None:
        if code is not None:  # maybe fail successfully
            raise RuntimeError("field 'type_params' does not exist on python < 3.12")

    @type_params.deleter
    def type_params(self: 'fst.FST') -> None:
        pass


# FunctionDef, AsyncFunctionDef, Lambda, Call, arguments
@property
def args(self: 'fst.FST') -> fstview | Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `args`."""

    if isinstance(child := self.a.args, list):
        return fstview(self, 'args')

    return child.f

@args.setter
def args(self: 'fst.FST', code: Code | None) -> None:
    if isinstance(self.a.args, list):
        self._put_slice(code, 0, 'end', 'args')
    else:
        self._put_one(code, None, 'args')

@args.deleter
def args(self: 'fst.FST') -> None:
    if isinstance(self.a.args, list):
        self._put_slice(None, 0, 'end', 'args')
    else:
        self._put_one(None, None, 'args')


# FunctionDef, AsyncFunctionDef, Assign, For, AsyncFor, With, AsyncWith, arg
@property
def type_comment(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `type_comment`."""

    return self.a.type_comment

@type_comment.setter
def type_comment(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'type_comment')

@type_comment.deleter
def type_comment(self: 'fst.FST') -> None:
    self._put_one(None, None, 'type_comment')


# ClassDef
@property
def bases(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `bases`."""

    self.a.bases  # noqa: B018

    return fstview(self, 'bases')

@bases.setter
def bases(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'bases')

@bases.deleter
def bases(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'bases')


# ClassDef, Call
@property
def keywords(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `keywords`."""

    self.a.keywords  # noqa: B018

    return fstview(self, 'keywords')

@keywords.setter
def keywords(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'keywords')

@keywords.deleter
def keywords(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'keywords')


# Return, Assign, TypeAlias, AugAssign, AnnAssign, Expr, NamedExpr, DictComp, Await, Yield, YieldFrom, FormattedValue, Interpolation, Constant, Attribute, Subscript, Starred, keyword, MatchValue, MatchSingleton
@property
def value(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `value`."""

    return child.f if isinstance(child := self.a.value, AST) else child

@value.setter
def value(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'value')

@value.deleter
def value(self: 'fst.FST') -> None:
    self._put_one(None, None, 'value')


# Delete, Assign, _Assign_targets
@property
def targets(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `targets`."""

    self.a.targets  # noqa: B018

    return fstview(self, 'targets')

@targets.setter
def targets(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'targets')

@targets.deleter
def targets(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'targets')


# AugAssign, AnnAssign, For, AsyncFor, NamedExpr, comprehension
@property
def target(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `target`."""

    return self.a.target.f

@target.setter
def target(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'target')

@target.deleter
def target(self: 'fst.FST') -> None:
    self._put_one(None, None, 'target')


# AugAssign, BoolOp, BinOp, UnaryOp
@property
def op(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `op`."""

    return self.a.op.f

@op.setter
def op(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'op')

@op.deleter
def op(self: 'fst.FST') -> None:
    self._put_one(None, None, 'op')


# AnnAssign, arg
@property
def annotation(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `annotation`."""

    return child.f if (child := self.a.annotation) else None

@annotation.setter
def annotation(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'annotation')

@annotation.deleter
def annotation(self: 'fst.FST') -> None:
    self._put_one(None, None, 'annotation')


# AnnAssign
@property
def simple(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `simple`."""

    return self.a.simple

@simple.setter
def simple(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'simple')

@simple.deleter
def simple(self: 'fst.FST') -> None:
    self._put_one(None, None, 'simple')


# For, AsyncFor, comprehension
@property
def iter(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `iter`."""

    return self.a.iter.f

@iter.setter
def iter(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'iter')

@iter.deleter
def iter(self: 'fst.FST') -> None:
    self._put_one(None, None, 'iter')


# For, AsyncFor, While, If, Try, TryStar, IfExp
@property
def orelse(self: 'fst.FST') -> fstview | Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `orelse`."""

    if isinstance(child := self.a.orelse, list):
        return fstview(self, 'orelse')

    return child.f

@orelse.setter
def orelse(self: 'fst.FST', code: Code | None) -> None:
    if isinstance(self.a.orelse, list):
        self._put_slice(code, 0, 'end', 'orelse')
    else:
        self._put_one(code, None, 'orelse')

@orelse.deleter
def orelse(self: 'fst.FST') -> None:
    if isinstance(self.a.orelse, list):
        self._put_slice(None, 0, 'end', 'orelse')
    else:
        self._put_one(None, None, 'orelse')


# While, If, Assert, IfExp
@property
def test(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `test`."""

    return self.a.test.f

@test.setter
def test(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'test')

@test.deleter
def test(self: 'fst.FST') -> None:
    self._put_one(None, None, 'test')


# With, AsyncWith, _withitems
@property
def items(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `items`."""

    self.a.items  # noqa: B018

    return fstview(self, 'items')

@items.setter
def items(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'items')

@items.deleter
def items(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'items')


# Match
@property
def subject(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `subject`."""

    return self.a.subject.f

@subject.setter
def subject(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'subject')

@subject.deleter
def subject(self: 'fst.FST') -> None:
    self._put_one(None, None, 'subject')


# Match, _match_cases
@property
def cases(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `cases`."""

    self.a.cases  # noqa: B018

    return fstview(self, 'cases')

@cases.setter
def cases(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'cases')

@cases.deleter
def cases(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'cases')


# Raise
@property
def exc(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `exc`."""

    return child.f if (child := self.a.exc) else None

@exc.setter
def exc(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'exc')

@exc.deleter
def exc(self: 'fst.FST') -> None:
    self._put_one(None, None, 'exc')


# Raise
@property
def cause(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `cause`."""

    return child.f if (child := self.a.cause) else None

@cause.setter
def cause(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'cause')

@cause.deleter
def cause(self: 'fst.FST') -> None:
    self._put_one(None, None, 'cause')


# Try, TryStar, _ExceptHandlers
@property
def handlers(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `handlers`."""

    self.a.handlers  # noqa: B018

    return fstview(self, 'handlers')

@handlers.setter
def handlers(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'handlers')

@handlers.deleter
def handlers(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'handlers')


# Try, TryStar
@property
def finalbody(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `finalbody`."""

    self.a.finalbody  # noqa: B018

    return fstview(self, 'finalbody')

@finalbody.setter
def finalbody(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'finalbody')

@finalbody.deleter
def finalbody(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'finalbody')


# Assert
@property
def msg(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `msg`."""

    return child.f if (child := self.a.msg) else None

@msg.setter
def msg(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'msg')

@msg.deleter
def msg(self: 'fst.FST') -> None:
    self._put_one(None, None, 'msg')


# Import, ImportFrom, Global, Nonlocal, _aliases
@property
def names(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `names`."""

    self.a.names  # noqa: B018

    return fstview(self, 'names')

@names.setter
def names(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'names')

@names.deleter
def names(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'names')


# ImportFrom
@property
def module(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `module`."""

    return self.a.module

@module.setter
def module(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'module')

@module.deleter
def module(self: 'fst.FST') -> None:
    self._put_one(None, None, 'module')


# ImportFrom
@property
def level(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `level`."""

    return self.a.level

@level.setter
def level(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'level')

@level.deleter
def level(self: 'fst.FST') -> None:
    self._put_one(None, None, 'level')


# BoolOp, Dict, JoinedStr, TemplateStr
@property
def values(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `values`."""

    self.a.values  # noqa: B018

    return fstview(self, 'values')

@values.setter
def values(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'values')

@values.deleter
def values(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'values')


# BinOp, Compare
@property
def left(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `left`."""

    return self.a.left.f

@left.setter
def left(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'left')

@left.deleter
def left(self: 'fst.FST') -> None:
    self._put_one(None, None, 'left')


# BinOp
@property
def right(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `right`."""

    return self.a.right.f

@right.setter
def right(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'right')

@right.deleter
def right(self: 'fst.FST') -> None:
    self._put_one(None, None, 'right')


# UnaryOp
@property
def operand(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `operand`."""

    return self.a.operand.f

@operand.setter
def operand(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'operand')

@operand.deleter
def operand(self: 'fst.FST') -> None:
    self._put_one(None, None, 'operand')


# Dict, MatchMapping
@property
def keys(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `keys`."""

    self.a.keys  # noqa: B018

    return fstview(self, 'keys')

@keys.setter
def keys(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'keys')

@keys.deleter
def keys(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'keys')


# Set, List, Tuple
@property
def elts(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `elts`."""

    self.a.elts  # noqa: B018

    return fstview(self, 'elts')

@elts.setter
def elts(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'elts')

@elts.deleter
def elts(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'elts')


# ListComp, SetComp, GeneratorExp
@property
def elt(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `elt`."""

    return self.a.elt.f

@elt.setter
def elt(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'elt')

@elt.deleter
def elt(self: 'fst.FST') -> None:
    self._put_one(None, None, 'elt')


# ListComp, SetComp, DictComp, GeneratorExp, _comprehensions
@property
def generators(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `generators`."""

    self.a.generators  # noqa: B018

    return fstview(self, 'generators')

@generators.setter
def generators(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'generators')

@generators.deleter
def generators(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'generators')


# DictComp
@property
def key(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `key`."""

    return self.a.key.f

@key.setter
def key(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'key')

@key.deleter
def key(self: 'fst.FST') -> None:
    self._put_one(None, None, 'key')


# Compare
@property
def ops(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `ops`."""

    self.a.ops  # noqa: B018

    return fstview(self, 'ops')

@ops.setter
def ops(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'ops')

@ops.deleter
def ops(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'ops')


# Compare
@property
def comparators(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `comparators`."""

    self.a.comparators  # noqa: B018

    return fstview(self, 'comparators')

@comparators.setter
def comparators(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'comparators')

@comparators.deleter
def comparators(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'comparators')


# Call
@property
def func(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `func`."""

    return self.a.func.f

@func.setter
def func(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'func')

@func.deleter
def func(self: 'fst.FST') -> None:
    self._put_one(None, None, 'func')


# FormattedValue, Interpolation
@property
def conversion(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `conversion`."""

    return self.a.conversion

@conversion.setter
def conversion(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'conversion')

@conversion.deleter
def conversion(self: 'fst.FST') -> None:
    self._put_one(None, None, 'conversion')


# FormattedValue, Interpolation
@property
def format_spec(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `format_spec`."""

    return child.f if (child := self.a.format_spec) else None

@format_spec.setter
def format_spec(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'format_spec')

@format_spec.deleter
def format_spec(self: 'fst.FST') -> None:
    self._put_one(None, None, 'format_spec')


# Interpolation
@property
def str(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `str`."""

    return self.a.str

@str.setter
def str(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'str')

@str.deleter
def str(self: 'fst.FST') -> None:
    self._put_one(None, None, 'str')


# Constant
@property
def kind(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `kind`."""

    return self.a.kind

@kind.setter
def kind(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'kind')

@kind.deleter
def kind(self: 'fst.FST') -> None:
    self._put_one(None, None, 'kind')


# Attribute
@property
def attr(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `attr`."""

    return self.a.attr

@attr.setter
def attr(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'attr')

@attr.deleter
def attr(self: 'fst.FST') -> None:
    self._put_one(None, None, 'attr')


# Attribute, Subscript, Starred, Name, List, Tuple
@property
def ctx(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `ctx`."""

    return self.a.ctx.f

@ctx.setter
def ctx(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'ctx')

@ctx.deleter
def ctx(self: 'fst.FST') -> None:
    self._put_one(None, None, 'ctx')


# Subscript
@property
def slice(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `slice`."""

    return self.a.slice.f

@slice.setter
def slice(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'slice')

@slice.deleter
def slice(self: 'fst.FST') -> None:
    self._put_one(None, None, 'slice')


# Name
@property
def id(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `id`."""

    return self.a.id

@id.setter
def id(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'id')

@id.deleter
def id(self: 'fst.FST') -> None:
    self._put_one(None, None, 'id')


# Slice
@property
def lower(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `lower`."""

    return child.f if (child := self.a.lower) else None

@lower.setter
def lower(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'lower')

@lower.deleter
def lower(self: 'fst.FST') -> None:
    self._put_one(None, None, 'lower')


# Slice
@property
def upper(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `upper`."""

    return child.f if (child := self.a.upper) else None

@upper.setter
def upper(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'upper')

@upper.deleter
def upper(self: 'fst.FST') -> None:
    self._put_one(None, None, 'upper')


# Slice
@property
def step(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `step`."""

    return child.f if (child := self.a.step) else None

@step.setter
def step(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'step')

@step.deleter
def step(self: 'fst.FST') -> None:
    self._put_one(None, None, 'step')


# comprehension, _comprehension_ifs
@property
def ifs(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `ifs`."""

    self.a.ifs  # noqa: B018

    return fstview(self, 'ifs')

@ifs.setter
def ifs(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'ifs')

@ifs.deleter
def ifs(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'ifs')


# comprehension
@property
def is_async(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `is_async`."""

    return self.a.is_async

@is_async.setter
def is_async(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'is_async')

@is_async.deleter
def is_async(self: 'fst.FST') -> None:
    self._put_one(None, None, 'is_async')


# ExceptHandler
@property
def type(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `type`."""

    return child.f if (child := self.a.type) else None

@type.setter
def type(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'type')

@type.deleter
def type(self: 'fst.FST') -> None:
    self._put_one(None, None, 'type')


# arguments
@property
def posonlyargs(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `posonlyargs`."""

    self.a.posonlyargs  # noqa: B018

    return fstview(self, 'posonlyargs')

@posonlyargs.setter
def posonlyargs(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'posonlyargs')

@posonlyargs.deleter
def posonlyargs(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'posonlyargs')


# arguments
@property
def defaults(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `defaults`."""

    self.a.defaults  # noqa: B018

    return fstview(self, 'defaults')

@defaults.setter
def defaults(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'defaults')

@defaults.deleter
def defaults(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'defaults')


# arguments
@property
def vararg(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `vararg`."""

    return child.f if (child := self.a.vararg) else None

@vararg.setter
def vararg(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'vararg')

@vararg.deleter
def vararg(self: 'fst.FST') -> None:
    self._put_one(None, None, 'vararg')


# arguments
@property
def kwonlyargs(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `kwonlyargs`."""

    self.a.kwonlyargs  # noqa: B018

    return fstview(self, 'kwonlyargs')

@kwonlyargs.setter
def kwonlyargs(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'kwonlyargs')

@kwonlyargs.deleter
def kwonlyargs(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'kwonlyargs')


# arguments
@property
def kw_defaults(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `kw_defaults`."""

    self.a.kw_defaults  # noqa: B018

    return fstview(self, 'kw_defaults')

@kw_defaults.setter
def kw_defaults(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'kw_defaults')

@kw_defaults.deleter
def kw_defaults(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'kw_defaults')


# arguments
@property
def kwarg(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `kwarg`."""

    return child.f if (child := self.a.kwarg) else None

@kwarg.setter
def kwarg(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'kwarg')

@kwarg.deleter
def kwarg(self: 'fst.FST') -> None:
    self._put_one(None, None, 'kwarg')


# arg, keyword
@property
def arg(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `arg`."""

    return self.a.arg

@arg.setter
def arg(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'arg')

@arg.deleter
def arg(self: 'fst.FST') -> None:
    self._put_one(None, None, 'arg')


# alias
@property
def asname(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `asname`."""

    return self.a.asname

@asname.setter
def asname(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'asname')

@asname.deleter
def asname(self: 'fst.FST') -> None:
    self._put_one(None, None, 'asname')


# withitem
@property
def context_expr(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `context_expr`."""

    return self.a.context_expr.f

@context_expr.setter
def context_expr(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'context_expr')

@context_expr.deleter
def context_expr(self: 'fst.FST') -> None:
    self._put_one(None, None, 'context_expr')


# withitem
@property
def optional_vars(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `optional_vars`."""

    return child.f if (child := self.a.optional_vars) else None

@optional_vars.setter
def optional_vars(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'optional_vars')

@optional_vars.deleter
def optional_vars(self: 'fst.FST') -> None:
    self._put_one(None, None, 'optional_vars')


# match_case, MatchAs
@property
def pattern(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `pattern`."""

    return child.f if (child := self.a.pattern) else None

@pattern.setter
def pattern(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'pattern')

@pattern.deleter
def pattern(self: 'fst.FST') -> None:
    self._put_one(None, None, 'pattern')


# match_case
@property
def guard(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `guard`."""

    return child.f if (child := self.a.guard) else None

@guard.setter
def guard(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'guard')

@guard.deleter
def guard(self: 'fst.FST') -> None:
    self._put_one(None, None, 'guard')


# MatchSequence, MatchMapping, MatchClass, MatchOr
@property
def patterns(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `patterns`."""

    self.a.patterns  # noqa: B018

    return fstview(self, 'patterns')

@patterns.setter
def patterns(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'patterns')

@patterns.deleter
def patterns(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'patterns')


# MatchMapping
@property
def rest(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `rest`."""

    return self.a.rest

@rest.setter
def rest(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'rest')

@rest.deleter
def rest(self: 'fst.FST') -> None:
    self._put_one(None, None, 'rest')


# MatchClass
@property
def cls(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `cls`."""

    return self.a.cls.f

@cls.setter
def cls(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'cls')

@cls.deleter
def cls(self: 'fst.FST') -> None:
    self._put_one(None, None, 'cls')


# MatchClass
@property
def kwd_attrs(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `kwd_attrs`."""

    self.a.kwd_attrs  # noqa: B018

    return fstview(self, 'kwd_attrs')

@kwd_attrs.setter
def kwd_attrs(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'kwd_attrs')

@kwd_attrs.deleter
def kwd_attrs(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'kwd_attrs')


# MatchClass
@property
def kwd_patterns(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `kwd_patterns`."""

    self.a.kwd_patterns  # noqa: B018

    return fstview(self, 'kwd_patterns')

@kwd_patterns.setter
def kwd_patterns(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'kwd_patterns')

@kwd_patterns.deleter
def kwd_patterns(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'kwd_patterns')


# TypeIgnore
@property
def tag(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `tag`."""

    return self.a.tag

@tag.setter
def tag(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'tag')

@tag.deleter
def tag(self: 'fst.FST') -> None:
    self._put_one(None, None, 'tag')


# TypeVar
@property
def bound(self: 'fst.FST') -> Union['fst.FST', None, constant]:
    """`FST` accessor for `AST` field `bound`."""

    return child.f if (child := self.a.bound) else None

@bound.setter
def bound(self: 'fst.FST', code: Code | constant | None) -> None:
    self._put_one(code, None, 'bound')

@bound.deleter
def bound(self: 'fst.FST') -> None:
    self._put_one(None, None, 'bound')


# TypeVar, ParamSpec, TypeVarTuple
if PYGE13:
    @property
    def default_value(self: 'fst.FST') -> Union['fst.FST', None, constant]:
        """`FST` accessor for `AST` field `default_value`."""

        return child.f if (child := self.a.default_value) else None

    @default_value.setter
    def default_value(self: 'fst.FST', code: Code | constant | None) -> None:
        self._put_one(code, None, 'default_value')

    @default_value.deleter
    def default_value(self: 'fst.FST') -> None:
        self._put_one(None, None, 'default_value')

else:  # safely access nonexistent field
    @property
    def default_value(self: 'fst.FST') -> Union['fst.FST', None, constant]:
        """`FST` accessor for `AST` field `default_value`."""

        return None

    @default_value.setter
    def default_value(self: 'fst.FST', code: Code | constant | None) -> None:
        if code is not None:  # maybe fail successfully
            raise RuntimeError("field 'default_value' does not exist on python < 3.13")

    @default_value.deleter
    def default_value(self: 'fst.FST') -> None:
        pass


# _arglikes
@property
def arglikes(self: 'fst.FST') -> fstview:
    """`FST` accessor for `AST` field `arglikes`."""

    self.a.arglikes  # noqa: B018

    return fstview(self, 'arglikes')

@arglikes.setter
def arglikes(self: 'fst.FST', code: Code | None) -> None:
    self._put_slice(code, 0, 'end', 'arglikes')

@arglikes.deleter
def arglikes(self: 'fst.FST') -> None:
    self._put_slice(None, 0, 'end', 'arglikes')
