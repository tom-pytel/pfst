#!/usr/bin/env python

import unittest

from fst import *

from fst.misc import PYGE12


class TestFSTMisc(unittest.TestCase):
    def test__get_trivia_params(self):
        with FST.options(trivia=False):
            self.assertEqual(('none', False, False, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=(True, True), neg=False))

        with FST.options(trivia=(False, False)):
            self.assertEqual(('none', False, False, 'none', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'none', False, False), FST._get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=(True, True), neg=False))

        with FST.options(trivia=(False, True)):
            self.assertEqual(('none', False, False, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), FST._get_trivia_params(trivia=(True, True), neg=False))
            self.assertEqual(('block', False, False, 'none', False, False), FST._get_trivia_params(trivia=(True, False), neg=False))

        with FST.options(trivia='all+1'):
            self.assertEqual(('all', 1, False, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('all', 1, False, 'line', False, False), FST._get_trivia_params(neg=True))

        with FST.options(trivia='all-1'):
            self.assertEqual(('all', False, True, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual(('all', 1, True, 'line', False, False), FST._get_trivia_params(neg=True))

        with FST.options(trivia='all-1'):
            self.assertEqual(('block', 2, False, 'line', False, False), FST._get_trivia_params(trivia='block+2', neg=False))
            self.assertEqual(('block', 2, False, 'line', False, False), FST._get_trivia_params(trivia='block+2', neg=True))
            self.assertEqual(('block', 2, False, 'line', 3, False), FST._get_trivia_params(trivia=('block+2', 'line+3'), neg=False))
            self.assertEqual(('block', 2, False, 'line', 3, False), FST._get_trivia_params(trivia=('block+2', 'line+3'), neg=True))
            self.assertEqual(('block', 2, False, 'line', 3, True), FST._get_trivia_params(trivia=('block+2', 'line-3'), neg=True))
            self.assertEqual(('block', 2, False, 'line', False, True), FST._get_trivia_params(trivia=('block+2', 'line-3'), neg=False))
            self.assertEqual(('block', False, True, 'line', False, True), FST._get_trivia_params(trivia=('block-2', 'line-3'), neg=False))

        with FST.options(trivia=1):
            self.assertEqual((1, False, False, 'line', False, False), FST._get_trivia_params(neg=False))
            self.assertEqual((2, False, False, 'line', False, False), FST._get_trivia_params(trivia=2, neg=False))
            self.assertEqual((2, False, False, 3, False, False), FST._get_trivia_params(trivia=(2, 3), neg=False))

    def test__loc_ClassDef_bases_pars(self):
        self.assertEqual('fstlocns(0, 9, 0, 9, n=0)', str(FST('class cls: pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 10, n=0)', str(FST('class cls : pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(1, 3, 1, 4, n=0)', str(FST('class \\\ncls : pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 1, 0, n=0)', str(FST('class cls \\\n: pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 11, n=1)', str(FST('class cls(): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(1, 0, 1, 2, n=1)', str(FST('class cls\\\n(): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 1, 1, n=1)', str(FST('class cls(\n): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(1, 0, 2, 1, n=1)', str(FST('class cls \\\n(\n): pass')._loc_ClassDef_bases_pars()))

        self.assertEqual('fstlocns(0, 9, 0, 12, n=1)', str(FST('class cls(b): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 14, n=1)', str(FST('class cls(k=v): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 14, n=1)', str(FST('class cls(**v): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 17, n=1)', str(FST('class cls(b, k=v): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 17, n=1)', str(FST('class cls(b, **v): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 2, 1, n=1)', str(FST('class cls(\nb\n): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(1, 1, 3, 1, n=1)', str(FST('class cls \\\n (\nb\n) \\\n: pass')._loc_ClassDef_bases_pars()))

        self.assertEqual('fstlocns(0, 9, 0, 13, n=1)', str(FST('class cls(b,): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 15, n=1)', str(FST('class cls(k=v,): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 15, n=1)', str(FST('class cls(**v,): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 18, n=1)', str(FST('class cls(b, k=v,): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 0, 18, n=1)', str(FST('class cls(b, **v,): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(0, 9, 3, 1, n=1)', str(FST('class cls(\nb\n,\n): pass')._loc_ClassDef_bases_pars()))
        self.assertEqual('fstlocns(1, 1, 4, 1, n=1)', str(FST('class cls \\\n (\nb\n,\n) \\\n: pass')._loc_ClassDef_bases_pars()))

        if PYGE12:
            self.assertEqual('fstlocns(0, 12, 0, 12, n=0)', str(FST('class cls[T]: pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(0, 12, 0, 13, n=0)', str(FST('class cls[T] : pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(0, 13, 0, 13, n=0)', str(FST('class cls[T,]: pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(0, 12, 0, 14, n=1)', str(FST('class cls[T](): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(0, 13, 0, 15, n=1)', str(FST('class cls[T,](): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(0, 15, 0, 17, n=1)', str(FST('class cls[T, U](): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(1, 3, 1, 5, n=1)', str(FST('class cls \\\n[T](): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(2, 1, 2, 3, n=1)', str(FST('class cls[\nT\n](): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(3, 1, 3, 3, n=1)', str(FST('class cls \\\n[\nT\n](): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(4, 0, 5, 1, n=1)', str(FST('class cls \\\n[\nT\n]\\\n(\n): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(6, 0, 7, 1, n=1)', str(FST('class cls \\\n[\nT\n,\nU\n]\\\n( \\\n): pass')._loc_ClassDef_bases_pars()))

            self.assertEqual('fstlocns(0, 12, 0, 15, n=1)', str(FST('class cls[T](b): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(0, 18, 0, 25, n=1)', str(FST('class cls[T, **U,]( b , ): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(1, 3, 1, 6, n=1)', str(FST('class cls \\\n[T](b): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(2, 1, 2, 4, n=1)', str(FST('class cls[\nT\n](b): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(3, 1, 3, 4, n=1)', str(FST('class cls \\\n[\nT\n](b): pass')._loc_ClassDef_bases_pars()))

            self.assertEqual('fstlocns(4, 0, 7, 1, n=1)', str(FST('class cls \\\n[\nT\n]\\\n(\nb\n,\n): pass')._loc_ClassDef_bases_pars()))
            self.assertEqual('fstlocns(6, 0, 7, 3, n=1)', str(FST('class cls \\\n[\nT\n,\nU\n]\\\n( \\\nb,): pass')._loc_ClassDef_bases_pars()))

    def test__loc_ImportFrom_names_pars(self):
        self.assertEqual('fstlocns(0, 14, 0, 15, n=0)', str(FST('from . import a')._loc_ImportFrom_names_pars()))
        self.assertEqual('fstlocns(0, 14, 0, 17, n=1)', str(FST('from . import (a)')._loc_ImportFrom_names_pars()))
        self.assertEqual('fstlocns(0, 14, 2, 1, n=1)', str(FST('from . import (\na\n)')._loc_ImportFrom_names_pars()))
        self.assertEqual('fstlocns(1, 0, 3, 1, n=1)', str(FST('from . import \\\n(\na\n)')._loc_ImportFrom_names_pars()))
        self.assertEqual('fstlocns(0, 14, 1, 1, n=0)', str(FST('from . import \\\na')._loc_ImportFrom_names_pars()))
        self.assertEqual('fstlocns(0, 13, 1, 1, n=0)', str(FST('from . import\\\na')._loc_ImportFrom_names_pars()))

        self.assertEqual('fstlocns(0, 22, 0, 23, n=0)', str(FST('from importlib import b')._loc_ImportFrom_names_pars()))
        self.assertEqual('fstlocns(0, 22, 1, 1, n=0)', str(FST('from importlib import \\\nb')._loc_ImportFrom_names_pars()))
        self.assertEqual('fstlocns(0, 22, 0, 25, n=1)', str(FST('from importlib import (b)')._loc_ImportFrom_names_pars()))
        self.assertEqual('fstlocns(0, 22, 2, 1, n=1)', str(FST('from importlib import (\nb\n)')._loc_ImportFrom_names_pars()))

        f = FST('from . import a')
        f._put_src(None, 0, 14, 0, 15, True)
        del f.a.names[:]
        self.assertEqual('fstlocns(0, 14, 0, 14, n=0)', str(f._loc_ImportFrom_names_pars()))
        f._put_src(None, 0, 13, 0, 14, True)
        self.assertEqual('fstlocns(0, 13, 0, 13, n=0)', str(f._loc_ImportFrom_names_pars()))
        f._put_src('\n', 0, 13, 0, 13, True)
        self.assertEqual('fstlocns(0, 13, 1, 0, n=0)', str(f._loc_ImportFrom_names_pars()))

    def test__loc_With_items_pars(self):
        def str_(loc_ret):
            del loc_ret.bound

            return str(loc_ret)

        self.assertEqual('fstlocns(0, 5, 0, 6, n=0)', str_(FST('with a: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 0, 8, n=0)', str_(FST('with (a): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 0, 13, n=1)', str_(FST('with (a as b): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 2, 1, n=1)', str_(FST('with (\na as b\n): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 0, 3, 1, n=1)', str_(FST('with \\\n(\na as b\n): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 1, 1, n=0)', str_(FST('with \\\na: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 4, 1, 1, n=0)', str_(FST('with\\\na: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 4, 3, 0, n=0)', str_(FST('with\\\n\\\na\\\n: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 0, 8, n=0)', str_(FST('with  a : pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 6, 0, 14, n=1)', str_(FST('with  (a as b)  : pass')._loc_With_items_pars()))

        self.assertEqual('fstlocns(0, 11, 0, 12, n=0)', str_(FST('async with a: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 11, 0, 14, n=0)', str_(FST('async with (a): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 11, 0, 19, n=1)', str_(FST('async with (a as b): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 11, 2, 1, n=1)', str_(FST('async with (\na as b\n): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 0, 3, 1, n=1)', str_(FST('async with \\\n(\na as b\n): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 11, 1, 1, n=0)', str_(FST('async with \\\na: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 10, 1, 1, n=0)', str_(FST('async with\\\na: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 10, 3, 0, n=0)', str_(FST('async with\\\n\\\na\\\n: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 11, 0, 14, n=0)', str_(FST('async with  a : pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 12, 0, 20, n=1)', str_(FST('async with  (a as b)  : pass')._loc_With_items_pars()))

        self.assertEqual('fstlocns(1, 6, 1, 7, n=0)', str_(FST('async \\\n with a: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 6, 1, 9, n=0)', str_(FST('async \\\n with (a): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 6, 1, 14, n=1)', str_(FST('async \\\n with (a as b): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 6, 3, 1, n=1)', str_(FST('async \\\n with (\na as b\n): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(2, 0, 4, 1, n=1)', str_(FST('async \\\n with \\\n(\na as b\n): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 6, 2, 1, n=0)', str_(FST('async \\\n with \\\na: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 5, 2, 1, n=0)', str_(FST('async \\\n with\\\na: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 5, 4, 0, n=0)', str_(FST('async \\\n with\\\n\\\na\\\n: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 6, 1, 9, n=0)', str_(FST('async \\\n with  a : pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(1, 7, 1, 15, n=1)', str_(FST('async \\\n with  (a as b)  : pass')._loc_With_items_pars()))

        f = FST('with a: pass')
        f._put_src(None, 0, 5, 0, 6, True)
        del f.a.items[:]
        self.assertEqual('fstlocns(0, 5, 0, 5, n=0)', str_(f._loc_With_items_pars()))
        f._put_src(None, 0, 4, 0, 5, True)
        self.assertEqual('fstlocns(0, 4, 0, 4, n=0)', str_(f._loc_With_items_pars()))
        f._put_src('\n', 0, 4, 0, 4, True)
        self.assertEqual('fstlocns(0, 4, 1, 0, n=0)', str_(f._loc_With_items_pars()))

        self.assertEqual('fstlocns(0, 5, 0, 8, n=0)', str_(FST('with (a): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 0, 13, n=0)', str_(FST('with (a) as b: pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 0, 15, n=1)', str_(FST('with ((a) as b): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 0, 15, n=0)', str_(FST('with (a) as (b): pass')._loc_With_items_pars()))
        self.assertEqual('fstlocns(0, 5, 0, 17, n=1)', str_(FST('with ((a) as (b)): pass')._loc_With_items_pars()))

    def test__loc_block_header_end(self):
        self.assertEqual((0, 15), parse('def f(a) -> int: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 8),  parse('def f(a): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 7),  parse('def f(): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 21), parse('async def f(a) -> int: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 14), parse('async def f(a): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 13), parse('async def f(): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 26), parse('class cls(base, keyword=1): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 15), parse('class cls(base): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 10), parse('for a in b: pass\nelse: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 16), parse('async for a in b: pass\nelse: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 7),  parse('while a: pass\nelse: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 4),  parse('if a: pass\nelse: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 8),  parse('with f(): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 13), parse('with f() as v: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 14), parse('async with f(): pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 19), parse('async with f() as v: pass').body[0].f._loc_block_header_end())
        self.assertEqual((0, 7),  parse('match a:\n case 2: pass').body[0].f._loc_block_header_end())
        self.assertEqual((1, 7),  parse('match a:\n case 2: pass').body[0].cases[0].f._loc_block_header_end())
        self.assertEqual((1, 15), parse('match a:\n case 2 if True: pass').body[0].cases[0].f._loc_block_header_end())
        self.assertEqual((0, 3),  parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].f._loc_block_header_end())
        self.assertEqual((1, 6),  parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
        self.assertEqual((1, 16), parse('try: pass\nexcept Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
        self.assertEqual((1, 33), parse('try: pass\nexcept (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
        self.assertEqual((1, 38), parse('try: pass\nexcept (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())

        if PYGE12:
            self.assertEqual((0, 3),  parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].f._loc_block_header_end())
            self.assertEqual((1, 17), parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
            self.assertEqual((1, 34), parse('try: pass\nexcept* (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
            self.assertEqual((1, 39), parse('try: pass\nexcept* (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end())
            self.assertEqual((0, 12), parse('class cls[T]: pass').body[0].f._loc_block_header_end())

        self.assertEqual((0, 15, 0, 15), parse('def f(a) -> int: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 8, 0, 7),  parse('def f(a): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 7, 0, 0),  parse('def f(): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 21, 0, 21), parse('async def f(a) -> int: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 14, 0, 13), parse('async def f(a): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 13, 0, 0), parse('async def f(): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 26, 0, 25), parse('class cls(base, keyword=1): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 15, 0, 14), parse('class cls(base): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 10, 0, 10), parse('for a in b: pass\nelse: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 16, 0, 16), parse('async for a in b: pass\nelse: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 7, 0, 7),  parse('while a: pass\nelse: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 4, 0, 4),  parse('if a: pass\nelse: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 8, 0, 8),  parse('with f(): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 13, 0, 13), parse('with f() as v: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 14, 0, 14), parse('async with f(): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 19, 0, 19), parse('async with f() as v: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 7, 0, 7),  parse('match a:\n case 2: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((1, 7, 1, 7),  parse('match a:\n case 2: pass').body[0].cases[0].f._loc_block_header_end(True))
        self.assertEqual((1, 15, 1, 15), parse('match a:\n case 2 if True: pass').body[0].cases[0].f._loc_block_header_end(True))
        self.assertEqual((0, 3, 0, 0),  parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((1, 6, 1, 0),  parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end(True))
        self.assertEqual((1, 16, 1, 16), parse('try: pass\nexcept Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end(True))
        self.assertEqual((1, 33, 1, 33), parse('try: pass\nexcept (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end(True))
        self.assertEqual((1, 38, 1, 33), parse('try: pass\nexcept (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end(True))

        if PYGE12:
            self.assertEqual((0, 3, 0, 0),  parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].f._loc_block_header_end(True))
            self.assertEqual((1, 17, 1, 17), parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end(True))
            self.assertEqual((1, 34, 1, 34), parse('try: pass\nexcept* (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end(True))
            self.assertEqual((1, 39, 1, 34), parse('try: pass\nexcept* (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_header_end(True))
            self.assertEqual((0, 12, 0, 11), parse('class cls[T]: pass').body[0].f._loc_block_header_end(True))

        self.assertEqual((0, 17, 0, 16), parse('def f(a) -> (int): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 28, 0, 27), parse('class cls(base, keyword=(1)): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 17, 0, 15), parse('class cls((base)): pass').body[0].f._loc_block_header_end(True))
        self.assertEqual((0, 12, 0, 11), parse('for a in (b): pass\nelse: pass').body[0].f._loc_block_header_end(True))

    def test__loc_call_pars(self):
        self.assertEqual((0, 4, 0, 6), FST('call()', 'exec').body[0].value._loc_call_pars())
        self.assertEqual((0, 4, 0, 7), FST('call(a)', 'exec').body[0].value._loc_call_pars())
        self.assertEqual((0, 4, 2, 1), FST('call(\na\n)', 'exec').body[0].value._loc_call_pars())
        self.assertEqual((0, 4, 2, 1), FST('call(\na, b=2\n)', 'exec').body[0].value._loc_call_pars())
        self.assertEqual((0, 4, 0, 12), FST('call(c="()")', 'exec').body[0].value._loc_call_pars())
        self.assertEqual((1, 0, 8, 1), FST('call\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n)', 'exec').body[0].value._loc_call_pars())
        self.assertEqual((1, 0, 8, 1), FST('"()("\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n)', 'exec').body[0].value._loc_call_pars())

    def test__loc_subscript_brackets(self):
        self.assertEqual((0, 1, 0, 4), FST('a[b]', 'exec').body[0].value._loc_subscript_brackets())
        self.assertEqual((0, 1, 0, 8), FST('a[b:c:d]', 'exec').body[0].value._loc_subscript_brackets())
        self.assertEqual((0, 1, 0, 7), FST('a["[]"]', 'exec').body[0].value._loc_subscript_brackets())
        self.assertEqual((1, 0, 7, 1), FST('a\\\n[\nb\n:\nc\n:\nd\n]', 'exec').body[0].value._loc_subscript_brackets())
        self.assertEqual((1, 0, 7, 1), FST('"[]["\\\n[\nb\n:\nc\n:\nd\n]', 'exec').body[0].value._loc_subscript_brackets())

    def test__loc_matchcls_pars(self):
        self.assertEqual((1, 9, 1, 11), FST('match a:\n case cls(): pass', 'exec').body[0].cases[0].pattern._loc_matchcls_pars())
        self.assertEqual((1, 9, 1, 12), FST('match a:\n case cls(a): pass', 'exec').body[0].cases[0].pattern._loc_matchcls_pars())
        self.assertEqual((1, 9, 3, 1), FST('match a:\n case cls(\na\n): pass', 'exec').body[0].cases[0].pattern._loc_matchcls_pars())
        self.assertEqual((1, 9, 3, 1), FST('match a:\n case cls(\na, b=2\n): pass', 'exec').body[0].cases[0].pattern._loc_matchcls_pars())
        self.assertEqual((1, 9, 1, 17), FST('match a:\n case cls(c="()"): pass', 'exec').body[0].cases[0].pattern._loc_matchcls_pars())
        self.assertEqual((2, 0, 9, 1), FST('match a:\n case cls\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n): pass', 'exec').body[0].cases[0].pattern._loc_matchcls_pars())

    def test__loc_operator_no_parent(self):
        self.assertEqual((1, 0, 1, 1), FST(Invert(), ['# pre', '~ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(Not(), ['# pre', 'not # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(UAdd(), ['# pre', '+ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(USub(), ['# pre', '- # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Add(), ['# pre', '+ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Sub(), ['# pre', '- # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Mult(), ['# pre', '* # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(MatMult(), ['# pre', '@ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Div(), ['# pre', '/ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Mod(), ['# pre', '% # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(LShift(), ['# pre', '<< # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(RShift(), ['# pre', '>> # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitOr(), ['# pre', '| # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitXor(), ['# pre', '^ # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitAnd(), ['# pre', '& # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(FloorDiv(), ['# pre', '// # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Pow(), ['# pre', '** # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Eq(), ['# pre', '== # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(NotEq(), ['# pre', '!= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Lt(), ['# pre', '< # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(LtE(), ['# pre', '<= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 1), FST(Gt(), ['# pre', '> # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(GtE(), ['# pre', '>= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Is(), ['# pre', 'is # post', '# next']).loc)
        self.assertEqual((1, 0, 2, 3), FST(IsNot(), ['# pre', 'is # inner', 'not # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(In(), ['# pre', 'in # post', '# next']).loc)
        self.assertEqual((1, 0, 2, 2), FST(NotIn(), ['# pre', 'not # inner', 'in # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(And(), ['# pre', 'and # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Or(), ['# pre', 'or # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Add(), ['# pre', '+= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Sub(), ['# pre', '-= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Mult(), ['# pre', '*= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(MatMult(), ['# pre', '@= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Div(), ['# pre', '/= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(Mod(), ['# pre', '%= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(LShift(), ['# pre', '<<= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(RShift(), ['# pre', '>>= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(BitOr(), ['# pre', '|= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(BitXor(), ['# pre', '^= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 2), FST(BitAnd(), ['# pre', '&= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(FloorDiv(), ['# pre', '//= # post', '# next']).loc)
        self.assertEqual((1, 0, 1, 3), FST(Pow(), ['# pre', '**= # post', '# next']).loc)

    def test__loc_maybe_dict_key(self):
        a = parse('''{
    a: """test
two  # fake comment start""", **b
            }''').body[0].value
        self.assertEqual((2, 30, 2, 32), a.f._loc_maybe_dict_key(1))

        a = parse('''{
    a: """test""", **  # comment
    b
            }''').body[0].value
        self.assertEqual((1, 19, 1, 21), a.f._loc_maybe_dict_key(1))

    def test__is_delimited_seq(self):
        self.assertFalse(FST('((pos < len(ranges))>>32),(r&((1<<32)-1))')._is_delimited_seq())
        self.assertFalse(FST('((1)+1),(1)')._is_delimited_seq())

    def test__maybe_add_line_continuations(self):
        f = FST(r'''
a + \
("""
*"""
"c")
''')
        self.assertFalse(f._maybe_add_line_continuations(whole=False))
        self.assertEqual(r'''
a + \
("""
*"""
"c")
''', f.src)
        f.verify('strict')

        f = FST(r'''
a + \
("""
*"""
"c")
''')
        f.right.unpar()
        self.assertTrue(f._maybe_add_line_continuations(whole=False))
        self.assertEqual(r'''
a + \
"""
*""" \
"c"
''', f.src)
        f.verify('strict')

        f = FST(r'''
a + \
("""
*"""
"c")
''')
        f.right.unpar()
        self.assertTrue(f._maybe_add_line_continuations(whole=True))
        self.assertEqual(r'''\
a + \
"""
*""" \
"c" \
''', f.src)
        f.verify('strict')

        f = FST(r'''(""" a
b # c""",
d)''')
        f.unpar(True)
        f._maybe_add_line_continuations()
        self.assertEqual(r'''""" a
b # c""", \
d''', f.src)

        f = FST(r'''(""" a
b # c""",
# comment0
  # comment1
e,  # comment2
d)  # comment3''')
        f.unpar(True)
        self.assertRaises(NodeError, f._maybe_add_line_continuations, del_comments=False)

        f = FST(r'''(""" a
b # c""",
# comment0
  # comment1
e,  # comment2
d)  # comment3''')
        f.unpar(True)
        f._maybe_add_line_continuations(del_comments=True)
        self.assertEqual(r'''""" a
b # c""", \
\
  \
e, \
d  # comment3''', f.src)

    def test__maybe_ins_separator(self):
        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, False, 0, 2)
        self.assertEqual('[a,#c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, True, 0, 2)
        self.assertEqual('[a, #c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, False, 0, 6)
        self.assertEqual('[a,#c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, True, 0, 6)
        self.assertEqual('[a, #c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, False, 1, 0)
        self.assertEqual('[a,#c\n]', f.src)

        f = FST('[a#c\n]')
        f._maybe_ins_separator(0, 2, True, 1, 0)
        self.assertEqual('[a, #c\n]', f.src)

    def test__maybe_fix_tuple(self):
        # parenthesize naked tuple preserve comments if present

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=0), ['# comment', ''])
        f._maybe_fix_tuple()
        self.assertEqual('(# comment\n)', f.src)
        f.verify()

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=1), [' # comment', ' '])
        f._maybe_fix_tuple()
        self.assertEqual('(# comment\n)', f.src)
        f.verify()

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=0), ['         ', ''])
        f._maybe_fix_tuple()
        self.assertEqual('()', f.src)
        f.verify()

    def test__maybe_fix_copy(self):
        f = FST.fromsrc('if 1:\n a\nelif 2:\n b')
        fc = f.a.body[0].orelse[0].f.copy()
        self.assertEqual(fc.lines[0], 'if 2:')
        fc.verify(raise_=True)

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual(fc.src, '1 +\n2')
        fc._maybe_fix_copy(pars=True)
        self.assertEqual(fc.src, '(1 +\n2)')
        fc.verify(raise_=True)

        f = FST.fromsrc('i = 1')
        self.assertIs(f.a.body[0].targets[0].ctx.__class__, Store)
        fc = f.a.body[0].targets[0].f.copy()
        self.assertIs(fc.a.ctx.__class__, Load)
        fc.verify(raise_=True)

        f = FST.fromsrc('if 1: pass\nelif 2: pass').a.body[0].orelse[0].f.copy()
        self.assertEqual('if 2: pass', f.src)

        f = FST.fromsrc('i, j = 1, 2').a.body[0].targets[0].f.copy(pars=False)
        self.assertEqual('i, j', f.src)
        fc._maybe_fix_copy(pars=True)
        self.assertEqual('i, j', f.src)  # because doesn't NEED them

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(pars=False)
        self.assertEqual('w := x,', f.src)
        f._maybe_fix_copy(pars=True)
        self.assertEqual('(w := x,)', f.src)

        f = FST.fromsrc('yield a1, a2')
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual('yield a1, a2', fc.src)
        fc._maybe_fix_copy(pars=True)
        self.assertEqual('yield a1, a2', fc.src)

        f = FST.fromsrc('yield from a')
        fc = f.a.body[0].value.f.copy()
        self.assertEqual('yield from a', fc.src)
        fc._maybe_fix_copy(pars=True)
        self.assertEqual('yield from a', fc.src)

        f = FST.fromsrc("""[
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format
]""".strip())
        fc = f.a.body[0].value.elts[0].f.copy(pars=False)
        self.assertEqual("""
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format""".strip(), fc.src)
        fc._maybe_fix_copy(pars=True)
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fc.src)

        f = FST.fromsrc("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))
        """.strip())
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual("""
(is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute))""".strip(), fc.src)
        fc._maybe_fix_copy(pars=True)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fc.src)

        if PYGE12:
            fc = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(pars=False)
            self.assertEqual('*tuple[int, ...]', fc.src)
            fc._maybe_fix_copy(pars=True)
            self.assertEqual('*tuple[int, ...],', fc.src)

        # don't parenthesize copied Slice even if it looks like it needs it

        self.assertEqual('b:\nc', (f := FST('a[b:\nc]').get('slice')).src)
        f.verify()

    def test__parenthesize_grouping(self):
        f = parse('[i]').f
        f.body[0].value.elts[0]._parenthesize_grouping()
        self.assertEqual('[(i)]', f.src)
        self.assertEqual((0, 0, 0, 5), f.loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].value.loc)
        self.assertEqual((0, 2, 0, 3), f.body[0].value.elts[0].loc)

        f = parse('a + b').f
        f.body[0].value.left._parenthesize_grouping()
        f.body[0].value.right._parenthesize_grouping()
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)

        f = parse('a + b').f
        f.body[0].value.right._parenthesize_grouping()
        f.body[0].value.left._parenthesize_grouping()
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)
        f.body[0].value._parenthesize_grouping()
        self.assertEqual('((a) + (b))', f.src)
        f.body[0].value.left._parenthesize_grouping()
        self.assertEqual('(((a)) + (b))', f.src)
        f.body[0].value.right._parenthesize_grouping()
        self.assertEqual('(((a)) + ((b)))', f.src)

        f = parse('call(i for i in j)').f
        f.body[0].value.args[0]._parenthesize_grouping()
        self.assertEqual(f.src, 'call((i for i in j))')
        f.body[0].value.args[0]._parenthesize_grouping()
        self.assertEqual(f.src, 'call(((i for i in j)))')

        f = parse('i').body[0].value.f.copy()
        f._put_src('\n# post', 0, 1, 0, 1, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_grouping(whole=True)
        self.assertEqual((1, 0, 1, 1), f.loc)
        self.assertEqual(f.root.src, '(# pre\ni\n# post)')

        f = parse('i').body[0].value.f.copy()
        f._put_src('\n# post', 0, 1, 0, 1, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_grouping(whole=False)
        self.assertEqual((1, 1, 1, 2), f.loc)
        self.assertEqual(f.root.src, '# pre\n(i)\n# post')

        # special rules for Starred

        f = FST('*\na')
        f._parenthesize_grouping()
        self.assertEqual('*(\na)', f.src)
        f.verify()

        f = FST('*\na')
        f._parenthesize_grouping(star_child=False)
        self.assertEqual('(*\na)', f.src)

    def test__delimit_node(self):
        # Tuple

        f = parse('i,').f
        f.body[0].value._delimit_node()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('a, b').f
        f.body[0].value._delimit_node()
        self.assertEqual('(a, b)', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.elts[1].loc)

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=True)
        self.assertEqual((0, 0, 2, 7), f.loc)
        self.assertEqual(f.src, '(# pre\ni,\n# post)')

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n(i,)\n# post')

        # MatchSequence

        f = FST('i,', pattern)
        f._delimit_node(delims='[]')
        self.assertEqual('[i,]', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 1, 0, 2), f.patterns[0].loc)

        f = FST('a, b', pattern)
        f._delimit_node(delims='[]')
        self.assertEqual('[a, b]', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 1, 0, 2), f.patterns[0].loc)
        self.assertEqual((0, 4, 0, 5), f.patterns[1].loc)

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=True, delims='[]')
        self.assertEqual((0, 0, 2, 7), f.loc)
        self.assertEqual(f.src, '[# pre\ni,\n# post]')

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=False, delims='[]')
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n[i,]\n# post')

    def test__unparenthesize_grouping(self):
        f = parse('a').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(a)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((a))').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(\n ( (a) )  \n)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((i,))').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('(\n ( (i,) ) \n)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=False)
        self.assertEqual(f.src, 'call((i for i in j))')
        self.assertEqual((0, 0, 0, 20), f.loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call( ( ( (i for i in j) ) ) )').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0]._unparenthesize_grouping(shared=False)
        self.assertEqual(f.src, 'call((i for i in j),)')
        self.assertEqual((0, 0, 0, 21), f.loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('( # pre\ni\n# post\n)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('( # pre\ni\n# post\n)').body[0].value.f.copy(pars=True)
        f._unparenthesize_grouping(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        f = parse('( # pre\n(i,)\n# post\n)').f
        f.body[0].value._unparenthesize_grouping(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)

        f = parse('( # pre\n(i)\n# post\n)').body[0].value.f.copy(pars=True)
        f._unparenthesize_grouping(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a)if(a)]', 'exec')
        f.body[0].value.generators[0].ifs[0]._unparenthesize_grouping(shared=False)
        f.body[0].value.generators[0].ifs[1]._unparenthesize_grouping(shared=False)
        self.assertEqual('[a for a in b if a if a]', f.src)

        f = FST('for(a)in b: pass', 'exec')
        f.body[0].target._unparenthesize_grouping(shared=False)
        self.assertEqual('for a in b: pass', f.src)

        f = FST('assert(test)', 'exec')
        f.body[0].test._unparenthesize_grouping(shared=False)
        self.assertEqual('assert test', f.src)

        f = FST('assert({test})', 'exec')
        f.body[0].test._unparenthesize_grouping(shared=False)
        self.assertEqual('assert{test}', f.src)

        # special rules for Starred

        f = FST('*(\na)')
        self.assertEqual('*(\na)', f.src)
        f._unparenthesize_grouping(star_child=False)
        self.assertEqual('*(\na)', f.src)
        f._unparenthesize_grouping()
        self.assertEqual('*a', f.src)
        f.verify()

        f = FST('*\na')
        f._parenthesize_grouping(star_child=False)
        self.assertEqual('(*\na)', f.src)
        f._unparenthesize_grouping()
        self.assertEqual('(*\na)', f.src)
        f._unparenthesize_grouping(star_child=False)
        self.assertEqual('*\na', f.src)
        f.verify()

    def test__undelimit_node(self):
        # Tuple

        f = parse('()').f
        f.body[0].value._undelimit_node()
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)

        f = parse('(i,)').f
        f.body[0].value._undelimit_node()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('(a, b)').f
        f.body[0].value._undelimit_node()
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.body[0].value.elts[1].loc)

        f = parse('( # pre\ni,\n# post\n)').f
        f.body[0].value._undelimit_node()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('( # pre\ni,\n# post\n)').body[0].value.f.copy()
        f._undelimit_node()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)

        # MatchSequence

        f = FST('()', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)

        f = FST('[i,]', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.patterns[0].loc)

        f = FST('(a, b)', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 1), f.patterns[0].loc)
        self.assertEqual((0, 3, 0, 4), f.patterns[1].loc)

        f = FST('[ # pre\ni,\n# post\n]', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.patterns[0].loc)

        f = FST('( # pre\ni,\n# post\n)', pattern)
        f._undelimit_node('patterns')
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 1), f.patterns[0].loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a,b)if(a,)if(a,b)]', 'exec')
        f.body[0].value.generators[0].ifs[0]._undelimit_node()
        f.body[0].value.generators[0].ifs[1]._undelimit_node()
        f.body[0].value.generators[0].ifs[2]._undelimit_node()
        self.assertEqual('[a for a in b if a,b if a,if a,b]', f.src)
        f.body[0].value.generators[0].ifs[0]._delimit_node()  # so that it will verify
        f.body[0].value.generators[0].ifs[1]._delimit_node()
        f.body[0].value.generators[0].ifs[2]._delimit_node()
        self.assertEqual('[a for a in b if (a,b) if (a,)if (a,b)]', f.src)
        f.verify()

        f = FST('for(a,b)in b: pass', 'exec')
        f.body[0].target._undelimit_node()
        self.assertEqual('for a,b in b: pass', f.src)
        f.verify()

        f = FST('for(a,)in b: pass', 'exec')
        f.body[0].target._undelimit_node()
        self.assertEqual('for a,in b: pass', f.src)
        f.verify()

        f = FST('case[1,2]as c: pass')
        f.pattern.pattern._undelimit_node('patterns')
        self.assertEqual('case 1,2 as c: pass', f.src)

        f = FST('case(1,2)as c: pass')
        f.pattern.pattern._undelimit_node('patterns')
        self.assertEqual('case 1,2 as c: pass', f.src)

    def test__normalize_block(self):
        a = parse('''
if 1: i ; j ; l ; m
            '''.strip())
        a.body[0].f._normalize_block()
        a.f.verify()
        self.assertEqual(a.f.src, 'if 1:\n    i ; j ; l ; m')

        a = parse('''
def f() -> int: \\
  i \\
  ; \\
  j
            '''.strip())
        a.body[0].f._normalize_block()
        a.f.verify()
        self.assertEqual(a.f.src, 'def f() -> int:\n    i \\\n  ; \\\n  j')

        a = parse('''def f(a = """ a
...   # something """): i = 2''')
        a.body[0].f._normalize_block()
        self.assertEqual(a.f.src, 'def f(a = """ a\n...   # something """):\n    i = 2')

    def test__elif_to_else_if(self):
        a = parse('''
if 1: pass
elif 2: pass
        '''.strip())
        a.body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
        '''.strip())
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
            '''.strip())

        a = parse('''
if 1: pass
elif 2: pass
return
        '''.strip())
        a.body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
return
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
    return
        '''.strip())
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
    return
            '''.strip())

        a = parse('''
if 1: pass
elif 2: pass
elif 3: pass
        '''.strip())
        a.body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
    elif 3: pass
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
    elif 3: pass
        '''.strip())
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
        elif 3: pass
            '''.strip())

    def test__get_indentable_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = "... \\\n2"\n else:\n  j \\\n=\\\n 2'
        ast = parse(src)

        self.assertEqual({1, 2, 5, 7, 8, 9, 10}, ast.f._get_indentable_lns(1))
        self.assertEqual({0, 1, 2, 5, 7, 8, 9, 10}, ast.f._get_indentable_lns(0))

        f = FST.fromsrc('''
def _splitext(p, sep, altsep, extsep):
    """Split the extension from a pathname.

    Extension is everything from the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work for text and bytes strings.

    sepIndex = p.rfind(sep)
            '''.strip())
        self.assertEqual({0, 1, 2, 3, 4, 5, 6, 7}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0, 1, 5, 6, 7}, f._get_indentable_lns(docstr=False))

        f = FST.fromsrc(r'''
_CookiePattern = re.compile(r"""
    \s*                            # Optional whitespace at start of cookie
    (?P<key>                       # Start of group 'key'
    [""" + _LegalKeyChars + r"""]+?   # Any word of at least one letter
    )                              # End of group 'key'
    (                              # Optional group: there may not be a value.
    \s*=\s*                          # Equal Sign
    (?P<val>                         # Start of group 'val'
    "(?:[^\\"]|\\.)*"                  # Any doublequoted string
    |                                  # or
    \w{3},\s[\w\d\s-]{9,11}\s[\d:]{8}\sGMT  # Special case for "expires" attr
    |                                  # or
    [""" + _LegalValueChars + r"""]*      # Any word or empty string
    )                                # End of group 'val'
    )?                             # End of optional value group
    \s*                            # Any number of spaces.
    (\s+|;|$)                      # Ending either at space, semicolon, or EOS.
    """, re.ASCII | re.VERBOSE)    # re.ASCII may be removed if safe.
            '''.strip())
        self.assertEqual({0}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0, 1}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
f"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0}, f._get_indentable_lns(docstr=True))  # because f-strings cannot be docstrings
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

    def test__touchall(self):
        a = parse('i = [1]').body[0]
        self.assertEqual(7, a.f.end_col)
        self.assertEqual(7, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.end_col_offset = 8
        a.value.end_col_offset = 8
        a.value.elts[0].end_col_offset = 7

        self.assertEqual(7, a.f.end_col)
        self.assertEqual(7, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall()
        self.assertEqual(7, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall(parents=True)
        self.assertEqual(8, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall(children=True)
        self.assertEqual(8, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(7, a.value.elts[0].f.end_col)

    def test__put_src(self):
        f = FST(Load(), [''])
        f._put_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['test'])
        f._put_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['testtest'])
        f._put_src('tost', 0, 0, 0, 8)
        self.assertEqual(f.lines, ['tost'])
        f._put_src('a\nb\nc', 0, 2, 0, 2)
        self.assertEqual(f.lines, ['toa', 'b', 'cst'])
        f._put_src('', 0, 3, 2, 1)
        self.assertEqual(f.lines, ['toast'])
        f._put_src('a\nb\nc\nd', 0, 0, 0, 5)
        self.assertEqual(f.lines, ['a', 'b', 'c', 'd'])
        f._put_src('efg\nhij', 1, 0, 2, 1)
        self.assertEqual(f.lines, ['a', 'efg', 'hij', 'd'])
        f._put_src('***', 1, 2, 2, 1)
        self.assertEqual(f.lines, ['a', 'ef***ij', 'd'])

    def test__offset(self):
        src = 'i = 1\nj = 2\nk = 3'

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 5, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1, exclude=ast.body[1].f)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1, exclude=ast.body[1].f, offset_excluded=False)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1, True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 3, 4), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 3, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1, True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 3, 4), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        def get():
            m = parse('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nbbbb\ncccc')

            m.body[0] = m.body[0].value
            m.body[1] = m.body[1].value
            m.body[2] = m.body[2].value

            m.body[0].lineno         = 1
            m.body[0].end_lineno     = 1
            m.body[0].col_offset     = 2
            m.body[0].end_col_offset = 6
            m.body[1].lineno         = 1
            m.body[1].end_lineno     = 1
            m.body[1].col_offset     = 6
            m.body[1].end_col_offset = 10
            m.body[2].lineno         = 1
            m.body[2].end_lineno     = 1
            m.body[2].col_offset     = 6
            m.body[2].end_col_offset = 6

            return m

        m = get()
        m.f._offset(0, 6, 0, 2, False, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, True, True)
        self.assertEqual((0, 2, 0, 8), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 8, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, False, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, True, False)
        self.assertEqual((0, 2, 0, 8), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, True)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, False)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 8, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, None)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, None, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

    def test__offset_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j = 2'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._offset_lns(lns, 1)
        self.assertEqual({1, 2, 5, 6, 7}, lns)
        self.assertEqual((0, 0, 7, 7), ast.f.loc)
        self.assertEqual((0, 0, 7, 8), ast.body[0].f.loc)
        self.assertEqual((1, 2, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 5, 1, 9), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._offset_lns(lns, 1)
        self.assertEqual({2, 5, 6, 7}, lns)
        self.assertEqual((1, 1, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 4, 1, 8), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._offset_lns(lns, 1)
        self.assertEqual(set(), lns)
        self.assertEqual((2, 2, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 6, 4, 3), ast.body[0].body[0].body[0].value.f.loc)

        src = 'i = 1\nj = 2\nk = 3\nl = \\\n4'
        ast = parse(src)
        off = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

        ast.f._offset_lns(off)
        self.assertEqual((0, 0, 4, 1), ast.f.loc)
        self.assertEqual((0, 0, 0, 5), ast.body[0].f.loc)
        self.assertEqual((0, 0, 0, 1), ast.body[0].targets[0].f.loc)
        self.assertEqual((0, 4, 0, 5), ast.body[0].value.f.loc)
        self.assertEqual((1, 1, 1, 6), ast.body[1].f.loc)
        self.assertEqual((1, 1, 1, 2), ast.body[1].targets[0].f.loc)
        self.assertEqual((1, 5, 1, 6), ast.body[1].value.f.loc)
        self.assertEqual((2, 2, 2, 7), ast.body[2].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[2].targets[0].f.loc)
        self.assertEqual((2, 6, 2, 7), ast.body[2].value.f.loc)
        self.assertEqual((3, 3, 4, 5), ast.body[3].f.loc)
        self.assertEqual((3, 3, 3, 4), ast.body[3].targets[0].f.loc)
        self.assertEqual((4, 4, 4, 5), ast.body[3].value.f.loc)

    def test__indent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._indent_lns('  ', lns)
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n   if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._indent_lns('  ', lns)
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._indent_lns('  ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._get_indentable_lns(1)
        ast.body[0].body[0].orelse[0].f._indent_lns('  ', lns)
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n  =\\\n   2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._indent_lns('  ', lns)
        self.assertEqual({1, 2}, lns)
        self.assertEqual('@decorator\n  class cls:\n   pass', ast.f.src)

    def test__dedent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._dedent_lns(' ', lns)
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\nif True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._get_indentable_lns(1)
        ast.body[0].body[0].orelse[0].f._dedent_lns(' ', lns)
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('@decorator\nclass cls:\n pass', ast.f.src)

        # ast = parse(src)
        # lns = ast.body[0].body[0].f._dedent_lns(' ', skip=0)
        # self.assertEqual({2}, lns)
        # self.assertEqual('@decorator\nclass cls:\npass', ast.f.src)

    def test__redent_lns(self):
        f = FST('''
[
a,
 b,
  c,
   d,
    e,
     f,
      g,

a,
 b,
  c,
   d,
    e,
     f,
      g,
]
            '''.strip())
        f._redent_lns('    ', '012')
        self.assertEqual('''
[
a,
b,
0c,
01d,
012e,
012 f,
012  g,

a,
b,
0c,
01d,
012e,
012 f,
012  g,
]
            '''.strip(), f.src)
        self.assertEqual((0, 0, 16, 1), f.loc)
        self.assertEqual((1, 0, 1, 1), f.elts[0].loc)
        self.assertEqual((2, 0, 2, 1), f.elts[1].loc)
        self.assertEqual((3, 1, 3, 2), f.elts[2].loc)
        self.assertEqual((4, 2, 4, 3), f.elts[3].loc)
        self.assertEqual((5, 3, 5, 4), f.elts[4].loc)
        self.assertEqual((6, 4, 6, 5), f.elts[5].loc)
        self.assertEqual((7, 5, 7, 6), f.elts[6].loc)
        self.assertEqual((9, 0, 9, 1), f.elts[7].loc)
        self.assertEqual((10, 0, 10, 1), f.elts[8].loc)
        self.assertEqual((11, 1, 11, 2), f.elts[9].loc)
        self.assertEqual((12, 2, 12, 3), f.elts[10].loc)
        self.assertEqual((13, 3, 13, 4), f.elts[11].loc)
        self.assertEqual((14, 4, 14, 5), f.elts[12].loc)
        self.assertEqual((15, 5, 15, 6), f.elts[13].loc)

        f = FST('''
    "OFFENDING RULE", self.ex.rule,
''')
        f.a.lineno = 1
        f.a.col_offset = f.a.end_col_offset = 0
        f.a.end_lineno = 3
        f._redent_lns('    ', ' ')
        self.assertEqual((0, 0, 2, 0), f.loc)
        self.assertEqual((1, 1, 1, 17), f.elts[0].loc)
        self.assertEqual((1, 19, 1, 31), f.elts[1].loc)
        self.assertEqual((1, 19, 1, 26), f.elts[1].value.loc)
        self.assertEqual((1, 19, 1, 23), f.elts[1].value.value.loc)


if __name__ == '__main__':
    unittest.main()
