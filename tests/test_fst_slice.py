#!/usr/bin/env python

import os
import sys
import unittest

from fst import *

from fst.misc import PYLT12, PYGE14

from data_other import (
    GET_SLICE_EXPRISH_DATA, GET_SLICE_STMTISH_DATA,
    PUT_SLICE_EXPRISH_DATA, PUT_SLICE_STMTISH_DATA, PUT_SLICE_DATA,
)


def read(fnm):
    with open(fnm) as f:
        return f.read()


def regen_get_slice_seq():
    newlines = []

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    for name in ('GET_SLICE_EXPRISH_DATA',):
        for i, (src, elt, start, stop, options, *_) in enumerate(globals()[name]):
            try:
                t     = parse(src)
                f     = eval(f't.{elt}', {'t': t}).f
                s     = f.get_slice(start, stop, cut=True, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                tdump = t.f.dump(out=list)
                sdump = s.dump(out=list)

                assert not tsrc.startswith('\n') or tsrc.endswith('\n')
                assert not ssrc.startswith('\n') or ssrc.endswith('\n')

                if options.get('_verify', True):
                    t.f.verify(raise_=True)
                    s.verify(raise_=True)

                newlines.extend(f'''(r"""{src}""", {elt!r}, {start}, {stop}, {options}, r"""\n{tsrc}\n""", r"""\n{ssrc}\n""", r"""'''.split('\n'))
                newlines.extend(tdump)
                newlines.append('""", r"""')
                newlines.extend(sdump)
                newlines.append('"""),\n')

            except Exception:
                print(i, elt, start, stop, options)
                print('...')
                print(src)
                print('...')
                print(tsrc)
                print('...')
                print(ssrc)

                raise

        start = lines.index(f'{name} = [')
        stop  = lines.index(f']  # END OF {name}')

        lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_get_slice_stmt():
    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    newlines = []

    for src, elt, start, stop, field, options, *_ in GET_SLICE_STMTISH_DATA:
        t     = parse(src)
        f     = (eval(f't.{elt}', {'t': t}) if elt else t).f
        s     = f.get_slice(start, stop, field, cut=True, **options)
        tsrc  = t.f.src
        ssrc  = s.src
        tdump = t.f.dump(out=list)
        sdump = s.dump(out=list)

        if options.get('_verify', True):
            t.f.verify(raise_=True)
            s.verify(raise_=True)

        newlines.extend(f'''(r"""{src}""", {elt!r}, {start}, {stop}, {field!r}, {options}, r"""{tsrc}""", r"""{ssrc}""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('""", r"""')
        newlines.extend(sdump)
        newlines.append('"""),\n')

    start = lines.index(f'GET_SLICE_STMTISH_DATA = [')
    stop  = lines.index(f']  # END OF GET_SLICE_STMTISH_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_seq():
    newlines = []

    try:
        for i, (dst, elt, start, stop, src, put_src, put_dump) in enumerate(PUT_SLICE_EXPRISH_DATA):
            t = parse(dst)
            f = eval(f't.{elt}', {'t': t}).f

            f.put_slice(None if src == '**DEL**' else src, start, stop)

            tdst  = t.f.src
            tdump = t.f.dump(out=list)

            assert not tdst.startswith('\n') or tdst.endswith('\n')

            t.f.verify(raise_=True)

            newlines.extend(f'''(r"""{dst}""", {elt!r}, {start}, {stop}, r"""{src}""", r"""\n{tdst}\n""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('"""),\n')

    except Exception:
        print(i, elt, start, stop)
        print('...')
        print(dst)
        print('...')
        print(src)
        print('...')
        print(put_src)
        print('...')
        print(t.f.src)

        raise

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_EXPRISH_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_EXPRISH_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_stmt():
    newlines = []

    for dst, stmt, start, stop, field, options, src, put_src, put_dump in PUT_SLICE_STMTISH_DATA:
        t = parse(dst)
        f = (eval(f't.{stmt}', {'t': t}) if stmt else t).f

        f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

        tdst  = t.f.src
        tdump = t.f.dump(out=list)

        t.f.verify(raise_=True)

        newlines.extend(f'''(r"""{dst}""", {stmt!r}, {start}, {stop}, {field!r}, {options!r}, r"""{src}""", r"""{tdst}""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_STMTISH_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_STMTISH_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice():
    newlines = []

    for i, (dst, attr, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_DATA):
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            try:
                f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

            except NotImplementedError as exc:
                tdst  = f'**{exc!r}**'
                tdump = ''

            else:
                tdst  = t.f.src
                tdump = t.f.dump(out=list)

                t.f.verify(raise_=True)

        except Exception:
            print(i, attr, start, stop, field, options)
            print(dst)
            print('...')
            print(src)
            print('...')
            print('\n'.join(repr(l) for l in t.f.lines))

            raise

        newlines.extend(f'''(r"""{dst}""", {attr!r}, {start}, {stop}, {field!r}, {options!r}, r"""{src}""", r"""{tdst}""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


class TestFSTSlice(unittest.TestCase):
    def test_cut_special(self):  # TODO: redo in a better way
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

    def test_cut_and_del_special(self):  # TODO: redo in a better way
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

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

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

        self.assertEqual(lines, [
            'i = 1',
            '...',
            'pass',
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
            ''
        ])

        fst = fst2

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

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

        for point, field in points:
            point.put_slice(None, field=field, check_node_type=False)

        self.assertEqual(fst.lines, [
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
            ''
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

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

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

        self.assertEqual(lines, [
            '# CASE',
            'i = 1',
            '...',
            'pass',
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
            'except:  \\',
            '  # EXCEPT',
            '    if 1: break',
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
            'except:  \\',
            '# EXCEPT',
            '    aa or bb or cc',
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
            'match b:',
            '',
            'if 1:',
            '',
            'try:',
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
            ''
        ])

        fst = fst2

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

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

        for point, field in points:
            point.put_slice(None, field=field)

        self.assertEqual(fst.lines, [
            'match a:',
            '    case 1:',
            '',
            'match b:',
            '',
            'if 1:',
            '',
            'try:',
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
            ''
        ])

    def test_cut_block_everything(self):  # TODO: redo in a better way
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
            asts = [a for a in walk(ast) if isinstance(a, fst.STMTISH)]

            for a in asts[::-1]:
                a.f.cut()

            ast  = parse(src.strip())
            asts = [a for a in walk(ast) if isinstance(a, fst.STMTISH)]

            for a in asts[::-1]:
                field, idx = a.f.pfield

                a.f.parent.put_slice(None, idx, idx + 1, field)

    def test_cut_slice_matchseq(self):
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

    def test_del_slice_matchseq(self):
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

    def test_get_slice_seq_copy(self):
        for i, (src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump) in enumerate(GET_SLICE_EXPRISH_DATA):
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                s     = f.get_slice(start, stop, cut=False, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                sdump = s.dump(out=list)

                self.assertEqual(tsrc, src.strip())
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print('copy:', i, elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_get_slice_seq_cut(self):
        for i, (src, elt, start, stop, options, src_cut, slice_copy, src_cut_dump, slice_dump) in enumerate(GET_SLICE_EXPRISH_DATA):
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                s     = f.get_slice(start, stop, cut=True, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                t.f._touchall()
                tdump = t.f.dump(out=list)
                sdump = s.dump(out=list)

                self.assertEqual(tsrc, src_cut.strip())
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(tdump, src_cut_dump.strip().split('\n'))
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print('cut:', i, elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(src_cut)
                print('...')
                print(slice_copy)

                print('='*80)
                print('\n'.join(tdump))
                print('-'*80)
                print('\n'.join(src_cut_dump.strip().split('\n')))
                print('.'*80)

                raise

    def test_get_slice_stmt_copy(self):
        for src, elt, start, stop, field, options, _, slice_cut, _, slice_dump in GET_SLICE_STMTISH_DATA:
            t = parse(src)
            f = (eval(f't.{elt}', {'t': t}) if elt else t).f

            try:
                s     = f.get_slice(start, stop, field, cut=False, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                sdump = s.dump(out=list)

                if options.get('_verify', True):
                    t.f.verify(raise_=True)
                    s.verify(raise_=True)

                self.assertEqual(tsrc, src)
                self.assertEqual(ssrc, slice_cut)
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(slice_cut)

                raise

    def test_get_slice_stmt_cut(self):
        for src, elt, start, stop, field, options, src_cut, slice_cut, src_dump, slice_dump in GET_SLICE_STMTISH_DATA:
            t = parse(src)
            f = (eval(f't.{elt}', {'t': t}) if elt else t).f

            try:
                s     = f.get_slice(start, stop, field, cut=True, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                tdump = t.f.dump(out=list)
                sdump = s.dump(out=list)

                if options.get('_verify', True):
                    t.f.verify(raise_=True)
                    s.verify(raise_=True)

                self.assertEqual(tsrc, src_cut)
                self.assertEqual(ssrc, slice_cut)
                self.assertEqual(tdump, src_dump.strip().split('\n'))
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(src_cut)
                print('...')
                print(slice_cut)

                raise

    def test_put_slice_seq_from_get_slice_data(self):
        for i, (src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump) in enumerate(GET_SLICE_EXPRISH_DATA):
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                f.put_slice(None, start, stop, **options)

                tdst  = t.f.src
                tdump = t.f.dump(out=list)

                self.assertEqual(tdst, src_cut.strip())
                self.assertEqual(tdump, src_dump.strip().split('\n'))

            except Exception:
                print(i, elt, start, stop)
                print('---')
                print(src)

                raise

    def test_put_slice_seq(self):
        for i, (dst, elt, start, stop, src, put_src, put_dump) in enumerate(PUT_SLICE_EXPRISH_DATA):
            t = parse(dst)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                f.put_slice(None if src == '**DEL**' else src, start, stop)

                tdst  = t.f.src
                tdump = t.f.dump(out=list)

                self.assertEqual(tdst, put_src.strip())
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, elt, start, stop)
                print('---')
                print(dst)
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_slice_stmt_del(self):
        for src, elt, start, stop, field, options, src_cut, _, src_dump, _ in GET_SLICE_STMTISH_DATA:
            t = parse(src)
            f = (eval(f't.{elt}', {'t': t}) if elt else t).f

            try:
                f.put_slice(None, start, stop, field, **options)

                tsrc  = t.f.src
                tdump = t.f.dump(out=list)

                if options.get('_verify', True):
                    t.f.verify(raise_=True)

                self.assertEqual(tsrc, src_cut)
                self.assertEqual(tdump, src_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(src_cut)

                raise

    def test_put_slice_stmt(self):
        for i, (dst, stmt, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_STMTISH_DATA):
            t = parse(dst)
            f = (eval(f't.{stmt}', {'t': t}) if stmt else t).f

            try:
                f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

                tdst  = t.f.src
                tdump = t.f.dump(out=list)

                t.f.verify(raise_=True)

                self.assertEqual(tdst, put_src)
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, stmt, start, stop, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_slice(self):
        for i, (dst, attr, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

                tdst  = t.f.src
                tdump = t.f.dump(out=list)

                t.f.verify(raise_=True)

                self.assertEqual(tdst, put_src)
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, src, start, stop, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

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

    def test_put_slice_empty_set(self):
        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, empty_set_put=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set_put=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set_put=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set_put=True).src)

        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, empty_set_put='both').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set_put='both').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set_put='both').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set_put='both').src)

        self.assertRaises(ValueError, FST('[1, 2]').put_slice, 'set()', raw=False, empty_set_put='star')
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set_put='star').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set_put='star').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set_put='star').src)

        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, empty_set_put='call').src)
        self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set_put='call').src)
        self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set_put='call').src)
        self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set_put='call').src)

        self.assertRaises(ValueError, FST('[1, 2]').put_slice, 'set()', raw=False, empty_set_put=False)
        self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set_put=False).src)
        self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set_put=False).src)
        self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set_put=False).src)

    def test_get_slice_empty_set(self):
        set_ = FST('{1}')

        self.assertEqual('{*()}', set_.get(0, 0, empty_set_get=True).src)
        self.assertEqual('{*()}', set_.get(0, 0, empty_set_get='star').src)
        self.assertEqual('set()', set_.get(0, 0, empty_set_get='call').src)
        self.assertEqual('()', set_.get(0, 0, empty_set_get='tuple').src)
        self.assertEqual('{}', set_.get(0, 0, empty_set_get=False).src)

    def test_empty_set_slice(self):
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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-get-slice-seq', default=False, action='store_true', help="regenerate get slice sequence test data")
    parser.add_argument('--regen-get-slice-stmt', default=False, action='store_true', help="regenerate get slice statement test data")
    parser.add_argument('--regen-put-slice-seq', default=False, action='store_true', help="regenerate put slice sequence test data")
    parser.add_argument('--regen-put-slice-stmt', default=False, action='store_true', help="regenerate put slice statement test data")
    parser.add_argument('--regen-put-slice', default=False, action='store_true', help="regenerate put slice test data")

    args, _ = parser.parse_known_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT12:
            raise RuntimeError('cannot regenerate on python version < 3.12')

    if args.regen_get_slice_seq or args.regen_all:
        print('Regenerating get slice sequence test data...')
        regen_get_slice_seq()

    if args.regen_get_slice_stmt or args.regen_all:
        print('Regenerating get slice statement cut test data...')
        regen_get_slice_stmt()

    if args.regen_put_slice_seq or args.regen_all:
        print('Regenerating put slice sequence test data...')
        regen_put_slice_seq()

    if args.regen_put_slice_stmt or args.regen_all:
        print('Regenerating put slice statement test data...')
        regen_put_slice_stmt()

    if args.regen_put_slice or args.regen_all:
        print('Regenerating put slice test data...')
        regen_put_slice()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
