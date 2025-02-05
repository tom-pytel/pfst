#!/usr/bin/env python

import os
import unittest

import ast as ast_
from fst.util import *

PYFNMS = sum((
    [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
    for top in ('src', 'tests')),
    start=[]
)

def read(fnm):
    with open(fnm) as f:
        return f.read()


class TestUtil(unittest.TestCase):
    def test_bistr(self):
        s = bistr('\x7f' * 127)

        self.assertEqual(s.c2b(0), 0)
        self.assertEqual(s.b2c(0), 0)
        self.assertEqual(s.c2b(127), 127)
        self.assertEqual(s.b2c(127), 127)
        self.assertEqual(s.c2b(128), 128)
        self.assertEqual(s.b2c(128), 128)

        s = bistr('\u00ff' * 127)

        self.assertEqual(s.c2b(0), 0)
        self.assertEqual(s.b2c(0), 0)
        self.assertEqual(s.c2b(127), 254)
        self.assertEqual(s.b2c(254), 127)
        self.assertRaises(IndexError, s.c2b, 128)
        self.assertRaises(IndexError, s.b2c, 255)
        self.assertEqual(s._c2b.typecode, 'B')
        self.assertEqual(s._b2c.typecode, 'B')

        for i in range(127):
            self.assertEqual(i, s.b2c(s.c2b(i)))
            self.assertEqual(i, s.b2c(s.c2b(i) + 1))

        s = bistr('\u00ff' * 128)

        self.assertEqual(s.c2b(0), 0)
        self.assertEqual(s.b2c(0), 0)
        self.assertEqual(s.c2b(128), 256)
        self.assertEqual(s.b2c(256), 128)
        self.assertRaises(IndexError, s.c2b, 129)
        self.assertRaises(IndexError, s.b2c, 257)
        self.assertEqual(s._c2b.typecode, 'H')
        self.assertEqual(s._b2c.typecode, 'B')

        for i in range(128):
            self.assertEqual(i, s.b2c(s.c2b(i)))
            self.assertEqual(i, s.b2c(s.c2b(i) + 1))

        s = bistr('\u00ff' * 256)

        self.assertEqual(s.c2b(0), 0)
        self.assertEqual(s.b2c(0), 0)
        self.assertEqual(s.c2b(256), 512)
        self.assertEqual(s.b2c(512), 256)
        self.assertRaises(IndexError, s.c2b, 257)
        self.assertRaises(IndexError, s.b2c, 513)

        self.assertEqual(s._c2b.typecode, 'H')
        self.assertEqual(s._b2c.typecode, 'H')

        for i in range(256):
            self.assertEqual(i, s.b2c(s.c2b(i)))
            self.assertEqual(i, s.b2c(s.c2b(i) + 1))


    # TODO: other tests


    def test_copy(self):
        for fnm in PYFNMS:
            with open(fnm) as f:
                src = f.read()

            for type_comments in (False, True):
                ast = ast_.parse(src, type_comments=type_comments)
                dst = copy(ast)

                compare(ast, dst, locations=True, type_comments=type_comments, do_raise=True)


if __name__ == '__main__':
    unittest.main()
