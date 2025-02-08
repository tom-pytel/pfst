#!/usr/bin/env python

import os
import ast as ast_
from fst.util import *
from fst import *



a = parse('class cls:\n @deco\n def f(self):\n  """ this\n  """\n  that')

print(a.body[0].body[0].body[1].f._get_preceding_lineends(5))



# PYFNMS = sum((
#     [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
#     for top in ('src', 'tests')),
#     start=[]
# )
with open('../pys14.txt') as f:
# with open('../pys10.txt') as f:
    PYFNMS = [s for s in f.read().split('\n') if s]

def read(fnm):
    with open(fnm) as f:
        return f.read()

empties = set()

for fnm in PYFNMS:
    if fnm.endswith('module_koi8_r.py') or fnm.endswith('module_iso_8859_1.py') or fnm.endswith('bad_coding.py') or fnm.endswith('bad_coding2.py'):  # weirdass encodings
        continue
    if fnm.endswith('badsyntax_3131.py') or fnm.endswith('badsyntax_pep3120.py'):
        continue

    print(fnm)

    ast = FST.from_src(read(fnm)).a

    for a in walk(ast):
        if a.f.loc is None:
            empties.add(a.__class__.__name__)

    print(sorted(empties))



f = parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f

print((1, 7, 1, 24), f.loc)

f = parse('with f() as f: pass').body[0].items[0].f

print((0, 5, 0, 13), f.loc)



from timeit import timeit

with open('src/fst/fst.py') as f:
    src = f.read()

fst = FST.from_src(src)

print(fst.a.body[-1])
print(fst.a.body[-1].f._get_preceding_lineends(fst.a.body[-1].f.end_ln))

print(timeit('fst.a.body[-1].f._get_preceding_lineends(fst.a.body[-2].f.end_ln)', number=1, globals=globals()))
print(timeit('fst.a.body[-1].f.line_ast_ends', number=1, globals=globals()))


