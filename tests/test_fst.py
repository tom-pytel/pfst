#!/usr/bin/env python

import os
import sys
import unittest
import ast as ast_
from random import randint, seed, shuffle

from fst import *
from fst import fst
fst_ = fst

PYFNMS = sum((
    [os.path.join(path, fnm) for path, _, fnms in os.walk(top) for fnm in fnms if fnm.endswith('.py')]
    for top in ('src', 'tests')),
    start=[]
)

PARS_DATA = [
(r"""
with ( f() ) as ( f ): pass
""", 'body[0].items[0].context_expr', r"""
( f() )
"""),

(r"""
with ( f() ) as ( f ): pass
""", 'body[0].items[0].optional_vars', r"""
( f )
"""),

(r"""
with ( f() ) as ( f ), ( g() ) as ( g ): pass
""", 'body[0].items[0].context_expr', r"""
( f() )
"""),

(r"""
with ( f() ) as ( f ), ( g() ) as ( g ): pass
""", 'body[0].items[0].optional_vars', r"""
( f )
"""),

(r"""
with ( f() ) as ( f ), ( g() ) as ( g ): pass
""", 'body[0].items[1].context_expr', r"""
( g() )
"""),

(r"""
with ( f() ) as ( f ), ( g() ) as ( g ): pass
""", 'body[0].items[1].optional_vars', r"""
( g )
"""),

(r"""
match a:
  case ( 2 ) if a == 1: pass
""", 'body[0].cases[0].pattern', r"""
( 2 )
"""),

(r"""
[ ( i ) for ( j ) in ( range(5) ) if ( k ) ]
""", 'body[0].value.elt', r"""
( i )
"""),

(r"""
[ ( i ) for ( j ) in ( range(5) ) if ( k ) ]
""", 'body[0].value.generators[0].target', r"""
( j )
"""),

(r"""
[ ( i ) for ( j ) in ( range(5) ) if ( k ) ]
""", 'body[0].value.generators[0].iter', r"""
( range(5) )
"""),

(r"""
[ ( i ) for ( j ) in ( range(5) ) if ( k ) ]
""", 'body[0].value.generators[0].ifs[0]', r"""
( k )
"""),

(r"""
( ( i ) for ( j ) in ( range(5) ) if ( k ) )
""", 'body[0].value.elt', r"""
( i )
"""),

(r"""
( ( i ) for ( j ) in ( range(5) ) if ( k ) )
""", 'body[0].value.generators[0].target', r"""
( j )
"""),

(r"""
( ( i ) for ( j ) in ( range(5) ) if ( k ) )
""", 'body[0].value.generators[0].iter', r"""
( range(5) )
"""),

(r"""
( ( i ) for ( j ) in ( range(5) ) if ( k ) )
""", 'body[0].value.generators[0].ifs[0]', r"""
( k )
"""),

(r"""
def f(a=(1)): pass
""", 'body[0].args.defaults[0]', r"""
(1)
"""),

(r"""
def f( a = ( 1 )): pass
""", 'body[0].args.defaults[0]', r"""
( 1 )
"""),

(r"""
lambda a = ( 1 ) : None
""", 'body[0].value.args.defaults[0]', r"""
( 1 )
"""),

(r"""
(1, ( 2 ), 3)
""", 'body[0].value.elts[1]', r"""
( 2 )
"""),

(r"""
(1),
""", 'body[0].value.elts[0]', r"""
(1)
"""),

(r"""
((1),)
""", 'body[0].value.elts[0]', r"""
(1)
"""),

(r"""
(1), ( 2 )
""", 'body[0].value.elts[0]', r"""
(1)
"""),

(r"""
(1), ( 2 )
""", 'body[0].value.elts[1]', r"""
( 2 )
"""),

(r"""
((1), ( 2 ))
""", 'body[0].value.elts[0]', r"""
(1)
"""),

(r"""
((1), ( 2 ))
""", 'body[0].value.elts[1]', r"""
( 2 )
"""),

(r"""
f(i for i in j)
""", 'body[0].value.args[0]', r"""
(i for i in j)
"""),

(r"""
f((i for i in j))
""", 'body[0].value.args[0]', r"""
(i for i in j)
"""),

(r"""
f(((i for i in j)))
""", 'body[0].value.args[0]', r"""
((i for i in j))
"""),

]  # END OF PARS_DATA

COPY_DATA = [
(r"""
opts.ignore_module = [mod.strip()
                      for i in opts.ignore_module for mod in i.split(',')]
""", 'body[0].value.generators[0].iter', r"""
opts.ignore_module
""", r"""
Attribute .. ROOT 0,0 -> 0,18
  .value Name 'opts' Load .. 0,0 -> 0,4
  .attr 'ignore_module'
  .ctx Load
"""),

]  # END OF COPY_DATA

GET_SLICE_SEQ_DATA = [
(r"""{1, 2}""", 'body[0].value', 0, 0, {}, r"""
{1, 2}
""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,6
  .body[1]
  0] Expr .. 0,0 -> 0,6
    .value Set .. 0,0 -> 0,6
      .elts[2]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 2 .. 0,4 -> 0,5
""", r"""
Call .. ROOT 0,0 -> 0,5
  .func Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)""", 'body[0].value', None, None, {}, r"""
()
""", r"""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  2] Constant 3 .. 3,4 -> 3,5
  .ctx Load
"""),

(r"""(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)""", 'body[0].value', 0, 2, {}, r"""
(       # hello
    3,  # third line
)
""", r"""
(
    1,  # last line
    2,  # second line
)
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value Tuple .. 0,0 -> 2,1
      .elts[1]
      0] Constant 3 .. 1,4 -> 1,5
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 3,1
  .elts[2]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  .ctx Load
"""),

(r"""(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)""", 'body[0].value', 1, 2, {}, r"""
(       # hello
    1,  # last line
    3,  # third line
)
""", r"""
(
    2,  # second line
)
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value Tuple .. 0,0 -> 3,1
      .elts[2]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 3 .. 2,4 -> 2,5
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 1,4 -> 1,5
  .ctx Load
"""),

(r"""(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)""", 'body[0].value', 2, None, {}, r"""
(       # hello
    1,  # last line
    2,  # second line
)
""", r"""
(
    3,  # third line
)
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value Tuple .. 0,0 -> 3,1
      .elts[2]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 2 .. 2,4 -> 2,5
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 3 .. 1,4 -> 1,5
  .ctx Load
"""),

(r"""(           # hello
    1, 2, 3 # last line
)""", 'body[0].value', None, None, {}, r"""
()
""", r"""
(           # hello
    1, 2, 3 # last line
)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 1,7 -> 1,8
  2] Constant 3 .. 1,10 -> 1,11
  .ctx Load
"""),

(r"""(           # hello
    1, 2, 3 # last line
)""", 'body[0].value', 0, 2, {}, r"""
(           # hello
    3, # last line
)
""", r"""
(
    1, 2)
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value Tuple .. 0,0 -> 2,1
      .elts[1]
      0] Constant 3 .. 1,4 -> 1,5
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 1,9
  .elts[2]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 1,7 -> 1,8
  .ctx Load
"""),

(r"""(           # hello
    1, 2, 3 # last line
)""", 'body[0].value', 1, 2, {}, r"""
(           # hello
    1, 3 # last line
)
""", r"""
(2,)
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value Tuple .. 0,0 -> 2,1
      .elts[2]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""(           # hello
    1, 2, 3 # last line
)""", 'body[0].value', 2, None, {}, r"""
(           # hello
    1, 2)
""", r"""
(3, # last line
)
""", r"""
Module .. ROOT 0,0 -> 1,9
  .body[1]
  0] Expr .. 0,0 -> 1,9
    .value Tuple .. 0,0 -> 1,9
      .elts[2]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 1,1
  .elts[1]
  0] Constant 3 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', 1, 3, {}, r"""
1, 4
""", r"""
(2, 3)
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value Tuple .. 0,0 -> 0,4
      .elts[2]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 4 .. 0,3 -> 0,4
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant 2 .. 0,1 -> 0,2
  1] Constant 3 .. 0,4 -> 0,5
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', -1, None, {}, r"""
1, 2, 3
""", r"""
(4,)
""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value Tuple .. 0,0 -> 0,7
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant 4 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', None, None, {}, r"""
()
""", r"""
(1, 2, 3, 4)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,12
  .elts[4]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
  2] Constant 3 .. 0,7 -> 0,8
  3] Constant 4 .. 0,10 -> 0,11
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', 1, 1, {}, r"""
1, 2, 3, 4
""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] Expr .. 0,0 -> 0,10
    .value Tuple .. 0,0 -> 0,10
      .elts[4]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      3] Constant 4 .. 0,9 -> 0,10
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,2
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', 1, None, {}, r"""
1,
""", r"""
(2, 3, 4)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Constant 1 .. 0,0 -> 0,1
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,9
  .elts[3]
  0] Constant 2 .. 0,1 -> 0,2
  1] Constant 3 .. 0,4 -> 0,5
  2] Constant 4 .. 0,7 -> 0,8
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', 0, 3, {}, r"""
4,
""", r"""
(1, 2, 3)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Constant 4 .. 0,0 -> 0,1
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,9
  .elts[3]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
  2] Constant 3 .. 0,7 -> 0,8
  .ctx Load
"""),

(r"""(1, 2
  ,  # comment
3, 4)""", 'body[0].value', 1, 2, {}, r"""
(1, 3, 4)
""", r"""
(2
  ,  # comment
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Tuple .. 0,0 -> 0,9
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 3 .. 0,4 -> 0,5
      2] Constant 4 .. 0,7 -> 0,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""(1, 2
  ,
  3, 4)""", 'body[0].value', 1, 2, {}, r"""
(1, 3, 4)
""", r"""
(2
  ,
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Tuple .. 0,0 -> 0,9
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 3 .. 0,4 -> 0,5
      2] Constant 4 .. 0,7 -> 0,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""(1, 2 \
  , \
  3, 4)""", 'body[0].value', 1, 2, {}, r"""
(1, 3, 4)
""", r"""
(2 \
  , \
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Tuple .. 0,0 -> 0,9
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 3 .. 0,4 -> 0,5
      2] Constant 4 .. 0,7 -> 0,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""(1, 2  # comment
  , \
  3, 4)""", 'body[0].value', 1, 2, {}, r"""
(1, 3, 4)
""", r"""
(2  # comment
  , \
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Tuple .. 0,0 -> 0,9
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 3 .. 0,4 -> 0,5
      2] Constant 4 .. 0,7 -> 0,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""(1, 2
  ,
3, 4)""", 'body[0].value', 1, 2, {}, r"""
(1, 3, 4)
""", r"""
(2
  ,
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Tuple .. 0,0 -> 0,9
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 3 .. 0,4 -> 0,5
      2] Constant 4 .. 0,7 -> 0,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""(1, 2
  , 3, 4)""", 'body[0].value', 1, 2, {}, r"""
(1, 3, 4)
""", r"""
(2
  ,)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Tuple .. 0,0 -> 0,9
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 3 .. 0,4 -> 0,5
      2] Constant 4 .. 0,7 -> 0,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 1,4
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""(1, 2  # comment
  , 3, 4)""", 'body[0].value', 1, 2, {}, r"""
(1, 3, 4)
""", r"""
(2  # comment
  ,)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Tuple .. 0,0 -> 0,9
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 3 .. 0,4 -> 0,5
      2] Constant 4 .. 0,7 -> 0,8
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 1,4
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )""", 'body[0].body[0].value', None, None, {}, r"""
if 1:
    ()
""", r"""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", r"""
Module .. ROOT 0,0 -> 1,6
  .body[1]
  0] If .. 0,0 -> 1,6
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 1,6
      .value Tuple .. 1,4 -> 1,6
        .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  2] Constant 3 .. 3,4 -> 3,5
  .ctx Load
"""),

(r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )""", 'body[0].body[0].value', 0, 2, {}, r"""
if 1:
    (       # hello
        3,  # third line
    )
""", r"""
(
    1,  # last line
    2,  # second line
)
""", r"""
Module .. ROOT 0,0 -> 3,5
  .body[1]
  0] If .. 0,0 -> 3,5
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 3,5
      .value Tuple .. 1,4 -> 3,5
        .elts[1]
        0] Constant 3 .. 2,8 -> 2,9
        .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 3,1
  .elts[2]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  .ctx Load
"""),

(r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )""", 'body[0].body[0].value', 1, 2, {}, r"""
if 1:
    (       # hello
        1,  # last line
        3,  # third line
    )
""", r"""
(
    2,  # second line
)
""", r"""
Module .. ROOT 0,0 -> 4,5
  .body[1]
  0] If .. 0,0 -> 4,5
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 4,5
      .value Tuple .. 1,4 -> 4,5
        .elts[2]
        0] Constant 1 .. 2,8 -> 2,9
        1] Constant 3 .. 3,8 -> 3,9
        .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 1,4 -> 1,5
  .ctx Load
"""),

(r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )""", 'body[0].body[0].value', 2, None, {}, r"""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
    )
""", r"""
(
    3,  # third line
)
""", r"""
Module .. ROOT 0,0 -> 4,5
  .body[1]
  0] If .. 0,0 -> 4,5
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 4,5
      .value Tuple .. 1,4 -> 4,5
        .elts[2]
        0] Constant 1 .. 2,8 -> 2,9
        1] Constant 2 .. 3,8 -> 3,9
        .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 3 .. 1,4 -> 1,5
  .ctx Load
"""),

(r"""{1: 2, **b, **c}""", 'body[0].value', 1, 2, {}, r"""
{1: 2, **c}
""", r"""
{**b}
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value Dict .. 0,0 -> 0,11
      .keys[2]
      0] Constant 1 .. 0,1 -> 0,2
      1] None
      .values[2]
      0] Constant 2 .. 0,4 -> 0,5
      1] Name 'c' Load .. 0,9 -> 0,10
""", r"""
Dict .. ROOT 0,0 -> 0,5
  .keys[1]
  0] None
  .values[1]
  0] Name 'b' Load .. 0,3 -> 0,4
"""),

(r"""{1: 2, **b, **c}""", 'body[0].value', None, None, {}, r"""
{}
""", r"""
{1: 2, **b, **c}
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Dict .. 0,0 -> 0,2
""", r"""
Dict .. ROOT 0,0 -> 0,16
  .keys[3]
  0] Constant 1 .. 0,1 -> 0,2
  1] None
  2] None
  .values[3]
  0] Constant 2 .. 0,4 -> 0,5
  1] Name 'b' Load .. 0,9 -> 0,10
  2] Name 'c' Load .. 0,14 -> 0,15
"""),

(r"""{1: 2, **b, **c}""", 'body[0].value', 2, None, {}, r"""
{1: 2, **b}
""", r"""
{**c}
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value Dict .. 0,0 -> 0,11
      .keys[2]
      0] Constant 1 .. 0,1 -> 0,2
      1] None
      .values[2]
      0] Constant 2 .. 0,4 -> 0,5
      1] Name 'b' Load .. 0,9 -> 0,10
""", r"""
Dict .. ROOT 0,0 -> 0,5
  .keys[1]
  0] None
  .values[1]
  0] Name 'c' Load .. 0,3 -> 0,4
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', None, None, {}, r"""
[]
""", r"""
[
    1,
    2,
    3,
]
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value List .. 0,0 -> 0,2
      .ctx Load
""", r"""
List .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  2] Constant 3 .. 3,4 -> 3,5
  .ctx Load
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', 0, 2, {}, r"""
[
    3,
]
""", r"""
[
    1,
    2,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[1]
      0] Constant 3 .. 1,4 -> 1,5
      .ctx Load
""", r"""
List .. ROOT 0,0 -> 3,1
  .elts[2]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  .ctx Load
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', 1, 2, {}, r"""
[
    1,
    3,
]
""", r"""
[
    2,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[2]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 3 .. 2,4 -> 2,5
      .ctx Load
""", r"""
List .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 2 .. 1,4 -> 1,5
  .ctx Load
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', 2, None, {}, r"""
[
    1,
    2,
]
""", r"""
[
    3,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[2]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 2 .. 2,4 -> 2,5
      .ctx Load
""", r"""
List .. ROOT 0,0 -> 2,1
  .elts[1]
  0] Constant 3 .. 1,4 -> 1,5
  .ctx Load
"""),

(r"""[            # hello
    1, 2, 3,
    4
]""", 'body[0].value', 2, 3, {}, r"""
[            # hello
    1, 2, 4
]
""", r"""
[3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Constant 4 .. 1,10 -> 1,11
      .ctx Load
""", r"""
List .. ROOT 0,0 -> 1,1
  .elts[1]
  0] Constant 3 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""[            # hello
    1, 2, ( 3
     ), 4
]""", 'body[0].value', 2, 3, {}, r"""
[            # hello
    1, 2, 4
]
""", r"""
[( 3
     )]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Constant 4 .. 1,10 -> 1,11
      .ctx Load
""", r"""
List .. ROOT 0,0 -> 1,7
  .elts[1]
  0] Constant 3 .. 0,3 -> 0,4
  .ctx Load
"""),

(r"""[            # hello
    1, 2, ( 3
     ), 4
]""", 'body[0].value', 1, 3, {}, r"""
[            # hello
    1, 4
]
""", r"""
[2, ( 3
     )]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[2]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 4 .. 1,7 -> 1,8
      .ctx Load
""", r"""
List .. ROOT 0,0 -> 1,7
  .elts[2]
  0] Constant 2 .. 0,1 -> 0,2
  1] Constant 3 .. 0,6 -> 0,7
  .ctx Load
"""),

(r"""[            # hello
    1, 2, ( 3
     ), 4
]""", 'body[0].value', 1, None, {}, r"""
[            # hello
    1]
""", r"""
[2, ( 3
     ), 4
]
""", r"""
Module .. ROOT 0,0 -> 1,6
  .body[1]
  0] Expr .. 0,0 -> 1,6
    .value List .. 0,0 -> 1,6
      .elts[1]
      0] Constant 1 .. 1,4 -> 1,5
      .ctx Load
""", r"""
List .. ROOT 0,0 -> 2,1
  .elts[3]
  0] Constant 2 .. 0,1 -> 0,2
  1] Constant 3 .. 0,6 -> 0,7
  2] Constant 4 .. 1,8 -> 1,9
  .ctx Load
"""),

(r"""i =                (self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                id(self) & (_sys.maxsize*2 + 1))""", 'body[0].value', 0, 3, {}, r"""
i =                (id(self) & (_sys.maxsize*2 + 1),)
""", r"""
(self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
)
""", r"""
Module .. ROOT 0,0 -> 0,53
  .body[1]
  0] Assign .. 0,0 -> 0,53
    .targets[1]
    0] Name 'i' Store .. 0,0 -> 0,1
    .value Tuple .. 0,19 -> 0,53
      .elts[1]
      0] BinOp .. 0,20 -> 0,51
        .left Call .. 0,20 -> 0,28
          .func Name 'id' Load .. 0,20 -> 0,22
          .args[1]
          0] Name 'self' Load .. 0,23 -> 0,27
        .op BitAnd .. 0,29 -> 0,30
        .right BinOp .. 0,32 -> 0,50
          .left BinOp .. 0,32 -> 0,46
            .left Attribute .. 0,32 -> 0,44
              .value Name '_sys' Load .. 0,32 -> 0,36
              .attr 'maxsize'
              .ctx Load
            .op Mult .. 0,44 -> 0,45
            .right Constant 2 .. 0,45 -> 0,46
          .op Add .. 0,47 -> 0,48
          .right Constant 1 .. 0,49 -> 0,50
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[3]
  0] Attribute .. 0,1 -> 0,24
    .value Attribute .. 0,1 -> 0,15
      .value Name 'self' Load .. 0,1 -> 0,5
      .attr '__class__'
      .ctx Load
    .attr '__name__'
    .ctx Load
  1] Attribute .. 0,26 -> 0,36
    .value Name 'self' Load .. 0,26 -> 0,30
    .attr '_name'
    .ctx Load
  2] BinOp .. 1,17 -> 1,52
    .left Attribute .. 1,17 -> 1,29
      .value Name 'self' Load .. 1,17 -> 1,21
      .attr '_handle'
      .ctx Load
    .op BitAnd .. 1,30 -> 1,31
    .right BinOp .. 1,33 -> 1,51
      .left BinOp .. 1,33 -> 1,47
        .left Attribute .. 1,33 -> 1,45
          .value Name '_sys' Load .. 1,33 -> 1,37
          .attr 'maxsize'
          .ctx Load
        .op Mult .. 1,45 -> 1,46
        .right Constant 2 .. 1,46 -> 1,47
      .op Add .. 1,48 -> 1,49
      .right Constant 1 .. 1,50 -> 1,51
  .ctx Load
"""),

(r"""i = namespace = {**__main__.__builtins__.__dict__,
             **__main__.__dict__}""", 'body[0].value', 0, 1, {}, r"""
i = namespace = {**__main__.__dict__}
""", r"""
{**__main__.__builtins__.__dict__,
}
""", r"""
Module .. ROOT 0,0 -> 0,37
  .body[1]
  0] Assign .. 0,0 -> 0,37
    .targets[2]
    0] Name 'i' Store .. 0,0 -> 0,1
    1] Name 'namespace' Store .. 0,4 -> 0,13
    .value Dict .. 0,16 -> 0,37
      .keys[1]
      0] None
      .values[1]
      0] Attribute .. 0,19 -> 0,36
        .value Name '__main__' Load .. 0,19 -> 0,27
        .attr '__dict__'
        .ctx Load
""", r"""
Dict .. ROOT 0,0 -> 1,1
  .keys[1]
  0] None
  .values[1]
  0] Attribute .. 0,3 -> 0,33
    .value Attribute .. 0,3 -> 0,24
      .value Name '__main__' Load .. 0,3 -> 0,11
      .attr '__builtins__'
      .ctx Load
    .attr '__dict__'
    .ctx Load
"""),

(r"""env = {
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1",
    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}""", 'body[0].value', None, 2, {}, r"""
env = {
    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}
""", r"""
{
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1",
}
""", r"""
Module .. ROOT 0,0 -> 4,1
  .body[1]
  0] Assign .. 0,0 -> 4,1
    .targets[1]
    0] Name 'env' Store .. 0,0 -> 0,3
    .value Dict .. 0,6 -> 4,1
      .keys[3]
      0] Constant 'PYLAUNCHER_DRYRUN' .. 1,4 -> 1,23
      1] Constant 'PYLAUNCHER_LIMIT_TO_COMPANY' .. 2,4 -> 2,33
      2] None
      .values[3]
      0] Constant '1' .. 1,25 -> 1,28
      1] Constant '' .. 2,35 -> 2,37
      2] DictComp .. 3,6 -> 3,52
        .key Call .. 3,7 -> 3,16
          .func Attribute .. 3,7 -> 3,14
            .value Name 'k' Load .. 3,7 -> 3,8
            .attr 'upper'
            .ctx Load
        .value Name 'v' Load .. 3,18 -> 3,19
        .generators[1]
        0] comprehension .. 3,20 -> 3,51
          .target Tuple .. 3,24 -> 3,28
            .elts[2]
            0] Name 'k' Store .. 3,24 -> 3,25
            1] Name 'v' Store .. 3,27 -> 3,28
            .ctx Store
          .iter Call .. 3,32 -> 3,51
            .func Attribute .. 3,32 -> 3,49
              .value BoolOp .. 3,33 -> 3,42
                .op Or
                .values[2]
                0] Name 'env' Load .. 3,33 -> 3,36
                1] Dict .. 3,40 -> 3,42
              .attr 'items'
              .ctx Load
          .is_async 0
""", r"""
Dict .. ROOT 0,0 -> 3,1
  .keys[2]
  0] None
  1] Constant 'PYLAUNCHER_DEBUG' .. 2,4 -> 2,22
  .values[2]
  0] DictComp .. 1,6 -> 1,78
    .key Call .. 1,7 -> 1,16
      .func Attribute .. 1,7 -> 1,14
        .value Name 'k' Load .. 1,7 -> 1,8
        .attr 'upper'
        .ctx Load
    .value Name 'v' Load .. 1,18 -> 1,19
    .generators[1]
    0] comprehension .. 1,20 -> 1,77
      .target Tuple .. 1,24 -> 1,28
        .elts[2]
        0] Name 'k' Store .. 1,24 -> 1,25
        1] Name 'v' Store .. 1,27 -> 1,28
        .ctx Store
      .iter Call .. 1,32 -> 1,50
        .func Attribute .. 1,32 -> 1,48
          .value Attribute .. 1,32 -> 1,42
            .value Name 'os' Load .. 1,32 -> 1,34
            .attr 'environ'
            .ctx Load
          .attr 'items'
          .ctx Load
      .ifs[1]
      0] Compare .. 1,54 -> 1,77
        .left Call .. 1,54 -> 1,63
          .func Attribute .. 1,54 -> 1,61
            .value Name 'k' Load .. 1,54 -> 1,55
            .attr 'upper'
            .ctx Load
        .ops[1]
        0] NotIn .. 1,64 -> 1,70
        .comparators[1]
        0] Name 'ignore' Load .. 1,71 -> 1,77
      .is_async 0
  1] Constant '1' .. 2,24 -> 2,27
"""),

(r"""(None, False, True, 12345, 123.45, 'abcde', 'абвгд', b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})""", 'body[0].value', 5, 7, {}, r"""
(None, False, True, 12345, 123.45, b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
""", r"""
('abcde', 'абвгд')
""", r"""
Module .. ROOT 0,0 -> 2,67
  .body[1]
  0] Expr .. 0,0 -> 2,67
    .value Tuple .. 0,0 -> 2,67
      .elts[11]
      0] Constant None .. 0,1 -> 0,5
      1] Constant False .. 0,7 -> 0,12
      2] Constant True .. 0,14 -> 0,18
      3] Constant 12345 .. 0,20 -> 0,25
      4] Constant 123.45 .. 0,27 -> 0,33
      5] Constant b'abcde' .. 0,35 -> 0,43
      6] Call .. 1,12 -> 1,55
        .func Attribute .. 1,12 -> 1,29
          .value Name 'datetime' Load .. 1,12 -> 1,20
          .attr 'datetime'
          .ctx Load
        .args[6]
        0] Constant 2004 .. 1,30 -> 1,34
        1] Constant 10 .. 1,36 -> 1,38
        2] Constant 26 .. 1,40 -> 1,42
        3] Constant 10 .. 1,44 -> 1,46
        4] Constant 33 .. 1,48 -> 1,50
        5] Constant 33 .. 1,52 -> 1,54
      7] Call .. 2,12 -> 2,31
        .func Name 'bytearray' Load .. 2,12 -> 2,21
        .args[1]
        0] Constant b'abcde' .. 2,22 -> 2,30
      8] List .. 2,33 -> 2,42
        .elts[2]
        0] Constant 12 .. 2,34 -> 2,36
        1] Constant 345 .. 2,38 -> 2,41
        .ctx Load
      9] Tuple .. 2,44 -> 2,53
        .elts[2]
        0] Constant 12 .. 2,45 -> 2,47
        1] Constant 345 .. 2,49 -> 2,52
        .ctx Load
      10] Dict .. 2,55 -> 2,66
        .keys[1]
        0] Constant '12' .. 2,56 -> 2,60
        .values[1]
        0] Constant 345 .. 2,62 -> 2,65
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,18
  .elts[2]
  0] Constant 'abcde' .. 0,1 -> 0,8
  1] Constant 'абвгд' .. 0,10 -> 0,17
  .ctx Load
"""),

(r"""[a, b] = c""", 'body[0].targets[0]', 1, 2, {}, r"""
[a] = c
""", r"""
[b]
""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Assign .. 0,0 -> 0,7
    .targets[1]
    0] List .. 0,0 -> 0,3
      .elts[1]
      0] Name 'a' Store .. 0,1 -> 0,2
      .ctx Store
    .value Name 'c' Load .. 0,6 -> 0,7
""", r"""
List .. ROOT 0,0 -> 0,3
  .elts[1]
  0] Name 'b' Load .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""{
            'exception': exc,
            'future': fut,
            'message': ('GetQueuedCompletionStatus() returned an '
                        'unexpected event'),
            'status': ('err=%s transferred=%s key=%#x address=%#x'
                       % (err, transferred, key, address),),
                                                 'addr': address}""", 'body[0].value', 1, 4, {}, r"""
{
            'exception': exc,
                                                 'addr': address}
""", r"""
{
            'future': fut,
            'message': ('GetQueuedCompletionStatus() returned an '
                        'unexpected event'),
            'status': ('err=%s transferred=%s key=%#x address=%#x'
                       % (err, transferred, key, address),),
}
""", r"""
Module .. ROOT 0,0 -> 2,65
  .body[1]
  0] Expr .. 0,0 -> 2,65
    .value Dict .. 0,0 -> 2,65
      .keys[2]
      0] Constant 'exception' .. 1,12 -> 1,23
      1] Constant 'addr' .. 2,49 -> 2,55
      .values[2]
      0] Name 'exc' Load .. 1,25 -> 1,28
      1] Name 'address' Load .. 2,57 -> 2,64
""", r"""
Dict .. ROOT 0,0 -> 6,1
  .keys[3]
  0] Constant 'future' .. 1,12 -> 1,20
  1] Constant 'message' .. 2,12 -> 2,21
  2] Constant 'status' .. 4,12 -> 4,20
  .values[3]
  0] Name 'fut' Load .. 1,22 -> 1,25
  1] Constant 'GetQueuedCompletionStatus() returned an unexpected event' .. 2,24 -> 3,42
  2] Tuple .. 4,22 -> 5,59
    .elts[1]
    0] BinOp .. 4,23 -> 5,57
      .left Constant 'err=%s transferred=%s key=%#x address=%#x' .. 4,23 -> 4,66
      .op Mod .. 5,23 -> 5,24
      .right Tuple .. 5,25 -> 5,57
        .elts[4]
        0] Name 'err' Load .. 5,26 -> 5,29
        1] Name 'transferred' Load .. 5,31 -> 5,42
        2] Name 'key' Load .. 5,44 -> 5,47
        3] Name 'address' Load .. 5,49 -> 5,56
        .ctx Load
    .ctx Load
"""),

(r"""(1, (2), 3)""", 'body[0].value', 1, 2, {}, r"""
(1, 3)
""", r"""
((2),)
""", r"""
Module .. ROOT 0,0 -> 0,6
  .body[1]
  0] Expr .. 0,0 -> 0,6
    .value Tuple .. 0,0 -> 0,6
      .elts[2]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 3 .. 0,4 -> 0,5
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,6
  .elts[1]
  0] Constant 2 .. 0,2 -> 0,3
  .ctx Load
"""),

(r"""@patch.dict({'a': 'b'})
class cls: pass""", 'body[0].decorator_list[0].args[0]', 0, 1, {}, r"""
@patch.dict({})
class cls: pass
""", r"""
{'a': 'b'}
""", r"""
Module .. ROOT 0,0 -> 1,15
  .body[1]
  0] ClassDef .. 1,0 -> 1,15
    .name 'cls'
    .body[1]
    0] Pass .. 1,11 -> 1,15
    .decorator_list[1]
    0] Call .. 0,1 -> 0,15
      .func Attribute .. 0,1 -> 0,11
        .value Name 'patch' Load .. 0,1 -> 0,6
        .attr 'dict'
        .ctx Load
      .args[1]
      0] Dict .. 0,12 -> 0,14
""", r"""
Dict .. ROOT 0,0 -> 0,10
  .keys[1]
  0] Constant 'a' .. 0,1 -> 0,4
  .values[1]
  0] Constant 'b' .. 0,6 -> 0,9
"""),

(r"""class cls:
    a, b = c""", 'body[0].body[0].targets[0]', 0, 2, {}, r"""
class cls:
    () = c
""", r"""
(a, b)
""", r"""
Module .. ROOT 0,0 -> 1,10
  .body[1]
  0] ClassDef .. 0,0 -> 1,10
    .name 'cls'
    .body[1]
    0] Assign .. 1,4 -> 1,10
      .targets[1]
      0] Tuple .. 1,4 -> 1,6
        .ctx Store
      .value Name 'c' Load .. 1,9 -> 1,10
""", r"""
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Name 'a' Load .. 0,1 -> 0,2
  1] Name 'b' Load .. 0,4 -> 0,5
  .ctx Load
"""),

(r"""if 1:
    yy, tm, = tm, yy""", 'body[0].body[0].targets[0]', 1, 2, {}, r"""
if 1:
    yy, = tm, yy
""", r"""
(tm,)
""", r"""
Module .. ROOT 0,0 -> 1,16
  .body[1]
  0] If .. 0,0 -> 1,16
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Assign .. 1,4 -> 1,16
      .targets[1]
      0] Tuple .. 1,4 -> 1,7
        .elts[1]
        0] Name 'yy' Store .. 1,4 -> 1,6
        .ctx Store
      .value Tuple .. 1,10 -> 1,16
        .elts[2]
        0] Name 'tm' Load .. 1,10 -> 1,12
        1] Name 'yy' Load .. 1,14 -> 1,16
        .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,5
  .elts[1]
  0] Name 'tm' Load .. 0,1 -> 0,3
  .ctx Load
"""),

(r"""{1, 2}""", 'body[0].value', 0, 2, {}, r"""
set()
""", r"""
{1, 2}
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Call .. 0,0 -> 0,5
      .func Name 'set' Load .. 0,0 -> 0,3
""", r"""
Set .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
"""),

(r"""{1, 2}""", 'body[0].value', 0, 0, {}, r"""
{1, 2}
""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,6
  .body[1]
  0] Expr .. 0,0 -> 0,6
    .value Set .. 0,0 -> 0,6
      .elts[2]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 2 .. 0,4 -> 0,5
""", r"""
Call .. ROOT 0,0 -> 0,5
  .func Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""set()""", 'body[0].value', 0, 0, {}, r"""
set()
""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Call .. 0,0 -> 0,5
      .func Name 'set' Load .. 0,0 -> 0,3
""", r"""
Call .. ROOT 0,0 -> 0,5
  .func Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 1, {}, r"""
2, 3,
""", r"""
(1,)
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[2]
      0] Constant 2 .. 0,0 -> 0,1
      1] Constant 3 .. 0,3 -> 0,4
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant 1 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 2, {}, r"""
1, 3,
""", r"""
(2,)
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[2]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 3 .. 0,3 -> 0,4
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant 2 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 3, {}, r"""
1, 2,
""", r"""
(3,)
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[2]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,4
  .elts[1]
  0] Constant 3 .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 2, {}, r"""
3,
""", r"""
(1, 2)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Constant 3 .. 0,0 -> 0,1
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 3, {}, r"""
1,
""", r"""
(2, 3)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Constant 1 .. 0,0 -> 0,1
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant 2 .. 0,1 -> 0,2
  1] Constant 3 .. 0,4 -> 0,5
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 3, {}, r"""
()
""", r"""
(1, 2, 3,)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,10
  .elts[3]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
  2] Constant 3 .. 0,7 -> 0,8
  .ctx Load
"""),

]  # END OF GET_SLICE_SEQ_DATA

GET_SLICE_STMT_DATA = [
(r"""
if 1:
    i
    # pre
    j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j ;
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j ; # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    # post
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j ; \
  k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j ; \
\
  k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j \
    ; \
\
  k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j \
    ; \
  k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j \
    ; k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i ; j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j  # post
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
  ; j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; \
  j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
  ; \
  j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j ; k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i ; k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,9
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 2,8 -> 2,9
      .value Name 'k' Load .. 2,8 -> 2,9
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1:
    i  # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j \
    # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i \
    # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; \
  j \
    # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i \
    # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
  ; \
  j \
    # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i \
    # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; \
    j  # post
    if 2: pass
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    if 2: pass
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    ; j  # post
    if 2: pass
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    if 2: pass
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    ; \
    j  # post
    if 2: pass
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    if 2: pass
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; \
    j
    if 2: pass
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    if 2: pass
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    ; j
    if 1: pass
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    if 1: pass
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test Constant 1 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    ; \
    j
    if 2: pass
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    if 2: pass
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1:
    i
    # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    \
    j
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i

    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j \

    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    \

    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'k' Load .. 5,4 -> 5,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j ;
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j ; \
  k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j \
  ;
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j \
  ; \
  k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass
else: \
  i ; j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""
if 1: pass
else:
  j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,3
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 3,2 -> 3,3
      .value Name 'j' Load .. 3,2 -> 3,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass
else: \
  i ; \
    j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""
if 1: pass
else:
    j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass
else: \
  i \
 ; \
    j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""
if 1: pass
else:
    j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass
else: i ; j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""
if 1: pass
else: j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,7
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 2,6 -> 2,7
      .value Name 'j' Load .. 2,6 -> 2,7
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""if 1: pass
else: \
  i ; j""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""if 1: pass
else:
  j""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,3
  .body[1]
  0] If .. 0,0 -> 2,3
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Pass .. 0,6 -> 0,10
    .orelse[1]
    0] Expr .. 2,2 -> 2,3
      .value Name 'j' Load .. 2,2 -> 2,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""if 1: pass
else: \
  i ; \
    j""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""if 1: pass
else:
    j""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,5
  .body[1]
  0] If .. 0,0 -> 2,5
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Pass .. 0,6 -> 0,10
    .orelse[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'j' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""if 1: pass
else:
  i \
 ; \
    j""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""if 1: pass
else:
  j""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,3
  .body[1]
  0] If .. 0,0 -> 2,3
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Pass .. 0,6 -> 0,10
    .orelse[1]
    0] Expr .. 2,2 -> 2,3
      .value Name 'j' Load .. 2,2 -> 2,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""if 1: pass
else: i ; j""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""if 1: pass
else: j""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,7
  .body[1]
  0] If .. 0,0 -> 1,7
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Pass .. 0,6 -> 0,10
    .orelse[1]
    0] Expr .. 1,6 -> 1,7
      .value Name 'j' Load .. 1,6 -> 1,7
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    # pre
    j
    if 2: pass
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    if 2: pass
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i \
    # pre
    j  # post
    if 2: pass
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    if 2: pass
""", r"""# pre
j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
  \
  i
  if 2: pass
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:

  if 2: pass
""", r"""i""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,12
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] If .. 3,2 -> 3,12
      .test Constant 2 .. 3,5 -> 3,6
      .body[1]
      0] Pass .. 3,8 -> 3,12
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    \
    j
    k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i

    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: \
    i; j
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'j' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    # pre
    j ; k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
class cls:
    i
    \




    def f(): pass
    j
""", 'body[0]', 1, 2, None, {'prespace': 1}, r"""
class cls:
    i
    \



    j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,5
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 7,4 -> 7,5
      .value Name 'j' Load .. 7,4 -> 7,5
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""
class cls:
    i
    \




    def f(): pass
    j
""", 'body[0]', 1, 2, None, {'pep8space': True}, r"""
class cls:
    i
    \



    j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,5
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 7,4 -> 7,5
      .value Name 'j' Load .. 7,4 -> 7,5
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, {'pep8space': True}, r"""
i
\


j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 5,0 -> 5,1
    .value Name 'j' Load .. 5,0 -> 5,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, {'pep8space': True, 'prespace': 3}, r"""
i
\

j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value Name 'j' Load .. 4,0 -> 4,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, {'pep8space': True, 'prespace': 4}, r"""
i

j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 3,0 -> 3,1
    .value Name 'j' Load .. 3,0 -> 3,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, {'pep8space': True, 'prespace': 5}, r"""
i
j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, {'pep8space': True, 'prespace': 6}, r"""
i
j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""
i
\



# pre
def f(): pass
j
""", '', 1, 2, None, {'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': 1}, r"""
i
\


j
""", r"""# pre
def f(): pass""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 5,0 -> 5,1
    .value Name 'j' Load .. 5,0 -> 5,1
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] FunctionDef .. 1,0 -> 1,13
    .name 'f'
    .body[1]
    0] Pass .. 1,9 -> 1,13
"""),

(r"""
i
# pre
@deco1
@deco2
class cls:
  pass  # post
j
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
i
# pre
# post
j
""", r"""@deco1
@deco2
class cls:
  pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value Name 'j' Load .. 4,0 -> 4,1
""", r"""
Module .. ROOT 0,0 -> 3,6
  .body[1]
  0] ClassDef .. 2,0 -> 3,6
    .name 'cls'
    .body[1]
    0] Pass .. 3,2 -> 3,6
    .decorator_list[2]
    0] Name 'deco1' Load .. 0,1 -> 0,6
    1] Name 'deco2' Load .. 1,1 -> 1,6
"""),

(r"""
i
# pre
@deco1
@deco2(a, b)
class cls:
  pass  # post
j
""", '', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
i
j
""", r"""# pre
@deco1
@deco2(a, b)
class cls:
  pass  # post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 3,0 -> 4,6
    .name 'cls'
    .body[1]
    0] Pass .. 4,2 -> 4,6
    .decorator_list[2]
    0] Name 'deco1' Load .. 1,1 -> 1,6
    1] Call .. 2,1 -> 2,12
      .func Name 'deco2' Load .. 2,1 -> 2,6
      .args[2]
      0] Name 'a' Load .. 2,7 -> 2,8
      1] Name 'b' Load .. 2,10 -> 2,11
"""),

(r"""
def func0():
    pass


def func1():
    break


continue
""", '', 0, 1, None, {'pep8space': True}, r"""
def func1():
    break


continue
""", r"""def func0():
    pass""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] FunctionDef .. 1,0 -> 2,9
    .name 'func1'
    .body[1]
    0] Break .. 2,4 -> 2,9
  1] Continue .. 5,0 -> 5,8
""", r"""
Module .. ROOT 0,0 -> 1,8
  .body[1]
  0] FunctionDef .. 0,0 -> 1,8
    .name 'func0'
    .body[1]
    0] Pass .. 1,4 -> 1,8
"""),

(r"""
def func0():
    pass


def func1():
    break


continue
""", '', 1, 2, None, {'pep8space': True}, r"""
def func0():
    pass


continue
""", r"""def func1():
    break""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] FunctionDef .. 1,0 -> 2,8
    .name 'func0'
    .body[1]
    0] Pass .. 2,4 -> 2,8
  1] Continue .. 5,0 -> 5,8
""", r"""
Module .. ROOT 0,0 -> 1,9
  .body[1]
  0] FunctionDef .. 0,0 -> 1,9
    .name 'func1'
    .body[1]
    0] Break .. 1,4 -> 1,9
"""),

(r"""
def func0():
    pass


def func1():
    break


continue
""", '', 0, 1, None, {'pep8space': 1}, r"""

def func1():
    break


continue
""", r"""def func0():
    pass""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[2]
  0] FunctionDef .. 2,0 -> 3,9
    .name 'func1'
    .body[1]
    0] Break .. 3,4 -> 3,9
  1] Continue .. 6,0 -> 6,8
""", r"""
Module .. ROOT 0,0 -> 1,8
  .body[1]
  0] FunctionDef .. 0,0 -> 1,8
    .name 'func0'
    .body[1]
    0] Pass .. 1,4 -> 1,8
"""),

(r"""
def func0():
    pass


def func1():
    break


continue
""", '', 1, 2, None, {'pep8space': 1}, r"""
def func0():
    pass



continue
""", r"""def func1():
    break""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[2]
  0] FunctionDef .. 1,0 -> 2,8
    .name 'func0'
    .body[1]
    0] Pass .. 2,4 -> 2,8
  1] Continue .. 6,0 -> 6,8
""", r"""
Module .. ROOT 0,0 -> 1,9
  .body[1]
  0] FunctionDef .. 0,0 -> 1,9
    .name 'func1'
    .body[1]
    0] Break .. 1,4 -> 1,9
"""),

(r"""
class cls:
    def meth0():
        pass

    def meth1():
        break

continue
""", 'body[0]', 0, 1, None, {'pep8space': True}, r"""
class cls:
    def meth1():
        break

continue
""", r"""def meth0():
    pass""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] ClassDef .. 1,0 -> 3,13
    .name 'cls'
    .body[1]
    0] FunctionDef .. 2,4 -> 3,13
      .name 'meth1'
      .body[1]
      0] Break .. 3,8 -> 3,13
  1] Continue .. 5,0 -> 5,8
""", r"""
Module .. ROOT 0,0 -> 1,8
  .body[1]
  0] FunctionDef .. 0,0 -> 1,8
    .name 'meth0'
    .body[1]
    0] Pass .. 1,4 -> 1,8
"""),

(r"""
class cls:
    def meth0():
        pass

    def meth1():
        break

continue
""", 'body[0]', 1, 2, None, {'pep8space': True}, r"""
class cls:
    def meth0():
        pass

continue
""", r"""def meth1():
    break""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] ClassDef .. 1,0 -> 3,12
    .name 'cls'
    .body[1]
    0] FunctionDef .. 2,4 -> 3,12
      .name 'meth0'
      .body[1]
      0] Pass .. 3,8 -> 3,12
  1] Continue .. 5,0 -> 5,8
""", r"""
Module .. ROOT 0,0 -> 1,9
  .body[1]
  0] FunctionDef .. 0,0 -> 1,9
    .name 'meth1'
    .body[1]
    0] Break .. 1,4 -> 1,9
"""),

(r"""
if 1:
    i ; j



""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1:
    i



""", r"""j""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j



""", 'body[0]', 1, 2, None, {'postspace': 1}, r"""
if 1:
    i


""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j



""", 'body[0]', 1, 2, None, {'postspace': True}, r"""
if 1:
    i
""", r"""j""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j



""", 'body[0]', 0, 1, None, {'postspace': True}, r"""
if 1:
    j



""", r"""i""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'j' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
def f():
    i ; j



""", '', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""



""", r"""def f():
    i ; j""", r"""
Module .. ROOT 0,0 -> 4,0
""", r"""
Module .. ROOT 0,0 -> 1,9
  .body[1]
  0] FunctionDef .. 0,0 -> 1,9
    .name 'f'
    .body[2]
    0] Expr .. 1,4 -> 1,5
      .value Name 'i' Load .. 1,4 -> 1,5
    1] Expr .. 1,8 -> 1,9
      .value Name 'j' Load .. 1,8 -> 1,9
"""),

(r"""
def f():
    i ; j



""", '', 0, 1, None, {'postspace': True}, r"""
""", r"""def f():
    i ; j""", r"""
Module .. ROOT 0,0 -> 1,0
""", r"""
Module .. ROOT 0,0 -> 1,9
  .body[1]
  0] FunctionDef .. 0,0 -> 1,9
    .name 'f'
    .body[2]
    0] Expr .. 1,4 -> 1,5
      .value Name 'i' Load .. 1,4 -> 1,5
    1] Expr .. 1,8 -> 1,9
      .value Name 'j' Load .. 1,8 -> 1,9
"""),

(r"""
def f():
    i
    \
  k
""", 'body[0]', 0, 1, None, {'postspace': True}, r"""
def f():
    \
  k
""", r"""i""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 1,0 -> 3,3
    .name 'f'
    .body[1]
    0] Expr .. 3,2 -> 3,3
      .value Name 'k' Load .. 3,2 -> 3,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
def f():
    i; j
    \
  k
""", 'body[0]', 1, 2, None, {'postspace': True}, r"""
def f():
    i
    \
  k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] FunctionDef .. 1,0 -> 4,3
    .name 'f'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,2 -> 4,3
      .value Name 'k' Load .. 4,2 -> 4,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
def f():
    i

    \
  k
""", 'body[0]', 0, 1, None, {'postspace': True}, r"""
def f():
    \
  k
""", r"""i""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 1,0 -> 3,3
    .name 'f'
    .body[1]
    0] Expr .. 3,2 -> 3,3
      .value Name 'k' Load .. 3,2 -> 3,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
def f():
    i; j

    \
  k
""", 'body[0]', 1, 2, None, {'postspace': True}, r"""
def f():
    i
    \
  k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] FunctionDef .. 1,0 -> 4,3
    .name 'f'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,2 -> 4,3
      .value Name 'k' Load .. 4,2 -> 4,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
def f():
    i
    \

    k
""", 'body[0]', 0, 1, None, {'postspace': True}, r"""
def f():
    \

    k
""", r"""i""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] FunctionDef .. 1,0 -> 4,5
    .name 'f'
    .body[1]
    0] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
def f():
    i; j
    \

    k
""", 'body[0]', 1, 2, None, {'postspace': True}, r"""
def f():
    i
    \

    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] FunctionDef .. 1,0 -> 5,5
    .name 'f'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'k' Load .. 5,4 -> 5,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
i ; \
 j
""", '', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

]  # END OF GET_SLICE_STMT_DATA

GET_SLICE_STMT_NOVERIFY_DATA = [
(r"""
if 1: i
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,5
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i  # post
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
""", r"""i  # post
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i  # post""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:""", r"""i  # post""", r"""
Module .. ROOT 0,0 -> 1,5
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i  # post
""", 'body[0]', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: # post
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i  # post""", 'body[0]', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: # post""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,5
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;  # post
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1: # post
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;  # post""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1: # post""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;  # post
""", 'body[0]', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: # post
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;  # post""", 'body[0]', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: # post""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] If .. 1,0 -> 1,5
    .test Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: pass

# pre
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 4,0 -> 4,1
    .value Name 'j' Load .. 4,0 -> 4,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': False, 'pep8space': False}, r"""
if 1: pass

j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 3,0 -> 3,1
    .value Name 'j' Load .. 3,0 -> 3,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
if 1: pass
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
if 1: pass

# pre
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 4,0 -> 4,1
    .value Name 'j' Load .. 4,0 -> 4,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
if 1: pass

# pre
else: pass  # post
j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
if 1: pass
# post
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 3,0 -> 3,1
    .value Name 'j' Load .. 3,0 -> 3,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
if 1: pass

# pre
else: pass  # post
j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True, 'pep8space': False, 'prespace': True}, r"""
if 1: pass
j
""", r"""pass  # post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass

# pre
finally: pass
j
""", 'body[0]', 0, 1, 'finalbody', {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass

# pre
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Try .. 1,0 -> 1,9
    .body[1]
    0] Pass .. 1,5 -> 1,9
  1] Expr .. 4,0 -> 4,1
    .value Name 'j' Load .. 4,0 -> 4,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass

# pre
finally: pass
j
""", 'body[0]', 0, 1, 'finalbody', {'precomms': True, 'postcomms': False, 'pep8space': False}, r"""
try: pass

j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Try .. 1,0 -> 1,9
    .body[1]
    0] Pass .. 1,5 -> 1,9
  1] Expr .. 3,0 -> 3,1
    .value Name 'j' Load .. 3,0 -> 3,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass

# pre
finally: pass
j
""", 'body[0]', 0, 1, 'finalbody', {'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
try: pass
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Try .. 1,0 -> 1,9
    .body[1]
    0] Pass .. 1,5 -> 1,9
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass

# pre
finally: pass
j
""", 'body[0]', 0, 1, 'finalbody', {'precomms': False, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
try: pass

# pre
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Try .. 1,0 -> 1,9
    .body[1]
    0] Pass .. 1,5 -> 1,9
  1] Expr .. 4,0 -> 4,1
    .value Name 'j' Load .. 4,0 -> 4,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass

# pre
finally: pass  # post
j
""", 'body[0]', 0, 1, 'finalbody', {'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
try: pass
# post
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Try .. 1,0 -> 1,9
    .body[1]
    0] Pass .. 1,5 -> 1,9
  1] Expr .. 3,0 -> 3,1
    .value Name 'j' Load .. 3,0 -> 3,1
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass

# pre
finally: pass  # post
j
""", 'body[0]', 0, 1, 'finalbody', {'precomms': True, 'postcomms': True, 'pep8space': False, 'prespace': True}, r"""
try: pass
j
""", r"""pass  # post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Try .. 1,0 -> 1,9
    .body[1]
    0] Pass .. 1,5 -> 1,9
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
if 1: i

# pre-else 1

# pre-else 2
else:

  # pre 1

  # pre 2
  j
""", 'body[0]', 0, 1, 'orelse', {'precomms': 'all', 'postcomms': False, 'pep8space': False}, r"""
if 1: i

""", r"""# pre 1

# pre 2
j""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 1,7
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 1,6 -> 1,7
      .value Name 'i' Load .. 1,6 -> 1,7
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 3,0 -> 3,1
    .value Name 'j' Load .. 3,0 -> 3,1
"""),

(r"""
if 1: i

# pre-else 1

# pre-else 2
else:

  # pre 1

  # pre 2
  j
""", 'body[0]', 0, 1, 'orelse', {'precomms': 'all', 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
if 1: i
""", r"""# pre 1

# pre 2
j""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,7
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 1,6 -> 1,7
      .value Name 'i' Load .. 1,6 -> 1,7
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 3,0 -> 3,1
    .value Name 'j' Load .. 3,0 -> 3,1
"""),

(r"""
try:
    pass
finally: pass
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
try:
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Try .. 1,0 -> 2,13
    .finalbody[1]
    0] Pass .. 2,9 -> 2,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass
finally: pass
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
try:
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Try .. 1,0 -> 2,13
    .finalbody[1]
    0] Pass .. 2,9 -> 2,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: i = \
  2
finally: pass
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
try:
finally: pass
""", r"""i = \
2""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Try .. 1,0 -> 2,13
    .finalbody[1]
    0] Pass .. 2,9 -> 2,13
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Assign .. 0,0 -> 1,1
    .targets[1]
    0] Name 'i' Store .. 0,0 -> 0,1
    .value Constant 2 .. 1,0 -> 1,1
"""),

(r"""
try: pass  # post
finally: pass
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
try:
finally: pass
""", r"""pass  # post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Try .. 1,0 -> 2,13
    .finalbody[1]
    0] Pass .. 2,9 -> 2,13
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass  # post
finally: pass
""", 'body[0]', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: # post
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Try .. 1,0 -> 2,13
    .finalbody[1]
    0] Pass .. 2,9 -> 2,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass
except: pass
else:
    pass
finally: pass
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""
try: pass
except: pass
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] Try .. 1,0 -> 3,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .handlers[1]
    0] ExceptHandler .. 2,0 -> 2,12
      .body[1]
      0] Pass .. 2,8 -> 2,12
    .finalbody[1]
    0] Pass .. 3,9 -> 3,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass
except: pass
else: pass
finally: pass
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""
try: pass
except: pass
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] Try .. 1,0 -> 3,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .handlers[1]
    0] ExceptHandler .. 2,0 -> 2,12
      .body[1]
      0] Pass .. 2,8 -> 2,12
    .finalbody[1]
    0] Pass .. 3,9 -> 3,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass
except:
    pass
else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', {'precomms': True, 'postcomms': True}, r"""
try: pass
else: pass
finally: pass
""", r"""except:
    pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] Try .. 1,0 -> 3,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .orelse[1]
    0] Pass .. 2,6 -> 2,10
    .finalbody[1]
    0] Pass .. 3,9 -> 3,13
""", r"""
Module .. ROOT 0,0 -> 1,8
  .body[1]
  0] ExceptHandler .. 0,0 -> 1,8
    .body[1]
    0] Pass .. 1,4 -> 1,8
"""),

(r"""
try: pass
except: pass
else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', {'precomms': True, 'postcomms': True}, r"""
try: pass
else: pass
finally: pass
""", r"""except: pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] Try .. 1,0 -> 3,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .orelse[1]
    0] Pass .. 2,6 -> 2,10
    .finalbody[1]
    0] Pass .. 3,9 -> 3,13
""", r"""
Module .. ROOT 0,0 -> 0,12
  .body[1]
  0] ExceptHandler .. 0,0 -> 0,12
    .body[1]
    0] Pass .. 0,8 -> 0,12
"""),

(r"""
try: pass
except: pass  # post
else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass
# post
else: pass
finally: pass
""", r"""except: pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] Try .. 1,0 -> 4,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .orelse[1]
    0] Pass .. 3,6 -> 3,10
    .finalbody[1]
    0] Pass .. 4,9 -> 4,13
""", r"""
Module .. ROOT 0,0 -> 0,12
  .body[1]
  0] ExceptHandler .. 0,0 -> 0,12
    .body[1]
    0] Pass .. 0,8 -> 0,12
"""),

(r"""
try: pass
except: pass  \

else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass
\

else: pass
finally: pass
""", r"""except: pass""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] Try .. 1,0 -> 5,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .orelse[1]
    0] Pass .. 4,6 -> 4,10
    .finalbody[1]
    0] Pass .. 5,9 -> 5,13
""", r"""
Module .. ROOT 0,0 -> 0,12
  .body[1]
  0] ExceptHandler .. 0,0 -> 0,12
    .body[1]
    0] Pass .. 0,8 -> 0,12
"""),

(r"""
try: pass
except:
    pass
else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
try: pass
except:
else: pass
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] Try .. 1,0 -> 4,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .handlers[1]
    0] ExceptHandler .. 2,0 -> 2,7
    .orelse[1]
    0] Pass .. 3,6 -> 3,10
    .finalbody[1]
    0] Pass .. 4,9 -> 4,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass
except: pass
else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
try: pass
except:
else: pass
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] Try .. 1,0 -> 4,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .handlers[1]
    0] ExceptHandler .. 2,0 -> 2,7
    .orelse[1]
    0] Pass .. 3,6 -> 3,10
    .finalbody[1]
    0] Pass .. 4,9 -> 4,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass
except: pass  # post
else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass
except: # post
else: pass
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] Try .. 1,0 -> 4,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .handlers[1]
    0] ExceptHandler .. 2,0 -> 2,7
    .orelse[1]
    0] Pass .. 3,6 -> 3,10
    .finalbody[1]
    0] Pass .. 4,9 -> 4,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
try: pass
except: pass \

else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass
except: \

else: pass
finally: pass
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] Try .. 1,0 -> 5,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .handlers[1]
    0] ExceptHandler .. 2,0 -> 2,7
    .orelse[1]
    0] Pass .. 4,6 -> 4,10
    .finalbody[1]
    0] Pass .. 5,9 -> 5,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

(r"""
if type in ('d', 'D'): cmd = 'TYPE A'; isdir = 1
else: cmd = 'TYPE ' + type; isdir = 0
""", 'body[0]', 0, 2, None, {}, r"""
if type in ('d', 'D'):
else: cmd = 'TYPE ' + type; isdir = 0
""", r"""cmd = 'TYPE A'; isdir = 1""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,37
    .test Compare .. 1,3 -> 1,21
      .left Name 'type' Load .. 1,3 -> 1,7
      .ops[1]
      0] In .. 1,8 -> 1,10
      .comparators[1]
      0] Tuple .. 1,11 -> 1,21
        .elts[2]
        0] Constant 'd' .. 1,12 -> 1,15
        1] Constant 'D' .. 1,17 -> 1,20
        .ctx Load
    .orelse[2]
    0] Assign .. 2,6 -> 2,26
      .targets[1]
      0] Name 'cmd' Store .. 2,6 -> 2,9
      .value BinOp .. 2,12 -> 2,26
        .left Constant 'TYPE ' .. 2,12 -> 2,19
        .op Add .. 2,20 -> 2,21
        .right Name 'type' Load .. 2,22 -> 2,26
    1] Assign .. 2,28 -> 2,37
      .targets[1]
      0] Name 'isdir' Store .. 2,28 -> 2,33
      .value Constant 0 .. 2,36 -> 2,37
""", r"""
Module .. ROOT 0,0 -> 0,25
  .body[2]
  0] Assign .. 0,0 -> 0,14
    .targets[1]
    0] Name 'cmd' Store .. 0,0 -> 0,3
    .value Constant 'TYPE A' .. 0,6 -> 0,14
  1] Assign .. 0,16 -> 0,25
    .targets[1]
    0] Name 'isdir' Store .. 0,16 -> 0,21
    .value Constant 1 .. 0,24 -> 0,25
"""),

(r"""
if type in ('d', 'D'): cmd = 'TYPE A'
else: cmd = 'TYPE ' + type; isdir = 0
""", 'body[0]', 0, 2, None, {}, r"""
if type in ('d', 'D'):
else: cmd = 'TYPE ' + type; isdir = 0
""", r"""cmd = 'TYPE A'""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,37
    .test Compare .. 1,3 -> 1,21
      .left Name 'type' Load .. 1,3 -> 1,7
      .ops[1]
      0] In .. 1,8 -> 1,10
      .comparators[1]
      0] Tuple .. 1,11 -> 1,21
        .elts[2]
        0] Constant 'd' .. 1,12 -> 1,15
        1] Constant 'D' .. 1,17 -> 1,20
        .ctx Load
    .orelse[2]
    0] Assign .. 2,6 -> 2,26
      .targets[1]
      0] Name 'cmd' Store .. 2,6 -> 2,9
      .value BinOp .. 2,12 -> 2,26
        .left Constant 'TYPE ' .. 2,12 -> 2,19
        .op Add .. 2,20 -> 2,21
        .right Name 'type' Load .. 2,22 -> 2,26
    1] Assign .. 2,28 -> 2,37
      .targets[1]
      0] Name 'isdir' Store .. 2,28 -> 2,33
      .value Constant 0 .. 2,36 -> 2,37
""", r"""
Module .. ROOT 0,0 -> 0,14
  .body[1]
  0] Assign .. 0,0 -> 0,14
    .targets[1]
    0] Name 'cmd' Store .. 0,0 -> 0,3
    .value Constant 'TYPE A' .. 0,6 -> 0,14
"""),

]  # END OF GET_SLICE_STMT_NOVERIFY_DATA

PUT_SLICE_SEQ_DATA = [
(r"""{
    a: 1
}""", 'body[0].value', 0, 1, r"""{}""", r"""
{}
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Dict .. 0,0 -> 0,2
"""),

(r"""1, 2""", 'body[0].value', 0, 2, r"""(

   )""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .ctx Load
"""),

(r"""if 1:
  {1, 2}""", 'body[0].body[0].value', 0, 2, r"""(

   )""", r"""
if 1:
  set()
""", r"""
Module .. ROOT 0,0 -> 1,7
  .body[1]
  0] If .. 0,0 -> 1,7
    .test Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,2 -> 1,7
      .value Call .. 1,2 -> 1,7
        .func Name 'set' Load .. 1,2 -> 1,5
"""),

(r"""{
    a: 1
}""", 'body[0].value', 0, 1, r"""{
}""", r"""
{
}
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 0,0 -> 1,1
    .value Dict .. 0,0 -> 1,1
"""),

(r"""{a: 1}""", 'body[0].value', 0, 1, r"""{}""", r"""
{}
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Dict .. 0,0 -> 0,2
"""),

(r"""{a: 1}""", 'body[0].value', 0, 1, r"""{
}""", r"""
{
}
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 0,0 -> 1,1
    .value Dict .. 0,0 -> 1,1
"""),

(r"""(1, 2)""", 'body[0].value', 1, 2, r"""()""", r"""
(1,)
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value Tuple .. 0,0 -> 0,4
      .elts[1]
      0] Constant 1 .. 0,1 -> 0,2
      .ctx Load
"""),

(r"""1, 2""", 'body[0].value', 1, 2, r"""()""", r"""
1,
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Constant 1 .. 0,0 -> 0,1
      .ctx Load
"""),

(r"""1, 2""", 'body[0].value', 0, 2, r"""()""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .ctx Load
"""),

(r"""(1, 2)""", 'body[0].value', 1, 2, r"""set()""", r"""
(1,)
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value Tuple .. 0,0 -> 0,4
      .elts[1]
      0] Constant 1 .. 0,1 -> 0,2
      .ctx Load
"""),

(r"""1, 2""", 'body[0].value', 1, 2, r"""set()""", r"""
1,
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Constant 1 .. 0,0 -> 0,1
      .ctx Load
"""),

(r"""1, 2""", 'body[0].value', 0, 2, r"""set()""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .ctx Load
"""),

(r"""[            # hello
    1, 2, 3
]""", 'body[0].value', 0, 2, r"""()""", r"""
[            # hello
    3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[1]
      0] Constant 3 .. 1,4 -> 1,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 0, 1, r"""[
    1]""", r"""
[            # hello
    1, b, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 1, 2, r"""[
    1]""", r"""
[            # hello
    a,
    1, c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 1 .. 2,4 -> 2,5
      2] Name 'c' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[
    1]""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value List .. 0,0 -> 2,6
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 0, 1, r"""[2]""", r"""
[            # hello
    2, b, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 2 .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 1, 2, r"""[2]""", r"""
[            # hello
    a, 2, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[2]""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value List .. 0,0 -> 1,12
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 0, 1, r"""[3
]""", r"""
[            # hello
    3,
    b, c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Constant 3 .. 1,4 -> 1,5
      1] Name 'b' Load .. 2,4 -> 2,5
      2] Name 'c' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 1, 2, r"""[3
]""", r"""
[            # hello
    a, 3,
    c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      2] Name 'c' Load .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[3
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 0, 1, r"""[
    1]""", r"""
[            # hello
    1, b, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 1, 2, r"""[
    1]""", r"""
[            # hello
    a,
    1, c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 1 .. 2,4 -> 2,5
      2] Name 'c' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[
    1]""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value List .. 0,0 -> 2,6
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 0, 1, r"""[2]""", r"""
[            # hello
    2, b, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 2 .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 1, 2, r"""[2]""", r"""
[            # hello
    a, 2, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[2]""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value List .. 0,0 -> 1,12
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 0, 1, r"""[3
]""", r"""
[            # hello
    3,
    b, c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Constant 3 .. 1,4 -> 1,5
      1] Name 'b' Load .. 2,4 -> 2,5
      2] Name 'c' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 1, 2, r"""[3
]""", r"""
[            # hello
    a, 3,
    c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      2] Name 'c' Load .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[3
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 0, 1, r"""[
    1,]""", r"""
[            # hello
    1, b, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 1, 2, r"""[
    1,]""", r"""
[            # hello
    a,
    1, c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 1 .. 2,4 -> 2,5
      2] Name 'c' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value List .. 0,0 -> 2,7
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 0, 1, r"""[2,]""", r"""
[            # hello
    2, b, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 2 .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 1, 2, r"""[2,]""", r"""
[            # hello
    a, 2, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[2,]""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value List .. 0,0 -> 1,13
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 0, 1, r"""[3,
]""", r"""
[            # hello
    3,
    b, c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Constant 3 .. 1,4 -> 1,5
      1] Name 'b' Load .. 2,4 -> 2,5
      2] Name 'c' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 1, 2, r"""[3,
]""", r"""
[            # hello
    a, 3,
    c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      2] Name 'c' Load .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[3,
]""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 0, 1, r"""[
    1,]""", r"""
[            # hello
    1, b, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 1, 2, r"""[
    1,]""", r"""
[            # hello
    a,
    1, c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 1 .. 2,4 -> 2,5
      2] Name 'c' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value List .. 0,0 -> 2,7
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 0, 1, r"""[2,]""", r"""
[            # hello
    2, b, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 2 .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 1, 2, r"""[2,]""", r"""
[            # hello
    a, 2, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Name 'c' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[2,]""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value List .. 0,0 -> 1,13
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 0, 1, r"""[3,
]""", r"""
[            # hello
    3,
    b, c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Constant 3 .. 1,4 -> 1,5
      1] Name 'b' Load .. 2,4 -> 2,5
      2] Name 'c' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 1, 2, r"""[3,
]""", r"""
[            # hello
    a, 3,
    c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      2] Name 'c' Load .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[3,
]""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[
    1]""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value List .. 0,0 -> 2,6
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[2]""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value List .. 0,0 -> 1,12
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[3
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value List .. 0,0 -> 2,7
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[2,]""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value List .. 0,0 -> 1,13
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[3,
]""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[
    1  # comment
]""", r"""
[            # hello
    a, b,
    1  # comment
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[2  # comment
]""", r"""
[            # hello
    a, b, 2  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[3  # comment
]""", r"""
[            # hello
    a, b, 3  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[
    1,  # comment
]""", r"""
[            # hello
    a, b,
    1,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[2,  # comment
]""", r"""
[            # hello
    a, b, 2,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[3,  # comment
]""", r"""
[            # hello
    a, b, 3,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 0, 0, r"""[
    1]""", r"""
[            # hello
    1, a, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Name 'a' Load .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 1, 1, r"""[
    1]""", r"""
[            # hello
    a,
    1, b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 1 .. 2,4 -> 2,5
      2] Name 'b' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[
    1]""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value List .. 0,0 -> 2,6
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 0, 0, r"""[2]""", r"""
[            # hello
    2, a, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 2 .. 1,4 -> 1,5
      1] Name 'a' Load .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 1, 1, r"""[2]""", r"""
[            # hello
    a, 2, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[2]""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value List .. 0,0 -> 1,12
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 0, 0, r"""[3
]""", r"""
[            # hello
    3,
    a, b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Constant 3 .. 1,4 -> 1,5
      1] Name 'a' Load .. 2,4 -> 2,5
      2] Name 'b' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 1, 1, r"""[3
]""", r"""
[            # hello
    a, 3,
    b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      2] Name 'b' Load .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[3
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 0, 0, r"""[
    1]""", r"""
[            # hello
    1, a, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Name 'a' Load .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 1, 1, r"""[
    1]""", r"""
[            # hello
    a,
    1, b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 1 .. 2,4 -> 2,5
      2] Name 'b' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[
    1]""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value List .. 0,0 -> 2,6
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 0, 0, r"""[2]""", r"""
[            # hello
    2, a, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 2 .. 1,4 -> 1,5
      1] Name 'a' Load .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 1, 1, r"""[2]""", r"""
[            # hello
    a, 2, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[2]""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value List .. 0,0 -> 1,12
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 0, 0, r"""[3
]""", r"""
[            # hello
    3,
    a, b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Constant 3 .. 1,4 -> 1,5
      1] Name 'a' Load .. 2,4 -> 2,5
      2] Name 'b' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 1, 1, r"""[3
]""", r"""
[            # hello
    a, 3,
    b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      2] Name 'b' Load .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[3
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 0, 0, r"""[
    1,]""", r"""
[            # hello
    1, a, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Name 'a' Load .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 1, 1, r"""[
    1,]""", r"""
[            # hello
    a,
    1, b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 1 .. 2,4 -> 2,5
      2] Name 'b' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value List .. 0,0 -> 2,7
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 0, 0, r"""[2,]""", r"""
[            # hello
    2, a, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 2 .. 1,4 -> 1,5
      1] Name 'a' Load .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 1, 1, r"""[2,]""", r"""
[            # hello
    a, 2, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[2,]""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value List .. 0,0 -> 1,13
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 0, 0, r"""[3,
]""", r"""
[            # hello
    3,
    a, b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Constant 3 .. 1,4 -> 1,5
      1] Name 'a' Load .. 2,4 -> 2,5
      2] Name 'b' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 1, 1, r"""[3,
]""", r"""
[            # hello
    a, 3,
    b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      2] Name 'b' Load .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[3,
]""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 0, 0, r"""[
    1,]""", r"""
[            # hello
    1, a, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Name 'a' Load .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 1, 1, r"""[
    1,]""", r"""
[            # hello
    a,
    1, b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 1 .. 2,4 -> 2,5
      2] Name 'b' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value List .. 0,0 -> 2,7
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 0, 0, r"""[2,]""", r"""
[            # hello
    2, a, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Constant 2 .. 1,4 -> 1,5
      1] Name 'a' Load .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 1, 1, r"""[2,]""", r"""
[            # hello
    a, 2, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 2 .. 1,7 -> 1,8
      2] Name 'b' Load .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[2,]""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value List .. 0,0 -> 1,13
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 0, 0, r"""[3,
]""", r"""
[            # hello
    3,
    a, b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Constant 3 .. 1,4 -> 1,5
      1] Name 'a' Load .. 2,4 -> 2,5
      2] Name 'b' Load .. 2,7 -> 2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 1, 1, r"""[3,
]""", r"""
[            # hello
    a, 3,
    b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Constant 3 .. 1,7 -> 1,8
      2] Name 'b' Load .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[3,
]""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[
    1]""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value List .. 0,0 -> 2,6
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[2]""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value List .. 0,0 -> 1,12
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[3
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value List .. 0,0 -> 2,7
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[2,]""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value List .. 0,0 -> 1,13
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[3,
]""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[
    1  # comment
]""", r"""
[            # hello
    a, b,
    1  # comment
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[2  # comment
]""", r"""
[            # hello
    a, b, 2  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[3  # comment
]""", r"""
[            # hello
    a, b, 3  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[
    1,  # comment
]""", r"""
[            # hello
    a, b,
    1,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value List .. 0,0 -> 3,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 1 .. 2,4 -> 2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[2,  # comment
]""", r"""
[            # hello
    a, b, 2,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 2 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[3,  # comment
]""", r"""
[            # hello
    a, b, 3,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[3]
      0] Name 'a' Load .. 1,4 -> 1,5
      1] Name 'b' Load .. 1,7 -> 1,8
      2] Constant 3 .. 1,10 -> 1,11
      .ctx Load
"""),

(r"""{
    'message': ('An open stream was garbage collected prior to '
                'establishing network connection; '
                'call "stream.close()" explicitly.')
}""", 'body[0].value', 1, 1, r"""{i: j}""", r"""
{
    'message': ('An open stream was garbage collected prior to '
                'establishing network connection; '
                'call "stream.close()" explicitly.'), i: j}
""", r"""
Module .. ROOT 0,0 -> 3,59
  .body[1]
  0] Expr .. 0,0 -> 3,59
    .value Dict .. 0,0 -> 3,59
      .keys[2]
      0] Constant 'message' .. 1,4 -> 1,13
      1] Name 'i' Load .. 3,54 -> 3,55
      .values[2]
      0] Constant 'An open stream was garbage collected prior to establishing network connection; call "stream.close()" explicitly.' .. 1,16 -> 3,51
      1] Name 'j' Load .. 3,57 -> 3,58
"""),

(r"""{
    1: 2,
    5: 6
}""", 'body[0].value', 1, 1, r"""{3: ("4")}""", r"""
{
    1: 2,
    3: ("4"), 5: 6
}
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value Dict .. 0,0 -> 3,1
      .keys[3]
      0] Constant 1 .. 1,4 -> 1,5
      1] Constant 3 .. 2,4 -> 2,5
      2] Constant 5 .. 2,14 -> 2,15
      .values[3]
      0] Constant 2 .. 1,7 -> 1,8
      1] Constant '4' .. 2,8 -> 2,11
      2] Constant 6 .. 2,17 -> 2,18
"""),

(r"""[
    # order of patterns matters
    r'file, line (\\d+)',
    3,
]""", 'body[0].value', 1, 1, r"""(1, 2)""", r"""
[
    # order of patterns matters
    r'file, line (\\d+)',
    1, 2, 3,
]
""", r"""
Module .. ROOT 0,0 -> 4,1
  .body[1]
  0] Expr .. 0,0 -> 4,1
    .value List .. 0,0 -> 4,1
      .elts[4]
      0] Constant 'file, line (\\\\d+)' .. 2,4 -> 2,24
      1] Constant 1 .. 3,4 -> 3,5
      2] Constant 2 .. 3,7 -> 3,8
      3] Constant 3 .. 3,10 -> 3,11
      .ctx Load
"""),

(r"""(IndexError, KeyError, isinstance,)""", 'body[0].value', 2, 3, r"""()""", r"""
(IndexError, KeyError,)
""", r"""
Module .. ROOT 0,0 -> 0,23
  .body[1]
  0] Expr .. 0,0 -> 0,23
    .value Tuple .. 0,0 -> 0,23
      .elts[2]
      0] Name 'IndexError' Load .. 0,1 -> 0,11
      1] Name 'KeyError' Load .. 0,13 -> 0,21
      .ctx Load
"""),

(r"""[a, b] = c""", 'body[0].targets[0]', 2, 2, r"""(d,)""", r"""
[a, b, d,] = c
""", r"""
Module .. ROOT 0,0 -> 0,14
  .body[1]
  0] Assign .. 0,0 -> 0,14
    .targets[1]
    0] List .. 0,0 -> 0,10
      .elts[3]
      0] Name 'a' Store .. 0,1 -> 0,2
      1] Name 'b' Store .. 0,4 -> 0,5
      2] Name 'd' Store .. 0,7 -> 0,8
      .ctx Store
    .value Name 'c' Load .. 0,13 -> 0,14
"""),

(r"""stat_list,""", 'body[0].value', 0, 1, r"""[ {-1: "stdname",
                   2: "cumulative"}[field[0]] ]""", r"""
( {-1: "stdname",
                   2: "cumulative"}[field[0]], )
""", r"""
Module .. ROOT 0,0 -> 1,48
  .body[1]
  0] Expr .. 0,0 -> 1,48
    .value Tuple .. 0,0 -> 1,48
      .elts[1]
      0] Subscript .. 0,2 -> 1,45
        .value Dict .. 0,2 -> 1,35
          .keys[2]
          0] UnaryOp .. 0,3 -> 0,5
            .op USub .. 0,3 -> 0,4
            .operand Constant 1 .. 0,4 -> 0,5
          1] Constant 2 .. 1,19 -> 1,20
          .values[2]
          0] Constant 'stdname' .. 0,7 -> 0,16
          1] Constant 'cumulative' .. 1,22 -> 1,34
        .slice Subscript .. 1,36 -> 1,44
          .value Name 'field' Load .. 1,36 -> 1,41
          .slice Constant 0 .. 1,42 -> 1,43
          .ctx Load
        .ctx Load
      .ctx Load
"""),

(r"""for a in a, b:
    pass""", 'body[0].iter', 1, 2, r"""(
c,)""", r"""
for a in (a,
c,):
    pass
""", r"""
Module .. ROOT 0,0 -> 2,8
  .body[1]
  0] For .. 0,0 -> 2,8
    .target Name 'a' Store .. 0,4 -> 0,5
    .iter Tuple .. 0,9 -> 1,3
      .elts[2]
      0] Name 'a' Load .. 0,10 -> 0,11
      1] Name 'c' Load .. 1,0 -> 1,1
      .ctx Load
    .body[1]
    0] Pass .. 2,4 -> 2,8
"""),

(r"""result = filename, headers""", 'body[0].value', 0, 0, r"""(
c,)""", r"""
result = (
c, filename, headers)
""", r"""
Module .. ROOT 0,0 -> 1,21
  .body[1]
  0] Assign .. 0,0 -> 1,21
    .targets[1]
    0] Name 'result' Store .. 0,0 -> 0,6
    .value Tuple .. 0,9 -> 1,21
      .elts[3]
      0] Name 'c' Load .. 1,0 -> 1,1
      1] Name 'filename' Load .. 1,3 -> 1,11
      2] Name 'headers' Load .. 1,13 -> 1,20
      .ctx Load
"""),

(r"""return (user if delim else None), host""", 'body[0].value', 0, 2, r"""()""", r"""
return ()
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Return .. 0,0 -> 0,9
    .value Tuple .. 0,7 -> 0,9
      .ctx Load
"""),

(r"""{1, 2}""", 'body[0].value', 0, 2, r"""()""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Call .. 0,0 -> 0,5
      .func Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""set()""", 'body[0].value', 0, 0, r"""()""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Call .. 0,0 -> 0,5
      .func Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""set()""", 'body[0].value', 0, 0, r"""(1, 2)""", r"""
{1, 2}
""", r"""
Module .. ROOT 0,0 -> 0,6
  .body[1]
  0] Expr .. 0,0 -> 0,6
    .value Set .. 0,0 -> 0,6
      .elts[2]
      0] Constant 1 .. 0,1 -> 0,2
      1] Constant 2 .. 0,4 -> 0,5
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 0, r"""a,""", r"""
a, 1, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value Tuple .. 0,0 -> 0,11
      .elts[4]
      0] Name 'a' Load .. 0,0 -> 0,1
      1] Constant 1 .. 0,3 -> 0,4
      2] Constant 2 .. 0,6 -> 0,7
      3] Constant 3 .. 0,9 -> 0,10
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 1, r"""a,""", r"""
1, a, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value Tuple .. 0,0 -> 0,11
      .elts[4]
      0] Constant 1 .. 0,0 -> 0,1
      1] Name 'a' Load .. 0,3 -> 0,4
      2] Constant 2 .. 0,6 -> 0,7
      3] Constant 3 .. 0,9 -> 0,10
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 2, r"""a,""", r"""
1, 2, a, 3,
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value Tuple .. 0,0 -> 0,11
      .elts[4]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Name 'a' Load .. 0,6 -> 0,7
      3] Constant 3 .. 0,9 -> 0,10
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 3, 3, r"""a,""", r"""
1, 2, 3, a,
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value Tuple .. 0,0 -> 0,11
      .elts[4]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      3] Name 'a' Load .. 0,9 -> 0,10
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 1, r"""a,""", r"""
a, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Name 'a' Load .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 2, r"""a,""", r"""
1, a, 3,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Name 'a' Load .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 3, r"""a,""", r"""
1, 2, a,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Name 'a' Load .. 0,6 -> 0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 2, r"""a,""", r"""
a, 3,
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[2]
      0] Name 'a' Load .. 0,0 -> 0,1
      1] Constant 3 .. 0,3 -> 0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 3, r"""a,""", r"""
1, a,
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[2]
      0] Constant 1 .. 0,0 -> 0,1
      1] Name 'a' Load .. 0,3 -> 0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 3, r"""a,""", r"""
a,
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Name 'a' Load .. 0,0 -> 0,1
      .ctx Load
"""),

(r"""[            # hello
    1, 2, 3
]""", 'body[0].value', 0, 2, r"""**DEL**""", r"""
[            # hello
    3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value List .. 0,0 -> 2,1
      .elts[1]
      0] Constant 3 .. 1,4 -> 1,5
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 0, r"""**DEL**""", r"""
1, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 1, r"""**DEL**""", r"""
1, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 2, r"""**DEL**""", r"""
1, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 3, 3, r"""**DEL**""", r"""
1, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      2] Constant 3 .. 0,6 -> 0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 1, r"""**DEL**""", r"""
2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[2]
      0] Constant 2 .. 0,0 -> 0,1
      1] Constant 3 .. 0,3 -> 0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 2, r"""**DEL**""", r"""
1, 3,
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[2]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 3 .. 0,3 -> 0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 3, r"""**DEL**""", r"""
1, 2,
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[2]
      0] Constant 1 .. 0,0 -> 0,1
      1] Constant 2 .. 0,3 -> 0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 2, r"""**DEL**""", r"""
3,
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Constant 3 .. 0,0 -> 0,1
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 3, r"""**DEL**""", r"""
1,
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .elts[1]
      0] Constant 1 .. 0,0 -> 0,1
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 3, r"""**DEL**""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Tuple .. 0,0 -> 0,2
      .ctx Load
"""),

]  # END OF PUT_SLICE_SEQ_DATA

PUT_SLICE_STMT_DATA = [
(r"""
if 1:
    i
    j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i  # post
    j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i  # post
    k
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i \
  # post
    j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i \
  # post
    k
    j
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
    2] Expr .. 5,4 -> 5,5
      .value Name 'j' Load .. 5,4 -> 5,5
"""),

(r"""
if 1:
    i  # post
    # pre
    j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i  # post
    k
    # pre
    j
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 5,4 -> 5,5
      .value Name 'j' Load .. 5,4 -> 5,5
"""),

(r"""
if 1:
    i
    # pre
    j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    # pre
    j
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 5,4 -> 5,5
      .value Name 'j' Load .. 5,4 -> 5,5
"""),

(r"""
if 1:
    i

    # pre pre

    # pre

    j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k

    # pre pre

    # pre

    j
""", r"""
Module .. ROOT 0,0 -> 10,0
  .body[1]
  0] If .. 1,0 -> 9,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 9,4 -> 9,5
      .value Name 'j' Load .. 9,4 -> 9,5
"""),

(r"""
if 1:
    i ; j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i ; \
  j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i \
  ; j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i \
  ; \
  j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if 1: i ; j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if 1: \
  i \
  ; \
  j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i ; j ; l ; m
""", 'body[0]', 2, 2, 'body', {}, r"""k""", r"""
if 1:
    i ; j
    k
    l ; m
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,9
    .test Constant 1 .. 1,3 -> 1,4
    .body[5]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 2,8 -> 2,9
      .value Name 'j' Load .. 2,8 -> 2,9
    2] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    3] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    4] Expr .. 4,8 -> 4,9
      .value Name 'm' Load .. 4,8 -> 4,9
"""),

(r"""
if 1: i ; j ; l ; m
""", 'body[0]', 2, 2, 'body', {}, r"""k""", r"""
if 1:
    i ; j
    k
    l ; m
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,9
    .test Constant 1 .. 1,3 -> 1,4
    .body[5]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 2,8 -> 2,9
      .value Name 'j' Load .. 2,8 -> 2,9
    2] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    3] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    4] Expr .. 4,8 -> 4,9
      .value Name 'm' Load .. 4,8 -> 4,9
"""),

(r"""
if 1:
    i
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i  # post
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i  # post
    k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i  # post
    # pre
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i  # post
    k
    # pre
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: i
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: i  # post
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i  # post
    k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: i  # post
    # pre
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i  # post
    k
    # pre
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: i ;
    # pre
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i ;
    k
    # pre
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: i ;  # post
    # pre
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i ;  # post
    k
    # pre
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:
    k
    i
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'k' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'i' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:  # post-block
    i
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:  # post-block
    k
    i
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'k' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'i' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    # pre
    i
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:
    k
    # pre
    i
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'k' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'i' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:  # post-block
    # pre
    i
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:  # post-block
    k
    # pre
    i
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'k' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'i' Load .. 4,4 -> 4,5
"""),

(r"""
if 1: \
  # post-lline-block
    # pre
    i
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1: \
  # post-lline-block
    k
    # pre
    i
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'i' Load .. 5,4 -> 5,5
"""),

(r"""
if 1: i ; j  # post-multi
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:
    k
    i ; j  # post-multi
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,9
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'k' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'i' Load .. 3,4 -> 3,5
    2] Expr .. 3,8 -> 3,9
      .value Name 'j' Load .. 3,8 -> 3,9
"""),

(r"""
if 1: \
  i ; j  # post-multi
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:
    k
    i ; j  # post-multi
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,9
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'k' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'i' Load .. 3,4 -> 3,5
    2] Expr .. 3,8 -> 3,9
      .value Name 'j' Load .. 3,8 -> 3,9
"""),

(r"""
def f():
    if 1:
        pass
""", 'body[0].body[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 2: break""", r"""
def f():
    if 1:
        pass
    elif 2: break
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] FunctionDef .. 1,0 -> 4,17
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 4,17
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 3,8 -> 3,12
      .orelse[1]
      0] If .. 4,4 -> 4,17
        .test Constant 2 .. 4,9 -> 4,10
        .body[1]
        0] Break .. 4,12 -> 4,17
"""),

(r"""
def f():
    if 1:
        pass  # post-if
    # post-line
""", 'body[0].body[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""# pre
if 2: break  # post-elif""", r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # post-line
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 5,17
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 5,17
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 3,8 -> 3,12
      .orelse[1]
      0] If .. 5,4 -> 5,17
        .test Constant 2 .. 5,9 -> 5,10
        .body[1]
        0] Break .. 5,12 -> 5,17
"""),

(r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # post-line
""", 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""# pre-3
if 3:  # post-elif-3
    continue  # post-elif-continue-3""", r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
""", r"""
Module .. ROOT 0,0 -> 10,0
  .body[1]
  0] FunctionDef .. 1,0 -> 8,16
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 8,16
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 3,8 -> 3,12
      .orelse[1]
      0] If .. 5,4 -> 8,16
        .test Constant 2 .. 5,9 -> 5,10
        .body[1]
        0] Break .. 5,12 -> 5,17
        .orelse[1]
        0] If .. 7,4 -> 8,16
          .test Constant 3 .. 7,9 -> 7,10
          .body[1]
          0] Continue .. 8,8 -> 8,16
"""),

(r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
""", 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""**DEL**""", r"""
def f():
    if 1:
        pass  # post-if
    # pre
    # post-elif-continue-3
    # post-line
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 3,12
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 3,12
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 3,8 -> 3,12
"""),

(r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
""", 'body[0].body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': False, 'pep8space': False}, r"""**DEL**""", r"""
def f():
    if 1:
        pass  # post-if
# post-elif-continue-3
    # post-line
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] FunctionDef .. 1,0 -> 3,12
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 3,12
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 3,8 -> 3,12
"""),

(r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
""", 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': True, 'pep8space': False}, r"""**DEL**""", r"""
def f():
    if 1:
        pass  # post-if
    # pre
    # post-line
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] FunctionDef .. 1,0 -> 3,12
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 3,12
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 3,8 -> 3,12
"""),

(r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
""", 'body[0].body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""**DEL**""", r"""
def f():
    if 1:
        pass  # post-if
    # post-line
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] FunctionDef .. 1,0 -> 3,12
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 3,12
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 3,8 -> 3,12
"""),

(r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif

    # pre-pre-3

    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3

    # post-line
""", 'body[0].body[0].orelse[0]', 0, 1, 'orelse', {'precomms': 'all', 'postcomms': True, 'pep8space': False, 'prespace': True}, r"""**DEL**""", r"""
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif

    # post-line
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] FunctionDef .. 1,0 -> 5,17
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 5,17
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 3,8 -> 3,12
      .orelse[1]
      0] If .. 5,4 -> 5,17
        .test Constant 2 .. 5,9 -> 5,10
        .body[1]
        0] Break .. 5,12 -> 5,17
"""),

(r"""""", None, 0, 0, None, {}, r"""i""", r"""i
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
""", None, 0, 0, None, {}, r"""i""", r"""
i
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
"""),

(r"""

""", None, 0, 0, None, {}, r"""i""", r"""

i
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Expr .. 2,0 -> 2,1
    .value Name 'i' Load .. 2,0 -> 2,1
"""),

(r"""
# comment
""", None, 0, 0, None, {}, r"""i""", r"""
# comment
i
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Expr .. 2,0 -> 2,1
    .value Name 'i' Load .. 2,0 -> 2,1
"""),

(r"""

# comment

# another comment
""", None, 0, 0, None, {}, r"""i""", r"""

# comment

# another comment
i
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] Expr .. 5,0 -> 5,1
    .value Name 'i' Load .. 5,0 -> 5,1
"""),

(r"""

# comment

# another comment
i
""", None, 0, 0, None, {}, r"""h""", r"""

# comment

# another comment
h
i
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[2]
  0] Expr .. 5,0 -> 5,1
    .value Name 'h' Load .. 5,0 -> 5,1
  1] Expr .. 6,0 -> 6,1
    .value Name 'i' Load .. 6,0 -> 6,1
"""),

(r"""

# comment

# another comment
i
""", None, 1, 1, None, {}, r"""j""", r"""

# comment

# another comment
i
j
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[2]
  0] Expr .. 5,0 -> 5,1
    .value Name 'i' Load .. 5,0 -> 5,1
  1] Expr .. 6,0 -> 6,1
    .value Name 'j' Load .. 6,0 -> 6,1
"""),

(r"""
def f():
    if 1: pass
    elif 2: pass
""", 'body[0].body[0]', 0, 0, 'orelse', {}, r"""break""", r"""
def f():
    if 1: pass
    else:
        break
        if 2: pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] FunctionDef .. 1,0 -> 5,18
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 5,18
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[2]
      0] Break .. 4,8 -> 4,13
      1] If .. 5,8 -> 5,18
        .test Constant 2 .. 5,11 -> 5,12
        .body[1]
        0] Pass .. 5,14 -> 5,18
"""),

(r"""
def f():
    if 1: pass
    elif 2: pass
""", 'body[0].body[0]', 1, 1, 'orelse', {}, r"""break""", r"""
def f():
    if 1: pass
    else:
        if 2: pass
        break
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] FunctionDef .. 1,0 -> 5,13
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 5,13
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[2]
      0] If .. 4,8 -> 4,18
        .test Constant 2 .. 4,11 -> 4,12
        .body[1]
        0] Pass .. 4,14 -> 4,18
      1] Break .. 5,8 -> 5,13
"""),

(r"""
def f():
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 0, 0, 'orelse', {}, r"""break""", r"""
def f():
    if 1: pass
    else:
        break
        if 2:
            pass
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 6,16
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 6,16
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[2]
      0] Break .. 4,8 -> 4,13
      1] If .. 5,8 -> 6,16
        .test Constant 2 .. 5,11 -> 5,12
        .body[1]
        0] Pass .. 6,12 -> 6,16
"""),

(r"""
def f():
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 1, 1, 'orelse', {}, r"""break""", r"""
def f():
    if 1: pass
    else:
        if 2:
            pass
        break
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 6,13
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 6,13
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[2]
      0] If .. 4,8 -> 5,16
        .test Constant 2 .. 4,11 -> 4,12
        .body[1]
        0] Pass .. 5,12 -> 5,16
      1] Break .. 6,8 -> 6,13
"""),

(r"""
def f():
    if 1: pass
    elif 2: continue
    elif 3: raise
""", 'body[0].body[0]', 0, 0, 'orelse', {}, r"""break""", r"""
def f():
    if 1: pass
    else:
        break
        if 2: continue
        elif 3: raise
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 6,21
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 6,21
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[2]
      0] Break .. 4,8 -> 4,13
      1] If .. 5,8 -> 6,21
        .test Constant 2 .. 5,11 -> 5,12
        .body[1]
        0] Continue .. 5,14 -> 5,22
        .orelse[1]
        0] If .. 6,8 -> 6,21
          .test Constant 3 .. 6,13 -> 6,14
          .body[1]
          0] Raise .. 6,16 -> 6,21
"""),

(r"""
def f():
    if 1: pass
    elif 2: continue
    elif 3: raise
""", 'body[0].body[0]', 1, 1, 'orelse', {}, r"""break""", r"""
def f():
    if 1: pass
    else:
        if 2: continue
        elif 3: raise
        break
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 6,13
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 6,13
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[2]
      0] If .. 4,8 -> 5,21
        .test Constant 2 .. 4,11 -> 4,12
        .body[1]
        0] Continue .. 4,14 -> 4,22
        .orelse[1]
        0] If .. 5,8 -> 5,21
          .test Constant 3 .. 5,13 -> 5,14
          .body[1]
          0] Raise .. 5,16 -> 5,21
      1] Break .. 6,8 -> 6,13
"""),

(r"""
def f():
    if 1: pass
    elif 2: continue
    elif 3: raise
""", 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {}, r"""break""", r"""
def f():
    if 1: pass
    elif 2: continue
    else:
        break
        if 3: raise
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 6,19
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 6,19
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 3,4 -> 6,19
        .test Constant 2 .. 3,9 -> 3,10
        .body[1]
        0] Continue .. 3,12 -> 3,20
        .orelse[2]
        0] Break .. 5,8 -> 5,13
        1] If .. 6,8 -> 6,19
          .test Constant 3 .. 6,11 -> 6,12
          .body[1]
          0] Raise .. 6,14 -> 6,19
"""),

(r"""
def f():
    if 1: pass
    elif 2: continue
    elif 3: raise
""", 'body[0].body[0].orelse[0]', 1, 1, 'orelse', {}, r"""break""", r"""
def f():
    if 1: pass
    elif 2: continue
    else:
        if 3: raise
        break
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 6,13
    .name 'f'
    .body[1]
    0] If .. 2,4 -> 6,13
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 3,4 -> 6,13
        .test Constant 2 .. 3,9 -> 3,10
        .body[1]
        0] Continue .. 3,12 -> 3,20
        .orelse[2]
        0] If .. 5,8 -> 5,19
          .test Constant 3 .. 5,11 -> 5,12
          .body[1]
          0] Raise .. 5,14 -> 5,19
        1] Break .. 6,8 -> 6,13
"""),

(r"""
def f():
    i
""", 'body[0]', 0, 0, None, {}, r"""# comment""", r"""
def f():
    # comment
    i
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 1,0 -> 3,5
    .name 'f'
    .body[1]
    0] Expr .. 3,4 -> 3,5
      .value Name 'i' Load .. 3,4 -> 3,5
"""),

(r"""
def f():
    i
""", 'body[0]', 1, 1, None, {}, r"""# comment""", r"""
def f():
    i
    # comment
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 1,0 -> 2,5
    .name 'f'
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
"""),

(r"""
def f():
    i ; j
""", 'body[0]', 0, 0, None, {}, r"""# comment""", r"""
def f():
    # comment
    i ; j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 1,0 -> 3,9
    .name 'f'
    .body[2]
    0] Expr .. 3,4 -> 3,5
      .value Name 'i' Load .. 3,4 -> 3,5
    1] Expr .. 3,8 -> 3,9
      .value Name 'j' Load .. 3,8 -> 3,9
"""),

(r"""
def f():
    i ; j
""", 'body[0]', 1, 1, None, {}, r"""# comment""", r"""
def f():
    i
    # comment
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] FunctionDef .. 1,0 -> 4,5
    .name 'f'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
def f():
    i ; j
""", 'body[0]', 2, 2, None, {}, r"""# comment""", r"""
def f():
    i ; j
    # comment
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 1,0 -> 2,9
    .name 'f'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 2,8 -> 2,9
      .value Name 'j' Load .. 2,8 -> 2,9
"""),

(r"""
def f():
    i \
  \
  ; \
  j
""", 'body[0]', 0, 0, None, {}, r"""# comment""", r"""
def f():
    # comment
    i \
  \
  ; \
  j
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 6,3
    .name 'f'
    .body[2]
    0] Expr .. 3,4 -> 3,5
      .value Name 'i' Load .. 3,4 -> 3,5
    1] Expr .. 6,2 -> 6,3
      .value Name 'j' Load .. 6,2 -> 6,3
"""),

(r"""
def f():
    i \
  \
  ; \
  j
""", 'body[0]', 1, 1, None, {}, r"""# comment""", r"""
def f():
    i
    # comment
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] FunctionDef .. 1,0 -> 4,5
    .name 'f'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
def f():
    i \
  \
  ; \
  j
""", 'body[0]', 2, 2, None, {}, r"""# comment""", r"""
def f():
    i \
  \
  ; \
  j
    # comment
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 5,3
    .name 'f'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,2 -> 5,3
      .value Name 'j' Load .. 5,2 -> 5,3
"""),

(r"""""", '', 0, 0, None, {'pep8space': True}, r"""def func(): pass""", r"""def func(): pass
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] FunctionDef .. 0,0 -> 0,16
    .name 'func'
    .body[1]
    0] Pass .. 0,12 -> 0,16
"""),

(r"""""", '', 0, 0, None, {'pep8space': True}, r"""
def func(): pass""", r"""
def func(): pass
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
"""),

(r"""'''Module
   docstring'''""", '', 1, 1, None, {'pep8space': True}, r"""def func(): pass""", r"""'''Module
   docstring'''

def func(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 0,0 -> 1,15
    .value Constant 'Module\n   docstring' .. 0,0 -> 1,15
  1] FunctionDef .. 3,0 -> 3,16
    .name 'func'
    .body[1]
    0] Pass .. 3,12 -> 3,16
"""),

(r"""'''Module
   docstring'''""", '', 1, 1, None, {'pep8space': True}, r"""def func(): pass""", r"""'''Module
   docstring'''

def func(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 0,0 -> 1,15
    .value Constant 'Module\n   docstring' .. 0,0 -> 1,15
  1] FunctionDef .. 3,0 -> 3,16
    .name 'func'
    .body[1]
    0] Pass .. 3,12 -> 3,16
"""),

(r"""'''Module
   docstring'''""", '', 1, 1, None, {'pep8space': True}, r"""
def func(): pass""", r"""'''Module
   docstring'''

def func(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 0,0 -> 1,15
    .value Constant 'Module\n   docstring' .. 0,0 -> 1,15
  1] FunctionDef .. 3,0 -> 3,16
    .name 'func'
    .body[1]
    0] Pass .. 3,12 -> 3,16
"""),

(r"""'''Module
   docstring'''""", '', 1, 1, None, {'pep8space': True}, r"""

def func(): pass""", r"""'''Module
   docstring'''


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Expr .. 0,0 -> 1,15
    .value Constant 'Module\n   docstring' .. 0,0 -> 1,15
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': True}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': 1}, r"""def func(): pass""", r"""
def prefunc(): pass

def func(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 3,0 -> 3,16
    .name 'func'
    .body[1]
    0] Pass .. 3,12 -> 3,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def func(): pass""", r"""
def prefunc(): pass
def func(): pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 2,0 -> 2,16
    .name 'func'
    .body[1]
    0] Pass .. 2,12 -> 2,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': True}, r"""
def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': 1}, r"""
def func(): pass""", r"""
def prefunc(): pass

def func(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 3,0 -> 3,16
    .name 'func'
    .body[1]
    0] Pass .. 3,12 -> 3,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def func(): pass""", r"""
def prefunc(): pass
def func(): pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 2,0 -> 2,16
    .name 'func'
    .body[1]
    0] Pass .. 2,12 -> 2,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': True}, r"""

def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': 1}, r"""

def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': True}, r"""


def func(): pass""", r"""
def prefunc(): pass



def func(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 5,0 -> 5,16
    .name 'func'
    .body[1]
    0] Pass .. 5,12 -> 5,16
"""),

(r"""
import stuff
""", '', 1, 1, None, {'pep8space': True}, r"""def func(): pass""", r"""
import stuff


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Import .. 1,0 -> 1,12
    .names[1]
    0] alias .. 1,7 -> 1,12
      .name 'stuff'
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
import stuff
""", '', 1, 1, None, {'pep8space': True}, r"""
def func(): pass""", r"""
import stuff


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Import .. 1,0 -> 1,12
    .names[1]
    0] alias .. 1,7 -> 1,12
      .name 'stuff'
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
import stuff
""", '', 1, 1, None, {'pep8space': True}, r"""

def func(): pass""", r"""
import stuff


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Import .. 1,0 -> 1,12
    .names[1]
    0] alias .. 1,7 -> 1,12
      .name 'stuff'
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
import stuff
""", '', 1, 1, None, {'pep8space': True}, r"""

def func(): pass""", r"""
import stuff


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Import .. 1,0 -> 1,12
    .names[1]
    0] alias .. 1,7 -> 1,12
      .name 'stuff'
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass""", r"""
def func(): pass


def prefunc(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
  1] FunctionDef .. 4,0 -> 4,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 4,15 -> 4,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {'pep8space': 1}, r"""def func(): pass""", r"""
def func(): pass

def prefunc(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
  1] FunctionDef .. 3,0 -> 3,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 3,15 -> 3,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def func(): pass""", r"""
def func(): pass
def prefunc(): pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
  1] FunctionDef .. 2,0 -> 2,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 2,15 -> 2,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass
""", r"""
def func(): pass


def prefunc(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
  1] FunctionDef .. 4,0 -> 4,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 4,15 -> 4,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass

""", r"""
def func(): pass


def prefunc(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
  1] FunctionDef .. 4,0 -> 4,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 4,15 -> 4,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass


""", r"""
def func(): pass


def prefunc(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
  1] FunctionDef .. 4,0 -> 4,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 4,15 -> 4,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass



""", r"""
def func(): pass



def prefunc(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
  1] FunctionDef .. 5,0 -> 5,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 5,15 -> 5,19
"""),

(r"""
def prefunc(): pass
def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 7,0 -> 7,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 7,16 -> 7,20
"""),

(r"""
def prefunc(): pass

def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 7,0 -> 7,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 7,16 -> 7,20
"""),

(r"""
def prefunc(): pass


def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 7,0 -> 7,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 7,16 -> 7,20
"""),

(r"""
def prefunc(): pass



def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass



def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 8,0 -> 8,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 8,16 -> 8,20
"""),

(r"""
def prefunc(): pass




def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass




def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 10,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 9,0 -> 9,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 9,16 -> 9,20
"""),

(r"""
def prefunc(): pass
def postfunc(): pass
""", '', 1, 1, None, {'pep8space': 1}, r"""def func(): pass""", r"""
def prefunc(): pass

def func(): pass

def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 3,0 -> 3,16
    .name 'func'
    .body[1]
    0] Pass .. 3,12 -> 3,16
  2] FunctionDef .. 5,0 -> 5,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 5,16 -> 5,20
"""),

(r"""
def prefunc(): pass
def postfunc(): pass
""", '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def func(): pass""", r"""
def prefunc(): pass
def func(): pass
def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 2,0 -> 2,16
    .name 'func'
    .body[1]
    0] Pass .. 2,12 -> 2,16
  2] FunctionDef .. 3,0 -> 3,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 3,16 -> 3,20
"""),

(r"""
def prefunc(): pass

def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass
""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 7,0 -> 7,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 7,16 -> 7,20
"""),

(r"""
def prefunc(): pass

def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass

""", r"""
def prefunc(): pass


def func(): pass



def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 8,0 -> 8,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 8,16 -> 8,20
"""),

(r"""
class cls:
    '''Class
       docstring'''
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    '''Class
       docstring'''

    def meth(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] ClassDef .. 1,0 -> 5,20
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 3,19
      .value Constant 'Class\n       docstring' .. 2,4 -> 3,19
    1] FunctionDef .. 5,4 -> 5,20
      .name 'meth'
      .body[1]
      0] Pass .. 5,16 -> 5,20
"""),

(r"""
class cls:
    '''Class
       docstring'''
""", 'body[0]', 1, 1, None, {}, r"""
def meth(): pass""", r"""
class cls:
    '''Class
       docstring'''

    def meth(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] ClassDef .. 1,0 -> 5,20
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 3,19
      .value Constant 'Class\n       docstring' .. 2,4 -> 3,19
    1] FunctionDef .. 5,4 -> 5,20
      .name 'meth'
      .body[1]
      0] Pass .. 5,16 -> 5,20
"""),

(r"""
class cls:
    '''Class
       docstring'''
""", 'body[0]', 1, 1, None, {}, r"""

def meth(): pass""", r"""
class cls:
    '''Class
       docstring'''


    def meth(): pass
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,20
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 3,19
      .value Constant 'Class\n       docstring' .. 2,4 -> 3,19
    1] FunctionDef .. 6,4 -> 6,20
      .name 'meth'
      .body[1]
      0] Pass .. 6,16 -> 6,20
"""),

(r"""
class cls:
    def premeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,20
    .name 'cls'
    .body[2]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
"""),

(r"""
class cls:
    def premeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""
def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,20
    .name 'cls'
    .body[2]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
"""),

(r"""
class cls:
    def premeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""

def meth(): pass""", r"""
class cls:
    def premeth(): pass


    def meth(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] ClassDef .. 1,0 -> 5,20
    .name 'cls'
    .body[2]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 5,4 -> 5,20
      .name 'meth'
      .body[1]
      0] Pass .. 5,16 -> 5,20
"""),

(r"""
class cls:
    def postmeth(): pass
""", 'body[0]', 0, 0, None, {}, r"""def meth(): pass""", r"""
class cls:
    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,24
    .name 'cls'
    .body[2]
    0] FunctionDef .. 2,4 -> 2,20
      .name 'meth'
      .body[1]
      0] Pass .. 2,16 -> 2,20
    1] FunctionDef .. 4,4 -> 4,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 4,20 -> 4,24
"""),

(r"""
class cls:
    def postmeth(): pass
""", 'body[0]', 0, 0, None, {}, r"""def meth(): pass
""", r"""
class cls:
    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,24
    .name 'cls'
    .body[2]
    0] FunctionDef .. 2,4 -> 2,20
      .name 'meth'
      .body[1]
      0] Pass .. 2,16 -> 2,20
    1] FunctionDef .. 4,4 -> 4,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 4,20 -> 4,24
"""),

(r"""
class cls:
    def postmeth(): pass
""", 'body[0]', 0, 0, None, {}, r"""def meth(): pass

""", r"""
class cls:
    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,24
    .name 'cls'
    .body[2]
    0] FunctionDef .. 2,4 -> 2,20
      .name 'meth'
      .body[1]
      0] Pass .. 2,16 -> 2,20
    1] FunctionDef .. 4,4 -> 4,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 4,20 -> 4,24
"""),

(r"""
class cls:
    def postmeth(): pass
""", 'body[0]', 0, 0, None, {}, r"""def meth(): pass


""", r"""
class cls:
    def meth(): pass


    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] ClassDef .. 1,0 -> 5,24
    .name 'cls'
    .body[2]
    0] FunctionDef .. 2,4 -> 2,20
      .name 'meth'
      .body[1]
      0] Pass .. 2,16 -> 2,20
    1] FunctionDef .. 5,4 -> 5,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 5,20 -> 5,24
"""),

(r"""
class cls:
    def premeth(): pass
    def postmeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] FunctionDef .. 6,4 -> 6,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 6,20 -> 6,24
"""),

(r"""
class cls:
    def premeth(): pass

    def postmeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] FunctionDef .. 6,4 -> 6,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 6,20 -> 6,24
"""),

(r"""
class cls:
    def premeth(): pass


    def postmeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass


    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] FunctionDef .. 7,4 -> 7,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 7,20 -> 7,24
"""),

(r"""
class cls:
    def premeth(): pass



    def postmeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass



    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] ClassDef .. 1,0 -> 8,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] FunctionDef .. 8,4 -> 8,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 8,20 -> 8,24
"""),

(r"""
class cls:
    def premeth(): pass
    def postmeth(): pass
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass
    def meth(): pass
    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 3,4 -> 3,20
      .name 'meth'
      .body[1]
      0] Pass .. 3,16 -> 3,20
    2] FunctionDef .. 4,4 -> 4,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 4,20 -> 4,24
"""),

(r"""
class cls:
    def premeth(): pass  # post
    # pre
    def postmeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass  # post

    def meth(): pass

    # pre
    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] FunctionDef .. 7,4 -> 7,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 7,20 -> 7,24
"""),

(r"""
class cls:
    def premeth(): pass  \
    # post
    \
    def postmeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass  \
    # post

    def meth(): pass

    \
    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] ClassDef .. 1,0 -> 8,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 5,4 -> 5,20
      .name 'meth'
      .body[1]
      0] Pass .. 5,16 -> 5,20
    2] FunctionDef .. 8,4 -> 8,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 8,20 -> 8,24
"""),

(r"""
class cls:
    def premeth(): pass
    \

    \
    def postmeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass

    \

    \
    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 10,0
  .body[1]
  0] ClassDef .. 1,0 -> 9,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] FunctionDef .. 9,4 -> 9,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 9,20 -> 9,24
"""),

(r"""
class cls:
    def premeth(): pass

    # pre
    def meth(): pass  # post

    def postmeth(): pass
""", 'body[0]', 1, 2, None, {'precomms': False}, r"""def newmeth(): pass""", r"""
class cls:
    def premeth(): pass

    # pre
    def newmeth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 5,4 -> 5,23
      .name 'newmeth'
      .body[1]
      0] Pass .. 5,19 -> 5,23
    2] FunctionDef .. 7,4 -> 7,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 7,20 -> 7,24
"""),

(r"""
class cls:
    def premeth(): pass
    def postmeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""i = 1""", r"""
class cls:
    def premeth(): pass

    i = 1

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] Assign .. 4,4 -> 4,9
      .targets[1]
      0] Name 'i' Store .. 4,4 -> 4,5
      .value Constant 1 .. 4,8 -> 4,9
    2] FunctionDef .. 6,4 -> 6,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 6,20 -> 6,24
"""),

(r"""
def prefunc(): pass
def postfunc(): pass
""", '', 1, 1, None, {}, r"""i = 1""", r"""
def prefunc(): pass


i = 1


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] Assign .. 4,0 -> 4,5
    .targets[1]
    0] Name 'i' Store .. 4,0 -> 4,1
    .value Constant 1 .. 4,4 -> 4,5
  2] FunctionDef .. 7,0 -> 7,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 7,16 -> 7,20
"""),

(r"""
i
j
k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
i
# pre
j  # post
k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
i
# pre
j  # post
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
i
# pre
l
# post
k
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 3,0 -> 3,1
    .value Name 'l' Load .. 3,0 -> 3,1
  2] Expr .. 5,0 -> 5,1
    .value Name 'k' Load .. 5,0 -> 5,1
"""),

(r"""
i
# pre
j  # post
k
""", '', 1, 2, None, {}, r"""# pre2
l  # post2""", r"""
i
# pre2
l  # post2
k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 3,0 -> 3,1
    .value Name 'l' Load .. 3,0 -> 3,1
  2] Expr .. 4,0 -> 4,1
    .value Name 'k' Load .. 4,0 -> 4,1
"""),

(r"""
i
# pre
j  # post
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre2
l  # post2""", r"""
i
# pre
# pre2
l  # post2
# post
k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value Name 'l' Load .. 4,0 -> 4,1
  2] Expr .. 6,0 -> 6,1
    .value Name 'k' Load .. 6,0 -> 6,1
"""),

(r"""
if 1:
    i
    j
    k
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i
    # pre
    j  # post
    k
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i
    # pre
    j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
if 1:
    i
    # pre
    l
    # post
    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] If .. 1,0 -> 6,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    2] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
if 1:
    i
    # pre
    j  # post
    k
""", 'body[0]', 1, 2, None, {}, r"""# pre2
l  # post2""", r"""
if 1:
    i
    # pre2
    l  # post2
    k
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    2] Expr .. 5,4 -> 5,5
      .value Name 'k' Load .. 5,4 -> 5,5
"""),

(r"""
if 1:
    i
    # pre
    j  # post
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre2
l  # post2""", r"""
if 1:
    i
    # pre
    # pre2
    l  # post2
    # post
    k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] If .. 1,0 -> 7,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'l' Load .. 5,4 -> 5,5
    2] Expr .. 7,4 -> 7,5
      .value Name 'k' Load .. 7,4 -> 7,5
"""),

(r"""
i \
# pre-before
j  # post-before
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
i \
# pre-before
l
# post-before
k
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 3,0 -> 3,1
    .value Name 'l' Load .. 3,0 -> 3,1
  2] Expr .. 5,0 -> 5,1
    .value Name 'k' Load .. 5,0 -> 5,1
"""),

(r"""
i \
# pre-before
j \
# post-line
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
i \
# pre-before
l
\
# post-line
k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 3,0 -> 3,1
    .value Name 'l' Load .. 3,0 -> 3,1
  2] Expr .. 6,0 -> 6,1
    .value Name 'k' Load .. 6,0 -> 6,1
"""),

(r"""
i
# pre-before
j \
# post-line
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
i
# pre-before
l
\
# post-line
k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 3,0 -> 3,1
    .value Name 'l' Load .. 3,0 -> 3,1
  2] Expr .. 6,0 -> 6,1
    .value Name 'k' Load .. 6,0 -> 6,1
"""),

(r"""
i \

j \
# post-line
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
i \

l
\
# post-line
k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 3,0 -> 3,1
    .value Name 'l' Load .. 3,0 -> 3,1
  2] Expr .. 6,0 -> 6,1
    .value Name 'k' Load .. 6,0 -> 6,1
"""),

(r"""
i \
# pre-before
j  # post-before
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre
l  # post""", r"""
i \
# pre-before
# pre
l  # post
# post-before
k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value Name 'l' Load .. 4,0 -> 4,1
  2] Expr .. 6,0 -> 6,1
    .value Name 'k' Load .. 6,0 -> 6,1
"""),

(r"""
i \
# pre-before
j \
# post-line
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre
l  # post""", r"""
i \
# pre-before
# pre
l  # post
\
# post-line
k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value Name 'l' Load .. 4,0 -> 4,1
  2] Expr .. 7,0 -> 7,1
    .value Name 'k' Load .. 7,0 -> 7,1
"""),

(r"""
i
# pre-before
j \
# post-line
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre
l  # post""", r"""
i
# pre-before
# pre
l  # post
\
# post-line
k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value Name 'l' Load .. 4,0 -> 4,1
  2] Expr .. 7,0 -> 7,1
    .value Name 'k' Load .. 7,0 -> 7,1
"""),

(r"""
i \

j \
# post-line
k
""", '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre
l  # post""", r"""
i \

# pre
l  # post
\
# post-line
k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value Name 'l' Load .. 4,0 -> 4,1
  2] Expr .. 7,0 -> 7,1
    .value Name 'k' Load .. 7,0 -> 7,1
"""),

(r"""
if 1:
    i \
    # pre-before
    j  # post-before
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
if 1:
    i \
    # pre-before
    l
    # post-before
    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] If .. 1,0 -> 6,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    2] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
if 1:
    i \
    # pre-before
    j \
    # post-line
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
if 1:
    i \
    # pre-before
    l
    \
    # post-line
    k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] If .. 1,0 -> 7,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    2] Expr .. 7,4 -> 7,5
      .value Name 'k' Load .. 7,4 -> 7,5
"""),

(r"""
if 1:
    i
    # pre-before
    j \
    # post-line
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
if 1:
    i
    # pre-before
    l
    \
    # post-line
    k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] If .. 1,0 -> 7,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    2] Expr .. 7,4 -> 7,5
      .value Name 'k' Load .. 7,4 -> 7,5
"""),

(r"""
if 1:
    i \

    j \
    # post-line
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""l""", r"""
if 1:
    i \

    l
    \
    # post-line
    k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] If .. 1,0 -> 7,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    2] Expr .. 7,4 -> 7,5
      .value Name 'k' Load .. 7,4 -> 7,5
"""),

(r"""
if 1:
    i \
    # pre-before
    j  # post-before
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre
l  # post""", r"""
if 1:
    i \
    # pre-before
    # pre
    l  # post
    # post-before
    k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] If .. 1,0 -> 7,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'l' Load .. 5,4 -> 5,5
    2] Expr .. 7,4 -> 7,5
      .value Name 'k' Load .. 7,4 -> 7,5
"""),

(r"""
if 1:
    i \
    # pre-before
    j \
    # post-line
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre
l  # post""", r"""
if 1:
    i \
    # pre-before
    # pre
    l  # post
    \
    # post-line
    k
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] If .. 1,0 -> 8,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'l' Load .. 5,4 -> 5,5
    2] Expr .. 8,4 -> 8,5
      .value Name 'k' Load .. 8,4 -> 8,5
"""),

(r"""
if 1:
    i
    # pre-before
    j \
    # post-line
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre
l  # post""", r"""
if 1:
    i
    # pre-before
    # pre
    l  # post
    \
    # post-line
    k
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] If .. 1,0 -> 8,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'l' Load .. 5,4 -> 5,5
    2] Expr .. 8,4 -> 8,5
      .value Name 'k' Load .. 8,4 -> 8,5
"""),

(r"""
if 1:
    i \

    j \
    # post-line
    k
""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""# pre
l  # post""", r"""
if 1:
    i \

    # pre
    l  # post
    \
    # post-line
    k
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] If .. 1,0 -> 8,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'l' Load .. 5,4 -> 5,5
    2] Expr .. 8,4 -> 8,5
      .value Name 'k' Load .. 8,4 -> 8,5
"""),

(r"""
i
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
i
j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
i
j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
"""),

(r"""
if 1:
    i
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
if 1:
    i
    j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i
    j
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
"""),

(r"""
i
j
k
""", '', 1, 2, None, {}, r"""if 1:
    pass""", r"""
i
if 1:
    pass
k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] If .. 2,0 -> 3,8
    .test Constant 1 .. 2,3 -> 2,4
    .body[1]
    0] Pass .. 3,4 -> 3,8
  2] Expr .. 4,0 -> 4,1
    .value Name 'k' Load .. 4,0 -> 4,1
"""),

(r"""
i
if 1: pass
k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
i
if 1:
    pass
k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
i
if 1:
    pass
k
""", '', 1, 2, None, {}, r"""if 2: break""", r"""
i
if 2: break
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] If .. 2,0 -> 2,11
    .test Constant 2 .. 2,3 -> 2,4
    .body[1]
    0] Break .. 2,6 -> 2,11
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
i
j
k
""", '', 1, 2, None, {}, r"""x
if 1:
    pass
z""", r"""
i
x
if 1:
    pass
z
k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[5]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'x' Load .. 2,0 -> 2,1
  2] If .. 3,0 -> 4,8
    .test Constant 1 .. 3,3 -> 3,4
    .body[1]
    0] Pass .. 4,4 -> 4,8
  3] Expr .. 5,0 -> 5,1
    .value Name 'z' Load .. 5,0 -> 5,1
  4] Expr .. 6,0 -> 6,1
    .value Name 'k' Load .. 6,0 -> 6,1
"""),

(r"""
i
if 1: pass
k
""", '', 1, 2, None, {}, r"""x
l
z""", r"""
i
x
l
z
k
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[5]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'x' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'l' Load .. 3,0 -> 3,1
  3] Expr .. 4,0 -> 4,1
    .value Name 'z' Load .. 4,0 -> 4,1
  4] Expr .. 5,0 -> 5,1
    .value Name 'k' Load .. 5,0 -> 5,1
"""),

(r"""
i
if 1:
    pass
k
""", '', 1, 2, None, {}, r"""x
l
z""", r"""
i
x
l
z
k
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[5]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'x' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'l' Load .. 3,0 -> 3,1
  3] Expr .. 4,0 -> 4,1
    .value Name 'z' Load .. 4,0 -> 4,1
  4] Expr .. 5,0 -> 5,1
    .value Name 'k' Load .. 5,0 -> 5,1
"""),

(r"""
i
if 1:
    pass
k
""", '', 1, 2, None, {}, r"""x
if 2: break
z""", r"""
i
x
if 2: break
z
k
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[5]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'x' Load .. 2,0 -> 2,1
  2] If .. 3,0 -> 3,11
    .test Constant 2 .. 3,3 -> 3,4
    .body[1]
    0] Break .. 3,6 -> 3,11
  3] Expr .. 4,0 -> 4,1
    .value Name 'z' Load .. 4,0 -> 4,1
  4] Expr .. 5,0 -> 5,1
    .value Name 'k' Load .. 5,0 -> 5,1
"""),

(r"""
if 2:
    i
    j
    k
""", 'body[0]', 1, 2, None, {}, r"""if 1:
    pass""", r"""
if 2:
    i
    if 1:
        pass
    k
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test Constant 2 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 4,12
      .test Constant 1 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 4,8 -> 4,12
    2] Expr .. 5,4 -> 5,5
      .value Name 'k' Load .. 5,4 -> 5,5
"""),

(r"""
if 2:
    i
    if 1: pass
    k
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 2:
    i
    l
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 2 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
if 2:
    i
    if 1:
        pass
    k
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 2:
    i
    l
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 2 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
if 2:
    i
    if 1:
        pass
    k
""", 'body[0]', 1, 2, None, {}, r"""if 2: break""", r"""
if 2:
    i
    if 2: break
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 2 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,15
      .test Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Break .. 3,10 -> 3,15
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
if 2:
    i
    j
    k
""", 'body[0]', 1, 2, None, {}, r"""x
if 1:
    pass
z""", r"""
if 2:
    i
    x
    if 1:
        pass
    z
    k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] If .. 1,0 -> 7,5
    .test Constant 2 .. 1,3 -> 1,4
    .body[5]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'x' Load .. 3,4 -> 3,5
    2] If .. 4,4 -> 5,12
      .test Constant 1 .. 4,7 -> 4,8
      .body[1]
      0] Pass .. 5,8 -> 5,12
    3] Expr .. 6,4 -> 6,5
      .value Name 'z' Load .. 6,4 -> 6,5
    4] Expr .. 7,4 -> 7,5
      .value Name 'k' Load .. 7,4 -> 7,5
"""),

(r"""
if 2:
    i
    if 1: pass
    k
""", 'body[0]', 1, 2, None, {}, r"""x
l
z""", r"""
if 2:
    i
    x
    l
    z
    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] If .. 1,0 -> 6,5
    .test Constant 2 .. 1,3 -> 1,4
    .body[5]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'x' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    3] Expr .. 5,4 -> 5,5
      .value Name 'z' Load .. 5,4 -> 5,5
    4] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
if 2:
    i
    if 1:
        pass
    k
""", 'body[0]', 1, 2, None, {}, r"""x
l
z""", r"""
if 2:
    i
    x
    l
    z
    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] If .. 1,0 -> 6,5
    .test Constant 2 .. 1,3 -> 1,4
    .body[5]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'x' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'l' Load .. 4,4 -> 4,5
    3] Expr .. 5,4 -> 5,5
      .value Name 'z' Load .. 5,4 -> 5,5
    4] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
if 2:
    i
    if 1:
        pass
    k
""", 'body[0]', 1, 2, None, {}, r"""x
if 2: break
z""", r"""
if 2:
    i
    x
    if 2: break
    z
    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] If .. 1,0 -> 6,5
    .test Constant 2 .. 1,3 -> 1,4
    .body[5]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'x' Load .. 3,4 -> 3,5
    2] If .. 4,4 -> 4,15
      .test Constant 2 .. 4,7 -> 4,8
      .body[1]
      0] Break .. 4,10 -> 4,15
    3] Expr .. 5,4 -> 5,5
      .value Name 'z' Load .. 5,4 -> 5,5
    4] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
i ; j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l

""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
"""),

(r"""
i \
 ; j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l

""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
"""),

(r"""
i ; \
 j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l

""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
"""),

(r"""
i \
; \
j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l

""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
"""),

(r"""
if 1:
    i ; j
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l

""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i \
    ; j
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l

""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i ; \
    j
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l

""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i \
    ; \
    j
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l

""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
"""),

(r"""
i ; j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
i \
 ; j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
i ; \
 j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
i \
; \
j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
if 1:
    i ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i \
     ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i ; \
     j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    i \
     ; \
     j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: \
    i ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: \
    i \
     ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: \
    i ; \
     j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: \
    i \
     ; \
     j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
i ;
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
i ;  # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
# post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
i ; \
 # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
i \
 ; \
 # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i ;
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
if 1:
    i ;  # post
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
if 1:
    i ; \
 # post
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
if 1:
    i \
 ; \
 # post
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
# pre
i ; \
 j
""", '', 0, 1, None, {}, r"""**DEL**""", r"""
j
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
# pre
i ; \
 j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
if 1: pass
else: \
  # pre
  i ; \
    j
""", 'body[0]', 0, 1, 'orelse', {}, r"""**DEL**""", r"""
if 1: pass
else:
  j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,3
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 3,2 -> 3,3
      .value Name 'j' Load .. 3,2 -> 3,3
"""),

(r"""
if 1: pass
else:
  \
  # pre
  i ; \
    j
  k
""", 'body[0]', 0, 1, 'orelse', {}, r"""**DEL**""", r"""
if 1: pass
else:

  j
  k
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,3
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[2]
    0] Expr .. 4,2 -> 4,3
      .value Name 'j' Load .. 4,2 -> 4,3
    1] Expr .. 5,2 -> 5,3
      .value Name 'k' Load .. 5,2 -> 5,3
"""),

(r"""
if 1: pass
else:
    k
    \
  # pre
    i ; \
    j
""", 'body[0]', 1, 2, 'orelse', {}, r"""**DEL**""", r"""
if 1: pass
else:
    k

    j
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[2]
    0] Expr .. 3,4 -> 3,5
      .value Name 'k' Load .. 3,4 -> 3,5
    1] Expr .. 5,4 -> 5,5
      .value Name 'j' Load .. 5,4 -> 5,5
"""),

(r"""
if 1: pass
else:
  # pre
  i \
 ; \
    j
""", 'body[0]', 0, 1, 'orelse', {}, r"""**DEL**""", r"""
if 1: pass
else:
  j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,3
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 3,2 -> 3,3
      .value Name 'j' Load .. 3,2 -> 3,3
"""),

(r"""
# pre
i ; j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
# pre
i \
 ; j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
# pre
i ; \
 j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
# pre
i \
; \
j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'j' Load .. 2,0 -> 2,1
"""),

(r"""
if 1:
    # pre
    i ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    # pre
    i \
     ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    # pre
    i ; \
     j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1:
    # pre
    i \
     ; \
     j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: \
    # pre
    i ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: \
    # pre
    i \
     ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: \
    # pre
    i ; \
     j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
if 1: \
    # pre
    i \
     ; \
     j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'j' Load .. 3,4 -> 3,5
"""),

(r"""
# pre
i ;
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
# pre
i ;  # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
# post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
# pre
i ; \
 # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
# pre
i \
 ; \
 # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value Name 'l' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    # pre
    i ;
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
if 1:
    # pre
    i ;  # post
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
# post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
if 1:
    # pre
    i ; \
 # post
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
if 1:
    # pre
    i \
 ; \
 # post
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value Name 'l' Load .. 2,4 -> 2,5
"""),

(r"""
def prefunc(): pass
pass
def postfunc(): pass
""", '', 1, 2, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 7,0 -> 7,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 7,16 -> 7,20
"""),

(r"""
def prefunc(): pass
# pre
pass  # post
def postfunc(): pass
""", '', 1, 2, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] FunctionDef .. 7,0 -> 7,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 7,16 -> 7,20
"""),

(r"""
def prefunc(): pass
i ; j
def postfunc(): pass
""", '', 1, 2, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


j
def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[4]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] Expr .. 7,0 -> 7,1
    .value Name 'j' Load .. 7,0 -> 7,1
  3] FunctionDef .. 8,0 -> 8,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 8,16 -> 8,20
"""),

(r"""
def prefunc(): pass
i ; j
def postfunc(): pass
""", '', 2, 3, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass
i


def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[4]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] Expr .. 2,0 -> 2,1
    .value Name 'i' Load .. 2,0 -> 2,1
  2] FunctionDef .. 5,0 -> 5,16
    .name 'func'
    .body[1]
    0] Pass .. 5,12 -> 5,16
  3] FunctionDef .. 8,0 -> 8,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 8,16 -> 8,20
"""),

(r"""
def prefunc(): pass
# pre
i ; j # post
def postfunc(): pass
""", '', 1, 2, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


j # post
def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[4]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
  2] Expr .. 7,0 -> 7,1
    .value Name 'j' Load .. 7,0 -> 7,1
  3] FunctionDef .. 8,0 -> 8,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 8,16 -> 8,20
"""),

(r"""
def prefunc(): pass
# pre
i ; j # post
def postfunc(): pass
""", '', 2, 3, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass
# pre
i


def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 10,0
  .body[4]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] Expr .. 3,0 -> 3,1
    .value Name 'i' Load .. 3,0 -> 3,1
  2] FunctionDef .. 6,0 -> 6,16
    .name 'func'
    .body[1]
    0] Pass .. 6,12 -> 6,16
  3] FunctionDef .. 9,0 -> 9,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 9,16 -> 9,20
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,19
    .name 'prefunc'
    .body[1]
    0] Pass .. 1,15 -> 1,19
  1] FunctionDef .. 4,0 -> 4,16
    .name 'func'
    .body[1]
    0] Pass .. 4,12 -> 4,16
"""),

(r"""
def postfunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass""", r"""
def func(): pass


def postfunc(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] FunctionDef .. 1,0 -> 1,16
    .name 'func'
    .body[1]
    0] Pass .. 1,12 -> 1,16
  1] FunctionDef .. 4,0 -> 4,20
    .name 'postfunc'
    .body[1]
    0] Pass .. 4,16 -> 4,20
"""),

(r"""
class cls:
    def premeth(): pass
    pass
    def postmeth(): pass
""", 'body[0]', 1, 2, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] FunctionDef .. 6,4 -> 6,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 6,20 -> 6,24
"""),

(r"""
class cls:
    def premeth(): pass
    # pre
    pass  # post
    def postmeth(): pass
""", 'body[0]', 1, 2, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,24
    .name 'cls'
    .body[3]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] FunctionDef .. 6,4 -> 6,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 6,20 -> 6,24
"""),

(r"""
class cls:
    def premeth(): pass
    i ; j
    def postmeth(): pass
""", 'body[0]', 1, 2, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass

    j
    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,24
    .name 'cls'
    .body[4]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] Expr .. 6,4 -> 6,5
      .value Name 'j' Load .. 6,4 -> 6,5
    3] FunctionDef .. 7,4 -> 7,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 7,20 -> 7,24
"""),

(r"""
class cls:
    def premeth(): pass
    i ; j
    def postmeth(): pass
""", 'body[0]', 2, 3, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass
    i

    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,24
    .name 'cls'
    .body[4]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] Expr .. 3,4 -> 3,5
      .value Name 'i' Load .. 3,4 -> 3,5
    2] FunctionDef .. 5,4 -> 5,20
      .name 'meth'
      .body[1]
      0] Pass .. 5,16 -> 5,20
    3] FunctionDef .. 7,4 -> 7,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 7,20 -> 7,24
"""),

(r"""
class cls:
    def premeth(): pass
    # pre
    i ; j # post
    def postmeth(): pass
""", 'body[0]', 1, 2, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass

    j # post
    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,24
    .name 'cls'
    .body[4]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 4,4 -> 4,20
      .name 'meth'
      .body[1]
      0] Pass .. 4,16 -> 4,20
    2] Expr .. 6,4 -> 6,5
      .value Name 'j' Load .. 6,4 -> 6,5
    3] FunctionDef .. 7,4 -> 7,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 7,20 -> 7,24
"""),

(r"""
class cls:
    def premeth(): pass
    # pre
    i ; j # post
    def postmeth(): pass
""", 'body[0]', 2, 3, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass
    # pre
    i

    def meth(): pass

    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] ClassDef .. 1,0 -> 8,24
    .name 'cls'
    .body[4]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] Expr .. 4,4 -> 4,5
      .value Name 'i' Load .. 4,4 -> 4,5
    2] FunctionDef .. 6,4 -> 6,20
      .name 'meth'
      .body[1]
      0] Pass .. 6,16 -> 6,20
    3] FunctionDef .. 8,4 -> 8,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 8,20 -> 8,24
"""),

(r"""
if 1:
    def premeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
if 1:
    def premeth(): pass


    def meth(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,20
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] FunctionDef .. 2,4 -> 2,23
      .name 'premeth'
      .body[1]
      0] Pass .. 2,19 -> 2,23
    1] FunctionDef .. 5,4 -> 5,20
      .name 'meth'
      .body[1]
      0] Pass .. 5,16 -> 5,20
"""),

(r"""
if 1:
    def postmeth(): pass
""", 'body[0]', 0, 0, None, {}, r"""def meth(): pass""", r"""
if 1:
    def meth(): pass


    def postmeth(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,24
    .test Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] FunctionDef .. 2,4 -> 2,20
      .name 'meth'
      .body[1]
      0] Pass .. 2,16 -> 2,20
    1] FunctionDef .. 5,4 -> 5,24
      .name 'postmeth'
      .body[1]
      0] Pass .. 5,20 -> 5,24
"""),

(r"""
def f():
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
def f():
    i

    def g(): pass

    j
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] FunctionDef .. 1,0 -> 6,5
    .name 'f'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'g'
      .body[1]
      0] Pass .. 4,13 -> 4,17
    2] Expr .. 6,4 -> 6,5
      .value Name 'j' Load .. 6,4 -> 6,5
"""),

(r"""
async def f():
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
async def f():
    i

    def g(): pass

    j
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] AsyncFunctionDef .. 1,0 -> 6,5
    .name 'f'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'g'
      .body[1]
      0] Pass .. 4,13 -> 4,17
    2] Expr .. 6,4 -> 6,5
      .value Name 'j' Load .. 6,4 -> 6,5
"""),

(r"""
class cls:
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
class cls:
    i

    def g(): pass

    j
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,5
    .name 'cls'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'g'
      .body[1]
      0] Pass .. 4,13 -> 4,17
    2] Expr .. 6,4 -> 6,5
      .value Name 'j' Load .. 6,4 -> 6,5
"""),

(r"""
for a in b:
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
for a in b:
    i


    def g(): pass


    j
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] For .. 1,0 -> 8,5
    .target Name 'a' Store .. 1,4 -> 1,5
    .iter Name 'b' Load .. 1,9 -> 1,10
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'g'
      .body[1]
      0] Pass .. 5,13 -> 5,17
    2] Expr .. 8,4 -> 8,5
      .value Name 'j' Load .. 8,4 -> 8,5
"""),

(r"""
async for a in b:
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
async for a in b:
    i


    def g(): pass


    j
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] AsyncFor .. 1,0 -> 8,5
    .target Name 'a' Store .. 1,10 -> 1,11
    .iter Name 'b' Load .. 1,15 -> 1,16
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'g'
      .body[1]
      0] Pass .. 5,13 -> 5,17
    2] Expr .. 8,4 -> 8,5
      .value Name 'j' Load .. 8,4 -> 8,5
"""),

(r"""
while a:
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
while a:
    i


    def g(): pass


    j
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] While .. 1,0 -> 8,5
    .test Name 'a' Load .. 1,6 -> 1,7
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'g'
      .body[1]
      0] Pass .. 5,13 -> 5,17
    2] Expr .. 8,4 -> 8,5
      .value Name 'j' Load .. 8,4 -> 8,5
"""),

(r"""
if a:
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
if a:
    i


    def g(): pass


    j
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] If .. 1,0 -> 8,5
    .test Name 'a' Load .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'g'
      .body[1]
      0] Pass .. 5,13 -> 5,17
    2] Expr .. 8,4 -> 8,5
      .value Name 'j' Load .. 8,4 -> 8,5
"""),

(r"""
with a:
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
with a:
    i


    def g(): pass


    j
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] With .. 1,0 -> 8,5
    .items[1]
    0] withitem .. 1,5 -> 1,6
      .context_expr
        Name 'a' Load .. 1,5 -> 1,6
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'g'
      .body[1]
      0] Pass .. 5,13 -> 5,17
    2] Expr .. 8,4 -> 8,5
      .value Name 'j' Load .. 8,4 -> 8,5
"""),

(r"""
async with a:
    i
    j
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
async with a:
    i


    def g(): pass


    j
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] AsyncWith .. 1,0 -> 8,5
    .items[1]
    0] withitem .. 1,11 -> 1,12
      .context_expr
        Name 'a' Load .. 1,11 -> 1,12
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'g'
      .body[1]
      0] Pass .. 5,13 -> 5,17
    2] Expr .. 8,4 -> 8,5
      .value Name 'j' Load .. 8,4 -> 8,5
"""),

(r"""
match a:
    case b:
        i
        j
""", 'body[0].cases[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
match a:
    case b:
        i


        def g(): pass


        j
""", r"""
Module .. ROOT 0,0 -> 10,0
  .body[1]
  0] Match .. 1,0 -> 9,9
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,4 -> 9,9
      .pattern MatchAs .. 2,9 -> 2,10
        .name 'b'
      .body[3]
      0] Expr .. 3,8 -> 3,9
        .value Name 'i' Load .. 3,8 -> 3,9
      1] FunctionDef .. 6,8 -> 6,21
        .name 'g'
        .body[1]
        0] Pass .. 6,17 -> 6,21
      2] Expr .. 9,8 -> 9,9
        .value Name 'j' Load .. 9,8 -> 9,9
"""),

(r"""
try:
    i
    j
finally:
    pass
""", 'body[0]', 1, 1, None, {}, r"""def g(): pass""", r"""
try:
    i


    def g(): pass


    j
finally:
    pass
""", r"""
Module .. ROOT 0,0 -> 11,0
  .body[1]
  0] Try .. 1,0 -> 10,8
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'g'
      .body[1]
      0] Pass .. 5,13 -> 5,17
    2] Expr .. 8,4 -> 8,5
      .value Name 'j' Load .. 8,4 -> 8,5
    .finalbody[1]
    0] Pass .. 10,4 -> 10,8
"""),

(r"""
def f():
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
def f():
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] FunctionDef .. 1,0 -> 4,5
    .name 'f'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
async def f():
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
async def f():
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] AsyncFunctionDef .. 1,0 -> 4,5
    .name 'f'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
class cls:
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
class cls:
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,5
    .name 'cls'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
for a in b:
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
for a in b:
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] For .. 1,0 -> 4,5
    .target Name 'a' Store .. 1,4 -> 1,5
    .iter Name 'b' Load .. 1,9 -> 1,10
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
async for a in b:
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
async for a in b:
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] AsyncFor .. 1,0 -> 4,5
    .target Name 'a' Store .. 1,10 -> 1,11
    .iter Name 'b' Load .. 1,15 -> 1,16
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
while a:
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
while a:
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] While .. 1,0 -> 4,5
    .test Name 'a' Load .. 1,6 -> 1,7
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
if a:
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
if a:
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Name 'a' Load .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
with a:
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
with a:
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] With .. 1,0 -> 4,5
    .items[1]
    0] withitem .. 1,5 -> 1,6
      .context_expr
        Name 'a' Load .. 1,5 -> 1,6
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
async with a:
    i
    j
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
async with a:
    i
    def g(): pass
    j
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] AsyncWith .. 1,0 -> 4,5
    .items[1]
    0] withitem .. 1,11 -> 1,12
      .context_expr
        Name 'a' Load .. 1,11 -> 1,12
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
"""),

(r"""
match a:
    case b:
        i
        j
""", 'body[0].cases[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
match a:
    case b:
        i
        def g(): pass
        j
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] Match .. 1,0 -> 5,9
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,4 -> 5,9
      .pattern MatchAs .. 2,9 -> 2,10
        .name 'b'
      .body[3]
      0] Expr .. 3,8 -> 3,9
        .value Name 'i' Load .. 3,8 -> 3,9
      1] FunctionDef .. 4,8 -> 4,21
        .name 'g'
        .body[1]
        0] Pass .. 4,17 -> 4,21
      2] Expr .. 5,8 -> 5,9
        .value Name 'j' Load .. 5,8 -> 5,9
"""),

(r"""
try:
    i
    j
finally:
    pass
""", 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def g(): pass""", r"""
try:
    i
    def g(): pass
    j
finally:
    pass
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] Try .. 1,0 -> 6,8
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 3,4 -> 3,17
      .name 'g'
      .body[1]
      0] Pass .. 3,13 -> 3,17
    2] Expr .. 4,4 -> 4,5
      .value Name 'j' Load .. 4,4 -> 4,5
    .finalbody[1]
    0] Pass .. 6,4 -> 6,8
"""),

(r"""
if 1:
    i
    j
""", 'body[0]', 1, 1, None, {'pep8space': 1}, r"""def g(): pass""", r"""
if 1:
    i

    def g(): pass

    j
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] If .. 1,0 -> 6,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'g'
      .body[1]
      0] Pass .. 4,13 -> 4,17
    2] Expr .. 6,4 -> 6,5
      .value Name 'j' Load .. 6,4 -> 6,5
"""),

(r"""
i ; j ; k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
i ; \
 j \
 ; k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
i \
 ; j ; \
 k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
i \
 ; \
 j \
 ; \
 k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value Name 'l' Load .. 2,0 -> 2,1
  2] Expr .. 3,0 -> 3,1
    .value Name 'k' Load .. 3,0 -> 3,1
"""),

(r"""
if 1:
    i ; j ; k
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i ; \
 j ; \
 k
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i \
 ; j ; \
 k
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
if 1:
    i \
 ; \
 j \
 ; \
 k
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l
    k
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value Name 'l' Load .. 3,4 -> 3,5
    2] Expr .. 4,4 -> 4,5
      .value Name 'k' Load .. 4,4 -> 4,5
"""),

(r"""
i ; j ; k
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass


k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
  2] Expr .. 7,0 -> 7,1
    .value Name 'k' Load .. 7,0 -> 7,1
"""),

(r"""
i ; \
 j \
 ; k
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass


k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
  2] Expr .. 7,0 -> 7,1
    .value Name 'k' Load .. 7,0 -> 7,1
"""),

(r"""
i \
 ; j ; \
 k
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass


k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
  2] Expr .. 7,0 -> 7,1
    .value Name 'k' Load .. 7,0 -> 7,1
"""),

(r"""
i \
 ; \
 j \
 ; \
 k
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass


k
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[3]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
  2] Expr .. 7,0 -> 7,1
    .value Name 'k' Load .. 7,0 -> 7,1
"""),

(r"""
class cls:
    i ; j ; k
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i

    def f(): pass

    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,5
    .name 'cls'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
    2] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
class cls:
    i ; \
 j ; \
 k
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i

    def f(): pass

    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,5
    .name 'cls'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
    2] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
class cls:
    i \
 ; j ; \
 k
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i

    def f(): pass

    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,5
    .name 'cls'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
    2] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
class cls:
    i \
 ; \
 j \
 ; \
 k
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i

    def f(): pass

    k
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,5
    .name 'cls'
    .body[3]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
    2] Expr .. 6,4 -> 6,5
      .value Name 'k' Load .. 6,4 -> 6,5
"""),

(r"""
i ; j ;
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
"""),

(r"""
i ; \
 j \
 ;
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i ;


def f(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
"""),

(r"""
i \
 ; j ;
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
"""),

(r"""
i \
 ; \
 j \
 ;
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i \
 ;


def f(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 5,0 -> 5,13
    .name 'f'
    .body[1]
    0] Pass .. 5,9 -> 5,13
"""),

(r"""
class cls:
    i ; j ;
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i

    def f(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,17
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
"""),

(r"""
class cls:
    i ; \
 j ;
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i ;

    def f(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,17
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
"""),

(r"""
class cls:
    i \
 ; j ;
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i

    def f(): pass
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,17
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
"""),

(r"""
class cls:
    i \
 ; \
 j \
 ;
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i \
 ;

    def f(): pass
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] ClassDef .. 1,0 -> 5,17
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'f'
      .body[1]
      0] Pass .. 5,13 -> 5,17
"""),

(r"""
i ; j ;  # post
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i ;


def f(): pass
# post
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
"""),

(r"""
i ; \
 j \
 ;  # post
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i ;


def f(): pass
 # post
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 4,0 -> 4,13
    .name 'f'
    .body[1]
    0] Pass .. 4,9 -> 4,13
"""),

(r"""
i \
 ; j ;  # post
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i \
 ;


def f(): pass
# post
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 5,0 -> 5,13
    .name 'f'
    .body[1]
    0] Pass .. 5,9 -> 5,13
"""),

(r"""
i \
 ; \
 j \
 ;  # post
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i \
 ;


def f(): pass
 # post
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value Name 'i' Load .. 1,0 -> 1,1
  1] FunctionDef .. 5,0 -> 5,13
    .name 'f'
    .body[1]
    0] Pass .. 5,9 -> 5,13
"""),

(r"""
class cls:
    i ; j ;  # post
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i ;

    def f(): pass
# post
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,17
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
"""),

(r"""
class cls:
    i ; \
 j ;  # post
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i ;

    def f(): pass
 # post
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,17
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 4,4 -> 4,17
      .name 'f'
      .body[1]
      0] Pass .. 4,13 -> 4,17
"""),

(r"""
class cls:
    i \
 ; j ;  # post
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i \
 ;

    def f(): pass
# post
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 5,17
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'f'
      .body[1]
      0] Pass .. 5,13 -> 5,17
"""),

(r"""
class cls:
    i \
 ; \
 j \
 ;  # post
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i \
 ;

    def f(): pass
 # post
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 5,17
    .name 'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value Name 'i' Load .. 2,4 -> 2,5
    1] FunctionDef .. 5,4 -> 5,17
      .name 'f'
      .body[1]
      0] Pass .. 5,13 -> 5,17
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0]', 0, 1, 'orelse', {}, r"""break""", r"""
if 1: pass
else:
    break
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,9
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Break .. 3,4 -> 3,9
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0]', 0, 1, 'orelse', {}, r"""if 3: break""", r"""
if 1: pass
else:
    if 3: break
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,15
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 3,4 -> 3,15
      .test Constant 3 .. 3,7 -> 3,8
      .body[1]
      0] Break .. 3,10 -> 3,15
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break""", r"""
if 1: pass
elif 3: break
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,13
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 2,0 -> 2,13
      .test Constant 3 .. 2,5 -> 2,6
      .body[1]
      0] Break .. 2,8 -> 2,13
"""),

(r"""
if 1: pass
else:
    pass
""", 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break""", r"""
if 1: pass
elif 3: break
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,13
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 2,0 -> 2,13
      .test Constant 3 .. 2,5 -> 2,6
      .body[1]
      0] Break .. 2,8 -> 2,13
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 0, 1, 'orelse', {}, r"""break""", r"""
class cls:
    if 1: pass
    else:
        break
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,13
    .name 'cls'
    .body[1]
    0] If .. 2,4 -> 4,13
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] Break .. 4,8 -> 4,13
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 0, 1, 'orelse', {}, r"""if 3: break""", r"""
class cls:
    if 1: pass
    else:
        if 3: break
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 1,0 -> 4,19
    .name 'cls'
    .body[1]
    0] If .. 2,4 -> 4,19
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 4,8 -> 4,19
        .test Constant 3 .. 4,11 -> 4,12
        .body[1]
        0] Break .. 4,14 -> 4,19
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break""", r"""
class cls:
    if 1: pass
    elif 3: break
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] ClassDef .. 1,0 -> 3,17
    .name 'cls'
    .body[1]
    0] If .. 2,4 -> 3,17
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 3,4 -> 3,17
        .test Constant 3 .. 3,9 -> 3,10
        .body[1]
        0] Break .. 3,12 -> 3,17
"""),

(r"""
class cls:
    if 1: pass
    else:
        pass
""", 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break""", r"""
class cls:
    if 1: pass
    elif 3: break
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] ClassDef .. 1,0 -> 3,17
    .name 'cls'
    .body[1]
    0] If .. 2,4 -> 3,17
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 3,4 -> 3,17
        .test Constant 3 .. 3,9 -> 3,10
        .body[1]
        0] Break .. 3,12 -> 3,17
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0]', 0, 1, 'orelse', {}, r"""if 3: break
else:
    continue""", r"""
if 1: pass
else:
    if 3: break
    else:
        continue
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,16
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 3,4 -> 5,16
      .test Constant 3 .. 3,7 -> 3,8
      .body[1]
      0] Break .. 3,10 -> 3,15
      .orelse[1]
      0] Continue .. 5,8 -> 5,16
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break
else:
    continue""", r"""
if 1: pass
elif 3: break
else:
    continue
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,12
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 2,0 -> 4,12
      .test Constant 3 .. 2,5 -> 2,6
      .body[1]
      0] Break .. 2,8 -> 2,13
      .orelse[1]
      0] Continue .. 4,4 -> 4,12
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0].orelse[0]', 0, 0, 'orelse', {}, r"""if 3: break
else:
    continue""", r"""
if 1: pass
elif 2:
    pass
else:
    if 3: break
    else:
        continue
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] If .. 1,0 -> 7,16
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 2,0 -> 7,16
      .test Constant 2 .. 2,5 -> 2,6
      .body[1]
      0] Pass .. 3,4 -> 3,8
      .orelse[1]
      0] If .. 5,4 -> 7,16
        .test Constant 3 .. 5,7 -> 5,8
        .body[1]
        0] Break .. 5,10 -> 5,15
        .orelse[1]
        0] Continue .. 7,8 -> 7,16
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0].orelse[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break
else:
    continue""", r"""
if 1: pass
elif 2:
    pass
elif 3: break
else:
    continue
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] If .. 1,0 -> 6,12
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 2,0 -> 6,12
      .test Constant 2 .. 2,5 -> 2,6
      .body[1]
      0] Pass .. 3,4 -> 3,8
      .orelse[1]
      0] If .. 4,0 -> 6,12
        .test Constant 3 .. 4,5 -> 4,6
        .body[1]
        0] Break .. 4,8 -> 4,13
        .orelse[1]
        0] Continue .. 6,4 -> 6,12
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 0, 1, 'orelse', {}, r"""if 3: break
else:
    continue""", r"""
class cls:
    if 1: pass
    else:
        if 3: break
        else:
            continue
""", r"""
Module .. ROOT 0,0 -> 7,0
  .body[1]
  0] ClassDef .. 1,0 -> 6,20
    .name 'cls'
    .body[1]
    0] If .. 2,4 -> 6,20
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 4,8 -> 6,20
        .test Constant 3 .. 4,11 -> 4,12
        .body[1]
        0] Break .. 4,14 -> 4,19
        .orelse[1]
        0] Continue .. 6,12 -> 6,20
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break
else:
    continue""", r"""
class cls:
    if 1: pass
    elif 3: break
    else:
        continue
""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] ClassDef .. 1,0 -> 5,16
    .name 'cls'
    .body[1]
    0] If .. 2,4 -> 5,16
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 3,4 -> 5,16
        .test Constant 3 .. 3,9 -> 3,10
        .body[1]
        0] Break .. 3,12 -> 3,17
        .orelse[1]
        0] Continue .. 5,8 -> 5,16
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {}, r"""if 3: break
else:
    continue""", r"""
class cls:
    if 1: pass
    elif 2:
        pass
    else:
        if 3: break
        else:
            continue
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] ClassDef .. 1,0 -> 8,20
    .name 'cls'
    .body[1]
    0] If .. 2,4 -> 8,20
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 3,4 -> 8,20
        .test Constant 2 .. 3,9 -> 3,10
        .body[1]
        0] Pass .. 4,8 -> 4,12
        .orelse[1]
        0] If .. 6,8 -> 8,20
          .test Constant 3 .. 6,11 -> 6,12
          .body[1]
          0] Break .. 6,14 -> 6,19
          .orelse[1]
          0] Continue .. 8,12 -> 8,20
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break
else:
    continue""", r"""
class cls:
    if 1: pass
    elif 2:
        pass
    elif 3: break
    else:
        continue
""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,16
    .name 'cls'
    .body[1]
    0] If .. 2,4 -> 7,16
      .test Constant 1 .. 2,7 -> 2,8
      .body[1]
      0] Pass .. 2,10 -> 2,14
      .orelse[1]
      0] If .. 3,4 -> 7,16
        .test Constant 2 .. 3,9 -> 3,10
        .body[1]
        0] Pass .. 4,8 -> 4,12
        .orelse[1]
        0] If .. 5,4 -> 7,16
          .test Constant 3 .. 5,9 -> 5,10
          .body[1]
          0] Break .. 5,12 -> 5,17
          .orelse[1]
          0] Continue .. 7,8 -> 7,16
"""),

(r"""
if 1:
    pass;
""", 'body[0]', 0, 0, 'orelse', {}, r"""i""", r"""
if 1:
    pass;
else:
    i
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 2,4 -> 2,8
    .orelse[1]
    0] Expr .. 4,4 -> 4,5
      .value Name 'i' Load .. 4,4 -> 4,5
"""),

(r"""
try:
    continue
except:
    pass;
finally:
    pass
""", 'body[0]', 0, 0, 'orelse', {}, r"""i""", r"""
try:
    continue
except:
    pass;
else:
    i
finally:
    pass
""", r"""
Module .. ROOT 0,0 -> 9,0
  .body[1]
  0] Try .. 1,0 -> 8,8
    .body[1]
    0] Continue .. 2,4 -> 2,12
    .handlers[1]
    0] ExceptHandler .. 3,0 -> 4,9
      .body[1]
      0] Pass .. 4,4 -> 4,8
    .orelse[1]
    0] Expr .. 6,4 -> 6,5
      .value Name 'i' Load .. 6,4 -> 6,5
    .finalbody[1]
    0] Pass .. 8,4 -> 8,8
"""),

]  # END OF PUT_SLICE_STMT_DATA

PUT_SLICE_DATA = [
(r"""(1, 2, 3)""", 'body[0].value', 1, 2, None, {'raw': True}, r"""*z""", r"""(1, *z, 3)""", r"""
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] Expr .. 0,0 -> 0,10
    .value Tuple .. 0,0 -> 0,10
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Starred .. 0,4 -> 0,6
        .value Name 'z' Load .. 0,5 -> 0,6
        .ctx Load
      2] Constant 3 .. 0,8 -> 0,9
      .ctx Load
"""),

(r"""(1, 2, 3)""", 'body[0].value', 0, 3, None, {'raw': True}, r"""*z,""", r"""(*z,)""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[1]
      0] Starred .. 0,1 -> 0,3
        .value Name 'z' Load .. 0,2 -> 0,3
        .ctx Load
      .ctx Load
"""),

(r"""1, 2, 3""", 'body[0].value', 1, 2, None, {'raw': True}, r"""*z""", r"""1, *z, 3""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Starred .. 0,3 -> 0,5
        .value Name 'z' Load .. 0,4 -> 0,5
        .ctx Load
      2] Constant 3 .. 0,7 -> 0,8
      .ctx Load
"""),

(r"""1, 2, 3""", 'body[0].value', 0, 3, None, {'raw': True}, r"""*z,""", r"""*z,""", r"""
Module .. ROOT 0,0 -> 0,3
  .body[1]
  0] Expr .. 0,0 -> 0,3
    .value Tuple .. 0,0 -> 0,3
      .elts[1]
      0] Starred .. 0,0 -> 0,2
        .value Name 'z' Load .. 0,1 -> 0,2
        .ctx Load
      .ctx Load
"""),

(r"""{a: b, c: d, e: f}""", 'body[0].value', 1, 2, None, {'raw': True}, r"""**z""", r"""{a: b, **z, e: f}""", r"""
Module .. ROOT 0,0 -> 0,17
  .body[1]
  0] Expr .. 0,0 -> 0,17
    .value Dict .. 0,0 -> 0,17
      .keys[3]
      0] Name 'a' Load .. 0,1 -> 0,2
      1] None
      2] Name 'e' Load .. 0,12 -> 0,13
      .values[3]
      0] Name 'b' Load .. 0,4 -> 0,5
      1] Name 'z' Load .. 0,9 -> 0,10
      2] Name 'f' Load .. 0,15 -> 0,16
"""),

(r"""{a: b, c: d, e: f}""", 'body[0].value', 0, 3, None, {'raw': True}, r"""**z""", r"""{**z}""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Dict .. 0,0 -> 0,5
      .keys[1]
      0] None
      .values[1]
      0] Name 'z' Load .. 0,3 -> 0,4
"""),

(r"""{a: b, **c, **d, **e}""", 'body[0].value', 1, 3, None, {'raw': True}, r"""f: g""", r"""{a: b, f: g, **e}""", r"""
Module .. ROOT 0,0 -> 0,17
  .body[1]
  0] Expr .. 0,0 -> 0,17
    .value Dict .. 0,0 -> 0,17
      .keys[3]
      0] Name 'a' Load .. 0,1 -> 0,2
      1] Name 'f' Load .. 0,7 -> 0,8
      2] None
      .values[3]
      0] Name 'b' Load .. 0,4 -> 0,5
      1] Name 'g' Load .. 0,10 -> 0,11
      2] Name 'e' Load .. 0,15 -> 0,16
"""),

(r"""del a, b, c""", 'body[0]', 1, 3, None, {'raw': True}, r"""z""", r"""del a, z""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Delete .. 0,0 -> 0,8
    .targets[2]
    0] Name 'a' Del .. 0,4 -> 0,5
    1] Name 'z' Del .. 0,7 -> 0,8
"""),

(r"""a = b = c = d""", 'body[0]', 1, 3, None, {'raw': True}, r"""z""", r"""a = z = d""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Assign .. 0,0 -> 0,9
    .targets[2]
    0] Name 'a' Store .. 0,0 -> 0,1
    1] Name 'z' Store .. 0,4 -> 0,5
    .value Name 'd' Load .. 0,8 -> 0,9
"""),

(r"""import a, b, c""", 'body[0]', 1, 3, None, {'raw': True}, r"""z as xyz""", r"""import a, z as xyz""", r"""
Module .. ROOT 0,0 -> 0,18
  .body[1]
  0] Import .. 0,0 -> 0,18
    .names[2]
    0] alias .. 0,7 -> 0,8
      .name 'a'
    1] alias .. 0,10 -> 0,18
      .name 'z'
      .asname
        'xyz'
"""),

(r"""from mod import a, b, c""", 'body[0]', 1, 3, None, {'raw': True}, r"""z as xyz""", r"""from mod import a, z as xyz""", r"""
Module .. ROOT 0,0 -> 0,27
  .body[1]
  0] ImportFrom .. 0,0 -> 0,27
    .module 'mod'
    .names[2]
    0] alias .. 0,16 -> 0,17
      .name 'a'
    1] alias .. 0,19 -> 0,27
      .name 'z'
      .asname
        'xyz'
    .level 0
"""),

(r"""with a as a, b as b, c as c: pass""", 'body[0]', 1, 3, 'items', {'raw': True}, r"""z as xyz""", r"""with a as a, z as xyz: pass""", r"""
Module .. ROOT 0,0 -> 0,27
  .body[1]
  0] With .. 0,0 -> 0,27
    .items[2]
    0] withitem .. 0,5 -> 0,11
      .context_expr
        Name 'a' Load .. 0,5 -> 0,6
      .optional_vars Name 'a' Store .. 0,10 -> 0,11
    1] withitem .. 0,13 -> 0,21
      .context_expr
        Name 'z' Load .. 0,13 -> 0,14
      .optional_vars Name 'xyz' Store .. 0,18 -> 0,21
    .body[1]
    0] Pass .. 0,23 -> 0,27
"""),

(r"""a and b and c""", 'body[0].value', 1, 3, None, {'raw': True}, r"""z""", r"""a and z""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value BoolOp .. 0,0 -> 0,7
      .op And
      .values[2]
      0] Name 'a' Load .. 0,0 -> 0,1
      1] Name 'z' Load .. 0,6 -> 0,7
"""),

(r"""a < b < c < d""", 'body[0].value', 1, 4, None, {'raw': True}, r"""x < y""", r"""a < x < y""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Compare .. 0,0 -> 0,9
      .left Name 'a' Load .. 0,0 -> 0,1
      .ops[2]
      0] Lt .. 0,2 -> 0,3
      1] Lt .. 0,6 -> 0,7
      .comparators[2]
      0] Name 'x' Load .. 0,4 -> 0,5
      1] Name 'y' Load .. 0,8 -> 0,9
"""),

(r"""[a for a in a() for b in b() for c in c()]""", 'body[0].value', 1, 3, None, {'raw': True}, r"""for z in z()""", r"""[a for a in a() for z in z()]""", r"""
Module .. ROOT 0,0 -> 0,29
  .body[1]
  0] Expr .. 0,0 -> 0,29
    .value ListComp .. 0,0 -> 0,29
      .elt Name 'a' Load .. 0,1 -> 0,2
      .generators[2]
      0] comprehension .. 0,3 -> 0,15
        .target Name 'a' Store .. 0,7 -> 0,8
        .iter Call .. 0,12 -> 0,15
          .func Name 'a' Load .. 0,12 -> 0,13
        .is_async 0
      1] comprehension .. 0,16 -> 0,28
        .target Name 'z' Store .. 0,20 -> 0,21
        .iter Call .. 0,25 -> 0,28
          .func Name 'z' Load .. 0,25 -> 0,26
        .is_async 0
"""),

(r"""[a for a in a() if a if b if c]""", 'body[0].value.generators[0]', 1, 3, None, {'raw': True}, r"""if z""", r"""[a for a in a() if a if z]""", r"""
Module .. ROOT 0,0 -> 0,26
  .body[1]
  0] Expr .. 0,0 -> 0,26
    .value ListComp .. 0,0 -> 0,26
      .elt Name 'a' Load .. 0,1 -> 0,2
      .generators[1]
      0] comprehension .. 0,3 -> 0,25
        .target Name 'a' Store .. 0,7 -> 0,8
        .iter Call .. 0,12 -> 0,15
          .func Name 'a' Load .. 0,12 -> 0,13
        .ifs[2]
        0] Name 'a' Load .. 0,19 -> 0,20
        1] Name 'z' Load .. 0,24 -> 0,25
        .is_async 0
"""),

(r"""f(a, b, c)""", 'body[0].value', 1, 3, None, {'raw': True}, r"""z""", r"""f(a, z)""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value Call .. 0,0 -> 0,7
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[2]
      0] Name 'a' Load .. 0,2 -> 0,3
      1] Name 'z' Load .. 0,5 -> 0,6
"""),

(r"""f(a, b, c)""", 'body[0].value', 1, 3, None, {'raw': True}, r"""**z""", r"""f(a, **z)""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Call .. 0,0 -> 0,9
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[1]
      0] Name 'a' Load .. 0,2 -> 0,3
      .keywords[1]
      0] keyword .. 0,5 -> 0,8
        .value Name 'z' Load .. 0,7 -> 0,8
"""),

(r"""
@a
@b
@c
def f(): pass
""", 'body[0]', 1, 3, 'decorator_list', {'raw': True}, r"""@z""", r"""
@a
@z
def f(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 3,0 -> 3,13
    .name 'f'
    .body[1]
    0] Pass .. 3,9 -> 3,13
    .decorator_list[2]
    0] Name 'a' Load .. 1,1 -> 1,2
    1] Name 'z' Load .. 2,1 -> 2,2
"""),

(r"""
match a:
  case [a, b, c]: pass
""", 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, r"""*z""", r"""
match a:
  case [a, *z]: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Match .. 1,0 -> 2,20
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,2 -> 2,20
      .pattern MatchSequence .. 2,7 -> 2,14
        .patterns[2]
        0] MatchAs .. 2,8 -> 2,9
          .name 'a'
        1] MatchStar .. 2,11 -> 2,13
          .name 'z'
      .body[1]
      0] Pass .. 2,16 -> 2,20
"""),

(r"""
match a:
  case a | b | c: pass
""", 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, r"""z""", r"""
match a:
  case a | z: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Match .. 1,0 -> 2,18
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,2 -> 2,18
      .pattern MatchOr .. 2,7 -> 2,12
        .patterns[2]
        0] MatchAs .. 2,7 -> 2,8
          .name 'a'
        1] MatchAs .. 2,11 -> 2,12
          .name 'z'
      .body[1]
      0] Pass .. 2,14 -> 2,18
"""),

(r"""
match a:
  case {'a': a, 'b': b, 'c': c}: pass
""", 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, r"""**z""", r"""
match a:
  case {'a': a, **z}: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Match .. 1,0 -> 2,26
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,2 -> 2,26
      .pattern MatchMapping .. 2,7 -> 2,20
        .keys[1]
        0] Constant 'a' .. 2,8 -> 2,11
        .patterns[1]
        0] MatchAs .. 2,13 -> 2,14
          .name 'a'
        .rest 'z'
      .body[1]
      0] Pass .. 2,22 -> 2,26
"""),

(r"""def f(a): pass""", 'body[0].args', 0, 1, 'args', {'raw': True}, r"""b""", r"""def f(b): pass""", r"""
Module .. ROOT 0,0 -> 0,14
  .body[1]
  0] FunctionDef .. 0,0 -> 0,14
    .name 'f'
    .args arguments .. 0,6 -> 0,7
      .args[1]
      0] arg .. 0,6 -> 0,7
        .arg 'b'
    .body[1]
    0] Pass .. 0,10 -> 0,14
"""),

(r"""def f(a): pass""", 'body[0].args', 0, 1, 'args', {'raw': True}, r"""""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""def f(a): pass""", 'body[0].args', 0, 1, 'args', {'raw': True}, r"""**DEL**""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""f(a)""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""(i for i in range(5))""", r"""f((i for i in range(5)))""", r"""
Module .. ROOT 0,0 -> 0,24
  .body[1]
  0] Expr .. 0,0 -> 0,24
    .value Call .. 0,0 -> 0,24
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[1]
      0] GeneratorExp .. 0,2 -> 0,23
        .elt Name 'i' Load .. 0,3 -> 0,4
        .generators[1]
        0] comprehension .. 0,5 -> 0,23
          .target Name 'i' Store .. 0,9 -> 0,10
          .iter Call .. 0,14 -> 0,22
            .func Name 'range' Load .. 0,14 -> 0,19
            .args[1]
            0] Constant 5 .. 0,20 -> 0,21
          .is_async 0
"""),

(r"""{1: 2, **(x), (3): (4)}""", 'body[0].value', 1, 3, None, {'raw': True}, r"""**z""", r"""{1: 2, **z}""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value Dict .. 0,0 -> 0,11
      .keys[2]
      0] Constant 1 .. 0,1 -> 0,2
      1] None
      .values[2]
      0] Constant 2 .. 0,4 -> 0,5
      1] Name 'z' Load .. 0,9 -> 0,10
"""),

(r"""((a) < (b) < (c))""", 'body[0].value', 1, 3, None, {'raw': True}, r"""z""", r"""((a) < z)""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Compare .. 0,1 -> 0,8
      .left Name 'a' Load .. 0,2 -> 0,3
      .ops[1]
      0] Lt .. 0,5 -> 0,6
      .comparators[1]
      0] Name 'z' Load .. 0,7 -> 0,8
"""),

(r"""(1, *(x), (3))""", 'body[0].value', 1, 3, None, {'raw': True}, r"""*z""", r"""(1, *z)""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value Tuple .. 0,0 -> 0,7
      .elts[2]
      0] Constant 1 .. 0,1 -> 0,2
      1] Starred .. 0,4 -> 0,6
        .value Name 'z' Load .. 0,5 -> 0,6
        .ctx Load
      .ctx Load
"""),

(r"""
match a:
  case {'a': (a), 'b': (b), 'c': (c)}: pass
""", 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, r"""**z""", r"""
match a:
  case {'a': (a), **z}: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Match .. 1,0 -> 2,28
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,2 -> 2,28
      .pattern MatchMapping .. 2,7 -> 2,22
        .keys[1]
        0] Constant 'a' .. 2,8 -> 2,11
        .patterns[1]
        0] MatchAs .. 2,14 -> 2,15
          .name 'a'
        .rest 'z'
      .body[1]
      0] Pass .. 2,24 -> 2,28
"""),

(r"""[a for a in a() if (a) if (b) if (c)]""", 'body[0].value.generators[0]', 1, 3, None, {'raw': True}, r"""if z""", r"""[a for a in a() if (a) if z]""", r"""
Module .. ROOT 0,0 -> 0,28
  .body[1]
  0] Expr .. 0,0 -> 0,28
    .value ListComp .. 0,0 -> 0,28
      .elt Name 'a' Load .. 0,1 -> 0,2
      .generators[1]
      0] comprehension .. 0,3 -> 0,27
        .target Name 'a' Store .. 0,7 -> 0,8
        .iter Call .. 0,12 -> 0,15
          .func Name 'a' Load .. 0,12 -> 0,13
        .ifs[2]
        0] Name 'a' Load .. 0,20 -> 0,21
        1] Name 'z' Load .. 0,26 -> 0,27
        .is_async 0
"""),

(r"""
@(a)
@(b)
@(c)
def f(): pass
""", 'body[0]', 1, 3, 'decorator_list', {'raw': True}, r"""@z""", r"""
@(a)
@z
def f(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 3,0 -> 3,13
    .name 'f'
    .body[1]
    0] Pass .. 3,9 -> 3,13
    .decorator_list[2]
    0] Name 'a' Load .. 1,2 -> 1,3
    1] Name 'z' Load .. 2,1 -> 2,2
"""),

(r"""((1), (2), (3))""", 'body[0].value', 1, 3, None, {'raw': True}, r"""*z""", r"""((1), *z)""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Tuple .. 0,0 -> 0,9
      .elts[2]
      0] Constant 1 .. 0,2 -> 0,3
      1] Starred .. 0,6 -> 0,8
        .value Name 'z' Load .. 0,7 -> 0,8
        .ctx Load
      .ctx Load
"""),

(r"""f(i for i in range(5))""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""a""", r"""f(a)""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value Call .. 0,0 -> 0,4
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[1]
      0] Name 'a' Load .. 0,2 -> 0,3
"""),

(r"""f((i for i in range(5)))""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""a""", r"""f(a)""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value Call .. 0,0 -> 0,4
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[1]
      0] Name 'a' Load .. 0,2 -> 0,3
"""),

(r"""f(((i for i in range(5))))""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""a""", r"""f(a)""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value Call .. 0,0 -> 0,4
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[1]
      0] Name 'a' Load .. 0,2 -> 0,3
"""),

(r"""f((i for i in range(5)), b)""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""a""", r"""f(a, b)""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value Call .. 0,0 -> 0,7
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[2]
      0] Name 'a' Load .. 0,2 -> 0,3
      1] Name 'b' Load .. 0,5 -> 0,6
"""),

(r"""f((i for i in range(5)), b)""", 'body[0].value', 0, 2, 'args', {'raw': True}, r"""a""", r"""f(a)""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value Call .. 0,0 -> 0,4
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[1]
      0] Name 'a' Load .. 0,2 -> 0,3
"""),

]  # END OF PUT_SLICE_DATA

PUT_RAW_DATA = [
(r"""(1, 2, 3)""", '', (0, 4, 0, 5), {}, r"""*z""", r"""*z""", r"""(1, *z, 3)""", r"""
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] Expr .. 0,0 -> 0,10
    .value Tuple .. 0,0 -> 0,10
      .elts[3]
      0] Constant 1 .. 0,1 -> 0,2
      1] Starred .. 0,4 -> 0,6
        .value Name 'z' Load .. 0,5 -> 0,6
        .ctx Load
      2] Constant 3 .. 0,8 -> 0,9
      .ctx Load
"""),

(r"""(1, 2, 3)""", '', (0, 1, 0, 8), {}, r"""*z,""", r"""*z""", r"""(*z,)""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Tuple .. 0,0 -> 0,5
      .elts[1]
      0] Starred .. 0,1 -> 0,3
        .value Name 'z' Load .. 0,2 -> 0,3
        .ctx Load
      .ctx Load
"""),

(r"""1, 2, 3""", '', (0, 3, 0, 4), {}, r"""*z""", r"""*z""", r"""1, *z, 3""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value Tuple .. 0,0 -> 0,8
      .elts[3]
      0] Constant 1 .. 0,0 -> 0,1
      1] Starred .. 0,3 -> 0,5
        .value Name 'z' Load .. 0,4 -> 0,5
        .ctx Load
      2] Constant 3 .. 0,7 -> 0,8
      .ctx Load
"""),

(r"""1, 2, 3""", '', (0, 0, 0, 7), {}, r"""*z,""", r"""*z,""", r"""*z,""", r"""
Module .. ROOT 0,0 -> 0,3
  .body[1]
  0] Expr .. 0,0 -> 0,3
    .value Tuple .. 0,0 -> 0,3
      .elts[1]
      0] Starred .. 0,0 -> 0,2
        .value Name 'z' Load .. 0,1 -> 0,2
        .ctx Load
      .ctx Load
"""),

(r"""{a: b, c: d, e: f}""", '', (0, 7, 0, 11), {}, r"""**z""", r"""z""", r"""{a: b, **z, e: f}""", r"""
Module .. ROOT 0,0 -> 0,17
  .body[1]
  0] Expr .. 0,0 -> 0,17
    .value Dict .. 0,0 -> 0,17
      .keys[3]
      0] Name 'a' Load .. 0,1 -> 0,2
      1] None
      2] Name 'e' Load .. 0,12 -> 0,13
      .values[3]
      0] Name 'b' Load .. 0,4 -> 0,5
      1] Name 'z' Load .. 0,9 -> 0,10
      2] Name 'f' Load .. 0,15 -> 0,16
"""),

(r"""{a: b, c: d, e: f}""", '', (0, 1, 0, 17), {}, r"""**z""", r"""z""", r"""{**z}""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value Dict .. 0,0 -> 0,5
      .keys[1]
      0] None
      .values[1]
      0] Name 'z' Load .. 0,3 -> 0,4
"""),

(r"""{a: b, **c, **d, **e}""", '', (0, 7, 0, 15), {}, r"""f: g""", r"""f""", r"""{a: b, f: g, **e}""", r"""
Module .. ROOT 0,0 -> 0,17
  .body[1]
  0] Expr .. 0,0 -> 0,17
    .value Dict .. 0,0 -> 0,17
      .keys[3]
      0] Name 'a' Load .. 0,1 -> 0,2
      1] Name 'f' Load .. 0,7 -> 0,8
      2] None
      .values[3]
      0] Name 'b' Load .. 0,4 -> 0,5
      1] Name 'g' Load .. 0,10 -> 0,11
      2] Name 'e' Load .. 0,15 -> 0,16
"""),

(r"""{a: b, c: d, e: f}""", '', (0, 7, 0, 10), {}, r"""**""", r"""{a: b, **d, e: f}""", r"""{a: b, **d, e: f}""", r"""
Module .. ROOT 0,0 -> 0,17
  .body[1]
  0] Expr .. 0,0 -> 0,17
    .value Dict .. 0,0 -> 0,17
      .keys[3]
      0] Name 'a' Load .. 0,1 -> 0,2
      1] None
      2] Name 'e' Load .. 0,12 -> 0,13
      .values[3]
      0] Name 'b' Load .. 0,4 -> 0,5
      1] Name 'd' Load .. 0,9 -> 0,10
      2] Name 'f' Load .. 0,15 -> 0,16
"""),

(r"""{a: b, **d, e: f}""", '', (0, 7, 0, 9), {}, r"""c: """, r"""c""", r"""{a: b, c: d, e: f}""", r"""
Module .. ROOT 0,0 -> 0,18
  .body[1]
  0] Expr .. 0,0 -> 0,18
    .value Dict .. 0,0 -> 0,18
      .keys[3]
      0] Name 'a' Load .. 0,1 -> 0,2
      1] Name 'c' Load .. 0,7 -> 0,8
      2] Name 'e' Load .. 0,13 -> 0,14
      .values[3]
      0] Name 'b' Load .. 0,4 -> 0,5
      1] Name 'd' Load .. 0,10 -> 0,11
      2] Name 'f' Load .. 0,16 -> 0,17
"""),

(r"""del a, b, c""", '', (0, 7, 0, 11), {}, r"""z""", r"""z""", r"""del a, z""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Delete .. 0,0 -> 0,8
    .targets[2]
    0] Name 'a' Del .. 0,4 -> 0,5
    1] Name 'z' Del .. 0,7 -> 0,8
"""),

(r"""a = b = c = d""", '', (0, 4, 0, 9), {}, r"""z""", r"""z""", r"""a = z = d""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Assign .. 0,0 -> 0,9
    .targets[2]
    0] Name 'a' Store .. 0,0 -> 0,1
    1] Name 'z' Store .. 0,4 -> 0,5
    .value Name 'd' Load .. 0,8 -> 0,9
"""),

(r"""import a, b, c""", '', (0, 10, 0, 14), {}, r"""z as xyz""", r"""z as xyz""", r"""import a, z as xyz""", r"""
Module .. ROOT 0,0 -> 0,18
  .body[1]
  0] Import .. 0,0 -> 0,18
    .names[2]
    0] alias .. 0,7 -> 0,8
      .name 'a'
    1] alias .. 0,10 -> 0,18
      .name 'z'
      .asname
        'xyz'
"""),

(r"""from mod import a, b, c""", '', (0, 19, 0, 23), {}, r"""z as xyz""", r"""z as xyz""", r"""from mod import a, z as xyz""", r"""
Module .. ROOT 0,0 -> 0,27
  .body[1]
  0] ImportFrom .. 0,0 -> 0,27
    .module 'mod'
    .names[2]
    0] alias .. 0,16 -> 0,17
      .name 'a'
    1] alias .. 0,19 -> 0,27
      .name 'z'
      .asname
        'xyz'
    .level 0
"""),

(r"""with a as a, b as b, c as c: pass""", '', (0, 13, 0, 27), {}, r"""z as xyz""", r"""z as xyz""", r"""with a as a, z as xyz: pass""", r"""
Module .. ROOT 0,0 -> 0,27
  .body[1]
  0] With .. 0,0 -> 0,27
    .items[2]
    0] withitem .. 0,5 -> 0,11
      .context_expr
        Name 'a' Load .. 0,5 -> 0,6
      .optional_vars Name 'a' Store .. 0,10 -> 0,11
    1] withitem .. 0,13 -> 0,21
      .context_expr
        Name 'z' Load .. 0,13 -> 0,14
      .optional_vars Name 'xyz' Store .. 0,18 -> 0,21
    .body[1]
    0] Pass .. 0,23 -> 0,27
"""),

(r"""a and b and c""", '', (0, 6, 0, 13), {}, r"""z""", r"""z""", r"""a and z""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value BoolOp .. 0,0 -> 0,7
      .op And
      .values[2]
      0] Name 'a' Load .. 0,0 -> 0,1
      1] Name 'z' Load .. 0,6 -> 0,7
"""),

(r"""a < b < c < d""", '', (0, 4, 0, 13), {}, r"""x < y""", r"""x""", r"""a < x < y""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Compare .. 0,0 -> 0,9
      .left Name 'a' Load .. 0,0 -> 0,1
      .ops[2]
      0] Lt .. 0,2 -> 0,3
      1] Lt .. 0,6 -> 0,7
      .comparators[2]
      0] Name 'x' Load .. 0,4 -> 0,5
      1] Name 'y' Load .. 0,8 -> 0,9
"""),

(r"""[a for a in a() for b in b() for c in c()]""", '', (0, 16, 0, 41), {}, r"""for z in z()""", r"""for z in z()""", r"""[a for a in a() for z in z()]""", r"""
Module .. ROOT 0,0 -> 0,29
  .body[1]
  0] Expr .. 0,0 -> 0,29
    .value ListComp .. 0,0 -> 0,29
      .elt Name 'a' Load .. 0,1 -> 0,2
      .generators[2]
      0] comprehension .. 0,3 -> 0,15
        .target Name 'a' Store .. 0,7 -> 0,8
        .iter Call .. 0,12 -> 0,15
          .func Name 'a' Load .. 0,12 -> 0,13
        .is_async 0
      1] comprehension .. 0,16 -> 0,28
        .target Name 'z' Store .. 0,20 -> 0,21
        .iter Call .. 0,25 -> 0,28
          .func Name 'z' Load .. 0,25 -> 0,26
        .is_async 0
"""),

(r"""[a for a in a() if a if b if c]""", '', (0, 21, 0, 30), {}, r"""if z""", r"""z""", r"""[a for a in a() if a if z]""", r"""
Module .. ROOT 0,0 -> 0,26
  .body[1]
  0] Expr .. 0,0 -> 0,26
    .value ListComp .. 0,0 -> 0,26
      .elt Name 'a' Load .. 0,1 -> 0,2
      .generators[1]
      0] comprehension .. 0,3 -> 0,25
        .target Name 'a' Store .. 0,7 -> 0,8
        .iter Call .. 0,12 -> 0,15
          .func Name 'a' Load .. 0,12 -> 0,13
        .ifs[2]
        0] Name 'a' Load .. 0,19 -> 0,20
        1] Name 'z' Load .. 0,24 -> 0,25
        .is_async 0
"""),

(r"""f(a, b, c)""", '', (0, 5, 0, 9), {}, r"""z""", r"""z""", r"""f(a, z)""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value Call .. 0,0 -> 0,7
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[2]
      0] Name 'a' Load .. 0,2 -> 0,3
      1] Name 'z' Load .. 0,5 -> 0,6
"""),

(r"""f(a, b, c)""", '', (0, 5, 0, 9), {}, r"""**z""", r"""**z""", r"""f(a, **z)""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value Call .. 0,0 -> 0,9
      .func Name 'f' Load .. 0,0 -> 0,1
      .args[1]
      0] Name 'a' Load .. 0,2 -> 0,3
      .keywords[1]
      0] keyword .. 0,5 -> 0,8
        .value Name 'z' Load .. 0,7 -> 0,8
"""),

(r"""
@a
@b
@c
def f(): pass
""", '', (2, 0, 3, 2), {}, r"""@z""", r"""z""", r"""
@a
@z
def f(): pass
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] FunctionDef .. 3,0 -> 3,13
    .name 'f'
    .body[1]
    0] Pass .. 3,9 -> 3,13
    .decorator_list[2]
    0] Name 'a' Load .. 1,1 -> 1,2
    1] Name 'z' Load .. 2,1 -> 2,2
"""),

(r"""
match a:
  case [a, b, c]: pass
""", '', (2, 11, 2, 15), {}, r"""*z""", r"""*z""", r"""
match a:
  case [a, *z]: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Match .. 1,0 -> 2,20
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,2 -> 2,20
      .pattern MatchSequence .. 2,7 -> 2,14
        .patterns[2]
        0] MatchAs .. 2,8 -> 2,9
          .name 'a'
        1] MatchStar .. 2,11 -> 2,13
          .name 'z'
      .body[1]
      0] Pass .. 2,16 -> 2,20
"""),

(r"""
match a:
  case a | b | c: pass
""", '', (2, 11, 2, 16), {}, r"""z""", r"""z""", r"""
match a:
  case a | z: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Match .. 1,0 -> 2,18
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,2 -> 2,18
      .pattern MatchOr .. 2,7 -> 2,12
        .patterns[2]
        0] MatchAs .. 2,7 -> 2,8
          .name 'a'
        1] MatchAs .. 2,11 -> 2,12
          .name 'z'
      .body[1]
      0] Pass .. 2,14 -> 2,18
"""),

(r"""
match a:
  case {'a': a, 'b': b, 'c': c}: pass
""", '', (2, 16, 2, 30), {}, r"""**z""", r"""{'a': a, **z}""", r"""
match a:
  case {'a': a, **z}: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Match .. 1,0 -> 2,26
    .subject Name 'a' Load .. 1,6 -> 1,7
    .cases[1]
    0] match_case .. 2,2 -> 2,26
      .pattern MatchMapping .. 2,7 -> 2,20
        .keys[1]
        0] Constant 'a' .. 2,8 -> 2,11
        .patterns[1]
        0] MatchAs .. 2,13 -> 2,14
          .name 'a'
        .rest 'z'
      .body[1]
      0] Pass .. 2,22 -> 2,26
"""),

(r"""a, b""", '', (0, 1, 0, 3), {}, r"""+""", r"""+""", r"""a+b""", r"""
Module .. ROOT 0,0 -> 0,3
  .body[1]
  0] Expr .. 0,0 -> 0,3
    .value BinOp .. 0,0 -> 0,3
      .left Name 'a' Load .. 0,0 -> 0,1
      .op Add .. 0,1 -> 0,2
      .right Name 'b' Load .. 0,2 -> 0,3
"""),

(r"""a, b""", '', (0, 1, 0, 3), {}, r""" + """, r"""+""", r"""a + b""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value BinOp .. 0,0 -> 0,5
      .left Name 'a' Load .. 0,0 -> 0,1
      .op Add .. 0,2 -> 0,3
      .right Name 'b' Load .. 0,4 -> 0,5
"""),

(r"""a, b""", '', (0, 1, 0, 3), {}, r"""""", r"""ab""", r"""ab""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value Name 'ab' Load .. 0,0 -> 0,2
"""),

(r"""
if 1: pass
else: pass
""", '', (2, 0, 2, 10), {}, r"""elif 2: pass""", r"""elif 2: pass""", r"""
if 1: pass
elif 2: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,12
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 2,0 -> 2,12
      .test Constant 2 .. 2,5 -> 2,6
      .body[1]
      0] Pass .. 2,8 -> 2,12
"""),

(r"""
if 1: pass
else: pass
""", '', (2, 0, 2, 5), {}, r"""elif 2:""", r"""2""", r"""
if 1: pass
elif 2: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,12
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] If .. 2,0 -> 2,12
      .test Constant 2 .. 2,5 -> 2,6
      .body[1]
      0] Pass .. 2,8 -> 2,12
"""),

(r"""
if 1: pass
elif 2: pass
""", '', (2, 0, 2, 12), {}, r"""else: pass""", r"""pass""", r"""
if 1: pass
else: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,10
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Pass .. 2,6 -> 2,10
"""),

(r"""
if 1: pass
elif 2: pass
""", '', (2, 0, 2, 7), {}, r"""else:""", r"""if 1: pass
else: pass""", r"""
if 1: pass
else: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,10
    .test Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Pass .. 2,6 -> 2,10
"""),

(r"""
try: pass
except Exception: pass
finally: pass
""", '', (2, 0, 3, 0), {}, r"""""", r"""try: pass
finally: pass""", r"""
try: pass
finally: pass
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] Try .. 1,0 -> 2,13
    .body[1]
    0] Pass .. 1,5 -> 1,9
    .finalbody[1]
    0] Pass .. 2,9 -> 2,13
"""),

(r"""def f(): pass""", '', (0, 6, 0, 6), {}, r"""a, *b, **c""", r"""a, *b, **c""", r"""def f(a, *b, **c): pass""", r"""
Module .. ROOT 0,0 -> 0,23
  .body[1]
  0] FunctionDef .. 0,0 -> 0,23
    .name 'f'
    .args arguments .. 0,6 -> 0,16
      .args[1]
      0] arg .. 0,6 -> 0,7
        .arg 'a'
      .vararg arg .. 0,10 -> 0,11
        .arg 'b'
      .kwarg arg .. 0,15 -> 0,16
        .arg 'c'
    .body[1]
    0] Pass .. 0,19 -> 0,23
"""),

(r"""def f(a, *b, **c): pass""", '', (0, 6, 0, 16), {}, r"""""", r"""def f(): pass""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

(r"""def f(a, *b, **c): pass""", '', (0, 6, 0, 16), {}, r""" """, r"""def f( ): pass""", r"""def f( ): pass""", r"""
Module .. ROOT 0,0 -> 0,14
  .body[1]
  0] FunctionDef .. 0,0 -> 0,14
    .name 'f'
    .body[1]
    0] Pass .. 0,10 -> 0,14
"""),

(r"""def f(a, *b, **c): pass""", '', (0, 6, 0, 16), {}, r"""**DEL**""", r"""def f(): pass""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name 'f'
    .body[1]
    0] Pass .. 0,9 -> 0,13
"""),

]  # END OF PUT_RAW_DATA

# end of refreshable data

REPLACE_EXISTING_SINGLE_DATA = [
# FunctionDef
("@d\ndef f(a) -> r: pass", 'body[0].decorator_list[0]', {}, "z", "z", "@z\ndef f(a) -> r: pass"),
("@d\ndef f(a) -> r: pass", 'body[0].args', {}, "z", "z", "@d\ndef f(z) -> r: pass"),
("@d\ndef f(a) -> r: pass", 'body[0].returns', {}, "z", "z", "@d\ndef f(a) -> z: pass"),

# AsyncFunctionDef
("@d\nasync def f(a) -> r: pass", 'body[0].decorator_list[0]', {}, "z", "z", "@z\nasync def f(a) -> r: pass"),
("@d\nasync def f(a) -> r: pass", 'body[0].args', {}, "z", "z", "@d\nasync def f(z) -> r: pass"),
("@d\nasync def f(a) -> r: pass", 'body[0].returns', {}, "z", "z", "@d\nasync def f(a) -> z: pass"),

# ClassDef
("@d\nclass c(b, k=v): pass", 'body[0].decorator_list[0]', {}, "z", "z", "@z\nclass c(b, k=v): pass"),
("@d\nclass c(b, k=v): pass", 'body[0].bases[0]', {}, "z", "z", "@d\nclass c(z, k=v): pass"),
("@d\nclass c(b, k=v): pass", 'body[0].keywords[0]', {}, "z=y", "z=y", "@d\nclass c(b, z=y): pass"),

# Return
("return r", 'body[0].value', {}, "z", "z", "return z"),

# Delete
("del d", 'body[0].targets[0]', {}, "z", "z", "del z"),

# Assign
("t = v", 'body[0].targets[0]', {}, "z", "z", "z = v"),
("t = v", 'body[0].value', {}, "z", "z", "t = z"),

# AugAssign
("t += v", 'body[0].target', {}, "z", "z", "z += v"),
("t += v", 'body[0].op', {}, "-=", "-=", "t -= v"),
("t += v", 'body[0].value', {}, "z", "z", "t += z"),

# AnnAssign
("t: int = v", 'body[0].target', {}, "z", "z", "z: int = v"),
("t: int = v", 'body[0].annotation', {}, "z", "z", "t: z = v"),
("t: int = v", 'body[0].value', {}, "z", "z", "t: int = z"),

# For
("for i in r: pass", 'body[0].target', {}, "z", "z", "for z in r: pass"),
("for i in r: pass", 'body[0].iter', {}, "z", "z", "for i in z: pass"),

# AsyncFor
("async for i in r: pass", 'body[0].target', {}, "z", "z", "async for z in r: pass"),
("async for i in r: pass", 'body[0].iter', {}, "z", "z", "async for i in z: pass"),

# While
("while t: pass", 'body[0].test', {}, "z", "z", "while z: pass"),

# If
("if t: pass", 'body[0].test', {}, "z", "z", "if z: pass"),

# With
("with c: pass", 'body[0].items[0]', {}, "z", "z", "with z: pass"),

# AsyncWith
("async with c: pass", 'body[0].items[0]', {}, "z", "z", "async with z: pass"),

# Match
("match s:\n case 1: pass", 'body[0].subject', {}, "z", "z", "match z:\n case 1: pass"),

# Raise
("raise e from c", 'body[0].exc', {}, "z", "z", "raise z from c"),
("raise e from c", 'body[0].cause', {}, "z", "z", "raise e from z"),

# Try
("try: pass\nexcept Exception as e: pass", 'body[0].handlers[0]', {}, "except: pass", "except: pass", "try: pass\nexcept: pass"),

# TryStar, working on py3.10 so no TryStar

# Assert
("assert a, m", 'body[0].test', {}, "z", "z", "assert z, m"),
("assert a, m", 'body[0].msg', {}, "z", "z", "assert a, z"),

# Import
("import p as n", 'body[0].names[0]', {}, "z as y", "z as y", "import z as y"),

# ImportFrom
("from g import p as n", 'body[0].names[0]', {}, "z as y", "z as y", "from g import z as y"),

# Expr
("e", 'body[0].value', {}, "z", "z", "z"),

# BoolOp
("a and b", 'body[0].value.values[0]', {}, "z", "z", "z and b"),

# NamedExpr
("(t := v)", 'body[0].value.target', {}, "z", "z", "(z := v)"),
("(t := v)", 'body[0].value.value', {}, "z", "z", "(t := z)"),

# BinOp
("a + b", 'body[0].value.left', {}, "z", "z", "z + b"),
("a + b", 'body[0].value.op', {}, "-", "-", "a - b"),
("a + b", 'body[0].value.right', {}, "z", "z", "a + z"),

# UnaryOp
("+a", 'body[0].value.op', {}, "-", "-", "-a"),
("+a", 'body[0].value.operand', {}, "z", "z", "+z"),

# Lambda
("lambda a: None", 'body[0].value.args', {}, "z", "z", "lambda z: None"),

# IfExp
("a if t else b", 'body[0].value.body', {}, "z", "z", "z if t else b"),
("a if t else b", 'body[0].value.test', {}, "z", "z", "a if z else b"),
("a if t else b", 'body[0].value.orelse', {}, "z", "z", "a if t else z"),

# Dict
("{a: b}", 'body[0].value.keys[0]', {}, "z", "z", "{z: b}"),
("{a: b}", 'body[0].value.values[0]', {}, "z", "z", "{a: z}"),

# Set
("{a}", 'body[0].value.elts[0]', {}, "z", "z", "{z}"),

# ListComp
("[i for i in t]", 'body[0].value.elt', {}, "z", "z", "[z for i in t]"),
("[i for i in t]", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "[i for z in y]"),

# SetComp
("{i for i in t}", 'body[0].value.elt', {}, "z", "z", "{z for i in t}"),
("{i for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{i for z in y}"),

# DictComp
("{k: v for i in t}", 'body[0].value.key', {}, "z", "z", "{z: v for i in t}"),
("{k: v for i in t}", 'body[0].value.value', {}, "z", "z", "{k: z for i in t}"),
("{k: v for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{k: v for z in y}"),

# GeneratorExp
("(i for i in t)", 'body[0].value.elt', {}, "z", "z", "(z for i in t)"),
("(i for i in t)", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "(i for z in y)"),

# Await
("await w", 'body[0].value.value', {}, "z", "z", "await z"),

# Yield
("yield w", 'body[0].value.value', {}, "z", "z", "yield z"),

# YieldFrom
("yield from w", 'body[0].value.value', {}, "z", "z", "yield from z"),

# Compare
("a < b", 'body[0].value.left', {}, "z", "z", "z < b"),
("a < b", 'body[0].value.ops[0]', {}, ">", ">", "a > b"),
("a < b", 'body[0].value.comparators[0]', {}, "z", "z", "a < z"),

# Call
("c(a, b=c)", 'body[0].value.func', {}, "z", "z", "z(a, b=c)"),
("c(a, b=c)", 'body[0].value.args[0]', {}, "z", "z", "c(z, b=c)"),
("c(a, b=c)", 'body[0].value.keywords[0]', {}, "z=y", "z=y", "c(a, z=y)"),

# FormattedValue, no locations in py3.10
# JoinedStr, no locations in py3.10

# Attribute
# (('value', 'expr'), ('attr', 'identifier'), ('ctx', 'expr_context'))),

# Subscript
("v[s]", 'body[0].value.value', {}, "z", "z", "z[s]"),
("v[s]", 'body[0].value.slice', {}, "z", "z", "v[z]"),

# Starred
("[*s]", 'body[0].value.elts[0].value', {}, "z", "z", "[*z]"),

# List
("[e]", 'body[0].value.elts[0]', {}, "z", "z", "[z]"),

# Tuple
("(e,)", 'body[0].value.elts[0]', {}, "z", "z", "(z,)"),

# Slice
("v[a:b:c]", 'body[0].value.slice.lower', {}, "z", "z", "v[z:b:c]"),
("v[a:b:c]", 'body[0].value.slice.upper', {}, "z", "z", "v[a:z:c]"),
("v[a:b:c]", 'body[0].value.slice.step', {}, "z", "z", "v[a:b:z]"),

# comprehension
("[i for i in t if s]", 'body[0].value.generators[0].target', {}, "z", "z", "[i for z in t if s]"),
("[i for i in t if s]", 'body[0].value.generators[0].iter', {}, "z", "z", "[i for i in z if s]"),
("[i for i in t if s]", 'body[0].value.generators[0].ifs[0]', {}, "z", "z", "[i for i in t if z]"),

# ExceptHandler
("try: pass\nexcept Exception as e: pass", 'body[0].handlers[0].type', {}, "z", "z", "try: pass\nexcept z as e: pass"),

# arguments
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.posonlyargs[0]', {}, "z", "z", "def f(z, /, b=1, *c, d=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.args[0]', {}, "z", "z", "def f(a, /, z=1, *c, d=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.defaults[0]', {}, "z", "z", "def f(a, /, b=z, *c, d=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.vararg', {}, "z", "z", "def f(a, /, b=1, *z, d=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.kwonlyargs[0]', {}, "z", "z", "def f(a, /, b=1, *c, z=2, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.kw_defaults[0]', {}, "z", "z", "def f(a, /, b=1, *c, d=z, **e): pass"),
("def f(a, /, b=1, *c, d=2, **e): pass", 'body[0].args.kwarg', {}, "z", "z", "def f(a, /, b=1, *c, d=2, **z): pass"),

# arg
("def f(a: int): pass", 'body[0].args.args[0].annotation', {}, "z", "z", "def f(a: z): pass"),

# keyword
("class c(k=v): pass", 'body[0].keywords[0].value', {}, "z", "z", "class c(k=z): pass"),

# alias nothing to test

# withitem
("with c as n: pass", 'body[0].items[0].context_expr', {}, "z", "z", "with z as n: pass"),
("with c as n: pass", 'body[0].items[0].optional_vars', {}, "z", "z", "with c as z: pass"),

# match_case
("match s:\n case 1 as a if g: pass", 'body[0].cases[0].pattern', {}, "'z'", "'z'", "match s:\n case 'z' if g: pass"),
("match s:\n case 1 as a if g: pass", 'body[0].cases[0].guard', {}, "z", "z", "match s:\n case 1 as a if z: pass"),

# MatchValue
("match s:\n case 1: pass", 'body[0].cases[0].pattern.value', {}, "2", "2", "match s:\n case 2: pass"),

# MatchSequence
("match s:\n case 1, 2: pass", 'body[0].cases[0].pattern.patterns[1].value', {}, "3", "3", "match s:\n case 1, 3: pass"),

# MatchMapping
("match s:\n case {1: a, **b}: pass", 'body[0].cases[0].pattern.keys[0]', {}, "2", "2", "match s:\n case {2: a, **b}: pass"),
("match s:\n case {1: a, **b}: pass", 'body[0].cases[0].pattern.patterns[0]', {}, "z", "z", "match s:\n case {1: z, **b}: pass"),

# MatchClass
("match s:\n case c(1, a=2): pass", 'body[0].cases[0].pattern.cls', {}, "z", "z", "match s:\n case z(1, a=2): pass"),
("match s:\n case c(1, a=2): pass", 'body[0].cases[0].pattern.patterns[0].value', {}, "3", "3", "match s:\n case c(3, a=2): pass"),
("match s:\n case c(1, a=2): pass", 'body[0].cases[0].pattern.kwd_patterns[0].value', {}, "3", "3", "match s:\n case c(1, a=3): pass"),

# MatchAs
("match s:\n case 1 as a: pass", 'body[0].cases[0].pattern.pattern', {}, "2", "2", "match s:\n case 2 as a: pass"),

# MatchOr
("match s:\n case 1 | 2: pass", 'body[0].cases[0].pattern.patterns[0].value', {}, "3", "3", "match s:\n case 3 | 2: pass"),

]

def read(fnm):
    with open(fnm) as f:
        return f.read()


def walktest(ast):
    for ast in walk(ast):
        ast.f.loc


class TestFST(unittest.TestCase):
    def test__loc_block_opener_end(self):
        self.assertEqual((0, 16), parse('def f(a) -> int: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 9),  parse('def f(a): pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 8),  parse('def f(): pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 22), parse('async def f(a) -> int: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 15), parse('async def f(a): pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 14), parse('async def f(): pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 27), parse('class cls(base, keyword=1): pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 16), parse('class cls(base): pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 11), parse('for a in b: pass\nelse: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 17), parse('async for a in b: pass\nelse: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 8),  parse('while a: pass\nelse: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 5),  parse('if a: pass\nelse: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 9),  parse('with f(): pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 14), parse('with f() as v: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 15), parse('async with f(): pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 20), parse('async with f() as v: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((0, 8),  parse('match a:\n case 2: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((1, 8),  parse('match a:\n case 2: pass').body[0].cases[0].f._loc_block_opener_end())
        self.assertEqual((1, 16), parse('match a:\n case 2 if True: pass').body[0].cases[0].f._loc_block_opener_end())
        self.assertEqual((0, 4),  parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].f._loc_block_opener_end())
        self.assertEqual((1, 7),  parse('try: pass\nexcept: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_opener_end())
        self.assertEqual((1, 17), parse('try: pass\nexcept Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_opener_end())
        self.assertEqual((1, 34), parse('try: pass\nexcept (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_opener_end())
        self.assertEqual((1, 39), parse('try: pass\nexcept (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_opener_end())

        if sys.version_info[:2] >= (3, 12):
            self.assertEqual((0, 4),  parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].f._loc_block_opener_end())
            self.assertEqual((1, 18), parse('try: pass\nexcept* Exception: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_opener_end())
            self.assertEqual((1, 35), parse('try: pass\nexcept* (Exception, BaseException): pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_opener_end())
            self.assertEqual((1, 40), parse('try: pass\nexcept* (Exception, BaseException) as e: pass\nelse: pass\nfinally: pass').body[0].handlers[0].f._loc_block_opener_end())
            self.assertEqual((0, 13), parse('class cls[T]: pass').body[0].f._loc_block_opener_end())

    def test__dict_key_or_mock_loc(self):
        a = parse('''{
    a: """test
two  # fake comment start""", **b
            }''').body[0].value
        self.assertEqual((2, 30, 2, 32), a.f._dict_key_or_mock_loc(a.keys[1], a.values[1].f))

        a = parse('''{
    a: """test""", **  # comment
    b
            }''').body[0].value
        self.assertEqual((1, 19, 1, 21), a.f._dict_key_or_mock_loc(a.keys[1], a.values[1].f))

    def test__normalize_code(self):
        f = fst._normalize_code('i')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code('i', coerce='expr')
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(['i'])
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(['i'], coerce='expr')
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(ast_.parse('i'))
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(ast_.parse('i', mode='single'))
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(ast_.parse('i'), coerce='expr')
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(ast_.parse('i', mode='eval'))
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(ast_.parse('i', mode='eval'), coerce='expr')
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(FST.fromsrc('i'))
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(FST.fromsrc('i', mode='single'))
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(FST.fromsrc('i', mode='eval'))
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(FST.fromsrc('i'), coerce='expr')
        self.assertIsInstance(f.a, Name)

        f = fst._normalize_code(FST.fromsrc('i', mode='eval'), coerce='expr')
        self.assertIsInstance(f.a, Name)

        # mod

        f = fst._normalize_code('i', coerce='mod')
        self.assertIsInstance(f.a, Module)

        f = fst._normalize_code(ast_.parse('i'), coerce='mod')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(ast_.parse('i').body[0], coerce='mod')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(ast_.parse('i', mode='eval'), coerce='mod')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(ast_.parse('i', mode='eval').body, coerce='mod')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(ast_.parse('i', mode='single'), coerce='mod')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], Expr)
        self.assertIsInstance(f.a.body[0].value, Name)

        f = fst._normalize_code(parse('try: pass\nexcept: pass').body[0].handlers[0].f.copy(), coerce='mod')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], ExceptHandler)

        f = fst._normalize_code(parse('match a:\n  case 1: pass').body[0].cases[0].f.copy(), coerce='mod')
        self.assertIsInstance(f.a, Module)
        self.assertIsInstance(f.a.body[0], match_case)

    def test__next_prev_src(self):
        lines = '''
  # pre
i \\
here \\
j \\
  # post
k \\
            '''.split('\n')

        self.assertEqual((4, 0, 'j'), fst._next_src(lines, 3, 4, 7, 0, False, False))
        self.assertEqual((4, 0, 'j'), fst._next_src(lines, 3, 4, 7, 0, True, False))
        self.assertEqual((6, 0, 'k'), fst._next_src(lines, 4, 1, 7, 0, False, False))
        self.assertEqual((5, 2, '# post'), fst._next_src(lines, 4, 1, 7, 0, True, False))
        self.assertEqual((6, 0, 'k'), fst._next_src(lines, 5, 8, 7, 0, False, False))
        self.assertEqual((6, 0, 'k'), fst._next_src(lines, 5, 8, 7, 0, True, False))

        self.assertEqual((3, 5, '\\'), fst._next_src(lines, 3, 4, 7, 0, False, True))
        self.assertEqual((3, 5, '\\'), fst._next_src(lines, 3, 4, 7, 0, True, True))
        self.assertEqual((4, 2, '\\'), fst._next_src(lines, 4, 1, 7, 0, False, True))
        self.assertEqual((4, 2, '\\'), fst._next_src(lines, 4, 1, 7, 0, True, True))
        self.assertEqual((6, 0, 'k'), fst._next_src(lines, 5, 8, 7, 0, False, True))
        self.assertEqual((6, 0, 'k'), fst._next_src(lines, 5, 8, 7, 0, True, True))

        self.assertEqual((4, 0, 'j'), fst._next_src(lines, 3, 4, 7, 0, False, None))
        self.assertEqual((4, 0, 'j'), fst._next_src(lines, 3, 4, 7, 0, True, None))
        self.assertEqual(None, fst._next_src(lines, 4, 1, 7, 0, False, None))
        self.assertEqual((5, 2, '# post'), fst._next_src(lines, 4, 1, 7, 0, True, None))
        self.assertEqual(None, fst._next_src(lines, 5, 8, 7, 0, False, None))
        self.assertEqual(None, fst._next_src(lines, 5, 8, 7, 0, True, None))

        self.assertEqual(None, fst._prev_src(lines, 0, 0, 2, 0, False, False))
        self.assertEqual((1, 2, '# pre'), fst._prev_src(lines, 0, 0, 2, 0, True, False))
        self.assertEqual((2, 0, 'i'), fst._prev_src(lines, 0, 0, 3, 0, False, False))
        self.assertEqual((2, 0, 'i'), fst._prev_src(lines, 0, 0, 3, 0, True, False))
        self.assertEqual((4, 0, 'j'), fst._prev_src(lines, 0, 0, 6, 0, False, False))
        self.assertEqual((5, 2, '# post'), fst._prev_src(lines, 0, 0, 6, 0, True, False))

        self.assertEqual(None, fst._prev_src(lines, 0, 0, 2, 0, False, True))
        self.assertEqual((1, 2, '# pre'), fst._prev_src(lines, 0, 0, 2, 0, True, True))
        self.assertEqual((2, 2, '\\'), fst._prev_src(lines, 0, 0, 3, 0, False, True))
        self.assertEqual((2, 2, '\\'), fst._prev_src(lines, 0, 0, 3, 0, True, True))
        self.assertEqual((4, 2, '\\'), fst._prev_src(lines, 0, 0, 6, 0, False, True))
        self.assertEqual((5, 2, '# post'), fst._prev_src(lines, 0, 0, 6, 0, True, True))

        self.assertEqual(None, fst._prev_src(lines, 0, 0, 1, 7, False, None))
        self.assertEqual((1, 2, '# pre'), fst._prev_src(lines, 0, 0, 1, 7, True, None))
        self.assertEqual((2, 0, 'i'), fst._prev_src(lines, 0, 0, 3, 0, False, None))
        self.assertEqual((2, 0, 'i'), fst._prev_src(lines, 0, 0, 3, 0, True, None))
        self.assertEqual((4, 0, 'j'), fst._prev_src(lines, 0, 0, 5, 3, False, None))
        self.assertEqual((5, 2, '#'), fst._prev_src(lines, 0, 0, 5, 3, True, None))

        self.assertEqual((1, 1, 'a'), fst._next_src(['\\', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual((2, 1, 'a'), fst._next_src(['\\', '\\', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual(None, fst._next_src(['\\', '', ' a'], 0, 0, 100, 0, True, None))
        self.assertEqual((1, 1, '# c'), fst._next_src(['\\', ' # c'], 0, 0, 100, 0, True, None))
        self.assertEqual(None, fst._next_src(['\\', ' # c', 'a'], 0, 0, 100, 0, False, None))

        self.assertEqual((0, 0, 'a'), fst._prev_src(['a \\', ''], 0, 0, 1, 0, True, None))
        self.assertEqual((0, 0, 'a'), fst._prev_src(['a \\', '\\', ''], 0, 0, 2, 0, True, None))
        self.assertEqual((0, 0, 'a'), fst._prev_src(['a \\', '\\', '\\', ''], 0, 0, 3, 0, True, None))
        self.assertEqual((1, 1, '# c'), fst._prev_src(['a \\', ' # c'], 0, 0, 1, 4, True, None))
        self.assertEqual((1, 1, '# '), fst._prev_src(['a \\', ' # c'], 0, 0, 1, 3, True, None))
        self.assertEqual((1, 1, '#'), fst._prev_src(['a \\', ' # c'], 0, 0, 1, 2, True, None))
        self.assertEqual((0, 0, 'a'), fst._prev_src(['a \\', ' # c'], 0, 0, 1, 1, True, None))
        self.assertEqual((1, 1, '# c'), fst._prev_src(['a', ' # c'], 0, 0, 1, 4, True, None))
        self.assertEqual((1, 1, '# '), fst._prev_src(['a', ' # c'], 0, 0, 1, 3, True, None))
        self.assertEqual((1, 1, '#'), fst._prev_src(['a', ' # c'], 0, 0, 1, 2, True, None))
        self.assertEqual(None, fst._prev_src(['a', ' # c'], 0, 0, 1, 1, True, None))

        state = []
        self.assertEqual((0, 4, '# c \\'), fst._prev_src(['a b # c \\'], 0, 0, 0, 9, True, True, state=state))
        self.assertEqual((0, 2, 'b'), fst._prev_src(['a b # c \\'], 0, 0, 0, 4, True, True, state=state))
        self.assertEqual((0, 0, 'a'), fst._prev_src(['a b # c \\'], 0, 0, 0, 2, True, True, state=state))
        self.assertEqual(None, fst._prev_src(['a b # c \\'], 0, 0, 0, 0, True, True, state=state))

        state = []
        self.assertEqual((0, 2, 'b'), fst._prev_src(['a b # c \\'], 0, 0, 0, 9, False, True, state=state))
        self.assertEqual((0, 0, 'a'), fst._prev_src(['a b # c \\'], 0, 0, 0, 2, False, True, state=state))
        self.assertEqual(None, fst._prev_src(['a b # c \\'], 0, 0, 0, 0, False, True, state=state))

        state = []
        self.assertEqual((0, 2, 'b'), fst._prev_src(['a b # c \\'], 0, 0, 0, 9, False, None, state=state))
        self.assertEqual((0, 0, 'a'), fst._prev_src(['a b # c \\'], 0, 0, 0, 2, False, None, state=state))
        self.assertEqual(None, fst._prev_src(['a b # c \\'], 0, 0, 0, 0, False, None, state=state))

        state = []
        self.assertEqual((0, 4, '# c \\'), fst._prev_src(['a b # c \\'], 0, 0, 0, 9, True, None, state=state))
        self.assertEqual((0, 2, 'b'), fst._prev_src(['a b # c \\'], 0, 0, 0, 4, True, None, state=state))
        self.assertEqual((0, 0, 'a'), fst._prev_src(['a b # c \\'], 0, 0, 0, 2, True, None, state=state))
        self.assertEqual(None, fst._prev_src(['a b # c \\'], 0, 0, 0, 0, True, None, state=state))

        state = []
        self.assertEqual((0, 4, 'c'), fst._prev_src(['a b c \\'], 0, 0, 0, 9, True, None, state=state))
        self.assertEqual((0, 2, 'b'), fst._prev_src(['a b c \\'], 0, 0, 0, 4, True, None, state=state))
        self.assertEqual((0, 0, 'a'), fst._prev_src(['a b c \\'], 0, 0, 0, 2, True, None, state=state))
        self.assertEqual(None, fst._prev_src(['a b c \\'], 0, 0, 0, 0, True, None, state=state))

    def test__next_pref_find(self):
        lines = '''
  ; \\
  # hello
  \\
  # world
  # word
            '''.split('\n')

        self.assertEqual((1, 2), fst._prev_find(lines, 0, 0, 5, 0, ';'))
        self.assertEqual((1, 2), fst._prev_find(lines, 0, 0, 5, 0, ';', True))
        self.assertEqual(None, fst._prev_find(lines, 0, 0, 5, 0, ';', True, comment=True))
        self.assertEqual(None, fst._prev_find(lines, 0, 0, 5, 0, ';', True, lcont=True))
        self.assertEqual((1, 2), fst._prev_find(lines, 0, 0, 2, 0, ';', True, lcont=None))
        self.assertEqual(None, fst._prev_find(lines, 0, 0, 3, 0, ';', True, lcont=None))
        self.assertEqual((1, 2), fst._prev_find(lines, 0, 0, 5, 0, ';', False, comment=True, lcont=True))
        self.assertEqual(None, fst._prev_find(lines, 0, 0, 5, 0, ';', True, comment=True, lcont=True))
        self.assertEqual((5, 2), fst._prev_find(lines, 0, 0, 6, 0, '# word', False, comment=True, lcont=True))
        self.assertEqual((4, 2), fst._prev_find(lines, 0, 0, 6, 0, '# world', False, comment=True, lcont=True))
        self.assertEqual(None, fst._prev_find(lines, 0, 0, 5, 0, '# world', False, comment=False, lcont=True))
        self.assertEqual((2, 2), fst._prev_find(lines, 0, 0, 5, 0, '# hello', False, comment=True, lcont=True))
        self.assertEqual(None, fst._prev_find(lines, 0, 0, 5, 0, '# hello', True, comment=True, lcont=True))

        lines = '''
  \\
  # hello
  ; \\
  # world
  # word
            '''.split('\n')

        self.assertEqual((3, 2), fst._next_find(lines, 2, 0, 6, 0, ';'))
        self.assertEqual((3, 2), fst._next_find(lines, 2, 0, 6, 0, ';', True))
        self.assertEqual(None, fst._next_find(lines, 2, 0, 6, 0, ';', True, comment=True))
        self.assertEqual((3, 2), fst._next_find(lines, 2, 0, 6, 0, ';', True, lcont=True))
        self.assertEqual(None, fst._next_find(lines, 2, 0, 6, 0, ';', True, lcont=None))
        self.assertEqual(None, fst._next_find(lines, 3, 3, 6, 0, '# word', False))
        self.assertEqual(None, fst._next_find(lines, 3, 3, 6, 0, '# word', True))
        self.assertEqual(None, fst._next_find(lines, 3, 3, 6, 0, '# word', True, comment=True))
        self.assertEqual((5, 2), fst._next_find(lines, 3, 3, 6, 0, '# word', False, comment=True))
        self.assertEqual(None, fst._next_find(lines, 3, 3, 6, 0, '# word', False, comment=True, lcont=None))
        self.assertEqual((4, 2), fst._next_find(lines, 3, 0, 6, 0, '# world', False, comment=True, lcont=None))
        self.assertEqual(None, fst._next_find(lines, 3, 0, 6, 0, '# word', False, comment=True, lcont=None))
        self.assertEqual((5, 2), fst._next_find(lines, 3, 0, 6, 0, '# word', False, comment=True, lcont=True))
        self.assertEqual(None, fst._next_find(lines, 3, 0, 6, 0, '# word', True, comment=True, lcont=True))

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
        a = parse('''
if 1: pass
elif 2: pass
        '''.strip())
        a.body[0].orelse[0].f._elif_to_else_if()
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
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
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
        a.body[0].orelse[0].f._elif_to_else_if()
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
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
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
        a.body[0].orelse[0].f._elif_to_else_if()
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
        a.body[0].body[0].orelse[0].f._elif_to_else_if()
        a.f.verify()
        self.assertEqual(a.f.src, '''
def f():
    if 1: pass
    else:
        if 2: pass
        elif 3: pass
            '''.strip())

    def test__parenthesize_grouping(self):
        f = parse('[i]').f
        f.body[0].value.elts[0]._parenthesize_grouping()
        self.assertEqual('[(i)]', f.src)
        self.assertEqual((0, 0, 0, 5), f.loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].loc)
        self.assertEqual((0, 0, 0, 5), f.body[0].value.loc)
        self.assertEqual((0, 2, 0, 3), f.body[0].value.elts[0].loc)

        f = parse('a + b').f
        f.body[0].value.left._parenthesize_grouping()
        f.body[0].value.right._parenthesize_grouping()
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)

        f = parse('a + b').f
        f.body[0].value.right._parenthesize_grouping()
        f.body[0].value.left._parenthesize_grouping()
        self.assertEqual('(a) + (b)', f.src)
        self.assertEqual((0, 0, 0, 9), f.loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].loc)
        self.assertEqual((0, 0, 0, 9), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.left.loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.op.loc)
        self.assertEqual((0, 7, 0, 8), f.body[0].value.right.loc)
        f.body[0].value._parenthesize_grouping()
        self.assertEqual('((a) + (b))', f.src)
        f.body[0].value.left._parenthesize_grouping()
        self.assertEqual('(((a)) + (b))', f.src)
        f.body[0].value.right._parenthesize_grouping()
        self.assertEqual('(((a)) + ((b)))', f.src)

        f = parse('call(i for i in j)').f
        f.body[0].value.args[0]._parenthesize_grouping()
        self.assertEqual(f.src, 'call((i for i in j))')
        f.body[0].value.args[0]._parenthesize_grouping()
        self.assertEqual(f.src, 'call(((i for i in j)))')

        f = parse('i').body[0].value.f.copy()
        f.put_src('\n# post', 0, 1, 0, 1, False)
        f.put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_grouping(whole=True)
        self.assertEqual((1, 0, 1, 1), f.loc)
        self.assertEqual(f.root.src, '(# pre\ni\n# post)')

        f = parse('i').body[0].value.f.copy()
        f.put_src('\n# post', 0, 1, 0, 1, False)
        f.put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_grouping(whole=False)
        self.assertEqual((1, 1, 1, 2), f.loc)
        self.assertEqual(f.root.src, '# pre\n(i)\n# post')

    def test__parenthesize_tuple(self):
        f = parse('i,').f
        f.body[0].value._parenthesize_tuple()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('a, b').f
        f.body[0].value._parenthesize_tuple()
        self.assertEqual('(a, b)', f.src)
        self.assertEqual((0, 0, 0, 6), f.loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].loc)
        self.assertEqual((0, 0, 0, 6), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 4, 0, 5), f.body[0].value.elts[1].loc)

        f = parse('i,').body[0].value.f.copy()
        f.put_src('\n# post', 0, 2, 0, 2, False)
        f.put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_tuple(whole=True)
        self.assertEqual((0, 0, 2, 7), f.loc)
        self.assertEqual(f.src, '(# pre\ni,\n# post)')

        f = parse('i,').body[0].value.f.copy()
        f.put_src('\n# post', 0, 2, 0, 2, False)
        f.put_src('# pre\n', 0, 0, 0, 0, False)
        f._parenthesize_tuple(whole=False)
        self.assertEqual((1, 0, 1, 4), f.loc)
        self.assertEqual(f.src, '# pre\n(i,)\n# post')

    def test__unparenthesize_grouping(self):
        f = parse('a').f
        f.body[0].value._unparenthesize_grouping()
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(a)').f
        f.body[0].value._unparenthesize_grouping()
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((a))').f
        f.body[0].value._unparenthesize_grouping()
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('(\n ( (a) )  \n)').f
        f.body[0].value._unparenthesize_grouping()
        self.assertEqual('a', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('((i,))').f
        f.body[0].value._unparenthesize_grouping()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('(\n ( (i,) ) \n)').f
        f.body[0].value._unparenthesize_grouping()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 1, 0, 2), f.body[0].value.elts[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0]._unparenthesize_grouping()
        self.assertEqual(f.src, 'call((i for i in j))')
        self.assertEqual((0, 0, 0, 20), f.loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].loc)
        self.assertEqual((0, 0, 0, 20), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 5, 0, 19), f.body[0].value.args[0].loc)

        f = parse('call((((i for i in j))))').f
        f.body[0].value.args[0]._unparenthesize_grouping(inc_genexpr_solo=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('call( ( ( (i for i in j) ) ) )').f
        f.body[0].value.args[0]._unparenthesize_grouping(inc_genexpr_solo=True)
        self.assertEqual(f.src, 'call(i for i in j)')
        self.assertEqual((0, 0, 0, 18), f.loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].loc)
        self.assertEqual((0, 0, 0, 18), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.func.loc)
        self.assertEqual((0, 4, 0, 18), f.body[0].value.args[0].loc)

        f = parse('( # pre\ni\n# post\n)').f
        f.body[0].value._unparenthesize_grouping()
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.loc)

        f = parse('( # pre\ni\n# post\n)').body[0].value.f.copy(pars=True)
        f._unparenthesize_grouping()
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

        f = parse('( # pre\n(i,)\n# post\n)').f
        f.body[0].value._unparenthesize_grouping()
        self.assertEqual('(i,)', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)

        f = parse('( # pre\n(i)\n# post\n)').body[0].value.f.copy(pars=True)
        f._unparenthesize_grouping()
        self.assertEqual('i', f.src)
        self.assertEqual((0, 0, 0, 1), f.loc)

    def test__unparenthesize_tuple(self):
        f = parse('()').f
        f.body[0].value._unparenthesize_tuple()
        self.assertEqual('()', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)

        f = parse('(i,)').f
        f.body[0].value._unparenthesize_tuple()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('(a, b)').f
        f.body[0].value._unparenthesize_tuple()
        self.assertEqual('a, b', f.src)
        self.assertEqual((0, 0, 0, 4), f.loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].loc)
        self.assertEqual((0, 0, 0, 4), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)
        self.assertEqual((0, 3, 0, 4), f.body[0].value.elts[1].loc)

        f = parse('( # pre\ni,\n# post\n)').f
        f.body[0].value._unparenthesize_tuple()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].loc)
        self.assertEqual((0, 0, 0, 2), f.body[0].value.loc)
        self.assertEqual((0, 0, 0, 1), f.body[0].value.elts[0].loc)

        f = parse('( # pre\ni,\n# post\n)').body[0].value.f.copy()
        f._unparenthesize_tuple()
        self.assertEqual('i,', f.src)
        self.assertEqual((0, 0, 0, 2), f.loc)
        self.assertEqual((0, 0, 0, 1), f.elts[0].loc)

    def test__fix(self):
        f = FST.fromsrc('if 1:\n a\nelif 2:\n b')
        fc = f.a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual(fc.lines[0], 'elif 2:')
        fc._fix(inplace=True)
        self.assertEqual(fc.lines[0], 'if 2:')
        fc.verify(raise_=True)

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual(fc.src, '1 +\n2')
        fc._fix(inplace=True)
        self.assertEqual(fc.src, '(1 +\n2)')
        fc.verify(raise_=True)

        f = FST.fromsrc('i = 1')
        self.assertIs(f.a.body[0].targets[0].ctx.__class__, Store)
        fc = f.a.body[0].targets[0].f.copy(fix=False)
        self.assertIs(fc.a.ctx.__class__, Store)
        fc._fix(inplace=True)
        self.assertIs(fc.a.ctx.__class__, Load)
        fc.verify(raise_=True)

        f = FST.fromsrc('if 1: pass\nelif 2: pass').a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual('elif 2: pass', f.src)

        g = f._fix(inplace=False)
        self.assertIsNot(g, f)
        self.assertEqual('if 2: pass', g.src)
        self.assertEqual('elif 2: pass', f.src)

        g = f._fix(inplace=True)
        self.assertIs(g, f)
        self.assertEqual('if 2: pass', g.src)
        self.assertEqual('if 2: pass', f.src)

        f = FST.fromsrc('i, j = 1, 2').a.body[0].targets[0].f.copy(fix=False)
        self.assertEqual('i, j', f.src)
        self.assertIsNot(f, f._fix(inplace=False))

        g = f._fix(inplace=False)
        self.assertFalse(compare_asts(f.a, g.a))
        self.assertIs(g, g._fix(inplace=False))

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(fix=False)
        self.assertEqual('w := x,', f.src)

        g = f._fix(inplace=False)
        self.assertEqual('(w := x,)', g.src)
        self.assertTrue(compare_asts(f.a, g.a, locs=False))
        self.assertFalse(compare_asts(f.a, g.a, locs=True))
        self.assertIs(g, g._fix(inplace=False))

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('1 +\n2', fc.src)
        fd = fc._fix(inplace=False)
        self.assertEqual('(1 +\n2)', fd.src)
        fc._fix(inplace=True)
        self.assertEqual('(1 +\n2)', fc.src)

        f = FST.fromsrc('yield a1, a2')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('yield a1, a2', fc.src)
        fd = fc._fix(inplace=False)
        self.assertEqual('(yield a1, a2)', fd.src)
        self.assertEqual('yield a1, a2', fc.src)
        fc._fix(inplace=True)
        self.assertEqual('(yield a1, a2)', fc.src)

        f = FST.fromsrc('yield from a')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('yield from a', fc.src)
        fd = fc._fix(inplace=False)
        self.assertEqual('(yield from a)', fd.src)
        self.assertEqual('yield from a', fc.src)
        fc._fix(inplace=True)
        self.assertEqual('(yield from a)', fc.src)

        f = FST.fromsrc('await a')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('await a', fc.src)
        fd = fc._fix(inplace=False)
        self.assertEqual('(await a)', fd.src)
        self.assertEqual('await a', fc.src)
        fc._fix(inplace=True)
        self.assertEqual('(await a)', fc.src)

        f = FST.fromsrc("""[
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format
]""".strip())
        fc = f.a.body[0].value.elts[0].f.copy(fix=False)
        self.assertEqual("""
"Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format""".strip(), fc.src)
        fd = fc._fix(inplace=False)
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fd.src)
        fc._fix(inplace=True)
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fc.src)

        f = FST.fromsrc("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))
        """.strip())
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual("""
(is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute))""".strip(), fc.src)
        fd = fc._fix(inplace=False)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fd.src)
        fc._fix(inplace=True)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fc.src)

        if sys.version_info[:2] >= (3, 12):
            fc = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(fix=False)
            self.assertEqual('*tuple[int, ...]', fc.src)
            fd = fc._fix(inplace=False)
            self.assertEqual('(*tuple[int, ...],)', fd.src)
            fc._fix(inplace=True)
            self.assertEqual('(*tuple[int, ...],)', fc.src)

    def test_loc(self):
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.loc)  # arguments
        self.assertEqual((0, 5, 0, 8), parse('with f(): pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((1, 2, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.loc)  # match_case
        self.assertEqual((0, 3, 0, 25), parse('[i for i in range(5) if i]').body[0].value.generators[0].f.loc)  # comprehension
        self.assertEqual((0, 3, 0, 25), parse('(i for i in range(5) if i)').body[0].value.generators[0].f.loc)  # comprehension

        self.assertEqual((0, 5, 0, 12), parse('with ( f() ): pass').body[0].items[0].f.loc)  # withitem w/ parens
        self.assertEqual((0, 5, 0, 21), parse('with ( f() ) as ( f ): pass').body[0].items[0].f.loc)  # withitem w/ parens
        self.assertEqual((1, 2, 1, 28), parse('match a:\n  case ( 2 ) if a == 1: pass').body[0].cases[0].f.loc)  # match_case w/ parens
        self.assertEqual((0, 3, 0, 33), parse('[i for ( i ) in range(5) if ( i ) ]').body[0].value.generators[0].f.loc)  # comprehension w/ parens
        self.assertEqual((0, 3, 0, 33), parse('(i for ( i ) in range(5) if ( i ) )').body[0].value.generators[0].f.loc)  # comprehension w/ parens

        self.assertEqual('( f() ) as ( f )', parse('with ( f() ) as ( f ): pass').body[0].items[0].f.src)
        self.assertEqual('( f() ) as ( f )', parse('with ( f() ) as ( f ), ( g() ) as ( g ): pass').body[0].items[0].f.src)
        self.assertEqual('( g() ) as ( g )', parse('with ( f() ) as ( f ), ( g() ) as ( g ): pass').body[0].items[1].f.src)
        self.assertEqual('case ( 2 ) if a == 1: pass', parse('match a:\n  case ( 2 ) if a == 1: pass').body[0].cases[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('[ ( i ) for ( i ) in range(5) if ( i ) ]').body[0].value.generators[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('( ( i ) for ( i ) in range(5) if ( i ) )').body[0].value.generators[0].f.src)
        self.assertEqual(None, parse('def f(): pass').body[0].args.f.src)
        self.assertEqual('a', parse('def f(a): pass').body[0].args.f.src)
        self.assertEqual('a', parse('def f( a ): pass').body[0].args.f.src)
        self.assertEqual(None, parse('lambda: None').body[0].value.args.f.src)
        self.assertEqual('a = ( 1 )', parse('lambda a = ( 1 ) : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 )', parse('lambda *, z, a, b = ( 2 ) : None').body[0].value.args.f.src)
        self.assertEqual('*s, a, b = ( 2 )', parse('lambda *s, a, b = ( 2 ) : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 ),', parse('lambda *, z, a, b = ( 2 ), : None').body[0].value.args.f.src)
        self.assertEqual('**ss', parse('lambda **ss : None').body[0].value.args.f.src)
        self.assertEqual('*, z, a, b = ( 2 )', parse('def f( *, z, a, b = ( 2 ) ): pass').body[0].args.f.src)
        self.assertEqual('*s, a, b = ( 2 )', parse('def f( *s, a, b = ( 2 ) ): pass').body[0].args.f.src)
        self.assertEqual('*, z, a, b = ( 2 ),', parse('def f( *, z, a, b = ( 2 ), ): pass').body[0].args.f.src)
        self.assertEqual('**ss', parse('def f( **ss ): pass').body[0].args.f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('[ ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) ]').body[0].value.generators[0].f.src)
        self.assertEqual('for ( i ) in range(5) if ( i )', parse('( ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) )').body[0].value.generators[0].f.src)
        self.assertEqual('for ( j ) in range(6) if ( j )', parse('[ ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) ]').body[0].value.generators[1].f.src)
        self.assertEqual('for ( j ) in range(6) if ( j )', parse('( ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) )').body[0].value.generators[1].f.src)

        # loc from children calculated at root
        self.assertEqual((0, 0, 0, 12), parse('match a:\n case 1: pass').body[0].cases[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 6), parse('with a as b: pass').body[0].items[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 1), parse('def f(a): pass').body[0].args.f.copy().loc)
        self.assertEqual((0, 0, 0, 1), parse('lambda a: None').body[0].value.args.f.copy().loc)
        self.assertEqual((0, 0, 0, 10), parse('[i for i in j]').body[0].value.generators[0].f.copy().loc)
        self.assertEqual((0, 0, 0, 15), parse('[i for i in j if k]').body[0].value.generators[0].f.copy().loc)

    def test_bloc(self):
        ast = parse('@deco\nclass cls:\n @deco\n def meth():\n  @deco\n  class fcls: pass')

        self.assertEqual((0, 0, 5, 18), ast.f.loc)
        self.assertEqual((0, 0, 5, 18), ast.f.bloc)
        self.assertEqual((1, 0, 5, 18), ast.body[0].f.loc)
        self.assertEqual((0, 0, 5, 18), ast.body[0].f.bloc)
        self.assertEqual((3, 1, 5, 18), ast.body[0].body[0].f.loc)
        self.assertEqual((2, 1, 5, 18), ast.body[0].body[0].f.bloc)
        self.assertEqual((5, 2, 5, 18), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((4, 2, 5, 18), ast.body[0].body[0].body[0].f.bloc)

    def test_fromsrc_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromsrc(read(fnm))

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_False_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(ast_.unparse(ast_.parse(read(fnm)))), calc_loc=False)

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_True_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(read(fnm)), calc_loc=True)

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_fromast_calc_loc_copy_bulk(self):
        for fnm in PYFNMS:
            fst = FST.fromast(ast_.parse(read(fnm)), calc_loc='copy')

            walktest(fst.a)
            fst.verify(raise_=True)

    def test_verify(self):
        ast = parse('i = 1')
        ast.f.verify(raise_=True)

        ast.body[0].lineno = 100

        self.assertRaises(WalkFail, ast.f.verify, raise_=True)
        self.assertEqual(None, ast.f.verify(raise_=False))

    def test_pars_special(self):
        f = parse('''
( (
 (
   a
  ) )
)
        '''.strip()).body[0].value.f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 0, 4, 1))

        f = parse('''
( (
 (
   a
  ) )
,)
        '''.strip()).body[0].value.elts[0].f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 2, 3, 5))

        f = parse('''
(

   a

,)
        '''.strip()).body[0].value.elts[0].f
        p = f.pars()
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (2, 3, 2, 4))

        self.assertEqual((0, 1, 0, 15), parse('f(i for i in j)').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 16), parse('f((i for i in j))').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 18), parse('f(((i for i in j)))').body[0].value.args[0].f.pars())
        self.assertEqual((0, 2, 0, 14), parse('f(i for i in j)').body[0].value.args[0].f.pars(exc_genexpr_solo=True))
        self.assertEqual((0, 2, 0, 16), parse('f((i for i in j))').body[0].value.args[0].f.pars(exc_genexpr_solo=True))
        self.assertEqual((0, 2, 0, 18), parse('f(((i for i in j)))').body[0].value.args[0].f.pars(exc_genexpr_solo=True))

    def test_walk(self):
        a = parse("""
def f(a, b=1, *c, d=2, **e): pass
            """.strip()).body[0].args
        l = list(a.f.walk(True))
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
        l = list(a.f.walk(True))
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
        l = list(a.f.walk(True))
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
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.posonlyargs[0].f)
        self.assertIs(l[2], a.defaults[0].f)
        self.assertIs(l[3], a.args[0].f)
        self.assertIs(l[4], a.defaults[1].f)

        a = parse("""
call(a, b=1, *c, d=2, **e)
            """.strip()).body[0].value
        l = list(a.f.walk(True))
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
        l = list(a.f.walk(True))
        self.assertIs(l[0], a.f)
        self.assertIs(l[1], a.func.f)
        self.assertIs(l[2], a.func.value.f)
        self.assertIs(l[3], a.keywords[0].f)
        self.assertIs(l[4], a.keywords[0].value.f)
        self.assertIs(l[5], a.args[0].f)
        self.assertIs(l[6], a.args[0].value.f)

        f = parse('[] + [i for i in l]').body[0].value.f
        self.assertEqual(12, len(list(f.walk(False))))
        self.assertEqual(8, len(list(f.walk('all'))))
        self.assertEqual(7, len(list(f.walk(True))))
        # self.assertEqual(1, len(list(f.walk('allown'))))  # doesn't support
        self.assertEqual(4, len(list(f.walk('own'))))

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
        for f in (gen := fst.walk(True, scope=True)):
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

    def test_walk_bulk(self):
        for fnm in PYFNMS:
            ast       = FST.fromsrc(read(fnm)).a
            bln, bcol = 0, 0

            for f in (gen := ast.f.walk(True)):
                if isinstance(f.a, JoinedStr):  # these are borked
                    gen.send(False)

                    continue

                self.assertTrue(f.bln > bln or (f.bln == bln and f.bcol >= bcol))

                lof = list(f.walk(True, self_=False, recurse=False))
                lob = list(f.walk(True, self_=False, recurse=False, back=True))

                self.assertEqual(lof, lob[::-1])

                lf, c = [], None
                while c := f.next_child(c, True): lf.append(c)
                self.assertEqual(lf, lof)

                lb, c = [], None
                while c := f.prev_child(c, True): lb.append(c)
                self.assertEqual(lb, lob)

                bln, bcol = f.bln, f.bcol

    def test_walk_modify(self):
        fst = parse('if 1:\n a\n b\n c\nelse:\n d\n e').body[0].f
        i   = 0

        for f in fst.walk(self_=False):
            if f.pfield.name in ('body', 'orelse'):
                f.replace(str(i := i + 1))

        self.assertEqual(fst.src, 'if 1:\n 1\n 2\n 3\nelse:\n 4\n 5')

        fst = parse('[a, b, c]').body[0].f
        i   = 0

        for f in fst.walk(self_=False):
            if f.pfield.name == 'elts':
                f.replace(str(i := i + 1))

        self.assertEqual(fst.src, '[1, 2, 3]')

    def test_next_prev(self):
        fst = parse('a and b and c and d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.op.f)
        self.assertIs((f := fst.next_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.values[3].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.values[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.op.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        if sys.version_info[:2] >= (3, 12):
            fst = parse('@deco\ndef f[T, U](a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
            a = fst.a
            f = None
            self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, True)), a.args.f)
            self.assertIs((f := fst.next_child(f, True)), a.returns.f)
            self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, True)), None)
            f = None
            self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.next_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.next_child(f, False)), a.args.f)
            self.assertIs((f := fst.next_child(f, False)), a.returns.f)
            self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.next_child(f, False)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, True)), a.args.f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, True)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, True)), None)
            f = None
            self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
            self.assertIs((f := fst.prev_child(f, False)), a.args.f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[1].f)
            self.assertIs((f := fst.prev_child(f, False)), a.type_params[0].f)
            self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
            self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('@deco\ndef f(a, /, b: int, *, c: int = 2) -> str: pass').body[0].f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.args.f)
        self.assertIs((f := fst.next_child(f, True)), a.returns.f)
        self.assertIs((f := fst.next_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.args.f)
        self.assertIs((f := fst.next_child(f, False)), a.returns.f)
        self.assertIs((f := fst.next_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, True)), a.args.f)
        self.assertIs((f := fst.prev_child(f, True)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.body[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.returns.f)
        self.assertIs((f := fst.prev_child(f, False)), a.args.f)
        self.assertIs((f := fst.prev_child(f, False)), a.decorator_list[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('a <= b == c >= d').body[0].value.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.left.f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.left.f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.ops[2].f)
        self.assertIs((f := fst.next_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.left.f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[2].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.comparators[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.ops[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.left.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('match a:\n case {1: a, 2: b, **rest}: pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.keys[0].f)
        self.assertIs((f := fst.prev_child(f, False)), None)

        fst = parse('match a:\n case cls(1, 2, a=3, b=4): pass').body[0].cases[0].pattern.f
        a = fst.a
        f = None
        self.assertIs((f := fst.next_child(f, True)), a.cls.f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, True)), None)
        f = None
        self.assertIs((f := fst.next_child(f, False)), a.cls.f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.next_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.next_child(f, False)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, True)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, True)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, True)), None)
        f = None
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.kwd_patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[1].f)
        self.assertIs((f := fst.prev_child(f, False)), a.patterns[0].f)
        self.assertIs((f := fst.prev_child(f, False)), a.cls.f)
        self.assertIs((f := fst.prev_child(f, False)), None)

    def test_next_prev_vs_walk(self):
        def test1(src):
            f = FST.fromsrc(src).a.body[0].args.f
            m = list(f.walk(True, self_=False, recurse=False))

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
            m = list(f.walk(True, self_=False, recurse=False))

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

    def test_next_prev_step_vs_walk(self):
        def test(src):
            fst = FST.fromsrc(src.strip())

            f, l = fst, []
            while f := f.next_step(True): l.append(f)
            self.assertEqual(l, list(fst.walk(True, self_=False)))

            f, l = fst, []
            while f := f.next_step(False): l.append(f)
            self.assertEqual(l, list(fst.walk(False, self_=False)))

            f, l = fst, []
            while f := f.next_step('own'): l.append(f)
            self.assertEqual(l, list(fst.walk('own', self_=False)))

            f, l = fst, []
            while f := f.next_step('allown'): l.append(f)
            self.assertEqual(l, [g for g in fst.walk(True, self_=False) if g.has_own_loc])

            f, l = fst, []
            while f := f.prev_step(True): l.append(f)
            self.assertEqual(l, list(fst.walk(True, self_=False, back=True)))

            f, l = fst, []
            while f := f.prev_step(False): l.append(f)
            self.assertEqual(l, list(fst.walk(False, self_=False, back=True)))

            f, l = fst, []
            while f := f.prev_step('own'): l.append(f)
            self.assertEqual(l, list(fst.walk('own', self_=False, back=True)))

            f, l = fst, []
            while f := f.prev_step('allown'): l.append(f)
            self.assertEqual(l, [g for g in fst.walk(True, self_=False, back=True) if g.has_own_loc])

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

    def test_child_path(self):
        f = parse('if 1: a = (1, 2, {1: 2})').f
        p = f.child_path(f.body[0].body[0].value.elts[2].keys[0], True)

        self.assertEqual(p, 'body[0].body[0].value.elts[2].keys[0]')
        self.assertIs(f.child_from_path(p), f.body[0].body[0].value.elts[2].keys[0])

        p = f.child_path(f.body[0].body[0].value.elts[2].keys[0], False)

        self.assertEqual(p, [astfield(name='body', idx=0), astfield(name='body', idx=0),
                             astfield(name='value', idx=None), astfield(name='elts', idx=2),
                             astfield(name='keys', idx=0)])
        self.assertIs(f.child_from_path(p), f.body[0].body[0].value.elts[2].keys[0])

        self.assertRaises(ValueError, f.child_path, parse('1').f)

    def test_is_parenthesized_tuple(self):
        self.assertTrue(parse('(1, 2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,),)').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('((a), b)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(a, (b))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((a), (b))').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('(\n1,2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1\n,2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,\n2)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,2\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(1,\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1)\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1),\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n,))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,\n))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,)\n)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(\n(1,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((\n1,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1\n,),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,\n),)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,)\n,)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((1,),\n)').body[0].value.f.is_parenthesized_tuple())

        self.assertTrue(parse('((a), b)').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('(a, (b))').body[0].value.f.is_parenthesized_tuple())
        self.assertTrue(parse('((a), (b))').body[0].value.f.is_parenthesized_tuple())

        self.assertFalse(parse('(1,),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('(1),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((1)),').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((1,),),').body[0].value.f.is_parenthesized_tuple())

        self.assertFalse(parse('(a), b').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((a)), b').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('a, (b)').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('a, ((b))').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('(a), (b)').body[0].value.f.is_parenthesized_tuple())
        self.assertFalse(parse('((a)), ((b))').body[0].value.f.is_parenthesized_tuple())

        self.assertIsNone(parse('[(a), (b)]').body[0].value.f.is_parenthesized_tuple())

    def test_get_indent(self):
        ast = parse('i = 1; j = 2')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual('', ast.body[1].f.get_indent())

        ast = parse('def f(): \\\n i = 1')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())

        ast = parse('class cls: i = 1')

        self.assertEqual('', ast.body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())

        ast = parse('class cls: i = 1; \\\n    j = 2')

        self.assertEqual(ast.f.root.indent, ast.body[0].body[0].f.get_indent())
        self.assertEqual(ast.f.root.indent, ast.body[0].body[1].f.get_indent())

        ast = parse('class cls:\n  i = 1; \\\n    j = 2')

        self.assertEqual('  ', ast.body[0].body[0].f.get_indent())
        self.assertEqual('  ', ast.body[0].body[1].f.get_indent())

        ast = parse('class cls:\n   def f(): i = 1')

        self.assertEqual('   ', ast.body[0].body[0].f.get_indent())
        self.assertEqual('   ' + ast.f.root.indent, ast.body[0].body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   1').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): 1').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1').body[0].body[0].f.get_indent())

        self.assertEqual('    ', parse('class cls:\n def f():\n    1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('     ', parse('class cls:\n def f(): 1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('     ', parse('class cls:\n def f(): \\\n   1').body[0].body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('class cls:\n def f(): # \\\n   1').body[0].body[0].body[0].f.get_indent())

        self.assertEqual('  ', parse('if 1:\n  2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: 2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('if 1: \\\n 2\nelse:\n   3').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('if 1: # \\\n  2\nelse:\n   3').body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('if 1:\n  2\nelse:\n   3').body[0].orelse[0].f.get_indent())
        self.assertEqual('    ', parse('if 1:\n  2\nelse: 3').body[0].orelse[0].f.get_indent())
        self.assertEqual('    ', parse('if 1:\n  2\nelse: \\\n 3').body[0].orelse[0].f.get_indent())
        self.assertEqual('   ', parse('if 1:\n  2\nelse: # \\\n   3').body[0].orelse[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): 1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): \\\n  1; 2').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('def f(): # \\\n  1; 2').body[0].body[1].f.get_indent())

        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('try:\n\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f.get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[1].f.get_indent())
        self.assertEqual('  ', parse('try:\n  \\\ni\n  j\nexcept: pass').body[0].body[0].f.get_indent())

        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[0].f.get_indent())
        self.assertEqual('   ', parse('def f():\n   i; j').body[0].body[1].f.get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[0].f.get_indent())
        self.assertEqual('    ', parse('def f(): i; j').body[0].body[1].f.get_indent())

        self.assertEqual('', parse('\\\ni').body[0].f.get_indent())
        self.assertEqual('    ', parse('try: i\nexcept: pass').body[0].body[0].f.get_indent())

    def test_get_indentable_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = "... \\\n2"\n else:\n  j \\\n=\\\n 2'
        ast = parse(src)

        self.assertEqual({1, 2, 5, 7, 8, 9, 10}, ast.f.get_indentable_lns(1))
        self.assertEqual({0, 1, 2, 5, 7, 8, 9, 10}, ast.f.get_indentable_lns(0))

        f = FST.fromsrc('''
def _splitext(p, sep, altsep, extsep):
    """Split the extension from a pathname.

    Extension is everything from the last dot to the end, ignoring
    leading dots.  Returns "(root, ext)"; ext may be empty."""
    # NOTE: This code must work for text and bytes strings.

    sepIndex = p.rfind(sep)
            '''.strip())
        self.assertEqual({0, 1, 2, 3, 4, 5, 6, 7}, f.get_indentable_lns(docstr=True))
        self.assertEqual({0, 1, 5, 6, 7}, f.get_indentable_lns(docstr=False))

        f = FST.fromsrc(r'''
_CookiePattern = re.compile(r"""
    \s*                            # Optional whitespace at start of cookie
    (?P<key>                       # Start of group 'key'
    [""" + _LegalKeyChars + r"""]+?   # Any word of at least one letter
    )                              # End of group 'key'
    (                              # Optional group: there may not be a value.
    \s*=\s*                          # Equal Sign
    (?P<val>                         # Start of group 'val'
    "(?:[^\\"]|\\.)*"                  # Any doublequoted string
    |                                  # or
    \w{3},\s[\w\d\s-]{9,11}\s[\d:]{8}\sGMT  # Special case for "expires" attr
    |                                  # or
    [""" + _LegalValueChars + r"""]*      # Any word or empty string
    )                                # End of group 'val'
    )?                             # End of optional value group
    \s*                            # Any number of spaces.
    (\s+|;|$)                      # Ending either at space, semicolon, or EOS.
    """, re.ASCII | re.VERBOSE)    # re.ASCII may be removed if safe.
            '''.strip())
        self.assertEqual({0}, f.get_indentable_lns(docstr=True))
        self.assertEqual({0}, f.get_indentable_lns(docstr=False))

        f = FST.fromsrc('''
"distutils.command.sdist.check_metadata is deprecated, \\
        use the check command instead"
            '''.strip())
        self.assertEqual({0, 1}, f.get_indentable_lns(docstr=True))
        self.assertEqual({0}, f.get_indentable_lns(docstr=False))

    def test_offset(self):
        src = 'i = 1\nj = 2\nk = 3'

        ast = parse(src)
        ast.f.offset(1, 4, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 5, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f.offset(1, 5, 0, 1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f.offset(1, 5, 0, 1, True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 6), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 0, 3, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 4, 3, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f.offset(1, 4, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((3, 3, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f.offset(1, 5, 1, -1)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 2, 5), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        ast = parse(src)
        ast.f.offset(1, 5, 1, -1, True)
        self.assertEqual((1, 4, 1, 5), ((n := ast.body[0].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 0, 2, 1), ((n := ast.body[1].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((2, 4, 3, 4), ((n := ast.body[1].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 0, 4, 1), ((n := ast.body[2].targets[0]).lineno, n.col_offset, n.end_lineno, n.end_col_offset))
        self.assertEqual((4, 4, 4, 5), ((n := ast.body[2].value).lineno, n.col_offset, n.end_lineno, n.end_col_offset))

        def get():
            m = parse('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nbbbb\ncccc')

            m.body[0] = m.body[0].value
            m.body[1] = m.body[1].value
            m.body[2] = m.body[2].value

            m.body[0].lineno         = 1
            m.body[0].end_lineno     = 1
            m.body[0].col_offset     = 2
            m.body[0].end_col_offset = 6
            m.body[1].lineno         = 1
            m.body[1].end_lineno     = 1
            m.body[1].col_offset     = 6
            m.body[1].end_col_offset = 10
            m.body[2].lineno         = 1
            m.body[2].end_lineno     = 1
            m.body[2].col_offset     = 6
            m.body[2].end_col_offset = 6

            return m

        m = get()
        m.f.offset(0, 6, 0, 2, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 8, 0, 8), m.body[2].f.loc)

        m = get()
        m.f.offset(0, 6, 0, 2, True)
        self.assertEqual((0, 2, 0, 8), m.body[0].f.loc)
        self.assertEqual((0, 8, 0, 12), m.body[1].f.loc)
        self.assertEqual((0, 6, 0, 8), m.body[2].f.loc)

        m = get()
        m.f.offset(0, 6, 0, -2, False)
        self.assertEqual((0, 2, 0, 6), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 6), m.body[2].f.loc)

        m = get()
        m.f.offset(0, 6, 0, -2, True)
        self.assertEqual((0, 2, 0, 4), m.body[0].f.loc)
        self.assertEqual((0, 4, 0, 8), m.body[1].f.loc)
        self.assertEqual((0, 4, 0, 4), m.body[2].f.loc)

    def test_offset_cols(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j = 2'

        ast = parse(src)
        lns = ast.f.get_indentable_lns(1)
        ast.f.offset_cols(1, lns)
        self.assertEqual({1, 2, 5, 6, 7}, lns)
        self.assertEqual((0, 0, 7, 7), ast.f.loc)
        self.assertEqual((0, 0, 7, 8), ast.body[0].f.loc)
        self.assertEqual((1, 2, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 5, 1, 9), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].f.get_indentable_lns(1)
        ast.body[0].body[0].f.offset_cols(1, lns)
        self.assertEqual({2, 5, 6, 7}, lns)
        self.assertEqual((1, 1, 7, 8), ast.body[0].body[0].f.loc)
        self.assertEqual((1, 4, 1, 8), ast.body[0].body[0].test.f.loc)
        self.assertEqual((2, 3, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 3, 2, 4), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 7, 4, 3), ast.body[0].body[0].body[0].value.f.loc)
        self.assertEqual((5, 3, 5, 8), ast.body[0].body[0].body[1].f.loc)
        self.assertEqual((5, 3, 5, 4), ast.body[0].body[0].body[1].targets[0].f.loc)
        self.assertEqual((5, 7, 5, 8), ast.body[0].body[0].body[1].value.f.loc)
        self.assertEqual((7, 3, 7, 8), ast.body[0].body[0].orelse[0].f.loc)
        self.assertEqual((7, 3, 7, 4), ast.body[0].body[0].orelse[0].targets[0].f.loc)
        self.assertEqual((7, 7, 7, 8), ast.body[0].body[0].orelse[0].value.f.loc)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f.get_indentable_lns(1)
        ast.body[0].body[0].body[0].f.offset_cols(1, lns)
        self.assertEqual(set(), lns)
        self.assertEqual((2, 2, 4, 3), ast.body[0].body[0].body[0].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[0].body[0].body[0].targets[0].f.loc)
        self.assertEqual((2, 6, 4, 3), ast.body[0].body[0].body[0].value.f.loc)

    def test_offset_cols_mapped(self):
        src = 'i = 1\nj = 2\nk = 3\nl = \\\n4'
        ast = parse(src)
        off = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4}

        ast.f.offset_cols_mapped(off)
        self.assertEqual((0, 0, 4, 1), ast.f.loc)
        self.assertEqual((0, 0, 0, 5), ast.body[0].f.loc)
        self.assertEqual((0, 0, 0, 1), ast.body[0].targets[0].f.loc)
        self.assertEqual((0, 4, 0, 5), ast.body[0].value.f.loc)
        self.assertEqual((1, 1, 1, 6), ast.body[1].f.loc)
        self.assertEqual((1, 1, 1, 2), ast.body[1].targets[0].f.loc)
        self.assertEqual((1, 5, 1, 6), ast.body[1].value.f.loc)
        self.assertEqual((2, 2, 2, 7), ast.body[2].f.loc)
        self.assertEqual((2, 2, 2, 3), ast.body[2].targets[0].f.loc)
        self.assertEqual((2, 6, 2, 7), ast.body[2].value.f.loc)
        self.assertEqual((3, 3, 4, 5), ast.body[3].f.loc)
        self.assertEqual((3, 3, 3, 4), ast.body[3].targets[0].f.loc)
        self.assertEqual((4, 4, 4, 5), ast.body[3].value.f.loc)

    def test_indent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f.indent_lns('  ')
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n   if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f.indent_lns('  ')
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n    i = """\nj\n"""\n    k = 3\n   else:\n    j \\\n  =\\\n   2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f.indent_lns('  ')
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f.indent_lns('  ')
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n  =\\\n   2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.f.indent_lns('  ')
        self.assertEqual({1, 2}, lns)
        self.assertEqual('@decorator\n  class cls:\n   pass', ast.f.src)

    def test_dedent_lns(self):
        src = 'class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2'

        ast = parse(src)
        lns = ast.f.dedent_lns(' ')
        self.assertEqual({1, 2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\nif True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].f.dedent_lns(' ')
        self.assertEqual({2, 5, 6, 7, 8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n i = """\nj\n"""\n k = 3\nelse:\n j \\\n=\\\n2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].body[0].f.dedent_lns(' ')
        self.assertEqual(set(), lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n 2', ast.f.src)

        ast = parse(src)
        lns = ast.body[0].body[0].orelse[0].f.dedent_lns(' ')
        self.assertEqual({8, 9}, lns)
        self.assertEqual('class cls:\n if True:\n  i = """\nj\n"""\n  k = 3\n else:\n  j \\\n=\\\n2', ast.f.src)

        src = '@decorator\nclass cls:\n pass'

        ast = parse(src)
        lns = ast.body[0].body[0].f.dedent_lns(' ')
        self.assertEqual(set(), lns)
        self.assertEqual('@decorator\nclass cls:\n pass', ast.f.src)

        # ast = parse(src)
        # lns = ast.body[0].body[0].f.dedent_lns(' ', skip=0)
        # self.assertEqual({2}, lns)
        # self.assertEqual('@decorator\nclass cls:\npass', ast.f.src)

    def test_dedent_multiline_strings(self):
        f = parse('''
class cls:
    def func():
        i = """This is a
        normal
        multiline string"""

        j = ("This is a "
        "split "
        "multiline string")

        k = f"""This is a
        normal
        multiline f-string"""

        l = (f"This is a "
        "split "
        f"multiline f-string")
            '''.strip()).body[0].body[0].f
        self.assertEqual('''
def func():
    i = """This is a
        normal
        multiline string"""

    j = ("This is a "
    "split "
    "multiline string")

    k = f"""This is a
        normal
        multiline f-string"""

    l = (f"This is a "
    "split "
    f"multiline f-string")
            '''.strip(), f.copy().src)

        f = parse('''
class cls:
    def func():
        l = (f"This is a "
        f"split " """
        super
        special
        """
        f"multiline f-string")
            '''.strip()).body[0].body[0].f
        self.assertEqual('''
def func():
    l = (f"This is a "
    f"split " """
        super
        special
        """
    f"multiline f-string")
            '''.strip(), f.copy().src)

    def test_copy_lines(self):
        src = 'class cls:\n if True:\n  i = 1\n else:\n  j = 2'
        ast = parse(src)

        self.assertEqual(src.split('\n'), ast.f.get_lines(*ast.f.loc))
        self.assertEqual(src.split('\n'), ast.body[0].f.get_lines(*ast.body[0].f.loc))
        self.assertEqual('if True:\n  i = 1\n else:\n  j = 2'.split('\n'), ast.body[0].body[0].f.get_lines(*ast.body[0].body[0].f.loc))
        self.assertEqual(['i = 1'], ast.body[0].body[0].body[0].f.get_lines(*ast.body[0].body[0].body[0].f.loc))
        self.assertEqual(['j = 2'], ast.body[0].body[0].orelse[0].f.get_lines(*ast.body[0].body[0].orelse[0].f.loc))

        self.assertEqual(['True:', '  i'], ast.f.root.get_lines(1, 4, 2, 3))

    def test_put_src(self):
        f = FST(Load(), lines=[bistr('')])
        f.put_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['test'])
        f.put_src('test', 0, 0, 0, 0)
        self.assertEqual(f.lines, ['testtest'])
        f.put_src('tost', 0, 0, 0, 8)
        self.assertEqual(f.lines, ['tost'])
        f.put_src('a\nb\nc', 0, 2, 0, 2)
        self.assertEqual(f.lines, ['toa', 'b', 'cst'])
        f.put_src('', 0, 3, 2, 1)
        self.assertEqual(f.lines, ['toast'])
        f.put_src('a\nb\nc\nd', 0, 0, 0, 5)
        self.assertEqual(f.lines, ['a', 'b', 'c', 'd'])
        f.put_src('efg\nhij', 1, 0, 2, 1)
        self.assertEqual(f.lines, ['a', 'efg', 'hij', 'd'])
        f.put_src('***', 1, 2, 2, 1)
        self.assertEqual(f.lines, ['a', 'ef***ij', 'd'])

    def test_pars(self):
        for src, elt, slice_copy in PARS_DATA:
            src  = src.strip()
            t    = parse(src)
            f    = eval(f't.{elt}', {'t': t}).f
            l    = f.pars()
            ssrc = f.get_src(*l)

            try:
                self.assertEqual(ssrc, slice_copy.strip())

            except Exception:
                print(elt)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_pars_special(self):
        f = parse('((1), ( (2) ))').body[0].value.f
        self.assertEqual(1, f.elts[0].pars(ret_npars=True)[1])
        self.assertEqual(2, f.elts[1].pars(ret_npars=True)[1])
        self.assertEqual(0, f.pars(ret_npars=True)[1])

        self.assertEqual(1, parse('call(((i for i in j)))').body[0].value.args[0].f.pars(ret_npars=True)[1])
        self.assertEqual(0, parse('call((i for i in j))').body[0].value.args[0].f.pars(ret_npars=True)[1])
        self.assertEqual(0, parse('call(i for i in j)').body[0].value.args[0].f.pars(ret_npars=True)[1])
        self.assertEqual(-1, parse('call(i for i in j)').body[0].value.args[0].f.pars(ret_npars=True, exc_genexpr_solo=True)[1])

    def test_comms(self):
        f = parse('''
# hello

# world
pass  # postcomment
# next line

# last line
pass
        '''.strip()).body[0].f

        g = f.comms()
        self.assertIsInstance(g, fstloc)
        self.assertEqual((2, 0, 4, 0), g)
        g = f.comms(True, False)
        self.assertIsInstance(g, fstloc)
        self.assertEqual((2, 0, 3, 4), g)
        g = f.comms('all', False)
        self.assertIsInstance(g, fstloc)
        self.assertEqual((0, 0, 3, 4), g)
        g = f.comms(False, True)
        self.assertIsInstance(g, fstloc)
        self.assertEqual((3, 0, 4, 0), g)
        g = f.comms(False, 'block')
        self.assertIsInstance(g, fstloc)
        self.assertEqual((3, 0, 5, 0), g)
        g = f.comms(False, 'all')
        self.assertIsInstance(g, fstloc)
        self.assertEqual((3, 0, 7, 0), g)

        g = f.comms()
        self.assertIsInstance(g, fstloc)
        self.assertEqual((2, 0, 4, 0), g)
        g = f.comms(True, False)
        self.assertIsInstance(g, fstloc)
        self.assertEqual((2, 0, 3, 4), g)
        g = f.comms(False, True)
        self.assertIsInstance(g, fstloc)
        self.assertEqual((3, 0, 4, 0), g)
        g = f.comms(False, False)
        self.assertIs(g, f.loc)

        f = parse('''
pass
# next line

# last line
pass
        '''.strip()).body[0].f

        g = f.comms(False, 'all')
        self.assertIsInstance(g, fstloc)
        self.assertEqual('pass\n# next line\n\n# last line\n', f.get_src(*g))

        lines = '''  # hello

  # world
  pass  # whatever
# whenever
            '''.split('\n')

        self.assertEqual((2, 0), FST.src_edit.pre_comments(lines, 0, 0, 3, 2))
        self.assertEqual((4, 0), FST.src_edit.post_comments(lines, 3, 6, 5, 0))
        self.assertEqual(None, FST.src_edit.pre_comments(lines, 0, 0, 2, 2))
        self.assertEqual(None, FST.src_edit.post_comments(lines, 2, 9, 5, 0))
        self.assertEqual((0, 0), FST.src_edit.pre_comments(lines, 0, 0, 2, 2, 'all'))
        self.assertEqual((5, 0), FST.src_edit.post_comments(lines, 3, 6, 5, 0, 'all'))

        lines = '''
i ; \\
# pre
j # post
k
'''.strip().split('\n')

        self.assertEqual((1, 0), FST.src_edit.pre_comments(lines, 0, 1, 2, 0))

    def test_copy_special(self):
        f = FST.fromsrc('@decorator\nclass cls:\n  pass')
        self.assertEqual(f.a.body[0].f.copy(fix=False).src, '@decorator\nclass cls:\n  pass')
        # self.assertEqual(f.a.body[0].f.copy(decos=False, fix=False).src, 'class cls:\n  pass')

        l = FST.fromsrc("['\\u007f', '\\u0080', 'ʁ', 'ᛇ', '時', '🐍', '\\ud800', 'Źdźbło']").a.body[0].value.elts
        self.assertEqual("'\\u007f'", l[0].f.copy().src)
        self.assertEqual("'\\u0080'", l[1].f.copy().src)
        self.assertEqual("'ʁ'", l[2].f.copy().src)
        self.assertEqual("'ᛇ'", l[3].f.copy().src)
        self.assertEqual("'時'", l[4].f.copy().src)
        self.assertEqual("'🐍'", l[5].f.copy().src)
        self.assertEqual("'\\ud800'", l[6].f.copy().src)
        self.assertEqual("'Źdźbło'", l[7].f.copy().src)

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(fix=True)
        self.assertEqual('(w := x,)', f.src)

        f = FST.fromsrc('a[1:2, 3:4]').a.body[0].value.slice.f.copy(fix=False)
        self.assertIs(f._fix(inplace=False), f)
        # self.assertRaises(SyntaxError, f.fix)
        # self.assertIs(None, f._fix(raise_=False))

        f = FST.fromsrc('''
if 1:
    def f():
        """
        strict docstring
        """
        """
        loose docstring
        """
            '''.strip())
        self.assertEqual('''
def f():
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    async def f():
        """
        strict docstring
        """
        """
        loose docstring
        """
            '''.strip())
        self.assertEqual('''
async def f():
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())
        self.assertEqual('''
class cls:
    """
    strict docstring
    """
    """
    loose docstring
    """
            '''.strip(), f.a.body[0].body[0].f.copy().src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())

        self.assertEqual('''
class cls:
    """
        strict docstring
        """
    """
        loose docstring
        """
            '''.strip(), f.a.body[0].body[0].f.copy(docstr=False).src)

        f = FST.fromsrc('''
if 1:
    class cls:
        """
        strict docstring
        """
        """
        loose docstring
        """
          '''.strip())

        self.assertEqual('''
class cls:
    """
    strict docstring
    """
    """
        loose docstring
        """
            '''.strip(), f.a.body[0].body[0].f.copy(docstr='strict').src)


        f = FST.fromsrc('''
# start

"""docstring"""

i = 1

# end
            '''.strip())
        self.assertEqual((g := f.copy()).get_src(*g.loc), f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            ''')
        self.assertEqual('i', a.body[0].f.copy(precomms=False, postcomms=False).src)
        self.assertEqual('# pre\ni', a.body[0].f.copy(precomms=True, postcomms=False).src)
        self.assertEqual('# pre\ni # post\n', a.body[0].f.copy(precomms=True, postcomms=True).src)
        self.assertEqual('# prepre\n\n# pre\ni', a.body[0].f.copy(precomms='all', postcomms=False).src)

        a = parse('( i )')
        self.assertEqual('i', a.body[0].value.f.copy(precomms=False, postcomms=False).src)
        self.assertEqual('( i )', a.body[0].value.f.copy(precomms=False, postcomms=False, pars=True).src)

        if sys.version_info[:2] >= (3, 12):
            f = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(fix=True)
            self.assertEqual('(*tuple[int, ...],)', f.src)

    def test_copy_bulk(self):
        for fnm in PYFNMS:
            ast = FST.fromsrc(read(fnm)).a

            for a in walk(ast):
                if a.f.is_parsable():
                    f = a.f.copy(fix=True)
                    f.verify(raise_=True)

    def test_copy(self):
        for src, elt, slice_copy, slice_dump in COPY_DATA:
            src   = src.strip()
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.copy(fix=True)
            ssrc  = s.src
            sdump = s.dump(out=list, compact=True)

            try:
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print(elt)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_cut_special(self):
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

    def test_cut_and_del_special(self):
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
        # fst.a.body[1].f._put_slice_stmt('pass', None, None, None, False, True, force=True)

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
        # fst.a.body[1].f._put_slice_stmt('pass', None, None, None, False, True, force=True)

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
            # point._put_slice_stmt(None, None, None, field, False, True, force=True)

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
        # fst.a.body[1].f._put_slice_stmt('pass', None, None, None, False, True, force=True)

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
        # fst.a.body[1].f._put_slice_stmt('pass', None, None, None, False, True, force=True)

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
            asts = [a for a in walk(ast) if isinstance(a, fst.STATEMENTISH)]

            for a in asts[::-1]:
                a.f.cut()

            ast  = parse(src.strip())
            asts = [a for a in walk(ast) if isinstance(a, fst.STATEMENTISH)]

            for a in asts[::-1]:
                field, idx = a.f.pfield

                a.f.parent.put_slice(None, idx, idx + 1, field)

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
        # a.body[0].f._put_slice_stmt('i', None, None, None, False, True, force=True)
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
        # a.body[0].body[0].f._put_slice_stmt('i', None, None, None, False, True, force=True)
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
        # fst.a.body[1].f._put_slice_stmt('pass', None, None, None, False, True, force=True)

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
            # f._put_slice_stmt(bs.pop(), 0, 0, field, False, True, force=True)

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
                # f._put_slice_stmt(bs.pop(), 0, 0, field, False, True, force=True)

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
        # fst.a.body[1].f._put_slice_stmt('pass', None, None, None, False, True, force=True)

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
            # point._put_slice_stmt(f'# {i}', 0, 0, field, False, True, force=True)

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
        # a.body[1].f._put_slice_stmt('# pre\nn  # post', 0, 0, 'handlers', False, True, force=True)
        a.body[1].f.put_slice('i', 0, 0, 'handlers', check_node_type=False)
        # a.body[1].f._put_slice_stmt('i', 0, 0, 'handlers', False, True, force=True)
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
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.elts[1].f.replace(f).root.src)

        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.f.put(f, 1).root.src)

        f = parse('( a )').body[0].value.f.copy(pars=True)
        self.assertEqual('[1, ( a ), 3]', parse('[1, 2, 3]').body[0].value.f.put_slice(f, 1, 2, one=True).root.src)

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
        self.assertIsNone(g.a)

    def test_replace_raw(self):
        old_defaults = set_defaults(pars=False)

        f = parse('def f(a, b): pass').f
        g = f.body[0].args.args[1]
        self.assertEqual('b', g.src)
        h = f.body[0].args.args[1].replace('c=1', raw=True)
        self.assertEqual('def f(a, c=1): pass', f.src)
        self.assertEqual('c', h.src)
        self.assertIsNone(g.a)
        i = f.body[0].args.args[1].replace('**d', raw=True, to=f.body[0].args.defaults[0])
        self.assertEqual('def f(a, **d): pass', f.src)
        self.assertEqual('d', i.src)
        self.assertIsNone(h.a)

        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.generators[1].replace('for x in y', raw=True)
        f = f.repath()
        self.assertEqual(f.src, '[a for c in d for x in y for a in b]')
        self.assertEqual(g.src, 'for x in y')
        g = f.generators[1].replace(None, raw=True)
        f = f.repath()
        self.assertEqual(f.src, '[a for c in d  for a in b]')
        self.assertIsNone(g)
        g = f.generators[1].replace(None, raw=True)
        f = f.repath()
        self.assertEqual(f.src, '[a for c in d  ]')
        self.assertIsNone(g)

        f = parse('f(i for i in j)').body[0].value.args[0].f
        g = f.replace('a', raw=True)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f(a)')

        f = parse('f((i for i in j))').body[0].value.args[0].f
        g = f.replace('a', raw=True)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f(a)')

        f = parse('f(((i for i in j)))').body[0].value.args[0].f
        g = f.replace('a', raw=True)
        self.assertEqual(g.src, 'a')
        self.assertEqual(f.root.src, 'f((a))')

        self.assertEqual('y', parse('n', mode='eval').body.f.replace('y').root.src)  # Expression.body

        set_defaults(**old_defaults)

    def test_replace_existing_single(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_SINGLE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.replace(None if src == '**DEL**' else src, **options) or f.root

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

    def test_put_existing_single(self):
        for i, (dst, attr, options, src, put_ret, put_src) in enumerate(REPLACE_EXISTING_SINGLE_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.replace(None if src == '**DEL**' else src, **options) or f.root

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

    def test_put_raw_special(self):
        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.put('for x in y', 1, raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d for x in y for a in b]')
        f = g
        g = f.put(None, 1, raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d  for a in b]')
        f = g
        g = f.put(None, 1, raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d  ]')
        f = g

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

        self.assertEqual('y', parse('n', mode='eval').f.put('y', field='body').root.src)  # Expression.body

    def test_put_raw_random_same(self):
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
                put_lines = master.get_lines(ln, col, end_ln, end_col)

                copy.put_raw(put_lines, ln, col, end_ln, end_col)
                copy.verify()

                compare_asts(master.a, copy.a, locs=True, raise_=True)

                assert copy.src == master.src

        except Exception:
            print('Random seed was:', rndseed)
            print(i, ln, col, end_ln, end_col)
            print('-'*80)
            print(copy.src)

            raise

    def test_put_slice_raw(self):
        f = parse('[a for c in d for b in c for a in b]').body[0].value.f
        g = f.put_slice('for x in y', 1, 2, raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d for x in y for a in b]')
        f = g
        g = f.put_slice(None, 1, 2, raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d  for a in b]')
        f = g
        g = f.put_slice(None, 1, 2, raw=True)
        self.assertIsNot(g, f)
        self.assertEqual(g.src, '[a for c in d  ]')
        f = g

        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('{a, x, y, c}', parse('{a, b, c}').body[0].value.f.put_slice('x, y', 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice('x: x, y: y', 1, 2, raw=True).root.src)

        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice('(x, y)', 1, 2, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice('[x, y]', 1, 2, raw=True).root.src)
        self.assertEqual('{a, {x, y}, c}', parse('{a, b, c}').body[0].value.f.put_slice('{x, y}', 1, 2, raw=True).root.src)  # invalid set but valid syntax
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, '{x: x, y: y}', 1, 2, raw=True)

        # strip delimiters if present
        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_.parse('x, y'), 1, 2, raw=True).root.src)
        self.assertEqual('(a, x, y, c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_.parse('(x, y)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x, y]'), 1, 2, raw=True).root.src)
        self.assertEqual('{a, x, y, c}', parse('{a, b, c}').body[0].value.f.put_slice(ast_.parse('{x, y}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_.parse('{x: x, y: y}'), 1, 2, raw=True).root.src)

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

        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('x,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('(x,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('{x,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_.parse('{x: x,}'), 1, 2, raw=True).root.src)

        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('x, y,'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('(x, y,)'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x, y,]'), 1, 2, raw=True).root.src)
        self.assertEqual('[a, x, y, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('{x, y,}'), 1, 2, raw=True).root.src)
        self.assertEqual('{a: a, x: x, y: y, c: c}', parse('{a: a, b: b, c: c}').body[0].value.f.put_slice(ast_.parse('{x: x, y: y,}'), 1, 2, raw=True).root.src)

        # as one so dont strip delimiters or add to unparenthesized tuple
        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_.parse('x, y'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('(a, (x, y), c)', parse('(a, b, c)').body[0].value.f.put_slice(ast_.parse('(x, y)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x, y]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('{a, {x, y}, c}', parse('{a, b, c}').body[0].value.f.put_slice(ast_.parse('{x, y}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_.parse('{x: x, y: y}'), 1, 2, one=True, raw=True)

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

        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('x,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x,), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('(x,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x}, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('{x,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_.parse('{x: x,}'), 1, 2, one=True, raw=True)

        self.assertEqual('[a, (x, y), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('x, y,'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, (x, y), c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('(x, y,)'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, [x, y], c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('[x, y,]'), 1, 2, one=True, raw=True).root.src)
        self.assertEqual('[a, {x, y}, c]', parse('[a, b, c]').body[0].value.f.put_slice(ast_.parse('{x, y,}'), 1, 2, one=True, raw=True).root.src)
        self.assertRaises(SyntaxError, parse('{a: a, b: b, c: c}').body[0].value.f.put_slice, ast_.parse('{x: x, y: y,}'), 1, 2, one=True, raw=True)

    def test_put_special_fields(self):
        old_defaults = set_defaults(pars=False)

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

        set_defaults(**old_defaults)

    def test_get_slice_seq_copy(self):
        for src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump in GET_SLICE_SEQ_DATA:
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                s     = f.get_slice(start, stop, cut=False, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                sdump = s.dump(out=list, compact=True)

                self.assertEqual(tsrc, src.strip())
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_get_slice_seq_cut(self):
        for src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump in GET_SLICE_SEQ_DATA:
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                s     = f.get_slice(start, stop, cut=True, **options)
                tsrc  = t.f.src
                ssrc  = s.src
                tdump = t.f.dump(out=list, compact=True)
                sdump = s.dump(out=list, compact=True)

                self.assertEqual(tsrc, src_cut.strip())
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(tdump, src_dump.strip().split('\n'))
                self.assertEqual(sdump, slice_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
                print('---')
                print(src)
                print('...')
                print(src_cut)
                print('...')
                print(slice_copy)

                raise

    def test_get_slice_stmt_copy(self):
        for name in ('GET_SLICE_STMT_DATA', 'GET_SLICE_STMT_NOVERIFY_DATA'):
            verify = 'NOVERIFY' not in name

            for src, elt, start, stop, field, options, _, slice_cut, _, slice_dump in globals()[name]:
                t = parse(src)
                f = (eval(f't.{elt}', {'t': t}) if elt else t).f

                try:
                    s     = f.get_slice(start, stop, field, cut=False, **options)
                    tsrc  = t.f.src
                    ssrc  = s.src
                    sdump = s.dump(out=list, compact=True)

                    if verify:
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
        for name in ('GET_SLICE_STMT_DATA', 'GET_SLICE_STMT_NOVERIFY_DATA'):
            verify = 'NOVERIFY' not in name

            for src, elt, start, stop, field, options, src_cut, slice_cut, src_dump, slice_dump in globals()[name]:
                t = parse(src)
                f = (eval(f't.{elt}', {'t': t}) if elt else t).f

                try:
                    s     = f.get_slice(start, stop, field, cut=True, **options)
                    tsrc  = t.f.src
                    ssrc  = s.src
                    tdump = t.f.dump(out=list, compact=True)
                    sdump = s.dump(out=list, compact=True)

                    if verify:
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

    def test_put_slice_seq_del(self):
        for src, elt, start, stop, options, src_cut, slice_copy, src_dump, slice_dump in GET_SLICE_SEQ_DATA:
            t = parse(src)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                f.put_slice(None, start, stop, **options)

                tdst  = t.f.src
                tdump = t.f.dump(out=list, compact=True)

                self.assertEqual(tdst, src_cut.strip())
                self.assertEqual(tdump, src_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
                print('---')
                print(src)

                raise

    def test_put_slice_seq(self):
        for dst, elt, start, stop, src, put_src, put_dump in PUT_SLICE_SEQ_DATA:
            t = parse(dst)
            f = eval(f't.{elt}', {'t': t}).f

            try:
                f.put_slice(None if src == '**DEL**' else src, start, stop)

                tdst  = t.f.src
                tdump = t.f.dump(out=list, compact=True)

                self.assertEqual(tdst, put_src.strip())
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
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
                    tdump = t.f.dump(out=list, compact=True)

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
                tdump = t.f.dump(out=list, compact=True)

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
                tdump = t.f.dump(out=list, compact=True)

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

    def test_put_raw(self):
        for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_RAW_DATA):
            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                g = f.put_raw(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root

                tdst  = f.root.src
                tdump = f.root.dump(out=list, compact=True)

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

    def test_put_raw_from_put_slice_data(self):
        for i, (dst, attr, start, stop, field, options, src, put_src, put_dump) in enumerate(PUT_SLICE_DATA):
            if options != {'raw': True}:
                continue

            t = parse(dst)
            f = (eval(f't.{attr}', {'t': t}) if attr else t).f

            try:
                loc = f._raw_slice_loc(start, stop, field)

                f.put_raw(None if src == '**DEL**' else src, *loc, **options)

                # ffrom, fto = f._raw_slice_from_to(start, stop, field)

                # if not (ffrom.is_FST and fto.is_FST):
                #     continue

                # ffrom.replace(None if src == '**DEL**' else src, to=fto, **options)  # raw=True is in `options`

                tdst  = f.root.src
                tdump = f.root.dump(out=list, compact=True)

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

    def test_put_default_non_list_field(self):
        self.assertEqual('y', parse('n').body[0].f.put('y').root.src)  # Expr
        self.assertEqual('return y', parse('return n').body[0].f.put('y').root.src)  # Return
        self.assertEqual('await y', parse('await n').body[0].value.f.put('y').root.src)  # Await
        self.assertEqual('yield y', parse('yield n').body[0].value.f.put('y').root.src)  # Yield
        self.assertEqual('yield from y', parse('yield from n').body[0].value.f.put('y').root.src)  # YieldFrom
        self.assertEqual('[*y]', parse('[*n]').body[0].value.elts[0].f.put('y').root.src)  # Starred
        self.assertEqual('match a:\n case "y": pass', parse('match a:\n case "n": pass').body[0].cases[0].pattern.f.put('"y"').root.src)  # MatchValue

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

    def test_line_continuation_error_at_top_level(self):
        # Works fine in a scope but error at top level

#         a = parse('''
# i ; \\
#  j
#         '''.strip())
#         a.f.put_slice(None, 0, 1)
#         self.assertFalse(a.f.verify(raise_=False))

#         a = parse('''
# i ; \\
#  j
#         '''.strip())
#         a.f.put_slice('l', 0, 1)
#         self.assertFalse(a.f.verify(raise_=False))

        pass

    def test_unparenthesized_tuple_with_line_continuations(self):
        # backslashes are annoying to include in the regenerable test cases

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 1, cut=True)
        self.assertEqual(a.f.src, '(2, \\\n3)')
        self.assertEqual(s.src, '(1, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(1, 2, cut=True)
        self.assertEqual(a.f.src, '(1, \\\n3)')
        self.assertEqual(s.src, '(\n2, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(2, 3, cut=True)
        self.assertEqual(a.f.src, '(1, \\\n2, \\\n)')
        self.assertEqual(s.src, '(\n3,)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 2, cut=True)
        self.assertEqual(a.f.src, '3,')
        self.assertEqual(s.src, '(1, \\\n2, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(1, 3, cut=True)
        self.assertEqual(a.f.src, '(1, \\\n)')
        self.assertEqual(s.src, '(\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        s = a.body[0].value.f.get_slice(0, 3, cut=True)
        self.assertEqual(a.f.src, '()')
        self.assertEqual(s.src, '(1, \\\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 0)
        self.assertEqual(a.f.src, '(a, \\\n1, \\\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 1)
        self.assertEqual(a.f.src, '(1, \\\na, \\\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 2, 2)
        self.assertEqual(a.f.src, '(1, \\\n2, \\\na, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 3, 3)
        self.assertEqual(a.f.src, '(1, \\\n2, \\\n3, a, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 1)
        self.assertEqual(a.f.src, '(a, \\\n2, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 2)
        self.assertEqual(a.f.src, '(1, \\\na, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 2, 3)
        self.assertEqual(a.f.src, '(1, \\\n2, \\\na, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 2)
        self.assertEqual(a.f.src, '(a, \\\n3)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 1, 3)
        self.assertEqual(a.f.src, '(1, \\\na, \\\n)')

        a = parse('1, \\\n2, \\\n3')
        a.body[0].value.f.put_slice('(a, \\\n)', 0, 3)
        self.assertEqual(a.f.src, '(a, \\\n)')

    def test_unparenthesized_tuple_put_as_one(self):
        f = parse('(1, 2, 3)').body[0].value.f
        f.put('a, b', 1)
        self.assertEqual('(1, (a, b), 3)', f.src)

    def test_fstlistproxy(self):
        self.assertEqual('a', parse('if 1: a').f.body[0].body[0].src)
        self.assertEqual('b', parse('if 1: a\nelse: b').f.body[0].orelse[0].src)
        self.assertEqual('a\nb\nc', parse('a\nb\nc').f.body.copy().src)

        f = parse('a\nb\nc').f
        g = f.body.cut()
        self.assertEqual('', f.src)
        self.assertEqual('a\nb\nc', g.src)

        f = parse('a\nb\nc\nd\ne').f
        g = f.body[1:4].cut()
        self.assertEqual('a\ne', f.src)
        self.assertEqual('b\nc\nd', g.src)

        f = parse('a\nb\nc\nd\ne').f
        g = f.body[1:4]
        g.replace('f')
        self.assertEqual(1, len(g))
        self.assertEqual('f', g[0].src)
        self.assertEqual('a\nf\ne', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.append('d')
        self.assertEqual(2, len(g))
        self.assertEqual('b', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('a\nb\nd\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.extend('d\ne')
        self.assertEqual(3, len(g))
        self.assertEqual('b', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('a\nb\nd\ne\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prepend('d')
        self.assertEqual(2, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('b', g[1].src)
        self.assertEqual('a\nd\nb\nc', f.src)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prextend('d\ne')
        self.assertEqual(3, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('e', g[1].src)
        self.assertEqual('b', g[2].src)
        self.assertEqual('a\nd\ne\nb\nc', f.src)

        f = parse('a\nb\nc').f
        f.body[1:2] = 'd\ne'
        self.assertEqual('a\nd\ne\nc', f.src)

        f = parse('a\nb\nc').f
        f.body[1] = 'd'
        self.assertEqual('a\nd\nc', f.src)

        f = parse('a\nb\nc\nd\ne').f
        f.body[1:4] = 'f'
        self.assertEqual('a\nf\ne', f.src)

        f = parse('a\nb\nc\nd\ne').f
        f.body[1:4] = 'f\ng'
        self.assertEqual('a\nf\ng\ne', f.src)

        f = parse('a\nb\nc').f
        def test():
            f.body[1] = 'd\ne'
        self.assertRaises(ValueError, test)

        f = parse('a\nb\nc').f
        g = f.body[1:2]
        g.prextend('d\ne')

        f = parse('a\nb\nc').f
        g = f.body
        g.cut()
        self.assertEqual(0, len(g))
        self.assertEqual('', f.src)
        g.append('d')
        self.assertEqual(1, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('d\n', f.src)
        g.prepend('e')
        self.assertEqual(2, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('e\nd\n', f.src)
        g.extend('f\ng')
        self.assertEqual(4, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('f', g[2].src)
        self.assertEqual('g', g[3].src)
        self.assertEqual('e\nd\nf\ng\n', f.src)
        g.prextend('h\ni')
        self.assertEqual(6, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('i', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('d', g[3].src)
        self.assertEqual('f', g[4].src)
        self.assertEqual('g', g[5].src)
        self.assertEqual('h\ni\ne\nd\nf\ng\n', f.src)
        g.replace('h')
        self.assertEqual(1, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('h\n', f.src)
        g.insert('i')
        self.assertEqual(2, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('h', g[1].src)
        self.assertEqual('i\nh\n', f.src)
        g.insert('j', 1)
        self.assertEqual(3, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('h', g[2].src)
        self.assertEqual('i\nj\nh\n', f.src)
        g.insert('k', -1)
        self.assertEqual(4, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('i\nj\nk\nh\n', f.src)
        g.insert('l', 'end')
        self.assertEqual(5, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('l', g[4].src)
        self.assertEqual('i\nj\nk\nh\nl\n', f.src)

        f = parse('x\na\nb\nc\ny').f
        g = f.body[1:-1]
        g.cut()
        self.assertEqual(0, len(g))
        self.assertEqual('x\ny', f.src)
        g.append('d')
        self.assertEqual(1, len(g))
        self.assertEqual('d', g[0].src)
        self.assertEqual('x\nd\ny', f.src)
        g.prepend('e')
        self.assertEqual(2, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('x\ne\nd\ny', f.src)
        g.extend('f\ng')
        self.assertEqual(4, len(g))
        self.assertEqual('e', g[0].src)
        self.assertEqual('d', g[1].src)
        self.assertEqual('f', g[2].src)
        self.assertEqual('g', g[3].src)
        self.assertEqual('x\ne\nd\nf\ng\ny', f.src)
        g.prextend('h\ni')
        self.assertEqual(6, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('i', g[1].src)
        self.assertEqual('e', g[2].src)
        self.assertEqual('d', g[3].src)
        self.assertEqual('f', g[4].src)
        self.assertEqual('g', g[5].src)
        self.assertEqual('x\nh\ni\ne\nd\nf\ng\ny', f.src)
        g.replace('h')
        self.assertEqual(1, len(g))
        self.assertEqual('h', g[0].src)
        self.assertEqual('x\nh\ny', f.src)
        g.insert('i')
        self.assertEqual(2, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('h', g[1].src)
        self.assertEqual('x\ni\nh\ny', f.src)
        g.insert('j', 1)
        self.assertEqual(3, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('h', g[2].src)
        self.assertEqual('x\ni\nj\nh\ny', f.src)
        g.insert('k', -1)
        self.assertEqual(4, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('x\ni\nj\nk\nh\ny', f.src)
        g.insert('l', 'end')
        self.assertEqual(5, len(g))
        self.assertEqual('i', g[0].src)
        self.assertEqual('j', g[1].src)
        self.assertEqual('k', g[2].src)
        self.assertEqual('h', g[3].src)
        self.assertEqual('l', g[4].src)
        self.assertEqual('x\ni\nj\nk\nh\nl\ny', f.src)

        a = parse('''
class cls:
    def prefunc(): pass
    def postfunc(): pass
            '''.strip())
        self.assertIsInstance(a.f.body, fstlistproxy)
        self.assertIsInstance(a.body[0].f.body, fstlistproxy)
        a.body[0].f.body.cut()
        self.assertIsInstance(a.body[0].f.body, fstlistproxy)

        a = parse('a\nb\nc\nd\ne')
        p = a.f.body[1:4]
        g = p[1]
        f = p.replace('f')
        self.assertEqual('a\nf\ne', a.f.src)
        self.assertEqual(1, len(f))
        self.assertEqual('f', f[0].src)
        self.assertIsNone(g.a)

    def test_is_node_type_properties_and_parents(self):
        fst = parse('''
match a:
    case 1:
        try:
            pass
        except Exception:
            class cls:
                def f():
                    return [lambda: None for i in ()]
            '''.strip())

        f = fst.body[0].cases[0].body[0].handlers[0].body[0].body[0].body[0].value.elt.body.f
        self.assertEqual(f.src, 'None')

        self.assertIsInstance((f := f.parent_scope()).a, Lambda)
        self.assertTrue(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertFalse(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtish)
        self.assertFalse(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_scope()).a, ListComp)
        self.assertTrue(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertFalse(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtish)
        self.assertFalse(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_named_scope()).a, FunctionDef)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_named_scope()).a, ClassDef)
        self.assertFalse(f.is_anon_scope)
        self.assertTrue(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertTrue(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmtish()).a, ExceptHandler)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmt()).a, Try)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_stmtish()).a, match_case)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertFalse(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_block()).a, Match)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertFalse(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertFalse(f.is_scope_or_mod)
        self.assertTrue(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertTrue(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertTrue(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertFalse(f.is_mod)

        self.assertIsInstance((f := f.parent_scope()).a, Module)
        self.assertFalse(f.is_anon_scope)
        self.assertFalse(f.is_named_scope)
        self.assertTrue(f.is_named_scope_or_mod)
        self.assertFalse(f.is_scope)
        self.assertTrue(f.is_scope_or_mod)
        self.assertFalse(f.is_block)
        self.assertTrue(f.is_block_or_mod)
        self.assertFalse(f.is_stmt)
        self.assertTrue(f.is_stmt_or_mod)
        self.assertFalse(f.is_stmtish)
        self.assertTrue(f.is_stmtish_or_mod)
        self.assertTrue(f.is_mod)

    def test_find_in_loc(self):
        f    = parse('abc += xyz').body[0].f
        fabc = f.target
        fpeq = f.op
        fxyz = f.value

        self.assertIs(f, f.find_in_loc(0, 0, 0, 10))
        self.assertIs(f, f.find_in_loc(-1, -1, 1, 11))
        self.assertIs(fabc, f.find_in_loc(0, 0, 0, 3))
        self.assertIs(fpeq, f.find_in_loc(0, 1, 0, 10))
        self.assertIs(fxyz, f.find_in_loc(0, 5, 0, 10))
        self.assertIs(None, f.find_in_loc(0, 5, 0, 6))

    def test_find_loc(self):
        f    = parse('abc += xyz').f
        fass = f.body[0]
        fabc = fass.target
        fpeq = fass.op
        fxyz = fass.value

        self.assertIs(fass, f.find_loc(0, 0, 0, 10))
        self.assertIs(None, f.find_loc(0, 0, 0, 10, False))
        self.assertIs(fabc, f.find_loc(0, 0, 0, 3))
        self.assertIs(fass, f.find_loc(0, 0, 0, 3, False))
        self.assertIs(fass, f.find_loc(0, 0, 0, 4))
        self.assertIs(fass, f.find_loc(0, 0, 0, 4, False))
        self.assertIs(fass, f.find_loc(0, 3, 0, 4, False))
        self.assertIs(fpeq, f.find_loc(0, 4, 0, 6))
        self.assertIs(fass, f.find_loc(0, 4, 0, 6, False))
        self.assertIs(fxyz, f.find_loc(0, 7, 0, 10))
        self.assertIs(fass, f.find_loc(0, 7, 0, 10, False))
        self.assertIs(fass, f.find_loc(0, 6, 0, 10))
        self.assertIs(fass, f.find_loc(0, 6, 0, 10, False))

        f  = parse('a+b').f
        fx = f.body[0]
        fo = fx.value
        fa = fo.left
        fp = fo.op
        fb = fo.right

        self.assertIs(fa, f.find_loc(0, 0, 0, 0))
        self.assertIs(fp, f.find_loc(0, 1, 0, 1))
        self.assertIs(fb, f.find_loc(0, 2, 0, 2))
        self.assertIs(f, f.find_loc(0, 3, 0, 3))
        self.assertIs(fa, f.find_loc(0, 0, 0, 1))
        self.assertIs(fo, f.find_loc(0, 0, 0, 2))
        self.assertIs(fo, f.find_loc(0, 0, 0, 3))
        self.assertIs(fp, f.find_loc(0, 1, 0, 2))
        self.assertIs(fo, f.find_loc(0, 1, 0, 3))
        self.assertIs(fb, f.find_loc(0, 2, 0, 3))

    def test_set_defaults(self):
        new = dict(
            docstr    = 'test_docstr',
            precomms  = 'test_precomms',
            postcomms = 'test_postcomms',
            prespace  = 'test_prespace',
            postspace = 'test_postspace',
            pep8space = 'test_pep8space',
            pars      = 'test_pars',
            elif_     = 'test_elif_',
            fix       = 'test_fix',
            raw       = 'test_raw',
        )

        old    = set_defaults(**new)
        newset = set_defaults(**old)
        oldset = set_defaults(**old)

        self.assertEqual(newset, new)
        self.assertEqual(oldset, old)


def regen_pars_data():
    newlines = []

    for src, elt, *_ in PARS_DATA:
        src   = src.strip()
        t     = parse(src)
        f     = eval(f't.{elt}', {'t': t}).f
        l     = f.pars()
        ssrc  = f.get_src(*l)

        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        newlines.append('(r"""')
        newlines.extend(f'''{src}\n""", {elt!r}, r"""\n{ssrc}\n"""),\n'''.split('\n'))

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('PARS_DATA = [')
    stop  = lines.index(']  # END OF PARS_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_copy_data():
    newlines = []

    for src, elt, *_ in COPY_DATA:
        src   = src.strip()
        t     = parse(src)
        f     = eval(f't.{elt}', {'t': t}).f
        s     = f.copy(fix=True)
        ssrc  = s.src
        sdump = s.dump(out=list, compact=True)

        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        s.verify(raise_=True)

        newlines.append('(r"""')
        newlines.extend(f'''{src}\n""", {elt!r}, r"""\n{ssrc}\n""", r"""'''.split('\n'))
        newlines.extend(sdump)
        newlines.append('"""),\n')

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('COPY_DATA = [')
    stop  = lines.index(']  # END OF COPY_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_get_slice_seq():
    newlines = []

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    for name in ('GET_SLICE_SEQ_DATA',):
        for src, elt, start, stop, options, *_ in globals()[name]:
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.get_slice(start, stop, cut=True, **options)
            tsrc  = t.f.src
            ssrc  = s.src
            tdump = t.f.dump(out=list, compact=True)
            sdump = s.dump(out=list, compact=True)

            assert not tsrc.startswith('\n') or tsrc.endswith('\n')
            assert not ssrc.startswith('\n') or ssrc.endswith('\n')

            if options.get('verify', True):
                t.f.verify(raise_=True)
                s.verify(raise_=True)

            newlines.extend(f'''(r"""{src}""", {elt!r}, {start}, {stop}, {options}, r"""\n{tsrc}\n""", r"""\n{ssrc}\n""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('""", r"""')
            newlines.extend(sdump)
            newlines.append('"""),\n')

        start = lines.index(f'{name} = [')
        stop  = lines.index(f']  # END OF {name}')

        lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_get_slice_stmt():
    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    for name in ('GET_SLICE_STMT_DATA', 'GET_SLICE_STMT_NOVERIFY_DATA'):
        verify   = 'NOVERIFY' not in name
        newlines = []

        for src, elt, start, stop, field, options, *_ in globals()[name]:
            t     = parse(src)
            f     = (eval(f't.{elt}', {'t': t}) if elt else t).f
            s     = f.get_slice(start, stop, field, cut=True, **options)
            tsrc  = t.f.src
            ssrc  = s.src
            tdump = t.f.dump(out=list, compact=True)
            sdump = s.dump(out=list, compact=True)

            if verify:
                t.f.verify(raise_=True)
                s.verify(raise_=True)

            newlines.extend(f'''(r"""{src}""", {elt!r}, {start}, {stop}, {field!r}, {options}, r"""{tsrc}""", r"""{ssrc}""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('""", r"""')
            newlines.extend(sdump)
            newlines.append('"""),\n')

        start = lines.index(f'{name} = [')
        stop  = lines.index(f']  # END OF {name}')

        lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_seq():
    newlines = []

    for dst, elt, start, stop, src, put_src, put_dump in PUT_SLICE_SEQ_DATA:
        t = parse(dst)
        f = eval(f't.{elt}', {'t': t}).f

        f.put_slice(None if src == '**DEL**' else src, start, stop)

        tdst  = t.f.src
        tdump = t.f.dump(out=list, compact=True)

        assert not tdst.startswith('\n') or tdst.endswith('\n')

        t.f.verify(raise_=True)

        newlines.extend(f'''(r"""{dst}""", {elt!r}, {start}, {stop}, r"""{src}""", r"""\n{tdst}\n""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_SEQ_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_SEQ_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_stmt():
    newlines = []

    for dst, stmt, start, stop, field, options, src, put_src, put_dump in PUT_SLICE_STMT_DATA:
        t = parse(dst)
        f = (eval(f't.{stmt}', {'t': t}) if stmt else t).f

        f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

        tdst  = t.f.src
        tdump = t.f.dump(out=list, compact=True)

        t.f.verify(raise_=True)

        newlines.extend(f'''(r"""{dst}""", {stmt!r}, {start}, {stop}, {field!r}, {options!r}, r"""{src}""", r"""{tdst}""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_STMT_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_STMT_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice():
    newlines = []

    for dst, attr, start, stop, field, options, src, put_src, put_dump in PUT_SLICE_DATA:
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        f.put_slice(None if src == '**DEL**' else src, start, stop, field, **options)

        tdst  = t.f.src
        tdump = t.f.dump(out=list, compact=True)

        t.f.verify(raise_=True)

        newlines.extend(f'''(r"""{dst}""", {attr!r}, {start}, {stop}, {field!r}, {options!r}, r"""{src}""", r"""{tdst}""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_raw():
    newlines = []

    for i, (dst, attr, (ln, col, end_ln, end_col), options, src, put_ret, put_src, put_dump) in enumerate(PUT_RAW_DATA):
        t = parse(dst)
        f = (eval(f't.{attr}', {'t': t}) if attr else t).f

        try:
            g = f.put_raw(None if src == '**DEL**' else src, ln, col, end_ln, end_col, **options) or f.root

            tdst  = f.root.src
            tdump = f.root.dump(out=list, compact=True)

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

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_RAW_DATA = [')
    stop  = lines.index(']  # END OF PUT_RAW_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-all', default=False, action='store_true', help="regenerate everything")
    parser.add_argument('--regen-pars', default=False, action='store_true', help="regenerate parentheses test data")
    parser.add_argument('--regen-copy', default=False, action='store_true', help="regenerate copy test data")
    parser.add_argument('--regen-get-slice-seq', default=False, action='store_true', help="regenerate get slice sequence test data")
    parser.add_argument('--regen-get-slice-stmt', default=False, action='store_true', help="regenerate get slice statement test data")
    parser.add_argument('--regen-put-slice-seq', default=False, action='store_true', help="regenerate put slice sequence test data")
    parser.add_argument('--regen-put-slice-stmt', default=False, action='store_true', help="regenerate put slice statement test data")
    parser.add_argument('--regen-put-slice', default=False, action='store_true', help="regenerate put slice test data")
    parser.add_argument('--regen-put-raw', default=False, action='store_true', help="regenerate put raw test data")

    args = parser.parse_args()

    if args.regen_pars or args.regen_all:
        print('Regenerating parentheses test data...')
        regen_pars_data()

    if args.regen_copy or args.regen_all:
        print('Regenerating copy test data...')
        regen_copy_data()

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

    if args.regen_put_raw or args.regen_all:
        print('Regenerating put raw test data...')
        regen_put_raw()

    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
