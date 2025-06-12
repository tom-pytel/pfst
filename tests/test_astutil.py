#!/usr/bin/env python

import os
import sys
import unittest

import ast as ast_
from ast import *
from fst.astutil import *
from fst.astutil import TypeVar, TryStar

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


    def test_compare_asts(self):
        ast1 = parse('def f():\n  i = 1\n  j = 2').body[0]
        ast2 = parse('def f():\n  i = 1\n  j = 2').body[0]
        ast3 = parse('def f():\n  i = 1\n  j =  2').body[0]
        ast4 = parse('def f():\n  i = 1\n  k = 3').body[0]
        ast5 = parse('def f():\n  i = 1').body[0]

        self.assertTrue(compare_asts(ast1, ast2, raise_=True))
        self.assertTrue(compare_asts(ast1, ast3, locs=False, raise_=True))
        self.assertRaises(WalkFail, compare_asts, ast1, ast3, locs=True, raise_=True)
        self.assertFalse(compare_asts(ast1, ast3, locs=True, raise_=False))
        self.assertFalse(compare_asts(ast1, ast4, raise_=False))
        self.assertTrue(compare_asts(ast1, ast4, skip1={ast1.body[1]}, skip2={ast4.body[1]}, raise_=False))
        self.assertTrue(compare_asts(ast1, ast4, recurse=False, raise_=False))
        self.assertFalse(compare_asts(ast1, ast5, recurse=False, raise_=False))

    def test_copy_ast(self):
        for fnm in PYFNMS:
            with open(fnm) as f:
                src = f.read()

            for type_comments in (False, True):
                ast = parse(src, type_comments=type_comments)
                dst = copy_ast(ast)

                compare_asts(ast, dst, locs=True, type_comments=type_comments, raise_=True)

    def test_last_block_header_child(self):
        self.assertIsInstance(last_block_header_child(parse('def f(a) -> int: pass').body[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('def f(a): pass').body[0]), arguments)
        self.assertIsInstance(last_block_header_child(parse('def f(): pass').body[0]), arguments)
        self.assertIsInstance(last_block_header_child(parse('async def f(a) -> int: pass').body[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('async def f(a): pass').body[0]), arguments)
        self.assertIsInstance(last_block_header_child(parse('async def f(): pass').body[0]), arguments)
        self.assertIsInstance(last_block_header_child(parse('class cls(base, keyword=1): pass').body[0]), keyword)
        self.assertIsInstance(last_block_header_child(parse('class cls(base): pass').body[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('for a in b: pass\nelse: pass').body[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('async for a in b: pass\nelse: pass').body[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('while a: pass\nelse: pass').body[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('if a: pass\nelse: pass').body[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('with f(): pass').body[0]), withitem)
        self.assertIsInstance(last_block_header_child(parse('with f() as v: pass').body[0]), withitem)
        self.assertIsInstance(last_block_header_child(parse('async with f(): pass').body[0]), withitem)
        self.assertIsInstance(last_block_header_child(parse('async with f() as v: pass').body[0]), withitem)
        self.assertIsInstance(last_block_header_child(parse('match a:\n case 2: pass').body[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('match a:\n case 2: pass').body[0].cases[0]), MatchValue)
        self.assertIsInstance(last_block_header_child(parse('match a:\n case 2 if True: pass').body[0].cases[0]), Constant)
        self.assertIsNone    (last_block_header_child(parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0]))
        self.assertIsNone    (last_block_header_child(parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].handlers[0]))
        self.assertIsInstance(last_block_header_child(parse('try: pass\nexcept Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0]), Name)
        self.assertIsInstance(last_block_header_child(parse('try: pass\nexcept (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0]), Tuple)
        self.assertIsInstance(last_block_header_child(parse('try: pass\nexcept (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0]), Tuple)

        if sys.version_info[:2] >= (3, 12):
            self.assertIsNone    (last_block_header_child(parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0]))
            self.assertIsInstance(last_block_header_child(parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0]), Name)
            self.assertIsInstance(last_block_header_child(parse('try: pass\nexcept* (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0]), Tuple)
            self.assertIsInstance(last_block_header_child(parse('try: pass\nexcept* (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0]), Tuple)
            self.assertIsInstance(last_block_header_child(parse('class cls[T]: pass').body[0]), TypeVar)
            self.assertIsInstance(last_block_header_child(parse('def f[T](): pass').body[0]), arguments)


if __name__ == '__main__':
    unittest.main()
