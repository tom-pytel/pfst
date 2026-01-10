# (attr, start, False, field, options, code | (parse_mode, code), put_code | (parse_mode, put_code),
#
# code after put,
# [code after put FST if different,]  - shouldn't be present if everything working correctly
# [code after put AST if different,]  - can be present
# dump code after put)
# - OR
# error)

from fst.asttypes import *

DATA_PUT_ONE = {
'old': [  # ................................................................................

('', 1, None, None, {}, ('exec', r'''
i = 1
j = 2
k = 3
'''), (None,
r'''l = 4'''), r'''
i = 1
l = 4
k = 3
''', r'''
Module - ROOT 0,0..2,5
  .body[3]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 1,0..1,5
     .targets[1]
      0] Name 'l' Store - 1,0..1,1
     .value Constant 4 - 1,4..1,5
   2] Assign - 2,0..2,5
     .targets[1]
      0] Name 'k' Store - 2,0..2,1
     .value Constant 3 - 2,4..2,5
'''),

('', -1, None, None, {}, ('exec', r'''
i = 1
j = 2
k = 3
'''), (None,
r'''l = 4'''), r'''
i = 1
j = 2
l = 4
''', r'''
Module - ROOT 0,0..2,5
  .body[3]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 1,0..1,5
     .targets[1]
      0] Name 'j' Store - 1,0..1,1
     .value Constant 2 - 1,4..1,5
   2] Assign - 2,0..2,5
     .targets[1]
      0] Name 'l' Store - 2,0..2,1
     .value Constant 4 - 2,4..2,5
'''),

('', -3, None, None, {}, ('exec', r'''
i = 1
j = 2
k = 3
'''), (None,
r'''l = 4'''), r'''
l = 4
j = 2
k = 3
''', r'''
Module - ROOT 0,0..2,5
  .body[3]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'l' Store - 0,0..0,1
     .value Constant 4 - 0,4..0,5
   1] Assign - 1,0..1,5
     .targets[1]
      0] Name 'j' Store - 1,0..1,1
     .value Constant 2 - 1,4..1,5
   2] Assign - 2,0..2,5
     .targets[1]
      0] Name 'k' Store - 2,0..2,1
     .value Constant 3 - 2,4..2,5
'''),

('', -4, None, None, {}, ('exec', r'''
i = 1
j = 2
k = 3
'''), (None,
r'''l = 4'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', 1, None, None, {}, ('exec',
r'''(1, 2, 3)'''), (None,
r'''4'''),
r'''(1, 4, 3)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Tuple - 0,0..0,9
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 4 - 0,4..0,5
        2] Constant 3 - 0,7..0,8
       .ctx Load
'''),

('body[0].value', -1, None, None, {}, ('exec',
r'''(1, 2, 3)'''), (None,
r'''4'''),
r'''(1, 2, 4)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Tuple - 0,0..0,9
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 2 - 0,4..0,5
        2] Constant 4 - 0,7..0,8
       .ctx Load
'''),

('body[0].value', -3, None, None, {}, ('exec',
r'''(1, 2, 3)'''), (None,
r'''4'''),
r'''(4, 2, 3)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Tuple - 0,0..0,9
       .elts[3]
        0] Constant 4 - 0,1..0,2
        1] Constant 2 - 0,4..0,5
        2] Constant 3 - 0,7..0,8
       .ctx Load
'''),

('body[0].value', -4, None, None, {}, ('exec',
r'''(1, 2, 3)'''), (None,
r'''4'''),
r'''**IndexError('index out of range')**'''),

('body[0]', None, None, None, {}, ('exec',
r'''i = j'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete Assign.value')**'''),

('body[0]', None, None, None, {}, ('exec',
r'''i = j'''), (None,
r'''k'''),
r'''i = k''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Name 'k' Load - 0,4..0,5
'''),

('body[0]', None, None, None, {'raw': False}, ('exec',
r'''i = j'''), (None,
r'''a, b'''),
r'''i = (a, b)''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Assign - 0,0..0,10
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Tuple - 0,4..0,10
       .elts[2]
        0] Name 'a' Load - 0,5..0,6
        1] Name 'b' Load - 0,8..0,9
       .ctx Load
'''),

('body[0]', None, None, None, {'pars': False}, ('exec',
r'''i = j'''), (None,
r'''a, b'''),
r'''i = a, b''',
r'''i = (a, b)''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Assign - 0,0..0,8
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Tuple - 0,4..0,8
       .elts[2]
        0] Name 'a' Load - 0,4..0,5
        1] Name 'b' Load - 0,7..0,8
       .ctx Load
'''),

('body[0]', None, None, None, {}, ('exec',
r'''i = (j)'''), (None,
r'''(a := b)'''),
r'''i = (a := b)''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Assign - 0,0..0,12
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value NamedExpr - 0,5..0,11
       .target Name 'a' Store - 0,5..0,6
       .value Name 'b' Load - 0,10..0,11
'''),

('body[0]', None, None, None, {'pars': False}, ('exec',
r'''i = (j)'''), (None,
r'''(a := b)'''),
r'''i = ((a := b))''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Assign - 0,0..0,14
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value NamedExpr - 0,6..0,12
       .target Name 'a' Store - 0,6..0,7
       .value Name 'b' Load - 0,11..0,12
'''),

('body[0]', None, None, None, {}, ('exec',
r'''i'''), (None,
r'''j'''),
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', None, None, None, {'raw': False}, ('exec',
r'''i'''), (None,
r'''a, b'''),
r'''(a, b)''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Tuple - 0,0..0,6
       .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

('body[0]', None, None, None, {'pars': False}, ('exec', r'''
( # 1
i
# 2
)
'''), (None, r'''
( # 3
j
# 4
)
'''), r'''
( # 1
( # 3
j
# 4
)
# 2
)
''', r'''
( # 1
j
# 2
)
''', r'''
Module - ROOT 0,0..6,1
  .body[1]
   0] Expr - 0,0..6,1
     .value Name 'j' Load - 2,0..2,1
'''),

('body[0]', None, None, None, {'pars': True}, ('exec', r'''
( # 1
i
# 2
)
'''), (None, r'''
( # 3
j
# 4
)
'''), r'''
( # 3
j
# 4
)
''',
r'''j''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value Name 'j' Load - 1,0..1,1
'''),

('body[0]', None, None, None, {'raw': False, 'pars': 'auto'}, ('exec', r'''
( # 1
i
# 2
)
'''), (None, r'''
( # 3
j
# 4
)
'''),
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', None, None, None, {'pars': False, '_verify': False, 'comment': 'will wind up with wrong unreparsable tuple position'}, ('exec', r'''
( # 1
i
# 2
)
'''), (None,
r'''a, b'''), r'''
( # 1
a, b
# 2
)
''', r'''
( # 1
(a, b)
# 2
)
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value Tuple - 1,0..1,4
       .elts[2]
        0] Name 'a' Load - 1,0..1,1
        1] Name 'b' Load - 1,3..1,4
       .ctx Load
'''),

('body[0]', None, None, None, {'raw': False, 'pars': True}, ('exec', r'''
( # 1
i
# 2
)
'''), (None,
r'''a, b'''),
r'''(a, b)''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Tuple - 0,0..0,6
       .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

('body[0]', None, None, None, {'raw': False, 'pars': 'auto'}, ('exec', r'''
( # 1
i
# 2
)
'''), (None,
r'''a, b'''),
r'''(a, b)''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Tuple - 0,0..0,6
       .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

('body[0]', None, None, None, {'pars': False}, ('exec',
r'''(f())'''), (None,
r'''g()'''),
r'''(g())''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Call - 0,1..0,4
       .func Name 'g' Load - 0,1..0,2
'''),

('body[0]', None, None, None, {'pars': True}, ('exec',
r'''(f())'''), (None,
r'''g()'''),
r'''g()''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Call - 0,0..0,3
       .func Name 'g' Load - 0,0..0,1
'''),

('body[0]', None, None, None, {'pars': False}, ('exec',
r'''(f())'''), (None,
r'''(g())'''),
r'''((g()))''',
r'''(g())''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Call - 0,2..0,5
       .func Name 'g' Load - 0,2..0,3
'''),

('body[0]', None, None, None, {'pars': True}, ('exec',
r'''(f())'''), (None,
r'''(g())'''),
r'''(g())''',
r'''g()''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Call - 0,1..0,4
       .func Name 'g' Load - 0,1..0,2
'''),

('body[0]', None, None, None, {'raw': False}, ('exec',
r'''i += j'''), (None,
r'''a, b'''),
r'''i += (a, b)''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] AugAssign - 0,0..0,11
     .target Name 'i' Store - 0,0..0,1
     .op Add - 0,2..0,3
     .value Tuple - 0,5..0,11
       .elts[2]
        0] Name 'a' Load - 0,6..0,7
        1] Name 'b' Load - 0,9..0,10
       .ctx Load
'''),

('body[0]', None, None, 'iter', {'raw': False}, ('exec',
r'''for i in j: pass'''), (None,
r'''a, b'''),
r'''for i in (a, b): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] For - 0,0..0,21
     .target Name 'i' Store - 0,4..0,5
     .iter Tuple - 0,9..0,15
       .elts[2]
        0] Name 'a' Load - 0,10..0,11
        1] Name 'b' Load - 0,13..0,14
       .ctx Load
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0]', None, None, 'iter', {'raw': False}, ('exec',
r'''async for i in j: pass'''), (None,
r'''a, b'''),
r'''async for i in (a, b): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] AsyncFor - 0,0..0,27
     .target Name 'i' Store - 0,10..0,11
     .iter Tuple - 0,15..0,21
       .elts[2]
        0] Name 'a' Load - 0,16..0,17
        1] Name 'b' Load - 0,19..0,20
       .ctx Load
     .body[1]
      0] Pass - 0,23..0,27
'''),

('body[0]', None, None, 'test', {'raw': False}, ('exec',
r'''while i: pass'''), (None,
r'''a, b'''),
r'''while (a, b): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] While - 0,0..0,18
     .test Tuple - 0,6..0,12
       .elts[2]
        0] Name 'a' Load - 0,7..0,8
        1] Name 'b' Load - 0,10..0,11
       .ctx Load
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0]', None, None, 'test', {'raw': False}, ('exec',
r'''if i: pass'''), (None,
r'''a, b'''),
r'''if (a, b): pass''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] If - 0,0..0,15
     .test Tuple - 0,3..0,9
       .elts[2]
        0] Name 'a' Load - 0,4..0,5
        1] Name 'b' Load - 0,7..0,8
       .ctx Load
     .body[1]
      0] Pass - 0,11..0,15
'''),

('body[0]', None, None, 'subject', {'raw': False}, ('exec', r'''
match i:
  case 1: pass
'''), (None,
r'''a, b'''), r'''
match (a, b):
  case 1: pass
''', r'''
Module - ROOT 0,0..1,14
  .body[1]
   0] Match - 0,0..1,14
     .subject Tuple - 0,6..0,12
       .elts[2]
        0] Name 'a' Load - 0,7..0,8
        1] Name 'b' Load - 0,10..0,11
       .ctx Load
     .cases[1]
      0] match_case - 1,2..1,14
        .pattern MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
'''),

('body[0]', None, None, None, {'raw': False}, ('exec',
r'''assert i'''), (None,
r'''a, b'''),
r'''assert (a, b)''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Assert - 0,0..0,13
     .test Tuple - 0,7..0,13
       .elts[2]
        0] Name 'a' Load - 0,8..0,9
        1] Name 'b' Load - 0,11..0,12
       .ctx Load
'''),

('body[0].value', None, None, None, {'raw': False}, ('exec',
r'''(i := j)'''), (None,
r'''a, b'''),
r'''(i := (a, b))''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Expr - 0,0..0,13
     .value NamedExpr - 0,1..0,12
       .target Name 'i' Store - 0,1..0,2
       .value Tuple - 0,6..0,12
         .elts[2]
          0] Name 'a' Load - 0,7..0,8
          1] Name 'b' Load - 0,10..0,11
         .ctx Load
'''),

('body[0].value', None, None, 'left', {'raw': False}, ('exec',
r'''i * j'''), (None,
r'''a + b'''),
r'''(a + b) * j''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value BinOp - 0,0..0,11
       .left BinOp - 0,1..0,6
         .left Name 'a' Load - 0,1..0,2
         .op Add - 0,3..0,4
         .right Name 'b' Load - 0,5..0,6
       .op Mult - 0,8..0,9
       .right Name 'j' Load - 0,10..0,11
'''),

('body[0].value', None, None, 'right', {'raw': False}, ('exec',
r'''i * j'''), (None,
r'''a + b'''),
r'''i * (a + b)''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value BinOp - 0,0..0,11
       .left Name 'i' Load - 0,0..0,1
       .op Mult - 0,2..0,3
       .right BinOp - 0,5..0,10
         .left Name 'a' Load - 0,5..0,6
         .op Add - 0,7..0,8
         .right Name 'b' Load - 0,9..0,10
'''),

('body[0].value', None, None, None, {'raw': False}, ('exec',
r'''-i'''), (None,
r'''a + b'''),
r'''-(a + b)''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value UnaryOp - 0,0..0,8
       .op USub - 0,0..0,1
       .operand BinOp - 0,2..0,7
         .left Name 'a' Load - 0,2..0,3
         .op Add - 0,4..0,5
         .right Name 'b' Load - 0,6..0,7
'''),

('body[0].value', None, None, None, {'raw': False}, ('exec',
r'''lambda: i'''), (None,
r'''a, b'''),
r'''lambda: (a, b)''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Expr - 0,0..0,14
     .value Lambda - 0,0..0,14
       .body Tuple - 0,8..0,14
         .elts[2]
          0] Name 'a' Load - 0,9..0,10
          1] Name 'b' Load - 0,12..0,13
         .ctx Load
'''),

('body[0].value', None, None, 'body', {'raw': False}, ('exec',
r'''i if j else k'''), (None,
r'''a if b else c'''),
r'''(a if b else c) if j else k''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Expr - 0,0..0,27
     .value IfExp - 0,0..0,27
       .test Name 'j' Load - 0,19..0,20
       .body IfExp - 0,1..0,14
         .test Name 'b' Load - 0,6..0,7
         .body Name 'a' Load - 0,1..0,2
         .orelse Name 'c' Load - 0,13..0,14
       .orelse Name 'k' Load - 0,26..0,27
'''),

('body[0].value', None, None, 'test', {'raw': False}, ('exec',
r'''i if j else k'''), (None,
r'''a if b else c'''),
r'''i if (a if b else c) else k''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Expr - 0,0..0,27
     .value IfExp - 0,0..0,27
       .test IfExp - 0,6..0,19
         .test Name 'b' Load - 0,11..0,12
         .body Name 'a' Load - 0,6..0,7
         .orelse Name 'c' Load - 0,18..0,19
       .body Name 'i' Load - 0,0..0,1
       .orelse Name 'k' Load - 0,26..0,27
'''),

('body[0].value', None, None, 'orelse', {}, ('exec',
r'''i if j else k'''), (None,
r'''a if b else c'''),
r'''i if j else a if b else c''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Expr - 0,0..0,25
     .value IfExp - 0,0..0,25
       .test Name 'j' Load - 0,5..0,6
       .body Name 'i' Load - 0,0..0,1
       .orelse IfExp - 0,12..0,25
         .test Name 'b' Load - 0,17..0,18
         .body Name 'a' Load - 0,12..0,13
         .orelse Name 'c' Load - 0,24..0,25
'''),

('body[0].value', None, None, 'elt', {'raw': False}, ('exec',
r'''[i for i in j]'''), (None,
r'''a, b'''),
r'''[(a, b) for i in j]''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Expr - 0,0..0,19
     .value ListComp - 0,0..0,19
       .elt Tuple - 0,1..0,7
         .elts[2]
          0] Name 'a' Load - 0,2..0,3
          1] Name 'b' Load - 0,5..0,6
         .ctx Load
       .generators[1]
        0] comprehension - 0,8..0,18
          .target Name 'i' Store - 0,12..0,13
          .iter Name 'j' Load - 0,17..0,18
          .is_async 0
'''),

('body[0].value', None, None, 'elt', {'raw': False}, ('exec',
r'''{i for i in j}'''), (None,
r'''a, b'''),
r'''{(a, b) for i in j}''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Expr - 0,0..0,19
     .value SetComp - 0,0..0,19
       .elt Tuple - 0,1..0,7
         .elts[2]
          0] Name 'a' Load - 0,2..0,3
          1] Name 'b' Load - 0,5..0,6
         .ctx Load
       .generators[1]
        0] comprehension - 0,8..0,18
          .target Name 'i' Store - 0,12..0,13
          .iter Name 'j' Load - 0,17..0,18
          .is_async 0
'''),

('body[0].value', None, None, 'key', {'raw': False}, ('exec',
r'''{k: v for i in j}'''), (None,
r'''a, b'''),
r'''{(a, b): v for i in j}''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value DictComp - 0,0..0,22
       .key Tuple - 0,1..0,7
         .elts[2]
          0] Name 'a' Load - 0,2..0,3
          1] Name 'b' Load - 0,5..0,6
         .ctx Load
       .value Name 'v' Load - 0,9..0,10
       .generators[1]
        0] comprehension - 0,11..0,21
          .target Name 'i' Store - 0,15..0,16
          .iter Name 'j' Load - 0,20..0,21
          .is_async 0
'''),

('body[0].value', None, None, 'value', {'raw': False}, ('exec',
r'''{k: v for i in j}'''), (None,
r'''a, b'''),
r'''{k: (a, b) for i in j}''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value DictComp - 0,0..0,22
       .key Name 'k' Load - 0,1..0,2
       .value Tuple - 0,4..0,10
         .elts[2]
          0] Name 'a' Load - 0,5..0,6
          1] Name 'b' Load - 0,8..0,9
         .ctx Load
       .generators[1]
        0] comprehension - 0,11..0,21
          .target Name 'i' Store - 0,15..0,16
          .iter Name 'j' Load - 0,20..0,21
          .is_async 0
'''),

('body[0].value', None, None, 'elt', {'raw': False}, ('exec',
r'''(i for i in j)'''), (None,
r'''a, b'''),
r'''((a, b) for i in j)''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Expr - 0,0..0,19
     .value GeneratorExp - 0,0..0,19
       .elt Tuple - 0,1..0,7
         .elts[2]
          0] Name 'a' Load - 0,2..0,3
          1] Name 'b' Load - 0,5..0,6
         .ctx Load
       .generators[1]
        0] comprehension - 0,8..0,18
          .target Name 'i' Store - 0,12..0,13
          .iter Name 'j' Load - 0,17..0,18
          .is_async 0
'''),

('body[0].value', None, None, None, {'raw': False}, ('exec',
r'''await i'''), (None,
r'''a, b'''),
r'''await (a, b)''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value Await - 0,0..0,12
       .value Tuple - 0,6..0,12
         .elts[2]
          0] Name 'a' Load - 0,7..0,8
          1] Name 'b' Load - 0,10..0,11
         .ctx Load
'''),

('body[0].value', None, None, None, {'raw': False}, ('exec',
r'''yield from i'''), (None,
r'''a, b'''),
r'''yield from (a, b)''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value YieldFrom - 0,0..0,17
       .value Tuple - 0,11..0,17
         .elts[2]
          0] Name 'a' Load - 0,12..0,13
          1] Name 'b' Load - 0,15..0,16
         .ctx Load
'''),

('body[0].value.values[0]', None, None, None, {'raw': False, '_ver': 12}, ('exec',
"\nf'{i}'\n"), (None,
r'''a, b'''),
"\nf'{(a, b)}'\n", r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value JoinedStr - 0,0..0,11
       .values[1]
        0] FormattedValue - 0,2..0,10
          .value Tuple - 0,3..0,9
            .elts[2]
             0] Name 'a' Load - 0,4..0,5
             1] Name 'b' Load - 0,7..0,8
            .ctx Load
          .conversion -1
'''),

('body[0].value.values[0]', None, None, None, {'raw': False, '_ver': 14}, ('exec',
"\nt'{i}'\n"), (None,
r'''a, b'''),
"\nt'{(a, b)}'\n", r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value TemplateStr - 0,0..0,11
       .values[1]
        0] Interpolation - 0,2..0,10
          .value Tuple - 0,3..0,9
            .elts[2]
             0] Name 'a' Load - 0,4..0,5
             1] Name 'b' Load - 0,7..0,8
            .ctx Load
          .str '(a, b)'
          .conversion -1
'''),

('body[0].value', None, None, None, {'raw': False}, ('exec',
r'''i.j'''), (None,
r'''a, b'''),
r'''(a, b).j''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Attribute - 0,0..0,8
       .value Tuple - 0,0..0,6
         .elts[2]
          0] Name 'a' Load - 0,1..0,2
          1] Name 'b' Load - 0,4..0,5
         .ctx Load
       .attr 'j'
       .ctx Load
'''),

('body[0].value', None, None, None, {'raw': False}, ('exec',
r'''i[j]'''), (None,
r'''a, b'''),
r'''(a, b)[j]''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Subscript - 0,0..0,9
       .value Tuple - 0,0..0,6
         .elts[2]
          0] Name 'a' Load - 0,1..0,2
          1] Name 'b' Load - 0,4..0,5
         .ctx Load
       .slice Name 'j' Load - 0,7..0,8
       .ctx Load
'''),

('body[0].value', None, None, 'slice', {}, ('exec',
r'''i[j]'''), (None,
r'''a, b'''),
r'''i[a, b]''',
r'''i[(a, b)]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'i' Load - 0,0..0,1
       .slice Tuple - 0,2..0,6
         .elts[2]
          0] Name 'a' Load - 0,2..0,3
          1] Name 'b' Load - 0,5..0,6
         .ctx Load
       .ctx Load
'''),

('body[0].value', None, None, 'slice', {}, ('exec',
r'''i[j]'''), (None,
r'''x:y:z'''),
r'''i[x:y:z]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'i' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .lower Name 'x' Load - 0,2..0,3
         .upper Name 'y' Load - 0,4..0,5
         .step Name 'z' Load - 0,6..0,7
       .ctx Load
'''),

('body[0].value', None, None, 'slice', {}, ('exec',
r'''i[a:b:c]'''), (None,
r'''a, b'''),
r'''i[a, b]''',
r'''i[(a, b)]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'i' Load - 0,0..0,1
       .slice Tuple - 0,2..0,6
         .elts[2]
          0] Name 'a' Load - 0,2..0,3
          1] Name 'b' Load - 0,5..0,6
         .ctx Load
       .ctx Load
'''),

('body[0].value', None, None, 'slice', {}, ('exec',
r'''i[a:b:c]'''), (None,
r'''z'''),
r'''i[z]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'i' Load - 0,0..0,1
       .slice Name 'z' Load - 0,2..0,3
       .ctx Load
'''),

('body[0].value.elts[0]', None, None, None, {'raw': False}, ('exec',
r'''[*i]'''), (None,
r'''a, b'''),
r'''[*(a, b)]''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value List - 0,0..0,9
       .elts[1]
        0] Starred - 0,1..0,8
          .value Tuple - 0,2..0,8
            .elts[2]
             0] Name 'a' Load - 0,3..0,4
             1] Name 'b' Load - 0,6..0,7
            .ctx Load
          .ctx Load
       .ctx Load
'''),

('body[0].value.generators[0]', None, None, 'iter', {'raw': False}, ('exec',
r'''[i for i in j]'''), (None,
r'''a, b'''),
r'''[i for i in (a, b)]''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Expr - 0,0..0,19
     .value ListComp - 0,0..0,19
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,18
          .target Name 'i' Store - 0,7..0,8
          .iter Tuple - 0,12..0,18
            .elts[2]
             0] Name 'a' Load - 0,13..0,14
             1] Name 'b' Load - 0,16..0,17
            .ctx Load
          .is_async 0
'''),

('body[0].value.generators[0]', None, None, 'iter', {'raw': False}, ('exec',
r'''[i for i in j]'''), (None,
r'''a, b'''),
r'''[i for i in (a, b)]''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Expr - 0,0..0,19
     .value ListComp - 0,0..0,19
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,18
          .target Name 'i' Store - 0,7..0,8
          .iter Tuple - 0,12..0,18
            .elts[2]
             0] Name 'a' Load - 0,13..0,14
             1] Name 'b' Load - 0,16..0,17
            .ctx Load
          .is_async 0
'''),

('body[0].value.keywords[0]', None, None, None, {'raw': False}, ('exec',
r'''f(i=j)'''), (None,
r'''a, b'''),
r'''f(i=(a, b))''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Call - 0,0..0,11
       .func Name 'f' Load - 0,0..0,1
       .keywords[1]
        0] keyword - 0,2..0,10
          .arg 'i'
          .value Tuple - 0,4..0,10
            .elts[2]
             0] Name 'a' Load - 0,5..0,6
             1] Name 'b' Load - 0,8..0,9
            .ctx Load
'''),

('body[0].keywords[0]', None, None, None, {'raw': False}, ('exec',
r'''class cls(i=j): pass'''), (None,
r'''a, b'''),
r'''class cls(i=(a, b)): pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] ClassDef - 0,0..0,25
     .name 'cls'
     .keywords[1]
      0] keyword - 0,10..0,18
        .arg 'i'
        .value Tuple - 0,12..0,18
          .elts[2]
           0] Name 'a' Load - 0,13..0,14
           1] Name 'b' Load - 0,16..0,17
          .ctx Load
     .body[1]
      0] Pass - 0,21..0,25
'''),

('body[0].items[0]', None, None, None, {'raw': False}, ('exec',
r'''with i as j: pass'''), (None,
r'''a, b'''),
r'''with (a, b) as j: pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] With - 0,0..0,22
     .items[1]
      0] withitem - 0,5..0,16
        .context_expr Tuple - 0,5..0,11
          .elts[2]
           0] Name 'a' Load - 0,6..0,7
           1] Name 'b' Load - 0,9..0,10
          .ctx Load
        .optional_vars Name 'j' Store - 0,15..0,16
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].items[0]', None, None, None, {'raw': False}, ('exec',
r'''with i: pass'''), (None,
r'''a, b'''),
r'''with ((a, b)): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] With - 0,0..0,19
     .items[1]
      0] withitem - 0,5..0,13
        .context_expr Tuple - 0,6..0,12
          .elts[2]
           0] Name 'a' Load - 0,7..0,8
           1] Name 'b' Load - 0,10..0,11
          .ctx Load
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0]', None, None, 'name', {}, ('exec',
r'''def oldname(): pass'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete FunctionDef.name')**'''),

('body[0]', None, None, 'name', {}, ('exec',
r'''def oldname(): pass'''), (None,
r'''new'''),
r'''def new(): pass''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] FunctionDef - 0,0..0,15
     .name 'new'
     .body[1]
      0] Pass - 0,11..0,15
'''),

('body[0]', None, None, 'name', {}, ('exec',
r'''async def oldname(): pass'''), (None,
r'''new'''),
r'''async def new(): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] AsyncFunctionDef - 0,0..0,21
     .name 'new'
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0]', None, None, 'name', {}, ('exec',
r'''class oldname: pass'''), (None,
r'''new'''),
r'''class new: pass''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] ClassDef - 0,0..0,15
     .name 'new'
     .body[1]
      0] Pass - 0,11..0,15
'''),

('body[0].value', None, None, 'id', {}, ('exec',
r'''oldname'''), (None,
r'''new'''),
r'''new''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'new' Load - 0,0..0,3
'''),

('body[0].args.args[0]', None, None, 'arg', {}, ('exec',
r'''def f(oldarg=val): pass'''), (None,
r'''new'''),
r'''def f(new=val): pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .args arguments - 0,6..0,13
       .args[1]
        0] arg - 0,6..0,9
          .arg 'new'
       .defaults[1]
        0] Name 'val' Load - 0,10..0,13
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0].names[0]', None, None, 'name', {}, ('exec',
r'''import oldname as thing'''), (None,
r'''new'''),
r'''import new as thing''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Import - 0,0..0,19
     .names[1]
      0] alias - 0,7..0,19
        .name 'new'
        .asname 'thing'
'''),

('body[0].type_params[0]', None, None, 'name', {'_ver': 12}, ('exec',
r'''def f[T](): pass'''), (None,
r'''new'''),
r'''def f[new](): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] FunctionDef - 0,0..0,18
     .name 'f'
     .body[1]
      0] Pass - 0,14..0,18
     .type_params[1]
      0] TypeVar - 0,6..0,9
        .name 'new'
'''),

('body[0].type_params[0]', None, None, 'name', {'_ver': 12}, ('exec',
r'''def f[*T](): pass'''), (None,
r'''new'''),
r'''def f[*new](): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] FunctionDef - 0,0..0,19
     .name 'f'
     .body[1]
      0] Pass - 0,15..0,19
     .type_params[1]
      0] TypeVarTuple - 0,6..0,10
        .name 'new'
'''),

('body[0].type_params[0]', None, None, 'name', {'_ver': 12}, ('exec',
r'''def f[**T](): pass'''), (None,
r'''new'''),
r'''def f[**new](): pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .body[1]
      0] Pass - 0,16..0,20
     .type_params[1]
      0] ParamSpec - 0,6..0,11
        .name 'new'
'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''i += j'''), (None,
r'''1'''),
r'''**NodeError('expecting one of (Name, Attribute, Subscript) for AugAssign.target, got Constant')**'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''i += j'''), (None,
r'''new'''),
r'''new += j''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] AugAssign - 0,0..0,8
     .target Name 'new' Store - 0,0..0,3
     .op Add - 0,4..0,5
     .value Name 'j' Load - 0,7..0,8
'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''i += j'''), (None,
r'''new.to'''),
r'''new.to += j''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] AugAssign - 0,0..0,11
     .target Attribute - 0,0..0,6
       .value Name 'new' Load - 0,0..0,3
       .attr 'to'
       .ctx Store
     .op Add - 0,7..0,8
     .value Name 'j' Load - 0,10..0,11
'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''i += j'''), (None,
r'''new[to]'''),
r'''new[to] += j''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] AugAssign - 0,0..0,12
     .target Subscript - 0,0..0,7
       .value Name 'new' Load - 0,0..0,3
       .slice Name 'to' Load - 0,4..0,6
       .ctx Store
     .op Add - 0,8..0,9
     .value Name 'j' Load - 0,11..0,12
'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''i: j = 1'''), (None,
r'''new'''),
r'''new: j = 1''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] AnnAssign - 0,0..0,10
     .target Name 'new' Store - 0,0..0,3
     .annotation Name 'j' Load - 0,5..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''i: j'''), (None,
r'''new'''),
r'''new: j''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] AnnAssign - 0,0..0,6
     .target Name 'new' Store - 0,0..0,3
     .annotation Name 'j' Load - 0,5..0,6
     .simple 1
'''),

('body[0]', None, None, 'annotation', {}, ('exec',
r'''i: j'''), (None,
r'''(yield 1)'''),
r'''i: (yield 1)''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] AnnAssign - 0,0..0,12
     .target Name 'i' Store - 0,0..0,1
     .annotation Yield - 0,4..0,11
       .value Constant 1 - 0,10..0,11
     .simple 1
'''),

('body[0]', None, None, 'annotation', {}, ('exec',
r'''i: j'''), (None,
r'''new'''),
r'''i: new''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] AnnAssign - 0,0..0,6
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'new' Load - 0,3..0,6
     .simple 1
'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''for i in j: pass'''), (None,
r'''new'''),
r'''for new in j: pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] For - 0,0..0,18
     .target Name 'new' Store - 0,4..0,7
     .iter Name 'j' Load - 0,11..0,12
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''for i in j: pass'''), (None,
r'''(new, to)'''),
r'''for (new, to) in j: pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] For - 0,0..0,24
     .target Tuple - 0,4..0,13
       .elts[2]
        0] Name 'new' Store - 0,5..0,8
        1] Name 'to' Store - 0,10..0,12
       .ctx Store
     .iter Name 'j' Load - 0,17..0,18
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0]', None, None, 'target', {}, ('exec',
r'''for i in j: pass'''), (None,
r'''[new, to]'''),
r'''for [new, to] in j: pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] For - 0,0..0,24
     .target List - 0,4..0,13
       .elts[2]
        0] Name 'new' Store - 0,5..0,8
        1] Name 'to' Store - 0,10..0,12
       .ctx Store
     .iter Name 'j' Load - 0,17..0,18
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0].value', None, None, 'target', {}, ('exec',
r'''(i := j)'''), (None,
r'''1'''),
r'''**NodeError('expecting a Name for NamedExpr.target, got Constant')**'''),

('body[0].value', None, None, 'target', {}, ('exec',
r'''(i := j)'''), (None,
r'''new'''),
r'''(new := j)''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Expr - 0,0..0,10
     .value NamedExpr - 0,1..0,9
       .target Name 'new' Store - 0,1..0,4
       .value Name 'j' Load - 0,8..0,9
'''),

('body[0].value.generators[0]', None, None, 'target', {}, ('exec',
r'''[i for i in j]'''), (None,
r'''new'''),
r'''[i for new in j]''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Expr - 0,0..0,16
     .value ListComp - 0,0..0,16
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,15
          .target Name 'new' Store - 0,7..0,10
          .iter Name 'j' Load - 0,14..0,15
          .is_async 0
'''),

('body[0].value.generators[0]', None, None, 'target', {}, ('exec',
r'''[i for i in j]'''), (None,
r'''(new, to)'''),
r'''[i for (new, to) in j]''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value ListComp - 0,0..0,22
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,21
          .target Tuple - 0,7..0,16
            .elts[2]
             0] Name 'new' Store - 0,8..0,11
             1] Name 'to' Store - 0,13..0,15
            .ctx Store
          .iter Name 'j' Load - 0,20..0,21
          .is_async 0
'''),

('body[0].value.generators[0]', None, None, 'target', {}, ('exec',
r'''[i for i in j]'''), (None,
r'''[new, to]'''),
r'''[i for [new, to] in j]''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value ListComp - 0,0..0,22
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,21
          .target List - 0,7..0,16
            .elts[2]
             0] Name 'new' Store - 0,8..0,11
             1] Name 'to' Store - 0,13..0,15
            .ctx Store
          .iter Name 'j' Load - 0,20..0,21
          .is_async 0
'''),

('body[0]', None, None, 'name', {'_ver': 12}, ('exec',
r'''type i = j'''), (None,
r'''1'''),
r'''**NodeError('expecting a Name for TypeAlias.name, got Constant')**'''),

('body[0]', None, None, 'name', {'_ver': 12}, ('exec',
r'''type i = j'''), (None,
r'''new'''),
r'''type new = j''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] TypeAlias - 0,0..0,12
     .name Name 'new' Store - 0,5..0,8
     .value Name 'j' Load - 0,11..0,12
'''),

('body[0]', None, None, None, {'_ver': 12}, ('exec',
r'''type i = j'''), (None,
r'''new'''),
r'''type i = new''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] TypeAlias - 0,0..0,12
     .name Name 'i' Store - 0,5..0,6
     .value Name 'new' Load - 0,9..0,12
'''),

('body[0].value', None, None, 'left', {'raw': False}, ('exec',
r'''i < j'''), (None,
r'''new, to'''),
r'''(new, to) < j''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Expr - 0,0..0,13
     .value Compare - 0,0..0,13
       .left Tuple - 0,0..0,9
         .elts[2]
          0] Name 'new' Load - 0,1..0,4
          1] Name 'to' Load - 0,6..0,8
         .ctx Load
       .ops[1]
        0] Lt - 0,10..0,11
       .comparators[1]
        0] Name 'j' Load - 0,12..0,13
'''),

('body[0].value', None, None, 'func', {'raw': False}, ('exec',
r'''call()'''), (None,
r'''new, to'''),
r'''(new, to)()''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Call - 0,0..0,11
       .func Tuple - 0,0..0,9
         .elts[2]
          0] Name 'new' Load - 0,1..0,4
          1] Name 'to' Load - 0,6..0,8
         .ctx Load
'''),

('body[0].cases[0].pattern', None, None, 'cls', {'raw': False}, ('exec', r'''
match a:
 case c(): pass
'''), (None,
r'''new, to'''),
r'''**NodeError('cannot put Tuple to pattern expression')**'''),

('body[0].cases[0].pattern', None, None, 'cls', {}, ('exec', r'''
match a:
 case c(): pass
'''), (None,
r'''new'''), r'''
match a:
 case new(): pass
''', r'''
Module - ROOT 0,0..1,17
  .body[1]
   0] Match - 0,0..1,17
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,17
        .pattern MatchClass - 1,6..1,11
          .cls Name 'new' Load - 1,6..1,9
        .body[1]
         0] Pass - 1,13..1,17
'''),

('body[0].cases[0].pattern', None, None, 'cls', {}, ('exec', r'''
match a:
 case c(): pass
'''), (None,
r'''new.to'''), r'''
match a:
 case new.to(): pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchClass - 1,6..1,14
          .cls Attribute - 1,6..1,12
            .value Name 'new' Load - 1,6..1,9
            .attr 'to'
            .ctx Load
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].value', 0, None, 'keys', {'raw': False}, ('exec',
r'''{i: j}'''), (None,
r'''yield 1'''),
r'''{(yield 1): j}''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Expr - 0,0..0,14
     .value Dict - 0,0..0,14
       .keys[1]
        0] Yield - 0,2..0,9
          .value Constant 1 - 0,8..0,9
       .values[1]
        0] Name 'j' Load - 0,12..0,13
'''),

('body[0].value', 0, None, 'values', {'raw': False}, ('exec',
r'''{i: j}'''), (None,
r'''yield 1'''),
r'''{i: (yield 1)}''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Expr - 0,0..0,14
     .value Dict - 0,0..0,14
       .keys[1]
        0] Name 'i' Load - 0,1..0,2
       .values[1]
        0] Yield - 0,5..0,12
          .value Constant 1 - 0,11..0,12
'''),

('body[0].value', 0, None, 'keys', {'raw': False}, ('exec',
r'''{**i}'''), (None,
r'''yield 1'''),
r'''{(yield 1): i}''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Expr - 0,0..0,14
     .value Dict - 0,0..0,14
       .keys[1]
        0] Yield - 0,2..0,9
          .value Constant 1 - 0,8..0,9
       .values[1]
        0] Name 'i' Load - 0,12..0,13
'''),

('body[0].value', 0, None, 'keys', {}, ('exec',
r'''{(yield 1): i}'''), (None,
r'''**DEL**'''),
r'''{**i}''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Dict - 0,0..0,5
       .keys[1]
        0] None
       .values[1]
        0] Name 'i' Load - 0,3..0,4
'''),

('body[0].value', 0, None, 'comparators', {'raw': False}, ('exec',
r'''a < b'''), (None,
r'''yield 1'''),
r'''a < (yield 1)''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Expr - 0,0..0,13
     .value Compare - 0,0..0,13
       .left Name 'a' Load - 0,0..0,1
       .ops[1]
        0] Lt - 0,2..0,3
       .comparators[1]
        0] Yield - 0,5..0,12
          .value Constant 1 - 0,11..0,12
'''),

('body[0].value', None, None, 'left', {'raw': False}, ('exec',
r'''a < b < c'''), (None,
r'''yield 1'''),
r'''(yield 1) < b < c''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Compare - 0,0..0,17
       .left Yield - 0,1..0,8
         .value Constant 1 - 0,7..0,8
       .ops[2]
        0] Lt - 0,10..0,11
        1] Lt - 0,14..0,15
       .comparators[2]
        0] Name 'b' Load - 0,12..0,13
        1] Name 'c' Load - 0,16..0,17
'''),

('body[0].value', 0, None, 'comparators', {'raw': False}, ('exec',
r'''a < b < c'''), (None,
r'''yield 1'''),
r'''a < (yield 1) < c''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Compare - 0,0..0,17
       .left Name 'a' Load - 0,0..0,1
       .ops[2]
        0] Lt - 0,2..0,3
        1] Lt - 0,14..0,15
       .comparators[2]
        0] Yield - 0,5..0,12
          .value Constant 1 - 0,11..0,12
        1] Name 'c' Load - 0,16..0,17
'''),

('body[0].value', 1, None, 'comparators', {'raw': False}, ('exec',
r'''a < b < c'''), (None,
r'''yield 1'''),
r'''a < b < (yield 1)''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Compare - 0,0..0,17
       .left Name 'a' Load - 0,0..0,1
       .ops[2]
        0] Lt - 0,2..0,3
        1] Lt - 0,6..0,7
       .comparators[2]
        0] Name 'b' Load - 0,4..0,5
        1] Yield - 0,9..0,16
          .value Constant 1 - 0,15..0,16
'''),

('body[0].value', 3, None, 'comparators', {}, ('exec',
r'''a < b < c'''), (None,
r'''yield 1'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', -1, None, 'comparators', {'raw': False}, ('exec',
r'''a < b < c'''), (None,
r'''yield 1'''),
r'''a < b < (yield 1)''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Compare - 0,0..0,17
       .left Name 'a' Load - 0,0..0,1
       .ops[2]
        0] Lt - 0,2..0,3
        1] Lt - 0,6..0,7
       .comparators[2]
        0] Name 'b' Load - 0,4..0,5
        1] Yield - 0,9..0,16
          .value Constant 1 - 0,15..0,16
'''),

('body[0].value', -2, None, 'comparators', {'raw': False}, ('exec',
r'''a < b < c'''), (None,
r'''yield 1'''),
r'''a < (yield 1) < c''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Compare - 0,0..0,17
       .left Name 'a' Load - 0,0..0,1
       .ops[2]
        0] Lt - 0,2..0,3
        1] Lt - 0,14..0,15
       .comparators[2]
        0] Yield - 0,5..0,12
          .value Constant 1 - 0,11..0,12
        1] Name 'c' Load - 0,16..0,17
'''),

('body[0].value', -3, None, 'comparators', {}, ('exec',
r'''a < b < c'''), (None,
r'''yield 1'''),
r'''**IndexError('index out of range')**'''),

('body[0].args', 0, None, 'defaults', {'raw': False}, ('exec',
r'''def f(a, b=1, c=2): pass'''), (None,
r'''yield 1'''),
r'''def f(a, b=(yield 1), c=2): pass''', r'''
Module - ROOT 0,0..0,32
  .body[1]
   0] FunctionDef - 0,0..0,32
     .name 'f'
     .args arguments - 0,6..0,25
       .args[3]
        0] arg - 0,6..0,7
          .arg 'a'
        1] arg - 0,9..0,10
          .arg 'b'
        2] arg - 0,22..0,23
          .arg 'c'
       .defaults[2]
        0] Yield - 0,12..0,19
          .value Constant 1 - 0,18..0,19
        1] Constant 2 - 0,24..0,25
     .body[1]
      0] Pass - 0,28..0,32
'''),

('body[0].cases[0].pattern', 0, None, 'keys', {}, ('exec', r'''
match a:
 case {1: i}: pass
'''), (None,
r'''a.b'''), r'''
match a:
 case {a.b: i}: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchMapping - 1,6..1,14
          .keys[1]
           0] Attribute - 1,7..1,10
             .value Name 'a' Load - 1,7..1,8
             .attr 'b'
             .ctx Load
          .patterns[1]
           0] MatchAs - 1,12..1,13
             .name 'i'
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0]', None, None, None, {}, ('exec',
r'''return a'''), (None,
r'''new'''),
r'''return new''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Return - 0,0..0,10
     .value Name 'new' Load - 0,7..0,10
'''),

('body[0]', None, None, None, {}, ('exec',
r'''return (a)'''), (None,
r'''new'''),
r'''return new''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Return - 0,0..0,10
     .value Name 'new' Load - 0,7..0,10
'''),

('body[0]', None, None, None, {}, ('exec',
r'''return a'''), (None,
r'''**DEL**'''),
r'''return''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Return - 0,0..0,6
'''),

('body[0]', None, None, None, {}, ('exec',
r'''return (a)'''), (None,
r'''**DEL**'''),
r'''return''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Return - 0,0..0,6
'''),

('body[0]', None, None, None, {}, ('exec',
r'''return'''), (None,
r'''**DEL**'''),
r'''return''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Return - 0,0..0,6
'''),

('body[0]', None, None, None, {}, ('exec',
r'''return'''), (None,
r'''new'''),
r'''return new''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Return - 0,0..0,10
     .value Name 'new' Load - 0,7..0,10
'''),

('body[0]', None, None, None, {}, ('exec',
r'''a: b = c'''), (None,
r'''new'''),
r'''a: b = new''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] AnnAssign - 0,0..0,10
     .target Name 'a' Store - 0,0..0,1
     .annotation Name 'b' Load - 0,3..0,4
     .value Name 'new' Load - 0,7..0,10
     .simple 1
'''),

('body[0]', None, None, None, {}, ('exec',
r'''a: b = (c)'''), (None,
r'''new'''),
r'''a: b = new''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] AnnAssign - 0,0..0,10
     .target Name 'a' Store - 0,0..0,1
     .annotation Name 'b' Load - 0,3..0,4
     .value Name 'new' Load - 0,7..0,10
     .simple 1
'''),

('body[0]', None, None, None, {}, ('exec',
r'''a: b = c'''), (None,
r'''**DEL**'''),
r'''a: b''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] AnnAssign - 0,0..0,4
     .target Name 'a' Store - 0,0..0,1
     .annotation Name 'b' Load - 0,3..0,4
     .simple 1
'''),

('body[0]', None, None, None, {}, ('exec',
r'''a: b = (c)'''), (None,
r'''**DEL**'''),
r'''a: b''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] AnnAssign - 0,0..0,4
     .target Name 'a' Store - 0,0..0,1
     .annotation Name 'b' Load - 0,3..0,4
     .simple 1
'''),

('body[0]', None, None, None, {}, ('exec',
r'''a: b'''), (None,
r'''**DEL**'''),
r'''a: b''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] AnnAssign - 0,0..0,4
     .target Name 'a' Store - 0,0..0,1
     .annotation Name 'b' Load - 0,3..0,4
     .simple 1
'''),

('body[0]', None, None, None, {}, ('exec',
r'''a: b'''), (None,
r'''new'''),
r'''a: b = new''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] AnnAssign - 0,0..0,10
     .target Name 'a' Store - 0,0..0,1
     .annotation Name 'b' Load - 0,3..0,4
     .value Name 'new' Load - 0,7..0,10
     .simple 1
'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise e'''), (None,
r'''new'''),
r'''raise new''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Raise - 0,0..0,9
     .exc Name 'new' Load - 0,6..0,9
'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise (e)'''), (None,
r'''new'''),
r'''raise new''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Raise - 0,0..0,9
     .exc Name 'new' Load - 0,6..0,9
'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise e'''), (None,
r'''**DEL**'''),
r'''raise''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Raise - 0,0..0,5
'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise (e)'''), (None,
r'''**DEL**'''),
r'''raise''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Raise - 0,0..0,5
'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise e from cause'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete Raise.exc in this state')**'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise'''), (None,
r'''**DEL**'''),
r'''raise''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Raise - 0,0..0,5
'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise'''), (None,
r'''new'''),
r'''raise new''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Raise - 0,0..0,9
     .exc Name 'new' Load - 0,6..0,9
'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise e from cause'''), (None,
r'''new'''),
r'''raise new from cause''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Raise - 0,0..0,20
     .exc Name 'new' Load - 0,6..0,9
     .cause Name 'cause' Load - 0,15..0,20
'''),

('body[0]', None, None, None, {}, ('exec',
r'''raise (e) from cause'''), (None,
r'''new'''),
r'''raise new from cause''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Raise - 0,0..0,20
     .exc Name 'new' Load - 0,6..0,9
     .cause Name 'cause' Load - 0,15..0,20
'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise e from c'''), (None,
r'''new'''),
r'''raise e from new''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Raise - 0,0..0,16
     .exc Name 'e' Load - 0,6..0,7
     .cause Name 'new' Load - 0,13..0,16
'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise e from (c)'''), (None,
r'''new'''),
r'''raise e from new''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Raise - 0,0..0,16
     .exc Name 'e' Load - 0,6..0,7
     .cause Name 'new' Load - 0,13..0,16
'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise e from c'''), (None,
r'''**DEL**'''),
r'''raise e''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Raise - 0,0..0,7
     .exc Name 'e' Load - 0,6..0,7
'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise e from (c)'''), (None,
r'''**DEL**'''),
r'''raise e''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Raise - 0,0..0,7
     .exc Name 'e' Load - 0,6..0,7
'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise (e) from c'''), (None,
r'''**DEL**'''),
r'''raise (e)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Raise - 0,0..0,9
     .exc Name 'e' Load - 0,7..0,8
'''),

('body[0]', None, None, 'cause', {'raw': False}, ('exec',
r'''raise'''), (None,
r'''**DEL**'''),
r'''raise''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Raise - 0,0..0,5
'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise e'''), (None,
r'''**DEL**'''),
r'''raise e''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Raise - 0,0..0,7
     .exc Name 'e' Load - 0,6..0,7
'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise'''), (None,
r'''c'''),
r'''**ValueError('cannot create Raise.cause in this state')**'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise e'''), (None,
r'''c'''),
r'''raise e from c''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Raise - 0,0..0,14
     .exc Name 'e' Load - 0,6..0,7
     .cause Name 'c' Load - 0,13..0,14
'''),

('body[0]', None, None, 'cause', {}, ('exec',
r'''raise (e)'''), (None,
r'''c'''),
r'''raise (e) from c''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Raise - 0,0..0,16
     .exc Name 'e' Load - 0,7..0,8
     .cause Name 'c' Load - 0,15..0,16
'''),

('body[0]', None, None, None, {}, ('exec',
r'''assert a, b'''), (None,
r'''new'''),
r'''assert new, b''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Assert - 0,0..0,13
     .test Name 'new' Load - 0,7..0,10
     .msg Name 'b' Load - 0,12..0,13
'''),

('body[0]', None, None, None, {}, ('exec',
r'''assert a, (b)'''), (None,
r'''new'''),
r'''assert new, (b)''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Assert - 0,0..0,15
     .test Name 'new' Load - 0,7..0,10
     .msg Name 'b' Load - 0,13..0,14
'''),

('body[0]', None, None, None, {}, ('exec',
r'''assert a, b'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete Assert.test')**'''),

('body[0]', None, None, 'msg', {}, ('exec',
r'''assert a, b'''), (None,
r'''new'''),
r'''assert a, new''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Assert - 0,0..0,13
     .test Name 'a' Load - 0,7..0,8
     .msg Name 'new' Load - 0,10..0,13
'''),

('body[0]', None, None, 'msg', {}, ('exec',
r'''assert a, (b)'''), (None,
r'''new'''),
r'''assert a, new''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Assert - 0,0..0,13
     .test Name 'a' Load - 0,7..0,8
     .msg Name 'new' Load - 0,10..0,13
'''),

('body[0]', None, None, 'msg', {}, ('exec',
r'''assert a, b'''), (None,
r'''**DEL**'''),
r'''assert a''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Assert - 0,0..0,8
     .test Name 'a' Load - 0,7..0,8
'''),

('body[0]', None, None, 'msg', {}, ('exec',
r'''assert a, (b)'''), (None,
r'''**DEL**'''),
r'''assert a''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Assert - 0,0..0,8
     .test Name 'a' Load - 0,7..0,8
'''),

('body[0]', None, None, 'msg', {}, ('exec',
r'''assert a'''), (None,
r'''**DEL**'''),
r'''assert a''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Assert - 0,0..0,8
     .test Name 'a' Load - 0,7..0,8
'''),

('body[0]', None, None, 'msg', {}, ('exec',
r'''assert a'''), (None,
r'''new'''),
r'''assert a, new''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Assert - 0,0..0,13
     .test Name 'a' Load - 0,7..0,8
     .msg Name 'new' Load - 0,10..0,13
'''),

('body[0].value', None, None, None, {}, ('exec',
r'''yield a'''), (None,
r'''new'''),
r'''yield new''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Yield - 0,0..0,9
       .value Name 'new' Load - 0,6..0,9
'''),

('body[0].value', None, None, None, {}, ('exec',
r'''yield (a)'''), (None,
r'''new'''),
r'''yield new''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Yield - 0,0..0,9
       .value Name 'new' Load - 0,6..0,9
'''),

('body[0].value', None, None, None, {}, ('exec',
r'''yield a'''), (None,
r'''**DEL**'''),
r'''yield''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Yield - 0,0..0,5
'''),

('body[0].value', None, None, None, {}, ('exec',
r'''yield (a)'''), (None,
r'''**DEL**'''),
r'''yield''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Yield - 0,0..0,5
'''),

('body[0].value', None, None, None, {}, ('exec',
r'''yield'''), (None,
r'''**DEL**'''),
r'''yield''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Yield - 0,0..0,5
'''),

('body[0].value', None, None, None, {}, ('exec',
r'''yield'''), (None,
r'''new'''),
r'''yield new''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Yield - 0,0..0,9
       .value Name 'new' Load - 0,6..0,9
'''),

('body[0].args.args[0]', None, None, 'annotation', {}, ('exec',
r'''def f(a: b): pass'''), (None,
r'''new'''),
r'''def f(a: new): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] FunctionDef - 0,0..0,19
     .name 'f'
     .args arguments - 0,6..0,12
       .args[1]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'new' Load - 0,9..0,12
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0].args.args[0]', None, None, 'annotation', {}, ('exec',
r'''def f(a: (b)): pass'''), (None,
r'''new'''),
r'''def f(a: new): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] FunctionDef - 0,0..0,19
     .name 'f'
     .args arguments - 0,6..0,12
       .args[1]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'new' Load - 0,9..0,12
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0].args.args[0]', None, None, 'annotation', {}, ('exec',
r'''def f(a: b): pass'''), (None,
r'''**DEL**'''),
r'''def f(a): pass''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] FunctionDef - 0,0..0,14
     .name 'f'
     .args arguments - 0,6..0,7
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
     .body[1]
      0] Pass - 0,10..0,14
'''),

('body[0].args.args[0]', None, None, 'annotation', {}, ('exec',
r'''def f(a: (b)): pass'''), (None,
r'''**DEL**'''),
r'''def f(a): pass''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] FunctionDef - 0,0..0,14
     .name 'f'
     .args arguments - 0,6..0,7
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
     .body[1]
      0] Pass - 0,10..0,14
'''),

('body[0].args.args[0]', None, None, 'annotation', {}, ('exec',
r'''def f(a): pass'''), (None,
r'''**DEL**'''),
r'''def f(a): pass''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] FunctionDef - 0,0..0,14
     .name 'f'
     .args arguments - 0,6..0,7
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
     .body[1]
      0] Pass - 0,10..0,14
'''),

('body[0].args.args[0]', None, None, 'annotation', {}, ('exec',
r'''def f(a): pass'''), (None,
r'''new'''),
r'''def f(a: new): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] FunctionDef - 0,0..0,19
     .name 'f'
     .args arguments - 0,6..0,12
       .args[1]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'new' Load - 0,9..0,12
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0].args.args[0]', None, None, 'annotation', {'_ver': 11}, ('exec',
r'''def f(a): pass'''), (None,
r'''lambda: x'''),
r'''def f(a: lambda: x): pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] FunctionDef - 0,0..0,25
     .name 'f'
     .args arguments - 0,6..0,18
       .args[1]
        0] arg - 0,6..0,18
          .arg 'a'
          .annotation Lambda - 0,9..0,18
            .body Name 'x' Load - 0,17..0,18
     .body[1]
      0] Pass - 0,21..0,25
'''),

('body[0].args.args[0]', None, None, 'annotation', {}, ('exec',
r'''def f(a :  ( b ) ): pass'''), (None,
r'''new'''),
r'''def f(a :  new ): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] FunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,6..0,14
       .args[1]
        0] arg - 0,6..0,14
          .arg 'a'
          .annotation Name 'new' Load - 0,11..0,14
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].args.args[0]', None, None, 'annotation', {}, ('exec',
r'''def f(a   :  ( b ) ): pass'''), (None,
r'''**DEL**'''),
r'''def f(a ): pass''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] FunctionDef - 0,0..0,15
     .name 'f'
     .args arguments - 0,6..0,7
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
     .body[1]
      0] Pass - 0,11..0,15
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with a as b: pass'''), (None,
r'''new'''),
r'''with a as new: pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] With - 0,0..0,19
     .items[1]
      0] withitem - 0,5..0,13
        .context_expr Name 'a' Load - 0,5..0,6
        .optional_vars Name 'new' Store - 0,10..0,13
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with a as (b): pass'''), (None,
r'''new'''),
r'''with a as new: pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] With - 0,0..0,19
     .items[1]
      0] withitem - 0,5..0,13
        .context_expr Name 'a' Load - 0,5..0,6
        .optional_vars Name 'new' Store - 0,10..0,13
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with (a as (b)): pass'''), (None,
r'''new'''),
r'''with (a as new): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] With - 0,0..0,21
     .items[1]
      0] withitem - 0,6..0,14
        .context_expr Name 'a' Load - 0,6..0,7
        .optional_vars Name 'new' Store - 0,11..0,14
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with a as b: pass'''), (None,
r'''**DEL**'''),
r'''with a: pass''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] With - 0,0..0,12
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with a as (b): pass'''), (None,
r'''**DEL**'''),
r'''with a: pass''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] With - 0,0..0,12
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with (a as (b)): pass'''), (None,
r'''**DEL**'''),
r'''with (a): pass''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] With - 0,0..0,14
     .items[1]
      0] withitem - 0,5..0,8
        .context_expr Name 'a' Load - 0,6..0,7
     .body[1]
      0] Pass - 0,10..0,14
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with (a as b): pass'''), (None,
r'''new'''),
r'''with (a as new): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] With - 0,0..0,21
     .items[1]
      0] withitem - 0,6..0,14
        .context_expr Name 'a' Load - 0,6..0,7
        .optional_vars Name 'new' Store - 0,11..0,14
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with (a as b): pass'''), (None,
r'''**DEL**'''),
r'''with (a): pass''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] With - 0,0..0,14
     .items[1]
      0] withitem - 0,5..0,8
        .context_expr Name 'a' Load - 0,6..0,7
     .body[1]
      0] Pass - 0,10..0,14
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with a: pass'''), (None,
r'''**DEL**'''),
r'''with a: pass''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] With - 0,0..0,12
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with a: pass'''), (None,
r'''new'''),
r'''with a as new: pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] With - 0,0..0,19
     .items[1]
      0] withitem - 0,5..0,13
        .context_expr Name 'a' Load - 0,5..0,6
        .optional_vars Name 'new' Store - 0,10..0,13
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with (a): pass'''), (None,
r'''new'''),
r'''with (a) as new: pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] With - 0,0..0,21
     .items[1]
      0] withitem - 0,5..0,15
        .context_expr Name 'a' Load - 0,6..0,7
        .optional_vars Name 'new' Store - 0,12..0,15
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].items[0]', None, None, 'optional_vars', {'raw': False}, ('exec',
r'''with (a): pass'''), (None,
r'''new, to'''),
r'''with (a) as (new, to): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] With - 0,0..0,27
     .items[1]
      0] withitem - 0,5..0,21
        .context_expr Name 'a' Load - 0,6..0,7
        .optional_vars Tuple - 0,12..0,21
          .elts[2]
           0] Name 'new' Store - 0,13..0,16
           1] Name 'to' Store - 0,18..0,20
          .ctx Store
     .body[1]
      0] Pass - 0,23..0,27
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with (a): pass'''), (None,
r'''[new, to]'''),
r'''with (a) as [new, to]: pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] With - 0,0..0,27
     .items[1]
      0] withitem - 0,5..0,21
        .context_expr Name 'a' Load - 0,6..0,7
        .optional_vars List - 0,12..0,21
          .elts[2]
           0] Name 'new' Store - 0,13..0,16
           1] Name 'to' Store - 0,18..0,20
          .ctx Store
     .body[1]
      0] Pass - 0,23..0,27
'''),

('body[0].items[0]', None, None, 'optional_vars', {}, ('exec',
r'''with (a): pass'''), (None,
r'''f()'''),
r'''**NodeError('expecting one of (Name, Tuple, List, Attribute, Subscript) for withitem.optional_vars, got Call')**'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1 if b: pass
'''), (None,
r'''new'''), r'''
match a:
 case 1 if new: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .guard Name 'new' Load - 1,11..1,14
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1 if (b): pass
'''), (None,
r'''new'''), r'''
match a:
 case 1 if new: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .guard Name 'new' Load - 1,11..1,14
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1 if b: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case 1: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1 if (b): pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case 1: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case 1: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
r'''new'''), r'''
match a:
 case 1 if new: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .guard Name 'new' Load - 1,11..1,14
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case (1): pass
'''), (None,
r'''new'''), r'''
match a:
 case (1) if new: pass
''', r'''
Module - ROOT 0,0..1,22
  .body[1]
   0] Match - 0,0..1,22
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,22
        .pattern MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        .guard Name 'new' Load - 1,13..1,16
        .body[1]
         0] Pass - 1,18..1,22
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1 if b  : pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case 1: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1 if (b)  : pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case 1: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case 1  : pass
'''), (None,
r'''new'''), r'''
match a:
 case 1 if new: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .guard Name 'new' Load - 1,11..1,14
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0]', None, None, 'guard', {}, ('exec', r'''
match a:
 case (1)  : pass
'''), (None,
r'''new'''), r'''
match a:
 case (1) if new: pass
''', r'''
Module - ROOT 0,0..1,22
  .body[1]
   0] Match - 0,0..1,22
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,22
        .pattern MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        .guard Name 'new' Load - 1,13..1,16
        .body[1]
         0] Pass - 1,18..1,22
'''),

('body[0].type_params[0]', None, None, 'bound', {'_ver': 13}, ('exec',
r'''type t[T: a] = ...'''), (None,
r'''new'''),
r'''type t[T: new] = ...''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] TypeAlias - 0,0..0,20
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,13
        .name 'T'
        .bound Name 'new' Load - 0,10..0,13
     .value Constant Ellipsis - 0,17..0,20
'''),

('body[0].type_params[0]', None, None, 'bound', {'_ver': 13}, ('exec',
r'''type t[T: (a)] = ...'''), (None,
r'''new'''),
r'''type t[T: new] = ...''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] TypeAlias - 0,0..0,20
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,13
        .name 'T'
        .bound Name 'new' Load - 0,10..0,13
     .value Constant Ellipsis - 0,17..0,20
'''),

('body[0].type_params[0]', None, None, 'bound', {'_ver': 13}, ('exec',
r'''type t[T: a] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T] = ...''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] TypeAlias - 0,0..0,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,8
        .name 'T'
     .value Constant Ellipsis - 0,12..0,15
'''),

('body[0].type_params[0]', None, None, 'bound', {'_ver': 13}, ('exec',
r'''type t[T: (a)] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T] = ...''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] TypeAlias - 0,0..0,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,8
        .name 'T'
     .value Constant Ellipsis - 0,12..0,15
'''),

('body[0].type_params[0]', None, None, 'bound', {'_ver': 13}, ('exec',
r'''type t[T] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T] = ...''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] TypeAlias - 0,0..0,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,8
        .name 'T'
     .value Constant Ellipsis - 0,12..0,15
'''),

('body[0].type_params[0]', None, None, 'bound', {'_ver': 13}, ('exec',
r'''type t[T] = ...'''), (None,
r'''new'''),
r'''type t[T: new] = ...''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] TypeAlias - 0,0..0,20
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,13
        .name 'T'
        .bound Name 'new' Load - 0,10..0,13
     .value Constant Ellipsis - 0,17..0,20
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T = a] = ...'''), (None,
r'''new'''),
r'''type t[T = new] = ...''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] TypeAlias - 0,0..0,21
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,14
        .name 'T'
        .default_value Name 'new' Load - 0,11..0,14
     .value Constant Ellipsis - 0,18..0,21
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T = (a)] = ...'''), (None,
r'''new'''),
r'''type t[T = new] = ...''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] TypeAlias - 0,0..0,21
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,14
        .name 'T'
        .default_value Name 'new' Load - 0,11..0,14
     .value Constant Ellipsis - 0,18..0,21
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T = a] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T] = ...''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] TypeAlias - 0,0..0,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,8
        .name 'T'
     .value Constant Ellipsis - 0,12..0,15
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T = (a)] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T] = ...''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] TypeAlias - 0,0..0,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,8
        .name 'T'
     .value Constant Ellipsis - 0,12..0,15
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T] = ...''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] TypeAlias - 0,0..0,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,8
        .name 'T'
     .value Constant Ellipsis - 0,12..0,15
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T] = ...'''), (None,
r'''new'''),
r'''type t[T = new] = ...''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] TypeAlias - 0,0..0,21
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,14
        .name 'T'
        .default_value Name 'new' Load - 0,11..0,14
     .value Constant Ellipsis - 0,18..0,21
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T: int = a] = ...'''), (None,
r'''new'''),
r'''type t[T: int = new] = ...''', r'''
Module - ROOT 0,0..0,26
  .body[1]
   0] TypeAlias - 0,0..0,26
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,19
        .name 'T'
        .bound Name 'int' Load - 0,10..0,13
        .default_value Name 'new' Load - 0,16..0,19
     .value Constant Ellipsis - 0,23..0,26
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T: (int) = (a)] = ...'''), (None,
r'''new'''),
r'''type t[T: (int) = new] = ...''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] TypeAlias - 0,0..0,28
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,21
        .name 'T'
        .bound Name 'int' Load - 0,11..0,14
        .default_value Name 'new' Load - 0,18..0,21
     .value Constant Ellipsis - 0,25..0,28
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T: int = a] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T: int] = ...''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] TypeAlias - 0,0..0,20
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,13
        .name 'T'
        .bound Name 'int' Load - 0,10..0,13
     .value Constant Ellipsis - 0,17..0,20
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T: (int) = (a)] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T: (int)] = ...''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] TypeAlias - 0,0..0,22
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,15
        .name 'T'
        .bound Name 'int' Load - 0,11..0,14
     .value Constant Ellipsis - 0,19..0,22
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T: int] = ...'''), (None,
r'''**DEL**'''),
r'''type t[T: int] = ...''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] TypeAlias - 0,0..0,20
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,13
        .name 'T'
        .bound Name 'int' Load - 0,10..0,13
     .value Constant Ellipsis - 0,17..0,20
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T: int] = ...'''), (None,
r'''new'''),
r'''type t[T: int = new] = ...''', r'''
Module - ROOT 0,0..0,26
  .body[1]
   0] TypeAlias - 0,0..0,26
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,19
        .name 'T'
        .bound Name 'int' Load - 0,10..0,13
        .default_value Name 'new' Load - 0,16..0,19
     .value Constant Ellipsis - 0,23..0,26
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[T: (int)] = ...'''), (None,
r'''new'''),
r'''type t[T: (int) = new] = ...''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] TypeAlias - 0,0..0,28
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,21
        .name 'T'
        .bound Name 'int' Load - 0,11..0,14
        .default_value Name 'new' Load - 0,18..0,21
     .value Constant Ellipsis - 0,25..0,28
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[**T = a] = ...'''), (None,
r'''new'''),
r'''type t[**T = new] = ...''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] TypeAlias - 0,0..0,23
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,16
        .name 'T'
        .default_value Name 'new' Load - 0,13..0,16
     .value Constant Ellipsis - 0,20..0,23
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[**T = (a)] = ...'''), (None,
r'''new'''),
r'''type t[**T = new] = ...''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] TypeAlias - 0,0..0,23
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,16
        .name 'T'
        .default_value Name 'new' Load - 0,13..0,16
     .value Constant Ellipsis - 0,20..0,23
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[**T = a] = ...'''), (None,
r'''**DEL**'''),
r'''type t[**T] = ...''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] TypeAlias - 0,0..0,17
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,10
        .name 'T'
     .value Constant Ellipsis - 0,14..0,17
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[**T = (a)] = ...'''), (None,
r'''**DEL**'''),
r'''type t[**T] = ...''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] TypeAlias - 0,0..0,17
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,10
        .name 'T'
     .value Constant Ellipsis - 0,14..0,17
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[**T] = ...'''), (None,
r'''**DEL**'''),
r'''type t[**T] = ...''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] TypeAlias - 0,0..0,17
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,10
        .name 'T'
     .value Constant Ellipsis - 0,14..0,17
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[**T] = ...'''), (None,
r'''new'''),
r'''type t[**T = new] = ...''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] TypeAlias - 0,0..0,23
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,16
        .name 'T'
        .default_value Name 'new' Load - 0,13..0,16
     .value Constant Ellipsis - 0,20..0,23
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[**T=a] = ...'''), (None,
r'''**DEL**'''),
r'''type t[**T] = ...''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] TypeAlias - 0,0..0,17
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,10
        .name 'T'
     .value Constant Ellipsis - 0,14..0,17
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[**T=a] = ...'''), (None,
r'''new'''),
r'''type t[**T=new] = ...''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] TypeAlias - 0,0..0,21
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,14
        .name 'T'
        .default_value Name 'new' Load - 0,11..0,14
     .value Constant Ellipsis - 0,18..0,21
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[ ** T] = ...'''), (None,
r'''new'''),
r'''type t[ ** T = new] = ...''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] TypeAlias - 0,0..0,25
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,8..0,18
        .name 'T'
        .default_value Name 'new' Load - 0,15..0,18
     .value Constant Ellipsis - 0,22..0,25
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec', r'''
type t[ \
 ** \
 T] = ...
'''), (None,
r'''new'''), r'''
type t[ \
 ** \
 T = new] = ...
''', r'''
Module - ROOT 0,0..2,15
  .body[1]
   0] TypeAlias - 0,0..2,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 1,1..2,8
        .name 'T'
        .default_value Name 'new' Load - 2,5..2,8
     .value Constant Ellipsis - 2,12..2,15
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[*T = a] = ...'''), (None,
r'''new'''),
r'''type t[*T = new] = ...''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] TypeAlias - 0,0..0,22
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,15
        .name 'T'
        .default_value Name 'new' Load - 0,12..0,15
     .value Constant Ellipsis - 0,19..0,22
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[*T = (a)] = ...'''), (None,
r'''new'''),
r'''type t[*T = new] = ...''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] TypeAlias - 0,0..0,22
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,15
        .name 'T'
        .default_value Name 'new' Load - 0,12..0,15
     .value Constant Ellipsis - 0,19..0,22
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[*T = a] = ...'''), (None,
r'''**DEL**'''),
r'''type t[*T] = ...''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] TypeAlias - 0,0..0,16
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,9
        .name 'T'
     .value Constant Ellipsis - 0,13..0,16
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[*T = (a)] = ...'''), (None,
r'''**DEL**'''),
r'''type t[*T] = ...''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] TypeAlias - 0,0..0,16
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,9
        .name 'T'
     .value Constant Ellipsis - 0,13..0,16
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[*T] = ...'''), (None,
r'''**DEL**'''),
r'''type t[*T] = ...''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] TypeAlias - 0,0..0,16
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,9
        .name 'T'
     .value Constant Ellipsis - 0,13..0,16
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[*T] = ...'''), (None,
r'''new'''),
r'''type t[*T = new] = ...''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] TypeAlias - 0,0..0,22
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,15
        .name 'T'
        .default_value Name 'new' Load - 0,12..0,15
     .value Constant Ellipsis - 0,19..0,22
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[*T=a] = ...'''), (None,
r'''**DEL**'''),
r'''type t[*T] = ...''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] TypeAlias - 0,0..0,16
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,9
        .name 'T'
     .value Constant Ellipsis - 0,13..0,16
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[*T=a] = ...'''), (None,
r'''new'''),
r'''type t[*T=new] = ...''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] TypeAlias - 0,0..0,20
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,13
        .name 'T'
        .default_value Name 'new' Load - 0,10..0,13
     .value Constant Ellipsis - 0,17..0,20
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec',
r'''type t[ * T] = ...'''), (None,
r'''new'''),
r'''type t[ * T = new] = ...''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] TypeAlias - 0,0..0,24
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,8..0,17
        .name 'T'
        .default_value Name 'new' Load - 0,14..0,17
     .value Constant Ellipsis - 0,21..0,24
'''),

('body[0].type_params[0]', None, None, 'default_value', {'_ver': 13}, ('exec', r'''
type t[ \
 * \
 T] = ...
'''), (None,
r'''new'''), r'''
type t[ \
 * \
 T = new] = ...
''', r'''
Module - ROOT 0,0..2,15
  .body[1]
   0] TypeAlias - 0,0..2,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 1,1..2,8
        .name 'T'
        .default_value Name 'new' Load - 2,5..2,8
     .value Constant Ellipsis - 2,12..2,15
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''def f() -> a: pass'''), (None,
r'''new'''),
r'''def f() -> new: pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .body[1]
      0] Pass - 0,16..0,20
     .returns Name 'new' Load - 0,11..0,14
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''def f() -> (a): pass'''), (None,
r'''new'''),
r'''def f() -> new: pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .body[1]
      0] Pass - 0,16..0,20
     .returns Name 'new' Load - 0,11..0,14
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''def f() -> a: pass'''), (None,
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''def f() -> (a): pass'''), (None,
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''def f(): pass'''), (None,
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''def f(): pass'''), (None,
r'''new'''),
r'''def f() -> new: pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .body[1]
      0] Pass - 0,16..0,20
     .returns Name 'new' Load - 0,11..0,14
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''def f() -> (a)  : pass'''), (None,
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''def f()  : pass'''), (None,
r'''new'''),
r'''def f() -> new: pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .body[1]
      0] Pass - 0,16..0,20
     .returns Name 'new' Load - 0,11..0,14
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''async def f(**b) -> a: pass'''), (None,
r'''new'''),
r'''async def f(**b) -> new: pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncFunctionDef - 0,0..0,29
     .name 'f'
     .args arguments - 0,12..0,15
       .kwarg arg - 0,14..0,15
         .arg 'b'
     .body[1]
      0] Pass - 0,25..0,29
     .returns Name 'new' Load - 0,20..0,23
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''async def f(**b) -> (a): pass'''), (None,
r'''new'''),
r'''async def f(**b) -> new: pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncFunctionDef - 0,0..0,29
     .name 'f'
     .args arguments - 0,12..0,15
       .kwarg arg - 0,14..0,15
         .arg 'b'
     .body[1]
      0] Pass - 0,25..0,29
     .returns Name 'new' Load - 0,20..0,23
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''async def f(**b) -> a: pass'''), (None,
r'''**DEL**'''),
r'''async def f(**b): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] AsyncFunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,12..0,15
       .kwarg arg - 0,14..0,15
         .arg 'b'
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''async def f(**b) -> (a): pass'''), (None,
r'''**DEL**'''),
r'''async def f(**b): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] AsyncFunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,12..0,15
       .kwarg arg - 0,14..0,15
         .arg 'b'
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''async def f(**b): pass'''), (None,
r'''**DEL**'''),
r'''async def f(**b): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] AsyncFunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,12..0,15
       .kwarg arg - 0,14..0,15
         .arg 'b'
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0]', None, None, 'returns', {}, ('exec',
r'''async def f(**b): pass'''), (None,
r'''new'''),
r'''async def f(**b) -> new: pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncFunctionDef - 0,0..0,29
     .name 'f'
     .args arguments - 0,12..0,15
       .kwarg arg - 0,14..0,15
         .arg 'b'
     .body[1]
      0] Pass - 0,25..0,29
     .returns Name 'new' Load - 0,20..0,23
'''),

('body[0]', None, None, 'op', {}, ('exec',
r'''a += b'''), (None,
r'''new'''),
r'''**SyntaxError("expecting operator, got 'new'")**'''),

('body[0].value', None, None, 'op', {}, ('exec',
r'''a and b'''), (None,
r'''new'''),
r'''**SyntaxError("expecting boolop, got 'new'")**'''),

('body[0].value', None, None, 'op', {}, ('exec',
r'''a + b'''), (None,
r'''new'''),
r'''**SyntaxError("expecting operator, got 'new'")**'''),

('body[0].value', None, None, 'op', {'raw': False}, ('exec',
r'''-a'''), (None,
r'''new'''),
r'''**SyntaxError("expecting unaryop, got 'new'")**'''),

('body[0].value', 0, None, 'ops', {}, ('exec',
r'''a < b'''), (None,
r'''new'''),
r'''**SyntaxError("expecting cmpop, got 'new'")**'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a=b): pass'''), (None,
r'''new'''),
r'''def f(*, a=new): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] FunctionDef - 0,0..0,21
     .name 'f'
     .args arguments - 0,6..0,14
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'a'
       .kw_defaults[1]
        0] Name 'new' Load - 0,11..0,14
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a=(b)): pass'''), (None,
r'''new'''),
r'''def f(*, a=new): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] FunctionDef - 0,0..0,21
     .name 'f'
     .args arguments - 0,6..0,14
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'a'
       .kw_defaults[1]
        0] Name 'new' Load - 0,11..0,14
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a=b): pass'''), (None,
r'''**DEL**'''),
r'''def f(*, a): pass''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] FunctionDef - 0,0..0,17
     .name 'f'
     .args arguments - 0,6..0,10
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'a'
       .kw_defaults[1]
        0] None
     .body[1]
      0] Pass - 0,13..0,17
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a=(b)): pass'''), (None,
r'''**DEL**'''),
r'''def f(*, a): pass''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] FunctionDef - 0,0..0,17
     .name 'f'
     .args arguments - 0,6..0,10
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'a'
       .kw_defaults[1]
        0] None
     .body[1]
      0] Pass - 0,13..0,17
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a): pass'''), (None,
r'''**DEL**'''),
r'''def f(*, a): pass''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] FunctionDef - 0,0..0,17
     .name 'f'
     .args arguments - 0,6..0,10
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'a'
       .kw_defaults[1]
        0] None
     .body[1]
      0] Pass - 0,13..0,17
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a): pass'''), (None,
r'''new'''),
r'''def f(*, a=new): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] FunctionDef - 0,0..0,21
     .name 'f'
     .args arguments - 0,6..0,14
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'a'
       .kw_defaults[1]
        0] Name 'new' Load - 0,11..0,14
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a, c=d): pass'''), (None,
r'''new'''),
r'''def f(*, a=new, c=d): pass''', r'''
Module - ROOT 0,0..0,26
  .body[1]
   0] FunctionDef - 0,0..0,26
     .name 'f'
     .args arguments - 0,6..0,19
       .kwonlyargs[2]
        0] arg - 0,9..0,10
          .arg 'a'
        1] arg - 0,16..0,17
          .arg 'c'
       .kw_defaults[2]
        0] Name 'new' Load - 0,11..0,14
        1] Name 'd' Load - 0,18..0,19
     .body[1]
      0] Pass - 0,22..0,26
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a: (int), c=d): pass'''), (None,
r'''new'''),
r'''def f(*, a: (int) = new, c=d): pass''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] FunctionDef - 0,0..0,35
     .name 'f'
     .args arguments - 0,6..0,28
       .kwonlyargs[2]
        0] arg - 0,9..0,17
          .arg 'a'
          .annotation Name 'int' Load - 0,13..0,16
        1] arg - 0,25..0,26
          .arg 'c'
       .kw_defaults[2]
        0] Name 'new' Load - 0,20..0,23
        1] Name 'd' Load - 0,27..0,28
     .body[1]
      0] Pass - 0,31..0,35
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a=b, c=d): pass'''), (None,
r'''**DEL**'''),
r'''def f(*, a, c=d): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] FunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,6..0,15
       .kwonlyargs[2]
        0] arg - 0,9..0,10
          .arg 'a'
        1] arg - 0,12..0,13
          .arg 'c'
       .kw_defaults[2]
        0] None
        1] Name 'd' Load - 0,14..0,15
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a, **c): pass'''), (None,
r'''new'''),
r'''def f(*, a=new, **c): pass''', r'''
Module - ROOT 0,0..0,26
  .body[1]
   0] FunctionDef - 0,0..0,26
     .name 'f'
     .args arguments - 0,6..0,19
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'a'
       .kw_defaults[1]
        0] Name 'new' Load - 0,11..0,14
       .kwarg arg - 0,18..0,19
         .arg 'c'
     .body[1]
      0] Pass - 0,22..0,26
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a: (int), **c): pass'''), (None,
r'''new'''),
r'''def f(*, a: (int) = new, **c): pass''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] FunctionDef - 0,0..0,35
     .name 'f'
     .args arguments - 0,6..0,28
       .kwonlyargs[1]
        0] arg - 0,9..0,17
          .arg 'a'
          .annotation Name 'int' Load - 0,13..0,16
       .kw_defaults[1]
        0] Name 'new' Load - 0,20..0,23
       .kwarg arg - 0,27..0,28
         .arg 'c'
     .body[1]
      0] Pass - 0,31..0,35
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a=b, **c): pass'''), (None,
r'''**DEL**'''),
r'''def f(*, a, **c): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] FunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,6..0,15
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'a'
       .kw_defaults[1]
        0] None
       .kwarg arg - 0,14..0,15
         .arg 'c'
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a: int = b): pass'''), (None,
r'''new'''),
r'''def f(*, a: int = new): pass''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] FunctionDef - 0,0..0,28
     .name 'f'
     .args arguments - 0,6..0,21
       .kwonlyargs[1]
        0] arg - 0,9..0,15
          .arg 'a'
          .annotation Name 'int' Load - 0,12..0,15
       .kw_defaults[1]
        0] Name 'new' Load - 0,18..0,21
     .body[1]
      0] Pass - 0,24..0,28
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a: (int) = (b)): pass'''), (None,
r'''new'''),
r'''def f(*, a: (int) = new): pass''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] FunctionDef - 0,0..0,30
     .name 'f'
     .args arguments - 0,6..0,23
       .kwonlyargs[1]
        0] arg - 0,9..0,17
          .arg 'a'
          .annotation Name 'int' Load - 0,13..0,16
       .kw_defaults[1]
        0] Name 'new' Load - 0,20..0,23
     .body[1]
      0] Pass - 0,26..0,30
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a: int = b): pass'''), (None,
r'''**DEL**'''),
r'''def f(*, a: int): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] FunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,6..0,15
       .kwonlyargs[1]
        0] arg - 0,9..0,15
          .arg 'a'
          .annotation Name 'int' Load - 0,12..0,15
       .kw_defaults[1]
        0] None
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a: (int) = (b)): pass'''), (None,
r'''**DEL**'''),
r'''def f(*, a: (int)): pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] FunctionDef - 0,0..0,24
     .name 'f'
     .args arguments - 0,6..0,17
       .kwonlyargs[1]
        0] arg - 0,9..0,17
          .arg 'a'
          .annotation Name 'int' Load - 0,13..0,16
       .kw_defaults[1]
        0] None
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a: int): pass'''), (None,
r'''**DEL**'''),
r'''def f(*, a: int): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] FunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,6..0,15
       .kwonlyargs[1]
        0] arg - 0,9..0,15
          .arg 'a'
          .annotation Name 'int' Load - 0,12..0,15
       .kw_defaults[1]
        0] None
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].args', 0, None, 'kw_defaults', {}, ('exec',
r'''def f(*, a: int): pass'''), (None,
r'''new'''),
r'''def f(*, a: int = new): pass''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] FunctionDef - 0,0..0,28
     .name 'f'
     .args arguments - 0,6..0,21
       .kwonlyargs[1]
        0] arg - 0,9..0,15
          .arg 'a'
          .annotation Name 'int' Load - 0,12..0,15
       .kw_defaults[1]
        0] Name 'new' Load - 0,18..0,21
     .body[1]
      0] Pass - 0,24..0,28
'''),

('body[0].keywords[0]', None, None, 'arg', {}, ('exec',
r'''class c(a=b): pass'''), (None,
r'''new'''),
r'''class c(new=b): pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] ClassDef - 0,0..0,20
     .name 'c'
     .keywords[1]
      0] keyword - 0,8..0,13
        .arg 'new'
        .value Name 'b' Load - 0,12..0,13
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0].keywords[0]', None, None, 'arg', {}, ('exec',
r'''class c(a=b): pass'''), (None,
r'''**DEL**'''),
r'''class c(**b): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ClassDef - 0,0..0,18
     .name 'c'
     .keywords[1]
      0] keyword - 0,8..0,11
        .value Name 'b' Load - 0,10..0,11
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0].keywords[0]', None, None, 'arg', {}, ('exec',
r'''class c(**b): pass'''), (None,
r'''**DEL**'''),
r'''class c(**b): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ClassDef - 0,0..0,18
     .name 'c'
     .keywords[1]
      0] keyword - 0,8..0,11
        .value Name 'b' Load - 0,10..0,11
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0].keywords[0]', None, None, 'arg', {}, ('exec',
r'''class c(**b): pass'''), (None,
r'''new'''),
r'''class c(new=b): pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] ClassDef - 0,0..0,20
     .name 'c'
     .keywords[1]
      0] keyword - 0,8..0,13
        .arg 'new'
        .value Name 'b' Load - 0,12..0,13
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0].keywords[0]', None, None, 'arg', {}, ('exec', r'''
class c( a
 =
 b
 ): pass
'''), (None,
r'''new'''), r'''
class c( new
 =
 b
 ): pass
''', r'''
Module - ROOT 0,0..3,8
  .body[1]
   0] ClassDef - 0,0..3,8
     .name 'c'
     .keywords[1]
      0] keyword - 0,9..2,2
        .arg 'new'
        .value Name 'b' Load - 2,1..2,2
     .body[1]
      0] Pass - 3,4..3,8
'''),

('body[0].keywords[0]', None, None, 'arg', {}, ('exec', r'''
class c( a
 =
 b
 ): pass
'''), (None,
r'''**DEL**'''), r'''
class c( **b
 ): pass
''', r'''
Module - ROOT 0,0..1,8
  .body[1]
   0] ClassDef - 0,0..1,8
     .name 'c'
     .keywords[1]
      0] keyword - 0,9..0,12
        .value Name 'b' Load - 0,11..0,12
     .body[1]
      0] Pass - 1,4..1,8
'''),

('body[0]', 1, None, 'keywords', {}, ('exec',
r'''class c(a=1, *b, c=2): pass'''), ('keyword',
r'''**new'''),
r'''class c(a=1, *b, **new): pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] ClassDef - 0,0..0,29
     .name 'c'
     .bases[1]
      0] Starred - 0,13..0,15
        .value Name 'b' Load - 0,14..0,15
        .ctx Load
     .keywords[2]
      0] keyword - 0,8..0,11
        .arg 'a'
        .value Constant 1 - 0,10..0,11
      1] keyword - 0,17..0,22
        .value Name 'new' Load - 0,19..0,22
     .body[1]
      0] Pass - 0,25..0,29
'''),

('body[0]', 0, None, 'keywords', {}, ('exec',
r'''class c(a=1, *b, c=2): pass'''), (None,
r'''**new'''),
r'''**ValueError("cannot put '**' ClassDef.keywords element at this location (non-keywords follow)")**'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
r'''a.b'''), r'''
match a:
 case a.b: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchValue - 1,6..1,9
          .value Attribute - 1,6..1,9
            .value Name 'a' Load - 1,6..1,7
            .attr 'b'
            .ctx Load
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
r'''2'''), r'''
match a:
 case 2: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchValue - 1,6..1,7
          .value Constant 2 - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
r'''2.0'''), r'''
match a:
 case 2.0: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchValue - 1,6..1,9
          .value Constant 2.0 - 1,6..1,9
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
r'''2j'''), r'''
match a:
 case 2j: pass
''', r'''
Module - ROOT 0,0..1,14
  .body[1]
   0] Match - 0,0..1,14
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,14
        .pattern MatchValue - 1,6..1,8
          .value Constant 2j - 1,6..1,8
        .body[1]
         0] Pass - 1,10..1,14
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
"\n'2'\n"), r'''
match a:
 case '2': pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchValue - 1,6..1,9
          .value Constant '2' - 1,6..1,9
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern', None, None, None, {'raw': False}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
r'''b'''),
r'''**NodeError('invalid value for MatchValue.value, got Name')**'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case 1: pass
'''), (None,
r'''1+2j'''), r'''
match a:
 case 1+2j: pass
''', r'''
match a:
 case 1 + 2j: pass
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] Match - 0,0..1,16
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,16
        .pattern MatchValue - 1,6..1,10
          .value BinOp - 1,6..1,10
            .left Constant 1 - 1,6..1,7
            .op Add - 1,7..1,8
            .right Constant 2j - 1,8..1,10
        .body[1]
         0] Pass - 1,12..1,16
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case (1): pass
'''), (None,
r'''2'''), r'''
match a:
 case (2): pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchValue - 1,7..1,8
          .value Constant 2 - 1,7..1,8
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case (1): pass
'''), (None,
r'''1+2j'''), r'''
match a:
 case (1+2j): pass
''', r'''
match a:
 case (1 + 2j): pass
''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] Match - 0,0..1,18
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,18
        .pattern MatchValue - 1,7..1,11
          .value BinOp - 1,7..1,11
            .left Constant 1 - 1,7..1,8
            .op Add - 1,8..1,9
            .right Constant 2j - 1,9..1,11
        .body[1]
         0] Pass - 1,14..1,18
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case (1+2j): pass
'''), (None,
r'''3'''), r'''
match a:
 case (3): pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchValue - 1,7..1,8
          .value Constant 3 - 1,7..1,8
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[b:]'''), (None,
r'''new'''),
r'''a[new:]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .lower Name 'new' Load - 0,2..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[(b):]'''), (None,
r'''new'''),
r'''a[new:]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .lower Name 'new' Load - 0,2..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[b:]'''), (None,
r'''**DEL**'''),
r'''a[:]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,3
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[(b):]'''), (None,
r'''**DEL**'''),
r'''a[:]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,3
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[:]'''), (None,
r'''**DEL**'''),
r'''a[:]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,3
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[:]'''), (None,
r'''new'''),
r'''a[new:]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .lower Name 'new' Load - 0,2..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[::]'''), (None,
r'''new'''),
r'''a[new::]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .lower Name 'new' Load - 0,2..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[:(b):]'''), (None,
r'''new'''),
r'''a[new:(b):]''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Subscript - 0,0..0,11
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,10
         .lower Name 'new' Load - 0,2..0,5
         .upper Name 'b' Load - 0,7..0,8
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[ : ]'''), (None,
r'''new'''),
r'''a[ new: ]''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Subscript - 0,0..0,9
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,7
         .lower Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[ b : ]'''), (None,
r'''**DEL**'''),
r'''a[ : ]''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Subscript - 0,0..0,6
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[':':]'''), (None,
r'''new'''),
r'''a[new:]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .lower Name 'new' Load - 0,2..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'lower', {}, ('exec',
r'''a[':':]'''), (None,
r'''**DEL**'''),
r'''a[:]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,3
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:b]'''), (None,
r'''new'''),
r'''a[:new]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .upper Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:(b)]'''), (None,
r'''new'''),
r'''a[:new]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .upper Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:b]'''), (None,
r'''**DEL**'''),
r'''a[:]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,3
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:(b)]'''), (None,
r'''**DEL**'''),
r'''a[:]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,3
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:]'''), (None,
r'''**DEL**'''),
r'''a[:]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,3
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:]'''), (None,
r'''new'''),
r'''a[:new]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .upper Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[::]'''), (None,
r'''new'''),
r'''a[:new:]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .upper Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[ : ]'''), (None,
r'''new'''),
r'''a[ :new ]''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Subscript - 0,0..0,9
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,7
         .upper Name 'new' Load - 0,4..0,7
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[ : b ]'''), (None,
r'''**DEL**'''),
r'''a[ : ]''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Subscript - 0,0..0,6
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[ : : ]'''), (None,
r'''new'''),
r'''a[ :new: ]''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Expr - 0,0..0,10
     .value Subscript - 0,0..0,10
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,8
         .upper Name 'new' Load - 0,4..0,7
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[ : b : ]'''), (None,
r'''**DEL**'''),
r'''a[ :: ]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:b:]'''), (None,
r'''new'''),
r'''a[:new:]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .upper Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:(b):]'''), (None,
r'''new'''),
r'''a[:new:]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .upper Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:b:]'''), (None,
r'''**DEL**'''),
r'''a[::]''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Subscript - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:(b):]'''), (None,
r'''**DEL**'''),
r'''a[::]''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Subscript - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:':']'''), (None,
r'''new'''),
r'''a[:new]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .upper Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:':']'''), (None,
r'''**DEL**'''),
r'''a[:]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,3
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:':':]'''), (None,
r'''new'''),
r'''a[:new:]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .upper Name 'new' Load - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[:':':]'''), (None,
r'''**DEL**'''),
r'''a[::]''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Subscript - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[":":':']'''), (None,
r'''new'''),
r'''a[":":new]''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Expr - 0,0..0,10
     .value Subscript - 0,0..0,10
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,9
         .lower Constant ':' - 0,2..0,5
         .upper Name 'new' Load - 0,6..0,9
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[":":':']'''), (None,
r'''**DEL**'''),
r'''a[":":]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .lower Constant ':' - 0,2..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[":":':':]'''), (None,
r'''new'''),
r'''a[":":new:]''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Subscript - 0,0..0,11
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,10
         .lower Constant ':' - 0,2..0,5
         .upper Name 'new' Load - 0,6..0,9
       .ctx Load
'''),

('body[0].value.slice', None, None, 'upper', {}, ('exec',
r'''a[":":':':]'''), (None,
r'''**DEL**'''),
r'''a[":"::]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .lower Constant ':' - 0,2..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[::b]'''), (None,
r'''new'''),
r'''a[::new]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .step Name 'new' Load - 0,4..0,7
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[::(b)]'''), (None,
r'''new'''),
r'''a[::new]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .step Name 'new' Load - 0,4..0,7
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[::b]'''), (None,
r'''**DEL**'''),
r'''a[::]''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Subscript - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[::(b)]'''), (None,
r'''**DEL**'''),
r'''a[::]''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Subscript - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[::]'''), (None,
r'''**DEL**'''),
r'''a[::]''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Subscript - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[::]'''), (None,
r'''new'''),
r'''a[::new]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .step Name 'new' Load - 0,4..0,7
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:]'''), (None,
r'''new'''),
r'''a[::new]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .step Name 'new' Load - 0,4..0,7
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[ :: ]'''), (None,
r'''new'''),
r'''a[ ::new ]''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Expr - 0,0..0,10
     .value Subscript - 0,0..0,10
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,8
         .step Name 'new' Load - 0,5..0,8
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[ : ]'''), (None,
r'''new'''),
r'''a[ ::new ]''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Expr - 0,0..0,10
     .value Subscript - 0,0..0,10
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,8
         .step Name 'new' Load - 0,5..0,8
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[ :: b ]'''), (None,
r'''**DEL**'''),
r'''a[ :: ]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[ : : ]'''), (None,
r'''new'''),
r'''a[ : :new ]''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Subscript - 0,0..0,11
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,9
         .step Name 'new' Load - 0,6..0,9
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[ : b : ]'''), (None,
r'''**DEL**'''),
r'''a[ : b : ]''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Expr - 0,0..0,10
     .value Subscript - 0,0..0,10
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,3..0,8
         .upper Name 'b' Load - 0,5..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:b]'''), (None,
r'''new'''),
r'''a[:b:new]''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Subscript - 0,0..0,9
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,8
         .upper Name 'b' Load - 0,3..0,4
         .step Name 'new' Load - 0,5..0,8
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:(b)]'''), (None,
r'''new'''),
r'''a[:(b):new]''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Subscript - 0,0..0,11
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,10
         .upper Name 'b' Load - 0,4..0,5
         .step Name 'new' Load - 0,7..0,10
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:b]'''), (None,
r'''**DEL**'''),
r'''a[:b]''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Subscript - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,4
         .upper Name 'b' Load - 0,3..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:(b)]'''), (None,
r'''**DEL**'''),
r'''a[:(b)]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .upper Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:':']'''), (None,
r'''new'''),
r'''a[:':':new]''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Subscript - 0,0..0,11
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,10
         .upper Constant ':' - 0,3..0,6
         .step Name 'new' Load - 0,7..0,10
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:':']'''), (None,
r'''**DEL**'''),
r'''a[:':']''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,6
         .upper Constant ':' - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:':':]'''), (None,
r'''new'''),
r'''a[:':':new]''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Subscript - 0,0..0,11
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,10
         .upper Constant ':' - 0,3..0,6
         .step Name 'new' Load - 0,7..0,10
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[:':':]'''), (None,
r'''**DEL**'''),
r'''a[:':':]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .upper Constant ':' - 0,3..0,6
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[::':']'''), (None,
r'''new'''),
r'''a[::new]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .step Name 'new' Load - 0,4..0,7
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[::':']'''), (None,
r'''**DEL**'''),
r'''a[::]''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Subscript - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,4
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[":":':']'''), (None,
r'''new'''),
r'''a[":":':':new]''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Expr - 0,0..0,14
     .value Subscript - 0,0..0,14
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,13
         .lower Constant ':' - 0,2..0,5
         .upper Constant ':' - 0,6..0,9
         .step Name 'new' Load - 0,10..0,13
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[":":':']'''), (None,
r'''**DEL**'''),
r'''a[":":':']''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Expr - 0,0..0,10
     .value Subscript - 0,0..0,10
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,9
         .lower Constant ':' - 0,2..0,5
         .upper Constant ':' - 0,6..0,9
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[":":':':]'''), (None,
r'''new'''),
r'''a[":":':':new]''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Expr - 0,0..0,14
     .value Subscript - 0,0..0,14
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,13
         .lower Constant ':' - 0,2..0,5
         .upper Constant ':' - 0,6..0,9
         .step Name 'new' Load - 0,10..0,13
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[":":':':]'''), (None,
r'''**DEL**'''),
r'''a[":":':':]''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Subscript - 0,0..0,11
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,10
         .lower Constant ':' - 0,2..0,5
         .upper Constant ':' - 0,6..0,9
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[":"::':']'''), (None,
r'''new'''),
r'''a[":"::new]''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value Subscript - 0,0..0,11
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,10
         .lower Constant ':' - 0,2..0,5
         .step Name 'new' Load - 0,7..0,10
       .ctx Load
'''),

('body[0].value.slice', None, None, 'step', {}, ('exec',
r'''a[":"::':']'''), (None,
r'''**DEL**'''),
r'''a[":"::]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .lower Constant ':' - 0,2..0,5
       .ctx Load
'''),

('body[0].value', None, None, 'attr', {}, ('exec',
r'''a.b'''), (None,
r'''new'''),
r'''a.new''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Attribute - 0,0..0,5
       .value Name 'a' Load - 0,0..0,1
       .attr 'new'
       .ctx Load
'''),

('body[0].value', None, None, 'attr', {}, ('exec',
r'''(a).b'''), (None,
r'''new'''),
r'''(a).new''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Attribute - 0,0..0,7
       .value Name 'a' Load - 0,1..0,2
       .attr 'new'
       .ctx Load
'''),

('body[0].value', None, None, 'attr', {}, ('exec',
r'''(a) . b'''), (None,
r'''new'''),
r'''(a) . new''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Attribute - 0,0..0,9
       .value Name 'a' Load - 0,1..0,2
       .attr 'new'
       .ctx Load
'''),

('body[0].value', None, None, 'attr', {}, ('exec',
r'''a.b'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete Attribute.attr')**'''),

('body[0].value', None, None, None, {}, ('exec',
r'''a'''), (None,
r'''new'''),
r'''new''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'new' Load - 0,0..0,3
'''),

('body[0].value', None, None, None, {}, ('exec',
r'''a'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete Name.id')**'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except e: pass
'''), (None,
r'''new'''), r'''
try: pass
except new: pass
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] Try - 0,0..1,16
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,16
        .type Name 'new' Load - 1,7..1,10
        .body[1]
         0] Pass - 1,12..1,16
'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except (e): pass
'''), (None,
r'''new'''), r'''
try: pass
except new: pass
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] Try - 0,0..1,16
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,16
        .type Name 'new' Load - 1,7..1,10
        .body[1]
         0] Pass - 1,12..1,16
'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except e: pass
'''), (None,
r'''**DEL**'''), r'''
try: pass
except: pass
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Try - 0,0..1,12
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,12
        .body[1]
         0] Pass - 1,8..1,12
'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except (e): pass
'''), (None,
r'''**DEL**'''), r'''
try: pass
except: pass
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Try - 0,0..1,12
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,12
        .body[1]
         0] Pass - 1,8..1,12
'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except e as n: pass
'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete ExceptHandler.type in this state')**'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except: pass
'''), (None,
r'''**DEL**'''), r'''
try: pass
except: pass
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Try - 0,0..1,12
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,12
        .body[1]
         0] Pass - 1,8..1,12
'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except: pass
'''), (None,
r'''new'''), r'''
try: pass
except new: pass
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] Try - 0,0..1,16
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,16
        .type Name 'new' Load - 1,7..1,10
        .body[1]
         0] Pass - 1,12..1,16
'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except e as n: pass
'''), (None,
r'''new'''), r'''
try: pass
except new as n: pass
''', r'''
Module - ROOT 0,0..1,21
  .body[1]
   0] Try - 0,0..1,21
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,21
        .type Name 'new' Load - 1,7..1,10
        .name 'n'
        .body[1]
         0] Pass - 1,17..1,21
'''),

('body[0].handlers[0]', None, None, 'type', {}, ('exec', r'''
try: pass
except (e) as n: pass
'''), (None,
r'''new'''), r'''
try: pass
except new as n: pass
''', r'''
Module - ROOT 0,0..1,21
  .body[1]
   0] Try - 0,0..1,21
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,21
        .type Name 'new' Load - 1,7..1,10
        .name 'n'
        .body[1]
         0] Pass - 1,17..1,21
'''),

('body[0].handlers[0]', None, None, 'name', {}, ('exec', r'''
try: pass
except e as n: pass
'''), (None,
r'''new'''), r'''
try: pass
except e as new: pass
''', r'''
Module - ROOT 0,0..1,21
  .body[1]
   0] Try - 0,0..1,21
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,21
        .type Name 'e' Load - 1,7..1,8
        .name 'new'
        .body[1]
         0] Pass - 1,17..1,21
'''),

('body[0].handlers[0]', None, None, 'name', {}, ('exec', r'''
try: pass
except (e) as a: pass
'''), (None,
r'''new'''), r'''
try: pass
except (e) as new: pass
''', r'''
Module - ROOT 0,0..1,23
  .body[1]
   0] Try - 0,0..1,23
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,23
        .type Name 'e' Load - 1,8..1,9
        .name 'new'
        .body[1]
         0] Pass - 1,19..1,23
'''),

('body[0].handlers[0]', None, None, 'name', {}, ('exec', r'''
try: pass
except e as n: pass
'''), (None,
r'''**DEL**'''), r'''
try: pass
except e: pass
''', r'''
Module - ROOT 0,0..1,14
  .body[1]
   0] Try - 0,0..1,14
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,14
        .type Name 'e' Load - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
'''),

('body[0].handlers[0]', None, None, 'name', {}, ('exec', r'''
try: pass
except (e) as n: pass
'''), (None,
r'''**DEL**'''), r'''
try: pass
except (e): pass
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] Try - 0,0..1,16
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,16
        .type Name 'e' Load - 1,8..1,9
        .body[1]
         0] Pass - 1,12..1,16
'''),

('body[0].handlers[0]', None, None, 'name', {}, ('exec', r'''
try: pass
except e: pass
'''), (None,
r'''**DEL**'''), r'''
try: pass
except e: pass
''', r'''
Module - ROOT 0,0..1,14
  .body[1]
   0] Try - 0,0..1,14
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,14
        .type Name 'e' Load - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
'''),

('body[0].handlers[0]', None, None, 'name', {}, ('exec', r'''
try: pass
except (e): pass
'''), (None,
r'''**DEL**'''), r'''
try: pass
except (e): pass
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] Try - 0,0..1,16
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,16
        .type Name 'e' Load - 1,8..1,9
        .body[1]
         0] Pass - 1,12..1,16
'''),

('body[0].handlers[0]', None, None, 'name', {}, ('exec', r'''
try: pass
except e: pass
'''), (None,
r'''new'''), r'''
try: pass
except e as new: pass
''', r'''
Module - ROOT 0,0..1,21
  .body[1]
   0] Try - 0,0..1,21
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,21
        .type Name 'e' Load - 1,7..1,8
        .name 'new'
        .body[1]
         0] Pass - 1,17..1,21
'''),

('body[0].handlers[0]', None, None, 'name', {'raw': False, '_ver': 14}, ('exec', r'''
try: pass
except e, f: pass
'''), (None,
r'''new'''), r'''
try: pass
except (e, f) as new: pass
''', r'''
Module - ROOT 0,0..1,26
  .body[1]
   0] Try - 0,0..1,26
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,26
        .type Tuple - 1,7..1,13
          .elts[2]
           0] Name 'e' Load - 1,8..1,9
           1] Name 'f' Load - 1,11..1,12
          .ctx Load
        .name 'new'
        .body[1]
         0] Pass - 1,22..1,26
'''),

('body[0].handlers[0]', None, None, 'name', {}, ('exec', r'''
try: pass
except: pass
'''), (None,
r'''new'''),
r'''**ValueError('cannot create ExceptHandler.name in this state')**'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''import a as b'''), (None,
r'''new'''),
r'''import a as new''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Import - 0,0..0,15
     .names[1]
      0] alias - 0,7..0,15
        .name 'a'
        .asname 'new'
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''import a as b'''), (None,
r'''**DEL**'''),
r'''import a''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Import - 0,0..0,8
     .names[1]
      0] alias - 0,7..0,8
        .name 'a'
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''import a'''), (None,
r'''new'''),
r'''import a as new''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Import - 0,0..0,15
     .names[1]
      0] alias - 0,7..0,15
        .name 'a'
        .asname 'new'
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''import a'''), (None,
r'''**DEL**'''),
r'''import a''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Import - 0,0..0,8
     .names[1]
      0] alias - 0,7..0,8
        .name 'a'
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''import a as b, c'''), (None,
r'''new'''),
r'''import a as new, c''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Import - 0,0..0,18
     .names[2]
      0] alias - 0,7..0,15
        .name 'a'
        .asname 'new'
      1] alias - 0,17..0,18
        .name 'c'
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''import a as b, c'''), (None,
r'''**DEL**'''),
r'''import a, c''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Import - 0,0..0,11
     .names[2]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'c'
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''import a, c'''), (None,
r'''new'''),
r'''import a as new, c''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Import - 0,0..0,18
     .names[2]
      0] alias - 0,7..0,15
        .name 'a'
        .asname 'new'
      1] alias - 0,17..0,18
        .name 'c'
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''import a, c'''), (None,
r'''**DEL**'''),
r'''import a, c''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Import - 0,0..0,11
     .names[2]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'c'
'''),

('body[0].names[1]', None, None, 'asname', {}, ('exec',
r'''import c, a as b'''), (None,
r'''new'''),
r'''import c, a as new''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Import - 0,0..0,18
     .names[2]
      0] alias - 0,7..0,8
        .name 'c'
      1] alias - 0,10..0,18
        .name 'a'
        .asname 'new'
'''),

('body[0].names[1]', None, None, 'asname', {}, ('exec',
r'''import c, a as b'''), (None,
r'''**DEL**'''),
r'''import c, a''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Import - 0,0..0,11
     .names[2]
      0] alias - 0,7..0,8
        .name 'c'
      1] alias - 0,10..0,11
        .name 'a'
'''),

('body[0].names[1]', None, None, 'asname', {}, ('exec',
r'''import c, a'''), (None,
r'''new'''),
r'''import c, a as new''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Import - 0,0..0,18
     .names[2]
      0] alias - 0,7..0,8
        .name 'c'
      1] alias - 0,10..0,18
        .name 'a'
        .asname 'new'
'''),

('body[0].names[1]', None, None, 'asname', {}, ('exec',
r'''import c, a'''), (None,
r'''**DEL**'''),
r'''import c, a''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Import - 0,0..0,11
     .names[2]
      0] alias - 0,7..0,8
        .name 'c'
      1] alias - 0,10..0,11
        .name 'a'
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''from z import (a as b)'''), (None,
r'''new'''),
r'''from z import (a as new)''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] ImportFrom - 0,0..0,24
     .module 'z'
     .names[1]
      0] alias - 0,15..0,23
        .name 'a'
        .asname 'new'
     .level 0
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''from z import (a as b)'''), (None,
r'''**DEL**'''),
r'''from z import (a)''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'z'
     .names[1]
      0] alias - 0,15..0,16
        .name 'a'
     .level 0
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''from z import (a)'''), (None,
r'''new'''),
r'''from z import (a as new)''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] ImportFrom - 0,0..0,24
     .module 'z'
     .names[1]
      0] alias - 0,15..0,23
        .name 'a'
        .asname 'new'
     .level 0
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''from z import (a)'''), (None,
r'''**DEL**'''),
r'''from z import (a)''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'z'
     .names[1]
      0] alias - 0,15..0,16
        .name 'a'
     .level 0
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''from z import (a as b, c)'''), (None,
r'''new'''),
r'''from z import (a as new, c)''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] ImportFrom - 0,0..0,27
     .module 'z'
     .names[2]
      0] alias - 0,15..0,23
        .name 'a'
        .asname 'new'
      1] alias - 0,25..0,26
        .name 'c'
     .level 0
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''from z import (a as b, c)'''), (None,
r'''**DEL**'''),
r'''from z import (a, c)''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] ImportFrom - 0,0..0,20
     .module 'z'
     .names[2]
      0] alias - 0,15..0,16
        .name 'a'
      1] alias - 0,18..0,19
        .name 'c'
     .level 0
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''from z import (a, c)'''), (None,
r'''new'''),
r'''from z import (a as new, c)''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] ImportFrom - 0,0..0,27
     .module 'z'
     .names[2]
      0] alias - 0,15..0,23
        .name 'a'
        .asname 'new'
      1] alias - 0,25..0,26
        .name 'c'
     .level 0
'''),

('body[0].names[0]', None, None, 'asname', {}, ('exec',
r'''from z import (a, c)'''), (None,
r'''**DEL**'''),
r'''from z import (a, c)''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] ImportFrom - 0,0..0,20
     .module 'z'
     .names[2]
      0] alias - 0,15..0,16
        .name 'a'
      1] alias - 0,18..0,19
        .name 'c'
     .level 0
'''),

('body[0].names[1]', None, None, 'asname', {}, ('exec',
r'''from z import (c, b as a)'''), (None,
r'''new'''),
r'''from z import (c, b as new)''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] ImportFrom - 0,0..0,27
     .module 'z'
     .names[2]
      0] alias - 0,15..0,16
        .name 'c'
      1] alias - 0,18..0,26
        .name 'b'
        .asname 'new'
     .level 0
'''),

('body[0].names[1]', None, None, 'asname', {}, ('exec',
r'''from z import (c, a as b)'''), (None,
r'''**DEL**'''),
r'''from z import (c, a)''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] ImportFrom - 0,0..0,20
     .module 'z'
     .names[2]
      0] alias - 0,15..0,16
        .name 'c'
      1] alias - 0,18..0,19
        .name 'a'
     .level 0
'''),

('body[0].names[1]', None, None, 'asname', {}, ('exec',
r'''from z import (c, a)'''), (None,
r'''new'''),
r'''from z import (c, a as new)''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] ImportFrom - 0,0..0,27
     .module 'z'
     .names[2]
      0] alias - 0,15..0,16
        .name 'c'
      1] alias - 0,18..0,26
        .name 'a'
        .asname 'new'
     .level 0
'''),

('body[0].names[1]', None, None, 'asname', {}, ('exec',
r'''from z import (c, a)'''), (None,
r'''**DEL**'''),
r'''from z import (c, a)''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] ImportFrom - 0,0..0,20
     .module 'z'
     .names[2]
      0] alias - 0,15..0,16
        .name 'c'
      1] alias - 0,18..0,19
        .name 'a'
     .level 0
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case 1 as a: pass
'''), (None,
r'''new'''), r'''
match a:
 case 1 as new: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchAs - 1,6..1,14
          .pattern MatchValue - 1,6..1,7
            .value Constant 1 - 1,6..1,7
          .name 'new'
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case (1) as a: pass
'''), (None,
r'''new'''), r'''
match a:
 case (1) as new: pass
''', r'''
Module - ROOT 0,0..1,22
  .body[1]
   0] Match - 0,0..1,22
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,22
        .pattern MatchAs - 1,6..1,16
          .pattern MatchValue - 1,7..1,8
            .value Constant 1 - 1,7..1,8
          .name 'new'
        .body[1]
         0] Pass - 1,18..1,22
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case (1 as a): pass
'''), (None,
r'''new'''), r'''
match a:
 case (1 as new): pass
''', r'''
Module - ROOT 0,0..1,22
  .body[1]
   0] Match - 0,0..1,22
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,22
        .pattern MatchAs - 1,7..1,15
          .pattern MatchValue - 1,7..1,8
            .value Constant 1 - 1,7..1,8
          .name 'new'
        .body[1]
         0] Pass - 1,18..1,22
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case 1 | 2 as a: pass
'''), (None,
r'''new'''), r'''
match a:
 case 1 | 2 as new: pass
''', r'''
Module - ROOT 0,0..1,24
  .body[1]
   0] Match - 0,0..1,24
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,24
        .pattern MatchAs - 1,6..1,18
          .pattern MatchOr - 1,6..1,11
            .patterns[2]
             0] MatchValue - 1,6..1,7
               .value Constant 1 - 1,6..1,7
             1] MatchValue - 1,10..1,11
               .value Constant 2 - 1,10..1,11
          .name 'new'
        .body[1]
         0] Pass - 1,20..1,24
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {}, ('exec', r'''
match a:
 case 1 | (2 as a): pass
'''), (None,
r'''new'''), r'''
match a:
 case 1 | (2 as new): pass
''', r'''
Module - ROOT 0,0..1,26
  .body[1]
   0] Match - 0,0..1,26
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,26
        .pattern MatchOr - 1,6..1,20
          .patterns[2]
           0] MatchValue - 1,6..1,7
             .value Constant 1 - 1,6..1,7
           1] MatchAs - 1,11..1,19
             .pattern MatchValue - 1,11..1,12
               .value Constant 2 - 1,11..1,12
             .name 'new'
        .body[1]
         0] Pass - 1,22..1,26
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case (1 | 2 as a): pass
'''), (None,
r'''new'''), r'''
match a:
 case (1 | 2 as new): pass
''', r'''
Module - ROOT 0,0..1,26
  .body[1]
   0] Match - 0,0..1,26
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,26
        .pattern MatchAs - 1,7..1,19
          .pattern MatchOr - 1,7..1,12
            .patterns[2]
             0] MatchValue - 1,7..1,8
               .value Constant 1 - 1,7..1,8
             1] MatchValue - 1,11..1,12
               .value Constant 2 - 1,11..1,12
          .name 'new'
        .body[1]
         0] Pass - 1,22..1,26
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {}, ('exec', r'''
match a:
 case (1 | (2 as a)): pass
'''), (None,
r'''new'''), r'''
match a:
 case (1 | (2 as new)): pass
''', r'''
Module - ROOT 0,0..1,28
  .body[1]
   0] Match - 0,0..1,28
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,28
        .pattern MatchOr - 1,7..1,21
          .patterns[2]
           0] MatchValue - 1,7..1,8
             .value Constant 1 - 1,7..1,8
           1] MatchAs - 1,12..1,20
             .pattern MatchValue - 1,12..1,13
               .value Constant 2 - 1,12..1,13
             .name 'new'
        .body[1]
         0] Pass - 1,24..1,28
'''),

('body[0].cases[0].pattern.patterns[0]', None, None, 'name', {}, ('exec', r'''
match a:
 case (1 as a) | 2: pass
'''), (None,
r'''new'''), r'''
match a:
 case (1 as new) | 2: pass
''', r'''
Module - ROOT 0,0..1,26
  .body[1]
   0] Match - 0,0..1,26
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,26
        .pattern MatchOr - 1,6..1,20
          .patterns[2]
           0] MatchAs - 1,7..1,15
             .pattern MatchValue - 1,7..1,8
               .value Constant 1 - 1,7..1,8
             .name 'new'
           1] MatchValue - 1,19..1,20
             .value Constant 2 - 1,19..1,20
        .body[1]
         0] Pass - 1,22..1,26
'''),

('body[0].cases[0].pattern.patterns[0]', None, None, 'name', {}, ('exec', r'''
match a:
 case ((1 as a) | 2): pass
'''), (None,
r'''new'''), r'''
match a:
 case ((1 as new) | 2): pass
''', r'''
Module - ROOT 0,0..1,28
  .body[1]
   0] Match - 0,0..1,28
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,28
        .pattern MatchOr - 1,7..1,21
          .patterns[2]
           0] MatchAs - 1,8..1,16
             .pattern MatchValue - 1,8..1,9
               .value Constant 1 - 1,8..1,9
             .name 'new'
           1] MatchValue - 1,20..1,21
             .value Constant 2 - 1,20..1,21
        .body[1]
         0] Pass - 1,24..1,28
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case 1 as a: pass
'''), (None,
r'''_'''),
r'''**ValueError("cannot change MatchAs with pattern into wildcard '_'")**'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case 1 as a: pass
'''), (None,
r'''**DEL**'''),
r'''**ValueError("cannot change MatchAs with pattern into wildcard '_'")**'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case a: pass
'''), (None,
r'''new'''), r'''
match a:
 case new: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchAs - 1,6..1,9
          .name 'new'
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case a: pass
'''), (None,
r'''_'''), r'''
match a:
 case _: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchAs - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0].pattern', None, None, 'name', {'raw': False}, ('exec', r'''
match a:
 case a: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case _: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchAs - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case _: pass
'''), (None,
r'''new'''), r'''
match a:
 case new: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchAs - 1,6..1,9
          .name 'new'
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern', None, None, 'name', {}, ('exec', r'''
match a:
 case _: pass
'''), (None,
r'''_'''), r'''
match a:
 case _: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchAs - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0].pattern', None, None, 'name', {'raw': False}, ('exec', r'''
match a:
 case _: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case _: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Match - 0,0..1,13
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,13
        .pattern MatchAs - 1,6..1,7
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {'raw': False}, ('exec', r'''
match a:
 case 1 | (a): pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case 1 | (_): pass
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] Match - 0,0..1,19
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,19
        .pattern MatchOr - 1,6..1,13
          .patterns[2]
           0] MatchValue - 1,6..1,7
             .value Constant 1 - 1,6..1,7
           1] MatchAs - 1,11..1,12
        .body[1]
         0] Pass - 1,15..1,19
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {'raw': False}, ('exec', r'''
match a:
 case (1 | (a)): pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case (1 | (_)): pass
''', r'''
Module - ROOT 0,0..1,21
  .body[1]
   0] Match - 0,0..1,21
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,21
        .pattern MatchOr - 1,7..1,14
          .patterns[2]
           0] MatchValue - 1,7..1,8
             .value Constant 1 - 1,7..1,8
           1] MatchAs - 1,12..1,13
        .body[1]
         0] Pass - 1,17..1,21
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {}, ('exec', r'''
match a:
 case 1 | (_): pass
'''), (None,
r'''new'''), r'''
match a:
 case 1 | (new): pass
''', r'''
Module - ROOT 0,0..1,21
  .body[1]
   0] Match - 0,0..1,21
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,21
        .pattern MatchOr - 1,6..1,15
          .patterns[2]
           0] MatchValue - 1,6..1,7
             .value Constant 1 - 1,6..1,7
           1] MatchAs - 1,11..1,14
             .name 'new'
        .body[1]
         0] Pass - 1,17..1,21
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {}, ('exec', r'''
match a:
 case (1 | (_)): pass
'''), (None,
r'''new'''), r'''
match a:
 case (1 | (new)): pass
''', r'''
Module - ROOT 0,0..1,23
  .body[1]
   0] Match - 0,0..1,23
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,23
        .pattern MatchOr - 1,7..1,16
          .patterns[2]
           0] MatchValue - 1,7..1,8
             .value Constant 1 - 1,7..1,8
           1] MatchAs - 1,12..1,15
             .name 'new'
        .body[1]
         0] Pass - 1,19..1,23
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {}, ('exec', r'''
match a:
 case 1, *b: pass
'''), (None,
r'''new'''), r'''
match a:
 case 1, *new: pass
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] Match - 0,0..1,19
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,19
        .pattern MatchSequence - 1,6..1,13
          .patterns[2]
           0] MatchValue - 1,6..1,7
             .value Constant 1 - 1,6..1,7
           1] MatchStar - 1,9..1,13
             .name 'new'
        .body[1]
         0] Pass - 1,15..1,19
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {}, ('exec', r'''
match a:
 case 1, *b: pass
'''), (None,
r'''_'''), r'''
match a:
 case 1, *_: pass
''', r'''
Module - ROOT 0,0..1,17
  .body[1]
   0] Match - 0,0..1,17
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,17
        .pattern MatchSequence - 1,6..1,11
          .patterns[2]
           0] MatchValue - 1,6..1,7
             .value Constant 1 - 1,6..1,7
           1] MatchStar - 1,9..1,11
        .body[1]
         0] Pass - 1,13..1,17
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {'raw': False}, ('exec', r'''
match a:
 case 1, *b: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case 1, *_: pass
''', r'''
Module - ROOT 0,0..1,17
  .body[1]
   0] Match - 0,0..1,17
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,17
        .pattern MatchSequence - 1,6..1,11
          .patterns[2]
           0] MatchValue - 1,6..1,7
             .value Constant 1 - 1,6..1,7
           1] MatchStar - 1,9..1,11
        .body[1]
         0] Pass - 1,13..1,17
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {}, ('exec', r'''
match a:
 case (1, *b): pass
'''), (None,
r'''new'''), r'''
match a:
 case (1, *new): pass
''', r'''
Module - ROOT 0,0..1,21
  .body[1]
   0] Match - 0,0..1,21
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,21
        .pattern MatchSequence - 1,6..1,15
          .patterns[2]
           0] MatchValue - 1,7..1,8
             .value Constant 1 - 1,7..1,8
           1] MatchStar - 1,10..1,14
             .name 'new'
        .body[1]
         0] Pass - 1,17..1,21
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {}, ('exec', r'''
match a:
 case (1, *b): pass
'''), (None,
r'''_'''), r'''
match a:
 case (1, *_): pass
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] Match - 0,0..1,19
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,19
        .pattern MatchSequence - 1,6..1,13
          .patterns[2]
           0] MatchValue - 1,7..1,8
             .value Constant 1 - 1,7..1,8
           1] MatchStar - 1,10..1,12
        .body[1]
         0] Pass - 1,15..1,19
'''),

('body[0].cases[0].pattern.patterns[1]', None, None, 'name', {'raw': False}, ('exec', r'''
match a:
 case (1, *b): pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case (1, *_): pass
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] Match - 0,0..1,19
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,19
        .pattern MatchSequence - 1,6..1,13
          .patterns[2]
           0] MatchValue - 1,7..1,8
             .value Constant 1 - 1,7..1,8
           1] MatchStar - 1,10..1,12
        .body[1]
         0] Pass - 1,15..1,19
'''),

('body[0].cases[0].pattern.patterns[0]', None, None, 'name', {}, ('exec', r'''
match a:
 case *b,: pass
'''), (None,
r'''new'''), r'''
match a:
 case *new,: pass
''', r'''
Module - ROOT 0,0..1,17
  .body[1]
   0] Match - 0,0..1,17
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,17
        .pattern MatchSequence - 1,6..1,11
          .patterns[1]
           0] MatchStar - 1,6..1,10
             .name 'new'
        .body[1]
         0] Pass - 1,13..1,17
'''),

('body[0].cases[0].pattern.patterns[0]', None, None, 'name', {}, ('exec', r'''
match a:
 case *b,: pass
'''), (None,
r'''_'''), r'''
match a:
 case *_,: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchSequence - 1,6..1,9
          .patterns[1]
           0] MatchStar - 1,6..1,8
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern.patterns[0]', None, None, 'name', {'raw': False}, ('exec', r'''
match a:
 case *b,: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case *_,: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchSequence - 1,6..1,9
          .patterns[1]
           0] MatchStar - 1,6..1,8
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern.patterns[0]', None, None, 'name', {}, ('exec', r'''
match a:
 case *_,: pass
'''), (None,
r'''new'''), r'''
match a:
 case *new,: pass
''', r'''
Module - ROOT 0,0..1,17
  .body[1]
   0] Match - 0,0..1,17
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,17
        .pattern MatchSequence - 1,6..1,11
          .patterns[1]
           0] MatchStar - 1,6..1,10
             .name 'new'
        .body[1]
         0] Pass - 1,13..1,17
'''),

('body[0].cases[0].pattern.patterns[0]', None, None, 'name', {}, ('exec', r'''
match a:
 case *_,: pass
'''), (None,
r'''_'''), r'''
match a:
 case *_,: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchSequence - 1,6..1,9
          .patterns[1]
           0] MatchStar - 1,6..1,8
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern.patterns[0]', None, None, 'name', {'raw': False}, ('exec', r'''
match a:
 case *_,: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case *_,: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchSequence - 1,6..1,9
          .patterns[1]
           0] MatchStar - 1,6..1,8
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {}: pass
'''), (None,
r'''new'''), r'''
match a:
 case {**new}: pass
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] Match - 0,0..1,19
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,19
        .pattern MatchMapping - 1,6..1,13
          .rest 'new'
        .body[1]
         0] Pass - 1,15..1,19
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {1: a}: pass
'''), (None,
r'''new'''), r'''
match a:
 case {1: a, **new}: pass
''', r'''
Module - ROOT 0,0..1,25
  .body[1]
   0] Match - 0,0..1,25
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,25
        .pattern MatchMapping - 1,6..1,19
          .keys[1]
           0] Constant 1 - 1,7..1,8
          .patterns[1]
           0] MatchAs - 1,10..1,11
             .name 'a'
          .rest 'new'
        .body[1]
         0] Pass - 1,21..1,25
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {1: a, }: pass
'''), (None,
r'''new'''), r'''
match a:
 case {1: a, **new}: pass
''', r'''
Module - ROOT 0,0..1,25
  .body[1]
   0] Match - 0,0..1,25
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,25
        .pattern MatchMapping - 1,6..1,19
          .keys[1]
           0] Constant 1 - 1,7..1,8
          .patterns[1]
           0] MatchAs - 1,10..1,11
             .name 'a'
          .rest 'new'
        .body[1]
         0] Pass - 1,21..1,25
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {**b}: pass
'''), (None,
r'''new'''), r'''
match a:
 case {**new}: pass
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] Match - 0,0..1,19
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,19
        .pattern MatchMapping - 1,6..1,13
          .rest 'new'
        .body[1]
         0] Pass - 1,15..1,19
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {1: a, **b}: pass
'''), (None,
r'''new'''), r'''
match a:
 case {1: a, **new}: pass
''', r'''
Module - ROOT 0,0..1,25
  .body[1]
   0] Match - 0,0..1,25
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,25
        .pattern MatchMapping - 1,6..1,19
          .keys[1]
           0] Constant 1 - 1,7..1,8
          .patterns[1]
           0] MatchAs - 1,10..1,11
             .name 'a'
          .rest 'new'
        .body[1]
         0] Pass - 1,21..1,25
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {1: a,  ** b }: pass
'''), (None,
r'''new'''), r'''
match a:
 case {1: a,  ** new }: pass
''', r'''
Module - ROOT 0,0..1,28
  .body[1]
   0] Match - 0,0..1,28
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,28
        .pattern MatchMapping - 1,6..1,22
          .keys[1]
           0] Constant 1 - 1,7..1,8
          .patterns[1]
           0] MatchAs - 1,10..1,11
             .name 'a'
          .rest 'new'
        .body[1]
         0] Pass - 1,24..1,28
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {**b}: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case {}: pass
''', r'''
Module - ROOT 0,0..1,14
  .body[1]
   0] Match - 0,0..1,14
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,14
        .pattern MatchMapping - 1,6..1,8
        .body[1]
         0] Pass - 1,10..1,14
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {1: a, **b}: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case {1: a}: pass
''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] Match - 0,0..1,18
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,18
        .pattern MatchMapping - 1,6..1,12
          .keys[1]
           0] Constant 1 - 1,7..1,8
          .patterns[1]
           0] MatchAs - 1,10..1,11
             .name 'a'
        .body[1]
         0] Pass - 1,14..1,18
'''),

('body[0].cases[0].pattern', None, None, 'rest', {}, ('exec', r'''
match a:
 case {1: a,  ** b }: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case {1: a}: pass
''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] Match - 0,0..1,18
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,18
        .pattern MatchMapping - 1,6..1,12
          .keys[1]
           0] Constant 1 - 1,7..1,8
          .patterns[1]
           0] MatchAs - 1,10..1,11
             .name 'a'
        .body[1]
         0] Pass - 1,14..1,18
'''),

('body[0].cases[0].pattern', 0, None, 'kwd_attrs', {}, ('exec', r'''
match a:
 case cls(a=b): pass
'''), (None,
r'''new'''), r'''
match a:
 case cls(new=b): pass
''', r'''
Module - ROOT 0,0..1,22
  .body[1]
   0] Match - 0,0..1,22
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,22
        .pattern MatchClass - 1,6..1,16
          .cls Name 'cls' Load - 1,6..1,9
          .kwd_attrs[1]
           0] 'new'
          .kwd_patterns[1]
           0] MatchAs - 1,14..1,15
             .name 'b'
        .body[1]
         0] Pass - 1,18..1,22
'''),

('body[0].cases[0].pattern', 0, None, 'kwd_attrs', {}, ('exec', r'''
match a:
 case cls(a=b): pass
'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete from MatchClass.kwd_attrs')**'''),

('body[0].cases[0].pattern', 0, None, 'kwd_attrs', {}, ('exec', r'''
match a:
 case cls(a=b): pass
'''), (None,
r'''1'''),
r'''**ParseError("expecting identifier, got '1'")**'''),

('body[0].cases[0].pattern', 1, None, 'kwd_attrs', {}, ('exec', r'''
match a:
 case cls(a=b, c=d): pass
'''), (None,
r'''new'''), r'''
match a:
 case cls(a=b, new=d): pass
''', r'''
Module - ROOT 0,0..1,27
  .body[1]
   0] Match - 0,0..1,27
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,27
        .pattern MatchClass - 1,6..1,21
          .cls Name 'cls' Load - 1,6..1,9
          .kwd_attrs[2]
           0] 'a'
           1] 'new'
          .kwd_patterns[2]
           0] MatchAs - 1,12..1,13
             .name 'b'
           1] MatchAs - 1,19..1,20
             .name 'd'
        .body[1]
         0] Pass - 1,23..1,27
'''),

('body[0].cases[0].pattern', 1, None, 'kwd_attrs', {}, ('exec', r'''
match a:
 case cls(a=(b), c=d): pass
'''), (None,
r'''new'''), r'''
match a:
 case cls(a=(b), new=d): pass
''', r'''
Module - ROOT 0,0..1,29
  .body[1]
   0] Match - 0,0..1,29
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,29
        .pattern MatchClass - 1,6..1,23
          .cls Name 'cls' Load - 1,6..1,9
          .kwd_attrs[2]
           0] 'a'
           1] 'new'
          .kwd_patterns[2]
           0] MatchAs - 1,13..1,14
             .name 'b'
           1] MatchAs - 1,21..1,22
             .name 'd'
        .body[1]
         0] Pass - 1,25..1,29
'''),

('body[0].cases[0].pattern', 0, None, 'kwd_attrs', {}, ('exec', r'''
match a:
 case cls( a = ( b ) , c=d): pass
'''), (None,
r'''new'''), r'''
match a:
 case cls( new = ( b ) , c=d): pass
''', r'''
Module - ROOT 0,0..1,35
  .body[1]
   0] Match - 0,0..1,35
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,35
        .pattern MatchClass - 1,6..1,29
          .cls Name 'cls' Load - 1,6..1,9
          .kwd_attrs[2]
           0] 'new'
           1] 'c'
          .kwd_patterns[2]
           0] MatchAs - 1,19..1,20
             .name 'b'
           1] MatchAs - 1,27..1,28
             .name 'd'
        .body[1]
         0] Pass - 1,31..1,35
'''),

('body[0].cases[0].pattern', 1, None, 'kwd_attrs', {}, ('exec', r'''
match a:
 case cls(a=(b),  c = d): pass
'''), (None,
r'''new'''), r'''
match a:
 case cls(a=(b),  new = d): pass
''', r'''
Module - ROOT 0,0..1,32
  .body[1]
   0] Match - 0,0..1,32
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,32
        .pattern MatchClass - 1,6..1,26
          .cls Name 'cls' Load - 1,6..1,9
          .kwd_attrs[2]
           0] 'a'
           1] 'new'
          .kwd_patterns[2]
           0] MatchAs - 1,13..1,14
             .name 'b'
           1] MatchAs - 1,24..1,25
             .name 'd'
        .body[1]
         0] Pass - 1,28..1,32
'''),

('body[0]', 0, None, None, {}, ('exec',
r'''del a, (b), c'''), (None,
r'''**DEL**'''),
r'''del (b), c''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Delete - 0,0..0,10
     .targets[2]
      0] Name 'b' Del - 0,5..0,6
      1] Name 'c' Del - 0,9..0,10
'''),

('body[0]', 0, None, None, {}, ('exec',
r'''del a, (b), c'''), (None,
r'''new'''),
r'''del new, (b), c''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Delete - 0,0..0,15
     .targets[3]
      0] Name 'new' Del - 0,4..0,7
      1] Name 'b' Del - 0,10..0,11
      2] Name 'c' Del - 0,14..0,15
'''),

('body[0]', 1, None, None, {}, ('exec',
r'''del a, (b), c'''), (None,
r'''new'''),
r'''del a, new, c''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Delete - 0,0..0,13
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'new' Del - 0,7..0,10
      2] Name 'c' Del - 0,12..0,13
'''),

('body[0]', 2, None, None, {}, ('exec',
r'''del a, (b), c'''), (None,
r'''new'''),
r'''del a, (b), new''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Delete - 0,0..0,15
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,8..0,9
      2] Name 'new' Del - 0,12..0,15
'''),

('body[0]', -1, None, None, {}, ('exec',
r'''del a, (b), c'''), (None,
r'''new'''),
r'''del a, (b), new''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Delete - 0,0..0,15
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,8..0,9
      2] Name 'new' Del - 0,12..0,15
'''),

('body[0]', -1, None, None, {'raw': False}, ('exec',
r'''del a, (b), c'''), (None,
r'''x, y'''),
r'''del a, (b), (x, y)''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Delete - 0,0..0,18
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,8..0,9
      2] Tuple - 0,12..0,18
        .elts[2]
         0] Name 'x' Del - 0,13..0,14
         1] Name 'y' Del - 0,16..0,17
        .ctx Del
'''),

('body[0]', -1, None, None, {}, ('exec',
r'''del a, (b), c'''), (None,
r'''f()'''),
r'''**NodeError('invalid value for Delete.targets, got Call')**'''),

('body[0]', -4, None, None, {}, ('exec',
r'''del a, (b), c'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'decorator_list', {'raw': False}, ('exec', r'''
@a
@(b)
def c(): pass
'''), (None,
r'''**DEL**'''), r'''
@(b)
def c(): pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] FunctionDef - 1,0..1,13
     .name 'c'
     .body[1]
      0] Pass - 1,9..1,13
     .decorator_list[1]
      0] Name 'b' Load - 0,2..0,3
'''),

('body[0]', 0, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
def c(): pass
'''), (None,
r'''new'''), r'''
@new
@(b)
def c(): pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 2,0..2,13
     .name 'c'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'new' Load - 0,1..0,4
      1] Name 'b' Load - 1,2..1,3
'''),

('body[0]', 1, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
def c(): pass
'''), (None,
r'''new'''), r'''
@a
@new
def c(): pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 2,0..2,13
     .name 'c'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'new' Load - 1,1..1,4
'''),

('body[0]', -1, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
def c(): pass
'''), (None,
r'''new'''), r'''
@a
@new
def c(): pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 2,0..2,13
     .name 'c'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'new' Load - 1,1..1,4
'''),

('body[0]', -2, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
def c(): pass
'''), (None,
r'''f()'''), r'''
@f()
@(b)
def c(): pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 2,0..2,13
     .name 'c'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Call - 0,1..0,4
        .func Name 'f' Load - 0,1..0,2
      1] Name 'b' Load - 1,2..1,3
'''),

('body[0]', -4, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
def c(): pass
'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'decorator_list', {'raw': False}, ('exec', r'''
@a
@(b)
async def c(): pass
'''), (None,
r'''**DEL**'''), r'''
@(b)
async def c(): pass
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] AsyncFunctionDef - 1,0..1,19
     .name 'c'
     .body[1]
      0] Pass - 1,15..1,19
     .decorator_list[1]
      0] Name 'b' Load - 0,2..0,3
'''),

('body[0]', 0, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
async def c(): pass
'''), (None,
r'''new'''), r'''
@new
@(b)
async def c(): pass
''', r'''
Module - ROOT 0,0..2,19
  .body[1]
   0] AsyncFunctionDef - 2,0..2,19
     .name 'c'
     .body[1]
      0] Pass - 2,15..2,19
     .decorator_list[2]
      0] Name 'new' Load - 0,1..0,4
      1] Name 'b' Load - 1,2..1,3
'''),

('body[0]', 1, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
async def c(): pass
'''), (None,
r'''new'''), r'''
@a
@new
async def c(): pass
''', r'''
Module - ROOT 0,0..2,19
  .body[1]
   0] AsyncFunctionDef - 2,0..2,19
     .name 'c'
     .body[1]
      0] Pass - 2,15..2,19
     .decorator_list[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'new' Load - 1,1..1,4
'''),

('body[0]', -1, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
async def c(): pass
'''), (None,
r'''new'''), r'''
@a
@new
async def c(): pass
''', r'''
Module - ROOT 0,0..2,19
  .body[1]
   0] AsyncFunctionDef - 2,0..2,19
     .name 'c'
     .body[1]
      0] Pass - 2,15..2,19
     .decorator_list[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'new' Load - 1,1..1,4
'''),

('body[0]', -2, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
async def c(): pass
'''), (None,
r'''f()'''), r'''
@f()
@(b)
async def c(): pass
''', r'''
Module - ROOT 0,0..2,19
  .body[1]
   0] AsyncFunctionDef - 2,0..2,19
     .name 'c'
     .body[1]
      0] Pass - 2,15..2,19
     .decorator_list[2]
      0] Call - 0,1..0,4
        .func Name 'f' Load - 0,1..0,2
      1] Name 'b' Load - 1,2..1,3
'''),

('body[0]', -4, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
async def c(): pass
'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'decorator_list', {'raw': False}, ('exec', r'''
@a
@(b)
class c: pass
'''), (None,
r'''**DEL**'''), r'''
@(b)
class c: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] ClassDef - 1,0..1,13
     .name 'c'
     .body[1]
      0] Pass - 1,9..1,13
     .decorator_list[1]
      0] Name 'b' Load - 0,2..0,3
'''),

('body[0]', 0, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
class c: pass
'''), (None,
r'''new'''), r'''
@new
@(b)
class c: pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] ClassDef - 2,0..2,13
     .name 'c'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'new' Load - 0,1..0,4
      1] Name 'b' Load - 1,2..1,3
'''),

('body[0]', 1, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
class c: pass
'''), (None,
r'''new'''), r'''
@a
@new
class c: pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] ClassDef - 2,0..2,13
     .name 'c'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'new' Load - 1,1..1,4
'''),

('body[0]', -1, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
class c: pass
'''), (None,
r'''new'''), r'''
@a
@new
class c: pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] ClassDef - 2,0..2,13
     .name 'c'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'new' Load - 1,1..1,4
'''),

('body[0]', -2, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
class c: pass
'''), (None,
r'''f()'''), r'''
@f()
@(b)
class c: pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] ClassDef - 2,0..2,13
     .name 'c'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Call - 0,1..0,4
        .func Name 'f' Load - 0,1..0,2
      1] Name 'b' Load - 1,2..1,3
'''),

('body[0]', -4, None, 'decorator_list', {}, ('exec', r'''
@a
@(b)
class c: pass
'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'bases', {}, ('exec',
r'''class c(a, (b)): pass'''), (None,
r'''**DEL**'''),
r'''class c((b)): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ClassDef - 0,0..0,18
     .name 'c'
     .bases[1]
      0] Name 'b' Load - 0,9..0,10
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0]', 0, None, 'bases', {}, ('exec',
r'''class c(a, (b)): pass'''), (None,
r'''new'''),
r'''class c(new, (b)): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] ClassDef - 0,0..0,23
     .name 'c'
     .bases[2]
      0] Name 'new' Load - 0,8..0,11
      1] Name 'b' Load - 0,14..0,15
     .body[1]
      0] Pass - 0,19..0,23
'''),

('body[0]', 1, None, 'bases', {}, ('exec',
r'''class c(a, (b)): pass'''), (None,
r'''new'''),
r'''class c(a, new): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] ClassDef - 0,0..0,21
     .name 'c'
     .bases[2]
      0] Name 'a' Load - 0,8..0,9
      1] Name 'new' Load - 0,11..0,14
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0]', -1, None, 'bases', {}, ('exec',
r'''class c(a, (b)): pass'''), (None,
r'''new'''),
r'''class c(a, new): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] ClassDef - 0,0..0,21
     .name 'c'
     .bases[2]
      0] Name 'a' Load - 0,8..0,9
      1] Name 'new' Load - 0,11..0,14
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0]', -2, None, 'bases', {}, ('exec',
r'''class c(a, (b)): pass'''), (None,
r'''f()'''),
r'''class c(f(), (b)): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] ClassDef - 0,0..0,23
     .name 'c'
     .bases[2]
      0] Call - 0,8..0,11
        .func Name 'f' Load - 0,8..0,9
      1] Name 'b' Load - 0,14..0,15
     .body[1]
      0] Pass - 0,19..0,23
'''),

('body[0]', -4, None, 'bases', {}, ('exec',
r'''class c(a, (b)): pass'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'bases', {'raw': False}, ('exec',
r'''class c(a): pass'''), (None,
r'''**DEL**'''),
r'''class c: pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] ClassDef - 0,0..0,13
     .name 'c'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0]', 0, None, 'bases', {}, ('exec',
r'''class c(a): pass'''), (None,
r'''new'''),
r'''class c(new): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ClassDef - 0,0..0,18
     .name 'c'
     .bases[1]
      0] Name 'new' Load - 0,8..0,11
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0]', 0, None, 'bases', {}, ('exec',
r'''class c(a,): pass'''), (None,
r'''new'''),
r'''class c(new,): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] ClassDef - 0,0..0,19
     .name 'c'
     .bases[1]
      0] Name 'new' Load - 0,8..0,11
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0]', 0, None, 'bases', {'raw': False}, ('exec',
r'''class c((a)): pass'''), (None,
r'''**DEL**'''),
r'''class c: pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] ClassDef - 0,0..0,13
     .name 'c'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0]', 0, None, 'bases', {}, ('exec',
r'''class c((a)): pass'''), (None,
r'''new'''),
r'''class c(new): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ClassDef - 0,0..0,18
     .name 'c'
     .bases[1]
      0] Name 'new' Load - 0,8..0,11
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0]', 0, None, 'bases', {}, ('exec',
r'''class c((a),): pass'''), (None,
r'''new'''),
r'''class c(new,): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] ClassDef - 0,0..0,19
     .name 'c'
     .bases[1]
      0] Name 'new' Load - 0,8..0,11
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0].value', 0, None, None, {'raw': False}, ('exec',
r'''a and (b) and c'''), (None,
r'''**DEL**'''),
r'''(b) and c''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value BoolOp - 0,0..0,9
       .op And
       .values[2]
        0] Name 'b' Load - 0,1..0,2
        1] Name 'c' Load - 0,8..0,9
'''),

('body[0].value', 0, None, None, {}, ('exec',
r'''a and (b) and c'''), (None,
r'''new'''),
r'''new and (b) and c''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value BoolOp - 0,0..0,17
       .op And
       .values[3]
        0] Name 'new' Load - 0,0..0,3
        1] Name 'b' Load - 0,9..0,10
        2] Name 'c' Load - 0,16..0,17
'''),

('body[0].value', 1, None, None, {}, ('exec',
r'''a and (b) and c'''), (None,
r'''new'''),
r'''a and new and c''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Expr - 0,0..0,15
     .value BoolOp - 0,0..0,15
       .op And
       .values[3]
        0] Name 'a' Load - 0,0..0,1
        1] Name 'new' Load - 0,6..0,9
        2] Name 'c' Load - 0,14..0,15
'''),

('body[0].value', -1, None, None, {}, ('exec',
r'''a and (b) and c'''), (None,
r'''new'''),
r'''a and (b) and new''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value BoolOp - 0,0..0,17
       .op And
       .values[3]
        0] Name 'a' Load - 0,0..0,1
        1] Name 'b' Load - 0,7..0,8
        2] Name 'new' Load - 0,14..0,17
'''),

('body[0].value', -2, None, None, {}, ('exec',
r'''a and (b) and c'''), (None,
r'''f()'''),
r'''a and f() and c''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Expr - 0,0..0,15
     .value BoolOp - 0,0..0,15
       .op And
       .values[3]
        0] Name 'a' Load - 0,0..0,1
        1] Call - 0,6..0,9
          .func Name 'f' Load - 0,6..0,7
        2] Name 'c' Load - 0,14..0,15
'''),

('body[0].value', -4, None, None, {}, ('exec',
r'''a and (b) and c'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].value.generators[0]', 0, None, 'ifs', {'raw': False}, ('exec',
r'''[i for i in j if a if (b)]'''), (None,
r'''**DEL**'''),
r'''[i for i in j if (b)]''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Expr - 0,0..0,21
     .value ListComp - 0,0..0,21
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,20
          .target Name 'i' Store - 0,7..0,8
          .iter Name 'j' Load - 0,12..0,13
          .ifs[1]
           0] Name 'b' Load - 0,18..0,19
          .is_async 0
'''),

('body[0].value.generators[0]', 0, None, 'ifs', {}, ('exec',
r'''[i for i in j if a if (b)]'''), (None,
r'''new'''),
r'''[i for i in j if new if (b)]''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] Expr - 0,0..0,28
     .value ListComp - 0,0..0,28
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,27
          .target Name 'i' Store - 0,7..0,8
          .iter Name 'j' Load - 0,12..0,13
          .ifs[2]
           0] Name 'new' Load - 0,17..0,20
           1] Name 'b' Load - 0,25..0,26
          .is_async 0
'''),

('body[0].value.generators[0]', 1, None, 'ifs', {}, ('exec',
r'''[i for i in j if a if (b)]'''), (None,
r'''new'''),
r'''[i for i in j if a if new]''', r'''
Module - ROOT 0,0..0,26
  .body[1]
   0] Expr - 0,0..0,26
     .value ListComp - 0,0..0,26
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,25
          .target Name 'i' Store - 0,7..0,8
          .iter Name 'j' Load - 0,12..0,13
          .ifs[2]
           0] Name 'a' Load - 0,17..0,18
           1] Name 'new' Load - 0,22..0,25
          .is_async 0
'''),

('body[0].value.generators[0]', -1, None, 'ifs', {}, ('exec',
r'''[i for i in j if a if (b)]'''), (None,
r'''new'''),
r'''[i for i in j if a if new]''', r'''
Module - ROOT 0,0..0,26
  .body[1]
   0] Expr - 0,0..0,26
     .value ListComp - 0,0..0,26
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,25
          .target Name 'i' Store - 0,7..0,8
          .iter Name 'j' Load - 0,12..0,13
          .ifs[2]
           0] Name 'a' Load - 0,17..0,18
           1] Name 'new' Load - 0,22..0,25
          .is_async 0
'''),

('body[0].value.generators[0]', -2, None, 'ifs', {}, ('exec',
r'''[i for i in j if a if (b)]'''), (None,
r'''f()'''),
r'''[i for i in j if f() if (b)]''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] Expr - 0,0..0,28
     .value ListComp - 0,0..0,28
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,27
          .target Name 'i' Store - 0,7..0,8
          .iter Name 'j' Load - 0,12..0,13
          .ifs[2]
           0] Call - 0,17..0,20
             .func Name 'f' Load - 0,17..0,18
           1] Name 'b' Load - 0,25..0,26
          .is_async 0
'''),

('body[0].value.generators[0]', -4, None, 'ifs', {}, ('exec',
r'''[i for i in j if a if (b)]'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', 0, None, 'args', {}, ('exec',
r'''call(a, (b))'''), (None,
r'''**DEL**'''),
r'''call((b))''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Call - 0,0..0,9
       .func Name 'call' Load - 0,0..0,4
       .args[1]
        0] Name 'b' Load - 0,6..0,7
'''),

('body[0].value', 0, None, 'args', {}, ('exec',
r'''call(a, (b))'''), (None,
r'''new'''),
r'''call(new, (b))''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Expr - 0,0..0,14
     .value Call - 0,0..0,14
       .func Name 'call' Load - 0,0..0,4
       .args[2]
        0] Name 'new' Load - 0,5..0,8
        1] Name 'b' Load - 0,11..0,12
'''),

('body[0].value', 1, None, 'args', {}, ('exec',
r'''call(a, (b))'''), (None,
r'''new'''),
r'''call(a, new)''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value Call - 0,0..0,12
       .func Name 'call' Load - 0,0..0,4
       .args[2]
        0] Name 'a' Load - 0,5..0,6
        1] Name 'new' Load - 0,8..0,11
'''),

('body[0].value', -1, None, 'args', {}, ('exec',
r'''call(a, (b))'''), (None,
r'''new'''),
r'''call(a, new)''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value Call - 0,0..0,12
       .func Name 'call' Load - 0,0..0,4
       .args[2]
        0] Name 'a' Load - 0,5..0,6
        1] Name 'new' Load - 0,8..0,11
'''),

('body[0].value', -2, None, 'args', {}, ('exec',
r'''call(a, (b))'''), (None,
r'''f()'''),
r'''call(f(), (b))''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Expr - 0,0..0,14
     .value Call - 0,0..0,14
       .func Name 'call' Load - 0,0..0,4
       .args[2]
        0] Call - 0,5..0,8
          .func Name 'f' Load - 0,5..0,6
        1] Name 'b' Load - 0,11..0,12
'''),

('body[0].value', -4, None, 'args', {}, ('exec',
r'''call(a, (b))'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', 0, None, 'args', {}, ('exec',
r'''call(i for i in j)'''), (None,
r'''new'''),
r'''call(new)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Call - 0,0..0,9
       .func Name 'call' Load - 0,0..0,4
       .args[1]
        0] Name 'new' Load - 0,5..0,8
'''),

('body[0].value', 0, None, 'args', {}, ('exec',
r'''call((i for i in j))'''), (None,
r'''new'''),
r'''call(new)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Call - 0,0..0,9
       .func Name 'call' Load - 0,0..0,4
       .args[1]
        0] Name 'new' Load - 0,5..0,8
'''),

('body[0].value', 0, None, 'args', {}, ('exec',
r'''call(i for i in j)'''), (None,
r'''(a for a in b)'''),
r'''call((a for a in b))''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Expr - 0,0..0,20
     .value Call - 0,0..0,20
       .func Name 'call' Load - 0,0..0,4
       .args[1]
        0] GeneratorExp - 0,5..0,19
          .elt Name 'a' Load - 0,6..0,7
          .generators[1]
           0] comprehension - 0,8..0,18
             .target Name 'a' Store - 0,12..0,13
             .iter Name 'b' Load - 0,17..0,18
             .is_async 0
'''),

('body[0].value', 0, None, 'args', {}, ('exec',
r'''call((i for i in j))'''), (None,
r'''(a for a in b)'''),
r'''call((a for a in b))''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Expr - 0,0..0,20
     .value Call - 0,0..0,20
       .func Name 'call' Load - 0,0..0,4
       .args[1]
        0] GeneratorExp - 0,5..0,19
          .elt Name 'a' Load - 0,6..0,7
          .generators[1]
           0] comprehension - 0,8..0,18
             .target Name 'a' Store - 0,12..0,13
             .iter Name 'b' Load - 0,17..0,18
             .is_async 0
'''),

('body[0].cases[0].pattern', 0, None, None, {}, ('exec', r'''
match a:
 case 1 as b, (2): pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case (2),: pass
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] Match - 0,0..1,16
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,16
        .pattern MatchSequence - 1,6..1,10
          .patterns[1]
           0] MatchValue - 1,7..1,8
             .value Constant 2 - 1,7..1,8
        .body[1]
         0] Pass - 1,12..1,16
'''),

('body[0].cases[0].pattern', 1, None, None, {}, ('exec', r'''
match a:
 case 1 as b, (2): pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case 1 as b,: pass
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] Match - 0,0..1,19
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,19
        .pattern MatchSequence - 1,6..1,13
          .patterns[1]
           0] MatchAs - 1,6..1,12
             .pattern MatchValue - 1,6..1,7
               .value Constant 1 - 1,6..1,7
             .name 'b'
        .body[1]
         0] Pass - 1,15..1,19
'''),

('body[0].cases[0].pattern', 0, None, None, {}, ('exec', r'''
match a:
 case 1 as b, (2): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case new, (2): pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchSequence - 1,6..1,14
          .patterns[2]
           0] MatchAs - 1,6..1,9
             .name 'new'
           1] MatchValue - 1,12..1,13
             .value Constant 2 - 1,12..1,13
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0].pattern', 1, None, None, {}, ('exec', r'''
match a:
 case 1 as b, (2): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case 1 as b, new: pass
''', r'''
Module - ROOT 0,0..1,23
  .body[1]
   0] Match - 0,0..1,23
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,23
        .pattern MatchSequence - 1,6..1,17
          .patterns[2]
           0] MatchAs - 1,6..1,12
             .pattern MatchValue - 1,6..1,7
               .value Constant 1 - 1,6..1,7
             .name 'b'
           1] MatchAs - 1,14..1,17
             .name 'new'
        .body[1]
         0] Pass - 1,19..1,23
'''),

('body[0].cases[0].pattern', -1, None, None, {}, ('exec', r'''
match a:
 case 1 as b, (2): pass
'''), ('pattern',
r'''{1: c, **d}'''), r'''
match a:
 case 1 as b, {1: c, **d}: pass
''', r'''
Module - ROOT 0,0..1,31
  .body[1]
   0] Match - 0,0..1,31
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,31
        .pattern MatchSequence - 1,6..1,25
          .patterns[2]
           0] MatchAs - 1,6..1,12
             .pattern MatchValue - 1,6..1,7
               .value Constant 1 - 1,6..1,7
             .name 'b'
           1] MatchMapping - 1,14..1,25
             .keys[1]
              0] Constant 1 - 1,15..1,16
             .patterns[1]
              0] MatchAs - 1,18..1,19
                .name 'c'
             .rest 'd'
        .body[1]
         0] Pass - 1,27..1,31
'''),

('body[0].cases[0].pattern', -2, None, None, {}, ('exec', r'''
match a:
 case 1 as b, (2): pass
'''), ('pattern',
r'''f(c=d)'''), r'''
match a:
 case f(c=d), (2): pass
''', r'''
Module - ROOT 0,0..1,23
  .body[1]
   0] Match - 0,0..1,23
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,23
        .pattern MatchSequence - 1,6..1,17
          .patterns[2]
           0] MatchClass - 1,6..1,12
             .cls Name 'f' Load - 1,6..1,7
             .kwd_attrs[1]
              0] 'c'
             .kwd_patterns[1]
              0] MatchAs - 1,10..1,11
                .name 'd'
           1] MatchValue - 1,15..1,16
             .value Constant 2 - 1,15..1,16
        .body[1]
         0] Pass - 1,19..1,23
'''),

('body[0].cases[0].pattern', -4, None, None, {}, ('exec', r'''
match a:
 case 1 as b, (2): pass
'''), ('pattern',
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].cases[0].pattern', 0, None, 'patterns', {}, ('exec', r'''
match a:
 case {1: a, 2: (b), **rest}: pass
'''), ('pattern',
r'''**DEL**'''),
r'''**ValueError('cannot delete from MatchMapping.patterns')**'''),

('body[0].cases[0].pattern', 0, None, 'patterns', {}, ('exec', r'''
match a:
 case {1: a, 2: (b), **rest}: pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case {1: new, 2: (b), **rest}: pass
''', r'''
Module - ROOT 0,0..1,36
  .body[1]
   0] Match - 0,0..1,36
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,36
        .pattern MatchMapping - 1,6..1,30
          .keys[2]
           0] Constant 1 - 1,7..1,8
           1] Constant 2 - 1,15..1,16
          .patterns[2]
           0] MatchAs - 1,10..1,13
             .name 'new'
           1] MatchAs - 1,19..1,20
             .name 'b'
          .rest 'rest'
        .body[1]
         0] Pass - 1,32..1,36
'''),

('body[0].cases[0].pattern', 1, None, 'patterns', {}, ('exec', r'''
match a:
 case {1: a, 2: (b), **rest}: pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case {1: a, 2: new, **rest}: pass
''', r'''
Module - ROOT 0,0..1,34
  .body[1]
   0] Match - 0,0..1,34
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,34
        .pattern MatchMapping - 1,6..1,28
          .keys[2]
           0] Constant 1 - 1,7..1,8
           1] Constant 2 - 1,13..1,14
          .patterns[2]
           0] MatchAs - 1,10..1,11
             .name 'a'
           1] MatchAs - 1,16..1,19
             .name 'new'
          .rest 'rest'
        .body[1]
         0] Pass - 1,30..1,34
'''),

('body[0].cases[0].pattern', -1, None, 'patterns', {}, ('exec', r'''
match a:
 case {1: a, 2: (b), **rest}: pass
'''), ('pattern',
r'''{1: c, **d}'''), r'''
match a:
 case {1: a, 2: {1: c, **d}, **rest}: pass
''', r'''
Module - ROOT 0,0..1,42
  .body[1]
   0] Match - 0,0..1,42
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,42
        .pattern MatchMapping - 1,6..1,36
          .keys[2]
           0] Constant 1 - 1,7..1,8
           1] Constant 2 - 1,13..1,14
          .patterns[2]
           0] MatchAs - 1,10..1,11
             .name 'a'
           1] MatchMapping - 1,16..1,27
             .keys[1]
              0] Constant 1 - 1,17..1,18
             .patterns[1]
              0] MatchAs - 1,20..1,21
                .name 'c'
             .rest 'd'
          .rest 'rest'
        .body[1]
         0] Pass - 1,38..1,42
'''),

('body[0].cases[0].pattern', -2, None, 'patterns', {}, ('exec', r'''
match a:
 case {1: a, 2: (b), **rest}: pass
'''), ('pattern',
r'''f(c=d)'''), r'''
match a:
 case {1: f(c=d), 2: (b), **rest}: pass
''', r'''
Module - ROOT 0,0..1,39
  .body[1]
   0] Match - 0,0..1,39
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,39
        .pattern MatchMapping - 1,6..1,33
          .keys[2]
           0] Constant 1 - 1,7..1,8
           1] Constant 2 - 1,18..1,19
          .patterns[2]
           0] MatchClass - 1,10..1,16
             .cls Name 'f' Load - 1,10..1,11
             .kwd_attrs[1]
              0] 'c'
             .kwd_patterns[1]
              0] MatchAs - 1,14..1,15
                .name 'd'
           1] MatchAs - 1,22..1,23
             .name 'b'
          .rest 'rest'
        .body[1]
         0] Pass - 1,35..1,39
'''),

('body[0].cases[0].pattern', -4, None, 'patterns', {}, ('exec', r'''
match a:
 case {1: a, 2: (b), **rest}: pass
'''), ('pattern',
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].cases[0].pattern', 0, None, 'patterns', {}, ('exec', r'''
match a:
 case c(a, (b)): pass
'''), ('pattern',
r'''**DEL**'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**'''),

('body[0].cases[0].pattern', 0, None, 'patterns', {}, ('exec', r'''
match a:
 case c(a, (b)): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case c(new, (b)): pass
''', r'''
Module - ROOT 0,0..1,23
  .body[1]
   0] Match - 0,0..1,23
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,23
        .pattern MatchClass - 1,6..1,17
          .cls Name 'c' Load - 1,6..1,7
          .patterns[2]
           0] MatchAs - 1,8..1,11
             .name 'new'
           1] MatchAs - 1,14..1,15
             .name 'b'
        .body[1]
         0] Pass - 1,19..1,23
'''),

('body[0].cases[0].pattern', 1, None, 'patterns', {}, ('exec', r'''
match a:
 case c(a, (b)): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case c(a, new): pass
''', r'''
Module - ROOT 0,0..1,21
  .body[1]
   0] Match - 0,0..1,21
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,21
        .pattern MatchClass - 1,6..1,15
          .cls Name 'c' Load - 1,6..1,7
          .patterns[2]
           0] MatchAs - 1,8..1,9
             .name 'a'
           1] MatchAs - 1,11..1,14
             .name 'new'
        .body[1]
         0] Pass - 1,17..1,21
'''),

('body[0].cases[0].pattern', -1, None, 'patterns', {}, ('exec', r'''
match a:
 case c(a, (b)): pass
'''), ('pattern',
r'''{1: c, **d}'''), r'''
match a:
 case c(a, {1: c, **d}): pass
''', r'''
Module - ROOT 0,0..1,29
  .body[1]
   0] Match - 0,0..1,29
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,29
        .pattern MatchClass - 1,6..1,23
          .cls Name 'c' Load - 1,6..1,7
          .patterns[2]
           0] MatchAs - 1,8..1,9
             .name 'a'
           1] MatchMapping - 1,11..1,22
             .keys[1]
              0] Constant 1 - 1,12..1,13
             .patterns[1]
              0] MatchAs - 1,15..1,16
                .name 'c'
             .rest 'd'
        .body[1]
         0] Pass - 1,25..1,29
'''),

('body[0].cases[0].pattern', -2, None, 'patterns', {}, ('exec', r'''
match a:
 case c(a, (b)): pass
'''), ('pattern',
r'''f(c=d)'''), r'''
match a:
 case c(f(c=d), (b)): pass
''', r'''
Module - ROOT 0,0..1,26
  .body[1]
   0] Match - 0,0..1,26
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,26
        .pattern MatchClass - 1,6..1,20
          .cls Name 'c' Load - 1,6..1,7
          .patterns[2]
           0] MatchClass - 1,8..1,14
             .cls Name 'f' Load - 1,8..1,9
             .kwd_attrs[1]
              0] 'c'
             .kwd_patterns[1]
              0] MatchAs - 1,12..1,13
                .name 'd'
           1] MatchAs - 1,17..1,18
             .name 'b'
        .body[1]
         0] Pass - 1,22..1,26
'''),

('body[0].cases[0].pattern', -4, None, 'patterns', {}, ('exec', r'''
match a:
 case c(a, (b)): pass
'''), ('pattern',
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].cases[0].pattern', 0, None, 'kwd_patterns', {}, ('exec', r'''
match a:
 case c(a={1: c}, b=(d())): pass
'''), ('pattern',
r'''**DEL**'''),
r'''**ValueError('cannot delete from MatchClass.kwd_patterns')**'''),

('body[0].cases[0].pattern', 0, None, 'kwd_patterns', {}, ('exec', r'''
match a:
 case c(a={1: c}, b=(d())): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case c(a=new, b=(d())): pass
''', r'''
Module - ROOT 0,0..1,29
  .body[1]
   0] Match - 0,0..1,29
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,29
        .pattern MatchClass - 1,6..1,23
          .cls Name 'c' Load - 1,6..1,7
          .kwd_attrs[2]
           0] 'a'
           1] 'b'
          .kwd_patterns[2]
           0] MatchAs - 1,10..1,13
             .name 'new'
           1] MatchClass - 1,18..1,21
             .cls Name 'd' Load - 1,18..1,19
        .body[1]
         0] Pass - 1,25..1,29
'''),

('body[0].cases[0].pattern', 1, None, 'kwd_patterns', {}, ('exec', r'''
match a:
 case c(a={1: c}, b=(d())): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case c(a={1: c}, b=new): pass
''', r'''
Module - ROOT 0,0..1,30
  .body[1]
   0] Match - 0,0..1,30
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,30
        .pattern MatchClass - 1,6..1,24
          .cls Name 'c' Load - 1,6..1,7
          .kwd_attrs[2]
           0] 'a'
           1] 'b'
          .kwd_patterns[2]
           0] MatchMapping - 1,10..1,16
             .keys[1]
              0] Constant 1 - 1,11..1,12
             .patterns[1]
              0] MatchAs - 1,14..1,15
                .name 'c'
           1] MatchAs - 1,20..1,23
             .name 'new'
        .body[1]
         0] Pass - 1,26..1,30
'''),

('body[0].cases[0].pattern', -1, None, 'kwd_patterns', {}, ('exec', r'''
match a:
 case c(a={1: c}, b=(d())): pass
'''), ('pattern',
r'''{1: c, **d}'''), r'''
match a:
 case c(a={1: c}, b={1: c, **d}): pass
''', r'''
Module - ROOT 0,0..1,38
  .body[1]
   0] Match - 0,0..1,38
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,38
        .pattern MatchClass - 1,6..1,32
          .cls Name 'c' Load - 1,6..1,7
          .kwd_attrs[2]
           0] 'a'
           1] 'b'
          .kwd_patterns[2]
           0] MatchMapping - 1,10..1,16
             .keys[1]
              0] Constant 1 - 1,11..1,12
             .patterns[1]
              0] MatchAs - 1,14..1,15
                .name 'c'
           1] MatchMapping - 1,20..1,31
             .keys[1]
              0] Constant 1 - 1,21..1,22
             .patterns[1]
              0] MatchAs - 1,24..1,25
                .name 'c'
             .rest 'd'
        .body[1]
         0] Pass - 1,34..1,38
'''),

('body[0].cases[0].pattern', -2, None, 'kwd_patterns', {}, ('exec', r'''
match a:
 case c(a={1: c}, b=(d())): pass
'''), ('pattern',
r'''f(c=d)'''), r'''
match a:
 case c(a=f(c=d), b=(d())): pass
''', r'''
Module - ROOT 0,0..1,32
  .body[1]
   0] Match - 0,0..1,32
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,32
        .pattern MatchClass - 1,6..1,26
          .cls Name 'c' Load - 1,6..1,7
          .kwd_attrs[2]
           0] 'a'
           1] 'b'
          .kwd_patterns[2]
           0] MatchClass - 1,10..1,16
             .cls Name 'f' Load - 1,10..1,11
             .kwd_attrs[1]
              0] 'c'
             .kwd_patterns[1]
              0] MatchAs - 1,14..1,15
                .name 'd'
           1] MatchClass - 1,21..1,24
             .cls Name 'd' Load - 1,21..1,22
        .body[1]
         0] Pass - 1,28..1,32
'''),

('body[0].cases[0].pattern', -4, None, 'kwd_patterns', {}, ('exec', r'''
match a:
 case c(a={1: c}, b=(d())): pass
'''), ('pattern',
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].cases[0].pattern', 0, None, None, {'norm': True}, ('exec', r'''
match a:
 case {1: c} | (d()): pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case (d()): pass
''', r'''
Module - ROOT 0,0..1,17
  .body[1]
   0] Match - 0,0..1,17
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,17
        .pattern MatchClass - 1,7..1,10
          .cls Name 'd' Load - 1,7..1,8
        .body[1]
         0] Pass - 1,13..1,17
'''),

('body[0].cases[0].pattern', 0, None, None, {}, ('exec', r'''
match a:
 case {1: c} | (d()): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case new | (d()): pass
''', r'''
Module - ROOT 0,0..1,23
  .body[1]
   0] Match - 0,0..1,23
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,23
        .pattern MatchOr - 1,6..1,17
          .patterns[2]
           0] MatchAs - 1,6..1,9
             .name 'new'
           1] MatchClass - 1,13..1,16
             .cls Name 'd' Load - 1,13..1,14
        .body[1]
         0] Pass - 1,19..1,23
'''),

('body[0].cases[0].pattern', 1, None, None, {}, ('exec', r'''
match a:
 case {1: c} | (d()): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case {1: c} | new: pass
''', r'''
Module - ROOT 0,0..1,24
  .body[1]
   0] Match - 0,0..1,24
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,24
        .pattern MatchOr - 1,6..1,18
          .patterns[2]
           0] MatchMapping - 1,6..1,12
             .keys[1]
              0] Constant 1 - 1,7..1,8
             .patterns[1]
              0] MatchAs - 1,10..1,11
                .name 'c'
           1] MatchAs - 1,15..1,18
             .name 'new'
        .body[1]
         0] Pass - 1,20..1,24
'''),

('body[0].cases[0].pattern', -1, None, None, {}, ('exec', r'''
match a:
 case {1: c} | (d()): pass
'''), ('pattern',
r'''{1: c, **d}'''), r'''
match a:
 case {1: c} | {1: c, **d}: pass
''', r'''
Module - ROOT 0,0..1,32
  .body[1]
   0] Match - 0,0..1,32
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,32
        .pattern MatchOr - 1,6..1,26
          .patterns[2]
           0] MatchMapping - 1,6..1,12
             .keys[1]
              0] Constant 1 - 1,7..1,8
             .patterns[1]
              0] MatchAs - 1,10..1,11
                .name 'c'
           1] MatchMapping - 1,15..1,26
             .keys[1]
              0] Constant 1 - 1,16..1,17
             .patterns[1]
              0] MatchAs - 1,19..1,20
                .name 'c'
             .rest 'd'
        .body[1]
         0] Pass - 1,28..1,32
'''),

('body[0].cases[0].pattern', -2, None, None, {}, ('exec', r'''
match a:
 case {1: c} | (d()): pass
'''), ('pattern',
r'''f(c=d)'''), r'''
match a:
 case f(c=d) | (d()): pass
''', r'''
Module - ROOT 0,0..1,26
  .body[1]
   0] Match - 0,0..1,26
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,26
        .pattern MatchOr - 1,6..1,20
          .patterns[2]
           0] MatchClass - 1,6..1,12
             .cls Name 'f' Load - 1,6..1,7
             .kwd_attrs[1]
              0] 'c'
             .kwd_patterns[1]
              0] MatchAs - 1,10..1,11
                .name 'd'
           1] MatchClass - 1,16..1,19
             .cls Name 'd' Load - 1,16..1,17
        .body[1]
         0] Pass - 1,22..1,26
'''),

('body[0].cases[0].pattern', -4, None, None, {}, ('exec', r'''
match a:
 case {1: c} | (d()): pass
'''), ('pattern',
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].cases[0]', None, None, 'pattern', {}, ('exec', r'''
match a:
 case {1: c} | (d()): pass
'''), ('pattern',
r'''**DEL**'''),
r'''**ValueError('cannot delete match_case.pattern')**'''),

('body[0].cases[0]', None, None, 'pattern', {}, ('exec', r'''
match a:
 case c(a={1: c}, b=(d())): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case new: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchAs - 1,6..1,9
          .name 'new'
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0]', None, None, 'pattern', {}, ('exec', r'''
match a:
 case c(a, (b)): pass
'''), ('pattern',
r'''new'''), r'''
match a:
 case new: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchAs - 1,6..1,9
          .name 'new'
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0]', None, None, 'pattern', {}, ('exec', r'''
match a:
 case {1: a, 2: (b), **rest}: pass
'''), ('pattern',
r'''{1: c, **d}'''), r'''
match a:
 case {1: c, **d}: pass
''', r'''
Module - ROOT 0,0..1,23
  .body[1]
   0] Match - 0,0..1,23
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,23
        .pattern MatchMapping - 1,6..1,17
          .keys[1]
           0] Constant 1 - 1,7..1,8
          .patterns[1]
           0] MatchAs - 1,10..1,11
             .name 'c'
          .rest 'd'
        .body[1]
         0] Pass - 1,19..1,23
'''),

('body[0].cases[0]', None, None, 'pattern', {}, ('exec', r'''
match a:
 case 1 as b, (2): pass
'''), ('pattern',
r'''f(c=d)'''), r'''
match a:
 case f(c=d): pass
''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] Match - 0,0..1,18
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,18
        .pattern MatchClass - 1,6..1,12
          .cls Name 'f' Load - 1,6..1,7
          .kwd_attrs[1]
           0] 'c'
          .kwd_patterns[1]
           0] MatchAs - 1,10..1,11
             .name 'd'
        .body[1]
         0] Pass - 1,14..1,18
'''),

('body[0].cases[0]', 0, None, 'pattern', {}, ('exec', r'''
match a:
 case {1: c} | (d()): pass
'''), ('pattern',
r'''new'''),
r'''**IndexError('match_case.pattern does not take an index')**'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case 1 as b: pass
'''), ('pattern',
r'''c.d'''), r'''
match a:
 case c.d as b: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchAs - 1,6..1,14
          .pattern MatchValue - 1,6..1,9
            .value Attribute - 1,6..1,9
              .value Name 'c' Load - 1,6..1,7
              .attr 'd'
              .ctx Load
          .name 'b'
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case (1) as b: pass
'''), ('pattern',
r'''c.d'''), r'''
match a:
 case c.d as b: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,20
        .pattern MatchAs - 1,6..1,14
          .pattern MatchValue - 1,6..1,9
            .value Attribute - 1,6..1,9
              .value Name 'c' Load - 1,6..1,7
              .attr 'd'
              .ctx Load
          .name 'b'
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case ((1) as b): pass
'''), ('pattern',
r'''c.d'''), r'''
match a:
 case (c.d as b): pass
''', r'''
Module - ROOT 0,0..1,22
  .body[1]
   0] Match - 0,0..1,22
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,22
        .pattern MatchAs - 1,7..1,15
          .pattern MatchValue - 1,7..1,10
            .value Attribute - 1,7..1,10
              .value Name 'c' Load - 1,7..1,8
              .attr 'd'
              .ctx Load
          .name 'b'
        .body[1]
         0] Pass - 1,18..1,22
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case 1 as b: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case b: pass
''', r'''
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
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case (1) as b: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case b: pass
''', r'''
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
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case ((1) as b): pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case (b): pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] Match - 0,0..1,15
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,15
        .pattern MatchAs - 1,7..1,8
          .name 'b'
        .body[1]
         0] Pass - 1,11..1,15
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case b: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case b: pass
''', r'''
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
'''),

('body[0].cases[0].pattern', None, None, None, {}, ('exec', r'''
match a:
 case _: pass
'''), ('pattern',
r'''c.d'''),
r'''**ValueError('cannot create MatchAs.pattern in this state')**'''),

('body[0].value', 0, None, 'generators', {'raw': False}, ('exec',
r'''[i for j in k async for (i) in j]'''), (None,
r'''**DEL**'''),
r'''[i async for (i) in j]''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value ListComp - 0,0..0,22
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,21
          .target Name 'i' Store - 0,14..0,15
          .iter Name 'j' Load - 0,20..0,21
          .is_async 1
'''),

('body[0].value', 0, None, 'generators', {}, ('exec',
r'''[i for j in k async for (i) in j]'''), (None,
r'''async for a in b'''),
r'''[i async for a in b async for (i) in j]''', r'''
Module - ROOT 0,0..0,39
  .body[1]
   0] Expr - 0,0..0,39
     .value ListComp - 0,0..0,39
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,19
          .target Name 'a' Store - 0,13..0,14
          .iter Name 'b' Load - 0,18..0,19
          .is_async 1
        1] comprehension - 0,20..0,38
          .target Name 'i' Store - 0,31..0,32
          .iter Name 'j' Load - 0,37..0,38
          .is_async 1
'''),

('body[0].value', 1, None, 'generators', {}, ('exec',
r'''[i for j in k async for (i) in j]'''), (None,
r'''async for a in b'''),
r'''[i for j in k async for a in b]''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] Expr - 0,0..0,31
     .value ListComp - 0,0..0,31
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,13
          .target Name 'j' Store - 0,7..0,8
          .iter Name 'k' Load - 0,12..0,13
          .is_async 0
        1] comprehension - 0,14..0,30
          .target Name 'a' Store - 0,24..0,25
          .iter Name 'b' Load - 0,29..0,30
          .is_async 1
'''),

('body[0].value', -1, None, 'generators', {}, ('exec',
r'''[i for j in k async for (i) in j]'''), (None,
r'''async for a in b'''),
r'''[i for j in k async for a in b]''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] Expr - 0,0..0,31
     .value ListComp - 0,0..0,31
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,13
          .target Name 'j' Store - 0,7..0,8
          .iter Name 'k' Load - 0,12..0,13
          .is_async 0
        1] comprehension - 0,14..0,30
          .target Name 'a' Store - 0,24..0,25
          .iter Name 'b' Load - 0,29..0,30
          .is_async 1
'''),

('body[0].value', -2, None, 'generators', {}, ('exec',
r'''[i for j in k async for (i) in j]'''), (None,
r'''async for a in b'''),
r'''[i async for a in b async for (i) in j]''', r'''
Module - ROOT 0,0..0,39
  .body[1]
   0] Expr - 0,0..0,39
     .value ListComp - 0,0..0,39
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,19
          .target Name 'a' Store - 0,13..0,14
          .iter Name 'b' Load - 0,18..0,19
          .is_async 1
        1] comprehension - 0,20..0,38
          .target Name 'i' Store - 0,31..0,32
          .iter Name 'j' Load - 0,37..0,38
          .is_async 1
'''),

('body[0].value', -4, None, 'generators', {}, ('exec',
r'''[i for j in k async for (i) in j]'''), (None,
r'''async for a in b'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', 0, None, 'generators', {'raw': False}, ('exec',
r'''{i for j in k async for (i) in j}'''), (None,
r'''**DEL**'''),
r'''{i async for (i) in j}''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value SetComp - 0,0..0,22
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,21
          .target Name 'i' Store - 0,14..0,15
          .iter Name 'j' Load - 0,20..0,21
          .is_async 1
'''),

('body[0].value', 0, None, 'generators', {}, ('exec',
r'''{i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''{i async for a in b async for (i) in j}''', r'''
Module - ROOT 0,0..0,39
  .body[1]
   0] Expr - 0,0..0,39
     .value SetComp - 0,0..0,39
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,19
          .target Name 'a' Store - 0,13..0,14
          .iter Name 'b' Load - 0,18..0,19
          .is_async 1
        1] comprehension - 0,20..0,38
          .target Name 'i' Store - 0,31..0,32
          .iter Name 'j' Load - 0,37..0,38
          .is_async 1
'''),

('body[0].value', 1, None, 'generators', {}, ('exec',
r'''{i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''{i for j in k async for a in b}''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] Expr - 0,0..0,31
     .value SetComp - 0,0..0,31
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,13
          .target Name 'j' Store - 0,7..0,8
          .iter Name 'k' Load - 0,12..0,13
          .is_async 0
        1] comprehension - 0,14..0,30
          .target Name 'a' Store - 0,24..0,25
          .iter Name 'b' Load - 0,29..0,30
          .is_async 1
'''),

('body[0].value', -1, None, 'generators', {}, ('exec',
r'''{i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''{i for j in k async for a in b}''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] Expr - 0,0..0,31
     .value SetComp - 0,0..0,31
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,13
          .target Name 'j' Store - 0,7..0,8
          .iter Name 'k' Load - 0,12..0,13
          .is_async 0
        1] comprehension - 0,14..0,30
          .target Name 'a' Store - 0,24..0,25
          .iter Name 'b' Load - 0,29..0,30
          .is_async 1
'''),

('body[0].value', -2, None, 'generators', {}, ('exec',
r'''{i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''{i async for a in b async for (i) in j}''', r'''
Module - ROOT 0,0..0,39
  .body[1]
   0] Expr - 0,0..0,39
     .value SetComp - 0,0..0,39
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,19
          .target Name 'a' Store - 0,13..0,14
          .iter Name 'b' Load - 0,18..0,19
          .is_async 1
        1] comprehension - 0,20..0,38
          .target Name 'i' Store - 0,31..0,32
          .iter Name 'j' Load - 0,37..0,38
          .is_async 1
'''),

('body[0].value', -4, None, 'generators', {}, ('exec',
r'''{i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', 0, None, 'generators', {'raw': False}, ('exec',
r'''{i: i for j in k async for (i) in j}'''), (None,
r'''**DEL**'''),
r'''{i: i async for (i) in j}''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Expr - 0,0..0,25
     .value DictComp - 0,0..0,25
       .key Name 'i' Load - 0,1..0,2
       .value Name 'i' Load - 0,4..0,5
       .generators[1]
        0] comprehension - 0,6..0,24
          .target Name 'i' Store - 0,17..0,18
          .iter Name 'j' Load - 0,23..0,24
          .is_async 1
'''),

('body[0].value', 0, None, 'generators', {}, ('exec',
r'''{i: i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''{i: i async for a in b async for (i) in j}''', r'''
Module - ROOT 0,0..0,42
  .body[1]
   0] Expr - 0,0..0,42
     .value DictComp - 0,0..0,42
       .key Name 'i' Load - 0,1..0,2
       .value Name 'i' Load - 0,4..0,5
       .generators[2]
        0] comprehension - 0,6..0,22
          .target Name 'a' Store - 0,16..0,17
          .iter Name 'b' Load - 0,21..0,22
          .is_async 1
        1] comprehension - 0,23..0,41
          .target Name 'i' Store - 0,34..0,35
          .iter Name 'j' Load - 0,40..0,41
          .is_async 1
'''),

('body[0].value', 1, None, 'generators', {}, ('exec',
r'''{i: i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''{i: i for j in k async for a in b}''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] Expr - 0,0..0,34
     .value DictComp - 0,0..0,34
       .key Name 'i' Load - 0,1..0,2
       .value Name 'i' Load - 0,4..0,5
       .generators[2]
        0] comprehension - 0,6..0,16
          .target Name 'j' Store - 0,10..0,11
          .iter Name 'k' Load - 0,15..0,16
          .is_async 0
        1] comprehension - 0,17..0,33
          .target Name 'a' Store - 0,27..0,28
          .iter Name 'b' Load - 0,32..0,33
          .is_async 1
'''),

('body[0].value', -1, None, 'generators', {}, ('exec',
r'''{i: i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''{i: i for j in k async for a in b}''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] Expr - 0,0..0,34
     .value DictComp - 0,0..0,34
       .key Name 'i' Load - 0,1..0,2
       .value Name 'i' Load - 0,4..0,5
       .generators[2]
        0] comprehension - 0,6..0,16
          .target Name 'j' Store - 0,10..0,11
          .iter Name 'k' Load - 0,15..0,16
          .is_async 0
        1] comprehension - 0,17..0,33
          .target Name 'a' Store - 0,27..0,28
          .iter Name 'b' Load - 0,32..0,33
          .is_async 1
'''),

('body[0].value', -2, None, 'generators', {}, ('exec',
r'''{i: i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''{i: i async for a in b async for (i) in j}''', r'''
Module - ROOT 0,0..0,42
  .body[1]
   0] Expr - 0,0..0,42
     .value DictComp - 0,0..0,42
       .key Name 'i' Load - 0,1..0,2
       .value Name 'i' Load - 0,4..0,5
       .generators[2]
        0] comprehension - 0,6..0,22
          .target Name 'a' Store - 0,16..0,17
          .iter Name 'b' Load - 0,21..0,22
          .is_async 1
        1] comprehension - 0,23..0,41
          .target Name 'i' Store - 0,34..0,35
          .iter Name 'j' Load - 0,40..0,41
          .is_async 1
'''),

('body[0].value', -4, None, 'generators', {}, ('exec',
r'''{i: i for j in k async for (i) in j}'''), (None,
r'''async for a in b'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', 0, None, 'generators', {'raw': False}, ('exec',
r'''(i for j in k async for (i) in j)'''), (None,
r'''**DEL**'''),
r'''(i async for (i) in j)''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value GeneratorExp - 0,0..0,22
       .elt Name 'i' Load - 0,1..0,2
       .generators[1]
        0] comprehension - 0,3..0,21
          .target Name 'i' Store - 0,14..0,15
          .iter Name 'j' Load - 0,20..0,21
          .is_async 1
'''),

('body[0].value', 0, None, 'generators', {}, ('exec',
r'''(i for j in k async for (i) in j)'''), (None,
r'''async for a in b'''),
r'''(i async for a in b async for (i) in j)''', r'''
Module - ROOT 0,0..0,39
  .body[1]
   0] Expr - 0,0..0,39
     .value GeneratorExp - 0,0..0,39
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,19
          .target Name 'a' Store - 0,13..0,14
          .iter Name 'b' Load - 0,18..0,19
          .is_async 1
        1] comprehension - 0,20..0,38
          .target Name 'i' Store - 0,31..0,32
          .iter Name 'j' Load - 0,37..0,38
          .is_async 1
'''),

('body[0].value', 1, None, 'generators', {}, ('exec',
r'''(i for j in k async for (i) in j)'''), (None,
r'''async for a in b'''),
r'''(i for j in k async for a in b)''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] Expr - 0,0..0,31
     .value GeneratorExp - 0,0..0,31
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,13
          .target Name 'j' Store - 0,7..0,8
          .iter Name 'k' Load - 0,12..0,13
          .is_async 0
        1] comprehension - 0,14..0,30
          .target Name 'a' Store - 0,24..0,25
          .iter Name 'b' Load - 0,29..0,30
          .is_async 1
'''),

('body[0].value', -1, None, 'generators', {}, ('exec',
r'''(i for j in k async for (i) in j)'''), (None,
r'''async for a in b'''),
r'''(i for j in k async for a in b)''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] Expr - 0,0..0,31
     .value GeneratorExp - 0,0..0,31
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,13
          .target Name 'j' Store - 0,7..0,8
          .iter Name 'k' Load - 0,12..0,13
          .is_async 0
        1] comprehension - 0,14..0,30
          .target Name 'a' Store - 0,24..0,25
          .iter Name 'b' Load - 0,29..0,30
          .is_async 1
'''),

('body[0].value', -2, None, 'generators', {}, ('exec',
r'''(i for j in k async for (i) in j)'''), (None,
r'''async for a in b'''),
r'''(i async for a in b async for (i) in j)''', r'''
Module - ROOT 0,0..0,39
  .body[1]
   0] Expr - 0,0..0,39
     .value GeneratorExp - 0,0..0,39
       .elt Name 'i' Load - 0,1..0,2
       .generators[2]
        0] comprehension - 0,3..0,19
          .target Name 'a' Store - 0,13..0,14
          .iter Name 'b' Load - 0,18..0,19
          .is_async 1
        1] comprehension - 0,20..0,38
          .target Name 'i' Store - 0,31..0,32
          .iter Name 'j' Load - 0,37..0,38
          .is_async 1
'''),

('body[0].value', -4, None, 'generators', {}, ('exec',
r'''(i for j in k async for (i) in j)'''), (None,
r'''async for a in b'''),
r'''**IndexError('index out of range')**'''),

('body[0].args', 0, None, 'posonlyargs', {}, ('exec',
r'''def f(a: int = 1, b: (str)='', /): pass'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete from arguments.posonlyargs')**'''),

('body[0].args', 0, None, 'posonlyargs', {}, ('exec',
r'''def f(a: int = 1, b: (str)='', /): pass'''), ('arg',
r'''new'''),
r'''def f(new = 1, b: (str)='', /): pass''', r'''
Module - ROOT 0,0..0,36
  .body[1]
   0] FunctionDef - 0,0..0,36
     .name 'f'
     .args arguments - 0,6..0,29
       .posonlyargs[2]
        0] arg - 0,6..0,9
          .arg 'new'
        1] arg - 0,15..0,23
          .arg 'b'
          .annotation Name 'str' Load - 0,19..0,22
       .defaults[2]
        0] Constant 1 - 0,12..0,13
        1] Constant '' - 0,24..0,26
     .body[1]
      0] Pass - 0,32..0,36
'''),

('body[0].args', 1, None, 'posonlyargs', {}, ('exec',
r'''def f(a: int = 1, b: (str)='', /): pass'''), ('arg',
r'''new'''),
r'''def f(a: int = 1, new='', /): pass''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] FunctionDef - 0,0..0,34
     .name 'f'
     .args arguments - 0,6..0,27
       .posonlyargs[2]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'int' Load - 0,9..0,12
        1] arg - 0,18..0,21
          .arg 'new'
       .defaults[2]
        0] Constant 1 - 0,15..0,16
        1] Constant '' - 0,22..0,24
     .body[1]
      0] Pass - 0,30..0,34
'''),

('body[0].args', -1, None, 'posonlyargs', {}, ('exec',
r'''def f(a: int = 1, b: (str)='', /): pass'''), ('arg',
r'''new'''),
r'''def f(a: int = 1, new='', /): pass''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] FunctionDef - 0,0..0,34
     .name 'f'
     .args arguments - 0,6..0,27
       .posonlyargs[2]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'int' Load - 0,9..0,12
        1] arg - 0,18..0,21
          .arg 'new'
       .defaults[2]
        0] Constant 1 - 0,15..0,16
        1] Constant '' - 0,22..0,24
     .body[1]
      0] Pass - 0,30..0,34
'''),

('body[0].args', -2, None, 'posonlyargs', {}, ('exec',
r'''def f(a: int = 1, b: (str)='', /): pass'''), ('arg',
r'''new'''),
r'''def f(new = 1, b: (str)='', /): pass''', r'''
Module - ROOT 0,0..0,36
  .body[1]
   0] FunctionDef - 0,0..0,36
     .name 'f'
     .args arguments - 0,6..0,29
       .posonlyargs[2]
        0] arg - 0,6..0,9
          .arg 'new'
        1] arg - 0,15..0,23
          .arg 'b'
          .annotation Name 'str' Load - 0,19..0,22
       .defaults[2]
        0] Constant 1 - 0,12..0,13
        1] Constant '' - 0,24..0,26
     .body[1]
      0] Pass - 0,32..0,36
'''),

('body[0].args', -4, None, 'posonlyargs', {}, ('exec',
r'''def f(a: int = 1, b: (str)='', /): pass'''), ('arg',
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].args', 0, None, 'args', {}, ('exec',
r'''def f(a: int = 1, b: (str)=''): pass'''), ('arg',
r'''**DEL**'''),
r'''**ValueError('cannot delete from arguments.args')**'''),

('body[0].args', 0, None, 'args', {}, ('exec',
r'''def f(a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''def f(new = 1, b: (str)=''): pass''', r'''
Module - ROOT 0,0..0,33
  .body[1]
   0] FunctionDef - 0,0..0,33
     .name 'f'
     .args arguments - 0,6..0,26
       .args[2]
        0] arg - 0,6..0,9
          .arg 'new'
        1] arg - 0,15..0,23
          .arg 'b'
          .annotation Name 'str' Load - 0,19..0,22
       .defaults[2]
        0] Constant 1 - 0,12..0,13
        1] Constant '' - 0,24..0,26
     .body[1]
      0] Pass - 0,29..0,33
'''),

('body[0].args', 1, None, 'args', {}, ('exec',
r'''def f(a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''def f(a: int = 1, new=''): pass''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] FunctionDef - 0,0..0,31
     .name 'f'
     .args arguments - 0,6..0,24
       .args[2]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'int' Load - 0,9..0,12
        1] arg - 0,18..0,21
          .arg 'new'
       .defaults[2]
        0] Constant 1 - 0,15..0,16
        1] Constant '' - 0,22..0,24
     .body[1]
      0] Pass - 0,27..0,31
'''),

('body[0].args', -1, None, 'args', {}, ('exec',
r'''def f(a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''def f(a: int = 1, new=''): pass''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] FunctionDef - 0,0..0,31
     .name 'f'
     .args arguments - 0,6..0,24
       .args[2]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'int' Load - 0,9..0,12
        1] arg - 0,18..0,21
          .arg 'new'
       .defaults[2]
        0] Constant 1 - 0,15..0,16
        1] Constant '' - 0,22..0,24
     .body[1]
      0] Pass - 0,27..0,31
'''),

('body[0].args', -2, None, 'args', {}, ('exec',
r'''def f(a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''def f(new = 1, b: (str)=''): pass''', r'''
Module - ROOT 0,0..0,33
  .body[1]
   0] FunctionDef - 0,0..0,33
     .name 'f'
     .args arguments - 0,6..0,26
       .args[2]
        0] arg - 0,6..0,9
          .arg 'new'
        1] arg - 0,15..0,23
          .arg 'b'
          .annotation Name 'str' Load - 0,19..0,22
       .defaults[2]
        0] Constant 1 - 0,12..0,13
        1] Constant '' - 0,24..0,26
     .body[1]
      0] Pass - 0,29..0,33
'''),

('body[0].args', -4, None, 'args', {}, ('exec',
r'''def f(a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0].args', 0, None, 'kwonlyargs', {}, ('exec',
r'''def f(*, a: int = 1, b: (str)=''): pass'''), ('arg',
r'''**DEL**'''),
r'''**ValueError('cannot delete from arguments.kwonlyargs')**'''),

('body[0].args', 0, None, 'kwonlyargs', {}, ('exec',
r'''def f(*, a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''def f(*, new = 1, b: (str)=''): pass''', r'''
Module - ROOT 0,0..0,36
  .body[1]
   0] FunctionDef - 0,0..0,36
     .name 'f'
     .args arguments - 0,6..0,29
       .kwonlyargs[2]
        0] arg - 0,9..0,12
          .arg 'new'
        1] arg - 0,18..0,26
          .arg 'b'
          .annotation Name 'str' Load - 0,22..0,25
       .kw_defaults[2]
        0] Constant 1 - 0,15..0,16
        1] Constant '' - 0,27..0,29
     .body[1]
      0] Pass - 0,32..0,36
'''),

('body[0].args', 1, None, 'kwonlyargs', {}, ('exec',
r'''def f(*, a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''def f(*, a: int = 1, new=''): pass''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] FunctionDef - 0,0..0,34
     .name 'f'
     .args arguments - 0,6..0,27
       .kwonlyargs[2]
        0] arg - 0,9..0,15
          .arg 'a'
          .annotation Name 'int' Load - 0,12..0,15
        1] arg - 0,21..0,24
          .arg 'new'
       .kw_defaults[2]
        0] Constant 1 - 0,18..0,19
        1] Constant '' - 0,25..0,27
     .body[1]
      0] Pass - 0,30..0,34
'''),

('body[0].args', -1, None, 'kwonlyargs', {}, ('exec',
r'''def f(*, a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''def f(*, a: int = 1, new=''): pass''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] FunctionDef - 0,0..0,34
     .name 'f'
     .args arguments - 0,6..0,27
       .kwonlyargs[2]
        0] arg - 0,9..0,15
          .arg 'a'
          .annotation Name 'int' Load - 0,12..0,15
        1] arg - 0,21..0,24
          .arg 'new'
       .kw_defaults[2]
        0] Constant 1 - 0,18..0,19
        1] Constant '' - 0,25..0,27
     .body[1]
      0] Pass - 0,30..0,34
'''),

('body[0].args', -2, None, 'kwonlyargs', {}, ('exec',
r'''def f(*, a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''def f(*, new = 1, b: (str)=''): pass''', r'''
Module - ROOT 0,0..0,36
  .body[1]
   0] FunctionDef - 0,0..0,36
     .name 'f'
     .args arguments - 0,6..0,29
       .kwonlyargs[2]
        0] arg - 0,9..0,12
          .arg 'new'
        1] arg - 0,18..0,26
          .arg 'b'
          .annotation Name 'str' Load - 0,22..0,25
       .kw_defaults[2]
        0] Constant 1 - 0,15..0,16
        1] Constant '' - 0,27..0,29
     .body[1]
      0] Pass - 0,32..0,36
'''),

('body[0].args', -4, None, 'kwonlyargs', {}, ('exec',
r'''def f(*, a: int = 1, b: (str)=''): pass'''), ('arg',
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'keywords', {}, ('exec',
r'''class c(a=1, b = (2)): pass'''), ('keyword',
r'''**DEL**'''),
r'''class c(b = (2)): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] ClassDef - 0,0..0,22
     .name 'c'
     .keywords[1]
      0] keyword - 0,8..0,15
        .arg 'b'
        .value Constant 2 - 0,13..0,14
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0]', 0, None, 'keywords', {}, ('exec',
r'''class c(a=1, b = (2)): pass'''), ('keyword',
r'''new=(3)'''),
r'''class c(new=(3), b = (2)): pass''',
r'''class c(new=3, b = (2)): pass''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] ClassDef - 0,0..0,31
     .name 'c'
     .keywords[2]
      0] keyword - 0,8..0,15
        .arg 'new'
        .value Constant 3 - 0,13..0,14
      1] keyword - 0,17..0,24
        .arg 'b'
        .value Constant 2 - 0,22..0,23
     .body[1]
      0] Pass - 0,27..0,31
'''),

('body[0]', 1, None, 'keywords', {}, ('exec',
r'''class c(a=1, b = (2)): pass'''), ('keyword',
r'''new=(3)'''),
r'''class c(a=1, new=(3)): pass''',
r'''class c(a=1, new=3): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] ClassDef - 0,0..0,27
     .name 'c'
     .keywords[2]
      0] keyword - 0,8..0,11
        .arg 'a'
        .value Constant 1 - 0,10..0,11
      1] keyword - 0,13..0,20
        .arg 'new'
        .value Constant 3 - 0,18..0,19
     .body[1]
      0] Pass - 0,23..0,27
'''),

('body[0]', -1, None, 'keywords', {}, ('exec',
r'''class c(a=1, b = (2)): pass'''), ('keyword',
r'''new=(3)'''),
r'''class c(a=1, new=(3)): pass''',
r'''class c(a=1, new=3): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] ClassDef - 0,0..0,27
     .name 'c'
     .keywords[2]
      0] keyword - 0,8..0,11
        .arg 'a'
        .value Constant 1 - 0,10..0,11
      1] keyword - 0,13..0,20
        .arg 'new'
        .value Constant 3 - 0,18..0,19
     .body[1]
      0] Pass - 0,23..0,27
'''),

('body[0]', -2, None, 'keywords', {}, ('exec',
r'''class c(a=1, b = (2)): pass'''), ('keyword',
r'''new=(3)'''),
r'''class c(new=(3), b = (2)): pass''',
r'''class c(new=3, b = (2)): pass''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] ClassDef - 0,0..0,31
     .name 'c'
     .keywords[2]
      0] keyword - 0,8..0,15
        .arg 'new'
        .value Constant 3 - 0,13..0,14
      1] keyword - 0,17..0,24
        .arg 'b'
        .value Constant 2 - 0,22..0,23
     .body[1]
      0] Pass - 0,27..0,31
'''),

('body[0]', -4, None, 'keywords', {}, ('exec',
r'''class c(a=1, b = (2)): pass'''), ('keyword',
r'''new=(3)'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', 0, None, 'keywords', {}, ('exec',
r'''call(a=1, b = (2))'''), ('keyword',
r'''**DEL**'''),
r'''call(b = (2))''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Expr - 0,0..0,13
     .value Call - 0,0..0,13
       .func Name 'call' Load - 0,0..0,4
       .keywords[1]
        0] keyword - 0,5..0,12
          .arg 'b'
          .value Constant 2 - 0,10..0,11
'''),

('body[0].value', 0, None, 'keywords', {}, ('exec',
r'''call(a=1, b = (2))'''), ('keyword',
r'''new=(3)'''),
r'''call(new=(3), b = (2))''',
r'''call(new=3, b = (2))''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value Call - 0,0..0,22
       .func Name 'call' Load - 0,0..0,4
       .keywords[2]
        0] keyword - 0,5..0,12
          .arg 'new'
          .value Constant 3 - 0,10..0,11
        1] keyword - 0,14..0,21
          .arg 'b'
          .value Constant 2 - 0,19..0,20
'''),

('body[0].value', 1, None, 'keywords', {}, ('exec',
r'''call(a=1, b = (2))'''), ('keyword',
r'''new=(3)'''),
r'''call(a=1, new=(3))''',
r'''call(a=1, new=3)''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Expr - 0,0..0,18
     .value Call - 0,0..0,18
       .func Name 'call' Load - 0,0..0,4
       .keywords[2]
        0] keyword - 0,5..0,8
          .arg 'a'
          .value Constant 1 - 0,7..0,8
        1] keyword - 0,10..0,17
          .arg 'new'
          .value Constant 3 - 0,15..0,16
'''),

('body[0].value', -1, None, 'keywords', {}, ('exec',
r'''call(a=1, b = (2))'''), ('keyword',
r'''new=(3)'''),
r'''call(a=1, new=(3))''',
r'''call(a=1, new=3)''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Expr - 0,0..0,18
     .value Call - 0,0..0,18
       .func Name 'call' Load - 0,0..0,4
       .keywords[2]
        0] keyword - 0,5..0,8
          .arg 'a'
          .value Constant 1 - 0,7..0,8
        1] keyword - 0,10..0,17
          .arg 'new'
          .value Constant 3 - 0,15..0,16
'''),

('body[0].value', -2, None, 'keywords', {}, ('exec',
r'''call(a=1, b = (2))'''), ('keyword',
r'''new=(3)'''),
r'''call(new=(3), b = (2))''',
r'''call(new=3, b = (2))''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value Call - 0,0..0,22
       .func Name 'call' Load - 0,0..0,4
       .keywords[2]
        0] keyword - 0,5..0,12
          .arg 'new'
          .value Constant 3 - 0,10..0,11
        1] keyword - 0,14..0,21
          .arg 'b'
          .value Constant 2 - 0,19..0,20
'''),

('body[0].value', -4, None, 'keywords', {}, ('exec',
r'''call(a=1, b = (2))'''), ('keyword',
r'''new=(3)'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', 1, None, 'keywords', {}, ('exec',
r'''call(a=1, *b, c=1)'''), ('keyword',
r'''**new'''),
r'''call(a=1, *b, **new)''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Expr - 0,0..0,20
     .value Call - 0,0..0,20
       .func Name 'call' Load - 0,0..0,4
       .args[1]
        0] Starred - 0,10..0,12
          .value Name 'b' Load - 0,11..0,12
          .ctx Load
       .keywords[2]
        0] keyword - 0,5..0,8
          .arg 'a'
          .value Constant 1 - 0,7..0,8
        1] keyword - 0,14..0,19
          .value Name 'new' Load - 0,16..0,19
'''),

('body[0].value', 0, None, 'keywords', {}, ('exec',
r'''call(a=1, *b, c=1)'''), ('keyword',
r'''**new'''),
r'''**ValueError("cannot put '**' Call.keywords element at this location (non-keywords follow)")**'''),

('body[0]', 0, None, 'items', {}, ('exec',
r'''with (a as b, (f()) as d): pass'''), (None,
r'''**DEL**'''),
r'''with ((f()) as d): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] With - 0,0..0,23
     .items[1]
      0] withitem - 0,6..0,16
        .context_expr Call - 0,7..0,10
          .func Name 'f' Load - 0,7..0,8
        .optional_vars Name 'd' Store - 0,15..0,16
     .body[1]
      0] Pass - 0,19..0,23
'''),

('body[0]', 0, None, 'items', {}, ('exec',
r'''with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''with (g() as new, (f()) as d): pass''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] With - 0,0..0,35
     .items[2]
      0] withitem - 0,6..0,16
        .context_expr Call - 0,6..0,9
          .func Name 'g' Load - 0,6..0,7
        .optional_vars Name 'new' Store - 0,13..0,16
      1] withitem - 0,18..0,28
        .context_expr Call - 0,19..0,22
          .func Name 'f' Load - 0,19..0,20
        .optional_vars Name 'd' Store - 0,27..0,28
     .body[1]
      0] Pass - 0,31..0,35
'''),

('body[0]', 1, None, 'items', {}, ('exec',
r'''with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''with (a as b, g() as new): pass''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] With - 0,0..0,31
     .items[2]
      0] withitem - 0,6..0,12
        .context_expr Name 'a' Load - 0,6..0,7
        .optional_vars Name 'b' Store - 0,11..0,12
      1] withitem - 0,14..0,24
        .context_expr Call - 0,14..0,17
          .func Name 'g' Load - 0,14..0,15
        .optional_vars Name 'new' Store - 0,21..0,24
     .body[1]
      0] Pass - 0,27..0,31
'''),

('body[0]', -1, None, 'items', {}, ('exec',
r'''with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''with (a as b, g() as new): pass''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] With - 0,0..0,31
     .items[2]
      0] withitem - 0,6..0,12
        .context_expr Name 'a' Load - 0,6..0,7
        .optional_vars Name 'b' Store - 0,11..0,12
      1] withitem - 0,14..0,24
        .context_expr Call - 0,14..0,17
          .func Name 'g' Load - 0,14..0,15
        .optional_vars Name 'new' Store - 0,21..0,24
     .body[1]
      0] Pass - 0,27..0,31
'''),

('body[0]', -2, None, 'items', {}, ('exec',
r'''with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''with (g() as new, (f()) as d): pass''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] With - 0,0..0,35
     .items[2]
      0] withitem - 0,6..0,16
        .context_expr Call - 0,6..0,9
          .func Name 'g' Load - 0,6..0,7
        .optional_vars Name 'new' Store - 0,13..0,16
      1] withitem - 0,18..0,28
        .context_expr Call - 0,19..0,22
          .func Name 'f' Load - 0,19..0,20
        .optional_vars Name 'd' Store - 0,27..0,28
     .body[1]
      0] Pass - 0,31..0,35
'''),

('body[0]', -4, None, 'items', {}, ('exec',
r'''with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'items', {}, ('exec',
r'''async with (a as b, (f()) as d): pass'''), ('withitem',
r'''**DEL**'''),
r'''async with ((f()) as d): pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncWith - 0,0..0,29
     .items[1]
      0] withitem - 0,12..0,22
        .context_expr Call - 0,13..0,16
          .func Name 'f' Load - 0,13..0,14
        .optional_vars Name 'd' Store - 0,21..0,22
     .body[1]
      0] Pass - 0,25..0,29
'''),

('body[0]', 0, None, 'items', {}, ('exec',
r'''async with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''async with (g() as new, (f()) as d): pass''', r'''
Module - ROOT 0,0..0,41
  .body[1]
   0] AsyncWith - 0,0..0,41
     .items[2]
      0] withitem - 0,12..0,22
        .context_expr Call - 0,12..0,15
          .func Name 'g' Load - 0,12..0,13
        .optional_vars Name 'new' Store - 0,19..0,22
      1] withitem - 0,24..0,34
        .context_expr Call - 0,25..0,28
          .func Name 'f' Load - 0,25..0,26
        .optional_vars Name 'd' Store - 0,33..0,34
     .body[1]
      0] Pass - 0,37..0,41
'''),

('body[0]', 1, None, 'items', {}, ('exec',
r'''async with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''async with (a as b, g() as new): pass''', r'''
Module - ROOT 0,0..0,37
  .body[1]
   0] AsyncWith - 0,0..0,37
     .items[2]
      0] withitem - 0,12..0,18
        .context_expr Name 'a' Load - 0,12..0,13
        .optional_vars Name 'b' Store - 0,17..0,18
      1] withitem - 0,20..0,30
        .context_expr Call - 0,20..0,23
          .func Name 'g' Load - 0,20..0,21
        .optional_vars Name 'new' Store - 0,27..0,30
     .body[1]
      0] Pass - 0,33..0,37
'''),

('body[0]', -1, None, 'items', {}, ('exec',
r'''async with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''async with (a as b, g() as new): pass''', r'''
Module - ROOT 0,0..0,37
  .body[1]
   0] AsyncWith - 0,0..0,37
     .items[2]
      0] withitem - 0,12..0,18
        .context_expr Name 'a' Load - 0,12..0,13
        .optional_vars Name 'b' Store - 0,17..0,18
      1] withitem - 0,20..0,30
        .context_expr Call - 0,20..0,23
          .func Name 'g' Load - 0,20..0,21
        .optional_vars Name 'new' Store - 0,27..0,30
     .body[1]
      0] Pass - 0,33..0,37
'''),

('body[0]', -2, None, 'items', {}, ('exec',
r'''async with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''async with (g() as new, (f()) as d): pass''', r'''
Module - ROOT 0,0..0,41
  .body[1]
   0] AsyncWith - 0,0..0,41
     .items[2]
      0] withitem - 0,12..0,22
        .context_expr Call - 0,12..0,15
          .func Name 'g' Load - 0,12..0,13
        .optional_vars Name 'new' Store - 0,19..0,22
      1] withitem - 0,24..0,34
        .context_expr Call - 0,25..0,28
          .func Name 'f' Load - 0,25..0,26
        .optional_vars Name 'd' Store - 0,33..0,34
     .body[1]
      0] Pass - 0,37..0,41
'''),

('body[0]', -4, None, 'items', {}, ('exec',
r'''async with (a as b, (f()) as d): pass'''), ('withitem',
r'''g() as new'''),
r'''**IndexError('index out of range')**'''),

('body[0].value', None, None, 'slice', {}, ('exec',
r'''a[b:c:d]'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete Subscript.slice')**'''),

('body[0].value', None, None, 'slice', {}, ('exec',
r'''a[b:c:d]'''), (None,
r'''e, f'''),
r'''a[e, f]''',
r'''a[(e, f)]''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Subscript - 0,0..0,7
       .value Name 'a' Load - 0,0..0,1
       .slice Tuple - 0,2..0,6
         .elts[2]
          0] Name 'e' Load - 0,2..0,3
          1] Name 'f' Load - 0,5..0,6
         .ctx Load
       .ctx Load
'''),

('body[0].value', None, None, 'slice', {}, ('exec',
r'''a[b,c,d]'''), (None,
r'''g'''),
r'''a[g]''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Subscript - 0,0..0,4
       .value Name 'a' Load - 0,0..0,1
       .slice Name 'g' Load - 0,2..0,3
       .ctx Load
'''),

('body[0].value', 0, None, 'slice', {}, ('exec',
r'''a[b:c:d]'''), (None,
r'''h'''),
r'''**IndexError('Subscript.slice does not take an index')**'''),

('body[0].value', None, None, 'slice', {}, ('exec',
r'''a[b]'''), (None,
r'''h:i:j'''),
r'''a[h:i:j]''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Subscript - 0,0..0,8
       .value Name 'a' Load - 0,0..0,1
       .slice Slice - 0,2..0,7
         .lower Name 'h' Load - 0,2..0,3
         .upper Name 'i' Load - 0,4..0,5
         .step Name 'j' Load - 0,6..0,7
       .ctx Load
'''),

('body[0]', None, None, 'args', {}, ('exec',
r'''def f(a=1): pass'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass''',
r'''def f(a: list[str], /, b: int=1, *c, d=100, **e): pass''', r'''
Module - ROOT 0,0..0,56
  .body[1]
   0] FunctionDef - 0,0..0,56
     .name 'f'
     .args arguments - 0,6..0,49
       .posonlyargs[1]
        0] arg - 0,6..0,18
          .arg 'a'
          .annotation Subscript - 0,9..0,18
            .value Name 'list' Load - 0,9..0,13
            .slice Name 'str' Load - 0,14..0,17
            .ctx Load
       .args[1]
        0] arg - 0,23..0,29
          .arg 'b'
          .annotation Name 'int' Load - 0,26..0,29
       .vararg arg - 0,36..0,37
         .arg 'c'
       .kwonlyargs[1]
        0] arg - 0,39..0,40
          .arg 'd'
       .kw_defaults[1]
        0] Constant 100 - 0,41..0,44
       .kwarg arg - 0,48..0,49
         .arg 'e'
       .defaults[1]
        0] Constant 1 - 0,32..0,33
     .body[1]
      0] Pass - 0,52..0,56
'''),

('body[0]', None, None, 'args', {}, ('exec',
r'''def f(): pass'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass''',
r'''def f(a: list[str], /, b: int=1, *c, d=100, **e): pass''', r'''
Module - ROOT 0,0..0,56
  .body[1]
   0] FunctionDef - 0,0..0,56
     .name 'f'
     .args arguments - 0,6..0,49
       .posonlyargs[1]
        0] arg - 0,6..0,18
          .arg 'a'
          .annotation Subscript - 0,9..0,18
            .value Name 'list' Load - 0,9..0,13
            .slice Name 'str' Load - 0,14..0,17
            .ctx Load
       .args[1]
        0] arg - 0,23..0,29
          .arg 'b'
          .annotation Name 'int' Load - 0,26..0,29
       .vararg arg - 0,36..0,37
         .arg 'c'
       .kwonlyargs[1]
        0] arg - 0,39..0,40
          .arg 'd'
       .kw_defaults[1]
        0] Constant 100 - 0,41..0,44
       .kwarg arg - 0,48..0,49
         .arg 'e'
       .defaults[1]
        0] Constant 1 - 0,32..0,33
     .body[1]
      0] Pass - 0,52..0,56
'''),

('body[0]', None, None, 'args', {}, ('exec', r'''
def f(\
\
): pass
'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass''',
r'''def f(a: list[str], /, b: int=1, *c, d=100, **e): pass''', r'''
Module - ROOT 0,0..0,56
  .body[1]
   0] FunctionDef - 0,0..0,56
     .name 'f'
     .args arguments - 0,6..0,49
       .posonlyargs[1]
        0] arg - 0,6..0,18
          .arg 'a'
          .annotation Subscript - 0,9..0,18
            .value Name 'list' Load - 0,9..0,13
            .slice Name 'str' Load - 0,14..0,17
            .ctx Load
       .args[1]
        0] arg - 0,23..0,29
          .arg 'b'
          .annotation Name 'int' Load - 0,26..0,29
       .vararg arg - 0,36..0,37
         .arg 'c'
       .kwonlyargs[1]
        0] arg - 0,39..0,40
          .arg 'd'
       .kw_defaults[1]
        0] Constant 100 - 0,41..0,44
       .kwarg arg - 0,48..0,49
         .arg 'e'
       .defaults[1]
        0] Constant 1 - 0,32..0,33
     .body[1]
      0] Pass - 0,52..0,56
'''),

('body[0]', 0, None, 'args', {}, ('exec',
r'''def f(a=1): pass'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''**IndexError('FunctionDef.args does not take an index')**'''),

('body[0]', None, None, 'args', {}, ('exec',
r'''def f(a=1): pass'''), ('arguments',
r''''''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0]', None, None, 'args', {}, ('exec',
r'''async def f(a=1): pass'''), (None,
r'''**DEL**'''),
r'''async def f(): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] AsyncFunctionDef - 0,0..0,19
     .name 'f'
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0]', None, None, 'args', {}, ('exec',
r'''async def f(a=1): pass'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''async def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass''',
r'''async def f(a: list[str], /, b: int=1, *c, d=100, **e): pass''', r'''
Module - ROOT 0,0..0,62
  .body[1]
   0] AsyncFunctionDef - 0,0..0,62
     .name 'f'
     .args arguments - 0,12..0,55
       .posonlyargs[1]
        0] arg - 0,12..0,24
          .arg 'a'
          .annotation Subscript - 0,15..0,24
            .value Name 'list' Load - 0,15..0,19
            .slice Name 'str' Load - 0,20..0,23
            .ctx Load
       .args[1]
        0] arg - 0,29..0,35
          .arg 'b'
          .annotation Name 'int' Load - 0,32..0,35
       .vararg arg - 0,42..0,43
         .arg 'c'
       .kwonlyargs[1]
        0] arg - 0,45..0,46
          .arg 'd'
       .kw_defaults[1]
        0] Constant 100 - 0,47..0,50
       .kwarg arg - 0,54..0,55
         .arg 'e'
       .defaults[1]
        0] Constant 1 - 0,38..0,39
     .body[1]
      0] Pass - 0,58..0,62
'''),

('body[0]', None, None, 'args', {}, ('exec',
r'''async def f(): pass'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''async def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass''',
r'''async def f(a: list[str], /, b: int=1, *c, d=100, **e): pass''', r'''
Module - ROOT 0,0..0,62
  .body[1]
   0] AsyncFunctionDef - 0,0..0,62
     .name 'f'
     .args arguments - 0,12..0,55
       .posonlyargs[1]
        0] arg - 0,12..0,24
          .arg 'a'
          .annotation Subscript - 0,15..0,24
            .value Name 'list' Load - 0,15..0,19
            .slice Name 'str' Load - 0,20..0,23
            .ctx Load
       .args[1]
        0] arg - 0,29..0,35
          .arg 'b'
          .annotation Name 'int' Load - 0,32..0,35
       .vararg arg - 0,42..0,43
         .arg 'c'
       .kwonlyargs[1]
        0] arg - 0,45..0,46
          .arg 'd'
       .kw_defaults[1]
        0] Constant 100 - 0,47..0,50
       .kwarg arg - 0,54..0,55
         .arg 'e'
       .defaults[1]
        0] Constant 1 - 0,38..0,39
     .body[1]
      0] Pass - 0,58..0,62
'''),

('body[0]', None, None, 'args', {}, ('exec', r'''
async def f(\
\
): pass
'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''async def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass''',
r'''async def f(a: list[str], /, b: int=1, *c, d=100, **e): pass''', r'''
Module - ROOT 0,0..0,62
  .body[1]
   0] AsyncFunctionDef - 0,0..0,62
     .name 'f'
     .args arguments - 0,12..0,55
       .posonlyargs[1]
        0] arg - 0,12..0,24
          .arg 'a'
          .annotation Subscript - 0,15..0,24
            .value Name 'list' Load - 0,15..0,19
            .slice Name 'str' Load - 0,20..0,23
            .ctx Load
       .args[1]
        0] arg - 0,29..0,35
          .arg 'b'
          .annotation Name 'int' Load - 0,32..0,35
       .vararg arg - 0,42..0,43
         .arg 'c'
       .kwonlyargs[1]
        0] arg - 0,45..0,46
          .arg 'd'
       .kw_defaults[1]
        0] Constant 100 - 0,47..0,50
       .kwarg arg - 0,54..0,55
         .arg 'e'
       .defaults[1]
        0] Constant 1 - 0,38..0,39
     .body[1]
      0] Pass - 0,58..0,62
'''),

('body[0]', 0, None, 'args', {}, ('exec',
r'''async def f(a=1): pass'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''**IndexError('AsyncFunctionDef.args does not take an index')**'''),

('body[0]', None, None, 'args', {}, ('exec',
r'''async def f(a=1): pass'''), ('arguments',
r''''''),
r'''async def f(): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] AsyncFunctionDef - 0,0..0,19
     .name 'f'
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0].value', None, None, 'args', {}, ('exec',
r'''lambda a=1: None'''), (None,
r'''**DEL**'''),
r'''lambda: None''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value Lambda - 0,0..0,12
       .body Constant None - 0,8..0,12
'''),

('body[0].value', None, None, 'args', {}, ('exec',
r'''lambda a=1: None'''), (None,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0].value', None, None, 'args', {}, ('exec',
r'''lambda a=1: None'''), (None,
r'''a, /, b=1, *c, d=100, **e'''),
r'''lambda a, /, b=1, *c, d=100, **e: None''', r'''
Module - ROOT 0,0..0,38
  .body[1]
   0] Expr - 0,0..0,38
     .value Lambda - 0,0..0,38
       .args arguments - 0,7..0,32
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .args[1]
          0] arg - 0,13..0,14
            .arg 'b'
         .vararg arg - 0,19..0,20
           .arg 'c'
         .kwonlyargs[1]
          0] arg - 0,22..0,23
            .arg 'd'
         .kw_defaults[1]
          0] Constant 100 - 0,24..0,27
         .kwarg arg - 0,31..0,32
           .arg 'e'
         .defaults[1]
          0] Constant 1 - 0,15..0,16
       .body Constant None - 0,34..0,38
'''),

('body[0].value', None, None, 'args', {}, ('exec',
r'''lambda: None'''), (None,
r'''a, /, b=1, *c, d=100, **e'''),
r'''lambda a, /, b=1, *c, d=100, **e: None''', r'''
Module - ROOT 0,0..0,38
  .body[1]
   0] Expr - 0,0..0,38
     .value Lambda - 0,0..0,38
       .args arguments - 0,7..0,32
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .args[1]
          0] arg - 0,13..0,14
            .arg 'b'
         .vararg arg - 0,19..0,20
           .arg 'c'
         .kwonlyargs[1]
          0] arg - 0,22..0,23
            .arg 'd'
         .kw_defaults[1]
          0] Constant 100 - 0,24..0,27
         .kwarg arg - 0,31..0,32
           .arg 'e'
         .defaults[1]
          0] Constant 1 - 0,15..0,16
       .body Constant None - 0,34..0,38
'''),

('body[0].value', None, None, 'args', {}, ('exec', r'''
lambda\
\
: None
'''), (None,
r'''a, /, b=1, *c, d=100, **e'''),
r'''lambda a, /, b=1, *c, d=100, **e: None''', r'''
Module - ROOT 0,0..0,38
  .body[1]
   0] Expr - 0,0..0,38
     .value Lambda - 0,0..0,38
       .args arguments - 0,7..0,32
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .args[1]
          0] arg - 0,13..0,14
            .arg 'b'
         .vararg arg - 0,19..0,20
           .arg 'c'
         .kwonlyargs[1]
          0] arg - 0,22..0,23
            .arg 'd'
         .kw_defaults[1]
          0] Constant 100 - 0,24..0,27
         .kwarg arg - 0,31..0,32
           .arg 'e'
         .defaults[1]
          0] Constant 1 - 0,15..0,16
       .body Constant None - 0,34..0,38
'''),

('body[0].value', 0, None, 'args', {}, ('exec',
r'''lambda a=1: None'''), ('arguments',
r'''a, /, b=1, *c, d=100, **e'''),
r'''**IndexError('Lambda.args does not take an index')**'''),

('body[0].value', None, None, 'args', {'raw': False}, ('exec',
r'''lambda a=1: None'''), ('arguments',
r''''''),
r'''lambda: None''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value Lambda - 0,0..0,12
       .body Constant None - 0,8..0,12
'''),

('body[0].value', None, None, 'op', {'raw': False}, ('exec',
r'''a and b'''), (None,
r'''or'''),
r'''a or b''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value BoolOp - 0,0..0,6
       .op Or
       .values[2]
        0] Name 'a' Load - 0,0..0,1
        1] Name 'b' Load - 0,5..0,6
'''),

('body[0].value', None, None, 'op', {}, ('exec',
r'''a and b'''), (None,
r'''+'''),
r'''**SyntaxError("expecting boolop, got '+'")**'''),

('body[0].value', None, None, 'op', {'raw': False}, ('exec',
r'''a and b and c'''), (None,
r'''or'''),
r'''a or b or c''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,11
     .value BoolOp - 0,0..0,11
       .op Or
       .values[3]
        0] Name 'a' Load - 0,0..0,1
        1] Name 'b' Load - 0,5..0,6
        2] Name 'c' Load - 0,10..0,11
'''),

('body[0].value', None, None, 'op', {'raw': False}, ('exec', r'''
(a) or ( b ) or (
c
)
'''), (None,
r'''and'''), r'''
(a) and ( b ) and (
c
)
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value BoolOp - 0,0..2,1
       .op And
       .values[3]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,10..0,11
        2] Name 'c' Load - 1,0..1,1
'''),

('body[0].value', None, None, 'op', {'raw': False}, ('exec', r'''
a\
and\
b \
  and \
 c
'''), (None,
r'''or'''), r'''
a\
or\
b \
  or \
 c
''', r'''
Module - ROOT 0,0..4,2
  .body[1]
   0] Expr - 0,0..4,2
     .value BoolOp - 0,0..4,2
       .op Or
       .values[3]
        0] Name 'a' Load - 0,0..0,1
        1] Name 'b' Load - 2,0..2,1
        2] Name 'c' Load - 4,1..4,2
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(*b): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(*b): pass'''), ('arg',
r'''new'''),
r'''def f(*new): pass''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] FunctionDef - 0,0..0,17
     .name 'f'
     .args arguments - 0,6..0,10
       .vararg arg - 0,7..0,10
         .arg 'new'
     .body[1]
      0] Pass - 0,13..0,17
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a=(1), *b): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(a=(1)): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] FunctionDef - 0,0..0,18
     .name 'f'
     .args arguments - 0,6..0,11
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a=(1), *b): pass'''), ('arg',
r'''new'''),
r'''def f(a=(1), *new): pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] FunctionDef - 0,0..0,24
     .name 'f'
     .args arguments - 0,6..0,17
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .vararg arg - 0,14..0,17
         .arg 'new'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a=(1), /, *b): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(a=(1), /): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] FunctionDef - 0,0..0,21
     .name 'f'
     .args arguments - 0,6..0,14
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].args', None, None, 'vararg', {}, ('exec', r'''
def f(a=(1), * \
 b \
 ): pass
'''), ('arg',
r'''**DEL**'''), r'''
def f(a=(1) \
 ): pass
''', r'''
Module - ROOT 0,0..1,8
  .body[1]
   0] FunctionDef - 0,0..1,8
     .name 'f'
     .args arguments - 0,6..0,11
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 1,4..1,8
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(*b, c=(1)): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(*, c=(1)): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] FunctionDef - 0,0..0,21
     .name 'f'
     .args arguments - 0,6..0,14
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,12..0,13
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(*b, c=(1)): pass'''), ('arg',
r'''new'''),
r'''def f(*new, c=(1)): pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] FunctionDef - 0,0..0,24
     .name 'f'
     .args arguments - 0,6..0,17
       .vararg arg - 0,7..0,10
         .arg 'new'
       .kwonlyargs[1]
        0] arg - 0,12..0,13
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,15..0,16
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(*b, ** c): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(** c): pass''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] FunctionDef - 0,0..0,17
     .name 'f'
     .args arguments - 0,6..0,10
       .kwarg arg - 0,9..0,10
         .arg 'c'
     .body[1]
      0] Pass - 0,13..0,17
'''),

('body[0].args', None, None, 'vararg', {}, ('exec', r'''
def f(*\
b\
, c=(1)): pass
'''), ('arg',
r'''**DEL**'''),
r'''def f(*, c=(1)): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] FunctionDef - 0,0..0,21
     .name 'f'
     .args arguments - 0,6..0,14
       .kwonlyargs[1]
        0] arg - 0,9..0,10
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,12..0,13
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a, *b, c=(1)): pass'''), ('arg',
r'''new'''),
r'''def f(a, *new, c=(1)): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] FunctionDef - 0,0..0,27
     .name 'f'
     .args arguments - 0,6..0,20
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .vararg arg - 0,10..0,13
         .arg 'new'
       .kwonlyargs[1]
        0] arg - 0,15..0,16
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,18..0,19
     .body[1]
      0] Pass - 0,23..0,27
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a, *b, ** c): pass'''), (None,
r'''**DEL**'''),
r'''def f(a, ** c): pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .args arguments - 0,6..0,13
       .args[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .kwarg arg - 0,12..0,13
         .arg 'c'
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a, /, *b, c=(1)): pass'''), ('arg',
r'''new'''),
r'''def f(a, /, *new, c=(1)): pass''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] FunctionDef - 0,0..0,30
     .name 'f'
     .args arguments - 0,6..0,23
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .vararg arg - 0,13..0,16
         .arg 'new'
       .kwonlyargs[1]
        0] arg - 0,18..0,19
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,21..0,22
     .body[1]
      0] Pass - 0,26..0,30
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a, /, *b, c=(1)): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(a, /, *, c=(1)): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] FunctionDef - 0,0..0,27
     .name 'f'
     .args arguments - 0,6..0,20
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .kwonlyargs[1]
        0] arg - 0,15..0,16
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,18..0,19
     .body[1]
      0] Pass - 0,23..0,27
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a, /, *b, ** c): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(a, /, ** c): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] FunctionDef - 0,0..0,23
     .name 'f'
     .args arguments - 0,6..0,16
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .kwarg arg - 0,15..0,16
         .arg 'c'
     .body[1]
      0] Pass - 0,19..0,23
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda: None'''), ('arg',
r'''**DEL**'''),
r'''lambda: None''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value Lambda - 0,0..0,12
       .body Constant None - 0,8..0,12
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda *b: None'''), ('arg',
r'''**DEL**'''),
r'''lambda: None''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value Lambda - 0,0..0,12
       .body Constant None - 0,8..0,12
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda *b: None'''), ('arg',
r'''new'''),
r'''lambda *new: None''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Lambda - 0,0..0,17
       .args arguments - 0,7..0,11
         .vararg arg - 0,8..0,11
           .arg 'new'
       .body Constant None - 0,13..0,17
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a=(1), *b: None'''), ('arg',
r'''**DEL**'''),
r'''lambda a=(1): None''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Expr - 0,0..0,18
     .value Lambda - 0,0..0,18
       .args arguments - 0,7..0,12
         .args[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,14..0,18
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a=(1), *b: None'''), ('arg',
r'''new'''),
r'''lambda a=(1), *new: None''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Expr - 0,0..0,24
     .value Lambda - 0,0..0,24
       .args arguments - 0,7..0,18
         .args[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .vararg arg - 0,15..0,18
           .arg 'new'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,20..0,24
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a=(1), /, *b: None'''), ('arg',
r'''**DEL**'''),
r'''lambda a=(1), /: None''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Expr - 0,0..0,21
     .value Lambda - 0,0..0,21
       .args arguments - 0,7..0,15
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,17..0,21
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec', r'''
lambda a=(1), * \
 b \
 : None
'''), ('arg',
r'''**DEL**'''), r'''
lambda a=(1) \
 : None
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Expr - 0,0..1,7
     .value Lambda - 0,0..1,7
       .args arguments - 0,7..0,12
         .args[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 1,3..1,7
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda *b, c=(1): None'''), ('arg',
r'''**DEL**'''),
r'''lambda *, c=(1): None''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Expr - 0,0..0,21
     .value Lambda - 0,0..0,21
       .args arguments - 0,7..0,15
         .kwonlyargs[1]
          0] arg - 0,10..0,11
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,13..0,14
       .body Constant None - 0,17..0,21
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda *b, ** c: None'''), ('arg',
r'''**DEL**'''),
r'''lambda ** c: None''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Lambda - 0,0..0,17
       .args arguments - 0,7..0,11
         .kwarg arg - 0,10..0,11
           .arg 'c'
       .body Constant None - 0,13..0,17
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda *b, c=(1): None'''), ('arg',
r'''new'''),
r'''lambda *new, c=(1): None''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Expr - 0,0..0,24
     .value Lambda - 0,0..0,24
       .args arguments - 0,7..0,18
         .vararg arg - 0,8..0,11
           .arg 'new'
         .kwonlyargs[1]
          0] arg - 0,13..0,14
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,16..0,17
       .body Constant None - 0,20..0,24
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec', r'''
lambda *\
b\
, c=(1): None
'''), ('arg',
r'''**DEL**'''),
r'''lambda *, c=(1): None''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Expr - 0,0..0,21
     .value Lambda - 0,0..0,21
       .args arguments - 0,7..0,15
         .kwonlyargs[1]
          0] arg - 0,10..0,11
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,13..0,14
       .body Constant None - 0,17..0,21
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a, *b, ** c: None'''), ('arg',
r'''**DEL**'''),
r'''lambda a, ** c: None''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Expr - 0,0..0,20
     .value Lambda - 0,0..0,20
       .args arguments - 0,7..0,14
         .args[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .kwarg arg - 0,13..0,14
           .arg 'c'
       .body Constant None - 0,16..0,20
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a, *b, c=(1): None'''), ('arg',
r'''new'''),
r'''lambda a, *new, c=(1): None''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Expr - 0,0..0,27
     .value Lambda - 0,0..0,27
       .args arguments - 0,7..0,21
         .args[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .vararg arg - 0,11..0,14
           .arg 'new'
         .kwonlyargs[1]
          0] arg - 0,16..0,17
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,19..0,20
       .body Constant None - 0,23..0,27
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a, /, *b, ** c: None'''), ('arg',
r'''**DEL**'''),
r'''lambda a, /, ** c: None''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] Expr - 0,0..0,23
     .value Lambda - 0,0..0,23
       .args arguments - 0,7..0,17
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .kwarg arg - 0,16..0,17
           .arg 'c'
       .body Constant None - 0,19..0,23
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a, /, *b, c=(2), ** d: None'''), ('arg',
r'''**DEL**'''),
r'''lambda a, /, *, c=(2), ** d: None''', r'''
Module - ROOT 0,0..0,33
  .body[1]
   0] Expr - 0,0..0,33
     .value Lambda - 0,0..0,33
       .args arguments - 0,7..0,27
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .kwonlyargs[1]
          0] arg - 0,16..0,17
            .arg 'c'
         .kw_defaults[1]
          0] Constant 2 - 0,19..0,20
         .kwarg arg - 0,26..0,27
           .arg 'd'
       .body Constant None - 0,29..0,33
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a, /, *b, c=(1): None'''), ('arg',
r'''new'''),
r'''lambda a, /, *new, c=(1): None''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] Expr - 0,0..0,30
     .value Lambda - 0,0..0,30
       .args arguments - 0,7..0,24
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .vararg arg - 0,14..0,17
           .arg 'new'
         .kwonlyargs[1]
          0] arg - 0,19..0,20
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,22..0,23
       .body Constant None - 0,26..0,30
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a, /, *b, c=(1): None'''), ('arg',
r'''**DEL**'''),
r'''lambda a, /, *, c=(1): None''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Expr - 0,0..0,27
     .value Lambda - 0,0..0,27
       .args arguments - 0,7..0,21
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .kwonlyargs[1]
          0] arg - 0,16..0,17
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,19..0,20
       .body Constant None - 0,23..0,27
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(*, c=(1)): pass'''), ('arg',
r'''new'''),
r'''def f(*new, c=(1)): pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] FunctionDef - 0,0..0,24
     .name 'f'
     .args arguments - 0,6..0,17
       .vararg arg - 0,7..0,10
         .arg 'new'
       .kwonlyargs[1]
        0] arg - 0,12..0,13
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,15..0,16
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(**d): pass'''), ('arg',
r'''new'''),
r'''def f(*new, **d): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] FunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,6..0,15
       .vararg arg - 0,7..0,10
         .arg 'new'
       .kwarg arg - 0,14..0,15
         .arg 'd'
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(b=(2), **d): pass'''), ('arg',
r'''new'''),
r'''def f(b=(2), *new, **d): pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] FunctionDef - 0,0..0,29
     .name 'f'
     .args arguments - 0,6..0,22
       .args[1]
        0] arg - 0,6..0,7
          .arg 'b'
       .vararg arg - 0,14..0,17
         .arg 'new'
       .kwarg arg - 0,21..0,22
         .arg 'd'
       .defaults[1]
        0] Constant 2 - 0,9..0,10
     .body[1]
      0] Pass - 0,25..0,29
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(b=(2)): pass'''), ('arg',
r'''new'''),
r'''def f(b=(2), *new): pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] FunctionDef - 0,0..0,24
     .name 'f'
     .args arguments - 0,6..0,17
       .args[1]
        0] arg - 0,6..0,7
          .arg 'b'
       .vararg arg - 0,14..0,17
         .arg 'new'
       .defaults[1]
        0] Constant 2 - 0,9..0,10
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(b=(2),): pass'''), ('arg',
r'''new'''),
r'''def f(b=(2), *new,): pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] FunctionDef - 0,0..0,25
     .name 'f'
     .args arguments - 0,6..0,18
       .args[1]
        0] arg - 0,6..0,7
          .arg 'b'
       .vararg arg - 0,14..0,17
         .arg 'new'
       .defaults[1]
        0] Constant 2 - 0,9..0,10
     .body[1]
      0] Pass - 0,21..0,25
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(b): pass'''), ('arg',
r'''new'''),
r'''def f(b, *new): pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .args arguments - 0,6..0,13
       .args[1]
        0] arg - 0,6..0,7
          .arg 'b'
       .vararg arg - 0,10..0,13
         .arg 'new'
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a=(3), /): pass'''), ('arg',
r'''new'''),
r'''def f(a=(3), /, *new): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] FunctionDef - 0,0..0,27
     .name 'f'
     .args arguments - 0,6..0,20
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .vararg arg - 0,17..0,20
         .arg 'new'
       .defaults[1]
        0] Constant 3 - 0,9..0,10
     .body[1]
      0] Pass - 0,23..0,27
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a, /): pass'''), ('arg',
r'''new'''),
r'''def f(a, /, *new): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] FunctionDef - 0,0..0,23
     .name 'f'
     .args arguments - 0,6..0,16
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .vararg arg - 0,13..0,16
         .arg 'new'
     .body[1]
      0] Pass - 0,19..0,23
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(): pass'''), ('arg',
r'''new'''),
r'''def f(*new): pass''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] FunctionDef - 0,0..0,17
     .name 'f'
     .args arguments - 0,6..0,10
       .vararg arg - 0,7..0,10
         .arg 'new'
     .body[1]
      0] Pass - 0,13..0,17
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(b=(2), *, c=(1)): pass'''), ('arg',
r'''new'''),
r'''def f(b=(2), *new, c=(1)): pass''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] FunctionDef - 0,0..0,31
     .name 'f'
     .args arguments - 0,6..0,24
       .args[1]
        0] arg - 0,6..0,7
          .arg 'b'
       .vararg arg - 0,14..0,17
         .arg 'new'
       .kwonlyargs[1]
        0] arg - 0,19..0,20
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,22..0,23
       .defaults[1]
        0] Constant 2 - 0,9..0,10
     .body[1]
      0] Pass - 0,27..0,31
'''),

('body[0].args', None, None, 'vararg', {}, ('exec',
r'''def f(a=(1), /, *, c=(1)): pass'''), ('arg',
r'''new'''),
r'''def f(a=(1), /, *new, c=(1)): pass''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] FunctionDef - 0,0..0,34
     .name 'f'
     .args arguments - 0,6..0,27
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .vararg arg - 0,17..0,20
         .arg 'new'
       .kwonlyargs[1]
        0] arg - 0,22..0,23
          .arg 'c'
       .kw_defaults[1]
        0] Constant 1 - 0,25..0,26
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,30..0,34
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda *, c=(1): None'''), ('arg',
r'''new'''),
r'''lambda *new, c=(1): None''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Expr - 0,0..0,24
     .value Lambda - 0,0..0,24
       .args arguments - 0,7..0,18
         .vararg arg - 0,8..0,11
           .arg 'new'
         .kwonlyargs[1]
          0] arg - 0,13..0,14
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,16..0,17
       .body Constant None - 0,20..0,24
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda **d: None'''), ('arg',
r'''new'''),
r'''lambda *new, **d: None''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value Lambda - 0,0..0,22
       .args arguments - 0,7..0,16
         .vararg arg - 0,8..0,11
           .arg 'new'
         .kwarg arg - 0,15..0,16
           .arg 'd'
       .body Constant None - 0,18..0,22
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda b=(2), **d: None'''), ('arg',
r'''new'''),
r'''lambda b=(2), *new, **d: None''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] Expr - 0,0..0,29
     .value Lambda - 0,0..0,29
       .args arguments - 0,7..0,23
         .args[1]
          0] arg - 0,7..0,8
            .arg 'b'
         .vararg arg - 0,15..0,18
           .arg 'new'
         .kwarg arg - 0,22..0,23
           .arg 'd'
         .defaults[1]
          0] Constant 2 - 0,10..0,11
       .body Constant None - 0,25..0,29
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda b=(2): None'''), ('arg',
r'''new'''),
r'''lambda b=(2), *new: None''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Expr - 0,0..0,24
     .value Lambda - 0,0..0,24
       .args arguments - 0,7..0,18
         .args[1]
          0] arg - 0,7..0,8
            .arg 'b'
         .vararg arg - 0,15..0,18
           .arg 'new'
         .defaults[1]
          0] Constant 2 - 0,10..0,11
       .body Constant None - 0,20..0,24
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda b=(2),: None'''), ('arg',
r'''new'''),
r'''lambda b=(2), *new,: None''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Expr - 0,0..0,25
     .value Lambda - 0,0..0,25
       .args arguments - 0,7..0,19
         .args[1]
          0] arg - 0,7..0,8
            .arg 'b'
         .vararg arg - 0,15..0,18
           .arg 'new'
         .defaults[1]
          0] Constant 2 - 0,10..0,11
       .body Constant None - 0,21..0,25
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda b: None'''), ('arg',
r'''new'''),
r'''lambda b, *new: None''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Expr - 0,0..0,20
     .value Lambda - 0,0..0,20
       .args arguments - 0,7..0,14
         .args[1]
          0] arg - 0,7..0,8
            .arg 'b'
         .vararg arg - 0,11..0,14
           .arg 'new'
       .body Constant None - 0,16..0,20
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a=(2), /: None'''), ('arg',
r'''new'''),
r'''lambda a=(2), /, *new: None''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Expr - 0,0..0,27
     .value Lambda - 0,0..0,27
       .args arguments - 0,7..0,21
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .vararg arg - 0,18..0,21
           .arg 'new'
         .defaults[1]
          0] Constant 2 - 0,10..0,11
       .body Constant None - 0,23..0,27
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a, /: None'''), ('arg',
r'''new'''),
r'''lambda a, /, *new: None''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] Expr - 0,0..0,23
     .value Lambda - 0,0..0,23
       .args arguments - 0,7..0,17
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .vararg arg - 0,14..0,17
           .arg 'new'
       .body Constant None - 0,19..0,23
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a, /: None'''), ('arg',
r'''new'''),
r'''lambda a, /, *new: None''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] Expr - 0,0..0,23
     .value Lambda - 0,0..0,23
       .args arguments - 0,7..0,17
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .vararg arg - 0,14..0,17
           .arg 'new'
       .body Constant None - 0,19..0,23
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda b=(2), *, c=(1): None'''), ('arg',
r'''new'''),
r'''lambda b=(2), *new, c=(1): None''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] Expr - 0,0..0,31
     .value Lambda - 0,0..0,31
       .args arguments - 0,7..0,25
         .args[1]
          0] arg - 0,7..0,8
            .arg 'b'
         .vararg arg - 0,15..0,18
           .arg 'new'
         .kwonlyargs[1]
          0] arg - 0,20..0,21
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,23..0,24
         .defaults[1]
          0] Constant 2 - 0,10..0,11
       .body Constant None - 0,27..0,31
'''),

('body[0].value.args', None, None, 'vararg', {}, ('exec',
r'''lambda a=(1), /, *, c=(1): None'''), ('arg',
r'''new'''),
r'''lambda a=(1), /, *new, c=(1): None''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] Expr - 0,0..0,34
     .value Lambda - 0,0..0,34
       .args arguments - 0,7..0,28
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .vararg arg - 0,18..0,21
           .arg 'new'
         .kwonlyargs[1]
          0] arg - 0,23..0,24
            .arg 'c'
         .kw_defaults[1]
          0] Constant 1 - 0,26..0,27
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,30..0,34
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(**e): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(**e): pass'''), ('arg',
r'''new'''),
r'''def f(**new): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] FunctionDef - 0,0..0,18
     .name 'f'
     .args arguments - 0,6..0,11
       .kwarg arg - 0,8..0,11
         .arg 'new'
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(d=(1), **e): pass'''), (None,
r'''**DEL**'''),
r'''def f(d=(1)): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] FunctionDef - 0,0..0,18
     .name 'f'
     .args arguments - 0,6..0,11
       .args[1]
        0] arg - 0,6..0,7
          .arg 'd'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(d=(1), **e): pass'''), ('arg',
r'''new'''),
r'''def f(d=(1), **new): pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] FunctionDef - 0,0..0,25
     .name 'f'
     .args arguments - 0,6..0,18
       .args[1]
        0] arg - 0,6..0,7
          .arg 'd'
       .kwarg arg - 0,15..0,18
         .arg 'new'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,21..0,25
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(*c, **e): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(*c): pass''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] FunctionDef - 0,0..0,15
     .name 'f'
     .args arguments - 0,6..0,8
       .vararg arg - 0,7..0,8
         .arg 'c'
     .body[1]
      0] Pass - 0,11..0,15
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(*c, **e): pass'''), ('arg',
r'''new'''),
r'''def f(*c, **new): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] FunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,6..0,15
       .vararg arg - 0,7..0,8
         .arg 'c'
       .kwarg arg - 0,12..0,15
         .arg 'new'
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(a, /, **e): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(a, /): pass''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] FunctionDef - 0,0..0,17
     .name 'f'
     .args arguments - 0,6..0,10
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
     .body[1]
      0] Pass - 0,13..0,17
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(a=(2), /, **e): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(a=(2), /): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] FunctionDef - 0,0..0,21
     .name 'f'
     .args arguments - 0,6..0,14
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .defaults[1]
        0] Constant 2 - 0,9..0,10
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(a: int, /, **e): pass'''), ('arg',
r'''**DEL**'''),
r'''def f(a: int, /): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] FunctionDef - 0,0..0,22
     .name 'f'
     .args arguments - 0,6..0,15
       .posonlyargs[1]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'int' Load - 0,9..0,12
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(a, /, **e): pass'''), ('arg',
r'''new'''),
r'''def f(a, /, **new): pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] FunctionDef - 0,0..0,24
     .name 'f'
     .args arguments - 0,6..0,17
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .kwarg arg - 0,14..0,17
         .arg 'new'
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda **e: None'''), ('arg',
r'''**DEL**'''),
r'''lambda: None''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value Lambda - 0,0..0,12
       .body Constant None - 0,8..0,12
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda **e: None'''), ('arg',
r'''new'''),
r'''lambda **new: None''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Expr - 0,0..0,18
     .value Lambda - 0,0..0,18
       .args arguments - 0,7..0,12
         .kwarg arg - 0,9..0,12
           .arg 'new'
       .body Constant None - 0,14..0,18
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda d=(1), **e: None'''), ('arg',
r'''**DEL**'''),
r'''lambda d=(1): None''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Expr - 0,0..0,18
     .value Lambda - 0,0..0,18
       .args arguments - 0,7..0,12
         .args[1]
          0] arg - 0,7..0,8
            .arg 'd'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,14..0,18
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda d=(1), **e: None'''), ('arg',
r'''new'''),
r'''lambda d=(1), **new: None''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Expr - 0,0..0,25
     .value Lambda - 0,0..0,25
       .args arguments - 0,7..0,19
         .args[1]
          0] arg - 0,7..0,8
            .arg 'd'
         .kwarg arg - 0,16..0,19
           .arg 'new'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,21..0,25
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda *c, **e: None'''), ('arg',
r'''**DEL**'''),
r'''lambda *c: None''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Expr - 0,0..0,15
     .value Lambda - 0,0..0,15
       .args arguments - 0,7..0,9
         .vararg arg - 0,8..0,9
           .arg 'c'
       .body Constant None - 0,11..0,15
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda *c, **e: None'''), ('arg',
r'''new'''),
r'''lambda *c, **new: None''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value Lambda - 0,0..0,22
       .args arguments - 0,7..0,16
         .vararg arg - 0,8..0,9
           .arg 'c'
         .kwarg arg - 0,13..0,16
           .arg 'new'
       .body Constant None - 0,18..0,22
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda a, /, **e: None'''), ('arg',
r'''**DEL**'''),
r'''lambda a, /: None''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Lambda - 0,0..0,17
       .args arguments - 0,7..0,11
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
       .body Constant None - 0,13..0,17
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda a=(2), /, **e: None'''), ('arg',
r'''**DEL**'''),
r'''lambda a=(2), /: None''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Expr - 0,0..0,21
     .value Lambda - 0,0..0,21
       .args arguments - 0,7..0,15
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .defaults[1]
          0] Constant 2 - 0,10..0,11
       .body Constant None - 0,17..0,21
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda a, /, **e: None'''), ('arg',
r'''new'''),
r'''lambda a, /, **new: None''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Expr - 0,0..0,24
     .value Lambda - 0,0..0,24
       .args arguments - 0,7..0,18
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .kwarg arg - 0,15..0,18
           .arg 'new'
       .body Constant None - 0,20..0,24
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(): pass'''), ('arg',
r'''new'''),
r'''def f(**new): pass''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] FunctionDef - 0,0..0,18
     .name 'f'
     .args arguments - 0,6..0,11
       .kwarg arg - 0,8..0,11
         .arg 'new'
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(c=(1)): pass'''), ('arg',
r'''new'''),
r'''def f(c=(1), **new): pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] FunctionDef - 0,0..0,25
     .name 'f'
     .args arguments - 0,6..0,18
       .args[1]
        0] arg - 0,6..0,7
          .arg 'c'
       .kwarg arg - 0,15..0,18
         .arg 'new'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,21..0,25
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(c=(1),): pass'''), ('arg',
r'''new'''),
r'''def f(c=(1), **new): pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] FunctionDef - 0,0..0,25
     .name 'f'
     .args arguments - 0,6..0,18
       .args[1]
        0] arg - 0,6..0,7
          .arg 'c'
       .kwarg arg - 0,15..0,18
         .arg 'new'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,21..0,25
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(a=(1), /): pass'''), ('arg',
r'''new'''),
r'''def f(a=(1), /, **new): pass''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] FunctionDef - 0,0..0,28
     .name 'f'
     .args arguments - 0,6..0,21
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .kwarg arg - 0,18..0,21
         .arg 'new'
       .defaults[1]
        0] Constant 1 - 0,9..0,10
     .body[1]
      0] Pass - 0,24..0,28
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(a: int, /): pass'''), ('arg',
r'''new'''),
r'''def f(a: int, /, **new): pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] FunctionDef - 0,0..0,29
     .name 'f'
     .args arguments - 0,6..0,22
       .posonlyargs[1]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'int' Load - 0,9..0,12
       .kwarg arg - 0,19..0,22
         .arg 'new'
     .body[1]
      0] Pass - 0,25..0,29
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(a, /): pass'''), ('arg',
r'''new'''),
r'''def f(a, /, **new): pass''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] FunctionDef - 0,0..0,24
     .name 'f'
     .args arguments - 0,6..0,17
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .kwarg arg - 0,14..0,17
         .arg 'new'
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0].args', None, None, 'kwarg', {}, ('exec',
r'''def f(a, /, ): pass'''), ('arg',
r'''new'''),
r'''def f(a, /, **new ): pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] FunctionDef - 0,0..0,25
     .name 'f'
     .args arguments - 0,6..0,17
       .posonlyargs[1]
        0] arg - 0,6..0,7
          .arg 'a'
       .kwarg arg - 0,14..0,17
         .arg 'new'
     .body[1]
      0] Pass - 0,21..0,25
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda: None'''), ('arg',
r'''new'''),
r'''lambda **new: None''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Expr - 0,0..0,18
     .value Lambda - 0,0..0,18
       .args arguments - 0,7..0,12
         .kwarg arg - 0,9..0,12
           .arg 'new'
       .body Constant None - 0,14..0,18
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda c=(1): None'''), ('arg',
r'''new'''),
r'''lambda c=(1), **new: None''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Expr - 0,0..0,25
     .value Lambda - 0,0..0,25
       .args arguments - 0,7..0,19
         .args[1]
          0] arg - 0,7..0,8
            .arg 'c'
         .kwarg arg - 0,16..0,19
           .arg 'new'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,21..0,25
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda c=(1),: None'''), ('arg',
r'''new'''),
r'''lambda c=(1), **new: None''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Expr - 0,0..0,25
     .value Lambda - 0,0..0,25
       .args arguments - 0,7..0,19
         .args[1]
          0] arg - 0,7..0,8
            .arg 'c'
         .kwarg arg - 0,16..0,19
           .arg 'new'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,21..0,25
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda a=(1), /: None'''), ('arg',
r'''new'''),
r'''lambda a=(1), /, **new: None''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] Expr - 0,0..0,28
     .value Lambda - 0,0..0,28
       .args arguments - 0,7..0,22
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .kwarg arg - 0,19..0,22
           .arg 'new'
         .defaults[1]
          0] Constant 1 - 0,10..0,11
       .body Constant None - 0,24..0,28
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda a, /: None'''), ('arg',
r'''new'''),
r'''lambda a, /, **new: None''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Expr - 0,0..0,24
     .value Lambda - 0,0..0,24
       .args arguments - 0,7..0,18
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .kwarg arg - 0,15..0,18
           .arg 'new'
       .body Constant None - 0,20..0,24
'''),

('body[0].value.args', None, None, 'kwarg', {}, ('exec',
r'''lambda a, /, : None'''), ('arg',
r'''new'''),
r'''lambda a, /, **new : None''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Expr - 0,0..0,25
     .value Lambda - 0,0..0,25
       .args arguments - 0,7..0,18
         .posonlyargs[1]
          0] arg - 0,7..0,8
            .arg 'a'
         .kwarg arg - 0,15..0,18
           .arg 'new'
       .body Constant None - 0,21..0,25
'''),

('body[0].value.values[0].value', None, None, 'operand', {'_ver': 12}, ('exec',
"\nf'{-0.:.1f}'\n"), (None,
r'''0.0'''),
"\nf'{-0.0:.1f}'\n", r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Expr - 0,0..0,13
     .value JoinedStr - 0,0..0,13
       .values[1]
        0] FormattedValue - 0,2..0,12
          .value UnaryOp - 0,3..0,7
            .op USub - 0,3..0,4
            .operand Constant 0.0 - 0,4..0,7
          .conversion -1
          .format_spec JoinedStr - 0,7..0,11
            .values[1]
             0] Constant '.1f' - 0,8..0,11
'''),

('body[0].targets[0]', 0, None, 'elts', {}, ('exec',
r'''(a, b) = c'''), (None,
r'''i in j'''),
r'''**NodeError('invalid expression for Tuple Store target')**'''),

('body[0].targets[0]', 0, None, 'elts', {}, ('exec',
r'''[a, b] = c'''), (None,
r'''i in j'''),
r'''**NodeError('invalid expression for List Store target')**'''),

('body[0].targets[0]', 0, None, 'elts', {}, ('exec',
r'''del (a, b)'''), (None,
r'''i in j'''),
r'''**NodeError('invalid expression for Tuple Del target')**'''),

('body[0].targets[0]', 0, None, 'elts', {}, ('exec',
r'''del [a, b]'''), (None,
r'''i in j'''),
r'''**NodeError('invalid expression for List Del target')**'''),
],

'Assign_targets': [  # ................................................................................

('body[0]', 0, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''), (None,
r'''**DEL**'''),
r'''(b, c) = d = z''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Assign - 0,0..0,14
     .targets[2]
      0] Tuple - 0,0..0,6
        .elts[2]
         0] Name 'b' Store - 0,1..0,2
         1] Name 'c' Store - 0,4..0,5
        .ctx Store
      1] Name 'd' Store - 0,9..0,10
     .value Name 'z' Load - 0,13..0,14
'''),

('body[0]', 0, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''), (None,
r'''new'''),
r'''new = (b, c) = d = z''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Assign - 0,0..0,20
     .targets[3]
      0] Name 'new' Store - 0,0..0,3
      1] Tuple - 0,6..0,12
        .elts[2]
         0] Name 'b' Store - 0,7..0,8
         1] Name 'c' Store - 0,10..0,11
        .ctx Store
      2] Name 'd' Store - 0,15..0,16
     .value Name 'z' Load - 0,19..0,20
'''),

('body[0]', 1, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''), (None,
r'''new'''),
r'''a = new = d = z''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Assign - 0,0..0,15
     .targets[3]
      0] Name 'a' Store - 0,0..0,1
      1] Name 'new' Store - 0,4..0,7
      2] Name 'd' Store - 0,10..0,11
     .value Name 'z' Load - 0,14..0,15
'''),

('body[0]', 2, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''), (None,
r'''new'''),
r'''a = (b, c) = new = z''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Assign - 0,0..0,20
     .targets[3]
      0] Name 'a' Store - 0,0..0,1
      1] Tuple - 0,4..0,10
        .elts[2]
         0] Name 'b' Store - 0,5..0,6
         1] Name 'c' Store - 0,8..0,9
        .ctx Store
      2] Name 'new' Store - 0,13..0,16
     .value Name 'z' Load - 0,19..0,20
'''),

('body[0]', -1, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''), (None,
r'''**DEL**'''),
r'''a = (b, c) = z''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Assign - 0,0..0,14
     .targets[2]
      0] Name 'a' Store - 0,0..0,1
      1] Tuple - 0,4..0,10
        .elts[2]
         0] Name 'b' Store - 0,5..0,6
         1] Name 'c' Store - 0,8..0,9
        .ctx Store
     .value Name 'z' Load - 0,13..0,14
'''),

('body[0]', -1, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''), (None,
r'''x, y'''),
r'''a = (b, c) = x, y = z''',
r'''a = (b, c) = (x, y) = z''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Assign - 0,0..0,21
     .targets[3]
      0] Name 'a' Store - 0,0..0,1
      1] Tuple - 0,4..0,10
        .elts[2]
         0] Name 'b' Store - 0,5..0,6
         1] Name 'c' Store - 0,8..0,9
        .ctx Store
      2] Tuple - 0,13..0,17
        .elts[2]
         0] Name 'x' Store - 0,13..0,14
         1] Name 'y' Store - 0,16..0,17
        .ctx Store
     .value Name 'z' Load - 0,20..0,21
'''),

('body[0]', -1, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''), (None,
r'''f()'''),
r'''**NodeError('invalid value for Assign.targets, got Call')**'''),

('body[0]', -4, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('', 1, None, 'targets', {'raw': False}, (None, r'''
a = \
b = \
c \
= \
z
'''), r'''
x \

''', r'''
a = \
x = \
c \
= \
z
''', r'''
Assign - ROOT 0,0..4,1
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 1,0..1,1
   2] Name 'c' Store - 2,0..2,1
  .value Name 'z' Load - 4,0..4,1
'''),

('', 1, None, 'targets', {}, (None, r'''
a = \
b = \
c \
= \
z
'''),
r'''x''', r'''
a = \
x = \
c \
= \
z
''', r'''
Assign - ROOT 0,0..4,1
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 1,0..1,1
   2] Name 'c' Store - 2,0..2,1
  .value Name 'z' Load - 4,0..4,1
'''),

('', 1, None, 'targets', {'raw': False}, ('_Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
x \

''', r'''
a = \
x = \
c \
= \

''', r'''
_Assign_targets - ROOT 0,0..4,0
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 1,0..1,1
   2] Name 'c' Store - 2,0..2,1
'''),

('', 1, None, 'targets', {}, ('_Assign_targets', r'''
a = \
b = \
c \
= \

'''),
r'''x''', r'''
a = \
x = \
c \
= \

''', r'''
_Assign_targets - ROOT 0,0..4,0
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 1,0..1,1
   2] Name 'c' Store - 2,0..2,1
'''),
],

'With_items': [  # ................................................................................

('', 0, None, 'items', {'raw': False}, (None,
r'''with _: pass'''), ('Tuple',
r'''x, y'''),
r'''with ((x, y)): pass''', r'''
With - ROOT 0,0..0,19
  .items[1]
   0] withitem - 0,5..0,13
     .context_expr Tuple - 0,6..0,12
       .elts[2]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'y' Load - 0,10..0,11
       .ctx Load
  .body[1]
   0] Pass - 0,15..0,19
'''),

('', 0, None, 'items', {'raw': False}, (None,
r'''with _: pass'''), ('Tuple',
r'''(x, y)'''),
r'''with ((x, y)): pass''', r'''
With - ROOT 0,0..0,19
  .items[1]
   0] withitem - 0,5..0,13
     .context_expr Tuple - 0,6..0,12
       .elts[2]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'y' Load - 0,10..0,11
       .ctx Load
  .body[1]
   0] Pass - 0,15..0,19
'''),

('', 0, None, 'items', {'raw': False}, (None,
r'''with (_): pass'''), ('Tuple',
r'''x, y'''),
r'''with ((x, y)): pass''', r'''
With - ROOT 0,0..0,19
  .items[1]
   0] withitem - 0,5..0,13
     .context_expr Tuple - 0,6..0,12
       .elts[2]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'y' Load - 0,10..0,11
       .ctx Load
  .body[1]
   0] Pass - 0,15..0,19
'''),

('', 0, None, 'items', {'raw': False}, (None,
r'''with (_): pass'''), ('Tuple',
r'''(x, y)'''),
r'''with ((x, y)): pass''', r'''
With - ROOT 0,0..0,19
  .items[1]
   0] withitem - 0,5..0,13
     .context_expr Tuple - 0,6..0,12
       .elts[2]
        0] Name 'x' Load - 0,7..0,8
        1] Name 'y' Load - 0,10..0,11
       .ctx Load
  .body[1]
   0] Pass - 0,15..0,19
'''),
],

'AsyncWith_items': [  # ................................................................................

('', 0, None, 'items', {'raw': False}, (None,
r'''async with _: pass'''), ('Tuple',
r'''x, y'''),
r'''async with ((x, y)): pass''', r'''
AsyncWith - ROOT 0,0..0,25
  .items[1]
   0] withitem - 0,11..0,19
     .context_expr Tuple - 0,12..0,18
       .elts[2]
        0] Name 'x' Load - 0,13..0,14
        1] Name 'y' Load - 0,16..0,17
       .ctx Load
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 0, None, 'items', {'raw': False}, (None,
r'''async with _: pass'''), ('Tuple',
r'''(x, y)'''),
r'''async with ((x, y)): pass''', r'''
AsyncWith - ROOT 0,0..0,25
  .items[1]
   0] withitem - 0,11..0,19
     .context_expr Tuple - 0,12..0,18
       .elts[2]
        0] Name 'x' Load - 0,13..0,14
        1] Name 'y' Load - 0,16..0,17
       .ctx Load
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 0, None, 'items', {'raw': False}, (None,
r'''async with (_): pass'''), ('Tuple',
r'''x, y'''),
r'''async with ((x, y)): pass''', r'''
AsyncWith - ROOT 0,0..0,25
  .items[1]
   0] withitem - 0,11..0,19
     .context_expr Tuple - 0,12..0,18
       .elts[2]
        0] Name 'x' Load - 0,13..0,14
        1] Name 'y' Load - 0,16..0,17
       .ctx Load
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 0, None, 'items', {'raw': False}, (None,
r'''async with (_): pass'''), ('Tuple',
r'''(x, y)'''),
r'''async with ((x, y)): pass''', r'''
AsyncWith - ROOT 0,0..0,25
  .items[1]
   0] withitem - 0,11..0,19
     .context_expr Tuple - 0,12..0,18
       .elts[2]
        0] Name 'x' Load - 0,13..0,14
        1] Name 'y' Load - 0,16..0,17
       .ctx Load
  .body[1]
   0] Pass - 0,21..0,25
'''),
],

'Import_names': [  # ................................................................................

('body[0]', 0, None, 'names', {}, ('exec',
r'''import a, c.d as e'''), (None,
r'''**DEL**'''),
r'''import c.d as e''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Import - 0,0..0,15
     .names[1]
      0] alias - 0,7..0,15
        .name 'c.d'
        .asname 'e'
'''),

('body[0]', 0, None, 'names', {}, ('exec',
r'''import a, c.d as e'''), ('alias',
r'''f as g'''),
r'''import f as g, c.d as e''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] Import - 0,0..0,23
     .names[2]
      0] alias - 0,7..0,13
        .name 'f'
        .asname 'g'
      1] alias - 0,15..0,23
        .name 'c.d'
        .asname 'e'
'''),

('body[0]', 1, None, 'names', {}, ('exec',
r'''import a, c.d as e'''), ('alias',
r'''f as g'''),
r'''import a, f as g''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Import - 0,0..0,16
     .names[2]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,16
        .name 'f'
        .asname 'g'
'''),

('body[0]', -1, None, 'names', {}, ('exec',
r'''import a, c.d as e'''), ('alias',
r'''f as g'''),
r'''import a, f as g''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Import - 0,0..0,16
     .names[2]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,16
        .name 'f'
        .asname 'g'
'''),

('body[0]', -2, None, 'names', {}, ('exec',
r'''import a, c.d as e'''), ('alias',
r'''f as g'''),
r'''import f as g, c.d as e''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] Import - 0,0..0,23
     .names[2]
      0] alias - 0,7..0,13
        .name 'f'
        .asname 'g'
      1] alias - 0,15..0,23
        .name 'c.d'
        .asname 'e'
'''),

('body[0]', -4, None, 'names', {}, ('exec',
r'''import a, c.d as e'''), ('alias',
r'''f as g'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'names', {}, ('exec',
r'''import a, c.d as e'''), ('alias',
r'''x.y as z'''),
r'''import x.y as z, c.d as e''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Import - 0,0..0,25
     .names[2]
      0] alias - 0,7..0,15
        .name 'x.y'
        .asname 'z'
      1] alias - 0,17..0,25
        .name 'c.d'
        .asname 'e'
'''),

('', 0, None, 'names', {'raw': False}, (None,
r'''import _'''), (None,
r'''(a)'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, None, 'names', {'coerce': False}, (None,
r'''import _'''), (None,
r'''(a)'''),
r'''**SyntaxError('invalid syntax')**'''),
],

'ImportFrom_names': [  # ................................................................................

('body[0]', None, None, 'module', {}, ('exec',
r'''from a import *'''), (None,
r'''new'''),
r'''from new import *''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'new'
     .names[1]
      0] alias - 0,16..0,17
        .name '*'
     .level 0
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from a import *'''), (None,
r'''x.y'''),
r'''from x.y import *''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'x.y'
     .names[1]
      0] alias - 0,16..0,17
        .name '*'
     .level 0
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from a import *'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete ImportFrom.module in this state')**'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from .a import *'''), (None,
r'''new'''),
r'''from .new import *''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ImportFrom - 0,0..0,18
     .module 'new'
     .names[1]
      0] alias - 0,17..0,18
        .name '*'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from .a import *'''), (None,
r'''x.y'''),
r'''from .x.y import *''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ImportFrom - 0,0..0,18
     .module 'x.y'
     .names[1]
      0] alias - 0,17..0,18
        .name '*'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from .a import *'''), (None,
r'''**DEL**'''),
r'''from . import *''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] ImportFrom - 0,0..0,15
     .names[1]
      0] alias - 0,14..0,15
        .name '*'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from . a import *'''), (None,
r'''new'''),
r'''from . new import *''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] ImportFrom - 0,0..0,19
     .module 'new'
     .names[1]
      0] alias - 0,18..0,19
        .name '*'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from . a import *'''), (None,
r'''x.y'''),
r'''from . x.y import *''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] ImportFrom - 0,0..0,19
     .module 'x.y'
     .names[1]
      0] alias - 0,18..0,19
        .name '*'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from . a import *'''), (None,
r'''**DEL**'''),
r'''from .  import *''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] ImportFrom - 0,0..0,16
     .names[1]
      0] alias - 0,15..0,16
        .name '*'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from . import *'''), (None,
r'''new'''),
r'''from .new import *''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ImportFrom - 0,0..0,18
     .module 'new'
     .names[1]
      0] alias - 0,17..0,18
        .name '*'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec', r'''
from . \
 .\
a import *
'''), (None,
r'''new'''), r'''
from . \
 .\
new import *
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] ImportFrom - 0,0..2,12
     .module 'new'
     .names[1]
      0] alias - 2,11..2,12
        .name '*'
     .level 2
'''),

('body[0]', None, None, 'module', {}, ('exec', r'''
from . \
.\
  a import *
'''), (None,
r'''**DEL**'''), r'''
from . \
.\
   import *
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] ImportFrom - 0,0..2,11
     .names[1]
      0] alias - 2,10..2,11
        .name '*'
     .level 2
'''),

('body[0]', None, None, 'module', {}, ('exec', r'''
from . \
 . \
 import *
'''), (None,
r'''new'''), r'''
from . \
 .new \
 import *
''', r'''
Module - ROOT 0,0..2,9
  .body[1]
   0] ImportFrom - 0,0..2,9
     .module 'new'
     .names[1]
      0] alias - 2,8..2,9
        .name '*'
     .level 2
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from a.b import c'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete ImportFrom.module in this state')**'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from a.b import c'''), (None,
r'''new'''),
r'''from new import c''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'new'
     .names[1]
      0] alias - 0,16..0,17
        .name 'c'
     .level 0
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from a.b import c'''), (None,
r'''x.y'''),
r'''from x.y import c''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'x.y'
     .names[1]
      0] alias - 0,16..0,17
        .name 'c'
     .level 0
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from .a.b import c'''), (None,
r'''**DEL**'''),
r'''from . import c''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] ImportFrom - 0,0..0,15
     .names[1]
      0] alias - 0,14..0,15
        .name 'c'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from .a.b import c'''), (None,
r'''new'''),
r'''from .new import c''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ImportFrom - 0,0..0,18
     .module 'new'
     .names[1]
      0] alias - 0,17..0,18
        .name 'c'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from .a.b import c'''), (None,
r'''x.y'''),
r'''from .x.y import c''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] ImportFrom - 0,0..0,18
     .module 'x.y'
     .names[1]
      0] alias - 0,17..0,18
        .name 'c'
     .level 1
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from ..a.b import c'''), (None,
r'''**DEL**'''),
r'''from .. import c''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] ImportFrom - 0,0..0,16
     .names[1]
      0] alias - 0,15..0,16
        .name 'c'
     .level 2
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from ..a.b import c'''), (None,
r'''new'''),
r'''from ..new import c''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] ImportFrom - 0,0..0,19
     .module 'new'
     .names[1]
      0] alias - 0,18..0,19
        .name 'c'
     .level 2
'''),

('body[0]', None, None, 'module', {}, ('exec',
r'''from ..a.b import c'''), (None,
r'''x.y'''),
r'''from ..x.y import c''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] ImportFrom - 0,0..0,19
     .module 'x.y'
     .names[1]
      0] alias - 0,18..0,19
        .name 'c'
     .level 2
'''),

('body[0]', 0, None, 'names', {}, ('exec',
r'''from z import (a, c as d)'''), ('alias',
r'''**DEL**'''),
r'''from z import (c as d)''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] ImportFrom - 0,0..0,22
     .module 'z'
     .names[1]
      0] alias - 0,15..0,21
        .name 'c'
        .asname 'd'
     .level 0
'''),

('body[0]', 0, None, 'names', {}, ('exec',
r'''from z import (a, c as d)'''), ('alias',
r'''f as g'''),
r'''from z import (f as g, c as d)''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] ImportFrom - 0,0..0,30
     .module 'z'
     .names[2]
      0] alias - 0,15..0,21
        .name 'f'
        .asname 'g'
      1] alias - 0,23..0,29
        .name 'c'
        .asname 'd'
     .level 0
'''),

('body[0]', 1, None, 'names', {}, ('exec',
r'''from z import (a, c as d)'''), ('alias',
r'''f as g'''),
r'''from z import (a, f as g)''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] ImportFrom - 0,0..0,25
     .module 'z'
     .names[2]
      0] alias - 0,15..0,16
        .name 'a'
      1] alias - 0,18..0,24
        .name 'f'
        .asname 'g'
     .level 0
'''),

('body[0]', -1, None, 'names', {}, ('exec',
r'''from z import (a, c as d)'''), ('alias',
r'''f as g'''),
r'''from z import (a, f as g)''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] ImportFrom - 0,0..0,25
     .module 'z'
     .names[2]
      0] alias - 0,15..0,16
        .name 'a'
      1] alias - 0,18..0,24
        .name 'f'
        .asname 'g'
     .level 0
'''),

('body[0]', -2, None, 'names', {}, ('exec',
r'''from z import (a, c as d)'''), ('alias',
r'''f as g'''),
r'''from z import (f as g, c as d)''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] ImportFrom - 0,0..0,30
     .module 'z'
     .names[2]
      0] alias - 0,15..0,21
        .name 'f'
        .asname 'g'
      1] alias - 0,23..0,29
        .name 'c'
        .asname 'd'
     .level 0
'''),

('body[0]', -4, None, 'names', {}, ('exec',
r'''from z import (a, c as d)'''), ('alias',
r'''f as g'''),
r'''**IndexError('index out of range')**'''),

('', 0, None, 'names', {'raw': False}, (None,
r'''from . import _'''), (None,
r'''(a)'''),
r'''**SyntaxError('ImportFrom.names cannot have explicit parentheses')**'''),

('', 0, None, 'names', {}, (None,
r'''from . import _'''), (None,
r'''(a, b)'''),
r'''**ParseError('expecting single name')**'''),

('', 0, None, 'names', {'coerce': False}, (None,
r'''from . import _'''), (None,
r'''(a)'''),
r'''**SyntaxError('ImportFrom.names cannot have explicit parentheses')**'''),

('', 0, None, 'names', {'coerce': False}, (None,
r'''from . import _'''), (None,
r'''(a, b)'''),
r'''**ParseError('expecting single name')**'''),
],

'Global_names': [  # ................................................................................

('body[0]', 0, None, 'names', {}, ('exec',
r'''global a, b'''), (None,
r'''**DEL**'''),
r'''global b''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'b'
'''),

('body[0]', 0, None, 'names', {}, ('exec',
r'''global a, b'''), (None,
r'''new'''),
r'''global new, b''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Global - 0,0..0,13
     .names[2]
      0] 'new'
      1] 'b'
'''),

('body[0]', 1, None, 'names', {}, ('exec',
r'''global a, b'''), (None,
r'''new'''),
r'''global a, new''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Global - 0,0..0,13
     .names[2]
      0] 'a'
      1] 'new'
'''),

('body[0]', -1, None, 'names', {}, ('exec',
r'''global a, b'''), (None,
r'''new'''),
r'''global a, new''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Global - 0,0..0,13
     .names[2]
      0] 'a'
      1] 'new'
'''),

('body[0]', -2, None, 'names', {}, ('exec', r'''
global \
a \
,\
b
'''), (None,
r'''new'''), r'''
global \
new \
,\
b
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Global - 0,0..3,1
     .names[2]
      0] 'new'
      1] 'b'
'''),

('body[0]', -4, None, 'names', {}, ('exec',
r'''global a, b'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),
],

'Nonlocal_names': [  # ................................................................................

('body[0]', 0, None, 'names', {}, ('exec',
r'''nonlocal a, b'''), (None,
r'''**DEL**'''),
r'''nonlocal b''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'b'
'''),

('body[0]', 0, None, 'names', {}, ('exec',
r'''nonlocal a, b'''), (None,
r'''new'''),
r'''nonlocal new, b''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Nonlocal - 0,0..0,15
     .names[2]
      0] 'new'
      1] 'b'
'''),

('body[0]', 1, None, 'names', {}, ('exec',
r'''nonlocal a, b'''), (None,
r'''new'''),
r'''nonlocal a, new''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Nonlocal - 0,0..0,15
     .names[2]
      0] 'a'
      1] 'new'
'''),

('body[0]', -1, None, 'names', {}, ('exec',
r'''nonlocal a, b'''), (None,
r'''new'''),
r'''nonlocal a, new''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Nonlocal - 0,0..0,15
     .names[2]
      0] 'a'
      1] 'new'
'''),

('body[0]', -2, None, 'names', {}, ('exec', r'''
nonlocal \
a \
,\
b
'''), (None,
r'''new'''), r'''
nonlocal \
new \
,\
b
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Nonlocal - 0,0..3,1
     .names[2]
      0] 'new'
      1] 'b'
'''),

('body[0]', -4, None, 'names', {}, ('exec',
r'''nonlocal a, b'''), (None,
r'''new'''),
r'''**IndexError('index out of range')**'''),

('body[0]', None, None, 'args', {}, ('exec',
r'''def f(a=1): pass'''), (None,
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),
],

'MatchClass': [  # ................................................................................

('', None, None, 'cls', {}, ('MatchClass',
r'''cls()'''), (None,
r'''new_cls'''),
r'''new_cls()''', r'''
MatchClass - ROOT 0,0..0,9
  .cls Name 'new_cls' Load - 0,0..0,7
'''),

('', None, None, 'cls', {}, ('MatchClass',
r'''cls()'''), (None, r'''
new
.
cls
'''),
r'''**NotImplementedError('cannot put multiline Attribute to MatchClass pattern expression')**'''),
],

'MatchMapping': [  # ................................................................................

('', 0, None, '_all', {}, ('MatchMapping',
r'''{1: a, 2: b, **c}'''), (None,
r'''**DEL**'''),
r'''{2: b, **c}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'b'
  .rest 'c'
'''),

('', 1, None, '_all', {}, ('MatchMapping',
r'''{1: a, 2: b, **c}'''), (None,
r'''**DEL**'''),
r'''{1: a, **c}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'c'
'''),

('', 2, None, '_all', {}, ('MatchMapping',
r'''{1: a, 2: b, **c}'''), (None,
r'''**DEL**'''),
r'''{1: a, 2: b}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'b'
'''),

('', 0, None, 'keys', {}, ('MatchMapping',
r'''{1: a}'''), (None,
r'''...'''),
r'''**NodeError('invalid value for MatchMapping.keys, got Constant')**'''),

('', 0, None, 'keys', {}, ('MatchMapping',
r'''{1: a}'''), (None, r'''
-
2
'''), r'''
{-
2: a}
''',
r'''{-2: a}''', r'''
MatchMapping - ROOT 0,0..1,5
  .keys[1]
   0] UnaryOp - 0,1..1,1
     .op USub - 0,1..0,2
     .operand Constant 2 - 1,0..1,1
  .patterns[1]
   0] MatchAs - 1,3..1,4
     .name 'a'
'''),
],

'type_params': [  # ................................................................................

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''), (None,
r'''**DEL**'''),
r'''def f[U: (str)](): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] FunctionDef - 0,0..0,23
     .name 'f'
     .body[1]
      0] Pass - 0,19..0,23
     .type_params[1]
      0] TypeVar - 0,6..0,14
        .name 'U'
        .bound Name 'str' Load - 0,10..0,13
'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''def f[V: list[int], U: (str)](): pass''', r'''
Module - ROOT 0,0..0,37
  .body[1]
   0] FunctionDef - 0,0..0,37
     .name 'f'
     .body[1]
      0] Pass - 0,33..0,37
     .type_params[2]
      0] TypeVar - 0,6..0,18
        .name 'V'
        .bound Subscript - 0,9..0,18
          .value Name 'list' Load - 0,9..0,13
          .slice Name 'int' Load - 0,14..0,17
          .ctx Load
      1] TypeVar - 0,20..0,28
        .name 'U'
        .bound Name 'str' Load - 0,24..0,27
'''),

('body[0]', 1, None, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''def f[T: int, V: list[int]](): pass''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] FunctionDef - 0,0..0,35
     .name 'f'
     .body[1]
      0] Pass - 0,31..0,35
     .type_params[2]
      0] TypeVar - 0,6..0,12
        .name 'T'
        .bound Name 'int' Load - 0,9..0,12
      1] TypeVar - 0,14..0,26
        .name 'V'
        .bound Subscript - 0,17..0,26
          .value Name 'list' Load - 0,17..0,21
          .slice Name 'int' Load - 0,22..0,25
          .ctx Load
'''),

('body[0]', -1, None, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''def f[T: int, V: list[int]](): pass''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] FunctionDef - 0,0..0,35
     .name 'f'
     .body[1]
      0] Pass - 0,31..0,35
     .type_params[2]
      0] TypeVar - 0,6..0,12
        .name 'T'
        .bound Name 'int' Load - 0,9..0,12
      1] TypeVar - 0,14..0,26
        .name 'V'
        .bound Subscript - 0,17..0,26
          .value Name 'list' Load - 0,17..0,21
          .slice Name 'int' Load - 0,22..0,25
          .ctx Load
'''),

('body[0]', -2, None, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''def f[V: list[int], U: (str)](): pass''', r'''
Module - ROOT 0,0..0,37
  .body[1]
   0] FunctionDef - 0,0..0,37
     .name 'f'
     .body[1]
      0] Pass - 0,33..0,37
     .type_params[2]
      0] TypeVar - 0,6..0,18
        .name 'V'
        .bound Subscript - 0,9..0,18
          .value Name 'list' Load - 0,9..0,13
          .slice Name 'int' Load - 0,14..0,17
          .ctx Load
      1] TypeVar - 0,20..0,28
        .name 'U'
        .bound Name 'str' Load - 0,24..0,27
'''),

('body[0]', -4, None, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''), (None,
r'''**DEL**'''),
r'''async def f[U: (str)](): pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncFunctionDef - 0,0..0,29
     .name 'f'
     .body[1]
      0] Pass - 0,25..0,29
     .type_params[1]
      0] TypeVar - 0,12..0,20
        .name 'U'
        .bound Name 'str' Load - 0,16..0,19
'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''async def f[V: list[int], U: (str)](): pass''', r'''
Module - ROOT 0,0..0,43
  .body[1]
   0] AsyncFunctionDef - 0,0..0,43
     .name 'f'
     .body[1]
      0] Pass - 0,39..0,43
     .type_params[2]
      0] TypeVar - 0,12..0,24
        .name 'V'
        .bound Subscript - 0,15..0,24
          .value Name 'list' Load - 0,15..0,19
          .slice Name 'int' Load - 0,20..0,23
          .ctx Load
      1] TypeVar - 0,26..0,34
        .name 'U'
        .bound Name 'str' Load - 0,30..0,33
'''),

('body[0]', 1, None, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''async def f[T: int, V: list[int]](): pass''', r'''
Module - ROOT 0,0..0,41
  .body[1]
   0] AsyncFunctionDef - 0,0..0,41
     .name 'f'
     .body[1]
      0] Pass - 0,37..0,41
     .type_params[2]
      0] TypeVar - 0,12..0,18
        .name 'T'
        .bound Name 'int' Load - 0,15..0,18
      1] TypeVar - 0,20..0,32
        .name 'V'
        .bound Subscript - 0,23..0,32
          .value Name 'list' Load - 0,23..0,27
          .slice Name 'int' Load - 0,28..0,31
          .ctx Load
'''),

('body[0]', -1, None, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''async def f[T: int, V: list[int]](): pass''', r'''
Module - ROOT 0,0..0,41
  .body[1]
   0] AsyncFunctionDef - 0,0..0,41
     .name 'f'
     .body[1]
      0] Pass - 0,37..0,41
     .type_params[2]
      0] TypeVar - 0,12..0,18
        .name 'T'
        .bound Name 'int' Load - 0,15..0,18
      1] TypeVar - 0,20..0,32
        .name 'V'
        .bound Subscript - 0,23..0,32
          .value Name 'list' Load - 0,23..0,27
          .slice Name 'int' Load - 0,28..0,31
          .ctx Load
'''),

('body[0]', -2, None, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''async def f[V: list[int], U: (str)](): pass''', r'''
Module - ROOT 0,0..0,43
  .body[1]
   0] AsyncFunctionDef - 0,0..0,43
     .name 'f'
     .body[1]
      0] Pass - 0,39..0,43
     .type_params[2]
      0] TypeVar - 0,12..0,24
        .name 'V'
        .bound Subscript - 0,15..0,24
          .value Name 'list' Load - 0,15..0,19
          .slice Name 'int' Load - 0,20..0,23
          .ctx Load
      1] TypeVar - 0,26..0,34
        .name 'U'
        .bound Name 'str' Load - 0,30..0,33
'''),

('body[0]', -4, None, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''), ('type_param',
r'''V: list[int]'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''), (None,
r'''**DEL**'''),
r'''class c[U: (str)]: pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] ClassDef - 0,0..0,23
     .name 'c'
     .body[1]
      0] Pass - 0,19..0,23
     .type_params[1]
      0] TypeVar - 0,8..0,16
        .name 'U'
        .bound Name 'str' Load - 0,12..0,15
'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''), ('type_param',
r'''V: list[int]'''),
r'''class c[V: list[int], U: (str)]: pass''', r'''
Module - ROOT 0,0..0,37
  .body[1]
   0] ClassDef - 0,0..0,37
     .name 'c'
     .body[1]
      0] Pass - 0,33..0,37
     .type_params[2]
      0] TypeVar - 0,8..0,20
        .name 'V'
        .bound Subscript - 0,11..0,20
          .value Name 'list' Load - 0,11..0,15
          .slice Name 'int' Load - 0,16..0,19
          .ctx Load
      1] TypeVar - 0,22..0,30
        .name 'U'
        .bound Name 'str' Load - 0,26..0,29
'''),

('body[0]', 1, None, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''), ('type_param',
r'''V: list[int]'''),
r'''class c[T: int, V: list[int]]: pass''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] ClassDef - 0,0..0,35
     .name 'c'
     .body[1]
      0] Pass - 0,31..0,35
     .type_params[2]
      0] TypeVar - 0,8..0,14
        .name 'T'
        .bound Name 'int' Load - 0,11..0,14
      1] TypeVar - 0,16..0,28
        .name 'V'
        .bound Subscript - 0,19..0,28
          .value Name 'list' Load - 0,19..0,23
          .slice Name 'int' Load - 0,24..0,27
          .ctx Load
'''),

('body[0]', -1, None, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''), ('type_param',
r'''V: list[int]'''),
r'''class c[T: int, V: list[int]]: pass''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] ClassDef - 0,0..0,35
     .name 'c'
     .body[1]
      0] Pass - 0,31..0,35
     .type_params[2]
      0] TypeVar - 0,8..0,14
        .name 'T'
        .bound Name 'int' Load - 0,11..0,14
      1] TypeVar - 0,16..0,28
        .name 'V'
        .bound Subscript - 0,19..0,28
          .value Name 'list' Load - 0,19..0,23
          .slice Name 'int' Load - 0,24..0,27
          .ctx Load
'''),

('body[0]', -2, None, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''), ('type_param',
r'''V: list[int]'''),
r'''class c[V: list[int], U: (str)]: pass''', r'''
Module - ROOT 0,0..0,37
  .body[1]
   0] ClassDef - 0,0..0,37
     .name 'c'
     .body[1]
      0] Pass - 0,33..0,37
     .type_params[2]
      0] TypeVar - 0,8..0,20
        .name 'V'
        .bound Subscript - 0,11..0,20
          .value Name 'list' Load - 0,11..0,15
          .slice Name 'int' Load - 0,16..0,19
          .ctx Load
      1] TypeVar - 0,22..0,30
        .name 'U'
        .bound Name 'str' Load - 0,26..0,29
'''),

('body[0]', -4, None, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''), ('type_param',
r'''V: list[int]'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''), ('type_param',
r'''**DEL**'''),
r'''type t[U: (str)] = ...''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] TypeAlias - 0,0..0,22
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,15
        .name 'U'
        .bound Name 'str' Load - 0,11..0,14
     .value Constant Ellipsis - 0,19..0,22
'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''), ('type_param',
r'''V: list[int]'''),
r'''type t[V: list[int], U: (str)] = ...''', r'''
Module - ROOT 0,0..0,36
  .body[1]
   0] TypeAlias - 0,0..0,36
     .name Name 't' Store - 0,5..0,6
     .type_params[2]
      0] TypeVar - 0,7..0,19
        .name 'V'
        .bound Subscript - 0,10..0,19
          .value Name 'list' Load - 0,10..0,14
          .slice Name 'int' Load - 0,15..0,18
          .ctx Load
      1] TypeVar - 0,21..0,29
        .name 'U'
        .bound Name 'str' Load - 0,25..0,28
     .value Constant Ellipsis - 0,33..0,36
'''),

('body[0]', 1, None, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''), ('type_param',
r'''V: list[int]'''),
r'''type t[T: int, V: list[int]] = ...''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] TypeAlias - 0,0..0,34
     .name Name 't' Store - 0,5..0,6
     .type_params[2]
      0] TypeVar - 0,7..0,13
        .name 'T'
        .bound Name 'int' Load - 0,10..0,13
      1] TypeVar - 0,15..0,27
        .name 'V'
        .bound Subscript - 0,18..0,27
          .value Name 'list' Load - 0,18..0,22
          .slice Name 'int' Load - 0,23..0,26
          .ctx Load
     .value Constant Ellipsis - 0,31..0,34
'''),

('body[0]', -1, None, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''), ('type_param',
r'''V: list[int]'''),
r'''type t[T: int, V: list[int]] = ...''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] TypeAlias - 0,0..0,34
     .name Name 't' Store - 0,5..0,6
     .type_params[2]
      0] TypeVar - 0,7..0,13
        .name 'T'
        .bound Name 'int' Load - 0,10..0,13
      1] TypeVar - 0,15..0,27
        .name 'V'
        .bound Subscript - 0,18..0,27
          .value Name 'list' Load - 0,18..0,22
          .slice Name 'int' Load - 0,23..0,26
          .ctx Load
     .value Constant Ellipsis - 0,31..0,34
'''),

('body[0]', -2, None, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''), ('type_param',
r'''V: list[int]'''),
r'''type t[V: list[int], U: (str)] = ...''', r'''
Module - ROOT 0,0..0,36
  .body[1]
   0] TypeAlias - 0,0..0,36
     .name Name 't' Store - 0,5..0,6
     .type_params[2]
      0] TypeVar - 0,7..0,19
        .name 'V'
        .bound Subscript - 0,10..0,19
          .value Name 'list' Load - 0,10..0,14
          .slice Name 'int' Load - 0,15..0,18
          .ctx Load
      1] TypeVar - 0,21..0,29
        .name 'U'
        .bound Name 'str' Load - 0,25..0,28
     .value Constant Ellipsis - 0,33..0,36
'''),

('body[0]', -4, None, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''), ('type_param',
r'''V: list[int]'''),
r'''**IndexError('index out of range')**'''),

('', 0, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''), (None,
r'''**DEL**'''),
r'''U: (str)''', r'''
_type_params - ROOT 0,0..0,8
  .type_params[1]
   0] TypeVar - 0,0..0,8
     .name 'U'
     .bound Name 'str' Load - 0,4..0,7
'''),

('', 0, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''), ('type_param',
r'''V: list[int]'''),
r'''V: list[int], U: (str)''', r'''
_type_params - ROOT 0,0..0,22
  .type_params[2]
   0] TypeVar - 0,0..0,12
     .name 'V'
     .bound Subscript - 0,3..0,12
       .value Name 'list' Load - 0,3..0,7
       .slice Name 'int' Load - 0,8..0,11
       .ctx Load
   1] TypeVar - 0,14..0,22
     .name 'U'
     .bound Name 'str' Load - 0,18..0,21
'''),

('', 1, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''), ('type_param',
r'''V: list[int]'''),
r'''T: int, V: list[int]''', r'''
_type_params - ROOT 0,0..0,20
  .type_params[2]
   0] TypeVar - 0,0..0,6
     .name 'T'
     .bound Name 'int' Load - 0,3..0,6
   1] TypeVar - 0,8..0,20
     .name 'V'
     .bound Subscript - 0,11..0,20
       .value Name 'list' Load - 0,11..0,15
       .slice Name 'int' Load - 0,16..0,19
       .ctx Load
'''),

('', -1, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''), ('type_param',
r'''V: list[int]'''),
r'''T: int, V: list[int]''', r'''
_type_params - ROOT 0,0..0,20
  .type_params[2]
   0] TypeVar - 0,0..0,6
     .name 'T'
     .bound Name 'int' Load - 0,3..0,6
   1] TypeVar - 0,8..0,20
     .name 'V'
     .bound Subscript - 0,11..0,20
       .value Name 'list' Load - 0,11..0,15
       .slice Name 'int' Load - 0,16..0,19
       .ctx Load
'''),

('', -2, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''), ('type_param',
r'''V: list[int]'''),
r'''V: list[int], U: (str)''', r'''
_type_params - ROOT 0,0..0,22
  .type_params[2]
   0] TypeVar - 0,0..0,12
     .name 'V'
     .bound Subscript - 0,3..0,12
       .value Name 'list' Load - 0,3..0,7
       .slice Name 'int' Load - 0,8..0,11
       .ctx Load
   1] TypeVar - 0,14..0,22
     .name 'U'
     .bound Name 'str' Load - 0,18..0,21
'''),

('', -4, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''), ('type_param',
r'''V: list[int]'''),
r'''**IndexError('index out of range')**'''),
],

'Call__args': [  # ................................................................................

('', 0, None, '_args', {}, ('Call',
r'''call(a0, b0)'''), ('Name',
r'''c0'''),
r'''call(c0, b0)''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'c0' Load - 0,5..0,7
   1] Name 'b0' Load - 0,9..0,11
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, *b1)'''), ('Name',
r'''c0'''),
r'''call(c0, *b1)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'c0' Load - 0,5..0,7
   1] Starred - 0,9..0,12
     .value Name 'b1' Load - 0,10..0,12
     .ctx Load
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, b=2)'''), ('Name',
r'''c0'''),
r'''call(c0, b=2)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'c0' Load - 0,5..0,7
  .keywords[1]
   0] keyword - 0,9..0,12
     .arg 'b'
     .value Constant 2 - 0,11..0,12
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, **b3)'''), ('Name',
r'''c0'''),
r'''call(c0, **b3)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'c0' Load - 0,5..0,7
  .keywords[1]
   0] keyword - 0,9..0,13
     .value Name 'b3' Load - 0,11..0,13
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, b0)'''), ('Starred',
r'''*c1'''),
r'''call(*c1, b0)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Starred - 0,5..0,8
     .value Name 'c1' Load - 0,6..0,8
     .ctx Load
   1] Name 'b0' Load - 0,10..0,12
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, *b1)'''), ('Starred',
r'''*c1'''),
r'''call(*c1, *b1)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Starred - 0,5..0,8
     .value Name 'c1' Load - 0,6..0,8
     .ctx Load
   1] Starred - 0,10..0,13
     .value Name 'b1' Load - 0,11..0,13
     .ctx Load
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, b=2)'''), ('Starred',
r'''*c1'''),
r'''call(*c1, b=2)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,8
     .value Name 'c1' Load - 0,6..0,8
     .ctx Load
  .keywords[1]
   0] keyword - 0,10..0,13
     .arg 'b'
     .value Constant 2 - 0,12..0,13
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, **b3)'''), ('Starred',
r'''*c1'''),
r'''call(*c1, **b3)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,8
     .value Name 'c1' Load - 0,6..0,8
     .ctx Load
  .keywords[1]
   0] keyword - 0,10..0,14
     .value Name 'b3' Load - 0,12..0,14
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, b0)'''), ('keyword',
r'''c=2'''),
r'''**NodeError('keyword arglike cannot precede positional arglike')**'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, *b1)'''), ('keyword',
r'''c=2'''),
r'''call(c=2, *b1)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,10..0,13
     .value Name 'b1' Load - 0,11..0,13
     .ctx Load
  .keywords[1]
   0] keyword - 0,5..0,8
     .arg 'c'
     .value Constant 2 - 0,7..0,8
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, b=2)'''), ('keyword',
r'''c=2'''),
r'''call(c=2, b=2)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .keywords[2]
   0] keyword - 0,5..0,8
     .arg 'c'
     .value Constant 2 - 0,7..0,8
   1] keyword - 0,10..0,13
     .arg 'b'
     .value Constant 2 - 0,12..0,13
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, **b3)'''), ('keyword',
r'''c=2'''),
r'''call(c=2, **b3)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .keywords[2]
   0] keyword - 0,5..0,8
     .arg 'c'
     .value Constant 2 - 0,7..0,8
   1] keyword - 0,10..0,14
     .value Name 'b3' Load - 0,12..0,14
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, b0)'''), ('keyword',
r'''**c3'''),
r'''**NodeError('keyword arglike unpacking cannot precede positional arglike')**'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, *b1)'''), ('keyword',
r'''**c3'''),
r'''**NodeError('keyword arglike unpacking cannot precede iterable arglike unpacking')**'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, b=2)'''), ('keyword',
r'''**c3'''),
r'''call(**c3, b=2)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .keywords[2]
   0] keyword - 0,5..0,9
     .value Name 'c3' Load - 0,7..0,9
   1] keyword - 0,11..0,14
     .arg 'b'
     .value Constant 2 - 0,13..0,14
'''),

('', 0, None, '_args', {}, ('Call',
r'''call(a0, **b3)'''), ('keyword',
r'''**c3'''),
r'''call(**c3, **b3)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .keywords[2]
   0] keyword - 0,5..0,9
     .value Name 'c3' Load - 0,7..0,9
   1] keyword - 0,11..0,15
     .value Name 'b3' Load - 0,13..0,15
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(a0, **b3)'''), ('Name',
r'''c0'''),
r'''call(a0, c0)''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a0' Load - 0,5..0,7
   1] Name 'c0' Load - 0,9..0,11
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(*a1, **b3)'''), ('Name',
r'''c0'''),
r'''call(*a1, c0)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Starred - 0,5..0,8
     .value Name 'a1' Load - 0,6..0,8
     .ctx Load
   1] Name 'c0' Load - 0,10..0,12
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(a=2, **b3)'''), ('Name',
r'''c0'''),
r'''**NodeError('positional arglike cannot follow keyword arglike')**'''),

('', 1, None, '_args', {}, ('Call',
r'''call(**a3, **b3)'''), ('Name',
r'''c0'''),
r'''**NodeError('positional arglike cannot follow keyword arglike unpacking')**'''),

('', 1, None, '_args', {}, ('Call',
r'''call(a0, **b3)'''), ('Starred',
r'''*c1'''),
r'''call(a0, *c1)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a0' Load - 0,5..0,7
   1] Starred - 0,9..0,12
     .value Name 'c1' Load - 0,10..0,12
     .ctx Load
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(*a1, **b3)'''), ('Starred',
r'''*c1'''),
r'''call(*a1, *c1)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Starred - 0,5..0,8
     .value Name 'a1' Load - 0,6..0,8
     .ctx Load
   1] Starred - 0,10..0,13
     .value Name 'c1' Load - 0,11..0,13
     .ctx Load
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(a=2, **b3)'''), ('Starred',
r'''*c1'''),
r'''call(a=2, *c1)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,10..0,13
     .value Name 'c1' Load - 0,11..0,13
     .ctx Load
  .keywords[1]
   0] keyword - 0,5..0,8
     .arg 'a'
     .value Constant 2 - 0,7..0,8
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(**a3, **b3)'''), ('Starred',
r'''*c1'''),
r'''**NodeError('iterable arglike unpacking cannot follow keyword arglike unpacking')**'''),

('', 1, None, '_args', {}, ('Call',
r'''call(a0, **b3)'''), ('keyword',
r'''c=2'''),
r'''call(a0, c=2)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a0' Load - 0,5..0,7
  .keywords[1]
   0] keyword - 0,9..0,12
     .arg 'c'
     .value Constant 2 - 0,11..0,12
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(*a1, **b3)'''), ('keyword',
r'''c=2'''),
r'''call(*a1, c=2)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,8
     .value Name 'a1' Load - 0,6..0,8
     .ctx Load
  .keywords[1]
   0] keyword - 0,10..0,13
     .arg 'c'
     .value Constant 2 - 0,12..0,13
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(a=2, **b3)'''), ('keyword',
r'''c=2'''),
r'''call(a=2, c=2)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .keywords[2]
   0] keyword - 0,5..0,8
     .arg 'a'
     .value Constant 2 - 0,7..0,8
   1] keyword - 0,10..0,13
     .arg 'c'
     .value Constant 2 - 0,12..0,13
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(**a3, **b3)'''), ('keyword',
r'''c=2'''),
r'''call(**a3, c=2)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .keywords[2]
   0] keyword - 0,5..0,9
     .value Name 'a3' Load - 0,7..0,9
   1] keyword - 0,11..0,14
     .arg 'c'
     .value Constant 2 - 0,13..0,14
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(a0, **b3)'''), ('keyword',
r'''**c3'''),
r'''call(a0, **c3)''', r'''
Call - ROOT 0,0..0,14
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a0' Load - 0,5..0,7
  .keywords[1]
   0] keyword - 0,9..0,13
     .value Name 'c3' Load - 0,11..0,13
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(*a1, **b3)'''), ('keyword',
r'''**c3'''),
r'''call(*a1, **c3)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,8
     .value Name 'a1' Load - 0,6..0,8
     .ctx Load
  .keywords[1]
   0] keyword - 0,10..0,14
     .value Name 'c3' Load - 0,12..0,14
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(a=2, **b3)'''), ('keyword',
r'''**c3'''),
r'''call(a=2, **c3)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .keywords[2]
   0] keyword - 0,5..0,8
     .arg 'a'
     .value Constant 2 - 0,7..0,8
   1] keyword - 0,10..0,14
     .value Name 'c3' Load - 0,12..0,14
'''),

('', 1, None, '_args', {}, ('Call',
r'''call(**a3, **b3)'''), ('keyword',
r'''**c3'''),
r'''call(**a3, **c3)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .keywords[2]
   0] keyword - 0,5..0,9
     .value Name 'a3' Load - 0,7..0,9
   1] keyword - 0,11..0,15
     .value Name 'c3' Load - 0,13..0,15
'''),
],

'ClassDef__bases': [  # ................................................................................

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, b0): pass'''), ('Name',
r'''c0'''),
r'''class cls(c0, b0): pass''', r'''
ClassDef - ROOT 0,0..0,23
  .name 'cls'
  .bases[2]
   0] Name 'c0' Load - 0,10..0,12
   1] Name 'b0' Load - 0,14..0,16
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, *b1): pass'''), ('Name',
r'''c0'''),
r'''class cls(c0, *b1): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[2]
   0] Name 'c0' Load - 0,10..0,12
   1] Starred - 0,14..0,17
     .value Name 'b1' Load - 0,15..0,17
     .ctx Load
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, b=2): pass'''), ('Name',
r'''c0'''),
r'''class cls(c0, b=2): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[1]
   0] Name 'c0' Load - 0,10..0,12
  .keywords[1]
   0] keyword - 0,14..0,17
     .arg 'b'
     .value Constant 2 - 0,16..0,17
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, **b3): pass'''), ('Name',
r'''c0'''),
r'''class cls(c0, **b3): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[1]
   0] Name 'c0' Load - 0,10..0,12
  .keywords[1]
   0] keyword - 0,14..0,18
     .value Name 'b3' Load - 0,16..0,18
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, b0): pass'''), ('Starred',
r'''*c1'''),
r'''class cls(*c1, b0): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[2]
   0] Starred - 0,10..0,13
     .value Name 'c1' Load - 0,11..0,13
     .ctx Load
   1] Name 'b0' Load - 0,15..0,17
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, *b1): pass'''), ('Starred',
r'''*c1'''),
r'''class cls(*c1, *b1): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[2]
   0] Starred - 0,10..0,13
     .value Name 'c1' Load - 0,11..0,13
     .ctx Load
   1] Starred - 0,15..0,18
     .value Name 'b1' Load - 0,16..0,18
     .ctx Load
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, b=2): pass'''), ('Starred',
r'''*c1'''),
r'''class cls(*c1, b=2): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,13
     .value Name 'c1' Load - 0,11..0,13
     .ctx Load
  .keywords[1]
   0] keyword - 0,15..0,18
     .arg 'b'
     .value Constant 2 - 0,17..0,18
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, **b3): pass'''), ('Starred',
r'''*c1'''),
r'''class cls(*c1, **b3): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,13
     .value Name 'c1' Load - 0,11..0,13
     .ctx Load
  .keywords[1]
   0] keyword - 0,15..0,19
     .value Name 'b3' Load - 0,17..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, b0): pass'''), ('keyword',
r'''c=2'''),
r'''**NodeError('keyword arglike cannot precede positional arglike')**'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, *b1): pass'''), ('keyword',
r'''c=2'''),
r'''class cls(c=2, *b1): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[1]
   0] Starred - 0,15..0,18
     .value Name 'b1' Load - 0,16..0,18
     .ctx Load
  .keywords[1]
   0] keyword - 0,10..0,13
     .arg 'c'
     .value Constant 2 - 0,12..0,13
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, b=2): pass'''), ('keyword',
r'''c=2'''),
r'''class cls(c=2, b=2): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,13
     .arg 'c'
     .value Constant 2 - 0,12..0,13
   1] keyword - 0,15..0,18
     .arg 'b'
     .value Constant 2 - 0,17..0,18
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, **b3): pass'''), ('keyword',
r'''c=2'''),
r'''class cls(c=2, **b3): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,13
     .arg 'c'
     .value Constant 2 - 0,12..0,13
   1] keyword - 0,15..0,19
     .value Name 'b3' Load - 0,17..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, b0): pass'''), ('keyword',
r'''**c3'''),
r'''**NodeError('keyword arglike unpacking cannot precede positional arglike')**'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, *b1): pass'''), ('keyword',
r'''**c3'''),
r'''**NodeError('keyword arglike unpacking cannot precede iterable arglike unpacking')**'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, b=2): pass'''), ('keyword',
r'''**c3'''),
r'''class cls(**c3, b=2): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,14
     .value Name 'c3' Load - 0,12..0,14
   1] keyword - 0,16..0,19
     .arg 'b'
     .value Constant 2 - 0,18..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 0, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, **b3): pass'''), ('keyword',
r'''**c3'''),
r'''class cls(**c3, **b3): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,14
     .value Name 'c3' Load - 0,12..0,14
   1] keyword - 0,16..0,20
     .value Name 'b3' Load - 0,18..0,20
  .body[1]
   0] Pass - 0,23..0,27
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, **b3): pass'''), ('Name',
r'''c0'''),
r'''class cls(a0, c0): pass''', r'''
ClassDef - ROOT 0,0..0,23
  .name 'cls'
  .bases[2]
   0] Name 'a0' Load - 0,10..0,12
   1] Name 'c0' Load - 0,14..0,16
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(*a1, **b3): pass'''), ('Name',
r'''c0'''),
r'''class cls(*a1, c0): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[2]
   0] Starred - 0,10..0,13
     .value Name 'a1' Load - 0,11..0,13
     .ctx Load
   1] Name 'c0' Load - 0,15..0,17
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(a=2, **b3): pass'''), ('Name',
r'''c0'''),
r'''**NodeError('positional arglike cannot follow keyword arglike')**'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(**a3, **b3): pass'''), ('Name',
r'''c0'''),
r'''**NodeError('positional arglike cannot follow keyword arglike unpacking')**'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, **b3): pass'''), ('Starred',
r'''*c1'''),
r'''class cls(a0, *c1): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[2]
   0] Name 'a0' Load - 0,10..0,12
   1] Starred - 0,14..0,17
     .value Name 'c1' Load - 0,15..0,17
     .ctx Load
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(*a1, **b3): pass'''), ('Starred',
r'''*c1'''),
r'''class cls(*a1, *c1): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[2]
   0] Starred - 0,10..0,13
     .value Name 'a1' Load - 0,11..0,13
     .ctx Load
   1] Starred - 0,15..0,18
     .value Name 'c1' Load - 0,16..0,18
     .ctx Load
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(a=2, **b3): pass'''), ('Starred',
r'''*c1'''),
r'''class cls(a=2, *c1): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[1]
   0] Starred - 0,15..0,18
     .value Name 'c1' Load - 0,16..0,18
     .ctx Load
  .keywords[1]
   0] keyword - 0,10..0,13
     .arg 'a'
     .value Constant 2 - 0,12..0,13
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(**a3, **b3): pass'''), ('Starred',
r'''*c1'''),
r'''**NodeError('iterable arglike unpacking cannot follow keyword arglike unpacking')**'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, **b3): pass'''), ('keyword',
r'''c=2'''),
r'''class cls(a0, c=2): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[1]
   0] Name 'a0' Load - 0,10..0,12
  .keywords[1]
   0] keyword - 0,14..0,17
     .arg 'c'
     .value Constant 2 - 0,16..0,17
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(*a1, **b3): pass'''), ('keyword',
r'''c=2'''),
r'''class cls(*a1, c=2): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,13
     .value Name 'a1' Load - 0,11..0,13
     .ctx Load
  .keywords[1]
   0] keyword - 0,15..0,18
     .arg 'c'
     .value Constant 2 - 0,17..0,18
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(a=2, **b3): pass'''), ('keyword',
r'''c=2'''),
r'''class cls(a=2, c=2): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,13
     .arg 'a'
     .value Constant 2 - 0,12..0,13
   1] keyword - 0,15..0,18
     .arg 'c'
     .value Constant 2 - 0,17..0,18
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(**a3, **b3): pass'''), ('keyword',
r'''c=2'''),
r'''class cls(**a3, c=2): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,14
     .value Name 'a3' Load - 0,12..0,14
   1] keyword - 0,16..0,19
     .arg 'c'
     .value Constant 2 - 0,18..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(a0, **b3): pass'''), ('keyword',
r'''**c3'''),
r'''class cls(a0, **c3): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[1]
   0] Name 'a0' Load - 0,10..0,12
  .keywords[1]
   0] keyword - 0,14..0,18
     .value Name 'c3' Load - 0,16..0,18
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(*a1, **b3): pass'''), ('keyword',
r'''**c3'''),
r'''class cls(*a1, **c3): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,13
     .value Name 'a1' Load - 0,11..0,13
     .ctx Load
  .keywords[1]
   0] keyword - 0,15..0,19
     .value Name 'c3' Load - 0,17..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(a=2, **b3): pass'''), ('keyword',
r'''**c3'''),
r'''class cls(a=2, **c3): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,13
     .arg 'a'
     .value Constant 2 - 0,12..0,13
   1] keyword - 0,15..0,19
     .value Name 'c3' Load - 0,17..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, None, '_bases', {}, ('ClassDef',
r'''class cls(**a3, **b3): pass'''), ('keyword',
r'''**c3'''),
r'''class cls(**a3, **c3): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,14
     .value Name 'a3' Load - 0,12..0,14
   1] keyword - 0,16..0,20
     .value Name 'c3' Load - 0,18..0,20
  .body[1]
   0] Pass - 0,23..0,27
'''),
],

'_arglikes': [  # ................................................................................

('', 0, None, None, {}, ('_arglikes',
r'''a0, b0'''), ('Name',
r'''c0'''),
r'''c0, b0''', r'''
_arglikes - ROOT 0,0..0,6
  .arglikes[2]
   0] Name 'c0' Load - 0,0..0,2
   1] Name 'b0' Load - 0,4..0,6
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, *b1'''), ('Name',
r'''c0'''),
r'''c0, *b1''', r'''
_arglikes - ROOT 0,0..0,7
  .arglikes[2]
   0] Name 'c0' Load - 0,0..0,2
   1] Starred - 0,4..0,7
     .value Name 'b1' Load - 0,5..0,7
     .ctx Load
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, b=2'''), ('Name',
r'''c0'''),
r'''c0, b=2''', r'''
_arglikes - ROOT 0,0..0,7
  .arglikes[2]
   0] Name 'c0' Load - 0,0..0,2
   1] keyword - 0,4..0,7
     .arg 'b'
     .value Constant 2 - 0,6..0,7
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, **b3'''), ('Name',
r'''c0'''),
r'''c0, **b3''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] Name 'c0' Load - 0,0..0,2
   1] keyword - 0,4..0,8
     .value Name 'b3' Load - 0,6..0,8
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, b0'''), ('Starred',
r'''*c1'''),
r'''*c1, b0''', r'''
_arglikes - ROOT 0,0..0,7
  .arglikes[2]
   0] Starred - 0,0..0,3
     .value Name 'c1' Load - 0,1..0,3
     .ctx Load
   1] Name 'b0' Load - 0,5..0,7
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, *b1'''), ('Starred',
r'''*c1'''),
r'''*c1, *b1''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] Starred - 0,0..0,3
     .value Name 'c1' Load - 0,1..0,3
     .ctx Load
   1] Starred - 0,5..0,8
     .value Name 'b1' Load - 0,6..0,8
     .ctx Load
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, b=2'''), ('Starred',
r'''*c1'''),
r'''*c1, b=2''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] Starred - 0,0..0,3
     .value Name 'c1' Load - 0,1..0,3
     .ctx Load
   1] keyword - 0,5..0,8
     .arg 'b'
     .value Constant 2 - 0,7..0,8
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, **b3'''), ('Starred',
r'''*c1'''),
r'''*c1, **b3''', r'''
_arglikes - ROOT 0,0..0,9
  .arglikes[2]
   0] Starred - 0,0..0,3
     .value Name 'c1' Load - 0,1..0,3
     .ctx Load
   1] keyword - 0,5..0,9
     .value Name 'b3' Load - 0,7..0,9
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, b0'''), ('keyword',
r'''c=2'''),
r'''**NodeError('keyword arglike cannot precede positional arglike')**'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, *b1'''), ('keyword',
r'''c=2'''),
r'''c=2, *b1''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] keyword - 0,0..0,3
     .arg 'c'
     .value Constant 2 - 0,2..0,3
   1] Starred - 0,5..0,8
     .value Name 'b1' Load - 0,6..0,8
     .ctx Load
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, b=2'''), ('keyword',
r'''c=2'''),
r'''c=2, b=2''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] keyword - 0,0..0,3
     .arg 'c'
     .value Constant 2 - 0,2..0,3
   1] keyword - 0,5..0,8
     .arg 'b'
     .value Constant 2 - 0,7..0,8
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, **b3'''), ('keyword',
r'''c=2'''),
r'''c=2, **b3''', r'''
_arglikes - ROOT 0,0..0,9
  .arglikes[2]
   0] keyword - 0,0..0,3
     .arg 'c'
     .value Constant 2 - 0,2..0,3
   1] keyword - 0,5..0,9
     .value Name 'b3' Load - 0,7..0,9
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, b0'''), ('keyword',
r'''**c3'''),
r'''**NodeError('keyword arglike unpacking cannot precede positional arglike')**'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, *b1'''), ('keyword',
r'''**c3'''),
r'''**NodeError('keyword arglike unpacking cannot precede iterable arglike unpacking')**'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, b=2'''), ('keyword',
r'''**c3'''),
r'''**c3, b=2''', r'''
_arglikes - ROOT 0,0..0,9
  .arglikes[2]
   0] keyword - 0,0..0,4
     .value Name 'c3' Load - 0,2..0,4
   1] keyword - 0,6..0,9
     .arg 'b'
     .value Constant 2 - 0,8..0,9
'''),

('', 0, None, None, {}, ('_arglikes',
r'''a0, **b3'''), ('keyword',
r'''**c3'''),
r'''**c3, **b3''', r'''
_arglikes - ROOT 0,0..0,10
  .arglikes[2]
   0] keyword - 0,0..0,4
     .value Name 'c3' Load - 0,2..0,4
   1] keyword - 0,6..0,10
     .value Name 'b3' Load - 0,8..0,10
'''),

('', 1, None, None, {}, ('_arglikes',
r'''a0, **b3'''), ('Name',
r'''c0'''),
r'''a0, c0''', r'''
_arglikes - ROOT 0,0..0,6
  .arglikes[2]
   0] Name 'a0' Load - 0,0..0,2
   1] Name 'c0' Load - 0,4..0,6
'''),

('', 1, None, None, {}, ('_arglikes',
r'''*a1, **b3'''), ('Name',
r'''c0'''),
r'''*a1, c0''', r'''
_arglikes - ROOT 0,0..0,7
  .arglikes[2]
   0] Starred - 0,0..0,3
     .value Name 'a1' Load - 0,1..0,3
     .ctx Load
   1] Name 'c0' Load - 0,5..0,7
'''),

('', 1, None, None, {}, ('_arglikes',
r'''a=2, **b3'''), ('Name',
r'''c0'''),
r'''**NodeError('positional arglike cannot follow keyword arglike')**'''),

('', 1, None, None, {}, ('_arglikes',
r'''**a3, **b3'''), ('Name',
r'''c0'''),
r'''**NodeError('positional arglike cannot follow keyword arglike unpacking')**'''),

('', 1, None, None, {}, ('_arglikes',
r'''a0, **b3'''), ('Starred',
r'''*c1'''),
r'''a0, *c1''', r'''
_arglikes - ROOT 0,0..0,7
  .arglikes[2]
   0] Name 'a0' Load - 0,0..0,2
   1] Starred - 0,4..0,7
     .value Name 'c1' Load - 0,5..0,7
     .ctx Load
'''),

('', 1, None, None, {}, ('_arglikes',
r'''*a1, **b3'''), ('Starred',
r'''*c1'''),
r'''*a1, *c1''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] Starred - 0,0..0,3
     .value Name 'a1' Load - 0,1..0,3
     .ctx Load
   1] Starred - 0,5..0,8
     .value Name 'c1' Load - 0,6..0,8
     .ctx Load
'''),

('', 1, None, None, {}, ('_arglikes',
r'''a=2, **b3'''), ('Starred',
r'''*c1'''),
r'''a=2, *c1''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] keyword - 0,0..0,3
     .arg 'a'
     .value Constant 2 - 0,2..0,3
   1] Starred - 0,5..0,8
     .value Name 'c1' Load - 0,6..0,8
     .ctx Load
'''),

('', 1, None, None, {}, ('_arglikes',
r'''**a3, **b3'''), ('Starred',
r'''*c1'''),
r'''**NodeError('iterable arglike unpacking cannot follow keyword arglike unpacking')**'''),

('', 1, None, None, {}, ('_arglikes',
r'''a0, **b3'''), ('keyword',
r'''c=2'''),
r'''a0, c=2''', r'''
_arglikes - ROOT 0,0..0,7
  .arglikes[2]
   0] Name 'a0' Load - 0,0..0,2
   1] keyword - 0,4..0,7
     .arg 'c'
     .value Constant 2 - 0,6..0,7
'''),

('', 1, None, None, {}, ('_arglikes',
r'''*a1, **b3'''), ('keyword',
r'''c=2'''),
r'''*a1, c=2''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] Starred - 0,0..0,3
     .value Name 'a1' Load - 0,1..0,3
     .ctx Load
   1] keyword - 0,5..0,8
     .arg 'c'
     .value Constant 2 - 0,7..0,8
'''),

('', 1, None, None, {}, ('_arglikes',
r'''a=2, **b3'''), ('keyword',
r'''c=2'''),
r'''a=2, c=2''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] keyword - 0,0..0,3
     .arg 'a'
     .value Constant 2 - 0,2..0,3
   1] keyword - 0,5..0,8
     .arg 'c'
     .value Constant 2 - 0,7..0,8
'''),

('', 1, None, None, {}, ('_arglikes',
r'''**a3, **b3'''), ('keyword',
r'''c=2'''),
r'''**a3, c=2''', r'''
_arglikes - ROOT 0,0..0,9
  .arglikes[2]
   0] keyword - 0,0..0,4
     .value Name 'a3' Load - 0,2..0,4
   1] keyword - 0,6..0,9
     .arg 'c'
     .value Constant 2 - 0,8..0,9
'''),

('', 1, None, None, {}, ('_arglikes',
r'''a0, **b3'''), ('keyword',
r'''**c3'''),
r'''a0, **c3''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[2]
   0] Name 'a0' Load - 0,0..0,2
   1] keyword - 0,4..0,8
     .value Name 'c3' Load - 0,6..0,8
'''),

('', 1, None, None, {}, ('_arglikes',
r'''*a1, **b3'''), ('keyword',
r'''**c3'''),
r'''*a1, **c3''', r'''
_arglikes - ROOT 0,0..0,9
  .arglikes[2]
   0] Starred - 0,0..0,3
     .value Name 'a1' Load - 0,1..0,3
     .ctx Load
   1] keyword - 0,5..0,9
     .value Name 'c3' Load - 0,7..0,9
'''),

('', 1, None, None, {}, ('_arglikes',
r'''a=2, **b3'''), ('keyword',
r'''**c3'''),
r'''a=2, **c3''', r'''
_arglikes - ROOT 0,0..0,9
  .arglikes[2]
   0] keyword - 0,0..0,3
     .arg 'a'
     .value Constant 2 - 0,2..0,3
   1] keyword - 0,5..0,9
     .value Name 'c3' Load - 0,7..0,9
'''),

('', 1, None, None, {}, ('_arglikes',
r'''**a3, **b3'''), ('keyword',
r'''**c3'''),
r'''**a3, **c3''', r'''
_arglikes - ROOT 0,0..0,10
  .arglikes[2]
   0] keyword - 0,0..0,4
     .value Name 'a3' Load - 0,2..0,4
   1] keyword - 0,6..0,10
     .value Name 'c3' Load - 0,8..0,10
'''),
],

'arglike_no_parenthesize': [  # ................................................................................

('', 0, None, 'bases', {}, (None,
r'''class cls(b): pass'''),
r'''*not b''',
r'''class cls(*not b): pass''', r'''
ClassDef - ROOT 0,0..0,23
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,16
     .value UnaryOp - 0,11..0,16
       .op Not - 0,11..0,14
       .operand Name 'b' Load - 0,15..0,16
     .ctx Load
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', 0, None, 'args', {}, (None,
r'''call(a)'''),
r'''*not a''',
r'''call(*not a)''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,11
     .value UnaryOp - 0,6..0,11
       .op Not - 0,6..0,9
       .operand Name 'a' Load - 0,10..0,11
     .ctx Load
'''),

('slice', 0, None, None, {'_ver': 11}, (None,
r'''a[b,]'''),
r'''*not a''',
r'''a[*not a,]''', r'''
Subscript - ROOT 0,0..0,10
  .value Name 'a' Load - 0,0..0,1
  .slice Tuple - 0,2..0,9
    .elts[1]
     0] Starred - 0,2..0,8
       .value UnaryOp - 0,3..0,8
         .op Not - 0,3..0,6
         .operand Name 'a' Load - 0,7..0,8
       .ctx Load
    .ctx Load
  .ctx Load
'''),

('slice', 0, None, None, {'_ver': 11, 'raw': False}, (None,
r'''a[*b]'''),
r'''*not a''',
r'''a[*not a,]''', r'''
Subscript - ROOT 0,0..0,10
  .value Name 'a' Load - 0,0..0,1
  .slice Tuple - 0,2..0,9
    .elts[1]
     0] Starred - 0,2..0,8
       .value UnaryOp - 0,3..0,8
         .op Not - 0,3..0,6
         .operand Name 'a' Load - 0,7..0,8
       .ctx Load
    .ctx Load
  .ctx Load
'''),

('slice', 0, None, None, {'_ver': 11, 'raw': False}, (None,
r'''a[(b,)]'''),
r'''*not a''',
r'''a[(*(not a),)]''', r'''
Subscript - ROOT 0,0..0,14
  .value Name 'a' Load - 0,0..0,1
  .slice Tuple - 0,2..0,13
    .elts[1]
     0] Starred - 0,3..0,11
       .value UnaryOp - 0,5..0,10
         .op Not - 0,5..0,8
         .operand Name 'a' Load - 0,9..0,10
       .ctx Load
    .ctx Load
  .ctx Load
'''),

('', 1, None, '_bases', {}, (None,
r'''class cls(a, *b): pass'''),
r'''*not b''',
r'''class cls(a, *not b): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,19
     .value UnaryOp - 0,14..0,19
       .op Not - 0,14..0,17
       .operand Name 'b' Load - 0,18..0,19
     .ctx Load
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, None, '_args', {}, (None,
r'''call(a, *b)'''),
r'''*not b''',
r'''call(a, *not b)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,8..0,14
     .value UnaryOp - 0,9..0,14
       .op Not - 0,9..0,12
       .operand Name 'b' Load - 0,13..0,14
     .ctx Load
'''),

('', 1, None, None, {}, ('_arglikes',
r'''a, *b'''),
r'''*not b''',
r'''a, *not b''', r'''
_arglikes - ROOT 0,0..0,9
  .arglikes[2]
   0] Name 'a' Load - 0,0..0,1
   1] Starred - 0,3..0,9
     .value UnaryOp - 0,4..0,9
       .op Not - 0,4..0,7
       .operand Name 'b' Load - 0,8..0,9
     .ctx Load
'''),
],

'raw': [  # ................................................................................

('', 1, None, None, {'raw': True, 'to': 'values[-1]'}, (None,
r'''{1: 2, 3: 4, 5: 6}'''),
r'''7: 8''',
r'''{1: 2, 7: 8}''', r'''
Dict - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 7 - 0,7..0,8
  .values[2]
   0] Constant 2 - 0,4..0,5
   1] Constant 8 - 0,10..0,11
'''),

('', 1, None, None, {'raw': True, 'to': 'patterns[-1]'}, ('pattern',
r'''{1: 2, 3: 4, 5: 6}'''),
r'''7: 8''',
r'''{1: 2, 7: 8}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 7 - 0,7..0,8
  .patterns[2]
   0] MatchValue - 0,4..0,5
     .value Constant 2 - 0,4..0,5
   1] MatchValue - 0,10..0,11
     .value Constant 8 - 0,10..0,11
'''),

('', 0, None, 'ops', {'raw': True, 'to': 'comparators[-1]'}, (None,
r'''a < b < c'''),
r'''>= z''',
r'''a >= z''', r'''
Compare - ROOT 0,0..0,6
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] GtE - 0,2..0,4
  .comparators[1]
   0] Name 'z' Load - 0,5..0,6
'''),

('', None, None, 'rest', {'raw': True}, ('pattern',
r'''{1: 2, **c}'''),
r'''d''',
r'''{1: 2, **d}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchValue - 0,4..0,5
     .value Constant 2 - 0,4..0,5
  .rest 'd'
'''),

('', None, None, 'args', {'raw': True}, (None,
r'''lambda: None'''),
r'''a''',
r'''lambda a: None''', r'''
Lambda - ROOT 0,0..0,14
  .args arguments - 0,7..0,8
    .args[1]
     0] arg - 0,7..0,8
       .arg 'a'
  .body Constant None - 0,10..0,14
'''),

('', None, None, 'args', {'raw': True}, (None,
r'''lambda: None'''),
r''' a''',
r'''lambda a: None''', r'''
Lambda - ROOT 0,0..0,14
  .args arguments - 0,7..0,8
    .args[1]
     0] arg - 0,7..0,8
       .arg 'a'
  .body Constant None - 0,10..0,14
'''),

('', None, None, 'args', {'raw': True}, (None,
r'''lambda a: None'''),
r'''''',
r'''lambda : None''', r'''
Lambda - ROOT 0,0..0,13
  .body Constant None - 0,9..0,13
'''),

('', 0, None, 'args', {'raw': True}, (None,
r'''call(i for i in j)'''),
r'''''',
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
'''),

('', 0, None, 'args', {'raw': True}, (None,
r'''call(i for i in j)'''),
r'''a''',
r'''call(a)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
'''),

('', 0, None, 'args', {'raw': True}, (None,
r'''call((i for i in j))'''),
r'''a''',
r'''call(a)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
'''),

('', 0, None, 'args', {'raw': True}, (None,
r'''call(a)'''),
r'''i for i in j''',
r'''call(i for i in j)''', r'''
Call - ROOT 0,0..0,18
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] GeneratorExp - 0,4..0,18
     .elt Name 'i' Load - 0,5..0,6
     .generators[1]
      0] comprehension - 0,7..0,17
        .target Name 'i' Store - 0,11..0,12
        .iter Name 'j' Load - 0,16..0,17
        .is_async 0
'''),

('', 1, None, None, {'raw': True, 'to': 'elts[2]'}, (None,
r'''[(a), (b), (c), (d)]'''),
r'''e''',
r'''[(a), e, (d)]''', r'''
List - ROOT 0,0..0,13
  .elts[3]
   0] Name 'a' Load - 0,2..0,3
   1] Name 'e' Load - 0,6..0,7
   2] Name 'd' Load - 0,10..0,11
  .ctx Load
'''),

('', 1, None, None, {'raw': True, 'to': 'elts[2]', 'pars': False}, (None,
r'''[(a), (b), (c), (d)]'''),
r'''e''',
r'''[(a), (e), (d)]''', r'''
List - ROOT 0,0..0,15
  .elts[3]
   0] Name 'a' Load - 0,2..0,3
   1] Name 'e' Load - 0,7..0,8
   2] Name 'd' Load - 0,12..0,13
  .ctx Load
'''),

('', 1, None, None, {'raw': True}, (None,
r'''global a, b, c'''),
r'''new''',
r'''global a, new, c''', r'''
Global - ROOT 0,0..0,16
  .names[3]
   0] 'a'
   1] 'new'
   2] 'c'
'''),

('', 1, None, None, {'raw': True, 'to': 'elts[0]'}, (None,
r'''[a, b]'''),
r'''new''',
r'''**ValueError("'to' node must follow self")**'''),

('', 1, None, None, {'raw': True, 'to': ''}, (None, r'''
a
b
c
'''),
r'''new''', r'''
a
new
''', r'''
Module - ROOT 0,0..1,3
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,3
     .value Name 'new' Load - 1,0..1,3
'''),

('body[1]', None, None, None, {'raw': True, 'to': ''}, (None, r'''
if 1:
    a
    b
    c
'''),
r'''new''', r'''
if 1:
    a
    new
''', r'''
If - ROOT 0,0..2,7
  .test Constant 1 - 0,3..0,4
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,7
     .value Name 'new' Load - 2,4..2,7
'''),

('body[0]', 1, None, 'body', {'raw': True, 'to': 'body[0]'}, ('exec', r'''
if 1:
    a
    b
    c
'''),
r'''new''', r'''
if 1:
    a
    new
''', r'''
Module - ROOT 0,0..2,7
  .body[1]
   0] If - 0,0..2,7
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'a' Load - 1,4..1,5
      1] Expr - 2,4..2,7
        .value Name 'new' Load - 2,4..2,7
'''),

('body[0].body[1]', None, None, None, {'raw': True, 'to': ''}, ('exec', r'''
if 1:
    a
    b
    c
'''),
r'''new''', r'''
if 1:
    a
    new
''', r'''
Module - ROOT 0,0..2,7
  .body[1]
   0] If - 0,0..2,7
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'a' Load - 1,4..1,5
      1] Expr - 2,4..2,7
        .value Name 'new' Load - 2,4..2,7
'''),

('', 0, None, 'body', {'raw': True, 'to': 'body[0].body[1]'}, ('exec', r'''
if 1:
    a
    b
    c
'''), r'''
if 2:
    new
''', r'''
if 2:
    new
    c
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 2 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,7
        .value Name 'new' Load - 1,4..1,7
      1] Expr - 2,4..2,5
        .value Name 'c' Load - 2,4..2,5
'''),

('', 1, None, None, {'raw': True, 'to': ''}, (None,
r'''a, b, c'''),
r'''new''',
r'''a, new''', r'''
Tuple - ROOT 0,0..0,6
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'new' Load - 0,3..0,6
  .ctx Load
'''),

('', 0, None, 'body', {'raw': True, 'to': 'body[0].value.elts[1]'}, ('exec',
r'''a, b, c'''),
r'''new''',
r'''new, c''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Tuple - 0,0..0,6
       .elts[2]
        0] Name 'new' Load - 0,0..0,3
        1] Name 'c' Load - 0,5..0,6
       .ctx Load
'''),

('body[0]', None, None, 'value', {'raw': True, 'to': 'body[0].value.elts[1]'}, ('exec',
r'''a, b, c'''),
r'''new''',
r'''new, c''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Tuple - 0,0..0,6
       .elts[2]
        0] Name 'new' Load - 0,0..0,3
        1] Name 'c' Load - 0,5..0,6
       .ctx Load
'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''None''',
r'''None''',
r'''Constant None - ROOT 0,0..0,4'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''True''',
r'''True''',
r'''Constant True - ROOT 0,0..0,4'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''False''',
r'''False''',
r'''Constant False - ROOT 0,0..0,5'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''b"bytes"''',
r'''b"bytes"''',
r'''Constant b'bytes' - ROOT 0,0..0,8'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''"str"''',
r'''"str"''',
r'''Constant 'str' - ROOT 0,0..0,5'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''1''',
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''1.0''',
r'''1.0''',
r'''Constant 1.0 - ROOT 0,0..0,3'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''1j''',
r'''1j''',
r'''Constant 1j - ROOT 0,0..0,2'''),

('', None, None, 'value', {'raw': True}, (None,
r'''123'''),
r'''...''',
r'''...''',
r'''Constant Ellipsis - ROOT 0,0..0,3'''),

('', None, None, None, {'raw': True}, (pattern,
r'''True'''),
r'''None''',
r'''None''',
r'''MatchSingleton None - ROOT 0,0..0,4'''),

('', None, None, None, {'raw': True}, (pattern,
r'''None'''),
r'''False''',
r'''False''',
r'''MatchSingleton False - ROOT 0,0..0,5'''),

('', None, None, None, {'raw': True}, (pattern,
r'''False'''),
r'''True''',
r'''True''',
r'''MatchSingleton True - ROOT 0,0..0,4'''),

('pattern', None, None, None, {'raw': True}, ('match_case',
r'''case 1: pass'''), (None,
r'''2'''),
r'''case 2: pass''', r'''
match_case - ROOT 0,0..0,12
  .pattern MatchValue - 0,5..0,6
    .value Constant 2 - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('pattern', None, None, None, {'raw': True}, ('match_case', r'''

case 1: pass
'''), (None,
r'''2'''), r'''

case 2: pass
''', r'''
match_case - ROOT 1,0..1,12
  .pattern MatchValue - 1,5..1,6
    .value Constant 2 - 1,5..1,6
  .body[1]
   0] Pass - 1,8..1,12
'''),

('', None, None, 'type', {'raw': True}, ('ExceptHandler',
r'''except ValueError as exc: pass'''), (None,
r'''RuntimeError'''),
r'''except RuntimeError as exc: pass''', r'''
ExceptHandler - ROOT 0,0..0,32
  .type Name 'RuntimeError' Load - 0,7..0,19
  .name 'exc'
  .body[1]
   0] Pass - 0,28..0,32
'''),

('', None, None, 'type', {'raw': True}, ('ExceptHandler', r'''

except ValueError as exc: pass
'''), (None,
r'''RuntimeError'''), r'''

except RuntimeError as exc: pass
''', r'''
ExceptHandler - ROOT 1,0..1,32
  .type Name 'RuntimeError' Load - 1,7..1,19
  .name 'exc'
  .body[1]
   0] Pass - 1,28..1,32
'''),

('handlers[0]', None, None, 'type', {'raw': True}, ('_ExceptHandlers', r'''
except Exception: pass
except Exception: pass
'''), (None,
r'''ValueError'''), r'''
except ValueError: pass
except Exception: pass
''', r'''
_ExceptHandlers - ROOT 0,0..1,22
  .handlers[2]
   0] ExceptHandler - 0,0..0,23
     .type Name 'ValueError' Load - 0,7..0,17
     .body[1]
      0] Pass - 0,19..0,23
   1] ExceptHandler - 1,0..1,22
     .type Name 'Exception' Load - 1,7..1,16
     .body[1]
      0] Pass - 1,18..1,22
'''),

('handlers[0]', None, None, 'type', {'raw': True, 'to': 'handlers[1].type'}, ('_ExceptHandlers', r'''
except Exception: pass
except Exception: pass
'''), (None, r'''
ValueError: _
except RuntimeError
'''), r'''
except ValueError: _
except RuntimeError: pass
''', r'''
_ExceptHandlers - ROOT 0,0..1,25
  .handlers[2]
   0] ExceptHandler - 0,0..0,20
     .type Name 'ValueError' Load - 0,7..0,17
     .body[1]
      0] Expr - 0,19..0,20
        .value Name '_' Load - 0,19..0,20
   1] ExceptHandler - 1,0..1,25
     .type Name 'RuntimeError' Load - 1,7..1,19
     .body[1]
      0] Pass - 1,21..1,25
'''),

('cases[0]', None, None, 'pattern', {'raw': True}, ('_match_cases', r'''
case 1: pass
case 2: pass
'''), (None,
r'''3'''), r'''
case 3: pass
case 2: pass
''', r'''
_match_cases - ROOT 0,0..1,12
  .cases[2]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 3 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..1,12
     .pattern MatchValue - 1,5..1,6
       .value Constant 2 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

('cases[0]', None, None, 'pattern', {'raw': True, 'to': 'cases[1].pattern'}, ('_match_cases', r'''
case 1: pass
case 2: pass
'''), (None, r'''
3: _
case 4
'''), r'''
case 3: _
case 4: pass
''', r'''
_match_cases - ROOT 0,0..1,12
  .cases[2]
   0] match_case - 0,0..0,9
     .pattern MatchValue - 0,5..0,6
       .value Constant 3 - 0,5..0,6
     .body[1]
      0] Expr - 0,8..0,9
        .value Name '_' Load - 0,8..0,9
   1] match_case - 1,0..1,12
     .pattern MatchValue - 1,5..1,6
       .value Constant 4 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

('targets[0]', None, None, None, {'raw': True}, ('_Assign_targets',
r'''a = b = c ='''), (None,
r'''**FIX ME**'''),
r'''**SyntaxError('invalid syntax')**'''),

('targets[0]', None, None, None, {'raw': True, 'to': 'targets[1]'}, ('_Assign_targets',
r'''a = b = c ='''), (None,
r'''x = y '''),
r'''x = y  = c =''', r'''
_Assign_targets - ROOT 0,0..0,12
  .targets[3]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'y' Store - 0,4..0,5
   2] Name 'c' Store - 0,9..0,10
'''),

('', 0, None, None, {'raw': True}, (None,
r'''{a: b}'''), (None,
r'''c: d'''),
r'''{c: d}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'c' Load - 0,1..0,2
  .values[1]
   0] Name 'd' Load - 0,4..0,5
'''),

('', None, None, 'returns', {'raw': True}, (None,
r'''def f() -> int: pass'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete in raw put')**'''),
],

'f-string': [  # ................................................................................

('values[1]', None, None, 'value', {'_ver': 12, 'raw': False}, (None,
r'''f"a{Εаo:}"'''), (None,
r'''99'''),
r'''f"a{99:}"''', r'''
JoinedStr - ROOT 0,0..0,9
  .values[2]
   0] Constant 'a' - 0,2..0,3
   1] FormattedValue - 0,3..0,8
     .value Constant 99 - 0,4..0,6
     .conversion -1
     .format_spec JoinedStr - 0,6..0,7
'''),

('values[1]', None, None, 'value', {'_ver': 12, 'raw': False}, (None,
r'''f"a{Εаo=:}"'''), (None,
r'''99'''),
r'''f"a{99=:}"''', r'''
JoinedStr - ROOT 0,0..0,10
  .values[2]
   0] Constant 'a99=' - 0,2..0,7
   1] FormattedValue - 0,3..0,9
     .value Constant 99 - 0,4..0,6
     .conversion -1
     .format_spec JoinedStr - 0,7..0,8
'''),

('values[1].value', None, None, 'func', {'_ver': 12, 'raw': False}, (None,
r'''f"a{Εаo()=:}"'''), (None,
r'''99'''),
r'''f"a{99()=:}"''', r'''
JoinedStr - ROOT 0,0..0,12
  .values[2]
   0] Constant 'a99()=' - 0,2..0,9
   1] FormattedValue - 0,3..0,11
     .value Call - 0,4..0,8
       .func Constant 99 - 0,4..0,6
     .conversion -1
     .format_spec JoinedStr - 0,9..0,10
'''),
],

't-string': [  # ................................................................................

('values[1]', None, None, 'value', {'_ver': 14, 'raw': False}, (None,
r'''t"a{Εаo:}"'''), (None,
r'''99'''),
r'''t"a{99:}"''', r'''
TemplateStr - ROOT 0,0..0,9
  .values[2]
   0] Constant 'a' - 0,2..0,3
   1] Interpolation - 0,3..0,8
     .value Constant 99 - 0,4..0,6
     .str '99'
     .conversion -1
     .format_spec JoinedStr - 0,6..0,7
'''),

('values[1]', None, None, 'value', {'_ver': 14, 'raw': False}, (None,
r'''t"a{Εаo=:}"'''), (None,
r'''99'''),
r'''t"a{99=:}"''', r'''
TemplateStr - ROOT 0,0..0,10
  .values[2]
   0] Constant 'a99=' - 0,2..0,7
   1] Interpolation - 0,3..0,9
     .value Constant 99 - 0,4..0,6
     .str '99'
     .conversion -1
     .format_spec JoinedStr - 0,7..0,8
'''),

('values[1].value', None, None, 'func', {'_ver': 14, 'raw': False}, (None,
r'''t"a{Εаo()=:}"'''), (None,
r'''99'''),
r'''t"a{99()=:}"''', r'''
TemplateStr - ROOT 0,0..0,12
  .values[2]
   0] Constant 'a99()=' - 0,2..0,9
   1] Interpolation - 0,3..0,11
     .value Call - 0,4..0,8
       .func Constant 99 - 0,4..0,6
     .str '99()'
     .conversion -1
     .format_spec JoinedStr - 0,9..0,10
'''),
],

'coerce_to_expr': [  # ................................................................................

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('Module',
r'''x'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('Module',
r'''(x)'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('Module', r'''
x
y
'''),
r'''**NodeError('expecting expression (standard), got Module, could not coerce, multiple statements')**'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('Module',
r'''x = y'''),
r'''**NodeError('expecting expression (standard), got Module, could not coerce, uncoercable type Assign')**'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('Interactive',
r'''x'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('Interactive',
r'''(x)'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('Interactive',
r'''x; y'''),
r'''**NodeError('expecting expression (standard), got Interactive, could not coerce, multiple statements')**'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('Expression',
r'''x'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('Expression',
r'''(x)'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('Expr',
r'''x'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('Expr',
r'''(x)'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('arg',
r'''x'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('arguments',
r'''#0'''), r'''
i = (#0
)
''',
r'''i = ()''', r'''
Assign - ROOT 0,0..1,1
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..1,1
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('arguments', r'''
*
b
,
c
,
'''), r'''
i = (*
b
,
c
,)
''',
r'''i = (*b, c)''', r'''
Assign - ROOT 0,0..4,2
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..4,2
    .elts[2]
     0] Starred - 0,5..1,1
       .value Name 'b' Load - 1,0..1,1
       .ctx Load
     1] Name 'c' Load - 3,0..3,1
    .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('arg',
r'''x: int'''),
r'''**NodeError('expecting expression (standard), got arg, could not coerce, arg has annotation')**'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('alias',
r'''x'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('alias',
r'''x.y.z'''),
r'''i = x.y.z''', r'''
Assign - ROOT 0,0..0,9
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Attribute - 0,4..0,9
    .value Attribute - 0,4..0,7
      .value Name 'x' Load - 0,4..0,5
      .attr 'y'
      .ctx Load
    .attr 'z'
    .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('alias',
r'''x as y'''),
r'''**NodeError('expecting expression (standard), got alias, could not coerce, alias has asname')**'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('alias',
r'''*'''),
r'''**NodeError("expecting expression (standard), got alias, could not coerce, star '*' alias")**'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('withitem',
r'''x'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('withitem',
r'''(x)'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('withitem',
r'''x as y'''),
r'''**NodeError('expecting expression (standard), got withitem, could not coerce, withitem has optional_vars')**'''),

('', None, None, 'value', {'_src': False, '_ver': 12}, (None,
r'''i = v'''), ('TypeVar',
r'''T'''),
r'''i = T''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'T' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, '_ver': 12}, (None,
r'''i = v'''), ('TypeVar',
r'''T: int'''),
r'''**NodeError('expecting expression (standard), got TypeVar, could not coerce, TypeVar has bound')**'''),

('', None, None, 'value', {'_src': False, '_ver': 13}, (None,
r'''i = v'''), ('TypeVar',
r'''T = int'''),
r'''**NodeError('expecting expression (standard), got TypeVar, could not coerce, TypeVar has default_value')**'''),

('', 0, None, None, {'_src': False, '_ver': 12}, (None,
r'''[v]'''), ('TypeVarTuple',
r'''*T'''),
r'''[*T]''', r'''
List - ROOT 0,0..0,4
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'T' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', None, None, 'value', {'_src': False, '_ver': 13}, (None,
r'''i = v'''), ('TypeVarTuple',
r'''*T = ()'''),
r'''**NodeError('expecting expression (standard), got TypeVarTuple, could not coerce, TypeVarTuple has default_value')**'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchValue',
r'''1'''),
r'''i = 1''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('MatchValue',
r'''(1)'''),
r'''i = 1''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchValue',
r'''a.b'''),
r'''i = a.b''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Attribute - 0,4..0,7
    .value Name 'a' Load - 0,4..0,5
    .attr 'b'
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('MatchValue',
r'''(a.b)'''),
r'''i = a.b''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Attribute - 0,4..0,7
    .value Name 'a' Load - 0,4..0,5
    .attr 'b'
    .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchSingleton',
r'''True'''),
r'''i = True''', r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Constant True - 0,4..0,8
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchSingleton',
r'''False'''),
r'''i = False''', r'''
Assign - ROOT 0,0..0,9
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Constant False - 0,4..0,9
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchSingleton',
r'''None'''),
r'''i = None''', r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Constant None - 0,4..0,8
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('MatchSingleton',
r'''(None)'''),
r'''i = None''', r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Constant None - 0,4..0,8
'''),

('', 0, None, None, {'_src': False}, (None,
r'''[v]'''), ('MatchStar',
r'''*s'''),
r'''[*s]''', r'''
List - ROOT 0,0..0,4
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 's' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchAs',
r'''x'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('MatchAs',
r'''(x)'''),
r'''i = x''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Name 'x' Load - 0,4..0,5
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchAs',
r'''x as y'''),
r'''**NodeError('expecting expression (standard), got MatchAs, could not coerce, MatchAs has pattern')**'''),

('', None, None, 'value', {'_src': False, '_same': False, 'raw': False}, (None,
r'''i = v'''), ('MatchSequence',
r'''x, 1, True, *y'''),
r'''i = (x, 1, True, *y)''',
r'''i = [x, 1, True, *y]''', r'''
Assign - ROOT 0,0..0,20
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,20
    .elts[4]
     0] Name 'x' Load - 0,5..0,6
     1] Constant 1 - 0,8..0,9
     2] Constant True - 0,11..0,15
     3] Starred - 0,17..0,19
       .value Name 'y' Load - 0,18..0,19
       .ctx Load
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, '_same': False}, (None,
r'''i = v'''), ('MatchSequence',
r'''(x, 1, True, *y)'''),
r'''i = (x, 1, True, *y)''',
r'''i = [x, 1, True, *y]''', r'''
Assign - ROOT 0,0..0,20
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,20
    .elts[4]
     0] Name 'x' Load - 0,5..0,6
     1] Constant 1 - 0,8..0,9
     2] Constant True - 0,11..0,15
     3] Starred - 0,17..0,19
       .value Name 'y' Load - 0,18..0,19
       .ctx Load
    .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchSequence',
r'''[x, 1, True, *y]'''),
r'''i = [x, 1, True, *y]''', r'''
Assign - ROOT 0,0..0,20
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value List - 0,4..0,20
    .elts[4]
     0] Name 'x' Load - 0,5..0,6
     1] Constant 1 - 0,8..0,9
     2] Constant True - 0,11..0,15
     3] Starred - 0,17..0,19
       .value Name 'y' Load - 0,18..0,19
       .ctx Load
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, '_same': False}, (None,
r'''i = v'''), ('MatchSequence',
r'''[([x, 1, True, *y],)]'''),
r'''i = [([x, 1, True, *y],)]''',
r'''i = [[[x, 1, True, *y]]]''', r'''
Assign - ROOT 0,0..0,25
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value List - 0,4..0,25
    .elts[1]
     0] Tuple - 0,5..0,24
       .elts[1]
        0] List - 0,6..0,22
          .elts[4]
           0] Name 'x' Load - 0,7..0,8
           1] Constant 1 - 0,10..0,11
           2] Constant True - 0,13..0,17
           3] Starred - 0,19..0,21
             .value Name 'y' Load - 0,20..0,21
             .ctx Load
          .ctx Load
       .ctx Load
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('MatchSequence',
r'''([x, 1, True, *y])'''),
r'''i = [x, 1, True, *y]''', r'''
Assign - ROOT 0,0..0,20
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value List - 0,4..0,20
    .elts[4]
     0] Name 'x' Load - 0,5..0,6
     1] Constant 1 - 0,8..0,9
     2] Constant True - 0,11..0,15
     3] Starred - 0,17..0,19
       .value Name 'y' Load - 0,18..0,19
       .ctx Load
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('MatchSequence',
r'''[x as y]'''),
r'''**NodeError('expecting expression (standard), got MatchSequence, could not coerce, MatchAs has pattern')**'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchMapping',
r'''{1: a, b.c: d, **e}'''),
r'''i = {1: a, b.c: d, **e}''', r'''
Assign - ROOT 0,0..0,23
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Dict - 0,4..0,23
    .keys[3]
     0] Constant 1 - 0,5..0,6
     1] Attribute - 0,11..0,14
       .value Name 'b' Load - 0,11..0,12
       .attr 'c'
       .ctx Load
     2] None
    .values[3]
     0] Name 'a' Load - 0,8..0,9
     1] Name 'd' Load - 0,16..0,17
     2] Name 'e' Load - 0,21..0,22
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('MatchMapping',
r'''({1: a, b.c: d, **e})'''),
r'''i = {1: a, b.c: d, **e}''', r'''
Assign - ROOT 0,0..0,23
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Dict - 0,4..0,23
    .keys[3]
     0] Constant 1 - 0,5..0,6
     1] Attribute - 0,11..0,14
       .value Name 'b' Load - 0,11..0,12
       .attr 'c'
       .ctx Load
     2] None
    .values[3]
     0] Name 'a' Load - 0,8..0,9
     1] Name 'd' Load - 0,16..0,17
     2] Name 'e' Load - 0,21..0,22
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('MatchMapping',
r'''{1: a as b}'''),
r'''**NodeError('expecting expression (standard), got MatchMapping, could not coerce, MatchAs has pattern')**'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('_Assign_targets',
r'''x = y = z ='''),
r'''i = (x, y, z)''', r'''
Assign - ROOT 0,0..0,13
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,13
    .elts[3]
     0] Name 'x' Load - 0,5..0,6
     1] Name 'y' Load - 0,8..0,9
     2] Name 'z' Load - 0,11..0,12
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('_decorator_list', r'''
@x
@y
@z
'''), r'''
i = (x,
y,
z)
''',
r'''i = (x, y, z)''', r'''
Assign - ROOT 0,0..2,2
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..2,2
    .elts[3]
     0] Name 'x' Load - 0,5..0,6
     1] Name 'y' Load - 1,0..1,1
     2] Name 'z' Load - 2,0..2,1
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('_comprehension_ifs',
r'''if x if y if z'''),
r'''i = (x, y, z)''', r'''
Assign - ROOT 0,0..0,13
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,13
    .elts[3]
     0] Name 'x' Load - 0,5..0,6
     1] Name 'y' Load - 0,8..0,9
     2] Name 'z' Load - 0,11..0,12
    .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('_arglikes',
r''''''),
r'''**SyntaxError('expecting expression, got nothing')**'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('_arglikes',
r'''a'''),
r'''i = (a,)''', r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,8
    .elts[1]
     0] Name 'a' Load - 0,5..0,6
    .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('_arglikes',
r'''a, b=c'''),
r'''**NodeError('expecting expression (standard), got _arglikes, could not coerce, _arglikes has a keyword')**'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('_arglikes',
r'''a, *b'''),
r'''i = (a, *b)''', r'''
Assign - ROOT 0,0..0,11
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,11
    .elts[2]
     0] Name 'a' Load - 0,5..0,6
     1] Starred - 0,8..0,10
       .value Name 'b' Load - 0,9..0,10
       .ctx Load
    .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('_withitems',
r''''''),
r'''**SyntaxError('expecting expression, got nothing')**'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('_withitems',
r'''a'''),
r'''i = (a,)''', r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,8
    .elts[1]
     0] Name 'a' Load - 0,5..0,6
    .ctx Load
'''),

('', None, None, 'value', {'_src': False}, (None,
r'''i = v'''), ('_withitems',
r'''a as b'''),
r'''**NodeError('expecting expression (standard), got _withitems, could not coerce, withitem has optional_vars')**'''),

('', None, None, 'value', {'_src': False, 'raw': False}, (None,
r'''i = v'''), ('_withitems',
r'''a, b'''),
r'''i = (a, b)''', r'''
Assign - ROOT 0,0..0,10
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,10
    .elts[2]
     0] Name 'a' Load - 0,5..0,6
     1] Name 'b' Load - 0,8..0,9
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, '_ver': 12, 'raw': False}, (None,
r'''i = v'''), ('_type_params',
r'''T, *U'''),
r'''i = (T, *U)''', r'''
Assign - ROOT 0,0..0,11
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,11
    .elts[2]
     0] Name 'T' Load - 0,5..0,6
     1] Starred - 0,8..0,10
       .value Name 'U' Load - 0,9..0,10
       .ctx Load
    .ctx Load
'''),

('', None, None, 'value', {'_src': False, '_ver': 12}, (None,
r'''i = v'''), ('_type_params',
r'''T, *U, **V'''),
r'''**NodeError('expecting expression (standard), got _type_params, could not coerce, incompatible type ParamSpec')**'''),

('', None, None, 'value', {'_src': False, '_ver': 12}, (None,
r'''i = v'''), ('_type_params',
r'''T: int, *U'''),
r'''**NodeError('expecting expression (standard), got _type_params, could not coerce, type_param has bound')**'''),

('', None, None, 'value', {'_src': False, '_ver': 13}, (None,
r'''i = v'''), ('_type_params',
r'''T = int, *U'''),
r'''**NodeError('expecting expression (standard), got _type_params, could not coerce, type_param has default_value')**'''),
],

'coerce_to__arglike': [  # ................................................................................

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('Module',
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('Module',
r'''(x)'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('Module', r'''
x
y
'''),
r'''**NodeError('expecting expression (arglike), got Module, could not coerce')**'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('Module',
r'''x = y'''),
r'''**NodeError('expecting expression (arglike), got Module, could not coerce')**'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('Interactive',
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('Interactive',
r'''(x)'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('Interactive',
r'''x; y'''),
r'''**NodeError('expecting expression (arglike), got Interactive, could not coerce')**'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('Expression',
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('Expression',
r'''(x)'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('Expr',
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('Expr',
r'''(x)'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('arg',
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('arg',
r'''x: int'''),
r'''**NodeError('expecting expression (arglike), got arg, could not coerce')**'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('alias',
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('alias',
r'''x as y'''),
r'''**NodeError('expecting expression (arglike), got alias, could not coerce')**'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('alias',
r'''*'''),
r'''**NodeError('expecting expression (arglike), got alias, could not coerce')**'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('withitem',
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('withitem',
r'''(x)'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('withitem',
r'''x as y'''),
r'''**NodeError('expecting expression (arglike), got withitem, could not coerce')**'''),

('', 0, None, '_args', {'_src': False, '_ver': 12}, (None,
r'''call(a)'''), ('TypeVar',
r'''T'''),
r'''call(T)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'T' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False, '_ver': 12}, (None,
r'''call(a)'''), ('TypeVar',
r'''T: int'''),
r'''**NodeError('expecting expression (arglike), got TypeVar, could not coerce')**'''),

('', 0, None, '_args', {'_src': False, '_ver': 13}, (None,
r'''call(a)'''), ('TypeVar',
r'''T = int'''),
r'''**NodeError('expecting expression (arglike), got TypeVar, could not coerce')**'''),

('', 0, None, '_args', {'_src': False, '_ver': 12}, (None,
r'''call(a)'''), ('TypeVarTuple',
r'''*T'''),
r'''call(*T)''', r'''
Call - ROOT 0,0..0,8
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,7
     .value Name 'T' Load - 0,6..0,7
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False, '_ver': 13}, (None,
r'''call(a)'''), ('TypeVarTuple',
r'''*T = ()'''),
r'''**NodeError('expecting expression (arglike), got TypeVarTuple, could not coerce')**'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchValue',
r'''1'''),
r'''call(1)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Constant 1 - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('MatchValue',
r'''(1)'''),
r'''call(1)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Constant 1 - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchValue',
r'''a.b'''),
r'''call(a.b)''', r'''
Call - ROOT 0,0..0,9
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Attribute - 0,5..0,8
     .value Name 'a' Load - 0,5..0,6
     .attr 'b'
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('MatchValue',
r'''(a.b)'''),
r'''call(a.b)''', r'''
Call - ROOT 0,0..0,9
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Attribute - 0,5..0,8
     .value Name 'a' Load - 0,5..0,6
     .attr 'b'
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchSingleton',
r'''True'''),
r'''call(True)''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Constant True - 0,5..0,9
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchSingleton',
r'''False'''),
r'''call(False)''', r'''
Call - ROOT 0,0..0,11
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Constant False - 0,5..0,10
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchSingleton',
r'''None'''),
r'''call(None)''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Constant None - 0,5..0,9
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('MatchSingleton',
r'''(None)'''),
r'''call(None)''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Constant None - 0,5..0,9
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchStar',
r'''*s'''),
r'''call(*s)''', r'''
Call - ROOT 0,0..0,8
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,7
     .value Name 's' Load - 0,6..0,7
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchAs',
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('MatchAs',
r'''(x)'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchAs',
r'''x as y'''),
r'''**NodeError('expecting expression (arglike), got MatchAs, could not coerce')**'''),

('', 0, None, '_args', {'_src': False, '_same': False, 'raw': False}, (None,
r'''call(a)'''), ('MatchSequence',
r'''x, 1, True, *y'''),
r'''call((x, 1, True, *y))''',
r'''call([x, 1, True, *y])''', r'''
Call - ROOT 0,0..0,22
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Tuple - 0,5..0,21
     .elts[4]
      0] Name 'x' Load - 0,6..0,7
      1] Constant 1 - 0,9..0,10
      2] Constant True - 0,12..0,16
      3] Starred - 0,18..0,20
        .value Name 'y' Load - 0,19..0,20
        .ctx Load
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False, '_same': False}, (None,
r'''call(a)'''), ('MatchSequence',
r'''(x, 1, True, *y)'''),
r'''call((x, 1, True, *y))''',
r'''call([x, 1, True, *y])''', r'''
Call - ROOT 0,0..0,22
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Tuple - 0,5..0,21
     .elts[4]
      0] Name 'x' Load - 0,6..0,7
      1] Constant 1 - 0,9..0,10
      2] Constant True - 0,12..0,16
      3] Starred - 0,18..0,20
        .value Name 'y' Load - 0,19..0,20
        .ctx Load
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchSequence',
r'''[x, 1, True, *y]'''),
r'''call([x, 1, True, *y])''', r'''
Call - ROOT 0,0..0,22
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] List - 0,5..0,21
     .elts[4]
      0] Name 'x' Load - 0,6..0,7
      1] Constant 1 - 0,9..0,10
      2] Constant True - 0,12..0,16
      3] Starred - 0,18..0,20
        .value Name 'y' Load - 0,19..0,20
        .ctx Load
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False, '_same': False}, (None,
r'''call(a)'''), ('MatchSequence',
r'''[([x, 1, True, *y],)]'''),
r'''call([([x, 1, True, *y],)])''',
r'''call([[[x, 1, True, *y]]])''', r'''
Call - ROOT 0,0..0,27
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] List - 0,5..0,26
     .elts[1]
      0] Tuple - 0,6..0,25
        .elts[1]
         0] List - 0,7..0,23
           .elts[4]
            0] Name 'x' Load - 0,8..0,9
            1] Constant 1 - 0,11..0,12
            2] Constant True - 0,14..0,18
            3] Starred - 0,20..0,22
              .value Name 'y' Load - 0,21..0,22
              .ctx Load
           .ctx Load
        .ctx Load
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('MatchSequence',
r'''([x, 1, True, *y])'''),
r'''call([x, 1, True, *y])''', r'''
Call - ROOT 0,0..0,22
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] List - 0,5..0,21
     .elts[4]
      0] Name 'x' Load - 0,6..0,7
      1] Constant 1 - 0,9..0,10
      2] Constant True - 0,12..0,16
      3] Starred - 0,18..0,20
        .value Name 'y' Load - 0,19..0,20
        .ctx Load
     .ctx Load
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('MatchMapping',
r'''{1: a, b.c: d, **e}'''),
r'''call({1: a, b.c: d, **e})''', r'''
Call - ROOT 0,0..0,25
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Dict - 0,5..0,24
     .keys[3]
      0] Constant 1 - 0,6..0,7
      1] Attribute - 0,12..0,15
        .value Name 'b' Load - 0,12..0,13
        .attr 'c'
        .ctx Load
      2] None
     .values[3]
      0] Name 'a' Load - 0,9..0,10
      1] Name 'd' Load - 0,17..0,18
      2] Name 'e' Load - 0,22..0,23
'''),

('', 0, None, '_args', {'_src': False, 'raw': False}, (None,
r'''call(a)'''), ('MatchMapping',
r'''({1: a, b.c: d, **e})'''),
r'''call({1: a, b.c: d, **e})''', r'''
Call - ROOT 0,0..0,25
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Dict - 0,5..0,24
     .keys[3]
      0] Constant 1 - 0,6..0,7
      1] Attribute - 0,12..0,15
        .value Name 'b' Load - 0,12..0,13
        .attr 'c'
        .ctx Load
      2] None
     .values[3]
      0] Name 'a' Load - 0,9..0,10
      1] Name 'd' Load - 0,17..0,18
      2] Name 'e' Load - 0,22..0,23
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('keyword',
r'''x=y'''),
r'''call(x=y)''', r'''
Call - ROOT 0,0..0,9
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,8
     .arg 'x'
     .value Name 'y' Load - 0,7..0,8
'''),
],

'coerce_to_arguments': [  # ................................................................................

('', None, None, 'args', {'_src': False}, (None,
r'''def f(): pass'''), ('arg',
r'''x'''),
r'''def f(x): pass''', r'''
FunctionDef - ROOT 0,0..0,14
  .name 'f'
  .args arguments - 0,6..0,7
    .args[1]
     0] arg - 0,6..0,7
       .arg 'x'
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', None, None, 'args', {'_src': False}, (None,
r'''def f(): pass'''), ('arg',
r'''x: int'''),
r'''def f(x: int): pass''', r'''
FunctionDef - ROOT 0,0..0,19
  .name 'f'
  .args arguments - 0,6..0,12
    .args[1]
     0] arg - 0,6..0,12
       .arg 'x'
       .annotation Name 'int' Load - 0,9..0,12
  .body[1]
   0] Pass - 0,15..0,19
'''),

('', None, None, 'args', {'_src': False}, (None,
r'''lambda: None'''), ('arg',
r'''x'''),
r'''lambda x: None''', r'''
Lambda - ROOT 0,0..0,14
  .args arguments - 0,7..0,8
    .args[1]
     0] arg - 0,7..0,8
       .arg 'x'
  .body Constant None - 0,10..0,14
'''),

('', None, None, 'args', {'_src': False}, (None,
r'''lambda: None'''), ('arg',
r'''x: int'''),
r'''**NodeError('expecting lambda arguments, got arg, could not coerce')**'''),
],

'coerce_to_arg': [  # ................................................................................

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('Module',
r'''x'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False, 'raw': False}, ('arguments',
r'''a, b, c'''), ('Module',
r'''(x)'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('Module', r'''
x
y
'''),
r'''**NodeError('expecting arg, got Module, could not coerce')**'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('Module',
r'''x = y'''),
r'''**NodeError('expecting arg, got Module, could not coerce')**'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('Interactive',
r'''x'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False, 'raw': False}, ('arguments',
r'''a, b, c'''), ('Interactive',
r'''(x)'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('Interactive',
r'''x; y'''),
r'''**NodeError('expecting arg, got Interactive, could not coerce')**'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('Expression',
r'''x'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False, 'raw': False}, ('arguments',
r'''a, b, c'''), ('Expression',
r'''(x)'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('Expr',
r'''x'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False, 'raw': False}, ('arguments',
r'''a, b, c'''), ('Expr',
r'''(x)'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('alias',
r'''x'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('alias',
r'''x as y'''),
r'''**NodeError('expecting arg, got alias, could not coerce')**'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('alias',
r'''*'''),
r'''**NodeError('expecting arg, got alias, could not coerce')**'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('withitem',
r'''x'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False, 'raw': False}, ('arguments',
r'''a, b, c'''), ('withitem',
r'''(x)'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('withitem',
r'''x as y'''),
r'''**NodeError('expecting arg, got withitem, could not coerce')**'''),

('', 1, None, 'args', {'_src': False, '_ver': 12}, ('arguments',
r'''a, b, c'''), ('TypeVar',
r'''T'''),
r'''a, T, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'T'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False, '_ver': 12}, ('arguments',
r'''a, b, c'''), ('TypeVar',
r'''T: int'''),
r'''**NodeError('expecting arg, got TypeVar, could not coerce')**'''),

('', 1, None, 'args', {'_src': False, '_ver': 13}, ('arguments',
r'''a, b, c'''), ('TypeVar',
r'''T = int'''),
r'''**NodeError('expecting arg, got TypeVar, could not coerce')**'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('MatchValue',
r'''a.b'''),
r'''**NodeError('expecting arg, got MatchValue, could not coerce')**'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('MatchValue',
r'''(a.b)'''),
r'''**NodeError('expecting arg, got MatchValue, could not coerce')**'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('MatchAs',
r'''x'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('MatchAs',
r'''x'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False, 'raw': False}, ('arguments',
r'''a, b, c'''), ('MatchAs',
r'''(x)'''),
r'''a, x, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'x'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, None, 'args', {'_src': False}, ('arguments',
r'''a, b, c'''), ('MatchAs',
r'''x as y'''),
r'''**NodeError('expecting arg, got MatchAs, could not coerce')**'''),
],

'coerce_to_alias': [  # ................................................................................

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('Module',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False, 'raw': False}, (None,
r'''import a'''), ('Module',
r'''(x)'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('Module', r'''
x
y
'''),
r'''**NodeError('expecting alias, got Module, could not coerce')**'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('Module',
r'''x = y'''),
r'''**NodeError('expecting alias, got Module, could not coerce')**'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('Interactive',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False, 'raw': False}, (None,
r'''import a'''), ('Interactive',
r'''(x)'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('Interactive',
r'''x; y'''),
r'''**NodeError('expecting alias, got Interactive, could not coerce')**'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('Expression',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False, 'raw': False}, (None,
r'''import a'''), ('Expression',
r'''(x)'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('Expr',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False, 'raw': False}, (None,
r'''import a'''), ('Expr',
r'''(x)'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('arg',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('arg',
r'''x: int'''),
r'''**NodeError('expecting alias, got arg, could not coerce')**'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('withitem',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False, 'raw': False}, (None,
r'''import a'''), ('withitem',
r'''(x)'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('withitem',
r'''x as y'''),
r'''**NodeError('expecting alias, got withitem, could not coerce')**'''),

('', 0, None, 'names', {'_src': False, '_ver': 12}, (None,
r'''import a'''), ('TypeVar',
r'''T'''),
r'''import T''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'T'
'''),

('', 0, None, 'names', {'_src': False, '_ver': 12}, (None,
r'''import a'''), ('TypeVar',
r'''T: int'''),
r'''**NodeError('expecting alias, got TypeVar, could not coerce')**'''),

('', 0, None, 'names', {'_src': False, '_ver': 13}, (None,
r'''import a'''), ('TypeVar',
r'''T = int'''),
r'''**NodeError('expecting alias, got TypeVar, could not coerce')**'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('MatchValue',
r'''a.b'''),
r'''import a.b''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'a.b'
'''),

('', 0, None, 'names', {'_src': False, 'raw': False}, (None,
r'''import a'''), ('MatchValue',
r'''(a.b)'''),
r'''import a.b''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'a.b'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('MatchAs',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('MatchAs',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False, 'raw': False}, (None,
r'''import a'''), ('MatchAs',
r'''(x)'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, 'names', {'_src': False}, (None,
r'''import a'''), ('MatchAs',
r'''x as y'''),
r'''**NodeError('expecting alias, got MatchAs, could not coerce')**'''),

('', 0, None, None, {'_src': False}, (None,
r'''import a'''), ('Name',
r'''x'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, None, {'_src': False}, (None,
r'''import a'''), ('Attribute',
r'''x.y'''),
r'''import x.y''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'x.y'
'''),

('', 0, None, None, {'_src': False, 'raw': False}, (None,
r'''import a'''), ('Name',
r'''(x)'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, None, None, {'_src': False, 'raw': False}, (None,
r'''import a'''), ('Attribute',
r'''(x).y'''),
r'''import x.y''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'x.y'
'''),

('', 0, None, None, {'_src': False, 'raw': False}, (None,
r'''import a'''), ('Attribute',
r'''((x).y)'''),
r'''import x.y''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'x.y'
'''),

('', 0, None, None, {'_src': False}, (None,
r'''from _ import a'''), ('Name',
r'''x'''),
r'''from _ import x''', r'''
ImportFrom - ROOT 0,0..0,15
  .module '_'
  .names[1]
   0] alias - 0,14..0,15
     .name 'x'
  .level 0
'''),

('', 0, None, None, {'_src': False}, (None,
r'''from _ import a'''), ('Attribute',
r'''x.y'''),
r'''**NodeError('expecting alias, got Attribute, could not coerce')**'''),

('', 0, None, None, {'_src': False}, (None,
r'''from _ import a'''), ('Attribute',
r'''x.y'''),
r'''**NodeError('expecting alias, got Attribute, could not coerce')**'''),
],

'coerce_to_withitem': [  # ................................................................................

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('Module',
r'''x'''),
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('Module',
r'''(x)'''),
r'''with (x): pass''',
r'''with x: pass''', r'''
With - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Name 'x' Load - 0,6..0,7
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('Module', r'''
x
y
'''),
r'''**NodeError('expecting withitem, got Module, could not coerce')**'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('Module',
r'''x = y'''),
r'''**NodeError('expecting withitem, got Module, could not coerce')**'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('Interactive',
r'''x'''),
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('Interactive',
r'''(x)'''),
r'''with (x): pass''',
r'''with x: pass''', r'''
With - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Name 'x' Load - 0,6..0,7
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('Interactive',
r'''x; y'''),
r'''**NodeError('expecting withitem, got Interactive, could not coerce')**'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('Expression',
r'''x'''),
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('Expression',
r'''(x)'''),
r'''with (x): pass''',
r'''with x: pass''', r'''
With - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Name 'x' Load - 0,6..0,7
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('Expr',
r'''x'''),
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('Expr',
r'''(x)'''),
r'''with (x): pass''',
r'''with x: pass''', r'''
With - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Name 'x' Load - 0,6..0,7
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('arg',
r'''x'''),
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('arg',
r'''x: int'''),
r'''**NodeError('expecting withitem, got arg, could not coerce')**'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('alias',
r'''x'''),
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('alias',
r'''x as y'''),
r'''**NodeError('expecting withitem, got alias, could not coerce')**'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('alias',
r'''*'''),
r'''**NodeError('expecting withitem, got alias, could not coerce')**'''),

('', 0, None, 'items', {'_src': False, '_ver': 12}, (None,
r'''with a: pass'''), ('TypeVar',
r'''T'''),
r'''with T: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'T' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False, '_ver': 12}, (None,
r'''with a: pass'''), ('TypeVar',
r'''T: int'''),
r'''**NodeError('expecting withitem, got TypeVar, could not coerce')**'''),

('', 0, None, 'items', {'_src': False, '_ver': 13}, (None,
r'''with a: pass'''), ('TypeVar',
r'''T = int'''),
r'''**NodeError('expecting withitem, got TypeVar, could not coerce')**'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchValue',
r'''1'''),
r'''with 1: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Constant 1 - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('MatchValue',
r'''(1)'''),
r'''with (1): pass''',
r'''with 1: pass''', r'''
With - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Constant 1 - 0,6..0,7
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchValue',
r'''a.b'''),
r'''with a.b: pass''', r'''
With - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Attribute - 0,5..0,8
       .value Name 'a' Load - 0,5..0,6
       .attr 'b'
       .ctx Load
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('MatchValue',
r'''(a.b)'''),
r'''with (a.b): pass''',
r'''with a.b: pass''', r'''
With - ROOT 0,0..0,16
  .items[1]
   0] withitem - 0,5..0,10
     .context_expr Attribute - 0,6..0,9
       .value Name 'a' Load - 0,6..0,7
       .attr 'b'
       .ctx Load
  .body[1]
   0] Pass - 0,12..0,16
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchSingleton',
r'''True'''),
r'''with True: pass''', r'''
With - ROOT 0,0..0,15
  .items[1]
   0] withitem - 0,5..0,9
     .context_expr Constant True - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchSingleton',
r'''False'''),
r'''with False: pass''', r'''
With - ROOT 0,0..0,16
  .items[1]
   0] withitem - 0,5..0,10
     .context_expr Constant False - 0,5..0,10
  .body[1]
   0] Pass - 0,12..0,16
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchSingleton',
r'''None'''),
r'''with None: pass''', r'''
With - ROOT 0,0..0,15
  .items[1]
   0] withitem - 0,5..0,9
     .context_expr Constant None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('MatchSingleton',
r'''(None)'''),
r'''with (None): pass''',
r'''with None: pass''', r'''
With - ROOT 0,0..0,17
  .items[1]
   0] withitem - 0,5..0,11
     .context_expr Constant None - 0,6..0,10
  .body[1]
   0] Pass - 0,13..0,17
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchAs',
r'''x'''),
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('MatchAs',
r'''(x)'''),
r'''with (x): pass''',
r'''with x: pass''', r'''
With - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Name 'x' Load - 0,6..0,7
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchAs',
r'''x as y'''),
r'''**NodeError('expecting withitem, got MatchAs, could not coerce')**'''),

('', 0, None, 'items', {'_src': False, '_same': False, 'raw': False}, (None,
r'''with a: pass'''), ('MatchSequence',
r'''x, 1, True, *y'''),
r'''with ((x, 1, True, *y)): pass''',
r'''with [x, 1, True, *y]: pass''', r'''
With - ROOT 0,0..0,29
  .items[1]
   0] withitem - 0,5..0,23
     .context_expr Tuple - 0,6..0,22
       .elts[4]
        0] Name 'x' Load - 0,7..0,8
        1] Constant 1 - 0,10..0,11
        2] Constant True - 0,13..0,17
        3] Starred - 0,19..0,21
          .value Name 'y' Load - 0,20..0,21
          .ctx Load
       .ctx Load
  .body[1]
   0] Pass - 0,25..0,29
'''),

('', 0, None, 'items', {'_src': False, '_same': False, 'raw': False}, (None,
r'''with a: pass'''), ('MatchSequence',
r'''(x, 1, True, *y)'''),
r'''with ((x, 1, True, *y)): pass''',
r'''with [x, 1, True, *y]: pass''', r'''
With - ROOT 0,0..0,29
  .items[1]
   0] withitem - 0,5..0,23
     .context_expr Tuple - 0,6..0,22
       .elts[4]
        0] Name 'x' Load - 0,7..0,8
        1] Constant 1 - 0,10..0,11
        2] Constant True - 0,13..0,17
        3] Starred - 0,19..0,21
          .value Name 'y' Load - 0,20..0,21
          .ctx Load
       .ctx Load
  .body[1]
   0] Pass - 0,25..0,29
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchSequence',
r'''[x, 1, True, *y]'''),
r'''with [x, 1, True, *y]: pass''', r'''
With - ROOT 0,0..0,27
  .items[1]
   0] withitem - 0,5..0,21
     .context_expr List - 0,5..0,21
       .elts[4]
        0] Name 'x' Load - 0,6..0,7
        1] Constant 1 - 0,9..0,10
        2] Constant True - 0,12..0,16
        3] Starred - 0,18..0,20
          .value Name 'y' Load - 0,19..0,20
          .ctx Load
       .ctx Load
  .body[1]
   0] Pass - 0,23..0,27
'''),

('', 0, None, 'items', {'_src': False, '_same': False}, (None,
r'''with a: pass'''), ('MatchSequence',
r'''[([x, 1, True, *y],)]'''),
r'''with [([x, 1, True, *y],)]: pass''',
r'''with [[[x, 1, True, *y]]]: pass''', r'''
With - ROOT 0,0..0,32
  .items[1]
   0] withitem - 0,5..0,26
     .context_expr List - 0,5..0,26
       .elts[1]
        0] Tuple - 0,6..0,25
          .elts[1]
           0] List - 0,7..0,23
             .elts[4]
              0] Name 'x' Load - 0,8..0,9
              1] Constant 1 - 0,11..0,12
              2] Constant True - 0,14..0,18
              3] Starred - 0,20..0,22
                .value Name 'y' Load - 0,21..0,22
                .ctx Load
             .ctx Load
          .ctx Load
       .ctx Load
  .body[1]
   0] Pass - 0,28..0,32
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('MatchSequence',
r'''([x, 1, True, *y])'''),
r'''with ([x, 1, True, *y]): pass''',
r'''with [x, 1, True, *y]: pass''', r'''
With - ROOT 0,0..0,29
  .items[1]
   0] withitem - 0,5..0,23
     .context_expr List - 0,6..0,22
       .elts[4]
        0] Name 'x' Load - 0,7..0,8
        1] Constant 1 - 0,10..0,11
        2] Constant True - 0,13..0,17
        3] Starred - 0,19..0,21
          .value Name 'y' Load - 0,20..0,21
          .ctx Load
       .ctx Load
  .body[1]
   0] Pass - 0,25..0,29
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a: pass'''), ('MatchMapping',
r'''{1: a, b.c: d, **e}'''),
r'''with {1: a, b.c: d, **e}: pass''', r'''
With - ROOT 0,0..0,30
  .items[1]
   0] withitem - 0,5..0,24
     .context_expr Dict - 0,5..0,24
       .keys[3]
        0] Constant 1 - 0,6..0,7
        1] Attribute - 0,12..0,15
          .value Name 'b' Load - 0,12..0,13
          .attr 'c'
          .ctx Load
        2] None
       .values[3]
        0] Name 'a' Load - 0,9..0,10
        1] Name 'd' Load - 0,17..0,18
        2] Name 'e' Load - 0,22..0,23
  .body[1]
   0] Pass - 0,26..0,30
'''),

('', 0, None, 'items', {'_src': False, 'raw': False}, (None,
r'''with a: pass'''), ('MatchMapping',
r'''({1: a, b.c: d, **e})'''),
r'''with ({1: a, b.c: d, **e}): pass''',
r'''with {1: a, b.c: d, **e}: pass''', r'''
With - ROOT 0,0..0,32
  .items[1]
   0] withitem - 0,5..0,26
     .context_expr Dict - 0,6..0,25
       .keys[3]
        0] Constant 1 - 0,7..0,8
        1] Attribute - 0,13..0,16
          .value Name 'b' Load - 0,13..0,14
          .attr 'c'
          .ctx Load
        2] None
       .values[3]
        0] Name 'a' Load - 0,10..0,11
        1] Name 'd' Load - 0,18..0,19
        2] Name 'e' Load - 0,23..0,24
  .body[1]
   0] Pass - 0,28..0,32
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a as b: pass'''), ('Name',
r'''x'''),
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a as b: pass'''), ('Attribute',
r'''x.y'''),
r'''with x.y: pass''', r'''
With - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Attribute - 0,5..0,8
       .value Name 'x' Load - 0,5..0,6
       .attr 'y'
       .ctx Load
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a as b: pass'''), ('Slice',
r'''x:y:z'''),
r'''**NodeError('expecting withitem, got Slice, could not coerce')**'''),

('', 0, None, 'items', {'_src': False}, (None,
r'''with a as b: pass'''), ('Slice',
r'''x:y:z'''),
r'''**NodeError('expecting withitem, got Slice, could not coerce')**'''),
],

'coerce_to_type_param': [  # ................................................................................

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Module',
r'''x'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Module',
r'''(x)'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Module', r'''
x
y
'''),
r'''**NodeError('expecting type_param, got Module, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Module',
r'''x = y'''),
r'''**NodeError('expecting type_param, got Module, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Interactive',
r'''x'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Interactive',
r'''(x)'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Interactive',
r'''x; y'''),
r'''**NodeError('expecting type_param, got Interactive, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Expression',
r'''x'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Expression',
r'''(x)'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Expr',
r'''x'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Expr',
r'''(x)'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('arg',
r'''x'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('arg',
r'''x: int'''),
r'''**NodeError('expecting type_param, got arg, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('alias',
r'''x'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('alias',
r'''x as y'''),
r'''**NodeError('expecting type_param, got alias, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('alias',
r'''*'''),
r'''**NodeError('expecting type_param, got alias, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('withitem',
r'''x'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('withitem',
r'''(x)'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('withitem',
r'''x as y'''),
r'''**NodeError('expecting type_param, got withitem, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchValue',
r'''1'''),
r'''**NodeError('expecting type_param, got MatchValue, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchValue',
r'''(1)'''),
r'''**NodeError('expecting type_param, got MatchValue, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchValue',
r'''a.b'''),
r'''**NodeError('expecting type_param, got MatchValue, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchValue',
r'''(a.b)'''),
r'''**NodeError('expecting type_param, got MatchValue, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchSingleton',
r'''True'''),
r'''**NodeError('expecting type_param, got MatchSingleton, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchSingleton',
r'''False'''),
r'''**NodeError('expecting type_param, got MatchSingleton, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchSingleton',
r'''None'''),
r'''**NodeError('expecting type_param, got MatchSingleton, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchSingleton',
r'''(None)'''),
r'''**NodeError('expecting type_param, got MatchSingleton, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchStar',
r'''*s'''),
r'''type t[*s] = ...''', r'''
TypeAlias - ROOT 0,0..0,16
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVarTuple - 0,7..0,9
     .name 's'
  .value Constant Ellipsis - 0,13..0,16
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchAs',
r'''x'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchAs',
r'''(x)'''),
r'''type t[x] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'x'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, None, 'type_params', {'_src': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('MatchAs',
r'''x as y'''),
r'''**NodeError('expecting type_param, got MatchAs, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_same': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Starred',
r'''*a.b'''),
r'''**NodeError('expecting type_param, got Starred, could not coerce')**'''),

('', 0, None, 'type_params', {'_src': False, '_same': False, 'raw': False, '_ver': 12}, (None,
r'''type t[T] = ...'''), ('Starred',
r'''*(a)'''),
r'''type t[*a] = ...''', r'''
TypeAlias - ROOT 0,0..0,16
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVarTuple - 0,7..0,9
     .name 'a'
  .value Constant Ellipsis - 0,13..0,16
'''),
],

'virtual_field__all': [  # ................................................................................

('', 1, None, '_all', {}, ('Dict',
r'''{1: a, 2: b, 3: c}'''),
r'''**DEL**''',
r'''{1: a, 3: c}''', r'''
Dict - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 3 - 0,7..0,8
  .values[2]
   0] Name 'a' Load - 0,4..0,5
   1] Name 'c' Load - 0,10..0,11
'''),

('', 1, None, '_all', {}, ('MatchMapping',
r'''{1: a, 2: b, 3: c}'''),
r'''**DEL**''',
r'''{1: a, 3: c}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 3 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'c'
'''),

('', 1, None, '_all', {'_verify_get': False}, ('Compare',
r'''a < b > c'''),
r'''**DEL**''',
r'''a > c''', r'''
Compare - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Gt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 0,4..0,5
'''),

('', 1, None, '_all', {'_verify_get': False, 'op_side': 'right'}, ('Compare',
r'''a < b > c'''),
r'''**DEL**''',
r'''a < c''', r'''
Compare - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 0,4..0,5
'''),
],

'virtual_field__body': [  # ................................................................................

('', 0, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''x''', r'''
"""doc"""
x
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'x' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, None, '_body', {'_verify': False, 'raw': False}, ('Interactive',
r'''"""non-doc"""; a; b'''),
r'''x''', r'''
x
a; b
''', r'''
Interactive - ROOT 0,0..1,4
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'x' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 1,3..1,4
     .value Name 'b' Load - 1,3..1,4
'''),

('', 0, None, '_body', {}, ('FunctionDef', r'''
def f():
    """doc"""
    a
    b
'''),
r'''x''', r'''
def f():
    """doc"""
    x
    b
''', r'''
FunctionDef - ROOT 0,0..3,5
  .name 'f'
  .body[3]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'x' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('AsyncFunctionDef', r'''
async def f():
    """doc"""
    a
    b
'''),
r'''x''', r'''
async def f():
    """doc"""
    x
    b
''', r'''
AsyncFunctionDef - ROOT 0,0..3,5
  .name 'f'
  .body[3]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'x' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('ClassDef', r'''
class cls:
    """doc"""
    a
    b
'''),
r'''x''', r'''
class cls:
    """doc"""
    x
    b
''', r'''
ClassDef - ROOT 0,0..3,5
  .name 'cls'
  .body[3]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'x' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('For', r'''
for _ in _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
for _ in _:
    x
    a
    b
''', r'''
For - ROOT 0,0..3,5
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('AsyncFor', r'''
async for _ in _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
async for _ in _:
    x
    a
    b
''', r'''
AsyncFor - ROOT 0,0..3,5
  .target Name '_' Store - 0,10..0,11
  .iter Name '_' Load - 0,15..0,16
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('While', r'''
while _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
while _:
    x
    a
    b
''', r'''
While - ROOT 0,0..3,5
  .test Name '_' Load - 0,6..0,7
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('If', r'''
if _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
if _:
    x
    a
    b
''', r'''
If - ROOT 0,0..3,5
  .test Name '_' Load - 0,3..0,4
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('With', r'''
with _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
with _:
    x
    a
    b
''', r'''
With - ROOT 0,0..3,5
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name '_' Load - 0,5..0,6
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('AsyncWith', r'''
async with _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
async with _:
    x
    a
    b
''', r'''
AsyncWith - ROOT 0,0..3,5
  .items[1]
   0] withitem - 0,11..0,12
     .context_expr Name '_' Load - 0,11..0,12
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('Try', r'''
try:
    """non-doc"""
    a
    b
except: pass
'''),
r'''x''', r'''
try:
    x
    a
    b
except: pass
''', r'''
Try - ROOT 0,0..4,12
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
  .handlers[1]
   0] ExceptHandler - 4,0..4,12
     .body[1]
      0] Pass - 4,8..4,12
'''),

('', 0, None, '_body', {'_ver': 11}, ('TryStar', r'''
try:
    """non-doc"""
    a
    b
except* Exception: pass
'''),
r'''x''', r'''
try:
    x
    a
    b
except* Exception: pass
''', r'''
TryStar - ROOT 0,0..4,23
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
  .handlers[1]
   0] ExceptHandler - 4,0..4,23
     .type Name 'Exception' Load - 4,8..4,17
     .body[1]
      0] Pass - 4,19..4,23
'''),

('', 0, None, '_body', {}, ('ExceptHandler', r'''
except:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
except:
    x
    a
    b
''', r'''
ExceptHandler - ROOT 0,0..3,5
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 0, None, '_body', {}, ('match_case', r'''
case _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
case _:
    x
    a
    b
''', r'''
match_case - ROOT 0,0..3,5
  .pattern MatchAs - 0,5..0,6
  .body[3]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
   2] Expr - 3,4..3,5
     .value Name 'b' Load - 3,4..3,5
'''),

('', 1, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''x''', r'''
"""doc"""
a
x
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'x' Load - 2,0..2,1
'''),

('', 2, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''**IndexError('index out of range')**''',
r'''**IndexError('index out of range')**'''),

('', -1, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''x''', r'''
"""doc"""
a
x
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'x' Load - 2,0..2,1
'''),

('', -2, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''x''', r'''
"""doc"""
x
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'x' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', -3, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''x''',
r'''**IndexError('index out of range')**'''),
],

'raw_virtual_fields': [  # ................................................................................

('', 1, None, '_all', {'raw': True, 'to': 'values[-1]'}, ('Dict',
r'''{1: a, 2: b, 3: c}'''), ('Dict',
r'''4: x'''),
r'''{1: a, 4: x}''', r'''
Dict - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 4 - 0,7..0,8
  .values[2]
   0] Name 'a' Load - 0,4..0,5
   1] Name 'x' Load - 0,10..0,11
'''),

('', 1, None, '_all', {'raw': True, 'to': 'patterns[-1]'}, ('MatchMapping',
r'''{1: a, 2: b, 3: c}'''), ('MatchMapping',
r'''4: x'''),
r'''{1: a, 4: x}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 4 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'x'
'''),

('', 1, None, '_all', {'raw': True}, ('MatchMapping',
r'''{1: a, 2: b}'''), ('MatchMapping',
r'''**x'''),
r'''{1: a, **x}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'x'
'''),

('', 1, None, '_all', {'raw': True}, ('MatchMapping',
r'''{1: a, **c}'''), ('MatchMapping',
r'''2: b'''),
r'''{1: a, 2: b}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'b'
'''),

('patterns[0]', 1, None, '_all', {'raw': True, 'to': 'patterns[1]'}, ('MatchSequence',
r'''[{1: a, **b}, c]'''), (None,
r'''3: c}, d'''),
r'''[{1: a, 3: c}, d]''', r'''
MatchSequence - ROOT 0,0..0,17
  .patterns[2]
   0] MatchMapping - 0,1..0,13
     .keys[2]
      0] Constant 1 - 0,2..0,3
      1] Constant 3 - 0,8..0,9
     .patterns[2]
      0] MatchAs - 0,5..0,6
        .name 'a'
      1] MatchAs - 0,11..0,12
        .name 'c'
   1] MatchAs - 0,15..0,16
     .name 'd'
'''),

('', 1, None, '_all', {'raw': True, 'to': 'comparators[-1]'}, ('Compare',
r'''a < b > c'''), ('Compare',
r'''x'''),
r'''a < x''', r'''
Compare - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'x' Load - 0,4..0,5
'''),

('', 0, None, '_body', {'raw': True, 'to': 'body[-1]'}, ('Module', r'''
"""doc"""
a
b
'''),
r'''x''', r'''
"""doc"""
x
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'x' Load - 1,0..1,1
'''),

('', 0, None, '_body', {'raw': True, 'to': 'body[-1]'}, ('Interactive',
r'''"""non-doc"""; a; b'''),
r'''x''',
r'''x''', r'''
Interactive - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'x' Load - 0,0..0,1
'''),

('', 0, None, '_body', {'raw': True, 'to': 'body[-1]'}, ('FunctionDef', r'''
def f():
    """doc"""
    a
    b
'''),
r'''x''', r'''
def f():
    """doc"""
    x
''', r'''
FunctionDef - ROOT 0,0..2,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'x' Load - 2,4..2,5
'''),

('', 0, None, '_body', {'raw': True, 'to': 'body[-1]'}, ('AsyncFunctionDef', r'''
async def f():
    """doc"""
    a
    b
'''),
r'''x''', r'''
async def f():
    """doc"""
    x
''', r'''
AsyncFunctionDef - ROOT 0,0..2,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'x' Load - 2,4..2,5
'''),

('', 0, None, '_body', {'raw': True, 'to': 'body[-1]'}, ('ClassDef', r'''
class cls:
    """doc"""
    a
    b
'''),
r'''x''', r'''
class cls:
    """doc"""
    x
''', r'''
ClassDef - ROOT 0,0..2,5
  .name 'cls'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'x' Load - 2,4..2,5
'''),

('', 0, None, '_body', {'raw': True, 'to': 'body[-1]'}, ('For', r'''
for _ in _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
for _ in _:
    x
''', r'''
For - ROOT 0,0..1,5
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
'''),

('', 1, None, '_bases', {'raw': True, 'to': 'keywords[0]'}, (None,
r'''class cls(a, *b, c=d, **e): pass'''),
r'''x''',
r'''class cls(a, x, **e): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Name 'x' Load - 0,13..0,14
  .keywords[1]
   0] keyword - 0,16..0,19
     .value Name 'e' Load - 0,18..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, None, '_args', {'raw': True, 'to': 'keywords[0]'}, (None,
r'''call(a, *b, c=d, **e)'''),
r'''x''',
r'''call(a, x, **e)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Name 'x' Load - 0,8..0,9
  .keywords[1]
   0] keyword - 0,11..0,14
     .value Name 'e' Load - 0,13..0,14
'''),
],

'misc': [  # ................................................................................

('target', None, None, 'value', {}, (None,
r'''a[b]: int = c'''), (None,
r'''f()'''),
r'''f()[b]: int = c''', r'''
AnnAssign - ROOT 0,0..0,15
  .target Subscript - 0,0..0,6
    .value Call - 0,0..0,3
      .func Name 'f' Load - 0,0..0,1
    .slice Name 'b' Load - 0,4..0,5
    .ctx Store
  .annotation Name 'int' Load - 0,8..0,11
  .value Name 'c' Load - 0,14..0,15
  .simple 0
'''),

('', None, None, 'ctx', {}, (None,
r'''a'''), (None,
r''''''),
r'''**ValueError('expecting expr_context, got str')**'''),

('values[0].format_spec', 0, None, 'values', {'_ver': 12}, (None,
r'''f"{a:s}"'''), (None,
r'''lambda: None'''),
r'''**NotImplementedError('this is not implemented yet')**'''),

('', 1, None, 'elts', {'_ver': 11}, (None,
r'''a, b'''), (None,
r'''lambda: None'''),
r'''a, lambda: None''', r'''
Tuple - ROOT 0,0..0,15
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Lambda - 0,3..0,15
     .body Constant None - 0,11..0,15
  .ctx Load
'''),

('', None, None, 'op', {'raw': True}, (None,
r'''a or b'''), (None,
r'''and'''),
r'''**ValueError('cannot determine location to put to')**'''),

('', 0, None, None, {}, ('exec',
r'''a'''), ('Expression',
r'''x'''),
r'''x''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'x' Load - 0,0..0,1
'''),

('', 0, None, None, {}, ('exec',
r'''a'''), ('Interactive',
r'''x'''),
r'''x''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'x' Load - 0,0..0,1
'''),

('', 0, None, '_args', {'_src': False}, (None,
r'''call(a)'''), ('Slice',
r'''x:y:z'''),
r'''**NodeError('expecting expression (arglike), got Slice')**'''),

('', 0, None, None, {'_src': False, 'raw': False}, (None,
r'''import a'''), (None,
r'''(b).c'''),
r'''import b.c''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'b.c'
'''),
],

}
