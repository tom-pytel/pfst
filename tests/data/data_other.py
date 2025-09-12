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
      .asname 'xyz'
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
      .asname 'xyz'
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
    'invalid value for Assign.targets, got NamedExpr',
    'invalid value for Assign.targets, got Lambda',
    'invalid value for Assign.targets, got IfExp',
    'invalid value for Assign.targets, got Await',
    'invalid value for Assign.targets, got Yield',
    'invalid value for Assign.targets, got YieldFrom',
    'invalid value for Assign.targets, got Compare',
    'invalid value for Assign.targets, got BoolOp',
    'invalid value for Assign.targets, got BoolOp',
    'invalid value for Assign.targets, got UnaryOp',
    'invalid value for Assign.targets, got UnaryOp',
    'invalid value for Assign.targets, got UnaryOp',
    'invalid value for Assign.targets, got UnaryOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'invalid value for Assign.targets, got BinOp',
    'for z in y:\n    pass',
    'for x, y in y:\n    pass',
    'for [x, y] in y:\n    pass',
    'invalid value for For.target, got NamedExpr',
    'invalid value for For.target, got Lambda',
    'invalid value for For.target, got IfExp',
    'invalid value for For.target, got Await',
    'invalid value for For.target, got Yield',
    'invalid value for For.target, got YieldFrom',
    'invalid value for For.target, got Compare',
    'invalid value for For.target, got BoolOp',
    'invalid value for For.target, got BoolOp',
    'invalid value for For.target, got UnaryOp',
    'invalid value for For.target, got UnaryOp',
    'invalid value for For.target, got UnaryOp',
    'invalid value for For.target, got UnaryOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'invalid value for For.target, got BinOp',
    'async for z in y:\n    pass',
    'async for x, y in y:\n    pass',
    'async for [x, y] in y:\n    pass',
    'invalid value for AsyncFor.target, got NamedExpr',
    'invalid value for AsyncFor.target, got Lambda',
    'invalid value for AsyncFor.target, got IfExp',
    'invalid value for AsyncFor.target, got Await',
    'invalid value for AsyncFor.target, got Yield',
    'invalid value for AsyncFor.target, got YieldFrom',
    'invalid value for AsyncFor.target, got Compare',
    'invalid value for AsyncFor.target, got BoolOp',
    'invalid value for AsyncFor.target, got BoolOp',
    'invalid value for AsyncFor.target, got UnaryOp',
    'invalid value for AsyncFor.target, got UnaryOp',
    'invalid value for AsyncFor.target, got UnaryOp',
    'invalid value for AsyncFor.target, got UnaryOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
    'invalid value for AsyncFor.target, got BinOp',
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
    'expecting a Name for NamedExpr.target, got Tuple',
    '(x := (x, y))',
    'expecting a Name for NamedExpr.target, got List',
    '(x := [x, y])',
    'expecting a Name for NamedExpr.target, got NamedExpr',
    '(x := (x := y))',
    'expecting a Name for NamedExpr.target, got Lambda',
    '(x := lambda: x)',
    'expecting a Name for NamedExpr.target, got IfExp',
    '(x := x if y else z)',
    'expecting a Name for NamedExpr.target, got Await',
    '(x := await x)',
    'expecting a Name for NamedExpr.target, got Yield',
    '(x := (yield x))',
    'expecting a Name for NamedExpr.target, got YieldFrom',
    '(x := (yield from x))',
    'expecting a Name for NamedExpr.target, got Compare',
    '(x := x < y)',
    'expecting a Name for NamedExpr.target, got BoolOp',
    '(x := x and y)',
    'expecting a Name for NamedExpr.target, got BoolOp',
    '(x := x or y)',
    'expecting a Name for NamedExpr.target, got UnaryOp',
    '(x := ~x)',
    'expecting a Name for NamedExpr.target, got UnaryOp',
    '(x := not x)',
    'expecting a Name for NamedExpr.target, got UnaryOp',
    '(x := +x)',
    'expecting a Name for NamedExpr.target, got UnaryOp',
    '(x := -x)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x + y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x - y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x * y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x @ y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x / y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x % y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x << y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x >> y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x | y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x ^ y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x & y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x // y)',
    'expecting a Name for NamedExpr.target, got BinOp',
    '(x := x ** y)',
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
