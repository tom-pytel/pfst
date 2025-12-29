# (attr, start, stop, field, options, code | (parse_mode, code), put_code | (parse_mode, put_code),
#
# code after put,
# [code after put FST if different,]  - shouldn't be present if everything working correctly
# [code after put AST if different,]  - can be present
# dump code after put)
# - OR
# error)

DATA_PUT_SLICE = {
'old_stmtlike': [  # ................................................................................

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i
    j
'''), (None,
r'''k'''), r'''
if 1:
    i
    k
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i  # post
    j
'''), (None,
r'''k'''), r'''
if 1:
    i  # post
    k
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i \
  # post
    j
'''), (None,
r'''k'''), r'''
if 1:
    i \
  # post
    k
    j
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] If - 0,0..4,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
      2] Expr - 4,4..4,5
        .value Name 'j' Load - 4,4..4,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i  # post
    # pre
    j
'''), (None,
r'''k'''), r'''
if 1:
    i  # post
    k
    # pre
    j
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] If - 0,0..4,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 4,4..4,5
        .value Name 'j' Load - 4,4..4,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i
    # pre
    j
'''), (None,
r'''k'''), r'''
if 1:
    i
    k
    # pre
    j
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] If - 0,0..4,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 4,4..4,5
        .value Name 'j' Load - 4,4..4,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i

    # pre pre

    # pre

    j
'''), (None,
r'''k'''), r'''
if 1:
    i
    k

    # pre pre

    # pre

    j
''', r'''
Module - ROOT 0,0..8,5
  .body[1]
   0] If - 0,0..8,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 8,4..8,5
        .value Name 'j' Load - 8,4..8,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i ; j
'''), (None,
r'''k'''), r'''
if 1:
    i
    k
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i ; \
  j
'''), (None,
r'''k'''), r'''
if 1:
    i
    k
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i \
  ; j
'''), (None,
r'''k'''), r'''
if 1:
    i
    k
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i \
  ; \
  j
'''), (None,
r'''k'''), r'''
if 1:
    i
    k
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec',
r'''if 1: i ; j'''), (None,
r'''k'''), r'''
if 1:
    i
    k
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1: \
  i \
  ; \
  j
'''), (None,
r'''k'''), r'''
if 1:
    i
    k
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 2, 2, 'body', {}, ('exec', r'''
if 1:
    i ; j ; l ; m
'''), (None,
r'''k'''), r'''
if 1:
    i ; j
    k
    l ; m
''', r'''
Module - ROOT 0,0..3,9
  .body[1]
   0] If - 0,0..3,9
     .test Constant 1 - 0,3..0,4
     .body[5]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 1,8..1,9
        .value Name 'j' Load - 1,8..1,9
      2] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      3] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      4] Expr - 3,8..3,9
        .value Name 'm' Load - 3,8..3,9
'''),

('body[0]', 2, 2, 'body', {}, ('exec',
r'''if 1: i ; j ; l ; m'''), (None,
r'''k'''), r'''
if 1:
    i ; j
    k
    l ; m
''', r'''
Module - ROOT 0,0..3,9
  .body[1]
   0] If - 0,0..3,9
     .test Constant 1 - 0,3..0,4
     .body[5]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 1,8..1,9
        .value Name 'j' Load - 1,8..1,9
      2] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      3] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      4] Expr - 3,8..3,9
        .value Name 'm' Load - 3,8..3,9
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i
'''), (None,
r'''k'''), r'''
if 1:
    i
    k
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i  # post
'''), (None,
r'''k'''), r'''
if 1:
    i  # post
    k
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i  # post
    # pre
'''), (None,
r'''k'''), r'''
if 1:
    i  # post
    k
    # pre
''', r'''
Module - ROOT 0,0..3,9
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec',
r'''if 1: i'''), (None,
r'''k'''), r'''
if 1:
    i
    k
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec',
r'''if 1: i  # post'''), (None,
r'''k'''), r'''
if 1:
    i  # post
    k
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1: i  # post
    # pre
'''), (None,
r'''k'''), r'''
if 1:
    i  # post
    k
    # pre
''', r'''
Module - ROOT 0,0..3,9
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1: i ;
    # pre
'''), (None,
r'''k'''), r'''
if 1:
    i ;
    k
    # pre
''', r'''
Module - ROOT 0,0..3,9
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
'''),

('body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1: i ;  # post
    # pre
'''), (None,
r'''k'''), r'''
if 1:
    i ;  # post
    k
    # pre
''', r'''
Module - ROOT 0,0..3,9
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
'''),

('body[0]', 0, 0, 'body', {}, ('exec', r'''
if 1:
    i
'''), (None,
r'''k'''), r'''
if 1:
    k
    i
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'k' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'i' Load - 2,4..2,5
'''),

('body[0]', 0, 0, 'body', {}, ('exec', r'''
if 1:  # post-block
    i
'''), (None,
r'''k'''), r'''
if 1:  # post-block
    k
    i
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'k' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'i' Load - 2,4..2,5
'''),

('body[0]', 0, 0, 'body', {}, ('exec', r'''
if 1:
    # pre
    i
'''), (None,
r'''k'''), r'''
if 1:
    k
    # pre
    i
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'k' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'i' Load - 3,4..3,5
'''),

('body[0]', 0, 0, 'body', {}, ('exec', r'''
if 1:  # post-block
    # pre
    i
'''), (None,
r'''k'''), r'''
if 1:  # post-block
    k
    # pre
    i
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'k' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'i' Load - 3,4..3,5
'''),

('body[0]', 0, 0, 'body', {}, ('exec', r'''
if 1: \
  # post-lline-block
    # pre
    i
'''), (None,
r'''k'''), r'''
if 1: \
  # post-lline-block
    k
    # pre
    i
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] If - 0,0..4,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      1] Expr - 4,4..4,5
        .value Name 'i' Load - 4,4..4,5
'''),

('body[0]', 0, 0, 'body', {}, ('exec',
r'''if 1: i ; j  # post-multi'''), (None,
r'''k'''), r'''
if 1:
    k
    i ; j  # post-multi
''', r'''
Module - ROOT 0,0..2,23
  .body[1]
   0] If - 0,0..2,9
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'k' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'i' Load - 2,4..2,5
      2] Expr - 2,8..2,9
        .value Name 'j' Load - 2,8..2,9
'''),

('body[0]', 0, 0, 'body', {}, ('exec', r'''
if 1: \
  i ; j  # post-multi
'''), (None,
r'''k'''), r'''
if 1:
    k
    i ; j  # post-multi
''', r'''
Module - ROOT 0,0..2,23
  .body[1]
   0] If - 0,0..2,9
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'k' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'i' Load - 2,4..2,5
      2] Expr - 2,8..2,9
        .value Name 'j' Load - 2,8..2,9
'''),

('body[0].body[0]', 0, 0, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
def f():
    if 1:
        pass
'''), (None,
r'''if 2: break'''), r'''
def f():
    if 1:
        pass
    elif 2: break
''', r'''
def f():
    if 1:
        pass
    elif 2:
        break
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] FunctionDef - 0,0..3,17
     .name 'f'
     .body[1]
      0] If - 1,4..3,17
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 2,8..2,12
        .orelse[1]
         0] If - 3,4..3,17
           .test Constant 2 - 3,9..3,10
           .body[1]
            0] Break - 3,12..3,17
'''),

('body[0].body[0]', 0, 0, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
def f():
    if 1:
        pass  # post-if
    # post-line
'''), (None, r'''
# pre
if 2: break  # post-elif
'''), r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # post-line
''', r'''
def f():
    if 1:
        pass  # post-if
    elif 2:
        break
    # post-line
''', r'''
Module - ROOT 0,0..5,15
  .body[1]
   0] FunctionDef - 0,0..4,17
     .name 'f'
     .body[1]
      0] If - 1,4..4,17
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 2,8..2,12
        .orelse[1]
         0] If - 4,4..4,17
           .test Constant 2 - 4,9..4,10
           .body[1]
            0] Break - 4,12..4,17
'''),

('body[0].body[0].orelse[0]', 0, 0, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # post-line
'''), (None, r'''
# pre-3
if 3:  # post-elif-3
    continue  # post-elif-continue-3
'''), r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
''', r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    elif 3:
        continue
    # post-line
''', r'''
Module - ROOT 0,0..8,15
  .body[1]
   0] FunctionDef - 0,0..7,16
     .name 'f'
     .body[1]
      0] If - 1,4..7,16
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 2,8..2,12
        .orelse[1]
         0] If - 4,4..7,16
           .test Constant 2 - 4,9..4,10
           .body[1]
            0] Break - 4,12..4,17
           .orelse[1]
            0] If - 6,4..7,16
              .test Constant 3 - 6,9..6,10
              .body[1]
               0] Continue - 7,8..7,16
'''),

('body[0].body[0]', 0, 1, 'orelse', {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
'''), (None,
r'''**DEL**'''), r'''
def f():
    if 1:
        pass  # post-if
    # pre
    # post-line
''', r'''
Module - ROOT 0,0..4,15
  .body[1]
   0] FunctionDef - 0,0..2,12
     .name 'f'
     .body[1]
      0] If - 1,4..2,12
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 2,8..2,12
'''),

('body[0].body[0]', 0, 1, 'orelse', {'trivia': (True, False), 'pep8space': False}, ('exec', r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
'''), (None,
r'''**DEL**'''), r'''
def f():
    if 1:
        pass  # post-if
    # post-line
''', r'''
Module - ROOT 0,0..3,15
  .body[1]
   0] FunctionDef - 0,0..2,12
     .name 'f'
     .body[1]
      0] If - 1,4..2,12
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 2,8..2,12
'''),

('body[0].body[0]', 0, 1, 'orelse', {'trivia': (False, True), 'pep8space': False}, ('exec', r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
'''), (None,
r'''**DEL**'''), r'''
def f():
    if 1:
        pass  # post-if
    # pre
    # post-line
''', r'''
Module - ROOT 0,0..4,15
  .body[1]
   0] FunctionDef - 0,0..2,12
     .name 'f'
     .body[1]
      0] If - 1,4..2,12
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 2,8..2,12
'''),

('body[0].body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif
    # pre-3
    elif 3:  # post-elif-3
        continue  # post-elif-continue-3
    # post-line
'''), (None,
r'''**DEL**'''), r'''
def f():
    if 1:
        pass  # post-if
    # post-line
''', r'''
Module - ROOT 0,0..3,15
  .body[1]
   0] FunctionDef - 0,0..2,12
     .name 'f'
     .body[1]
      0] If - 1,4..2,12
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 2,8..2,12
'''),

('body[0].body[0].orelse[0]', 0, 1, 'orelse', {'trivia': ('all-', True), 'pep8space': False}, ('exec', r'''
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
'''), (None,
r'''**DEL**'''), r'''
def f():
    if 1:
        pass  # post-if
    # pre
    elif 2: break  # post-elif

    # post-line
''', r'''
Module - ROOT 0,0..6,15
  .body[1]
   0] FunctionDef - 0,0..4,17
     .name 'f'
     .body[1]
      0] If - 1,4..4,17
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 2,8..2,12
        .orelse[1]
         0] If - 4,4..4,17
           .test Constant 2 - 4,9..4,10
           .body[1]
            0] Break - 4,12..4,17
'''),

('', 0, 0, None, {}, ('exec',
r''''''), (None,
r'''i'''),
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

('', 0, 0, None, {}, ('exec',
r'''# comment'''), (None,
r'''i'''), r'''
# comment
i
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'i' Load - 1,0..1,1
'''),

('', 0, 0, None, {}, ('exec', r'''
# comment

# another comment
'''), (None,
r'''i'''), r'''
# comment

# another comment
i
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 3,0..3,1
     .value Name 'i' Load - 3,0..3,1
'''),

('', 0, 0, None, {}, ('exec', r'''
# comment

# another comment
i
'''), (None,
r'''h'''), r'''
# comment

# another comment
h
i
''', r'''
Module - ROOT 0,0..4,1
  .body[2]
   0] Expr - 3,0..3,1
     .value Name 'h' Load - 3,0..3,1
   1] Expr - 4,0..4,1
     .value Name 'i' Load - 4,0..4,1
'''),

('', 1, 1, None, {}, ('exec', r'''
# comment

# another comment
i
'''), (None,
r'''j'''), r'''
# comment

# another comment
i
j
''', r'''
Module - ROOT 0,0..4,1
  .body[2]
   0] Expr - 3,0..3,1
     .value Name 'i' Load - 3,0..3,1
   1] Expr - 4,0..4,1
     .value Name 'j' Load - 4,0..4,1
'''),

('body[0].body[0]', 0, 0, 'orelse', {}, ('exec', r'''
def f():
    if 1: pass
    elif 2: pass
'''), (None,
r'''break'''), r'''
def f():
    if 1: pass
    else:
        break
        if 2: pass
''', r'''
Module - ROOT 0,0..4,18
  .body[1]
   0] FunctionDef - 0,0..4,18
     .name 'f'
     .body[1]
      0] If - 1,4..4,18
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[2]
         0] Break - 3,8..3,13
         1] If - 4,8..4,18
           .test Constant 2 - 4,11..4,12
           .body[1]
            0] Pass - 4,14..4,18
'''),

('body[0].body[0]', 1, 1, 'orelse', {}, ('exec', r'''
def f():
    if 1: pass
    elif 2: pass
'''), (None,
r'''break'''), r'''
def f():
    if 1: pass
    else:
        if 2: pass
        break
''', r'''
Module - ROOT 0,0..4,13
  .body[1]
   0] FunctionDef - 0,0..4,13
     .name 'f'
     .body[1]
      0] If - 1,4..4,13
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[2]
         0] If - 3,8..3,18
           .test Constant 2 - 3,11..3,12
           .body[1]
            0] Pass - 3,14..3,18
         1] Break - 4,8..4,13
'''),

('body[0].body[0]', 0, 0, 'orelse', {}, ('exec', r'''
def f():
    if 1: pass
    elif 2:
        pass
'''), (None,
r'''break'''), r'''
def f():
    if 1: pass
    else:
        break
        if 2:
            pass
''', r'''
Module - ROOT 0,0..5,16
  .body[1]
   0] FunctionDef - 0,0..5,16
     .name 'f'
     .body[1]
      0] If - 1,4..5,16
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[2]
         0] Break - 3,8..3,13
         1] If - 4,8..5,16
           .test Constant 2 - 4,11..4,12
           .body[1]
            0] Pass - 5,12..5,16
'''),

('body[0].body[0]', 1, 1, 'orelse', {}, ('exec', r'''
def f():
    if 1: pass
    elif 2:
        pass
'''), (None,
r'''break'''), r'''
def f():
    if 1: pass
    else:
        if 2:
            pass
        break
''', r'''
Module - ROOT 0,0..5,13
  .body[1]
   0] FunctionDef - 0,0..5,13
     .name 'f'
     .body[1]
      0] If - 1,4..5,13
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[2]
         0] If - 3,8..4,16
           .test Constant 2 - 3,11..3,12
           .body[1]
            0] Pass - 4,12..4,16
         1] Break - 5,8..5,13
'''),

('body[0].body[0]', 0, 0, 'orelse', {}, ('exec', r'''
def f():
    if 1: pass
    elif 2: continue
    elif 3: raise
'''), (None,
r'''break'''), r'''
def f():
    if 1: pass
    else:
        break
        if 2: continue
        elif 3: raise
''', r'''
Module - ROOT 0,0..5,21
  .body[1]
   0] FunctionDef - 0,0..5,21
     .name 'f'
     .body[1]
      0] If - 1,4..5,21
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[2]
         0] Break - 3,8..3,13
         1] If - 4,8..5,21
           .test Constant 2 - 4,11..4,12
           .body[1]
            0] Continue - 4,14..4,22
           .orelse[1]
            0] If - 5,8..5,21
              .test Constant 3 - 5,13..5,14
              .body[1]
               0] Raise - 5,16..5,21
'''),

('body[0].body[0]', 1, 1, 'orelse', {}, ('exec', r'''
def f():
    if 1: pass
    elif 2: continue
    elif 3: raise
'''), (None,
r'''break'''), r'''
def f():
    if 1: pass
    else:
        if 2: continue
        elif 3: raise
        break
''', r'''
Module - ROOT 0,0..5,13
  .body[1]
   0] FunctionDef - 0,0..5,13
     .name 'f'
     .body[1]
      0] If - 1,4..5,13
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[2]
         0] If - 3,8..4,21
           .test Constant 2 - 3,11..3,12
           .body[1]
            0] Continue - 3,14..3,22
           .orelse[1]
            0] If - 4,8..4,21
              .test Constant 3 - 4,13..4,14
              .body[1]
               0] Raise - 4,16..4,21
         1] Break - 5,8..5,13
'''),

('body[0].body[0].orelse[0]', 0, 0, 'orelse', {}, ('exec', r'''
def f():
    if 1: pass
    elif 2: continue
    elif 3: raise
'''), (None,
r'''break'''), r'''
def f():
    if 1: pass
    elif 2: continue
    else:
        break
        if 3: raise
''', r'''
Module - ROOT 0,0..5,19
  .body[1]
   0] FunctionDef - 0,0..5,19
     .name 'f'
     .body[1]
      0] If - 1,4..5,19
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 2,4..5,19
           .test Constant 2 - 2,9..2,10
           .body[1]
            0] Continue - 2,12..2,20
           .orelse[2]
            0] Break - 4,8..4,13
            1] If - 5,8..5,19
              .test Constant 3 - 5,11..5,12
              .body[1]
               0] Raise - 5,14..5,19
'''),

('body[0].body[0].orelse[0]', 1, 1, 'orelse', {}, ('exec', r'''
def f():
    if 1: pass
    elif 2: continue
    elif 3: raise
'''), (None,
r'''break'''), r'''
def f():
    if 1: pass
    elif 2: continue
    else:
        if 3: raise
        break
''', r'''
Module - ROOT 0,0..5,13
  .body[1]
   0] FunctionDef - 0,0..5,13
     .name 'f'
     .body[1]
      0] If - 1,4..5,13
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 2,4..5,13
           .test Constant 2 - 2,9..2,10
           .body[1]
            0] Continue - 2,12..2,20
           .orelse[2]
            0] If - 4,8..4,19
              .test Constant 3 - 4,11..4,12
              .body[1]
               0] Raise - 4,14..4,19
            1] Break - 5,8..5,13
'''),

('body[0]', 0, 0, None, {}, ('exec', r'''
def f():
    i
'''), (None,
r'''# comment'''), r'''
def f():
    # comment
    i
''', r'''
def f():
    i
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] FunctionDef - 0,0..2,5
     .name 'f'
     .body[1]
      0] Expr - 2,4..2,5
        .value Name 'i' Load - 2,4..2,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
def f():
    i
'''), (None,
r'''# comment'''), r'''
def f():
    i
    # comment
''', r'''
def f():
    i
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 0,0..1,5
     .name 'f'
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
'''),

('body[0]', 0, 0, None, {}, ('exec', r'''
def f():
    i ; j
'''), (None,
r'''# comment'''), r'''
def f():
    # comment
    i ; j
''', r'''
def f():
    i ; j
''', r'''
Module - ROOT 0,0..2,9
  .body[1]
   0] FunctionDef - 0,0..2,9
     .name 'f'
     .body[2]
      0] Expr - 2,4..2,5
        .value Name 'i' Load - 2,4..2,5
      1] Expr - 2,8..2,9
        .value Name 'j' Load - 2,8..2,9
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
def f():
    i ; j
'''), (None,
r'''# comment'''), r'''
def f():
    i
    # comment
    j
''', r'''
def f():
    i ; j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] FunctionDef - 0,0..3,5
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 2, 2, None, {}, ('exec', r'''
def f():
    i ; j
'''), (None,
r'''# comment'''), r'''
def f():
    i ; j
    # comment
''', r'''
def f():
    i ; j
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 0,0..1,9
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 1,8..1,9
        .value Name 'j' Load - 1,8..1,9
'''),

('body[0]', 0, 0, None, {}, ('exec', r'''
def f():
    i \
  \
  ; \
  j
'''), (None,
r'''# comment'''), r'''
def f():
    # comment
    i \
  \
  ; \
  j
''', r'''
def f():
    i \
  \
  ; \
  j
''', r'''
Module - ROOT 0,0..5,3
  .body[1]
   0] FunctionDef - 0,0..5,3
     .name 'f'
     .body[2]
      0] Expr - 2,4..2,5
        .value Name 'i' Load - 2,4..2,5
      1] Expr - 5,2..5,3
        .value Name 'j' Load - 5,2..5,3
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
def f():
    i \
  \
  ; \
  j
'''), (None,
r'''# comment'''), r'''
def f():
    i
    # comment
    j
''', r'''
def f():
    i \
  \
  ; \
  j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] FunctionDef - 0,0..3,5
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 2, 2, None, {}, ('exec', r'''
def f():
    i \
  \
  ; \
  j
'''), (None,
r'''# comment'''), r'''
def f():
    i \
  \
  ; \
  j
    # comment
''', r'''
def f():
    i \
  \
  ; \
  j
''', r'''
Module - ROOT 0,0..5,13
  .body[1]
   0] FunctionDef - 0,0..4,3
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 4,2..4,3
        .value Name 'j' Load - 4,2..4,3
'''),

('', 0, 0, None, {'pep8space': True}, ('exec',
r''''''), (None,
r'''def func(): pass'''),
r'''def func(): pass''', r'''
def func():
    pass
''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
'''),

('', 0, 0, None, {'pep8space': True}, ('exec',
r''''''), (None, r'''

def func(): pass
'''), r'''

def func(): pass
''', r'''
def func():
    pass
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] FunctionDef - 1,0..1,16
     .name 'func'
     .body[1]
      0] Pass - 1,12..1,16
'''),

('', 0, 0, None, {'pep8space': True}, ('exec',
r''''''), (None, r'''

def func(): pass

'''), r'''

def func(): pass

''', r'''
def func():
    pass
''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] FunctionDef - 1,0..1,16
     .name 'func'
     .body[1]
      0] Pass - 1,12..1,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec', r'''
"""Module
   docstring"""
'''), (None,
r'''def func(): pass'''), r'''
"""Module
   docstring"""

def func(): pass
''', r'''
"""Module
   docstring"""

def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] Expr - 0,0..1,15
     .value Constant 'Module\n   docstring' - 0,0..1,15
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec', r'''
"""Module
   docstring"""
'''), (None,
r'''def func(): pass'''), r'''
"""Module
   docstring"""

def func(): pass
''', r'''
"""Module
   docstring"""

def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] Expr - 0,0..1,15
     .value Constant 'Module\n   docstring' - 0,0..1,15
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec', r'''
"""Module
   docstring"""
'''), (None, r'''

def func(): pass
'''), r'''
"""Module
   docstring"""

def func(): pass
''', r'''
"""Module
   docstring"""

def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] Expr - 0,0..1,15
     .value Constant 'Module\n   docstring' - 0,0..1,15
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec', r'''
"""Module
   docstring"""
'''), (None, r'''


def func(): pass
'''), r'''
"""Module
   docstring"""


def func(): pass
''', r'''
"""Module
   docstring"""

def func():
    pass
''', r'''
Module - ROOT 0,0..4,16
  .body[2]
   0] Expr - 0,0..1,15
     .value Constant 'Module\n   docstring' - 0,0..1,15
   1] FunctionDef - 4,0..4,16
     .name 'func'
     .body[1]
      0] Pass - 4,12..4,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass
''', r'''
def prefunc(): pass


def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': 1}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass

def func(): pass
''', r'''
def prefunc(): pass

def func():
    pass
''', r'''
Module - ROOT 0,0..2,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 2,0..2,16
     .name 'func'
     .body[1]
      0] Pass - 2,12..2,16
'''),

('', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass
def func(): pass
''', r'''
def prefunc(): pass
def func():
    pass
''', r'''
Module - ROOT 0,0..1,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 1,0..1,16
     .name 'func'
     .body[1]
      0] Pass - 1,12..1,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec',
r'''def prefunc(): pass'''), (None, r'''

def func(): pass
'''), r'''
def prefunc(): pass


def func(): pass
''', r'''
def prefunc(): pass


def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': 1}, ('exec',
r'''def prefunc(): pass'''), (None, r'''

def func(): pass
'''), r'''
def prefunc(): pass

def func(): pass
''', r'''
def prefunc(): pass

def func():
    pass
''', r'''
Module - ROOT 0,0..2,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 2,0..2,16
     .name 'func'
     .body[1]
      0] Pass - 2,12..2,16
'''),

('', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass
def func(): pass
''', r'''
def prefunc(): pass
def func():
    pass
''', r'''
Module - ROOT 0,0..1,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 1,0..1,16
     .name 'func'
     .body[1]
      0] Pass - 1,12..1,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec',
r'''def prefunc(): pass'''), (None, r'''


def func(): pass
'''), r'''
def prefunc(): pass


def func(): pass
''', r'''
def prefunc(): pass


def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': 1}, ('exec',
r'''def prefunc(): pass'''), (None, r'''


def func(): pass
'''), r'''
def prefunc(): pass


def func(): pass
''', r'''
def prefunc(): pass

def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec',
r'''def prefunc(): pass'''), (None, r'''



def func(): pass
'''), r'''
def prefunc(): pass



def func(): pass
''', r'''
def prefunc(): pass


def func():
    pass
''', r'''
Module - ROOT 0,0..4,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 4,0..4,16
     .name 'func'
     .body[1]
      0] Pass - 4,12..4,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec',
r'''import stuff'''), (None,
r'''def func(): pass'''), r'''
import stuff


def func(): pass
''', r'''
import stuff


def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] Import - 0,0..0,12
     .names[1]
      0] alias - 0,7..0,12
        .name 'stuff'
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec',
r'''import stuff'''), (None, r'''

def func(): pass
'''), r'''
import stuff


def func(): pass
''', r'''
import stuff


def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] Import - 0,0..0,12
     .names[1]
      0] alias - 0,7..0,12
        .name 'stuff'
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec',
r'''import stuff'''), (None, r'''


def func(): pass
'''), r'''
import stuff


def func(): pass
''', r'''
import stuff


def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] Import - 0,0..0,12
     .names[1]
      0] alias - 0,7..0,12
        .name 'stuff'
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 1, 1, None, {'pep8space': True}, ('exec',
r'''import stuff'''), (None, r'''


def func(): pass
'''), r'''
import stuff


def func(): pass
''', r'''
import stuff


def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] Import - 0,0..0,12
     .names[1]
      0] alias - 0,7..0,12
        .name 'stuff'
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 0, 0, None, {}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def func(): pass


def prefunc(): pass
''', r'''
def func():
    pass


def prefunc(): pass
''', r'''
Module - ROOT 0,0..3,19
  .body[2]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
   1] FunctionDef - 3,0..3,19
     .name 'prefunc'
     .body[1]
      0] Pass - 3,15..3,19
'''),

('', 0, 0, None, {'pep8space': 1}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def func(): pass

def prefunc(): pass
''', r'''
def func():
    pass

def prefunc(): pass
''', r'''
Module - ROOT 0,0..2,19
  .body[2]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
   1] FunctionDef - 2,0..2,19
     .name 'prefunc'
     .body[1]
      0] Pass - 2,15..2,19
'''),

('', 0, 0, None, {'trivia': (False, False), 'pep8space': False}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def func(): pass
def prefunc(): pass
''', r'''
def func():
    pass
def prefunc(): pass
''', r'''
Module - ROOT 0,0..1,19
  .body[2]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
   1] FunctionDef - 1,0..1,19
     .name 'prefunc'
     .body[1]
      0] Pass - 1,15..1,19
'''),

('', 0, 0, None, {}, ('exec',
r'''def prefunc(): pass'''), (None, r'''
def func(): pass

'''), r'''
def func(): pass


def prefunc(): pass
''', r'''
def func():
    pass


def prefunc(): pass
''', r'''
Module - ROOT 0,0..3,19
  .body[2]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
   1] FunctionDef - 3,0..3,19
     .name 'prefunc'
     .body[1]
      0] Pass - 3,15..3,19
'''),

('', 0, 0, None, {}, ('exec',
r'''def prefunc(): pass'''), (None, r'''
def func(): pass


'''), r'''
def func(): pass


def prefunc(): pass
''', r'''
def func():
    pass


def prefunc(): pass
''', r'''
Module - ROOT 0,0..3,19
  .body[2]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
   1] FunctionDef - 3,0..3,19
     .name 'prefunc'
     .body[1]
      0] Pass - 3,15..3,19
'''),

('', 0, 0, None, {}, ('exec',
r'''def prefunc(): pass'''), (None, r'''
def func(): pass



'''), r'''
def func(): pass


def prefunc(): pass
''', r'''
def func():
    pass


def prefunc(): pass
''', r'''
Module - ROOT 0,0..3,19
  .body[2]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
   1] FunctionDef - 3,0..3,19
     .name 'prefunc'
     .body[1]
      0] Pass - 3,15..3,19
'''),

('', 0, 0, None, {}, ('exec',
r'''def prefunc(): pass'''), (None, r'''
def func(): pass




'''), r'''
def func(): pass



def prefunc(): pass
''', r'''
def func():
    pass


def prefunc(): pass
''', r'''
Module - ROOT 0,0..4,19
  .body[2]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
   1] FunctionDef - 4,0..4,19
     .name 'prefunc'
     .body[1]
      0] Pass - 4,15..4,19
'''),

('', 1, 1, None, {}, ('exec', r'''
def prefunc(): pass
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass


def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..6,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 6,0..6,20
     .name 'postfunc'
     .body[1]
      0] Pass - 6,16..6,20
'''),

('', 1, 1, None, {}, ('exec', r'''
def prefunc(): pass

def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass


def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..6,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 6,0..6,20
     .name 'postfunc'
     .body[1]
      0] Pass - 6,16..6,20
'''),

('', 1, 1, None, {}, ('exec', r'''
def prefunc(): pass


def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass


def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..6,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 6,0..6,20
     .name 'postfunc'
     .body[1]
      0] Pass - 6,16..6,20
'''),

('', 1, 1, None, {}, ('exec', r'''
def prefunc(): pass



def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass



def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass



def postfunc(): pass
''', r'''
Module - ROOT 0,0..7,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 7,0..7,20
     .name 'postfunc'
     .body[1]
      0] Pass - 7,16..7,20
'''),

('', 1, 1, None, {}, ('exec', r'''
def prefunc(): pass




def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass




def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass




def postfunc(): pass
''', r'''
Module - ROOT 0,0..8,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 8,0..8,20
     .name 'postfunc'
     .body[1]
      0] Pass - 8,16..8,20
'''),

('', 1, 1, None, {'pep8space': 1}, ('exec', r'''
def prefunc(): pass
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass

def func(): pass

def postfunc(): pass
''', r'''
def prefunc(): pass

def func():
    pass

def postfunc(): pass
''', r'''
Module - ROOT 0,0..4,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 2,0..2,16
     .name 'func'
     .body[1]
      0] Pass - 2,12..2,16
   2] FunctionDef - 4,0..4,20
     .name 'postfunc'
     .body[1]
      0] Pass - 4,16..4,20
'''),

('', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
def prefunc(): pass
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass
def func(): pass
def postfunc(): pass
''', r'''
def prefunc(): pass
def func():
    pass
def postfunc(): pass
''', r'''
Module - ROOT 0,0..2,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 1,0..1,16
     .name 'func'
     .body[1]
      0] Pass - 1,12..1,16
   2] FunctionDef - 2,0..2,20
     .name 'postfunc'
     .body[1]
      0] Pass - 2,16..2,20
'''),

('', 1, 1, None, {}, ('exec', r'''
def prefunc(): pass

def postfunc(): pass
'''), (None, r'''
def func(): pass

'''), r'''
def prefunc(): pass


def func(): pass


def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..6,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 6,0..6,20
     .name 'postfunc'
     .body[1]
      0] Pass - 6,16..6,20
'''),

('', 1, 1, None, {}, ('exec', r'''
def prefunc(): pass

def postfunc(): pass
'''), (None, r'''
def func(): pass


'''), r'''
def prefunc(): pass


def func(): pass



def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..7,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 7,0..7,20
     .name 'postfunc'
     .body[1]
      0] Pass - 7,16..7,20
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    """Class
       docstring"""
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    """Class
       docstring"""

    def meth(): pass
''', r'''
class cls:
    """Class
       docstring"""

    def meth():
        pass
''', r'''
Module - ROOT 0,0..4,20
  .body[1]
   0] ClassDef - 0,0..4,20
     .name 'cls'
     .body[2]
      0] Expr - 1,4..2,19
        .value Constant 'Class\n       docstring' - 1,4..2,19
      1] FunctionDef - 4,4..4,20
        .name 'meth'
        .body[1]
         0] Pass - 4,16..4,20
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    """Class
       docstring"""
'''), (None, r'''

def meth(): pass
'''), r'''
class cls:
    """Class
       docstring"""

    def meth(): pass
''', r'''
class cls:
    """Class
       docstring"""

    def meth():
        pass
''', r'''
Module - ROOT 0,0..4,20
  .body[1]
   0] ClassDef - 0,0..4,20
     .name 'cls'
     .body[2]
      0] Expr - 1,4..2,19
        .value Constant 'Class\n       docstring' - 1,4..2,19
      1] FunctionDef - 4,4..4,20
        .name 'meth'
        .body[1]
         0] Pass - 4,16..4,20
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    """Class
       docstring"""
'''), (None, r'''


def meth(): pass
'''), r'''
class cls:
    """Class
       docstring"""


    def meth(): pass
''', r'''
class cls:
    """Class
       docstring"""

    def meth():
        pass
''', r'''
Module - ROOT 0,0..5,20
  .body[1]
   0] ClassDef - 0,0..5,20
     .name 'cls'
     .body[2]
      0] Expr - 1,4..2,19
        .value Constant 'Class\n       docstring' - 1,4..2,19
      1] FunctionDef - 5,4..5,20
        .name 'meth'
        .body[1]
         0] Pass - 5,16..5,20
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass
''', r'''
Module - ROOT 0,0..3,20
  .body[1]
   0] ClassDef - 0,0..3,20
     .name 'cls'
     .body[2]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
'''), (None, r'''

def meth(): pass
'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass
''', r'''
Module - ROOT 0,0..3,20
  .body[1]
   0] ClassDef - 0,0..3,20
     .name 'cls'
     .body[2]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
'''), (None, r'''


def meth(): pass
'''), r'''
class cls:
    def premeth(): pass


    def meth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass
''', r'''
Module - ROOT 0,0..4,20
  .body[1]
   0] ClassDef - 0,0..4,20
     .name 'cls'
     .body[2]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 4,4..4,20
        .name 'meth'
        .body[1]
         0] Pass - 4,16..4,20
'''),

('body[0]', 0, 0, None, {}, ('exec', r'''
class cls:
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..3,24
  .body[1]
   0] ClassDef - 0,0..3,24
     .name 'cls'
     .body[2]
      0] FunctionDef - 1,4..1,20
        .name 'meth'
        .body[1]
         0] Pass - 1,16..1,20
      1] FunctionDef - 3,4..3,24
        .name 'postmeth'
        .body[1]
         0] Pass - 3,20..3,24
'''),

('body[0]', 0, 0, None, {}, ('exec', r'''
class cls:
    def postmeth(): pass
'''), (None, r'''
def meth(): pass

'''), r'''
class cls:
    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..3,24
  .body[1]
   0] ClassDef - 0,0..3,24
     .name 'cls'
     .body[2]
      0] FunctionDef - 1,4..1,20
        .name 'meth'
        .body[1]
         0] Pass - 1,16..1,20
      1] FunctionDef - 3,4..3,24
        .name 'postmeth'
        .body[1]
         0] Pass - 3,20..3,24
'''),

('body[0]', 0, 0, None, {}, ('exec', r'''
class cls:
    def postmeth(): pass
'''), (None, r'''
def meth(): pass


'''), r'''
class cls:
    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..3,24
  .body[1]
   0] ClassDef - 0,0..3,24
     .name 'cls'
     .body[2]
      0] FunctionDef - 1,4..1,20
        .name 'meth'
        .body[1]
         0] Pass - 1,16..1,20
      1] FunctionDef - 3,4..3,24
        .name 'postmeth'
        .body[1]
         0] Pass - 3,20..3,24
'''),

('body[0]', 0, 0, None, {}, ('exec', r'''
class cls:
    def postmeth(): pass
'''), (None, r'''
def meth(): pass



'''), r'''
class cls:
    def meth(): pass


    def postmeth(): pass
''', r'''
class cls:
    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..4,24
  .body[1]
   0] ClassDef - 0,0..4,24
     .name 'cls'
     .body[2]
      0] FunctionDef - 1,4..1,20
        .name 'meth'
        .body[1]
         0] Pass - 1,16..1,20
      1] FunctionDef - 4,4..4,24
        .name 'postmeth'
        .body[1]
         0] Pass - 4,20..4,24
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..5,24
  .body[1]
   0] ClassDef - 0,0..5,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] FunctionDef - 5,4..5,24
        .name 'postmeth'
        .body[1]
         0] Pass - 5,20..5,24
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass

    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..5,24
  .body[1]
   0] ClassDef - 0,0..5,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] FunctionDef - 5,4..5,24
        .name 'postmeth'
        .body[1]
         0] Pass - 5,20..5,24
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass


    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass


    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass


    def postmeth(): pass
''', r'''
Module - ROOT 0,0..6,24
  .body[1]
   0] ClassDef - 0,0..6,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] FunctionDef - 6,4..6,24
        .name 'postmeth'
        .body[1]
         0] Pass - 6,20..6,24
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass



    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass



    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass



    def postmeth(): pass
''', r'''
Module - ROOT 0,0..7,24
  .body[1]
   0] ClassDef - 0,0..7,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] FunctionDef - 7,4..7,24
        .name 'postmeth'
        .body[1]
         0] Pass - 7,20..7,24
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
class cls:
    def premeth(): pass
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass
    def meth(): pass
    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass
    def meth():
        pass
    def postmeth(): pass
''', r'''
Module - ROOT 0,0..3,24
  .body[1]
   0] ClassDef - 0,0..3,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 2,4..2,20
        .name 'meth'
        .body[1]
         0] Pass - 2,16..2,20
      2] FunctionDef - 3,4..3,24
        .name 'postmeth'
        .body[1]
         0] Pass - 3,20..3,24
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass  # post
    # pre
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass  # post

    def meth(): pass

    # pre
    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass  # post

    def meth():
        pass

    # pre
    def postmeth(): pass
''', r'''
Module - ROOT 0,0..6,24
  .body[1]
   0] ClassDef - 0,0..6,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] FunctionDef - 6,4..6,24
        .name 'postmeth'
        .body[1]
         0] Pass - 6,20..6,24
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass  \
    # post
    \
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass  \
    # post

    def meth(): pass

    \
    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass  \
    # post

    def meth():
        pass

    \
    def postmeth(): pass
''', r'''
Module - ROOT 0,0..7,24
  .body[1]
   0] ClassDef - 0,0..7,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 4,4..4,20
        .name 'meth'
        .body[1]
         0] Pass - 4,16..4,20
      2] FunctionDef - 7,4..7,24
        .name 'postmeth'
        .body[1]
         0] Pass - 7,20..7,24
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    \

    \
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass

    \

    \
    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass

    \

    \
    def postmeth(): pass
''', r'''
Module - ROOT 0,0..8,24
  .body[1]
   0] ClassDef - 0,0..8,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] FunctionDef - 8,4..8,24
        .name 'postmeth'
        .body[1]
         0] Pass - 8,20..8,24
'''),

('body[0]', 1, 2, None, {'trivia': False}, ('exec', r'''
class cls:
    def premeth(): pass

    # pre
    def meth(): pass  # post

    def postmeth(): pass
'''), (None,
r'''def newmeth(): pass'''), r'''
class cls:
    def premeth(): pass

    # pre
    def newmeth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    # pre
    def newmeth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..6,24
  .body[1]
   0] ClassDef - 0,0..6,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 4,4..4,23
        .name 'newmeth'
        .body[1]
         0] Pass - 4,19..4,23
      2] FunctionDef - 6,4..6,24
        .name 'postmeth'
        .body[1]
         0] Pass - 6,20..6,24
'''),

('', 1, 2, None, {}, ('exec', r'''
def prefunc(): pass



# pre
def SHOULDNT_EAT_THE_SPACE(): pass  # post
'''), (None,
r'''def newfunc(): pass'''), r'''
def prefunc(): pass


def newfunc(): pass
''', r'''
def prefunc(): pass


def newfunc():
    pass
''', r'''
Module - ROOT 0,0..3,19
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,19
     .name 'newfunc'
     .body[1]
      0] Pass - 3,15..3,19
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    def postmeth(): pass
'''), (None,
r'''i = 1'''), r'''
class cls:
    def premeth(): pass

    i = 1

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..5,24
  .body[1]
   0] ClassDef - 0,0..5,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] Assign - 3,4..3,9
        .targets[1]
         0] Name 'i' Store - 3,4..3,5
        .value Constant 1 - 3,8..3,9
      2] FunctionDef - 5,4..5,24
        .name 'postmeth'
        .body[1]
         0] Pass - 5,20..5,24
'''),

('', 1, 1, None, {}, ('exec', r'''
def prefunc(): pass
def postfunc(): pass
'''), (None,
r'''i = 1'''), r'''
def prefunc(): pass


i = 1


def postfunc(): pass
''', r'''
Module - ROOT 0,0..6,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'i' Store - 3,0..3,1
     .value Constant 1 - 3,4..3,5
   2] FunctionDef - 6,0..6,20
     .name 'postfunc'
     .body[1]
      0] Pass - 6,16..6,20
'''),

('', 1, 2, None, {}, ('exec', r'''
i
j
k
'''), (None,
r'''l'''), r'''
i
l
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
# pre
j  # post
k
'''), (None,
r'''l'''), r'''
i
l
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i
# pre
j  # post
k
'''), (None,
r'''l'''), r'''
i
# pre
l
# post
k
''', r'''
Module - ROOT 0,0..4,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'l' Load - 2,0..2,1
   2] Expr - 4,0..4,1
     .value Name 'k' Load - 4,0..4,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
# pre
j  # post
k
'''), (None, r'''
# pre2
l  # post2
'''), r'''
i
# pre2
l  # post2
k
''', r'''
i
l
k
''', r'''
Module - ROOT 0,0..3,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'l' Load - 2,0..2,1
   2] Expr - 3,0..3,1
     .value Name 'k' Load - 3,0..3,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i
# pre
j  # post
k
'''), (None, r'''
# pre2
l  # post2
'''), r'''
i
# pre
# pre2
l  # post2
# post
k
''', r'''
i
# pre
l
# post
k
''', r'''
Module - ROOT 0,0..5,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 3,0..3,1
     .value Name 'l' Load - 3,0..3,1
   2] Expr - 5,0..5,1
     .value Name 'k' Load - 5,0..5,1
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i
    j
    k
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i
    # pre
    j  # post
    k
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i
    # pre
    j  # post
    k
'''), (None,
r'''l'''), r'''
if 1:
    i
    # pre
    l
    # post
    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] If - 0,0..5,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      2] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i
    # pre
    j  # post
    k
'''), (None, r'''
# pre2
l  # post2
'''), r'''
if 1:
    i
    # pre2
    l  # post2
    k
''', r'''
if 1:
    i
    l
    k
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] If - 0,0..4,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      2] Expr - 4,4..4,5
        .value Name 'k' Load - 4,4..4,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i
    # pre
    j  # post
    k
'''), (None, r'''
# pre2
l  # post2
'''), r'''
if 1:
    i
    # pre
    # pre2
    l  # post2
    # post
    k
''', r'''
if 1:
    i
    # pre
    l
    # post
    k
''', r'''
Module - ROOT 0,0..6,5
  .body[1]
   0] If - 0,0..6,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 4,4..4,5
        .value Name 'l' Load - 4,4..4,5
      2] Expr - 6,4..6,5
        .value Name 'k' Load - 6,4..6,5
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i \
# pre-before
j  # post-before
k
'''), (None,
r'''l'''), r'''
i \
# pre-before
l
# post-before
k
''', r'''
Module - ROOT 0,0..4,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'l' Load - 2,0..2,1
   2] Expr - 4,0..4,1
     .value Name 'k' Load - 4,0..4,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i \
# pre-before
j \
# post-line
k
'''), (None,
r'''l'''), r'''
i \
# pre-before
l
\
# post-line
k
''', r'''
Module - ROOT 0,0..5,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'l' Load - 2,0..2,1
   2] Expr - 5,0..5,1
     .value Name 'k' Load - 5,0..5,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i
# pre-before
j \
# post-line
k
'''), (None,
r'''l'''), r'''
i
# pre-before
l
\
# post-line
k
''', r'''
Module - ROOT 0,0..5,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'l' Load - 2,0..2,1
   2] Expr - 5,0..5,1
     .value Name 'k' Load - 5,0..5,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i \

j \
# post-line
k
'''), (None,
r'''l'''), r'''
i \

l
\
# post-line
k
''', r'''
Module - ROOT 0,0..5,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'l' Load - 2,0..2,1
   2] Expr - 5,0..5,1
     .value Name 'k' Load - 5,0..5,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i \
# pre-before
j  # post-before
k
'''), (None, r'''
# pre
l  # post
'''), r'''
i \
# pre-before
# pre
l  # post
# post-before
k
''', r'''
i \
# pre-before
l
# post-before
k
''', r'''
Module - ROOT 0,0..5,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 3,0..3,1
     .value Name 'l' Load - 3,0..3,1
   2] Expr - 5,0..5,1
     .value Name 'k' Load - 5,0..5,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i \
# pre-before
j \
# post-line
k
'''), (None, r'''
# pre
l  # post
'''), r'''
i \
# pre-before
# pre
l  # post
\
# post-line
k
''', r'''
i \
# pre-before
l
\
# post-line
k
''', r'''
Module - ROOT 0,0..6,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 3,0..3,1
     .value Name 'l' Load - 3,0..3,1
   2] Expr - 6,0..6,1
     .value Name 'k' Load - 6,0..6,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i
# pre-before
j \
# post-line
k
'''), (None, r'''
# pre
l  # post
'''), r'''
i
# pre-before
# pre
l  # post
\
# post-line
k
''', r'''
i
# pre-before
l
\
# post-line
k
''', r'''
Module - ROOT 0,0..6,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 3,0..3,1
     .value Name 'l' Load - 3,0..3,1
   2] Expr - 6,0..6,1
     .value Name 'k' Load - 6,0..6,1
'''),

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i \

j \
# post-line
k
'''), (None, r'''
# pre
l  # post
'''), r'''
i \

# pre
l  # post
\
# post-line
k
''', r'''
i \

l
\
# post-line
k
''', r'''
Module - ROOT 0,0..6,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 3,0..3,1
     .value Name 'l' Load - 3,0..3,1
   2] Expr - 6,0..6,1
     .value Name 'k' Load - 6,0..6,1
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i \
    # pre-before
    j  # post-before
    k
'''), (None,
r'''l'''), r'''
if 1:
    i \
    # pre-before
    l
    # post-before
    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] If - 0,0..5,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      2] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i \
    # pre-before
    j \
    # post-line
    k
'''), (None,
r'''l'''), r'''
if 1:
    i \
    # pre-before
    l
    \
    # post-line
    k
''', r'''
Module - ROOT 0,0..6,5
  .body[1]
   0] If - 0,0..6,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      2] Expr - 6,4..6,5
        .value Name 'k' Load - 6,4..6,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i
    # pre-before
    j \
    # post-line
    k
'''), (None,
r'''l'''), r'''
if 1:
    i
    # pre-before
    l
    \
    # post-line
    k
''', r'''
Module - ROOT 0,0..6,5
  .body[1]
   0] If - 0,0..6,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      2] Expr - 6,4..6,5
        .value Name 'k' Load - 6,4..6,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i \

    j \
    # post-line
    k
'''), (None,
r'''l'''), r'''
if 1:
    i \

    l
    \
    # post-line
    k
''', r'''
Module - ROOT 0,0..6,5
  .body[1]
   0] If - 0,0..6,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      2] Expr - 6,4..6,5
        .value Name 'k' Load - 6,4..6,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i \
    # pre-before
    j  # post-before
    k
'''), (None, r'''
# pre
l  # post
'''), r'''
if 1:
    i \
    # pre-before
    # pre
    l  # post
    # post-before
    k
''', r'''
if 1:
    i \
    # pre-before
    l
    # post-before
    k
''', r'''
Module - ROOT 0,0..6,5
  .body[1]
   0] If - 0,0..6,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 4,4..4,5
        .value Name 'l' Load - 4,4..4,5
      2] Expr - 6,4..6,5
        .value Name 'k' Load - 6,4..6,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i \
    # pre-before
    j \
    # post-line
    k
'''), (None, r'''
# pre
l  # post
'''), r'''
if 1:
    i \
    # pre-before
    # pre
    l  # post
    \
    # post-line
    k
''', r'''
if 1:
    i \
    # pre-before
    l
    \
    # post-line
    k
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] If - 0,0..7,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 4,4..4,5
        .value Name 'l' Load - 4,4..4,5
      2] Expr - 7,4..7,5
        .value Name 'k' Load - 7,4..7,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i
    # pre-before
    j \
    # post-line
    k
'''), (None, r'''
# pre
l  # post
'''), r'''
if 1:
    i
    # pre-before
    # pre
    l  # post
    \
    # post-line
    k
''', r'''
if 1:
    i
    # pre-before
    l
    \
    # post-line
    k
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] If - 0,0..7,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 4,4..4,5
        .value Name 'l' Load - 4,4..4,5
      2] Expr - 7,4..7,5
        .value Name 'k' Load - 7,4..7,5
'''),

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i \

    j \
    # post-line
    k
'''), (None, r'''
# pre
l  # post
'''), r'''
if 1:
    i \

    # pre
    l  # post
    \
    # post-line
    k
''', r'''
if 1:
    i \

    l
    \
    # post-line
    k
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] If - 0,0..7,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 4,4..4,5
        .value Name 'l' Load - 4,4..4,5
      2] Expr - 7,4..7,5
        .value Name 'k' Load - 7,4..7,5
'''),

('', 0, 1, None, {}, ('exec',
r'''i'''), (None,
r'''l'''),
r'''l''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec', r'''
i
j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
j
'''), (None,
r'''l'''), r'''
i
l
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i
'''), (None,
r'''l'''), r'''
if 1:
    l
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i
    j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i
    j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
'''),

('', 1, 2, None, {}, ('exec', r'''
i
j
k
'''), (None, r'''
if 1:
    pass
'''), r'''
i
if 1:
    pass
k
''', r'''
Module - ROOT 0,0..3,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] If - 1,0..2,8
     .test Constant 1 - 1,3..1,4
     .body[1]
      0] Pass - 2,4..2,8
   2] Expr - 3,0..3,1
     .value Name 'k' Load - 3,0..3,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
if 1: pass
k
'''), (None,
r'''l'''), r'''
i
l
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
if 1:
    pass
k
'''), (None,
r'''l'''), r'''
i
l
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
if 1:
    pass
k
'''), (None,
r'''if 2: break'''), r'''
i
if 2: break
k
''', r'''
i
if 2:
    break
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] If - 1,0..1,11
     .test Constant 2 - 1,3..1,4
     .body[1]
      0] Break - 1,6..1,11
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
j
k
'''), (None, r'''
x
if 1:
    pass
z
'''), r'''
i
x
if 1:
    pass
z
k
''', r'''
Module - ROOT 0,0..5,1
  .body[5]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'x' Load - 1,0..1,1
   2] If - 2,0..3,8
     .test Constant 1 - 2,3..2,4
     .body[1]
      0] Pass - 3,4..3,8
   3] Expr - 4,0..4,1
     .value Name 'z' Load - 4,0..4,1
   4] Expr - 5,0..5,1
     .value Name 'k' Load - 5,0..5,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
if 1: pass
k
'''), (None, r'''
x
l
z
'''), r'''
i
x
l
z
k
''', r'''
Module - ROOT 0,0..4,1
  .body[5]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'x' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'l' Load - 2,0..2,1
   3] Expr - 3,0..3,1
     .value Name 'z' Load - 3,0..3,1
   4] Expr - 4,0..4,1
     .value Name 'k' Load - 4,0..4,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
if 1:
    pass
k
'''), (None, r'''
x
l
z
'''), r'''
i
x
l
z
k
''', r'''
Module - ROOT 0,0..4,1
  .body[5]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'x' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'l' Load - 2,0..2,1
   3] Expr - 3,0..3,1
     .value Name 'z' Load - 3,0..3,1
   4] Expr - 4,0..4,1
     .value Name 'k' Load - 4,0..4,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i
if 1:
    pass
k
'''), (None, r'''
x
if 2: break
z
'''), r'''
i
x
if 2: break
z
k
''', r'''
i
x
if 2:
    break
z
k
''', r'''
Module - ROOT 0,0..4,1
  .body[5]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'x' Load - 1,0..1,1
   2] If - 2,0..2,11
     .test Constant 2 - 2,3..2,4
     .body[1]
      0] Break - 2,6..2,11
   3] Expr - 3,0..3,1
     .value Name 'z' Load - 3,0..3,1
   4] Expr - 4,0..4,1
     .value Name 'k' Load - 4,0..4,1
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 2:
    i
    j
    k
'''), (None, r'''
if 1:
    pass
'''), r'''
if 2:
    i
    if 1:
        pass
    k
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] If - 0,0..4,5
     .test Constant 2 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..3,12
        .test Constant 1 - 2,7..2,8
        .body[1]
         0] Pass - 3,8..3,12
      2] Expr - 4,4..4,5
        .value Name 'k' Load - 4,4..4,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 2:
    i
    if 1: pass
    k
'''), (None,
r'''l'''), r'''
if 2:
    i
    l
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 2 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 2:
    i
    if 1:
        pass
    k
'''), (None,
r'''l'''), r'''
if 2:
    i
    l
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 2 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 2:
    i
    if 1:
        pass
    k
'''), (None,
r'''if 2: break'''), r'''
if 2:
    i
    if 2: break
    k
''', r'''
if 2:
    i
    if 2:
        break
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 2 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,15
        .test Constant 2 - 2,7..2,8
        .body[1]
         0] Break - 2,10..2,15
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 2:
    i
    j
    k
'''), (None, r'''
x
if 1:
    pass
z
'''), r'''
if 2:
    i
    x
    if 1:
        pass
    z
    k
''', r'''
Module - ROOT 0,0..6,5
  .body[1]
   0] If - 0,0..6,5
     .test Constant 2 - 0,3..0,4
     .body[5]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'x' Load - 2,4..2,5
      2] If - 3,4..4,12
        .test Constant 1 - 3,7..3,8
        .body[1]
         0] Pass - 4,8..4,12
      3] Expr - 5,4..5,5
        .value Name 'z' Load - 5,4..5,5
      4] Expr - 6,4..6,5
        .value Name 'k' Load - 6,4..6,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 2:
    i
    if 1: pass
    k
'''), (None, r'''
x
l
z
'''), r'''
if 2:
    i
    x
    l
    z
    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] If - 0,0..5,5
     .test Constant 2 - 0,3..0,4
     .body[5]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'x' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      3] Expr - 4,4..4,5
        .value Name 'z' Load - 4,4..4,5
      4] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 2:
    i
    if 1:
        pass
    k
'''), (None, r'''
x
l
z
'''), r'''
if 2:
    i
    x
    l
    z
    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] If - 0,0..5,5
     .test Constant 2 - 0,3..0,4
     .body[5]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'x' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'l' Load - 3,4..3,5
      3] Expr - 4,4..4,5
        .value Name 'z' Load - 4,4..4,5
      4] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 2:
    i
    if 1:
        pass
    k
'''), (None, r'''
x
if 2: break
z
'''), r'''
if 2:
    i
    x
    if 2: break
    z
    k
''', r'''
if 2:
    i
    x
    if 2:
        break
    z
    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] If - 0,0..5,5
     .test Constant 2 - 0,3..0,4
     .body[5]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'x' Load - 2,4..2,5
      2] If - 3,4..3,15
        .test Constant 2 - 3,7..3,8
        .body[1]
         0] Break - 3,10..3,15
      3] Expr - 4,4..4,5
        .value Name 'z' Load - 4,4..4,5
      4] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('', 1, 2, None, {}, ('exec',
r'''i ; j'''), (None,
r'''l'''), r'''
i
l
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; j
'''), (None,
r'''l'''), r'''
i
l
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i ; \
 j
'''), (None,
r'''l'''), r'''
i
l
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
; \
j
'''), (None,
r'''l'''), r'''
i
l
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i ; j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i \
    ; j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i ; \
    j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i \
    ; \
    j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
'''),

('', 0, 1, None, {}, ('exec',
r'''i ; j'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('', 0, 1, None, {}, ('exec', r'''
i \
 ; j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('', 0, 1, None, {}, ('exec', r'''
i ; \
 j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('', 0, 1, None, {}, ('exec', r'''
i \
; \
j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i ; j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i \
     ; j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i ; \
     j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i \
     ; \
     j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1: \
    i ; j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1: \
    i \
     ; j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1: \
    i ; \
     j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1: \
    i \
     ; \
     j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('', 0, 1, None, {}, ('exec',
r'''i ;'''), (None,
r'''l'''),
r'''l''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec',
r'''i ;  # post'''), (None,
r'''l'''),
r'''l''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec', r'''
i ; \
 # post
'''), (None,
r'''l'''), r'''
l
 # post
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec', r'''
i ; \
 j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('', 0, 1, None, {}, ('exec', r'''
i \
 ; \
 # post
'''), (None,
r'''l'''), r'''
l
 # post
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec', r'''
i \
 ; \
 j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i ;
'''), (None,
r'''l'''), r'''
if 1:
    l
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i ;  # post
'''), (None,
r'''l'''), r'''
if 1:
    l
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i ; \
 # post
'''), (None,
r'''l'''), r'''
if 1:
    l
     # post
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i \
 ; \
 # post
'''), (None,
r'''l'''), r'''
if 1:
    l
     # post
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i ; \
 j
'''), (None,
r'''**DEL**'''),
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i ; \
 j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('body[0]', 0, 1, 'orelse', {}, ('exec', r'''
if 1: pass
else: \
  # pre
  i ; \
    j
'''), (None,
r'''**DEL**'''), r'''
if 1: pass
else:
  j
''', r'''
Module - ROOT 0,0..2,3
  .body[1]
   0] If - 0,0..2,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Expr - 2,2..2,3
        .value Name 'j' Load - 2,2..2,3
'''),

('body[0]', 0, 1, 'orelse', {}, ('exec', r'''
if 1: pass
else:
  \
  # pre
  i ; \
    j
  k
'''), (None,
r'''**DEL**'''), r'''
if 1: pass
else:

  j
  k
''', r'''
Module - ROOT 0,0..4,3
  .body[1]
   0] If - 0,0..4,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[2]
      0] Expr - 3,2..3,3
        .value Name 'j' Load - 3,2..3,3
      1] Expr - 4,2..4,3
        .value Name 'k' Load - 4,2..4,3
'''),

('body[0]', 1, 2, 'orelse', {}, ('exec', r'''
if 1: pass
else:
    k
    \
  # pre
    i ; \
    j
'''), (None,
r'''**DEL**'''), r'''
if 1: pass
else:
    k

    j
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] If - 0,0..4,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[2]
      0] Expr - 2,4..2,5
        .value Name 'k' Load - 2,4..2,5
      1] Expr - 4,4..4,5
        .value Name 'j' Load - 4,4..4,5
'''),

('body[0]', 0, 1, 'orelse', {}, ('exec', r'''
if 1: pass
else:
  # pre
  i \
 ; \
    j
'''), (None,
r'''**DEL**'''), r'''
if 1: pass
else:
  j
''', r'''
Module - ROOT 0,0..2,3
  .body[1]
   0] If - 0,0..2,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Expr - 2,2..2,3
        .value Name 'j' Load - 2,2..2,3
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i ; j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i \
 ; j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i ; \
 j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i \
; \
j
'''), (None,
r'''l'''), r'''
l
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i ; j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i \
     ; j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i ; \
     j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i \
     ; \
     j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1: \
    # pre
    i ; j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1: \
    # pre
    i \
     ; j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1: \
    # pre
    i ; \
     j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1: \
    # pre
    i \
     ; \
     j
'''), (None,
r'''l'''), r'''
if 1:
    l
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i ;
'''), (None,
r'''l'''),
r'''l''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i ;  # post
'''), (None,
r'''l'''),
r'''l''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i ; \
 # post
'''), (None,
r'''l'''), r'''
l
 # post
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('', 0, 1, None, {}, ('exec', r'''
# pre
i \
 ; \
 # post
'''), (None,
r'''l'''), r'''
l
 # post
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'l' Load - 0,0..0,1
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i ;
'''), (None,
r'''l'''), r'''
if 1:
    l
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i ;  # post
'''), (None,
r'''l'''), r'''
if 1:
    l
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i ; \
 # post
'''), (None,
r'''l'''), r'''
if 1:
    l
 # post
''', r'''
Module - ROOT 0,0..2,7
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i \
 ; \
 # post
'''), (None,
r'''l'''), r'''
if 1:
    l
 # post
''', r'''
Module - ROOT 0,0..2,7
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'l' Load - 1,4..1,5
'''),

('', 1, 2, None, {}, ('exec', r'''
def prefunc(): pass
pass
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass


def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..6,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 6,0..6,20
     .name 'postfunc'
     .body[1]
      0] Pass - 6,16..6,20
'''),

('', 1, 2, None, {}, ('exec', r'''
def prefunc(): pass
# pre
pass  # post
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass


def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..6,20
  .body[3]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] FunctionDef - 6,0..6,20
     .name 'postfunc'
     .body[1]
      0] Pass - 6,16..6,20
'''),

('', 1, 2, None, {}, ('exec', r'''
def prefunc(): pass
i ; j
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass


j
def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


j
def postfunc(): pass
''', r'''
Module - ROOT 0,0..7,20
  .body[4]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] Expr - 6,0..6,1
     .value Name 'j' Load - 6,0..6,1
   3] FunctionDef - 7,0..7,20
     .name 'postfunc'
     .body[1]
      0] Pass - 7,16..7,20
'''),

('', 2, 3, None, {}, ('exec', r'''
def prefunc(): pass
i ; j
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass
i


def func(): pass


def postfunc(): pass
''', r'''
def prefunc(): pass
i


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..7,20
  .body[4]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] Expr - 1,0..1,1
     .value Name 'i' Load - 1,0..1,1
   2] FunctionDef - 4,0..4,16
     .name 'func'
     .body[1]
      0] Pass - 4,12..4,16
   3] FunctionDef - 7,0..7,20
     .name 'postfunc'
     .body[1]
      0] Pass - 7,16..7,20
'''),

('', 1, 2, None, {}, ('exec', r'''
def prefunc(): pass
# pre
i ; j # post
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass


j # post
def postfunc(): pass
''', r'''
def prefunc(): pass


def func():
    pass


j # post
def postfunc(): pass
''', r'''
Module - ROOT 0,0..7,20
  .body[4]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
   2] Expr - 6,0..6,1
     .value Name 'j' Load - 6,0..6,1
   3] FunctionDef - 7,0..7,20
     .name 'postfunc'
     .body[1]
      0] Pass - 7,16..7,20
'''),

('', 2, 3, None, {}, ('exec', r'''
def prefunc(): pass
# pre
i ; j # post
def postfunc(): pass
'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass
# pre
i


def func(): pass


def postfunc(): pass
''', r'''
def prefunc(): pass
# pre
i


def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..8,20
  .body[4]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
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
'''),

('', 1, 1, None, {}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass
''', r'''
def prefunc(): pass


def func():
    pass
''', r'''
Module - ROOT 0,0..3,16
  .body[2]
   0] FunctionDef - 0,0..0,19
     .name 'prefunc'
     .body[1]
      0] Pass - 0,15..0,19
   1] FunctionDef - 3,0..3,16
     .name 'func'
     .body[1]
      0] Pass - 3,12..3,16
'''),

('', 0, 0, None, {}, ('exec',
r'''def postfunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def func(): pass


def postfunc(): pass
''', r'''
def func():
    pass


def postfunc(): pass
''', r'''
Module - ROOT 0,0..3,20
  .body[2]
   0] FunctionDef - 0,0..0,16
     .name 'func'
     .body[1]
      0] Pass - 0,12..0,16
   1] FunctionDef - 3,0..3,20
     .name 'postfunc'
     .body[1]
      0] Pass - 3,16..3,20
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    pass
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..5,24
  .body[1]
   0] ClassDef - 0,0..5,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] FunctionDef - 5,4..5,24
        .name 'postmeth'
        .body[1]
         0] Pass - 5,20..5,24
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    # pre
    pass  # post
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..5,24
  .body[1]
   0] ClassDef - 0,0..5,24
     .name 'cls'
     .body[3]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] FunctionDef - 5,4..5,24
        .name 'postmeth'
        .body[1]
         0] Pass - 5,20..5,24
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    i ; j
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass

    j
    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass

    j
    def postmeth(): pass
''', r'''
Module - ROOT 0,0..6,24
  .body[1]
   0] ClassDef - 0,0..6,24
     .name 'cls'
     .body[4]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] Expr - 5,4..5,5
        .value Name 'j' Load - 5,4..5,5
      3] FunctionDef - 6,4..6,24
        .name 'postmeth'
        .body[1]
         0] Pass - 6,20..6,24
'''),

('body[0]', 2, 3, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    i ; j
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass
    i

    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass
    i

    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..6,24
  .body[1]
   0] ClassDef - 0,0..6,24
     .name 'cls'
     .body[4]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] Expr - 2,4..2,5
        .value Name 'i' Load - 2,4..2,5
      2] FunctionDef - 4,4..4,20
        .name 'meth'
        .body[1]
         0] Pass - 4,16..4,20
      3] FunctionDef - 6,4..6,24
        .name 'postmeth'
        .body[1]
         0] Pass - 6,20..6,24
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    # pre
    i ; j # post
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass

    def meth(): pass

    j # post
    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass

    def meth():
        pass

    j # post
    def postmeth(): pass
''', r'''
Module - ROOT 0,0..6,24
  .body[1]
   0] ClassDef - 0,0..6,24
     .name 'cls'
     .body[4]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 3,4..3,20
        .name 'meth'
        .body[1]
         0] Pass - 3,16..3,20
      2] Expr - 5,4..5,5
        .value Name 'j' Load - 5,4..5,5
      3] FunctionDef - 6,4..6,24
        .name 'postmeth'
        .body[1]
         0] Pass - 6,20..6,24
'''),

('body[0]', 2, 3, None, {}, ('exec', r'''
class cls:
    def premeth(): pass
    # pre
    i ; j # post
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
class cls:
    def premeth(): pass
    # pre
    i

    def meth(): pass

    def postmeth(): pass
''', r'''
class cls:
    def premeth(): pass
    # pre
    i

    def meth():
        pass

    def postmeth(): pass
''', r'''
Module - ROOT 0,0..7,24
  .body[1]
   0] ClassDef - 0,0..7,24
     .name 'cls'
     .body[4]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
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
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
    def premeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
if 1:
    def premeth(): pass


    def meth(): pass
''', r'''
if 1:
    def premeth(): pass


    def meth():
        pass
''', r'''
Module - ROOT 0,0..4,20
  .body[1]
   0] If - 0,0..4,20
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] FunctionDef - 1,4..1,23
        .name 'premeth'
        .body[1]
         0] Pass - 1,19..1,23
      1] FunctionDef - 4,4..4,20
        .name 'meth'
        .body[1]
         0] Pass - 4,16..4,20
'''),

('body[0]', 0, 0, None, {}, ('exec', r'''
if 1:
    def postmeth(): pass
'''), (None,
r'''def meth(): pass'''), r'''
if 1:
    def meth(): pass


    def postmeth(): pass
''', r'''
if 1:
    def meth():
        pass


    def postmeth(): pass
''', r'''
Module - ROOT 0,0..4,24
  .body[1]
   0] If - 0,0..4,24
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] FunctionDef - 1,4..1,20
        .name 'meth'
        .body[1]
         0] Pass - 1,16..1,20
      1] FunctionDef - 4,4..4,24
        .name 'postmeth'
        .body[1]
         0] Pass - 4,20..4,24
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
def f():
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
def f():
    i

    def g(): pass

    j
''', r'''
def f():
    i

    def g():
        pass

    j
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] FunctionDef - 0,0..5,5
     .name 'f'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'g'
        .body[1]
         0] Pass - 3,13..3,17
      2] Expr - 5,4..5,5
        .value Name 'j' Load - 5,4..5,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
async def f():
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
async def f():
    i

    def g(): pass

    j
''', r'''
async def f():
    i

    def g():
        pass

    j
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] AsyncFunctionDef - 0,0..5,5
     .name 'f'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'g'
        .body[1]
         0] Pass - 3,13..3,17
      2] Expr - 5,4..5,5
        .value Name 'j' Load - 5,4..5,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
class cls:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
class cls:
    i

    def g(): pass

    j
''', r'''
class cls:
    i

    def g():
        pass

    j
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] ClassDef - 0,0..5,5
     .name 'cls'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'g'
        .body[1]
         0] Pass - 3,13..3,17
      2] Expr - 5,4..5,5
        .value Name 'j' Load - 5,4..5,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
for a in b:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
for a in b:
    i


    def g(): pass


    j
''', r'''
for a in b:
    i


    def g():
        pass


    j
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] For - 0,0..7,5
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'b' Load - 0,9..0,10
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'g'
        .body[1]
         0] Pass - 4,13..4,17
      2] Expr - 7,4..7,5
        .value Name 'j' Load - 7,4..7,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
async for a in b:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
async for a in b:
    i


    def g(): pass


    j
''', r'''
async for a in b:
    i


    def g():
        pass


    j
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] AsyncFor - 0,0..7,5
     .target Name 'a' Store - 0,10..0,11
     .iter Name 'b' Load - 0,15..0,16
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'g'
        .body[1]
         0] Pass - 4,13..4,17
      2] Expr - 7,4..7,5
        .value Name 'j' Load - 7,4..7,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
while a:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
while a:
    i


    def g(): pass


    j
''', r'''
while a:
    i


    def g():
        pass


    j
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] While - 0,0..7,5
     .test Name 'a' Load - 0,6..0,7
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'g'
        .body[1]
         0] Pass - 4,13..4,17
      2] Expr - 7,4..7,5
        .value Name 'j' Load - 7,4..7,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
if a:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
if a:
    i


    def g(): pass


    j
''', r'''
if a:
    i


    def g():
        pass


    j
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] If - 0,0..7,5
     .test Name 'a' Load - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'g'
        .body[1]
         0] Pass - 4,13..4,17
      2] Expr - 7,4..7,5
        .value Name 'j' Load - 7,4..7,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
with a:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
with a:
    i


    def g(): pass


    j
''', r'''
with a:
    i


    def g():
        pass


    j
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] With - 0,0..7,5
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'g'
        .body[1]
         0] Pass - 4,13..4,17
      2] Expr - 7,4..7,5
        .value Name 'j' Load - 7,4..7,5
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
async with a:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
async with a:
    i


    def g(): pass


    j
''', r'''
async with a:
    i


    def g():
        pass


    j
''', r'''
Module - ROOT 0,0..7,5
  .body[1]
   0] AsyncWith - 0,0..7,5
     .items[1]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'g'
        .body[1]
         0] Pass - 4,13..4,17
      2] Expr - 7,4..7,5
        .value Name 'j' Load - 7,4..7,5
'''),

('body[0].cases[0]', 1, 1, None, {}, ('exec', r'''
match a:
    case b:
        i
        j
'''), (None,
r'''def g(): pass'''), r'''
match a:
    case b:
        i


        def g(): pass


        j
''', r'''
match a:
    case b:
        i


        def g():
            pass


        j
''', r'''
Module - ROOT 0,0..8,9
  .body[1]
   0] Match - 0,0..8,9
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,4..8,9
        .pattern MatchAs - 1,9..1,10
          .name 'b'
        .body[3]
         0] Expr - 2,8..2,9
           .value Name 'i' Load - 2,8..2,9
         1] FunctionDef - 5,8..5,21
           .name 'g'
           .body[1]
            0] Pass - 5,17..5,21
         2] Expr - 8,8..8,9
           .value Name 'j' Load - 8,8..8,9
'''),

('body[0]', 1, 1, None, {}, ('exec', r'''
try:
    i
    j
finally:
    pass
'''), (None,
r'''def g(): pass'''), r'''
try:
    i


    def g(): pass


    j
finally:
    pass
''', r'''
try:
    i


    def g():
        pass


    j
finally:
    pass
''', r'''
Module - ROOT 0,0..9,8
  .body[1]
   0] Try - 0,0..9,8
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'g'
        .body[1]
         0] Pass - 4,13..4,17
      2] Expr - 7,4..7,5
        .value Name 'j' Load - 7,4..7,5
     .finalbody[1]
      0] Pass - 9,4..9,8
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
def f():
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
def f():
    i
    def g(): pass
    j
''', r'''
def f():
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] FunctionDef - 0,0..3,5
     .name 'f'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
async def f():
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
async def f():
    i
    def g(): pass
    j
''', r'''
async def f():
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] AsyncFunctionDef - 0,0..3,5
     .name 'f'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
class cls:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
class cls:
    i
    def g(): pass
    j
''', r'''
class cls:
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] ClassDef - 0,0..3,5
     .name 'cls'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
for a in b:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
for a in b:
    i
    def g(): pass
    j
''', r'''
for a in b:
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] For - 0,0..3,5
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'b' Load - 0,9..0,10
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
async for a in b:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
async for a in b:
    i
    def g(): pass
    j
''', r'''
async for a in b:
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] AsyncFor - 0,0..3,5
     .target Name 'a' Store - 0,10..0,11
     .iter Name 'b' Load - 0,15..0,16
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
while a:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
while a:
    i
    def g(): pass
    j
''', r'''
while a:
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] While - 0,0..3,5
     .test Name 'a' Load - 0,6..0,7
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if a:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
if a:
    i
    def g(): pass
    j
''', r'''
if a:
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Name 'a' Load - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
with a:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
with a:
    i
    def g(): pass
    j
''', r'''
with a:
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] With - 0,0..3,5
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
async with a:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
async with a:
    i
    def g(): pass
    j
''', r'''
async with a:
    i
    def g():
        pass
    j
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] AsyncWith - 0,0..3,5
     .items[1]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
'''),

('body[0].cases[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
match a:
    case b:
        i
        j
'''), (None,
r'''def g(): pass'''), r'''
match a:
    case b:
        i
        def g(): pass
        j
''', r'''
match a:
    case b:
        i
        def g():
            pass
        j
''', r'''
Module - ROOT 0,0..4,9
  .body[1]
   0] Match - 0,0..4,9
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,4..4,9
        .pattern MatchAs - 1,9..1,10
          .name 'b'
        .body[3]
         0] Expr - 2,8..2,9
           .value Name 'i' Load - 2,8..2,9
         1] FunctionDef - 3,8..3,21
           .name 'g'
           .body[1]
            0] Pass - 3,17..3,21
         2] Expr - 4,8..4,9
           .value Name 'j' Load - 4,8..4,9
'''),

('body[0]', 1, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
try:
    i
    j
finally:
    pass
'''), (None,
r'''def g(): pass'''), r'''
try:
    i
    def g(): pass
    j
finally:
    pass
''', r'''
try:
    i
    def g():
        pass
    j
finally:
    pass
''', r'''
Module - ROOT 0,0..5,8
  .body[1]
   0] Try - 0,0..5,8
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 2,4..2,17
        .name 'g'
        .body[1]
         0] Pass - 2,13..2,17
      2] Expr - 3,4..3,5
        .value Name 'j' Load - 3,4..3,5
     .finalbody[1]
      0] Pass - 5,4..5,8
'''),

('body[0]', 1, 1, None, {'pep8space': 1}, ('exec', r'''
if 1:
    i
    j
'''), (None,
r'''def g(): pass'''), r'''
if 1:
    i

    def g(): pass

    j
''', r'''
if 1:
    i

    def g():
        pass

    j
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] If - 0,0..5,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'g'
        .body[1]
         0] Pass - 3,13..3,17
      2] Expr - 5,4..5,5
        .value Name 'j' Load - 5,4..5,5
'''),

('', 1, 2, None, {}, ('exec',
r'''i ; j ; k'''), (None,
r'''l'''), r'''
i
l
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i ; \
 j \
 ; k
'''), (None,
r'''l'''), r'''
i
l
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; j ; \
 k
'''), (None,
r'''l'''), r'''
i
l
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; \
 j \
 ; \
 k
'''), (None,
r'''l'''), r'''
i
l
k
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'l' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'k' Load - 2,0..2,1
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i ; j ; k
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i ; \
 j ; \
 k
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i \
 ; j ; \
 k
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i \
 ; \
 j \
 ; \
 k
'''), (None,
r'''l'''), r'''
if 1:
    i
    l
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 2,4..2,5
        .value Name 'l' Load - 2,4..2,5
      2] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
'''),

('', 1, 2, None, {}, ('exec',
r'''i ; j ; k'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass


k
''', r'''
i


def f():
    pass


k
''', r'''
Module - ROOT 0,0..6,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
   2] Expr - 6,0..6,1
     .value Name 'k' Load - 6,0..6,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i ; \
 j \
 ; k
'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass


k
''', r'''
i


def f():
    pass


k
''', r'''
Module - ROOT 0,0..6,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
   2] Expr - 6,0..6,1
     .value Name 'k' Load - 6,0..6,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; j ; \
 k
'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass


k
''', r'''
i


def f():
    pass


k
''', r'''
Module - ROOT 0,0..6,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
   2] Expr - 6,0..6,1
     .value Name 'k' Load - 6,0..6,1
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; \
 j \
 ; \
 k
'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass


k
''', r'''
i


def f():
    pass


k
''', r'''
Module - ROOT 0,0..6,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
   2] Expr - 6,0..6,1
     .value Name 'k' Load - 6,0..6,1
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i ; j ; k
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass

    k
''', r'''
class cls:
    i

    def f():
        pass

    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] ClassDef - 0,0..5,5
     .name 'cls'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
      2] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i ; \
 j ; \
 k
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass

    k
''', r'''
class cls:
    i

    def f():
        pass

    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] ClassDef - 0,0..5,5
     .name 'cls'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
      2] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i \
 ; j ; \
 k
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass

    k
''', r'''
class cls:
    i

    def f():
        pass

    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] ClassDef - 0,0..5,5
     .name 'cls'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
      2] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i \
 ; \
 j \
 ; \
 k
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass

    k
''', r'''
class cls:
    i

    def f():
        pass

    k
''', r'''
Module - ROOT 0,0..5,5
  .body[1]
   0] ClassDef - 0,0..5,5
     .name 'cls'
     .body[3]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
      2] Expr - 5,4..5,5
        .value Name 'k' Load - 5,4..5,5
'''),

('', 1, 2, None, {}, ('exec',
r'''i ; j ;'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass
''', r'''
i


def f():
    pass
''', r'''
Module - ROOT 0,0..3,13
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
'''),

('', 1, 2, None, {}, ('exec', r'''
i ; \
 j \
 ;
'''), (None,
r'''def f(): pass'''), r'''
i ;


def f(): pass
''', r'''
i ;


def f():
    pass
''', r'''
Module - ROOT 0,0..3,13
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; j ;
'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass
''', r'''
i


def f():
    pass
''', r'''
Module - ROOT 0,0..3,13
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; \
 j \
 ;
'''), (None,
r'''def f(): pass'''), r'''
i \
 ;


def f(): pass
''', r'''
i \
 ;


def f():
    pass
''', r'''
Module - ROOT 0,0..4,13
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 4,0..4,13
     .name 'f'
     .body[1]
      0] Pass - 4,9..4,13
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i ; j ;
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass
''', r'''
class cls:
    i

    def f():
        pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] ClassDef - 0,0..3,17
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i ; \
 j ;
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i ;

    def f(): pass
''', r'''
class cls:
    i ;

    def f():
        pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] ClassDef - 0,0..3,17
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i \
 ; j ;
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass
''', r'''
class cls:
    i

    def f():
        pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] ClassDef - 0,0..3,17
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i \
 ; \
 j \
 ;
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i \
 ;

    def f(): pass
''', r'''
class cls:
    i \
 ;

    def f():
        pass
''', r'''
Module - ROOT 0,0..4,17
  .body[1]
   0] ClassDef - 0,0..4,17
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'f'
        .body[1]
         0] Pass - 4,13..4,17
'''),

('', 1, 2, None, {}, ('exec',
r'''i ; j ;  # post'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass
''', r'''
i


def f():
    pass
''', r'''
Module - ROOT 0,0..3,13
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
'''),

('', 1, 2, None, {}, ('exec', r'''
i ; \
 j \
 ;  # post
'''), (None,
r'''def f(): pass'''), r'''
i ;


def f(): pass
 # post
''', r'''
i ;


def f():
    pass
 # post
''', r'''
Module - ROOT 0,0..4,7
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; j ;  # post
'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass
''', r'''
i


def f():
    pass
''', r'''
Module - ROOT 0,0..3,13
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 3,0..3,13
     .name 'f'
     .body[1]
      0] Pass - 3,9..3,13
'''),

('', 1, 2, None, {}, ('exec', r'''
i \
 ; \
 j \
 ;  # post
'''), (None,
r'''def f(): pass'''), r'''
i \
 ;


def f(): pass
 # post
''', r'''
i \
 ;


def f():
    pass
 # post
''', r'''
Module - ROOT 0,0..5,7
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] FunctionDef - 4,0..4,13
     .name 'f'
     .body[1]
      0] Pass - 4,9..4,13
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i ; j ;  # post
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass
''', r'''
class cls:
    i

    def f():
        pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] ClassDef - 0,0..3,17
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i ; \
 j ;  # post
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass
''', r'''
class cls:
    i

    def f():
        pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] ClassDef - 0,0..3,17
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i \
 ; j ;  # post
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i

    def f(): pass
''', r'''
class cls:
    i

    def f():
        pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] ClassDef - 0,0..3,17
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 3,4..3,17
        .name 'f'
        .body[1]
         0] Pass - 3,13..3,17
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i \
 ; \
 j \
 ;  # post
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i \
 ;

    def f(): pass
 # post
''', r'''
class cls:
    i \
 ;

    def f():
        pass
 # post
''', r'''
Module - ROOT 0,0..5,7
  .body[1]
   0] ClassDef - 0,0..4,17
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] FunctionDef - 4,4..4,17
        .name 'f'
        .body[1]
         0] Pass - 4,13..4,17
'''),

('body[0]', 0, 1, 'orelse', {}, ('exec', r'''
if 1: pass
elif 2:
    pass
'''), (None,
r'''break'''), r'''
if 1: pass
else:
    break
''', r'''
Module - ROOT 0,0..2,9
  .body[1]
   0] If - 0,0..2,9
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Break - 2,4..2,9
'''),

('body[0]', 0, 1, 'orelse', {'elif_': False}, ('exec', r'''
if 1: pass
elif 2:
    pass
'''), (None,
r'''if 3: break'''), r'''
if 1: pass
else:
    if 3: break
''', r'''
if 1: pass
else:
    if 3:
        break
''', r'''
Module - ROOT 0,0..2,15
  .body[1]
   0] If - 0,0..2,15
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] If - 2,4..2,15
        .test Constant 3 - 2,7..2,8
        .body[1]
         0] Break - 2,10..2,15
'''),

('body[0]', 0, 1, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
if 1: pass
elif 2:
    pass
'''), (None,
r'''if 3: break'''), r'''
if 1: pass
elif 3: break
''', r'''
if 1: pass
elif 3:
    break
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] If - 0,0..1,13
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] If - 1,0..1,13
        .test Constant 3 - 1,5..1,6
        .body[1]
         0] Break - 1,8..1,13
'''),

('body[0]', 0, 1, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
if 1: pass
else:
    pass
'''), (None,
r'''if 3: break'''), r'''
if 1: pass
elif 3: break
''', r'''
if 1: pass
elif 3:
    break
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] If - 0,0..1,13
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] If - 1,0..1,13
        .test Constant 3 - 1,5..1,6
        .body[1]
         0] Break - 1,8..1,13
'''),

('body[0].body[0]', 0, 1, 'orelse', {}, ('exec', r'''
class cls:
    if 1: pass
    elif 2:
        pass
'''), (None,
r'''break'''), r'''
class cls:
    if 1: pass
    else:
        break
''', r'''
Module - ROOT 0,0..3,13
  .body[1]
   0] ClassDef - 0,0..3,13
     .name 'cls'
     .body[1]
      0] If - 1,4..3,13
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] Break - 3,8..3,13
'''),

('body[0].body[0]', 0, 1, 'orelse', {'elif_': False}, ('exec', r'''
class cls:
    if 1: pass
    elif 2:
        pass
'''), (None,
r'''if 3: break'''), r'''
class cls:
    if 1: pass
    else:
        if 3: break
''', r'''
class cls:
    if 1: pass
    else:
        if 3:
            break
''', r'''
Module - ROOT 0,0..3,19
  .body[1]
   0] ClassDef - 0,0..3,19
     .name 'cls'
     .body[1]
      0] If - 1,4..3,19
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 3,8..3,19
           .test Constant 3 - 3,11..3,12
           .body[1]
            0] Break - 3,14..3,19
'''),

('body[0].body[0]', 0, 1, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
class cls:
    if 1: pass
    elif 2:
        pass
'''), (None,
r'''if 3: break'''), r'''
class cls:
    if 1: pass
    elif 3: break
''', r'''
class cls:
    if 1: pass
    elif 3:
        break
''', r'''
Module - ROOT 0,0..2,17
  .body[1]
   0] ClassDef - 0,0..2,17
     .name 'cls'
     .body[1]
      0] If - 1,4..2,17
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 2,4..2,17
           .test Constant 3 - 2,9..2,10
           .body[1]
            0] Break - 2,12..2,17
'''),

('body[0].body[0]', 0, 1, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
class cls:
    if 1: pass
    else:
        pass
'''), (None,
r'''if 3: break'''), r'''
class cls:
    if 1: pass
    elif 3: break
''', r'''
class cls:
    if 1: pass
    elif 3:
        break
''', r'''
Module - ROOT 0,0..2,17
  .body[1]
   0] ClassDef - 0,0..2,17
     .name 'cls'
     .body[1]
      0] If - 1,4..2,17
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 2,4..2,17
           .test Constant 3 - 2,9..2,10
           .body[1]
            0] Break - 2,12..2,17
'''),

('body[0]', 0, 1, 'orelse', {'elif_': False}, ('exec', r'''
if 1: pass
elif 2:
    pass
'''), (None, r'''
if 3: break
else:
    continue
'''), r'''
if 1: pass
else:
    if 3: break
    else:
        continue
''', r'''
if 1: pass
else:
    if 3:
        break
    else:
        continue
''', r'''
Module - ROOT 0,0..4,16
  .body[1]
   0] If - 0,0..4,16
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] If - 2,4..4,16
        .test Constant 3 - 2,7..2,8
        .body[1]
         0] Break - 2,10..2,15
        .orelse[1]
         0] Continue - 4,8..4,16
'''),

('body[0]', 0, 1, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
if 1: pass
elif 2:
    pass
'''), (None, r'''
if 3: break
else:
    continue
'''), r'''
if 1: pass
elif 3: break
else:
    continue
''', r'''
if 1: pass
elif 3:
    break
else:
    continue
''', r'''
Module - ROOT 0,0..3,12
  .body[1]
   0] If - 0,0..3,12
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] If - 1,0..3,12
        .test Constant 3 - 1,5..1,6
        .body[1]
         0] Break - 1,8..1,13
        .orelse[1]
         0] Continue - 3,4..3,12
'''),

('body[0].orelse[0]', 0, 0, 'orelse', {'elif_': False}, ('exec', r'''
if 1: pass
elif 2:
    pass
'''), (None, r'''
if 3: break
else:
    continue
'''), r'''
if 1: pass
elif 2:
    pass
else:
    if 3: break
    else:
        continue
''', r'''
if 1: pass
elif 2:
    pass
else:
    if 3:
        break
    else:
        continue
''', r'''
Module - ROOT 0,0..6,16
  .body[1]
   0] If - 0,0..6,16
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] If - 1,0..6,16
        .test Constant 2 - 1,5..1,6
        .body[1]
         0] Pass - 2,4..2,8
        .orelse[1]
         0] If - 4,4..6,16
           .test Constant 3 - 4,7..4,8
           .body[1]
            0] Break - 4,10..4,15
           .orelse[1]
            0] Continue - 6,8..6,16
'''),

('body[0].orelse[0]', 0, 0, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
if 1: pass
elif 2:
    pass
'''), (None, r'''
if 3: break
else:
    continue
'''), r'''
if 1: pass
elif 2:
    pass
elif 3: break
else:
    continue
''', r'''
if 1: pass
elif 2:
    pass
elif 3:
    break
else:
    continue
''', r'''
Module - ROOT 0,0..5,12
  .body[1]
   0] If - 0,0..5,12
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] If - 1,0..5,12
        .test Constant 2 - 1,5..1,6
        .body[1]
         0] Pass - 2,4..2,8
        .orelse[1]
         0] If - 3,0..5,12
           .test Constant 3 - 3,5..3,6
           .body[1]
            0] Break - 3,8..3,13
           .orelse[1]
            0] Continue - 5,4..5,12
'''),

('body[0].body[0]', 0, 1, 'orelse', {'elif_': False}, ('exec', r'''
class cls:
    if 1: pass
    elif 2:
        pass
'''), (None, r'''
if 3: break
else:
    continue
'''), r'''
class cls:
    if 1: pass
    else:
        if 3: break
        else:
            continue
''', r'''
class cls:
    if 1: pass
    else:
        if 3:
            break
        else:
            continue
''', r'''
Module - ROOT 0,0..5,20
  .body[1]
   0] ClassDef - 0,0..5,20
     .name 'cls'
     .body[1]
      0] If - 1,4..5,20
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 3,8..5,20
           .test Constant 3 - 3,11..3,12
           .body[1]
            0] Break - 3,14..3,19
           .orelse[1]
            0] Continue - 5,12..5,20
'''),

('body[0].body[0]', 0, 1, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
class cls:
    if 1: pass
    elif 2:
        pass
'''), (None, r'''
if 3: break
else:
    continue
'''), r'''
class cls:
    if 1: pass
    elif 3: break
    else:
        continue
''', r'''
class cls:
    if 1: pass
    elif 3:
        break
    else:
        continue
''', r'''
Module - ROOT 0,0..4,16
  .body[1]
   0] ClassDef - 0,0..4,16
     .name 'cls'
     .body[1]
      0] If - 1,4..4,16
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 2,4..4,16
           .test Constant 3 - 2,9..2,10
           .body[1]
            0] Break - 2,12..2,17
           .orelse[1]
            0] Continue - 4,8..4,16
'''),

('body[0].body[0].orelse[0]', 0, 0, 'orelse', {'elif_': False}, ('exec', r'''
class cls:
    if 1: pass
    elif 2:
        pass
'''), (None, r'''
if 3: break
else:
    continue
'''), r'''
class cls:
    if 1: pass
    elif 2:
        pass
    else:
        if 3: break
        else:
            continue
''', r'''
class cls:
    if 1: pass
    elif 2:
        pass
    else:
        if 3:
            break
        else:
            continue
''', r'''
Module - ROOT 0,0..7,20
  .body[1]
   0] ClassDef - 0,0..7,20
     .name 'cls'
     .body[1]
      0] If - 1,4..7,20
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 2,4..7,20
           .test Constant 2 - 2,9..2,10
           .body[1]
            0] Pass - 3,8..3,12
           .orelse[1]
            0] If - 5,8..7,20
              .test Constant 3 - 5,11..5,12
              .body[1]
               0] Break - 5,14..5,19
              .orelse[1]
               0] Continue - 7,12..7,20
'''),

('body[0].body[0].orelse[0]', 0, 0, 'orelse', {'trivia': (False, False), 'pep8space': False, 'elif_': True}, ('exec', r'''
class cls:
    if 1: pass
    elif 2:
        pass
'''), (None, r'''
if 3: break
else:
    continue
'''), r'''
class cls:
    if 1: pass
    elif 2:
        pass
    elif 3: break
    else:
        continue
''', r'''
class cls:
    if 1: pass
    elif 2:
        pass
    elif 3:
        break
    else:
        continue
''', r'''
Module - ROOT 0,0..6,16
  .body[1]
   0] ClassDef - 0,0..6,16
     .name 'cls'
     .body[1]
      0] If - 1,4..6,16
        .test Constant 1 - 1,7..1,8
        .body[1]
         0] Pass - 1,10..1,14
        .orelse[1]
         0] If - 2,4..6,16
           .test Constant 2 - 2,9..2,10
           .body[1]
            0] Pass - 3,8..3,12
           .orelse[1]
            0] If - 4,4..6,16
              .test Constant 3 - 4,9..4,10
              .body[1]
               0] Break - 4,12..4,17
              .orelse[1]
               0] Continue - 6,8..6,16
'''),

('body[0]', 0, 0, 'orelse', {}, ('exec', r'''
if 1:
    pass;
'''), (None,
r'''i'''), r'''
if 1:
    pass;
else:
    i
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 1,4..1,8
     .orelse[1]
      0] Expr - 3,4..3,5
        .value Name 'i' Load - 3,4..3,5
'''),

('body[0]', 0, 0, 'orelse', {}, ('exec', r'''
try:
    continue
except:
    pass;
finally:
    pass
'''), (None,
r'''i'''), r'''
try:
    continue
except:
    pass;
else:
    i
finally:
    pass
''', r'''
Module - ROOT 0,0..7,8
  .body[1]
   0] Try - 0,0..7,8
     .body[1]
      0] Continue - 1,4..1,12
     .handlers[1]
      0] ExceptHandler - 2,0..3,9
        .body[1]
         0] Pass - 3,4..3,8
     .orelse[1]
      0] Expr - 5,4..5,5
        .value Name 'i' Load - 5,4..5,5
     .finalbody[1]
      0] Pass - 7,4..7,8
'''),
],

'old_exprlike': [  # ................................................................................

('body[0].value', 0, 1, None, {}, ('exec', r'''
{
    a: 1
}
'''), (None,
r'''{}'''), r'''
{
}
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value Dict - 0,0..1,1
'''),

('body[0].value', 0, 2, None, {}, ('exec',
r'''1, 2'''), (None, r'''
(

   )
'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .ctx Load
'''),

('body[0].body[0].value', 0, 2, None, {'norm': True}, ('exec', r'''
if 1:
  {1, 2}
'''), (None, r'''
(

   )
'''), r'''
if 1:
  {*()}
''', r'''
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
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
{
    a: 1
}
'''), (None, r'''
{
}
'''), r'''
{
}
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value Dict - 0,0..1,1
'''),

('body[0].value', 0, 1, None, {}, ('exec',
r'''{a: 1}'''), (None,
r'''{}'''),
r'''{}''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Dict - 0,0..0,2
'''),

('body[0].value', 0, 1, None, {}, ('exec',
r'''{a: 1}'''), (None, r'''
{
}
'''),
r'''{}''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Dict - 0,0..0,2
'''),

('body[0].value', 1, 2, None, {}, ('exec',
r'''(1, 2)'''), (None,
r'''()'''),
r'''(1,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Constant 1 - 0,1..0,2
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec',
r'''1, 2'''), (None,
r'''()'''),
r'''1,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Constant 1 - 0,0..0,1
       .ctx Load
'''),

('body[0].value', 0, 2, None, {}, ('exec',
r'''1, 2'''), (None,
r'''()'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .ctx Load
'''),

('body[0].value', 1, 2, None, {'norm': True}, ('exec',
r'''(1, 2)'''), (None,
r'''{*()}'''),
r'''(1,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Constant 1 - 0,1..0,2
       .ctx Load
'''),

('body[0].value', 1, 2, None, {'norm': True}, ('exec',
r'''1, 2'''), (None,
r'''{*()}'''),
r'''1,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Constant 1 - 0,0..0,1
       .ctx Load
'''),

('body[0].value', 0, 2, None, {'norm': True}, ('exec',
r'''1, 2'''), (None,
r'''{*()}'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .ctx Load
'''),

('body[0].value', 0, 2, None, {}, ('exec', r'''
[            # hello
    1, 2, 3
]
'''), (None,
r'''()'''), r'''
[            # hello
    3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[1]
        0] Constant 3 - 1,4..1,5
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    1, b, c
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a,
    1, c
]
''', r'''
[            # hello
    a, 1, c
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 1 - 2,4..2,5
        2] Name 'c' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    2, b, c
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 2 - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, 2, c
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    3,
    b, c
]
''', r'''
[            # hello
    3, b, c
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 3 - 1,4..1,5
        1] Name 'b' Load - 2,4..2,5
        2] Name 'c' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, 3,
    c
]
''', r'''
[            # hello
    a, 3, c
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 3 - 1,7..1,8
        2] Name 'c' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec',
'[            # hello\n    a, b, c   \n]'), (None, r'''
[3
]
'''), r'''
[            # hello
    a, b, 3
]
''',
'[            # hello\n    a, b, 3   \n]', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    1, b, c,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a,
    1, c,
]
''', r'''
[            # hello
    a, 1, c,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 1 - 2,4..2,5
        2] Name 'c' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    2, b, c,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 2 - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, 2, c,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    3,
    b, c,
]
''', r'''
[            # hello
    3, b, c,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 3 - 1,4..1,5
        1] Name 'b' Load - 2,4..2,5
        2] Name 'c' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, 3,
    c,
]
''', r'''
[            # hello
    a, 3, c,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 3 - 1,7..1,8
        2] Name 'c' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    1, b, c
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a,
    1, c
]
''', r'''
[            # hello
    a, 1, c
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 1 - 2,4..2,5
        2] Name 'c' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    2, b, c
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 2 - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, 2, c
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    3,
    b, c
]
''', r'''
[            # hello
    3, b, c
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 3 - 1,4..1,5
        1] Name 'b' Load - 2,4..2,5
        2] Name 'c' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, 3,
    c
]
''', r'''
[            # hello
    a, 3, c
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 3 - 1,7..1,8
        2] Name 'c' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    1, b, c,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a,
    1, c,
]
''', r'''
[            # hello
    a, 1, c,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 1 - 2,4..2,5
        2] Name 'c' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    2, b, c,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 2 - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, 2, c,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Name 'c' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    3,
    b, c,
]
''', r'''
[            # hello
    3, b, c,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 3 - 1,4..1,5
        1] Name 'b' Load - 2,4..2,5
        2] Name 'c' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, 3,
    c,
]
''', r'''
[            # hello
    a, 3, c,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 3 - 1,7..1,8
        2] Name 'c' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c,
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[
    1  # comment
]
'''), r'''
[            # hello
    a, b,
    1  # comment
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[2  # comment
]
'''), r'''
[            # hello
    a, b, 2  # comment
]
''', r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[3  # comment
]
'''), r'''
[            # hello
    a, b, 3  # comment
]
''', r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[
    1,  # comment
]
'''), r'''
[            # hello
    a, b,
    1,  # comment
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[2,  # comment
]
'''), r'''
[            # hello
    a, b, 2,  # comment
]
''', r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    a, b, c  # blah
]
'''), (None, r'''
[3,  # comment
]
'''), r'''
[            # hello
    a, b, 3,  # comment
]
''', r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    1, a, b
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Name 'a' Load - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a,
    1, b
]
''', r'''
[            # hello
    a, 1, b
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 1 - 2,4..2,5
        2] Name 'b' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    2, a, b
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 2 - 1,4..1,5
        1] Name 'a' Load - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, 2, b
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    3,
    a, b
]
''', r'''
[            # hello
    3, a, b
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 3 - 1,4..1,5
        1] Name 'a' Load - 2,4..2,5
        2] Name 'b' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, 3,
    b
]
''', r'''
[            # hello
    a, 3, b
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 3 - 1,7..1,8
        2] Name 'b' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    1, a, b,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Name 'a' Load - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a,
    1, b,
]
''', r'''
[            # hello
    a, 1, b,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 1 - 2,4..2,5
        2] Name 'b' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    2, a, b,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 2 - 1,4..1,5
        1] Name 'a' Load - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, 2, b,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    3,
    a, b,
]
''', r'''
[            # hello
    3, a, b,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 3 - 1,4..1,5
        1] Name 'a' Load - 2,4..2,5
        2] Name 'b' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, 3,
    b,
]
''', r'''
[            # hello
    a, 3, b,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 3 - 1,7..1,8
        2] Name 'b' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    1, a, b
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Name 'a' Load - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a,
    1, b
]
''', r'''
[            # hello
    a, 1, b
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 1 - 2,4..2,5
        2] Name 'b' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    2, a, b
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 2 - 1,4..1,5
        1] Name 'a' Load - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, 2, b
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    3,
    a, b
]
''', r'''
[            # hello
    3, a, b
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 3 - 1,4..1,5
        1] Name 'a' Load - 2,4..2,5
        2] Name 'b' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, 3,
    b
]
''', r'''
[            # hello
    a, 3, b
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 3 - 1,7..1,8
        2] Name 'b' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    1, a, b,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Name 'a' Load - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a,
    1, b,
]
''', r'''
[            # hello
    a, 1, b,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 1 - 2,4..2,5
        2] Name 'b' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    2, a, b,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 2 - 1,4..1,5
        1] Name 'a' Load - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, 2, b,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Name 'b' Load - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    3,
    a, b,
]
''', r'''
[            # hello
    3, a, b,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 3 - 1,4..1,5
        1] Name 'a' Load - 2,4..2,5
        2] Name 'b' Load - 2,7..2,8
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, 3,
    b,
]
''', r'''
[            # hello
    a, 3, b,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Constant 3 - 1,7..1,8
        2] Name 'b' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b,
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[
    1]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None,
r'''[2]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[3
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[
    1,]
'''), r'''
[            # hello
    a, b,
    1
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None,
r'''[2,]'''), r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[3,
]
'''), r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[
    1  # comment
]
'''), r'''
[            # hello
    a, b,
    1  # comment
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[2  # comment
]
'''), r'''
[            # hello
    a, b, 2  # comment
]
''', r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[3  # comment
]
'''), r'''
[            # hello
    a, b, 3  # comment
]
''', r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[
    1,  # comment
]
'''), r'''
[            # hello
    a, b,
    1,  # comment
]
''', r'''
[            # hello
    a, b, 1
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 1 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[2,  # comment
]
'''), r'''
[            # hello
    a, b, 2,  # comment
]
''', r'''
[            # hello
    a, b, 2
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 2 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec', r'''
[            # hello
    a, b  # blah
]
'''), (None, r'''
[3,  # comment
]
'''), r'''
[            # hello
    a, b, 3,  # comment
]
''', r'''
[            # hello
    a, b, 3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Name 'a' Load - 1,4..1,5
        1] Name 'b' Load - 1,7..1,8
        2] Constant 3 - 1,10..1,11
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
{
    'message': ('An open stream was garbage collected prior to '
                'establishing network connection; '
                'call "stream.close()" explicitly.')
}
'''), (None,
r'''{i: j}'''), r'''
{
    'message': ('An open stream was garbage collected prior to '
                'establishing network connection; '
                'call "stream.close()" explicitly.'), i: j
}
''', r'''
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
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
{
    1: 2,
    5: 6
}
'''), (None,
r'''{3: ("4")}'''), r'''
{
    1: 2,
    3: ("4"), 5: 6
}
''', r'''
{
    1: 2,
    3: '4', 5: 6
}
''', r'''
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
'''),

('body[0].value', 1, 1, None, {}, ('exec', r'''
[
    # order of patterns matters
    r'file, line (\\d+)',
    3,
]
'''), (None,
r'''(1, 2)'''), r'''
[
    # order of patterns matters
    r'file, line (\\d+)',
    1, 2, 3,
]
''', r'''
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
'''),

('body[0].value', 2, 3, None, {}, ('exec',
r'''(IndexError, KeyError, isinstance,)'''), (None,
r'''()'''),
r'''(IndexError, KeyError)''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value Tuple - 0,0..0,22
       .elts[2]
        0] Name 'IndexError' Load - 0,1..0,11
        1] Name 'KeyError' Load - 0,13..0,21
       .ctx Load
'''),

('body[0].targets[0]', 2, 2, None, {}, ('exec',
r'''[a, b] = c'''), (None,
r'''(d,)'''),
r'''[a, b, d] = c''', r'''
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
'''),

('body[0].value', 0, 1, None, {}, ('exec',
r'''stat_list,'''), (None, r'''
[ {-1: "stdname",
                   2: "cumulative"}[field[0]] ]
'''), r'''
{-1: "stdname",
                   2: "cumulative"}[field[0]],
''',
r'''{-1: 'stdname', 2: 'cumulative'}[field[0]],''', r'''
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
'''),

('body[0].iter', 1, 2, None, {}, ('exec', r'''
for a in a, b:
    pass
'''), (None, r'''
(
c,)
'''), r'''
for a in (a,
         c):
    pass
''', r'''
for a in a, c:
    pass
''', r'''
Module - ROOT 0,0..2,8
  .body[1]
   0] For - 0,0..2,8
     .target Name 'a' Store - 0,4..0,5
     .iter Tuple - 0,9..1,11
       .elts[2]
        0] Name 'a' Load - 0,10..0,11
        1] Name 'c' Load - 1,9..1,10
       .ctx Load
     .body[1]
      0] Pass - 2,4..2,8
'''),

('body[0].value', 0, 0, None, {}, ('exec',
r'''result = filename, headers'''), (None, r'''
(
c,)
'''), r'''
result = (
         c, filename, headers)
''',
r'''result = c, filename, headers''', r'''
Module - ROOT 0,0..1,30
  .body[1]
   0] Assign - 0,0..1,30
     .targets[1]
      0] Name 'result' Store - 0,0..0,6
     .value Tuple - 0,9..1,30
       .elts[3]
        0] Name 'c' Load - 1,9..1,10
        1] Name 'filename' Load - 1,12..1,20
        2] Name 'headers' Load - 1,22..1,29
       .ctx Load
'''),

('body[0].value', 0, 2, None, {}, ('exec',
r'''return (user if delim else None), host'''), (None,
r'''()'''),
r'''return ()''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Return - 0,0..0,9
     .value Tuple - 0,7..0,9
       .ctx Load
'''),

('body[0].value', 0, 2, None, {'norm': True}, ('exec',
r'''{1, 2}'''), (None,
r'''()'''),
r'''{*()}''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Set - 0,0..0,5
       .elts[1]
        0] Starred - 0,1..0,4
          .value Tuple - 0,2..0,4
            .ctx Load
          .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec',
r'''{*()}'''), (None,
r'''()'''),
r'''{*()}''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Set - 0,0..0,5
       .elts[1]
        0] Starred - 0,1..0,4
          .value Tuple - 0,2..0,4
            .ctx Load
          .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec',
r'''{*()}'''), (None,
r'''(1, 2)'''),
r'''{1, 2, *()}''', r'''
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
'''),

('body[0].value', 0, 0, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''a, 1, 2, 3,''', r'''
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
'''),

('body[0].value', 1, 1, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''1, a, 2, 3,''', r'''
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
'''),

('body[0].value', 2, 2, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''1, 2, a, 3,''', r'''
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
'''),

('body[0].value', 3, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''1, 2, 3, a''', r'''
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
'''),

('body[0].value', 0, 1, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''a, 2, 3,''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Tuple - 0,0..0,8
       .elts[3]
        0] Name 'a' Load - 0,0..0,1
        1] Constant 2 - 0,3..0,4
        2] Constant 3 - 0,6..0,7
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''1, a, 3,''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Tuple - 0,0..0,8
       .elts[3]
        0] Constant 1 - 0,0..0,1
        1] Name 'a' Load - 0,3..0,4
        2] Constant 3 - 0,6..0,7
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''1, 2, a''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Tuple - 0,0..0,7
       .elts[3]
        0] Constant 1 - 0,0..0,1
        1] Constant 2 - 0,3..0,4
        2] Name 'a' Load - 0,6..0,7
       .ctx Load
'''),

('body[0].value', 0, 2, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''a, 3,''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Tuple - 0,0..0,5
       .elts[2]
        0] Name 'a' Load - 0,0..0,1
        1] Constant 3 - 0,3..0,4
       .ctx Load
'''),

('body[0].value', 1, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''1, a''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[2]
        0] Constant 1 - 0,0..0,1
        1] Name 'a' Load - 0,3..0,4
       .ctx Load
'''),

('body[0].value', 0, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''a,'''),
r'''a,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Name 'a' Load - 0,0..0,1
       .ctx Load
'''),

('body[0].value', 0, 2, None, {}, ('exec', r'''
[            # hello
    1, 2, 3
]
'''), (None,
r'''**DEL**'''), r'''
[            # hello
    3
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[1]
        0] Constant 3 - 1,4..1,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''1, 2, 3,''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Tuple - 0,0..0,8
       .elts[3]
        0] Constant 1 - 0,0..0,1
        1] Constant 2 - 0,3..0,4
        2] Constant 3 - 0,6..0,7
       .ctx Load
'''),

('body[0].value', 1, 1, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''1, 2, 3,''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Tuple - 0,0..0,8
       .elts[3]
        0] Constant 1 - 0,0..0,1
        1] Constant 2 - 0,3..0,4
        2] Constant 3 - 0,6..0,7
       .ctx Load
'''),

('body[0].value', 2, 2, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''1, 2, 3,''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Tuple - 0,0..0,8
       .elts[3]
        0] Constant 1 - 0,0..0,1
        1] Constant 2 - 0,3..0,4
        2] Constant 3 - 0,6..0,7
       .ctx Load
'''),

('body[0].value', 3, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''1, 2, 3,''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Tuple - 0,0..0,8
       .elts[3]
        0] Constant 1 - 0,0..0,1
        1] Constant 2 - 0,3..0,4
        2] Constant 3 - 0,6..0,7
       .ctx Load
'''),

('body[0].value', 0, 1, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''2, 3,''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Tuple - 0,0..0,5
       .elts[2]
        0] Constant 2 - 0,0..0,1
        1] Constant 3 - 0,3..0,4
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''1, 3,''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Tuple - 0,0..0,5
       .elts[2]
        0] Constant 1 - 0,0..0,1
        1] Constant 3 - 0,3..0,4
       .ctx Load
'''),

('body[0].value', 2, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''1, 2''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[2]
        0] Constant 1 - 0,0..0,1
        1] Constant 2 - 0,3..0,4
       .ctx Load
'''),

('body[0].value', 0, 2, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''3,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Constant 3 - 0,0..0,1
       .ctx Load
'''),

('body[0].value', 1, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''1,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Constant 1 - 0,0..0,1
       .ctx Load
'''),

('body[0].value', 0, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .ctx Load
'''),

('body[0].body[0].value.elts[1]', 1, 2, None, {}, ('exec', r'''
if 1:
  [1,  [
        2, 3, 4]]
'''), (None, r'''
[5,
]
'''), r'''
if 1:
  [1,  [
        2, 5,
        4]]
''', r'''
if 1:
  [1,  [
        2, 5, 4]]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 2, 3, None, {}, ('exec', r'''
if 1:
  [1,  [
        2,
        3, 4]]
'''), (None, r'''
[5,
]
'''), r'''
if 1:
  [1,  [
        2,
        3, 5
       ]]
''', r'''
if 1:
  [1,  [
        2,
        3, 5]]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 0, 2, None, {}, ('exec', r'''
if 1:
  [1,  [
        2, 3, 4]]
'''), (None, r'''
[5,
]
'''), r'''
if 1:
  [1,  [
        5,
        4]]
''', r'''
if 1:
  [1,  [
        5, 4]]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 0, 3, None, {}, ('exec', r'''
if 1:
  [1,  [
        2,
        3, 4]]
'''), (None, r'''
[5,
]
'''), r'''
if 1:
  [1,  [
        5
       ]]
''', r'''
if 1:
  [1,  [
        5]]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 0, 3, None, {}, ('exec', r'''
if 1:
  [1,  [
        2,
        3, 4],
   6]
'''), (None, r'''
[5,
]
'''), r'''
if 1:
  [1,  [
        5
       ],
   6]
''', r'''
if 1:
  [1,  [
        5],
   6]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 1, 3, None, {}, ('exec', r'''
if 1:
  [1,  [
    2,
    3, 4],
   6]
'''), (None, r'''
[5,
]
'''), r'''
if 1:
  [1,  [
    2,
    5
    ],
   6]
''', r'''
if 1:
  [1,  [
    2,
    5],
   6]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 1, 2, None, {}, ('exec', r'''
if 1:
  [1,  {
        2:2, 3:3, 4:4}]
'''), (None, r'''
{5:5,
}
'''), r'''
if 1:
  [1,  {
        2:2, 5:5,
        4:4}]
''', r'''
if 1:
  [1,  {
        2:2, 5: 5, 4:4}]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 2, 3, None, {}, ('exec', r'''
if 1:
  [1,  {
        2:2,
        3:3, 4:4}]
'''), (None, r'''
{5:5,
}
'''), r'''
if 1:
  [1,  {
        2:2,
        3:3, 5:5
       }]
''', r'''
if 1:
  [1,  {
        2:2,
        3:3, 5: 5}]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 0, 2, None, {}, ('exec', r'''
if 1:
  [1,  {
        2:2, 3:3, 4:4}]
'''), (None, r'''
{5:5,
}
'''), r'''
if 1:
  [1,  {
        5:5,
        4:4}]
''', r'''
if 1:
  [1,  {
        5: 5, 4:4}]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 0, 3, None, {}, ('exec', r'''
if 1:
  [1,  {
        2:2,
        3:3, 4:4}]
'''), (None, r'''
{5:5,
}
'''), r'''
if 1:
  [1,  {
        5:5
       }]
''', r'''
if 1:
  [1,  {
        5: 5}]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 0, 3, None, {}, ('exec', r'''
if 1:
  [1,  {
        2:2,
        3:3, 4:4},
   6]
'''), (None, r'''
{5:5,
}
'''), r'''
if 1:
  [1,  {
        5:5
       },
   6]
''', r'''
if 1:
  [1,  {
        5: 5},
   6]
''', r'''
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
'''),

('body[0].body[0].value.elts[1]', 1, 3, None, {}, ('exec', r'''
if 1:
  [1,  {
    2:2,
    3:3, 4:4},
   6]
'''), (None, r'''
{5:5,
}
'''), r'''
if 1:
  [1,  {
    2:2,
    5:5
    },
   6]
''', r'''
if 1:
  [1,  {
    2:2,
    5: 5},
   6]
''', r'''
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
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[
    1,
    2,
    3,
]
'''), (None,
r'''**DEL**'''), r'''
[
    1,
    3,
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 3 - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 1, 2, None, {}, ('exec', r'''
[
    1,
    2,
    3,
]
'''), (None, r'''
[e,
    None]
'''), r'''
[
    1,
    e,
    None,
    3,
]
''', r'''
[
    1,
    e, None,
    3,
]
''', r'''
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
'''),

('body[0].value.slice', 1, 2, None, {}, ('exec',
r'''Tuple[(r & ((1 << 32) - 1)), (r & ((1 << 32) - 1))]'''), (None,
r'''()'''),
r'''Tuple[(r & ((1 << 32) - 1)),]''', r'''
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
'''),

('body[0].cases[0].pattern.patterns[0].patterns[0].patterns[0].patterns[0].pattern', 0, 2, None, {}, ('exec', r'''
match a:
    case list([({-0-0j: int(real=0+0j, imag=0-0j) | 1 |
                  (g, b) | (1) as z},)]): pass
'''), (None,
r'''**DEL**'''),
'match a:\n    case list([({-0-0j: \n                  (g, b) | (1) as z},)]): pass', r'''
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
'''),
],

'old_general': [  # ................................................................................

('body[0].value', 1, 2, None, {'raw': True}, ('exec',
r'''(1, 2, 3)'''), (None,
r'''*z'''),
r'''(1, *z, 3)''', r'''
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
'''),

('body[0].value', 0, 3, None, {'raw': True}, ('exec',
r'''(1, 2, 3)'''), (None,
r'''*z,'''),
r'''(*z,)''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Tuple - 0,0..0,5
       .elts[1]
        0] Starred - 0,1..0,3
          .value Name 'z' Load - 0,2..0,3
          .ctx Load
       .ctx Load
'''),

('body[0].value', 1, 2, None, {'raw': True}, ('exec',
r'''1, 2, 3'''), (None,
r'''*z'''),
r'''1, *z, 3''', r'''
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
'''),

('body[0].value', 0, 3, None, {'raw': True}, ('exec',
r'''1, 2, 3'''), (None,
r'''*z,'''),
r'''*z,''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Tuple - 0,0..0,3
       .elts[1]
        0] Starred - 0,0..0,2
          .value Name 'z' Load - 0,1..0,2
          .ctx Load
       .ctx Load
'''),

('body[0].value', 1, 2, None, {'raw': True}, ('exec',
r'''{a: b, c: d, e: f}'''), (None,
r'''**z'''),
r'''{a: b, **z, e: f}''', r'''
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
'''),

('body[0].value', 0, 3, None, {'raw': True}, ('exec',
r'''{a: b, c: d, e: f}'''), (None,
r'''**z'''),
r'''{**z}''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Dict - 0,0..0,5
       .keys[1]
        0] None
       .values[1]
        0] Name 'z' Load - 0,3..0,4
'''),

('body[0].value', 1, 3, None, {'raw': True}, ('exec',
r'''{a: b, **c, **d, **e}'''), (None,
r'''f: g'''),
r'''{a: b, f: g, **e}''', r'''
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
'''),

('body[0]', 1, 3, None, {'raw': True}, ('exec',
r'''del a, b, c'''), (None,
r'''z'''),
r'''del a, z''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Delete - 0,0..0,8
     .targets[2]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'z' Del - 0,7..0,8
'''),

('body[0]', 1, 3, 'targets', {'raw': True}, ('exec',
r'''a = b = c = d'''), (None,
r'''z'''),
r'''a = z = d''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Assign - 0,0..0,9
     .targets[2]
      0] Name 'a' Store - 0,0..0,1
      1] Name 'z' Store - 0,4..0,5
     .value Name 'd' Load - 0,8..0,9
'''),

('body[0]', 1, 3, None, {'raw': True}, ('exec',
r'''import a, b, c'''), (None,
r'''z as xyz'''),
r'''import a, z as xyz''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Import - 0,0..0,18
     .names[2]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,18
        .name 'z'
        .asname 'xyz'
'''),

('body[0]', 1, 3, None, {'raw': True}, ('exec',
r'''from mod import a, b, c'''), (None,
r'''z as xyz'''),
r'''from mod import a, z as xyz''', r'''
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
'''),

('body[0]', 1, 3, 'items', {'raw': True}, ('exec',
r'''with a as a, b as b, c as c: pass'''), (None,
r'''z as xyz'''),
r'''with a as a, z as xyz: pass''', r'''
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
'''),

('body[0].value', 1, 3, None, {'raw': True}, ('exec',
r'''a and b and c'''), (None,
r'''z'''),
r'''a and z''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value BoolOp - 0,0..0,7
       .op And
       .values[2]
        0] Name 'a' Load - 0,0..0,1
        1] Name 'z' Load - 0,6..0,7
'''),

('body[0].value', 0, 3, 'comparators', {'raw': True}, ('exec',
r'''a < b < c < d'''), (None,
r'''x < y'''),
r'''a < x < y''', r'''
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
'''),

('body[0].value', 1, 3, 'generators', {'raw': True}, ('exec',
r'''[a for a in a() for b in b() for c in c()]'''), (None,
r'''for z in z()'''),
r'''[a for a in a() for z in z()]''', r'''
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
'''),

('body[0].value.generators[0]', 1, 3, 'ifs', {'raw': True}, ('exec',
r'''[a for a in a() if a if b if c]'''), (None,
r'''if z'''),
r'''[a for a in a() if a if z]''', r'''
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
'''),

('body[0].value', 1, 3, None, {'raw': True}, ('exec',
r'''f(a, b, c)'''), (None,
r'''z'''),
r'''f(a, z)''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Call - 0,0..0,7
       .func Name 'f' Load - 0,0..0,1
       .args[2]
        0] Name 'a' Load - 0,2..0,3
        1] Name 'z' Load - 0,5..0,6
'''),

('body[0].value', 1, 3, None, {'raw': True}, ('exec',
r'''f(a, b, c)'''), (None,
r'''**z'''),
r'''f(a, **z)''', r'''
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
'''),

('body[0]', 1, 3, 'decorator_list', {'raw': True}, ('exec', r'''
@a
@b
@c
def f(): pass
'''), (None,
r'''@z'''), r'''
@a
@z
def f(): pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 2,0..2,13
     .name 'f'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'z' Load - 1,1..1,2
'''),

('body[0].cases[0].pattern', 1, 3, None, {'raw': True}, ('exec', r'''
match a:
  case [a, b, c]: pass
'''), (None,
r'''*z'''), r'''
match a:
  case [a, *z]: pass
''', r'''
Module - ROOT 0,0..1,20
  .body[1]
   0] Match - 0,0..1,20
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,2..1,20
        .pattern MatchSequence - 1,7..1,14
          .patterns[2]
           0] MatchAs - 1,8..1,9
             .name 'a'
           1] MatchStar - 1,11..1,13
             .name 'z'
        .body[1]
         0] Pass - 1,16..1,20
'''),

('body[0].cases[0].pattern', 1, 3, None, {'raw': True}, ('exec', r'''
match a:
  case a | b | c: pass
'''), (None,
r'''z'''), r'''
match a:
  case a | z: pass
''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] Match - 0,0..1,18
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,2..1,18
        .pattern MatchOr - 1,7..1,12
          .patterns[2]
           0] MatchAs - 1,7..1,8
             .name 'a'
           1] MatchAs - 1,11..1,12
             .name 'z'
        .body[1]
         0] Pass - 1,14..1,18
'''),

('body[0].cases[0].pattern', 1, 3, None, {'raw': True}, ('exec', r'''
match a:
  case {'a': a, 'b': b, 'c': c}: pass
'''), (None,
r'''**z'''), r'''
match a:
  case {'a': a, **z}: pass
''', r'''
Module - ROOT 0,0..1,26
  .body[1]
   0] Match - 0,0..1,26
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,2..1,26
        .pattern MatchMapping - 1,7..1,20
          .keys[1]
           0] Constant 'a' - 1,8..1,11
          .patterns[1]
           0] MatchAs - 1,13..1,14
             .name 'a'
          .rest 'z'
        .body[1]
         0] Pass - 1,22..1,26
'''),

('body[0].args', 0, 1, 'args', {'raw': True}, ('exec',
r'''def f(a): pass'''), (None,
r'''b'''),
r'''def f(b): pass''', r'''
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
'''),

('body[0].args', 0, 1, 'args', {'raw': True}, ('exec',
r'''def f(a): pass'''), (None,
r''''''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
r'''f(a)'''), (None,
r'''(i for i in range(5))'''),
r'''f((i for i in range(5)))''', r'''
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
'''),

('body[0].value', 1, 3, None, {'raw': True}, ('exec',
r'''{1: 2, **(x), (3): (4)}'''), (None,
r'''**z'''),
r'''{1: 2, **z}''', r'''
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
'''),

('body[0].value', 0, 2, 'comparators', {'raw': True}, ('exec',
r'''((a) < (b) < (c))'''), (None,
r'''z'''),
r'''((a) < z)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Compare - 0,1..0,8
       .left Name 'a' Load - 0,2..0,3
       .ops[1]
        0] Lt - 0,5..0,6
       .comparators[1]
        0] Name 'z' Load - 0,7..0,8
'''),

('body[0].value', 1, 3, None, {'raw': True}, ('exec',
r'''(1, *(x), (3))'''), (None,
r'''*z'''),
r'''(1, *z)''', r'''
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
'''),

('body[0].cases[0].pattern', 1, 3, None, {'raw': True}, ('exec', r'''
match a:
  case {'a': (a), 'b': (b), 'c': (c)}: pass
'''), (None,
r'''**z'''), r'''
match a:
  case {'a': (a), **z}: pass
''', r'''
Module - ROOT 0,0..1,28
  .body[1]
   0] Match - 0,0..1,28
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,2..1,28
        .pattern MatchMapping - 1,7..1,22
          .keys[1]
           0] Constant 'a' - 1,8..1,11
          .patterns[1]
           0] MatchAs - 1,14..1,15
             .name 'a'
          .rest 'z'
        .body[1]
         0] Pass - 1,24..1,28
'''),

('body[0].value.generators[0]', 1, 3, 'ifs', {'raw': True}, ('exec',
r'''[a for a in a() if (a) if (b) if (c)]'''), (None,
r'''if z'''),
r'''[a for a in a() if (a) if z]''', r'''
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
'''),

('body[0]', 1, 3, 'decorator_list', {'raw': True}, ('exec', r'''
@(a)
@(b)
@(c)
def f(): pass
'''), (None,
r'''@z'''), r'''
@(a)
@z
def f(): pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 2,0..2,13
     .name 'f'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'a' Load - 0,2..0,3
      1] Name 'z' Load - 1,1..1,2
'''),

('body[0].value', 1, 3, None, {'raw': True}, ('exec',
r'''((1), (2), (3))'''), (None,
r'''*z'''),
r'''((1), *z)''', r'''
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
'''),

('body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
r'''f(i for i in range(5))'''), (None,
r'''a'''),
r'''f(a)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Call - 0,0..0,4
       .func Name 'f' Load - 0,0..0,1
       .args[1]
        0] Name 'a' Load - 0,2..0,3
'''),

('body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
r'''f((i for i in range(5)))'''), (None,
r'''a'''),
r'''f(a)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Call - 0,0..0,4
       .func Name 'f' Load - 0,0..0,1
       .args[1]
        0] Name 'a' Load - 0,2..0,3
'''),

('body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
r'''f(((i for i in range(5))))'''), (None,
r'''a'''),
r'''f(a)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Call - 0,0..0,4
       .func Name 'f' Load - 0,0..0,1
       .args[1]
        0] Name 'a' Load - 0,2..0,3
'''),

('body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
r'''f((i for i in range(5)), b)'''), (None,
r'''a'''),
r'''f(a, b)''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Call - 0,0..0,7
       .func Name 'f' Load - 0,0..0,1
       .args[2]
        0] Name 'a' Load - 0,2..0,3
        1] Name 'b' Load - 0,5..0,6
'''),

('body[0].value', 0, 2, 'args', {'raw': True}, ('exec',
r'''f((i for i in range(5)), b)'''), (None,
r'''a'''),
r'''f(a)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Call - 0,0..0,4
       .func Name 'f' Load - 0,0..0,1
       .args[1]
        0] Name 'a' Load - 0,2..0,3
'''),

('body[0].value', 1, 1, None, {'trivia': (None, False)}, ('exec', r'''
[a# comment
]
'''), (None,
r'''b,'''), r'''
[a, b, # comment
]
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value List - 0,0..1,1
       .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

('body[0].value', 1, 1, None, {'trivia': (None, False)}, ('exec', r'''
[a# comment
]
'''), (None,
r'''[b]'''), r'''
[a, b # comment
]
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value List - 0,0..1,1
       .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

('body[0].value', 1, 1, None, {'trivia': (None, False)}, ('exec', r'''
[a,  # test
]
'''), (None,
r'''b,'''), r'''
[a, b, # test
]
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value List - 0,0..1,1
       .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

('body[0].value', 1, 1, None, {'trivia': (None, False)}, ('exec', r'''
[a,  # test
]
'''), (None,
r'''[b]'''), r'''
[a, b # test
]
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value List - 0,0..1,1
       .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
[
# c0

# c2
]
'''), (None,
r'''[a]'''), r'''
[a
# c0

# c2
]
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 0,0..4,1
     .value List - 0,0..4,1
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
[
# c0

# c2
]
'''), (None,
r'''[a]'''), r'''
[
a # c0

# c2
]
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 0,0..4,1
     .value List - 0,0..4,1
       .elts[1]
        0] Name 'a' Load - 1,0..1,1
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
[
# c0

# c2
]
'''), (None,
r'''[a]'''), r'''
[
# c0
a
# c2
]
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 0,0..4,1
     .value List - 0,0..4,1
       .elts[1]
        0] Name 'a' Load - 2,0..2,1
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
[
# c0

# c2
]
'''), (None,
r'''[a]'''), r'''
[
# c0

a # c2
]
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 0,0..4,1
     .value List - 0,0..4,1
       .elts[1]
        0] Name 'a' Load - 3,0..3,1
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
[
# c0

# c2
]
'''), (None,
r'''[a]'''), r'''
[
# c0

# c2
a]
''', r'''
Module - ROOT 0,0..4,2
  .body[1]
   0] Expr - 0,0..4,2
     .value List - 0,0..4,2
       .elts[1]
        0] Name 'a' Load - 4,0..4,1
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
[
# c0

# c2
]
'''), (None, r'''
[
a
]
'''), r'''
[
    a
# c0

# c2
]
''', r'''
[a
# c0

# c2
]
''', r'''
Module - ROOT 0,0..5,1
  .body[1]
   0] Expr - 0,0..5,1
     .value List - 0,0..5,1
       .elts[1]
        0] Name 'a' Load - 1,4..1,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
[
# c0

# c2
]
'''), (None, r'''
[
a
]
'''), r'''
[
    a
# c0

# c2
]
''', r'''
[
a # c0

# c2
]
''', r'''
Module - ROOT 0,0..5,1
  .body[1]
   0] Expr - 0,0..5,1
     .value List - 0,0..5,1
       .elts[1]
        0] Name 'a' Load - 1,4..1,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
[
# c0

# c2
]
'''), (None, r'''
[
a
]
'''), r'''
[
# c0
    a
# c2
]
''', r'''
[
# c0
a
# c2
]
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 0,0..4,1
     .value List - 0,0..4,1
       .elts[1]
        0] Name 'a' Load - 2,4..2,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
[
# c0

# c2
]
'''), (None, r'''
[
a
]
'''), r'''
[
# c0

    a
# c2
]
''', r'''
[
# c0

a # c2
]
''', r'''
Module - ROOT 0,0..5,1
  .body[1]
   0] Expr - 0,0..5,1
     .value List - 0,0..5,1
       .elts[1]
        0] Name 'a' Load - 3,4..3,5
       .ctx Load
'''),

('body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
[
# c0

# c2
]
'''), (None, r'''
[
a
]
'''), r'''
[
# c0

# c2
    a
]
''', r'''
[
# c0

# c2
a]
''', r'''
Module - ROOT 0,0..5,1
  .body[1]
   0] Expr - 0,0..5,1
     .value List - 0,0..5,1
       .elts[1]
        0] Name 'a' Load - 4,4..4,5
       .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None,
r'''[a]'''), r'''
if 1: [a
    # c0

    # c2
  ]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None,
r'''[a]'''), r'''
if 1: [
    a # c0

    # c2
  ]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None,
r'''[a]'''), r'''
if 1: [
    # c0
    a
    # c2
  ]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None,
r'''[a]'''), r'''
if 1: [
    # c0

    a # c2
  ]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None,
r'''[a]'''), r'''
if 1: [
    # c0

    # c2
  a]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a]
'''), r'''
if 1: [
        a
    # c0

    # c2
  ]
''', r'''
if 1: [a
    # c0

    # c2
  ]
''', r'''
Module - ROOT 0,0..5,3
  .body[1]
   0] If - 0,0..5,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..5,3
        .value List - 0,6..5,3
          .elts[1]
           0] Name 'a' Load - 1,8..1,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a]
'''), r'''
if 1: [
        a # c0

    # c2
  ]
''', r'''
if 1: [
    a # c0

    # c2
  ]
''', r'''
Module - ROOT 0,0..4,3
  .body[1]
   0] If - 0,0..4,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..4,3
        .value List - 0,6..4,3
          .elts[1]
           0] Name 'a' Load - 1,8..1,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a]
'''), r'''
if 1: [
    # c0
        a
    # c2
  ]
''', r'''
if 1: [
    # c0
    a
    # c2
  ]
''', r'''
Module - ROOT 0,0..4,3
  .body[1]
   0] If - 0,0..4,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..4,3
        .value List - 0,6..4,3
          .elts[1]
           0] Name 'a' Load - 2,8..2,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a]
'''), r'''
if 1: [
    # c0

        a # c2
  ]
''', r'''
if 1: [
    # c0

    a # c2
  ]
''', r'''
Module - ROOT 0,0..4,3
  .body[1]
   0] If - 0,0..4,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..4,3
        .value List - 0,6..4,3
          .elts[1]
           0] Name 'a' Load - 3,8..3,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a]
'''), r'''
if 1: [
    # c0

    # c2
        a]
''', r'''
if 1: [
    # c0

    # c2
  a]
''', r'''
Module - ROOT 0,0..4,10
  .body[1]
   0] If - 0,0..4,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..4,10
        .value List - 0,6..4,10
          .elts[1]
           0] Name 'a' Load - 4,8..4,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[a
]
'''), r'''
if 1: [a
    # c0

    # c2
  ]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[a
]
'''), r'''
if 1: [
    a
    # c0

    # c2
  ]
''', r'''
if 1: [
    a # c0

    # c2
  ]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[a
]
'''), r'''
if 1: [
    # c0
    a
    # c2
  ]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[a
]
'''), r'''
if 1: [
    # c0

    a
    # c2
  ]
''', r'''
if 1: [
    # c0

    a # c2
  ]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[a
]
'''), r'''
if 1: [
    # c0

    # c2
  a
  ]
''', r'''
if 1: [
    # c0

    # c2
  a]
''', r'''
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
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [
        a
    # c0

    # c2
  ]
''', r'''
if 1: [a
    # c0

    # c2
  ]
''', r'''
Module - ROOT 0,0..5,3
  .body[1]
   0] If - 0,0..5,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..5,3
        .value List - 0,6..5,3
          .elts[1]
           0] Name 'a' Load - 1,8..1,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [
        a
    # c0

    # c2
  ]
''', r'''
if 1: [
    a # c0

    # c2
  ]
''', r'''
Module - ROOT 0,0..5,3
  .body[1]
   0] If - 0,0..5,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..5,3
        .value List - 0,6..5,3
          .elts[1]
           0] Name 'a' Load - 1,8..1,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [
    # c0
        a
    # c2
  ]
''', r'''
if 1: [
    # c0
    a
    # c2
  ]
''', r'''
Module - ROOT 0,0..4,3
  .body[1]
   0] If - 0,0..4,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..4,3
        .value List - 0,6..4,3
          .elts[1]
           0] Name 'a' Load - 2,8..2,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [
    # c0

        a
    # c2
  ]
''', r'''
if 1: [
    # c0

    a # c2
  ]
''', r'''
Module - ROOT 0,0..5,3
  .body[1]
   0] If - 0,0..5,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..5,3
        .value List - 0,6..5,3
          .elts[1]
           0] Name 'a' Load - 3,8..3,9
          .ctx Load
'''),

('body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
if 1: [
    # c0

    # c2
  ]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [
    # c0

    # c2
        a
  ]
''', r'''
if 1: [
    # c0

    # c2
  a]
''', r'''
Module - ROOT 0,0..5,3
  .body[1]
   0] If - 0,0..5,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..5,3
        .value List - 0,6..5,3
          .elts[1]
           0] Name 'a' Load - 4,8..4,9
          .ctx Load
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None,
r'''[a]'''), r'''
if 1: [x, a,
    # c0

    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None,
r'''[a]'''), r'''
if 1: [x,
    a, # c0

    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None,
r'''[a]'''), r'''
if 1: [x,
    # c0
    a,
    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None,
r'''[a]'''), r'''
if 1: [x,
    # c0

    a, # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None,
r'''[a]'''), r'''
if 1: [x,
    # c0

    # c2
  a, y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [x,
    a,
    # c0

    # c2
  y]
''', r'''
if 1: [x, a,
    # c0

    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [x,
    a,
    # c0

    # c2
  y]
''', r'''
if 1: [x,
    a, # c0

    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [x,
    # c0
    a,
    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [x,
    # c0

    a,
    # c2
  y]
''', r'''
if 1: [x,
    # c0

    a, # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a
]
'''), r'''
if 1: [x,
    # c0

    # c2
    a,
  y]
''', r'''
if 1: [x,
    # c0

    # c2
  a, y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a,
 b]
'''), r'''
if 1: [x,
    a,
     b,
    # c0

    # c2
  y]
''', r'''
if 1: [x, a, b,
    # c0

    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a,
 b]
'''), r'''
if 1: [x,
    a,
     b, # c0

    # c2
  y]
''', r'''
if 1: [x,
    a, b, # c0

    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a,
 b]
'''), r'''
if 1: [x,
    # c0
    a,
     b,
    # c2
  y]
''', r'''
if 1: [x,
    # c0
    a, b,
    # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a,
 b]
'''), r'''
if 1: [x,
    # c0

    a,
     b, # c2
  y]
''', r'''
if 1: [x,
    # c0

    a, b, # c2
  y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
if 1: [x,
    # c0

    # c2
  y]
'''), (None, r'''
[
a,
 b]
'''), r'''
if 1: [x,
    # c0

    # c2
    a,
     b, y]
''', r'''
if 1: [x,
    # c0

    # c2
  a, b, y]
''', r'''
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
'''),

('body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
if 1: {**x,
    # c0

    # c2
  **y}
'''), (None,
r'''{**a}'''), r'''
if 1: {**x,
    # c0

    # c2
  **a, **y}
''', r'''
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
'''),

('body[0].cases[0].pattern', 0, 1, None, {'norm_self': False, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
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
        .pattern MatchOr - 1,6..1,7
          .patterns[1]
           0] MatchAs - 1,6..1,7
             .name 'b'
        .body[1]
         0] Pass - 1,9..1,13
'''),

('body[0].cases[0].pattern', 0, 2, None, {'norm_self': False, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), (None,
r'''**DEL**'''), r'''
match a:
 case : pass
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Match - 0,0..1,12
     .subject Name 'a' Load - 0,6..0,7
     .cases[1]
      0] match_case - 1,1..1,12
        .pattern MatchOr - 1,6..1,6
        .body[1]
         0] Pass - 1,8..1,12
'''),

('body[0].cases[0].pattern', 0, 1, None, {'norm_self': True, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
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

('body[0].cases[0].pattern', 0, 2, None, {'norm_self': True, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), (None,
r'''**DEL**'''),
r'''**ValueError('cannot delete all MatchOr.patterns without norm_self=False')**'''),

('body[0].cases[0].pattern', 0, 1, None, {'norm_self': False, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), ('pattern',
r'''z'''), r'''
match a:
 case z | b: pass
''', r'''
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
'''),

('body[0].cases[0].pattern', 0, 2, None, {'norm_self': False, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), ('pattern',
r'''z'''), r'''
match a:
 case z: pass
''', r'''
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
'''),

('body[0].cases[0].pattern', 0, 1, None, {'norm_self': True, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), ('pattern',
r'''z'''), r'''
match a:
 case z | b: pass
''', r'''
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
'''),

('body[0].cases[0].pattern', 0, 2, None, {'norm_self': True, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), ('pattern',
r'''z'''), r'''
match a:
 case z: pass
''', r'''
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
'''),

('body[0].cases[0].pattern', 0, 1, None, {'norm_put': False, 'norm': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), ('pattern',
r'''z'''), r'''
match a:
 case z | b: pass
''', r'''
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
'''),

('body[0].body[0].value', 'end', 'end', None, {'one': True}, ('exec', r'''
if 1:
  [
    a, # a
    b, # b
    c, # c
  ]
'''), (None, r'''
[
  d, # d
]
'''), r'''
if 1:
  [
    a, # a
    b, # b
    c, [
      d, # d
    ]
  ]
''', r'''
if 1:
  [
    a, # a
    b, # b
    c, [d]
  ]
''', r'''
Module - ROOT 0,0..7,3
  .body[1]
   0] If - 0,0..7,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,2..7,3
        .value List - 1,2..7,3
          .elts[4]
           0] Name 'a' Load - 2,4..2,5
           1] Name 'b' Load - 3,4..3,5
           2] Name 'c' Load - 4,4..4,5
           3] List - 4,7..6,5
             .elts[1]
              0] Name 'd' Load - 5,6..5,7
             .ctx Load
          .ctx Load
'''),

('body[0].body[0].value', 1, 1, None, {'one': True}, ('exec', r'''
if 1:
  [
    a, # a
    b, # b
    c, # c
  ]
'''), (None, r'''
[
  d, # d
]
'''), r'''
if 1:
  [
    a, # a
    [
      d, # d
    ], b, # b
    c, # c
  ]
''', r'''
if 1:
  [
    a, # a
    [d], b, # b
    c, # c
  ]
''', r'''
Module - ROOT 0,0..7,3
  .body[1]
   0] If - 0,0..7,3
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,2..7,3
        .value List - 1,2..7,3
          .elts[4]
           0] Name 'a' Load - 2,4..2,5
           1] List - 3,4..5,5
             .elts[1]
              0] Name 'd' Load - 4,6..4,7
             .ctx Load
           2] Name 'b' Load - 5,7..5,8
           3] Name 'c' Load - 6,4..6,5
          .ctx Load
'''),

('body[0].value.slice', 2, 2, None, {}, ('exec',
r'''a[b:c:d, e:f:g]'''), (None,
r'''x:y:z,'''),
r'''a[b:c:d, e:f:g, x:y:z]''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Expr - 0,0..0,22
     .value Subscript - 0,0..0,22
       .value Name 'a' Load - 0,0..0,1
       .slice Tuple - 0,2..0,21
         .elts[3]
          0] Slice - 0,2..0,7
            .lower Name 'b' Load - 0,2..0,3
            .upper Name 'c' Load - 0,4..0,5
            .step Name 'd' Load - 0,6..0,7
          1] Slice - 0,9..0,14
            .lower Name 'e' Load - 0,9..0,10
            .upper Name 'f' Load - 0,11..0,12
            .step Name 'g' Load - 0,13..0,14
          2] Slice - 0,16..0,21
            .lower Name 'x' Load - 0,16..0,17
            .upper Name 'y' Load - 0,18..0,19
            .step Name 'z' Load - 0,20..0,21
         .ctx Load
       .ctx Load
'''),

('body[0].value.slice', 2, 2, None, {'one': True}, ('exec',
r'''a[b:c:d, e:f:g]'''), (None,
r'''x:y:z,'''),
r'''**NodeError('cannot put tuple with Slices to tuple')**'''),
],

'docstr': [  # ................................................................................

('', 0, 0, None, {}, ('exec',
r'''pass'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
pass
''', r'''
"""One
  Two"""
'Three\n  Four'
i
'Five\n  Six'
pass
''', r'''
Module - ROOT 0,0..6,4
  .body[5]
   0] Expr - 0,0..1,8
     .value Constant 'One\n  Two' - 0,0..1,8
   1] Expr - 2,0..3,9
     .value Constant 'Three\n  Four' - 2,0..3,9
   2] Expr - 4,0..4,1
     .value Name 'i' Load - 4,0..4,1
   3] Expr - 4,4..5,8
     .value Constant 'Five\n  Six' - 4,4..5,8
   4] Pass - 6,0..6,4
'''),

('body[0]', 0, 0, None, {'_cmp_asts': False}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
    pass
''', r'''
def f():
    """One
      Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
    pass
''', r'''
Module - ROOT 0,0..7,8
  .body[1]
   0] FunctionDef - 0,0..7,8
     .name 'f'
     .body[5]
      0] Expr - 1,4..2,12
        .value Constant 'One\n      Two' - 1,4..2,12
      1] Expr - 3,4..4,13
        .value Constant 'Three\n      Four' - 3,4..4,13
      2] Expr - 5,4..5,5
        .value Name 'i' Load - 5,4..5,5
      3] Expr - 5,8..6,12
        .value Constant 'Five\n      Six' - 5,8..6,12
      4] Pass - 7,4..7,8
'''),

('body[0]', 0, 0, None, {'_cmp_asts': False, 'docstr': 'strict'}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    """One
      Two"""
    """Three
  Four"""
    i ; """Five
  Six"""
    pass
''', r'''
def f():
    """One
      Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
    pass
''', r'''
Module - ROOT 0,0..7,8
  .body[1]
   0] FunctionDef - 0,0..7,8
     .name 'f'
     .body[5]
      0] Expr - 1,4..2,12
        .value Constant 'One\n      Two' - 1,4..2,12
      1] Expr - 3,4..4,9
        .value Constant 'Three\n  Four' - 3,4..4,9
      2] Expr - 5,4..5,5
        .value Name 'i' Load - 5,4..5,5
      3] Expr - 5,8..6,8
        .value Constant 'Five\n  Six' - 5,8..6,8
      4] Pass - 7,4..7,8
'''),

('body[0]', 0, 0, None, {'_cmp_asts': False, 'docstr': False}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    """One
  Two"""
    """Three
  Four"""
    i ; """Five
  Six"""
    pass
''', r'''
def f():
    """One
  Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
    pass
''', r'''
Module - ROOT 0,0..7,8
  .body[1]
   0] FunctionDef - 0,0..7,8
     .name 'f'
     .body[5]
      0] Expr - 1,4..2,8
        .value Constant 'One\n  Two' - 1,4..2,8
      1] Expr - 3,4..4,9
        .value Constant 'Three\n  Four' - 3,4..4,9
      2] Expr - 5,4..5,5
        .value Name 'i' Load - 5,4..5,5
      3] Expr - 5,8..6,8
        .value Constant 'Five\n  Six' - 5,8..6,8
      4] Pass - 7,4..7,8
'''),

('body[0]', 0, 1, None, {'_cmp_asts': False}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
''', r'''
def f():
    """One
      Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
''', r'''
Module - ROOT 0,0..6,12
  .body[1]
   0] FunctionDef - 0,0..6,12
     .name 'f'
     .body[4]
      0] Expr - 1,4..2,12
        .value Constant 'One\n      Two' - 1,4..2,12
      1] Expr - 3,4..4,13
        .value Constant 'Three\n      Four' - 3,4..4,13
      2] Expr - 5,4..5,5
        .value Name 'i' Load - 5,4..5,5
      3] Expr - 5,8..6,12
        .value Constant 'Five\n      Six' - 5,8..6,12
'''),

('body[0]', 0, 1, None, {'_cmp_asts': False, 'docstr': 'strict'}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    """One
      Two"""
    """Three
  Four"""
    i ; """Five
  Six"""
''', r'''
def f():
    """One
      Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
''', r'''
Module - ROOT 0,0..6,8
  .body[1]
   0] FunctionDef - 0,0..6,8
     .name 'f'
     .body[4]
      0] Expr - 1,4..2,12
        .value Constant 'One\n      Two' - 1,4..2,12
      1] Expr - 3,4..4,9
        .value Constant 'Three\n  Four' - 3,4..4,9
      2] Expr - 5,4..5,5
        .value Name 'i' Load - 5,4..5,5
      3] Expr - 5,8..6,8
        .value Constant 'Five\n  Six' - 5,8..6,8
'''),

('body[0]', 0, 1, None, {'_cmp_asts': False, 'docstr': False}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    """One
  Two"""
    """Three
  Four"""
    i ; """Five
  Six"""
''', r'''
def f():
    """One
  Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
''', r'''
Module - ROOT 0,0..6,8
  .body[1]
   0] FunctionDef - 0,0..6,8
     .name 'f'
     .body[4]
      0] Expr - 1,4..2,8
        .value Constant 'One\n  Two' - 1,4..2,8
      1] Expr - 3,4..4,9
        .value Constant 'Three\n  Four' - 3,4..4,9
      2] Expr - 5,4..5,5
        .value Name 'i' Load - 5,4..5,5
      3] Expr - 5,8..6,8
        .value Constant 'Five\n  Six' - 5,8..6,8
'''),

('body[0]', 1, 1, None, {'_cmp_asts': False}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    pass
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
''', r'''
def f():
    pass
    """One
      Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
''', r'''
Module - ROOT 0,0..7,12
  .body[1]
   0] FunctionDef - 0,0..7,12
     .name 'f'
     .body[5]
      0] Pass - 1,4..1,8
      1] Expr - 2,4..3,12
        .value Constant 'One\n      Two' - 2,4..3,12
      2] Expr - 4,4..5,13
        .value Constant 'Three\n      Four' - 4,4..5,13
      3] Expr - 6,4..6,5
        .value Name 'i' Load - 6,4..6,5
      4] Expr - 6,8..7,12
        .value Constant 'Five\n      Six' - 6,8..7,12
'''),

('body[0]', 1, 1, None, {'_cmp_asts': False, 'docstr': 'strict'}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    pass
    """One
  Two"""
    """Three
  Four"""
    i ; """Five
  Six"""
''', r'''
def f():
    pass
    """One
  Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
''', r'''
Module - ROOT 0,0..7,8
  .body[1]
   0] FunctionDef - 0,0..7,8
     .name 'f'
     .body[5]
      0] Pass - 1,4..1,8
      1] Expr - 2,4..3,8
        .value Constant 'One\n  Two' - 2,4..3,8
      2] Expr - 4,4..5,9
        .value Constant 'Three\n  Four' - 4,4..5,9
      3] Expr - 6,4..6,5
        .value Name 'i' Load - 6,4..6,5
      4] Expr - 6,8..7,8
        .value Constant 'Five\n  Six' - 6,8..7,8
'''),

('body[0]', 1, 1, None, {'_cmp_asts': False, 'docstr': False}, ('exec', r'''
def f():
    pass
'''), (None, r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
'''), r'''
def f():
    pass
    """One
  Two"""
    """Three
  Four"""
    i ; """Five
  Six"""
''', r'''
def f():
    pass
    """One
  Two"""
    'Three\n  Four'
    i
    'Five\n  Six'
''', r'''
Module - ROOT 0,0..7,8
  .body[1]
   0] FunctionDef - 0,0..7,8
     .name 'f'
     .body[5]
      0] Pass - 1,4..1,8
      1] Expr - 2,4..3,8
        .value Constant 'One\n  Two' - 2,4..3,8
      2] Expr - 4,4..5,9
        .value Constant 'Three\n  Four' - 4,4..5,9
      3] Expr - 6,4..6,5
        .value Name 'i' Load - 6,4..6,5
      4] Expr - 6,8..7,8
        .value Constant 'Five\n  Six' - 6,8..7,8
'''),
],

'stmtlike_trailing_newline': [  # ................................................................................

('', 1, 2, None, {}, (None, r'''
if 1:
    i = 1
    j = 2
'''), (None,
r'''k = 3'''), r'''
if 1:
    i = 1
    k = 3
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[2]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'i' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
   1] Assign - 2,4..2,9
     .targets[1]
      0] Name 'k' Store - 2,4..2,5
     .value Constant 3 - 2,8..2,9
'''),

('', 1, 2, None, {}, (None, r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3

'''), r'''
if 1:
    i = 1
    k = 3

''', r'''
if 1:
    i = 1
    k = 3
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[2]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'i' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
   1] Assign - 2,4..2,9
     .targets[1]
      0] Name 'k' Store - 2,4..2,5
     .value Constant 3 - 2,8..2,9
'''),

('', 2, 2, None, {}, (None, r'''
if 1:
    i = 1
    j = 2
'''), (None,
r'''k = 3'''), r'''
if 1:
    i = 1
    j = 2
    k = 3
''', r'''
If - ROOT 0,0..3,9
  .test Constant 1 - 0,3..0,4
  .body[3]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'i' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
   1] Assign - 2,4..2,9
     .targets[1]
      0] Name 'j' Store - 2,4..2,5
     .value Constant 2 - 2,8..2,9
   2] Assign - 3,4..3,9
     .targets[1]
      0] Name 'k' Store - 3,4..3,5
     .value Constant 3 - 3,8..3,9
'''),

('', 2, 2, None, {}, (None, r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3

'''), r'''
if 1:
    i = 1
    j = 2
    k = 3

''', r'''
if 1:
    i = 1
    j = 2
    k = 3
''', r'''
If - ROOT 0,0..3,9
  .test Constant 1 - 0,3..0,4
  .body[3]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'i' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
   1] Assign - 2,4..2,9
     .targets[1]
      0] Name 'j' Store - 2,4..2,5
     .value Constant 2 - 2,8..2,9
   2] Assign - 3,4..3,9
     .targets[1]
      0] Name 'k' Store - 3,4..3,5
     .value Constant 3 - 3,8..3,9
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None,
r'''k = 3'''), r'''
if 1:
    i = 1
    k = 3
''', r'''
Module - ROOT 0,0..2,9
  .body[1]
   0] If - 0,0..2,9
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'k' Store - 2,4..2,5
        .value Constant 3 - 2,8..2,9
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3

'''), r'''
if 1:
    i = 1
    k = 3

''', r'''
if 1:
    i = 1
    k = 3
''', r'''
Module - ROOT 0,0..3,0
  .body[1]
   0] If - 0,0..2,9
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'k' Store - 2,4..2,5
        .value Constant 3 - 2,8..2,9
'''),

('body[0]', 2, 2, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None,
r'''k = 3'''), r'''
if 1:
    i = 1
    j = 2
    k = 3
''', r'''
Module - ROOT 0,0..3,9
  .body[1]
   0] If - 0,0..3,9
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'j' Store - 2,4..2,5
        .value Constant 2 - 2,8..2,9
      2] Assign - 3,4..3,9
        .targets[1]
         0] Name 'k' Store - 3,4..3,5
        .value Constant 3 - 3,8..3,9
'''),

('body[0]', 2, 2, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3

'''), r'''
if 1:
    i = 1
    j = 2
    k = 3

''', r'''
if 1:
    i = 1
    j = 2
    k = 3
''', r'''
Module - ROOT 0,0..4,0
  .body[1]
   0] If - 0,0..3,9
     .test Constant 1 - 0,3..0,4
     .body[3]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'j' Store - 2,4..2,5
        .value Constant 2 - 2,8..2,9
      2] Assign - 3,4..3,9
        .targets[1]
         0] Name 'k' Store - 3,4..3,5
        .value Constant 3 - 3,8..3,9
'''),

('', 0, 0, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None,
r'''k = 3'''), r'''
k = 3
if 1:
    i = 1
    j = 2
''', r'''
Module - ROOT 0,0..3,9
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'k' Store - 0,0..0,1
     .value Constant 3 - 0,4..0,5
   1] If - 1,0..3,9
     .test Constant 1 - 1,3..1,4
     .body[2]
      0] Assign - 2,4..2,9
        .targets[1]
         0] Name 'i' Store - 2,4..2,5
        .value Constant 1 - 2,8..2,9
      1] Assign - 3,4..3,9
        .targets[1]
         0] Name 'j' Store - 3,4..3,5
        .value Constant 2 - 3,8..3,9
'''),

('', 0, 0, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3

'''), r'''
k = 3
if 1:
    i = 1
    j = 2
''', r'''
Module - ROOT 0,0..3,9
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'k' Store - 0,0..0,1
     .value Constant 3 - 0,4..0,5
   1] If - 1,0..3,9
     .test Constant 1 - 1,3..1,4
     .body[2]
      0] Assign - 2,4..2,9
        .targets[1]
         0] Name 'i' Store - 2,4..2,5
        .value Constant 1 - 2,8..2,9
      1] Assign - 3,4..3,9
        .targets[1]
         0] Name 'j' Store - 3,4..3,5
        .value Constant 2 - 3,8..3,9
'''),

('', 0, 0, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3


'''), r'''
k = 3

if 1:
    i = 1
    j = 2
''', r'''
k = 3
if 1:
    i = 1
    j = 2
''', r'''
Module - ROOT 0,0..4,9
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'k' Store - 0,0..0,1
     .value Constant 3 - 0,4..0,5
   1] If - 2,0..4,9
     .test Constant 1 - 2,3..2,4
     .body[2]
      0] Assign - 3,4..3,9
        .targets[1]
         0] Name 'i' Store - 3,4..3,5
        .value Constant 1 - 3,8..3,9
      1] Assign - 4,4..4,9
        .targets[1]
         0] Name 'j' Store - 4,4..4,5
        .value Constant 2 - 4,8..4,9
'''),

('', 0, 1, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None,
r'''k = 3'''),
r'''k = 3''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'k' Store - 0,0..0,1
     .value Constant 3 - 0,4..0,5
'''),

('', 0, 1, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3

'''), r'''
k = 3

''',
r'''k = 3''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'k' Store - 0,0..0,1
     .value Constant 3 - 0,4..0,5
'''),

('', 0, 1, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3


'''), r'''
k = 3


''',
r'''k = 3''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'k' Store - 0,0..0,1
     .value Constant 3 - 0,4..0,5
'''),

('', 1, 1, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None,
r'''k = 3'''), r'''
if 1:
    i = 1
    j = 2
k = 3
''', r'''
Module - ROOT 0,0..3,5
  .body[2]
   0] If - 0,0..2,9
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'j' Store - 2,4..2,5
        .value Constant 2 - 2,8..2,9
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'k' Store - 3,0..3,1
     .value Constant 3 - 3,4..3,5
'''),

('', 1, 1, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3

'''), r'''
if 1:
    i = 1
    j = 2
k = 3

''', r'''
if 1:
    i = 1
    j = 2
k = 3
''', r'''
Module - ROOT 0,0..4,0
  .body[2]
   0] If - 0,0..2,9
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'j' Store - 2,4..2,5
        .value Constant 2 - 2,8..2,9
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'k' Store - 3,0..3,1
     .value Constant 3 - 3,4..3,5
'''),

('', 1, 1, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), (None, r'''
k = 3


'''), r'''
if 1:
    i = 1
    j = 2
k = 3


''', r'''
if 1:
    i = 1
    j = 2
k = 3
''', r'''
Module - ROOT 0,0..5,0
  .body[2]
   0] If - 0,0..2,9
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'j' Store - 2,4..2,5
        .value Constant 2 - 2,8..2,9
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'k' Store - 3,0..3,1
     .value Constant 3 - 3,4..3,5
'''),

('', 1, 1, None, {}, ('_ExceptHandlers',
r'''except a: pass'''), ('ExceptHandler',
r'''except: pass'''), r'''
except a: pass
except: pass
''', r'''
except a: pass
except:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..1,12
  .handlers[2]
   0] ExceptHandler - 0,0..0,14
     .type Name 'a' Load - 0,7..0,8
     .body[1]
      0] Pass - 0,10..0,14
   1] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', 1, 1, None, {}, ('_ExceptHandlers',
r'''except a: pass'''), ('ExceptHandler', r'''
except: pass

'''), r'''
except a: pass
except: pass

''', r'''
except a: pass
except:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..2,0
  .handlers[2]
   0] ExceptHandler - 0,0..0,14
     .type Name 'a' Load - 0,7..0,8
     .body[1]
      0] Pass - 0,10..0,14
   1] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', 1, 1, None, {}, ('_ExceptHandlers',
r'''except a: pass'''), ('ExceptHandler', r'''
except: pass


'''), r'''
except a: pass
except: pass


''', r'''
except a: pass
except:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..3,0
  .handlers[2]
   0] ExceptHandler - 0,0..0,14
     .type Name 'a' Load - 0,7..0,8
     .body[1]
      0] Pass - 0,10..0,14
   1] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', 1, 1, None, {}, ('_ExceptHandlers',
r'''except a: pass'''), ('ExceptHandler', r'''
except:
    pass
'''), r'''
except a: pass
except:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..2,8
  .handlers[2]
   0] ExceptHandler - 0,0..0,14
     .type Name 'a' Load - 0,7..0,8
     .body[1]
      0] Pass - 0,10..0,14
   1] ExceptHandler - 1,0..2,8
     .body[1]
      0] Pass - 2,4..2,8
'''),

('', 1, 1, None, {}, ('_ExceptHandlers',
r'''except a: pass'''), ('ExceptHandler', r'''
except:
    pass

'''), r'''
except a: pass
except:
    pass

''', r'''
except a: pass
except:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..3,0
  .handlers[2]
   0] ExceptHandler - 0,0..0,14
     .type Name 'a' Load - 0,7..0,8
     .body[1]
      0] Pass - 0,10..0,14
   1] ExceptHandler - 1,0..2,8
     .body[1]
      0] Pass - 2,4..2,8
'''),

('', 1, 1, None, {}, ('_ExceptHandlers',
r'''except a: pass'''), ('ExceptHandler', r'''
except:
    pass


'''), r'''
except a: pass
except:
    pass


''', r'''
except a: pass
except:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..4,0
  .handlers[2]
   0] ExceptHandler - 0,0..0,14
     .type Name 'a' Load - 0,7..0,8
     .body[1]
      0] Pass - 0,10..0,14
   1] ExceptHandler - 1,0..2,8
     .body[1]
      0] Pass - 2,4..2,8
'''),

('', 1, 1, None, {}, ('_match_cases',
r'''case 1: pass'''), ('match_case',
r'''case 2: pass'''), r'''
case 1: pass
case 2: pass
''', r'''
case 1: pass
case 2:
    pass
''', r'''
_match_cases - ROOT 0,0..1,12
  .cases[2]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..1,12
     .pattern MatchValue - 1,5..1,6
       .value Constant 2 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', 1, 1, None, {}, ('_match_cases',
r'''case 1: pass'''), ('match_case', r'''
case 2: pass

'''), r'''
case 1: pass
case 2: pass

''', r'''
case 1: pass
case 2:
    pass
''', r'''
_match_cases - ROOT 0,0..2,0
  .cases[2]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..1,12
     .pattern MatchValue - 1,5..1,6
       .value Constant 2 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', 1, 1, None, {}, ('_match_cases',
r'''case 1: pass'''), ('match_case', r'''
case 2: pass


'''), r'''
case 1: pass
case 2: pass


''', r'''
case 1: pass
case 2:
    pass
''', r'''
_match_cases - ROOT 0,0..3,0
  .cases[2]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..1,12
     .pattern MatchValue - 1,5..1,6
       .value Constant 2 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', 1, 1, None, {}, ('_match_cases',
r'''case 1: pass'''), ('match_case', r'''
case 2:
    pass
'''), r'''
case 1: pass
case 2:
    pass
''', r'''
_match_cases - ROOT 0,0..2,8
  .cases[2]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..2,8
     .pattern MatchValue - 1,5..1,6
       .value Constant 2 - 1,5..1,6
     .body[1]
      0] Pass - 2,4..2,8
'''),

('', 1, 1, None, {}, ('_match_cases',
r'''case 1: pass'''), ('match_case', r'''
case 2:
    pass

'''), r'''
case 1: pass
case 2:
    pass

''', r'''
case 1: pass
case 2:
    pass
''', r'''
_match_cases - ROOT 0,0..3,0
  .cases[2]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..2,8
     .pattern MatchValue - 1,5..1,6
       .value Constant 2 - 1,5..1,6
     .body[1]
      0] Pass - 2,4..2,8
'''),

('', 1, 1, None, {}, ('_match_cases',
r'''case 1: pass'''), ('match_case', r'''
case 2:
    pass


'''), r'''
case 1: pass
case 2:
    pass


''', r'''
case 1: pass
case 2:
    pass
''', r'''
_match_cases - ROOT 0,0..4,0
  .cases[2]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..2,8
     .pattern MatchValue - 1,5..1,6
       .value Constant 2 - 1,5..1,6
     .body[1]
      0] Pass - 2,4..2,8
'''),
],

'stmtlike_trailing_semicolon': [  # ................................................................................

('', 1, 2, None, {}, (None, r'''
a = 1;
b = 2;
'''), (None,
r'''c = 3;'''), r'''
a = 1;
c = 3;
''', r'''
a = 1;
c = 3
''', r'''
Module - ROOT 0,0..1,6
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 1,0..1,5
     .targets[1]
      0] Name 'c' Store - 1,0..1,1
     .value Constant 3 - 1,4..1,5
'''),

('', 1, 2, None, {}, (None, r'''
a = 1;
b = 2
'''), (None,
r'''c = 3;'''), r'''
a = 1;
c = 3;
''', r'''
a = 1;
c = 3
''', r'''
Module - ROOT 0,0..1,6
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 1,0..1,5
     .targets[1]
      0] Name 'c' Store - 1,0..1,1
     .value Constant 3 - 1,4..1,5
'''),

('', 1, 2, None, {}, (None, r'''
if 1:
    a = 1;
    b = 2;
'''), (None,
r'''c = 3;'''), r'''
if 1:
    a = 1;
    c = 3;
''', r'''
if 1:
    a = 1;
    c = 3
''', r'''
If - ROOT 0,0..2,10
  .test Constant 1 - 0,3..0,4
  .body[2]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
   1] Assign - 2,4..2,9
     .targets[1]
      0] Name 'c' Store - 2,4..2,5
     .value Constant 3 - 2,8..2,9
'''),

('', 1, 2, None, {}, (None, r'''
if 1:
    a = 1;
    b = 2
'''), (None,
r'''c = 3;'''), r'''
if 1:
    a = 1;
    c = 3;
''', r'''
if 1:
    a = 1;
    c = 3
''', r'''
If - ROOT 0,0..2,10
  .test Constant 1 - 0,3..0,4
  .body[2]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
   1] Assign - 2,4..2,9
     .targets[1]
      0] Name 'c' Store - 2,4..2,5
     .value Constant 3 - 2,8..2,9
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    a = 1;
    b = 2;
'''), (None,
r'''c = 3;'''), r'''
if 1:
    a = 1;
    c = 3;
''', r'''
if 1:
    a = 1;
    c = 3
''', r'''
Module - ROOT 0,0..2,10
  .body[1]
   0] If - 0,0..2,10
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'a' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'c' Store - 2,4..2,5
        .value Constant 3 - 2,8..2,9
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    a = 1;
    b = 2
'''), (None,
r'''c = 3;'''), r'''
if 1:
    a = 1;
    c = 3;
''', r'''
if 1:
    a = 1;
    c = 3
''', r'''
Module - ROOT 0,0..2,10
  .body[1]
   0] If - 0,0..2,10
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'a' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'c' Store - 2,4..2,5
        .value Constant 3 - 2,8..2,9
'''),

('', 1, 1, None, {}, ('_ExceptHandlers',
r'''except a: pass'''), ('ExceptHandler',
r'''except: pass;'''), r'''
except a: pass
except: pass;
''', r'''
except a: pass
except:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..1,13
  .handlers[2]
   0] ExceptHandler - 0,0..0,14
     .type Name 'a' Load - 0,7..0,8
     .body[1]
      0] Pass - 0,10..0,14
   1] ExceptHandler - 1,0..1,13
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', 1, 1, None, {}, ('_match_cases',
r'''case 1: pass'''), ('match_case',
r'''case 2: pass;'''), r'''
case 1: pass
case 2: pass;
''', r'''
case 1: pass
case 2:
    pass
''', r'''
_match_cases - ROOT 0,0..1,13
  .cases[2]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..1,13
     .pattern MatchValue - 1,5..1,6
       .value Constant 2 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
try: pass
except: pass
else: truly_evil\
 ;
finally: pass
'''),
r'''I_banish_thee''', r'''
try: pass
except: pass
else:
    I_banish_thee
finally: pass
''', r'''
Try - ROOT 0,0..4,13
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
  .orelse[1]
   0] Expr - 3,4..3,17
     .value Name 'I_banish_thee' Load - 3,4..3,17
  .finalbody[1]
   0] Pass - 4,9..4,13
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
try: pass
except: pass
else: beyond_truly_evil\
 ; \
\

\
finally: pass
'''),
r'''I_super_duper_banish_thee''',
'try: pass\nexcept: pass\nelse: \n    I_super_duper_banish_thee\n\\\n\n\\\nfinally: pass', r'''
Try - ROOT 0,0..7,13
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
  .orelse[1]
   0] Expr - 3,4..3,29
     .value Name 'I_super_duper_banish_thee' Load - 3,4..3,29
  .finalbody[1]
   0] Pass - 7,9..7,13
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
if 1: pass
else: oh_well\
 ; \
\

'''),
r'''blah''',
'if 1: pass\nelse: \n    blah\n\\\n', r'''
If - ROOT 0,0..2,8
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Pass - 0,6..0,10
  .orelse[1]
   0] Expr - 2,4..2,8
     .value Name 'blah' Load - 2,4..2,8
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
if 1: pass
else: oh_well\
 ; \
\
i = j
'''),
r'''blah''', r'''
if 1: pass
else:
    blah
''', r'''
If - ROOT 0,0..2,8
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Pass - 0,6..0,10
  .orelse[1]
   0] Expr - 2,4..2,8
     .value Name 'blah' Load - 2,4..2,8
'''),

('body[0]', 0, 'end', 'orelse', {}, ('exec', r'''
if 1: pass
else: oh_well\
 ; \
\

i = j
'''),
r'''blah''',
'if 1: pass\nelse: \n    blah\n\n\\\n\ni = j', r'''
Module - ROOT 0,0..6,5
  .body[2]
   0] If - 0,0..2,8
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Expr - 2,4..2,8
        .value Name 'blah' Load - 2,4..2,8
   1] Assign - 6,0..6,5
     .targets[1]
      0] Name 'i' Store - 6,0..6,1
     .value Name 'j' Load - 6,4..6,5
'''),
],

'stmtlike_semicolon': [  # ................................................................................

('', 1, 2, None, {}, (None, r'''
a
    # comment
x ; y
'''), (None,
r'''t'''), r'''
a
t
y
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 't' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'y' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, (None, r'''
a \
; b ; \
c ; \
d
'''), (None,
r'''**DEL**'''), r'''
a \
; \
c ; \
d
''', r'''
Module - ROOT 0,0..3,1
  .body[3]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'c' Load - 2,0..2,1
   2] Expr - 3,0..3,1
     .value Name 'd' Load - 3,0..3,1
'''),
],

'trivia_stmtlike_by_ln': [  # ................................................................................

('', 0, 1, None, {'trivia': (6, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''zzz''', r'''
# ln 0

# ln 2

# ln 4
zzz
''', r'''
Module - ROOT 0,0..5,3
  .body[1]
   0] Expr - 5,0..5,3
     .value Name 'zzz' Load - 5,0..5,3
'''),

('', 0, 1, None, {'trivia': (5, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''zzz''', r'''
# ln 0

# ln 2

# ln 4
zzz
''', r'''
Module - ROOT 0,0..5,3
  .body[1]
   0] Expr - 5,0..5,3
     .value Name 'zzz' Load - 5,0..5,3
'''),

('', 0, 1, None, {'trivia': (4, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''zzz''', r'''
# ln 0

# ln 2

zzz
''', r'''
Module - ROOT 0,0..4,3
  .body[1]
   0] Expr - 4,0..4,3
     .value Name 'zzz' Load - 4,0..4,3
'''),

('', 0, 1, None, {'trivia': (3, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''zzz''', r'''
# ln 0

# ln 2
zzz
''', r'''
Module - ROOT 0,0..3,3
  .body[1]
   0] Expr - 3,0..3,3
     .value Name 'zzz' Load - 3,0..3,3
'''),

('', 0, 1, None, {'trivia': (2, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''zzz''', r'''
# ln 0

zzz
''', r'''
Module - ROOT 0,0..2,3
  .body[1]
   0] Expr - 2,0..2,3
     .value Name 'zzz' Load - 2,0..2,3
'''),

('', 0, 1, None, {'trivia': (1, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''zzz''', r'''
# ln 0
zzz
''', r'''
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 1,0..1,3
     .value Name 'zzz' Load - 1,0..1,3
'''),

('', 0, 1, None, {'trivia': (0, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''zzz''',
r'''zzz''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (-1, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''zzz''',
r'''zzz''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (False, 6)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''zzz''',
r'''zzz''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (False, 5)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''zzz''',
r'''zzz''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (False, 4)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''zzz''', r'''
zzz
# ln 5
''', r'''
Module - ROOT 0,0..1,6
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (False, 3)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''zzz''', r'''
zzz

# ln 5
''', r'''
Module - ROOT 0,0..2,6
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (False, 2)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''zzz''', r'''
zzz
# ln 3

# ln 5
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (False, 1)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''zzz''', r'''
zzz

# ln 3

# ln 5
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (False, 0)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''zzz''', r'''
zzz
# ln 1

# ln 3

# ln 5
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (False, -1)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''zzz''', r'''
zzz
# ln 0
# ln 1

# ln 3

# ln 5
''', r'''
Module - ROOT 0,0..6,6
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (-1, 7)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''),
r'''zzz''',
r'''zzz''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (0, 6)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''),
r'''zzz''',
r'''zzz''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Name 'zzz' Load - 0,0..0,3
'''),

('', 0, 1, None, {'trivia': (1, 5)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 6
'''),
r'''zzz''', r'''
# ln 0
zzz
# ln 6
''', r'''
Module - ROOT 0,0..2,6
  .body[1]
   0] Expr - 1,0..1,3
     .value Name 'zzz' Load - 1,0..1,3
'''),

('', 0, 1, None, {'trivia': (2, 4)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''),
r'''zzz''', r'''
# ln 0

zzz

# ln 5
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] Expr - 2,0..2,3
     .value Name 'zzz' Load - 2,0..2,3
'''),

('', 0, 1, None, {'trivia': (3, 3)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''),
r'''zzz''', r'''
# ln 0

# ln 2
zzz
# ln 4

# ln 5
''', r'''
Module - ROOT 0,0..6,6
  .body[1]
   0] Expr - 3,0..3,3
     .value Name 'zzz' Load - 3,0..3,3
'''),

('', 0, 1, None, {'trivia': (4, 2)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''),
r'''zzz''', r'''
# ln 0

# ln 2
zzz
# ln 3
# ln 4

# ln 5
''', r'''
Module - ROOT 0,0..7,6
  .body[1]
   0] Expr - 3,0..3,3
     .value Name 'zzz' Load - 3,0..3,3
'''),
],

'trivia_exprlike_by_ln': [  # ................................................................................

('', 0, 1, None, {'trivia': (6, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0

# ln 2

# ln 4
zzz
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'zzz' Load - 5,0..5,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (5, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0

# ln 2

# ln 4
zzz
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'zzz' Load - 5,0..5,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (4, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0

# ln 2

zzz
]
''', r'''
List - ROOT 0,0..5,1
  .elts[1]
   0] Name 'zzz' Load - 4,0..4,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (3, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0

# ln 2
zzz
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'zzz' Load - 3,0..3,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (2, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0

zzz
]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Name 'zzz' Load - 2,0..2,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (1, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (0, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (-1, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 6)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 5)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 4)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
# ln 5
]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 3)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz

# ln 5
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 2)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..5,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 1)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz

# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 0)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz # ln 1

# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, -1)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz # ln 1

# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (-1, 7)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (0, 6)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (1, 5)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''),
r'''zzz''', r'''
[ # ln 0
zzz
# ln 6
]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Name 'zzz' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (2, 4)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''),
r'''zzz''', r'''
[ # ln 0

zzz

# ln 6
]
''', r'''
List - ROOT 0,0..5,1
  .elts[1]
   0] Name 'zzz' Load - 2,0..2,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (3, 3)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''),
r'''zzz''', r'''
[ # ln 0

# ln 2
zzz
# ln 4

# ln 6
]
''', r'''
List - ROOT 0,0..7,1
  .elts[1]
   0] Name 'zzz' Load - 3,0..3,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (4, 2)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''),
r'''zzz''', r'''
[ # ln 0

# ln 2
zzz # ln 3
# ln 4

# ln 6
]
''', r'''
List - ROOT 0,0..7,1
  .elts[1]
   0] Name 'zzz' Load - 3,0..3,3
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (1, 1)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''**DEL**''', r'''
a, # 0
c, # 2
''', r'''
Tuple - ROOT 0,0..1,2
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 1,0..1,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (0, 1)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''**DEL**''', r'''
a, # 0
c, # 2
''', r'''
Tuple - ROOT 0,0..1,2
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 1,0..1,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (1, 0)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''**DEL**''', r'''
a, # 0
# 1
c, # 2
''', r'''
Tuple - ROOT 0,0..2,2
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 2,0..2,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (1, 1)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''x''', r'''
a, # 0
x,
c, # 2
''', r'''
Tuple - ROOT 0,0..2,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 1,0..1,1
   2] Name 'c' Load - 2,0..2,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (0, 1)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''x''', r'''
a, # 0
x,
c, # 2
''', r'''
Tuple - ROOT 0,0..2,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 1,0..1,1
   2] Name 'c' Load - 2,0..2,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (1, 0)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''x''', r'''
a, # 0
x, # 1
c, # 2
''', r'''
Tuple - ROOT 0,0..2,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 1,0..1,1
   2] Name 'c' Load - 2,0..2,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (1, 1)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''x # line''', r'''
a, # 0
x, # line
c, # 2
''', r'''
a, # 0
x,
c, # 2
''', r'''
Tuple - ROOT 0,0..2,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 1,0..1,1
   2] Name 'c' Load - 2,0..2,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (0, 1)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''x # line''', r'''
a, # 0
x, # line
c, # 2
''', r'''
a, # 0
x,
c, # 2
''', r'''
Tuple - ROOT 0,0..2,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 1,0..1,1
   2] Name 'c' Load - 2,0..2,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (1, 0)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''),
r'''x # line''', r'''
a, # 0
x, # line
# 1
c, # 2
''', r'''
a, # 0
x, # 1
c, # 2
''', r'''
Tuple - ROOT 0,0..3,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 1,0..1,1
   2] Name 'c' Load - 3,0..3,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (1, 1)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''), r'''
# pre
x # line
# post
''', r'''
a, # 0
# pre
x, # line
# post
c, # 2
''', r'''
a, # 0
x,
c, # 2
''', r'''
Tuple - ROOT 0,0..4,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 2,0..2,1
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (0, 1)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''), r'''
# pre
x # line
# post
''', r'''
a, # 0
# pre
x, # line
# post
c, # 2
''', r'''
a, # 0
x,
c, # 2
''', r'''
Tuple - ROOT 0,0..4,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 2,0..2,1
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

('', 1, 2, None, {'pars': False, 'trivia': (1, 0)}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
'''), r'''
# pre
x # line
# post
''', r'''
a, # 0
# pre
x, # line
# post
# 1
c, # 2
''', r'''
a, # 0
x, # 1
c, # 2
''', r'''
Tuple - ROOT 0,0..5,2
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 2,0..2,1
   2] Name 'c' Load - 5,0..5,1
  .ctx Load
'''),
],

'except_vs_except_star': [  # ................................................................................

('', 1, 1, 'handlers', {'_ver': 11}, (None, r'''
try: pass
except Exception: pass
'''), (None,
r'''except* Exception: pass'''),
r'''**ParseError("expecting plain 'except' handler, got star 'except*'")**'''),

('', 1, 1, 'handlers', {'_ver': 11}, (None, r'''
try: pass
except Exception: pass
'''), (None,
r'''except Exception: pass'''), r'''
try: pass
except Exception: pass
except Exception: pass
''', r'''
try: pass
except Exception: pass
except Exception:
    pass
''', r'''
Try - ROOT 0,0..2,22
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[2]
   0] ExceptHandler - 1,0..1,22
     .type Name 'Exception' Load - 1,7..1,16
     .body[1]
      0] Pass - 1,18..1,22
   1] ExceptHandler - 2,0..2,22
     .type Name 'Exception' Load - 2,7..2,16
     .body[1]
      0] Pass - 2,18..2,22
'''),

('', 0, 1, 'handlers', {'_ver': 11, '_ast': False}, (None, r'''
try: pass
except Exception: pass
'''), (None,
r'''except* Exception: pass'''), r'''
try: pass
except* Exception: pass
''', r'''
TryStar - ROOT 0,0..1,23
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,23
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Pass - 1,19..1,23
'''),

('body[0]', 0, 1, 'handlers', {'_ver': 11, '_ast': False}, ('exec', r'''
try: pass
except Exception: pass
'''), (None,
r'''except* Exception: pass'''), r'''
try: pass
except* Exception: pass
''', r'''
Module - ROOT 0,0..1,23
  .body[1]
   0] TryStar - 0,0..1,23
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,23
        .type Name 'Exception' Load - 1,8..1,17
        .body[1]
         0] Pass - 1,19..1,23
'''),

('', 1, 1, 'handlers', {'_ver': 11}, (None, r'''
try: pass
except* Exception: pass
'''), (None,
r'''except Exception: pass'''),
r'''**ParseError("expecting star 'except*' handler, got plain 'except'")**'''),

('', 1, 1, 'handlers', {'_ver': 11}, (None, r'''
try: pass
except* Exception: pass
'''), (None,
r'''except* Exception: pass'''), r'''
try: pass
except* Exception: pass
except* Exception: pass
''', r'''
try: pass
except* Exception: pass
except* Exception:
    pass
''', r'''
TryStar - ROOT 0,0..2,23
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[2]
   0] ExceptHandler - 1,0..1,23
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Pass - 1,19..1,23
   1] ExceptHandler - 2,0..2,23
     .type Name 'Exception' Load - 2,8..2,17
     .body[1]
      0] Pass - 2,19..2,23
'''),

('', 0, 1, 'handlers', {'_ver': 11, '_ast': False}, (None, r'''
try: pass
except* Exception: pass
'''), (None,
r'''except Exception: pass'''), r'''
try: pass
except Exception: pass
''', r'''
Try - ROOT 0,0..1,22
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,22
     .type Name 'Exception' Load - 1,7..1,16
     .body[1]
      0] Pass - 1,18..1,22
'''),

('body[0]', 0, 1, 'handlers', {'_ver': 11, '_ast': False}, ('exec', r'''
try: pass
except* Exception: pass
'''), (None,
r'''except Exception: pass'''), r'''
try: pass
except Exception: pass
''', r'''
Module - ROOT 0,0..1,22
  .body[1]
   0] Try - 0,0..1,22
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,22
        .type Name 'Exception' Load - 1,7..1,16
        .body[1]
         0] Pass - 1,18..1,22
'''),

('', 1, 1, None, {'_ver': 11}, ('_ExceptHandlers',
r'''except Exception: pass'''), (None,
r'''except* Exception: pass'''),
r'''**ParseError("expecting plain 'except' handler, got star 'except*'")**'''),

('', 0, 1, None, {'_ver': 11}, ('_ExceptHandlers',
r'''except Exception: pass'''), (None,
r'''except* Exception: pass'''),
r'''except* Exception: pass''', r'''
except Exception:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..0,23
  .handlers[1]
   0] ExceptHandler - 0,0..0,23
     .type Name 'Exception' Load - 0,8..0,17
     .body[1]
      0] Pass - 0,19..0,23
'''),

('', 1, 1, None, {'_ver': 11}, ('_ExceptHandlers',
r'''except* Exception: pass'''), (None,
r'''except Exception: pass'''),
r'''**ParseError("expecting star 'except*' handler, got plain 'except'")**'''),

('', 0, 1, None, {'_ver': 11}, ('_ExceptHandlers',
r'''except* Exception: pass'''), (None,
r'''except Exception: pass'''),
r'''except Exception: pass''', r'''
except* Exception:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..0,22
  .handlers[1]
   0] ExceptHandler - 0,0..0,22
     .type Name 'Exception' Load - 0,7..0,16
     .body[1]
      0] Pass - 0,18..0,22
'''),
],

'seq_w_Slice': [  # ................................................................................

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), ('Slice',
r'''x:y:z'''),
r'''x:y:z,''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Slice - 0,0..0,5
     .lower Name 'x' Load - 0,0..0,1
     .upper Name 'y' Load - 0,2..0,3
     .step Name 'z' Load - 0,4..0,5
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), ('expr_slice',
r'''x:y:z,'''),
r'''x:y:z,''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Slice - 0,0..0,5
     .lower Name 'x' Load - 0,0..0,1
     .upper Name 'y' Load - 0,2..0,3
     .step Name 'z' Load - 0,4..0,5
  .ctx Load
'''),

('', 0, 'end', None, {'_verify': False}, (None,
r'''(a, b, c)'''), ('Slice',
r'''x:y:z'''),
r'''(x:y:z,)''', r'''
Tuple - ROOT 0,0..0,8
  .elts[1]
   0] Slice - 0,1..0,6
     .lower Name 'x' Load - 0,1..0,2
     .upper Name 'y' Load - 0,3..0,4
     .step Name 'z' Load - 0,5..0,6
  .ctx Load
'''),

('', 0, 'end', None, {'_verify': False}, (None,
r'''(a, b, c)'''), ('expr_slice',
r'''x:y:z,'''),
r'''(x:y:z,)''', r'''
Tuple - ROOT 0,0..0,8
  .elts[1]
   0] Slice - 0,1..0,6
     .lower Name 'x' Load - 0,1..0,2
     .upper Name 'y' Load - 0,3..0,4
     .step Name 'z' Load - 0,5..0,6
  .ctx Load
'''),

('value', 0, 'end', None, {}, ('Expr',
r'''a, b, c'''), ('Slice',
r'''x:y:z'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('value', 0, 'end', None, {}, ('Expr',
r'''a, b, c'''), ('expr_slice',
r'''x:y:z,'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('value', 0, 'end', None, {'_verify': False}, ('Expr',
r'''(a, b, c)'''), ('Slice',
r'''x:y:z'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('value', 0, 'end', None, {'_verify': False}, ('Expr',
r'''(a, b, c)'''), ('expr_slice',
r'''x:y:z,'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('body[0].value', 0, 'end', None, {}, ('exec',
r'''a, b, c'''), ('Slice',
r'''x:y:z'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('body[0].value', 0, 'end', None, {}, ('exec',
r'''a, b, c'''), ('expr_slice',
r'''x:y:z,'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('body[0].value', 0, 'end', None, {'_verify': False}, ('exec',
r'''(a, b, c)'''), ('Slice',
r'''x:y:z'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('body[0].value', 0, 'end', None, {'_verify': False}, ('exec',
r'''(a, b, c)'''), ('expr_slice',
r'''x:y:z,'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('slice', 0, 'end', None, {}, (None,
r'''s[a, b, c]'''), ('Slice',
r'''x:y:z'''),
r'''s[x:y:z,]''', r'''
Subscript - ROOT 0,0..0,9
  .value Name 's' Load - 0,0..0,1
  .slice Tuple - 0,2..0,8
    .elts[1]
     0] Slice - 0,2..0,7
       .lower Name 'x' Load - 0,2..0,3
       .upper Name 'y' Load - 0,4..0,5
       .step Name 'z' Load - 0,6..0,7
    .ctx Load
  .ctx Load
'''),

('slice', 0, 'end', None, {}, (None,
r'''s[a, b, c]'''), ('expr_slice',
r'''x:y:z,'''),
r'''s[x:y:z,]''', r'''
Subscript - ROOT 0,0..0,9
  .value Name 's' Load - 0,0..0,1
  .slice Tuple - 0,2..0,8
    .elts[1]
     0] Slice - 0,2..0,7
       .lower Name 'x' Load - 0,2..0,3
       .upper Name 'y' Load - 0,4..0,5
       .step Name 'z' Load - 0,6..0,7
    .ctx Load
  .ctx Load
'''),

('slice', 0, 'end', None, {'_verify': False}, (None,
r'''s[(a, b, c)]'''), ('Slice',
r'''x:y:z'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('slice', 0, 'end', None, {'_verify': False}, (None,
r'''s[(a, b, c)]'''), ('expr_slice',
r'''x:y:z,'''),
r'''**NodeError('cannot put Slice into non-root non-unparenthesized-slice Tuple')**'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('value', 0, 'end', None, {}, ('Expr',
r'''[a, b, c]'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('value', 0, 'end', None, {}, ('Expr',
r'''[a, b, c]'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0].value', 0, 'end', None, {}, ('exec',
r'''[a, b, c]'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0].value', 0, 'end', None, {}, ('exec',
r'''[a, b, c]'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('slice', 0, 'end', None, {'_verify': False}, (None,
r'''s[[a, b, c]]'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('slice', 0, 'end', None, {'_verify': False}, (None,
r'''s[[a, b, c]]'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('value', 0, 'end', None, {}, ('Expr',
r'''{a, b, c}'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('value', 0, 'end', None, {}, ('Expr',
r'''{a, b, c}'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0].value', 0, 'end', None, {}, ('exec',
r'''{a, b, c}'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0].value', 0, 'end', None, {}, ('exec',
r'''{a, b, c}'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('slice', 0, 'end', None, {'_verify': False}, (None,
r'''s[{a, b, c}]'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('slice', 0, 'end', None, {'_verify': False}, (None,
r'''s[{a, b, c}]'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''del a, b, c'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''del a, b, c'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''global a, b, c'''), ('Slice',
r'''x:y:z'''),
r'''**SyntaxError('invalid syntax')**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''global a, b, c'''), ('expr_slice',
r'''x:y:z,'''),
r'''**SyntaxError('invalid syntax')**'''),
],

'Tuple_elts': [  # ................................................................................

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), (None,
r'''x'''),
r'''x,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'x' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), (None,
r'''x.y'''),
r'''x.y,''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Attribute - 0,0..0,3
     .value Name 'x' Load - 0,0..0,1
     .attr 'y'
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), (None,
r'''x[y]'''),
r'''x[y],''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Subscript - 0,0..0,4
     .value Name 'x' Load - 0,0..0,1
     .slice Name 'y' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), (None,
r'''*x'''),
r'''*x,''', r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 'x' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), (None,
r'''x,'''),
r'''x,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'x' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''a, b, c'''), (None,
r'''x,'''),
r'''(x,),''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Tuple - 0,0..0,4
     .elts[1]
      0] Name 'x' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), (None,
r'''(x,)'''),
r'''x,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'x' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''a, b, c'''), (None,
r'''(x,)'''),
r'''(x,),''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Tuple - 0,0..0,4
     .elts[1]
      0] Name 'x' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), (None,
r'''[x]'''),
r'''x,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'x' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''a, b, c'''), (None,
r'''[x]'''),
r'''[x],''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] List - 0,0..0,3
     .elts[1]
      0] Name 'x' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''a, b, c'''), (None,
r'''{x}'''),
r'''x,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'x' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''a, b, c'''), (None,
r'''{x}'''),
r'''{x},''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Set - 0,0..0,3
     .elts[1]
      0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''a, b, c'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to Tuple without 'one=True' or 'coerce=True'")**'''),

('', 0, 'end', None, {'coerce': False, 'one': True}, (None,
r'''a, b, c'''), (None,
r'''x'''),
r'''x,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'x' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''(a, b, c)'''), (None,
r'''x'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''(a, b, c)'''), (None,
r'''x.y'''),
r'''(x.y,)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Attribute - 0,1..0,4
     .value Name 'x' Load - 0,1..0,2
     .attr 'y'
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''(a, b, c)'''), (None,
r'''x[y]'''),
r'''(x[y],)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[1]
   0] Subscript - 0,1..0,5
     .value Name 'x' Load - 0,1..0,2
     .slice Name 'y' Load - 0,3..0,4
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''(a, b, c)'''), (None,
r'''*x'''),
r'''(*x,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''(a, b, c)'''), (None,
r'''x,'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''(a, b, c)'''), (None,
r'''x,'''),
r'''((x,),)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[1]
   0] Tuple - 0,1..0,5
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''(a, b, c)'''), (None,
r'''(x,)'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''(a, b, c)'''), (None,
r'''(x,)'''),
r'''((x,),)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[1]
   0] Tuple - 0,1..0,5
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''(a, b, c)'''), (None,
r'''[x]'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''(a, b, c)'''), (None,
r'''[x]'''),
r'''([x],)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] List - 0,1..0,4
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''(a, b, c)'''), (None,
r'''{x}'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''(a, b, c)'''), (None,
r'''{x}'''),
r'''({x},)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Set - 0,1..0,4
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
  .ctx Load
'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''(a, b, c)'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to Tuple without 'one=True' or 'coerce=True'")**'''),

('', 0, 'end', None, {'coerce': False, 'one': True}, (None,
r'''(a, b, c)'''), (None,
r'''x'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 1, 3, None, {'pars': 'auto'}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
d, # 3
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
(a, # 0
x, # 9
y, # 0
d, # 3
)
''', r'''
(a, # 0
x, y,
d, # 3
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,0..1,1
   2] Name 'y' Load - 2,0..2,1
   3] Name 'd' Load - 3,0..3,1
  .ctx Load
'''),

('', 1, 3, None, {'pars': True}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
d, # 3
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
(a, # 0
x, # 9
y, # 0
d, # 3
)
''', r'''
(a, # 0
x, y,
d, # 3
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,0..1,1
   2] Name 'y' Load - 2,0..2,1
   3] Name 'd' Load - 3,0..3,1
  .ctx Load
'''),

('', 1, 3, None, {'pars': False}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
d, # 3
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
a, # 0
x, # 9
y, # 0
d, # 3
''', r'''
a, # 0
x, y,
d, # 3
''', r'''
Tuple - ROOT 0,0..3,2
  .elts[4]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 1,0..1,1
   2] Name 'y' Load - 2,0..2,1
   3] Name 'd' Load - 3,0..3,1
  .ctx Load
'''),

('', 1, 3, None, {'pars': 'auto'}, ('Tuple', r'''
(
    a, # 0
    b, # 1
    c, # 2
    d, # 3
)
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
(
    a, # 0
    x, # 9
    y, # 0
    d, # 3
)
''', r'''
(
    a, # 0
    x, y,
    d, # 3
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[4]
   0] Name 'a' Load - 1,4..1,5
   1] Name 'x' Load - 2,4..2,5
   2] Name 'y' Load - 3,4..3,5
   3] Name 'd' Load - 4,4..4,5
  .ctx Load
'''),

('', 1, 3, None, {'pars': True}, ('Tuple', r'''
(
    a, # 0
    b, # 1
    c, # 2
    d, # 3
)
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
(
    a, # 0
    x, # 9
    y, # 0
    d, # 3
)
''', r'''
(
    a, # 0
    x, y,
    d, # 3
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[4]
   0] Name 'a' Load - 1,4..1,5
   1] Name 'x' Load - 2,4..2,5
   2] Name 'y' Load - 3,4..3,5
   3] Name 'd' Load - 4,4..4,5
  .ctx Load
'''),

('', 1, 3, None, {'pars': False}, ('Tuple', r'''
(
    a, # 0
    b, # 1
    c, # 2
    d, # 3
)
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
(
    a, # 0
    x, # 9
    y, # 0
    d, # 3
)
''', r'''
(
    a, # 0
    x, y,
    d, # 3
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[4]
   0] Name 'a' Load - 1,4..1,5
   1] Name 'x' Load - 2,4..2,5
   2] Name 'y' Load - 3,4..3,5
   3] Name 'd' Load - 4,4..4,5
  .ctx Load
'''),

('value', 1, 3, None, {'pars': 'auto'}, (None,
r'''i = a, b, c, d'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
i = (a, x, # 9
    y, # 0
    d)
''',
r'''i = a, x, y, d''', r'''
Assign - ROOT 0,0..2,6
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..2,6
    .elts[4]
     0] Name 'a' Load - 0,5..0,6
     1] Name 'x' Load - 0,8..0,9
     2] Name 'y' Load - 1,4..1,5
     3] Name 'd' Load - 2,4..2,5
    .ctx Load
'''),

('value', 1, 3, None, {'pars': True}, (None,
r'''i = a, b, c, d'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
i = (a, x, # 9
    y, # 0
    d)
''',
r'''i = a, x, y, d''', r'''
Assign - ROOT 0,0..2,6
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..2,6
    .elts[4]
     0] Name 'a' Load - 0,5..0,6
     1] Name 'x' Load - 0,8..0,9
     2] Name 'y' Load - 1,4..1,5
     3] Name 'd' Load - 2,4..2,5
    .ctx Load
'''),

('value', 1, 3, None, {'pars': False}, (None,
r'''i = a, b, c, d'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
i = (a, x, # 9
    y, # 0
    d)
''',
r'''i = a, x, y, d''', r'''
Assign - ROOT 0,0..2,6
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..2,6
    .elts[4]
     0] Name 'a' Load - 0,5..0,6
     1] Name 'x' Load - 0,8..0,9
     2] Name 'y' Load - 1,4..1,5
     3] Name 'd' Load - 2,4..2,5
    .ctx Load
'''),

('value', 1, 3, None, {'pars': 'auto'}, (None, r'''
i = a, \
    b, \
    c, \
    d,
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
i = (a, \
    x, # 9
    y, # 0
    d,)
''', r'''
i = (a, \
    x, y,
    d,)
''', r'''
Assign - ROOT 0,0..3,7
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..3,7
    .elts[4]
     0] Name 'a' Load - 0,5..0,6
     1] Name 'x' Load - 1,4..1,5
     2] Name 'y' Load - 2,4..2,5
     3] Name 'd' Load - 3,4..3,5
    .ctx Load
'''),

('value', 1, 3, None, {'pars': True}, (None, r'''
i = a, \
    b, \
    c, \
    d,
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
i = (a, \
    x, # 9
    y, # 0
    d,)
''', r'''
i = (a, \
    x, y,
    d,)
''', r'''
Assign - ROOT 0,0..3,7
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..3,7
    .elts[4]
     0] Name 'a' Load - 0,5..0,6
     1] Name 'x' Load - 1,4..1,5
     2] Name 'y' Load - 2,4..2,5
     3] Name 'd' Load - 3,4..3,5
    .ctx Load
'''),

('value', 1, 3, None, {'pars': False}, (None, r'''
i = a, \
    b, \
    c, \
    d,
'''), ('Tuple', r'''
x, # 9
y, # 0
'''), r'''
i = (a, \
    x, # 9
    y, # 0
    d,)
''', r'''
i = (a, \
    x, y,
    d,)
''', r'''
Assign - ROOT 0,0..3,7
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..3,7
    .elts[4]
     0] Name 'a' Load - 0,5..0,6
     1] Name 'x' Load - 1,4..1,5
     2] Name 'y' Load - 2,4..2,5
     3] Name 'd' Load - 3,4..3,5
    .ctx Load
'''),
],

'List_elts': [  # ................................................................................

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), (None,
r'''x'''),
r'''[x]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), (None,
r'''x.y'''),
r'''[x.y]''', r'''
List - ROOT 0,0..0,5
  .elts[1]
   0] Attribute - 0,1..0,4
     .value Name 'x' Load - 0,1..0,2
     .attr 'y'
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), (None,
r'''x[y]'''),
r'''[x[y]]''', r'''
List - ROOT 0,0..0,6
  .elts[1]
   0] Subscript - 0,1..0,5
     .value Name 'x' Load - 0,1..0,2
     .slice Name 'y' Load - 0,3..0,4
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), (None,
r'''*x'''),
r'''[*x]''', r'''
List - ROOT 0,0..0,4
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), (None,
r'''x,'''),
r'''[x]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''[a, b, c]'''), (None,
r'''x,'''),
r'''[(x,)]''', r'''
List - ROOT 0,0..0,6
  .elts[1]
   0] Tuple - 0,1..0,5
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), (None,
r'''(x,)'''),
r'''[x]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''[a, b, c]'''), (None,
r'''(x,)'''),
r'''[(x,)]''', r'''
List - ROOT 0,0..0,6
  .elts[1]
   0] Tuple - 0,1..0,5
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), (None,
r'''[x]'''),
r'''[x]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''[a, b, c]'''), (None,
r'''[x]'''),
r'''[[x]]''', r'''
List - ROOT 0,0..0,5
  .elts[1]
   0] List - 0,1..0,4
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''[a, b, c]'''), (None,
r'''{x}'''),
r'''[x]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''[a, b, c]'''), (None,
r'''{x}'''),
r'''[{x}]''', r'''
List - ROOT 0,0..0,5
  .elts[1]
   0] Set - 0,1..0,4
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
  .ctx Load
'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''[a, b, c]'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to List without 'one=True' or 'coerce=True'")**'''),

('', 0, 'end', None, {'coerce': False, 'one': True}, (None,
r'''[a, b, c]'''), (None,
r'''x'''),
r'''[x]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),
],

'Set_elts': [  # ................................................................................

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), (None,
r'''x'''),
r'''{x}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), (None,
r'''x.y'''),
r'''{x.y}''', r'''
Set - ROOT 0,0..0,5
  .elts[1]
   0] Attribute - 0,1..0,4
     .value Name 'x' Load - 0,1..0,2
     .attr 'y'
     .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), (None,
r'''x[y]'''),
r'''{x[y]}''', r'''
Set - ROOT 0,0..0,6
  .elts[1]
   0] Subscript - 0,1..0,5
     .value Name 'x' Load - 0,1..0,2
     .slice Name 'y' Load - 0,3..0,4
     .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), (None,
r'''*x'''),
r'''{*x}''', r'''
Set - ROOT 0,0..0,4
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'x' Load - 0,2..0,3
     .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), (None,
r'''x,'''),
r'''{x}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''{a, b, c}'''), (None,
r'''x,'''),
r'''{(x,)}''', r'''
Set - ROOT 0,0..0,6
  .elts[1]
   0] Tuple - 0,1..0,5
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), (None,
r'''(x,)'''),
r'''{x}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''{a, b, c}'''), (None,
r'''(x,)'''),
r'''{(x,)}''', r'''
Set - ROOT 0,0..0,6
  .elts[1]
   0] Tuple - 0,1..0,5
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), (None,
r'''[x]'''),
r'''{x}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''{a, b, c}'''), (None,
r'''[x]'''),
r'''{[x]}''', r'''
Set - ROOT 0,0..0,5
  .elts[1]
   0] List - 0,1..0,4
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
'''),

('', 0, 'end', None, {}, (None,
r'''{a, b, c}'''), (None,
r'''{x}'''),
r'''{x}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''{a, b, c}'''), (None,
r'''{x}'''),
r'''{{x}}''', r'''
Set - ROOT 0,0..0,5
  .elts[1]
   0] Set - 0,1..0,4
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''{a, b, c}'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to Set without 'one=True' or 'coerce=True'")**'''),

('', 0, 'end', None, {'coerce': False, 'one': True}, (None,
r'''{a, b, c}'''), (None,
r'''x'''),
r'''{x}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
'''),
],

'Delete_targets': [  # ................................................................................

('body[0]', 0, 'end', None, {}, ('exec',
r'''del a, b, c'''), (None,
r'''x,'''),
r'''del x''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'x' Del - 0,4..0,5
'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''del a, b, c'''), (None,
r'''x'''),
r'''del x''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'x' Del - 0,4..0,5
'''),

('body[0]', 0, 'end', None, {'one': True}, ('exec',
r'''del a, b, c'''), (None,
r'''x'''),
r'''del x''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'x' Del - 0,4..0,5
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''del a, b, c'''), (None,
r'''()'''),
r'''del a, c''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Delete - 0,0..0,8
     .targets[2]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'c' Del - 0,7..0,8
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''del a, b, c'''), (None,
r'''(),'''),
r'''del a, (), c''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Delete - 0,0..0,12
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Tuple - 0,7..0,9
        .ctx Del
      2] Name 'c' Del - 0,11..0,12
'''),

('body[0]', 1, 2, None, {'one': True}, ('exec',
r'''del a, b, c'''), (None,
r'''()'''),
r'''del a, (), c''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Delete - 0,0..0,12
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Tuple - 0,7..0,9
        .ctx Del
      2] Name 'c' Del - 0,11..0,12
'''),

('body[0]', 1, 2, None, {'one': True}, ('exec',
r'''del a, b, c'''), (None,
r'''(),'''),
r'''del a, ((),), c''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] Delete - 0,0..0,15
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Tuple - 0,7..0,12
        .elts[1]
         0] Tuple - 0,8..0,10
           .ctx Del
        .ctx Del
      2] Name 'c' Del - 0,14..0,15
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''del a, b, c'''), (None, r'''
x
.
y
'''), r'''
del a, x \
    . \
    y, c
''',
r'''del a, x.y, c''', r'''
Module - ROOT 0,0..2,8
  .body[1]
   0] Delete - 0,0..2,8
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Attribute - 0,7..2,5
        .value Name 'x' Load - 0,7..0,8
        .attr 'y'
        .ctx Del
      2] Name 'c' Del - 2,7..2,8
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''del a, b, c'''), (None, r'''
x
,
'''), r'''
del a, x \
    , c
''',
r'''del a, x, c''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Delete - 0,0..1,7
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'x' Del - 0,7..0,8
      2] Name 'c' Del - 1,6..1,7
'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''del a, b, c'''), (None, r'''
x \

'''), r'''
del x \

''',
r'''del x''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'x' Del - 0,4..0,5
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  del a
'''), (None, r'''
(
    b \
    , \
  )
'''),
'if 1:\n  del a, \\\n      b \\\n       \\\n    ', r'''
if 1:
  del a, b
''', r'''
Module - ROOT 0,0..4,4
  .body[1]
   0] If - 0,0..2,7
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Delete - 1,2..2,7
        .targets[2]
         0] Name 'a' Del - 1,6..1,7
         1] Name 'b' Del - 2,6..2,7
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  del a
'''), (None, r'''
(
    b, \
)
'''), r'''
if 1:
  del a, \
      b \

''', r'''
if 1:
  del a, b
''', r'''
Module - ROOT 0,0..3,0
  .body[1]
   0] If - 0,0..2,7
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Delete - 1,2..2,7
        .targets[2]
         0] Name 'a' Del - 1,6..1,7
         1] Name 'b' Del - 2,6..2,7
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  del a
'''), (None, r'''
(
    b,
)
'''), r'''
if 1:
  del a, \
      b

''', r'''
if 1:
  del a, b
''', r'''
Module - ROOT 0,0..3,0
  .body[1]
   0] If - 0,0..2,7
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Delete - 1,2..2,7
        .targets[2]
         0] Name 'a' Del - 1,6..1,7
         1] Name 'b' Del - 2,6..2,7
'''),

('', 1, 2, None, {}, (None,
r'''del a, b, c'''), (None, r'''
(x,  # blah
# blah
)  # blah
'''), r'''
del a, x, \
    \
    c
''',
r'''del a, x, c''', r'''
Delete - ROOT 0,0..2,5
  .targets[3]
   0] Name 'a' Del - 0,4..0,5
   1] Name 'x' Del - 0,7..0,8
   2] Name 'c' Del - 2,4..2,5
'''),

('', 1, 2, None, {}, (None,
r'''del a, b, c'''), (None, r'''
x,  # blah
  # blah
y  # blah
'''), r'''
del a, x, \
      \
    y, \
    c
''',
r'''**NodeError('expecting expression (standard), got multiple statements')**''', r'''
Delete - ROOT 0,0..3,5
  .targets[4]
   0] Name 'a' Del - 0,4..0,5
   1] Name 'x' Del - 0,7..0,8
   2] Name 'y' Del - 2,4..2,5
   3] Name 'c' Del - 3,4..3,5
'''),

('body[0]', 1, 1, None, {}, (None, r'''
if 1:
  del x;
'''), (None,
r'''y'''), r'''
if 1:
  del x, y;
''', r'''
If - ROOT 0,0..1,11
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Delete - 1,2..1,10
     .targets[2]
      0] Name 'x' Del - 1,6..1,7
      1] Name 'y' Del - 1,9..1,10
'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''x'''),
r'''del x''', r'''
Delete - ROOT 0,0..0,5
  .targets[1]
   0] Name 'x' Del - 0,4..0,5
'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''x.y'''),
r'''del x.y''', r'''
Delete - ROOT 0,0..0,7
  .targets[1]
   0] Attribute - 0,4..0,7
     .value Name 'x' Load - 0,4..0,5
     .attr 'y'
     .ctx Del
'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''x[y]'''),
r'''del x[y]''', r'''
Delete - ROOT 0,0..0,8
  .targets[1]
   0] Subscript - 0,4..0,8
     .value Name 'x' Load - 0,4..0,5
     .slice Name 'y' Load - 0,6..0,7
     .ctx Del
'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''*x'''),
r'''**NodeError('invalid slice for Delete target')**'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''x,'''),
r'''del x''', r'''
Delete - ROOT 0,0..0,5
  .targets[1]
   0] Name 'x' Del - 0,4..0,5
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''del a, b, c'''), (None,
r'''x,'''),
r'''del (x,)''', r'''
Delete - ROOT 0,0..0,8
  .targets[1]
   0] Tuple - 0,4..0,8
     .elts[1]
      0] Name 'x' Del - 0,5..0,6
     .ctx Del
'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''(x,)'''),
r'''del x''', r'''
Delete - ROOT 0,0..0,5
  .targets[1]
   0] Name 'x' Del - 0,4..0,5
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''del a, b, c'''), (None,
r'''(x,)'''),
r'''del (x,)''', r'''
Delete - ROOT 0,0..0,8
  .targets[1]
   0] Tuple - 0,4..0,8
     .elts[1]
      0] Name 'x' Del - 0,5..0,6
     .ctx Del
'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''[x]'''),
r'''del x''', r'''
Delete - ROOT 0,0..0,5
  .targets[1]
   0] Name 'x' Del - 0,4..0,5
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''del a, b, c'''), (None,
r'''[x]'''),
r'''del [x]''', r'''
Delete - ROOT 0,0..0,7
  .targets[1]
   0] List - 0,4..0,7
     .elts[1]
      0] Name 'x' Del - 0,5..0,6
     .ctx Del
'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''{x}'''),
r'''del x''', r'''
Delete - ROOT 0,0..0,5
  .targets[1]
   0] Name 'x' Del - 0,4..0,5
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''del a, b, c'''), (None,
r'''{x}'''),
r'''**NodeError('invalid slice for Delete target')**'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''del a, b, c'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to Delete without 'one=True' or 'coerce=True'")**'''),

('', 0, 'end', None, {'coerce': False, 'one': True}, (None,
r'''del a, b, c'''), (None,
r'''x'''),
r'''del x''', r'''
Delete - ROOT 0,0..0,5
  .targets[1]
   0] Name 'x' Del - 0,4..0,5
'''),

('', 0, 'end', None, {}, (None,
r'''del a, b, c'''), (None,
r'''f()'''),
r'''**NodeError('invalid slice for Delete target')**'''),

('', 0, 'end', None, {'one': True}, (None,
r'''del a, b, c'''), (None,
r'''f()'''),
r'''**NodeError('invalid slice for Delete target')**'''),
],

'Delete_targets_semicolon': [  # ................................................................................

('body[0]', 2, 2, None, {}, ('exec',
r'''del a, b ; del c'''), ('Tuple',
r'''d,  # comment'''),
r'''del a, b, d ; del c''', r'''
Module - ROOT 0,0..0,19
  .body[2]
   0] Delete - 0,0..0,11
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,7..0,8
      2] Name 'd' Del - 0,10..0,11
   1] Delete - 0,14..0,19
     .targets[1]
      0] Name 'c' Del - 0,18..0,19
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''del a, b ; del c'''), ('Tuple', r'''
d,
e

'''), r'''
del a, b, d, \
    e ; del c
''',
r'''del a, b, d, e ; del c''', r'''
Module - ROOT 0,0..1,13
  .body[2]
   0] Delete - 0,0..1,5
     .targets[4]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,7..0,8
      2] Name 'd' Del - 0,10..0,11
      3] Name 'e' Del - 1,4..1,5
   1] Delete - 1,8..1,13
     .targets[1]
      0] Name 'c' Del - 1,12..1,13
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''del a, b ; del c'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
del a, b, d, \
    e ; del c
''',
r'''del a, b, d, e ; del c''', r'''
Module - ROOT 0,0..1,13
  .body[2]
   0] Delete - 0,0..1,5
     .targets[4]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,7..0,8
      2] Name 'd' Del - 0,10..0,11
      3] Name 'e' Del - 1,4..1,5
   1] Delete - 1,8..1,13
     .targets[1]
      0] Name 'c' Del - 1,12..1,13
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''del a, b ;'''), ('Tuple',
r'''d,  # comment'''),
r'''del a, b, d ;''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Delete - 0,0..0,11
     .targets[3]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,7..0,8
      2] Name 'd' Del - 0,10..0,11
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''del a, b ;'''), ('Tuple', r'''
d,
e

'''), r'''
del a, b, d, \
    e ;
''',
r'''del a, b, d, e ;''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Delete - 0,0..1,5
     .targets[4]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,7..0,8
      2] Name 'd' Del - 0,10..0,11
      3] Name 'e' Del - 1,4..1,5
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''del a, b ;'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
del a, b, d, \
    e ;
''',
r'''del a, b, d, e ;''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Delete - 0,0..1,5
     .targets[4]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'b' Del - 0,7..0,8
      2] Name 'd' Del - 0,10..0,11
      3] Name 'e' Del - 1,4..1,5
'''),

('', 2, 2, None, {}, (None,
r'''del a, b ;'''), ('Tuple',
r'''d,  # comment'''),
r'''del a, b, d ;''', r'''
Delete - ROOT 0,0..0,11
  .targets[3]
   0] Name 'a' Del - 0,4..0,5
   1] Name 'b' Del - 0,7..0,8
   2] Name 'd' Del - 0,10..0,11
'''),

('', 2, 2, None, {}, (None,
r'''del a, b ;'''), ('Tuple', r'''
d,
e

'''), r'''
del a, b, d, \
    e ;
''',
r'''del a, b, d, e ;''', r'''
Delete - ROOT 0,0..1,5
  .targets[4]
   0] Name 'a' Del - 0,4..0,5
   1] Name 'b' Del - 0,7..0,8
   2] Name 'd' Del - 0,10..0,11
   3] Name 'e' Del - 1,4..1,5
'''),

('', 2, 2, None, {}, (None,
r'''del a, b ;'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
del a, b, d, \
    e ;
''',
r'''del a, b, d, e ;''', r'''
Delete - ROOT 0,0..1,5
  .targets[4]
   0] Name 'a' Del - 0,4..0,5
   1] Name 'b' Del - 0,7..0,8
   2] Name 'd' Del - 0,10..0,11
   3] Name 'e' Del - 1,4..1,5
'''),
],

'Assign_targets': [  # ................................................................................

('body[0]', 0, 'end', 'targets', {}, ('exec',
r'''a = b = c = d'''), ('_Assign_targets',
r'''x'''),
r'''x = d''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'x' Store - 0,0..0,1
     .value Name 'd' Load - 0,4..0,5
'''),

('body[0]', 0, 'end', 'targets', {'one': True}, ('exec',
r'''a = b = c = d'''), (None,
r'''x'''),
r'''x = d''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'x' Store - 0,0..0,1
     .value Name 'd' Load - 0,4..0,5
'''),

('body[0]', 0, 'end', 'targets', {}, ('exec',
r'''a = b = c = d'''), (None,
r'''x ='''),
r'''x = d''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'x' Store - 0,0..0,1
     .value Name 'd' Load - 0,4..0,5
'''),

('body[0]', 1, 2, 'targets', {}, ('exec',
r'''a = b = c = d'''), ('_Assign_targets', r'''
x \
. \
y \
= \
z
'''), r'''
a = x \
. \
y \
= \
z = c = d
''',
r'''a = x.y = z = c = d''', r'''
Module - ROOT 0,0..4,9
  .body[1]
   0] Assign - 0,0..4,9
     .targets[4]
      0] Name 'a' Store - 0,0..0,1
      1] Attribute - 0,4..2,1
        .value Name 'x' Load - 0,4..0,5
        .attr 'y'
        .ctx Store
      2] Name 'z' Store - 4,0..4,1
      3] Name 'c' Store - 4,4..4,5
     .value Name 'd' Load - 4,8..4,9
'''),

('body[0]', 0, 'end', 'targets', {}, ('exec',
r'''a = b = c = d'''), ('_Assign_targets', r'''
x \

'''), r'''
x = \
 d
''',
r'''x = d''', r'''
Module - ROOT 0,0..1,2
  .body[1]
   0] Assign - 0,0..1,2
     .targets[1]
      0] Name 'x' Store - 0,0..0,1
     .value Name 'd' Load - 1,1..1,2
'''),

('body[0]', 0, 'end', 'targets', {}, ('exec',
r'''a = b = c = d'''), ('_Assign_targets', r'''

x \

'''), r'''
x = \
 d
''',
r'''x = d''', r'''
Module - ROOT 0,0..1,2
  .body[1]
   0] Assign - 0,0..1,2
     .targets[1]
      0] Name 'x' Store - 0,0..0,1
     .value Name 'd' Load - 1,1..1,2
'''),

('', 0, 'end', 'targets', {'norm': True}, (None,
r'''a = b = c = d'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all Assign.targets without norm_self=False')**'''),

('', 0, 'end', 'targets', {'norm_self': False, '_verify_self': False}, (None,
r'''a = b = c = d'''),
r'''**DEL**''',
r''' d''', r'''
Assign - ROOT 0,0..0,2
  .value Name 'd' Load - 0,1..0,2
'''),

('', 0, 'end', 'targets', {}, ('_Assign_targets',
r'''a = b = c ='''), ('_Assign_targets',
r'''x'''),
r'''x =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'x' Store - 0,0..0,1
'''),

('', 0, 'end', 'targets', {'one': True}, ('_Assign_targets',
r'''a = b = c ='''), (None,
r'''x'''),
r'''x =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'x' Store - 0,0..0,1
'''),

('', 0, 'end', 'targets', {}, ('_Assign_targets',
r'''a = b = c ='''), (None,
r'''x ='''),
r'''x =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'x' Store - 0,0..0,1
'''),

('', 1, 2, 'targets', {}, ('_Assign_targets',
r'''a = b = c ='''), ('_Assign_targets', r'''
x \
. \
y \
= \
z
'''), r'''
a = x \
. \
y \
= \
z = c =
''',
r'''a = x.y = z = c =''', r'''
_Assign_targets - ROOT 0,0..4,7
  .targets[4]
   0] Name 'a' Store - 0,0..0,1
   1] Attribute - 0,4..2,1
     .value Name 'x' Load - 0,4..0,5
     .attr 'y'
     .ctx Store
   2] Name 'z' Store - 4,0..4,1
   3] Name 'c' Store - 4,4..4,5
'''),

('', 0, 'end', 'targets', {}, ('_Assign_targets',
r'''a = b = c ='''), ('_Assign_targets', r'''
x \

'''), r'''
x = \

''',
r'''x =''', r'''
_Assign_targets - ROOT 0,0..1,0
  .targets[1]
   0] Name 'x' Store - 0,0..0,1
'''),

('', 0, 'end', 'targets', {}, ('_Assign_targets',
r'''a = b = c ='''), ('_Assign_targets', r'''

x \

'''), r'''
x = \

''',
r'''x =''', r'''
_Assign_targets - ROOT 0,0..1,0
  .targets[1]
   0] Name 'x' Store - 0,0..0,1
'''),
],

'Assign_targets_coerce': [  # ................................................................................

('', 1, 3, 'targets', {'one': True}, (None,
r'''a = b = c = d'''), ('_Assign_targets',
r'''x = y ='''),
r'''a = x = y = d''', r'''
Assign - ROOT 0,0..0,13
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
   2] Name 'y' Store - 0,8..0,9
  .value Name 'd' Load - 0,12..0,13
'''),

('', 1, 3, 'targets', {'one': True, 'coerce': False}, (None,
r'''a = b = c = d'''), ('_Assign_targets',
r'''x = y ='''),
r'''a = x = y = d''',
r'''**ValueError("cannot put _Assign_targets node as 'one=True' without 'coerce=True'")**''', r'''
Assign - ROOT 0,0..0,13
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
   2] Name 'y' Store - 0,8..0,9
  .value Name 'd' Load - 0,12..0,13
'''),

('', 1, 3, 'targets', {}, (None,
r'''a = b = c = d'''), ('Name',
r'''x'''),
r'''a = x = d''', r'''
Assign - ROOT 0,0..0,9
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
  .value Name 'd' Load - 0,8..0,9
'''),

('', 1, 3, 'targets', {'coerce': False}, (None,
r'''a = b = c = d'''), ('Name',
r'''x'''),
r'''a = x = d''',
r'''**NodeError('expecting _Assign_targets, got Name')**''', r'''
Assign - ROOT 0,0..0,9
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
  .value Name 'd' Load - 0,8..0,9
'''),

('', 1, 3, 'targets', {'coerce': False, 'one': True}, (None,
r'''a = b = c = d'''), ('Name',
r'''x'''),
r'''a = x = d''', r'''
Assign - ROOT 0,0..0,9
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
  .value Name 'd' Load - 0,8..0,9
'''),

('', 1, 3, 'targets', {'one': True}, ('_Assign_targets',
r'''a = b = c ='''), ('_Assign_targets',
r'''x = y ='''),
r'''a = x = y =''', r'''
_Assign_targets - ROOT 0,0..0,11
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
   2] Name 'y' Store - 0,8..0,9
'''),

('', 1, 3, 'targets', {'one': True, 'coerce': False}, ('_Assign_targets',
r'''a = b = c ='''), ('_Assign_targets',
r'''x = y ='''),
r'''a = x = y =''',
r'''**ValueError("cannot put _Assign_targets node as 'one=True' without 'coerce=True'")**''', r'''
_Assign_targets - ROOT 0,0..0,11
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
   2] Name 'y' Store - 0,8..0,9
'''),

('', 1, 3, 'targets', {}, ('_Assign_targets',
r'''a = b = c ='''), ('Name',
r'''x'''),
r'''a = x =''', r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
'''),

('', 1, 3, 'targets', {'coerce': False}, ('_Assign_targets',
r'''a = b = c ='''), ('Name',
r'''x'''),
r'''a = x =''',
r'''**NodeError('expecting _Assign_targets, got Name')**''', r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
'''),

('', 1, 3, 'targets', {'coerce': False, 'one': True}, ('_Assign_targets',
r'''a = b = c ='''), ('Name',
r'''x'''),
r'''a = x =''', r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
'''),
],

'With_items': [  # ................................................................................

('body[0]', 1, 2, 'items', {}, ('exec',
r'''with a, b, c: pass  # comment'''), (None,
r'''**DEL**'''),
r'''with a, c: pass  # comment''', r'''
Module - ROOT 0,0..0,26
  .body[1]
   0] With - 0,0..0,15
     .items[2]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
      1] withitem - 0,8..0,9
        .context_expr Name 'c' Load - 0,8..0,9
     .body[1]
      0] Pass - 0,11..0,15
'''),

('body[0]', 1, 3, 'items', {}, ('exec',
r'''with a, b, c: pass  # comment'''), (None,
r'''**DEL**'''),
r'''with a: pass  # comment''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] With - 0,0..0,12
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
'''),

('body[0]', 0, 2, 'items', {}, ('exec',
r'''with a, b, c: pass  # comment'''), (None,
r'''**DEL**'''),
r'''with c: pass  # comment''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] With - 0,0..0,12
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'c' Load - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
'''),

('body[0]', 1, 2, 'items', {}, ('exec', r'''
with a \
, \
b \
, \
c: pass  # comment
'''), (None,
r'''**DEL**'''), r'''
with a \
, \
c: pass  # comment
''', r'''
Module - ROOT 0,0..2,18
  .body[1]
   0] With - 0,0..2,7
     .items[2]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
      1] withitem - 2,0..2,1
        .context_expr Name 'c' Load - 2,0..2,1
     .body[1]
      0] Pass - 2,3..2,7
'''),

('body[0]', 0, 2, 'items', {}, ('exec', r'''
with a \
, \
b \
, \
c: pass  # comment
'''), (None,
r'''**DEL**'''), r'''
with (
c): pass  # comment
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] With - 0,0..1,8
     .items[1]
      0] withitem - 0,5..1,2
        .context_expr Name 'c' Load - 1,0..1,1
     .body[1]
      0] Pass - 1,4..1,8
'''),

('body[0]', 1, 3, 'items', {}, ('exec', r'''
with a \
, \
b \
, \
c: pass  # comment
'''), (None,
r'''**DEL**'''), r'''
with a \
 \
: pass  # comment
''', r'''
Module - ROOT 0,0..2,17
  .body[1]
   0] With - 0,0..2,6
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
     .body[1]
      0] Pass - 2,2..2,6
'''),

('body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
if 1:
  with a \
  , \
  b: pass  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  with  \
  b: pass  # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] With - 1,2..2,9
        .items[1]
         0] withitem - 2,2..2,3
           .context_expr Name 'b' Load - 2,2..2,3
        .body[1]
         0] Pass - 2,5..2,9
      1] Pass - 3,2..3,6
'''),

('body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
if 1:
  with a \
  , \
  b: pass  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  with a \
   \
  : pass  # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] With - 1,2..3,8
        .items[1]
         0] withitem - 1,7..1,8
           .context_expr Name 'a' Load - 1,7..1,8
        .body[1]
         0] Pass - 3,4..3,8
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, 'items', {}, ('exec', r'''
if 1:
  with a: pass
  pass
'''), ('_withitems', r'''
x \
  , \
  y

'''), r'''
if 1:
  with (x \
       , \
       y,
       a): pass
  pass
''', r'''
if 1:
  with x, y, a: pass
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] With - 1,2..4,15
        .items[3]
         0] withitem - 1,8..1,9
           .context_expr Name 'x' Load - 1,8..1,9
         1] withitem - 3,7..3,8
           .context_expr Name 'y' Load - 3,7..3,8
         2] withitem - 4,7..4,8
           .context_expr Name 'a' Load - 4,7..4,8
        .body[1]
         0] Pass - 4,11..4,15
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, 'items', {}, ('exec',
r'''with a, b, c: pass  # comment'''), ('_withitems',
r'''x'''),
r'''with a, x, c: pass  # comment''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] With - 0,0..0,18
     .items[3]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
      1] withitem - 0,8..0,9
        .context_expr Name 'x' Load - 0,8..0,9
      2] withitem - 0,11..0,12
        .context_expr Name 'c' Load - 0,11..0,12
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0]', 1, 2, 'items', {}, ('exec',
r'''with a, b, c: pass  # comment'''), ('_withitems',
r'''x.y'''),
r'''with a, x.y, c: pass  # comment''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] With - 0,0..0,20
     .items[3]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
      1] withitem - 0,8..0,11
        .context_expr Attribute - 0,8..0,11
          .value Name 'x' Load - 0,8..0,9
          .attr 'y'
          .ctx Load
      2] withitem - 0,13..0,14
        .context_expr Name 'c' Load - 0,13..0,14
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0]', 0, 'end', 'items', {}, ('exec',
r'''with a, b, c: pass  # comment'''), ('_withitems', r'''
x \

'''), r'''
with x \
: pass  # comment
''',
r'''with x: pass  # comment''', r'''
Module - ROOT 0,0..1,17
  .body[1]
   0] With - 0,0..1,6
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'x' Load - 0,5..0,6
     .body[1]
      0] Pass - 1,2..1,6
'''),

('', 0, 'end', 'items', {'norm': True}, (None,
r'''with a, b, c: pass  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all With.items without norm_self=False')**'''),

('', 0, 'end', 'items', {'norm_self': False, '_verify_self': False}, (None,
r'''with a, b, c: pass  # comment'''),
r'''**DEL**''',
r'''with : pass  # comment''', r'''
With - ROOT 0,0..0,11
  .body[1]
   0] Pass - 0,7..0,11
'''),

('body[0]', 1, 1, 'items', {}, ('exec',
r'''with a: pass'''), ('_withitems', r'''
b \
, \
c \

'''), r'''
with a, b \
     , \
     c \
: pass
''',
r'''with a, b, c: pass''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] With - 0,0..3,6
     .items[3]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
      1] withitem - 0,8..0,9
        .context_expr Name 'b' Load - 0,8..0,9
      2] withitem - 2,5..2,6
        .context_expr Name 'c' Load - 2,5..2,6
     .body[1]
      0] Pass - 3,2..3,6
'''),

('body[0]', 1, 1, 'items', {}, ('exec',
r'''with a: pass'''), ('_withitems', r'''
\
b \
, \
c \

'''), r'''
with a, \
     b \
     , \
     c \
: pass
''',
r'''with a, b, c: pass''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] With - 0,0..4,6
     .items[3]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
      1] withitem - 1,5..1,6
        .context_expr Name 'b' Load - 1,5..1,6
      2] withitem - 3,5..3,6
        .context_expr Name 'c' Load - 3,5..3,6
     .body[1]
      0] Pass - 4,2..4,6
'''),

('body[0]', 1, 1, 'items', {}, (None, r'''
if 1:
  with x:
    pass;
'''), ('_withitems',
r'''y'''), r'''
if 1:
  with x, y:
    pass;
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] With - 1,2..2,9
     .items[2]
      0] withitem - 1,7..1,8
        .context_expr Name 'x' Load - 1,7..1,8
      1] withitem - 1,10..1,11
        .context_expr Name 'y' Load - 1,10..1,11
     .body[1]
      0] Pass - 2,4..2,8
'''),

('', 1, 1, 'items', {}, (None,
r'''with x, y, z: pass'''), ('_withitems',
r''''''),
r'''with x, y, z: pass''', r'''
With - ROOT 0,0..0,18
  .items[3]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'y' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'z' Load - 0,11..0,12
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', 0, 'end', 'items', {'_src': False}, (None,
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

('', 0, 'end', 'items', {'_src': False}, (None,
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

('', 0, 'end', 'items', {'_src': False}, (None,
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

('', 0, 'end', 'items', {'_src': False}, (None,
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

'With_items_coerce': [  # ................................................................................

('', 1, 3, 'items', {'one': True}, (None,
r'''with a as a, b as b, c as c: pass'''), ('_withitems',
r'''x as x, y as y'''),
r'''with a as a, x as x, y as y: pass''', r'''
With - ROOT 0,0..0,33
  .items[3]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'x' Load - 0,13..0,14
     .optional_vars Name 'x' Store - 0,18..0,19
   2] withitem - 0,21..0,27
     .context_expr Name 'y' Load - 0,21..0,22
     .optional_vars Name 'y' Store - 0,26..0,27
  .body[1]
   0] Pass - 0,29..0,33
'''),

('', 1, 3, 'items', {'one': True, 'coerce': False}, (None,
r'''with a as a, b as b, c as c: pass'''), ('_withitems',
r'''x as x, y as y'''),
r'''with a as a, x as x, y as y: pass''',
r'''**ValueError("cannot put _withitems node as 'one=True' without 'coerce=True'")**''', r'''
With - ROOT 0,0..0,33
  .items[3]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'x' Load - 0,13..0,14
     .optional_vars Name 'x' Store - 0,18..0,19
   2] withitem - 0,21..0,27
     .context_expr Name 'y' Load - 0,21..0,22
     .optional_vars Name 'y' Store - 0,26..0,27
  .body[1]
   0] Pass - 0,29..0,33
'''),

('', 1, 3, 'items', {}, (None,
r'''with a as a, b as b, c as c: pass'''), ('withitem',
r'''x as x'''),
r'''with a as a, x as x: pass''', r'''
With - ROOT 0,0..0,25
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'x' Load - 0,13..0,14
     .optional_vars Name 'x' Store - 0,18..0,19
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 1, 3, 'items', {'coerce': False}, (None,
r'''with a as a, b as b, c as c: pass'''), ('withitem',
r'''x as x'''),
r'''with a as a, x as x: pass''',
r'''**NodeError('expecting _withitems, got withitem')**''', r'''
With - ROOT 0,0..0,25
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'x' Load - 0,13..0,14
     .optional_vars Name 'x' Store - 0,18..0,19
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 1, 3, 'items', {'coerce': False, 'one': True}, (None,
r'''with a as a, b as b, c as c: pass'''), ('withitem',
r'''x as x'''),
r'''with a as a, x as x: pass''', r'''
With - ROOT 0,0..0,25
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'x' Load - 0,13..0,14
     .optional_vars Name 'x' Store - 0,18..0,19
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', 1, 3, 'items', {}, (None,
r'''with a as a, b as b, c as c: pass'''), ('Name',
r'''x'''),
r'''with a as a, x: pass''', r'''
With - ROOT 0,0..0,20
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,14
     .context_expr Name 'x' Load - 0,13..0,14
  .body[1]
   0] Pass - 0,16..0,20
'''),

('', 1, 3, 'items', {'coerce': False}, (None,
r'''with a as a, b as b, c as c: pass'''), ('Name',
r'''x'''),
r'''with a as a, x: pass''',
r'''**NodeError('expecting _withitems, got Name')**''', r'''
With - ROOT 0,0..0,20
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,14
     .context_expr Name 'x' Load - 0,13..0,14
  .body[1]
   0] Pass - 0,16..0,20
'''),

('', 1, 3, 'items', {'coerce': False, 'one': True}, (None,
r'''with a as a, b as b, c as c: pass'''), ('Name',
r'''x'''),
r'''with a as a, x: pass''', r'''
With - ROOT 0,0..0,20
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,14
     .context_expr Name 'x' Load - 0,13..0,14
  .body[1]
   0] Pass - 0,16..0,20
'''),

('', 1, 3, 'items', {'one': True}, ('_withitems',
r'''a as a, b as b, c as c'''), ('_withitems',
r'''x as x, y as y'''),
r'''a as a, x as x, y as y''', r'''
_withitems - ROOT 0,0..0,22
  .items[3]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
   2] withitem - 0,16..0,22
     .context_expr Name 'y' Load - 0,16..0,17
     .optional_vars Name 'y' Store - 0,21..0,22
'''),

('', 1, 3, 'items', {'one': True, 'coerce': False}, ('_withitems',
r'''a as a, b as b, c as c'''), ('_withitems',
r'''x as x, y as y'''),
r'''a as a, x as x, y as y''',
r'''**ValueError("cannot put _withitems node as 'one=True' without 'coerce=True'")**''', r'''
_withitems - ROOT 0,0..0,22
  .items[3]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
   2] withitem - 0,16..0,22
     .context_expr Name 'y' Load - 0,16..0,17
     .optional_vars Name 'y' Store - 0,21..0,22
'''),

('', 1, 3, 'items', {}, ('_withitems',
r'''a as a, b as b, c as c'''), ('withitem',
r'''x as x'''),
r'''a as a, x as x''', r'''
_withitems - ROOT 0,0..0,14
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
'''),

('', 1, 3, 'items', {'coerce': False}, ('_withitems',
r'''a as a, b as b, c as c'''), ('withitem',
r'''x as x'''),
r'''a as a, x as x''',
r'''**NodeError('expecting _withitems, got withitem')**''', r'''
_withitems - ROOT 0,0..0,14
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
'''),

('', 1, 3, 'items', {'coerce': False, 'one': True}, ('_withitems',
r'''a as a, b as b, c as c'''), ('withitem',
r'''x as x'''),
r'''a as a, x as x''', r'''
_withitems - ROOT 0,0..0,14
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
'''),

('', 1, 3, 'items', {}, ('_withitems',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'x' Load - 0,8..0,9
'''),

('', 1, 3, 'items', {'coerce': False}, ('_withitems',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''',
r'''**NodeError('expecting _withitems, got Name')**''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'x' Load - 0,8..0,9
'''),

('', 1, 3, 'items', {'coerce': False, 'one': True}, ('_withitems',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'x' Load - 0,8..0,9
'''),
],

'With_item_w_pars': [  # ................................................................................

('body[0]', 1, 2, 'items', {}, ('exec',
r'''with (a, b, c): pass  # comment'''), (None,
r'''**DEL**'''),
r'''with (a, c): pass  # comment''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] With - 0,0..0,17
     .items[2]
      0] withitem - 0,6..0,7
        .context_expr Name 'a' Load - 0,6..0,7
      1] withitem - 0,9..0,10
        .context_expr Name 'c' Load - 0,9..0,10
     .body[1]
      0] Pass - 0,13..0,17
'''),

('body[0]', 1, 3, 'items', {}, ('exec',
r'''with (a, b, c): pass  # comment'''), (None,
r'''**DEL**'''),
r'''with (a): pass  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] With - 0,0..0,14
     .items[1]
      0] withitem - 0,5..0,8
        .context_expr Name 'a' Load - 0,6..0,7
     .body[1]
      0] Pass - 0,10..0,14
'''),

('body[0]', 0, 2, 'items', {}, ('exec',
r'''with (a, b, c): pass  # comment'''), (None,
r'''**DEL**'''),
r'''with (c): pass  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] With - 0,0..0,14
     .items[1]
      0] withitem - 0,5..0,8
        .context_expr Name 'c' Load - 0,6..0,7
     .body[1]
      0] Pass - 0,10..0,14
'''),

('body[0]', 1, 2, 'items', {}, ('exec', r'''
with (a \
, \
b \
, \
c): pass  # comment
'''), (None,
r'''**DEL**'''), r'''
with (a \
, \
c): pass  # comment
''', r'''
Module - ROOT 0,0..2,19
  .body[1]
   0] With - 0,0..2,8
     .items[2]
      0] withitem - 0,6..0,7
        .context_expr Name 'a' Load - 0,6..0,7
      1] withitem - 2,0..2,1
        .context_expr Name 'c' Load - 2,0..2,1
     .body[1]
      0] Pass - 2,4..2,8
'''),

('body[0]', 0, 2, 'items', {}, ('exec', r'''
with (a \
, \
b \
, \
c): pass  # comment
'''), (None,
r'''**DEL**'''), r'''
with (
c): pass  # comment
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] With - 0,0..1,8
     .items[1]
      0] withitem - 0,5..1,2
        .context_expr Name 'c' Load - 1,0..1,1
     .body[1]
      0] Pass - 1,4..1,8
'''),

('body[0]', 1, 3, 'items', {}, ('exec', r'''
with (a \
, \
b \
, \
c): pass  # comment
'''), (None,
r'''**DEL**'''), r'''
with (a \
 \
): pass  # comment
''', r'''
Module - ROOT 0,0..2,18
  .body[1]
   0] With - 0,0..2,7
     .items[1]
      0] withitem - 0,5..2,1
        .context_expr Name 'a' Load - 0,6..0,7
     .body[1]
      0] Pass - 2,3..2,7
'''),

('body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
if 1:
  with (a \
  , \
  b): pass  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  with ( \
  b): pass  # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] With - 1,2..2,10
        .items[1]
         0] withitem - 1,7..2,4
           .context_expr Name 'b' Load - 2,2..2,3
        .body[1]
         0] Pass - 2,6..2,10
      1] Pass - 3,2..3,6
'''),

('body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
if 1:
  with (a \
  , \
  b): pass  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  with (a \
   \
  ): pass  # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] With - 1,2..3,9
        .items[1]
         0] withitem - 1,7..3,3
           .context_expr Name 'a' Load - 1,8..1,9
        .body[1]
         0] Pass - 3,5..3,9
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, 'items', {}, ('exec', r'''
if 1:
  with (a): pass
  pass
'''), ('_withitems', r'''
x \
  , \
  y

'''), r'''
if 1:
  with (x \
       , \
       y,
       (a)): pass
  pass
''', r'''
if 1:
  with x, y, (a): pass
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] With - 1,2..4,17
        .items[3]
         0] withitem - 1,8..1,9
           .context_expr Name 'x' Load - 1,8..1,9
         1] withitem - 3,7..3,8
           .context_expr Name 'y' Load - 3,7..3,8
         2] withitem - 4,7..4,10
           .context_expr Name 'a' Load - 4,8..4,9
        .body[1]
         0] Pass - 4,13..4,17
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, 'items', {}, ('exec',
r'''with (a, b, c): pass  # comment'''), ('_withitems',
r'''x'''),
r'''with (a, x, c): pass  # comment''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] With - 0,0..0,20
     .items[3]
      0] withitem - 0,6..0,7
        .context_expr Name 'a' Load - 0,6..0,7
      1] withitem - 0,9..0,10
        .context_expr Name 'x' Load - 0,9..0,10
      2] withitem - 0,12..0,13
        .context_expr Name 'c' Load - 0,12..0,13
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0]', 1, 2, 'items', {}, ('exec',
r'''with (a, b, c): pass  # comment'''), ('_withitems',
r'''x.y'''),
r'''with (a, x.y, c): pass  # comment''', r'''
Module - ROOT 0,0..0,33
  .body[1]
   0] With - 0,0..0,22
     .items[3]
      0] withitem - 0,6..0,7
        .context_expr Name 'a' Load - 0,6..0,7
      1] withitem - 0,9..0,12
        .context_expr Attribute - 0,9..0,12
          .value Name 'x' Load - 0,9..0,10
          .attr 'y'
          .ctx Load
      2] withitem - 0,14..0,15
        .context_expr Name 'c' Load - 0,14..0,15
     .body[1]
      0] Pass - 0,18..0,22
'''),

('body[0]', 0, 'end', 'items', {}, ('exec',
r'''with (a, b, c): pass  # comment'''), ('_withitems', r'''
x \

'''), r'''
with (x \
): pass  # comment
''',
r'''with (x): pass  # comment''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] With - 0,0..1,7
     .items[1]
      0] withitem - 0,5..1,1
        .context_expr Name 'x' Load - 0,6..0,7
     .body[1]
      0] Pass - 1,3..1,7
'''),

('', 0, 'end', 'items', {'norm': True}, (None,
r'''with (a, b, c): pass  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all With.items without norm_self=False')**'''),

('', 0, 'end', 'items', {'norm_self': False, '_verify_self': False}, (None,
r'''with (a, b, c): pass  # comment'''),
r'''**DEL**''',
r'''with (): pass  # comment''', r'''
With - ROOT 0,0..0,13
  .body[1]
   0] Pass - 0,9..0,13
'''),

('body[0]', 1, 1, 'items', {}, ('exec',
r'''with (a): pass'''), ('_withitems', r'''
b \
, \
c \

'''), r'''
with (a), b \
     , \
     c \
: pass
''',
r'''with (a), b, c: pass''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] With - 0,0..3,6
     .items[3]
      0] withitem - 0,5..0,8
        .context_expr Name 'a' Load - 0,6..0,7
      1] withitem - 0,10..0,11
        .context_expr Name 'b' Load - 0,10..0,11
      2] withitem - 2,5..2,6
        .context_expr Name 'c' Load - 2,5..2,6
     .body[1]
      0] Pass - 3,2..3,6
'''),

('body[0]', 1, 1, 'items', {}, ('exec',
r'''with (a): pass'''), ('_withitems', r'''
\
b \
, \
c \

'''), r'''
with (a), \
     b \
     , \
     c \
: pass
''',
r'''with (a), b, c: pass''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] With - 0,0..4,6
     .items[3]
      0] withitem - 0,5..0,8
        .context_expr Name 'a' Load - 0,6..0,7
      1] withitem - 1,5..1,6
        .context_expr Name 'b' Load - 1,5..1,6
      2] withitem - 3,5..3,6
        .context_expr Name 'c' Load - 3,5..3,6
     .body[1]
      0] Pass - 4,2..4,6
'''),

('body[0]', 1, 1, 'items', {}, (None, r'''
if 1:
  with (x):
    pass;
'''), ('_withitems',
r'''y'''), r'''
if 1:
  with (x), y:
    pass;
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] With - 1,2..2,9
     .items[2]
      0] withitem - 1,7..1,10
        .context_expr Name 'x' Load - 1,8..1,9
      1] withitem - 1,12..1,13
        .context_expr Name 'y' Load - 1,12..1,13
     .body[1]
      0] Pass - 2,4..2,8
'''),
],

'AsyncWith_items': [  # ................................................................................

('body[0]', 1, 2, 'items', {}, ('exec',
r'''async with a, b, c: pass  # comment'''), (None,
r'''**DEL**'''),
r'''async with a, c: pass  # comment''', r'''
Module - ROOT 0,0..0,32
  .body[1]
   0] AsyncWith - 0,0..0,21
     .items[2]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
      1] withitem - 0,14..0,15
        .context_expr Name 'c' Load - 0,14..0,15
     .body[1]
      0] Pass - 0,17..0,21
'''),

('body[0]', 1, 3, 'items', {}, ('exec',
r'''async with a, b, c: pass  # comment'''), (None,
r'''**DEL**'''),
r'''async with a: pass  # comment''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncWith - 0,0..0,18
     .items[1]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0]', 0, 2, 'items', {}, ('exec',
r'''async with a, b, c: pass  # comment'''), (None,
r'''**DEL**'''),
r'''async with c: pass  # comment''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncWith - 0,0..0,18
     .items[1]
      0] withitem - 0,11..0,12
        .context_expr Name 'c' Load - 0,11..0,12
     .body[1]
      0] Pass - 0,14..0,18
'''),

('body[0]', 1, 2, 'items', {}, ('exec', r'''
async with a \
, \
b \
, \
c: pass  # comment
'''), (None,
r'''**DEL**'''), r'''
async with a \
, \
c: pass  # comment
''', r'''
Module - ROOT 0,0..2,18
  .body[1]
   0] AsyncWith - 0,0..2,7
     .items[2]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
      1] withitem - 2,0..2,1
        .context_expr Name 'c' Load - 2,0..2,1
     .body[1]
      0] Pass - 2,3..2,7
'''),

('body[0]', 0, 2, 'items', {}, ('exec', r'''
async with a \
, \
b \
, \
c: pass  # comment
'''), (None,
r'''**DEL**'''), r'''
async with (
c): pass  # comment
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] AsyncWith - 0,0..1,8
     .items[1]
      0] withitem - 0,11..1,2
        .context_expr Name 'c' Load - 1,0..1,1
     .body[1]
      0] Pass - 1,4..1,8
'''),

('body[0]', 1, 3, 'items', {}, ('exec', r'''
async with a \
, \
b \
, \
c: pass  # comment
'''), (None,
r'''**DEL**'''), r'''
async with a \
 \
: pass  # comment
''', r'''
Module - ROOT 0,0..2,17
  .body[1]
   0] AsyncWith - 0,0..2,6
     .items[1]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
     .body[1]
      0] Pass - 2,2..2,6
'''),

('body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
if 1:
  async with a \
  , \
  b: pass  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  async with  \
  b: pass  # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] AsyncWith - 1,2..2,9
        .items[1]
         0] withitem - 2,2..2,3
           .context_expr Name 'b' Load - 2,2..2,3
        .body[1]
         0] Pass - 2,5..2,9
      1] Pass - 3,2..3,6
'''),

('body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
if 1:
  async with a \
  , \
  b: pass  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  async with a \
   \
  : pass  # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] AsyncWith - 1,2..3,8
        .items[1]
         0] withitem - 1,13..1,14
           .context_expr Name 'a' Load - 1,13..1,14
        .body[1]
         0] Pass - 3,4..3,8
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, 'items', {}, ('exec', r'''
if 1:
  async with a: pass
  pass
'''), ('_withitems', r'''
x \
  , \
  y

'''), r'''
if 1:
  async with (x \
             , \
             y,
             a): pass
  pass
''', r'''
if 1:
  async with x, y, a: pass
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] AsyncWith - 1,2..4,21
        .items[3]
         0] withitem - 1,14..1,15
           .context_expr Name 'x' Load - 1,14..1,15
         1] withitem - 3,13..3,14
           .context_expr Name 'y' Load - 3,13..3,14
         2] withitem - 4,13..4,14
           .context_expr Name 'a' Load - 4,13..4,14
        .body[1]
         0] Pass - 4,17..4,21
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, 'items', {}, ('exec',
r'''async with a, b, c: pass  # comment'''), ('_withitems',
r'''x'''),
r'''async with a, x, c: pass  # comment''', r'''
Module - ROOT 0,0..0,35
  .body[1]
   0] AsyncWith - 0,0..0,24
     .items[3]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
      1] withitem - 0,14..0,15
        .context_expr Name 'x' Load - 0,14..0,15
      2] withitem - 0,17..0,18
        .context_expr Name 'c' Load - 0,17..0,18
     .body[1]
      0] Pass - 0,20..0,24
'''),

('body[0]', 1, 2, 'items', {}, ('exec',
r'''async with a, b, c: pass  # comment'''), ('_withitems',
r'''x.y'''),
r'''async with a, x.y, c: pass  # comment''', r'''
Module - ROOT 0,0..0,37
  .body[1]
   0] AsyncWith - 0,0..0,26
     .items[3]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
      1] withitem - 0,14..0,17
        .context_expr Attribute - 0,14..0,17
          .value Name 'x' Load - 0,14..0,15
          .attr 'y'
          .ctx Load
      2] withitem - 0,19..0,20
        .context_expr Name 'c' Load - 0,19..0,20
     .body[1]
      0] Pass - 0,22..0,26
'''),

('body[0]', 0, 'end', 'items', {}, ('exec',
r'''async with a, b, c: pass  # comment'''), ('_withitems', r'''
x \

'''), r'''
async with x \
: pass  # comment
''',
r'''async with x: pass  # comment''', r'''
Module - ROOT 0,0..1,17
  .body[1]
   0] AsyncWith - 0,0..1,6
     .items[1]
      0] withitem - 0,11..0,12
        .context_expr Name 'x' Load - 0,11..0,12
     .body[1]
      0] Pass - 1,2..1,6
'''),

('', 0, 'end', 'items', {'norm': True}, (None,
r'''async with a, b, c: pass  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all AsyncWith.items without norm_self=False')**'''),

('', 0, 'end', 'items', {'norm_self': False, '_verify_self': False}, (None,
r'''async with a, b, c: pass  # comment'''),
r'''**DEL**''',
r'''async with : pass  # comment''', r'''
AsyncWith - ROOT 0,0..0,17
  .body[1]
   0] Pass - 0,13..0,17
'''),

('body[0]', 1, 1, 'items', {}, ('exec',
r'''async with a: pass'''), ('_withitems', r'''
b \
, \
c \

'''), r'''
async with a, b \
           , \
           c \
: pass
''',
r'''async with a, b, c: pass''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] AsyncWith - 0,0..3,6
     .items[3]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
      1] withitem - 0,14..0,15
        .context_expr Name 'b' Load - 0,14..0,15
      2] withitem - 2,11..2,12
        .context_expr Name 'c' Load - 2,11..2,12
     .body[1]
      0] Pass - 3,2..3,6
'''),

('body[0]', 1, 1, 'items', {}, ('exec',
r'''async with a: pass'''), ('_withitems', r'''
\
b \
, \
c \

'''), r'''
async with a, \
           b \
           , \
           c \
: pass
''',
r'''async with a, b, c: pass''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] AsyncWith - 0,0..4,6
     .items[3]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
      1] withitem - 1,11..1,12
        .context_expr Name 'b' Load - 1,11..1,12
      2] withitem - 3,11..3,12
        .context_expr Name 'c' Load - 3,11..3,12
     .body[1]
      0] Pass - 4,2..4,6
'''),

('body[0]', 1, 1, 'items', {}, (None, r'''
if 1:
  async with x:
    pass;
'''), ('_withitems',
r'''y'''), r'''
if 1:
  async with x, y:
    pass;
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] AsyncWith - 1,2..2,9
     .items[2]
      0] withitem - 1,13..1,14
        .context_expr Name 'x' Load - 1,13..1,14
      1] withitem - 1,16..1,17
        .context_expr Name 'y' Load - 1,16..1,17
     .body[1]
      0] Pass - 2,4..2,8
'''),

('', 0, 'end', 'items', {'_src': False}, (None,
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

('', 0, 'end', 'items', {'_src': False}, (None,
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

('', 0, 'end', 'items', {'_src': False}, (None,
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

('', 0, 'end', 'items', {'_src': False}, (None,
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

'AsyncWith_items_coerce': [  # ................................................................................

('', 1, 3, 'items', {'one': True}, (None,
r'''with a as a, b as b, c as c: pass'''), ('_withitems',
r'''x as x, y as y'''),
r'''with a as a, x as x, y as y: pass''', r'''
With - ROOT 0,0..0,33
  .items[3]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'a' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'x' Load - 0,13..0,14
     .optional_vars Name 'x' Store - 0,18..0,19
   2] withitem - 0,21..0,27
     .context_expr Name 'y' Load - 0,21..0,22
     .optional_vars Name 'y' Store - 0,26..0,27
  .body[1]
   0] Pass - 0,29..0,33
'''),

('', 1, 3, 'items', {'one': True, 'coerce': False}, (None,
r'''async with a as a, b as b, c as c: pass'''), ('_withitems',
r'''x as x, y as y'''),
r'''async with a as a, x as x, y as y: pass''',
r'''**ValueError("cannot put _withitems node as 'one=True' without 'coerce=True'")**''', r'''
AsyncWith - ROOT 0,0..0,39
  .items[3]
   0] withitem - 0,11..0,17
     .context_expr Name 'a' Load - 0,11..0,12
     .optional_vars Name 'a' Store - 0,16..0,17
   1] withitem - 0,19..0,25
     .context_expr Name 'x' Load - 0,19..0,20
     .optional_vars Name 'x' Store - 0,24..0,25
   2] withitem - 0,27..0,33
     .context_expr Name 'y' Load - 0,27..0,28
     .optional_vars Name 'y' Store - 0,32..0,33
  .body[1]
   0] Pass - 0,35..0,39
'''),

('', 1, 3, 'items', {}, (None,
r'''async with a as a, b as b, c as c: pass'''), ('withitem',
r'''x as x'''),
r'''async with a as a, x as x: pass''', r'''
AsyncWith - ROOT 0,0..0,31
  .items[2]
   0] withitem - 0,11..0,17
     .context_expr Name 'a' Load - 0,11..0,12
     .optional_vars Name 'a' Store - 0,16..0,17
   1] withitem - 0,19..0,25
     .context_expr Name 'x' Load - 0,19..0,20
     .optional_vars Name 'x' Store - 0,24..0,25
  .body[1]
   0] Pass - 0,27..0,31
'''),

('', 1, 3, 'items', {'coerce': False}, (None,
r'''async with a as a, b as b, c as c: pass'''), ('withitem',
r'''x as x'''),
r'''async with a as a, x as x: pass''',
r'''**NodeError('expecting _withitems, got withitem')**''', r'''
AsyncWith - ROOT 0,0..0,31
  .items[2]
   0] withitem - 0,11..0,17
     .context_expr Name 'a' Load - 0,11..0,12
     .optional_vars Name 'a' Store - 0,16..0,17
   1] withitem - 0,19..0,25
     .context_expr Name 'x' Load - 0,19..0,20
     .optional_vars Name 'x' Store - 0,24..0,25
  .body[1]
   0] Pass - 0,27..0,31
'''),

('', 1, 3, 'items', {'coerce': False, 'one': True}, (None,
r'''async with a as a, b as b, c as c: pass'''), ('withitem',
r'''x as x'''),
r'''async with a as a, x as x: pass''', r'''
AsyncWith - ROOT 0,0..0,31
  .items[2]
   0] withitem - 0,11..0,17
     .context_expr Name 'a' Load - 0,11..0,12
     .optional_vars Name 'a' Store - 0,16..0,17
   1] withitem - 0,19..0,25
     .context_expr Name 'x' Load - 0,19..0,20
     .optional_vars Name 'x' Store - 0,24..0,25
  .body[1]
   0] Pass - 0,27..0,31
'''),

('', 1, 3, 'items', {}, (None,
r'''async with a as a, b as b, c as c: pass'''), ('Name',
r'''x'''),
r'''async with a as a, x: pass''', r'''
AsyncWith - ROOT 0,0..0,26
  .items[2]
   0] withitem - 0,11..0,17
     .context_expr Name 'a' Load - 0,11..0,12
     .optional_vars Name 'a' Store - 0,16..0,17
   1] withitem - 0,19..0,20
     .context_expr Name 'x' Load - 0,19..0,20
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, 3, 'items', {'coerce': False}, (None,
r'''async with a as a, b as b, c as c: pass'''), ('Name',
r'''x'''),
r'''async with a as a, x: pass''',
r'''**NodeError('expecting _withitems, got Name')**''', r'''
AsyncWith - ROOT 0,0..0,26
  .items[2]
   0] withitem - 0,11..0,17
     .context_expr Name 'a' Load - 0,11..0,12
     .optional_vars Name 'a' Store - 0,16..0,17
   1] withitem - 0,19..0,20
     .context_expr Name 'x' Load - 0,19..0,20
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, 3, 'items', {'coerce': False, 'one': True}, (None,
r'''async with a as a, b as b, c as c: pass'''), ('Name',
r'''x'''),
r'''async with a as a, x: pass''', r'''
AsyncWith - ROOT 0,0..0,26
  .items[2]
   0] withitem - 0,11..0,17
     .context_expr Name 'a' Load - 0,11..0,12
     .optional_vars Name 'a' Store - 0,16..0,17
   1] withitem - 0,19..0,20
     .context_expr Name 'x' Load - 0,19..0,20
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, 3, 'items', {'one': True}, ('_withitems',
r'''a as a, b as b, c as c'''), ('_withitems',
r'''x as x, y as y'''),
r'''a as a, x as x, y as y''', r'''
_withitems - ROOT 0,0..0,22
  .items[3]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
   2] withitem - 0,16..0,22
     .context_expr Name 'y' Load - 0,16..0,17
     .optional_vars Name 'y' Store - 0,21..0,22
'''),

('', 1, 3, 'items', {'one': True, 'coerce': False}, ('_withitems',
r'''a as a, b as b, c as c'''), ('_withitems',
r'''x as x, y as y'''),
r'''a as a, x as x, y as y''',
r'''**ValueError("cannot put _withitems node as 'one=True' without 'coerce=True'")**''', r'''
_withitems - ROOT 0,0..0,22
  .items[3]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
   2] withitem - 0,16..0,22
     .context_expr Name 'y' Load - 0,16..0,17
     .optional_vars Name 'y' Store - 0,21..0,22
'''),

('', 1, 3, 'items', {}, ('_withitems',
r'''a as a, b as b, c as c'''), ('withitem',
r'''x as x'''),
r'''a as a, x as x''', r'''
_withitems - ROOT 0,0..0,14
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
'''),

('', 1, 3, 'items', {'coerce': False}, ('_withitems',
r'''a as a, b as b, c as c'''), ('withitem',
r'''x as x'''),
r'''a as a, x as x''',
r'''**NodeError('expecting _withitems, got withitem')**''', r'''
_withitems - ROOT 0,0..0,14
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
'''),

('', 1, 3, 'items', {'coerce': False, 'one': True}, ('_withitems',
r'''a as a, b as b, c as c'''), ('withitem',
r'''x as x'''),
r'''a as a, x as x''', r'''
_withitems - ROOT 0,0..0,14
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
'''),

('', 1, 3, 'items', {}, ('_withitems',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'x' Load - 0,8..0,9
'''),

('', 1, 3, 'items', {'coerce': False}, ('_withitems',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''',
r'''**NodeError('expecting _withitems, got Name')**''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'x' Load - 0,8..0,9
'''),

('', 1, 3, 'items', {'coerce': False, 'one': True}, ('_withitems',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'x' Load - 0,8..0,9
'''),
],

'AsyncWith_item_w_pars': [  # ................................................................................

('body[0]', 1, 2, 'items', {}, ('exec',
r'''async with (a, b, c): pass  # comment'''), (None,
r'''**DEL**'''),
r'''async with (a, c): pass  # comment''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] AsyncWith - 0,0..0,23
     .items[2]
      0] withitem - 0,12..0,13
        .context_expr Name 'a' Load - 0,12..0,13
      1] withitem - 0,15..0,16
        .context_expr Name 'c' Load - 0,15..0,16
     .body[1]
      0] Pass - 0,19..0,23
'''),

('body[0]', 1, 3, 'items', {}, ('exec',
r'''async with (a, b, c): pass  # comment'''), (None,
r'''**DEL**'''),
r'''async with (a): pass  # comment''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] AsyncWith - 0,0..0,20
     .items[1]
      0] withitem - 0,11..0,14
        .context_expr Name 'a' Load - 0,12..0,13
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0]', 0, 2, 'items', {}, ('exec',
r'''async with (a, b, c): pass  # comment'''), (None,
r'''**DEL**'''),
r'''async with (c): pass  # comment''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] AsyncWith - 0,0..0,20
     .items[1]
      0] withitem - 0,11..0,14
        .context_expr Name 'c' Load - 0,12..0,13
     .body[1]
      0] Pass - 0,16..0,20
'''),

('body[0]', 1, 2, 'items', {}, ('exec', r'''
async with (a \
, \
b \
, \
c): pass  # comment
'''), (None,
r'''**DEL**'''), r'''
async with (a \
, \
c): pass  # comment
''', r'''
Module - ROOT 0,0..2,19
  .body[1]
   0] AsyncWith - 0,0..2,8
     .items[2]
      0] withitem - 0,12..0,13
        .context_expr Name 'a' Load - 0,12..0,13
      1] withitem - 2,0..2,1
        .context_expr Name 'c' Load - 2,0..2,1
     .body[1]
      0] Pass - 2,4..2,8
'''),

('body[0]', 0, 2, 'items', {}, ('exec', r'''
async with (a \
, \
b \
, \
c): pass  # comment
'''), (None,
r'''**DEL**'''), r'''
async with (
c): pass  # comment
''', r'''
Module - ROOT 0,0..1,19
  .body[1]
   0] AsyncWith - 0,0..1,8
     .items[1]
      0] withitem - 0,11..1,2
        .context_expr Name 'c' Load - 1,0..1,1
     .body[1]
      0] Pass - 1,4..1,8
'''),

('body[0]', 1, 3, 'items', {}, ('exec', r'''
async with (a \
, \
b \
, \
c): pass  # comment
'''), (None,
r'''**DEL**'''), r'''
async with (a \
 \
): pass  # comment
''', r'''
Module - ROOT 0,0..2,18
  .body[1]
   0] AsyncWith - 0,0..2,7
     .items[1]
      0] withitem - 0,11..2,1
        .context_expr Name 'a' Load - 0,12..0,13
     .body[1]
      0] Pass - 2,3..2,7
'''),

('body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
if 1:
  async with (a \
  , \
  b): pass  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  async with ( \
  b): pass  # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] AsyncWith - 1,2..2,10
        .items[1]
         0] withitem - 1,13..2,4
           .context_expr Name 'b' Load - 2,2..2,3
        .body[1]
         0] Pass - 2,6..2,10
      1] Pass - 3,2..3,6
'''),

('body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
if 1:
  async with (a \
  , \
  b): pass  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  async with (a \
   \
  ): pass  # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] AsyncWith - 1,2..3,9
        .items[1]
         0] withitem - 1,13..3,3
           .context_expr Name 'a' Load - 1,14..1,15
        .body[1]
         0] Pass - 3,5..3,9
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, 'items', {}, ('exec', r'''
if 1:
  async with (a): pass
  pass
'''), ('_withitems', r'''
x \
  , \
  y

'''), r'''
if 1:
  async with (x \
             , \
             y,
             (a)): pass
  pass
''', r'''
if 1:
  async with x, y, (a): pass
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] AsyncWith - 1,2..4,23
        .items[3]
         0] withitem - 1,14..1,15
           .context_expr Name 'x' Load - 1,14..1,15
         1] withitem - 3,13..3,14
           .context_expr Name 'y' Load - 3,13..3,14
         2] withitem - 4,13..4,16
           .context_expr Name 'a' Load - 4,14..4,15
        .body[1]
         0] Pass - 4,19..4,23
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, 'items', {}, ('exec',
r'''async with (a, b, c): pass  # comment'''), ('_withitems',
r'''x'''),
r'''async with (a, x, c): pass  # comment''', r'''
Module - ROOT 0,0..0,37
  .body[1]
   0] AsyncWith - 0,0..0,26
     .items[3]
      0] withitem - 0,12..0,13
        .context_expr Name 'a' Load - 0,12..0,13
      1] withitem - 0,15..0,16
        .context_expr Name 'x' Load - 0,15..0,16
      2] withitem - 0,18..0,19
        .context_expr Name 'c' Load - 0,18..0,19
     .body[1]
      0] Pass - 0,22..0,26
'''),

('body[0]', 1, 2, 'items', {}, ('exec',
r'''async with (a, b, c): pass  # comment'''), ('_withitems',
r'''x.y'''),
r'''async with (a, x.y, c): pass  # comment''', r'''
Module - ROOT 0,0..0,39
  .body[1]
   0] AsyncWith - 0,0..0,28
     .items[3]
      0] withitem - 0,12..0,13
        .context_expr Name 'a' Load - 0,12..0,13
      1] withitem - 0,15..0,18
        .context_expr Attribute - 0,15..0,18
          .value Name 'x' Load - 0,15..0,16
          .attr 'y'
          .ctx Load
      2] withitem - 0,20..0,21
        .context_expr Name 'c' Load - 0,20..0,21
     .body[1]
      0] Pass - 0,24..0,28
'''),

('body[0]', 0, 'end', 'items', {}, ('exec',
r'''async with (a, b, c): pass  # comment'''), ('_withitems', r'''
x \

'''), r'''
async with (x \
): pass  # comment
''',
r'''async with (x): pass  # comment''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] AsyncWith - 0,0..1,7
     .items[1]
      0] withitem - 0,11..1,1
        .context_expr Name 'x' Load - 0,12..0,13
     .body[1]
      0] Pass - 1,3..1,7
'''),

('', 0, 'end', 'items', {'norm': True}, (None,
r'''async with (a, b, c): pass  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all AsyncWith.items without norm_self=False')**'''),

('', 0, 'end', 'items', {'norm_self': False, '_verify_self': False}, (None,
r'''async with (a, b, c): pass  # comment'''),
r'''**DEL**''',
r'''async with (): pass  # comment''', r'''
AsyncWith - ROOT 0,0..0,19
  .body[1]
   0] Pass - 0,15..0,19
'''),

('body[0]', 1, 1, 'items', {}, ('exec',
r'''async with (a): pass'''), ('_withitems', r'''
b \
, \
c \

'''), r'''
async with (a), b \
           , \
           c \
: pass
''',
r'''async with (a), b, c: pass''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] AsyncWith - 0,0..3,6
     .items[3]
      0] withitem - 0,11..0,14
        .context_expr Name 'a' Load - 0,12..0,13
      1] withitem - 0,16..0,17
        .context_expr Name 'b' Load - 0,16..0,17
      2] withitem - 2,11..2,12
        .context_expr Name 'c' Load - 2,11..2,12
     .body[1]
      0] Pass - 3,2..3,6
'''),

('body[0]', 1, 1, 'items', {}, ('exec',
r'''async with (a): pass'''), ('_withitems', r'''
\
b \
, \
c \

'''), r'''
async with (a), \
           b \
           , \
           c \
: pass
''',
r'''async with (a), b, c: pass''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] AsyncWith - 0,0..4,6
     .items[3]
      0] withitem - 0,11..0,14
        .context_expr Name 'a' Load - 0,12..0,13
      1] withitem - 1,11..1,12
        .context_expr Name 'b' Load - 1,11..1,12
      2] withitem - 3,11..3,12
        .context_expr Name 'c' Load - 3,11..3,12
     .body[1]
      0] Pass - 4,2..4,6
'''),

('body[0]', 1, 1, 'items', {}, (None, r'''
if 1:
  async with (x):
    pass;
'''), ('_withitems',
r'''y'''), r'''
if 1:
  async with (x), y:
    pass;
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] AsyncWith - 1,2..2,9
     .items[2]
      0] withitem - 1,13..1,16
        .context_expr Name 'x' Load - 1,14..1,15
      1] withitem - 1,18..1,19
        .context_expr Name 'y' Load - 1,18..1,19
     .body[1]
      0] Pass - 2,4..2,8
'''),
],

'Import_names': [  # ................................................................................

('body[0]', 1, 2, None, {}, ('exec',
r'''import a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''import a, c  # comment''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Import - 0,0..0,11
     .names[2]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'c'
'''),

('body[0]', 1, 3, None, {}, ('exec',
r'''import a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''import a  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Import - 0,0..0,8
     .names[1]
      0] alias - 0,7..0,8
        .name 'a'
'''),

('body[0]', 0, 2, None, {}, ('exec',
r'''import a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''import c  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Import - 0,0..0,8
     .names[1]
      0] alias - 0,7..0,8
        .name 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
import a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
import a \
, \
c  # comment
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] Import - 0,0..2,1
     .names[2]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 2,0..2,1
        .name 'c'
'''),

('body[0]', 0, 2, None, {}, ('exec', r'''
import a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
import \
c  # comment
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Import - 0,0..1,1
     .names[1]
      0] alias - 1,0..1,1
        .name 'c'
'''),

('body[0]', 1, 3, None, {}, ('exec', r'''
import a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
import a \
 \
  # comment
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] Import - 0,0..0,8
     .names[1]
      0] alias - 0,7..0,8
        .name 'a'
'''),

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  import a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  import  \
  b  # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Import - 1,2..2,3
        .names[1]
         0] alias - 2,2..2,3
           .name 'b'
      1] Pass - 3,2..3,6
'''),

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  import a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  import a \
   \
    # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Import - 1,2..1,10
        .names[1]
         0] alias - 1,9..1,10
           .name 'a'
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, None, {}, ('exec', r'''
if 1:
  import a
  pass
'''), ('_Import_names', r'''
x \
  , \
  y

'''), r'''
if 1:
  import x \
         , \
         y, \
         a
  pass
''', r'''
if 1:
  import x, y, a
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Import - 1,2..4,10
        .names[3]
         0] alias - 1,9..1,10
           .name 'x'
         1] alias - 3,9..3,10
           .name 'y'
         2] alias - 4,9..4,10
           .name 'a'
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''import a, b, c  # comment'''), ('_Import_names',
r'''x'''),
r'''import a, x, c  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Import - 0,0..0,14
     .names[3]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'x'
      2] alias - 0,13..0,14
        .name 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''import a, b, c  # comment'''), ('_Import_names',
r'''x.y'''),
r'''import a, x.y, c  # comment''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Import - 0,0..0,16
     .names[3]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,13
        .name 'x.y'
      2] alias - 0,15..0,16
        .name 'c'
'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''import a, b, c  # comment'''), ('_Import_names', r'''
x \

'''), r'''
import x \
  # comment
''',
r'''import x  # comment''', r'''
Module - ROOT 0,0..1,11
  .body[1]
   0] Import - 0,0..0,8
     .names[1]
      0] alias - 0,7..0,8
        .name 'x'
'''),

('', 0, 'end', None, {'norm': True}, (None,
r'''import a, b, c  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all Import.names without norm_self=False')**'''),

('', 0, 'end', None, {'norm_self': False, '_verify_self': False}, (None,
r'''import a, b, c  # comment'''),
r'''**DEL**''',
r'''import   # comment''',
r'''Import - ROOT 0,0..0,7'''),

('body[0]', 1, 1, None, {}, ('exec',
r'''import a'''), ('_Import_names', r'''
b \
, \
c \

'''), r'''
import a, b \
       , \
       c \

''',
r'''import a, b, c''', r'''
Module - ROOT 0,0..3,0
  .body[1]
   0] Import - 0,0..2,8
     .names[3]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'b'
      2] alias - 2,7..2,8
        .name 'c'
'''),

('body[0]', 1, 1, None, {}, ('exec',
r'''import a'''), ('_Import_names', r'''
\
b \
, \
c \

'''), r'''
import a, \
       b \
       , \
       c \

''',
r'''import a, b, c''', r'''
Module - ROOT 0,0..4,0
  .body[1]
   0] Import - 0,0..3,8
     .names[3]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 1,7..1,8
        .name 'b'
      2] alias - 3,7..3,8
        .name 'c'
'''),

('body[0]', 1, 1, None, {}, (None, r'''
if 1:
  import x;
'''), ('_Import_names',
r'''y'''), r'''
if 1:
  import x, y;
''', r'''
If - ROOT 0,0..1,14
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Import - 1,2..1,13
     .names[2]
      0] alias - 1,9..1,10
        .name 'x'
      1] alias - 1,12..1,13
        .name 'y'
'''),

('', 1, 1, None, {}, (None,
r'''import x, y, z'''), ('_Import_names',
r''''''),
r'''import x, y, z''', r'''
Import - ROOT 0,0..0,14
  .names[3]
   0] alias - 0,7..0,8
     .name 'x'
   1] alias - 0,10..0,11
     .name 'y'
   2] alias - 0,13..0,14
     .name 'z'
'''),

('', 0, 'end', None, {}, (None,
r'''import _'''), (None,
r'''(a)'''),
r'''import a''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'a'
'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''import _'''), (None,
r'''(a)'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 0, 'end', None, {}, (None,
r'''import _'''), (None,
r'''(a, b)'''),
r'''**ParseError('expecting _aliases, could not parse or coerce')**'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''import _'''), (None,
r'''(a, b)'''),
r'''**SyntaxError('invalid syntax')**'''),
],

'Import_names_coerce': [  # ................................................................................

('', 1, 3, 'names', {'one': True}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('_aliases',
r'''x.x as x, y.y as y'''),
r'''import a.a as a, x.x as x, y.y as y''', r'''
Import - ROOT 0,0..0,35
  .names[3]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,25
     .name 'x.x'
     .asname 'x'
   2] alias - 0,27..0,35
     .name 'y.y'
     .asname 'y'
'''),

('', 1, 3, 'names', {'one': True, 'coerce': False}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('_aliases',
r'''x.x as x, y.y as y'''),
r'''import a.a as a, x.x as x, y.y as y''',
r'''**ValueError("cannot put _aliases node as 'one=True' without 'coerce=True'")**''', r'''
Import - ROOT 0,0..0,35
  .names[3]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,25
     .name 'x.x'
     .asname 'x'
   2] alias - 0,27..0,35
     .name 'y.y'
     .asname 'y'
'''),

('', 1, 3, 'names', {}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('alias',
r'''x.x as x'''),
r'''import a.a as a, x.x as x''', r'''
Import - ROOT 0,0..0,25
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,25
     .name 'x.x'
     .asname 'x'
'''),

('', 1, 3, 'names', {'coerce': False}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('alias',
r'''x.x as x'''),
r'''import a.a as a, x.x as x''',
r'''**NodeError('expecting _aliases, got alias')**''', r'''
Import - ROOT 0,0..0,25
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,25
     .name 'x.x'
     .asname 'x'
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('alias',
r'''x.x as x'''),
r'''import a.a as a, x.x as x''', r'''
Import - ROOT 0,0..0,25
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,25
     .name 'x.x'
     .asname 'x'
'''),

('', 1, 3, 'names', {}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('Name',
r'''x'''),
r'''import a.a as a, x''', r'''
Import - ROOT 0,0..0,18
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,18
     .name 'x'
'''),

('', 1, 3, 'names', {'coerce': False}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('Name',
r'''x'''),
r'''import a.a as a, x''',
r'''**NodeError('expecting _aliases, got Name')**''', r'''
Import - ROOT 0,0..0,18
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,18
     .name 'x'
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('Name',
r'''x'''),
r'''import a.a as a, x''', r'''
Import - ROOT 0,0..0,18
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,18
     .name 'x'
'''),

('', 1, 3, 'names', {}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('Attribute',
r'''x.x'''),
r'''import a.a as a, x.x''', r'''
Import - ROOT 0,0..0,20
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,20
     .name 'x.x'
'''),

('', 1, 3, 'names', {'coerce': False}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('Attribute',
r'''x.x'''),
r'''import a.a as a, x.x''',
r'''**NodeError('expecting _aliases, got Attribute')**''', r'''
Import - ROOT 0,0..0,20
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,20
     .name 'x.x'
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, (None,
r'''import a.a as a, b.b as b, c.c as c'''), ('Attribute',
r'''x.x'''),
r'''import a.a as a, x.x''', r'''
Import - ROOT 0,0..0,20
  .names[2]
   0] alias - 0,7..0,15
     .name 'a.a'
     .asname 'a'
   1] alias - 0,17..0,20
     .name 'x.x'
'''),

('', 1, 3, 'names', {'one': True}, ('_aliases',
r'''a as a, b as b, c as c'''), ('_aliases',
r'''x.x as x, y.y as y'''),
r'''a as a, x.x as x, y.y as y''', r'''
_aliases - ROOT 0,0..0,26
  .names[3]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,16
     .name 'x.x'
     .asname 'x'
   2] alias - 0,18..0,26
     .name 'y.y'
     .asname 'y'
'''),

('', 1, 3, 'names', {'one': True, 'coerce': False}, ('_aliases',
r'''a as a, b as b, c as c'''), ('_aliases',
r'''x.x as x, y.y as y'''),
r'''a as a, x.x as x, y.y as y''',
r'''**ValueError("cannot put _aliases node as 'one=True' without 'coerce=True'")**''', r'''
_aliases - ROOT 0,0..0,26
  .names[3]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,16
     .name 'x.x'
     .asname 'x'
   2] alias - 0,18..0,26
     .name 'y.y'
     .asname 'y'
'''),

('', 1, 3, 'names', {}, ('_aliases',
r'''a as a, b as b, c as c'''), ('alias',
r'''x.x as x'''),
r'''a as a, x.x as x''', r'''
_aliases - ROOT 0,0..0,16
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,16
     .name 'x.x'
     .asname 'x'
'''),

('', 1, 3, 'names', {'coerce': False}, ('_aliases',
r'''a as a, b as b, c as c'''), ('alias',
r'''x.x as x'''),
r'''a as a, x.x as x''',
r'''**NodeError('expecting _aliases, got alias')**''', r'''
_aliases - ROOT 0,0..0,16
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,16
     .name 'x.x'
     .asname 'x'
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, ('_aliases',
r'''a as a, b as b, c as c'''), ('alias',
r'''x.x as x'''),
r'''a as a, x.x as x''', r'''
_aliases - ROOT 0,0..0,16
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,16
     .name 'x.x'
     .asname 'x'
'''),

('', 1, 3, 'names', {}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,9
     .name 'x'
'''),

('', 1, 3, 'names', {'coerce': False}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''',
r'''**NodeError('expecting _aliases, got Name')**''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,9
     .name 'x'
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,9
     .name 'x'
'''),

('', 1, 3, 'names', {}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Attribute',
r'''x.x'''),
r'''a as a, x.x''', r'''
_aliases - ROOT 0,0..0,11
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,11
     .name 'x.x'
'''),

('', 1, 3, 'names', {'coerce': False}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Attribute',
r'''x.x'''),
r'''a as a, x.x''',
r'''**NodeError('expecting _aliases, got Attribute')**''', r'''
_aliases - ROOT 0,0..0,11
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,11
     .name 'x.x'
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Attribute',
r'''x.x'''),
r'''a as a, x.x''', r'''
_aliases - ROOT 0,0..0,11
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,11
     .name 'x.x'
'''),

('', 0, 'end', 'names', {}, (None,
r'''import a'''), ('Name',
r'''(x)'''),
r'''import x''', r'''
Import - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,7..0,8
     .name 'x'
'''),

('', 0, 'end', 'names', {}, (None,
r'''import a'''), ('Attribute',
r'''(x).y'''),
r'''import x.y''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'x.y'
'''),

('', 0, 'end', 'names', {}, (None,
r'''import a'''), ('Attribute',
r'''((x).y)'''),
r'''import x.y''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'x.y'
'''),
],

'Import_names_semicolon': [  # ................................................................................

('body[0]', 2, 2, None, {}, ('exec',
r'''import a, b ; import c'''), ('_aliases',
r'''d  # comment'''),
r'''import a, b, d ; import c''', r'''
Module - ROOT 0,0..0,25
  .body[2]
   0] Import - 0,0..0,14
     .names[3]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'b'
      2] alias - 0,13..0,14
        .name 'd'
   1] Import - 0,17..0,25
     .names[1]
      0] alias - 0,24..0,25
        .name 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''import a, b ; import c'''), ('_aliases', r'''
d,
e

'''), r'''
import a, b, d, \
       e ; import c
''',
r'''import a, b, d, e ; import c''', r'''
Module - ROOT 0,0..1,19
  .body[2]
   0] Import - 0,0..1,8
     .names[4]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'b'
      2] alias - 0,13..0,14
        .name 'd'
      3] alias - 1,7..1,8
        .name 'e'
   1] Import - 1,11..1,19
     .names[1]
      0] alias - 1,18..1,19
        .name 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''import a, b ; import c'''), ('_aliases', r'''
d,
e  # comment

'''), r'''
import a, b, d, \
       e ; import c
''',
r'''import a, b, d, e ; import c''', r'''
Module - ROOT 0,0..1,19
  .body[2]
   0] Import - 0,0..1,8
     .names[4]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'b'
      2] alias - 0,13..0,14
        .name 'd'
      3] alias - 1,7..1,8
        .name 'e'
   1] Import - 1,11..1,19
     .names[1]
      0] alias - 1,18..1,19
        .name 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''import a, b ;'''), ('_aliases',
r'''d  # comment'''),
r'''import a, b, d ;''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Import - 0,0..0,14
     .names[3]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'b'
      2] alias - 0,13..0,14
        .name 'd'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''import a, b ;'''), ('_aliases', r'''
d,
e

'''), r'''
import a, b, d, \
       e ;
''',
r'''import a, b, d, e ;''', r'''
Module - ROOT 0,0..1,10
  .body[1]
   0] Import - 0,0..1,8
     .names[4]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'b'
      2] alias - 0,13..0,14
        .name 'd'
      3] alias - 1,7..1,8
        .name 'e'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''import a, b ;'''), ('_aliases', r'''
d,
e  # comment

'''), r'''
import a, b, d, \
       e ;
''',
r'''import a, b, d, e ;''', r'''
Module - ROOT 0,0..1,10
  .body[1]
   0] Import - 0,0..1,8
     .names[4]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'b'
      2] alias - 0,13..0,14
        .name 'd'
      3] alias - 1,7..1,8
        .name 'e'
'''),

('', 2, 2, None, {}, (None,
r'''import a, b ;'''), ('_aliases',
r'''d  # comment'''),
r'''import a, b, d ;''', r'''
Import - ROOT 0,0..0,14
  .names[3]
   0] alias - 0,7..0,8
     .name 'a'
   1] alias - 0,10..0,11
     .name 'b'
   2] alias - 0,13..0,14
     .name 'd'
'''),

('', 2, 2, None, {}, (None,
r'''import a, b ;'''), ('_aliases', r'''
d,
e

'''), r'''
import a, b, d, \
       e ;
''',
r'''import a, b, d, e ;''', r'''
Import - ROOT 0,0..1,8
  .names[4]
   0] alias - 0,7..0,8
     .name 'a'
   1] alias - 0,10..0,11
     .name 'b'
   2] alias - 0,13..0,14
     .name 'd'
   3] alias - 1,7..1,8
     .name 'e'
'''),

('', 2, 2, None, {}, (None,
r'''import a, b ;'''), ('_aliases', r'''
d,
e  # comment

'''), r'''
import a, b, d, \
       e ;
''',
r'''import a, b, d, e ;''', r'''
Import - ROOT 0,0..1,8
  .names[4]
   0] alias - 0,7..0,8
     .name 'a'
   1] alias - 0,10..0,11
     .name 'b'
   2] alias - 0,13..0,14
     .name 'd'
   3] alias - 1,7..1,8
     .name 'e'
'''),
],

'ImportFrom_names': [  # ................................................................................

('body[0]', 1, 2, None, {}, ('exec',
r'''from mod import a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''from mod import a, c  # comment''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] ImportFrom - 0,0..0,20
     .module 'mod'
     .names[2]
      0] alias - 0,16..0,17
        .name 'a'
      1] alias - 0,19..0,20
        .name 'c'
     .level 0
'''),

('body[0]', 1, 3, None, {}, ('exec',
r'''from mod import a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''from mod import a  # comment''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name 'a'
     .level 0
'''),

('body[0]', 0, 2, None, {}, ('exec',
r'''from mod import a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''from mod import c  # comment''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name 'c'
     .level 0
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
from mod import a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
from mod import a \
, \
c  # comment
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] ImportFrom - 0,0..2,1
     .module 'mod'
     .names[2]
      0] alias - 0,16..0,17
        .name 'a'
      1] alias - 2,0..2,1
        .name 'c'
     .level 0
'''),

('body[0]', 0, 2, None, {}, ('exec', r'''
from mod import a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
from mod import (
c)  # comment
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] ImportFrom - 0,0..1,2
     .module 'mod'
     .names[1]
      0] alias - 1,0..1,1
        .name 'c'
     .level 0
'''),

('body[0]', 1, 3, None, {}, ('exec', r'''
from mod import a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
from mod import a \
 \
  # comment
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name 'a'
     .level 0
'''),

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  from mod import a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  from mod import  \
  b  # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] ImportFrom - 1,2..2,3
        .module 'mod'
        .names[1]
         0] alias - 2,2..2,3
           .name 'b'
        .level 0
      1] Pass - 3,2..3,6
'''),

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  from mod import a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  from mod import a \
   \
    # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] ImportFrom - 1,2..1,19
        .module 'mod'
        .names[1]
         0] alias - 1,18..1,19
           .name 'a'
        .level 0
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, None, {}, ('exec', r'''
if 1:
  from mod import a
  pass
'''), ('_Import_names', r'''
x \
  , \
  y

'''), r'''
if 1:
  from mod import (x \
                  , \
                  y,
                  a)
  pass
''', r'''
if 1:
  from mod import x, y, a
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] ImportFrom - 1,2..4,20
        .module 'mod'
        .names[3]
         0] alias - 1,19..1,20
           .name 'x'
         1] alias - 3,18..3,19
           .name 'y'
         2] alias - 4,18..4,19
           .name 'a'
        .level 0
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''from mod import a, b, c  # comment'''), ('_Import_names',
r'''x'''),
r'''from mod import a, x, c  # comment''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] ImportFrom - 0,0..0,23
     .module 'mod'
     .names[3]
      0] alias - 0,16..0,17
        .name 'a'
      1] alias - 0,19..0,20
        .name 'x'
      2] alias - 0,22..0,23
        .name 'c'
     .level 0
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''from mod import a, b, c  # comment'''), ('_Import_names',
r'''x.y'''),
r'''**ParseError('expecting _aliases, could not parse or coerce')**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''from mod import a, b, c  # comment'''), ('_Import_names', r'''
x \

'''), r'''
from mod import x \
  # comment
''',
r'''from mod import x  # comment''', r'''
Module - ROOT 0,0..1,11
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name 'x'
     .level 0
'''),

('', 0, 'end', None, {'norm': True}, (None,
r'''from mod import a, b, c  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all ImportFrom.names without norm_self=False')**'''),

('', 0, 'end', None, {'norm_self': False, '_verify_self': False}, (None,
r'''from mod import a, b, c  # comment'''),
r'''**DEL**''',
r'''from mod import   # comment''', r'''
ImportFrom - ROOT 0,0..0,16
  .module 'mod'
  .level 0
'''),

('body[0]', 1, 1, None, {}, ('exec',
r'''from mod import a'''), ('_Import_names', r'''
b \
, \
c \

'''), r'''
from mod import a, b \
                , \
                c \

''',
r'''from mod import a, b, c''', r'''
Module - ROOT 0,0..3,0
  .body[1]
   0] ImportFrom - 0,0..2,17
     .module 'mod'
     .names[3]
      0] alias - 0,16..0,17
        .name 'a'
      1] alias - 0,19..0,20
        .name 'b'
      2] alias - 2,16..2,17
        .name 'c'
     .level 0
'''),

('body[0]', 1, 1, None, {}, ('exec',
r'''from mod import a'''), ('_Import_names', r'''
\
b \
, \
c \

'''), r'''
from mod import a, \
                b \
                , \
                c \

''',
r'''from mod import a, b, c''', r'''
Module - ROOT 0,0..4,0
  .body[1]
   0] ImportFrom - 0,0..3,17
     .module 'mod'
     .names[3]
      0] alias - 0,16..0,17
        .name 'a'
      1] alias - 1,16..1,17
        .name 'b'
      2] alias - 3,16..3,17
        .name 'c'
     .level 0
'''),

('body[0]', 1, 1, None, {}, (None, r'''
if 1:
  from mod import x;
'''), ('_Import_names',
r'''y'''), r'''
if 1:
  from mod import x, y;
''', r'''
If - ROOT 0,0..1,23
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ImportFrom - 1,2..1,22
     .module 'mod'
     .names[2]
      0] alias - 1,18..1,19
        .name 'x'
      1] alias - 1,21..1,22
        .name 'y'
     .level 0
'''),

('', 0, 'end', None, {}, (None,
r'''from . import _'''), (None,
r'''(a)'''),
r'''from . import a''', r'''
ImportFrom - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,14..0,15
     .name 'a'
  .level 1
'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''from . import _'''), (None,
r'''(a)'''),
r'''**SyntaxError('ImportFrom.names cannot have explicit parentheses')**'''),

('', 0, 'end', None, {}, (None,
r'''from . import _'''), (None,
r'''(a, b)'''),
r'''**ParseError('expecting _aliases, could not parse or coerce')**'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''from . import _'''), (None,
r'''(a, b)'''),
r'''**SyntaxError('ImportFrom.names cannot have explicit parentheses')**'''),
],

'ImportFrom_names_coerce': [  # ................................................................................

('', 1, 3, 'names', {'one': True}, (None,
r'''from _ import a as a, b as b, c as c'''), ('_aliases',
r'''x as x, y as y'''),
r'''from _ import a as a, x as x, y as y''', r'''
ImportFrom - ROOT 0,0..0,36
  .module '_'
  .names[3]
   0] alias - 0,14..0,20
     .name 'a'
     .asname 'a'
   1] alias - 0,22..0,28
     .name 'x'
     .asname 'x'
   2] alias - 0,30..0,36
     .name 'y'
     .asname 'y'
  .level 0
'''),

('', 1, 3, 'names', {'one': True, 'coerce': False}, (None,
r'''from _ import a as a, b as b, c as c'''), ('_aliases',
r'''x as x, y as y'''),
r'''from _ import a as a, x as x, y as y''',
r'''**ValueError("cannot put _aliases node as 'one=True' without 'coerce=True'")**''', r'''
ImportFrom - ROOT 0,0..0,36
  .module '_'
  .names[3]
   0] alias - 0,14..0,20
     .name 'a'
     .asname 'a'
   1] alias - 0,22..0,28
     .name 'x'
     .asname 'x'
   2] alias - 0,30..0,36
     .name 'y'
     .asname 'y'
  .level 0
'''),

('', 1, 3, 'names', {}, (None,
r'''from _ import a as a, b as b, c as c'''), ('alias',
r'''x as x'''),
r'''from _ import a as a, x as x''', r'''
ImportFrom - ROOT 0,0..0,28
  .module '_'
  .names[2]
   0] alias - 0,14..0,20
     .name 'a'
     .asname 'a'
   1] alias - 0,22..0,28
     .name 'x'
     .asname 'x'
  .level 0
'''),

('', 1, 3, 'names', {'coerce': False}, (None,
r'''from _ import a as a, b as b, c as c'''), ('alias',
r'''x as x'''),
r'''from _ import a as a, x as x''',
r'''**NodeError('expecting _aliases, got alias')**''', r'''
ImportFrom - ROOT 0,0..0,28
  .module '_'
  .names[2]
   0] alias - 0,14..0,20
     .name 'a'
     .asname 'a'
   1] alias - 0,22..0,28
     .name 'x'
     .asname 'x'
  .level 0
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, (None,
r'''from _ import a as a, b as b, c as c'''), ('alias',
r'''x as x'''),
r'''from _ import a as a, x as x''', r'''
ImportFrom - ROOT 0,0..0,28
  .module '_'
  .names[2]
   0] alias - 0,14..0,20
     .name 'a'
     .asname 'a'
   1] alias - 0,22..0,28
     .name 'x'
     .asname 'x'
  .level 0
'''),

('', 1, 3, 'names', {}, (None,
r'''from _ import a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''from _ import a as a, x''', r'''
ImportFrom - ROOT 0,0..0,23
  .module '_'
  .names[2]
   0] alias - 0,14..0,20
     .name 'a'
     .asname 'a'
   1] alias - 0,22..0,23
     .name 'x'
  .level 0
'''),

('', 1, 3, 'names', {'coerce': False}, (None,
r'''from _ import a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''from _ import a as a, x''',
r'''**NodeError('expecting _aliases, got Name')**''', r'''
ImportFrom - ROOT 0,0..0,23
  .module '_'
  .names[2]
   0] alias - 0,14..0,20
     .name 'a'
     .asname 'a'
   1] alias - 0,22..0,23
     .name 'x'
  .level 0
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, (None,
r'''from _ import a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''from _ import a as a, x''', r'''
ImportFrom - ROOT 0,0..0,23
  .module '_'
  .names[2]
   0] alias - 0,14..0,20
     .name 'a'
     .asname 'a'
   1] alias - 0,22..0,23
     .name 'x'
  .level 0
'''),

('', 1, 3, 'names', {'one': True}, ('_aliases',
r'''a as a, b as b, c as c'''), ('_aliases',
r'''x as x, y as y'''),
r'''a as a, x as x, y as y''', r'''
_aliases - ROOT 0,0..0,22
  .names[3]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,14
     .name 'x'
     .asname 'x'
   2] alias - 0,16..0,22
     .name 'y'
     .asname 'y'
'''),

('', 1, 3, 'names', {'one': True, 'coerce': False}, ('_aliases',
r'''a as a, b as b, c as c'''), ('_aliases',
r'''x as x, y as y'''),
r'''a as a, x as x, y as y''',
r'''**ValueError("cannot put _aliases node as 'one=True' without 'coerce=True'")**''', r'''
_aliases - ROOT 0,0..0,22
  .names[3]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,14
     .name 'x'
     .asname 'x'
   2] alias - 0,16..0,22
     .name 'y'
     .asname 'y'
'''),

('', 1, 3, 'names', {}, ('_aliases',
r'''a as a, b as b, c as c'''), ('alias',
r'''x as x'''),
r'''a as a, x as x''', r'''
_aliases - ROOT 0,0..0,14
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,14
     .name 'x'
     .asname 'x'
'''),

('', 1, 3, 'names', {'coerce': False}, ('_aliases',
r'''a as a, b as b, c as c'''), ('alias',
r'''x as x'''),
r'''a as a, x as x''',
r'''**NodeError('expecting _aliases, got alias')**''', r'''
_aliases - ROOT 0,0..0,14
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,14
     .name 'x'
     .asname 'x'
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, ('_aliases',
r'''a as a, b as b, c as c'''), ('alias',
r'''x as x'''),
r'''a as a, x as x''', r'''
_aliases - ROOT 0,0..0,14
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,14
     .name 'x'
     .asname 'x'
'''),

('', 1, 3, 'names', {}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,9
     .name 'x'
'''),

('', 1, 3, 'names', {'coerce': False}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''',
r'''**NodeError('expecting _aliases, got Name')**''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,9
     .name 'x'
'''),

('', 1, 3, 'names', {'coerce': False, 'one': True}, ('_aliases',
r'''a as a, b as b, c as c'''), ('Name',
r'''x'''),
r'''a as a, x''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,9
     .name 'x'
'''),

('', 0, 'end', 'names', {}, (None,
r'''from . import a'''), ('Name',
r'''(x)'''),
r'''from . import x''', r'''
ImportFrom - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,14..0,15
     .name 'x'
  .level 1
'''),
],

'ImportFrom_names_w_pars': [  # ................................................................................

('body[0]', 1, 2, None, {}, ('exec',
r'''from mod import (a, b, c)  # comment'''), (None,
r'''**DEL**'''),
r'''from mod import (a, c)  # comment''', r'''
Module - ROOT 0,0..0,33
  .body[1]
   0] ImportFrom - 0,0..0,22
     .module 'mod'
     .names[2]
      0] alias - 0,17..0,18
        .name 'a'
      1] alias - 0,20..0,21
        .name 'c'
     .level 0
'''),

('body[0]', 1, 3, None, {}, ('exec',
r'''from mod import (a, b, c)  # comment'''), (None,
r'''**DEL**'''),
r'''from mod import (a)  # comment''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] ImportFrom - 0,0..0,19
     .module 'mod'
     .names[1]
      0] alias - 0,17..0,18
        .name 'a'
     .level 0
'''),

('body[0]', 0, 2, None, {}, ('exec',
r'''from mod import (a, b, c)  # comment'''), (None,
r'''**DEL**'''),
r'''from mod import (c)  # comment''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] ImportFrom - 0,0..0,19
     .module 'mod'
     .names[1]
      0] alias - 0,17..0,18
        .name 'c'
     .level 0
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
from mod import (a \
, \
b \
, \
c  # blah
)  # comment
'''), (None,
r'''**DEL**'''), r'''
from mod import (a \
, \
c  # blah
)  # comment
''', r'''
Module - ROOT 0,0..3,12
  .body[1]
   0] ImportFrom - 0,0..3,1
     .module 'mod'
     .names[2]
      0] alias - 0,17..0,18
        .name 'a'
      1] alias - 2,0..2,1
        .name 'c'
     .level 0
'''),

('body[0]', 0, 2, None, {}, ('exec', r'''
from mod import (a \
, \
b \
, \
c  # blah
)  # comment
'''), (None,
r'''**DEL**'''), r'''
from mod import (
c  # blah
)  # comment
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] ImportFrom - 0,0..2,1
     .module 'mod'
     .names[1]
      0] alias - 1,0..1,1
        .name 'c'
     .level 0
'''),

('body[0]', 1, 3, None, {}, ('exec', r'''
from mod import (a \
, \
b \
, \
c  # blah
)  # comment
'''), (None,
r'''**DEL**'''), r'''
from mod import (a \
 \
)  # comment
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] ImportFrom - 0,0..2,1
     .module 'mod'
     .names[1]
      0] alias - 0,17..0,18
        .name 'a'
     .level 0
'''),

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  from mod import (a \
  , \
  b  # blah
  )  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  from mod import ( \
  b  # blah
  )  # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] ImportFrom - 1,2..3,3
        .module 'mod'
        .names[1]
         0] alias - 2,2..2,3
           .name 'b'
        .level 0
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  from mod import (a \
  , \
  b  # blah
  )  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  from mod import (a \
   \
  )  # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] ImportFrom - 1,2..3,3
        .module 'mod'
        .names[1]
         0] alias - 1,19..1,20
           .name 'a'
        .level 0
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, None, {}, ('exec', r'''
if 1:
  from mod import (a)
  pass
'''), ('_Import_names', r'''
x \
  , \
  y

'''), r'''
if 1:
  from mod import (x \
                   , \
                   y,
                   a)
  pass
''', r'''
if 1:
  from mod import (x, y, a)
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] ImportFrom - 1,2..4,21
        .module 'mod'
        .names[3]
         0] alias - 1,19..1,20
           .name 'x'
         1] alias - 3,19..3,20
           .name 'y'
         2] alias - 4,19..4,20
           .name 'a'
        .level 0
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''from mod import (a, b, c)  # comment'''), ('_Import_names',
r'''x'''),
r'''from mod import (a, x, c)  # comment''', r'''
Module - ROOT 0,0..0,36
  .body[1]
   0] ImportFrom - 0,0..0,25
     .module 'mod'
     .names[3]
      0] alias - 0,17..0,18
        .name 'a'
      1] alias - 0,20..0,21
        .name 'x'
      2] alias - 0,23..0,24
        .name 'c'
     .level 0
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''from mod import (a, b, c)  # comment'''), ('_Import_names',
r'''x.y'''),
r'''**ParseError('expecting _aliases, could not parse or coerce')**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''from mod import (a, b, c)  # comment'''), ('_Import_names', r'''
x \

'''), r'''
from mod import (x \
)  # comment
''',
r'''from mod import (x)  # comment''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] ImportFrom - 0,0..1,1
     .module 'mod'
     .names[1]
      0] alias - 0,17..0,18
        .name 'x'
     .level 0
'''),

('', 0, 'end', None, {'norm': True}, (None,
r'''from mod import (a, b, c)  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all ImportFrom.names without norm_self=False')**'''),

('', 0, 'end', None, {'norm_self': False, '_verify_self': False}, (None,
r'''from mod import (a, b, c)  # comment'''),
r'''**DEL**''',
r'''from mod import ()  # comment''', r'''
ImportFrom - ROOT 0,0..0,18
  .module 'mod'
  .level 0
'''),

('body[0]', 1, 1, None, {}, ('exec',
r'''from mod import (a)'''), ('_Import_names', r'''
b \
, \
c \
  # blah
'''), r'''
from mod import (a, b \
                 , \
                 c \
                   # blah
)
''',
r'''from mod import (a, b, c)''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] ImportFrom - 0,0..4,1
     .module 'mod'
     .names[3]
      0] alias - 0,17..0,18
        .name 'a'
      1] alias - 0,20..0,21
        .name 'b'
      2] alias - 2,17..2,18
        .name 'c'
     .level 0
'''),

('body[0]', 1, 1, None, {}, ('exec',
r'''from mod import (a)'''), ('_Import_names', r'''
\
b \
, \
c \
  # blah
'''), r'''
from mod import (a, \
                 b \
                 , \
                 c \
                   # blah
)
''',
r'''from mod import (a, b, c)''', r'''
Module - ROOT 0,0..5,1
  .body[1]
   0] ImportFrom - 0,0..5,1
     .module 'mod'
     .names[3]
      0] alias - 0,17..0,18
        .name 'a'
      1] alias - 1,17..1,18
        .name 'b'
      2] alias - 3,17..3,18
        .name 'c'
     .level 0
'''),

('body[0]', 1, 1, None, {}, (None, r'''
if 1:
  from mod import (x);
'''), ('_Import_names',
r'''y'''), r'''
if 1:
  from mod import (x, y);
''', r'''
If - ROOT 0,0..1,25
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ImportFrom - 1,2..1,24
     .module 'mod'
     .names[2]
      0] alias - 1,19..1,20
        .name 'x'
      1] alias - 1,22..1,23
        .name 'y'
     .level 0
'''),
],

'ImportFrom_names_star': [  # ................................................................................

('body[0]', 0, 1, None, {}, ('exec',
r'''from mod import a'''), ('_ImportFrom_names',
r'''*'''),
r'''from mod import *''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name '*'
     .level 0
'''),

('body[0]', 0, 0, None, {}, ('exec',
r'''from mod import a'''), ('_ImportFrom_names',
r'''*'''),
r'''**NodeError("if putting star '*' alias it must overwrite all other aliases")**'''),

('body[0]', 1, 1, None, {}, ('exec',
r'''from mod import a'''), ('_ImportFrom_names',
r'''*'''),
r'''**NodeError("if putting star '*' alias it must overwrite all other aliases")**'''),

('body[0]', 0, 1, None, {}, ('exec',
r'''from mod import *'''), ('_ImportFrom_names',
r'''a'''),
r'''from mod import a''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name 'a'
     .level 0
'''),

('body[0]', 0, 0, None, {}, ('exec',
r'''from mod import *'''), ('_ImportFrom_names',
r'''a'''),
r'''**NodeError("if putting over star '*' alias it must be overwritten")**'''),

('body[0]', 1, 1, None, {}, ('exec',
r'''from mod import *'''), ('_ImportFrom_names',
r'''a'''),
r'''**NodeError("if putting over star '*' alias it must be overwritten")**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''from mod import *'''), ('_ImportFrom_names',
r'''*'''),
r'''from mod import *''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name '*'
     .level 0
'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''from mod import a'''), ('_ImportFrom_names', r'''
* \
# blah
'''), r'''
from mod import * \
                # blah

''',
r'''from mod import *''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name '*'
     .level 0
'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''from mod import (a)'''), ('_ImportFrom_names', r'''
* \
# blah
'''),
r'''from mod import *''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name '*'
     .level 0
'''),
],

'ImportFrom_names_semicolon': [  # ................................................................................

('body[0]', 2, 2, None, {}, ('exec',
r'''from z import a, b ; from z import c'''), ('_aliases',
r'''d  # comment'''),
r'''from z import a, b, d ; from z import c''', r'''
Module - ROOT 0,0..0,39
  .body[2]
   0] ImportFrom - 0,0..0,21
     .module 'z'
     .names[3]
      0] alias - 0,14..0,15
        .name 'a'
      1] alias - 0,17..0,18
        .name 'b'
      2] alias - 0,20..0,21
        .name 'd'
     .level 0
   1] ImportFrom - 0,24..0,39
     .module 'z'
     .names[1]
      0] alias - 0,38..0,39
        .name 'c'
     .level 0
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''from z import a, b ; from z import c'''), ('_aliases', r'''
d,
e

'''), r'''
from z import (a, b, d,
              e) ; from z import c
''',
r'''from z import a, b, d, e ; from z import c''', r'''
Module - ROOT 0,0..1,34
  .body[2]
   0] ImportFrom - 0,0..1,16
     .module 'z'
     .names[4]
      0] alias - 0,15..0,16
        .name 'a'
      1] alias - 0,18..0,19
        .name 'b'
      2] alias - 0,21..0,22
        .name 'd'
      3] alias - 1,14..1,15
        .name 'e'
     .level 0
   1] ImportFrom - 1,19..1,34
     .module 'z'
     .names[1]
      0] alias - 1,33..1,34
        .name 'c'
     .level 0
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''from z import a, b ; from z import c'''), ('_aliases', r'''
d,
e  # comment

'''), r'''
from z import (a, b, d,
              e) ; from z import c
''',
r'''from z import a, b, d, e ; from z import c''', r'''
Module - ROOT 0,0..1,34
  .body[2]
   0] ImportFrom - 0,0..1,16
     .module 'z'
     .names[4]
      0] alias - 0,15..0,16
        .name 'a'
      1] alias - 0,18..0,19
        .name 'b'
      2] alias - 0,21..0,22
        .name 'd'
      3] alias - 1,14..1,15
        .name 'e'
     .level 0
   1] ImportFrom - 1,19..1,34
     .module 'z'
     .names[1]
      0] alias - 1,33..1,34
        .name 'c'
     .level 0
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''from z import a, b ;'''), ('_aliases',
r'''d  # comment'''),
r'''from z import a, b, d ;''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] ImportFrom - 0,0..0,21
     .module 'z'
     .names[3]
      0] alias - 0,14..0,15
        .name 'a'
      1] alias - 0,17..0,18
        .name 'b'
      2] alias - 0,20..0,21
        .name 'd'
     .level 0
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''from z import a, b ;'''), ('_aliases', r'''
d,
e

'''), r'''
from z import (a, b, d,
              e) ;
''',
r'''from z import a, b, d, e ;''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] ImportFrom - 0,0..1,16
     .module 'z'
     .names[4]
      0] alias - 0,15..0,16
        .name 'a'
      1] alias - 0,18..0,19
        .name 'b'
      2] alias - 0,21..0,22
        .name 'd'
      3] alias - 1,14..1,15
        .name 'e'
     .level 0
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''from z import a, b ;'''), ('_aliases', r'''
d,
e  # comment

'''), r'''
from z import (a, b, d,
              e) ;
''',
r'''from z import a, b, d, e ;''', r'''
Module - ROOT 0,0..1,18
  .body[1]
   0] ImportFrom - 0,0..1,16
     .module 'z'
     .names[4]
      0] alias - 0,15..0,16
        .name 'a'
      1] alias - 0,18..0,19
        .name 'b'
      2] alias - 0,21..0,22
        .name 'd'
      3] alias - 1,14..1,15
        .name 'e'
     .level 0
'''),

('', 2, 2, None, {}, (None,
r'''from z import a, b ;'''), ('_aliases',
r'''d  # comment'''),
r'''from z import a, b, d ;''', r'''
ImportFrom - ROOT 0,0..0,21
  .module 'z'
  .names[3]
   0] alias - 0,14..0,15
     .name 'a'
   1] alias - 0,17..0,18
     .name 'b'
   2] alias - 0,20..0,21
     .name 'd'
  .level 0
'''),

('', 2, 2, None, {}, (None,
r'''from z import a, b ;'''), ('_aliases', r'''
d,
e

'''), r'''
from z import (a, b, d,
              e) ;
''',
r'''from z import a, b, d, e ;''', r'''
ImportFrom - ROOT 0,0..1,16
  .module 'z'
  .names[4]
   0] alias - 0,15..0,16
     .name 'a'
   1] alias - 0,18..0,19
     .name 'b'
   2] alias - 0,21..0,22
     .name 'd'
   3] alias - 1,14..1,15
     .name 'e'
  .level 0
'''),

('', 2, 2, None, {}, (None,
r'''from z import a, b ;'''), ('_aliases', r'''
d,
e  # comment

'''), r'''
from z import (a, b, d,
              e) ;
''',
r'''from z import a, b, d, e ;''', r'''
ImportFrom - ROOT 0,0..1,16
  .module 'z'
  .names[4]
   0] alias - 0,15..0,16
     .name 'a'
   1] alias - 0,18..0,19
     .name 'b'
   2] alias - 0,21..0,22
     .name 'd'
   3] alias - 1,14..1,15
     .name 'e'
  .level 0
'''),
],

'Global_names': [  # ................................................................................

('body[0]', 0, 2, None, {'raw': True}, ('exec',
r'''global a, b, c'''), (None,
r'''x'''),
r'''global x, c''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Global - 0,0..0,11
     .names[2]
      0] 'x'
      1] 'c'
'''),

('body[0]', 0, 'end', None, {'raw': True}, ('exec',
r'''global a, b, c'''), (None,
r'''x'''),
r'''global x''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'x'
'''),

('body[0]', 1, 2, None, {'raw': True}, ('exec',
r'''global a, b, c'''), (None,
r'''x, y'''),
r'''global a, x, y, c''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Global - 0,0..0,17
     .names[4]
      0] 'a'
      1] 'x'
      2] 'y'
      3] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''global a, c  # comment''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Global - 0,0..0,11
     .names[2]
      0] 'a'
      1] 'c'
'''),

('body[0]', 1, 3, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''global a  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'a'
'''),

('body[0]', 0, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''global c  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
global a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
global a \
, \
c  # comment
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] Global - 0,0..2,1
     .names[2]
      0] 'a'
      1] 'c'
'''),

('body[0]', 0, 2, None, {}, ('exec', r'''
global a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
global \
c  # comment
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Global - 0,0..1,1
     .names[1]
      0] 'c'
'''),

('body[0]', 1, 3, None, {}, ('exec', r'''
global a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
global a \
 \
  # comment
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'a'
'''),

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  global a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  global  \
  b  # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Global - 1,2..2,3
        .names[1]
         0] 'b'
      1] Pass - 3,2..3,6
'''),

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  global a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  global a \
   \
    # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Global - 1,2..1,10
        .names[1]
         0] 'a'
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  global a
  pass
'''), (None, r'''
(
    b \
    , \
  )
'''),
'if 1:\n  global a, \\\n         b \\\n          \\\n       \n  pass', r'''
if 1:
  global a, b
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Global - 1,2..2,10
        .names[2]
         0] 'a'
         1] 'b'
      1] Pass - 5,2..5,6
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  global a
  pass
'''), (None, r'''
(
    b, \
)
'''), r'''
if 1:
  global a, \
         b \

  pass
''', r'''
if 1:
  global a, b
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Global - 1,2..2,10
        .names[2]
         0] 'a'
         1] 'b'
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  global a
  pass
'''), (None, r'''
(
    b,
)
'''), r'''
if 1:
  global a, \
         b

  pass
''', r'''
if 1:
  global a, b
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Global - 1,2..2,10
        .names[2]
         0] 'a'
         1] 'b'
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, None, {}, ('exec', r'''
if 1:
  global a
  pass
'''), (None, r'''
x \
  , \
  y \
  ,
'''), r'''
if 1:
  global x \
         , \
         y \
         , a
  pass
''', r'''
if 1:
  global x, y, a
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Global - 1,2..4,12
        .names[3]
         0] 'x'
         1] 'y'
         2] 'a'
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''x'''),
r'''global a, x, c  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Global - 0,0..0,14
     .names[3]
      0] 'a'
      1] 'x'
      2] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''[x]'''),
r'''global a, x, c  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Global - 0,0..0,14
     .names[3]
      0] 'a'
      1] 'x'
      2] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''{x}'''),
r'''global a, x, c  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Global - 0,0..0,14
     .names[3]
      0] 'a'
      1] 'x'
      2] 'c'
'''),

('body[0]', 1, 2, None, {'norm': True}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''{*()}'''),
r'''global a, c  # comment''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Global - 0,0..0,11
     .names[2]
      0] 'a'
      1] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''x,'''),
r'''global a, x, c  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] Global - 0,0..0,14
     .names[3]
      0] 'a'
      1] 'x'
      2] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''x.y,'''),
r'''**NodeError('cannot put Attribute to Global.names')**'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''(x),'''),
r'''**NodeError('cannot put parenthesized Name to Global.names')**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''global a, b, c  # comment'''), (None, r'''
x \

'''), r'''
global x \
  # comment
''',
r'''global x  # comment''', r'''
Module - ROOT 0,0..1,11
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'x'
'''),

('body[0]', 0, 'end', None, {'norm': True}, ('exec',
r'''global a, b, c  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all Global.names without norm_self=False')**'''),

('body[0]', 0, 'end', None, {'norm_self': False, '_verify_self': False}, ('exec',
r'''global a, b, c  # comment'''),
r'''**DEL**''',
r'''global   # comment''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Global - 0,0..0,7
'''),

('body[0]', 1, 1, None, {}, (None, r'''
if 1:
  global x;
'''), (None,
r'''y,'''), r'''
if 1:
  global x, y;
''', r'''
If - ROOT 0,0..1,14
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Global - 1,2..1,13
     .names[2]
      0] 'x'
      1] 'y'
'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''x'''),
r'''global x''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''x.y'''),
r'''**NodeError('cannot put Attribute to Global.names')**'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''x[y]'''),
r'''**NodeError('cannot put Subscript to Global.names')**'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''*x'''),
r'''**NodeError('cannot put Starred to Global.names')**'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''x,'''),
r'''global x''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''global a, b, c'''), (None,
r'''x,'''),
r'''**NodeError('cannot put Tuple to Global.names')**'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''(x,)'''),
r'''global x''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''global a, b, c'''), (None,
r'''(x,)'''),
r'''**NodeError('cannot put Tuple to Global.names')**'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''[x]'''),
r'''global x''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''global a, b, c'''), (None,
r'''[x]'''),
r'''**NodeError('cannot put List to Global.names')**'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''{x}'''),
r'''global x''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''global a, b, c'''), (None,
r'''{x}'''),
r'''**NodeError('cannot put Set to Global.names')**'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''global a, b, c'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to Global without 'one=True' or 'coerce=True'")**'''),

('', 0, 'end', None, {'coerce': False, 'one': True}, (None,
r'''global a, b, c'''), (None,
r'''x'''),
r'''global x''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {}, (None,
r'''global a, b, c'''), (None,
r'''f()'''),
r'''**NodeError('cannot put Call to Global.names')**'''),

('', 0, 'end', None, {'one': True}, (None,
r'''global a, b, c'''), (None,
r'''f()'''),
r'''**NodeError('cannot put Call to Global.names')**'''),
],

'Global_names_semicolon': [  # ................................................................................

('body[0]', 2, 2, None, {}, ('exec',
r'''global a, b ; global c'''), ('Tuple',
r'''d,  # comment'''),
r'''global a, b, d ; global c''', r'''
Module - ROOT 0,0..0,25
  .body[2]
   0] Global - 0,0..0,14
     .names[3]
      0] 'a'
      1] 'b'
      2] 'd'
   1] Global - 0,17..0,25
     .names[1]
      0] 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''global a, b ; global c'''), ('Tuple', r'''
d,
e

'''), r'''
global a, b, d, \
       e ; global c
''',
r'''global a, b, d, e ; global c''', r'''
Module - ROOT 0,0..1,19
  .body[2]
   0] Global - 0,0..1,8
     .names[4]
      0] 'a'
      1] 'b'
      2] 'd'
      3] 'e'
   1] Global - 1,11..1,19
     .names[1]
      0] 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''global a, b ; global c'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
global a, b, d, \
       e ; global c
''',
r'''global a, b, d, e ; global c''', r'''
Module - ROOT 0,0..1,19
  .body[2]
   0] Global - 0,0..1,8
     .names[4]
      0] 'a'
      1] 'b'
      2] 'd'
      3] 'e'
   1] Global - 1,11..1,19
     .names[1]
      0] 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''global a, b ;'''), ('Tuple',
r'''d,  # comment'''),
r'''global a, b, d ;''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Global - 0,0..0,14
     .names[3]
      0] 'a'
      1] 'b'
      2] 'd'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''global a, b ;'''), ('Tuple', r'''
d,
e

'''), r'''
global a, b, d, \
       e ;
''',
r'''global a, b, d, e ;''', r'''
Module - ROOT 0,0..1,10
  .body[1]
   0] Global - 0,0..1,8
     .names[4]
      0] 'a'
      1] 'b'
      2] 'd'
      3] 'e'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''global a, b ;'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
global a, b, d, \
       e ;
''',
r'''global a, b, d, e ;''', r'''
Module - ROOT 0,0..1,10
  .body[1]
   0] Global - 0,0..1,8
     .names[4]
      0] 'a'
      1] 'b'
      2] 'd'
      3] 'e'
'''),

('', 2, 2, None, {}, (None,
r'''global a, b ;'''), ('Tuple',
r'''d,  # comment'''),
r'''global a, b, d ;''', r'''
Global - ROOT 0,0..0,14
  .names[3]
   0] 'a'
   1] 'b'
   2] 'd'
'''),

('', 2, 2, None, {}, (None,
r'''global a, b ;'''), ('Tuple', r'''
d,
e

'''), r'''
global a, b, d, \
       e ;
''',
r'''global a, b, d, e ;''', r'''
Global - ROOT 0,0..1,8
  .names[4]
   0] 'a'
   1] 'b'
   2] 'd'
   3] 'e'
'''),

('', 2, 2, None, {}, (None,
r'''global a, b ;'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
global a, b, d, \
       e ;
''',
r'''global a, b, d, e ;''', r'''
Global - ROOT 0,0..1,8
  .names[4]
   0] 'a'
   1] 'b'
   2] 'd'
   3] 'e'
'''),
],

'Nonlocal_names': [  # ................................................................................

('body[0]', 0, 2, None, {'raw': True}, ('exec',
r'''nonlocal a, b, c'''), (None,
r'''x'''),
r'''nonlocal x, c''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Nonlocal - 0,0..0,13
     .names[2]
      0] 'x'
      1] 'c'
'''),

('body[0]', 0, 'end', None, {'raw': True}, ('exec',
r'''nonlocal a, b, c'''), (None,
r'''x'''),
r'''nonlocal x''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'x'
'''),

('body[0]', 1, 2, None, {'raw': True}, ('exec',
r'''nonlocal a, b, c'''), (None,
r'''x, y'''),
r'''nonlocal a, x, y, c''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Nonlocal - 0,0..0,19
     .names[4]
      0] 'a'
      1] 'x'
      2] 'y'
      3] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''nonlocal a, c  # comment''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Nonlocal - 0,0..0,13
     .names[2]
      0] 'a'
      1] 'c'
'''),

('body[0]', 1, 3, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''nonlocal a  # comment''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'a'
'''),

('body[0]', 0, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''nonlocal c  # comment''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
nonlocal a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
nonlocal a \
, \
c  # comment
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] Nonlocal - 0,0..2,1
     .names[2]
      0] 'a'
      1] 'c'
'''),

('body[0]', 0, 2, None, {}, ('exec', r'''
nonlocal a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
nonlocal \
c  # comment
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Nonlocal - 0,0..1,1
     .names[1]
      0] 'c'
'''),

('body[0]', 1, 3, None, {}, ('exec', r'''
nonlocal a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''), r'''
nonlocal a \
 \
  # comment
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'a'
'''),

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  nonlocal a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  nonlocal  \
  b  # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Nonlocal - 1,2..2,3
        .names[1]
         0] 'b'
      1] Pass - 3,2..3,6
'''),

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  nonlocal a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  nonlocal a \
   \
    # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Nonlocal - 1,2..1,12
        .names[1]
         0] 'a'
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  nonlocal a
  pass
'''), (None, r'''
(
    b \
    , \
  )
'''),
'if 1:\n  nonlocal a, \\\n           b \\\n            \\\n         \n  pass', r'''
if 1:
  nonlocal a, b
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Nonlocal - 1,2..2,12
        .names[2]
         0] 'a'
         1] 'b'
      1] Pass - 5,2..5,6
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  nonlocal a
  pass
'''), (None, r'''
(
    b, \
)
'''), r'''
if 1:
  nonlocal a, \
           b \

  pass
''', r'''
if 1:
  nonlocal a, b
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Nonlocal - 1,2..2,12
        .names[2]
         0] 'a'
         1] 'b'
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  nonlocal a
  pass
'''), (None, r'''
(
    b,
)
'''), r'''
if 1:
  nonlocal a, \
           b

  pass
''', r'''
if 1:
  nonlocal a, b
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Nonlocal - 1,2..2,12
        .names[2]
         0] 'a'
         1] 'b'
      1] Pass - 4,2..4,6
'''),

('body[0].body[0]', 0, 0, None, {}, ('exec', r'''
if 1:
  nonlocal a
  pass
'''), (None, r'''
x \
  , \
  y \
  ,
'''), r'''
if 1:
  nonlocal x \
           , \
           y \
           , a
  pass
''', r'''
if 1:
  nonlocal x, y, a
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Nonlocal - 1,2..4,14
        .names[3]
         0] 'x'
         1] 'y'
         2] 'a'
      1] Pass - 5,2..5,6
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''x'''),
r'''nonlocal a, x, c  # comment''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Nonlocal - 0,0..0,16
     .names[3]
      0] 'a'
      1] 'x'
      2] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''[x]'''),
r'''nonlocal a, x, c  # comment''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Nonlocal - 0,0..0,16
     .names[3]
      0] 'a'
      1] 'x'
      2] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''{x}'''),
r'''nonlocal a, x, c  # comment''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Nonlocal - 0,0..0,16
     .names[3]
      0] 'a'
      1] 'x'
      2] 'c'
'''),

('body[0]', 1, 2, None, {'norm': True}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''{*()}'''),
r'''nonlocal a, c  # comment''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Nonlocal - 0,0..0,13
     .names[2]
      0] 'a'
      1] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''x,'''),
r'''nonlocal a, x, c  # comment''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] Nonlocal - 0,0..0,16
     .names[3]
      0] 'a'
      1] 'x'
      2] 'c'
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''x.y,'''),
r'''**NodeError('cannot put Attribute to Nonlocal.names')**'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''(x),'''),
r'''**NodeError('cannot put parenthesized Name to Nonlocal.names')**'''),

('body[0]', 0, 'end', None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None, r'''
x \

'''), r'''
nonlocal x \
  # comment
''',
r'''nonlocal x  # comment''', r'''
Module - ROOT 0,0..1,11
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'x'
'''),

('body[0]', 0, 'end', None, {'norm': True}, ('exec',
r'''nonlocal a, b, c  # comment'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all Nonlocal.names without norm_self=False')**'''),

('body[0]', 0, 'end', None, {'norm_self': False, '_verify_self': False}, ('exec',
r'''nonlocal a, b, c  # comment'''),
r'''**DEL**''',
r'''nonlocal   # comment''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Nonlocal - 0,0..0,9
'''),

('body[0]', 1, 1, None, {}, (None, r'''
if 1:
  nonlocal x;
'''), (None,
r'''y,'''), r'''
if 1:
  nonlocal x, y;
''', r'''
If - ROOT 0,0..1,16
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Nonlocal - 1,2..1,15
     .names[2]
      0] 'x'
      1] 'y'
'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x'''),
r'''nonlocal x''', r'''
Nonlocal - ROOT 0,0..0,10
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x.y'''),
r'''**NodeError('cannot put Attribute to Nonlocal.names')**'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x[y]'''),
r'''**NodeError('cannot put Subscript to Nonlocal.names')**'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''*x'''),
r'''**NodeError('cannot put Starred to Nonlocal.names')**'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x,'''),
r'''nonlocal x''', r'''
Nonlocal - ROOT 0,0..0,10
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x,'''),
r'''**NodeError('cannot put Tuple to Nonlocal.names')**'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''(x,)'''),
r'''nonlocal x''', r'''
Nonlocal - ROOT 0,0..0,10
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''(x,)'''),
r'''**NodeError('cannot put Tuple to Nonlocal.names')**'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''[x]'''),
r'''nonlocal x''', r'''
Nonlocal - ROOT 0,0..0,10
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''[x]'''),
r'''**NodeError('cannot put List to Nonlocal.names')**'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''{x}'''),
r'''nonlocal x''', r'''
Nonlocal - ROOT 0,0..0,10
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {'one': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''{x}'''),
r'''**NodeError('cannot put Set to Nonlocal.names')**'''),

('', 0, 'end', None, {'coerce': False}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to Nonlocal without 'one=True' or 'coerce=True'")**'''),

('', 0, 'end', None, {'coerce': False, 'one': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x'''),
r'''nonlocal x''', r'''
Nonlocal - ROOT 0,0..0,10
  .names[1]
   0] 'x'
'''),

('', 0, 'end', None, {}, (None,
r'''nonlocal a, b, c'''), (None,
r'''f()'''),
r'''**NodeError('cannot put Call to Nonlocal.names')**'''),

('', 0, 'end', None, {'one': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''f()'''),
r'''**NodeError('cannot put Call to Nonlocal.names')**'''),
],

'Nonlocal_names_semicolon': [  # ................................................................................

('body[0]', 2, 2, None, {}, ('exec',
r'''nonlocal a, b ; nonlocal c'''), ('Tuple',
r'''d,  # comment'''),
r'''nonlocal a, b, d ; nonlocal c''', r'''
Module - ROOT 0,0..0,29
  .body[2]
   0] Nonlocal - 0,0..0,16
     .names[3]
      0] 'a'
      1] 'b'
      2] 'd'
   1] Nonlocal - 0,19..0,29
     .names[1]
      0] 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''nonlocal a, b ; nonlocal c'''), ('Tuple', r'''
d,
e

'''), r'''
nonlocal a, b, d, \
         e ; nonlocal c
''',
r'''nonlocal a, b, d, e ; nonlocal c''', r'''
Module - ROOT 0,0..1,23
  .body[2]
   0] Nonlocal - 0,0..1,10
     .names[4]
      0] 'a'
      1] 'b'
      2] 'd'
      3] 'e'
   1] Nonlocal - 1,13..1,23
     .names[1]
      0] 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''nonlocal a, b ; nonlocal c'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
nonlocal a, b, d, \
         e ; nonlocal c
''',
r'''nonlocal a, b, d, e ; nonlocal c''', r'''
Module - ROOT 0,0..1,23
  .body[2]
   0] Nonlocal - 0,0..1,10
     .names[4]
      0] 'a'
      1] 'b'
      2] 'd'
      3] 'e'
   1] Nonlocal - 1,13..1,23
     .names[1]
      0] 'c'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''nonlocal a, b ;'''), ('Tuple',
r'''d,  # comment'''),
r'''nonlocal a, b, d ;''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Nonlocal - 0,0..0,16
     .names[3]
      0] 'a'
      1] 'b'
      2] 'd'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''nonlocal a, b ;'''), ('Tuple', r'''
d,
e

'''), r'''
nonlocal a, b, d, \
         e ;
''',
r'''nonlocal a, b, d, e ;''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Nonlocal - 0,0..1,10
     .names[4]
      0] 'a'
      1] 'b'
      2] 'd'
      3] 'e'
'''),

('body[0]', 2, 2, None, {}, ('exec',
r'''nonlocal a, b ;'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
nonlocal a, b, d, \
         e ;
''',
r'''nonlocal a, b, d, e ;''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Nonlocal - 0,0..1,10
     .names[4]
      0] 'a'
      1] 'b'
      2] 'd'
      3] 'e'
'''),

('', 2, 2, None, {}, (None,
r'''nonlocal a, b ;'''), ('Tuple',
r'''d,  # comment'''),
r'''nonlocal a, b, d ;''', r'''
Nonlocal - ROOT 0,0..0,16
  .names[3]
   0] 'a'
   1] 'b'
   2] 'd'
'''),

('', 2, 2, None, {}, (None,
r'''nonlocal a, b ;'''), ('Tuple', r'''
d,
e

'''), r'''
nonlocal a, b, d, \
         e ;
''',
r'''nonlocal a, b, d, e ;''', r'''
Nonlocal - ROOT 0,0..1,10
  .names[4]
   0] 'a'
   1] 'b'
   2] 'd'
   3] 'e'
'''),

('', 2, 2, None, {}, (None,
r'''nonlocal a, b ;'''), ('Tuple', r'''
d,
e  # comment

'''), r'''
nonlocal a, b, d, \
         e ;
''',
r'''nonlocal a, b, d, e ;''', r'''
Nonlocal - ROOT 0,0..1,10
  .names[4]
   0] 'a'
   1] 'b'
   2] 'd'
   3] 'e'
'''),
],

'ClassDef_bases': [  # ................................................................................

('', 0, 1, 'bases', {}, (None, r'''
class cls( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''x,'''), r'''
class cls( \
x,
* \
b \
, \
c \
, \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..9,7
  .name 'cls'
  .bases[3]
   0] Name 'x' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 5,0..5,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
  .body[1]
   0] Pass - 9,3..9,7
'''),

('', 1, 2, 'bases', {}, (None, r'''
class cls( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''x,'''), r'''
class cls( \
a \
, \
x,
c \
, \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..8,7
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'x' Load - 3,0..3,1
   2] Name 'c' Load - 4,0..4,1
  .keywords[1]
   0] keyword - 6,0..7,1
     .value Name 'd' Load - 7,0..7,1
  .body[1]
   0] Pass - 8,3..8,7
'''),

('', 2, 3, 'bases', {}, (None, r'''
class cls( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''x,'''), r'''
class cls( \
a \
, \
* \
b \
, \
x,
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..9,7
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'x' Load - 6,0..6,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
  .body[1]
   0] Pass - 9,3..9,7
'''),

('', 0, 3, 'bases', {}, (None, r'''
class cls( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''x,'''), r'''
class cls( \
x,
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..4,7
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 1,0..1,1
  .keywords[1]
   0] keyword - 2,0..3,1
     .value Name 'd' Load - 3,0..3,1
  .body[1]
   0] Pass - 4,3..4,7
'''),

('', 0, 3, 'bases', {}, (None, r'''
class cls( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''**DEL**'''), r'''
class cls( \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..3,7
  .name 'cls'
  .keywords[1]
   0] keyword - 1,0..2,1
     .value Name 'd' Load - 2,0..2,1
  .body[1]
   0] Pass - 3,3..3,7
'''),

('', 0, 1, 'bases', {}, (None, r'''
class cls(
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''x,'''), r'''
class cls(
x,
*
b
,
c
,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..9,7
  .name 'cls'
  .bases[3]
   0] Name 'x' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 5,0..5,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
  .body[1]
   0] Pass - 9,3..9,7
'''),

('', 1, 2, 'bases', {}, (None, r'''
class cls(
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''x,'''), r'''
class cls(
a
,
x,
c
,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..8,7
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'x' Load - 3,0..3,1
   2] Name 'c' Load - 4,0..4,1
  .keywords[1]
   0] keyword - 6,0..7,1
     .value Name 'd' Load - 7,0..7,1
  .body[1]
   0] Pass - 8,3..8,7
'''),

('', 2, 3, 'bases', {}, (None, r'''
class cls(
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''x,'''), r'''
class cls(
a
,
*
b
,
x,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..9,7
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'x' Load - 6,0..6,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
  .body[1]
   0] Pass - 9,3..9,7
'''),

('', 0, 3, 'bases', {}, (None, r'''
class cls(
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''x,'''), r'''
class cls(
x,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..4,7
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 1,0..1,1
  .keywords[1]
   0] keyword - 2,0..3,1
     .value Name 'd' Load - 3,0..3,1
  .body[1]
   0] Pass - 4,3..4,7
'''),

('', 0, 3, 'bases', {}, (None, r'''
class cls(
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''**DEL**'''), r'''
class cls(
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..3,7
  .name 'cls'
  .keywords[1]
   0] keyword - 1,0..2,1
     .value Name 'd' Load - 2,0..2,1
  .body[1]
   0] Pass - 3,3..3,7
'''),

('', 0, 2, 'bases', {}, (None,
r'''class cls(a, b=c, *d): pass'''), (None,
r'''x,'''),
r'''**NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')**'''),

('', 1, 2, 'bases', {}, (None,
r'''class cls(a, b=c, *d): pass'''), (None,
r'''x,'''),
r'''**NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')**'''),

('', 0, 1, 'bases', {}, (None,
r'''class cls(a, b=c, *d): pass'''), (None,
r'''x,'''),
r'''class cls(x, b=c, *d): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'd' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'b'
     .value Name 'c' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,23..0,27
'''),

('', 0, 1, 'bases', {}, (None,
r'''class cls(a, b=c, *d,): pass'''), (None,
r'''x,'''),
r'''class cls(x, b=c, *d,): pass''', r'''
ClassDef - ROOT 0,0..0,28
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'd' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'b'
     .value Name 'c' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,24..0,28
'''),

('', 0, 1, 'bases', {}, (None,
r'''class cls(a, b, c=d, *e): pass'''), (None,
r'''x,'''),
r'''class cls(x, b, c=d, *e): pass''', r'''
ClassDef - ROOT 0,0..0,30
  .name 'cls'
  .bases[3]
   0] Name 'x' Load - 0,10..0,11
   1] Name 'b' Load - 0,13..0,14
   2] Starred - 0,21..0,23
     .value Name 'e' Load - 0,22..0,23
     .ctx Load
  .keywords[1]
   0] keyword - 0,16..0,19
     .arg 'c'
     .value Name 'd' Load - 0,18..0,19
  .body[1]
   0] Pass - 0,26..0,30
'''),

('', 1, 2, 'bases', {}, (None,
r'''class cls(a, b, c=d, *e): pass'''), (None,
r'''x,'''),
r'''class cls(a, x, c=d, *e): pass''', r'''
ClassDef - ROOT 0,0..0,30
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 0,10..0,11
   1] Name 'x' Load - 0,13..0,14
   2] Starred - 0,21..0,23
     .value Name 'e' Load - 0,22..0,23
     .ctx Load
  .keywords[1]
   0] keyword - 0,16..0,19
     .arg 'c'
     .value Name 'd' Load - 0,18..0,19
  .body[1]
   0] Pass - 0,26..0,30
'''),

('', 0, 2, 'bases', {}, (None,
r'''class cls(a, b, c=d, *e): pass'''), (None,
r'''x,'''),
r'''class cls(x, c=d, *e): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'e' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'c'
     .value Name 'd' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,23..0,27
'''),

('', 0, 2, 'bases', {}, (None,
r'''class cls(a, b, c=d, *e,): pass'''), (None,
r'''x,'''),
r'''class cls(x, c=d, *e,): pass''', r'''
ClassDef - ROOT 0,0..0,28
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'e' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'c'
     .value Name 'd' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,24..0,28
'''),

('', 0, 0, 'bases', {}, (None,
r'''class cls: pass'''), (None,
r'''x,'''),
r'''class cls(x): pass''', r'''
ClassDef - ROOT 0,0..0,18
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,10..0,11
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', 0, 0, 'bases', {}, (None,
r'''class cls: pass'''), (None,
r'''x,'''),
r'''class cls(x): pass''', r'''
ClassDef - ROOT 0,0..0,18
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,10..0,11
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', 0, 0, 'bases', {}, (None,
r'''class cls: pass'''), (None,
r'''x, y,'''),
r'''class cls(x, y): pass''', r'''
ClassDef - ROOT 0,0..0,21
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Name 'y' Load - 0,13..0,14
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', 0, 0, 'bases', {}, (None,
r'''class cls(a=b): pass'''), (None,
r'''x,'''),
r'''class cls(x, a=b): pass''', r'''
ClassDef - ROOT 0,0..0,23
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,10..0,11
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'a'
     .value Name 'b' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', 0, 0, 'bases', {}, (None,
r'''class cls(a=b,): pass'''), (None,
r'''x,'''),
r'''class cls(x, a=b,): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,10..0,11
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'a'
     .value Name 'b' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 0, 1, 'bases', {}, (None,
r'''class cls(a, b): pass'''), (None,
r'''**DEL**'''),
r'''class cls(b): pass''', r'''
ClassDef - ROOT 0,0..0,18
  .name 'cls'
  .bases[1]
   0] Name 'b' Load - 0,10..0,11
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', 1, 2, 'bases', {}, (None,
r'''class cls(a, b): pass'''), (None,
r'''**DEL**'''),
r'''class cls(a): pass''', r'''
ClassDef - ROOT 0,0..0,18
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,10..0,11
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', 0, 2, 'bases', {}, (None,
r'''class cls(a, b): pass'''), (None,
r'''**DEL**'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
'''),

('', 1, 2, 'bases', {}, (None,
r'''class cls(a, b, **c): pass'''), (None,
r'''**DEL**'''),
r'''class cls(a, **c): pass''', r'''
ClassDef - ROOT 0,0..0,23
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,10..0,11
  .keywords[1]
   0] keyword - 0,13..0,16
     .value Name 'c' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', 0, 2, 'bases', {}, (None,
r'''class cls(a, b, **c): pass'''), (None,
r'''**DEL**'''),
r'''class cls(**c): pass''', r'''
ClassDef - ROOT 0,0..0,20
  .name 'cls'
  .keywords[1]
   0] keyword - 0,10..0,13
     .value Name 'c' Load - 0,12..0,13
  .body[1]
   0] Pass - 0,16..0,20
'''),

('', 1, 2, 'bases', {}, (None,
r'''class cls(a, b, **c,): pass'''), (None,
r'''**DEL**'''),
r'''class cls(a, **c,): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,10..0,11
  .keywords[1]
   0] keyword - 0,13..0,16
     .value Name 'c' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 0, 2, 'bases', {}, (None,
r'''class cls(a, b, **c,): pass'''), (None,
r'''**DEL**'''),
r'''class cls(**c,): pass''', r'''
ClassDef - ROOT 0,0..0,21
  .name 'cls'
  .keywords[1]
   0] keyword - 0,10..0,13
     .value Name 'c' Load - 0,12..0,13
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', 0, 0, 'bases', {'one': True}, (None,
r'''class cls(): pass'''), (None,
r'''x'''),
r'''class cls(x): pass''', r'''
ClassDef - ROOT 0,0..0,18
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,10..0,11
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', 0, 0, 'bases', {'one': True}, (None,
r'''class cls(): pass'''), (None,
r'''x,'''),
r'''class cls((x,)): pass''', r'''
ClassDef - ROOT 0,0..0,21
  .name 'cls'
  .bases[1]
   0] Tuple - 0,10..0,14
     .elts[1]
      0] Name 'x' Load - 0,11..0,12
     .ctx Load
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', 0, 0, 'bases', {'one': True}, (None,
r'''class cls(): pass'''), (None,
r'''x, y,'''),
r'''class cls((x, y,)): pass''',
r'''class cls((x, y)): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[1]
   0] Tuple - 0,10..0,17
     .elts[2]
      0] Name 'x' Load - 0,11..0,12
      1] Name 'y' Load - 0,14..0,15
     .ctx Load
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', 0, 2, 'bases', {'one': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''x'''),
r'''class cls(x, c): pass''', r'''
ClassDef - ROOT 0,0..0,21
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Name 'c' Load - 0,13..0,14
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', 1, 3, 'bases', {'one': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''x'''),
r'''class cls(a, x): pass''', r'''
ClassDef - ROOT 0,0..0,21
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Name 'x' Load - 0,13..0,14
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', 0, 3, 'bases', {'one': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''x'''),
r'''class cls(x): pass''', r'''
ClassDef - ROOT 0,0..0,18
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,10..0,11
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', 0, 2, 'bases', {'one': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''*not a'''),
r'''class cls(*not a, c): pass''',
r'''class cls(*(not a), c): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[2]
   0] Starred - 0,10..0,16
     .value UnaryOp - 0,11..0,16
       .op Not - 0,11..0,14
       .operand Name 'a' Load - 0,15..0,16
     .ctx Load
   1] Name 'c' Load - 0,18..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, 3, 'bases', {'one': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''*not a'''),
r'''class cls(a, *not a): pass''',
r'''class cls(a, *(not a)): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,19
     .value UnaryOp - 0,14..0,19
       .op Not - 0,14..0,17
       .operand Name 'a' Load - 0,18..0,19
     .ctx Load
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 0, 3, 'bases', {'one': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''*not a'''),
r'''class cls(*not a): pass''',
r'''class cls(*(not a)): pass''', r'''
ClassDef - ROOT 0,0..0,23
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,16
     .value UnaryOp - 0,11..0,16
       .op Not - 0,11..0,14
       .operand Name 'a' Load - 0,15..0,16
     .ctx Load
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', 0, 2, 'bases', {'_ver': 11}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''*not a,'''),
r'''class cls(*not a, c): pass''',
r'''class cls(*(not a), c): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[2]
   0] Starred - 0,10..0,16
     .value UnaryOp - 0,11..0,16
       .op Not - 0,11..0,14
       .operand Name 'a' Load - 0,15..0,16
     .ctx Load
   1] Name 'c' Load - 0,18..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 1, 3, 'bases', {'_ver': 11}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''*not a,'''),
r'''class cls(a, *not a): pass''',
r'''class cls(a, *(not a)): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,19
     .value UnaryOp - 0,14..0,19
       .op Not - 0,14..0,17
       .operand Name 'a' Load - 0,18..0,19
     .ctx Load
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 0, 3, 'bases', {'_ver': 11}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''*not a,'''),
r'''class cls(*not a): pass''',
r'''class cls(*(not a)): pass''', r'''
ClassDef - ROOT 0,0..0,23
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,16
     .value UnaryOp - 0,11..0,16
       .op Not - 0,11..0,14
       .operand Name 'a' Load - 0,15..0,16
     .ctx Load
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', 1, 2, 'bases', {}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''*(not a),'''),
r'''class cls(a, *(not a), c): pass''', r'''
ClassDef - ROOT 0,0..0,31
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,21
     .value UnaryOp - 0,15..0,20
       .op Not - 0,15..0,18
       .operand Name 'a' Load - 0,19..0,20
     .ctx Load
   2] Name 'c' Load - 0,23..0,24
  .body[1]
   0] Pass - 0,27..0,31
'''),

('', 0, 2, 'bases', {'one': True}, (None,
r'''class cls(a, b, **c,): pass'''), (None,
r'''*not a'''),
r'''class cls(*not a, **c,): pass''',
r'''class cls(*(not a), **c,): pass''', r'''
ClassDef - ROOT 0,0..0,29
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,16
     .value UnaryOp - 0,11..0,16
       .op Not - 0,11..0,14
       .operand Name 'a' Load - 0,15..0,16
     .ctx Load
  .keywords[1]
   0] keyword - 0,18..0,21
     .value Name 'c' Load - 0,20..0,21
  .body[1]
   0] Pass - 0,25..0,29
'''),

('', 0, 'end', 'bases', {'_ver': 11}, (None,
r'''class cls: pass'''), (None,
r'''*not a, *b or c'''),
r'''class cls(*not a, *b or c): pass''',
r'''class cls(*(not a), *(b or c)): pass''', r'''
ClassDef - ROOT 0,0..0,32
  .name 'cls'
  .bases[2]
   0] Starred - 0,10..0,16
     .value UnaryOp - 0,11..0,16
       .op Not - 0,11..0,14
       .operand Name 'a' Load - 0,15..0,16
     .ctx Load
   1] Starred - 0,18..0,25
     .value BoolOp - 0,19..0,25
       .op Or
       .values[2]
        0] Name 'b' Load - 0,19..0,20
        1] Name 'c' Load - 0,24..0,25
     .ctx Load
  .body[1]
   0] Pass - 0,28..0,32
'''),

('', 0, 'end', 'bases', {'one': True}, (None,
r'''class cls: pass'''), (None,
r'''*not a, *b or c'''),
r'''**ParseError('expecting single expression (arglike)')**'''),

('', 0, 2, 'bases', {}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''*not a'''),
r'''class cls(*not a, c): pass''',
r'''class cls(*(not a), c): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[2]
   0] Starred - 0,10..0,16
     .value UnaryOp - 0,11..0,16
       .op Not - 0,11..0,14
       .operand Name 'a' Load - 0,15..0,16
     .ctx Load
   1] Name 'c' Load - 0,18..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),
],

'ClassDef_bases_w_type_params': [  # ................................................................................

('', 0, 1, 'bases', {'_ver': 12}, (None, r'''
class cls[T]( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''x,'''), r'''
class cls[T]( \
x,
* \
b \
, \
c \
, \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..9,7
  .name 'cls'
  .bases[3]
   0] Name 'x' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 5,0..5,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
  .body[1]
   0] Pass - 9,3..9,7
  .type_params[1]
   0] TypeVar - 0,10..0,11
     .name 'T'
'''),

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls[T, *U]( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''x,'''), r'''
class cls[T, *U]( \
a \
, \
x,
c \
, \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..8,7
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'x' Load - 3,0..3,1
   2] Name 'c' Load - 4,0..4,1
  .keywords[1]
   0] keyword - 6,0..7,1
     .value Name 'd' Load - 7,0..7,1
  .body[1]
   0] Pass - 8,3..8,7
  .type_params[2]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,13..0,15
     .name 'U'
'''),

('', 2, 3, 'bases', {'_ver': 12}, (None, r'''
class cls [T,
*U] ( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''x,'''), r'''
class cls [T,
*U] ( \
a \
, \
* \
b \
, \
x,
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..10,7
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 2,0..2,1
   1] Starred - 4,0..5,1
     .value Name 'b' Load - 5,0..5,1
     .ctx Load
   2] Name 'x' Load - 7,0..7,1
  .keywords[1]
   0] keyword - 8,0..9,1
     .value Name 'd' Load - 9,0..9,1
  .body[1]
   0] Pass - 10,3..10,7
  .type_params[2]
   0] TypeVar - 0,11..0,12
     .name 'T'
   1] TypeVarTuple - 1,0..1,2
     .name 'U'
'''),

('', 0, 3, 'bases', {'_ver': 12}, (None, r'''
class cls [
T
] \
( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''x,'''), r'''
class cls [
T
] \
( \
x,
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..7,7
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 4,0..4,1
  .keywords[1]
   0] keyword - 5,0..6,1
     .value Name 'd' Load - 6,0..6,1
  .body[1]
   0] Pass - 7,3..7,7
  .type_params[1]
   0] TypeVar - 1,0..1,1
     .name 'T'
'''),

('', 0, 3, 'bases', {'_ver': 12}, (None, r'''
class cls \
[T] \
( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
): pass
'''), (None,
r'''**DEL**'''), r'''
class cls \
[T] \
( \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..5,7
  .name 'cls'
  .keywords[1]
   0] keyword - 3,0..4,1
     .value Name 'd' Load - 4,0..4,1
  .body[1]
   0] Pass - 5,3..5,7
  .type_params[1]
   0] TypeVar - 1,1..1,2
     .name 'T'
'''),

('', 0, 1, 'bases', {'_ver': 12}, (None, r'''
class cls[T, *U
](
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''x,'''), r'''
class cls[T, *U
](
x,
*
b
,
c
,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..10,7
  .name 'cls'
  .bases[3]
   0] Name 'x' Load - 2,0..2,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'c' Load - 6,0..6,1
  .keywords[1]
   0] keyword - 8,0..9,1
     .value Name 'd' Load - 9,0..9,1
  .body[1]
   0] Pass - 10,3..10,7
  .type_params[2]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,13..0,15
     .name 'U'
'''),

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls \
[
T, *U
] \
(
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''x,'''), r'''
class cls \
[
T, *U
] \
(
a
,
x,
c
,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..12,7
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 5,0..5,1
   1] Name 'x' Load - 7,0..7,1
   2] Name 'c' Load - 8,0..8,1
  .keywords[1]
   0] keyword - 10,0..11,1
     .value Name 'd' Load - 11,0..11,1
  .body[1]
   0] Pass - 12,3..12,7
  .type_params[2]
   0] TypeVar - 2,0..2,1
     .name 'T'
   1] TypeVarTuple - 2,3..2,5
     .name 'U'
'''),

('', 2, 3, 'bases', {'_ver': 12}, (None, r'''
class cls[T, *U, **V](
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''x,'''), r'''
class cls[T, *U, **V](
a
,
*
b
,
x,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..9,7
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'x' Load - 6,0..6,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
  .body[1]
   0] Pass - 9,3..9,7
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,13..0,15
     .name 'U'
   2] ParamSpec - 0,17..0,20
     .name 'V'
'''),

('', 0, 3, 'bases', {'_ver': 12}, (None, r'''
class cls \
[T, *U, \
**V] \
(
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''x,'''), r'''
class cls \
[T, *U, \
**V] \
(
x,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..7,7
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 4,0..4,1
  .keywords[1]
   0] keyword - 5,0..6,1
     .value Name 'd' Load - 6,0..6,1
  .body[1]
   0] Pass - 7,3..7,7
  .type_params[3]
   0] TypeVar - 1,1..1,2
     .name 'T'
   1] TypeVarTuple - 1,4..1,6
     .name 'U'
   2] ParamSpec - 2,0..2,3
     .name 'V'
'''),

('', 0, 3, 'bases', {'_ver': 12}, (None, r'''
class cls[
T, *U, **V] \
(
a
,
*
b
,
c
,
**
d
): pass
'''), (None,
r'''**DEL**'''), r'''
class cls[
T, *U, **V] \
(
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..5,7
  .name 'cls'
  .keywords[1]
   0] keyword - 3,0..4,1
     .value Name 'd' Load - 4,0..4,1
  .body[1]
   0] Pass - 5,3..5,7
  .type_params[3]
   0] TypeVar - 1,0..1,1
     .name 'T'
   1] TypeVarTuple - 1,3..1,5
     .name 'U'
   2] ParamSpec - 1,7..1,10
     .name 'V'
'''),

('', 0, 2, 'bases', {'_ver': 12}, (None,
r'''class cls [T, *U, **V] (a, b=c, *d): pass'''), (None,
r'''x,'''),
r'''**NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')**'''),

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls [T,
*U,
**V,
] (a, b=c, *d): pass
'''), (None,
r'''x,'''),
r'''**NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')**'''),

('', 0, 1, 'bases', {'_ver': 12}, (None,
r'''class cls[T,](a, b=c, *d): pass'''), (None,
r'''x,'''),
r'''class cls[T,](x, b=c, *d): pass''', r'''
ClassDef - ROOT 0,0..0,31
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,14..0,15
   1] Starred - 0,22..0,24
     .value Name 'd' Load - 0,23..0,24
     .ctx Load
  .keywords[1]
   0] keyword - 0,17..0,20
     .arg 'b'
     .value Name 'c' Load - 0,19..0,20
  .body[1]
   0] Pass - 0,27..0,31
  .type_params[1]
   0] TypeVar - 0,10..0,11
     .name 'T'
'''),

('', 0, 1, 'bases', {'_ver': 12}, (None, r'''
class cls[ \
T \
, \
* \
U \
, \
** \
V \
, \
](a, b=c, *d,): pass
'''), (None,
r'''x,'''), r'''
class cls[ \
T \
, \
* \
U \
, \
** \
V \
, \
](x, b=c, *d,): pass
''', r'''
ClassDef - ROOT 0,0..9,20
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 9,2..9,3
   1] Starred - 9,10..9,12
     .value Name 'd' Load - 9,11..9,12
     .ctx Load
  .keywords[1]
   0] keyword - 9,5..9,8
     .arg 'b'
     .value Name 'c' Load - 9,7..9,8
  .body[1]
   0] Pass - 9,16..9,20
  .type_params[3]
   0] TypeVar - 1,0..1,1
     .name 'T'
   1] TypeVarTuple - 3,0..4,1
     .name 'U'
   2] ParamSpec - 6,0..7,1
     .name 'V'
'''),

('', 0, 1, 'bases', {'_ver': 12}, (None, r'''
class cls \
[ \
T \
, \
* \
U \
, \
** \
V \
, \
] \
(a, b, c=d, *e): pass
'''), (None,
r'''x,'''), r'''
class cls \
[ \
T \
, \
* \
U \
, \
** \
V \
, \
] \
(x, b, c=d, *e): pass
''', r'''
ClassDef - ROOT 0,0..11,21
  .name 'cls'
  .bases[3]
   0] Name 'x' Load - 11,1..11,2
   1] Name 'b' Load - 11,4..11,5
   2] Starred - 11,12..11,14
     .value Name 'e' Load - 11,13..11,14
     .ctx Load
  .keywords[1]
   0] keyword - 11,7..11,10
     .arg 'c'
     .value Name 'd' Load - 11,9..11,10
  .body[1]
   0] Pass - 11,17..11,21
  .type_params[3]
   0] TypeVar - 2,0..2,1
     .name 'T'
   1] TypeVarTuple - 4,0..5,1
     .name 'U'
   2] ParamSpec - 7,0..8,1
     .name 'V'
'''),

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls[ \
T] \
(a, b, c=d, *e): pass
'''), (None,
r'''x,'''), r'''
class cls[ \
T] \
(a, x, c=d, *e): pass
''', r'''
ClassDef - ROOT 0,0..2,21
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 2,1..2,2
   1] Name 'x' Load - 2,4..2,5
   2] Starred - 2,12..2,14
     .value Name 'e' Load - 2,13..2,14
     .ctx Load
  .keywords[1]
   0] keyword - 2,7..2,10
     .arg 'c'
     .value Name 'd' Load - 2,9..2,10
  .body[1]
   0] Pass - 2,17..2,21
  .type_params[1]
   0] TypeVar - 1,0..1,1
     .name 'T'
'''),

('', 0, 2, 'bases', {'_ver': 12}, (None, r'''
class cls[
T
,
*
U
,
**
V
,
](a, b, c=d, *e): pass
'''), (None,
r'''x,'''), r'''
class cls[
T
,
*
U
,
**
V
,
](x, c=d, *e): pass
''', r'''
ClassDef - ROOT 0,0..9,19
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 9,2..9,3
   1] Starred - 9,10..9,12
     .value Name 'e' Load - 9,11..9,12
     .ctx Load
  .keywords[1]
   0] keyword - 9,5..9,8
     .arg 'c'
     .value Name 'd' Load - 9,7..9,8
  .body[1]
   0] Pass - 9,15..9,19
  .type_params[3]
   0] TypeVar - 1,0..1,1
     .name 'T'
   1] TypeVarTuple - 3,0..4,1
     .name 'U'
   2] ParamSpec - 6,0..7,1
     .name 'V'
'''),

('', 0, 2, 'bases', {'_ver': 12}, (None, r'''
class cls[
T
,
*
U
,
**
V
] \
(a, b, c=d, *e,): pass
'''), (None,
r'''x,'''), r'''
class cls[
T
,
*
U
,
**
V
] \
(x, c=d, *e,): pass
''', r'''
ClassDef - ROOT 0,0..9,19
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 9,1..9,2
   1] Starred - 9,9..9,11
     .value Name 'e' Load - 9,10..9,11
     .ctx Load
  .keywords[1]
   0] keyword - 9,4..9,7
     .arg 'c'
     .value Name 'd' Load - 9,6..9,7
  .body[1]
   0] Pass - 9,15..9,19
  .type_params[3]
   0] TypeVar - 1,0..1,1
     .name 'T'
   1] TypeVarTuple - 3,0..4,1
     .name 'U'
   2] ParamSpec - 6,0..7,1
     .name 'V'
'''),

('', 0, 0, 'bases', {'_ver': 12}, (None,
r'''class cls[ T, *U ]: pass'''), (None,
r'''x,'''),
r'''class cls[ T, *U ](x): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,19..0,20
  .body[1]
   0] Pass - 0,23..0,27
  .type_params[2]
   0] TypeVar - 0,11..0,12
     .name 'T'
   1] TypeVarTuple - 0,14..0,16
     .name 'U'
'''),

('', 0, 0, 'bases', {'_ver': 12}, (None,
r'''class cls[T]: pass'''), (None,
r'''x,'''),
r'''class cls[T](x): pass''', r'''
ClassDef - ROOT 0,0..0,21
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,13..0,14
  .body[1]
   0] Pass - 0,17..0,21
  .type_params[1]
   0] TypeVar - 0,10..0,11
     .name 'T'
'''),

('', 0, 0, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U]: pass'''), (None,
r'''x, y,'''),
r'''class cls[T,*U](x, y): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,16..0,17
   1] Name 'y' Load - 0,19..0,20
  .body[1]
   0] Pass - 0,23..0,27
  .type_params[2]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
'''),

('', 0, 0, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a=b): pass'''), (None,
r'''x,'''),
r'''class cls[T,*U,**V](x, a=b): pass''', r'''
ClassDef - ROOT 0,0..0,33
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,20..0,21
  .keywords[1]
   0] keyword - 0,23..0,26
     .arg 'a'
     .value Name 'b' Load - 0,25..0,26
  .body[1]
   0] Pass - 0,29..0,33
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 0, 'bases', {'_ver': 12}, (None, r'''
class cls[
T
,
](a=b,): pass
'''), (None,
r'''x,'''), r'''
class cls[
T
,
](x, a=b,): pass
''', r'''
ClassDef - ROOT 0,0..3,16
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 3,2..3,3
  .keywords[1]
   0] keyword - 3,5..3,8
     .arg 'a'
     .value Name 'b' Load - 3,7..3,8
  .body[1]
   0] Pass - 3,12..3,16
  .type_params[1]
   0] TypeVar - 1,0..1,1
     .name 'T'
'''),

('', 0, 1, 'bases', {'_ver': 12}, (None, r'''
class cls\
[T]\
(a, b): pass
'''), (None,
r'''**DEL**'''), r'''
class cls\
[T]\
(b): pass
''', r'''
ClassDef - ROOT 0,0..2,9
  .name 'cls'
  .bases[1]
   0] Name 'b' Load - 2,1..2,2
  .body[1]
   0] Pass - 2,5..2,9
  .type_params[1]
   0] TypeVar - 1,1..1,2
     .name 'T'
'''),

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls \
 [T] \
 \
 (a, b): pass
'''), (None,
r'''**DEL**'''), r'''
class cls \
 [T] \
 \
 (a): pass
''', r'''
ClassDef - ROOT 0,0..3,10
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 3,2..3,3
  .body[1]
   0] Pass - 3,6..3,10
  .type_params[1]
   0] TypeVar - 1,2..1,3
     .name 'T'
'''),

('', 0, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U](a, b): pass'''), (None,
r'''**DEL**'''),
r'''class cls[T,*U]: pass''', r'''
ClassDef - ROOT 0,0..0,21
  .name 'cls'
  .body[1]
   0] Pass - 0,17..0,21
  .type_params[2]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
'''),

('', 1, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a, b, **c): pass'''), (None,
r'''**DEL**'''),
r'''class cls[T,*U,**V](a, **c): pass''', r'''
ClassDef - ROOT 0,0..0,33
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,20..0,21
  .keywords[1]
   0] keyword - 0,23..0,26
     .value Name 'c' Load - 0,25..0,26
  .body[1]
   0] Pass - 0,29..0,33
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a, b, **c): pass'''), (None,
r'''**DEL**'''),
r'''class cls[T,*U,**V](**c): pass''', r'''
ClassDef - ROOT 0,0..0,30
  .name 'cls'
  .keywords[1]
   0] keyword - 0,20..0,23
     .value Name 'c' Load - 0,22..0,23
  .body[1]
   0] Pass - 0,26..0,30
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 1, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a, b, **c,): pass'''), (None,
r'''**DEL**'''),
r'''class cls[T,*U,**V](a, **c,): pass''', r'''
ClassDef - ROOT 0,0..0,34
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,20..0,21
  .keywords[1]
   0] keyword - 0,23..0,26
     .value Name 'c' Load - 0,25..0,26
  .body[1]
   0] Pass - 0,30..0,34
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a, b, **c,): pass'''), (None,
r'''**DEL**'''),
r'''class cls[T,*U,**V](**c,): pass''', r'''
ClassDef - ROOT 0,0..0,31
  .name 'cls'
  .keywords[1]
   0] keyword - 0,20..0,23
     .value Name 'c' Load - 0,22..0,23
  .body[1]
   0] Pass - 0,27..0,31
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 0, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V](): pass'''), (None,
r'''x'''),
r'''class cls[T,*U,**V](x): pass''', r'''
ClassDef - ROOT 0,0..0,28
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,20..0,21
  .body[1]
   0] Pass - 0,24..0,28
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 0, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V]: pass'''), (None,
r'''x,'''),
r'''class cls[T,*U,**V]((x,)): pass''', r'''
ClassDef - ROOT 0,0..0,31
  .name 'cls'
  .bases[1]
   0] Tuple - 0,20..0,24
     .elts[1]
      0] Name 'x' Load - 0,21..0,22
     .ctx Load
  .body[1]
   0] Pass - 0,27..0,31
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 0, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V]: pass'''), (None,
r'''x, y,'''),
r'''class cls[T,*U,**V]((x, y,)): pass''',
r'''class cls[T,*U,**V]((x, y)): pass''', r'''
ClassDef - ROOT 0,0..0,34
  .name 'cls'
  .bases[1]
   0] Tuple - 0,20..0,27
     .elts[2]
      0] Name 'x' Load - 0,21..0,22
      1] Name 'y' Load - 0,24..0,25
     .ctx Load
  .body[1]
   0] Pass - 0,30..0,34
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 2, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''x'''),
r'''class cls[T,*U,**V](x, c): pass''', r'''
ClassDef - ROOT 0,0..0,31
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,20..0,21
   1] Name 'c' Load - 0,23..0,24
  .body[1]
   0] Pass - 0,27..0,31
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 1, 3, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''x'''),
r'''class cls[T,*U,**V](a, x): pass''', r'''
ClassDef - ROOT 0,0..0,31
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,20..0,21
   1] Name 'x' Load - 0,23..0,24
  .body[1]
   0] Pass - 0,27..0,31
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 3, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''x'''),
r'''class cls[T,*U,**V](x): pass''', r'''
ClassDef - ROOT 0,0..0,28
  .name 'cls'
  .bases[1]
   0] Name 'x' Load - 0,20..0,21
  .body[1]
   0] Pass - 0,24..0,28
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 2, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''*not a'''),
r'''class cls[T,*U,**V](*not a, c): pass''',
r'''class cls[T,*U,**V](*(not a), c): pass''', r'''
ClassDef - ROOT 0,0..0,36
  .name 'cls'
  .bases[2]
   0] Starred - 0,20..0,26
     .value UnaryOp - 0,21..0,26
       .op Not - 0,21..0,24
       .operand Name 'a' Load - 0,25..0,26
     .ctx Load
   1] Name 'c' Load - 0,28..0,29
  .body[1]
   0] Pass - 0,32..0,36
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 1, 3, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''*not a'''),
r'''class cls[T,*U,**V](a, *not a): pass''',
r'''class cls[T,*U,**V](a, *(not a)): pass''', r'''
ClassDef - ROOT 0,0..0,36
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,20..0,21
   1] Starred - 0,23..0,29
     .value UnaryOp - 0,24..0,29
       .op Not - 0,24..0,27
       .operand Name 'a' Load - 0,28..0,29
     .ctx Load
  .body[1]
   0] Pass - 0,32..0,36
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 3, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''*not a'''),
r'''class cls[T,*U,**V](*not a): pass''',
r'''class cls[T,*U,**V](*(not a)): pass''', r'''
ClassDef - ROOT 0,0..0,33
  .name 'cls'
  .bases[1]
   0] Starred - 0,20..0,26
     .value UnaryOp - 0,21..0,26
       .op Not - 0,21..0,24
       .operand Name 'a' Load - 0,25..0,26
     .ctx Load
  .body[1]
   0] Pass - 0,29..0,33
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''*not a,'''),
r'''class cls[T,*U,**V](*not a, c): pass''',
r'''class cls[T,*U,**V](*(not a), c): pass''', r'''
ClassDef - ROOT 0,0..0,36
  .name 'cls'
  .bases[2]
   0] Starred - 0,20..0,26
     .value UnaryOp - 0,21..0,26
       .op Not - 0,21..0,24
       .operand Name 'a' Load - 0,25..0,26
     .ctx Load
   1] Name 'c' Load - 0,28..0,29
  .body[1]
   0] Pass - 0,32..0,36
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 1, 3, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''*not a,'''),
r'''class cls[T,*U,**V](a, *not a): pass''',
r'''class cls[T,*U,**V](a, *(not a)): pass''', r'''
ClassDef - ROOT 0,0..0,36
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,20..0,21
   1] Starred - 0,23..0,29
     .value UnaryOp - 0,24..0,29
       .op Not - 0,24..0,27
       .operand Name 'a' Load - 0,28..0,29
     .ctx Load
  .body[1]
   0] Pass - 0,32..0,36
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 3, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''*not a,'''),
r'''class cls[T,*U,**V](*not a): pass''',
r'''class cls[T,*U,**V](*(not a)): pass''', r'''
ClassDef - ROOT 0,0..0,33
  .name 'cls'
  .bases[1]
   0] Starred - 0,20..0,26
     .value UnaryOp - 0,21..0,26
       .op Not - 0,21..0,24
       .operand Name 'a' Load - 0,25..0,26
     .ctx Load
  .body[1]
   0] Pass - 0,29..0,33
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 1, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T,*U,**V](a, b, c): pass'''), (None,
r'''*(not a),'''),
r'''class cls[T,*U,**V](a, *(not a), c): pass''', r'''
ClassDef - ROOT 0,0..0,41
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 0,20..0,21
   1] Starred - 0,23..0,31
     .value UnaryOp - 0,25..0,30
       .op Not - 0,25..0,28
       .operand Name 'a' Load - 0,29..0,30
     .ctx Load
   2] Name 'c' Load - 0,33..0,34
  .body[1]
   0] Pass - 0,37..0,41
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),

('', 0, 2, 'bases', {'_ver': 12, 'one': True}, (None,
r'''class cls[T,*U,**V](a, b, **c,): pass'''), (None,
r'''*not a'''),
r'''class cls[T,*U,**V](*not a, **c,): pass''',
r'''class cls[T,*U,**V](*(not a), **c,): pass''', r'''
ClassDef - ROOT 0,0..0,39
  .name 'cls'
  .bases[1]
   0] Starred - 0,20..0,26
     .value UnaryOp - 0,21..0,26
       .op Not - 0,21..0,24
       .operand Name 'a' Load - 0,25..0,26
     .ctx Load
  .keywords[1]
   0] keyword - 0,28..0,31
     .value Name 'c' Load - 0,30..0,31
  .body[1]
   0] Pass - 0,35..0,39
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,12..0,14
     .name 'U'
   2] ParamSpec - 0,15..0,18
     .name 'V'
'''),
],

'BoolOp_values': [  # ................................................................................

('', 0, 1, None, {}, (None,
r'''a and b and c'''), (None,
r'''x'''),
r'''x and b and c''', r'''
BoolOp - ROOT 0,0..0,13
  .op And
  .values[3]
   0] Name 'x' Load - 0,0..0,1
   1] Name 'b' Load - 0,6..0,7
   2] Name 'c' Load - 0,12..0,13
'''),

('', 1, 2, None, {}, (None,
r'''a and b and c'''), (None,
r'''x'''),
r'''a and x and c''', r'''
BoolOp - ROOT 0,0..0,13
  .op And
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 0,6..0,7
   2] Name 'c' Load - 0,12..0,13
'''),

('', 2, 3, None, {}, (None,
r'''a and b and c'''), (None,
r'''x'''),
r'''a and b and x''', r'''
BoolOp - ROOT 0,0..0,13
  .op And
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,6..0,7
   2] Name 'x' Load - 0,12..0,13
'''),

('', 0, 2, None, {}, (None,
r'''a and b and c'''), (None,
r'''x'''),
r'''x and c''', r'''
BoolOp - ROOT 0,0..0,7
  .op And
  .values[2]
   0] Name 'x' Load - 0,0..0,1
   1] Name 'c' Load - 0,6..0,7
'''),

('', 1, 3, None, {}, (None,
r'''a and b and c'''), (None,
r'''x'''),
r'''a and x''', r'''
BoolOp - ROOT 0,0..0,7
  .op And
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 0,6..0,7
'''),

('', 0, 3, None, {'_verify_self': False}, (None,
r'''a and b and c'''), (None,
r'''x'''),
r'''x''', r'''
BoolOp - ROOT 0,0..0,1
  .op And
  .values[1]
   0] Name 'x' Load - 0,0..0,1
'''),

('', 0, 3, None, {'norm_self': True}, (None,
r'''a and b and c'''), (None,
r'''x'''),
r'''x''',
r'''Name 'x' Load - ROOT 0,0..0,1'''),

('', 0, 1, None, {}, (None,
r'''a and b and c'''), (None,
r'''( x )'''),
r'''( x ) and b and c''',
r'''x and b and c''', r'''
BoolOp - ROOT 0,0..0,17
  .op And
  .values[3]
   0] Name 'x' Load - 0,2..0,3
   1] Name 'b' Load - 0,10..0,11
   2] Name 'c' Load - 0,16..0,17
'''),

('', 1, 2, None, {}, (None,
r'''a and b and c'''), (None,
r'''( x )'''),
r'''a and ( x ) and c''',
r'''a and x and c''', r'''
BoolOp - ROOT 0,0..0,17
  .op And
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 0,8..0,9
   2] Name 'c' Load - 0,16..0,17
'''),

('', 2, 3, None, {}, (None,
r'''a and b and c'''), (None,
r'''( x )'''),
r'''a and b and ( x )''',
r'''a and b and x''', r'''
BoolOp - ROOT 0,0..0,17
  .op And
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,6..0,7
   2] Name 'x' Load - 0,14..0,15
'''),

('', 0, 2, None, {}, (None,
r'''a and b and c'''), (None,
r'''( x )'''),
r'''( x ) and c''',
r'''x and c''', r'''
BoolOp - ROOT 0,0..0,11
  .op And
  .values[2]
   0] Name 'x' Load - 0,2..0,3
   1] Name 'c' Load - 0,10..0,11
'''),

('', 1, 3, None, {}, (None,
r'''a and b and c'''), (None,
r'''( x )'''),
r'''a and ( x )''',
r'''a and x''', r'''
BoolOp - ROOT 0,0..0,11
  .op And
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 0,8..0,9
'''),

('', 0, 3, None, {'_verify_self': False}, (None,
r'''a and b and c'''), (None,
r'''( x )'''),
r'''( x )''',
r'''x''', r'''
BoolOp - ROOT 0,0..0,5
  .op And
  .values[1]
   0] Name 'x' Load - 0,2..0,3
'''),

('', 0, 3, None, {'norm_self': True}, (None,
r'''a and b and c'''), (None,
r'''( x )'''),
r'''( x )''',
r'''x''',
r'''Name 'x' Load - ROOT 0,2..0,3'''),

('', 0, 1, None, {}, (None,
r'''a and b and c'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(# pre
x  # line
# post
and b and c)
''',
r'''x and b and c''', r'''
BoolOp - ROOT 1,0..3,11
  .op And
  .values[3]
   0] Name 'x' Load - 1,0..1,1
   1] Name 'b' Load - 3,4..3,5
   2] Name 'c' Load - 3,10..3,11
'''),

('', 0, 1, None, {'pars': False}, (None,
r'''a and b and c'''), (None, r'''
# pre
x  # line
# post
'''), r'''
# pre
x  # line
# post
and b and c
''',
r'''x and b and c''', r'''
BoolOp - ROOT 1,0..3,11
  .op And
  .values[3]
   0] Name 'x' Load - 1,0..1,1
   1] Name 'b' Load - 3,4..3,5
   2] Name 'c' Load - 3,10..3,11
'''),

('', 1, 2, None, {}, (None,
r'''a and b and c'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(a and # pre
x  # line
# post
and c)
''',
r'''a and x and c''', r'''
BoolOp - ROOT 0,1..3,5
  .op And
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,0..1,1
   2] Name 'c' Load - 3,4..3,5
'''),

('', 1, 2, None, {}, (None,
r'''a and b and c'''), (None, r'''

# pre
x  # line
# post

'''), r'''
(a and
# pre
x  # line
# post
and c)
''',
r'''a and x and c''', r'''
BoolOp - ROOT 0,1..4,5
  .op And
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 2,0..2,1
   2] Name 'c' Load - 4,4..4,5
'''),

('', 2, 3, None, {}, (None,
r'''a and b and c'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(a and b and # pre
x  # line
# post
)
''',
r'''a and b and x''', r'''
BoolOp - ROOT 0,1..1,1
  .op And
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,7..0,8
   2] Name 'x' Load - 1,0..1,1
'''),

('', 0, 2, None, {}, (None,
r'''a and b and c'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(# pre
x  # line
# post
and c)
''',
r'''x and c''', r'''
BoolOp - ROOT 1,0..3,5
  .op And
  .values[2]
   0] Name 'x' Load - 1,0..1,1
   1] Name 'c' Load - 3,4..3,5
'''),

('', 1, 3, None, {}, (None,
r'''a and b and c'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(a and # pre
x  # line
# post
)
''',
r'''a and x''', r'''
BoolOp - ROOT 0,1..1,1
  .op And
  .values[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,0..1,1
'''),

('', 0, 3, None, {'_verify_self': False}, (None,
r'''a and b and c'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(# pre
x  # line
# post
)
''',
r'''x''', r'''
BoolOp - ROOT 1,0..1,1
  .op And
  .values[1]
   0] Name 'x' Load - 1,0..1,1
'''),

('', 0, 3, None, {'norm_self': True}, (None,
r'''a and b and c'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(# pre
x  # line
# post
)
''',
r'''x''',
r'''Name 'x' Load - ROOT 1,0..1,1'''),

('', 0, 1, None, {}, (None, r'''
a
and b
and c
'''), (None, r'''
x
and y
'''), r'''
(x
and y
and b
and c)
''', r'''
(x and y
and b
and c)
''', r'''
BoolOp - ROOT 0,1..3,5
  .op And
  .values[4]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,4..1,5
   2] Name 'b' Load - 2,4..2,5
   3] Name 'c' Load - 3,4..3,5
'''),

('', 1, 2, None, {}, (None, r'''
a
and b
and c
'''), (None, r'''
x
and y
'''), r'''
(a
and x
and y
and c)
''', r'''
(a
and x and y
and c)
''', r'''
BoolOp - ROOT 0,1..3,5
  .op And
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,4..1,5
   2] Name 'y' Load - 2,4..2,5
   3] Name 'c' Load - 3,4..3,5
'''),

('', 2, 3, None, {}, (None, r'''
a
and b
and c
'''), (None, r'''
x
and y
'''), r'''
(a
and b
and x
and y)
''', r'''
(a
and b
and x and y)
''', r'''
BoolOp - ROOT 0,1..3,5
  .op And
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,4..1,5
   2] Name 'x' Load - 2,4..2,5
   3] Name 'y' Load - 3,4..3,5
'''),

('', 0, 2, None, {}, (None, r'''
a
and b
and c
'''), (None, r'''
x
and y
'''), r'''
(x
and y
and c)
''', r'''
(x and y
and c)
''', r'''
BoolOp - ROOT 0,1..2,5
  .op And
  .values[3]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,4..1,5
   2] Name 'c' Load - 2,4..2,5
'''),

('', 1, 3, None, {}, (None, r'''
a
and b
and c
'''), (None, r'''
x
and y
'''), r'''
(a
and x
and y)
''', r'''
(a
and x and y)
''', r'''
BoolOp - ROOT 0,1..2,5
  .op And
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,4..1,5
   2] Name 'y' Load - 2,4..2,5
'''),

('', 0, 3, None, {}, (None, r'''
a
and b
and c
'''), (None, r'''
x
and y
'''), r'''
(x
and y)
''',
r'''x and y''', r'''
BoolOp - ROOT 0,1..1,5
  .op And
  .values[2]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,4..1,5
'''),

('', 0, 1, None, {}, (None, r'''
(a
and b
and c)
'''), (None, r'''
x
and y
'''), r'''
(x
 and y
and b
and c)
''', r'''
(x and y
and b
and c)
''', r'''
BoolOp - ROOT 0,1..3,5
  .op And
  .values[4]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,5..1,6
   2] Name 'b' Load - 2,4..2,5
   3] Name 'c' Load - 3,4..3,5
'''),

('', 1, 2, None, {}, (None, r'''
(a
and b
and c)
'''), (None, r'''
x
and y
'''), r'''
(a
and x
 and y
and c)
''', r'''
(a
and x and y
and c)
''', r'''
BoolOp - ROOT 0,1..3,5
  .op And
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,4..1,5
   2] Name 'y' Load - 2,5..2,6
   3] Name 'c' Load - 3,4..3,5
'''),

('', 2, 3, None, {}, (None, r'''
(a
and b
and c)
'''), (None, r'''
x
and y
'''), r'''
(a
and b
and x
 and y)
''', r'''
(a
and b
and x and y)
''', r'''
BoolOp - ROOT 0,1..3,6
  .op And
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,4..1,5
   2] Name 'x' Load - 2,4..2,5
   3] Name 'y' Load - 3,5..3,6
'''),

('', 0, 2, None, {}, (None, r'''
(a
and b
and c)
'''), (None, r'''
x
and y
'''), r'''
(x
 and y
and c)
''', r'''
(x and y
and c)
''', r'''
BoolOp - ROOT 0,1..2,5
  .op And
  .values[3]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,5..1,6
   2] Name 'c' Load - 2,4..2,5
'''),

('', 1, 3, None, {}, (None, r'''
(a
and b
and c)
'''), (None, r'''
x
and y
'''), r'''
(a
and x
 and y)
''', r'''
(a
and x and y)
''', r'''
BoolOp - ROOT 0,1..2,6
  .op And
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,4..1,5
   2] Name 'y' Load - 2,5..2,6
'''),

('', 0, 3, None, {}, (None, r'''
(a
and b
and c)
'''), (None, r'''
x
and y
'''), r'''
(x
 and y)
''',
r'''(x and y)''', r'''
BoolOp - ROOT 0,1..1,6
  .op And
  .values[2]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,5..1,6
'''),

('', 0, 1, None, {}, (None, r'''
a \
and \
b \
and \
c
'''), (None, r'''
x \
and \
y
'''), r'''
(x \
and \
y
and \
b \
and \
c)
''', r'''
(x and y
and \
b \
and \
c)
''', r'''
BoolOp - ROOT 0,1..6,1
  .op And
  .values[4]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 2,0..2,1
   2] Name 'b' Load - 4,0..4,1
   3] Name 'c' Load - 6,0..6,1
'''),

('', 1, 2, None, {}, (None, r'''
a \
and \
b \
and \
c
'''), (None, r'''
x \
and \
y
'''), r'''
(a \
and \
x \
and \
y
and \
c)
''', r'''
(a \
and \
x and y
and \
c)
''', r'''
BoolOp - ROOT 0,1..6,1
  .op And
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 2,0..2,1
   2] Name 'y' Load - 4,0..4,1
   3] Name 'c' Load - 6,0..6,1
'''),

('', 2, 3, None, {}, (None, r'''
a \
and \
b \
and \
c
'''), (None, r'''
x \
and \
y
'''), r'''
a \
and \
b \
and \
x \
and \
y
''', r'''
a \
and \
b \
and \
x and y
''', r'''
BoolOp - ROOT 0,0..6,1
  .op And
  .values[4]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 2,0..2,1
   2] Name 'x' Load - 4,0..4,1
   3] Name 'y' Load - 6,0..6,1
'''),

('', 0, 2, None, {}, (None, r'''
a \
and \
b \
and \
c
'''), (None, r'''
x \
and \
y
'''), r'''
(x \
and \
y
and \
c)
''', r'''
(x and y
and \
c)
''', r'''
BoolOp - ROOT 0,1..4,1
  .op And
  .values[3]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 2,0..2,1
   2] Name 'c' Load - 4,0..4,1
'''),

('', 1, 3, None, {}, (None, r'''
a \
and \
b \
and \
c
'''), (None, r'''
x \
and \
y
'''), r'''
a \
and \
x \
and \
y
''', r'''
a \
and \
x and y
''', r'''
BoolOp - ROOT 0,0..4,1
  .op And
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 2,0..2,1
   2] Name 'y' Load - 4,0..4,1
'''),

('', 0, 3, None, {}, (None, r'''
a \
and \
b \
and \
c
'''), (None, r'''
x \
and \
y
'''), r'''
x \
and \
y
''',
r'''x and y''', r'''
BoolOp - ROOT 0,0..2,1
  .op And
  .values[2]
   0] Name 'x' Load - 0,0..0,1
   1] Name 'y' Load - 2,0..2,1
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''x or y'''),
r'''a or (x or y) or c''', r'''
BoolOp - ROOT 0,0..0,18
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] BoolOp - 0,6..0,12
     .op Or
     .values[2]
      0] Name 'x' Load - 0,6..0,7
      1] Name 'y' Load - 0,11..0,12
   2] Name 'c' Load - 0,17..0,18
'''),

('', 1, 2, None, {'coerce': False}, (None,
r'''a or b or c'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to BoolOp without 'one=True' or 'coerce=True'")**'''),

('', 1, 2, None, {'coerce': False, 'one': True}, (None,
r'''a or b or c'''), (None,
r'''x'''),
r'''a or x or c''', r'''
BoolOp - ROOT 0,0..0,11
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 0,5..0,6
   2] Name 'c' Load - 0,10..0,11
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''x'''),
r'''a or x or c''', r'''
BoolOp - ROOT 0,0..0,11
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'x' Load - 0,5..0,6
   2] Name 'c' Load - 0,10..0,11
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''x := y'''),
r'''a or (x := y) or c''', r'''
BoolOp - ROOT 0,0..0,18
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] NamedExpr - 0,6..0,12
     .target Name 'x' Store - 0,6..0,7
     .value Name 'y' Load - 0,11..0,12
   2] Name 'c' Load - 0,17..0,18
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''yield'''),
r'''a or (yield) or c''', r'''
BoolOp - ROOT 0,0..0,17
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Yield - 0,6..0,11
   2] Name 'c' Load - 0,16..0,17
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''yield x'''),
r'''a or (yield x) or c''', r'''
BoolOp - ROOT 0,0..0,19
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] Yield - 0,6..0,13
     .value Name 'x' Load - 0,12..0,13
   2] Name 'c' Load - 0,18..0,19
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''yield from x'''),
r'''a or (yield from x) or c''', r'''
BoolOp - ROOT 0,0..0,24
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] YieldFrom - 0,6..0,18
     .value Name 'x' Load - 0,17..0,18
   2] Name 'c' Load - 0,23..0,24
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''x if y else z'''),
r'''a or (x if y else z) or c''', r'''
BoolOp - ROOT 0,0..0,25
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] IfExp - 0,6..0,19
     .test Name 'y' Load - 0,11..0,12
     .body Name 'x' Load - 0,6..0,7
     .orelse Name 'z' Load - 0,18..0,19
   2] Name 'c' Load - 0,24..0,25
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''x and y'''),
r'''a or x and y or c''', r'''
BoolOp - ROOT 0,0..0,17
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] BoolOp - 0,5..0,12
     .op And
     .values[2]
      0] Name 'x' Load - 0,5..0,6
      1] Name 'y' Load - 0,11..0,12
   2] Name 'c' Load - 0,16..0,17
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a and b and c'''), (None,
r'''x or y'''),
r'''a and (x or y) and c''', r'''
BoolOp - ROOT 0,0..0,20
  .op And
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] BoolOp - 0,7..0,13
     .op Or
     .values[2]
      0] Name 'x' Load - 0,7..0,8
      1] Name 'y' Load - 0,12..0,13
   2] Name 'c' Load - 0,19..0,20
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''not x'''),
r'''a or not x or c''', r'''
BoolOp - ROOT 0,0..0,15
  .op Or
  .values[3]
   0] Name 'a' Load - 0,0..0,1
   1] UnaryOp - 0,5..0,10
     .op Not - 0,5..0,8
     .operand Name 'x' Load - 0,9..0,10
   2] Name 'c' Load - 0,14..0,15
'''),

('body[0].value', 0, 1, None, {'trivia': ('block+1', 'none')}, (None, r'''
if 1:
  7 \
and \
None
'''), (None, r'''

 None \

'''), r'''
if 1:
  (
   None \
 \
and \
None)
''', r'''
if 1:
  None \
and \
None
''', r'''
If - ROOT 0,0..5,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Expr - 1,2..5,5
     .value BoolOp - 2,3..5,4
       .op And
       .values[2]
        0] Constant None - 2,3..2,7
        1] Constant None - 5,0..5,4
'''),

('body[0].value', 0, 1, None, {'trivia': ('block+1', 'none')}, (None, r'''
if 1:
  7 \
and \
None
'''), (None, r'''
  None \

'''), r'''
if 1:
  None \
 \
and \
None
''', r'''
if 1:
  None \
and \
None
''', r'''
If - ROOT 0,0..4,4
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Expr - 1,2..4,4
     .value BoolOp - 1,2..4,4
       .op And
       .values[2]
        0] Constant None - 1,2..1,6
        1] Constant None - 4,0..4,4
'''),

('', 1, 2, None, {'op_side': 'left'}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''**DEL**'''), r'''
a
or # right
c
''', r'''
BoolOp - ROOT 0,0..2,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 2,0..2,1
'''),

('', 1, 2, None, {'op_side': 'right'}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''**DEL**'''), r'''
a
or # left
c
''', r'''
BoolOp - ROOT 0,0..2,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''and x'''),
r'''**ParseError('dangling BoolOp operator does not match')**'''),

('', 1, 2, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''x and'''),
r'''**ParseError('dangling BoolOp operator does not match')**'''),

('', 0, 1, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''or x'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 2, 3, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''x or'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 1, 2, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''or x'''), r'''
(a
or x
or # right
c)
''',
r'''**SyntaxError("unexpected code after boolop, 'x'")**''', r'''
BoolOp - ROOT 0,1..3,1
  .op Or
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,3..1,4
   2] Name 'c' Load - 3,0..3,1
'''),

('', 1, 2, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''x or'''), r'''
(a
or # left
x or
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
BoolOp - ROOT 0,1..3,1
  .op Or
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 2,0..2,1
   2] Name 'c' Load - 3,0..3,1
'''),

('', 1, 1, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''or x'''), r'''
(a
or x or # left
b
or # right
c)
''',
r'''**SyntaxError("unexpected code after boolop, 'x'")**''', r'''
BoolOp - ROOT 0,1..4,1
  .op Or
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,3..1,4
   2] Name 'b' Load - 2,0..2,1
   3] Name 'c' Load - 4,0..4,1
'''),

('', 1, 1, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''x or'''), r'''
(a
or # left
x or b
or # right
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
BoolOp - ROOT 0,1..4,1
  .op Or
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 2,0..2,1
   2] Name 'b' Load - 2,5..2,6
   3] Name 'c' Load - 4,0..4,1
'''),

('', 1, 1, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None, r'''

or # dangling
x

'''), r'''
(a
or # dangling
x
or # left
b
or # right
c)
''',
r'''**SyntaxError("unexpected code after boolop, 'x'")**''', r'''
BoolOp - ROOT 0,1..6,1
  .op Or
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 2,0..2,1
   2] Name 'b' Load - 4,0..4,1
   3] Name 'c' Load - 6,0..6,1
'''),

('', 1, 1, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None, r'''

x
or # dangling

'''), r'''
(a
or # left
x
or # dangling
b
or # right
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
BoolOp - ROOT 0,1..6,1
  .op Or
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 2,0..2,1
   2] Name 'b' Load - 4,0..4,1
   3] Name 'c' Load - 6,0..6,1
'''),

('', 3, 3, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None, r'''

or # dangling
x

'''), r'''
(a
or # left
b
or # right
c
or # dangling
x
)
''',
r'''**SyntaxError("unexpected code after boolop, 'x'")**''', r'''
BoolOp - ROOT 0,1..6,1
  .op Or
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 2,0..2,1
   2] Name 'c' Load - 4,0..4,1
   3] Name 'x' Load - 6,0..6,1
'''),

('', 0, 0, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None, r'''

x
or # dangling

'''), r'''
(x
or # dangling
a
or # left
b
or # right
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
BoolOp - ROOT 0,1..6,1
  .op Or
  .values[4]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'a' Load - 2,0..2,1
   2] Name 'b' Load - 4,0..4,1
   3] Name 'c' Load - 6,0..6,1
'''),

('', 3, 3, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''x'''), r'''
(a
or # left
b
or # right
c or x)
''', r'''
BoolOp - ROOT 0,1..4,6
  .op Or
  .values[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 2,0..2,1
   2] Name 'c' Load - 4,0..4,1
   3] Name 'x' Load - 4,5..4,6
'''),

('', 0, 0, None, {}, (None, r'''
a
or # left
b
or # right
c
'''), (None,
r'''x'''), r'''
(x or a
or # left
b
or # right
c)
''', r'''
BoolOp - ROOT 0,1..4,1
  .op Or
  .values[4]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'a' Load - 0,6..0,7
   2] Name 'b' Load - 2,0..2,1
   3] Name 'c' Load - 4,0..4,1
'''),

('body[0].value', 1, 2, None, {}, (None, r'''
if 1:
    a = (a
         and b
         and c
    )
'''), (None, r'''

and d
and e

'''), r'''
if 1:
    a = (a
         and d
         and e
         and c
    )
''',
r'''**SyntaxError("unexpected code after boolop, 'd'")**''', r'''
If - ROOT 0,0..5,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..5,5
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value BoolOp - 1,9..4,14
       .op And
       .values[4]
        0] Name 'a' Load - 1,9..1,10
        1] Name 'd' Load - 2,13..2,14
        2] Name 'e' Load - 3,13..3,14
        3] Name 'c' Load - 4,13..4,14
'''),

('body[0].value', 1, 2, None, {}, (None, r'''
if 1:
    a = (a
         and b
         and c
    )
'''), (None, r'''

d and
e and

'''), r'''
if 1:
    a = (a
         and
         d and
         e and
         c
    )
''',
r'''**ParseError('invalid syntax')**''', r'''
If - ROOT 0,0..6,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..6,5
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value BoolOp - 1,9..5,10
       .op And
       .values[4]
        0] Name 'a' Load - 1,9..1,10
        1] Name 'd' Load - 3,9..3,10
        2] Name 'e' Load - 4,9..4,10
        3] Name 'c' Load - 5,9..5,10
'''),

('body[0].value', 1, 2, None, {}, (None, r'''
if 1:
    a = (a and
         b and
         c
    )
'''), (None, r'''

and d
and e

'''), r'''
if 1:
    a = (a
         and d
         and e
         and
         c
    )
''',
r'''**SyntaxError("unexpected code after boolop, 'd'")**''', r'''
If - ROOT 0,0..6,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..6,5
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value BoolOp - 1,9..5,10
       .op And
       .values[4]
        0] Name 'a' Load - 1,9..1,10
        1] Name 'd' Load - 2,13..2,14
        2] Name 'e' Load - 3,13..3,14
        3] Name 'c' Load - 5,9..5,10
'''),

('body[0].value', 1, 2, None, {}, (None, r'''
if 1:
    a = (a and
         b and
         c
    )
'''), (None, r'''

d and
e and

'''), r'''
if 1:
    a = (a and
         d and
         e and
         c
    )
''',
r'''**ParseError('invalid syntax')**''', r'''
If - ROOT 0,0..5,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..5,5
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value BoolOp - 1,9..4,10
       .op And
       .values[4]
        0] Name 'a' Load - 1,9..1,10
        1] Name 'd' Load - 2,9..2,10
        2] Name 'e' Load - 3,9..3,10
        3] Name 'c' Load - 4,9..4,10
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a or b or c'''), (None,
r'''x or'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 1, 2, None, {}, (None,
r'''a or b or c'''), (None,
r'''**DEL**'''),
r'''a or c''', r'''
BoolOp - ROOT 0,0..0,6
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 0,5..0,6
'''),
],

'Compare__all': [  # ................................................................................

('', 0, 1, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''x is not (b) not in (c)''', r'''
Compare - ROOT 0,0..0,23
  .left Name 'x' Load - 0,0..0,1
  .ops[2]
   0] IsNot - 0,2..0,8
   1] NotIn - 0,13..0,19
  .comparators[2]
   0] Name 'b' Load - 0,10..0,11
   1] Name 'c' Load - 0,21..0,22
'''),

('', 1, 2, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''(a) is not x not in (c)''', r'''
Compare - ROOT 0,0..0,23
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,13..0,19
  .comparators[2]
   0] Name 'x' Load - 0,11..0,12
   1] Name 'c' Load - 0,21..0,22
'''),

('', 2, 3, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''(a) is not (b) not in x''', r'''
Compare - ROOT 0,0..0,23
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,15..0,21
  .comparators[2]
   0] Name 'b' Load - 0,12..0,13
   1] Name 'x' Load - 0,22..0,23
'''),

('', 0, 2, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''x not in (c)''', r'''
Compare - ROOT 0,0..0,12
  .left Name 'x' Load - 0,0..0,1
  .ops[1]
   0] NotIn - 0,2..0,8
  .comparators[1]
   0] Name 'c' Load - 0,10..0,11
'''),

('', 1, 3, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''(a) is not x''', r'''
Compare - ROOT 0,0..0,12
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] IsNot - 0,4..0,10
  .comparators[1]
   0] Name 'x' Load - 0,11..0,12
'''),

('', 0, 3, None, {'_verify_self': False}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''x''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'x' Load - 0,0..0,1
'''),

('', 0, 3, None, {'norm_self': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''x''',
r'''Name 'x' Load - ROOT 0,0..0,1'''),

('', 0, 1, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''( x )'''),
r'''( x ) is not (b) not in (c)''',
r'''x is not (b) not in (c)''', r'''
Compare - ROOT 0,0..0,27
  .left Name 'x' Load - 0,2..0,3
  .ops[2]
   0] IsNot - 0,6..0,12
   1] NotIn - 0,17..0,23
  .comparators[2]
   0] Name 'b' Load - 0,14..0,15
   1] Name 'c' Load - 0,25..0,26
'''),

('', 1, 2, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''( x )'''),
r'''(a) is not ( x ) not in (c)''',
r'''(a) is not x not in (c)''', r'''
Compare - ROOT 0,0..0,27
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,17..0,23
  .comparators[2]
   0] Name 'x' Load - 0,13..0,14
   1] Name 'c' Load - 0,25..0,26
'''),

('', 2, 3, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''( x )'''),
r'''(a) is not (b) not in ( x )''',
r'''(a) is not (b) not in x''', r'''
Compare - ROOT 0,0..0,27
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,15..0,21
  .comparators[2]
   0] Name 'b' Load - 0,12..0,13
   1] Name 'x' Load - 0,24..0,25
'''),

('', 0, 2, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''( x )'''),
r'''( x ) not in (c)''',
r'''x not in (c)''', r'''
Compare - ROOT 0,0..0,16
  .left Name 'x' Load - 0,2..0,3
  .ops[1]
   0] NotIn - 0,6..0,12
  .comparators[1]
   0] Name 'c' Load - 0,14..0,15
'''),

('', 1, 3, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''( x )'''),
r'''(a) is not ( x )''',
r'''(a) is not x''', r'''
Compare - ROOT 0,0..0,16
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] IsNot - 0,4..0,10
  .comparators[1]
   0] Name 'x' Load - 0,13..0,14
'''),

('', 0, 3, None, {'_verify_self': False}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''( x )'''),
r'''( x )''',
r'''x''', r'''
Compare - ROOT 0,0..0,5
  .left Name 'x' Load - 0,2..0,3
'''),

('', 0, 3, None, {'norm_self': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''( x )'''),
r'''( x )''',
r'''x''',
r'''Name 'x' Load - ROOT 0,2..0,3'''),

('', 0, 1, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(# pre
x  # line
# post
is not (b) not in (c))
''',
r'''x is not (b) not in (c)''', r'''
Compare - ROOT 1,0..3,21
  .left Name 'x' Load - 1,0..1,1
  .ops[2]
   0] IsNot - 3,0..3,6
   1] NotIn - 3,11..3,17
  .comparators[2]
   0] Name 'b' Load - 3,8..3,9
   1] Name 'c' Load - 3,19..3,20
'''),

('', 0, 1, None, {'pars': False}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''
# pre
x  # line
# post
'''), r'''
# pre
x  # line
# post
is not (b) not in (c)
''',
r'''x is not (b) not in (c)''', r'''
Compare - ROOT 1,0..3,21
  .left Name 'x' Load - 1,0..1,1
  .ops[2]
   0] IsNot - 3,0..3,6
   1] NotIn - 3,11..3,17
  .comparators[2]
   0] Name 'b' Load - 3,8..3,9
   1] Name 'c' Load - 3,19..3,20
'''),

('', 1, 2, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''
# pre
x  # line
# post
'''), r'''
((a) is not # pre
x  # line
# post
not in (c))
''',
r'''(a) is not x not in (c)''', r'''
Compare - ROOT 0,1..3,10
  .left Name 'a' Load - 0,2..0,3
  .ops[2]
   0] IsNot - 0,5..0,11
   1] NotIn - 3,0..3,6
  .comparators[2]
   0] Name 'x' Load - 1,0..1,1
   1] Name 'c' Load - 3,8..3,9
'''),

('', 1, 2, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''

# pre
x  # line
# post

'''), r'''
((a) is not
# pre
x  # line
# post
not in (c))
''',
r'''(a) is not x not in (c)''', r'''
Compare - ROOT 0,1..4,10
  .left Name 'a' Load - 0,2..0,3
  .ops[2]
   0] IsNot - 0,5..0,11
   1] NotIn - 4,0..4,6
  .comparators[2]
   0] Name 'x' Load - 2,0..2,1
   1] Name 'c' Load - 4,8..4,9
'''),

('', 2, 3, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''
# pre
x  # line
# post
'''), r'''
((a) is not (b) not in # pre
x  # line
# post
)
''',
r'''(a) is not (b) not in x''', r'''
Compare - ROOT 0,1..1,1
  .left Name 'a' Load - 0,2..0,3
  .ops[2]
   0] IsNot - 0,5..0,11
   1] NotIn - 0,16..0,22
  .comparators[2]
   0] Name 'b' Load - 0,13..0,14
   1] Name 'x' Load - 1,0..1,1
'''),

('', 0, 2, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(# pre
x  # line
# post
not in (c))
''',
r'''x not in (c)''', r'''
Compare - ROOT 1,0..3,10
  .left Name 'x' Load - 1,0..1,1
  .ops[1]
   0] NotIn - 3,0..3,6
  .comparators[1]
   0] Name 'c' Load - 3,8..3,9
'''),

('', 1, 3, None, {}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''
# pre
x  # line
# post
'''), r'''
((a) is not # pre
x  # line
# post
)
''',
r'''(a) is not x''', r'''
Compare - ROOT 0,1..1,1
  .left Name 'a' Load - 0,2..0,3
  .ops[1]
   0] IsNot - 0,5..0,11
  .comparators[1]
   0] Name 'x' Load - 1,0..1,1
'''),

('', 0, 3, None, {'_verify_self': False}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(# pre
x  # line
# post
)
''',
r'''x''', r'''
Compare - ROOT 1,0..1,1
  .left Name 'x' Load - 1,0..1,1
'''),

('', 0, 3, None, {'norm_self': True}, (None,
r'''(a) is not (b) not in (c)'''), (None, r'''
# pre
x  # line
# post
'''), r'''
(# pre
x  # line
# post
)
''',
r'''x''',
r'''Name 'x' Load - ROOT 1,0..1,1'''),

('', 0, 1, None, {}, (None, r'''
(a)
< (b)
< (c)
'''), (None, r'''
(x)
> (y)
'''), r'''
((x)
> (y)
< (b)
< (c))
''', r'''
(x > y
< (b)
< (c))
''', r'''
Compare - ROOT 0,1..3,5
  .left Name 'x' Load - 0,2..0,3
  .ops[3]
   0] Gt - 1,0..1,1
   1] Lt - 2,0..2,1
   2] Lt - 3,0..3,1
  .comparators[3]
   0] Name 'y' Load - 1,3..1,4
   1] Name 'b' Load - 2,3..2,4
   2] Name 'c' Load - 3,3..3,4
'''),

('', 1, 2, None, {}, (None, r'''
(a)
< (b)
< (c)
'''), (None, r'''
(x)
> (y)
'''), r'''
((a)
< (x)
> (y)
< (c))
''', r'''
((a)
< x > y
< (c))
''', r'''
Compare - ROOT 0,1..3,5
  .left Name 'a' Load - 0,2..0,3
  .ops[3]
   0] Lt - 1,0..1,1
   1] Gt - 2,0..2,1
   2] Lt - 3,0..3,1
  .comparators[3]
   0] Name 'x' Load - 1,3..1,4
   1] Name 'y' Load - 2,3..2,4
   2] Name 'c' Load - 3,3..3,4
'''),

('', 2, 3, None, {}, (None, r'''
(a)
< (b)
< (c)
'''), (None, r'''
(x)
> (y)
'''), r'''
((a)
< (b)
< (x)
> (y))
''', r'''
((a)
< (b)
< x > y)
''', r'''
Compare - ROOT 0,1..3,5
  .left Name 'a' Load - 0,2..0,3
  .ops[3]
   0] Lt - 1,0..1,1
   1] Lt - 2,0..2,1
   2] Gt - 3,0..3,1
  .comparators[3]
   0] Name 'b' Load - 1,3..1,4
   1] Name 'x' Load - 2,3..2,4
   2] Name 'y' Load - 3,3..3,4
'''),

('', 0, 2, None, {}, (None, r'''
(a)
< (b)
< (c)
'''), (None, r'''
(x)
> (y)
'''), r'''
((x)
> (y)
< (c))
''', r'''
(x > y
< (c))
''', r'''
Compare - ROOT 0,1..2,5
  .left Name 'x' Load - 0,2..0,3
  .ops[2]
   0] Gt - 1,0..1,1
   1] Lt - 2,0..2,1
  .comparators[2]
   0] Name 'y' Load - 1,3..1,4
   1] Name 'c' Load - 2,3..2,4
'''),

('', 1, 3, None, {}, (None, r'''
(a)
< (b)
< (c)
'''), (None, r'''
(x)
> (y)
'''), r'''
((a)
< (x)
> (y))
''', r'''
((a)
< x > y)
''', r'''
Compare - ROOT 0,1..2,5
  .left Name 'a' Load - 0,2..0,3
  .ops[2]
   0] Lt - 1,0..1,1
   1] Gt - 2,0..2,1
  .comparators[2]
   0] Name 'x' Load - 1,3..1,4
   1] Name 'y' Load - 2,3..2,4
'''),

('', 0, 3, None, {}, (None, r'''
(a)
< (b)
< (c)
'''), (None, r'''
(x)
> (y)
'''), r'''
((x)
> (y))
''',
r'''x > y''', r'''
Compare - ROOT 0,1..1,5
  .left Name 'x' Load - 0,2..0,3
  .ops[1]
   0] Gt - 1,0..1,1
  .comparators[1]
   0] Name 'y' Load - 1,3..1,4
'''),

('', 0, 1, None, {}, (None, r'''
((a)
< (b)
< (c))
'''), (None, r'''
(x)
> (y)
'''), r'''
((x)
 > (y)
< (b)
< (c))
''', r'''
(x > y
< (b)
< (c))
''', r'''
Compare - ROOT 0,1..3,5
  .left Name 'x' Load - 0,2..0,3
  .ops[3]
   0] Gt - 1,1..1,2
   1] Lt - 2,0..2,1
   2] Lt - 3,0..3,1
  .comparators[3]
   0] Name 'y' Load - 1,4..1,5
   1] Name 'b' Load - 2,3..2,4
   2] Name 'c' Load - 3,3..3,4
'''),

('', 1, 2, None, {}, (None, r'''
((a)
< (b)
< (c))
'''), (None, r'''
(x)
> (y)
'''), r'''
((a)
< (x)
 > (y)
< (c))
''', r'''
((a)
< x > y
< (c))
''', r'''
Compare - ROOT 0,1..3,5
  .left Name 'a' Load - 0,2..0,3
  .ops[3]
   0] Lt - 1,0..1,1
   1] Gt - 2,1..2,2
   2] Lt - 3,0..3,1
  .comparators[3]
   0] Name 'x' Load - 1,3..1,4
   1] Name 'y' Load - 2,4..2,5
   2] Name 'c' Load - 3,3..3,4
'''),

('', 2, 3, None, {}, (None, r'''
((a)
< (b)
< (c))
'''), (None, r'''
(x)
> (y)
'''), r'''
((a)
< (b)
< (x)
 > (y))
''', r'''
((a)
< (b)
< x > y)
''', r'''
Compare - ROOT 0,1..3,6
  .left Name 'a' Load - 0,2..0,3
  .ops[3]
   0] Lt - 1,0..1,1
   1] Lt - 2,0..2,1
   2] Gt - 3,1..3,2
  .comparators[3]
   0] Name 'b' Load - 1,3..1,4
   1] Name 'x' Load - 2,3..2,4
   2] Name 'y' Load - 3,4..3,5
'''),

('', 0, 2, None, {}, (None, r'''
((a)
< (b)
< (c))
'''), (None, r'''
(x)
> (y)
'''), r'''
((x)
 > (y)
< (c))
''', r'''
(x > y
< (c))
''', r'''
Compare - ROOT 0,1..2,5
  .left Name 'x' Load - 0,2..0,3
  .ops[2]
   0] Gt - 1,1..1,2
   1] Lt - 2,0..2,1
  .comparators[2]
   0] Name 'y' Load - 1,4..1,5
   1] Name 'c' Load - 2,3..2,4
'''),

('', 1, 3, None, {}, (None, r'''
((a)
< (b)
< (c))
'''), (None, r'''
(x)
> (y)
'''), r'''
((a)
< (x)
 > (y))
''', r'''
((a)
< x > y)
''', r'''
Compare - ROOT 0,1..2,6
  .left Name 'a' Load - 0,2..0,3
  .ops[2]
   0] Lt - 1,0..1,1
   1] Gt - 2,1..2,2
  .comparators[2]
   0] Name 'x' Load - 1,3..1,4
   1] Name 'y' Load - 2,4..2,5
'''),

('', 0, 3, None, {}, (None, r'''
((a)
< (b)
< (c))
'''), (None, r'''
(x)
> (y)
'''), r'''
((x)
 > (y))
''',
r'''(x > y)''', r'''
Compare - ROOT 0,1..1,6
  .left Name 'x' Load - 0,2..0,3
  .ops[1]
   0] Gt - 1,1..1,2
  .comparators[1]
   0] Name 'y' Load - 1,4..1,5
'''),

('', 0, 1, None, {}, (None, r'''
a \
is \
not \
b \
not \
in \
c
'''), (None, r'''
x \
> \
y
'''), r'''
(x \
> \
y
is \
not \
b \
not \
in \
c)
''', r'''
(x > y
is \
not \
b \
not \
in \
c)
''', r'''
Compare - ROOT 0,1..8,1
  .left Name 'x' Load - 0,1..0,2
  .ops[3]
   0] Gt - 1,0..1,1
   1] IsNot - 3,0..4,3
   2] NotIn - 6,0..7,2
  .comparators[3]
   0] Name 'y' Load - 2,0..2,1
   1] Name 'b' Load - 5,0..5,1
   2] Name 'c' Load - 8,0..8,1
'''),

('', 1, 2, None, {}, (None, r'''
a \
is \
not \
b \
not \
in \
c
'''), (None, r'''
x \
> \
y
'''), r'''
(a \
is \
not \
x \
> \
y
not \
in \
c)
''', r'''
(a \
is \
not \
x > y
not \
in \
c)
''', r'''
Compare - ROOT 0,1..8,1
  .left Name 'a' Load - 0,1..0,2
  .ops[3]
   0] IsNot - 1,0..2,3
   1] Gt - 4,0..4,1
   2] NotIn - 6,0..7,2
  .comparators[3]
   0] Name 'x' Load - 3,0..3,1
   1] Name 'y' Load - 5,0..5,1
   2] Name 'c' Load - 8,0..8,1
'''),

('', 2, 3, None, {}, (None, r'''
a \
is \
not \
b \
not \
in \
c
'''), (None, r'''
x \
> \
y
'''), r'''
a \
is \
not \
b \
not \
in \
x \
> \
y
''', r'''
a \
is \
not \
b \
not \
in \
x > y
''', r'''
Compare - ROOT 0,0..8,1
  .left Name 'a' Load - 0,0..0,1
  .ops[3]
   0] IsNot - 1,0..2,3
   1] NotIn - 4,0..5,2
   2] Gt - 7,0..7,1
  .comparators[3]
   0] Name 'b' Load - 3,0..3,1
   1] Name 'x' Load - 6,0..6,1
   2] Name 'y' Load - 8,0..8,1
'''),

('', 0, 2, None, {}, (None, r'''
a \
is \
not \
b \
not \
in \
c
'''), (None, r'''
x \
> \
y
'''), r'''
(x \
> \
y
not \
in \
c)
''', r'''
(x > y
not \
in \
c)
''', r'''
Compare - ROOT 0,1..5,1
  .left Name 'x' Load - 0,1..0,2
  .ops[2]
   0] Gt - 1,0..1,1
   1] NotIn - 3,0..4,2
  .comparators[2]
   0] Name 'y' Load - 2,0..2,1
   1] Name 'c' Load - 5,0..5,1
'''),

('', 1, 3, None, {}, (None, r'''
a \
is \
not \
b \
not \
in \
c
'''), (None, r'''
x \
> \
y
'''), r'''
a \
is \
not \
x \
> \
y
''', r'''
a \
is \
not \
x > y
''', r'''
Compare - ROOT 0,0..5,1
  .left Name 'a' Load - 0,0..0,1
  .ops[2]
   0] IsNot - 1,0..2,3
   1] Gt - 4,0..4,1
  .comparators[2]
   0] Name 'x' Load - 3,0..3,1
   1] Name 'y' Load - 5,0..5,1
'''),

('', 0, 3, None, {}, (None, r'''
a \
is \
not \
b \
not \
in \
c
'''), (None, r'''
x \
> \
y
'''), r'''
x \
> \
y
''',
r'''x > y''', r'''
Compare - ROOT 0,0..2,1
  .left Name 'x' Load - 0,0..0,1
  .ops[1]
   0] Gt - 1,0..1,1
  .comparators[1]
   0] Name 'y' Load - 2,0..2,1
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x < y'''),
r'''(a) is not (x < y) not in (c)''', r'''
Compare - ROOT 0,0..0,29
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,19..0,25
  .comparators[2]
   0] Compare - 0,12..0,17
     .left Name 'x' Load - 0,12..0,13
     .ops[1]
      0] Lt - 0,14..0,15
     .comparators[1]
      0] Name 'y' Load - 0,16..0,17
   1] Name 'c' Load - 0,27..0,28
'''),

('', 1, 2, None, {'coerce': False}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''**ValueError("cannot put Name as slice to Compare without 'one=True' or 'coerce=True'")**'''),

('', 1, 2, None, {'coerce': False, 'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''(a) is not x not in (c)''', r'''
Compare - ROOT 0,0..0,23
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,13..0,19
  .comparators[2]
   0] Name 'x' Load - 0,11..0,12
   1] Name 'c' Load - 0,21..0,22
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x'''),
r'''(a) is not x not in (c)''', r'''
Compare - ROOT 0,0..0,23
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,13..0,19
  .comparators[2]
   0] Name 'x' Load - 0,11..0,12
   1] Name 'c' Load - 0,21..0,22
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x := y'''),
r'''(a) is not (x := y) not in (c)''', r'''
Compare - ROOT 0,0..0,30
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,20..0,26
  .comparators[2]
   0] NamedExpr - 0,12..0,18
     .target Name 'x' Store - 0,12..0,13
     .value Name 'y' Load - 0,17..0,18
   1] Name 'c' Load - 0,28..0,29
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''yield'''),
r'''(a) is not (yield) not in (c)''', r'''
Compare - ROOT 0,0..0,29
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,19..0,25
  .comparators[2]
   0] Yield - 0,12..0,17
   1] Name 'c' Load - 0,27..0,28
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''yield x'''),
r'''(a) is not (yield x) not in (c)''', r'''
Compare - ROOT 0,0..0,31
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,21..0,27
  .comparators[2]
   0] Yield - 0,12..0,19
     .value Name 'x' Load - 0,18..0,19
   1] Name 'c' Load - 0,29..0,30
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''yield from x'''),
r'''(a) is not (yield from x) not in (c)''', r'''
Compare - ROOT 0,0..0,36
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,26..0,32
  .comparators[2]
   0] YieldFrom - 0,12..0,24
     .value Name 'x' Load - 0,23..0,24
   1] Name 'c' Load - 0,34..0,35
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x if y else z'''),
r'''(a) is not (x if y else z) not in (c)''', r'''
Compare - ROOT 0,0..0,37
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,27..0,33
  .comparators[2]
   0] IfExp - 0,12..0,25
     .test Name 'y' Load - 0,17..0,18
     .body Name 'x' Load - 0,12..0,13
     .orelse Name 'z' Load - 0,24..0,25
   1] Name 'c' Load - 0,35..0,36
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''x and y'''),
r'''(a) is not (x and y) not in (c)''', r'''
Compare - ROOT 0,0..0,31
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,21..0,27
  .comparators[2]
   0] BoolOp - 0,12..0,19
     .op And
     .values[2]
      0] Name 'x' Load - 0,12..0,13
      1] Name 'y' Load - 0,18..0,19
   1] Name 'c' Load - 0,29..0,30
'''),

('', 1, 2, None, {'one': True}, (None,
r'''(a) is not (b) not in (c)'''), (None,
r'''not x'''),
r'''(a) is not (not x) not in (c)''', r'''
Compare - ROOT 0,0..0,29
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,19..0,25
  .comparators[2]
   0] UnaryOp - 0,12..0,17
     .op Not - 0,12..0,15
     .operand Name 'x' Load - 0,16..0,17
   1] Name 'c' Load - 0,27..0,28
'''),

('body[0].value', 0, 1, None, {'trivia': ('block+1', 'none')}, (None, r'''
if 1:
  7 \
not in \
None
'''), (None, r'''

 None \

'''), r'''
if 1:
  (
   None \
 \
not in \
None)
''', r'''
if 1:
  None \
not in \
None
''', r'''
If - ROOT 0,0..5,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Expr - 1,2..5,5
     .value Compare - 2,3..5,4
       .left Constant None - 2,3..2,7
       .ops[1]
        0] NotIn - 4,0..4,6
       .comparators[1]
        0] Constant None - 5,0..5,4
'''),

('', 1, 2, None, {'op_side': 'left'}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''**DEL**'''), r'''
a
> # right
c
''', r'''
Compare - ROOT 0,0..2,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Gt - 1,0..1,1
  .comparators[1]
   0] Name 'c' Load - 2,0..2,1
'''),

('', 1, 2, None, {'op_side': 'right'}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''**DEL**'''), r'''
a
< # left
c
''', r'''
Compare - ROOT 0,0..2,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 1,0..1,1
  .comparators[1]
   0] Name 'c' Load - 2,0..2,1
'''),

('', 1, 2, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''!= x'''), r'''
(a
!= x
> # right
c)
''',
r'''**SyntaxError("unexpected code after cmpop, 'x'")**''', r'''
Compare - ROOT 0,1..3,1
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] NotEq - 1,0..1,2
   1] Gt - 2,0..2,1
  .comparators[2]
   0] Name 'x' Load - 1,3..1,4
   1] Name 'c' Load - 3,0..3,1
'''),

('', 1, 2, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x !='''), r'''
(a
< # left
x !=
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
Compare - ROOT 0,1..3,1
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] Lt - 1,0..1,1
   1] NotEq - 2,2..2,4
  .comparators[2]
   0] Name 'x' Load - 2,0..2,1
   1] Name 'c' Load - 3,0..3,1
'''),

('', 0, 1, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''== x'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 2, 3, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x =='''),
r'''**SyntaxError('invalid syntax')**'''),

('', 1, 2, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''== x'''), r'''
(a
== x
> # right
c)
''',
r'''**SyntaxError("unexpected code after cmpop, 'x'")**''', r'''
Compare - ROOT 0,1..3,1
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] Eq - 1,0..1,2
   1] Gt - 2,0..2,1
  .comparators[2]
   0] Name 'x' Load - 1,3..1,4
   1] Name 'c' Load - 3,0..3,1
'''),

('', 1, 2, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x =='''), r'''
(a
< # left
x ==
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
Compare - ROOT 0,1..3,1
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] Lt - 1,0..1,1
   1] Eq - 2,2..2,4
  .comparators[2]
   0] Name 'x' Load - 2,0..2,1
   1] Name 'c' Load - 3,0..3,1
'''),

('', 1, 1, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''== x'''), r'''
(a
== x < # left
b
> # right
c)
''',
r'''**SyntaxError("unexpected code after cmpop, 'x'")**''', r'''
Compare - ROOT 0,1..4,1
  .left Name 'a' Load - 0,1..0,2
  .ops[3]
   0] Eq - 1,0..1,2
   1] Lt - 1,5..1,6
   2] Gt - 3,0..3,1
  .comparators[3]
   0] Name 'x' Load - 1,3..1,4
   1] Name 'b' Load - 2,0..2,1
   2] Name 'c' Load - 4,0..4,1
'''),

('', 1, 1, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x =='''), r'''
(a
< # left
x == b
> # right
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
Compare - ROOT 0,1..4,1
  .left Name 'a' Load - 0,1..0,2
  .ops[3]
   0] Lt - 1,0..1,1
   1] Eq - 2,2..2,4
   2] Gt - 3,0..3,1
  .comparators[3]
   0] Name 'x' Load - 2,0..2,1
   1] Name 'b' Load - 2,5..2,6
   2] Name 'c' Load - 4,0..4,1
'''),

('', 1, 1, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None, r'''

== # dangling
x

'''), r'''
(a
== # dangling
x
< # left
b
> # right
c)
''',
r'''**SyntaxError("unexpected code after cmpop, 'x'")**''', r'''
Compare - ROOT 0,1..6,1
  .left Name 'a' Load - 0,1..0,2
  .ops[3]
   0] Eq - 1,0..1,2
   1] Lt - 3,0..3,1
   2] Gt - 5,0..5,1
  .comparators[3]
   0] Name 'x' Load - 2,0..2,1
   1] Name 'b' Load - 4,0..4,1
   2] Name 'c' Load - 6,0..6,1
'''),

('', 1, 1, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None, r'''

x
== # dangling

'''), r'''
(a
< # left
x
== # dangling
b
> # right
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
Compare - ROOT 0,1..6,1
  .left Name 'a' Load - 0,1..0,2
  .ops[3]
   0] Lt - 1,0..1,1
   1] Eq - 3,0..3,2
   2] Gt - 5,0..5,1
  .comparators[3]
   0] Name 'x' Load - 2,0..2,1
   1] Name 'b' Load - 4,0..4,1
   2] Name 'c' Load - 6,0..6,1
'''),

('', 3, 3, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None, r'''

== # dangling
x

'''), r'''
(a
< # left
b
> # right
c
== # dangling
x
)
''',
r'''**SyntaxError("unexpected code after cmpop, 'x'")**''', r'''
Compare - ROOT 0,1..6,1
  .left Name 'a' Load - 0,1..0,2
  .ops[3]
   0] Lt - 1,0..1,1
   1] Gt - 3,0..3,1
   2] Eq - 5,0..5,2
  .comparators[3]
   0] Name 'b' Load - 2,0..2,1
   1] Name 'c' Load - 4,0..4,1
   2] Name 'x' Load - 6,0..6,1
'''),

('', 0, 0, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None, r'''

x
== # dangling

'''), r'''
(x
== # dangling
a
< # left
b
> # right
c)
''',
r'''**ParseError('invalid syntax')**''', r'''
Compare - ROOT 0,1..6,1
  .left Name 'x' Load - 0,1..0,2
  .ops[3]
   0] Eq - 1,0..1,2
   1] Lt - 3,0..3,1
   2] Gt - 5,0..5,1
  .comparators[3]
   0] Name 'a' Load - 2,0..2,1
   1] Name 'b' Load - 4,0..4,1
   2] Name 'c' Load - 6,0..6,1
'''),

('', 3, 3, None, {}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x'''),
r'''**ValueError("insertion to Compare requires an 'op' extra operator to insert")**'''),

('', 3, 3, None, {'op': '=='}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x'''), r'''
(a
< # left
b
> # right
c == x)
''', r'''
Compare - ROOT 0,1..4,6
  .left Name 'a' Load - 0,1..0,2
  .ops[3]
   0] Lt - 1,0..1,1
   1] Gt - 3,0..3,1
   2] Eq - 4,2..4,4
  .comparators[3]
   0] Name 'b' Load - 2,0..2,1
   1] Name 'c' Load - 4,0..4,1
   2] Name 'x' Load - 4,5..4,6
'''),

('', 3, 3, None, {'op': '\n==\n'}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x'''), r'''
(a
< # left
b
> # right
c
==
x)
''', r'''
Compare - ROOT 0,1..6,1
  .left Name 'a' Load - 0,1..0,2
  .ops[3]
   0] Lt - 1,0..1,1
   1] Gt - 3,0..3,1
   2] Eq - 5,0..5,2
  .comparators[3]
   0] Name 'b' Load - 2,0..2,1
   1] Name 'c' Load - 4,0..4,1
   2] Name 'x' Load - 6,0..6,1
'''),

('', 0, 0, None, {'op': '=='}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x'''), r'''
(x == a
< # left
b
> # right
c)
''', r'''
Compare - ROOT 0,1..4,1
  .left Name 'x' Load - 0,1..0,2
  .ops[3]
   0] Eq - 0,3..0,5
   1] Lt - 1,0..1,1
   2] Gt - 3,0..3,1
  .comparators[3]
   0] Name 'a' Load - 0,6..0,7
   1] Name 'b' Load - 2,0..2,1
   2] Name 'c' Load - 4,0..4,1
'''),

('', 0, 0, None, {'op': '\n==\n'}, (None, r'''
a
< # left
b
> # right
c
'''), (None,
r'''x'''), r'''
(x
==
a
< # left
b
> # right
c)
''', r'''
Compare - ROOT 0,1..6,1
  .left Name 'x' Load - 0,1..0,2
  .ops[3]
   0] Eq - 1,0..1,2
   1] Lt - 3,0..3,1
   2] Gt - 5,0..5,1
  .comparators[3]
   0] Name 'a' Load - 2,0..2,1
   1] Name 'b' Load - 4,0..4,1
   2] Name 'c' Load - 6,0..6,1
'''),

('body[0].value', 1, 2, None, {}, (None, r'''
if 1:
    a = (a
         < b
         > c
    )
'''), (None, r'''

== d
!= e

'''), r'''
if 1:
    a = (a
         == d
         != e
         > c
    )
''',
r'''**SyntaxError("unexpected code after cmpop, 'd'")**''', r'''
If - ROOT 0,0..5,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..5,5
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value Compare - 1,9..4,12
       .left Name 'a' Load - 1,9..1,10
       .ops[3]
        0] Eq - 2,9..2,11
        1] NotEq - 3,9..3,11
        2] Gt - 4,9..4,10
       .comparators[3]
        0] Name 'd' Load - 2,12..2,13
        1] Name 'e' Load - 3,12..3,13
        2] Name 'c' Load - 4,11..4,12
'''),

('body[0].value', 1, 2, None, {}, (None, r'''
if 1:
    a = (a
         < b
         > c
    )
'''), (None, r'''

d ==
e !=

'''), r'''
if 1:
    a = (a
         <
         d ==
         e !=
         c
    )
''',
r'''**ParseError('invalid syntax')**''', r'''
If - ROOT 0,0..6,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..6,5
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value Compare - 1,9..5,10
       .left Name 'a' Load - 1,9..1,10
       .ops[3]
        0] Lt - 2,9..2,10
        1] Eq - 3,11..3,13
        2] NotEq - 4,11..4,13
       .comparators[3]
        0] Name 'd' Load - 3,9..3,10
        1] Name 'e' Load - 4,9..4,10
        2] Name 'c' Load - 5,9..5,10
'''),

('body[0].value', 1, 2, None, {}, (None, r'''
if 1:
    a = (a <
         b >
         c
    )
'''), (None, r'''

== d
!= e

'''), r'''
if 1:
    a = (a
         == d
         != e
         >
         c
    )
''',
r'''**SyntaxError("unexpected code after cmpop, 'd'")**''', r'''
If - ROOT 0,0..6,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..6,5
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value Compare - 1,9..5,10
       .left Name 'a' Load - 1,9..1,10
       .ops[3]
        0] Eq - 2,9..2,11
        1] NotEq - 3,9..3,11
        2] Gt - 4,9..4,10
       .comparators[3]
        0] Name 'd' Load - 2,12..2,13
        1] Name 'e' Load - 3,12..3,13
        2] Name 'c' Load - 5,9..5,10
'''),

('body[0].value', 1, 2, None, {}, (None, r'''
if 1:
    a = (a <
         b >
         c
    )
'''), (None, r'''

d ==
e !=

'''), r'''
if 1:
    a = (a <
         d ==
         e !=
         c
    )
''',
r'''**ParseError('invalid syntax')**''', r'''
If - ROOT 0,0..5,5
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..5,5
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value Compare - 1,9..4,10
       .left Name 'a' Load - 1,9..1,10
       .ops[3]
        0] Lt - 1,11..1,12
        1] Eq - 2,11..2,13
        2] NotEq - 3,11..3,13
       .comparators[3]
        0] Name 'd' Load - 2,9..2,10
        1] Name 'e' Load - 3,9..3,10
        2] Name 'c' Load - 4,9..4,10
'''),

('', 1, 2, None, {'one': True}, (None,
r'''a < b > c'''), (None,
r'''x or'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 1, 1, None, {'one': True}, (None,
r'''a < b > c'''), (None,
r'''**DEL**'''),
r'''a < b > c''', r'''
Compare - ROOT 0,0..0,9
  .left Name 'a' Load - 0,0..0,1
  .ops[2]
   0] Lt - 0,2..0,3
   1] Gt - 0,6..0,7
  .comparators[2]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'c' Load - 0,8..0,9
'''),
],

'Call_args': [  # ................................................................................

('', 0, 1, None, {}, (None, r'''
call( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
)
'''), (None,
r'''x,'''), r'''
call( \
x,
* \
b \
, \
c \
, \
** \
d \
)
''', r'''
Call - ROOT 0,0..9,1
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'x' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 5,0..5,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
'''),

('', 1, 2, None, {}, (None, r'''
call( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
)
'''), (None,
r'''x,'''), r'''
call( \
a \
, \
x,
c \
, \
** \
d \
)
''', r'''
Call - ROOT 0,0..8,1
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'x' Load - 3,0..3,1
   2] Name 'c' Load - 4,0..4,1
  .keywords[1]
   0] keyword - 6,0..7,1
     .value Name 'd' Load - 7,0..7,1
'''),

('', 2, 3, None, {}, (None, r'''
call( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
)
'''), (None,
r'''x,'''), r'''
call( \
a \
, \
* \
b \
, \
x,
** \
d \
)
''', r'''
Call - ROOT 0,0..9,1
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'x' Load - 6,0..6,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
'''),

('', 0, 3, None, {}, (None, r'''
call( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
)
'''), (None,
r'''x,'''), r'''
call( \
x,
** \
d \
)
''', r'''
Call - ROOT 0,0..4,1
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 1,0..1,1
  .keywords[1]
   0] keyword - 2,0..3,1
     .value Name 'd' Load - 3,0..3,1
'''),

('', 0, 3, None, {}, (None, r'''
call( \
a \
, \
* \
b \
, \
c \
, \
** \
d \
)
'''), (None,
r'''**DEL**'''), r'''
call( \
** \
d \
)
''', r'''
Call - ROOT 0,0..3,1
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 1,0..2,1
     .value Name 'd' Load - 2,0..2,1
'''),

('', 0, 1, None, {}, (None, r'''
call(
a
,
*
b
,
c
,
**
d
)
'''), (None,
r'''x,'''), r'''
call(
x,
*
b
,
c
,
**
d
)
''', r'''
Call - ROOT 0,0..9,1
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'x' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 5,0..5,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
'''),

('', 1, 2, None, {}, (None, r'''
call(
a
,
*
b
,
c
,
**
d
)
'''), (None,
r'''x,'''), r'''
call(
a
,
x,
c
,
**
d
)
''', r'''
Call - ROOT 0,0..8,1
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'x' Load - 3,0..3,1
   2] Name 'c' Load - 4,0..4,1
  .keywords[1]
   0] keyword - 6,0..7,1
     .value Name 'd' Load - 7,0..7,1
'''),

('', 2, 3, None, {}, (None, r'''
call(
a
,
*
b
,
c
,
**
d
)
'''), (None,
r'''x,'''), r'''
call(
a
,
*
b
,
x,
**
d
)
''', r'''
Call - ROOT 0,0..9,1
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'x' Load - 6,0..6,1
  .keywords[1]
   0] keyword - 7,0..8,1
     .value Name 'd' Load - 8,0..8,1
'''),

('', 0, 3, None, {}, (None, r'''
call(
a
,
*
b
,
c
,
**
d
)
'''), (None,
r'''x,'''), r'''
call(
x,
**
d
)
''', r'''
Call - ROOT 0,0..4,1
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 1,0..1,1
  .keywords[1]
   0] keyword - 2,0..3,1
     .value Name 'd' Load - 3,0..3,1
'''),

('', 0, 3, None, {}, (None, r'''
call(
a
,
*
b
,
c
,
**
d
)
'''), (None,
r'''**DEL**'''), r'''
call(
**
d
)
''', r'''
Call - ROOT 0,0..3,1
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 1,0..2,1
     .value Name 'd' Load - 2,0..2,1
'''),

('', 0, 2, None, {}, (None,
r'''call(a, b=c, *d)'''), (None,
r'''x,'''),
r'''**NodeError('cannot get this Call.args slice because it includes parts after a keyword')**'''),

('', 1, 2, None, {}, (None,
r'''call(a, b=c, *d)'''), (None,
r'''x,'''),
r'''**NodeError('cannot get this Call.args slice because it includes parts after a keyword')**'''),

('', 0, 1, None, {}, (None,
r'''call(a, b=c, *d)'''), (None,
r'''x,'''),
r'''call(x, b=c, *d)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'x' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'd' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'b'
     .value Name 'c' Load - 0,10..0,11
'''),

('', 0, 1, None, {}, (None,
r'''call(a, b=c, *d,)'''), (None,
r'''x,'''),
r'''call(x, b=c, *d,)''', r'''
Call - ROOT 0,0..0,17
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'x' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'd' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'b'
     .value Name 'c' Load - 0,10..0,11
'''),

('', 0, 1, None, {}, (None,
r'''call(a, b, c=d, *e)'''), (None,
r'''x,'''),
r'''call(x, b, c=d, *e)''', r'''
Call - ROOT 0,0..0,19
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'x' Load - 0,5..0,6
   1] Name 'b' Load - 0,8..0,9
   2] Starred - 0,16..0,18
     .value Name 'e' Load - 0,17..0,18
     .ctx Load
  .keywords[1]
   0] keyword - 0,11..0,14
     .arg 'c'
     .value Name 'd' Load - 0,13..0,14
'''),

('', 1, 2, None, {}, (None,
r'''call(a, b, c=d, *e)'''), (None,
r'''x,'''),
r'''call(a, x, c=d, *e)''', r'''
Call - ROOT 0,0..0,19
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'a' Load - 0,5..0,6
   1] Name 'x' Load - 0,8..0,9
   2] Starred - 0,16..0,18
     .value Name 'e' Load - 0,17..0,18
     .ctx Load
  .keywords[1]
   0] keyword - 0,11..0,14
     .arg 'c'
     .value Name 'd' Load - 0,13..0,14
'''),

('', 0, 2, None, {}, (None,
r'''call(a, b, c=d, *e)'''), (None,
r'''x,'''),
r'''call(x, c=d, *e)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'x' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'e' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'c'
     .value Name 'd' Load - 0,10..0,11
'''),

('', 0, 2, None, {}, (None,
r'''call(a, b, c=d, *e,)'''), (None,
r'''x,'''),
r'''call(x, c=d, *e,)''', r'''
Call - ROOT 0,0..0,17
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'x' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'e' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'c'
     .value Name 'd' Load - 0,10..0,11
'''),

('', 0, 0, None, {}, (None,
r'''call()'''), (None,
r'''x,'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, 0, None, {}, (None,
r'''call()'''), (None,
r'''x, y,'''),
r'''call(x, y)''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'x' Load - 0,5..0,6
   1] Name 'y' Load - 0,8..0,9
'''),

('', 0, 0, None, {}, (None,
r'''call(a=b)'''), (None,
r'''x,'''),
r'''call(x, a=b)''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'a'
     .value Name 'b' Load - 0,10..0,11
'''),

('', 0, 0, None, {}, (None,
r'''call(a=b,)'''), (None,
r'''x,'''),
r'''call(x, a=b,)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'a'
     .value Name 'b' Load - 0,10..0,11
'''),

('', 0, 1, None, {}, (None,
r'''call(a, b)'''), (None,
r'''**DEL**'''),
r'''call(b)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'b' Load - 0,5..0,6
'''),

('', 1, 2, None, {}, (None,
r'''call(a, b)'''), (None,
r'''**DEL**'''),
r'''call(a)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
'''),

('', 0, 2, None, {}, (None,
r'''call(a, b)'''), (None,
r'''**DEL**'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
'''),

('', 1, 2, None, {}, (None,
r'''call(a, b, **c)'''), (None,
r'''**DEL**'''),
r'''call(a, **c)''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
  .keywords[1]
   0] keyword - 0,8..0,11
     .value Name 'c' Load - 0,10..0,11
'''),

('', 0, 2, None, {}, (None,
r'''call(a, b, **c)'''), (None,
r'''**DEL**'''),
r'''call(**c)''', r'''
Call - ROOT 0,0..0,9
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,8
     .value Name 'c' Load - 0,7..0,8
'''),

('', 1, 2, None, {}, (None,
r'''call(a, b, **c,)'''), (None,
r'''**DEL**'''),
r'''call(a, **c,)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
  .keywords[1]
   0] keyword - 0,8..0,11
     .value Name 'c' Load - 0,10..0,11
'''),

('', 0, 2, None, {}, (None,
r'''call(a, b, **c,)'''), (None,
r'''**DEL**'''),
r'''call(**c,)''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,8
     .value Name 'c' Load - 0,7..0,8
'''),

('', 0, 1, None, {}, (None,
r'''call(i for i in j)'''), (None,
r'''x,'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, 1, None, {}, (None,
r'''call(i for i in j)'''), (None,
r'''(x for x in y),'''),
r'''call((x for x in y))''', r'''
Call - ROOT 0,0..0,20
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] GeneratorExp - 0,5..0,19
     .elt Name 'x' Load - 0,6..0,7
     .generators[1]
      0] comprehension - 0,8..0,18
        .target Name 'x' Store - 0,12..0,13
        .iter Name 'y' Load - 0,17..0,18
        .is_async 0
'''),

('', 0, 1, None, {}, (None,
r'''call(i for i in j)'''), (None,
r'''**DEL**'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
'''),

('', 1, 2, None, {}, (None,
r'''call(i for i in j)'''), (None,
r'''a,'''),
r'''call((i for i in j), a)''', r'''
Call - ROOT 0,0..0,23
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] GeneratorExp - 0,5..0,19
     .elt Name 'i' Load - 0,6..0,7
     .generators[1]
      0] comprehension - 0,8..0,18
        .target Name 'i' Store - 0,12..0,13
        .iter Name 'j' Load - 0,17..0,18
        .is_async 0
   1] Name 'a' Load - 0,21..0,22
'''),

('', 1, 2, None, {}, (None,
r'''call(i for i in j)'''), (None,
r'''a, b'''),
r'''call((i for i in j), a, b)''', r'''
Call - ROOT 0,0..0,26
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] GeneratorExp - 0,5..0,19
     .elt Name 'i' Load - 0,6..0,7
     .generators[1]
      0] comprehension - 0,8..0,18
        .target Name 'i' Store - 0,12..0,13
        .iter Name 'j' Load - 0,17..0,18
        .is_async 0
   1] Name 'a' Load - 0,21..0,22
   2] Name 'b' Load - 0,24..0,25
'''),

('', 1, 2, None, {'one': True}, (None,
r'''call(i for i in j)'''), (None,
r'''a, b'''),
r'''call((i for i in j), (a, b))''', r'''
Call - ROOT 0,0..0,28
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] GeneratorExp - 0,5..0,19
     .elt Name 'i' Load - 0,6..0,7
     .generators[1]
      0] comprehension - 0,8..0,18
        .target Name 'i' Store - 0,12..0,13
        .iter Name 'j' Load - 0,17..0,18
        .is_async 0
   1] Tuple - 0,21..0,27
     .elts[2]
      0] Name 'a' Load - 0,22..0,23
      1] Name 'b' Load - 0,25..0,26
     .ctx Load
'''),

('', 0, 0, None, {'one': True}, (None,
r'''call()'''), (None,
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, 0, None, {'one': True}, (None,
r'''call()'''), (None,
r'''x,'''),
r'''call((x,))''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Tuple - 0,5..0,9
     .elts[1]
      0] Name 'x' Load - 0,6..0,7
     .ctx Load
'''),

('', 0, 0, None, {'one': True}, (None,
r'''call()'''), (None,
r'''x, y,'''),
r'''call((x, y,))''',
r'''call((x, y))''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Tuple - 0,5..0,12
     .elts[2]
      0] Name 'x' Load - 0,6..0,7
      1] Name 'y' Load - 0,9..0,10
     .ctx Load
'''),

('', 0, 2, None, {'one': True}, (None,
r'''call(a, b, c)'''), (None,
r'''x'''),
r'''call(x, c)''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'x' Load - 0,5..0,6
   1] Name 'c' Load - 0,8..0,9
'''),

('', 1, 3, None, {'one': True}, (None,
r'''call(a, b, c)'''), (None,
r'''x'''),
r'''call(a, x)''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Name 'x' Load - 0,8..0,9
'''),

('', 0, 3, None, {'one': True}, (None,
r'''call(a, b, c)'''), (None,
r'''x'''),
r'''call(x)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'x' Load - 0,5..0,6
'''),

('', 0, 2, None, {'one': True}, (None,
r'''call(a, b, c)'''), (None,
r'''*not a'''),
r'''call(*not a, c)''',
r'''call(*(not a), c)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Starred - 0,5..0,11
     .value UnaryOp - 0,6..0,11
       .op Not - 0,6..0,9
       .operand Name 'a' Load - 0,10..0,11
     .ctx Load
   1] Name 'c' Load - 0,13..0,14
'''),

('', 1, 3, None, {'one': True}, (None,
r'''call(a, b, c)'''), (None,
r'''*not a'''),
r'''call(a, *not a)''',
r'''call(a, *(not a))''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,8..0,14
     .value UnaryOp - 0,9..0,14
       .op Not - 0,9..0,12
       .operand Name 'a' Load - 0,13..0,14
     .ctx Load
'''),

('', 0, 3, None, {'one': True}, (None,
r'''call(a, b, c)'''), (None,
r'''*not a'''),
r'''call(*not a)''',
r'''call(*(not a))''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,11
     .value UnaryOp - 0,6..0,11
       .op Not - 0,6..0,9
       .operand Name 'a' Load - 0,10..0,11
     .ctx Load
'''),

('', 0, 2, None, {'_ver': 11}, (None,
r'''call(a, b, c)'''), (None,
r'''*not a,'''),
r'''call(*not a, c)''',
r'''call(*(not a), c)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Starred - 0,5..0,11
     .value UnaryOp - 0,6..0,11
       .op Not - 0,6..0,9
       .operand Name 'a' Load - 0,10..0,11
     .ctx Load
   1] Name 'c' Load - 0,13..0,14
'''),

('', 1, 3, None, {'_ver': 11}, (None,
r'''call(a, b, c)'''), (None,
r'''*not a,'''),
r'''call(a, *not a)''',
r'''call(a, *(not a))''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,8..0,14
     .value UnaryOp - 0,9..0,14
       .op Not - 0,9..0,12
       .operand Name 'a' Load - 0,13..0,14
     .ctx Load
'''),

('', 0, 3, None, {'_ver': 11}, (None,
r'''call(a, b, c)'''), (None,
r'''*not a,'''),
r'''call(*not a)''',
r'''call(*(not a))''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,11
     .value UnaryOp - 0,6..0,11
       .op Not - 0,6..0,9
       .operand Name 'a' Load - 0,10..0,11
     .ctx Load
'''),

('', 1, 2, None, {}, (None,
r'''call(a, b, c)'''), (None,
r'''*(not a),'''),
r'''call(a, *(not a), c)''', r'''
Call - ROOT 0,0..0,20
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,8..0,16
     .value UnaryOp - 0,10..0,15
       .op Not - 0,10..0,13
       .operand Name 'a' Load - 0,14..0,15
     .ctx Load
   2] Name 'c' Load - 0,18..0,19
'''),

('', 0, 2, None, {'one': True}, (None,
r'''call(a, b, **c,)'''), (None,
r'''*not a'''),
r'''call(*not a, **c,)''',
r'''call(*(not a), **c,)''', r'''
Call - ROOT 0,0..0,18
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,11
     .value UnaryOp - 0,6..0,11
       .op Not - 0,6..0,9
       .operand Name 'a' Load - 0,10..0,11
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .value Name 'c' Load - 0,15..0,16
'''),

('', 0, 2, None, {'_ver': 11}, (None,
r'''call()'''), (None,
r'''*not a, *b or c'''),
r'''call(*not a, *b or c)''',
r'''call(*(not a), *(b or c))''', r'''
Call - ROOT 0,0..0,21
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Starred - 0,5..0,11
     .value UnaryOp - 0,6..0,11
       .op Not - 0,6..0,9
       .operand Name 'a' Load - 0,10..0,11
     .ctx Load
   1] Starred - 0,13..0,20
     .value BoolOp - 0,14..0,20
       .op Or
       .values[2]
        0] Name 'b' Load - 0,14..0,15
        1] Name 'c' Load - 0,19..0,20
     .ctx Load
'''),

('', 0, 2, None, {'one': True}, (None,
r'''call()'''), (None,
r'''*not a, *b or c'''),
r'''**ParseError('expecting single expression (arglike)')**'''),

('', 0, 2, None, {}, (None,
r'''call(a, b, c)'''), (None,
r'''*not a'''),
r'''call(*not a, c)''',
r'''call(*(not a), c)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Starred - 0,5..0,11
     .value UnaryOp - 0,6..0,11
       .op Not - 0,6..0,9
       .operand Name 'a' Load - 0,10..0,11
     .ctx Load
   1] Name 'c' Load - 0,13..0,14
'''),
],

'decorator_list': [  # ................................................................................

('', 0, 'end', 'decorator_list', {}, (None, r'''

@a

def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''

@x
@y

def f(): pass
''', r'''
FunctionDef - ROOT 4,0..4,13
  .name 'f'
  .body[1]
   0] Pass - 4,9..4,13
  .decorator_list[2]
   0] Name 'x' Load - 1,1..1,2
   1] Name 'y' Load - 2,1..2,2
'''),

('body[0]', 0, 'end', 'decorator_list', {}, (None, r'''
if 1:

  @a

  def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
if 1:

  @x
  @y

  def f(): pass
''', r'''
If - ROOT 0,0..5,15
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] FunctionDef - 5,2..5,15
     .name 'f'
     .body[1]
      0] Pass - 5,11..5,15
     .decorator_list[2]
      0] Name 'x' Load - 2,3..2,4
      1] Name 'y' Load - 3,3..3,4
'''),

('', 0, 'end', 'decorator_list', {'trivia': ('+', '+')}, (None, r'''

@a

def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''

@x
@y
def f(): pass
''', r'''
FunctionDef - ROOT 3,0..3,13
  .name 'f'
  .body[1]
   0] Pass - 3,9..3,13
  .decorator_list[2]
   0] Name 'x' Load - 1,1..1,2
   1] Name 'y' Load - 2,1..2,2
'''),

('body[0]', 0, 'end', 'decorator_list', {'trivia': ('+', '+')}, (None, r'''
if 1:

  @a

  def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
if 1:

  @x
  @y
  def f(): pass
''', r'''
If - ROOT 0,0..4,15
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] FunctionDef - 4,2..4,15
     .name 'f'
     .body[1]
      0] Pass - 4,11..4,15
     .decorator_list[2]
      0] Name 'x' Load - 2,3..2,4
      1] Name 'y' Load - 3,3..3,4
'''),

('', 0, 1, 'decorator_list', {}, (None, r'''
@a

# pre
def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
@x
@y

# pre
def f(): pass
''', r'''
FunctionDef - ROOT 4,0..4,13
  .name 'f'
  .body[1]
   0] Pass - 4,9..4,13
  .decorator_list[2]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,1..1,2
'''),

('', 0, 1, 'decorator_list', {}, (None, r'''
@a

# pre
def f(): pass
'''), (None,
r'''**DEL**'''), r'''

# pre
def f(): pass
''', r'''
FunctionDef - ROOT 2,0..2,13
  .name 'f'
  .body[1]
   0] Pass - 2,9..2,13
'''),

('', 0, 1, 'decorator_list', {}, (None,
'@a\n  \n# pre\nclass cls: pass'), ('_decorator_list', r'''
@x
@y
'''),
'@x\n@y\n  \n# pre\nclass cls: pass', r'''
ClassDef - ROOT 4,0..4,15
  .name 'cls'
  .body[1]
   0] Pass - 4,11..4,15
  .decorator_list[2]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,1..1,2
'''),

('', 0, 1, 'decorator_list', {'trivia': (None, '+')}, (None,
'@a\n  \n# pre\nclass cls: pass'), ('_decorator_list', r'''
@x
@y
'''), r'''
@x
@y
# pre
class cls: pass
''', r'''
ClassDef - ROOT 3,0..3,15
  .name 'cls'
  .body[1]
   0] Pass - 3,11..3,15
  .decorator_list[2]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,1..1,2
'''),

('', 0, 1, 'decorator_list', {'trivia': (None, 'all+')}, (None,
'@a\n  \n# pre\nclass cls: pass'), ('_decorator_list', r'''
@x
@y
'''), r'''
@x
@y
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,1..1,2
'''),

('', 1, 2, 'decorator_list', {}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
@a

@x
@y

# post

@c
def f(): pass
''', r'''
FunctionDef - ROOT 8,0..8,13
  .name 'f'
  .body[1]
   0] Pass - 8,9..8,13
  .decorator_list[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 2,1..2,2
   2] Name 'y' Load - 3,1..3,2
   3] Name 'c' Load - 7,1..7,2
'''),

('', 1, 2, 'decorator_list', {'trivia': ('all+', 'all+')}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
@a
@x
@y
@c
def f(): pass
''', r'''
FunctionDef - ROOT 4,0..4,13
  .name 'f'
  .body[1]
   0] Pass - 4,9..4,13
  .decorator_list[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
   2] Name 'y' Load - 2,1..2,2
   3] Name 'c' Load - 3,1..3,2
'''),

('', 2, 3, 'decorator_list', {}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
@a

# pre
@b  # line

# post

@x
@y
def f(): pass
''', r'''
FunctionDef - ROOT 9,0..9,13
  .name 'f'
  .body[1]
   0] Pass - 9,9..9,13
  .decorator_list[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 3,1..3,2
   2] Name 'x' Load - 7,1..7,2
   3] Name 'y' Load - 8,1..8,2
'''),

('', 2, 3, 'decorator_list', {'trivia': ('all+', 'all+')}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
@a

# pre
@b  # line
@x
@y
def f(): pass
''', r'''
FunctionDef - ROOT 6,0..6,13
  .name 'f'
  .body[1]
   0] Pass - 6,9..6,13
  .decorator_list[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 3,1..3,2
   2] Name 'x' Load - 4,1..4,2
   3] Name 'y' Load - 5,1..5,2
'''),

('', 0, 2, 'decorator_list', {'trivia': (None, 'all+')}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
@x
@y
@c
def f(): pass
''', r'''
FunctionDef - ROOT 3,0..3,13
  .name 'f'
  .body[1]
   0] Pass - 3,9..3,13
  .decorator_list[3]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,1..1,2
   2] Name 'c' Load - 2,1..2,2
'''),

('', 1, 3, 'decorator_list', {'trivia': 'all+'}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), ('_decorator_list', r'''
@x
@y
'''), r'''
@a
@x
@y
def f(): pass
''', r'''
FunctionDef - ROOT 3,0..3,13
  .name 'f'
  .body[1]
   0] Pass - 3,9..3,13
  .decorator_list[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
   2] Name 'y' Load - 2,1..2,2
'''),
],

'decorator_list_coerce': [  # ................................................................................

('', 1, 3, 'decorator_list', {'one': True}, (None, r'''
@a
@b
@c
def f(): pass
'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x
def f(): pass
''', r'''
FunctionDef - ROOT 2,0..2,13
  .name 'f'
  .body[1]
   0] Pass - 2,9..2,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 3, 'decorator_list', {'one': True, 'coerce': False}, (None, r'''
@a
@b
@c
def f(): pass
'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x
def f(): pass
''',
r'''**ValueError("cannot put _decorator_list node as 'one=True' without 'coerce=True'")**''', r'''
FunctionDef - ROOT 2,0..2,13
  .name 'f'
  .body[1]
   0] Pass - 2,9..2,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 3, 'decorator_list', {}, (None, r'''
@a
@b
@c
def f(): pass
'''), ('Name',
r'''x'''), r'''
@a
@x
def f(): pass
''', r'''
FunctionDef - ROOT 2,0..2,13
  .name 'f'
  .body[1]
   0] Pass - 2,9..2,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 3, 'decorator_list', {'coerce': False}, (None, r'''
@a
@b
@c
def f(): pass
'''), ('Name',
r'''x'''),
r'''**SyntaxError('unexpected multiple statements')**'''),

('', 1, 3, 'decorator_list', {'_src': False, 'coerce': False}, (None, r'''
@a
@b
@c
def f(): pass
'''), ('Name',
r'''x'''),
r'''**NodeError('expecting _decorator_list, got Name')**'''),

('', 1, 3, 'decorator_list', {'coerce': False, 'one': True}, (None, r'''
@a
@b
@c
def f(): pass
'''), ('Name',
r'''x'''), r'''
@a
@x
def f(): pass
''', r'''
FunctionDef - ROOT 2,0..2,13
  .name 'f'
  .body[1]
   0] Pass - 2,9..2,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 3, 'decorator_list', {}, (None, r'''
@a
@b
@c
def f(): pass
'''), ('Name', r'''

(
x
)

'''), r'''
@a

@(
x
)

def f(): pass
''', r'''
@a
@x
def f(): pass
''', r'''
FunctionDef - ROOT 6,0..6,13
  .name 'f'
  .body[1]
   0] Pass - 6,9..6,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 3,0..3,1
'''),

('', 1, 3, 'decorator_list', {'one': True}, ('_decorator_list', r'''
@a
@b
@c
'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x
''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 3, 'decorator_list', {'one': True, 'coerce': False}, ('_decorator_list', r'''
@a
@b
@c
'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x
''',
r'''**ValueError("cannot put _decorator_list node as 'one=True' without 'coerce=True'")**''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 3, 'decorator_list', {}, ('_decorator_list', r'''
@a
@b
@c
'''), ('Name',
r'''x'''), r'''
@a
@x
''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 3, 'decorator_list', {'coerce': False}, ('_decorator_list', r'''
@a
@b
@c
'''), ('Name',
r'''x'''),
r'''**SyntaxError('unexpected multiple statements')**'''),

('', 1, 3, 'decorator_list', {'coerce': False, 'one': True}, ('_decorator_list', r'''
@a
@b
@c
'''), ('Name',
r'''x'''), r'''
@a
@x
''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 3, 'decorator_list', {}, ('_decorator_list', r'''
@a
@b
@c
'''), ('Name', r'''

(
x
)

'''), r'''
@a

@(
x
)

''', r'''
@a
@x
''', r'''
_decorator_list - ROOT 0,0..5,0
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 3,0..3,1
'''),
],

'decorator_list_newlines': [  # ................................................................................

('', 0, 'end', None, {}, ('_decorator_list',
r'''@a'''), (None,
r'''**DEL**'''),
r'''''',
r'''_decorator_list - ROOT 0,0..0,0'''),

('', 0, 2, None, {}, ('_decorator_list', r'''
@a
@b
'''), (None,
r'''**DEL**'''),
r'''''',
r'''_decorator_list - ROOT 0,0..0,0'''),

('', 1, 2, None, {}, ('_decorator_list', r'''
@a
@b
'''), (None,
r'''**DEL**'''),
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, None, {}, ('_decorator_list', r'''
@a

@b
'''), (None,
r'''**DEL**'''), r'''
@a

''', r'''
_decorator_list - ROOT 0,0..1,0
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, None, {'trivia': '-'}, ('_decorator_list', r'''
@a

@b
'''), (None,
r'''**DEL**'''),
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, None, {}, ('_decorator_list', r'''
@a
# comment
@b
'''), (None,
r'''**DEL**'''),
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, None, {'trivia': False}, ('_decorator_list', r'''
@a
# comment
@b
'''), (None,
r'''**DEL**'''), r'''
@a
# comment
''', r'''
_decorator_list - ROOT 0,0..1,9
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, None, {}, ('_decorator_list', r'''
@a
# comment

@b
'''), (None,
r'''**DEL**'''), r'''
@a
# comment

''', r'''
_decorator_list - ROOT 0,0..2,0
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, None, {'trivia': '-'}, ('_decorator_list', r'''
@a
# comment

@b
'''), (None,
r'''**DEL**'''), r'''
@a
# comment
''', r'''
_decorator_list - ROOT 0,0..1,9
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('body[1]', 0, 1, 'decorator_list', {'trivia': '-'}, (None, r'''
pass

@a
class cls: pass
'''), (None,
r'''**DEL**'''), r'''
pass

class cls: pass
''', r'''
Module - ROOT 0,0..2,15
  .body[2]
   0] Pass - 0,0..0,4
   1] ClassDef - 2,0..2,15
     .name 'cls'
     .body[1]
      0] Pass - 2,11..2,15
'''),

('body[1]', 0, 1, 'decorator_list', {'trivia': '-'}, (None, r'''
if 1:
  pass

  @a
  class cls: pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  pass

  class cls: pass
''', r'''
If - ROOT 0,0..3,17
  .test Constant 1 - 0,3..0,4
  .body[2]
   0] Pass - 1,2..1,6
   1] ClassDef - 3,2..3,17
     .name 'cls'
     .body[1]
      0] Pass - 3,13..3,17
'''),

('', 0, 1, 'decorator_list', {}, (None, r'''

@a
@b
class cls: pass
'''), (None,
r'''**DEL**'''), r'''

@b
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[1]
   0] Name 'b' Load - 1,1..1,2
'''),

('', 0, 2, 'decorator_list', {}, (None, r'''

@a
@b
class cls: pass
'''), (None,
r'''**DEL**'''), r'''

class cls: pass
''', r'''
ClassDef - ROOT 1,0..1,15
  .name 'cls'
  .body[1]
   0] Pass - 1,11..1,15
'''),

('body[0]', 0, 1, 'decorator_list', {}, (None, r'''
if 1:

  @a
  @b
  class cls: pass
'''), (None,
r'''**DEL**'''), r'''
if 1:

  @b
  class cls: pass
''', r'''
If - ROOT 0,0..3,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 3,2..3,17
     .name 'cls'
     .body[1]
      0] Pass - 3,13..3,17
     .decorator_list[1]
      0] Name 'b' Load - 2,3..2,4
'''),

('body[0]', 0, 2, 'decorator_list', {}, (None, r'''
if 1:

  @a
  @b
  class cls: pass
'''), (None,
r'''**DEL**'''), r'''
if 1:

  class cls: pass
''', r'''
If - ROOT 0,0..2,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 2,2..2,17
     .name 'cls'
     .body[1]
      0] Pass - 2,13..2,17
'''),

('body[1]', 0, 'end', 'decorator_list', {}, ('exec', r'''
pass
class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
pass
@x
class cls: pass
''', r'''
Module - ROOT 0,0..2,15
  .body[2]
   0] Pass - 0,0..0,4
   1] ClassDef - 2,0..2,15
     .name 'cls'
     .body[1]
      0] Pass - 2,11..2,15
     .decorator_list[1]
      0] Name 'x' Load - 1,1..1,2
'''),

('body[1]', 0, 'end', 'decorator_list', {}, ('exec', r'''
pass

class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
pass

@x
class cls: pass
''', r'''
Module - ROOT 0,0..3,15
  .body[2]
   0] Pass - 0,0..0,4
   1] ClassDef - 3,0..3,15
     .name 'cls'
     .body[1]
      0] Pass - 3,11..3,15
     .decorator_list[1]
      0] Name 'x' Load - 2,1..2,2
'''),

('body[1]', 0, 'end', 'decorator_list', {}, ('exec',
'pass\n  \nclass cls: pass'), ('_decorator_list',
r'''@x'''),
'pass\n  \n@x\nclass cls: pass', r'''
Module - ROOT 0,0..3,15
  .body[2]
   0] Pass - 0,0..0,4
   1] ClassDef - 3,0..3,15
     .name 'cls'
     .body[1]
      0] Pass - 3,11..3,15
     .decorator_list[1]
      0] Name 'x' Load - 2,1..2,2
'''),

('body[1]', 0, 'end', 'decorator_list', {}, ('exec', r'''
pass

@a
class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
pass

@x
class cls: pass
''', r'''
Module - ROOT 0,0..3,15
  .body[2]
   0] Pass - 0,0..0,4
   1] ClassDef - 3,0..3,15
     .name 'cls'
     .body[1]
      0] Pass - 3,11..3,15
     .decorator_list[1]
      0] Name 'x' Load - 2,1..2,2
'''),

('body[0]', 0, 'end', 'decorator_list', {}, ('exec', r'''

class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''

@x
class cls: pass
''', r'''
Module - ROOT 0,0..2,15
  .body[1]
   0] ClassDef - 2,0..2,15
     .name 'cls'
     .body[1]
      0] Pass - 2,11..2,15
     .decorator_list[1]
      0] Name 'x' Load - 1,1..1,2
'''),

('body[0]', 0, 'end', 'decorator_list', {}, ('exec', r'''

@a
class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''

@x
class cls: pass
''', r'''
Module - ROOT 0,0..2,15
  .body[1]
   0] ClassDef - 2,0..2,15
     .name 'cls'
     .body[1]
      0] Pass - 2,11..2,15
     .decorator_list[1]
      0] Name 'x' Load - 1,1..1,2
'''),

('', 0, 'end', 'decorator_list', {}, (None, r'''

class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''

@x
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[1]
   0] Name 'x' Load - 1,1..1,2
'''),

('', 0, 0, 'decorator_list', {}, (None, r'''
@a
class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
@x
@a
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'a' Load - 1,1..1,2
'''),

('', 0, 0, 'decorator_list', {}, (None, r'''

@a
class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''

@x
@a
class cls: pass
''', r'''
ClassDef - ROOT 3,0..3,15
  .name 'cls'
  .body[1]
   0] Pass - 3,11..3,15
  .decorator_list[2]
   0] Name 'x' Load - 1,1..1,2
   1] Name 'a' Load - 2,1..2,2
'''),

('', 0, 'end', 'decorator_list', {}, (None, r'''
@a
class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
@x
class cls: pass
''', r'''
ClassDef - ROOT 1,0..1,15
  .name 'cls'
  .body[1]
   0] Pass - 1,11..1,15
  .decorator_list[1]
   0] Name 'x' Load - 0,1..0,2
'''),

('', 0, 'end', 'decorator_list', {}, (None, r'''

@a
class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''

@x
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[1]
   0] Name 'x' Load - 1,1..1,2
'''),

('', 1, 1, 'decorator_list', {}, (None, r'''
@a
class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 0, 'end', 'decorator_list', {}, (None,
r'''class cls: pass'''), ('_decorator_list',
r'''@x'''), r'''
@x
class cls: pass
''', r'''
ClassDef - ROOT 1,0..1,15
  .name 'cls'
  .body[1]
   0] Pass - 1,11..1,15
  .decorator_list[1]
   0] Name 'x' Load - 0,1..0,2
'''),

('body[0].body[1]', 0, 'end', 'decorator_list', {}, ('exec', r'''
if 1:
  pass
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:
  pass
  @x
  class cls: pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] If - 0,0..3,17
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Pass - 1,2..1,6
      1] ClassDef - 3,2..3,17
        .name 'cls'
        .body[1]
         0] Pass - 3,13..3,17
        .decorator_list[1]
         0] Name 'x' Load - 2,3..2,4
'''),

('body[0].body[1]', 0, 'end', 'decorator_list', {}, ('exec', r'''
if 1:
  pass

  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:
  pass

  @x
  class cls: pass
''', r'''
Module - ROOT 0,0..4,17
  .body[1]
   0] If - 0,0..4,17
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Pass - 1,2..1,6
      1] ClassDef - 4,2..4,17
        .name 'cls'
        .body[1]
         0] Pass - 4,13..4,17
        .decorator_list[1]
         0] Name 'x' Load - 3,3..3,4
'''),

('body[0].body[1]', 0, 'end', 'decorator_list', {}, ('exec',
'if 1:\n  pass\n  \n  class cls: pass'), ('_decorator_list',
r'''@x'''),
'if 1:\n  pass\n  \n  @x\n  class cls: pass', r'''
Module - ROOT 0,0..4,17
  .body[1]
   0] If - 0,0..4,17
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Pass - 1,2..1,6
      1] ClassDef - 4,2..4,17
        .name 'cls'
        .body[1]
         0] Pass - 4,13..4,17
        .decorator_list[1]
         0] Name 'x' Load - 3,3..3,4
'''),

('body[0].body[1]', 0, 'end', 'decorator_list', {}, ('exec', r'''
if 1:
  pass

  @a
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:
  pass

  @x
  class cls: pass
''', r'''
Module - ROOT 0,0..4,17
  .body[1]
   0] If - 0,0..4,17
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Pass - 1,2..1,6
      1] ClassDef - 4,2..4,17
        .name 'cls'
        .body[1]
         0] Pass - 4,13..4,17
        .decorator_list[1]
         0] Name 'x' Load - 3,3..3,4
'''),

('body[0].body[0]', 0, 'end', 'decorator_list', {}, ('exec', r'''
if 1:

  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:

  @x
  class cls: pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] If - 0,0..3,17
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] ClassDef - 3,2..3,17
        .name 'cls'
        .body[1]
         0] Pass - 3,13..3,17
        .decorator_list[1]
         0] Name 'x' Load - 2,3..2,4
'''),

('body[0].body[0]', 0, 'end', 'decorator_list', {}, ('exec', r'''
if 1:

  @a
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:

  @x
  class cls: pass
''', r'''
Module - ROOT 0,0..3,17
  .body[1]
   0] If - 0,0..3,17
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] ClassDef - 3,2..3,17
        .name 'cls'
        .body[1]
         0] Pass - 3,13..3,17
        .decorator_list[1]
         0] Name 'x' Load - 2,3..2,4
'''),

('body[0]', 0, 'end', 'decorator_list', {}, (None, r'''
if 1:

  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:

  @x
  class cls: pass
''', r'''
If - ROOT 0,0..3,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 3,2..3,17
     .name 'cls'
     .body[1]
      0] Pass - 3,13..3,17
     .decorator_list[1]
      0] Name 'x' Load - 2,3..2,4
'''),

('body[0]', 0, 0, 'decorator_list', {}, (None, r'''
if 1:
  @a
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:
  @x
  @a
  class cls: pass
''', r'''
If - ROOT 0,0..3,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 3,2..3,17
     .name 'cls'
     .body[1]
      0] Pass - 3,13..3,17
     .decorator_list[2]
      0] Name 'x' Load - 1,3..1,4
      1] Name 'a' Load - 2,3..2,4
'''),

('body[0]', 0, 0, 'decorator_list', {}, (None, r'''
if 1:

  @a
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:

  @x
  @a
  class cls: pass
''', r'''
If - ROOT 0,0..4,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 4,2..4,17
     .name 'cls'
     .body[1]
      0] Pass - 4,13..4,17
     .decorator_list[2]
      0] Name 'x' Load - 2,3..2,4
      1] Name 'a' Load - 3,3..3,4
'''),

('body[0]', 0, 'end', 'decorator_list', {}, (None, r'''
if 1:
  @a
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:
  @x
  class cls: pass
''', r'''
If - ROOT 0,0..2,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 2,2..2,17
     .name 'cls'
     .body[1]
      0] Pass - 2,13..2,17
     .decorator_list[1]
      0] Name 'x' Load - 1,3..1,4
'''),

('body[0]', 0, 'end', 'decorator_list', {}, (None, r'''
if 1:

  @a
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:

  @x
  class cls: pass
''', r'''
If - ROOT 0,0..3,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 3,2..3,17
     .name 'cls'
     .body[1]
      0] Pass - 3,13..3,17
     .decorator_list[1]
      0] Name 'x' Load - 2,3..2,4
'''),

('body[0]', 1, 1, 'decorator_list', {}, (None, r'''
if 1:
  @a
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:
  @a
  @x
  class cls: pass
''', r'''
If - ROOT 0,0..3,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 3,2..3,17
     .name 'cls'
     .body[1]
      0] Pass - 3,13..3,17
     .decorator_list[2]
      0] Name 'a' Load - 1,3..1,4
      1] Name 'x' Load - 2,3..2,4
'''),

('body[0]', 0, 'end', 'decorator_list', {}, (None, r'''
if 1:
  class cls: pass
'''), ('_decorator_list',
r'''@x'''), r'''
if 1:
  @x
  class cls: pass
''', r'''
If - ROOT 0,0..2,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 2,2..2,17
     .name 'cls'
     .body[1]
      0] Pass - 2,13..2,17
     .decorator_list[1]
      0] Name 'x' Load - 1,3..1,4
'''),

('', 0, 'end', None, {}, ('_decorator_list',
r''''''), ('_decorator_list',
r'''@x'''),
r'''@x''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'x' Load - 0,1..0,2
'''),

('', 1, 1, None, {}, ('_decorator_list',
r'''@a'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x
''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 1, None, {}, ('_decorator_list', r'''
@a

'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x

''', r'''
_decorator_list - ROOT 0,0..2,0
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 1, None, {}, ('_decorator_list', r'''
@a
# comment
'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x
# comment
''', r'''
_decorator_list - ROOT 0,0..2,9
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),

('', 1, 1, None, {}, ('_decorator_list', r'''
@a
# comment

'''), ('_decorator_list',
r'''@x'''), r'''
@a
@x
# comment

''', r'''
_decorator_list - ROOT 0,0..3,0
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
'''),
],

'generators': [  # ................................................................................

('', 0, 'end', 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('_comprehensions',
r'''for x in x'''),
r'''[_ for x in x]''', r'''
ListComp - ROOT 0,0..0,14
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name 'x' Store - 0,7..0,8
     .iter Name 'x' Load - 0,12..0,13
     .is_async 0
'''),

('', 0, 'end', 'generators', {'one': True}, (None,
r'''[_ for a in a for b in b for c in c]'''), (None,
r'''for x in x'''),
r'''[_ for x in x]''', r'''
ListComp - ROOT 0,0..0,14
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name 'x' Store - 0,7..0,8
     .iter Name 'x' Load - 0,12..0,13
     .is_async 0
'''),

('', 0, 'end', 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('_comprehensions',
r''' for x in x '''),
r'''[_  for x in x ]''',
r'''[_ for x in x]''', r'''
ListComp - ROOT 0,0..0,16
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,4..0,14
     .target Name 'x' Store - 0,8..0,9
     .iter Name 'x' Load - 0,13..0,14
     .is_async 0
'''),

('', 1, 2, 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('_comprehensions', r'''
for \
x \
in \
x
'''), r'''
[_ for a in a for \
   x \
   in \
   x for c in c]
''',
r'''[_ for a in a for x in x for c in c]''', r'''
ListComp - ROOT 0,0..3,16
  .elt Name '_' Load - 0,1..0,2
  .generators[3]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..3,4
     .target Name 'x' Store - 1,3..1,4
     .iter Name 'x' Load - 3,3..3,4
     .is_async 0
   2] comprehension - 3,5..3,15
     .target Name 'c' Store - 3,9..3,10
     .iter Name 'c' Load - 3,14..3,15
     .is_async 0
'''),

('', 0, 'end', 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('_comprehensions', r'''
for \
x \
in \
x \

'''), r'''
[_ for \
   x \
   in \
   x \
]
''',
r'''[_ for x in x]''', r'''
ListComp - ROOT 0,0..4,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..3,4
     .target Name 'x' Store - 1,3..1,4
     .iter Name 'x' Load - 3,3..3,4
     .is_async 0
'''),

('', 0, 'end', 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('_comprehensions', r'''

for \
x \
in \
x \

'''), r'''
[_
   for \
   x \
   in \
   x \
]
''',
r'''[_ for x in x]''', r'''
ListComp - ROOT 0,0..5,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 1,3..4,4
     .target Name 'x' Store - 2,3..2,4
     .iter Name 'x' Load - 4,3..4,4
     .is_async 0
'''),

('', 0, 'end', 'generators', {'norm': True}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''**DEL**''',
r'''**ValueError('cannot delete all ListComp.generators without norm_self=False')**'''),

('', 0, 'end', 'generators', {'norm_self': False, '_verify_self': False}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''**DEL**''',
r'''[_]''', r'''
ListComp - ROOT 0,0..0,3
  .elt Name '_' Load - 0,1..0,2
'''),

('', 0, 'end', 'generators', {}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('_comprehensions',
r'''for x in x'''),
r'''for x in x''', r'''
_comprehensions - ROOT 0,0..0,10
  .generators[1]
   0] comprehension - 0,0..0,10
     .target Name 'x' Store - 0,4..0,5
     .iter Name 'x' Load - 0,9..0,10
     .is_async 0
'''),

('', 0, 'end', 'generators', {'one': True}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), (None,
r'''for x in x'''),
r'''for x in x''', r'''
_comprehensions - ROOT 0,0..0,10
  .generators[1]
   0] comprehension - 0,0..0,10
     .target Name 'x' Store - 0,4..0,5
     .iter Name 'x' Load - 0,9..0,10
     .is_async 0
'''),

('', 0, 'end', 'generators', {}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('_comprehensions',
r''' for x in x '''),
r''' for x in x ''',
r'''for x in x''', r'''
_comprehensions - ROOT 0,0..0,12
  .generators[1]
   0] comprehension - 0,1..0,11
     .target Name 'x' Store - 0,5..0,6
     .iter Name 'x' Load - 0,10..0,11
     .is_async 0
'''),

('', 1, 2, 'generators', {}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('_comprehensions', r'''
for \
x \
in \
x
'''), r'''
for a in a for \
x \
in \
x for c in c
''',
r'''for a in a for x in x for c in c''', r'''
_comprehensions - ROOT 0,0..3,12
  .generators[3]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..3,1
     .target Name 'x' Store - 1,0..1,1
     .iter Name 'x' Load - 3,0..3,1
     .is_async 0
   2] comprehension - 3,2..3,12
     .target Name 'c' Store - 3,6..3,7
     .iter Name 'c' Load - 3,11..3,12
     .is_async 0
'''),

('', 0, 'end', 'generators', {}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('_comprehensions', r'''
for \
x \
in \
x \

'''), r'''
for \
x \
in \
x \

''',
r'''for x in x''', r'''
_comprehensions - ROOT 0,0..4,0
  .generators[1]
   0] comprehension - 0,0..3,1
     .target Name 'x' Store - 1,0..1,1
     .iter Name 'x' Load - 3,0..3,1
     .is_async 0
'''),

('', 0, 'end', 'generators', {}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('_comprehensions', r'''

for \
x \
in \
x \

'''), r'''
for \
x \
in \
x \

''',
r'''for x in x''', r'''
_comprehensions - ROOT 0,0..4,0
  .generators[1]
   0] comprehension - 0,0..3,1
     .target Name 'x' Store - 1,0..1,1
     .iter Name 'x' Load - 3,0..3,1
     .is_async 0
'''),
],

'generators_coerce': [  # ................................................................................

('', 1, 3, 'generators', {'one': True}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('_comprehensions',
r'''for x in x for y in y'''),
r'''[_ for a in a for x in x for y in y]''', r'''
ListComp - ROOT 0,0..0,36
  .elt Name '_' Load - 0,1..0,2
  .generators[3]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'x' Store - 0,18..0,19
     .iter Name 'x' Load - 0,23..0,24
     .is_async 0
   2] comprehension - 0,25..0,35
     .target Name 'y' Store - 0,29..0,30
     .iter Name 'y' Load - 0,34..0,35
     .is_async 0
'''),

('', 1, 3, 'generators', {'one': True, 'coerce': False}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('_comprehensions',
r'''for x in x for y in y'''),
r'''[_ for a in a for x in x for y in y]''',
r'''**ValueError("cannot put _comprehensions node as 'one=True' without 'coerce=True'")**''', r'''
ListComp - ROOT 0,0..0,36
  .elt Name '_' Load - 0,1..0,2
  .generators[3]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'x' Store - 0,18..0,19
     .iter Name 'x' Load - 0,23..0,24
     .is_async 0
   2] comprehension - 0,25..0,35
     .target Name 'y' Store - 0,29..0,30
     .iter Name 'y' Load - 0,34..0,35
     .is_async 0
'''),

('', 1, 3, 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('comprehension',
r'''for x in x'''),
r'''[_ for a in a for x in x]''', r'''
ListComp - ROOT 0,0..0,25
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'x' Store - 0,18..0,19
     .iter Name 'x' Load - 0,23..0,24
     .is_async 0
'''),

('', 1, 3, 'generators', {'coerce': False}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('comprehension',
r'''for x in x'''),
r'''[_ for a in a for x in x]''',
r'''**NodeError('expecting _comprehensions, got comprehension')**''', r'''
ListComp - ROOT 0,0..0,25
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'x' Store - 0,18..0,19
     .iter Name 'x' Load - 0,23..0,24
     .is_async 0
'''),

('', 1, 3, 'generators', {'coerce': False, 'one': True}, (None,
r'''[_ for a in a for b in b for c in c]'''), ('comprehension',
r'''for x in x'''),
r'''[_ for a in a for x in x]''', r'''
ListComp - ROOT 0,0..0,25
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'x' Store - 0,18..0,19
     .iter Name 'x' Load - 0,23..0,24
     .is_async 0
'''),

('', 1, 3, 'generators', {'one': True}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('_comprehensions',
r'''for x in x for y in y'''),
r'''for a in a for x in x for y in y''', r'''
_comprehensions - ROOT 0,0..0,32
  .generators[3]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'x' Store - 0,15..0,16
     .iter Name 'x' Load - 0,20..0,21
     .is_async 0
   2] comprehension - 0,22..0,32
     .target Name 'y' Store - 0,26..0,27
     .iter Name 'y' Load - 0,31..0,32
     .is_async 0
'''),

('', 1, 3, 'generators', {'one': True, 'coerce': False}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('_comprehensions',
r'''for x in x for y in y'''),
r'''for a in a for x in x for y in y''',
r'''**ValueError("cannot put _comprehensions node as 'one=True' without 'coerce=True'")**''', r'''
_comprehensions - ROOT 0,0..0,32
  .generators[3]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'x' Store - 0,15..0,16
     .iter Name 'x' Load - 0,20..0,21
     .is_async 0
   2] comprehension - 0,22..0,32
     .target Name 'y' Store - 0,26..0,27
     .iter Name 'y' Load - 0,31..0,32
     .is_async 0
'''),

('', 1, 3, 'generators', {}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('comprehension',
r'''for x in x'''),
r'''for a in a for x in x''', r'''
_comprehensions - ROOT 0,0..0,21
  .generators[2]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'x' Store - 0,15..0,16
     .iter Name 'x' Load - 0,20..0,21
     .is_async 0
'''),

('', 1, 3, 'generators', {'coerce': False}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('comprehension',
r'''for x in x'''),
r'''for a in a for x in x''',
r'''**NodeError('expecting _comprehensions, got comprehension')**''', r'''
_comprehensions - ROOT 0,0..0,21
  .generators[2]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'x' Store - 0,15..0,16
     .iter Name 'x' Load - 0,20..0,21
     .is_async 0
'''),

('', 1, 3, 'generators', {'coerce': False, 'one': True}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), ('comprehension',
r'''for x in x'''),
r'''for a in a for x in x''', r'''
_comprehensions - ROOT 0,0..0,21
  .generators[2]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'x' Store - 0,15..0,16
     .iter Name 'x' Load - 0,20..0,21
     .is_async 0
'''),
],

'comprehension_ifs': [  # ................................................................................

('generators[0]', 0, 'end', 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''), ('_comprehension_ifs',
r'''if x'''),
r'''[_ for _ in _ if x]''', r'''
ListComp - ROOT 0,0..0,19
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,18
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'x' Load - 0,17..0,18
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {'one': True}, (None,
r'''[_ for _ in _ if a if b if c]'''), (None,
r'''x'''),
r'''[_ for _ in _ if x]''', r'''
ListComp - ROOT 0,0..0,19
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,18
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'x' Load - 0,17..0,18
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''), ('_comprehension_ifs',
r''' if x '''),
r'''[_ for _ in _  if x ]''',
r'''[_ for _ in _ if x]''', r'''
ListComp - ROOT 0,0..0,21
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,19
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'x' Load - 0,18..0,19
     .is_async 0
'''),

('generators[0]', 1, 2, 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''), ('_comprehension_ifs', r'''
if \
x
'''), r'''
[_ for _ in _ if a if \
              x if c]
''',
r'''[_ for _ in _ if a if x if c]''', r'''
ListComp - ROOT 0,0..1,21
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..1,20
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[3]
      0] Name 'a' Load - 0,17..0,18
      1] Name 'x' Load - 1,14..1,15
      2] Name 'c' Load - 1,19..1,20
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''), ('_comprehension_ifs', r'''
if \
x \

'''), r'''
[_ for _ in _ if \
              x \
]
''',
r'''[_ for _ in _ if x]''', r'''
ListComp - ROOT 0,0..2,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..1,15
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'x' Load - 1,14..1,15
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''), ('_comprehension_ifs', r'''

if \
x \

'''), r'''
[_ for _ in _
              if \
              x \
]
''',
r'''[_ for _ in _ if x]''', r'''
ListComp - ROOT 0,0..3,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..2,15
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'x' Load - 2,14..2,15
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''),
r'''**DEL**''',
r'''[_ for _ in _]''', r'''
ListComp - ROOT 0,0..0,14
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {}, ('_comprehensions',
r'''for _ in _ if a if b if c for _ in _'''), ('_comprehension_ifs',
r'''if x'''),
r'''for _ in _ if x for _ in _''', r'''
_comprehensions - ROOT 0,0..0,26
  .generators[2]
   0] comprehension - 0,0..0,15
     .target Name '_' Store - 0,4..0,5
     .iter Name '_' Load - 0,9..0,10
     .ifs[1]
      0] Name 'x' Load - 0,14..0,15
     .is_async 0
   1] comprehension - 0,16..0,26
     .target Name '_' Store - 0,20..0,21
     .iter Name '_' Load - 0,25..0,26
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {'one': True}, ('_comprehensions',
r'''for _ in _ if a if b if c for _ in _'''), (None,
r'''x'''),
r'''for _ in _ if x for _ in _''', r'''
_comprehensions - ROOT 0,0..0,26
  .generators[2]
   0] comprehension - 0,0..0,15
     .target Name '_' Store - 0,4..0,5
     .iter Name '_' Load - 0,9..0,10
     .ifs[1]
      0] Name 'x' Load - 0,14..0,15
     .is_async 0
   1] comprehension - 0,16..0,26
     .target Name '_' Store - 0,20..0,21
     .iter Name '_' Load - 0,25..0,26
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {}, ('_comprehensions',
r'''for _ in _ if a if b if c for _ in _'''), ('_comprehension_ifs',
r''' if x '''),
r'''for _ in _  if x  for _ in _''',
r'''for _ in _ if x for _ in _''', r'''
_comprehensions - ROOT 0,0..0,28
  .generators[2]
   0] comprehension - 0,0..0,16
     .target Name '_' Store - 0,4..0,5
     .iter Name '_' Load - 0,9..0,10
     .ifs[1]
      0] Name 'x' Load - 0,15..0,16
     .is_async 0
   1] comprehension - 0,18..0,28
     .target Name '_' Store - 0,22..0,23
     .iter Name '_' Load - 0,27..0,28
     .is_async 0
'''),

('generators[0]', 1, 2, 'ifs', {}, ('_comprehensions',
r'''for _ in _ if a if b if c for _ in _'''), ('_comprehension_ifs', r'''
if \
x
'''), r'''
for _ in _ if a if \
           x if c for _ in _
''',
r'''for _ in _ if a if x if c for _ in _''', r'''
_comprehensions - ROOT 0,0..1,28
  .generators[2]
   0] comprehension - 0,0..1,17
     .target Name '_' Store - 0,4..0,5
     .iter Name '_' Load - 0,9..0,10
     .ifs[3]
      0] Name 'a' Load - 0,14..0,15
      1] Name 'x' Load - 1,11..1,12
      2] Name 'c' Load - 1,16..1,17
     .is_async 0
   1] comprehension - 1,18..1,28
     .target Name '_' Store - 1,22..1,23
     .iter Name '_' Load - 1,27..1,28
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {}, ('_comprehensions',
r'''for _ in _ if a if b if c for _ in _'''), ('_comprehension_ifs', r'''
if \
x \

'''), r'''
for _ in _ if \
           x \
 for _ in _
''',
r'''for _ in _ if x for _ in _''', r'''
_comprehensions - ROOT 0,0..2,11
  .generators[2]
   0] comprehension - 0,0..1,12
     .target Name '_' Store - 0,4..0,5
     .iter Name '_' Load - 0,9..0,10
     .ifs[1]
      0] Name 'x' Load - 1,11..1,12
     .is_async 0
   1] comprehension - 2,1..2,11
     .target Name '_' Store - 2,5..2,6
     .iter Name '_' Load - 2,10..2,11
     .is_async 0
'''),

('generators[0]', 0, 'end', 'ifs', {}, ('_comprehensions',
r'''for _ in _ if a if b if c for _ in _'''), ('_comprehension_ifs', r'''

if \
x \

'''), r'''
for _ in _
           if \
           x \
 for _ in _
''',
r'''for _ in _ if x for _ in _''', r'''
_comprehensions - ROOT 0,0..3,11
  .generators[2]
   0] comprehension - 0,0..2,12
     .target Name '_' Store - 0,4..0,5
     .iter Name '_' Load - 0,9..0,10
     .ifs[1]
      0] Name 'x' Load - 2,11..2,12
     .is_async 0
   1] comprehension - 3,1..3,11
     .target Name '_' Store - 3,5..3,6
     .iter Name '_' Load - 3,10..3,11
     .is_async 0
'''),

('', 0, 'end', 'ifs', {}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('_comprehension_ifs',
r'''if x'''),
r'''for _ in _ if x''', r'''
comprehension - ROOT 0,0..0,15
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[1]
   0] Name 'x' Load - 0,14..0,15
  .is_async 0
'''),

('', 0, 'end', 'ifs', {'one': True}, ('comprehension',
r'''for _ in _ if a if b if c'''), (None,
r'''x'''),
r'''for _ in _ if x''', r'''
comprehension - ROOT 0,0..0,15
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[1]
   0] Name 'x' Load - 0,14..0,15
  .is_async 0
'''),

('', 0, 'end', 'ifs', {}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('_comprehension_ifs',
r''' if x '''),
r'''for _ in _  if x ''',
r'''for _ in _ if x''', r'''
comprehension - ROOT 0,0..0,16
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[1]
   0] Name 'x' Load - 0,15..0,16
  .is_async 0
'''),

('', 1, 2, 'ifs', {}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('_comprehension_ifs', r'''
if \
x
'''), r'''
for _ in _ if a if \
           x if c
''',
r'''for _ in _ if a if x if c''', r'''
comprehension - ROOT 0,0..1,17
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[3]
   0] Name 'a' Load - 0,14..0,15
   1] Name 'x' Load - 1,11..1,12
   2] Name 'c' Load - 1,16..1,17
  .is_async 0
'''),

('', 0, 'end', 'ifs', {}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('_comprehension_ifs', r'''
if \
x \

'''), r'''
for _ in _ if \
           x \

''',
r'''for _ in _ if x''', r'''
comprehension - ROOT 0,0..1,12
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[1]
   0] Name 'x' Load - 1,11..1,12
  .is_async 0
'''),

('', 0, 'end', 'ifs', {}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('_comprehension_ifs', r'''

if \
x \

'''), r'''
for _ in _
           if \
           x \

''',
r'''for _ in _ if x''', r'''
comprehension - ROOT 0,0..2,12
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[1]
   0] Name 'x' Load - 2,11..2,12
  .is_async 0
'''),
],

'comprehension_ifs_coerce': [  # ................................................................................

('', 1, 3, 'ifs', {'one': True}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('_comprehension_ifs',
r'''if x if y'''),
r'''for _ in _ if a if x if y''', r'''
comprehension - ROOT 0,0..0,25
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[3]
   0] Name 'a' Load - 0,14..0,15
   1] Name 'x' Load - 0,19..0,20
   2] Name 'y' Load - 0,24..0,25
  .is_async 0
'''),

('', 1, 3, 'ifs', {'one': True, 'coerce': False}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('_comprehension_ifs',
r'''if x if y'''),
r'''for _ in _ if a if x if y''',
r'''**ValueError("cannot put _comprehension_ifs node as 'one=True' without 'coerce=True'")**''', r'''
comprehension - ROOT 0,0..0,25
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[3]
   0] Name 'a' Load - 0,14..0,15
   1] Name 'x' Load - 0,19..0,20
   2] Name 'y' Load - 0,24..0,25
  .is_async 0
'''),

('', 1, 3, 'ifs', {}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('Name',
r'''x'''),
r'''for _ in _ if a if x''', r'''
comprehension - ROOT 0,0..0,20
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[2]
   0] Name 'a' Load - 0,14..0,15
   1] Name 'x' Load - 0,19..0,20
  .is_async 0
'''),

('', 1, 3, 'ifs', {'coerce': False}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('Name',
r'''x'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 1, 3, 'ifs', {'coerce': False, 'one': True}, ('comprehension',
r'''for _ in _ if a if b if c'''), ('Name',
r'''x'''),
r'''for _ in _ if a if x''', r'''
comprehension - ROOT 0,0..0,20
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[2]
   0] Name 'a' Load - 0,14..0,15
   1] Name 'x' Load - 0,19..0,20
  .is_async 0
'''),

('', 1, 3, 'ifs', {'one': True}, ('_comprehension_ifs',
r'''if a if b if c'''), ('_comprehension_ifs',
r'''if x if y'''),
r'''if a if x if y''', r'''
_comprehension_ifs - ROOT 0,0..0,14
  .ifs[3]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'x' Load - 0,8..0,9
   2] Name 'y' Load - 0,13..0,14
'''),

('', 1, 3, 'ifs', {'one': True, 'coerce': False}, ('_comprehension_ifs',
r'''if a if b if c'''), ('_comprehension_ifs',
r'''if x if y'''),
r'''if a if x if y''',
r'''**ValueError("cannot put _comprehension_ifs node as 'one=True' without 'coerce=True'")**''', r'''
_comprehension_ifs - ROOT 0,0..0,14
  .ifs[3]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'x' Load - 0,8..0,9
   2] Name 'y' Load - 0,13..0,14
'''),

('', 1, 3, 'ifs', {}, ('_comprehension_ifs',
r'''if a if b if c'''), ('Name',
r'''x'''),
r'''if a if x''', r'''
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[2]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'x' Load - 0,8..0,9
'''),

('', 1, 3, 'ifs', {'coerce': False}, ('_comprehension_ifs',
r'''if a if b if c'''), ('Name',
r'''x'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 1, 3, 'ifs', {'coerce': False, 'one': True}, ('_comprehension_ifs',
r'''if a if b if c'''), ('Name',
r'''x'''),
r'''if a if x''', r'''
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[2]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'x' Load - 0,8..0,9
'''),
],

'MatchSequence': [  # ................................................................................

('', 1, 3, None, {}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchValue',
r'''1'''),
r'''[a, 1, d]''', r'''
MatchSequence - ROOT 0,0..0,9
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchValue - 0,4..0,5
     .value Constant 1 - 0,4..0,5
   2] MatchAs - 0,7..0,8
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchSingleton',
r'''True'''),
r'''[a, True, d]''', r'''
MatchSequence - ROOT 0,0..0,12
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchSingleton True - 0,4..0,8
   2] MatchAs - 0,10..0,11
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchSequence',
r'''1, 2'''),
r'''[a, 1, 2, d]''', r'''
MatchSequence - ROOT 0,0..0,12
  .patterns[4]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchValue - 0,4..0,5
     .value Constant 1 - 0,4..0,5
   2] MatchValue - 0,7..0,8
     .value Constant 2 - 0,7..0,8
   3] MatchAs - 0,10..0,11
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchMapping',
r'''{1: a}'''),
r'''[a, {1: a}, d]''', r'''
MatchSequence - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchMapping - 0,4..0,10
     .keys[1]
      0] Constant 1 - 0,5..0,6
     .patterns[1]
      0] MatchAs - 0,8..0,9
        .name 'a'
   2] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchClass',
r'''cls()'''),
r'''[a, cls(), d]''', r'''
MatchSequence - ROOT 0,0..0,13
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchClass - 0,4..0,9
     .cls Name 'cls' Load - 0,4..0,7
   2] MatchAs - 0,11..0,12
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchStar',
r'''*st'''),
r'''[a, *st, d]''', r'''
MatchSequence - ROOT 0,0..0,11
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchStar - 0,4..0,7
     .name 'st'
   2] MatchAs - 0,9..0,10
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchAs',
r'''x as y'''),
r'''[a, x as y, d]''', r'''
MatchSequence - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchAs - 0,4..0,10
     .pattern MatchAs - 0,4..0,5
       .name 'x'
     .name 'y'
   2] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchOr',
r'''x | y'''),
r'''[a, x | y, d]''', r'''
MatchSequence - ROOT 0,0..0,13
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchOr - 0,4..0,9
     .patterns[2]
      0] MatchAs - 0,4..0,5
        .name 'x'
      1] MatchAs - 0,8..0,9
        .name 'y'
   2] MatchAs - 0,11..0,12
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchValue',
r'''1'''),
r'''**ValueError("cannot put MatchValue as slice to MatchSequence without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchSingleton',
r'''True'''),
r'''**ValueError("cannot put MatchSingleton as slice to MatchSequence without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchSequence',
r'''1, 2'''),
r'''[a, 1, 2, d]''', r'''
MatchSequence - ROOT 0,0..0,12
  .patterns[4]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchValue - 0,4..0,5
     .value Constant 1 - 0,4..0,5
   2] MatchValue - 0,7..0,8
     .value Constant 2 - 0,7..0,8
   3] MatchAs - 0,10..0,11
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchMapping',
r'''{1: a}'''),
r'''**ValueError("cannot put MatchMapping as slice to MatchSequence without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchClass',
r'''cls()'''),
r'''**ValueError("cannot put MatchClass as slice to MatchSequence without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchStar',
r'''*st'''),
r'''**ValueError("cannot put MatchStar as slice to MatchSequence without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchAs',
r'''x as y'''),
r'''**ValueError("cannot put MatchAs as slice to MatchSequence without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchOr',
r'''x | y'''),
r'''**ValueError("cannot put MatchOr as slice to MatchSequence without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchValue',
r'''1'''),
r'''[a, 1, d]''', r'''
MatchSequence - ROOT 0,0..0,9
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchValue - 0,4..0,5
     .value Constant 1 - 0,4..0,5
   2] MatchAs - 0,7..0,8
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchSingleton',
r'''True'''),
r'''[a, True, d]''', r'''
MatchSequence - ROOT 0,0..0,12
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchSingleton True - 0,4..0,8
   2] MatchAs - 0,10..0,11
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchSequence',
r'''1, 2'''),
r'''[a, [1, 2], d]''', r'''
MatchSequence - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchSequence - 0,4..0,10
     .patterns[2]
      0] MatchValue - 0,5..0,6
        .value Constant 1 - 0,5..0,6
      1] MatchValue - 0,8..0,9
        .value Constant 2 - 0,8..0,9
   2] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchMapping',
r'''{1: a}'''),
r'''[a, {1: a}, d]''', r'''
MatchSequence - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchMapping - 0,4..0,10
     .keys[1]
      0] Constant 1 - 0,5..0,6
     .patterns[1]
      0] MatchAs - 0,8..0,9
        .name 'a'
   2] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchClass',
r'''cls()'''),
r'''[a, cls(), d]''', r'''
MatchSequence - ROOT 0,0..0,13
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchClass - 0,4..0,9
     .cls Name 'cls' Load - 0,4..0,7
   2] MatchAs - 0,11..0,12
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchStar',
r'''*st'''),
r'''[a, *st, d]''', r'''
MatchSequence - ROOT 0,0..0,11
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchStar - 0,4..0,7
     .name 'st'
   2] MatchAs - 0,9..0,10
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchAs',
r'''x as y'''),
r'''[a, x as y, d]''', r'''
MatchSequence - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchAs - 0,4..0,10
     .pattern MatchAs - 0,4..0,5
       .name 'x'
     .name 'y'
   2] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchOr',
r'''x | y'''),
r'''[a, x | y, d]''', r'''
MatchSequence - ROOT 0,0..0,13
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchOr - 0,4..0,9
     .patterns[2]
      0] MatchAs - 0,4..0,5
        .name 'x'
      1] MatchAs - 0,8..0,9
        .name 'y'
   2] MatchAs - 0,11..0,12
     .name 'd'
'''),

('', 1, 3, None, {'one': True}, ('MatchSequence',
r'''[a, b, c, d]'''), ('MatchSequence',
r'''1, 2'''),
r'''[a, [1, 2], d]''', r'''
MatchSequence - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchSequence - 0,4..0,10
     .patterns[2]
      0] MatchValue - 0,5..0,6
        .value Constant 1 - 0,5..0,6
      1] MatchValue - 0,8..0,9
        .value Constant 2 - 0,8..0,9
   2] MatchAs - 0,12..0,13
     .name 'd'
'''),
],

'MatchMapping': [  # ................................................................................

('', 0, 0, None, {}, ('pattern',
r'''{}'''), ('pattern',
r'''{0: x}'''),
r'''{0: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{}'''), ('pattern',
r'''{0: x,}'''),
r'''{0: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{}'''), ('pattern',
r'''{0: x, 1: y}'''),
r'''{0: x, 1: y}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 0 - 0,1..0,2
   1] Constant 1 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'x'
   1] MatchAs - 0,10..0,11
     .name 'y'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{}'''), ('pattern',
r'''{0: x, 1: y,}'''),
r'''{0: x, 1: y}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 0 - 0,1..0,2
   1] Constant 1 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'x'
   1] MatchAs - 0,10..0,11
     .name 'y'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{**rest}'''), ('pattern',
r'''{0: x}'''),
r'''{0: x, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{**rest}'''), ('pattern',
r'''{0: x,}'''),
r'''{0: x, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{**rest,}'''), ('pattern',
r'''{0: x}'''),
r'''{0: x, **rest,}''', r'''
MatchMapping - ROOT 0,0..0,15
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{**rest,}'''), ('pattern',
r'''{0: x,}'''),
r'''{0: x, **rest,}''', r'''
MatchMapping - ROOT 0,0..0,15
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
'''),

('', 0, 1, None, {}, ('pattern',
r'''{0: x, 1: y}'''), ('pattern',
r'''**DEL**'''),
r'''{1: y}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'y'
'''),

('', 1, 2, None, {}, ('pattern',
r'''{0: x, 1: y}'''), ('pattern',
r'''**DEL**'''),
r'''{0: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 2, None, {}, ('pattern',
r'''{0: x, 1: y}'''), ('pattern',
r'''**DEL**'''),
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2'''),

('', 1, 2, None, {}, ('pattern',
r'''{0: x, 1: y, **rest}'''), ('pattern',
r'''**DEL**'''),
r'''{0: x, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
'''),

('', 0, 2, None, {}, ('pattern',
r'''{0: x, 1: y, **rest}'''), ('pattern',
r'''**DEL**'''),
r'''{**rest}''', r'''
MatchMapping - ROOT 0,0..0,8
  .rest 'rest'
'''),

('', 1, 2, None, {}, ('pattern',
r'''{0: x, 1: y, **rest,}'''), ('pattern',
r'''**DEL**'''),
r'''{0: x, **rest,}''', r'''
MatchMapping - ROOT 0,0..0,15
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
'''),

('', 0, 2, None, {}, ('pattern',
r'''{0: x, 1: y, **rest,}'''), ('pattern',
r'''**DEL**'''),
r'''{**rest,}''', r'''
MatchMapping - ROOT 0,0..0,9
  .rest 'rest'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{}'''), ('pattern',
r'''{}'''),
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2'''),

('', 0, 0, None, {}, ('pattern',
r'''{}'''), ('pattern',
r'''{2: x}'''),
r'''{2: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{}'''), ('pattern',
r'''{**y}'''),
r'''{**y}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'y'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{}'''), ('pattern',
r'''{2: x, **y}'''),
r'''{2: x, **y}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'y'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{}'''),
r'''{1: a}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{2: x}'''),
r'''{2: x, 1: a}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 2 - 0,1..0,2
   1] Constant 1 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'x'
   1] MatchAs - 0,10..0,11
     .name 'a'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{**y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 0, 0, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{2: x, **y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 0, 1, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{}'''),
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2'''),

('', 0, 1, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{2: x}'''),
r'''{2: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 1, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{**y}'''),
r'''{**y}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'y'
'''),

('', 0, 1, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{2: x, **y}'''),
r'''{2: x, **y}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'y'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{}'''),
r'''{1: a}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{2: x}'''),
r'''{1: a, 2: x}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'x'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{**y}'''),
r'''{1: a, **y}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'y'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{1: a}'''), ('pattern',
r'''{2: x, **y}'''),
r'''{1: a, 2: x, **y}''', r'''
MatchMapping - ROOT 0,0..0,17
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'x'
  .rest 'y'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{}'''),
r'''{**b}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'b'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{2: x}'''),
r'''{2: x, **b}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'b'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{**y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 0, 0, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 0, 1, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{}'''),
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2'''),

('', 0, 1, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{2: x}'''),
r'''{2: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 1, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{**y}'''),
r'''{**y}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'y'
'''),

('', 0, 1, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''{2: x, **y}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'y'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{}'''),
r'''{**b}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'b'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{2: x}'''),
r'''**ValueError("cannot put slice to MatchMapping after 'rest' element")**'''),

('', 1, 1, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{**y}'''),
r'''**ValueError("cannot put slice to MatchMapping after 'rest' element")**'''),

('', 1, 1, None, {}, ('pattern',
r'''{**b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''**ValueError("cannot put slice to MatchMapping after 'rest' element")**'''),

('', 0, 0, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{}'''),
r'''{1: a, **b}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'b'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x}'''),
r'''{2: x, 1: a, **b}''', r'''
MatchMapping - ROOT 0,0..0,17
  .keys[2]
   0] Constant 2 - 0,1..0,2
   1] Constant 1 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'x'
   1] MatchAs - 0,10..0,11
     .name 'a'
  .rest 'b'
'''),

('', 0, 0, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{**y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 0, 0, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 0, 1, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{}'''),
r'''{**b}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'b'
'''),

('', 0, 1, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x}'''),
r'''{2: x, **b}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'b'
'''),

('', 0, 1, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{**y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 0, 1, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 0, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{}'''),
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2'''),

('', 0, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x}'''),
r'''{2: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{**y}'''),
r'''{**y}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'y'
'''),

('', 0, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''{2: x, **y}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'y'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{}'''),
r'''{1: a, **b}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'b'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x}'''),
r'''{1: a, 2: x, **b}''', r'''
MatchMapping - ROOT 0,0..0,17
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'x'
  .rest 'b'
'''),

('', 1, 1, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{**y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 1, 1, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''**ValueError("put slice with 'rest' element to MatchMapping must be at end")**'''),

('', 1, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{}'''),
r'''{1: a}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
'''),

('', 1, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x}'''),
r'''{1: a, 2: x}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'x'
'''),

('', 1, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{**y}'''),
r'''{1: a, **y}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'y'
'''),

('', 1, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''{1: a, 2: x, **y}''', r'''
MatchMapping - ROOT 0,0..0,17
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'x'
  .rest 'y'
'''),

('', 2, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{}'''),
r'''{1: a, **b}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'b'
'''),

('', 2, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x}'''),
r'''**ValueError("cannot put slice to MatchMapping after 'rest' element")**'''),

('', 2, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{**y}'''),
r'''**ValueError("cannot put slice to MatchMapping after 'rest' element")**'''),

('', 2, 2, None, {}, ('pattern',
r'''{1: a, **b}'''), ('pattern',
r'''{2: x, **y}'''),
r'''**ValueError("cannot put slice to MatchMapping after 'rest' element")**'''),
],

'MatchOr': [  # ................................................................................

('', 0, 0, None, {}, ('MatchOr',
r'''a | b'''), ('pattern',
r'''**DEL**'''),
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', 0, 1, None, {'_verify_self': False}, ('MatchOr',
r'''a | b'''), ('pattern',
r'''**DEL**'''),
r'''b''', r'''
MatchOr - ROOT 0,0..0,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'b'
'''),

('', 0, 2, None, {'_verify_self': False}, ('MatchOr',
r'''a | b'''), ('pattern',
r'''**DEL**'''),
r'''''',
r'''MatchOr - ROOT 0,0..0,0'''),

('', 0, 0, None, {'norm_self': True}, ('MatchOr',
r'''a | b'''), ('pattern',
r'''**DEL**'''),
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', 0, 1, None, {'norm_self': True}, ('MatchOr',
r'''a | b'''), ('pattern',
r'''**DEL**'''),
r'''b''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'b'
'''),

('', 0, 2, None, {'norm_self': True}, ('MatchOr',
r'''a | b'''), ('pattern',
r'''**DEL**'''),
r'''**ValueError('cannot delete all MatchOr.patterns without norm_self=False')**'''),

('', 1, 3, None, {'one': True}, ('pattern',
r'''a | b | c | d'''), ('pattern',
r'''x, y'''),
r'''a | [x, y] | d''', r'''
MatchOr - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchSequence - 0,4..0,10
     .patterns[2]
      0] MatchAs - 0,5..0,6
        .name 'x'
      1] MatchAs - 0,8..0,9
        .name 'y'
   2] MatchAs - 0,13..0,14
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchOr',
r'''a | b | c | d'''), ('MatchValue',
r'''1'''),
r'''a | 1 | d''', r'''
MatchOr - ROOT 0,0..0,9
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchValue - 0,4..0,5
     .value Constant 1 - 0,4..0,5
   2] MatchAs - 0,8..0,9
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchOr',
r'''a | b | c | d'''), ('MatchSingleton',
r'''True'''),
r'''a | True | d''', r'''
MatchOr - ROOT 0,0..0,12
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchSingleton True - 0,4..0,8
   2] MatchAs - 0,11..0,12
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchOr',
r'''a | b | c | d'''), ('MatchSequence',
r'''1, 2'''),
r'''a | [1, 2] | d''', r'''
MatchOr - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchSequence - 0,4..0,10
     .patterns[2]
      0] MatchValue - 0,5..0,6
        .value Constant 1 - 0,5..0,6
      1] MatchValue - 0,8..0,9
        .value Constant 2 - 0,8..0,9
   2] MatchAs - 0,13..0,14
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchOr',
r'''a | b | c | d'''), ('MatchMapping',
r'''{1: a}'''),
r'''a | {1: a} | d''', r'''
MatchOr - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchMapping - 0,4..0,10
     .keys[1]
      0] Constant 1 - 0,5..0,6
     .patterns[1]
      0] MatchAs - 0,8..0,9
        .name 'a'
   2] MatchAs - 0,13..0,14
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchOr',
r'''a | b | c | d'''), ('MatchClass',
r'''cls()'''),
r'''a | cls() | d''', r'''
MatchOr - ROOT 0,0..0,13
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchClass - 0,4..0,9
     .cls Name 'cls' Load - 0,4..0,7
   2] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchOr',
r'''a | b | c | d'''), ('MatchStar',
r'''*st'''),
r'''**ValueError('cannot put MatchStar as slice to MatchOr')**'''),

('', 1, 3, None, {}, ('MatchOr',
r'''a | b | c | d'''), ('MatchAs',
r'''x as y'''),
r'''a | (x as y) | d''', r'''
MatchOr - ROOT 0,0..0,16
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,5..0,11
     .pattern MatchAs - 0,5..0,6
       .name 'x'
     .name 'y'
   2] MatchAs - 0,15..0,16
     .name 'd'
'''),

('', 1, 3, None, {}, ('MatchOr',
r'''a | b | c | d'''), ('MatchOr',
r'''x | y'''),
r'''a | x | y | d''', r'''
MatchOr - ROOT 0,0..0,13
  .patterns[4]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'x'
   2] MatchAs - 0,8..0,9
     .name 'y'
   3] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False}, ('MatchOr',
r'''a | b | c | d'''), ('MatchValue',
r'''1'''),
r'''**ValueError("cannot put MatchValue as slice to MatchOr without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchOr',
r'''a | b | c | d'''), ('MatchSingleton',
r'''True'''),
r'''**ValueError("cannot put MatchSingleton as slice to MatchOr without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchOr',
r'''a | b | c | d'''), ('MatchSequence',
r'''1, 2'''),
r'''**ValueError("cannot put MatchSequence as slice to MatchOr without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchOr',
r'''a | b | c | d'''), ('MatchMapping',
r'''{1: a}'''),
r'''**ValueError("cannot put MatchMapping as slice to MatchOr without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchOr',
r'''a | b | c | d'''), ('MatchClass',
r'''cls()'''),
r'''**ValueError("cannot put MatchClass as slice to MatchOr without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchOr',
r'''a | b | c | d'''), ('MatchStar',
r'''*st'''),
r'''**ValueError('cannot put MatchStar as slice to MatchOr')**'''),

('', 1, 3, None, {'coerce': False}, ('MatchOr',
r'''a | b | c | d'''), ('MatchAs',
r'''x as y'''),
r'''**ValueError("cannot put MatchAs as slice to MatchOr without 'one=True' or 'coerce=True'")**'''),

('', 1, 3, None, {'coerce': False}, ('MatchOr',
r'''a | b | c | d'''), ('MatchOr',
r'''x | y'''),
r'''a | x | y | d''', r'''
MatchOr - ROOT 0,0..0,13
  .patterns[4]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'x'
   2] MatchAs - 0,8..0,9
     .name 'y'
   3] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchValue',
r'''1'''),
r'''a | 1 | d''', r'''
MatchOr - ROOT 0,0..0,9
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchValue - 0,4..0,5
     .value Constant 1 - 0,4..0,5
   2] MatchAs - 0,8..0,9
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchSingleton',
r'''True'''),
r'''a | True | d''', r'''
MatchOr - ROOT 0,0..0,12
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchSingleton True - 0,4..0,8
   2] MatchAs - 0,11..0,12
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchSequence',
r'''1, 2'''),
r'''a | [1, 2] | d''', r'''
MatchOr - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchSequence - 0,4..0,10
     .patterns[2]
      0] MatchValue - 0,5..0,6
        .value Constant 1 - 0,5..0,6
      1] MatchValue - 0,8..0,9
        .value Constant 2 - 0,8..0,9
   2] MatchAs - 0,13..0,14
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchMapping',
r'''{1: a}'''),
r'''a | {1: a} | d''', r'''
MatchOr - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchMapping - 0,4..0,10
     .keys[1]
      0] Constant 1 - 0,5..0,6
     .patterns[1]
      0] MatchAs - 0,8..0,9
        .name 'a'
   2] MatchAs - 0,13..0,14
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchClass',
r'''cls()'''),
r'''a | cls() | d''', r'''
MatchOr - ROOT 0,0..0,13
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchClass - 0,4..0,9
     .cls Name 'cls' Load - 0,4..0,7
   2] MatchAs - 0,12..0,13
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchStar',
r'''*st'''),
r'''**ValueError('cannot put MatchStar as slice to MatchOr')**'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchAs',
r'''x as y'''),
r'''a | (x as y) | d''', r'''
MatchOr - ROOT 0,0..0,16
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,5..0,11
     .pattern MatchAs - 0,5..0,6
       .name 'x'
     .name 'y'
   2] MatchAs - 0,15..0,16
     .name 'd'
'''),

('', 1, 3, None, {'coerce': False, 'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchOr',
r'''x | y'''),
r'''a | (x | y) | d''', r'''
MatchOr - ROOT 0,0..0,15
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchOr - 0,5..0,10
     .patterns[2]
      0] MatchAs - 0,5..0,6
        .name 'x'
      1] MatchAs - 0,9..0,10
        .name 'y'
   2] MatchAs - 0,14..0,15
     .name 'd'
'''),

('', 1, 3, None, {'one': True}, ('MatchOr',
r'''a | b | c | d'''), ('MatchOr',
r'''x | y'''),
r'''a | (x | y) | d''', r'''
MatchOr - ROOT 0,0..0,15
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchOr - 0,5..0,10
     .patterns[2]
      0] MatchAs - 0,5..0,6
        .name 'x'
      1] MatchAs - 0,9..0,10
        .name 'y'
   2] MatchAs - 0,14..0,15
     .name 'd'
'''),
],

'type_params': [  # ................................................................................

('body[0]', 0, 3, 'type_params', {'_ver': 13}, ('exec',
r'''def f[T, *U, **V](): pass'''), ('_type_params',
r'''**Z = ()'''),
r'''def f[**Z = ()](): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] FunctionDef - 0,0..0,23
     .name 'f'
     .body[1]
      0] Pass - 0,19..0,23
     .type_params[1]
      0] ParamSpec - 0,6..0,14
        .name 'Z'
        .default_value Tuple - 0,12..0,14
          .ctx Load
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T, *U, **V](): pass'''), (None,
r'''**DEL**'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''def f(): pass'''), ('_type_params',
r'''T, *U, **V'''),
r'''def f[T, *U, **V](): pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] FunctionDef - 0,0..0,25
     .name 'f'
     .body[1]
      0] Pass - 0,21..0,25
     .type_params[3]
      0] TypeVar - 0,6..0,7
        .name 'T'
      1] TypeVarTuple - 0,9..0,11
        .name 'U'
      2] ParamSpec - 0,13..0,16
        .name 'V'
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 13}, ('exec',
r'''async def f[T, *U, **V](): pass'''), ('_type_params',
r'''**Z = ()'''),
r'''async def f[**Z = ()](): pass''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncFunctionDef - 0,0..0,29
     .name 'f'
     .body[1]
      0] Pass - 0,25..0,29
     .type_params[1]
      0] ParamSpec - 0,12..0,20
        .name 'Z'
        .default_value Tuple - 0,18..0,20
          .ctx Load
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T, *U, **V](): pass'''), (None,
r'''**DEL**'''),
r'''async def f(): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] AsyncFunctionDef - 0,0..0,19
     .name 'f'
     .body[1]
      0] Pass - 0,15..0,19
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''async def f(): pass'''), ('_type_params',
r'''T, *U, **V'''),
r'''async def f[T, *U, **V](): pass''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] AsyncFunctionDef - 0,0..0,31
     .name 'f'
     .body[1]
      0] Pass - 0,27..0,31
     .type_params[3]
      0] TypeVar - 0,12..0,13
        .name 'T'
      1] TypeVarTuple - 0,15..0,17
        .name 'U'
      2] ParamSpec - 0,19..0,22
        .name 'V'
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 13}, ('exec',
r'''class cls[T, *U, **V]: pass'''), ('_type_params',
r'''**Z = ()'''),
r'''class cls[**Z = ()]: pass''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] ClassDef - 0,0..0,25
     .name 'cls'
     .body[1]
      0] Pass - 0,21..0,25
     .type_params[1]
      0] ParamSpec - 0,10..0,18
        .name 'Z'
        .default_value Tuple - 0,16..0,18
          .ctx Load
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''class cls[T, *U, **V]: pass'''), (None,
r'''**DEL**'''),
r'''class cls: pass''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] ClassDef - 0,0..0,15
     .name 'cls'
     .body[1]
      0] Pass - 0,11..0,15
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''class cls: pass'''), ('_type_params',
r'''T, *U, **V'''),
r'''class cls[T, *U, **V]: pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] ClassDef - 0,0..0,27
     .name 'cls'
     .body[1]
      0] Pass - 0,23..0,27
     .type_params[3]
      0] TypeVar - 0,10..0,11
        .name 'T'
      1] TypeVarTuple - 0,13..0,15
        .name 'U'
      2] ParamSpec - 0,17..0,20
        .name 'V'
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 13}, ('exec',
r'''type t[T, *U, **V] = ...'''), ('_type_params',
r'''**Z = ()'''),
r'''type t[**Z = ()] = ...''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] TypeAlias - 0,0..0,22
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] ParamSpec - 0,7..0,15
        .name 'Z'
        .default_value Tuple - 0,13..0,15
          .ctx Load
     .value Constant Ellipsis - 0,19..0,22
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T, *U, **V] = ...'''), (None,
r'''**DEL**'''),
r'''type t = ...''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] TypeAlias - 0,0..0,12
     .name Name 't' Store - 0,5..0,6
     .value Constant Ellipsis - 0,9..0,12
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''type t = ...'''), ('_type_params',
r'''T, *U, **V'''),
r'''type t[T, *U, **V] = ...''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] TypeAlias - 0,0..0,24
     .name Name 't' Store - 0,5..0,6
     .type_params[3]
      0] TypeVar - 0,7..0,8
        .name 'T'
      1] TypeVarTuple - 0,10..0,12
        .name 'U'
      2] ParamSpec - 0,14..0,17
        .name 'V'
     .value Constant Ellipsis - 0,21..0,24
'''),

('body[0]', 0, 0, 'type_params', {'_ver': 12}, ('exec',
r'''type t[**V]=...'''), ('_type_params',
r'''T'''),
r'''type t[T, **V]=...''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] TypeAlias - 0,0..0,18
     .name Name 't' Store - 0,5..0,6
     .type_params[2]
      0] TypeVar - 0,7..0,8
        .name 'T'
      1] ParamSpec - 0,10..0,13
        .name 'V'
     .value Constant Ellipsis - 0,15..0,18
'''),

('body[0]', 1, 1, 'type_params', {'_ver': 12}, ('exec',
r'''type t[**V]=...'''), ('_type_params',
r'''T'''),
r'''type t[**V, T]=...''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] TypeAlias - 0,0..0,18
     .name Name 't' Store - 0,5..0,6
     .type_params[2]
      0] ParamSpec - 0,7..0,10
        .name 'V'
      1] TypeVar - 0,12..0,13
        .name 'T'
     .value Constant Ellipsis - 0,15..0,18
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 13, 'one': True}, ('exec',
r'''type t[T, *U, **V] = ...'''), (None,
r'''*Z = ()'''),
r'''type t[*Z = ()] = ...''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] TypeAlias - 0,0..0,21
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVarTuple - 0,7..0,14
        .name 'Z'
        .default_value Tuple - 0,12..0,14
          .ctx Load
     .value Constant Ellipsis - 0,18..0,21
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12, 'one': True}, ('exec',
r'''type t[T, *U, **V] = ...'''), (None,
r'''X, *Y'''),
r'''type t[X, *Y] = ...''',
r'''**NodeError('expecting _type_params, got Tuple, could not coerce')**''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] TypeAlias - 0,0..0,19
     .name Name 't' Store - 0,5..0,6
     .type_params[2]
      0] TypeVar - 0,7..0,8
        .name 'X'
      1] TypeVarTuple - 0,10..0,12
        .name 'Y'
     .value Constant Ellipsis - 0,16..0,19
'''),

('body[0]', 0, 3, 'type_params', {'_ver': 12, 'one': True}, ('exec',
r'''type t[T, *U, **V] = ...'''), (None,
r'''X,'''),
r'''type t[X] = ...''',
r'''**NodeError('expecting _type_params, got Tuple, could not coerce')**''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] TypeAlias - 0,0..0,15
     .name Name 't' Store - 0,5..0,6
     .type_params[1]
      0] TypeVar - 0,7..0,8
        .name 'X'
     .value Constant Ellipsis - 0,12..0,15
'''),

('', 0, 3, 'type_params', {'_ver': 13}, ('_type_params',
r'''T, *U, **V'''), ('_type_params',
r'''**Z = ()'''),
r'''**Z = ()''', r'''
_type_params - ROOT 0,0..0,8
  .type_params[1]
   0] ParamSpec - 0,0..0,8
     .name 'Z'
     .default_value Tuple - 0,6..0,8
       .ctx Load
'''),

('', 0, 3, 'type_params', {'_ver': 12}, ('_type_params',
r'''T, *U, **V'''), (None,
r'''**DEL**'''),
r'''''',
r'''_type_params - ROOT 0,0..0,0'''),

('', 0, 3, 'type_params', {'_ver': 12}, ('_type_params',
r''''''), ('_type_params',
r'''T, *U, **V'''),
r'''T, *U, **V''', r'''
_type_params - ROOT 0,0..0,10
  .type_params[3]
   0] TypeVar - 0,0..0,1
     .name 'T'
   1] TypeVarTuple - 0,3..0,5
     .name 'U'
   2] ParamSpec - 0,7..0,10
     .name 'V'
'''),

('', 1, 1, 'type_params', {'_ver': 12}, (None,
r'''def f[T, *U, **V](): pass'''), ('_type_params',
r''''''),
r'''def f[T, *U, **V](): pass''', r'''
FunctionDef - ROOT 0,0..0,25
  .name 'f'
  .body[1]
   0] Pass - 0,21..0,25
  .type_params[3]
   0] TypeVar - 0,6..0,7
     .name 'T'
   1] TypeVarTuple - 0,9..0,11
     .name 'U'
   2] ParamSpec - 0,13..0,16
     .name 'V'
'''),
],

'type_params_coerce': [  # ................................................................................

('', 1, 3, 'type_params', {'one': True, '_ver': 12}, (None,
r'''type t[T, *U, **V] = ...'''), ('_type_params',
r'''X, **Y'''),
r'''type t[T, X, **Y] = ...''', r'''
TypeAlias - ROOT 0,0..0,23
  .name Name 't' Store - 0,5..0,6
  .type_params[3]
   0] TypeVar - 0,7..0,8
     .name 'T'
   1] TypeVar - 0,10..0,11
     .name 'X'
   2] ParamSpec - 0,13..0,16
     .name 'Y'
  .value Constant Ellipsis - 0,20..0,23
'''),

('', 1, 3, 'type_params', {'one': True, 'coerce': False, '_ver': 12}, (None,
r'''type t[T, *U, **V] = ...'''), ('_type_params',
r'''X, **Y'''),
r'''type t[T, X, **Y] = ...''',
r'''**ValueError("cannot put _type_params node as 'one=True' without 'coerce=True'")**''', r'''
TypeAlias - ROOT 0,0..0,23
  .name Name 't' Store - 0,5..0,6
  .type_params[3]
   0] TypeVar - 0,7..0,8
     .name 'T'
   1] TypeVar - 0,10..0,11
     .name 'X'
   2] ParamSpec - 0,13..0,16
     .name 'Y'
  .value Constant Ellipsis - 0,20..0,23
'''),

('', 1, 3, 'type_params', {'_ver': 12}, (None,
r'''type t[T, *U, **V] = ...'''), ('type_param',
r'''**X'''),
r'''type t[T, **X] = ...''', r'''
TypeAlias - ROOT 0,0..0,20
  .name Name 't' Store - 0,5..0,6
  .type_params[2]
   0] TypeVar - 0,7..0,8
     .name 'T'
   1] ParamSpec - 0,10..0,13
     .name 'X'
  .value Constant Ellipsis - 0,17..0,20
'''),

('', 1, 3, 'type_params', {'coerce': False, '_ver': 12}, (None,
r'''type t[T, *U, **V] = ...'''), ('type_param',
r'''**X'''),
r'''type t[T, **X] = ...''',
r'''**NodeError('expecting _type_params, got ParamSpec')**''', r'''
TypeAlias - ROOT 0,0..0,20
  .name Name 't' Store - 0,5..0,6
  .type_params[2]
   0] TypeVar - 0,7..0,8
     .name 'T'
   1] ParamSpec - 0,10..0,13
     .name 'X'
  .value Constant Ellipsis - 0,17..0,20
'''),

('', 1, 3, 'type_params', {'coerce': False, 'one': True, '_ver': 12}, (None,
r'''type t[T, *U, **V] = ...'''), ('type_param',
r'''**X'''),
r'''type t[T, **X] = ...''', r'''
TypeAlias - ROOT 0,0..0,20
  .name Name 't' Store - 0,5..0,6
  .type_params[2]
   0] TypeVar - 0,7..0,8
     .name 'T'
   1] ParamSpec - 0,10..0,13
     .name 'X'
  .value Constant Ellipsis - 0,17..0,20
'''),

('', 1, 3, 'type_params', {'one': True, '_ver': 12}, ('_type_params',
r'''T, *U, **V'''), ('_type_params',
r'''X, **Y'''),
r'''T, X, **Y''', r'''
_type_params - ROOT 0,0..0,9
  .type_params[3]
   0] TypeVar - 0,0..0,1
     .name 'T'
   1] TypeVar - 0,3..0,4
     .name 'X'
   2] ParamSpec - 0,6..0,9
     .name 'Y'
'''),

('', 1, 3, 'type_params', {'one': True, 'coerce': False, '_ver': 12}, ('_type_params',
r'''T, *U, **V'''), ('_type_params',
r'''X, **Y'''),
r'''T, X, **Y''',
r'''**ValueError("cannot put _type_params node as 'one=True' without 'coerce=True'")**''', r'''
_type_params - ROOT 0,0..0,9
  .type_params[3]
   0] TypeVar - 0,0..0,1
     .name 'T'
   1] TypeVar - 0,3..0,4
     .name 'X'
   2] ParamSpec - 0,6..0,9
     .name 'Y'
'''),

('', 1, 3, 'type_params', {'_ver': 12}, ('_type_params',
r'''T, *U, **V'''), ('type_param',
r'''**X'''),
r'''T, **X''', r'''
_type_params - ROOT 0,0..0,6
  .type_params[2]
   0] TypeVar - 0,0..0,1
     .name 'T'
   1] ParamSpec - 0,3..0,6
     .name 'X'
'''),

('', 1, 3, 'type_params', {'coerce': False, '_ver': 12}, ('_type_params',
r'''T, *U, **V'''), ('type_param',
r'''**X'''),
r'''T, **X''',
r'''**NodeError('expecting _type_params, got ParamSpec')**''', r'''
_type_params - ROOT 0,0..0,6
  .type_params[2]
   0] TypeVar - 0,0..0,1
     .name 'T'
   1] ParamSpec - 0,3..0,6
     .name 'X'
'''),

('', 1, 3, 'type_params', {'coerce': False, 'one': True, '_ver': 12}, ('_type_params',
r'''T, *U, **V'''), ('type_param',
r'''**X'''),
r'''T, **X''', r'''
_type_params - ROOT 0,0..0,6
  .type_params[2]
   0] TypeVar - 0,0..0,1
     .name 'T'
   1] ParamSpec - 0,3..0,6
     .name 'X'
'''),
],

'virtual_field__all': [  # ................................................................................

('', 1, 2, '_all', {}, ('Dict',
r'''{1: a, 2: b, 3: c}'''), ('Dict',
r'''{4: x, 5: y}'''),
r'''{1: a, 4: x, 5: y, 3: c}''', r'''
Dict - ROOT 0,0..0,24
  .keys[4]
   0] Constant 1 - 0,1..0,2
   1] Constant 4 - 0,7..0,8
   2] Constant 5 - 0,13..0,14
   3] Constant 3 - 0,19..0,20
  .values[4]
   0] Name 'a' Load - 0,4..0,5
   1] Name 'x' Load - 0,10..0,11
   2] Name 'y' Load - 0,16..0,17
   3] Name 'c' Load - 0,22..0,23
'''),

('', 1, 2, '_all', {}, ('Dict',
r'''{1: a, 2: b, 3: c}'''), ('Dict',
r'''a'''),
r'''**NodeError('slice being assigned to a Dict must be a Dict, not a Name')**'''),

('', 1, 2, '_all', {}, ('MatchMapping',
r'''{1: a, 2: b, 3: c}'''), ('MatchMapping',
r'''{4: x, 5: y}'''),
r'''{1: a, 4: x, 5: y, 3: c}''', r'''
MatchMapping - ROOT 0,0..0,24
  .keys[4]
   0] Constant 1 - 0,1..0,2
   1] Constant 4 - 0,7..0,8
   2] Constant 5 - 0,13..0,14
   3] Constant 3 - 0,19..0,20
  .patterns[4]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'x'
   2] MatchAs - 0,16..0,17
     .name 'y'
   3] MatchAs - 0,22..0,23
     .name 'c'
'''),

('', 1, 2, '_all', {}, ('MatchMapping',
r'''{1: a, 2: b, 3: c}'''), ('MatchMapping',
r'''a'''),
r'''**NodeError('slice being assigned to a MatchMapping must be a MatchMapping, not a MatchAs')**'''),

('', 1, 2, '_all', {}, ('Compare',
r'''a < b > c'''), ('Compare',
r'''x != y'''),
r'''a < x != y > c''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,0..0,1
  .ops[3]
   0] Lt - 0,2..0,3
   1] NotEq - 0,6..0,8
   2] Gt - 0,11..0,12
  .comparators[3]
   0] Name 'x' Load - 0,4..0,5
   1] Name 'y' Load - 0,9..0,10
   2] Name 'c' Load - 0,13..0,14
'''),
],

'virtual_field__body': [  # ................................................................................

('', 0, 'end', '_body', {}, ('Module', r'''
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

('', 0, 'end', '_body', {'_verify': False}, ('Interactive',
r'''"""non-doc"""; a; b'''),
r'''x''',
r'''x''', r'''
Interactive - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'x' Load - 0,0..0,1
'''),

('', 0, 'end', '_body', {}, ('FunctionDef', r'''
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

('', 0, 'end', '_body', {}, ('AsyncFunctionDef', r'''
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

('', 0, 'end', '_body', {}, ('ClassDef', r'''
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

('', 0, 'end', '_body', {}, ('For', r'''
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

('', 0, 'end', '_body', {}, ('AsyncFor', r'''
async for _ in _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
async for _ in _:
    x
''', r'''
AsyncFor - ROOT 0,0..1,5
  .target Name '_' Store - 0,10..0,11
  .iter Name '_' Load - 0,15..0,16
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
'''),

('', 0, 'end', '_body', {}, ('While', r'''
while _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
while _:
    x
''', r'''
While - ROOT 0,0..1,5
  .test Name '_' Load - 0,6..0,7
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
'''),

('', 0, 'end', '_body', {}, ('If', r'''
if _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
if _:
    x
''', r'''
If - ROOT 0,0..1,5
  .test Name '_' Load - 0,3..0,4
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
'''),

('', 0, 'end', '_body', {}, ('With', r'''
with _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
with _:
    x
''', r'''
With - ROOT 0,0..1,5
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name '_' Load - 0,5..0,6
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
'''),

('', 0, 'end', '_body', {}, ('AsyncWith', r'''
async with _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
async with _:
    x
''', r'''
AsyncWith - ROOT 0,0..1,5
  .items[1]
   0] withitem - 0,11..0,12
     .context_expr Name '_' Load - 0,11..0,12
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
'''),

('', 0, 'end', '_body', {}, ('Try', r'''
try:
    """non-doc"""
    a
    b
except: pass
'''),
r'''x''', r'''
try:
    x
except: pass
''', r'''
Try - ROOT 0,0..2,12
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
  .handlers[1]
   0] ExceptHandler - 2,0..2,12
     .body[1]
      0] Pass - 2,8..2,12
'''),

('', 0, 'end', '_body', {'_ver': 11}, ('TryStar', r'''
try:
    """non-doc"""
    a
    b
except* Exception: pass
'''),
r'''x''', r'''
try:
    x
except* Exception: pass
''', r'''
TryStar - ROOT 0,0..2,23
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
  .handlers[1]
   0] ExceptHandler - 2,0..2,23
     .type Name 'Exception' Load - 2,8..2,17
     .body[1]
      0] Pass - 2,19..2,23
'''),

('', 0, 'end', '_body', {}, ('ExceptHandler', r'''
except:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
except:
    x
''', r'''
ExceptHandler - ROOT 0,0..1,5
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
'''),

('', 0, 'end', '_body', {}, ('match_case', r'''
case _:
    """non-doc"""
    a
    b
'''),
r'''x''', r'''
case _:
    x
''', r'''
match_case - ROOT 0,0..1,5
  .pattern MatchAs - 0,5..0,6
  .body[1]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
'''),

('', 0, 1, '_body', {'trivia': False}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''),
r'''x''', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    x
''', r'''
FunctionDef - ROOT 0,0..6,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 6,4..6,5
     .value Name 'x' Load - 6,4..6,5
'''),

('', 0, 1, '_body', {'trivia': 'block'}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''),
r'''x''', r'''
def f():
    """doc"""

    # pre-2

    x
''', r'''
FunctionDef - ROOT 0,0..5,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 5,4..5,5
     .value Name 'x' Load - 5,4..5,5
'''),

('', 0, 1, '_body', {'trivia': 'block+'}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''),
r'''x''', r'''
def f():
    """doc"""

    # pre-2
    x
''', r'''
FunctionDef - ROOT 0,0..4,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 4,4..4,5
     .value Name 'x' Load - 4,4..4,5
'''),

('', 0, 1, '_body', {'trivia': 'all'}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''),
r'''x''', r'''
def f():
    """doc"""

    x
''', r'''
FunctionDef - ROOT 0,0..3,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 3,4..3,5
     .value Name 'x' Load - 3,4..3,5
'''),

('', 0, 1, '_body', {'trivia': 'all+'}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
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
],

'raw': [  # ................................................................................

('', 0, 1, None, {'raw': True}, (None,
r'''(a,)'''), (None,
r'''x'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 1, None, {'raw': True}, (None,
r'''(a,)'''), (None,
r'''x,'''),
r'''**ParseError('invalid syntax')**'''),

('', 0, 2, None, {'raw': True}, (None,
r'''(a, b)'''), (None,
r'''x'''),
r'''(x)''',
r'''Name 'x' Load - ROOT 0,1..0,2'''),

('', 0, 2, None, {'raw': True}, (None,
r'''(a, b)'''), (None,
r'''x,'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 1, None, {'raw': True}, (None,
r'''[a]'''), (None,
r'''x'''),
r'''[x]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 1, None, {'raw': True}, (None,
r'''[a]'''), (None,
r'''x,'''),
r'''[x,]''', r'''
List - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 1, None, {'raw': True}, (None,
r'''[a,]'''), (None,
r'''x'''),
r'''[x,]''', r'''
List - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 1, None, {'raw': True}, (None,
r'''[a,]'''), (None,
r'''x,'''),
r'''**ParseError('invalid syntax')**'''),

('', 0, 2, None, {'raw': True}, (None,
r'''[a, b]'''), (None,
r'''x'''),
r'''[x]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 2, None, {'raw': True}, (None,
r'''[a, b]'''), (None,
r'''x,'''),
r'''[x,]''', r'''
List - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''x, y'''),
r'''(a, x, y, c)''', r'''
Tuple - ROOT 0,0..0,12
  .elts[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 0,4..0,5
   2] Name 'y' Load - 0,7..0,8
   3] Name 'c' Load - 0,10..0,11
  .ctx Load
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''x, y,'''),
r'''**ParseError('invalid syntax')**'''),

('', 1, 2, None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''[x, y]'''),
r'''(a, [x, y], c)''', r'''
Tuple - ROOT 0,0..0,14
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] List - 0,4..0,10
     .elts[2]
      0] Name 'x' Load - 0,5..0,6
      1] Name 'y' Load - 0,8..0,9
     .ctx Load
   2] Name 'c' Load - 0,12..0,13
  .ctx Load
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''[x, y,]'''),
r'''(a, [x, y,], c)''', r'''
Tuple - ROOT 0,0..0,15
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] List - 0,4..0,11
     .elts[2]
      0] Name 'x' Load - 0,5..0,6
      1] Name 'y' Load - 0,8..0,9
     .ctx Load
   2] Name 'c' Load - 0,13..0,14
  .ctx Load
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''{x, y}'''),
r'''(a, {x, y}, c)''', r'''
Tuple - ROOT 0,0..0,14
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Set - 0,4..0,10
     .elts[2]
      0] Name 'x' Load - 0,5..0,6
      1] Name 'y' Load - 0,8..0,9
   2] Name 'c' Load - 0,12..0,13
  .ctx Load
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''{x, y,}'''),
r'''(a, {x, y,}, c)''', r'''
Tuple - ROOT 0,0..0,15
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Set - 0,4..0,11
     .elts[2]
      0] Name 'x' Load - 0,5..0,6
      1] Name 'y' Load - 0,8..0,9
   2] Name 'c' Load - 0,13..0,14
  .ctx Load
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''x,'''),
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''(x,)'''),
r'''((x,))''', r'''
Tuple - ROOT 0,1..0,5
  .elts[1]
   0] Name 'x' Load - 0,2..0,3
  .ctx Load
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''[x]'''),
r'''([x])''', r'''
List - ROOT 0,1..0,4
  .elts[1]
   0] Name 'x' Load - 0,2..0,3
  .ctx Load
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''(a, b, c)'''), (None,
r'''[x,]'''),
r'''([x,])''', r'''
List - ROOT 0,1..0,5
  .elts[1]
   0] Name 'x' Load - 0,2..0,3
  .ctx Load
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''[a, b, c]'''), (None,
r'''x,'''),
r'''[x,]''', r'''
List - ROOT 0,0..0,4
  .elts[1]
   0] Name 'x' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''[a, b, c]'''), (None,
r'''(x,)'''),
r'''[(x,)]''', r'''
List - ROOT 0,0..0,6
  .elts[1]
   0] Tuple - 0,1..0,5
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''[a, b, c]'''), (None,
r'''[x]'''),
r'''[[x]]''', r'''
List - ROOT 0,0..0,5
  .elts[1]
   0] List - 0,1..0,4
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''[a, b, c]'''), (None,
r'''[x,]'''),
r'''[[x,]]''', r'''
List - ROOT 0,0..0,6
  .elts[1]
   0] List - 0,1..0,5
     .elts[1]
      0] Name 'x' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''{a: b, c: d, e: f}'''), (None,
r'''x: y'''),
r'''{a: b, x: y, e: f}''', r'''
Dict - ROOT 0,0..0,18
  .keys[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 0,7..0,8
   2] Name 'e' Load - 0,13..0,14
  .values[3]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'y' Load - 0,10..0,11
   2] Name 'f' Load - 0,16..0,17
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''{a: b, c: d, e: f}'''), (None,
r'''**z'''),
r'''{a: b, **z, e: f}''', r'''
Dict - ROOT 0,0..0,17
  .keys[3]
   0] Name 'a' Load - 0,1..0,2
   1] None
   2] Name 'e' Load - 0,12..0,13
  .values[3]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'z' Load - 0,9..0,10
   2] Name 'f' Load - 0,15..0,16
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''{a: b, c: d, e: f}'''), (None,
r'''**z,'''),
r'''{**z,}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] None
  .values[1]
   0] Name 'z' Load - 0,3..0,4
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''{a: b, c: d, e: f}'''), (None,
r''''''),
r'''{}''',
r'''Dict - ROOT 0,0..0,2'''),

('', 1, 2, None, {'raw': True}, ('pattern',
r'''{1: b, 3: d, 5: f}'''), (None,
r'''7: y'''),
r'''{1: b, 7: y, 5: f}''', r'''
MatchMapping - ROOT 0,0..0,18
  .keys[3]
   0] Constant 1 - 0,1..0,2
   1] Constant 7 - 0,7..0,8
   2] Constant 5 - 0,13..0,14
  .patterns[3]
   0] MatchAs - 0,4..0,5
     .name 'b'
   1] MatchAs - 0,10..0,11
     .name 'y'
   2] MatchAs - 0,16..0,17
     .name 'f'
'''),

('', 1, 2, None, {'raw': True}, ('pattern',
r'''{1: b, 3: d, 5: f}'''), (None,
r'''**z'''),
r'''{1: b, **z, 5: f}''', r'''
Dict - ROOT 0,0..0,17
  .keys[3]
   0] Constant 1 - 0,1..0,2
   1] None
   2] Constant 5 - 0,12..0,13
  .values[3]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'z' Load - 0,9..0,10
   2] Name 'f' Load - 0,15..0,16
'''),

('pattern', 1, 2, None, {'raw': True}, ('match_case',
r'''case {1: b, 3: d, 5: f}: pass'''), (None,
r'''**z'''),
r'''**SyntaxError('invalid syntax')**'''),

('pattern', 1, 2, None, {'raw': True}, ('match_case',
r'''case {1: b, 3: d, 5: f}: pass'''), (None,
r'''7: h'''),
r'''case {1: b, 7: h, 5: f}: pass''', r'''
match_case - ROOT 0,0..0,29
  .pattern MatchMapping - 0,5..0,23
    .keys[3]
     0] Constant 1 - 0,6..0,7
     1] Constant 7 - 0,12..0,13
     2] Constant 5 - 0,18..0,19
    .patterns[3]
     0] MatchAs - 0,9..0,10
       .name 'b'
     1] MatchAs - 0,15..0,16
       .name 'h'
     2] MatchAs - 0,21..0,22
       .name 'f'
  .body[1]
   0] Pass - 0,25..0,29
'''),

('pattern', 1, 2, None, {'raw': True}, ('match_case', r'''

case {1: b, 3: d, 5: f}: pass
'''), (None,
r'''7: h'''), r'''

case {1: b, 7: h, 5: f}: pass
''', r'''
match_case - ROOT 1,0..1,29
  .pattern MatchMapping - 1,5..1,23
    .keys[3]
     0] Constant 1 - 1,6..1,7
     1] Constant 7 - 1,12..1,13
     2] Constant 5 - 1,18..1,19
    .patterns[3]
     0] MatchAs - 1,9..1,10
       .name 'b'
     1] MatchAs - 1,15..1,16
       .name 'h'
     2] MatchAs - 1,21..1,22
       .name 'f'
  .body[1]
   0] Pass - 1,25..1,29
'''),

('', 2, 3, None, {'raw': True}, ('pattern',
r'''{1: b, 3: d, 5: f}'''), (None,
r'''**z'''),
r'''{1: b, 3: d, **z}''', r'''
MatchMapping - ROOT 0,0..0,17
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 3 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'b'
   1] MatchAs - 0,10..0,11
     .name 'd'
  .rest 'z'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''{1: b, 3: d, 5: f}'''), (None,
r'''**z'''),
r'''{**z}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'z'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''{1: b, 3: d, 5: f}'''), (None,
r'''**z,'''),
r'''{**z,}''', r'''
MatchMapping - ROOT 0,0..0,6
  .rest 'z'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''{1: b, 3: d, 5: f}'''), (None,
r''''''),
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''{1: b, 3: d, **f}'''), (None,
r'''7: y'''),
r'''{7: y}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 7 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'y'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''{1: b, 3: d, **f}'''), (None,
r'''**z'''),
r'''{**z}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'z'
'''),

('', 0, 1, None, {'raw': True}, ('pattern',
r'''{1: b, **f}'''), (None,
r'''7: y'''),
r'''{7: y, **f}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 7 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'y'
  .rest 'f'
'''),

('', 1, 2, None, {'raw': True}, ('pattern',
r'''{1: b, **f}'''), (None,
r'''7: y'''),
r'''{1: b, 7: y}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 7 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'b'
   1] MatchAs - 0,10..0,11
     .name 'y'
'''),

('', 0, 1, None, {'raw': True}, ('pattern',
r'''{1: b, **f}'''), (None,
r'''**z'''),
r'''{**z, **f}''', r'''
Dict - ROOT 0,0..0,10
  .keys[2]
   0] None
   1] None
  .values[2]
   0] Name 'z' Load - 0,3..0,4
   1] Name 'f' Load - 0,8..0,9
'''),

('', 1, 2, None, {'raw': True}, ('pattern',
r'''{1: b, **f}'''), (None,
r'''**z'''),
r'''{1: b, **z}''', r'''
MatchMapping - ROOT 0,0..0,11
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'b'
  .rest 'z'
'''),

('', 0, 1, None, {'raw': True}, ('pattern',
r'''{**f}'''), (None,
r'''**z'''),
r'''{**z}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'z'
'''),

('', 1, 2, None, {'raw': True}, ('pattern',
r'''[a, b, c]'''), (None,
r'''x, y'''),
r'''[a, x, y, c]''', r'''
MatchSequence - ROOT 0,0..0,12
  .patterns[4]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'x'
   2] MatchAs - 0,7..0,8
     .name 'y'
   3] MatchAs - 0,10..0,11
     .name 'c'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''[a, b, c]'''), (None,
r'''z,'''),
r'''[z,]''', r'''
MatchSequence - ROOT 0,0..0,4
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'z'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''[a, b, c]'''), (None,
r''''''),
r'''[]''',
r'''MatchSequence - ROOT 0,0..0,2'''),

('', 1, 2, None, {'raw': True}, ('pattern',
r'''a | b | c'''), (None,
r'''x | y'''),
r'''a | x | y | c''', r'''
MatchOr - ROOT 0,0..0,13
  .patterns[4]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'x'
   2] MatchAs - 0,8..0,9
     .name 'y'
   3] MatchAs - 0,12..0,13
     .name 'c'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''a | b | c'''), (None,
r'''x | y'''),
r'''x | y''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'x'
   1] MatchAs - 0,4..0,5
     .name 'y'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''a | b | c'''), (None,
r'''x'''),
r'''x''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'x'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''a | b | c'''), (None,
r''''''),
r'''''',
r'''Module - ROOT 0,0..0,0'''),

('', 1, 2, None, {'raw': True}, ('pattern',
r'''cls(a, b, c)'''), (None,
r'''x, y'''),
r'''cls(a, x, y, c)''', r'''
MatchClass - ROOT 0,0..0,15
  .cls Name 'cls' Load - 0,0..0,3
  .patterns[4]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,7..0,8
     .name 'x'
   2] MatchAs - 0,10..0,11
     .name 'y'
   3] MatchAs - 0,13..0,14
     .name 'c'
'''),

('', 1, 2, None, {'raw': True}, ('pattern',
r'''cls(a, b, c)'''), (None,
r'''z=1'''),
r'''**ParseError('invalid syntax')**'''),

('', 2, 3, None, {'raw': True}, ('pattern',
r'''cls(a, b, c)'''), (None,
r'''z=1'''),
r'''cls(a, b, z=1)''', r'''
MatchClass - ROOT 0,0..0,14
  .cls Name 'cls' Load - 0,0..0,3
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,7..0,8
     .name 'b'
  .kwd_attrs[1]
   0] 'z'
  .kwd_patterns[1]
   0] MatchValue - 0,12..0,13
     .value Constant 1 - 0,12..0,13
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''cls(a, b, c)'''), (None,
r'''x, y'''),
r'''cls(x, y)''', r'''
MatchClass - ROOT 0,0..0,9
  .cls Name 'cls' Load - 0,0..0,3
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'x'
   1] MatchAs - 0,7..0,8
     .name 'y'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''cls(a, b, c)'''), (None,
r'''z,'''),
r'''cls(z,)''', r'''
MatchClass - ROOT 0,0..0,7
  .cls Name 'cls' Load - 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'z'
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''cls(a, b, c)'''), (None,
r'''z=1'''),
r'''cls(z=1)''', r'''
MatchClass - ROOT 0,0..0,8
  .cls Name 'cls' Load - 0,0..0,3
  .kwd_attrs[1]
   0] 'z'
  .kwd_patterns[1]
   0] MatchValue - 0,6..0,7
     .value Constant 1 - 0,6..0,7
'''),

('', 0, 'end', None, {'raw': True}, ('pattern',
r'''cls(a, b, c)'''), (None,
r''''''),
r'''cls()''', r'''
MatchClass - ROOT 0,0..0,5
  .cls Name 'cls' Load - 0,0..0,3
'''),

('', 1, 2, 'bases', {'raw': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''x, y'''),
r'''class cls(a, x, y, c): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[4]
   0] Name 'a' Load - 0,10..0,11
   1] Name 'x' Load - 0,13..0,14
   2] Name 'y' Load - 0,16..0,17
   3] Name 'c' Load - 0,19..0,20
  .body[1]
   0] Pass - 0,23..0,27
'''),

('', 1, 2, 'bases', {'raw': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''**z'''),
r'''**SyntaxError('positional argument follows keyword argument unpacking')**'''),

('', 1, 2, 'bases', {'raw': True}, (None,
r'''class cls(a, b, *c): pass'''), (None,
r'''**z'''),
r'''**SyntaxError('iterable argument unpacking follows keyword argument unpacking')**'''),

('', 1, 2, 'bases', {'raw': True}, (None,
r'''class cls(a, b, *c): pass'''), (None,
r'''u=v'''),
r'''class cls(a, u=v, *c): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'c' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'u'
     .value Name 'v' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,23..0,27
'''),

('', 2, 3, 'bases', {'raw': True}, (None,
r'''class cls(a, b, c): pass'''), (None,
r'''**z'''),
r'''class cls(a, b, **z): pass''', r'''
ClassDef - ROOT 0,0..0,26
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Name 'b' Load - 0,13..0,14
  .keywords[1]
   0] keyword - 0,16..0,19
     .value Name 'z' Load - 0,18..0,19
  .body[1]
   0] Pass - 0,22..0,26
'''),

('', 0, 'end', 'bases', {'raw': True}, (None,
r'''class cls(a, u=v, *b): pass'''), (None,
r'''x, y'''),
r'''class cls(x, y): pass''', r'''
ClassDef - ROOT 0,0..0,21
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Name 'y' Load - 0,13..0,14
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', 1, 2, 'args', {'raw': True}, (None,
r'''call(a, b, c)'''), (None,
r'''x, y'''),
r'''call(a, x, y, c)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .args[4]
   0] Name 'a' Load - 0,5..0,6
   1] Name 'x' Load - 0,8..0,9
   2] Name 'y' Load - 0,11..0,12
   3] Name 'c' Load - 0,14..0,15
'''),

('', 1, 2, 'args', {'raw': True}, (None,
r'''call(a, b, c)'''), (None,
r'''**z'''),
r'''**ParseError('invalid syntax')**'''),

('', 1, 2, 'args', {'raw': True}, (None,
r'''call(a, b, *c)'''), (None,
r'''**z'''),
r'''**ParseError('invalid syntax')**'''),

('', 1, 2, 'args', {'raw': True}, (None,
r'''call(a, b, *c)'''), (None,
r'''u=v'''),
r'''call(a, u=v, *c)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'c' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'u'
     .value Name 'v' Load - 0,10..0,11
'''),

('', 2, 3, 'args', {'raw': True}, (None,
r'''call(a, b, c)'''), (None,
r'''**z'''),
r'''call(a, b, **z)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Name 'b' Load - 0,8..0,9
  .keywords[1]
   0] keyword - 0,11..0,14
     .value Name 'z' Load - 0,13..0,14
'''),

('', 0, 'end', 'args', {'raw': True}, (None,
r'''call(a, u=v, *b)'''), (None,
r'''x, y'''),
r'''call(x, y)''', r'''
Call - ROOT 0,0..0,10
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'x' Load - 0,5..0,6
   1] Name 'y' Load - 0,8..0,9
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''del a, b, c'''), (None,
r'''x, y'''),
r'''del a, x, y, c''', r'''
Delete - ROOT 0,0..0,14
  .targets[4]
   0] Name 'a' Del - 0,4..0,5
   1] Name 'x' Del - 0,7..0,8
   2] Name 'y' Del - 0,10..0,11
   3] Name 'c' Del - 0,13..0,14
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''del a, b, c'''), (None,
r'''x, y'''),
r'''del x, y''', r'''
Delete - ROOT 0,0..0,8
  .targets[2]
   0] Name 'x' Del - 0,4..0,5
   1] Name 'y' Del - 0,7..0,8
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''del a, b, c'''), (None,
r'''x, y,'''),
r'''del x, y,''', r'''
Delete - ROOT 0,0..0,9
  .targets[2]
   0] Name 'x' Del - 0,4..0,5
   1] Name 'y' Del - 0,7..0,8
'''),

('', 1, 2, 'targets', {'raw': True}, (None,
r'''a = b = c = d'''), (None,
r'''x = y'''),
r'''a = x = y = c = d''', r'''
Assign - ROOT 0,0..0,17
  .targets[4]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
   2] Name 'y' Store - 0,8..0,9
   3] Name 'c' Store - 0,12..0,13
  .value Name 'd' Load - 0,16..0,17
'''),

('', 0, 'end', 'targets', {'raw': True}, (None,
r'''a = b = c = d'''), (None,
r'''x = y'''),
r'''x = y = d''', r'''
Assign - ROOT 0,0..0,9
  .targets[2]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'y' Store - 0,4..0,5
  .value Name 'd' Load - 0,8..0,9
'''),

('', 1, 2, 'decorator_list', {'raw': True}, (None, r'''
@a
@b
@c
class cls: pass
'''), (None, r'''
@x
@y
'''), r'''
@a
@x
@y
@c
class cls: pass
''', r'''
ClassDef - ROOT 4,0..4,15
  .name 'cls'
  .body[1]
   0] Pass - 4,11..4,15
  .decorator_list[4]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'x' Load - 1,1..1,2
   2] Name 'y' Load - 2,1..2,2
   3] Name 'c' Load - 3,1..3,2
'''),

('', 0, 'end', 'decorator_list', {'raw': True}, (None, r'''
@a
@b
@c
class cls: pass
'''), (None, r'''
@x
@y
'''), r'''
@x
@y
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'y' Load - 1,1..1,2
'''),

('', 1, 2, None, {'raw': True}, (None,
r'''global a, b, c'''), (None,
r'''x, y'''),
r'''global a, x, y, c''', r'''
Global - ROOT 0,0..0,17
  .names[4]
   0] 'a'
   1] 'x'
   2] 'y'
   3] 'c'
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''global a, b, c'''), (None,
r'''x, y'''),
r'''global x, y''', r'''
Global - ROOT 0,0..0,11
  .names[2]
   0] 'x'
   1] 'y'
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''global a, b, c'''), (None,
r'''x, y,'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 1, 2, None, {'raw': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x, y'''),
r'''nonlocal a, x, y, c''', r'''
Nonlocal - ROOT 0,0..0,19
  .names[4]
   0] 'a'
   1] 'x'
   2] 'y'
   3] 'c'
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x, y'''),
r'''nonlocal x, y''', r'''
Nonlocal - ROOT 0,0..0,13
  .names[2]
   0] 'x'
   1] 'y'
'''),

('', 0, 'end', None, {'raw': True}, (None,
r'''nonlocal a, b, c'''), (None,
r'''x, y,'''),
r'''**SyntaxError('invalid syntax')**'''),

('', 1, 2, 'generators', {'raw': True}, (None,
r'''[_ for a in a for b in b for c in c]'''), (None,
r'''for x in x for y in y'''),
r'''[_ for a in a for x in x for y in y for c in c]''', r'''
ListComp - ROOT 0,0..0,47
  .elt Name '_' Load - 0,1..0,2
  .generators[4]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'x' Store - 0,18..0,19
     .iter Name 'x' Load - 0,23..0,24
     .is_async 0
   2] comprehension - 0,25..0,35
     .target Name 'y' Store - 0,29..0,30
     .iter Name 'y' Load - 0,34..0,35
     .is_async 0
   3] comprehension - 0,36..0,46
     .target Name 'c' Store - 0,40..0,41
     .iter Name 'c' Load - 0,45..0,46
     .is_async 0
'''),

('', 0, 'end', 'generators', {'raw': True}, (None,
r'''[_ for a in a for b in b for c in c]'''), (None,
r'''for x in x for y in y'''),
r'''[_ for x in x for y in y]''', r'''
ListComp - ROOT 0,0..0,25
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..0,13
     .target Name 'x' Store - 0,7..0,8
     .iter Name 'x' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'y' Store - 0,18..0,19
     .iter Name 'y' Load - 0,23..0,24
     .is_async 0
'''),

('', 1, 2, 'ifs', {'raw': True}, (None,
r'''for _ in _ if a if b if c'''), (None,
r'''if x if y'''),
r'''for _ in _ if a if x if y if c''', r'''
comprehension - ROOT 0,0..0,30
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[4]
   0] Name 'a' Load - 0,14..0,15
   1] Name 'x' Load - 0,19..0,20
   2] Name 'y' Load - 0,24..0,25
   3] Name 'c' Load - 0,29..0,30
  .is_async 0
'''),

('', 0, 'end', 'ifs', {'raw': True}, (None,
r'''for _ in _ if a if b if c'''), (None,
r'''if x if y'''),
r'''for _ in _ if x if y''', r'''
comprehension - ROOT 0,0..0,20
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .ifs[2]
   0] Name 'x' Load - 0,14..0,15
   1] Name 'y' Load - 0,19..0,20
  .is_async 0
'''),
],

'raw_SPECIAL_SLICE': [  # ................................................................................

('', 1, 2, None, {'raw': True}, ('_ExceptHandlers', r'''
except ValueError as a: pass
except RuntimeError as b: pass
except IndexError as c: pass
'''), (None,
r'''except: pass'''), r'''
except ValueError as a: pass
except: pass
except IndexError as c: pass
''', r'''
_ExceptHandlers - ROOT 0,0..2,28
  .handlers[3]
   0] ExceptHandler - 0,0..0,28
     .type Name 'ValueError' Load - 0,7..0,17
     .name 'a'
     .body[1]
      0] Pass - 0,24..0,28
   1] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
   2] ExceptHandler - 2,0..2,28
     .type Name 'IndexError' Load - 2,7..2,17
     .name 'c'
     .body[1]
      0] Pass - 2,24..2,28
'''),

('', 0, 'end', None, {'raw': True}, ('_ExceptHandlers', r'''
except ValueError as a: pass
except RuntimeError as b: pass
except IndexError as c: pass
'''), (None,
r'''except: pass'''),
r'''except: pass''', r'''
_ExceptHandlers - ROOT 0,0..0,12
  .handlers[1]
   0] ExceptHandler - 0,0..0,12
     .body[1]
      0] Pass - 0,8..0,12
'''),

('', 1, 2, None, {'raw': True}, ('_match_cases', r'''
case 1: pass
case cls(a, b=c): pass
case _: pass
'''), (None,
r'''case True: pass'''), r'''
case 1: pass
case True: pass
case _: pass
''', r'''
_match_cases - ROOT 0,0..2,12
  .cases[3]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
   1] match_case - 1,0..1,15
     .pattern MatchSingleton True - 1,5..1,9
     .body[1]
      0] Pass - 1,11..1,15
   2] match_case - 2,0..2,12
     .pattern MatchAs - 2,5..2,6
     .body[1]
      0] Pass - 2,8..2,12
'''),

('', 0, 'end', None, {'raw': True}, ('_match_cases', r'''
case 1: pass
case cls(a, b=c): pass
case _: pass
'''), (None,
r'''case True: pass'''),
r'''case True: pass''', r'''
_match_cases - ROOT 0,0..0,15
  .cases[1]
   0] match_case - 0,0..0,15
     .pattern MatchSingleton True - 0,5..0,9
     .body[1]
      0] Pass - 0,11..0,15
'''),

('', 1, 2, None, {'raw': True}, ('_Assign_targets',
r'''a = b = c ='''), (None,
r'''x'''),
r'''a = x = c =''', r'''
_Assign_targets - ROOT 0,0..0,11
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'x' Store - 0,4..0,5
   2] Name 'c' Store - 0,8..0,9
'''),

('', 0, 'end', None, {'raw': True}, ('_Assign_targets',
r'''a = b = c ='''), (None,
r'''x'''),
r'''x =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'x' Store - 0,0..0,1
'''),

('', 1, 2, None, {'raw': True}, ('_decorator_list', r'''
@deco1
@deco2(arg)
@deco3
'''), (None,
r'''deco4(arg1, arg2)'''), r'''
@deco1
@deco4(arg1, arg2)
@deco3
''', r'''
_decorator_list - ROOT 0,0..2,6
  .decorator_list[3]
   0] Name 'deco1' Load - 0,1..0,6
   1] Call - 1,1..1,18
     .func Name 'deco4' Load - 1,1..1,6
     .args[2]
      0] Name 'arg1' Load - 1,7..1,11
      1] Name 'arg2' Load - 1,13..1,17
   2] Name 'deco3' Load - 2,1..2,6
'''),

('', 0, 'end', None, {'raw': True}, ('_decorator_list', r'''
@deco1
@deco2(arg)
@deco3
'''), (None,
r'''deco4(arg1, arg2)'''),
r'''@deco4(arg1, arg2)''', r'''
_decorator_list - ROOT 0,0..0,18
  .decorator_list[1]
   0] Call - 0,1..0,18
     .func Name 'deco4' Load - 0,1..0,6
     .args[2]
      0] Name 'arg1' Load - 0,7..0,11
      1] Name 'arg2' Load - 0,13..0,17
'''),

('', 1, 2, None, {'raw': True}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), (None,
r'''for x in x'''),
r'''for a in a for x in x for c in c''', r'''
_comprehensions - ROOT 0,0..0,32
  .generators[3]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'x' Store - 0,15..0,16
     .iter Name 'x' Load - 0,20..0,21
     .is_async 0
   2] comprehension - 0,22..0,32
     .target Name 'c' Store - 0,26..0,27
     .iter Name 'c' Load - 0,31..0,32
     .is_async 0
'''),

('', 0, 'end', None, {'raw': True}, ('_comprehensions',
r'''for a in a for b in b for c in c'''), (None,
r'''for x in x'''),
r'''for x in x''', r'''
_comprehensions - ROOT 0,0..0,10
  .generators[1]
   0] comprehension - 0,0..0,10
     .target Name 'x' Store - 0,4..0,5
     .iter Name 'x' Load - 0,9..0,10
     .is_async 0
'''),

('', 1, 2, None, {'raw': True}, ('_comprehension_ifs',
r'''if a if b if c'''), (None,
r'''x'''),
r'''if a if x if c''', r'''
_comprehension_ifs - ROOT 0,0..0,14
  .ifs[3]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'x' Load - 0,8..0,9
   2] Name 'c' Load - 0,13..0,14
'''),

('', 0, 'end', None, {'raw': True}, ('_comprehension_ifs',
r'''if a if b if c'''), (None,
r'''x'''),
r'''if x''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'x' Load - 0,3..0,4
'''),

('', 1, 2, None, {'raw': True}, ('_aliases',
r'''a as a, b as b, c as c'''), (None,
r'''x as x'''),
r'''a as a, x as x, c as c''', r'''
_aliases - ROOT 0,0..0,22
  .names[3]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'a'
   1] alias - 0,8..0,14
     .name 'x'
     .asname 'x'
   2] alias - 0,16..0,22
     .name 'c'
     .asname 'c'
'''),

('', 0, 'end', None, {'raw': True}, ('_aliases',
r'''a as a, b as b, c as c'''), (None,
r'''x as x'''),
r'''x as x''', r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'x'
     .asname 'x'
'''),

('', 1, 2, None, {'raw': True}, ('_withitems',
r'''a as a, b as b, c as c'''), (None,
r'''x as x'''),
r'''a as a, x as x, c as c''', r'''
_withitems - ROOT 0,0..0,22
  .items[3]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'a' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'x' Store - 0,13..0,14
   2] withitem - 0,16..0,22
     .context_expr Name 'c' Load - 0,16..0,17
     .optional_vars Name 'c' Store - 0,21..0,22
'''),

('', 0, 'end', None, {'raw': True}, ('_withitems',
r'''a as a, b as b, c as c'''), (None,
r'''x as x'''),
r'''x as x''', r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Name 'x' Load - 0,0..0,1
     .optional_vars Name 'x' Store - 0,5..0,6
'''),

('', 1, 2, None, {'_ver': 12, 'raw': True}, ('_type_params',
r'''T, *U, **V'''), (None,
r'''X: int'''),
r'''T, X: int, **V''', r'''
_type_params - ROOT 0,0..0,14
  .type_params[3]
   0] TypeVar - 0,0..0,1
     .name 'T'
   1] TypeVar - 0,3..0,9
     .name 'X'
     .bound Name 'int' Load - 0,6..0,9
   2] ParamSpec - 0,11..0,14
     .name 'V'
'''),

('', 0, 'end', None, {'_ver': 12, 'raw': True}, ('_type_params',
r'''T, *U, **V'''), (None,
r'''X: int'''),
r'''X: int''', r'''
_type_params - ROOT 0,0..0,6
  .type_params[1]
   0] TypeVar - 0,0..0,6
     .name 'X'
     .bound Name 'int' Load - 0,3..0,6
'''),
],

'raw_virtual_fields': [  # ................................................................................

('', 1, 2, '_all', {'raw': True}, ('Dict',
r'''{1: a, 2: b, 3: c}'''), ('Dict',
r'''4: x, 5: y'''),
r'''{1: a, 4: x, 5: y, 3: c}''', r'''
Dict - ROOT 0,0..0,24
  .keys[4]
   0] Constant 1 - 0,1..0,2
   1] Constant 4 - 0,7..0,8
   2] Constant 5 - 0,13..0,14
   3] Constant 3 - 0,19..0,20
  .values[4]
   0] Name 'a' Load - 0,4..0,5
   1] Name 'x' Load - 0,10..0,11
   2] Name 'y' Load - 0,16..0,17
   3] Name 'c' Load - 0,22..0,23
'''),

('', 1, 2, '_all', {'raw': True}, ('MatchMapping',
r'''{1: a, 2: b, 3: c}'''), ('MatchMapping',
r'''4: x, 5: y'''),
r'''{1: a, 4: x, 5: y, 3: c}''', r'''
MatchMapping - ROOT 0,0..0,24
  .keys[4]
   0] Constant 1 - 0,1..0,2
   1] Constant 4 - 0,7..0,8
   2] Constant 5 - 0,13..0,14
   3] Constant 3 - 0,19..0,20
  .patterns[4]
   0] MatchAs - 0,4..0,5
     .name 'a'
   1] MatchAs - 0,10..0,11
     .name 'x'
   2] MatchAs - 0,16..0,17
     .name 'y'
   3] MatchAs - 0,22..0,23
     .name 'c'
'''),

('', 1, 2, '_all', {'raw': True}, ('Compare',
r'''a < b > c'''), ('Compare',
r'''x != y'''),
r'''a < x != y > c''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,0..0,1
  .ops[3]
   0] Lt - 0,2..0,3
   1] NotEq - 0,6..0,8
   2] Gt - 0,11..0,12
  .comparators[3]
   0] Name 'x' Load - 0,4..0,5
   1] Name 'y' Load - 0,9..0,10
   2] Name 'c' Load - 0,13..0,14
'''),

('', 0, 'end', '_body', {'raw': True}, ('Module', r'''
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

('', 0, 'end', '_body', {'_verify': False}, ('Interactive',
r'''"""non-doc"""; a; b'''),
r'''x''',
r'''x''', r'''
Interactive - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'x' Load - 0,0..0,1
'''),

('', 0, 'end', '_body', {'raw': True}, ('FunctionDef', r'''
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

('', 0, 'end', '_body', {'raw': True}, ('AsyncFunctionDef', r'''
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

('', 0, 'end', '_body', {'raw': True}, ('ClassDef', r'''
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

('', 0, 'end', '_body', {'raw': True}, ('For', r'''
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
],

'misc': [  # ................................................................................

('', 0, 0, None, {}, (None, r'''
def f():  # comment
    a  # blah
'''), (None,
r'''b  # bloh'''), r'''
def f():  # comment
    b  # bloh
    a  # blah
''', r'''
def f():  # comment
    b
    a  # blah
''', r'''
FunctionDef - ROOT 0,0..2,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'b' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'a' Load - 2,4..2,5
'''),

('', 0, 1, None, {}, (None, r'''
[
1,

# pre
2,
]
'''), (None, r'''
[
3,
4,
]
'''), r'''
[
3,
4,

# pre
2,
]
''', r'''
[
3, 4,

# pre
2,
]
''', r'''
List - ROOT 0,0..6,1
  .elts[3]
   0] Constant 3 - 1,0..1,1
   1] Constant 4 - 2,0..2,1
   2] Constant 2 - 5,0..5,1
  .ctx Load
'''),

('', 0, 1, None, {}, (None,
'[1,\n  \n# pre\n2,\n]'), (None, r'''
[
3,
4,
]
'''),
'[\n3,\n4,\n  \n# pre\n2,\n]',
'[3, 4,\n  \n# pre\n2,\n]', r'''
List - ROOT 0,0..6,1
  .elts[3]
   0] Constant 3 - 1,0..1,1
   1] Constant 4 - 2,0..2,1
   2] Constant 2 - 5,0..5,1
  .ctx Load
'''),

('', 0, 1, None, {}, (None,
'[\n1,\n  \n# pre\n2,\n]'), (None, r'''
[
3,
4,
]
'''),
'[\n3,\n4,\n  \n# pre\n2,\n]',
'[\n3, 4,\n  \n# pre\n2,\n]', r'''
List - ROOT 0,0..6,1
  .elts[3]
   0] Constant 3 - 1,0..1,1
   1] Constant 4 - 2,0..2,1
   2] Constant 2 - 5,0..5,1
  .ctx Load
'''),

('', 0, 1, None, {}, (None, r'''
match _:
    case _:
        pass
'''), (None, r'''
case _:
    if False:
        return 0  # comment
'''), r'''
match _:
    case _:
        if False:
            return 0  # comment
''', r'''
match _:
    case _:
        if False:
            return 0
''', r'''
Match - ROOT 0,0..3,20
  .subject Name '_' Load - 0,6..0,7
  .cases[1]
   0] match_case - 1,4..3,20
     .pattern MatchAs - 1,9..1,10
     .body[1]
      0] If - 2,8..3,20
        .test Constant False - 2,11..2,16
        .body[1]
         0] Return - 3,12..3,20
           .value Constant 0 - 3,19..3,20
'''),

('', 0, 1, None, {}, (None, r'''
match _:
    case _:
        pass;
'''), (None, r'''
case _:
    if False:
        return 0  # comment
'''), r'''
match _:
    case _:
        if False:
            return 0  # comment
''', r'''
match _:
    case _:
        if False:
            return 0
''', r'''
Match - ROOT 0,0..3,20
  .subject Name '_' Load - 0,6..0,7
  .cases[1]
   0] match_case - 1,4..3,20
     .pattern MatchAs - 1,9..1,10
     .body[1]
      0] If - 2,8..3,20
        .test Constant False - 2,11..2,16
        .body[1]
         0] Return - 3,12..3,20
           .value Constant 0 - 3,19..3,20
'''),

('', 0, 1, None, {}, (None, r'''
match _:
    case _:
        pass
'''), (None, r'''
case _:
    if False:
        return 0 ;
'''), r'''
match _:
    case _:
        if False:
            return 0 ;
''', r'''
match _:
    case _:
        if False:
            return 0
''', r'''
Match - ROOT 0,0..3,22
  .subject Name '_' Load - 0,6..0,7
  .cases[1]
   0] match_case - 1,4..3,22
     .pattern MatchAs - 1,9..1,10
     .body[1]
      0] If - 2,8..3,22
        .test Constant False - 2,11..2,16
        .body[1]
         0] Return - 3,12..3,20
           .value Constant 0 - 3,19..3,20
'''),

('', 0, 0, 'orelse', {}, (None, r'''
if 1:
    pass
'''), (None,
r'''  '''),
r'''**ValueError("cannot insert empty statement into empty 'orelse' field")**'''),

('', 0, 0, 'finalbody', {}, (None, r'''
try: pass
except: pass
'''), (None,
r'''  '''),
r'''**ValueError("cannot insert empty statement into empty 'finalbody' field")**'''),

('', 0, 1, None, {}, ('exec', r'''

if 1: pass
'''),
r'''**DEL**''',
r'''''',
r'''Module - ROOT 0,0..0,0'''),
],

}
