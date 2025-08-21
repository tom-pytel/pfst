"""Standalone AST utilities."""

import re
from array import array
from ast import iter_fields, walk
from itertools import chain
from keyword import iskeyword as keyword_iskeyword
from types import  EllipsisType, NoneType
from typing import Any, Callable, Iterable, Iterator, Literal
from enum import IntEnum, auto

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
    expr,
    expr_context,
    keyword,
    match_case,
    operator,
    pattern,
    type_ignore,
    unaryop,
    withitem,
    TryStar,
    TypeAlias,
    TypeVar,
    ParamSpec,
    TypeVarTuple,
    TemplateStr,
    Interpolation,
)

__all__ = [
    'bistr', 'constant',
    'is_valid_identifier', 'is_valid_identifier_dotted', 'is_valid_identifier_star', 'is_valid_identifier_alias',
    'is_valid_MatchSingleton_value', 'is_valid_MatchValue_value', 'is_valid_MatchMapping_key',
    'is_valid_target', 'is_valid_del_target',
    'reduce_ast', 'get_field', 'set_field', 'has_type_comments', 'is_parsable', 'get_parse_mode',
    'WalkFail', 'walk2', 'compare_asts', 'copy_attributes', 'copy_ast', 'set_ctx',
    'get_func_class_or_ass_by_name', 'syntax_ordered_children', 'last_block_header_child', 'is_atom',
    'precedence_require_parens_by_type', 'precedence_require_parens',
]

from_iterable = chain.from_iterable


class bistr(str):
    """Byte-indexed string, easy mapping between character and encoded byte index (including 1 past last valid unit).
    Only positive indices."""

    _c2b: array  # character to byte indices
    _b2c: array  # byte to character indices

    _i2i_same = lambda idx: idx

    @property
    def lenbytes(self) -> int:
        """Length of encoded string in bytes."""

        return self.c2b(len(self))

    def __new__(cls, s: str) -> 'bistr':
        return s if isinstance(s, bistr) else str.__new__(cls, s)

    @staticmethod
    def _make_array(len_array: int, highest_value: int) -> array:
        if highest_value < 0x100:
            return array('B', b'\x00' * (len_array + 1))
        if highest_value < 0x10000:
            return array('H', b'\x00\x00' * (len_array + 1))
        if highest_value < 0x100000000:
            return array('I', b'\x00\x00\x00\x00' * (len_array + 1))

        return array('Q', b'\x00\x00\x00\x00\x00\x00\x00\x00' * (len_array + 1))

    def _c2b_lookup(self, idx: int) -> int:
        return self._c2b[idx]

    def c2b(self, idx: int) -> int:
        """Character to encoded byte index, [0..len(str)] inclusive."""

        if (lc := len(self)) == (lb := len(self.encode())):
            self.c2b = self.b2c = bistr._i2i_same

            return idx

        c2b = self._c2b = self._make_array(lc, lb)
        j   = 0

        for i, c in enumerate(self):
            c2b[i]  = j
            j      += len(c.encode())

        c2b[-1]  = j
        self.c2b = self._c2b_lookup

        return c2b[idx]

    def _b2c_lookup(self, idx: int) -> int:
        return self._b2c[idx]

    def b2c(self, idx: int) -> int:
        """Encoded byte to character index, [0..len(str.encode())] inclusive. Indices inside encoded characters are
        mapped to the beginning of the character."""

        if (lb := self.c2b(lc := len(self))) == lc:
            return idx  # no chars > '\x7f' so funcs are `_i2i_same` identity

        b2c = self._b2c = self._make_array(lb, lc)

        for i, j in enumerate(self._c2b):
            b2c[j] = i

        k = 0

        for i, j in enumerate(b2c):  # set off-boundary utf8 byte indices for safety
            if j:
                k = j
            else:
                b2c[i] = k

        self.b2c = self._b2c_lookup

        return b2c[idx]

    def clear_cache(self) -> None:
        """Remove the lookup array (if need to save some memory)."""

        try:
            del self.c2b, self._c2b
        except AttributeError:
            pass

        try:
            del self.b2c, self._b2c
        except AttributeError:
            pass


constant = EllipsisType | int | float | complex | str | bytes | bool | None

pat_alnum                  = r'\w\uFE00-\uFE0F\U000E0100-\U000E01EF'

re_alnum                   = re.compile(r'[\w\uFE00-\uFE0F\U000E0100-\U000E01EF]')
re_alnumdot                = re.compile(r'[\w\uFE00-\uFE0F\U000E0100-\U000E01EF.]')
re_alnumdot_alnum          = re.compile(r'[\w\uFE00-\uFE0F\U000E0100-\U000E01EF.][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]')

re_identifier              = re.compile(r'[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*')  # some other weird unicode crap accepted by python but no, just no
re_identifier_only         = re.compile(r'^[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*$')
re_identifier_dotted       = re.compile(r'[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*(?:\.[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*)*')
re_identifier_dotted_only  = re.compile(r'^[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*(?:\.[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*)*$')
re_identifier_or_star      = re.compile(r'(?:\*|[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*)')
re_identifier_or_star_only = re.compile(r'^(?:\*|[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*)$')
re_identifier_alias        = re.compile(r'(?:\*|[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*(?:\.[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*)*)')
re_identifier_alias_only   = re.compile(r'^(?:\*|[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*(?:\.[^\d\W][\w\uFE00-\uFE0F\U000E0100-\U000E01EF]*)*)$')

# Mostly in syntax order except a few special cases:
#   BoolOp        - multiple simultaneous locations possible for single `op`
#   Dict          - interleaved `keys` and `values`
#   Compare       - interleaved `ops` and `comparators`
#   MatchMapping  - interleaved `keys` and `patterns`
#   arguments     - interleaved `posonlyargs`/`args` and `defaults` (partially), interleaved `kwonlyargs` and `kw_defaults`
#   Call          - type `Starred` can be in `args`, `arg=None` in `keywords` means double starred

FIELDS = dict([
    (Module,             (('body', 'stmt*'), ('type_ignores', 'type_ignore*'))),
    (Interactive,        (('body', 'stmt*'),)),
    (Expression,         (('body', 'expr'),)),
    (FunctionType,       (('argtypes', 'expr*'), ('returns', 'expr'))),
    (FunctionDef,        (('decorator_list', 'expr*'), ('name', 'identifier'), ('type_params', 'type_param*'), ('args', 'arguments'), ('returns', 'expr?'), ('body', 'stmt*'), ('type_comment', 'string?'))),
    (AsyncFunctionDef,   (('decorator_list', 'expr*'), ('name', 'identifier'), ('type_params', 'type_param*'), ('args', 'arguments'), ('returns', 'expr?'), ('body', 'stmt*'), ('type_comment', 'string?'))),
    (ClassDef,           (('decorator_list', 'expr*'), ('name', 'identifier'), ('type_params', 'type_param*'), ('bases', 'expr*'), ('keywords', 'keyword*'), ('body', 'stmt*'))),
    (Return,             (('value', 'expr?'),)),
    (Delete,             (('targets', 'expr*'),)),
    (Assign,             (('targets', 'expr*'), ('value', 'expr'), ('type_comment', 'string?'))),
    (TypeAlias,          (('name', 'expr'), ('type_params', 'type_param*'), ('value', 'expr'))),
    (AugAssign,          (('target', 'expr'), ('op', 'operator'), ('value', 'expr'))),
    (AnnAssign,          (('target', 'expr'), ('annotation', 'expr'), ('value', 'expr?'), ('simple', 'int'))),
    (For,                (('target', 'expr'), ('iter', 'expr'), ('body', 'stmt*'), ('orelse', 'stmt*'), ('type_comment', 'string?'))),
    (AsyncFor,           (('target', 'expr'), ('iter', 'expr'), ('body', 'stmt*'), ('orelse', 'stmt*'), ('type_comment', 'string?'))),
    (While,              (('test', 'expr'), ('body', 'stmt*'), ('orelse', 'stmt*'))),
    (If,                 (('test', 'expr'), ('body', 'stmt*'), ('orelse', 'stmt*'))),
    (With,               (('items', 'withitem*'), ('body', 'stmt*'), ('type_comment', 'string?'))),
    (AsyncWith,          (('items', 'withitem*'), ('body', 'stmt*'), ('type_comment', 'string?'))),
    (Match,              (('subject', 'expr'), ('cases', 'match_case*'))),
    (Raise,              (('exc', 'expr?'), ('cause', 'expr?'))),
    (Try,                (('body', 'stmt*'), ('handlers', 'excepthandler*'), ('orelse', 'stmt*'), ('finalbody', 'stmt*'))),
    (TryStar,            (('body', 'stmt*'), ('handlers', 'excepthandler*'), ('orelse', 'stmt*'), ('finalbody', 'stmt*'))),
    (Assert,             (('test', 'expr'), ('msg', 'expr?'))),
    (Import,             (('names', 'alias*'),)),
    (ImportFrom,         (('module', 'identifier?'), ('names', 'alias*'), ('level', 'int?'))),
    (Global,             (('names', 'identifier*'),)),
    (Nonlocal,           (('names', 'identifier*'),)),
    (Expr,               (('value', 'expr'),)),
    (Pass,               ()),
    (Break,              ()),
    (Continue,           ()),

    (BoolOp,             (('op', 'boolop'), ('values', 'expr*'))),
    (NamedExpr,          (('target', 'expr'), ('value', 'expr'))),
    (BinOp,              (('left', 'expr'), ('op', 'operator'), ('right', 'expr'))),
    (UnaryOp,            (('op', 'unaryop'), ('operand', 'expr'))),
    (Lambda,             (('args', 'arguments'), ('body', 'expr'))),
    (IfExp,              (('body', 'expr'), ('test', 'expr'), ('orelse', 'expr'))),
    (Dict,               (('keys', 'expr*'), ('values', 'expr*'))),
    (Set,                (('elts', 'expr*'),)),
    (ListComp,           (('elt', 'expr'), ('generators', 'comprehension*'))),
    (SetComp,            (('elt', 'expr'), ('generators', 'comprehension*'))),
    (DictComp,           (('key', 'expr'), ('value', 'expr'), ('generators', 'comprehension*'))),
    (GeneratorExp,       (('elt', 'expr'), ('generators', 'comprehension*'))),
    (Await,              (('value', 'expr'),)),
    (Yield,              (('value', 'expr?'),)),
    (YieldFrom,          (('value', 'expr'),)),
    (Compare,            (('left', 'expr'), ('ops', 'cmpop*'), ('comparators', 'expr*'))),
    (Call,               (('func', 'expr'), ('args', 'expr*'), ('keywords', 'keyword*'))),
    (FormattedValue,     (('value', 'expr'), ('conversion', 'int'), ('format_spec', 'expr?'))),
    (Interpolation,      (('value', 'expr'), ('str', 'constant'), ('conversion', 'int'), ('format_spec', 'expr?'))),
    (JoinedStr,          (('values', 'expr*'),)),
    (TemplateStr,        (('values', 'expr*'),)),
    (Constant,           (('value', 'constant'), ('kind', 'string?'))),
    (Attribute,          (('value', 'expr'), ('attr', 'identifier'), ('ctx', 'expr_context'))),
    (Subscript,          (('value', 'expr'), ('slice', 'expr'), ('ctx', 'expr_context'))),
    (Starred,            (('value', 'expr'), ('ctx', 'expr_context'))),
    (Name,               (('id', 'identifier'), ('ctx', 'expr_context'))),
    (List,               (('elts', 'expr*'), ('ctx', 'expr_context'))),
    (Tuple,              (('elts', 'expr*'), ('ctx', 'expr_context'))),
    (Slice,              (('lower', 'expr?'), ('upper', 'expr?'), ('step', 'expr?'))),

    (Load,               ()),
    (Store,              ()),
    (Del,                ()),
    (And,                ()),
    (Or,                 ()),
    (Add,                ()),
    (Sub,                ()),
    (Mult,               ()),
    (MatMult,            ()),
    (Div,                ()),
    (Mod,                ()),
    (Pow,                ()),
    (LShift,             ()),
    (RShift,             ()),
    (BitOr,              ()),
    (BitXor,             ()),
    (BitAnd,             ()),
    (FloorDiv,           ()),
    (Invert,             ()),
    (Not,                ()),
    (UAdd,               ()),
    (USub,               ()),
    (Eq,                 ()),
    (NotEq,              ()),
    (Lt,                 ()),
    (LtE,                ()),
    (Gt,                 ()),
    (GtE,                ()),
    (Is,                 ()),
    (IsNot,              ()),
    (In,                 ()),
    (NotIn,              ()),

    (comprehension,      (('target', 'expr'), ('iter', 'expr'), ('ifs', 'expr*'), ('is_async', 'int'))),

    (ExceptHandler,      (('type', 'expr?'), ('name', 'identifier?'), ('body', 'stmt*'))),

    (arguments,          (('posonlyargs', 'arg*'), ('args', 'arg*'), ('defaults', 'expr*'), ('vararg', 'arg?'), ('kwonlyargs', 'arg*'), ('kw_defaults', 'expr*'), ('kwarg', 'arg?'))),
    (arg,                (('arg', 'identifier'), ('annotation', 'expr?'), ('type_comment', 'string?'))),
    (keyword,            (('arg', 'identifier?'), ('value', 'expr'))),
    (alias,              (('name', 'identifier'), ('asname', 'identifier?'))),
    (withitem,           (('context_expr', 'expr'), ('optional_vars', 'expr?'))),
    (match_case,         (('pattern', 'pattern'), ('guard', 'expr?'), ('body', 'stmt*'))),

    (MatchValue,         (('value', 'expr'),)),
    (MatchSingleton,     (('value', 'constant'),)),
    (MatchSequence,      (('patterns', 'pattern*'),)),
    (MatchMapping,       (('keys', 'expr*'), ('patterns', 'pattern*'), ('rest', 'identifier?'))),
    (MatchClass,         (('cls', 'expr'), ('patterns', 'pattern*'), ('kwd_attrs', 'identifier*'), ('kwd_patterns', 'pattern*'))),
    (MatchStar,          (('name', 'identifier?'),)),
    (MatchAs,            (('pattern', 'pattern?'), ('name', 'identifier?'))),
    (MatchOr,            (('patterns', 'pattern*'),)),

    (TypeIgnore,         (('lineno', 'int'), ('tag', 'string'))),

    (TypeVar,            (('name', 'identifier'), ('bound', 'expr?'), ('default_value', 'expr?'))),
    (ParamSpec,          (('name', 'identifier'), ('default_value', 'expr?'))),
    (TypeVarTuple,       (('name', 'identifier'), ('default_value', 'expr?'))),
])  ; """List of all fields for AST classes: [(`AST` class, (('field name', 'type name'), ...)), ...]"""

# only fields which can contain an AST, {cls: ('field1', 'field2', ...), ...}
AST_FIELDS = {cls: tuple(f for f, t in fields
                         if not t.startswith('int') and not t.startswith('string') and
                         not t.startswith('identifier') and not t.startswith('constant') and
                         not t.startswith('type_ignore'))
              for cls, fields in FIELDS.items()}  ; """Mapping of `AST` class to tuple of fields which may contain an `AST` node or `list` of `AST` nodes or `None` if optional `AST` node."""

OPSTR2CLS_UNARY = {
    '~':      Invert,
    'not':    Not,
    '+':      UAdd,
    '-':      USub,
}  ; """String to `unaryop` unary operator `AST` class mapping, e.g. `'+': ast.UAdd`."""

OPSTR2CLS_BIN = {
    '+':      Add,
    '-':      Sub,
    '*':      Mult,
    '@':      MatMult,
    '/':      Div,
    '%':      Mod,
    '<<':     LShift,
    '>>':     RShift,
    '|':      BitOr,
    '^':      BitXor,
    '&':      BitAnd,
    '//':     FloorDiv,
    '**':     Pow,
}  ; """String (non-augmented) to `operator` binary operator `AST` class mapping, e.g. `'+': ast.Add`."""

OPSTR2CLS_CMP = {
    '==':     Eq,
    '!=':     NotEq,
    '<':      Lt,
    '<=':     LtE,
    '>':      Gt,
    '>=':     GtE,
    'is':     Is,
    'is not': IsNot,
    'in':     In,
    'not in': NotIn,
}  ; "String to `cmpop` compare operator `AST` class mapping, e.g. `'==': ast.Eq`."""

OPSTR2CLS_BOOL = {
    'and':    And,
    'or':     Or,
}  ; "String to `boolop` boolean operator `AST` class mapping, e.g. `'and': ast.And`."""

OPSTR2CLS_AUG = {
    '+=':     Add,
    '-=':     Sub,
    '*=':     Mult,
    '@=':     MatMult,
    '/=':     Div,
    '%=':     Mod,
    '<<=':    LShift,
    '>>=':    RShift,
    '|=':     BitOr,
    '^=':     BitXor,
    '&=':     BitAnd,
    '//=':    FloorDiv,
    '**=':    Pow,
}  ; """String (augmented) to `operator` binary operator `AST` class mapping, e.g. `'+=': ast.Add`."""

OPSTR2CLS     = {**OPSTR2CLS_UNARY, **OPSTR2CLS_BIN, **OPSTR2CLS_CMP, **OPSTR2CLS_BOOL}                                ; """Mapping of operator string to operator `AST` class, e.g. `'+': ast.Add`. Unary `'-'` and `'+'` are overridden by the binary versions."""
OPSTR2CLSWAUG = {**OPSTR2CLS, **OPSTR2CLS}                                                                             ; """Mapping of all operator strings to operator `AST` class including AugAssign operators."""
OPCLS2STR     = {v: k for d in (OPSTR2CLS_UNARY, OPSTR2CLS_BIN, OPSTR2CLS_CMP, OPSTR2CLS_BOOL) for k, v in d.items()}  ; """Mapping of operator `AST` class to operator string, e.g. `ast.Add: '+'`."""
OPCLS2STR_AUG = {v: k for k, v in OPSTR2CLS_AUG.items()}                                                               ; """Mapping of operator `AST` class to operator string mapping to augmented operator strings, e.g. `ast.Add: '+='`."""


def is_valid_identifier(s: str) -> bool:
    """Check if `s` is a valid python identifier."""

    return (re_identifier_only.match(s) or False) and not keyword_iskeyword(s)


def is_valid_identifier_dotted(s: str) -> bool:
    """Check if `s` is a valid python dotted identifier (for modules)."""

    return (re_identifier_dotted_only.match(s) or False) and not keyword_iskeyword(s)


def is_valid_identifier_star(s: str) -> bool:
    """Check if `s` is a valid python identifier or a star '*'."""

    return (re_identifier_or_star_only.match(s) or False) and not keyword_iskeyword(s)


def is_valid_identifier_alias(s: str) -> bool:
    """Check if `s` is a valid python dotted identifier or a star '*'."""

    return (re_identifier_alias_only.match(s) or False) and not keyword_iskeyword(s)


def is_valid_MatchSingleton_value(ast: AST) -> bool:
    """Check if `ast` is a valid `Constant` node for a `MatchSingleton.value` field."""

    return isinstance(ast, Constant) and ast.value in (True, False, None)


def is_valid_MatchValue_value(ast: AST, consts: tuple[type[constant]] = (str, bytes, int, float, complex)) -> bool:
    """Check if `ast` is a valid node for a `MatchValue.value` field."""

    if isinstance(ast, Attribute):
        while isinstance(ast := ast.value, Attribute):
            pass

        return isinstance(ast, Name)

    if isinstance(ast, UnaryOp):
        if not isinstance(ast.op, USub):
            return False

        ast = ast.operand

    if isinstance(ast, Constant):
        return ast.value.__class__ in consts  # because bool is int

    if isinstance(ast, BinOp):
        if isinstance(ast.op, (Add, Sub)) and isinstance(r := ast.right, Constant) and isinstance(r.value, complex):
            l = ast.left

            if isinstance(l, UnaryOp):
                if not isinstance(l.op, USub):
                    return False

                l = l.operand

            if isinstance(l, Constant) and isinstance(l.value, (int, float)):
                return True

    return False


def is_valid_MatchMapping_key(ast: AST) -> bool:
    """Check if `ast` is a valid node for a `MatchMapping.keys` field."""

    return is_valid_MatchValue_value(ast, (str, bytes, int, float, complex, bool, NoneType))


def is_valid_target(asts: AST | list[AST]) -> bool:
    """Check if `asts` is a valid target for `Assign` or `For` operations. Must be `Name`, `Attribute`, `Subscript`
    and / or possibly nested `Starred`, `Tuple` and `List`."""

    stack = [asts] if isinstance(asts, AST) else list(asts)

    while stack:
        if isinstance(a := stack.pop(), (Tuple, List)):
            stack.extend(a.elts)
        elif isinstance(a, Starred):
            stack.append(a.value)
        elif not isinstance(a, (Name, Attribute, Subscript)):
            return False

    return True


def is_valid_del_target(asts: AST | list[AST]) -> bool:
    """Check if `asts` is a valid target for `Delete` operations. Must be `Name`, `Attribute`, `Subscript` and / or
    possibly nested `Tuple` and `List`."""

    stack = [asts] if isinstance(asts, AST) else list(asts)

    while stack:
        if isinstance(a := stack.pop(), (Tuple, List)):
            stack.extend(a.elts)
        elif not isinstance(a, (Name, Attribute, Subscript)):
            return False

    return True


def reduce_ast(ast: AST, multi_mod: bool | type[Exception] = False, reduce_Expr: bool = True) -> AST | None:
    """Reduce a `mod` / `Expr` wrapped expression or single statement if possible, otherwise return original `AST`,
    `None` or raise.

    **Parameters:**
    - `ast`: `AST` to reduce.
    - `multi_mod`: If `ast` is a `mod` with not exactly one statements then:
        - `True`: Return it.
        - `False`: Return `None`.
        - `type[Exception]`: If an exception class is passed then will `raise multi_mod(error)`.
    - `reduce_Expr`: Whether to reduce a single `Expr` node and return its expression or not.
    """

    if isinstance(ast, (Module, Interactive)):
        if len(body := ast.body) == 1:
            ast = body[0]

            return ast.value if isinstance(ast, Expr) and reduce_Expr else ast

        elif multi_mod is False:
            return None
        elif multi_mod is not True:
            raise multi_mod('expecting single element')

    elif isinstance(ast, Expression):
        return ast.body
    elif isinstance(ast, Expr) and reduce_Expr:
        return ast.value

    return ast


def get_field(parent: AST, name: str, idx: int | None = None) -> AST:
    """Get child node at field `name` in the given `parent` optionally at the given index `idx`."""

    return getattr(parent, name) if idx is None else getattr(parent, name)[idx]


def set_field(parent: AST, child: AST | constant, name: str, idx: int | None = None) -> None:
    """Set child node at field `name` in the given `parent` optionally at the given index `idx` to `child`."""

    if idx is None:
        setattr(parent, name, child)
    else:
        getattr(parent, name)[idx] = child


def has_type_comments(ast: AST) -> bool:
    """Does it has type comments?"""

    for n in walk(ast):
        if getattr(n, 'type_comments', None) is not None:
            return True

    return False


def is_parsable(ast: AST) -> bool:
    """Really means if the AST is `unparse()`able and then re`parse()`able which will get it to this top level AST node
    surrounded by the appropriate `ast.mod`"""

    if not isinstance(ast, AST):
        return False

    if isinstance(ast, (
        expr_context, TypeIgnore, FormattedValue, Interpolation,  # Starred is inconsistent as source but should always unparse to something parsable
        ExceptHandler, Slice,
        unaryop, boolop, operator, cmpop,
        alias, arguments, comprehension, withitem, match_case, pattern, type_ignore,
        arg, keyword,
        TypeVar, ParamSpec, TypeVarTuple,  # py 3.12+
    )):
        return False

    if isinstance(ast, Tuple):  # tuple of slices used in indexing (like numpy)
        if any(isinstance(e, Slice) for e in ast.elts):
            return False

    return True


def get_parse_mode(ast: AST) -> Literal['exec', 'eval', 'single']:
    """Return the original `mode` string that is used to parse to this `mod`."""

    if isinstance(ast, Module):
        return 'exec'
    if isinstance(ast, Expression):
        return 'eval'
    if isinstance(ast, Interactive):
        return 'single'

    return None


class WalkFail(Exception):
    """Raised in `walk2()`, `compare_asts()` and `copy_attributes()` on compare failure."""

def walk2(ast1: AST, ast2: AST, cb_primitive: Callable[[Any, Any, str, int], bool] | None = None, *, ctx: bool = True,
          recurse: bool = True, skip1: set | frozenset | None = None, skip2: set | frozenset | None = None,
          ) -> Iterator[tuple[AST, AST]]:
    """Walk two asts simultaneously comparing along the way to ensure they have the same structure.

    **Parameters:**
    - `ast1`: First `AST` tree (redundant) to walk.
    - `ast2`: Second `AST` tree to walk.
    - `cb_primitive`: A function to call to compare primitive nodes which is called with the values of the nodes from
        tree1 and tree2 and the name and index of the field. It should return whether the values compare equal or not,
        or just `True` if they are being ignored for example.
    - `ctx`: Whether to compare `ctx` fields or not.
    - `recurse`: Whether recurse into children or not. With this as `False` it just becomes a compare of two individual
        `AST` nodes.
    - `skip1`: List of nodes in the first tree to skip, will skip the corresponding node in the second tree.
    - `skip2`: List of nodes in the second tree to skip, will skip the corresponding node in the first tree.

    **Returns:**
    - `Iterator`
    """

    if ast1.__class__ is not ast2.__class__:
        raise WalkFail(f"top level nodes differ in '{ast1.__class__.__qualname__}' vs. '{ast2.__class__.__qualname__}'")

    if skip1 is None:
        skip1 = ()

    if skip2 is None:
        skip2 = ()

    stack      = [(ast1, ast2)]
    next_stack = stack if recurse else []

    while stack:
        a1, a2 = stack.pop()

        if a1 in skip1 or a2 in skip2:
            continue

        yield a1, a2

        if ctx or not (hasattr(a1, 'ctx') or hasattr(a2, 'ctx')):
            fields1 = list(iter_fields(a1))
            fields2 = list(iter_fields(a2))
        else:
            fields1 = list((n, c) for n, c in iter_fields(a1) if n != 'ctx')
            fields2 = list((n, c) for n, c in iter_fields(a2) if n != 'ctx')

        if len(fields1) != len(fields2):
            raise WalkFail(f"number of fields differ in {a1.__class__.__qualname__}")

        for (name1, child1), (name2, child2) in zip(fields1, fields2, strict=True):
            if name1 != name2:
                raise WalkFail(f"field names differ in {a1.__class__.__qualname__}, '{name1}' vs. '{name2}'")

            if (is_ast := isinstance(child1, AST)) or isinstance(child1, list) or isinstance(child2, (AST, list)):
                if child1.__class__ is not child2.__class__:
                    # if not ctx and is_ast and isinstance(child1, expr_context) and isinstance(child2, expr_context):
                    #     continue

                    locs = (f"{(getattr(child1, 'lineno', '?'), getattr(child1, 'col_offset', '?'), getattr(child1, 'end_lineno', '?'), getattr(child1, 'end_col_offset', '?'))} / "
                            f"{(getattr(child2, 'lineno', '?'), getattr(child2, 'col_offset', '?'), getattr(child2, 'end_lineno', '?'), getattr(child2, 'end_col_offset', '?'))}")

                    raise WalkFail(f"child classes differ in {a1.__class__.__qualname__}.{name1}, "
                                   f"{child1.__class__.__qualname__} vs. {child2.__class__.__qualname__}, locs {locs}")

                if is_ast:
                    stack.append((child1, child2))

                elif len(child1) != len(child2):
                    locs = (f"{(getattr(a1, 'lineno', '?'), getattr(a1, 'col_offset', '?'), getattr(a1, 'end_lineno', '?'), getattr(a1, 'end_col_offset', '?'))} / "
                            f"{(getattr(a2, 'lineno', '?'), getattr(a2, 'col_offset', '?'), getattr(a2, 'end_lineno', '?'), getattr(a2, 'end_col_offset', '?'))}")

                    raise WalkFail(f"child list lengths differ in {a1.__class__.__qualname__}.{name1}, "
                                   f"{len(child1)} vs. {len(child2)}, locs {locs}")

                else:
                    for i, (c1, c2) in enumerate(zip(child1, child2, strict=True)):
                        if (is_ast1 := isinstance(c1, AST)) and c1 in skip1:
                            continue

                        if (is_ast2 := isinstance(c2, AST)) and c2 in skip2:
                            continue

                        if is_ast1 != is_ast2:
                            locs = (f"{(getattr(c1, 'lineno', '?'), getattr(c1, 'col_offset', '?'), getattr(c1, 'end_lineno', '?'), getattr(c1, 'end_col_offset', '?'))} / "
                                    f"{(getattr(c2, 'lineno', '?'), getattr(c2, 'col_offset', '?'), getattr(c2, 'end_lineno', '?'), getattr(c2, 'end_col_offset', '?'))}")

                            raise WalkFail(f"child elements differ in {a1.__class__.__qualname__}.{name1}[{i}], "
                                           f"{c1.__class__.__qualname__} vs. {c2.__class__.__qualname__}, locs {locs}")

                        if is_ast1:
                            if c1.__class__ is not c2.__class__:
                                locs = (f"{(getattr(c1, 'lineno', '?'), getattr(c1, 'col_offset', '?'), getattr(c1, 'end_lineno', '?'), getattr(c1, 'end_col_offset', '?'))} / "
                                        f"{(getattr(c2, 'lineno', '?'), getattr(c2, 'col_offset', '?'), getattr(c2, 'end_lineno', '?'), getattr(c2, 'end_col_offset', '?'))}")

                                raise WalkFail(f"child element classes differ in {a1.__class__.__qualname__}.{name1}[{i}], "
                                               f"{c1.__class__.__qualname__} vs. {c2.__class__.__qualname__}, locs {locs}")

                            stack.append((c1, c2))

                        elif cb_primitive and cb_primitive(c1, c2, name1, i) is False:
                            locs = (f"{(getattr(a1, 'lineno', '?'), getattr(a1, 'col_offset', '?'), getattr(a1, 'end_lineno', '?'), getattr(a1, 'end_col_offset', '?'))} / "
                                    f"{(getattr(a2, 'lineno', '?'), getattr(a2, 'col_offset', '?'), getattr(a2, 'end_lineno', '?'), getattr(a2, 'end_col_offset', '?'))}")

                            raise WalkFail(f"primitives differ in {a1.__class__.__qualname__}.{name1}[{i}], "
                                           f"{c1!r} vs. {c2!r}, locs {locs}")

            elif cb_primitive and cb_primitive(child1, child2, name1, None) is False:
                locs = (f"{(getattr(a1, 'lineno', '?'), getattr(a1, 'col_offset', '?'), getattr(a1, 'end_lineno', '?'), getattr(a1, 'end_col_offset', '?'))} / "
                        f"{(getattr(a2, 'lineno', '?'), getattr(a2, 'col_offset', '?'), getattr(a2, 'end_lineno', '?'), getattr(a2, 'end_col_offset', '?'))}")

                raise WalkFail(f"primitives differ in {a1.__class__.__qualname__}.{name1}, "
                               f"{child1!r} vs. {child2!r}, locs {locs}")

        stack = next_stack


_compare_primitive_type_comments_func = (
    (lambda p1, p2, n, i: n == 'type_comment' or (p1.__class__ is p2.__class__ and p1 == p2)),
    (lambda p1, p2, n, i: p1.__class__ is p2.__class__ and p1 == p2),
)

def compare_asts(ast1: AST, ast2: AST, *, locs: bool = False, ctx: bool = True, type_comments: bool = False,
                 recurse: bool = True, skip1: set | frozenset | None = None, skip2: set | frozenset | None = None,
                 cb_primitive: Callable[[Any, Any, str, int], bool] | None = None, raise_: bool = False) -> bool:
    """Compare two trees including possibly locations and type comments using `walk2()`.

    **Parameters:**
    - `ast1`: First `AST` tree (redundant) to compare.
    - `ast2`: Second `AST` tree to compare.
    - `locs`: Whether to compare location attributes or not (`lineno`, `col_offset`, etc...).
    - `ctx`: Whether to compare `ctx` nodes or not.
    - `type_comments`: Whether to compare type comments or not. Ignored if `cb_primitive` provided.
    - `skip1`: List of nodes in the first tree to skip comparing, will skip the corresponding node in the second tree.
    - `skip2`: List of nodes in the second tree to skip comparing, will skip the corresponding node in the first tree.
    - `cb_primitive`: Callback for comparing primitives. Is called with `cb_primitive(val1, val2, field, idx)` and
        should return `True` if the two primitives compare same or not. Used to make certain fields always compare same.
    - `raise_`: Whether to raise `WalkFail` on compare fail or just return `False`.

    **Returns:**
    - `bool`: Indicating if the two trees compare equal under given parameters (if return on error allowed by `raise_`).
    """

    if cb_primitive is None:
        cb_primitive = _compare_primitive_type_comments_func[bool(type_comments)]

    try:
        for n1, n2 in walk2(ast1, ast2, cb_primitive, ctx=ctx, recurse=recurse, skip1=skip1, skip2=skip2):
            if locs:
                if (getattr(n1, 'lineno', None) != getattr(n2, 'lineno', None) or
                    getattr(n1, 'col_offset', None) != getattr(n2, 'col_offset', None) or
                    getattr(n1, 'end_lineno', None) != getattr(n2, 'end_lineno', None) or
                    getattr(n1, 'end_col_offset', None) != getattr(n2, 'end_col_offset', None)
                ):
                    raise WalkFail(f"locations differ in '{n1.__class__.__qualname__}', "
                                   f"{(n1.lineno, n1.col_offset, n1.end_lineno, n1.end_col_offset)} vs. "
                                   f"{(n2.lineno, n2.col_offset, n2.end_lineno, n2.end_col_offset)}")

    except WalkFail:
        if raise_:
            raise

        return False

    return True


def copy_attributes(src: AST, dst: AST, *, compare: bool = True, type_comments: bool = False,
                    recurse: bool = True, skip1: set | frozenset | None = None, skip2: set | frozenset | None = None,
                    raise_: bool = True) -> bool:
    """Copy attributes from one tree to another using `walk2()` to walk them both simultaneously and this checking
    structure equality in the process. By "attributes" we mean everything specified in `src._attributes`.

    **Parameters:**
    - `src`: Source `AST` tree to copy attributes from.
    - `dst`: Destination `AST` tree to copy attributes to.
    - `recurse`: Whether recurse into children or not. With this as `False` it just becomes a copy of attributes from one
        `AST` node to another.
    - `skip1`: List of nodes in the source tree to skip.
    - `skip2`: List of nodes in the destination tree to skip.
    - `raise_`: Whether to raise `WalkFail` on compare fail or just return `False`.

    **Returns:**
    - `bool`: Indicating if the two trees compare equal during the walk (if return on error allowed by `raise_`).
    """

    cb_primitive = _compare_primitive_type_comments_func[bool(type_comments)] if compare else lambda p1, p2, n, i: True

    try:
        for ns, nd in walk2(src, dst, cb_primitive, recurse=recurse, skip1=skip1, skip2=skip2):
            for attr in ns._attributes:
                if (val := getattr(ns, attr, cb_primitive)) is not cb_primitive:
                    setattr(nd, attr, val)
                elif hasattr(nd, attr):
                    delattr(nd, attr)

    except WalkFail:
        if raise_:
            raise

        return False

    return True


def copy_ast(ast: AST | None) -> AST | None:
    """Copy a whole tree."""

    if ast is None:
        return None

    params = {}

    for field in ast._fields:
        child = getattr(ast, field)

        if isinstance(child, AST):
            params[field] = copy_ast(child)
        elif isinstance(child, list):
            params[field] = [copy_ast(c) if isinstance(c, AST) else c for c in child]
        else:
            params[field] = child

    ret = ast.__class__(**params)

    for attr in ast._attributes:
        if (val := getattr(ast, attr, ret)) is not ret:
            setattr(ret, attr, val)

    return ret


def set_ctx(asts: AST | list[AST], ctx: type[expr_context], *, doit: bool = True) -> bool:
    """Set all `ctx` fields in this node and any children which may participate in an assignment (`Tuple`, `List`,
    `Starred`, `Subscript`, `Attribute`, `Name`) to the passed `ctx` type.

    **WARNING!** This will not recurse into elements which have a `ctx` of the type being set.

    **Parameters:**
    - `asts`: Single `AST` (will be recursed) or list of `AST` nodes (will be consumed, each one will also be recursed)
        to process.
    - `ctx`: The `exprt_context` `AST` type to set. Any container encountered which matches this `ctx` will not be
        recursed.
    - `doit`: Whether to actually carry out the assignments or just analyze and return whethere there are candidate
        locations for assignment. `doit=False` used to query if any context-modifiable `ctx` present.

    **Returns:**
    - `bool`: Whether any modifications were made or can be made (if `doit=False`).
    """

    change = False
    stack  = [asts] if isinstance(asts, AST) else asts

    while stack:
        if a := stack.pop():  # might be `None`s in there
            if (((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
                isinstance(a, (Name, Subscript, Attribute))) and not isinstance(a.ctx, ctx)
            ):
                change = True

                if doit:
                    a.ctx = ctx()

                if is_seq:
                    stack.extend(a.elts)
                elif is_starred:
                    stack.append(a.value)

    return change


def get_func_class_or_ass_by_name(asts: Iterable[AST], name: str, ass: bool = True) -> AST | None:
    """Walk through an `Iterable` of `AST` nodes looking for the first `FunctionDef`, `AsyncFunctionDef`, `ClassDef` or
    optionally `Assign` or `AnnAssign` which has a `name` or `target` or any `targets` field matching `name`.

    **Parameters:**
    - `asts`: `Iterable` of `AST`s to search through, e.g. a `body` list.
    - `name`: Name to look for.
    - `ass`: A domesticated donkey: a sturdy, short-haired animal used as a beast of burden.

    **Returns:**
    - `AST` node if found matching, else `None`
    """

    for a in asts:
        if isinstance(a, (FunctionDef, AsyncFunctionDef, ClassDef)):
            if a.name == name:
                return a

        elif ass:
            if isinstance(a, Assign):
                if any(isinstance(t, Name) and t.id == name for t in a.targets):
                    return a

            elif isinstance(a, AnnAssign):
                if isinstance(t := a.target, Name) and t.id == name:
                    return a

    return None


def _syntax_ordered_children_Call(ast: AST) -> list[AST]:
    children = [ast.func]
    args     = ast.args
    keywords = ast.keywords

    if not args or not keywords or not isinstance(args[-1], Starred):
        children.extend(args)
        children.extend(keywords)

    else:
        star            = args[-1]
        star_lineno     = star.lineno
        star_col_offset = star.col_offset

        children.extend(args[:-1])

        for i, kw in enumerate(keywords):
            if (lineno := kw.lineno) < star_lineno or ((lineno == star_lineno) and kw.col_offset < star_col_offset):
                children.append(kw)

            else:
                children.append(star)
                children.extend(keywords[i:])

                break

        else:
            children.append(star)

    return children

def _syntax_ordered_children_arguments(ast: AST) -> list[AST]:
    children = []

    if not (defaults := ast.defaults):
        children.extend(ast.posonlyargs)
        children.extend(ast.args)

    elif (ldefaults := len(defaults)) <= (largs := len(args := ast.args)):
        children.extend(ast.posonlyargs)
        children.extend(args[:-ldefaults])
        children.extend(from_iterable(zip(args[-ldefaults:], defaults, strict=True)))

    else:
        children.extend((posonlyargs := ast.posonlyargs)[:-(lposonly_defaults := ldefaults - largs)])
        children.extend(from_iterable(zip(posonlyargs[-lposonly_defaults:], defaults[:lposonly_defaults], strict=True)))
        children.extend(from_iterable(zip(args, defaults[lposonly_defaults:], strict=True)))

    if (vararg := ast.vararg):
        children.append(vararg)

    if not (kw_defaults := ast.kw_defaults):
        children.extend(ast.kwonlyargs)
    else:
        children.extend(from_iterable(zip(ast.kwonlyargs, kw_defaults, strict=True)))

    if (kwarg := ast.kwarg):
        children.append(kwarg)

    return children

def _syntax_ordered_children_default(ast: AST) -> list[AST]:
    children = []

    for field in AST_FIELDS[ast.__class__]:
        if child := getattr(ast, field, None):
            if isinstance(child, list):
                children.extend(child)
            else:
                children.append(child)

    return children

_syntax_ordered_children_nothing      = lambda ast: []
_syntax_ordered_children_value        = lambda ast: [ast.value]
_syntax_ordered_children_elts         = lambda ast: ast.elts[:]
_syntax_ordered_children_elts_and_ctx = lambda ast: [*ast.elts, ast.ctx]
_syntax_ordered_children_ctx          = lambda ast: [ast.ctx]

_SYNTAX_ORDERED_CHILDREN = {
    # quick optimized get

    Return:       _syntax_ordered_children_value,
    Expr:         _syntax_ordered_children_value,
    Await:        _syntax_ordered_children_value,
    Yield:        _syntax_ordered_children_value,
    YieldFrom:    _syntax_ordered_children_value,

    Set:          _syntax_ordered_children_elts,
    List:         _syntax_ordered_children_elts_and_ctx,
    Tuple:        _syntax_ordered_children_elts_and_ctx,

    Name:         _syntax_ordered_children_ctx,

    Pass:         _syntax_ordered_children_nothing,
    Break:        _syntax_ordered_children_nothing,
    Continue:     _syntax_ordered_children_nothing,

    Constant:     _syntax_ordered_children_nothing,

    Load:         _syntax_ordered_children_nothing,
    Store:        _syntax_ordered_children_nothing,
    Del:          _syntax_ordered_children_nothing,
    And:          _syntax_ordered_children_nothing,
    Or:           _syntax_ordered_children_nothing,
    Add:          _syntax_ordered_children_nothing,
    Sub:          _syntax_ordered_children_nothing,
    Mult:         _syntax_ordered_children_nothing,
    MatMult:      _syntax_ordered_children_nothing,
    Div:          _syntax_ordered_children_nothing,
    Mod:          _syntax_ordered_children_nothing,
    Pow:          _syntax_ordered_children_nothing,
    LShift:       _syntax_ordered_children_nothing,
    RShift:       _syntax_ordered_children_nothing,
    BitOr:        _syntax_ordered_children_nothing,
    BitXor:       _syntax_ordered_children_nothing,
    BitAnd:       _syntax_ordered_children_nothing,
    FloorDiv:     _syntax_ordered_children_nothing,
    Invert:       _syntax_ordered_children_nothing,
    Not:          _syntax_ordered_children_nothing,
    UAdd:         _syntax_ordered_children_nothing,
    USub:         _syntax_ordered_children_nothing,
    Eq:           _syntax_ordered_children_nothing,
    NotEq:        _syntax_ordered_children_nothing,
    Lt:           _syntax_ordered_children_nothing,
    LtE:          _syntax_ordered_children_nothing,
    Gt:           _syntax_ordered_children_nothing,
    GtE:          _syntax_ordered_children_nothing,
    Is:           _syntax_ordered_children_nothing,
    IsNot:        _syntax_ordered_children_nothing,
    In:           _syntax_ordered_children_nothing,
    NotIn:        _syntax_ordered_children_nothing,

    # special cases

    Dict:         lambda ast: list(from_iterable(zip(ast.keys, ast.values, strict=True))),
    Compare:      lambda ast: [ast.left] + (list(from_iterable(zip(ops, ast.comparators, strict=True)))
                                            if len(ops := ast.ops) > 1 else [ops[0], ast.comparators[0]]),
    Call:         _syntax_ordered_children_Call,
    arguments:    _syntax_ordered_children_arguments,
    MatchMapping: lambda ast: list(from_iterable(zip(ast.keys, ast.patterns, strict=True))),
}

def syntax_ordered_children(ast: AST) -> list:
    """Get list of all `AST` children in syntax order. This will include individual fields and aggregate fields like
    `body` all smushed up together into a single flat list. The list may contain `None` values for example from a `Dict`
    `keys` field which has `**` elements."""

    return _SYNTAX_ORDERED_CHILDREN.get(ast.__class__, _syntax_ordered_children_default)(ast)


def last_block_header_child(ast: AST) -> AST | None:
    """Return last `AST` node in the block header before the ':'. Returns `None` for non-block nodes and things like
    `Try` and empty  `ExceptHandler` nodes or other block nodes which might have normally present fields missing."""

    if not isinstance(ast, (FunctionDef, AsyncFunctionDef, ClassDef, For, AsyncFor, While, If, With, AsyncWith, Match,
                            ExceptHandler, match_case)):  # Try, TryStar open blocks but don't have children
        return None

    for field in reversed(AST_FIELDS[ast.__class__]):
        if field in ('body', 'orelse', 'finalbody', 'handlers', 'cases') or not (child := getattr(ast, field, None)):
            continue

        if isinstance(child, AST):
            return child

        elif isinstance(child, list):
            if any(ret := a for a in reversed(child) if isinstance(a, AST)):
                return ret

    return None


def is_atom(ast: AST, *, unparse_pars_as_atom: bool | None = None, tuple_as_atom: bool | None = True,
            matchseq_as_atom: bool | None = True) -> bool | None:
    """Whether `ast` is enclosed in some kind of delimiters `'()'`, `'[]'`, `'{}'` when `unparse()`d or otherwise atomic
    like `Name`, `Constant`, etc... Node types where this doesn't normally apply like `stmt` will return `True`. `Tuple`
    and `MatchSequence` which can otherwise be ambiguous will normally return `True` as they `unparse()` with
    delimiters, but can be overridden.

    **Parameters:**
    - `ast`: Self-explanatory.
    - `unparse_pars_as_atom`: What to return for `NamedExpr`, `Yield` and `YieldFrom` node type as they `unparse()` with
        enclosing parentheses. Default `None` as falsey value but also distinguishes from `False`.
    - `tuple_as_atom`: What to return for `Tuple` as this always `unparse()`s with parentheses but these are not
        strictly required for a `Tuple`.
    - `matchseq_as_atom`: What to return for `MatchSequence` as this always `unparse()`s with brackets but these are not
        strictly required for a `MatchSequence`.

    **Returns:**
    - `True` if is enclosed and no combination with another node can change its precedence, `False` otherwise. Returns
        `unparse_pars_as_atom` value for `NamedExpr`, `Yield` and `YieldFrom`, `tuple_as_atom` value for `Tuple` and
        `matchseq_as_atom` for `MatchSequence` as those all are special cases.
    """

    if isinstance(ast, (Dict, Set, ListComp, SetComp, DictComp, GeneratorExp, Constant, Attribute, Subscript, Name,  # , Await
                        List, MatchValue, MatchSingleton, MatchMapping, MatchClass, MatchStar, MatchAs,
                        MatchSequence)):
        return True

    if isinstance(ast, Tuple):
        return tuple_as_atom

    if isinstance(ast, (NamedExpr, Yield, YieldFrom)):
        return unparse_pars_as_atom

    if isinstance(ast, MatchSequence):
        return matchseq_as_atom

    if isinstance(ast, (expr, pattern)):
        return False

    return True


# directly from python ast
class _Precedence(IntEnum):
    """Precedence table that originated from python grammar."""

    NAMED_EXPR = auto()  # <target> := <expr1>
    TUPLE = auto()       # <expr1>, <expr2>
    YIELD = auto()       # 'yield', 'yield from'
    TEST = auto()        # 'if'-'else', 'lambda'
    OR = auto()          # 'or'
    AND = auto()         # 'and'
    NOT = auto()         # 'not'
    CMP = auto()         # '<', '>', '==', '>=', '<=', '!=', 'in', 'not in', 'is', 'is not'
    EXPR = auto()
    BOR = EXPR           # '|'
    BXOR = auto()        # '^'
    BAND = auto()        # '&'
    SHIFT = auto()       # '<<', '>>'
    ARITH = auto()       # '+', '-'
    TERM = auto()        # '*', '@', '/', '%', '//'
    FACTOR = auto()      # unary '+', '-', '~'
    POWER = auto()       # '**'
    AWAIT = auto()       # 'await'
    ATOM = auto()

    def next(self) -> '_Precedence':
        try:
            return self.__class__(self + 1)
        except ValueError:
            return self

# Special precedence rules:
# * Unparenthesized tuple should always be parenthesized.
# * Value for dict unpack has _Precedence.EXPR.
# * BinOp, UnaryOp and BoolOp inherit precedence from `.op`.
# * BinOp addtionally has associativity to consider, opposite operand from associativity gets precedence bumped.

_PRECEDENCE_NODES = {  # default is _Precedence.ATOM
    BoolOp:         False,  # should be passed as the 'op'
    NamedExpr:      _Precedence.NAMED_EXPR,
    BinOp:          False,
    UnaryOp:        False,
    Lambda:         _Precedence.TEST,
    IfExp:          _Precedence.TEST,
    # Dict:           None,
    # Set:            None,
    # ListComp:       None,
    # SetComp:        None,
    # DictComp:       None,
    # GeneratorExp:   None,
    Await:          _Precedence.AWAIT,
    Yield:          _Precedence.YIELD,
    YieldFrom:      _Precedence.YIELD,
    Compare:        _Precedence.CMP,
    # Call:           None,
    # FormattedValue: None,
    # Interpolation:  None,
    # JoinedStr:      None,
    # TemplateStr:    None,
    # Constant:       None,
    # Attribute:      None,
    # Subscript:      None,
    # Starred:        None,
    # Name:           None,
    # List:           None,
    Tuple:          _Precedence.TUPLE,
    # Slice:          None,

    Invert:         _Precedence.FACTOR,
    Not:            _Precedence.NOT,
    UAdd:           _Precedence.FACTOR,
    USub:           _Precedence.FACTOR,

    Add:            _Precedence.ARITH,
    Sub:            _Precedence.ARITH,
    Mult:           _Precedence.TERM,
    MatMult:        _Precedence.TERM,
    Div:            _Precedence.TERM,
    Mod:            _Precedence.TERM,
    LShift:         _Precedence.SHIFT,
    RShift:         _Precedence.SHIFT,
    BitOr:          _Precedence.BOR,
    BitXor:         _Precedence.BXOR,
    BitAnd:         _Precedence.BAND,
    FloorDiv:       _Precedence.TERM,
    Pow:            _Precedence.POWER,

    # Eq:             None,
    # NotEq:          None,
    # Lt:             None,
    # LtE:            None,
    # Gt:             None,
    # GtE:            None,
    # Is:             None,
    # IsNot:          None,
    # In:             None,
    # NotIn:          None,

    And:            _Precedence.AND,
    Or:             _Precedence.OR,

    # comprehension:  None,

    # arguments:      None,
    # arg:            None,
    # keyword:        None,
    # alias:          None,
    # withitem:       None,
    # match_case:     None,

    # MatchValue:     None,
    # MatchSingleton: None,
    # MatchSequence:  None,
    # MatchMapping:   None,
    # MatchClass:     None,
    # MatchStar:      None,
    MatchAs:        True,             # special case precedence decided py presence or absence of `pattern`
    MatchOr:        _Precedence.BOR,

    # TypeIgnore:     None,

    # TypeVar:        None,
    # ParamSpec:      None,
    # TypeVarTuple:   None,
}

_PRECEDENCE_NODE_FIELDS = {  # default is _Precedence.TEST
    (Expr, 'value'):           _Precedence.YIELD,
    (Assign, 'targets'):       _Precedence.TUPLE,
    (For, 'target'):           _Precedence.TUPLE,
    (AsyncFor, 'target'):      _Precedence.TUPLE,

    (BinOp, 'values'):         False,                    # should be passed as the 'op'
    (NamedExpr, 'target'):     _Precedence.ATOM,
    (NamedExpr, 'value'):      _Precedence.TEST,         # XXX: python ast.unparse() has this as _Precedence.ATOM, which as far as I can tell is unnecessary
    (BinOp, 'left'):           False,                    # should be passed as the 'op'
    (BinOp, 'right'):          False,                    # should be passed as the 'op'
    (UnaryOp, 'operand'):      False,                    # should be passed as the 'op'
    (Lambda, 'body'):          _Precedence.TEST,
    (IfExp, 'body'):           _Precedence.TEST.next(),
    (IfExp, 'test'):           _Precedence.TEST.next(),
    (IfExp, 'orelse'):         _Precedence.TEST,
    (Dict, 'values'):          False,                    # special case, '**' dict unpack `.value` gets _Precedence.EXPR
    (Await, 'value'):          _Precedence.ATOM,
    (Yield, 'value'):          _Precedence.ATOM,
    (YieldFrom, 'value'):      _Precedence.ATOM,
    (Compare, 'left'):         _Precedence.CMP.next(),
    (Compare, 'comparators'):  _Precedence.CMP.next(),
    (Call, 'func'):            _Precedence.ATOM,
    (FormattedValue, 'value'): _Precedence.TEST.next(),
    (Interpolation, 'value'):  _Precedence.TEST.next(),
    (Attribute, 'value'):      False,                    # Constant integers require parentheses, e.g. '(1).bit_count()'
    (Subscript, 'value'):      _Precedence.ATOM,
    (Subscript, 'slice'):      False,                    # unparenthesized tuples put to slice don't need parens
    (Starred, 'value'):        False,                    # different precedence when Starred is a call argument

    (Invert, 'operand'):       _Precedence.FACTOR,
    (Not, 'operand'):          _Precedence.NOT,
    (UAdd, 'operand'):         _Precedence.FACTOR,
    (USub, 'operand'):         _Precedence.FACTOR,

    (Add, 'left'):             _Precedence.ARITH,
    (Sub, 'left'):             _Precedence.ARITH,
    (Mult, 'left'):            _Precedence.TERM,
    (MatMult, 'left'):         _Precedence.TERM,
    (Div, 'left'):             _Precedence.TERM,
    (Mod, 'left'):             _Precedence.TERM,
    (LShift, 'left'):          _Precedence.SHIFT,
    (RShift, 'left'):          _Precedence.SHIFT,
    (BitOr, 'left'):           _Precedence.BOR,
    (BitXor, 'left'):          _Precedence.BXOR,
    (BitAnd, 'left'):          _Precedence.BAND,
    (FloorDiv, 'left'):        _Precedence.TERM,
    (Pow, 'left'):             _Precedence.POWER.next(),

    (Add, 'right'):            _Precedence.ARITH.next(),
    (Sub, 'right'):            _Precedence.ARITH.next(),
    (Mult, 'right'):           _Precedence.TERM.next(),
    (MatMult, 'right'):        _Precedence.TERM.next(),
    (Div, 'right'):            _Precedence.TERM.next(),
    (Mod, 'right'):            _Precedence.TERM.next(),
    (LShift, 'right'):         _Precedence.SHIFT.next(),
    (RShift, 'right'):         _Precedence.SHIFT.next(),
    (BitOr, 'right'):          _Precedence.BOR.next(),
    (BitXor, 'right'):         _Precedence.BXOR.next(),
    (BitAnd, 'right'):         _Precedence.BAND.next(),
    (FloorDiv, 'right'):       _Precedence.TERM.next(),
    (Pow, 'right'):            _Precedence.POWER,

    (And, 'values'):           False,                    # special handling for BoolOp child
    (Or, 'values'):            False,                    # special handling for BoolOp child

    (comprehension, 'target'): _Precedence.TUPLE,
    (comprehension, 'iter'):   _Precedence.TEST.next(),
    (comprehension, 'ifs'):    _Precedence.TEST.next(),

    (MatchClass, 'cls'):       _Precedence.ATOM,
    (MatchAs, 'pattern'):      _Precedence.BOR,
    (MatchOr, 'patterns'):     _Precedence.BOR.next(),
}

def precedence_require_parens_by_type(child_type: type[AST], parent_type: type[AST], field: str,
                                      **flags: dict[str, bool]) -> bool:
    """Returns whether parentheses are required for the child for the given parent / child combination or not. Both
    parent and child `BoolOp`, `BinOp` and `UnaryOp` types should be passed as the type of the `op` field.

    **Parameters**:
    - `child_type`: Type of the child `AST` node or of its `op` field if it is a `BoolOp`, `BinOp` or `UnaryOp`.
    - `parent_type`: Type of the parent `AST` node or of its `op` field if it is a `BoolOp`, `BinOp` or `UnaryOp`.
    - `field`: The name of the field in the parent where the child resides.
    - `flags`: Special case flags, individual flags assumed `False` if not passed as `True`:
        - `dict_key_None`: Parent is `Dict` and the corresponding key is `None`, leading to `**value`. Only has effect
            if `field` is `'value'`, otherwise no effect.
        - `matchas_pat_None`: Child is `MatchAs` and the `pattern` is `None` (just a name).
        - `attr_val_int`: Parent is `Attribute` and child `value` is a `Constant` integer.
        - `star_call_arg`: Parent is `Starred` and it is a `Call` `args` argument, different rules for child
            parentheses.

    **Returns:**
    - `bool`: Whether parentheses are needed around the child for correct parsing or not.
    """

    child_precedence  = _PRECEDENCE_NODES.get(child_type, _Precedence.ATOM)
    parent_precedence = _PRECEDENCE_NODE_FIELDS.get((parent_type, field), _Precedence.TEST)

    assert child_precedence, "type of 'op' should be passed for 'BoolOp', 'BinOp' or 'UnaryOp'"

    if child_precedence is True:
        child_precedence = _Precedence.ATOM if flags.get('matchas_pat_None') else _Precedence.TEST

    if not parent_precedence:
        if parent_type is Dict:
            parent_precedence = _Precedence.EXPR if flags.get('dict_key_None') else _Precedence.TEST

        elif parent_type is Attribute:
            if flags.get('attr_val_int'):
                return True

            parent_precedence = _Precedence.ATOM

        elif parent_type is Subscript:
            parent_precedence = _Precedence.TUPLE if child_type is Tuple else _Precedence.TEST  # tuples in slice don't need parens

        elif parent_type is And:
            if child_type is And:
                return True

            parent_precedence = _Precedence.AND

        elif parent_type is Or:
            if child_type is Or:
                return True

            parent_precedence = _Precedence.OR

        elif parent_type is Starred:
            parent_precedence = _Precedence.TEST if flags.get('star_call_arg') else _Precedence.EXPR

        else:
            raise ValueError("type of 'op' should be passed")

    return child_precedence < parent_precedence

def precedence_require_parens(child: AST, parent: AST, field: str, idx: int | None = None, **flags: dict[str, bool],
                              ) -> bool:
    """Returns whether parentheses are required for the given parent / child combination or not. Unlike
    `precedence_require_parens_by_type()`, this takes the actual node instances and figures out the respective types
    and flags.

    **Parameters**:
    - `child`: Child `AST` node.
    - `parent`: Parent `AST` node.
    - `field`: The name of the field in the parent where the child resides.
    - `idx`: The optional index of the child in the parent field, or `None` if does not apply.
    - `flags`: Used to passed in some flags that cannot be determined here, specifically `star_call_arg`.

    **Returns:**
    - `bool`: Whether parentheses are needed around the child for correct parsing or not.
    """

    child_type  = (child.op.__class__
                   if (child_cls := child.__class__) in (BoolOp, BinOp, UnaryOp) else child_cls)
    parent_type = (parent.op.__class__
                   if (parent_cls := parent.__class__) in (BoolOp, BinOp, UnaryOp) else parent_cls)

    if child_cls is MatchAs and child.pattern is None:
        flags['matchas_pat_None'] = True

    if parent_cls is Dict:
        if parent.keys[idx] is None:
            flags['dict_key_None'] = True

    elif parent_cls is Attribute:
        if child_cls is Constant and isinstance(child.value, int):
            flags['attr_val_int'] = True

    return precedence_require_parens_by_type(child_type, parent_type, field, **flags)
