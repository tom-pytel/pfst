from array import array
from ast import *
from typing import Any, Callable, Iterator, Literal, NamedTuple, Sequence

__all__ = [
    'aststr', 'astfield', 'get_field', 'has_type_comments', 'guess_parse_mode', 'Walk2Fail', 'walk2',
    'compare', 'copy_attributes',
]


class aststr(str):
    """Easy mapping between char and encoded byte index (including 1 past last valid unit). Only positive indices."""

    _c2b: array  # character to byte indices
    _b2c: array  # byte to character indices

    _i2i_same = lambda idx: idx

    def __new__(cls, s: str) -> 'aststr':
        return s if s.__class__ is aststr else str.__new__(cls, s)

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
            self.c2b = self.b2c = aststr._i2i_same

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
    field: str
    idx:   int | None = None


def get_field(node: AST, field: str, idx: int | None = None) -> AST:
    field = getattr(node, field)

    return field if idx is None else field[idx]


def has_type_comments(node: AST) -> bool:
    for n in walk(node):
        if getattr(n, 'type_comments', None) is not None:
            return True

    return False


def guess_parse_mode(node: AST) -> Literal['exec'] | Literal['eval'] | Literal['single']:
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

def walk2(node1: AST, node2: AST, cbnonast: Callable[[str, Any, Any], bool] | None = None) -> Iterator[tuple[AST, AST]]:
    """Walk two asts simultaneously ensuring they have the same structure."""

    if node1.__class__ is not node2.__class__:
        raise Walk2Fail

    stack1 = [node1]
    stack2 = [node2]

    while stack1 and stack2:
        node1 = stack1.pop()
        node2 = stack2.pop()

        yield node1, node2

        fields1 = list(iter_fields(node1))
        fields2 = list(iter_fields(node2))

        if len(fields1) != len(fields2):
            raise Walk2Fail

        for (name1, value1), (name2, value2) in zip(fields1, fields2):
            if name1 != name2:
                raise Walk2Fail

            if (is_ast := isinstance(value1, AST)) or isinstance(value1, list) or isinstance(value2, (AST, list)):
                if value1.__class__ is not value2.__class__:
                    raise Walk2Fail

                if is_ast:
                    stack1.append(value1)
                    stack2.append(value2)

                elif len(value1) != len(value2):
                    raise Walk2Fail

                else:
                    stack1.extend(n for n in value1 if isinstance(n, AST))
                    stack2.extend(n for n in value2 if isinstance(n, AST))

            elif cbnonast and cbnonast(name1, value1, value2) is False:
                raise Walk2Fail

    if stack1 or stack2:
        raise Walk2Fail

    return True


def compare(ast1: AST, ast2: AST, *, locations: bool = False, type_comments: bool = False) -> bool:
    if type_comments:
        cbnonast = lambda f, n1, n2: n1.__class__ is n2.__class__ and n1 == n2
    else:
        cbnonast = lambda f, n1, n2: f == 'type_comment' or (n1.__class__ is n2.__class__ and n1 == n2)

    try:
        for n1, n2 in walk2(ast1, ast2, cbnonast):
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
    if type_comments:
        cbnonast = lambda f, n1, n2: n1.__class__ is n2.__class__ and n1 == n2
    else:
        cbnonast = lambda f, n1, n2: f == 'type_comment' or (n1.__class__ is n2.__class__ and n1 == n2)

    try:
        for ns, nd in walk2(src, dst, cbnonast):
            for attr in attrs:
                if (val := getattr(ns, attr, cbnonast)) is not cbnonast:  # cbnonast is sentinel
                    setattr(nd, attr, val)
                elif hasattr(nd, attr):
                    delattr(nd, attr)

    except Walk2Fail:
        return False

    return True
