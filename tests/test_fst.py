#!/usr/bin/env python

import ast
import builtins
import os
import threading
import tokenize
import unittest
from ast import parse as ast_parse, unparse as ast_unparse
from io import StringIO
from itertools import combinations
from pprint import pformat
from random import randint, seed

from fst import *
import fst

from fst.asttypes import (
    _ExceptHandlers,
    _match_cases,
    _Assign_targets,
    _decorator_list,
    _comprehensions,
    _comprehension_ifs,
    _aliases,
    _withitems,
    _type_params,
)

from fst.astutil import (
    WalkFail,
    copy_ast,
    compare_asts,
)

from fst.common import PYVER, PYLT11, PYLT12, PYLT13, PYLT14, PYGE11, PYGE12, PYGE13, PYGE14, PYGE15, astfield, fstloc
from fst.code import *
from fst.view import fstview, fstview_dummy

from test_parse import PARSE_TESTS
from data.data_other import PARS_DATA, PUT_SRC_REPARSE_DATA, PRECEDENCE_DATA


DIR_NAME = os.path.dirname(__file__)

ASTSTMT = lambda src: parse(src).body[0].f.copy()
ASTEXPR = lambda src: parse(src).f

PRECEDENCE_DST_STMTS = [
    (ASTSTMT('x'), 'value'),  # when able to replace in non-mod roots then can use this
    (ASTSTMT('x = y'), 'targets[0]'),
    (ASTSTMT('for x in y:\n    pass'), 'target'),
    (ASTSTMT('async for x in y:\n    pass'), 'target'),
]

PRECEDENCE_DST_EXPRS = [
    (ASTEXPR('(x,)'), 'elts[0]'),
    (ASTEXPR('[x]'), 'elts[0]'),
    (ASTEXPR('[*x]'), 'elts[0].value'),
    (ASTEXPR('{k: v}'), 'keys[0]'),
    (ASTEXPR('{k: v}'), 'values[0]'),
    (ASTEXPR('{**x}'), 'values[0]'),
    (ASTEXPR("f'{x}'"), 'values[0].value'),
    (ASTEXPR('x.y'), 'value'),
    (ASTEXPR('x[y]'), 'value'),
    (ASTEXPR('x[y]'), 'slice'),
    (ASTEXPR('call(a)'), 'args[0]'),
    (ASTEXPR('call(**a)'), 'keywords[0].value'),
]

PRECEDENCE_SRC_EXPRS = [
    (ASTEXPR('z'),),
    (ASTEXPR('x, y'), 'elts[0]'),
    (ASTEXPR('[x, y]'), 'elts[0]'),
    (ASTEXPR('(x := y)'), 'target', 'value'),
    (ASTEXPR('lambda: x'), 'body'),
    (ASTEXPR('x if y else z'), 'body', 'test', 'orelse'),
    (ASTEXPR('await x'), 'value'),
    (ASTEXPR('yield x'), 'value'),
    (ASTEXPR('yield from x'), 'value'),
    (ASTEXPR('x < y'), 'left', 'comparators[0]'),
    (ASTEXPR('x and y'), 'values[0]'),
    (ASTEXPR('x or y'), 'values[0]'),
    (ASTEXPR('~x'), 'operand'),
    (ASTEXPR('not x'), 'operand'),
    (ASTEXPR('+x'), 'operand'),
    (ASTEXPR('-x'), 'operand'),
    (ASTEXPR('x + y'), 'left', 'right'),
    (ASTEXPR('x - y'), 'left', 'right'),
    (ASTEXPR('x * y'), 'left', 'right'),
    (ASTEXPR('x @ y'), 'left', 'right'),
    (ASTEXPR('x / y'), 'left', 'right'),
    (ASTEXPR('x % y'), 'left', 'right'),
    (ASTEXPR('x << y'), 'left', 'right'),
    (ASTEXPR('x >> y'), 'left', 'right'),
    (ASTEXPR('x | y'), 'left', 'right'),
    (ASTEXPR('x ^ y'), 'left', 'right'),
    (ASTEXPR('x & y'), 'left', 'right'),
    (ASTEXPR('x // y'), 'left', 'right'),
    (ASTEXPR('x ** y'), 'left', 'right'),
]


INDIVIDUAL_NODES = [
    ('', 'Module'),
    ('a', 'Interactive'),
    ('v', 'Expression'),
    ('def f(): pass', 'FunctionDef'),
    ('async def f(): pass', 'AsyncFunctionDef'),
    ('class cls: pass', 'ClassDef'),
    ('return', 'Return'),
    ('del a', 'Delete'),
    ('a = b', 'Assign'),
    ('a += b', 'AugAssign'),
    ('a: b', 'AnnAssign'),
    ('for _ in _: pass', 'For'),
    ('async for _ in _: pass', 'AsyncFor'),
    ('while _: pass', 'While'),
    ('if _: pass', 'If'),
    ('with _: pass', 'With'),
    ('async with _: pass', 'AsyncWith'),
    ('match _:\n  case _: pass', 'Match'),
    ('raise', 'Raise'),
    ('try: pass\nexcept: pass', 'Try'),
    ('assert v', 'Assert'),
    ('import m', 'Import'),
    ('from . import a', 'ImportFrom'),
    ('global n', 'Global'),
    ('nonlocal n', 'Nonlocal'),
    ('a', 'Expr'),
    ('pass', 'Pass'),
    ('break', 'Break'),
    ('continue', 'Continue'),
    ('a or b', 'BoolOp'),
    ('a := b', 'NamedExpr'),
    ('a + b', 'BinOp'),
    ('-a', 'UnaryOp'),
    ('lambda: None', 'Lambda'),
    ('a if b else c', 'IfExp'),
    ('{a: b}', 'Dict'),
    ('{a}', 'Set'),
    ('[_ for _ in _]', 'ListComp'),
    ('{_ for _ in _}', 'SetComp'),
    ('{_: _ for _ in _}', 'DictComp'),
    ('(_ for _ in _)', 'GeneratorExp'),
    ('await _', 'Await'),
    ('yield _', 'Yield'),
    ('yield from _', 'YieldFrom'),
    ('a < b', 'Compare'),
    ('f()', 'Call'),
    # ('zzz', 'FormattedValue'),
    # ('zzz', 'Interpolation'),
    ('f"{1}"', 'JoinedStr'),
    ('1', 'Constant'),
    ('a.b', 'Attribute'),
    ('a[b]', 'Subscript'),
    ('*s', 'Starred'),
    ('n', 'Name'),
    ('[a]', 'List'),
    ('(a,)', 'Tuple'),
    ('a:b:c', 'Slice'),
    ('', 'Load'),
    ('', 'Store'),
    ('', 'Del'),
    ('and', 'And'),
    ('or', 'Or'),
    ('+', 'Add'),
    ('-', 'Sub'),
    ('*', 'Mult'),
    ('@', 'MatMult'),
    ('/', 'Div'),
    ('%', 'Mod'),
    ('**', 'Pow'),
    ('<<', 'LShift'),
    ('>>', 'RShift'),
    ('|', 'BitOr'),
    ('^', 'BitXor'),
    ('&', 'BitAnd'),
    ('//', 'FloorDiv'),
    ('~', 'Invert'),
    ('not', 'Not'),
    ('+', 'UAdd'),
    ('-', 'USub'),
    ('==', 'Eq'),
    ('!=', 'NotEq'),
    ('<', 'Lt'),
    ('<=', 'LtE'),
    ('>', 'Gt'),
    ('>=', 'GtE'),
    ('is', 'Is'),
    ('is not', 'IsNot'),
    ('in', 'In'),
    ('not in', 'NotIn'),
    ('for _ in _', 'comprehension'),
    ('except: pass', 'ExceptHandler'),
    ('a', 'arguments'),
    ('a', 'arg'),
    ('k=v', 'keyword'),
    ('a', 'alias'),
    ('w', 'withitem'),
    ('case _: pass', 'match_case'),
    ('1', 'MatchValue'),
    ('None', 'MatchSingleton'),
    ('[p]', 'MatchSequence'),
    ('{1: p}', 'MatchMapping'),
    ('cls()', 'MatchClass'),
    ('*s', 'MatchStar'),
    ('p', 'MatchAs'),
    ('a | b', 'MatchOr'),
    ('', '_ExceptHandlers'),
    ('', '_match_cases'),
    ('', '_Assign_targets'),
    ('', '_decorator_list'),
    ('', '_comprehensions'),
    ('', '_comprehension_ifs'),
    ('', '_aliases'),
    ('', '_withitems'),
]

if PYGE11:
    INDIVIDUAL_NODES.extend([
        ('try: pass\nexcept* Exception: pass', 'TryStar'),
        ('except* Exception: pass', 'ExceptHandler'),
    ])

if PYGE12:
    INDIVIDUAL_NODES.extend([
        ('type t[T] = ...', 'TypeAlias'),
        ('T', 'TypeVar'),
        ('**V', 'ParamSpec'),
        ('*U', 'TypeVarTuple'),
        ('', '_type_params'),
    ])

if PYGE14:
    INDIVIDUAL_NODES.extend([
        ('t"{1}"', 'TemplateStr'),
    ])


def read(fnm):
    with open(fnm) as f:
        return f.read()


def regen_pars_data():
    newlines = []

    for src, elt, *_ in PARS_DATA:
        src   = src.strip()
        t     = parse(src)
        f     = eval(f't.{elt}', {'t': t}).f
        l     = f.pars()
        ssrc  = f._get_src(*l)

        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        newlines.append('(r"""')
        newlines.extend(f'''{src}\n""", {elt!r}, r"""\n{ssrc}\n"""),\n'''.split('\n'))

    fnm = os.path.join(DIR_NAME, 'data/data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PARS_DATA = [')
    stop  = lines.index(']  # END OF PARS_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_src():
    newlines = []

    for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_SRC_REPARSE_DATA):
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            eln, ecol = f.put_src(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root
            g = f.root.find_loc(ln, col, eln, ecol)

            tdst  = f.root.src
            tdump = f.root.dump(out='lines')

            f.root.verify(raise_=True)

            newlines.extend(f'''(r"""{dst}""", {attr!r}, ({ln}, {col}, {end_ln}, {end_col}), {options!r}, r"""{src}""", r"""{g.src}""", r"""{tdst}""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('"""),\n')

        except Exception:
            print(i, attr, (ln, col, end_ln, end_col), src, options)
            print('---')
            print(repr(dst))
            print('...')
            print(src)
            print('...')
            print(put_src)

            raise

    fnm = os.path.join(DIR_NAME, 'data/data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SRC_REPARSE_DATA = [')
    stop  = lines.index(']  # END OF PUT_SRC_REPARSE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_precedence_data():
    newlines = []

    for dst, *attrs in PRECEDENCE_DST_STMTS + PRECEDENCE_DST_EXPRS + PRECEDENCE_SRC_EXPRS:
        for src, *_ in PRECEDENCE_SRC_EXPRS:
            for attr in attrs:
                d       = dst.copy()
                s       = src.body[0].value.copy()
                is_stmt = isinstance(d.a, stmt)
                f       = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})

                # # put python precedence

                # is_unpar_tup = False if is_stmt else (d.body[0].value.is_parenthesized_tuple() is False)

                # f.pfield.set(f.parent.a, s.a)

                # truth = ast_unparse(f.root.a)

                # if is_unpar_tup:
                #     truth = truth[1:-1]

                # newlines.append(f'    {truth!r},')

                # put our precedence

                d            = dst.copy()
                s            = src.body[0].value.copy()
                is_stmt      = isinstance(d.a, stmt)
                f            = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})

                try:
                    f.parent.put(s, f.pfield.idx, f.pfield.name)
                except Exception as exc:
                    truth = str(exc)

                else:
                    f.root.verify()

                    truth = f.root.src

                newlines.append(f'    {truth!r},')

    fnm = os.path.join(DIR_NAME, 'data/data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PRECEDENCE_DATA = [')
    stop  = lines.index(']  # END OF PRECEDENCE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


class TestFST(unittest.TestCase):
    """Main fst module, `FST` class and core functions."""

    maxDiff = None

    def test_fst_unparse(self):
        a = fst.parse('if 1: pass')

        self.assertEqual('if 1: pass', fst.unparse(a))
        self.assertEqual('if 1:\n    pass', ast.unparse(a))
        self.assertEqual('if 1:\n    pass', ast.unparse(a.f.copy_ast()))

        self.assertEqual('if 1: pass', fst.unparse(a.body[0]))
        self.assertEqual('if 1:\n    pass', ast.unparse(a.body[0]))
        self.assertEqual('if 1:\n    pass', ast.unparse(a.body[0].f.copy_ast()))

        self.assertEqual('pass', fst.unparse(a.body[0].body[0]))
        self.assertEqual('pass', ast.unparse(a.body[0].body[0]))
        self.assertEqual('pass', ast.unparse(a.body[0].body[0].f.copy_ast()))

        a.f._lines = None

        self.assertEqual('if 1:\n    pass', fst.unparse(a))

        a = fst.parse('if 1:\n  if 2: pass')

        self.assertEqual('if 1:\n  if 2: pass', fst.unparse(a))
        self.assertEqual('if 1:\n    if 2:\n        pass', ast.unparse(a))
        self.assertEqual('if 1:\n    if 2:\n        pass', ast.unparse(a.f.copy_ast()))

        self.assertEqual('if 1:\n  if 2: pass', fst.unparse(a.body[0]))
        self.assertEqual('if 1:\n    if 2:\n        pass', ast.unparse(a.body[0]))
        self.assertEqual('if 1:\n    if 2:\n        pass', ast.unparse(a.body[0].f.copy_ast()))

        self.assertEqual('if 2: pass', fst.unparse(a.body[0].body[0]))
        self.assertEqual('if 2:\n    pass', ast.unparse(a.body[0].body[0]))
        self.assertEqual('if 2:\n    pass', ast.unparse(a.body[0].body[0].f.copy_ast()))

    def test__sanitize_stmtlike(self):
        f = FST('# pre\ni = j  # line\n# post', 'stmt')
        self.assertEqual('# pre\ni = j  # line\n# post', f.src)
        self.assertEqual('i = j', f._sanitize().src)

        f = FST('# pre\nexcept:\n  pass  # line\n# post', 'ExceptHandler')
        self.assertEqual('# pre\nexcept:\n  pass  # line\n# post', f.src)
        self.assertEqual('except:\n  pass  # line', f._sanitize().src)

        f = FST('# pre\nexcept: pass  # line\n# post', 'ExceptHandler')
        self.assertEqual('# pre\nexcept: pass  # line\n# post', f.src)
        self.assertEqual('except: pass  # line', f._sanitize().src)

        f = FST('# pre\ncase None:\n  pass  # line\n# post', 'match_case')
        self.assertEqual('# pre\ncase None:\n  pass  # line\n# post', f.src)
        self.assertEqual('case None:\n  pass  # line', f._sanitize().src)

        f = FST('# pre\ncase None: pass  # line\n# post', 'match_case')
        self.assertEqual('# pre\ncase None: pass  # line\n# post', f.src)
        self.assertEqual('case None: pass  # line', f._sanitize().src)

    def test__sanitize(self):
        f = FST('#0\n ( a ) #1\n#2')._sanitize()
        self.assertEqual('( a )', f.src)
        f.verify()

    def test__is_atom(self):
        self.assertIs(False, parse('1 + 2').body[0].value.f._is_atom())
        self.assertEqual('unenclosable', parse('f()').body[0].value.f._is_atom())
        self.assertEqual('pars', parse('(1 + 2)').body[0].value.f._is_atom())
        self.assertIs(False, parse('(1 + 2)').body[0].value.f._is_atom(pars=False))

        self.assertIs(False, parse('1, 2').body[0].value.f._is_atom())
        self.assertIs(True, parse('(1, 2)').body[0].value.f._is_atom())
        self.assertIs(True, parse('[1, 2]').body[0].value.f._is_atom())

        self.assertIs(False, parse('match a:\n case 1, 2: pass').body[0].cases[0].pattern.f._is_atom())
        self.assertIs(True, parse('match a:\n case (1, 2): pass').body[0].cases[0].pattern.f._is_atom())
        self.assertIs(True, parse('match a:\n case [1, 2]: pass').body[0].cases[0].pattern.f._is_atom())

        self.assertIs(False, FST('*a')._is_atom())  # because of `*a or b`

        self.assertEqual('unenclosable', FST('for i in j', 'comprehension')._is_atom())
        self.assertEqual('unenclosable', FST('', 'arguments')._is_atom())
        self.assertEqual('unenclosable', FST('a', 'arg')._is_atom())
        self.assertEqual('unenclosable', FST('a=b', 'keyword')._is_atom())
        self.assertEqual('unenclosable', FST('a as b', 'alias')._is_atom())
        self.assertEqual('unenclosable', FST('a as b', 'withitem')._is_atom())
        self.assertEqual('unenclosable', FST('is not', 'cmpop')._is_atom())
        self.assertEqual('unenclosable', FST('not in', 'cmpop')._is_atom())
        self.assertEqual('unenclosable', FST('"a"', 'Constant')._is_atom())
        self.assertEqual(True, FST('1', 'Constant')._is_atom())

        if PYGE12:
            self.assertEqual('unenclosable', FST('T', 'TypeVar')._is_atom())
            self.assertEqual('unenclosable', FST('*U', 'TypeVarTuple')._is_atom())
            self.assertEqual('unenclosable', FST('**V', 'ParamSpec')._is_atom())

        self.assertIs(False, FST('for i in j', 'comprehension')._is_atom(always_enclosed=True))
        self.assertIs(False, FST('', 'arguments')._is_atom(always_enclosed=True))
        self.assertIs(False, FST('a', 'arg')._is_atom(always_enclosed=True))
        self.assertIs(False, FST('a=b', 'keyword')._is_atom(always_enclosed=True))
        self.assertIs(False, FST('a as b', 'alias')._is_atom(always_enclosed=True))
        self.assertIs(False, FST('a as b', 'withitem')._is_atom(always_enclosed=True))
        self.assertIs(False, FST('is not', 'cmpop')._is_atom(always_enclosed=True))
        self.assertIs(False, FST('not in', 'cmpop')._is_atom(always_enclosed=True))
        self.assertIs(False, FST('"a"', 'Constant')._is_atom(always_enclosed=True))
        self.assertIs(True, FST('1', 'Constant')._is_atom(always_enclosed=True))

        if PYGE12:
            self.assertIs(False, FST('T', 'TypeVar')._is_atom(always_enclosed=True))
            self.assertIs(False, FST('*U', 'TypeVarTuple')._is_atom(always_enclosed=True))
            self.assertIs(False, FST('**V', 'ParamSpec')._is_atom(always_enclosed=True))

        self.assertIs(True, FST('<', 'cmpop')._is_atom())

    def test__is_enclosed_or_line_special(self):
        # Call
        # JoinedStr
        # TemplateStr
        # Constant - str
        # Attribute
        # Subscript
        # MatchClass
        # MatchStar
        # MatchAs
        # cmpop
        # comprehension
        # arguments
        # arg
        # alias
        # withitem

        self.assertTrue(FST('f(a, b=1)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('f\\\n(a, b=1)', 'exec').body[0].copy(pars=False).value._is_enclosed_or_line())
        self.assertTrue(FST('(f\\\n(a, b=1))', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(f\n(a, b=1))', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(f(\na\n,\nb\n=\n1))', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(f(\na\n,\nb\n=\n"()"))', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        if PYGE12:
            self.assertTrue(FST(r'''
(f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
            self.assertFalse(FST(r'''
(f"a{(1,

2)}b" f"""{3}

{4}
{5}"""
f"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

            self.assertTrue(FST(r'''
(f"a" f"""c
b""" f"d\
\
e")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

            self.assertFalse(FST(r'''
(f"a" f"""c
b"""

f"d\
\
e")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a.b', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\n.\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n.\\\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a[b]', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\n[\nb\n])', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\n[(\nb\n)])', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n[(\nb\n)])', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n[\\\nb\\\n])', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case f(a, b=1): pass', 'exec').body[0].cases[0].pattern._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case f\\\n(a, b=1): pass', 'exec').body[0].cases[0].pattern._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f\\\n(a, b=1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (f\n(a, b=1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f(\na\n,\nb\n=\n1)): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (f(\na\n,\nb\n=\n"()")): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case *s,: pass', 'exec').body[0].cases[0].pattern.patterns[0]._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (*\ns,): pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case *\\\ns,: pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (*\\\ns,): pass', 'exec').body[0].cases[0].pattern.patterns[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('match a:\n case a as b: pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a as b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\nas b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a\\\nas b): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\\\nas\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('match a:\n case (a\\\nas\\\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('match a:\n case (a\\\nas\n\\\nb): pass', 'exec').body[0].cases[0].pattern.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a not in b', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a not in b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a not\nin b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a not\\\nin b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a is\nnot b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a is\\\nnot b)', 'exec').body[0].value.ops[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('[i for\n i in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('[i for i\n in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('[i for i in\n j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('[i for\\\n i in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('[i for i\\\n in j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('[i for i in\\\n j]', 'exec').body[0].value.generators[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('def f(a, b=1): pass', 'exec').body[0].args.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('def f(a,\n b=1): pass', 'exec').body[0].args.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('def f(a,\\\n b=1): pass', 'exec').body[0].args.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('def f(a, b=(1,\n2)): pass', 'exec').body[0].args.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('def f(a:\n int): pass', 'exec').body[0].args.args[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('def f(a:\\\n int): pass', 'exec').body[0].args.args[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('from a import (b as c)', 'exec').body[0].names[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('from a import (b\n as c)', 'exec').body[0].names[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('from a import (b\\\n as c)', 'exec').body[0].names[0].copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('with (b as c): pass', 'exec').body[0].items[0].copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('with (b\n as c): pass', 'exec').body[0].items[0].copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('with (b\\\n as c): pass', 'exec').body[0].items[0].copy(pars=False)._is_enclosed_or_line())

        if PYGE14:
            self.assertTrue(FST(r'''
(t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
            self.assertFalse(FST(r'''
(t"a{(1,

2)}b" t"""{3}

{4}
{5}"""
t"x\
y")
                '''.strip(), 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

    def test__is_enclosed_or_line_general(self):
        self.assertTrue(FST('a < b', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\n< b)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n< b)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\\\n<\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('(a\\\n<\\\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertFalse(FST('(a\\\n<\n\\\nb)', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a, b, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, b\\\n, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, [\nb\n], c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a, {\nx: y\n}, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, {\nb\n}, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, [\ni for i in j\n], c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, {\ni for i in j\n}, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, {\ni: j for i, j in k\n}, c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, (\ni for i in j\n), c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, [i,\nj], c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())
        self.assertTrue(FST('a, b[\ni:j:k\n], c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        self.assertTrue(FST('a\n: \nb: \nc', 'expr_slice')._is_enclosed_or_line())  # because is never used unenclosed
        self.assertTrue(FST('a\\\n: \\\nb: \\\nc', 'expr_slice')._is_enclosed_or_line())

        self.assertTrue(FST('1')._is_enclosed_or_line())

        if PYGE12:
            self.assertTrue(FST('a, f"{(1,\n2)}", c', 'exec').body[0].value.copy(pars=False)._is_enclosed_or_line())

        # whole

        self.assertTrue(FST('\na + b\n')._is_enclosed_or_line(whole=False))
        self.assertFalse(FST('\na + b\n')._is_enclosed_or_line(whole=True))
        self.assertFalse(FST('\\\na + b\n')._is_enclosed_or_line(whole=True))
        self.assertFalse(FST('\na + b\\\n')._is_enclosed_or_line(whole=True))
        self.assertTrue(FST('\\\na + b\\\n')._is_enclosed_or_line(whole=True))
        self.assertTrue(FST('a + b')._is_enclosed_or_line(whole=True))

        self.assertTrue(FST('\na + b * c\n').right._is_enclosed_or_line(whole=False))
        self.assertRaises(ValueError, FST('\na + b * c\n').right._is_enclosed_or_line, whole=True)

        # out_lns

        self.assertTrue(FST('\na + \\\n(b\n*\nc)\n')._is_enclosed_or_line(whole=False, out_lns=(lns := set())))
        self.assertEqual(set(), lns)

        self.assertFalse(FST('\na + \n(b\n*\nc)\n')._is_enclosed_or_line(whole=False, out_lns=(lns := set())))
        self.assertEqual({1}, lns)

        self.assertFalse(FST('\na + \n(b\n*\nc)\n')._is_enclosed_or_line(whole=True, out_lns=(lns := set())))
        self.assertEqual({0, 1, 4}, lns)

        f = FST(r'''
a + \
("""
*"""
"c")
''')
        self.assertTrue(f._is_enclosed_or_line(whole=False, out_lns=(lns := set())))
        self.assertEqual(set(), lns)
        f.right.unpar()
        self.assertFalse(f._is_enclosed_or_line(whole=False, out_lns=(lns := set())))
        self.assertEqual({3}, lns)
        self.assertFalse(f._is_enclosed_or_line(whole=True, out_lns=(lns := set())))
        self.assertEqual({0, 3, 4}, lns)

        # ImportFrom

        self.assertTrue(FST('from a import \\\nb')._is_enclosed_or_line())
        self.assertTrue(FST('from a import (\nb)')._is_enclosed_or_line())

        f = FST('from a import (\nb)')
        f._put_src(None, 1, 1, 1, 2, True)
        f._put_src(None, 0, 14, 0, 15, False)
        self.assertFalse(f._is_enclosed_or_line())

        # With / AsyncWith

        self.assertTrue(FST('with \\\nb\\\n:\n  pass')._is_enclosed_or_line())
        self.assertTrue(FST('with (\nb\n):\n  pass')._is_enclosed_or_line())

        f = FST('with (\na\n):\n  pass')
        f._put_src(None, 2, 0, 2, 1, True)
        f._put_src(None, 0, 5, 0, 6, False)
        self.assertFalse(f._is_enclosed_or_line())

        # not implemented yet (because haven't run into a need)

        self.assertRaises(NotImplementedError, FST('a\nb')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('a; b', 'Interactive')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('def f(): pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('async def f(): pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('class cls: pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('for _ in _: pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('async for _ in _: pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('while _: pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('if _: pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('match _:\n  case _: pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('try: pass\nexcept: pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('except: pass')._is_enclosed_or_line)
        self.assertRaises(NotImplementedError, FST('case _: pass')._is_enclosed_or_line)

        if PYGE11:
            self.assertRaises(NotImplementedError, FST('try: pass\nexcept* Exception: pass')._is_enclosed_or_line)

    def test__is_enclosed_or_multiline_str(self):
        self.assertTrue(FST(r'''["""a
b
c"""]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''["a \
b \
c"]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''["a" \
"b" \
"c"]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''["a" \
"b \
c"]''').elts[0]._is_enclosed_or_line())

        self.assertFalse(FST(r'''["a" \
"b"
"c"]''').elts[0]._is_enclosed_or_line())

        # f-string

        self.assertTrue(FST(r'''[f"""a
b
c"""]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''[f"a \
b \
c"]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''[f"a" \
f"b" \
f"c"]''').elts[0]._is_enclosed_or_line())

        self.assertTrue(FST(r'''[f"a" \
f"b \
c"]''').elts[0]._is_enclosed_or_line())

        self.assertFalse(FST(r'''[f"a" \
f"b"
f"c"]''').elts[0]._is_enclosed_or_line())

        # t-string

        if PYGE14:
            self.assertTrue(FST(r'''[t"""a
b
c"""]''').elts[0]._is_enclosed_or_line())

            self.assertTrue(FST(r'''[t"a \
b \
c"]''').elts[0]._is_enclosed_or_line())

            self.assertTrue(FST(r'''[t"a" \
t"b" \
t"c"]''').elts[0]._is_enclosed_or_line())

            self.assertTrue(FST(r'''[t"a" \
t"b \
c"]''').elts[0]._is_enclosed_or_line())

            self.assertFalse(FST(r'''[t"a" \
t"b"
t"c"]''').elts[0]._is_enclosed_or_line())

    def test__is_enclosed_in_parents(self):
        self.assertFalse(FST('i', 'exec').body[0]._is_enclosed_in_parents())
        self.assertFalse(FST('i', 'single').body[0]._is_enclosed_in_parents())
        self.assertFalse(FST('i', 'eval').body._is_enclosed_in_parents())

        self.assertFalse(FST('@d\ndef f(): pass', 'exec').body[0].decorator_list[0]._is_enclosed_in_parents())
        self.assertTrue(FST('def f(): pass', 'exec').body[0].args._is_enclosed_in_parents())
        self.assertTrue(FST('def f(a) -> int: pass', 'exec').body[0].args._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a) -> int: pass', 'exec').body[0].returns._is_enclosed_in_parents())

        self.assertFalse(FST('@d\nasync def f(): pass', 'exec').body[0].decorator_list[0]._is_enclosed_in_parents())
        self.assertTrue(FST('async def f(): pass', 'exec').body[0].args._is_enclosed_in_parents())
        self.assertTrue(FST('async def f(a) -> int: pass', 'exec').body[0].args._is_enclosed_in_parents())
        self.assertFalse(FST('async def f(a) -> int: pass', 'exec').body[0].returns._is_enclosed_in_parents())

        self.assertFalse(FST('@d\nclass c: pass', 'exec').body[0].decorator_list[0]._is_enclosed_in_parents())
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0].bases[0]._is_enclosed_in_parents())
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0].keywords[0]._is_enclosed_in_parents())

        self.assertFalse(FST('return v', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('del v', 'exec').body[0].targets[0]._is_enclosed_in_parents())
        self.assertFalse(FST('t = v', 'exec').body[0].targets[0]._is_enclosed_in_parents())
        self.assertFalse(FST('t = v', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].target._is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].op._is_enclosed_in_parents())
        self.assertFalse(FST('t += v', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].target._is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].annotation._is_enclosed_in_parents())
        self.assertFalse(FST('t: int = v', 'exec').body[0].value._is_enclosed_in_parents())

        self.assertFalse(FST('for a in b: pass', 'exec').body[0].target._is_enclosed_in_parents())
        self.assertFalse(FST('for a in b: pass', 'exec').body[0].iter._is_enclosed_in_parents())
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0].target._is_enclosed_in_parents())
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0].iter._is_enclosed_in_parents())
        self.assertFalse(FST('while a: pass', 'exec').body[0].test._is_enclosed_in_parents())
        self.assertFalse(FST('if a: pass', 'exec').body[0].test._is_enclosed_in_parents())

        self.assertFalse(FST('with a: pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertFalse(FST('with (a): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())  # pars belong to `a`
        self.assertFalse(FST('with ((a)): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())  # pars belong to `a`
        self.assertTrue(FST('with (a as b): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())  # pars belong to `with`
        self.assertTrue(FST('with ((a) as b): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())  # outer pars belong to `with`
        self.assertFalse(FST('async with a: pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertFalse(FST('async with (a): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertFalse(FST('async with ((a)): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertTrue(FST('async with (a as b): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())
        self.assertTrue(FST('async with ((a) as b): pass', 'exec').body[0].items[0]._is_enclosed_in_parents())

        self.assertFalse(FST('match (a):\n case 1: pass', 'exec').body[0].subject._is_enclosed_in_parents())
        self.assertFalse(FST('raise exc from cause', 'exec').body[0].exc._is_enclosed_in_parents())
        self.assertFalse(FST('raise exc from cause', 'exec').body[0].cause._is_enclosed_in_parents())
        self.assertFalse(FST('try: pass\nexcept Exception as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())
        self.assertFalse(FST('try: pass\nexcept (Exception) as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())  # because pars belong to `type`
        self.assertFalse(FST('try: pass\nexcept ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())  # same
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0].test._is_enclosed_in_parents())
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0].msg._is_enclosed_in_parents())
        self.assertFalse(FST('import a as b', 'exec').body[0].names[0]._is_enclosed_in_parents())
        self.assertFalse(FST('from a import b', 'exec').body[0].names[0]._is_enclosed_in_parents())
        self.assertFalse(FST('from a import b as c', 'exec').body[0].names[0]._is_enclosed_in_parents())
        self.assertTrue(FST('from a import (b)', 'exec').body[0].names[0]._is_enclosed_in_parents())
        self.assertTrue(FST('from a import (b as c)', 'exec').body[0].names[0]._is_enclosed_in_parents())

        self.assertFalse(FST('(a)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.op._is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[0]._is_enclosed_in_parents())
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[1]._is_enclosed_in_parents())
        self.assertFalse(FST('(a := b)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.left._is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.op._is_enclosed_in_parents())
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value.right._is_enclosed_in_parents())
        self.assertFalse(FST('-(a)', 'exec').body[0].value.op._is_enclosed_in_parents())
        self.assertFalse(FST('-(a)', 'exec').body[0].value.operand._is_enclosed_in_parents())
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value.args._is_enclosed_in_parents())
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value.body._is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.body._is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.test._is_enclosed_in_parents())
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value.orelse._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v}', 'exec').body[0].value.keys[0]._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v}', 'exec').body[0].value.values[0]._is_enclosed_in_parents())
        self.assertTrue(FST('{a}', 'exec').body[0].value.elts[0]._is_enclosed_in_parents())
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.elt._is_enclosed_in_parents())
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value.generators[0]._is_enclosed_in_parents())
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value.elt._is_enclosed_in_parents())
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value.generators[0]._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.key._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.value._is_enclosed_in_parents())
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value.generators[0]._is_enclosed_in_parents())
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value.elt._is_enclosed_in_parents())
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value.generators[0]._is_enclosed_in_parents())
        self.assertFalse(FST('await (a)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('yield (a)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('yield from (a)', 'exec').body[0].value._is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.left._is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.ops[0]._is_enclosed_in_parents())
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value.comparators[0]._is_enclosed_in_parents())
        self.assertFalse(FST('call(a, b=c)', 'exec').body[0].value.func._is_enclosed_in_parents())
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value.args[0]._is_enclosed_in_parents())
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value.keywords[0]._is_enclosed_in_parents())
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[0]._is_enclosed_in_parents())
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[1].value._is_enclosed_in_parents())

        self.assertFalse(FST('(a).b', 'exec').body[0].value.value._is_enclosed_in_parents())
        self.assertFalse(FST('(a).b', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value.value._is_enclosed_in_parents())
        self.assertTrue(FST('(a)[b]', 'exec').body[0].value.slice._is_enclosed_in_parents())
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('*(a)', 'exec').body[0].value.value._is_enclosed_in_parents())
        self.assertFalse(FST('*(a)', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('a', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('(a)', 'exec').body[0].value.ctx._is_enclosed_in_parents())

        self.assertTrue(FST('[a]', 'exec').body[0].value.elts[0]._is_enclosed_in_parents())
        self.assertFalse(FST('[a]', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertTrue(FST('(a,)', 'exec').body[0].value.elts[0]._is_enclosed_in_parents())
        self.assertFalse(FST('(a,)', 'exec').body[0].value.ctx._is_enclosed_in_parents())
        self.assertFalse(FST('a,', 'exec').body[0].value.elts[0]._is_enclosed_in_parents())
        self.assertFalse(FST('a,', 'exec').body[0].value.ctx._is_enclosed_in_parents())

        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).lower._is_enclosed_in_parents())
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).upper._is_enclosed_in_parents())
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True).step._is_enclosed_in_parents())

        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).target._is_enclosed_in_parents())
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).iter._is_enclosed_in_parents())
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True).ifs[0]._is_enclosed_in_parents())

        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).posonlyargs[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).args[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).defaults[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).vararg._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kwonlyargs[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kw_defaults[0]._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True).kwarg._is_enclosed_in_parents())
        self.assertFalse(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=True).annotation._is_enclosed_in_parents())

        self.assertFalse(FST('call(k=v)', 'exec').body[0].value.keywords[0].copy(pars=True).value._is_enclosed_in_parents())

        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True).context_expr._is_enclosed_in_parents())
        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True).optional_vars._is_enclosed_in_parents())

        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True).pattern._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True).guard._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).value._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).value._is_enclosed_in_parents())  # inconsistent case, MatchValue owns the pars
        self.assertFalse(FST('match a:\n case 1, 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1, 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case [1, 2]: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).keys[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).cls._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).kwd_patterns[0]._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1 as a: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).pattern._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1 as a): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).pattern._is_enclosed_in_parents())
        self.assertFalse(FST('match a:\n case 1 | 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())
        self.assertTrue(FST('match a:\n case (1 | 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True).patterns[0]._is_enclosed_in_parents())

        if PYGE12:
            self.assertTrue(FST('def f[T]() -> int: pass', 'exec').body[0].type_params[0]._is_enclosed_in_parents())
            self.assertTrue(FST('async def f[T]() -> int: pass', 'exec').body[0].type_params[0]._is_enclosed_in_parents())
            self.assertTrue(FST('class c[T]: pass', 'exec').body[0].type_params[0]._is_enclosed_in_parents())

            self.assertFalse(FST('type t[T] = v', 'exec').body[0].name._is_enclosed_in_parents())
            self.assertTrue(FST('type t[T] = v', 'exec').body[0].type_params[0]._is_enclosed_in_parents())
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].value._is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* Exception as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* (Exception) as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())
            self.assertFalse(FST('try: pass\nexcept* ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0].type._is_enclosed_in_parents())
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())
            self.assertFalse(FST('type t[*T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())
            self.assertFalse(FST('type t[**T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())

        if PYGE14:
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[0]._is_enclosed_in_parents())
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[1].value._is_enclosed_in_parents())

        # with field

        self.assertFalse(FST('i', 'exec')._is_enclosed_in_parents('body'))
        self.assertFalse(FST('i', 'single')._is_enclosed_in_parents('body'))
        self.assertFalse(FST('i', 'eval')._is_enclosed_in_parents('body'))

        self.assertFalse(FST('@d\ndef f(): pass', 'exec').body[0]._is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('def f(): pass', 'exec').body[0]._is_enclosed_in_parents('args'))
        self.assertTrue(FST('def f(a) -> int: pass', 'exec').body[0]._is_enclosed_in_parents('args'))
        self.assertFalse(FST('def f(a) -> int: pass', 'exec').body[0]._is_enclosed_in_parents('returns'))

        self.assertFalse(FST('@d\nasync def f(): pass', 'exec').body[0]._is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('async def f(): pass', 'exec').body[0]._is_enclosed_in_parents('args'))
        self.assertTrue(FST('async def f(a) -> int: pass', 'exec').body[0]._is_enclosed_in_parents('args'))
        self.assertFalse(FST('async def f(a) -> int: pass', 'exec').body[0]._is_enclosed_in_parents('returns'))

        self.assertFalse(FST('@d\nclass c: pass', 'exec').body[0]._is_enclosed_in_parents('decorator_list'))
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0]._is_enclosed_in_parents('bases'))
        self.assertTrue(FST('class c(b, k=v): pass', 'exec').body[0]._is_enclosed_in_parents('keywords'))

        self.assertFalse(FST('return v', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('del v', 'exec').body[0]._is_enclosed_in_parents('targets'))
        self.assertFalse(FST('t = v', 'exec').body[0]._is_enclosed_in_parents('targets'))
        self.assertFalse(FST('t = v', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('t += v', 'exec').body[0]._is_enclosed_in_parents('target'))
        self.assertFalse(FST('t += v', 'exec').body[0]._is_enclosed_in_parents('op'))
        self.assertFalse(FST('t += v', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('t: int = v', 'exec').body[0]._is_enclosed_in_parents('target'))
        self.assertFalse(FST('t: int = v', 'exec').body[0]._is_enclosed_in_parents('annotation'))
        self.assertFalse(FST('t: int = v', 'exec').body[0]._is_enclosed_in_parents('value'))

        self.assertFalse(FST('for a in b: pass', 'exec').body[0]._is_enclosed_in_parents('target'))
        self.assertFalse(FST('for a in b: pass', 'exec').body[0]._is_enclosed_in_parents('iter'))
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0]._is_enclosed_in_parents('target'))
        self.assertFalse(FST('async for a in b: pass', 'exec').body[0]._is_enclosed_in_parents('iter'))
        self.assertFalse(FST('while a: pass', 'exec').body[0]._is_enclosed_in_parents('test'))
        self.assertFalse(FST('if a: pass', 'exec').body[0]._is_enclosed_in_parents('test'))

        self.assertFalse(FST('with a: pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertFalse(FST('with (a): pass', 'exec').body[0]._is_enclosed_in_parents('items'))  # pars belong to `a`
        self.assertFalse(FST('with ((a)): pass', 'exec').body[0]._is_enclosed_in_parents('items'))  # pars belong to `a`
        self.assertTrue(FST('with (a as b): pass', 'exec').body[0]._is_enclosed_in_parents('items'))  # pars belong to `with`
        self.assertTrue(FST('with ((a) as b): pass', 'exec').body[0]._is_enclosed_in_parents('items'))  # outer pars belong to `with`
        self.assertFalse(FST('async with a: pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertFalse(FST('async with (a): pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertFalse(FST('async with ((a)): pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertTrue(FST('async with (a as b): pass', 'exec').body[0]._is_enclosed_in_parents('items'))
        self.assertTrue(FST('async with ((a) as b): pass', 'exec').body[0]._is_enclosed_in_parents('items'))

        self.assertFalse(FST('match (a):\n case 1: pass', 'exec').body[0]._is_enclosed_in_parents('subject'))
        self.assertFalse(FST('raise exc from cause', 'exec').body[0]._is_enclosed_in_parents('exc'))
        self.assertFalse(FST('raise exc from cause', 'exec').body[0]._is_enclosed_in_parents('cause'))
        self.assertFalse(FST('try: pass\nexcept Exception as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))
        self.assertFalse(FST('try: pass\nexcept (Exception) as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))  # because pars belong to `type`
        self.assertFalse(FST('try: pass\nexcept ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))  # same
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0]._is_enclosed_in_parents('test'))
        self.assertFalse(FST('assert (a), (b)', 'exec').body[0]._is_enclosed_in_parents('msg'))
        self.assertFalse(FST('import a as b', 'exec').body[0]._is_enclosed_in_parents('names'))
        self.assertFalse(FST('from a import b', 'exec').body[0]._is_enclosed_in_parents('names'))
        self.assertFalse(FST('from a import b as c', 'exec').body[0]._is_enclosed_in_parents('names'))
        self.assertTrue(FST('from a import (b)', 'exec').body[0]._is_enclosed_in_parents('names'))
        self.assertTrue(FST('from a import (b as c)', 'exec').body[0]._is_enclosed_in_parents('names'))

        self.assertFalse(FST('(a)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value._is_enclosed_in_parents('op'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value._is_enclosed_in_parents('values'))
        self.assertFalse(FST('(a) or (b)', 'exec').body[0].value.values[1]._is_enclosed_in_parents())
        self.assertFalse(FST('(a := b)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value._is_enclosed_in_parents('left'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value._is_enclosed_in_parents('op'))
        self.assertFalse(FST('(a) + (b)', 'exec').body[0].value._is_enclosed_in_parents('right'))
        self.assertFalse(FST('-(a)', 'exec').body[0].value._is_enclosed_in_parents('op'))
        self.assertFalse(FST('-(a)', 'exec').body[0].value._is_enclosed_in_parents('operand'))
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value._is_enclosed_in_parents('args'))
        self.assertFalse(FST('lambda a: (b)', 'exec').body[0].value._is_enclosed_in_parents('body'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value._is_enclosed_in_parents('body'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value._is_enclosed_in_parents('test'))
        self.assertFalse(FST('(a) if (b) else (c)', 'exec').body[0].value._is_enclosed_in_parents('orelse'))
        self.assertTrue(FST('{k: v}', 'exec').body[0].value._is_enclosed_in_parents('keys'))
        self.assertTrue(FST('{k: v}', 'exec').body[0].value._is_enclosed_in_parents('values'))
        self.assertTrue(FST('{a}', 'exec').body[0].value._is_enclosed_in_parents('elts'))
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value._is_enclosed_in_parents('elt'))
        self.assertTrue(FST('[i for i in j]', 'exec').body[0].value._is_enclosed_in_parents('generators'))
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value._is_enclosed_in_parents('elt'))
        self.assertTrue(FST('{i for i in j}', 'exec').body[0].value._is_enclosed_in_parents('generators'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value._is_enclosed_in_parents('key'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value._is_enclosed_in_parents('value'))
        self.assertTrue(FST('{k: v for k, v in j}', 'exec').body[0].value._is_enclosed_in_parents('generators'))
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value._is_enclosed_in_parents('elt'))
        self.assertTrue(FST('(i for i in j)', 'exec').body[0].value._is_enclosed_in_parents('generators'))
        self.assertFalse(FST('await (a)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('yield (a)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('yield from (a)', 'exec').body[0]._is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value._is_enclosed_in_parents('left'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value._is_enclosed_in_parents('ops'))
        self.assertFalse(FST('(a) < (b)', 'exec').body[0].value._is_enclosed_in_parents('comparators'))
        self.assertFalse(FST('call(a, b=c)', 'exec').body[0].value._is_enclosed_in_parents('func'))
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value._is_enclosed_in_parents('args'))
        self.assertTrue(FST('call(a, b=c)', 'exec').body[0].value._is_enclosed_in_parents('keywords'))
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value._is_enclosed_in_parents('values'))
        self.assertTrue(FST('''f"1{2}"''', 'exec').body[0].value.values[1]._is_enclosed_in_parents('value'))

        self.assertFalse(FST('(a).b', 'exec').body[0].value._is_enclosed_in_parents('value'))
        self.assertFalse(FST('(a).b', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value._is_enclosed_in_parents('value'))
        self.assertTrue(FST('(a)[b]', 'exec').body[0].value._is_enclosed_in_parents('slice'))
        self.assertFalse(FST('(a)[b]', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('*(a)', 'exec').body[0].value._is_enclosed_in_parents('value'))
        self.assertFalse(FST('*(a)', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('a', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('(a)', 'exec').body[0].value._is_enclosed_in_parents('ctx'))

        self.assertTrue(FST('[a]', 'exec').body[0].value._is_enclosed_in_parents('elts'))
        self.assertFalse(FST('[a]', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertTrue(FST('(a,)', 'exec').body[0].value._is_enclosed_in_parents('elts'))
        self.assertFalse(FST('(a,)', 'exec').body[0].value._is_enclosed_in_parents('ctx'))
        self.assertFalse(FST('a,', 'exec').body[0].value._is_enclosed_in_parents('elts'))
        self.assertFalse(FST('a,', 'exec').body[0].value._is_enclosed_in_parents('ctx'))

        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True)._is_enclosed_in_parents('lower'))
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True)._is_enclosed_in_parents('upper'))
        self.assertFalse(FST('a[b:c:d]', 'exec').body[0].value.slice.copy(pars=True)._is_enclosed_in_parents('step'))

        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True)._is_enclosed_in_parents('target'))
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True)._is_enclosed_in_parents('iter'))
        self.assertFalse(FST('[i for (i) in (j) if (i)]', 'exec').body[0].value.generators[0].copy(pars=True)._is_enclosed_in_parents('ifs'))

        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('posonlyargs'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('args'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('defaults'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('vararg'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('kwonlyargs'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('kw_defaults'))
        self.assertFalse(FST('def f(a, /, b=1, *c, d=2, **e): pass', 'exec').body[0].args.copy(pars=True)._is_enclosed_in_parents('kwarg'))
        self.assertFalse(FST('def f(a: int): pass', 'exec').body[0].args.args[0].copy(pars=True)._is_enclosed_in_parents('annotation'))

        self.assertFalse(FST('call(k=v)', 'exec').body[0].value.keywords[0].copy(pars=True)._is_enclosed_in_parents('value'))

        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True)._is_enclosed_in_parents('context_expr'))
        self.assertFalse(FST('with ((a) as (b)): pass', 'exec').body[0].items[0].copy(pars=True)._is_enclosed_in_parents('optional_vars'))

        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True)._is_enclosed_in_parents('pattern'))
        self.assertFalse(FST('match a:\n case (1 as i) if (i): pass', 'exec').body[0].cases[0].copy(pars=True)._is_enclosed_in_parents('guard'))
        self.assertFalse(FST('match a:\n case 1: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('value'))
        self.assertTrue(FST('match a:\n case (1): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('value'))  # inconsistent case, MatchValue owns the pars
        self.assertFalse(FST('match a:\n case 1, 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case (1, 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case [1, 2]: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('keys'))
        self.assertTrue(FST('match a:\n case {1: a}: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertFalse(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('cls'))
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case c(a, b=c): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('kwd_patterns'))
        self.assertFalse(FST('match a:\n case 1 as a: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('pattern'))
        self.assertTrue(FST('match a:\n case (1 as a): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('pattern'))
        self.assertFalse(FST('match a:\n case 1 | 2: pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))
        self.assertTrue(FST('match a:\n case (1 | 2): pass', 'exec').body[0].cases[0].pattern.copy(pars=True)._is_enclosed_in_parents('patterns'))

        if PYGE12:
            self.assertTrue(FST('def f[T]() -> int: pass', 'exec').body[0]._is_enclosed_in_parents('type_params'))
            self.assertTrue(FST('async def f[T]() -> int: pass', 'exec').body[0]._is_enclosed_in_parents('type_params'))
            self.assertTrue(FST('class c[T]: pass', 'exec').body[0]._is_enclosed_in_parents('type_params'))

            self.assertFalse(FST('type t[T] = v', 'exec').body[0]._is_enclosed_in_parents('name'))
            self.assertTrue(FST('type t[T] = v', 'exec').body[0]._is_enclosed_in_parents('type_params'))
            self.assertFalse(FST('type t[T] = v', 'exec').body[0]._is_enclosed_in_parents('value'))
            self.assertFalse(FST('try: pass\nexcept* Exception as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))
            self.assertFalse(FST('try: pass\nexcept* (Exception) as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))
            self.assertFalse(FST('try: pass\nexcept* ((Exception, ValueError)) as exc: pass', 'exec').body[0].handlers[0]._is_enclosed_in_parents('type'))
            self.assertFalse(FST('type t[T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())
            self.assertFalse(FST('type t[*T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())
            self.assertFalse(FST('type t[**T] = v', 'exec').body[0].type_params[0].copy()._is_enclosed_in_parents())

        if PYGE14:
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value._is_enclosed_in_parents('values'))
            self.assertTrue(FST('t"1{2}"', 'exec').body[0].value.values[1]._is_enclosed_in_parents('value'))

        # extreme misc for coverage

        self.assertFalse(FST(Load())._is_enclosed_in_parents())

    def test__touchall(self):
        a = parse('i = [1]').body[0]
        self.assertEqual(7, a.f.end_col)
        self.assertEqual(7, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.end_col_offset = 8
        a.value.end_col_offset = 8
        a.value.elts[0].end_col_offset = 7

        self.assertEqual(7, a.f.end_col)
        self.assertEqual(7, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall(False, True, False)
        self.assertEqual(7, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall(parents=True, children=False)
        self.assertEqual(8, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(6, a.value.elts[0].f.end_col)

        a.value.f._touchall(parents=False, children=True)
        self.assertEqual(8, a.f.end_col)
        self.assertEqual(8, a.value.f.end_col)
        self.assertEqual(7, a.value.elts[0].f.end_col)

    def test__offset(self):
        src = 'i = 1\nj = 2\nk = 3'

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 5, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1, exclude=ast.body[1].f)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 0, 1, exclude=ast.body[1].f, offset_excluded=False)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 0, 1, True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 6), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 4, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 3, 4), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 3, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 5), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f._offset(1, 5, 1, -1, True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 3, 4), ((n := ast.body[1]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        def get():
            m = parse('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nbbbb\ncccc')

            m.body[0] = m.body[0].value
            m.body[1] = m.body[1].value
            m.body[2] = m.body[2].value

            m.body[0].lineno         = 1
            m.body[0].end_lineno     = 1
            m.body[0].col_offset     = 2
            m.body[0].end_col_offset = 6
            m.body[1].lineno         = 1
            m.body[1].end_lineno     = 1
            m.body[1].col_offset     = 6
            m.body[1].end_col_offset = 10
            m.body[2].lineno         = 1
            m.body[2].end_lineno     = 1
            m.body[2].col_offset     = 6
            m.body[2].end_col_offset = 6

            return m

        m = get()
        m.f._offset(0, 6, 0, 2, False, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, True, True)
        self.assertEqual((0, 2, 0, 8), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 8, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, False, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, True, False)
        self.assertEqual((0, 2, 0, 8), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, True)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, False)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, True)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 8, 0, 8), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, 2, None, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, False, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, True, None)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

        m = get()
        m.f._offset(0, 6, 0, -2, None, None)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 6), m.body[2].f.loc)

        # misc for coverage

        (f := FST('1'))._offset(0, 0, 0, 0, exclude=f, self_=False)
        f.verify()

    def test__get_block_indent(self):
        ast = parse('i = 1; j = 2')

        self.assertEqual('', ast.body[0].f._get_block_indent())
        self.assertEqual('', ast.body[1].f._get_block_indent())

        ast = parse('def f(): \\\n i = 1')

        self.assertEqual('', ast.body[0].f._get_block_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f._get_block_indent())

        ast = parse('class cls: i = 1')

        self.assertEqual('', ast.body[0].f._get_block_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f._get_block_indent())

        ast = parse('class cls: i = 1; \\\n    j = 2')

        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f._get_block_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[1].f._get_block_indent())

        ast = parse('class cls:\n  i = 1; \\\n    j = 2')

        self.assertEqual('  ', ast.body[0].body[0].f._get_block_indent())
        self.assertEqual('  ', ast.body[0].body[1].f._get_block_indent())

        ast = parse('class cls:\n   def f(): i = 1')

        self.assertEqual('   ', ast.body[0].body[0].f._get_block_indent())
        self.assertEqual('   ' + ast.f.root.indent, ast.body[0].body[0].body[0].f._get_block_indent())

        self.assertEqual('   ', parse('def f():\n   1').body[0].body[0].f._get_block_indent())
        self.assertEqual('    ', parse('def f(): 1').body[0].body[0].f._get_block_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1').body[0].body[0].f._get_block_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1').body[0].body[0].f._get_block_indent())

        self.assertEqual('    ', parse('class cls:\n def f():\n    1').body[0].body[0].body[0].f._get_block_indent())
        self.assertEqual('  ', parse('class cls:\n def f(): 1').body[0].body[0].body[0].f._get_block_indent())  # indentation inferred otherwise would be '     '
        self.assertEqual('  ', parse('class cls:\n def f(): \\\n   1').body[0].body[0].body[0].f._get_block_indent())  # indentation inferred otherwise would be '     '
        self.assertEqual('   ', parse('class cls:\n def f(): # \\\n   1').body[0].body[0].body[0].f._get_block_indent())

        self.assertEqual('  ', parse('if 1:\n  2\nelse:\n   3').body[0].body[0].f._get_block_indent())
        self.assertEqual('   ', parse('if 1: 2\nelse:\n   3').body[0].body[0].f._get_block_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('   ', parse('if 1: \\\n 2\nelse:\n   3').body[0].body[0].f._get_block_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('  ', parse('if 1: # \\\n  2\nelse:\n   3').body[0].body[0].f._get_block_indent())

        self.assertEqual('   ', parse('if 1:\n  2\nelse:\n   3').body[0].orelse[0].f._get_block_indent())
        self.assertEqual('  ', parse('if 1:\n  2\nelse: 3').body[0].orelse[0].f._get_block_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('  ', parse('if 1:\n  2\nelse: \\\n 3').body[0].orelse[0].f._get_block_indent())  # candidate for sibling indentation, indentation inferred otherwise would be '    '
        self.assertEqual('   ', parse('if 1:\n  2\nelse: # \\\n   3').body[0].orelse[0].f._get_block_indent())

        self.assertEqual('   ', parse('def f():\n   1; 2').body[0].body[1].f._get_block_indent())
        self.assertEqual('    ', parse('def f(): 1; 2').body[0].body[1].f._get_block_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1; 2').body[0].body[1].f._get_block_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1; 2').body[0].body[1].f._get_block_indent())

        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f._get_block_indent())
        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f._get_block_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f._get_block_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f._get_block_indent())

        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[0].f._get_block_indent())
        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[1].f._get_block_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[0].f._get_block_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[1].f._get_block_indent())

        self.assertEqual('', parse('\\\ni').body[0].f._get_block_indent())
        self.assertEqual('    ', parse('try: i\nexcept: pass').body[0].body[0].f._get_block_indent())

        self.assertEqual('', parse('if 1: i\nelif 2: j').body[0].f._get_block_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j').body[0].body[0].f._get_block_indent())
        self.assertEqual('', parse('if 1: i\nelif 2: j').body[0].orelse[0].f._get_block_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j').body[0].orelse[0].body[0].f._get_block_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j\nelse: k').body[0].orelse[0].orelse[0].f._get_block_indent())
        self.assertEqual('    ', parse('if 1: i\nelif 2: j\nelif 3: k').body[0].orelse[0].orelse[0].body[0].f._get_block_indent())

        # self.assertEqual('  ', parse('if 1: i\nelse:\n  j').body[0].body[0].f._get_block_indent())  # candidate for sibling indentation, nope, not doing this

        self.assertEqual('  ', parse('if 1:\n\\\n  \\\n i').body[0].body[0].f._get_block_indent())
        self.assertEqual('  ', parse('if 1:\n  \\\n\\\n i').body[0].body[0].f._get_block_indent())
        self.assertEqual('  ', parse('if 1:\n  \\\n   \\\n\\\n i').body[0].body[0].f._get_block_indent())
        self.assertEqual('   ', parse('if 1:\n   \\\n  \\\n\\\n i').body[0].body[0].f._get_block_indent())
        self.assertEqual('    ', parse('if 1: \\\n\\\n  \\\n   \\\n\\\n i').body[0].body[0].f._get_block_indent())
        self.assertEqual('  ', parse('if 1:\n\\\n  \\\n   \\\n\\\n i').body[0].body[0].f._get_block_indent())
        self.assertEqual('     ', parse('if 1:\n\\\n\\\n     \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].f._get_block_indent())

        self.assertEqual('          ', parse('if 2:\n     if 1:\\\n\\\n\\\n  \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].body[0].f._get_block_indent())  # indentation inferred otherwise would be '         '
        self.assertEqual('      ', parse('if 2:\n     if 1:\n\\\n      \\\n  \\\n\\\n\\\n  \\\n\\\n   \\\n\\\n i').body[0].body[0].body[0].f._get_block_indent())

    def test__get_indentable_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = "... \\\n2"\n else:\n  j \\\n=\\\n 2'
        ast = parse(src)

        self.assertEqual({1, 2, 5, 7, 8, 9, 10}, ast.f._get_indentable_lns(1))
        self.assertEqual({0, 1, 2, 5, 7, 8, 9, 10}, ast.f._get_indentable_lns(0))

        self.assertEqual(set(), ast.body[0].body[0].body[0].value.f._get_indentable_lns(1))
        self.assertEqual({2}, ast.body[0].body[0].body[0].value.f._get_indentable_lns(0))

        f = FST.fromsrc('''
def _splitext(p, sep, altsep, extsep):
    """Split the extension from a pathname.

    Extension is everything from the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work for text and bytes strings.

    sepIndex = p.rfind(sep)
            '''.strip())
        self.assertEqual({0, 1, 2, 3, 4, 5, 6, 7}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0, 1, 5, 6, 7}, f._get_indentable_lns(docstr=False))

        f = FST.fromsrc(r'''
_CookiePattern = re.compile(r"""
    \s*                            # Optional whitespace at start of cookie
    (?P<key>                       # Start of group 'key'
    [""" + _LegalKeyChars + r"""]+?   # Any word of at least one letter
    )                              # End of group 'key'
    (                              # Optional group: there may not be a value.
    \s*=\s*                          # Equal Sign
    (?P<val>                         # Start of group 'val'
    "(?:[^\\"]|\\.)*"                  # Any doublequoted string
    |                                  # or
    \w{3},\s[\w\d\s-]{9,11}\s[\d:]{8}\sGMT  # Special case for "expires" attr
    |                                  # or
    [""" + _LegalValueChars + r"""]*      # Any word or empty string
    )                                # End of group 'val'
    )?                             # End of optional value group
    \s*                            # Any number of spaces.
    (\s+|;|$)                      # Ending either at space, semicolon, or EOS.
    """, re.ASCII | re.VERBOSE)    # re.ASCII may be removed if safe.
            '''.strip())
        self.assertEqual({0}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0, 1}, f._get_indentable_lns(docstr=True))
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
f"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0}, f._get_indentable_lns(docstr=True))  # because f-strings cannot be docstrings
        self.assertEqual({0}, f._get_indentable_lns(docstr=False))

    def test__offset_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j = 2'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._offset_lns(lns, 1)
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
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._offset_lns(lns, 1)
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
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._offset_lns(lns, 1)
        self.assertEqual(set(), lns)
        self.assertEqual((2, 2, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 6, 4, 3), ast.body[0].body[0].body[0].value.f.loc)

        src = 'i = 1\nj = 2\nk = 3\nl = \\\n4'
        ast = parse(src)
        off = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

        ast.f._offset_lns(off)
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

    def test__indent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._indent_lns('  ', lns)
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n   if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._indent_lns('  ', lns)
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._indent_lns('  ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._get_indentable_lns(1)
        ast.body[0].body[0].orelse[0].f._indent_lns('  ', lns)
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n  =\\\n   2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._indent_lns('  ', lns)
        self.assertEqual({1, 2}, lns)
        self.assertEqual('@decorator\n  class cls:\n   pass', ast.f.src)

    def test__dedent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f._get_indentable_lns(1)
        ast.f._dedent_lns(' ', lns)
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\nif True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f._get_indentable_lns(1)
        ast.body[0].body[0].orelse[0].f._dedent_lns(' ', lns)
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.body[0].body[0].f._get_indentable_lns(1)
        ast.body[0].body[0].f._dedent_lns(' ', lns)
        self.assertEqual(set(), lns)
        self.assertEqual('@decorator\nclass cls:\n pass', ast.f.src)

        # ast = parse(src)
        # lns = ast.body[0].body[0].f._dedent_lns(' ', skip=0)
        # self.assertEqual({2}, lns)
        # self.assertEqual('@decorator\nclass cls:\npass', ast.f.src)

        # misc for coverage

        (f := FST('if 1:\n  pass'))._dedent_lns(None, {0, 1})
        self.assertEqual('if 1:\npass', f.src)

    def test__redent_lns(self):
        f = FST('''
[
a,
 b,
  c,
   d,
    e,
     f,
      g,

a,
 b,
  c,
   d,
    e,
     f,
      g,
]
            '''.strip())
        f._redent_lns('    ', '012')
        self.assertEqual('''
[
a,
b,
0c,
01d,
012e,
012 f,
012  g,

a,
b,
0c,
01d,
012e,
012 f,
012  g,
]
            '''.strip(), f.src)
        self.assertEqual((0, 0, 16, 1), f.loc)
        self.assertEqual((1, 0, 1, 1), f.elts[0].loc)
        self.assertEqual((2, 0, 2, 1), f.elts[1].loc)
        self.assertEqual((3, 1, 3, 2), f.elts[2].loc)
        self.assertEqual((4, 2, 4, 3), f.elts[3].loc)
        self.assertEqual((5, 3, 5, 4), f.elts[4].loc)
        self.assertEqual((6, 4, 6, 5), f.elts[5].loc)
        self.assertEqual((7, 5, 7, 6), f.elts[6].loc)
        self.assertEqual((9, 0, 9, 1), f.elts[7].loc)
        self.assertEqual((10, 0, 10, 1), f.elts[8].loc)
        self.assertEqual((11, 1, 11, 2), f.elts[9].loc)
        self.assertEqual((12, 2, 12, 3), f.elts[10].loc)
        self.assertEqual((13, 3, 13, 4), f.elts[11].loc)
        self.assertEqual((14, 4, 14, 5), f.elts[12].loc)
        self.assertEqual((15, 5, 15, 6), f.elts[13].loc)

        f = FST('''
    "OFFENDING RULE", self.ex.rule,
''')
        f.a.lineno = 1
        f.a.col_offset = f.a.end_col_offset = 0
        f.a.end_lineno = 3
        f._redent_lns('    ', ' ')
        self.assertEqual((0, 0, 2, 0), f.loc)
        self.assertEqual((1, 1, 1, 17), f.elts[0].loc)
        self.assertEqual((1, 19, 1, 31), f.elts[1].loc)
        self.assertEqual((1, 19, 1, 26), f.elts[1].value.loc)
        self.assertEqual((1, 19, 1, 23), f.elts[1].value.value.loc)

        # misc for coverage

        f = FST('if 1:\n  pass')
        f._redent_lns(None, None, {0, 1})
        self.assertEqual('if 1:\n  pass', f.src)
        f._redent_lns('  ', '    ', {})
        self.assertEqual('if 1:\n  pass', f.src)
        f._redent_lns('  ', '    ', {1})
        self.assertEqual('if 1:\n    pass', f.src)

        f = FST('if 1:\n    pass\n  # inconsistent')
        f._redent_lns('    ', ' ', {1, 2})
        self.assertEqual('if 1:\n pass\n# inconsistent', f.src)

    def test__put_src(self):
        f = FST(Load(), [''], None)
        f._put_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['test'])
        f._put_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['testtest'])
        f._put_src('tost', 0, 0, 0, 8)
        self.assertEqual(f.lines, ['tost'])
        f._put_src('a\nb\nc', 0, 2, 0, 2)
        self.assertEqual(f.lines, ['toa', 'b', 'cst'])
        f._put_src('', 0, 3, 2, 1)
        self.assertEqual(f.lines, ['toast'])
        f._put_src('a\nb\nc\nd', 0, 0, 0, 5)
        self.assertEqual(f.lines, ['a', 'b', 'c', 'd'])
        f._put_src('efg\nhij', 1, 0, 2, 1)
        self.assertEqual(f.lines, ['a', 'efg', 'hij', 'd'])
        f._put_src('***', 1, 2, 2, 1)
        self.assertEqual(f.lines, ['a', 'ef***ij', 'd'])

    def test__multiline_str_continuation_lns(self):
        from fst.fst_core import _multiline_str_continuation_lns as mscl

        self.assertEqual([], mscl(ls := r'''
'a'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
"a"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"""a
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"""a

b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
"a"
"b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "z" "c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" "z" "c\
b" """y"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" "z" "c\
b" """y
"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" "z" "c\
b" "x" """y
"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
"a" """c
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
"a" """c
b""" "d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3], mscl(ls := r'''
"a" """c
b"""
"d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3, 4], mscl(ls := r'''
"a" """c
b"""
"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
"a" """c
b"""

"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
b"a" b"""c
b"""

b"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
u"a" u"""c
b"""

u"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
r"a" r"""c
b"""

r"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([2], mscl(ls := r'''
'a' \
'b\
c' \
'd'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := [
            "r'<[a-zA-Z][-_.:a-zA-Z0-9]*\\s*('",
            "        r'\\s*([a-zA-Z_][-:.a-zA-Z_0-9]*)(\\s*=\\s*'",
            '        r\'(\\\'[^\\\']*\\\'|"[^"]*"|[-a-zA-Z0-9./,:;+*%?!&$\\(\\)_#=~@]\'',
            '        r\'[][\\-a-zA-Z0-9./,:;+*%?!&$\\(\\)_#=~\\\'"@]*(?=[\\s>/<])))?\'',
            "    r')*\\s*/?\\s*(?=[<>])'"], 0, 0, len(ls) - 1, len(ls[-1])))

        # coverage

        f = FST('''f"""{f'{1}'}\n"""''')
        self.assertEqual([1], mscl(f._lines, *f.whole_loc))

        f.put_src(None, 1, 0, 1, 3, 'offset')
        self.assertRaises(tokenize.TokenError, mscl, f._lines, *f.whole_loc)

    def test__multiline_ftstr_continuation_lns(self):
        from fst.fst_core import _multiline_ftstr_continuation_lns as mscl

        self.assertEqual([], mscl(ls := r'''
f'a'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
f"a"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"""a
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"""a

b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
f"a"
"b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a" f"c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a" f"""c
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"a" f"""c
b""" "d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3], mscl(ls := r'''
f"a" f"""c
b"""
f"d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3, 4], mscl(ls := r'''
f"a" f"""c
b"""
f"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
f"a" f"""c
b"""

f"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([2], mscl(ls := r'''
f'a' \
f'b\
c' \
f'd'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        # with values

        self.assertEqual([], mscl(ls := r'''
f"a{1}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
f"a{(1,)}"\
f"{(2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a{(1,)}\
{(2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"a{(1,)}\
{(2)}b""" f"c\
d"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3], mscl(ls := r'''
f"a{(1,)}\
{(2)}b" f"""{3}
{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,)}\
\
{(2)}b" f"""{3}

{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,)}\
\
{(2)}b" f"""{3}

{4}
{5}""" f"x"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5, 6], mscl(ls := r'''
f"a{(1,)}\
\
{(2)}b" f"""{3}

{4}
{5}""" f"x\
y"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

    @unittest.skipUnless(PYGE12, 'only valid for py >= 3.12')
    def test__multiline_ftstr_continuation_lns_pyge12(self):
        from fst.fst_core import _multiline_ftstr_continuation_lns as mscl

        self.assertEqual([1], mscl(ls := r'''
f"a{(1,
2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
f"a{(1,\
2)}b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
f"a{(1,\
2)}b""" f"c\
d"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3], mscl(ls := r'''
f"a{(1,
2)}b" f"""{3}
{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5, 6], mscl(ls := r'''
f"a{(1,

2)}b" f"""{3}

{4}
{5}""" f"x\
y"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

    @unittest.skipUnless(PYGE14, 'only valid for py >= 3.14')
    def test__multiline_tstr_continuation_lns(self):
        from fst.fst_core import _multiline_ftstr_continuation_lns as mscl

        self.assertEqual([], mscl(ls := r'''
t'a'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
t"a"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"""a
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
t"""a

b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([], mscl(ls := r'''
t"a"
"b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a" t"c\
b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a" t"""c
b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
t"a" t"""c
b""" "d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3], mscl(ls := r'''
t"a" t"""c
b"""
t"d\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 3, 4], mscl(ls := r'''
t"a" t"""c
b"""
t"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 4, 5], mscl(ls := r'''
t"a" t"""c
b"""

t"d\
\
e"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([2], mscl(ls := r'''
t'a' \
t'b\
c' \
t'd'
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        # with values

        self.assertEqual([], mscl(ls := r'''
t"a{1}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a{(1,
2)}b"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1], mscl(ls := r'''
t"a{(1,\
2)}b"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2], mscl(ls := r'''
t"a{(1,\
2)}b""" t"c\
d"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3], mscl(ls := r'''
t"a{(1,
2)}b" t"""{3}
{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}"""
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

        self.assertEqual([1, 2, 3, 4, 5, 6], mscl(ls := r'''
t"a{(1,

2)}b" t"""{3}

{4}
{5}""" t"x\
y"
            '''.strip().split('\n'), 0, 0, len(ls) - 1, len(ls[-1])))

    def test__modifying(self):
        # don't allow nested mofifying same tree

        f = FST('a, b')
        g = FST('c, d')

        with f.elts[0]._modifying():
            with g.elts[0]._modifying():
                pass

        with self.assertRaises(RuntimeError):
            with f.elts[0]._modifying():
                with f.elts[1]._modifying():
                    pass

        # for coverage

        f = FST('i = a, b')
        m = f.value.elts[0]._modifying()
        m.enter()
        f._set_ast(FST('i = a, b').a, True)
        m.success(f)

    def test___new__(self):
        f = FST()
        self.assertEqual('', f.src)
        self.assertIsInstance(f.a, Module)
        self.assertEqual([], f.a.body)

        f = FST('')
        self.assertEqual('', f.src)
        self.assertIsInstance(f.a, Module)
        self.assertEqual([], f.a.body)

        f = FST('', 'exec')
        self.assertEqual('', f.src)
        self.assertIsInstance(f.a, Module)
        self.assertEqual([], f.a.body)

        f = FST('i = 1', 'exec')
        self.assertEqual('i = 1', f.src)
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Assign)

        f = FST('i = 1', 'single')
        self.assertEqual('i = 1', f.src)
        self.assertIsInstance(f.a, Interactive)
        self.assertIsInstance(f.a.body[0], Assign)

        f = FST('i', 'eval')
        self.assertEqual('i', f.src)
        self.assertIsInstance(f.a, Expression)
        self.assertIsInstance(f.a.body, Name)

        v = PYVER
        f = FST.fromsrc('i', 'exec', filename='fnm', type_comments=True, feature_version=v)

        g = FST('j', 'exec', from_=f)
        self.assertEqual('fnm', g.parse_params['filename'])
        self.assertIs(True, g.parse_params['type_comments'])
        self.assertEqual(v, g.parse_params['feature_version'])

        g = FST('j', 'exec', from_=f, filename='blah', type_comments=False, feature_version=None)
        self.assertEqual('blah', g.parse_params['filename'])
        self.assertIs(False, g.parse_params['type_comments'])
        self.assertIs(None, g.parse_params['feature_version'])

        # full parse tests

        for mode, func, res, src in PARSE_TESTS:
            try:
                try:
                    fst = FST(src, mode)

                except (SyntaxError, NodeError) as exc:
                    if res is not exc.__class__:
                        raise

                else:
                    if issubclass(res, Exception):
                        raise RuntimeError(f'expected {res.__name__}')

                    ref = func(src)

                    self.assertEqual(src, fst.src)
                    self.assertEqual(fst.a.__class__, res)
                    self.assertTrue(compare_asts(fst.a, ref, locs=True, raise_=True))

            except Exception:
                print()
                print(f'{mode = }')
                print(f'{func = }')
                print(f'{res = }')
                print(f'{src = !r}')

                raise

    def test_fromast(self):
        a = ast_parse('i = 1', '', 'exec')

        self.assertEqual('i = 1', FST.fromast(a).src)
        self.assertEqual('i = 1', FST.fromast(a, 'exec').src)
        self.assertEqual('i = 1', FST.fromast(a.body[0]).src)
        self.assertEqual('i = 1', FST.fromast(a.body[0], 'exec').src)
        # self.assertRaises(ValueError, FST.fromast, a.body[0], 'exec')

        # just testing, don't use type_comments

        # a = ast_parse('i = 1  # type: int', '', 'exec', type_comments=True)

        # self.assertEqual('i = 1 # type: int', FST.fromast(a).src)
        # self.assertEqual('i = 1 # type: int', FST.fromast(a, 'exec').src)
        # self.assertEqual('i = 1 # type: int', FST.fromast(a, type_comments=True).src)
        # self.assertEqual('i = 1 # type: int', FST.fromast(a, 'exec', type_comments=True).src)
        # self.assertEqual('i = 1 # type: int', FST.fromast(a, type_comments=None).src)
        # self.assertEqual('i = 1 # type: int', FST.fromast(a, 'exec', type_comments=None).src)
        # self.assertEqual('i = 1 # type: int', FST.fromast(a.body[0], type_comments=True).src)
        # self.assertEqual('i = 1 # type: int', FST.fromast(a.body[0], 'exec', type_comments=True).src)
        # self.assertRaises(ValueError, FST.fromast, a.body[0], 'exec', type_comments=True)

        a = ast_parse('i = 1  # type: ignore', '', 'exec', type_comments=True)

        # self.assertRaises(ValueError, FST.fromast, a)
        # self.assertRaises(ValueError, FST.fromast, a, 'exec')
        # self.assertEqual('i = 1 # type: ignore', FST.fromast(a, 'exec').src)
        # self.assertEqual('i = 1 # type: ignore', FST.fromast(a, type_comments=True).src)
        # self.assertEqual('i = 1 # type: ignore', FST.fromast(a, 'exec', type_comments=True).src)
        # self.assertEqual('i = 1 # type: ignore', FST.fromast(a, type_comments=None).src)
        # self.assertEqual('i = 1 # type: ignore', FST.fromast(a, 'exec', type_comments=None).src)
        # self.assertEqual('i = 1', FST.fromast(a.body[0], type_comments=True).src)
        # self.assertEqual('i = 1', FST.fromast(a.body[0], 'exec', type_comments=True).src)
        # self.assertRaises(ValueError, FST.fromast, a.body[0], 'exec', type_comments=True)

        # TODO: more tests, explicit coerce with same source

    def test_infer_indent(self):
        self.assertEqual('    ', FST.fromsrc('def f(): pass').indent)
        self.assertEqual('  ', FST.fromsrc('def f():\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('async def f():\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('class cls:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('with a:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('async with a:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('for a in b:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('for a in b: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('for a in b:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST.fromsrc('async for a in b:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('async for a in b: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('async for a in b:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST.fromsrc('while a:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('while a: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('while a:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST.fromsrc('if 1:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('if 1: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('if 1:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST.fromsrc('match 1:\n  case 1: pass').indent)
        self.assertEqual('  ', FST.fromsrc('try:\n  pass\nexcept: pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept: pass\nelse: pass\nfinally:\n  pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept: pass\nelse:\n  pass\nfinally: pass').indent)
        self.assertEqual('  ', FST.fromsrc('try: pass\nexcept:\n  pass\nelse: pass\nfinally: pass').indent)
        self.assertEqual('  ', FST.fromsrc('try:\n  pass\nexcept: pass\nelse: pass\nfinally: pass').indent)

        self.assertEqual('    ', FST('def f(): pass').indent)
        self.assertEqual('  ', FST('def f():\n  pass').indent)
        self.assertEqual('  ', FST('async def f():\n  pass').indent)
        self.assertEqual('  ', FST('class cls:\n  pass').indent)
        self.assertEqual('  ', FST('with a:\n  pass').indent)
        self.assertEqual('  ', FST('async with a:\n  pass').indent)
        self.assertEqual('  ', FST('for a in b:\n  pass').indent)
        self.assertEqual('  ', FST('for a in b: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST('for a in b:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST('async for a in b:\n  pass').indent)
        self.assertEqual('  ', FST('async for a in b: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST('async for a in b:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST('while a:\n  pass').indent)
        self.assertEqual('  ', FST('while a: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST('while a:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST('if 1:\n  pass').indent)
        self.assertEqual('  ', FST('if 1: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST('if 1:\n  pass\nelse: pass').indent)
        self.assertEqual('  ', FST('match 1:\n  case 1: pass').indent)
        self.assertEqual('  ', FST('try:\n  pass\nexcept: pass').indent)
        self.assertEqual('  ', FST('try: pass\nexcept:\n  pass').indent)
        self.assertEqual('  ', FST('try: pass\nexcept: pass\nelse:\n  pass').indent)
        self.assertEqual('  ', FST('try: pass\nexcept: pass\nelse: pass\nfinally:\n  pass').indent)
        self.assertEqual('  ', FST('try: pass\nexcept: pass\nelse:\n  pass\nfinally: pass').indent)
        self.assertEqual('  ', FST('try: pass\nexcept:\n  pass\nelse: pass\nfinally: pass').indent)
        self.assertEqual('  ', FST('try:\n  pass\nexcept: pass\nelse: pass\nfinally: pass').indent)

        self.assertEqual('    ', FST('except: pass').indent)
        self.assertEqual('  ', FST('except:\n  pass').indent)
        self.assertEqual('    ', FST('except: pass', '_ExceptHandlers').indent)
        self.assertEqual('  ', FST('except:\n  pass', '_ExceptHandlers').indent)

        self.assertEqual('    ', FST('case 1: pass').indent)
        self.assertEqual('  ', FST('case 1:\n  pass').indent)
        self.assertEqual('    ', FST('case 1: pass', '_match_cases').indent)
        self.assertEqual('  ', FST('case 1:\n  pass', '_match_cases').indent)

        if PYGE12:
            self.assertEqual('  ', FST.fromsrc('try:\n  pass\nexcept* Exception: pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception:\n  pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception: pass\nelse:\n  pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception: pass\nelse: pass\nfinally:\n  pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception: pass\nelse:\n  pass\nfinally: pass').indent)
            self.assertEqual('  ', FST.fromsrc('try: pass\nexcept* Exception:\n  pass\nelse: pass\nfinally: pass').indent)
            self.assertEqual('  ', FST.fromsrc('try:\n  pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').indent)

            self.assertEqual('  ', FST('try:\n  pass\nexcept* Exception: pass').indent)
            self.assertEqual('  ', FST('try: pass\nexcept* Exception:\n  pass').indent)
            self.assertEqual('  ', FST('try: pass\nexcept* Exception: pass\nelse:\n  pass').indent)
            self.assertEqual('  ', FST('try: pass\nexcept* Exception: pass\nelse: pass\nfinally:\n  pass').indent)
            self.assertEqual('  ', FST('try: pass\nexcept* Exception: pass\nelse:\n  pass\nfinally: pass').indent)
            self.assertEqual('  ', FST('try: pass\nexcept* Exception:\n  pass\nelse: pass\nfinally: pass').indent)
            self.assertEqual('  ', FST('try:\n  pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').indent)

            self.assertEqual('    ', FST('except* Exception: pass').indent)
            self.assertEqual('  ', FST('except* Exception:\n  pass').indent)
            self.assertEqual('    ', FST('except* Exception: pass', '_ExceptHandlers').indent)
            self.assertEqual('  ', FST('except* Exception:\n  pass', '_ExceptHandlers').indent)

    def test_unmake_fst_in_operations(self):
        # basic, more comprehensive in one and slice tests

        f = parse('(1, 2, 3)').f
        g = parse('(4, 5)').f
        i = f.body[0].value.elts[1]
        h = g.body[0]
        f.body[0].value.put_slice(g, 1, 2)
        self.assertEqual('(1, 4, 5, 3)', f.src)
        self.assertIsNone(i.a)
        self.assertIsNone(h.a)
        self.assertIsNone(g.a)

        f = parse('[1, 2, 3]').f
        g = parse('[4, 5]').f
        i = f.body[0].value.elts[1]
        h = g.body[0]
        f.body[0].value.put_slice(g, 1, 2)
        self.assertEqual('[1, 4, 5, 3]', f.src)
        self.assertIsNone(i.a)
        self.assertIsNone(h.a)
        self.assertIsNone(g.a)

        f = parse('{1, 2, 3}').f
        g = parse('{4, 5}').f
        i = f.body[0].value.elts[1]
        h = g.body[0]
        f.body[0].value.put_slice(g, 1, 2)
        self.assertEqual('{1, 4, 5, 3}', f.src)
        self.assertIsNone(i.a)
        self.assertIsNone(h.a)
        self.assertIsNone(g.a)

        f = parse('{1:1, 1:1, 3:3}').f
        g = parse('{4:4, 5:5}').f
        ik = f.body[0].value.keys[1]
        iv = f.body[0].value.values[1]
        h = g.body[0]
        f.body[0].value.put_slice(g, 1, 2)
        self.assertEqual('{1:1, 4:4, 5:5, 3:3}', f.src)
        self.assertIsNone(ik.a)
        self.assertIsNone(iv.a)
        self.assertIsNone(h.a)
        self.assertIsNone(g.a)

    def test_src_and_lines(self):
        self.assertEqual('and', FST('a and b').op.src)
        self.assertEqual('or', FST('a or b').op.src)
        self.assertEqual(['and'], FST('a and b').op.lines)
        self.assertEqual(['or'], FST('a or b').op.lines)

        f = FST('# 0\na = b\n# 1')
        self.assertEqual('# 0\na = b\n# 1', f.src)
        self.assertEqual(['# 0', 'a = b', '# 1'], f.lines)
        self.assertEqual('a = b', f.get_src(*f.loc))
        self.assertEqual(['a = b'], f.get_src(*f.loc, as_lines=True))

        f = FST('if 1:\n  if 2: pass  # line')
        self.assertEqual('if 2: pass  # line', f.body[0].src)
        self.assertEqual(['  if 2: pass  # line'], f.body[0].lines)
        self.assertEqual('pass', f.body[0].body[0].src)
        self.assertEqual(['  if 2: pass  # line'], f.body[0].body[0].lines)

    def test_loc(self):
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.loc)  # arguments
        self.assertEqual((0, 5, 0, 8), parse('with f(): pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((1, 2, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.loc)  # match_case
        self.assertEqual((0, 3, 0, 25), parse('[i for i in range(5) if i]').body[0].value.generators[0].f.loc)  # comprehension
        self.assertEqual((0, 3, 0, 25), parse('(i for i in range(5) if i)').body[0].value.generators[0].f.loc)  # comprehension

        self.assertEqual((0, 5, 0, 12), parse('with ( f() ): pass').body[0].items[0].f.loc)  # withitem only context_expr w/ parens
        self.assertEqual((0, 5, 0, 21), parse('with ( f() ) as ( f ): pass').body[0].items[0].f.loc)  # withitem w/ parens
        self.assertEqual((1, 2, 1, 28), parse('match a:\n  case ( 2 ) if a == 1: pass').body[0].cases[0].f.loc)  # match_case w/ parens
        self.assertEqual((0, 3, 0, 33), parse('[i for ( i ) in range(5) if ( i ) ]').body[0].value.generators[0].f.loc)  # comprehension w/ parens
        self.assertEqual((0, 3, 0, 33), parse('(i for ( i ) in range(5) if ( i ) )').body[0].value.generators[0].f.loc)  # comprehension w/ parens

        self.assertEqual('f() as ( f )', parse('with f() as ( f ): pass').body[0].items[0].f.src)
        self.assertEqual('( f() ) as f', parse('with ( f() ) as f: pass').body[0].items[0].f.src)
        self.assertEqual('( f() ) as ( f )', parse('with ( f() ) as ( f ): pass').body[0].items[0].f.src)
        self.assertEqual('( f() ) as ( f )', parse('with ( f() ) as ( f ), ( g() ) as ( g ): pass').body[0].items[0].f.src)
        self.assertEqual('( g() ) as ( g )', parse('with ( f() ) as ( f ), ( g() ) as ( g ): pass').body[0].items[1].f.src)
        self.assertEqual('( f() )', parse('with ( f() ): pass').body[0].items[0].f.src)
        self.assertEqual('a as b', parse('with (a as b): pass').body[0].items[0].f.src)
        self.assertEqual('a as b', parse('with (a as b, c as d): pass').body[0].items[0].f.src)
        self.assertEqual('c as d', parse('with (a as b, c as d): pass').body[0].items[1].f.src)
        self.assertEqual('c as d', parse('with (a as b, c as d, e as f): pass').body[0].items[1].f.src)
        self.assertEqual('e as f', parse('with (a as b, c as d, e as f): pass').body[0].items[2].f.src)

        self.assertEqual('case 1: pass', parse('match a:\n  case 1: pass').body[0].cases[0].f.src)
        self.assertEqual('case (1 | 2): pass', parse('match a:\n  case (1 | 2): pass').body[0].cases[0].f.src)
        self.assertEqual('case ( 2 ) if a == 1: pass', parse('match a:\n  case ( 2 ) if a == 1: pass').body[0].cases[0].f.src)

        self.assertEqual('for ( i ) in range(5) if ( i )', parse('[ ( i ) for ( i ) in range(5) if ( i ) ]').body[0].value.generators[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('( ( i ) for ( i ) in range(5) if ( i ) )').body[0].value.generators[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('[ ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) ]').body[0].value.generators[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('( ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) )').body[0].value.generators[0].f.src)
        self.assertEqual('for ( j ) in range(6) if ( j )', parse('[ ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) ]').body[0].value.generators[1].f.src)
        self.assertEqual('for ( j ) in range(6) if ( j )', parse('( ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) )').body[0].value.generators[1].f.src)

        self.assertEqual('', parse('def f(): pass').body[0].args.f.src)
        self.assertEqual('a', parse('def f(a): pass').body[0].args.f.src)
        self.assertEqual(' a ', parse('def f( a ): pass').body[0].args.f.src)
        self.assertEqual('', parse('lambda: None').body[0].value.args.f.src)
        self.assertEqual('a = ( 1 ) ', parse('lambda a = ( 1 ) : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = 2', parse('lambda *, z, a, b = 2: None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = 2 ', parse('lambda *, z, a, b = 2 : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 )', parse('lambda *, z, a, b = ( 2 ): None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 ) ', parse('lambda *, z, a, b = ( 2 ) : None').body[0].value.args.f.src)
        self.assertEqual('*s, a, b = ( 2 ) ', parse('lambda *s, a, b = ( 2 ) : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 ),', parse('lambda *, z, a, b = ( 2 ),: None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 ), ', parse('lambda *, z, a, b = ( 2 ), : None').body[0].value.args.f.src)
        self.assertEqual('**ss ', parse('lambda **ss : None').body[0].value.args.f.src)
        self.assertEqual('a, /', parse('lambda a, /: None').body[0].value.args.f.src)
        self.assertEqual(' a, / ', parse('lambda  a, / : None').body[0].value.args.f.src)
        self.assertEqual('a, /, ', parse('lambda a, /, : None').body[0].value.args.f.src)
        self.assertEqual(' a, / , ', parse('lambda  a, / , : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = 2', parse('def f(*, z, a, b = 2): pass').body[0].args.f.src)
        self.assertEqual('*, z, a, b = ( 2 )', parse('def f(*, z, a, b = ( 2 )): pass').body[0].args.f.src)
        self.assertEqual(' *, z, a, b = ( 2 ) ', parse('def f( *, z, a, b = ( 2 ) ): pass').body[0].args.f.src)
        self.assertEqual(' *s, a, b = ( 2 ) ', parse('def f( *s, a, b = ( 2 ) ): pass').body[0].args.f.src)
        self.assertEqual(' *, z, a, b = ( 2 ), ', parse('def f( *, z, a, b = ( 2 ), ): pass').body[0].args.f.src)
        self.assertEqual(' **ss ', parse('def f( **ss ): pass').body[0].args.f.src)
        self.assertEqual('a, /', parse('def f(a, /): pass').body[0].args.f.src)
        self.assertEqual(' a, / ', parse('def f( a, / ): pass').body[0].args.f.src)
        self.assertEqual('a, /,', parse('def f(a, /,): pass').body[0].args.f.src)
        self.assertEqual('a, / , ', parse('def f(a, / , ): pass').body[0].args.f.src)

        # loc calculated from children at root

        self.assertEqual((0, 0, 0, 12), parse('match a:\n case 1: pass').body[0].cases[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 6), parse('with a as b: pass').body[0].items[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 1), parse('def f(a): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 1), parse('lambda a: None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 10), parse('[i for i in j]').body[0].value.generators[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 15), parse('[i for i in j if k]').body[0].value.generators[0].f.copy().loc)

        self.assertEqual((0, 0, 0, 10), parse('lambda a = ( 1 ) : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 14), parse('lambda *, z, a, b = 2: None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 15), parse('lambda *, z, a, b = 2 : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 18), parse('lambda *, z, a, b = ( 2 ): None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 19), parse('lambda *, z, a, b = ( 2 ) : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 17), parse('lambda *s, a, b = ( 2 ) : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 19), parse('lambda *, z, a, b = ( 2 ),: None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 20), parse('lambda *, z, a, b = ( 2 ), : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 5), parse('lambda **ss : None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 14), parse('def f(*, z, a, b = 2): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 18), parse('def f(*, z, a, b = ( 2 )): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 20), parse('def f( *, z, a, b = ( 2 ) ): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 18), parse('def f( *s, a, b = ( 2 ) ): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 21), parse('def f( *, z, a, b = ( 2 ), ): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 6), parse('def f( **ss ): pass').body[0].args.f.copy().loc)

        # special cases

        self.assertEqual((0, 12, 0, 14), FST('f"a{(lambda *a: b)}"', 'exec').body[0].value.values[1].value.args.loc)

    def test_bloc(self):
        # decorators

        ast = parse('@deco\nclass cls:\n @deco\n def meth():\n  @deco\n  class fcls: pass')

        self.assertEqual((0, 0, 5, 18), ast.f.loc)
        self.assertEqual((0, 0, 5, 18), ast.f.bloc)
        self.assertEqual((1, 0, 5, 18), ast.body[0].f.loc)
        self.assertEqual((0, 0, 5, 18), ast.body[0].f.bloc)
        self.assertEqual((3, 1, 5, 18), ast.body[0].body[0].f.loc)
        self.assertEqual((2, 1, 5, 18), ast.body[0].body[0].f.bloc)
        self.assertEqual((5, 2, 5, 18), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((4, 2, 5, 18), ast.body[0].body[0].body[0].f.bloc)

        self.assertEqual((2, 1, 3, 15), f := FST(r'''
if 1:
  \
 @deco
  def f(): pass
'''.strip()).body[0].bloc)
        self.assertEqual(2, f.bln)
        self.assertEqual(1, f.bcol)
        self.assertEqual(3, f.bend_ln)
        self.assertEqual(15, f.bend_col)

        self.assertEqual((2, 0, 3, 19), f := FST(r'''
if 1:
      \
@real#@fake
      def f(): pass
'''.strip()).body[0].bloc)
        self.assertEqual(2, f.bln)
        self.assertEqual(0, f.bcol)
        self.assertEqual(3, f.bend_ln)
        self.assertEqual(19, f.bend_col)

        # trailing comment

        f = FST('if 1:\n  pass  # line', 'exec').body[0]
        self.assertEqual((0, 0, 1, 6), f.loc)
        self.assertEqual((0, 0, 1, 14), f.bloc)

        f = FST('if 1: pass  # line', 'exec').body[0]
        self.assertEqual((0, 0, 0, 10), f.loc)
        self.assertEqual((0, 0, 0, 18), f.bloc)

        f = FST('if 1:  # line\n  pass', 'exec').body[0]
        del f.body[0]
        self.assertEqual('if 1:  # line', f.src)
        self.assertEqual((0, 0, 0, 5), f.loc)
        self.assertEqual((0, 0, 0, 13), f.bloc)

    def test_fromast_special(self):
        f = FST.fromast(ast_parse('*t').body[0].value)
        self.assertEqual('*t', f.src)
        self.assertIsInstance(f.a, Starred)

    def test_dump(self):
        f = FST('a = b ; ')
        f.value.put_src(' b ', 0, 4, 0, 5, 'offset')
        self.assertEqual(f.dump('node', list_indent=2, out='lines'), [
            '0: a =  b  ;',
            'Assign - ROOT 0,0..0,7',
            '  .targets[1]',
            '0: a',
            "    0] Name 'a' Store - 0,0..0,1",
            '0: ---> b <*END*',
            "  .value Name 'b' Load - 0,4..0,7",
        ])

        f = FST('call() ;', 'exec')
        self.assertEqual(f.dump('node', loc=False, out='lines'), [
            'Module - ROOT',
            '  .body[1]',
            '0: call() ;',
            '   0] Expr',
            '     .value Call',
            '0: call',
            "       .func Name 'call' Load",
        ])

        f = FST('''
if 1:  # 1
  a  # 2
  b ;
  c ;  # 3
            '''.strip())
        self.assertEqual(f.dump('stmt', out='lines'), [
            "0: if 1:  # 1",
            "If - ROOT 0,0..3,5",
            "  .test Constant 1 - 0,3..0,4",
            "  .body[3]",
            "1:   a  # 2",
            "   0] Expr - 1,2..1,3",
            "     .value Name 'a' Load - 1,2..1,3",
            "2:   b ;",
            "   1] Expr - 2,2..2,3",
            "     .value Name 'b' Load - 2,2..2,3",
            "3:   c ;  # 3",
            "   2] Expr - 3,2..3,3",
            "     .value Name 'c' Load - 3,2..3,3",
        ])

        # src_plus

        f = FST('# 1\nif a:\n  # 2\n  pass\n  # 3\n# 4', 'exec')
        self.assertEqual(f.dump('stmt', out='lines'), [
            'Module - ROOT 0,0..5,3',
            '  .body[1]',
            '1: if a:',
            '   0] If - 1,0..3,6',
            "     .test Name 'a' Load - 1,3..1,4",
            '     .body[1]',
            '3:   pass',
            '      0] Pass - 3,2..3,6'
        ])
        self.assertEqual(f.dump('stmt+', out='lines'), [
            'Module - ROOT 0,0..5,3',
            '  .body[1]',
            '0: # 1',
            '1: if a:',
            '   0] If - 1,0..3,6',
            "     .test Name 'a' Load - 1,3..1,4",
            '     .body[1]',
            '2:   # 2',
            '3:   pass',
            '      0] Pass - 3,2..3,6',
            '4:   # 3',
            '5: # 4'
        ])
        self.assertEqual(f.body[0].dump('stmt', out='lines'), [
            '1: if a:',
            'If - 1,0..3,6',
            "  .test Name 'a' Load - 1,3..1,4",
            '  .body[1]',
            '3:   pass',
            '   0] Pass - 3,2..3,6'
        ])
        self.assertEqual(f.body[0].dump('stmt+', out='lines'), [
            '1: if a:',
            'If - 1,0..3,6',
            "  .test Name 'a' Load - 1,3..1,4",
            '  .body[1]',
            '2:   # 2',
            '3:   pass',
            '   0] Pass - 3,2..3,6'
        ])
        self.assertEqual(f.body[0].body[0].dump('stmt', out='lines'), [
            '3:   pass',
            'Pass - 3,2..3,6'
        ])
        self.assertEqual(f.body[0].body[0].dump('stmt+', out='lines'), [
            '3:   pass',
            'Pass - 3,2..3,6'
        ])

        f = FST('# 1\nif a:\n  # 2\n  pass\n  # 3\n# 4', 'exec')
        self.assertEqual(f.dump('node', out='lines'), [
            'Module - ROOT 0,0..5,3',
            '  .body[1]',
            '1: if a:',
            '   0] If - 1,0..3,6',
            '1:    a',
            "     .test Name 'a' Load - 1,3..1,4",
            '     .body[1]',
            '3:   pass',
            '      0] Pass - 3,2..3,6'
        ])
        self.assertEqual(f.dump('node+', out='lines'), [
            'Module - ROOT 0,0..5,3',
            '  .body[1]',
            '0: # 1',
            '1: if a:',
            '   0] If - 1,0..3,6',
            '1:    a',
            "     .test Name 'a' Load - 1,3..1,4",
            '     .body[1]',
            '2:   # 2',
            '3:   pass',
            '      0] Pass - 3,2..3,6',
            '4:   # 3',
            '5: # 4'
        ])
        self.assertEqual(f.body[0].dump('node', out='lines'), [
            '1: if a:',
            'If - 1,0..3,6',
            '1:    a',
            "  .test Name 'a' Load - 1,3..1,4",
            '  .body[1]',
            '3:   pass',
            '   0] Pass - 3,2..3,6'
        ])
        self.assertEqual(f.body[0].dump('node+', out='lines'), [
            '1: if a:',
            'If - 1,0..3,6',
            '1:    a',
            "  .test Name 'a' Load - 1,3..1,4",
            '  .body[1]',
            '2:   # 2',
            '3:   pass',
            '   0] Pass - 3,2..3,6'
        ])
        self.assertEqual(f.body[0].body[0].dump('node', out='lines'), [
            '3:   pass',
            'Pass - 3,2..3,6'
        ])
        self.assertEqual(f.body[0].body[0].dump('node+', out='lines'), [
            '3:   pass',
            'Pass - 3,2..3,6'
        ])

        f = FST(r'''
def f():
    """.................................................................................
    ................................................................................
    ................................................................................"""
    pass
'''.strip())
        self.assertEqual(f.dump(out='lines'), [
            "FunctionDef - ROOT 0,0..4,8",
            "  .name 'f'",
            "  .body[2]",
            "   0] Expr - 1,4..3,87",
            "     .value Constant - 1,4..3,87",
            "       '.................................................................................\\n'",
            "       '    ................................................................................\\n'",
            "       '    ................................................................................'",
            "   1] Pass - 4,4..4,8",
        ])
        self.assertEqual(f.dump(expand=True, out='lines'), [
            "FunctionDef - ROOT 0,0..4,8",
            "  .name",
            "    'f'",
            "  .args",
            "    arguments - 0,6..0,6",
            "  .body[2]",
            "   0] Expr - 1,4..3,87",
            "     .value",
            "       Constant - 1,4..3,87",
            "         .value",
            "           '.................................................................................\\n'",
            "           '    ................................................................................\\n'",
            "           '    ................................................................................'",
            "   1] Pass - 4,4..4,8",
        ])

        f = FST('#!/usr/bin/env python\n\ni = 1')
        self.assertEqual([
            'Assign - ROOT 2,0..2,5',
            '  .targets[1]',
            "   0] Name 'i' Store - 2,0..2,1",
            '  .value Constant 1 - 2,4..2,5',
        ], f.dump(out='lines'))
        self.assertEqual([
            '2: i = 1',
            'Assign - ROOT 2,0..2,5',
            '  .targets[1]',
            "   0] Name 'i' Store - 2,0..2,1",
            '  .value Constant 1 - 2,4..2,5',
        ], f.dump('s', out='lines'))
        self.assertEqual([
            '0: #!/usr/bin/env python',
            '1:',
            '2: i = 1',
            'Assign - ROOT 2,0..2,5',
            '  .targets[1]',
            "   0] Name 'i' Store - 2,0..2,1",
            '  .value Constant 1 - 2,4..2,5',
        ], f.dump('S', out='lines'))
        self.assertEqual([
            '2: i = 1',
            'Assign - ROOT 2,0..2,5',
            '  .targets[1]',
            '2: i',
            "   0] Name 'i' Store - 2,0..2,1",
            '2:     1',
            '  .value Constant 1 - 2,4..2,5',
        ], f.dump('n', out='lines'))
        self.assertEqual([
            '0: #!/usr/bin/env python',
            '1:',
            '2: i = 1',
            'Assign - ROOT 2,0..2,5',
            '  .targets[1]',
            '2: i',
            "   0] Name 'i' Store - 2,0..2,1",
            '2:     1',
            '  .value Constant 1 - 2,4..2,5',
        ], f.dump('N', out='lines'))

        fp = StringIO()
        f.dump(out=fp)
        self.assertEqual("Assign - ROOT 2,0..2,5\n  .targets[1]\n   0] Name 'i' Store - 2,0..2,1\n  .value Constant 1 - 2,4..2,5\n", fp.getvalue())

        f = FST('None')
        self.assertEqual('Constant None - ROOT 0,0..0,4', f.dump(color=False, out='str'))
        self.assertEqual('\x1b[1;34mConstant\x1b[0m \x1b[1;36mNone\x1b[0m \x1b[90m- ROOT 0,0..0,4\x1b[0m', f.dump(color=True, out='str'))

        # line tails

        self.assertEqual([
            'Module - ROOT 0,0..0,16',
            '  .body[3]',
            '0: a ;',
            '   0] Expr - 0,0..0,1',
            "     .value Name 'a' Load - 0,0..0,1",
            '0:     b ;',
            '   1] Expr - 0,4..0,5',
            "     .value Name 'b' Load - 0,4..0,5",
            '0:         c  # end',
            '   2] Expr - 0,8..0,9',
            "     .value Name 'c' Load - 0,8..0,9",
        ], FST('a ; b ; c  # end').dump('s', out='lines'))

        self.assertEqual([
            'Module - ROOT 0,0..0,16',
            '  .body[3]',
            '0: a ;',
            '   0] Expr - 0,0..0,1',
            "     .value Name 'a' Load - 0,0..0,1",
            '0:     b ;',
            '   1] Expr - 0,4..0,5',
            "     .value Name 'b' Load - 0,4..0,5",
            '0:         c  # end',
            '   2] Expr - 0,8..0,9',
            "     .value Name 'c' Load - 0,8..0,9",
        ], FST('a ; b ; c  # end').dump('S', out='lines'))

        self.assertEqual([
            '0: if 1:',
            'If - ROOT 0,0..0,17',
            '  .test Constant 1 - 0,3..0,4',
            '  .body[2]',
            '0:       pass ;',
            '   0] Pass - 0,6..0,10',
            '0:              pass  # end',
            '   1] Pass - 0,13..0,17',
        ], FST('if 1: pass ; pass  # end').dump('s', out='lines'))

        self.assertEqual([
            '0: if 1:',
            'If - ROOT 0,0..0,17',
            '0:    1',
            '  .test Constant 1 - 0,3..0,4',
            '  .body[2]',
            '0:       pass ;',
            '   0] Pass - 0,6..0,10',
            '0:              pass  # end',
            '   1] Pass - 0,13..0,17',
        ], FST('if 1: pass ; pass  # end').dump('n', out='lines'))

        self.assertEqual([
            '0: if 1:',
            'If - ROOT 0,0..0,17',
            '0:    1',
            '  .test Constant 1 - 0,3..0,4',
            '  .body[2]',
            '0:       pass ;',
            '   0] Pass - 0,6..0,10',
            '0:              pass  # end',
            '   1] Pass - 0,13..0,17',
        ], FST('if 1: pass ; pass  # end').dump('N', out='lines'))

        # `else` and `finally`

        self.assertEqual([
            '0: try:',
            'Try - ROOT 0,0..5,3',
            '  .body[1]',
            '0:      a',
            '   0] Expr - 0,5..0,6',
            "     .value Name 'a' Load - 0,5..0,6",
            '  .handlers[1]',
            '1: except:',
            '   0] ExceptHandler - 1,0..1,9',
            '     .body[1]',
            '1:         b',
            '      0] Expr - 1,8..1,9',
            "        .value Name 'b' Load - 1,8..1,9",
            '2: else:',
            '  .orelse[1]',
            '3:   c',
            '   0] Expr - 3,2..3,3',
            "     .value Name 'c' Load - 3,2..3,3",
            '4: finally:',
            '  .finalbody[1]',
            '5:   d',
            '   0] Expr - 5,2..5,3',
            "     .value Name 'd' Load - 5,2..5,3",
        ], FST('try: a\nexcept: b\nelse:\n  c\nfinally:\n  d').dump('S', out='lines'))

        self.assertEqual([
            '0: try:',
            'Try - ROOT 0,0..3,10',
            '  .body[1]',
            '0:      a',
            '   0] Expr - 0,5..0,6',
            "     .value Name 'a' Load - 0,5..0,6",
            '  .handlers[1]',
            '1: except:',
            '   0] ExceptHandler - 1,0..1,9',
            '     .body[1]',
            '1:         b',
            '      0] Expr - 1,8..1,9',
            "        .value Name 'b' Load - 1,8..1,9",
            '2: else:',
            '  .orelse[1]',
            '2:       c',
            '   0] Expr - 2,6..2,7',
            "     .value Name 'c' Load - 2,6..2,7",
            '3: finally:',
            '  .finalbody[1]',
            '3:          d',
            '   0] Expr - 3,9..3,10',
            "     .value Name 'd' Load - 3,9..3,10",
        ], FST('try: a\nexcept: b\nelse: c\nfinally: d').dump('S', out='lines'))

        self.assertEqual([
            '0: if 1:',
            'If - ROOT 0,0..2,6',
            '  .test Constant 1 - 0,3..0,4',
            '  .body[1]',
            '0:       pass',
            '   0] Pass - 0,6..0,10',
            '  .orelse[1]',
            '1: elif 2:',
            '   0] If - 1,0..2,6',
            '     .test Constant 2 - 1,5..1,6',
            '     .body[1]',
            '2:   pass',
            '      0] Pass - 2,2..2,6',
        ], FST('if 1: pass\nelif 2:\n  pass').dump('S', out='lines'))

        self.assertEqual([
            '0: if 1:',
            'If - ROOT 0,0..1,12',
            '  .test Constant 1 - 0,3..0,4',
            '  .body[1]',
            '0:       pass',
            '   0] Pass - 0,6..0,10',
            '  .orelse[1]',
            '1: elif 2:',
            '   0] If - 1,0..1,12',
            '     .test Constant 2 - 1,5..1,6',
            '     .body[1]',
            '1:         pass',
            '      0] Pass - 1,8..1,12',
        ], FST('if 1: pass\nelif 2: pass').dump('S', out='lines'))

    def test_verify(self):
        ast = parse('i = 1')
        ast.f.verify(raise_=True)

        ast.body[0].lineno = 100

        self.assertRaises(WalkFail, ast.f.verify, raise_=True)
        self.assertEqual(None, ast.f.verify(raise_=False))

        for mode, func, res, src in PARSE_TESTS:
            try:
                if issubclass(res, Exception) or (isinstance(mode, str) and mode.startswith('_')):
                    continue

                fst = FST(src, mode)

                fst.verify(mode)
                fst.verify()

                if isinstance(a := fst.a, Expression):
                    a = a.body

                elif isinstance(a, (Module, Interactive)):
                    if not a.body:
                        continue

                    a = a.body[0]

                if end_col_offset := getattr(a, 'end_col_offset', None):
                    a.end_col_offset = end_col_offset + 1

                    self.assertFalse(fst.verify(mode, raise_=False))

            except Exception:
                print()
                print(mode, src, res, func)

                raise

        f = FST('a = b')

        self.assertRaises(ValueError, f.value.verify)

        self.assertIs(f, f.verify(raise_=False))
        f.value.parent = None
        self.assertIsNone(f.verify(raise_=False))
        self.assertRaises(WalkFail, f.verify)

        f = FST('a = b')
        f.put_src(None, 0, 4, 0, 5, None)

        self.assertIsNone(f.verify(raise_=False))
        self.assertRaises(SyntaxError, f.verify)

    def test_reparse(self):
        a = (f := FST('# pre\nstmt  # line\n# post', 'stmt')).a
        g = f.reparse()
        self.assertIs(g, f)
        self.assertIsNot(g.a, a)
        self.assertEqual('# pre\nstmt  # line\n# post', g.src)

        a = (f := FST('# pre\nand  # line\n# post', 'And')).a
        g = f.reparse()
        self.assertIs(g, f)
        self.assertIsNot(g.a, a)
        self.assertEqual('# pre\nand  # line\n# post', g.src)

        a = (f := FST('# pre\n  # line\n# post', 'Load')).a
        g = f.reparse()
        self.assertIs(g, f)
        self.assertIsNot(g.a, a)
        self.assertEqual('# pre\n  # line\n# post', g.src)

        f = FST('a\nb\nc')
        fa = old_fa = (old_aa := f.a.body[0]).f
        fb = old_fb = (old_ab := f.a.body[1]).f
        fc = old_fc = (old_ac := f.a.body[2]).f

        fa.put_src('new_a', *fa.loc, 'offset')
        fa = fa.reparse()
        self.assertIs(fa, old_fa)
        self.assertIsNot(fa.a, old_aa)
        self.assertIs(fb, old_fb)
        self.assertIs(fb.a, old_ab)
        self.assertIs(fc, old_fc)
        self.assertIs(fc.a, old_ac)
        old_aa = fa.a

        fc.put_src('new_c', *fc.loc, 'offset')
        fc = fc.reparse()
        self.assertIs(fc, old_fc)
        self.assertIsNot(fc.a, old_aa)
        self.assertIs(fa, old_fa)
        self.assertIs(fa.a, old_aa)
        self.assertIs(fb, old_fb)
        self.assertIs(fb.a, old_ab)
        old_ac = fc.a

        fb.put_src('new_b', *fb.loc, 'offset')
        fb = fb.reparse()
        self.assertIs(fb, old_fb)
        self.assertIsNot(fb.a, old_aa)
        self.assertIs(fa, old_fa)
        self.assertIs(fa.a, old_aa)
        self.assertIs(fc, old_fc)
        self.assertIs(fc.a, old_ac)
        old_ac = fb.a

        a = f.a
        f = f.reparse()
        self.assertIsNot(f.a, a)
        self.assertIsNot(f.body[0], old_fa)
        self.assertIsNot(f.body[0].a, old_aa)
        self.assertIsNot(f.body[1], old_fb)
        self.assertIsNot(f.body[1].a, old_aa)
        self.assertIsNot(f.body[2], old_fc)
        self.assertIsNot(f.body[2].a, old_ac)

        self.assertEqual(f.dump('stmt', out='lines'), [
            'Module - ROOT 0,0..2,5',
            '  .body[3]',
            '0: new_a',
            '   0] Expr - 0,0..0,5',
            "     .value Name 'new_a' Load - 0,0..0,5",
            '1: new_b',
            '   1] Expr - 1,0..1,5',
            "     .value Name 'new_b' Load - 1,0..1,5",
            '2: new_c',
            '   2] Expr - 2,0..2,5',
            "     .value Name 'new_c' Load - 2,0..2,5",
        ])

        if PYGE12:
            f = FST('a\nf"a{b}c"\nc')
            fa = old_fa = (old_aa := f.a.body[0]).f
            fb = old_fb = (old_ab := f.a.body[1]).f
            fc = old_fc = (old_ac := f.a.body[2]).f

            self.assertEqual(f.dump('stmt', out='lines'), [
                'Module - ROOT 0,0..2,1',
                '  .body[3]',
                '0: a',
                '   0] Expr - 0,0..0,1',
                "     .value Name 'a' Load - 0,0..0,1",
                '1: f"a{b}c"',
                '   1] Expr - 1,0..1,8',
                '     .value JoinedStr - 1,0..1,8',
                '       .values[3]',
                "        0] Constant 'a' - 1,2..1,3",
                '        1] FormattedValue - 1,3..1,6',
                "          .value Name 'b' Load - 1,4..1,5",
                '          .conversion -1',
                "        2] Constant 'c' - 1,6..1,7",
                '2: c',
                '   2] Expr - 2,0..2,1',
                "     .value Name 'c' Load - 2,0..2,1",
            ])

            fa.put_src('new_a', *fa.loc, 'offset')
            fa = fa.reparse()
            self.assertIs(fa, old_fa)
            self.assertIsNot(fa.a, old_aa)
            self.assertIs(fb, old_fb)
            self.assertIs(fb.a, old_ab)
            self.assertIs(fc, old_fc)
            self.assertIs(fc.a, old_ac)
            old_aa = fa.a

            fc.put_src('new_c', *fc.loc, 'offset')
            fc = fc.reparse()
            self.assertIs(fc, old_fc)
            self.assertIsNot(fc.a, old_aa)
            self.assertIs(fa, old_fa)
            self.assertIs(fa.a, old_aa)
            self.assertIs(fb, old_fb)
            self.assertIs(fb.a, old_ab)
            old_ac = fc.a

            fb.value.values[1].put_src('=', 1, 5, 1, 5, 'offset')

            self.assertEqual(f.dump('stmt', out='lines'), [
                'Module - ROOT 0,0..2,5',
                '  .body[3]',
                '0: new_a',
                '   0] Expr - 0,0..0,5',
                "     .value Name 'new_a' Load - 0,0..0,5",
                '1: f"a{b=}c"',
                '   1] Expr - 1,0..1,9',
                '     .value JoinedStr - 1,0..1,9',
                '       .values[3]',
                "        0] Constant 'a' - 1,2..1,3",
                '        1] FormattedValue - 1,3..1,7',
                "          .value Name 'b' Load - 1,4..1,5",
                '          .conversion -1',
                "        2] Constant 'c' - 1,7..1,8",
                '2: new_c',
                '   2] Expr - 2,0..2,5',
                "     .value Name 'new_c' Load - 2,0..2,5",
            ])

            fb = fb.reparse()
            self.assertIs(fb, old_fb)
            self.assertIsNot(fb.a, old_aa)
            self.assertIs(fa, old_fa)
            self.assertIs(fa.a, old_aa)
            self.assertIs(fc, old_fc)
            self.assertIs(fc.a, old_ac)
            old_ac = fb.a

            self.assertEqual(f.dump('stmt', out='lines'), [
                'Module - ROOT 0,0..2,5',
                '  .body[3]',
                '0: new_a',
                '   0] Expr - 0,0..0,5',
                "     .value Name 'new_a' Load - 0,0..0,5",
                '1: f"a{b=}c"',
                '   1] Expr - 1,0..1,9',
                '     .value JoinedStr - 1,0..1,9',
                '       .values[3]',
                "        0] Constant 'ab=' - 1,2..1,6",
                '        1] FormattedValue - 1,3..1,7',
                "          .value Name 'b' Load - 1,4..1,5",
                '          .conversion 114',
                "        2] Constant 'c' - 1,7..1,8",
                '2: new_c',
                '   2] Expr - 2,0..2,5',
                "     .value Name 'new_c' Load - 2,0..2,5",
            ])

            a = f.a
            f = f.reparse()
            self.assertIsNot(f.a, a)
            self.assertIsNot(f.body[0], old_fa)
            self.assertIsNot(f.body[0].a, old_aa)
            self.assertIsNot(f.body[1], old_fb)
            self.assertIsNot(f.body[1].a, old_aa)
            self.assertIsNot(f.body[2], old_fc)
            self.assertIsNot(f.body[2].a, old_ac)

    def test_own_src(self):
        # whole

        f = FST('''
# pre
var # line
# post
            '''.strip())
        self.assertEqual(f.own_src(), '''
# pre
var # line
# post
            '''.strip())
        self.assertEqual(f.own_src(whole=False), '''
var
            '''.strip())

        # fix_elif

        f = FST('''
if 1: pass
elif 2:
    pass
            '''.strip())
        self.assertEqual(f.orelse[0].own_src(), '''
if 2:
    pass
            '''.strip())

        # docstr

        f = FST('''
if 1:
    def func():
        """doc
        str"""
        """non-doc
        str"""
        """unaligned
  str"""
        i = [
            1,
            2,
        ]
            '''.strip())

        self.assertEqual(f.body[0].own_src(docstr=True), '''
def func():
    """doc
    str"""
    """non-doc
    str"""
    """unaligned
str"""
    i = [
        1,
        2,
    ]
            '''.strip())

        self.assertEqual(f.body[0].own_src(docstr='strict'), '''
def func():
    """doc
    str"""
    """non-doc
        str"""
    """unaligned
  str"""
    i = [
        1,
        2,
    ]
            '''.strip())

        self.assertEqual(f.body[0].own_src(docstr=False), '''
def func():
    """doc
        str"""
    """non-doc
        str"""
    """unaligned
  str"""
    i = [
        1,
        2,
    ]
            '''.strip())

        # no location but not at root

        self.assertEqual('', FST('def f(): pass').args.own_src())  # arguments
        self.assertEqual('>>', FST('a >> b').op.own_src())  # operator
        self.assertEqual('', FST('a').ctx.own_src())  # expr_context

    def test_walk(self):
        a = parse("""
def f(a, b=1, *c, d=2, **e): pass
            """.strip()).body[0].args
        l = list(a.f.walk())
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.args[0].f)
        self.assertIs(l[2], a.args[1].f)
        self.assertIs(l[3], a.defaults[0].f)
        self.assertIs(l[4], a.vararg.f)
        self.assertIs(l[5], a.kwonlyargs[0].f)
        self.assertIs(l[6], a.kw_defaults[0].f)
        self.assertIs(l[7], a.kwarg.f)

        a = parse("""
def f(*, a, b, c=1, d=2, **e): pass
            """.strip()).body[0].args
        l = list(a.f.walk())
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.kwonlyargs[0].f)
        self.assertIs(l[2], a.kwonlyargs[1].f)
        self.assertIs(l[3], a.kwonlyargs[2].f)
        self.assertIs(None, a.kw_defaults[0])
        self.assertIs(None, a.kw_defaults[1])
        self.assertIs(l[4], a.kw_defaults[2].f)
        self.assertIs(l[5], a.kwonlyargs[3].f)
        self.assertIs(l[6], a.kw_defaults[3].f)
        self.assertIs(l[7], a.kwarg.f)

        a = parse("""
def f(a, b=1, /, c=2, d=3, *e, f=4, **g): pass
            """.strip()).body[0].args
        l = list(a.f.walk())
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.posonlyargs[0].f)
        self.assertIs(l[2], a.posonlyargs[1].f)
        self.assertIs(l[3], a.defaults[0].f)
        self.assertIs(l[4], a.args[0].f)
        self.assertIs(l[5], a.defaults[1].f)
        self.assertIs(l[6], a.args[1].f)
        self.assertIs(l[7], a.defaults[2].f)
        self.assertIs(l[8], a.vararg.f)
        self.assertIs(l[9], a.kwonlyargs[0].f)
        self.assertIs(l[10], a.kw_defaults[0].f)
        self.assertIs(l[11], a.kwarg.f)

        a = parse("""
def f(a=1, /, b=2): pass
            """.strip()).body[0].args
        l = list(a.f.walk())
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.posonlyargs[0].f)
        self.assertIs(l[2], a.defaults[0].f)
        self.assertIs(l[3], a.args[0].f)
        self.assertIs(l[4], a.defaults[1].f)

        a = parse("""
call(a, b=1, *c, d=2, **e)
            """.strip()).body[0].value
        l = list(a.f.walk())
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.func.f)
        self.assertIs(l[2], a.args[0].f)
        self.assertIs(l[3], a.keywords[0].f)
        self.assertIs(l[4], a.keywords[0].value.f)
        self.assertIs(l[5], a.args[1].f)
        self.assertIs(l[6], a.args[1].value.f)
        self.assertIs(l[7], a.keywords[1].f)
        self.assertIs(l[8], a.keywords[1].value.f)
        self.assertIs(l[9], a.keywords[2].f)
        self.assertIs(l[10], a.keywords[2].value.f)

        a = parse("""
i = 1
self.save_reduce(obj=obj, *rv)
            """.strip()).body[1].value
        l = list(a.f.walk())
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.func.f)
        self.assertIs(l[2], a.func.value.f)
        self.assertIs(l[3], a.keywords[0].f)
        self.assertIs(l[4], a.keywords[0].value.f)
        self.assertIs(l[5], a.args[0].f)
        self.assertIs(l[6], a.args[0].value.f)

        f = parse('[] + [i for i in l]').body[0].value.f
        self.assertEqual(12, len(list(f.walk(True))))
        self.assertEqual(8, len(list(f.walk('loc'))))
        self.assertEqual(7, len(list(f.walk(False))))

        # reenable recurse, disable scope

        f = FST('''
def f():
    def g():
        pass
            '''.strip())
        ff = f.body[0]
        fff = ff.body[0]

        self.assertEqual(list(f.walk()), [f, ff, fff])
        self.assertEqual(list(f.walk(recurse=False)), [f, ff])
        self.assertEqual(list(f.walk(scope=True)), [f, ff])
        self.assertEqual(list(f.walk(recurse=False, scope=True)), [f, ff])

        l = []
        for g in (gen := f.walk(recurse=False, scope=True)):
            if g is f:
                gen.send(True)
            l.append(g)

        self.assertEqual(l, [f, ff, fff])

    def test_walk_scope(self):
        fst = FST.fromsrc("""
def f(a, /, b, *c, d, **e):
    f = 1
    [i for i in g if i]
    {k: v for k, v in h if k and v}
    @deco1
    def func(l=m): hidden
    @deco2
    class sup(cls, meta=moto): hidden
    lambda n=o, **kw: hidden
            """.strip()).a.body[0].f
        self.assertEqual(['f', 'g', 'h', 'deco1', 'm', 'deco2', 'cls', 'moto', 'o'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])
        self.assertEqual(['a', 'b', 'c', 'd', 'e'],
                         [f.a.arg for f in fst.walk(scope=True) if isinstance(f.a, arg)])

        l = []
        for f in (gen := fst.walk(scope=True)):
            if isinstance(f.a, Name):
                l.append(f.a.id)
            elif isinstance(f.a, ClassDef):
                gen.send(True)
        self.assertEqual(['f', 'g', 'h', 'deco1', 'm', 'deco2', 'cls', 'moto', 'hidden', 'o'], l)

        fst = FST.fromsrc("""[z for a in b if (c := a)]""".strip()).a.body[0].value.f
        self.assertEqual(['z', 'a', 'c', 'a'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

        fst = FST.fromsrc("""[z for a in b if (c := a)]""".strip()).a.body[0].f
        self.assertEqual(['b', 'c'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

        fst = FST.fromsrc("""[z for a in b if b in [c := i for i in j if i in {d := k for k in l}]]""".strip()).a.body[0].value.f
        self.assertEqual(['z', 'a', 'b', 'c', 'j', 'd'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

        fst = FST.fromsrc("""[z for a in b if b in [c := i for i in j if i in {d := k for k in l}]]""".strip()).a.body[0].f
        self.assertEqual(['b', 'c', 'd'],
                         [f.a.id for f in fst.walk(scope=True) if isinstance(f.a, Name)])

        # walrus in comprehensions

        def walkscope(fst_or_list, back=False, all=False):
            return '\n'.join(f'{str(f):<32} {f.src or "."}' for f in (fst_or_list.walk(all, scope=True, back=back) if isinstance(fst_or_list, FST) else fst_or_list))

        self.assertEqual(walkscope(FST('z = [i := a for a in b(d := c) if (e := a)]')), '''
<Assign ROOT 0,0..0,43>          z = [i := a for a in b(d := c) if (e := a)]
<Name 0,0..0,1>                  z
<ListComp 0,4..0,43>             [i := a for a in b(d := c) if (e := a)]
<Name 0,5..0,6>                  i
<Call 0,21..0,30>                b(d := c)
<Name 0,21..0,22>                b
<NamedExpr 0,23..0,29>           d := c
<Name 0,23..0,24>                d
<Name 0,28..0,29>                c
<Name 0,35..0,36>                e
            '''.strip())

        self.assertEqual(walkscope(FST('[a for a in b]')), '''
<ListComp ROOT 0,0..0,14>        [a for a in b]
<Name 0,1..0,2>                  a
<comprehension 0,3..0,13>        for a in b
<Name 0,7..0,8>                  a
            '''.strip())

        self.assertEqual(walkscope(FST('var = [a for a in b]')), '''
<Assign ROOT 0,0..0,20>          var = [a for a in b]
<Name 0,0..0,3>                  var
<ListComp 0,6..0,20>             [a for a in b]
<Name 0,18..0,19>                b
            '''.strip())

        self.assertEqual(walkscope(FST('var = [a for a in b]'), back=True), '''
<Assign ROOT 0,0..0,20>          var = [a for a in b]
<ListComp 0,6..0,20>             [a for a in b]
<Name 0,18..0,19>                b
<Name 0,0..0,3>                  var
            '''.strip())

        self.assertEqual(walkscope(FST('[i := a for a in b(j := c) if (k := a)]')), '''
<ListComp ROOT 0,0..0,39>        [i := a for a in b(j := c) if (k := a)]
<NamedExpr 0,1..0,7>             i := a
<Name 0,1..0,2>                  i
<Name 0,6..0,7>                  a
<comprehension 0,8..0,38>        for a in b(j := c) if (k := a)
<Name 0,12..0,13>                a
<NamedExpr 0,31..0,37>           k := a
<Name 0,31..0,32>                k
<Name 0,36..0,37>                a
            '''.strip())

        self.assertEqual(walkscope(FST('var = [i := a for a in b(j := c) if (k := a)]')), '''
<Assign ROOT 0,0..0,45>          var = [i := a for a in b(j := c) if (k := a)]
<Name 0,0..0,3>                  var
<ListComp 0,6..0,45>             [i := a for a in b(j := c) if (k := a)]
<Name 0,7..0,8>                  i
<Call 0,23..0,32>                b(j := c)
<Name 0,23..0,24>                b
<NamedExpr 0,25..0,31>           j := c
<Name 0,25..0,26>                j
<Name 0,30..0,31>                c
<Name 0,37..0,38>                k
            '''.strip())

        self.assertEqual(walkscope(FST('var = [i := a for a in b(j := c) if (k := a)]'), back=True), '''
<Assign ROOT 0,0..0,45>          var = [i := a for a in b(j := c) if (k := a)]
<ListComp 0,6..0,45>             [i := a for a in b(j := c) if (k := a)]
<Name 0,37..0,38>                k
<Call 0,23..0,32>                b(j := c)
<NamedExpr 0,25..0,31>           j := c
<Name 0,30..0,31>                c
<Name 0,25..0,26>                j
<Name 0,23..0,24>                b
<Name 0,7..0,8>                  i
<Name 0,0..0,3>                  var
            '''.strip())

        self.assertEqual(walkscope(FST('[[i := c for c in a] for a in b]')), '''
<ListComp ROOT 0,0..0,32>        [[i := c for c in a] for a in b]
<ListComp 0,1..0,20>             [i := c for c in a]
<Name 0,2..0,3>                  i
<Name 0,18..0,19>                a
<comprehension 0,21..0,31>       for a in b
<Name 0,25..0,26>                a
            '''.strip())

        self.assertEqual(walkscope(FST('[[i := c for c in a] for a in b]'), back=True), '''
<ListComp ROOT 0,0..0,32>        [[i := c for c in a] for a in b]
<comprehension 0,21..0,31>       for a in b
<Name 0,25..0,26>                a
<ListComp 0,1..0,20>             [i := c for c in a]
<Name 0,18..0,19>                a
<Name 0,2..0,3>                  i
            '''.strip())

        # normal comprehensions

        f = FST('[i for j in k if g(j) for i in j if f(i)]')

        self.assertEqual(walkscope(f), '''
<ListComp ROOT 0,0..0,41>        [i for j in k if g(j) for i in j if f(i)]
<Name 0,1..0,2>                  i
<comprehension 0,3..0,21>        for j in k if g(j)
<Name 0,7..0,8>                  j
<Call 0,17..0,21>                g(j)
<Name 0,17..0,18>                g
<Name 0,19..0,20>                j
<comprehension 0,22..0,40>       for i in j if f(i)
<Name 0,26..0,27>                i
<Name 0,31..0,32>                j
<Call 0,36..0,40>                f(i)
<Name 0,36..0,37>                f
<Name 0,38..0,39>                i
            '''.strip())

        self.assertEqual(walkscope(f, back=True), '''
<ListComp ROOT 0,0..0,41>        [i for j in k if g(j) for i in j if f(i)]
<comprehension 0,22..0,40>       for i in j if f(i)
<Call 0,36..0,40>                f(i)
<Name 0,38..0,39>                i
<Name 0,36..0,37>                f
<Name 0,31..0,32>                j
<Name 0,26..0,27>                i
<comprehension 0,3..0,21>        for j in k if g(j)
<Call 0,17..0,21>                g(j)
<Name 0,19..0,20>                j
<Name 0,17..0,18>                g
<Name 0,7..0,8>                  j
<Name 0,1..0,2>                  i
            '''.strip())

        # tricky scope ownership

        f = FST('a = [i for i in (lambda: [out_of_scope for x in y])()]')

        self.assertEqual(walkscope(f), '''
<Assign ROOT 0,0..0,54>          a = [i for i in (lambda: [out_of_scope for x in y])()]
<Name 0,0..0,1>                  a
<ListComp 0,4..0,54>             [i for i in (lambda: [out_of_scope for x in y])()]
<Call 0,16..0,53>                (lambda: [out_of_scope for x in y])()
<Lambda 0,17..0,50>              lambda: [out_of_scope for x in y]
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True)):
            if g.is_Call:  # first iterator
                gen.send(True)  # enable walk into lambda scope of iterator
            l.append(g)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,54>          a = [i for i in (lambda: [out_of_scope for x in y])()]
<Name 0,0..0,1>                  a
<ListComp 0,4..0,54>             [i for i in (lambda: [out_of_scope for x in y])()]
<Call 0,16..0,53>                (lambda: [out_of_scope for x in y])()
<Lambda 0,17..0,50>              lambda: [out_of_scope for x in y]
<ListComp 0,25..0,50>            [out_of_scope for x in y]
<Name 0,26..0,38>                out_of_scope
<comprehension 0,39..0,49>       for x in y
<Name 0,43..0,44>                x
<Name 0,48..0,49>                y
            '''.strip())

        self.assertEqual(walkscope(f.value), '''
<ListComp 0,4..0,54>             [i for i in (lambda: [out_of_scope for x in y])()]
<Name 0,5..0,6>                  i
<comprehension 0,7..0,53>        for i in (lambda: [out_of_scope for x in y])()
<Name 0,11..0,12>                i
            '''.strip())

        l = []
        for g in (gen := f.value.walk(scope=True)):
            if g.is_comprehension:
                gen.send(True)  # enable walk into first comprehension (second nested one as well but that was going to be walked anyway after this first send(True))
            l.append(g)
        self.assertEqual(walkscope(l), '''
<ListComp 0,4..0,54>             [i for i in (lambda: [out_of_scope for x in y])()]
<Name 0,5..0,6>                  i
<comprehension 0,7..0,53>        for i in (lambda: [out_of_scope for x in y])()
<Name 0,11..0,12>                i
<Call 0,16..0,53>                (lambda: [out_of_scope for x in y])()
<Lambda 0,17..0,50>              lambda: [out_of_scope for x in y]
<ListComp 0,25..0,50>            [out_of_scope for x in y]
<Name 0,26..0,38>                out_of_scope
<comprehension 0,39..0,49>       for x in y
<Name 0,43..0,44>                x
<Name 0,48..0,49>                y
            '''.strip())

        self.assertEqual(walkscope(f, back=True), '''
<Assign ROOT 0,0..0,54>          a = [i for i in (lambda: [out_of_scope for x in y])()]
<ListComp 0,4..0,54>             [i for i in (lambda: [out_of_scope for x in y])()]
<Call 0,16..0,53>                (lambda: [out_of_scope for x in y])()
<Lambda 0,17..0,50>              lambda: [out_of_scope for x in y]
<Name 0,0..0,1>                  a
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True, back=True)):
            if g.is_Call:  # first iterator
                gen.send(True)  # enable walk into lambda scope of iterator
            l.append(g)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,54>          a = [i for i in (lambda: [out_of_scope for x in y])()]
<ListComp 0,4..0,54>             [i for i in (lambda: [out_of_scope for x in y])()]
<Call 0,16..0,53>                (lambda: [out_of_scope for x in y])()
<Lambda 0,17..0,50>              lambda: [out_of_scope for x in y]
<ListComp 0,25..0,50>            [out_of_scope for x in y]
<comprehension 0,39..0,49>       for x in y
<Name 0,48..0,49>                y
<Name 0,43..0,44>                x
<Name 0,26..0,38>                out_of_scope
<Name 0,0..0,1>                  a
            '''.strip())

        self.assertEqual(walkscope(f.value, back=True), '''
<ListComp 0,4..0,54>             [i for i in (lambda: [out_of_scope for x in y])()]
<comprehension 0,7..0,53>        for i in (lambda: [out_of_scope for x in y])()
<Name 0,11..0,12>                i
<Name 0,5..0,6>                  i
            '''.strip())

        l = []
        for g in (gen := f.value.walk(scope=True, back=True)):
            if g.is_comprehension:
                gen.send(True)  # enable walk into first comprehension (second nested one as well but that was going to be walked anyway after this first send(True))
            l.append(g)
        self.assertEqual(walkscope(l), '''
<ListComp 0,4..0,54>             [i for i in (lambda: [out_of_scope for x in y])()]
<comprehension 0,7..0,53>        for i in (lambda: [out_of_scope for x in y])()
<Call 0,16..0,53>                (lambda: [out_of_scope for x in y])()
<Lambda 0,17..0,50>              lambda: [out_of_scope for x in y]
<ListComp 0,25..0,50>            [out_of_scope for x in y]
<comprehension 0,39..0,49>       for x in y
<Name 0,48..0,49>                y
<Name 0,43..0,44>                x
<Name 0,26..0,38>                out_of_scope
<Name 0,11..0,12>                i
<Name 0,5..0,6>                  i
            '''.strip())

        # make sure we get all our precious NamedExpr.target.ctx nodes

        f = FST('a = [i := l for j in k if (l := j)]')

        self.assertEqual(walkscope(f, all=True), '''
<Assign ROOT 0,0..0,35>          a = [i := l for j in k if (l := j)]
<Name 0,0..0,1>                  a
<Store>                          .
<ListComp 0,4..0,35>             [i := l for j in k if (l := j)]
<Name 0,5..0,6>                  i
<Store>                          .
<Name 0,21..0,22>                k
<Load>                           .
<Name 0,27..0,28>                l
<Store>                          .
            '''.strip())

        l = []
        for g in (gen := f.walk(True, scope=True)):
            if g.is_Name and g.parent.is_NamedExpr:
                if g.src == 'i':
                    gen.send(False)
            elif g.is_Store:
                gen.send(False)  # don't recurse into the ctx XD, just for coverage
            l.append(g)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,35>          a = [i := l for j in k if (l := j)]
<Name 0,0..0,1>                  a
<Store>                          .
<ListComp 0,4..0,35>             [i := l for j in k if (l := j)]
<Name 0,5..0,6>                  i
<Name 0,21..0,22>                k
<Load>                           .
<Name 0,27..0,28>                l
<Store>                          .
            '''.strip())

        # funcdef arguments

        f = FST(r'''
def f(a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te) -> rf:
    def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
            '''.strip(), 'exec')

        self.assertEqual(walkscope(f), '''
<Module ROOT 0,0..1,74>          def f(a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te) -> rf:
    def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<FunctionDef 0,0..1,74>          def f(a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te) -> rf:
    def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<Name 0,9..0,11>                 ta
<Constant 0,14..0,15>            1
<Name 0,23..0,25>                tb
<Constant 0,28..0,29>            2
<Name 0,35..0,37>                tc
<Name 0,42..0,44>                td
<Constant 0,47..0,48>            3
<Name 0,55..0,57>                te
<Name 0,62..0,64>                rf
            '''.strip())

        self.assertEqual(walkscope(f.body[0]), '''
<FunctionDef 0,0..1,74>          def f(a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te) -> rf:
    def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<arguments 0,6..0,57>            a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te
<arg 0,6..0,11>                  a: ta
<arg 0,20..0,25>                 b: tb
<arg 0,32..0,37>                 c: tc
<arg 0,39..0,44>                 d: td
<arg 0,52..0,57>                 e: te
<FunctionDef 1,4..1,74>          def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<Name 1,13..1,15>                th
<Constant 1,18..1,19>            5
<Name 1,27..1,29>                ti
<Constant 1,32..1,33>            6
<Name 1,39..1,41>                tj
<Name 1,46..1,48>                tk
<Constant 1,51..1,52>            7
<Name 1,59..1,61>                tl
<Name 1,66..1,68>                rg
            '''.strip())

        self.assertEqual(walkscope(f.body[0].body[0]), '''
<FunctionDef 1,4..1,74>          def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<arguments 1,10..1,61>           h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl
<arg 1,10..1,15>                 h: th
<arg 1,24..1,29>                 i: ti
<arg 1,36..1,41>                 j: tj
<arg 1,43..1,48>                 k: tk
<arg 1,56..1,61>                 l: tl
<Pass 1,70..1,74>                pass
            '''.strip())

        self.assertEqual(walkscope(f, back=True), '''
<Module ROOT 0,0..1,74>          def f(a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te) -> rf:
    def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<FunctionDef 0,0..1,74>          def f(a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te) -> rf:
    def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<Name 0,62..0,64>                rf
<Name 0,55..0,57>                te
<Constant 0,47..0,48>            3
<Name 0,42..0,44>                td
<Name 0,35..0,37>                tc
<Constant 0,28..0,29>            2
<Name 0,23..0,25>                tb
<Constant 0,14..0,15>            1
<Name 0,9..0,11>                 ta
            '''.strip())

        self.assertEqual(walkscope(f.body[0], back=True), '''
<FunctionDef 0,0..1,74>          def f(a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te) -> rf:
    def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<FunctionDef 1,4..1,74>          def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<Name 1,66..1,68>                rg
<Name 1,59..1,61>                tl
<Constant 1,51..1,52>            7
<Name 1,46..1,48>                tk
<Name 1,39..1,41>                tj
<Constant 1,32..1,33>            6
<Name 1,27..1,29>                ti
<Constant 1,18..1,19>            5
<Name 1,13..1,15>                th
<arguments 0,6..0,57>            a: ta = 1, /, b: tb = 2, *c: tc, d: td = 3, **e: te
<arg 0,52..0,57>                 e: te
<arg 0,39..0,44>                 d: td
<arg 0,32..0,37>                 c: tc
<arg 0,20..0,25>                 b: tb
<arg 0,6..0,11>                  a: ta
            '''.strip())

        self.assertEqual(walkscope(f.body[0].body[0], back=True), '''
<FunctionDef 1,4..1,74>          def g(h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl) -> rg: pass
<Pass 1,70..1,74>                pass
<arguments 1,10..1,61>           h: th = 5, /, i: ti = 6, *j: tj, k: tk = 7, **l: tl
<arg 1,56..1,61>                 l: tl
<arg 1,43..1,48>                 k: tk
<arg 1,36..1,41>                 j: tj
<arg 1,24..1,29>                 i: ti
<arg 1,10..1,15>                 h: th
            '''.strip())

        # lambda

        f = FST('_ = lambda a=1, /, b=2, *d, e=3, **g: None')

        self.assertEqual(walkscope(f, back=True), '''
<Assign ROOT 0,0..0,42>          _ = lambda a=1, /, b=2, *d, e=3, **g: None
<Lambda 0,4..0,42>               lambda a=1, /, b=2, *d, e=3, **g: None
<Constant 0,30..0,31>            3
<Constant 0,21..0,22>            2
<Constant 0,13..0,14>            1
<Name 0,0..0,1>                  _
            '''.strip())

        self.assertEqual(walkscope(f.value, back=True), '''
<Lambda 0,4..0,42>               lambda a=1, /, b=2, *d, e=3, **g: None
<Constant 0,38..0,42>            None
<arguments 0,11..0,36>           a=1, /, b=2, *d, e=3, **g
<arg 0,35..0,36>                 g
<arg 0,28..0,29>                 e
<arg 0,25..0,26>                 d
<arg 0,19..0,20>                 b
<arg 0,11..0,12>                 a
            '''.strip())

        # class bases

        f = FST(r'''
class cls(a, b=c):
    class nest(d, e=f): pass
            '''.strip(), 'exec')

        self.assertEqual(walkscope(f), '''
<Module ROOT 0,0..1,28>          class cls(a, b=c):
    class nest(d, e=f): pass
<ClassDef 0,0..1,28>             class cls(a, b=c):
    class nest(d, e=f): pass
<Name 0,10..0,11>                a
<keyword 0,13..0,16>             b=c
<Name 0,15..0,16>                c
            '''.strip())

        self.assertEqual(walkscope(f.body[0]), '''
<ClassDef 0,0..1,28>             class cls(a, b=c):
    class nest(d, e=f): pass
<ClassDef 1,4..1,28>             class nest(d, e=f): pass
<Name 1,15..1,16>                d
<keyword 1,18..1,21>             e=f
<Name 1,20..1,21>                f
            '''.strip())

        self.assertEqual(walkscope(f, back=True), '''
<Module ROOT 0,0..1,28>          class cls(a, b=c):
    class nest(d, e=f): pass
<ClassDef 0,0..1,28>             class cls(a, b=c):
    class nest(d, e=f): pass
<keyword 0,13..0,16>             b=c
<Name 0,15..0,16>                c
<Name 0,10..0,11>                a
            '''.strip())

        self.assertEqual(walkscope(f.body[0], back=True), '''
<ClassDef 0,0..1,28>             class cls(a, b=c):
    class nest(d, e=f): pass
<ClassDef 1,4..1,28>             class nest(d, e=f): pass
<keyword 1,18..1,21>             e=f
<Name 1,20..1,21>                f
<Name 1,15..1,16>                d
            '''.strip())

        # TypeAlias

        if PYGE13:
            f = FST('type t[T: ftb = ftd, *U = fud, **V = fvd] = ...'.strip(), 'exec')

            self.assertEqual(walkscope(f), '''
<Module ROOT 0,0..0,47>          type t[T: ftb = ftd, *U = fud, **V = fvd] = ...
<TypeAlias 0,0..0,47>            type t[T: ftb = ftd, *U = fud, **V = fvd] = ...
<Name 0,5..0,6>                  t
<TypeVar 0,7..0,19>              T: ftb = ftd
<Name 0,10..0,13>                ftb
<Name 0,16..0,19>                ftd
<TypeVarTuple 0,21..0,29>        *U = fud
<Name 0,26..0,29>                fud
<ParamSpec 0,31..0,40>           **V = fvd
<Name 0,37..0,40>                fvd
<Constant 0,44..0,47>            ...
                '''.strip())

            self.assertEqual(walkscope(f.body[0]), '''
<TypeAlias 0,0..0,47>            type t[T: ftb = ftd, *U = fud, **V = fvd] = ...
<Name 0,5..0,6>                  t
<TypeVar 0,7..0,19>              T: ftb = ftd
<Name 0,10..0,13>                ftb
<Name 0,16..0,19>                ftd
<TypeVarTuple 0,21..0,29>        *U = fud
<Name 0,26..0,29>                fud
<ParamSpec 0,31..0,40>           **V = fvd
<Name 0,37..0,40>                fvd
<Constant 0,44..0,47>            ...
                '''.strip())

        if PYGE12:
            f = FST('type t[T: ftb, *U, **V] = ...'.strip(), 'exec')

            self.assertEqual(walkscope(f), '''
<Module ROOT 0,0..0,29>          type t[T: ftb, *U, **V] = ...
<TypeAlias 0,0..0,29>            type t[T: ftb, *U, **V] = ...
<Name 0,5..0,6>                  t
<TypeVar 0,7..0,13>              T: ftb
<Name 0,10..0,13>                ftb
<TypeVarTuple 0,15..0,17>        *U
<ParamSpec 0,19..0,22>           **V
<Constant 0,26..0,29>            ...
                '''.strip())

            self.assertEqual(walkscope(f.body[0]), '''
<TypeAlias 0,0..0,29>            type t[T: ftb, *U, **V] = ...
<Name 0,5..0,6>                  t
<TypeVar 0,7..0,13>              T: ftb
<Name 0,10..0,13>                ftb
<TypeVarTuple 0,15..0,17>        *U
<ParamSpec 0,19..0,22>           **V
<Constant 0,26..0,29>            ...
                '''.strip())

        # type_params

        if PYGE13:
            f = FST(r'''
def f[T: ftb = ftd, *U = fud, **V = fvd]():
    def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
                '''.strip(), 'exec')

            self.assertEqual(walkscope(f), '''
<Module ROOT 0,0..1,52>          def f[T: ftb = ftd, *U = fud, **V = fvd]():
    def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<FunctionDef 0,0..1,52>          def f[T: ftb = ftd, *U = fud, **V = fvd]():
    def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<Name 0,9..0,12>                 ftb
<Name 0,15..0,18>                ftd
<Name 0,25..0,28>                fud
<Name 0,36..0,39>                fvd
                '''.strip())

            self.assertEqual(walkscope(f.body[0]), '''
<FunctionDef 0,0..1,52>          def f[T: ftb = ftd, *U = fud, **V = fvd]():
    def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<TypeVar 0,6..0,18>              T: ftb = ftd
<TypeVarTuple 0,20..0,28>        *U = fud
<ParamSpec 0,30..0,39>           **V = fvd
<FunctionDef 1,4..1,52>          def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<Name 1,13..1,16>                gtb
<Name 1,19..1,22>                gtd
<Name 1,29..1,32>                gud
<Name 1,40..1,43>                gvd
                '''.strip())

            self.assertEqual(walkscope(f.body[0].body[0]), '''
<FunctionDef 1,4..1,52>          def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<TypeVar 1,10..1,22>             X: gtb = gtd
<TypeVarTuple 1,24..1,32>        *Y = gud
<ParamSpec 1,34..1,43>           **Z = gvd
<Pass 1,48..1,52>                pass
                '''.strip())

            self.assertEqual(walkscope(f, back=True), '''
<Module ROOT 0,0..1,52>          def f[T: ftb = ftd, *U = fud, **V = fvd]():
    def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<FunctionDef 0,0..1,52>          def f[T: ftb = ftd, *U = fud, **V = fvd]():
    def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<Name 0,36..0,39>                fvd
<Name 0,25..0,28>                fud
<Name 0,15..0,18>                ftd
<Name 0,9..0,12>                 ftb
                '''.strip())

            self.assertEqual(walkscope(f.body[0], back=True), '''
<FunctionDef 0,0..1,52>          def f[T: ftb = ftd, *U = fud, **V = fvd]():
    def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<FunctionDef 1,4..1,52>          def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<Name 1,40..1,43>                gvd
<Name 1,29..1,32>                gud
<Name 1,19..1,22>                gtd
<Name 1,13..1,16>                gtb
<ParamSpec 0,30..0,39>           **V = fvd
<TypeVarTuple 0,20..0,28>        *U = fud
<TypeVar 0,6..0,18>              T: ftb = ftd
                '''.strip())

            self.assertEqual(walkscope(f.body[0].body[0], back=True), '''
<FunctionDef 1,4..1,52>          def g[X: gtb = gtd, *Y = gud, **Z = gvd](): pass
<Pass 1,48..1,52>                pass
<ParamSpec 1,34..1,43>           **Z = gvd
<TypeVarTuple 1,24..1,32>        *Y = gud
<TypeVar 1,10..1,22>             X: gtb = gtd
                '''.strip())

            f = FST('class cls[T: int = bool, *U = u, **V = v](a, b=c): pass', 'exec')

            self.assertEqual(walkscope(f, back=True), '''
<Module ROOT 0,0..0,55>          class cls[T: int = bool, *U = u, **V = v](a, b=c): pass
<ClassDef 0,0..0,55>             class cls[T: int = bool, *U = u, **V = v](a, b=c): pass
<keyword 0,45..0,48>             b=c
<Name 0,47..0,48>                c
<Name 0,42..0,43>                a
<Name 0,39..0,40>                v
<Name 0,30..0,31>                u
<Name 0,19..0,23>                bool
<Name 0,13..0,16>                int
                '''.strip())

            self.assertEqual(walkscope(f.body[0], back=True), '''
<ClassDef 0,0..0,55>             class cls[T: int = bool, *U = u, **V = v](a, b=c): pass
<Pass 0,51..0,55>                pass
<ParamSpec 0,33..0,40>           **V = v
<TypeVarTuple 0,25..0,31>        *U = u
<TypeVar 0,10..0,23>             T: int = bool
                '''.strip())

        if PYGE12:
            f = FST(r'''
def f[T: ftb, *U, **V]():
    def g[X: gtb, *Y, **Z](): pass
                '''.strip(), 'exec')

            self.assertEqual(walkscope(f), '''
<Module ROOT 0,0..1,34>          def f[T: ftb, *U, **V]():
    def g[X: gtb, *Y, **Z](): pass
<FunctionDef 0,0..1,34>          def f[T: ftb, *U, **V]():
    def g[X: gtb, *Y, **Z](): pass
<Name 0,9..0,12>                 ftb
                '''.strip())

            self.assertEqual(walkscope(f.body[0]), '''
<FunctionDef 0,0..1,34>          def f[T: ftb, *U, **V]():
    def g[X: gtb, *Y, **Z](): pass
<TypeVar 0,6..0,12>              T: ftb
<TypeVarTuple 0,14..0,16>        *U
<ParamSpec 0,18..0,21>           **V
<FunctionDef 1,4..1,34>          def g[X: gtb, *Y, **Z](): pass
<Name 1,13..1,16>                gtb
                '''.strip())

            self.assertEqual(walkscope(f.body[0].body[0]), '''
<FunctionDef 1,4..1,34>          def g[X: gtb, *Y, **Z](): pass
<TypeVar 1,10..1,16>             X: gtb
<TypeVarTuple 1,18..1,20>        *Y
<ParamSpec 1,22..1,25>           **Z
<Pass 1,30..1,34>                pass
                '''.strip())

            self.assertEqual(walkscope(f, back=True), '''
<Module ROOT 0,0..1,34>          def f[T: ftb, *U, **V]():
    def g[X: gtb, *Y, **Z](): pass
<FunctionDef 0,0..1,34>          def f[T: ftb, *U, **V]():
    def g[X: gtb, *Y, **Z](): pass
<Name 0,9..0,12>                 ftb
                '''.strip())

            self.assertEqual(walkscope(f.body[0], back=True), '''
<FunctionDef 0,0..1,34>          def f[T: ftb, *U, **V]():
    def g[X: gtb, *Y, **Z](): pass
<FunctionDef 1,4..1,34>          def g[X: gtb, *Y, **Z](): pass
<Name 1,13..1,16>                gtb
<ParamSpec 0,18..0,21>           **V
<TypeVarTuple 0,14..0,16>        *U
<TypeVar 0,6..0,12>              T: ftb
                '''.strip())

            self.assertEqual(walkscope(f.body[0].body[0], back=True), '''
<FunctionDef 1,4..1,34>          def g[X: gtb, *Y, **Z](): pass
<Pass 1,30..1,34>                pass
<ParamSpec 1,22..1,25>           **Z
<TypeVarTuple 1,18..1,20>        *Y
<TypeVar 1,10..1,16>             X: gtb
                '''.strip())

            f = FST('class cls[T: int, *U, **V](a, b=c): pass', 'exec')

            self.assertEqual(walkscope(f, back=True), '''
<Module ROOT 0,0..0,40>          class cls[T: int, *U, **V](a, b=c): pass
<ClassDef 0,0..0,40>             class cls[T: int, *U, **V](a, b=c): pass
<keyword 0,30..0,33>             b=c
<Name 0,32..0,33>                c
<Name 0,27..0,28>                a
<Name 0,13..0,16>                int
                '''.strip())

            self.assertEqual(walkscope(f.body[0], back=True), '''
<ClassDef 0,0..0,40>             class cls[T: int, *U, **V](a, b=c): pass
<Pass 0,36..0,40>                pass
<ParamSpec 0,22..0,25>           **V
<TypeVarTuple 0,18..0,20>        *U
<TypeVar 0,10..0,16>             T: int
                '''.strip())

    def test_walk_modify(self):
        fst = parse('if 1:\n a\n b\n c\nelse:\n d\n e').body[0].f
        i   = 0

        for f in fst.walk(self_=False):
            if f.pfield.name in ('body', 'orelse'):
                f.replace(str(i := i + 1), raw=False)

        self.assertEqual(fst.src, 'if 1:\n 1\n 2\n 3\nelse:\n 4\n 5')

        fst = parse('[a, b, c]').body[0].f
        i   = 0

        for f in fst.walk(self_=False):
            if f.pfield.name == 'elts':
                f.replace(str(i := i + 1), raw=False)

        self.assertEqual(fst.src, '[1, 2, 3]')

        # replace raw which changes parent doesn't error

        def test(f, all):
            for g in f.walk(all=all):
                if g.is_Constant:
                    g.replace('2', raw=True)

        f = FST('i = x + 1')
        test(f, False)
        test(f, True)
        self.assertEqual('i = x + 2', f.src)

        f = FST('i = x + 1', 'stmt')
        test(f, False)
        test(f, True)
        self.assertEqual('i = x + 2', f.src)

        f = FST('i = x + 1', 'exec')
        test(f, False)
        test(f, True)
        self.assertEqual('i = x + 2', f.src)

        # this replace raw works because changes root AST

        f = FST('i = 1')
        test(f, False)
        test(f, True)
        self.assertEqual('i = 2', f.src)

        # replace root

        a = (f := FST('a')).a
        for g in f.walk():
            g.replace('1')
        self.assertIsNone(a.f)
        self.assertIsNot(f.a, a)
        self.assertEqual('1', f.src)
        self.assertTrue(f.is_Constant)
        f.verify()

        f = FST('a + b')
        ns = []
        for g in f.walk(True):
            if g.is_BinOp:
                g.replace('x * y')  # replace and continue walk into new node
            else:
                ns.append(g.src)
        self.assertEqual(['x', '', '*', 'y', ''], ns)  # should be newly replaced child nodes (including ctx)
        self.assertEqual('x * y', f.src)
        f.verify()

        f = FST('a + b', 'Expr')  # doesn't replace root but just below it
        ns = []
        for g in f.walk(True):
            if g.is_BinOp:
                g.replace('x * y')  # replace and continue walk into new node
            else:
                ns.append(g.src)
        self.assertEqual(['a + b', 'x', '', '*', 'y', ''], ns)  # first node is original expr
        self.assertEqual('x * y', f.src)
        f.verify()

        # replace but don't recurse into it

        f = FST('a + b')
        ns = []
        for g in (gen := f.walk()):
            ns.append(g.src)
            if g.is_BinOp:
                g.replace('x * y')  # replace and continue walk into new node
                gen.send(False)
        self.assertEqual(['a + b'], ns)  # should be newly replaced child nodes (including ctx)
        self.assertEqual('x * y', f.src)
        f.verify()

        # remove first node walked which is not root

        f = FST('[1, b, 3]')
        ns = []
        for g in f.elts[1].walk():
            ns.append(g.src)
            g.remove()
        self.assertEqual(['b'], ns)
        self.assertEqual('[1, 3]', f.src)
        f.verify()

        # remove or replace parent's parent is fine

        f = FST('a + 1', 'exec')
        for g in f.walk():
            if g.is_Name:
                g.parent.parent.remove()
        self.assertEqual('', f.src)

        f = FST('a + 1', 'exec')
        for g in f.walk():
            if g.is_Name:
                g.parent.parent.replace('x * y')
        self.assertEqual('x * y', f.src)

        # replace nodes previously walked

        f = FST('a + 1\na + 1\na + 1')
        for g in f.walk():
            if g.is_Constant:
                if (idx := g.parent.parent.pfield.idx):  # g.BinOp.Expr.pfield.idx (in Module)
                    f.put('b', idx - 1)  # replace previous stmt to ours
        self.assertEqual('b\nb\na + 1', f.src)
        f.verify()

        # replace or remove sibling nodes not yet walked

        f = FST('[1, b, 3]')
        ns = []
        for g in f.walk(self_=False):
            ns.append(g.src)
            if g.is_Name:
                g.next().replace('4')
        self.assertEqual(['1', 'b'], ns)
        self.assertEqual('[1, b, 4]', f.src)
        f.verify()

        f = FST('[1, b, 3]')
        ns = []
        for g in f.walk(self_=False):
            ns.append(g.src)
            if g.is_Name:
                g.next().remove()
        self.assertEqual(['1', 'b'], ns)
        self.assertEqual('[1, b]', f.src)
        f.verify()

        # replace or remove parent sibling nodes not yet walked

        f = FST('a + b\nc + 1\nd + e\ny')
        ns = []
        for g in f.walk(self_=False):
            ns.append(g.src)
            if g.is_Constant:
                g.parent.parent.next().replace('x')  # g.BinOp.Expr.next()
        self.assertEqual(['a + b', 'a + b', 'a', 'b', 'c + 1', 'c + 1', 'c', '1', 'y', 'y'], ns)
        self.assertEqual('a + b\nc + 1\nx\ny', f.src)
        f.verify()

        f = FST('a + b\nc + 1\nd + e\ny')
        ns = []
        for g in f.walk(self_=False):
            ns.append(g.src)
            if g.is_Constant:
                g.parent.parent.next().remove()  # g.BinOp.Expr.next()
        self.assertEqual(['a + b', 'a + b', 'a', 'b', 'c + 1', 'c + 1', 'c', '1', 'y', 'y'], ns)
        self.assertEqual('a + b\nc + 1\ny', f.src)
        f.verify()

    def test_scope_symbols(self):
        f = FST(r'''
def func():
    global f
    nonlocal a
    a = b
    del c
    d += e
    import f
    import h.i
    import j as k
    from l import m
    from o import p as q
    from r import *
    [s := t for t in z if (w := t) for x in y if (z := x)]
            ''')
        self.assertEqual(['f', 'a', 'b', 'c', 'd', 'e', 'h', 'k', 'm', 'q', 's', 'z', 'w'], list(f.scope_symbols()))
        self.assertEqual(pformat(f.scope_symbols(full=True), sort_dicts=False), '''
{'load': {'b': [<Name 4,8..4,9>],
          'd': [<Name 6,4..6,5>],
          'e': [<Name 6,9..6,10>],
          'z': [<Name 13,21..13,22>]},
 'store': {'a': [<Name 4,4..4,5>],
           'd': [<Name 6,4..6,5>],
           'f': [<alias 7,11..7,12>],
           'h': [<alias 8,11..8,14>],
           'k': [<alias 9,11..9,17>],
           'm': [<alias 10,18..10,19>],
           'q': [<alias 11,18..11,24>],
           's': [<Name 13,5..13,6>],
           'w': [<Name 13,27..13,28>],
           'z': [<Name 13,50..13,51>]},
 'del': {'c': [<Name 5,8..5,9>]},
 'global': {'f': [<Global 2,4..2,12>]},
 'nonlocal': {'a': [<Nonlocal 3,4..3,14>]},
 'local': {'d': [<Name 6,4..6,5>],
           'h': [<alias 8,11..8,14>],
           'k': [<alias 9,11..9,17>],
           'm': [<alias 10,18..10,19>],
           'q': [<alias 11,18..11,24>],
           's': [<Name 13,5..13,6>],
           'w': [<Name 13,27..13,28>],
           'z': [<Name 13,50..13,51>]},
 'free': {'b': [<Name 4,8..4,9>], 'e': [<Name 6,9..6,10>]}}
            '''.strip())

        # arguments

        f = FST('def func(a: b = c, /, d: e = f, *g, h: i = j, **k) -> l: _', 'exec')
        self.assertEqual(['func', 'b', 'c', 'e', 'f', 'i', 'j', 'l'], list(f.scope_symbols()))
        self.assertEqual(['a', 'd', 'g', 'h', 'k', '_'], list(f.body[0].scope_symbols()))

        # class bases

        f = FST(r'''
class cls(a, b=c):
    class nest(d, e=f): pass
            '''.strip(), 'exec')

        self.assertEqual(['cls', 'a', 'c'], list(f.scope_symbols()))
        self.assertEqual(['nest', 'd', 'f'], list(f.body[0].scope_symbols()))

        # TypeAlias

        if PYGE13:
            f = FST('type t[T: ftb = ftd, *U = fud, **V = fvd] = ...'.strip(), 'exec')

            self.assertEqual(['t', 'T', 'ftb', 'ftd', 'U', 'fud', 'V', 'fvd'], list(f.scope_symbols()))
            self.assertEqual(['t', 'T', 'ftb', 'ftd', 'U', 'fud', 'V', 'fvd'], list(f.body[0].scope_symbols()))

        if PYGE12:
            f = FST('type t[T: ftb, *U, **V] = ...'.strip(), 'exec')

            self.assertEqual(['t', 'T', 'ftb', 'U', 'V'], list(f.scope_symbols()))
            self.assertEqual(['t', 'T', 'ftb', 'U', 'V'], list(f.body[0].scope_symbols()))

        # type_params

        if PYGE13:
            f = FST('def func[T: ftb = ftd, *U = fud, **V = fvd](): pass', 'exec')
            self.assertEqual(['func', 'ftb', 'ftd', 'fud', 'fvd'], list(f.scope_symbols()))
            self.assertEqual(['T', 'U', 'V'], list(f.body[0].scope_symbols()))

            f = FST('async def afunc[T: ftb = ftd, *U = fud, **V = fvd](): pass', 'exec')
            self.assertEqual(['afunc', 'ftb', 'ftd', 'fud', 'fvd'], list(f.scope_symbols()))
            self.assertEqual(['T', 'U', 'V'], list(f.body[0].scope_symbols()))

            f = FST('class cls[T: ftb = ftd, *U = fud, **V = fvd]: pass', 'exec')
            self.assertEqual(['cls', 'ftb', 'ftd', 'fud', 'fvd'], list(f.scope_symbols()))
            self.assertEqual(['T', 'U', 'V'], list(f.body[0].scope_symbols()))

        if PYGE12:
            f = FST('def func[T: ftb, *U, **V](): pass', 'exec')
            self.assertEqual(['func', 'ftb'], list(f.scope_symbols()))
            self.assertEqual(['T', 'U', 'V'], list(f.body[0].scope_symbols()))

            f = FST('async def afunc[T: ftb, *U, **V](): pass', 'exec')
            self.assertEqual(['afunc', 'ftb'], list(f.scope_symbols()))
            self.assertEqual(['T', 'U', 'V'], list(f.body[0].scope_symbols()))

            f = FST('class cls[T: ftb, *U, **V]: pass', 'exec')
            self.assertEqual(['cls', 'ftb'], list(f.scope_symbols()))
            self.assertEqual(['T', 'U', 'V'], list(f.body[0].scope_symbols()))

        # Comp walrus detail

        self.assertEqual(pformat(FST('[i for a in b if (i := a)]').scope_symbols(full=True), sort_dicts=False), '''
{'load': {'i': [<Name 0,1..0,2>], 'a': [<Name 0,23..0,24>]},
 'store': {'a': [<Name 0,7..0,8>], 'i': [<Name 0,18..0,19>]},
 'del': {},
 'global': {},
 'nonlocal': {},
 'local': {'a': [<Name 0,7..0,8>]},
 'free': {'i': [<Name 0,1..0,2>, <Name 0,18..0,19>]}}
            '''.strip())

        self.assertEqual(pformat(FST('[i := a for a in b]').scope_symbols(full=True), sort_dicts=False), '''
{'load': {'a': [<Name 0,6..0,7>]},
 'store': {'i': [<Name 0,1..0,2>], 'a': [<Name 0,12..0,13>]},
 'del': {},
 'global': {},
 'nonlocal': {},
 'local': {'a': [<Name 0,12..0,13>]},
 'free': {'i': [<Name 0,1..0,2>]}}
            '''.strip())

        # ListComp

        self.assertEqual(['a'], list(FST('[a for a in b(c)]').scope_symbols()))
        self.assertEqual(['a', 'b', 'e'], list(FST('[a for b in c(d) for a in b(e)]').scope_symbols()))

        self.assertEqual(['i', 'a'], list(FST('[i := a for a in (j := b)]').scope_symbols()))
        self.assertEqual(['i', 'a'], list(FST('[i for a in b if (i := a)]').scope_symbols()))

        # SetComp

        self.assertEqual(['a'], list(FST('{a for a in b(c)}').scope_symbols()))
        self.assertEqual(['a', 'b', 'e'], list(FST('{a for b in c(d) for a in b(e)}').scope_symbols()))

        self.assertEqual(['i', 'a'], list(FST('{i := a for a in (j := b)}').scope_symbols()))
        self.assertEqual(['i', 'a'], list(FST('{i for a in b if (i := a)}').scope_symbols()))

        # GeneratorExp

        self.assertEqual(['a'], list(FST('(a for a in b(c))').scope_symbols()))
        self.assertEqual(['a', 'b', 'e'], list(FST('(a for b in c(d) for a in b(e))').scope_symbols()))

        self.assertEqual(['i', 'a'], list(FST('(i := a for a in (j := b))').scope_symbols()))
        self.assertEqual(['i', 'a'], list(FST('(i for a in b if (i := a))').scope_symbols()))

        # DictComp

        self.assertEqual(['a'], list(FST('{a: a for a in b(c)}').scope_symbols()))
        self.assertEqual(['a', 'b', 'e'], list(FST('{a: a for b in c(d) for a in b(e)}').scope_symbols()))

        self.assertEqual(['i', 'a'], list(FST('{(i := a): a for a in (j := b)}').scope_symbols()))
        self.assertEqual(['i', 'a'], list(FST('{i: a for a in b if (i := a)}').scope_symbols()))

        # other detail and test coverage

        self.assertEqual(pformat(FST('a\na += b').scope_symbols(full=True), sort_dicts=False), '''
{'load': {'a': [<Name 0,0..0,1>, <Name 1,0..1,1>], 'b': [<Name 1,5..1,6>]},
 'store': {'a': [<Name 1,0..1,1>]},
 'del': {},
 'global': {},
 'nonlocal': {},
 'local': {'a': [<Name 1,0..1,1>]},
 'free': {'b': [<Name 1,5..1,6>]}}
            '''.strip())

        self.assertEqual(pformat(FST('a = 1\nfrom b import a').scope_symbols(full=True), sort_dicts=False), '''
{'load': {},
 'store': {'a': [<Name 0,0..0,1>, <alias 1,14..1,15>]},
 'del': {},
 'global': {},
 'nonlocal': {},
 'local': {'a': [<Name 0,0..0,1>, <alias 1,14..1,15>]},
 'free': {}}
            '''.strip())

        self.assertEqual(pformat(FST('global a\nglobal a\nnonlocal b\nnonlocal b').scope_symbols(full=True), sort_dicts=False), '''
{'load': {},
 'store': {},
 'del': {},
 'global': {'a': [<Global 0,0..0,8>, <Global 1,0..1,8>]},
 'nonlocal': {'b': [<Nonlocal 2,0..2,10>, <Nonlocal 3,0..3,10>]},
 'local': {},
 'free': {}}
            '''.strip())

    def test_next_prev_child(self):
        fst = parse('a and b and c and d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.op.f)
        self.assertIs((f := fst.next_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.op.f)
        self.assertIs((f := fst.prev_child(f, True)), None)

        if PYGE12:
            fst = parse('@deco\ndef f[T, U](a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
            a = fst.a
            f = None
            self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, False)), a.args.f)
            self.assertIs((f := fst.next_child(f, False)), a.returns.f)
            self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, False)), None)
            f = None
            self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, True)), a.args.f)
            self.assertIs((f := fst.next_child(f, True)), a.returns.f)
            self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, True)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, False)), a.args.f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, False)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, True)), a.args.f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, True)), None)

        fst = parse('@deco\ndef f(a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.args.f)
        self.assertIs((f := fst.next_child(f, False)), a.returns.f)
        self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.args.f)
        self.assertIs((f := fst.next_child(f, True)), a.returns.f)
        self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, False)), a.args.f)
        self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, True)), a.args.f)
        self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)

        fst = parse('a <= b == c >= d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.left.f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.left.f)
        self.assertIs((f := fst.next_child(f, True)), a.ops[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.ops[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.ops[2].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.left.f)
        self.assertIs((f := fst.prev_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.ops[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.ops[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.ops[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.left.f)
        self.assertIs((f := fst.prev_child(f, True)), None)

        fst = parse('match a:\n case {1: a, 2: b, **rest}: pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)

        fst = parse('match a:\n case cls(1, 2, a=3, b=4): pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.cls.f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.cls.f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, True)), None)

        # ...

        f = FST('name')
        self.assertIsNone(f.first_child(False))
        self.assertIsNone(f.last_child(False))
        self.assertIsNone(f.first_child('loc'))
        self.assertIsNone(f.last_child('loc'))
        self.assertIs(f.ctx, f.first_child(True))
        self.assertIs(f.ctx, f.last_child(True))

        f = FST('def f(): pass')
        self.assertIsNone(f.body[0].prev(False))
        self.assertIs(f.args, f.body[0].prev('loc'))
        self.assertIs(f.args, f.body[0].prev(True))

        f = FST('-a')
        self.assertIsNone(f.operand.prev(False))
        self.assertIs(f.op, f.operand.prev('loc'))
        self.assertIs(f.op, f.operand.prev(True))

        f = FST('a + b')
        self.assertIs(f.right, f.left.next(False))
        self.assertIs(f.op, f.left.next('loc'))
        self.assertIs(f.op, f.left.next(True))

        f = FST('a < b')
        self.assertIs(f.comparators[0], f.left.next(False))
        self.assertIs(f.ops[0], f.left.next('loc'))
        self.assertIs(f.ops[0], f.left.next(True))

        f = FST('a and b')
        self.assertIs(f.values[1], f.values[0].next(False))
        self.assertIs(f.values[1], f.values[0].next('loc'))
        self.assertIs(f.values[1], f.values[0].next(True))

        # last_header_child

        f = FST('def f(a) -> int: pass')
        self.assertEqual('int', f.last_header_child().src)
        self.assertEqual('a', f.last_header_child(arguments).src)
        self.assertIsNone(f.last_header_child(Constant))

    def test_walk_vs_next_prev_child(self):
        def test1(src):
            f = FST.fromsrc(src).a.body[0].args.f
            m = list(f.walk(self_=False, recurse=False))

            l, c = [], None
            while c := f.next_child(c): l.append(c)
            self.assertEqual(l, m)

            l, c = [], None
            while c := f.prev_child(c): l.append(c)
            self.assertEqual(l, m[::-1])

        test1('def f(**a): apass')
        test1('def f(*, e, d, c=3, b=2, **a): pass')
        test1('def f(*f, e, d, c=3, b=2, **a): pass')
        test1('def f(g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(h, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(i, /, h, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j, i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, e, d, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, c=3, b=2, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, e, d, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, *f, **a): pass')
        test1('def f(j=7, i=6, /, h=5, g=4, **a): pass')
        test1('def f(j, i, /, h, g, **a): pass')
        test1('def f(j, i, /, **a): pass')
        test1('def f(j, i, /, *f, **a): pass')
        test1('def f(j=7, i=6, /, **a): pass')
        test1('def f(**a): pass')
        test1('def f(b=1, **a): pass')
        test1('def f(a, /): pass')
        test1('def f(a, /, b): pass')
        test1('def f(a, /, b, c=1): pass')
        test1('def f(a, /, b, c=1, *d): pass')
        test1('def f(a, /, b, c=1, *d, e): pass')
        test1('def f(a, /, b, c=1, *d, e, f=2): pass')
        test1('def f(a, /, b, c=1, *d, e, f=2, **g): pass')
        test1('def f(a=1, b=2, *e): pass')
        test1('def f(a, b, /, c, d, *e): pass')
        test1('def f(a, b, /, c, d=1, *e): pass')
        test1('def f(a, b, /, c=2, d=1, *e): pass')
        test1('def f(a, b=3, /, c=2, d=1, *e): pass')
        test1('def f(a=4, b=3, /, c=2, d=1, *e): pass')
        test1('def f(a, b=1, /, c=2, d=3, *e, f=4, **g): pass')
        test1('def __init__(self, max_size=0, *, ctx, pending_work_items, shutdown_lock, thread_wakeup): pass')

        def test2(src):
            f = FST.fromsrc(src).a.body[0].value.f
            m = list(f.walk(self_=False, recurse=False))

            l, c = [], None
            while c := f.next_child(c): l.append(c)
            self.assertEqual(l, m)

            l, c = [], None
            while c := f.prev_child(c): l.append(c)
            self.assertEqual(l, m[::-1])

        test2('call(a=1, *b)')
        test2('call()')
        test2('call(a, b)')
        test2('call(c=1, d=1)')
        test2('call(a, b, c=1, d=1)')
        test2('call(a, b, *c, d)')
        test2('call(a, b, *c, d=2)')
        test2('call(a, b=1, *c, d=2)')
        test2('call(a, b=1, *c, d=2, **e)')
        test2('system_message(message, level=level, type=type,*children, **kwargs)')

        if PYGE15:
            test2('[*i for i in j]')
            test2('{*i for i in j}')
            test2('(*i for i in j)')
            test2('{i: j for i, j in k}')
            test2('{**i for i, j in k}')

    def test_walk_vs_next_prev_tricky_nodes(self):
        def test(fst_, expect):
            expect_back = expect[::-1]

            self.assertEqual(list(f.src for f in fst_.walk(self_=False, recurse=False)), expect)
            self.assertEqual(list(f.src for f in fst_.walk(self_=False, recurse=False, back=True)), expect_back)

            l = [f := fst_.first_child()]
            while f := f.next():
                l.append(f)
            self.assertEqual(list(f.src for f in l), expect)

            l = [f := fst_.last_child()]
            while f := f.prev():
                l.append(f)
            self.assertEqual(list(f.src for f in l), expect_back)

        test(FST('a, /', arguments), ['a'])
        test(FST('a', arguments), ['a'])
        test(FST('*a', arguments), ['a'])
        test(FST('*, a', arguments), ['a'])
        test(FST('**a', arguments), ['a'])
        test(FST('a, b, /', arguments), ['a', 'b'])
        test(FST('a=1, /', arguments), ['a', '1'])
        test(FST('a, b=1, /', arguments), ['a', 'b', '1'])
        test(FST('a=1, b=2, /', arguments), ['a', '1', 'b', '2'])
        test(FST('a, b', arguments), ['a', 'b'])
        test(FST('a=1', arguments), ['a', '1'])
        test(FST('a, b=1', arguments), ['a', 'b', '1'])
        test(FST('a=1, b=2', arguments), ['a', '1', 'b', '2'])
        test(FST('a, b, /, c, d', arguments), ['a', 'b', 'c', 'd'])
        test(FST('a, b, /, c, d=1', arguments), ['a', 'b', 'c', 'd', '1'])
        test(FST('a, b, /, c=2, d=1', arguments), ['a', 'b', 'c', '2', 'd', '1'])
        test(FST('a, b=3, /, c=2, d=1', arguments), ['a', 'b', '3', 'c', '2', 'd', '1'])
        test(FST('a=4, b=3, /, c=2, d=1', arguments), ['a', '4', 'b', '3', 'c', '2', 'd', '1'])
        test(FST('*, a, b', arguments), ['a', 'b'])
        test(FST('*, a, b=1', arguments), ['a', 'b', '1'])
        test(FST('*, a=1, b=1', arguments), ['a', '1', 'b', '1'])
        test(FST('*, a=1, b', arguments), ['a', '1', 'b'])

        test(FST('call(a)'), ['call', 'a'])
        test(FST('call(a=b)'), ['call', 'a=b'])
        test(FST('call(a, b)'), ['call', 'a', 'b'])
        test(FST('call(a, b, *c)'), ['call', 'a', 'b', '*c'])
        test(FST('call(a, b, *c, d=e)'), ['call', 'a', 'b', '*c', 'd=e'])
        test(FST('call(a, b, *c, d=e, f=g)'), ['call', 'a', 'b', '*c', 'd=e', 'f=g'])
        test(FST('call(d=e, f=g)'), ['call', 'd=e', 'f=g'])
        test(FST('call(a=b, *c)'), ['call', 'a=b', '*c'])
        test(FST('call(a=b, c=d, *e)'), ['call', 'a=b', 'c=d', '*e'])
        test(FST('call(*c, d=e, f=g)'), ['call', '*c', 'd=e', 'f=g'])
        test(FST('call(a=b, *c, *d)'), ['call', 'a=b', '*c', '*d'])
        test(FST('call(e, a=b, *c, *d)'), ['call', 'e', 'a=b', '*c', '*d'])
        test(FST('call(*e, a=b, *c, *d)'), ['call', '*e', 'a=b', '*c', '*d'])
        test(FST('call(a, d=e, *c)'), ['call', 'a', 'd=e', '*c'])
        test(FST('call(a, *b, d=e, *c)'), ['call', 'a', '*b', 'd=e', '*c'])
        test(FST('call(*b, d=e, *c, f=g)'), ['call', '*b', 'd=e', '*c', 'f=g'])
        test(FST('call(d=e, *c)'), ['call', 'd=e', '*c'])
        test(FST('call(d=e, *c, *d)'), ['call', 'd=e', '*c', '*d'])
        test(FST('call(d=e, *c, a=b)'), ['call', 'd=e', '*c', 'a=b'])
        test(FST('call(a=b, d=e, *c, f=g)'), ['call', 'a=b', 'd=e', '*c', 'f=g'])
        test(FST('call(a, *b, d=e, *c, f=g)'), ['call', 'a', '*b', 'd=e', '*c', 'f=g'])
        test(FST('call(a=b, *c, d=e, *f, g=h, i=j, *k, *l)'), ['call', 'a=b', '*c', 'd=e', '*f', 'g=h', 'i=j', '*k', '*l'])

        test(FST('class cls(a): pass'), ['a', 'pass'])
        test(FST('class cls(a=b): pass'), ['a=b', 'pass'])
        test(FST('class cls(a, b): pass'), ['a', 'b', 'pass'])
        test(FST('class cls(a, b, *c): pass'), ['a', 'b', '*c', 'pass'])
        test(FST('class cls(a, b, *c, d=e): pass'), ['a', 'b', '*c', 'd=e', 'pass'])
        test(FST('class cls(a, b, *c, d=e, f=g): pass'), ['a', 'b', '*c', 'd=e', 'f=g', 'pass'])
        test(FST('class cls(d=e, f=g): pass'), ['d=e', 'f=g', 'pass'])
        test(FST('class cls(a=b, *c): pass'), ['a=b', '*c', 'pass'])
        test(FST('class cls(a=b, c=d, *e): pass'), ['a=b', 'c=d', '*e', 'pass'])
        test(FST('class cls(*c, d=e, f=g): pass'), ['*c', 'd=e', 'f=g', 'pass'])
        test(FST('class cls(a=b, *c, *d): pass'), ['a=b', '*c', '*d', 'pass'])
        test(FST('class cls(e, a=b, *c, *d): pass'), ['e', 'a=b', '*c', '*d', 'pass'])
        test(FST('class cls(*e, a=b, *c, *d): pass'), ['*e', 'a=b', '*c', '*d', 'pass'])
        test(FST('class cls(a, d=e, *c): pass'), ['a', 'd=e', '*c', 'pass'])
        test(FST('class cls(a, *b, d=e, *c): pass'), ['a', '*b', 'd=e', '*c', 'pass'])
        test(FST('class cls(*b, d=e, *c, f=g): pass'), ['*b', 'd=e', '*c', 'f=g', 'pass'])
        test(FST('class cls(d=e, *c): pass'), ['d=e', '*c', 'pass'])
        test(FST('class cls(d=e, *c, *d): pass'), ['d=e', '*c', '*d', 'pass'])
        test(FST('class cls(d=e, *c, a=b): pass'), ['d=e', '*c', 'a=b', 'pass'])
        test(FST('class cls(a=b, d=e, *c, f=g): pass'), ['a=b', 'd=e', '*c', 'f=g', 'pass'])
        test(FST('class cls(a, *b, d=e, *c, f=g): pass'), ['a', '*b', 'd=e', '*c', 'f=g', 'pass'])
        test(FST('class cls(a=b, *c, d=e, *f, g=h, i=j, *k, *l): pass'), ['a=b', '*c', 'd=e', '*f', 'g=h', 'i=j', '*k', '*l', 'pass'])

    def test_walk_vs_next_prev_field_combinations(self):
        nodes = {
            Module:             'a',
            Interactive:        'a',
            Expression:         'a',
            FunctionDef:        'def f(a) -> b: c',
            AsyncFunctionDef:   'async def f(a) -> b: c',
            ClassDef:           'class cls(a, b=c): c',
            Return:             'return a',
            Delete:             'del a',
            Assign:             'a = b',
            AugAssign:          'a += b',
            AnnAssign:          'a: b = c',
            For:                'for a in b: c',
            AsyncFor:           'async for a in b: c',
            While:              'while a: b',
            If:                 'if a: b',
            With:               'with a: b',
            AsyncWith:          'async with a: b',
            Match:              'match a:\n  case b: c',
            Raise:              'raise a from b',
            Try:                'try: a\nexcept: b\nelse: c\nfinally: d',
            Assert:             'assert a, b',
            Import:             'import a',
            ImportFrom:         'from .a import b',
            Global:             'global a',
            Nonlocal:           'nonlocal a',
            Expr:               'a',
            Pass:               'pass',
            Break:              'break',
            Continue:           'continue',
            BoolOp:             'a and b',
            NamedExpr:          'a := b',
            BinOp:              'a + b',
            UnaryOp:            '-a',
            Lambda:             'lambda a: b',
            IfExp:              'a if b else c',
            Dict:               '{a: b}',
            Set:                '{a}',
            ListComp:           '[a for b in c]',
            SetComp:            '{a for b in c}',
            DictComp:           '{a: b for c in d}',
            GeneratorExp:       '(a for b in c)',
            Await:              'await a',
            Yield:              'yield a',
            YieldFrom:          'yield from a',
            Compare:            'a < b',
            Call:               'f(a, b=c)',
            FormattedValue:     '',  # parse not supported
            Interpolation:      '',  # parse not supported
            JoinedStr:          'f"{1:<2}"',
            Constant:           'u"a"',
            Attribute:          'a.b',
            Subscript:          'a[b]',
            Starred:            '*a',
            Name:               'a',
            List:               '[a]',
            Tuple:              '(a,)',
            Slice:              'a:b:c',
            Load:               ' ',
            Store:              ' ',
            Del:                ' ',
            And:                'and',
            Or:                 'or',
            Add:                '+',
            Sub:                '-',
            Mult:               '*',
            MatMult:            '@',
            Div:                '/',
            Mod:                '%',
            Pow:                '**',
            LShift:             '<<',
            RShift:             '>>',
            BitOr:              '|',
            BitXor:             '^',
            BitAnd:             '&',
            FloorDiv:           '//',
            Invert:             '~',
            Not:                'not',
            UAdd:               '+',
            USub:               '-',
            Eq:                 '==',
            NotEq:              '!=',
            Lt:                 '<',
            LtE:                '<=',
            Gt:                 '>',
            GtE:                '>=',
            Is:                 'is',
            IsNot:              'is not',
            In:                 'in',
            NotIn:              'not in',
            comprehension:      'for a in b if c',
            ExceptHandler:      'except a as b: c',
            arguments:          'a, /, b=c, *d, e=f, **g',
            arg:                'a: b',
            keyword:            'a=b',
            alias:              'a as b',
            withitem:           'a as b',
            match_case:         'case a if b: c',
            MatchValue:         '1',
            MatchSingleton:     'None',
            MatchSequence:      '[a]',
            MatchMapping:       '{1: a, **b}',
            MatchClass:         'a(b, c=d)',
            MatchStar:          '*s',
            MatchAs:            'a',
            MatchOr:            'a | b',
            _ExceptHandlers:    'except: a',
            _match_cases:       'case a: b',
            _Assign_targets:    'a =',
            _decorator_list:    '@a',
            _comprehensions:    'for a in b',
            _comprehension_ifs: 'if a',
            _aliases:           'a as b',
            _withitems:         'a as b',
        }

        if PYGE11:
            nodes.update({
                TryStar: 'try: a\nexcept* b: c\nelse: d\nfinally: e',
            })

        if PYGE12:
            nodes.update({
                FunctionDef:      'def f[a](b) -> c: d',
                AsyncFunctionDef: 'async def f[a](b) -> c: d',
                ClassDef:         'class cls[a](b, c=d): e',
                TypeAlias:        'type t[a] = b',
                TypeVar:          'a: b',
                ParamSpec:        '**a',
                TypeVarTuple:     '*a',
                _type_params:     'a',
            })

        if PYGE13:
            nodes.update({
                TypeVar:      'a: b = c',
                ParamSpec:    '**a = b',
                TypeVarTuple: '*a = b',
            })

        if PYGE14:
            nodes.update({
                TemplateStr: 't"{1:<2}"',
            })


        # try to delete all combinations of fields and the ones that succeed walk and make sure walk() matches next()/prev() and all nodes expected are there

        for ast_cls, src in nodes.items():
            if not src:  # skip FormattedValue and Interpolation
                continue

            deletions = None
            copy_src = None

            try:
                fst_ = FST(src, ast_cls)
                ast_fields = []

                for field, child in iter_fields(fst_.a):
                    if child and (isinstance(child, AST) or (isinstance(child, list) and isinstance(child[0], AST))):
                        ast_fields.append(field)

                if not ast_fields:  # if no children then nothing to compare traversal of
                    self.assertIsNone(fst_.first_child())
                    self.assertIsNone(fst_.last_child())

                    continue

                astfields = [f.pfield for f in fst_.walk(True, self_=False, recurse=False)]  # will have duplicate field names (but not indexes) for BoolOp and MatchOr, its fine for what we are doing
                nastfields = len(ast_fields)

                self.assertEqual(list(sorted({af.name for af in astfields})), list(sorted(ast_fields)))  # check that our fields match what ast module says should be there

                for deletions in sum((list(combinations(range(nastfields), i)) for i in range(0, nastfields + 1)), []):
                    copy = fst_.copy()
                    copy_astfields = astfields.copy()

                    try:
                        for i in reversed(deletions):
                            field, idx = astfields[i]
                            is_arguments = isinstance((n := getattr(copy, field)), FST) and n.is_arguments

                            if ast_cls not in (BoolOp, MatchOr):
                                delattr(copy, field)  # for coverage
                            else:
                                copy.put(None, idx, field)

                            if not is_arguments:  # because this doesn't go away when deleted
                                del copy_astfields[i]

                    except (ValueError, NotImplementedError, NodeError):  # skip combinations that can't be deleted together
                        continue

                    copy_src = copy.src

                    # check forward

                    if f := copy.first_child(True):
                        nodes_walk = list(copy.walk(True, self_=False, recurse=False))
                        nodes_next = [f]

                        while f := f.next(True):
                            nodes_next.append(f)

                        self.assertEqual(nodes_next, nodes_walk)

                        if ast_cls not in (BoolOp, MatchOr):
                            self.assertEqual(copy_astfields, [n.pfield for n in nodes_next])

                    # check backward

                    if f := copy.last_child(True):
                        nodes_prev = [f]
                        nodes_walk = list(copy.walk(True, self_=False, recurse=False, back=True))

                        if f:
                            while f := f.prev(True):
                                nodes_prev.append(f)

                        self.assertEqual(nodes_prev, nodes_walk)

                        if ast_cls not in (BoolOp, MatchOr):
                            self.assertEqual(copy_astfields, [n.pfield for n in nodes_prev[::-1]])

            except Exception:
                print(f'\nast_cls={ast_cls.__name__}, {src=}, {deletions=}, {copy_src=}')

                raise

    def test_walk_vs_next_prev_list_fields(self):
        nodes = {
            Module:             ('a\nb', ['a', 'b']),
            Interactive:        ('a; b', ['a', 'b']),
            FunctionDef:        ('def f(): a; b', ['', 'a', 'b']),
            AsyncFunctionDef:   ('async def f(): a; b', ['', 'a', 'b']),
            ClassDef:           ('class cls(a, b, c=c, d=d): e; f', ['a', 'b', 'c=c', 'd=d', 'e', 'f']),
            Delete:             ('del a, b', ['a', 'b']),
            Assign:             ('a = b = c', ['a', 'b', 'c']),
            For:                ('for a in b: c; d', ['a', 'b', 'c', 'd']),
            AsyncFor:           ('async for a in b: c; d', ['a', 'b', 'c', 'd']),
            While:              ('while a: b; c', ['a', 'b', 'c']),
            If:                 ('if a: b; c', ['a', 'b', 'c']),
            With:               ('with a, b: c; d', ['a', 'b', 'c', 'd']),
            AsyncWith:          ('async with a, b: c; d', ['a', 'b', 'c', 'd']),
            Match:              ('match a:\n  case b: c\n  case d: e', ['a', 'case b: c', 'case d: e']),
            Try:                ('try: a; b\nexcept c: c\nexcept d: d\nelse: e; f\nfinally: g; h', ['a', 'b', 'except c: c', 'except d: d', 'e', 'f', 'g', 'h']),
            Import:             ('import a, b', ['a', 'b']),
            ImportFrom:         ('from . import a, b', ['a', 'b']),
            BoolOp:             ('a and b', ['a', 'b']),
            Dict:               ('{a: b, c: d}', ['a', 'b', 'c', 'd']),
            Set:                ('{a, b}', ['a', 'b']),
            ListComp:           ('[a for b in b for c in c]', ['a', 'for b in b', 'for c in c']),
            SetComp:            ('{a for b in b for c in c}', ['a', 'for b in b', 'for c in c']),
            DictComp:           ('{a: b for c in c for d in d}', ['a', 'b', 'for c in c', 'for d in d']),
            GeneratorExp:       ('(a for b in b for c in c)', ['a', 'for b in b', 'for c in c']),
            Compare:            ('a < b > c', ['a', '<', 'b', '>', 'c']),
            Call:               ('call(a, b, c=d, e=f)', ['call', 'a', 'b', 'c=d', 'e=f']),
            List:               ('[a, b]', ['a', 'b']),
            Tuple:              ('(a, b)', ['a', 'b']),
            comprehension:      ('for a in b if c if d', ['a', 'b', 'c', 'd']),
            arguments:          ('a=b, /, c=d, *e, f=g, h=i, **j', ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']),
            MatchSequence:      ('[a, b]', ['a', 'b']),
            MatchMapping:       ('{1: a, 2: b}', ['1', 'a', '2', 'b']),
            MatchClass:         ('a(b, c, d=e, f=g)', ['a', 'b', 'c', 'e', 'g']),
            MatchOr:            ('a | b', ['a', 'b']),
            _ExceptHandlers:    ('except: a\nexcept: b', ['except: a', 'except: b']),
            _match_cases:       ('case a: _\ncase b: _', ['case a: _', 'case b: _']),
            _Assign_targets:    ('a = b =', ['a', 'b']),
            _decorator_list:    ('@a\n@b', ['a', 'b']),
            _comprehensions:    ('for a in a for b in b', ['for a in a', 'for b in b']),
            _comprehension_ifs: ('if a if b', ['a', 'b']),
            _aliases:           ('a as a, b as b', ['a as a', 'b as b']),
            _withitems:         ('a as a, b as b', ['a as a', 'b as b']),
        }

        if PYGE11:
            nodes.update({
                TryStar: ('try: a; b\nexcept* c: c\nexcept* d: d\nelse: e; f\nfinally: g; h', ['a', 'b', 'except* c: c', 'except* d: d', 'e', 'f', 'g', 'h']),
            })

        if PYGE12:
            nodes.update({
                FunctionDef:      ('def f[a, *b, **c]() -> d: e', ['a', '*b', '**c', '', 'd', 'e']),
                AsyncFunctionDef: ('async def f[a, *b, **c]() -> d: e', ['a', '*b', '**c', '', 'd', 'e']),
                ClassDef:         ('class cls[a, *b, **c](d, e, f=f, g=g): h', ['a', '*b', '**c', 'd', 'e', 'f=f', 'g=g', 'h']),
                TypeAlias:        ('type t[a, *b, **c] = d', ['t', 'a', '*b', '**c', 'd']),
                JoinedStr:        ('f"a{b}c"', ['a', '{b}', 'c']),
                _type_params:     ('a, b', ['a', 'b']),
            })

        if PYGE13:
            nodes.update({
            })

        if PYGE14:
            nodes.update({
                TemplateStr: ('t"a{b}c"', ['a', '{b}', 'c']),
            })


        for ast_cls, (src, nodes_srcs) in nodes.items():
            try:
                # forward

                fst_ = FST(src, ast_cls)

                nodes_next = []

                if f := fst_.first_child('loc'):
                    nodes_next.append(f.src)

                    while f := f.next('loc'):
                        nodes_next.append(f.src)

                self.assertEqual(nodes_next, nodes_srcs)
                self.assertEqual(nodes_next, [f.src for f in fst_.walk('loc', self_=False, recurse=False)])

                # backward

                fst_ = FST(src, ast_cls)

                nodes_prev = []

                if f := fst_.last_child('loc'):
                    nodes_prev.append(f.src)

                    while f := f.prev('loc'):
                        nodes_prev.append(f.src)

                self.assertEqual(nodes_prev, nodes_srcs[::-1])
                self.assertEqual(nodes_prev, [f.src for f in fst_.walk('loc', self_=False, recurse=False, back=True)])

            except Exception:
                print(f'\nast_cls={ast_cls.__name__}, {src=}, {nodes_srcs=}')

                raise

    def test_step_vs_walk(self):
        def test(src, all=None):
            fst = FST.fromsrc(src.strip())

            f, l = fst, []
            while f := f.step_fwd(False):
                l.append(f)
            self.assertEqual(l, list(fst.walk(False, self_=False)))

            f, l = fst, []
            while f := f.step_fwd(True):
                l.append(f)
            self.assertEqual(l, list(fst.walk(True, self_=False)))

            f, l = fst, []
            while f := f.step_back(False):
                l.append(f)
            self.assertEqual(l, list(fst.walk(False, self_=False, back=True)))

            f, l = fst, []
            while f := f.step_back(True):
                l.append(f)
            self.assertEqual(l, list(fst.walk(True, self_=False, back=True)))

            if all is not None:
                f, l = fst, []
                while f := f.step_fwd(all):
                    l.append(f)
                self.assertEqual(l, list(fst.walk(all, self_=False)))

                f, l = fst, []
                while f := f.step_back(all):
                    l.append(f)
                self.assertEqual(l, list(fst.walk(all, self_=False, back=True)))

        test('''
def f(a=1, b=2) -> int:
    i = [[k for k in range(j)] for i in range(5) if i for j in range(i) if j]
            ''')

        test('''
match a:
    case 1 | 2:
          pass
            ''')

        test('''
with a as b, c as d:
    pass
            ''')

        if PYGE15:
            test('''
[*s for s in t]
{*s for s in t}
(*s for s in t)
{i: k for i, j in k}
{**i for i, j in k}
            ''')

        test('[a, [c], [2, 3, [b]]]', Name)
        test('[a, [c], [2, 3, [b]]]', Constant)

    def test_child_path(self):
        f = parse('if 1: a = (1, 2, {1: 2})').f
        p = f.child_path(f.body[0].body[0].value.elts[2].keys[0], True)

        self.assertEqual(p, 'body[0].body[0].value.elts[2].keys[0]')
        self.assertIs(f.child_from_path(p), f.body[0].body[0].value.elts[2].keys[0])

        p = f.child_path(f.body[0].body[0].value.elts[2].keys[0], False)

        self.assertEqual(p, [astfield(name='body', idx=0), astfield(name='body', idx=0),
                             astfield(name='value', idx=None), astfield(name='elts', idx=2),
                             astfield(name='keys', idx=0)])
        self.assertIs(f.child_from_path(p), f.body[0].body[0].value.elts[2].keys[0])

        self.assertRaises(ValueError, f.child_path, parse('1').f)

        f = FST('i = [a, b]')
        self.assertRaises(ValueError, f.value.elts[0].child_path, f.value.elts[1])

    def test_get_src_clip(self):
        f = FST('if 1:\n    j = 2\n    pass')

        self.assertEqual('if', f.get_src(-999, -999, 0, 2))
        self.assertEqual('pass', f.get_src(2, 4, 999, 999))
        self.assertEqual('if 1:\n    j = 2\n    pass', f.get_src(-999, -999, 999, 999))
        self.assertEqual('    j = 2', f.get_src(1, -999, 1, 999))
        self.assertEqual('1:\n    j = 2\n    p', f.get_src(-999, 3, 999, 5))

        self.assertRaises(IndexError, f.get_src, 2, 0, 1, 0)
        self.assertRaises(IndexError, f.get_src, 1, 2, 1, 1)

        self.assertEqual('= 2\n', f.get_src(-2, -3, -1, 0))
        self.assertEqual('j =', f.get_src(-2, -5, -2, -2))
        self.assertEqual('if 1:', f.get_src(-3, 0, -3, 'end'))
        self.assertEqual('s', f.get_src(-1, -1, 'end', 'end'))
        self.assertEqual('', f.get_src('end', 'end', 'end', 'end'))

    def test_put_src_clip(self):
        f = FST('if 1:\n    j = 2\n    pass')

        f.put_src('if', -999, -999, 0, 2)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        f.put_src('pass', 2, 4, 999, 999)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        f.put_src('if 1:\n    j = 2\n    pass', -999, -999, 999, 999)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        f.put_src('    j = 2', 1, -999, 1, 999)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        f.put_src('1:\n    j = 2\n    p', -999, 3, 999, 5)
        self.assertEqual('if 1:\n    j = 2\n    pass', f.src)
        f.verify()

        self.assertRaises(IndexError, f.put_src, None, 2, 0, 1, 0)
        self.assertRaises(IndexError, f.put_src, None, 1, 2, 1, 1)

        f.put_src('call()\n', -2, -5, 'end', 0)
        self.assertEqual('if 1:\n    call()\n    pass', f.src)
        f.verify()

        f.put_src('True:', -3, -2, 0, 'end')
        self.assertEqual('if True:\n    call()\n    pass', f.src)
        f.verify()

    def test_put_src_reparse(self):
        for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_SRC_REPARSE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                eln, ecol = f.put_src(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root
                g = f.root.find_loc(ln, col, eln, ecol)

                tdst  = f.root.src
                tdump = f.root.dump(out='lines')

                f.root.verify(raise_=True)

                self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst, put_src)
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, attr, (ln, col, end_ln, end_col), src, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_src_reparse_random_same(self):
        seed(rndseed := randint(0, 0x7fffffff))

        try:
            master = parse('''
def f():
    i = 1

async def af():
    i = 2

class cls:
    i = 3

for _ in ():
    i = 4
else:
    i = 5

async for _ in ():
    i = 6
else:
    i = 7

while _:
    i = 8
else:
    i = 9

if _:
    i = 10
elif _:
    i = 11
else:
    i = 12

with _:
    i = 13

async with _:
    i = 14

match _:
    case 15:
        i = 15

    case 16:
        i = 16

    case 17:
        i = 17

try:
    i = 18
except Exception as e:
    i = 19
except ValueError as v:
    i = 20
except:
    i = 21
else:
    i = 22
finally:
    i = 23
                '''.strip()).f

            lines = master._lines

            for i in range(100):
                copy      = master.copy()
                ln        = randint(0, len(lines) - 1)
                col       = randint(0, len(lines[ln]))
                end_ln    = randint(ln, len(lines) - 1)
                end_col   = randint(col if end_ln == ln else 0, len(lines[end_ln]))
                put_lines = master._get_src(ln, col, end_ln, end_col, True)

                copy.put_src(put_lines, ln, col, end_ln, end_col)
                copy.verify()

                compare_asts(master.a, copy.a, locs=True, raise_=True)

                assert copy.src == master.src

        except Exception:
            print('Random seed was:', rndseed)
            print(i, ln, col, end_ln, end_col)
            print('-'*80)
            print(copy.src)

            raise

    def test_put_src_reparse_special(self):
        # tabs

        src = '''
if u:
\tif a:
\t\tpass
\telif x:
\t\tif y:
\t\t\toutput.append('/')
\t\tif z:
\t\t\tpass
\t\t\t# directory (with paths underneath it). E.g., "foo" matches "foo",
\t\t\tpass
            '''.strip()
        f = FST(src)
        s = f._get_src(5, 8, 8, 14)
        f.put_src(s, 5, 8, 8, 14)
        self.assertEqual(f.src, src)
        f.verify()

        f = FST('''
if u:
\tmatch x:
\t\tcase 1:
\t\t\ti = 2
            '''.strip())
        f.put_src('2', 2, 7, 2, 8)
        self.assertEqual(f.src, '''
if u:
\tmatch x:
\t\tcase 2:
\t\t\ti = 2
            '''.strip())
        f.verify()

        f = FST('''
if u:
\tmatch x:
\t\tcase 1:
\t\t\ti = 2
            '''.strip())
        f.put_src('2:\n\t\t\tj', 2, 7, 3, 4)
        self.assertEqual(f.src, '''
if u:
\tmatch x:
\t\tcase 2:
\t\t\tj = 2
            '''.strip())
        f.verify()

        # comments trailing single global root statement

        src = '''
if u:
  if a:
    pass
  elif x:
    if y:
      output.append('/')
    if z:
      pass
      # directory (with paths underneath it). E.g., "foo" matches "foo",
            '''.strip()
        f = FST(src)
        s = f._get_src(5, 8, 8, 14)
        f.put_src(s, 5, 8, 8, 14)
        self.assertEqual(f.src, src)
        f.verify()

        # semicoloned statements

        f = FST('\na; b = 1; c')
        f.put_src(' = 2', 1, 4, 1, 8)
        self.assertEqual('\na; b = 2; c', f.src)
        f.verify()

        f = FST('aaa;b = 1; c')
        f.put_src(' = 2', 0, 5, 0, 9)
        self.assertEqual('aaa;b = 2; c', f.src)
        f.verify()

        f = FST('a;b = 1; c')
        self.assertRaises(NotImplementedError, f.put_src, ' = 2', 0, 3, 0, 7)
        f.verify()

        f = FST('a; b = 1; c')
        self.assertRaises(NotImplementedError, f.put_src, ' = 2', 0, 4, 0, 8)
        f.verify()

        # line continuations

        f = FST('\\\nb = 1')
        f.put_src(' = 2', 1, 1, 1, 5)
        self.assertEqual('\\\nb = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\nb = 1')
        f.put_src(' = 2', 2, 1, 2, 5)
        self.assertEqual('if 1:\n \\\nb = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\n b = 1')
        f.put_src(' = 2', 2, 2, 2, 6)
        self.assertEqual('if 1:\n \\\n b = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\n  b = 1')
        f.put_src(' = 2', 2, 3, 2, 7)
        self.assertEqual('if 1:\n \\\n  b = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\naa; b = 1')
        f.put_src(' = 2', 2, 5, 2, 9)
        self.assertEqual('if 1:\n \\\naa; b = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\n a; b = 1')
        f.put_src(' = 2', 2, 5, 2, 9)
        self.assertEqual('if 1:\n \\\n a; b = 2', f.src)
        f.verify()

        f = FST('if 1:\n \\\n  a;b = 1')
        f.put_src(' = 2', 2, 5, 2, 9)
        self.assertEqual('if 1:\n \\\n  a;b = 2', f.src)
        f.verify()

        if PYGE11:
            # make sure TryStar reparses to TryStar

            f = FST('''
try:
    raise Exception('yarr!')
except* BaseException:
    hit_except = True
finally:
    hit_finally = True
                '''.strip())
            f.put_src('ry', 0, 1, 0, 3)
            self.assertIsInstance(f.a, TryStar)
            f.verify()

        # statement that lives on compound block header line

        f = FST(src := r'''
if 1:
    if \
 args:args=['-']
            '''.strip())
        f.put_src('', 2, 15, 2, 15)
        self.assertEqual(src, f.src)
        f.verify()

        # calling on a node which is not in the location of source being changed

        f = FST(r'''
if 1: pass
else:
    if 2:
        i = 3
            '''.strip(), 'exec')
        f.body[0].orelse[0].body[0].value.put_src(r'''
if 2:
    if 3:
        j +='''.strip(), 1, 2, 3, 11)
        self.assertEqual(r'''
if 1: pass
elif 2:
    if 3:
        j += 3
            '''.strip(), f.src)
        f.verify()

        # leading multibyte chars replaced with spaces during reparse

        (f := FST('f(д);f(d)', 'exec')).put_src('g', 0, 5, 0, 6)
        self.assertEqual('f(д);g(d)', f.root.src)
        f.verify()

        (f := FST(r'''
if 1:
    f(д);f(d)
            '''.strip(), 'exec')).put_src("g", 1, 9, 1, 10)
        self.assertEqual(r'''
if 1:
    f(д);g(d)
            '''.strip(), f.root.src)
        f.verify()

        self.assertRaises(ValueError, FST('i').put_src, 'i', 0, 0, 0, 1, 'INVALID')

        self.assertEqual((1, 1), (f := FST('i')).put_src(['a', 'b'], 0, 0, 0, 1, None))  # misc, not really reparse
        self.assertEqual('a\nb', f.src)

        # reparse FormattedValue and Interpolation crating and destroying self-documenting debug Constant

        f = FST('f"{a}"')
        f.put_src('=', 0, 4, 0, 4)
        f.verify()

        f = FST('f"{a=}"')
        f.put_src(None, 0, 4, 0, 5)
        f.verify()

        if PYGE14:
            f = FST('t"{a}"')
            f.put_src('=', 0, 4, 0, 4)
            f.verify()

            f = FST('t"{a=}"')
            f.put_src(None, 0, 4, 0, 5)
            f.verify()

    def test_put_src_offset(self):
        f = FST('a, b, c')
        f.put_src(' ', 0, 0, 0, 0, 'offset')
        self.assertEqual(' a, b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 1, 0, 2), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 1, 0, 1, 'offset')
        self.assertEqual('a , b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 3, 0, 3, 'offset')
        self.assertEqual('a,  b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 4, 0, 4, 'offset')
        self.assertEqual('a, b , c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 6, 0, 6, 'offset')
        self.assertEqual('a, b,  c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.put_src(' ', 0, 7, 0, 7, 'offset')
        self.assertEqual('a, b, c ', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 6, 0, 7), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[0].put_src(' ', 0, 0, 0, 0, 'offset')
        self.assertEqual(' a, b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 2), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[0].put_src(' ', 0, 1, 0, 1, 'offset')
        self.assertEqual('a , b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 2), f.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[1].put_src(' ', 0, 3, 0, 3, 'offset')
        self.assertEqual('a,  b, c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[1].put_src(' ', 0, 4, 0, 4, 'offset')
        self.assertEqual('a, b , c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 5), f.elts[1].loc)
        self.assertEqual((0, 7, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[2].put_src(' ', 0, 6, 0, 6, 'offset')
        self.assertEqual('a, b,  c', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 6, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        f.elts[2].put_src(' ', 0, 7, 0, 7, 'offset')
        self.assertEqual('a, b, c ', f.src)
        self.assertEqual((0, 0, 0, 8), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.elts[1].loc)
        self.assertEqual((0, 6, 0, 8), f.elts[2].loc)

        f = FST('a, b, c')
        self.assertRaises(ValueError, f.elts[0].put_src, ' ', 0, 2, 0, 2, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 2, 0, 2, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 5, 0, 5, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 2, 0, 4, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 3, 0, 5, 'offset')
        self.assertRaises(ValueError, f.elts[1].put_src, ' ', 0, 2, 0, 5, 'offset')

        self.assertRaises(ValueError, FST('a').ctx.put_src, '', 0, 0, 0, 0, 'offset')

        # special case of modifying exactly inside FormattedValue or Interpolation

        if PYGE12:
            f = FST('f"{a+b=}"')
            f.values[1].put_src(' ', 0, 7, 0, 7, 'offset')
            f.values[1].put_src(' ', 0, 6, 0, 6, 'offset')
            f.values[1].put_src(' ', 0, 5, 0, 5, 'offset')
            f.values[1].put_src(' ', 0, 4, 0, 4, 'offset')
            f.values[1].put_src(' ', 0, 3, 0, 3, 'offset')
            f.verify()
            self.assertEqual(f.values[0].value, ' a + b = ')

        if PYGE14:
            f = FST('t"{a+b=}"')
            f.values[1].put_src(' ', 0, 7, 0, 7, 'offset')
            f.values[1].put_src(' ', 0, 6, 0, 6, 'offset')
            f.values[1].put_src(' ', 0, 5, 0, 5, 'offset')
            f.values[1].put_src(' ', 0, 4, 0, 4, 'offset')
            f.values[1].put_src(' ', 0, 3, 0, 3, 'offset')
            f.verify()
            self.assertEqual(f.values[0].value, ' a + b = ')

    def test_dedent_multiline_strings(self):
        f = parse('''
class cls:
    def func():
        i = """This is a
        normal
        multiline string"""

        j = ("This is a "
        "split "
        "multiline string")

        k = f"""This is a
        normal
        multiline f-string"""

        l = (f"This is a "
        "split "
        f"multiline f-string")
            '''.strip()).body[0].body[0].f
        self.assertEqual('''
def func():
    i = """This is a
        normal
        multiline string"""

    j = ("This is a "
    "split "
    "multiline string")

    k = f"""This is a
        normal
        multiline f-string"""

    l = (f"This is a "
    "split "
    f"multiline f-string")
            '''.strip(), f.copy().src)

        f = parse('''
class cls:
    def func():
        l = (f"This is a "
        f"split " """
        super
        special
        """
        f"multiline f-string")
            '''.strip()).body[0].body[0].f
        self.assertEqual('''
def func():
    l = (f"This is a "
    f"split " """
        super
        special
        """
    f"multiline f-string")
            '''.strip(), f.copy().src)

    def test_copy_lines(self):
        src = 'class cls:\n if True:\n  i = 1\n else:\n  j = 2'
        ast = parse(src)

        self.assertEqual(src.split('\n'), ast.f._get_src(*ast.f.loc, True))
        self.assertEqual(src.split('\n'), ast.body[0].f._get_src(*ast.body[0].f.loc, True))
        self.assertEqual('if True:\n  i = 1\n else:\n  j = 2'.split('\n'), ast.body[0].body[0].f._get_src(*ast.body[0].body[0].f.loc, True))
        self.assertEqual(['i = 1'], ast.body[0].body[0].body[0].f._get_src(*ast.body[0].body[0].body[0].f.loc, True))
        self.assertEqual(['j = 2'], ast.body[0].body[0].orelse[0].f._get_src(*ast.body[0].body[0].orelse[0].f.loc, True))

        self.assertEqual(['True:', '  i'], ast.f.root._get_src(1, 4, 2, 3, True))

    def test_get_put_docstr(self):
        f = FST('''
class cls:
    """doc
bad
    string"""

    def f():
        """cod
dog
           ind
        bell"""
'''.strip())
        self.assertEqual('doc\nbad\nstring', f.get_docstr())
        self.assertEqual('cod\ndog\n   ind\nbell', f.body[1].get_docstr())

        f.body[1].put_docstr(None)
        f.put_docstr(None)

        self.assertEqual('''
class cls:

    def f():
'''.strip(), f.src)

        f.body[0].put_docstr("Hello\nWorld\n  ...")
        f.put_docstr('"""YAY!!!\n\'\'\'\\nHEY!!!\x00')

        self.assertEqual('''
class cls:
    \'\'\'"""YAY!!!
    \\'\\'\\'\\\\nHEY!!!\\x00\'\'\'


    def f():
        """Hello
        World
          ..."""
'''.strip(), f.src)

        f.put_docstr('"')

        self.assertEqual('\'\'\'"\'\'\'', f.body[0].src)

        f = FST('if 1: pass')
        self.assertIsNone(f.get_docstr())

        f.put_docstr('test')

        self.assertEqual('class cls: pass', FST('class cls: pass').put_docstr(None).src)

        f = FST('''
class cls:
    # pre-comment
    """docstr"""  # line-comment
    # post-comment
'''.strip())
        f.put_docstr('test', reput=True)
        self.assertEqual('''
class cls:
    """test"""
    # pre-comment
    # line-comment
    # post-comment
'''.strip(), f.src)

    def test_get_put_line_comment(self):
        f = FST('if a:# comment 0  \n  b\n  c # comment 1  \n  d ;\n  e ;  # comment 2  \n  f ; g\n  h \\\n\n  if i: j\n  if k: \\\n\n    l')

        self.assertEqual('comment 0', f.get_line_comment(full=False))
        self.assertEqual('# comment 0  ', f.get_line_comment(full=True))
        self.assertIsNone(f.body[0].get_line_comment(full=False))
        self.assertIsNone(f.body[0].get_line_comment(full=True))
        self.assertEqual('comment 1', f.body[1].get_line_comment(full=False))
        self.assertEqual(' # comment 1  ', f.body[1].get_line_comment(full=True))
        self.assertIsNone(f.body[2].get_line_comment(full=False))
        self.assertIsNone(f.body[2].get_line_comment(full=True))
        self.assertEqual('comment 2', f.body[3].get_line_comment(full=False))
        self.assertEqual('  # comment 2  ', f.body[3].get_line_comment(full=True))
        self.assertIsNone(f.body[4].get_line_comment(full=False))
        self.assertIsNone(f.body[4].get_line_comment(full=True))
        self.assertIsNone(f.body[5].get_line_comment(full=False))
        self.assertIsNone(f.body[5].get_line_comment(full=True))
        self.assertIsNone(f.body[6].get_line_comment(full=False))
        self.assertIsNone(f.body[6].get_line_comment(full=True))
        self.assertIsNone(f.body[7].get_line_comment(full=False))
        self.assertIsNone(f.body[7].get_line_comment(full=True))
        self.assertIsNone(f.body[8].get_line_comment(full=False))
        self.assertIsNone(f.body[8].get_line_comment(full=True))

        g = f.copy()
        g.body[8].put_line_comment('zzz', full=False)
        g.body[7].put_line_comment('zzz', full=False)
        g.body[6].put_line_comment('zzz', full=False)
        g.body[5].put_line_comment('zzz', full=False)
        g.body[4].put_line_comment('zzz', full=False)
        g.body[3].put_line_comment('zzz', full=False)
        g.body[2].put_line_comment('zzz', full=False)
        g.body[1].put_line_comment('zzz', full=False)
        g.body[0].put_line_comment('zzz', full=False)
        g.put_line_comment('zzz', full=False)

        self.assertEqual(g.src, r'''
if a:# zzz
  b  # zzz
  c # zzz
  d ;  # zzz
  e ;  # zzz
  f  # zzz
  g  # zzz
  h  # zzz

  if i:  # zzz
    j
  if k:  # zzz

    l
        '''.strip())

        g = f.copy()
        g.body[8].put_line_comment('#zzz', full=True)
        g.body[7].put_line_comment('#zzz', full=True)
        g.body[6].put_line_comment('#zzz', full=True)
        g.body[5].put_line_comment('#zzz', full=True)
        g.body[4].put_line_comment('#zzz', full=True)
        g.body[3].put_line_comment('#zzz', full=True)
        g.body[2].put_line_comment('#zzz', full=True)
        g.body[1].put_line_comment('#zzz', full=True)
        g.body[0].put_line_comment('#zzz', full=True)
        g.put_line_comment('#zzz', full=True)
        self.assertEqual(g.src, r'''
if a:#zzz
  b#zzz
  c#zzz
  d ;#zzz
  e ;#zzz
  f#zzz
  g#zzz
  h#zzz

  if i:#zzz
    j
  if k:#zzz

    l
        '''.strip())

        # block statement header without a body

        f = FST('if a: # comment\n  pass')
        del f.body

        self.assertEqual('comment', f.get_line_comment(full=False))
        self.assertEqual(' # comment', f.get_line_comment(full=True))

        self.assertEqual('comment', f.put_line_comment('blomment', full=False))
        self.assertEqual('if a: # blomment', f.lines[0])
        self.assertEqual('blomment', f.put_line_comment(' blomment  ', full=False))
        self.assertEqual('if a: # blomment  ', f.lines[0])
        self.assertEqual(' # blomment  ', f.put_line_comment('    # blomment    ',full=True))
        self.assertEqual('if a:    # blomment    ', f.lines[0])

        # orelse and finalbody

        f = FST('''
try: pass
except: pass
else: pass
finally: pass
            '''.strip())

        self.assertIsNone(f.get_line_comment(field='orelse', full=False))
        self.assertIsNone(f.get_line_comment(field='finalbody', full=True))

        self.assertIsNone(f.put_line_comment('zzz', field='orelse', full=False))
        self.assertIsNone(f.put_line_comment('zzz', field='finalbody', full=False))

        self.assertEqual(f.src, r'''
try: pass
except: pass
else:  # zzz
    pass
finally:  # zzz
    pass
        '''.strip())

        self.assertEqual('  # zzz', f.put_line_comment('#zzz', field='orelse', full=True))
        self.assertEqual('  # zzz', f.put_line_comment('#zzz', field='finalbody', full=True))

        self.assertEqual(f.src, r'''
try: pass
except: pass
else:#zzz
    pass
finally:#zzz
    pass
        '''.strip())

        self.assertEqual('zzz', f.put_line_comment(None, field='orelse', full=False))
        self.assertEqual('#zzz', f.put_line_comment(None, field='finalbody', full=True))

        self.assertEqual(f.src, r'''
try: pass
except: pass
else:
    pass
finally:
    pass
        '''.strip())

        # validate field

        self.assertRaises(ValueError, f.get_line_comment, 'blah')

        # for test coverage

        self.assertRaises(NotImplementedError, FST('expr').get_line_comment)
        self.assertRaises(ValueError, FST('stmt', 'stmt').put_line_comment, "can't\nhave\nnewline")
        self.assertRaises(ValueError, FST('stmt', 'stmt').put_line_comment, 'full must start with #', full=True)
        self.assertRaises(ValueError, FST('if 1: pass').put_line_comment, 'yay', 'orelse')
        self.assertIsNone(FST('stmt', 'stmt').put_line_comment(None))

        f = FST('a ; \\\n b')
        f.put_src(';', 1, 0, 1, 0, None)
        self.assertEqual('a ; \\\n; b', f.src)
        self.assertRaises(RuntimeError, f.body[0].put_line_comment, 'blah')

        f = FST('a \\\n; b')
        f.body[0].put_line_comment('blah')
        self.assertEqual('a  # blah\nb', f.src)

        f = FST('if z: a \\\n; b')
        f.body[0].put_line_comment('blah')
        self.assertEqual('if z:\n    a  # blah\n    b', f.src)

    def test_par(self):
        f = parse('1,').body[0].value.f.copy()
        f.par()
        self.assertEqual('(1,)', f.src)
        f.par()
        self.assertEqual('(1,)', f.src)
        f.par(force=True)
        self.assertEqual('((1,))', f.src)
        self.assertEqual((0, 1, 0, 5), f.loc)
        f.par()
        self.assertEqual('((1,))', f.src)
        self.assertEqual((0, 1, 0, 5), f.loc)

        # self.assertFalse(parse('()').body[0].value.f.copy().par())
        # self.assertFalse(parse('[]').body[0].value.f.copy().par())
        # self.assertFalse(parse('{}').body[0].value.f.copy().par())
        self.assertEqual('()', parse('()').body[0].value.f.copy().par().src)
        self.assertEqual('[]', parse('[]').body[0].value.f.copy().par().src)
        self.assertEqual('{}', parse('{}').body[0].value.f.copy().par().src)

        f = parse('i = 1').body[0].f.copy()
        f._put_src(['# comment', ''], 0, 0, 0, 0)
        f.par()
        self.assertEqual('# comment\ni = 1', f.src)
        f.par(force='invalid')
        self.assertEqual('(# comment\ni = 1)', f.src)

        if PYGE14:  # make sure parent Interpolation.str gets modified
            f = FST('t"{a}"', 'exec').body[0].value.copy()
            f.values[0].value.par(force=True)
            self.assertEqual('t"{(a)}"', f.src)
            self.assertEqual('(a)', f.values[0].str)

            f = FST('t"{a,}"', 'exec').body[0].value.copy()
            f.values[0].value.par(force=True)
            self.assertEqual('t"{(a,)}"', f.src)
            self.assertEqual('(a,)', f.values[0].str)

            f = FST('t"{a+b}"', 'exec').body[0].value.copy()
            f.values[0].value.par()
            self.assertEqual('t"{(a+b)}"', f.src)
            self.assertEqual('(a+b)', f.values[0].str)

        # grouping

        f = parse('[i]').f
        f.body[0].value.elts[0].par(force=True)
        self.assertEqual('[(i)]', f.src)
        self.assertEqual((0, 0, 0, 5), f.loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].value.loc)
        self.assertEqual((0, 2, 0, 3), f.body[0].value.elts[0].loc)

        f = parse('a + b').f
        f.body[0].value.left.par(force=True)
        f.body[0].value.right.par(force=True)
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)

        f = parse('a + b').f
        f.body[0].value.right.par(force=True)
        f.body[0].value.left.par(force=True)
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)
        f.body[0].value.par(force=True)
        self.assertEqual('((a) + (b))', f.src)
        f.body[0].value.left.par(force=True)
        self.assertEqual('(((a)) + (b))', f.src)
        f.body[0].value.right.par(force=True)
        self.assertEqual('(((a)) + ((b)))', f.src)

        f = parse('call(i for i in j)').f
        f.body[0].value.args[0].par(force=True)
        self.assertEqual(f.src, 'call((i for i in j))')
        f.body[0].value.args[0].par(force=True)
        self.assertEqual(f.src, 'call(((i for i in j)))')

        f = parse('i').body[0].value.f.copy()
        f._put_src('\n# post', 0, 1, 0, 1, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(True, whole=True)
        self.assertEqual((1, 0, 1, 1), f.loc)
        self.assertEqual(f.root.src, '(# pre\ni\n# post\n)')

        f = parse('i').body[0].value.f.copy()
        f._put_src('\n# post', 0, 1, 0, 1, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(True, whole=False)
        self.assertEqual((1, 1, 1, 2), f.loc)
        self.assertEqual(f.root.src, '# pre\n(i)\n# post')

        # Tuple

        f = parse('i,').f
        f.body[0].value.par()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('a, b').f
        f.body[0].value.par()
        self.assertEqual('(a, b)', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.elts[1].loc)

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(whole=True)
        self.assertEqual((0, 0, 3, 1), f.loc)
        self.assertEqual(f.src, '(# pre\ni,\n# post\n)')

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n\\', 0, 2, 0, 2, False)
        f.par(whole=True)
        self.assertEqual((0, 0, 1, 1), f.loc)
        self.assertEqual(f.src, '(i,\n)')

        f = parse('i,').body[0].value.f.copy()
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n(i,)\n# post')

        # MatchSequence

        f = FST('i,', pattern)
        f.par()
        self.assertEqual('[i,]', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 1, 0, 2), f.patterns[0].loc)

        f = FST('a, b', pattern)
        f.par()
        self.assertEqual('[a, b]', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 1, 0, 2), f.patterns[0].loc)
        self.assertEqual((0, 4, 0, 5), f.patterns[1].loc)

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(whole=True)
        self.assertEqual((0, 0, 3, 1), f.loc)
        self.assertEqual(f.src, '[# pre\ni,\n# post\n]')

        f = FST('i,', pattern)
        f._put_src('\n\\', 0, 2, 0, 2, False)
        f.par(whole=True)
        self.assertEqual((0, 0, 1, 1), f.loc)
        self.assertEqual(f.src, '[i,\n]')

        f = FST('i,', pattern)
        f._put_src('\n# post', 0, 2, 0, 2, False)
        f._put_src('# pre\n', 0, 0, 0, 0, False)
        f.par(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n[i,]\n# post')

        # special rules for Starred

        f = FST('*\na')
        f.par()
        self.assertEqual('*(\na)', f.src)
        f.verify()

        f.par()
        self.assertEqual('*(\na)', f.src)
        f.verify()

        f = FST('\n*\na\n')
        f.par()
        self.assertEqual('\n*(\na\n)', f.src)
        f.verify()

        f.par()
        self.assertEqual('\n*(\na\n)', f.src)
        f.verify()

        f = FST('\n*\na\n')
        f.par(whole=False)
        self.assertEqual('\n*(\na)\n', f.src)
        f.verify()

        f.par(whole=False)
        self.assertEqual('\n*(\na)\n', f.src)
        f.verify()

        f = FST('*a')
        f.par(True)
        self.assertEqual('*(a)', f.src)
        f.verify()

        # unparenthesizable

        self.assertEqual('a:b:c', FST('a:b:c').par().src)
        self.assertEqual('for i in j', FST('for i in j').par().src)
        self.assertEqual('a: int, b=2', FST('a: int, b=2').par().src)
        self.assertEqual('a: int', FST('a: int', arg).par().src)
        self.assertEqual('key="word"', FST('key="word"', keyword).par().src)
        self.assertEqual('a as b', FST('a as b', alias).par().src)
        self.assertEqual('a as b', FST('a as b', withitem).par().src)

        if not PYLT13:
            self.assertEqual('t: int = int', FST('t: int = int', type_param).par().src)
            self.assertEqual('*t = (int,)', FST('*t = (int,)', type_param).par().src)
            self.assertEqual('**t = {T: int}', FST('**t = {T: int}', type_param).par().src)

        elif not PYLT12:
            self.assertEqual('t: int', FST('t: int', type_param).par().src)
            self.assertEqual('*t', FST('*t', type_param).par().src)
            self.assertEqual('**t', FST('**t', type_param).par().src)

        # make sure parenthesized elements update parent locations

        self.assertEqual('if 1: *(a.b)', (f := FST('if 1: *a.b')).body[0].value.par().root.src)
        self.assertEqual((0, 0, 0, 12), f.loc)
        self.assertEqual((0, 6, 0, 12), f.body[0].loc)
        self.assertEqual((0, 6, 0, 12), f.body[0].value.loc)
        self.assertEqual((0, 8, 0, 11), f.body[0].value.value.loc)

        self.assertEqual('if 1: (a, b)', (f := FST('if 1: a, b')).body[0].value.par().root.src)
        self.assertEqual((0, 0, 0, 12), f.loc)
        self.assertEqual((0, 6, 0, 12), f.body[0].loc)
        self.assertEqual((0, 6, 0, 12), f.body[0].value.loc)

        self.assertEqual('if 1: ((a, b))', f.body[0].value.par(force=True).root.src)
        self.assertEqual((0, 0, 0, 14), f.loc)
        self.assertEqual((0, 6, 0, 14), f.body[0].loc)
        self.assertEqual((0, 7, 0, 13), f.body[0].value.loc)

        self.assertEqual('case [a, b]: pass', (f := FST('case a, b: pass')).pattern.par().root.src)
        self.assertEqual((0, 0, 0, 17), f.loc)
        self.assertEqual((0, 5, 0, 11), f.pattern.loc)
        self.assertEqual((0, 13, 0, 17), f.body[0].loc)

        self.assertEqual('case ([a, b]): pass', f.pattern.par(force=True).root.src)
        self.assertEqual((0, 0, 0, 19), f.loc)
        self.assertEqual((0, 6, 0, 12), f.pattern.loc)
        self.assertEqual((0, 15, 0, 19), f.body[0].loc)

        # location in Starred after forced parenthesize

        self.assertEqual('*((*a,))', (f := FST('*(*a,)')).par(force=True).root.src)
        f.verify()

        self.assertEqual('*((*ä,))', (f := FST('*(*ä,)')).par(force=True).root.src)
        f.verify()

        # very specific tricky case

        self.assertEqual('f(*(*a,))', (f := FST('f(*(*a,))')).put(FST('*(*a,)'), 0, 'args').root.src)
        f.verify()

        # lets force par some empty arguments at root

        self.assertEqual('()', FST('', 'arguments').par(force='invalid').src)

        # force='invalid'

        self.assertEqual('(expr)', FST('expr').par(force='invalid').src)
        self.assertEqual('(pat)', FST('pat', 'pattern').par(force='invalid').src)
        self.assertEqual('(a, b)', FST('a, b').par(force='invalid').src)
        self.assertEqual('[u, v]', FST('u, v', 'pattern').par(force='invalid').src)
        self.assertEqual('(arg)', FST('arg', 'arg').par(force='invalid').src)
        self.assertEqual('(stmt)', FST('stmt', 'stmt').par(force='invalid').src)
        self.assertEqual('(except: pass)', FST('except: pass').par(force='invalid').src)
        self.assertEqual('(>>)', FST('>>', 'operator').par(force='invalid').src)

        if PYGE12:
            self.assertEqual('(T)', FST('T', 'TypeVar').par(force='invalid').src)

        self.assertRaises(ValueError, FST('a').par, force='whatever')

    def test_unpar(self):
        f = parse('((1,))').body[0].value.f.copy(pars=True)
        self.assertEqual('((1,))', f.src)
        f.unpar()  # self.assertTrue()
        self.assertEqual('(1,)', f.src)
        f.unpar()  # self.assertFalse()
        self.assertEqual('(1,)', f.src)
        f.unpar(node=True)  # self.assertTrue()
        self.assertEqual('1,', f.src)
        f.unpar()  # self.assertFalse()

        # self.assertFalse(parse('()').body[0].value.f.copy().unpar())
        # self.assertFalse(parse('[]').body[0].value.f.copy().unpar())
        # self.assertFalse(parse('{}').body[0].value.f.copy().unpar())
        self.assertEqual('()', parse('()').body[0].value.f.copy().unpar().src)
        self.assertEqual('[]', parse('[]').body[0].value.f.copy().unpar().src)
        self.assertEqual('{}', parse('{}').body[0].value.f.copy().unpar().src)

        f = parse('( # pre1\n( # pre2\n1,\n # post1\n) # post2\n)').body[0].value.f.copy(pars=True)
        self.assertEqual('( # pre1\n( # pre2\n1,\n # post1\n) # post2\n)', f.src)
        f.unpar()  # self.assertTrue()
        self.assertEqual('( # pre2\n1,\n # post1\n)', f.src)
        f.unpar()  # self.assertFalse()
        self.assertEqual('( # pre2\n1,\n # post1\n)', f.src)
        f.unpar(node=True)  # self.assertTrue()
        self.assertEqual('1,', f.src)

        if PYGE14:  # make sure parent Interpolation.str gets modified
            f = FST('t"{(a)}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar()
            self.assertEqual('t"{a}"', f.src)
            self.assertEqual('a', f.values[0].str)

            f = FST('t"{((a,))}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar()
            self.assertEqual('t"{(a,)}"', f.src)
            self.assertEqual('(a,)', f.values[0].str)

            f = FST('t"{((a,))}"', 'exec').body[0].value.copy()
            f.values[0].value.unpar(node=True)
            self.assertEqual('t"{a,}"', f.src)
            self.assertEqual('a,', f.values[0].str)

        # f = FST('a:b:c', 'expr_slice')  # no way to do this currenly, would need unpar(force) which would need lots of code just for this stupid unnatural case
        # f.par(True)
        # self.assertEqual('(a:b:c)', f.src)
        # f.unpar()
        # self.assertEqual('a:b:c', f.src)

        # grouping

        f = parse('a').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(a)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((a))').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(\n ( (a) )  \n)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((i,))').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('(\n ( (i,) ) \n)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0].unpar(shared=False)
        self.assertEqual(f.src, 'call((i for i in j))')
        self.assertEqual((0, 0, 0, 20), f.loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0].unpar(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call( ( ( (i for i in j) ) ) )').f
        f.body[0].value.args[0].unpar(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0].unpar(shared=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))),)').f
        f.body[0].value.args[0].unpar(shared=False)
        self.assertEqual(f.src, 'call((i for i in j),)')
        self.assertEqual((0, 0, 0, 21), f.loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].loc)
        self.assertEqual((0, 0, 0, 21), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        self.assertEqual('call(i for i in j)', FST('call(((i for i in j)))').args[0].unpar().root.src)
        self.assertEqual('call(i for i in j)', FST('call((i for i in j))').args[0].unpar().root.src)
        self.assertEqual('call(i for i in j)', FST('call(i for i in j)').args[0].unpar().root.src)
        self.assertEqual('call((i for i in j), k)', FST('call(((i for i in j)), k)').args[0].unpar().root.src)
        self.assertEqual('call((i for i in j), k)', FST('call((i for i in j), k)').args[0].unpar().root.src)

        self.assertEqual('call((i for i in j))', FST('call(((i for i in j)))').args[0].unpar(shared=False).root.src)
        self.assertEqual('call((i for i in j))', FST('call((i for i in j))').args[0].unpar(shared=False).root.src)
        self.assertEqual('call(i for i in j)', FST('call(i for i in j)').args[0].unpar(shared=False).root.src)
        self.assertEqual('call((i for i in j), k)', FST('call(((i for i in j)), k)').args[0].unpar(shared=False).root.src)
        self.assertEqual('call((i for i in j), k)', FST('call((i for i in j), k)').args[0].unpar(shared=False).root.src)

        f = parse('( # pre\ni\n# post\n)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('( # pre\ni\n# post\n)').body[0].value.f.copy(pars=True)
        f.unpar(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        f = parse('( # pre\n(i,)\n# post\n)').f
        f.body[0].value.unpar(shared=False)
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)

        f = parse('( # pre\n(i)\n# post\n)').body[0].value.f.copy(pars=True)
        f.unpar(shared=False)
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a)if(a)]', 'exec')
        f.body[0].value.generators[0].ifs[0].unpar(shared=False)
        f.body[0].value.generators[0].ifs[1].unpar(shared=False)
        self.assertEqual('[a for a in b if a if a]', f.src)

        f = FST('for(a)in b: pass', 'exec')
        f.body[0].target.unpar(shared=False)
        self.assertEqual('for a in b: pass', f.src)

        f = FST('assert(test)', 'exec')
        f.body[0].test.unpar(shared=False)
        self.assertEqual('assert test', f.src)

        f = FST('assert({test})', 'exec')
        f.body[0].test.unpar(shared=False)
        self.assertEqual('assert{test}', f.src)

        # tuple

        f = parse('()').f
        f.body[0].value.unpar()
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)

        f = parse('(i,)').f
        f.body[0].value.unpar(node=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('(a, b)').f
        f.body[0].value.unpar(node=True)
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.body[0].value.elts[1].loc)

        f = parse('( # pre\ni,\n# post\n)').f
        f.body[0].value.unpar(node=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('( # pre\ni,\n# post\n)').body[0].value.f.copy()
        f.unpar(node=True)
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)

        # replace with space where directly touching other text

        f = FST('[a for a in b if(a,b)if(a,)if(a,b)]', 'exec')
        f.body[0].value.generators[0].ifs[0].unpar(node=True)
        f.body[0].value.generators[0].ifs[1].unpar(node=True)
        f.body[0].value.generators[0].ifs[2].unpar(node=True)
        self.assertEqual('[a for a in b if a,b if a,if a,b]', f.src)
        f.body[0].value.generators[0].ifs[0].par()  # so that it will verify
        f.body[0].value.generators[0].ifs[1].par()
        f.body[0].value.generators[0].ifs[2].par()
        self.assertEqual('[a for a in b if (a,b) if (a,)if (a,b)]', f.src)
        f.verify()

        f = FST('for(a,b)in b: pass', 'exec')
        f.body[0].target.unpar(node=True)
        self.assertEqual('for a,b in b: pass', f.src)
        f.verify()

        f = FST('for(a,)in b: pass', 'exec')
        f.body[0].target.unpar(node=True)
        self.assertEqual('for a,in b: pass', f.src)
        f.verify()

        # special rules for Starred

        f = FST('*(\na)')
        self.assertEqual('*(\na)', f.src)
        f.unpar()
        self.assertEqual('*a', f.src)
        f.verify()

        f = FST('*(\na\n)')
        self.assertEqual('*(\na\n)', f.src)
        f.unpar()
        self.assertEqual('*a', f.src)
        f.verify()

        f = FST('*\na')
        f._parenthesize_grouping(star_child=False)
        self.assertEqual('(*\na)', f.src)
        f.unpar()
        self.assertEqual('(*\na)', f.src)

        # unowned pars

        f = FST('a:b:c')
        f.par(force='invalid')
        self.assertEqual('(a:b:c)', f.src)
        f.unpar(shared=None)
        self.assertEqual('a:b:c', f.src)

        f = FST('f(a)')
        f.args[0].unpar(shared=None)
        self.assertEqual('f a', f.src)

        f = FST('class c(a): pass')
        f.bases[0].unpar(shared=None)
        self.assertEqual('class c a: pass', f.src)

        f = FST('case c(a): pass')
        f.pattern.patterns[0].unpar(shared=None)
        self.assertEqual('case c a: pass', f.src)

        f = FST('from a import (b)')
        f.names[0].unpar(shared=None)
        self.assertEqual('from a import b', f.src)

        # invalid node param

        f = FST('a')
        self.assertRaises(ValueError, f.unpar, 0)
        self.assertRaises(ValueError, f.unpar, 1)
        self.assertRaises(ValueError, f.unpar, None)
        self.assertRaises(ValueError, f.unpar, '')
        self.assertRaises(ValueError, f.unpar, 'valid')

        # 'invalid' non-Tuple non-MatchSequence delimited nodes

        self.assertEqual('  1,  ', FST('  [ 1, ]  ').unpar('invalid').src)
        self.assertEqual('  1,  ', FST('  { 1, }  ').unpar('invalid').src)
        self.assertEqual('  1: a,  ', FST('  { 1: a, }  ').unpar('invalid').src)
        self.assertEqual('  **a,  ', FST('  { **a, }  ').unpar('invalid').src)
        self.assertEqual('  1: a, **b,  ', FST('  { 1: a, **b, }  ').unpar('invalid').src)
        self.assertEqual('  1: a,  ', FST('  { 1: a, }  ', pattern).unpar('invalid').src)
        self.assertEqual('  **a,  ', FST('  { **a, }  ', pattern).unpar('invalid').src)
        self.assertEqual('  1: a,  ', FST('  { 1: a, }  ', pattern).unpar('invalid').src)
        self.assertEqual('  1: a, **b,  ', FST('  { 1: a, **b, }  ', pattern).unpar('invalid').src)
        self.assertEqual('  i for i in j  ', FST('  [ i for i in j ]  ').unpar('invalid').src)
        self.assertEqual('  i for i in j if i  ', FST('  [ i for i in j if i ]  ').unpar('invalid').src)

        f = FST('  [ i for i in j ]  ')
        del f.generators[0]
        self.assertEqual('  i  ', f.unpar('invalid').src)

        self.assertEqual('  i for i in j  ', FST('  { i for i in j }  ').unpar('invalid').src)
        self.assertEqual('  i for i in j  ', FST('  ( i for i in j )  ').unpar('invalid').src)
        self.assertEqual('  i: i for i in j  ', FST('  { i: i for i in j }  ').unpar('invalid').src)

        # for test coverage

        f = FST('(i)')
        f._unparenthesize_grouping = lambda *a, **kw: 1/0
        self.assertRaises(ZeroDivisionError, f.unpar)

    def test_pars(self):
        for src, elt, slice_copy in PARS_DATA:
            src  = src.strip()
            t    = parse(src)
            f    = eval(f't.{elt}', {'t': t}).f
            l    = f.pars()
            ssrc = f._get_src(*l)

            try:
                self.assertEqual(ssrc, slice_copy.strip())

            except Exception:
                print(elt)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_pars_special(self):
        f = parse('''
( (
 (
   a
  ) )
)
        '''.strip()).body[0].value.f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 0, 4, 1))

        f = parse('''
( (
 (
   a
  ) )
,)
        '''.strip()).body[0].value.elts[0].f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 2, 3, 5))

        f = parse('''
(

   a

,)
        '''.strip()).body[0].value.elts[0].f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (2, 3, 2, 4))

        self.assertEqual((0, 1, 0, 15), parse('f(i for i in j)').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 16), parse('f((i for i in j))').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 18), parse('f(((i for i in j)))').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 14), parse('f(i for i in j)').body[0].value.args[0].f.pars(shared=False))
        self.assertEqual((0, 2, 0, 16), parse('f((i for i in j))').body[0].value.args[0].f.pars(shared=False))
        self.assertEqual((0, 2, 0, 18), parse('f(((i for i in j)))').body[0].value.args[0].f.pars(shared=False))

        f = parse('((1), ( (2) ))').body[0].value.f
        self.assertEqual(1, f.elts[0].pars().n)
        self.assertEqual(2, f.elts[1].pars().n)
        self.assertEqual(0, f.pars().n)

        self.assertEqual(1, parse('call(((i for i in j)))').body[0].value.args[0].f.pars().n)
        self.assertEqual(0, parse('call((i for i in j))').body[0].value.args[0].f.pars().n)
        self.assertEqual(0, parse('call(i for i in j)').body[0].value.args[0].f.pars().n)
        self.assertEqual(-1, parse('call(i for i in j)').body[0].value.args[0].f.pars(shared=False).n)

        self.assertEqual((0, 8, 0, 9), parse('class c(b): pass').body[0].bases[0].f.pars())
        self.assertEqual((0, 8, 0, 9), parse('class c(b,): pass').body[0].bases[0].f.pars())
        self.assertEqual((0, 8, 0, 11), parse('class c((b)): pass').body[0].bases[0].f.pars())
        self.assertEqual((0, 8, 0, 11), parse('class c((b),): pass').body[0].bases[0].f.pars())

        self.assertEqual((0, 5, 0, 8), parse('with (a): pass').body[0].items[0].context_expr.f.pars())
        self.assertEqual((0, 5, 0, 8), parse('with (a): pass').body[0].items[0].f.pars())
        self.assertEqual((0, 5, 0, 10), parse('with ((a)): pass').body[0].items[0].context_expr.f.pars())
        self.assertEqual((0, 5, 0, 10), parse('with ((a)): pass').body[0].items[0].f.pars())
        self.assertEqual((0, 6, 0, 7), parse('with (a as b): pass').body[0].items[0].context_expr.f.pars())
        self.assertEqual((0, 6, 0, 12), parse('with (a as b): pass').body[0].items[0].f.pars())
        self.assertEqual((0, 6, 0, 9), parse('with ((a) as b): pass').body[0].items[0].context_expr.f.pars())
        self.assertEqual((0, 6, 0, 14), parse('with ((a) as b): pass').body[0].items[0].f.pars())
        self.assertRaises(SyntaxError, parse, 'with ((a as b)): pass')

        self.assertEqual((0, 15, 0, 16), parse('from a import (b)').body[0].names[0].f.pars())
        self.assertRaises(SyntaxError, parse, 'from a import ((b))')
        self.assertEqual((0, 15, 0, 21), parse('from a import (b as c)').body[0].names[0].f.pars())
        self.assertRaises(SyntaxError, parse, 'from a import ((b as c))')

        # tricky cases, large pars delta

        self.assertEqual('for i in (j)', FST('((i for i in (j)))', 'exec').body[0].value.generators[0].src)
        self.assertEqual((0, 2, 0, 5), FST('(((a), b))', 'exec').body[0].value.elts[0].pars())
        self.assertEqual((0, 5, 0, 8), FST('call((i),)', 'exec').body[0].value.args[0].pars())
        self.assertEqual((0, 5, 0, 10), FST('call(((i)),)', 'exec').body[0].value.args[0].pars())
        self.assertEqual((0, 8, 0, 13), FST('class c(((b))): pass', 'exec').body[0].bases[0].pars())
        self.assertEqual((0, 8, 0, 13), FST('class c(((b)),): pass', 'exec').body[0].bases[0].pars())
        self.assertEqual((0, 22, 0, 25), FST('call(i for i in range(256))', 'exec').body[0].value.args[0].generators[0].iter.args[0].pars())

        f = parse('bytes((x ^ 0x5C) for x in range(256))').body[0].value.f
        f.args[0].generators[0].iter.put('256', 0, field='args', raw=False)
        self.assertEqual('bytes((x ^ 0x5C) for x in range(256))', f.root.src)

        # unowned pars

        f = FST('a:b:c')
        f.par(force='invalid')
        self.assertEqual((0, 1, 0, 6), f.pars())
        self.assertEqual((0, 0, 0, 7), f.pars(shared=None))

        f = FST('f(a)')
        self.assertEqual((0, 2, 0, 3), f.args[0].pars())
        self.assertEqual((0, 1, 0, 4), f.args[0].pars(shared=None))

        f = FST('class c(a): pass')
        self.assertEqual((0, 8, 0, 9), f.bases[0].pars())
        self.assertEqual((0, 7, 0, 10), f.bases[0].pars(shared=None))

        f = FST('case f(a): pass')
        self.assertEqual((0, 7, 0, 8), f.pattern.patterns[0].pars())
        self.assertEqual((0, 6, 0, 9), f.pattern.patterns[0].pars(shared=None))

        f = FST('from a import (b)')
        self.assertEqual((0, 15, 0, 16), f.names[0].pars())
        self.assertEqual((0, 14, 0, 17), f.names[0].pars(shared=None))

        # walruses

        self.assertEqual('b := c', FST('a, b := c, d').elts[1].copy(pars_walrus=False).src)
        self.assertEqual('b := c', FST('a = (b := c)').value.copy(pars_walrus=False).src)

        self.assertEqual('(b := c)', FST('a, b := c, d').elts[1].copy(pars_walrus=True).src)
        self.assertEqual('(b := c)', FST('a = (b := c)').value.copy(pars_walrus=True).src)

        # more cases

        self.assertEqual('fstlocn(0, 0, 0, 9, n=0)', str(FST('(a,), (b)').pars()))
        self.assertEqual('fstlocn(0, 0, 0, 9, n=0)', str(FST('(a), (b,)').pars()))

    def test_pars_walrus(self):
        # not already parenthesized

        self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=True).src)
        self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=False).src)
        self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=None).src)

        self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=True).src)
        self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=False).src)
        self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=None).src)

        self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=True).src)
        self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=False).src)
        self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=None).src)

        with FST.options(pars_walrus=False):
            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=False).src)
            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=None).src)

            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=False).src)
            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=None).src)

            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=False).src)
            self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=None).src)

        with FST.options(pars_walrus=None):
            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=False).src)
            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=True, pars_walrus=None).src)

            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=False).src)
            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars='auto', pars_walrus=None).src)

            self.assertEqual('(i := j)', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=False).src)
            self.assertEqual('i := j', FST('k, i := j').get(1, 'elts', pars=False, pars_walrus=None).src)

        # already parenthesized

        self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=True).src)
        self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=False).src)
        self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=None).src)

        self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=True).src)
        self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=False).src)
        self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=None).src)

        self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=True).src)
        self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=False).src)
        self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=None).src)

        with FST.options(pars_walrus=False):
            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=True).src)
            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=False).src)
            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=None).src)

            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=False).src)
            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=None).src)

            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=False).src)
            self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=None).src)

        with FST.options(pars_walrus=None):
            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=True).src)
            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=False).src)
            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=True, pars_walrus=None).src)

            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=False).src)
            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars='auto', pars_walrus=None).src)

            self.assertEqual('(i := j)', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=True).src)
            self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=False).src)
            self.assertEqual('i := j', FST('k, (i := j)').get(1, 'elts', pars=False, pars_walrus=None).src)

        # need pars for parsability

        f = FST('(a, i\n:=\n1\n)')
        self.assertEqual('(i\n:=\n1)', f.elts[1].copy(pars=True, pars_walrus=True).src)
        self.assertEqual('(i\n:=\n1)', f.elts[1].copy(pars=True, pars_walrus=None).src)
        self.assertEqual('(i\n:=\n1)', f.elts[1].copy(pars=True, pars_walrus=False).src)
        self.assertEqual('(i\n:=\n1)', f.elts[1].copy(pars='auto', pars_walrus=True).src)
        self.assertEqual('(i\n:=\n1)', f.elts[1].copy(pars='auto', pars_walrus=None).src)
        self.assertEqual('(i\n:=\n1)', f.elts[1].copy(pars='auto', pars_walrus=False).src)
        self.assertEqual('(i\n:=\n1)', f.elts[1].copy(pars=False, pars_walrus=True).src)
        self.assertEqual('i\n:=\n1', f.elts[1].copy(pars=False, pars_walrus=None).src)
        self.assertEqual('i\n:=\n1', f.elts[1].copy(pars=False, pars_walrus=False).src)

    def test_pars_arglike(self):
        # not already parenthesized

        self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=True).src)
        self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=False).src)
        self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=None).src)
        self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=True).src)

        self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=True).src)
        self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=False).src)
        self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=None).src)
        self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars='auto').src)

        self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=True).src)
        self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=False).src)
        self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=None).src)
        self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=False).src)

        with FST.options(pars_arglike=False):
            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=True).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=None).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=True).src)

            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=True).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=None).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars='auto').src)

            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=True).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=False).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=None).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=False).src)

        with FST.options(pars_arglike=None):
            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=True).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=True, pars_arglike=None).src)
            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=True).src)

            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=True).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars='auto', pars_arglike=None).src)
            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars='auto').src)

            self.assertEqual('*(not a)', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=True).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=False).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=False, pars_arglike=None).src)
            self.assertEqual('*not a', FST('call(*not a)').get(0, 'args', pars=False).src)

        # already parenthesized

        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=True).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=False).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=None).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True).src)

        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=True).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=False).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=None).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto').src)

        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=True).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=False).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=None).src)
        self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False).src)

        with FST.options(pars_arglike=False):
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=True).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=None).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True).src)

            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=True).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=None).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto').src)

            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=True).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=None).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False).src)

        with FST.options(pars_arglike=None):
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=True).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True, pars_arglike=None).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=True).src)

            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=True).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto', pars_arglike=None).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars='auto').src)

            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=True).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=False).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False, pars_arglike=None).src)
            self.assertEqual('*(not a)', FST('call(*(not a))').get(0, 'args', pars=False).src)

        f = FST('call(1, *\nnot\nb)')
        self.assertEqual('*(\nnot\nb)', f.args[1].copy(pars=True, pars_walrus=True).src)
        self.assertEqual('*(\nnot\nb)', f.args[1].copy(pars=True, pars_walrus=None).src)
        self.assertEqual('*(\nnot\nb)', f.args[1].copy(pars=True, pars_walrus=False).src)
        self.assertEqual('*(\nnot\nb)', f.args[1].copy(pars='auto', pars_walrus=True).src)
        self.assertEqual('*(\nnot\nb)', f.args[1].copy(pars='auto', pars_walrus=None).src)
        self.assertEqual('*(\nnot\nb)', f.args[1].copy(pars='auto', pars_walrus=False).src)
        self.assertEqual('*(\nnot\nb)', f.args[1].copy(pars=False, pars_arglike=True).src)
        self.assertEqual('*\nnot\nb', f.args[1].copy(pars=False, pars_arglike=None).src)
        self.assertEqual('*\nnot\nb', f.args[1].copy(pars=False, pars_arglike=False).src)

        f = FST('call(1, *\nb)')
        self.assertEqual('*(\nb)', f.args[1].copy(pars=True, pars_walrus=True).src)
        self.assertEqual('*(\nb)', f.args[1].copy(pars=True, pars_walrus=None).src)
        self.assertEqual('*(\nb)', f.args[1].copy(pars=True, pars_walrus=False).src)
        self.assertEqual('*(\nb)', f.args[1].copy(pars='auto', pars_walrus=True).src)
        self.assertEqual('*(\nb)', f.args[1].copy(pars='auto', pars_walrus=None).src)
        self.assertEqual('*(\nb)', f.args[1].copy(pars='auto', pars_walrus=False).src)
        self.assertEqual('*\nb', f.args[1].copy(pars=False, pars_arglike=True).src)
        self.assertEqual('*\nb', f.args[1].copy(pars=False, pars_arglike=None).src)
        self.assertEqual('*\nb', f.args[1].copy(pars=False, pars_arglike=False).src)

    def test_pars_n(self):
        self.assertEqual(1, FST('(a)', 'exec').body[0].value.pars().n)
        self.assertEqual(0, FST('(a, b)', 'exec').body[0].value.elts[0].pars().n)
        self.assertEqual(0, FST('(a, b)', 'exec').body[0].value.elts[1].pars().n)
        self.assertEqual(1, FST('((a), b)', 'exec').body[0].value.elts[0].pars().n)
        self.assertEqual(1, FST('(a, (b))', 'exec').body[0].value.elts[1].pars().n)

        self.assertEqual(0, FST('(a, b)', 'exec').body[0].value.pars().n)
        self.assertEqual(1, FST('((a, b))', 'exec').body[0].value.pars().n)

        self.assertEqual(0, FST('f(i for i in j)', 'exec').body[0].value.args[0].pars().n)
        self.assertEqual(-1, FST('f(i for i in j)', 'exec').body[0].value.args[0].pars(shared=False).n)
        self.assertTrue((f := FST('f(i for i in j)', 'exec').body[0].value.args[0]).pars(shared=False) > f.bloc)
        self.assertEqual(0, FST('f((i for i in j))', 'exec').body[0].value.args[0].pars(shared=False).n)
        self.assertTrue((f := FST('f((i for i in j))', 'exec').body[0].value.args[0]).pars(shared=False) == f.bloc)
        self.assertEqual(1, FST('f(((i for i in j)))', 'exec').body[0].value.args[0].pars(shared=False).n)
        self.assertTrue((f := FST('f(((i for i in j)))', 'exec').body[0].value.args[0]).pars(shared=False) < f.bloc)

    def test_copy_pars(self):
        self.assertEqual('a', parse('(a)').body[0].value.f.copy(pars=False).root.src)
        self.assertEqual('a', parse('(a)').body[0].value.f.copy(pars='auto').root.src)
        self.assertEqual('(a)', parse('(a)').body[0].value.f.copy(pars=True).root.src)
        self.assertEqual('a', parse('( # pre\na\n # post\n)').body[0].value.f.copy(pars=False).root.src)
        self.assertEqual('( # pre\na\n # post\n)', parse('( # pre\na\n # post\n)').body[0].value.f.copy(pars=True).root.src)

        self.assertEqual('b as c', parse('from a import (b as c)').body[0].names[0].f.copy(pars=False).root.src)
        self.assertEqual('b as c', parse('from a import (b as c)').body[0].names[0].f.copy(pars='auto').root.src)
        self.assertEqual('b as c', parse('from a import (b as c)').body[0].names[0].f.copy(pars=True).root.src)  # cannot be individually parenthesized
        self.assertEqual('b as c', parse('from a import (b as c, d as e)').body[0].names[0].f.copy(pars=False).root.src)
        self.assertEqual('b as c', parse('from a import ( # pre\nb as c\n# post\n)').body[0].names[0].f.copy(pars=False).root.src)
        self.assertEqual('b as c', parse('from a import ( # pre\nb as c\n# post\n)').body[0].names[0].f.copy(pars=True).root.src)  # cannot be individually parenthesized

        self.assertEqual('a as b', parse('with (a as b): pass').body[0].items[0].f.copy(pars=False).root.src)
        self.assertEqual('a as b', parse('with (a as b): pass').body[0].items[0].f.copy(pars='auto').root.src)
        self.assertEqual('a as b', parse('with (a as b): pass').body[0].items[0].f.copy(pars=True).root.src)  # cannot be individually parenthesized
        self.assertEqual('a as b', parse('with (a as b, c as d): pass').body[0].items[0].f.copy(pars=True).root.src)
        self.assertEqual('a as b', parse('with ( # pre\na as b\n# post\n): pass').body[0].items[0].f.copy(pars=False).root.src)
        self.assertEqual('a as b', parse('with ( # pre\na as b\n# post\n): pass').body[0].items[0].f.copy(pars=True).root.src)  # cannot be individually parenthesized

        self.assertEqual('1|2', parse('match a:\n case (1|2): pass').body[0].cases[0].pattern.f.copy(pars=False).root.src)
        self.assertEqual('1|2', parse('match a:\n case (1|2): pass').body[0].cases[0].pattern.f.copy(pars='auto').root.src)
        self.assertEqual('(1|2)', parse('match a:\n case (1|2): pass').body[0].cases[0].pattern.f.copy(pars=True).root.src)
        self.assertEqual('1|2', parse('match a:\n case ( # pre\n1|2\n# post\n): pass').body[0].cases[0].pattern.f.copy(pars=False).root.src)
        self.assertEqual('( # pre\n1|2\n# post\n)', parse('match a:\n case ( # pre\n1|2\n# post\n): pass').body[0].cases[0].pattern.f.copy(pars=True).root.src)

    def test_copy_unwhole_at_root(self):
        self.assertEqual('i', FST('# 0\ni\n # 1').copy(whole=False).src)
        self.assertEqual('# 0\ni\n # 1', FST('# 0\ni\n # 1', 'exec').copy(whole=False).src)

        self.assertEqual('i,', FST('# 0\ni,\n # 1').copy(whole=False).src)

        self.assertEqual('# 0\n# 1\n# 2', FST('# 0\n# 1\n# 2', 'arguments').copy(whole=False).src)  # no loc
        self.assertEqual('# 0\n# 1\n# 2', FST('# 0\n# 1\n# 2', 'Load').copy(whole=False).src)
        self.assertEqual('# 0\n# 1\n# 2', FST('# 0\n# 1\n# 2', 'Store').copy(whole=False).src)
        self.assertEqual('# 0\n# 1\n# 2', FST('# 0\n# 1\n# 2', 'Del').copy(whole=False).src)

        self.assertEqual('and', FST('# 0\nand\n# 2', 'And').copy(whole=False).src)  # have loc
        self.assertEqual('or', FST('# 0\nor\n# 2', 'Or').copy(whole=False).src)

        # statementlike

        self.assertEqual('i', FST('# 0\ni\n # 1', 'Expr').copy(whole=False, trivia=(False, False)).src)
        self.assertEqual('# 0\ni', FST('# 0\ni\n # 1', 'Expr').copy(whole=False).src)
        self.assertEqual('# 0\ni\n # 1', FST('# 0\ni\n # 1', 'Expr').copy(whole=False, trivia=('all', 'all')).src)

        f = FST('# pre\nexcept a: pass\n# post', 'ExceptHandler')
        self.assertEqual('except a: pass', f.copy(whole=False, trivia=(False, False)).src)
        self.assertEqual('# pre\nexcept a: pass', f.copy(whole=False).src)
        self.assertEqual('# pre\nexcept a: pass\n# post', f.copy(whole=False, trivia=('all', 'all')).src)

        f = FST('# pre\ncase _: pass\n# post', 'match_case')
        self.assertEqual('case _: pass', f.copy(whole=False, trivia=(False, False)).src)
        self.assertEqual('# pre\ncase _: pass', f.copy(whole=False).src)
        self.assertEqual('# pre\ncase _: pass\n# post', f.copy(whole=False, trivia=('all', 'all')).src)

        # parentheses

        f = FST('(expr)')
        self.assertEqual('expr', f.copy(False).src)
        self.assertEqual('(expr)', f.copy(False, pars=True).src)

        f = FST('a := b')
        self.assertEqual('a := b', f.copy(False, pars_walrus=False).src)
        self.assertEqual('(a := b)', f.copy(False, pars_walrus=True).src)

        f = FST('(a := b)')
        self.assertEqual('a := b', f.copy(False, pars_walrus=False).src)
        self.assertEqual('(a := b)', f.copy(False, pars_walrus=True).src)

        f = FST('*a or b')
        self.assertEqual('*a or b', f.copy(False, pars_arglike=False).src)
        self.assertEqual('*(a or b)', f.copy(False, pars_arglike=True).src)

        f = FST('*(a or b)')
        self.assertEqual('*(a or b)', f.copy(False, pars_arglike=False).src)
        self.assertEqual('*(a or b)', f.copy(False, pars_arglike=True).src)

        f = FST('a\n+\nb')
        self.assertEqual('(a\n+\nb)', f.copy(False).src)
        self.assertEqual('a\n+\nb', f.copy(False, pars=False).src)

        # all

        try:
            for src, mode in INDIVIDUAL_NODES:
                if mode in ('alias', '_Assign_targets'):  # can't add comments to these
                    continue

                commented_src = f'# pre\n{src}  # line\n# post'

                f = FST(commented_src, mode)
                copy_src = f.copy(whole=False, pars_walrus=False).src

                if f.is_stmtlike:
                    self.assertEqual(copy_src, f'# pre\n{src}  # line')
                elif f.is_mod or f.is_expr_context or f.is__slice or f.is_arguments:
                    self.assertEqual(copy_src, commented_src)
                else:
                    self.assertEqual(copy_src, src)

                if f.is_parenthesizable(star=False):
                    pard_src = f'({src})'

                    f.par(force=True, whole=False)
                    self.assertEqual(f.copy(whole=False, pars=False).src, src)
                    self.assertEqual(f.copy(whole=False, pars=True).src, pard_src)

        except Exception:
            print(f'\n{mode=}, {src=}')

            raise

        # recover from error

        self.assertRaises(KeyError, (f := FST('a = b')).copy, False, trivia='bad')
        self.assertEqual('a = b', f.src)
        f.verify()

    def test_copy_special(self):
        f = FST.fromsrc('@decorator\nclass cls:\n  pass')
        self.assertEqual(f.a.body[0].f.copy().src, '@decorator\nclass cls:\n  pass')
        # self.assertEqual(f.a.body[0].f.copy(decos=False).src, 'class cls:\n  pass')

        l = FST.fromsrc("['\\u007f', '\\u0080', 'ʁ', 'ᛇ', '時', '🐍', '\\ud800', 'Źdźbło']").a.body[0].value.elts
        self.assertEqual("'\\u007f'", l[0].f.copy().src)
        self.assertEqual("'\\u0080'", l[1].f.copy().src)
        self.assertEqual("'ʁ'", l[2].f.copy().src)
        self.assertEqual("'ᛇ'", l[3].f.copy().src)
        self.assertEqual("'時'", l[4].f.copy().src)
        self.assertEqual("'🐍'", l[5].f.copy().src)
        self.assertEqual("'\\ud800'", l[6].f.copy().src)
        self.assertEqual("'Źdźbło'", l[7].f.copy().src)

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy()
        self.assertEqual('(w := x,)', f.src)

        f = FST.fromsrc('''
if 1:
    def f():
        """
        strict docstring
        """
        """
        loose docstring
        """
            '''.strip())
        self.assertEqual('''
def f():
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    async def f():
        """
        strict docstring
        """
        """
        loose docstring
        """
            '''.strip())
        self.assertEqual('''
async def f():
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())
        self.assertEqual('''
class cls:
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())

        self.assertEqual('''
class cls:
    """
        strict docstring
        """
    """
        loose docstring
        """
            '''.strip(), f.a.body[0].body[0].f.copy(docstr=False).src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())

        self.assertEqual('''
class cls:
    """
    strict docstring
    """
    """
        loose docstring
        """
            '''.strip(), f.a.body[0].body[0].f.copy(docstr='strict').src)


        f = FST.fromsrc('''
# start

"""docstring"""

i = 1

# end
            '''.strip())
        self.assertEqual((g := f.copy())._get_src(*g.loc), f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            ''')
        self.assertEqual('i', a.body[0].f.copy(trivia=(False, False)).src)
        self.assertEqual('# pre\ni', a.body[0].f.copy(trivia=(True, False)).src)
        self.assertEqual('# pre\ni # post', a.body[0].f.copy(trivia=(True, True)).src)
        self.assertEqual('# prepre\n\n# pre\ni', a.body[0].f.copy(trivia=('all', False)).src)

        a = parse('( i )')
        self.assertEqual('i', a.body[0].value.f.copy(trivia=(False, False)).src)
        self.assertEqual('( i )', a.body[0].value.f.copy(trivia=(False, False), pars=True).src)

        if PYGE12:
            f = FST.fromsrc('a[*b]').a.body[0].value.slice.f.copy()
            self.assertEqual('*b,', f.src)

            f = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy()
            self.assertEqual('*tuple[int, ...],', f.src)

        # misc

        self.assertEqual('opts.ignore_module', FST('''
opts.ignore_module = [mod.strip()
                      for i in opts.ignore_module for mod in i.split(',')]
            '''.strip(), 'exec').body[0].value.generators[0].iter.copy().src)

    def test_fst___item__accessors(self):
        f = parse('a\nb\nc').f
        f[1:2] = 'd\ne'
        self.assertEqual('a\nd\ne\nc', f.src)

        f = parse('a\nb\nc').f
        f[1] = 'd'
        self.assertEqual('a\nd\nc', f.src)

        f = parse('a\nb\nc\nd\ne').f
        f[1:4] = 'f'
        self.assertEqual('a\nf\ne', f.src)

        f = parse('a\nb\nc\nd\ne').f
        f[1:4] = 'f\ng'
        self.assertEqual('a\nf\ng\ne', f.src)

        f = parse('a\nb\nc\nd\ne').f
        del f[1:3]
        self.assertEqual('a\nd\ne', f.src)
        del f[1]
        self.assertEqual('a\ne', f.src)
        f[1:1] = 'b\nc\nd'
        self.assertEqual('a\nb\nc\nd\ne', f.src)

        f = parse('a\nb\nc').f
        def test():
            f[1] = 'd\ne'
        self.assertRaises(ValueError, test)

    def test_fst_insert_append_extend_prepend_prextend(self):
        f = parse('a\nb\nc').f
        g = f[1:2]
        g.append('d')
        self.assertEqual(2, len(g))
        self.assertEqual('b', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('a\nb\nd\nc', f.src)

        f = parse('a\nb\nc').f
        g = f[1:2]
        g.extend('d\ne')
        self.assertEqual(3, len(g))
        self.assertEqual('b', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('a\nb\nd\ne\nc', f.src)

        f = parse('a\nb\nc').f
        g = f[1:2]
        g.prepend('d')
        self.assertEqual(2, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('b', g[1].src)
        self.assertEqual('a\nd\nb\nc', f.src)

        f = parse('a\nb\nc').f
        g = f[1:2]
        g.prextend('d\ne')
        self.assertEqual(3, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('e', g[1].src)
        self.assertEqual('b', g[2].src)
        self.assertEqual('a\nd\ne\nb\nc', f.src)

        f = parse('', 'exec').f
        g = f
        g.append('d')
        self.assertEqual(1, len(g.body))
        self.assertEqual('d', g[0].src)
        self.assertEqual('d', f.src)
        g.prepend('e')
        self.assertEqual(2, len(g.body))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('e\nd', f.src)
        g.extend('f\ng')
        self.assertEqual(4, len(g.body))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('f', g[2].src)
        self.assertEqual('g', g[3].src)
        self.assertEqual('e\nd\nf\ng', f.src)
        g.prextend('h\ni')
        self.assertEqual(6, len(g.body))
        self.assertEqual('h', g[0].src)
        self.assertEqual('i', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('d', g[3].src)
        self.assertEqual('f', g[4].src)
        self.assertEqual('g', g[5].src)
        self.assertEqual('h\ni\ne\nd\nf\ng', f.src)
        g.body.replace('h')
        self.assertEqual(1, len(g.body))
        self.assertEqual('h', g[0].src)
        self.assertEqual('h', f.src)
        g.insert('i')
        self.assertEqual(2, len(g.body))
        self.assertEqual('i', g[0].src)
        self.assertEqual('h', g[1].src)
        self.assertEqual('i\nh', f.src)
        g.insert('j', 1)
        self.assertEqual(3, len(g.body))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('h', g[2].src)
        self.assertEqual('i\nj\nh', f.src)
        g.insert('k', -1)
        self.assertEqual(4, len(g.body))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('i\nj\nk\nh', f.src)
        g.insert('l', 'end')
        self.assertEqual(5, len(g.body))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('l', g[4].src)
        self.assertEqual('i\nj\nk\nh\nl', f.src)

    def test_find_def(self):
        def test(fst_, path, recurse=True, asts=None):
            ret = []
            prev_found = None

            while prev_found := fst_.find_def(path, prev_found, recurse=recurse, asts=asts):
                ret.append(prev_found)

            return ret

        f = FST('''
class pre: pass
def f(): pass
class g: pass
if something:
    pass
    def g():
        class inner: pass
def h(): pass
def g(): pass
'''.strip())

        self.assertEqual([f.body[2], f.body[3].body[1], f.body[5]], test(f, 'g', True))
        self.assertEqual([f.body[2], f.body[5]], test(f, 'g', False))

        self.assertEqual([f.body[3].body[1].body[0]], test(f, 'def g.class inner', True))
        self.assertEqual([f.body[3].body[1].body[0]], test(f, 'def g.class inner', False))

        # on a non-scope block statement node

        self.assertEqual([f.body[3].body[1].body[0]], test(f.body[3], 'g.inner', True))
        self.assertEqual([f.body[3].body[1].body[0]], test(f.body[3], 'g.inner', False))

        self.assertEqual([f.body[3].body[1]], test(f.body[3], 'g', True))
        self.assertEqual([f.body[3].body[1]], test(f.body[3], 'g', False))

        # explicit list of asts

        f = FST('''
if 1:
    def f(): pass
    def g(): pass
    class f: pass
else:
    class f(h): pass
    def h(): pass
    def f(i): pass
'''.strip())

        self.assertEqual([f.body[0], f.body[2], f.orelse[0], f.orelse[2]], test(f, 'f'))
        self.assertEqual([f.body[0], f.body[2]], test(f, 'f', asts=f.a.body))
        self.assertEqual([f.orelse[0], f.orelse[2]], test(f, 'f', asts=f.a.orelse))

        self.assertEqual([f.body[0], f.orelse[2]], test(f, 'f', asts=[f.a.body[0], f.a.body[1], f.a.orelse[1], f.a.orelse[2]]))
        self.assertEqual([f.body[2], f.orelse[0]], test(f, 'f', asts=[f.a.body[2], f.a.body[1], f.a.orelse[1], f.a.orelse[0]]))

    def test_find_loc_in(self):
        f    = parse('abc += xyz').f
        fass = f.body[0]
        fabc = fass.target
        fpeq = fass.op
        fxyz = fass.value

        self.assertIs(fass, f.find_contains_loc(0, 0, 0, 10))
        self.assertIs(None, f.find_contains_loc(0, 0, 0, 10, False))
        self.assertIs(f, f.find_contains_loc(0, 0, 0, 10, 'top'))
        self.assertIs(fabc, f.find_contains_loc(0, 0, 0, 3))
        self.assertIs(fass, f.find_contains_loc(0, 0, 0, 3, False))
        self.assertIs(fabc, f.find_contains_loc(0, 0, 0, 3, 'top'))
        self.assertIs(fass, f.find_contains_loc(0, 0, 0, 4))
        self.assertIs(fass, f.find_contains_loc(0, 0, 0, 4, False))
        self.assertIs(fass, f.find_contains_loc(0, 0, 0, 4, 'top'))
        self.assertIs(fass, f.find_contains_loc(0, 3, 0, 4, False))
        self.assertIs(fass, f.find_contains_loc(0, 3, 0, 4, 'top'))
        self.assertIs(fpeq, f.find_contains_loc(0, 4, 0, 5))
        self.assertIs(fass, f.find_contains_loc(0, 4, 0, 6, False))
        self.assertIs(fpeq, f.find_contains_loc(0, 4, 0, 5, 'top'))
        self.assertIs(fxyz, f.find_contains_loc(0, 7, 0, 10))
        self.assertIs(fass, f.find_contains_loc(0, 7, 0, 10, False))
        self.assertIs(fxyz, f.find_contains_loc(0, 7, 0, 10, 'top'))
        self.assertIs(fass, f.find_contains_loc(0, 6, 0, 10))
        self.assertIs(fass, f.find_contains_loc(0, 7, 0, 10, False))
        self.assertIs(fass, f.find_contains_loc(0, 6, 0, 10, 'top'))

        f  = parse('a+b').f
        fx = f.body[0]
        fo = fx.value
        fa = fo.left
        fp = fo.op
        fb = fo.right

        self.assertIs(fa, f.find_contains_loc(0, 0, 0, 0))
        self.assertIs(fp, f.find_contains_loc(0, 1, 0, 1))
        self.assertIs(fb, f.find_contains_loc(0, 2, 0, 2))
        self.assertIs(f, f.find_contains_loc(0, 3, 0, 3))
        self.assertIs(fa, f.find_contains_loc(0, 0, 0, 1))
        self.assertIs(fo, f.find_contains_loc(0, 0, 0, 2))
        self.assertIs(fo, f.find_contains_loc(0, 0, 0, 3))
        self.assertIs(fp, f.find_contains_loc(0, 1, 0, 2))
        self.assertIs(fo, f.find_contains_loc(0, 1, 0, 3))
        self.assertIs(fb, f.find_contains_loc(0, 2, 0, 3))

        froot = FST('var', 'exec')
        fexpr = froot.body[0]
        fname = fexpr.value

        self.assertIs(fname, froot.find_contains_loc(0, 0, 0, 3, True))
        self.assertIs(None, froot.find_contains_loc(0, 0, 0, 3, False))
        self.assertIs(froot, froot.find_contains_loc(0, 0, 0, 3, 'top'))
        self.assertIs(fname, froot.find_contains_loc(0, 1, 0, 2, True))
        self.assertIs(fname, froot.find_contains_loc(0, 1, 0, 2, False))
        self.assertIs(fname, froot.find_contains_loc(0, 1, 0, 2, 'top'))
        self.assertIs(fname, froot.find_contains_loc(0, 0, 0, 1, True))
        self.assertIs(fname, froot.find_contains_loc(0, 0, 0, 1, False))
        self.assertIs(fname, froot.find_contains_loc(0, 0, 0, 1, 'top'))
        self.assertIs(fname, froot.find_contains_loc(0, 2, 0, 3, True))
        self.assertIs(fname, froot.find_contains_loc(0, 2, 0, 3, False))
        self.assertIs(fname, froot.find_contains_loc(0, 2, 0, 3, 'top'))

    def test_find_in_loc(self):
        f    = parse('abc += xyz').body[0].f
        fabc = f.target
        fpeq = f.op
        fxyz = f.value

        self.assertIs(f, f.find_in_loc(0, 0, 0, 10))
        self.assertIs(f, f.find_in_loc(-1, -1, 1, 11))
        self.assertIs(fabc, f.find_in_loc(0, 0, 0, 3))
        self.assertIs(fpeq, f.find_in_loc(0, 1, 0, 10))
        self.assertIs(fxyz, f.find_in_loc(0, 5, 0, 10))
        self.assertIs(None, f.find_in_loc(0, 5, 0, 6))

    def test_find_loc(self):
        f    = parse('abc += xyz').f
        fass = f.body[0]
        fabc = fass.target
        fpeq = fass.op
        fxyz = fass.value

        self.assertIs(fass, f.find_loc(0, 0, 0, 10))
        self.assertIs(f, f.find_loc(0, 0, 0, 10, True))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 3))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 3, True))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 4))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 4, True))
        self.assertIs(fass, f.find_loc(0, 3, 0, 4))
        self.assertIs(fass, f.find_loc(0, 3, 0, 4, True))
        self.assertIs(fpeq, f.find_loc(0, 4, 0, 6))
        self.assertIs(fpeq, f.find_loc(0, 4, 0, 6, True))
        self.assertIs(fxyz, f.find_loc(0, 7, 0, 10))
        self.assertIs(fxyz, f.find_loc(0, 7, 0, 10, True))
        self.assertIs(fxyz, f.find_loc(0, 6, 0, 10))
        self.assertIs(fxyz, f.find_loc(0, 6, 0, 10, True))
        self.assertIs(fass, f.find_loc(0, 6, 0, 9))
        self.assertIs(fass, f.find_loc(0, 6, 0, 9, True))

        f  = parse('a+b').f
        fx = f.body[0]
        fo = fx.value
        fa = fo.left
        fp = fo.op
        fb = fo.right

        self.assertIs(fa, f.find_loc(0, 0, 0, 0))
        self.assertIs(fp, f.find_loc(0, 1, 0, 1))
        self.assertIs(fb, f.find_loc(0, 2, 0, 2))
        self.assertIs(f, f.find_loc(0, 3, 0, 3))
        self.assertIs(fa, f.find_loc(0, 0, 0, 1))
        self.assertIs(fa, f.find_loc(0, 0, 0, 2))
        self.assertIs(fo, f.find_loc(0, 0, 0, 3))
        self.assertIs(f, f.find_loc(0, 0, 0, 3, True))
        self.assertIs(fp, f.find_loc(0, 1, 0, 2))
        self.assertIs(fp, f.find_loc(0, 1, 0, 3))
        self.assertIs(fb, f.find_loc(0, 2, 0, 3))

        froot = FST('var', 'exec')
        fexpr = froot.body[0]
        fname = fexpr.value

        self.assertIs(fname, froot.find_loc(0, 0, 0, 3))
        self.assertIs(froot, froot.find_loc(0, 0, 0, 3, True))
        self.assertIs(fname, froot.find_loc(0, 1, 0, 2))
        self.assertIs(fname, froot.find_loc(0, 1, 0, 2, True))
        self.assertIs(fname, froot.find_loc(0, 0, 0, 1))
        self.assertIs(fname, froot.find_loc(0, 0, 0, 1, True))
        self.assertIs(fname, froot.find_loc(0, 2, 0, 3))
        self.assertIs(fname, froot.find_loc(0, 2, 0, 3, True))

        f    = parse('abc += xyz').f
        fass = f.body[0]
        fabc = fass.target
        fpeq = fass.op
        fxyz = fass.value

        self.assertIs(fass, f.find_loc(0, 0, 0, 10))
        self.assertIs(f, f.find_loc(0, 0, 0, 10, True))
        self.assertIs(f, f.find_loc(-1, -1, 1, 11))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 3))
        self.assertIs(fpeq, f.find_loc(0, 1, 0, 10))
        self.assertIs(fxyz, f.find_loc(0, 5, 0, 10))
        self.assertIs(fpeq, f.find_loc(0, 4, 0, 6))
        self.assertIs(fass, f.find_loc(0, 6, 0, 7))
        self.assertIs(fass, f.find_loc(0, 6, 0, 7, True))

    def test_fstview(self):
        self.assertEqual('a', parse('if 1: a').f.body[0].body[0].src)
        self.assertEqual('b', parse('if 1: a\nelse: b').f.body[0].orelse[0].src)
        self.assertEqual('a\nb\nc', parse('a\nb\nc').f.body.copy().src)

        f = parse('a\nb\nc').f
        g = f.body.cut(norm=False)
        self.assertEqual('', f.src)
        self.assertEqual('a\nb\nc', g.src)

        f = parse('a\nb\nc\nd\ne').f
        g = f.body[1:4].cut()
        self.assertEqual('a\ne', f.src)
        self.assertEqual('b\nc\nd', g.src)

        f = parse('a\nb\nc\nd\ne').f
        g = f.body[1:4]
        g.replace('f')
        self.assertEqual(1, len(g))
        self.assertEqual('f', g[0].src)
        self.assertEqual('a\nf\ne', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.append('d')
        self.assertEqual(2, len(g))
        self.assertEqual('b', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('a\nb\nd\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.extend('d\ne')
        self.assertEqual(3, len(g))
        self.assertEqual('b', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('a\nb\nd\ne\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prepend('d')
        self.assertEqual(2, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('b', g[1].src)
        self.assertEqual('a\nd\nb\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prextend('d\ne')
        self.assertEqual(3, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('e', g[1].src)
        self.assertEqual('b', g[2].src)
        self.assertEqual('a\nd\ne\nb\nc', f.src)

        f = parse('a\nb\nc').f
        f.body[1:2] = 'd\ne'
        self.assertEqual('a\nd\ne\nc', f.src)

        f = parse('a\nb\nc').f
        f.body[1] = 'd'
        self.assertEqual('a\nd\nc', f.src)

        f = parse('a\nb\nc\nd\ne').f
        f.body[1:4] = 'f'
        self.assertEqual('a\nf\ne', f.src)

        f = parse('a\nb\nc\nd\ne').f
        f.body[1:4] = 'f\ng'
        self.assertEqual('a\nf\ng\ne', f.src)

        f = parse('a\nb\nc').f
        def test():
            f.body[1] = 'd\ne'
        self.assertRaises(ValueError, test)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prextend('d\ne')

        f = parse('a\nb\nc').f
        g = f.body
        g.cut(norm=False)
        self.assertEqual(0, len(g))
        self.assertEqual('', f.src)
        g.append('d')
        self.assertEqual(1, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('d', f.src)
        g.prepend('e')
        self.assertEqual(2, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('e\nd', f.src)
        g.extend('f\ng')
        self.assertEqual(4, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('f', g[2].src)
        self.assertEqual('g', g[3].src)
        self.assertEqual('e\nd\nf\ng', f.src)
        g.prextend('h\ni')
        self.assertEqual(6, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('i', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('d', g[3].src)
        self.assertEqual('f', g[4].src)
        self.assertEqual('g', g[5].src)
        self.assertEqual('h\ni\ne\nd\nf\ng', f.src)
        g.replace('h')
        self.assertEqual(1, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('h', f.src)
        g.insert('i')
        self.assertEqual(2, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('h', g[1].src)
        self.assertEqual('i\nh', f.src)
        g.insert('j', 1)
        self.assertEqual(3, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('h', g[2].src)
        self.assertEqual('i\nj\nh', f.src)
        g.insert('k', -1)
        self.assertEqual(4, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('i\nj\nk\nh', f.src)
        g.insert('l', 'end')
        self.assertEqual(5, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('l', g[4].src)
        self.assertEqual('i\nj\nk\nh\nl', f.src)

        f = parse('x\na\nb\nc\ny').f
        g = f.body[1:-1]
        g.cut()
        self.assertEqual(0, len(g))
        self.assertEqual('x\ny', f.src)
        g.append('d')
        self.assertEqual(1, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('x\nd\ny', f.src)
        g.prepend('e')
        self.assertEqual(2, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('x\ne\nd\ny', f.src)
        g.extend('f\ng')
        self.assertEqual(4, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('f', g[2].src)
        self.assertEqual('g', g[3].src)
        self.assertEqual('x\ne\nd\nf\ng\ny', f.src)
        g.prextend('h\ni')
        self.assertEqual(6, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('i', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('d', g[3].src)
        self.assertEqual('f', g[4].src)
        self.assertEqual('g', g[5].src)
        self.assertEqual('x\nh\ni\ne\nd\nf\ng\ny', f.src)
        g.replace('h')
        self.assertEqual(1, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('x\nh\ny', f.src)
        g.insert('i')
        self.assertEqual(2, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('h', g[1].src)
        self.assertEqual('x\ni\nh\ny', f.src)
        g.insert('j', 1)
        self.assertEqual(3, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('h', g[2].src)
        self.assertEqual('x\ni\nj\nh\ny', f.src)
        g.insert('k', -1)
        self.assertEqual(4, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('x\ni\nj\nk\nh\ny', f.src)
        g.insert('l', 'end')
        self.assertEqual(5, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('l', g[4].src)
        self.assertEqual('x\ni\nj\nk\nh\nl\ny', f.src)

        a = parse('''
class cls:
    def prefunc(): pass
    def postfunc(): pass
            '''.strip())
        self.assertIsInstance(a.f.body, fstview)
        self.assertIsInstance(a.body[0].f.body, fstview)
        a.body[0].f.body.cut(norm=False)
        self.assertIsInstance(a.body[0].f.body, fstview)

        a = parse('a\nb\nc\nd\ne')
        p = a.f.body[1:4]
        g = p[1]
        f = p.replace('f')
        self.assertEqual('a\nf\ne', a.f.src)
        self.assertEqual(1, len(f))
        self.assertEqual('f', f[0].src)
        self.assertIsNone(g.a)

        c = FST('a\nb').body
        c[0] = None
        self.assertEqual('b', c.base.src)
        self.assertEqual(1, c.stop)

        c = FST().body
        c[0:0] = 'a\nb'
        self.assertEqual('a\nb', c.base.src)
        self.assertEqual(2, c.stop)

    def test_fstview_refresh_indices(self):
        f = FST('[a, b, c]')
        v = f.elts
        self.assertEqual('<<List ROOT 0,0..0,9>.elts [<Name 0,1..0,2>, <Name 0,4..0,5>, <Name 0,7..0,8>]>', repr(v))

        f.put_slice('x', 'end')
        self.assertEqual('<<List ROOT 0,0..0,12>.elts [<Name 0,1..0,2>, <Name 0,4..0,5>, <Name 0,7..0,8>, <Name 0,10..0,11>]>', repr(v))

        f.elts[1:3].remove()
        self.assertEqual('<<List ROOT 0,0..0,6>.elts [<Name 0,1..0,2>, <Name 0,4..0,5>]>', repr(v))

        # TODO: this is not exhaustive

    def test_fstview_fixed_indices(self):
        # update non-refreshing indices

        f = FST('[1, 2, 3, 4]')
        v = f.elts[1:3]
        self.assertEqual(3, v.stop)

        del v[-1:]
        self.assertEqual('[1, 2, 4]', f.src)
        self.assertEqual(2, v.stop)

        del v[-1]
        self.assertEqual('[1, 4]', f.src)
        self.assertEqual(1, v.stop)

        v[0:] = 'x, y'
        self.assertEqual('[1, x, y, 4]', f.src)
        self.assertEqual(3, v.stop)

        v[-1] = 'z'
        self.assertEqual('[1, x, z, 4]', f.src)
        self.assertEqual(3, v.stop)

        self.assertEqual('[x, z]', v.copy().src)
        self.assertEqual('[[a, b]]', v.replace('[a, b]', one=False).copy().src)
        self.assertEqual('[a, b]', v.replace('[a, b]', one=None).copy().src)
        self.assertEqual('[a, b]', v.replace('a, b', one=False).copy().src)
        self.assertEqual(3, v.stop)
        self.assertEqual('[[c, d]]', v.replace('[c, d]').copy().src)
        self.assertEqual(2, v.stop)
        self.assertEqual('[[c, d]]', v.cut().src)
        self.assertEqual('[1, 4]', f.src)
        self.assertEqual('[1, e, f, 4]', v.insert('e, f', 0, one=False).base.src)
        self.assertEqual('[1, e, (g, h), f, 4]', v.insert('g, h', 1).base.src)
        self.assertEqual(4, v.stop)
        self.assertEqual('[1, 4]', v.remove().base.src)
        self.assertEqual('[1, a, 4]', v.append('a').base.src)
        self.assertEqual('[1, a, b, c, 4]', v.extend('b, c').base.src)
        self.assertEqual('[1, d, a, b, c, 4]', v.prepend('d').base.src)
        self.assertEqual('[1, e, f, d, a, b, c, 4]', v.prextend('e, f').base.src)
        self.assertEqual(1, v.start)
        self.assertEqual(7, v.stop)

    def test_fstview_dummy(self):
        v = fstview_dummy(FST('a'), 'type_params')

        self.assertRaises(IndexError, lambda: v[0])
        self.assertIs(v, v[:])

        self.assertRaises(IndexError, lambda: v[0])
        def setitem(idx): v[idx] = True
        self.assertRaises(RuntimeError, setitem, builtins.slice(None, None))
        self.assertRaises(IndexError, setitem, 0)
        v[:] = None

        def delitem(): del v[0]
        self.assertRaises(IndexError, delitem)
        del v[:]

        self.assertRaises(RuntimeError, v.copy)
        self.assertRaises(RuntimeError, v.cut)
        self.assertIs(v, v.replace(None))
        self.assertRaises(RuntimeError, v.replace, True)
        self.assertIs(v, v.remove())
        self.assertIs(v, v.insert(None))
        self.assertRaises(RuntimeError, v.insert, True)
        self.assertIs(v, v.append(None))
        self.assertRaises(RuntimeError, v.append, True)
        self.assertIs(v, v.extend(None))
        self.assertRaises(RuntimeError, v.extend, True)
        self.assertIs(v, v.prepend(None))
        self.assertRaises(RuntimeError, v.prepend, True)
        self.assertIs(v, v.prextend(None))
        self.assertRaises(RuntimeError, v.prextend, True)

        self.assertEqual('<<Name ROOT 0,0..0,1>.type_params DUMMY VIEW>', repr(v))

    def test_fstview_coverage(self):
        # misc stuff to fill out test coverage

        # slice with step errors

        v = FST('[1, 2, 3]').elts
        self.assertRaises(IndexError, lambda: v[::2])
        def setitem(): v[::2] = True
        self.assertRaises(IndexError, setitem)
        def delitem(): del v[::2]
        self.assertRaises(IndexError, delitem)

    def test_fstview_named_indexing(self):
        f = FST('''
if 1:                     # ln 0
    def f(a): pass        # ln 1
    def g(b): pass        # ln 2
    class f(c): pass      # ln 3
else:                     # ln 4
    class f(d):           # ln 5
        def g(e): pass    # ln 6
    def h(f): pass        # ln 7
    try:                  # ln 8
        def i(g): pass    # ln 9
    except:               # ln 10
        def j(h): pass    # ln 11
    else:                 # ln 12
        class i(i): pass  # ln 13
    finally:              # ln 14
        class j(j): pass  # ln 15
def h(k): pass            # ln 16
'''.strip())

        self.assertEqual('<FunctionDef 7,4..7,18>', str(f['h']))
        self.assertEqual('<FunctionDef 7,4..7,18>', str(f.body['h']))

        self.assertEqual('<FunctionDef 1,4..1,18>', str(f['f']))
        self.assertEqual('<FunctionDef 1,4..1,18>', str(f.body['f']))
        self.assertEqual('<FunctionDef 1,4..1,18>', str(f.body[0].body['f']))
        self.assertEqual('<ClassDef 5,4..6,22>', str(f.body[0].orelse['f']))

        self.assertEqual('<FunctionDef 6,8..6,22>', str(f.body[0].orelse['f.g']))

        self.assertEqual('<FunctionDef 2,4..2,18>', str(f['g']))
        self.assertEqual('<FunctionDef 2,4..2,18>', str(f.body['g']))
        self.assertEqual('<FunctionDef 2,4..2,18>', str(f.body[0].body['g']))
        self.assertRaises(IndexError, lambda: f.body[0].orelse['g'])
        self.assertEqual('<FunctionDef 7,4..7,18>', str(f.body[0].orelse['h']))

        self.assertEqual('<FunctionDef 9,8..9,22>', str(f['i']))
        self.assertEqual('<FunctionDef 9,8..9,22>', str(f.body['i']))
        self.assertEqual('<FunctionDef 9,8..9,22>', str(f.body[0].orelse['i']))
        self.assertEqual('<FunctionDef 9,8..9,22>', str(f.body[0].orelse[2].body['i']))

        self.assertEqual('<FunctionDef 11,8..11,22>', str(f['j']))
        self.assertEqual('<FunctionDef 11,8..11,22>', str(f.body['j']))
        self.assertEqual('<FunctionDef 11,8..11,22>', str(f.body[0].orelse['j']))
        self.assertEqual('<FunctionDef 11,8..11,22>', str(f.body[0].orelse[2].handlers[0].body['j']))

        self.assertEqual('<ClassDef 13,8..13,24>', str(f.body[0].orelse[2].orelse['i']))

        self.assertEqual('<ClassDef 15,8..15,24>', str(f.body[0].orelse[2].finalbody['j']))

    def test_options(self):
        new = dict(
            docstr    = 'test_docstr',
            trivia    = 'test_trivia',
            pep8space = 'test_pep8space',
            pars      = 'test_pars',
            elif_     = 'test_elif_',
            raw       = 'test_raw',
        )

        old    = FST.set_options(**new)
        newset = FST.set_options(**old)
        oldset = FST.set_options(**old)

        self.assertEqual(newset, new)
        self.assertEqual(oldset, old)

        with FST.options(**new) as opts:
            self.assertEqual(opts, old)
            self.assertEqual(new, FST.set_options(**new))

        self.assertEqual(old, FST.set_options(**old))

        try:
            with FST.options(**new) as opts:
                self.assertEqual(opts, old)
                self.assertEqual(new, FST.set_options(**new))

                raise NodeError

        except NodeError:
            pass

        self.assertEqual(old, FST.set_options(**old))

    def test_options_invalid(self):
        self.assertRaises(ValueError, FST.set_options, invalid_option=True)
        self.assertRaises(ValueError, FST.set_options, to=True)
        self.assertRaises(ValueError, FST.set_options, op=True)

        f = FST('[a]')

        self.assertRaises(ValueError, f.reconcile, invalid_option=True)  # doesn't matter what we call it with, the options check is first and should raise immediately
        self.assertRaises(ValueError, f.copy, invalid_option=True)
        self.assertRaises(ValueError, f.cut, invalid_option=True)
        self.assertRaises(ValueError, f.replace, None, invalid_option=True)
        self.assertRaises(ValueError, f.remove, invalid_option=True)
        self.assertRaises(ValueError, f.get, invalid_option=True)
        self.assertRaises(ValueError, f.get_slice, invalid_option=True)
        self.assertRaises(ValueError, f.put, None, invalid_option=True)
        self.assertRaises(ValueError, f.put_slice, None, invalid_option=True)
        self.assertRaises(ValueError, f.put_docstr, None, invalid_option=True)

        v = f.elts

        self.assertRaises(ValueError, v.copy, invalid_option=True)
        self.assertRaises(ValueError, v.cut, invalid_option=True)
        self.assertRaises(ValueError, v.replace, None, invalid_option=True)
        self.assertRaises(ValueError, v.remove, invalid_option=True)
        self.assertRaises(ValueError, v.insert, None, invalid_option=True)
        self.assertRaises(ValueError, v.append, None, invalid_option=True)
        self.assertRaises(ValueError, v.extend, None, invalid_option=True)
        self.assertRaises(ValueError, v.prepend, None, invalid_option=True)
        self.assertRaises(ValueError, v.prextend, None, invalid_option=True)

    def test_options_thread_local(self):
        def threadfunc(barrier, ret, option, value):
            FST.set_options(**{option: value})
            barrier.wait()

            ret[0] = FST.get_option(option)

        barrier = threading.Barrier(2)
        thread0 = threading.Thread(target=threadfunc, args=(barrier, ret0 := [None], 'pars', True))
        thread1 = threading.Thread(target=threadfunc, args=(barrier, ret1 := [None], 'pars', False))

        thread0.start()
        thread1.start()
        thread0.join()
        thread1.join()

        self.assertEqual('auto', FST.get_option('pars'))
        self.assertEqual(True, ret0[0])
        self.assertEqual(False, ret1[0])

    def test_reconcile(self):
        # basic replacements

        self.assertRaises(ValueError, FST('i = 1').value.mark)

        o = FST('i = 1').mark()

        self.assertRaises(ValueError, o.value.reconcile)  # only on root
        oldo = o

        o.a.value = Name(id='test')
        o = o.reconcile()
        self.assertEqual('i = test', o.src)
        o.verify()

        self.assertFalse(oldo.is_alive)

        o.mark()
        o.a.targets[0].id = 'blah'
        o = o.reconcile()
        self.assertEqual('blah = test', o.src)
        o.verify()

        o.mark()
        o.a.value = copy_ast(o.a.targets[0])
        o = o.reconcile()
        self.assertEqual('blah = blah', o.src)
        o.verify()

        o.mark()
        o.a.value.ctx = Load()
        o.a.targets[0].ctx = Store()
        o = o.reconcile()
        self.assertEqual('blah = blah', o.src)
        o.verify()

        # error causing parent replacement

        if PYGE12:
            o = FST("f'{a}'").mark()

            o.a.values[0].conversion = 97
            o = o.reconcile()
            self.assertEqual("f'{a!a}'", o.src)
            o.verify()

            o.mark()
            o.a.values[0].conversion = 115
            o = o.reconcile()
            self.assertEqual("f'{a!s}'", o.src)
            o.verify()

            o.mark()
            o.a.values[0].conversion = 114
            o = o.reconcile()
            self.assertEqual("f'{a!r}'", o.src)
            o.verify()

            o.mark()
            o.a.values[0].conversion = -1
            o = o.reconcile()
            self.assertEqual("f'{a}'", o.src)
            o.verify()

        # misc change ctx

        o = FST('i').mark()
        o.a.ctx = Load()
        o = o.reconcile()
        self.assertEqual('i', o.src)
        self.assertIsInstance(o.a.ctx.f, FST)
        o.verify()

        # AST from same tree moved around

        o = FST('i = a').mark()
        o.a.value = Starred(value=o.a.value)
        o = o.reconcile()
        self.assertEqual('i = *a', o.src)
        o.verify()

        # FST from another tree

        o = FST('i = 1').mark()
        o.a.value = FST('(x,\n # comment\ny)').a
        o = o.reconcile()
        self.assertEqual('i = (x,\n # comment\ny)', o.src)
        o.verify()

        # delete one from non-slice

        o = FST('def f() -> int: pass').mark()
        o.a.returns = None
        o = o.reconcile()
        self.assertEqual('def f(): pass', o.src)
        o.verify()

        # add nonexistent node from pure AST

        o = FST('def f(): int').mark()
        o.a.returns = Name(id='str')
        o = o.reconcile()
        self.assertEqual('def f() -> str: int', o.src)
        o.verify()

        # add nonexistent node from same tree

        o = FST('def f(): int').mark()
        o.a.returns = o.a.body[0].value
        o = o.reconcile()
        self.assertEqual('def f() -> int: int', o.src)
        o.verify()

        # replace root from same tree

        o = FST('def f(): int').mark()
        o.a = o.a.body[0].value
        o = o.reconcile()
        self.assertIsInstance(o.a, Name)
        self.assertEqual('int', o.src)
        o.verify()

        # replace root from different tree

        o = FST('def f(): int').mark()
        o.a = FST('call()').a
        o = o.reconcile()
        self.assertIsInstance(o.a, Call)
        self.assertEqual('call()', o.src)
        o.verify()

        # replace root from pure AST

        o = FST('def f(): int').mark()
        o.a = Name(id='hello')
        o = o.reconcile()
        self.assertIsInstance(o.a, Name)
        self.assertEqual('hello', o.src)
        o.verify()

        # simple slice replace

        o = FST('[\n1,  # one\n2,  # two\n3   # three\n]').mark()
        o.a.elts[0] = UnaryOp(USub(), Constant(value=1))
        o.a.elts[1] = UnaryOp(USub(), Constant(value=2))
        o.a.elts[2] = UnaryOp(USub(), Constant(value=3))
        o = o.reconcile()
        self.assertEqual('[\n-1,  # one\n-2,  # two\n-3   # three\n]', o.src)
        o.verify()

        # 2 level pure AST

        o = FST('i = 1').mark()
        o.a.value = List(elts=[Name(id='a')])
        o = o.reconcile()
        self.assertEqual('i = [a]', o.src)
        o.verify()

        # level 1 pure AST, level 2 from another tree

        o = FST('i = 1').mark()
        o.a.value = List(elts=[FST('(a, # yay!\n)').a])
        o = o.reconcile()
        self.assertEqual('i = [(a, # yay!\n)]', o.src)
        o.verify()

        # level 1 pure AST, level 2 from same tree

        o = FST('i = (a, # yay!\n)').mark()
        o.a.value = List(elts=[o.value.a])
        o = o.reconcile()
        self.assertEqual('i = [(a, # yay!\n)]', o.src)
        o.verify()

        # slice, don't do first because src is at end and don't do second because dst is at end

        o = FST('[\n1, # 1\n2, # 2\n]').mark()
        a = o.a.elts[0]
        o.a.elts[0] = o.a.elts[1]
        o.a.elts[1] = a
        o = o.reconcile()
        self.assertEqual('[\n2, # 2\n1, # 1\n]', o.src)
        o.verify()

        # slice, delete tail

        o = FST('[1, 2, 3, 4]').mark()
        del o.a.elts[2:]
        o = o.reconcile()
        self.assertEqual('[1, 2]', o.src)
        o.verify()

        o = FST('[1, 2, 3, 4]').mark()
        del o.a.elts[:]
        o = o.reconcile()
        self.assertEqual('[]', o.src)
        o.verify()

        # slice, swap two from same tree

        o = FST('[1, 2, 3, 4]').mark()
        e0 = o.a.elts[0]
        e1 = o.a.elts[1]
        o.a.elts[0] = o.a.elts[2]
        o.a.elts[1] = o.a.elts[3]
        o.a.elts[2] = e0
        o.a.elts[3] = e1
        o = o.reconcile()
        self.assertEqual('[3, 4, 1, 2]', o.src)
        o.verify()

        # slice, extend from same tree

        o = FST('[1, 2, 3]').mark()
        o.a.elts.extend(o.a.elts[:2])
        o = o.reconcile()
        self.assertEqual('[1, 2, 3, 1, 2]', o.src)
        o.verify()

        # slice, extend from different tree

        o = FST('[1, 2, 3]').mark()
        o.a.elts.extend(FST('[4, 5]').a.elts)
        o = o.reconcile()
        self.assertEqual('[1, 2, 3, 4, 5]', o.src)
        o.verify()

        # slice, extend from pure ASTs

        o = FST('[1, 2, 3]').mark()
        o.a.elts.extend([Name(id='x'), Name(id='y')])
        o = o.reconcile()
        self.assertEqual('[1, 2, 3, x, y]', o.src)
        o.verify()

        o = FST('i = 1\nj = 2\nk = 3').mark()
        o.a.body.append(Assign(targets=[Name(id='x')], value=Constant(value=4)))
        o.a.body.append(Assign(targets=[Name(id='y')], value=Constant(value=5)))
        o = o.reconcile()
        self.assertEqual('i = 1\nj = 2\nk = 3\nx = 4\ny = 5', o.src)
        o.verify()

        # other recurse slice FST

        o = FST('[1]').mark()
        o.a.elts.extend(FST('[2,#2\n3,#3\n4,#4\n]').a.elts)
        o = o.reconcile()
        self.assertEqual('[1, 2,#2\n 3,#3\n 4,#4\n]', o.src)
        o.verify()

        o = FST('{a: b, **c}').mark()
        o.a.keys[1] = o.a.keys[0]
        o.a.keys[0] = None
        o = o.reconcile()
        self.assertEqual('{**b, a: c}', o.src)
        o.verify()

        o = FST('if 1:\n  i = 1\n  j = 2\n  k = 3\nelse:\n  a = 4\n  b = 5\n  c = 6').mark()
        body = o.a.body[:]
        o.a.body[:] = o.a.orelse[1:]
        o.a.orelse = body * 2
        o = o.reconcile()
        self.assertEqual('if 1:\n  b = 5\n  c = 6\nelse:\n  i = 1\n  j = 2\n  k = 3\n  i = 1\n  j = 2\n  k = 3', o.src)
        o.verify()

        o = FST('def f(*, a=1, b=2): pass').mark()
        o.a.args.kw_defaults[0] = None
        o = o.reconcile()
        self.assertEqual('def f(*, a, b=2): pass', o.src)
        o.verify()

        o = FST('{1: a, **b}', MatchMapping).mark()
        o.a.rest = None
        o = o.reconcile()
        self.assertEqual('{1: a}', o.src)
        o.verify()

        o = FST('{1: a, **b}', MatchMapping).mark()
        o.a.rest = 'rest'
        o = o.reconcile()
        self.assertEqual('{1: a, **rest}', o.src)
        o.verify()

        o = FST('{1: a}', MatchMapping).mark()
        o.a.rest = 'rest'
        o = o.reconcile()
        self.assertEqual('{1: a, **rest}', o.src)
        o.verify()

        # recurse slice in pure AST that has FSTs

        o = FST('[\n1, # 1\n2, # 2\n]').mark()
        o.a = List(elts=[o.a.elts[1], o.a.elts[0]])
        o = o.reconcile()
        self.assertEqual('[\n 2, # 2\n 1, # 1\n]', o.src)
        o.verify()

        o = FST('[1,\n# 1and2\n2, 3,\n# 3and4\n4]').mark()
        o.a = List(elts=[o.a.elts[2], o.a.elts[3], o.a.elts[0], o.a.elts[1]])
        o = o.reconcile()
        self.assertEqual('[3,\n # 3and4\n 4, 1,\n # 1and2\n 2]', o.src)
        o.verify()

        o = FST('[1,#1\n]').mark()
        o.a = List(elts=[o.a.elts[0]])
        o.a.elts.extend(FST('[2,#2\n3,#3\n4,#4\n]').a.elts)
        o = o.reconcile()
        self.assertEqual('[1, #1\n 2,#2\n 3,#3\n 4,#4\n]', o.src)
        o.verify()

        o = FST('{a: b, **c}').mark()
        o.a = Dict(keys=[None, o.a.keys[0]], values=[o.a.values[0], o.a.values[1]])
        o = o.reconcile()
        self.assertEqual('{**b, a: c}', o.src)
        o.verify()

        o = FST('def f(*, a=1, b=2): pass').mark()
        o.a.args = arguments(kwonlyargs=o.a.args.kwonlyargs, kw_defaults=[None, o.a.args.kw_defaults[1]], posonlyargs=[], args=[], defaults=[])
        o = o.reconcile()
        self.assertEqual('def f(*, a, b=2): pass', o.src)
        o.verify()

        o = FST('{1: a, **b}', MatchMapping).mark()
        o.a = MatchMapping(keys=[o.a.keys[0]], patterns=[o.a.patterns[0]], rest=None)
        o = o.reconcile()
        self.assertEqual('{1: a}', o.src)
        o.verify()

        o = FST('{1: a, **b}', MatchMapping).mark()
        o.a = MatchMapping(keys=[o.a.keys[0]], patterns=[o.a.patterns[0]], rest='rest')
        o = o.reconcile()
        self.assertEqual('{1: a, **rest}', o.src)
        o.verify()

        o = FST('{1: a}', MatchMapping).mark()
        o.a = MatchMapping(keys=[o.a.keys[0]], patterns=[o.a.patterns[0]], rest='rest')
        o = o.reconcile()
        self.assertEqual('{1: a, **rest}', o.src)
        o.verify()

        # Dict

        o = FST('{a: b}').mark()
        o.a.keys[0] = Name(id='x')
        o.a.values[0] = Name(id='y')
        o = o.reconcile()
        self.assertEqual('{x: y}', o.src)
        o.verify()

        o = FST('{a: b}').mark()
        o.a.keys[0] = None
        o = o.reconcile()
        self.assertEqual('{**b}', o.src)
        o.verify()

        o = FST('{a : b, c : d}').mark()
        a = o.a
        a.keys.append(Name(id='x'))
        a.values.append(Name(id='y'))
        a.keys.extend(a.keys[:2])
        a.values.extend(a.values[:2])
        b = FST('{s : t, u : v}').a
        a.keys.extend(b.keys)
        a.values.extend(b.values)
        o = o.reconcile()
        self.assertEqual('{a : b, c : d, x: y, a : b, c : d, s : t, u : v}', o.src)
        o.verify()

        o = FST('{a : b, c : d}').mark()
        a = o.a
        a.keys.append(Name(id='x'))
        a.values.append(Name(id='y'))
        a.keys.extend(a.keys[:2])
        a.values.extend(a.values[:2])
        b = FST('{s : t, u : v}').a
        a.keys.extend(b.keys)
        a.values.extend(b.values)
        o.a = Dict(keys=o.a.keys, values=o.a.values)
        o = o.reconcile()
        self.assertEqual('{a : b, c : d, x: y, a : b, c : d, s : t, u : v}', o.src)
        o.verify()

        # operators

        o = FST('a or b or c')
        m = o.mark()
        o.a.op = And()
        o = o.reconcile()
        self.assertEqual('a and b and c', o.src)
        o.verify()

        o = FST('a or b or c')
        m = o.mark()
        o.a.op = FST(And()).a
        o = o.reconcile()
        self.assertEqual('a and b and c', o.src)
        o.verify()

        o = FST('a or b or c\nd and e')
        m = o.mark()
        o.a.body[0].value.op = o.a.body[1].value.op
        o = o.reconcile()
        self.assertEqual('a and b and c\nd and e', o.src)
        o.verify()

        o = FST('a + b')
        m = o.mark()
        o.a.op = Mult()
        o = o.reconcile()
        self.assertEqual('a * b', o.src)
        o.verify()

        o = FST('a + b')
        m = o.mark()
        o.a.op = FST(Mult()).a
        o = o.reconcile()
        self.assertEqual('a * b', o.src)
        o.verify()

        o = FST('a + b')
        m = o.mark()
        o.a.op = FST('*').a
        o = o.reconcile()
        self.assertEqual('a * b', o.src)
        o.verify()

        o = FST('a + b\nc * d')
        m = o.mark()
        o.a.body[0].value.op = o.a.body[1].value.op
        o = o.reconcile()
        self.assertEqual('a * b\nc * d', o.src)
        o.verify()

        o = FST('a + b\nc *= d')
        m = o.mark()
        o.a.body[0].value.op = o.a.body[1].op
        o = o.reconcile()
        self.assertEqual('a * b\nc *= d', o.src)
        o.verify()

        o = FST('a += b')
        m = o.mark()
        o.a.op = Mult()
        o = o.reconcile()
        self.assertEqual('a *= b', o.src)
        o.verify()

        o = FST('a += b')
        m = o.mark()
        o.a.op = FST(Mult()).a
        o = o.reconcile()
        self.assertEqual('a *= b', o.src)
        o.verify()

        o = FST('a += b')
        m = o.mark()
        o.a.op = FST('*').a
        o = o.reconcile()
        self.assertEqual('a *= b', o.src)
        o.verify()

        o = FST('a += b\nc *= d')
        m = o.mark()
        o.a.body[0].op = o.a.body[1].op
        o = o.reconcile()
        self.assertEqual('a *= b\nc *= d', o.src)
        o.verify()

        o = FST('a += b\nc * d')
        m = o.mark()
        o.a.body[0].op = o.a.body[1].value.op
        o = o.reconcile()
        self.assertEqual('a *= b\nc * d', o.src)
        o.verify()

        o = FST('-a')
        m = o.mark()
        o.a.op = Not()
        o = o.reconcile()
        self.assertEqual('not a', o.src)
        o.verify()

        o = FST('-a')
        m = o.mark()
        o.a.op = FST(Not()).a
        o = o.reconcile()
        self.assertEqual('not a', o.src)
        o.verify()

        o = FST('-a\nnot b')
        m = o.mark()
        o.a.body[0].value.op = o.a.body[1].value.op
        o = o.reconcile()
        self.assertEqual('not a\nnot b', o.src)
        o.verify()

        o = FST('a<b')
        m = o.mark()
        o.a.ops[0] = IsNot()
        o = o.reconcile()
        self.assertEqual('a is not b', o.src)
        o.verify()

        o = FST('a<b')
        m = o.mark()
        o.a.ops[0] = FST(IsNot()).a
        o = o.reconcile()
        self.assertEqual('a is not b', o.src)
        o.verify()

        o = FST('a<b\nc is not d')
        m = o.mark()
        o.a.body[0].value.ops[0] = o.a.body[1].value.ops[0]
        o = o.reconcile()
        self.assertEqual('a is not b\nc is not d', o.src)
        o.verify()

        # misc

        if not PYLT12:
            m = (o := FST(r'''
if 1:
    "a\n"
    f"{f()}"
                '''.strip(), 'exec')).mark()
            o.a.body[0].body[1].value.values[0].value.func = o.a.body[0].body[0].value
            o = o.reconcile()
            self.assertEqual(r'''
if 1:
    "a\n"
    f"{"a\n"()}"
                '''.strip(), o.src)
            o.verify()

        a = (o := FST('[\n[\n[\n[\n[\n[\n[\n[\nx,#0\n0\n],#1\n1\n],#2\n2\n],#3\n3\n],#4\n4\n],#5\n5\n],#6\n6\n],#7\n7\n]')).a
        m = o.mark()
        a.elts[0] = List(elts=[a.elts[0].elts[0]])
        a.elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0]])
        o = o.reconcile()
        self.assertEqual('[\n[\n [\n[\n [\n[\n [\n[\n x,#0\n],#1\n1\n],#2\n],#3\n3\n],#4\n],#5\n5\n],#6\n],#7\n7\n]', o.src)
        o.verify()

        a = (o := FST('[\n[\n[\n[\n[\n[\n[\n[\nx,#0\n0\n],#1\n1\n],#2\n2\n],#3\n3\n],#4\n4\n],#5\n5\n],#6\n6\n],#7\n7\n]')).a
        m = o.mark()
        o.a = List(elts=[a.elts[0]])
        a.elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0]])
        a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0] = List(elts=[a.elts[0].elts[0].elts[0].elts[0].elts[0].elts[0].elts[0]])
        o = o.reconcile()
        self.assertEqual('[\n [\n[\n [\n[\n [\n[\n [\nx,#0\n0\n],#1\n],#2\n2\n],#3\n],#4\n4\n],#5\n],#6\n6\n],#7\n]', o.src)
        o.verify()

        a = (o := FST('f(#0\ng(#1\nh(#2\ni(#3\n))))')).a
        m = o.mark()
        a.args[0] = Call(func=Name('g'), args=[a.args[0].args[0]], keywords=[])
        a.args[0].args[0].args[0] = Call(func=Name('i'), args=[], keywords=[])
        o = o.reconcile()
        self.assertEqual('f(#0\ng(h(#2\ni())))', o.src)
        o.verify()

        # allowed options

        self.assertEqual('i', FST('i').mark().reconcile(elif_=True).src)
        self.assertEqual('i', FST('i').mark().reconcile(pep8space=1).src)

        # disallowed options

        o = FST('i').mark()

        self.assertRaises(ValueError, FST('i').reconcile, raw=None)
        self.assertRaises(ValueError, FST('i').reconcile, trivia=None)
        self.assertRaises(ValueError, FST('i').reconcile, coerce=None)
        self.assertRaises(ValueError, FST('i').reconcile, docstr=None)
        self.assertRaises(ValueError, FST('i').reconcile, pars=None)
        self.assertRaises(ValueError, FST('i').reconcile, pars_walrus=None)
        self.assertRaises(ValueError, FST('i').reconcile, pars_arglike=None)
        self.assertRaises(ValueError, FST('i').reconcile, norm=None)
        self.assertRaises(ValueError, FST('i').reconcile, norm_self=None)
        self.assertRaises(ValueError, FST('i').reconcile, norm_get=None)

        # unmarked error

        self.assertRaises(RuntimeError, FST('i').reconcile)

        # make sure modifications are detected

        o = FST('i = [a, b]').mark()
        self.assertEqual('i = [a, b]', o.reconcile().src)  # no modification no error

        o = FST('i = [a, b]').mark()
        o.value.elts = '[]'
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('i = [a, b]').mark()
        o.value.elts[0] = 'a'
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('i = [a, b]').mark()
        del o.value.elts
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('i = [a, b]').mark()
        o.value.elts[0] = 'a'
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('i = 1').mark()
        o.value = '1'
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('i = 1').mark()
        o.value.par(True)
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('i = (1)').mark()
        o.value.unpar()
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('i = 1').mark()
        o.put_src('j', 0, 0, 0, 1)
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('i = 1').mark()
        o.put_src(' ', 0, 1, 0, 1, 'offset')
        self.assertRaises(RuntimeError, o.reconcile)

        o = FST('def f(): pass').mark()
        o.put_docstr("test")
        self.assertRaises(RuntimeError, o.reconcile)

    def test_reconcile_slices(self):
        o = FST('a # a\nb # b\nc # c', 'exec').mark()
        o.a.body[0] = o.a.body[1]
        o.a.body[1] = o.a.body[2]
        o = o.reconcile()
        self.assertEqual('b # b\nc # c\nc # c', o.src)
        o.verify()

        o = FST('{\na, # a\nb, # b\nc, # c\n}', 'exec').mark()
        o.a.body[0].value.elts[0] = o.a.body[0].value.elts[1]
        o.a.body[0].value.elts[1] = o.a.body[0].value.elts[2]
        o = o.reconcile()
        self.assertEqual('{\nb, # b\nc, # c\nc, # c\n}', o.src)
        o.verify()

        o = FST('[\na, # a\nb, # b\nc, # c\n]', 'exec').mark()
        o.a.body[0].value.elts[0] = o.a.body[0].value.elts[1]
        o.a.body[0].value.elts[1] = o.a.body[0].value.elts[2]
        o = o.reconcile()
        self.assertEqual('[\nb, # b\nc, # c\nc, # c\n]', o.src)
        o.verify()

        o = FST('(\na, # a\nb, # b\nc, # c\n)', 'exec').mark()
        o.a.body[0].value.elts[0] = o.a.body[0].value.elts[1]
        o.a.body[0].value.elts[1] = o.a.body[0].value.elts[2]
        o = o.reconcile()
        self.assertEqual('(\nb, # b\nc, # c\nc, # c\n)', o.src)
        o.verify()

        o = FST('{\na:a, # a\nb:b, # b\nc:c, # c\n}', 'exec').mark()
        o.a.body[0].value.keys[0] = o.a.body[0].value.keys[1]
        o.a.body[0].value.values[0] = o.a.body[0].value.values[1]
        o.a.body[0].value.keys[1] = o.a.body[0].value.keys[2]
        o.a.body[0].value.values[1] = o.a.body[0].value.values[2]
        o = o.reconcile()
        self.assertEqual('{\nb:b, # b\nc:c, # c\nc:c, # c\n}', o.src)
        o.verify()

        o = FST('@a # a\n@b # b\n@c # c\ndef f(): pass', 'exec').mark()
        o.a.body[0].decorator_list[0] = o.a.body[0].decorator_list[1]
        o.a.body[0].decorator_list[1] = o.a.body[0].decorator_list[2]
        o = o.reconcile()
        self.assertEqual('@b # a\n@c # b\n@c # c\ndef f(): pass', o.src)
        o.verify()

        o = FST('@a # a\n@b # b\n@c # c\nasync def f(): pass', 'exec').mark()
        o.a.body[0].decorator_list[0] = o.a.body[0].decorator_list[1]
        o.a.body[0].decorator_list[1] = o.a.body[0].decorator_list[2]
        o = o.reconcile()
        self.assertEqual('@b # a\n@c # b\n@c # c\nasync def f(): pass', o.src)
        o.verify()

        o = FST('@a # a\n@b # b\n@c # c\nclass cls: pass', 'exec').mark()
        o.a.body[0].decorator_list[0] = o.a.body[0].decorator_list[1]
        o.a.body[0].decorator_list[1] = o.a.body[0].decorator_list[2]
        o = o.reconcile()
        self.assertEqual('@b # a\n@c # b\n@c # c\nclass cls: pass', o.src)
        o.verify()

        o = FST('class cls(a,b,c): pass', 'exec').mark()
        o.a.body[0].bases[0] = o.a.body[0].bases[1]
        o.a.body[0].bases[1] = o.a.body[0].bases[2]
        o = o.reconcile()
        self.assertEqual('class cls(b,c,c): pass', o.src)
        o.verify()

        o = FST('del a,b,c', 'exec').mark()
        o.a.body[0].targets[0] = o.a.body[0].targets[1]
        o.a.body[0].targets[1] = o.a.body[0].targets[2]
        o = o.reconcile()
        self.assertEqual('del b,c,c', o.src)
        o.verify()

        o = FST('a=b=c = d', 'exec').mark()
        o.a.body[0].targets[0] = o.a.body[0].targets[1]
        o.a.body[0].targets[1] = o.a.body[0].targets[2]
        o = o.reconcile()
        self.assertEqual('b=c=c = d', o.src)
        o.verify()

        o = FST('a  or  b  or  c', 'exec').mark()
        o.a.body[0].value.values[0] = o.a.body[0].value.values[1]
        o.a.body[0].value.values[1] = o.a.body[0].value.values[2]
        o = o.reconcile()
        self.assertEqual('b  or  c  or  c', o.src)
        o.verify()

        o = FST('call(a,b,c)', 'exec').mark()
        o.a.body[0].value.args[0] = o.a.body[0].value.args[1]
        o.a.body[0].value.args[1] = o.a.body[0].value.args[2]
        o = o.reconcile()
        self.assertEqual('call(b,c,c)', o.src)
        o.verify()

        o = FST('[i for i in j if a if b if c]', 'exec').mark()
        o.a.body[0].value.generators[0].ifs[0] = o.a.body[0].value.generators[0].ifs[1]
        o.a.body[0].value.generators[0].ifs[1] = o.a.body[0].value.generators[0].ifs[2]
        o = o.reconcile()
        self.assertEqual('[i for i in j if b if c if c]', o.src)
        o.verify()

        o = FST('[i for k in l if k for j in k if j for i in j if i]', 'exec').mark()
        o.a.body[0].value.generators[0] = o.a.body[0].value.generators[1]
        o.a.body[0].value.generators[1] = o.a.body[0].value.generators[2]
        o = o.reconcile()
        self.assertEqual('[i for j in k if j for i in j if i for i in j if i]', o.src)
        o.verify()

        o = FST('{i for k in l if k for j in k if j for i in j if i}', 'exec').mark()
        o.a.body[0].value.generators[0] = o.a.body[0].value.generators[1]
        o.a.body[0].value.generators[1] = o.a.body[0].value.generators[2]
        o = o.reconcile()
        self.assertEqual('{i for j in k if j for i in j if i for i in j if i}', o.src)
        o.verify()

        o = FST('{i: i for k in l if k for j in k if j for i in j if i}', 'exec').mark()
        o.a.body[0].value.generators[0] = o.a.body[0].value.generators[1]
        o.a.body[0].value.generators[1] = o.a.body[0].value.generators[2]
        o = o.reconcile()
        self.assertEqual('{i: i for j in k if j for i in j if i for i in j if i}', o.src)
        o.verify()

        o = FST('(i for k in l if k for j in k if j for i in j if i)', 'exec').mark()
        o.a.body[0].value.generators[0] = o.a.body[0].value.generators[1]
        o.a.body[0].value.generators[1] = o.a.body[0].value.generators[2]
        o = o.reconcile()
        self.assertEqual('(i for j in k if j for i in j if i for i in j if i)', o.src)
        o.verify()

        o = FST('class cls(a=1,b=2,c=3): pass', 'exec').mark()
        o.a.body[0].keywords[0] = o.a.body[0].keywords[1]
        o.a.body[0].keywords[1] = o.a.body[0].keywords[2]
        o = o.reconcile()
        self.assertEqual('class cls(b=2,c=3,c=3): pass', o.src)
        o.verify()

        o = FST('call(a=1,b=2,c=3)', 'exec').mark()
        o.a.body[0].value.keywords[0] = o.a.body[0].value.keywords[1]
        o.a.body[0].value.keywords[1] = o.a.body[0].value.keywords[2]
        o = o.reconcile()
        self.assertEqual('call(b=2,c=3,c=3)', o.src)
        o.verify()

        o = FST('import a,b,c', 'exec').mark()
        o.a.body[0].names[0] = o.a.body[0].names[1]
        o.a.body[0].names[1] = o.a.body[0].names[2]
        o = o.reconcile()
        self.assertEqual('import b,c,c', o.src)
        o.verify()

        o = FST('from z import a,b,c', 'exec').mark()
        o.a.body[0].names[0] = o.a.body[0].names[1]
        o.a.body[0].names[1] = o.a.body[0].names[2]
        o = o.reconcile()
        self.assertEqual('from z import b,c,c', o.src)
        o.verify()

        o = FST('with a  as  a, b  as  b, c  as  c: pass', 'exec').mark()
        o.a.body[0].items[0] = o.a.body[0].items[1]
        o.a.body[0].items[1] = o.a.body[0].items[2]
        o = o.reconcile()
        self.assertEqual('with b  as  b, c  as  c, c  as  c: pass', o.src)
        o.verify()

        o = FST('async with a  as  a, b  as  b, c  as  c: pass', 'exec').mark()
        o.a.body[0].items[0] = o.a.body[0].items[1]
        o.a.body[0].items[1] = o.a.body[0].items[2]
        o = o.reconcile()
        self.assertEqual('async with b  as  b, c  as  c, c  as  c: pass', o.src)
        o.verify()

        o = FST('case [a,b,c]: pass', 'match_case').mark()
        o.a.pattern.patterns[0] = o.a.pattern.patterns[1]
        o.a.pattern.patterns[1] = o.a.pattern.patterns[2]
        o = o.reconcile()
        self.assertEqual('case [b,c,c]: pass', o.src)
        o.verify()

        o = FST('case {1:a,2:b,3:c}: pass', 'match_case').mark()
        o.a.pattern.keys[0] = o.a.pattern.keys[1]
        o.a.pattern.patterns[0] = o.a.pattern.patterns[1]
        o.a.pattern.keys[1] = o.a.pattern.keys[2]
        o.a.pattern.patterns[1] = o.a.pattern.patterns[2]
        o = o.reconcile()
        self.assertEqual('case {2:b,3:c,3:c}: pass', o.src)
        o.verify()

        o = FST('case cls(a,b,c): pass', 'match_case').mark()
        o.a.pattern.patterns[0] = o.a.pattern.patterns[1]
        o.a.pattern.patterns[1] = o.a.pattern.patterns[2]
        o = o.reconcile()
        self.assertEqual('case cls(b,c,c): pass', o.src)
        o.verify()

        o = FST('case a|b|c: pass', 'match_case').mark()
        o.a.pattern.patterns[0] = o.a.pattern.patterns[1]
        o.a.pattern.patterns[1] = o.a.pattern.patterns[2]
        o = o.reconcile()
        self.assertEqual('case b|c|c: pass', o.src)
        o.verify()

        o = FST('global a,b,c', 'exec').mark()
        o.a.body[0].names[0] = o.a.body[0].names[1]
        o.a.body[0].names[1] = o.a.body[0].names[2]
        o = o.reconcile()
        self.assertEqual('global b,c,c', o.src)
        o.verify()

        o = FST('nonlocal a,b,c', 'exec').mark()
        o.a.body[0].names[0] = o.a.body[0].names[1]
        o.a.body[0].names[1] = o.a.body[0].names[2]
        o = o.reconcile()
        self.assertEqual('nonlocal b,c,c', o.src)
        o.verify()

        o = FST("f'a{a}b{b}c{c}'", 'exec').mark()
        o.a.body[0].value.values[0] = o.a.body[0].value.values[2]
        o.a.body[0].value.values[1] = o.a.body[0].value.values[3]
        o.a.body[0].value.values[2] = o.a.body[0].value.values[4]
        o.a.body[0].value.values[3] = o.a.body[0].value.values[5]
        o = o.reconcile()
        self.assertEqual("f'b{b}c{c}c{c}'", o.src)
        o.verify()

        if not PYLT12:
            o = FST('def f[T,U,V](): pass', 'exec').mark()
            o.a.body[0].type_params[0] = o.a.body[0].type_params[1]
            o.a.body[0].type_params[1] = o.a.body[0].type_params[2]
            o = o.reconcile()
            self.assertEqual('def f[U,V,V](): pass', o.src)
            o.verify()

            o = FST('async def f[T,U,V](): pass', 'exec').mark()
            o.a.body[0].type_params[0] = o.a.body[0].type_params[1]
            o.a.body[0].type_params[1] = o.a.body[0].type_params[2]
            o = o.reconcile()
            self.assertEqual('async def f[U,V,V](): pass', o.src)
            o.verify()

            o = FST('class cls[T,U,V]: pass', 'exec').mark()
            o.a.body[0].type_params[0] = o.a.body[0].type_params[1]
            o.a.body[0].type_params[1] = o.a.body[0].type_params[2]
            o = o.reconcile()
            self.assertEqual('class cls[U,V,V]: pass', o.src)
            o.verify()

            o = FST('type t[T,U,V] = ...', 'exec').mark()
            o.a.body[0].type_params[0] = o.a.body[0].type_params[1]
            o.a.body[0].type_params[1] = o.a.body[0].type_params[2]
            o = o.reconcile()
            self.assertEqual('type t[U,V,V] = ...', o.src)
            o.verify()

        if not PYLT14:
            o = FST("t'a{a}b{b}c{c}'", 'exec').mark()
            o.a.body[0].value.values[0] = o.a.body[0].value.values[2]
            o.a.body[0].value.values[1] = o.a.body[0].value.values[3]
            o.a.body[0].value.values[2] = o.a.body[0].value.values[4]
            o.a.body[0].value.values[3] = o.a.body[0].value.values[5]
            o = o.reconcile()
            self.assertEqual("t'b{b}c{c}c{c}'", o.src)
            o.verify()

        # non-slice lists

        o = FST('def f(a=1,b=2,/,c=3,d=4,*,e=5,f=6): pass', 'exec').mark()
        o.a.body[0].args.posonlyargs[0] = o.a.body[0].args.posonlyargs[1]
        o.a.body[0].args.defaults[0] = o.a.body[0].args.defaults[1]
        o.a.body[0].args.args[0] = o.a.body[0].args.args[1]
        o.a.body[0].args.defaults[2] = o.a.body[0].args.defaults[3]
        o.a.body[0].args.kwonlyargs[0] = o.a.body[0].args.kwonlyargs[1]
        o.a.body[0].args.kw_defaults[0] = o.a.body[0].args.kw_defaults[1]
        o = o.reconcile()
        self.assertEqual('def f(b=2,b=2,/,d=4,d=4,*,f=6,f=6): pass', o.src)
        o.verify()

        o = FST('case cls(a=1,b=2,c=3): pass', 'match_case').mark()
        o.a.pattern.kwd_attrs[0] = o.a.pattern.kwd_attrs[1]
        o.a.pattern.kwd_patterns[0] = o.a.pattern.kwd_patterns[1]
        o.a.pattern.kwd_attrs[1] = o.a.pattern.kwd_attrs[2]
        o.a.pattern.kwd_patterns[1] = o.a.pattern.kwd_patterns[2]
        o = o.reconcile()
        self.assertEqual('case cls(b=2,c=3,c=3): pass', o.src)
        o.verify()

    def test_ast_accessors(self):
        def test(f, field, put, expect, src=None):
            got = getattr(f, field)

            if expect is None:
                self.assertEqual(str(got) if isinstance(got, fstview) else got, src)  # fstview for kwd_attrs

            else:
                self.assertIsInstance(got, expect)

                if src is not None:
                    if expect is FST:
                        self.assertEqual(src, got.src)

                    else:
                        try:
                            self.assertEqual(src, got.copy().src)
                        except NotImplementedError:  # TODO: because not all slices are implemented prescribed
                            self.assertEqual(src, str(got))

                        except ValueError as exc:
                            if not str(exc).startswith('cannot get slice from'):
                                raise

                            self.assertEqual(src, got[0].copy().src)

            try:
                setattr(f, field, put)

            except NotImplementedError:
                with FST.options(raw=True):
                    try:
                        setattr(f, field, put)

                    except ValueError as exc:
                        if not str(exc).startswith('cannot specify a field'):
                            raise

                        getattr(f, field)[0] = put

            except (NodeError, ValueError) as exc:
                if not str(exc).startswith('cannot put slice to'):
                    raise

                getattr(f, field)[0] = put

            f.verify()

            return f

        self.assertEqual('a', test(FST('i\nj', 'exec'), 'body', 'a', fstview, 'i\nj').src)
        self.assertEqual('a', test(FST('i;j', 'single'), 'body', 'a', fstview, 'i;j').src)
        self.assertEqual('a', test(FST('i', 'eval'), 'body', 'a', FST, 'i').src)

        f = FST('@deco\ndef func(args) -> ret: pass')
        self.assertEqual('@deco\ndef func(args) -> ret: pass', test(f, 'decorator_list', '@deco', fstview,
                                                                    '@deco').src)
        self.assertEqual('@deco\ndef new(args) -> ret: pass', test(f, 'name', 'new', None, 'func').src)
        self.assertEqual('@deco\ndef new(nargs) -> ret: pass', test(f, 'args', 'nargs', FST, 'args').src)
        self.assertEqual('@deco\ndef new(nargs) -> int: pass', test(f, 'returns', 'int', FST, 'ret').src)
        self.assertEqual('@deco\ndef new(nargs) -> int:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('@deco\nasync def func(args) -> ret: pass')
        self.assertEqual('@deco\nasync def func(args) -> ret: pass', test(f, 'decorator_list', '@deco', fstview,
                                                                          '@deco').src)
        self.assertEqual('@deco\nasync def new(args) -> ret: pass', test(f, 'name', 'new', None, 'func').src)
        self.assertEqual('@deco\nasync def new(nargs) -> ret: pass', test(f, 'args', 'nargs', FST, 'args').src)
        self.assertEqual('@deco\nasync def new(nargs) -> int: pass', test(f, 'returns', 'int', FST, 'ret').src)
        self.assertEqual('@deco\nasync def new(nargs) -> int:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('@deco\nclass cls(base, meta=other): pass')
        self.assertEqual('@deco\nclass cls(base, meta=other): pass', test(f, 'decorator_list', '@deco', fstview,
                                                                          '@deco').src)
        self.assertEqual('@deco\nclass new(base, meta=other): pass', test(f, 'name', 'new', None, 'cls').src)
        self.assertEqual('@deco\nclass new(bass, meta=other): pass', test(f, 'bases', 'bass,', fstview, '(base,)').src)
        self.assertEqual('@deco\nclass new(bass, moto=some): pass', test(f, 'keywords', 'moto=some', fstview,
                                                                         'meta=other').src)
        self.assertEqual('@deco\nclass new(bass, moto=some):\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        self.assertEqual('return yup', test(FST('return yes'), 'value', 'yup', FST, 'yes').src)

        self.assertEqual('del zzz', test(FST('del a, b'), 'targets', 'zzz', fstview, 'a, b').src)

        self.assertEqual('zzz = c', test(FST('a, b = c'), 'targets', 'zzz', fstview, 'a, b =').src)
        self.assertEqual('a, b = zzz', test(FST('a, b = c'), 'value', 'zzz', FST, 'c').src)

        f = FST('a += b')
        self.assertEqual('new += b', test(f, 'target', 'new', FST, 'a').src)
        self.assertEqual('new >>= b', test(f, 'op', '>>', FST, '+').src)
        self.assertEqual('new >>= zzz', test(f, 'value', 'zzz', FST, 'b').src)

        f = FST('a: int = v')
        self.assertEqual('new: int = v', test(f, 'target', 'new', FST, 'a').src)
        self.assertEqual('new: int = zzz', test(f, 'value', 'zzz', FST, 'v').src)
        self.assertEqual('new: str = zzz', test(f, 'annotation', 'str', FST, 'int').src)
        self.assertEqual('(new): str = zzz', test(f, 'simple', 0, None, 1).src)

        f = FST('for a, b in c: pass\nelse: pass')
        self.assertEqual('for new in c: pass\nelse: pass', test(f, 'target', 'new', FST, 'a, b').src)
        self.assertEqual('for new in zzz: pass\nelse: pass', test(f, 'iter', 'zzz', FST, 'c').src)
        self.assertEqual('for new in zzz:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('for new in zzz:\n    return\nelse:\n    continue', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('async for a, b in c: pass\nelse: pass')
        self.assertEqual('async for new in c: pass\nelse: pass', test(f, 'target', 'new', FST, 'a, b').src)
        self.assertEqual('async for new in zzz: pass\nelse: pass', test(f, 'iter', 'zzz', FST, 'c').src)
        self.assertEqual('async for new in zzz:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('async for new in zzz:\n    return\nelse:\n    continue', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('while a: pass\nelse: pass')
        self.assertEqual('while new: pass\nelse: pass', test(f, 'test', 'new', FST, 'a').src)
        self.assertEqual('while new:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('while new:\n    return\nelse:\n    continue', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('if a: pass\nelse: pass')
        self.assertEqual('if new: pass\nelse: pass', test(f, 'test', 'new', FST, 'a').src)
        self.assertEqual('if new:\n    return\nelse: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('if new:\n    return\nelse:\n    continue', test(f, 'orelse', 'continue', fstview, 'pass').src)

        f = FST('with a as b: pass')
        self.assertEqual('with old as new: pass', test(f, 'items', 'old as new', fstview, 'a as b').src)
        self.assertEqual('with old as new:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('async with a as b: pass')
        self.assertEqual('async with old as new: pass', test(f, 'items', 'old as new', fstview, 'a as b').src)
        self.assertEqual('async with old as new:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('match a:\n    case _: pass')
        self.assertEqual('match new:\n    case _: pass', test(f, 'subject', 'new', FST, 'a').src)
        self.assertEqual('match new:\n    case 1: return', test(f, 'cases', 'case 1: return', fstview, 'case _: pass').src)

        f = FST('raise exc from cause')
        self.assertEqual('raise e from cause', test(f, 'exc', 'e', FST, 'exc').src)
        self.assertEqual('raise e from c', test(f, 'cause', 'c', FST, 'cause').src)

        f = FST('try: pass\nexcept: pass\nelse: pass\nfinally: pass')
        self.assertEqual('try:\n    return\nexcept: pass\nelse: pass\nfinally: pass', test(f, 'body', 'return', fstview, 'pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse: pass\nfinally: pass', test(f, 'handlers', 'except Exception as e: continue', fstview, 'except: pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse:\n    break\nfinally: pass', test(f, 'orelse', 'break', fstview, 'pass').src)
        self.assertEqual('try:\n    return\nexcept Exception as e: continue\nelse:\n    break\nfinally:\n    f()', test(f, 'finalbody', 'f()', fstview, 'pass').src)

        f = FST('assert test, "msg"')
        self.assertEqual('assert toast, "msg"', test(f, 'test', 'toast', FST, 'test').src)
        self.assertEqual('assert toast, "sheep"', test(f, 'msg', '"sheep"', FST, '"msg"').src)

        self.assertEqual('import a, b, c', test(FST('import x, y'), 'names', 'a, b, c', fstview, 'x, y').src)

        f = FST('from .module import x, y')
        self.assertEqual('from .new import x, y', test(f, 'module', 'new', None, 'module').src)
        self.assertEqual('from .new import a, b, c', test(f, 'names', 'a, b, c', fstview, 'x, y').src)
        self.assertEqual('from ...new import a, b, c', test(f, 'level', 3, None, 1).src)

        self.assertEqual('global a, b, c', test(FST('global x, y'), 'names', 'a, b, c', fstview, 'x, y').src)

        self.assertEqual('nonlocal a, b, c', test(FST('nonlocal x, y'), 'names', 'a, b, c', fstview, 'x, y').src)

        self.assertEqual('new', test(FST('v', Expr), 'value', 'new', FST, 'v').src)

        f = FST('a and b and c')
        self.assertEqual('<<BoolOp ROOT 0,0..0,13>.values [<Name 0,0..0,1>, <Name 0,6..0,7>, <Name 0,12..0,13>]>', str(f.values))
        self.assertEqual('a or b or c', test(f, 'op', 'or', FST, 'and').src)

        f = FST('(a := b)')
        self.assertEqual('(new := b)', test(f, 'target', 'new', FST, 'a').src)
        self.assertEqual('(new := old)', test(f, 'value', 'old', FST, 'b').src)

        f = FST('a + b')
        self.assertEqual('new + b', test(f, 'left', 'new', FST, 'a').src)
        self.assertEqual('new >> b', test(f, 'op', '>>', FST, '+').src)
        self.assertEqual('new >> newtoo', test(f, 'right', 'newtoo', FST, 'b').src)

        f = FST('-a')
        self.assertEqual('not a', test(f, 'op', 'not', FST, '-').src)
        self.assertEqual('not new', test(f, 'operand', 'new', FST, 'a').src)

        f = FST('lambda a: None')
        self.assertEqual('lambda args: None', test(f, 'args', 'args', FST, 'a').src)
        self.assertEqual('lambda args: new', test(f, 'body', 'new', FST, 'None').src)

        f = FST('a if b else c')
        self.assertEqual('new if b else c', test(f, 'body', 'new', FST, 'a').src)
        self.assertEqual('new if test else c', test(f, 'test', 'test', FST, 'b').src)
        self.assertEqual('new if test else blah', test(f, 'orelse', 'blah', FST, 'c').src)

        f = FST('{a: b}')
        self.assertEqual('<<Dict ROOT 0,0..0,6>.keys [<Name 0,1..0,2>]>', str(f.keys))
        self.assertEqual('<<Dict ROOT 0,0..0,6>.values [<Name 0,4..0,5>]>', str(f.values))

        self.assertEqual('{{a, b, c}}', test(FST('{x, y}'), 'elts', '{a, b, c}', fstview, '{x, y}').src)
        self.assertEqual('{a, b, c}', test(FST('{x, y}'), 'elts', 'a, b, c', fstview, '{x, y}').src)

        f = FST('[i for i in j if i]')
        self.assertEqual('[new for i in j if i]', test(f, 'elt', 'new', FST, 'i').src)
        self.assertEqual('[new async for dog in dogs]', test(f, 'generators', 'async for dog in dogs', fstview,
                                                             'for i in j if i').src)

        f = FST('{i for i in j if i}')
        self.assertEqual('{new for i in j if i}', test(f, 'elt', 'new', FST, 'i').src)
        self.assertEqual('{new async for dog in dogs}', test(f, 'generators', 'async for dog in dogs', fstview,
                                                             'for i in j if i').src)

        f = FST('{i: i for i in j if i}')
        self.assertEqual('{new: i for i in j if i}', test(f, 'key', 'new', FST, 'i').src)
        self.assertEqual('{new: old for i in j if i}', test(f, 'value', 'old', FST, 'i').src)
        self.assertEqual('{new: old async for dog in dogs}', test(f, 'generators', 'async for dog in dogs', fstview,
                                                             'for i in j if i').src)

        f = FST('(i for i in j if i)')
        self.assertEqual('(new for i in j if i)', test(f, 'elt', 'new', FST, 'i').src)
        self.assertEqual('(new async for dog in dogs)', test(f, 'generators', 'async for dog in dogs', fstview,
                                                             'for i in j if i').src)

        self.assertEqual('await yup', test(FST('await yes'), 'value', 'yup', FST, 'yes').src)

        self.assertEqual('yield yup', test(FST('yield yes'), 'value', 'yup', FST, 'yes').src)

        self.assertEqual('yield from yup', test(FST('yield from yes'), 'value', 'yup', FST, 'yes').src)

        f = FST('a < b < c')
        self.assertEqual('new < b < c', test(f, 'left', 'new', FST, 'a').src)
        self.assertEqual('<<Compare ROOT 0,0..0,11>.ops [<Lt 0,4..0,5>, <Lt 0,8..0,9>]>', str(f.ops))
        self.assertEqual('<<Compare ROOT 0,0..0,11>.comparators [<Name 0,6..0,7>, <Name 0,10..0,11>]>', str(f.comparators))

        f = FST('call(arg, kw=blah)')
        self.assertEqual('call(a, b, kw=blah)', test(f, 'args', 'a, b', fstview, '(arg,)').src)
        self.assertEqual('call(a, b, kw1=bloh, kws=hmm)', test(f, 'keywords', 'kw1=bloh, kws=hmm', fstview,
                                                               'kw=blah').src)

        f = FST('u"a"')
        self.assertEqual('u', f.kind)
        self.assertEqual("'new'", test(f, 'value', 'new', None, 'a').src)
        self.assertEqual("u'new'", test(f, 'kind', 'u', None, None).src)

        f = FST('a.b')
        self.assertEqual('new.b', test(f, 'value', 'new', FST, 'a').src)
        self.assertEqual('new.dog', test(f, 'attr', 'dog', None, 'b').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('a[b]')
        self.assertEqual('new[b]', test(f, 'value', 'new', FST, 'a').src)
        self.assertEqual('new[dog]', test(f, 'slice', 'dog', FST, 'b').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('*a')
        self.assertEqual('*new', test(f, 'value', 'new', FST, 'a').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('name')
        self.assertEqual('new', test(f, 'id', 'new', None, 'name').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('[a, b]')
        self.assertEqual('[[x, y, z]]', test(f, 'elts', '[x, y, z]', fstview, '[a, b]').src)
        self.assertIsInstance(f.ctx.a, Load)
        self.assertEqual('[x, y, z]', test(f, 'elts', 'x, y, z', fstview, '[[x, y, z]]').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('(a, b)')
        self.assertEqual('((x, y, z),)', test(f, 'elts', '(x, y, z)', fstview, '(a, b)').src)
        self.assertIsInstance(f.ctx.a, Load)
        self.assertEqual('(x, y, z)', test(f, 'elts', 'x, y, z', fstview, '((x, y, z),)').src)
        self.assertIsInstance(f.ctx.a, Load)

        f = FST('a:b:c')
        self.assertEqual('low:b:c', test(f, 'lower', 'low', FST, 'a').src)
        self.assertEqual('low:up:c', test(f, 'upper', 'up', FST, 'b').src)
        self.assertEqual('low:up:st', test(f, 'step', 'st', FST, 'c').src)

        f = FST('for i in j if i')
        self.assertEqual('for new in j if i', test(f, 'target', 'new', FST, 'i').src)
        self.assertEqual('for new in blah if i', test(f, 'iter', 'blah', FST, 'j').src)
        self.assertEqual('for new in blah if new', test(f, 'ifs', 'if new', fstview,
                                                        'if i').src)
        self.assertEqual('async for new in blah if new', test(f, 'is_async', 1, None, 0).src)

        f = FST('except Exception as exc: pass')
        self.assertEqual('except ValueError as exc: pass', test(f, 'type', 'ValueError', FST, 'Exception').src)
        self.assertEqual('except ValueError as blah: pass', test(f, 'name', 'blah', None, 'exc').src)
        self.assertEqual('except ValueError as blah:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        f = FST('a, /, b=c, *d, e=f, **g')
        self.assertEqual('new, /, b=c, *d, e=f, **g', test(f, 'posonlyargs', 'new', fstview, 'a').src)
        self.assertEqual('new, /, blah=c, *d, e=f, **g', test(f, 'args', 'blah', fstview, 'b').src)
        self.assertEqual('new, /, blah=cat, *d, e=f, **g', test(f, 'defaults', 'cat', fstview, 'c').src)
        self.assertEqual('new, /, blah=cat, *va, e=f, **g', test(f, 'vararg', 'va', FST, 'd').src)
        self.assertEqual('new, /, blah=cat, *va, lemur=f, **g', test(f, 'kwonlyargs', 'lemur', fstview, 'e').src)
        self.assertEqual('new, /, blah=cat, *va, lemur=raisin, **g', test(f, 'kw_defaults', 'raisin', fstview, 'f').src)
        self.assertEqual('new, /, blah=cat, *va, lemur=raisin, **splat', test(f, 'kwarg', 'splat', FST, 'g').src)

        f = FST('a: int', arg)
        self.assertEqual('new: int', test(f, 'arg', 'new', None, 'a').src)
        self.assertEqual('new: list', test(f, 'annotation', 'list', FST, 'int').src)

        f = FST('a=blah', keyword)
        self.assertEqual('new=blah', test(f, 'arg', 'new', None, 'a').src)
        self.assertEqual('new=dog', test(f, 'value', 'dog', FST, 'blah').src)

        f = FST('a as b', alias)
        self.assertEqual('new as b', test(f, 'name', 'new', None, 'a').src)
        self.assertEqual('new as cat', test(f, 'asname', 'cat', None, 'b').src)

        f = FST('a as b', withitem)
        self.assertEqual('new as b', test(f, 'context_expr', 'new', FST, 'a').src)
        self.assertEqual('new as cat', test(f, 'optional_vars', 'cat', FST, 'b').src)

        f = FST('case a if b: pass')
        self.assertEqual('case new if b: pass', test(f, 'pattern', 'new', FST, 'a').src)
        self.assertEqual('case new if old: pass', test(f, 'guard', 'old', FST, 'b').src)
        self.assertEqual('case new if old:\n    return', test(f, 'body', 'return', fstview, 'pass').src)

        self.assertEqual('2', test(FST('1', MatchValue), 'value', '2', FST, '1').src)

        self.assertEqual('True', test(FST('False', MatchSingleton), 'value', True, None, False).src)

        self.assertEqual('[a, b, c]', test(FST('[x, y]', MatchSequence), 'patterns', 'a, b, c', fstview, '[x, y]').src)

        f = FST('{1: a, **b}', MatchMapping)
        self.assertEqual('{2: a, **b}', test(f, 'keys', '2', fstview, '1').src)
        # self.assertEqual('{2: new, **b}', test(f, None, 'new', fstview,
        #                                        '<<MatchMapping ROOT 0,0..0,11>.patterns [<MatchAs 0,4..0,5>]>').src)
        self.assertEqual('{2: a, **rest}', test(f, 'rest', 'rest', None, 'b').src)

        f = FST('cls(a, b=c)', MatchClass)
        self.assertEqual('glob(a, b=c)', test(f, 'cls', 'glob', FST, 'cls').src)
        self.assertEqual('glob(new, b=c)', test(f, 'patterns', 'new', fstview, '[a]').src)
        self.assertEqual('glob(new, kw=c)', test(f, 'kwd_attrs', 'kw', None,
                                                "<<MatchClass ROOT 0,0..0,14>.kwd_attrs ['b']>").src)
        self.assertEqual('glob(new, kw=blah)', test(f, 'kwd_patterns', 'blah', fstview, 'c').src)

        self.assertEqual('*new', test(FST('*star', MatchStar), 'name', 'new', None, 'star').src)

        f = FST('a as b', MatchAs)
        self.assertEqual('new as b', test(f, 'pattern', 'new', FST, 'a').src)
        self.assertEqual('new as grog', test(f, 'name', 'grog', None, 'b').src)

        self.assertEqual('1 | 2 | 3', test(FST('a.b | c.d', MatchOr), 'patterns', '1 | 2 | 3', fstview, 'a.b | c.d').src)

        if not PYLT11:
            f = FST('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass')
            self.assertEqual('try:\n    return\nexcept* Exception: pass\nelse: pass\nfinally: pass', test(f, 'body', 'return', fstview, 'pass').src)
            self.assertEqual('try:\n    return\nexcept* Exception as e: continue\nelse: pass\nfinally: pass', test(f, 'handlers', 'except* Exception as e: continue', fstview, 'except* Exception: pass').src)
            self.assertEqual('try:\n    return\nexcept* Exception as e: continue\nelse:\n    break\nfinally: pass', test(f, 'orelse', 'break', fstview, 'pass').src)
            self.assertEqual('try:\n    return\nexcept* Exception as e: continue\nelse:\n    break\nfinally:\n    f()', test(f, 'finalbody', 'f()', fstview, 'pass').src)

        if not PYLT12:
            self.assertEqual('def func[U](): pass', test(FST('def func[T](): pass'), 'type_params', 'U', fstview, 'T').src)

            self.assertEqual('async def func[U](): pass', test(FST('async def func[T](): pass'), 'type_params', 'U', fstview, 'T').src)

            self.assertEqual('class cls[U]: pass', test(FST('class cls[T]: pass'), 'type_params', 'U', fstview, 'T').src)

            f = FST('type t[T] = v')
            self.assertEqual('type new[T] = v', test(f, 'name', 'new', FST, 't').src)
            self.assertEqual('type new[U] = v', test(f, 'type_params', 'U', fstview, 'T').src)
            self.assertEqual('type new[U] = zzz', test(f, 'value', 'zzz', FST, 'v').src)

            # these are complicated...

            # (FormattedValue, 'value'):            _get_one_FormattedValue_value, # expr
            # (FormattedValue, 'conversion'):       _get_one_conversion, # int
            # (FormattedValue, 'format_spec'):      _get_one_format_spec, # expr?  - no location on py < 3.12

            self.assertEqual('f"new"', test(FST('f"{a}"'), 'values', 'new', fstview,
                                            '<<JoinedStr ROOT 0,0..0,6>.values [<FormattedValue 0,2..0,5>]>').src)  # TODO: the result of this put is incorrect because it is not implemented yet

            self.assertEqual('new', test(FST('T', TypeVar), 'name', 'new', None, 'T').src)
            self.assertEqual('T: str', test(FST('T: int', TypeVar), 'bound', 'str', FST, 'int').src)

            self.assertEqual('*new', test(FST('*T', TypeVarTuple), 'name', 'new', None, 'T').src)

            self.assertEqual('**new', test(FST('**T', ParamSpec), 'name', 'new', None, 'T').src)

        else:
            pass

            # (FormattedValue, 'value'):            _get_one_FormattedValue_value, # expr
            # (FormattedValue, 'conversion'):       _get_one_conversion, # int
            # (FormattedValue, 'format_spec'):      _get_one_format_spec, # expr?  - no location on py < 3.12

            self.assertEqual('new', test(FST('f"{a}"'), 'values', 'new', fstview,
                                         '<<JoinedStr ROOT 0,0..0,6>.values [<FormattedValue 0,0..0,6>]>').src)  # TODO: the result of this put is incorrect because it is not implemented yet, and will probably not be implemented for py < 3.12

        if not PYLT13:
            self.assertEqual('T = str', test(FST('T = int', TypeVar), 'default_value', 'str', FST, 'int').src)
            self.assertEqual('*T = str', test(FST('*T = int', TypeVarTuple), 'default_value', 'str', FST, 'int').src)
            self.assertEqual('**T = str', test(FST('**T = int', ParamSpec), 'default_value', 'str', FST, 'int').src)

        if not PYLT14:
            # (Interpolation, 'value'):             _get_one_default, # expr
            # (Interpolation, 'str'):               _get_one_constant, # constant
            # (Interpolation, 'conversion'):        _get_one_conversion, # int
            # (Interpolation, 'format_spec'):       _get_one_format_spec, # expr?  - no location on py < 3.12

            self.assertEqual('t"new"', test(FST('t"{a}"'), 'values', 'new', fstview,
                                            '<<TemplateStr ROOT 0,0..0,6>.values [<Interpolation 0,2..0,5>]>').src)  # TODO: the result of this put is incorrect because it is not implemented yet

    def test_ast_accessors_virtual_field__all(self):
        # Dict

        f = FST('{a: b, c: d, e: f}')
        self.assertEqual('<<Dict ROOT 0,0..0,18>._all {<Name 0,1..0,2>: <Name 0,4..0,5>, <Name 0,7..0,8>: <Name 0,10..0,11>, <Name 0,13..0,14>: <Name 0,16..0,17>}>', str(f._all))
        self.assertEqual('{a: b}', f._all[:1].copy().src)
        self.assertEqual('{e: f}', f._all[-1:].copy().src)
        self.assertEqual('{}', f._all[0:0].copy().src)
        self.assertEqual('<<Dict ROOT 0,0..0,18>._all[1:2] {<Name 0,7..0,8>: <Name 0,10..0,11>}>', str(f._all[1]))

        self.assertRaises(NodeError, f._all.__setitem__, 1, 'x')

        f._all[1] = None

        self.assertEqual('{a: b, e: f}', f.src)

        f._all = '{x: y}'

        self.assertEqual('{x: y}', f.src)

        del f._all

        self.assertEqual('{}', f.src)

        # MatchMapping

        f = FST('{1: a, 2: b, **c}', pattern)
        self.assertEqual('<<MatchMapping ROOT 0,0..0,17>._all {<Constant 0,1..0,2>: <MatchAs 0,4..0,5>, <Constant 0,7..0,8>: <MatchAs 0,10..0,11>, **c}>', str(f._all))
        self.assertEqual('{1: a}', f._all[:1].copy().src)
        self.assertEqual('{**c}', f._all[-1:].copy().src)
        self.assertEqual('{2: b, **c}', f._all[-2:].copy().src)
        self.assertEqual('{}', f._all[0:0].copy().src)

        self.assertEqual('<<MatchMapping ROOT 0,0..0,17>._all[1:2] {<Constant 0,7..0,8>: <MatchAs 0,10..0,11>}>', str(f._all[1:2]))
        # self.assertRaises(ValueError, lambda: f._all[0])
        self.assertRaises(NodeError, f._all.__setitem__, 1, 'x')

        f._all[1] = None

        self.assertEqual('{1: a, **c}', f.src)

        f._all = '{1: y}'

        self.assertEqual('{1: y}', f.src)

        del f._all

        self.assertEqual('{}', f.src)

        # Compare

        f = FST('a < b > c')
        self.assertEqual('<<Compare ROOT 0,0..0,9>._all <Name 0,0..0,1> < <Name 0,4..0,5> > <Name 0,8..0,9>>', str(f._all))
        self.assertEqual('a', f._all[:1].copy().src)
        self.assertEqual('c', f._all[-1:].copy().src)
        self.assertEqual('a < b', f._all[:2].copy().src)
        self.assertEqual('b > c', f._all[-2:].copy().src)

        self.assertRaises(ValueError, f._all[0:0].copy)

        self.assertEqual('b', f._all[1].src)

        f._all[1] = 'x'

        self.assertEqual('a < x > c', f.src)

        f._all[1] = None

        self.assertEqual('a > c', f.src)

        self.assertEqual('<<Compare ROOT 0,0..0,14>._all[1:3] <Name 0,4..0,5> == <Name 0,9..0,10>>', repr(FST('a < b == c > d')._all[1:3]))

        f._all = 'x != y'

        self.assertEqual('x != y', f.src)

        def delitem(): del f._all
        self.assertRaises(ValueError, delitem)

        # error

        f = FST('a')

        self.assertRaises(AttributeError, lambda: f._all)

        def setitem(): f._all = '[]'
        self.assertRaises(NodeError, setitem)

        def delitem(): del f._all
        self.assertRaises(NodeError, delitem)

    def test_ast_accessors_virtual_field__body(self):
        f = FST('"""doc"""\na\nb')
        self.assertEqual('a\nb', f._body.copy().src)
        self.assertEqual('a', f._body[0].src)
        self.assertEqual('b', f._body[1].src)
        self.assertRaises(IndexError, lambda: f._body[2])
        self.assertEqual('b', f._body[-1].src)
        self.assertEqual('a', f._body[-2].src)
        self.assertRaises(IndexError, lambda: f._body[-3])

        del f._body
        self.assertEqual('"""doc"""', f.src)

        f._body = 'x\ny'
        self.assertEqual('"""doc"""\nx\ny', f.src)

        self.assertEqual(0, len(fstview_dummy(f, 'invalid')))

        self.assertEqual('b', FST('if 1:\n  a\n  b\n  c')._body[1].src)

        # error

        f = FST('a')

        self.assertRaises(AttributeError, lambda: f._body)

        def setitem(): f._body = '[]'
        self.assertRaises(NodeError, setitem)

        def delitem(): del f._body
        self.assertRaises(NodeError, delitem)

    def test_ast_accessors_dummy(self):
        if PYLT12:
            self.assertIsInstance(FST('def f(): pass').type_params, fstview_dummy)
            self.assertIsInstance(FST('async def f(): pass').type_params, fstview_dummy)
            self.assertIsInstance(FST('class cls: pass').type_params, fstview_dummy)

            f = FST('class cls: pass')
            del f.type_params
            f.type_params = None
            self.assertRaises(RuntimeError, setattr, f, 'type_params', True)

            self.assertEqual(0, len(f.type_params))

        if PYGE12 and PYLT13:
            self.assertIsNone(FST('T', 'TypeVar').default_value)
            self.assertIsNone(FST('*U', 'TypeVarTuple').default_value)
            self.assertIsNone(FST('**V', 'ParamSpec').default_value)

            f = FST('T', 'TypeVar')
            del f.default_value
            f.default_value = None
            self.assertRaises(RuntimeError, setattr, f, 'default_value', True)

    def test_parents_and_their_is_type_predicates(self):
        fst = parse('''
match a:
    case 1:
        try:
            pass
        except Exception:
            class cls:
                def f():
                    return [lambda: None for i in ()]
            '''.strip())

        f = fst.body[0].cases[0].body[0].handlers[0].body[0].body[0].body[0].value.elt.body.f
        self.assertEqual(f.src, 'None')

        self.assertIsInstance((f := f.parent_scope()).a, Lambda)
        self.assertTrue(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertFalse(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtlike)
        self.assertFalse(f.is_stmtlike_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_scope()).a, ListComp)
        self.assertTrue(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertFalse(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtlike)
        self.assertFalse(f.is_stmtlike_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_named_scope()).a, FunctionDef)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtlike)
        self.assertTrue(f.is_stmtlike_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_named_scope()).a, ClassDef)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmtlike)
        self.assertTrue(f.is_stmtlike_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmtlike()).a, ExceptHandler)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtlike)
        self.assertTrue(f.is_stmtlike_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmt()).a, Try)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtlike)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmtlike()).a, match_case)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtlike)
        self.assertTrue(f.is_stmtlike_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_block()).a, Match)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtlike)
        self.assertTrue(f.is_stmtlike_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_scope()).a, Module)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtlike)
        self.assertTrue(f.is_stmtlike_or_mod)
        self.assertTrue(f.is_mod)

        self.assertIs((f := FST('i = 1')).parent_stmt(self_=True), f)
        self.assertIs((f := FST('except: pass')).parent_stmtlike(self_=True), f)
        self.assertIs((f := FST('if 1: pass')).parent_block(self_=True), f)
        self.assertIs((f := FST('class cls: pass')).parent_scope(self_=True), f)
        self.assertIs((f := FST('def f(): pass')).parent_named_scope(self_=True), f)
        self.assertIs((f := FST('a as b', 'withitem')).parent_non_expr(self_=True), f)
        self.assertIs((f := FST('a as b', 'pattern')).parent_pattern(self_=True), f)

        # f and t-strings

        f = FST('f"{1}"')

        self.assertTrue(f.is_ftstr)
        self.assertTrue(f.values[0].is_ftstr_fmt)
        self.assertIs(f.values[0].value.parent_ftstr(), f)
        self.assertIs(f.parent_ftstr(self_=True), f)

        if PYGE14:
            f = FST('t"{1}"')

            self.assertTrue(f.is_ftstr)
            self.assertTrue(f.values[0].is_ftstr_fmt)
            self.assertIs(f.values[0].value.parent_ftstr(), f)
            self.assertIs(f.parent_ftstr(self_=True), f)

    def test_misc_predicates(self):
        f = FST('a = (b, c)')
        val = f.value
        elt0 = val.elts[0]
        self.assertTrue(val.is_alive)
        self.assertTrue(elt0.is_alive)
        f.value.elts[0] = 'x'
        self.assertTrue(val.is_alive)
        self.assertTrue(elt0.is_alive)  # yeah, quirk, it changed but is still alive because only its .a changed
        f.value = 'y'
        self.assertTrue(val.is_alive)
        self.assertFalse(elt0.is_alive)  # here it finally died

        self.assertTrue(FST('', 'exec').is_mod)
        self.assertTrue(FST('i = i', 'Assign').is_stmt)
        self.assertTrue(FST('f()', 'Call').is_expr)
        self.assertTrue(FST('i').ctx.is_expr_context)
        self.assertTrue(FST('and', 'And').is_boolop)
        self.assertTrue(FST('+', 'Add').is_operator)
        self.assertTrue(FST('~', 'Invert').is_unaryop)
        self.assertTrue(FST('>', 'Gt').is_cmpop)

        self.assertTrue(FST('def f(): pass').is_def)
        self.assertTrue(FST('async def f(): pass').is_def)
        self.assertTrue(FST('class cls: pass').is_def)
        self.assertTrue(FST('', 'exec').is_def_or_mod)
        self.assertTrue(FST('for _ in _: pass').is_for)
        self.assertTrue(FST('async for _ in _: pass').is_for)
        self.assertTrue(FST('with _: pass').is_with)
        self.assertTrue(FST('async with _: pass').is_with)
        self.assertTrue(FST('try: pass\nexcept: pass').is_try)
        self.assertTrue(FST('import _').is_import)
        self.assertTrue(FST('from . import _').is_import)

        if PYGE11:
            self.assertTrue(FST('try: pass\nexcept* Exception: pass').is_try)

        f = FST('call(a, b=c)', 'exec')
        self.assertTrue(f.is_mod)
        self.assertTrue(f.is_Module)
        self.assertFalse(f.is_Interactive)
        self.assertFalse(f.body[0].is_Name)
        self.assertTrue(f.body[0].is_stmt)
        self.assertTrue(f.body[0].is_Expr)
        self.assertFalse(f.body[0].is_Call)
        self.assertTrue(f.body[0].value.is_Call)
        self.assertFalse(f.body[0].value.is_Name)
        self.assertTrue(f.body[0].value.args[0].is_Name)
        self.assertTrue(f.body[0].value.keywords[0].is_keyword)

        f = FST('case [a, b as c, 3]: pass', 'match_case')
        self.assertTrue(f.is_match_case)
        self.assertFalse(f.is_pattern)
        self.assertTrue(f.pattern.is_pattern)
        self.assertTrue(f.pattern.is_MatchSequence)
        self.assertTrue(f.pattern.patterns[0].is_pattern)
        self.assertTrue(f.pattern.patterns[0].is_MatchAs)
        self.assertFalse(f.pattern.patterns[0].is_MatchSequence)
        self.assertTrue(f.pattern.patterns[1].is_pattern)
        self.assertTrue(f.pattern.patterns[1].is_MatchAs)
        self.assertTrue(f.pattern.patterns[1].pattern.is_MatchAs)
        self.assertTrue(f.pattern.patterns[2].is_pattern)
        self.assertFalse(f.pattern.patterns[2].value.is_pattern)
        self.assertFalse(f.pattern.patterns[2].value.is_stmt)
        self.assertTrue(f.pattern.patterns[2].value.is_expr)
        self.assertTrue(f.pattern.patterns[2].value.is_Constant)

        f = FST('if a if b', '_comprehension_ifs')
        self.assertTrue(f.is__slice)
        self.assertTrue(f.is__comprehension_ifs)
        self.assertFalse(f.is__comprehensions)

        self.assertFalse(FST('a').is_FunctionType)

        f = FST.fromsrc('x = 1  # type: ignore', type_comments=True)
        self.assertTrue(f.type_ignores[0].is_TypeIgnore)
        self.assertTrue(f.type_ignores[0].is_type_ignore)

        self.assertTrue(FST('f"{a}"').values[0].is_FormattedValue)

        if PYGE14:
            self.assertTrue(FST('t"{a}"').values[0].is_Interpolation)

    def test_generated_predicates(self):
        for src, mode in INDIVIDUAL_NODES:
            f = FST(src, mode)

            self.assertTrue(getattr(f, f'is_{mode}'))

            if (base := f.a.__class__.__bases__[0]) is not AST:
                self.assertTrue(getattr(f, f'is_{base.__name__}'))

            for _, not_mode in INDIVIDUAL_NODES:
                if not_mode is not mode:
                    self.assertFalse(getattr(f, f'is_{not_mode}'))

    @unittest.skipUnless(PYLT12, 'only valid for py < 3.12')
    def test_disallow_put_JoinedStr_pylt12(self):
        self.assertRaises(NotImplementedError, FST('i = f"a{b}c"', 'exec').body[0].value.values[1].value.replace, 'z')
        self.assertRaises(NotImplementedError, FST('i = f"a{b}c"').value.values[1].value.replace, 'z')
        self.assertRaises(NotImplementedError, FST('f"a{b}c"').values[1].value.replace, 'z')
        self.assertRaises(NotImplementedError, FST('f"{a}"').values[0].value.replace, 'z')

    def test_precedence(self):
        data = iter(PRECEDENCE_DATA)

        for dst, *attrs in PRECEDENCE_DST_STMTS + PRECEDENCE_DST_EXPRS + PRECEDENCE_SRC_EXPRS:
            for src, *_ in PRECEDENCE_SRC_EXPRS:
                for attr in attrs:
                    d       = dst.copy()
                    s       = src.body[0].value.copy()
                    is_stmt = isinstance(d.a, stmt)
                    f       = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})
                    truth   = next(data)

                    try:
                        (parent := f.parent).put(s, idx := f.pfield.idx, name := f.pfield.name)

                    except Exception as exc:
                        is_exc = True
                        test   = str(exc)

                        if test == 'put inside JoinedStr not implemented on python < 3.12':
                            continue

                    else:
                        is_exc = False
                        test   = f.root.src

                        f.root.verify()

                    self.assertEqual(test, truth)

                    if is_exc:
                        continue

                    # vs. python

                    if attr == 'value' and isinstance(parent.a, NamedExpr):  # we explicitly parenthesize NamedExpr.value because by default we differ from python ast.unparse() and don't do this normally
                        test = parent.put(src.body[0].value.copy().par(), idx, name, pars=True).root.src

                    d            = dst.copy()
                    s            = src.body[0].value.copy()
                    f            = eval(f'd.{attr}' if is_stmt else f'd.body[0].value.{attr}', {'d': d})
                    is_unpar_tup = False if is_stmt else (d.body[0].value.is_parenthesized_tuple() is False)

                    if PYLT11 and isinstance(s.a, Tuple) and isinstance(d.a, (Assign, For, AsyncFor)):  # py 3.10 parenthesizes target tuples, we do not normally so we do it here explicitly for the compare
                        test = parent.put(src.body[0].value.copy().par(), idx, name, pars=True).root.src

                    f.pfield.set(f.parent.a, s.a)

                    py_truth = ast_unparse(f.root.a).replace('lambda :', 'lambda:')

                    if is_unpar_tup:
                        py_truth = py_truth[1:-1]

                    self.assertEqual(test, py_truth)

    def test_is_parenthesized_tuple(self):
        self.assertTrue(parse('(1, 2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,),)').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('((a), b)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(a, (b))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((a), (b))').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('(\n1,2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1\n,2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,\n2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,2\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1)\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1),\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,\n))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,)\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,\n),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,)\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,),\n)').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('((a), b)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(a, (b))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((a), (b))').body[0].value.f.is_parenthesized_tuple())

        self.assertFalse(parse('(1,),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('(1),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((1)),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((1,),),').body[0].value.f.is_parenthesized_tuple())

        self.assertFalse(parse('(a), b').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((a)), b').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('a, (b)').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('a, ((b))').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('(a), (b)').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((a)), ((b))').body[0].value.f.is_parenthesized_tuple())

        self.assertIsNone(parse('[(a), (b)]').body[0].value.f.is_parenthesized_tuple())

    def test_misc(self):
        f = FST('a')
        self.assertRaises(RuntimeError, lambda: f.f)

        from fst.common import shortstr
        self.assertEqual('123', shortstr('123'))
        self.assertEqual('12312312312312312312312 .. [90 chars] .. 23123123123123123123123', shortstr('123' * 30))

        self.assertFalse(FST('f"a{b}"').values[0].is_parenthesizable())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-pars', default=False, action='store_true', help="regenerate parentheses test data")
    parser.add_argument('--regen-put-src', default=False, action='store_true', help="regenerate put src test data")
    parser.add_argument('--regen-precedence', default=False, action='store_true', help="regenerate precedence test data")

    args, _ = parser.parse_known_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT14:
            raise RuntimeError('cannot regenerate on python version < 3.14')

    if args.regen_pars or args.regen_all:
        print('Regenerating parentheses test data...')
        regen_pars_data()

    if args.regen_put_src or args.regen_all:
        print('Regenerating put raw test data...')
        regen_put_src()

    if args.regen_precedence or args.regen_all:
        print('Regenerating precedence test data...')
        regen_precedence_data()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
