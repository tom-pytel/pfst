#!/usr/bin/env python

import unittest
from ast import AST
from itertools import combinations

from fst import *
from fst import FST, parse

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

from fst.common import (
    PYGE11,
    PYGE12,
    PYGE13,
    PYGE14,
    PYGE15,
)

from support import assertRaises


def walkscope(fst_or_list, back=False, all=False):
    if isinstance(fst_or_list, FST):
        fst_or_list = fst_or_list.walk(all, scope=True, back=back)

    return '\n'.join(f'{str(f):<32} {f.src or "."}' for f in fst_or_list)


class TestTraverse(unittest.TestCase):
    """Traversal."""

    maxDiff = None

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

    def test_walk_scope_Comp_first_iter(self):
        # Comprehension first generator iterator, this is a real pain

        f = FST('[_ for _ in (lambda: b) for _ in (lambda: c)]')

        self.assertEqual(walkscope(f, all=True), '''
<ListComp ROOT 0,0..0,45>        [_ for _ in (lambda: b) for _ in (lambda: c)]
<Name 0,1..0,2>                  _
<Load>                           .
<comprehension 0,3..0,23>        for _ in (lambda: b)
<Name 0,7..0,8>                  _
<Store>                          .
<comprehension 0,24..0,44>       for _ in (lambda: c)
<Name 0,28..0,29>                _
<Store>                          .
<Lambda 0,34..0,43>              lambda: c
            '''.strip())

        l = []
        for g in (gen := f.walk(True, scope=True)):
            l.append(g)
            if g.is_Lambda:
                gen.send(True)  # recurse into Lambda in first generator iterator
        self.assertEqual(walkscope(l), '''
<ListComp ROOT 0,0..0,45>        [_ for _ in (lambda: b) for _ in (lambda: c)]
<Name 0,1..0,2>                  _
<Load>                           .
<comprehension 0,3..0,23>        for _ in (lambda: b)
<Name 0,7..0,8>                  _
<Store>                          .
<comprehension 0,24..0,44>       for _ in (lambda: c)
<Name 0,28..0,29>                _
<Store>                          .
<Lambda 0,34..0,43>              lambda: c
<arguments 0,40..0,40>           .
<Name 0,42..0,43>                c
<Load>                           .
            '''.strip())

        f = FST('[_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]')

        self.assertEqual(walkscope(f, all=True), '''
<ListComp ROOT 0,0..0,63>        [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<Name 0,1..0,2>                  _
<Load>                           .
<comprehension 0,3..0,32>        for b in (lambda c=1, d=2: c)
<Name 0,7..0,8>                  b
<Store>                          .
<comprehension 0,33..0,62>       for e in (lambda f=3, g=4: f)
<Name 0,37..0,38>                e
<Store>                          .
<Lambda 0,43..0,61>              lambda f=3, g=4: f
<Constant 0,52..0,53>            3
<Constant 0,57..0,58>            4
            '''.strip())

        self.assertEqual(walkscope(f, back=True, all=True), '''
<ListComp ROOT 0,0..0,63>        [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<comprehension 0,33..0,62>       for e in (lambda f=3, g=4: f)
<Lambda 0,43..0,61>              lambda f=3, g=4: f
<Constant 0,57..0,58>            4
<Constant 0,52..0,53>            3
<Name 0,37..0,38>                e
<Store>                          .
<comprehension 0,3..0,32>        for b in (lambda c=1, d=2: c)
<Name 0,7..0,8>                  b
<Store>                          .
<Name 0,1..0,2>                  _
<Load>                           .
            '''.strip())

        l = []
        for g in (gen := f.walk(all=True, scope=True)):
            l.append(g)
            if g.is_Lambda:
                gen.send(True)  # recurse into Lambda in second generator iterator (second because scope is the ListComp)
        self.assertEqual(walkscope(l), '''
<ListComp ROOT 0,0..0,63>        [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<Name 0,1..0,2>                  _
<Load>                           .
<comprehension 0,3..0,32>        for b in (lambda c=1, d=2: c)
<Name 0,7..0,8>                  b
<Store>                          .
<comprehension 0,33..0,62>       for e in (lambda f=3, g=4: f)
<Name 0,37..0,38>                e
<Store>                          .
<Lambda 0,43..0,61>              lambda f=3, g=4: f
<arguments 0,50..0,58>           f=3, g=4
<arg 0,50..0,51>                 f
<Constant 0,52..0,53>            3
<arg 0,55..0,56>                 g
<Constant 0,57..0,58>            4
<Name 0,60..0,61>                f
<Load>                           .
            '''.strip())

        l = []
        for g in (gen := f.walk(all=True, scope=True, back=True)):
            l.append(g)
            if g.is_Lambda:
                gen.send(True)  # recurse into Lambda in second generator iterator (second because scope is the ListComp)
        self.assertEqual(walkscope(l), '''
<ListComp ROOT 0,0..0,63>        [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<comprehension 0,33..0,62>       for e in (lambda f=3, g=4: f)
<Lambda 0,43..0,61>              lambda f=3, g=4: f
<Name 0,60..0,61>                f
<Load>                           .
<arguments 0,50..0,58>           f=3, g=4
<Constant 0,57..0,58>            4
<arg 0,55..0,56>                 g
<Constant 0,52..0,53>            3
<arg 0,50..0,51>                 f
<Name 0,37..0,38>                e
<Store>                          .
<comprehension 0,3..0,32>        for b in (lambda c=1, d=2: c)
<Name 0,7..0,8>                  b
<Store>                          .
<Name 0,1..0,2>                  _
<Load>                           .
            '''.strip())

        f = FST('a = [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]')

        self.assertEqual(walkscope(f, all=True), '''
<Assign ROOT 0,0..0,67>          a = [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<Name 0,0..0,1>                  a
<Store>                          .
<ListComp 0,4..0,67>             [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<Lambda 0,17..0,35>              lambda c=1, d=2: c
<Constant 0,26..0,27>            1
<Constant 0,31..0,32>            2
            '''.strip())

        f = FST('a = [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]')

        self.assertEqual(walkscope(f, all=True, back=True), '''
<Assign ROOT 0,0..0,67>          a = [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<ListComp 0,4..0,67>             [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<Lambda 0,17..0,35>              lambda c=1, d=2: c
<Constant 0,31..0,32>            2
<Constant 0,26..0,27>            1
<Name 0,0..0,1>                  a
<Store>                          .
            '''.strip())

        l = []
        for g in (gen := f.walk(all=True, scope=True)):
            l.append(g)
            if g.is_Lambda:
                gen.send(True)  # recurse into Lambda in first generator iterator (first because scope is outside the ListComp)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,67>          a = [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<Name 0,0..0,1>                  a
<Store>                          .
<ListComp 0,4..0,67>             [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<Lambda 0,17..0,35>              lambda c=1, d=2: c
<arguments 0,24..0,32>           c=1, d=2
<arg 0,24..0,25>                 c
<Constant 0,26..0,27>            1
<arg 0,29..0,30>                 d
<Constant 0,31..0,32>            2
<Name 0,34..0,35>                c
<Load>                           .
            '''.strip())

        l = []
        for g in (gen := f.walk(all=True, scope=True, back=True)):
            l.append(g)
            if g.is_Lambda:
                gen.send(True)  # recurse into Lambda in first generator iterator (first because scope is outside the ListComp)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,67>          a = [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<ListComp 0,4..0,67>             [_ for b in (lambda c=1, d=2: c) for e in (lambda f=3, g=4: f)]
<Lambda 0,17..0,35>              lambda c=1, d=2: c
<Name 0,34..0,35>                c
<Load>                           .
<arguments 0,24..0,32>           c=1, d=2
<Constant 0,31..0,32>            2
<arg 0,29..0,30>                 d
<Constant 0,26..0,27>            1
<arg 0,24..0,25>                 c
<Name 0,0..0,1>                  a
<Store>                          .
            '''.strip())

        f = FST('[_ for b in [c for d in e] for f in [g for h in i]]')

        self.assertEqual(walkscope(f), '''
<ListComp ROOT 0,0..0,51>        [_ for b in [c for d in e] for f in [g for h in i]]
<Name 0,1..0,2>                  _
<comprehension 0,3..0,26>        for b in [c for d in e]
<Name 0,7..0,8>                  b
<comprehension 0,27..0,50>       for f in [g for h in i]
<Name 0,31..0,32>                f
<ListComp 0,36..0,50>            [g for h in i]
<Name 0,48..0,49>                i
            '''.strip())

        self.assertEqual(walkscope(f, back=True), '''
<ListComp ROOT 0,0..0,51>        [_ for b in [c for d in e] for f in [g for h in i]]
<comprehension 0,27..0,50>       for f in [g for h in i]
<ListComp 0,36..0,50>            [g for h in i]
<Name 0,48..0,49>                i
<Name 0,31..0,32>                f
<comprehension 0,3..0,26>        for b in [c for d in e]
<Name 0,7..0,8>                  b
<Name 0,1..0,2>                  _
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True)):
            l.append(g)
            if g.is_ListComp:
                gen.send(True)
        self.assertEqual(walkscope(l), '''
<ListComp ROOT 0,0..0,51>        [_ for b in [c for d in e] for f in [g for h in i]]
<Name 0,1..0,2>                  _
<comprehension 0,3..0,26>        for b in [c for d in e]
<Name 0,7..0,8>                  b
<ListComp 0,12..0,26>            [c for d in e]
<Name 0,13..0,14>                c
<comprehension 0,15..0,25>       for d in e
<Name 0,19..0,20>                d
<Name 0,24..0,25>                e
<comprehension 0,27..0,50>       for f in [g for h in i]
<Name 0,31..0,32>                f
<ListComp 0,36..0,50>            [g for h in i]
<Name 0,37..0,38>                g
<comprehension 0,39..0,49>       for h in i
<Name 0,43..0,44>                h
<Name 0,48..0,49>                i
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True, back=True)):
            l.append(g)
            if g.is_ListComp:
                gen.send(True)
        self.assertEqual(walkscope(l), '''
<ListComp ROOT 0,0..0,51>        [_ for b in [c for d in e] for f in [g for h in i]]
<comprehension 0,27..0,50>       for f in [g for h in i]
<ListComp 0,36..0,50>            [g for h in i]
<comprehension 0,39..0,49>       for h in i
<Name 0,48..0,49>                i
<Name 0,43..0,44>                h
<Name 0,37..0,38>                g
<Name 0,31..0,32>                f
<comprehension 0,3..0,26>        for b in [c for d in e]
<ListComp 0,12..0,26>            [c for d in e]
<comprehension 0,15..0,25>       for d in e
<Name 0,24..0,25>                e
<Name 0,19..0,20>                d
<Name 0,13..0,14>                c
<Name 0,7..0,8>                  b
<Name 0,1..0,2>                  _
            '''.strip())

        f = FST('a = [_ for b in [c for d in e] for f in [g for h in i]]')

        self.assertEqual(walkscope(f), '''
<Assign ROOT 0,0..0,55>          a = [_ for b in [c for d in e] for f in [g for h in i]]
<Name 0,0..0,1>                  a
<ListComp 0,4..0,55>             [_ for b in [c for d in e] for f in [g for h in i]]
<ListComp 0,16..0,30>            [c for d in e]
<Name 0,28..0,29>                e
            '''.strip())

        self.assertEqual(walkscope(f, back=True), '''
<Assign ROOT 0,0..0,55>          a = [_ for b in [c for d in e] for f in [g for h in i]]
<ListComp 0,4..0,55>             [_ for b in [c for d in e] for f in [g for h in i]]
<ListComp 0,16..0,30>            [c for d in e]
<Name 0,28..0,29>                e
<Name 0,0..0,1>                  a
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True)):
            l.append(g)
            if g.is_ListComp:
                gen.send(True)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,55>          a = [_ for b in [c for d in e] for f in [g for h in i]]
<Name 0,0..0,1>                  a
<ListComp 0,4..0,55>             [_ for b in [c for d in e] for f in [g for h in i]]
<Name 0,5..0,6>                  _
<comprehension 0,7..0,30>        for b in [c for d in e]
<Name 0,11..0,12>                b
<ListComp 0,16..0,30>            [c for d in e]
<Name 0,17..0,18>                c
<comprehension 0,19..0,29>       for d in e
<Name 0,23..0,24>                d
<Name 0,28..0,29>                e
<comprehension 0,31..0,54>       for f in [g for h in i]
<Name 0,35..0,36>                f
<ListComp 0,40..0,54>            [g for h in i]
<Name 0,41..0,42>                g
<comprehension 0,43..0,53>       for h in i
<Name 0,47..0,48>                h
<Name 0,52..0,53>                i
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True, back=True)):
            l.append(g)
            if g.is_ListComp:
                gen.send(True)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,55>          a = [_ for b in [c for d in e] for f in [g for h in i]]
<ListComp 0,4..0,55>             [_ for b in [c for d in e] for f in [g for h in i]]
<comprehension 0,31..0,54>       for f in [g for h in i]
<ListComp 0,40..0,54>            [g for h in i]
<comprehension 0,43..0,53>       for h in i
<Name 0,52..0,53>                i
<Name 0,47..0,48>                h
<Name 0,41..0,42>                g
<Name 0,35..0,36>                f
<comprehension 0,7..0,30>        for b in [c for d in e]
<ListComp 0,16..0,30>            [c for d in e]
<comprehension 0,19..0,29>       for d in e
<Name 0,28..0,29>                e
<Name 0,23..0,24>                d
<Name 0,17..0,18>                c
<Name 0,11..0,12>                b
<Name 0,5..0,6>                  _
<Name 0,0..0,1>                  a
            '''.strip())

        # deeper nesting of Comprehensions and NamedExprs

        f = FST('[a := b for c in [d := e for f in [g := h for i in j]]]')

        self.assertEqual(walkscope(f), '''
<ListComp ROOT 0,0..0,55>        [a := b for c in [d := e for f in [g := h for i in j]]]
<NamedExpr 0,1..0,7>             a := b
<Name 0,1..0,2>                  a
<Name 0,6..0,7>                  b
<comprehension 0,8..0,54>        for c in [d := e for f in [g := h for i in j]]
<Name 0,12..0,13>                c
            '''.strip())

        self.assertEqual(walkscope(f, back=True), '''
<ListComp ROOT 0,0..0,55>        [a := b for c in [d := e for f in [g := h for i in j]]]
<comprehension 0,8..0,54>        for c in [d := e for f in [g := h for i in j]]
<Name 0,12..0,13>                c
<NamedExpr 0,1..0,7>             a := b
<Name 0,6..0,7>                  b
<Name 0,1..0,2>                  a
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True)):
            l.append(g)
            if g.is_ListComp:
                gen.send(True)
        self.assertEqual(walkscope(l), '''
<ListComp ROOT 0,0..0,55>        [a := b for c in [d := e for f in [g := h for i in j]]]
<NamedExpr 0,1..0,7>             a := b
<Name 0,1..0,2>                  a
<Name 0,6..0,7>                  b
<comprehension 0,8..0,54>        for c in [d := e for f in [g := h for i in j]]
<Name 0,12..0,13>                c
<ListComp 0,17..0,54>            [d := e for f in [g := h for i in j]]
<NamedExpr 0,18..0,24>           d := e
<Name 0,18..0,19>                d
<Name 0,23..0,24>                e
<comprehension 0,25..0,53>       for f in [g := h for i in j]
<Name 0,29..0,30>                f
<ListComp 0,34..0,53>            [g := h for i in j]
<NamedExpr 0,35..0,41>           g := h
<Name 0,35..0,36>                g
<Name 0,40..0,41>                h
<comprehension 0,42..0,52>       for i in j
<Name 0,46..0,47>                i
<Name 0,51..0,52>                j
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True, back=True)):
            l.append(g)
            if g.is_ListComp:
                gen.send(True)
        self.assertEqual(walkscope(l), '''
<ListComp ROOT 0,0..0,55>        [a := b for c in [d := e for f in [g := h for i in j]]]
<comprehension 0,8..0,54>        for c in [d := e for f in [g := h for i in j]]
<ListComp 0,17..0,54>            [d := e for f in [g := h for i in j]]
<comprehension 0,25..0,53>       for f in [g := h for i in j]
<ListComp 0,34..0,53>            [g := h for i in j]
<comprehension 0,42..0,52>       for i in j
<Name 0,51..0,52>                j
<Name 0,46..0,47>                i
<NamedExpr 0,35..0,41>           g := h
<Name 0,40..0,41>                h
<Name 0,35..0,36>                g
<Name 0,29..0,30>                f
<NamedExpr 0,18..0,24>           d := e
<Name 0,23..0,24>                e
<Name 0,18..0,19>                d
<Name 0,12..0,13>                c
<NamedExpr 0,1..0,7>             a := b
<Name 0,6..0,7>                  b
<Name 0,1..0,2>                  a
            '''.strip())

        f = FST('_ = [a := b for c in [d := e for f in [g := h for i in j]]]')

        self.assertEqual(walkscope(f), '''
<Assign ROOT 0,0..0,59>          _ = [a := b for c in [d := e for f in [g := h for i in j]]]
<Name 0,0..0,1>                  _
<ListComp 0,4..0,59>             [a := b for c in [d := e for f in [g := h for i in j]]]
<Name 0,5..0,6>                  a
<ListComp 0,21..0,58>            [d := e for f in [g := h for i in j]]
<Name 0,22..0,23>                d
<ListComp 0,38..0,57>            [g := h for i in j]
<Name 0,39..0,40>                g
<Name 0,55..0,56>                j
            '''.strip())

        self.assertEqual(walkscope(f, back=True), '''
<Assign ROOT 0,0..0,59>          _ = [a := b for c in [d := e for f in [g := h for i in j]]]
<ListComp 0,4..0,59>             [a := b for c in [d := e for f in [g := h for i in j]]]
<ListComp 0,21..0,58>            [d := e for f in [g := h for i in j]]
<ListComp 0,38..0,57>            [g := h for i in j]
<Name 0,55..0,56>                j
<Name 0,39..0,40>                g
<Name 0,22..0,23>                d
<Name 0,5..0,6>                  a
<Name 0,0..0,1>                  _
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True)):
            l.append(g)
            if g.is_ListComp:
                gen.send(True)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,59>          _ = [a := b for c in [d := e for f in [g := h for i in j]]]
<Name 0,0..0,1>                  _
<ListComp 0,4..0,59>             [a := b for c in [d := e for f in [g := h for i in j]]]
<NamedExpr 0,5..0,11>            a := b
<Name 0,5..0,6>                  a
<Name 0,10..0,11>                b
<comprehension 0,12..0,58>       for c in [d := e for f in [g := h for i in j]]
<Name 0,16..0,17>                c
<ListComp 0,21..0,58>            [d := e for f in [g := h for i in j]]
<NamedExpr 0,22..0,28>           d := e
<Name 0,22..0,23>                d
<Name 0,27..0,28>                e
<comprehension 0,29..0,57>       for f in [g := h for i in j]
<Name 0,33..0,34>                f
<ListComp 0,38..0,57>            [g := h for i in j]
<NamedExpr 0,39..0,45>           g := h
<Name 0,39..0,40>                g
<Name 0,44..0,45>                h
<comprehension 0,46..0,56>       for i in j
<Name 0,50..0,51>                i
<Name 0,55..0,56>                j
            '''.strip())

        l = []
        for g in (gen := f.walk(scope=True, back=True)):
            l.append(g)
            if g.is_ListComp:
                gen.send(True)
        self.assertEqual(walkscope(l), '''
<Assign ROOT 0,0..0,59>          _ = [a := b for c in [d := e for f in [g := h for i in j]]]
<ListComp 0,4..0,59>             [a := b for c in [d := e for f in [g := h for i in j]]]
<comprehension 0,12..0,58>       for c in [d := e for f in [g := h for i in j]]
<ListComp 0,21..0,58>            [d := e for f in [g := h for i in j]]
<comprehension 0,29..0,57>       for f in [g := h for i in j]
<ListComp 0,38..0,57>            [g := h for i in j]
<comprehension 0,46..0,56>       for i in j
<Name 0,55..0,56>                j
<Name 0,50..0,51>                i
<NamedExpr 0,39..0,45>           g := h
<Name 0,44..0,45>                h
<Name 0,39..0,40>                g
<Name 0,33..0,34>                f
<NamedExpr 0,22..0,28>           d := e
<Name 0,27..0,28>                e
<Name 0,22..0,23>                d
<Name 0,16..0,17>                c
<NamedExpr 0,5..0,11>            a := b
<Name 0,10..0,11>                b
<Name 0,5..0,6>                  a
<Name 0,0..0,1>                  _
            '''.strip())

    @unittest.skipUnless(PYGE12, 'only valid for py >= 3.12')
    def test_walk_scope_type_params(self):
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

    def test_walk_on_leave(self):
        assertRaises(ValueError("invalid walk 'on' value 'BAD'"), list, FST('a').walk(on='BAD'))
        assertRaises(NotImplementedError("'scope=True' is only supported for 'on=\"enter\"'"), list, FST('a').walk(on='leave', scope=True))
        assertRaises(NotImplementedError("'scope=True' is only supported for 'on=\"enter\"'"), list, FST('a').walk(on='both', scope=True))

        # basic on leave

        f = FST('[a, [b, c], d]')

        self.assertEqual(['a', 'b', 'c', '[b, c]', 'd', '[a, [b, c], d]'], list(f.src for f in f.walk(on='leave')))
        self.assertEqual(['d', 'c', 'b', '[b, c]', 'a', '[a, [b, c], d]'], list(f.src for f in f.walk(on='leave', back=True)))
        self.assertEqual(['a', '[b, c]', 'd', '[a, [b, c], d]'], list(f.src for f in f.walk(on='leave', recurse=False)))
        self.assertEqual(['d', '[b, c]', 'a', '[a, [b, c], d]'], list(f.src for f in f.walk(on='leave', recurse=False, back=True)))
        self.assertEqual(['a', 'b', 'c', '[b, c]', 'd'], list(f.src for f in f.walk(on='leave', self_=False)))
        self.assertEqual(['d', 'c', 'b', '[b, c]', 'a'], list(f.src for f in f.walk(on='leave', self_=False, back=True)))
        self.assertEqual(['a', '[b, c]', 'd'], list(f.src for f in f.walk(on='leave', self_=False, recurse=False)))
        self.assertEqual(['d', '[b, c]', 'a'], list(f.src for f in f.walk(on='leave', self_=False, recurse=False, back=True)))

        # test send(True) on last node

        def test(gen, repeat_node):
            l = []

            for f in gen:
                l.append(f.src)

                if f is repeat_node:
                    repeat_node = None

                    gen.send(True)

            return l

        f = FST('[a, [b, c], d]')

        self.assertEqual(['a', 'b', 'c', '[b, c]', 'd', '[a, [b, c], d]', 'a', 'b', 'c', '[b, c]', 'd', '[a, [b, c], d]'], test(f.walk(on='leave'), f))
        self.assertEqual(['d', 'c', 'b', '[b, c]', 'a', '[a, [b, c], d]', 'd', 'c', 'b', '[b, c]', 'a', '[a, [b, c], d]'], test(f.walk(on='leave', back=True), f))
        self.assertEqual(['a', '[b, c]', 'd', '[a, [b, c], d]', 'a', 'b', 'c', '[b, c]', 'd', '[a, [b, c], d]'], test(f.walk(on='leave', recurse=False), f))
        self.assertEqual(['d', '[b, c]', 'a', '[a, [b, c], d]', 'd', 'c', 'b', '[b, c]', 'a', '[a, [b, c], d]'], test(f.walk(on='leave', recurse=False, back=True), f))
        self.assertEqual(['a', 'b', 'c', '[b, c]', 'b', 'c', '[b, c]', 'd'], test(f.walk(on='leave', self_=False), f.elts[1]))
        self.assertEqual(['d', 'c', 'b', '[b, c]', 'c', 'b', '[b, c]', 'a'], test(f.walk(on='leave', self_=False, back=True), f.elts[1]))
        self.assertEqual(['a', '[b, c]', 'b', 'c', '[b, c]', 'd', ], test(f.walk(on='leave', self_=False, recurse=False), f.elts[1]))
        self.assertEqual(['d', '[b, c]', 'c', 'b', '[b, c]', 'a', ], test(f.walk(on='leave', self_=False, recurse=False, back=True), f.elts[1]))

        # send(True) overrides recurse=False

        f = FST('[a, [b, [c, d]]]')

        self.assertEqual(['a', '[b, [c, d]]', '[a, [b, [c, d]]]', 'a', 'b', 'c', 'd', '[c, d]', '[b, [c, d]]', '[a, [b, [c, d]]]'], test(f.walk(on='leave', recurse=False), f))
        self.assertEqual(['[b, [c, d]]', 'a', '[a, [b, [c, d]]]', 'd', 'c', '[c, d]', 'b', '[b, [c, d]]', 'a', '[a, [b, [c, d]]]'], test(f.walk(on='leave', recurse=False, back=True), f))
        self.assertEqual(['a', '[b, [c, d]]', 'b', 'c', 'd', '[c, d]', '[b, [c, d]]', '[a, [b, [c, d]]]'], test(f.walk(on='leave', recurse=False), f.elts[1]))
        self.assertEqual(['[b, [c, d]]', 'd', 'c', '[c, d]', 'b', '[b, [c, d]]', 'a', '[a, [b, [c, d]]]'], test(f.walk(on='leave', recurse=False, back=True), f.elts[1]))
        self.assertEqual(['a', '[b, [c, d]]', '[a, [b, [c, d]]]'], test(f.walk(on='leave', recurse=False), f.elts[1].elts[1]))
        self.assertEqual(['[b, [c, d]]', 'a', '[a, [b, [c, d]]]'], test(f.walk(on='leave', recurse=False, back=True), f.elts[1].elts[1]))

        # test delete with send(True) on last node

        def testdel(gen, repeat_node):
            l = []

            for f in gen:
                l.append(f.src)

                if f is repeat_node:
                    repeat_node = None

                    gen.send(True)

                elif f.is_Name:
                    f.remove()

            return l

        f = FST('[a, [b, [c, d], e], f]')

        self.assertEqual(['a', 'b', 'c', 'd', '[]', 'e', '[[]]', 'f', '[[[]]]', '[]', '[[]]', '[[[]]]'], testdel((g := f.copy()).walk(on='leave'), g))
        self.assertEqual(['f', 'e', 'd', 'c', '[]', 'b', '[[]]', 'a', '[[[]]]', '[]', '[[]]', '[[[]]]'], testdel((g := f.copy()).walk(on='leave', back=True), g))

        # test replace with send(True) on outermost node

        def testrepl(gen, repeat_node):
            l = []

            for f in gen:
                l.append(f.src)

                if f is repeat_node:
                    repeat_node = None

                    gen.send(True)

                elif f.is_Name:
                    i = f.id
                    f.replace(i.upper() if i.islower() else i.lower())  # swap uppercase and lowercase

            return l

        self.assertEqual(['a', 'b', 'c', 'd', '[C, D]', 'e', '[B, [C, D], E]', 'f', '[A, [B, [C, D], E], F]', 'A', 'B', 'C', 'D', '[c, d]', 'E', '[b, [c, d], e]', 'F', '[a, [b, [c, d], e], f]'], testrepl((g := f.copy()).walk(on='leave'), g))
        self.assertEqual(['f', 'e', 'd', 'c', '[C, D]', 'b', '[B, [C, D], E]', 'a', '[A, [B, [C, D], E], F]', 'F', 'E', 'D', 'C', '[c, d]', 'B', '[b, [c, d], e]', 'A', '[a, [b, [c, d], e], f]'], testrepl((g := f.copy()).walk(on='leave', back=True), g))

        # test replace with send(True) on intermediate node

        self.assertEqual(['a', 'b', 'c', 'd', '[C, D]', 'e', '[B, [C, D], E]', 'B', 'C', 'D', '[c, d]', 'E', '[b, [c, d], e]', 'f', '[A, [b, [c, d], e], F]'], testrepl((g := f.copy()).walk(on='leave'), g.elts[1]))
        self.assertEqual(['f', 'e', 'd', 'c', '[C, D]', 'b', '[B, [C, D], E]', 'E', 'D', 'C', '[c, d]', 'B', '[b, [c, d], e]', 'a', '[A, [b, [c, d], e], F]'], testrepl((g := f.copy()).walk(on='leave', back=True), g.elts[1]))

        # test replace with send(True) on innermost node

        self.assertEqual(['a', 'b', 'c', 'd', '[C, D]', 'C', 'D', '[c, d]', 'e', '[B, [c, d], E]', 'f', '[A, [B, [c, d], E], F]'], testrepl((g := f.copy()).walk(on='leave'), g.elts[1].elts[1]))
        self.assertEqual(['f', 'e', 'd', 'c', '[C, D]', 'D', 'C', '[c, d]', 'b', '[B, [c, d], E]', 'a', '[A, [B, [c, d], E], F]'], testrepl((g := f.copy()).walk(on='leave', back=True), g.elts[1].elts[1]))

    def test_walk_on_both(self):
        ON = '+-'  # enter / leave string, '+' = enter, '-' = leave

        # basic on both

        f = FST('[a, [b, c], d]')

        self.assertEqual(['+[a, [b, c], d]', '+a', '-a', '+[b, c]', '+b', '-b', '+c', '-c', '-[b, c]', '+d', '-d', '-[a, [b, c], d]'], list(ON[on] + f.src for f, on in f.walk(on='both')))
        self.assertEqual(['+[a, [b, c], d]', '+d', '-d', '+[b, c]', '+c', '-c', '+b', '-b', '-[b, c]', '+a', '-a', '-[a, [b, c], d]'], list(ON[on] + f.src for f, on in f.walk(on='both', back=True)))
        self.assertEqual(['+[a, [b, c], d]', '+a', '-a', '+[b, c]', '-[b, c]', '+d', '-d', '-[a, [b, c], d]'], list(ON[on] + f.src for f, on in f.walk(on='both', recurse=False)))
        self.assertEqual(['+[a, [b, c], d]', '+d', '-d', '+[b, c]', '-[b, c]', '+a', '-a', '-[a, [b, c], d]'], list(ON[on] + f.src for f, on in f.walk(on='both', recurse=False, back=True)))
        self.assertEqual(['+a', '-a', '+[b, c]', '+b', '-b', '+c', '-c', '-[b, c]', '+d', '-d'], list(ON[on] + f.src for f, on in f.walk(on='both', self_=False)))
        self.assertEqual(['+d', '-d', '+[b, c]', '+c', '-c', '+b', '-b', '-[b, c]', '+a', '-a'], list(ON[on] + f.src for f, on in f.walk(on='both', self_=False, back=True)))
        self.assertEqual(['+a', '-a', '+[b, c]', '-[b, c]', '+d', '-d'], list(ON[on] + f.src for f, on in f.walk(on='both', self_=False, recurse=False)))
        self.assertEqual(['+d', '-d', '+[b, c]', '-[b, c]', '+a', '-a'], list(ON[on] + f.src for f, on in f.walk(on='both', self_=False, recurse=False, back=True)))

        # test send(True) on last node

        def test(gen, repeat_node):
            l = []

            for f, on in gen:
                l.append(ON[on] + f.src)

                if on and f is repeat_node:
                    repeat_node = None

                    gen.send(True)

            return l

        f = FST('[a, [b, c], d]')

        self.assertEqual(['+[a, [b, c], d]', '+a', '-a', '+[b, c]', '+b', '-b', '+c', '-c', '-[b, c]', '+d', '-d', '-[a, [b, c], d]', '+[a, [b, c], d]', '+a', '-a', '+[b, c]', '+b', '-b', '+c', '-c', '-[b, c]', '+d', '-d', '-[a, [b, c], d]'], test(f.walk(on='both'), f))
        self.assertEqual(['+[a, [b, c], d]', '+d', '-d', '+[b, c]', '+c', '-c', '+b', '-b', '-[b, c]', '+a', '-a', '-[a, [b, c], d]', '+[a, [b, c], d]', '+d', '-d', '+[b, c]', '+c', '-c', '+b', '-b', '-[b, c]', '+a', '-a', '-[a, [b, c], d]'], test(f.walk(on='both', back=True), f))
        self.assertEqual(['+[a, [b, c], d]', '+a', '-a', '+[b, c]', '-[b, c]', '+d', '-d', '-[a, [b, c], d]', '+[a, [b, c], d]', '+a', '-a', '+[b, c]', '+b', '-b', '+c', '-c', '-[b, c]', '+d', '-d', '-[a, [b, c], d]'], test(f.walk(on='both', recurse=False), f))
        self.assertEqual(['+[a, [b, c], d]', '+d', '-d', '+[b, c]', '-[b, c]', '+a', '-a', '-[a, [b, c], d]', '+[a, [b, c], d]', '+d', '-d', '+[b, c]', '+c', '-c', '+b', '-b', '-[b, c]', '+a', '-a', '-[a, [b, c], d]'], test(f.walk(on='both', recurse=False, back=True), f))
        self.assertEqual(['+a', '-a', '+[b, c]', '+b', '-b', '+c', '-c', '-[b, c]', '+[b, c]', '+b', '-b', '+c', '-c', '-[b, c]', '+d', '-d'], test(f.walk(on='both', self_=False), f.elts[1]))
        self.assertEqual(['+d', '-d', '+[b, c]', '+c', '-c', '+b', '-b', '-[b, c]', '+[b, c]', '+c', '-c', '+b', '-b', '-[b, c]', '+a', '-a'], test(f.walk(on='both', self_=False, back=True), f.elts[1]))
        self.assertEqual(['+a', '-a', '+[b, c]', '-[b, c]', '+[b, c]', '+b', '-b', '+c', '-c', '-[b, c]', '+d', '-d'], test(f.walk(on='both', self_=False, recurse=False), f.elts[1]))
        self.assertEqual(['+d', '-d', '+[b, c]', '-[b, c]', '+[b, c]', '+c', '-c', '+b', '-b', '-[b, c]', '+a', '-a'], test(f.walk(on='both', self_=False, recurse=False, back=True), f.elts[1]))

        # send(True) overrides recurse=False

        f = FST('[a, [b, [c, d]]]')

        self.assertEqual(['+[a, [b, [c, d]]]', '+a', '-a', '+[b, [c, d]]', '-[b, [c, d]]', '-[a, [b, [c, d]]]', '+[a, [b, [c, d]]]', '+a', '-a', '+[b, [c, d]]', '+b', '-b', '+[c, d]', '+c', '-c', '+d', '-d', '-[c, d]', '-[b, [c, d]]', '-[a, [b, [c, d]]]'], test(f.walk(on='both', recurse=False), f))
        self.assertEqual(['+[a, [b, [c, d]]]', '+[b, [c, d]]', '-[b, [c, d]]', '+a', '-a', '-[a, [b, [c, d]]]', '+[a, [b, [c, d]]]', '+[b, [c, d]]', '+[c, d]', '+d', '-d', '+c', '-c', '-[c, d]', '+b', '-b', '-[b, [c, d]]', '+a', '-a', '-[a, [b, [c, d]]]'], test(f.walk(on='both', recurse=False, back=True), f))
        self.assertEqual(['+[a, [b, [c, d]]]', '+a', '-a', '+[b, [c, d]]', '-[b, [c, d]]', '+[b, [c, d]]', '+b', '-b', '+[c, d]', '+c', '-c', '+d', '-d', '-[c, d]', '-[b, [c, d]]', '-[a, [b, [c, d]]]'], test(f.walk(on='both', recurse=False), f.elts[1]))
        self.assertEqual(['+[a, [b, [c, d]]]', '+[b, [c, d]]', '-[b, [c, d]]', '+[b, [c, d]]', '+[c, d]', '+d', '-d', '+c', '-c', '-[c, d]', '+b', '-b', '-[b, [c, d]]', '+a', '-a', '-[a, [b, [c, d]]]'], test(f.walk(on='both', recurse=False, back=True), f.elts[1]))
        self.assertEqual(['+[a, [b, [c, d]]]', '+a', '-a', '+[b, [c, d]]', '-[b, [c, d]]', '-[a, [b, [c, d]]]'], test(f.walk(on='both', recurse=False), f.elts[1].elts[1]))
        self.assertEqual(['+[a, [b, [c, d]]]', '+[b, [c, d]]', '-[b, [c, d]]', '+a', '-a', '-[a, [b, [c, d]]]'], test(f.walk(on='both', recurse=False, back=True), f.elts[1].elts[1]))

        # test delete with send(True) on last node

        def testdelin(gen, repeat_node):
            l = []

            for f, on in gen:
                l.append(ON[on] + f.src)

                if on and f is repeat_node:
                    repeat_node = None

                    gen.send(True)

                elif f.is_Name:
                    f.remove()

            return l

        def testdelout(gen, repeat_node):
            l = []

            for f, on in gen:
                l.append(ON[on] + f.src)

                if on and f is repeat_node:
                    repeat_node = None

                    gen.send(True)

                elif on and f.is_Name:
                    f.remove()

            return l

        f = FST('[a, [b, [c, d], e], f]')

        self.assertEqual(['+[a, [b, [c, d], e], f]', '+a', '+[b, [c, d], e]', '+b', '+[c, d]', '+c', '+d', '-[]', '+e', '-[[]]', '+f', '-[[[]]]', '+[[[]]]', '+[[]]', '+[]', '-[]', '-[[]]', '-[[[]]]'], testdelin((g := f.copy()).walk(on='both'), g))
        self.assertEqual(['+[a, [b, [c, d], e], f]', '+f', '+[b, [c, d], e]', '+e', '+[c, d]', '+d', '+c', '-[]', '+b', '-[[]]', '+a', '-[[[]]]', '+[[[]]]', '+[[]]', '+[]', '-[]', '-[[]]', '-[[[]]]'], testdelin((g := f.copy()).walk(on='both', back=True), g))

        self.assertEqual(['+[a, [b, [c, d], e], f]', '+a', '-a', '+[b, [c, d], e]', '+b', '-b', '+[c, d]', '+c', '-c', '+d', '-d', '-[]', '+e', '-e', '-[[]]', '+f', '-f', '-[[[]]]', '+[[[]]]', '+[[]]', '+[]', '-[]', '-[[]]', '-[[[]]]'], testdelout((g := f.copy()).walk(on='both'), g))
        self.assertEqual(['+[a, [b, [c, d], e], f]', '+f', '-f', '+[b, [c, d], e]', '+e', '-e', '+[c, d]', '+d', '-d', '+c', '-c', '-[]', '+b', '-b', '-[[]]', '+a', '-a', '-[[[]]]', '+[[[]]]', '+[[]]', '+[]', '-[]', '-[[]]', '-[[[]]]'], testdelout((g := f.copy()).walk(on='both', back=True), g))

        # test replace with send(True) on outermost node

        def testreplin(gen, repeat_node):
            l = []

            for f, on in gen:
                l.append(ON[on] + f.src)

                if on and f is repeat_node:
                    repeat_node = None

                    gen.send(True)

                elif not on and f.is_Name:
                    i = f.id
                    f.replace(i.upper() if i.islower() else i.lower())  # swap uppercase and lowercase

            return l

        def testreplout(gen, repeat_node):
            l = []

            for f, on in gen:
                l.append(ON[on] + f.src)

                if on and f is repeat_node:
                    repeat_node = None

                    gen.send(True)

                elif on and f.is_Name:
                    i = f.id
                    f.replace(i.upper() if i.islower() else i.lower())  # swap uppercase and lowercase

            return l

        self.assertEqual(['+[a, [b, [c, d], e], f]', '+a', '-A', '+[b, [c, d], e]', '+b', '-B', '+[c, d]', '+c', '-C', '+d', '-D', '-[C, D]', '+e', '-E', '-[B, [C, D], E]', '+f', '-F', '-[A, [B, [C, D], E], F]',
                          '+[A, [B, [C, D], E], F]', '+A', '-a', '+[B, [C, D], E]', '+B', '-b', '+[C, D]', '+C', '-c', '+D', '-d', '-[c, d]', '+E', '-e', '-[b, [c, d], e]', '+F', '-f', '-[a, [b, [c, d], e], f]'], testreplin((g := f.copy()).walk(on='both'), g))
        self.assertEqual(['+[a, [b, [c, d], e], f]', '+f', '-F', '+[b, [c, d], e]', '+e', '-E', '+[c, d]', '+d', '-D', '+c', '-C', '-[C, D]', '+b', '-B', '-[B, [C, D], E]', '+a', '-A', '-[A, [B, [C, D], E], F]',
                          '+[A, [B, [C, D], E], F]', '+F', '-f', '+[B, [C, D], E]', '+E', '-e', '+[C, D]', '+D', '-d', '+C', '-c', '-[c, d]', '+B', '-b', '-[b, [c, d], e]', '+A', '-a', '-[a, [b, [c, d], e], f]'], testreplin((g := f.copy()).walk(on='both', back=True), g))

        self.assertEqual(['+[a, [b, [c, d], e], f]', '+a', '-a', '+[b, [c, d], e]', '+b', '-b', '+[c, d]', '+c', '-c', '+d', '-d', '-[C, D]', '+e', '-e', '-[B, [C, D], E]', '+f', '-f', '-[A, [B, [C, D], E], F]',
                          '+[A, [B, [C, D], E], F]', '+A', '-A', '+[B, [C, D], E]', '+B', '-B', '+[C, D]', '+C', '-C', '+D', '-D', '-[c, d]', '+E', '-E', '-[b, [c, d], e]', '+F', '-F', '-[a, [b, [c, d], e], f]'], testreplout((g := f.copy()).walk(on='both'), g))
        self.assertEqual(['+[a, [b, [c, d], e], f]', '+f', '-f', '+[b, [c, d], e]', '+e', '-e', '+[c, d]', '+d', '-d', '+c', '-c', '-[C, D]', '+b', '-b', '-[B, [C, D], E]', '+a', '-a', '-[A, [B, [C, D], E], F]',
                          '+[A, [B, [C, D], E], F]', '+F', '-F', '+[B, [C, D], E]', '+E', '-E', '+[C, D]', '+D', '-D', '+C', '-C', '-[c, d]', '+B', '-B', '-[b, [c, d], e]', '+A', '-A', '-[a, [b, [c, d], e], f]'], testreplout((g := f.copy()).walk(on='both', back=True), g))

        # test replace with send(True) on intermediate node

        self.assertEqual(['+[a, [b, [c, d], e], f]', '+a', '-A', '+[b, [c, d], e]', '+b', '-B', '+[c, d]', '+c', '-C', '+d', '-D', '-[C, D]', '+e', '-E', '-[B, [C, D], E]',
                                                                 '+[B, [C, D], E]', '+B', '-b', '+[C, D]', '+C', '-c', '+D', '-d', '-[c, d]', '+E', '-e', '-[b, [c, d], e]', '+f', '-F', '-[A, [b, [c, d], e], F]'], testreplin((g := f.copy()).walk(on='both'), g.elts[1]))
        self.assertEqual(['+[a, [b, [c, d], e], f]', '+f', '-F', '+[b, [c, d], e]', '+e', '-E', '+[c, d]', '+d', '-D', '+c', '-C', '-[C, D]', '+b', '-B', '-[B, [C, D], E]',
                                                                 '+[B, [C, D], E]', '+E', '-e', '+[C, D]', '+D', '-d', '+C', '-c', '-[c, d]', '+B', '-b', '-[b, [c, d], e]', '+a', '-A', '-[A, [b, [c, d], e], F]'], testreplin((g := f.copy()).walk(on='both', back=True), g.elts[1]))

        self.assertEqual(['+[a, [b, [c, d], e], f]', '+a', '-a', '+[b, [c, d], e]', '+b', '-b', '+[c, d]', '+c', '-c', '+d', '-d', '-[C, D]', '+e', '-e', '-[B, [C, D], E]',
                                                                 '+[B, [C, D], E]', '+B', '-B', '+[C, D]', '+C', '-C', '+D', '-D', '-[c, d]', '+E', '-E', '-[b, [c, d], e]', '+f', '-f', '-[A, [b, [c, d], e], F]'], testreplout((g := f.copy()).walk(on='both'), g.elts[1]))
        self.assertEqual(['+[a, [b, [c, d], e], f]', '+f', '-f', '+[b, [c, d], e]', '+e', '-e', '+[c, d]', '+d', '-d', '+c', '-c', '-[C, D]', '+b', '-b', '-[B, [C, D], E]',
                                                                 '+[B, [C, D], E]', '+E', '-E', '+[C, D]', '+D', '-D', '+C', '-C', '-[c, d]', '+B', '-B', '-[b, [c, d], e]', '+a', '-a', '-[A, [b, [c, d], e], F]'], testreplout((g := f.copy()).walk(on='both', back=True), g.elts[1]))

        # test replace with send(True) on innermost node

        self.assertEqual(['+[a, [b, [c, d], e], f]', '+a', '-A', '+[b, [c, d], e]', '+b', '-B', '+[c, d]', '+c', '-C', '+d', '-D', '-[C, D]',
                                                                                                '+[C, D]', '+C', '-c', '+D', '-d', '-[c, d]', '+e', '-E', '-[B, [c, d], E]', '+f', '-F', '-[A, [B, [c, d], E], F]'], testreplin((g := f.copy()).walk(on='both'), g.elts[1].elts[1]))
        self.assertEqual(['+[a, [b, [c, d], e], f]', '+f', '-F', '+[b, [c, d], e]', '+e', '-E', '+[c, d]', '+d', '-D', '+c', '-C', '-[C, D]',
                                                                                                '+[C, D]', '+D', '-d', '+C', '-c', '-[c, d]', '+b', '-B', '-[B, [c, d], E]', '+a', '-A', '-[A, [B, [c, d], E], F]'], testreplin((g := f.copy()).walk(on='both', back=True), g.elts[1].elts[1]))

        self.assertEqual(['+[a, [b, [c, d], e], f]', '+a', '-a', '+[b, [c, d], e]', '+b', '-b', '+[c, d]', '+c', '-c', '+d', '-d', '-[C, D]',
                                                                                                '+[C, D]', '+C', '-C', '+D', '-D', '-[c, d]', '+e', '-e', '-[B, [c, d], E]', '+f', '-f', '-[A, [B, [c, d], E], F]'], testreplout((g := f.copy()).walk(on='both'), g.elts[1].elts[1]))
        self.assertEqual(['+[a, [b, [c, d], e], f]', '+f', '-f', '+[b, [c, d], e]', '+e', '-e', '+[c, d]', '+d', '-d', '+c', '-c', '-[C, D]',
                                                                                                '+[C, D]', '+D', '-D', '+C', '-C', '-[c, d]', '+b', '-b', '-[B, [c, d], E]', '+a', '-a', '-[A, [B, [c, d], E], F]'], testreplout((g := f.copy()).walk(on='both', back=True), g.elts[1].elts[1]))

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

    def test_traverse_misc(self):
        f = FST('{{}, 1}')
        self.assertIsNone(f.elts[0].step_fwd(top=f.elts[0]))

        f = FST('{1, {}}')
        self.assertIsNone(f.elts[1].step_back(top=f.elts[1]))


if __name__ == '__main__':
    unittest.main()

