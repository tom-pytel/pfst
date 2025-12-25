#!/usr/bin/env python

import os
import sys
import sysconfig
import unittest

from fst.astutil import *
from fst import *


_sanitize_filename_tbl = str.maketrans(' <>:;"\\|&?$*\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f/', '_' * 45)

def _sanitize_filename(fnm: str) -> str:
    return fnm.translate(_sanitize_filename_tbl)


def _find_pys(path) -> list[str]:
    fnms = []

    if os.path.isdir(path):
        for dir, _, fnms_ in os.walk(path):
            fnms.extend(os.path.join(dir, fnm) for fnm in fnms_ if fnm.endswith('.py'))

    return fnms


FNMS = []

FNMS.extend(_find_pys('src'))
FNMS.extend(_find_pys('tests'))
FNMS.extend(_find_pys(sys.prefix))

if stdlib := sysconfig.get_paths().get('stdlib'):
    FNMS.extend(_find_pys(stdlib))


RUN_SLOW = os.getenv("RUN_SLOW") == "1"

def slow_test(func):
    return unittest.skipUnless(RUN_SLOW, "slow test")(func)


class TestFSTBulk(unittest.TestCase):
    """Dynamically generated, these take a while to execute, set environment variable "RUN_SLOW=1" to run."""


if RUN_SLOW:
    for fnm in FNMS:
        if '/test/tokenizedata/badsyntax' in fnm or '/test/tokenizedata/bad_coding' in fnm:
            continue

        def _test_func(self, fnm=fnm):
            try:
                with open(fnm) as f:
                    src = f.read()

                fst_ = FST.fromsrc(src, 'exec', filename=fnm)

            except (UnicodeDecodeError, SyntaxError):  # we don't do special encodings yet and don't answer for aleady bad syntax in files
                return

            with self.subTest('fromast() == fromsrc()'):
                fst2 = FST.fromast(fst_.a, 'exec', filename=fnm)

                self.assertTrue(compare_asts(fst2.a, fst_.a))

            with self.subTest('walk() == step_fwd()'):
                g = fst_

                for f in fst_.walk(self_=False):
                    self.assertIs(f, g := g.step_fwd())

            with self.subTest('walk(back=True) == step_back()'):
                g = fst_

                for f in fst_.walk(self_=False, back=True):
                    self.assertIs(f, g := g.step_back())

            with self.subTest('self.replace(self.copy())'):
                g = fst_.copy()

                for f in (gen := g.walk(self_=False)):
                    # if f.is_stmtish or (n := f.pfield.name) == 'keywords' or (n == 'patterns' and f.is_MatchClass):
                    if f.is_stmtish or (f.pfield.name == 'patterns' and f.is_MatchClass):
                        continue

                    f.replace(f.copy())

                    if f.is_ftstr:
                        gen.send(False)

                g.verify()

            with self.subTest('self.replace(self.copy().src)'):
                g = fst_.copy()

                for f in (gen := g.walk(self_=False)):
                    # if f.is_stmtish or (n := f.pfield.name) == 'keywords' or (n == 'patterns' and f.is_MatchClass):
                    if f.is_stmtish or (f.pfield.name == 'patterns' and f.is_MatchClass):
                        continue

                    f.replace(f.copy().src)

                    if f.is_ftstr:
                        gen.send(False)

                g.verify()

            with self.subTest('self.replace(self.a)'):
                g = fst_.copy()

                for f in (gen := g.walk(self_=False)):
                    # if f.is_stmtish or (n := f.pfield.name) == 'keywords' or (n == 'patterns' and f.is_MatchClass):
                    if f.is_stmtish or (f.pfield.name == 'patterns' and f.is_MatchClass):
                        continue

                    f.replace(f.a)

                    if f.is_ftstr:
                        gen.send(False)

                g.verify()

        func_name = f'test_bulk_file_{_sanitize_filename(fnm)}'

        setattr(TestFSTBulk, func_name, _test_func)


if __name__ == '__main__':
    unittest.main()
