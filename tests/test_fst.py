#!/usr/bin/env python

import unittest
from fst import *


class TestFST(unittest.TestCase):
    def test_pos_arguments(self):
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.pos)

    def test_pos_withitem(self):
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.pos)

    def test_pos_matchcase(self):
        self.assertEqual((1, 7, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.pos)


if __name__ == '__main__':
    unittest.main()
