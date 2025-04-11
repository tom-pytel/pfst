import sys
from array import array
from ast import *
from itertools import chain
from typing import Any, Callable, Iterable, Iterator, Literal

from_iterable = chain.from_iterable

__all__ = [
    'FIELDS', 'AST_FIELDS',
    'bistr', 'get_field', 'has_type_comments', 'is_parsable', 'get_parse_mode',
    'WalkFail', 'walk2', 'compare_asts', 'copy_attributes', 'copy_ast', 'set_ctx', 'get_func_class_or_ass_by_name',
    'syntax_ordered_children',
]


if sys.version_info[:2] < (3, 12):  # for isinstance() checks
    class TryStar(AST): pass
    class TypeVar(AST): pass
    class ParamSpec(AST): pass
    class TypeVarTuple(AST): pass
    class TypeAlias(AST): pass


# Mostly in syntax order except a few special cases:
#   BoolOp        - multiple simultaneous locations possible for single `op`
#   Dict          - interleaved `keys` and `values`
#   Compare       - interleaved `ops` and `comparators`
#   MatchMapping  - interleaved `keys` and `patterns`
#   arguments     - interleaved `posonlyargs`/`args` and `defaults` (partially), interleaved `kwonlyargs` and `kw_defaults`
#   Call          - `args` type `Starred` can be inside `keywords`
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
    (FormattedValue,     (('value', 'expr'), ('format_spec', 'expr?'), ('conversion', 'int'))),
    (JoinedStr,          (('values', 'expr*'),)),
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
])

# only fields which can contain an AST, {cls: ('field1', 'field2', ...), ...}
AST_FIELDS = {cls: tuple(f for f, t in fields
                         if not t.startswith('int') and not t.startswith('string') and
                         not t.startswith('identifier') and not t.startswith('constant') and
                         not t.startswith('type_ignore'))
              for cls, fields in FIELDS.items()}


class bistr(str):
    """Byte-indexed string, easy mapping between character and encoded byte index (including 1 past last valid unit).
    Only positive indices."""

    _c2b: array  # character to byte indices
    _b2c: array  # byte to character indices

    _i2i_same = lambda idx: idx

    @property
    def lenbytes(self) -> int:
        return self.c2b(len(self))

    def __new__(cls, s: str) -> 'bistr':
        return s if s.__class__ is bistr else str.__new__(cls, s)

    @staticmethod
    def _make_array(len_array: int, highest_value: int) -> array:
        if highest_value < 0x100:
            return array('B', b'\x00' * (len_array + 1))
        if highest_value < 0x10000:
            return array('H', b'\x00\x00' * (len_array + 1))
        if highest_value < 0x100000000:
            return array('I', b'\x00\x00\x00\x00' * (len_array + 1))

        return array('Q', b'\x00\x00\x00\x00\x00\x00\x00\x00' * (len_array + 1))

    def c2b_lookup(self, idx):
        return self._c2b[idx]

    def c2b(self, idx: int) -> int:
        if (lc := len(self)) == (lb := len(self.encode())):
            self.c2b = self.b2c = bistr._i2i_same

            return idx

        c2b = self._c2b = self._make_array(lc, lb)
        j   = 0

        for i, c in enumerate(self):
            c2b[i]  = j
            j      += len(c.encode())

        c2b[-1]  = j
        self.c2b = self.c2b_lookup

        return c2b[idx]

    def b2c_lookup(self, idx):
        return self._b2c[idx]

    def b2c(self, idx: int) -> int:
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

        self.b2c = self.b2c_lookup

        return b2c[idx]

    def clear_cache(self):
        try:
            del self.c2b, self._c2b
        except AttributeError:
            pass

        try:
            del self.b2c, self._b2c
        except AttributeError:
            pass


def get_field(node: AST, name: str, idx: int | None = None) -> AST:
    return getattr(node, name) if idx is None else getattr(node, name)[idx]


def has_type_comments(ast: AST) -> bool:
    for n in walk(ast):
        if getattr(n, 'type_comments', None) is not None:
            return True

    return False


def is_parsable(ast: AST) -> bool:
    """Really means the AST is `unparse()`able and then re`parse()`able which will get it to this top level AST node
    surrounded by the appropriate `ast.mod`. The source may change a bit though, parentheses, 'if' <-> 'elif'."""

    if not isinstance(ast, AST):
        return False

    if isinstance(ast, (
        ExceptHandler, Slice, FormattedValue, Starred, TypeIgnore,
        expr_context, unaryop, boolop, operator, cmpop,
        alias, arguments, comprehension, withitem, match_case, pattern, type_ignore,
        arg, keyword,
        TypeVar, ParamSpec, TypeVarTuple,  # py 3.12+
    )):
        return False

    return True


def get_parse_mode(ast: AST) -> Literal['exec'] | Literal['eval'] | Literal['single']:
    if isinstance(ast, stmt):
        return 'exec'
    if isinstance(ast, expr):
        return 'eval'
    if isinstance(ast, Module):
        return 'exec'
    if isinstance(ast, Expression):
        return 'eval'
    if isinstance(ast, Interactive):
        return 'single'

    raise ValueError('can not determine parse mode')


class WalkFail(Exception): pass

def walk2(ast1: AST, ast2: AST, cb_primitive: Callable[[Any, Any, str, int], bool] | None = None, *,
          ctx: bool = True, recurse: bool = True) -> Iterator[tuple[AST, AST]]:
    """Walk two asts simultaneously ensuring they have the same structure."""

    if ast1.__class__ is not ast2.__class__:
        raise WalkFail(f"top level nodes differ in '{ast1.__class__.__qualname__}' vs. '{ast1.__class__.__qualname__}'")

    stack      = [(ast1, ast2)]
    next_stack = stack if recurse else []

    while stack:
        a1, a2 = stack.pop()

        yield a1, a2

        fields1 = list(iter_fields(a1))
        fields2 = list(iter_fields(a2))

        if len(fields1) != len(fields2):
            raise WalkFail(f"number of fields differ in '{a1.__class__.__qualname__}'")

        for (name1, child1), (name2, child2) in zip(fields1, fields2):
            if name1 != name2:
                raise WalkFail(f"field names differ in '{a1.__class__.__qualname__}', '{name1}' vs. '{name2}'")

            if (is_ast := isinstance(child1, AST)) or isinstance(child1, list) or isinstance(child2, (AST, list)):
                if child1.__class__ is not child2.__class__:
                    if not ctx and is_ast and isinstance(child1, expr_context) and isinstance(child2, expr_context):
                        continue

                    raise WalkFail(f"child classes differ at .{name1} in '{a1.__class__.__qualname__}', "
                                   f"'{child1.__class__.__qualname__}' vs. '{child2.__class__.__qualname__}'")

                if is_ast:
                    stack.append((child1, child2))

                elif len(child1) != len(child2):
                    raise WalkFail(f"child list lengths differ at .{name1} in '{a1.__class__.__qualname__}'")

                else:
                    for i, (c1, c2) in enumerate(zip(child1, child2)):
                        if (is_ast := isinstance(c1, AST)) ^ isinstance(c2, AST):
                            raise WalkFail(f"child elements differ at .{name1}[{i}] in '{a1.__class__.__qualname__}'")

                        if is_ast:
                            if c1.__class__ is not c2.__class__:
                                raise WalkFail(f"child element classes differ at .{name1}[{i}] in '{a1.__class__.__qualname__}', "
                                               f"'{c1.__class__.__qualname__}' vs. '{c2.__class__.__qualname__}'")

                            stack.append((c1, c2))

                        elif cb_primitive and cb_primitive(c1, c2, name1, i) is False:
                            raise WalkFail(f"primitives differ at .{name1}[{i}] in '{a1.__class__.__qualname__}', {c1!r} vs. {c2!r}")

            elif cb_primitive and cb_primitive(child1, child2, name1, None) is False:
                raise WalkFail(f"primitives differ at .{name1} in '{a1.__class__.__qualname__}', {child1!r} vs. {child2!r}")

        stack = next_stack

    return True


_compare_primitive_type_comments_func = (
    (lambda p1, p2, n, i: n == 'type_comment' or (p1.__class__ is p2.__class__ and p1 == p2)),
    (lambda p1, p2, n, i: p1.__class__ is p2.__class__ and p1 == p2),
)

def compare_asts(ast1: AST, ast2: AST, *, locs: bool = False, type_comments: bool = False, ctx: bool = True,
                 recurse: bool = True, raise_: bool = False) -> bool:
    """Copy two trees including possibly locations and type comments."""

    cb_primitive = _compare_primitive_type_comments_func[bool(type_comments)]

    try:
        for n1, n2 in walk2(ast1, ast2, cb_primitive, ctx=ctx, recurse=recurse):
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


def copy_attributes(src: AST, dst: AST, *, compare: bool = True, type_comments: bool = False, raise_: bool = True) -> bool:
    """Copy attributes from one tree to another checking structure equality in the process."""

    cb_primitive = _compare_primitive_type_comments_func[bool(type_comments)] if compare else lambda p1, p2, n, i: True

    try:
        for ns, nd in walk2(src, dst, cb_primitive):
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


def copy_ast(ast: AST | None) -> AST:
    """Copy a tree."""

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


def set_ctx(ast_or_stack: AST | list[AST], ctx: type[expr_context], *, doit=True) -> bool:
    change = False
    stack  = [ast_or_stack] if isinstance(ast_or_stack, AST) else ast_or_stack

    while stack:  # anything that might have been a ctx Store or Del before (outside NamedExpr) set to Load
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


def _syntax_ordered_children_Call(ast):
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

def _syntax_ordered_children_arguments(ast):
    children = []

    if not (defaults := ast.defaults):
        children.extend(ast.posonlyargs)
        children.extend(ast.args)

    elif (ldefaults := len(defaults)) <= (largs := len(args := ast.args)):
        children.extend(ast.posonlyargs)
        children.extend(args[:-ldefaults])
        children.extend(from_iterable(zip(args[-ldefaults:], defaults)))

    else:
        children.extend((posonlyargs := ast.posonlyargs)[:-(lposonly_defaults := ldefaults - largs)])
        children.extend(from_iterable(zip(posonlyargs[-lposonly_defaults:], defaults[:lposonly_defaults])))
        children.extend(from_iterable(zip(args, defaults[lposonly_defaults:])))

    if (vararg := ast.vararg):
        children.append(vararg)

    if not (kw_defaults := ast.kw_defaults):
        children.extend(ast.kwonlyargs)
    else:
        children.extend(from_iterable(zip(ast.kwonlyargs, kw_defaults)))

    if (kwarg := ast.kwarg):
        children.append(kwarg)

    return children

def _syntax_ordered_children_default(ast):
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

_syntax_ordered_children = {
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

    Dict:         lambda ast: list(from_iterable(zip(ast.keys, ast.values))),
    Compare:      lambda ast: [ast.left] + (list(from_iterable(zip(ops, ast.comparators)))
                                            if len(ops := ast.ops) > 1 else [ops[0], ast.comparators[0]]),
    Call:         _syntax_ordered_children_Call,
    arguments:    _syntax_ordered_children_arguments,
    MatchMapping: lambda ast: list(from_iterable(zip(ast.keys, ast.patterns))),
}

def syntax_ordered_children(ast: AST) -> list:
    """Returned `list` may contain `None` values."""

    return _syntax_ordered_children.get(ast.__class__, _syntax_ordered_children_default)(ast)
