#!/usr/bin/env python

import os
import unittest
from ast import parse as ast_parse

from fst.astutil import *
from fst import *
# from fst.asttypes import TemplateStr, type_param, TypeVar, ParamSpec, TypeVarTuple

PYFNMS = sum((
    [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
    for top in ('src', 'tests')),
    start=[]
)


def read(fnm):
    with open(fnm) as f:
        return f.read()


class TestFST(unittest.TestCase):
    """These take a while to execute (relatively speaking for quick checking) so are annoying for now. TODO: Make
    specific long / thorough test mode which will execute these and more bulk tests."""

    # def test_copy_ast_bulk(self):
    #     for fnm in PYFNMS:
    #         with open(fnm) as f:
    #             src = f.read()

    #         for type_comments in (False, True):
    #             ast = parse(src, type_comments=type_comments)
    #             dst = copy_ast(ast)

    #             compare_asts(ast, dst, locs=True, type_comments=type_comments, raise_=True)

    # def test_fromsrc_bulk(self):
    #     for fnm in PYFNMS:
    #         fst = FST.fromsrc(read(fnm))

    #         for ast in walk(fst.a):
    #             ast.f.loc

    #         fst.verify(raise_=True)

    # def test_fromast_bulk(self):
    #     for fnm in PYFNMS:
    #         fst = FST.fromast(ast_parse(read(fnm)))

    #         for ast in walk(fst.a):
    #             ast.f.loc

    #         fst.verify(raise_=True)

    # def test_walk_bulk(self):
    #     for fnm in PYFNMS:
    #         ast       = FST.fromsrc(read(fnm)).a
    #         bln, bcol = 0, 0

    #         for f in (gen := ast.f.walk(True)):
    #             if isinstance(f.a, (JoinedStr, TemplateStr)):  # these are borked
    #                 gen.send(False)

    #                 continue

    #             self.assertTrue(f.bln > bln or (f.bln == bln and f.bcol >= bcol))

    #             lof = list(f.walk(True, self_=False, recurse=False))
    #             lob = list(f.walk(True, self_=False, recurse=False, back=True))

    #             self.assertEqual(lof, lob[::-1])

    #             lf, c = [], None
    #             while c := f.next_child(c, True): lf.append(c)
    #             self.assertEqual(lf, lof)

    #             lb, c = [], None
    #             while c := f.prev_child(c, True): lb.append(c)
    #             self.assertEqual(lb, lob)

    #             bln, bcol = f.bln, f.bcol

    # def test_copy_bulk(self):
    #     for fnm in PYFNMS:
    #         ast = FST.fromsrc(read(fnm)).a

    #         for a in walk(ast):
    #             if a.f.is_parsable():
    #                 f = a.f.copy()

    #                 f.verify(raise_=True)


if __name__ == '__main__':
    unittest.main()
