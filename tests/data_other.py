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

GET_SLICE_EXPRISH_DATA = [
(r"""{1, 2}""", 'body[0].value', 0, 0, {}, r"""{1, 2}""", r"""{*()}""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value Set - 0,0..0,6
      .elts[2]
      0] Constant 1 - 0,1..0,2
      1] Constant 2 - 0,4..0,5
""", r"""
Set - ROOT 0,0..0,5
  .elts[1]
  0] Starred - 0,1..0,4
    .value Tuple - 0,2..0,4
      .ctx Load
    .ctx Load
"""),

(r"""(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)""", 'body[0].value', None, None, {}, r"""(       # hello
)""", r"""(
    1,  # last line
    2,  # second line
    3,  # third line
)""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value Tuple - 0,0..1,1
      .ctx Load
""", r"""
Tuple - ROOT 0,0..4,1
  .elts[3]
  0] Constant 1 - 1,4..1,5
  1] Constant 2 - 2,4..2,5
  2] Constant 3 - 3,4..3,5
  .ctx Load
"""),

(r"""(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)""", 'body[0].value', 0, 2, {}, r"""(       # hello
    3,  # third line
)""", r"""(
    1,  # last line
    2,  # second line
)""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value Tuple - 0,0..2,1
      .elts[1]
      0] Constant 3 - 1,4..1,5
      .ctx Load
""", r"""
Tuple - ROOT 0,0..3,1
  .elts[2]
  0] Constant 1 - 1,4..1,5
  1] Constant 2 - 2,4..2,5
  .ctx Load
"""),

(r"""(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)""", 'body[0].value', 1, 2, {}, r"""(       # hello
    1,  # last line
    3,  # third line
)""", r"""(
    2,  # second line
)""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value Tuple - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
""", r"""
Tuple - ROOT 0,0..2,1
  .elts[1]
  0] Constant 2 - 1,4..1,5
  .ctx Load
"""),

(r"""(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)""", 'body[0].value', 2, None, {}, r"""(       # hello
    1,  # last line
    2,  # second line
)""", r"""(
    3,  # third line
)""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value Tuple - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 2 - 2,4..2,5
      .ctx Load
""", r"""
Tuple - ROOT 0,0..2,1
  .elts[1]
  0] Constant 3 - 1,4..1,5
  .ctx Load
"""),

(r"""(           # hello
    1, 2, 3 # last line
)""", 'body[0].value', None, None, {}, r"""(           # hello
)""", r"""(
    1, 2, 3 # last line
)""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value Tuple - 0,0..1,1
      .ctx Load
""", r"""
Tuple - ROOT 0,0..2,1
  .elts[3]
  0] Constant 1 - 1,4..1,5
  1] Constant 2 - 1,7..1,8
  2] Constant 3 - 1,10..1,11
  .ctx Load
"""),

(r"""(           # hello
    1, 2, 3 # last line
)""", 'body[0].value', 0, 2, {}, r"""(           # hello
    3, # last line
)""", r"""(1, 2)""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value Tuple - 0,0..2,1
      .elts[1]
      0] Constant 3 - 1,4..1,5
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,6
  .elts[2]
  0] Constant 1 - 0,1..0,2
  1] Constant 2 - 0,4..0,5
  .ctx Load
"""),

(r"""(           # hello
    1, 2, 3 # last line
)""", 'body[0].value', 1, 2, {}, r"""(           # hello
    1, 3 # last line
)""", r"""(2,)""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value Tuple - 0,0..2,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,4
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""(           # hello
    1, 2, 3 # last line
)""", 'body[0].value', 2, None, {}, r"""(           # hello
    1, 2
)""", r"""(3, # last line
)""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value Tuple - 0,0..2,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      .ctx Load
""", r"""
Tuple - ROOT 0,0..1,1
  .elts[1]
  0] Constant 3 - 0,1..0,2
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', 1, 3, {}, r"""1, 4""", r"""2, 3""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Tuple - 0,0..0,4
      .elts[2]
      0] Constant 1 - 0,0..0,1
      1] Constant 4 - 0,3..0,4
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,4
  .elts[2]
  0] Constant 2 - 0,0..0,1
  1] Constant 3 - 0,3..0,4
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', -1, None, {}, r"""1, 2, 3""", r"""4,""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Tuple - 0,0..0,7
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,2
  .elts[1]
  0] Constant 4 - 0,0..0,1
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', None, None, {}, r"""()""", r"""1, 2, 3, 4""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,10
  .elts[4]
  0] Constant 1 - 0,0..0,1
  1] Constant 2 - 0,3..0,4
  2] Constant 3 - 0,6..0,7
  3] Constant 4 - 0,9..0,10
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', 1, 1, {}, r"""1, 2, 3, 4""", r"""()""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Tuple - 0,0..0,10
      .elts[4]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      3] Constant 4 - 0,9..0,10
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,2
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', 1, None, {}, r"""1,""", r"""2, 3, 4""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Constant 1 - 0,0..0,1
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,7
  .elts[3]
  0] Constant 2 - 0,0..0,1
  1] Constant 3 - 0,3..0,4
  2] Constant 4 - 0,6..0,7
  .ctx Load
"""),

(r"""1, 2, 3, 4""", 'body[0].value', 0, 3, {}, r"""4,""", r"""1, 2, 3""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Constant 4 - 0,0..0,1
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,7
  .elts[3]
  0] Constant 1 - 0,0..0,1
  1] Constant 2 - 0,3..0,4
  2] Constant 3 - 0,6..0,7
  .ctx Load
"""),

(r"""(1, 2
  ,  # comment
3, 4)""", 'body[0].value', 1, 2, {}, r"""(1,
3, 4)""", r"""(2
  ,  # comment
)""", r"""
Module - ROOT 0,0..1,5
  .body[1]
  0] Expr - 0,0..1,5
    .value Tuple - 0,0..1,5
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 3 - 1,0..1,1
      2] Constant 4 - 1,3..1,4
      .ctx Load
""", r"""
Tuple - ROOT 0,0..2,1
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""(1, 2
  ,
  3, 4)""", 'body[0].value', 1, 2, {}, r"""(1,
  3, 4)""", r"""(2
  ,)""", r"""
Module - ROOT 0,0..1,7
  .body[1]
  0] Expr - 0,0..1,7
    .value Tuple - 0,0..1,7
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 3 - 1,2..1,3
      2] Constant 4 - 1,5..1,6
      .ctx Load
""", r"""
Tuple - ROOT 0,0..1,4
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""(1, 2 \
  , \
  3, 4)""", 'body[0].value', 1, 2, {}, r"""(1, \
  3, 4)""", r"""(2 \
  ,)""", r"""
Module - ROOT 0,0..1,7
  .body[1]
  0] Expr - 0,0..1,7
    .value Tuple - 0,0..1,7
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 3 - 1,2..1,3
      2] Constant 4 - 1,5..1,6
      .ctx Load
""", r"""
Tuple - ROOT 0,0..1,4
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""(1, 2  # comment
  , \
  3, 4)""", 'body[0].value', 1, 2, {}, r"""(1, \
  3, 4)""", r"""(2  # comment
  ,)""", r"""
Module - ROOT 0,0..1,7
  .body[1]
  0] Expr - 0,0..1,7
    .value Tuple - 0,0..1,7
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 3 - 1,2..1,3
      2] Constant 4 - 1,5..1,6
      .ctx Load
""", r"""
Tuple - ROOT 0,0..1,4
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""(1, 2
  ,
3, 4)""", 'body[0].value', 1, 2, {}, r"""(1,
3, 4)""", r"""(2
  ,)""", r"""
Module - ROOT 0,0..1,5
  .body[1]
  0] Expr - 0,0..1,5
    .value Tuple - 0,0..1,5
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 3 - 1,0..1,1
      2] Constant 4 - 1,3..1,4
      .ctx Load
""", r"""
Tuple - ROOT 0,0..1,4
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""(1, 2
  , 3, 4)""", 'body[0].value', 1, 2, {}, r"""(1, 3, 4)""", r"""(2
  ,)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Tuple - 0,0..0,9
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 3 - 0,4..0,5
      2] Constant 4 - 0,7..0,8
      .ctx Load
""", r"""
Tuple - ROOT 0,0..1,4
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""(1, 2  # comment
  , 3, 4)""", 'body[0].value', 1, 2, {}, r"""(1, 3, 4)""", r"""(2  # comment
  ,)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Tuple - 0,0..0,9
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 3 - 0,4..0,5
      2] Constant 4 - 0,7..0,8
      .ctx Load
""", r"""
Tuple - ROOT 0,0..1,4
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )""", 'body[0].body[0].value', None, None, {}, r"""if 1:
    (       # hello
    )""", r"""(
    1,  # last line
    2,  # second line
    3,  # third line
)""", r"""
Module - ROOT 0,0..2,5
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..2,5
      .value Tuple - 1,4..2,5
        .ctx Load
""", r"""
Tuple - ROOT 0,0..4,1
  .elts[3]
  0] Constant 1 - 1,4..1,5
  1] Constant 2 - 2,4..2,5
  2] Constant 3 - 3,4..3,5
  .ctx Load
"""),

(r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )""", 'body[0].body[0].value', 0, 2, {}, r"""if 1:
    (       # hello
        3,  # third line
    )""", r"""(
    1,  # last line
    2,  # second line
)""", r"""
Module - ROOT 0,0..3,5
  .body[1]
  0] If - 0,0..3,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..3,5
      .value Tuple - 1,4..3,5
        .elts[1]
        0] Constant 3 - 2,8..2,9
        .ctx Load
""", r"""
Tuple - ROOT 0,0..3,1
  .elts[2]
  0] Constant 1 - 1,4..1,5
  1] Constant 2 - 2,4..2,5
  .ctx Load
"""),

(r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )""", 'body[0].body[0].value', 1, 2, {}, r"""if 1:
    (       # hello
        1,  # last line
        3,  # third line
    )""", r"""(
    2,  # second line
)""", r"""
Module - ROOT 0,0..4,5
  .body[1]
  0] If - 0,0..4,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..4,5
      .value Tuple - 1,4..4,5
        .elts[2]
        0] Constant 1 - 2,8..2,9
        1] Constant 3 - 3,8..3,9
        .ctx Load
""", r"""
Tuple - ROOT 0,0..2,1
  .elts[1]
  0] Constant 2 - 1,4..1,5
  .ctx Load
"""),

(r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )""", 'body[0].body[0].value', 2, None, {}, r"""if 1:
    (       # hello
        1,  # last line
        2,  # second line
    )""", r"""(
    3,  # third line
)""", r"""
Module - ROOT 0,0..4,5
  .body[1]
  0] If - 0,0..4,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..4,5
      .value Tuple - 1,4..4,5
        .elts[2]
        0] Constant 1 - 2,8..2,9
        1] Constant 2 - 3,8..3,9
        .ctx Load
""", r"""
Tuple - ROOT 0,0..2,1
  .elts[1]
  0] Constant 3 - 1,4..1,5
  .ctx Load
"""),

(r"""{1: 2, **b, **c}""", 'body[0].value', 1, 2, {}, r"""{1: 2, **c}""", r"""{**b}""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Dict - 0,0..0,11
      .keys[2]
      0] Constant 1 - 0,1..0,2
      1] None
      .values[2]
      0] Constant 2 - 0,4..0,5
      1] Name 'c' Load - 0,9..0,10
""", r"""
Dict - ROOT 0,0..0,5
  .keys[1]
  0] None
  .values[1]
  0] Name 'b' Load - 0,3..0,4
"""),

(r"""{1: 2, **b, **c}""", 'body[0].value', None, None, {}, r"""{}""", r"""{1: 2, **b, **c}""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Dict - 0,0..0,2
""", r"""
Dict - ROOT 0,0..0,16
  .keys[3]
  0] Constant 1 - 0,1..0,2
  1] None
  2] None
  .values[3]
  0] Constant 2 - 0,4..0,5
  1] Name 'b' Load - 0,9..0,10
  2] Name 'c' Load - 0,14..0,15
"""),

(r"""{1: 2, **b, **c}""", 'body[0].value', 2, None, {}, r"""{1: 2, **b}""", r"""{**c}""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Dict - 0,0..0,11
      .keys[2]
      0] Constant 1 - 0,1..0,2
      1] None
      .values[2]
      0] Constant 2 - 0,4..0,5
      1] Name 'b' Load - 0,9..0,10
""", r"""
Dict - ROOT 0,0..0,5
  .keys[1]
  0] None
  .values[1]
  0] Name 'c' Load - 0,3..0,4
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', None, None, {}, r"""[
]""", r"""[
    1,
    2,
    3,
]""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value List - 0,0..1,1
      .ctx Load
""", r"""
List - ROOT 0,0..4,1
  .elts[3]
  0] Constant 1 - 1,4..1,5
  1] Constant 2 - 2,4..2,5
  2] Constant 3 - 3,4..3,5
  .ctx Load
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', 0, 2, {}, r"""[
    3,
]""", r"""[
    1,
    2
]""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[1]
      0] Constant 3 - 1,4..1,5
      .ctx Load
""", r"""
List - ROOT 0,0..3,1
  .elts[2]
  0] Constant 1 - 1,4..1,5
  1] Constant 2 - 2,4..2,5
  .ctx Load
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', 1, 2, {}, r"""[
    1,
    3,
]""", r"""[
    2
]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..2,1
  .elts[1]
  0] Constant 2 - 1,4..1,5
  .ctx Load
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', 2, None, {}, r"""[
    1,
    2
]""", r"""[
    3,
]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 2 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..2,1
  .elts[1]
  0] Constant 3 - 1,4..1,5
  .ctx Load
"""),

(r"""[            # hello
    1, 2, 3,
    4
]""", 'body[0].value', 2, 3, {}, r"""[            # hello
    1, 2,
    4
]""", r"""[3]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Constant 4 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..0,3
  .elts[1]
  0] Constant 3 - 0,1..0,2
  .ctx Load
"""),

(r"""[            # hello
    1, 2, ( 3
     ), 4
]""", 'body[0].value', 2, 3, {}, r"""[            # hello
    1, 2, 4
]""", r"""[( 3
     )]""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Constant 4 - 1,10..1,11
      .ctx Load
""", r"""
List - ROOT 0,0..1,7
  .elts[1]
  0] Constant 3 - 0,3..0,4
  .ctx Load
"""),

(r"""[            # hello
    1, 2, ( 3
     ), 4
]""", 'body[0].value', 1, 3, {}, r"""[            # hello
    1, 4
]""", r"""[2, ( 3
     )]""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 4 - 1,7..1,8
      .ctx Load
""", r"""
List - ROOT 0,0..1,7
  .elts[2]
  0] Constant 2 - 0,1..0,2
  1] Constant 3 - 0,6..0,7
  .ctx Load
"""),

(r"""[            # hello
    1, 2, ( 3
     ), 4
]""", 'body[0].value', 1, None, {}, r"""[            # hello
    1
]""", r"""[2, ( 3
     ), 4]""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[1]
      0] Constant 1 - 1,4..1,5
      .ctx Load
""", r"""
List - ROOT 0,0..1,10
  .elts[3]
  0] Constant 2 - 0,1..0,2
  1] Constant 3 - 0,6..0,7
  2] Constant 4 - 1,8..1,9
  .ctx Load
"""),

(r"""i =                (self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                id(self) & (_sys.maxsize*2 + 1))""", 'body[0].value', 0, 3, {}, r"""i =                (
                id(self) & (_sys.maxsize*2 + 1),)""", r"""(self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1))
)""", r"""
Module - ROOT 0,0..1,49
  .body[1]
  0] Assign - 0,0..1,49
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value Tuple - 0,19..1,49
      .elts[1]
      0] BinOp - 1,16..1,47
        .left Call - 1,16..1,24
          .func Name 'id' Load - 1,16..1,18
          .args[1]
          0] Name 'self' Load - 1,19..1,23
        .op BitAnd - 1,25..1,26
        .right BinOp - 1,28..1,46
          .left BinOp - 1,28..1,42
            .left Attribute - 1,28..1,40
              .value Name '_sys' Load - 1,28..1,32
              .attr 'maxsize'
              .ctx Load
            .op Mult - 1,40..1,41
            .right Constant 2 - 1,41..1,42
          .op Add - 1,43..1,44
          .right Constant 1 - 1,45..1,46
      .ctx Load
""", r"""
Tuple - ROOT 0,0..2,1
  .elts[3]
  0] Attribute - 0,1..0,24
    .value Attribute - 0,1..0,15
      .value Name 'self' Load - 0,1..0,5
      .attr '__class__'
      .ctx Load
    .attr '__name__'
    .ctx Load
  1] Attribute - 0,26..0,36
    .value Name 'self' Load - 0,26..0,30
    .attr '_name'
    .ctx Load
  2] BinOp - 1,17..1,52
    .left Attribute - 1,17..1,29
      .value Name 'self' Load - 1,17..1,21
      .attr '_handle'
      .ctx Load
    .op BitAnd - 1,30..1,31
    .right BinOp - 1,33..1,51
      .left BinOp - 1,33..1,47
        .left Attribute - 1,33..1,45
          .value Name '_sys' Load - 1,33..1,37
          .attr 'maxsize'
          .ctx Load
        .op Mult - 1,45..1,46
        .right Constant 2 - 1,46..1,47
      .op Add - 1,48..1,49
      .right Constant 1 - 1,50..1,51
  .ctx Load
"""),

(r"""i = namespace = {**__main__.__builtins__.__dict__,
             **__main__.__dict__}""", 'body[0].value', 0, 1, {}, r"""i = namespace = {
             **__main__.__dict__}""", r"""{**__main__.__builtins__.__dict__}""", r"""
Module - ROOT 0,0..1,33
  .body[1]
  0] Assign - 0,0..1,33
    .targets[2]
    0] Name 'i' Store - 0,0..0,1
    1] Name 'namespace' Store - 0,4..0,13
    .value Dict - 0,16..1,33
      .keys[1]
      0] None
      .values[1]
      0] Attribute - 1,15..1,32
        .value Name '__main__' Load - 1,15..1,23
        .attr '__dict__'
        .ctx Load
""", r"""
Dict - ROOT 0,0..0,34
  .keys[1]
  0] None
  .values[1]
  0] Attribute - 0,3..0,33
    .value Attribute - 0,3..0,24
      .value Name '__main__' Load - 0,3..0,11
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
}""", 'body[0].value', None, 2, {}, r"""env = {
    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}""", r"""{
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1"
}""", r"""
Module - ROOT 0,0..4,1
  .body[1]
  0] Assign - 0,0..4,1
    .targets[1]
    0] Name 'env' Store - 0,0..0,3
    .value Dict - 0,6..4,1
      .keys[3]
      0] Constant 'PYLAUNCHER_DRYRUN' - 1,4..1,23
      1] Constant 'PYLAUNCHER_LIMIT_TO_COMPANY' - 2,4..2,33
      2] None
      .values[3]
      0] Constant '1' - 1,25..1,28
      1] Constant '' - 2,35..2,37
      2] DictComp - 3,6..3,52
        .key Call - 3,7..3,16
          .func Attribute - 3,7..3,14
            .value Name 'k' Load - 3,7..3,8
            .attr 'upper'
            .ctx Load
        .value Name 'v' Load - 3,18..3,19
        .generators[1]
        0] comprehension - 3,20..3,51
          .target Tuple - 3,24..3,28
            .elts[2]
            0] Name 'k' Store - 3,24..3,25
            1] Name 'v' Store - 3,27..3,28
            .ctx Store
          .iter Call - 3,32..3,51
            .func Attribute - 3,32..3,49
              .value BoolOp - 3,33..3,42
                .op Or
                .values[2]
                0] Name 'env' Load - 3,33..3,36
                1] Dict - 3,40..3,42
              .attr 'items'
              .ctx Load
          .is_async 0
""", r"""
Dict - ROOT 0,0..3,1
  .keys[2]
  0] None
  1] Constant 'PYLAUNCHER_DEBUG' - 2,4..2,22
  .values[2]
  0] DictComp - 1,6..1,78
    .key Call - 1,7..1,16
      .func Attribute - 1,7..1,14
        .value Name 'k' Load - 1,7..1,8
        .attr 'upper'
        .ctx Load
    .value Name 'v' Load - 1,18..1,19
    .generators[1]
    0] comprehension - 1,20..1,77
      .target Tuple - 1,24..1,28
        .elts[2]
        0] Name 'k' Store - 1,24..1,25
        1] Name 'v' Store - 1,27..1,28
        .ctx Store
      .iter Call - 1,32..1,50
        .func Attribute - 1,32..1,48
          .value Attribute - 1,32..1,42
            .value Name 'os' Load - 1,32..1,34
            .attr 'environ'
            .ctx Load
          .attr 'items'
          .ctx Load
      .ifs[1]
      0] Compare - 1,54..1,77
        .left Call - 1,54..1,63
          .func Attribute - 1,54..1,61
            .value Name 'k' Load - 1,54..1,55
            .attr 'upper'
            .ctx Load
        .ops[1]
        0] NotIn - 1,64..1,70
        .comparators[1]
        0] Name 'ignore' Load - 1,71..1,77
      .is_async 0
  1] Constant '1' - 2,24..2,27
"""),

(r"""(None, False, True, 12345, 123.45, 'abcde', 'абвгд', b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})""", 'body[0].value', 5, 7, {}, r"""(None, False, True, 12345, 123.45, b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})""", r"""('abcde', 'абвгд')""", r"""
Module - ROOT 0,0..2,67
  .body[1]
  0] Expr - 0,0..2,67
    .value Tuple - 0,0..2,67
      .elts[11]
      0] Constant None - 0,1..0,5
      1] Constant False - 0,7..0,12
      2] Constant True - 0,14..0,18
      3] Constant 12345 - 0,20..0,25
      4] Constant 123.45 - 0,27..0,33
      5] Constant b'abcde' - 0,35..0,43
      6] Call - 1,12..1,55
        .func Attribute - 1,12..1,29
          .value Name 'datetime' Load - 1,12..1,20
          .attr 'datetime'
          .ctx Load
        .args[6]
        0] Constant 2004 - 1,30..1,34
        1] Constant 10 - 1,36..1,38
        2] Constant 26 - 1,40..1,42
        3] Constant 10 - 1,44..1,46
        4] Constant 33 - 1,48..1,50
        5] Constant 33 - 1,52..1,54
      7] Call - 2,12..2,31
        .func Name 'bytearray' Load - 2,12..2,21
        .args[1]
        0] Constant b'abcde' - 2,22..2,30
      8] List - 2,33..2,42
        .elts[2]
        0] Constant 12 - 2,34..2,36
        1] Constant 345 - 2,38..2,41
        .ctx Load
      9] Tuple - 2,44..2,53
        .elts[2]
        0] Constant 12 - 2,45..2,47
        1] Constant 345 - 2,49..2,52
        .ctx Load
      10] Dict - 2,55..2,66
        .keys[1]
        0] Constant '12' - 2,56..2,60
        .values[1]
        0] Constant 345 - 2,62..2,65
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,18
  .elts[2]
  0] Constant 'abcde' - 0,1..0,8
  1] Constant 'абвгд' - 0,10..0,17
  .ctx Load
"""),

(r"""[a, b] = c""", 'body[0].targets[0]', 1, 2, {}, r"""[a] = c""", r"""[b]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Assign - 0,0..0,7
    .targets[1]
    0] List - 0,0..0,3
      .elts[1]
      0] Name 'a' Store - 0,1..0,2
      .ctx Store
    .value Name 'c' Load - 0,6..0,7
""", r"""
List - ROOT 0,0..0,3
  .elts[1]
  0] Name 'b' Load - 0,1..0,2
  .ctx Load
"""),

(r"""{
            'exception': exc,
            'future': fut,
            'message': ('GetQueuedCompletionStatus() returned an '
                        'unexpected event'),
            'status': ('err=%s transferred=%s key=%#x address=%#x'
                       % (err, transferred, key, address),),
                                                 'addr': address}""", 'body[0].value', 1, 4, {}, r"""{
            'exception': exc,
                                                 'addr': address}""", r"""{
            'future': fut,
            'message': ('GetQueuedCompletionStatus() returned an '
                        'unexpected event'),
            'status': ('err=%s transferred=%s key=%#x address=%#x'
                       % (err, transferred, key, address),)
}""", r"""
Module - ROOT 0,0..2,65
  .body[1]
  0] Expr - 0,0..2,65
    .value Dict - 0,0..2,65
      .keys[2]
      0] Constant 'exception' - 1,12..1,23
      1] Constant 'addr' - 2,49..2,55
      .values[2]
      0] Name 'exc' Load - 1,25..1,28
      1] Name 'address' Load - 2,57..2,64
""", r"""
Dict - ROOT 0,0..6,1
  .keys[3]
  0] Constant 'future' - 1,12..1,20
  1] Constant 'message' - 2,12..2,21
  2] Constant 'status' - 4,12..4,20
  .values[3]
  0] Name 'fut' Load - 1,22..1,25
  1] Constant 'GetQueuedCompletionStatus() returned an unexpected event' - 2,24..3,42
  2] Tuple - 4,22..5,59
    .elts[1]
    0] BinOp - 4,23..5,57
      .left Constant 'err=%s transferred=%s key=%#x address=%#x' - 4,23..4,66
      .op Mod - 5,23..5,24
      .right Tuple - 5,25..5,57
        .elts[4]
        0] Name 'err' Load - 5,26..5,29
        1] Name 'transferred' Load - 5,31..5,42
        2] Name 'key' Load - 5,44..5,47
        3] Name 'address' Load - 5,49..5,56
        .ctx Load
    .ctx Load
"""),

(r"""(1, (2), 3)""", 'body[0].value', 1, 2, {}, r"""(1, 3)""", r"""((2),)""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value Tuple - 0,0..0,6
      .elts[2]
      0] Constant 1 - 0,1..0,2
      1] Constant 3 - 0,4..0,5
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,6
  .elts[1]
  0] Constant 2 - 0,2..0,3
  .ctx Load
"""),

(r"""@patch.dict({'a': 'b'})
class cls: pass""", 'body[0].decorator_list[0].args[0]', 0, 1, {}, r"""@patch.dict({})
class cls: pass""", r"""{'a': 'b'}""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] ClassDef - 1,0..1,15
    .name 'cls'
    .body[1]
    0] Pass - 1,11..1,15
    .decorator_list[1]
    0] Call - 0,1..0,15
      .func Attribute - 0,1..0,11
        .value Name 'patch' Load - 0,1..0,6
        .attr 'dict'
        .ctx Load
      .args[1]
      0] Dict - 0,12..0,14
""", r"""
Dict - ROOT 0,0..0,10
  .keys[1]
  0] Constant 'a' - 0,1..0,4
  .values[1]
  0] Constant 'b' - 0,6..0,9
"""),

(r"""class cls:
    a, b = c""", 'body[0].body[0].targets[0]', 0, 2, {}, r"""class cls:
    () = c""", r"""a, b""", r"""
Module - ROOT 0,0..1,10
  .body[1]
  0] ClassDef - 0,0..1,10
    .name 'cls'
    .body[1]
    0] Assign - 1,4..1,10
      .targets[1]
      0] Tuple - 1,4..1,6
        .ctx Store
      .value Name 'c' Load - 1,9..1,10
""", r"""
Tuple - ROOT 0,0..0,4
  .elts[2]
  0] Name 'a' Load - 0,0..0,1
  1] Name 'b' Load - 0,3..0,4
  .ctx Load
"""),

(r"""if 1:
    yy, tm, = tm, yy""", 'body[0].body[0].targets[0]', 1, 2, {}, r"""if 1:
    yy, = tm, yy""", r"""tm,""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] If - 0,0..1,16
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Assign - 1,4..1,16
      .targets[1]
      0] Tuple - 1,4..1,7
        .elts[1]
        0] Name 'yy' Store - 1,4..1,6
        .ctx Store
      .value Tuple - 1,10..1,16
        .elts[2]
        0] Name 'tm' Load - 1,10..1,12
        1] Name 'yy' Load - 1,14..1,16
        .ctx Load
""", r"""
Tuple - ROOT 0,0..0,3
  .elts[1]
  0] Name 'tm' Load - 0,0..0,2
  .ctx Load
"""),

(r"""{1, 2}""", 'body[0].value', 0, 2, {}, r"""{*()}""", r"""{1, 2}""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Set - 0,0..0,5
      .elts[1]
      0] Starred - 0,1..0,4
        .value Tuple - 0,2..0,4
          .ctx Load
        .ctx Load
""", r"""
Set - ROOT 0,0..0,6
  .elts[2]
  0] Constant 1 - 0,1..0,2
  1] Constant 2 - 0,4..0,5
"""),

(r"""{1, 2}""", 'body[0].value', 0, 0, {}, r"""{1, 2}""", r"""{*()}""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value Set - 0,0..0,6
      .elts[2]
      0] Constant 1 - 0,1..0,2
      1] Constant 2 - 0,4..0,5
""", r"""
Set - ROOT 0,0..0,5
  .elts[1]
  0] Starred - 0,1..0,4
    .value Tuple - 0,2..0,4
      .ctx Load
    .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 1, {}, r"""2, 3,""", r"""1,""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Tuple - 0,0..0,5
      .elts[2]
      0] Constant 2 - 0,0..0,1
      1] Constant 3 - 0,3..0,4
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,2
  .elts[1]
  0] Constant 1 - 0,0..0,1
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 2, {}, r"""1, 3,""", r"""2,""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Tuple - 0,0..0,5
      .elts[2]
      0] Constant 1 - 0,0..0,1
      1] Constant 3 - 0,3..0,4
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,2
  .elts[1]
  0] Constant 2 - 0,0..0,1
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 3, {}, r"""1, 2""", r"""3,""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Tuple - 0,0..0,4
      .elts[2]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,2
  .elts[1]
  0] Constant 3 - 0,0..0,1
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 2, {}, r"""3,""", r"""1, 2""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Constant 3 - 0,0..0,1
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,4
  .elts[2]
  0] Constant 1 - 0,0..0,1
  1] Constant 2 - 0,3..0,4
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 3, {}, r"""1,""", r"""2, 3,""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Constant 1 - 0,0..0,1
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,5
  .elts[2]
  0] Constant 2 - 0,0..0,1
  1] Constant 3 - 0,3..0,4
  .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 3, {}, r"""()""", r"""1, 2, 3,""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
""", r"""
Tuple - ROOT 0,0..0,8
  .elts[3]
  0] Constant 1 - 0,0..0,1
  1] Constant 2 - 0,3..0,4
  2] Constant 3 - 0,6..0,7
  .ctx Load
"""),

(r"""[
    1,

    # pre
    2, # line
    # post

    3,
]""", 'body[0].value', 1, 2, {'trivia': ('-1', '-1')}, r"""[
    1,

    # pre
    # line
    # post

    3,
]""", r"""[2]""", r"""
Module - ROOT 0,0..8,1
  .body[1]
  0] Expr - 0,0..8,1
    .value List - 0,0..8,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 7,4..7,5
      .ctx Load
""", r"""
List - ROOT 0,0..0,3
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""[
    1,

    # pre
    2, # line
    # post

    3,
]""", 'body[0].value', 1, 2, {'trivia': ('block-1', 'line-1')}, r"""[
    1,
    # post

    3,
]""", r"""[
    # pre
    2, # line
]""", r"""
Module - ROOT 0,0..5,1
  .body[1]
  0] Expr - 0,0..5,1
    .value List - 0,0..5,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 4,4..4,5
      .ctx Load
""", r"""
List - ROOT 0,0..3,1
  .elts[1]
  0] Constant 2 - 2,4..2,5
  .ctx Load
"""),

(r"""[
    1,
    # prepre

    # pre
    2, # line
    # post

    3,
]""", 'body[0].value', 1, 2, {'trivia': ('block+1', 'line+1')}, r"""[
    1,
    # prepre
    # post

    3,
]""", r"""[

    # pre
    2, # line
]""", r"""
Module - ROOT 0,0..6,1
  .body[1]
  0] Expr - 0,0..6,1
    .value List - 0,0..6,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 5,4..5,5
      .ctx Load
""", r"""
List - ROOT 0,0..4,1
  .elts[1]
  0] Constant 2 - 3,4..3,5
  .ctx Load
"""),

(r"""[
    1,
    # prepre

    # pre
    2, # line
    # post

    3,
]""", 'body[0].value', 1, 2, {'trivia': ('all-1', 'block-1')}, r"""[
    1,
    3,
]""", r"""[
    # prepre

    # pre
    2, # line
    # post
]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..6,1
  .elts[1]
  0] Constant 2 - 4,4..4,5
  .ctx Load
"""),

(r"""[
    1,

    # prepre

    # pre
    2, # line
    # post

    # postpost

    3,
]""", 'body[0].value', 1, 2, {'trivia': ('all-1', 'all-1')}, r"""[
    1,
    3,
]""", r"""[
    # prepre

    # pre
    2, # line
    # post

    # postpost
]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..8,1
  .elts[1]
  0] Constant 2 - 4,4..4,5
  .ctx Load
"""),

(r"""[
    1,

    # prepre

    # pre
    2, # line
    # post

    # postpost

    3,
]""", 'body[0].value', 1, 2, {'trivia': ('all+1', 'all+1')}, r"""[
    1,
    3,
]""", r"""[

    # prepre

    # pre
    2, # line
    # post

    # postpost

]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..10,1
  .elts[1]
  0] Constant 2 - 5,4..5,5
  .ctx Load
"""),

(r"""[
    1,
    \
    # prepre
    \
    # pre
    2, # line
    # post
    \
    # postpost
    \
    3,
]""", 'body[0].value', 1, 2, {'trivia': ('all+1', 'all+1')}, r"""[
    1,
    3,
]""", r"""[
    \
    # prepre
    \
    # pre
    2, # line
    # post
    \
    # postpost
    \
]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..10,1
  .elts[1]
  0] Constant 2 - 5,4..5,5
  .ctx Load
"""),

(r"""[
    1,
    # prepre
    # pre
    2, # line
    # post
    # postpost
    3,
]""", 'body[0].value', 1, 2, {'trivia': (3, 5)}, r"""[
    1,
    # prepre
    # postpost
    3,
]""", r"""[
    # pre
    2, # line
    # post
]""", r"""
Module - ROOT 0,0..5,1
  .body[1]
  0] Expr - 0,0..5,1
    .value List - 0,0..5,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 4,4..4,5
      .ctx Load
""", r"""
List - ROOT 0,0..4,1
  .elts[1]
  0] Constant 2 - 2,4..2,5
  .ctx Load
"""),

(r"""[
    1, \
    2, \
    3,
]""", 'body[0].value', 1, 2, {}, r"""[
    1, \
    3,
]""", r"""[
    2, \
]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..2,1
  .elts[1]
  0] Constant 2 - 1,4..1,5
  .ctx Load
"""),

(r"""[
    1, 2, \
    3,
]""", 'body[0].value', 1, 2, {}, r"""[
    1, \
    3,
]""", r"""[2]""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
""", r"""
List - ROOT 0,0..0,3
  .elts[1]
  0] Constant 2 - 0,1..0,2
  .ctx Load
"""),

(r"""{a: b,

    # pre
    c: d,  # line
    # post

    e: f}""", 'body[0].value', 1, 2, {}, r"""{a: b,

    # post

    e: f}""", r"""{
    # pre
    c: d,  # line
}""", r"""
Module - ROOT 0,0..4,9
  .body[1]
  0] Expr - 0,0..4,9
    .value Dict - 0,0..4,9
      .keys[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'e' Load - 4,4..4,5
      .values[2]
      0] Name 'b' Load - 0,4..0,5
      1] Name 'f' Load - 4,7..4,8
""", r"""
Dict - ROOT 0,0..3,1
  .keys[1]
  0] Name 'c' Load - 2,4..2,5
  .values[1]
  0] Name 'd' Load - 2,7..2,8
"""),

(r"""{a: b,

    # pre
    c: d,  # line
    # post

    e: f}""", 'body[0].value', 1, 2, {'trivia': (False, 'block+1')}, r"""{a: b,

    # pre
    e: f}""", r"""{
    c: d,  # line
    # post

}""", r"""
Module - ROOT 0,0..3,9
  .body[1]
  0] Expr - 0,0..3,9
    .value Dict - 0,0..3,9
      .keys[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'e' Load - 3,4..3,5
      .values[2]
      0] Name 'b' Load - 0,4..0,5
      1] Name 'f' Load - 3,7..3,8
""", r"""
Dict - ROOT 0,0..4,1
  .keys[1]
  0] Name 'c' Load - 1,4..1,5
  .values[1]
  0] Name 'd' Load - 1,7..1,8
"""),

(r"""{**a, **b, **c}""", 'body[0].value', 1, 2, {}, r"""{**a, **c}""", r"""{**b}""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Dict - 0,0..0,10
      .keys[2]
      0] None
      1] None
      .values[2]
      0] Name 'a' Load - 0,3..0,4
      1] Name 'c' Load - 0,8..0,9
""", r"""
Dict - ROOT 0,0..0,5
  .keys[1]
  0] None
  .values[1]
  0] Name 'b' Load - 0,3..0,4
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 0, {'matchor_get': False, '_verify': False}, r"""match a:
 case a | b: pass""", r"""""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchOr - 1,6..1,11
        .patterns[2]
        0] MatchAs - 1,6..1,7
          .name 'a'
        1] MatchAs - 1,10..1,11
          .name 'b'
      .body[1]
      0] Pass - 1,13..1,17
""", r"""
MatchOr - ROOT 0,0..0,0
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 1, {'matchor_get': False, 'matchor_del': False, '_verify': False}, r"""match a:
 case b: pass""", r"""a""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchOr - 1,6..1,7
        .patterns[1]
        0] MatchAs - 1,6..1,7
          .name 'b'
      .body[1]
      0] Pass - 1,9..1,13
""", r"""
MatchOr - ROOT 0,0..0,1
  .patterns[1]
  0] MatchAs - 0,0..0,1
    .name 'a'
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 2, {'matchor_del': False, '_verify': False}, r"""match a:
 case : pass""", r"""a | b""", r"""
Module - ROOT 0,0..1,12
  .body[1]
  0] Match - 0,0..1,12
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,12
      .pattern MatchOr - 1,6..1,6
      .body[1]
      0] Pass - 1,8..1,12
""", r"""
MatchOr - ROOT 0,0..0,5
  .patterns[2]
  0] MatchAs - 0,0..0,1
    .name 'a'
  1] MatchAs - 0,4..0,5
    .name 'b'
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 1, {'matchor_get': True, 'matchor_del': True, '_verify': False}, r"""match a:
 case b: pass""", r"""a""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
        .name 'b'
      .body[1]
      0] Pass - 1,9..1,13
""", r"""
MatchAs - ROOT 0,0..0,1
  .name 'a'
"""),

(r"""match a:
 case (a |
# pre
b | # line1
c | # line2
# post
d): pass""", 'body[0].cases[0].pattern', 1, 2, {}, r"""match a:
 case (a |
c | # line2
# post
d): pass""", r"""
# pre
b # line1
""", r"""
Module - ROOT 0,0..4,8
  .body[1]
  0] Match - 0,0..4,8
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..4,8
      .pattern MatchOr - 1,7..4,1
        .patterns[3]
        0] MatchAs - 1,7..1,8
          .name 'a'
        1] MatchAs - 2,0..2,1
          .name 'c'
        2] MatchAs - 4,0..4,1
          .name 'd'
      .body[1]
      0] Pass - 4,4..4,8
""", r"""
MatchAs - ROOT 2,0..2,1
  .name 'b'
"""),

(r"""match a:
 case (a |
# pre
b | # line1
c | # line2
# post
d): pass""", 'body[0].cases[0].pattern', 1, 3, {'trivia': (None, 'block')}, r"""match a:
 case (a |
d): pass""", r"""(
# pre
b | # line1
c # line2
# post
)""", r"""
Module - ROOT 0,0..2,8
  .body[1]
  0] Match - 0,0..2,8
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..2,8
      .pattern MatchOr - 1,7..2,1
        .patterns[2]
        0] MatchAs - 1,7..1,8
          .name 'a'
        1] MatchAs - 2,0..2,1
          .name 'd'
      .body[1]
      0] Pass - 2,4..2,8
""", r"""
MatchOr - ROOT 2,0..3,1
  .patterns[2]
  0] MatchAs - 2,0..2,1
    .name 'b'
  1] MatchAs - 3,0..3,1
    .name 'c'
"""),

]  # END OF GET_SLICE_EXPRISH_DATA

GET_SLICE_STMTISH_DATA = [
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""
if 1:
    i ; j  # post
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i
""", r"""j  # post
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""
if 1:
    i ; j ; k
""", 'body[0]', 1, 2, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    i ; k
""", r"""j""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,9
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 2,8..2,9
      .value Name 'k' Load - 2,8..2,9
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,14
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,14
      .test Constant 2 - 3,7..3,8
      .body[1]
      0] Pass - 3,10..3,14
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,14
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,14
      .test Constant 2 - 3,7..3,8
      .body[1]
      0] Pass - 3,10..3,14
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,14
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,14
      .test Constant 2 - 3,7..3,8
      .body[1]
      0] Pass - 3,10..3,14
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,14
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,14
      .test Constant 2 - 3,7..3,8
      .body[1]
      0] Pass - 3,10..3,14
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,14
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,14
      .test Constant 1 - 3,7..3,8
      .body[1]
      0] Pass - 3,10..3,14
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,14
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,14
      .test Constant 2 - 3,7..3,8
      .body[1]
      0] Pass - 3,10..3,14
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 5,4..5,5
      .value Name 'k' Load - 5,4..5,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,3
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Expr - 3,2..3,3
      .value Name 'j' Load - 3,2..3,3
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: pass
else: i ; j
""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""
if 1: pass
else: j
""", r"""i""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,7
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Expr - 2,6..2,7
      .value Name 'j' Load - 2,6..2,7
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""if 1: pass
else: \
  i ; j""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""if 1: pass
else:
  j""", r"""i""", r"""
Module - ROOT 0,0..2,3
  .body[1]
  0] If - 0,0..2,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Pass - 0,6..0,10
    .orelse[1]
    0] Expr - 2,2..2,3
      .value Name 'j' Load - 2,2..2,3
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""if 1: pass
else: \
  i ; \
    j""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""if 1: pass
else:
    j""", r"""i""", r"""
Module - ROOT 0,0..2,5
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Pass - 0,6..0,10
    .orelse[1]
    0] Expr - 2,4..2,5
      .value Name 'j' Load - 2,4..2,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""if 1: pass
else:
  i \
 ; \
    j""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""if 1: pass
else:
  j""", r"""i""", r"""
Module - ROOT 0,0..2,3
  .body[1]
  0] If - 0,0..2,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Pass - 0,6..0,10
    .orelse[1]
    0] Expr - 2,2..2,3
      .value Name 'j' Load - 2,2..2,3
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""if 1: pass
else: i ; j""", 'body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, r"""if 1: pass
else: j""", r"""i""", r"""
Module - ROOT 0,0..1,7
  .body[1]
  0] If - 0,0..1,7
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Pass - 0,6..0,10
    .orelse[1]
    0] Expr - 1,6..1,7
      .value Name 'j' Load - 1,6..1,7
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,14
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,14
      .test Constant 2 - 3,7..3,8
      .body[1]
      0] Pass - 3,10..3,14
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,14
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,14
      .test Constant 2 - 3,7..3,8
      .body[1]
      0] Pass - 3,10..3,14
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,12
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] If - 3,2..3,12
      .test Constant 2 - 3,5..3,6
      .body[1]
      0] Pass - 3,8..3,12
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""
if 1: \
    i; j
""", 'body[0]', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
if 1:
    j
""", r"""i""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'j' Load - 2,4..2,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,5
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 7,4..7,5
      .value Name 'j' Load - 7,4..7,5
""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,5
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 7,4..7,5
      .value Name 'j' Load - 7,4..7,5
""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
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
Module - ROOT 0,0..6,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 5,0..5,1
    .value Name 'j' Load - 5,0..5,1
""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
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
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 4,0..4,1
    .value Name 'j' Load - 4,0..4,1
""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
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
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 3,0..3,1
    .value Name 'j' Load - 3,0..3,1
""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
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
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
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
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
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
Module - ROOT 0,0..6,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 5,0..5,1
    .value Name 'j' Load - 5,0..5,1
""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] FunctionDef - 1,0..1,13
    .name 'f'
    .body[1]
    0] Pass - 1,9..1,13
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
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 4,0..4,1
    .value Name 'j' Load - 4,0..4,1
""", r"""
Module - ROOT 0,0..3,6
  .body[1]
  0] ClassDef - 2,0..3,6
    .name 'cls'
    .body[1]
    0] Pass - 3,2..3,6
    .decorator_list[2]
    0] Name 'deco1' Load - 0,1..0,6
    1] Name 'deco2' Load - 1,1..1,6
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
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 3,0..4,6
    .name 'cls'
    .body[1]
    0] Pass - 4,2..4,6
    .decorator_list[2]
    0] Name 'deco1' Load - 1,1..1,6
    1] Call - 2,1..2,12
      .func Name 'deco2' Load - 2,1..2,6
      .args[2]
      0] Name 'a' Load - 2,7..2,8
      1] Name 'b' Load - 2,10..2,11
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
Module - ROOT 0,0..6,0
  .body[2]
  0] FunctionDef - 1,0..2,9
    .name 'func1'
    .body[1]
    0] Break - 2,4..2,9
  1] Continue - 5,0..5,8
""", r"""
Module - ROOT 0,0..1,8
  .body[1]
  0] FunctionDef - 0,0..1,8
    .name 'func0'
    .body[1]
    0] Pass - 1,4..1,8
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
Module - ROOT 0,0..6,0
  .body[2]
  0] FunctionDef - 1,0..2,8
    .name 'func0'
    .body[1]
    0] Pass - 2,4..2,8
  1] Continue - 5,0..5,8
""", r"""
Module - ROOT 0,0..1,9
  .body[1]
  0] FunctionDef - 0,0..1,9
    .name 'func1'
    .body[1]
    0] Break - 1,4..1,9
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
Module - ROOT 0,0..7,0
  .body[2]
  0] FunctionDef - 2,0..3,9
    .name 'func1'
    .body[1]
    0] Break - 3,4..3,9
  1] Continue - 6,0..6,8
""", r"""
Module - ROOT 0,0..1,8
  .body[1]
  0] FunctionDef - 0,0..1,8
    .name 'func0'
    .body[1]
    0] Pass - 1,4..1,8
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
Module - ROOT 0,0..7,0
  .body[2]
  0] FunctionDef - 1,0..2,8
    .name 'func0'
    .body[1]
    0] Pass - 2,4..2,8
  1] Continue - 6,0..6,8
""", r"""
Module - ROOT 0,0..1,9
  .body[1]
  0] FunctionDef - 0,0..1,9
    .name 'func1'
    .body[1]
    0] Break - 1,4..1,9
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
Module - ROOT 0,0..6,0
  .body[2]
  0] ClassDef - 1,0..3,13
    .name 'cls'
    .body[1]
    0] FunctionDef - 2,4..3,13
      .name 'meth1'
      .body[1]
      0] Break - 3,8..3,13
  1] Continue - 5,0..5,8
""", r"""
Module - ROOT 0,0..1,8
  .body[1]
  0] FunctionDef - 0,0..1,8
    .name 'meth0'
    .body[1]
    0] Pass - 1,4..1,8
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
Module - ROOT 0,0..6,0
  .body[2]
  0] ClassDef - 1,0..3,12
    .name 'cls'
    .body[1]
    0] FunctionDef - 2,4..3,12
      .name 'meth0'
      .body[1]
      0] Pass - 3,8..3,12
  1] Continue - 5,0..5,8
""", r"""
Module - ROOT 0,0..1,9
  .body[1]
  0] FunctionDef - 0,0..1,9
    .name 'meth1'
    .body[1]
    0] Break - 1,4..1,9
"""),

(r"""
if 1:
    i ; j



""", 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1:
    i



""", r"""j""", r"""
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""
if 1:
    i ; j



""", 'body[0]', 1, 2, None, {'postspace': 1}, r"""
if 1:
    i


""", r"""j""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""
if 1:
    i ; j



""", 'body[0]', 1, 2, None, {'postspace': True}, r"""
if 1:
    i
""", r"""j""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""
if 1:
    i ; j



""", 'body[0]', 0, 1, None, {'postspace': True}, r"""
if 1:
    j



""", r"""i""", r"""
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'j' Load - 2,4..2,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
def f():
    i ; j



""", '', 0, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""



""", r"""def f():
    i ; j""", r"""
Module - ROOT 0,0..4,0
""", r"""
Module - ROOT 0,0..1,9
  .body[1]
  0] FunctionDef - 0,0..1,9
    .name 'f'
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 1,8..1,9
      .value Name 'j' Load - 1,8..1,9
"""),

(r"""
def f():
    i ; j



""", '', 0, 1, None, {'postspace': True}, r"""
""", r"""def f():
    i ; j""", r"""
Module - ROOT 0,0..1,0
""", r"""
Module - ROOT 0,0..1,9
  .body[1]
  0] FunctionDef - 0,0..1,9
    .name 'f'
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 1,8..1,9
      .value Name 'j' Load - 1,8..1,9
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
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 1,0..3,3
    .name 'f'
    .body[1]
    0] Expr - 3,2..3,3
      .value Name 'k' Load - 3,2..3,3
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] FunctionDef - 1,0..4,3
    .name 'f'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,2..4,3
      .value Name 'k' Load - 4,2..4,3
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 1,0..3,3
    .name 'f'
    .body[1]
    0] Expr - 3,2..3,3
      .value Name 'k' Load - 3,2..3,3
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] FunctionDef - 1,0..4,3
    .name 'f'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,2..4,3
      .value Name 'k' Load - 4,2..4,3
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] FunctionDef - 1,0..4,5
    .name 'f'
    .body[1]
    0] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
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
Module - ROOT 0,0..6,0
  .body[1]
  0] FunctionDef - 1,0..5,5
    .name 'f'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 5,4..5,5
      .value Name 'k' Load - 5,4..5,5
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""
i ; \
 j
""", '', 0, 1, None, {'precomms': True, 'postcomms': True}, r"""
j
""", r"""i""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
def foo():
    # verify statements that end with semi-colons
    x = 1; pass; del x;
foo()
""", 'body[0]', 2, 3, None, {}, r"""
def foo():
    # verify statements that end with semi-colons
    x = 1; pass
foo()
""", r"""del x""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..3,15
    .name 'foo'
    .body[2]
    0] Assign - 3,4..3,9
      .targets[1]
      0] Name 'x' Store - 3,4..3,5
      .value Constant 1 - 3,8..3,9
    1] Pass - 3,11..3,15
  1] Expr - 4,0..4,5
    .value Call - 4,0..4,5
      .func Name 'foo' Load - 4,0..4,3
""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Delete - 0,0..0,5
    .targets[1]
    0] Name 'x' Del - 0,4..0,5
"""),

(r"""
if 1: i
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
if 1:
""", r"""i""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
if 1:""", r"""i""", r"""
Module - ROOT 0,0..1,5
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i  # post
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
if 1:
""", r"""i  # post
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i  # post""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
if 1:""", r"""i  # post""", r"""
Module - ROOT 0,0..1,5
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i  # post
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: # post
""", r"""i""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i  # post""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: # post""", r"""i""", r"""
Module - ROOT 0,0..1,12
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i ;
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
if 1:

""", r"""i""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i ;""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
if 1:""", r"""i""", r"""
Module - ROOT 0,0..1,5
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i ;  # post
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
if 1: # post
""", r"""i""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i ;  # post""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
if 1: # post""", r"""i""", r"""
Module - ROOT 0,0..1,12
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i ;  # post
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: # post
""", r"""i""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: i ;  # post""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: # post""", r"""i""", r"""
Module - ROOT 0,0..1,12
  .body[1]
  0] If - 1,0..1,5
    .test Constant 1 - 1,3..1,4
""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
if 1: pass

# pre
j
""", r"""pass""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] If - 1,0..1,10
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
  1] Expr - 4,0..4,1
    .value Name 'j' Load - 4,0..4,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': True, 'postcomms': False, 'pep8space': False}, r"""
if 1: pass

j
""", r"""pass""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] If - 1,0..1,10
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
  1] Expr - 3,0..3,1
    .value Name 'j' Load - 3,0..3,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
if 1: pass
j
""", r"""pass""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] If - 1,0..1,10
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
if 1: pass

# pre
else: pass
j
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
if 1: pass

# pre
j
""", r"""pass""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] If - 1,0..1,10
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
  1] Expr - 4,0..4,1
    .value Name 'j' Load - 4,0..4,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
if 1: pass

# pre
else: pass  # post
j
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
if 1: pass
# post
j
""", r"""pass""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] If - 1,0..1,10
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
  1] Expr - 3,0..3,1
    .value Name 'j' Load - 3,0..3,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
if 1: pass

# pre
else: pass  # post
j
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': True, 'postcomms': True, 'pep8space': False, 'prespace': True}, r"""
if 1: pass
j
""", r"""pass  # post
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] If - 1,0..1,10
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass

# pre
finally: pass
j
""", 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass

# pre
j
""", r"""pass""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Try - 1,0..1,9
    .body[1]
    0] Pass - 1,5..1,9
  1] Expr - 4,0..4,1
    .value Name 'j' Load - 4,0..4,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass

# pre
finally: pass
j
""", 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'precomms': True, 'postcomms': False, 'pep8space': False}, r"""
try: pass

j
""", r"""pass""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Try - 1,0..1,9
    .body[1]
    0] Pass - 1,5..1,9
  1] Expr - 3,0..3,1
    .value Name 'j' Load - 3,0..3,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass

# pre
finally: pass
j
""", 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
try: pass
j
""", r"""pass""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Try - 1,0..1,9
    .body[1]
    0] Pass - 1,5..1,9
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass

# pre
finally: pass
j
""", 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
try: pass

# pre
j
""", r"""pass""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Try - 1,0..1,9
    .body[1]
    0] Pass - 1,5..1,9
  1] Expr - 4,0..4,1
    .value Name 'j' Load - 4,0..4,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass

# pre
finally: pass  # post
j
""", 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'precomms': True, 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
try: pass
# post
j
""", r"""pass""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Try - 1,0..1,9
    .body[1]
    0] Pass - 1,5..1,9
  1] Expr - 3,0..3,1
    .value Name 'j' Load - 3,0..3,1
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass

# pre
finally: pass  # post
j
""", 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'precomms': True, 'postcomms': True, 'pep8space': False, 'prespace': True}, r"""
try: pass
j
""", r"""pass  # post
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Try - 1,0..1,9
    .body[1]
    0] Pass - 1,5..1,9
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
if 1: i

# pre-else 1

# pre-else 2
else:

  # pre 1

  # pre 2
  j
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': 'all', 'postcomms': False, 'pep8space': False}, r"""
if 1: i

""", r"""# pre 1

# pre 2
j""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..1,7
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 1,6..1,7
      .value Name 'i' Load - 1,6..1,7
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 3,0..3,1
    .value Name 'j' Load - 3,0..3,1
"""),

(r"""
if 1: i

# pre-else 1

# pre-else 2
else:

  # pre 1

  # pre 2
  j
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': 'all', 'postcomms': False, 'pep8space': False, 'prespace': True}, r"""
if 1: i
""", r"""# pre 1

# pre 2
j""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 1,0..1,7
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 1,6..1,7
      .value Name 'i' Load - 1,6..1,7
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 3,0..3,1
    .value Name 'j' Load - 3,0..3,1
"""),

(r"""
try:
    pass
finally: pass
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try:
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Try - 1,0..2,13
    .finalbody[1]
    0] Pass - 2,9..2,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass
finally: pass
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try:
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Try - 1,0..2,13
    .finalbody[1]
    0] Pass - 2,9..2,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: i = \
  2
finally: pass
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try:
finally: pass
""", r"""i = \
2""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Try - 1,0..2,13
    .finalbody[1]
    0] Pass - 2,9..2,13
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Assign - 0,0..1,1
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value Constant 2 - 1,0..1,1
"""),

(r"""
try: pass  # post
finally: pass
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try:
finally: pass
""", r"""pass  # post
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Try - 1,0..2,13
    .finalbody[1]
    0] Pass - 2,9..2,13
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass  # post
finally: pass
""", 'body[0]', 0, 1, None, {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: # post
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Try - 1,0..2,13
    .finalbody[1]
    0] Pass - 2,9..2,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass
except: pass
else:
    pass
finally: pass
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try: pass
except: pass
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] Try - 1,0..3,13
    .body[1]
    0] Pass - 1,5..1,9
    .handlers[1]
    0] ExceptHandler - 2,0..2,12
      .body[1]
      0] Pass - 2,8..2,12
    .finalbody[1]
    0] Pass - 3,9..3,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass
except: pass
else: pass
finally: pass
""", 'body[0]', 0, 1, 'orelse', {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try: pass
except: pass
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] Try - 1,0..3,13
    .body[1]
    0] Pass - 1,5..1,9
    .handlers[1]
    0] ExceptHandler - 2,0..2,12
      .body[1]
      0] Pass - 2,8..2,12
    .finalbody[1]
    0] Pass - 3,9..3,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass
except:
    pass
else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try: pass
else: pass
finally: pass
""", r"""except:
    pass""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] Try - 1,0..3,13
    .body[1]
    0] Pass - 1,5..1,9
    .orelse[1]
    0] Pass - 2,6..2,10
    .finalbody[1]
    0] Pass - 3,9..3,13
""", r"""
Module - ROOT 0,0..1,8
  .body[1]
  0] ExceptHandler - 0,0..1,8
    .body[1]
    0] Pass - 1,4..1,8
"""),

(r"""
try: pass
except: pass
else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try: pass
else: pass
finally: pass
""", r"""except: pass""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] Try - 1,0..3,13
    .body[1]
    0] Pass - 1,5..1,9
    .orelse[1]
    0] Pass - 2,6..2,10
    .finalbody[1]
    0] Pass - 3,9..3,13
""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] ExceptHandler - 0,0..0,12
    .body[1]
    0] Pass - 0,8..0,12
"""),

(r"""
try: pass
except: pass  # post
else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass
# post
else: pass
finally: pass
""", r"""except: pass""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] Try - 1,0..4,13
    .body[1]
    0] Pass - 1,5..1,9
    .orelse[1]
    0] Pass - 3,6..3,10
    .finalbody[1]
    0] Pass - 4,9..4,13
""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] ExceptHandler - 0,0..0,12
    .body[1]
    0] Pass - 0,8..0,12
"""),

(r"""
try: pass
except: pass  \

else: pass
finally: pass
""", 'body[0]', 0, 1, 'handlers', {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass
\

else: pass
finally: pass
""", r"""except: pass""", r"""
Module - ROOT 0,0..6,0
  .body[1]
  0] Try - 1,0..5,13
    .body[1]
    0] Pass - 1,5..1,9
    .orelse[1]
    0] Pass - 4,6..4,10
    .finalbody[1]
    0] Pass - 5,9..5,13
""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] ExceptHandler - 0,0..0,12
    .body[1]
    0] Pass - 0,8..0,12
"""),

(r"""
try: pass
except:
    pass
else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try: pass
except:
else: pass
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] Try - 1,0..4,13
    .body[1]
    0] Pass - 1,5..1,9
    .handlers[1]
    0] ExceptHandler - 2,0..2,7
    .orelse[1]
    0] Pass - 3,6..3,10
    .finalbody[1]
    0] Pass - 4,9..4,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass
except: pass
else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, {'_verify': False, 'precomms': True, 'postcomms': True}, r"""
try: pass
except:
else: pass
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] Try - 1,0..4,13
    .body[1]
    0] Pass - 1,5..1,9
    .handlers[1]
    0] ExceptHandler - 2,0..2,7
    .orelse[1]
    0] Pass - 3,6..3,10
    .finalbody[1]
    0] Pass - 4,9..4,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass
except: pass  # post
else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass
except: # post
else: pass
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] Try - 1,0..4,13
    .body[1]
    0] Pass - 1,5..1,9
    .handlers[1]
    0] ExceptHandler - 2,0..2,7
    .orelse[1]
    0] Pass - 3,6..3,10
    .finalbody[1]
    0] Pass - 4,9..4,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
try: pass
except: pass \

else: pass
finally: pass
""", 'body[0].handlers[0]', 0, 1, None, {'_verify': False, 'precomms': False, 'postcomms': False, 'pep8space': False}, r"""
try: pass
except: \

else: pass
finally: pass
""", r"""pass""", r"""
Module - ROOT 0,0..6,0
  .body[1]
  0] Try - 1,0..5,13
    .body[1]
    0] Pass - 1,5..1,9
    .handlers[1]
    0] ExceptHandler - 2,0..2,7
    .orelse[1]
    0] Pass - 4,6..4,10
    .finalbody[1]
    0] Pass - 5,9..5,13
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Pass - 0,0..0,4
"""),

(r"""
if type in ('d', 'D'): cmd = 'TYPE A'; isdir = 1
else: cmd = 'TYPE ' + type; isdir = 0
""", 'body[0]', 0, 2, None, {'_verify': False}, r"""
if type in ('d', 'D'):
else: cmd = 'TYPE ' + type; isdir = 0
""", r"""cmd = 'TYPE A'; isdir = 1""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,37
    .test Compare - 1,3..1,21
      .left Name 'type' Load - 1,3..1,7
      .ops[1]
      0] In - 1,8..1,10
      .comparators[1]
      0] Tuple - 1,11..1,21
        .elts[2]
        0] Constant 'd' - 1,12..1,15
        1] Constant 'D' - 1,17..1,20
        .ctx Load
    .orelse[2]
    0] Assign - 2,6..2,26
      .targets[1]
      0] Name 'cmd' Store - 2,6..2,9
      .value BinOp - 2,12..2,26
        .left Constant 'TYPE ' - 2,12..2,19
        .op Add - 2,20..2,21
        .right Name 'type' Load - 2,22..2,26
    1] Assign - 2,28..2,37
      .targets[1]
      0] Name 'isdir' Store - 2,28..2,33
      .value Constant 0 - 2,36..2,37
""", r"""
Module - ROOT 0,0..0,25
  .body[2]
  0] Assign - 0,0..0,14
    .targets[1]
    0] Name 'cmd' Store - 0,0..0,3
    .value Constant 'TYPE A' - 0,6..0,14
  1] Assign - 0,16..0,25
    .targets[1]
    0] Name 'isdir' Store - 0,16..0,21
    .value Constant 1 - 0,24..0,25
"""),

(r"""
if type in ('d', 'D'): cmd = 'TYPE A'
else: cmd = 'TYPE ' + type; isdir = 0
""", 'body[0]', 0, 2, None, {'_verify': False}, r"""
if type in ('d', 'D'):
else: cmd = 'TYPE ' + type; isdir = 0
""", r"""cmd = 'TYPE A'""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,37
    .test Compare - 1,3..1,21
      .left Name 'type' Load - 1,3..1,7
      .ops[1]
      0] In - 1,8..1,10
      .comparators[1]
      0] Tuple - 1,11..1,21
        .elts[2]
        0] Constant 'd' - 1,12..1,15
        1] Constant 'D' - 1,17..1,20
        .ctx Load
    .orelse[2]
    0] Assign - 2,6..2,26
      .targets[1]
      0] Name 'cmd' Store - 2,6..2,9
      .value BinOp - 2,12..2,26
        .left Constant 'TYPE ' - 2,12..2,19
        .op Add - 2,20..2,21
        .right Name 'type' Load - 2,22..2,26
    1] Assign - 2,28..2,37
      .targets[1]
      0] Name 'isdir' Store - 2,28..2,33
      .value Constant 0 - 2,36..2,37
""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Assign - 0,0..0,14
    .targets[1]
    0] Name 'cmd' Store - 0,0..0,3
    .value Constant 'TYPE A' - 0,6..0,14
"""),

(r"""[
    a, b,
    c
]""", 'body[0].value', 1, 3, None, {}, r"""[
    a
]""", r"""[b,
    c
]""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[1]
      0] Name 'a' Load - 1,4..1,5
      .ctx Load
""", r"""
List - ROOT 0,0..2,1
  .elts[2]
  0] Name 'b' Load - 0,1..0,2
  1] Name 'c' Load - 1,4..1,5
  .ctx Load
"""),

(r"""[
    a,
    b, c
]""", 'body[0].value', 0, 2, None, {}, r"""[
    c
]""", r"""[
    a,
    b]""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[1]
      0] Name 'c' Load - 1,4..1,5
      .ctx Load
""", r"""
List - ROOT 0,0..2,6
  .elts[2]
  0] Name 'a' Load - 1,4..1,5
  1] Name 'b' Load - 2,4..2,5
  .ctx Load
"""),

]  # END OF GET_SLICE_STMTISH_DATA

PUT_SLICE_EXPRISH_DATA = [
(r"""{
    a: 1
}""", 'body[0].value', 0, 1, r"""{}""", r"""
{
}
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value Dict - 0,0..1,1
"""),

(r"""1, 2""", 'body[0].value', 0, 2, r"""(

   )""", r"""
()
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
"""),

(r"""if 1:
  {1, 2}""", 'body[0].body[0].value', 0, 2, r"""(

   )""", r"""
if 1:
  {*()}
""", r"""
Module - ROOT 0,0..1,7
  .body[1]
  0] If - 0,0..1,7
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..1,7
      .value Set - 1,2..1,7
        .elts[1]
        0] Starred - 1,3..1,6
          .value Tuple - 1,4..1,6
            .ctx Load
          .ctx Load
"""),

(r"""{
    a: 1
}""", 'body[0].value', 0, 1, r"""{
}""", r"""
{
}
""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value Dict - 0,0..1,1
"""),

(r"""{a: 1}""", 'body[0].value', 0, 1, r"""{}""", r"""
{}
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Dict - 0,0..0,2
"""),

(r"""{a: 1}""", 'body[0].value', 0, 1, r"""{
}""", r"""
{}
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Dict - 0,0..0,2
"""),

(r"""(1, 2)""", 'body[0].value', 1, 2, r"""()""", r"""
(1,)
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Tuple - 0,0..0,4
      .elts[1]
      0] Constant 1 - 0,1..0,2
      .ctx Load
"""),

(r"""1, 2""", 'body[0].value', 1, 2, r"""()""", r"""
1,
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Constant 1 - 0,0..0,1
      .ctx Load
"""),

(r"""1, 2""", 'body[0].value', 0, 2, r"""()""", r"""
()
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
"""),

(r"""(1, 2)""", 'body[0].value', 1, 2, r"""{*()}""", r"""
(1,)
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Tuple - 0,0..0,4
      .elts[1]
      0] Constant 1 - 0,1..0,2
      .ctx Load
"""),

(r"""1, 2""", 'body[0].value', 1, 2, r"""{*()}""", r"""
1,
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Constant 1 - 0,0..0,1
      .ctx Load
"""),

(r"""1, 2""", 'body[0].value', 0, 2, r"""{*()}""", r"""
()
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
"""),

(r"""[            # hello
    1, 2, 3
]""", 'body[0].value', 0, 2, r"""()""", r"""
[            # hello
    3
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[1]
      0] Constant 3 - 1,4..1,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 1 - 2,4..2,5
      2] Name 'c' Load - 2,7..2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[
    1]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 0, 1, r"""[2]""", r"""
[            # hello
    2, b, c
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 2 - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 1, 2, r"""[2]""", r"""
[            # hello
    a, 2, c
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[2]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 3 - 1,4..1,5
      1] Name 'b' Load - 2,4..2,5
      2] Name 'c' Load - 2,7..2,8
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      2] Name 'c' Load - 2,4..2,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 1 - 2,4..2,5
      2] Name 'c' Load - 2,7..2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[
    1]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 0, 1, r"""[2]""", r"""
[            # hello
    2, b, c,
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 2 - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 1, 2, r"""[2]""", r"""
[            # hello
    a, 2, c,
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[2]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 3 - 1,4..1,5
      1] Name 'b' Load - 2,4..2,5
      2] Name 'c' Load - 2,7..2,8
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      2] Name 'c' Load - 2,4..2,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 1 - 2,4..2,5
      2] Name 'c' Load - 2,7..2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 0, 1, r"""[2,]""", r"""
[            # hello
    2, b, c
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 2 - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 1, 2, r"""[2,]""", r"""
[            # hello
    a, 2, c
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[2,]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 3 - 1,4..1,5
      1] Name 'b' Load - 2,4..2,5
      2] Name 'c' Load - 2,7..2,8
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      2] Name 'c' Load - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c
]""", 'body[0].value', 2, 3, r"""[3,
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 1 - 2,4..2,5
      2] Name 'c' Load - 2,7..2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 0, 1, r"""[2,]""", r"""
[            # hello
    2, b, c,
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 2 - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 1, 2, r"""[2,]""", r"""
[            # hello
    a, 2, c,
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Name 'c' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[2,]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 3 - 1,4..1,5
      1] Name 'b' Load - 2,4..2,5
      2] Name 'c' Load - 2,7..2,8
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      2] Name 'c' Load - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c,
]""", 'body[0].value', 2, 3, r"""[3,
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[
    1]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[2]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[2,]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b, c  # blah
]""", 'body[0].value', 2, 3, r"""[3,
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Name 'a' Load - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 1 - 2,4..2,5
      2] Name 'b' Load - 2,7..2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[
    1]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 0, 0, r"""[2]""", r"""
[            # hello
    2, a, b
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 2 - 1,4..1,5
      1] Name 'a' Load - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 1, 1, r"""[2]""", r"""
[            # hello
    a, 2, b
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[2]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 3 - 1,4..1,5
      1] Name 'a' Load - 2,4..2,5
      2] Name 'b' Load - 2,7..2,8
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      2] Name 'b' Load - 2,4..2,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Name 'a' Load - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 1 - 2,4..2,5
      2] Name 'b' Load - 2,7..2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[
    1]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 0, 0, r"""[2]""", r"""
[            # hello
    2, a, b,
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 2 - 1,4..1,5
      1] Name 'a' Load - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 1, 1, r"""[2]""", r"""
[            # hello
    a, 2, b,
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[2]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 3 - 1,4..1,5
      1] Name 'a' Load - 2,4..2,5
      2] Name 'b' Load - 2,7..2,8
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      2] Name 'b' Load - 2,4..2,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Name 'a' Load - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 1 - 2,4..2,5
      2] Name 'b' Load - 2,7..2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 0, 0, r"""[2,]""", r"""
[            # hello
    2, a, b
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 2 - 1,4..1,5
      1] Name 'a' Load - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 1, 1, r"""[2,]""", r"""
[            # hello
    a, 2, b
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[2,]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 3 - 1,4..1,5
      1] Name 'a' Load - 2,4..2,5
      2] Name 'b' Load - 2,7..2,8
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      2] Name 'b' Load - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b
]""", 'body[0].value', 2, 2, r"""[3,
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 1 - 1,4..1,5
      1] Name 'a' Load - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 1 - 2,4..2,5
      2] Name 'b' Load - 2,7..2,8
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 0, 0, r"""[2,]""", r"""
[            # hello
    2, a, b,
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Constant 2 - 1,4..1,5
      1] Name 'a' Load - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 1, 1, r"""[2,]""", r"""
[            # hello
    a, 2, b,
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 2 - 1,7..1,8
      2] Name 'b' Load - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[2,]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Constant 3 - 1,4..1,5
      1] Name 'a' Load - 2,4..2,5
      2] Name 'b' Load - 2,7..2,8
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Constant 3 - 1,7..1,8
      2] Name 'b' Load - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b,
]""", 'body[0].value', 2, 2, r"""[3,
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[
    1]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[2]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[
    1,]""", r"""
[            # hello
    a, b,
    1
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[2,]""", r"""
[            # hello
    a, b, 2
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
      .ctx Load
"""),

(r"""[            # hello
    a, b  # blah
]""", 'body[0].value', 2, 2, r"""[3,
]""", r"""
[            # hello
    a, b, 3
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 1 - 2,4..2,5
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 2 - 1,10..1,11
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
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[3]
      0] Name 'a' Load - 1,4..1,5
      1] Name 'b' Load - 1,7..1,8
      2] Constant 3 - 1,10..1,11
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
                'call "stream.close()" explicitly.'), i: j
}
""", r"""
Module - ROOT 0,0..4,1
  .body[1]
  0] Expr - 0,0..4,1
    .value Dict - 0,0..4,1
      .keys[2]
      0] Constant 'message' - 1,4..1,13
      1] Name 'i' Load - 3,54..3,55
      .values[2]
      0] Constant 'An open stream was garbage collected prior to establishing network connection; call "stream.close()" explicitly.' - 1,16..3,51
      1] Name 'j' Load - 3,57..3,58
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
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value Dict - 0,0..3,1
      .keys[3]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      2] Constant 5 - 2,14..2,15
      .values[3]
      0] Constant 2 - 1,7..1,8
      1] Constant '4' - 2,8..2,11
      2] Constant 6 - 2,17..2,18
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
Module - ROOT 0,0..4,1
  .body[1]
  0] Expr - 0,0..4,1
    .value List - 0,0..4,1
      .elts[4]
      0] Constant 'file, line (\\\\d+)' - 2,4..2,24
      1] Constant 1 - 3,4..3,5
      2] Constant 2 - 3,7..3,8
      3] Constant 3 - 3,10..3,11
      .ctx Load
"""),

(r"""(IndexError, KeyError, isinstance,)""", 'body[0].value', 2, 3, r"""()""", r"""
(IndexError, KeyError)
""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value Tuple - 0,0..0,22
      .elts[2]
      0] Name 'IndexError' Load - 0,1..0,11
      1] Name 'KeyError' Load - 0,13..0,21
      .ctx Load
"""),

(r"""[a, b] = c""", 'body[0].targets[0]', 2, 2, r"""(d,)""", r"""
[a, b, d] = c
""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Assign - 0,0..0,13
    .targets[1]
    0] List - 0,0..0,9
      .elts[3]
      0] Name 'a' Store - 0,1..0,2
      1] Name 'b' Store - 0,4..0,5
      2] Name 'd' Store - 0,7..0,8
      .ctx Store
    .value Name 'c' Load - 0,12..0,13
"""),

(r"""stat_list,""", 'body[0].value', 0, 1, r"""[ {-1: "stdname",
                   2: "cumulative"}[field[0]] ]""", r"""
{-1: "stdname",
                   2: "cumulative"}[field[0]],
""", r"""
Module - ROOT 0,0..1,46
  .body[1]
  0] Expr - 0,0..1,46
    .value Tuple - 0,0..1,46
      .elts[1]
      0] Subscript - 0,0..1,45
        .value Dict - 0,0..1,35
          .keys[2]
          0] UnaryOp - 0,1..0,3
            .op USub - 0,1..0,2
            .operand Constant 1 - 0,2..0,3
          1] Constant 2 - 1,19..1,20
          .values[2]
          0] Constant 'stdname' - 0,5..0,14
          1] Constant 'cumulative' - 1,22..1,34
        .slice Subscript - 1,36..1,44
          .value Name 'field' Load - 1,36..1,41
          .slice Constant 0 - 1,42..1,43
          .ctx Load
        .ctx Load
      .ctx Load
"""),

(r"""for a in a, b:
    pass""", 'body[0].iter', 1, 2, r"""(
c,)""", r"""
for a in (a,
c):
    pass
""", r"""
Module - ROOT 0,0..2,8
  .body[1]
  0] For - 0,0..2,8
    .target Name 'a' Store - 0,4..0,5
    .iter Tuple - 0,9..1,2
      .elts[2]
      0] Name 'a' Load - 0,10..0,11
      1] Name 'c' Load - 1,0..1,1
      .ctx Load
    .body[1]
    0] Pass - 2,4..2,8
"""),

(r"""result = filename, headers""", 'body[0].value', 0, 0, r"""(
c,)""", r"""
result = (
c, filename, headers)
""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Assign - 0,0..1,21
    .targets[1]
    0] Name 'result' Store - 0,0..0,6
    .value Tuple - 0,9..1,21
      .elts[3]
      0] Name 'c' Load - 1,0..1,1
      1] Name 'filename' Load - 1,3..1,11
      2] Name 'headers' Load - 1,13..1,20
      .ctx Load
"""),

(r"""return (user if delim else None), host""", 'body[0].value', 0, 2, r"""()""", r"""
return ()
""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Return - 0,0..0,9
    .value Tuple - 0,7..0,9
      .ctx Load
"""),

(r"""{1, 2}""", 'body[0].value', 0, 2, r"""()""", r"""
{*()}
""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Set - 0,0..0,5
      .elts[1]
      0] Starred - 0,1..0,4
        .value Tuple - 0,2..0,4
          .ctx Load
        .ctx Load
"""),

(r"""{*()}""", 'body[0].value', 0, 0, r"""()""", r"""
{*()}
""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Set - 0,0..0,5
      .elts[1]
      0] Starred - 0,1..0,4
        .value Tuple - 0,2..0,4
          .ctx Load
        .ctx Load
"""),

(r"""{*()}""", 'body[0].value', 0, 0, r"""(1, 2)""", r"""
{1, 2, *()}
""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Set - 0,0..0,11
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 2 - 0,4..0,5
      2] Starred - 0,7..0,10
        .value Tuple - 0,8..0,10
          .ctx Load
        .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 0, r"""a,""", r"""
a, 1, 2, 3,
""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Tuple - 0,0..0,11
      .elts[4]
      0] Name 'a' Load - 0,0..0,1
      1] Constant 1 - 0,3..0,4
      2] Constant 2 - 0,6..0,7
      3] Constant 3 - 0,9..0,10
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 1, r"""a,""", r"""
1, a, 2, 3,
""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Tuple - 0,0..0,11
      .elts[4]
      0] Constant 1 - 0,0..0,1
      1] Name 'a' Load - 0,3..0,4
      2] Constant 2 - 0,6..0,7
      3] Constant 3 - 0,9..0,10
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 2, r"""a,""", r"""
1, 2, a, 3,
""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Tuple - 0,0..0,11
      .elts[4]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Name 'a' Load - 0,6..0,7
      3] Constant 3 - 0,9..0,10
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 3, 3, r"""a,""", r"""
1, 2, 3, a
""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Tuple - 0,0..0,10
      .elts[4]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      3] Name 'a' Load - 0,9..0,10
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 1, r"""a,""", r"""
a, 2, 3,
""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Tuple - 0,0..0,8
      .elts[3]
      0] Name 'a' Load - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 2, r"""a,""", r"""
1, a, 3,
""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Tuple - 0,0..0,8
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Name 'a' Load - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 3, r"""a,""", r"""
1, 2, a
""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Tuple - 0,0..0,7
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Name 'a' Load - 0,6..0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 2, r"""a,""", r"""
a, 3,
""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Tuple - 0,0..0,5
      .elts[2]
      0] Name 'a' Load - 0,0..0,1
      1] Constant 3 - 0,3..0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 3, r"""a,""", r"""
1, a
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Tuple - 0,0..0,4
      .elts[2]
      0] Constant 1 - 0,0..0,1
      1] Name 'a' Load - 0,3..0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 3, r"""a,""", r"""
a,
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Name 'a' Load - 0,0..0,1
      .ctx Load
"""),

(r"""[            # hello
    1, 2, 3
]""", 'body[0].value', 0, 2, r"""**DEL**""", r"""
[            # hello
    3
]
""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value List - 0,0..2,1
      .elts[1]
      0] Constant 3 - 1,4..1,5
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 0, r"""**DEL**""", r"""
1, 2, 3,
""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Tuple - 0,0..0,8
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 1, r"""**DEL**""", r"""
1, 2, 3,
""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Tuple - 0,0..0,8
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 2, r"""**DEL**""", r"""
1, 2, 3,
""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Tuple - 0,0..0,8
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 3, 3, r"""**DEL**""", r"""
1, 2, 3,
""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Tuple - 0,0..0,8
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      2] Constant 3 - 0,6..0,7
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 1, r"""**DEL**""", r"""
2, 3,
""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Tuple - 0,0..0,5
      .elts[2]
      0] Constant 2 - 0,0..0,1
      1] Constant 3 - 0,3..0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 2, r"""**DEL**""", r"""
1, 3,
""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Tuple - 0,0..0,5
      .elts[2]
      0] Constant 1 - 0,0..0,1
      1] Constant 3 - 0,3..0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 2, 3, r"""**DEL**""", r"""
1, 2
""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Tuple - 0,0..0,4
      .elts[2]
      0] Constant 1 - 0,0..0,1
      1] Constant 2 - 0,3..0,4
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 2, r"""**DEL**""", r"""
3,
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Constant 3 - 0,0..0,1
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 1, 3, r"""**DEL**""", r"""
1,
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .elts[1]
      0] Constant 1 - 0,0..0,1
      .ctx Load
"""),

(r"""1, 2, 3,""", 'body[0].value', 0, 3, r"""**DEL**""", r"""
()
""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
"""),

(r"""if 1:
  [1,  [
        2, 3, 4]]""", 'body[0].body[0].value.elts[1]', 1, 2, r"""[5,
]""", r"""
if 1:
  [1,  [
        2, 5,
        4]]
""", r"""
Module - ROOT 0,0..3,11
  .body[1]
  0] If - 0,0..3,11
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..3,11
      .value List - 1,2..3,11
        .elts[2]
        0] Constant 1 - 1,3..1,4
        1] List - 1,7..3,10
          .elts[3]
          0] Constant 2 - 2,8..2,9
          1] Constant 5 - 2,11..2,12
          2] Constant 4 - 3,8..3,9
          .ctx Load
        .ctx Load
"""),

(r"""if 1:
  [1,  [
        2,
        3, 4]]""", 'body[0].body[0].value.elts[1]', 2, 3, r"""[5,
]""", r"""
if 1:
  [1,  [
        2,
        3, 5
       ]]
""", r"""
Module - ROOT 0,0..4,9
  .body[1]
  0] If - 0,0..4,9
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..4,9
      .value List - 1,2..4,9
        .elts[2]
        0] Constant 1 - 1,3..1,4
        1] List - 1,7..4,8
          .elts[3]
          0] Constant 2 - 2,8..2,9
          1] Constant 3 - 3,8..3,9
          2] Constant 5 - 3,11..3,12
          .ctx Load
        .ctx Load
"""),

(r"""if 1:
  [1,  [
        2, 3, 4]]""", 'body[0].body[0].value.elts[1]', 0, 2, r"""[5,
]""", r"""
if 1:
  [1,  [
        5,
        4]]
""", r"""
Module - ROOT 0,0..3,11
  .body[1]
  0] If - 0,0..3,11
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..3,11
      .value List - 1,2..3,11
        .elts[2]
        0] Constant 1 - 1,3..1,4
        1] List - 1,7..3,10
          .elts[2]
          0] Constant 5 - 2,8..2,9
          1] Constant 4 - 3,8..3,9
          .ctx Load
        .ctx Load
"""),

(r"""if 1:
  [1,  [
        2,
        3, 4]]""", 'body[0].body[0].value.elts[1]', 0, 3, r"""[5,
]""", r"""
if 1:
  [1,  [
        5
       ]]
""", r"""
Module - ROOT 0,0..3,9
  .body[1]
  0] If - 0,0..3,9
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..3,9
      .value List - 1,2..3,9
        .elts[2]
        0] Constant 1 - 1,3..1,4
        1] List - 1,7..3,8
          .elts[1]
          0] Constant 5 - 2,8..2,9
          .ctx Load
        .ctx Load
"""),

(r"""if 1:
  [1,  [
        2,
        3, 4],
   6]""", 'body[0].body[0].value.elts[1]', 0, 3, r"""[5,
]""", r"""
if 1:
  [1,  [
        5
       ],
   6]
""", r"""
Module - ROOT 0,0..4,5
  .body[1]
  0] If - 0,0..4,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..4,5
      .value List - 1,2..4,5
        .elts[3]
        0] Constant 1 - 1,3..1,4
        1] List - 1,7..3,8
          .elts[1]
          0] Constant 5 - 2,8..2,9
          .ctx Load
        2] Constant 6 - 4,3..4,4
        .ctx Load
"""),

(r"""if 1:
  [1,  [
    2,
    3, 4],
   6]""", 'body[0].body[0].value.elts[1]', 1, 3, r"""[5,
]""", r"""
if 1:
  [1,  [
    2,
    5
    ],
   6]
""", r"""
Module - ROOT 0,0..5,5
  .body[1]
  0] If - 0,0..5,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..5,5
      .value List - 1,2..5,5
        .elts[3]
        0] Constant 1 - 1,3..1,4
        1] List - 1,7..4,5
          .elts[2]
          0] Constant 2 - 2,4..2,5
          1] Constant 5 - 3,4..3,5
          .ctx Load
        2] Constant 6 - 5,3..5,4
        .ctx Load
"""),

(r"""if 1:
  [1,  {
        2:2, 3:3, 4:4}]""", 'body[0].body[0].value.elts[1]', 1, 2, r"""{5:5,
}""", r"""
if 1:
  [1,  {
        2:2, 5:5,
        4:4}]
""", r"""
Module - ROOT 0,0..3,13
  .body[1]
  0] If - 0,0..3,13
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..3,13
      .value List - 1,2..3,13
        .elts[2]
        0] Constant 1 - 1,3..1,4
        1] Dict - 1,7..3,12
          .keys[3]
          0] Constant 2 - 2,8..2,9
          1] Constant 5 - 2,13..2,14
          2] Constant 4 - 3,8..3,9
          .values[3]
          0] Constant 2 - 2,10..2,11
          1] Constant 5 - 2,15..2,16
          2] Constant 4 - 3,10..3,11
        .ctx Load
"""),

(r"""if 1:
  [1,  {
        2:2,
        3:3, 4:4}]""", 'body[0].body[0].value.elts[1]', 2, 3, r"""{5:5,
}""", r"""
if 1:
  [1,  {
        2:2,
        3:3, 5:5
       }]
""", r"""
Module - ROOT 0,0..4,9
  .body[1]
  0] If - 0,0..4,9
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..4,9
      .value List - 1,2..4,9
        .elts[2]
        0] Constant 1 - 1,3..1,4
        1] Dict - 1,7..4,8
          .keys[3]
          0] Constant 2 - 2,8..2,9
          1] Constant 3 - 3,8..3,9
          2] Constant 5 - 3,13..3,14
          .values[3]
          0] Constant 2 - 2,10..2,11
          1] Constant 3 - 3,10..3,11
          2] Constant 5 - 3,15..3,16
        .ctx Load
"""),

(r"""if 1:
  [1,  {
        2:2, 3:3, 4:4}]""", 'body[0].body[0].value.elts[1]', 0, 2, r"""{5:5,
}""", r"""
if 1:
  [1,  {
        5:5,
        4:4}]
""", r"""
Module - ROOT 0,0..3,13
  .body[1]
  0] If - 0,0..3,13
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..3,13
      .value List - 1,2..3,13
        .elts[2]
        0] Constant 1 - 1,3..1,4
        1] Dict - 1,7..3,12
          .keys[2]
          0] Constant 5 - 2,8..2,9
          1] Constant 4 - 3,8..3,9
          .values[2]
          0] Constant 5 - 2,10..2,11
          1] Constant 4 - 3,10..3,11
        .ctx Load
"""),

(r"""if 1:
  [1,  {
        2:2,
        3:3, 4:4}]""", 'body[0].body[0].value.elts[1]', 0, 3, r"""{5:5,
}""", r"""
if 1:
  [1,  {
        5:5
       }]
""", r"""
Module - ROOT 0,0..3,9
  .body[1]
  0] If - 0,0..3,9
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..3,9
      .value List - 1,2..3,9
        .elts[2]
        0] Constant 1 - 1,3..1,4
        1] Dict - 1,7..3,8
          .keys[1]
          0] Constant 5 - 2,8..2,9
          .values[1]
          0] Constant 5 - 2,10..2,11
        .ctx Load
"""),

(r"""if 1:
  [1,  {
        2:2,
        3:3, 4:4},
   6]""", 'body[0].body[0].value.elts[1]', 0, 3, r"""{5:5,
}""", r"""
if 1:
  [1,  {
        5:5
       },
   6]
""", r"""
Module - ROOT 0,0..4,5
  .body[1]
  0] If - 0,0..4,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..4,5
      .value List - 1,2..4,5
        .elts[3]
        0] Constant 1 - 1,3..1,4
        1] Dict - 1,7..3,8
          .keys[1]
          0] Constant 5 - 2,8..2,9
          .values[1]
          0] Constant 5 - 2,10..2,11
        2] Constant 6 - 4,3..4,4
        .ctx Load
"""),

(r"""if 1:
  [1,  {
    2:2,
    3:3, 4:4},
   6]""", 'body[0].body[0].value.elts[1]', 1, 3, r"""{5:5,
}""", r"""
if 1:
  [1,  {
    2:2,
    5:5
    },
   6]
""", r"""
Module - ROOT 0,0..5,5
  .body[1]
  0] If - 0,0..5,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,2..5,5
      .value List - 1,2..5,5
        .elts[3]
        0] Constant 1 - 1,3..1,4
        1] Dict - 1,7..4,5
          .keys[2]
          0] Constant 2 - 2,4..2,5
          1] Constant 5 - 3,4..3,5
          .values[2]
          0] Constant 2 - 2,6..2,7
          1] Constant 5 - 3,6..3,7
        2] Constant 6 - 5,3..5,4
        .ctx Load
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', 1, 2, r"""**DEL**""", r"""
[
    1,
    3,
]
""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value List - 0,0..3,1
      .elts[2]
      0] Constant 1 - 1,4..1,5
      1] Constant 3 - 2,4..2,5
      .ctx Load
"""),

(r"""[
    1,
    2,
    3,
]""", 'body[0].value', 1, 2, r"""[e,
    None]""", r"""
[
    1,
    e,
    None,
    3,
]
""", r"""
Module - ROOT 0,0..5,1
  .body[1]
  0] Expr - 0,0..5,1
    .value List - 0,0..5,1
      .elts[4]
      0] Constant 1 - 1,4..1,5
      1] Name 'e' Load - 2,4..2,5
      2] Constant None - 3,4..3,8
      3] Constant 3 - 4,4..4,5
      .ctx Load
"""),

(r"""Tuple[(r & ((1 << 32) - 1)), (r & ((1 << 32) - 1))]""", 'body[0].value.slice', 1, 2, r"""()""", r"""
Tuple[(r & ((1 << 32) - 1)),]
""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] Expr - 0,0..0,29
    .value Subscript - 0,0..0,29
      .value Name 'Tuple' Load - 0,0..0,5
      .slice Tuple - 0,6..0,28
        .elts[1]
        0] BinOp - 0,7..0,26
          .left Name 'r' Load - 0,7..0,8
          .op BitAnd - 0,9..0,10
          .right BinOp - 0,12..0,25
            .left BinOp - 0,13..0,20
              .left Constant 1 - 0,13..0,14
              .op LShift - 0,15..0,17
              .right Constant 32 - 0,18..0,20
            .op Sub - 0,22..0,23
            .right Constant 1 - 0,24..0,25
        .ctx Load
      .ctx Load
"""),

(r"""match a:
    case list([({-0-0j: int(real=0+0j, imag=0-0j) | 1 |
                  (g, b) | (1) as z},)]): pass""", 'body[0].cases[0].pattern.patterns[0].patterns[0].patterns[0].patterns[0].pattern', 0, 2, r"""**DEL**""", r"""
match a:
    case list([({-0-0j: 
                  (g, b) | (1) as z},)]): pass
""", r"""
Module - ROOT 0,0..2,46
  .body[1]
  0] Match - 0,0..2,46
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,4..2,46
      .pattern MatchClass - 1,9..2,40
        .cls Name 'list' Load - 1,9..1,13
        .patterns[1]
        0] MatchSequence - 1,14..2,39
          .patterns[1]
          0] MatchSequence - 1,15..2,38
            .patterns[1]
            0] MatchMapping - 1,16..2,36
              .keys[1]
              0] BinOp - 1,17..1,22
                .left UnaryOp - 1,17..1,19
                  .op USub - 1,17..1,18
                  .operand Constant 0 - 1,18..1,19
                .op Sub - 1,19..1,20
                .right Constant 0j - 1,20..1,22
              .patterns[1]
              0] MatchAs - 2,18..2,35
                .pattern MatchOr - 2,18..2,30
                  .patterns[2]
                  0] MatchSequence - 2,18..2,24
                    .patterns[2]
                    0] MatchAs - 2,19..2,20
                      .name 'g'
                    1] MatchAs - 2,22..2,23
                      .name 'b'
                  1] MatchValue - 2,28..2,29
                    .value Constant 1 - 2,28..2,29
                .name 'z'
      .body[1]
      0] Pass - 2,42..2,46
"""),

]  # END OF PUT_SLICE_EXPRISH_DATA

PUT_SLICE_STMTISH_DATA = [
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
    2] Expr - 5,4..5,5
      .value Name 'j' Load - 5,4..5,5
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 5,4..5,5
      .value Name 'j' Load - 5,4..5,5
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 5,4..5,5
      .value Name 'j' Load - 5,4..5,5
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
Module - ROOT 0,0..10,0
  .body[1]
  0] If - 1,0..9,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 9,4..9,5
      .value Name 'j' Load - 9,4..9,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
"""),

(r"""
if 1: i ; j
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
    j
""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,9
    .test Constant 1 - 1,3..1,4
    .body[5]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 2,8..2,9
      .value Name 'j' Load - 2,8..2,9
    2] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    3] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    4] Expr - 4,8..4,9
      .value Name 'm' Load - 4,8..4,9
"""),

(r"""
if 1: i ; j ; l ; m
""", 'body[0]', 2, 2, 'body', {}, r"""k""", r"""
if 1:
    i ; j
    k
    l ; m
""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,9
    .test Constant 1 - 1,3..1,4
    .body[5]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 2,8..2,9
      .value Name 'j' Load - 2,8..2,9
    2] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    3] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    4] Expr - 4,8..4,9
      .value Name 'm' Load - 4,8..4,9
"""),

(r"""
if 1:
    i
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
"""),

(r"""
if 1:
    i  # post
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i  # post
    k
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
"""),

(r"""
if 1: i
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i
    k
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
"""),

(r"""
if 1: i  # post
""", 'body[0]', 1, 1, 'body', {}, r"""k""", r"""
if 1:
    i  # post
    k
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
"""),

(r"""
if 1:
    i
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:
    k
    i
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
"""),

(r"""
if 1:  # post-block
    i
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:  # post-block
    k
    i
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'i' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'i' Load - 4,4..4,5
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    1] Expr - 5,4..5,5
      .value Name 'i' Load - 5,4..5,5
"""),

(r"""
if 1: i ; j  # post-multi
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:
    k
    i ; j  # post-multi
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,9
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
    2] Expr - 3,8..3,9
      .value Name 'j' Load - 3,8..3,9
"""),

(r"""
if 1: \
  i ; j  # post-multi
""", 'body[0]', 0, 0, 'body', {}, r"""k""", r"""
if 1:
    k
    i ; j  # post-multi
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,9
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
    2] Expr - 3,8..3,9
      .value Name 'j' Load - 3,8..3,9
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
Module - ROOT 0,0..5,0
  .body[1]
  0] FunctionDef - 1,0..4,17
    .name 'f'
    .body[1]
    0] If - 2,4..4,17
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 3,8..3,12
      .orelse[1]
      0] If - 4,4..4,17
        .test Constant 2 - 4,9..4,10
        .body[1]
        0] Break - 4,12..4,17
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..5,17
    .name 'f'
    .body[1]
    0] If - 2,4..5,17
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 3,8..3,12
      .orelse[1]
      0] If - 5,4..5,17
        .test Constant 2 - 5,9..5,10
        .body[1]
        0] Break - 5,12..5,17
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
Module - ROOT 0,0..10,0
  .body[1]
  0] FunctionDef - 1,0..8,16
    .name 'f'
    .body[1]
    0] If - 2,4..8,16
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 3,8..3,12
      .orelse[1]
      0] If - 5,4..8,16
        .test Constant 2 - 5,9..5,10
        .body[1]
        0] Break - 5,12..5,17
        .orelse[1]
        0] If - 7,4..8,16
          .test Constant 3 - 7,9..7,10
          .body[1]
          0] Continue - 8,8..8,16
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..3,12
    .name 'f'
    .body[1]
    0] If - 2,4..3,12
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 3,8..3,12
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
Module - ROOT 0,0..6,0
  .body[1]
  0] FunctionDef - 1,0..3,12
    .name 'f'
    .body[1]
    0] If - 2,4..3,12
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 3,8..3,12
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
Module - ROOT 0,0..6,0
  .body[1]
  0] FunctionDef - 1,0..3,12
    .name 'f'
    .body[1]
    0] If - 2,4..3,12
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 3,8..3,12
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
Module - ROOT 0,0..5,0
  .body[1]
  0] FunctionDef - 1,0..3,12
    .name 'f'
    .body[1]
    0] If - 2,4..3,12
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 3,8..3,12
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
Module - ROOT 0,0..8,0
  .body[1]
  0] FunctionDef - 1,0..5,17
    .name 'f'
    .body[1]
    0] If - 2,4..5,17
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 3,8..3,12
      .orelse[1]
      0] If - 5,4..5,17
        .test Constant 2 - 5,9..5,10
        .body[1]
        0] Break - 5,12..5,17
"""),

(r"""""", None, 0, 0, None, {}, r"""i""", r"""i
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
"""),

(r"""
""", None, 0, 0, None, {}, r"""i""", r"""
i
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
"""),

(r"""

""", None, 0, 0, None, {}, r"""i""", r"""

i
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Expr - 2,0..2,1
    .value Name 'i' Load - 2,0..2,1
"""),

(r"""
# comment
""", None, 0, 0, None, {}, r"""i""", r"""
# comment
i
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Expr - 2,0..2,1
    .value Name 'i' Load - 2,0..2,1
"""),

(r"""

# comment

# another comment
""", None, 0, 0, None, {}, r"""i""", r"""

# comment

# another comment
i
""", r"""
Module - ROOT 0,0..6,0
  .body[1]
  0] Expr - 5,0..5,1
    .value Name 'i' Load - 5,0..5,1
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
Module - ROOT 0,0..7,0
  .body[2]
  0] Expr - 5,0..5,1
    .value Name 'h' Load - 5,0..5,1
  1] Expr - 6,0..6,1
    .value Name 'i' Load - 6,0..6,1
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
Module - ROOT 0,0..7,0
  .body[2]
  0] Expr - 5,0..5,1
    .value Name 'i' Load - 5,0..5,1
  1] Expr - 6,0..6,1
    .value Name 'j' Load - 6,0..6,1
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
Module - ROOT 0,0..6,0
  .body[1]
  0] FunctionDef - 1,0..5,18
    .name 'f'
    .body[1]
    0] If - 2,4..5,18
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[2]
      0] Break - 4,8..4,13
      1] If - 5,8..5,18
        .test Constant 2 - 5,11..5,12
        .body[1]
        0] Pass - 5,14..5,18
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
Module - ROOT 0,0..6,0
  .body[1]
  0] FunctionDef - 1,0..5,13
    .name 'f'
    .body[1]
    0] If - 2,4..5,13
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[2]
      0] If - 4,8..4,18
        .test Constant 2 - 4,11..4,12
        .body[1]
        0] Pass - 4,14..4,18
      1] Break - 5,8..5,13
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..6,16
    .name 'f'
    .body[1]
    0] If - 2,4..6,16
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[2]
      0] Break - 4,8..4,13
      1] If - 5,8..6,16
        .test Constant 2 - 5,11..5,12
        .body[1]
        0] Pass - 6,12..6,16
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..6,13
    .name 'f'
    .body[1]
    0] If - 2,4..6,13
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[2]
      0] If - 4,8..5,16
        .test Constant 2 - 4,11..4,12
        .body[1]
        0] Pass - 5,12..5,16
      1] Break - 6,8..6,13
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..6,21
    .name 'f'
    .body[1]
    0] If - 2,4..6,21
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[2]
      0] Break - 4,8..4,13
      1] If - 5,8..6,21
        .test Constant 2 - 5,11..5,12
        .body[1]
        0] Continue - 5,14..5,22
        .orelse[1]
        0] If - 6,8..6,21
          .test Constant 3 - 6,13..6,14
          .body[1]
          0] Raise - 6,16..6,21
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..6,13
    .name 'f'
    .body[1]
    0] If - 2,4..6,13
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[2]
      0] If - 4,8..5,21
        .test Constant 2 - 4,11..4,12
        .body[1]
        0] Continue - 4,14..4,22
        .orelse[1]
        0] If - 5,8..5,21
          .test Constant 3 - 5,13..5,14
          .body[1]
          0] Raise - 5,16..5,21
      1] Break - 6,8..6,13
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..6,19
    .name 'f'
    .body[1]
    0] If - 2,4..6,19
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 3,4..6,19
        .test Constant 2 - 3,9..3,10
        .body[1]
        0] Continue - 3,12..3,20
        .orelse[2]
        0] Break - 5,8..5,13
        1] If - 6,8..6,19
          .test Constant 3 - 6,11..6,12
          .body[1]
          0] Raise - 6,14..6,19
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..6,13
    .name 'f'
    .body[1]
    0] If - 2,4..6,13
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 3,4..6,13
        .test Constant 2 - 3,9..3,10
        .body[1]
        0] Continue - 3,12..3,20
        .orelse[2]
        0] If - 5,8..5,19
          .test Constant 3 - 5,11..5,12
          .body[1]
          0] Raise - 5,14..5,19
        1] Break - 6,8..6,13
"""),

(r"""
def f():
    i
""", 'body[0]', 0, 0, None, {}, r"""# comment""", r"""
def f():
    # comment
    i
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 1,0..3,5
    .name 'f'
    .body[1]
    0] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
"""),

(r"""
def f():
    i
""", 'body[0]', 1, 1, None, {}, r"""# comment""", r"""
def f():
    i
    # comment
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 1,0..2,5
    .name 'f'
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
"""),

(r"""
def f():
    i ; j
""", 'body[0]', 0, 0, None, {}, r"""# comment""", r"""
def f():
    # comment
    i ; j
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 1,0..3,9
    .name 'f'
    .body[2]
    0] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
    1] Expr - 3,8..3,9
      .value Name 'j' Load - 3,8..3,9
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
Module - ROOT 0,0..5,0
  .body[1]
  0] FunctionDef - 1,0..4,5
    .name 'f'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
"""),

(r"""
def f():
    i ; j
""", 'body[0]', 2, 2, None, {}, r"""# comment""", r"""
def f():
    i ; j
    # comment
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 1,0..2,9
    .name 'f'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 2,8..2,9
      .value Name 'j' Load - 2,8..2,9
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..6,3
    .name 'f'
    .body[2]
    0] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
    1] Expr - 6,2..6,3
      .value Name 'j' Load - 6,2..6,3
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
Module - ROOT 0,0..5,0
  .body[1]
  0] FunctionDef - 1,0..4,5
    .name 'f'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..5,3
    .name 'f'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 5,2..5,3
      .value Name 'j' Load - 5,2..5,3
"""),

(r"""""", '', 0, 0, None, {'pep8space': True}, r"""def func(): pass""", r"""def func(): pass
""", r"""
Module - ROOT 0,0..1,0
  .body[1]
  0] FunctionDef - 0,0..0,16
    .name 'func'
    .body[1]
    0] Pass - 0,12..0,16
"""),

(r"""""", '', 0, 0, None, {'pep8space': True}, r"""
def func(): pass""", r"""
def func(): pass
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
"""),

(r"""'''Module
   docstring'''""", '', 1, 1, None, {'pep8space': True}, r"""def func(): pass""", r"""'''Module
   docstring'''

def func(): pass
""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..1,15
    .value Constant 'Module\n   docstring' - 0,0..1,15
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
"""),

(r"""'''Module
   docstring'''""", '', 1, 1, None, {'pep8space': True}, r"""def func(): pass""", r"""'''Module
   docstring'''

def func(): pass
""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..1,15
    .value Constant 'Module\n   docstring' - 0,0..1,15
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
"""),

(r"""'''Module
   docstring'''""", '', 1, 1, None, {'pep8space': True}, r"""
def func(): pass""", r"""'''Module
   docstring'''

def func(): pass
""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..1,15
    .value Constant 'Module\n   docstring' - 0,0..1,15
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
"""),

(r"""'''Module
   docstring'''""", '', 1, 1, None, {'pep8space': True}, r"""

def func(): pass""", r"""'''Module
   docstring'''


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 0,0..1,15
    .value Constant 'Module\n   docstring' - 0,0..1,15
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': True}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': 1}, r"""def func(): pass""", r"""
def prefunc(): pass

def func(): pass
""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def func(): pass""", r"""
def prefunc(): pass
def func(): pass
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 2,0..2,16
    .name 'func'
    .body[1]
    0] Pass - 2,12..2,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': True}, r"""
def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': 1}, r"""
def func(): pass""", r"""
def prefunc(): pass

def func(): pass
""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def func(): pass""", r"""
def prefunc(): pass
def func(): pass
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 2,0..2,16
    .name 'func'
    .body[1]
    0] Pass - 2,12..2,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': True}, r"""

def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': 1}, r"""

def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {'pep8space': True}, r"""


def func(): pass""", r"""
def prefunc(): pass



def func(): pass
""", r"""
Module - ROOT 0,0..6,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 5,0..5,16
    .name 'func'
    .body[1]
    0] Pass - 5,12..5,16
"""),

(r"""
import stuff
""", '', 1, 1, None, {'pep8space': True}, r"""def func(): pass""", r"""
import stuff


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Import - 1,0..1,12
    .names[1]
    0] alias - 1,7..1,12
      .name 'stuff'
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
import stuff
""", '', 1, 1, None, {'pep8space': True}, r"""
def func(): pass""", r"""
import stuff


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Import - 1,0..1,12
    .names[1]
    0] alias - 1,7..1,12
      .name 'stuff'
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
import stuff
""", '', 1, 1, None, {'pep8space': True}, r"""

def func(): pass""", r"""
import stuff


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Import - 1,0..1,12
    .names[1]
    0] alias - 1,7..1,12
      .name 'stuff'
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
import stuff
""", '', 1, 1, None, {'pep8space': True}, r"""

def func(): pass""", r"""
import stuff


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Import - 1,0..1,12
    .names[1]
    0] alias - 1,7..1,12
      .name 'stuff'
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass""", r"""
def func(): pass


def prefunc(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
  1] FunctionDef - 4,0..4,19
    .name 'prefunc'
    .body[1]
    0] Pass - 4,15..4,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {'pep8space': 1}, r"""def func(): pass""", r"""
def func(): pass

def prefunc(): pass
""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
  1] FunctionDef - 3,0..3,19
    .name 'prefunc'
    .body[1]
    0] Pass - 3,15..3,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def func(): pass""", r"""
def func(): pass
def prefunc(): pass
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
  1] FunctionDef - 2,0..2,19
    .name 'prefunc'
    .body[1]
    0] Pass - 2,15..2,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass
""", r"""
def func(): pass


def prefunc(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
  1] FunctionDef - 4,0..4,19
    .name 'prefunc'
    .body[1]
    0] Pass - 4,15..4,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass

""", r"""
def func(): pass


def prefunc(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
  1] FunctionDef - 4,0..4,19
    .name 'prefunc'
    .body[1]
    0] Pass - 4,15..4,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass


""", r"""
def func(): pass


def prefunc(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
  1] FunctionDef - 4,0..4,19
    .name 'prefunc'
    .body[1]
    0] Pass - 4,15..4,19
"""),

(r"""
def prefunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass



""", r"""
def func(): pass



def prefunc(): pass
""", r"""
Module - ROOT 0,0..6,0
  .body[2]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
  1] FunctionDef - 5,0..5,19
    .name 'prefunc'
    .body[1]
    0] Pass - 5,15..5,19
"""),

(r"""
def prefunc(): pass
def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module - ROOT 0,0..8,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 7,0..7,20
    .name 'postfunc'
    .body[1]
    0] Pass - 7,16..7,20
"""),

(r"""
def prefunc(): pass

def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module - ROOT 0,0..8,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 7,0..7,20
    .name 'postfunc'
    .body[1]
    0] Pass - 7,16..7,20
"""),

(r"""
def prefunc(): pass


def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass


def postfunc(): pass
""", r"""
Module - ROOT 0,0..8,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 7,0..7,20
    .name 'postfunc'
    .body[1]
    0] Pass - 7,16..7,20
"""),

(r"""
def prefunc(): pass



def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass



def postfunc(): pass
""", r"""
Module - ROOT 0,0..9,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 8,0..8,20
    .name 'postfunc'
    .body[1]
    0] Pass - 8,16..8,20
"""),

(r"""
def prefunc(): pass




def postfunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass




def postfunc(): pass
""", r"""
Module - ROOT 0,0..10,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 9,0..9,20
    .name 'postfunc'
    .body[1]
    0] Pass - 9,16..9,20
"""),

(r"""
def prefunc(): pass
def postfunc(): pass
""", '', 1, 1, None, {'pep8space': 1}, r"""def func(): pass""", r"""
def prefunc(): pass

def func(): pass

def postfunc(): pass
""", r"""
Module - ROOT 0,0..6,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
  2] FunctionDef - 5,0..5,20
    .name 'postfunc'
    .body[1]
    0] Pass - 5,16..5,20
"""),

(r"""
def prefunc(): pass
def postfunc(): pass
""", '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, r"""def func(): pass""", r"""
def prefunc(): pass
def func(): pass
def postfunc(): pass
""", r"""
Module - ROOT 0,0..4,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 2,0..2,16
    .name 'func'
    .body[1]
    0] Pass - 2,12..2,16
  2] FunctionDef - 3,0..3,20
    .name 'postfunc'
    .body[1]
    0] Pass - 3,16..3,20
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
Module - ROOT 0,0..8,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 7,0..7,20
    .name 'postfunc'
    .body[1]
    0] Pass - 7,16..7,20
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
Module - ROOT 0,0..9,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 8,0..8,20
    .name 'postfunc'
    .body[1]
    0] Pass - 8,16..8,20
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
Module - ROOT 0,0..6,0
  .body[1]
  0] ClassDef - 1,0..5,20
    .name 'cls'
    .body[2]
    0] Expr - 2,4..3,19
      .value Constant 'Class\n       docstring' - 2,4..3,19
    1] FunctionDef - 5,4..5,20
      .name 'meth'
      .body[1]
      0] Pass - 5,16..5,20
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
Module - ROOT 0,0..6,0
  .body[1]
  0] ClassDef - 1,0..5,20
    .name 'cls'
    .body[2]
    0] Expr - 2,4..3,19
      .value Constant 'Class\n       docstring' - 2,4..3,19
    1] FunctionDef - 5,4..5,20
      .name 'meth'
      .body[1]
      0] Pass - 5,16..5,20
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,20
    .name 'cls'
    .body[2]
    0] Expr - 2,4..3,19
      .value Constant 'Class\n       docstring' - 2,4..3,19
    1] FunctionDef - 6,4..6,20
      .name 'meth'
      .body[1]
      0] Pass - 6,16..6,20
"""),

(r"""
class cls:
    def premeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
class cls:
    def premeth(): pass

    def meth(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,20
    .name 'cls'
    .body[2]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
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
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,20
    .name 'cls'
    .body[2]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
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
Module - ROOT 0,0..6,0
  .body[1]
  0] ClassDef - 1,0..5,20
    .name 'cls'
    .body[2]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 5,4..5,20
      .name 'meth'
      .body[1]
      0] Pass - 5,16..5,20
"""),

(r"""
class cls:
    def postmeth(): pass
""", 'body[0]', 0, 0, None, {}, r"""def meth(): pass""", r"""
class cls:
    def meth(): pass

    def postmeth(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,24
    .name 'cls'
    .body[2]
    0] FunctionDef - 2,4..2,20
      .name 'meth'
      .body[1]
      0] Pass - 2,16..2,20
    1] FunctionDef - 4,4..4,24
      .name 'postmeth'
      .body[1]
      0] Pass - 4,20..4,24
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
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,24
    .name 'cls'
    .body[2]
    0] FunctionDef - 2,4..2,20
      .name 'meth'
      .body[1]
      0] Pass - 2,16..2,20
    1] FunctionDef - 4,4..4,24
      .name 'postmeth'
      .body[1]
      0] Pass - 4,20..4,24
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
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,24
    .name 'cls'
    .body[2]
    0] FunctionDef - 2,4..2,20
      .name 'meth'
      .body[1]
      0] Pass - 2,16..2,20
    1] FunctionDef - 4,4..4,24
      .name 'postmeth'
      .body[1]
      0] Pass - 4,20..4,24
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
Module - ROOT 0,0..6,0
  .body[1]
  0] ClassDef - 1,0..5,24
    .name 'cls'
    .body[2]
    0] FunctionDef - 2,4..2,20
      .name 'meth'
      .body[1]
      0] Pass - 2,16..2,20
    1] FunctionDef - 5,4..5,24
      .name 'postmeth'
      .body[1]
      0] Pass - 5,20..5,24
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] FunctionDef - 6,4..6,24
      .name 'postmeth'
      .body[1]
      0] Pass - 6,20..6,24
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] FunctionDef - 6,4..6,24
      .name 'postmeth'
      .body[1]
      0] Pass - 6,20..6,24
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] FunctionDef - 7,4..7,24
      .name 'postmeth'
      .body[1]
      0] Pass - 7,20..7,24
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
Module - ROOT 0,0..9,0
  .body[1]
  0] ClassDef - 1,0..8,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] FunctionDef - 8,4..8,24
      .name 'postmeth'
      .body[1]
      0] Pass - 8,20..8,24
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
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 3,4..3,20
      .name 'meth'
      .body[1]
      0] Pass - 3,16..3,20
    2] FunctionDef - 4,4..4,24
      .name 'postmeth'
      .body[1]
      0] Pass - 4,20..4,24
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] FunctionDef - 7,4..7,24
      .name 'postmeth'
      .body[1]
      0] Pass - 7,20..7,24
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
Module - ROOT 0,0..9,0
  .body[1]
  0] ClassDef - 1,0..8,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 5,4..5,20
      .name 'meth'
      .body[1]
      0] Pass - 5,16..5,20
    2] FunctionDef - 8,4..8,24
      .name 'postmeth'
      .body[1]
      0] Pass - 8,20..8,24
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
Module - ROOT 0,0..10,0
  .body[1]
  0] ClassDef - 1,0..9,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] FunctionDef - 9,4..9,24
      .name 'postmeth'
      .body[1]
      0] Pass - 9,20..9,24
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 5,4..5,23
      .name 'newmeth'
      .body[1]
      0] Pass - 5,19..5,23
    2] FunctionDef - 7,4..7,24
      .name 'postmeth'
      .body[1]
      0] Pass - 7,20..7,24
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] Assign - 4,4..4,9
      .targets[1]
      0] Name 'i' Store - 4,4..4,5
      .value Constant 1 - 4,8..4,9
    2] FunctionDef - 6,4..6,24
      .name 'postmeth'
      .body[1]
      0] Pass - 6,20..6,24
"""),

(r"""
def prefunc(): pass
def postfunc(): pass
""", '', 1, 1, None, {}, r"""i = 1""", r"""
def prefunc(): pass


i = 1


def postfunc(): pass
""", r"""
Module - ROOT 0,0..8,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] Assign - 4,0..4,5
    .targets[1]
    0] Name 'i' Store - 4,0..4,1
    .value Constant 1 - 4,4..4,5
  2] FunctionDef - 7,0..7,20
    .name 'postfunc'
    .body[1]
    0] Pass - 7,16..7,20
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
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..6,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 3,0..3,1
    .value Name 'l' Load - 3,0..3,1
  2] Expr - 5,0..5,1
    .value Name 'k' Load - 5,0..5,1
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
Module - ROOT 0,0..5,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 3,0..3,1
    .value Name 'l' Load - 3,0..3,1
  2] Expr - 4,0..4,1
    .value Name 'k' Load - 4,0..4,1
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
Module - ROOT 0,0..7,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 4,0..4,1
    .value Name 'l' Load - 4,0..4,1
  2] Expr - 6,0..6,1
    .value Name 'k' Load - 6,0..6,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] If - 1,0..6,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    2] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    2] Expr - 5,4..5,5
      .value Name 'k' Load - 5,4..5,5
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
Module - ROOT 0,0..8,0
  .body[1]
  0] If - 1,0..7,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 5,4..5,5
      .value Name 'l' Load - 5,4..5,5
    2] Expr - 7,4..7,5
      .value Name 'k' Load - 7,4..7,5
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
Module - ROOT 0,0..6,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 3,0..3,1
    .value Name 'l' Load - 3,0..3,1
  2] Expr - 5,0..5,1
    .value Name 'k' Load - 5,0..5,1
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
Module - ROOT 0,0..7,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 3,0..3,1
    .value Name 'l' Load - 3,0..3,1
  2] Expr - 6,0..6,1
    .value Name 'k' Load - 6,0..6,1
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
Module - ROOT 0,0..7,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 3,0..3,1
    .value Name 'l' Load - 3,0..3,1
  2] Expr - 6,0..6,1
    .value Name 'k' Load - 6,0..6,1
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
Module - ROOT 0,0..7,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 3,0..3,1
    .value Name 'l' Load - 3,0..3,1
  2] Expr - 6,0..6,1
    .value Name 'k' Load - 6,0..6,1
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
Module - ROOT 0,0..7,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 4,0..4,1
    .value Name 'l' Load - 4,0..4,1
  2] Expr - 6,0..6,1
    .value Name 'k' Load - 6,0..6,1
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
Module - ROOT 0,0..8,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 4,0..4,1
    .value Name 'l' Load - 4,0..4,1
  2] Expr - 7,0..7,1
    .value Name 'k' Load - 7,0..7,1
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
Module - ROOT 0,0..8,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 4,0..4,1
    .value Name 'l' Load - 4,0..4,1
  2] Expr - 7,0..7,1
    .value Name 'k' Load - 7,0..7,1
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
Module - ROOT 0,0..8,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 4,0..4,1
    .value Name 'l' Load - 4,0..4,1
  2] Expr - 7,0..7,1
    .value Name 'k' Load - 7,0..7,1
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
Module - ROOT 0,0..7,0
  .body[1]
  0] If - 1,0..6,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    2] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
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
Module - ROOT 0,0..8,0
  .body[1]
  0] If - 1,0..7,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    2] Expr - 7,4..7,5
      .value Name 'k' Load - 7,4..7,5
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
Module - ROOT 0,0..8,0
  .body[1]
  0] If - 1,0..7,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    2] Expr - 7,4..7,5
      .value Name 'k' Load - 7,4..7,5
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
Module - ROOT 0,0..8,0
  .body[1]
  0] If - 1,0..7,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    2] Expr - 7,4..7,5
      .value Name 'k' Load - 7,4..7,5
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
Module - ROOT 0,0..8,0
  .body[1]
  0] If - 1,0..7,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 5,4..5,5
      .value Name 'l' Load - 5,4..5,5
    2] Expr - 7,4..7,5
      .value Name 'k' Load - 7,4..7,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] If - 1,0..8,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 5,4..5,5
      .value Name 'l' Load - 5,4..5,5
    2] Expr - 8,4..8,5
      .value Name 'k' Load - 8,4..8,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] If - 1,0..8,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 5,4..5,5
      .value Name 'l' Load - 5,4..5,5
    2] Expr - 8,4..8,5
      .value Name 'k' Load - 8,4..8,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] If - 1,0..8,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 5,4..5,5
      .value Name 'l' Load - 5,4..5,5
    2] Expr - 8,4..8,5
      .value Name 'k' Load - 8,4..8,5
"""),

(r"""
i
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
i
j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
"""),

(r"""
i
j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
"""),

(r"""
if 1:
    i
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] If - 2,0..3,8
    .test Constant 1 - 2,3..2,4
    .body[1]
    0] Pass - 3,4..3,8
  2] Expr - 4,0..4,1
    .value Name 'k' Load - 4,0..4,1
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
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] If - 2,0..2,11
    .test Constant 2 - 2,3..2,4
    .body[1]
    0] Break - 2,6..2,11
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..7,0
  .body[5]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'x' Load - 2,0..2,1
  2] If - 3,0..4,8
    .test Constant 1 - 3,3..3,4
    .body[1]
    0] Pass - 4,4..4,8
  3] Expr - 5,0..5,1
    .value Name 'z' Load - 5,0..5,1
  4] Expr - 6,0..6,1
    .value Name 'k' Load - 6,0..6,1
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
Module - ROOT 0,0..6,0
  .body[5]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'x' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'l' Load - 3,0..3,1
  3] Expr - 4,0..4,1
    .value Name 'z' Load - 4,0..4,1
  4] Expr - 5,0..5,1
    .value Name 'k' Load - 5,0..5,1
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
Module - ROOT 0,0..6,0
  .body[5]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'x' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'l' Load - 3,0..3,1
  3] Expr - 4,0..4,1
    .value Name 'z' Load - 4,0..4,1
  4] Expr - 5,0..5,1
    .value Name 'k' Load - 5,0..5,1
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
Module - ROOT 0,0..6,0
  .body[5]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'x' Load - 2,0..2,1
  2] If - 3,0..3,11
    .test Constant 2 - 3,3..3,4
    .body[1]
    0] Break - 3,6..3,11
  3] Expr - 4,0..4,1
    .value Name 'z' Load - 4,0..4,1
  4] Expr - 5,0..5,1
    .value Name 'k' Load - 5,0..5,1
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,5
    .test Constant 2 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..4,12
      .test Constant 1 - 3,7..3,8
      .body[1]
      0] Pass - 4,8..4,12
    2] Expr - 5,4..5,5
      .value Name 'k' Load - 5,4..5,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 2 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 2 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 2 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] If - 3,4..3,15
      .test Constant 2 - 3,7..3,8
      .body[1]
      0] Break - 3,10..3,15
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
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
Module - ROOT 0,0..8,0
  .body[1]
  0] If - 1,0..7,5
    .test Constant 2 - 1,3..1,4
    .body[5]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'x' Load - 3,4..3,5
    2] If - 4,4..5,12
      .test Constant 1 - 4,7..4,8
      .body[1]
      0] Pass - 5,8..5,12
    3] Expr - 6,4..6,5
      .value Name 'z' Load - 6,4..6,5
    4] Expr - 7,4..7,5
      .value Name 'k' Load - 7,4..7,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] If - 1,0..6,5
    .test Constant 2 - 1,3..1,4
    .body[5]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'x' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    3] Expr - 5,4..5,5
      .value Name 'z' Load - 5,4..5,5
    4] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] If - 1,0..6,5
    .test Constant 2 - 1,3..1,4
    .body[5]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'x' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'l' Load - 4,4..4,5
    3] Expr - 5,4..5,5
      .value Name 'z' Load - 5,4..5,5
    4] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] If - 1,0..6,5
    .test Constant 2 - 1,3..1,4
    .body[5]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'x' Load - 3,4..3,5
    2] If - 4,4..4,15
      .test Constant 2 - 4,7..4,8
      .body[1]
      0] Break - 4,10..4,15
    3] Expr - 5,4..5,5
      .value Name 'z' Load - 5,4..5,5
    4] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
"""),

(r"""
i ; j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l

""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
"""),

(r"""
i \
 ; j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l

""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
"""),

(r"""
i ; \
 j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l

""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
"""),

(r"""
i \
; \
j
""", '', 1, 2, None, {}, r"""l""", r"""
i
l

""", r"""
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
"""),

(r"""
if 1:
    i ; j
""", 'body[0]', 1, 2, None, {}, r"""l""", r"""
if 1:
    i
    l

""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
"""),

(r"""
i ; j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
"""),

(r"""
i \
 ; j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
"""),

(r"""
i ; \
 j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
"""),

(r"""
i \
; \
j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
"""),

(r"""
if 1:
    i ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
"""),

(r"""
if 1: \
    i ; j
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    j
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
"""),

(r"""
i ;
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
i ;  # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
# post
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
i ; \
 # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
i \
 ; \
 # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
if 1:
    i ;
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
"""),

(r"""
if 1:
    i ;  # post
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
    # post
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
"""),

(r"""
if 1:
    i ; \
 # post
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
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
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
"""),

(r"""
# pre
i ; \
 j
""", '', 0, 1, None, {}, r"""**DEL**""", r"""
j
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'j' Load - 1,0..1,1
"""),

(r"""
# pre
i ; \
 j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,3
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Expr - 3,2..3,3
      .value Name 'j' Load - 3,2..3,3
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,3
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[2]
    0] Expr - 4,2..4,3
      .value Name 'j' Load - 4,2..4,3
    1] Expr - 5,2..5,3
      .value Name 'k' Load - 5,2..5,3
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
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[2]
    0] Expr - 3,4..3,5
      .value Name 'k' Load - 3,4..3,5
    1] Expr - 5,4..5,5
      .value Name 'j' Load - 5,4..5,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,3
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Expr - 3,2..3,3
      .value Name 'j' Load - 3,2..3,3
"""),

(r"""
# pre
i ; j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
"""),

(r"""
# pre
i \
 ; j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
"""),

(r"""
# pre
i ; \
 j
""", '', 0, 1, None, {}, r"""l""", r"""
l
j
""", r"""
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
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
Module - ROOT 0,0..3,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'j' Load - 2,0..2,1
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,5
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'j' Load - 3,4..3,5
"""),

(r"""
# pre
i ;
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
# pre
i ;  # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
# post
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
# pre
i ; \
 # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
# pre
i \
 ; \
 # post
""", '', 0, 1, None, {}, r"""l""", r"""
l
""", r"""
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
"""),

(r"""
if 1:
    # pre
    i ;
""", 'body[0]', 0, 1, None, {}, r"""l""", r"""
if 1:
    l
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
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
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
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
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
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
Module - ROOT 0,0..8,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 7,0..7,20
    .name 'postfunc'
    .body[1]
    0] Pass - 7,16..7,20
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
Module - ROOT 0,0..8,0
  .body[3]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] FunctionDef - 7,0..7,20
    .name 'postfunc'
    .body[1]
    0] Pass - 7,16..7,20
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
Module - ROOT 0,0..9,0
  .body[4]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] Expr - 7,0..7,1
    .value Name 'j' Load - 7,0..7,1
  3] FunctionDef - 8,0..8,20
    .name 'postfunc'
    .body[1]
    0] Pass - 8,16..8,20
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
Module - ROOT 0,0..9,0
  .body[4]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] Expr - 2,0..2,1
    .value Name 'i' Load - 2,0..2,1
  2] FunctionDef - 5,0..5,16
    .name 'func'
    .body[1]
    0] Pass - 5,12..5,16
  3] FunctionDef - 8,0..8,20
    .name 'postfunc'
    .body[1]
    0] Pass - 8,16..8,20
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
Module - ROOT 0,0..9,0
  .body[4]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
  2] Expr - 7,0..7,1
    .value Name 'j' Load - 7,0..7,1
  3] FunctionDef - 8,0..8,20
    .name 'postfunc'
    .body[1]
    0] Pass - 8,16..8,20
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
Module - ROOT 0,0..10,0
  .body[4]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] Expr - 3,0..3,1
    .value Name 'i' Load - 3,0..3,1
  2] FunctionDef - 6,0..6,16
    .name 'func'
    .body[1]
    0] Pass - 6,12..6,16
  3] FunctionDef - 9,0..9,20
    .name 'postfunc'
    .body[1]
    0] Pass - 9,16..9,20
"""),

(r"""
def prefunc(): pass
""", '', 1, 1, None, {}, r"""def func(): pass""", r"""
def prefunc(): pass


def func(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,19
    .name 'prefunc'
    .body[1]
    0] Pass - 1,15..1,19
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
"""),

(r"""
def postfunc(): pass
""", '', 0, 0, None, {}, r"""def func(): pass""", r"""
def func(): pass


def postfunc(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] FunctionDef - 1,0..1,16
    .name 'func'
    .body[1]
    0] Pass - 1,12..1,16
  1] FunctionDef - 4,0..4,20
    .name 'postfunc'
    .body[1]
    0] Pass - 4,16..4,20
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] FunctionDef - 6,4..6,24
      .name 'postmeth'
      .body[1]
      0] Pass - 6,20..6,24
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,24
    .name 'cls'
    .body[3]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] FunctionDef - 6,4..6,24
      .name 'postmeth'
      .body[1]
      0] Pass - 6,20..6,24
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,24
    .name 'cls'
    .body[4]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] Expr - 6,4..6,5
      .value Name 'j' Load - 6,4..6,5
    3] FunctionDef - 7,4..7,24
      .name 'postmeth'
      .body[1]
      0] Pass - 7,20..7,24
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,24
    .name 'cls'
    .body[4]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
    2] FunctionDef - 5,4..5,20
      .name 'meth'
      .body[1]
      0] Pass - 5,16..5,20
    3] FunctionDef - 7,4..7,24
      .name 'postmeth'
      .body[1]
      0] Pass - 7,20..7,24
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,24
    .name 'cls'
    .body[4]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 4,4..4,20
      .name 'meth'
      .body[1]
      0] Pass - 4,16..4,20
    2] Expr - 6,4..6,5
      .value Name 'j' Load - 6,4..6,5
    3] FunctionDef - 7,4..7,24
      .name 'postmeth'
      .body[1]
      0] Pass - 7,20..7,24
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
Module - ROOT 0,0..9,0
  .body[1]
  0] ClassDef - 1,0..8,24
    .name 'cls'
    .body[4]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] Expr - 4,4..4,5
      .value Name 'i' Load - 4,4..4,5
    2] FunctionDef - 6,4..6,20
      .name 'meth'
      .body[1]
      0] Pass - 6,16..6,20
    3] FunctionDef - 8,4..8,24
      .name 'postmeth'
      .body[1]
      0] Pass - 8,20..8,24
"""),

(r"""
if 1:
    def premeth(): pass
""", 'body[0]', 1, 1, None, {}, r"""def meth(): pass""", r"""
if 1:
    def premeth(): pass


    def meth(): pass
""", r"""
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,20
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] FunctionDef - 2,4..2,23
      .name 'premeth'
      .body[1]
      0] Pass - 2,19..2,23
    1] FunctionDef - 5,4..5,20
      .name 'meth'
      .body[1]
      0] Pass - 5,16..5,20
"""),

(r"""
if 1:
    def postmeth(): pass
""", 'body[0]', 0, 0, None, {}, r"""def meth(): pass""", r"""
if 1:
    def meth(): pass


    def postmeth(): pass
""", r"""
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,24
    .test Constant 1 - 1,3..1,4
    .body[2]
    0] FunctionDef - 2,4..2,20
      .name 'meth'
      .body[1]
      0] Pass - 2,16..2,20
    1] FunctionDef - 5,4..5,24
      .name 'postmeth'
      .body[1]
      0] Pass - 5,20..5,24
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
Module - ROOT 0,0..7,0
  .body[1]
  0] FunctionDef - 1,0..6,5
    .name 'f'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'g'
      .body[1]
      0] Pass - 4,13..4,17
    2] Expr - 6,4..6,5
      .value Name 'j' Load - 6,4..6,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] AsyncFunctionDef - 1,0..6,5
    .name 'f'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'g'
      .body[1]
      0] Pass - 4,13..4,17
    2] Expr - 6,4..6,5
      .value Name 'j' Load - 6,4..6,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,5
    .name 'cls'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'g'
      .body[1]
      0] Pass - 4,13..4,17
    2] Expr - 6,4..6,5
      .value Name 'j' Load - 6,4..6,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] For - 1,0..8,5
    .target Name 'a' Store - 1,4..1,5
    .iter Name 'b' Load - 1,9..1,10
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'g'
      .body[1]
      0] Pass - 5,13..5,17
    2] Expr - 8,4..8,5
      .value Name 'j' Load - 8,4..8,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] AsyncFor - 1,0..8,5
    .target Name 'a' Store - 1,10..1,11
    .iter Name 'b' Load - 1,15..1,16
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'g'
      .body[1]
      0] Pass - 5,13..5,17
    2] Expr - 8,4..8,5
      .value Name 'j' Load - 8,4..8,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] While - 1,0..8,5
    .test Name 'a' Load - 1,6..1,7
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'g'
      .body[1]
      0] Pass - 5,13..5,17
    2] Expr - 8,4..8,5
      .value Name 'j' Load - 8,4..8,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] If - 1,0..8,5
    .test Name 'a' Load - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'g'
      .body[1]
      0] Pass - 5,13..5,17
    2] Expr - 8,4..8,5
      .value Name 'j' Load - 8,4..8,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] With - 1,0..8,5
    .items[1]
    0] withitem - 1,5..1,6
      .context_expr Name 'a' Load - 1,5..1,6
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'g'
      .body[1]
      0] Pass - 5,13..5,17
    2] Expr - 8,4..8,5
      .value Name 'j' Load - 8,4..8,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] AsyncWith - 1,0..8,5
    .items[1]
    0] withitem - 1,11..1,12
      .context_expr Name 'a' Load - 1,11..1,12
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'g'
      .body[1]
      0] Pass - 5,13..5,17
    2] Expr - 8,4..8,5
      .value Name 'j' Load - 8,4..8,5
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
Module - ROOT 0,0..10,0
  .body[1]
  0] Match - 1,0..9,9
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,4..9,9
      .pattern MatchAs - 2,9..2,10
        .name 'b'
      .body[3]
      0] Expr - 3,8..3,9
        .value Name 'i' Load - 3,8..3,9
      1] FunctionDef - 6,8..6,21
        .name 'g'
        .body[1]
        0] Pass - 6,17..6,21
      2] Expr - 9,8..9,9
        .value Name 'j' Load - 9,8..9,9
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
Module - ROOT 0,0..11,0
  .body[1]
  0] Try - 1,0..10,8
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'g'
      .body[1]
      0] Pass - 5,13..5,17
    2] Expr - 8,4..8,5
      .value Name 'j' Load - 8,4..8,5
    .finalbody[1]
    0] Pass - 10,4..10,8
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
Module - ROOT 0,0..5,0
  .body[1]
  0] FunctionDef - 1,0..4,5
    .name 'f'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] AsyncFunctionDef - 1,0..4,5
    .name 'f'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,5
    .name 'cls'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] For - 1,0..4,5
    .target Name 'a' Store - 1,4..1,5
    .iter Name 'b' Load - 1,9..1,10
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] AsyncFor - 1,0..4,5
    .target Name 'a' Store - 1,10..1,11
    .iter Name 'b' Load - 1,15..1,16
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] While - 1,0..4,5
    .test Name 'a' Load - 1,6..1,7
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Name 'a' Load - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] With - 1,0..4,5
    .items[1]
    0] withitem - 1,5..1,6
      .context_expr Name 'a' Load - 1,5..1,6
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] AsyncWith - 1,0..4,5
    .items[1]
    0] withitem - 1,11..1,12
      .context_expr Name 'a' Load - 1,11..1,12
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
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
Module - ROOT 0,0..6,0
  .body[1]
  0] Match - 1,0..5,9
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,4..5,9
      .pattern MatchAs - 2,9..2,10
        .name 'b'
      .body[3]
      0] Expr - 3,8..3,9
        .value Name 'i' Load - 3,8..3,9
      1] FunctionDef - 4,8..4,21
        .name 'g'
        .body[1]
        0] Pass - 4,17..4,21
      2] Expr - 5,8..5,9
        .value Name 'j' Load - 5,8..5,9
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
Module - ROOT 0,0..7,0
  .body[1]
  0] Try - 1,0..6,8
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 3,4..3,17
      .name 'g'
      .body[1]
      0] Pass - 3,13..3,17
    2] Expr - 4,4..4,5
      .value Name 'j' Load - 4,4..4,5
    .finalbody[1]
    0] Pass - 6,4..6,8
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
Module - ROOT 0,0..7,0
  .body[1]
  0] If - 1,0..6,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'g'
      .body[1]
      0] Pass - 4,13..4,17
    2] Expr - 6,4..6,5
      .value Name 'j' Load - 6,4..6,5
"""),

(r"""
i ; j ; k
""", '', 1, 2, None, {}, r"""l""", r"""
i
l
k
""", r"""
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..4,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] Expr - 2,0..2,1
    .value Name 'l' Load - 2,0..2,1
  2] Expr - 3,0..3,1
    .value Name 'k' Load - 3,0..3,1
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] Expr - 3,4..3,5
      .value Name 'l' Load - 3,4..3,5
    2] Expr - 4,4..4,5
      .value Name 'k' Load - 4,4..4,5
"""),

(r"""
i ; j ; k
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass


k
""", r"""
Module - ROOT 0,0..8,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
  2] Expr - 7,0..7,1
    .value Name 'k' Load - 7,0..7,1
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
Module - ROOT 0,0..8,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
  2] Expr - 7,0..7,1
    .value Name 'k' Load - 7,0..7,1
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
Module - ROOT 0,0..8,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
  2] Expr - 7,0..7,1
    .value Name 'k' Load - 7,0..7,1
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
Module - ROOT 0,0..8,0
  .body[3]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
  2] Expr - 7,0..7,1
    .value Name 'k' Load - 7,0..7,1
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,5
    .name 'cls'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
    2] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,5
    .name 'cls'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
    2] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,5
    .name 'cls'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
    2] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,5
    .name 'cls'
    .body[3]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
    2] Expr - 6,4..6,5
      .value Name 'k' Load - 6,4..6,5
"""),

(r"""
i ; j ;
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
"""),

(r"""
i ; \
 j \
 ;
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i ;


def f(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
"""),

(r"""
i \
 ; j ;
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i


def f(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
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
Module - ROOT 0,0..6,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 5,0..5,13
    .name 'f'
    .body[1]
    0] Pass - 5,9..5,13
"""),

(r"""
class cls:
    i ; j ;
""", 'body[0]', 1, 2, None, {}, r"""def f(): pass""", r"""
class cls:
    i

    def f(): pass
""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,17
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
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
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,17
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
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
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,17
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
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
Module - ROOT 0,0..6,0
  .body[1]
  0] ClassDef - 1,0..5,17
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'f'
      .body[1]
      0] Pass - 5,13..5,17
"""),

(r"""
i ; j ;  # post
""", '', 1, 2, None, {}, r"""def f(): pass""", r"""
i ;


def f(): pass
# post
""", r"""
Module - ROOT 0,0..6,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
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
Module - ROOT 0,0..6,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
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
Module - ROOT 0,0..7,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 5,0..5,13
    .name 'f'
    .body[1]
    0] Pass - 5,9..5,13
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
Module - ROOT 0,0..7,0
  .body[2]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
  1] FunctionDef - 5,0..5,13
    .name 'f'
    .body[1]
    0] Pass - 5,9..5,13
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
Module - ROOT 0,0..6,0
  .body[1]
  0] ClassDef - 1,0..4,17
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
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
Module - ROOT 0,0..6,0
  .body[1]
  0] ClassDef - 1,0..4,17
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 4,4..4,17
      .name 'f'
      .body[1]
      0] Pass - 4,13..4,17
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..5,17
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'f'
      .body[1]
      0] Pass - 5,13..5,17
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
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..5,17
    .name 'cls'
    .body[2]
    0] Expr - 2,4..2,5
      .value Name 'i' Load - 2,4..2,5
    1] FunctionDef - 5,4..5,17
      .name 'f'
      .body[1]
      0] Pass - 5,13..5,17
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
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,9
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Break - 3,4..3,9
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0]', 0, 1, 'orelse', {'elif_': False}, r"""if 3: break""", r"""
if 1: pass
else:
    if 3: break
""", r"""
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 1,0..3,15
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 3,4..3,15
      .test Constant 3 - 3,7..3,8
      .body[1]
      0] Break - 3,10..3,15
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break""", r"""
if 1: pass
elif 3: break
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,13
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 2,0..2,13
      .test Constant 3 - 2,5..2,6
      .body[1]
      0] Break - 2,8..2,13
"""),

(r"""
if 1: pass
else:
    pass
""", 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, r"""if 3: break""", r"""
if 1: pass
elif 3: break
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,13
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 2,0..2,13
      .test Constant 3 - 2,5..2,6
      .body[1]
      0] Break - 2,8..2,13
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
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,13
    .name 'cls'
    .body[1]
    0] If - 2,4..4,13
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] Break - 4,8..4,13
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 0, 1, 'orelse', {'elif_': False}, r"""if 3: break""", r"""
class cls:
    if 1: pass
    else:
        if 3: break
""", r"""
Module - ROOT 0,0..5,0
  .body[1]
  0] ClassDef - 1,0..4,19
    .name 'cls'
    .body[1]
    0] If - 2,4..4,19
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 4,8..4,19
        .test Constant 3 - 4,11..4,12
        .body[1]
        0] Break - 4,14..4,19
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
Module - ROOT 0,0..4,0
  .body[1]
  0] ClassDef - 1,0..3,17
    .name 'cls'
    .body[1]
    0] If - 2,4..3,17
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 3,4..3,17
        .test Constant 3 - 3,9..3,10
        .body[1]
        0] Break - 3,12..3,17
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
Module - ROOT 0,0..4,0
  .body[1]
  0] ClassDef - 1,0..3,17
    .name 'cls'
    .body[1]
    0] If - 2,4..3,17
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 3,4..3,17
        .test Constant 3 - 3,9..3,10
        .body[1]
        0] Break - 3,12..3,17
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0]', 0, 1, 'orelse', {'elif_': False}, r"""if 3: break
else:
    continue""", r"""
if 1: pass
else:
    if 3: break
    else:
        continue
""", r"""
Module - ROOT 0,0..6,0
  .body[1]
  0] If - 1,0..5,16
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 3,4..5,16
      .test Constant 3 - 3,7..3,8
      .body[1]
      0] Break - 3,10..3,15
      .orelse[1]
      0] Continue - 5,8..5,16
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,12
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 2,0..4,12
      .test Constant 3 - 2,5..2,6
      .body[1]
      0] Break - 2,8..2,13
      .orelse[1]
      0] Continue - 4,4..4,12
"""),

(r"""
if 1: pass
elif 2:
    pass
""", 'body[0].orelse[0]', 0, 0, 'orelse', {'elif_': False}, r"""if 3: break
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
Module - ROOT 0,0..8,0
  .body[1]
  0] If - 1,0..7,16
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 2,0..7,16
      .test Constant 2 - 2,5..2,6
      .body[1]
      0] Pass - 3,4..3,8
      .orelse[1]
      0] If - 5,4..7,16
        .test Constant 3 - 5,7..5,8
        .body[1]
        0] Break - 5,10..5,15
        .orelse[1]
        0] Continue - 7,8..7,16
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
Module - ROOT 0,0..7,0
  .body[1]
  0] If - 1,0..6,12
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 2,0..6,12
      .test Constant 2 - 2,5..2,6
      .body[1]
      0] Pass - 3,4..3,8
      .orelse[1]
      0] If - 4,0..6,12
        .test Constant 3 - 4,5..4,6
        .body[1]
        0] Break - 4,8..4,13
        .orelse[1]
        0] Continue - 6,4..6,12
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0]', 0, 1, 'orelse', {'elif_': False}, r"""if 3: break
else:
    continue""", r"""
class cls:
    if 1: pass
    else:
        if 3: break
        else:
            continue
""", r"""
Module - ROOT 0,0..7,0
  .body[1]
  0] ClassDef - 1,0..6,20
    .name 'cls'
    .body[1]
    0] If - 2,4..6,20
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 4,8..6,20
        .test Constant 3 - 4,11..4,12
        .body[1]
        0] Break - 4,14..4,19
        .orelse[1]
        0] Continue - 6,12..6,20
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
Module - ROOT 0,0..6,0
  .body[1]
  0] ClassDef - 1,0..5,16
    .name 'cls'
    .body[1]
    0] If - 2,4..5,16
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 3,4..5,16
        .test Constant 3 - 3,9..3,10
        .body[1]
        0] Break - 3,12..3,17
        .orelse[1]
        0] Continue - 5,8..5,16
"""),

(r"""
class cls:
    if 1: pass
    elif 2:
        pass
""", 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {'elif_': False}, r"""if 3: break
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
Module - ROOT 0,0..9,0
  .body[1]
  0] ClassDef - 1,0..8,20
    .name 'cls'
    .body[1]
    0] If - 2,4..8,20
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 3,4..8,20
        .test Constant 2 - 3,9..3,10
        .body[1]
        0] Pass - 4,8..4,12
        .orelse[1]
        0] If - 6,8..8,20
          .test Constant 3 - 6,11..6,12
          .body[1]
          0] Break - 6,14..6,19
          .orelse[1]
          0] Continue - 8,12..8,20
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
Module - ROOT 0,0..8,0
  .body[1]
  0] ClassDef - 1,0..7,16
    .name 'cls'
    .body[1]
    0] If - 2,4..7,16
      .test Constant 1 - 2,7..2,8
      .body[1]
      0] Pass - 2,10..2,14
      .orelse[1]
      0] If - 3,4..7,16
        .test Constant 2 - 3,9..3,10
        .body[1]
        0] Pass - 4,8..4,12
        .orelse[1]
        0] If - 5,4..7,16
          .test Constant 3 - 5,9..5,10
          .body[1]
          0] Break - 5,12..5,17
          .orelse[1]
          0] Continue - 7,8..7,16
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
Module - ROOT 0,0..5,0
  .body[1]
  0] If - 1,0..4,5
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 2,4..2,8
    .orelse[1]
    0] Expr - 4,4..4,5
      .value Name 'i' Load - 4,4..4,5
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
Module - ROOT 0,0..9,0
  .body[1]
  0] Try - 1,0..8,8
    .body[1]
    0] Continue - 2,4..2,12
    .handlers[1]
    0] ExceptHandler - 3,0..4,9
      .body[1]
      0] Pass - 4,4..4,8
    .orelse[1]
    0] Expr - 6,4..6,5
      .value Name 'i' Load - 6,4..6,5
    .finalbody[1]
    0] Pass - 8,4..8,8
"""),

]  # END OF PUT_SLICE_STMTISH_DATA

PUT_SLICE_DATA = [
(r"""(1, 2, 3)""", 'body[0].value', 1, 2, None, {'raw': True}, r"""*z""", r"""(1, *z, 3)""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Tuple - 0,0..0,10
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Starred - 0,4..0,6
        .value Name 'z' Load - 0,5..0,6
        .ctx Load
      2] Constant 3 - 0,8..0,9
      .ctx Load
"""),

(r"""(1, 2, 3)""", 'body[0].value', 0, 3, None, {'raw': True}, r"""*z,""", r"""(*z,)""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Tuple - 0,0..0,5
      .elts[1]
      0] Starred - 0,1..0,3
        .value Name 'z' Load - 0,2..0,3
        .ctx Load
      .ctx Load
"""),

(r"""1, 2, 3""", 'body[0].value', 1, 2, None, {'raw': True}, r"""*z""", r"""1, *z, 3""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Tuple - 0,0..0,8
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Starred - 0,3..0,5
        .value Name 'z' Load - 0,4..0,5
        .ctx Load
      2] Constant 3 - 0,7..0,8
      .ctx Load
"""),

(r"""1, 2, 3""", 'body[0].value', 0, 3, None, {'raw': True}, r"""*z,""", r"""*z,""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value Tuple - 0,0..0,3
      .elts[1]
      0] Starred - 0,0..0,2
        .value Name 'z' Load - 0,1..0,2
        .ctx Load
      .ctx Load
"""),

(r"""{a: b, c: d, e: f}""", 'body[0].value', 1, 2, None, {'raw': True}, r"""**z""", r"""{a: b, **z, e: f}""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Dict - 0,0..0,17
      .keys[3]
      0] Name 'a' Load - 0,1..0,2
      1] None
      2] Name 'e' Load - 0,12..0,13
      .values[3]
      0] Name 'b' Load - 0,4..0,5
      1] Name 'z' Load - 0,9..0,10
      2] Name 'f' Load - 0,15..0,16
"""),

(r"""{a: b, c: d, e: f}""", 'body[0].value', 0, 3, None, {'raw': True}, r"""**z""", r"""{**z}""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Dict - 0,0..0,5
      .keys[1]
      0] None
      .values[1]
      0] Name 'z' Load - 0,3..0,4
"""),

(r"""{a: b, **c, **d, **e}""", 'body[0].value', 1, 3, None, {'raw': True}, r"""f: g""", r"""{a: b, f: g, **e}""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Dict - 0,0..0,17
      .keys[3]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'f' Load - 0,7..0,8
      2] None
      .values[3]
      0] Name 'b' Load - 0,4..0,5
      1] Name 'g' Load - 0,10..0,11
      2] Name 'e' Load - 0,15..0,16
"""),

(r"""del a, b, c""", 'body[0]', 1, 3, None, {'raw': True}, r"""z""", r"""del a, z""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Delete - 0,0..0,8
    .targets[2]
    0] Name 'a' Del - 0,4..0,5
    1] Name 'z' Del - 0,7..0,8
"""),

(r"""a = b = c = d""", 'body[0]', 1, 3, 'targets', {'raw': True}, r"""z""", r"""a = z = d""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Assign - 0,0..0,9
    .targets[2]
    0] Name 'a' Store - 0,0..0,1
    1] Name 'z' Store - 0,4..0,5
    .value Name 'd' Load - 0,8..0,9
"""),

(r"""import a, b, c""", 'body[0]', 1, 3, None, {'raw': True}, r"""z as xyz""", r"""import a, z as xyz""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Import - 0,0..0,18
    .names[2]
    0] alias - 0,7..0,8
      .name 'a'
    1] alias - 0,10..0,18
      .name 'z'
      .asname
        'xyz'
"""),

(r"""from mod import a, b, c""", 'body[0]', 1, 3, None, {'raw': True}, r"""z as xyz""", r"""from mod import a, z as xyz""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] ImportFrom - 0,0..0,27
    .module 'mod'
    .names[2]
    0] alias - 0,16..0,17
      .name 'a'
    1] alias - 0,19..0,27
      .name 'z'
      .asname
        'xyz'
    .level 0
"""),

(r"""with a as a, b as b, c as c: pass""", 'body[0]', 1, 3, 'items', {'raw': True}, r"""z as xyz""", r"""with a as a, z as xyz: pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] With - 0,0..0,27
    .items[2]
    0] withitem - 0,5..0,11
      .context_expr Name 'a' Load - 0,5..0,6
      .optional_vars Name 'a' Store - 0,10..0,11
    1] withitem - 0,13..0,21
      .context_expr Name 'z' Load - 0,13..0,14
      .optional_vars Name 'xyz' Store - 0,18..0,21
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""a and b and c""", 'body[0].value', 1, 3, None, {'raw': True}, r"""z""", r"""a and z""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value BoolOp - 0,0..0,7
      .op And
      .values[2]
      0] Name 'a' Load - 0,0..0,1
      1] Name 'z' Load - 0,6..0,7
"""),

(r"""a < b < c < d""", 'body[0].value', 1, 4, None, {'raw': True}, r"""x < y""", r"""a < x < y""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Compare - 0,0..0,9
      .left Name 'a' Load - 0,0..0,1
      .ops[2]
      0] Lt - 0,2..0,3
      1] Lt - 0,6..0,7
      .comparators[2]
      0] Name 'x' Load - 0,4..0,5
      1] Name 'y' Load - 0,8..0,9
"""),

(r"""[a for a in a() for b in b() for c in c()]""", 'body[0].value', 1, 3, None, {'raw': True}, r"""for z in z()""", r"""[a for a in a() for z in z()]""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] Expr - 0,0..0,29
    .value ListComp - 0,0..0,29
      .elt Name 'a' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,15
        .target Name 'a' Store - 0,7..0,8
        .iter Call - 0,12..0,15
          .func Name 'a' Load - 0,12..0,13
        .is_async 0
      1] comprehension - 0,16..0,28
        .target Name 'z' Store - 0,20..0,21
        .iter Call - 0,25..0,28
          .func Name 'z' Load - 0,25..0,26
        .is_async 0
"""),

(r"""[a for a in a() if a if b if c]""", 'body[0].value.generators[0]', 1, 3, None, {'raw': True}, r"""if z""", r"""[a for a in a() if a if z]""", r"""
Module - ROOT 0,0..0,26
  .body[1]
  0] Expr - 0,0..0,26
    .value ListComp - 0,0..0,26
      .elt Name 'a' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,25
        .target Name 'a' Store - 0,7..0,8
        .iter Call - 0,12..0,15
          .func Name 'a' Load - 0,12..0,13
        .ifs[2]
        0] Name 'a' Load - 0,19..0,20
        1] Name 'z' Load - 0,24..0,25
        .is_async 0
"""),

(r"""f(a, b, c)""", 'body[0].value', 1, 3, None, {'raw': True}, r"""z""", r"""f(a, z)""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Call - 0,0..0,7
      .func Name 'f' Load - 0,0..0,1
      .args[2]
      0] Name 'a' Load - 0,2..0,3
      1] Name 'z' Load - 0,5..0,6
"""),

(r"""f(a, b, c)""", 'body[0].value', 1, 3, None, {'raw': True}, r"""**z""", r"""f(a, **z)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Call - 0,0..0,9
      .func Name 'f' Load - 0,0..0,1
      .args[1]
      0] Name 'a' Load - 0,2..0,3
      .keywords[1]
      0] keyword - 0,5..0,8
        .value Name 'z' Load - 0,7..0,8
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
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 3,0..3,13
    .name 'f'
    .body[1]
    0] Pass - 3,9..3,13
    .decorator_list[2]
    0] Name 'a' Load - 1,1..1,2
    1] Name 'z' Load - 2,1..2,2
"""),

(r"""
match a:
  case [a, b, c]: pass
""", 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, r"""*z""", r"""
match a:
  case [a, *z]: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Match - 1,0..2,20
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,2..2,20
      .pattern MatchSequence - 2,7..2,14
        .patterns[2]
        0] MatchAs - 2,8..2,9
          .name 'a'
        1] MatchStar - 2,11..2,13
          .name 'z'
      .body[1]
      0] Pass - 2,16..2,20
"""),

(r"""
match a:
  case a | b | c: pass
""", 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, r"""z""", r"""
match a:
  case a | z: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Match - 1,0..2,18
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,2..2,18
      .pattern MatchOr - 2,7..2,12
        .patterns[2]
        0] MatchAs - 2,7..2,8
          .name 'a'
        1] MatchAs - 2,11..2,12
          .name 'z'
      .body[1]
      0] Pass - 2,14..2,18
"""),

(r"""
match a:
  case {'a': a, 'b': b, 'c': c}: pass
""", 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, r"""**z""", r"""
match a:
  case {'a': a, **z}: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Match - 1,0..2,26
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,2..2,26
      .pattern MatchMapping - 2,7..2,20
        .keys[1]
        0] Constant 'a' - 2,8..2,11
        .patterns[1]
        0] MatchAs - 2,13..2,14
          .name 'a'
        .rest 'z'
      .body[1]
      0] Pass - 2,22..2,26
"""),

(r"""def f(a): pass""", 'body[0].args', 0, 1, 'args', {'raw': True}, r"""b""", r"""def f(b): pass""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] FunctionDef - 0,0..0,14
    .name 'f'
    .args arguments - 0,6..0,7
      .args[1]
      0] arg - 0,6..0,7
        .arg 'b'
    .body[1]
    0] Pass - 0,10..0,14
"""),

(r"""def f(a): pass""", 'body[0].args', 0, 1, 'args', {'raw': True}, r"""""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""f(a)""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""(i for i in range(5))""", r"""f((i for i in range(5)))""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] Expr - 0,0..0,24
    .value Call - 0,0..0,24
      .func Name 'f' Load - 0,0..0,1
      .args[1]
      0] GeneratorExp - 0,2..0,23
        .elt Name 'i' Load - 0,3..0,4
        .generators[1]
        0] comprehension - 0,5..0,22
          .target Name 'i' Store - 0,9..0,10
          .iter Call - 0,14..0,22
            .func Name 'range' Load - 0,14..0,19
            .args[1]
            0] Constant 5 - 0,20..0,21
          .is_async 0
"""),

(r"""{1: 2, **(x), (3): (4)}""", 'body[0].value', 1, 3, None, {'raw': True}, r"""**z""", r"""{1: 2, **z}""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Dict - 0,0..0,11
      .keys[2]
      0] Constant 1 - 0,1..0,2
      1] None
      .values[2]
      0] Constant 2 - 0,4..0,5
      1] Name 'z' Load - 0,9..0,10
"""),

(r"""((a) < (b) < (c))""", 'body[0].value', 1, 3, None, {'raw': True}, r"""z""", r"""((a) < z)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Compare - 0,1..0,8
      .left Name 'a' Load - 0,2..0,3
      .ops[1]
      0] Lt - 0,5..0,6
      .comparators[1]
      0] Name 'z' Load - 0,7..0,8
"""),

(r"""(1, *(x), (3))""", 'body[0].value', 1, 3, None, {'raw': True}, r"""*z""", r"""(1, *z)""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Tuple - 0,0..0,7
      .elts[2]
      0] Constant 1 - 0,1..0,2
      1] Starred - 0,4..0,6
        .value Name 'z' Load - 0,5..0,6
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
Module - ROOT 0,0..3,0
  .body[1]
  0] Match - 1,0..2,28
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,2..2,28
      .pattern MatchMapping - 2,7..2,22
        .keys[1]
        0] Constant 'a' - 2,8..2,11
        .patterns[1]
        0] MatchAs - 2,14..2,15
          .name 'a'
        .rest 'z'
      .body[1]
      0] Pass - 2,24..2,28
"""),

(r"""[a for a in a() if (a) if (b) if (c)]""", 'body[0].value.generators[0]', 1, 3, None, {'raw': True}, r"""if z""", r"""[a for a in a() if (a) if z]""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] Expr - 0,0..0,28
    .value ListComp - 0,0..0,28
      .elt Name 'a' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,27
        .target Name 'a' Store - 0,7..0,8
        .iter Call - 0,12..0,15
          .func Name 'a' Load - 0,12..0,13
        .ifs[2]
        0] Name 'a' Load - 0,20..0,21
        1] Name 'z' Load - 0,26..0,27
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
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 3,0..3,13
    .name 'f'
    .body[1]
    0] Pass - 3,9..3,13
    .decorator_list[2]
    0] Name 'a' Load - 1,2..1,3
    1] Name 'z' Load - 2,1..2,2
"""),

(r"""((1), (2), (3))""", 'body[0].value', 1, 3, None, {'raw': True}, r"""*z""", r"""((1), *z)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Tuple - 0,0..0,9
      .elts[2]
      0] Constant 1 - 0,2..0,3
      1] Starred - 0,6..0,8
        .value Name 'z' Load - 0,7..0,8
        .ctx Load
      .ctx Load
"""),

(r"""f(i for i in range(5))""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""a""", r"""f(a)""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Call - 0,0..0,4
      .func Name 'f' Load - 0,0..0,1
      .args[1]
      0] Name 'a' Load - 0,2..0,3
"""),

(r"""f((i for i in range(5)))""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""a""", r"""f(a)""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Call - 0,0..0,4
      .func Name 'f' Load - 0,0..0,1
      .args[1]
      0] Name 'a' Load - 0,2..0,3
"""),

(r"""f(((i for i in range(5))))""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""a""", r"""f(a)""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Call - 0,0..0,4
      .func Name 'f' Load - 0,0..0,1
      .args[1]
      0] Name 'a' Load - 0,2..0,3
"""),

(r"""f((i for i in range(5)), b)""", 'body[0].value', 0, 1, 'args', {'raw': True}, r"""a""", r"""f(a, b)""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Call - 0,0..0,7
      .func Name 'f' Load - 0,0..0,1
      .args[2]
      0] Name 'a' Load - 0,2..0,3
      1] Name 'b' Load - 0,5..0,6
"""),

(r"""f((i for i in range(5)), b)""", 'body[0].value', 0, 2, 'args', {'raw': True}, r"""a""", r"""f(a)""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Call - 0,0..0,4
      .func Name 'f' Load - 0,0..0,1
      .args[1]
      0] Name 'a' Load - 0,2..0,3
"""),

(r"""global a, b, c""", 'body[0]', 0, 2, None, {'raw': True}, r"""x""", r"""global x, c""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Global - 0,0..0,11
    .names[2]
    0] 'x'
    1] 'c'
"""),

(r"""global a, b, c""", 'body[0]', None, None, None, {'raw': True}, r"""x""", r"""global x""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Global - 0,0..0,8
    .names[1]
    0] 'x'
"""),

(r"""global a, b, c""", 'body[0]', 1, 2, None, {'raw': True}, r"""x, y""", r"""global a, x, y, c""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Global - 0,0..0,17
    .names[4]
    0] 'a'
    1] 'x'
    2] 'y'
    3] 'c'
"""),

(r"""nonlocal a, b, c""", 'body[0]', 0, 2, None, {'raw': True}, r"""x""", r"""nonlocal x, c""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Nonlocal - 0,0..0,13
    .names[2]
    0] 'x'
    1] 'c'
"""),

(r"""nonlocal a, b, c""", 'body[0]', None, None, None, {'raw': True}, r"""x""", r"""nonlocal x""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Nonlocal - 0,0..0,10
    .names[1]
    0] 'x'
"""),

(r"""nonlocal a, b, c""", 'body[0]', 1, 2, None, {'raw': True}, r"""x, y""", r"""nonlocal a, x, y, c""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] Nonlocal - 0,0..0,19
    .names[4]
    0] 'a'
    1] 'x'
    2] 'y'
    3] 'c'
"""),

(r"""[a# comment
]""", 'body[0].value', 1, 1, None, {'trivia': (None, False)}, r"""b,""", r"""[a, b, # comment
]""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value List - 0,0..1,1
      .elts[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,4..0,5
      .ctx Load
"""),

(r"""[a# comment
]""", 'body[0].value', 1, 1, None, {'trivia': (None, False)}, r"""[b]""", r"""[a, b # comment
]""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value List - 0,0..1,1
      .elts[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,4..0,5
      .ctx Load
"""),

(r"""[a,  # test
]""", 'body[0].value', 1, 1, None, {'trivia': (None, False)}, r"""b,""", r"""[a, b, # test
]""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value List - 0,0..1,1
      .elts[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,4..0,5
      .ctx Load
"""),

(r"""[a,  # test
]""", 'body[0].value', 1, 1, None, {'trivia': (None, False)}, r"""[b]""", r"""[a, b # test
]""", r"""
Module - ROOT 0,0..1,1
  .body[1]
  0] Expr - 0,0..1,1
    .value List - 0,0..1,1
      .elts[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,4..0,5
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[a]""", r"""[a
# c0

# c2
]""", r"""
Module - ROOT 0,0..4,1
  .body[1]
  0] Expr - 0,0..4,1
    .value List - 0,0..4,1
      .elts[1]
      0] Name 'a' Load - 0,1..0,2
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[a]""", r"""[
a # c0

# c2
]""", r"""
Module - ROOT 0,0..4,1
  .body[1]
  0] Expr - 0,0..4,1
    .value List - 0,0..4,1
      .elts[1]
      0] Name 'a' Load - 1,0..1,1
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[a]""", r"""[
# c0
a
# c2
]""", r"""
Module - ROOT 0,0..4,1
  .body[1]
  0] Expr - 0,0..4,1
    .value List - 0,0..4,1
      .elts[1]
      0] Name 'a' Load - 2,0..2,1
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[a]""", r"""[
# c0

a # c2
]""", r"""
Module - ROOT 0,0..4,1
  .body[1]
  0] Expr - 0,0..4,1
    .value List - 0,0..4,1
      .elts[1]
      0] Name 'a' Load - 3,0..3,1
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[a]""", r"""[
# c0

# c2
a]""", r"""
Module - ROOT 0,0..4,2
  .body[1]
  0] Expr - 0,0..4,2
    .value List - 0,0..4,2
      .elts[1]
      0] Name 'a' Load - 4,0..4,1
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[
a
]""", r"""[
a
# c0

# c2
]""", r"""
Module - ROOT 0,0..5,1
  .body[1]
  0] Expr - 0,0..5,1
    .value List - 0,0..5,1
      .elts[1]
      0] Name 'a' Load - 1,0..1,1
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[
a
]""", r"""[
a
# c0

# c2
]""", r"""
Module - ROOT 0,0..5,1
  .body[1]
  0] Expr - 0,0..5,1
    .value List - 0,0..5,1
      .elts[1]
      0] Name 'a' Load - 1,0..1,1
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[
a
]""", r"""[
# c0
a
# c2
]""", r"""
Module - ROOT 0,0..4,1
  .body[1]
  0] Expr - 0,0..4,1
    .value List - 0,0..4,1
      .elts[1]
      0] Name 'a' Load - 2,0..2,1
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[
a
]""", r"""[
# c0

a
# c2
]""", r"""
Module - ROOT 0,0..5,1
  .body[1]
  0] Expr - 0,0..5,1
    .value List - 0,0..5,1
      .elts[1]
      0] Name 'a' Load - 3,0..3,1
      .ctx Load
"""),

(r"""[
# c0

# c2
]""", 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[
a
]""", r"""[
# c0

# c2
a
]""", r"""
Module - ROOT 0,0..5,1
  .body[1]
  0] Expr - 0,0..5,1
    .value List - 0,0..5,1
      .elts[1]
      0] Name 'a' Load - 4,0..4,1
      .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[a]""", r"""if 1: [a
    # c0

    # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 0,7..0,8
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[a]""", r"""if 1: [
    a # c0

    # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 1,4..1,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[a]""", r"""if 1: [
    # c0
    a
    # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 2,4..2,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[a]""", r"""if 1: [
    # c0

    a # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 3,4..3,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[a]""", r"""if 1: [
    # c0

    # c2
  a]""", r"""
Module - ROOT 0,0..4,4
  .body[1]
  0] If - 0,0..4,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,4
      .value List - 0,6..4,4
        .elts[1]
        0] Name 'a' Load - 4,2..4,3
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[
a]""", r"""if 1: [
    a
    # c0

    # c2
  ]""", r"""
Module - ROOT 0,0..5,3
  .body[1]
  0] If - 0,0..5,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,3
      .value List - 0,6..5,3
        .elts[1]
        0] Name 'a' Load - 1,4..1,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[
a]""", r"""if 1: [
    a # c0

    # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 1,4..1,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[
a]""", r"""if 1: [
    # c0
    a
    # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 2,4..2,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[
a]""", r"""if 1: [
    # c0

    a # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 3,4..3,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[
a]""", r"""if 1: [
    # c0

    # c2
    a]""", r"""
Module - ROOT 0,0..4,6
  .body[1]
  0] If - 0,0..4,6
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,6
      .value List - 0,6..4,6
        .elts[1]
        0] Name 'a' Load - 4,4..4,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[a
]""", r"""if 1: [a
    # c0

    # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 0,7..0,8
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[a
]""", r"""if 1: [
    a
    # c0

    # c2
  ]""", r"""
Module - ROOT 0,0..5,3
  .body[1]
  0] If - 0,0..5,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,3
      .value List - 0,6..5,3
        .elts[1]
        0] Name 'a' Load - 1,4..1,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[a
]""", r"""if 1: [
    # c0
    a
    # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 2,4..2,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[a
]""", r"""if 1: [
    # c0

    a
    # c2
  ]""", r"""
Module - ROOT 0,0..5,3
  .body[1]
  0] If - 0,0..5,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,3
      .value List - 0,6..5,3
        .elts[1]
        0] Name 'a' Load - 3,4..3,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[a
]""", r"""if 1: [
    # c0

    # c2
  a
  ]""", r"""
Module - ROOT 0,0..5,3
  .body[1]
  0] If - 0,0..5,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,3
      .value List - 0,6..5,3
        .elts[1]
        0] Name 'a' Load - 4,2..4,3
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[
a
]""", r"""if 1: [
    a
    # c0

    # c2
  ]""", r"""
Module - ROOT 0,0..5,3
  .body[1]
  0] If - 0,0..5,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,3
      .value List - 0,6..5,3
        .elts[1]
        0] Name 'a' Load - 1,4..1,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[
a
]""", r"""if 1: [
    a
    # c0

    # c2
  ]""", r"""
Module - ROOT 0,0..5,3
  .body[1]
  0] If - 0,0..5,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,3
      .value List - 0,6..5,3
        .elts[1]
        0] Name 'a' Load - 1,4..1,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[
a
]""", r"""if 1: [
    # c0
    a
    # c2
  ]""", r"""
Module - ROOT 0,0..4,3
  .body[1]
  0] If - 0,0..4,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,3
      .value List - 0,6..4,3
        .elts[1]
        0] Name 'a' Load - 2,4..2,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[
a
]""", r"""if 1: [
    # c0

    a
    # c2
  ]""", r"""
Module - ROOT 0,0..5,3
  .body[1]
  0] If - 0,0..5,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,3
      .value List - 0,6..5,3
        .elts[1]
        0] Name 'a' Load - 3,4..3,5
        .ctx Load
"""),

(r"""if 1: [
    # c0

    # c2
  ]""", 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[
a
]""", r"""if 1: [
    # c0

    # c2
    a
  ]""", r"""
Module - ROOT 0,0..5,3
  .body[1]
  0] If - 0,0..5,3
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,3
      .value List - 0,6..5,3
        .elts[1]
        0] Name 'a' Load - 4,4..4,5
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[a]""", r"""if 1: [x, a,
    # c0

    # c2
  y]""", r"""
Module - ROOT 0,0..4,4
  .body[1]
  0] If - 0,0..4,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,4
      .value List - 0,6..4,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 0,10..0,11
        2] Name 'y' Load - 4,2..4,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[a]""", r"""if 1: [x,
    a, # c0

    # c2
  y]""", r"""
Module - ROOT 0,0..4,4
  .body[1]
  0] If - 0,0..4,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,4
      .value List - 0,6..4,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 1,4..1,5
        2] Name 'y' Load - 4,2..4,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[a]""", r"""if 1: [x,
    # c0
    a,
    # c2
  y]""", r"""
Module - ROOT 0,0..4,4
  .body[1]
  0] If - 0,0..4,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,4
      .value List - 0,6..4,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 2,4..2,5
        2] Name 'y' Load - 4,2..4,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[a]""", r"""if 1: [x,
    # c0

    a, # c2
  y]""", r"""
Module - ROOT 0,0..4,4
  .body[1]
  0] If - 0,0..4,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,4
      .value List - 0,6..4,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 3,4..3,5
        2] Name 'y' Load - 4,2..4,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[a]""", r"""if 1: [x,
    # c0

    # c2
  a, y]""", r"""
Module - ROOT 0,0..4,7
  .body[1]
  0] If - 0,0..4,7
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,7
      .value List - 0,6..4,7
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 4,2..4,3
        2] Name 'y' Load - 4,5..4,6
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[
a
]""", r"""if 1: [x,
    a,
    # c0

    # c2
  y]""", r"""
Module - ROOT 0,0..5,4
  .body[1]
  0] If - 0,0..5,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,4
      .value List - 0,6..5,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 1,4..1,5
        2] Name 'y' Load - 5,2..5,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[
a
]""", r"""if 1: [x,
    a,
    # c0

    # c2
  y]""", r"""
Module - ROOT 0,0..5,4
  .body[1]
  0] If - 0,0..5,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,4
      .value List - 0,6..5,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 1,4..1,5
        2] Name 'y' Load - 5,2..5,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[
a
]""", r"""if 1: [x,
    # c0
    a,
    # c2
  y]""", r"""
Module - ROOT 0,0..4,4
  .body[1]
  0] If - 0,0..4,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,4
      .value List - 0,6..4,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 2,4..2,5
        2] Name 'y' Load - 4,2..4,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[
a
]""", r"""if 1: [x,
    # c0

    a,
    # c2
  y]""", r"""
Module - ROOT 0,0..5,4
  .body[1]
  0] If - 0,0..5,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,4
      .value List - 0,6..5,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 3,4..3,5
        2] Name 'y' Load - 5,2..5,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[
a
]""", r"""if 1: [x,
    # c0

    # c2
    a,
  y]""", r"""
Module - ROOT 0,0..5,4
  .body[1]
  0] If - 0,0..5,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,4
      .value List - 0,6..5,4
        .elts[3]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 4,4..4,5
        2] Name 'y' Load - 5,2..5,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, r"""[
a,
 b]""", r"""if 1: [x,
    a,
     b,
    # c0

    # c2
  y]""", r"""
Module - ROOT 0,0..6,4
  .body[1]
  0] If - 0,0..6,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..6,4
      .value List - 0,6..6,4
        .elts[4]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 1,4..1,5
        2] Name 'b' Load - 2,5..2,6
        3] Name 'y' Load - 6,2..6,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, r"""[
a,
 b]""", r"""if 1: [x,
    a,
     b, # c0

    # c2
  y]""", r"""
Module - ROOT 0,0..5,4
  .body[1]
  0] If - 0,0..5,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,4
      .value List - 0,6..5,4
        .elts[4]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 1,4..1,5
        2] Name 'b' Load - 2,5..2,6
        3] Name 'y' Load - 5,2..5,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, r"""[
a,
 b]""", r"""if 1: [x,
    # c0
    a,
     b,
    # c2
  y]""", r"""
Module - ROOT 0,0..5,4
  .body[1]
  0] If - 0,0..5,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,4
      .value List - 0,6..5,4
        .elts[4]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 2,4..2,5
        2] Name 'b' Load - 3,5..3,6
        3] Name 'y' Load - 5,2..5,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, r"""[
a,
 b]""", r"""if 1: [x,
    # c0

    a,
     b, # c2
  y]""", r"""
Module - ROOT 0,0..5,4
  .body[1]
  0] If - 0,0..5,4
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,4
      .value List - 0,6..5,4
        .elts[4]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 3,4..3,5
        2] Name 'b' Load - 4,5..4,6
        3] Name 'y' Load - 5,2..5,3
        .ctx Load
"""),

(r"""if 1: [x,
    # c0

    # c2
  y]""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, r"""[
a,
 b]""", r"""if 1: [x,
    # c0

    # c2
    a,
     b, y]""", r"""
Module - ROOT 0,0..5,10
  .body[1]
  0] If - 0,0..5,10
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..5,10
      .value List - 0,6..5,10
        .elts[4]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'a' Load - 4,4..4,5
        2] Name 'b' Load - 5,5..5,6
        3] Name 'y' Load - 5,8..5,9
        .ctx Load
"""),

(r"""if 1: {**x,
    # c0

    # c2
  **y}""", 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, r"""{**a}""", r"""if 1: {**x,
    # c0

    # c2
  **a, **y}""", r"""
Module - ROOT 0,0..4,11
  .body[1]
  0] If - 0,0..4,11
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 0,6..4,11
      .value Dict - 0,6..4,11
        .keys[3]
        0] None
        1] None
        2] None
        .values[3]
        0] Name 'x' Load - 0,9..0,10
        1] Name 'a' Load - 4,4..4,5
        2] Name 'y' Load - 4,9..4,10
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 1, None, {'matchor_del': False, '_verify': False}, r"""**DEL**""", r"""match a:
 case b: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchOr - 1,6..1,7
        .patterns[1]
        0] MatchAs - 1,6..1,7
          .name 'b'
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 2, None, {'matchor_del': False, '_verify': False}, r"""**DEL**""", r"""match a:
 case : pass""", r"""
Module - ROOT 0,0..1,12
  .body[1]
  0] Match - 0,0..1,12
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,12
      .pattern MatchOr - 1,6..1,6
      .body[1]
      0] Pass - 1,8..1,12
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 1, None, {'matchor_del': True, '_verify': False}, r"""**DEL**""", r"""match a:
 case b: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
        .name 'b'
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 2, None, {'matchor_del': True, '_verify': False}, r"""**DEL**""", r"""**NodeError('cannot del MatchOr to empty without matchor_del=False')**""", r"""
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 1, None, {'matchor_del': False, '_verify': False}, r"""z""", r"""match a:
 case z | b: pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchOr - 1,6..1,11
        .patterns[2]
        0] MatchAs - 1,6..1,7
          .name 'z'
        1] MatchAs - 1,10..1,11
          .name 'b'
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 2, None, {'matchor_del': False, '_verify': False}, r"""z""", r"""match a:
 case z: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchOr - 1,6..1,7
        .patterns[1]
        0] MatchAs - 1,6..1,7
          .name 'z'
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 1, None, {'matchor_del': True, '_verify': False}, r"""z""", r"""match a:
 case z | b: pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchOr - 1,6..1,11
        .patterns[2]
        0] MatchAs - 1,6..1,7
          .name 'z'
        1] MatchAs - 1,10..1,11
          .name 'b'
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 2, None, {'matchor_del': True, '_verify': False}, r"""z""", r"""match a:
 case z: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
        .name 'z'
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 1, None, {'matchor_del': 'strict', '_verify': False}, r"""z""", r"""match a:
 case z | b: pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchOr - 1,6..1,11
        .patterns[2]
        0] MatchAs - 1,6..1,7
          .name 'z'
        1] MatchAs - 1,10..1,11
          .name 'b'
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 1, None, {'matchor_put': False, '_verify': False}, r"""z""", r"""**NodeError('slice being assigned to a MatchOr must be a MatchOr with matchor_put=False, not a MatchAs')**""", r"""
"""),

(r"""match a:
 case a | b: pass""", 'body[0].cases[0].pattern', 0, 2, None, {'matchor_del': 'strict', '_verify': False}, r"""z""", r"""**NodeError("cannot put MatchOr to length 1 with matchor_del='strict'")**""", r"""
"""),

]  # END OF PUT_SLICE_DATA

PUT_SRC_DATA = [
(r"""(1, 2, 3)""", '', (0, 4, 0, 5), {}, r"""*z""", r"""*z""", r"""(1, *z, 3)""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Tuple - 0,0..0,10
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Starred - 0,4..0,6
        .value Name 'z' Load - 0,5..0,6
        .ctx Load
      2] Constant 3 - 0,8..0,9
      .ctx Load
"""),

(r"""(1, 2, 3)""", '', (0, 1, 0, 8), {}, r"""*z,""", r"""*z""", r"""(*z,)""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Tuple - 0,0..0,5
      .elts[1]
      0] Starred - 0,1..0,3
        .value Name 'z' Load - 0,2..0,3
        .ctx Load
      .ctx Load
"""),

(r"""1, 2, 3""", '', (0, 3, 0, 4), {}, r"""*z""", r"""*z""", r"""1, *z, 3""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Tuple - 0,0..0,8
      .elts[3]
      0] Constant 1 - 0,0..0,1
      1] Starred - 0,3..0,5
        .value Name 'z' Load - 0,4..0,5
        .ctx Load
      2] Constant 3 - 0,7..0,8
      .ctx Load
"""),

(r"""1, 2, 3""", '', (0, 0, 0, 7), {}, r"""*z,""", r"""*z,""", r"""*z,""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value Tuple - 0,0..0,3
      .elts[1]
      0] Starred - 0,0..0,2
        .value Name 'z' Load - 0,1..0,2
        .ctx Load
      .ctx Load
"""),

(r"""{a: b, c: d, e: f}""", '', (0, 7, 0, 11), {}, r"""**z""", r"""z""", r"""{a: b, **z, e: f}""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Dict - 0,0..0,17
      .keys[3]
      0] Name 'a' Load - 0,1..0,2
      1] None
      2] Name 'e' Load - 0,12..0,13
      .values[3]
      0] Name 'b' Load - 0,4..0,5
      1] Name 'z' Load - 0,9..0,10
      2] Name 'f' Load - 0,15..0,16
"""),

(r"""{a: b, c: d, e: f}""", '', (0, 1, 0, 17), {}, r"""**z""", r"""z""", r"""{**z}""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Dict - 0,0..0,5
      .keys[1]
      0] None
      .values[1]
      0] Name 'z' Load - 0,3..0,4
"""),

(r"""{a: b, **c, **d, **e}""", '', (0, 7, 0, 15), {}, r"""f: g""", r"""f""", r"""{a: b, f: g, **e}""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Dict - 0,0..0,17
      .keys[3]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'f' Load - 0,7..0,8
      2] None
      .values[3]
      0] Name 'b' Load - 0,4..0,5
      1] Name 'g' Load - 0,10..0,11
      2] Name 'e' Load - 0,15..0,16
"""),

(r"""{a: b, c: d, e: f}""", '', (0, 7, 0, 10), {}, r"""**""", r"""{a: b, **d, e: f}""", r"""{a: b, **d, e: f}""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Dict - 0,0..0,17
      .keys[3]
      0] Name 'a' Load - 0,1..0,2
      1] None
      2] Name 'e' Load - 0,12..0,13
      .values[3]
      0] Name 'b' Load - 0,4..0,5
      1] Name 'd' Load - 0,9..0,10
      2] Name 'f' Load - 0,15..0,16
"""),

(r"""{a: b, **d, e: f}""", '', (0, 7, 0, 9), {}, r"""c: """, r"""c""", r"""{a: b, c: d, e: f}""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Expr - 0,0..0,18
    .value Dict - 0,0..0,18
      .keys[3]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'c' Load - 0,7..0,8
      2] Name 'e' Load - 0,13..0,14
      .values[3]
      0] Name 'b' Load - 0,4..0,5
      1] Name 'd' Load - 0,10..0,11
      2] Name 'f' Load - 0,16..0,17
"""),

(r"""del a, b, c""", '', (0, 7, 0, 11), {}, r"""z""", r"""z""", r"""del a, z""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Delete - 0,0..0,8
    .targets[2]
    0] Name 'a' Del - 0,4..0,5
    1] Name 'z' Del - 0,7..0,8
"""),

(r"""a = b = c = d""", '', (0, 4, 0, 9), {}, r"""z""", r"""z""", r"""a = z = d""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Assign - 0,0..0,9
    .targets[2]
    0] Name 'a' Store - 0,0..0,1
    1] Name 'z' Store - 0,4..0,5
    .value Name 'd' Load - 0,8..0,9
"""),

(r"""import a, b, c""", '', (0, 10, 0, 14), {}, r"""z as xyz""", r"""z as xyz""", r"""import a, z as xyz""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Import - 0,0..0,18
    .names[2]
    0] alias - 0,7..0,8
      .name 'a'
    1] alias - 0,10..0,18
      .name 'z'
      .asname
        'xyz'
"""),

(r"""from mod import a, b, c""", '', (0, 19, 0, 23), {}, r"""z as xyz""", r"""z as xyz""", r"""from mod import a, z as xyz""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] ImportFrom - 0,0..0,27
    .module 'mod'
    .names[2]
    0] alias - 0,16..0,17
      .name 'a'
    1] alias - 0,19..0,27
      .name 'z'
      .asname
        'xyz'
    .level 0
"""),

(r"""with a as a, b as b, c as c: pass""", '', (0, 13, 0, 27), {}, r"""z as xyz""", r"""z as xyz""", r"""with a as a, z as xyz: pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] With - 0,0..0,27
    .items[2]
    0] withitem - 0,5..0,11
      .context_expr Name 'a' Load - 0,5..0,6
      .optional_vars Name 'a' Store - 0,10..0,11
    1] withitem - 0,13..0,21
      .context_expr Name 'z' Load - 0,13..0,14
      .optional_vars Name 'xyz' Store - 0,18..0,21
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""a and b and c""", '', (0, 6, 0, 13), {}, r"""z""", r"""z""", r"""a and z""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value BoolOp - 0,0..0,7
      .op And
      .values[2]
      0] Name 'a' Load - 0,0..0,1
      1] Name 'z' Load - 0,6..0,7
"""),

(r"""a < b < c < d""", '', (0, 4, 0, 13), {}, r"""x < y""", r"""x""", r"""a < x < y""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Compare - 0,0..0,9
      .left Name 'a' Load - 0,0..0,1
      .ops[2]
      0] Lt - 0,2..0,3
      1] Lt - 0,6..0,7
      .comparators[2]
      0] Name 'x' Load - 0,4..0,5
      1] Name 'y' Load - 0,8..0,9
"""),

(r"""[a for a in a() for b in b() for c in c()]""", '', (0, 16, 0, 41), {}, r"""for z in z()""", r"""for z in z()""", r"""[a for a in a() for z in z()]""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] Expr - 0,0..0,29
    .value ListComp - 0,0..0,29
      .elt Name 'a' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,15
        .target Name 'a' Store - 0,7..0,8
        .iter Call - 0,12..0,15
          .func Name 'a' Load - 0,12..0,13
        .is_async 0
      1] comprehension - 0,16..0,28
        .target Name 'z' Store - 0,20..0,21
        .iter Call - 0,25..0,28
          .func Name 'z' Load - 0,25..0,26
        .is_async 0
"""),

(r"""[a for a in a() if a if b if c]""", '', (0, 21, 0, 30), {}, r"""if z""", r"""z""", r"""[a for a in a() if a if z]""", r"""
Module - ROOT 0,0..0,26
  .body[1]
  0] Expr - 0,0..0,26
    .value ListComp - 0,0..0,26
      .elt Name 'a' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,25
        .target Name 'a' Store - 0,7..0,8
        .iter Call - 0,12..0,15
          .func Name 'a' Load - 0,12..0,13
        .ifs[2]
        0] Name 'a' Load - 0,19..0,20
        1] Name 'z' Load - 0,24..0,25
        .is_async 0
"""),

(r"""f(a, b, c)""", '', (0, 5, 0, 9), {}, r"""z""", r"""z""", r"""f(a, z)""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Call - 0,0..0,7
      .func Name 'f' Load - 0,0..0,1
      .args[2]
      0] Name 'a' Load - 0,2..0,3
      1] Name 'z' Load - 0,5..0,6
"""),

(r"""f(a, b, c)""", '', (0, 5, 0, 9), {}, r"""**z""", r"""**z""", r"""f(a, **z)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Call - 0,0..0,9
      .func Name 'f' Load - 0,0..0,1
      .args[1]
      0] Name 'a' Load - 0,2..0,3
      .keywords[1]
      0] keyword - 0,5..0,8
        .value Name 'z' Load - 0,7..0,8
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
Module - ROOT 0,0..4,0
  .body[1]
  0] FunctionDef - 3,0..3,13
    .name 'f'
    .body[1]
    0] Pass - 3,9..3,13
    .decorator_list[2]
    0] Name 'a' Load - 1,1..1,2
    1] Name 'z' Load - 2,1..2,2
"""),

(r"""
match a:
  case [a, b, c]: pass
""", '', (2, 11, 2, 15), {}, r"""*z""", r"""*z""", r"""
match a:
  case [a, *z]: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Match - 1,0..2,20
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,2..2,20
      .pattern MatchSequence - 2,7..2,14
        .patterns[2]
        0] MatchAs - 2,8..2,9
          .name 'a'
        1] MatchStar - 2,11..2,13
          .name 'z'
      .body[1]
      0] Pass - 2,16..2,20
"""),

(r"""
match a:
  case a | b | c: pass
""", '', (2, 11, 2, 16), {}, r"""z""", r"""z""", r"""
match a:
  case a | z: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Match - 1,0..2,18
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,2..2,18
      .pattern MatchOr - 2,7..2,12
        .patterns[2]
        0] MatchAs - 2,7..2,8
          .name 'a'
        1] MatchAs - 2,11..2,12
          .name 'z'
      .body[1]
      0] Pass - 2,14..2,18
"""),

(r"""
match a:
  case {'a': a, 'b': b, 'c': c}: pass
""", '', (2, 16, 2, 30), {}, r"""**z""", r"""{'a': a, **z}""", r"""
match a:
  case {'a': a, **z}: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] Match - 1,0..2,26
    .subject Name 'a' Load - 1,6..1,7
    .cases[1]
    0] match_case - 2,2..2,26
      .pattern MatchMapping - 2,7..2,20
        .keys[1]
        0] Constant 'a' - 2,8..2,11
        .patterns[1]
        0] MatchAs - 2,13..2,14
          .name 'a'
        .rest 'z'
      .body[1]
      0] Pass - 2,22..2,26
"""),

(r"""a, b""", '', (0, 1, 0, 3), {}, r"""+""", r"""+""", r"""a+b""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value BinOp - 0,0..0,3
      .left Name 'a' Load - 0,0..0,1
      .op Add - 0,1..0,2
      .right Name 'b' Load - 0,2..0,3
"""),

(r"""a, b""", '', (0, 1, 0, 3), {}, r""" + """, r"""+""", r"""a + b""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value BinOp - 0,0..0,5
      .left Name 'a' Load - 0,0..0,1
      .op Add - 0,2..0,3
      .right Name 'b' Load - 0,4..0,5
"""),

(r"""a, b""", '', (0, 1, 0, 3), {}, r"""""", r"""ab""", r"""ab""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Name 'ab' Load - 0,0..0,2
"""),

(r"""
if 1: pass
else: pass
""", '', (2, 0, 2, 10), {}, r"""elif 2: pass""", r"""elif 2: pass""", r"""
if 1: pass
elif 2: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,12
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 2,0..2,12
      .test Constant 2 - 2,5..2,6
      .body[1]
      0] Pass - 2,8..2,12
"""),

(r"""
if 1: pass
else: pass
""", '', (2, 0, 2, 5), {}, r"""elif 2:""", r"""2""", r"""
if 1: pass
elif 2: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,12
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] If - 2,0..2,12
      .test Constant 2 - 2,5..2,6
      .body[1]
      0] Pass - 2,8..2,12
"""),

(r"""
if 1: pass
elif 2: pass
""", '', (2, 0, 2, 12), {}, r"""else: pass""", r"""pass""", r"""
if 1: pass
else: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,10
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Pass - 2,6..2,10
"""),

(r"""
if 1: pass
elif 2: pass
""", '', (2, 0, 2, 7), {}, r"""else:""", r"""if 1: pass
else: pass""", r"""
if 1: pass
else: pass
""", r"""
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 1,0..2,10
    .test Constant 1 - 1,3..1,4
    .body[1]
    0] Pass - 1,6..1,10
    .orelse[1]
    0] Pass - 2,6..2,10
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
Module - ROOT 0,0..3,0
  .body[1]
  0] Try - 1,0..2,13
    .body[1]
    0] Pass - 1,5..1,9
    .finalbody[1]
    0] Pass - 2,9..2,13
"""),

(r"""def f(): pass""", '', (0, 6, 0, 6), {}, r"""a, *b, **c""", r"""a, *b, **c""", r"""def f(a, *b, **c): pass""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] FunctionDef - 0,0..0,23
    .name 'f'
    .args arguments - 0,6..0,16
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .vararg arg - 0,10..0,11
        .arg 'b'
      .kwarg arg - 0,15..0,16
        .arg 'c'
    .body[1]
    0] Pass - 0,19..0,23
"""),

(r"""def f(a, *b, **c): pass""", '', (0, 6, 0, 16), {}, r"""""", r"""def f(): pass""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f(a, *b, **c): pass""", '', (0, 6, 0, 16), {}, r""" """, r"""def f( ): pass""", r"""def f( ): pass""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] FunctionDef - 0,0..0,14
    .name 'f'
    .body[1]
    0] Pass - 0,10..0,14
"""),

(r"""def f(a, *b, **c): pass""", '', (0, 6, 0, 16), {}, r"""**DEL**""", r"""def f(): pass""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

]  # END OF PUT_SRC_DATA

PRECEDENCE_DATA = [
    'z',
    '(x, y)',
    '[x, y]',
    '(x := y)',
    'lambda: x',
    'x if y else z',
    'await x',
    'yield x',
    'yield from x',
    'x < y',
    'x and y',
    'x or y',
    '~x',
    'not x',
    '+x',
    '-x',
    'x + y',
    'x - y',
    'x * y',
    'x @ y',
    'x / y',
    'x % y',
    'x << y',
    'x >> y',
    'x | y',
    'x ^ y',
    'x & y',
    'x // y',
    'x ** y',
    'z = y',
    'x, y = y',
    '[x, y] = y',
    '(x := y) = y',
    'lambda: x = y',
    'x if y else z = y',
    'await x = y',
    'yield x = y',
    'yield from x = y',
    'x < y = y',
    'x and y = y',
    'x or y = y',
    '~x = y',
    'not x = y',
    '+x = y',
    '-x = y',
    'x + y = y',
    'x - y = y',
    'x * y = y',
    'x @ y = y',
    'x / y = y',
    'x % y = y',
    'x << y = y',
    'x >> y = y',
    'x | y = y',
    'x ^ y = y',
    'x & y = y',
    'x // y = y',
    'x ** y = y',
    'for z in y:\n    pass',
    'for x, y in y:\n    pass',
    'for [x, y] in y:\n    pass',
    'for (x := y) in y:\n    pass',
    'for lambda: x in y:\n    pass',
    'for x if y else z in y:\n    pass',
    'for await x in y:\n    pass',
    'for yield x in y:\n    pass',
    'for yield from x in y:\n    pass',
    'for x < y in y:\n    pass',
    'for x and y in y:\n    pass',
    'for x or y in y:\n    pass',
    'for ~x in y:\n    pass',
    'for not x in y:\n    pass',
    'for +x in y:\n    pass',
    'for -x in y:\n    pass',
    'for x + y in y:\n    pass',
    'for x - y in y:\n    pass',
    'for x * y in y:\n    pass',
    'for x @ y in y:\n    pass',
    'for x / y in y:\n    pass',
    'for x % y in y:\n    pass',
    'for x << y in y:\n    pass',
    'for x >> y in y:\n    pass',
    'for x | y in y:\n    pass',
    'for x ^ y in y:\n    pass',
    'for x & y in y:\n    pass',
    'for x // y in y:\n    pass',
    'for x ** y in y:\n    pass',
    'async for z in y:\n    pass',
    'async for x, y in y:\n    pass',
    'async for [x, y] in y:\n    pass',
    'async for (x := y) in y:\n    pass',
    'async for lambda: x in y:\n    pass',
    'async for x if y else z in y:\n    pass',
    'async for await x in y:\n    pass',
    'async for yield x in y:\n    pass',
    'async for yield from x in y:\n    pass',
    'async for x < y in y:\n    pass',
    'async for x and y in y:\n    pass',
    'async for x or y in y:\n    pass',
    'async for ~x in y:\n    pass',
    'async for not x in y:\n    pass',
    'async for +x in y:\n    pass',
    'async for -x in y:\n    pass',
    'async for x + y in y:\n    pass',
    'async for x - y in y:\n    pass',
    'async for x * y in y:\n    pass',
    'async for x @ y in y:\n    pass',
    'async for x / y in y:\n    pass',
    'async for x % y in y:\n    pass',
    'async for x << y in y:\n    pass',
    'async for x >> y in y:\n    pass',
    'async for x | y in y:\n    pass',
    'async for x ^ y in y:\n    pass',
    'async for x & y in y:\n    pass',
    'async for x // y in y:\n    pass',
    'async for x ** y in y:\n    pass',
    '(z,)',
    '((x, y),)',
    '([x, y],)',
    '((x := y),)',
    '(lambda: x,)',
    '(x if y else z,)',
    '(await x,)',
    '((yield x),)',
    '((yield from x),)',
    '(x < y,)',
    '(x and y,)',
    '(x or y,)',
    '(~x,)',
    '(not x,)',
    '(+x,)',
    '(-x,)',
    '(x + y,)',
    '(x - y,)',
    '(x * y,)',
    '(x @ y,)',
    '(x / y,)',
    '(x % y,)',
    '(x << y,)',
    '(x >> y,)',
    '(x | y,)',
    '(x ^ y,)',
    '(x & y,)',
    '(x // y,)',
    '(x ** y,)',
    '[z]',
    '[(x, y)]',
    '[[x, y]]',
    '[(x := y)]',
    '[lambda: x]',
    '[x if y else z]',
    '[await x]',
    '[(yield x)]',
    '[(yield from x)]',
    '[x < y]',
    '[x and y]',
    '[x or y]',
    '[~x]',
    '[not x]',
    '[+x]',
    '[-x]',
    '[x + y]',
    '[x - y]',
    '[x * y]',
    '[x @ y]',
    '[x / y]',
    '[x % y]',
    '[x << y]',
    '[x >> y]',
    '[x | y]',
    '[x ^ y]',
    '[x & y]',
    '[x // y]',
    '[x ** y]',
    '[*z]',
    '[*(x, y)]',
    '[*[x, y]]',
    '[*(x := y)]',
    '[*(lambda: x)]',
    '[*(x if y else z)]',
    '[*await x]',
    '[*(yield x)]',
    '[*(yield from x)]',
    '[*(x < y)]',
    '[*(x and y)]',
    '[*(x or y)]',
    '[*~x]',
    '[*(not x)]',
    '[*+x]',
    '[*-x]',
    '[*x + y]',
    '[*x - y]',
    '[*x * y]',
    '[*x @ y]',
    '[*x / y]',
    '[*x % y]',
    '[*x << y]',
    '[*x >> y]',
    '[*x | y]',
    '[*x ^ y]',
    '[*x & y]',
    '[*x // y]',
    '[*x ** y]',
    '{z: v}',
    '{(x, y): v}',
    '{[x, y]: v}',
    '{(x := y): v}',
    '{lambda: x: v}',
    '{x if y else z: v}',
    '{await x: v}',
    '{(yield x): v}',
    '{(yield from x): v}',
    '{x < y: v}',
    '{x and y: v}',
    '{x or y: v}',
    '{~x: v}',
    '{not x: v}',
    '{+x: v}',
    '{-x: v}',
    '{x + y: v}',
    '{x - y: v}',
    '{x * y: v}',
    '{x @ y: v}',
    '{x / y: v}',
    '{x % y: v}',
    '{x << y: v}',
    '{x >> y: v}',
    '{x | y: v}',
    '{x ^ y: v}',
    '{x & y: v}',
    '{x // y: v}',
    '{x ** y: v}',
    '{k: z}',
    '{k: (x, y)}',
    '{k: [x, y]}',
    '{k: (x := y)}',
    '{k: lambda: x}',
    '{k: x if y else z}',
    '{k: await x}',
    '{k: (yield x)}',
    '{k: (yield from x)}',
    '{k: x < y}',
    '{k: x and y}',
    '{k: x or y}',
    '{k: ~x}',
    '{k: not x}',
    '{k: +x}',
    '{k: -x}',
    '{k: x + y}',
    '{k: x - y}',
    '{k: x * y}',
    '{k: x @ y}',
    '{k: x / y}',
    '{k: x % y}',
    '{k: x << y}',
    '{k: x >> y}',
    '{k: x | y}',
    '{k: x ^ y}',
    '{k: x & y}',
    '{k: x // y}',
    '{k: x ** y}',
    '{**z}',
    '{**(x, y)}',
    '{**[x, y]}',
    '{**(x := y)}',
    '{**(lambda: x)}',
    '{**(x if y else z)}',
    '{**await x}',
    '{**(yield x)}',
    '{**(yield from x)}',
    '{**(x < y)}',
    '{**(x and y)}',
    '{**(x or y)}',
    '{**~x}',
    '{**(not x)}',
    '{**+x}',
    '{**-x}',
    '{**x + y}',
    '{**x - y}',
    '{**x * y}',
    '{**x @ y}',
    '{**x / y}',
    '{**x % y}',
    '{**x << y}',
    '{**x >> y}',
    '{**x | y}',
    '{**x ^ y}',
    '{**x & y}',
    '{**x // y}',
    '{**x ** y}',
    "f'{z}'",
    "f'{(x, y)}'",
    "f'{[x, y]}'",
    "f'{(x := y)}'",
    "f'{(lambda: x)}'",
    "f'{(x if y else z)}'",
    "f'{await x}'",
    "f'{(yield x)}'",
    "f'{(yield from x)}'",
    "f'{x < y}'",
    "f'{x and y}'",
    "f'{x or y}'",
    "f'{~x}'",
    "f'{not x}'",
    "f'{+x}'",
    "f'{-x}'",
    "f'{x + y}'",
    "f'{x - y}'",
    "f'{x * y}'",
    "f'{x @ y}'",
    "f'{x / y}'",
    "f'{x % y}'",
    "f'{x << y}'",
    "f'{x >> y}'",
    "f'{x | y}'",
    "f'{x ^ y}'",
    "f'{x & y}'",
    "f'{x // y}'",
    "f'{x ** y}'",
    'z.y',
    '(x, y).y',
    '[x, y].y',
    '(x := y).y',
    '(lambda: x).y',
    '(x if y else z).y',
    '(await x).y',
    '(yield x).y',
    '(yield from x).y',
    '(x < y).y',
    '(x and y).y',
    '(x or y).y',
    '(~x).y',
    '(not x).y',
    '(+x).y',
    '(-x).y',
    '(x + y).y',
    '(x - y).y',
    '(x * y).y',
    '(x @ y).y',
    '(x / y).y',
    '(x % y).y',
    '(x << y).y',
    '(x >> y).y',
    '(x | y).y',
    '(x ^ y).y',
    '(x & y).y',
    '(x // y).y',
    '(x ** y).y',
    'z[y]',
    '(x, y)[y]',
    '[x, y][y]',
    '(x := y)[y]',
    '(lambda: x)[y]',
    '(x if y else z)[y]',
    '(await x)[y]',
    '(yield x)[y]',
    '(yield from x)[y]',
    '(x < y)[y]',
    '(x and y)[y]',
    '(x or y)[y]',
    '(~x)[y]',
    '(not x)[y]',
    '(+x)[y]',
    '(-x)[y]',
    '(x + y)[y]',
    '(x - y)[y]',
    '(x * y)[y]',
    '(x @ y)[y]',
    '(x / y)[y]',
    '(x % y)[y]',
    '(x << y)[y]',
    '(x >> y)[y]',
    '(x | y)[y]',
    '(x ^ y)[y]',
    '(x & y)[y]',
    '(x // y)[y]',
    '(x ** y)[y]',
    'x[z]',
    'x[x, y]',
    'x[[x, y]]',
    'x[(x := y)]',
    'x[lambda: x]',
    'x[x if y else z]',
    'x[await x]',
    'x[(yield x)]',
    'x[(yield from x)]',
    'x[x < y]',
    'x[x and y]',
    'x[x or y]',
    'x[~x]',
    'x[not x]',
    'x[+x]',
    'x[-x]',
    'x[x + y]',
    'x[x - y]',
    'x[x * y]',
    'x[x @ y]',
    'x[x / y]',
    'x[x % y]',
    'x[x << y]',
    'x[x >> y]',
    'x[x | y]',
    'x[x ^ y]',
    'x[x & y]',
    'x[x // y]',
    'x[x ** y]',
    'call(z)',
    'call((x, y))',
    'call([x, y])',
    'call((x := y))',
    'call(lambda: x)',
    'call(x if y else z)',
    'call(await x)',
    'call((yield x))',
    'call((yield from x))',
    'call(x < y)',
    'call(x and y)',
    'call(x or y)',
    'call(~x)',
    'call(not x)',
    'call(+x)',
    'call(-x)',
    'call(x + y)',
    'call(x - y)',
    'call(x * y)',
    'call(x @ y)',
    'call(x / y)',
    'call(x % y)',
    'call(x << y)',
    'call(x >> y)',
    'call(x | y)',
    'call(x ^ y)',
    'call(x & y)',
    'call(x // y)',
    'call(x ** y)',
    'call(**z)',
    'call(**(x, y))',
    'call(**[x, y])',
    'call(**(x := y))',
    'call(**lambda: x)',
    'call(**x if y else z)',
    'call(**await x)',
    'call(**(yield x))',
    'call(**(yield from x))',
    'call(**x < y)',
    'call(**x and y)',
    'call(**x or y)',
    'call(**~x)',
    'call(**not x)',
    'call(**+x)',
    'call(**-x)',
    'call(**x + y)',
    'call(**x - y)',
    'call(**x * y)',
    'call(**x @ y)',
    'call(**x / y)',
    'call(**x % y)',
    'call(**x << y)',
    'call(**x >> y)',
    'call(**x | y)',
    'call(**x ^ y)',
    'call(**x & y)',
    'call(**x // y)',
    'call(**x ** y)',
    'z, y',
    '(x, y), y',
    '[x, y], y',
    '(x := y), y',
    'lambda: x, y',
    'x if y else z, y',
    'await x, y',
    '(yield x), y',
    '(yield from x), y',
    'x < y, y',
    'x and y, y',
    'x or y, y',
    '~x, y',
    'not x, y',
    '+x, y',
    '-x, y',
    'x + y, y',
    'x - y, y',
    'x * y, y',
    'x @ y, y',
    'x / y, y',
    'x % y, y',
    'x << y, y',
    'x >> y, y',
    'x | y, y',
    'x ^ y, y',
    'x & y, y',
    'x // y, y',
    'x ** y, y',
    '[z, y]',
    '[(x, y), y]',
    '[[x, y], y]',
    '[(x := y), y]',
    '[lambda: x, y]',
    '[x if y else z, y]',
    '[await x, y]',
    '[(yield x), y]',
    '[(yield from x), y]',
    '[x < y, y]',
    '[x and y, y]',
    '[x or y, y]',
    '[~x, y]',
    '[not x, y]',
    '[+x, y]',
    '[-x, y]',
    '[x + y, y]',
    '[x - y, y]',
    '[x * y, y]',
    '[x @ y, y]',
    '[x / y, y]',
    '[x % y, y]',
    '[x << y, y]',
    '[x >> y, y]',
    '[x | y, y]',
    '[x ^ y, y]',
    '[x & y, y]',
    '[x // y, y]',
    '[x ** y, y]',
    '(z := y)',
    '(x := z)',
    '((x, y) := y)',
    '(x := (x, y))',
    '([x, y] := y)',
    '(x := [x, y])',
    '((x := y) := y)',
    '(x := (x := y))',
    '((lambda: x) := y)',
    '(x := (lambda: x))',
    '((x if y else z) := y)',
    '(x := (x if y else z))',
    '((await x) := y)',
    '(x := (await x))',
    '((yield x) := y)',
    '(x := (yield x))',
    '((yield from x) := y)',
    '(x := (yield from x))',
    '((x < y) := y)',
    '(x := (x < y))',
    '((x and y) := y)',
    '(x := (x and y))',
    '((x or y) := y)',
    '(x := (x or y))',
    '((~x) := y)',
    '(x := (~x))',
    '((not x) := y)',
    '(x := (not x))',
    '((+x) := y)',
    '(x := (+x))',
    '((-x) := y)',
    '(x := (-x))',
    '((x + y) := y)',
    '(x := (x + y))',
    '((x - y) := y)',
    '(x := (x - y))',
    '((x * y) := y)',
    '(x := (x * y))',
    '((x @ y) := y)',
    '(x := (x @ y))',
    '((x / y) := y)',
    '(x := (x / y))',
    '((x % y) := y)',
    '(x := (x % y))',
    '((x << y) := y)',
    '(x := (x << y))',
    '((x >> y) := y)',
    '(x := (x >> y))',
    '((x | y) := y)',
    '(x := (x | y))',
    '((x ^ y) := y)',
    '(x := (x ^ y))',
    '((x & y) := y)',
    '(x := (x & y))',
    '((x // y) := y)',
    '(x := (x // y))',
    '((x ** y) := y)',
    '(x := (x ** y))',
    'lambda: z',
    'lambda: (x, y)',
    'lambda: [x, y]',
    'lambda: (x := y)',
    'lambda: lambda: x',
    'lambda: x if y else z',
    'lambda: await x',
    'lambda: (yield x)',
    'lambda: (yield from x)',
    'lambda: x < y',
    'lambda: x and y',
    'lambda: x or y',
    'lambda: ~x',
    'lambda: not x',
    'lambda: +x',
    'lambda: -x',
    'lambda: x + y',
    'lambda: x - y',
    'lambda: x * y',
    'lambda: x @ y',
    'lambda: x / y',
    'lambda: x % y',
    'lambda: x << y',
    'lambda: x >> y',
    'lambda: x | y',
    'lambda: x ^ y',
    'lambda: x & y',
    'lambda: x // y',
    'lambda: x ** y',
    'z if y else z',
    'x if z else z',
    'x if y else z',
    '(x, y) if y else z',
    'x if (x, y) else z',
    'x if y else (x, y)',
    '[x, y] if y else z',
    'x if [x, y] else z',
    'x if y else [x, y]',
    '(x := y) if y else z',
    'x if (x := y) else z',
    'x if y else (x := y)',
    '(lambda: x) if y else z',
    'x if (lambda: x) else z',
    'x if y else lambda: x',
    '(x if y else z) if y else z',
    'x if (x if y else z) else z',
    'x if y else x if y else z',
    'await x if y else z',
    'x if await x else z',
    'x if y else await x',
    '(yield x) if y else z',
    'x if (yield x) else z',
    'x if y else (yield x)',
    '(yield from x) if y else z',
    'x if (yield from x) else z',
    'x if y else (yield from x)',
    'x < y if y else z',
    'x if x < y else z',
    'x if y else x < y',
    'x and y if y else z',
    'x if x and y else z',
    'x if y else x and y',
    'x or y if y else z',
    'x if x or y else z',
    'x if y else x or y',
    '~x if y else z',
    'x if ~x else z',
    'x if y else ~x',
    'not x if y else z',
    'x if not x else z',
    'x if y else not x',
    '+x if y else z',
    'x if +x else z',
    'x if y else +x',
    '-x if y else z',
    'x if -x else z',
    'x if y else -x',
    'x + y if y else z',
    'x if x + y else z',
    'x if y else x + y',
    'x - y if y else z',
    'x if x - y else z',
    'x if y else x - y',
    'x * y if y else z',
    'x if x * y else z',
    'x if y else x * y',
    'x @ y if y else z',
    'x if x @ y else z',
    'x if y else x @ y',
    'x / y if y else z',
    'x if x / y else z',
    'x if y else x / y',
    'x % y if y else z',
    'x if x % y else z',
    'x if y else x % y',
    'x << y if y else z',
    'x if x << y else z',
    'x if y else x << y',
    'x >> y if y else z',
    'x if x >> y else z',
    'x if y else x >> y',
    'x | y if y else z',
    'x if x | y else z',
    'x if y else x | y',
    'x ^ y if y else z',
    'x if x ^ y else z',
    'x if y else x ^ y',
    'x & y if y else z',
    'x if x & y else z',
    'x if y else x & y',
    'x // y if y else z',
    'x if x // y else z',
    'x if y else x // y',
    'x ** y if y else z',
    'x if x ** y else z',
    'x if y else x ** y',
    'await z',
    'await (x, y)',
    'await [x, y]',
    'await (x := y)',
    'await (lambda: x)',
    'await (x if y else z)',
    'await (await x)',
    'await (yield x)',
    'await (yield from x)',
    'await (x < y)',
    'await (x and y)',
    'await (x or y)',
    'await (~x)',
    'await (not x)',
    'await (+x)',
    'await (-x)',
    'await (x + y)',
    'await (x - y)',
    'await (x * y)',
    'await (x @ y)',
    'await (x / y)',
    'await (x % y)',
    'await (x << y)',
    'await (x >> y)',
    'await (x | y)',
    'await (x ^ y)',
    'await (x & y)',
    'await (x // y)',
    'await (x ** y)',
    'yield z',
    'yield (x, y)',
    'yield [x, y]',
    'yield (x := y)',
    'yield (lambda: x)',
    'yield (x if y else z)',
    'yield (await x)',
    'yield (yield x)',
    'yield (yield from x)',
    'yield (x < y)',
    'yield (x and y)',
    'yield (x or y)',
    'yield (~x)',
    'yield (not x)',
    'yield (+x)',
    'yield (-x)',
    'yield (x + y)',
    'yield (x - y)',
    'yield (x * y)',
    'yield (x @ y)',
    'yield (x / y)',
    'yield (x % y)',
    'yield (x << y)',
    'yield (x >> y)',
    'yield (x | y)',
    'yield (x ^ y)',
    'yield (x & y)',
    'yield (x // y)',
    'yield (x ** y)',
    'yield from z',
    'yield from (x, y)',
    'yield from [x, y]',
    'yield from (x := y)',
    'yield from (lambda: x)',
    'yield from (x if y else z)',
    'yield from (await x)',
    'yield from (yield x)',
    'yield from (yield from x)',
    'yield from (x < y)',
    'yield from (x and y)',
    'yield from (x or y)',
    'yield from (~x)',
    'yield from (not x)',
    'yield from (+x)',
    'yield from (-x)',
    'yield from (x + y)',
    'yield from (x - y)',
    'yield from (x * y)',
    'yield from (x @ y)',
    'yield from (x / y)',
    'yield from (x % y)',
    'yield from (x << y)',
    'yield from (x >> y)',
    'yield from (x | y)',
    'yield from (x ^ y)',
    'yield from (x & y)',
    'yield from (x // y)',
    'yield from (x ** y)',
    'z < y',
    'x < z',
    '(x, y) < y',
    'x < (x, y)',
    '[x, y] < y',
    'x < [x, y]',
    '(x := y) < y',
    'x < (x := y)',
    '(lambda: x) < y',
    'x < (lambda: x)',
    '(x if y else z) < y',
    'x < (x if y else z)',
    'await x < y',
    'x < await x',
    '(yield x) < y',
    'x < (yield x)',
    '(yield from x) < y',
    'x < (yield from x)',
    '(x < y) < y',
    'x < (x < y)',
    '(x and y) < y',
    'x < (x and y)',
    '(x or y) < y',
    'x < (x or y)',
    '~x < y',
    'x < ~x',
    '(not x) < y',
    'x < (not x)',
    '+x < y',
    'x < +x',
    '-x < y',
    'x < -x',
    'x + y < y',
    'x < x + y',
    'x - y < y',
    'x < x - y',
    'x * y < y',
    'x < x * y',
    'x @ y < y',
    'x < x @ y',
    'x / y < y',
    'x < x / y',
    'x % y < y',
    'x < x % y',
    'x << y < y',
    'x < x << y',
    'x >> y < y',
    'x < x >> y',
    'x | y < y',
    'x < x | y',
    'x ^ y < y',
    'x < x ^ y',
    'x & y < y',
    'x < x & y',
    'x // y < y',
    'x < x // y',
    'x ** y < y',
    'x < x ** y',
    'z and y',
    '(x, y) and y',
    '[x, y] and y',
    '(x := y) and y',
    '(lambda: x) and y',
    '(x if y else z) and y',
    'await x and y',
    '(yield x) and y',
    '(yield from x) and y',
    'x < y and y',
    '(x and y) and y',
    '(x or y) and y',
    '~x and y',
    'not x and y',
    '+x and y',
    '-x and y',
    'x + y and y',
    'x - y and y',
    'x * y and y',
    'x @ y and y',
    'x / y and y',
    'x % y and y',
    'x << y and y',
    'x >> y and y',
    'x | y and y',
    'x ^ y and y',
    'x & y and y',
    'x // y and y',
    'x ** y and y',
    'z or y',
    '(x, y) or y',
    '[x, y] or y',
    '(x := y) or y',
    '(lambda: x) or y',
    '(x if y else z) or y',
    'await x or y',
    '(yield x) or y',
    '(yield from x) or y',
    'x < y or y',
    'x and y or y',
    '(x or y) or y',
    '~x or y',
    'not x or y',
    '+x or y',
    '-x or y',
    'x + y or y',
    'x - y or y',
    'x * y or y',
    'x @ y or y',
    'x / y or y',
    'x % y or y',
    'x << y or y',
    'x >> y or y',
    'x | y or y',
    'x ^ y or y',
    'x & y or y',
    'x // y or y',
    'x ** y or y',
    '~z',
    '~(x, y)',
    '~[x, y]',
    '~(x := y)',
    '~(lambda: x)',
    '~(x if y else z)',
    '~await x',
    '~(yield x)',
    '~(yield from x)',
    '~(x < y)',
    '~(x and y)',
    '~(x or y)',
    '~~x',
    '~(not x)',
    '~+x',
    '~-x',
    '~(x + y)',
    '~(x - y)',
    '~(x * y)',
    '~(x @ y)',
    '~(x / y)',
    '~(x % y)',
    '~(x << y)',
    '~(x >> y)',
    '~(x | y)',
    '~(x ^ y)',
    '~(x & y)',
    '~(x // y)',
    '~x ** y',
    'not z',
    'not (x, y)',
    'not [x, y]',
    'not (x := y)',
    'not (lambda: x)',
    'not (x if y else z)',
    'not await x',
    'not (yield x)',
    'not (yield from x)',
    'not x < y',
    'not (x and y)',
    'not (x or y)',
    'not ~x',
    'not not x',
    'not +x',
    'not -x',
    'not x + y',
    'not x - y',
    'not x * y',
    'not x @ y',
    'not x / y',
    'not x % y',
    'not x << y',
    'not x >> y',
    'not x | y',
    'not x ^ y',
    'not x & y',
    'not x // y',
    'not x ** y',
    '+z',
    '+(x, y)',
    '+[x, y]',
    '+(x := y)',
    '+(lambda: x)',
    '+(x if y else z)',
    '+await x',
    '+(yield x)',
    '+(yield from x)',
    '+(x < y)',
    '+(x and y)',
    '+(x or y)',
    '+~x',
    '+(not x)',
    '++x',
    '+-x',
    '+(x + y)',
    '+(x - y)',
    '+(x * y)',
    '+(x @ y)',
    '+(x / y)',
    '+(x % y)',
    '+(x << y)',
    '+(x >> y)',
    '+(x | y)',
    '+(x ^ y)',
    '+(x & y)',
    '+(x // y)',
    '+x ** y',
    '-z',
    '-(x, y)',
    '-[x, y]',
    '-(x := y)',
    '-(lambda: x)',
    '-(x if y else z)',
    '-await x',
    '-(yield x)',
    '-(yield from x)',
    '-(x < y)',
    '-(x and y)',
    '-(x or y)',
    '-~x',
    '-(not x)',
    '-+x',
    '--x',
    '-(x + y)',
    '-(x - y)',
    '-(x * y)',
    '-(x @ y)',
    '-(x / y)',
    '-(x % y)',
    '-(x << y)',
    '-(x >> y)',
    '-(x | y)',
    '-(x ^ y)',
    '-(x & y)',
    '-(x // y)',
    '-x ** y',
    'z + y',
    'x + z',
    '(x, y) + y',
    'x + (x, y)',
    '[x, y] + y',
    'x + [x, y]',
    '(x := y) + y',
    'x + (x := y)',
    '(lambda: x) + y',
    'x + (lambda: x)',
    '(x if y else z) + y',
    'x + (x if y else z)',
    'await x + y',
    'x + await x',
    '(yield x) + y',
    'x + (yield x)',
    '(yield from x) + y',
    'x + (yield from x)',
    '(x < y) + y',
    'x + (x < y)',
    '(x and y) + y',
    'x + (x and y)',
    '(x or y) + y',
    'x + (x or y)',
    '~x + y',
    'x + ~x',
    '(not x) + y',
    'x + (not x)',
    '+x + y',
    'x + +x',
    '-x + y',
    'x + -x',
    'x + y + y',
    'x + (x + y)',
    'x - y + y',
    'x + (x - y)',
    'x * y + y',
    'x + x * y',
    'x @ y + y',
    'x + x @ y',
    'x / y + y',
    'x + x / y',
    'x % y + y',
    'x + x % y',
    '(x << y) + y',
    'x + (x << y)',
    '(x >> y) + y',
    'x + (x >> y)',
    '(x | y) + y',
    'x + (x | y)',
    '(x ^ y) + y',
    'x + (x ^ y)',
    '(x & y) + y',
    'x + (x & y)',
    'x // y + y',
    'x + x // y',
    'x ** y + y',
    'x + x ** y',
    'z - y',
    'x - z',
    '(x, y) - y',
    'x - (x, y)',
    '[x, y] - y',
    'x - [x, y]',
    '(x := y) - y',
    'x - (x := y)',
    '(lambda: x) - y',
    'x - (lambda: x)',
    '(x if y else z) - y',
    'x - (x if y else z)',
    'await x - y',
    'x - await x',
    '(yield x) - y',
    'x - (yield x)',
    '(yield from x) - y',
    'x - (yield from x)',
    '(x < y) - y',
    'x - (x < y)',
    '(x and y) - y',
    'x - (x and y)',
    '(x or y) - y',
    'x - (x or y)',
    '~x - y',
    'x - ~x',
    '(not x) - y',
    'x - (not x)',
    '+x - y',
    'x - +x',
    '-x - y',
    'x - -x',
    'x + y - y',
    'x - (x + y)',
    'x - y - y',
    'x - (x - y)',
    'x * y - y',
    'x - x * y',
    'x @ y - y',
    'x - x @ y',
    'x / y - y',
    'x - x / y',
    'x % y - y',
    'x - x % y',
    '(x << y) - y',
    'x - (x << y)',
    '(x >> y) - y',
    'x - (x >> y)',
    '(x | y) - y',
    'x - (x | y)',
    '(x ^ y) - y',
    'x - (x ^ y)',
    '(x & y) - y',
    'x - (x & y)',
    'x // y - y',
    'x - x // y',
    'x ** y - y',
    'x - x ** y',
    'z * y',
    'x * z',
    '(x, y) * y',
    'x * (x, y)',
    '[x, y] * y',
    'x * [x, y]',
    '(x := y) * y',
    'x * (x := y)',
    '(lambda: x) * y',
    'x * (lambda: x)',
    '(x if y else z) * y',
    'x * (x if y else z)',
    'await x * y',
    'x * await x',
    '(yield x) * y',
    'x * (yield x)',
    '(yield from x) * y',
    'x * (yield from x)',
    '(x < y) * y',
    'x * (x < y)',
    '(x and y) * y',
    'x * (x and y)',
    '(x or y) * y',
    'x * (x or y)',
    '~x * y',
    'x * ~x',
    '(not x) * y',
    'x * (not x)',
    '+x * y',
    'x * +x',
    '-x * y',
    'x * -x',
    '(x + y) * y',
    'x * (x + y)',
    '(x - y) * y',
    'x * (x - y)',
    'x * y * y',
    'x * (x * y)',
    'x @ y * y',
    'x * (x @ y)',
    'x / y * y',
    'x * (x / y)',
    'x % y * y',
    'x * (x % y)',
    '(x << y) * y',
    'x * (x << y)',
    '(x >> y) * y',
    'x * (x >> y)',
    '(x | y) * y',
    'x * (x | y)',
    '(x ^ y) * y',
    'x * (x ^ y)',
    '(x & y) * y',
    'x * (x & y)',
    'x // y * y',
    'x * (x // y)',
    'x ** y * y',
    'x * x ** y',
    'z @ y',
    'x @ z',
    '(x, y) @ y',
    'x @ (x, y)',
    '[x, y] @ y',
    'x @ [x, y]',
    '(x := y) @ y',
    'x @ (x := y)',
    '(lambda: x) @ y',
    'x @ (lambda: x)',
    '(x if y else z) @ y',
    'x @ (x if y else z)',
    'await x @ y',
    'x @ await x',
    '(yield x) @ y',
    'x @ (yield x)',
    '(yield from x) @ y',
    'x @ (yield from x)',
    '(x < y) @ y',
    'x @ (x < y)',
    '(x and y) @ y',
    'x @ (x and y)',
    '(x or y) @ y',
    'x @ (x or y)',
    '~x @ y',
    'x @ ~x',
    '(not x) @ y',
    'x @ (not x)',
    '+x @ y',
    'x @ +x',
    '-x @ y',
    'x @ -x',
    '(x + y) @ y',
    'x @ (x + y)',
    '(x - y) @ y',
    'x @ (x - y)',
    'x * y @ y',
    'x @ (x * y)',
    'x @ y @ y',
    'x @ (x @ y)',
    'x / y @ y',
    'x @ (x / y)',
    'x % y @ y',
    'x @ (x % y)',
    '(x << y) @ y',
    'x @ (x << y)',
    '(x >> y) @ y',
    'x @ (x >> y)',
    '(x | y) @ y',
    'x @ (x | y)',
    '(x ^ y) @ y',
    'x @ (x ^ y)',
    '(x & y) @ y',
    'x @ (x & y)',
    'x // y @ y',
    'x @ (x // y)',
    'x ** y @ y',
    'x @ x ** y',
    'z / y',
    'x / z',
    '(x, y) / y',
    'x / (x, y)',
    '[x, y] / y',
    'x / [x, y]',
    '(x := y) / y',
    'x / (x := y)',
    '(lambda: x) / y',
    'x / (lambda: x)',
    '(x if y else z) / y',
    'x / (x if y else z)',
    'await x / y',
    'x / await x',
    '(yield x) / y',
    'x / (yield x)',
    '(yield from x) / y',
    'x / (yield from x)',
    '(x < y) / y',
    'x / (x < y)',
    '(x and y) / y',
    'x / (x and y)',
    '(x or y) / y',
    'x / (x or y)',
    '~x / y',
    'x / ~x',
    '(not x) / y',
    'x / (not x)',
    '+x / y',
    'x / +x',
    '-x / y',
    'x / -x',
    '(x + y) / y',
    'x / (x + y)',
    '(x - y) / y',
    'x / (x - y)',
    'x * y / y',
    'x / (x * y)',
    'x @ y / y',
    'x / (x @ y)',
    'x / y / y',
    'x / (x / y)',
    'x % y / y',
    'x / (x % y)',
    '(x << y) / y',
    'x / (x << y)',
    '(x >> y) / y',
    'x / (x >> y)',
    '(x | y) / y',
    'x / (x | y)',
    '(x ^ y) / y',
    'x / (x ^ y)',
    '(x & y) / y',
    'x / (x & y)',
    'x // y / y',
    'x / (x // y)',
    'x ** y / y',
    'x / x ** y',
    'z % y',
    'x % z',
    '(x, y) % y',
    'x % (x, y)',
    '[x, y] % y',
    'x % [x, y]',
    '(x := y) % y',
    'x % (x := y)',
    '(lambda: x) % y',
    'x % (lambda: x)',
    '(x if y else z) % y',
    'x % (x if y else z)',
    'await x % y',
    'x % await x',
    '(yield x) % y',
    'x % (yield x)',
    '(yield from x) % y',
    'x % (yield from x)',
    '(x < y) % y',
    'x % (x < y)',
    '(x and y) % y',
    'x % (x and y)',
    '(x or y) % y',
    'x % (x or y)',
    '~x % y',
    'x % ~x',
    '(not x) % y',
    'x % (not x)',
    '+x % y',
    'x % +x',
    '-x % y',
    'x % -x',
    '(x + y) % y',
    'x % (x + y)',
    '(x - y) % y',
    'x % (x - y)',
    'x * y % y',
    'x % (x * y)',
    'x @ y % y',
    'x % (x @ y)',
    'x / y % y',
    'x % (x / y)',
    'x % y % y',
    'x % (x % y)',
    '(x << y) % y',
    'x % (x << y)',
    '(x >> y) % y',
    'x % (x >> y)',
    '(x | y) % y',
    'x % (x | y)',
    '(x ^ y) % y',
    'x % (x ^ y)',
    '(x & y) % y',
    'x % (x & y)',
    'x // y % y',
    'x % (x // y)',
    'x ** y % y',
    'x % x ** y',
    'z << y',
    'x << z',
    '(x, y) << y',
    'x << (x, y)',
    '[x, y] << y',
    'x << [x, y]',
    '(x := y) << y',
    'x << (x := y)',
    '(lambda: x) << y',
    'x << (lambda: x)',
    '(x if y else z) << y',
    'x << (x if y else z)',
    'await x << y',
    'x << await x',
    '(yield x) << y',
    'x << (yield x)',
    '(yield from x) << y',
    'x << (yield from x)',
    '(x < y) << y',
    'x << (x < y)',
    '(x and y) << y',
    'x << (x and y)',
    '(x or y) << y',
    'x << (x or y)',
    '~x << y',
    'x << ~x',
    '(not x) << y',
    'x << (not x)',
    '+x << y',
    'x << +x',
    '-x << y',
    'x << -x',
    'x + y << y',
    'x << x + y',
    'x - y << y',
    'x << x - y',
    'x * y << y',
    'x << x * y',
    'x @ y << y',
    'x << x @ y',
    'x / y << y',
    'x << x / y',
    'x % y << y',
    'x << x % y',
    'x << y << y',
    'x << (x << y)',
    'x >> y << y',
    'x << (x >> y)',
    '(x | y) << y',
    'x << (x | y)',
    '(x ^ y) << y',
    'x << (x ^ y)',
    '(x & y) << y',
    'x << (x & y)',
    'x // y << y',
    'x << x // y',
    'x ** y << y',
    'x << x ** y',
    'z >> y',
    'x >> z',
    '(x, y) >> y',
    'x >> (x, y)',
    '[x, y] >> y',
    'x >> [x, y]',
    '(x := y) >> y',
    'x >> (x := y)',
    '(lambda: x) >> y',
    'x >> (lambda: x)',
    '(x if y else z) >> y',
    'x >> (x if y else z)',
    'await x >> y',
    'x >> await x',
    '(yield x) >> y',
    'x >> (yield x)',
    '(yield from x) >> y',
    'x >> (yield from x)',
    '(x < y) >> y',
    'x >> (x < y)',
    '(x and y) >> y',
    'x >> (x and y)',
    '(x or y) >> y',
    'x >> (x or y)',
    '~x >> y',
    'x >> ~x',
    '(not x) >> y',
    'x >> (not x)',
    '+x >> y',
    'x >> +x',
    '-x >> y',
    'x >> -x',
    'x + y >> y',
    'x >> x + y',
    'x - y >> y',
    'x >> x - y',
    'x * y >> y',
    'x >> x * y',
    'x @ y >> y',
    'x >> x @ y',
    'x / y >> y',
    'x >> x / y',
    'x % y >> y',
    'x >> x % y',
    'x << y >> y',
    'x >> (x << y)',
    'x >> y >> y',
    'x >> (x >> y)',
    '(x | y) >> y',
    'x >> (x | y)',
    '(x ^ y) >> y',
    'x >> (x ^ y)',
    '(x & y) >> y',
    'x >> (x & y)',
    'x // y >> y',
    'x >> x // y',
    'x ** y >> y',
    'x >> x ** y',
    'z | y',
    'x | z',
    '(x, y) | y',
    'x | (x, y)',
    '[x, y] | y',
    'x | [x, y]',
    '(x := y) | y',
    'x | (x := y)',
    '(lambda: x) | y',
    'x | (lambda: x)',
    '(x if y else z) | y',
    'x | (x if y else z)',
    'await x | y',
    'x | await x',
    '(yield x) | y',
    'x | (yield x)',
    '(yield from x) | y',
    'x | (yield from x)',
    '(x < y) | y',
    'x | (x < y)',
    '(x and y) | y',
    'x | (x and y)',
    '(x or y) | y',
    'x | (x or y)',
    '~x | y',
    'x | ~x',
    '(not x) | y',
    'x | (not x)',
    '+x | y',
    'x | +x',
    '-x | y',
    'x | -x',
    'x + y | y',
    'x | x + y',
    'x - y | y',
    'x | x - y',
    'x * y | y',
    'x | x * y',
    'x @ y | y',
    'x | x @ y',
    'x / y | y',
    'x | x / y',
    'x % y | y',
    'x | x % y',
    'x << y | y',
    'x | x << y',
    'x >> y | y',
    'x | x >> y',
    'x | y | y',
    'x | (x | y)',
    'x ^ y | y',
    'x | x ^ y',
    'x & y | y',
    'x | x & y',
    'x // y | y',
    'x | x // y',
    'x ** y | y',
    'x | x ** y',
    'z ^ y',
    'x ^ z',
    '(x, y) ^ y',
    'x ^ (x, y)',
    '[x, y] ^ y',
    'x ^ [x, y]',
    '(x := y) ^ y',
    'x ^ (x := y)',
    '(lambda: x) ^ y',
    'x ^ (lambda: x)',
    '(x if y else z) ^ y',
    'x ^ (x if y else z)',
    'await x ^ y',
    'x ^ await x',
    '(yield x) ^ y',
    'x ^ (yield x)',
    '(yield from x) ^ y',
    'x ^ (yield from x)',
    '(x < y) ^ y',
    'x ^ (x < y)',
    '(x and y) ^ y',
    'x ^ (x and y)',
    '(x or y) ^ y',
    'x ^ (x or y)',
    '~x ^ y',
    'x ^ ~x',
    '(not x) ^ y',
    'x ^ (not x)',
    '+x ^ y',
    'x ^ +x',
    '-x ^ y',
    'x ^ -x',
    'x + y ^ y',
    'x ^ x + y',
    'x - y ^ y',
    'x ^ x - y',
    'x * y ^ y',
    'x ^ x * y',
    'x @ y ^ y',
    'x ^ x @ y',
    'x / y ^ y',
    'x ^ x / y',
    'x % y ^ y',
    'x ^ x % y',
    'x << y ^ y',
    'x ^ x << y',
    'x >> y ^ y',
    'x ^ x >> y',
    '(x | y) ^ y',
    'x ^ (x | y)',
    'x ^ y ^ y',
    'x ^ (x ^ y)',
    'x & y ^ y',
    'x ^ x & y',
    'x // y ^ y',
    'x ^ x // y',
    'x ** y ^ y',
    'x ^ x ** y',
    'z & y',
    'x & z',
    '(x, y) & y',
    'x & (x, y)',
    '[x, y] & y',
    'x & [x, y]',
    '(x := y) & y',
    'x & (x := y)',
    '(lambda: x) & y',
    'x & (lambda: x)',
    '(x if y else z) & y',
    'x & (x if y else z)',
    'await x & y',
    'x & await x',
    '(yield x) & y',
    'x & (yield x)',
    '(yield from x) & y',
    'x & (yield from x)',
    '(x < y) & y',
    'x & (x < y)',
    '(x and y) & y',
    'x & (x and y)',
    '(x or y) & y',
    'x & (x or y)',
    '~x & y',
    'x & ~x',
    '(not x) & y',
    'x & (not x)',
    '+x & y',
    'x & +x',
    '-x & y',
    'x & -x',
    'x + y & y',
    'x & x + y',
    'x - y & y',
    'x & x - y',
    'x * y & y',
    'x & x * y',
    'x @ y & y',
    'x & x @ y',
    'x / y & y',
    'x & x / y',
    'x % y & y',
    'x & x % y',
    'x << y & y',
    'x & x << y',
    'x >> y & y',
    'x & x >> y',
    '(x | y) & y',
    'x & (x | y)',
    '(x ^ y) & y',
    'x & (x ^ y)',
    'x & y & y',
    'x & (x & y)',
    'x // y & y',
    'x & x // y',
    'x ** y & y',
    'x & x ** y',
    'z // y',
    'x // z',
    '(x, y) // y',
    'x // (x, y)',
    '[x, y] // y',
    'x // [x, y]',
    '(x := y) // y',
    'x // (x := y)',
    '(lambda: x) // y',
    'x // (lambda: x)',
    '(x if y else z) // y',
    'x // (x if y else z)',
    'await x // y',
    'x // await x',
    '(yield x) // y',
    'x // (yield x)',
    '(yield from x) // y',
    'x // (yield from x)',
    '(x < y) // y',
    'x // (x < y)',
    '(x and y) // y',
    'x // (x and y)',
    '(x or y) // y',
    'x // (x or y)',
    '~x // y',
    'x // ~x',
    '(not x) // y',
    'x // (not x)',
    '+x // y',
    'x // +x',
    '-x // y',
    'x // -x',
    '(x + y) // y',
    'x // (x + y)',
    '(x - y) // y',
    'x // (x - y)',
    'x * y // y',
    'x // (x * y)',
    'x @ y // y',
    'x // (x @ y)',
    'x / y // y',
    'x // (x / y)',
    'x % y // y',
    'x // (x % y)',
    '(x << y) // y',
    'x // (x << y)',
    '(x >> y) // y',
    'x // (x >> y)',
    '(x | y) // y',
    'x // (x | y)',
    '(x ^ y) // y',
    'x // (x ^ y)',
    '(x & y) // y',
    'x // (x & y)',
    'x // y // y',
    'x // (x // y)',
    'x ** y // y',
    'x // x ** y',
    'z ** y',
    'x ** z',
    '(x, y) ** y',
    'x ** (x, y)',
    '[x, y] ** y',
    'x ** [x, y]',
    '(x := y) ** y',
    'x ** (x := y)',
    '(lambda: x) ** y',
    'x ** (lambda: x)',
    '(x if y else z) ** y',
    'x ** (x if y else z)',
    'await x ** y',
    'x ** await x',
    '(yield x) ** y',
    'x ** (yield x)',
    '(yield from x) ** y',
    'x ** (yield from x)',
    '(x < y) ** y',
    'x ** (x < y)',
    '(x and y) ** y',
    'x ** (x and y)',
    '(x or y) ** y',
    'x ** (x or y)',
    '(~x) ** y',
    'x ** (~x)',
    '(not x) ** y',
    'x ** (not x)',
    '(+x) ** y',
    'x ** (+x)',
    '(-x) ** y',
    'x ** (-x)',
    '(x + y) ** y',
    'x ** (x + y)',
    '(x - y) ** y',
    'x ** (x - y)',
    '(x * y) ** y',
    'x ** (x * y)',
    '(x @ y) ** y',
    'x ** (x @ y)',
    '(x / y) ** y',
    'x ** (x / y)',
    '(x % y) ** y',
    'x ** (x % y)',
    '(x << y) ** y',
    'x ** (x << y)',
    '(x >> y) ** y',
    'x ** (x >> y)',
    '(x | y) ** y',
    'x ** (x | y)',
    '(x ^ y) ** y',
    'x ** (x ^ y)',
    '(x & y) ** y',
    'x ** (x & y)',
    '(x // y) ** y',
    'x ** (x // y)',
    '(x ** y) ** y',
    'x ** x ** y',
]  # END OF PRECEDENCE_DATA

# end of refreshable data

REPLACE_EXISTING_ONE_DATA = [
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

# TryStar, not available on py3.10 so no TryStar

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
("[i for i in t]", 'body[0].value.generators[0]', {}, "async for z in y", "async for z in y", "[i async for z in y]"),
("[i async for i in t]", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "[i for z in y]"),

# SetComp
("{i for i in t}", 'body[0].value.elt', {}, "z", "z", "{z for i in t}"),
("{i for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{i for z in y}"),
("{i for i in t}", 'body[0].value.generators[0]', {}, "async for z in y", "async for z in y", "{i async for z in y}"),
("{i async for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{i for z in y}"),

# DictComp
("{k: v for i in t}", 'body[0].value.key', {}, "z", "z", "{z: v for i in t}"),
("{k: v for i in t}", 'body[0].value.value', {}, "z", "z", "{k: z for i in t}"),
("{k: v for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{k: v for z in y}"),
("{k: v for i in t}", 'body[0].value.generators[0]', {}, "async for z in y", "async for z in y", "{k: v async for z in y}"),
("{k: v async for i in t}", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "{k: v for z in y}"),

# GeneratorExp
("(i for i in t)", 'body[0].value.elt', {}, "z", "z", "(z for i in t)"),
("(i for i in t)", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "(i for z in y)"),
("(i for i in t)", 'body[0].value.generators[0]', {}, "async for z in y", "async for z in y", "(i async for z in y)"),
("(i async for i in t)", 'body[0].value.generators[0]', {}, "for z in y", "for z in y", "(i for z in y)"),

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
# Interpolation, no exist in py3.10
# TemplateStr, no exist in py3.10

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
