from array import array
from ast import *
from typing import NamedTuple

__all__ = ['aststr', 'astfield', 'get_node_field']


class aststr(str):
    """Easy mapping between char and encoded byte indices (including 1 past last valid unit). Negative index conversions
    start with this nonexistent one past character so give length of string in chars when converting -1. Last index of
    an actual character or utf8 codeword is at -2."""

    __c2b: array  # character to byte indices
    __b2c: array  # byte to character indices

    _i2i = lambda idx: idx

    def __new__(cls, s: str) -> 'aststr':
        return s if s.__class__ is aststr else str.__new__(cls, s)

    def __empty_array(self, len_array: int, highest_value: int) -> array:
        if highest_value < 0x100:
            return array('B', b'\x00' * (len_array + 1))
        if highest_value < 0x10000:
            return array('H', b'\x00\x00' * (len_array + 1))
        if highest_value < 0x100000000:
            return array('L', b'\x00\x00\x00\x00' * (len_array + 1))

        return array('Q', b'\x00\x00\x00\x00\x00\x00\x00\x00' * (len_array + 1))

    def _c2b(self, idx):
        return self.__c2b[idx]

    def c2b(self, idx: int) -> int:
        if (lc := len(self)) == (lb := len(self.encode())):
            self.c2b = self.b2c = aststr._i2i

            return idx

        c2b = self.__c2b = self.__empty_array(lc, lb)
        j   = 0

        for i, c in enumerate(self):
            c2b[i]  = j
            j      += len(c.encode())

        c2b[-1]  = j
        self.c2b = self._c2b

        return c2b[idx]

    def _b2c(self, idx):
        return self.__b2c[idx] or (idx and (None if idx > -len(self.__b2c) else 0))

    def b2c(self, idx: int) -> int:
        if (lb := self.c2b(lc := len(self))) == lc:
            return idx  # no chars > '\x7f' so funcs are set to `_i2i` identity

        b2c = self.__b2c = self.__empty_array(lb, lc)

        for i, j in enumerate(self.__c2b):
            b2c[j] = i

        self.b2c = self._b2c

        return b2c[idx]

    def clear(self):
        try:
            del self.c2b
            del self.__c2b
        except AttributeError:
            pass

        try:
            del self.b2c
            del self.__b2c
        except AttributeError:
            pass


class astfield(NamedTuple):
    field: str
    idx:   int | None = None


def get_node_field(node: AST, field: str, idx: int | None = None) -> AST:
    field = getattr(node, field)

    return field if idx is None else field[idx]
