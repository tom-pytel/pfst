#!/usr/bin/env python

import re
import unittest

from fst.common import PYGE12, PYGE14


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
        from fst.common import leading_trivia

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
        from fst.common import trailing_trivia

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

        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, -1, 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 0, 0))
        self.assertEqual(((2, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 1, 0))
        self.assertEqual(((3, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 2, 0))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 3, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 4, 0))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 5, 0))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 6, 0))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 7, 0))

        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, -1, 1))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 0, 1))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 1, 1))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 2, 1))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 3, 1))
        self.assertEqual(((5, 0), (6, 0), True), trailing_trivia(ls, 6, 2, 0, 3, 4, 1))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 5, 1))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 6, 1))
        self.assertEqual(((6, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, 7, 1))

        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 6, 2, 0, 3, -1, 2))
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

        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, -1, 0))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 0, 0))
        self.assertEqual(((2, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 1, 0))
        self.assertEqual(((3, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 2, 0))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 3, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 4, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 5, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 6, 0))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 7, 0))

        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, -1, 1))
        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 0, 1))
        self.assertEqual(((2, 0), (3, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 1, 1))
        self.assertEqual(((3, 0), (4, 0), True), trailing_trivia(ls, 5, 0, 0, 3, 2, 1))
        self.assertEqual(((4, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 3, 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 4, 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 5, 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 6, 1))
        self.assertEqual(((5, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, 7, 1))

        self.assertEqual(((1, 0), None, True), trailing_trivia(ls, 5, 0, 0, 3, -1, 2))
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

    def test__multiline_str_continuation_lns(self):
        from fst.fst_core import _multiline_str_continuation_lns as mscl

        self.assertEqual([], mscl(ls := r'''
'a'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
"a"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"""a
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"""a

b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
"a"
"b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "z" "c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "z" "c\
b" """y"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" "z" "c\
b" """y
"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" "z" "c\
b" "x" """y
"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" """c
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" """c
b""" "d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3], mscl(ls := r'''
"a" """c
b"""
"d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3, 4], mscl(ls := r'''
"a" """c
b"""
"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
"a" """c
b"""

"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
b"a" b"""c
b"""

b"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
u"a" u"""c
b"""

u"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
r"a" r"""c
b"""

r"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([2], mscl(ls := r'''
'a' \
'b\
c' \
'd'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := [
            "r'<[a-zA-Z][-_.:a-zA-Z0-9]*\\s*('",
            "        r'\\s*([a-zA-Z_][-:.a-zA-Z_0-9]*)(\\s*=\\s*'",
            '        r\'(\\\'[^\\\']*\\\'|"[^"]*"|[-a-zA-Z0-9./,:;+*%?!&$\\(\\)_#=~@]\'',
            '        r\'[][\\-a-zA-Z0-9./,:;+*%?!&$\\(\\)_#=~\\\'"@]*(?=[\\s>/<])))?\'',
            "    r')*\\s*/?\\s*(?=[<>])'"], 0, 0, len(ls) - 1, len(ls[-1])))

    def test__multiline_ftstr_continuation_lns(self):
        from fst.fst_core import _multiline_ftstr_continuation_lns as mscl

        self.assertEqual([], mscl(ls := r'''
f'a'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
f"a"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"""a
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"""a

b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
f"a"
"b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a" f"c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a" f"""c
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"a" f"""c
b""" "d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3], mscl(ls := r'''
f"a" f"""c
b"""
f"d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3, 4], mscl(ls := r'''
f"a" f"""c
b"""
f"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
f"a" f"""c
b"""

f"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([2], mscl(ls := r'''
f'a' \
f'b\
c' \
f'd'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        # with values

        self.assertEqual([], mscl(ls := r'''
f"a{1}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
f"a{(1,)}"\
f"{(2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a{(1,)}\
{(2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"a{(1,)}\
{(2)}b""" f"c\
d"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3], mscl(ls := r'''
f"a{(1,)}\
{(2)}b" f"""{3}
{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,)}\
\
{(2)}b" f"""{3}

{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,)}\
\
{(2)}b" f"""{3}

{4}
{5}""" f"x"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5, 6], mscl(ls := r'''
f"a{(1,)}\
\
{(2)}b" f"""{3}

{4}
{5}""" f"x\
y"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

    @unittest.skipUnless(PYGE12, 'only valid for py >= 3.12')
    def test__multiline_ftstr_continuation_lns_pyge12(self):
        from fst.fst_core import _multiline_ftstr_continuation_lns as mscl

        self.assertEqual([1], mscl(ls := r'''
f"a{(1,
2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a{(1,\
2)}b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"a{(1,\
2)}b""" f"c\
d"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3], mscl(ls := r'''
f"a{(1,
2)}b" f"""{3}
{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5, 6], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x\
y"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

    @unittest.skipUnless(PYGE14, 'only valid for py >= 3.14')
    def test__multiline_tstr_continuation_lns(self):
        from fst.fst_core import _multiline_ftstr_continuation_lns as mscl

        self.assertEqual([], mscl(ls := r'''
t'a'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
t"a"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"""a
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
t"""a

b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
t"a"
"b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a" t"c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a" t"""c
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
t"a" t"""c
b""" "d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3], mscl(ls := r'''
t"a" t"""c
b"""
t"d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3, 4], mscl(ls := r'''
t"a" t"""c
b"""
t"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
t"a" t"""c
b"""

t"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([2], mscl(ls := r'''
t'a' \
t'b\
c' \
t'd'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        # with values

        self.assertEqual([], mscl(ls := r'''
t"a{1}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a{(1,
2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a{(1,\
2)}b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
t"a{(1,\
2)}b""" t"c\
d"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3], mscl(ls := r'''
t"a{(1,
2)}b" t"""{3}
{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5, 6], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x\
y"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))


if __name__ == '__main__':
    unittest.main()
