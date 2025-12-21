#!/usr/bin/env python

import os
import unittest

from fst import *

from fst.asttypes import *
from fst.common import PYLT11, PYLT12, PYGE11, PYGE12, PYGE13, PYGE14

from support import GetCases, PutCases


DIR_NAME     = os.path.dirname(__file__)
DATA_GET_ONE = GetCases(os.path.join(DIR_NAME, 'data/data_get_one.py'))
DATA_PUT_ONE = PutCases(os.path.join(DIR_NAME, 'data/data_put_one.py'))

REPLACE_EXISTING_ONE_DATA = [
# FunctionDef
("@d\ndef f(a) -> r: pass", 'body[0].decorator_list[0]', {}, "z", "z", "@z\ndef f(a) -> r: pass"),
("@d\ndef f(a) -> r: pass", 'body[0].args', {}, "z", "z", "@d\ndef f(z) -> r: pass"),
("@d\ndef f(a) -> r: pass", 'body[0].returns', {}, "z", "z", "@d\ndef f(a) -> z: pass"),

# AsyncFunctionDef
("@d\nasync def f(a) -> r: pass", 'body[0].decorator_list[0]', {}, "z", "z", "@z\nasync def f(a) -> r: pass"),
("@d\nasync def f(a) -> r: pass", 'body[0].args', {}, "z", "z", "@d\nasync def f(z) -> r: pass"),
("@d\nasync def f(a) -> r: pass", 'body[0].returns', {}, "z", "z", "@d\nasync def f(a) -> z: pass"),

# ClassDef
("@d\nclass c(b, k=v): pass", 'body[0].decorator_list[0]', {}, "z", "z", "@z\nclass c(b, k=v): pass"),
("@d\nclass c(b, k=v): pass", 'body[0].bases[0]', {}, "z", "z", "@d\nclass c(z, k=v): pass"),
("@d\nclass c(b, k=v): pass", 'body[0].keywords[0]', {}, "z=y", "z=y", "@d\nclass c(b, z=y): pass"),

# Return
("return r", 'body[0].value', {}, "z", "z", "return z"),

# Delete
("del d", 'body[0].targets[0]', {}, "z", "z", "del z"),

# Assign
("t = v", 'body[0].targets[0]', {}, "z", "z", "z = v"),
("t = v", 'body[0].value', {}, "z", "z", "t = z"),

# AugAssign
("t += v", 'body[0].target', {}, "z", "z", "z += v"),
("t += v", 'body[0].op', {}, "-", "-", "t -= v"),
("t += v", 'body[0].value', {}, "z", "z", "t += z"),

# AnnAssign
("t: int = v", 'body[0].target', {}, "z", "z", "z: int = v"),
("t: int = v", 'body[0].annotation', {}, "z", "z", "t: z = v"),
("t: int = v", 'body[0].value', {}, "z", "z", "t: int = z"),

# For
("for i in r: pass", 'body[0].target', {}, "z", "z", "for z in r: pass"),
("for i in r: pass", 'body[0].iter', {}, "z", "z", "for i in z: pass"),

# AsyncFor
("async for i in r: pass", 'body[0].target', {}, "z", "z", "async for z in r: pass"),
("async for i in r: pass", 'body[0].iter', {}, "z", "z", "async for i in z: pass"),

# While
("while t: pass", 'body[0].test', {}, "z", "z", "while z: pass"),

# If
("if t: pass", 'body[0].test', {}, "z", "z", "if z: pass"),

# With
("with c: pass", 'body[0].items[0]', {}, "z", "z", "with z: pass"),

# AsyncWith
("async with c: pass", 'body[0].items[0]', {}, "z", "z", "async with z: pass"),

# Match
("match s:\n case 1: pass", 'body[0].subject', {}, "z", "z", "match z:\n case 1: pass"),

# Raise
("raise e from c", 'body[0].exc', {}, "z", "z", "raise z from c"),
("raise e from c", 'body[0].cause', {}, "z", "z", "raise e from z"),

# Try
("try: pass\nexcept Exception as e: pass", 'body[0].handlers[0]', {}, "except: pass", "except: pass", "try: pass\nexcept: pass"),

# TryStar, not available on py3.10 so no TryStar

# Assert
("assert a, m", 'body[0].test', {}, "z", "z", "assert z, m"),
("assert a, m", 'body[0].msg', {}, "z", "z", "assert a, z"),

# Import
("import p as n", 'body[0].names[0]', {}, "z as y", "z as y", "import z as y"),

# ImportFrom
("from g import p as n", 'body[0].names[0]', {}, "z as y", "z as y", "from g import z as y"),

# Expr
("e", 'body[0].value', {}, "z", "z", "z"),

# BoolOp
("a and b", 'body[0].value.values[0]', {}, "z", "z", "z and b"),

# NamedExpr
("(t := v)", 'body[0].value.target', {}, "z", "z", "(z := v)"),
("(t := v)", 'body[0].value.value', {}, "z", "z", "(t := z)"),

# BinOp
("a + b", 'body[0].value.left', {}, "z", "z", "z + b"),
("a + b", 'body[0].value.op', {}, "-", "-", "a - b"),
("a + b", 'body[0].value.right', {}, "z", "z", "a + z"),

# UnaryOp
("+a", 'body[0].value.op', {}, "-", "-", "-a"),
("+a", 'body[0].value.operand', {}, "z", "z", "+z"),

# Lambda
("lambda a: None", 'body[0].value.args', {}, "z", "z", "lambda z: None"),

# IfExp
("a if t else b", 'body[0].value.body', {}, "z", "z", "z if t else b"),
("a if t else b", 'body[0].value.test', {}, "z", "z", "a if z else b"),
("a if t else b", 'body[0].value.orelse', {}, "z", "z", "a if t else z"),

# Dict
("{a: b}", 'body[0].value.keys[0]', {}, "z", "z", "{z: b}"),
("{a: b}", 'body[0].value.values[0]', {}, "z", "z", "{a: z}"),

# Set
("{a}", 'body[0].value.elts[0]', {}, "z", "z", "{z}"),

# ListComp
("[i for i in t]", 'body[0].value.elt', {}, "z", "z", "[z for i in t]"),
("[i for i in t]", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "[i for z in y]"),
("[i for i in t]", 'body[0].value.generators[0]', {}, "async for z in y", "async for z in y", "[i async for z in y]"),
("[i async for i in t]", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "[i for z in y]"),

# SetComp
("{i for i in t}", 'body[0].value.elt', {}, "z", "z", "{z for i in t}"),
("{i for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{i for z in y}"),
("{i for i in t}", 'body[0].value.generators[0]', {}, "async for z in y", "async for z in y", "{i async for z in y}"),
("{i async for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{i for z in y}"),

# DictComp
("{k: v for i in t}", 'body[0].value.key', {}, "z", "z", "{z: v for i in t}"),
("{k: v for i in t}", 'body[0].value.value', {}, "z", "z", "{k: z for i in t}"),
("{k: v for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{k: v for z in y}"),
("{k: v for i in t}", 'body[0].value.generators[0]', {}, "async for z in y", "async for z in y", "{k: v async for z in y}"),
("{k: v async for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{k: v for z in y}"),

# GeneratorExp
("(i for i in t)", 'body[0].value.elt', {}, "z", "z", "(z for i in t)"),
("(i for i in t)", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "(i for z in y)"),
("(i for i in t)", 'body[0].value.generators[0]', {}, "async for z in y", "async for z in y", "(i async for z in y)"),
("(i async for i in t)", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "(i for z in y)"),

# Await
("await w", 'body[0].value.value', {}, "z", "z", "await z"),

# Yield
("yield w", 'body[0].value.value', {}, "z", "z", "yield z"),

# YieldFrom
("yield from w", 'body[0].value.value', {}, "z", "z", "yield from z"),

# Compare
("a < b", 'body[0].value.left', {}, "z", "z", "z < b"),
("a < b", 'body[0].value.ops[0]', {}, ">", ">", "a > b"),
("a < b", 'body[0].value.comparators[0]', {}, "z", "z", "a < z"),

# Call
("c(a, b=c)", 'body[0].value.func', {}, "z", "z", "z(a, b=c)"),
("c(a, b=c)", 'body[0].value.args[0]', {}, "z", "z", "c(z, b=c)"),
("c(a, b=c)", 'body[0].value.keywords[0]', {}, "z=y", "z=y", "c(a, z=y)"),

# FormattedValue, no locations in py3.10
# JoinedStr, no locations in py3.10
# Interpolation, no exist in py3.10
# TemplateStr, no exist in py3.10

# Attribute
# (('value', 'expr'), ('attr', 'identifier'), ('ctx', 'expr_context'))),

# Subscript
("v[s]", 'body[0].value.value', {}, "z", "z", "z[s]"),
("v[s]", 'body[0].value.slice', {}, "z", "z", "v[z]"),

# Starred
("[*s]", 'body[0].value.elts[0].value', {}, "z", "z", "[*z]"),

# List
("[e]", 'body[0].value.elts[0]', {}, "z", "z", "[z]"),

# Tuple
("(e,)", 'body[0].value.elts[0]', {}, "z", "z", "(z,)"),

# Slice
("v[a:b:c]", 'body[0].value.slice.lower', {}, "z", "z", "v[z:b:c]"),
("v[a:b:c]", 'body[0].value.slice.upper', {}, "z", "z", "v[a:z:c]"),
("v[a:b:c]", 'body[0].value.slice.step', {}, "z", "z", "v[a:b:z]"),

# comprehension
("[i for i in t if s]", 'body[0].value.generators[0].target', {}, "z", "z", "[i for z in t if s]"),
("[i for i in t if s]", 'body[0].value.generators[0].iter', {}, "z", "z", "[i for i in z if s]"),
("[i for i in t if s]", 'body[0].value.generators[0].ifs[0]', {}, "z", "z", "[i for i in t if z]"),

# ExceptHandler
("try: pass\nexcept Exception as e: pass", 'body[0].handlers[0].type', {}, "z", "z", "try: pass\nexcept z as e: pass"),

# arguments
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.posonlyargs[0]', {}, "z", "z", "def f(z, /, b=1, *c, d=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.args[0]', {}, "z", "z", "def f(a, /, z=1, *c, d=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.defaults[0]', {}, "z", "z", "def f(a, /, b=z, *c, d=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.vararg', {}, "z", "z", "def f(a, /, b=1, *z, d=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.kwonlyargs[0]', {}, "z", "z", "def f(a, /, b=1, *c, z=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.kw_defaults[0]', {}, "z", "z", "def f(a, /, b=1, *c, d=z, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.kwarg', {}, "z", "z", "def f(a, /, b=1, *c, d=2, **z): pass"),

# arg
("def f(a: int): pass", 'body[0].args.args[0].annotation', {}, "z", "z", "def f(a: z): pass"),

# keyword
("class c(k=v): pass", 'body[0].keywords[0].value', {}, "z", "z", "class c(k=z): pass"),

# alias nothing to test

# withitem
("with c as n: pass", 'body[0].items[0].context_expr', {}, "z", "z", "with z as n: pass"),
("with c as n: pass", 'body[0].items[0].optional_vars', {}, "z", "z", "with c as z: pass"),

# match_case
("match s:\n case 1 as a if g: pass", 'body[0].cases[0].pattern', {}, "'z'", "'z'", "match s:\n case 'z' if g: pass"),
("match s:\n case 1 as a if g: pass", 'body[0].cases[0].guard', {}, "z", "z", "match s:\n case 1 as a if z: pass"),

# MatchValue
("match s:\n case 1: pass", 'body[0].cases[0].pattern.value', {}, "2", "2", "match s:\n case 2: pass"),

# MatchSequence
("match s:\n case 1, 2: pass", 'body[0].cases[0].pattern.patterns[1].value', {}, "3", "3", "match s:\n case 1, 3: pass"),

# MatchMapping
("match s:\n case {1: a, **b}: pass", 'body[0].cases[0].pattern.keys[0]', {}, "2", "2", "match s:\n case {2: a, **b}: pass"),
("match s:\n case {1: a, **b}: pass", 'body[0].cases[0].pattern.patterns[0]', {}, "z", "z", "match s:\n case {1: z, **b}: pass"),

# MatchClass
("match s:\n case c(1, a=2): pass", 'body[0].cases[0].pattern.cls', {}, "z", "z", "match s:\n case z(1, a=2): pass"),
("match s:\n case c(1, a=2): pass", 'body[0].cases[0].pattern.patterns[0].value', {}, "3", "3", "match s:\n case c(3, a=2): pass"),
("match s:\n case c(1, a=2): pass", 'body[0].cases[0].pattern.kwd_patterns[0].value', {}, "3", "3", "match s:\n case c(1, a=3): pass"),

# MatchAs
("match s:\n case 1 as a: pass", 'body[0].cases[0].pattern.pattern', {}, "2", "2", "match s:\n case 2 as a: pass"),

# MatchOr
("match s:\n case 1 | 2: pass", 'body[0].cases[0].pattern.patterns[0].value', {}, "3", "3", "match s:\n case 3 | 2: pass"),
]


def read(fnm):
    with open(fnm) as f:
        return f.read()


def regen_get_one():
    DATA_GET_ONE.generate()
    DATA_GET_ONE.write()


def regen_put_one():
    DATA_PUT_ONE.generate()
    DATA_PUT_ONE.write()


class TestFSTPut(unittest.TestCase):
    def test_get_one_from_data(self):
        for case, rest in DATA_GET_ONE.iterate(True):
            for rest_idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                self.assertEqual(c, r, f'{case.id()}, rest idx = {rest_idx}')

    def test_put_one_from_data(self):
        for case, rest in DATA_PUT_ONE.iterate(True):
            for rest_idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                self.assertEqual(c, r, f'{case.id()}, rest idx = {rest_idx}')

    def test_put_one_raw_from_put_one_data(self):
        from support import _unfmt_code, _make_fst, _clean_options

        for case, rest in DATA_PUT_ONE.iterate(True):
            if case.options.get('raw') is not None or rest[1].startswith('**'):
                continue

            options = {**case.options, 'raw': True}
            f       = _make_fst(case.code, case.attr)
            src     = _unfmt_code(r0 if isinstance(r0 := rest[0], str) else r0[1])

            if src == '**DEL**':
                continue

            try:
                try:
                    f.put(src, case.start, case.stop, field=case.field, **_clean_options(options))  # None if src == '**DEL**' else src

                except ValueError as exc:
                    if str(exc) != 'cannot insert in raw put':
                        raise

                    continue

                except NodeError as exc:  # putting to empty arguments
                    if str(exc) != 'cannot determine location to put to':
                        raise

                    continue

                if options.get('_verify', True):
                    f.root.verify(raise_=True)

            except NotImplementedError:
                continue

            except Exception:
                print(f'{case.id()}')

                raise

            else:
                if f.root.src != rest[1]:
                    raise RuntimeError(f'put raw and put FST src are not identical, {case.id()}\n{f.root.src}\n...\n{rest[1]}')

                # if (root_dump := f.root.dump(out=str)) != rest[2]  # we don't do this because of trailing newline added with statement ops, need to fix
                #     raise RuntimeError(f'put raw and put FST dump are not identical, {key = }, {idx = }\n{root_dump}\n...\n{rest[2]}')

    def test_get_one_constant(self):
        for v in (True, False, None):
            f = FST(f'match a:\n case {v}: pass').cases[0].pattern
            c = f.get('value')
            self.assertIs(c, v)

        for s in ('...', '2', '2.0', '2j', '"str"', 'b"bytes"', 'True', 'False', 'None'):
            f = FST(s)
            self.assertIsInstance(f.a, Constant)

            c = f.get('value')
            self.assertIs(c, f.a.value)

        self.assertEqual(1, FST('i: int', AnnAssign).get('simple'))
        self.assertEqual(0, FST('(i): int', AnnAssign).get('simple'))
        self.assertEqual(0, FST('from a import *', ImportFrom).get('level'))
        self.assertEqual(1, FST('from .a import *', ImportFrom).get('level'))
        self.assertEqual(2, FST('from ..a import *', ImportFrom).get('level'))
        self.assertIs(None, FST('"a"', Constant).get('kind'))
        self.assertEqual('u', FST('u"a"', Constant).get('kind'))
        self.assertEqual(0, FST('for i in j', comprehension).get('is_async'))
        self.assertEqual(1, FST('async for i in j', comprehension).get('is_async'))

        if PYGE14:
            self.assertEqual('blah', FST('t"{blah}"').values[0].get('str'))

    def test_get_one_ctx(self):
        self.assertIsInstance(a := FST('a.b').get('ctx').a, Load)
        a.f.verify()
        self.assertIsInstance(a := FST('a.b = 1').targets[0].get('ctx').a, Store)
        a.f.verify()
        self.assertIsInstance(a := FST('del a.b').targets[0].get('ctx').a, Del)
        a.f.verify()

        self.assertIsInstance(a := FST('a[b]').get('ctx').a, Load)
        a.f.verify()
        self.assertIsInstance(a := FST('a[b] = 1').targets[0].get('ctx').a, Store)
        a.f.verify()
        self.assertIsInstance(a := FST('del a[b]').targets[0].get('ctx').a, Del)
        a.f.verify()

        self.assertIsInstance(a := FST('*a,').elts[0].get('ctx').a, Load)
        a.f.verify()
        self.assertIsInstance(a := FST('*a, = 1').targets[0].elts[0].get('ctx').a, Store)
        a.f.verify()

        self.assertIsInstance(a := FST('a').get('ctx').a, Load)
        a.f.verify()
        self.assertIsInstance(a := FST('a = 1').targets[0].get('ctx').a, Store)
        a.f.verify()
        self.assertIsInstance(a := FST('del a').targets[0].get('ctx').a, Del)
        a.f.verify()

        self.assertIsInstance(a := FST('[a.b]').get('ctx').a, Load)
        a.f.verify()
        self.assertIsInstance(a := FST('[a.b] = 1').targets[0].get('ctx').a, Store)
        a.f.verify()
        self.assertIsInstance(a := FST('del [a.b]').targets[0].get('ctx').a, Del)
        a.f.verify()

        self.assertIsInstance(a := FST('(a.b,)').get('ctx').a, Load)
        a.f.verify()
        self.assertIsInstance(a := FST('(a.b,) = 1').targets[0].get('ctx').a, Store)
        a.f.verify()
        self.assertIsInstance(a := FST('del (a.b,)').targets[0].get('ctx').a, Del)
        a.f.verify()

    def test_get_one_special(self):
        f = FST('a = b', 'exec').body[0]
        self.assertIsInstance(f.targets[0].get('ctx').a, Store)
        self.assertIsInstance(f.value.get('ctx').a, Load)

        f = FST('{a: b}', 'exec').body[0].value
        self.assertRaises(ValueError, f.get, 0)  # cannot get single element from combined field of Dict

        f = FST('match a:\n case {1: b}: pass', 'exec').body[0].cases[0].pattern
        self.assertRaises(ValueError, f.get, 0)  # cannot get single element from combined field of MatchMapping

        f = FST('a < b < c', 'exec').body[0].value
        self.assertEqual('a', f.get(0).src)
        self.assertEqual('b', f.get(1).src)
        self.assertEqual('c', f.get(2).src)
        # self.assertRaises(ValueError, f.get, 0)
        self.assertEqual('a', f.get('left').src)
        self.assertEqual('b', f.get(0, 'comparators').src)
        self.assertEqual('c', f.get(1, 'comparators').src)

        f = FST('def func() -> int: pass', 'exec').body[0]  # identifier
        self.assertEqual('func', f.get('name'))
        self.assertRaises(ValueError, f.get, 'name', cut=True)  # cannot delete FunctionDef.name
        self.assertEqual('int', f.get('returns', cut=True).src)
        self.assertEqual('def func(): pass', f.src)

        f = FST('from .a import *', 'exec').body[0]
        self.assertEqual('a', f.get('module', cut=True))
        self.assertEqual('from . import *', f.src)

        f = FST('from a import *', 'exec').body[0]
        self.assertRaises(ValueError, f.get, 'module', cut=True)

        f = FST('import a as b', 'exec').body[0]
        self.assertEqual('b', f.names[0].get('asname', cut=True))
        self.assertEqual('import a', f.src)

        f = FST('match a:\n case {**a}: pass', 'exec').body[0]
        self.assertEqual('a', f.cases[0].pattern.get('rest', cut=True))
        self.assertEqual('match a:\n case {}: pass', f.src)

        # other

        f = FST('a and b').get('op')
        self.assertIsInstance(f.a, And)
        self.assertEqual('and', f.src)

        f = FST('a or b').get('op')
        self.assertIsInstance(f.a, Or)
        self.assertEqual('or', f.src)

        f = FST('a or b').get('op')
        self.assertIsInstance(f.a, Or)
        self.assertEqual('or', f.src)

        self.assertRaises(ValueError, FST('{a: b}').get, 0)
        self.assertRaises(ValueError, FST('match a:\n case {1: b}: pass').cases[0].pattern.get, 0)

        f = FST('a < b < c')
        self.assertEqual('a', f.get(0).src)
        self.assertEqual('b', f.get(1).src)
        self.assertEqual('c', f.get(2).src)

        f = FST('def f(): pass').get('args')
        self.assertIsInstance(f.a, arguments)
        self.assertEqual('', f.src)

        f = FST('lambda: None').get('args')
        self.assertIsInstance(f.a, arguments)
        self.assertEqual('', f.src)

        # identifier

        self.assertEqual('ident', FST('def ident(): pass').get('name'))
        self.assertEqual('ident', FST('async def ident(): pass').get('name'))
        self.assertEqual('ident', FST('class ident: pass').get('name'))
        self.assertEqual('ident', FST('from ident import *').get('module'))
        self.assertEqual('ident', FST('global ident').get(0, 'names'))
        self.assertEqual('ident', FST('nonlocal ident').get(0, 'names'))
        self.assertEqual('ident', FST('obj.ident').get('attr'))
        self.assertEqual('ident', FST('ident').get('id'))
        self.assertEqual('ident', FST('except Exception as ident: pass').get('name'))
        self.assertEqual('ident', FST('def f(ident): pass').args.args[0].get('arg'))
        self.assertEqual('ident', FST('call(ident=1)').keywords[0].get('arg'))
        self.assertEqual('ident', FST('import ident as b').names[0].get('name'))
        self.assertEqual('ident', FST('import a as ident').names[0].get('asname'))
        self.assertEqual('ident', FST('match a:\n case {**ident}: pass').cases[0].pattern.get('rest'))
        self.assertEqual('ident', FST('match a:\n case cls(ident=1): pass').cases[0].pattern.get(0, 'kwd_attrs'))
        self.assertEqual('ident', FST('match a:\n case (*ident,): pass').cases[0].pattern.patterns[0].get('name'))
        self.assertEqual('ident', FST('match a:\n case 1 as ident: pass').cases[0].pattern.get('name'))

        if PYGE12:
            self.assertEqual('ident', FST('type t[ident] = ...').type_params[0].get('name'))
            self.assertEqual('ident', FST('type t[*ident] = ...').type_params[0].get('name'))
            self.assertEqual('ident', FST('type t[**ident] = ...').type_params[0].get('name'))

        # FormattedValue/Interpolation conversion and format_spec, JoinedStr/TemplateStr values

        if PYGE12:
            self.assertIsNone(None, FST('f"{a}"').values[0].get('conversion'))
            self.assertEqual("'a'", FST('f"{a!a}"').values[0].get('conversion').src)
            self.assertEqual("'r'", FST('f"{a!r}"').values[0].get('conversion').src)
            self.assertEqual("'s'", FST('f"{a!s}"').values[0].get('conversion').src)
            self.assertEqual("'r'", FST('f"{a=}"').values[1].get('conversion').src)

            f = FST('if 1:\n    f"{a!r\n : {\'0.5f<12\'} }"').body[0].value.values[0].get('format_spec')
            self.assertEqual('''f" {'0.5f<12'} "''', f.src)
            f.verify()

            f = FST('f"{a!r\n : {\'0.5f<12\'} }"').values[0].get('format_spec')
            self.assertEqual('''f" {'0.5f<12'} "''', f.src)
            f.verify()

            f = FST('f"{a!r\n : 0.5f<12 }"').values[0].get('format_spec')
            self.assertEqual("f' 0.5f<12 '", f.src)
            f.verify()

            f = FST('f"{a!r : 0.5f<12 }"').values[0].get('format_spec')
            self.assertEqual("f' 0.5f<12 '", f.src)
            f.verify()

            f = FST('f"{a!r:0.5f<12}"').values[0].get('format_spec')
            self.assertEqual("f'0.5f<12'", f.src)
            f.verify()

            f = FST(r'''
f'\
{a:0.5f<12}a' "b" \
 "c" \
f"{d : {"0.5f<12"} }"
                '''.strip())
            g = f.get(1, 'values')
            self.assertEqual("'abc'", g.src)
            g.verify()
            g = f.get(0, 'values')
            self.assertEqual("f'{a:0.5f<12}'", g.src)
            g.verify()
            g = f.get(2, 'values')
            self.assertEqual("""f'{d : {"0.5f<12"} }'""", g.src)
            g.verify()

            f = FST(r'''
if 1:
    f'\
    {a:0.5f<12}a' "b" \
     "c" \
    f"{d : {"0.5f<12"} }"
                '''.strip())
            g = f.body[0].value.get(2, 'values')
            self.assertEqual("'abc'", g.src)
            g.verify()
            g = f.body[0].value.get(1, 'values')
            self.assertEqual("f'{a:0.5f<12}'", g.src)
            g.verify()
            g = f.body[0].value.get(3, 'values')
            self.assertEqual("""f'{d : {"0.5f<12"} }'""", g.src)
            g.verify()

        if PYGE14:
            self.assertIsNone(None, FST('t"{a}"').values[0].get('conversion'))
            self.assertEqual("'a'", FST('t"{a!a}"').values[0].get('conversion').src)
            self.assertEqual("'r'", FST('t"{a!r}"').values[0].get('conversion').src)
            self.assertEqual("'s'", FST('t"{a!s}"').values[0].get('conversion').src)
            self.assertEqual("'r'", FST('t"{a=}"').values[1].get('conversion').src)

            f = FST('if 1:\n    t"{a!r\n : {\'0.5f<12\'} }"').body[0].value.values[0].get('format_spec')
            self.assertEqual('''f" {'0.5f<12'} "''', f.src)
            f.verify()

            f = FST('t"{a!r\n : {\'0.5f<12\'} }"').values[0].get('format_spec')
            self.assertEqual('''f" {'0.5f<12'} "''', f.src)
            f.verify()

            f = FST('t"{a!r\n : 0.5f<12 }"').values[0].get('format_spec')
            self.assertEqual("f' 0.5f<12 '", f.src)
            f.verify()

            f = FST('t"{a!r : 0.5f<12 }"').values[0].get('format_spec')
            self.assertEqual("f' 0.5f<12 '", f.src)
            f.verify()

            f = FST('t"{a!r:0.5f<12}"').values[0].get('format_spec')
            self.assertEqual("f'0.5f<12'", f.src)
            f.verify()

            f = FST(r'''
t'\
{a:0.5f<12}a' t"b" \
 t"c" \
t"{d : {"0.5f<12"} }"
                '''.strip())
            g = f.get(1, 'values')
            self.assertEqual("'abc'", g.src)
            g.verify()
            g = f.get(0, 'values')
            self.assertEqual("t'{a:0.5f<12}'", g.src)
            g.verify()
            g = f.get(2, 'values')
            self.assertEqual("""t'{d : {"0.5f<12"} }'""", g.src)
            g.verify()

            f = FST(r'''
if 1:
    t'\
    {a:0.5f<12}a' t"b" \
     t"c" \
    t"{d : {"0.5f<12"} }"
                '''.strip())
            g = f.body[0].value.get(2, 'values')
            self.assertEqual("'abc'", g.src)
            g.verify()
            g = f.body[0].value.get(1, 'values')
            self.assertEqual("t'{a:0.5f<12}'", g.src)
            g.verify()
            g = f.body[0].value.get(3, 'values')
            self.assertEqual("""t'{d : {"0.5f<12"} }'""", g.src)
            g.verify()

            f = FST("f'a{b:<3}'")
            self.assertEqual("'a'", (g := f.get(0)).src)
            g.verify()

            f = FST('f"{a}" \'b\' "c" \'d\'')
            self.assertEqual("'bcd'", (g := f.get(1)).src)
            g.verify()

            f = FST('f"{a}" \'b\' f"{c}"')
            self.assertEqual("'b'", (g := f.get(1)).src)
            g.verify()

            f = FST('f"abc"')
            self.assertEqual("'abc'", (g := f.get(0)).src)
            g.verify()

        if PYLT12:
            self.assertEqual('(a,)', FST('f"{a,}"').values[0].get().src)
            self.assertEqual('(a, b)', FST('f"{a, b}"').values[0].get().src)
            self.assertEqual('( a, b )', FST('f"{ a, b }"').values[0].get().src)
            self.assertEqual('(a, b)', FST('f"{ (a, b) }"').values[0].get().src)

        # these are truly evil

        if PYGE12:
            if PYGE13:
                self.assertEqual("rf'\\xFF'", (f := FST(r'''rf"{a:\xFF}"''').values[0].format_spec.copy()).src)
                f.verify()

                self.assertEqual("rf'\\n'", (f := FST(r'''rf"{a:\n}"''').values[0].format_spec.copy()).src)
                f.verify()

            else:
                self.assertEqual("f'\\xFF'", (f := FST(r'''rf"{a:\xFF}"''').values[0].format_spec.copy()).src)
                f.verify()

                self.assertEqual("f'\\n'", (f := FST(r'''rf"{a:\n}"''').values[0].format_spec.copy()).src)
                f.verify()

            self.assertEqual("f'\\xFF'", (f := FST(r'''f"{a:\xFF}"''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual('f"{\'\\xff\'}"', (f := FST(r'''f"{a:{'\xff'}}"''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual('f"{\'\\xff\'}"', (f := FST(r'''rf"{a:{'\xff'}}"''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual('f"{r\'\\xff\'}"', (f := FST(r'''f"{a:{r'\xff'}}"''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual('f"{\'\\xff\'}{r\'\\xff\'}"', (f := FST(r'''f"{a:{'\xff'}{r'\xff'}}"''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual("f'\\n'", (f := FST(r'''f"{a:\n}"''').values[0].format_spec.copy()).src)
            f.verify()

            # too many quotes in string so can't figure out which to use

            if PYGE12:
                self.assertRaises(RuntimeError, FST('''f\'\'\'{1:<{f"{f"""{f'{f\'\'\'{1}\'\'\'}'}"""}"} }\'\'\' ''').values[0].get, 'format_spec')

            # type and field not in handlers list

            self.assertRaises(NodeError, FST.fromsrc('x = 1  # type: int', type_comments=True).body[0].get, 'type_comment')

    @unittest.skipUnless(PYGE12, 'only valid for py >= 3.12')
    def test_get_format_spec(self):
        self.assertEqual('''f" {a}, 'b': {b}, 'c': {c}"''', (f := FST('''f"{'a': {a}, 'b': {b}, 'c': {c}}"''').values[0].format_spec.copy()).src)
        f.verify()

        self.assertEqual('''f""" '2', "3" """''', (f := FST('''f"""{1: '2', "3" }"""''').values[0].format_spec.copy()).src)
        f.verify()

        self.assertEqual('''f""" f'2', f"3" """''', (f := FST('''f"""{1: f'2', f"3" }"""''').values[0].format_spec.copy()).src)
        f.verify()

        self.assertEqual("""f''' '2', "3"'''""", (f := FST('''f"""{1: '2', "3"}"""''').values[0].format_spec.copy()).src)
        f.verify()

        self.assertEqual("""f''' f'2', f"3"'''""", (f := FST('''f"""{1: f'2', f"3"}"""''').values[0].format_spec.copy()).src)
        f.verify()

        self.assertEqual('''f""""2", '3'"""''', (f := FST('''f"""{1:"2", '3'}"""''').values[0].format_spec.copy()).src)
        f.verify()

        self.assertEqual("""f'''"2", '3', "4"'''""", (f := FST('''f"""{1:"2", '3', "4"}"""''').values[0].format_spec.copy()).src)
        f.verify()

        if PYGE14:
            self.assertEqual('''f" {a}, 'b': {b}, 'c': {c}"''', (f := FST('''t"{'a': {a}, 'b': {b}, 'c': {c}}"''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual('''f""" '2', "3" """''', (f := FST('''t"""{1: '2', "3" }"""''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual('''f""" t'2', t"3" """''', (f := FST('''t"""{1: t'2', t"3" }"""''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual("""f''' '2', "3"'''""", (f := FST('''t"""{1: '2', "3"}"""''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual("""f''' t'2', t"3"'''""", (f := FST('''t"""{1: t'2', t"3"}"""''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual('''f""""2", '3'"""''', (f := FST('''t"""{1:"2", '3'}"""''').values[0].format_spec.copy()).src)
            f.verify()

            self.assertEqual("""f'''"2", '3', "4"'''""", (f := FST('''t"""{1:"2", '3', "4"}"""''').values[0].format_spec.copy()).src)
            f.verify()

        # evil s@&t

        if PYGE12:
            if PYGE13:
                self.assertEqual(FST(r'''rf"{1:\xFF}"''').values[0].format_spec.copy().a.values[0].value, '\\xFF')
            else:
                self.assertEqual(FST(r'''rf"{1:\xFF}"''').values[0].format_spec.copy().a.values[0].value, 'ÿ')

            self.assertEqual(FST(r'''f"{1:\xFF}"''').values[0].format_spec.copy().a.values[0].value, 'ÿ')
            self.assertEqual(FST(r'''rf"{1:{'\xFF'}}"''').values[0].format_spec.copy().a.values[0].value.value, 'ÿ')
            self.assertEqual(FST(r'''f"{1:{r'\xFF'}}"''').values[0].format_spec.copy().a.values[0].value.value, '\\xFF')
            self.assertEqual(FST(r'''rf"{1:{r'\xFF'}}"''').values[0].format_spec.copy().a.values[0].value.value, '\\xFF')
            self.assertEqual(FST(r'''f"""{1:{'a'\
                                             'b'}}"""''').values[0].format_spec.copy().a.values[0].value.value, 'ab')
            self.assertEqual(FST(r'''rf"""{1:{'a'\
                                              'b'}}"""''').values[0].format_spec.copy().a.values[0].value.value, 'ab')

    def test_get_param_matrix(self):
        f = FST('a = b')

        self.assertEqual('b', f.get(None, None).src)
        self.assertRaises(IndexError, f.get, 0, None)
        self.assertRaises(IndexError, f.get, 'end', None)
        self.assertRaises(IndexError, f.get, None, 0)
        self.assertRaises(IndexError, f.get, 0, 0)
        self.assertRaises(IndexError, f.get, 'end', 0)
        self.assertRaises(IndexError, f.get, None, 'end')
        self.assertRaises(IndexError, f.get, 0, 'end')
        self.assertRaises(IndexError, f.get, 'end', 'end')

        f = FST('[a, b, c]')

        self.assertEqual('[a, b, c]', f.get(None, None).src)
        self.assertEqual('b', f.get(1, None).src)
        self.assertEqual('[]', f.get('end', None).src)
        self.assertEqual('[a]', f.get(None, 1).src)
        self.assertEqual('[]', f.get(1, 1).src)
        self.assertRaises(IndexError, f.get, 'end', 1)
        self.assertEqual('[a, b, c]', f.get(None, 'end').src)
        self.assertEqual('[b, c]', f.get(1, 'end').src)
        self.assertEqual('[]', f.get('end', 'end').src)

    def test_put_param_matrix(self):
        self.assertEqual('a = x', FST('a = b').put('x', None, None).src)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 0, None)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 'end', None)
        self.assertRaises(IndexError, FST('a = b').put, 'x', None, 0)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 0, 0)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 'end', 0)
        self.assertRaises(IndexError, FST('a = b').put, 'x', None, 'end')
        self.assertRaises(IndexError, FST('a = b').put, 'x', 0, 'end')
        self.assertRaises(IndexError, FST('a = b').put, 'x', 'end', 'end')

        self.assertRaises(ValueError, FST('a = b').put, 'x', None, None, one=False)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 0, None, one=False)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 'end', None, one=False)
        self.assertRaises(IndexError, FST('a = b').put, 'x', None, 0, one=False)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 0, 0, one=False)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 'end', 0, one=False)
        self.assertRaises(IndexError, FST('a = b').put, 'x', None, 'end', one=False)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 0, 'end', one=False)
        self.assertRaises(IndexError, FST('a = b').put, 'x', 'end', 'end', one=False)

        self.assertEqual('[[x]]', FST('[a, b, c]').put('[x]', None, None).src)
        self.assertEqual('[a, [x], c]', FST('[a, b, c]').put('[x]', 1, None).src)
        self.assertEqual('[a, b, c, [x]]', FST('[a, b, c]').put('[x]', 'end', None).src)
        self.assertEqual('[[x], b, c]', FST('[a, b, c]').put('[x]', None, 1).src)
        self.assertEqual('[a, [x], b, c]', FST('[a, b, c]').put('[x]', 1, 1).src)
        self.assertRaises(IndexError, FST('[a, b, c]').put,'[x]', 'end', 1)
        self.assertEqual('[[x]]', FST('[a, b, c]').put('[x]', None, 'end').src)
        self.assertEqual('[a, [x]]', FST('[a, b, c]').put('[x]', 1, 'end').src)
        self.assertEqual('[a, b, c, [x]]', FST('[a, b, c]').put('[x]', 'end', 'end').src)

        self.assertEqual('[x]', FST('[a, b, c]').put('[x]', None, None, one=False).src)
        self.assertRaises(ValueError, FST('[a, b, c]').put, '[x]', 1, None, one=False)
        self.assertEqual('[a, b, c, x]', FST('[a, b, c]').put('[x]', 'end', None, one=False).src)
        self.assertEqual('[x, b, c]', FST('[a, b, c]').put('[x]', None, 1, one=False).src)
        self.assertEqual('[a, x, b, c]', FST('[a, b, c]').put('[x]', 1, 1, one=False).src)
        self.assertRaises(IndexError, FST('[a, b, c]').put,'[x]', 'end', 1)
        self.assertEqual('[x]', FST('[a, b, c]').put('[x]', None, 'end', one=False).src)
        self.assertEqual('[a, x]', FST('[a, b, c]').put('[x]', 1, 'end', one=False).src)
        self.assertEqual('[a, b, c, x]', FST('[a, b, c]').put('[x]', 'end', 'end', one=False).src)

    def test_replace_and_put_pars_special(self):
        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.elts[1].f.replace(f, pars=True).root.src)

        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, a, 3]', parse('[1, 2, 3]').body[0].value.f.put(f, 1, pars='auto').root.src)

        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.f.put_slice(f, 1, 2, pars='auto', one=True).root.src)

    def test_replace_returns_new_node(self):
        a = parse('a\nb\nc')
        g = a.body[1].f
        f = g.replace('d')
        self.assertEqual(a.f.src, 'a\nd\nc')
        self.assertEqual(f.src, 'd')
        self.assertIsNone(g.a)

        a = parse('[a, b, c]')
        g = a.body[0].value.elts[1].f
        f = g.replace('d')
        self.assertEqual(a.f.src, '[a, d, c]')
        self.assertEqual(f.src, 'd')
        # self.assertIsNone(g.a)

    def test_replace_raw(self):
        f = parse('def f(a, b): pass').f
        g = f.body[0].args.args[1]
        self.assertEqual('b', g.src)
        h = f.body[0].args.args[1].replace('c=1', raw=True, pars=False)
        self.assertEqual('def f(a, c=1): pass', f.src)
        self.assertEqual('c', h.src)
        self.assertIsNone(g.a)
        i = f.body[0].args.args[1].replace('**d', raw=True, pars=False, to=f.body[0].args.defaults[0])
        self.assertEqual('def f(a, **d): pass', f.src)
        self.assertEqual('d', i.src)
        self.assertIsNone(h.a)

        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.generators[1].replace('for x in y', raw=True, pars=False)
        f = f.repath()
        self.assertEqual(f.src, '[a for c in d for x in y for a in b]')
        self.assertEqual(g.src, 'for x in y')
        # g = f.generators[1].replace(None, raw=True, pars=False)
        # f = f.repath()
        # self.assertEqual(f.src, '[a for c in d  for a in b]')
        # self.assertIsNone(g)
        # # self.assertEqual(g.src, '[a for c in d  for a in b]')
        # g = f.generators[1].replace(None, raw=True, pars=False)
        # f = f.repath()
        # self.assertEqual(f.src, '[a for c in d  ]')
        # self.assertIsNone(g)
        # # self.assertEqual(g.src, '[a for c in d  ]')

        f = parse('f(i for i in j)').body[0].value.args[0].f
        g = f.replace('a', raw=True, pars=False)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f(a)')

        f = parse('f((i for i in j))').body[0].value.args[0].f
        g = f.replace('a', raw=True, pars=False)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f(a)')

        f = parse('f(((i for i in j)))').body[0].value.args[0].f
        g = f.replace('a', raw=True, pars=False)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f((a))')

        self.assertEqual('y', parse('n', mode='eval').body.f.replace('y', raw=True, pars=False).root.src)  # Expression.body

        # parentheses handling

        f = parse('( # 1\ni\n# 2\n)').f
        g = parse('( # 3\nj\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.replace(g, raw=True, pars=False)
        self.assertEqual('( # 1\n( # 3\nj\n# 4\n)\n# 2\n)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        g = parse('( # 3\nj\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.replace(g, raw=True, pars=True)
        self.assertEqual('( # 3\nj\n# 4\n)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        g = parse('( # 3\nj\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.replace(g, raw=True, pars='auto')
        self.assertEqual('( # 3\nj\n# 4\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('( # 3\na + b\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars=False)
        self.assertEqual('i * ( # 1\n( # 3\na + b\n# 4\n)\n# 2\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('( # 3\na + b\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars=True)
        self.assertEqual('i * ( # 3\na + b\n# 4\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('( # 3\na + b\n# 4\n)').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars='auto')
        self.assertEqual('i * ( # 3\na + b\n# 4\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('a + b').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars=False)
        self.assertEqual('i * ( # 1\na + b\n# 2\n)', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('a + b').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars=True)
        self.assertEqual('i * a + b', f.src)

        f = parse('i * ( # 1\nj\n# 2\n)').f
        g = parse('a + b').body[0].value.f.copy(pars=True)
        f.body[0].value.right.replace(g, raw=True, pars='auto')
        self.assertEqual('i * a + b', f.src)

        # put AST

        f = parse('( # 1\ni\n# 2\n)').f
        a = Yield(value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars=False)
        self.assertEqual('( # 1\n(yield 1)\n# 2\n)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = Yield(value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars=True)
        self.assertEqual('(yield 1)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = Yield(value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars='auto')
        self.assertEqual('(yield 1)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = NamedExpr(target=Name(id='i', ctx=Store()), value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars=False)
        self.assertEqual('( # 1\n(i := 1)\n# 2\n)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = NamedExpr(target=Name(id='i', ctx=Store()), value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars=True)
        self.assertEqual('(i := 1)', f.src)

        f = parse('( # 1\ni\n# 2\n)').f
        a = NamedExpr(target=Name(id='i', ctx=Store()), value=Constant(value=1))
        f.body[0].value.replace(a, raw=True, pars='auto')
        self.assertEqual('(i := 1)', f.src)

    def test_replace_existing_one(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_ONE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.replace(None if src == '**DEL**' else src, raw=False, **options) or f.root

                tdst = f.root.src

                f.root.verify(raise_=True)

                self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst, put_src)

            except Exception:
                print(i, attr, options, src)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_ret)
                print('...')
                print(put_src)

                raise

    def test_replace_existing_one_raw(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_ONE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.replace(None if src == '**DEL**' else src, raw=True, **options) or f.root

                tdst = f.root.src

                f.root.verify(raise_=True)

                self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst, put_src)

            except Exception:
                print(i, attr, options, src)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_ret)
                print('...')
                print(put_src)

                raise

    def test_replace_root(self):
        f = FST('i = 1')
        g = f.value
        a = g.a
        h = f.replace('j = 2')
        self.assertIs(h, f)
        self.assertIs(f.root, f)
        self.assertIsNone(g.a)
        self.assertIsNone(a.f)
        self.assertEqual('j = 2', f.src)

        self.assertRaises(ValueError, f.replace, None)
        self.assertRaises(ValueError, f.replace, 'i', to=f.value)

    def test_put_existing_one(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_ONE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                # g = f.replace(None if src == '**DEL**' else src, **options) or f.root
                f.parent.put(None if src == '**DEL**' else src, f.pfield.idx, field=f.pfield.name, raw=False, **options)

                tdst = f.root.src

                f.root.verify(raise_=True)

                # self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst, put_src)

            except Exception:
                print(i, attr, options, src)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_ret)
                print('...')
                print(put_src)

                raise

    def test_put_existing_one_raw(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_ONE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                # g = f.replace(None if src == '**DEL**' else src, **options) or f.root
                f.parent.put(None if src == '**DEL**' else src, f.pfield.idx, field=f.pfield.name, raw=True, **options)

                tdst = f.root.src

                f.root.verify(raise_=True)

                # self.assertEqual(g.src, put_ret)
                self.assertEqual(tdst, put_src)

            except Exception:
                print(i, attr, options, src)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_ret)
                print('...')
                print(put_src)

                raise

    def test_put_special_fields_raw(self):
        with FST.options(pars=False, raw=True):
            self.assertEqual('{a: b, **c, e: f}', parse('{a: b, **d, e: f}').body[0].value.f.put('c', 1, field='values').root.src)
            self.assertEqual('{a: b, c: d, e: f}', parse('{a: b, **d, e: f}').body[0].value.f.put('c: ', 1, field='keys').root.src)
            self.assertEqual('{a: b, **g, e: f}', parse('{a: b, c: d, e: f}').body[0].value.f.put('**g', 1).root.src)
            self.assertEqual('{a: b, c: d, e: f}', parse('{a: b, **g, e: f}').body[0].value.f.put('c: d', 1).root.src)
            self.assertEqual('{a: b, g: d, e: f}', parse('{a: b, c: d, e: f}').body[0].value.f.put('g', 1, field='keys').root.src)
            self.assertEqual('{a: b, c: g, e: f}', parse('{a: b, c: d, e: f}').body[0].value.f.put('g', 1, field='values').root.src)
            self.assertEqual('{a: b, **g, e: f}', parse('{a: b, c: d, e: f}').body[0].value.f.put_slice('**g', 1, 2).root.src)

            self.assertEqual('match a:\n case {4: d, 2: b, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put('4: d', 0).root.src)
            self.assertEqual('match a:\n case {4: a, 2: b, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put('4', 0, field='keys').root.src)
            self.assertEqual('match a:\n case {1: d, 2: b, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put('d', 0, field='patterns').root.src)
            self.assertEqual('match a:\n case {1: a, 2: b, **d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put('**d', 2).root.src)
            self.assertEqual('match a:\n case {4: d, 2: b, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 0, 1).root.src)
            self.assertEqual('match a:\n case {1: a, 4: d, 3: c}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 1, 2).root.src)
            self.assertEqual('match a:\n case {1: a, 2: b, 4: d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 2, 3).root.src)
            self.assertEqual('match a:\n case {1: a, 4: d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 1, 3).root.src)
            self.assertEqual('match a:\n case {4: d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d', 0, 3).root.src)
            self.assertEqual('match a:\n case {4: d}: pass', parse('match a:\n case {1: a, 2: b, 3: c}: pass').body[0].cases[0].pattern.f.put_slice('4: d').root.src)

            self.assertEqual('z < b < c', parse('a < b < c').body[0].value.f.put('z', 0).root.src)
            self.assertEqual('a < z < c', parse('a < b < c').body[0].value.f.put('z', 1).root.src)
            self.assertEqual('a < b < z', parse('a < b < c').body[0].value.f.put('z', 2).root.src)
            self.assertEqual('a < b < z', parse('a < b < c').body[0].value.f.put('z', -1).root.src)
            self.assertEqual('a < z < c', parse('a < b < c').body[0].value.f.put('z', -2).root.src)
            self.assertEqual('z < b < c', parse('a < b < c').body[0].value.f.put('z', -3).root.src)
            self.assertRaises(IndexError, parse('a < b < c').body[0].value.f.put, 'z', 4)
            self.assertRaises(IndexError, parse('a < b < c').body[0].value.f.put, 'z', -4)
            self.assertEqual('z < b < c', parse('a < b < c').body[0].value.f.put('z', field='left').root.src)
            self.assertEqual('a < b < z', parse('a < b < c').body[0].value.f.put('z', 1, field='comparators').root.src)
            self.assertEqual('a < b > c', parse('a < b < c').body[0].value.f.put('>', 1, field='ops').root.src)

            self.assertRaises(ValueError, parse('a < b < c').body[0].value.f.put_slice, 'z', 0, 0)
            self.assertEqual('z < b < c', parse('a < b < c').body[0].value.f.put_slice('z', 0, 1).root.src)
            self.assertEqual('z < c', parse('a < b < c').body[0].value.f.put_slice('z', 0, 2).root.src)
            self.assertEqual('z', parse('a < b < c').body[0].value.f.put_slice('z', 0, 3).root.src)
            self.assertRaises(ValueError, parse('a < b < c').body[0].value.f.put_slice, 'z', 1, 1)
            self.assertEqual('a < z < c', parse('a < b < c').body[0].value.f.put_slice('z', 1, 2).root.src)
            self.assertEqual('a < z', parse('a < b < c').body[0].value.f.put_slice('z', 1, 3).root.src)
            self.assertRaises(ValueError, parse('a < b < c').body[0].value.f.put_slice, 'z', 2, 2)
            self.assertEqual('a < b < z', parse('a < b < c').body[0].value.f.put_slice('z', 2, 3).root.src)
            self.assertRaises(ValueError, parse('a < b < c').body[0].value.f.put_slice, 'z', 3, 3)

            self.assertEqual('[i for i in j if a if z if c]', parse('[i for i in j if a if b if c]').body[0].value.generators[0].f.put('z', 1, field='ifs').root.src)
            self.assertEqual('[i for i in j if a if z if c]', parse('[i for i in j if a if b if c]').body[0].value.generators[0].f.put_slice('if z', 1, 2, field='ifs').root.src)
            self.assertEqual('[i for i in j if a if z]', parse('[i for i in j if a if b if c]').body[0].value.generators[0].f.put_slice('if z', 1, 3, field='ifs').root.src)
            self.assertEqual('[i for i in j if z]', parse('[i for i in j if a if b if c]').body[0].value.generators[0].f.put_slice('if z', field='ifs').root.src)
            self.assertEqual('[i for i in j if a if (z) if c]', parse('[i for i in j if a if (b) if c]').body[0].value.generators[0].f.put('z', 1, field='ifs').root.src)
            self.assertEqual('[i for i in j if a if z if c]', parse('[i for i in j if a if (b) if c]').body[0].value.generators[0].f.put_slice('if z', 1, 2, field='ifs').root.src)
            self.assertEqual('[i for i in j if a if z]', parse('[i for i in j if a if (b) if (c)]').body[0].value.generators[0].f.put_slice('if z', 1, 3, field='ifs').root.src)

            self.assertEqual('@a\n@z\n@c\nclass cls: pass', parse('@a\n@b\n@c\nclass cls: pass').body[0].f.put('z', 1, field='decorator_list').root.src)
            self.assertEqual('@a\n@z\n@c\nclass cls: pass', parse('@a\n@b\n@c\nclass cls: pass').body[0].f.put_slice('@z', 1, 2, field='decorator_list').root.src)
            self.assertEqual('@a\n@z\nclass cls: pass', parse('@a\n@b\n@c\nclass cls: pass').body[0].f.put_slice('@z', 1, 3, field='decorator_list').root.src)
            self.assertEqual('@z\nclass cls: pass', parse('@a\n@b\n@c\nclass cls: pass').body[0].f.put_slice('@z', field='decorator_list').root.src)
            self.assertEqual('@a\n@(z)\n@c\nclass cls: pass', parse('@a\n@(b)\n@c\nclass cls: pass').body[0].f.put('z', 1, field='decorator_list').root.src)
            self.assertEqual('@a\n@z\n@c\nclass cls: pass', parse('@a\n@(b)\n@c\nclass cls: pass').body[0].f.put_slice('@z', 1, 2, field='decorator_list').root.src)
            self.assertEqual('@a\n@z\nclass cls: pass', parse('@a\n@(b)\n@(c)\nclass cls: pass').body[0].f.put_slice('@z', 1, 3, field='decorator_list').root.src)

            self.assertEqual('{a: b, e: f}', FST('{a: b, c: d, e: f}', 'exec').body[0].value.put(None, 1, raw='auto').root.src)
            self.assertEqual('{a: b, e: f}', FST('{a: b, c: d, e: f}', 'exec').body[0].value.put(None, 1, raw=False).root.src)

    def test_put_one_constant(self):
        f = FST('None', Constant)

        for value in (..., 1, 1.0, 1j, 'str', b'bytes', True, False, None):
            self.assertIs(f, f.put(value))
            self.assertEqual(repr(value), f.src)
            self.assertIs(value, f.a.value)

        f = FST('case None: pass')

        for value in (True, False, None):
            self.assertIs(f.pattern, f.pattern.put(value))
            self.assertEqual(f'case {value}: pass', f.src)
            self.assertIs(f.pattern.value, value)

        # if PYGE14:
        #     f = FST('t"{blah}"')

        #     self.assertEqual(f.values[0], f.values[0].put('blah', 'str'))
        #     self.assertEqual('blah', f.values[0].str)

    def test_put_one_ctx(self):
        f = FST('a.b')
        f.put(FST('', Load), 'ctx')
        f.put(Load(), 'ctx')
        self.assertRaises(ValueError, f.put, Store(), 'ctx')
        f.verify()
        f = FST('a.b = 1')
        f.targets[0].put(FST('', Store), 'ctx')
        f.targets[0].put(Store(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Del(), 'ctx')
        f.verify()
        f = FST('del a.b')
        f.targets[0].put(FST('', Del), 'ctx')
        f.targets[0].put(Del(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Load(), 'ctx')
        f.verify()

        f = FST('a[b]')
        f.put(FST('', Load), 'ctx')
        f.put(Load(), 'ctx')
        self.assertRaises(ValueError, f.put, Store(), 'ctx')
        f.verify()
        f = FST('a[b] = 1')
        f.targets[0].put(FST('', Store), 'ctx')
        f.targets[0].put(Store(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Del(), 'ctx')
        f.verify()
        f = FST('del a[b]')
        f.targets[0].put(FST('', Del), 'ctx')
        f.targets[0].put(Del(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Load(), 'ctx')
        f.verify()

        f = FST('*a,')
        f.elts[0].put(FST('', Load), 'ctx')
        f.elts[0].put(Load(), 'ctx')
        self.assertRaises(ValueError, f.elts[0].put, Store(), 'ctx')
        f.verify()
        f = FST('*a, = 1')
        f.targets[0].elts[0].put(FST('', Store), 'ctx')
        f.targets[0].elts[0].put(Store(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].elts[0].put, Del(), 'ctx')
        f.verify()

        f = FST('a')
        f.put(FST('', Load), 'ctx')
        f.put(Load(), 'ctx')
        self.assertRaises(ValueError, f.put, Store(), 'ctx')
        f.verify()
        f = FST('a = 1')
        f.targets[0].put(FST('', Store), 'ctx')
        f.targets[0].put(Store(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Del(), 'ctx')
        f.verify()
        f = FST('del a')
        f.targets[0].put(FST('', Del), 'ctx')
        f.targets[0].put(Del(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Load(), 'ctx')
        f.verify()

        f = FST('[a.b]')
        f.put(FST('', Load), 'ctx')
        f.put(Load(), 'ctx')
        self.assertRaises(ValueError, f.put, Store(), 'ctx')
        f.verify()
        f = FST('[a.b] = 1')
        f.targets[0].put(FST('', Store), 'ctx')
        f.targets[0].put(Store(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Del(), 'ctx')
        f.verify()
        f = FST('del [a.b]')
        f.targets[0].put(FST('', Del), 'ctx')
        f.targets[0].put(Del(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Load(), 'ctx')
        f.verify()

        f = FST('(a.b,)')
        f.put(FST('', Load), 'ctx')
        f.put(Load(), 'ctx')
        self.assertRaises(ValueError, f.put, Store(), 'ctx')
        f.verify()
        f = FST('(a.b,) = 1')
        f.targets[0].put(FST('', Store), 'ctx')
        f.targets[0].put(Store(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Del(), 'ctx')
        f.verify()
        f = FST('del (a.b,)')
        f.targets[0].put(FST('', Del), 'ctx')
        f.targets[0].put(Del(), 'ctx')
        self.assertRaises(ValueError, f.targets[0].put, Load(), 'ctx')
        f.verify()

    def test_put_one_special(self):
        f = parse('i', mode='eval').f
        self.assertIsInstance(f.a.body, expr)
        f.put('j', raw=False)
        self.assertEqual('j', f.src)
        self.assertRaises(SyntaxError, f.put, 'k = 1', raw=False)
        self.assertRaises(IndexError, f.put, 'k', 1, raw=False)

        g = parse('yield 1').body[0].value.f.copy()
        self.assertEqual('yield 1', g.src)
        f.put(g, raw=False)
        self.assertEqual('(yield 1)', f.src)

        f.put('yield from a', raw=False)
        self.assertEqual('(yield from a)', f.src)

        f.put('await x', raw=False)
        self.assertEqual('await x', f.src)

        g = parse('l = 2').body[0].f.copy()
        self.assertEqual('l = 2', g.src)
        self.assertRaises(NodeError, f.put, g, raw=False)

        f.put('m', raw=False)
        self.assertEqual('m', f.src)

        f = parse('[1, 2, 3, 4]').body[0].value.f
        self.assertRaises(NodeError, f.put, '5', 1, raw=False, to=f.elts[2])

        f = parse('[1, 2, 3, 4]').body[0].value.f
        g = f.put('5', 1, raw='auto', to=f.elts[2])
        self.assertEqual('[1, 5, 4]', g.src)

        # make sure put doesn't eat arguments pars

        f = parse('f(i for i in j)').body[0].value.f
        f.put('a', 0, 'args', pars=False, raw=False)
        self.assertEqual('f(a)', f.src)

        f = parse('f((i for i in j))').body[0].value.f
        f.put('a', 0, 'args', pars=False, raw=False)
        self.assertEqual('f(a)', f.src)

        f = parse('f(((i for i in j)))').body[0].value.f
        f.put('a', 0, 'args', pars=False, raw=False)
        self.assertEqual('f((a))', f.src)

        # make sure we can't put TO invalid locations

        f = parse('[1, 2, 3]').body[0].value.f
        # self.assertEqual('[1, 4]', f.elts[1].replace('4', to=f.elts[2], raw=False).root.src)
        self.assertRaises(NodeError, f.elts[1].replace, '4', to=f.elts[2], raw=False)

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertRaises(NodeError, f.elts[1].replace, '4', to=f.elts[0], raw=False)

        f = parse('a = b').body[0].f
        self.assertRaises(NodeError, f.targets[0].replace, 'c', to=f.value, raw=False)

        f = parse('a = b').body[0].f
        self.assertRaises(NodeError, f.value.replace, 'c', to=f.targets[0], raw=False)

        # reject Slice putting to expr

        f = parse('a = b').body[0].f
        s = parse('s[a:b]').body[0].value.slice.f.copy()
        self.assertRaises(NodeError, f.put, s, field='value', raw=False)

        # slice in tuple

        f = parse('s[a:b, x:y:z]').body[0].value.f
        t = f.slice.copy()
        s0 = t.elts[0].copy()
        s1 = t.elts[1].copy()
        self.assertEqual('a:b, x:y:z', t.src)
        self.assertEqual('a:b', s0.src)
        self.assertEqual('x:y:z', s1.src)

        f.put(t, field='slice', raw=False)
        self.assertEqual('a:b, x:y:z', f.slice.src)
        f.slice.put(s1, 0, raw=False)
        self.assertEqual('x:y:z, x:y:z', f.slice.src)
        f.slice.put(s0, 1, raw=False)
        self.assertEqual('x:y:z, a:b', f.slice.src)

        # make sure we don't merge alnums on unparenthesize

        f = FST('[a for a in b if(a)if(a)]', 'exec')
        f.body[0].value.generators[0].put('a', 0, field='ifs')
        f.body[0].value.generators[0].put('a', 1, field='ifs')
        self.assertEqual('[a for a in b if a if a]', f.src)
        f.verify()

        # check that it sanitizes

        f = FST('a = b', 'exec')
        g = FST('c', 'exec').body[0].value.copy()
        g._put_src(' # line\n# post', 0, 1, 0, 1, False)
        g._put_src('# pre\n', 0, 0, 0, 0, False)
        f.body[0].put(g, 'value', pars=False)
        self.assertEqual('a = c', f.src)

        # don't parenthesize put of starred to tuple

        f = FST('a, *b = c', 'exec')
        g = f.body[0].targets[0].elts[1].copy()
        f.body[0].targets[0].put(g.a, 1, raw=False)
        self.assertEqual('a, *b = c', f.src)

        if PYGE12:
            # except vs. except*

            f = FST('try:\n    pass\nexcept Exception:\n    pass', 'exec').body[0].handlers[0].copy()

            g = FST('try:\n    pass\nexcept* ValueError:\n    pass', 'exec')
            g.body[0].put(f.copy().a, 0, field='handlers', raw=False)
            self.assertEqual('try:\n    pass\nexcept* Exception:\n    pass', g.src)

            g = FST('try:\n    pass\nexcept ValueError:\n    pass', 'exec')
            g.body[0].put(f.a, 0, field='handlers', raw=False)
            self.assertEqual('try:\n    pass\nexcept Exception:\n    pass', g.src)

			# except* can't delete type

            f = FST('''
try:
	raise ExceptionGroup("eg", [ValueError(42)])
except* (TypeError, ExceptionGroup):
	pass
            '''.strip(), 'exec')
            g = f.body[0].handlers[0]
            self.assertRaises(ValueError, g.put, None, 'type', raw=False)

            # *args: *starred annotation

            f = FST('def f(*args: *starred): pass', 'exec')
            g = f.body[0].args.vararg.copy()
            f.body[0].args.put(g.a, 'vararg', raw=False)
            self.assertEqual('def f(*args: *starred): pass', f.src)
            f.verify()

        # tuple slice in annotation

        f = FST('def f(x: a[b:c, d:e]): pass', 'exec')
        g = f.body[0].args.args[0].annotation.slice.elts[0].copy()
        f.body[0].args.args[0].annotation.slice.put(g.src, 0, 'elts', raw=False)
        self.assertEqual('def f(x: a[b:c, d:e]): pass', f.src)
        f.verify()

        # special Call.args but not otherwise

        f = FST('call(a)', 'exec')
        f.body[0].value.put('*[] or []', 0, 'args', raw=False)
        self.assertEqual('call(*[] or [])', f.src)
        f.verify()

        f = FST('call(a)', 'exec')
        f.body[0].value.put('yield 1', 0, 'args', raw=False)
        self.assertEqual('call((yield 1))', f.src)
        f.verify()

        # can't delete keyword.arg if non-keywords follow

        f = FST('call(a=b, *c)', 'exec').body[0].value.copy()
        self.assertRaises(ValueError, f.keywords[0].put, None, 'arg')

        f = FST('class c(a=b, *c): pass', 'exec').body[0].copy()
        self.assertRaises(ValueError, f.keywords[0].put, None, 'arg')

        # parenthesize value of deleted Dict key if it needs it

        f = FST('{a: lambda b: None}', 'exec')
        g = f.body[0].value.keys[0].copy()
        f.body[0].value.put(None, 0, 'keys')
        self.assertEqual('{**(lambda b: None)}', f.src)
        f.body[0].value.put(g.a, 0, 'keys')
        self.assertEqual('{a: (lambda b: None)}', f.src)
        f.verify()

        # lone vararg del trailing comma

        f = FST('lambda *args,: 0', 'exec').body[0].value.copy()
        g = f.args.vararg.copy()
        f.args.put(None, 'vararg')
        self.assertEqual('lambda: 0', f.src)
        f.args.put(g, 'vararg')
        self.assertEqual('lambda *args: 0', f.src)

        f = FST('def f(*args,): pass', 'exec').body[0].copy()
        g = f.args.vararg.copy()
        f.args.put(None, 'vararg')
        self.assertEqual('def f(): pass', f.src)
        f.args.put(g, 'vararg')
        self.assertEqual('def f(*args): pass', f.src)

        # lone parenthesized tuple in unparenthesized With.items left after delete of optional_vars needs grouping pars

        f = FST('with (a, b) as c: pass', 'exec').body[0].copy()
        f.items[0].put(None, 'optional_vars', raw=False)
        self.assertEqual('with ((a, b)): pass', f.src)
        f.verify()

        f = FST('with ((a, b) as c): pass', 'exec').body[0].copy()
        f.items[0].put(None, 'optional_vars', raw=False)
        self.assertEqual('with ((a, b)): pass', f.src)
        f.verify()

        f = FST('with ((a, b)) as c: pass', 'exec').body[0].copy()
        f.items[0].put(None, 'optional_vars', raw=False)
        self.assertEqual('with ((a, b)): pass', f.src)
        f.verify()

        f = FST('with (a) as c: pass', 'exec').body[0].copy()
        f.items[0].put(None, 'optional_vars', raw=False)
        self.assertEqual('with (a): pass', f.src)
        f.verify()

        if PYGE14:
            # make sure TemplateStr.str gets modified

            f = FST('''
t"{
t'{
(
a
)
=
!r:>16}'
!r:>16}"
'''.strip(), 'exec')
            self.assertEqual("\nt'{\n(\na\n)\n=\n!r:>16}'", f.body[0].value.values[0].str)
            self.assertEqual('\n(\na\n)', f.body[0].value.values[0].value.values[1].str)

            f.body[0].value.values[0].value.values[1].put('b')
            self.assertEqual("\nt'{\nb\n=\n!r:>16}'", f.body[0].value.values[0].str)
            self.assertEqual('\nb', f.body[0].value.values[0].value.values[1].str)

            f = FST('t"{a}"', 'exec').body[0].value.copy()
            f.values[0].put('b')
            self.assertEqual('b', f.a.values[0].str)

        # put constant

        f = FST('match a:\n case None: pass').cases[0].pattern
        self.assertIsInstance((g := FST('True')).a, Constant)
        f.put(g, 'value', raw=False)
        self.assertEqual('True', g.src)
        self.assertIs(True, g.value)

        self.assertIsInstance((g := FST('False')).a, Constant)
        f.put(g, 'value', raw=False)
        self.assertEqual('False', g.src)
        self.assertIs(False, g.value)

        self.assertIsInstance((g := FST('None')).a, Constant)
        f.put(g, 'value', raw=False)
        self.assertEqual('None', g.src)
        self.assertIs(None, g.value)

        self.assertIsInstance((h := FST('None')).a, Constant)

        for s in ('...', '2', '2.0', '2j', '"str"', 'b"bytes"', 'True', 'False', 'None'):
            self.assertIsInstance((g := FST(s)).a, Constant)

            if g.a.value not in (True, False, None):
                self.assertRaises(NodeError, f.put, g, 'value', raw=False)

            h.put(g, 'value', raw=False)
            self.assertEqual(s, g.src)
            self.assertEqual(h.value, g.value)

        # put other special primitives

        f = FST('from .\\\n.\\\n.module import a')
        f.put(0, 'level')
        self.assertEqual('from module import a', f.src)
        self.assertEqual(0, f.level)
        f.verify()
        f.put(5, 'level')
        self.assertEqual('from .....module import a', f.src)
        self.assertEqual(5, f.level)
        f.verify()

        f = FST('"text"')
        f.put('u', 'kind')
        self.assertEqual('u"text"', f.src)
        self.assertEqual('u', f.kind)
        f.verify()
        f.put(None, 'kind')
        self.assertEqual('"text"', f.src)
        self.assertEqual(None, f.kind)
        f.verify()

        f = FST('[i for j in k for i in j]')
        f.generators[0].put(1, 'is_async')
        self.assertEqual('[i async for j in k for i in j]', f.src)
        self.assertEqual(1, f.generators[0].is_async)
        f.verify()
        f.generators[1].put(1, 'is_async')
        self.assertEqual('[i async for j in k async for i in j]', f.src)
        self.assertEqual(1, f.generators[1].is_async)
        f.verify()
        f.generators[0].put(0, 'is_async')
        self.assertEqual('[i for j in k async for i in j]', f.src)
        self.assertEqual(0, f.generators[0].is_async)
        f.verify()
        f.generators[1].put(0, 'is_async')
        self.assertEqual('[i for j in k for i in j]', f.src)
        self.assertEqual(0, f.generators[1].is_async)
        f.verify()

        # FormattedValue/Interpolation conversion and format_spec, JoinedStr/TemplateStr values

        if PYGE12:
            self.assertRaises(NotImplementedError, FST('f"{a}"').values[0].put, '"s"', 'conversion', raw=False)  # not implemented yet
            self.assertRaises(NotImplementedError, FST('f"{a}"').values[0].put, 'f"0.5f"', 'format_spec', raw=False)  # not implemented yet
            self.assertRaises(NotImplementedError, FST('f"{a}"').put, '"s"', 0, 'values', raw=False)  # not implemented yet

            # f = FST('f"{a}"', stmt)

            # f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            # self.assertEqual('f"{a:0.5f<8}"', f.src)
            # f.verify()

            # # f.value.values[0].put(None, 'format_spec', raw=True)
            # # self.assertEqual('f"{a}"', f.src)
            # # f.verify()

            # f.value.values[0].put('r', 'conversion', raw=True)
            # self.assertEqual('f"{a!r}"', f.src)
            # f.verify()

            # # f.value.values[0].put(None, 'conversion', raw=True)
            # # self.assertEqual('f"{a}"', f.src)
            # # f.verify()

            # f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            # f.value.values[0].put('r', 'conversion', raw=True)
            # self.assertEqual('f"{a!r:0.5f<8}"', f.src)
            # f.verify()

            # # f.value.values[0].put(None, 'format_spec', raw=True)
            # # self.assertEqual('f"{a!r}"', f.src)
            # # f.verify()

            # # f.value.values[0].put(None, 'conversion', raw=True)
            # # self.assertEqual('f"{a}"', f.src)
            # # f.verify()

            # f.value.values[0].put('r', 'conversion', raw=True)
            # f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            # self.assertEqual('f"{a!r:0.5f<8}"', f.src)
            # f.verify()

            # # f.value.values[0].put(None, 'conversion', raw=True)
            # # self.assertEqual('f"{a:0.5f<8}"', f.src)
            # # f.verify()

            # # f.value.values[0].put(None, 'format_spec', raw=True)
            # # self.assertEqual('f"{a}"', f.src)
            # # f.verify()

            # f.value.put('{z}', 0, 'values', raw=True)
            # self.assertEqual('f"{z}"', f.src)
            # f.verify()

            # f = FST('f"{a=}"', stmt)

            # f.value.values[1].put('r', 'conversion', raw=True)
            # self.assertEqual('f"{a=!r}"', f.src)
            # f.verify()

            # # f.value.values[1].put(None, 'conversion', raw=True)
            # # self.assertEqual('f"{a=}"', f.src)
            # # f.verify()

            # f.value.values[1].put('0.5f<8', 'format_spec', raw=True)
            # f.value.values[1].put('r', 'conversion', raw=True)
            # self.assertEqual('f"{a=!r:0.5f<8}"', f.src)
            # f.verify()

            # # f.value.values[1].put(None, 'conversion', raw=True)
            # # self.assertEqual('f"{a=:0.5f<8}"', f.src)
            # # f.verify()

            # # f.value.values[1].put(None, 'format_spec', raw=True)
            # # self.assertEqual('f"{a=}"', f.src)
            # # f.verify()

        if PYGE14:
            self.assertRaises(NotImplementedError, FST('t"{a}"').values[0].put, '"s"', 'conversion', raw=False)  # not implemented yet
            self.assertRaises(NotImplementedError, FST('t"{a}"').values[0].put, 'f"0.5f"', 'format_spec', raw=False)  # not implemented yet
            self.assertRaises(NotImplementedError, FST('t"{a}"').put, '"s"', 0, 'values', raw=False)  # not implemented yet

            # f = FST('t"{a}"', stmt)

            # f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            # self.assertEqual('t"{a:0.5f<8}"', f.src)
            # f.verify()

            # # f.value.values[0].put(None, 'format_spec', raw=True)
            # # self.assertEqual('t"{a}"', f.src)
            # # f.verify()

            # f.value.values[0].put('r', 'conversion', raw=True)
            # self.assertEqual('t"{a!r}"', f.src)
            # f.verify()

            # # f.value.values[0].put(None, 'conversion', raw=True)
            # # self.assertEqual('t"{a}"', f.src)
            # # f.verify()

            # f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            # f.value.values[0].put('r', 'conversion', raw=True)
            # self.assertEqual('t"{a!r:0.5f<8}"', f.src)
            # f.verify()

            # # f.value.values[0].put(None, 'format_spec', raw=True)
            # # self.assertEqual('t"{a!r}"', f.src)
            # # f.verify()

            # # f.value.values[0].put(None, 'conversion', raw=True)
            # # self.assertEqual('t"{a}"', f.src)
            # # f.verify()

            # f.value.values[0].put('r', 'conversion', raw=True)
            # f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            # self.assertEqual('t"{a!r:0.5f<8}"', f.src)
            # f.verify()

            # f.value.values[0].put(None, 'conversion', raw=True)
            # self.assertEqual('t"{a:0.5f<8}"', f.src)
            # f.verify()

            # # f.value.values[0].put(None, 'format_spec', raw=True)
            # # self.assertEqual('t"{a}"', f.src)
            # # f.verify()

            # f.value.put('{z}', 0, 'values', raw=True)
            # self.assertEqual('t"{z}"', f.src)
            # f.verify()

            # f = FST('t"{a=}"', stmt)

            # f.value.values[1].put('r', 'conversion', raw=True)
            # self.assertEqual('t"{a=!r}"', f.src)
            # f.verify()

            # # f.value.values[1].put(None, 'conversion', raw=True)
            # # self.assertEqual('t"{a=}"', f.src)
            # # f.verify()

            # f.value.values[1].put('0.5f<8', 'format_spec', raw=True)
            # f.value.values[1].put('r', 'conversion', raw=True)
            # self.assertEqual('t"{a=!r:0.5f<8}"', f.src)
            # f.verify()

            # # f.value.values[1].put(None, 'conversion', raw=True)
            # # self.assertEqual('t"{a=:0.5f<8}"', f.src)
            # # f.verify()

            # # f.value.values[1].put(None, 'format_spec', raw=True)
            # # self.assertEqual('t"{a=}"', f.src)
            # # f.verify()

        # Starred has different behavior as a call arg

        f = FST('call(a)')
        g = FST('*(b or c)')
        f.put(g, 0, 'args')
        self.assertEqual('call(*b or c)', f.src)
        f.verify()

        g = FST('*(b if c else d)')
        f.put(g, 0, 'args')
        self.assertEqual('call(*b if c else d)', f.src)
        f.verify()

        g = FST('*(yield)')
        f.put(g, 0, 'args')
        self.assertEqual('call(*(yield))', f.src)
        f.verify()

        g = FST('*(b := c)')
        f.put(g, 0, 'args')
        self.assertEqual('call(*(b := c))', f.src)
        f.verify()

        # More misc stuff

        f = FST('a.b')
        f.put('1', 'value', raw=False)
        self.assertEqual('(1).b', f.src)

        if PYGE12:
            f = FST('f"a{b}"')
            f.values[1].put('{1}', 'value', raw=False)
            self.assertEqual('f"a{ {1}}"', f.src)
            f.verify()

            f = FST('f"{b=}"')
            f.values[1].put('{1}', 'value', raw=False)
            self.assertEqual('f"{ {1}=}"', f.src)
            f.verify()

            f = FST('f"a{b=}"')
            f.values[1].put('{1}', 'value', raw=False)
            self.assertEqual('f"a{ {1}=}"', f.src)
            f.verify()

        f = FST('f(o=o, *s)')
        self.assertRaises(ValueError, f.put, 'a', 0, 'args')
        f.put('*a', 0, 'args')
        self.assertEqual('f(o=o, *a)', f.src)
        f.verify()

        f = FST('class cls(o=o, *s): pass')
        self.assertRaises(ValueError, f.put, 'a', 0, 'bases')
        f.put('*a', 0, 'bases')
        self.assertEqual('class cls(o=o, *a): pass', f.src)
        f.verify()

        f = FST('with a: pass')
        f.items[0].put('b\n,', 'context_expr')
        self.assertEqual('with ((b\n,)): pass', f.src)
        f.verify()

        f = FST('a: int = x.y')
        f.value.value.replace('(c.d)', pars=True)
        self.assertEqual('a: int = (c.d).y', f.src)
        self.assertEqual(1, f.a.simple)
        f.verify()

        f = FST('a.b: int')
        f.target.value.replace('(c.d)', pars=True)
        self.assertEqual('((c.d).b): int', f.src)
        self.assertEqual(0, f.a.simple)
        f.verify()

        f = FST('a.b: int')
        f.target.value.replace('(c).d', pars=True)
        self.assertEqual('((c).d.b): int', f.src)
        self.assertEqual(0, f.a.simple)
        f.verify()

        f = FST('a[b]: int')
        f.target.value.replace('(c[d])', pars=True)
        self.assertEqual('((c[d])[b]): int', f.src)
        self.assertEqual(0, f.a.simple)
        f.verify()

        f = FST('a[b]: int')
        f.target.value.replace('(c)[d]', pars=True)
        self.assertEqual('((c)[d][b]): int', f.src)
        self.assertEqual(0, f.a.simple)
        f.verify()

        f = FST('a.b[c].d[e]: int')
        f.target.value.value.value.value.replace('(f[g])', pars=True)
        self.assertEqual('((f[g]).b[c].d[e]): int', f.src)
        self.assertEqual(0, f.a.simple)
        f.verify()

        f = FST('a.b[c].d[e]: int')
        f.target.value.value.value.value.replace('(f)[g].h[i]', pars=True)
        self.assertEqual('((f)[g].h[i].b[c].d[e]): int', f.src)
        self.assertEqual(0, f.a.simple)
        f.verify()

        f = FST('a.b: int')
        f.put(0, 'simple')
        self.assertEqual('a.b: int', f.src)
        self.assertEqual(0, f.a.simple)
        f.verify()
        self.assertRaises(ValueError, f.put, 1, 'simple')

        f = FST('a: int')
        f.put(0, 'simple')
        self.assertEqual('(a): int', f.src)
        self.assertEqual(0, f.a.simple)
        f.verify()
        f.put(1, 'simple')
        self.assertEqual('a: int', f.src)
        self.assertEqual(1, f.a.simple)

        if PYGE12:
            f = FST('f"{a if b else c}"')
            f.values[0].value.orelse.replace('lambda: None', raw=False)
            self.assertEqual('f"{a if b else (lambda: None)}"', f.src)
            f.verify()

        # Tuple Slice behavior

        self.assertEqual('x:y:z, b', FST('a, b').elts[0].replace('x:y:z', raw=False).root.src)
        self.assertEqual('(x:y:z, b)', FST('(a, b)').elts[0].replace('x:y:z', raw=False).root.src)
        self.assertEqual('s[x:y:z, b]', FST('s[a, b]').slice.elts[0].replace('x:y:z', raw=False).root.src)
        self.assertRaises(NodeError, FST('s[(a, b)]').slice.elts[0].replace, 'x:y:z', raw=False)
        self.assertRaises(NodeError, FST('i = a, b').value.elts[0].replace, 'x:y:z', raw=False)
        self.assertRaises(NodeError, FST('i = (a, b)').value.elts[0].replace, 'x:y:z', raw=False)

        # Starred where allowed

        self.assertEqual('*x, b', FST('a, b').elts[0].replace('*x', raw=False).root.src)
        self.assertEqual('(*x, b)', FST('(a, b)').elts[0].replace('*x', raw=False).root.src)
        self.assertEqual('[*x, b]', FST('[a, b]').elts[0].replace('*x', raw=False).root.src)
        self.assertEqual('{*x, b}', FST('{a, b}').elts[0].replace('*x', raw=False).root.src)
        self.assertEqual('class cls(*x): pass', FST('class cls(a): pass').bases[0].replace('*x', raw=False).root.src)
        self.assertEqual('call(*x)', FST('call(a)').args[0].replace('*x', raw=False).root.src)

        # lone With.items tuple

        self.assertEqual('with ((x, y)): pass', (f := FST('with a: pass').items[0].replace('x, y', raw=False).root).src)
        f.verify()

        self.assertEqual('with ((x, y)): pass', (f := FST('with a: pass').items[0].replace('(x, y)', raw=False).root).src)
        f.verify()

        self.assertEqual('with ((x, y)): pass', (f := FST('with a: pass').items[0].replace(FST('x, y', withitem), raw=False).root).src)
        f.verify()

        self.assertEqual('with ((x, y)): pass', (f := FST('with a: pass').items[0].replace(FST('(x, y)', withitem), raw=False).root).src)
        f.verify()

        self.assertEqual('with ((x, y)): pass', (f := FST('with a: pass').items[0].replace(FST('(x, y)', withitem).a, raw=False).root).src)
        f.verify()

        # starred annotation in FunctionDef

        self.assertRaises(NodeError, FST('def f(a): pass').args.args[0].put, '*ann', 'annotation', raw=False)

        if PYLT11:
            self.assertRaises(NodeError, FST('def f(*a): pass').args.vararg.put, '*ann', 'annotation', raw=False)
        else:
            self.assertEqual('def f(*a: *ann): pass', FST('def f(*a): pass').args.vararg.put('*ann', 'annotation', raw=False).root.src)

        # update AnnAssign.simple

        f = FST('a.b: int')
        self.assertEqual(f.a.simple, 0)
        f.target.replace('c')
        self.assertEqual(f.a.simple, 1)
        f.verify()

        if not PYLT12:
            # gh-135148 behavior, should verify regardless of if bug is present or not

            f = FST('f"{a=}"')
            f.values[1].value.replace('''(
a, # a
b, # b
c, # c
)''', raw=False)
            f.verify()

            f = FST('f"{a=}"')
            f.values[1].value.replace('''
a, # a
b, # b
c, # c
''', raw=False)
            f.verify()

            f = FST('f"{a=}"')
            f.values[1].value.replace('''"""
a, # a
b, # b
c, # c
"""''', raw=False)
            f.verify()

        # incorrect alias FST not allowed

        a = FST('import a.b')
        b = FST('from c import *')
        self.assertRaises(NodeError, a.a.names[0].f.replace, b.names[0].copy(), raw=False)
        self.assertRaises(NodeError, b.a.names[0].f.replace, a.names[0].copy(), raw=False)

        # replacing implicit starred tuple

        f = FST(['a[(*b,)]'])
        f.slice.elts[0].replace('c.d', raw=False)
        self.assertEqual('a[(c.d,)]', f.src)
        f.verify()

        if not PYLT12:
            f = FST(['a[*b,]'])
            f.slice.elts[0].replace('c.d', raw=False)
            self.assertEqual('a[c.d,]', f.src)
            f.verify()

            f = FST(['a[*b]'])
            f.slice.elts[0].replace('c.d', raw=False)
            self.assertEqual('a[c.d,]', f.src)
            f.verify()

        # no Starred in unparenthesized slice Tuple

        if PYLT11:
            f = FST('a: b[c, d]')
            f.annotation.slice.elts[1].replace('*s', raw=False)
            self.assertEqual('a: b[(c, *s)]', f.src)

            f = FST('a: b[c, d]')
            g = FST('for a, *s in b: pass').target.copy()
            self.assertRaises(NodeError, f.annotation.slice.replace, g, raw=False)

            f = FST('a[b,]')
            f.slice.put('*st', 0, raw=False)
            self.assertEqual('a[(*st,)]', f.src)

            f = FST('a[b:c:d,]')
            f.slice.put('*st', 0, raw=False)
            self.assertEqual('a[(*st,)]', f.src)

            f = FST('a[b:c:d, e]')
            f.slice.put('*st', 0, raw=False)
            self.assertEqual('a[(*st, e)]', f.src)

            f = FST('a[b:c:d, e]')
            self.assertRaises(NodeError, f.slice.put, '*st', 1, raw=False)

        # don't allow vararg with starred annotation into normal args

        if not PYLT11:
            f = FST('def f(a, /, b, *v: *s, c): pass')
            self.assertRaises(NodeError, f.args.posonlyargs[0].replace, f.args.vararg.copy(), raw=False)
            self.assertRaises(NodeError, f.args.args[0].replace, f.args.vararg.copy(), raw=False)
            self.assertRaises(NodeError, f.args.kwonlyargs[0].replace, f.args.vararg.copy(), raw=False)

        # star to ImportFrom.names

        f = FST('from a import b, c')
        self.assertRaises(NodeError, f.put, FST('*', alias), 0, 'names')

        f = FST('from a import (b)')
        f.put(FST('*', alias), 0, 'names')
        self.assertEqual('from a import *', f.src)

        f = FST('from a import (b,)')
        f.put(FST('*', alias), 0, 'names')
        self.assertEqual('from a import *', f.src)

        f = FST('from a import (\nb\n)')
        f.put(FST('*', alias), 0, 'names')
        self.assertEqual('from a import *', f.src)

        f = FST('from a import (\nb,\n)')
        f.put(FST('*', alias), 0, 'names')
        self.assertEqual('from a import *', f.src)

        self.assertEqual('from time import *', (f := FST('from time import (time)')).put('*', 0).root.src)
        f.verify()

        self.assertEqual('from time import *', (f := FST('from time import(time)')).put('*', 0).root.src)
        f.verify()

        if PYGE14:
            # parenthesize ExceptHandler.type Tuple if put Starred to it

            f = FST('except a, b: pass')
            f.type.put('*c', 1)
            self.assertEqual('except (a, *c): pass', f.src)

        # proper Store / Del targets

        f = FST('[a,] = b')
        self.assertRaises(NodeError, f.targets[0].put, '2', 0, 'elts')

        f = FST('del [a]')
        self.assertRaises(NodeError, f.targets[0].put, '2', 0, 'elts')
        self.assertRaises(NodeError, f.targets[0].put, '*z', 0, 'elts')

        f = FST('(a,) = b')
        self.assertRaises(NodeError, f.targets[0].put, '2', 0, 'elts')
        f = FST('a, = b')
        self.assertRaises(NodeError, f.targets[0].put, '2', 0, 'elts')
        self.assertEqual('*z, = b', f.targets[0].put('*z', 0, 'elts').root.src)

        f = FST('del (a,)')
        self.assertRaises(NodeError, f.targets[0].put, '2', 0, 'elts')
        self.assertRaises(NodeError, f.targets[0].put, '*z', 0, 'elts')

        # ImportFrom dot schenanigans

        self.assertEqual('from.ConsoleOptions import Text', (f := FST('from.text import Text')).put('ConsoleOptions', 'module').src)
        self.assertEqual('from.ConsoleOptions import Text', (f := FST('from. import Text')).put('ConsoleOptions', 'module').src)

        self.assertRaises(NotImplementedError, FST('from . a . b import c').put, 'd', 'module')

        # 1. put in front of alphanumeric

        self.assertEqual('with 1. as a: pass', (f := FST('with []as a: pass')).items[0].context_expr.replace('1.').root.src)
        f.verify()

        # don't allow Starred as a target in del

        self.assertRaises(NodeError, FST('del a').put, '*st', 0)

        # multiline Import name

        self.assertEqual('import x, a \\\n. \\\nb, z', (f := FST('import x, y, z')).put('a\n.\nb', 1).root.src)
        f.verify()

        self.assertEqual('import x, a\\\n.\\\nb, z', (f := FST('import x, y, z')).put('a\\\n.\\\nb', 1).root.src)
        f.verify()

        # multiline ImportFrom name

        self.assertEqual('from m import x, a as b, z', (f := FST('from m import x, y, z')).put('a as b', 1).root.src)
        f.verify()

        self.assertEqual('from m import (x, a\nas\nb, z)', (f := FST('from m import x, y, z')).put('a\nas\nb', 1).root.src)
        f.verify()

        self.assertEqual('from m import (x, a\nas\nb, z)', (f := FST('from m import (x, y, z)')).put('a\nas\nb', 1).root.src)
        f.verify()

        # Constant.value which is in JoinedStr/TemplateStr.values

        self.assertRaises(NotImplementedError, FST('f"a"').values[0].put, '"b"')

        # misc incorrect constant values

        self.assertRaises(ValueError, FST('a: int', 'AnnAssign').put, -1, 'simple')
        self.assertRaises(ValueError, FST('from . import *').put, -1, 'level')
        self.assertRaises(ValueError, FST('from . import *').put, 0, 'level')
        self.assertRaises(ValueError, FST('"a"').put, 'z', 'kind')
        self.assertRaises(ValueError, FST('async for a in b').put, -1, 'is_async')

    def test_put_one_pattern(self):

        # pattern BinOp and UnaryOp

        f = FST('case -1: pass')
        self.assertRaises(NodeError, f.pattern.value.op.replace, '+', raw=False)

        f = FST('case 1 + 1j: pass')
        self.assertRaises(NodeError, f.pattern.value.op.replace, '*', raw=False)

        f = FST('case -1: pass')
        f.pattern.value.operand.replace('2', raw=False)
        self.assertEqual('case -2: pass', f.src)

        f = FST('case -1: pass')
        f.pattern.value.operand.replace('1j', raw=False)
        self.assertEqual('case -1j: pass', f.src)

        f = FST('case -1: pass')
        self.assertRaises(NodeError, f.pattern.value.operand.replace, 'a', raw=False)

        f = FST('case -1: pass')
        self.assertRaises(NodeError, f.pattern.value.operand.replace, '"a"', raw=False)

        f = FST('case 1 + 1j: pass')
        f.pattern.value.right.replace('2j', raw=False)
        self.assertEqual('case 1 + 2j: pass', f.src)

        f = FST('case 1 + 1j: pass')
        self.assertRaises(NodeError, f.pattern.value.right.replace, '-2j', raw=False)

        f = FST('case 1 + 1j: pass')
        self.assertRaises(NodeError, f.pattern.value.right.replace, 'a', raw=False)

        f = FST('case 1 + 1j: pass')
        self.assertRaises(NodeError, f.pattern.value.right.replace, '"a"', raw=False)

        f = FST('case 1 + 1j: pass')
        f.pattern.value.left.replace('2', raw=False)
        self.assertEqual('case 2 + 1j: pass', f.src)

        f = FST('case 1 + 1j: pass')
        f.pattern.value.left.replace('-2', raw=False)
        self.assertEqual('case -2 + 1j: pass', f.src)

        f = FST('case 1 + 1j: pass')
        self.assertRaises(NodeError, f.pattern.value.left.replace, '2j', raw=False)

        f = FST('case 1 + 1j: pass')
        self.assertRaises(NodeError, f.pattern.value.left.replace, '+2', raw=False)

        f = FST('case 1 + 1j: pass')
        self.assertRaises(NodeError, f.pattern.value.left.replace, 'a', raw=False)

        f = FST('case 1 + 1j: pass')
        self.assertRaises(NodeError, f.pattern.value.left.replace, '"a"', raw=False)

        # naked MatchStar and other star/sequence

        f = FST('match x: \n case [*_]: pass', 'exec')
        g = f.body[0].cases[0].pattern.patterns[0].copy()
        f.body[0].cases[0].pattern.put(g.a, 0, 'patterns', raw=False)
        self.assertEqual('match x: \n case [*_]: pass', f.src)
        f.verify()

        f = FST('match x: \n case 1: pass', 'exec')
        f.body[0].cases[0].put('*x, 1,', 'pattern', raw=False)
        self.assertEqual('match x: \n case [*x, 1,]: pass', f.src)
        f.verify()

        f = FST('match x: \n case 1: pass', 'exec')
        f.body[0].cases[0].put('1, *x,', 'pattern', raw=False)
        self.assertEqual('match x: \n case [1, *x,]: pass', f.src)
        f.verify()

        # MatchAs, ugh...

        f = FST('match a:\n case _ as unknown: pass', 'exec')
        g = f.body[0].cases[0].pattern.pattern.copy()
        f.body[0].cases[0].pattern.put(None, 'pattern', raw=False)
        self.assertEqual('match a:\n case unknown: pass', f.src)
        f.body[0].cases[0].pattern.put(g, 'pattern', raw=False)
        self.assertEqual('match a:\n case _ as unknown: pass', f.src)
        f.verify()

        # more patterns

        f = FST('case {a.b: 1}: pass')
        self.assertRaises(NodeError, f.pattern.keys[0].put, 'f().b', raw=False)
        self.assertRaises(NodeError, f.pattern.keys[0].put, '(1+2).b', raw=False)
        self.assertRaises(NodeError, f.pattern.keys[0].put, 'a[b].b', raw=False)
        self.assertRaises(NodeError, f.pattern.keys[0].put, '(a)', raw=False)
        self.assertRaises(NodeError, f.pattern.keys[0].put, '(a).b', raw=False)
        self.assertRaises(NodeError, f.pattern.keys[0].replace, '(a).b', raw=False)
        f.pattern.keys[0].put('x.y.z', raw=False)
        self.assertEqual('case {x.y.z.b: 1}: pass', f.src)
        f.pattern.keys[0].replace('x.y.z', raw=False)
        self.assertEqual('case {x.y.z: 1}: pass', f.src)
        f.verify()

        f = FST('case a.b: pass')
        self.assertRaises(NodeError, f.pattern.value.put, 'f().b', raw=False)
        self.assertRaises(NodeError, f.pattern.value.put, '(1+2).b', raw=False)
        self.assertRaises(NodeError, f.pattern.value.put, 'a[b].b', raw=False)
        self.assertRaises(NodeError, f.pattern.value.put, '(a)', raw=False)
        self.assertRaises(NodeError, f.pattern.value.put, '(a).b', raw=False)
        self.assertRaises(NodeError, f.pattern.value.replace, '(a).b', raw=False)
        f.pattern.value.put('x.y.z', raw=False)
        self.assertEqual('case x.y.z.b: pass', f.src)
        f.pattern.value.replace('x.y.z', raw=False)
        self.assertEqual('case x.y.z: pass', f.src)
        f.verify()

        f = FST('case a.b(): pass')
        self.assertRaises(NodeError, f.pattern.cls.put, 'f().b', raw=False)
        self.assertRaises(NodeError, f.pattern.cls.put, '(1+2).b', raw=False)
        self.assertRaises(NodeError, f.pattern.cls.put, 'a[b].b', raw=False)
        self.assertRaises(NodeError, f.pattern.cls.put, '(a)', raw=False)
        self.assertRaises(NodeError, f.pattern.cls.put, '(a).b', raw=False)
        self.assertRaises(NodeError, f.pattern.cls.put, 'a\n.\nb', raw=False)
        self.assertRaises(NodeError, f.pattern.cls.replace, '(a).b', raw=False)
        f.pattern.cls.put('x.y.z', raw=False)
        self.assertEqual('case x.y.z.b(): pass', f.src)
        f.pattern.cls.replace('x.y.z', raw=False)
        self.assertEqual('case x.y.z(): pass', f.src)
        f.verify()

        f = FST('case a, b: pass')
        f.pattern.patterns[0].replace(FST('x, *y', pattern), raw=False)
        self.assertEqual('case [x, *y], b: pass', f.src)
        f.verify()

        f = FST('case [a, b]: pass')
        f.pattern.patterns[0].replace(FST('x, *y', pattern), raw=False)
        self.assertEqual('case [[x, *y], b]: pass', f.src)
        f.verify()

        f = FST('case cls(a): pass')
        f.pattern.patterns[0].replace(FST('x, *y', pattern), raw=False)
        self.assertEqual('case cls([x, *y]): pass', f.src)
        f.verify()

        f = FST('case cls(a=b): pass')
        f.pattern.kwd_patterns[0].replace(FST('x, *y', pattern), raw=False)
        self.assertEqual('case cls(a=[x, *y]): pass', f.src)
        f.verify()

        f = FST('case a | b: pass')
        f.pattern.patterns[0].replace(FST('x, *y', pattern), raw=False)
        self.assertEqual('case [x, *y] | b: pass', f.src)
        f.verify()

        f = FST('case {1: b}: pass')
        f.pattern.patterns[0].replace(FST('x, *y', pattern), raw=False)
        self.assertEqual('case {1: [x, *y]}: pass', f.src)
        f.verify()

        f = FST('case a as b: pass')
        f.pattern.pattern.replace(FST('x, *y', pattern), raw=False)
        self.assertEqual('case [x, *y] as b: pass', f.src)
        f.verify()

        f = FST('case (a | b): pass')
        f.pattern.replace(FST('x, *y', pattern), raw=False)
        self.assertEqual('case [x, *y]: pass', f.src)
        f.verify()

        f = FST('case 1: pass')
        self.assertRaises(NodeError, f.pattern.value.replace, 'True', raw=False)
        self.assertRaises(NodeError, f.pattern.value.replace, 'False', raw=False)
        self.assertRaises(NodeError, f.pattern.value.replace, 'None', raw=False)
        f.verify()

        f = FST('case {1: a.b}: pass')
        f.pattern.patterns[0].value.value.replace(FST('x\n  .\n  y', expr), raw=False)
        self.assertEqual('case {1: x\n  .\n  y.b}: pass', f.src)
        f.verify()

        f = FST('case 1: pass')
        self.assertRaises(NodeError, f.pattern.replace, '*s', raw=False)

        f = FST('case 0 as z: pass')
        self.assertRaises(NodeError, f.pattern.pattern.replace, '*s', raw=False)

        f = FST('case {0: z}: pass')
        self.assertRaises(NodeError, f.pattern.patterns[0].replace, '*s', raw=False)

        f = FST('case cls(a): pass')
        self.assertRaises(NodeError, f.pattern.patterns[0].replace, '*s', raw=False)

        f = FST('case cls(a=1): pass')
        self.assertRaises(NodeError, f.pattern.kwd_patterns[0].replace, '*s', raw=False)

        f = FST('case a | b: pass')
        self.assertRaises(NodeError, f.pattern.patterns[0].replace, '*s', raw=False)

        f = FST('case f(): pass')
        self.assertRaises(NodeError, f.pattern.cls.replace, '_', raw=False)

    def test_put_one_op(self):
        # self.assertEqual('a >>= b', parse('a *= b').body[0].f.put('>>=', field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('a *= b').body[0].f.put, 'and', field='op', raw=False)
        self.assertEqual('a += b', parse('a *= b').body[0].f.put('+', field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('a *= b').body[0].f.put, '~', field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a *= b').body[0].f.put, '<', field='op', raw=False)

        self.assertRaises(SyntaxError, parse('a or b').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put('and', field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('a or b').body[0].value.f.put, '/', field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a or b').body[0].value.f.put, '~', field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a or b').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(SyntaxError, parse('a + b').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a + b').body[0].value.f.put, 'and', field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put('>>', field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('a + b').body[0].value.f.put, '~', field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a + b').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(SyntaxError, parse('-a').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertRaises(SyntaxError, parse('-a').body[0].value.f.put, 'and', field='op', raw=False)
        self.assertRaises(SyntaxError, parse('-a').body[0].value.f.put, '*', field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put('+', field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('-a').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(SyntaxError, parse('a is not b').body[0].value.f.put, '*=', 0, field='ops', raw=False)
        self.assertRaises(SyntaxError, parse('a is not b').body[0].value.f.put, 'and', 0, field='ops', raw=False)
        self.assertRaises(SyntaxError, parse('a is not b').body[0].value.f.put, '*', 0, field='ops', raw=False)
        self.assertRaises(SyntaxError, parse('a is not b').body[0].value.f.put, '~', 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a is not b').body[0].value.f.put('>', 0, field='ops', raw=False).src)

        # self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(['>>='], field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('a *= b').body[0].f.put, ['and'], field='op', raw=False)
        self.assertEqual('a += b', parse('a *= b').body[0].f.put(['+'], field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('a *= b').body[0].f.put, ['~'], field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a *= b').body[0].f.put, ['<'], field='op', raw=False)

        self.assertRaises(SyntaxError, parse('a or b').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put(['and'], field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('a or b').body[0].value.f.put, ['/'], field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a or b').body[0].value.f.put, ['~'], field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a or b').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(SyntaxError, parse('a + b').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a + b').body[0].value.f.put, ['and'], field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put(['>>'], field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('a + b').body[0].value.f.put, ['~'], field='op', raw=False)
        self.assertRaises(SyntaxError, parse('a + b').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(SyntaxError, parse('-a').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertRaises(SyntaxError, parse('-a').body[0].value.f.put, ['and'], field='op', raw=False)
        self.assertRaises(SyntaxError, parse('-a').body[0].value.f.put, ['*'], field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put(['+'], field='op', raw=False).src)
        self.assertRaises(SyntaxError, parse('-a').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(SyntaxError, parse('a < b').body[0].value.f.put, ['*='], 0, field='ops', raw=False)
        self.assertRaises(SyntaxError, parse('a < b').body[0].value.f.put, ['and'], 0, field='ops', raw=False)
        self.assertRaises(SyntaxError, parse('a < b').body[0].value.f.put, ['*'], 0, field='ops', raw=False)
        self.assertRaises(SyntaxError, parse('a < b').body[0].value.f.put, ['~'], 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a < b').body[0].value.f.put(['>'], 0, field='ops', raw=False).src)

        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(RShift(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, And(), field='op', raw=False)
        self.assertEqual('a *= b', parse('a *= b').body[0].f.put(Mult(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, Invert(), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, Lt(), field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, Mult(), field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put(And(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, Div(), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, Invert(), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, Lt(), field='op', raw=False)

        self.assertEqual('a * b', parse('a + b').body[0].value.f.put(Mult(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, And(), field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put(RShift(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, Invert(), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, Lt(), field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, Mult(), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, And(), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, Sub(), field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put(UAdd(), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, Lt(), field='op', raw=False)

        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, Mult(), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, And(), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, Sub(), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, UAdd(), 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a < b').body[0].value.f.put(Gt(), 0, field='ops', raw=False).src)

        # self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(FST(RShift(), ['>>=']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(And(), ['and'], None), field='op', raw=False)
        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(FST(RShift(), ['>>'], None), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(Invert(), ['~'], None), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(Lt(), ['<'], None), field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Mult(), ['*'], None), field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put(FST(And(), ['and'], None), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Div(), ['/'], None), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Invert(), ['~'], None), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Lt(), ['<'], None), field='op', raw=False)

        self.assertEqual('a * b', parse('a + b').body[0].value.f.put(FST(Mult(), ['*'], None), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(And(), ['and'], None), field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put(FST(RShift(), ['>>'], None), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(Invert(), ['~'], None), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(Lt(), ['<'], None), field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Mult(), ['*'], None), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(And(), ['and'], None), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Sub(), ['-='], None), field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put(FST(UAdd(), ['+'], None), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Lt(), ['-='], None), field='op', raw=False)

        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(Mult(), ['*'], None), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(And(), ['and'], None), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(Sub(), ['-='], None), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(UAdd(), ['-='], None), 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a < b').body[0].value.f.put(FST(Gt(), ['>'], None), 0, field='ops', raw=False).src)

        # make sure alphanumeric operators get the spaces they need

        f = FST('1 or-1')
        f.values[1].op.replace('not')
        self.assertEqual('1 or not 1', f.src)
        f.verify()

        f = FST('a<b')
        f.ops[0].replace('is')
        self.assertEqual('a is b', f.src)
        f.verify()

        f = FST('a<b')
        f.ops[0].replace('is not')
        self.assertEqual('a is not b', f.src)
        f.verify()

        f = FST('a<b')
        f.ops[0].replace('in')
        self.assertEqual('a in b', f.src)
        f.verify()

        f = FST('a<b')
        f.ops[0].replace('not in')
        self.assertEqual('a not in b', f.src)
        f.verify()

        f = FST('1.<b')
        f.ops[0].replace('is')
        self.assertEqual('1. is b', f.src)
        f.verify()

        f = FST('not a')
        f.op.replace('not')
        self.assertEqual('not a', f.src)
        f.verify()

        f = FST('a not in b')
        f.ops[0].replace('not in')
        self.assertEqual('a not in b', f.src)
        f.verify()

        f = FST('1 is-1')  # this one was annoying
        f.comparators[0].op.replace('not')
        self.assertEqual('1 is(not 1)', f.src)
        f.verify()

        f = FST('if(a): pass')
        f.test.replace('b')
        self.assertEqual('if b: pass', f.src)
        f.verify()

        f = FST('if\\\n(a): pass')
        f.test.replace('b')
        self.assertEqual('if\\\nb: pass', f.src)
        f.verify()

        f = FST('if(\\\na): pass')
        f.test.replace('b')
        self.assertEqual('if b: pass', f.src)
        f.verify()

        f = FST('if(a\\\n): pass')
        f.test.replace('b')
        self.assertEqual('if b: pass', f.src)
        f.verify()

        f = FST('a if not f()else c')
        f.test.operand.replace('b')
        self.assertEqual('a if not b else c', f.src)
        f.verify()

        f = FST('a if not f(\n)else c')
        f.test.operand.replace('b')
        self.assertEqual('a if not b else c', f.src)
        f.verify()

        f = FST('a if not f()\\\nelse c')
        f.test.operand.replace('b')
        self.assertEqual('a if not b\\\nelse c', f.src)
        f.verify()

    def test_put_one_op_pars(self):
        # boolop

        f = FST('a or b and c')
        f.op.replace(And())
        self.assertEqual('a and (b and c)', f.src)
        f.verify()

        f = FST('a or (b and c)')
        f.op.replace(And())
        self.assertEqual('a and (b and c)', f.src)
        f.verify()

        f = FST('a or b and c')
        f.values[1].op.replace(Or())
        self.assertEqual('a or (b or c)', f.src)
        f.verify()

        f = FST('a or (b and c)')
        f.values[1].op.replace(Or())
        self.assertEqual('a or (b or c)', f.src)
        f.verify()

        f = FST('a and b or c')
        f.op.replace(And())
        self.assertEqual('(a and b) and c', f.src)
        f.verify()

        f = FST('(a and b) or c')
        f.op.replace(And())
        self.assertEqual('(a and b) and c', f.src)
        f.verify()

        f = FST('a and b or c')
        f.values[0].op.replace(Or())
        self.assertEqual('(a or b) or c', f.src)
        f.verify()

        f = FST('(a and b) or c')
        f.values[0].op.replace(Or())
        self.assertEqual('(a or b) or c', f.src)
        f.verify()

        # operator

        f = FST('a * b + c')
        f.left.op.replace(BitOr())
        self.assertEqual('(a | b) + c', f.src)
        f.verify()

        f = FST('(a * b) + c')
        f.left.op.replace(BitOr())
        self.assertEqual('(a | b) + c', f.src)
        f.verify()

        f = FST('a + b | c + d')
        f.op.replace(Mult())
        self.assertEqual('(a + b) * (c + d)', f.src)
        f.verify()

        f = FST('(a + b) | (c + d)')
        f.op.replace(Mult())
        self.assertEqual('(a + b) * (c + d)', f.src)
        f.verify()

        f = FST('--a')
        f.op.replace(Not())
        self.assertEqual('not-a', f.src)
        f.verify()

        f = FST('--a')
        f.operand.op.replace(Not())
        self.assertEqual('-(not a)', f.src)
        f.verify()

        f = FST('-(-a)')
        f.operand.op.replace(Not())
        self.assertEqual('-(not a)', f.src)
        f.verify()

        f = FST('not not a')
        f.op.replace(USub())
        self.assertEqual('- (not a)', f.src)
        f.verify()

        f = FST('not (not a)')
        f.op.replace(USub())
        self.assertEqual('- (not a)', f.src)
        f.verify()

        f = FST('not not a')
        f.operand.op.replace(USub())
        self.assertEqual('not - a', f.src)
        f.verify()

    def test_put_one_pars(self):
        f = FST('a = b', 'exec').body[0]
        g = FST('(i := j)', 'exec').body[0].value.copy(pars_walrus=False)
        self.assertEqual('i := j', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = i := j')
        f.put(g.copy(), field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = (i := j)')
        f.put(g, field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = (i := j)')

        f = FST('a = b', 'exec').body[0]
        g = FST('("i"\n"j")', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('"i"\n"j"', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = "i"\n"j"')
        f.put(g.copy(), field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = ("i"\n"j")')
        f.put(g, field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = ("i"\n"j")')

        f = FST('a = b', 'exec').body[0]
        g = FST('[i, j]', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('[i, j]', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = [i, j]')
        f.put(g.copy(), field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = [i, j]')
        f.put(g, field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = [i, j]')

        f = FST('a = b', 'exec').body[0]
        g = FST('(i,\nj)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('(i,\nj)', g.src)
        g.unpar(node=True)
        self.assertEqual('i,\nj', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = i,\nj')
        f.put(g.copy(), field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = (i,\nj)')
        f.put(g, field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = (i,\nj)')

        f = FST('a = ( # pre\nb\n# post\n)', 'exec').body[0]
        g = FST('( i )', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('( i )', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = ( # pre\n( i )\n# post\n)')
        f.put(g.copy(), field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = ( i )')
        f.put(g, field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = i')

        # leave needed pars in target

        f = FST('a = ( # pre\nb\n# post\n)', 'exec').body[0]
        g = FST('(1\n+\n2)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('1\n+\n2', g.src)
        f.put(g.copy(), field='value', raw=False, pars=False)
        self.assertEqual(f.src, 'a = ( # pre\n1\n+\n2\n# post\n)')
        f.put(g.copy(), field='value', raw=False, pars=True)
        self.assertEqual(f.src, 'a = ( # pre\n1\n+\n2\n# post\n)')
        f.put(g, field='value', raw=False, pars='auto')
        self.assertEqual(f.src, 'a = ( # pre\n1\n+\n2\n# post\n)')

        # annoying solo MatchValue

        f = FST('match a:\n case (1): pass', 'exec')
        # f.body[0].cases[0].pattern.put('(2)', pars='auto', raw=False)
        # self.assertEqual('match a:\n case ((2)): pass', f.src)
        self.assertRaises(NodeError, f.body[0].cases[0].pattern.put, '(2)', pars='auto', raw=False)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        self.assertRaises(NodeError, f.body[0].cases[0].pattern.put, '(2)', pars=True, raw=False)
        # f.body[0].cases[0].pattern.put('(2)', pars=True, raw=False)
        # self.assertEqual('match a:\n case ((2)): pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        self.assertRaises(NodeError, f.body[0].cases[0].pattern.put, '(2)', pars=False, raw=False)
        # f.body[0].cases[0].pattern.put('(2)', pars=False, raw=False)
        # self.assertEqual('match a:\n case ((2)): pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].put('(2)', field='pattern', pars='auto')
        self.assertEqual('match a:\n case 2: pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].put('(2)', field='pattern', pars=True)
        self.assertEqual('match a:\n case (2): pass', f.src)
        f.verify()

        f = FST('match a:\n case (1): pass', 'exec')
        f.body[0].cases[0].put('(2)', field='pattern', pars=False)
        self.assertEqual('match a:\n case ((2)): pass', f.src)
        f.verify()

        # misc cases

        f = FST('match a:\n case (0 as z) | (1 as z): pass', 'exec')
        g = f.body[0].cases[0].pattern.patterns[0].copy(pars=False)
        f.body[0].cases[0].pattern.put(g, 0, field='patterns', raw=False)
        self.assertEqual('match a:\n case (0 as z) | (1 as z): pass', f.src)

        f = FST('match a:\n case range(10): pass', 'exec')
        g = f.body[0].cases[0].pattern.patterns[0].value.copy(pars=False)
        f.body[0].cases[0].pattern.patterns[0].put(g, None, field='value')
        self.assertEqual('match a:\n case range(10): pass', f.src)

        f = FST('(1).to_bytes(2, "little")', 'exec')
        f.body[0].value.func.put('2', raw=False)
        self.assertEqual('(2).to_bytes(2, "little")', f.src)

        f = FST('(a): int', 'exec')
        f.body[0].put('b', 'target', raw=False, pars='auto')
        self.assertEqual('(b): int', f.src)

        f = FST('(a): int', 'exec')
        f.body[0].put('b', 'target', raw=False, pars=True)
        self.assertEqual('b: int', f.src)

        f = FST('with (\na\n): pass', 'exec')
        g = f.body[0].items[0].copy()
        f.body[0].put(g, 0, 'items')
        self.assertEqual('with (\na\n): pass', f.src)

        f = FST('match a:\n case (1): pass', 'exec')
        self.assertRaises(NodeError, f.body[0].cases[0].pattern.put, '(2)', raw=False)
        # f.body[0].cases[0].pattern.put('(2)', raw=False)
        # self.assertEqual('match a:\n case ((2)): pass', f.src)
        # f.body[0].cases[0].pattern.put('(3)', pars=True)

    def test_put_one_pars_need_matrix(self):
        # pars=True, needed for precedence, needed for parse, present in dst, present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n+\ny # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# src\nx\n+\ny # src\n)', f.root.src)

        # pars=True, needed for precedence, needed for parse, present in dst, not present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n+\ny', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# dst\nx\n+\ny # dst\n)', f.root.src)

        # pars=True, needed for precedence, needed for parse, not present in dst, present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n+\ny # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# src\nx\n+\ny # src\n)', f.root.src)

        # pars=True, needed for precedence, needed for parse, not present in dst, not present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n+\ny', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (x\n+\ny)', f.root.src)

        # pars=True, needed for precedence, not needed for parse, present in dst, present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx + y # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# src\nx + y # src\n)', f.root.src)

        # pars=True, needed for precedence, not needed for parse, present in dst, not present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x + y', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# dst\nx + y # dst\n)', f.root.src)

        # pars=True, needed for precedence, not needed for parse, not present in dst, present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx + y # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (# src\nx + y # src\n)', f.root.src)

        # pars=True, needed for precedence, not needed for parse, not present in dst, not present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x + y', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i * (x + y)', f.root.src)

        # pars=True, not needed for precedence, needed for parse, present in dst, present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n*\ny # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# src\nx\n*\ny # src\n)', f.root.src)

        # pars=True, not needed for precedence, needed for parse, present in dst, not present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n*\ny', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# dst\nx\n*\ny # dst\n)', f.root.src)

        # pars=True, not needed for precedence, needed for parse, not present in dst, present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n*\ny # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# src\nx\n*\ny # src\n)', f.root.src)

        # pars=True, not needed for precedence, needed for parse, not present in dst, not present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n*\ny', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (x\n*\ny)', f.root.src)

        # pars=True, not needed for precedence, not needed for parse, present in dst, present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx * y # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# src\nx * y # src\n)', f.root.src)

        # pars=True, not needed for precedence, not needed for parse, present in dst, not present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x * y', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + x * y', f.root.src)

        # pars=True, not needed for precedence, not needed for parse, not present in dst, present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx * y # src\n)', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + (# src\nx * y # src\n)', f.root.src)

        # pars=True, not needed for precedence, not needed for parse, not present in dst, not present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x * y', g.src)
        f.put(g, field='right', pars=True)
        self.assertEqual('i + x * y', f.root.src)

        # pars='auto', needed for precedence, needed for parse, present in dst, present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n+\ny # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# src\nx\n+\ny # src\n)', f.root.src)

        # pars='auto', needed for precedence, needed for parse, present in dst, not present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n+\ny', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# dst\nx\n+\ny # dst\n)', f.root.src)

        # pars='auto', needed for precedence, needed for parse, not present in dst, present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n+\ny # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# src\nx\n+\ny # src\n)', f.root.src)

        # pars='auto', needed for precedence, needed for parse, not present in dst, not present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx\n+\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n+\ny', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (x\n+\ny)', f.root.src)

        # pars='auto', needed for precedence, not needed for parse, present in dst, present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx + y # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# src\nx + y # src\n)', f.root.src)

        # pars='auto', needed for precedence, not needed for parse, present in dst, not present in src
        f = FST('i * (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x + y', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# dst\nx + y # dst\n)', f.root.src)

        # pars='auto', needed for precedence, not needed for parse, not present in dst, present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx + y # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (# src\nx + y # src\n)', f.root.src)

        # pars='auto', needed for precedence, not needed for parse, not present in dst, not present in src
        f = FST('i * j', 'exec').body[0].value
        g = FST('(# src\nx + y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x + y', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i * (x + y)', f.root.src)

        # pars='auto', not needed for precedence, needed for parse, present in dst, present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n*\ny # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + (# src\nx\n*\ny # src\n)', f.root.src)

        # pars='auto', not needed for precedence, needed for parse, present in dst, not present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n*\ny', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + (# dst\nx\n*\ny # dst\n)', f.root.src)

        # pars='auto', not needed for precedence, needed for parse, not present in dst, present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx\n*\ny # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + (# src\nx\n*\ny # src\n)', f.root.src)

        # pars='auto', not needed for precedence, needed for parse, not present in dst, not present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx\n*\ny # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x\n*\ny', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + (x\n*\ny)', f.root.src)

        # pars='auto', not needed for precedence, not needed for parse, present in dst, present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx * y # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + x * y', f.root.src)

        # pars='auto', not needed for precedence, not needed for parse, present in dst, not present in src
        f = FST('i + (# dst\nj # dst\n)', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x * y', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + x * y', f.root.src)

        # pars='auto', not needed for precedence, not needed for parse, not present in dst, present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=True)
        self.assertEqual('(# src\nx * y # src\n)', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + x * y', f.root.src)

        # pars='auto', not needed for precedence, not needed for parse, not present in dst, not present in src
        f = FST('i + j', 'exec').body[0].value
        g = FST('(# src\nx * y # src\n)', 'exec').body[0].value.copy(pars=False)
        self.assertEqual('x * y', g.src)
        f.put(g, field='right', pars='auto')
        self.assertEqual('i + x * y', f.root.src)

    def test_put_one_negative_idx(self):
        FST('{**b}').put('a', -1, 'keys')

    def test__put_one_virtual_field(self):
        # Dict return child

        child = (self_ := FST('{a: b, c: d, e: f}', 'exec').body[0].value)._put_one(None, 1, '_all', {'raw': False}, True)
        self.assertIsNone(child)
        self.assertIsNotNone(self_.a)  # .a will be None if deleted
        self.assertEqual('{a: b, e: f}', self_.src)

        self.assertRaises(ValueError, FST('{a: b, c: d, e: f}')._put_one, None, 1, '_all', {'raw': True}, True)
        self.assertRaises(ValueError, FST('{a: b, c: d, e: f}')._put_one, 'x: y', 1, '_all', {'raw': False}, True)

        child = (self_ := FST('{a: b, c: d, e: f}', 'exec').body[0].value)._put_one('x: y', 1, '_all', {'raw': True}, True)
        self.assertIsNone(child)
        self.assertIsNone(self_.a)
        self.assertEqual('{a: b, x: y, e: f}', self_.repath().src)

        # Dict return self

        new_self = (self_ := FST('{a: b, c: d, e: f}', 'exec').body[0].value)._put_one(None, 1, '_all', {'raw': False}, False)
        self.assertIs(new_self, self_)
        self.assertIsNotNone(self_.a)
        self.assertEqual('{a: b, e: f}', self_.src)

        self.assertRaises(ValueError, FST('{a: b, c: d, e: f}')._put_one, None, 1, '_all', {'raw': True}, False)
        self.assertRaises(ValueError, FST('{a: b, c: d, e: f}')._put_one, 'x: y', 1, '_all', {'raw': False}, False)

        new_self = (self_ := FST('{a: b, c: d, e: f}', 'exec').body[0].value)._put_one('x: y', 1, '_all', {'raw': True}, False)
        self.assertIsNot(new_self, self)
        self.assertIsNone(self_.a)
        self.assertEqual('{a: b, x: y, e: f}', new_self.src)

        # MatchMapping return child

        child = (self_ := FST('case {1: a, 2: b, 3: c}: pass', 'match_case')).pattern._put_one(None, 1, '_all', {'raw': False}, True)
        self.assertIsNone(child)
        self.assertIsNotNone(self_.a)
        self.assertEqual('case {1: a, 3: c}: pass', self_.src)

        self.assertRaises(ValueError, FST('case {1: a, 2: b, 3: c}: pass').pattern._put_one, None, 1, '_all', {'raw': True}, True)
        self.assertRaises(ValueError, FST('case {1: a, 2: b, 3: c}: pass').pattern._put_one, '4: x', 1, '_all', {'raw': False}, True)

        self_ = FST('case {1: a, 2: b, 3: c}: pass', 'match_case')
        ast = self_.a
        child = self_.pattern._put_one('4: x', 1, '_all', {'raw': True}, True)
        self.assertIsNone(child)
        self.assertIsNot(self_.a, ast)
        self.assertEqual('case {1: a, 4: x, 3: c}: pass', self_.repath().src)

        # MatchMapping return self

        new_pat = (old_pat := (self_ := FST('case {1: a, 2: b, 3: c}: pass', 'match_case')).pattern)._put_one(None, 1, '_all', {'raw': False}, False)
        self.assertIs(new_pat, old_pat)
        self.assertIsNotNone(self_.a)
        self.assertEqual('case {1: a, 3: c}: pass', self_.src)

        self.assertRaises(ValueError, FST('case {1: a, 2: b, 3: c}: pass').pattern._put_one, None, 1, '_all', {'raw': True}, False)
        self.assertRaises(ValueError, FST('case {1: a, 2: b, 3: c}: pass').pattern._put_one, '4: x', 1, '_all', {'raw': False}, False)


        new_pat = (old_pat := (self_ := FST('case {1: a, 2: b, 3: c}: pass', 'match_case')).pattern)._put_one('4: x', 1, '_all', {'raw': True}, False)
        self.assertIsNot(new_pat, old_pat)
        self.assertIsNotNone(self_.a)
        self.assertEqual('case {1: a, 4: x, 3: c}: pass', self_.src)

        # MatchMapping return child

        child = (self_ := FST('match _:\n case {1: a, 2: b, 3: c}: pass', 'Match').cases[0]).pattern._put_one(None, 1, '_all', {'raw': False}, True)
        self.assertIsNone(child)
        self.assertIsNotNone(self_.a)
        self.assertEqual('case {1: a, 3: c}: pass', self_.src)

        self.assertRaises(ValueError, FST('match _:\n case {1: a, 2: b, 3: c}: pass').cases[0].pattern._put_one, None, 1, '_all', {'raw': True}, True)
        self.assertRaises(ValueError, FST('match _:\n case {1: a, 2: b, 3: c}: pass').cases[0].pattern._put_one, '4: x', 1, '_all', {'raw': False}, True)

        child = (self_ := FST('match _:\n case {1: a, 2: b, 3: c}: pass', 'Match').cases[0]).pattern._put_one('4: x', 1, '_all', {'raw': True}, True)
        self.assertIsNone(child)
        self.assertIsNotNone(self_.a)
        self.assertEqual('case {1: a, 4: x, 3: c}: pass', self_.repath().src)

        # MatchMapping return self

        new_pat = (old_pat := (self_ := FST('match _:\n case {1: a, 2: b, 3: c}: pass', 'Match').cases[0]).pattern)._put_one(None, 1, '_all', {'raw': False}, False)
        self.assertIs(new_pat, old_pat)
        self.assertIsNotNone(self_.a)
        self.assertEqual('case {1: a, 3: c}: pass', self_.src)

        self.assertRaises(ValueError, FST('match _:\n case {1: a, 2: b, 3: c}: pass').cases[0].pattern._put_one, None, 1, '_all', {'raw': True}, False)
        self.assertRaises(ValueError, FST('match _:\n case {1: a, 2: b, 3: c}: pass').cases[0].pattern._put_one, '4: x', 1, '_all', {'raw': False}, False)

        new_pat = (old_pat := (self_ := FST('match _:\n case {1: a, 2: b, 3: c}: pass', 'Match').cases[0]).pattern)._put_one('4: x', 1, '_all', {'raw': True}, False)
        self.assertIsNot(new_pat, old_pat)
        self.assertIsNotNone(self_.a)
        self.assertEqual('case {1: a, 4: x, 3: c}: pass', self_.src)

        # Compare return child left

        child = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one(None, 0, '_all', {'raw': False}, True)
        self.assertIsNone(child)
        self.assertIsNotNone(self_.a)
        self.assertEqual('b > c', self_.src)

        self.assertRaises(ValueError, FST('a < b > c')._put_one, None, 0, '_all', {'raw': True}, True)

        child = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one('x', 0, '_all', {'raw': False}, True)
        self.assertIsNotNone(child)
        self.assertIsNotNone(self_.a)
        self.assertIs(child.a, self_.a.left)
        self.assertIs(child, self_.a.left.f)
        self.assertEqual('x < b > c', self_.src)

        child = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one('x', 0, '_all', {'raw': True}, True)
        self.assertIsNotNone(child)
        self.assertIsNone(self_.a)
        self_ = self_.repath()
        self.assertIs(child.a, self_.a.left)
        self.assertIs(child, self_.a.left.f)
        self.assertEqual('x < b > c', self_.src)

        # Compare return child comparator

        child = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one(None, 1, '_all', {'raw': False}, True)
        self.assertIsNone(child)
        self.assertIsNotNone(self_.a)
        self.assertEqual('a > c', self_.src)

        self.assertRaises(ValueError, FST('a < b > c')._put_one, None, 1, '_all', {'raw': True}, True)

        child = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one('x', 1, '_all', {'raw': False}, True)
        self.assertIsNotNone(child)
        self.assertIsNotNone(self_.a)
        self.assertIs(child.a, self_.a.comparators[0])
        self.assertIs(child, self_.a.comparators[0].f)
        self.assertEqual('a < x > c', self_.src)

        child = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one('x', 1, '_all', {'raw': True}, True)
        self.assertIsNotNone(child)
        self.assertIsNone(self_.a)
        self_ = self_.repath()
        self.assertIs(child.a, self_.a.comparators[0])
        self.assertIs(child, self_.a.comparators[0].f)
        self.assertEqual('a < x > c', self_.src)

        # Compare return self

        new_self = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one(None, 0, '_all', {'raw': False}, False)
        self.assertIs(new_self, self_)
        self.assertIsNotNone(self_.a)
        self.assertEqual('b > c', self_.src)

        self.assertRaises(ValueError, FST('a < b > c')._put_one, None, 0, '_all', {'raw': True}, False)

        new_self = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one('x', 0, '_all', {'raw': False}, False)
        self.assertIs(new_self, self_)
        self.assertIsNotNone(self_.a)
        self.assertEqual('x < b > c', self_.src)

        new_self = (self_ := FST('a < b > c', 'exec').body[0].value)._put_one('x', 0, '_all', {'raw': True}, False)
        self.assertIsNot(new_self, self)
        self.assertIsNone(self_.a)
        self.assertEqual('x < b > c', new_self.src)

    def test_put_default_non_list_field(self):
        self.assertEqual('y', parse('n').body[0].f.put('y').root.src)  # Expr
        self.assertEqual('return y', parse('return n').body[0].f.put('y').root.src)  # Return
        self.assertEqual('await y', parse('await n').body[0].value.f.put('y').root.src)  # Await
        self.assertEqual('yield y', parse('yield n').body[0].value.f.put('y').root.src)  # Yield
        self.assertEqual('yield from y', parse('yield from n').body[0].value.f.put('y').root.src)  # YieldFrom
        self.assertEqual('[*y]', parse('[*n]').body[0].value.elts[0].f.put('y').root.src)  # Starred
        self.assertEqual('match a:\n case "y": pass', parse('match a:\n case "n": pass').body[0].cases[0].pattern.f.put('"y"').root.src)  # MatchValue

    def test_put_disallow_ouroboros(self):
        f = FST('i := j')
        self.assertRaises(ValueError, f.value.replace, f)

        f = FST('[1, 2]')
        self.assertRaises(ValueError, f.elts.append, f)

    def test_put_one_raw(self):
        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.put('for x in y', 1, 'generators', raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d for x in y for a in b]')
        f = g
        # g = f.put(None, 1, raw=True)
        # self.assertIsNot(g, f)
        # self.assertEqual(g.src, '[a for c in d  for a in b]')
        # f = g
        # g = f.put(None, 1, raw=True)
        # self.assertIsNot(g, f)
        # self.assertEqual(g.src, '[a for c in d  ]')
        # f = g

        f = parse('try:pass\nfinally: pass').body[0].f
        g = f.put('break', 0, raw=True)
        self.assertIs(g, f)
        self.assertEqual(g.src, 'try:break\nfinally: pass')

        f = parse('try: pass\nexcept: pass').body[0].handlers[0].f
        g = f.put('break', 0, raw=True)
        self.assertIs(g, f)
        self.assertEqual(g.src, 'except: break')

        f = parse('match a:\n case 1: pass').body[0].cases[0].f
        g = f.put('break', 0, raw=True)
        self.assertIs(g, f)
        self.assertEqual(g.src, 'case 1: break')

        self.assertEqual('y', parse('n', mode='eval').f.put('y', field='body', raw=True).root.src)  # Expression.body

        # make sure we can't put TO location behind self

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertEqual('[1, 4]', f.elts[1].replace('4', to=f.elts[2], raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertRaises(ValueError, f.elts[1].replace, '4', to=f.elts[0], raw=True)

        f = parse('a = b').body[0].f
        self.assertEqual('c', f.targets[0].replace('c', to=f.value, raw=True).root.src)

        f = parse('a = b').body[0].f
        self.assertRaises(ValueError, f.value.replace, 'c', to=f.targets[0], raw=True)

        # make sure replace returns appropriate node

        # self.assertIsNone(FST('def f() -> int: pass').returns.replace(None, raw=True))
        self.assertEqual('str', FST('def f() -> int: pass').returns.replace('str', raw=True).src)

        # special None fields of Dict, MatchMapping and Compare

        self.assertEqual('{1: 2, 7: 8}', (f := FST('{1: 2, 3: 4, 5: 6}')).put('7: 8', 1, raw=True, to=f.values[-1]).root.src)
        self.assertEqual('{1: 2, 7: 8}', (f := FST('{1: 2, 3: 4, 5: 6}', pattern)).put('7: 8', 1, raw=True, to=f.patterns[-1]).root.src)
        self.assertEqual('a < x > z', (f := FST('a < b < c')).put('x > z', 1, raw=True, to=f.comparators[-1]).root.src)

        # field disappears

        self.assertIsNone(FST('a + b').op.replace(',', raw=True))

        # replace try header (nothing there to replace)

        f = FST('try: pass\nexcept: pass')
        f.put_src('try', 0, 0, 0, 3)
        self.assertEqual('try: pass\nexcept: pass', f.src)
        f.verify()

        if PYGE11:
            f = FST('try: pass\nexcept* Exception: pass')
            f.put_src('try', 0, 0, 0, 3)
            self.assertEqual('try: pass\nexcept* Exception: pass', f.src)
            f.verify()

        # misc

        self.assertRaises(ValueError, FST('a + b').put, 'x', 'right', raw=True, to=FST('DIFFERENT_TREE'))  # `to` a node in a different tree

        self.assertRaises(ValueError, (f := FST('a = b and c')).put, 'x or', 0, 'targets', raw=True, to=f.value.op)  # `to` a node without a location

        self.assertEqual('x, lambda y: None', (f := FST('a = lambda: None')).put('x, lambda y', 0, 'targets', raw=True, to=f.value.args).root.src)  # `to` empty arguments
        f.verify()

        self.assertEqual('x, (y)', (f := FST('a = f(i for i in j)')).put('x, (y', 0, 'targets', raw=True, to=f.value.args[0]).root.src)  # `to` GeneratorExp Call arg with shared parentheses
        f.verify()
        self.assertEqual('x, (y)', (f := FST('a = f(i for i in j)')).put('x, (y', 0, 'targets', raw=True, pars=False, to=f.value.args[0]).root.src)  # `to` GeneratorExp Call arg with shared parentheses
        f.verify()

        self.assertIsNone((f := FST('a\nb')).body[1].replace('', raw=True))
        f.verify()

    def test_replace_raw_non_mod_stmt_root(self):
        f = FST('call(a, *b, **c)')
        f.args[0].replace('d', to=f.keywords[-1], raw=True)
        self.assertEqual('call(d)', f.src)
        self.assertIsInstance(f.a, Call)
        f.verify()

        f = FST('1, 2')
        f.elts[0].replace('d', to=f.elts[-1], raw=True)
        self.assertEqual('d', f.src)
        self.assertIsInstance(f.a, Name)
        f.verify()

        f = FST('for i in range(-5, 5) if i', 'all')
        f.iter.args[0].replace('99', to=f.iter.args[-1], raw=True)
        self.assertEqual('for i in range(99) if i', f.src)
        self.assertIsInstance(f.a, comprehension)
        f.verify()

        f = FST('1 * 1', 'all')
        f.left.replace('+', to=f.right, raw=True)
        self.assertEqual('+', f.src)
        self.assertIsInstance(f.a, Add)
        f.verify()

    def test_unparenthesized_tuple_put_as_one(self):
        f = parse('(1, 2, 3)').body[0].value.f
        f.put('a, b', 1)
        self.assertEqual('(1, (a, b), 3)', f.src)

    def test_modify_parent_fmtvals_and_interpolations(self):
        if PYGE12:
            f = FST('f"{a=}"')
            f.values[-1].value.replace('b')
            self.assertEqual('b=', f.values[0].value)
            f.verify()

            f = FST('f"c{a=}"')
            f.values[-1].value.replace('b')
            self.assertEqual('cb=', f.values[0].value)
            f.verify()

            f = FST('''f"""c
{
# 1
a
# 2
=
# 3
!r:0.5f<5}"""''')
            f.values[-1].value.replace('b')
            self.assertEqual('c\n\n\nb\n\n=\n\n', f.values[0].value)
            f.verify()

            f = FST('''f"""c
{
# 1
f'd{f"e{f=!s:0.1f<1}"=}'
# 2
=
# 3
!r:0.5f<5}"""''')
            f.values[-1].value.values[-1].value.values[-1].value.replace('z')
            self.assertEqual('ez=', f.values[-1].value.values[-1].value.values[0].value)
            self.assertEqual('df"e{z=!s:0.1f<1}"=', f.values[-1].value.values[0].value)
            self.assertEqual('c\n\n\nf\'d{f"e{z=!s:0.1f<1}"=}\'\n\n=\n\n', f.values[0].value)
            f.verify()

        if PYGE14:
            f = FST('''t"""c
{
# 1
f'd{t"e{f=!s:0.1f<1}"=}'
# 2
=
# 3
!r:0.5f<5}"""''')
            f.values[-1].value.values[-1].value.values[-1].value.replace('z')
            self.assertEqual('ez=', f.values[-1].value.values[-1].value.values[0].value)
            self.assertEqual('z', f.values[-1].value.values[-1].value.values[-1].str)
            self.assertEqual('dt"e{z=!s:0.1f<1}"=', f.values[-1].value.values[0].value)
            self.assertEqual('c\n\n\nf\'d{t"e{z=!s:0.1f<1}"=}\'\n\n=\n\n', f.values[0].value)
            self.assertEqual('\n\nf\'d{t"e{z=!s:0.1f<1}"=}\'', f.values[-1].str)
            f.verify()

    def test_ctx_change(self):
        a = parse('a, b = x, y').body[0]
        a.targets[0].f.put(a.value.f.get())
        self.assertEqual('(x, y), = x, y', a.f.src)
        self.assertIsInstance(a.targets[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[0].elts[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[0].elts[1].ctx, Store)

        a = parse('a, b = x, y').body[0]
        a.value.f.put(a.targets[0].f.get())
        self.assertEqual('a, b = (a, b),', a.f.src)
        self.assertIsInstance(a.value.ctx, Load)
        self.assertIsInstance(a.value.elts[0].ctx, Load)
        self.assertIsInstance(a.value.elts[0].elts[0].ctx, Load)
        self.assertIsInstance(a.value.elts[0].elts[1].ctx, Load)

        a = parse('a, b = x, y').body[0]
        a.targets[0].f.put_slice(a.value.f.get())
        self.assertEqual('x, y = x, y', a.f.src)
        self.assertIsInstance(a.targets[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[0].ctx, Store)
        self.assertIsInstance(a.targets[0].elts[1].ctx, Store)

        a = parse('a, b = x, y').body[0]
        a.value.f.put_slice(a.targets[0].f.get())
        self.assertEqual('a, b = a, b', a.f.src)
        self.assertIsInstance(a.value.ctx, Load)
        self.assertIsInstance(a.value.elts[0].ctx, Load)
        self.assertIsInstance(a.value.elts[1].ctx, Load)

    def test_one_coverage(self):
        # misc stuff to fill out test coverage

        from fst.fst_put_one import _validate_put
        self.assertRaises(IndexError, _validate_put, f := FST('a, b'), None, None, 'elts', f.a.elts)
        self.assertRaises(IndexError, _validate_put, f := FST('a = 1'), None, 0, 'value', f.a.value)

        self.assertRaises(ValueError, (f := FST('a + b')).put, 'z', 'left', raw=True, to=f.a.right)

        self.assertRaises(NodeError, FST('def f(): pass').put, 'x', 'type_comment')

        from fst.fst_put_one import _put_one_raw
        self.assertEqual('{x: y}', _put_one_raw(FST('{a: b}'), 'x: y', 0, '_all', [], None, {}).root.src)

        # misc

        f = FST('i = 1')
        self.assertRaises(ValueError, f.value.replace, 'i, j', one=False)
        self.assertRaises(ValueError, f.remove)
        self.assertRaises(ValueError, f.get_slice, 'value')
        self.assertRaises(ValueError, f.put_slice, 'a, b', 'value')

        from fst.fst_get_one import _validate_get
        self.assertRaises(IndexError, _validate_get, FST('i = j'), 1, 'value')
        self.assertRaises(IndexError, _validate_get, FST('[0, 1]'), None, 'elts')

        from fst.fst_get_one import _get_one_default
        self.assertRaises(ValueError, _get_one_default, FST('i'), None, 'ctx', False, {})


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-get-one', default=False, action='store_true', help="regenerate get one test data")
    parser.add_argument('--regen-put-one', default=False, action='store_true', help="regenerate put one test data")

    args, _ = parser.parse_known_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT12:
            raise RuntimeError('cannot regenerate on python version < 3.12')

    if args.regen_get_one or args.regen_all:
        print('Regenerating get one test data...')
        regen_get_one()

    if args.regen_put_one or args.regen_all:
        print('Regenerating put one test data...')
        regen_put_one()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
