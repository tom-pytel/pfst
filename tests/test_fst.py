#!/usr/bin/env python

import os
import unittest

import ast as ast_
from fst import *

PYFNMS = sum((
    [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
    for top in ('src', 'tests')),
    start=[]
)

def read(fnm):
    with open(fnm) as f:
        return f.read()

def walktest(ast):
    for ast in walk(ast):
        ast.f.loc


class TestFST(unittest.TestCase):
    def test_pos_arguments(self):
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.loc)

    def test_pos_withitem(self):
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.loc)

    def test_pos_matchcase(self):
        self.assertEqual((1, 7, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.loc)

    def test_from_src(self):
        for fnm in PYFNMS:
            walktest(FST.from_src(read(fnm)).ast)

    def test_from_ast_calc_loc_False(self):
        for fnm in PYFNMS:
            walktest(FST.from_ast(ast_.parse(ast_.unparse(ast_.parse(read(fnm)))), calc_loc=False).ast)

    def test_from_ast_calc_loc_True(self):
        for fnm in PYFNMS:
            walktest(FST.from_ast(ast_.parse(read(fnm)), calc_loc=True).ast)

    def test_from_ast_calc_loc_copy(self):
        for fnm in PYFNMS:
            walktest(FST.from_ast(ast_.parse(read(fnm)), calc_loc='copy').ast)


if __name__ == '__main__':
    unittest.main()
