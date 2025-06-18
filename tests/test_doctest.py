#!/usr/bin/env python

import doctest
import unittest
from types import FunctionType

import fst


def cleanup_docstrs(obj, exclude: set[str] = set()):
    for name, o in obj.__dict__.items():
        if isinstance(o, (FunctionType, type, staticmethod, classmethod)):
            o = getattr(obj, name)

            if doc := getattr(o, '__doc__', None):
                try:
                    doc       = '' if name in exclude else doc.replace('```', '')#.replace(r'\\n', '\n')
                    o.__doc__ = doc

                except Exception:
                    pass
                else:
                    cleanup_docstrs(o, exclude)


class TestDocTest(unittest.TestCase):
    def test_fst(self):
        options = fst.FST.get_options()

        try:
            cleanup_docstrs(fst.fst, {'get_indentable_lns', 'is_enclosed'})  # just exclude these for now, backslashes

            results = doctest.testmod(fst.fst)

            self.assertEqual(0, results.failed)

        finally:
            fst.FST.set_options(**options)

    # def test_fstview(self):
    #     fstview = sys.modules['fst.fstview']

    #     cleanup_docstrs(fstview)

    #     results = doctest.testmod(fstview)

    #     self.assertEqual(0, results.failed)


if __name__ == '__main__':
    unittest.main()
