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
    def test_calculated_loc_arguments(self):
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.loc)

    def test_calculated_loc_withitem(self):
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.loc)

    def test_calculated_loc_matchcase(self):
        self.assertEqual((1, 7, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.loc)

    def test_from_src(self):
        for fnm in PYFNMS:
            fst = FST.from_src(read(fnm))

            walktest(fst.ast)
            fst.verify()

    def test_from_ast_calc_loc_False(self):
        for fnm in PYFNMS:
            fst = FST.from_ast(ast_.parse(ast_.unparse(ast_.parse(read(fnm)))), calc_loc=False)

            walktest(fst.ast)
            fst.verify()

    def test_from_ast_calc_loc_True(self):
        for fnm in PYFNMS:
            fst = FST.from_ast(ast_.parse(read(fnm)), calc_loc=True)

            walktest(fst.ast)
            fst.verify()

    def test_from_ast_calc_loc_copy(self):
        for fnm in PYFNMS:
            fst = FST.from_ast(ast_.parse(read(fnm)), calc_loc='copy')

            walktest(fst.ast)
            fst.verify()

    def test_verify(self):
        ast = parse('i = 1')

        ast.f.verify()

        ast.body[0].lineno = 100

        self.assertRaises(RuntimeError, ast.f.verify)
        self.assertEqual(None, ast.f.verify(do_raise=False))

    def test_starts_new_line(self):
        ast = parse('i = 1; j = 2')

        self.assertEqual('', ast.body[0].f.starts_new_line())
        self.assertEqual(None, ast.body[1].f.starts_new_line())

        ast = parse('def f(): \\\n i = 1')

        self.assertEqual('', ast.body[0].f.starts_new_line())
        self.assertEqual(None, ast.body[0].body[0].f.starts_new_line())

        ast = parse('class cls: i = 1')

        self.assertEqual('', ast.body[0].f.starts_new_line())
        self.assertEqual(None, ast.body[0].body[0].f.starts_new_line())

        ast = parse('class cls: i = 1; \\\n    j = 2')

        self.assertEqual(None, ast.body[0].body[0].f.starts_new_line())
        self.assertEqual(None, ast.body[0].body[1].f.starts_new_line())

        ast = parse('class cls:\n  i = 1; \\\n    j = 2')

        self.assertEqual('  ', ast.body[0].body[0].f.starts_new_line())
        self.assertEqual(None, ast.body[0].body[1].f.starts_new_line())

    def test_get_indent(self):
        ast = parse('i = 1; j = 2')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual('', ast.body[1].f.get_indent())

        ast = parse('def f(): \\\n i = 1')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())

        ast = parse('class cls: i = 1')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())

        ast = parse('class cls: i = 1; \\\n    j = 2')

        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[1].f.get_indent())

        ast = parse('class cls:\n  i = 1; \\\n    j = 2')

        self.assertEqual('  ', ast.body[0].body[0].f.get_indent())
        self.assertEqual('  ', ast.body[0].body[1].f.get_indent())

        ast = parse('class cls:\n   def f(): i = 1')

        self.assertEqual('   ', ast.body[0].body[0].f.get_indent())
        self.assertEqual('   ' + ast.f.root.indent, ast.body[0].body[0].body[0].f.get_indent())

    def test_snip(self):
        src = 'class cls:\n if True:\n  i = 1\n else:\n  j = 2'
        ast = parse(src)

        self.assertEqual(src.split('\n'), ast.f.snip())
        self.assertEqual(src.split('\n'), ast.body[0].f.snip())
        self.assertEqual('if True:\n  i = 1\n else:\n  j = 2'.split('\n'), ast.body[0].body[0].f.snip())
        self.assertEqual(['i = 1'], ast.body[0].body[0].body[0].f.snip())
        self.assertEqual(['j = 2'], ast.body[0].body[0].orelse[0].f.snip())

        self.assertEqual(['True:', '  i'], ast.f.root.sniploc(1, 4, 2, 3))


if __name__ == '__main__':
    unittest.main()
