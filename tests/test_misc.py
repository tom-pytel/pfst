#!/usr/bin/env python

import re
import unittest

from fst import *

from fst.common import PYGE12, PYGE13
from fst.fst_misc import get_trivia_params


class TestMisc(unittest.TestCase):
    def test_next_prev_frag(self):
        from fst.common import next_frag, prev_frag

        lines = '''
  # pre
i \\
here \\
j \\
  # post
k \\
            '''.split('\n')

        self.assertEqual((4, 0, 'j'), next_frag(lines, 3, 4, 7, 0, False, False))
        self.assertEqual((4, 0, 'j'), next_frag(lines, 3, 4, 7, 0, True, False))
        self.assertEqual((6, 0, 'k'), next_frag(lines, 4, 1, 7, 0, False, False))
        self.assertEqual((5, 2, '# post'), next_frag(lines, 4, 1, 7, 0, True, False))
        self.assertEqual((6, 0, 'k'), next_frag(lines, 5, 8, 7, 0, False, False))
        self.assertEqual((6, 0, 'k'), next_frag(lines, 5, 8, 7, 0, True, False))

        self.assertEqual((3, 5, '\\'), next_frag(lines, 3, 4, 7, 0, False, True))
        self.assertEqual((3, 5, '\\'), next_frag(lines, 3, 4, 7, 0, True, True))
        self.assertEqual((4, 2, '\\'), next_frag(lines, 4, 1, 7, 0, False, True))
        self.assertEqual((4, 2, '\\'), next_frag(lines, 4, 1, 7, 0, True, True))
        self.assertEqual((6, 0, 'k'), next_frag(lines, 5, 8, 7, 0, False, True))
        self.assertEqual((6, 0, 'k'), next_frag(lines, 5, 8, 7, 0, True, True))

        self.assertEqual((4, 0, 'j'), next_frag(lines, 3, 4, 7, 0, False, None))
        self.assertEqual((4, 0, 'j'), next_frag(lines, 3, 4, 7, 0, True, None))
        self.assertEqual(None, next_frag(lines, 4, 1, 7, 0, False, None))
        self.assertEqual((5, 2, '# post'), next_frag(lines, 4, 1, 7, 0, True, None))
        self.assertEqual(None, next_frag(lines, 5, 8, 7, 0, False, None))
        self.assertEqual(None, next_frag(lines, 5, 8, 7, 0, True, None))

        self.assertEqual(None, prev_frag(lines, 0, 0, 2, 0, False, False))
        self.assertEqual((1, 2, '# pre'), prev_frag(lines, 0, 0, 2, 0, True, False))
        self.assertEqual((2, 0, 'i'), prev_frag(lines, 0, 0, 3, 0, False, False))
        self.assertEqual((2, 0, 'i'), prev_frag(lines, 0, 0, 3, 0, True, False))
        self.assertEqual((4, 0, 'j'), prev_frag(lines, 0, 0, 6, 0, False, False))
        self.assertEqual((5, 2, '# post'), prev_frag(lines, 0, 0, 6, 0, True, False))

        self.assertEqual(None, prev_frag(lines, 0, 0, 2, 0, False, True))
        self.assertEqual((1, 2, '# pre'), prev_frag(lines, 0, 0, 2, 0, True, True))
        self.assertEqual((2, 2, '\\'), prev_frag(lines, 0, 0, 3, 0, False, True))
        self.assertEqual((2, 2, '\\'), prev_frag(lines, 0, 0, 3, 0, True, True))
        self.assertEqual((4, 2, '\\'), prev_frag(lines, 0, 0, 6, 0, False, True))
        self.assertEqual((5, 2, '# post'), prev_frag(lines, 0, 0, 6, 0, True, True))

        self.assertEqual(None, prev_frag(lines, 0, 0, 1, 7, False, None))
        self.assertEqual((1, 2, '# pre'), prev_frag(lines, 0, 0, 1, 7, True, None))
        self.assertEqual((2, 0, 'i'), prev_frag(lines, 0, 0, 3, 0, False, None))
        self.assertEqual((2, 0, 'i'), prev_frag(lines, 0, 0, 3, 0, True, None))
        self.assertEqual((4, 0, 'j'), prev_frag(lines, 0, 0, 5, 3, False, None))
        self.assertEqual((5, 2, '#'), prev_frag(lines, 0, 0, 5, 3, True, None))

        self.assertEqual((1, 1, 'a'), next_frag(['\\', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual((2, 1, 'a'), next_frag(['\\', '\\', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual(None, next_frag(['\\', '', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual((1, 1, '# c'), next_frag(['\\', ' # c'], 0, 0, 100, 0, True, None))
        self.assertEqual(None, next_frag(['\\', ' # c', 'a'], 0, 0, 100, 0, False, None))

        self.assertEqual((0, 0, 'a'), prev_frag(['a \\', ''], 0, 0, 1, 0, True, None))
        self.assertEqual((0, 0, 'a'), prev_frag(['a \\', '\\', ''], 0, 0, 2, 0, True, None))
        self.assertEqual((0, 0, 'a'), prev_frag(['a \\', '\\', '\\', ''], 0, 0, 3, 0, True, None))
        self.assertEqual((1, 1, '# c'), prev_frag(['a \\', ' # c'], 0, 0, 1, 4, True, None))
        self.assertEqual((1, 1, '# '), prev_frag(['a \\', ' # c'], 0, 0, 1, 3, True, None))
        self.assertEqual((1, 1, '#'), prev_frag(['a \\', ' # c'], 0, 0, 1, 2, True, None))
        self.assertEqual((0, 0, 'a'), prev_frag(['a \\', ' # c'], 0, 0, 1, 1, True, None))
        self.assertEqual((1, 1, '# c'), prev_frag(['a', ' # c'], 0, 0, 1, 4, True, None))
        self.assertEqual((1, 1, '# '), prev_frag(['a', ' # c'], 0, 0, 1, 3, True, None))
        self.assertEqual((1, 1, '#'), prev_frag(['a', ' # c'], 0, 0, 1, 2, True, None))
        self.assertEqual(None, prev_frag(['a', ' # c'], 0, 0, 1, 1, True, None))

        state = []
        self.assertEqual((0, 4, '# c \\'), prev_frag(['a b # c \\'], 0, 0, 0, 9, True, True, state=state))
        self.assertEqual((0, 2, 'b'), prev_frag(['a b # c \\'], 0, 0, 0, 4, True, True, state=state))
        self.assertEqual((0, 0, 'a'), prev_frag(['a b # c \\'], 0, 0, 0, 2, True, True, state=state))
        self.assertEqual(None, prev_frag(['a b # c \\'], 0, 0, 0, 0, True, True, state=state))

        state = []
        self.assertEqual((0, 2, 'b'), prev_frag(['a b # c \\'], 0, 0, 0, 9, False, True, state=state))
        self.assertEqual((0, 0, 'a'), prev_frag(['a b # c \\'], 0, 0, 0, 2, False, True, state=state))
        self.assertEqual(None, prev_frag(['a b # c \\'], 0, 0, 0, 0, False, True, state=state))

        state = []
        self.assertEqual((0, 2, 'b'), prev_frag(['a b # c \\'], 0, 0, 0, 9, False, None, state=state))
        self.assertEqual((0, 0, 'a'), prev_frag(['a b # c \\'], 0, 0, 0, 2, False, None, state=state))
        self.assertEqual(None, prev_frag(['a b # c \\'], 0, 0, 0, 0, False, None, state=state))

        state = []
        self.assertEqual((0, 4, '# c \\'), prev_frag(['a b # c \\'], 0, 0, 0, 9, True, None, state=state))
        self.assertEqual((0, 2, 'b'), prev_frag(['a b # c \\'], 0, 0, 0, 4, True, None, state=state))
        self.assertEqual((0, 0, 'a'), prev_frag(['a b # c \\'], 0, 0, 0, 2, True, None, state=state))
        self.assertEqual(None, prev_frag(['a b # c \\'], 0, 0, 0, 0, True, None, state=state))

        state = []
        self.assertEqual((0, 4, 'c'), prev_frag(['a b c \\'], 0, 0, 0, 9, True, None, state=state))
        self.assertEqual((0, 2, 'b'), prev_frag(['a b c \\'], 0, 0, 0, 4, True, None, state=state))
        self.assertEqual((0, 0, 'a'), prev_frag(['a b c \\'], 0, 0, 0, 2, True, None, state=state))
        self.assertEqual(None, prev_frag(['a b c \\'], 0, 0, 0, 0, True, None, state=state))

        self.assertEqual((0, 0, '('), prev_frag(['(# comment', ''], 0, 0, 1, 0))
        self.assertEqual((0, 1, '# comment'), prev_frag(['(# comment', ''], 0, 0, 1, 0, True))
        self.assertEqual((0, 0, '('), prev_frag(['(\\', ''], 0, 0, 1, 0))
        self.assertEqual((0, 0, '('), prev_frag(['(\\', ''], 0, 0, 1, 0, False, False))
        self.assertEqual((0, 1, '\\'), prev_frag(['(\\', ''], 0, 0, 1, 0, False, True))
        self.assertEqual((0, 0, '('), prev_frag(['(\\', ''], 0, 0, 1, 0, False, None))
        self.assertEqual((0, 0, '('), prev_frag(['(\\', ''], 0, 0, 1, 0, True, False))
        self.assertEqual((0, 1, '\\'), prev_frag(['(\\', ''], 0, 0, 1, 0, True, True))
        self.assertEqual((0, 0, '('), prev_frag(['(\\', ''], 0, 0, 1, 0, True, None))

    def test_next_prev_find(self):
        from fst.common import next_find, prev_find

        lines = '''
  ; \\
  # hello
  \\
  # world
  # word
            '''.split('\n')

        self.assertEqual((1, 2), prev_find(lines, 0, 0, 5, 0, ';'))
        self.assertEqual((1, 2), prev_find(lines, 0, 0, 5, 0, ';', True))
        self.assertEqual(None, prev_find(lines, 0, 0, 5, 0, ';', True, comment=True))
        self.assertEqual(None, prev_find(lines, 0, 0, 5, 0, ';', True, lcont=True))
        self.assertEqual((1, 2), prev_find(lines, 0, 0, 2, 0, ';', True, lcont=None))
        self.assertEqual(None, prev_find(lines, 0, 0, 3, 0, ';', True, lcont=None))
        self.assertEqual((1, 2), prev_find(lines, 0, 0, 5, 0, ';', False, comment=True, lcont=True))
        self.assertEqual(None, prev_find(lines, 0, 0, 5, 0, ';', True, comment=True, lcont=True))
        self.assertEqual((5, 2), prev_find(lines, 0, 0, 6, 0, '# word', False, comment=True, lcont=True))
        self.assertEqual((4, 2), prev_find(lines, 0, 0, 6, 0, '# world', False, comment=True, lcont=True))
        self.assertEqual(None, prev_find(lines, 0, 0, 5, 0, '# world', False, comment=False, lcont=True))
        self.assertEqual((2, 2), prev_find(lines, 0, 0, 5, 0, '# hello', False, comment=True, lcont=True))
        self.assertEqual(None, prev_find(lines, 0, 0, 5, 0, '# hello', True, comment=True, lcont=True))
        self.assertEqual((0, 2), prev_find(['i # test'], 0, 0, 0, 8, '# test', True, comment=True))

        lines = '''
  \\
  # hello
  ; \\
  # world
  # word
            '''.split('\n')

        self.assertEqual((3, 2), next_find(lines, 2, 0, 6, 0, ';'))
        self.assertEqual((3, 2), next_find(lines, 2, 0, 6, 0, ';', True))
        self.assertEqual(None, next_find(lines, 2, 0, 6, 0, ';', True, comment=True))
        self.assertEqual((3, 2), next_find(lines, 2, 0, 6, 0, ';', True, lcont=True))
        self.assertEqual(None, next_find(lines, 2, 0, 6, 0, ';', True, lcont=None))
        self.assertEqual(None, next_find(lines, 3, 3, 6, 0, '# word', False))
        self.assertEqual(None, next_find(lines, 3, 3, 6, 0, '# word', True))
        self.assertEqual(None, next_find(lines, 3, 3, 6, 0, '# word', True, comment=True))
        self.assertEqual((5, 2), next_find(lines, 3, 3, 6, 0, '# word', False, comment=True))
        self.assertEqual(None, next_find(lines, 3, 3, 6, 0, '# word', False, comment=True, lcont=None))
        self.assertEqual((4, 2), next_find(lines, 3, 0, 6, 0, '# world', False, comment=True, lcont=None))
        self.assertEqual(None, next_find(lines, 3, 0, 6, 0, '# word', False, comment=True, lcont=None))
        self.assertEqual((5, 2), next_find(lines, 3, 0, 6, 0, '# word', False, comment=True, lcont=True))
        self.assertEqual(None, next_find(lines, 3, 0, 6, 0, '# word', True, comment=True, lcont=True))

    def test_next_find_re(self):
        from fst.common import next_find_re

        lines = '''
  \\
  # hello
  aaab ; \\
  # world
b # word
            '''.split('\n')
        pat = re.compile('a*b')

        self.assertEqual((3, 2, 'aaab'), next_find_re(lines, 2, 0, 6, 0, pat))
        self.assertEqual((3, 2, 'aaab'), next_find_re(lines, 2, 0, 6, 0, pat, True))
        self.assertEqual(None, next_find_re(lines, 2, 0, 6, 0, pat, True, comment=True))
        self.assertEqual((3, 2, 'aaab'), next_find_re(lines, 2, 0, 6, 0, pat, True, lcont=True))
        self.assertEqual(None, next_find_re(lines, 2, 0, 6, 0, pat, True, lcont=None))
        self.assertEqual((3, 3, 'aab'), next_find_re(lines, 3, 3, 6, 0, pat, False))
        self.assertEqual((3, 4, 'ab'), next_find_re(lines, 3, 4, 6, 0, pat, False))
        self.assertEqual((3, 5, 'b'), next_find_re(lines, 3, 5, 6, 0, pat, True))
        self.assertEqual(None, next_find_re(lines, 3, 6, 6, 0, pat, True))
        self.assertEqual((5, 0, 'b'), next_find_re(lines, 3, 6, 6, 0, pat, False))
        self.assertEqual(None, next_find_re(lines, 3, 6, 6, 0, pat, True))
        self.assertEqual((5, 0, 'b'), next_find_re(lines, 3, 6, 6, 0, pat, False, comment=True))
        self.assertEqual(None, next_find_re(lines, 3, 6, 6, 0, pat, False, comment=True, lcont=None))
        self.assertEqual((5, 0, 'b'), next_find_re(lines, 4, 0, 6, 0, pat, False, comment=False, lcont=False))
        self.assertEqual(None, next_find_re(lines, 4, 0, 6, 0, pat, False, comment=True, lcont=None))
        self.assertEqual((5, 0, 'b'), next_find_re(lines, 4, 0, 6, 0, pat, False, comment=True, lcont=True))
        self.assertEqual(None, next_find_re(lines, 4, 0, 6, 0, pat, True, comment=True, lcont=True))

    def test_leading_trivia(self):
        from fst.fst_misc import leading_trivia

        self.assertEqual(((0, 0), None, ''), leading_trivia(['a'], 0, 0, 0, 0, 'all', True))

        ls = '''
[a,

# 1
   b, c]
        '''.strip().split('\n')

        self.assertEqual(((2, 0), (1, 0), '   '), leading_trivia(ls, 0, 3, 3, 3, 'all', True))
        self.assertEqual(((3, 6), None, None), leading_trivia(ls, 0, 3, 3, 6, 'all', True))

        ls = '''
[a,

# 1

 \\
# 2
  # 3
  b]
        '''.strip().split('\n')

        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 'none', 0))
        self.assertEqual(((5, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 'block', 0))
        self.assertEqual(((5, 0), (4, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 'block', 1))
        self.assertEqual(((5, 0), (3, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 'block', 2))
        self.assertEqual(((5, 0), (3, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 'block', 3))
        self.assertEqual(((2, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 'all', 0))
        self.assertEqual(((2, 0), (1, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 'all', 1))
        self.assertEqual(((2, 0), (1, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 'all', 2))

        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 8, 0))
        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 7, 0))
        self.assertEqual(((6, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 6, 0))
        self.assertEqual(((5, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 5, 0))
        self.assertEqual(((4, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 4, 0))
        self.assertEqual(((3, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 3, 0))
        self.assertEqual(((2, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 2, 0))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 1, 0))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 0, 0))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, -1, 0))

        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 8, 1))
        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 7, 1))
        self.assertEqual(((6, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 6, 1))
        self.assertEqual(((5, 0), (4, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 5, 1))
        self.assertEqual(((4, 0), (3, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 4, 1))
        self.assertEqual(((3, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 3, 1))
        self.assertEqual(((2, 0), (1, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 2, 1))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 1, 1))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 0, 1))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, -1, 1))

        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 8, 2))
        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 7, 2))
        self.assertEqual(((6, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 6, 2))
        self.assertEqual(((5, 0), (3, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 5, 2))
        self.assertEqual(((4, 0), (3, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 4, 2))
        self.assertEqual(((3, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 3, 2))
        self.assertEqual(((2, 0), (1, 0), '  '), leading_trivia(ls, 0, 3, 7, 2, 2, 2))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 1, 2))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, 0, 2))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 0, 3, 7, 2, -1, 2))

        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 'none', 0))
        self.assertEqual(((5, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 'block', 0))
        self.assertEqual(((5, 0), (4, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 'block', 1))
        self.assertEqual(((5, 0), (3, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 'block', 2))
        self.assertEqual(((5, 0), (3, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 'block', 3))
        self.assertEqual(((2, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 'all', 0))
        self.assertEqual(((2, 0), (1, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 'all', 1))
        self.assertEqual(((2, 0), (1, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 'all', 2))

        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 8, 0))
        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 7, 0))
        self.assertEqual(((6, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 6, 0))
        self.assertEqual(((5, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 5, 0))
        self.assertEqual(((4, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 4, 0))
        self.assertEqual(((3, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 3, 0))
        self.assertEqual(((2, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 2, 0))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 1, 0))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 0, 0))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, -1, 0))

        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 8, 1))
        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 7, 1))
        self.assertEqual(((6, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 6, 1))
        self.assertEqual(((5, 0), (4, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 5, 1))
        self.assertEqual(((4, 0), (3, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 4, 1))
        self.assertEqual(((3, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 3, 1))
        self.assertEqual(((2, 0), (1, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 2, 1))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 1, 1))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 0, 1))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, -1, 1))

        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 8, 2))
        self.assertEqual(((7, 2), (7, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 7, 2))
        self.assertEqual(((6, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 6, 2))
        self.assertEqual(((5, 0), (3, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 5, 2))
        self.assertEqual(((4, 0), (3, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 4, 2))
        self.assertEqual(((3, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 3, 2))
        self.assertEqual(((2, 0), (1, 0), '  '), leading_trivia(ls, 1, 0, 7, 2, 2, 2))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 1, 2))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, 0, 2))
        self.assertEqual(((1, 0), None, '  '), leading_trivia(ls, 1, 0, 7, 2, -1, 2))

        ls = '''
[a



]
        '''.strip().split('\n')

        self.assertEqual(((4, 0), None, ''), leading_trivia(ls, 0, 2, 4, 0, 'all', 0))
        self.assertEqual(((4, 0), (3, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 'all', 1))
        self.assertEqual(((4, 0), (2, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 'all', 2))
        self.assertEqual(((4, 0), (1, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 'all', 3))

        self.assertEqual(((4, 0), None, ''), leading_trivia(ls, 0, 2, 4, 0, 4, 0))
        self.assertEqual(((4, 0), (3, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 4, 1))
        self.assertEqual(((4, 0), (2, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 4, 2))
        self.assertEqual(((4, 0), (1, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 4, 3))

        self.assertEqual(((3, 0), None, ''), leading_trivia(ls, 0, 2, 4, 0, 3, 0))
        self.assertEqual(((3, 0), (2, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 3, 1))
        self.assertEqual(((3, 0), (1, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 3, 2))
        self.assertEqual(((3, 0), (1, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 3, 3))

        self.assertEqual(((2, 0), None, ''), leading_trivia(ls, 0, 2, 4, 0, 2, 0))
        self.assertEqual(((2, 0), (1, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 2, 1))
        self.assertEqual(((2, 0), (1, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 2, 2))
        self.assertEqual(((2, 0), (1, 0), ''), leading_trivia(ls, 0, 2, 4, 0, 2, 3))

        self.assertEqual(((1, 0), None, ''), leading_trivia(ls, 0, 2, 4, 0, 1, 0))
        self.assertEqual(((1, 0), None, ''), leading_trivia(ls, 0, 2, 4, 0, 1, 1))
        self.assertEqual(((1, 0), None, ''), leading_trivia(ls, 0, 2, 4, 0, 1, 2))
        self.assertEqual(((1, 0), None, ''), leading_trivia(ls, 0, 2, 4, 0, 1, 3))

        # special empty space handling

        self.assertEqual(((2, 3), None, None), leading_trivia([' ', ' ', 'a; b'], 0, 0, 2, 3, 'none', True))
        self.assertEqual(((2, 3), None, None), leading_trivia([' ', ' ', 'a; b'], 0, 0, 2, 3, 'all', True))
        self.assertEqual(((2, 3), None, None), leading_trivia([' ', ' ', 'a; b'], 0, 0, 2, 3, 'block', True))

        self.assertEqual(((2, 0), None, ''), leading_trivia([' ', ' ', 'a'], 0, 0, 2, 0, 'all', False))
        self.assertEqual(((2, 0), None, ''), leading_trivia([' ', ' ', 'a'], 0, 0, 2, 0, 'all', 0))
        self.assertEqual(((2, 0), (1, 0), ''), leading_trivia([' ', ' ', 'a'], 0, 0, 2, 0, 'all', 1))
        self.assertEqual(((2, 0), (0, 0), ''), leading_trivia([' ', ' ', 'a'], 0, 0, 2, 0, 'all', 2))
        self.assertEqual(((2, 0), (0, 0), ''), leading_trivia([' ', ' ', 'a'], 0, 0, 2, 0, 'all', 3))
        self.assertEqual(((2, 0), (0, 0), ''), leading_trivia([' ', ' ', 'a'], 0, 0, 2, 0, 'all', True))

        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'all', False))
        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'all', 0))
        self.assertEqual(((2, 1), (1, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'all', 1))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'all', 2))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'all', 3))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'all', True))

        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'block', False))
        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'block', 0))
        self.assertEqual(((2, 1), (1, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'block', 1))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'block', 2))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'block', 3))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 'block', True))

        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 2, False))
        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 2, 0))
        self.assertEqual(((2, 1), (1, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 2, 1))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 2, 2))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 2, 3))
        self.assertEqual(((2, 1), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 2, True))

        self.assertEqual(((1, 0), None, ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 1, False))
        self.assertEqual(((1, 0), None, ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 1, 0))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 1, 1))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 1, 2))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 1, 3))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 1, True))

        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 0, False))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 0, 0))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 0, 1))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 0, 2))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 0, 3))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', ' ', ' a'], 0, 0, 2, 1, 0, True))

        # special empty space handling with comment

        self.assertEqual(((2, 3), None, None), leading_trivia([' ', '# c', 'a; b'], 0, 0, 2, 3, 'none', True))
        self.assertEqual(((2, 3), None, None), leading_trivia([' ', '# c', 'a; b'], 0, 0, 2, 3, 'all', True))
        self.assertEqual(((2, 3), None, None), leading_trivia([' ', '# c', 'a; b'], 0, 0, 2, 3, 'block', True))

        self.assertEqual(((1, 0), None, ''), leading_trivia([' ', '# c', 'a'], 0, 0, 2, 0, 'all', False))
        self.assertEqual(((1, 0), None, ''), leading_trivia([' ', '# c', 'a'], 0, 0, 2, 0, 'all', 0))
        self.assertEqual(((1, 0), (0, 0), ''), leading_trivia([' ', '# c', 'a'], 0, 0, 2, 0, 'all', 1))
        self.assertEqual(((1, 0), (0, 0), ''), leading_trivia([' ', '# c', 'a'], 0, 0, 2, 0, 'all', 2))
        self.assertEqual(((1, 0), (0, 0), ''), leading_trivia([' ', '# c', 'a'], 0, 0, 2, 0, 'all', 3))
        self.assertEqual(((1, 0), (0, 0), ''), leading_trivia([' ', '# c', 'a'], 0, 0, 2, 0, 'all', True))

        self.assertEqual(((1, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'all', False))
        self.assertEqual(((1, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'all', 0))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'all', 1))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'all', 2))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'all', 3))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'all', True))

        self.assertEqual(((1, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'block', False))
        self.assertEqual(((1, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'block', 0))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'block', 1))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'block', 2))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'block', 3))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 'block', True))

        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 2, False))
        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 2, 0))
        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 2, 1))
        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 2, 2))
        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 2, 3))
        self.assertEqual(((2, 1), (2, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 2, True))

        self.assertEqual(((1, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 1, False))
        self.assertEqual(((1, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 1, 0))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 1, 1))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 1, 2))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 1, 3))
        self.assertEqual(((1, 0), (0, 0), ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 1, True))

        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 0, False))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 0, 0))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 0, 1))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 0, 2))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 0, 3))
        self.assertEqual(((0, 0), None, ' '), leading_trivia([' ', '# c', ' a'], 0, 0, 2, 1, 0, True))

    def test_trailing_trivia(self):
        from fst.fst_misc import trailing_trivia

        self.assertEqual(((0, 1), (0, 4), True), trailing_trivia(['a   '], 0, 4, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 4), True), trailing_trivia(['a  \\'], 0, 4, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 3), False), trailing_trivia(['a  b'], 0, 4, 0, 1, 'all', True))
        self.assertEqual(((0, 4), None, True), trailing_trivia(['a #c'], 0, 4, 0, 1, 'all', True))
        self.assertEqual(((0, 4), None, True), trailing_trivia(['a# c'], 0, 4, 0, 1, 'all', True))

        self.assertRaises(AssertionError, trailing_trivia, ['a   '], -1, 4, 0, 1, 'all', True)
        self.assertRaises(AssertionError, trailing_trivia, ['a   '], 0, 0, 0, 1, 'all', True)

        self.assertEqual(((0, 1), None, True), trailing_trivia(['a'], 0, 1, 0, 1, 'all', True))
        self.assertEqual(((0, 1), None, False), trailing_trivia(['a   '], 0, 1, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 2), False), trailing_trivia(['a   '], 0, 2, 0, 1, 'all', True))

        self.assertEqual(((0, 1), None, False), trailing_trivia(['ab'], 0, 2, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 2), False), trailing_trivia(['a c'], 0, 3, 0, 1, 'all', True))
        self.assertEqual(((0, 1), None, False), trailing_trivia(['a#c'], 0, 3, 0, 1, 'none', True))
        self.assertEqual(((0, 1), (0, 2), False), trailing_trivia(['a # c'], 0, 5, 0, 1, 'none', True))

        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a ', ' b'], 1, 2, 0, 1, 'line', True))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a # c', ''], 1, 0, 0, 1, 'line', True))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a # c', ' b'], 1, 2, 0, 1, 'line', True))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a # c', '', ' b'], 2, 2, 0, 1, 'line', False))

        self.assertEqual(((1, 0), (2, 0), True), trailing_trivia(['a # c', '', ' b'], 2, 2, 0, 1, 'line', True))
        self.assertEqual(((1, 0), (2, 0), True), trailing_trivia(['a # c', '', ''], 2, 0, 0, 1, 'line', True))
        self.assertEqual(((1, 0), (2, 0), True), trailing_trivia(['a # c', '', '# c'], 2, 3, 0, 1, 'line', True))
        self.assertEqual(((1, 0), (2, 0), True), trailing_trivia(['a # c', '', '', ''], 3, 0, 0, 1, 'line', 1))
        self.assertEqual(((1, 0), (3, 0), True), trailing_trivia(['a # c', '', '', ''], 3, 0, 0, 1, 'line', 2))

        ls = '''
[a, # 1
# 2

 \\
  # 3

  b]
        '''.strip().split('\n')

        self.assertEqual(((0, 3), (0, 4), False), trailing_trivia(ls, 6, 2, 0, 3, 'none', 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 'line', 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 'line', 1))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 'line', 2))
        self.assertEqual(((2, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 'block', 0))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 'block', 1))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 'block', 2))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 'block', 3))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 'all', 0))
        self.assertEqual(((5, 0), (6, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 'all', 1))
        self.assertEqual(((5, 0), (6, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 'all', 2))

        self.assertEqual(((0, 3), (0, 4), False), trailing_trivia(ls, 6, 2, 0, 3, -1, 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 0, 0))
        self.assertEqual(((2, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 1, 0))
        self.assertEqual(((3, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 2, 0))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 3, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 4, 0))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 5, 0))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 6, 0))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 7, 0))

        self.assertEqual(((0, 3), (0, 4), False), trailing_trivia(ls, 6, 2, 0, 3, -1, 1))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 0, 1))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 1, 1))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 2, 1))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 3, 1))
        self.assertEqual(((5, 0), (6, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 4, 1))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 5, 1))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 6, 1))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 7, 1))

        self.assertEqual(((0, 3), (0, 4), False), trailing_trivia(ls, 6, 2, 0, 3, -1, 2))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 0, 2))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 1, 2))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 2, 2))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 3, 2))
        self.assertEqual(((5, 0), (6, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 4, 2))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 5, 2))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 6, 2))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 7, 2))

        self.assertEqual(((0, 3), (0, 4), False), trailing_trivia(ls, 5, 0, 0, 3, 'none', 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 'line', 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 'line', 1))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 'line', 2))
        self.assertEqual(((2, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 'block', 0))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 'block', 1))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 'block', 2))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 'block', 3))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 'all', 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 'all', 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 'all', 2))

        self.assertEqual(((0, 3), (0, 4), False), trailing_trivia(ls, 5, 0, 0, 3, -1, 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 0, 0))
        self.assertEqual(((2, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 1, 0))
        self.assertEqual(((3, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 2, 0))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 3, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 4, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 5, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 6, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 7, 0))

        self.assertEqual(((0, 3), (0, 4), False), trailing_trivia(ls, 5, 0, 0, 3, -1, 1))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 0, 1))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 1, 1))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 2, 1))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 3, 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 4, 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 5, 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 6, 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 7, 1))

        self.assertEqual(((0, 3), (0, 4), False), trailing_trivia(ls, 5, 0, 0, 3, -1, 2))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 0, 2))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 1, 2))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 2, 2))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 3, 2))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 4, 2))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 5, 2))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 6, 2))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 7, 2))

        ls = '''
[a



]
        '''.strip().split('\n')

        self.assertEqual(((0, 2), (1, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 'all', 0))
        self.assertEqual(((0, 2), (2, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 'all', 1))
        self.assertEqual(((0, 2), (3, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 'all', 2))
        self.assertEqual(((0, 2), (4, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 'all', 3))

        self.assertEqual(((0, 2), (1, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 0, 0))
        self.assertEqual(((0, 2), (2, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 0, 1))
        self.assertEqual(((0, 2), (3, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 0, 2))
        self.assertEqual(((0, 2), (4, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 0, 3))

        self.assertEqual(((2, 0), None, True), trailing_trivia(ls, 4, 0, 0, 2, 1, 0))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 1, 1))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 1, 2))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 1, 3))

        self.assertEqual(((3, 0), None, True), trailing_trivia(ls, 4, 0, 0, 2, 2, 0))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 2, 1))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 2, 2))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 4, 0, 0, 2, 2, 3))

        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 4, 0, 0, 2, 3, 0))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 4, 0, 0, 2, 3, 1))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 4, 0, 0, 2, 3, 2))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 4, 0, 0, 2, 3, 3))

        # ends line on first line if hit bound and bound at end

        self.assertEqual(((0, 1), None, True), trailing_trivia(['a'], 0, 1, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), None, False), trailing_trivia(['a '], 0, 1, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (0, 2), True), trailing_trivia(['a '], 0, 2, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (0, 2), False), trailing_trivia(['a  '], 0, 2, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a  '], 0, 3, 0, 1, 'all', 0))

        # hit bound not non-start line

        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a ', ''], 1, 1, 0, 1, 'all', 0))

        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a', ''], 1, 0, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a', ' '], 1, 1, 0, 1, 'all', 0))

        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a', ''], 1, 0, 0, 1, 'all', 1))
        self.assertEqual(((0, 1), (1, 1), True), trailing_trivia(['a', ' '], 1, 1, 0, 1, 'all', 1))

        self.assertEqual(((1, 3), None, True), trailing_trivia(['a', '# c'], 1, 3, 0, 1, 'all', 0))
        self.assertEqual(((2, 0), None, True), trailing_trivia(['a', '# c', ''], 2, 0, 0, 1, 'all', 0))
        self.assertEqual(((2, 0), None, True), trailing_trivia(['a', '# c', ''], 2, 0, 0, 1, 'all', 1))
        self.assertEqual(((2, 0), (2, 1), True), trailing_trivia(['a', '# c', ' '], 2, 1, 0, 1, 'all', 1))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(['a', '# c', ' ', ''], 3, 0, 0, 1, 'all', 1))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(['a', '# c', ' ', ' '], 3, 1, 0, 1, 'all', 1))
        self.assertEqual(((2, 0), (3, 1), True), trailing_trivia(['a', '# c', ' ', ' '], 3, 1, 0, 1, 'all', 2))
        self.assertEqual(((2, 0), (4, 0), True), trailing_trivia(['a', '# c', ' ', ' ', ''], 4, 0, 0, 1, 'all', 2))

        # returning end of element if trailing space on element line, bound on same line

        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a  '], 0, 3, 0, 1, 'all', False))
        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a \\'], 0, 3, 0, 1, 'all', False))
        self.assertEqual(((0, 3), None, True), trailing_trivia(['a #'], 0, 3, 0, 1, 'all', False))
        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a  '], 0, 3, 0, 1, 'block', False))
        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a \\'], 0, 3, 0, 1, 'block', False))
        self.assertEqual(((0, 3), None, True), trailing_trivia(['a #'], 0, 3, 0, 1, 'block', False))
        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a  '], 0, 3, 0, 1, 'line', False))
        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a \\'], 0, 3, 0, 1, 'line', False))
        self.assertEqual(((0, 3), None, True), trailing_trivia(['a #'], 0, 3, 0, 1, 'line', False))
        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a  '], 0, 3, 0, 1, 'none', False))
        self.assertEqual(((0, 1), (0, 3), True), trailing_trivia(['a \\'], 0, 3, 0, 1, 'none', False))
        self.assertEqual(((0, 1), (0, 2), False), trailing_trivia(['a #'], 0, 3, 0, 1, 'none', False))

        # returning end of element if trailing space on element line, bound not on same line

        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'all', False))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'all', False))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'all', False))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'block', False))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'block', False))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'block', False))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'line', False))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'line', False))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'line', False))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'none', False))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'none', False))
        self.assertEqual(((0, 1), (0, 2), False), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'none', False))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 0, False))
        self.assertEqual(((2, 0), None, True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 1, False))
        self.assertEqual(((2, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 2, False))

        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'all', 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'block', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'block', 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'block', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'line', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'line', 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'line', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'none', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'none', 0))
        self.assertEqual(((0, 1), (0, 2), False), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'none', 0))
        self.assertEqual(((0, 1), (1, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 0, 0))
        self.assertEqual(((2, 0), None, True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 1, 0))
        self.assertEqual(((2, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 2, 0))

        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'all', 1))
        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'all', 1))
        self.assertEqual(((1, 0), (2, 0), True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'all', 1))
        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'block', 1))
        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'block', 1))
        self.assertEqual(((1, 0), (2, 0), True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'block', 1))
        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'line', 1))
        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'line', 1))
        self.assertEqual(((1, 0), (2, 0), True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'line', 1))
        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 'none', 1))
        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 'none', 1))
        self.assertEqual(((0, 1), (0, 2), False), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 'none', 1))
        self.assertEqual(((0, 1), (2, 0), True), trailing_trivia(['a  ', ' ', ''], 2, 0, 0, 1, 0, 1))
        self.assertEqual(((2, 0), None, True), trailing_trivia(['a \\', ' ', ''], 2, 0, 0, 1, 1, 1))
        self.assertEqual(((2, 0), None, True), trailing_trivia(['a #', ' ', ''], 2, 0, 0, 1, 2, 1))

        # misc

        self.assertEqual(((2, 0), (2, 1), True), trailing_trivia(['a ', '# c', ' '], 2, 1, 0, 1, 1, 1))
        self.assertEqual(((2, 1), None, True), trailing_trivia(['a ', '   ', ' '], 2, 1, 0, 1, 2, 2))
        self.assertEqual(((2, 1), None, True), trailing_trivia(['a ', '   ', ' '], 2, 1, 0, 1, 2, 0))
        self.assertEqual(((0, 1), (2, 1), True), trailing_trivia(['a ', '   ', ' '], 2, 1, 0, 1, 'block', 2))

    def test_get_trivia_params(self):
        with FST.options(trivia=False):
            self.assertEqual(('none', False, False, 'line', False, False), get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), get_trivia_params(trivia=(True, True), neg=False))

        with FST.options(trivia=(False, False)):
            self.assertEqual(('none', False, False, 'none', False, False), get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'none', False, False), get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), get_trivia_params(trivia=(True, True), neg=False))

        with FST.options(trivia=(False, True)):
            self.assertEqual(('none', False, False, 'line', False, False), get_trivia_params(neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), get_trivia_params(trivia=True, neg=False))
            self.assertEqual(('block', False, False, 'line', False, False), get_trivia_params(trivia=(True, True), neg=False))
            self.assertEqual(('block', False, False, 'none', False, False), get_trivia_params(trivia=(True, False), neg=False))

        with FST.options(trivia='all+1'):
            self.assertEqual(('all', 1, False, 'line', False, False), get_trivia_params(neg=False))
            self.assertEqual(('all', 1, False, 'line', False, False), get_trivia_params(neg=True))

        with FST.options(trivia='all-1'):
            self.assertEqual(('all', False, True, 'line', False, False), get_trivia_params(neg=False))
            self.assertEqual(('all', 1, True, 'line', False, False), get_trivia_params(neg=True))

        with FST.options(trivia='all-1'):
            self.assertEqual(('block', 2, False, 'line', False, False), get_trivia_params(trivia='block+2', neg=False))
            self.assertEqual(('block', 2, False, 'line', False, False), get_trivia_params(trivia='block+2', neg=True))
            self.assertEqual(('block', 2, False, 'line', 3, False), get_trivia_params(trivia=('block+2', 'line+3'), neg=False))
            self.assertEqual(('block', 2, False, 'line', 3, False), get_trivia_params(trivia=('block+2', 'line+3'), neg=True))
            self.assertEqual(('block', 2, False, 'line', 3, True), get_trivia_params(trivia=('block+2', 'line-3'), neg=True))
            self.assertEqual(('block', 2, False, 'line', False, True), get_trivia_params(trivia=('block+2', 'line-3'), neg=False))
            self.assertEqual(('block', False, True, 'line', False, True), get_trivia_params(trivia=('block-2', 'line-3'), neg=False))

        with FST.options(trivia=1):
            self.assertEqual((1, False, False, 'line', False, False), get_trivia_params(neg=False))
            self.assertEqual((2, False, False, 'line', False, False), get_trivia_params(trivia=2, neg=False))
            self.assertEqual((2, False, False, 3, False, False), get_trivia_params(trivia=(2, 3), neg=False))

    def test__is_delimited_seq(self):
        self.assertFalse(FST('((pos < len(ranges))>>32),(r&((1<<32)-1))')._is_delimited_seq())
        self.assertFalse(FST('((1)+1),(1)')._is_delimited_seq())

        self.assertFalse(FST('(a,), (b)')._is_delimited_seq())
        self.assertFalse(FST('(a), (b,)')._is_delimited_seq())

    def test__is_expr_arglike(self):
        self.assertIsNone(FST('*a')._is_expr_arglike())
        self.assertTrue(FST('*a or b')._is_expr_arglike())
        self.assertFalse(FST('*(a or b)')._is_expr_arglike())
        self.assertIsNone(FST('*(a, b)')._is_expr_arglike())

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

    def test__maybe_del_separator(self):
        f = FST('[a, #c\n]')
        f._maybe_del_separator(0, 2, True, 0, 2)
        self.assertEqual('[a, #c\n]', f.src)

        f = FST('[a, #c\n]')
        f._maybe_del_separator(0, 2, True, 0, 3)
        self.assertEqual('[a #c\n]', f.src)

        f = FST('[a, #c\n]')
        f._maybe_del_separator(0, 2, False)
        self.assertEqual('[a, #c\n]', f.src)

        f = FST('[a, \\\n]')
        f._maybe_del_separator(0, 2, False)
        self.assertEqual('[a, \\\n]', f.src)

        f = FST('[a, #c\n]')
        f._maybe_del_separator(0, 2, True)
        self.assertEqual('[a #c\n]', f.src)

        f = FST('[a,\n]')
        f._maybe_del_separator(0, 2, False)
        self.assertEqual('[a\n]', f.src)

    def test__maybe_fix_tuple(self):
        # parenthesize naked tuple preserve comments if present

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=0), ['# comment', ''], None)
        f._maybe_fix_tuple()
        self.assertEqual('(# comment\n)', f.src)
        f.verify()

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=1), [' # comment', ' '], None)
        f._maybe_fix_tuple()
        self.assertEqual('(# comment\n)', f.src)
        f.verify()

        f = FST(Tuple(elts=[], ctx=Load(), lineno=1, col_offset=0, end_lineno=2, end_col_offset=0), ['         ', ''], None)
        f._maybe_fix_tuple()
        self.assertEqual('()', f.src)
        f.verify()

        # fix parent location after removing trailing whitespace

        f = FST('a = b, c')
        f.value.put_src(None, 0, 7, 0, 8, 'offset')
        del f.a.value.elts[-1]  # specifically just the AST
        self.assertEqual((0, 4, 0, 7), f.value.loc)
        f.value._maybe_fix_tuple()
        self.assertEqual('a = b,', f.src)
        f.verify()

        f = FST('(yield a, b)')
        f.value.put_src(None, 0, 10, 0, 11, 'offset')
        del f.a.value.elts[-1]  # specifically just the AST
        self.assertEqual((0, 7, 0, 10), f.value.loc)
        f.value._maybe_fix_tuple()
        self.assertEqual('(yield a,)', f.src)
        f.verify()

    def test__maybe_fix_copy(self):
        f = FST.fromsrc('if 1:\n a\nelif 2:\n b')
        fc = f.a.body[0].orelse[0].f.copy()
        self.assertEqual(fc.lines[0], 'if 2:')
        fc.verify(raise_=True)

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual(fc.src, '1 +\n2')
        fc._maybe_fix_copy(dict(pars=True))
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
        fc._maybe_fix_copy(dict(pars=True))
        self.assertEqual('i, j', f.src)  # because doesn't NEED them

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(pars=False)
        self.assertEqual('w := x,', f.src)
        f._maybe_fix_copy(dict(pars=True))
        self.assertEqual('(w := x,)', f.src)

        f = FST.fromsrc('yield a1, a2')
        fc = f.a.body[0].value.f.copy(pars=False)
        self.assertEqual('yield a1, a2', fc.src)
        fc._maybe_fix_copy(dict(pars=True))
        self.assertEqual('yield a1, a2', fc.src)

        f = FST.fromsrc('yield from a')
        fc = f.a.body[0].value.f.copy()
        self.assertEqual('yield from a', fc.src)
        fc._maybe_fix_copy(dict(pars=True))
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
        fc._maybe_fix_copy(dict(pars=True))
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
        fc._maybe_fix_copy(dict(pars=True))
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fc.src)

        if PYGE12:
            fc = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(pars=False)
            self.assertEqual('*tuple[int, ...]', fc.src)
            fc._maybe_fix_copy(dict(pars=True))
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
        self.assertEqual(f.root.src, '(# pre\ni\n# post\n)')

        f = FST('*\na\n# comment').par(whole=True)
        self.assertEqual(f.src, '*(\na\n# comment\n)')
        f.verify()

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
        self.assertEqual((0, 0, 3, 1), f.loc)
        self.assertEqual(f.src, '(# pre\ni,\n# post\n)')

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n(i,)\n# post')

        f = FST('a, # 0\nb, # 1', Tuple)
        f._delimit_node(whole=False)
        self.assertEqual('(a, # 0\nb,) # 1', f.src)

        f = FST('a, # 0\nb, # 1', Tuple)
        f._delimit_node()
        self.assertEqual('(a, # 0\nb, # 1\n)', f.src)

        f = FST('a, # 0\nb, # 1\n', Tuple)
        f._delimit_node()
        self.assertEqual('(a, # 0\nb, # 1\n)', f.src)

        f = FST('a, # 0\nb, # 1\n# 2', Tuple)
        f._delimit_node()
        self.assertEqual('(a, # 0\nb, # 1\n# 2\n)', f.src)

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
        self.assertEqual((0, 0, 3, 1), f.loc)
        self.assertEqual(f.src, '[# pre\ni,\n# post\n]')

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f._delimit_node(whole=False, delims='[]')
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n[i,]\n# post')

        f = FST('a, # 0\nb, # 1', pattern)
        f._delimit_node(whole=False, delims='[]')
        self.assertEqual('[a, # 0\nb,] # 1', f.src)

        f = FST('a, # 0\nb, # 1', pattern)
        f._delimit_node(delims='[]')
        self.assertEqual('[a, # 0\nb, # 1\n]', f.src)

        f = FST('a, # 0\nb, # 1\n', pattern)
        f._delimit_node(delims='[]')
        self.assertEqual('[a, # 0\nb, # 1\n]', f.src)

        f = FST('a, # 0\nb, # 1\n# 2', pattern)
        f._delimit_node(delims='[]')
        self.assertEqual('[a, # 0\nb, # 1\n# 2\n]', f.src)

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

    def test__loc_maybe_key(self):
        a = parse('''{
    a: """test
two  # fake comment start""", **b
            }''').body[0].value
        self.assertEqual((2, 30, 2, 32), a.f._loc_maybe_key(1))

        a = parse('''{
    a: """test""", **  # comment
    b
            }''').body[0].value
        self.assertEqual((1, 19, 1, 21), a.f._loc_maybe_key(1))

    def test__loc_match_case(self):
        # make sure it includes trailing semicolon

        self.assertEqual((0, 0, 0, 13), FST('case 1: pass;', match_case).loc)

    def test__loc_operator_no_parent(self):
        self.assertEqual((1, 0, 1, 1), FST(Invert(), ['# pre', '~ # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 3), FST(Not(), ['# pre', 'not # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(UAdd(), ['# pre', '+ # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(USub(), ['# pre', '- # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(Add(), ['# pre', '+ # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(Sub(), ['# pre', '- # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(Mult(), ['# pre', '* # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(MatMult(), ['# pre', '@ # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(Div(), ['# pre', '/ # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(Mod(), ['# pre', '% # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(LShift(), ['# pre', '<< # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(RShift(), ['# pre', '>> # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitOr(), ['# pre', '| # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitXor(), ['# pre', '^ # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(BitAnd(), ['# pre', '& # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(FloorDiv(), ['# pre', '// # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(Pow(), ['# pre', '** # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(Eq(), ['# pre', '== # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(NotEq(), ['# pre', '!= # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(Lt(), ['# pre', '< # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(LtE(), ['# pre', '<= # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 1), FST(Gt(), ['# pre', '> # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(GtE(), ['# pre', '>= # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(Is(), ['# pre', 'is # post', '# next'], None).loc)
        self.assertEqual((1, 0, 2, 3), FST(IsNot(), ['# pre', 'is # inner', 'not # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(In(), ['# pre', 'in # post', '# next'], None).loc)
        self.assertEqual((1, 0, 2, 2), FST(NotIn(), ['# pre', 'not # inner', 'in # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 3), FST(And(), ['# pre', 'and # post', '# next'], None).loc)
        self.assertEqual((1, 0, 1, 2), FST(Or(), ['# pre', 'or # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(Add(), ['# pre', '+= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(Sub(), ['# pre', '-= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(Mult(), ['# pre', '*= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(MatMult(), ['# pre', '@= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(Div(), ['# pre', '/= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(Mod(), ['# pre', '%= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 3), FST(LShift(), ['# pre', '<<= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 3), FST(RShift(), ['# pre', '>>= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(BitOr(), ['# pre', '|= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(BitXor(), ['# pre', '^= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 2), FST(BitAnd(), ['# pre', '&= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 3), FST(FloorDiv(), ['# pre', '//= # post', '# next'], None).loc)
        # self.assertEqual((1, 0, 1, 3), FST(Pow(), ['# pre', '**= # post', '# next'], None).loc)

    def test__loc_block_header_end(self):
        from fst.fst_locs import _loc_block_header_end

        self.assertEqual((0, 15, 0, 16), _loc_block_header_end(parse('def f(a) -> int: pass').body[0].f))
        self.assertEqual((0, 7, 0, 9),  _loc_block_header_end(parse('def f(a): pass').body[0].f))
        self.assertEqual((0, 0, 0, 8),  _loc_block_header_end(parse('def f(): pass').body[0].f))
        self.assertEqual((0, 21, 0, 22), _loc_block_header_end(parse('async def f(a) -> int: pass').body[0].f))
        self.assertEqual((0, 13, 0, 15), _loc_block_header_end(parse('async def f(a): pass').body[0].f))
        self.assertEqual((0, 0, 0, 14), _loc_block_header_end(parse('async def f(): pass').body[0].f))
        self.assertEqual((0, 25, 0, 27), _loc_block_header_end(parse('class cls(base, keyword=1): pass').body[0].f))
        self.assertEqual((0, 14, 0, 16), _loc_block_header_end(parse('class cls(base): pass').body[0].f))
        self.assertEqual((0, 10, 0, 11), _loc_block_header_end(parse('for a in b: pass\nelse: pass').body[0].f))
        self.assertEqual((0, 16, 0, 17), _loc_block_header_end(parse('async for a in b: pass\nelse: pass').body[0].f))
        self.assertEqual((0, 7, 0, 8),  _loc_block_header_end(parse('while a: pass\nelse: pass').body[0].f))
        self.assertEqual((0, 4, 0, 5),  _loc_block_header_end(parse('if a: pass\nelse: pass').body[0].f))
        self.assertEqual((0, 8, 0, 9),  _loc_block_header_end(parse('with f(): pass').body[0].f))
        self.assertEqual((0, 13, 0, 14), _loc_block_header_end(parse('with f() as v: pass').body[0].f))
        self.assertEqual((0, 14, 0, 15), _loc_block_header_end(parse('async with f(): pass').body[0].f))
        self.assertEqual((0, 19, 0, 20), _loc_block_header_end(parse('async with f() as v: pass').body[0].f))
        self.assertEqual((0, 7, 0, 8),  _loc_block_header_end(parse('match a:\n case 2: pass').body[0].f))
        self.assertEqual((1, 7, 1, 8),  _loc_block_header_end(parse('match a:\n case 2: pass').body[0].cases[0].f))
        self.assertEqual((1, 15, 1, 16), _loc_block_header_end(parse('match a:\n case 2 if True: pass').body[0].cases[0].f))
        self.assertEqual((0, 0, 0, 4),  _loc_block_header_end(parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].f))
        self.assertEqual((1, 0, 1, 7),  _loc_block_header_end(parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
        self.assertEqual((1, 16, 1, 17), _loc_block_header_end(parse('try: pass\nexcept Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
        self.assertEqual((1, 33, 1, 34), _loc_block_header_end(parse('try: pass\nexcept (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
        self.assertEqual((1, 33, 1, 39), _loc_block_header_end(parse('try: pass\nexcept (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))

        if PYGE12:
            self.assertEqual((0, 0, 0, 4),  _loc_block_header_end(parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].f))
            self.assertEqual((1, 17, 1, 18), _loc_block_header_end(parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
            self.assertEqual((1, 34, 1, 35), _loc_block_header_end(parse('try: pass\nexcept* (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
            self.assertEqual((1, 34, 1, 40), _loc_block_header_end(parse('try: pass\nexcept* (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f))
            self.assertEqual((0, 11, 0, 13), _loc_block_header_end(parse('class cls[T]: pass').body[0].f))

        self.assertEqual((0, 16, 0, 18), _loc_block_header_end(parse('def f(a) -> (int): pass').body[0].f))
        self.assertEqual((0, 27, 0, 29), _loc_block_header_end(parse('class cls(base, keyword=(1)): pass').body[0].f))
        self.assertEqual((0, 15, 0, 18), _loc_block_header_end(parse('class cls((base)): pass').body[0].f))
        self.assertEqual((0, 11, 0, 13), _loc_block_header_end(parse('for a in (b): pass\nelse: pass').body[0].f))

        # else and finally

        f = FST('''
try: pass  # :
    # :
except: pass  # :
    # :
else:  # :
    pass  # :
finally:  # :
    pass  # :
            '''[1:-1])
        self.assertEqual((4, 0, 4, 5), f._loc_block_header_end('orelse'))
        self.assertEqual((6, 0, 6, 8), f._loc_block_header_end('finalbody'))
        del f.body[0]
        self.assertEqual((3, 0, 3, 5), f._loc_block_header_end('orelse'))
        self.assertEqual((5, 0, 5, 8), f._loc_block_header_end('finalbody'))
        del f.handlers[0]
        self.assertEqual((2, 0, 2, 5), f._loc_block_header_end('orelse'))
        self.assertEqual((4, 0, 4, 8), f._loc_block_header_end('finalbody'))
        del f.orelse[0]
        self.assertIsNone(f._loc_block_header_end('orelse'))
        self.assertEqual((1, 0, 1, 8), f._loc_block_header_end('finalbody'))
        del f.finalbody[0]
        self.assertIsNone(f._loc_block_header_end('orelse'))
        self.assertIsNone(f._loc_block_header_end('finalbody'))

        f = FST('''
if 1:
    try: pass  # :
        # :
    except: pass  # :
        # :
    else:  # :
        pass  # :
    finally:  # :
        pass  # :
            '''[1:-1])
        self.assertEqual((5, 4, 5, 9), f.body[0]._loc_block_header_end('orelse'))
        self.assertEqual((7, 4, 7, 12), f.body[0]._loc_block_header_end('finalbody'))
        del f.body[0].body[0]
        self.assertEqual((5, 4, 5, 9), f.body[0]._loc_block_header_end('orelse'))
        self.assertEqual((7, 4, 7, 12), f.body[0]._loc_block_header_end('finalbody'))
        del f.body[0].handlers[0]
        self.assertEqual((3, 4, 3, 9), f.body[0]._loc_block_header_end('orelse'))
        self.assertEqual((5, 4, 5, 12), f.body[0]._loc_block_header_end('finalbody'))
        del f.body[0].orelse[0]
        self.assertIsNone(f.body[0]._loc_block_header_end('orelse'))
        self.assertEqual((2, 4, 2, 12), f.body[0]._loc_block_header_end('finalbody'))
        del f.body[0].finalbody[0]
        self.assertIsNone(f.body[0]._loc_block_header_end('orelse'))
        self.assertIsNone(f.body[0]._loc_block_header_end('finalbody'))

    def test__loc_arguments_empty(self):
        self.assertEqual((0, 0, 0, 6), FST('# test', 'arguments')._loc_arguments_empty())
        self.assertEqual((0, 6, 0, 6), FST('lambda: None').args._loc_arguments_empty())
        self.assertEqual((0, 6, 0, 8), FST('lambda  : None').args._loc_arguments_empty())
        self.assertEqual((0, 6, 0, 6), FST('def f(): pass').args._loc_arguments_empty())
        self.assertEqual((0, 6, 0, 8), FST('def f(  ): pass').args._loc_arguments_empty())

        if PYGE12:
            self.assertEqual((0, 14, 0, 14), FST('def f[T: int](): pass').args._loc_arguments_empty())
            self.assertEqual((0, 14, 0, 16), FST('def f[T: int](  ): pass').args._loc_arguments_empty())

        if PYGE13:
            self.assertEqual((0, 21, 0, 21), FST('def f[T: int = bool](): pass').args._loc_arguments_empty())
            self.assertEqual((0, 21, 0, 23), FST('def f[T: int = bool](  ): pass').args._loc_arguments_empty())

    def test__loc_decorator(self):
        self.assertEqual((1, 2, 1, 10), FST('if 1:\n  @ ( deco )\n  class cls: pass').body[0]._loc_decorator(0, pars=False))
        self.assertEqual((1, 2, 1, 12), FST('if 1:\n  @ ( deco )\n  class cls: pass').body[0]._loc_decorator(0, pars=True))

        self.assertEqual((3, 2, 4, 6), FST(r'''
if 1:
    @deco1
    \
  @ \
 deco2
    class cls: pass
'''.strip()).body[0]._loc_decorator(1))

    def test__loc_ClassDef_bases_pars(self):
        from fst.fst_locs import _loc_ClassDef_bases_pars

        self.assertEqual('fstlocn(0, 9, 0, 9, n=0)', str(_loc_ClassDef_bases_pars(FST('class cls: pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 10, n=0)', str(_loc_ClassDef_bases_pars(FST('class cls : pass'))))
        self.assertEqual('fstlocn(1, 3, 1, 4, n=0)', str(_loc_ClassDef_bases_pars(FST('class \\\ncls : pass'))))
        self.assertEqual('fstlocn(0, 9, 1, 0, n=0)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n: pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 11, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(): pass'))))
        self.assertEqual('fstlocn(1, 0, 1, 2, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls\\\n(): pass'))))
        self.assertEqual('fstlocn(0, 9, 1, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(\n): pass'))))
        self.assertEqual('fstlocn(1, 0, 2, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n(\n): pass'))))

        self.assertEqual('fstlocn(0, 9, 0, 12, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(b): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 14, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(k=v): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 14, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(**v): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 17, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(b, k=v): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 17, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(b, **v): pass'))))
        self.assertEqual('fstlocn(0, 9, 2, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(\nb\n): pass'))))
        self.assertEqual('fstlocn(1, 1, 3, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n (\nb\n) \\\n: pass'))))

        self.assertEqual('fstlocn(0, 9, 0, 13, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(b,): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 15, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(k=v,): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 15, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(**v,): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 18, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(b, k=v,): pass'))))
        self.assertEqual('fstlocn(0, 9, 0, 18, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(b, **v,): pass'))))
        self.assertEqual('fstlocn(0, 9, 3, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls(\nb\n,\n): pass'))))
        self.assertEqual('fstlocn(1, 1, 4, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n (\nb\n,\n) \\\n: pass'))))

        if PYGE12:
            self.assertEqual('fstlocn(0, 12, 0, 12, n=0)', str(_loc_ClassDef_bases_pars(FST('class cls[T]: pass'))))
            self.assertEqual('fstlocn(0, 12, 0, 13, n=0)', str(_loc_ClassDef_bases_pars(FST('class cls[T] : pass'))))
            self.assertEqual('fstlocn(0, 13, 0, 13, n=0)', str(_loc_ClassDef_bases_pars(FST('class cls[T,]: pass'))))
            self.assertEqual('fstlocn(0, 12, 0, 14, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls[T](): pass'))))
            self.assertEqual('fstlocn(0, 13, 0, 15, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls[T,](): pass'))))
            self.assertEqual('fstlocn(0, 15, 0, 17, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls[T, U](): pass'))))
            self.assertEqual('fstlocn(1, 3, 1, 5, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n[T](): pass'))))
            self.assertEqual('fstlocn(2, 1, 2, 3, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls[\nT\n](): pass'))))
            self.assertEqual('fstlocn(3, 1, 3, 3, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n](): pass'))))
            self.assertEqual('fstlocn(4, 0, 5, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n]\\\n(\n): pass'))))
            self.assertEqual('fstlocn(6, 0, 7, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n,\nU\n]\\\n( \\\n): pass'))))

            self.assertEqual('fstlocn(0, 12, 0, 15, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls[T](b): pass'))))
            self.assertEqual('fstlocn(0, 18, 0, 25, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls[T, **U,]( b , ): pass'))))
            self.assertEqual('fstlocn(1, 3, 1, 6, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n[T](b): pass'))))
            self.assertEqual('fstlocn(2, 1, 2, 4, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls[\nT\n](b): pass'))))
            self.assertEqual('fstlocn(3, 1, 3, 4, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n](b): pass'))))

            self.assertEqual('fstlocn(4, 0, 7, 1, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n]\\\n(\nb\n,\n): pass'))))
            self.assertEqual('fstlocn(6, 0, 7, 3, n=1)', str(_loc_ClassDef_bases_pars(FST('class cls \\\n[\nT\n,\nU\n]\\\n( \\\nb,): pass'))))

    def test__loc_ImportFrom_names_pars(self):
        from fst.fst_locs import _loc_ImportFrom_names_pars

        self.assertEqual('fstlocn(0, 14, 0, 15, n=0)', str(_loc_ImportFrom_names_pars(FST('from . import a'))))
        self.assertEqual('fstlocn(0, 14, 0, 17, n=1)', str(_loc_ImportFrom_names_pars(FST('from . import (a)'))))
        self.assertEqual('fstlocn(0, 14, 2, 1, n=1)', str(_loc_ImportFrom_names_pars(FST('from . import (\na\n)'))))
        self.assertEqual('fstlocn(1, 0, 3, 1, n=1)', str(_loc_ImportFrom_names_pars(FST('from . import \\\n(\na\n)'))))
        self.assertEqual('fstlocn(0, 14, 1, 1, n=0)', str(_loc_ImportFrom_names_pars(FST('from . import \\\na'))))
        self.assertEqual('fstlocn(0, 13, 1, 1, n=0)', str(_loc_ImportFrom_names_pars(FST('from . import\\\na'))))

        self.assertEqual('fstlocn(0, 22, 0, 23, n=0)', str(_loc_ImportFrom_names_pars(FST('from importlib import b'))))
        self.assertEqual('fstlocn(0, 22, 1, 1, n=0)', str(_loc_ImportFrom_names_pars(FST('from importlib import \\\nb'))))
        self.assertEqual('fstlocn(0, 22, 0, 25, n=1)', str(_loc_ImportFrom_names_pars(FST('from importlib import (b)'))))
        self.assertEqual('fstlocn(0, 22, 2, 1, n=1)', str(_loc_ImportFrom_names_pars(FST('from importlib import (\nb\n)'))))

        f = FST('from . import a')
        f._put_src(None, 0, 14, 0, 15, True)
        del f.a.names[:]
        self.assertEqual('fstlocn(0, 14, 0, 14, n=0)', str(_loc_ImportFrom_names_pars(f)))
        f._put_src(None, 0, 13, 0, 14, True)
        self.assertEqual('fstlocn(0, 13, 0, 13, n=0)', str(_loc_ImportFrom_names_pars(f)))
        f._put_src('\n', 0, 13, 0, 13, True)
        self.assertEqual('fstlocn(0, 13, 1, 0, n=0)', str(_loc_ImportFrom_names_pars(f)))

    def test__loc_With_items_pars(self):
        from fst.fst_locs import _loc_With_items_pars

        def str_(loc_ret):
            del loc_ret.bound

            return str(loc_ret)

        self.assertEqual('fstlocn(0, 5, 0, 6, n=0)', str_(_loc_With_items_pars(FST('with a: pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 8, n=0)', str_(_loc_With_items_pars(FST('with (a): pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 13, n=1)', str_(_loc_With_items_pars(FST('with (a as b): pass'))))
        self.assertEqual('fstlocn(0, 5, 2, 1, n=1)', str_(_loc_With_items_pars(FST('with (\na as b\n): pass'))))
        self.assertEqual('fstlocn(1, 0, 3, 1, n=1)', str_(_loc_With_items_pars(FST('with \\\n(\na as b\n): pass'))))
        self.assertEqual('fstlocn(0, 5, 1, 1, n=0)', str_(_loc_With_items_pars(FST('with \\\na: pass'))))
        self.assertEqual('fstlocn(0, 4, 1, 1, n=0)', str_(_loc_With_items_pars(FST('with\\\na: pass'))))
        self.assertEqual('fstlocn(0, 4, 3, 0, n=0)', str_(_loc_With_items_pars(FST('with\\\n\\\na\\\n: pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 8, n=0)', str_(_loc_With_items_pars(FST('with  a : pass'))))
        self.assertEqual('fstlocn(0, 6, 0, 14, n=1)', str_(_loc_With_items_pars(FST('with  (a as b)  : pass'))))

        self.assertEqual('fstlocn(0, 11, 0, 12, n=0)', str_(_loc_With_items_pars(FST('async with a: pass'))))
        self.assertEqual('fstlocn(0, 11, 0, 14, n=0)', str_(_loc_With_items_pars(FST('async with (a): pass'))))
        self.assertEqual('fstlocn(0, 11, 0, 19, n=1)', str_(_loc_With_items_pars(FST('async with (a as b): pass'))))
        self.assertEqual('fstlocn(0, 11, 2, 1, n=1)', str_(_loc_With_items_pars(FST('async with (\na as b\n): pass'))))
        self.assertEqual('fstlocn(1, 0, 3, 1, n=1)', str_(_loc_With_items_pars(FST('async with \\\n(\na as b\n): pass'))))
        self.assertEqual('fstlocn(0, 11, 1, 1, n=0)', str_(_loc_With_items_pars(FST('async with \\\na: pass'))))
        self.assertEqual('fstlocn(0, 10, 1, 1, n=0)', str_(_loc_With_items_pars(FST('async with\\\na: pass'))))
        self.assertEqual('fstlocn(0, 10, 3, 0, n=0)', str_(_loc_With_items_pars(FST('async with\\\n\\\na\\\n: pass'))))
        self.assertEqual('fstlocn(0, 11, 0, 14, n=0)', str_(_loc_With_items_pars(FST('async with  a : pass'))))
        self.assertEqual('fstlocn(0, 12, 0, 20, n=1)', str_(_loc_With_items_pars(FST('async with  (a as b)  : pass'))))

        self.assertEqual('fstlocn(1, 6, 1, 7, n=0)', str_(_loc_With_items_pars(FST('async \\\n with a: pass'))))
        self.assertEqual('fstlocn(1, 6, 1, 9, n=0)', str_(_loc_With_items_pars(FST('async \\\n with (a): pass'))))
        self.assertEqual('fstlocn(1, 6, 1, 14, n=1)', str_(_loc_With_items_pars(FST('async \\\n with (a as b): pass'))))
        self.assertEqual('fstlocn(1, 6, 3, 1, n=1)', str_(_loc_With_items_pars(FST('async \\\n with (\na as b\n): pass'))))
        self.assertEqual('fstlocn(2, 0, 4, 1, n=1)', str_(_loc_With_items_pars(FST('async \\\n with \\\n(\na as b\n): pass'))))
        self.assertEqual('fstlocn(1, 6, 2, 1, n=0)', str_(_loc_With_items_pars(FST('async \\\n with \\\na: pass'))))
        self.assertEqual('fstlocn(1, 5, 2, 1, n=0)', str_(_loc_With_items_pars(FST('async \\\n with\\\na: pass'))))
        self.assertEqual('fstlocn(1, 5, 4, 0, n=0)', str_(_loc_With_items_pars(FST('async \\\n with\\\n\\\na\\\n: pass'))))
        self.assertEqual('fstlocn(1, 6, 1, 9, n=0)', str_(_loc_With_items_pars(FST('async \\\n with  a : pass'))))
        self.assertEqual('fstlocn(1, 7, 1, 15, n=1)', str_(_loc_With_items_pars(FST('async \\\n with  (a as b)  : pass'))))

        f = FST('with a: pass')
        f._put_src(None, 0, 5, 0, 6, True)
        del f.a.items[:]
        self.assertEqual('fstlocn(0, 5, 0, 5, n=0)', str_(_loc_With_items_pars(f)))
        f._put_src(None, 0, 4, 0, 5, True)
        self.assertEqual('fstlocn(0, 4, 0, 4, n=0)', str_(_loc_With_items_pars(f)))
        f._put_src('\n', 0, 4, 0, 4, True)
        self.assertEqual('fstlocn(0, 4, 1, 0, n=0)', str_(_loc_With_items_pars(f)))

        self.assertEqual('fstlocn(0, 5, 0, 8, n=0)', str_(_loc_With_items_pars(FST('with (a): pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 13, n=0)', str_(_loc_With_items_pars(FST('with (a) as b: pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 15, n=1)', str_(_loc_With_items_pars(FST('with ((a) as b): pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 15, n=0)', str_(_loc_With_items_pars(FST('with (a) as (b): pass'))))
        self.assertEqual('fstlocn(0, 5, 0, 17, n=1)', str_(_loc_With_items_pars(FST('with ((a) as (b)): pass'))))

        f = FST(r'''
with (
    a as b
    ): pass
'''.strip())
        f.items[0].remove()
        self.assertEqual('fstlocn(0, 5, 1, 5, n=1)', str_(_loc_With_items_pars(f)))

    def test__loc_Call_pars(self):
        from fst.fst_locs import _loc_Call_pars

        self.assertEqual((0, 4, 0, 6), _loc_Call_pars(FST('call()', 'exec').body[0].value))
        self.assertEqual((0, 4, 0, 7), _loc_Call_pars(FST('call(a)', 'exec').body[0].value))
        self.assertEqual((0, 4, 2, 1), _loc_Call_pars(FST('call(\na\n)', 'exec').body[0].value))
        self.assertEqual((0, 4, 2, 1), _loc_Call_pars(FST('call(\na, b=2\n)', 'exec').body[0].value))
        self.assertEqual((0, 4, 0, 12), _loc_Call_pars(FST('call(c="()")', 'exec').body[0].value))
        self.assertEqual((1, 0, 8, 1), _loc_Call_pars(FST('call\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n)', 'exec').body[0].value))
        self.assertEqual((1, 0, 8, 1), _loc_Call_pars(FST('"()("\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n)', 'exec').body[0].value))

    def test__loc_Subscript_brackets(self):
        from fst.fst_locs import _loc_Subscript_brackets

        self.assertEqual((0, 1, 0, 4), _loc_Subscript_brackets(FST('a[b]', 'exec').body[0].value))
        self.assertEqual((0, 1, 0, 8), _loc_Subscript_brackets(FST('a[b:c:d]', 'exec').body[0].value))
        self.assertEqual((0, 1, 0, 7), _loc_Subscript_brackets(FST('a["[]"]', 'exec').body[0].value))
        self.assertEqual((1, 0, 7, 1), _loc_Subscript_brackets(FST('a\\\n[\nb\n:\nc\n:\nd\n]', 'exec').body[0].value))
        self.assertEqual((1, 0, 7, 1), _loc_Subscript_brackets(FST('"[]["\\\n[\nb\n:\nc\n:\nd\n]', 'exec').body[0].value))

    def test__loc_MatchMapping_rest(self):
        self.assertIsNone(FST('{1: a, 2: b}', 'MatchMapping')._loc_MatchMapping_rest())
        self.assertEqual((0, 15, 0, 19), FST('{1: a, 2: b, **rest}', 'MatchMapping')._loc_MatchMapping_rest())
        self.assertEqual((0, 3, 0, 7), FST('{**rest}', 'MatchMapping')._loc_MatchMapping_rest())

    def test__loc_MatchClass_pars(self):
        from fst.fst_locs import _loc_MatchClass_pars

        self.assertEqual((1, 9, 1, 11), _loc_MatchClass_pars(FST('match a:\n case cls(): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((1, 9, 1, 12), _loc_MatchClass_pars(FST('match a:\n case cls(a): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((1, 9, 3, 1), _loc_MatchClass_pars(FST('match a:\n case cls(\na\n): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((1, 9, 3, 1), _loc_MatchClass_pars(FST('match a:\n case cls(\na, b=2\n): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((1, 9, 1, 17), _loc_MatchClass_pars(FST('match a:\n case cls(c="()"): pass', 'exec').body[0].cases[0].pattern))
        self.assertEqual((2, 0, 9, 1), _loc_MatchClass_pars(FST('match a:\n case cls\\\n(\nc\n=\n"\\\n(\\\n)\\\n"\n): pass', 'exec').body[0].cases[0].pattern))

    def test__loc_FunctionDef_type_params_brackets(self):
        f = FST('def f(): pass')
        self.assertEqual((None, (0, 5)), f._loc_FunctionDef_type_params_brackets())
        del f.body
        self.assertEqual((None, (0, 5)), f._loc_FunctionDef_type_params_brackets())

        f = FST(r'''
def f():
    @deco(["\\"])
    def gen(): pass
                '''.strip())
        self.assertEqual((None, (0, 5)), f._loc_FunctionDef_type_params_brackets())
        del f.body
        self.assertEqual((None, (0, 5)), f._loc_FunctionDef_type_params_brackets())

        if PYGE12:
            f = FST('def f [T] (): pass')
            self.assertEqual(((0, 6, 0, 9), (0, 5)), f._loc_FunctionDef_type_params_brackets())
            del f.body
            self.assertEqual(((0, 6, 0, 9), (0, 5)), f._loc_FunctionDef_type_params_brackets())

    def test__loc_ClassDef_type_params_brackets(self):
        f = FST('class cls: pass')
        self.assertEqual((None, (0, 9)), f._loc_ClassDef_type_params_brackets())
        del f.body
        self.assertEqual((None, (0, 9)), f._loc_ClassDef_type_params_brackets())

        f = FST(r'''
class cls:
    @deco(["\\"])
    def gen(): pass
                '''.strip())
        self.assertEqual((None, (0, 9)), f._loc_ClassDef_type_params_brackets())
        del f.body
        self.assertEqual((None, (0, 9)), f._loc_ClassDef_type_params_brackets())

        if PYGE12:
            f = FST('class cls [T] (): pass')
            self.assertEqual(((0, 10, 0, 13), (0, 9)), f._loc_ClassDef_type_params_brackets())
            del f.body
            self.assertEqual(((0, 10, 0, 13), (0, 9)), f._loc_ClassDef_type_params_brackets())


if __name__ == '__main__':
    unittest.main()
