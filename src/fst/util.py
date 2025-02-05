from array import array
from ast import *
from typing import Any, Callable, Iterator, Literal, NamedTuple

__all__ = [
    'bistr', 'astfield', 'get_field', 'has_type_comments', 'is_parsable', 'get_parse_mode', 'Walk2Fail', 'walk2',
    'compare', 'copy_attributes', 'copy',
]


class bistr(str):
    """Easy mapping between char and encoded byte index (including 1 past last valid unit). Only positive indices."""

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


class astfield(NamedTuple):
    name: str
    idx:  int | None = None

    def get(self, node: AST) -> Any:
        return getattr(node, self.name) if self.idx is None else getattr(node, self.name)[self.idx]


def get_field(node: AST, name: str, idx: int | None = None) -> AST:
    return getattr(node, name) if idx is None else getattr(node, name)[idx]


def has_type_comments(ast: AST) -> bool:
    for n in walk(ast):
        if getattr(n, 'type_comments', None) is not None:
            return True

    return False


def is_parsable(node: AST) -> bool:
    if not isinstance(node, AST) or isinstance(node, (Load, Store, Del,
            Attribute, ExceptHandler, Starred, Slice, FormattedValue,
            expr_context, operator, cmpop, boolop, alias, unaryop, arguments, arg, keyword, comprehension,
            withitem)):
        return False

    if isinstance(node, Call) and not is_parsable(node.func):
        return False

    return True


def get_parse_mode(node: AST) -> Literal['exec'] | Literal['eval'] | Literal['single']:
    if isinstance(node, stmt):
        return 'exec'
    if isinstance(node, expr):
        return 'eval'
    if isinstance(node, Module):
        return 'exec'
    if isinstance(node, Expression):
        return 'eval'
    if isinstance(node, Interactive):
        return 'single'

    raise ValueError('can not determine parse mode')


class Walk2Fail(Exception): pass

def walk2(ast1: AST, ast2: AST, cb_primitive: Callable[[Any, Any, str, int], bool] | None = None) -> Iterator[tuple[AST, AST]]:
    """Walk two asts simultaneously ensuring they have the same structure."""

    if ast1.__class__ is not ast2.__class__:
        raise Walk2Fail(f"top level nodes differ in '{ast1.__class__.__qualname__}' vs. '{ast1.__class__.__qualname__}'")

    stack1 = [ast1]
    stack2 = [ast2]

    while stack1 and stack2:
        a1 = stack1.pop()
        a2 = stack2.pop()

        yield a1, a2

        fields1 = list(iter_fields(a1))
        fields2 = list(iter_fields(a2))

        if len(fields1) != len(fields2):
            raise Walk2Fail(f"number of fields differ in '{a1.__class__.__qualname__}'")

        for (name1, child1), (name2, child2) in zip(fields1, fields2):
            if name1 != name2:
                raise Walk2Fail(f"field names differ in '{a1.__class__.__qualname__}', '{name1}' vs. '{name2}'")

            if (is_ast := isinstance(child1, AST)) or isinstance(child1, list) or isinstance(child2, (AST, list)):
                if child1.__class__ is not child2.__class__:
                    raise Walk2Fail(f"child classes differ at .{name1} in '{a1.__class__.__qualname__}', "
                                    f"'{child1.__class__.__qualname__}' vs. '{child2.__class__.__qualname__}'")

                if is_ast:
                    stack1.append(child1)
                    stack2.append(child2)

                elif len(child1) != len(child2):
                    raise Walk2Fail(f"child list lengths differ at .{name1} in '{a1.__class__.__qualname__}'")

                else:
                    for i, (c1, c2) in enumerate(zip(child1, child2)):
                        if (is_ast := isinstance(c1, AST)) ^ isinstance(c2, AST):
                            raise Walk2Fail(f"child elements differ at .{name1}[{i}] in '{a1.__class__.__qualname__}'")

                        if is_ast:
                            if c1.__class__ is not c2.__class__:
                                raise Walk2Fail(f"child element classes differ at .{name1}[{i}] in '{a1.__class__.__qualname__}', "
                                                f"'{c1.__class__.__qualname__}' vs. '{c2.__class__.__qualname__}'")

                            stack1.append(c1)
                            stack2.append(c2)

                        elif cb_primitive and cb_primitive(c1, c2, name1, i) is False:
                            raise Walk2Fail(f"primitives differ at .{name1}[{i}] in '{a1.__class__.__qualname__}', {c1!r} vs. {c2!r}")

            elif cb_primitive and cb_primitive(child1, child2, name1, None) is False:
                raise Walk2Fail(f"primitives differ at .{name1} in '{a1.__class__.__qualname__}', {child1!r} vs. {child2!r}")

    if stack1 or stack2:
        raise Walk2Fail('structure lengths differ')

    return True


_compare_primitive_type_comments_func = (
    (lambda p1, p2, n, i: n == 'type_comment' or (p1.__class__ is p2.__class__ and p1 == p2)),
    (lambda p1, p2, n, i: p1.__class__ is p2.__class__ and p1 == p2),
)

def compare(ast1: AST, ast2: AST, *, locations: bool = False, type_comments: bool = False, do_raise: bool = False) -> bool:
    """Copy two trees including possibly locations and type comments."""

    cb_primitive = _compare_primitive_type_comments_func[bool(type_comments)]

    try:
        for n1, n2 in walk2(ast1, ast2, cb_primitive):
            if locations:
                if (getattr(n1, 'lineno', None) != getattr(n2, 'lineno', None) or
                    getattr(n1, 'col_offset', None) != getattr(n2, 'col_offset', None) or
                    getattr(n1, 'end_lineno', None) != getattr(n2, 'end_lineno', None) or
                    getattr(n1, 'end_col_offset', None) != getattr(n2, 'end_col_offset', None)
                ):
                    raise Walk2Fail(f"locations differ in '{n1.__class__.__qualname__}'")

    except Walk2Fail:
        if do_raise:
            raise

        return False

    return True


def copy_attributes(src: AST, dst: AST, *, compare: bool = True, type_comments: bool = False, do_raise: bool = False) -> bool:
    """Copy attributes from one tree to another checking structure equality in the process."""

    cb_primitive = _compare_primitive_type_comments_func[bool(type_comments)] if compare else lambda p1, p2, n, i: True

    try:
        for ns, nd in walk2(src, dst, cb_primitive):
            for attr in ns._attributes:
                if (val := getattr(ns, attr, cb_primitive)) is not cb_primitive:
                    setattr(nd, attr, val)
                elif hasattr(nd, attr):
                    delattr(nd, attr)

    except Walk2Fail:
        if do_raise:
            raise

        return False

    return True


def copy(ast: AST) -> AST:
    """Copy a tree."""

    params = {}

    for field in ast._fields:
        child = getattr(ast, field)

        if isinstance(child, AST):
            params[field] = copy(child)
        elif not isinstance(child, list):
            params[field] = child

        else:
            children = []

            for c in child:
                if isinstance(c, AST):
                    children.append(copy(c))
                elif not isinstance(c, list):
                    children.append(c)

            params[field] = children

    ret = ast.__class__(**params)

    for attr in ast._attributes:
        if (val := getattr(ast, attr, ret)) is not ret:
            setattr(ret, attr, val)

    return ret
