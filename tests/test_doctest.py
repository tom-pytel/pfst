#!/usr/bin/env python

import doctest
import importlib
import os
import sys
import unittest
from types import FunctionType

import fst


def cleanup_docstrs_recurse(obj, exclude: set[str] = set()):
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
                    cleanup_docstrs_recurse(o, exclude)


def cleanup_docstrs(obj, exclude: set[str] = set()):
    if doc := getattr(obj, '__doc__', None):  # at the module level
        obj.__doc__ = doc.replace('```', '')

    cleanup_docstrs_recurse(obj, exclude)


class TestDocTest(unittest.TestCase):
    def test_fst(self):
        options = fst.FST.get_options()

        try:
            for mod in (fst.fst, fst.fst_reconcile, fst.fst_walk):
                cleanup_docstrs(mod)

                self.assertEqual(0, doctest.testmod(mod).failed)

        finally:
            fst.FST.set_options(**options)

    def test_fstview(self):
        view = sys.modules['fst.view']

        cleanup_docstrs(view)
        self.assertEqual(0, doctest.testmod(view).failed)

    def test_examples(self):
        sys.path.insert(0, '')

        try:
            for example in sorted(e for e in os.listdir('examples') if e.endswith('.py') and not e.startswith('__')):
                mod = importlib.import_module(f'examples.{example[:-3]}')

                cleanup_docstrs(mod)

                self.assertEqual(0, doctest.testmod(mod).failed)

        finally:
            del sys.path[0]


if __name__ == '__main__':
    unittest.main()
