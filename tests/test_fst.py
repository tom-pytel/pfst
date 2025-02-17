#!/usr/bin/env python

import os
import sys
import unittest
import ast as ast_

from fst import *

PYFNMS = sum((
    [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
    for top in ('src', 'tests')),
    start=[]
)

CUT_DATA = [
("""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', None, None, """
()
""", """
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
"""),

("""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 0, 2, """
(3,  # third line
)
""", """
(       # hello
    1,  # last line
    2,  # second line
)
"""),

("""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 1, 2, """
(       # hello
    1,  # last line
    3,  # third line
)
""", """
(
    2,  # second line
)
"""),

("""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 2, None, """
(       # hello
    1,  # last line
    2,  # second line
)
""", """
(
    3,  # third line
)
"""),

("""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', None, None, """
()
""", """
(           # hello
    1, 2, 3 # last line
)
"""),

("""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 0, 2, """
(3, # last line
)
""", """
(           # hello
    1, 2)
"""),

("""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 1, 2, """
(           # hello
    1, 3 # last line
)
""", """
(2,)
"""),

("""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 2, None, """
(           # hello
    1, 2)
""", """
(3, # last line
)
"""),

("""
1, 2, 3, 4
""", 'body[0].value', 1, 3, """
1, 4
""", """
(2, 3)
"""),

("""
1, 2, 3, 4
""", 'body[0].value', -1, None, """
1, 2, 3
""", """
(4,)
"""),

("""
1, 2, 3, 4
""", 'body[0].value', None, None, """
()
""", """
(1, 2, 3, 4)
"""),

("""
1, 2, 3, 4
""", 'body[0].value', 1, 1, """
1, 2, 3, 4
""", """
()
"""),

("""
1, 2, 3, 4
""", 'body[0].value', 1, None, """
1,
""", """
(2, 3, 4)
"""),

("""
1, 2, 3, 4
""", 'body[0].value', 0, 3, """
4,
""", """
(1, 2, 3)
"""),

("""
(1, 2
  ,  # comment
3, 4)
""", 'body[0].value', 1, 2, """
(1, 3, 4)
""", """
(2
  ,  # comment
)
"""),

("""
(1, 2
  ,
3, 4)
""", 'body[0].value', 1, 2, """
(1, 3, 4)
""", """
(2
  ,
)
"""),

("""
(1, 2
  , 3, 4)
""", 'body[0].value', 1, 2, """
(1, 3, 4)
""", """
(2
  ,)
"""),

("""
(1, 2  # comment
  , 3, 4)
""", 'body[0].value', 1, 2, """
(1, 3, 4)
""", """
(2  # comment
  ,)
"""),

("""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', None, None, """
if 1:
    ()
""", """
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
"""),

("""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 0, 2, """
if 1:
    (3,  # third line
    )
""", """
(       # hello
    1,  # last line
    2,  # second line
)
"""),

("""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 1, 2, """
if 1:
    (       # hello
        1,  # last line
        3,  # third line
    )
""", """
(
    2,  # second line
)
"""),

("""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 2, None, """
if 1:
    (       # hello
        1,  # last line
        2,  # second line
    )
""", """
(
    3,  # third line
)
"""),

("""
{1: 2, **b, **c}
""", 'body[0].value', 1, 2, """
{1: 2, **c}
""", """
{**b}
"""),

("""
{1: 2, **b, **c}
""", 'body[0].value', None, None, """
{}
""", """
{1: 2, **b, **c}
"""),

("""
{1: 2, **b, **c}
""", 'body[0].value', 2, None, """
{1: 2, **b}
""", """
{**c}
"""),

("""
i =                (self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                id(self) & (_sys.maxsize*2 + 1))
""", 'body[0].value', 0, 3, """
i =                (id(self) & (_sys.maxsize*2 + 1),)
""", """
(self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                )
"""),

("""
i = namespace = {**__main__.__builtins__.__dict__,
             **__main__.__dict__}
""", 'body[0].value', 0, 1, """
i = namespace = {**__main__.__dict__}
""", """
{**__main__.__builtins__.__dict__,
             }
"""),

("""
env = {
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1",
    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}
""", 'body[0].value', None, 2, """
env = {"PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}
""", """
{
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1",
}
"""),

("""
(None, False, True, 12345, 123.45, 'abcde', 'абвгд', b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
""", 'body[0].value', 5, 7, """
(None, False, True, 12345, 123.45, b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
""", """
('abcde', 'абвгд')
"""),

]  # END OF CUT_DATA


def read(fnm):
    with open(fnm) as f:
        return f.read()


def walktest(ast):
    for ast in walk(ast):
        ast.f.loc


def dumptest(self, fst, dump, src):
    self.assertEqual(dump.strip(), '\n'.join(fst.dump(print=False)))
    self.assertEqual(src, fst.src)


class TestFST(unittest.TestCase):
    def test_loc(self):
        # from children
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.loc)
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.loc)
        self.assertEqual((1, 7, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.loc)

    def test_bloc(self):
        ast = parse('@deco\nclass cls:\n @deco\n def meth():\n  @deco\n  class fcls: pass')

        self.assertEqual((0, 0, 5, 18), ast.f.loc)
        self.assertEqual((0, 0, 5, 18), ast.f.bloc)
        self.assertEqual((1, 0, 5, 18), ast.body[0].f.loc)
        self.assertEqual((0, 0, 5, 18), ast.body[0].f.bloc)
        self.assertEqual((3, 1, 5, 18), ast.body[0].body[0].f.loc)
        self.assertEqual((2, 1, 5, 18), ast.body[0].body[0].f.bloc)
        self.assertEqual((5, 2, 5, 18), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((4, 2, 5, 18), ast.body[0].body[0].body[0].f.bloc)

    def test_fromsrc_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromsrc(read(fnm))

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_False_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(ast_.unparse(ast_.parse(read(fnm)))), calc_loc=False)

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_True_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(read(fnm)), calc_loc=True)

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_copy_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(read(fnm)), calc_loc='copy')

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_verify(self):
        ast = parse('i = 1')
        ast.f.verify(raise_=True)

        ast.body[0].lineno = 100

        self.assertRaises(WalkFail, ast.f.verify, raise_=True)
        self.assertEqual(None, ast.f.verify(raise_=False))

    def test_next_prev(self):
        fst = parse('a and b and c and d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.op.f)
        self.assertIs((f := fst.next_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.op.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        if sys.version_info[:2] >= (3, 12):
            fst = parse('@deco\ndef f[T, U](a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
            a = fst.a
            f = None
            self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, True)), a.args.f)
            self.assertIs((f := fst.next_child(f, True)), a.returns.f)
            self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, True)), None)
            f = None
            self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, False)), a.args.f)
            self.assertIs((f := fst.next_child(f, False)), a.returns.f)
            self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, False)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, True)), a.args.f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, True)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, False)), a.args.f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('@deco\ndef f(a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.args.f)
        self.assertIs((f := fst.next_child(f, True)), a.returns.f)
        self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.args.f)
        self.assertIs((f := fst.next_child(f, False)), a.returns.f)
        self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, True)), a.args.f)
        self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, False)), a.args.f)
        self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('a <= b == c >= d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.left.f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.left.f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.left.f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.left.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('match a:\n case {1: a, 2: b, **rest}: pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('match a:\n case cls(1, 2, a=3, b=4): pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.cls.f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.cls.f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

    def test_copy_lines(self):
        src = 'class cls:\n if True:\n  i = 1\n else:\n  j = 2'
        ast = parse(src)

        self.assertEqual(src.split('\n'), ast.f.copy_lines())
        self.assertEqual(src.split('\n'), ast.body[0].f.copy_lines())
        self.assertEqual('if True:\n  i = 1\n else:\n  j = 2'.split('\n'), ast.body[0].body[0].f.copy_lines())
        self.assertEqual(['i = 1'], ast.body[0].body[0].body[0].f.copy_lines())
        self.assertEqual(['j = 2'], ast.body[0].body[0].orelse[0].f.copy_lines())

        self.assertEqual(['True:', '  i'], ast.f.root.copyl_lines(1, 4, 2, 3))

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

        self.assertEqual('   ', parse('def f():\n   1').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): 1').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1').body[0].body[0].f.get_indent())

        self.assertEqual('    ', parse('class cls:\n def f():\n    1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('     ', parse('class cls:\n def f(): 1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('     ', parse('class cls:\n def f(): \\\n   1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('class cls:\n def f(): # \\\n   1').body[0].body[0].body[0].f.get_indent())

        self.assertEqual('  ', parse('if 1:\n  2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: 2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: \\\n 2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('if 1: # \\\n  2\nelse:\n   3').body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('if 1:\n  2\nelse:\n   3').body[0].orelse[0].f.get_indent())
        self.assertEqual('    ', parse('if 1:\n  2\nelse: 3').body[0].orelse[0].f.get_indent())
        self.assertEqual('    ', parse('if 1:\n  2\nelse: \\\n 3').body[0].orelse[0].f.get_indent())
        self.assertEqual('   ', parse('if 1:\n  2\nelse: # \\\n   3').body[0].orelse[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): 1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1; 2').body[0].body[1].f.get_indent())

        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[1].f.get_indent())

        self.assertEqual('', parse('\\\ni').body[0].f.get_indent())
        self.assertEqual('    ', parse('try: i\nexcept: pass').body[0].body[0].f.get_indent())

    def test__indentable_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = "... \\\n2"\n else:\n  j \\\n=\\\n 2'
        ast = parse(src)

        self.assertEqual({1, 2, 5, 7, 8, 9, 10}, ast.f._indentable_lns(1))
        self.assertEqual({0, 1, 2, 5, 7, 8, 9, 10}, ast.f._indentable_lns(0))

    def test__offset(self):
        src = 'i = 1\nj = 2\nk = 3'

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 5, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1, inc=True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 3, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1, inc=True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

    def test__offset_cols(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j = 2'

        ast = parse(src)
        lns = ast.f._indentable_lns(1)
        ast.f._offset_cols(1, lns)
        self.assertEqual({1, 2, 5, 6, 7}, lns)
        self.assertEqual((0, 0, 7, 7), ast.f.loc)
        self.assertEqual((0, 0, 7, 8), ast.body[0].f.loc)
        self.assertEqual((1, 2, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 5, 1, 9), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].f._indentable_lns(1)
        ast.body[0].body[0].f._offset_cols(1, lns)
        self.assertEqual({2, 5, 6, 7}, lns)
        self.assertEqual((1, 1, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 4, 1, 8), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._indentable_lns(1)
        ast.body[0].body[0].body[0].f._offset_cols(1, lns)
        self.assertEqual(set(), lns)
        self.assertEqual((2, 2, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 6, 4, 3), ast.body[0].body[0].body[0].value.f.loc)

    def test__offset_cols_mapped(self):
        src = 'i = 1\nj = 2\nk = 3\nl = \\\n4'
        ast = parse(src)
        off = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

        ast.f._offset_cols_mapped(off)
        self.assertEqual((0, 0, 4, 1), ast.f.loc)
        self.assertEqual((0, 0, 0, 5), ast.body[0].f.loc)
        self.assertEqual((0, 0, 0, 1), ast.body[0].targets[0].f.loc)
        self.assertEqual((0, 4, 0, 5), ast.body[0].value.f.loc)
        self.assertEqual((1, 1, 1, 6), ast.body[1].f.loc)
        self.assertEqual((1, 1, 1, 2), ast.body[1].targets[0].f.loc)
        self.assertEqual((1, 5, 1, 6), ast.body[1].value.f.loc)
        self.assertEqual((2, 2, 2, 7), ast.body[2].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[2].targets[0].f.loc)
        self.assertEqual((2, 6, 2, 7), ast.body[2].value.f.loc)
        self.assertEqual((3, 3, 4, 5), ast.body[3].f.loc)
        self.assertEqual((3, 3, 3, 4), ast.body[3].targets[0].f.loc)
        self.assertEqual((4, 4, 4, 5), ast.body[3].value.f.loc)

    def test__indent_tail(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._indent_tail('  ')
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n   if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._indent_tail('  ')
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._indent_tail('  ')
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._indent_tail('  ')
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n  =\\\n   2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.f._indent_tail('  ')
        self.assertEqual({1, 2}, lns)
        self.assertEqual('@decorator\n  class cls:\n   pass', ast.f.src)

    def test__dedent_tail(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._dedent_tail(' ')
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\nif True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._dedent_tail(' ')
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._dedent_tail(' ')
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._dedent_tail(' ')
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.body[0].body[0].f._dedent_tail(' ')
        self.assertEqual(set(), lns)
        self.assertEqual('@decorator\nclass cls:\n pass', ast.f.src)

        # ast = parse(src)
        # lns = ast.body[0].body[0].f._dedent_tail(' ', skip=0)
        # self.assertEqual({2}, lns)
        # self.assertEqual('@decorator\nclass cls:\npass', ast.f.src)

    def test_fix(self):
        f = FST.fromsrc('if 1:\n a\nelif 2:\n b')
        fc = f.a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual(fc.lines[0], 'elif 2:')
        fc.fix(inplace=True)
        self.assertEqual(fc.lines[0], 'if 2:')
        fc.verify(raise_=True)

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual(fc.src, '1 +\n2')
        fc.fix(inplace=True)
        self.assertEqual(fc.src, '(1 +\n2)')
        fc.verify(raise_=True)

        f = FST.fromsrc('i = 1')
        self.assertIs(f.a.body[0].targets[0].ctx.__class__, Store)
        fc = f.a.body[0].targets[0].f.copy(fix=False)
        self.assertIs(fc.a.ctx.__class__, Store)
        fc.fix(inplace=True)
        self.assertIs(fc.a.ctx.__class__, Load)
        fc.verify(raise_=True)

        f = FST.fromsrc('if 1: pass\nelif 2: pass').a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual('elif 2: pass', f.src)

        g = f.fix(inplace=False)
        self.assertIsNot(g, f)
        self.assertEqual('if 2: pass', g.src)
        self.assertEqual('elif 2: pass', f.src)

        g = f.fix(inplace=True)
        self.assertIs(g, f)
        self.assertEqual('if 2: pass', g.src)
        self.assertEqual('if 2: pass', f.src)

        f = FST.fromsrc('i, j = 1, 2').a.body[0].targets[0].f.copy(fix=False)
        self.assertEqual('i, j', f.src)
        self.assertIsNot(f, f.fix())

        g = f.fix(inplace=False)
        self.assertFalse(compare(f.a, g.a))
        self.assertIs(g, g.fix())

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(fix=False)
        self.assertEqual('w := x,', f.src)

        g = f.fix(inplace=False)
        self.assertEqual('(w := x,)', g.src)
        self.assertTrue(compare(f.a, g.a, locs=False))
        self.assertFalse(compare(f.a, g.a, locs=True))
        self.assertIs(g, g.fix())

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('1 +\n2', fc.src)
        fd = fc.fix()
        self.assertEqual('(1 +\n2)', fd.src)
        fc.fix(inplace=True)
        self.assertEqual('(1 +\n2)', fc.src)

        f = FST.fromsrc('yield a1, a2')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('yield a1, a2', fc.src)
        fd = fc.fix()
        self.assertEqual('(yield a1, a2)', fd.src)
        fc.fix(inplace=True)
        self.assertEqual('(yield a1, a2)', fc.src)

        f = FST.fromsrc("""[
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format
]""".strip())
        fc = f.a.body[0].value.elts[0].f.copy(fix=False)
        self.assertEqual("""
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format""".strip(), fc.src)
        fd = fc.fix()
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fd.src)
        fc.fix(inplace=True)
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fc.src)

        f = FST.fromsrc("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))
        """.strip())
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual("""
(is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute))""".strip(), fc.src)
        fd = fc.fix()
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fd.src)
        fc.fix(inplace=True)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fc.src)

        if sys.version_info[:2] >= (3, 12):
            fc = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(fix=False)
            self.assertEqual('*tuple[int, ...]', fc.src)
            fd = fc.fix()
            self.assertEqual('(*tuple[int, ...],)', fd.src)
            fc.fix(inplace=True)
            self.assertEqual('(*tuple[int, ...],)', fc.src)

    def test_copy_bulk(self):
        for fnm in PYFNMS:
            ast = FST.fromsrc(read(fnm)).a

            for a in walk(ast):
                if a.f.is_parsable():
                    f = a.f.copy(fix=True)
                    f.verify(raise_=True)

    def test_copy(self):
        f = FST.fromsrc('@decorator\nclass cls:\n  pass')
        self.assertEqual(f.a.body[0].f.copy(fix=False).src, '@decorator\nclass cls:\n  pass')
        self.assertEqual(f.a.body[0].f.copy(decorators=False, fix=False).src, 'class cls:\n  pass')

        l = FST.fromsrc("['\\u007f', '\\u0080', 'ʁ', 'ᛇ', '時', '🐍', '\\ud800', 'Źdźbło']").a.body[0].value.elts
        self.assertEqual("'\\u007f'", l[0].f.copy().src)
        self.assertEqual("'\\u0080'", l[1].f.copy().src)
        self.assertEqual("'ʁ'", l[2].f.copy().src)
        self.assertEqual("'ᛇ'", l[3].f.copy().src)
        self.assertEqual("'時'", l[4].f.copy().src)
        self.assertEqual("'🐍'", l[5].f.copy().src)
        self.assertEqual("'\\ud800'", l[6].f.copy().src)
        self.assertEqual("'Źdźbło'", l[7].f.copy().src)

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(fix=True)
        self.assertEqual('(w := x,)', f.src)

        f = FST.fromsrc('a[1:2, 3:4]').a.body[0].value.slice.f.copy(fix=False)
        self.assertIs(f.fix(), f)
        # self.assertRaises(SyntaxError, f.fix)
        # self.assertIs(None, f.fix(raise_=False))

        f = FST.fromsrc('''
if 1:
    def f():
        """
        docstring
        """
        """
        regular text
        """
          '''.strip())
        self.assertEqual('''
def f():
    """
    docstring
    """
    """
        regular text
        """
          '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    async def f():
        """
        docstring
        """
        """
        regular text
        """
          '''.strip())
        self.assertEqual('''
async def f():
    """
    docstring
    """
    """
        regular text
        """
          '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        docstring
        """
        """
        regular text
        """
          '''.strip())
        self.assertEqual('''
class cls:
    """
    docstring
    """
    """
        regular text
        """
          '''.strip(), f.a.body[0].body[0].f.copy().src)






        if sys.version_info[:2] >= (3, 12):
            f = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(fix=True)
            self.assertEqual('(*tuple[int, ...],)', f.src)

    def test_slice_stmt(self):
        self.assertEqual('\n'.join(parse("""
def f():
    i = 1
    j = 1
    k = 1
    l = 1
            """.strip()).body[0].f.slice(-2).dump(print=False)), """
Module .. ROOT 0,0 -> 1,5
  .body[2]
  0] Assign .. 0,0 -> 0,5
    .targets[1]
    0] Name .. 0,0 -> 0,1
      .id
        'k'
      .ctx
        Store
    .value
      Constant .. 0,4 -> 0,5
        .value
          1
        .kind
          None
    .type_comment
      None
  1] Assign .. 1,0 -> 1,5
    .targets[1]
    0] Name .. 1,0 -> 1,1
      .id
        'l'
      .ctx
        Store
    .value
      Constant .. 1,4 -> 1,5
        .value
          1
        .kind
          None
    .type_comment
      None
            """.strip())

        self.assertEqual('\n'.join(parse("""
try: pass
except ValueError: pass
except RuntimeError: pass
except IndexError: pass
except TypeError: pass
            """.strip()).body[0].f.slice(-1, field='handlers').dump(print=False)), """
Module .. ROOT 0,0 -> 0,22
  .body[1]
  0] ExceptHandler .. 0,0 -> 0,22
    .type
      Name .. 0,7 -> 0,16
        .id
          'TypeError'
        .ctx
          Load
    .name
      None
    .body[1]
    0] Pass .. 0,18 -> 0,22
            """.strip())

        self.assertEqual('\n'.join(parse("""
match a:
    case 1: pass
    case f: pass
    case None: pass
    case 3 | 4: pass
            """.strip()).body[0].f.slice(1, 3).dump(print=False)), """
Module .. ROOT 0,0 -> 1,15
  .body[2]
  0] match_case .. 0,0 -> 0,7
    .pattern
      MatchAs .. 0,0 -> 0,1
        .pattern
          None
        .name
          'f'
    .guard
      None
    .body[1]
    0] Pass .. 0,3 -> 0,7
  1] match_case .. 1,5 -> 1,15
    .pattern
      MatchSingleton .. 1,5 -> 1,9
        .value
          None
    .guard
      None
    .body[1]
    0] Pass .. 1,11 -> 1,15
            """.strip())


        dumptest(self, parse("""
if 1: pass
elif 2: pass
            """.strip()).body[0].f.slice(field='orelse'), """
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] If .. 0,0 -> 0,10
    .test
      Constant .. 0,3 -> 0,4
        .value
          2
        .kind
          None
    .body[1]
    0] Pass .. 0,6 -> 0,10
            """.strip(), 'if 2: pass')

        dumptest(self, parse("""
if 1: pass
else:
  if 2: pass
            """.strip()).body[0].f.slice(field='orelse'), """
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] If .. 0,0 -> 0,10
    .test
      Constant .. 0,3 -> 0,4
        .value
          2
        .kind
          None
    .body[1]
    0] Pass .. 0,6 -> 0,10
            """.strip(), 'if 2: pass')

    def test_slice_seq_expr_1(self):
        dumptest(self, parse("""
(1, 2, 3, 4)
            """.strip()).body[0].value.f.slice(1, 3), """
Expression .. ROOT 0,0 -> 0,6
  .body
    Tuple .. 0,0 -> 0,6
      .elts[2]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), '(2, 3)')

        dumptest(self, parse("""
(1, 2, 3, 4)
            """.strip()).body[0].value.f.slice(-1), """
Expression .. ROOT 0,0 -> 0,4
  .body
    Tuple .. 0,0 -> 0,4
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          4
        .kind
          None
      .ctx
        Load
            """.strip(), '(4,)')

        dumptest(self, parse("""
(1, 2, 3, 4)
            """.strip()).body[0].value.f.slice(), """
Expression .. ROOT 0,0 -> 0,12
  .body
    Tuple .. 0,0 -> 0,12
      .elts[4]
      0] Constant .. 0,1 -> 0,2
        .value
          1
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          2
        .kind
          None
      2] Constant .. 0,7 -> 0,8
        .value
          3
        .kind
          None
      3] Constant .. 0,10 -> 0,11
        .value
          4
        .kind
          None
      .ctx
        Load
            """.strip(), '(1, 2, 3, 4)')

        dumptest(self, parse("""
(1, 2, 3, 4)
            """.strip()).body[0].value.f.slice(1, 1), """
Expression .. ROOT 0,0 -> 0,2
  .body
    Tuple .. 0,0 -> 0,2
      .ctx
        Load

            """.strip(), '()')

        dumptest(self, parse("""
[1, 2, 3, 4]
            """.strip()).body[0].value.f.slice(1, 3), """
Expression .. ROOT 0,0 -> 0,6
  .body
    List .. 0,0 -> 0,6
      .elts[2]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), '[2, 3]')

        dumptest(self, parse("""
[1, 2, 3, 4]
            """.strip()).body[0].value.f.slice(-1), """
Expression .. ROOT 0,0 -> 0,3
  .body
    List .. 0,0 -> 0,3
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          4
        .kind
          None
      .ctx
        Load
            """.strip(), '[4]')

        dumptest(self, parse("""
[1, 2, 3, 4]
            """.strip()).body[0].value.f.slice(), """
Expression .. ROOT 0,0 -> 0,12
  .body
    List .. 0,0 -> 0,12
      .elts[4]
      0] Constant .. 0,1 -> 0,2
        .value
          1
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          2
        .kind
          None
      2] Constant .. 0,7 -> 0,8
        .value
          3
        .kind
          None
      3] Constant .. 0,10 -> 0,11
        .value
          4
        .kind
          None
      .ctx
        Load
            """.strip(), '[1, 2, 3, 4]')

        dumptest(self, parse("""
[1, 2, 3, 4]
            """.strip()).body[0].value.f.slice(1, 1), """
Expression .. ROOT 0,0 -> 0,2
  .body
    List .. 0,0 -> 0,2
      .ctx
        Load
            """.strip(), '[]')

        dumptest(self, parse("""
{1, 2, 3, 4}
            """.strip()).body[0].value.f.slice(1, 3), """
Expression .. ROOT 0,0 -> 0,6
  .body
    Set .. 0,0 -> 0,6
      .elts[2]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          3
        .kind
          None
            """.strip(), '{2, 3}')

        dumptest(self, parse("""
{1, 2, 3, 4}
            """.strip()).body[0].value.f.slice(-1), """
Expression .. ROOT 0,0 -> 0,3
  .body
    Set .. 0,0 -> 0,3
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          4
        .kind
          None
            """.strip(), '{4}')

        dumptest(self, parse("""
{1, 2, 3, 4}
            """.strip()).body[0].value.f.slice(), """
Expression .. ROOT 0,0 -> 0,12
  .body
    Set .. 0,0 -> 0,12
      .elts[4]
      0] Constant .. 0,1 -> 0,2
        .value
          1
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          2
        .kind
          None
      2] Constant .. 0,7 -> 0,8
        .value
          3
        .kind
          None
      3] Constant .. 0,10 -> 0,11
        .value
          4
        .kind
          None
            """.strip(), '{1, 2, 3, 4}')

        dumptest(self, parse("""
{1, 2, 3, 4}
            """.strip()).body[0].value.f.slice(1, 1), """
Expression .. ROOT 0,0 -> 0,5
  .body
    Call .. 0,0 -> 0,5
      .func
        Name .. 0,0 -> 0,3
          .id
            'set'
          .ctx
            Load
            """.strip(), 'set()')

        dumptest(self, parse("""

(1, 2, 3, 4)
            """.strip()).body[0].value.f.slice(1, 3), """
Expression .. ROOT 0,0 -> 0,6
  .body
    Tuple .. 0,0 -> 0,6
      .elts[2]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), '(2, 3)')

        dumptest(self, parse("""
{1: 2, 3: 4, 5: 6, 7: 8}
            """.strip()).body[0].value.f.slice(1, 3), """
Expression .. ROOT 0,0 -> 0,12
  .body
    Dict .. 0,0 -> 0,12
      .keys[2]
      0] Constant .. 0,1 -> 0,2
        .value
          3
        .kind
          None
      1] Constant .. 0,7 -> 0,8
        .value
          5
        .kind
          None
      .values[2]
      0] Constant .. 0,4 -> 0,5
        .value
          4
        .kind
          None
      1] Constant .. 0,10 -> 0,11
        .value
          6
        .kind
          None
            """.strip(), '{3: 4, 5: 6}')

        dumptest(self, parse("""
{1: 2, 3: 4, 5: 6, 7: 8}
            """.strip()).body[0].value.f.slice(-1), """
Expression .. ROOT 0,0 -> 0,6
  .body
    Dict .. 0,0 -> 0,6
      .keys[1]
      0] Constant .. 0,1 -> 0,2
        .value
          7
        .kind
          None
      .values[1]
      0] Constant .. 0,4 -> 0,5
        .value
          8
        .kind
          None
            """.strip(), '{7: 8}')

        dumptest(self, parse("""
{1: 2, 3: 4, 5: 6, 7: 8}
            """.strip()).body[0].value.f.slice(), """
Expression .. ROOT 0,0 -> 0,24
  .body
    Dict .. 0,0 -> 0,24
      .keys[4]
      0] Constant .. 0,1 -> 0,2
        .value
          1
        .kind
          None
      1] Constant .. 0,7 -> 0,8
        .value
          3
        .kind
          None
      2] Constant .. 0,13 -> 0,14
        .value
          5
        .kind
          None
      3] Constant .. 0,19 -> 0,20
        .value
          7
        .kind
          None
      .values[4]
      0] Constant .. 0,4 -> 0,5
        .value
          2
        .kind
          None
      1] Constant .. 0,10 -> 0,11
        .value
          4
        .kind
          None
      2] Constant .. 0,16 -> 0,17
        .value
          6
        .kind
          None
      3] Constant .. 0,22 -> 0,23
        .value
          8
        .kind
          None
            """.strip(), '{1: 2, 3: 4, 5: 6, 7: 8}')

        dumptest(self, parse("""
{1: 2, 3: 4, 5: 6, 7: 8}
            """.strip()).body[0].value.f.slice(1, 1), """
Expression .. ROOT 0,0 -> 0,2
  .body
    Dict .. 0,0 -> 0,2
            """.strip(), '{}')

    def test_slice_seq_expr_2(self):
        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)           """.strip()).body[0].value.f.slice(), """
Expression .. ROOT 0,0 -> 4,1
  .body
    Tuple .. 0,0 -> 4,1
      .elts[3]
      0] Constant .. 1,4 -> 1,5
        .value
          1
        .kind
          None
      1] Constant .. 2,4 -> 2,5
        .value
          2
        .kind
          None
      2] Constant .. 3,4 -> 3,5
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), """
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.slice(0, 2), """
Expression .. ROOT 0,0 -> 3,1
  .body
    Tuple .. 0,0 -> 3,1
      .elts[2]
      0] Constant .. 1,4 -> 1,5
        .value
          1
        .kind
          None
      1] Constant .. 2,4 -> 2,5
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(       # hello
    1,  # first line
    2,  # second line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.slice(1, 2), """
Expression .. ROOT 0,0 -> 2,1
  .body
    Tuple .. 0,0 -> 2,1
      .elts[1]
      0] Constant .. 1,4 -> 1,5
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(
    2,  # second line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.slice(2), """
Expression .. ROOT 0,0 -> 2,1
  .body
    Tuple .. 0,0 -> 2,1
      .elts[1]
      0] Constant .. 1,4 -> 1,5
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), """
(
    3,  # third line
)
            """.strip())

        dumptest(self, parse("""
(           # hello
    1, 2, 3 # last line
)
            """.strip()).body[0].value.f.slice(), """
Expression .. ROOT 0,0 -> 2,1
  .body
    Tuple .. 0,0 -> 2,1
      .elts[3]
      0] Constant .. 1,4 -> 1,5
        .value
          1
        .kind
          None
      1] Constant .. 1,7 -> 1,8
        .value
          2
        .kind
          None
      2] Constant .. 1,10 -> 1,11
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), """
(           # hello
    1, 2, 3 # last line
)
            """.strip())

        dumptest(self, parse("""
(           # hello
    1, 2, 3 # last line
)
            """.strip()).body[0].value.f.slice(0, 2), """
Expression .. ROOT 0,0 -> 1,9
  .body
    Tuple .. 0,0 -> 1,9
      .elts[2]
      0] Constant .. 1,4 -> 1,5
        .value
          1
        .kind
          None
      1] Constant .. 1,7 -> 1,8
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(           # hello
    1, 2)
            """.strip())

        dumptest(self, parse("""
(           # hello
    1, 2, 3 # last line
)
            """.strip()).body[0].value.f.slice(1, 2), """
Expression .. ROOT 0,0 -> 0,4
  .body
    Tuple .. 0,0 -> 0,4
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(2,)
            """.strip())

        dumptest(self, parse("""
(           # hello
    1, 2, 3 # last line
)
            """.strip()).body[0].value.f.slice(2), """
Expression .. ROOT 0,0 -> 1,1
  .body
    Tuple .. 0,0 -> 1,1
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), """
(3, # last line
)
            """.strip())

    def test_slice_seq_expr_3(self):
        dumptest(self, parse("""
1, 2, 3, 4
            """.strip()).body[0].value.f.slice(1, 3), """
Expression .. ROOT 0,0 -> 0,6
  .body
    Tuple .. 0,0 -> 0,6
      .elts[2]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), """
(2, 3)
            """.strip())

        dumptest(self, parse("""
1, 2, 3, 4
            """.strip()).body[0].value.f.slice(-1), """
Expression .. ROOT 0,0 -> 0,4
  .body
    Tuple .. 0,0 -> 0,4
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          4
        .kind
          None
      .ctx
        Load
            """.strip(), """
(4,)
            """.strip())

        dumptest(self, parse("""
1, 2, 3, 4
            """.strip()).body[0].value.f.slice(), """
Expression .. ROOT 0,0 -> 0,12
  .body
    Tuple .. 0,0 -> 0,12
      .elts[4]
      0] Constant .. 0,1 -> 0,2
        .value
          1
        .kind
          None
      1] Constant .. 0,4 -> 0,5
        .value
          2
        .kind
          None
      2] Constant .. 0,7 -> 0,8
        .value
          3
        .kind
          None
      3] Constant .. 0,10 -> 0,11
        .value
          4
        .kind
          None
      .ctx
        Load
            """.strip(), """
(1, 2, 3, 4)
            """.strip())

        dumptest(self, parse("""
1, 2, 3, 4
            """.strip()).body[0].value.f.slice(1, 1), """
Expression .. ROOT 0,0 -> 0,2
  .body
    Tuple .. 0,0 -> 0,2
      .ctx
        Load
            """.strip(), """
()
            """.strip())

    def test_slice_seq_expr_4(self):
        dumptest(self, parse("""
(1, 2
  ,  # comment
3, 4)
            """.strip()).body[0].value.f.slice(1, 2), """
Expression .. ROOT 0,0 -> 2,1
  .body
    Tuple .. 0,0 -> 2,1
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(2
  ,  # comment
)
            """.strip())

        dumptest(self, parse("""
(1, 2
  ,
3, 4)
            """.strip()).body[0].value.f.slice(1, 2), """
Expression .. ROOT 0,0 -> 2,1
  .body
    Tuple .. 0,0 -> 2,1
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(2
  ,
)
            """.strip())

        dumptest(self, parse("""
(1, 2
  , 3, 4)
            """.strip()).body[0].value.f.slice(1, 2), """
Expression .. ROOT 0,0 -> 1,4
  .body
    Tuple .. 0,0 -> 1,4
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(2
  ,)
            """.strip())

        dumptest(self, parse("""
(1, 2  # comment
  , 3, 4)
            """.strip()).body[0].value.f.slice(1, 2), """
Expression .. ROOT 0,0 -> 1,4
  .body
    Tuple .. 0,0 -> 1,4
      .elts[1]
      0] Constant .. 0,1 -> 0,2
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(2  # comment
  ,)
            """.strip())

    def test_slice_seq_expr_5(self):
        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.slice(), """
Expression .. ROOT 0,0 -> 4,1
  .body
    Tuple .. 0,0 -> 4,1
      .elts[3]
      0] Constant .. 1,4 -> 1,5
        .value
          1
        .kind
          None
      1] Constant .. 2,4 -> 2,5
        .value
          2
        .kind
          None
      2] Constant .. 3,4 -> 3,5
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), """
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.slice(0, 2), """
Expression .. ROOT 0,0 -> 3,1
  .body
    Tuple .. 0,0 -> 3,1
      .elts[2]
      0] Constant .. 1,4 -> 1,5
        .value
          1
        .kind
          None
      1] Constant .. 2,4 -> 2,5
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(       # hello
    1,  # first line
    2,  # second line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.slice(1, 2), """
Expression .. ROOT 0,0 -> 2,1
  .body
    Tuple .. 0,0 -> 2,1
      .elts[1]
      0] Constant .. 1,4 -> 1,5
        .value
          2
        .kind
          None
      .ctx
        Load
            """.strip(), """
(
    2,  # second line
)
            """.strip())

        dumptest(self, parse("""
(       # hello
    1,  # first line
    2,  # second line
    3,  # third line
)
            """.strip()).body[0].value.f.slice(2), """
Expression .. ROOT 0,0 -> 2,1
  .body
    Tuple .. 0,0 -> 2,1
      .elts[1]
      0] Constant .. 1,4 -> 1,5
        .value
          3
        .kind
          None
      .ctx
        Load
            """.strip(), """
(
    3,  # third line
)
            """.strip())






















        # dumptest(self, parse("""
        #     """.strip()).body[0].value.f.slice(0, 2), """
        #     """.strip(), """
        #     """.strip())

    def test_cut(self):
        for src, elt, start, stop, cut_src, cut_slice in CUT_DATA:
            src  = src.strip()
            t    = parse(src)
            f    = eval(f't.{elt}', {'t': t}).f
            s    = f.slice(start, stop, cut=True)
            tsrc = t.f.src
            ssrc = s.src

            self.assertEqual(tsrc, cut_src.strip())
            self.assertEqual(ssrc, cut_slice.strip())













def regen_cut_data():
    newlines = []

    for src, elt, start, stop, *_ in CUT_DATA:
        src  = src.strip()
        t    = parse(src)
        f    = eval(f't.{elt}', {'t': t}).f
        s    = f.slice(start, stop, cut=True)
        tsrc = t.f.src
        ssrc = s.src

        assert not tsrc.startswith('\n') or tsrc.endswith('\n')
        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        newlines.extend(f'''("""\n{src}\n""", {elt!r}, {start}, {stop}, """\n{tsrc}\n""", """\n{ssrc}\n"""),\n'''.split('\n'))

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('CUT_DATA = [')
    stop  = lines.index(']  # END OF CUT_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='python -m fst')

    parser.add_argument('--regen', default=False, action='store_true',
                        help="regenerate stuff")

    args = parser.parse_args()

    if args.regen:
        regen_cut_data()
        sys.exit(0)

    unittest.main()
