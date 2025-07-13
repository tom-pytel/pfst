#!/usr/bin/env python

import doctest
import os
import sys
import unittest
from types import FunctionType, ModuleType

import fst

# VERBOSE = any(arg == '-v' for arg in sys.argv)


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


def load_tests(loader, tests, ignore):
    if '-k' in sys.argv:
        for i, a in enumerate(sys.argv):
            if a == '-k' and i < len(sys.argv) - 1 and sys.argv[i + 1] == 'doctests':
                break

        else:
            return tests

    path_doctests = os.path.join(os.path.split(__file__)[0], 'doctests')

    for dir, _, fnms in os.walk(path_doctests):
        for fnm in sorted(fnms):
            if fnm.startswith('test_') and fnm.endswith('.txt'):
                full_fnm = os.path.join(dir, fnm)

                tests.addTests(doctest.DocFileSuite(full_fnm[len(path_doctests) - 8:]))

    return tests


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

    # def test_standalone(self):
    #     if VERBOSE:
    #         print()

    #     path_doctests = os.path.join(os.path.split(__file__)[0], 'doctests')

    #     for dir, _, fnms in os.walk(path_doctests):
    #         for fnm in sorted(fnms):
    #             if fnm.startswith('test_') and fnm.endswith('.txt'):
    #                 full_fnm = os.path.join(dir, fnm)

    #                 if VERBOSE:
    #                     print('......................................................................')
    #                     print(full_fnm[len(path_doctests) - 8:])

    #                 doctest.testfile(full_fnm, module_relative=False)


if __name__ == '__main__':
    unittest.main()
