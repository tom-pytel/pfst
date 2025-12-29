#!/usr/bin/env python

import os
import re
import unittest
from ast import parse as ast_parse
from random import seed, shuffle

from fst import *

from fst.asttypes import ASTS_LEAF_STMTISH
from fst.astutil import compare_asts
from fst.common import PYLT11, PYLT12, PYGE11, PYGE12, PYGE14
from fst.fst_misc import new_empty_set_curlies

from support import GetSliceCases, PutSliceCases, _clean_options


DIR_NAME       = os.path.dirname(__file__)
DATA_GET_SLICE = GetSliceCases(os.path.join(DIR_NAME, 'data/data_get_slice.py'))
DATA_PUT_SLICE = PutSliceCases(os.path.join(DIR_NAME, 'data/data_put_slice.py'))


def fixtailspace(s, r='_'):
    return re.sub(r'[ ]+$', lambda m: r * len(m.group()), s, flags=re.MULTILINE)


def read(fnm):
    with open(fnm) as f:
        return f.read()


def regen_get_slice():
    DATA_GET_SLICE.generate()
    DATA_GET_SLICE.write()


def regen_put_slice():
    DATA_PUT_SLICE.generate()
    DATA_PUT_SLICE.write()


class TestFSTSlice(unittest.TestCase):
    def test_get_slice_from_data(self):
        for case, rest in DATA_GET_SLICE.iterate(True):
            for rest_idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                self.assertEqual(c, r, f'{case.id()}, rest idx = {rest_idx}')

    def test_del_slice_from_get_slice_data(self):
        from support import _make_fst

        for case, rest in DATA_GET_SLICE.iterate(True):
            if not case.options.get('_del', True):
                continue

            f = _make_fst(case.code, case.attr)

            try:
                f.put_slice(None, case.start, case.stop, case.field, **_clean_options(case.options))

            except Exception:
                if not ((r0 := rest[0]).startswith('**') and r0.endswith('**')):
                    raise RuntimeError(f'del raises while cut did not, {case.id()}')

            else:
                if f.root.src != rest[0]:
                    raise RuntimeError(f'del and cut FST src are not identical, {case.id()}\n{f.root.src}\n...\n{rest[0]}')

                if (root_dump := f.root.dump(out=str)) != rest[1]:
                    raise RuntimeError(f'del and cut FST dump are not identical, {case.id()}\n{root_dump}\n...\n{rest[1]}')

    def test_put_slice_from_data(self):
        for case, rest in DATA_PUT_SLICE.iterate(True):
            for rest_idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                self.assertEqual(c, r, f'{case.id()}, rest idx = {rest_idx}')

    def test_put_src_from_put_slice_data(self):  # this test may go away at some point
        from fst.fst_misc import fixup_field_body
        from fst.fst_put_slice import _loc_slice_raw_put
        from support import _unfmt_code, _make_fst

        for case, rest in DATA_PUT_SLICE.iterate(True):
            if not case.options.get('raw') or rest[1].startswith('**'):
                continue

            try:
                f        = _make_fst(case.code, case.attr)
                field, _ = fixup_field_body(f.a, case.field, True)
                loc      = _loc_slice_raw_put(f, case.start, case.stop, field)[:4]
                src      = _unfmt_code(r0 if isinstance(r0 := rest[0], str) else r0[1])

                f.put_src(None if src == '**DEL**' else src, *loc)
                f.root.verify(raise_=True)

            except Exception:
                print(case.id())

                raise

            if f.root.src != rest[1]:
                raise RuntimeError(f'put_src and put raw FST src are not identical, {case.id()}\n{f.root.src}\n...\n{rest[1]}')

            if (root_dump := f.root.dump(out=str)) != rest[2]:
                raise RuntimeError(f'put_src and put raw FST dump are not identical, {case.id()}\n{root_dump}\n...\n{rest[2]}')

    def test_cut_slice_neg_space(self):
        f = FST('''[

# pre
    a,  # line
# post

    b
]           '''.strip())
        self.assertEqual(f.get_slice(0, 1, trivia=('all+', 'all+')).src, '''[

# pre
    a,  # line
# post

]           '''.strip())
        self.assertEqual(f.get_slice(0, 1, trivia=('all-', 'all-')).src, '''[
# pre
    a,  # line
# post
]           '''.strip())

        self.assertEqual(f.get_slice(0, 1, cut=True, trivia=('all-', 'all-')).src, '''[
# pre
    a,  # line
# post
]           '''.strip())
        self.assertEqual(f.src, '''[
    b
]           '''.strip())

        f = FST('''[

# pre
    a,  # line
# post

    b
]           '''.strip())
        self.assertEqual(f.get_slice(0, 1, cut=True, trivia=('all+', 'all+')).src, '''[

# pre
    a,  # line
# post

]           '''.strip())
        self.assertEqual(f.src, '''[
    b
]           '''.strip())

        f = FST('''[

# pre
    a,  # line
# post

    b
]           '''.strip())
        self.assertEqual(f.get_slice(0, 1, cut=True, trivia=('all', 'all')).src, '''[
# pre
    a,  # line
# post
]           '''.strip())
        self.assertEqual(f.src, '''[


    b
]           '''.strip())

    def test_cut_stmtish_special(self):
        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('i', a.body[0].f.cut(trivia=(False, False), norm=False).src)  # , precomms=False, postcomms=False
        self.assertEqual('# prepre\n\n# pre\n# post\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# pre\ni', a.body[0].f.cut(trivia=(True, False), norm=False).src)  # , precomms=True, postcomms=False
        self.assertEqual('# prepre\n\n# post\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# pre\ni # post', a.body[0].f.cut(trivia=(True, True), norm=False).src)  # , precomms=True, postcomms=True
        self.assertEqual('# prepre\n\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# prepre\n\n# pre\ni', a.body[0].f.cut(trivia=('all', False), norm=False).src)  # , precomms='all', postcomms=False
        self.assertEqual('# post\n# postpost', a.f.src)

        a = parse('( ( i ), )')
        f = a.body[0].value.elts[0].f.cut(trivia=(False, False))  # , precomms=False, postcomms=False
        self.assertEqual('()', a.f.src)
        self.assertEqual('i', f.src)

        a = parse('( ( i ), )')
        f = a.body[0].value.elts[0].f.cut(trivia=(False, False), pars=True)  # , precomms=False, postcomms=False
        self.assertEqual('()', a.f.src)
        self.assertEqual('( i )', f.src)

        a = parse('''
match a:
  case 1:
    if 1:
      pass
    else:
      pass
  case 2:
    try:
      pass
    except:
      pass
    else:
      pass
    finally:
      pass
  case 2:
    for a in b:
      pass
    else:
      pass
  case 3:
    async for a in b:
      pass
    else:
      pass
  case 4:
    while a in b:
      pass
    else:
      pass
  case 5:
    with a as b:
      pass
  case 6:
    async with a as b:
      pass
  case 7:
    def func():
      pass
  case 8:
    async def func():
      pass
  case 9:
    class cls:
      pass
            '''.strip())
        with FST.options(norm=False):
            a.body[0].cases[0].body[0].body[0].f.cut()
            a.body[0].cases[0].body[0].orelse[0].f.cut()
            a.body[0].cases[1].body[0].body[0].f.cut()
            a.body[0].cases[1].body[0].handlers[0].f.cut()
            a.body[0].cases[1].body[0].orelse[0].f.cut()
            a.body[0].cases[1].body[0].finalbody[0].f.cut()
            a.body[0].cases[2].body[0].body[0].f.cut()
            a.body[0].cases[2].body[0].orelse[0].f.cut()
            a.body[0].cases[3].body[0].body[0].f.cut()
            a.body[0].cases[3].body[0].orelse[0].f.cut()
            a.body[0].cases[4].body[0].body[0].f.cut()
            a.body[0].cases[4].body[0].orelse[0].f.cut()
            a.body[0].cases[5].body[0].body[0].f.cut()
            a.body[0].cases[6].body[0].body[0].f.cut()
            a.body[0].cases[7].body[0].body[0].f.cut()
            a.body[0].cases[8].body[0].body[0].f.cut()
            a.body[0].cases[9].body[0].body[0].f.cut()

        self.assertEqual(a.f.src, '''
match a:
  case 1:
    if 1:
  case 2:
    try:
  case 2:
    for a in b:
  case 3:
    async for a in b:
  case 4:
    while a in b:
  case 5:
    with a as b:
  case 6:
    async with a as b:
  case 7:
    def func():
  case 8:
    async def func():
  case 9:
    class cls:
'''.strip())

        with FST.options(norm=False):
            a.body[0].cases[0].body[0].f.cut()
            a.body[0].cases[1].body[0].f.cut()
            a.body[0].cases[2].body[0].f.cut()
            a.body[0].cases[3].body[0].f.cut()
            a.body[0].cases[4].body[0].f.cut()
            a.body[0].cases[5].body[0].f.cut()
            a.body[0].cases[6].body[0].f.cut()
            a.body[0].cases[7].body[0].f.cut()
            a.body[0].cases[8].body[0].f.cut()
            a.body[0].cases[9].body[0].f.cut()

        self.assertEqual(a.f.src, '''
match a:
  case 1:
  case 2:
  case 2:
  case 3:
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 9:
'''.strip())

        with FST.options(norm=False):
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()
            a.body[0].cases[0].f.cut()

        self.assertEqual(a.f.src, '''match a:''')

        a = parse('''
match a:
  case 1:
    if 1:
      pass
    else:
      pass
  case 2:
    try:
      pass
    except:
      pass
    else:
      pass
    finally:
      pass
  case 2:
    for a in b:
      pass
    else:
      pass
  case 3:
    async for a in b:
      pass
    else:
      pass
  case 4:
    while a in b:
      pass
    else:
      pass
  case 5:
    with a as b:
      pass
  case 6:
    async with a as b:
      pass
  case 7:
    def func():
      pass
  case 8:
    async def func():
      pass
  case 9:
    class cls:
      pass
            '''.strip())
        with FST.options(norm=False):
            a.body[0].cases[9].body[0].body[0].f.cut()
            a.body[0].cases[8].body[0].body[0].f.cut()
            a.body[0].cases[7].body[0].body[0].f.cut()
            a.body[0].cases[6].body[0].body[0].f.cut()
            a.body[0].cases[5].body[0].body[0].f.cut()
            a.body[0].cases[4].body[0].orelse[0].f.cut()
            a.body[0].cases[4].body[0].body[0].f.cut()
            a.body[0].cases[3].body[0].orelse[0].f.cut()
            a.body[0].cases[3].body[0].body[0].f.cut()
            a.body[0].cases[2].body[0].orelse[0].f.cut()
            a.body[0].cases[2].body[0].body[0].f.cut()
            a.body[0].cases[1].body[0].finalbody[0].f.cut()
            a.body[0].cases[1].body[0].orelse[0].f.cut()
            a.body[0].cases[1].body[0].handlers[0].f.cut()
            a.body[0].cases[1].body[0].body[0].f.cut()
            a.body[0].cases[0].body[0].orelse[0].f.cut()
            a.body[0].cases[0].body[0].body[0].f.cut()

        self.assertEqual(a.f.src, '''
match a:
  case 1:
    if 1:
  case 2:
    try:
  case 2:
    for a in b:
  case 3:
    async for a in b:
  case 4:
    while a in b:
  case 5:
    with a as b:
  case 6:
    async with a as b:
  case 7:
    def func():
  case 8:
    async def func():
  case 9:
    class cls:
'''.strip())

        with FST.options(norm=False):
            a.body[0].cases[9].body[0].f.cut()
            a.body[0].cases[8].body[0].f.cut()
            a.body[0].cases[7].body[0].f.cut()
            a.body[0].cases[6].body[0].f.cut()
            a.body[0].cases[5].body[0].f.cut()
            a.body[0].cases[4].body[0].f.cut()
            a.body[0].cases[3].body[0].f.cut()
            a.body[0].cases[2].body[0].f.cut()
            a.body[0].cases[1].body[0].f.cut()
            a.body[0].cases[0].body[0].f.cut()

        self.assertEqual(a.f.src, '''
match a:
  case 1:
  case 2:
  case 2:
  case 3:
  case 4:
  case 5:
  case 6:
  case 7:
  case 8:
  case 9:
'''.strip())

        with FST.options(norm=False):
            a.body[0].cases[9].f.cut()
            a.body[0].cases[8].f.cut()
            a.body[0].cases[7].f.cut()
            a.body[0].cases[6].f.cut()
            a.body[0].cases[5].f.cut()
            a.body[0].cases[4].f.cut()
            a.body[0].cases[3].f.cut()
            a.body[0].cases[2].f.cut()
            a.body[0].cases[1].f.cut()
            a.body[0].cases[0].f.cut()

        self.assertEqual(a.f.src, '''match a:''')

    def test_cut_and_del_stmtish_special(self):  # TODO: legacy, do better when possible
        fst = parse('''
match a:
    case 1:  # CASE
        i = 1

match b:  # MATCH
    case 2:
        pass  # this is removed

if 1:  # IF
    j; k
else:  # ELSE
    l ; \\
  m

try:  # TRY
    # pre
    n  # post
except:  # EXCEPT
    if 1: break
else:  # delelse
    if 2: continue
    elif 3: o
    else: p
finally:  # delfinally
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q

for a in b:  # FOR
    # pre-classdeco
    @classdeco
    class cls:
        @methdeco
        def meth(self):
            mvar = 5  # post-meth
else:  # delelse
    """Multi
    line # notcomment
    string."""

async for a in b:  # ASYNC FOR
    ("Multi"
     "line  # notcomment"
     "string \\\\ not linecont")
else:  # delelse
    r = [i for i in range(100)]  # post-list-comprehension

while a in b:  # WHILE
    # pre-global
    global c
else:  # delelse
    lambda x: x**2

with a as b:  # WITH
    try: a ; #  post-try
    except: b ; c  # post-except
    else: return 5
    finally: yield 6

async with a as b:  # ASYNC WITH
    del x, y, z

def func(a = """ \\\\ not linecont
            # notcomment"""):  # FUNC
    assert s, t

@asyncdeco
async def func():  # ASYNC FUNC
    match z:
        case 1: zz
        case 2:
            zzz

class cls:  # CLASS
    def docfunc(a, /, b=2, *c, d=""" # not \\\\ linecont
            # comment
            """, **e):
        """Doc
        string # ."""

        return -1

if clause:
    while something:  # WHILE
        yield from blah
    else:  # delelse
        @funcdeco
        def func(args) -> list[int]:
            return [2]

if indented:
    try:  # TRY
        try: raise
        except Exception as exc:
            raise exc from exc
    except:  # EXCEPT
        aa or bb or cc
    else:  # delelse
        f'{i:2} plus 1'
    finally:  # delelse
        j = (i := k)
'''.lstrip()).f

        fst2 = fst.copy()

        # fst.a.body[1].cases[0].f.cut()
        # fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),

            (fst.a.body[3].f, 'body'),
            (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'orelse'),

            (fst.a.body[13].body[0].f, 'body'),
            (fst.a.body[13].body[0].f, 'handlers'),
            (fst.a.body[13].body[0].f, 'orelse'),
            (fst.a.body[13].body[0].f, 'finalbody'),
        ]

        lines = []

        for point, field in points:
            f = point.get_slice(field=field, cut=True, norm=False)

            lines.extend(f.lines)
            lines.append('...')

        lines.extend(fst.lines)

        # print('...')
        # print('\n'.join(repr(l) for l in lines))
        # print('...')

        self.assertEqual(lines, [
            'i = 1',
            '...',
            'case 2:',
            '    pass  # this is removed',
            '...',
            'j; k',
            '...',
            'l ; \\',
            'm',
            '...',
            '# pre',
            'n  # post',
            '...',
            'except:  # EXCEPT',
            '    if 1: break',
            '...',
            'if 2: continue',
            'elif 3: o',
            'else: p',
            '...',
            '@deco',
            'def inner() -> list[int]:',
            '    q = 4  # post-inner-q',
            '...',
            '# pre-classdeco',
            '@classdeco',
            'class cls:',
            '    @methdeco',
            '    def meth(self):',
            '        mvar = 5  # post-meth',
            '...',
            '"""Multi',
            'line # notcomment',
            'string."""',
            '...',
            '("Multi"',
            ' "line  # notcomment"',
            ' "string \\\\ not linecont")',
            '...',
            'r = [i for i in range(100)]  # post-list-comprehension',
            '...',
            '# pre-global',
            'global c',
            '...',
            'lambda x: x**2',
            '...',
            'try: a ; #  post-try',
            'except: b ; c  # post-except',
            'else: return 5',
            'finally: yield 6',
            '...',
            'del x, y, z',
            '...',
            'assert s, t',
            '...',
            'match z:',
            '    case 1: zz',
            '    case 2:',
            '        zzz',
            '...',
            'def docfunc(a, /, b=2, *c, d=""" # not \\\\ linecont',
            '            # comment',
            '            """, **e):',
            '    """Doc',
            '    string # ."""',
            '',
            '    return -1',
            '...',
            'yield from blah',
            '...',
            '@funcdeco',
            'def func(args) -> list[int]:',
            '    return [2]',
            '...',
            'try: raise',
            'except Exception as exc:',
            '    raise exc from exc',
            '...',
            'except:  # EXCEPT',
            '    aa or bb or cc',
            '...',
            "f'{i:2} plus 1'",
            '...',
            'j = (i := k)',
            '...',
            'match a:',
            '    case 1:  # CASE',
            '',
            'match b:  # MATCH',
            '',
            'if 1:  # IF',
            '',
            'try:  # TRY',
            '',
            'for a in b:  # FOR',
            '',
            'async for a in b:  # ASYNC FOR',
            '',
            'while a in b:  # WHILE',
            '',
            'with a as b:  # WITH',
            '',
            'async with a as b:  # ASYNC WITH',
            '',
            'def func(a = """ \\\\ not linecont',
            '            # notcomment"""):  # FUNC',
            '',
            '@asyncdeco',
            'async def func():  # ASYNC FUNC',
            '',
            'class cls:  # CLASS',
            '',
            'if clause:',
            '    while something:  # WHILE',
            '',
            'if indented:',
            '    try:  # TRY',
            '',
        ])

        fst = fst2

        # fst.a.body[1].cases[0].f.cut()
        # fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            # (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),

            (fst.a.body[3].f, 'body'),
            # (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'orelse'),

            (fst.a.body[13].body[0].f, 'body'),
            # (fst.a.body[13].body[0].f, 'handlers'),
            (fst.a.body[13].body[0].f, 'orelse'),
            (fst.a.body[13].body[0].f, 'finalbody'),
        ]

        for point, field in points:
            point.put_slice(None, field=field, norm=False)#, check_node_type=False)

        # print('...')
        # print('\n'.join(repr(l) for l in fst.lines))
        # print('...')

        self.assertEqual(fst.lines, [
            'match a:',
            '    case 1:  # CASE',
            '',
            'match b:  # MATCH',
            '    case 2:',
            '        pass  # this is removed',
            '',
            'if 1:  # IF',
            '',
            'try:  # TRY',
            'except:  # EXCEPT',
            '    if 1: break',
            '',
            'for a in b:  # FOR',
            '',
            'async for a in b:  # ASYNC FOR',
            '',
            'while a in b:  # WHILE',
            '',
            'with a as b:  # WITH',
            '',
            'async with a as b:  # ASYNC WITH',
            '',
            'def func(a = """ \\\\ not linecont',
            '            # notcomment"""):  # FUNC',
            '',
            '@asyncdeco',
            'async def func():  # ASYNC FUNC',
            '',
            'class cls:  # CLASS',
            '',
            'if clause:',
            '    while something:  # WHILE',
            '',
            'if indented:',
            '    try:  # TRY',
            '    except:  # EXCEPT',
            '        aa or bb or cc',
            '',
        ])

        fst = parse('''
match a:
    case 1:  \\
  # CASE
        i = 1

match b:  \\
  # MATCH
    case 2:
        pass  # this is removed

if 1:  \\
  # IF
    j; k
else:  \\
  # ELSE
    l ; \\
      m

try:  \\
  # TRY
    # pre
    n  # post
except:  \\
  # EXCEPT
    if 1: break
else:  \\
  # delelse
    if 2: continue
    elif 3: o
    else: p
finally:  \\
  # delfinally
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q

for a in b:  \\
  # FOR
    # pre-classdeco
    @classdeco
    class cls:
        @methdeco
        def meth(self):
            mvar = 5  # post-meth
else:  \\
  # delelse
    """Multi
    line # notcomment
    string."""

async for a in b:  \\
  # ASYNC FOR
    ("Multi"
     "line  # notcomment"
     "string \\\\ not linecont")
else:  \\
  # delelse
    r = [i for i in range(100)]  # post-list-comprehension

while a in b:  \\
  # WHILE
    # pre-global
    global c
else:  \\
  # delelse
    lambda x: x**2

with a as b:  \\
  # WITH
    try: a ; #  post-try
    except: b ; c  # post-except
    else: return 5
    finally: yield 6

async with a as b:  \\
  # ASYNC WITH
    del x, y, z

def func(a = """ \\\\ not linecont
            # notcomment"""):  \\
  # FUNC
    assert s, t

@asyncdeco
async def func():  \\
  # ASYNC FUNC
    match z:
        case 1: zz
        case 2:
            zzz

class cls:  \\
  # CLASS
    def docfunc(a, /, b=2, *c, d=""" # not \\\\ linecont
            # comment
            """, **e):
        """Doc
        string # ."""

        return -1

if clause:
    while something:  \\
  # WHILE
        yield from blah
    else:  \\
  # delelse
        @funcdeco
        def func(args) -> list[int]:
            return [2]

if indented:
    try:  \\
  # TRY
        try: raise
        except Exception as exc:
            raise exc from exc
    except:  \\
  # EXCEPT
        aa or bb or cc
    else:  \\
  # delelse
        f'{i:2} plus 1'
    finally:  \\
  # delelse
        j = (i := k)
'''.lstrip()).f

        fst2 = fst.copy()

        # fst.a.body[1].cases[0].f.cut()
        # fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            # (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),

            (fst.a.body[3].f, 'body'),
            # (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'orelse'),

            (fst.a.body[13].body[0].f, 'body'),
            # (fst.a.body[13].body[0].f, 'handlers'),
            (fst.a.body[13].body[0].f, 'orelse'),
            (fst.a.body[13].body[0].f, 'finalbody'),
        ]

        lines = []

        for point, field in points:
            f = point.get_slice(field=field, cut=True, norm=False)

            lines.extend(f.lines)
            lines.append('...')

        lines.extend(fst.lines)

        # print('...')
        # print('\n'.join(repr(l) for l in lines))
        # print('...')

        self.assertEqual(lines, [
            '# CASE',
            'i = 1',
            '...',
            '# IF',
            'j; k',
            '...',
            '# ELSE',
            'l ; \\',
            '  m',
            '...',
            '# TRY',
            '# pre',
            'n  # post',
            '...',
            '# delelse',
            'if 2: continue',
            'elif 3: o',
            'else: p',
            '...',
            '# delfinally',
            '@deco',
            'def inner() -> list[int]:',
            '    q = 4  # post-inner-q',
            '...',
            '# FOR',
            '# pre-classdeco',
            '@classdeco',
            'class cls:',
            '    @methdeco',
            '    def meth(self):',
            '        mvar = 5  # post-meth',
            '...',
            '# delelse',
            '"""Multi',
            'line # notcomment',
            'string."""',
            '...',
            '# ASYNC FOR',
            '("Multi"',
            ' "line  # notcomment"',
            ' "string \\\\ not linecont")',
            '...',
            '# delelse',
            'r = [i for i in range(100)]  # post-list-comprehension',
            '...',
            '# WHILE',
            '# pre-global',
            'global c',
            '...',
            '# delelse',
            'lambda x: x**2',
            '...',
            '# WITH',
            'try: a ; #  post-try',
            'except: b ; c  # post-except',
            'else: return 5',
            'finally: yield 6',
            '...',
            '# ASYNC WITH',
            'del x, y, z',
            '...',
            '# FUNC',
            'assert s, t',
            '...',
            '# ASYNC FUNC',
            'match z:',
            '    case 1: zz',
            '    case 2:',
            '        zzz',
            '...',
            '# CLASS',
            'def docfunc(a, /, b=2, *c, d=""" # not \\\\ linecont',
            '            # comment',
            '            """, **e):',
            '    """Doc',
            '    string # ."""',
            '',
            '    return -1',
            '...',
            '# WHILE',
            'yield from blah',
            '...',
            '# delelse',
            '@funcdeco',
            'def func(args) -> list[int]:',
            '    return [2]',
            '...',
            '# TRY',
            'try: raise',
            'except Exception as exc:',
            '    raise exc from exc',
            '...',
            '# delelse',
            "f'{i:2} plus 1'",
            '...',
            '# delelse',
            'j = (i := k)',
            '...',
            'match a:',
            '    case 1:',
            '',
            'match b:  \\',
            '  # MATCH',
            '    case 2:',
            '        pass  # this is removed',
            '',
            'if 1:',
            '',
            'try:',
            'except:  \\',
            '  # EXCEPT',
            '    if 1: break',
            '',
            'for a in b:',
            '',
            'async for a in b:',
            '',
            'while a in b:',
            '',
            'with a as b:',
            '',
            'async with a as b:',
            '',
            'def func(a = """ \\\\ not linecont',
            '            # notcomment"""):',
            '',
            '@asyncdeco',
            'async def func():',
            '',
            'class cls:',
            '',
            'if clause:',
            '    while something:',
            '',
            'if indented:',
            '    try:',
            '    except:  \\',
            '  # EXCEPT',
            '        aa or bb or cc',
            '',
        ])

        fst = fst2

        # fst.a.body[1].cases[0].f.cut()
        # fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            # (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),

            (fst.a.body[3].f, 'body'),
            # (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            (fst.a.body[12].body[0].f, 'orelse'),

            (fst.a.body[13].body[0].f, 'body'),
            # (fst.a.body[13].body[0].f, 'handlers'),
            (fst.a.body[13].body[0].f, 'orelse'),
            (fst.a.body[13].body[0].f, 'finalbody'),
        ]

        for point, field in points:
            point.put_slice(None, field=field, norm=False)

        # print('...')
        # print('\n'.join(repr(l) for l in fst.lines))
        # print('...')

        self.assertEqual(fst.lines, [
            'match a:',
            '    case 1:',
            '',
            'match b:  \\',
            '  # MATCH',
            '    case 2:',
            '        pass  # this is removed',
            '',
            'if 1:',
            '',
            'try:',
            'except:  \\',
            '  # EXCEPT',
            '    if 1: break',
            '',
            'for a in b:',
            '',
            'async for a in b:',
            '',
            'while a in b:',
            '',
            'with a as b:',
            '',
            'async with a as b:',
            '',
            'def func(a = """ \\\\ not linecont',
            '            # notcomment"""):',
            '',
            '@asyncdeco',
            'async def func():',
            '',
            'class cls:',
            '',
            'if clause:',
            '    while something:',
            '',
            'if indented:',
            '    try:',
            '    except:  \\',
            '  # EXCEPT',
            '        aa or bb or cc',
            '',
        ])

    def test_cut_block_everything(self):
        for src in ('''
if mo:
    if 1:
        a = 1
        b = 2
    else:
        c = 3
else:
    d = 4
''', '''
try:
    pass
except:
    try:
        pass
    except:
        pass
else:
    pass
''', '''
def func(args):
    pass
''', '''
@decorator(arg)
def func():
    pass
'''     ):

            ast  = parse(src.strip())
            asts = [a for a in walk(ast) if a.__class__ in ASTS_LEAF_STMTISH]

            for a in asts[::-1]:
                a.f.cut(norm=False)

            ast  = parse(src.strip())
            asts = [a for a in walk(ast) if a.__class__ in ASTS_LEAF_STMTISH]

            for a in asts[::-1]:
                field, idx = a.f.pfield

                a.f.parent.put_slice(None, idx, idx + 1, field, norm=False)

    def test_cut_and_del_slice_matchseq(self):
        f = FST('[a, b, c]', pattern)
        self.assertEqual('[c]', f.get_slice(2, 'end', cut=True).src)
        self.assertEqual('[a, b]', f.src)
        self.assertEqual('[b]', f.get_slice(1, 'end', cut=True).src)
        self.assertEqual('[a]', f.src)
        self.assertEqual('[a]', f.get_slice(0, 'end', cut=True).src)
        self.assertEqual('[]', f.src)

        f = FST('(a, b, c)', pattern)
        self.assertEqual('(c,)', f.get_slice(2, 'end', cut=True).src)
        self.assertEqual('(a, b)', f.src)
        self.assertEqual('(b,)', f.get_slice(1, 'end', cut=True).src)
        self.assertEqual('(a,)', f.src)
        self.assertEqual('(a,)', f.get_slice(0, 'end', cut=True).src)
        self.assertEqual('()', f.src)

        f = FST('a, b, c', pattern)
        self.assertEqual('c,', f.get_slice(2, 'end', cut=True).src)
        self.assertEqual('a, b', f.src)
        self.assertEqual('b,', f.get_slice(1, 'end', cut=True).src)
        self.assertEqual('a,', f.src)
        self.assertEqual('a,', f.get_slice(0, 'end', cut=True).src)
        self.assertEqual('[]', f.src)

        f = FST('[a, b, c]', pattern)
        f.put_slice(None, 2, 'end')
        self.assertEqual('[a, b]', f.src)
        f.put_slice(None, 1, 'end')
        self.assertEqual('[a]', f.src)
        f.put_slice(None, 0, 'end')
        self.assertEqual('[]', f.src)

        f = FST('(a, b, c)', pattern)
        f.put_slice(None, 2, 'end')
        self.assertEqual('(a, b)', f.src)
        f.put_slice(None, 1, 'end')
        self.assertEqual('(a,)', f.src)
        f.put_slice(None, 0, 'end')
        self.assertEqual('()', f.src)

        f = FST('a, b, c', pattern)
        f.put_slice(None, 2, 'end')
        self.assertEqual('a, b', f.src)
        f.put_slice(None, 1, 'end')
        self.assertEqual('a,', f.src)
        f.put_slice(None, 0, 'end')
        self.assertEqual('[]', f.src)

        f = FST('a, b, c', pattern)
        f.put_slice(None, 0, 1)
        self.assertEqual('b, c', f.src)
        f.put_slice(None, 0, 1)
        self.assertEqual('c,', f.src)
        f.put_slice(None, 0, 1)
        self.assertEqual('[]', f.src)

        f = FST('1,\\\n2,\\\n3,\\\n4,\\\n', pattern)
        self.assertEqual('[\n2,\\\n3,\\\n]', f.get_slice(1, 3).src)

    def test_cut_and_del_slice_matchmap(self):
        f = FST('{1: a, 2: b, **z}', pattern)
        self.assertEqual('{2: b}', f.get_slice(1, 2, cut=True).src)
        self.assertEqual('{1: a, **z}', f.src)

        f = FST('{1: a, 2: b, **z}', pattern)
        f.put_slice(None, 1, 2)
        self.assertEqual('{1: a, **z}', f.src)

        f = FST('{1: a, **z}', pattern)
        self.assertEqual('{1: a}', f.get_slice(0, 1, cut=True).src)
        self.assertEqual('{**z}', f.src)

        f = FST('{1: a, **z}', pattern)
        f.put_slice(None, 0, 1)
        self.assertEqual('{**z}', f.src)

        f = FST('{1: a, **z}', pattern)
        f.put_slice('{2: b}', 0, 1)
        self.assertEqual('{2: b, **z}', f.src)

        f = FST('{1: a, **z}', pattern)
        f.put_slice('{2: b}', 1, 1)
        self.assertEqual('{1: a, 2: b, **z}', f.src)

        f = FST('{1: a, 2: b}', pattern)
        self.assertEqual('{2: b}', f.get_slice(1, 2, cut=True).src)
        self.assertEqual('{1: a}', f.src)

        f = FST('{1: a, 2: b}', pattern)
        f.put_slice(None, 1, 2)
        self.assertEqual('{1: a}', f.src)

        f = FST('{1: a}', pattern)
        self.assertEqual('{1: a}', f.get_slice(0, 1, cut=True).src)
        self.assertEqual('{}', f.src)

        f = FST('{1: a}', pattern)
        f.put_slice(None, 0, 1)
        self.assertEqual('{}', f.src)

        f = FST('{1: a}', pattern)
        f.put_slice('{2: b}', 0, 1)
        self.assertEqual('{2: b}', f.src)

        f = FST('{1: a}', pattern)
        f.put_slice('{2: b}', 1, 1)
        self.assertEqual('{1: a, 2: b}', f.src)

    def test_cut_and_del_slice_delete(self):
        with FST.options(norm=True):
            f = FST('del a, b, c')
            self.assertRaises(ValueError, f.get_slice, cut=True)

            f = FST('del a, b, c')
            self.assertRaises(ValueError, f.put_slice, None)

            f = FST('del a, b, c')
            self.assertEqual('a, b, c', f.get_slice(cut=True, norm_self=False).src)
            self.assertEqual('del ', f.src)
            f.put_slice('x, y, z')
            self.assertEqual('del x, y, z', f.src)

            f = FST('del a, b, c')
            self.assertEqual('del ', f.put_slice(None, norm_self=False).src)
            f.put_slice('x, y, z')
            self.assertEqual('del x, y, z', f.src)

    def test_cut_and_del_slice_assign(self):
        with FST.options(norm=True):
            f = FST('a = b = c = q')
            self.assertRaises(ValueError, f.get_slice, 'targets', cut=True)

            f = FST('a = b = c = q')
            self.assertRaises(ValueError, f.put_slice, None, 'targets')

            f = FST('a = b = c = q')
            self.assertEqual('a = b = c =', f.get_slice('targets', cut=True, norm_self=False).src)
            self.assertEqual(' q', f.src)
            f.put_slice('x = y = z', 'targets')
            self.assertEqual('x = y = z = q', f.src)

            f = FST('a = b = c = q')
            self.assertEqual(' q', f.put_slice(None, 'targets', norm_self=False).src)
            f.put_slice('x = y = z =', 'targets')
            self.assertEqual('x = y = z = q', f.src)

    def test_cut_and_del_slice_import(self):
        with FST.options(norm=True):
            f = FST('import a, b, c')
            self.assertRaises(ValueError, f.get_slice, cut=True)

            f = FST('import a, b, c')
            self.assertRaises(ValueError, f.put_slice, None)

            f = FST('import a, b, c')
            self.assertEqual('a, b, c', f.get_slice(cut=True, norm_self=False).src)
            self.assertEqual('import ', f.src)
            f.put_slice('x, y, z')
            self.assertEqual('import x, y, z', f.src)

            f = FST('import a, b, c')
            self.assertEqual('import ', f.put_slice(None, norm_self=False).src)
            f.put_slice('x, y, z')
            self.assertEqual('import x, y, z', f.src)

    def test_cut_and_del_slice_global_and_nonlocal(self):
        with FST.options(norm=True):
            # global

            f = FST('global a, b, c')
            self.assertRaises(ValueError, f.get_slice, cut=True)

            f = FST('global a, b, c')
            self.assertRaises(ValueError, f.put_slice, None)

            f = FST('global a, b, c')
            self.assertEqual('a, b, c', f.get_slice(cut=True, norm_self=False).src)
            self.assertEqual('global ', f.src)
            f.put_slice('x, y, z')
            self.assertEqual('global x, y, z', f.src)

            f = FST('global a, b, c')
            self.assertEqual('global ', f.put_slice(None, norm_self=False).src)
            f.put_slice('x, y, z')
            self.assertEqual('global x, y, z', f.src)

            # nonlocal

            f = FST('nonlocal a, b, c')
            self.assertRaises(ValueError, f.get_slice, cut=True)

            f = FST('nonlocal a, b, c')
            self.assertRaises(ValueError, f.put_slice, None)

            f = FST('nonlocal a, b, c')
            self.assertEqual('a, b, c', f.get_slice(cut=True, norm_self=False).src)
            self.assertEqual('nonlocal ', f.src)
            f.put_slice('x, y, z')
            self.assertEqual('nonlocal x, y, z', f.src)

            f = FST('nonlocal a, b, c')
            self.assertEqual('nonlocal ', f.put_slice(None, norm_self=False).src)
            f.put_slice('x, y, z')
            self.assertEqual('nonlocal x, y, z', f.src)

    def test_get_slice_param_matrix(self):
        f = FST('[a, b, c]')

        self.assertEqual('[b]', f.get_slice(1, 2).src)
        self.assertRaises(IndexError, f.get_slice, 'end', 2)
        self.assertEqual('[b, c]', f.get_slice(1, 'end').src)
        self.assertEqual('[]', f.get_slice('end', 'end').src)

    def test_put_slice_param_matrix(self):
        self.assertEqual('[a, x, c]', FST('[a, b, c]').put_slice('[x]', 1, 2).src)
        self.assertRaises(IndexError, FST('[a, b, c]').put_slice,'[x]', 'end', 2)
        self.assertEqual('[a, x]', FST('[a, b, c]').put_slice('[x]', 1, 'end').src)
        self.assertEqual('[a, b, c, x]', FST('[a, b, c]').put_slice('[x]', 'end', 'end').src)

        self.assertEqual('[a, [x], c]', FST('[a, b, c]').put_slice('[x]', 1, 2, one=True).src)
        self.assertRaises(IndexError, FST('[a, b, c]').put_slice,'[x]', 'end', 2, one=True)
        self.assertEqual('[a, [x]]', FST('[a, b, c]').put_slice('[x]', 1, 'end', one=True).src)
        self.assertEqual('[a, b, c, [x]]', FST('[a, b, c]').put_slice('[x]', 'end', 'end', one=True).src)

    def test_replace_with_slice(self):
        f = FST('a\nb\nc')
        self.assertRaises(ValueError, f.body[1].replace, 'x\ny')
        self.assertEqual('x', f.body[1].replace('x\ny', one=False).src)
        self.assertEqual('a\nx\ny\nc', f.src)
        f.verify()
        self.assertIsNone(f.body[1].replace(None, one=False))
        self.assertEqual('a\ny\nc', f.src)
        f.verify()

        f = FST('[a, b, c]')
        self.assertEqual('[x, y]', f.elts[1].replace('[x, y]').src)
        self.assertEqual('[a, [x, y], c]', f.src)
        f.verify()
        self.assertEqual('x', f.elts[1].replace('[x, y]', one=False).src)
        self.assertEqual('[a, x, y, c]', f.src)
        f.verify()
        self.assertIsNone(f.elts[1].replace(None, one=False))
        self.assertEqual('[a, y, c]', f.src)

    def test_slice_coverage(self):
        # misc stuff to fill out test coverage

        self.assertRaises(ValueError, FST('a or b').get_slice, 0, 0, norm_get=True)

        self.assertEqual('case 2, 1 | c: pass', (f := FST('case 2, 1 | "a": pass')).pattern.patterns[1].put_slice('c', 1, 2, norm=True).root.src)
        f.verify()

        self.assertRaises(ValueError, FST('pass').get)
        self.assertRaises(ValueError, FST('pass').get, 'nonexistent_field')
        self.assertRaises(ValueError, FST('a = b').get_slice, 'value')

        from fst.fst_get_slice import _maybe_fix_MatchSequence
        f = FST('a, b', 'MatchSequence')
        del f.a.patterns[-1]
        f.put_src(None, 0, 1, 0, 4, 'offset')
        _maybe_fix_MatchSequence(f)
        self.assertEqual('a,', f.src)
        f.verify()

        self.assertRaises(ValueError, FST('a = 1', 'exec').put_slice, 'x', 0, 1, pep8space=3)
        self.assertRaises(ValueError, FST('a = 1', 'exec').put_slice, 'x', 0, 0, pep8space=3)

    def test_slice_special(self):
        # Global.names preserves trailing commas and locations

        f = FST(src := r'''
del a \
, \
b \
, \
c  # comment
            '''.strip())
        g = f.get_slice(1, 2, cut=True)
        f.put_slice(g, 1, 1)
        self.assertEqual(f.src, src)
        f.verify()

        f = FST(src := r'''
a = \
b = \
c = \
d  # comment
            '''.strip())
        g = f.get_slice(1, 2, 'targets', cut=True)
        f.put_slice(g, 1, 1, 'targets')
        self.assertEqual(f.src, src)
        f.verify()

        # Import.names slice doesn't preserve trailing commas (or their locations)

        f = FST(src := r'''
import a \
, \
b, \
c  # comment
            '''.strip())
        g = f.get_slice(1, 2, cut=True)
        f.put_slice(g, 1, 1)
        self.assertEqual(f.src, src)
        f.verify()

        # Global.names preserves trailing commas and locations

        f = FST(src := r'''
global a \
, \
b \
, \
c  # comment
            '''.strip())
        g = f.get_slice(1, 2, cut=True)
        f.put_slice(g, 1, 1)
        self.assertEqual(f.src, src)
        f.verify()

        # Assign target 0 must always start at same position as Assign

        (f := FST('a = \\\n  \\\n b = z')).get_slice(0, 1, 'targets', cut=True)
        self.assertEqual('b = z', f.src)
        f.verify()

        self.assertEqual('b = z', (f := FST('a = \\\n  \\\n b = z')).put_slice(None, 0, 1, 'targets').src)
        f.verify()

        self.assertEqual('c = b = z', (f := FST('a = b = z')).put_slice('\\\n  \\\n c =', 0, 1, 'targets').src)
        f.verify()

        (f := FST('a = \\\n  \\\n (b) = z')).get_slice(0, 1, 'targets', cut=True)
        self.assertEqual('(b) = z', f.src)
        f.verify()

        self.assertEqual('(b) = z', (f := FST('a = \\\n  \\\n (b) = z')).put_slice(None, 0, 1, 'targets').src)
        f.verify()

        self.assertEqual('(c) = b = z', (f := FST('a = b = z')).put_slice('\\\n  \\\n (c) =', 0, 1, 'targets').src)
        f.verify()

    def test_slice_special_BoolOp(self):
        # joined alnum

        self.assertEqual('a if 1 else 0', (f := FST('a and(b)if 1 else 0')).body.put_slice(None, 1, 2, norm=True).root.src)
        f.verify()

        self.assertEqual('2 if 1 else b', (f := FST('2 if 1 else(a)and b')).orelse.put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        self.assertEqual('(a)and x and y', (f := FST('(a)and(b)')).put_slice('x and y', 1, 2, norm=True).root.src)
        f.verify()

        self.assertEqual('(a)and x and y and(c)', (f := FST('(a)and(b)and(c)')).put_slice('x and y', 1, 2, norm=True).root.src)
        f.verify()

        self.assertEqual('(a)and c', (f := FST('(a)and(b)and c')).put_slice(None, 1, 2, norm=True).root.src)
        f.verify()

        self.assertEqual('(a)and d', (f := FST('(a)and(b)and(c)and d')).put_slice(None, 1, 3, norm=True).root.src)
        f.verify()

        # start and end positions

        f = FST(r'''
if"repository"or ext_data["jupyterlab"] if b else c:
    pass
            '''.strip())
        self.assertEqual(r'''
if "extension" or ext_data["jupyterlab"] if b else c:
    pass
            '''.strip(), f.test.body.put_slice('"extension"', 0, 1).root.src)
        f.verify()

        f = FST(r'''
if as_upstream if 1 \
else b or\
 b\
 :
    pass
            '''.strip())
        g = FST('name\\\nor 0').get_slice(0, 1)
        self.assertEqual(r'''
if as_upstream if 1 \
else b or\
 name\
 \
 :
    pass
            '''.strip(), f.test.orelse.put_slice(g, 1, 2, trivia=('all+', 'none+2')).root.src)
        f.verify()

        # VERY SPECIAL CASE of child of Expr leaving a leading line continuation on delete which is not aligned with indentation

        f = FST(r'''
if 1:
    a \
 and \
 b and c
    pass
            '''.strip())
        self.assertEqual(r'''
if 1:
    \
 b and c
    pass
            '''.strip(), f.body[0].value.put_slice(None, 0, 1).root.src)
        f.verify()

        f = FST(r'''
if 1:
    a \
 and \
 b
    pass
            '''.strip())
        self.assertEqual(r'''
if 1:
    \
 b
    pass
            '''.strip(), f.body[0].value.put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        f = FST(r'''
if 1:
    a \
 and \
 b
    pass
            '''.strip())
        self.assertEqual(r'''
if 1:
    \
 b
    pass
            '''.strip(), f.body[0].value.put_slice(None, 0, 1).root.src)
        # f.verify()  # no verify() because was not normalized

        f = FST(r'''
if 1:
    pass
    a and \
       b and c if d else e
            '''.strip())
        self.assertEqual(r'''
if 1:
    pass
    \
       b and c if d else e
            '''.strip(), f.body[1].value.body.put_slice(None, 0, 1).root.src)
        f.verify()

        f = FST(r'''
if 1:
    pass
    a and \
       b if d else e
            '''.strip())
        self.assertEqual(r'''
if 1:
    pass
    \
       b if d else e
            '''.strip(), f.body[1].value.body.put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        f = FST(r'''
if 1:
    pass
    a and \
       b if d else e
            '''.strip())
        self.assertEqual(r'''
if 1:
    pass
    \
       b if d else e
            '''.strip(), f.body[1].value.body.put_slice(None, 0, 1).root.src)
        # f.verify()  # no verify() because was not normalized

        f = FST(r'''
if 1:
    pass ; \
    a and \
       b if d else e
            '''.strip())
        self.assertEqual(r'''
if 1:
    pass ; \
    \
       b if d else e
            '''.strip(), f.body[1].value.body.put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        f = FST(r'''
pass
a and \
    b if d else e
            '''.strip())
        self.assertEqual(r'''
pass
b if d else e
            '''.strip(), f.body[1].value.body.put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        f = FST(r'''
pass ; \
a and \
    b if d else e
            '''.strip())
        self.assertEqual(r'''
pass ; \
b if d else e
            '''.strip(), f.body[1].value.body.put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        # make sure enclosed and parsable

        f = FST(r'''
if  \
  a and \
  a and \
  a and \
  a:
      pass
            '''.strip())
        f.test.get_slice(0, 2, cut=True)
        self.assertEqual(r'''
if  \
  (
  a and \
  a):
      pass
            '''.strip(), f.root.src)
        f.verify()

        f = FST(r'''
if a and \
  a and \
  a and \
  a:
      pass
            '''.strip())
        f.test.get_slice(0, 2, cut=True)
        self.assertEqual(r'''
if (
  a and \
  a):
      pass
            '''.strip(), f.root.src)
        f.verify()

        # putting slice at end of sequence which ends exactly where a parent .format_spec starts

        if PYGE12:
            self.assertEqual("f'{x and y:<12}'", (f := FST("f'{a and b and c:<12}'")).values[0].value.put_slice('x and y', 0, 3).root.src)
            f.verify()

        # 'and' and 'or' may be part of non-operator identifiers

        self.assertEqual('a or x is y or org is b', (f := FST('a or org is b')).put_slice('x is y', 1, 1).root.src)
        f.verify()

        self.assertEqual('a and x is y and andy is b', (f := FST('a and andy is b')).put_slice('x is y', 1, 1).root.src)
        f.verify()

        # had random error in _loc_With_items_pars() because of intermediate expression before fix

        self.assertEqual('with (\n     (x) or (a) or b or (c)): pass'.strip(), (f := FST('with (a) or b or (c): pass')).items[0].context_expr.put_slice('\n(x)', 0, 0).root.src)
        f.verify()

        # put empty slice

        f = FST('a or b')
        f.put_slice(None)
        self.assertEqual('', f.src)
        self.assertEqual(0, len(f.a.values))

        self.assertEqual('x or z', FST('x or y or z').put_slice(f, 1, 2).src)

        # can't put incompatible op type without coercion

        self.assertRaises(ValueError, FST('a or b').put_slice, 'x and y', coerce=False)

        # parenthesize tuple put as one

        self.assertEqual('a or (x, y) or d', FST('a or b or c or d').put_slice('x, y', 1, 3).src)

        # other misc

        f = FST(r'''
a or b \
\
  if 1 else 2
            '''.strip(), 'exec')
        self.assertEqual('if 1 else 2', f.body[0].value.body.put_slice(None).root.src)

        f = FST(r'''
a or b \
\

'''.lstrip(), 'exec')
        self.assertEqual('\n', f.body[0].value.put_slice(None).root.src)

        self.assertEqual('(a or x\nor c)', FST('a or b or c').put_slice(['x', 'or'], 1, 2).src)

    def test_slice_special_Compare(self):
        self.assertRaises(ValueError, FST('a < b').get_slice, 0, 0)
        self.assertRaises(ValueError, FST('a < b').get_slice, 0, 0, norm=True)

        # joined alnum

        self.assertEqual('a< x and c', (f := FST('a<(b)and c')).values[0].put_slice('x', 1, 2).root.src)
        f.verify()

        self.assertEqual('1 if 2 else b<c', (f := FST('1 if 2 else(a)<b<c')).orelse.put_slice(None, 0, 1).root.src)
        f.verify()

        self.assertEqual('a and x <c', (f := FST('a and(b)<c')).values[1].put_slice('x', 0, 1).root.src)
        f.verify()

        self.assertEqual('a is not x not in c', (f := FST('a is not(b)not in c')).put_slice('x', 1, 2).root.src)
        f.verify()

        self.assertEqual('a is c', (f := FST('a!= b is c')).put_slice(None, 1, 2).root.src)
        f.verify()

        self.assertEqual('a is c', (f := FST('a is(b)!=c')).put_slice(None, 1, 2, op_side='right').root.src)
        f.verify()

        # start and end positions

        f = FST(r'''
if"repository"in ext_data["jupyterlab"] and b:
    pass
            '''.strip())
        self.assertEqual(r'''
if "extension" in ext_data["jupyterlab"] and b:
    pass
            '''.strip(), f.test.values[0].put_slice('"extension"', 0, 1).root.src)
        f.verify()

        f = FST(r'''
if as_upstream \
and b in\
 b\
 :
    pass
            '''.strip())
        g = FST('name\\\n< 0').get_slice(0, 1)
        self.assertEqual(r'''
if as_upstream \
and b in\
 name\
 \
 :
    pass
            '''.strip(), f.test.values[1].put_slice(g, 1, 2, trivia=('all+', 'none+2')).root.src)
        f.verify()

        # VERY SPECIAL CASE of child of Expr leaving a leading line continuation on delete which is not aligned with indentation

        f = FST(r'''
if 1:
    a \
 in \
 b in c
    pass
            '''.strip())
        self.assertEqual(r'''
if 1:
    \
 b in c
    pass
            '''.strip(), f.body[0].value.put_slice(None, 0, 1).root.src)
        f.verify()

        f = FST(r'''
if 1:
    a \
 in \
 b
    pass
            '''.strip())
        self.assertEqual(r'''
if 1:
    \
 b
    pass
            '''.strip(), f.body[0].value.put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        f = FST(r'''
if 1:
    a \
 in \
 b
    pass
            '''.strip())
        self.assertEqual(r'''
if 1:
    \
 b
    pass
            '''.strip(), f.body[0].value.put_slice(None, 0, 1).root.src)
        # f.verify()  # no verify() because was not normalized

        f = FST(r'''
if 1:
    pass
    a in \
       b in c or d
            '''.strip())
        self.assertEqual(r'''
if 1:
    pass
    \
       b in c or d
            '''.strip(), f.body[1].value.values[0].put_slice(None, 0, 1).root.src)
        f.verify()

        f = FST(r'''
if 1:
    pass
    a in \
       b or d
            '''.strip())
        self.assertEqual(r'''
if 1:
    pass
    \
       b or d
            '''.strip(), f.body[1].value.values[0].put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        f = FST(r'''
if 1:
    pass
    a in \
       b or d
            '''.strip())
        self.assertEqual(r'''
if 1:
    pass
    \
       b or d
            '''.strip(), f.body[1].value.values[0].put_slice(None, 0, 1).root.src)
        # f.verify()  # no verify() because was not normalized

        f = FST(r'''
if 1:
    pass ; \
    a in \
       b or d
            '''.strip())
        self.assertEqual(r'''
if 1:
    pass ; \
    \
       b or d
            '''.strip(), f.body[1].value.values[0].put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        f = FST(r'''
pass
a in \
    b or d
            '''.strip())
        self.assertEqual(r'''
pass
b or d
            '''.strip(), f.body[1].value.values[0].put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        f = FST(r'''
pass ; \
a in \
    b or d
            '''.strip())
        self.assertEqual(r'''
pass ; \
b or d
            '''.strip(), f.body[1].value.values[0].put_slice(None, 0, 1, norm=True).root.src)
        f.verify()

        # make sure enclosed and parsable

        f = FST(r'''
if  \
  casefolded in \
  casefolded in \
  casefolded in \
  casefolded:
      pass
            '''.strip())
        f.test.get_slice(0, 2, cut=True)
        self.assertEqual(r'''
if  \
  (
  casefolded in \
  casefolded):
      pass
            '''.strip(), f.root.src)
        f.verify()

        f = FST(r'''
if casefolded in \
  casefolded in \
  casefolded in \
  casefolded:
      pass
            '''.strip())
        f.test.get_slice(0, 2, cut=True)
        self.assertEqual(r'''
if (
  casefolded in \
  casefolded):
      pass
            '''.strip(), f.root.src)
        f.verify()

        # putting slice at end of sequence which ends exactly where a parent .format_spec starts

        if PYGE12:
            self.assertEqual("f'{3 == 4:<12}'", (f := FST("f'{4 != 4 == 4:<12}'")).values[0].value.put_slice('3 == 4', 0, 3).root.src)
            f.verify()

        # parenthesize tuple put as one

        self.assertEqual('a < (x, y) > d', FST('a < b == c > d').put_slice('x, y', 1, 3).src)

        # other misc

        self.assertEqual('(a < x\n== c)', FST('a < b > c').put_slice(['x', '=='], 1, 2).src)

        # misc errors

        f = FST(r'''
if 1:
    ('' < """
""") > c
'''.strip())
        self.assertEqual('''('' < """\n""")''', f.body[0].value.get_slice(0, 1).src)
        f.verify()

        self.assertEqual('c < b', (f := FST('a < b', 'exec')).body[0].value.put_slice(' \\\n c', 0, 1).root.src)
        f.verify()

        self.assertEqual('c < b', (f := FST('a < b', 'exec')).body[0].value.put_slice(' \\\n\\\n c', 0, 1).root.src)
        f.verify()

    def test_slice_special_Compare_op(self):
        # invalid

        self.assertRaises(SyntaxError, (f := FST('a < b')).put_slice, 'x', 1, 1, op_side='left', op='?')
        self.assertRaises(NodeError, (f := FST('a < b')).put_slice, 'x', 1, 1, op_side='left', op=Mult)
        self.assertRaises(ValueError, (f := FST('a < b')).put_slice, 'x', 1, 1, op_side='left', op=list)
        self.assertRaises(ValueError, (f := FST('a < b')).put_slice, 'x', 1, 1, op_side='left', op=Mult())
        self.assertRaises(NodeError, (f := FST('a < b')).put_slice, 'x', 1, 1, op_side='left', op=FST('*', Mult))
        self.assertRaises(ValueError, (f := FST('a < b')).put_slice, 'x', 1, 1, op_side='left', op=FST('a + b').left)

        # insert

        self.assertEqual('a is not x < b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='left', op='is not').src)
        f.verify()

        self.assertEqual('a < x is not b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='right', op='is not').src)
        f.verify()

        self.assertEqual('a\nis\nnot\nx < b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='left', op='\nis\nnot\n', pars=False).src)
        f.verify()

        self.assertEqual('a < x\nis\nnot\nb', (f := FST('a < b')).put_slice('x', 1, 1, op_side='right', op='\nis\nnot\n', pars=False).src)
        f.verify()

        self.assertEqual('a # 1\nis # 2\nnot # 3\nx < b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='left', op='# 1\nis # 2\nnot # 3', pars=False).src)
        f.verify()

        self.assertEqual('a < x # 1\nis # 2\nnot # 3\nb', (f := FST('a < b')).put_slice('x', 1, 1, op_side='right', op='# 1\nis # 2\nnot # 3', pars=False).src)
        f.verify()

        self.assertEqual('a is not x < b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='left', op=IsNot).src)
        f.verify()

        self.assertEqual('a < x is not b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='right', op=IsNot).src)
        f.verify()

        self.assertEqual('a is not x < b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='left', op=IsNot()).src)
        f.verify()

        self.assertEqual('a < x is not b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='right', op=IsNot()).src)
        f.verify()

        self.assertEqual('a is not x < b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='left', op=FST('is not', cmpop)).src)
        f.verify()

        self.assertEqual('a < x is not b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='right', op=FST('is not', cmpop)).src)
        f.verify()

        # replace

        self.assertEqual('a is not x', (f := FST('a < b')).put_slice('x', 1, 2, op='is not').src)
        f.verify()

        self.assertEqual('x is not b', (f := FST('a < b')).put_slice('x', 0, 1, op='is not').src)
        f.verify()

        self.assertEqual('a\nis\nnot\nx', (f := FST('a < b')).put_slice('x', 1, 2, op='\nis\nnot\n', pars=False).src)
        f.verify()

        self.assertEqual('x\nis\nnot\nb', (f := FST('a < b')).put_slice('x', 0, 1, op='\nis\nnot\n', pars=False).src)
        f.verify()

        self.assertEqual('a # 1\nis # 2\nnot # 3\nx', (f := FST('a < b')).put_slice('x', 1, 2, op='# 1\nis # 2\nnot # 3', pars=False).src)
        f.verify()

        self.assertEqual('x # 1\nis # 2\nnot # 3\nb', (f := FST('a < b')).put_slice('x', 0, 1, op='# 1\nis # 2\nnot # 3', pars=False).src)
        f.verify()

        self.assertEqual('a is not x', (f := FST('a < b')).put_slice('x', 1, 2, op=IsNot).src)
        f.verify()

        self.assertEqual('x is not b', (f := FST('a < b')).put_slice('x', 0, 1, op=IsNot).src)
        f.verify()

        self.assertEqual('a is not x', (f := FST('a < b')).put_slice('x', 1, 2, op=IsNot()).src)
        f.verify()

        self.assertEqual('x is not b', (f := FST('a < b')).put_slice('x', 0, 1, op=IsNot()).src)
        f.verify()

        self.assertEqual('a is not x', (f := FST('a < b')).put_slice('x', 1, 2, op=FST('is not', cmpop)).src)
        f.verify()

        self.assertEqual('x is not b', (f := FST('a < b')).put_slice('x', 0, 1, op=FST('is not', cmpop)).src)
        f.verify()

        # more replace

        self.assertEqual('a is not x > c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='left', op='is not').src)
        f.verify()

        self.assertEqual('a < x is not c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='right', op='is not').src)
        f.verify()

        self.assertEqual('a\nis\nnot\nx > c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='left', op='\nis\nnot\n', pars=False).src)
        f.verify()

        self.assertEqual('a < x\nis\nnot\nc', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='right', op='\nis\nnot\n', pars=False).src)
        f.verify()

        self.assertEqual('a # 1\nis # 2\nnot # 3\nx > c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='left', op='# 1\nis # 2\nnot # 3', pars=False).src)
        f.verify()

        self.assertEqual('a < x # 1\nis # 2\nnot # 3\nc', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='right', op='# 1\nis # 2\nnot # 3', pars=False).src)
        f.verify()

        self.assertEqual('a is not x > c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='left', op=IsNot).src)
        f.verify()

        self.assertEqual('a < x is not c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='right', op=IsNot).src)
        f.verify()

        self.assertEqual('a is not x > c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='left', op=IsNot()).src)
        f.verify()

        self.assertEqual('a < x is not c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='right', op=IsNot()).src)
        f.verify()

        self.assertEqual('a is not x > c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='left', op=FST('is not', cmpop)).src)
        f.verify()

        self.assertEqual('a < x is not c', (f := FST('a < b > c')).put_slice('x', 1, 2, op_side='right', op=FST('is not', cmpop)).src)
        f.verify()

        # list, if this one works every case works

        self.assertEqual('a is not x < b', (f := FST('a < b')).put_slice('x', 1, 1, op_side='left', op=['is not']).src)
        f.verify()

    def test_get_slice_special(self):
        f = FST('''(
            TI(string="case"),
            )''', pattern)
        g = f.get_slice(0, 1, cut=True)
        self.assertEqual('(\n            )', f.src)
        self.assertEqual('(\n            TI(string="case"),\n)', g.src)

        # With / AsyncWith get doesn't join alnums on cut

        (f := FST('with(a),b: pass')).get_slice(0, 1, 'items', cut=True)
        self.assertEqual('with b: pass', f.src)

        (f := FST('async with(a),b: pass')).get_slice(0, 1, 'items', cut=True)
        self.assertEqual('async with b: pass', f.src)

        # misc error found under py < 3.12

        self.assertEqual('3,', (f := FST("f'{3,}'")).values[0].value.get_slice().src)
        f.verify()

    def test_put_slice_special(self):
        if PYGE14:  # make sure parent Interpolation.str gets modified
            f = FST('t"{(1, 2)}"', 'exec').body[0].value.copy()
            f.values[0].value.put_slice("()")
            self.assertEqual('()', f.values[0].value.src)
            self.assertEqual('()', f.values[0].str)

            f = FST('t"{(1, 2)}"', 'exec').body[0].value.copy()
            f.values[0].value.put("()", None, None, one=False)
            self.assertEqual('()', f.values[0].value.src)
            self.assertEqual('()', f.values[0].str)

        f = FST('a, b = c')
        f.targets[0].put_slice('{z}', 1, 2)
        self.assertEqual('a, z = c', f.src)
        f.verify()

        f = FST('a, b = c')
        self.assertRaises(NodeError, f.targets[0].put_slice, '{z}', 1, 2, one=True)

        f = FST('a, b = c, d')
        f.value.put_slice('(e := ((b + 1), 2))', 1, 2, one=True)
        self.assertEqual('a, b = c, (e := ((b + 1), 2))', f.src)
        f.verify()

        f = FST('a, b = c, d')
        f.value.put_slice('e := f', 1, 2, one=True)
        self.assertEqual('a, b = c, (e := f)', f.src)
        f.verify()

        f = FST('a, b')
        f.put_slice('end := self.Label(),', 1, 2, raw=False)
        self.assertEqual('(a, end := self.Label())', f.src)
        f.verify()

        # patterns

        f = FST('case a | b: pass')
        g = f.pattern.get_slice(cut=True, norm_self=False)
        f.pattern.put_slice(g)
        self.assertEqual('case a | b: pass', f.src)
        f.verify()

        f = FST('a | b', pattern)
        g = f.get_slice(cut=True, norm_self=False)
        f.put_slice(g)
        self.assertEqual('a | b', f.src)
        f.verify()

        f = FST('{0: a, **r}', pattern)
        f.put_slice('{1: b, 2: c}', 0, 1)
        self.assertEqual('{1: b, 2: c, **r}', f.src)
        f.verify()

        # stars and slices

        f = FST('{1, 2}')
        self.assertRaises(NodeError, f.put_slice, FST('x:y:z,', 'expr_slice'))

        f = FST('[1, 2]')
        self.assertRaises(NodeError, f.put_slice, FST('x:y:z,', 'expr_slice'))

        f = FST('[a,] = b')
        self.assertRaises(NodeError, f.targets[0].put_slice, '2,')

        f = FST('del [a]')
        self.assertRaises(NodeError, f.targets[0].put_slice, '2,')

        # f = FST('(1, 2)')
        # self.assertRaises(NodeError, f.put_slice, FST('x:y:z,', 'expr_slice'))
        f = FST('(1, 2)')
        self.assertEqual('(x:y:z,)', f.put_slice(FST('x:y:z,', 'expr_slice')).src)

        f = FST('(a,) = b')
        self.assertRaises(NodeError, f.targets[0].put_slice, '2,')
        f = FST('a, = b')
        self.assertRaises(NodeError, f.targets[0].put_slice, '2,')

        f = FST('del (a,)')
        self.assertRaises(NodeError, f.targets[0].put_slice, '2,')

        if PYLT11:
            f = FST('a[b, c]')
            self.assertEqual('a[(*x,)]', f.slice.put_slice('*x,').root.src)
            f.verify()

            f = FST('a[b, c:d]')
            self.assertEqual('a[(*x,)]', f.slice.put_slice('*x,').root.src)
            f.verify()

            f = FST('a[b, c:d]')
            self.assertEqual('a[(b, *x)]', f.slice.put_slice('*x,', 1, 2).root.src)
            f.verify()

            f = FST('a[b, c:d]')
            self.assertRaises(NodeError, f.slice.put_slice, '*x,', 0, 1)

        else:
            f = FST('a[b, c]')
            self.assertEqual('a[*x,]', f.slice.put_slice('*x,').root.src)
            f.verify()

            f = FST('a[b, c:d]')
            self.assertEqual('a[*x,]', f.slice.put_slice('*x,').root.src)
            f.verify()

            f = FST('a[b, c:d]')
            self.assertEqual('a[b, *x]', f.slice.put_slice('*x,', 1, 2).root.src)
            f.verify()

            f = FST('a[b, c:d]')
            self.assertEqual('a[*x, c:d]', f.slice.put_slice('*x,', 0, 1).root.src)
            f.verify()

        if PYGE14:
            f = FST('except a,: pass')
            self.assertEqual('except (*x,): pass', f.type.put_slice('*x,').root.src)
            f.verify()

            f = FST('except a,: pass')
            self.assertEqual('except (a, *x): pass', f.type.put_slice('*x,', 1, 1).root.src)
            f.verify()

            f = FST('except a, b: pass')
            self.assertEqual('except (a, b, *x): pass', f.type.put_slice('*x,', 2, 2).root.src)
            f.verify()

        # trailing comment without newline

        f = FST('a, b  # comment')
        g = FST('(x, y, z)')
        f.a.end_col_offset = 15
        f._touch()
        g.put_slice(f, 1, 2)
        self.assertEqual('(x, a, b,  # comment\n z)', g.src)

        # enclose leading / traling newlines

        self.assertEqual('z = (\n\n    c, \n    d, b)', (f := FST('z = a, b')).value.put_slice('\n\nc, \nd', 0, 1).root.src)
        f.verify()

        self.assertEqual('case [\n\n     c, \n     d, b]: pass', (f := FST('case a, b: pass')).pattern.put_slice('\n\nc, \nd', 0, 1).root.src)
        f.verify()

        self.assertEqual('case (\n\n     c | \n     d | b): pass', (f := FST('case a | b: pass')).pattern.put_slice('\n\nc | \nd', 0, 1).root.src)
        f.verify()

        f = FST('case a | b: pass')
        self.assertEqual('\n\n# pre\ny # line\n# post\n', (g := FST('(x |\n\n# pre\ny | # line\n# post\n z)', pattern).get_slice(1, 2, trivia=('all+', 'all'))).src)
        self.assertEqual('case (\n\n     # pre\n     y | # line\n     # post\n     b): pass', (f := FST('case a | b: pass')).pattern.put_slice(g, 0, 1).root.src)
        f.verify()

        f = FST('case a | b: pass')
        self.assertEqual('\n\n# pre\n(y | # line\n# post\n z)', (g := FST('(x |\n\n# pre\ny | # line\n# post\n z)', pattern).get_slice(1, 3, trivia=('all+', 'all'))).src)
        self.assertEqual('case (\n\n     # pre\n     y | # line\n     # post\n      z | b): pass', (f := FST('case a | b: pass')).pattern.put_slice(g, 0, 1).root.src)
        f.verify()

        # unparenthesized tuple joined alnum by operation

        self.assertEqual('for i in b, 2: pass', (f := FST('for i in"a", 2: pass')).iter.put_slice('b,', 0, 1).root.src)
        f.verify()

        self.assertEqual('for b, c in a: pass', (f := FST('for (),in a: pass')).target.put_slice('b, c', 0, 1).root.src)
        f.verify()

        self.assertEqual('for (), b, c in a: pass', (f := FST('for (),in a: pass')).target.put_slice('b, c', 1, 1).root.src)
        f.verify()

        self.assertEqual('for b, c in a: pass', (f := FST('for(),in a: pass')).target.put_slice('b, c', 0, 1).root.src)
        f.verify()

        # undelimited matchsequence joined alnum by operation

        self.assertEqual('case b, 2: pass', (f := FST('case"a", 2: pass')).pattern.put_slice('b,', 0, 1).root.src)
        f.verify()

        # matchor joined alnum by operation

        self.assertEqual('case b | 2: pass', (f := FST('case"a" | 2: pass')).pattern.put_slice('b', 0, 1, norm=True).root.src)
        f.verify()

        self.assertEqual('case 1 | c as b: pass', (f := FST('case 1 | "a"as b: pass')).pattern.pattern.put_slice('c', 1, 2, norm=True).root.src)
        f.verify()

        if PYGE11:
            # lone starred slice without comma being put as 'one'

            self.assertEqual('(*a,),', (f := FST('1, 2, 3')).put_slice(FST('*a', 'expr_slice'), one=True).src)
            f.verify()

        if PYGE12:
            # put single type_param as 'one' to tuple_params slice

            self.assertEqual('Z, **V', (f := FST('T, *U, **V', '_type_params').put_slice('Z', 0, 2)).src)
            f.verify()

        # putting invalid MatchOr slice

        self.assertRaises(NodeError, FST('[x, y, z]', pattern).put, FST('a | b', pattern).get_slice(2, norm_get=False), 0)  # length 0

        self.assertEqual('[b, y, z]', (f := FST('[x, y, z]', pattern)).put(FST('a | b', pattern).get_slice(1, norm_get=False), 0).src)  # length 1
        f.verify()

        self.assertRaises(SyntaxError, FST('x | y', pattern).put_slice, ['+'])

        # del

        self.assertRaises(NodeError, FST('del a, b, c').put, '*(),', 1, 2, norm_put=False)
        self.assertRaises(NodeError, FST('del a, b, c').put, '*()', 1, 2, norm_put=False)

        self.assertEqual('del a, x, y, c', (f := FST('del a, b, c')).put_slice('{x, y}', 1, 2).src)
        f.verify()

        self.assertEqual('del a, x, y, c', (f := FST('del a, b, c')).put_slice('[x, y]', 1, 2).src)
        f.verify()

        self.assertEqual('del b', (f := FST('del(a)')).put_slice('b', 0, 1).src)
        f.verify()

        f = FST('del(a),b')
        self.assertEqual('(a),', f.get_slice(0, 1, cut=True).src)
        self.assertEqual('del b', f.src)
        f.verify()

        f = FST('del(a),b')
        self.assertEqual('del b', f.put_slice(None, 0, 1).src)
        f.verify()

        # make sure we can't put '* to Import.names

        self.assertRaises(NodeError, FST('import a, b, c').put, FST('*', '_ImportFrom_names'), 1, 2)

        # from import with import in modules

        self.assertEqual('from importlib.support import (a,\n                              b)', (f := FST('from importlib.support import a')).put_slice('\nb', 1, 1).src)

        # With / AsyncWith put doesn't join alnums on del or put

        self.assertEqual('with b: pass', (f := FST('with(a),b: pass')).put_slice(None, 0, 1, 'items').src)
        f.verify()
        self.assertEqual('async with b: pass', (f := FST('async with(a),b: pass')).put_slice(None, 0, 1, 'items').src)
        f.verify()

        self.assertEqual('with b: pass', (f := FST('with(a): pass')).put_slice('b', 0, 1, 'items').src)
        f.verify()
        self.assertEqual('async with b: pass', (f := FST('async with(a): pass')).put_slice('b', 0, 1, 'items').src)
        f.verify()

        self.assertEqual('with b: pass', (f := FST('with(a): pass')).put_slice(None, 0, 1, 'items', norm_self=False).put_slice('b', 0, 1, 'items').src)
        f.verify()
        self.assertEqual('async with b: pass', (f := FST('async with(a): pass')).put_slice(None, 0, 1, 'items', norm_self=False).put_slice('b', 0, 1, 'items').src)
        f.verify()

        # withitem dynamic location calculation in put slice

        self.assertEqual('with (z), (c): pass', (f := FST('with a, \\\nb, (c): pass')).put_slice('(z)', 0, 2, 'items').src)
        f.verify()

        self.assertEqual('(z), (c)', (f := FST('a, \\\nb, (c)', '_withitems')).put_slice('(z)', 0, 2, 'items').src)
        f.verify()

        if PYGE11:
            # multiple arglikes as `one` to single arglike field

            self.assertEqual('call((*not a, *b or c))', (f := FST('call()')).put_slice(FST('*not a, *b or c', Tuple), one=True).src)  # TODO this should be fixed on put
            self.assertFalse(f.verify(raise_=False))

        # more unparenthesized tuple schenanigans

        f = FST('a[:, b]')
        f.slice.put_slice('[\n"foo"\n]', 1, 2, 'elts')
        self.assertEqual('a[:,\n  "foo"\n]', f.src)

        f = FST('a = b, c')
        f.value.put_slice('[\n"foo"\n]', 1, 2, 'elts')
        self.assertEqual('a = (b,\n    "foo"\n)', f.src)

        f = FST('a = b, c')
        f.value.put_slice('["foo"   ]', 1, 2, 'elts')
        self.assertEqual('a = b, "foo"', f.src)

        f = FST('for a, b in c: pass')
        f.target.put_slice('[\nz\n]', 1, 2, 'elts')
        self.assertEqual('for (a,\n    z\n) in c: pass', f.src)

        f = FST('for a, b in c: pass')
        f.target.put_slice('[z   ]', 1, 2, 'elts')
        self.assertEqual('for a, z in c: pass', f.src)

        f = FST('a[:, b]')
        f.slice.put_slice('["foo"\\\n]', 1, 2, 'elts')
        self.assertEqual('a[:, "foo"\\\n]', f.src)

        f = FST('a = b, c')
        f.value.put_slice('["foo"\\\n]', 1, 2, 'elts')
        self.assertEqual('a = b, "foo"', f.src)

        f = FST('for a, b in c: pass')
        f.target.put_slice('[z\\\n]', 1, 2, 'elts')
        self.assertEqual('for a, z\\\n in c: pass', f.src)

        f = FST('a,')
        f.put_slice('[ {z} ]', 0, 1)
        self.assertEqual('{z},', f.src)

        f = FST('a[:, b]')
        f.slice.put_slice('[ {z} ]', 0, 1)
        self.assertEqual('a[{z}, b]', f.src)

        # make sure indent preserved on ins pep8space to semicoloned stmts

        f = FST(r'''
class cls:
    a; b
    end
            '''.strip())

        self.assertEqual(r'''
class cls:
    a

    def f(): g

    b
    end
            '''.strip(), f.put_slice('def f(): g', 1, 1).root.src)
        f.verify()

        # last comprehension joining alnums

        self.assertEqual('[_ for _ in "a" if x for _ in _]', (f := FST('[_ for _ in "a"for _ in _]')).generators[0].put_slice('if x', 'ifs').root.src)
        f.verify()

        self.assertEqual('[_ for _ in _ if x for _ in _]', (f := FST('[_ for _ in _ if "a"for _ in _]')).generators[0].put_slice('if x', 'ifs').root.src)
        f.verify()

        self.assertEqual('[_ for _ in _ if "a" if x for _ in _]', (f := FST('[_ for _ in _ if "a"for _ in _]')).generators[0].put_slice('if x', 1, 1, 'ifs').root.src)
        f.verify()

        # putting slice at end of sequence which ends exactly where a parent .format_spec starts

        if PYGE12:
            self.assertEqual("f'{x,:}'", (f := FST("f'{a,b:}'")).values[0].value.put_slice('x,', 0, 2).root.src)
            f.verify()

    def test_unparenthesized_tuple_with_line_continuations(self):
        # backslashes are annoying to include in the regenerable test cases

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 1, cut=True)
        self.assertEqual(a.f.src, '2, \\\n3')
        self.assertEqual(s.src, '1,')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(1, 2, cut=True)
        self.assertEqual(a.f.src, '1, \\\n3')
        self.assertEqual(s.src, '(\n2, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(2, 3, cut=True)
        self.assertEqual(a.f.src, '1, \\\n2,')
        self.assertEqual(s.src, '3,')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 2, cut=True)
        self.assertEqual(a.f.src, '3,')
        self.assertEqual(s.src, '1, \\\n2,')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(1, 3, cut=True)
        self.assertEqual(a.f.src, '1,')
        self.assertEqual(s.src, '(\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 3, cut=True)
        self.assertEqual(a.f.src, '()')
        self.assertEqual(s.src, '1, \\\n2, \\\n3')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 0)
        self.assertEqual(a.f.src, 'a, \\\n1, \\\n2, \\\n3')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 1)
        self.assertEqual(a.f.src, '1, \\\na, \\\n2, \\\n3')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 2, 2)
        self.assertEqual(a.f.src, '1, \\\n2, \\\na, \\\n3')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 3, 3)
        self.assertEqual(a.f.src, '1, \\\n2, \\\n3, a,')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 1)
        self.assertEqual(a.f.src, 'a, \\\n2, \\\n3')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 2)
        self.assertEqual(a.f.src, '1, \\\na, \\\n3')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 2, 3)
        self.assertEqual(a.f.src, '1, \\\n2, \\\na,')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 2)
        self.assertEqual(a.f.src, 'a, \\\n3')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 3)
        self.assertEqual(a.f.src, '1, \\\na,')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 3)
        self.assertEqual(a.f.src, 'a,')

    def test_line_continuation_issue_at_top_level(self):
        a = parse('''
i ; \\
 j
        '''.strip())
        a.f.put_slice(None, 0, 1)
        self.assertTrue(a.f.verify(raise_=False))

        a = parse('''
i ; \\
 j
        '''.strip())
        a.f.put_slice('l', 0, 1)
        self.assertTrue(a.f.verify(raise_=False))

    def test_put_slice_seq_namedexpr_and_yield(self):
        self.assertEqual('a, (x := y)', (f := FST('a, b')).put_slice('x := y', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('(a, x := y)', (f := FST('a, b')).put_slice('x := y,', 1, 2).src)
        f.verify()
        self.assertEqual('a, (yield)', (f := FST('a, b')).put_slice('yield', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('a, (yield)', (f := FST('a, b')).put_slice('(yield),', 1, 2).src)
        f.verify()
        self.assertEqual('a, (yield from x)', (f := FST('a, b')).put_slice('yield from x', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('a, (yield from x)', (f := FST('a, b')).put_slice('(yield from x),', 1, 2).src)
        f.verify()

        self.assertEqual('(a, x := y)', (f := FST('(a, b)')).put_slice('x := y', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('(a, x := y)', (f := FST('(a, b)')).put_slice('x := y,', 1, 2).src)
        f.verify()
        self.assertEqual('(a, (yield))', (f := FST('(a, b)')).put_slice('yield', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('(a, (yield))', (f := FST('(a, b)')).put_slice('(yield),', 1, 2).src)
        f.verify()
        self.assertEqual('(a, (yield from x))', (f := FST('(a, b)')).put_slice('yield from x', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('(a, (yield from x))', (f := FST('(a, b)')).put_slice('(yield from x),', 1, 2).src)
        f.verify()

        self.assertEqual('[a, x := y]', (f := FST('[a, b]')).put_slice('x := y', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('[a, x := y]', (f := FST('[a, b]')).put_slice('x := y,', 1, 2).src)
        f.verify()
        self.assertEqual('[a, (yield)]', (f := FST('[a, b]')).put_slice('yield', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('[a, (yield)]', (f := FST('[a, b]')).put_slice('(yield),', 1, 2).src)
        f.verify()
        self.assertEqual('[a, (yield from x)]', (f := FST('[a, b]')).put_slice('yield from x', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('[a, (yield from x)]', (f := FST('[a, b]')).put_slice('(yield from x),', 1, 2).src)
        f.verify()

        self.assertEqual('{a, x := y}', (f := FST('{a, b}')).put_slice('x := y', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('{a, x := y}', (f := FST('{a, b}')).put_slice('x := y,', 1, 2).src)
        f.verify()
        self.assertEqual('{a, (yield)}', (f := FST('{a, b}')).put_slice('yield', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('{a, (yield)}', (f := FST('{a, b}')).put_slice('(yield),', 1, 2).src)
        f.verify()
        self.assertEqual('{a, (yield from x)}', (f := FST('{a, b}')).put_slice('yield from x', 1, 2, one=True).src)
        f.verify()
        self.assertEqual('{a, (yield from x)}', (f := FST('{a, b}')).put_slice('(yield from x),', 1, 2).src)
        f.verify()

    def test_put_slice_one(self):
        # Tuple

        self.assertEqual('(a, x, d)', (f := FST('(a, b, c, d)')).put_slice(FST('x'), 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('(a, x, d)', (f := FST('(a, b, c, d)')).put_slice(FST('x').a, 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('(a, x, d)', (f := FST('(a, b, c, d)')).put_slice('x', 1, 3, one=True).root.src)
        f.verify()

        # List

        self.assertEqual('[a, x, d]', (f := FST('[a, b, c, d]')).put_slice(FST('x'), 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('[a, x, d]', (f := FST('[a, b, c, d]')).put_slice(FST('x').a, 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('[a, x, d]', (f := FST('[a, b, c, d]')).put_slice('x', 1, 3, one=True).root.src)
        f.verify()

        # Set

        self.assertEqual('{a, x, d}', (f := FST('{a, b, c, d}')).put_slice(FST('x'), 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('{a, x, d}', (f := FST('{a, b, c, d}')).put_slice(FST('x').a, 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('{a, x, d}', (f := FST('{a, b, c, d}')).put_slice('x', 1, 3, one=True).root.src)
        f.verify()

        # Dict doesn't support 'one' because has multi-element items

        # MatchSequence

        self.assertEqual('[a, x, d]', (f := FST('[a, b, c, d]', 'pattern')).put_slice(FST('x', 'pattern'), 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('[a, x, d]', (f := FST('[a, b, c, d]', 'pattern')).put_slice(FST('x', 'pattern').a, 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('[a, x, d]', (f := FST('[a, b, c, d]', 'pattern')).put_slice('x', 1, 3, one=True).root.src)
        f.verify()

        # MatchDict doesn't support 'one' because has multi-element items

        # MatchOr

        self.assertEqual('a | x | d', (f := FST('a | b | c | d', 'pattern')).put_slice(FST('x', 'pattern'), 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('a | x | d', (f := FST('a | b | c | d', 'pattern')).put_slice(FST('x', 'pattern').a, 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('a | x | d', (f := FST('a | b | c | d', 'pattern')).put_slice('x', 1, 3, one=True).root.src)
        f.verify()

        if PYGE12:
            # type_params

            self.assertEqual('type t[T, **Z, **W] = ...', (f := FST('type t[T, *U, **V, **W] = ...')).put_slice(FST('**Z', 'type_param'), 1, 3, 'type_params', one=True).root.src)
            f.verify()

            self.assertEqual('type t[T, **Z, **W] = ...', (f := FST('type t[T, *U, **V, **W] = ...')).put_slice(FST('**Z', 'type_param').a, 1, 3, 'type_params', one=True).root.src)
            f.verify()

            self.assertEqual('type t[T, **Z, **W] = ...', (f := FST('type t[T, *U, **V, **W] = ...')).put_slice('**Z', 1, 3, 'type_params', one=True).root.src)
            f.verify()

        # Delete

        self.assertEqual('del a, x, d', (f := FST('del a, b, c, d')).put_slice(FST('x'), 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('del a, x, d', (f := FST('del a, b, c, d')).put_slice(FST('x').a, 1, 3, one=True).root.src)
        f.verify()

        self.assertEqual('del a, x, d', (f := FST('del a, b, c, d')).put_slice('x', 1, 3, one=True).root.src)
        f.verify()

        # Assign

        self.assertEqual('a = x = d = z', (f := FST('a = b = c = d = z')).put_slice(FST('x'), 1, 3, 'targets', one=True).root.src)
        f.verify()

        self.assertEqual('a = x = d = z', (f := FST('a = b = c = d = z')).put_slice(FST('x').a, 1, 3, 'targets', one=True).root.src)
        f.verify()

        self.assertEqual('a = x = d = z', (f := FST('a = b = c = d = z')).put_slice('x', 1, 3, 'targets', one=True).root.src)
        f.verify()

    def test_put_slice_Delete(self):
        self.assertEqual('del z', (f := FST('del a, b')).put_slice('z').root.src)
        f.verify()

        self.assertEqual('del z', (f := FST('del a, b')).put_slice(['z']).root.src)
        f.verify()

        # self.assertRaises(NodeError, FST('del a, b').put_slice, FST('z'))
        # self.assertRaises(NodeError, FST('del a, b').put_slice, FST('z').a)

        self.assertEqual('del z', (f := FST('del a, b')).put_slice(FST('z')).root.src)
        f.verify()

        self.assertEqual('del z', (f := FST('del a, b')).put_slice(FST('z').a).root.src)
        f.verify()

    def test_put_slice_raw(self):
        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.put_slice('for x in y', 1, 2, 'generators', raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d for x in y for a in b]')
        f = g
        # g = f.put_slice(None, 1, 2, raw=True)
        # self.assertIsNot(g, f)
        # self.assertEqual(g.src, '[a for c in d  for a in b]')
        # f = g
        # g = f.put_slice(None, 1, 2, raw=True)
        # self.assertIsNot(g, f)
        # self.assertEqual(g.src, '[a for c in d  ]')
        # f = g

        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('{a, x, y, c}', parse('{a, b, c}').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice('x: x, y: y', 1, 2, raw=True).root.src)

        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice('(x, y)', 1, 2, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice('[x, y]', 1, 2, raw=True).root.src)
        self.assertEqual('{a, {x, y}, c}', parse('{a, b, c}').body[0].value.f.put_slice('{x, y}', 1, 2, raw=True).root.src)  # invalid set but valid syntax
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, '{x: x, y: y}', 1, 2, raw=True)

        # strip delimiters if present

        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_parse('x, y'), 1, 2, raw=True).root.src)
        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_parse('(x, y)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('[x, y]'), 1, 2, raw=True).root.src)
        self.assertEqual('{a, x, y, c}', parse('{a, b, c}').body[0].value.f.put_slice(ast_parse('{x, y}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_parse('{x: x, y: y}'), 1, 2, raw=True).root.src)

        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(FST.fromsrc('x, y'), 1, 2, raw=True).root.src)
        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(FST.fromsrc('(x, y)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x, y]'), 1, 2, raw=True).root.src)
        self.assertEqual('{a, x, y, c}', parse('{a, b, c}').body[0].value.f.put_slice(FST.fromsrc('{x, y}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(FST.fromsrc('{x: x, y: y}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('x,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('(x,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('{x,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(FST.fromsrc('{x: x,}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('x, y,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('(x, y,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x, y,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('{x, y,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(FST.fromsrc('{x: x, y: y,}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('x,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('(x,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('[x,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('{x,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_parse('{x: x,}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('x, y,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('(x, y,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('[x, y,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('{x, y,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_parse('{x: x, y: y,}'), 1, 2, raw=True).root.src)

        # as one so don't strip delimiters or add to unparenthesized tuple

        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_parse('x, y'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_parse('(x, y)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('[x, y]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('{a, {x, y}, c}', parse('{a, b, c}').body[0].value.f.put_slice(ast_parse('{x, y}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_parse('{x: x, y: y}'), 1, 2, one=True, raw=True)

        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(FST.fromsrc('x, y'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(FST.fromsrc('(x, y)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x, y]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('{a, {x, y}, c}', parse('{a, b, c}').body[0].value.f.put_slice(FST.fromsrc('{x, y}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, FST.fromsrc('{x: x, y: y}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('x,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('(x,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x,], c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x,}, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('{x,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, FST.fromsrc('{x: x,}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x, y,), c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('x, y,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x, y,), c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('(x, y,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y,], c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('[x, y,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x, y,}, c]', parse('[a, b, c]').body[0].value.f.put_slice(FST.fromsrc('{x, y,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, FST.fromsrc('{x: x, y: y,}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('x,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('(x,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('[x,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x}, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('{x,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_parse('{x: x,}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x, y), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('x, y,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x, y), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('(x, y,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('[x, y,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x, y}, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_parse('{x, y,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_parse('{x: x, y: y,}'), 1, 2, one=True, raw=True)

        # can't put empty slice raw

        self.assertRaises(NodeError, FST('a, b').put_slice, FST('()').a, raw=True)
        self.assertRaises(NodeError, FST('a, b').put_slice, FST('()'), raw=True)

        # FST must be root

        self.assertRaises(ValueError, FST('a, b').put_slice, FST('x, y').elts[0], raw=True)

        # misc raw 'auto' for test coverage

        self.assertEqual('a, x, c', FST('a, b, c').put_slice(FST('x', pattern), 1, 2,raw='auto').root.src)

    def test_put_slice_raw_strip_delimiters(self):
        # strip or add delimiters from/to different type of node to put as slice

        f = parse('{a: b, c: d, e: f}').body[0].value.f
        g = parse('match a:\n case {1: x}: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('{a: b, 1: x, e: f}', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('match a:\n case {1: x, 2: y, 3: z}: pass').body[0].cases[0].pattern.f
        g = parse('{1: a}').body[0].value.f.copy()
        self.assertEqual('match a:\n case {1: x, 1: a, 3: z}: pass', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        g = parse('match a:\n case a, b: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('[1, a, b, 3]', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        g = parse('match a:\n case (a, b): pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('[1, a, b, 3]', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, a, b, 3: pass', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, [a, b], 3: pass', f.put_slice(g.a, 1, 2, raw=True, one=True).root.src)

        f = parse('match a:\n case 1 | 2 | 3: pass').body[0].cases[0].pattern.f
        g = parse('a | b').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1 | a | b | 3: pass', f.put_slice(g.a, 1, 2, raw=True).root.src)

        f = parse('{a: b, c: d, e: f}').body[0].value.f
        g = parse('match a:\n case {1: x}: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('{a: b, 1: x, e: f}', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('match a:\n case {1: x, 2: y, 3: z}: pass').body[0].cases[0].pattern.f
        g = parse('{1: a}').body[0].value.f.copy()
        self.assertEqual('match a:\n case {1: x, 1: a, 3: z}: pass', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        g = parse('match a:\n case a, b: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('[1, a, b, 3]', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        g = parse('match a:\n case a, b: pass').body[0].cases[0].pattern.f.copy()
        self.assertEqual('[1, [a, b], 3]', f.put_slice(g, 1, 2, raw=True, one=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, a, b, 3: pass', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, [a, b], 3: pass', f.put_slice(g, 1, 2, raw=True, one=True).root.src)

        f = parse('match a:\n case 1 | 2 | 3: pass').body[0].cases[0].pattern.f
        g = parse('a | b').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1 | a | b | 3: pass', f.put_slice(g, 1, 2, raw=True).root.src)

    def test_put_slice_raw_trailing_comma_ast(self):
        self.assertEqual('[x]', FST('[a]').put_slice(FST('[x]').a, 0, 1, raw=True).src)
        self.assertEqual('[x]', FST('[a]').put_slice(FST('(x,)').a, 0, 1, raw=True).src)
        self.assertEqual('[x, y]', FST('[a]').put_slice(FST('[x, y]').a, 0, 1, raw=True).src)
        self.assertEqual('[x, y]', FST('[a]').put_slice(FST('(x, y)').a, 0, 1, raw=True).src)

        self.assertEqual('(x,)', FST('(a,)').put_slice(FST('[x]').a, 0, 1, raw=True).src)
        self.assertEqual('(x,)', FST('(a,)').put_slice(FST('(x,)').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('[x, y]').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('(x, y)').a, 0, 1, raw=True).src)

        self.assertEqual('[x  ,]', FST('[a  ,]').put_slice(FST('[x]').a, 0, 1, raw=True).src)
        self.assertEqual('[x  ,]', FST('[a  ,]').put_slice(FST('(x,)').a, 0, 1, raw=True).src)
        self.assertEqual('[x, y  ,]', FST('[a  ,]').put_slice(FST('[x, y]').a, 0, 1, raw=True).src)
        self.assertEqual('[x, y  ,]', FST('[a  ,]').put_slice(FST('(x, y)').a, 0, 1, raw=True).src)

        self.assertEqual('(x  ,)', FST('(a  ,)').put_slice(FST('[x]').a, 0, 1, raw=True).src)
        self.assertEqual('(x  ,)', FST('(a  ,)').put_slice(FST('(x,)').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y  ,)', FST('(a  ,)').put_slice(FST('[x, y]').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y  ,)', FST('(a  ,)').put_slice(FST('(x, y)').a, 0, 1, raw=True).src)

        self.assertEqual('[x, b]', FST('[a, b]').put_slice(FST('[x]').a, 0, 1, raw=True).src)
        self.assertEqual('[x, b]', FST('[a, b]').put_slice(FST('(x,)').a, 0, 1, raw=True).src)
        self.assertEqual('[x, y, b]', FST('[a, b]').put_slice(FST('[x, y]').a, 0, 1, raw=True).src)
        self.assertEqual('[x, y, b]', FST('[a, b]').put_slice(FST('(x, y)').a, 0, 1, raw=True).src)

        self.assertEqual('[x]', FST('[a, b]').put_slice(FST('[x]').a, 0, 2, raw=True).src)
        self.assertEqual('[x]', FST('[a, b]').put_slice(FST('(x,)').a, 0, 2, raw=True).src)
        self.assertEqual('[x, y]', FST('[a, b]').put_slice(FST('[x, y]').a, 0, 2, raw=True).src)
        self.assertEqual('[x, y]', FST('[a, b]').put_slice(FST('(x, y)').a, 0, 2, raw=True).src)

        self.assertEqual('[a, x]', FST('[a, b]').put_slice(FST('[x]').a, 1, 2, raw=True).src)
        self.assertEqual('[a, x]', FST('[a, b]').put_slice(FST('(x,)').a, 1, 2, raw=True).src)
        self.assertEqual('[a, x, y]', FST('[a, b]').put_slice(FST('[x, y]').a, 1, 2, raw=True).src)
        self.assertEqual('[a, x, y]', FST('[a, b]').put_slice(FST('(x, y)').a, 1, 2, raw=True).src)

        self.assertEqual('(x, b)', FST('(a, b)').put_slice(FST('[x]').a, 0, 1, raw=True).src)
        self.assertEqual('(x, b)', FST('(a, b)').put_slice(FST('(x,)').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y, b)', FST('(a, b)').put_slice(FST('[x, y]').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y, b)', FST('(a, b)').put_slice(FST('(x, y)').a, 0, 1, raw=True).src)

        self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('[x]').a, 0, 2, raw=True).src)
        self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('(x,)').a, 0, 2, raw=True).src)
        self.assertEqual('(x, y)', FST('(a, b)').put_slice(FST('[x, y]').a, 0, 2, raw=True).src)
        self.assertEqual('(x, y)', FST('(a, b)').put_slice(FST('(x, y)').a, 0, 2, raw=True).src)

        self.assertEqual('(a, x)', FST('(a, b)').put_slice(FST('[x]').a, 1, 2, raw=True).src)
        self.assertEqual('(a, x)', FST('(a, b)').put_slice(FST('(x,)').a, 1, 2, raw=True).src)
        self.assertEqual('(a, x, y)', FST('(a, b)').put_slice(FST('[x, y]').a, 1, 2, raw=True).src)
        self.assertEqual('(a, x, y)', FST('(a, b)').put_slice(FST('(x, y)').a, 1, 2, raw=True).src)

        self.assertEqual('[x, b  ,]', FST('[a, b  ,]').put_slice(FST('[x]').a, 0, 1, raw=True).src)
        self.assertEqual('[x, b  ,]', FST('[a, b  ,]').put_slice(FST('(x,)').a, 0, 1, raw=True).src)
        self.assertEqual('[x, y, b  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]').a, 0, 1, raw=True).src)
        self.assertEqual('[x, y, b  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)').a, 0, 1, raw=True).src)

        self.assertEqual('[x  ,]', FST('[a, b  ,]').put_slice(FST('[x]').a, 0, 2, raw=True).src)
        self.assertEqual('[x  ,]', FST('[a, b  ,]').put_slice(FST('(x,)').a, 0, 2, raw=True).src)
        self.assertEqual('[x, y  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]').a, 0, 2, raw=True).src)
        self.assertEqual('[x, y  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)').a, 0, 2, raw=True).src)

        self.assertEqual('[a, x  ,]', FST('[a, b  ,]').put_slice(FST('[x]').a, 1, 2, raw=True).src)
        self.assertEqual('[a, x  ,]', FST('[a, b  ,]').put_slice(FST('(x,)').a, 1, 2, raw=True).src)
        self.assertEqual('[a, x, y  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]').a, 1, 2, raw=True).src)
        self.assertEqual('[a, x, y  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)').a, 1, 2, raw=True).src)

        self.assertEqual('(x, b  ,)', FST('(a, b  ,)').put_slice(FST('[x]').a, 0, 1, raw=True).src)
        self.assertEqual('(x, b  ,)', FST('(a, b  ,)').put_slice(FST('(x,)').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y, b  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y, b  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)').a, 0, 1, raw=True).src)

        self.assertEqual('(x  ,)', FST('(a, b  ,)').put_slice(FST('[x]').a, 0, 2, raw=True).src)
        self.assertEqual('(x  ,)', FST('(a, b  ,)').put_slice(FST('(x,)').a, 0, 2, raw=True).src)
        self.assertEqual('(x, y  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]').a, 0, 2, raw=True).src)
        self.assertEqual('(x, y  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)').a, 0, 2, raw=True).src)

        self.assertEqual('(a, x  ,)', FST('(a, b  ,)').put_slice(FST('[x]').a, 1, 2, raw=True).src)
        self.assertEqual('(a, x  ,)', FST('(a, b  ,)').put_slice(FST('(x,)').a, 1, 2, raw=True).src)
        self.assertEqual('(a, x, y  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]').a, 1, 2, raw=True).src)
        self.assertEqual('(a, x, y  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)').a, 1, 2, raw=True).src)

        # one

        self.assertEqual('[[x]]', FST('[a]').put_slice(FST('[x]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,)]', FST('[a]').put_slice(FST('(x,)').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y]]', FST('[a]').put_slice(FST('[x, y]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y)]', FST('[a]').put_slice(FST('(x, y)').a, 0, 1, raw=True, one=True).src)

        self.assertEqual('([x],)', FST('(a,)').put_slice(FST('[x]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,),)', FST('(a,)').put_slice(FST('(x,)').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y],)', FST('(a,)').put_slice(FST('[x, y]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y),)', FST('(a,)').put_slice(FST('(x, y)').a, 0, 1, raw=True, one=True).src)

        self.assertEqual('[[x]  ,]', FST('[a  ,]').put_slice(FST('[x]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,)  ,]', FST('[a  ,]').put_slice(FST('(x,)').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y]  ,]', FST('[a  ,]').put_slice(FST('[x, y]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y)  ,]', FST('[a  ,]').put_slice(FST('(x, y)').a, 0, 1, raw=True, one=True).src)

        self.assertEqual('([x]  ,)', FST('(a  ,)').put_slice(FST('[x]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,)  ,)', FST('(a  ,)').put_slice(FST('(x,)').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y]  ,)', FST('(a  ,)').put_slice(FST('[x, y]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y)  ,)', FST('(a  ,)').put_slice(FST('(x, y)').a, 0, 1, raw=True, one=True).src)

        self.assertEqual('[[x], b]', FST('[a, b]').put_slice(FST('[x]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,), b]', FST('[a, b]').put_slice(FST('(x,)').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y], b]', FST('[a, b]').put_slice(FST('[x, y]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y), b]', FST('[a, b]').put_slice(FST('(x, y)').a, 0, 1, raw=True, one=True).src)

        self.assertEqual('[[x]]', FST('[a, b]').put_slice(FST('[x]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x,)]', FST('[a, b]').put_slice(FST('(x,)').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('[[x, y]]', FST('[a, b]').put_slice(FST('[x, y]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x, y)]', FST('[a, b]').put_slice(FST('(x, y)').a, 0, 2, raw=True, one=True).src)

        self.assertEqual('[a, [x]]', FST('[a, b]').put_slice(FST('[x]').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x,)]', FST('[a, b]').put_slice(FST('(x,)').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x, y]]', FST('[a, b]').put_slice(FST('[x, y]').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x, y)]', FST('[a, b]').put_slice(FST('(x, y)').a, 1, 2, raw=True, one=True).src)

        self.assertEqual('([x], b)', FST('(a, b)').put_slice(FST('[x]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,), b)', FST('(a, b)').put_slice(FST('(x,)').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y], b)', FST('(a, b)').put_slice(FST('[x, y]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y), b)', FST('(a, b)').put_slice(FST('(x, y)').a, 0, 1, raw=True, one=True).src)

        self.assertEqual('([x],)', FST('(a, b)').put_slice(FST('[x]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('((x,),)', FST('(a, b)').put_slice(FST('(x,)').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('([x, y],)', FST('(a, b)').put_slice(FST('[x, y]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('((x, y),)', FST('(a, b)').put_slice(FST('(x, y)').a, 0, 2, raw=True, one=True).src)

        self.assertEqual('(a, [x])', FST('(a, b)').put_slice(FST('[x]').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x,))', FST('(a, b)').put_slice(FST('(x,)').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, [x, y])', FST('(a, b)').put_slice(FST('[x, y]').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x, y))', FST('(a, b)').put_slice(FST('(x, y)').a, 1, 2, raw=True, one=True).src)

        self.assertEqual('[[x], b  ,]', FST('[a, b  ,]').put_slice(FST('[x]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,), b  ,]', FST('[a, b  ,]').put_slice(FST('(x,)').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y], b  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y), b  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)').a, 0, 1, raw=True, one=True).src)

        self.assertEqual('[[x]  ,]', FST('[a, b  ,]').put_slice(FST('[x]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x,)  ,]', FST('[a, b  ,]').put_slice(FST('(x,)').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('[[x, y]  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x, y)  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)').a, 0, 2, raw=True, one=True).src)

        self.assertEqual('[a, [x]  ,]', FST('[a, b  ,]').put_slice(FST('[x]').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x,)  ,]', FST('[a, b  ,]').put_slice(FST('(x,)').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x, y]  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x, y)  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)').a, 1, 2, raw=True, one=True).src)

        self.assertEqual('([x], b  ,)', FST('(a, b  ,)').put_slice(FST('[x]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,), b  ,)', FST('(a, b  ,)').put_slice(FST('(x,)').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y], b  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]').a, 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y), b  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)').a, 0, 1, raw=True, one=True).src)

        self.assertEqual('([x]  ,)', FST('(a, b  ,)').put_slice(FST('[x]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('((x,)  ,)', FST('(a, b  ,)').put_slice(FST('(x,)').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('([x, y]  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('((x, y)  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)').a, 0, 2, raw=True, one=True).src)

        self.assertEqual('(a, [x]  ,)', FST('(a, b  ,)').put_slice(FST('[x]').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x,)  ,)', FST('(a, b  ,)').put_slice(FST('(x,)').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, [x, y]  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]').a, 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x, y)  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)').a, 1, 2, raw=True, one=True).src)

        # MatchSequence (sometimes needs traling comma on singleton and sometimes not, thank you structural pattern matching for all your wonderful contributions to python syntax)

        self.assertEqual('[x]', FST('[a]', pattern).put_slice(FST('[x]', pattern).a, 0, 1, raw=True).src)
        self.assertEqual('[x]', FST('[a]', pattern).put_slice(FST('(x,)', pattern).a, 0, 1, raw=True).src)

        self.assertEqual('(x ,)', FST('(a ,)', pattern).put_slice(FST('[x]', pattern).a, 0, 1, raw=True).src)
        self.assertEqual('(x ,)', FST('(a ,)', pattern).put_slice(FST('(x,)', pattern).a, 0, 1, raw=True).src)

        self.assertEqual('(x,)', FST('(a, b)', pattern).put_slice(FST('[x]', pattern).a, 0, 2, raw=True).src)
        self.assertEqual('(x,)', FST('(a, b)', pattern).put_slice(FST('(x,)', pattern).a, 0, 2, raw=True).src)

        self.assertEqual('[[x]]', FST('[a]', pattern).put_slice(FST('[x]', pattern).a, 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x]]', FST('[a]', pattern).put_slice(FST('(x,)', pattern).a, 0, 1, raw=True, one=True).src)

        self.assertEqual('([x] ,)', FST('(a ,)', pattern).put_slice(FST('[x]', pattern).a, 0, 1, raw=True, one=True).src)
        self.assertEqual('([x] ,)', FST('(a ,)', pattern).put_slice(FST('(x,)', pattern).a, 0, 1, raw=True, one=True).src)

        self.assertEqual('([x],)', FST('(a, b)', pattern).put_slice(FST('[x]', pattern).a, 0, 2, raw=True, one=True).src)
        self.assertEqual('([x],)', FST('(a, b)', pattern).put_slice(FST('(x,)', pattern).a, 0, 2, raw=True, one=True).src)

        # non-sequence types with trailing commas

        self.assertEqual('class cls(x ,): pass', FST('class cls(a, b ,): pass').put_slice(FST('[x]').a, 0, 2, 'bases', raw=True).src)
        self.assertEqual('class cls(x ,): pass', FST('class cls(a, b ,): pass').put_slice(FST('(x,)').a, 0, 2, 'bases', raw=True).src)

        self.assertEqual('call(x ,)', FST('call(a, b ,)').put_slice(FST('[x]').a, 0, 2, raw=True).src)
        self.assertEqual('call(x ,)', FST('call(a, b ,)').put_slice(FST('(x,)').a, 0, 2, raw=True).src)

        self.assertEqual('del x ,', FST('del a, b ,').put_slice(FST('[x]').a, 0, 2, raw=True).src)
        self.assertEqual('del x ,', FST('del a, b ,').put_slice(FST('(x,)').a, 0, 2, raw=True).src)

        self.assertEqual('class cls([x] ,): pass', FST('class cls(a, b ,): pass').put_slice(FST('[x]').a, 0, 2, 'bases', raw=True, one=True).src)
        self.assertEqual('class cls((x,) ,): pass', FST('class cls(a, b ,): pass').put_slice(FST('(x,)').a, 0, 2, 'bases', raw=True, one=True).src)

        self.assertEqual('call([x] ,)', FST('call(a, b ,)').put_slice(FST('[x]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('call((x,) ,)', FST('call(a, b ,)').put_slice(FST('(x,)').a, 0, 2, raw=True, one=True).src)

        self.assertEqual('del [x] ,', FST('del a, b ,').put_slice(FST('[x]').a, 0, 2, raw=True, one=True).src)
        self.assertEqual('del (x,) ,', FST('del a, b ,').put_slice(FST('(x,)').a, 0, 2, raw=True, one=True).src)

        # special slices

        self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('x, y', '_withitems').a, 0, 1, raw=True).src)
        self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('x, y', '_aliases').a, 0, 1, raw=True).src)

        self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('x', '_withitems').a, 0, 2, raw=True).src)
        self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('x', '_aliases').a, 0, 2, raw=True).src)

        self.assertRaises(NodeError, FST('(a,)').put_slice, FST('x, y', '_withitems').a, 0, 1, raw=True, one=True)
        self.assertRaises(NodeError, FST('(a,)').put_slice, FST('x, y', '_aliases').a, 0, 1, raw=True, one=True)

        if PYGE12:
            self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('x, y', '_type_params').a, 0, 1, raw=True).src)
            self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('x', '_type_params').a, 0, 2, raw=True).src)
            self.assertRaises(NodeError, FST('(a,)').put_slice, FST('x, y', '_type_params').a, 0, 1, raw=True, one=True)

    def test_put_slice_raw_trailing_comma_fst(self):
        self.assertEqual('[x]', FST('[a]').put_slice(FST('[x]'), 0, 1, raw=True).src)
        self.assertEqual('[x]', FST('[a]').put_slice(FST('(x,)'), 0, 1, raw=True).src)
        self.assertEqual('[x ,]', FST('[a]').put_slice(FST('[x ,]'), 0, 1, raw=True).src)
        self.assertEqual('[x ,]', FST('[a]').put_slice(FST('(x ,)'), 0, 1, raw=True).src)
        self.assertEqual('[x, y]', FST('[a]').put_slice(FST('[x, y]'), 0, 1, raw=True).src)
        self.assertEqual('[x, y]', FST('[a]').put_slice(FST('(x, y)'), 0, 1, raw=True).src)
        self.assertEqual('[x, y ,]', FST('[a]').put_slice(FST('[x, y ,]'), 0, 1, raw=True).src)
        self.assertEqual('[x, y ,]', FST('[a]').put_slice(FST('(x, y ,)'), 0, 1, raw=True).src)

        self.assertEqual('(x,)', FST('(a,)').put_slice(FST('[x]'), 0, 1, raw=True).src)
        self.assertEqual('(x,)', FST('(a,)').put_slice(FST('(x,)'), 0, 1, raw=True).src)
        self.assertEqual('(x ,)', FST('(a,)').put_slice(FST('[x ,]'), 0, 1, raw=True).src)
        self.assertEqual('(x ,)', FST('(a,)').put_slice(FST('(x ,)'), 0, 1, raw=True).src)
        self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('[x, y]'), 0, 1, raw=True).src)
        self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('(x, y)'), 0, 1, raw=True).src)
        self.assertEqual('(x, y ,)', FST('(a,)').put_slice(FST('[x, y ,]'), 0, 1, raw=True).src)
        self.assertEqual('(x, y ,)', FST('(a,)').put_slice(FST('(x, y ,)'), 0, 1, raw=True).src)

        self.assertEqual('[x  ,]', FST('[a  ,]').put_slice(FST('[x]'), 0, 1, raw=True).src)
        self.assertEqual('[x  ,]', FST('[a  ,]').put_slice(FST('(x,)'), 0, 1, raw=True).src)
        self.assertEqual('[x ,]', FST('[a  ,]').put_slice(FST('[x ,]'), 0, 1, raw=True).src)
        self.assertEqual('[x ,]', FST('[a  ,]').put_slice(FST('(x ,)'), 0, 1, raw=True).src)
        self.assertEqual('[x, y  ,]', FST('[a  ,]').put_slice(FST('[x, y]'), 0, 1, raw=True).src)
        self.assertEqual('[x, y  ,]', FST('[a  ,]').put_slice(FST('(x, y)'), 0, 1, raw=True).src)
        self.assertEqual('[x, y ,]', FST('[a  ,]').put_slice(FST('[x, y ,]'), 0, 1, raw=True).src)
        self.assertEqual('[x, y ,]', FST('[a  ,]').put_slice(FST('(x, y ,)'), 0, 1, raw=True).src)

        self.assertEqual('(x  ,)', FST('(a  ,)').put_slice(FST('[x]'), 0, 1, raw=True).src)
        self.assertEqual('(x  ,)', FST('(a  ,)').put_slice(FST('(x,)'), 0, 1, raw=True).src)
        self.assertEqual('(x ,)', FST('(a  ,)').put_slice(FST('[x ,]'), 0, 1, raw=True).src)
        self.assertEqual('(x ,)', FST('(a  ,)').put_slice(FST('(x ,)'), 0, 1, raw=True).src)
        self.assertEqual('(x, y  ,)', FST('(a  ,)').put_slice(FST('[x, y]'), 0, 1, raw=True).src)
        self.assertEqual('(x, y  ,)', FST('(a  ,)').put_slice(FST('(x, y)'), 0, 1, raw=True).src)
        self.assertEqual('(x, y ,)', FST('(a  ,)').put_slice(FST('[x, y ,]'), 0, 1, raw=True).src)
        self.assertEqual('(x, y ,)', FST('(a  ,)').put_slice(FST('(x, y ,)'), 0, 1, raw=True).src)

        self.assertEqual('[x, b]', FST('[a, b]').put_slice(FST('[x]'), 0, 1, raw=True).src)
        self.assertEqual('[x, b]', FST('[a, b]').put_slice(FST('(x,)'), 0, 1, raw=True).src)
        self.assertEqual('[x , b]', FST('[a, b]').put_slice(FST('[x ,]'), 0, 1, raw=True).src)
        self.assertEqual('[x , b]', FST('[a, b]').put_slice(FST('(x ,)'), 0, 1, raw=True).src)
        self.assertEqual('[x, y, b]', FST('[a, b]').put_slice(FST('[x, y]'), 0, 1, raw=True).src)
        self.assertEqual('[x, y, b]', FST('[a, b]').put_slice(FST('(x, y)'), 0, 1, raw=True).src)
        self.assertEqual('[x, y , b]', FST('[a, b]').put_slice(FST('[x, y ,]'), 0, 1, raw=True).src)
        self.assertEqual('[x, y , b]', FST('[a, b]').put_slice(FST('(x, y ,)'), 0, 1, raw=True).src)

        self.assertEqual('[x]', FST('[a, b]').put_slice(FST('[x]'), 0, 2, raw=True).src)
        self.assertEqual('[x]', FST('[a, b]').put_slice(FST('(x,)'), 0, 2, raw=True).src)
        self.assertEqual('[x ,]', FST('[a, b]').put_slice(FST('[x ,]'), 0, 2, raw=True).src)
        self.assertEqual('[x ,]', FST('[a, b]').put_slice(FST('(x ,)'), 0, 2, raw=True).src)
        self.assertEqual('[x, y]', FST('[a, b]').put_slice(FST('[x, y]'), 0, 2, raw=True).src)
        self.assertEqual('[x, y]', FST('[a, b]').put_slice(FST('(x, y)'), 0, 2, raw=True).src)
        self.assertEqual('[x, y ,]', FST('[a, b]').put_slice(FST('[x, y ,]'), 0, 2, raw=True).src)
        self.assertEqual('[x, y ,]', FST('[a, b]').put_slice(FST('(x, y ,)'), 0, 2, raw=True).src)

        self.assertEqual('[a, x]', FST('[a, b]').put_slice(FST('[x]'), 1, 2, raw=True).src)
        self.assertEqual('[a, x]', FST('[a, b]').put_slice(FST('(x,)'), 1, 2, raw=True).src)
        self.assertEqual('[a, x ,]', FST('[a, b]').put_slice(FST('[x ,]'), 1, 2, raw=True).src)
        self.assertEqual('[a, x ,]', FST('[a, b]').put_slice(FST('(x ,)'), 1, 2, raw=True).src)
        self.assertEqual('[a, x, y]', FST('[a, b]').put_slice(FST('[x, y]'), 1, 2, raw=True).src)
        self.assertEqual('[a, x, y]', FST('[a, b]').put_slice(FST('(x, y)'), 1, 2, raw=True).src)
        self.assertEqual('[a, x, y ,]', FST('[a, b]').put_slice(FST('[x, y ,]'), 1, 2, raw=True).src)
        self.assertEqual('[a, x, y ,]', FST('[a, b]').put_slice(FST('(x, y ,)'), 1, 2, raw=True).src)

        self.assertEqual('(x, b)', FST('(a, b)').put_slice(FST('[x]'), 0, 1, raw=True).src)
        self.assertEqual('(x, b)', FST('(a, b)').put_slice(FST('(x,)'), 0, 1, raw=True).src)
        self.assertEqual('(x , b)', FST('(a, b)').put_slice(FST('[x ,]'), 0, 1, raw=True).src)
        self.assertEqual('(x , b)', FST('(a, b)').put_slice(FST('(x ,)'), 0, 1, raw=True).src)
        self.assertEqual('(x, y, b)', FST('(a, b)').put_slice(FST('[x, y]'), 0, 1, raw=True).src)
        self.assertEqual('(x, y, b)', FST('(a, b)').put_slice(FST('(x, y)'), 0, 1, raw=True).src)
        self.assertEqual('(x, y , b)', FST('(a, b)').put_slice(FST('[x, y ,]'), 0, 1, raw=True).src)
        self.assertEqual('(x, y , b)', FST('(a, b)').put_slice(FST('(x, y ,)'), 0, 1, raw=True).src)

        self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('[x]'), 0, 2, raw=True).src)
        self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('(x,)'), 0, 2, raw=True).src)
        self.assertEqual('(x ,)', FST('(a, b)').put_slice(FST('[x ,]'), 0, 2, raw=True).src)
        self.assertEqual('(x ,)', FST('(a, b)').put_slice(FST('(x ,)'), 0, 2, raw=True).src)
        self.assertEqual('(x, y)', FST('(a, b)').put_slice(FST('[x, y]'), 0, 2, raw=True).src)
        self.assertEqual('(x, y)', FST('(a, b)').put_slice(FST('(x, y)'), 0, 2, raw=True).src)
        self.assertEqual('(x, y ,)', FST('(a, b)').put_slice(FST('[x, y ,]'), 0, 2, raw=True).src)
        self.assertEqual('(x, y ,)', FST('(a, b)').put_slice(FST('(x, y ,)'), 0, 2, raw=True).src)

        self.assertEqual('(a, x)', FST('(a, b)').put_slice(FST('[x]'), 1, 2, raw=True).src)
        self.assertEqual('(a, x)', FST('(a, b)').put_slice(FST('(x,)'), 1, 2, raw=True).src)
        self.assertEqual('(a, x ,)', FST('(a, b)').put_slice(FST('[x ,]'), 1, 2, raw=True).src)
        self.assertEqual('(a, x ,)', FST('(a, b)').put_slice(FST('(x ,)'), 1, 2, raw=True).src)
        self.assertEqual('(a, x, y)', FST('(a, b)').put_slice(FST('[x, y]'), 1, 2, raw=True).src)
        self.assertEqual('(a, x, y)', FST('(a, b)').put_slice(FST('(x, y)'), 1, 2, raw=True).src)
        self.assertEqual('(a, x, y ,)', FST('(a, b)').put_slice(FST('[x, y ,]'), 1, 2, raw=True).src)
        self.assertEqual('(a, x, y ,)', FST('(a, b)').put_slice(FST('(x, y ,)'), 1, 2, raw=True).src)

        self.assertEqual('[x, b  ,]', FST('[a, b  ,]').put_slice(FST('[x]'), 0, 1, raw=True).src)
        self.assertEqual('[x, b  ,]', FST('[a, b  ,]').put_slice(FST('(x,)'), 0, 1, raw=True).src)
        self.assertEqual('[x , b  ,]', FST('[a, b  ,]').put_slice(FST('[x ,]'), 0, 1, raw=True).src)
        self.assertEqual('[x , b  ,]', FST('[a, b  ,]').put_slice(FST('(x ,)'), 0, 1, raw=True).src)
        self.assertEqual('[x, y, b  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]'), 0, 1, raw=True).src)
        self.assertEqual('[x, y, b  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)'), 0, 1, raw=True).src)
        self.assertEqual('[x, y , b  ,]', FST('[a, b  ,]').put_slice(FST('[x, y ,]'), 0, 1, raw=True).src)
        self.assertEqual('[x, y , b  ,]', FST('[a, b  ,]').put_slice(FST('(x, y ,)'), 0, 1, raw=True).src)

        self.assertEqual('[x  ,]', FST('[a, b  ,]').put_slice(FST('[x]'), 0, 2, raw=True).src)
        self.assertEqual('[x  ,]', FST('[a, b  ,]').put_slice(FST('(x,)'), 0, 2, raw=True).src)
        self.assertEqual('[x ,]', FST('[a, b  ,]').put_slice(FST('[x ,]'), 0, 2, raw=True).src)
        self.assertEqual('[x ,]', FST('[a, b  ,]').put_slice(FST('(x ,)'), 0, 2, raw=True).src)
        self.assertEqual('[x, y  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]'), 0, 2, raw=True).src)
        self.assertEqual('[x, y  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)'), 0, 2, raw=True).src)
        self.assertEqual('[x, y ,]', FST('[a, b  ,]').put_slice(FST('[x, y ,]'), 0, 2, raw=True).src)
        self.assertEqual('[x, y ,]', FST('[a, b  ,]').put_slice(FST('(x, y ,)'), 0, 2, raw=True).src)

        self.assertEqual('[a, x  ,]', FST('[a, b  ,]').put_slice(FST('[x]'), 1, 2, raw=True).src)
        self.assertEqual('[a, x  ,]', FST('[a, b  ,]').put_slice(FST('(x,)'), 1, 2, raw=True).src)
        self.assertEqual('[a, x ,]', FST('[a, b  ,]').put_slice(FST('[x ,]'), 1, 2, raw=True).src)
        self.assertEqual('[a, x ,]', FST('[a, b  ,]').put_slice(FST('(x ,)'), 1, 2, raw=True).src)
        self.assertEqual('[a, x, y  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]'), 1, 2, raw=True).src)
        self.assertEqual('[a, x, y  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)'), 1, 2, raw=True).src)
        self.assertEqual('[a, x, y ,]', FST('[a, b  ,]').put_slice(FST('[x, y ,]'), 1, 2, raw=True).src)
        self.assertEqual('[a, x, y ,]', FST('[a, b  ,]').put_slice(FST('(x, y ,)'), 1, 2, raw=True).src)

        self.assertEqual('(x, b  ,)', FST('(a, b  ,)').put_slice(FST('[x]'), 0, 1, raw=True).src)
        self.assertEqual('(x, b  ,)', FST('(a, b  ,)').put_slice(FST('(x,)'), 0, 1, raw=True).src)
        self.assertEqual('(x , b  ,)', FST('(a, b  ,)').put_slice(FST('[x ,]'), 0, 1, raw=True).src)
        self.assertEqual('(x , b  ,)', FST('(a, b  ,)').put_slice(FST('(x ,)'), 0, 1, raw=True).src)
        self.assertEqual('(x, y, b  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]'), 0, 1, raw=True).src)
        self.assertEqual('(x, y, b  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)'), 0, 1, raw=True).src)
        self.assertEqual('(x, y , b  ,)', FST('(a, b  ,)').put_slice(FST('[x, y ,]'), 0, 1, raw=True).src)
        self.assertEqual('(x, y , b  ,)', FST('(a, b  ,)').put_slice(FST('(x, y ,)'), 0, 1, raw=True).src)

        self.assertEqual('(x  ,)', FST('(a, b  ,)').put_slice(FST('[x]'), 0, 2, raw=True).src)
        self.assertEqual('(x  ,)', FST('(a, b  ,)').put_slice(FST('(x,)'), 0, 2, raw=True).src)
        self.assertEqual('(x ,)', FST('(a, b  ,)').put_slice(FST('[x ,]'), 0, 2, raw=True).src)
        self.assertEqual('(x ,)', FST('(a, b  ,)').put_slice(FST('(x ,)'), 0, 2, raw=True).src)
        self.assertEqual('(x, y  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]'), 0, 2, raw=True).src)
        self.assertEqual('(x, y  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)'), 0, 2, raw=True).src)
        self.assertEqual('(x, y ,)', FST('(a, b  ,)').put_slice(FST('[x, y ,]'), 0, 2, raw=True).src)
        self.assertEqual('(x, y ,)', FST('(a, b  ,)').put_slice(FST('(x, y ,)'), 0, 2, raw=True).src)

        self.assertEqual('(a, x  ,)', FST('(a, b  ,)').put_slice(FST('[x]'), 1, 2, raw=True).src)
        self.assertEqual('(a, x  ,)', FST('(a, b  ,)').put_slice(FST('(x,)'), 1, 2, raw=True).src)
        self.assertEqual('(a, x ,)', FST('(a, b  ,)').put_slice(FST('[x ,]'), 1, 2, raw=True).src)
        self.assertEqual('(a, x ,)', FST('(a, b  ,)').put_slice(FST('(x ,)'), 1, 2, raw=True).src)
        self.assertEqual('(a, x, y  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]'), 1, 2, raw=True).src)
        self.assertEqual('(a, x, y  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)'), 1, 2, raw=True).src)
        self.assertEqual('(a, x, y ,)', FST('(a, b  ,)').put_slice(FST('[x, y ,]'), 1, 2, raw=True).src)
        self.assertEqual('(a, x, y ,)', FST('(a, b  ,)').put_slice(FST('(x, y ,)'), 1, 2, raw=True).src)

        # one

        self.assertEqual('[[x]]', FST('[a]').put_slice(FST('[x]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,)]', FST('[a]').put_slice(FST('(x,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x ,]]', FST('[a]').put_slice(FST('[x ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x ,)]', FST('[a]').put_slice(FST('(x ,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y]]', FST('[a]').put_slice(FST('[x, y]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y)]', FST('[a]').put_slice(FST('(x, y)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y ,]]', FST('[a]').put_slice(FST('[x, y ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y ,)]', FST('[a]').put_slice(FST('(x, y ,)'), 0, 1, raw=True, one=True).src)

        self.assertEqual('([x],)', FST('(a,)').put_slice(FST('[x]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,),)', FST('(a,)').put_slice(FST('(x,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x ,],)', FST('(a,)').put_slice(FST('[x ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x ,),)', FST('(a,)').put_slice(FST('(x ,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y],)', FST('(a,)').put_slice(FST('[x, y]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y),)', FST('(a,)').put_slice(FST('(x, y)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y ,],)', FST('(a,)').put_slice(FST('[x, y ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y ,),)', FST('(a,)').put_slice(FST('(x, y ,)'), 0, 1, raw=True, one=True).src)

        self.assertEqual('[[x]  ,]', FST('[a  ,]').put_slice(FST('[x]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,)  ,]', FST('[a  ,]').put_slice(FST('(x,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x ,]  ,]', FST('[a  ,]').put_slice(FST('[x ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x ,)  ,]', FST('[a  ,]').put_slice(FST('(x ,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y]  ,]', FST('[a  ,]').put_slice(FST('[x, y]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y)  ,]', FST('[a  ,]').put_slice(FST('(x, y)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y ,]  ,]', FST('[a  ,]').put_slice(FST('[x, y ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y ,)  ,]', FST('[a  ,]').put_slice(FST('(x, y ,)'), 0, 1, raw=True, one=True).src)

        self.assertEqual('([x]  ,)', FST('(a  ,)').put_slice(FST('[x]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,)  ,)', FST('(a  ,)').put_slice(FST('(x,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x ,]  ,)', FST('(a  ,)').put_slice(FST('[x ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x ,)  ,)', FST('(a  ,)').put_slice(FST('(x ,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y]  ,)', FST('(a  ,)').put_slice(FST('[x, y]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y)  ,)', FST('(a  ,)').put_slice(FST('(x, y)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y ,]  ,)', FST('(a  ,)').put_slice(FST('[x, y ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y ,)  ,)', FST('(a  ,)').put_slice(FST('(x, y ,)'), 0, 1, raw=True, one=True).src)

        self.assertEqual('[[x], b]', FST('[a, b]').put_slice(FST('[x]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,), b]', FST('[a, b]').put_slice(FST('(x,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x ,], b]', FST('[a, b]').put_slice(FST('[x ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x ,), b]', FST('[a, b]').put_slice(FST('(x ,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y], b]', FST('[a, b]').put_slice(FST('[x, y]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y), b]', FST('[a, b]').put_slice(FST('(x, y)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y ,], b]', FST('[a, b]').put_slice(FST('[x, y ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y ,), b]', FST('[a, b]').put_slice(FST('(x, y ,)'), 0, 1, raw=True, one=True).src)

        self.assertEqual('[[x]]', FST('[a, b]').put_slice(FST('[x]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x,)]', FST('[a, b]').put_slice(FST('(x,)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[[x ,]]', FST('[a, b]').put_slice(FST('[x ,]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x ,)]', FST('[a, b]').put_slice(FST('(x ,)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[[x, y]]', FST('[a, b]').put_slice(FST('[x, y]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x, y)]', FST('[a, b]').put_slice(FST('(x, y)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[[x, y ,]]', FST('[a, b]').put_slice(FST('[x, y ,]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x, y ,)]', FST('[a, b]').put_slice(FST('(x, y ,)'), 0, 2, raw=True, one=True).src)

        self.assertEqual('[a, [x]]', FST('[a, b]').put_slice(FST('[x]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x,)]', FST('[a, b]').put_slice(FST('(x,)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x ,]]', FST('[a, b]').put_slice(FST('[x ,]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x ,)]', FST('[a, b]').put_slice(FST('(x ,)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x, y]]', FST('[a, b]').put_slice(FST('[x, y]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x, y)]', FST('[a, b]').put_slice(FST('(x, y)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x, y ,]]', FST('[a, b]').put_slice(FST('[x, y ,]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x, y ,)]', FST('[a, b]').put_slice(FST('(x, y ,)'), 1, 2, raw=True, one=True).src)

        self.assertEqual('([x], b)', FST('(a, b)').put_slice(FST('[x]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,), b)', FST('(a, b)').put_slice(FST('(x,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x ,], b)', FST('(a, b)').put_slice(FST('[x ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x ,), b)', FST('(a, b)').put_slice(FST('(x ,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y], b)', FST('(a, b)').put_slice(FST('[x, y]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y), b)', FST('(a, b)').put_slice(FST('(x, y)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y ,], b)', FST('(a, b)').put_slice(FST('[x, y ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y ,), b)', FST('(a, b)').put_slice(FST('(x, y ,)'), 0, 1, raw=True, one=True).src)

        self.assertEqual('([x],)', FST('(a, b)').put_slice(FST('[x]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x,),)', FST('(a, b)').put_slice(FST('(x,)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('([x ,],)', FST('(a, b)').put_slice(FST('[x ,]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x ,),)', FST('(a, b)').put_slice(FST('(x ,)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('([x, y],)', FST('(a, b)').put_slice(FST('[x, y]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x, y),)', FST('(a, b)').put_slice(FST('(x, y)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('([x, y ,],)', FST('(a, b)').put_slice(FST('[x, y ,]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x, y ,),)', FST('(a, b)').put_slice(FST('(x, y ,)'), 0, 2, raw=True, one=True).src)

        self.assertEqual('(a, [x])', FST('(a, b)').put_slice(FST('[x]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x,))', FST('(a, b)').put_slice(FST('(x,)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, [x ,])', FST('(a, b)').put_slice(FST('[x ,]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x ,))', FST('(a, b)').put_slice(FST('(x ,)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, [x, y])', FST('(a, b)').put_slice(FST('[x, y]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x, y))', FST('(a, b)').put_slice(FST('(x, y)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, [x, y ,])', FST('(a, b)').put_slice(FST('[x, y ,]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x, y ,))', FST('(a, b)').put_slice(FST('(x, y ,)'), 1, 2, raw=True, one=True).src)

        self.assertEqual('[[x], b  ,]', FST('[a, b  ,]').put_slice(FST('[x]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,), b  ,]', FST('[a, b  ,]').put_slice(FST('(x,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x ,], b  ,]', FST('[a, b  ,]').put_slice(FST('[x ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x ,), b  ,]', FST('[a, b  ,]').put_slice(FST('(x ,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y], b  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y), b  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[[x, y ,], b  ,]', FST('[a, b  ,]').put_slice(FST('[x, y ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x, y ,), b  ,]', FST('[a, b  ,]').put_slice(FST('(x, y ,)'), 0, 1, raw=True, one=True).src)

        self.assertEqual('[[x]  ,]', FST('[a, b  ,]').put_slice(FST('[x]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x,)  ,]', FST('[a, b  ,]').put_slice(FST('(x,)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[[x ,]  ,]', FST('[a, b  ,]').put_slice(FST('[x ,]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x ,)  ,]', FST('[a, b  ,]').put_slice(FST('(x ,)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[[x, y]  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x, y)  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[[x, y ,]  ,]', FST('[a, b  ,]').put_slice(FST('[x, y ,]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('[(x, y ,)  ,]', FST('[a, b  ,]').put_slice(FST('(x, y ,)'), 0, 2, raw=True, one=True).src)

        self.assertEqual('[a, [x]  ,]', FST('[a, b  ,]').put_slice(FST('[x]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x,)  ,]', FST('[a, b  ,]').put_slice(FST('(x,)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x ,]  ,]', FST('[a, b  ,]').put_slice(FST('[x ,]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x ,)  ,]', FST('[a, b  ,]').put_slice(FST('(x ,)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x, y]  ,]', FST('[a, b  ,]').put_slice(FST('[x, y]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x, y)  ,]', FST('[a, b  ,]').put_slice(FST('(x, y)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x, y ,]  ,]', FST('[a, b  ,]').put_slice(FST('[x, y ,]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x, y ,)  ,]', FST('[a, b  ,]').put_slice(FST('(x, y ,)'), 1, 2, raw=True, one=True).src)

        self.assertEqual('([x], b  ,)', FST('(a, b  ,)').put_slice(FST('[x]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,), b  ,)', FST('(a, b  ,)').put_slice(FST('(x,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x ,], b  ,)', FST('(a, b  ,)').put_slice(FST('[x ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x ,), b  ,)', FST('(a, b  ,)').put_slice(FST('(x ,)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y], b  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y), b  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)'), 0, 1, raw=True, one=True).src)
        self.assertEqual('([x, y ,], b  ,)', FST('(a, b  ,)').put_slice(FST('[x, y ,]'), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x, y ,), b  ,)', FST('(a, b  ,)').put_slice(FST('(x, y ,)'), 0, 1, raw=True, one=True).src)

        self.assertEqual('([x]  ,)', FST('(a, b  ,)').put_slice(FST('[x]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x,)  ,)', FST('(a, b  ,)').put_slice(FST('(x,)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('([x ,]  ,)', FST('(a, b  ,)').put_slice(FST('[x ,]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x ,)  ,)', FST('(a, b  ,)').put_slice(FST('(x ,)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('([x, y]  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x, y)  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)'), 0, 2, raw=True, one=True).src)
        self.assertEqual('([x, y ,]  ,)', FST('(a, b  ,)').put_slice(FST('[x, y ,]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x, y ,)  ,)', FST('(a, b  ,)').put_slice(FST('(x, y ,)'), 0, 2, raw=True, one=True).src)

        self.assertEqual('(a, [x]  ,)', FST('(a, b  ,)').put_slice(FST('[x]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x,)  ,)', FST('(a, b  ,)').put_slice(FST('(x,)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, [x ,]  ,)', FST('(a, b  ,)').put_slice(FST('[x ,]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x ,)  ,)', FST('(a, b  ,)').put_slice(FST('(x ,)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, [x, y]  ,)', FST('(a, b  ,)').put_slice(FST('[x, y]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x, y)  ,)', FST('(a, b  ,)').put_slice(FST('(x, y)'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, [x, y ,]  ,)', FST('(a, b  ,)').put_slice(FST('[x, y ,]'), 1, 2, raw=True, one=True).src)
        self.assertEqual('(a, (x, y ,)  ,)', FST('(a, b  ,)').put_slice(FST('(x, y ,)'), 1, 2, raw=True, one=True).src)

        self.assertEqual('[a, (x,), c]', FST('[a, b, c]').put_slice(FST('x,'), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, (x, y), c]', FST('[a, b, c]').put_slice(FST('x, y'), 1, 2, raw=True, one=True).src)

        # MatchSequence (sometimes needs traling comma on singleton and sometimes not, thank you structural pattern matching for all your wonderful contributions to python syntax)

        self.assertEqual('[x]', FST('[a]', pattern).put_slice(FST('[x]', pattern), 0, 1, raw=True).src)
        self.assertEqual('[x]', FST('[a]', pattern).put_slice(FST('(x,)', pattern), 0, 1, raw=True).src)

        self.assertEqual('(x ,)', FST('(a ,)', pattern).put_slice(FST('[x]', pattern), 0, 1, raw=True).src)
        self.assertEqual('(x ,)', FST('(a ,)', pattern).put_slice(FST('(x,)', pattern), 0, 1, raw=True).src)

        self.assertEqual('(x,)', FST('(a, b)', pattern).put_slice(FST('[x]', pattern), 0, 2, raw=True).src)
        self.assertEqual('(x,)', FST('(a, b)', pattern).put_slice(FST('(x,)', pattern), 0, 2, raw=True).src)

        self.assertEqual('[[x]]', FST('[a]', pattern).put_slice(FST('[x]', pattern), 0, 1, raw=True, one=True).src)
        self.assertEqual('[(x,)]', FST('[a]', pattern).put_slice(FST('(x,)', pattern), 0, 1, raw=True, one=True).src)

        self.assertEqual('([x] ,)', FST('(a ,)', pattern).put_slice(FST('[x]', pattern), 0, 1, raw=True, one=True).src)
        self.assertEqual('((x,) ,)', FST('(a ,)', pattern).put_slice(FST('(x,)', pattern), 0, 1, raw=True, one=True).src)

        self.assertEqual('([x],)', FST('(a, b)', pattern).put_slice(FST('[x]', pattern), 0, 2, raw=True, one=True).src)
        self.assertEqual('((x,),)', FST('(a, b)', pattern).put_slice(FST('(x,)', pattern), 0, 2, raw=True, one=True).src)

        self.assertEqual('[a, [x,], c]', FST('[a, b, c]', pattern).put_slice(FST('x,', pattern), 1, 2, raw=True, one=True).src)
        self.assertEqual('[a, [x, y], c]', FST('[a, b, c]', pattern).put_slice(FST('x, y', pattern), 1, 2, raw=True, one=True).src)

        # non-sequence types with trailing commas

        self.assertEqual('class cls(x ,): pass', FST('class cls(a, b ,): pass').put_slice(FST('[x]'), 0, 2, 'bases', raw=True).src)
        self.assertEqual('class cls(x ,): pass', FST('class cls(a, b ,): pass').put_slice(FST('(x,)'), 0, 2, 'bases', raw=True).src)

        self.assertEqual('call(x ,)', FST('call(a, b ,)').put_slice(FST('[x]'), 0, 2, raw=True).src)
        self.assertEqual('call(x ,)', FST('call(a, b ,)').put_slice(FST('(x,)'), 0, 2, raw=True).src)

        self.assertEqual('del x ,', FST('del a, b ,').put_slice(FST('[x]'), 0, 2, raw=True).src)
        self.assertEqual('del x ,', FST('del a, b ,').put_slice(FST('(x,)'), 0, 2, raw=True).src)

        self.assertEqual('class cls([x] ,): pass', FST('class cls(a, b ,): pass').put_slice(FST('[x]'), 0, 2, 'bases', raw=True, one=True).src)
        self.assertEqual('class cls((x,) ,): pass', FST('class cls(a, b ,): pass').put_slice(FST('(x,)'), 0, 2, 'bases', raw=True, one=True).src)

        self.assertEqual('call([x] ,)', FST('call(a, b ,)').put_slice(FST('[x]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('call((x,) ,)', FST('call(a, b ,)').put_slice(FST('(x,)'), 0, 2, raw=True, one=True).src)

        self.assertEqual('del [x] ,', FST('del a, b ,').put_slice(FST('[x]'), 0, 2, raw=True, one=True).src)
        self.assertEqual('del (x,) ,', FST('del a, b ,').put_slice(FST('(x,)'), 0, 2, raw=True, one=True).src)

        # special slices

        self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('x, y', '_withitems'), 0, 1, raw=True).src)
        self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('x, y', '_aliases'), 0, 1, raw=True).src)

        self.assertEqual('(x, y ,)', FST('(a,)').put_slice(FST('x, y ,', '_withitems'), 0, 1, raw=True).src)

        self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('x', '_withitems'), 0, 2, raw=True).src)
        self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('x', '_aliases'), 0, 2, raw=True).src)

        self.assertRaises(NodeError, FST('(a,)').put_slice, FST('x, y', '_withitems'), 0, 1, raw=True, one=True)
        self.assertRaises(NodeError, FST('(a,)').put_slice, FST('x, y', '_aliases'), 0, 1, raw=True, one=True)

        if PYGE12:
            self.assertEqual('(x, y)', FST('(a,)').put_slice(FST('x, y', '_type_params'), 0, 1, raw=True).src)
            self.assertEqual('(x, y ,)', FST('(a,)').put_slice(FST('x, y ,', '_type_params'), 0, 1, raw=True).src)
            self.assertEqual('(x,)', FST('(a, b)').put_slice(FST('x', '_type_params'), 0, 2, raw=True).src)
            self.assertRaises(NodeError, FST('(a,)').put_slice, FST('x, y', '_type_params'), 0, 1, raw=True, one=True)

    def test_slice_empty_set(self):
        with FST.options(norm=True):
            # put slice using norm_put=

            self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False).src)
            self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False).src)
            self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False).src)
            self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False).src)

            # self.assertRaises(NodeError, FST('[1, 2]').put_slice, 'set()', raw=False, norm_put='star')
            self.assertEqual('[set()]', FST('[1, 2]').put_slice('set()', raw=False, norm_put='star').src)
            self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, norm_put='star').src)
            self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, norm_put='star').src)
            self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, norm_put='star').src)

            self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, norm_put='call').src)
            self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, norm_put='call').src)
            self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, norm_put='call').src)
            self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, norm_put='call').src)

            # self.assertRaises(NodeError, FST('[1, 2]').put_slice, 'set()', raw=False, norm_put=False)
            self.assertEqual('[set()]', FST('[1, 2]').put_slice('{set()}', raw=False, norm_put=False).src)
            self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, norm_put=False).src)
            self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, norm_put=False).src)
            self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, norm_put=False).src)

            # using norm=

            # self.assertRaises(NodeError, FST('[1, 2]').put_slice, 'set()', raw=False, norm='star')
            self.assertEqual('[set()]', FST('[1, 2]').put_slice('set()', raw=False, norm='star').src)
            self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, norm='star').src)

            self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, norm='call').src)
            self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, norm='call').src)

            # self.assertRaises(NodeError, FST('[1, 2]').put_slice, 'set()', raw=False, norm=False)
            self.assertEqual('[set()]', FST('[1, 2]').put_slice('set()', raw=False, norm=False).src)
            self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, norm=False).src)

            # using set_norm=

            # self.assertRaises(NodeError, FST('[1, 2]').put_slice, 'set()', raw=False, set_norm='star')
            self.assertEqual('[set()]', FST('[1, 2]').put_slice('set()', raw=False, set_norm='star').src)
            self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, set_norm='star').src)

            self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, set_norm='call').src)
            self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, set_norm='call').src)

            # self.assertRaises(NodeError, FST('[1, 2]').put_slice, 'set()', raw=False, set_norm=False)
            self.assertEqual('[set()]', FST('[1, 2]').put_slice('set()', raw=False, set_norm=False).src)
            self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, set_norm=False).src)

            # delete

            self.assertEqual('{*()}', FST('{1}').put_slice(None, norm_self=True).src)
            self.assertEqual('{*()}', FST('{1}').put_slice(None, norm_self='star').src)
            self.assertEqual('{}', FST('{1}').put_slice(None, norm_self=False).src)
            self.assertEqual('set()', FST('{1}').put_slice(None, norm_self='call').src)

            self.assertEqual('{*()}', FST('{1}').put_slice(None, norm=True).src)
            self.assertEqual('{*()}', FST('{1}').put_slice(None, norm='star').src)
            self.assertEqual('{}', FST('{1}').put_slice(None, norm=False).src)
            self.assertEqual('set()', FST('{1}').put_slice(None, norm='call').src)

            self.assertEqual('{*()}', FST('{1}').put_slice(None, set_norm=True).src)
            self.assertEqual('{*()}', FST('{1}').put_slice(None, set_norm='star').src)
            self.assertEqual('{}', FST('{1}').put_slice(None, set_norm=False).src)
            self.assertEqual('set()', FST('{1}').put_slice(None, set_norm='call').src)

            # put as one

            self.assertEqual('[1, {*()}, 2]', (f := FST('[1, 2]')).put_slice(new_empty_set_curlies(), 1, 1, one=True).src)
            f.verify()

            self.assertEqual('[1, set(), 2]', (f := FST('[1, 2]')).put_slice(new_empty_set_curlies(), 1, 1, one=True, norm_put='call').src)
            f.verify()

            self.assertEqual('[1, set(), 2]', (f := FST('[1, 2]')).put_slice(new_empty_set_curlies(), 1, 1, one=True, norm='call').src)
            f.verify()

            self.assertEqual('[1, set(), 2]', (f := FST('[1, 2]')).put_slice(new_empty_set_curlies(), 1, 1, one=True, set_norm='call').src)
            f.verify()

            self.assertEqual('[1, {}, 2]', (f := FST('[1, 2]')).put_slice(new_empty_set_curlies(), 1, 1, one=True, norm_put=False).src)
            self.assertIsNone(f.verify(raise_=False))

            self.assertEqual('[1, {}, 2]', (f := FST('[1, 2]')).put_slice(new_empty_set_curlies(), 1, 1, one=True, norm=False).src)
            self.assertIsNone(f.verify(raise_=False))

            self.assertEqual('[1, {}, 2]', (f := FST('[1, 2]')).put_slice(new_empty_set_curlies(), 1, 1, one=True, set_norm=False).src)
            self.assertIsNone(f.verify(raise_=False))

            # get empty slice

            set_ = FST('{1}')

            self.assertEqual('{*()}', set_.get(0, 0, norm_get=True).src)
            self.assertEqual('{*()}', set_.get(0, 0, norm_get='star').src)
            self.assertEqual('set()', set_.get(0, 0, norm_get='call').src)
            self.assertEqual('{}', set_.get(0, 0, norm_get=False).src)

            self.assertEqual('{*()}', set_.get(0, 0, norm=True).src)
            self.assertEqual('{*()}', set_.get(0, 0, norm='star').src)
            self.assertEqual('set()', set_.get(0, 0, norm='call').src)
            self.assertEqual('{}', set_.get(0, 0, norm=False).src)

            self.assertEqual('{*()}', set_.get(0, 0, set_norm=True).src)
            self.assertEqual('{*()}', set_.get(0, 0, set_norm='star').src)
            self.assertEqual('set()', set_.get(0, 0, set_norm='call').src)
            self.assertEqual('{}', set_.get(0, 0, set_norm=False).src)

            # cut empty slice

            self.assertEqual(('{1}', '{*()}'), ((f := FST('{1}')).get_slice(cut=True, norm_self=True).src, f.src))
            self.assertEqual(('{1}', '{*()}'), ((f := FST('{1}')).get_slice(cut=True, norm_self='star').src, f.src))
            self.assertEqual(('{1}', '{}'), ((f := FST('{1}')).get_slice(cut=True, norm_self=False).src, f.src))
            self.assertEqual(('{1}', 'set()'), ((f := FST('{1}')).get_slice(cut=True, norm_self='call').src, f.src))

            self.assertEqual(('{1}', '{*()}'), ((f := FST('{1}')).get_slice(cut=True, norm=True).src, f.src))
            self.assertEqual(('{1}', '{*()}'), ((f := FST('{1}')).get_slice(cut=True, norm='star').src, f.src))
            self.assertEqual(('{1}', '{}'), ((f := FST('{1}')).get_slice(cut=True, norm=False).src, f.src))
            self.assertEqual(('{1}', 'set()'), ((f := FST('{1}')).get_slice(cut=True, norm='call').src, f.src))

            self.assertEqual(('{1}', '{*()}'), ((f := FST('{1}')).get_slice(cut=True, set_norm=True).src, f.src))
            self.assertEqual(('{1}', '{*()}'), ((f := FST('{1}')).get_slice(cut=True, set_norm='star').src, f.src))
            self.assertEqual(('{1}', '{}'), ((f := FST('{1}')).get_slice(cut=True, set_norm=False).src, f.src))
            self.assertEqual(('{1}', 'set()'), ((f := FST('{1}')).get_slice(cut=True, set_norm='call').src, f.src))

            # misc

            f = parse('{*()}').body[0].value.f
            self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
            self.assertEqual('{*()}', f.src)
            self.assertEqual('{*()}', f.put_slice('{*()}', 0, 0).src)
            f.root.verify()

            f = parse('{*[]}').body[0].value.f
            self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
            self.assertEqual('{*[]}', f.src)
            self.assertEqual('{*[]}', f.put_slice('{*()}', 0, 0).src)
            f.root.verify()

            f = parse('{*{}}').body[0].value.f
            self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
            self.assertEqual('{*{}}', f.src)
            self.assertEqual('{*{}}', f.put_slice('{*()}', 0, 0).src)
            f.root.verify()

            f = parse('{ * ( ) }').body[0].value.f
            self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
            self.assertEqual('{ * ( ) }', f.src)
            self.assertEqual('{ * ( ) }', f.put_slice('{*()}', 0, 0).src)
            f.root.verify()

    def test_slice_matchor_empty_or_len1(self):
        with FST.options(norm=True):
            self.assertEqual('', FST('a | b', pattern).get_slice(0, 0, norm_get=False).src)
            self.assertRaises(ValueError, FST('a | b', pattern).get_slice, 0, 0, norm_get=True)

            self.assertEqual('a', FST('a | b', pattern).get_slice(0, 1, norm_get=False).src)
            self.assertEqual('a', FST('a | b', pattern).get_slice(0, 1, norm_get=True).src)

            self.assertEqual('a | b', FST('a | b', pattern).get_slice(0, 2, norm_get=False).src)
            self.assertEqual('a | b', FST('a | b', pattern).get_slice(0, 2, norm_get=True).src)

            self.assertEqual('', FST('a | b', pattern).get_slice(0, 0, norm=False).src)
            self.assertRaises(ValueError, FST('a | b', pattern).get_slice, 0, 0, norm=True)

            self.assertEqual('a', FST('a | b', pattern).get_slice(0, 1, norm=False).src)
            self.assertEqual('a', FST('a | b', pattern).get_slice(0, 1, norm=True).src)

            self.assertEqual('a | b', FST('a | b', pattern).get_slice(0, 2, norm=False).src)
            self.assertEqual('a | b', FST('a | b', pattern).get_slice(0, 2, norm=True).src)

            len0mo = FST('c | d', pattern).get_slice(0, 0, norm_get=False)
            len1mo = FST('c | d', pattern).get_slice(0, 1, norm_get=False)
            len2mo = FST('c | d', pattern)

            self.assertTrue(compare_asts(len0mo.a, FST('c | d', pattern).get_slice(0, 0, norm=False).a, locs=True))

            self.assertTrue(compare_asts(len1mo.a, FST('c | d', pattern).get_slice(0, 1, norm=False).a, locs=True))

            self.assertEqual('a | b', FST('a | b', pattern).put_slice(None, 2, 2, norm_put=False).src)
            self.assertEqual('a | b', FST('a | b', pattern).put_slice(None, 2, 2, norm_put=True).src)

            self.assertEqual('a | b', FST('a | b', pattern).put_slice('', 2, 2, norm_put=False).src)
            self.assertEqual('a | b', FST('a | b', pattern).put_slice('', 2, 2, norm_put=True).src)

            self.assertEqual('a | b', FST('a | b', pattern).put_slice(len0mo.copy(), 2, 2, norm_put=False).src)
            self.assertEqual('a | b', FST('a | b', pattern).put_slice(len0mo.copy(), 2, 2, norm_put=True).src)

            self.assertEqual('a | b | c', FST('a | b', pattern).put_slice(len1mo.copy(), 2, 2, norm_put=False).src)
            self.assertEqual('a | b | c', FST('a | b', pattern).put_slice(len1mo.copy(), 2, 2, norm_put=True).src)

            self.assertEqual('a | b | c | d', FST('a | b', pattern).put_slice(len2mo.copy(), 2, 2, norm_put=False).src)
            self.assertEqual('a | b | c | d', FST('a | b', pattern).put_slice(len2mo.copy(), 2, 2, norm_put=True).src)

            self.assertEqual('a | b', FST('a | b', pattern).put_slice(len0mo.copy(), 2, 2, one=True, norm_put=False).src)
            self.assertEqual('a | b', FST('a | b', pattern).put_slice(len0mo.copy(), 2, 2, one=True, norm_put=True).src)

            self.assertEqual('a | b | c', FST('a | b', pattern).put_slice(len1mo.copy(), 2, 2, one=True, norm_put=False).src)
            self.assertEqual('a | b | c', FST('a | b', pattern).put_slice(len1mo.copy(), 2, 2, one=True, norm_put=True).src)

            self.assertEqual('a | b | (c | d)', FST('a | b', pattern).put_slice(len2mo.copy(), 2, 2, one=True, norm_put=False).src)
            self.assertEqual('a | b | (c | d)', FST('a | b', pattern).put_slice(len2mo.copy(), 2, 2, one=True, norm_put=True).src)

            self.assertEqual('a | y', FST('a | b | x | y', pattern).put_slice(len0mo.copy(), 1, 3, one=True, norm_put=False).src)
            self.assertEqual('a | y', FST('a | b | x | y', pattern).put_slice(len0mo.copy(), 1, 3, one=True, norm_put=True).src)

            self.assertEqual('a | c | y', FST('a | b | x | y', pattern).put_slice(len1mo.copy(), 1, 3, one=True, norm_put=False).src)
            self.assertEqual('a | c | y', FST('a | b | x | y', pattern).put_slice(len1mo.copy(), 1, 3, one=True, norm_put=True).src)

            with FST.options(norm_get=False):
                (f := FST('a | b', pattern)).get_slice(0, 0, cut=True, norm_self=False)
                self.assertEqual('a | b', f.src)
                self.assertIsInstance(f.a, MatchOr)

                (f := FST('a | b', pattern)).get_slice(0, 0, cut=True, norm_self=True)
                self.assertEqual('a | b', f.src)
                self.assertIsInstance(f.a, MatchOr)

                (f := FST('a | b', pattern)).get_slice(0, 1, cut=True, norm_self=False)
                self.assertEqual('b', f.src)
                self.assertIsInstance(f.a, MatchOr)

                (f := FST('a | b', pattern)).get_slice(0, 1, cut=True, norm_self=True)
                self.assertEqual('b', f.src)
                self.assertIsInstance(f.a, MatchAs)

                (f := FST('a | b', pattern)).get_slice(0, 2, cut=True, norm_self=False)
                self.assertEqual('', f.src)
                self.assertIsInstance(f.a, MatchOr)

                self.assertRaises(ValueError, (f := FST('a | b', pattern)).get_slice, 0, 2, cut=True, norm_self=True)

                (f := FST('a | b', pattern)).put_slice(None, 0, 0, norm_self=False)
                self.assertEqual('a | b', f.src)
                self.assertIsInstance(f.a, MatchOr)

                (f := FST('a | b', pattern)).put_slice(None, 0, 0, norm_self=True)
                self.assertEqual('a | b', f.src)
                self.assertIsInstance(f.a, MatchOr)

                (f := FST('a | b', pattern)).put_slice(None, 0, 1, norm_self=False)
                self.assertEqual('b', f.src)
                self.assertIsInstance(f.a, MatchOr)

                (f := FST('a | b', pattern)).put_slice(None, 0, 1, norm_self=True)
                self.assertEqual('b', f.src)
                self.assertIsInstance(f.a, MatchAs)

                (f := FST('a | b', pattern)).put_slice(None, 0, 2, norm_self=False)
                self.assertEqual('', f.src)
                self.assertIsInstance(f.a, MatchOr)

                self.assertRaises(ValueError, (f := FST('a | b', pattern)).put_slice, None, 0, 2, norm_self=True)

    def test_slice_line_continuations(self):
        f = FST(r'''del a, b, c, \
 \
z''')
        g = f.get_slice(2, 3, 'targets', cut=True, trivia=(None, 'all-'))
        self.assertEqual('del a, b, \\\nz', f.src)
        self.assertEqual('c,', g.src)
        f.verify()
        g.verify()

        f = FST(r'''del a, b, c, \
 \
z''')
        f.put_slice(None, 2, 3, 'targets', trivia=(None, 'all-'))
        self.assertEqual('del a, b, \\\nz', f.src)
        f.verify()

        self.assertEqual('del a, x, \\\n    y, c', (f := FST('del a, b, c')).put_slice('x,\ny', 1, 2).src)
        f.verify()

        f = FST(r'''a = b = c = \
 \
z''')
        g = f.get_slice(2, 3, 'targets', cut=True, trivia=(None, 'all-'))
        self.assertEqual('a = b = \\\nz', f.src)
        self.assertEqual('c =', g.src)
        f.verify()
        g.verify()

        f = FST(r'''a = b = c = \
 \
z''')
        f.put_slice(None, 2, 3, 'targets', trivia=(None, 'all-'))
        self.assertEqual('a = b = \\\nz', f.src)
        f.verify()

        s = FST('x =\\\ny', '_Assign_targets')
        s._put_src(' ', 0, 3, 0, 4)
        self.assertEqual('x = \ny', s.src)
        self.assertEqual('a = x = \\\ny = c', (f := FST('a = b = c')).put_slice(s, 1, 2, 'targets').src)
        f.verify()

    def test_slice_trivia_pars_and_one(self):
        # matchor

        f = FST('a | b', pattern)
        self.assertEqual(f.put_slice('( # pre\nc | # line\nd # line\n# post\n)', 1, 1, one=True).src, '''
a | ( # pre
c | # line
d # line
# post
) | b
            '''.strip())
        f.verify()

        f = FST('a | b', pattern)
        self.assertEqual(f.put_slice('# pre\nc | # line\nd # line\n# post\n', 1, 1).src, '''
(a | # pre
c | # line
d | # line
# post
b)
            '''.strip())
        f.verify()

        f = FST('a | b', pattern)
        self.assertEqual(f.put_slice('# pre\nc | # line\nd # line\n# post\n', 1, 1, one=True).src, '''
a | (# pre
c | # line
d # line
# post
) | b
            '''.strip())
        f.verify()

        f = FST('a |\n# pre\nc | # line\nd # line\n# post\n| b', pattern)
        self.assertEqual((g := f.get_slice(1, 3, cut=True, trivia=('all', 'all'))).src, '''
# pre
(c | # line
d) # line
# post
''')
        g.verify()

        self.assertEqual(f.src, '''
(a |
b)'''.strip())
        f.verify()

        self.assertEqual(f.put_slice(g, 1, 1).src, '''
(a |
# pre
c | # line
d | # line
# post
b)'''.strip())
        f.verify()

        self.assertEqual('''
(a |
# pre
c | d | # line
# post
b)
            '''.strip(), (f := FST('a | b', pattern)).put_slice('\n# pre\nc | d # line\n# post\n', 1, 1).src)
        f.verify()

        self.assertEqual('''
a | (
# pre
c | d # line
# post
) | b
            '''.strip(), (f := FST('a | b', pattern)).put_slice('\n# pre\nc | d # line\n# post\n', 1, 1, one=True).src)
        f.verify()

        self.assertEqual('''
(a |
# pre
c | d | # post
b)
            '''.strip(), (f := FST('a | b', pattern)).put_slice('\n# pre\n(c | d # line\n) # post\n', 1, 1).src)
        f.verify()

        self.assertEqual('''
(a |
# pre
(c | d # line
) | # post
b)
            '''.strip(), (f := FST('a | b', pattern)).put_slice('\n# pre\n(c | d # line\n) # post\n', 1, 1, one=True).src)
        f.verify()

        self.assertEqual('''
(a |
(# pre
(c | d # line
)) | # post
b)
            '''.strip(), (f := FST('a | b', pattern)).put_slice('\n(# pre\n(c | d # line\n)) # post\n', 1, 1, one=True).src)
        f.verify()

        self.assertEqual('''
a | (
# pre
(c | d # line
) # post
) | b
            '''.strip(), (f := FST('a | b', pattern)).put_slice('(\n# pre\n(c | d # line\n) # post\n)', 1, 1, one=True).src)
        f.verify()

        # Tuple (and list and Set)

        self.assertEqual('1, a,\\\nb, \\\n2', (f := FST('1, 2').put_slice('a,\\\nb,\\\n', 1, 1)).src)
        f.verify()
        self.assertEqual('1, (a,\\\nb,\\\n), 2', (f := FST('1, 2').put_slice('a,\\\nb,\\\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('(1, a, # comment\nb, \\\n2)', (f := FST('1, 2').put_slice('a, # comment\nb,\\\n', 1, 1)).src)
        f.verify()
        self.assertEqual('1, (a, # comment\nb,\\\n), 2', (f := FST('1, 2').put_slice('a, # comment\nb,\\\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('(a,\n# pre\nc, # line\n# post\nb)', (f := FST('a, b').put_slice('\n# pre\nc, # line\n# post\n', 1, 1)).src)
        f.verify()
        self.assertEqual('a, (\n# pre\nc, # line\n# post\n), b', (f := FST('a, b').put_slice('\n# pre\nc, # line\n# post\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('(a, c, # line\nb)', (f := FST('a, b').put_slice('\n# pre\n[c, # line\n]# post\n', 1, 1)).src)
        f.verify()
        self.assertEqual('(a,\n# pre\n[c, # line\n], # post\nb)', (f := FST('a, b').put_slice('\n# pre\n[c, # line\n]# post\n', 1, 1, one=True)).src)
        f.verify()
        self.assertEqual('(a,\n(# pre\n[c, # line\n]), # post\nb)', (f := FST('a, b').put_slice('\n(# pre\n[c, # line\n])# post\n', 1, 1, one=True)).src)
        f.verify()
        self.assertEqual('a, (\n# pre\n[c, # line\n]# post\n), b', (f := FST('a, b').put_slice('(\n# pre\n[c, # line\n]# post\n)', 1, 1, one=True)).src)
        f.verify()

        # List (for the brackets)

        self.assertEqual('[1, a,\\\n b, \\\n 2]', (f := FST('[1, 2]').put_slice('a,\\\nb,\\\n', 1, 1)).src)
        f.verify()
        self.assertEqual('[1, (a,\\\n b,\\\n ), 2]', (f := FST('[1, 2]').put_slice('a,\\\nb,\\\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('[1, a, # comment\n b, \\\n 2]', (f := FST('[1, 2]').put_slice('a, # comment\nb,\\\n', 1, 1)).src)
        f.verify()
        self.assertEqual('[1, (a, # comment\n b,\\\n ), 2]', (f := FST('[1, 2]').put_slice('a, # comment\nb,\\\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('[a,\n # pre\n c, # line\n # post\n b]', (f := FST('[a, b]').put_slice('\n# pre\nc, # line\n# post\n', 1, 1)).src)
        f.verify()
        self.assertEqual('[a, (\n # pre\n c, # line\n # post\n ), b]', (f := FST('[a, b]').put_slice('\n# pre\nc, # line\n# post\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('[a, c, # line\n b]', (f := FST('[a, b]').put_slice('\n# pre\n[c, # line\n]# post\n', 1, 1)).src)
        f.verify()
        self.assertEqual('[a,\n # pre\n [c, # line\n ], # post\n b]', (f := FST('[a, b]').put_slice('\n# pre\n[c, # line\n]# post\n', 1, 1, one=True)).src)
        f.verify()
        self.assertEqual('[a,\n (# pre\n [c, # line\n ]), # post\n b]', (f := FST('[a, b]').put_slice('\n(# pre\n[c, # line\n])# post\n', 1, 1, one=True)).src)
        f.verify()
        self.assertEqual('[a, (\n # pre\n [c, # line\n ]# post\n ), b]', (f := FST('[a, b]').put_slice('(\n# pre\n[c, # line\n]# post\n)', 1, 1, one=True)).src)
        f.verify()

        # Dict

        self.assertEqual('{a: a,\n # pre\n c: c, # line\n # post\n b: b}', (f := FST('{a: a, b: b}').put_slice('{\n# pre\nc: c, # line\n# post\n}', 1, 1)).src)
        f.verify()
        self.assertEqual('{a: a, c: c, # line\n b: b}', (f := FST('{a: a, b: b}').put_slice('\n# pre\n{c: c, # line\n}# post\n', 1, 1)).src)
        f.verify()
        self.assertEqual('{a: a, c: c, b: b}', (f := FST('{a: a, b: b}').put_slice('\n# pre\n{c: c} # line\n# post\n', 1, 1)).src)
        f.verify()

        # MatchSequence

        self.assertEqual('1, a,\\\nb, \\\n2', (f := FST('1, 2', pattern).put_slice('a,\\\nb,\\\n', 1, 1)).src)
        f.verify()
        self.assertEqual('1, [a,\\\nb,\\\n], 2', (f := FST('1, 2', pattern).put_slice('a,\\\nb,\\\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('[1, a, # comment\nb, \\\n2]', (f := FST('1, 2', pattern).put_slice('a, # comment\nb,\\\n', 1, 1)).src)
        f.verify()
        self.assertEqual('1, [a, # comment\nb,\\\n], 2', (f := FST('1, 2', pattern).put_slice('a, # comment\nb,\\\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('[a,\n# pre\nc, # line\n# post\nb]', (f := FST('a, b', pattern).put_slice('\n# pre\nc, # line\n# post\n', 1, 1)).src)
        f.verify()
        self.assertEqual('a, [\n# pre\nc, # line\n# post\n], b', (f := FST('a, b', pattern).put_slice('\n# pre\nc, # line\n# post\n', 1, 1, one=True)).src)
        f.verify()

        self.assertEqual('[a, c, # line\nb]', (f := FST('a, b', pattern).put_slice('\n# pre\n[c, # line\n]# post\n', 1, 1)).src)
        f.verify()
        self.assertEqual('[a,\n# pre\n[c, # line\n], # post\nb]', (f := FST('a, b', pattern).put_slice('\n# pre\n[c, # line\n]# post\n', 1, 1, one=True)).src)
        f.verify()
        self.assertEqual('[a,\n(# pre\n[c, # line\n]), # post\nb]', (f := FST('a, b', pattern).put_slice('\n(# pre\n[c, # line\n])# post\n', 1, 1, one=True)).src)
        f.verify()
        self.assertEqual('a, (\n# pre\n[c, # line\n]# post\n), b', (f := FST('a, b', pattern).put_slice('(\n# pre\n[c, # line\n]# post\n)', 1, 1, one=True)).src)
        f.verify()

    def test_insert_into_empty_block(self):
        a = parse('''
if 1:
    i \\

'''.lstrip())
        a.body[0].f.put_slice('j', field='orelse')
        a.f.verify()
        self.assertEqual(a.f.src, 'if 1:\n    i\nelse:\n    j\n\n')

        a = parse('''
def f():
    pass
        '''.strip())
        a.body[0].body[0].f.cut(norm=False)
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'def f():\n    i')

        a = parse('''
def f(): pass
        '''.strip())
        a.body[0].body[0].f.cut(norm=False)
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'def f():\n    i')

        a = parse('''
def f():
    pass
        '''.strip())
        a.body[0].body[0].f.cut(norm=False)
        a.body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'def f():\n    # pre\n    i  # post')

        a = parse('''
def f(): pass
        '''.strip())
        a.body[0].body[0].f.cut(norm=False)
        a.body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'def f():\n    # pre\n    i  # post')

        a = parse('''
match a:
    case 1: pass
        '''.strip())
        a.body[0].cases[0].body[0].f.cut(norm=False)
        a.body[0].cases[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'match a:\n    case 1:\n        i')

        a = parse('''
match a:
    case 1: pass
        '''.strip())
        a.body[0].cases[0].f.cut(norm=False)
        a.body[0].f.put_slice('case 2: return')
        self.assertEqual(a.f.src, 'match a:\n    case 2: return')


        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].body[0].f.cut(norm=False)
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 1:\n    i')

        a = parse('''
if 1:
    pass
else: pass
        '''.strip())
        a.body[0].body[0].f.cut(norm=False)
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 1:\n    i\nelse: pass')

        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].body[0].f.cut(norm=False)
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 1:\nelse:\n    i')

        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 1:\n    pass\nelse:\n    i')


        a = parse('''if 2:
    def f():
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut(norm=False)
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        i')

        a = parse('''if 2:
    def f(): pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut(norm=False)
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        i')

        a = parse('''if 2:
    def f():
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut(norm=False)
        a.body[0].body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        # pre\n        i  # post')

        a = parse('''if 2:
    def f(): pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut(norm=False)
        a.body[0].body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        # pre\n        i  # post')

        a = parse('''if 2:
    match a:
        case 1: pass
        '''.strip())
        a.body[0].body[0].cases[0].body[0].f.cut(norm=False)
        a.body[0].body[0].cases[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    match a:\n        case 1:\n            i')

        a = parse('''if 2:
    match a:
        case 1: pass
        '''.strip())
        a.body[0].body[0].cases[0].f.cut(norm=False)
        a.body[0].body[0].f.put_slice('case 3: return')
        self.assertEqual(a.f.src, 'if 2:\n    match a:\n        case 3: return')


        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut(norm=False)
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        i')

        a = parse('''if 2:
    if 1:
        pass
    else: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut(norm=False)
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        i\n    else: pass')

        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut(norm=False)
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n    else:\n        i')

        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        pass\n    else:\n        i')


        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='finalbody')
            self.assertEqual(a.f.src, 'try:\nfinally:\n    i')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='orelse')
            self.assertEqual(a.f.src, 'try:\nelse:\n    i')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            handler = a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice(handler, field='handlers')
            self.assertEqual(a.f.src, 'try:\nexcept: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='body')
            self.assertEqual(a.f.src, 'try:\n    i')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].handlers[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='finalbody')
            self.assertEqual(a.f.src, 'try:\nelse: pass\nfinally:\n    i')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='finalbody')
            self.assertEqual(a.f.src, 'try:\nexcept: pass\nfinally:\n    i')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='finalbody')
            self.assertEqual(a.f.src, 'try: pass\nfinally:\n    i')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].f.put_slice('i', field='orelse')
            self.assertEqual(a.f.src, 'try:\nelse:\n    i\nfinally: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='orelse')
            self.assertEqual(a.f.src, 'try:\nexcept: pass\nelse:\n    i')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='orelse')
            self.assertEqual(a.f.src, 'try: pass\nelse:\n    i')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            handler = a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].f.put_slice(handler, field='handlers')
            self.assertEqual(a.f.src, 'try:\nexcept: pass\nfinally: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            handler = a.body[0].handlers[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice(handler, field='handlers')
            self.assertEqual(a.f.src, 'try:\nexcept: pass\nelse: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            handler = a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice(handler, field='handlers')
            self.assertEqual(a.f.src, 'try: pass\nexcept: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].handlers[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].f.put_slice('i', field='body')
            self.assertEqual(a.f.src, 'try:\n    i\nfinally: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].handlers[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='body')
            self.assertEqual(a.f.src, 'try:\n    i\nelse: pass')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].f.cut()
            a.body[0].orelse[0].f.cut()
            a.body[0].finalbody[0].f.cut()
            a.body[0].f.put_slice('i', field='body')
            self.assertEqual(a.f.src, 'try:\n    i\nexcept: pass')


        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='finalbody')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    finally:\n        i')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='orelse')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    else:\n        i')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            handler = a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice(handler, field='handlers')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='body')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n        i')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='finalbody')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    else: pass\n    finally:\n        i')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='finalbody')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    finally:\n        i')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='finalbody')
            self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    finally:\n        i')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='orelse')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    else:\n        i\n    finally: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='orelse')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    else:\n        i')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='orelse')
            self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    else:\n        i')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            handler = a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].f.put_slice(handler, field='handlers')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    finally: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            handler = a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice(handler, field='handlers')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    else: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            handler = a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice(handler, field='handlers')
            self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    except: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='body')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n    finally: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].handlers[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='body')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n    else: pass')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        with FST.options(norm=False):
            a.body[0].body[0].body[0].f.cut()
            a.body[0].body[0].orelse[0].f.cut()
            a.body[0].body[0].finalbody[0].f.cut()
            a.body[0].body[0].f.put_slice('i', field='body')
            self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n    except: pass')

    def test_insert_into_empty_block_shuffle(self):  # TODO: legacy, do better when possible
        fst = parse('''
match a:
    case 1:
        i = 1

match b:
    case 2:
        pass  # this is removed

if 1:
    j; k
else:
    l
    m

try:
    # pre
    n  # post
except:
    if 1: break
else:
    if 2: continue
    elif 3: o
    else: p
finally:
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q

for a in b:
    # pre-classdeco
    @classdeco
    class cls:
        @methdeco
        def meth(self):
            mvar = 5  # post-meth
else:
    """Multi
    line
    string."""

async for a in b:
    ("Multi"
    "line"
    "string")
else:
    r = [i for i in range(100)]  # post-list-comprehension

while a in b:
    global c
else:
    lambda x: x**2

with a as b:
    try: a ; #  post-try
    except: b ; c  # post-except
    else: return 5
    finally: yield 6

async with a as b:
    del x, y, z

def func():
    assert s, t

@asyncdeco
async def func():
    match z:
        case 1: zz
        case 2:
            zzz

class cls:
    def docfunc(a, /, b=2, *c, d=3, **e):
        """Doc
        string."""

        return -1

if indented:
    try:
        try: raise
        except Exception as exc:
            raise exc from exc
    except:
        aa or bb or cc
    else:
        f'{i:2} plus 1'
    finally:
        j = (i := k)
'''.lstrip()).f

        # fst.a.body[1].cases[0].f.cut()
        # fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            # (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),
            (fst.a.body[2].f, 'orelse'),
            (fst.a.body[3].f, 'body'),
            # (fst.a.body[3].f, 'handlers'),
            (fst.a.body[3].f, 'orelse'),
            (fst.a.body[3].f, 'finalbody'),
            (fst.a.body[4].f, 'body'),
            (fst.a.body[4].f, 'orelse'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[5].f, 'orelse'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[6].f, 'orelse'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),
            # (fst.a.body[12].body[0].f, 'handlers'),
            (fst.a.body[12].body[0].f, 'orelse'),
            (fst.a.body[12].body[0].f, 'finalbody'),
        ]

        seed(0)

        bs = []
        ps = points[:]

        shuffle(ps)

        while ps:
            f, field = ps.pop()

            bs.append(f.get_slice(field=field, cut=True, norm=False))

        ps = points[:]

        shuffle(ps)
        shuffle(bs)

        while ps:
            f, field = ps.pop()

            f.put_slice(bs.pop(), 0, 0, field=field)#, check_node_type=False)

        # print('...')
        # print(fst.src)
        # print('...')

        self.assertEqual(fst.src, '''
match a:
    case 1:
        if 2: continue
        elif 3: o
        else: p

match b:
    case 2:
        pass  # this is removed

if 1:
    # pre
    n  # post
else:
    try: a ; #  post-try
    except: b ; c  # post-except
    else: return 5
    finally: yield 6

try:
    l
    m
except:
    if 1: break
else:
    assert s, t
finally:
    # pre-classdeco
    @classdeco
    class cls:
        @methdeco
        def meth(self):
            mvar = 5  # post-meth

for a in b:
    lambda x: x**2
else:
    """Multi
    line
    string."""

async for a in b:
    ("Multi"
    "line"
    "string")
else:
    j; k

while a in b:
    i = 1
else:
    global c

with a as b:
    del x, y, z

async with a as b:
    f'{i:2} plus 1'

def func():
    j = (i := k)

@asyncdeco
async def func():
    r = [i for i in range(100)]  # post-list-comprehension

class cls:
    def docfunc(a, /, b=2, *c, d=3, **e):
        """Doc
        string."""

        return -1

if indented:
    try:
        match z:
            case 1: zz
            case 2:
                zzz
    except:
        aa or bb or cc
    else:
        @deco
        def inner() -> list[int]:
            q = 4  # post-inner-q
    finally:
        try: raise
        except Exception as exc:
            raise exc from exc
'''.strip())

        for _ in range(25):  # now just fuzz it a bit, just in case
            bs = []
            ps = points[:]

            shuffle(ps)

            while ps:
                f, field = ps.pop()

                bs.append(f.get_slice(field=field, cut=True, norm=False))

            ps = points[:]

            shuffle(ps)
            shuffle(bs)

            while ps:
                f, field = ps.pop()

                f.put_slice(bs.pop(), 0, 0, field=field)#, check_node_type=False)

    def test_insert_comment_into_empty_field(self):  # TODO: legacy, do better when possible
        fst = parse('''
match a:
    case 1:  # CASE
        pass

match b:  # MATCH
    case 2:
        pass

if 1:  # IF
    pass

try:  # TRY
    pass
except:  # EXCEPT
    pass

for a in b:  # FOR
    pass

async for a in b:  # ASYNC FOR
    pass

while a in b:  # WHILE
    pass

with a as b:  # WITH
    pass

async with a as b:  # ASYNC WITH
    pass

def func(a = """ \\\\ not linecont
         # comment
         """, **e):
    pass

@asyncdeco
async def func():  # ASYNC FUNC
    pass

class cls:  # CLASS
    pass

if clause:
    while something:  # WHILE
        pass

if indented:
    try:  # TRY
        pass
    except:  # EXCEPT
        pass
'''.lstrip()).f

        # fst.a.body[1].cases[0].f.cut()
        # fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            # (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),

            (fst.a.body[3].f, 'body'),
            # (fst.a.body[3].f, 'handlers'),

            (fst.a.body[4].f, 'body'),
            (fst.a.body[5].f, 'body'),
            (fst.a.body[6].f, 'body'),
            (fst.a.body[7].f, 'body'),
            (fst.a.body[8].f, 'body'),
            (fst.a.body[9].f, 'body'),
            (fst.a.body[10].f, 'body'),
            (fst.a.body[11].f, 'body'),
            (fst.a.body[12].body[0].f, 'body'),

            (fst.a.body[13].body[0].f, 'body'),
            # (fst.a.body[13].body[0].f, 'handlers'),
        ]

        for point, field in points:
            point.get_slice(field=field, cut=True, norm=False)

        for i, (point, field) in enumerate(reversed(points)):
            point.put_slice(f'# {i}', 0, 0, field, norm=False)#, check_node_type=False)

        # print('...')
        # print('\n'.join(repr(l) for l in fst.lines))
        # print('...')

        self.assertEqual(fst.lines, [
            'match a:',
            '    case 1:  # CASE',
            '        # 12',
            '',
            'match b:  # MATCH',
            '    case 2:',
            '        pass',
            '',
            'if 1:  # IF',
            '    # 11',
            '',
            'try:  # TRY',
            '    # 10',
            'except:  # EXCEPT',
            '    pass',
            '',
            'for a in b:  # FOR',
            '    # 9',
            '',
            'async for a in b:  # ASYNC FOR',
            '    # 8',
            '',
            'while a in b:  # WHILE',
            '    # 7',
            '',
            'with a as b:  # WITH',
            '    # 6',
            '',
            'async with a as b:  # ASYNC WITH',
            '    # 5',
            '',
            'def func(a = """ \\\\ not linecont',
            '         # comment',
            '         """, **e):',
            '    # 4',
            '',
            '@asyncdeco',
            'async def func():  # ASYNC FUNC',
            '    # 3',
            '',
            'class cls:  # CLASS',
            '    # 2',
            '',
            'if clause:',
            '    while something:  # WHILE',
            '        # 1',
            '',
            'if indented:',
            '    try:  # TRY',
            '        # 0',
            '    except:  # EXCEPT',
            '        pass',
            '',
        ])

    def test_insert_stmt_special(self):
        a = parse('''
pass

try:
    break
except:
    continue
else:
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q
finally:
    pass
        '''.strip())
        a.body[1].body[0].f.cut(norm=False)
        a.body[1].handlers[0].f.cut()
        a.body[1].f.put_slice('# pre\nexcept Exception as exc: n  # post', 0, 0, 'handlers')
        a.body[1].f.put_slice('except ValueError as v: m', 0, 0, 'handlers')
        self.assertEqual(a.f.src, '''
pass

try:
except ValueError as v: m
# pre
except Exception as exc: n  # post
else:
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q
finally:
    pass
            '''.strip())

    def test_replace_stmt_special(self):
        a = parse('''
if 1: pass
elif 2:
    pass
        '''.strip())
        a.body[0].orelse[0].f.put_slice(None, 0, 1, norm=False)
        a.body[0].f.put_slice('break', 0, 1, 'orelse')
        self.assertEqual(a.f.src, 'if 1: pass\nelse:\n    break')

        a = parse('''
class cls:
    if 1: pass
    elif 2:
        pass
        '''.strip())
        a.body[0].body[0].orelse[0].f.put_slice(None, 0, 1, norm=False)
        a.body[0].body[0].f.put_slice('break', 0, 1, 'orelse')
        self.assertEqual(a.f.src, 'class cls:\n    if 1: pass\n    else:\n        break')

    def test_get_and_put_slice_from_to_slice(self):
        # stmts

        with FST.options(norm=True):
            self.assertEqual('a', (g := (f := FST('a\nb\nc').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('a\nb\na', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('a\nb\nc').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            f.verify()

        # ExceptHandlers

        with FST.options(norm=True):
            self.assertEqual('except a: pass', (g := (f := FST('except a: pass\nexcept b: pass\nexcept c: pass').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('except a: pass\nexcept b: pass\nexcept a: pass', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('except a: pass\nexcept b: pass\nexcept c: pass').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            f.verify()

        # match_cases

        with FST.options(norm=True):
            self.assertEqual('case a: pass', (g := (f := FST('case a: pass\ncase b: pass\ncase c: pass').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('case a: pass\ncase b: pass\ncase a: pass', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('case a: pass\ncase b: pass\ncase c: pass').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            f.verify()

        # Assign

        with FST.options(norm=True):
            self.assertEqual('a =', (g := (f := FST('a = b = c = z').get_slice(0, 2, 'targets')).get_slice(0, 1)).src)
            self.assertEqual('a = b = a =', f.put_slice(g, 'end', 'targets').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('a = b = c = z').get_slice(0, 0, 'targets')).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end', 'targets').src)
            f.verify()

        # Import

        with FST.options(norm=True):
            self.assertEqual('a', (g := (f := FST('import a, b, c').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('a, b, a', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('import a, b, c').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            f.verify()

        # Tuple (unparenthesized)

        with FST.options(norm=True):
            self.assertEqual('a,', (g := (f := FST('a, b, c').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('a, b, a', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('()', (g := (f := FST('a, b, c').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('()', f.put_slice(g, 'end').src)
            f.verify()

        # Tuple (parenthesized)

        with FST.options(norm=True):
            self.assertEqual('(a,)', (g := (f := FST('(a, b, c)').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('(a, b, a)', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('()', (g := (f := FST('(a, b, c)').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('()', f.put_slice(g, 'end').src)
            f.verify()

        # List

        with FST.options(norm=True):
            self.assertEqual('[a]', (g := (f := FST('[a, b, c]').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('[a, b, a]', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('[]', (g := (f := FST('[a, b, c]').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('[]', f.put_slice(g, 'end').src)
            f.verify()

        # Set

        with FST.options(norm=True):
            self.assertEqual('{a}', (g := (f := FST('{a, b, c}').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('{a, b, a}', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('{}', (g := (f := FST('{a, b, c}').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('{}', f.put_slice(g, 'end').src)
            # f.verify()  # empty invalid

        # Dict

        with FST.options(norm=True):
            self.assertEqual('{1:a}', (g := (f := FST('{1:a, 2:b, 3:c}').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('{1:a, 2:b, 1:a}', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('{}', (g := (f := FST('{1:a, 2:b, 3:c}').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('{}', f.put_slice(g, 'end').src)
            f.verify()

        # decorators

        with FST.options(norm=True):
            self.assertEqual('@a', (g := (f := FST('@a\n@b\n@c\nclass cls: pass').get_slice(0, 2, 'decorator_list')).get_slice(0, 1)).src)
            self.assertEqual('@a\n@b\n@a', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('@a\n@b\n@c\nclass cls: pass').get_slice(0, 0, 'decorator_list')).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            f.verify()

        # comprehensions

        with FST.options(norm=True):
            self.assertEqual('for i in i', (g := (f := FST('[_ for i in i for j in j for k in k]').get_slice(0, 2, 'generators')).get_slice(0, 1)).src)
            self.assertEqual('for i in i for j in j for i in i', f.put_slice(g, 'end', 'generators').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('[_ for i in i for j in j for k in k]').get_slice(0, 0, 'generators')).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end', 'generators').src)
            f.verify()

        # comprehension_ifs

        with FST.options(norm=True):
            self.assertEqual('if i', (g := (f := FST('for _ in _ if i if j if k').get_slice(0, 2, 'ifs')).get_slice(0, 1)).src)
            self.assertEqual('if i if j if i', f.put_slice(g, 'end', 'ifs').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('for _ in _ if i if j if k').get_slice(0, 0, 'ifs')).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end', 'ifs').src)
            f.verify()

        # Compare

        with FST.options(norm=True):
            self.assertEqual('i', (g := (f := FST('i < j < k').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('i < i', f.put_slice(g, 1).src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('i', (g := (f := FST('i < j < k').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('i < i', f.put_slice(g, 1).src)
            f.verify()

        # BoolOp

        with FST.options(norm=True):
            self.assertEqual('a', (g := (f := FST('a or b or c').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('a or b or a', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('a or b or c').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            # f.verify()

        # aliases

        with FST.options(norm=True):
            self.assertEqual('a.a', (g := (f := FST('import a.a, b.b, c.c').get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('a.a, b.b, a.a', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('import a.a, b.b, c.c').get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            f.verify()

        # withitems

        with FST.options(norm=True):
            self.assertEqual('a as a', (g := (f := FST('with a as a, b as b, c as c: pass').get_slice(0, 2, 'items')).get_slice(0, 1)).src)
            self.assertEqual('a as a, b as b, a as a', f.put_slice(g, 'end').src)
            f.verify()

            self.assertEqual('', (g := (f := FST('with a as a, b as b, c as c: pass').get_slice(0, 0, 'items')).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            f.verify()

        # MatchSequence

        with FST.options(norm=True):
            self.assertEqual('[a]', (g := (f := FST('[a, b, c]', pattern).get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('[a, b, a]', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('[]', (g := (f := FST('[a, b, c]', pattern).get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('[]', f.put_slice(g, 'end').src)
            f.verify()

        # MatchMapping

        with FST.options(norm=True):
            self.assertEqual('{1:a}', (g := (f := FST('{1:a, 2:b, 3:c}', pattern).get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('{1:a, 2:b, 1:a}', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('{}', (g := (f := FST('{1:a, 2:b, 3:c}', pattern).get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('{}', f.put_slice(g, 'end').src)
            f.verify()

        # MatchOr

        with FST.options(norm=True):
            self.assertEqual('a', (g := (f := FST('a | b | c', pattern).get_slice(0, 2)).get_slice(0, 1)).src)
            self.assertEqual('a | b | a', f.put_slice(g, 'end').src)
            f.verify()

        with FST.options(norm=False):
            self.assertEqual('', (g := (f := FST('a | b | c', pattern).get_slice(0, 0)).get_slice(0, 0)).src)
            self.assertEqual('', f.put_slice(g, 'end').src)
            # f.verify()  # empty invalid

        # type_params

        if PYGE12:
            # FunctionDef

            with FST.options(norm=True):
                self.assertEqual('T', (g := (f := FST('def f[T, *U, **V](): pass').get_slice(0, 2, 'type_params')).get_slice(0, 1)).src)
                self.assertEqual('T, *U, T', f.put_slice(g, 'end').src)
                f.verify()

            with FST.options(norm=False):
                self.assertEqual('', (g := (f := FST('def f[T, *U, **V](): pass').get_slice(0, 0, 'type_params')).get_slice(0, 0)).src)
                self.assertEqual('', f.put_slice(g, 'end').src)
                f.verify()

            # AsyncFunctionDef

            with FST.options(norm=True):
                self.assertEqual('T', (g := (f := FST('async def f[T, *U, **V](): pass').get_slice(0, 2, 'type_params')).get_slice(0, 1)).src)
                self.assertEqual('T, *U, T', f.put_slice(g, 'end').src)
                f.verify()

            with FST.options(norm=False):
                self.assertEqual('', (g := (f := FST('async def f[T, *U, **V](): pass').get_slice(0, 0, 'type_params')).get_slice(0, 0)).src)
                self.assertEqual('', f.put_slice(g, 'end').src)
                f.verify()

            # ClassDef

            with FST.options(norm=True):
                self.assertEqual('T', (g := (f := FST('class cls[T, *U, **V]: pass').get_slice(0, 2, 'type_params')).get_slice(0, 1)).src)
                self.assertEqual('T, *U, T', f.put_slice(g, 'end').src)
                f.verify()

            with FST.options(norm=False):
                self.assertEqual('', (g := (f := FST('class cls[T, *U, **V]: pass').get_slice(0, 0, 'type_params')).get_slice(0, 0)).src)
                self.assertEqual('', f.put_slice(g, 'end').src)
                f.verify()

            # TypeAlias

            with FST.options(norm=True):
                self.assertEqual('T', (g := (f := FST('type t[T, *U, **V] = ...').get_slice(0, 2, 'type_params')).get_slice(0, 1)).src)
                self.assertEqual('T, *U, T', f.put_slice(g, 'end').src)
                f.verify()

            with FST.options(norm=False):
                self.assertEqual('', (g := (f := FST('type t[T, *U, **V] = ...').get_slice(0, 0, 'type_params')).get_slice(0, 0)).src)
                self.assertEqual('', f.put_slice(g, 'end').src)
                f.verify()

    def test_invalid_AST_slice_usage_errors(self):
        # invalid-AST Tuple slice

        # TODO: with other invalid slices, e.g. Tuple[withitem]

        if PYGE12:
            self.assertRaises(NodeError, FST('a = b').put, FST('T, **U', '_type_params'), 'value')  # expr
            self.assertRaises(NodeError, FST('a = b').put, FST('T, **U', '_type_params').a, 'value')

            self.assertRaises(NodeError, FST('f(a)').put, FST('T, **U', '_type_params'), 0, 'args')  # expr_arglike
            self.assertRaises(NodeError, FST('f(a)').put, FST('T, **U', '_type_params').a, 0, 'args')

            self.assertRaises(NodeError, FST('a[b]').put, FST('T, **U', '_type_params'), 'slice')  # expr_slice
            self.assertRaises(NodeError, FST('a[b]').put, FST('T, **U', '_type_params').a, 'slice')

            self.assertRaises(NodeError, FST('a[b, c]').slice.put, FST('T, **U', '_type_params'), 0, 'elts')  # Tuple_elt
            self.assertRaises(NodeError, FST('a[b, c]').slice.put, FST('T, **U', '_type_params').a, 0, 'elts')

            self.assertRaises(NodeError, FST('(b, c)').put, FST('T, **U', '_type_params'), 0, 'elts')  # Tuple_elt
            self.assertRaises(NodeError, FST('(b, c)').put, FST('T, **U', '_type_params').a, 0, 'elts')

    @unittest.skipUnless(PYGE11, 'only valid for py >= 3.11')
    def test_except_vs_except_star(self):
        with FST.options(norm=False):
            # put to Try

            self.assertEqual('try: pass\nexcept  Exception: pass\nexcept  Exception: pass',
                             FST('try: pass\nexcept  Exception: pass').handlers.append('except  Exception: pass').base.root.src)
            self.assertEqual('try: pass\nexcept  Exception: pass\nexcept  Exception: pass',
                             FST('try: pass\nexcept  Exception: pass').handlers.append(FST('except  Exception: pass')).base.root.src)
            self.assertRaises(ParseError, FST('try: pass\nexcept  Exception: pass').handlers.append, 'except* Exception: pass')
            self.assertRaises(NodeError, FST('try: pass\nexcept  Exception: pass').handlers.append, FST('except* Exception: pass'))

            # put to Try with empty handlers

            self.assertEqual('try: pass\nexcept  Exception: pass',
                             FST('try: pass\nexcept  Exception: pass').put(None, 0, 1, 'handlers')
                             .handlers.append('except  Exception: pass').base.root.src)
            self.assertEqual('try: pass\nexcept  Exception: pass',
                             FST('try: pass\nexcept  Exception: pass').put(None, 0, 1, 'handlers')
                             .handlers.append(FST('except  Exception: pass')).base.root.src)
            self.assertEqual('try: pass\nexcept* Exception: pass',
                             FST('try: pass\nexcept  Exception: pass').put(None, 0, 1, 'handlers')
                             .handlers.append('except* Exception: pass').base.root.src)
            self.assertEqual('try: pass\nexcept* Exception: pass',
                             FST('try: pass\nexcept  Exception: pass').put(None, 0, 1, 'handlers')
                             .handlers.append(FST('except* Exception: pass')).base.root.src)

            # put to TryStar

            self.assertEqual('try: pass\nexcept* Exception: pass\nexcept* Exception: pass',
                             FST('try: pass\nexcept* Exception: pass').handlers.append('except* Exception: pass').base.root.src)
            self.assertEqual('try: pass\nexcept* Exception: pass\nexcept* Exception: pass',
                             FST('try: pass\nexcept* Exception: pass').handlers.append(FST('except* Exception: pass')).base.root.src)
            self.assertRaises(ParseError, FST('try: pass\nexcept* Exception: pass').handlers.append, 'except Exception: pass')
            self.assertRaises(NodeError, FST('try: pass\nexcept* Exception: pass').handlers.append, FST('except Exception: pass'))

            # put to TryStar with empty handlers

            self.assertEqual('try: pass\nexcept* Exception: pass',
                             FST('try: pass\nexcept* Exception: pass').put(None, 0, 1, 'handlers')
                             .handlers.append('except* Exception: pass').base.root.src)
            self.assertEqual('try: pass\nexcept* Exception: pass',
                             FST('try: pass\nexcept* Exception: pass').put(None, 0, 1, 'handlers')
                             .handlers.append(FST('except* Exception: pass')).base.root.src)
            self.assertEqual('try: pass\nexcept Exception: pass',
                             FST('try: pass\nexcept* Exception: pass').put(None, 0, 1, 'handlers')
                             .handlers.append('except Exception: pass').base.root.src)
            self.assertEqual('try: pass\nexcept Exception: pass',
                             FST('try: pass\nexcept* Exception: pass').put(None, 0, 1, 'handlers')
                             .handlers.append(FST('except Exception: pass')).base.root.src)

            # put to _ExceptHandlers with plain handlers

            self.assertEqual('except  Exception: pass\nexcept  Exception: pass',
                             FST('except  Exception: pass', '_ExceptHandlers').handlers.append('except  Exception: pass').base.root.src)
            self.assertEqual('except  Exception: pass\nexcept  Exception: pass',
                             FST('except  Exception: pass', '_ExceptHandlers').handlers.append(FST('except  Exception: pass')).base.root.src)
            self.assertRaises(ParseError, FST('except  Exception: pass', '_ExceptHandlers').handlers.append, 'except* Exception: pass')
            self.assertRaises(NodeError, FST('except  Exception: pass', '_ExceptHandlers').handlers.append, FST('except* Exception: pass'))

            # put to _ExceptHandlers with star handlers

            self.assertEqual('except* Exception: pass\nexcept* Exception: pass',
                             FST('except* Exception: pass', '_ExceptHandlers').handlers.append('except* Exception: pass').base.root.src)
            self.assertEqual('except* Exception: pass\nexcept* Exception: pass',
                             FST('except* Exception: pass', '_ExceptHandlers').handlers.append(FST('except* Exception: pass')).base.root.src)
            self.assertRaises(ParseError, FST('except* Exception: pass', '_ExceptHandlers').handlers.append, 'except  Exception: pass')
            self.assertRaises(NodeError, FST('except* Exception: pass', '_ExceptHandlers').handlers.append, FST('except  Exception: pass'))

            # put to empty _ExceptHandlers

            self.assertEqual('except  Exception: pass',
                             FST('', '_ExceptHandlers').handlers.append('except  Exception: pass').base.root.src)
            self.assertEqual('except  Exception: pass',
                             FST('', '_ExceptHandlers').handlers.append(FST('except  Exception: pass')).base.root.src)
            self.assertEqual('except* Exception: pass',
                             FST('', '_ExceptHandlers').handlers.append('except* Exception: pass').base.root.src)
            self.assertEqual('except* Exception: pass',
                             FST('', '_ExceptHandlers').handlers.append(FST('except* Exception: pass')).base.root.src)

    def test__normalize_block(self):
        a = parse('''
if 1: i ; j ; l ; m
            '''.strip())
        a.body[0].f._normalize_block()
        a.f.verify()
        self.assertEqual(a.f.src, 'if 1:\n    i ; j ; l ; m')

        a = parse('''
def f() -> int: \\
  i \\
  ; \\
  j
            '''.strip())
        a.body[0].f._normalize_block()
        a.f.verify()
        self.assertEqual(a.f.src, 'def f() -> int:\n    i \\\n  ; \\\n  j')

        a = parse('''def f(a = """ a
...   # something """): i = 2''')
        a.body[0].f._normalize_block()
        self.assertEqual(a.f.src, 'def f(a = """ a\n...   # something """):\n    i = 2')

    def test__elif_to_else_if(self):
        from fst.slice_stmtish import _elif_to_else_if

        a = parse('''
if 1: pass
elif 2: pass
        '''.strip())
        _elif_to_else_if(a.body[0].orelse[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
        '''.strip())
        _elif_to_else_if(a.body[0].body[0].orelse[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
            '''.strip())

        a = parse('''
if 1: pass
elif 2: pass
return
        '''.strip())
        _elif_to_else_if(a.body[0].orelse[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
return
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
    return
        '''.strip())
        _elif_to_else_if(a.body[0].body[0].orelse[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
    return
            '''.strip())

        a = parse('''
if 1: pass
elif 2: pass
elif 3: pass
        '''.strip())
        _elif_to_else_if(a.body[0].orelse[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, '''
if 1: pass
else:
    if 2: pass
    elif 3: pass
            '''.strip())

        a = parse('''
def f():
    if 1: pass
    elif 2: pass
    elif 3: pass
        '''.strip())
        _elif_to_else_if(a.body[0].body[0].orelse[0].f)
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
        elif 3: pass
            '''.strip())

    def test_unmake_on_put_slice(self):
        s = FST('a', 'exec')
        s0 = s.body[0]
        d = FST('b', 'exec')
        d0 = d.body[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.body[0])
        self.assertIs(s0.a, d.a.body[0])

        s0 = FST('a', 'Expr')
        d = FST('b', 'exec')
        d0 = d.body[0]
        d.put_slice(s0)
        self.assertIsNone(d0.a)
        self.assertIs(s0, d.body[0])
        self.assertIs(s0.a, d.a.body[0])

        s0 = FST('a', 'Name')
        d = FST('b', 'exec')
        d0 = d.body[0]
        d.put_slice(s0)
        self.assertIsNone(d0.a)
        self.assertIs(s0, d.body[0].value)
        self.assertIs(s0.a, d.a.body[0].value)

        s = FST('0,')
        s0 = s.elts[0]
        sc = s.ctx
        d = FST('1,')
        d0 = d.elts[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIsNone(sc.a)
        self.assertIs(s0, d.elts[0])
        self.assertIs(s0.a, d.a.elts[0])

        s = FST('[0]')
        s0 = s.elts[0]
        sc = s.ctx
        d = FST('[1]')
        d0 = d.elts[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIsNone(sc.a)
        self.assertIs(s0, d.elts[0])
        self.assertIs(s0.a, d.a.elts[0])

        s = FST('{0}')
        s0 = s.elts[0]
        d = FST('{1}')
        d0 = d.elts[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.elts[0])
        self.assertIs(s0.a, d.a.elts[0])

        s = FST('{0: 0}')
        sk0 = s.keys[0]
        sv0 = s.values[0]
        d = FST('{1: 0}')
        dk0 = d.keys[0]
        dv0 = d.values[0]
        d.put_slice(s)
        self.assertIsNone(dk0.a)
        self.assertIsNone(dv0.a)
        self.assertIsNone(s.a)
        self.assertIs(sk0, d.keys[0])
        self.assertIs(sk0.a, d.a.keys[0])
        self.assertIs(sv0, d.values[0])
        self.assertIs(sv0.a, d.a.values[0])

        s = FST('a,')
        s0 = s.elts[0]
        sc = s.ctx
        d = FST('del b')
        d0 = d.targets[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIsNone(sc.a)
        self.assertIs(s0, d.targets[0])
        self.assertIs(s0.a, d.a.targets[0])

        s = FST('a =', '_Assign_targets')
        s0 = s.targets[0]
        d = FST('b = c')
        d0 = d.targets[0]
        d.put_slice(s, 'targets')
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.targets[0])
        self.assertIs(s0.a, d.a.targets[0])

        s = FST('a as b', '_withitems')
        s0 = s.items[0]
        d = FST('with c as d: pass')
        d0 = d.items[0]
        d.put_slice(s, 'items')
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.items[0])
        self.assertIs(s0.a, d.a.items[0])

        s = FST('a as b', '_aliases')
        s0 = s.names[0]
        d = FST('import c')
        d0 = d.names[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.names[0])
        self.assertIs(s0.a, d.a.names[0])

        s = FST('a as b', '_aliases')
        s0 = s.names[0]
        d = FST('from c import d')
        d0 = d.names[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.names[0])
        self.assertIs(s0.a, d.a.names[0])

        s = FST('a,')
        sc = s.ctx
        s0 = s.elts[0]
        s0c = s0.ctx
        d = FST('global b')
        d.put_slice(s)
        self.assertIsNone(s.a)
        self.assertIsNone(sc.a)
        self.assertIsNone(s0.a)
        self.assertIsNone(s0c.a)

        s = FST('a,')
        sc = s.ctx
        s0 = s.elts[0]
        s0c = s0.ctx
        d = FST('nonlocal b')
        d.put_slice(s)
        self.assertIsNone(s.a)
        self.assertIsNone(sc.a)
        self.assertIsNone(s0.a)
        self.assertIsNone(s0c.a)

        s = FST('a', '_expr_arglikes')  # is Tuple
        s0 = s.elts[0]
        sc = s.ctx
        d = FST('class cls(b): pass')
        d0 = d.bases[0]
        d.put_slice(s, 'bases')
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIsNone(sc.a)
        self.assertIs(s0, d.bases[0])
        self.assertIs(s0.a, d.a.bases[0])

        s = FST('@a', '_decorator_list')
        s0 = s.decorator_list[0]
        d = FST('@b\nclass cls: pass')
        d0 = d.decorator_list[0]
        d.put_slice(s, 'decorator_list')
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.decorator_list[0])
        self.assertIs(s0.a, d.a.decorator_list[0])

        s = FST('for a in a', '_comprehensions')
        s0 = s.generators[0]
        d = FST('[b for b in b]')
        d0 = d.generators[0]
        d.put_slice(s, 'generators')
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.generators[0])
        self.assertIs(s0.a, d.a.generators[0])

        s = FST('if a', '_comprehension_ifs')
        s0 = s.ifs[0]
        d = FST('for _ in _ if b')
        d0 = d.ifs[0]
        d.put_slice(s, 'ifs')
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.ifs[0])
        self.assertIs(s0.a, d.a.ifs[0])

        s = FST('a and b')
        s0 = s.values[0]
        s1 = s.values[1]
        d = FST('c and d')
        d0 = d.values[0]
        d1 = d.values[0]
        d.put_slice(s, 'values')
        self.assertIsNone(d0.a)
        self.assertIsNone(d1.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.values[0])
        self.assertIs(s0.a, d.a.values[0])
        self.assertIs(s1, d.values[1])
        self.assertIs(s1.a, d.a.values[1])

        s = FST('a < b')
        sl = s.left
        so = s.ops[0]
        sc = s.comparators[0]
        d = FST('c > d')
        dl = d.left
        do = d.ops[0]
        dc = d.comparators[0]
        d.put_slice(s)
        self.assertIsNone(dl.a)
        self.assertIsNone(do.a)
        self.assertIsNone(dc.a)
        self.assertIsNone(s.a)
        self.assertIs(sl, d.left)
        self.assertIs(sl.a, d.a.left)
        self.assertIs(so, d.ops[0])
        self.assertIs(so.a, d.a.ops[0])
        self.assertIs(sc, d.comparators[0])
        self.assertIs(sc.a, d.a.comparators[0])

        s = FST('a', '_expr_arglikes')  # is Tuple
        s0 = s.elts[0]
        sc = s.ctx
        d = FST('call(b)')
        d0 = d.args[0]
        d.put_slice(s, 'args')
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIsNone(sc.a)
        self.assertIs(s0, d.args[0])
        self.assertIs(s0.a, d.a.args[0])

        s = FST('[0]', pattern)
        s0 = s.patterns[0]
        d = FST('[1]', pattern)
        d0 = d.patterns[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.patterns[0])
        self.assertIs(s0.a, d.a.patterns[0])

        s = FST('{0: a}', pattern)
        sk0 = s.keys[0]
        sv0 = s.patterns[0]
        d = FST('{1: b}', pattern)
        dk0 = d.keys[0]
        dv0 = d.patterns[0]
        d.put_slice(s)
        self.assertIsNone(dk0.a)
        self.assertIsNone(dv0.a)
        self.assertIsNone(s.a)
        self.assertIs(sk0, d.keys[0])
        self.assertIs(sk0.a, d.a.keys[0])
        self.assertIs(sv0, d.patterns[0])
        self.assertIs(sv0.a, d.a.patterns[0])

        s = FST('a | b', pattern)
        s0 = s.patterns[0]
        s1 = s.patterns[1]
        d = FST('c | d', pattern)
        d0 = d.patterns[0]
        d1 = d.patterns[1]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(d1.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.patterns[0])
        self.assertIs(s0.a, d.a.patterns[0])
        self.assertIs(s1, d.patterns[1])
        self.assertIs(s1.a, d.a.patterns[1])

        if PYGE12:
            s = FST('T', '_type_params')
            s0 = s.type_params[0]
            d = FST('class cls[T]: pass')
            d0 = d.type_params[0]
            d.put_slice(s, 'type_params')
            self.assertIsNone(d0.a)
            self.assertIsNone(s.a)
            self.assertIs(s0, d.type_params[0])
            self.assertIs(s0.a, d.a.type_params[0])

        s = FST('except a: pass', '_ExceptHandlers')
        s0 = s.handlers[0]
        d = FST('except b: pass', '_ExceptHandlers')
        d0 = d.handlers[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.handlers[0])
        self.assertIs(s0.a, d.a.handlers[0])

        s = FST('case a: pass', '_match_cases')
        s0 = s.cases[0]
        d = FST('case b: pass', '_match_cases')
        d0 = d.cases[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.cases[0])
        self.assertIs(s0.a, d.a.cases[0])

        s = FST('a =', '_Assign_targets')
        s0 = s.targets[0]
        d = FST('b =', '_Assign_targets')
        d0 = d.targets[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.targets[0])
        self.assertIs(s0.a, d.a.targets[0])

        s = FST('@a', '_decorator_list')
        s0 = s.decorator_list[0]
        d = FST('@b', '_decorator_list')
        d0 = d.decorator_list[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.decorator_list[0])
        self.assertIs(s0.a, d.a.decorator_list[0])

        s = FST('for a in a', '_comprehensions')
        s0 = s.generators[0]
        d = FST('for b in b', '_comprehensions')
        d0 = d.generators[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.generators[0])
        self.assertIs(s0.a, d.a.generators[0])

        s = FST('if a', '_comprehension_ifs')
        s0 = s.ifs[0]
        d = FST('if b', '_comprehension_ifs')
        d0 = d.ifs[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.ifs[0])
        self.assertIs(s0.a, d.a.ifs[0])

        s = FST('a as b', '_aliases')
        s0 = s.names[0]
        d = FST('c as d', '_aliases')
        d0 = d.names[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.names[0])
        self.assertIs(s0.a, d.a.names[0])

        s = FST('a as b', '_withitems')
        s0 = s.items[0]
        d = FST('c as d', '_withitems')
        d0 = d.items[0]
        d.put_slice(s)
        self.assertIsNone(d0.a)
        self.assertIsNone(s.a)
        self.assertIs(s0, d.items[0])
        self.assertIs(s0.a, d.a.items[0])

        if PYGE12:
            s = FST('T', '_type_params')
            s0 = s.type_params[0]
            d = FST('U', '_type_params')
            d0 = d.type_params[0]
            d.put_slice(s)
            self.assertIsNone(d0.a)
            self.assertIsNone(s.a)
            self.assertIs(s0, d.type_params[0])
            self.assertIs(s0.a, d.a.type_params[0])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-get-slice', default=False, action='store_true', help="regenerate get slice test data")
    parser.add_argument('--regen-put-slice', default=False, action='store_true', help="regenerate put slice test data")

    args, _ = parser.parse_known_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT12:
            raise RuntimeError('cannot regenerate on python version < 3.12')

    if args.regen_get_slice or args.regen_all:
        print('Regenerating get slice test data...')
        regen_get_slice()

    if args.regen_put_slice or args.regen_all:
        print('Regenerating put slice test data...')
        regen_put_slice()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
