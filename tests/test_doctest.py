#!/usr/bin/env python

import doctest
import sys
import unittest
from types import FunctionType

import fst


def cleanup_docstrs(obj, exclude: set[str] = set()):
    for name, o in obj.__dict__.items():
        if isinstance(o, (FunctionType, type, staticmethod, classmethod)):
            o = getattr(obj, name)

            if doc := getattr(o, '__doc__', None):
                try:
                    doc       = '' if name in exclude else doc.replace('```', '')
                    o.__doc__ = doc

                except Exception:
                    pass
                else:
                    cleanup_docstrs(o, exclude)


class TestDocTest(unittest.TestCase):
    def test_fst(self):
        options = fst.FST.get_options()

        try:
            cleanup_docstrs(fst.fst, {'parse'})  # exclude parse because of change in ast.dump() behavior between py 3.12 and 3.13
            self.assertEqual(0, doctest.testmod(fst.fst).failed)

        finally:
            fst.FST.set_options(**options)

    def test_fstview(self):
        fstview = sys.modules['fst.fstview']

        cleanup_docstrs(fstview)
        self.assertEqual(0, doctest.testmod(fstview).failed)


if __name__ == '__main__':
    unittest.main()
