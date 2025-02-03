from array import array
from ast import *
from typing import Iterator, Literal, NamedTuple

__all__ = [
    'aststr', 'astfield', 'get_node_field', 'has_type_comments', 'guess_parse_mode', 'compare_asts',
    'copy_ast_attributes',
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
            return array('L', b'\x00\x00\x00\x00' * (len_array + 1))

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


def get_node_field(node: AST, field: str, idx: int | None = None) -> AST:
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


def compare_asts(node1: AST, node2: AST, *, type_comments=True) -> bool:
    stack1 = [node1]
    stack2 = [node2]

    while stack1 and stack2:
        node1 = stack1.pop()
        node2 = stack2.pop()

        if node1.__class__ is not node2.__class__:
            return False

        fields1 = list(iter_fields(node1))
        fields2 = list(iter_fields(node2))

        if len(fields1) != len(fields2):
            return False

        for (name1, value1), (name2, value2) in zip(fields1, fields2):
            if name1 != name2:
                return False

            if not type_comments and name1 == 'type_comment':
                continue

            if value1.__class__ is not value2.__class__:
                return False

            if isinstance(value1, AST):
                stack1.append(value1)
                stack2.append(value2)

            elif isinstance(value1, list):
                stack1.extend(value1)
                stack2.extend(value2)

            elif value1 != value2:
                return False

    if stack1 or stack2:
        return False

    return True


def copy_ast_attributes(src: AST, dst: AST):
    """Expects asts to have same sturcture, raises otherwise."""

    # TODO: this


class StructureError(ValueError):
    pass

def walk2(node1: AST, node2: AST) -> Iterator[tuple[tuple[astfield | None, object], tuple[astfield | None, object]]]:
    stack1 = [(None, node1)]
    stack2 = [(None, node2)]

    while stack1 and stack2:
        _, node1 = fldnod1 = stack1.pop()
        _, node2 = fldnod2 = stack2.pop()

        if node1.__class__ is not node2.__class__:
            raise StructureError('ast structure does not match')

        yield fldnod1, fldnod2

        fields1 = list(iter_fields(node1))
        fields2 = list(iter_fields(node2))

        if len(fields1) != len(fields2):
            raise StructureError('ast structure does not match')

        for (name1, value1), (name2, value2) in zip(fields1, fields2):
            if name1 != name2:
                raise StructureError('ast structure does not match')

            if isinstance(value1, (AST, list)) or isinstance(value2, (AST, list)):
                if value1.__class__ is not value2.__class__:
                    raise StructureError('ast structure does not match')

                if isinstance(value1, AST):
                    field = astfield(name1)

                    stack1.append((field, value1))
                    stack2.append((field, value2))

                else:
                    for idx, (node1, node2) in enumerate(zip(value1, value2)):
                        field = astfield(name1, idx)

                        stack1.append((field, node1))
                        stack2.append((field, node2))

            else:
                field = astfield(name1)

                yield (field, value1), (field, value2)

    if stack1 or stack2:
        return False

    return True



            # if not type_comments and name1 == 'type_comment':
            #     continue

            # if value1.__class__ is not value2.__class__:
            #     return False

            # elif value1 != value2:
            #     return False


            # if value1.__class__ is not value2.__class__ or value1 != value2:
            #     StructureError('asts are not equal')
