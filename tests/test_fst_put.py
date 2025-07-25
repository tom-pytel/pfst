#!/usr/bin/env python

import os
import sys
import unittest
from ast import parse as ast_parse
from random import randint, seed, shuffle

from fst import *

from fst.astutil import compare_asts
from fst.misc import PYVER, PYLT11, PYLT12, PYGE12, PYGE14

from data_put_one import PUT_ONE_DATA
from data_other import (GET_SLICE_SEQ_DATA, GET_SLICE_STMT_DATA, GET_SLICE_STMT_NOVERIFY_DATA,
                        PUT_SLICE_SEQ_DATA, PUT_SLICE_STMT_DATA, PUT_SLICE_DATA, PUT_SRC_DATA,
                        REPLACE_EXISTING_ONE_DATA)

def read(fnm):
    with open(fnm) as f:
        return f.read()


def regen_put_slice_seq():
    newlines = []

    try:
        for dst, elt, start, stop, src, put_src, put_dump in PUT_SLICE_SEQ_DATA:
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
        print(dst, elt, start, stop, src, put_src)
        print(t.f.src)

        raise

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_SEQ_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_SEQ_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_stmt():
    newlines = []

    for dst, stmt, start, stop, field, options, src, put_src, put_dump in PUT_SLICE_STMT_DATA:
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

    start = lines.index('PUT_SLICE_STMT_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_STMT_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice():
    newlines = []

    for dst, attr, start, stop, field, options, src, put_src, put_dump in PUT_SLICE_DATA:
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

        except NotImplementedError as exc:
            tdst  = f'**{exc!r}**'
            tdump = ''

        else:
            tdst  = t.f.src
            tdump = t.f.dump(out=list)

            t.f.verify(raise_=True)

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


def regen_put_one():
    newlines = []

    for i, (dst, attr, idx, field, options, src, put_src, put_dump) in enumerate(PUT_ONE_DATA):
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            if options.get('raw') is True:
                continue

            options_ = {**options, 'raw': False}

            try:
                f.put(None if src == '**DEL**' else src, idx, field=field, **options_)

            except Exception as exc:
                tdst  = '**SyntaxError**' if isinstance(exc, SyntaxError) else f'**{exc!r}**'
                tdump = ''

            else:
                tdst  = f.root.src
                tdump = f.root.dump(out=list)

                if options.get('_verify', True):
                    f.root.verify(raise_=True)

            newlines.extend(f'''(r"""{dst}""", {attr!r}, {idx}, {field!r}, {options!r}, r"""{src}""", r"""{tdst}""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('"""),\n')

        except Exception:
            print(i, attr, idx, field, src, options)
            print('---')
            print(repr(dst))
            print('...')
            print(src)
            print('...')
            print(put_src)

            raise

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_put_one.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_ONE_DATA = [')
    stop  = lines.index(']  # END OF PUT_ONE_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_src():
    newlines = []

    for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_SRC_DATA):
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            g = f.put_src(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root

            tdst  = f.root.src
            tdump = f.root.dump(out=list)

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

    fnm = os.path.join(os.path.dirname(sys.argv[0]), 'data_other.py')

    with open(fnm) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SRC_DATA = [')
    stop  = lines.index(']  # END OF PUT_SRC_DATA')

    lines[start + 1 : stop] = newlines

    with open(fnm, 'w') as f:
        lines = f.write('\n'.join(lines))


class TestFSTPut(unittest.TestCase):
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
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'def f():\n    i\n')

        a = parse('''
def f(): pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'def f():\n    i\n')

        a = parse('''
def f():
    pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'def f():\n    # pre\n    i  # post\n')

        a = parse('''
def f(): pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'def f():\n    # pre\n    i  # post\n')

        a = parse('''
match a:
    case 1: pass
        '''.strip())
        a.body[0].cases[0].body[0].f.cut()
        a.body[0].cases[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'match a:\n    case 1:\n        i\n')

        a = parse('''
match a:
    case 1: pass
        '''.strip())
        a.body[0].cases[0].f.cut()
        a.body[0].f.put_slice('i', check_node_type=False)
        self.assertEqual(a.f.src, 'match a:\n    i\n')


        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 1:\n    i\n')

        a = parse('''
if 1:
    pass
else: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 1:\n    i\nelse: pass')

        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 1:\nelse:\n    i\n')

        a = parse('''
if 1:
    pass
        '''.strip())
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 1:\n    pass\nelse:\n    i\n')


        a = parse('''if 2:
    def f():
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        i\n')

        a = parse('''if 2:
    def f(): pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        i\n')

        a = parse('''if 2:
    def f():
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        # pre\n        i  # post\n')

        a = parse('''if 2:
    def f(): pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('# pre\ni  # post')
        self.assertEqual(a.f.src, 'if 2:\n    def f():\n        # pre\n        i  # post\n')

        a = parse('''if 2:
    match a:
        case 1: pass
        '''.strip())
        a.body[0].body[0].cases[0].body[0].f.cut()
        a.body[0].body[0].cases[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    match a:\n        case 1:\n            i\n')

        a = parse('''if 2:
    match a:
        case 1: pass
        '''.strip())
        a.body[0].body[0].cases[0].f.cut()
        a.body[0].body[0].f.put_slice('i', check_node_type=False)
        self.assertEqual(a.f.src, 'if 2:\n    match a:\n        i\n')


        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        i\n')

        a = parse('''if 2:
    if 1:
        pass
    else: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        i\n    else: pass')

        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n    else:\n        i\n')

        a = parse('''if 2:
    if 1:
        pass
        '''.strip())
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    if 1:\n        pass\n    else:\n        i\n')


        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'try:\nfinally:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'try:\nelse:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        handler = a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'try:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'try:\nelse: pass\nfinally:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\nfinally:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'try: pass\nfinally:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
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
        a.body[0].body[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\nelse:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'try: pass\nelse:\n    i\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
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
        a.body[0].body[0].f.cut()
        handler = a.body[0].handlers[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'try:\nexcept: pass\nelse: pass\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        handler = a.body[0].handlers[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'try: pass\nexcept: pass\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
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
        a.body[0].body[0].f.cut()
        a.body[0].handlers[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'try:\n    i\nelse: pass\n')

        a = parse('''
try: pass
except: pass
else: pass
finally: pass
        '''.strip())
        a.body[0].body[0].f.cut()
        a.body[0].orelse[0].f.cut()
        a.body[0].finalbody[0].f.cut()
        a.body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'try:\n    i\nexcept: pass\n')


        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    finally:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    else:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        handler = a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    else: pass\n    finally:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    finally:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='finalbody')
        self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    finally:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
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
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    else:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='orelse')
        self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    else:\n        i\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
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
        a.body[0].body[0].body[0].f.cut()
        handler = a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n    except: pass\n    else: pass\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        handler = a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice(handler, field='handlers')
        self.assertEqual(a.f.src, 'if 2:\n    try: pass\n    except: pass\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
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
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].handlers[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n    else: pass\n')

        a = parse('''if 2:
    try: pass
    except: pass
    else: pass
    finally: pass
        '''.strip())
        a.body[0].body[0].body[0].f.cut()
        a.body[0].body[0].orelse[0].f.cut()
        a.body[0].body[0].finalbody[0].f.cut()
        a.body[0].body[0].f.put_slice('i', field='body')
        self.assertEqual(a.f.src, 'if 2:\n    try:\n        i\n    except: pass\n')

    def test_insert_into_empty_block_shuffle(self):
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
            (fst.a.body[12].body[0].f, 'handlers'),
            (fst.a.body[12].body[0].f, 'orelse'),
            (fst.a.body[12].body[0].f, 'finalbody'),
        ]

        seed(0)

        bs = []
        ps = points[:]

        shuffle(ps)

        while ps:
            f, field = ps.pop()

            bs.append(f.get_slice(field=field, cut=True))

        ps = points[:]

        shuffle(ps)
        shuffle(bs)

        while ps:
            f, field = ps.pop()

            f.put_slice(bs.pop(), 0, 0, field=field, check_node_type=False)

        self.assertEqual(fst.src, '''
match a:
    case 1:
        try: a ; #  post-try
        except: b ; c  # post-except
        else: return 5
        finally: yield 6

match b:
    if 2: continue
    elif 3: o
    else: p

if 1:
    r = [i for i in range(100)]  # post-list-comprehension
else:
    try: raise
    except Exception as exc:
        raise exc from exc

try:
    assert s, t
j; k
else:
    l
    m
finally:
    ("Multi"
    "line"
    "string")

for a in b:
    # pre
    n  # post
else:
    pass

async for a in b:
    global c
else:
    i = 1

while a in b:
    except:
        aa or bb or cc
else:
    del x, y, z

with a as b:
    j = (i := k)

async with a as b:
    def docfunc(a, /, b=2, *c, d=3, **e):
        """Doc
        string."""

        return -1

def func():
    except:
        if 1: break

@asyncdeco
async def func():
    match z:
        case 1: zz
        case 2:
            zzz

class cls:
    f'{i:2} plus 1'

if indented:
    try:
        # pre-classdeco
        @classdeco
        class cls:
            @methdeco
            def meth(self):
                mvar = 5  # post-meth
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q
    else:
        """Multi
        line
        string."""
    finally:
        lambda x: x**2
'''.lstrip())

        for _ in range(25):  # now just fuzz it a bit, just in case
            bs = []
            ps = points[:]

            shuffle(ps)

            while ps:
                f, field = ps.pop()

                bs.append(f.get_slice(field=field, cut=True))

            ps = points[:]

            shuffle(ps)
            shuffle(bs)

            while ps:
                f, field = ps.pop()

                f.put_slice(bs.pop(), 0, 0, field=field, check_node_type=False)

    def test_insert_comment_into_empty_field(self):
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

        fst.a.body[1].cases[0].f.cut()
        fst.a.body[1].f.put_slice('pass', check_node_type=False)

        points = [
            (fst.a.body[0].cases[0].f, 'body'),
            (fst.a.body[1].f, 'cases'),
            (fst.a.body[2].f, 'body'),

            (fst.a.body[3].f, 'body'),
            (fst.a.body[3].f, 'handlers'),

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
            (fst.a.body[13].body[0].f, 'handlers'),
        ]

        for point, field in points:
            point.get_slice(field=field, cut=True)

        for i, (point, field) in enumerate(reversed(points)):
            point.put_slice(f'# {i}', 0, 0, field, check_node_type=False)

        self.assertEqual(fst.lines, [
            'match a:',
            '    case 1:  # CASE',
            '        # 15',
            '',
            'match b:  # MATCH',
            '    # 14',
            '',
            'if 1:  # IF',
            '    # 13',
            '',
            'try:  # TRY',
            '    # 12',
            '# 11',
            '',
            'for a in b:  # FOR',
            '    # 10',
            '',
            'async for a in b:  # ASYNC FOR',
            '    # 9',
            '',
            'while a in b:  # WHILE',
            '    # 8',
            '',
            'with a as b:  # WITH',
            '    # 7',
            '',
            'async with a as b:  # ASYNC WITH',
            '    # 6',
            '',
            'def func(a = """ \\\\ not linecont',
            '         # comment',
            '         """, **e):',
            '    # 5',
            '',
            '@asyncdeco',
            'async def func():  # ASYNC FUNC',
            '    # 4',
            '',
            'class cls:  # CLASS',
            '    # 3',
            '',
            'if clause:',
            '    while something:  # WHILE',
            '        # 2',
            '',
            'if indented:',
            '    try:  # TRY',
            '        # 1',
            '    # 0',
            ''
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
        a.body[1].body[0].f.cut()
        a.body[1].handlers[0].f.cut()
        a.body[1].f.put_slice('# pre\nn  # post', 0, 0, 'handlers', check_node_type=False)
        a.body[1].f.put_slice('i', 0, 0, 'handlers', check_node_type=False)
        self.assertEqual(a.f.src, '''
pass

try:
i
# pre
n  # post
else:
    @deco
    def inner() -> list[int]:
        q = 4  # post-inner-q
finally:
    pass
            '''.strip())

    def test_replace_and_put_pars_special(self):
        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.elts[1].f.replace(f, pars=True).root.src)

        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, a, 3]', parse('[1, 2, 3]').body[0].value.f.put(f, 1, pars='auto').root.src)

        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.f.put_slice(f, 1, 2, pars='auto', one=True).root.src)

    def test_replace_stmt_special(self):
        a = parse('''
if 1: pass
elif 2:
    pass
        '''.strip())
        a.body[0].orelse[0].f.put_slice(None, 0, 1)
        a.body[0].f.put_slice('break', 0, 1, 'orelse')
        self.assertEqual(a.f.src, 'if 1: pass\nelse:\n    break\n')

        a = parse('''
class cls:
    if 1: pass
    elif 2:
        pass
        '''.strip())
        a.body[0].body[0].orelse[0].f.put_slice(None, 0, 1)
        a.body[0].body[0].f.put_slice('break', 0, 1, 'orelse')
        self.assertEqual(a.f.src, 'class cls:\n    if 1: pass\n    else:\n        break\n')

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
                self.assertEqual(tdst.rstrip(), put_src)  # rstrip() because at current time stmt operations can add trailing newline

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
                self.assertEqual(tdst.rstrip(), put_src)  # rstrip() because at current time stmt operations can add trailing newline

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

    def test_put_special_fields(self):
        old_options = FST.set_options(pars=False, raw=True)

        self.assertEqual('{a: b, **c, e: f}', parse('{a: b, **d, e: f}').body[0].value.f.put('c', 1, field='values').root.src)
        self.assertEqual('{a: b, c: d, e: f}', parse('{a: b, **d, e: f}').body[0].value.f.put('c', 1, field='keys').root.src)
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

        FST.set_options(**old_options)

    def test_put_slice_seq_del(self):
        for i, (src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump) in enumerate(GET_SLICE_SEQ_DATA):
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
        for i, (dst, elt, start, stop, src, put_src, put_dump) in enumerate(PUT_SLICE_SEQ_DATA):
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
        for name in ('GET_SLICE_STMT_DATA', 'GET_SLICE_STMT_NOVERIFY_DATA'):
            verify = 'NOVERIFY' not in name

            for i, (src, elt, start, stop, field, options, src_cut, _, src_dump, _) in enumerate(globals()[name]):
                t = parse(src)
                f = (eval(f't.{elt}', {'t': t}) if elt else t).f

                try:
                    f.put_slice(None, start, stop, field, **options)

                    tsrc  = t.f.src
                    tdump = t.f.dump(out=list)

                    if verify:
                        t.f.verify(raise_=True)

                    self.assertEqual(tsrc, src_cut)
                    self.assertEqual(tdump, src_dump.strip().split('\n'))

                except Exception:
                    print(i, name, elt, start, stop)
                    print('---')
                    print(src)
                    print('...')
                    print(src_cut)

                    raise

    def test_put_slice_stmt(self):
        for i, (dst, stmt, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_STMT_DATA):
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
        self.assertEqual('(a, end := self.Label(),)', f.src)
        f.verify()

    def test_put_slice_empty_set(self):
        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, empty_set=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set=True).src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set=True).src)

        self.assertRaises(ValueError, FST('[1, 2]').put_slice, 'set()', raw=False, empty_set='seq')
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set='seq').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set='seq').src)
        self.assertEqual('[]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set='seq').src)

        self.assertEqual('[]', FST('[1, 2]').put_slice('set()', raw=False, empty_set='call').src)
        self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set='call').src)
        self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set='call').src)
        self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set='call').src)

        self.assertRaises(ValueError, FST('[1, 2]').put_slice, 'set()', raw=False, empty_set=False)
        self.assertEqual('[*()]', FST('[1, 2]').put_slice('{*()}', raw=False, empty_set=False).src)
        self.assertEqual('[*[]]', FST('[1, 2]').put_slice('{*[]}', raw=False, empty_set=False).src)
        self.assertEqual('[*{}]', FST('[1, 2]').put_slice('{*{}}', raw=False, empty_set=False).src)

    def test_put_one(self):
        ver = PYVER[1]

        for i, (dst, attr, idx, field, options, src, put_src, put_dump) in enumerate(PUT_ONE_DATA):
            if options.get('_ver', 0) > ver:
                continue

            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                if options.get('raw') is True:
                    continue

                options = {**options, 'raw': False}

                try:
                    f.put(None if src == '**DEL**' else src, idx, field=field, **options)

                except Exception as exc:
                    if not put_dump.strip() and put_src.startswith('**') and put_src.endswith('**'):
                        tdst  = '**SyntaxError**' if isinstance(exc, SyntaxError) else f'**{exc!r}**'
                        tdump = ['']

                    else:
                        raise

                else:
                    tdst  = f.root.src
                    tdump = f.root.dump(out=list)

                    if options.get('_verify', True):
                        f.root.verify(raise_=True)

                self.assertEqual(tdst, put_src)

                if (vd := options.get('_verdump')) and PYVER < (3, vd):
                    continue

                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(i, attr, idx, field, src, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

    def test_put_one_raw(self):
        ver = PYVER[1]

        for i, (dst, attr, idx, field, options, src, put_src, put_dump) in enumerate(PUT_ONE_DATA):
            if options.get('_ver', 0) > ver:
                continue

            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                if options.get('raw') is False:
                    continue

                options = {**options, 'raw': True}

                try:
                    f.put(None if src == '**DEL**' else src, idx, field=field, **options)

                except Exception as exc:
                    if not put_dump.strip() and put_src.startswith('**') and put_src.endswith('**'):
                        continue  # assume raw errors in line with non-raw, just different actual error
                    else:
                        raise

                else:
                    tdst  = f.root.src
                    tdump = f.root.dump(out=list)

                    if options.get('_verify', True):
                        f.root.verify(raise_=True)

                self.assertEqual(tdst.rstrip(), put_src.rstrip())

                if (vd := options.get('_verdump')) and PYVER < (3, vd):
                    continue

                # self.assertEqual(tdump, put_dump.strip().split('\n'))  # don't compare this because of the trailing newline difference

            except Exception:
                print(i, attr, idx, field, src, options)
                print('---')
                print(repr(dst))
                print('...')
                print(src)
                print('...')
                print(put_src)

                raise

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

        # ops

        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put('>>=', field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, 'and', field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, '*', field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, '~', field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, '<', field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put('and', field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, '/', field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, '~', field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, 'and', field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put('>>', field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, '~', field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, '*=', field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, 'and', field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, '*', field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put('+', field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, '<', field='op', raw=False)

        self.assertRaises(NodeError, parse('a is not b').body[0].value.f.put, '*=', 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a is not b').body[0].value.f.put, 'and', 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a is not b').body[0].value.f.put, '*', 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a is not b').body[0].value.f.put, '~', 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a is not b').body[0].value.f.put('>', 0, field='ops', raw=False).src)

        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(['>>='], field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, ['and'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, ['*'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, ['~'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, ['<'], field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put(['and'], field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, ['/'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, ['~'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, ['and'], field='op', raw=False)
        self.assertEqual('a >> b', parse('a + b').body[0].value.f.put(['>>'], field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, ['~'], field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, ['*='], field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, ['and'], field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, ['*'], field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put(['+'], field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, ['<'], field='op', raw=False)

        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, ['*='], 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, ['and'], 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, ['*'], 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, ['~'], 0, field='ops', raw=False)
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

        self.assertEqual('a >>= b', parse('a *= b').body[0].f.put(FST(RShift(), ['>>=']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(And(), ['and']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(Add(), ['+']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(Invert(), ['~']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a *= b').body[0].f.put, FST(Lt(), ['~']), field='op', raw=False)

        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Mult(), ['*']), field='op', raw=False)
        self.assertEqual('a and b', parse('a or b').body[0].value.f.put(FST(And(), ['and']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Div(), ['/']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Invert(), ['~']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a or b').body[0].value.f.put, FST(Lt(), ['~']), field='op', raw=False)

        self.assertEqual('a * b', parse('a + b').body[0].value.f.put(FST(Mult(), ['*']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(And(), ['and']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(RShift(), ['>>=']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(Invert(), ['~']), field='op', raw=False)
        self.assertRaises(NodeError, parse('a + b').body[0].value.f.put, FST(Lt(), ['~']), field='op', raw=False)

        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Mult(), ['*']), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(And(), ['and']), field='op', raw=False)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Sub(), ['-=']), field='op', raw=False)
        self.assertEqual('+a', parse('-a').body[0].value.f.put(FST(UAdd(), ['+']), field='op', raw=False).src)
        self.assertRaises(NodeError, parse('-a').body[0].value.f.put, FST(Lt(), ['-=']), field='op', raw=False)

        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(Mult(), ['*']), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(And(), ['and']), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(Sub(), ['-=']), 0, field='ops', raw=False)
        self.assertRaises(NodeError, parse('a < b').body[0].value.f.put, FST(UAdd(), ['-=']), 0, field='ops', raw=False)
        self.assertEqual('a > b', parse('a < b').body[0].value.f.put(FST(Gt(), ['>']), 0, field='ops', raw=False).src)

        # make sure we can't put TO invalid locations

        f = parse('[1, 2, 3]').body[0].value.f
        # self.assertEqual('[1, 4]', f.elts[1].replace('4', to=f.elts[2], raw=False).root.src)
        self.assertRaises(NodeError, f.elts[1].replace, '4', to=f.elts[2], raw=False)

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertRaises(ValueError, f.elts[1].replace, '4', to=f.elts[0], raw=False)

        f = parse('a = b').body[0].f
        self.assertRaises(NodeError, f.targets[0].replace, 'c', to=f.value, raw=False)

        f = parse('a = b').body[0].f
        self.assertRaises(ValueError, f.value.replace, 'c', to=f.targets[0], raw=False)

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
            self.assertEqual('try:\n    pass\nexcept* Exception:\n    pass\n', g.src)

            g = FST('try:\n    pass\nexcept ValueError:\n    pass', 'exec')
            g.body[0].put(f.a, 0, field='handlers', raw=False)
            self.assertEqual('try:\n    pass\nexcept Exception:\n    pass\n', g.src)

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

        # special Call.args but not otherwise

        f = FST('call(a)', 'exec')
        f.body[0].value.put('*[] or []', 0, 'args', raw=False)
        self.assertEqual('call(*[] or [])', f.src)
        f.verify()

        f = FST('call(a)', 'exec')
        f.body[0].value.put('yield 1', 0, 'args', raw=False)
        self.assertEqual('call((yield 1))', f.src)
        f.verify()

        # MatchAs, ugh...

        f = FST('match a:\n case _ as unknown: pass', 'exec')
        g = f.body[0].cases[0].pattern.pattern.copy()
        f.body[0].cases[0].pattern.put(None, 'pattern', raw=False)
        self.assertEqual('match a:\n case unknown: pass', f.src)
        f.body[0].cases[0].pattern.put(g, 'pattern', raw=False)
        self.assertEqual('match a:\n case _ as unknown: pass', f.src)
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

            f = FST('f"{a}"', stmt)

            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            self.assertEqual('f"{a:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('f"{a}"', f.src)
            f.verify()

            f.value.values[0].put('r', 'conversion', raw=True)
            self.assertEqual('f"{a!r}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a}"', f.src)
            f.verify()

            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            f.value.values[0].put('r', 'conversion', raw=True)
            self.assertEqual('f"{a!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('f"{a!r}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a}"', f.src)
            f.verify()

            f.value.values[0].put('r', 'conversion', raw=True)
            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            self.assertEqual('f"{a!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('f"{a}"', f.src)
            f.verify()

            f.value.put('{z}', 0, 'values', raw=True)
            self.assertEqual('f"{z}"', f.src)
            f.verify()

            f = FST('f"{a=}"', stmt)

            f.value.values[1].put('r', 'conversion', raw=True)
            self.assertEqual('f"{a=!r}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a=}"', f.src)
            f.verify()

            f.value.values[1].put('0.5f<8', 'format_spec', raw=True)
            f.value.values[1].put('r', 'conversion', raw=True)
            self.assertEqual('f"{a=!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'conversion', raw=True)
            self.assertEqual('f"{a=:0.5f<8}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'format_spec', raw=True)
            self.assertEqual('f"{a=}"', f.src)
            f.verify()

        if PYGE14:
            self.assertRaises(NotImplementedError, FST('t"{a}"').values[0].put, '"s"', 'conversion', raw=False)  # not implemented yet
            self.assertRaises(NotImplementedError, FST('t"{a}"').values[0].put, 'f"0.5f"', 'format_spec', raw=False)  # not implemented yet
            self.assertRaises(NotImplementedError, FST('t"{a}"').put, '"s"', 0, 'values', raw=False)  # not implemented yet

            f = FST('t"{a}"', stmt)

            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            self.assertEqual('t"{a:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('t"{a}"', f.src)
            f.verify()

            f.value.values[0].put('r', 'conversion', raw=True)
            self.assertEqual('t"{a!r}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a}"', f.src)
            f.verify()

            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            f.value.values[0].put('r', 'conversion', raw=True)
            self.assertEqual('t"{a!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('t"{a!r}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a}"', f.src)
            f.verify()

            f.value.values[0].put('r', 'conversion', raw=True)
            f.value.values[0].put('0.5f<8', 'format_spec', raw=True)
            self.assertEqual('t"{a!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a:0.5f<8}"', f.src)
            f.verify()

            f.value.values[0].put(None, 'format_spec', raw=True)
            self.assertEqual('t"{a}"', f.src)
            f.verify()

            f.value.put('{z}', 0, 'values', raw=True)
            self.assertEqual('t"{z}"', f.src)
            f.verify()

            f = FST('t"{a=}"', stmt)

            f.value.values[1].put('r', 'conversion', raw=True)
            self.assertEqual('t"{a=!r}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a=}"', f.src)
            f.verify()

            f.value.values[1].put('0.5f<8', 'format_spec', raw=True)
            f.value.values[1].put('r', 'conversion', raw=True)
            self.assertEqual('t"{a=!r:0.5f<8}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'conversion', raw=True)
            self.assertEqual('t"{a=:0.5f<8}"', f.src)
            f.verify()

            f.value.values[1].put(None, 'format_spec', raw=True)
            self.assertEqual('t"{a=}"', f.src)
            f.verify()

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

        # Tuple Slice behavior

        self.assertEqual('x:y:z, b', FST('a, b').elts[0].replace('x:y:z', raw=False).root.src)
        self.assertRaises(NodeError, FST('(a, b)').elts[0].replace, 'x:y:z', raw=False)
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
            self.assertRaises(NodeError, f.annotation.slice.elts[1].replace, '*s', raw=False)

            f = FST('a: b[c, d]')
            g = FST('for a, *s in b: pass').target.copy()
            self.assertRaises(NodeError, f.annotation.slice.replace, g, raw=False)

        # don't allow vararg with starred annotation into normal args

        if not PYLT11:
            f = FST('def f(a, /, b, *v: *s, c): pass')
            self.assertRaises(NodeError, f.args.posonlyargs[0].replace, f.args.vararg.copy(), raw=False)
            self.assertRaises(NodeError, f.args.args[0].replace, f.args.vararg.copy(), raw=False)
            self.assertRaises(NodeError, f.args.kwonlyargs[0].replace, f.args.vararg.copy(), raw=False)

        # more unparenthesized tuple schenanigans

        f = FST('a[:, b]')
        f.slice.put_slice('[\n"foo"\n]', 1, 2, 'elts')
        self.assertEqual('a[:,\n"foo"\n]', f.src)

        f = FST('a = b, c')
        f.value.put_slice('[\n"foo"\n]', 1, 2, 'elts')
        self.assertEqual('a = (b,\n"foo"\n)', f.src)

        f = FST('a = b, c')
        f.value.put_slice('["foo"   ]', 1, 2, 'elts')
        self.assertEqual('a = b, "foo"', f.src)

        f = FST('for a, b in c: pass')
        f.target.put_slice('[\nz\n]', 1, 2, 'elts')
        self.assertEqual('for (a,\nz\n) in c: pass', f.src)

        f = FST('for a, b in c: pass')
        f.target.put_slice('[z   ]', 1, 2, 'elts')
        self.assertEqual('for a, z in c: pass', f.src)

        f = FST('a[:, b]')
        f.slice.put_slice('["foo"\\\n]', 1, 2, 'elts')
        self.assertEqual('a[:, "foo"\\\n]', f.src)

        f = FST('a = b, c')
        f.value.put_slice('["foo"\\\n ]', 1, 2, 'elts')  # TODO: without that last space at end of file we get unexpected EOF, way too niche for now
        self.assertEqual('a = b, "foo"', f.src)

        f = FST('for a, b in c: pass')
        f.target.put_slice('[z\\\n]', 1, 2, 'elts')
        self.assertEqual('for a, z in c: pass', f.src)

        f = FST('a,')
        f.put_slice('[ {z} ]', 0, 1)
        self.assertEqual('{z},', f.src)

        f = FST('a[:, b]')
        f.slice.put_slice('[ {z} ]', 0, 1)
        self.assertEqual('a[{z}, b]', f.src)

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
        g = FST('(i := j)', 'exec').body[0].value.copy(pars=False)
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

    def test_put_src(self):
        for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_SRC_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.put_src(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root

                tdst  = f.root.src
                tdump = f.root.dump(out=list)

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

    def test_put_src_random_same(self):
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
                put_lines = master.get_src(ln, col, end_ln, end_col, True)

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

    def test_put_src_from_put_slice_data(self):
        from fst.misc import _fixup_field_body
        from fst.fst_slice import _raw_slice_loc

        for i, (dst, attr, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_DATA):
            if options != {'raw': True}:
                continue

            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                field, _ = _fixup_field_body(f.a, field)
                loc      = _raw_slice_loc(f, start, stop, field)

                f.put_src(None if src == '**DEL**' else src, *loc)

                tdst  = f.root.src
                tdump = f.root.dump(out=list)

                f.root.verify(raise_=True)

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

    def test_put_src_special(self):
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
        s = f.get_src(5, 8, 8, 14)
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
        s = f.get_src(5, 8, 8, 14)
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
        self.assertRaises(NodeError, f.value.replace, f)

        f = FST('[1, 2]')
        self.assertRaises(NodeError, f.elts.append, f)

    def test_raw_special(self):
        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.put('for x in y', 1, raw=True)
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
        self.assertEqual('[1, (a, b), 3]', f.put_slice(g, 1, 2, raw=True, one=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, a, b, 3: pass', f.put_slice(g, 1, 2, raw=True).root.src)

        f = parse('match a:\n case 1, 2, 3: pass').body[0].cases[0].pattern.f
        g = parse('[a, b]').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1, [a, b], 3: pass', f.put_slice(g, 1, 2, raw=True, one=True).root.src)

        f = parse('match a:\n case 1 | 2 | 3: pass').body[0].cases[0].pattern.f
        g = parse('a | b').body[0].value.f.copy()
        self.assertEqual('match a:\n case 1 | a | b | 3: pass', f.put_slice(g, 1, 2, raw=True).root.src)

        # make sure we can't put TO location behind self

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertEqual('[1, 4]', f.elts[1].replace('4', to=f.elts[2], raw=True).root.src)

        f = parse('[1, 2, 3]').body[0].value.f
        self.assertRaises(ValueError, f.elts[1].replace, '4', to=f.elts[0], raw=True)

        f = parse('a = b').body[0].f
        self.assertEqual('c', f.targets[0].replace('c', to=f.value, raw=True).root.src)

        f = parse('a = b').body[0].f
        self.assertRaises(ValueError, f.value.replace, 'c', to=f.targets[0], raw=True)

    def test_raw_non_mod_stmt_root(self):
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

    def test_unparenthesized_tuple_with_line_continuations(self):
        # backslashes are annoying to include in the regenerable test cases

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 1, cut=True)
        self.assertEqual(a.f.src, '2, \\\n3')
        self.assertEqual(s.src, '(1, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(1, 2, cut=True)
        self.assertEqual(a.f.src, '1, \\\n3')
        self.assertEqual(s.src, '(\n2, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(2, 3, cut=True)
        self.assertEqual(a.f.src, '1, \\\n2,')
        self.assertEqual(s.src, '(\n3,)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 2, cut=True)
        self.assertEqual(a.f.src, '3,')
        self.assertEqual(s.src, '(1, \\\n2, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(1, 3, cut=True)
        self.assertEqual(a.f.src, '1,')
        self.assertEqual(s.src, '(\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 3, cut=True)
        self.assertEqual(a.f.src, '()')
        self.assertEqual(s.src, '(1, \\\n2, \\\n3)')

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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-put-slice-seq', default=False, action='store_true', help="regenerate put slice sequence test data")
    parser.add_argument('--regen-put-slice-stmt', default=False, action='store_true', help="regenerate put slice statement test data")
    parser.add_argument('--regen-put-slice', default=False, action='store_true', help="regenerate put slice test data")
    parser.add_argument('--regen-put-one', default=False, action='store_true', help="regenerate put one test data")
    parser.add_argument('--regen-put-src', default=False, action='store_true', help="regenerate put src test data")

    args = parser.parse_args()

    if any(getattr(args, n) for n in dir(args) if n.startswith('regen_')):
        if PYLT12:
            raise RuntimeError('cannot regenerate on python version < 3.12')

    if args.regen_put_slice_seq or args.regen_all:
        print('Regenerating put slice sequence test data...')
        regen_put_slice_seq()

    if args.regen_put_slice_stmt or args.regen_all:
        print('Regenerating put slice statement test data...')
        regen_put_slice_stmt()

    if args.regen_put_slice or args.regen_all:
        print('Regenerating put slice test data...')
        regen_put_slice()

    if args.regen_put_one or args.regen_all:
        print('Regenerating put one test data...')
        regen_put_one()

    if args.regen_put_src or args.regen_all:
        print('Regenerating put raw test data...')
        regen_put_src()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
