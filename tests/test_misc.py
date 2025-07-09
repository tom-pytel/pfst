#!/usr/bin/env python

import re
import unittest

from fst.misc import PYGE14


class TestMisc(unittest.TestCase):
    def test__next_prev_src(self):
        from fst.misc import _next_src, _prev_src

        lines = '''
  # pre
i \\
here \\
j \\
  # post
k \\
            '''.split('\n')

        self.assertEqual((4, 0, 'j'), _next_src(lines, 3, 4, 7, 0, False, False))
        self.assertEqual((4, 0, 'j'), _next_src(lines, 3, 4, 7, 0, True, False))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 4, 1, 7, 0, False, False))
        self.assertEqual((5, 2, '# post'), _next_src(lines, 4, 1, 7, 0, True, False))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 5, 8, 7, 0, False, False))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 5, 8, 7, 0, True, False))

        self.assertEqual((3, 5, '\\'), _next_src(lines, 3, 4, 7, 0, False, True))
        self.assertEqual((3, 5, '\\'), _next_src(lines, 3, 4, 7, 0, True, True))
        self.assertEqual((4, 2, '\\'), _next_src(lines, 4, 1, 7, 0, False, True))
        self.assertEqual((4, 2, '\\'), _next_src(lines, 4, 1, 7, 0, True, True))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 5, 8, 7, 0, False, True))
        self.assertEqual((6, 0, 'k'), _next_src(lines, 5, 8, 7, 0, True, True))

        self.assertEqual((4, 0, 'j'), _next_src(lines, 3, 4, 7, 0, False, None))
        self.assertEqual((4, 0, 'j'), _next_src(lines, 3, 4, 7, 0, True, None))
        self.assertEqual(None, _next_src(lines, 4, 1, 7, 0, False, None))
        self.assertEqual((5, 2, '# post'), _next_src(lines, 4, 1, 7, 0, True, None))
        self.assertEqual(None, _next_src(lines, 5, 8, 7, 0, False, None))
        self.assertEqual(None, _next_src(lines, 5, 8, 7, 0, True, None))

        self.assertEqual(None, _prev_src(lines, 0, 0, 2, 0, False, False))
        self.assertEqual((1, 2, '# pre'), _prev_src(lines, 0, 0, 2, 0, True, False))
        self.assertEqual((2, 0, 'i'), _prev_src(lines, 0, 0, 3, 0, False, False))
        self.assertEqual((2, 0, 'i'), _prev_src(lines, 0, 0, 3, 0, True, False))
        self.assertEqual((4, 0, 'j'), _prev_src(lines, 0, 0, 6, 0, False, False))
        self.assertEqual((5, 2, '# post'), _prev_src(lines, 0, 0, 6, 0, True, False))

        self.assertEqual(None, _prev_src(lines, 0, 0, 2, 0, False, True))
        self.assertEqual((1, 2, '# pre'), _prev_src(lines, 0, 0, 2, 0, True, True))
        self.assertEqual((2, 2, '\\'), _prev_src(lines, 0, 0, 3, 0, False, True))
        self.assertEqual((2, 2, '\\'), _prev_src(lines, 0, 0, 3, 0, True, True))
        self.assertEqual((4, 2, '\\'), _prev_src(lines, 0, 0, 6, 0, False, True))
        self.assertEqual((5, 2, '# post'), _prev_src(lines, 0, 0, 6, 0, True, True))

        self.assertEqual(None, _prev_src(lines, 0, 0, 1, 7, False, None))
        self.assertEqual((1, 2, '# pre'), _prev_src(lines, 0, 0, 1, 7, True, None))
        self.assertEqual((2, 0, 'i'), _prev_src(lines, 0, 0, 3, 0, False, None))
        self.assertEqual((2, 0, 'i'), _prev_src(lines, 0, 0, 3, 0, True, None))
        self.assertEqual((4, 0, 'j'), _prev_src(lines, 0, 0, 5, 3, False, None))
        self.assertEqual((5, 2, '#'), _prev_src(lines, 0, 0, 5, 3, True, None))

        self.assertEqual((1, 1, 'a'), _next_src(['\\', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual((2, 1, 'a'), _next_src(['\\', '\\', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual(None, _next_src(['\\', '', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual((1, 1, '# c'), _next_src(['\\', ' # c'], 0, 0, 100, 0, True, None))
        self.assertEqual(None, _next_src(['\\', ' # c', 'a'], 0, 0, 100, 0, False, None))

        self.assertEqual((0, 0, 'a'), _prev_src(['a \\', ''], 0, 0, 1, 0, True, None))
        self.assertEqual((0, 0, 'a'), _prev_src(['a \\', '\\', ''], 0, 0, 2, 0, True, None))
        self.assertEqual((0, 0, 'a'), _prev_src(['a \\', '\\', '\\', ''], 0, 0, 3, 0, True, None))
        self.assertEqual((1, 1, '# c'), _prev_src(['a \\', ' # c'], 0, 0, 1, 4, True, None))
        self.assertEqual((1, 1, '# '), _prev_src(['a \\', ' # c'], 0, 0, 1, 3, True, None))
        self.assertEqual((1, 1, '#'), _prev_src(['a \\', ' # c'], 0, 0, 1, 2, True, None))
        self.assertEqual((0, 0, 'a'), _prev_src(['a \\', ' # c'], 0, 0, 1, 1, True, None))
        self.assertEqual((1, 1, '# c'), _prev_src(['a', ' # c'], 0, 0, 1, 4, True, None))
        self.assertEqual((1, 1, '# '), _prev_src(['a', ' # c'], 0, 0, 1, 3, True, None))
        self.assertEqual((1, 1, '#'), _prev_src(['a', ' # c'], 0, 0, 1, 2, True, None))
        self.assertEqual(None, _prev_src(['a', ' # c'], 0, 0, 1, 1, True, None))

        state = []
        self.assertEqual((0, 4, '# c \\'), _prev_src(['a b # c \\'], 0, 0, 0, 9, True, True, state=state))
        self.assertEqual((0, 2, 'b'), _prev_src(['a b # c \\'], 0, 0, 0, 4, True, True, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b # c \\'], 0, 0, 0, 2, True, True, state=state))
        self.assertEqual(None, _prev_src(['a b # c \\'], 0, 0, 0, 0, True, True, state=state))

        state = []
        self.assertEqual((0, 2, 'b'), _prev_src(['a b # c \\'], 0, 0, 0, 9, False, True, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b # c \\'], 0, 0, 0, 2, False, True, state=state))
        self.assertEqual(None, _prev_src(['a b # c \\'], 0, 0, 0, 0, False, True, state=state))

        state = []
        self.assertEqual((0, 2, 'b'), _prev_src(['a b # c \\'], 0, 0, 0, 9, False, None, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b # c \\'], 0, 0, 0, 2, False, None, state=state))
        self.assertEqual(None, _prev_src(['a b # c \\'], 0, 0, 0, 0, False, None, state=state))

        state = []
        self.assertEqual((0, 4, '# c \\'), _prev_src(['a b # c \\'], 0, 0, 0, 9, True, None, state=state))
        self.assertEqual((0, 2, 'b'), _prev_src(['a b # c \\'], 0, 0, 0, 4, True, None, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b # c \\'], 0, 0, 0, 2, True, None, state=state))
        self.assertEqual(None, _prev_src(['a b # c \\'], 0, 0, 0, 0, True, None, state=state))

        state = []
        self.assertEqual((0, 4, 'c'), _prev_src(['a b c \\'], 0, 0, 0, 9, True, None, state=state))
        self.assertEqual((0, 2, 'b'), _prev_src(['a b c \\'], 0, 0, 0, 4, True, None, state=state))
        self.assertEqual((0, 0, 'a'), _prev_src(['a b c \\'], 0, 0, 0, 2, True, None, state=state))
        self.assertEqual(None, _prev_src(['a b c \\'], 0, 0, 0, 0, True, None, state=state))

        self.assertEqual((0, 0, '('), _prev_src(['(# comment', ''], 0, 0, 1, 0))
        self.assertEqual((0, 1, '# comment'), _prev_src(['(# comment', ''], 0, 0, 1, 0, True))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0, False, False))
        self.assertEqual((0, 1, '\\'), _prev_src(['(\\', ''], 0, 0, 1, 0, False, True))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0, False, None))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0, True, False))
        self.assertEqual((0, 1, '\\'), _prev_src(['(\\', ''], 0, 0, 1, 0, True, True))
        self.assertEqual((0, 0, '('), _prev_src(['(\\', ''], 0, 0, 1, 0, True, None))

    def test__next_prev_find(self):
        from fst.misc import _next_find, _prev_find

        lines = '''
  ; \\
  # hello
  \\
  # world
  # word
            '''.split('\n')

        self.assertEqual((1, 2), _prev_find(lines, 0, 0, 5, 0, ';'))
        self.assertEqual((1, 2), _prev_find(lines, 0, 0, 5, 0, ';', True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, ';', True, comment=True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, ';', True, lcont=True))
        self.assertEqual((1, 2), _prev_find(lines, 0, 0, 2, 0, ';', True, lcont=None))
        self.assertEqual(None, _prev_find(lines, 0, 0, 3, 0, ';', True, lcont=None))
        self.assertEqual((1, 2), _prev_find(lines, 0, 0, 5, 0, ';', False, comment=True, lcont=True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, ';', True, comment=True, lcont=True))
        self.assertEqual((5, 2), _prev_find(lines, 0, 0, 6, 0, '# word', False, comment=True, lcont=True))
        self.assertEqual((4, 2), _prev_find(lines, 0, 0, 6, 0, '# world', False, comment=True, lcont=True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, '# world', False, comment=False, lcont=True))
        self.assertEqual((2, 2), _prev_find(lines, 0, 0, 5, 0, '# hello', False, comment=True, lcont=True))
        self.assertEqual(None, _prev_find(lines, 0, 0, 5, 0, '# hello', True, comment=True, lcont=True))

        lines = '''
  \\
  # hello
  ; \\
  # world
  # word
            '''.split('\n')

        self.assertEqual((3, 2), _next_find(lines, 2, 0, 6, 0, ';'))
        self.assertEqual((3, 2), _next_find(lines, 2, 0, 6, 0, ';', True))
        self.assertEqual(None, _next_find(lines, 2, 0, 6, 0, ';', True, comment=True))
        self.assertEqual((3, 2), _next_find(lines, 2, 0, 6, 0, ';', True, lcont=True))
        self.assertEqual(None, _next_find(lines, 2, 0, 6, 0, ';', True, lcont=None))
        self.assertEqual(None, _next_find(lines, 3, 3, 6, 0, '# word', False))
        self.assertEqual(None, _next_find(lines, 3, 3, 6, 0, '# word', True))
        self.assertEqual(None, _next_find(lines, 3, 3, 6, 0, '# word', True, comment=True))
        self.assertEqual((5, 2), _next_find(lines, 3, 3, 6, 0, '# word', False, comment=True))
        self.assertEqual(None, _next_find(lines, 3, 3, 6, 0, '# word', False, comment=True, lcont=None))
        self.assertEqual((4, 2), _next_find(lines, 3, 0, 6, 0, '# world', False, comment=True, lcont=None))
        self.assertEqual(None, _next_find(lines, 3, 0, 6, 0, '# word', False, comment=True, lcont=None))
        self.assertEqual((5, 2), _next_find(lines, 3, 0, 6, 0, '# word', False, comment=True, lcont=True))
        self.assertEqual(None, _next_find(lines, 3, 0, 6, 0, '# word', True, comment=True, lcont=True))

    def test__next_find_re(self):
        from fst.misc import _next_find_re

        lines = '''
  \\
  # hello
  aaab ; \\
  # world
b # word
            '''.split('\n')
        pat = re.compile('a*b')

        self.assertEqual((3, 2, 'aaab'), _next_find_re(lines, 2, 0, 6, 0, pat))
        self.assertEqual((3, 2, 'aaab'), _next_find_re(lines, 2, 0, 6, 0, pat, True))
        self.assertEqual(None, _next_find_re(lines, 2, 0, 6, 0, pat, True, comment=True))
        self.assertEqual((3, 2, 'aaab'), _next_find_re(lines, 2, 0, 6, 0, pat, True, lcont=True))
        self.assertEqual(None, _next_find_re(lines, 2, 0, 6, 0, pat, True, lcont=None))
        self.assertEqual((3, 3, 'aab'), _next_find_re(lines, 3, 3, 6, 0, pat, False))
        self.assertEqual((3, 4, 'ab'), _next_find_re(lines, 3, 4, 6, 0, pat, False))
        self.assertEqual((3, 5, 'b'), _next_find_re(lines, 3, 5, 6, 0, pat, True))
        self.assertEqual(None, _next_find_re(lines, 3, 6, 6, 0, pat, True))
        self.assertEqual((5, 0, 'b'), _next_find_re(lines, 3, 6, 6, 0, pat, False))
        self.assertEqual(None, _next_find_re(lines, 3, 6, 6, 0, pat, True))
        self.assertEqual((5, 0, 'b'), _next_find_re(lines, 3, 6, 6, 0, pat, False, comment=True))
        self.assertEqual(None, _next_find_re(lines, 3, 6, 6, 0, pat, False, comment=True, lcont=None))
        self.assertEqual((5, 0, 'b'), _next_find_re(lines, 4, 0, 6, 0, pat, False, comment=False, lcont=False))
        self.assertEqual(None, _next_find_re(lines, 4, 0, 6, 0, pat, False, comment=True, lcont=None))
        self.assertEqual((5, 0, 'b'), _next_find_re(lines, 4, 0, 6, 0, pat, False, comment=True, lcont=True))
        self.assertEqual(None, _next_find_re(lines, 4, 0, 6, 0, pat, True, comment=True, lcont=True))

    def test__leading_trivia(self):
        from fst.misc import _leading_trivia

        self.assertEqual(((0, 0), None, ''), _leading_trivia(['a'], 0, 0, 0, 0, 'all', True))

        ls = '''
[a,

# 1
   b, c]
        '''.strip().split('\n')

        self.assertEqual(((2, 0), (1, 0), '   '), _leading_trivia(ls, 0, 3, 3, 3, 'all', True))
        self.assertEqual(((3, 6), None, None), _leading_trivia(ls, 0, 3, 3, 6, 'all', True))

        ls = '''
[a,

# 1

 \\
# 2
  # 3
  b]
        '''.strip().split('\n')

        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, False, 0))
        self.assertEqual(((5, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, True, 0))
        self.assertEqual(((5, 0), (4, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, True, 1))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, True, 2))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, True, 3))
        self.assertEqual(((5, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 'block', 0))
        self.assertEqual(((5, 0), (4, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 'block', 1))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 'block', 2))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 'block', 3))
        self.assertEqual(((2, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 'all', 0))
        self.assertEqual(((2, 0), (1, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 'all', 1))
        self.assertEqual(((2, 0), (1, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 'all', 2))

        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 8, 0))
        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 7, 0))
        self.assertEqual(((6, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 6, 0))
        self.assertEqual(((5, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 5, 0))
        self.assertEqual(((4, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 4, 0))
        self.assertEqual(((3, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 3, 0))
        self.assertEqual(((2, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 2, 0))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 1, 0))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 0, 0))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, -1, 0))

        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 8, 1))
        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 7, 1))
        self.assertEqual(((6, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 6, 1))
        self.assertEqual(((5, 0), (4, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 5, 1))
        self.assertEqual(((4, 0), (3, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 4, 1))
        self.assertEqual(((3, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 3, 1))
        self.assertEqual(((2, 0), (1, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 2, 1))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 1, 1))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 0, 1))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, -1, 1))

        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 8, 2))
        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 7, 2))
        self.assertEqual(((6, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 6, 2))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 5, 2))
        self.assertEqual(((4, 0), (3, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 4, 2))
        self.assertEqual(((3, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 3, 2))
        self.assertEqual(((2, 0), (1, 0), '  '), _leading_trivia(ls, 0, 3, 7, 2, 2, 2))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 1, 2))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, 0, 2))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 0, 3, 7, 2, -1, 2))

        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, False, 0))
        self.assertEqual(((5, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, True, 0))
        self.assertEqual(((5, 0), (4, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, True, 1))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, True, 2))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, True, 3))
        self.assertEqual(((5, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 'block', 0))
        self.assertEqual(((5, 0), (4, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 'block', 1))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 'block', 2))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 'block', 3))
        self.assertEqual(((2, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 'all', 0))
        self.assertEqual(((2, 0), (1, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 'all', 1))
        self.assertEqual(((2, 0), (1, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 'all', 2))

        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 8, 0))
        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 7, 0))
        self.assertEqual(((6, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 6, 0))
        self.assertEqual(((5, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 5, 0))
        self.assertEqual(((4, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 4, 0))
        self.assertEqual(((3, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 3, 0))
        self.assertEqual(((2, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 2, 0))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 1, 0))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 0, 0))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, -1, 0))

        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 8, 1))
        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 7, 1))
        self.assertEqual(((6, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 6, 1))
        self.assertEqual(((5, 0), (4, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 5, 1))
        self.assertEqual(((4, 0), (3, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 4, 1))
        self.assertEqual(((3, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 3, 1))
        self.assertEqual(((2, 0), (1, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 2, 1))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 1, 1))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 0, 1))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, -1, 1))

        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 8, 2))
        self.assertEqual(((7, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 7, 2))
        self.assertEqual(((6, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 6, 2))
        self.assertEqual(((5, 0), (3, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 5, 2))
        self.assertEqual(((4, 0), (3, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 4, 2))
        self.assertEqual(((3, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 3, 2))
        self.assertEqual(((2, 0), (1, 0), '  '), _leading_trivia(ls, 1, 0, 7, 2, 2, 2))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 1, 2))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, 0, 2))
        self.assertEqual(((1, 0), None, '  '), _leading_trivia(ls, 1, 0, 7, 2, -1, 2))

        ls = '''
[a



]
        '''.strip().split('\n')

        self.assertEqual(((4, 0), None, ''), _leading_trivia(ls, 0, 2, 4, 0, 'all', 0))
        self.assertEqual(((4, 0), (3, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 'all', 1))
        self.assertEqual(((4, 0), (2, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 'all', 2))
        self.assertEqual(((4, 0), (1, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 'all', 3))

        self.assertEqual(((4, 0), None, ''), _leading_trivia(ls, 0, 2, 4, 0, 4, 0))
        self.assertEqual(((4, 0), (3, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 4, 1))
        self.assertEqual(((4, 0), (2, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 4, 2))
        self.assertEqual(((4, 0), (1, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 4, 3))

        self.assertEqual(((3, 0), None, ''), _leading_trivia(ls, 0, 2, 4, 0, 3, 0))
        self.assertEqual(((3, 0), (2, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 3, 1))
        self.assertEqual(((3, 0), (1, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 3, 2))
        self.assertEqual(((3, 0), (1, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 3, 3))

        self.assertEqual(((2, 0), None, ''), _leading_trivia(ls, 0, 2, 4, 0, 2, 0))
        self.assertEqual(((2, 0), (1, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 2, 1))
        self.assertEqual(((2, 0), (1, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 2, 2))
        self.assertEqual(((2, 0), (1, 0), ''), _leading_trivia(ls, 0, 2, 4, 0, 2, 3))

        self.assertEqual(((1, 0), None, ''), _leading_trivia(ls, 0, 2, 4, 0, 1, 0))
        self.assertEqual(((1, 0), None, ''), _leading_trivia(ls, 0, 2, 4, 0, 1, 1))
        self.assertEqual(((1, 0), None, ''), _leading_trivia(ls, 0, 2, 4, 0, 1, 2))
        self.assertEqual(((1, 0), None, ''), _leading_trivia(ls, 0, 2, 4, 0, 1, 3))

    def test__trailing_trivia(self):
        from fst.misc import _trailing_trivia

        self.assertEqual(((0, 1), (0, 4), True), _trailing_trivia(['a   '], 0, 4, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 4), True), _trailing_trivia(['a  \\'], 0, 4, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 3), False), _trailing_trivia(['a  b'], 0, 4, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 2), False), _trailing_trivia(['a #c'], 0, 4, 0, 1, 'all', True))
        self.assertEqual(((0, 1), None, False), _trailing_trivia(['a# c'], 0, 4, 0, 1, 'all', True))

        self.assertRaises(AssertionError, _trailing_trivia, ['a   '], -1, 4, 0, 1, 'all', True)
        self.assertRaises(AssertionError, _trailing_trivia, ['a   '], 0, 0, 0, 1, 'all', True)

        self.assertEqual(((0, 1), None, True), _trailing_trivia(['a'], 0, 1, 0, 1, 'all', True))
        self.assertEqual(((0, 1), None, False), _trailing_trivia(['a   '], 0, 1, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 2), False), _trailing_trivia(['a   '], 0, 2, 0, 1, 'all', True))

        self.assertEqual(((0, 1), None, False), _trailing_trivia(['ab'], 0, 2, 0, 1, 'all', True))
        self.assertEqual(((0, 1), (0, 2), False), _trailing_trivia(['a c'], 0, 3, 0, 1, 'all', True))
        self.assertEqual(((0, 1), None, False), _trailing_trivia(['a#c'], 0, 3, 0, 1, False, True))
        self.assertEqual(((0, 1), (0, 2), False), _trailing_trivia(['a # c'], 0, 5, 0, 1, False, True))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(['a ', ' b'], 1, 2, 0, 1, 'line', True))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(['a # c', ''], 1, 0, 0, 1, 'line', True))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(['a # c', ' b'], 1, 2, 0, 1, 'line', True))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(['a # c', '', ' b'], 2, 2, 0, 1, 'line', False))

        self.assertEqual(((1, 0), (2, 0), True), _trailing_trivia(['a # c', '', ' b'], 2, 2, 0, 1, 'line', True))
        self.assertEqual(((1, 0), (2, 0), True), _trailing_trivia(['a # c', '', ''], 2, 0, 0, 1, 'line', True))
        self.assertEqual(((1, 0), (2, 0), True), _trailing_trivia(['a # c', '', '# c'], 2, 3, 0, 1, 'line', True))
        self.assertEqual(((1, 0), (2, 0), True), _trailing_trivia(['a # c', '', '', ''], 3, 0, 0, 1, 'line', 1))
        self.assertEqual(((1, 0), (3, 0), True), _trailing_trivia(['a # c', '', '', ''], 3, 0, 0, 1, 'line', 2))

        ls = '''
[a, # 1
# 2

 \\
  # 3

  b]
        '''.strip().split('\n')

        self.assertEqual(((0, 3), (0, 4), False), _trailing_trivia(ls, 6, 2, 0, 3, False, 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, True, 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, True, 1))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, True, 2))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 'line', 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 'line', 1))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 'line', 2))
        self.assertEqual(((2, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 'block', 0))
        self.assertEqual(((2, 0), (3, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 'block', 1))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 'block', 2))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 'block', 3))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 'all', 0))
        self.assertEqual(((5, 0), (6, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 'all', 1))
        self.assertEqual(((5, 0), (6, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 'all', 2))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, -1, 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 0, 0))
        self.assertEqual(((2, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 1, 0))
        self.assertEqual(((3, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 2, 0))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 3, 0))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 4, 0))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 5, 0))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 6, 0))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 7, 0))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, -1, 1))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 0, 1))
        self.assertEqual(((2, 0), (3, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 1, 1))
        self.assertEqual(((3, 0), (4, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 2, 1))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 3, 1))
        self.assertEqual(((5, 0), (6, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 4, 1))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 5, 1))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 6, 1))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 7, 1))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, -1, 2))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 0, 2))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 1, 2))
        self.assertEqual(((3, 0), (4, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 2, 2))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 3, 2))
        self.assertEqual(((5, 0), (6, 0), True), _trailing_trivia(ls, 6, 2, 0, 3, 4, 2))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 5, 2))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 6, 2))
        self.assertEqual(((6, 0), None, True), _trailing_trivia(ls, 6, 2, 0, 3, 7, 2))

        self.assertEqual(((0, 3), (0, 4), False), _trailing_trivia(ls, 5, 0, 0, 3, False, 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, True, 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, True, 1))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, True, 2))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 'line', 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 'line', 1))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 'line', 2))
        self.assertEqual(((2, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 'block', 0))
        self.assertEqual(((2, 0), (3, 0), True), _trailing_trivia(ls, 5, 0, 0, 3, 'block', 1))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(ls, 5, 0, 0, 3, 'block', 2))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(ls, 5, 0, 0, 3, 'block', 3))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 'all', 0))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 'all', 1))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 'all', 2))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, -1, 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 0, 0))
        self.assertEqual(((2, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 1, 0))
        self.assertEqual(((3, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 2, 0))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 3, 0))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 4, 0))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 5, 0))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 6, 0))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 7, 0))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, -1, 1))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 0, 1))
        self.assertEqual(((2, 0), (3, 0), True), _trailing_trivia(ls, 5, 0, 0, 3, 1, 1))
        self.assertEqual(((3, 0), (4, 0), True), _trailing_trivia(ls, 5, 0, 0, 3, 2, 1))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 3, 1))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 4, 1))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 5, 1))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 6, 1))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 7, 1))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, -1, 2))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 0, 2))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(ls, 5, 0, 0, 3, 1, 2))
        self.assertEqual(((3, 0), (4, 0), True), _trailing_trivia(ls, 5, 0, 0, 3, 2, 2))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 3, 2))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 4, 2))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 5, 2))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 6, 2))
        self.assertEqual(((5, 0), None, True), _trailing_trivia(ls, 5, 0, 0, 3, 7, 2))

        ls = '''
[a



]
        '''.strip().split('\n')

        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 4, 0, 0, 2, 'all', 0))
        self.assertEqual(((1, 0), (2, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 'all', 1))
        self.assertEqual(((1, 0), (3, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 'all', 2))
        self.assertEqual(((1, 0), (4, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 'all', 3))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(ls, 4, 0, 0, 2, 0, 0))
        self.assertEqual(((1, 0), (2, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 0, 1))
        self.assertEqual(((1, 0), (3, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 0, 2))
        self.assertEqual(((1, 0), (4, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 0, 3))

        self.assertEqual(((2, 0), None, True), _trailing_trivia(ls, 4, 0, 0, 2, 1, 0))
        self.assertEqual(((2, 0), (3, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 1, 1))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 1, 2))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 1, 3))

        self.assertEqual(((3, 0), None, True), _trailing_trivia(ls, 4, 0, 0, 2, 2, 0))
        self.assertEqual(((3, 0), (4, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 2, 1))
        self.assertEqual(((3, 0), (4, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 2, 2))
        self.assertEqual(((3, 0), (4, 0), True), _trailing_trivia(ls, 4, 0, 0, 2, 2, 3))

        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 4, 0, 0, 2, 3, 0))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 4, 0, 0, 2, 3, 1))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 4, 0, 0, 2, 3, 2))
        self.assertEqual(((4, 0), None, True), _trailing_trivia(ls, 4, 0, 0, 2, 3, 3))

        # ends line on first line if hit bound and bound at end

        self.assertEqual(((0, 1), None, True), _trailing_trivia(['a'], 0, 1, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), None, False), _trailing_trivia(['a '], 0, 1, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (0, 2), True), _trailing_trivia(['a '], 0, 2, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (0, 2), False), _trailing_trivia(['a  '], 0, 2, 0, 1, 'all', 0))
        self.assertEqual(((0, 1), (0, 3), True), _trailing_trivia(['a  '], 0, 3, 0, 1, 'all', 0))

        # hit bound not non-start line

        self.assertEqual(((1, 0), None, True), _trailing_trivia(['a ', ''], 1, 1, 0, 1, 'all', 0))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(['a', ''], 1, 0, 0, 1, 'all', 0))
        self.assertEqual(((1, 0), None, True), _trailing_trivia(['a', ' '], 1, 1, 0, 1, 'all', 0))

        self.assertEqual(((1, 0), None, True), _trailing_trivia(['a', ''], 1, 0, 0, 1, 'all', 1))
        self.assertEqual(((1, 0), (1, 1), True), _trailing_trivia(['a', ' '], 1, 1, 0, 1, 'all', 1))

        self.assertEqual(((1, 3), None, True), _trailing_trivia(['a', '# c'], 1, 3, 0, 1, 'all', 0))
        self.assertEqual(((2, 0), None, True), _trailing_trivia(['a', '# c', ''], 2, 0, 0, 1, 'all', 0))
        self.assertEqual(((2, 0), None, True), _trailing_trivia(['a', '# c', ''], 2, 0, 0, 1, 'all', 1))
        self.assertEqual(((2, 0), (2, 1), True), _trailing_trivia(['a', '# c', ' '], 2, 1, 0, 1, 'all', 1))
        self.assertEqual(((2, 0), (3, 0), True), _trailing_trivia(['a', '# c', ' ', ''], 3, 0, 0, 1, 'all', 1))
        self.assertEqual(((2, 0), (3, 0), True), _trailing_trivia(['a', '# c', ' ', ' '], 3, 1, 0, 1, 'all', 1))
        self.assertEqual(((2, 0), (3, 1), True), _trailing_trivia(['a', '# c', ' ', ' '], 3, 1, 0, 1, 'all', 2))
        self.assertEqual(((2, 0), (4, 0), True), _trailing_trivia(['a', '# c', ' ', ' ', ''], 4, 0, 0, 1, 'all', 2))

    def test__multiline_str_continuation_lns(self):
        from fst.misc import _multiline_str_continuation_lns as mscl

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

    def test__multiline_fstr_continuation_lns(self):
        from fst.misc import _multiline_fstr_continuation_lns as mscl

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

        # with values

        self.assertEqual([], mscl(ls := r'''
f"a{1}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

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
        from fst.misc import _multiline_fstr_continuation_lns as mscl

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
