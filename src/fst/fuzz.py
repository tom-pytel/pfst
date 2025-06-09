"""Fuzzers, mostly mean for debugging `fst` itself."""

import argparse
import os
import sys
import sysconfig
from ast import *
from itertools import repeat
from math import log10
from random import choice, randint, seed, shuffle
from types import NoneType
from typing import Any, Generator

from .astutil import *
from .astutil import TemplateStr, Interpolation
from .fst import FST, NodeError

PROGRAM     = 'python -m fst.fuzz'
_PY_VERSION = sys.version_info[:2]
_PYLT12     = _PY_VERSION < (3, 12)
_PYLT14     = _PY_VERSION < (3, 14)


def find_pys(path) -> list[str]:
    if os.path.isfile(path):
        return [path] if path.endswith('.py') else []

    if os.path.isdir(path):
        fnms = []

        for dir, _, fnms_ in os.walk(path):
            fnms.extend(os.path.join(dir, fnm) for fnm in fnms_ if fnm.endswith('.py'))

        return fnms

    raise ValueError(f'unknown thing: {path}')


class Fuzzy:
    syspyfnms = None
    name      = 'Fuzzy'
    forever   = False

    def __init__(self, args: dict[str, Any]):
        self.args    = args
        self.batch   = args.get('batch')
        self.debug   = args.get('debug')
        self.loop    = args.get('loop')
        self.seed    = args.get('seed')
        self.shuffle = args.get('shuffle')
        self.verbose = args.get('verbose')
        self.verify  = args.get('verify')

        if paths := args.get('PATH'):
            fnms = sum((find_pys(path) for path in paths), start=[])

        elif Fuzzy.syspyfnms is None:
            fnms = find_pys(sys.prefix)

            if stdlib := sysconfig.get_paths().get('stdlib'):
                fnms.extend(find_pys(stdlib))

        self.fnms = fnms

    def iter_pys(self) -> Generator[tuple[str, FST], None, None]:
        fnms  = self.fnms
        width = int(log10(len(fnms) - 1 or 1)) + 1

        if self.args['shuffle']:
            fnms = fnms[:]

            shuffle(fnms)

        for i, fnm in enumerate(fnms):
            head = f'{i:<{width}}: {fnm}'

            try:
                with open(fnm) as f:
                    fst = FST.fromsrc(f.read())

            except (NodeError, SyntaxError, UnicodeDecodeError) as exc:
                print(f'{head} - read/parse fail: **{exc.__class__.__name__}**')

            else:
                print(head)

                yield fnm, fst

    def fuzz(self) -> bool:
        for fnm, fst in self.iter_pys():
            seed((rnd_seed := randint(0, 2**32-1)) if (rnd_seed := self.seed) is None else rnd_seed)

            try:
                self.fuzz_one(fst, fnm)

            except Exception:
                print('-'*80)
                print('Random seed was:', rnd_seed)

                raise

        return self.forever

    def fuzz_one(self, fst: FST, fnm: str):
        pass


class VerifyCopy(Fuzzy):
    name = 'verify_copy'

    def fuzz_one(self, fst, fnm) -> bool:
        for f in fst.walk('all'):
            if not f.is_parsable():  # because .verify() needs to parse
                continue

            g = None

            try:
                g = f.copy()

                g.verify()

            except Exception:
                print('src:', '-'*75)
                print(f.src)
                print('.'*80)
                f.dump('stmt')

                if g:
                    print('cpy:', '-'*75)
                    print(g.src)
                    print('.'*80)
                    g.dump('stmt')

                raise


class SynOrder(Fuzzy):
    name = 'syn_order'

    def fuzz_one(self, fst, fnm) -> bool:
        bln, bcol = 0, 0

        for f in (gen := fst.walk(True)):
            if _PYLT12 and isinstance(f.a, JoinedStr):  # these have no location info in py <3.12
                gen.send(False)

                continue

            try:
                if not isinstance(f.a, (FormattedValue, Interpolation)):  # preceding '=' debug strings may start after these
                    assert f.bln > bln or (f.bln == bln and f.bcol >= bcol)

                l2   = list(f.walk(True, self_=False, recurse=False))
                l, c = [], None

                while c := f.next_child(c, True):
                    l.append(c)

                try:
                    assert l == l2

                except Exception:
                    print(l)
                    print(l2)

                    raise

                l3   = l2[::-1]
                l, c = [], None

                while c := f.prev_child(c, True):
                    l.append(c)

                try:
                    assert l == l3

                except Exception:
                    print(l)
                    print(l3)

                    raise

                l4 = list(f.walk(True, self_=False, recurse=False, back=True))

                # print('l3:', l3)
                # print('l4:', l4)

                assert l3 == l4

                if isinstance(f.a, (FunctionDef, AsyncFunctionDef, ClassDef, Lambda, ListComp, SetComp, DictComp, GeneratorExp)):
                    l5 = list(f.walk(True, self_=False, recurse=False, scope=True))
                    l6 = list(f.walk(True, self_=False, recurse=False, scope=True, back=True))

                    # for g in l5: print(g)
                    # print('...')
                    # for g in l6: print(g)

                    assert l5 == l6[::-1]

            except Exception:
                print(f'... {bln}, {bcol} ... {f.bln}, {f.bcol} ... {f.pfield} ... {f.parent}')

                f.parent.dump()

                while f:
                    print(f)

                    f = f.parent

                raise

            bln, bcol = f.bln, f.bcol


class ReputSrc(Fuzzy):
    name    = 'reput_src'
    forever = True

    def fuzz_one(self, fst, fnm) -> bool:
        lines = fst._lines

        seed(rnd_seed := randint(0, 2**32-1))

        try:
            for count in range(self.batch or 1000):
                copy      = fst.copy()
                ln        = randint(0, len(lines) - 1)
                col       = randint(0, len(lines[ln]))
                end_ln    = randint(ln, len(lines) - 1)
                end_col   = randint(col if end_ln == ln else 0, len(lines[end_ln]))
                put_lines = fst.get_src(ln, col, end_ln, end_col, True)

                if not (count % 10):
                    # s = f'{count, ln, col, end_ln, end_col}'

                    # sys.stdout.write('\x08' * 40 + s.ljust(40))
                    sys.stdout.write('.')
                    sys.stdout.flush()

                try:
                    copy.put_src(put_lines, ln, col, end_ln, end_col)
                    copy.verify()

                    compare_asts(fst.a, copy.a, locs=True, raise_=True)

                    assert copy.src == fst.src

                except:
                    print('\nRandom seed was:', rnd_seed)
                    print(count, ln, col, end_ln, end_col)
                    print('-'*80)
                    print(put_lines)
                    # print('.'*80)
                    # print(copy.src)

                    raise

        finally:
            print()


from fst.fst_one import (
    _PUT_ONE_HANDLERS, _put_one_exprish_optional, _put_one_identifier_optional,
    _put_one_Dict_keys, _put_one_withitem_optional_vars,
    _put_one_ExceptHandler_name, _put_one_keyword_arg, _put_one_NOT_IMPLEMENTED_YET,
)

class ReputOne(Fuzzy):
    name = 'reput_one'

    DELETE     = True  #False  #
    VERIFY     = False  #True  #
    VERIFY_DEL = True

    def fuzz_one(self, fst, fnm) -> bool:
        backup = fst.copy()
        count  = 0

        for f in fst.walk(True, self_=False):

            assert f.a is not None

            sig = (f.parent.a.__class__, f.pfield.name)

            if sig not in _PUT_ONE_HANDLERS or sig in ((Constant, 'value'), (MatchSingleton, 'value')):
                continue

            if (handler := _PUT_ONE_HANDLERS.get(sig, [None])[1]) is _put_one_NOT_IMPLEMENTED_YET:
                continue

            try:
                field, idx = f.pfield

                put = None
                g   = None
                g   = f.copy()
                ast = copy_ast(g.a)
                src = g.src
                put = 'ident'

                if not (count := count + 1) % 100:
                    sys.stdout.write('.'); sys.stdout.flush()


                # IDENTIFIERS

                for subfield in ('name', 'module', 'names', 'attr', 'id', 'arg', 'rest', 'kwd_attrs'):  # check identifiers
                    changed = False

                    if (child := getattr(f.a, subfield, False)) is not False:
                        delete  = self.DELETE and _PUT_ONE_HANDLERS.get((f.a.__class__, subfield), [None])[1] in (
                            _put_one_identifier_optional, _put_one_ExceptHandler_name, _put_one_keyword_arg)
                        changed = True
                        subs    = list(enumerate(child)) if isinstance(child, list) else [(None, child)]

                        for i, child in subs:
                            if isinstance(child, (str, NoneType)):
                                if delete:
                                    try:
                                        f.put(None, i, field=subfield, raw=False)
                                    except Exception as e:
                                        if 'in this state' not in str(e):
                                            raise

                                    if self.verify:
                                        fst.verify()

                                f.put(child, i, field=subfield, raw=False)

                if changed:
                    fst.verify()


                # NODES

                delete = self.DELETE and handler in (_put_one_exprish_optional, _put_one_Dict_keys,
                                                        _put_one_withitem_optional_vars)
                if self.debug:
                    print('...', g, idx, field, g.parent, g.src)
                    f.parent.dump(True); print(f.parent.src); print()

                if delete:

                    put = 'del'

                    try:
                        f.parent.put(None, idx, field=field, raw=False)
                    except Exception as e:
                        if not str(e).endswith('in this state'): raise

                    if self.verify:
                        fst.verify()

                puts = [
                    ('fst', lambda: f.parent.put(g, idx, field=field, raw=False)),
                    ('ast', lambda: f.parent.put(ast, idx, field=field, raw=False)),
                    ('src', lambda: f.parent.put(src, idx, field=field, raw=False)),
                ]

                shuffle(puts)

                for put, func in puts:
                    if self.debug:
                        print(f'   ', f.parent.src)

                    func()

                    if self.verify:
                        fst.verify()

            except Exception:
                print('-'*80)
                print(sig, put, fst.child_path(f, True), idx, field, f.parent)
                print(f)
                print(f.src)
                print(g)
                print(g.src)

                raise


        sys.stdout.write('\n')

        if self.verbose:
            print(fst.src)

        if not self.verify:
            fst.verify()

        for ast in (fst.a, backup.a):
            for a in walk(ast):
                if isinstance(a, Constant) and isinstance(a.value, str) and (p := (f := a.f).parent):
                    if isinstance(pa := p.a, Expr):  # zero out docstrings because indentation may have changed for docstrings which do not respect their own indentation level
                        a.value = ''

                    elif isinstance(pa, (JoinedStr, TemplateStr)):  # also zero out these Constants in JoinedStr if they are debug strings because different source for same effective expression will cause compare to fail
                        # if ((idx := f.pfield.idx + 1) < len(pa.values) and
                        #     isinstance(na := pa.values[idx], (FormattedValue, Interpolation)) and
                        #     (strs := na.f._get_fmtval_interp_strs()) and strs[0]
                        # ):
                        #     a.value = ''
                        a.value = ''  # just don't compare, pain-in-the-ass because of AST JoinedStrs unparsing without needef information

        try:
            compare_asts(fst.a, backup.a,
                         cb_primitive=(lambda p1, p2, n, i: n in ('kind', 'type_comment') or (p1.__class__ is p2.__class__ and p1 == p2)),
                         raise_=True)

        except Exception as exc:
            if self.debug:
                try:
                    fst.dump()
                except Exception:
                    pass

            raise


class PutOneExprish(Fuzzy):
    name    = 'put_one_exprish'
    forever = True

    exprs   = [
        'a or b',
        'a\nor\nb',
        'a := b',
        'a\n:=\nb',
        'a | b',
        'a\n|\nb',
        'a ** b',
        'a\n**\nb',
        'not a',
        'not\na',
        '~a',
        '~\na',
        'lambda: None',
        'lambda:\nNone',
        'a if b else c',
        'a\nif\nb\nelse\nc',
        '{a: b}',
        '{a:\nb}',
        '{a}',
        '{a,\nb}',
        '[a for a in b]',
        '[a\nfor\na\nin\nb]',
        '{a for a in b}',
        '{a\nfor\na\nin\nb}',
        '{a: c for a, c in b}',
        '{a: c\nfor\na, c\nin\nb}',
        '(a for a in b)',
        '(a\nfor\na\nin\nb)',
        'await a',
        'await\na',
        'yield',
        'yield a',
        'yield\na',
        'yield from a',
        'yield\nfrom\na',
        'a < b',
        'a\n<\nb',
        'f(a)',
        'f\n(\na\n)',
        "f'{a}'",
        'f"{a}"',
        "f'''{a}'''",
        'f"""{a}"""',
        '...',
        'None',
        'True',
        'False',
        '1',
        '1.0',
        '1j',
        "'a'",
        '"a"',
        "'''a'''",
        '"""a"""',
        "b'a'",
        'b"a"',
        "b'''a'''",
        'b"""a"""',
        'a.b',
        'a\n.\nb',
        'a[b]',
        'a\n[\nb\n]',
        # '*a',
        # '*\na',
        '[a, b]',
        '[\na\n,\nb\n]',
        '(a, b)',
        '(\na\n,\nb\n)',
        'a,',
        'a\n,',
        'a, b',
        'a\n,\nb',
    ]

    if not _PYLT14:
        exprs.extend([
            "t'{a}'",
            't"{a}"',
            "t'''{a}'''",
            't"""{a}"""',
        ])

    exprs = [FST(e, 'expr') for e in exprs]

    pats = [
        '42',
        'None',
        '[a, *b]',
        '[\na\n,\n*\nb\n]',
        'a, *b',
        '\na\n,\n*\nb\n',
        '{"key": _}',
        '{\n"key"\n:\n_\n}',
        'SomeClass(attr=val)',
        'SomeClass\n(\nattr\n=\nval\n)',
        'as_var',
        '1 as as_var',
        '1\nas\nas_var',
        '1 | 2',
        '1\n|\n2',
    ]

    pats = [FST(e, 'pattern') for e in pats]

    def fuzz_one(self, fst, fnm) -> bool:
        count = 0
        exprs = []
        pats  = []

        for f in fst.walk(True):
            if isinstance(a := f.a, expr):
                if getattr(a, 'ctx', None).__class__ is Load and not isinstance(f.parent.a, pattern) and f.is_parsable():
                    # not isinstance(a, Starred) and   # don't mess with Starred because its just too inconsistemt
                    exprs.append(f)

            elif isinstance(a, pattern):
                pats.append(f)

        try:
            for e in reversed(exprs):
                if not ((count := count + 1) % 100):
                    sys.stdout.write('.')
                    sys.stdout.flush()

                while True:
                    org = choice(self.exprs)

                    if not (_PYLT12 and isinstance(org.a, Starred) and e.pfield.name == 'slice'):  # because py <3.12 can't have naked Starred in .slice
                        break

                code = org.copy()

                match randint(0, 2):
                    case 0:
                        put  = 'fst'
                    case 1:
                        put  = 'ast'
                        code = code.a
                    case 2:
                        put  = 'src'
                        code = code.src

                try:
                    e.replace(code, raw=False)

                    if self.verify:
                        fst.verify()

                except Exception:
                    print('\n-', put, '-'*74)
                    print((p := e.parent_stmtish()).src)
                    print('.'*80)
                    p.dump()
                    print('-'*80)
                    print(e.src)
                    print('.'*80)
                    print(e.dump())
                    print('-'*80)
                    org.dump()
                    print('.'*80)
                    print(org.src)

                    raise

            for e in reversed(pats):
                if not ((count := count + 1) % 100):
                    sys.stdout.write('.')
                    sys.stdout.flush()

                org  = choice(self.pats)
                code = org.copy()

                match randint(0, 2):
                    case 0:
                        put  = 'fst'
                    case 1:
                        put  = 'ast'
                        code = code.a
                    case 2:
                        put  = 'src'
                        code = code.src

                try:
                    e.replace(code, raw=False)

                    if self.verify:
                        fst.verify()

                except Exception:
                    print('\n-', put, '-'*74)
                    print((p := e.parent_stmtish()).src)
                    print('.'*80)
                    p.dump()
                    print('-'*80)
                    print(e.src)
                    print('.'*80)
                    print(e.dump())
                    print('-'*80)
                    org.dump()
                    print('.'*80)
                    print(org.src)

                    raise

            fst.verify()

        finally:
            sys.stdout.write('\n')


FUZZIES = {o.name: o for o in globals().values() if isinstance(o, type) and o is not Fuzzy and issubclass(o, Fuzzy)}


def main():
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=f'Available fuzzies: {", ".join(FUZZIES)}'
    )

    parser.add_argument('PATH', nargs='*',
                        help='path of file or directory of files to use')
    parser.add_argument('-f', '--fuzz', action='append', default=[],
                        help='which fuzzies to run')
    parser.add_argument('-b', '--batch', type=int, default=None,
                        help='batch size')
    parser.add_argument('-g', '--debug', default=False, action='store_true',
                        help='print debug info')
    parser.add_argument('-l', '--loop', type=int, default=None,
                        help='number of times to loop')
    parser.add_argument('-d', '--seed', type=int, default=None,
                        help='random seed (set per file)')
    parser.add_argument('-s', '--shuffle', default=False, action='store_true',
                        help='shuffle files on each loop')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='verbose output')
    parser.add_argument('-y', '--verify', default=False, action='store_true',
                        help='verify after everything (slower)')

    args = parser.parse_args()
    fuzz = dict.fromkeys(sum((f.replace(',', ' ').split() for f in args.fuzz), start=[]) if args.fuzz else FUZZIES)

    print(args)

    if any((fuzzy := f) not in FUZZIES for f in fuzz):
        raise ValueError(f'invalid fuzzy: {fuzzy}')

    fuzzies = []
    args    = vars(args)

    for f in fuzz:
        fuzzies.append(FUZZIES[f](args))

    for _ in range(l) if (l := args['loop']) else repeat(None):
        for f in fuzzies[:]:
            print(f'Running: {f.name}')

            if not f.fuzz():
                print(f'{f.name} has finished and will not be run again.')

                fuzzies.remove(f)

        if not fuzzies:
            print('Done...')

            break


if __name__ == '__main__':
    main()
