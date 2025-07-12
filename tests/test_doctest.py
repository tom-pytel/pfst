#!/usr/bin/env python

import doctest
import os
import sys
import unittest
from types import FunctionType, ModuleType

import fst


# def load_tests(loader, tests, ignore):
#     print(loader)
#     print(tests)
#     print(ignore)
#     print(__file__)
#     print(__path__)

#     return tests


def cleanup_docstrs_recurse(obj, exclude: set[str] = set()):
    for name, o in obj.__dict__.items():
        if isinstance(o, (FunctionType, type, staticmethod, classmethod, property)):
            o = getattr(obj, name)

            if doc := getattr(o, '__doc__', None):
                try:
                    doc       = '' if name in exclude else doc.replace('```', '')
                    o.__doc__ = doc

                except Exception:
                    pass

                else:
                    if not isinstance(o, property):
                        cleanup_docstrs_recurse(o, exclude)


def cleanup_docstrs(obj, exclude: set[str] = set()):
    if doc := getattr(obj, '__doc__', None):  # at the module level
        obj.__doc__ = doc.replace('```', '')

    cleanup_docstrs_recurse(obj, exclude)


class TestDocTest(unittest.TestCase):
    def test_fst(self):
        options = fst.FST.get_options()

        try:
            for mod in (fst.fst,):
                cleanup_docstrs(mod)

                self.assertEqual(0, doctest.testmod(mod).failed)

        finally:
            fst.FST.set_options(**options)

    def test_view(self):
        options = fst.FST.get_options()

        try:
            mod = sys.modules['fst.view']

            cleanup_docstrs(mod)
            self.assertEqual(0, doctest.testmod(mod).failed)

        finally:
            fst.FST.set_options(**options)

    def test_docs(self):
        from fst import docs

        mods    = list(sorted((m for m in docs.__dict__.values() if isinstance(m, ModuleType)),
                              key=lambda m: m.__name__))
        options = fst.FST.get_options()

        try:
            for mod in mods:
                cleanup_docstrs(mod)
                self.assertEqual(0, doctest.testmod(mod).failed)

        finally:
            fst.FST.set_options(**options)

    def test_standalone(self):
        for dir, _, fnms in os.walk(os.path.join(os.path.split(__file__)[0], 'doctests')):
            for fnm in sorted(fnms):
                if fnm.startswith('test_') and fnm.endswith('.txt'):
                    doctest.testfile(os.path.join(dir, fnm), module_relative=False)


if __name__ == '__main__':
    unittest.main()
