#!/usr/bin/env python

import os
import sys
import unittest
import ast as ast_
from random import seed, shuffle

from fst import *
from fst import fst

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
""", r"""
Call .. MOCK 0,5 -> 0,12
  .func
    Name 'f' Load .. 0,7 -> 0,8
"""),

(r"""
with ( f() ) as ( f ): pass
""", 'body[0].items[0].optional_vars', r"""
( f )
""", r"""
Name 'f' Store .. MOCK 0,16 -> 0,21
"""),

(r"""
with ( f() ) as ( f ), ( g() ) as ( g ): pass
""", 'body[0].items[0].context_expr', r"""
( f() )
""", r"""
Call .. MOCK 0,5 -> 0,12
  .func
    Name 'f' Load .. 0,7 -> 0,8
"""),

(r"""
with ( f() ) as ( f ), ( g() ) as ( g ): pass
""", 'body[0].items[0].optional_vars', r"""
( f )
""", r"""
Name 'f' Store .. MOCK 0,16 -> 0,21
"""),

(r"""
with ( f() ) as ( f ), ( g() ) as ( g ): pass
""", 'body[0].items[1].context_expr', r"""
( g() )
""", r"""
Call .. MOCK 0,23 -> 0,30
  .func
    Name 'g' Load .. 0,25 -> 0,26
"""),

(r"""
with ( f() ) as ( f ), ( g() ) as ( g ): pass
""", 'body[0].items[1].optional_vars', r"""
( g )
""", r"""
Name 'g' Store .. MOCK 0,34 -> 0,39
"""),

(r"""
match a:
  case ( 2 ) if a == 1: pass
""", 'body[0].cases[0].pattern', r"""
( 2 )
""", r"""
MatchValue .. MOCK 1,7 -> 1,12
  .value
    Constant 2 .. 1,9 -> 1,10
"""),

(r"""
[ ( i ) for ( j ) in ( range(5) ) if ( k ) ]
""", 'body[0].value.elt', r"""
( i )
""", r"""
Name 'i' Load .. MOCK 0,2 -> 0,7
"""),

(r"""
[ ( i ) for ( j ) in ( range(5) ) if ( k ) ]
""", 'body[0].value.generators[0].target', r"""
( j )
""", r"""
Name 'j' Store .. MOCK 0,12 -> 0,17
"""),

(r"""
[ ( i ) for ( j ) in ( range(5) ) if ( k ) ]
""", 'body[0].value.generators[0].iter', r"""
( range(5) )
""", r"""
Call .. MOCK 0,21 -> 0,33
  .func
    Name 'range' Load .. 0,23 -> 0,28
  .args[1]
  0] Constant 5 .. 0,29 -> 0,30
"""),

(r"""
[ ( i ) for ( j ) in ( range(5) ) if ( k ) ]
""", 'body[0].value.generators[0].ifs[0]', r"""
( k )
""", r"""
Name 'k' Load .. MOCK 0,37 -> 0,42
"""),

(r"""
( ( i ) for ( j ) in ( range(5) ) if ( k ) )
""", 'body[0].value.elt', r"""
( i )
""", r"""
Name 'i' Load .. MOCK 0,2 -> 0,7
"""),

(r"""
( ( i ) for ( j ) in ( range(5) ) if ( k ) )
""", 'body[0].value.generators[0].target', r"""
( j )
""", r"""
Name 'j' Store .. MOCK 0,12 -> 0,17
"""),

(r"""
( ( i ) for ( j ) in ( range(5) ) if ( k ) )
""", 'body[0].value.generators[0].iter', r"""
( range(5) )
""", r"""
Call .. MOCK 0,21 -> 0,33
  .func
    Name 'range' Load .. 0,23 -> 0,28
  .args[1]
  0] Constant 5 .. 0,29 -> 0,30
"""),

(r"""
( ( i ) for ( j ) in ( range(5) ) if ( k ) )
""", 'body[0].value.generators[0].ifs[0]', r"""
( k )
""", r"""
Name 'k' Load .. MOCK 0,37 -> 0,42
"""),

(r"""
def f(a=(1)): pass
""", 'body[0].args.defaults[0]', r"""
(1)
""", r"""
Constant 1 .. MOCK 0,8 -> 0,11
"""),

(r"""
def f( a = ( 1 )): pass
""", 'body[0].args.defaults[0]', r"""
( 1 )
""", r"""
Constant 1 .. MOCK 0,11 -> 0,16
"""),

(r"""
lambda a = ( 1 ) : None
""", 'body[0].value.args.defaults[0]', r"""
( 1 )
""", r"""
Constant 1 .. MOCK 0,11 -> 0,16
"""),

(r"""
(1, ( 2 ), 3)
""", 'body[0].value.elts[1]', r"""
( 2 )
""", r"""
Constant 2 .. MOCK 0,4 -> 0,9
"""),

(r"""
(1),
""", 'body[0].value.elts[0]', r"""
(1)
""", r"""
Constant 1 .. MOCK 0,0 -> 0,3
"""),

(r"""
((1),)
""", 'body[0].value.elts[0]', r"""
(1)
""", r"""
Constant 1 .. MOCK 0,1 -> 0,4
"""),

(r"""
(1), ( 2 )
""", 'body[0].value.elts[0]', r"""
(1)
""", r"""
Constant 1 .. MOCK 0,0 -> 0,3
"""),

(r"""
(1), ( 2 )
""", 'body[0].value.elts[1]', r"""
( 2 )
""", r"""
Constant 2 .. MOCK 0,5 -> 0,10
"""),

(r"""
((1), ( 2 ))
""", 'body[0].value.elts[0]', r"""
(1)
""", r"""
Constant 1 .. MOCK 0,1 -> 0,4
"""),

(r"""
((1), ( 2 ))
""", 'body[0].value.elts[1]', r"""
( 2 )
""", r"""
Constant 2 .. MOCK 0,6 -> 0,11
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
  .value
    Name 'opts' Load .. 0,0 -> 0,4
  .attr
    'ignore_module'
  .ctx Load
"""),

]  # END OF COPY_DATA

GET_SLICE_SEQ_CUT_DATA = [
(r"""
{1, 2}
""", 'body[0].value', 0, 0, r"""
{1, 2}
""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,6
  .body[1]
  0] Expr .. 0,0 -> 0,6
    .value
      Set .. 0,0 -> 0,6
        .elts[2]
        0] Constant 1 .. 0,1 -> 0,2
        1] Constant 2 .. 0,4 -> 0,5
""", r"""
Call .. ROOT 0,0 -> 0,5
  .func
    Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', None, None, r"""
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
    .value
      Tuple .. 0,0 -> 0,2
        .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  2] Constant 3 .. 3,4 -> 3,5
  .ctx Load
"""),

(r"""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 0, 2, r"""
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
    .value
      Tuple .. 0,0 -> 2,1
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

(r"""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 1, 2, r"""
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
    .value
      Tuple .. 0,0 -> 3,1
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

(r"""
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
""", 'body[0].value', 2, None, r"""
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
    .value
      Tuple .. 0,0 -> 3,1
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

(r"""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', None, None, r"""
()
""", r"""
(           # hello
    1, 2, 3 # last line
)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 1,7 -> 1,8
  2] Constant 3 .. 1,10 -> 1,11
  .ctx Load
"""),

(r"""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 0, 2, r"""
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
    .value
      Tuple .. 0,0 -> 2,1
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

(r"""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 1, 2, r"""
(           # hello
    1, 3 # last line
)
""", r"""
(2,)
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      Tuple .. 0,0 -> 2,1
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

(r"""
(           # hello
    1, 2, 3 # last line
)
""", 'body[0].value', 2, None, r"""
(           # hello
    1, 2)
""", r"""
(3, # last line
)
""", r"""
Module .. ROOT 0,0 -> 1,9
  .body[1]
  0] Expr .. 0,0 -> 1,9
    .value
      Tuple .. 0,0 -> 1,9
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

(r"""
1, 2, 3, 4
""", 'body[0].value', 1, 3, r"""
1, 4
""", r"""
(2, 3)
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value
      Tuple .. 0,0 -> 0,4
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

(r"""
1, 2, 3, 4
""", 'body[0].value', -1, None, r"""
1, 2, 3
""", r"""
(4,)
""", r"""
Module .. ROOT 0,0 -> 0,7
  .body[1]
  0] Expr .. 0,0 -> 0,7
    .value
      Tuple .. 0,0 -> 0,7
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

(r"""
1, 2, 3, 4
""", 'body[0].value', None, None, r"""
()
""", r"""
(1, 2, 3, 4)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
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

(r"""
1, 2, 3, 4
""", 'body[0].value', 1, 1, r"""
1, 2, 3, 4
""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,10
  .body[1]
  0] Expr .. 0,0 -> 0,10
    .value
      Tuple .. 0,0 -> 0,10
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

(r"""
1, 2, 3, 4
""", 'body[0].value', 1, None, r"""
1,
""", r"""
(2, 3, 4)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
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

(r"""
1, 2, 3, 4
""", 'body[0].value', 0, 3, r"""
4,
""", r"""
(1, 2, 3)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
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

(r"""
(1, 2
  ,  # comment
3, 4)
""", 'body[0].value', 1, 2, r"""
(1, 3, 4)
""", r"""
(2
  ,  # comment
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
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

(r"""
(1, 2
  ,
  3, 4)
""", 'body[0].value', 1, 2, r"""
(1, 3, 4)
""", r"""
(2
  ,
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
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

(r"""
(1, 2 \
  , \
  3, 4)
""", 'body[0].value', 1, 2, r"""
(1, 3, 4)
""", r"""
(2 \
  , \
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
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

(r"""
(1, 2  # comment
  , \
  3, 4)
""", 'body[0].value', 1, 2, r"""
(1, 3, 4)
""", r"""
(2  # comment
  , \
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
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

(r"""
(1, 2
  ,
3, 4)
""", 'body[0].value', 1, 2, r"""
(1, 3, 4)
""", r"""
(2
  ,
)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
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

(r"""
(1, 2
  , 3, 4)
""", 'body[0].value', 1, 2, r"""
(1, 3, 4)
""", r"""
(2
  ,)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
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

(r"""
(1, 2  # comment
  , 3, 4)
""", 'body[0].value', 1, 2, r"""
(1, 3, 4)
""", r"""
(2  # comment
  ,)
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,9
    .value
      Tuple .. 0,0 -> 0,9
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

(r"""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', None, None, r"""
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
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 1,6
      .value
        Tuple .. 1,4 -> 1,6
          .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  2] Constant 3 .. 3,4 -> 3,5
  .ctx Load
"""),

(r"""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 0, 2, r"""
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
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 3,5
      .value
        Tuple .. 1,4 -> 3,5
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

(r"""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 1, 2, r"""
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
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 4,5
      .value
        Tuple .. 1,4 -> 4,5
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

(r"""
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
""", 'body[0].body[0].value', 2, None, r"""
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
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,4 -> 4,5
      .value
        Tuple .. 1,4 -> 4,5
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

(r"""
{1: 2, **b, **c}
""", 'body[0].value', 1, 2, r"""
{1: 2, **c}
""", r"""
{**b}
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value
      Dict .. 0,0 -> 0,11
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

(r"""
{1: 2, **b, **c}
""", 'body[0].value', None, None, r"""
{}
""", r"""
{1: 2, **b, **c}
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Dict .. 0,0 -> 0,2
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

(r"""
{1: 2, **b, **c}
""", 'body[0].value', 2, None, r"""
{1: 2, **b}
""", r"""
{**c}
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value
      Dict .. 0,0 -> 0,11
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

(r"""
[
    1,
    2,
    3,
]
""", 'body[0].value', None, None, r"""
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
    .value
      List .. 0,0 -> 0,2
        .ctx Load
""", r"""
List .. ROOT 0,0 -> 4,1
  .elts[3]
  0] Constant 1 .. 1,4 -> 1,5
  1] Constant 2 .. 2,4 -> 2,5
  2] Constant 3 .. 3,4 -> 3,5
  .ctx Load
"""),

(r"""
[
    1,
    2,
    3,
]
""", 'body[0].value', 0, 2, r"""
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
    .value
      List .. 0,0 -> 2,1
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

(r"""
[
    1,
    2,
    3,
]
""", 'body[0].value', 1, 2, r"""
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
    .value
      List .. 0,0 -> 3,1
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

(r"""
[
    1,
    2,
    3,
]
""", 'body[0].value', 2, None, r"""
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
    .value
      List .. 0,0 -> 3,1
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

(r"""
[            # hello
    1, 2, 3,
    4
]
""", 'body[0].value', 2, 3, r"""
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
    .value
      List .. 0,0 -> 2,1
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

(r"""
[            # hello
    1, 2, ( 3
     ), 4
]
""", 'body[0].value', 2, 3, r"""
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
    .value
      List .. 0,0 -> 2,1
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

(r"""
[            # hello
    1, 2, ( 3
     ), 4
]
""", 'body[0].value', 1, 3, r"""
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
    .value
      List .. 0,0 -> 2,1
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

(r"""
[            # hello
    1, 2, ( 3
     ), 4
]
""", 'body[0].value', 1, None, r"""
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
    .value
      List .. 0,0 -> 1,6
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

(r"""
i =                (self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                id(self) & (_sys.maxsize*2 + 1))
""", 'body[0].value', 0, 3, r"""
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
    .value
      Tuple .. 0,19 -> 0,53
        .elts[1]
        0] BinOp .. 0,20 -> 0,51
          .left
            Call .. 0,20 -> 0,28
              .func
                Name 'id' Load .. 0,20 -> 0,22
              .args[1]
              0] Name 'self' Load .. 0,23 -> 0,27
          .op
            BitAnd
          .right
            BinOp .. 0,32 -> 0,50
              .left
                BinOp .. 0,32 -> 0,46
                  .left
                    Attribute .. 0,32 -> 0,44
                      .value
                        Name '_sys' Load .. 0,32 -> 0,36
                      .attr
                        'maxsize'
                      .ctx Load
                  .op
                    Mult
                  .right
                    Constant 2 .. 0,45 -> 0,46
              .op
                Add
              .right
                Constant 1 .. 0,49 -> 0,50
        .ctx Load
    .type_comment
      None
""", r"""
Tuple .. ROOT 0,0 -> 2,1
  .elts[3]
  0] Attribute .. 0,1 -> 0,24
    .value
      Attribute .. 0,1 -> 0,15
        .value
          Name 'self' Load .. 0,1 -> 0,5
        .attr
          '__class__'
        .ctx Load
    .attr
      '__name__'
    .ctx Load
  1] Attribute .. 0,26 -> 0,36
    .value
      Name 'self' Load .. 0,26 -> 0,30
    .attr
      '_name'
    .ctx Load
  2] BinOp .. 1,17 -> 1,52
    .left
      Attribute .. 1,17 -> 1,29
        .value
          Name 'self' Load .. 1,17 -> 1,21
        .attr
          '_handle'
        .ctx Load
    .op
      BitAnd
    .right
      BinOp .. 1,33 -> 1,51
        .left
          BinOp .. 1,33 -> 1,47
            .left
              Attribute .. 1,33 -> 1,45
                .value
                  Name '_sys' Load .. 1,33 -> 1,37
                .attr
                  'maxsize'
                .ctx Load
            .op
              Mult
            .right
              Constant 2 .. 1,46 -> 1,47
        .op
          Add
        .right
          Constant 1 .. 1,50 -> 1,51
  .ctx Load
"""),

(r"""
i = namespace = {**__main__.__builtins__.__dict__,
             **__main__.__dict__}
""", 'body[0].value', 0, 1, r"""
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
    .value
      Dict .. 0,16 -> 0,37
        .keys[1]
        0] None
        .values[1]
        0] Attribute .. 0,19 -> 0,36
          .value
            Name '__main__' Load .. 0,19 -> 0,27
          .attr
            '__dict__'
          .ctx Load
    .type_comment
      None
""", r"""
Dict .. ROOT 0,0 -> 1,1
  .keys[1]
  0] None
  .values[1]
  0] Attribute .. 0,3 -> 0,33
    .value
      Attribute .. 0,3 -> 0,24
        .value
          Name '__main__' Load .. 0,3 -> 0,11
        .attr
          '__builtins__'
        .ctx Load
    .attr
      '__dict__'
    .ctx Load
"""),

(r"""
env = {
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1",
    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}
""", 'body[0].value', None, 2, r"""
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
    .value
      Dict .. 0,6 -> 4,1
        .keys[3]
        0] Constant 'PYLAUNCHER_DRYRUN' .. 1,4 -> 1,23
        1] Constant 'PYLAUNCHER_LIMIT_TO_COMPANY' .. 2,4 -> 2,33
        2] None
        .values[3]
        0] Constant '1' .. 1,25 -> 1,28
        1] Constant '' .. 2,35 -> 2,37
        2] DictComp .. 3,6 -> 3,52
          .key
            Call .. 3,7 -> 3,16
              .func
                Attribute .. 3,7 -> 3,14
                  .value
                    Name 'k' Load .. 3,7 -> 3,8
                  .attr
                    'upper'
                  .ctx Load
          .value
            Name 'v' Load .. 3,18 -> 3,19
          .generators[1]
          0] comprehension .. 3,24 -> 3,51
            .target
              Tuple .. 3,24 -> 3,28
                .elts[2]
                0] Name 'k' Store .. 3,24 -> 3,25
                1] Name 'v' Store .. 3,27 -> 3,28
                .ctx Store
            .iter
              Call .. 3,32 -> 3,51
                .func
                  Attribute .. 3,32 -> 3,49
                    .value
                      BoolOp .. 3,33 -> 3,42
                        .op
                          Or
                        .values[2]
                        0] Name 'env' Load .. 3,33 -> 3,36
                        1] Dict .. 3,40 -> 3,42
                    .attr
                      'items'
                    .ctx Load
            .is_async
              0
    .type_comment
      None
""", r"""
Dict .. ROOT 0,0 -> 3,1
  .keys[2]
  0] None
  1] Constant 'PYLAUNCHER_DEBUG' .. 2,4 -> 2,22
  .values[2]
  0] DictComp .. 1,6 -> 1,78
    .key
      Call .. 1,7 -> 1,16
        .func
          Attribute .. 1,7 -> 1,14
            .value
              Name 'k' Load .. 1,7 -> 1,8
            .attr
              'upper'
            .ctx Load
    .value
      Name 'v' Load .. 1,18 -> 1,19
    .generators[1]
    0] comprehension .. 1,24 -> 1,77
      .target
        Tuple .. 1,24 -> 1,28
          .elts[2]
          0] Name 'k' Store .. 1,24 -> 1,25
          1] Name 'v' Store .. 1,27 -> 1,28
          .ctx Store
      .iter
        Call .. 1,32 -> 1,50
          .func
            Attribute .. 1,32 -> 1,48
              .value
                Attribute .. 1,32 -> 1,42
                  .value
                    Name 'os' Load .. 1,32 -> 1,34
                  .attr
                    'environ'
                  .ctx Load
              .attr
                'items'
              .ctx Load
      .ifs[1]
      0] Compare .. 1,54 -> 1,77
        .left
          Call .. 1,54 -> 1,63
            .func
              Attribute .. 1,54 -> 1,61
                .value
                  Name 'k' Load .. 1,54 -> 1,55
                .attr
                  'upper'
                .ctx Load
        .ops[1]
        0] NotIn
        .comparators[1]
        0] Name 'ignore' Load .. 1,71 -> 1,77
      .is_async
        0
  1] Constant '1' .. 2,24 -> 2,27
"""),

(r"""
(None, False, True, 12345, 123.45, 'abcde', 'абвгд', b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
""", 'body[0].value', 5, 7, r"""
(None, False, True, 12345, 123.45, b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
""", r"""
('abcde', 'абвгд')
""", r"""
Module .. ROOT 0,0 -> 2,67
  .body[1]
  0] Expr .. 0,0 -> 2,67
    .value
      Tuple .. 0,0 -> 2,67
        .elts[11]
        0] Constant None .. 0,1 -> 0,5
        1] Constant False .. 0,7 -> 0,12
        2] Constant True .. 0,14 -> 0,18
        3] Constant 12345 .. 0,20 -> 0,25
        4] Constant 123.45 .. 0,27 -> 0,33
        5] Constant b'abcde' .. 0,35 -> 0,43
        6] Call .. 1,12 -> 1,55
          .func
            Attribute .. 1,12 -> 1,29
              .value
                Name 'datetime' Load .. 1,12 -> 1,20
              .attr
                'datetime'
              .ctx Load
          .args[6]
          0] Constant 2004 .. 1,30 -> 1,34
          1] Constant 10 .. 1,36 -> 1,38
          2] Constant 26 .. 1,40 -> 1,42
          3] Constant 10 .. 1,44 -> 1,46
          4] Constant 33 .. 1,48 -> 1,50
          5] Constant 33 .. 1,52 -> 1,54
        7] Call .. 2,12 -> 2,31
          .func
            Name 'bytearray' Load .. 2,12 -> 2,21
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

(r"""
[a, b] = c
""", 'body[0].targets[0]', 1, 2, r"""
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
    .value
      Name 'c' Load .. 0,6 -> 0,7
    .type_comment
      None
""", r"""
List .. ROOT 0,0 -> 0,3
  .elts[1]
  0] Name 'b' Load .. 0,1 -> 0,2
  .ctx Load
"""),

(r"""
{
            'exception': exc,
            'future': fut,
            'message': ('GetQueuedCompletionStatus() returned an '
                        'unexpected event'),
            'status': ('err=%s transferred=%s key=%#x address=%#x'
                       % (err, transferred, key, address),),
                                                 'addr': address}
""", 'body[0].value', 1, 4, r"""
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
    .value
      Dict .. 0,0 -> 2,65
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
      .left
        Constant 'err=%s transferred=%s key=%#x address=%#x' .. 4,23 -> 4,66
      .op
        Mod
      .right
        Tuple .. 5,25 -> 5,57
          .elts[4]
          0] Name 'err' Load .. 5,26 -> 5,29
          1] Name 'transferred' Load .. 5,31 -> 5,42
          2] Name 'key' Load .. 5,44 -> 5,47
          3] Name 'address' Load .. 5,49 -> 5,56
          .ctx Load
    .ctx Load
"""),

(r"""
(1, (2), 3)
""", 'body[0].value', 1, 2, r"""
(1, 3)
""", r"""
((2),)
""", r"""
Module .. ROOT 0,0 -> 0,6
  .body[1]
  0] Expr .. 0,0 -> 0,6
    .value
      Tuple .. 0,0 -> 0,6
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

(r"""
@patch.dict({'a': 'b'})
class cls: pass
""", 'body[0].decorator_list[0].args[0]', 0, 1, r"""
@patch.dict({})
class cls: pass
""", r"""
{'a': 'b'}
""", r"""
Module .. ROOT 0,0 -> 1,15
  .body[1]
  0] ClassDef .. 1,0 -> 1,15
    .name
      'cls'
    .body[1]
    0] Pass .. 1,11 -> 1,15
    .decorator_list[1]
    0] Call .. 0,1 -> 0,15
      .func
        Attribute .. 0,1 -> 0,11
          .value
            Name 'patch' Load .. 0,1 -> 0,6
          .attr
            'dict'
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

(r"""
class cls:
    a, b = c
""", 'body[0].body[0].targets[0]', 0, 2, r"""
class cls:
    () = c
""", r"""
(a, b)
""", r"""
Module .. ROOT 0,0 -> 1,10
  .body[1]
  0] ClassDef .. 0,0 -> 1,10
    .name
      'cls'
    .body[1]
    0] Assign .. 1,4 -> 1,10
      .targets[1]
      0] Tuple .. 1,4 -> 1,6
        .ctx Store
      .value
        Name 'c' Load .. 1,9 -> 1,10
      .type_comment
        None
""", r"""
Tuple .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Name 'a' Load .. 0,1 -> 0,2
  1] Name 'b' Load .. 0,4 -> 0,5
  .ctx Load
"""),

(r"""
if 1:
    yy, tm, = tm, yy
""", 'body[0].body[0].targets[0]', 1, 2, r"""
if 1:
    yy, = tm, yy
""", r"""
(tm,)
""", r"""
Module .. ROOT 0,0 -> 1,16
  .body[1]
  0] If .. 0,0 -> 1,16
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Assign .. 1,4 -> 1,16
      .targets[1]
      0] Tuple .. 1,4 -> 1,7
        .elts[1]
        0] Name 'yy' Store .. 1,4 -> 1,6
        .ctx Store
      .value
        Tuple .. 1,10 -> 1,16
          .elts[2]
          0] Name 'tm' Load .. 1,10 -> 1,12
          1] Name 'yy' Load .. 1,14 -> 1,16
          .ctx Load
      .type_comment
        None
""", r"""
Tuple .. ROOT 0,0 -> 0,5
  .elts[1]
  0] Name 'tm' Load .. 0,1 -> 0,3
  .ctx Load
"""),

(r"""
{1, 2}
""", 'body[0].value', 0, 2, r"""
set()
""", r"""
{1, 2}
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Call .. 0,0 -> 0,5
        .func
          Name 'set' Load .. 0,0 -> 0,3
""", r"""
Set .. ROOT 0,0 -> 0,6
  .elts[2]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
"""),

(r"""
{1, 2}
""", 'body[0].value', 0, 0, r"""
{1, 2}
""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,6
  .body[1]
  0] Expr .. 0,0 -> 0,6
    .value
      Set .. 0,0 -> 0,6
        .elts[2]
        0] Constant 1 .. 0,1 -> 0,2
        1] Constant 2 .. 0,4 -> 0,5
""", r"""
Call .. ROOT 0,0 -> 0,5
  .func
    Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""
set()
""", 'body[0].value', 0, 0, r"""
set()
""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Call .. 0,0 -> 0,5
        .func
          Name 'set' Load .. 0,0 -> 0,3
""", r"""
Call .. ROOT 0,0 -> 0,5
  .func
    Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 0, 1, r"""
2, 3,
""", r"""
(1,)
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Tuple .. 0,0 -> 0,5
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

(r"""
1, 2, 3,
""", 'body[0].value', 1, 2, r"""
1, 3,
""", r"""
(2,)
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Tuple .. 0,0 -> 0,5
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

(r"""
1, 2, 3,
""", 'body[0].value', 2, 3, r"""
1, 2,
""", r"""
(3,)
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Tuple .. 0,0 -> 0,5
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

(r"""
1, 2, 3,
""", 'body[0].value', 0, 2, r"""
3,
""", r"""
(1, 2)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
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

(r"""
1, 2, 3,
""", 'body[0].value', 1, 3, r"""
1,
""", r"""
(2, 3)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
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

(r"""
1, 2, 3,
""", 'body[0].value', 0, 3, r"""
()
""", r"""
(1, 2, 3,)
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx Load
""", r"""
Tuple .. ROOT 0,0 -> 0,10
  .elts[3]
  0] Constant 1 .. 0,1 -> 0,2
  1] Constant 2 .. 0,4 -> 0,5
  2] Constant 3 .. 0,7 -> 0,8
  .ctx Load
"""),

]  # END OF GET_SLICE_SEQ_CUT_DATA

GET_SLICE_STMT_CUT_DATA = [
(r"""
if 1:
    i
    # pre
    j  # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""# pre
j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j ;
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j ; # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    # post
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value
        Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j ; \
  k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    \
  k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,3
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,2 -> 4,3
      .value
        Name 'k' Load .. 4,2 -> 4,3
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j ; \
\
  k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    \
\
  k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,3
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,2 -> 5,3
      .value
        Name 'k' Load .. 5,2 -> 5,3
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j \
    ; \
\
  k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    \
\
  k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,3
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,2 -> 5,3
      .value
        Name 'k' Load .. 5,2 -> 5,3
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j \
    ; \
  k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    \
  k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,3
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,2 -> 4,3
      .value
        Name 'k' Load .. 4,2 -> 4,3
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j \
    ; k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i
    # pre
    j
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i ; j  # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j  # post
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
  ; j  # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; \
  j  # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
  ; \
  j  # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j ; k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i ; k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,9
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 2,8 -> 2,9
      .value
        Name 'k' Load .. 2,8 -> 2,9
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j  # post
    k
""", 'body[0]', 1, 2, None, '', r"""
if 1:
    i  # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; j \
    # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i \
    # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value
        Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; \
  j \
    # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i \
    # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value
        Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
  ; \
  j \
    # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i \
    # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value
        Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; \
    j  # post
    if 2: pass
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    if 2: pass
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test
        Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    ; j  # post
    if 2: pass
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    if 2: pass
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test
        Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    ; \
    j  # post
    if 2: pass
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    if 2: pass
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test
        Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i ; \
    j
    if 2: pass
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    if 2: pass
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test
        Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    ; j
    if 1: pass
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    if 1: pass
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test
        Constant 1 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    ; \
    j
    if 2: pass
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    if 2: pass
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test
        Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j  # post
    k
""", 'body[0]', 1, 2, None, '', r"""
if 1:
    i
    # post
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value
        Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    \
    j
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i

    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value
        Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j \

    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    \

    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[1]
  0] If .. 1,0 -> 5,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 5,4 -> 5,5
      .value
        Name 'k' Load .. 5,4 -> 5,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j ;
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j ; \
  k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    \
  k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,3
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,2 -> 4,3
      .value
        Name 'k' Load .. 4,2 -> 4,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j \
  ;
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j \
  ; \
  k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    \
  k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,3
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,2 -> 4,3
      .value
        Name 'k' Load .. 4,2 -> 4,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    j  # post
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass
else: \
  i ; j
""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""
if 1: pass
else:
  j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,3
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 3,2 -> 3,3
      .value
        Name 'j' Load .. 3,2 -> 3,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass
else: \
  i ; \
    j
""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""
if 1: pass
else:
  \
    j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 4,4 -> 4,5
      .value
        Name 'j' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass
else: \
  i \
 ; \
    j
""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""
if 1: pass
else:
  \
    j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 4,4 -> 4,5
      .value
        Name 'j' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass
else: i ; j
""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""
if 1: pass
else: j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,7
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
    .orelse[1]
    0] Expr .. 2,6 -> 2,7
      .value
        Name 'j' Load .. 2,6 -> 2,7
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""if 1: pass
else: \
  i ; j""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""if 1: pass
else:
  j""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,3
  .body[1]
  0] If .. 0,0 -> 2,3
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Pass .. 0,6 -> 0,10
    .orelse[1]
    0] Expr .. 2,2 -> 2,3
      .value
        Name 'j' Load .. 2,2 -> 2,3
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""if 1: pass
else: \
  i ; \
    j""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""if 1: pass
else:
  \
    j""", r"""i""", r"""
Module .. ROOT 0,0 -> 3,5
  .body[1]
  0] If .. 0,0 -> 3,5
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Pass .. 0,6 -> 0,10
    .orelse[1]
    0] Expr .. 3,4 -> 3,5
      .value
        Name 'j' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""if 1: pass
else:
  i \
 ; \
    j""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""if 1: pass
else:
  \
    j""", r"""i""", r"""
Module .. ROOT 0,0 -> 3,5
  .body[1]
  0] If .. 0,0 -> 3,5
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Pass .. 0,6 -> 0,10
    .orelse[1]
    0] Expr .. 3,4 -> 3,5
      .value
        Name 'j' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""if 1: pass
else: i ; j""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""if 1: pass
else: j""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,7
  .body[1]
  0] If .. 0,0 -> 1,7
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Pass .. 0,6 -> 0,10
    .orelse[1]
    0] Expr .. 1,6 -> 1,7
      .value
        Name 'j' Load .. 1,6 -> 1,7
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    # pre
    j
    if 2: pass
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    if 2: pass
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test
        Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
    i \
    # pre
    j  # post
    if 2: pass
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    if 2: pass
""", r"""# pre
j  # post
""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,14
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] If .. 3,4 -> 3,14
      .test
        Constant 2 .. 3,7 -> 3,8
      .body[1]
      0] Pass .. 3,10 -> 3,14
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
if 1:
  \
  i
  if 2: pass
""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1:

  if 2: pass
""", r"""i""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,12
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] If .. 3,2 -> 3,12
      .test
        Constant 2 .. 3,5 -> 3,6
      .body[1]
      0] Pass .. 3,8 -> 3,12
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i
    \
    j
    k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i

    k
""", r"""j""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] If .. 1,0 -> 4,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 4,4 -> 4,5
      .value
        Name 'k' Load .. 4,4 -> 4,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'j' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: \
    i; j
""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1:
    j
""", r"""i""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 2,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'j' Load .. 2,4 -> 2,5
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1:
    i \
    # pre
    j ; k
""", 'body[0]', 1, 2, None, 'pre,post', r"""
if 1:
    i
    k
""", r"""# pre
j""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[1]
  0] If .. 1,0 -> 3,5
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 3,4 -> 3,5
      .value
        Name 'k' Load .. 3,4 -> 3,5
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'j' Load .. 1,0 -> 1,1
"""),

(r"""
class cls:
    i
    \




    def f(): pass
    j
""", 'body[0]', 1, 2, None, 'space1', r"""
class cls:
    i
    \



    j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,5
    .name
      'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 7,4 -> 7,5
      .value
        Name 'j' Load .. 7,4 -> 7,5
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name
      'f'
    .args
      arguments
        .vararg
          None
        .kwarg
          None
    .body[1]
    0] Pass .. 0,9 -> 0,13
    .returns
      None
    .type_comment
      None
"""),

(r"""
class cls:
    i
    \




    def f(): pass
    j
""", 'body[0]', 1, 2, None, 'pep8', r"""
class cls:
    i
    \



    j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 8,0
  .body[1]
  0] ClassDef .. 1,0 -> 7,5
    .name
      'cls'
    .body[2]
    0] Expr .. 2,4 -> 2,5
      .value
        Name 'i' Load .. 2,4 -> 2,5
    1] Expr .. 7,4 -> 7,5
      .value
        Name 'j' Load .. 7,4 -> 7,5
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name
      'f'
    .args
      arguments
        .vararg
          None
        .kwarg
          None
    .body[1]
    0] Pass .. 0,9 -> 0,13
    .returns
      None
    .type_comment
      None
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, 'pep8', r"""
i
\


j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 5,0 -> 5,1
    .value
      Name 'j' Load .. 5,0 -> 5,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name
      'f'
    .args
      arguments
        .vararg
          None
        .kwarg
          None
    .body[1]
    0] Pass .. 0,9 -> 0,13
    .returns
      None
    .type_comment
      None
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, 'pep8,space3', r"""
i
\

j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value
      Name 'j' Load .. 4,0 -> 4,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name
      'f'
    .args
      arguments
        .vararg
          None
        .kwarg
          None
    .body[1]
    0] Pass .. 0,9 -> 0,13
    .returns
      None
    .type_comment
      None
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, 'pep8,space4', r"""
i

j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 3,0 -> 3,1
    .value
      Name 'j' Load .. 3,0 -> 3,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name
      'f'
    .args
      arguments
        .vararg
          None
        .kwarg
          None
    .body[1]
    0] Pass .. 0,9 -> 0,13
    .returns
      None
    .type_comment
      None
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, 'pep8,space5', r"""
i
j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value
      Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name
      'f'
    .args
      arguments
        .vararg
          None
        .kwarg
          None
    .body[1]
    0] Pass .. 0,9 -> 0,13
    .returns
      None
    .type_comment
      None
"""),

(r"""
i
\




def f(): pass
j
""", '', 1, 2, None, 'pep8,space6', r"""
i
j
""", r"""def f(): pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value
      Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 0,13
  .body[1]
  0] FunctionDef .. 0,0 -> 0,13
    .name
      'f'
    .args
      arguments
        .vararg
          None
        .kwarg
          None
    .body[1]
    0] Pass .. 0,9 -> 0,13
    .returns
      None
    .type_comment
      None
"""),

(r"""
i
\



# pre
def f(): pass
j
""", '', 1, 2, None, 'pre,space1', r"""
i
\


j
""", r"""# pre
def f(): pass""", r"""
Module .. ROOT 0,0 -> 6,0
  .body[2]
  0] Expr .. 1,0 -> 1,1
    .value
      Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 5,0 -> 5,1
    .value
      Name 'j' Load .. 5,0 -> 5,1
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] FunctionDef .. 1,0 -> 1,13
    .name
      'f'
    .args
      arguments
        .vararg
          None
        .kwarg
          None
    .body[1]
    0] Pass .. 1,9 -> 1,13
    .returns
      None
    .type_comment
      None
"""),

(r"""
i
# pre
@deco1
@deco2
class cls:
  pass  # post
j
""", '', 1, 2, None, '', r"""
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
    .value
      Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 4,0 -> 4,1
    .value
      Name 'j' Load .. 4,0 -> 4,1
""", r"""
Module .. ROOT 0,0 -> 3,6
  .body[1]
  0] ClassDef .. 2,0 -> 3,6
    .name
      'cls'
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
""", '', 1, 2, None, 'pre,post', r"""
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
    .value
      Name 'i' Load .. 1,0 -> 1,1
  1] Expr .. 2,0 -> 2,1
    .value
      Name 'j' Load .. 2,0 -> 2,1
""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[1]
  0] ClassDef .. 3,0 -> 4,6
    .name
      'cls'
    .body[1]
    0] Pass .. 4,2 -> 4,6
    .decorator_list[2]
    0] Name 'deco1' Load .. 1,1 -> 1,6
    1] Call .. 2,1 -> 2,12
      .func
        Name 'deco2' Load .. 2,1 -> 2,6
      .args[2]
      0] Name 'a' Load .. 2,7 -> 2,8
      1] Name 'b' Load .. 2,10 -> 2,11
"""),

]  # END OF GET_SLICE_STMT_CUT_DATA

GET_SLICE_STMT_CUT_NOVERIFY_DATA = [
(r"""
if 1: i
""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1:
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1:""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,5
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i  # post
""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1:
""", r"""i  # post
""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 1,0
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i  # post""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1:""", r"""i  # post""", r"""
Module .. ROOT 0,0 -> 1,5
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i  # post
""", 'body[0]', 0, 1, None, '', r"""
if 1: # post
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i  # post""", 'body[0]', 0, 1, None, '', r"""
if 1: # post""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;
""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1:
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1:""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,5
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;  # post
""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1: # post
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;  # post""", 'body[0]', 0, 1, None, 'pre,post', r"""
if 1: # post""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;  # post
""", 'body[0]', 0, 1, None, '', r"""
if 1: # post
""", r"""i""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: i ;  # post""", 'body[0]', 0, 1, None, '', r"""
if 1: # post""", r"""i""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] If .. 1,0 -> 1,5
    .test
      Constant 1 .. 1,3 -> 1,4
""", r"""
Module .. ROOT 0,0 -> 0,1
  .body[1]
  0] Expr .. 0,0 -> 0,1
    .value
      Name 'i' Load .. 0,0 -> 0,1
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', '', r"""
if 1: pass

# pre
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 4,0 -> 4,1
    .value
      Name 'j' Load .. 4,0 -> 4,1
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
""", 'body[0]', 0, 1, 'orelse', 'pre', r"""
if 1: pass

j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 3,0 -> 3,1
    .value
      Name 'j' Load .. 3,0 -> 3,1
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
""", 'body[0]', 0, 1, 'orelse', 'pre,space', r"""
if 1: pass
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 2,0 -> 2,1
    .value
      Name 'j' Load .. 2,0 -> 2,1
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
""", 'body[0]', 0, 1, 'orelse', 'space', r"""
if 1: pass

# pre
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 5,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 4,0 -> 4,1
    .value
      Name 'j' Load .. 4,0 -> 4,1
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
""", 'body[0]', 0, 1, 'orelse', 'pre,space', r"""
if 1: pass
# post
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 3,0 -> 3,1
    .value
      Name 'j' Load .. 3,0 -> 3,1
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
""", 'body[0]', 0, 1, 'orelse', 'pre,post,space', r"""
if 1: pass
j
""", r"""pass  # post
""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] If .. 1,0 -> 1,10
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Pass .. 1,6 -> 1,10
  1] Expr .. 2,0 -> 2,1
    .value
      Name 'j' Load .. 2,0 -> 2,1
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
""", 'body[0]', 0, 1, 'finalbody', '', r"""
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
    .value
      Name 'j' Load .. 4,0 -> 4,1
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
""", 'body[0]', 0, 1, 'finalbody', 'pre', r"""
try: pass

j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 4,0
  .body[2]
  0] Try .. 1,0 -> 1,9
    .body[1]
    0] Pass .. 1,5 -> 1,9
  1] Expr .. 3,0 -> 3,1
    .value
      Name 'j' Load .. 3,0 -> 3,1
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
""", 'body[0]', 0, 1, 'finalbody', 'pre,space', r"""
try: pass
j
""", r"""pass""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[2]
  0] Try .. 1,0 -> 1,9
    .body[1]
    0] Pass .. 1,5 -> 1,9
  1] Expr .. 2,0 -> 2,1
    .value
      Name 'j' Load .. 2,0 -> 2,1
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
""", 'body[0]', 0, 1, 'finalbody', 'space', r"""
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
    .value
      Name 'j' Load .. 4,0 -> 4,1
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
""", 'body[0]', 0, 1, 'finalbody', 'pre,space', r"""
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
    .value
      Name 'j' Load .. 3,0 -> 3,1
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
""", 'body[0]', 0, 1, 'finalbody', 'pre,post,space', r"""
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
    .value
      Name 'j' Load .. 2,0 -> 2,1
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
""", 'body[0]', 0, 1, 'orelse', 'allpre', r"""
if 1: i

""", r"""# pre 1

# pre 2
j""", r"""
Module .. ROOT 0,0 -> 3,0
  .body[1]
  0] If .. 1,0 -> 1,7
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 1,6 -> 1,7
      .value
        Name 'i' Load .. 1,6 -> 1,7
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 3,0 -> 3,1
    .value
      Name 'j' Load .. 3,0 -> 3,1
"""),

(r"""
if 1: i

# pre-else 1

# pre-else 2
else:

  # pre 1

  # pre 2
  j
""", 'body[0]', 0, 1, 'orelse', 'allpre,space', r"""
if 1: i
""", r"""# pre 1

# pre 2
j""", r"""
Module .. ROOT 0,0 -> 2,0
  .body[1]
  0] If .. 1,0 -> 1,7
    .test
      Constant 1 .. 1,3 -> 1,4
    .body[1]
    0] Expr .. 1,6 -> 1,7
      .value
        Name 'i' Load .. 1,6 -> 1,7
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 3,0 -> 3,1
    .value
      Name 'j' Load .. 3,0 -> 3,1
"""),

(r"""
try:
    pass
finally: pass
""", 'body[0]', 0, 1, None, 'pre,post', r"""
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
""", 'body[0]', 0, 1, None, 'pre,post', r"""
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
""", 'body[0]', 0, 1, None, 'pre,post', r"""
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
    .value
      Constant 2 .. 1,0 -> 1,1
    .type_comment
      None
"""),

(r"""
try: pass  # post
finally: pass
""", 'body[0]', 0, 1, None, 'pre,post', r"""
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
""", 'body[0]', 0, 1, None, '', r"""
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
""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""
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
      .type
        None
      .name
        None
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
""", 'body[0]', 0, 1, 'orelse', 'pre,post', r"""
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
      .type
        None
      .name
        None
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
""", 'body[0]', 0, 1, 'handlers', 'pre,post', r"""
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
    .type
      None
    .name
      None
    .body[1]
    0] Pass .. 1,4 -> 1,8
"""),

(r"""
try: pass
except: pass
else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', 'pre,post', r"""
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
    .type
      None
    .name
      None
    .body[1]
    0] Pass .. 0,8 -> 0,12
"""),

(r"""
try: pass
except: pass  # post
else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', '', r"""
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
    .type
      None
    .name
      None
    .body[1]
    0] Pass .. 0,8 -> 0,12
"""),

(r"""
try: pass
except: pass  \

else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', '', r"""
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
    .type
      None
    .name
      None
    .body[1]
    0] Pass .. 0,8 -> 0,12
"""),

(r"""
try: pass
except:
    pass
else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, 'pre,post', r"""
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
      .type
        None
      .name
        None
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
""", 'body[0].handlers[0]', 0, 1, None, 'pre,post', r"""
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
      .type
        None
      .name
        None
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
""", 'body[0].handlers[0]', 0, 1, None, '', r"""
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
      .type
        None
      .name
        None
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
""", 'body[0].handlers[0]', 0, 1, None, '', r"""
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
      .type
        None
      .name
        None
    .orelse[1]
    0] Pass .. 4,6 -> 4,10
    .finalbody[1]
    0] Pass .. 5,9 -> 5,13
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Pass .. 0,0 -> 0,4
"""),

]  # END OF GET_SLICE_STMT_CUT_NOVERIFY_DATA

PUT_SLICE_SEQ_DATA = [
(r"""
{
    a: 1
}
""", 'body[0].value', 0, 1, r"""
{}
""", r"""
{}
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Dict .. 0,0 -> 0,2
"""),

(r"""
1, 2
""", 'body[0].value', 0, 2, r"""
(

   )
""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx Load
"""),

(r"""
if 1:
  {1, 2}
""", 'body[0].body[0].value', 0, 2, r"""
(

   )
""", r"""
if 1:
  set()
""", r"""
Module .. ROOT 0,0 -> 1,7
  .body[1]
  0] If .. 0,0 -> 1,7
    .test
      Constant 1 .. 0,3 -> 0,4
    .body[1]
    0] Expr .. 1,2 -> 1,7
      .value
        Call .. 1,2 -> 1,7
          .func
            Name 'set' Load .. 1,2 -> 1,5
"""),

(r"""
{
    a: 1
}
""", 'body[0].value', 0, 1, r"""
{
}
""", r"""
{
}
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 0,0 -> 1,1
    .value
      Dict .. 0,0 -> 1,1
"""),

(r"""
{a: 1}
""", 'body[0].value', 0, 1, r"""
{}
""", r"""
{}
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Dict .. 0,0 -> 0,2
"""),

(r"""
{a: 1}
""", 'body[0].value', 0, 1, r"""
{
}
""", r"""
{
}
""", r"""
Module .. ROOT 0,0 -> 1,1
  .body[1]
  0] Expr .. 0,0 -> 1,1
    .value
      Dict .. 0,0 -> 1,1
"""),

(r"""
(1, 2)
""", 'body[0].value', 1, 2, r"""
()
""", r"""
(1,)
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value
      Tuple .. 0,0 -> 0,4
        .elts[1]
        0] Constant 1 .. 0,1 -> 0,2
        .ctx Load
"""),

(r"""
1, 2
""", 'body[0].value', 1, 2, r"""
()
""", r"""
1,
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Constant 1 .. 0,0 -> 0,1
        .ctx Load
"""),

(r"""
1, 2
""", 'body[0].value', 0, 2, r"""
()
""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx Load
"""),

(r"""
(1, 2)
""", 'body[0].value', 1, 2, r"""
set()
""", r"""
(1,)
""", r"""
Module .. ROOT 0,0 -> 0,4
  .body[1]
  0] Expr .. 0,0 -> 0,4
    .value
      Tuple .. 0,0 -> 0,4
        .elts[1]
        0] Constant 1 .. 0,1 -> 0,2
        .ctx Load
"""),

(r"""
1, 2
""", 'body[0].value', 1, 2, r"""
set()
""", r"""
1,
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Constant 1 .. 0,0 -> 0,1
        .ctx Load
"""),

(r"""
1, 2
""", 'body[0].value', 0, 2, r"""
set()
""", r"""
()
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx Load
"""),

(r"""
[            # hello
    1, 2, 3
]
""", 'body[0].value', 0, 2, r"""
()
""", r"""
[            # hello
    3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[1]
        0] Constant 3 .. 1,4 -> 1,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 0, 1, r"""
[
    1]
""", r"""
[            # hello
    1, b, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 1, 2, r"""
[
    1]
""", r"""
[            # hello
    a,
    1, c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 1 .. 2,4 -> 2,5
        2] Name 'c' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 2, 3, r"""
[
    1]
""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value
      List .. 0,0 -> 2,6
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 0, 1, r"""
[2]
""", r"""
[            # hello
    2, b, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 2 .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 1, 2, r"""
[2]
""", r"""
[            # hello
    a, 2, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 2, 3, r"""
[2]
""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value
      List .. 0,0 -> 1,12
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 0, 1, r"""
[3
]
""", r"""
[            # hello
    3,
    b, c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Constant 3 .. 1,4 -> 1,5
        1] Name 'b' Load .. 2,4 -> 2,5
        2] Name 'c' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 1, 2, r"""
[3
]
""", r"""
[            # hello
    a, 3,
    c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        2] Name 'c' Load .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 2, 3, r"""
[3
]
""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 0, 1, r"""
[
    1]
""", r"""
[            # hello
    1, b, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 1, 2, r"""
[
    1]
""", r"""
[            # hello
    a,
    1, c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 1 .. 2,4 -> 2,5
        2] Name 'c' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 2, 3, r"""
[
    1]
""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value
      List .. 0,0 -> 2,6
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 0, 1, r"""
[2]
""", r"""
[            # hello
    2, b, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 2 .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 1, 2, r"""
[2]
""", r"""
[            # hello
    a, 2, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 2, 3, r"""
[2]
""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value
      List .. 0,0 -> 1,12
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 0, 1, r"""
[3
]
""", r"""
[            # hello
    3,
    b, c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Constant 3 .. 1,4 -> 1,5
        1] Name 'b' Load .. 2,4 -> 2,5
        2] Name 'c' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 1, 2, r"""
[3
]
""", r"""
[            # hello
    a, 3,
    c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        2] Name 'c' Load .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 2, 3, r"""
[3
]
""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 0, 1, r"""
[
    1,]
""", r"""
[            # hello
    1, b, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 1, 2, r"""
[
    1,]
""", r"""
[            # hello
    a,
    1, c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 1 .. 2,4 -> 2,5
        2] Name 'c' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 2, 3, r"""
[
    1,]
""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value
      List .. 0,0 -> 2,7
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 0, 1, r"""
[2,]
""", r"""
[            # hello
    2, b, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 2 .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 1, 2, r"""
[2,]
""", r"""
[            # hello
    a, 2, c
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 2, 3, r"""
[2,]
""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value
      List .. 0,0 -> 1,13
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 0, 1, r"""
[3,
]
""", r"""
[            # hello
    3,
    b, c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Constant 3 .. 1,4 -> 1,5
        1] Name 'b' Load .. 2,4 -> 2,5
        2] Name 'c' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 1, 2, r"""
[3,
]
""", r"""
[            # hello
    a, 3,
    c
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        2] Name 'c' Load .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c
]
""", 'body[0].value', 2, 3, r"""
[3,
]
""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 0, 1, r"""
[
    1,]
""", r"""
[            # hello
    1, b, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 1, 2, r"""
[
    1,]
""", r"""
[            # hello
    a,
    1, c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 1 .. 2,4 -> 2,5
        2] Name 'c' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 2, 3, r"""
[
    1,]
""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value
      List .. 0,0 -> 2,7
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 0, 1, r"""
[2,]
""", r"""
[            # hello
    2, b, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 2 .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 1, 2, r"""
[2,]
""", r"""
[            # hello
    a, 2, c,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        2] Name 'c' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 2, 3, r"""
[2,]
""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value
      List .. 0,0 -> 1,13
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 0, 1, r"""
[3,
]
""", r"""
[            # hello
    3,
    b, c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Constant 3 .. 1,4 -> 1,5
        1] Name 'b' Load .. 2,4 -> 2,5
        2] Name 'c' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 1, 2, r"""
[3,
]
""", r"""
[            # hello
    a, 3,
    c,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        2] Name 'c' Load .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c,
]
""", 'body[0].value', 2, 3, r"""
[3,
]
""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[
    1]
""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value
      List .. 0,0 -> 2,6
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[2]
""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value
      List .. 0,0 -> 1,12
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[3
]
""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[
    1,]
""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value
      List .. 0,0 -> 2,7
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[2,]
""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value
      List .. 0,0 -> 1,13
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[3,
]
""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[
    1  # comment
]
""", r"""
[            # hello
    a, b,
    1  # comment
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[2  # comment
]
""", r"""
[            # hello
    a, b, 2  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[3  # comment
]
""", r"""
[            # hello
    a, b, 3  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[
    1,  # comment
]
""", r"""
[            # hello
    a, b,
    1,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[2,  # comment
]
""", r"""
[            # hello
    a, b, 2,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b, c  # blah
]
""", 'body[0].value', 2, 3, r"""
[3,  # comment
]
""", r"""
[            # hello
    a, b, 3,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 0, 0, r"""
[
    1]
""", r"""
[            # hello
    1, a, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Name 'a' Load .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 1, 1, r"""
[
    1]
""", r"""
[            # hello
    a,
    1, b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 1 .. 2,4 -> 2,5
        2] Name 'b' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 2, 2, r"""
[
    1]
""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value
      List .. 0,0 -> 2,6
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 0, 0, r"""
[2]
""", r"""
[            # hello
    2, a, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 2 .. 1,4 -> 1,5
        1] Name 'a' Load .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 1, 1, r"""
[2]
""", r"""
[            # hello
    a, 2, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 2, 2, r"""
[2]
""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value
      List .. 0,0 -> 1,12
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 0, 0, r"""
[3
]
""", r"""
[            # hello
    3,
    a, b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Constant 3 .. 1,4 -> 1,5
        1] Name 'a' Load .. 2,4 -> 2,5
        2] Name 'b' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 1, 1, r"""
[3
]
""", r"""
[            # hello
    a, 3,
    b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        2] Name 'b' Load .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 2, 2, r"""
[3
]
""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 0, 0, r"""
[
    1]
""", r"""
[            # hello
    1, a, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Name 'a' Load .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 1, 1, r"""
[
    1]
""", r"""
[            # hello
    a,
    1, b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 1 .. 2,4 -> 2,5
        2] Name 'b' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 2, 2, r"""
[
    1]
""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value
      List .. 0,0 -> 2,6
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 0, 0, r"""
[2]
""", r"""
[            # hello
    2, a, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 2 .. 1,4 -> 1,5
        1] Name 'a' Load .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 1, 1, r"""
[2]
""", r"""
[            # hello
    a, 2, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 2, 2, r"""
[2]
""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value
      List .. 0,0 -> 1,12
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 0, 0, r"""
[3
]
""", r"""
[            # hello
    3,
    a, b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Constant 3 .. 1,4 -> 1,5
        1] Name 'a' Load .. 2,4 -> 2,5
        2] Name 'b' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 1, 1, r"""
[3
]
""", r"""
[            # hello
    a, 3,
    b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        2] Name 'b' Load .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 2, 2, r"""
[3
]
""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 0, 0, r"""
[
    1,]
""", r"""
[            # hello
    1, a, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Name 'a' Load .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 1, 1, r"""
[
    1,]
""", r"""
[            # hello
    a,
    1, b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 1 .. 2,4 -> 2,5
        2] Name 'b' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 2, 2, r"""
[
    1,]
""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value
      List .. 0,0 -> 2,7
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 0, 0, r"""
[2,]
""", r"""
[            # hello
    2, a, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 2 .. 1,4 -> 1,5
        1] Name 'a' Load .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 1, 1, r"""
[2,]
""", r"""
[            # hello
    a, 2, b
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 2, 2, r"""
[2,]
""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value
      List .. 0,0 -> 1,13
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 0, 0, r"""
[3,
]
""", r"""
[            # hello
    3,
    a, b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Constant 3 .. 1,4 -> 1,5
        1] Name 'a' Load .. 2,4 -> 2,5
        2] Name 'b' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 1, 1, r"""
[3,
]
""", r"""
[            # hello
    a, 3,
    b
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        2] Name 'b' Load .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b
]
""", 'body[0].value', 2, 2, r"""
[3,
]
""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 0, 0, r"""
[
    1,]
""", r"""
[            # hello
    1, a, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Name 'a' Load .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 1, 1, r"""
[
    1,]
""", r"""
[            # hello
    a,
    1, b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 1 .. 2,4 -> 2,5
        2] Name 'b' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 2, 2, r"""
[
    1,]
""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value
      List .. 0,0 -> 2,7
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 0, 0, r"""
[2,]
""", r"""
[            # hello
    2, a, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Constant 2 .. 1,4 -> 1,5
        1] Name 'a' Load .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 1, 1, r"""
[2,]
""", r"""
[            # hello
    a, 2, b,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 2 .. 1,7 -> 1,8
        2] Name 'b' Load .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 2, 2, r"""
[2,]
""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value
      List .. 0,0 -> 1,13
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 0, 0, r"""
[3,
]
""", r"""
[            # hello
    3,
    a, b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Constant 3 .. 1,4 -> 1,5
        1] Name 'a' Load .. 2,4 -> 2,5
        2] Name 'b' Load .. 2,7 -> 2,8
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 1, 1, r"""
[3,
]
""", r"""
[            # hello
    a, 3,
    b,
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Constant 3 .. 1,7 -> 1,8
        2] Name 'b' Load .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b,
]
""", 'body[0].value', 2, 2, r"""
[3,
]
""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[
    1]
""", r"""
[            # hello
    a, b,
    1]
""", r"""
Module .. ROOT 0,0 -> 2,6
  .body[1]
  0] Expr .. 0,0 -> 2,6
    .value
      List .. 0,0 -> 2,6
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[2]
""", r"""
[            # hello
    a, b, 2]
""", r"""
Module .. ROOT 0,0 -> 1,12
  .body[1]
  0] Expr .. 0,0 -> 1,12
    .value
      List .. 0,0 -> 1,12
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[3
]
""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[
    1,]
""", r"""
[            # hello
    a, b,
    1,]
""", r"""
Module .. ROOT 0,0 -> 2,7
  .body[1]
  0] Expr .. 0,0 -> 2,7
    .value
      List .. 0,0 -> 2,7
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[2,]
""", r"""
[            # hello
    a, b, 2,]
""", r"""
Module .. ROOT 0,0 -> 1,13
  .body[1]
  0] Expr .. 0,0 -> 1,13
    .value
      List .. 0,0 -> 1,13
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[3,
]
""", r"""
[            # hello
    a, b, 3,
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[
    1  # comment
]
""", r"""
[            # hello
    a, b,
    1  # comment
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[2  # comment
]
""", r"""
[            # hello
    a, b, 2  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[3  # comment
]
""", r"""
[            # hello
    a, b, 3  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[
    1,  # comment
]
""", r"""
[            # hello
    a, b,
    1,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      List .. 0,0 -> 3,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 1 .. 2,4 -> 2,5
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[2,  # comment
]
""", r"""
[            # hello
    a, b, 2,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 2 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
[            # hello
    a, b  # blah
]
""", 'body[0].value', 2, 2, r"""
[3,  # comment
]
""", r"""
[            # hello
    a, b, 3,  # comment
]
""", r"""
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[3]
        0] Name 'a' Load .. 1,4 -> 1,5
        1] Name 'b' Load .. 1,7 -> 1,8
        2] Constant 3 .. 1,10 -> 1,11
        .ctx Load
"""),

(r"""
{
    'message': ('An open stream was garbage collected prior to '
                'establishing network connection; '
                'call "stream.close()" explicitly.')
}
""", 'body[0].value', 1, 1, r"""
{i: j}
""", r"""
{
    'message': ('An open stream was garbage collected prior to '
                'establishing network connection; '
                'call "stream.close()" explicitly.'), i: j}
""", r"""
Module .. ROOT 0,0 -> 3,59
  .body[1]
  0] Expr .. 0,0 -> 3,59
    .value
      Dict .. 0,0 -> 3,59
        .keys[2]
        0] Constant 'message' .. 1,4 -> 1,13
        1] Name 'i' Load .. 3,54 -> 3,55
        .values[2]
        0] Constant 'An open stream was garbage collected prior to establishing network connection; call "stream.close()" explicitly.' .. 1,16 -> 3,51
        1] Name 'j' Load .. 3,57 -> 3,58
"""),

(r"""
{
    1: 2,
    5: 6
}
""", 'body[0].value', 1, 1, r"""
{3: ("4")}
""", r"""
{
    1: 2,
    3: ("4"), 5: 6
}
""", r"""
Module .. ROOT 0,0 -> 3,1
  .body[1]
  0] Expr .. 0,0 -> 3,1
    .value
      Dict .. 0,0 -> 3,1
        .keys[3]
        0] Constant 1 .. 1,4 -> 1,5
        1] Constant 3 .. 2,4 -> 2,5
        2] Constant 5 .. 2,14 -> 2,15
        .values[3]
        0] Constant 2 .. 1,7 -> 1,8
        1] Constant '4' .. 2,8 -> 2,11
        2] Constant 6 .. 2,17 -> 2,18
"""),

(r"""
[
    # order of patterns matters
    r'file, line (\\d+)',
    3,
]
""", 'body[0].value', 1, 1, r"""
(1, 2)
""", r"""
[
    # order of patterns matters
    r'file, line (\\d+)',
    1, 2, 3,
]
""", r"""
Module .. ROOT 0,0 -> 4,1
  .body[1]
  0] Expr .. 0,0 -> 4,1
    .value
      List .. 0,0 -> 4,1
        .elts[4]
        0] Constant 'file, line (\\\\d+)' .. 2,4 -> 2,24
        1] Constant 1 .. 3,4 -> 3,5
        2] Constant 2 .. 3,7 -> 3,8
        3] Constant 3 .. 3,10 -> 3,11
        .ctx Load
"""),

(r"""
(IndexError, KeyError, isinstance,)
""", 'body[0].value', 2, 3, r"""
()
""", r"""
(IndexError, KeyError,)
""", r"""
Module .. ROOT 0,0 -> 0,23
  .body[1]
  0] Expr .. 0,0 -> 0,23
    .value
      Tuple .. 0,0 -> 0,23
        .elts[2]
        0] Name 'IndexError' Load .. 0,1 -> 0,11
        1] Name 'KeyError' Load .. 0,13 -> 0,21
        .ctx Load
"""),

(r"""
[a, b] = c
""", 'body[0].targets[0]', 2, 2, r"""
(d,)
""", r"""
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
    .value
      Name 'c' Load .. 0,13 -> 0,14
    .type_comment
      None
"""),

(r"""
stat_list,
""", 'body[0].value', 0, 1, r"""
[ {-1: "stdname",
                   2: "cumulative"}[field[0]] ]
""", r"""
( {-1: "stdname",
                   2: "cumulative"}[field[0]], )
""", r"""
Module .. ROOT 0,0 -> 1,48
  .body[1]
  0] Expr .. 0,0 -> 1,48
    .value
      Tuple .. 0,0 -> 1,48
        .elts[1]
        0] Subscript .. 0,2 -> 1,45
          .value
            Dict .. 0,2 -> 1,35
              .keys[2]
              0] UnaryOp .. 0,3 -> 0,5
                .op
                  USub
                .operand
                  Constant 1 .. 0,4 -> 0,5
              1] Constant 2 .. 1,19 -> 1,20
              .values[2]
              0] Constant 'stdname' .. 0,7 -> 0,16
              1] Constant 'cumulative' .. 1,22 -> 1,34
          .slice
            Subscript .. 1,36 -> 1,44
              .value
                Name 'field' Load .. 1,36 -> 1,41
              .slice
                Constant 0 .. 1,42 -> 1,43
              .ctx Load
          .ctx Load
        .ctx Load
"""),

(r"""
for a in a, b:
    pass
""", 'body[0].iter', 1, 2, r"""
(
c,)
""", r"""
for a in (a,
c,):
    pass
""", r"""
Module .. ROOT 0,0 -> 2,8
  .body[1]
  0] For .. 0,0 -> 2,8
    .target
      Name 'a' Store .. 0,4 -> 0,5
    .iter
      Tuple .. 0,9 -> 1,3
        .elts[2]
        0] Name 'a' Load .. 0,10 -> 0,11
        1] Name 'c' Load .. 1,0 -> 1,1
        .ctx Load
    .body[1]
    0] Pass .. 2,4 -> 2,8
    .type_comment
      None
"""),

(r"""
result = filename, headers
""", 'body[0].value', 0, 0, r"""
(
c,)
""", r"""
result = (
c, filename, headers)
""", r"""
Module .. ROOT 0,0 -> 1,21
  .body[1]
  0] Assign .. 0,0 -> 1,21
    .targets[1]
    0] Name 'result' Store .. 0,0 -> 0,6
    .value
      Tuple .. 0,9 -> 1,21
        .elts[3]
        0] Name 'c' Load .. 1,0 -> 1,1
        1] Name 'filename' Load .. 1,3 -> 1,11
        2] Name 'headers' Load .. 1,13 -> 1,20
        .ctx Load
    .type_comment
      None
"""),

(r"""
return (user if delim else None), host
""", 'body[0].value', 0, 2, r"""
()
""", r"""
return ()
""", r"""
Module .. ROOT 0,0 -> 0,9
  .body[1]
  0] Return .. 0,0 -> 0,9
    .value
      Tuple .. 0,7 -> 0,9
        .ctx Load
"""),

(r"""
{1, 2}
""", 'body[0].value', 0, 2, r"""
()
""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Call .. 0,0 -> 0,5
        .func
          Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""
set()
""", 'body[0].value', 0, 0, r"""
()
""", r"""
set()
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Call .. 0,0 -> 0,5
        .func
          Name 'set' Load .. 0,0 -> 0,3
"""),

(r"""
set()
""", 'body[0].value', 0, 0, r"""
(1, 2)
""", r"""
{1, 2}
""", r"""
Module .. ROOT 0,0 -> 0,6
  .body[1]
  0] Expr .. 0,0 -> 0,6
    .value
      Set .. 0,0 -> 0,6
        .elts[2]
        0] Constant 1 .. 0,1 -> 0,2
        1] Constant 2 .. 0,4 -> 0,5
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 0, 0, r"""
a,
""", r"""
a, 1, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value
      Tuple .. 0,0 -> 0,11
        .elts[4]
        0] Name 'a' Load .. 0,0 -> 0,1
        1] Constant 1 .. 0,3 -> 0,4
        2] Constant 2 .. 0,6 -> 0,7
        3] Constant 3 .. 0,9 -> 0,10
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 1, 1, r"""
a,
""", r"""
1, a, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value
      Tuple .. 0,0 -> 0,11
        .elts[4]
        0] Constant 1 .. 0,0 -> 0,1
        1] Name 'a' Load .. 0,3 -> 0,4
        2] Constant 2 .. 0,6 -> 0,7
        3] Constant 3 .. 0,9 -> 0,10
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 2, 2, r"""
a,
""", r"""
1, 2, a, 3,
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value
      Tuple .. 0,0 -> 0,11
        .elts[4]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Name 'a' Load .. 0,6 -> 0,7
        3] Constant 3 .. 0,9 -> 0,10
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 3, 3, r"""
a,
""", r"""
1, 2, 3, a,
""", r"""
Module .. ROOT 0,0 -> 0,11
  .body[1]
  0] Expr .. 0,0 -> 0,11
    .value
      Tuple .. 0,0 -> 0,11
        .elts[4]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        3] Name 'a' Load .. 0,9 -> 0,10
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 0, 1, r"""
a,
""", r"""
a, 2, 3,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value
      Tuple .. 0,0 -> 0,8
        .elts[3]
        0] Name 'a' Load .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 1, 2, r"""
a,
""", r"""
1, a, 3,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value
      Tuple .. 0,0 -> 0,8
        .elts[3]
        0] Constant 1 .. 0,0 -> 0,1
        1] Name 'a' Load .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 2, 3, r"""
a,
""", r"""
1, 2, a,
""", r"""
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value
      Tuple .. 0,0 -> 0,8
        .elts[3]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Name 'a' Load .. 0,6 -> 0,7
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 0, 2, r"""
a,
""", r"""
a, 3,
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Tuple .. 0,0 -> 0,5
        .elts[2]
        0] Name 'a' Load .. 0,0 -> 0,1
        1] Constant 3 .. 0,3 -> 0,4
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 1, 3, r"""
a,
""", r"""
1, a,
""", r"""
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Tuple .. 0,0 -> 0,5
        .elts[2]
        0] Constant 1 .. 0,0 -> 0,1
        1] Name 'a' Load .. 0,3 -> 0,4
        .ctx Load
"""),

(r"""
1, 2, 3,
""", 'body[0].value', 0, 3, r"""
a,
""", r"""
a,
""", r"""
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Name 'a' Load .. 0,0 -> 0,1
        .ctx Load
"""),

]  # END OF PUT_SLICE_SEQ_DATA

PUT_SLICE_SEQ_DEL_DATA = [
("""
[            # hello
    1, 2, 3
]
""", 'body[0].value', 0, 2, """
[            # hello
    3
]
""", """
Module .. ROOT 0,0 -> 2,1
  .body[1]
  0] Expr .. 0,0 -> 2,1
    .value
      List .. 0,0 -> 2,1
        .elts[1]
        0] Constant 3 .. 1,4 -> 1,5
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 0, 0, """
1, 2, 3,
""", """
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value
      Tuple .. 0,0 -> 0,8
        .elts[3]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 1, 1, """
1, 2, 3,
""", """
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value
      Tuple .. 0,0 -> 0,8
        .elts[3]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 2, 2, """
1, 2, 3,
""", """
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value
      Tuple .. 0,0 -> 0,8
        .elts[3]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 3, 3, """
1, 2, 3,
""", """
Module .. ROOT 0,0 -> 0,8
  .body[1]
  0] Expr .. 0,0 -> 0,8
    .value
      Tuple .. 0,0 -> 0,8
        .elts[3]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        2] Constant 3 .. 0,6 -> 0,7
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 0, 1, """
2, 3,
""", """
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Tuple .. 0,0 -> 0,5
        .elts[2]
        0] Constant 2 .. 0,0 -> 0,1
        1] Constant 3 .. 0,3 -> 0,4
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 1, 2, """
1, 3,
""", """
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Tuple .. 0,0 -> 0,5
        .elts[2]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 3 .. 0,3 -> 0,4
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 2, 3, """
1, 2,
""", """
Module .. ROOT 0,0 -> 0,5
  .body[1]
  0] Expr .. 0,0 -> 0,5
    .value
      Tuple .. 0,0 -> 0,5
        .elts[2]
        0] Constant 1 .. 0,0 -> 0,1
        1] Constant 2 .. 0,3 -> 0,4
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 0, 2, """
3,
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Constant 3 .. 0,0 -> 0,1
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 1, 3, """
1,
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .elts[1]
        0] Constant 1 .. 0,0 -> 0,1
        .ctx Load
"""),

("""
1, 2, 3,
""", 'body[0].value', 0, 3, """
()
""", """
Module .. ROOT 0,0 -> 0,2
  .body[1]
  0] Expr .. 0,0 -> 0,2
    .value
      Tuple .. 0,0 -> 0,2
        .ctx Load
"""),

]  # END OF PUT_SLICE_SEQ_DEL_DATA


def read(fnm):
    with open(fnm) as f:
        return f.read()


def walktest(ast):
    for ast in walk(ast):
        ast.f.loc


def dumptest(self, fst, dump, src):
    self.assertEqual(dump.strip(), '\n'.join(fst.dump(linefunc=list)))
    self.assertEqual(src, fst.src)


class TestFST(unittest.TestCase):
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

    def test_loc(self):
        self.assertEqual((0, 6, 0, 9), parse('def f(i=1): pass').body[0].args.f.loc)  # arguments
        self.assertEqual((0, 5, 0, 8), parse('with f(): pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((0, 5, 0, 13), parse('with f() as f: pass').body[0].items[0].f.loc)  # withitem
        self.assertEqual((1, 2, 1, 24), parse('match a:\n  case 2 if a == 1: pass').body[0].cases[0].f.loc)  # match_case
        self.assertEqual((0, 7, 0, 25), parse('[i for i in range(5) if i]').body[0].value.generators[0].f.loc)  # comprehension
        self.assertEqual((0, 7, 0, 25), parse('(i for i in range(5) if i)').body[0].value.generators[0].f.loc)  # comprehension

        self.assertEqual((0, 5, 0, 12), parse('with ( f() ): pass').body[0].items[0].f.loc)  # withitem w/ parens
        self.assertEqual((0, 5, 0, 21), parse('with ( f() ) as ( f ): pass').body[0].items[0].f.loc)  # withitem w/ parens
        self.assertEqual((1, 2, 1, 28), parse('match a:\n  case ( 2 ) if a == 1: pass').body[0].cases[0].f.loc)  # match_case w/ parens
        self.assertEqual((0, 7, 0, 33), parse('[i for ( i ) in range(5) if ( i ) ]').body[0].value.generators[0].f.loc)  # comprehension w/ parens
        self.assertEqual((0, 7, 0, 33), parse('(i for ( i ) in range(5) if ( i ) )').body[0].value.generators[0].f.loc)  # comprehension w/ parens

        self.assertEqual('( f() ) as ( f )', parse('with ( f() ) as ( f ): pass').body[0].items[0].f.src)
        self.assertEqual('( f() ) as ( f )', parse('with ( f() ) as ( f ), ( g() ) as ( g ): pass').body[0].items[0].f.src)
        self.assertEqual('( g() ) as ( g )', parse('with ( f() ) as ( f ), ( g() ) as ( g ): pass').body[0].items[1].f.src)
        self.assertEqual('case ( 2 ) if a == 1: pass', parse('match a:\n  case ( 2 ) if a == 1: pass').body[0].cases[0].f.src)
        self.assertEqual('( i ) in range(5) if ( i )', parse('[ ( i ) for ( i ) in range(5) if ( i ) ]').body[0].value.generators[0].f.src)
        self.assertEqual('( i ) in range(5) if ( i )', parse('( ( i ) for ( i ) in range(5) if ( i ) )').body[0].value.generators[0].f.src)
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
        self.assertEqual('( i ) in range(5) if ( i )', parse('[ ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) ]').body[0].value.generators[0].f.src)
        self.assertEqual('( i ) in range(5) if ( i )', parse('( ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) )').body[0].value.generators[0].f.src)
        self.assertEqual('( j ) in range(6) if ( j )', parse('[ ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) ]').body[0].value.generators[1].f.src)
        self.assertEqual('( j ) in range(6) if ( j )', parse('( ( i ) for ( i ) in range(5) if ( i ) for ( j ) in range(6) if ( j ) )').body[0].value.generators[1].f.src)

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
        p = f.pars(False)
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 0, 4, 1))
        p = f.pars(None)
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 0, 4, 1))
        p = f.pars(True)
        self.assertIsInstance(p, FST)
        self.assertEqual(p.loc, (0, 0, 4, 1))

        f = parse('''
( (
 (
   a
  ) )
,)
        '''.strip()).body[0].value.elts[0].f
        p = f.pars(False)
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 2, 3, 5))
        p = f.pars(None)
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (0, 2, 3, 5))
        p = f.pars(True)
        self.assertIsInstance(p, FST)
        self.assertEqual(p.loc, (0, 2, 3, 5))

        f = parse('''
(

   a

,)
        '''.strip()).body[0].value.elts[0].f
        p = f.pars(False)
        self.assertIsInstance(p, fstloc)
        self.assertEqual(p, (2, 3, 2, 4))
        p = f.pars(None)
        self.assertIsInstance(p, FST)
        self.assertEqual(p.loc, (2, 3, 2, 4))
        p = f.pars(True)
        self.assertIsInstance(p, FST)
        self.assertEqual(p.loc, (2, 3, 2, 4))

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

    def test_is_tuple_parenthesized(self):
        self.assertTrue(parse('(1, 2)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(1,)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1),)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1,))').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1,),)').body[0].value.f.is_tuple_parenthesized())

        self.assertTrue(parse('((a), b)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(a, (b))').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((a), (b))').body[0].value.f.is_tuple_parenthesized())

        self.assertTrue(parse('(\n1,2)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(1\n,2)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(1,\n2)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(1,2\n)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(1\n,)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(1,\n)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(\n(1),)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((\n1),)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1\n),)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1)\n,)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1),\n)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(\n(1,))').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((\n1,))').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1\n,))').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1,\n))').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1,)\n)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(\n(1,),)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((\n1,),)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1\n,),)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1,\n),)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1,)\n,)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((1,),\n)').body[0].value.f.is_tuple_parenthesized())

        self.assertTrue(parse('((a), b)').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('(a, (b))').body[0].value.f.is_tuple_parenthesized())
        self.assertTrue(parse('((a), (b))').body[0].value.f.is_tuple_parenthesized())

        self.assertFalse(parse('(1,),').body[0].value.f.is_tuple_parenthesized())
        self.assertFalse(parse('(1),').body[0].value.f.is_tuple_parenthesized())
        self.assertFalse(parse('((1)),').body[0].value.f.is_tuple_parenthesized())
        self.assertFalse(parse('((1,),),').body[0].value.f.is_tuple_parenthesized())

        self.assertFalse(parse('(a), b').body[0].value.f.is_tuple_parenthesized())
        self.assertFalse(parse('((a)), b').body[0].value.f.is_tuple_parenthesized())
        self.assertFalse(parse('a, (b)').body[0].value.f.is_tuple_parenthesized())
        self.assertFalse(parse('a, ((b))').body[0].value.f.is_tuple_parenthesized())
        self.assertFalse(parse('(a), (b)').body[0].value.f.is_tuple_parenthesized())
        self.assertFalse(parse('((a)), ((b))').body[0].value.f.is_tuple_parenthesized())

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
        ast.f.offset(1, 5, 0, 1, inc=True)
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
        ast.f.offset(1, 5, 1, -1, inc=True)
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

    def test_put_lines(self):
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

    def test_fix(self):
        f = FST.fromsrc('if 1:\n a\nelif 2:\n b')
        fc = f.a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual(fc.lines[0], 'elif 2:')
        fc.fix(inplace=True)
        self.assertEqual(fc.lines[0], 'if 2:')
        fc.verify(raise_=True)

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual(fc.src, '1 +\n2')
        fc.fix(inplace=True)
        self.assertEqual(fc.src, '(1 +\n2)')
        fc.verify(raise_=True)

        f = FST.fromsrc('i = 1')
        self.assertIs(f.a.body[0].targets[0].ctx.__class__, Store)
        fc = f.a.body[0].targets[0].f.copy(fix=False)
        self.assertIs(fc.a.ctx.__class__, Store)
        fc.fix(inplace=True)
        self.assertIs(fc.a.ctx.__class__, Load)
        fc.verify(raise_=True)

        f = FST.fromsrc('if 1: pass\nelif 2: pass').a.body[0].orelse[0].f.copy(fix=False)
        self.assertEqual('elif 2: pass', f.src)

        g = f.fix(inplace=False)
        self.assertIsNot(g, f)
        self.assertEqual('if 2: pass', g.src)
        self.assertEqual('elif 2: pass', f.src)

        g = f.fix(inplace=True)
        self.assertIs(g, f)
        self.assertEqual('if 2: pass', g.src)
        self.assertEqual('if 2: pass', f.src)

        f = FST.fromsrc('i, j = 1, 2').a.body[0].targets[0].f.copy(fix=False)
        self.assertEqual('i, j', f.src)
        self.assertIsNot(f, f.fix(inplace=False))

        g = f.fix(inplace=False)
        self.assertFalse(compare_asts(f.a, g.a))
        self.assertIs(g, g.fix(inplace=False))

        f = FST.fromsrc('match w := x,:\n case 0: pass').a.body[0].subject.f.copy(fix=False)
        self.assertEqual('w := x,', f.src)

        g = f.fix(inplace=False)
        self.assertEqual('(w := x,)', g.src)
        self.assertTrue(compare_asts(f.a, g.a, locs=False))
        self.assertFalse(compare_asts(f.a, g.a, locs=True))
        self.assertIs(g, g.fix(inplace=False))

        f = FST.fromsrc('(1 +\n2)')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('1 +\n2', fc.src)
        fd = fc.fix(inplace=False)
        self.assertEqual('(1 +\n2)', fd.src)
        fc.fix(inplace=True)
        self.assertEqual('(1 +\n2)', fc.src)

        f = FST.fromsrc('yield a1, a2')
        fc = f.a.body[0].value.f.copy(fix=False)
        self.assertEqual('yield a1, a2', fc.src)
        fd = fc.fix(inplace=False)
        self.assertEqual('(yield a1, a2)', fd.src)
        fc.fix(inplace=True)
        self.assertEqual('(yield a1, a2)', fc.src)

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
        fd = fc.fix(inplace=False)
        self.assertEqual("""
("Bad value substitution: option {!r} in section {!r} contains "
               "an interpolation key {!r} which is not a valid option name. "
               "Raw value: {!r}".format)""".strip(), fd.src)
        fc.fix(inplace=True)
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
        fd = fc.fix(inplace=False)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fd.src)
        fc.fix(inplace=True)
        self.assertEqual("""
((is_seq := isinstance(a, (Tuple, List))) or (is_starred := isinstance(a, Starred)) or
            isinstance(a, (Name, Subscript, Attribute)))""".strip(), fc.src)

        if sys.version_info[:2] >= (3, 12):
            fc = FST.fromsrc('tuple[*tuple[int, ...]]').a.body[0].value.slice.f.copy(fix=False)
            self.assertEqual('*tuple[int, ...]', fc.src)
            fd = fc.fix(inplace=False)
            self.assertEqual('(*tuple[int, ...],)', fd.src)
            fc.fix(inplace=True)
            self.assertEqual('(*tuple[int, ...],)', fc.src)

    def test_pars(self):
        for src, elt, slice_copy, slice_dump in PARS_DATA:
            src   = src.strip()
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.pars()
            ssrc  = s.src
            sdump = s.dump(linefunc=list, compact=True)

            try:
                self.assertEqual(ssrc, slice_copy.strip())
                self.assertEqual(sdump, slice_dump.strip().split('\n'))
                self.assertEqual(s.src, s.pars().src)

            except Exception:
                print(elt)
                print('---')
                print(src)
                print('...')
                print(slice_copy)

                raise

    def test_comms(self):
        f = parse('''
# hello

# world
pass  # postcomment
# next line comment
pass
        '''.strip()).body[0].f

        g = f.comms()
        self.assertIsInstance(g, FST)
        self.assertEqual('# world\npass  # postcomment\n', g.src)
        g = f.comms(True, 'pre')
        self.assertIsInstance(g, FST)
        self.assertEqual('# world\npass', g.src)
        g = f.comms(True, 'allpre')
        self.assertIsInstance(g, FST)
        self.assertEqual('# hello\n\n# world\npass', g.src)
        g = f.comms(True, 'post')
        self.assertIsInstance(g, FST)
        self.assertEqual('pass  # postcomment\n', g.src)
        g = f.comms(True, False)
        self.assertIs(g, f)

        g = f.comms(None)
        self.assertIsInstance(g, fstloc)
        self.assertEqual((2, 0, 4, 0), g)
        g = f.comms(None, 'pre')
        self.assertIsInstance(g, fstloc)
        self.assertEqual((2, 0, 3, 4), g)
        g = f.comms(None, 'allpre')
        self.assertIsInstance(g, fstloc)
        self.assertEqual((0, 0, 3, 4), g)
        g = f.comms(None, 'post')
        self.assertIsInstance(g, fstloc)
        self.assertEqual((3, 0, 4, 0), g)
        g = f.comms(None, False)
        self.assertIs(g, f)

        g = f.comms(False)
        self.assertIsInstance(g, fstloc)
        self.assertEqual((2, 0, 4, 0), g)
        g = f.comms(False, 'pre')
        self.assertIsInstance(g, fstloc)
        self.assertEqual((2, 0, 3, 4), g)
        g = f.comms(False, 'post')
        self.assertIsInstance(g, fstloc)
        self.assertEqual((3, 0, 4, 0), g)
        g = f.comms(False, False)
        self.assertIs(g, f.loc)

        lines = '''  # hello

  # world
  pass  # whatever
# whenever
            '''.split('\n')

        self.assertEqual((2, 0), FST.src_edit.pre_comments(lines, 0, 0, 3, 2))
        self.assertEqual((4, 0), FST.src_edit.post_comments(lines, 3, 6, 5, 0))
        self.assertEqual(None, FST.src_edit.pre_comments(lines, 0, 0, 2, 2))
        self.assertEqual(None, FST.src_edit.post_comments(lines, 2, 9, 5, 0))
        self.assertEqual((0, 0), FST.src_edit.pre_comments(lines, 0, 0, 2, 2, {'allpre'}))

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
        self.assertIs(f.fix(inplace=False), f)
        # self.assertRaises(SyntaxError, f.fix)
        # self.assertIs(None, f.fix(raise_=False))

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
        self.assertEqual('i', a.body[0].f.copy(fmt='').src)
        self.assertEqual('# pre\ni', a.body[0].f.copy(fmt='pre').src)
        self.assertEqual('# pre\ni # post\n', a.body[0].f.copy(fmt='pre,post').src)
        self.assertEqual('# prepre\n\n# pre\ni', a.body[0].f.copy(fmt='allpre').src)

        a = parse('( i )')
        self.assertEqual('i', a.body[0].value.f.copy(fmt='').src)
        self.assertEqual('( i )', a.body[0].value.f.copy(fmt='pars').src)

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

    # def test_cut_bulk(self):
    #     for fnm in PYFNMS:
    #         ast  = FST.fromsrc(read(fnm)).a
    #         asts = [a for a in walk(ast)
    #                 if isinstance(a, fst.STATEMENTISH) or
    #                    isinstance(a.f.parent, (Tuple, List, Set))
    #         ]

    #         for a in asts[::-1]:
    #             a.f.cut()

    def test_copy(self):
        for src, elt, slice_copy, slice_dump in COPY_DATA:
            src   = src.strip()
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.copy(fix=True)
            ssrc  = s.src
            sdump = s.dump(linefunc=list, compact=True)

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
        self.assertEqual('i', a.body[0].f.cut(fmt='').src)
        self.assertEqual('# prepre\n\n# pre\n# post\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# pre\ni', a.body[0].f.cut(fmt='pre').src)
        self.assertEqual('# prepre\n\n# post\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# pre\ni # post\n', a.body[0].f.cut(fmt='pre,post').src)
        self.assertEqual('# prepre\n\n# postpost', a.f.src)

        a = parse('''
# prepre

# pre
i # post
# postpost
            '''.strip())
        self.assertEqual('# prepre\n\n# pre\ni', a.body[0].f.cut(fmt='allpre').src)
        self.assertEqual('# post\n# postpost', a.f.src)

        a = parse('( ( i ), )')
        f = a.body[0].value.elts[0].f.cut(fmt='')
        self.assertEqual('()', a.f.src)
        self.assertEqual('i', f.src)

        a = parse('( ( i ), )')
        f = a.body[0].value.elts[0].f.cut(fmt='pars')
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
        a.body[0].f.put_slice('i')
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
        a.body[0].body[0].f.put_slice('i')
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

    def test_insert_into_empty_block_2(self):
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

        fst.body[1].cases[0].cut()
        fst.body[1].put_slice('pass')

        points = [
            (fst.body[0].cases[0], 'body'),
            (fst.body[1], 'cases'),
            (fst.body[2], 'body'),
            (fst.body[2], 'orelse'),
            (fst.body[3], 'body'),
            (fst.body[3], 'handlers'),
            (fst.body[3], 'orelse'),
            (fst.body[3], 'finalbody'),
            (fst.body[4], 'body'),
            (fst.body[4], 'orelse'),
            (fst.body[5], 'body'),
            (fst.body[5], 'orelse'),
            (fst.body[6], 'body'),
            (fst.body[6], 'orelse'),
            (fst.body[7], 'body'),
            (fst.body[8], 'body'),
            (fst.body[9], 'body'),
            (fst.body[10], 'body'),
            (fst.body[11], 'body'),
            (fst.body[12].body[0], 'body'),
            (fst.body[12].body[0], 'handlers'),
            (fst.body[12].body[0], 'orelse'),
            (fst.body[12].body[0], 'finalbody'),
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

            f.put_slice(bs.pop(), 0, 0, field=field)

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

                f.put_slice(bs.pop(), 0, 0, field=field)

    def test_get_slice_seq_copy(self):
        for src, elt, start, stop, _, slice_copy, _, slice_dump in GET_SLICE_SEQ_CUT_DATA:
            src   = src.strip()
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.get_slice(start, stop, cut=False)
            tsrc  = t.f.src
            ssrc  = s.src
            sdump = s.dump(linefunc=list, compact=True)

            try:
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
        for src, elt, start, stop, src_cut, slice_cut, src_dump, slice_dump in GET_SLICE_SEQ_CUT_DATA:
            src   = src.strip()
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.get_slice(start, stop, cut=True)
            tsrc  = t.f.src
            ssrc  = s.src
            tdump = t.f.dump(linefunc=list, compact=True)
            sdump = s.dump(linefunc=list, compact=True)

            try:
                self.assertEqual(tsrc, src_cut.strip())
                self.assertEqual(ssrc, slice_cut.strip())
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

    def test_get_slice_stmt_copy(self):
        for name in ('GET_SLICE_STMT_CUT_DATA', 'GET_SLICE_STMT_CUT_NOVERIFY_DATA'):
            verify = 'NOVERIFY' not in name

            for src, elt, start, stop, field, fmt, _, slice_cut, _, slice_dump in globals()[name]:
                t     = parse(src)
                f     = (eval(f't.{elt}', {'t': t}) if elt else t).f
                s     = f.get_slice(start, stop, field, cut=False, fmt=fmt)
                tsrc  = t.f.src
                ssrc  = s.src
                sdump = s.dump(linefunc=list, compact=True)

                if verify:
                    t.f.verify(raise_=True)
                    s.verify(raise_=True)

                try:
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
        for name in ('GET_SLICE_STMT_CUT_DATA', 'GET_SLICE_STMT_CUT_NOVERIFY_DATA'):
            verify = 'NOVERIFY' not in name

            for src, elt, start, stop, field, fmt, src_cut, slice_cut, src_dump, slice_dump in globals()[name]:
                t     = parse(src)
                f     = (eval(f't.{elt}', {'t': t}) if elt else t).f
                s     = f.get_slice(start, stop, field, cut=True, fmt=fmt)
                tsrc  = t.f.src
                ssrc  = s.src
                tdump = t.f.dump(linefunc=list, compact=True)
                sdump = s.dump(linefunc=list, compact=True)

                if verify:
                    t.f.verify(raise_=True)
                    s.verify(raise_=True)

                try:
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

    def test_put_slice(self):
        for dst, elt, start, stop, src, put_src, put_dump in PUT_SLICE_SEQ_DATA:
            dst = dst.strip()
            src = src.strip()
            t   = parse(dst)
            f   = eval(f't.{elt}', {'t': t}).f

            f.put_slice(src, start, stop)

            tdst  = t.f.src
            tdump = t.f.dump(linefunc=list, compact=True)

            try:
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

    def test_put_slice_del(self):
        for dst, elt, start, stop, put_src, put_dump in PUT_SLICE_SEQ_DEL_DATA:
            dst = dst.strip()
            t   = parse(dst)
            f   = eval(f't.{elt}', {'t': t}).f

            f.put_slice(None, start, stop)

            tdst  = t.f.src
            tdump = t.f.dump(linefunc=list, compact=True)

            try:
                self.assertEqual(tdst, put_src.strip())
                self.assertEqual(tdump, put_dump.strip().split('\n'))

            except Exception:
                print(elt, start, stop)
                print('---')
                print(dst)

                raise

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


def regen_pars_data():
    newlines = []

    for src, elt, *_ in PARS_DATA:
        src   = src.strip()
        t     = parse(src)
        f     = eval(f't.{elt}', {'t': t}).f
        s     = f.pars()
        ssrc  = s.src
        sdump = s.dump(linefunc=list, compact=True)

        assert not ssrc.startswith('\n') or ssrc.endswith('\n')

        newlines.append('(r"""')
        newlines.extend(f'''{src}\n""", {elt!r}, r"""\n{ssrc}\n""", r"""'''.split('\n'))
        newlines.extend(sdump)
        newlines.append('"""),\n')

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
        sdump = s.dump(linefunc=list, compact=True)

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


def regen_get_slice_seq_cut_data():
    newlines = []

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    for name in ('GET_SLICE_SEQ_CUT_DATA',):
        for src, elt, start, stop, *_ in globals()[name]:
            src   = src.strip()
            t     = parse(src)
            f     = eval(f't.{elt}', {'t': t}).f
            s     = f.get_slice(start, stop, cut=True)
            tsrc  = t.f.src
            ssrc  = s.src
            tdump = t.f.dump(linefunc=list, compact=True)
            sdump = s.dump(linefunc=list, compact=True)

            assert not tsrc.startswith('\n') or tsrc.endswith('\n')
            assert not ssrc.startswith('\n') or ssrc.endswith('\n')

            t.f.verify(raise_=True)
            s.verify(raise_=True)

            newlines.append('(r"""')
            newlines.extend(f'''{src}\n""", {elt!r}, {start}, {stop}, r"""\n{tsrc}\n""", r"""\n{ssrc}\n""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('""", r"""')
            newlines.extend(sdump)
            newlines.append('"""),\n')

        start = lines.index(f'{name} = [')
        stop  = lines.index(f']  # END OF {name}')

        lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_get_slice_stmt_cut_data():
    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    for name in ('GET_SLICE_STMT_CUT_DATA', 'GET_SLICE_STMT_CUT_NOVERIFY_DATA'):
        verify   = 'NOVERIFY' not in name
        newlines = []

        for src, elt, start, stop, field, fmt, *_ in globals()[name]:
            t     = parse(src)
            f     = (eval(f't.{elt}', {'t': t}) if elt else t).f
            s     = f.get_slice(start, stop, field, cut=True, fmt=fmt)
            tsrc  = t.f.src
            ssrc  = s.src
            tdump = t.f.dump(linefunc=list, compact=True)
            sdump = s.dump(linefunc=list, compact=True)

            if verify:
                t.f.verify(raise_=True)
                s.verify(raise_=True)

            newlines.extend(f'''(r"""{src}""", {elt!r}, {start}, {stop}, {field!r}, {fmt!r}, r"""{tsrc}""", r"""{ssrc}""", r"""'''.split('\n'))
            newlines.extend(tdump)
            newlines.append('""", r"""')
            newlines.extend(sdump)
            newlines.append('"""),\n')

        start = lines.index(f'{name} = [')
        stop  = lines.index(f']  # END OF {name}')

        lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_seq_data():
    newlines = []

    for dst, elt, start, stop, src, put_src, put_dump in PUT_SLICE_SEQ_DATA:
        dst = dst.strip()
        src = src.strip()
        t   = parse(dst)
        f   = eval(f't.{elt}', {'t': t}).f

        f.put_slice(src, start, stop)

        tdst  = t.f.src
        tdump = t.f.dump(linefunc=list, compact=True)

        assert not tdst.startswith('\n') or tdst.endswith('\n')

        t.f.verify(raise_=True)

        newlines.append('(r"""')
        newlines.extend(f'''{dst}\n""", {elt!r}, {start}, {stop}, r"""\n{src}\n""", r"""\n{tdst}\n""", r"""'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_SEQ_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_SEQ_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


def regen_put_slice_seq_del_data():
    newlines = []

    for dst, elt, start, stop, put_src, put_dump in PUT_SLICE_SEQ_DEL_DATA:
        dst = dst.strip()
        t   = parse(dst)
        f   = eval(f't.{elt}', {'t': t}).f

        f.put_slice(None, start, stop)

        tdst  = t.f.src
        tdump = t.f.dump(linefunc=list, compact=True)

        assert not tdst.startswith('\n') or tdst.endswith('\n')

        t.f.verify(raise_=True)

        newlines.append('("""')
        newlines.extend(f'''{dst}\n""", {elt!r}, {start}, {stop}, """\n{tdst}\n""", """'''.split('\n'))
        newlines.extend(tdump)
        newlines.append('"""),\n')

    with open(sys.argv[0]) as f:
        lines = f.read().split('\n')

    start = lines.index('PUT_SLICE_SEQ_DEL_DATA = [')
    stop  = lines.index(']  # END OF PUT_SLICE_SEQ_DEL_DATA')

    lines[start + 1 : stop] = newlines

    with open(sys.argv[0], 'w') as f:
        lines = f.write('\n'.join(lines))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(prog='test_fst.py')

    parser.add_argument('--regen-pars', default=False, action='store_true', help="regenerate parentheses test data")
    parser.add_argument('--regen-copy', default=False, action='store_true', help="regenerate copy test data")
    parser.add_argument('--regen-get-slice-seq-cut', default=False, action='store_true', help="regenerate get slice sequence test data")
    parser.add_argument('--regen-get-slice-stmt-cut', default=False, action='store_true', help="regenerate get slice statement test data")
    parser.add_argument('--regen-put-slice-seq', default=False, action='store_true', help="regenerate put slice sequence test data")
    parser.add_argument('--regen-put-slice-seq-del', default=False, action='store_true', help="regenerate put slice del sequence test data")

    args = parser.parse_args()

    if args.regen_pars:
        print('Regenerating parentheses test data...')
        regen_pars_data()

    if args.regen_copy:
        print('Regenerating copy test data...')
        regen_copy_data()

    if args.regen_get_slice_seq_cut:
        print('Regenerating get slice sequence cut test data...')
        regen_get_slice_seq_cut_data()

    if args.regen_get_slice_stmt_cut:
        print('Regenerating get slice statement cut test data...')
        regen_get_slice_stmt_cut_data()

    if args.regen_put_slice_seq:
        print('Regenerating put slice sequence test data...')
        regen_put_slice_seq_data()

    if args.regen_put_slice_seq_del:
        print('Regenerating put slice del sequence test data...')
        regen_put_slice_seq_del_data()

    # if (not args.regen_pars and not args.regen_copy and
    #     not args.regen_get_slice_seq_cut and not args.regen_get_slice_stmt_cut and
    #     not args.regen_put_slice and
    #     not args.regen_put_slice_del
    # ):
    if (all(not getattr(args, n) for n in dir(args) if n.startswith('regen_'))):
        unittest.main()
