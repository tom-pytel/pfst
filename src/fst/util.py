from array import array
from ast import *
from typing import Any, Callable, Iterator, Literal, NamedTuple, Sequence

__all__ = [
    'bistr', 'astfield', 'get_field', 'has_type_comments', 'guess_parse_mode', 'Walk2Fail', 'walk2',
    'compare', 'copy_attributes',
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


def get_field(ast: AST, name: str, idx: int | None = None) -> AST:
    return getattr(ast, name) if idx is None else getattr(ast, name)[idx]


def has_type_comments(ast: AST) -> bool:
    for n in walk(ast):
        if getattr(n, 'type_comments', None) is not None:
            return True

    return False


def guess_parse_mode(ast: AST) -> Literal['exec'] | Literal['eval'] | Literal['single']:
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


class Walk2Fail(Exception): pass

def walk2(ast1: AST, ast2: AST, cb_primitive: Callable[[Any, Any, str, int], bool] | None = None) -> Iterator[tuple[AST, AST]]:
    """Walk two asts simultaneously ensuring they have the same structure."""

    if ast1.__class__ is not ast2.__class__:
        raise Walk2Fail

    stack1 = [ast1]
    stack2 = [ast2]

    while stack1 and stack2:
        ast1 = stack1.pop()
        ast2 = stack2.pop()

        yield ast1, ast2

        fields1 = list(iter_fields(ast1))
        fields2 = list(iter_fields(ast2))

        if len(fields1) != len(fields2):
            raise Walk2Fail

        for (name1, child1), (name2, child2) in zip(fields1, fields2):
            if name1 != name2:
                raise Walk2Fail

            if (is_ast := isinstance(child1, AST)) or isinstance(child1, list) or isinstance(child2, (AST, list)):
                if child1.__class__ is not child2.__class__:
                    raise Walk2Fail

                if is_ast:
                    stack1.append(child1)
                    stack2.append(child2)

                elif len(child1) != len(child2):
                    raise Walk2Fail

                else:
                    for i, (c1, c2) in enumerate(zip(child1, child2)):
                        if (is_ast := isinstance(c1, AST)) ^ isinstance(c2, AST):
                            raise Walk2Fail

                        if is_ast:
                            stack1.append(c1)
                            stack2.append(c2)

                        elif cb_primitive and cb_primitive(c1, c2, name1, i) is False:
                            raise Walk2Fail

            elif cb_primitive and cb_primitive(child1, child2, name1, None) is False:
                raise Walk2Fail

    if stack1 or stack2:
        raise Walk2Fail

    return True


_compare_primitive_type_comments_func = (
    (lambda p1, p2, n, i: n == 'type_comment' or (p1.__class__ is p2.__class__ and p1 == p2)),
    (lambda p1, p2, n, i: p1.__class__ is p2.__class__ and p1 == p2),
)

def compare(ast1: AST, ast2: AST, *, locations: bool = False, type_comments: bool = False) -> bool:
    cb_primitive = _compare_primitive_type_comments_func[bool(type_comments)]

    try:
        for n1, n2 in walk2(ast1, ast2, cb_primitive):
            if locations:
                if (getattr(n1, 'lineno', None) != getattr(n2, 'lineno', None) or
                    getattr(n1, 'col_offset', None) != getattr(n2, 'col_offset', None) or
                    getattr(n1, 'end_lineno', None) != getattr(n2, 'end_lineno', None) or
                    getattr(n1, 'end_col_offset', None) != getattr(n2, 'end_col_offset', None)
                ):
                    raise Walk2Fail

    except Walk2Fail:
        return False

    return True


def copy_attributes(src: AST, dst: AST, attrs: Sequence[str], *, compare: bool = False, type_comments: bool = False) -> bool:
    cb_primitive = _compare_primitive_type_comments_func[bool(type_comments)]

    try:
        for ns, nd in walk2(src, dst, cb_primitive):
            for attr in attrs:
                if (val := getattr(ns, attr, cb_primitive)) is not cb_primitive:  # cb_primitive is sentinel
                    setattr(nd, attr, val)
                elif hasattr(nd, attr):
                    delattr(nd, attr)

    except Walk2Fail:
        return False

    return True
