#!/usr/bin/env python

import os
import re
import unittest
from ast import parse as ast_parse

from fst import *

from fst.asttypes import ASTS_STMTISH
from fst.common import PYLT11, PYLT12, PYGE11, PYGE12, PYGE14

from support import GetSliceCases, PutSliceCases


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
        for key, case, rest in DATA_GET_SLICE.iterate(True):
            for idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                self.assertEqual(c, r, f'{key = }, {case.idx = }, rest {idx = }')

    def test_del_slice_from_get_slice_data(self):
        from support import _make_fst

        for key, case, rest in DATA_GET_SLICE.iterate(True):
            f = _make_fst(case.code, case.attr)

            try:
                f.put_slice(None, case.start, case.stop, case.field, **case.options)

            except Exception:
                if not ((r0 := rest[0]).startswith('**') and r0.endswith('**')):
                    raise RuntimeError(f'del raises while cut did not, {key = }, {case.idx = }')

            else:
                if f.root.src != rest[0]:
                    raise RuntimeError(f'del and cut FST src are not identical, {key = }, {case.idx = }\n{f.root.src}\n...\n{rest[0]}')

                if (root_dump := f.root.dump(out=str)) != rest[1]:
                    raise RuntimeError(f'del and cut FST dump are not identical, {key = }, {case.idx = }\n{root_dump}\n...\n{rest[1]}')

    def test_put_slice_from_data(self):
        for key, case, rest in DATA_PUT_SLICE.iterate(True):
            for idx, (c, r) in enumerate(zip(case.rest, rest, strict=True)):
                self.assertEqual(c, r, f'{key = }, {case.idx = }, rest {idx = }')

    def test_put_src_from_put_slice_data(self):  # this test will probably go away at some point
        from fst.fst import _fixup_field_body
        from fst.fst_slice import _loc_slice_raw_put
        from support import _unfmt_code, _make_fst

        for key, case, rest in DATA_PUT_SLICE.iterate(True):
            if not case.options.get('raw') or rest[1].startswith('**'):
                continue

            f        = _make_fst(case.code, case.attr)
            field, _ = _fixup_field_body(f.a, case.field)
            loc      = _loc_slice_raw_put(f, case.start, case.stop, field)
            src      = _unfmt_code(r0 if isinstance(r0 := rest[0], str) else r0[1])

            f.put_src(None if src == '**DEL**' else src, *loc)
            f.root.verify(raise_=True)

            if f.root.src != rest[1]:
                raise RuntimeError(f'put_src and put raw FST src are not identical, {key = }, {case.idx = }\n{f.root.src}\n...\n{rest[1]}')

            if (root_dump := f.root.dump(out=str)) != rest[2]:
                raise RuntimeError(f'put_src and put raw FST dump are not identical, {key = }, {case.idx = }\n{root_dump}\n...\n{rest[2]}')

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
        self.assertEqual('i', a.body[0].f.cut(precomms=False, postcomms=False).src)
        self.assertEqual('# prepre\n\n# pre\n# post\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# pre\ni', a.body[0].f.cut(precomms=True, postcomms=False).src)
        self.assertEqual('# prepre\n\n# post\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# pre\ni # post\n', a.body[0].f.cut(precomms=True, postcomms=True).src)
        self.assertEqual('# prepre\n\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# prepre\n\n# pre\ni', a.body[0].f.cut(precomms='all', postcomms=False).src)
        self.assertEqual('# post\n# postpost', a.f.src)

        a = parse('( ( i ), )')
        f = a.body[0].value.elts[0].f.cut(precomms=False, postcomms=False)
        self.assertEqual('()', a.f.src)
        self.assertEqual('i', f.src)

        a = parse('( ( i ), )')
        f = a.body[0].value.elts[0].f.cut(precomms=False, postcomms=False, pars=True)
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
'''.lstrip())

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
'''.lstrip())

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

        self.assertEqual(a.f.src, '''match a:\n''')

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
'''.lstrip())

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
'''.lstrip())

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

        self.assertEqual(a.f.src, '''match a:\n''')

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
            f = point.get_slice(field=field, cut=True)

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
            '',
            '...',
            'j; k',
            '...',
            'l ; \\',
            'm',
            '...',
            '# pre',
            'n  # post',
            '',
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
            '',
            '...',
            '# pre-classdeco',
            '@classdeco',
            'class cls:',
            '    @methdeco',
            '    def meth(self):',
            '        mvar = 5  # post-meth',
            '',
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
            '',
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
            point.put_slice(None, field=field)#, check_node_type=False)

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
            f = point.get_slice(field=field, cut=True)

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
            '',
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
            '',
            '...',
            '# FOR',
            '# pre-classdeco',
            '@classdeco',
            'class cls:',
            '    @methdeco',
            '    def meth(self):',
            '        mvar = 5  # post-meth',
            '',
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
            '',
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
            point.put_slice(None, field=field)

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
            asts = [a for a in walk(ast) if isinstance(a, ASTS_STMTISH)]

            for a in asts[::-1]:
                a.f.cut()

            ast  = parse(src.strip())
            asts = [a for a in walk(ast) if isinstance(a, ASTS_STMTISH)]

            for a in asts[::-1]:
                field, idx = a.f.pfield

                a.f.parent.put_slice(None, idx, idx + 1, field)

    def test_cut_and_del_slice_matchseq(self):
        f = FST('[a, b, c]', pattern)
        self.assertEqual('[c]', f.get_slice(2, None, cut=True).src)
        self.assertEqual('[a, b]', f.src)
        self.assertEqual('[b]', f.get_slice(1, None, cut=True).src)
        self.assertEqual('[a]', f.src)
        self.assertEqual('[a]', f.get_slice(0, None, cut=True).src)
        self.assertEqual('[]', f.src)

        f = FST('(a, b, c)', pattern)
        self.assertEqual('(c,)', f.get_slice(2, None, cut=True).src)
        self.assertEqual('(a, b)', f.src)
        self.assertEqual('(b,)', f.get_slice(1, None, cut=True).src)
        self.assertEqual('(a,)', f.src)
        self.assertEqual('(a,)', f.get_slice(0, None, cut=True).src)
        self.assertEqual('()', f.src)

        f = FST('a, b, c', pattern)
        self.assertEqual('c,', f.get_slice(2, None, cut=True).src)
        self.assertEqual('a, b', f.src)
        self.assertEqual('b,', f.get_slice(1, None, cut=True).src)
        self.assertEqual('a,', f.src)
        self.assertEqual('a,', f.get_slice(0, None, cut=True).src)
        self.assertEqual('[]', f.src)

        f = FST('[a, b, c]', pattern)
        f.put_slice(None, 2, None)
        self.assertEqual('[a, b]', f.src)
        f.put_slice(None, 1, None)
        self.assertEqual('[a]', f.src)
        f.put_slice(None, 0, None)
        self.assertEqual('[]', f.src)

        f = FST('(a, b, c)', pattern)
        f.put_slice(None, 2, None)
        self.assertEqual('(a, b)', f.src)
        f.put_slice(None, 1, None)
        self.assertEqual('(a,)', f.src)
        f.put_slice(None, 0, None)
        self.assertEqual('()', f.src)

        f = FST('a, b, c', pattern)
        f.put_slice(None, 2, None)
        self.assertEqual('a, b', f.src)
        f.put_slice(None, 1, None)
        self.assertEqual('a,', f.src)
        f.put_slice(None, 0, None)
        self.assertEqual('[]', f.src)

        f = FST('a, b, c', pattern)
        f.put_slice(None, None, 1)
        self.assertEqual('b, c', f.src)
        f.put_slice(None, None, 1)
        self.assertEqual('c,', f.src)
        f.put_slice(None, None, 1)
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
        f = FST('del a, b, c')
        self.assertRaises(ValueError, f.get_slice, cut=True)

        f = FST('del a, b, c')
        self.assertRaises(ValueError, f.put_slice, None)

        f = FST('del a, b, c')
        self.assertEqual('a, b, c', f.get_slice(cut=True, fix_delete_self=False).src)
        self.assertEqual('del ', f.src)
        f.put_slice('x, y, z')
        self.assertEqual('del x, y, z', f.src)

        f = FST('del a, b, c')
        self.assertEqual('del ', f.put_slice(None, fix_delete_self=False).src)
        f.put_slice('x, y, z')
        self.assertEqual('del x, y, z', f.src)

    def test_cut_and_del_slice_assign(self):
        f = FST('a = b = c = q')
        self.assertRaises(ValueError, f.get_slice, 'targets', cut=True)

        f = FST('a = b = c = q')
        self.assertRaises(ValueError, f.put_slice, None, 'targets')

        f = FST('a = b = c = q')
        self.assertEqual('a = b = c =', f.get_slice('targets', cut=True, fix_assign_self=False).src)
        self.assertEqual(' q', f.src)
        f.put_slice('x = y = z', 'targets')
        self.assertEqual('x = y = z = q', f.src)

        f = FST('a = b = c = q')
        self.assertEqual(' q', f.put_slice(None, 'targets', fix_assign_self=False).src)
        f.put_slice('x = y = z =', 'targets')
        self.assertEqual('x = y = z = q', f.src)

    def test_cut_and_del_slice_import(self):
        f = FST('import a, b, c')
        self.assertRaises(ValueError, f.get_slice, cut=True)

        f = FST('import a, b, c')
        self.assertRaises(ValueError, f.put_slice, None)

        f = FST('import a, b, c')
        self.assertEqual('a, b, c', f.get_slice(cut=True, fix_import_self=False).src)
        self.assertEqual('import ', f.src)
        f.put_slice('x, y, z')
        self.assertEqual('import x, y, z', f.src)

        f = FST('import a, b, c')
        self.assertEqual('import ', f.put_slice(None, fix_import_self=False).src)
        f.put_slice('x, y, z')
        self.assertEqual('import x, y, z', f.src)

    def test_cut_and_del_slice_global_and_nonlocal(self):
        # global

        f = FST('global a, b, c')
        self.assertRaises(ValueError, f.get_slice, cut=True)

        f = FST('global a, b, c')
        self.assertRaises(ValueError, f.put_slice, None)

        f = FST('global a, b, c')
        self.assertEqual('a, b, c', f.get_slice(cut=True, fix_global_self=False).src)
        self.assertEqual('global ', f.src)
        f.put_slice('x, y, z')
        self.assertEqual('global x, y, z', f.src)

        f = FST('global a, b, c')
        self.assertEqual('global ', f.put_slice(None, fix_global_self=False).src)
        f.put_slice('x, y, z')
        self.assertEqual('global x, y, z', f.src)

        # nonlocal

        f = FST('nonlocal a, b, c')
        self.assertRaises(ValueError, f.get_slice, cut=True)

        f = FST('nonlocal a, b, c')
        self.assertRaises(ValueError, f.put_slice, None)

        f = FST('nonlocal a, b, c')
        self.assertEqual('a, b, c', f.get_slice(cut=True, fix_global_self=False).src)
        self.assertEqual('nonlocal ', f.src)
        f.put_slice('x, y, z')
        self.assertEqual('nonlocal x, y, z', f.src)

        f = FST('nonlocal a, b, c')
        self.assertEqual('nonlocal ', f.put_slice(None, fix_global_self=False).src)
        f.put_slice('x, y, z')
        self.assertEqual('nonlocal x, y, z', f.src)

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
        g = f.pattern.get_slice(cut=True, fix_matchor_self=False)
        f.pattern.put_slice(g)
        self.assertEqual('case a | b: pass', f.src)
        f.verify()

        f = FST('a | b', pattern)
        g = f.get_slice(cut=True, fix_matchor_self=False)
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

        f = FST('(1, 2)')
        self.assertRaises(NodeError, f.put_slice, FST('x:y:z,', 'expr_slice'))

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

        self.assertEqual('case b | 2: pass', (f := FST('case"a" | 2: pass')).pattern.put_slice('b', 0, 1).root.src)
        f.verify()

        self.assertEqual('case 1 | c as b: pass', (f := FST('case 1 | "a"as b: pass')).pattern.pattern.put_slice('c', 1, 2).root.src)
        f.verify()

        if PYGE11:
            # lone starred slice without comma being put as 'one'

            self.assertEqual('(*a,),', (f := FST('1, 2, 3')).put_slice(FST('*a', 'expr_slice'), one=True).src)
            f.verify()

        if PYGE12:
            # put single type_param as 'one' to tuple_params slice

            self.assertEqual('Z, **V', (f := FST('T, *U, **V', 'type_params').put_slice('Z', 0, 2)).src)
            f.verify()

        # putting invalid MatchOr slice

        self.assertRaises(NodeError, FST('[x, y, z]', pattern).put, FST('a | b', pattern).get_slice(2, fix_matchor_get=False), 0)  # length 0

        self.assertEqual('[b, y, z]', (f := FST('[x, y, z]', pattern)).put(FST('a | b', pattern).get_slice(1, fix_matchor_get=False), 0).src)  # length 1
        f.verify()

        # del

        self.assertRaises(NodeError, FST('del a, b, c').put, '*(),', 1, 2, fix_set_put=False)
        self.assertRaises(NodeError, FST('del a, b, c').put, '*()', 1, 2, fix_set_put=False)

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

        self.assertRaises(NodeError, FST('import a, b, c').put, FST('*', 'ImportFrom_names'), 1, 2)

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

        self.assertEqual('with b: pass', (f := FST('with(a): pass')).put_slice(None, 0, 1, 'items', fix_with_self=False).put_slice('b', 0, 1, 'items').src)
        f.verify()
        self.assertEqual('async with b: pass', (f := FST('async with(a): pass')).put_slice(None, 0, 1, 'items', fix_with_self=False).put_slice('b', 0, 1, 'items').src)
        f.verify()

        # withitem dynamic location calculation in put slice

        self.assertEqual('with (z), (c): pass', (f := FST('with a, \\\nb, (c): pass')).put_slice('(z)', 0, 2, 'items').src)
        f.verify()

        self.assertEqual('(z), (c)', (f := FST('a, \\\nb, (c)', 'withitems')).put_slice('(z)', 0, 2, 'items').src)
        f.verify()

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

        self.assertRaises(NodeError, FST('del a, b').put_slice, FST('z'))
        self.assertRaises(NodeError, FST('del a, b').put_slice, FST('z').a)

    def test_put_slice_raw(self):
        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.put_slice('for x in y', 1, 2, raw=True)
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

        # as one so dont strip delimiters or add to unparenthesized tuple
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

    def test_slice_set_empty(self):
        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, fix_set_put=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, fix_set_put=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, fix_set_put=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, fix_set_put=True).src)

        self.assertRaises(NodeError, FST('[1, 2]').put_slice, 'set()', raw=False, fix_set_put='star')
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, fix_set_put='star').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, fix_set_put='star').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, fix_set_put='star').src)

        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, fix_set_put='call').src)
        self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, fix_set_put='call').src)
        self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, fix_set_put='call').src)
        self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, fix_set_put='call').src)

        self.assertRaises(NodeError, FST('[1, 2]').put_slice, 'set()', raw=False, fix_set_put=False)
        self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, fix_set_put=False).src)
        self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, fix_set_put=False).src)
        self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, fix_set_put=False).src)

        set_ = FST('{1}')

        self.assertEqual('{*()}', set_.get(0, 0, fix_set_get=True).src)
        self.assertEqual('{*()}', set_.get(0, 0, fix_set_get='star').src)
        self.assertEqual('set()', set_.get(0, 0, fix_set_get='call').src)
        self.assertEqual('()', set_.get(0, 0, fix_set_get='tuple').src)
        self.assertEqual('{}', set_.get(0, 0, fix_set_get=False).src)

        self.assertEqual(('{1}', '{*()}'), ((f := FST('{1}')).get_slice(cut=True, fix_set_self=True).src, f.src))
        self.assertEqual(('{1}', '{*()}'), ((f := FST('{1}')).get_slice(cut=True, fix_set_self='star').src, f.src))
        self.assertEqual(('{1}', '{}'), ((f := FST('{1}')).get_slice(cut=True, fix_set_self=False).src, f.src))
        self.assertEqual(('{1}', 'set()'), ((f := FST('{1}')).get_slice(cut=True, fix_set_self='call').src, f.src))

        self.assertEqual('{*()}', FST('{1}').put_slice(None, fix_set_self=True).src)
        self.assertEqual('{*()}', FST('{1}').put_slice(None, fix_set_self='star').src)
        self.assertEqual('{}', FST('{1}').put_slice(None, fix_set_self=False).src)
        self.assertEqual('set()', FST('{1}').put_slice(None, fix_set_self='call').src)

        # f = parse('set()').body[0].value.f
        # self.assertEqual('{*()}', f.get_slice(0, 0, cut=True).src)
        # self.assertEqual('set()', f.src)
        # self.assertEqual('set()', f.put_slice('{*()}', 0, 0).src)
        # f.root.verify()

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

        # put as one

        self.assertEqual('[1, {*()}, 2]', (f := FST('[1, 2]')).put_slice(FST._new_empty_set_curlies(), 1, 1, one=True).src)
        f.verify()

        self.assertEqual('[1, set(), 2]', (f := FST('[1, 2]')).put_slice(FST._new_empty_set_curlies(), 1, 1, one=True, fix_set_self='call').src)
        f.verify()

        self.assertEqual('[1, {}, 2]', (f := FST('[1, 2]')).put_slice(FST._new_empty_set_curlies(), 1, 1, one=True, fix_set_self=False).src)
        self.assertIsNone(f.verify(raise_=False))

    def test_slice_matchor_empty_or_len1(self):
        self.assertEqual('', FST('a | b', pattern).get_slice(0, 0, fix_matchor_get=False).src)
        self.assertRaises(ValueError, FST('a | b', pattern).get_slice, 0, 0, fix_matchor_get=True)
        self.assertRaises(ValueError, FST('a | b', pattern).get_slice, 0, 0, fix_matchor_get='strict')

        self.assertEqual('a', FST('a | b', pattern).get_slice(0, 1, fix_matchor_get=False).src)
        self.assertEqual('a', FST('a | b', pattern).get_slice(0, 1, fix_matchor_get=True).src)
        self.assertRaises(ValueError, FST('a | b', pattern).get_slice, 0, 1, fix_matchor_get='strict')

        self.assertEqual('a | b', FST('a | b', pattern).get_slice(0, 2, fix_matchor_get=False).src)
        self.assertEqual('a | b', FST('a | b', pattern).get_slice(0, 2, fix_matchor_get=True).src)
        self.assertEqual('a | b', FST('a | b', pattern).get_slice(0, 2, fix_matchor_get='strict').src)

        len0mo = FST('c | d', pattern).get_slice(0, 0, fix_matchor_get=False)
        len1mo = FST('c | d', pattern).get_slice(0, 1, fix_matchor_get=False)
        len2mo = FST('c | d', pattern)

        self.assertEqual('a | b', FST('a | b', pattern).put_slice(None, 2, 2, fix_matchor_put=False).src)
        self.assertEqual('a | b', FST('a | b', pattern).put_slice(None, 2, 2, fix_matchor_put=True).src)

        self.assertEqual('a | b', FST('a | b', pattern).put_slice('', 2, 2, fix_matchor_put=False).src)
        self.assertEqual('a | b', FST('a | b', pattern).put_slice('', 2, 2, fix_matchor_put=True).src)

        self.assertEqual('a | b', FST('a | b', pattern).put_slice(len0mo.copy(), 2, 2, fix_matchor_put=False).src)
        self.assertEqual('a | b', FST('a | b', pattern).put_slice(len0mo.copy(), 2, 2, fix_matchor_put=True).src)

        self.assertEqual('a | b | c', FST('a | b', pattern).put_slice(len1mo.copy(), 2, 2, fix_matchor_put=False).src)
        self.assertEqual('a | b | c', FST('a | b', pattern).put_slice(len1mo.copy(), 2, 2, fix_matchor_put=True).src)

        self.assertEqual('a | b | c | d', FST('a | b', pattern).put_slice(len2mo.copy(), 2, 2, fix_matchor_put=False).src)
        self.assertEqual('a | b | c | d', FST('a | b', pattern).put_slice(len2mo.copy(), 2, 2, fix_matchor_put=True).src)

        self.assertEqual('a | b', FST('a | b', pattern).put_slice(len0mo.copy(), 2, 2, one=True, fix_matchor_put=False).src)
        self.assertEqual('a | b', FST('a | b', pattern).put_slice(len0mo.copy(), 2, 2, one=True, fix_matchor_put=True).src)

        self.assertEqual('a | b | c', FST('a | b', pattern).put_slice(len1mo.copy(), 2, 2, one=True, fix_matchor_put=False).src)
        self.assertEqual('a | b | c', FST('a | b', pattern).put_slice(len1mo.copy(), 2, 2, one=True, fix_matchor_put=True).src)

        self.assertEqual('a | b | (c | d)', FST('a | b', pattern).put_slice(len2mo.copy(), 2, 2, one=True, fix_matchor_put=False).src)
        self.assertEqual('a | b | (c | d)', FST('a | b', pattern).put_slice(len2mo.copy(), 2, 2, one=True, fix_matchor_put=True).src)

        self.assertEqual('a | y', FST('a | b | x | y', pattern).put_slice(len0mo.copy(), 1, 3, one=True, fix_matchor_put=False).src)
        self.assertEqual('a | y', FST('a | b | x | y', pattern).put_slice(len0mo.copy(), 1, 3, one=True, fix_matchor_put=True).src)

        self.assertEqual('a | c | y', FST('a | b | x | y', pattern).put_slice(len1mo.copy(), 1, 3, one=True, fix_matchor_put=False).src)
        self.assertEqual('a | c | y', FST('a | b | x | y', pattern).put_slice(len1mo.copy(), 1, 3, one=True, fix_matchor_put=True).src)

        with FST.options(fix_matchor_get=False):
            (f := FST('a | b', pattern)).get_slice(0, 0, cut=True, fix_matchor_self=False)
            self.assertEqual('a | b', f.src)
            self.assertIsInstance(f.a, MatchOr)

            (f := FST('a | b', pattern)).get_slice(0, 0, cut=True, fix_matchor_self=True)
            self.assertEqual('a | b', f.src)
            self.assertIsInstance(f.a, MatchOr)

            (f := FST('a | b', pattern)).get_slice(0, 0, cut=True, fix_matchor_self='strict')
            self.assertEqual('a | b', f.src)
            self.assertIsInstance(f.a, MatchOr)

            (f := FST('a | b', pattern)).get_slice(0, 1, cut=True, fix_matchor_self=False)
            self.assertEqual('b', f.src)
            self.assertIsInstance(f.a, MatchOr)

            (f := FST('a | b', pattern)).get_slice(0, 1, cut=True, fix_matchor_self=True)
            self.assertEqual('b', f.src)
            self.assertIsInstance(f.a, MatchAs)

            self.assertRaises(ValueError, (f := FST('a | b', pattern)).get_slice, 0, 1, cut=True, fix_matchor_self='strict')

            (f := FST('a | b', pattern)).get_slice(0, 2, cut=True, fix_matchor_self=False)
            self.assertEqual('', f.src)
            self.assertIsInstance(f.a, MatchOr)

            self.assertRaises(ValueError, (f := FST('a | b', pattern)).get_slice, 0, 2, cut=True, fix_matchor_self=True)
            self.assertRaises(ValueError, (f := FST('a | b', pattern)).get_slice, 0, 2, cut=True, fix_matchor_self='strict')

            (f := FST('a | b', pattern)).put_slice(None, 0, 0, fix_matchor_self=False)
            self.assertEqual('a | b', f.src)
            self.assertIsInstance(f.a, MatchOr)

            (f := FST('a | b', pattern)).put_slice(None, 0, 0, fix_matchor_self=True)
            self.assertEqual('a | b', f.src)
            self.assertIsInstance(f.a, MatchOr)

            (f := FST('a | b', pattern)).put_slice(None, 0, 0, fix_matchor_self='strict')
            self.assertEqual('a | b', f.src)
            self.assertIsInstance(f.a, MatchOr)

            (f := FST('a | b', pattern)).put_slice(None, 0, 1, fix_matchor_self=False)
            self.assertEqual('b', f.src)
            self.assertIsInstance(f.a, MatchOr)

            (f := FST('a | b', pattern)).put_slice(None, 0, 1, fix_matchor_self=True)
            self.assertEqual('b', f.src)
            self.assertIsInstance(f.a, MatchAs)

            self.assertRaises(ValueError, (f := FST('a | b', pattern)).put_slice, None, 0, 1, fix_matchor_self='strict')

            (f := FST('a | b', pattern)).put_slice(None, 0, 2, fix_matchor_self=False)
            self.assertEqual('', f.src)
            self.assertIsInstance(f.a, MatchOr)

            self.assertRaises(ValueError, (f := FST('a | b', pattern)).put_slice, None, 0, 2, fix_matchor_self=True)
            self.assertRaises(ValueError, (f := FST('a | b', pattern)).put_slice, None, 0, 2, fix_matchor_self='strict')

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

        s = FST('x =\\\ny', 'Assign_targets')
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

    def test_get_and_put_slice_from_to_slice(self):
        # stmts

        self.assertEqual('a', g := (f := FST('a\nb\nc').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('a\nb\na\n', f.put_slice(g, 'end').src)
        f.verify()

        # ExceptHandlers

        self.assertEqual('except a: pass', g := (f := FST('except a: pass\nexcept b: pass\nexcept c: pass').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('except a: pass\nexcept b: pass\nexcept a: pass\n', f.put_slice(g, 'end').src)
        f.verify()

        # match_cases

        self.assertEqual('case a: pass', g := (f := FST('case a: pass\ncase b: pass\ncase c: pass').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('case a: pass\ncase b: pass\ncase a: pass\n', f.put_slice(g, 'end').src)
        f.verify()

        # Assign

        self.assertEqual('a =', g := (f := FST('a = b = c = z').get_slice(0, 2, 'targets')).get_slice(0, 1).src)
        self.assertEqual('a = b = a =', f.put_slice(g, 'end', 'targets').src)
        f.verify()

        # Import

        self.assertEqual('a', g := (f := FST('import a, b, c').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('a, b, a', f.put_slice(g, 'end').src)
        f.verify()

        # Tuple (unparenthesized)

        self.assertEqual('a,', g := (f := FST('a, b, c').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('a, b, a', f.put_slice(g, 'end').src)
        f.verify()

        # Tuple (parenthesized)

        self.assertEqual('(a,)', g := (f := FST('(a, b, c)').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('(a, b, a)', f.put_slice(g, 'end').src)
        f.verify()

        # List

        self.assertEqual('[a]', g := (f := FST('[a, b, c]').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('[a, b, a]', f.put_slice(g, 'end').src)
        f.verify()

        # Set

        self.assertEqual('{a}', g := (f := FST('{a, b, c}').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('{a, b, a}', f.put_slice(g, 'end').src)
        f.verify()

        # Dict

        self.assertEqual('{1:a}', g := (f := FST('{1:a, 2:b, 3:c}').get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('{1:a, 2:b, 1:a}', f.put_slice(g, 'end').src)
        f.verify()

        # MatchSequence

        self.assertEqual('[a]', g := (f := FST('[a, b, c]', pattern).get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('[a, b, a]', f.put_slice(g, 'end').src)
        f.verify()

        # MatchMapping

        self.assertEqual('{1:a}', g := (f := FST('{1:a, 2:b, 3:c}', pattern).get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('{1:a, 2:b, 1:a}', f.put_slice(g, 'end').src)
        f.verify()

        # MatchOr

        self.assertEqual('a', g := (f := FST('a | b | c', pattern).get_slice(0, 2)).get_slice(0, 1).src)
        self.assertEqual('a | b | a', f.put_slice(g, 'end').src)
        f.verify()

        if PYGE12:
            # type_params

            self.assertEqual('T', g := (f := FST('def f[T, *U, **V](): pass').get_slice(0, 2, 'type_params')).get_slice(0, 1).src)
            self.assertEqual('T, *U, T', f.put_slice(g, 'end').src)
            f.verify()

            self.assertEqual('T', g := (f := FST('async def f[T, *U, **V](): pass').get_slice(0, 2, 'type_params')).get_slice(0, 1).src)
            self.assertEqual('T, *U, T', f.put_slice(g, 'end').src)
            f.verify()

            self.assertEqual('T', g := (f := FST('class cls[T, *U, **V]: pass').get_slice(0, 2, 'type_params')).get_slice(0, 1).src)
            self.assertEqual('T, *U, T', f.put_slice(g, 'end').src)
            f.verify()

            self.assertEqual('T', g := (f := FST('type t[T, *U, **V] = ...').get_slice(0, 2, 'type_params')).get_slice(0, 1).src)
            self.assertEqual('T, *U, T', f.put_slice(g, 'end').src)
            f.verify()

    def test_invalid_AST_slice_usage_errors(self):
        # invalid-AST Tuple slice

        # TODO: with other invalid slices, e.g. Tuple[withitem]

        if PYGE12:
            self.assertRaises(NodeError, FST('a = b').put, FST('T, **U', 'type_params'), 'value')  # expr
            self.assertRaises(NodeError, FST('a = b').put, FST('T, **U', 'type_params').a, 'value')

            self.assertRaises(NodeError, FST('f(a)').put, FST('T, **U', 'type_params'), 0, 'args')  # expr_arglike
            self.assertRaises(NodeError, FST('f(a)').put, FST('T, **U', 'type_params').a, 0, 'args')

            self.assertRaises(NodeError, FST('a[b]').put, FST('T, **U', 'type_params'), 'slice')  # expr_slice
            self.assertRaises(NodeError, FST('a[b]').put, FST('T, **U', 'type_params').a, 'slice')

            self.assertRaises(NodeError, FST('a[b, c]').slice.put, FST('T, **U', 'type_params'), 0, 'elts')  # expr_sliceelt
            self.assertRaises(NodeError, FST('a[b, c]').slice.put, FST('T, **U', 'type_params').a, 0, 'elts')

            self.assertRaises(NodeError, FST('(b, c)').put, FST('T, **U', 'type_params'), 0, 'elts')  # expr_sliceelt
            self.assertRaises(NodeError, FST('(b, c)').put, FST('T, **U', 'type_params').a, 0, 'elts')


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
