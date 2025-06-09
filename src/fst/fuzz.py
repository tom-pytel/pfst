import argparse
import os
import sys
import sysconfig
from ast import *
from itertools import repeat
from random import randint, seed, shuffle
from types import NoneType
from typing import Any, Generator

from .astutil import *
from .fst import FST, NodeError

PROGRAM = 'python -m fst.fuzz'


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

    def __init__(self, args: dict[str, Any]):
        self.args   = args
        self.verify = args['verify']

        if paths := args['PATH']:
            fnms = sum((find_pys(path) for path in paths), start=[])

        elif Fuzzy.syspyfnms is None:
            fnms = find_pys(sys.prefix)

            if stdlib := sysconfig.get_paths().get('stdlib'):
                fnms.extend(find_pys(stdlib))

        self.fnms = fnms

    def iter_pys(self) -> Generator[tuple[str, FST], None, None]:
        fnms = self.fnms

        if self.args['shuffle']:
            fnms = fnms[:]

            shuffle(fnms)

        for fnm in fnms:
            try:
                with open(fnm) as f:
                    fst = FST.fromsrc(f.read())

            except (NodeError, SyntaxError, UnicodeDecodeError) as exc:
                print(f'{fnm} - read/parse fail: **{exc.__class__.__name__}**')

            else:
                print(fnm)

                yield fnm, fst

    def fuzz(self) -> bool:
        for fnm, fst in self.iter_pys():
            fst.dump()

        return False


class VerifyCopy(Fuzzy):
    name = 'verify_copy'

    def fuzz(self) -> bool:
        for fnm, fst in self.iter_pys():
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


class ReputSrc(Fuzzy):
    name = 'reput_src'

    def fuzz(self) -> bool:
        for fnm, fst in self.iter_pys():
            lines = fst._lines

            seed(rnd_seed := randint(0, 2**32-1))

            try:
                for count in range(self.args.get('batch') or 1000):
                    copy      = fst.copy()
                    ln        = randint(0, len(lines) - 1)
                    col       = randint(0, len(lines[ln]))
                    end_ln    = randint(ln, len(lines) - 1)
                    end_col   = randint(col if end_ln == ln else 0, len(lines[end_ln]))
                    put_lines = fst.get_src(ln, col, end_ln, end_col, True)

                    if not (count % 10):
                        s = f'{count, ln, col, end_ln, end_col}'

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

        return True


class ReputOne(Fuzzy):
    name = 'reput_one'

    DELETE     = True  #False  #
    VERIFY     = False  #True  #
    VERIFY_DEL = True

    def fuzz(self) -> bool:
        from fst.fst_one import (
            _PUT_ONE_HANDLERS, _put_one_exprish_optional, _put_one_identifier_optional,
            _put_one_Dict_keys, _put_one_withitem_optional_vars,
            _put_one_ExceptHandler_name, _put_one_keyword_arg, _put_one_NOT_IMPLEMENTED_YET,
        )

        for fnm, fst in self.iter_pys():
            backup  = fst.copy()
            lines   = fst._lines
            prevloc = (0, 0, 0, 0)
            count   = 0

            seed(rnd_seed := randint(0, 2**32-1))
            # seed(643622660)

            # for p in [fst.child_path(f) for f in fst.walk(True, self_=False)]:
            #     f = fst.child_from_path(p)
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

                    # sys.stdout.write('\x08' * 32 + f'{tuple(f.loc)}'.ljust(32)); sys.stdout.flush()
                    # if f.loc[0] < prevloc[0]: print('<', tuple(prevloc))
                    # prevloc = f.loc


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
                                        try: f.put(None, i, field=subfield, raw=False)
                                        except Exception as e:
                                            if 'in this state' not in str(e): raise
                                        if self.verify: fst.verify()
                                        # elif VERIFY_DEL: fst.verify()

                                    f.put(child, i, field=subfield, raw=False)

                    if changed:
                        fst.verify()


                    # NODES

                    delete = self.DELETE and handler in (_put_one_exprish_optional, _put_one_Dict_keys,
                                                         _put_one_withitem_optional_vars)

                    # if not delete: continue

                    # print('...', g, g.src)
                    # f.parent.dump(True); print(f.parent.src); print()

                    if delete:
                        put = 'del'
                        try: f.parent.put(None, idx, field=field, raw=False)
                        except Exception as e:
                            if not str(e).endswith('in this state'): raise
                        # f.parent.dump(True); print(f.parent.src); print()
                        if self.verify: fst.verify()
                        # elif VERIFY_DEL: fst.verify()

                    put = 'fst'
                    f.parent.put(g, idx, field=field, raw=False)
                    # f.parent.dump(True); print(f.parent.src); print()
                    if self.verify: fst.verify()

                    # if delete:
                    #     try: f.parent.put(None, idx, field=field, raw=False)
                    #     except Exception: pass

                    put = 'ast'
                    f.parent.put(ast, idx, field=field, raw=False)
                    # f.parent.dump(True); print(f.parent.src); print()
                    if self.verify: fst.verify()

                    # if delete:
                    #     try: f.parent.put(None, idx, field=field, raw=False)
                    #     except Exception: pass

                    put = 'src'
                    f.parent.put(src, idx, field=field, raw=False)
                    # f.parent.dump(True); print(f.parent.src); print()
                    if self.verify: fst.verify()

                except:
                    print('\nRandom seed was:', rnd_seed)
                    print(sig, put, fst.child_path(f, True), idx, field, f.parent)
                    print(f)
                    print(f.src)
                    print(g)
                    print(g.src)

                    raise


            sys.stdout.write('\n')

            fst.verify()

            for ast in (fst.a, backup.a):  # zero out docstrings because indentation may have changed for docstrings which do not respect their own indentation level
                for a in walk(ast):
                    if isinstance(a, Constant) and isinstance(a.value, str) and (p := (f := a.f).parent) and isinstance(p.a, Expr):
                        a.value = ''
            compare_asts(fst.a, backup.a, raise_=True)

            print(fst.src)


FUZZERS = {o.name: o for o in globals().values() if isinstance(o, type) and o is not Fuzzy and issubclass(o, Fuzzy)}


def main():
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=f'Available fuzzers: {", ".join(FUZZERS)}'
    )

    parser.add_argument('PATH', nargs='*',
                        help='path of file or directory of files to use')
    parser.add_argument('-f', '--fuzz', action='append', default=[],
                        help='which fuzzers to run')
    parser.add_argument('-s', '--shuffle', default=False, action='store_true',
                        help='shuffle files on each loop')
    parser.add_argument('-l', '--loop', type=int, default=None,
                        help='number of times to loop')
    parser.add_argument('-b', '--batch', type=int, default=None,
                        help='batch size')
    parser.add_argument('-v', '--verify', default=False, action='store_true',
                        help='verify after everything (slower)')

    args = parser.parse_args()
    fuzz = dict.fromkeys(sum((f.replace(',', ' ').split() for f in args.fuzz), start=[]) if args.fuzz else FUZZERS)

    print(args)

    if any((fuzzer := f) not in FUZZERS for f in fuzz):
        raise ValueError(f'invalid fuzzer: {fuzzer}')

    fuzzers = []
    args    = vars(args)

    for f in fuzz:
        fuzzers.append(FUZZERS[f](args))

    for _ in range(l) if (l := args['loop']) else repeat(None):
        still_going = 0

        for f in fuzzers:
            print(f'Running: {f.name}')

            still_going += bool(f.fuzz())

        if not still_going:
            print('Done...')

            break


if __name__ == '__main__':
    main()
