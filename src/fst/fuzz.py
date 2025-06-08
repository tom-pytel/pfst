import argparse
import os
import sys
import sysconfig
from ast import *
from itertools import repeat
from random import shuffle
from typing import Any, Generator

from .astutil import TemplateStr, Interpolation
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
        self.args = args

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
