# (case idx, attr, start, stop, field, options, code | (parse_mode, code),
#
# code after cut,
# dump code after cut)
# - OR
# error)

DATA_GET_SLICE = {
'old_stmtish': [  # ................................................................................

(0, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j  # post
    k
'''), r'''
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
''', r'''
# pre
j  # post

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(1, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j ;
    k
'''), r'''
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
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(2, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j ; # post
    k
'''), r'''
if 1:
    i
    # post
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(3, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j ; \
  k
'''), r'''
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
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(4, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j ; \
\
  k
'''), r'''
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
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(5, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j \
    ; \
\
  k
'''), r'''
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
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(6, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j \
    ; \
  k
'''), r'''
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
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(7, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j \
    ; k
'''), r'''
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
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(8, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j
    k
'''), r'''
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
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(9, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; j  # post
    k
'''), r'''
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
''', r'''
j  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(10, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; j  # post
'''), r'''
if 1:
    i
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(11, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
  ; j  # post
    k
'''), r'''
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
''', r'''
j  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(12, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; \
  j  # post
    k
'''), r'''
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
''', r'''
j  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(13, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
  ; \
  j  # post
    k
'''), r'''
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
''', r'''
j  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(14, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; j ; k
'''), r'''
if 1:
    i ; k
''', r'''
Module - ROOT 0,0..1,9
  .body[1]
   0] If - 0,0..1,9
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 1,8..1,9
        .value Name 'k' Load - 1,8..1,9
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(15, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; j
    k
'''), r'''
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
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(16, 'body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i ; j  # post
    k
'''), r'''
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
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(17, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; j \
    # post
    k
'''), r'''
if 1:
    i \
    # post
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(18, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; \
  j \
    # post
    k
'''), r'''
if 1:
    i \
    # post
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(19, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
  ; \
  j \
    # post
    k
'''), r'''
if 1:
    i \
    # post
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(20, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; \
    j  # post
    if 2: pass
'''), r'''
if 1:
    i
    if 2: pass
''', r'''
Module - ROOT 0,0..2,14
  .body[1]
   0] If - 0,0..2,14
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,14
        .test Constant 2 - 2,7..2,8
        .body[1]
         0] Pass - 2,10..2,14
''', r'''
j  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(21, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
    ; j  # post
    if 2: pass
'''), r'''
if 1:
    i
    if 2: pass
''', r'''
Module - ROOT 0,0..2,14
  .body[1]
   0] If - 0,0..2,14
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,14
        .test Constant 2 - 2,7..2,8
        .body[1]
         0] Pass - 2,10..2,14
''', r'''
j  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(22, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
    ; \
    j  # post
    if 2: pass
'''), r'''
if 1:
    i
    if 2: pass
''', r'''
Module - ROOT 0,0..2,14
  .body[1]
   0] If - 0,0..2,14
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,14
        .test Constant 2 - 2,7..2,8
        .body[1]
         0] Pass - 2,10..2,14
''', r'''
j  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(23, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i ; \
    j
    if 2: pass
'''), r'''
if 1:
    i
    if 2: pass
''', r'''
Module - ROOT 0,0..2,14
  .body[1]
   0] If - 0,0..2,14
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,14
        .test Constant 2 - 2,7..2,8
        .body[1]
         0] Pass - 2,10..2,14
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(24, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
    ; j
    if 1: pass
'''), r'''
if 1:
    i
    if 1: pass
''', r'''
Module - ROOT 0,0..2,14
  .body[1]
   0] If - 0,0..2,14
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,14
        .test Constant 1 - 2,7..2,8
        .body[1]
         0] Pass - 2,10..2,14
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(25, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
    ; \
    j
    if 2: pass
'''), r'''
if 1:
    i
    if 2: pass
''', r'''
Module - ROOT 0,0..2,14
  .body[1]
   0] If - 0,0..2,14
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,14
        .test Constant 2 - 2,7..2,8
        .body[1]
         0] Pass - 2,10..2,14
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(26, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    j
    k
'''), r'''
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
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(27, 'body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i
    j  # post
    k
'''), r'''
if 1:
    i
    # post
    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(28, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    \
    j
    k
'''), r'''
if 1:
    i

    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(29, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    j \

    k
'''), r'''
if 1:
    i
    \

    k
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] If - 0,0..4,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 4,4..4,5
        .value Name 'k' Load - 4,4..4,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(30, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    j ;
    k
'''), r'''
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
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(31, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    j ; \
  k
'''), r'''
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
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(32, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    j \
  ;
    k
'''), r'''
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
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(33, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    j \
  ; \
  k
'''), r'''
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
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(34, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    j  # post
    k
'''), r'''
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
''', r'''
j  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(35, 'body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
if 1: pass
else: \
  i ; j
'''), r'''
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
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(36, 'body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
if 1: pass
else: \
  i ; \
    j
'''), r'''
if 1: pass
else:
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(37, 'body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
if 1: pass
else: \
  i \
 ; \
    j
'''), r'''
if 1: pass
else:
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(38, 'body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
if 1: pass
else: i ; j
'''), r'''
if 1: pass
else: j
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] If - 0,0..1,7
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Expr - 1,6..1,7
        .value Name 'j' Load - 1,6..1,7
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(39, 'body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
if 1: pass
else: \
  i ; j
'''), r'''
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
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(40, 'body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
if 1: pass
else: \
  i ; \
    j
'''), r'''
if 1: pass
else:
    j
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Expr - 2,4..2,5
        .value Name 'j' Load - 2,4..2,5
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(41, 'body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
if 1: pass
else:
  i \
 ; \
    j
'''), r'''
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
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(42, 'body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
if 1: pass
else: i ; j
'''), r'''
if 1: pass
else: j
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] If - 0,0..1,7
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
     .orelse[1]
      0] Expr - 1,6..1,7
        .value Name 'j' Load - 1,6..1,7
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(43, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
    # pre
    j
    if 2: pass
'''), r'''
if 1:
    i
    if 2: pass
''', r'''
Module - ROOT 0,0..2,14
  .body[1]
   0] If - 0,0..2,14
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,14
        .test Constant 2 - 2,7..2,8
        .body[1]
         0] Pass - 2,10..2,14
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(44, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
    # pre
    j  # post
    if 2: pass
'''), r'''
if 1:
    i
    if 2: pass
''', r'''
Module - ROOT 0,0..2,14
  .body[1]
   0] If - 0,0..2,14
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] If - 2,4..2,14
        .test Constant 2 - 2,7..2,8
        .body[1]
         0] Pass - 2,10..2,14
''', r'''
# pre
j  # post

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(45, 'body[0]', 0, 1, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
  \
  i
  if 2: pass
'''), r'''
if 1:

  if 2: pass
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] If - 0,0..2,12
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] If - 2,2..2,12
        .test Constant 2 - 2,5..2,6
        .body[1]
         0] Pass - 2,8..2,12
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(46, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    \
    j
    k
'''), r'''
if 1:
    i

    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] If - 0,0..3,5
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(47, 'body[0]', 0, 1, None, {'trivia': (True, True)}, ('exec', r'''
if 1: \
    i; j
'''), r'''
if 1:
    j
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'j' Load - 1,4..1,5
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(48, 'body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i \
    # pre
    j ; k
'''), r'''
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
''', r'''
# pre
j
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(49, 'body[0]', 1, 2, None, {'trivia': 'block-1'}, ('exec', r'''
class cls:
    i
    \




    def f(): pass
    j
'''), r'''
class cls:
    i
    \



    j
''', r'''
Module - ROOT 0,0..6,5
  .body[1]
   0] ClassDef - 0,0..6,5
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 6,4..6,5
        .value Name 'j' Load - 6,4..6,5
''',
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

(50, 'body[0]', 1, 2, None, {'pep8space': True}, ('exec', r'''
class cls:
    i
    \




    def f(): pass
    j
'''), r'''
class cls:
    i
    \



    j
''', r'''
Module - ROOT 0,0..6,5
  .body[1]
   0] ClassDef - 0,0..6,5
     .name 'cls'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 6,4..6,5
        .value Name 'j' Load - 6,4..6,5
''',
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

(51, '', 1, 2, None, {'pep8space': True}, ('exec', r'''
i
\




def f(): pass
j
'''), r'''
i
\


j
''', r'''
Module - ROOT 0,0..4,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 4,0..4,1
     .value Name 'j' Load - 4,0..4,1
''',
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

(52, '', 1, 2, None, {'pep8space': True, 'trivia': 'block-3'}, ('exec', r'''
i
\




def f(): pass
j
'''), r'''
i
\

j
''', r'''
Module - ROOT 0,0..3,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 3,0..3,1
     .value Name 'j' Load - 3,0..3,1
''',
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

(53, '', 1, 2, None, {'pep8space': True, 'trivia': 'block-4'}, ('exec', r'''
i
\




def f(): pass
j
'''), r'''
i

j
''', r'''
Module - ROOT 0,0..2,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'j' Load - 2,0..2,1
''',
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

(54, '', 1, 2, None, {'pep8space': True, 'trivia': 'block-5'}, ('exec', r'''
i
\




def f(): pass
j
'''), r'''
i
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
''',
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

(55, '', 1, 2, None, {'pep8space': True, 'trivia': 'block-6'}, ('exec', r'''
i
\




def f(): pass
j
'''), r'''
i
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
''',
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

(56, '', 1, 2, None, {'trivia': ('block-1', False), 'pep8space': False}, ('exec', r'''
i
\



# pre
def f(): pass
j
'''), r'''
i
\


j
''', r'''
Module - ROOT 0,0..4,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 4,0..4,1
     .value Name 'j' Load - 4,0..4,1
''', r'''
# pre
def f(): pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] FunctionDef - 1,0..1,13
     .name 'f'
     .body[1]
      0] Pass - 1,9..1,13
'''),

(57, '', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
i
# pre
@deco1
@deco2
class cls:
  pass  # post
j
'''), r'''
i
# pre
# post
j
''', r'''
Module - ROOT 0,0..3,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 3,0..3,1
     .value Name 'j' Load - 3,0..3,1
''', r'''
@deco1
@deco2
class cls:
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] ClassDef - 2,0..3,6
     .name 'cls'
     .body[1]
      0] Pass - 3,2..3,6
     .decorator_list[2]
      0] Name 'deco1' Load - 0,1..0,6
      1] Name 'deco2' Load - 1,1..1,6
'''),

(58, '', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
i
# pre
@deco1
@deco2(a, b)
class cls:
  pass  # post
j
'''), r'''
i
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
''', r'''
# pre
@deco1
@deco2(a, b)
class cls:
  pass  # post

''', r'''
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
'''),

(59, '', 0, 1, None, {'pep8space': True}, ('exec', r'''
def func0():
    pass


def func1():
    break


continue
'''), r'''
def func1():
    break


continue
''', r'''
Module - ROOT 0,0..4,8
  .body[2]
   0] FunctionDef - 0,0..1,9
     .name 'func1'
     .body[1]
      0] Break - 1,4..1,9
   1] Continue - 4,0..4,8
''', r'''
def func0():
    pass
''', r'''
Module - ROOT 0,0..1,8
  .body[1]
   0] FunctionDef - 0,0..1,8
     .name 'func0'
     .body[1]
      0] Pass - 1,4..1,8
'''),

(60, '', 1, 2, None, {'pep8space': True}, ('exec', r'''
def func0():
    pass


def func1():
    break


continue
'''), r'''
def func0():
    pass


continue
''', r'''
Module - ROOT 0,0..4,8
  .body[2]
   0] FunctionDef - 0,0..1,8
     .name 'func0'
     .body[1]
      0] Pass - 1,4..1,8
   1] Continue - 4,0..4,8
''', r'''
def func1():
    break
''', r'''
Module - ROOT 0,0..1,9
  .body[1]
   0] FunctionDef - 0,0..1,9
     .name 'func1'
     .body[1]
      0] Break - 1,4..1,9
'''),

(61, '', 0, 1, None, {'pep8space': 1}, ('exec', r'''
def func0():
    pass


def func1():
    break


continue
'''), r'''

def func1():
    break


continue
''', r'''
Module - ROOT 0,0..5,8
  .body[2]
   0] FunctionDef - 1,0..2,9
     .name 'func1'
     .body[1]
      0] Break - 2,4..2,9
   1] Continue - 5,0..5,8
''', r'''
def func0():
    pass
''', r'''
Module - ROOT 0,0..1,8
  .body[1]
   0] FunctionDef - 0,0..1,8
     .name 'func0'
     .body[1]
      0] Pass - 1,4..1,8
'''),

(62, '', 1, 2, None, {'pep8space': 1}, ('exec', r'''
def func0():
    pass


def func1():
    break


continue
'''), r'''
def func0():
    pass



continue
''', r'''
Module - ROOT 0,0..5,8
  .body[2]
   0] FunctionDef - 0,0..1,8
     .name 'func0'
     .body[1]
      0] Pass - 1,4..1,8
   1] Continue - 5,0..5,8
''', r'''
def func1():
    break
''', r'''
Module - ROOT 0,0..1,9
  .body[1]
   0] FunctionDef - 0,0..1,9
     .name 'func1'
     .body[1]
      0] Break - 1,4..1,9
'''),

(63, 'body[0]', 0, 1, None, {'pep8space': True}, ('exec', r'''
class cls:
    def meth0():
        pass

    def meth1():
        break

continue
'''), r'''
class cls:
    def meth1():
        break

continue
''', r'''
Module - ROOT 0,0..4,8
  .body[2]
   0] ClassDef - 0,0..2,13
     .name 'cls'
     .body[1]
      0] FunctionDef - 1,4..2,13
        .name 'meth1'
        .body[1]
         0] Break - 2,8..2,13
   1] Continue - 4,0..4,8
''', r'''
def meth0():
    pass
''', r'''
Module - ROOT 0,0..1,8
  .body[1]
   0] FunctionDef - 0,0..1,8
     .name 'meth0'
     .body[1]
      0] Pass - 1,4..1,8
'''),

(64, 'body[0]', 1, 2, None, {'pep8space': True}, ('exec', r'''
class cls:
    def meth0():
        pass

    def meth1():
        break

continue
'''), r'''
class cls:
    def meth0():
        pass

continue
''', r'''
Module - ROOT 0,0..4,8
  .body[2]
   0] ClassDef - 0,0..2,12
     .name 'cls'
     .body[1]
      0] FunctionDef - 1,4..2,12
        .name 'meth0'
        .body[1]
         0] Pass - 2,8..2,12
   1] Continue - 4,0..4,8
''', r'''
def meth1():
    break
''', r'''
Module - ROOT 0,0..1,9
  .body[1]
   0] FunctionDef - 0,0..1,9
     .name 'meth1'
     .body[1]
      0] Break - 1,4..1,9
'''),

(65, 'body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1:
    i ; j



'''), r'''
if 1:
    i



''', r'''
Module - ROOT 0,0..4,0
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(66, 'body[0]', 1, 2, None, {'trivia': (None, 'line-1')}, ('exec', r'''
if 1:
    i ; j



'''), r'''
if 1:
    i


''', r'''
Module - ROOT 0,0..3,0
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(67, 'body[0]', 1, 2, None, {'trivia': (None, 'line-')}, ('exec', r'''
if 1:
    i ; j



'''), r'''
if 1:
    i

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(68, 'body[0]', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
if 1:
    i ; j



'''), r'''
if 1:
    j



''', r'''
Module - ROOT 0,0..4,0
  .body[1]
   0] If - 0,0..1,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..1,5
        .value Name 'j' Load - 1,4..1,5
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(69, '', 0, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
def f():
    i ; j



'''), r'''



''',
r'''Module - ROOT 0,0..2,0''', r'''
def f():
    i ; j
''', r'''
Module - ROOT 0,0..1,9
  .body[1]
   0] FunctionDef - 0,0..1,9
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 1,8..1,9
        .value Name 'j' Load - 1,8..1,9
'''),

(70, '', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
def f():
    i ; j



'''),
r'''''',
r'''Module - ROOT 0,0..0,0''', r'''
def f():
    i ; j
''', r'''
Module - ROOT 0,0..1,9
  .body[1]
   0] FunctionDef - 0,0..1,9
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 1,8..1,9
        .value Name 'j' Load - 1,8..1,9
'''),

(71, 'body[0]', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
def f():
    i
    \
  k
'''), r'''
def f():
    \
  k
''', r'''
Module - ROOT 0,0..2,3
  .body[1]
   0] FunctionDef - 0,0..2,3
     .name 'f'
     .body[1]
      0] Expr - 2,2..2,3
        .value Name 'k' Load - 2,2..2,3
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(72, 'body[0]', 1, 2, None, {'trivia': (None, 'line-')}, ('exec', r'''
def f():
    i; j
    \
  k
'''), r'''
def f():
    i
    \
  k
''', r'''
Module - ROOT 0,0..3,3
  .body[1]
   0] FunctionDef - 0,0..3,3
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,2..3,3
        .value Name 'k' Load - 3,2..3,3
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(73, 'body[0]', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
def f():
    i

    \
  k
'''), r'''
def f():
    \
  k
''', r'''
Module - ROOT 0,0..2,3
  .body[1]
   0] FunctionDef - 0,0..2,3
     .name 'f'
     .body[1]
      0] Expr - 2,2..2,3
        .value Name 'k' Load - 2,2..2,3
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(74, 'body[0]', 1, 2, None, {'trivia': (None, 'line-')}, ('exec', r'''
def f():
    i; j

    \
  k
'''), r'''
def f():
    i
    \
  k
''', r'''
Module - ROOT 0,0..3,3
  .body[1]
   0] FunctionDef - 0,0..3,3
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 3,2..3,3
        .value Name 'k' Load - 3,2..3,3
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(75, 'body[0]', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
def f():
    i
    \

    k
'''), r'''
def f():
    \

    k
''', r'''
Module - ROOT 0,0..3,5
  .body[1]
   0] FunctionDef - 0,0..3,5
     .name 'f'
     .body[1]
      0] Expr - 3,4..3,5
        .value Name 'k' Load - 3,4..3,5
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(76, 'body[0]', 1, 2, None, {'trivia': (None, 'line-')}, ('exec', r'''
def f():
    i; j
    \

    k
'''), r'''
def f():
    i
    \

    k
''', r'''
Module - ROOT 0,0..4,5
  .body[1]
   0] FunctionDef - 0,0..4,5
     .name 'f'
     .body[2]
      0] Expr - 1,4..1,5
        .value Name 'i' Load - 1,4..1,5
      1] Expr - 4,4..4,5
        .value Name 'k' Load - 4,4..4,5
''',
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(77, '', 0, 1, None, {'trivia': (True, True)}, ('exec', r'''
i ; \
 j
'''),
r'''j''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(78, 'body[0]', 2, 3, None, {}, ('exec', r'''
def foo():
    # verify statements that end with semi-colons
    x = 1; pass; del x;
foo()
'''), r'''
def foo():
    # verify statements that end with semi-colons
    x = 1; pass
foo()
''', r'''
Module - ROOT 0,0..3,5
  .body[2]
   0] FunctionDef - 0,0..2,15
     .name 'foo'
     .body[2]
      0] Assign - 2,4..2,9
        .targets[1]
         0] Name 'x' Store - 2,4..2,5
        .value Constant 1 - 2,8..2,9
      1] Pass - 2,11..2,15
   1] Expr - 3,0..3,5
     .value Call - 3,0..3,5
       .func Name 'foo' Load - 3,0..3,3
''',
r'''del x''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'x' Del - 0,4..0,5
'''),

(79, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec',
r'''if 1: i'''),
r'''if 1:''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] If - 0,0..0,5
     .test Constant 1 - 0,3..0,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(80, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''

if 1: i
'''), r'''

if 1:
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 1,0..1,5
     .test Constant 1 - 1,3..1,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(81, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec',
r'''if 1: i  # post'''),
r'''if 1:''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] If - 0,0..0,5
     .test Constant 1 - 0,3..0,4
''',
r'''i  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(82, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''

if 1: i  # post
'''), r'''

if 1:
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 1,0..1,5
     .test Constant 1 - 1,3..1,4
''',
r'''i  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(83, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec',
r'''if 1: i  # post'''),
r'''if 1: # post''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] If - 0,0..0,5
     .test Constant 1 - 0,3..0,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(84, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''

if 1: i  # post
'''), r'''

if 1: # post
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] If - 1,0..1,5
     .test Constant 1 - 1,3..1,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(85, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec',
r'''if 1: i ;'''),
r'''if 1:''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] If - 0,0..0,5
     .test Constant 1 - 0,3..0,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(86, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''

if 1: i ;
'''), r'''

if 1:
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 1,0..1,5
     .test Constant 1 - 1,3..1,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(87, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec',
r'''if 1: i ;  # post'''),
r'''if 1: # post''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] If - 0,0..0,5
     .test Constant 1 - 0,3..0,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(88, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''

if 1: i ;  # post
'''), r'''

if 1: # post
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] If - 1,0..1,5
     .test Constant 1 - 1,3..1,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(89, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec',
r'''if 1: i ;  # post'''),
r'''if 1: # post''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] If - 0,0..0,5
     .test Constant 1 - 0,3..0,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(90, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''

if 1: i ;  # post
'''), r'''

if 1: # post
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] If - 1,0..1,5
     .test Constant 1 - 1,3..1,4
''',
r'''i''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

(91, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
if 1: pass

# pre
else: pass
j
'''), r'''
if 1: pass

# pre
j
''', r'''
Module - ROOT 0,0..3,1
  .body[2]
   0] If - 0,0..0,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
   1] Expr - 3,0..3,1
     .value Name 'j' Load - 3,0..3,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(92, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': (True, False), 'pep8space': False}, ('exec', r'''
if 1: pass

# pre
else: pass
j
'''), r'''
if 1: pass

j
''', r'''
Module - ROOT 0,0..2,1
  .body[2]
   0] If - 0,0..0,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
   1] Expr - 2,0..2,1
     .value Name 'j' Load - 2,0..2,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(93, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('block-', False), 'pep8space': False}, ('exec', r'''
if 1: pass

# pre
else: pass
j
'''), r'''
if 1: pass
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] If - 0,0..0,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(94, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('none-', False), 'pep8space': False}, ('exec', r'''
if 1: pass

# pre
else: pass
j
'''), r'''
if 1: pass

# pre
j
''', r'''
Module - ROOT 0,0..3,1
  .body[2]
   0] If - 0,0..0,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
   1] Expr - 3,0..3,1
     .value Name 'j' Load - 3,0..3,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(95, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('block-', False), 'pep8space': False}, ('exec', r'''
if 1: pass

# pre
else: pass  # post
j
'''), r'''
if 1: pass
# post
j
''', r'''
Module - ROOT 0,0..2,1
  .body[2]
   0] If - 0,0..0,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
   1] Expr - 2,0..2,1
     .value Name 'j' Load - 2,0..2,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(96, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('block-', True), 'pep8space': False}, ('exec', r'''
if 1: pass

# pre
else: pass  # post
j
'''), r'''
if 1: pass
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] If - 0,0..0,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
''', r'''
pass  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Pass - 0,0..0,4
'''),

(97, 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
try: pass

# pre
finally: pass
j
'''), r'''
try: pass

# pre
j
''', r'''
Module - ROOT 0,0..3,1
  .body[2]
   0] Try - 0,0..0,9
     .body[1]
      0] Pass - 0,5..0,9
   1] Expr - 3,0..3,1
     .value Name 'j' Load - 3,0..3,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(98, 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': (True, False), 'pep8space': False}, ('exec', r'''
try: pass

# pre
finally: pass
j
'''), r'''
try: pass

j
''', r'''
Module - ROOT 0,0..2,1
  .body[2]
   0] Try - 0,0..0,9
     .body[1]
      0] Pass - 0,5..0,9
   1] Expr - 2,0..2,1
     .value Name 'j' Load - 2,0..2,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(99, 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': ('block-', False), 'pep8space': False}, ('exec', r'''
try: pass

# pre
finally: pass
j
'''), r'''
try: pass
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Try - 0,0..0,9
     .body[1]
      0] Pass - 0,5..0,9
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(100, 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': ('none-', False), 'pep8space': False}, ('exec', r'''
try: pass

# pre
finally: pass
j
'''), r'''
try: pass

# pre
j
''', r'''
Module - ROOT 0,0..3,1
  .body[2]
   0] Try - 0,0..0,9
     .body[1]
      0] Pass - 0,5..0,9
   1] Expr - 3,0..3,1
     .value Name 'j' Load - 3,0..3,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(101, 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': ('block-', False), 'pep8space': False}, ('exec', r'''
try: pass

# pre
finally: pass  # post
j
'''), r'''
try: pass
# post
j
''', r'''
Module - ROOT 0,0..2,1
  .body[2]
   0] Try - 0,0..0,9
     .body[1]
      0] Pass - 0,5..0,9
   1] Expr - 2,0..2,1
     .value Name 'j' Load - 2,0..2,1
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(102, 'body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': ('block-', True), 'pep8space': False}, ('exec', r'''
try: pass

# pre
finally: pass  # post
j
'''), r'''
try: pass
j
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Try - 0,0..0,9
     .body[1]
      0] Pass - 0,5..0,9
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
''', r'''
pass  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Pass - 0,0..0,4
'''),

(103, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('all', False), 'pep8space': False}, ('exec', r'''
if 1: i

# pre-else 1

# pre-else 2
else:

  # pre 1

  # pre 2
  j
'''), r'''
if 1: i

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] If - 0,0..0,7
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..0,7
        .value Name 'i' Load - 0,6..0,7
''', r'''
# pre 1

# pre 2
j
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 3,0..3,1
     .value Name 'j' Load - 3,0..3,1
'''),

(104, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('all-', False), 'pep8space': False}, ('exec', r'''
if 1: i

# pre-else 1

# pre-else 2
else:

  # pre 1

  # pre 2
  j
'''),
r'''if 1: i''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] If - 0,0..0,7
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 0,6..0,7
        .value Name 'i' Load - 0,6..0,7
''', r'''
# pre 1

# pre 2
j
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 3,0..3,1
     .value Name 'j' Load - 3,0..3,1
'''),

(105, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try:
    pass
finally: pass
'''), r'''
try:
finally: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Try - 0,0..1,13
     .finalbody[1]
      0] Pass - 1,9..1,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(106, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: pass
finally: pass
'''), r'''
try:
finally: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Try - 0,0..1,13
     .finalbody[1]
      0] Pass - 1,9..1,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(107, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: i = \
  2
finally: pass
'''), r'''
try:
finally: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Try - 0,0..1,13
     .finalbody[1]
      0] Pass - 1,9..1,13
''', r'''
i = \
2
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Assign - 0,0..1,1
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 2 - 1,0..1,1
'''),

(108, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: pass  # post
finally: pass
'''), r'''
try:
finally: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Try - 0,0..1,13
     .finalbody[1]
      0] Pass - 1,9..1,13
''', r'''
pass  # post

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Pass - 0,0..0,4
'''),

(109, 'body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
try: pass  # post
finally: pass
'''), r'''
try: # post
finally: pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] Try - 0,0..1,13
     .finalbody[1]
      0] Pass - 1,9..1,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(110, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: pass
except: pass
else:
    pass
finally: pass
'''), r'''
try: pass
except: pass
finally: pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] Try - 0,0..2,13
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,12
        .body[1]
         0] Pass - 1,8..1,12
     .finalbody[1]
      0] Pass - 2,9..2,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(111, 'body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: pass
except: pass
else: pass
finally: pass
'''), r'''
try: pass
except: pass
finally: pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] Try - 0,0..2,13
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,12
        .body[1]
         0] Pass - 1,8..1,12
     .finalbody[1]
      0] Pass - 2,9..2,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(112, 'body[0]', 0, 1, 'handlers', {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: pass
except:
    pass
else: pass
finally: pass
'''), r'''
try: pass
else: pass
finally: pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] Try - 0,0..2,13
     .body[1]
      0] Pass - 0,5..0,9
     .orelse[1]
      0] Pass - 1,6..1,10
     .finalbody[1]
      0] Pass - 2,9..2,13
''', r'''
except:
    pass
''', r'''
_ExceptHandlers - ROOT 0,0..1,8
  .handlers[1]
   0] ExceptHandler - 0,0..1,8
     .body[1]
      0] Pass - 1,4..1,8
'''),

(113, 'body[0]', 0, 1, 'handlers', {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: pass
except: pass
else: pass
finally: pass
'''), r'''
try: pass
else: pass
finally: pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] Try - 0,0..2,13
     .body[1]
      0] Pass - 0,5..0,9
     .orelse[1]
      0] Pass - 1,6..1,10
     .finalbody[1]
      0] Pass - 2,9..2,13
''',
r'''except: pass''', r'''
_ExceptHandlers - ROOT 0,0..0,12
  .handlers[1]
   0] ExceptHandler - 0,0..0,12
     .body[1]
      0] Pass - 0,8..0,12
'''),

(114, 'body[0]', 0, 1, 'handlers', {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
try: pass
except: pass  # post
else: pass
finally: pass
'''), r'''
try: pass
# post
else: pass
finally: pass
''', r'''
Module - ROOT 0,0..3,13
  .body[1]
   0] Try - 0,0..3,13
     .body[1]
      0] Pass - 0,5..0,9
     .orelse[1]
      0] Pass - 2,6..2,10
     .finalbody[1]
      0] Pass - 3,9..3,13
''',
r'''except: pass''', r'''
_ExceptHandlers - ROOT 0,0..0,12
  .handlers[1]
   0] ExceptHandler - 0,0..0,12
     .body[1]
      0] Pass - 0,8..0,12
'''),

(115, 'body[0]', 0, 1, 'handlers', {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
try: pass
except: pass  \

else: pass
finally: pass
'''), r'''
try: pass
\

else: pass
finally: pass
''', r'''
Module - ROOT 0,0..4,13
  .body[1]
   0] Try - 0,0..4,13
     .body[1]
      0] Pass - 0,5..0,9
     .orelse[1]
      0] Pass - 3,6..3,10
     .finalbody[1]
      0] Pass - 4,9..4,13
''',
r'''except: pass''', r'''
_ExceptHandlers - ROOT 0,0..0,12
  .handlers[1]
   0] ExceptHandler - 0,0..0,12
     .body[1]
      0] Pass - 0,8..0,12
'''),

(116, 'body[0].handlers[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: pass
except:
    pass
else: pass
finally: pass
'''), r'''
try: pass
except:
else: pass
finally: pass
''', r'''
Module - ROOT 0,0..3,13
  .body[1]
   0] Try - 0,0..3,13
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,7
     .orelse[1]
      0] Pass - 2,6..2,10
     .finalbody[1]
      0] Pass - 3,9..3,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(117, 'body[0].handlers[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
try: pass
except: pass
else: pass
finally: pass
'''), r'''
try: pass
except:
else: pass
finally: pass
''', r'''
Module - ROOT 0,0..3,13
  .body[1]
   0] Try - 0,0..3,13
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,7
     .orelse[1]
      0] Pass - 2,6..2,10
     .finalbody[1]
      0] Pass - 3,9..3,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(118, 'body[0].handlers[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
try: pass
except: pass  # post
else: pass
finally: pass
'''), r'''
try: pass
except: # post
else: pass
finally: pass
''', r'''
Module - ROOT 0,0..3,13
  .body[1]
   0] Try - 0,0..3,13
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,7
     .orelse[1]
      0] Pass - 2,6..2,10
     .finalbody[1]
      0] Pass - 3,9..3,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(119, 'body[0].handlers[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
try: pass
except: pass \

else: pass
finally: pass
'''), r'''
try: pass
except: \

else: pass
finally: pass
''', r'''
Module - ROOT 0,0..4,13
  .body[1]
   0] Try - 0,0..4,13
     .body[1]
      0] Pass - 0,5..0,9
     .handlers[1]
      0] ExceptHandler - 1,0..1,7
     .orelse[1]
      0] Pass - 3,6..3,10
     .finalbody[1]
      0] Pass - 4,9..4,13
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

(120, 'body[0]', 0, 2, None, {'_verify': False}, ('exec', r'''
if type in ('d', 'D'): cmd = 'TYPE A'; isdir = 1
else: cmd = 'TYPE ' + type; isdir = 0
'''), r'''
if type in ('d', 'D'):
else: cmd = 'TYPE ' + type; isdir = 0
''', r'''
Module - ROOT 0,0..1,37
  .body[1]
   0] If - 0,0..1,37
     .test Compare - 0,3..0,21
       .left Name 'type' Load - 0,3..0,7
       .ops[1]
        0] In - 0,8..0,10
       .comparators[1]
        0] Tuple - 0,11..0,21
          .elts[2]
           0] Constant 'd' - 0,12..0,15
           1] Constant 'D' - 0,17..0,20
          .ctx Load
     .orelse[2]
      0] Assign - 1,6..1,26
        .targets[1]
         0] Name 'cmd' Store - 1,6..1,9
        .value BinOp - 1,12..1,26
          .left Constant 'TYPE ' - 1,12..1,19
          .op Add - 1,20..1,21
          .right Name 'type' Load - 1,22..1,26
      1] Assign - 1,28..1,37
        .targets[1]
         0] Name 'isdir' Store - 1,28..1,33
        .value Constant 0 - 1,36..1,37
''',
r'''cmd = 'TYPE A'; isdir = 1''', r'''
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
'''),

(121, 'body[0]', 0, 2, None, {'_verify': False}, ('exec', r'''
if type in ('d', 'D'): cmd = 'TYPE A'
else: cmd = 'TYPE ' + type; isdir = 0
'''), r'''
if type in ('d', 'D'):
else: cmd = 'TYPE ' + type; isdir = 0
''', r'''
Module - ROOT 0,0..1,37
  .body[1]
   0] If - 0,0..1,37
     .test Compare - 0,3..0,21
       .left Name 'type' Load - 0,3..0,7
       .ops[1]
        0] In - 0,8..0,10
       .comparators[1]
        0] Tuple - 0,11..0,21
          .elts[2]
           0] Constant 'd' - 0,12..0,15
           1] Constant 'D' - 0,17..0,20
          .ctx Load
     .orelse[2]
      0] Assign - 1,6..1,26
        .targets[1]
         0] Name 'cmd' Store - 1,6..1,9
        .value BinOp - 1,12..1,26
          .left Constant 'TYPE ' - 1,12..1,19
          .op Add - 1,20..1,21
          .right Name 'type' Load - 1,22..1,26
      1] Assign - 1,28..1,37
        .targets[1]
         0] Name 'isdir' Store - 1,28..1,33
        .value Constant 0 - 1,36..1,37
''',
"\ncmd = 'TYPE A'\n", r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Assign - 0,0..0,14
     .targets[1]
      0] Name 'cmd' Store - 0,0..0,3
     .value Constant 'TYPE A' - 0,6..0,14
'''),

(122, 'body[0].value', 1, 3, None, {}, ('exec', r'''
[
    a, b,
    c
]
'''), r'''
[
    a
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[1]
        0] Name 'a' Load - 1,4..1,5
       .ctx Load
''', r'''
[b,
    c
]
''', r'''
List - ROOT 0,0..2,1
  .elts[2]
   0] Name 'b' Load - 0,1..0,2
   1] Name 'c' Load - 1,4..1,5
  .ctx Load
'''),

(123, 'body[0].value', 0, 2, None, {}, ('exec', r'''
[
    a,
    b, c
]
'''), r'''
[
    c
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[1]
        0] Name 'c' Load - 1,4..1,5
       .ctx Load
''', r'''
[
    a,
    b]
''', r'''
List - ROOT 0,0..2,6
  .elts[2]
   0] Name 'a' Load - 1,4..1,5
   1] Name 'b' Load - 2,4..2,5
  .ctx Load
'''),
],

'old_exprish': [  # ................................................................................

(0, 'body[0].value', 0, 0, None, {}, ('exec',
r'''{1, 2}'''),
r'''{1, 2}''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Set - 0,0..0,6
       .elts[2]
        0] Constant 1 - 0,1..0,2
        1] Constant 2 - 0,4..0,5
''',
r'''{*()}''', r'''
Set - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,4
     .value Tuple - 0,2..0,4
       .ctx Load
     .ctx Load
'''),

(1, 'body[0].value', None, None, None, {}, ('exec', r'''
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
'''), r'''
(       # hello
)
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value Tuple - 0,0..1,1
       .ctx Load
''', r'''
(
    1,  # last line
    2,  # second line
    3,  # third line
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[3]
   0] Constant 1 - 1,4..1,5
   1] Constant 2 - 2,4..2,5
   2] Constant 3 - 3,4..3,5
  .ctx Load
'''),

(2, 'body[0].value', 0, 2, None, {}, ('exec', r'''
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
'''), r'''
(       # hello
    3,  # third line
)
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value Tuple - 0,0..2,1
       .elts[1]
        0] Constant 3 - 1,4..1,5
       .ctx Load
''', r'''
(
    1,  # last line
    2,  # second line
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Constant 1 - 1,4..1,5
   1] Constant 2 - 2,4..2,5
  .ctx Load
'''),

(3, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
'''), r'''
(       # hello
    1,  # last line
    3,  # third line
)
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value Tuple - 0,0..3,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 3 - 2,4..2,5
       .ctx Load
''', r'''
(
    2,  # second line
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[1]
   0] Constant 2 - 1,4..1,5
  .ctx Load
'''),

(4, 'body[0].value', 2, None, None, {}, ('exec', r'''
(       # hello
    1,  # last line
    2,  # second line
    3,  # third line
)
'''), r'''
(       # hello
    1,  # last line
    2,  # second line
)
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value Tuple - 0,0..3,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 2 - 2,4..2,5
       .ctx Load
''', r'''
(
    3,  # third line
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[1]
   0] Constant 3 - 1,4..1,5
  .ctx Load
'''),

(5, 'body[0].value', None, None, None, {}, ('exec', r'''
(           # hello
    1, 2, 3 # last line
)
'''), r'''
(           # hello
)
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value Tuple - 0,0..1,1
       .ctx Load
''', r'''
(
    1, 2, 3 # last line
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[3]
   0] Constant 1 - 1,4..1,5
   1] Constant 2 - 1,7..1,8
   2] Constant 3 - 1,10..1,11
  .ctx Load
'''),

(6, 'body[0].value', 0, 2, None, {}, ('exec', r'''
(           # hello
    1, 2, 3 # last line
)
'''), r'''
(           # hello
    3, # last line
)
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value Tuple - 0,0..2,1
       .elts[1]
        0] Constant 3 - 1,4..1,5
       .ctx Load
''',
r'''(1, 2)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,4..0,5
  .ctx Load
'''),

(7, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(           # hello
    1, 2, 3 # last line
)
'''), r'''
(           # hello
    1, 3 # last line
)
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value Tuple - 0,0..2,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 3 - 1,7..1,8
       .ctx Load
''',
r'''(2,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(8, 'body[0].value', 2, None, None, {}, ('exec', r'''
(           # hello
    1, 2, 3 # last line
)
'''), r'''
(           # hello
    1, 2
)
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value Tuple - 0,0..2,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 2 - 1,7..1,8
       .ctx Load
''', r'''
(3, # last line
)
''', r'''
Tuple - ROOT 0,0..1,1
  .elts[1]
   0] Constant 3 - 0,1..0,2
  .ctx Load
'''),

(9, 'body[0].value', 1, 3, None, {}, ('exec',
r'''1, 2, 3, 4'''),
r'''1, 4''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[2]
        0] Constant 1 - 0,0..0,1
        1] Constant 4 - 0,3..0,4
       .ctx Load
''',
r'''2, 3''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Constant 2 - 0,0..0,1
   1] Constant 3 - 0,3..0,4
  .ctx Load
'''),

(10, 'body[0].value', -1, None, None, {}, ('exec',
r'''1, 2, 3, 4'''),
r'''1, 2, 3''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Tuple - 0,0..0,7
       .elts[3]
        0] Constant 1 - 0,0..0,1
        1] Constant 2 - 0,3..0,4
        2] Constant 3 - 0,6..0,7
       .ctx Load
''',
r'''4,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Constant 4 - 0,0..0,1
  .ctx Load
'''),

(11, 'body[0].value', None, None, None, {}, ('exec',
r'''1, 2, 3, 4'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .ctx Load
''',
r'''1, 2, 3, 4''', r'''
Tuple - ROOT 0,0..0,10
  .elts[4]
   0] Constant 1 - 0,0..0,1
   1] Constant 2 - 0,3..0,4
   2] Constant 3 - 0,6..0,7
   3] Constant 4 - 0,9..0,10
  .ctx Load
'''),

(12, 'body[0].value', 1, 1, None, {}, ('exec',
r'''1, 2, 3, 4'''),
r'''1, 2, 3, 4''', r'''
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
''',
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
'''),

(13, 'body[0].value', 1, None, None, {}, ('exec',
r'''1, 2, 3, 4'''),
r'''1,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Constant 1 - 0,0..0,1
       .ctx Load
''',
r'''2, 3, 4''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Constant 2 - 0,0..0,1
   1] Constant 3 - 0,3..0,4
   2] Constant 4 - 0,6..0,7
  .ctx Load
'''),

(14, 'body[0].value', 0, 3, None, {}, ('exec',
r'''1, 2, 3, 4'''),
r'''4,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Constant 4 - 0,0..0,1
       .ctx Load
''',
r'''1, 2, 3''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Constant 1 - 0,0..0,1
   1] Constant 2 - 0,3..0,4
   2] Constant 3 - 0,6..0,7
  .ctx Load
'''),

(15, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(1, 2
  ,  # comment
3, 4)
'''), r'''
(1,
3, 4)
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] Expr - 0,0..1,5
     .value Tuple - 0,0..1,5
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 3 - 1,0..1,1
        2] Constant 4 - 1,3..1,4
       .ctx Load
''', r'''
(2
  ,  # comment
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(16, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(1, 2
  ,
  3, 4)
'''), r'''
(1,
  3, 4)
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Expr - 0,0..1,7
     .value Tuple - 0,0..1,7
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 3 - 1,2..1,3
        2] Constant 4 - 1,5..1,6
       .ctx Load
''', r'''
(2
  ,)
''', r'''
Tuple - ROOT 0,0..1,4
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(17, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(1, 2 \
  , \
  3, 4)
'''), r'''
(1, \
  3, 4)
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Expr - 0,0..1,7
     .value Tuple - 0,0..1,7
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 3 - 1,2..1,3
        2] Constant 4 - 1,5..1,6
       .ctx Load
''', r'''
(2 \
  ,)
''', r'''
Tuple - ROOT 0,0..1,4
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(18, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(1, 2  # comment
  , \
  3, 4)
'''), r'''
(1, \
  3, 4)
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] Expr - 0,0..1,7
     .value Tuple - 0,0..1,7
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 3 - 1,2..1,3
        2] Constant 4 - 1,5..1,6
       .ctx Load
''', r'''
(2  # comment
  ,)
''', r'''
Tuple - ROOT 0,0..1,4
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(19, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(1, 2
  ,
3, 4)
'''), r'''
(1,
3, 4)
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] Expr - 0,0..1,5
     .value Tuple - 0,0..1,5
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 3 - 1,0..1,1
        2] Constant 4 - 1,3..1,4
       .ctx Load
''', r'''
(2
  ,)
''', r'''
Tuple - ROOT 0,0..1,4
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(20, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(1, 2
  , 3, 4)
'''),
r'''(1, 3, 4)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Tuple - 0,0..0,9
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 3 - 0,4..0,5
        2] Constant 4 - 0,7..0,8
       .ctx Load
''', r'''
(2
  ,)
''', r'''
Tuple - ROOT 0,0..1,4
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(21, 'body[0].value', 1, 2, None, {}, ('exec', r'''
(1, 2  # comment
  , 3, 4)
'''),
r'''(1, 3, 4)''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Tuple - 0,0..0,9
       .elts[3]
        0] Constant 1 - 0,1..0,2
        1] Constant 3 - 0,4..0,5
        2] Constant 4 - 0,7..0,8
       .ctx Load
''', r'''
(2  # comment
  ,)
''', r'''
Tuple - ROOT 0,0..1,4
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(22, 'body[0].body[0].value', None, None, None, {}, ('exec', r'''
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
'''), r'''
if 1:
    (       # hello
    )
''', r'''
Module - ROOT 0,0..2,5
  .body[1]
   0] If - 0,0..2,5
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Expr - 1,4..2,5
        .value Tuple - 1,4..2,5
          .ctx Load
''', r'''
(
    1,  # last line
    2,  # second line
    3,  # third line
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[3]
   0] Constant 1 - 1,4..1,5
   1] Constant 2 - 2,4..2,5
   2] Constant 3 - 3,4..3,5
  .ctx Load
'''),

(23, 'body[0].body[0].value', 0, 2, None, {}, ('exec', r'''
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
'''), r'''
if 1:
    (       # hello
        3,  # third line
    )
''', r'''
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
''', r'''
(
    1,  # last line
    2,  # second line
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Constant 1 - 1,4..1,5
   1] Constant 2 - 2,4..2,5
  .ctx Load
'''),

(24, 'body[0].body[0].value', 1, 2, None, {}, ('exec', r'''
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
'''), r'''
if 1:
    (       # hello
        1,  # last line
        3,  # third line
    )
''', r'''
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
''', r'''
(
    2,  # second line
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[1]
   0] Constant 2 - 1,4..1,5
  .ctx Load
'''),

(25, 'body[0].body[0].value', 2, None, None, {}, ('exec', r'''
if 1:
    (       # hello
        1,  # last line
        2,  # second line
        3,  # third line
    )
'''), r'''
if 1:
    (       # hello
        1,  # last line
        2,  # second line
    )
''', r'''
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
''', r'''
(
    3,  # third line
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[1]
   0] Constant 3 - 1,4..1,5
  .ctx Load
'''),

(26, 'body[0].value', 1, 2, None, {}, ('exec',
r'''{1: 2, **b, **c}'''),
r'''{1: 2, **c}''', r'''
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
''',
r'''{**b}''', r'''
Dict - ROOT 0,0..0,5
  .keys[1]
   0] None
  .values[1]
   0] Name 'b' Load - 0,3..0,4
'''),

(27, 'body[0].value', None, None, None, {}, ('exec',
r'''{1: 2, **b, **c}'''),
r'''{}''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Dict - 0,0..0,2
''',
r'''{1: 2, **b, **c}''', r'''
Dict - ROOT 0,0..0,16
  .keys[3]
   0] Constant 1 - 0,1..0,2
   1] None
   2] None
  .values[3]
   0] Constant 2 - 0,4..0,5
   1] Name 'b' Load - 0,9..0,10
   2] Name 'c' Load - 0,14..0,15
'''),

(28, 'body[0].value', 2, None, None, {}, ('exec',
r'''{1: 2, **b, **c}'''),
r'''{1: 2, **b}''', r'''
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
''',
r'''{**c}''', r'''
Dict - ROOT 0,0..0,5
  .keys[1]
   0] None
  .values[1]
   0] Name 'c' Load - 0,3..0,4
'''),

(29, 'body[0].value', None, None, None, {}, ('exec', r'''
[
    1,
    2,
    3,
]
'''), r'''
[
]
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 0,0..1,1
     .value List - 0,0..1,1
       .ctx Load
''', r'''
[
    1,
    2,
    3,
]
''', r'''
List - ROOT 0,0..4,1
  .elts[3]
   0] Constant 1 - 1,4..1,5
   1] Constant 2 - 2,4..2,5
   2] Constant 3 - 3,4..3,5
  .ctx Load
'''),

(30, 'body[0].value', 0, 2, None, {}, ('exec', r'''
[
    1,
    2,
    3,
]
'''), r'''
[
    3,
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[1]
        0] Constant 3 - 1,4..1,5
       .ctx Load
''', r'''
[
    1,
    2
]
''', r'''
List - ROOT 0,0..3,1
  .elts[2]
   0] Constant 1 - 1,4..1,5
   1] Constant 2 - 2,4..2,5
  .ctx Load
'''),

(31, 'body[0].value', 1, 2, None, {}, ('exec', r'''
[
    1,
    2,
    3,
]
'''), r'''
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
''', r'''
[
    2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Constant 2 - 1,4..1,5
  .ctx Load
'''),

(32, 'body[0].value', 2, None, None, {}, ('exec', r'''
[
    1,
    2,
    3,
]
'''), r'''
[
    1,
    2
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 2 - 2,4..2,5
       .ctx Load
''', r'''
[
    3,
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Constant 3 - 1,4..1,5
  .ctx Load
'''),

(33, 'body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    1, 2, 3,
    4
]
'''), r'''
[            # hello
    1, 2,
    4
]
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 0,0..3,1
     .value List - 0,0..3,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Constant 4 - 2,4..2,5
       .ctx Load
''',
r'''[3]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Constant 3 - 0,1..0,2
  .ctx Load
'''),

(34, 'body[0].value', 2, 3, None, {}, ('exec', r'''
[            # hello
    1, 2, ( 3
     ), 4
]
'''), r'''
[            # hello
    1, 2, 4
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[3]
        0] Constant 1 - 1,4..1,5
        1] Constant 2 - 1,7..1,8
        2] Constant 4 - 1,10..1,11
       .ctx Load
''', r'''
[( 3
     )]
''', r'''
List - ROOT 0,0..1,7
  .elts[1]
   0] Constant 3 - 0,3..0,4
  .ctx Load
'''),

(35, 'body[0].value', 1, 3, None, {}, ('exec', r'''
[            # hello
    1, 2, ( 3
     ), 4
]
'''), r'''
[            # hello
    1, 4
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 4 - 1,7..1,8
       .ctx Load
''', r'''
[2, ( 3
     )]
''', r'''
List - ROOT 0,0..1,7
  .elts[2]
   0] Constant 2 - 0,1..0,2
   1] Constant 3 - 0,6..0,7
  .ctx Load
'''),

(36, 'body[0].value', 1, None, None, {}, ('exec', r'''
[            # hello
    1, 2, ( 3
     ), 4
]
'''), r'''
[            # hello
    1
]
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 0,0..2,1
     .value List - 0,0..2,1
       .elts[1]
        0] Constant 1 - 1,4..1,5
       .ctx Load
''', r'''
[2, ( 3
     ), 4]
''', r'''
List - ROOT 0,0..1,10
  .elts[3]
   0] Constant 2 - 0,1..0,2
   1] Constant 3 - 0,6..0,7
   2] Constant 4 - 1,8..1,9
  .ctx Load
'''),

(37, 'body[0].value', 0, 3, None, {}, ('exec', r'''
i =                (self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1)),
                id(self) & (_sys.maxsize*2 + 1))
'''), r'''
i =                (
                id(self) & (_sys.maxsize*2 + 1),)
''', r'''
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
''', r'''
(self.__class__.__name__, self._name,
                (self._handle & (_sys.maxsize*2 + 1))
)
''', r'''
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
'''),

(38, 'body[0].value', 0, 1, None, {}, ('exec', r'''
i = namespace = {**__main__.__builtins__.__dict__,
             **__main__.__dict__}
'''), r'''
i = namespace = {
             **__main__.__dict__}
''', r'''
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
''',
r'''{**__main__.__builtins__.__dict__}''', r'''
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
'''),

(39, 'body[0].value', None, 2, None, {}, ('exec', r'''
env = {
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1",
    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}
'''), r'''
env = {
    "PYLAUNCHER_DRYRUN": "1",
    "PYLAUNCHER_LIMIT_TO_COMPANY": "",
    **{k.upper(): v for k, v in (env or {}).items()},
}
''', r'''
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
''', r'''
{
    **{k.upper(): v for k, v in os.environ.items() if k.upper() not in ignore},
    "PYLAUNCHER_DEBUG": "1"
}
''', r'''
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
'''),

(40, 'body[0].value', 5, 7, None, {}, ('exec', r'''
(None, False, True, 12345, 123.45, 'abcde', 'абвгд', b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
'''), r'''
(None, False, True, 12345, 123.45, b'abcde',
            datetime.datetime(2004, 10, 26, 10, 33, 33),
            bytearray(b'abcde'), [12, 345], (12, 345), {'12': 345})
''', r'''
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
''',
r'''('abcde', 'абвгд')''', r'''
Tuple - ROOT 0,0..0,18
  .elts[2]
   0] Constant 'abcde' - 0,1..0,8
   1] Constant 'абвгд' - 0,10..0,17
  .ctx Load
'''),

(41, 'body[0].targets[0]', 1, 2, None, {}, ('exec',
r'''[a, b] = c'''),
r'''[a] = c''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Assign - 0,0..0,7
     .targets[1]
      0] List - 0,0..0,3
        .elts[1]
         0] Name 'a' Store - 0,1..0,2
        .ctx Store
     .value Name 'c' Load - 0,6..0,7
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(42, 'body[0].value', 1, 4, None, {}, ('exec', r'''
{
            'exception': exc,
            'future': fut,
            'message': ('GetQueuedCompletionStatus() returned an '
                        'unexpected event'),
            'status': ('err=%s transferred=%s key=%#x address=%#x'
                       % (err, transferred, key, address),),
                                                 'addr': address}
'''), r'''
{
            'exception': exc,
                                                 'addr': address}
''', r'''
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
''', r'''
{
            'future': fut,
            'message': ('GetQueuedCompletionStatus() returned an '
                        'unexpected event'),
            'status': ('err=%s transferred=%s key=%#x address=%#x'
                       % (err, transferred, key, address),)
}
''', r'''
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
'''),

(43, 'body[0].value', 1, 2, None, {}, ('exec',
r'''(1, (2), 3)'''),
r'''(1, 3)''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Tuple - 0,0..0,6
       .elts[2]
        0] Constant 1 - 0,1..0,2
        1] Constant 3 - 0,4..0,5
       .ctx Load
''',
r'''((2),)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Constant 2 - 0,2..0,3
  .ctx Load
'''),

(44, 'body[0].decorator_list[0].args[0]', 0, 1, None, {}, ('exec', r'''
@patch.dict({'a': 'b'})
class cls: pass
'''), r'''
@patch.dict({})
class cls: pass
''', r'''
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
''',
r'''{'a': 'b'}''', r'''
Dict - ROOT 0,0..0,10
  .keys[1]
   0] Constant 'a' - 0,1..0,4
  .values[1]
   0] Constant 'b' - 0,6..0,9
'''),

(45, 'body[0].body[0].targets[0]', 0, 2, None, {}, ('exec', r'''
class cls:
    a, b = c
'''), r'''
class cls:
    () = c
''', r'''
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
''',
r'''a, b''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
  .ctx Load
'''),

(46, 'body[0].body[0].targets[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    yy, tm, = tm, yy
'''), r'''
if 1:
    yy, = tm, yy
''', r'''
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
''',
r'''tm,''', r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Name 'tm' Load - 0,0..0,2
  .ctx Load
'''),

(47, 'body[0].value', 0, 2, None, {}, ('exec',
r'''{1, 2}'''),
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
''',
r'''{1, 2}''', r'''
Set - ROOT 0,0..0,6
  .elts[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 2 - 0,4..0,5
'''),

(48, 'body[0].value', 0, 0, None, {}, ('exec',
r'''{1, 2}'''),
r'''{1, 2}''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Set - 0,0..0,6
       .elts[2]
        0] Constant 1 - 0,1..0,2
        1] Constant 2 - 0,4..0,5
''',
r'''{*()}''', r'''
Set - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,4
     .value Tuple - 0,2..0,4
       .ctx Load
     .ctx Load
'''),

(49, 'body[0].value', 0, 1, None, {}, ('exec',
r'''1, 2, 3,'''),
r'''2, 3,''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Tuple - 0,0..0,5
       .elts[2]
        0] Constant 2 - 0,0..0,1
        1] Constant 3 - 0,3..0,4
       .ctx Load
''',
r'''1,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Constant 1 - 0,0..0,1
  .ctx Load
'''),

(50, 'body[0].value', 1, 2, None, {}, ('exec',
r'''1, 2, 3,'''),
r'''1, 3,''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Tuple - 0,0..0,5
       .elts[2]
        0] Constant 1 - 0,0..0,1
        1] Constant 3 - 0,3..0,4
       .ctx Load
''',
r'''2,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Constant 2 - 0,0..0,1
  .ctx Load
'''),

(51, 'body[0].value', 2, 3, None, {}, ('exec',
r'''1, 2, 3,'''),
r'''1, 2''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[2]
        0] Constant 1 - 0,0..0,1
        1] Constant 2 - 0,3..0,4
       .ctx Load
''',
r'''3,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Constant 3 - 0,0..0,1
  .ctx Load
'''),

(52, 'body[0].value', 0, 2, None, {}, ('exec',
r'''1, 2, 3,'''),
r'''3,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Constant 3 - 0,0..0,1
       .ctx Load
''',
r'''1, 2''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Constant 1 - 0,0..0,1
   1] Constant 2 - 0,3..0,4
  .ctx Load
'''),

(53, 'body[0].value', 1, 3, None, {}, ('exec',
r'''1, 2, 3,'''),
r'''1,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Constant 1 - 0,0..0,1
       .ctx Load
''',
r'''2, 3,''', r'''
Tuple - ROOT 0,0..0,5
  .elts[2]
   0] Constant 2 - 0,0..0,1
   1] Constant 3 - 0,3..0,4
  .ctx Load
'''),

(54, 'body[0].value', 0, 3, None, {}, ('exec',
r'''1, 2, 3,'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .ctx Load
''',
r'''1, 2, 3,''', r'''
Tuple - ROOT 0,0..0,8
  .elts[3]
   0] Constant 1 - 0,0..0,1
   1] Constant 2 - 0,3..0,4
   2] Constant 3 - 0,6..0,7
  .ctx Load
'''),

(55, 'body[0].value', 1, 2, None, {'trivia': ('-1', '-1')}, ('exec', r'''
[
    1,

    # pre
    2, # line
    # post

    3,
]
'''), r'''
[
    1,

    # pre
    # line
    # post

    3,
]
''', r'''
Module - ROOT 0,0..8,1
  .body[1]
   0] Expr - 0,0..8,1
     .value List - 0,0..8,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 3 - 7,4..7,5
       .ctx Load
''',
r'''[2]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(56, 'body[0].value', 1, 2, None, {'trivia': ('block-1', 'line-1')}, ('exec', r'''
[
    1,

    # pre
    2, # line
    # post

    3,
]
'''), r'''
[
    1,
    # post

    3,
]
''', r'''
Module - ROOT 0,0..5,1
  .body[1]
   0] Expr - 0,0..5,1
     .value List - 0,0..5,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 3 - 4,4..4,5
       .ctx Load
''', r'''
[
    # pre
    2, # line
]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Constant 2 - 2,4..2,5
  .ctx Load
'''),

(57, 'body[0].value', 1, 2, None, {'trivia': ('block+1', 'line+1')}, ('exec', r'''
[
    1,
    # prepre

    # pre
    2, # line
    # post

    3,
]
'''), r'''
[
    1,
    # prepre
    # post

    3,
]
''', r'''
Module - ROOT 0,0..6,1
  .body[1]
   0] Expr - 0,0..6,1
     .value List - 0,0..6,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 3 - 5,4..5,5
       .ctx Load
''', r'''
[

    # pre
    2, # line
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Constant 2 - 3,4..3,5
  .ctx Load
'''),

(58, 'body[0].value', 1, 2, None, {'trivia': ('all-1', 'block-1')}, ('exec', r'''
[
    1,
    # prepre

    # pre
    2, # line
    # post

    3,
]
'''), r'''
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
''', r'''
[
    # prepre

    # pre
    2, # line
    # post
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Constant 2 - 4,4..4,5
  .ctx Load
'''),

(59, 'body[0].value', 1, 2, None, {'trivia': ('all-1', 'all-1')}, ('exec', r'''
[
    1,

    # prepre

    # pre
    2, # line
    # post

    # postpost

    3,
]
'''), r'''
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
''', r'''
[
    # prepre

    # pre
    2, # line
    # post

    # postpost
]
''', r'''
List - ROOT 0,0..8,1
  .elts[1]
   0] Constant 2 - 4,4..4,5
  .ctx Load
'''),

(60, 'body[0].value', 1, 2, None, {'trivia': ('all+1', 'all+1')}, ('exec', r'''
[
    1,

    # prepre

    # pre
    2, # line
    # post

    # postpost

    3,
]
'''), r'''
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
''', r'''
[

    # prepre

    # pre
    2, # line
    # post

    # postpost

]
''', r'''
List - ROOT 0,0..10,1
  .elts[1]
   0] Constant 2 - 5,4..5,5
  .ctx Load
'''),

(61, 'body[0].value', 1, 2, None, {'trivia': ('all+1', 'all+1')}, ('exec', r'''
[
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
]
'''), r'''
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
''', r'''
[
    \
    # prepre
    \
    # pre
    2, # line
    # post
    \
    # postpost
    \
]
''', r'''
List - ROOT 0,0..10,1
  .elts[1]
   0] Constant 2 - 5,4..5,5
  .ctx Load
'''),

(62, 'body[0].value', 1, 2, None, {'trivia': (3, 5)}, ('exec', r'''
[
    1,
    # prepre
    # pre
    2, # line
    # post
    # postpost
    3,
]
'''), r'''
[
    1,
    # prepre
    # postpost
    3,
]
''', r'''
Module - ROOT 0,0..5,1
  .body[1]
   0] Expr - 0,0..5,1
     .value List - 0,0..5,1
       .elts[2]
        0] Constant 1 - 1,4..1,5
        1] Constant 3 - 4,4..4,5
       .ctx Load
''', r'''
[
    # pre
    2, # line
    # post
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Constant 2 - 2,4..2,5
  .ctx Load
'''),

(63, 'body[0].value', 1, 2, None, {}, ('exec', r'''
[
    1, \
    2, \
    3,
]
'''), r'''
[
    1, \
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
''', r'''
[
    2, \
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Constant 2 - 1,4..1,5
  .ctx Load
'''),

(64, 'body[0].value', 1, 2, None, {}, ('exec', r'''
[
    1, 2, \
    3,
]
'''), r'''
[
    1, \
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
''',
r'''[2]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Constant 2 - 0,1..0,2
  .ctx Load
'''),

(65, 'body[0].value', 1, 2, None, {}, ('exec', r'''
{a: b,

    # pre
    c: d,  # line
    # post

    e: f}
'''), r'''
{a: b,

    # post

    e: f}
''', r'''
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
''', r'''
{
    # pre
    c: d,  # line
}
''', r'''
Dict - ROOT 0,0..3,1
  .keys[1]
   0] Name 'c' Load - 2,4..2,5
  .values[1]
   0] Name 'd' Load - 2,7..2,8
'''),

(66, 'body[0].value', 1, 2, None, {'trivia': (False, 'block+1')}, ('exec', r'''
{a: b,

    # pre
    c: d,  # line
    # post

    e: f}
'''), r'''
{a: b,

    # pre
    e: f}
''', r'''
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
''', r'''
{
    c: d,  # line
    # post

}
''', r'''
Dict - ROOT 0,0..4,1
  .keys[1]
   0] Name 'c' Load - 1,4..1,5
  .values[1]
   0] Name 'd' Load - 1,7..1,8
'''),

(67, 'body[0].value', 1, 2, None, {}, ('exec',
r'''{**a, **b, **c}'''),
r'''{**a, **c}''', r'''
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
''',
r'''{**b}''', r'''
Dict - ROOT 0,0..0,5
  .keys[1]
   0] None
  .values[1]
   0] Name 'b' Load - 0,3..0,4
'''),

(68, 'body[0].cases[0].pattern', 0, 0, None, {'norm_get': False, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), r'''
match a:
 case a | b: pass
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
             .name 'a'
           1] MatchAs - 1,10..1,11
             .name 'b'
        .body[1]
         0] Pass - 1,13..1,17
''',
r'''''',
r'''MatchOr - ROOT 0,0..0,0'''),

(69, 'body[0].cases[0].pattern', 0, 1, None, {'norm_get': False, 'norm_self': False, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), r'''
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
''',
r'''a''', r'''
MatchOr - ROOT 0,0..0,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

(70, 'body[0].cases[0].pattern', 0, 2, None, {'norm_self': False, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), r'''
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
''',
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

(71, 'body[0].cases[0].pattern', 0, 1, None, {'norm_get': True, 'norm_self': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), r'''
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
''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

(72, 'body[0].cases[0].pattern', 1, 2, None, {}, ('exec', r'''
match a:
 case (a |
# pre
b | # line1
c | # line2
# post
d): pass
'''), r'''
match a:
 case (a |
c | # line2
# post
d): pass
''', r'''
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
''', r'''

# pre
b # line1

''', r'''
MatchAs - ROOT 2,0..2,1
  .name 'b'
'''),

(73, 'body[0].cases[0].pattern', 1, 3, None, {'trivia': (None, 'block')}, ('exec', r'''
match a:
 case (a |
# pre
b | # line1
c | # line2
# post
d): pass
'''), r'''
match a:
 case (a |
d): pass
''', r'''
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
''', r'''

# pre
(b | # line1
c) # line2
# post

''', r'''
MatchOr - ROOT 2,1..3,1
  .patterns[2]
   0] MatchAs - 2,1..2,2
     .name 'b'
   1] MatchAs - 3,0..3,1
     .name 'c'
'''),

(74, 'body[0]', 0, 2, None, {}, ('exec',
r'''del a, b, c'''),
r'''del c''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'c' Del - 0,4..0,5
''',
r'''a, b''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
  .ctx Load
'''),

(75, 'body[0]', 1, 3, None, {}, ('exec',
r'''del a, b, c'''),
r'''del a''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'a' Del - 0,4..0,5
''',
r'''b, c''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 0,3..0,4
  .ctx Load
'''),
],

'docstr': [  # ................................................................................

(0, '', 0, 4, None, {}, ('exec', r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
pass
'''),
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
''', r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
''', r'''
Module - ROOT 0,0..5,8
  .body[4]
   0] Expr - 0,0..1,8
     .value Constant 'One\n  Two' - 0,0..1,8
   1] Expr - 2,0..3,9
     .value Constant 'Three\n  Four' - 2,0..3,9
   2] Expr - 4,0..4,1
     .value Name 'i' Load - 4,0..4,1
   3] Expr - 4,4..5,8
     .value Constant 'Five\n  Six' - 4,4..5,8
'''),

(1, 'body[0]', 0, 4, None, {}, ('exec', r'''
def f():
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
    pass
'''), r'''
def f():
    pass
''', r'''
Module - ROOT 0,0..1,8
  .body[1]
   0] FunctionDef - 0,0..1,8
     .name 'f'
     .body[1]
      0] Pass - 1,4..1,8
''', r'''
"""One
  Two"""
"""Three
  Four"""
i ; """Five
  Six"""
''', r'''
Module - ROOT 0,0..5,8
  .body[4]
   0] Expr - 0,0..1,8
     .value Constant 'One\n  Two' - 0,0..1,8
   1] Expr - 2,0..3,9
     .value Constant 'Three\n  Four' - 2,0..3,9
   2] Expr - 4,0..4,1
     .value Name 'i' Load - 4,0..4,1
   3] Expr - 4,4..5,8
     .value Constant 'Five\n  Six' - 4,4..5,8
'''),

(2, 'body[0]', 0, 4, None, {'docstr': 'strict'}, ('exec', r'''
def f():
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
    pass
'''), r'''
def f():
    pass
''', r'''
Module - ROOT 0,0..1,8
  .body[1]
   0] FunctionDef - 0,0..1,8
     .name 'f'
     .body[1]
      0] Pass - 1,4..1,8
''', r'''
"""One
  Two"""
"""Three
      Four"""
i ; """Five
      Six"""
''', r'''
Module - ROOT 0,0..5,12
  .body[4]
   0] Expr - 0,0..1,8
     .value Constant 'One\n  Two' - 0,0..1,8
   1] Expr - 2,0..3,13
     .value Constant 'Three\n      Four' - 2,0..3,13
   2] Expr - 4,0..4,1
     .value Name 'i' Load - 4,0..4,1
   3] Expr - 4,4..5,12
     .value Constant 'Five\n      Six' - 4,4..5,12
'''),

(3, 'body[0]', 0, 4, None, {'docstr': False}, ('exec', r'''
def f():
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
    pass
'''), r'''
def f():
    pass
''', r'''
Module - ROOT 0,0..1,8
  .body[1]
   0] FunctionDef - 0,0..1,8
     .name 'f'
     .body[1]
      0] Pass - 1,4..1,8
''', r'''
"""One
      Two"""
"""Three
      Four"""
i ; """Five
      Six"""
''', r'''
Module - ROOT 0,0..5,12
  .body[4]
   0] Expr - 0,0..1,12
     .value Constant 'One\n      Two' - 0,0..1,12
   1] Expr - 2,0..3,13
     .value Constant 'Three\n      Four' - 2,0..3,13
   2] Expr - 4,0..4,1
     .value Name 'i' Load - 4,0..4,1
   3] Expr - 4,4..5,12
     .value Constant 'Five\n      Six' - 4,4..5,12
'''),

(4, 'body[0]', 1, 4, None, {}, ('exec', r'''
def f():
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
    pass
'''), r'''
def f():
    """One
      Two"""
    pass
''', r'''
Module - ROOT 0,0..3,8
  .body[1]
   0] FunctionDef - 0,0..3,8
     .name 'f'
     .body[2]
      0] Expr - 1,4..2,12
        .value Constant 'One\n      Two' - 1,4..2,12
      1] Pass - 3,4..3,8
''', r'''
"""Three
  Four"""
i ; """Five
  Six"""
''', r'''
Module - ROOT 0,0..3,8
  .body[3]
   0] Expr - 0,0..1,9
     .value Constant 'Three\n  Four' - 0,0..1,9
   1] Expr - 2,0..2,1
     .value Name 'i' Load - 2,0..2,1
   2] Expr - 2,4..3,8
     .value Constant 'Five\n  Six' - 2,4..3,8
'''),

(5, 'body[0]', 1, 4, None, {'docstr': 'strict'}, ('exec', r'''
def f():
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
    pass
'''), r'''
def f():
    """One
      Two"""
    pass
''', r'''
Module - ROOT 0,0..3,8
  .body[1]
   0] FunctionDef - 0,0..3,8
     .name 'f'
     .body[2]
      0] Expr - 1,4..2,12
        .value Constant 'One\n      Two' - 1,4..2,12
      1] Pass - 3,4..3,8
''', r'''
"""Three
      Four"""
i ; """Five
      Six"""
''', r'''
Module - ROOT 0,0..3,12
  .body[3]
   0] Expr - 0,0..1,13
     .value Constant 'Three\n      Four' - 0,0..1,13
   1] Expr - 2,0..2,1
     .value Name 'i' Load - 2,0..2,1
   2] Expr - 2,4..3,12
     .value Constant 'Five\n      Six' - 2,4..3,12
'''),

(6, 'body[0]', 1, 4, None, {'docstr': False}, ('exec', r'''
def f():
    """One
      Two"""
    """Three
      Four"""
    i ; """Five
      Six"""
    pass
'''), r'''
def f():
    """One
      Two"""
    pass
''', r'''
Module - ROOT 0,0..3,8
  .body[1]
   0] FunctionDef - 0,0..3,8
     .name 'f'
     .body[2]
      0] Expr - 1,4..2,12
        .value Constant 'One\n      Two' - 1,4..2,12
      1] Pass - 3,4..3,8
''', r'''
"""Three
      Four"""
i ; """Five
      Six"""
''', r'''
Module - ROOT 0,0..3,12
  .body[3]
   0] Expr - 0,0..1,13
     .value Constant 'Three\n      Four' - 0,0..1,13
   1] Expr - 2,0..2,1
     .value Name 'i' Load - 2,0..2,1
   2] Expr - 2,4..3,12
     .value Constant 'Five\n      Six' - 2,4..3,12
'''),
],

'exprish_trivia_leading': [  # ................................................................................

(0, '', 1, 2, None, {'trivia': (False, False)}, (None, r'''
[a,
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(1, '', 1, 2, None, {'trivia': (False, False)}, (None, r'''
[a,
# 1
b]
'''), r'''
[a
# 1
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(2, '', 1, 2, None, {'trivia': (False, False)}, (None, r'''
[a,

b]
'''), r'''
[a

]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(3, '', 1, 2, None, {'trivia': (False, False)}, (None, r'''
[a,
\
b]
'''), r'''
[a
\
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(4, '', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
[a,
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(5, '', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
[a,
# 1
b]
'''), r'''
[a
# 1
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(6, '', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
[a,

b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[

b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(7, '', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
[a,
\
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
\
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(8, '', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
[a,
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(9, '', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
[a,
# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 1
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(10, '', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
[a,

b]
'''), r'''
[a

]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(11, '', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
[a,
\
b]
'''), r'''
[a
\
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''',
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(12, '', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
[a,


# 1
b]
'''), r'''
[a

]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[

# 1
b]
''', r'''
List - ROOT 0,0..3,2
  .elts[1]
   0] Name 'b' Load - 3,0..3,1
  .ctx Load
'''),

(13, '', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
[a,

\
# 1
b]
'''), r'''
[a

]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
\
# 1
b]
''', r'''
List - ROOT 0,0..3,2
  .elts[1]
   0] Name 'b' Load - 3,0..3,1
  .ctx Load
'''),

(14, '', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
[a,
\

# 1
b]
'''), r'''
[a
\
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[

# 1
b]
''', r'''
List - ROOT 0,0..3,2
  .elts[1]
   0] Name 'b' Load - 3,0..3,1
  .ctx Load
'''),

(15, '', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
[a,


# 1
b]
'''), r'''
[a

]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 1
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(16, '', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
[a,

\
# 1
b]
'''), r'''
[a

]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 1
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(17, '', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
[a,
\

# 1
b]
'''), r'''
[a
\
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 1
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(18, '', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
[a,


# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[


# 1
b]
''', r'''
List - ROOT 0,0..4,2
  .elts[1]
   0] Name 'b' Load - 4,0..4,1
  .ctx Load
'''),

(19, '', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
[a,

\
# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[

\
# 1
b]
''', r'''
List - ROOT 0,0..4,2
  .elts[1]
   0] Name 'b' Load - 4,0..4,1
  .ctx Load
'''),

(20, '', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
[a,
\

# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
\

# 1
b]
''', r'''
List - ROOT 0,0..4,2
  .elts[1]
   0] Name 'b' Load - 4,0..4,1
  .ctx Load
'''),

(21, '', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
[a,


# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 1
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(22, '', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
[a,

\
# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 1
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(23, '', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
[a,
\

# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 1
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(24, '', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
[a,


# 2


# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[


# 2


# 1
b]
''', r'''
List - ROOT 0,0..7,2
  .elts[1]
   0] Name 'b' Load - 7,0..7,1
  .ctx Load
'''),

(25, '', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
[a,

\
# 2

\
# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[

\
# 2

\
# 1
b]
''', r'''
List - ROOT 0,0..7,2
  .elts[1]
   0] Name 'b' Load - 7,0..7,1
  .ctx Load
'''),

(26, '', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
[a,
\

# 2
\

# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
\

# 2
\

# 1
b]
''', r'''
List - ROOT 0,0..7,2
  .elts[1]
   0] Name 'b' Load - 7,0..7,1
  .ctx Load
'''),

(27, '', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
[a,


# 2


# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 2


# 1
b]
''', r'''
List - ROOT 0,0..5,2
  .elts[1]
   0] Name 'b' Load - 5,0..5,1
  .ctx Load
'''),

(28, '', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
[a,

\
# 2

\
# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 2

\
# 1
b]
''', r'''
List - ROOT 0,0..5,2
  .elts[1]
   0] Name 'b' Load - 5,0..5,1
  .ctx Load
'''),

(29, '', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
[a,
\

# 2
\

# 1
b]
'''), r'''
[a
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
''', r'''
[
# 2
\

# 1
b]
''', r'''
List - ROOT 0,0..5,2
  .elts[1]
   0] Name 'b' Load - 5,0..5,1
  .ctx Load
'''),
],

'exprish_trivia_trailing': [  # ................................................................................

(0, '', 0, 1, None, {'trivia': (False, False)}, (None, r'''
[a,
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(1, '', 0, 1, None, {'trivia': (False, False)}, (None, r'''
[a, # 1
b]
'''), r'''
[# 1
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(2, '', 0, 1, None, {'trivia': (False, False)}, (None, r'''
[a,

b]
'''), r'''
[

b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(3, '', 0, 1, None, {'trivia': (False, False)}, (None, r'''
[a,
\
b]
'''), r'''
[
\
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(4, '', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
[a,
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(5, '', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
[a, # 1
b]
'''), r'''
[# 1
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(6, '', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
[a,

b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a

]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(7, '', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
[a,
\
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a
\
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(8, '', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
[a,
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(9, '', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
[a, # 1
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(10, '', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
[a,

b]
'''), r'''
[

b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(11, '', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
[a,
\
b]
'''), r'''
[
\
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(12, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
[a,
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(13, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
[a, # 1
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(14, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
[a,  # 1

b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a,  # 1

]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(15, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
[a,  # 1
\
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a,  # 1
\
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(16, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
[a,
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(17, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
[a,

b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''',
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(18, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
[a, # 1
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(19, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
[a,  # 1

b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a,  # 1
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(20, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
[a,  # 1
\
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a,  # 1
]
''', r'''
List - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(21, '', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
[a, # 1
# 2


b]
'''), r'''
[


b]
''', r'''
List - ROOT 0,0..3,2
  .elts[1]
   0] Name 'b' Load - 3,0..3,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(22, '', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
[a, # 1
# 2
\

b]
'''), r'''
[
\

b]
''', r'''
List - ROOT 0,0..3,2
  .elts[1]
   0] Name 'b' Load - 3,0..3,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(23, '', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
[a, # 1
# 2

\
b]
'''), r'''
[

\
b]
''', r'''
List - ROOT 0,0..3,2
  .elts[1]
   0] Name 'b' Load - 3,0..3,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(24, '', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
[a, # 1
# 2


b]
'''), r'''
[

b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''', r'''
[a, # 1
# 2

]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(25, '', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
[a, # 1
# 2
\

b]
'''), r'''
[

b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''', r'''
[a, # 1
# 2
\
]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(26, '', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
[a, # 1
# 2

\
b]
'''), r'''
[
\
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''', r'''
[a, # 1
# 2

]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(27, '', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
[a, # 1
# 2


b]
'''), r'''
[

b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(28, '', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
[a, # 1
# 2
\

b]
'''), r'''
[

b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(29, '', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
[a, # 1
# 2

\
b]
'''), r'''
[
\
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(30, '', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
[a, # 1
# 2


b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2


]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(31, '', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
[a, # 1
# 2
\

b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2
\

]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(32, '', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
[a, # 1
# 2

\
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2

\
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(33, '', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
[a, # 1
# 2


b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(34, '', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
[a, # 1
# 2
\

b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(35, '', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
[a, # 1
# 2

\
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(36, '', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
[a, # 1
# 2


# 3


b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2


# 3


]
''', r'''
List - ROOT 0,0..7,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(37, '', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
[a, # 1
# 2
\

# 3
\

b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2
\

# 3
\

]
''', r'''
List - ROOT 0,0..7,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(38, '', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
[a, # 1
# 2

\
# 3

\
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2

\
# 3

\
]
''', r'''
List - ROOT 0,0..7,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(39, '', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
[a, # 1
# 2


# 3


b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2


# 3
]
''', r'''
List - ROOT 0,0..5,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(40, '', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
[a, # 1
# 2
\

# 3
\

b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2
\

# 3
]
''', r'''
List - ROOT 0,0..5,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(41, '', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
[a, # 1
# 2

\
# 3

\
b]
'''), r'''
[
b]
''', r'''
List - ROOT 0,0..1,2
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
''', r'''
[a, # 1
# 2

\
# 3
]
''', r'''
List - ROOT 0,0..5,1
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),
],

'stmtish_trivia_leading (currently not entirely to spec)': [  # ................................................................................

(0, '', 1, 2, None, {'trivia': (False, False)}, (None, r'''
a
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(1, '', 1, 2, None, {'trivia': (False, False)}, (None, r'''
a
# 1
b
'''), r'''
a
# 1
''', r'''
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(2, '', 1, 2, None, {'trivia': (False, False)}, (None, r'''
a

b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(3, '', 1, 2, None, {'trivia': (False, False)}, (None, r'''
a
\
b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(4, '', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
a
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(5, '', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
a
# 1
b
'''), r'''
a
# 1
''', r'''
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(6, '', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
a

b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(7, '', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
a
\
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(8, '', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
a
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(9, '', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
a
# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(10, '', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
a

b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(11, '', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
a
\
b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

(12, '', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
a


# 1
b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(13, '', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
a

\
# 1
b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(14, '', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
a
\

# 1
b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(15, '', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
a


# 1
b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(16, '', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
a

\
# 1
b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(17, '', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
a
\

# 1
b
'''), r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(18, '', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
a


# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(19, '', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
a

\
# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(20, '', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
a
\

# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(21, '', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
a


# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(22, '', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
a

\
# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(23, '', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
a
\

# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

(24, '', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
a


# 2


# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 2


# 1
b
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 4,0..4,1
     .value Name 'b' Load - 4,0..4,1
'''),

(25, '', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
a

\
# 2

\
# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 2

\
# 1
b
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 4,0..4,1
     .value Name 'b' Load - 4,0..4,1
'''),

(26, '', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
a
\

# 2
\

# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 2
\

# 1
b
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 4,0..4,1
     .value Name 'b' Load - 4,0..4,1
'''),

(27, '', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
a


# 2


# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 2


# 1
b
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 4,0..4,1
     .value Name 'b' Load - 4,0..4,1
'''),

(28, '', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
a

\
# 2

\
# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 2

\
# 1
b
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 4,0..4,1
     .value Name 'b' Load - 4,0..4,1
'''),

(29, '', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
a
\

# 2
\

# 1
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''
# 2
\

# 1
b
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 4,0..4,1
     .value Name 'b' Load - 4,0..4,1
'''),
],

'stmtish_trivia_trailing (currently not entirely to spec)': [  # ................................................................................

(0, '', 0, 1, None, {'trivia': (False, False)}, (None, r'''
a
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(1, '', 0, 1, None, {'trivia': (False, False)}, (None, r'''
a # 1
b
'''), r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(2, '', 0, 1, None, {'trivia': (False, False)}, (None, r'''
a

b
'''), r'''

b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(3, '', 0, 1, None, {'trivia': (False, False)}, (None, r'''
a
\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(4, '', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
a
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(5, '', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
a # 1
b
'''), r'''
# 1
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(6, '', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
a

b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(7, '', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
a
\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(8, '', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
a
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(9, '', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
a # 1
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a # 1

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(10, '', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
a

b
'''), r'''

b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(11, '', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
a
\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(12, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
a
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(13, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
a

b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(14, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
a # 1
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a # 1

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(15, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
a  # 1

b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a  # 1

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(16, '', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
a  # 1
\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a  # 1

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(17, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
a
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(18, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
a

b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(19, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
a # 1
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a # 1

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(20, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
a  # 1

b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a  # 1

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(21, '', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
a  # 1
\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a  # 1

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(22, '', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
a # 1
# 2


b
'''), r'''


b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(23, '', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
a # 1
# 2
\

b
'''), r'''
\

b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(24, '', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
a # 1
# 2

\
b
'''), r'''

\
b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(25, '', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
a # 1
# 2


b
'''), r'''

b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(26, '', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
a # 1
# 2
\

b
'''), r'''
\

b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(27, '', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
a # 1
# 2

\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(28, '', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
a # 1
# 2


b
'''), r'''

b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(29, '', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
a # 1
# 2
\

b
'''), r'''
\

b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(30, '', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
a # 1
# 2

\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(31, '', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
a # 1
# 2


b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(32, '', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
a # 1
# 2
\

b
'''), r'''
\

b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(33, '', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
a # 1
# 2

\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(34, '', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
a # 1
# 2


b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(35, '', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
a # 1
# 2
\

b
'''), r'''
\

b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(36, '', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
a # 1
# 2

\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a # 1
# 2

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(37, '', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
a # 1
# 2


# 3


b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a # 1
# 2


# 3

''', r'''
Module - ROOT 0,0..5,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(38, '', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
a # 1
# 2
\

# 3
\

b
'''), r'''
\

b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2
\

# 3

''', r'''
Module - ROOT 0,0..5,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(39, '', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
a # 1
# 2

\
# 3

\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a # 1
# 2

\
# 3

''', r'''
Module - ROOT 0,0..5,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(40, '', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
a # 1
# 2


# 3


b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a # 1
# 2


# 3

''', r'''
Module - ROOT 0,0..5,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(41, '', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
a # 1
# 2
\

# 3
\

b
'''), r'''
\

b
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''', r'''
a # 1
# 2
\

# 3

''', r'''
Module - ROOT 0,0..5,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

(42, '', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
a # 1
# 2

\
# 3

\
b
'''), r'''
\
b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''', r'''
a # 1
# 2

\
# 3

''', r'''
Module - ROOT 0,0..5,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),
],

'stmtish_trailing_newline': [  # ................................................................................

(0, '', 1, 2, None, {}, (None, r'''
if 1:
    i = 1
    j = 2
'''), r'''
if 1:
    i = 1
''', r'''
If - ROOT 0,0..1,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'i' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
''',
r'''j = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(1, '', 1, 2, None, {}, (None, r'''
if 1:
    i = 1
    j = 2  # comment
'''), r'''
if 1:
    i = 1
''', r'''
If - ROOT 0,0..1,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'i' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
''',
r'''j = 2  # comment''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(2, '', 1, 2, None, {}, (None, r'''
if 1:
    i = 1
    j = 2  # comment

'''), r'''
if 1:
    i = 1

''', r'''
If - ROOT 0,0..1,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'i' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
''', r'''
j = 2  # comment

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(3, '', 1, 2, None, {}, (None, r'''
if 1:
    i = 1
    j = 2

'''), r'''
if 1:
    i = 1

''', r'''
If - ROOT 0,0..1,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'i' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
''',
r'''j = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(4, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2
'''), r'''
if 1:
    i = 1
''', r'''
Module - ROOT 0,0..1,9
  .body[1]
   0] If - 0,0..1,9
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
''',
r'''j = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(5, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2  # comment
'''), r'''
if 1:
    i = 1
''', r'''
Module - ROOT 0,0..1,9
  .body[1]
   0] If - 0,0..1,9
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
''',
r'''j = 2  # comment''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(6, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2  # comment

'''), r'''
if 1:
    i = 1

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] If - 0,0..1,9
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
''', r'''
j = 2  # comment

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(7, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i = 1
    j = 2

'''), r'''
if 1:
    i = 1

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] If - 0,0..1,9
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'i' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
''',
r'''j = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(8, '', 1, 2, None, {}, ('exec', r'''
i = 1
j = 2
'''),
r'''i = 1''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
''',
r'''j = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(9, '', 1, 2, None, {}, ('exec', r'''
i = 1
j = 2

'''), r'''
i = 1

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
''',
r'''j = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(10, '', 0, 1, None, {}, ('exec',
r'''i = 1'''),
r'''''',
r'''Module - ROOT 0,0..0,0''',
r'''i = 1''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
'''),

(11, '', 0, 1, None, {}, ('exec', r'''
i = 1

'''),
r'''''',
r'''Module - ROOT 0,0..0,0''',
r'''i = 1''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
'''),

(12, '', 0, 1, None, {}, ('exec', r'''
i = 1


'''), r'''


''',
r'''Module - ROOT 0,0..1,0''',
r'''i = 1''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
'''),
],

'stmtish_trailing_semicolon': [  # ................................................................................

(0, '', 1, 2, None, {}, (None, r'''
a = 1;
b = 2;
'''),
r'''a = 1;''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
''',
r'''b = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(1, '', 1, 2, None, {}, (None, r'''
if 1:
    a = 1;
    b = 2;
'''), r'''
if 1:
    a = 1;
''', r'''
If - ROOT 0,0..1,10
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Assign - 1,4..1,9
     .targets[1]
      0] Name 'a' Store - 1,4..1,5
     .value Constant 1 - 1,8..1,9
''',
r'''b = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(2, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    a = 1;
    b = 2;
'''), r'''
if 1:
    a = 1;
''', r'''
Module - ROOT 0,0..1,10
  .body[1]
   0] If - 0,0..1,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'a' Store - 1,4..1,5
        .value Constant 1 - 1,8..1,9
''',
r'''b = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

(3, 'body[0]', 1, 2, None, {}, ('exec',
r'''if 1: a = 1; b = 2;'''),
r'''if 1: a = 1''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] If - 0,0..0,11
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Assign - 0,6..0,11
        .targets[1]
         0] Name 'a' Store - 0,6..0,7
        .value Constant 1 - 0,10..0,11
''',
r'''b = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),
],

'Tuple_elts': [  # ................................................................................

(0, 'slice', None, None, None, {'_ver': 11}, (None,
r'''a[*not a, b, *c or d, *e]'''),
r'''a[()]''', r'''
Subscript - ROOT 0,0..0,5
  .value Name 'a' Load - 0,0..0,1
  .slice Tuple - 0,2..0,4
    .ctx Load
  .ctx Load
''',
r'''*(not a), b, *(c or d), *e''', r'''
Tuple - ROOT 0,0..0,26
  .elts[4]
   0] Starred - 0,0..0,8
     .value UnaryOp - 0,2..0,7
       .op Not - 0,2..0,5
       .operand Name 'a' Load - 0,6..0,7
     .ctx Load
   1] Name 'b' Load - 0,10..0,11
   2] Starred - 0,13..0,22
     .value BoolOp - 0,15..0,21
       .op Or
       .values[2]
        0] Name 'c' Load - 0,15..0,16
        1] Name 'd' Load - 0,20..0,21
     .ctx Load
   3] Starred - 0,24..0,26
     .value Name 'e' Load - 0,25..0,26
     .ctx Load
  .ctx Load
'''),

(1, 'slice', None, None, None, {'_ver': 11, 'pars': False, '_verify_get': False}, (None,
r'''a[*not a, b, *c or d, *e]'''),
r'''a[()]''', r'''
Subscript - ROOT 0,0..0,5
  .value Name 'a' Load - 0,0..0,1
  .slice Tuple - 0,2..0,4
    .ctx Load
  .ctx Load
''',
r'''*not a, b, *c or d, *e''', r'''
Tuple - ROOT 0,0..0,22
  .elts[4]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'a' Load - 0,5..0,6
     .ctx Load
   1] Name 'b' Load - 0,8..0,9
   2] Starred - 0,11..0,18
     .value BoolOp - 0,12..0,18
       .op Or
       .values[2]
        0] Name 'c' Load - 0,12..0,13
        1] Name 'd' Load - 0,17..0,18
     .ctx Load
   3] Starred - 0,20..0,22
     .value Name 'e' Load - 0,21..0,22
     .ctx Load
  .ctx Load
'''),

(2, 'slice', None, None, None, {'_ver': 11, 'pars_arglike': False, '_verify_get': False}, (None,
r'''a[*not a, b, *c or d, *e]'''),
r'''a[()]''', r'''
Subscript - ROOT 0,0..0,5
  .value Name 'a' Load - 0,0..0,1
  .slice Tuple - 0,2..0,4
    .ctx Load
  .ctx Load
''',
r'''*not a, b, *c or d, *e''', r'''
Tuple - ROOT 0,0..0,22
  .elts[4]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'a' Load - 0,5..0,6
     .ctx Load
   1] Name 'b' Load - 0,8..0,9
   2] Starred - 0,11..0,18
     .value BoolOp - 0,12..0,18
       .op Or
       .values[2]
        0] Name 'c' Load - 0,12..0,13
        1] Name 'd' Load - 0,17..0,18
     .ctx Load
   3] Starred - 0,20..0,22
     .value Name 'e' Load - 0,21..0,22
     .ctx Load
  .ctx Load
'''),
],

'Delete_targets': [  # ................................................................................

(0, 'body[0]', 1, 2, None, {}, ('exec',
r'''del a, b, c  # comment'''),
r'''del a, c  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Delete - 0,0..0,8
     .targets[2]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'c' Del - 0,7..0,8
''',
r'''b,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'b' Load - 0,0..0,1
  .ctx Load
'''),

(1, 'body[0]', 1, 3, None, {}, ('exec',
r'''del a, b, c  # comment'''),
r'''del a  # comment''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'a' Del - 0,4..0,5
''',
r'''b, c''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 0,3..0,4
  .ctx Load
'''),

(2, 'body[0]', 0, 2, None, {}, ('exec',
r'''del a, b, c  # comment'''),
r'''del c  # comment''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'c' Del - 0,4..0,5
''',
r'''a, b''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
  .ctx Load
'''),

(3, 'body[0]', 1, 2, None, {}, ('exec', r'''
del a \
, \
b \
, \
c  # comment
'''), r'''
del a \
, \
c  # comment
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] Delete - 0,0..2,1
     .targets[2]
      0] Name 'a' Del - 0,4..0,5
      1] Name 'c' Del - 2,0..2,1
''', r'''
(
b \
, \
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
'''),

(4, 'body[0]', 0, 2, None, {}, ('exec', r'''
del a \
, \
b \
, \
c  # comment
'''), r'''
del \
c  # comment
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Delete - 0,0..1,1
     .targets[1]
      0] Name 'c' Del - 1,0..1,1
''', r'''
a \
, \
b \
,
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(5, 'body[0]', 1, 3, None, {}, ('exec', r'''
del a \
, \
b \
, \
c  # comment
'''), r'''
del a \
 \
  # comment
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] Delete - 0,0..0,5
     .targets[1]
      0] Name 'a' Del - 0,4..0,5
''', r'''
(
b \
, \
c)
''', r'''
Tuple - ROOT 0,0..3,2
  .elts[2]
   0] Name 'b' Load - 1,0..1,1
   1] Name 'c' Load - 3,0..3,1
  .ctx Load
'''),

(6, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  del a \
  , \
  b # comment
  pass
'''), r'''
if 1:
  del  \
  b # comment
  pass
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] If - 0,0..3,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Delete - 1,2..2,3
        .targets[1]
         0] Name 'b' Del - 2,2..2,3
      1] Pass - 3,2..3,6
''', r'''
a \
,
''', r'''
Tuple - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

(7, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  del a \
  , \
  b # comment
  pass
'''), r'''
if 1:
  del a \
   \
   # comment
  pass
''', r'''
Module - ROOT 0,0..4,6
  .body[1]
   0] If - 0,0..4,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Delete - 1,2..1,7
        .targets[1]
         0] Name 'a' Del - 1,6..1,7
      1] Pass - 4,2..4,6
''',
r'''b,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'b' Load - 0,0..0,1
  .ctx Load
'''),

(8, '', 0, 3, None, {}, (None,
r'''del a, b, c'''),
r'''**ValueError('cannot cut all Delete.targets without norm_self=False')**''',
r'''a, b, c''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'c' Load - 0,6..0,7
  .ctx Load
'''),

(9, '', 0, 3, None, {'norm_self': False, '_verify_self': False}, (None, r'''
del a \
, \
b \
, \
c  # comment
'''),
r'''del   # comment''',
r'''Delete - ROOT 0,0..0,4''', r'''
a \
, \
b \
, \
c
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 2,0..2,1
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

(10, 'body[0]', 1, 2, None, {}, (None, r'''
if 1:
  del a, b;
'''), r'''
if 1:
  del a;
''', r'''
If - ROOT 0,0..1,8
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Delete - 1,2..1,7
     .targets[1]
      0] Name 'a' Del - 1,6..1,7
''',
r'''b,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'b' Load - 0,0..0,1
  .ctx Load
'''),
],

'Assign_targets': [  # ................................................................................

(0, 'body[0]', 0, 2, 'targets', {}, ('exec',
r'''a = b = c = z'''),
r'''c = z''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'c' Store - 0,0..0,1
     .value Name 'z' Load - 0,4..0,5
''',
r'''a = b =''', r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
'''),

(1, 'body[0]', 1, 2, 'targets', {}, ('exec',
r'''a = b = c = z'''),
r'''a = c = z''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Assign - 0,0..0,9
     .targets[2]
      0] Name 'a' Store - 0,0..0,1
      1] Name 'c' Store - 0,4..0,5
     .value Name 'z' Load - 0,8..0,9
''',
r'''b =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'b' Store - 0,0..0,1
'''),

(2, 'body[0]', 1, 3, 'targets', {}, ('exec',
r'''a = b = c = z'''),
r'''a = z''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Name 'z' Load - 0,4..0,5
''',
r'''b = c =''', r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'b' Store - 0,0..0,1
   1] Name 'c' Store - 0,4..0,5
'''),

(3, 'body[0]', 2, 3, 'targets', {}, ('exec',
r'''a = b = c = z'''),
r'''a = b = z''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Assign - 0,0..0,9
     .targets[2]
      0] Name 'a' Store - 0,0..0,1
      1] Name 'b' Store - 0,4..0,5
     .value Name 'z' Load - 0,8..0,9
''',
r'''c =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'c' Store - 0,0..0,1
'''),

(4, 'body[0]', 3, 3, 'targets', {'_verify': False}, ('exec',
r'''a = b = c = z'''),
r'''a = b = c = z''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Assign - 0,0..0,13
     .targets[3]
      0] Name 'a' Store - 0,0..0,1
      1] Name 'b' Store - 0,4..0,5
      2] Name 'c' Store - 0,8..0,9
     .value Name 'z' Load - 0,12..0,13
''',
r'''''',
r'''_Assign_targets - ROOT 0,0..0,0'''),

(5, 'body[0]', 0, 2, 'targets', {}, ('exec', r'''
a = \
b = \
c \
= \
z
'''), r'''
c \
= \
z
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Assign - 0,0..2,1
     .targets[1]
      0] Name 'c' Store - 0,0..0,1
     .value Name 'z' Load - 2,0..2,1
''', r'''
a = \
b = \

''', r'''
_Assign_targets - ROOT 0,0..2,0
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 1,0..1,1
'''),

(6, 'body[0]', 1, 2, 'targets', {}, ('exec', r'''
a = \
b = \
c \
= \
z
'''), r'''
a = \
c \
= \
z
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Assign - 0,0..3,1
     .targets[2]
      0] Name 'a' Store - 0,0..0,1
      1] Name 'c' Store - 1,0..1,1
     .value Name 'z' Load - 3,0..3,1
''', r'''

b = \

''', r'''
_Assign_targets - ROOT 0,0..2,0
  .targets[1]
   0] Name 'b' Store - 1,0..1,1
'''),

(7, 'body[0]', 1, 3, 'targets', {}, ('exec', r'''
a = \
b = \
c \
= \
z
'''), r'''
a = \
z
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Assign - 0,0..1,1
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Name 'z' Load - 1,0..1,1
''', r'''

b = \
c \
= \

''', r'''
_Assign_targets - ROOT 0,0..4,0
  .targets[2]
   0] Name 'b' Store - 1,0..1,1
   1] Name 'c' Store - 2,0..2,1
'''),

(8, 'body[0]', 2, 3, 'targets', {}, ('exec', r'''
a = \
b = \
c \
= \
z
'''), r'''
a = \
b = \
z
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Assign - 0,0..2,1
     .targets[2]
      0] Name 'a' Store - 0,0..0,1
      1] Name 'b' Store - 1,0..1,1
     .value Name 'z' Load - 2,0..2,1
''', r'''

c \
= \

''', r'''
_Assign_targets - ROOT 0,0..3,0
  .targets[1]
   0] Name 'c' Store - 1,0..1,1
'''),

(9, 'body[0]', 3, 3, 'targets', {}, ('exec', r'''
a = \
b = \
c \
= \
z
'''), r'''
a = \
b = \
c \
= \
z
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Assign - 0,0..4,1
     .targets[3]
      0] Name 'a' Store - 0,0..0,1
      1] Name 'b' Store - 1,0..1,1
      2] Name 'c' Store - 2,0..2,1
     .value Name 'z' Load - 4,0..4,1
''',
r'''''',
r'''_Assign_targets - ROOT 0,0..0,0'''),

(10, '', 0, 2, 'targets', {}, ('_Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
c \
= \

''', r'''
_Assign_targets - ROOT 0,0..2,0
  .targets[1]
   0] Name 'c' Store - 0,0..0,1
''', r'''
a = \
b = \

''', r'''
_Assign_targets - ROOT 0,0..2,0
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 1,0..1,1
'''),

(11, '', 1, 2, 'targets', {}, ('_Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
a = \
c \
= \

''', r'''
_Assign_targets - ROOT 0,0..3,0
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'c' Store - 1,0..1,1
''', r'''

b = \

''', r'''
_Assign_targets - ROOT 0,0..2,0
  .targets[1]
   0] Name 'b' Store - 1,0..1,1
'''),

(12, '', 1, 3, 'targets', {}, ('_Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
a = \

''', r'''
_Assign_targets - ROOT 0,0..1,0
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
''', r'''

b = \
c \
= \

''', r'''
_Assign_targets - ROOT 0,0..4,0
  .targets[2]
   0] Name 'b' Store - 1,0..1,1
   1] Name 'c' Store - 2,0..2,1
'''),

(13, '', 2, 3, 'targets', {}, ('_Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
a = \
b = \

''', r'''
_Assign_targets - ROOT 0,0..2,0
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 1,0..1,1
''', r'''

c \
= \

''', r'''
_Assign_targets - ROOT 0,0..3,0
  .targets[1]
   0] Name 'c' Store - 1,0..1,1
'''),

(14, '', 3, 3, 'targets', {}, ('_Assign_targets', r'''
a = \
b = \
c \
= \
z
'''), r'''
a = \
b = \
c \
= \
z
''', r'''
_Assign_targets - ROOT 0,0..4,1
  .targets[4]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 1,0..1,1
   2] Name 'c' Store - 2,0..2,1
   3] Name 'z' Store - 4,0..4,1
''',
r'''''',
r'''_Assign_targets - ROOT 0,0..0,0'''),

(15, '', 0, 3, 'targets', {}, (None,
r'''a = b = c = z'''),
r'''**ValueError('cannot cut all Assign.targets without norm_self=False')**''',
r'''a = b = c =''', r'''
_Assign_targets - ROOT 0,0..0,11
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
   2] Name 'c' Store - 0,8..0,9
'''),

(16, '', 0, 3, 'targets', {'norm_self': False, '_verify_self': False}, (None,
r'''a = b = c = z'''),
r''' z''', r'''
Assign - ROOT 0,0..0,2
  .value Name 'z' Load - 0,1..0,2
''',
r'''a = b = c =''', r'''
_Assign_targets - ROOT 0,0..0,11
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
   2] Name 'c' Store - 0,8..0,9
'''),
],

'With_items': [  # ................................................................................

(0, 'body[0]', 1, 2, 'items', {}, ('exec',
r'''with a, b as y, c: pass  # comment'''),
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
''',
r'''b as y''', r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 0,5..0,6
'''),

(1, 'body[0]', 1, 3, 'items', {}, ('exec',
r'''with a, b as y, c: pass  # comment'''),
r'''with a: pass  # comment''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] With - 0,0..0,12
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'a' Load - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
''',
r'''b as y, c''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'c' Load - 0,8..0,9
'''),

(2, 'body[0]', 0, 2, 'items', {}, ('exec',
r'''with a, b as y, c: pass  # comment'''),
r'''with c: pass  # comment''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] With - 0,0..0,12
     .items[1]
      0] withitem - 0,5..0,6
        .context_expr Name 'c' Load - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
''',
r'''a, b as y''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,9
     .context_expr Name 'b' Load - 0,3..0,4
     .optional_vars Name 'y' Store - 0,8..0,9
'''),

(3, 'body[0]', 1, 2, 'items', {}, ('exec', r'''
with a \
, \
b \
as \
y \
, \
c: pass  # comment
'''), r'''
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
''', r'''

b \
as \
y \
 \

''', r'''
_withitems - ROOT 0,0..5,0
  .items[1]
   0] withitem - 1,0..3,1
     .context_expr Name 'b' Load - 1,0..1,1
     .optional_vars Name 'y' Store - 3,0..3,1
'''),

(4, 'body[0]', 0, 2, 'items', {}, ('exec', r'''
with a \
, \
b \
as \
y \
, \
c: pass  # comment
'''), r'''
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
''', r'''
a \
, \
b \
as \
y \
 \

''', r'''
_withitems - ROOT 0,0..6,0
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 2,0..4,1
     .context_expr Name 'b' Load - 2,0..2,1
     .optional_vars Name 'y' Store - 4,0..4,1
'''),

(5, 'body[0]', 1, 3, 'items', {}, ('exec', r'''
with a \
, \
b \
as \
y \
, \
c: pass  # comment
'''), r'''
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
''', r'''

b \
as \
y \
, \
c
''', r'''
_withitems - ROOT 0,0..5,1
  .items[2]
   0] withitem - 1,0..3,1
     .context_expr Name 'b' Load - 1,0..1,1
     .optional_vars Name 'y' Store - 3,0..3,1
   1] withitem - 5,0..5,1
     .context_expr Name 'c' Load - 5,0..5,1
'''),

(6, 'body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
if 1:
  with a \
  , \
  b \
  as \
  y: pass  # comment
  pass
'''), r'''
if 1:
  with  \
  b \
  as \
  y: pass  # comment
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] With - 1,2..4,9
        .items[1]
         0] withitem - 2,2..4,3
           .context_expr Name 'b' Load - 2,2..2,3
           .optional_vars Name 'y' Store - 4,2..4,3
        .body[1]
         0] Pass - 4,5..4,9
      1] Pass - 5,2..5,6
''', r'''
a \

''', r'''
_withitems - ROOT 0,0..1,0
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

(7, 'body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
if 1:
  with a \
  , \
  b \
  as \
  y: pass  # comment
  pass
'''), r'''
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
''', r'''
b \
as \
y
''', r'''
_withitems - ROOT 0,0..2,1
  .items[1]
   0] withitem - 0,0..2,1
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 2,0..2,1
'''),

(8, '', 0, 3, 'items', {}, (None,
r'''with a, b, c: pass'''),
r'''**ValueError('cannot cut all With.items without norm_self=False')**''',
r'''a, b, c''', r'''
_withitems - ROOT 0,0..0,7
  .items[3]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,4
     .context_expr Name 'b' Load - 0,3..0,4
   2] withitem - 0,6..0,7
     .context_expr Name 'c' Load - 0,6..0,7
'''),

(9, '', 0, 3, 'items', {'norm_self': False, '_verify_self': False}, (None, r'''
with a \
, \
b \
as \
y \
, \
c: pass  # comment
'''),
r'''with : pass  # comment''', r'''
With - ROOT 0,0..0,11
  .body[1]
   0] Pass - 0,7..0,11
''', r'''
a \
, \
b \
as \
y \
, \
c
''', r'''
_withitems - ROOT 0,0..6,1
  .items[3]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 2,0..4,1
     .context_expr Name 'b' Load - 2,0..2,1
     .optional_vars Name 'y' Store - 4,0..4,1
   2] withitem - 6,0..6,1
     .context_expr Name 'c' Load - 6,0..6,1
'''),

(10, 'body[0]', 1, 2, 'items', {}, (None, r'''
if 1:
  with a, b:
    pass;
'''), r'''
if 1:
  with a:
    pass;
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] With - 1,2..2,9
     .items[1]
      0] withitem - 1,7..1,8
        .context_expr Name 'a' Load - 1,7..1,8
     .body[1]
      0] Pass - 2,4..2,8
''',
r'''b''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'b' Load - 0,0..0,1
'''),
],

'With_items_w_pars': [  # ................................................................................

(0, 'body[0]', 1, 2, 'items', {}, ('exec',
r'''with (a, b as y, c): pass  # comment'''),
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
''',
r'''b as y''', r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 0,5..0,6
'''),

(1, 'body[0]', 1, 3, 'items', {}, ('exec',
r'''with (a, b as y, c): pass  # comment'''),
r'''with (a): pass  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] With - 0,0..0,14
     .items[1]
      0] withitem - 0,5..0,8
        .context_expr Name 'a' Load - 0,6..0,7
     .body[1]
      0] Pass - 0,10..0,14
''',
r'''b as y, c''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'c' Load - 0,8..0,9
'''),

(2, 'body[0]', 0, 2, 'items', {}, ('exec',
r'''with (a, b as y, c): pass  # comment'''),
r'''with (c): pass  # comment''', r'''
Module - ROOT 0,0..0,25
  .body[1]
   0] With - 0,0..0,14
     .items[1]
      0] withitem - 0,5..0,8
        .context_expr Name 'c' Load - 0,6..0,7
     .body[1]
      0] Pass - 0,10..0,14
''',
r'''a, b as y''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,9
     .context_expr Name 'b' Load - 0,3..0,4
     .optional_vars Name 'y' Store - 0,8..0,9
'''),

(3, 'body[0]', 1, 2, 'items', {}, ('exec', r'''
with (a
,
b
as
y
,
c): pass  # comment
'''), r'''
with (a
,
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
''', r'''

b
as
y


''', r'''
_withitems - ROOT 0,0..5,0
  .items[1]
   0] withitem - 1,0..3,1
     .context_expr Name 'b' Load - 1,0..1,1
     .optional_vars Name 'y' Store - 3,0..3,1
'''),

(4, 'body[0]', 0, 2, 'items', {}, ('exec', r'''
with (a
,
b
as
y
,
c): pass  # comment
'''), r'''
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
''', r'''
a
,
b
as
y


''', r'''
_withitems - ROOT 0,0..6,0
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 2,0..4,1
     .context_expr Name 'b' Load - 2,0..2,1
     .optional_vars Name 'y' Store - 4,0..4,1
'''),

(5, 'body[0]', 1, 3, 'items', {}, ('exec', r'''
with (a
,
b
as
y
,
c): pass  # comment
'''), r'''
with (a

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
''', r'''

b
as
y
,
c
''', r'''
_withitems - ROOT 0,0..5,1
  .items[2]
   0] withitem - 1,0..3,1
     .context_expr Name 'b' Load - 1,0..1,1
     .optional_vars Name 'y' Store - 3,0..3,1
   1] withitem - 5,0..5,1
     .context_expr Name 'c' Load - 5,0..5,1
'''),

(6, 'body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
if 1:
  with (a
  ,
  b
  as
  y): pass  # comment
  pass
'''), r'''
if 1:
  with (
  b
  as
  y): pass  # comment
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] With - 1,2..4,10
        .items[1]
         0] withitem - 2,2..4,3
           .context_expr Name 'b' Load - 2,2..2,3
           .optional_vars Name 'y' Store - 4,2..4,3
        .body[1]
         0] Pass - 4,6..4,10
      1] Pass - 5,2..5,6
''', r'''
a

''', r'''
_withitems - ROOT 0,0..1,0
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

(7, 'body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
if 1:
  with (a
  ,
  b
  as
  y): pass  # comment
  pass
'''),
'if 1:\n  with (a\n  \n  ): pass  # comment\n  pass', r'''
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
''', r'''
b
as
y
''', r'''
_withitems - ROOT 0,0..2,1
  .items[1]
   0] withitem - 0,0..2,1
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 2,0..2,1
'''),

(8, '', 0, 3, 'items', {}, (None,
r'''with (a, b, c): pass'''),
r'''**ValueError('cannot cut all With.items without norm_self=False')**''',
r'''a, b, c''', r'''
_withitems - ROOT 0,0..0,7
  .items[3]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,4
     .context_expr Name 'b' Load - 0,3..0,4
   2] withitem - 0,6..0,7
     .context_expr Name 'c' Load - 0,6..0,7
'''),

(9, '', 0, 3, 'items', {'norm_self': False, '_verify_self': False}, (None, r'''
with (a
,
b
as
y
,
c): pass  # comment
'''),
r'''with (): pass  # comment''', r'''
With - ROOT 0,0..0,13
  .body[1]
   0] Pass - 0,9..0,13
''', r'''
a
,
b
as
y
,
c
''', r'''
_withitems - ROOT 0,0..6,1
  .items[3]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 2,0..4,1
     .context_expr Name 'b' Load - 2,0..2,1
     .optional_vars Name 'y' Store - 4,0..4,1
   2] withitem - 6,0..6,1
     .context_expr Name 'c' Load - 6,0..6,1
'''),

(10, 'body[0]', 1, 2, 'items', {}, (None, r'''
if 1:
  with (a, b):
    pass;
'''), r'''
if 1:
  with (a):
    pass;
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] With - 1,2..2,9
     .items[1]
      0] withitem - 1,7..1,10
        .context_expr Name 'a' Load - 1,8..1,9
     .body[1]
      0] Pass - 2,4..2,8
''',
r'''b''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'b' Load - 0,0..0,1
'''),
],

'AsyncWith_items': [  # ................................................................................

(0, 'body[0]', 1, 2, 'items', {}, ('exec',
r'''async with a, b as y, c: pass  # comment'''),
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
''',
r'''b as y''', r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 0,5..0,6
'''),

(1, 'body[0]', 1, 3, 'items', {}, ('exec',
r'''async with a, b as y, c: pass  # comment'''),
r'''async with a: pass  # comment''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncWith - 0,0..0,18
     .items[1]
      0] withitem - 0,11..0,12
        .context_expr Name 'a' Load - 0,11..0,12
     .body[1]
      0] Pass - 0,14..0,18
''',
r'''b as y, c''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'c' Load - 0,8..0,9
'''),

(2, 'body[0]', 0, 2, 'items', {}, ('exec',
r'''async with a, b as y, c: pass  # comment'''),
r'''async with c: pass  # comment''', r'''
Module - ROOT 0,0..0,29
  .body[1]
   0] AsyncWith - 0,0..0,18
     .items[1]
      0] withitem - 0,11..0,12
        .context_expr Name 'c' Load - 0,11..0,12
     .body[1]
      0] Pass - 0,14..0,18
''',
r'''a, b as y''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,9
     .context_expr Name 'b' Load - 0,3..0,4
     .optional_vars Name 'y' Store - 0,8..0,9
'''),

(3, 'body[0]', 1, 2, 'items', {}, ('exec', r'''
async with a \
, \
b \
as \
y \
, \
c: pass  # comment
'''), r'''
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
''', r'''

b \
as \
y \
 \

''', r'''
_withitems - ROOT 0,0..5,0
  .items[1]
   0] withitem - 1,0..3,1
     .context_expr Name 'b' Load - 1,0..1,1
     .optional_vars Name 'y' Store - 3,0..3,1
'''),

(4, 'body[0]', 0, 2, 'items', {}, ('exec', r'''
async with a \
, \
b \
as \
y \
, \
c: pass  # comment
'''), r'''
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
''', r'''
a \
, \
b \
as \
y \
 \

''', r'''
_withitems - ROOT 0,0..6,0
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 2,0..4,1
     .context_expr Name 'b' Load - 2,0..2,1
     .optional_vars Name 'y' Store - 4,0..4,1
'''),

(5, 'body[0]', 1, 3, 'items', {}, ('exec', r'''
async with a \
, \
b \
as \
y \
, \
c: pass  # comment
'''), r'''
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
''', r'''

b \
as \
y \
, \
c
''', r'''
_withitems - ROOT 0,0..5,1
  .items[2]
   0] withitem - 1,0..3,1
     .context_expr Name 'b' Load - 1,0..1,1
     .optional_vars Name 'y' Store - 3,0..3,1
   1] withitem - 5,0..5,1
     .context_expr Name 'c' Load - 5,0..5,1
'''),

(6, 'body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
if 1:
  async with a \
  , \
  b \
  as \
  y: pass  # comment
  pass
'''), r'''
if 1:
  async with  \
  b \
  as \
  y: pass  # comment
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] AsyncWith - 1,2..4,9
        .items[1]
         0] withitem - 2,2..4,3
           .context_expr Name 'b' Load - 2,2..2,3
           .optional_vars Name 'y' Store - 4,2..4,3
        .body[1]
         0] Pass - 4,5..4,9
      1] Pass - 5,2..5,6
''', r'''
a \

''', r'''
_withitems - ROOT 0,0..1,0
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

(7, 'body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
if 1:
  async with a \
  , \
  b \
  as \
  y: pass  # comment
  pass
'''), r'''
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
''', r'''
b \
as \
y
''', r'''
_withitems - ROOT 0,0..2,1
  .items[1]
   0] withitem - 0,0..2,1
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 2,0..2,1
'''),

(8, '', 0, 3, 'items', {}, (None,
r'''async with a, b, c: pass'''),
r'''**ValueError('cannot cut all AsyncWith.items without norm_self=False')**''',
r'''a, b, c''', r'''
_withitems - ROOT 0,0..0,7
  .items[3]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,4
     .context_expr Name 'b' Load - 0,3..0,4
   2] withitem - 0,6..0,7
     .context_expr Name 'c' Load - 0,6..0,7
'''),

(9, '', 0, 3, 'items', {'norm_self': False, '_verify_self': False}, (None, r'''
async with a \
, \
b \
as \
y \
, \
c: pass  # comment
'''),
r'''async with : pass  # comment''', r'''
AsyncWith - ROOT 0,0..0,17
  .body[1]
   0] Pass - 0,13..0,17
''', r'''
a \
, \
b \
as \
y \
, \
c
''', r'''
_withitems - ROOT 0,0..6,1
  .items[3]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 2,0..4,1
     .context_expr Name 'b' Load - 2,0..2,1
     .optional_vars Name 'y' Store - 4,0..4,1
   2] withitem - 6,0..6,1
     .context_expr Name 'c' Load - 6,0..6,1
'''),

(10, 'body[0]', 1, 2, 'items', {}, (None, r'''
if 1:
  async with a, b:
    pass;
'''), r'''
if 1:
  async with a:
    pass;
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] AsyncWith - 1,2..2,9
     .items[1]
      0] withitem - 1,13..1,14
        .context_expr Name 'a' Load - 1,13..1,14
     .body[1]
      0] Pass - 2,4..2,8
''',
r'''b''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'b' Load - 0,0..0,1
'''),
],

'AsyncWith_items_w_pars': [  # ................................................................................

(0, 'body[0]', 1, 2, 'items', {}, ('exec',
r'''async with (a, b as y, c): pass  # comment'''),
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
''',
r'''b as y''', r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 0,5..0,6
'''),

(1, 'body[0]', 1, 3, 'items', {}, ('exec',
r'''async with (a, b as y, c): pass  # comment'''),
r'''async with (a): pass  # comment''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] AsyncWith - 0,0..0,20
     .items[1]
      0] withitem - 0,11..0,14
        .context_expr Name 'a' Load - 0,12..0,13
     .body[1]
      0] Pass - 0,16..0,20
''',
r'''b as y, c''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'c' Load - 0,8..0,9
'''),

(2, 'body[0]', 0, 2, 'items', {}, ('exec',
r'''async with (a, b as y, c): pass  # comment'''),
r'''async with (c): pass  # comment''', r'''
Module - ROOT 0,0..0,31
  .body[1]
   0] AsyncWith - 0,0..0,20
     .items[1]
      0] withitem - 0,11..0,14
        .context_expr Name 'c' Load - 0,12..0,13
     .body[1]
      0] Pass - 0,16..0,20
''',
r'''a, b as y''', r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,9
     .context_expr Name 'b' Load - 0,3..0,4
     .optional_vars Name 'y' Store - 0,8..0,9
'''),

(3, 'body[0]', 1, 2, 'items', {}, ('exec', r'''
async with (a
,
b
as
y
,
c): pass  # comment
'''), r'''
async with (a
,
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
''', r'''

b
as
y


''', r'''
_withitems - ROOT 0,0..5,0
  .items[1]
   0] withitem - 1,0..3,1
     .context_expr Name 'b' Load - 1,0..1,1
     .optional_vars Name 'y' Store - 3,0..3,1
'''),

(4, 'body[0]', 0, 2, 'items', {}, ('exec', r'''
async with (a
,
b
as
y
,
c): pass  # comment
'''), r'''
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
''', r'''
a
,
b
as
y


''', r'''
_withitems - ROOT 0,0..6,0
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 2,0..4,1
     .context_expr Name 'b' Load - 2,0..2,1
     .optional_vars Name 'y' Store - 4,0..4,1
'''),

(5, 'body[0]', 1, 3, 'items', {}, ('exec', r'''
async with (a
,
b
as
y
,
c): pass  # comment
'''), r'''
async with (a

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
''', r'''

b
as
y
,
c
''', r'''
_withitems - ROOT 0,0..5,1
  .items[2]
   0] withitem - 1,0..3,1
     .context_expr Name 'b' Load - 1,0..1,1
     .optional_vars Name 'y' Store - 3,0..3,1
   1] withitem - 5,0..5,1
     .context_expr Name 'c' Load - 5,0..5,1
'''),

(6, 'body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
if 1:
  async with (a
  ,
  b
  as
  y): pass  # comment
  pass
'''), r'''
if 1:
  async with (
  b
  as
  y): pass  # comment
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] AsyncWith - 1,2..4,10
        .items[1]
         0] withitem - 2,2..4,3
           .context_expr Name 'b' Load - 2,2..2,3
           .optional_vars Name 'y' Store - 4,2..4,3
        .body[1]
         0] Pass - 4,6..4,10
      1] Pass - 5,2..5,6
''', r'''
a

''', r'''
_withitems - ROOT 0,0..1,0
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

(7, 'body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
if 1:
  async with (a
  ,
  b
  as
  y): pass  # comment
  pass
'''),
'if 1:\n  async with (a\n  \n  ): pass  # comment\n  pass', r'''
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
''', r'''
b
as
y
''', r'''
_withitems - ROOT 0,0..2,1
  .items[1]
   0] withitem - 0,0..2,1
     .context_expr Name 'b' Load - 0,0..0,1
     .optional_vars Name 'y' Store - 2,0..2,1
'''),

(8, '', 0, 3, 'items', {}, (None,
r'''async with (a, b, c): pass'''),
r'''**ValueError('cannot cut all AsyncWith.items without norm_self=False')**''',
r'''a, b, c''', r'''
_withitems - ROOT 0,0..0,7
  .items[3]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,4
     .context_expr Name 'b' Load - 0,3..0,4
   2] withitem - 0,6..0,7
     .context_expr Name 'c' Load - 0,6..0,7
'''),

(9, '', 0, 3, 'items', {'norm_self': False, '_verify_self': False}, (None, r'''
async with (a
,
b
as
y
,
c): pass  # comment
'''),
r'''async with (): pass  # comment''', r'''
AsyncWith - ROOT 0,0..0,19
  .body[1]
   0] Pass - 0,15..0,19
''', r'''
a
,
b
as
y
,
c
''', r'''
_withitems - ROOT 0,0..6,1
  .items[3]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 2,0..4,1
     .context_expr Name 'b' Load - 2,0..2,1
     .optional_vars Name 'y' Store - 4,0..4,1
   2] withitem - 6,0..6,1
     .context_expr Name 'c' Load - 6,0..6,1
'''),

(10, 'body[0]', 1, 2, 'items', {}, (None, r'''
if 1:
  async with (a, b):
    pass;
'''), r'''
if 1:
  async with (a):
    pass;
''', r'''
If - ROOT 0,0..2,9
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] AsyncWith - 1,2..2,9
     .items[1]
      0] withitem - 1,13..1,16
        .context_expr Name 'a' Load - 1,14..1,15
     .body[1]
      0] Pass - 2,4..2,8
''',
r'''b''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'b' Load - 0,0..0,1
'''),
],

'Import_names': [  # ................................................................................

(0, 'body[0]', 1, 2, None, {}, ('exec',
r'''import a, b as y, c  # comment'''),
r'''import a, c  # comment''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Import - 0,0..0,11
     .names[2]
      0] alias - 0,7..0,8
        .name 'a'
      1] alias - 0,10..0,11
        .name 'c'
''',
r'''b as y''', r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'b'
     .asname 'y'
'''),

(1, 'body[0]', 1, 3, None, {}, ('exec',
r'''import a, b as y, c  # comment'''),
r'''import a  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Import - 0,0..0,8
     .names[1]
      0] alias - 0,7..0,8
        .name 'a'
''',
r'''b as y, c''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'b'
     .asname 'y'
   1] alias - 0,8..0,9
     .name 'c'
'''),

(2, 'body[0]', 0, 2, None, {}, ('exec',
r'''import a, b as y, c  # comment'''),
r'''import c  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Import - 0,0..0,8
     .names[1]
      0] alias - 0,7..0,8
        .name 'c'
''',
r'''a, b as y''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,9
     .name 'b'
     .asname 'y'
'''),

(3, 'body[0]', 1, 2, None, {}, ('exec', r'''
import a \
, \
b \
as \
y \
, \
c  # comment
'''), r'''
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
''', r'''

b \
as \
y \
 \

''', r'''
_aliases - ROOT 0,0..5,0
  .names[1]
   0] alias - 1,0..3,1
     .name 'b'
     .asname 'y'
'''),

(4, 'body[0]', 0, 2, None, {}, ('exec', r'''
import a \
, \
b \
as \
y \
, \
c  # comment
'''), r'''
import \
c  # comment
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Import - 0,0..1,1
     .names[1]
      0] alias - 1,0..1,1
        .name 'c'
''', r'''
a \
, \
b \
as \
y \
 \

''', r'''
_aliases - ROOT 0,0..6,0
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 2,0..4,1
     .name 'b'
     .asname 'y'
'''),

(5, 'body[0]', 1, 3, None, {}, ('exec', r'''
import a \
, \
b \
as \
y \
, \
c  # comment
'''), r'''
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
''', r'''

b \
as \
y \
, \
c
''', r'''
_aliases - ROOT 0,0..5,1
  .names[2]
   0] alias - 1,0..3,1
     .name 'b'
     .asname 'y'
   1] alias - 5,0..5,1
     .name 'c'
'''),

(6, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  import a \
  , \
  b \
  as \
  y # comment
  pass
'''), r'''
if 1:
  import  \
  b \
  as \
  y # comment
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Import - 1,2..4,3
        .names[1]
         0] alias - 2,2..4,3
           .name 'b'
           .asname 'y'
      1] Pass - 5,2..5,6
''', r'''
a \

''', r'''
_aliases - ROOT 0,0..1,0
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

(7, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  import a \
  , \
  b \
  as \
  y # comment
  pass
'''), r'''
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
''', r'''
b \
as \
y
''', r'''
_aliases - ROOT 0,0..2,1
  .names[1]
   0] alias - 0,0..2,1
     .name 'b'
     .asname 'y'
'''),

(8, '', 0, 3, None, {}, (None,
r'''import a, b, c'''),
r'''**ValueError('cannot cut all Import.names without norm_self=False')**''',
r'''a, b, c''', r'''
_aliases - ROOT 0,0..0,7
  .names[3]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
   2] alias - 0,6..0,7
     .name 'c'
'''),

(9, '', 0, 3, None, {'norm_self': False, '_verify_self': False}, (None, r'''
import a \
, \
b \
as \
y \
, \
c  # comment
'''),
r'''import   # comment''',
r'''Import - ROOT 0,0..0,7''', r'''
a \
, \
b \
as \
y \
, \
c
''', r'''
_aliases - ROOT 0,0..6,1
  .names[3]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 2,0..4,1
     .name 'b'
     .asname 'y'
   2] alias - 6,0..6,1
     .name 'c'
'''),

(10, 'body[0]', 1, 2, None, {}, (None, r'''
if 1:
  import a, b;
'''), r'''
if 1:
  import a;
''', r'''
If - ROOT 0,0..1,11
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Import - 1,2..1,10
     .names[1]
      0] alias - 1,9..1,10
        .name 'a'
''',
r'''b''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'b'
'''),
],

'ImportFrom_names': [  # ................................................................................

(0, 'body[0]', 1, 2, None, {}, ('exec',
r'''from mod import a, b as y, c  # comment'''),
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
''',
r'''b as y''', r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'b'
     .asname 'y'
'''),

(1, 'body[0]', 1, 3, None, {}, ('exec',
r'''from mod import a, b as y, c  # comment'''),
r'''from mod import a  # comment''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name 'a'
     .level 0
''',
r'''b as y, c''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'b'
     .asname 'y'
   1] alias - 0,8..0,9
     .name 'c'
'''),

(2, 'body[0]', 0, 2, None, {}, ('exec',
r'''from mod import a, b as y, c  # comment'''),
r'''from mod import c  # comment''', r'''
Module - ROOT 0,0..0,28
  .body[1]
   0] ImportFrom - 0,0..0,17
     .module 'mod'
     .names[1]
      0] alias - 0,16..0,17
        .name 'c'
     .level 0
''',
r'''a, b as y''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,9
     .name 'b'
     .asname 'y'
'''),

(3, 'body[0]', 1, 2, None, {}, ('exec', r'''
from mod import a \
, \
b \
as \
y \
, \
c  # comment
'''), r'''
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
''', r'''

b \
as \
y \
 \

''', r'''
_aliases - ROOT 0,0..5,0
  .names[1]
   0] alias - 1,0..3,1
     .name 'b'
     .asname 'y'
'''),

(4, 'body[0]', 0, 2, None, {}, ('exec', r'''
from mod import a \
, \
b \
as \
y \
, \
c  # comment
'''), r'''
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
''', r'''
a \
, \
b \
as \
y \
 \

''', r'''
_aliases - ROOT 0,0..6,0
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 2,0..4,1
     .name 'b'
     .asname 'y'
'''),

(5, 'body[0]', 1, 3, None, {}, ('exec', r'''
from mod import a \
, \
b \
as \
y \
, \
c  # comment
'''), r'''
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
''', r'''

b \
as \
y \
, \
c
''', r'''
_aliases - ROOT 0,0..5,1
  .names[2]
   0] alias - 1,0..3,1
     .name 'b'
     .asname 'y'
   1] alias - 5,0..5,1
     .name 'c'
'''),

(6, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  from mod import a \
  , \
  b \
  as \
  y # comment
  pass
'''), r'''
if 1:
  from mod import  \
  b \
  as \
  y # comment
  pass
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] If - 0,0..5,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] ImportFrom - 1,2..4,3
        .module 'mod'
        .names[1]
         0] alias - 2,2..4,3
           .name 'b'
           .asname 'y'
        .level 0
      1] Pass - 5,2..5,6
''', r'''
a \

''', r'''
_aliases - ROOT 0,0..1,0
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

(7, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  from mod import a \
  , \
  b \
  as \
  y # comment
  pass
'''), r'''
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
''', r'''
b \
as \
y
''', r'''
_aliases - ROOT 0,0..2,1
  .names[1]
   0] alias - 0,0..2,1
     .name 'b'
     .asname 'y'
'''),

(8, '', 0, 3, None, {}, (None,
r'''from mod import a, b, c'''),
r'''**ValueError('cannot cut all ImportFrom.names without norm_self=False')**''',
r'''a, b, c''', r'''
_aliases - ROOT 0,0..0,7
  .names[3]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
   2] alias - 0,6..0,7
     .name 'c'
'''),

(9, '', 0, 3, None, {'norm_self': False, '_verify_self': False}, (None, r'''
from mod import a \
, \
b \
as \
y \
, \
c  # comment
'''),
r'''from mod import   # comment''', r'''
ImportFrom - ROOT 0,0..0,16
  .module 'mod'
  .level 0
''', r'''
a \
, \
b \
as \
y \
, \
c
''', r'''
_aliases - ROOT 0,0..6,1
  .names[3]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 2,0..4,1
     .name 'b'
     .asname 'y'
   2] alias - 6,0..6,1
     .name 'c'
'''),

(10, 'body[0]', 1, 2, None, {}, (None, r'''
if 1:
  from mod import a, b;
'''), r'''
if 1:
  from mod import a;
''', r'''
If - ROOT 0,0..1,20
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ImportFrom - 1,2..1,19
     .module 'mod'
     .names[1]
      0] alias - 1,18..1,19
        .name 'a'
     .level 0
''',
r'''b''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'b'
'''),
],

'ImportFrom_names_w_pars': [  # ................................................................................

(0, 'body[0]', 1, 2, None, {}, ('exec',
r'''from mod import (a, b as y, c)  # comment'''),
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
''',
r'''b as y''', r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'b'
     .asname 'y'
'''),

(1, 'body[0]', 1, 3, None, {}, ('exec',
r'''from mod import (a, b as y, c)  # comment'''),
r'''from mod import (a)  # comment''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] ImportFrom - 0,0..0,19
     .module 'mod'
     .names[1]
      0] alias - 0,17..0,18
        .name 'a'
     .level 0
''',
r'''b as y, c''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,6
     .name 'b'
     .asname 'y'
   1] alias - 0,8..0,9
     .name 'c'
'''),

(2, 'body[0]', 0, 2, None, {}, ('exec',
r'''from mod import (a, b as y, c)  # comment'''),
r'''from mod import (c)  # comment''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] ImportFrom - 0,0..0,19
     .module 'mod'
     .names[1]
      0] alias - 0,17..0,18
        .name 'c'
     .level 0
''',
r'''a, b as y''', r'''
_aliases - ROOT 0,0..0,9
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,9
     .name 'b'
     .asname 'y'
'''),

(3, 'body[0]', 1, 2, None, {}, ('exec', r'''
from mod import (a
,
b
as
y
,
c  # blah
)  # comment
'''), r'''
from mod import (a
,
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
''', r'''

b
as
y


''', r'''
_aliases - ROOT 0,0..5,0
  .names[1]
   0] alias - 1,0..3,1
     .name 'b'
     .asname 'y'
'''),

(4, 'body[0]', 0, 2, None, {}, ('exec', r'''
from mod import (a
,
b
as
y
,  # blah
c)  # comment
'''), r'''
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
''', r'''
a
,
b
as
y
  # blah

''', r'''
_aliases - ROOT 0,0..6,0
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 2,0..4,1
     .name 'b'
     .asname 'y'
'''),

(5, 'body[0]', 1, 3, None, {}, ('exec', r'''
from mod import (a
,
b
as
y
,
c  # blah
)  # comment
'''), r'''
from mod import (a

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
''', r'''

b
as
y
,
c  # blah

''', r'''
_aliases - ROOT 0,0..6,0
  .names[2]
   0] alias - 1,0..3,1
     .name 'b'
     .asname 'y'
   1] alias - 5,0..5,1
     .name 'c'
'''),

(6, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  from mod import (a
  ,
  b
  as
  y  # blah
  )  # comment
  pass
'''), r'''
if 1:
  from mod import (
  b
  as
  y  # blah
  )  # comment
  pass
''', r'''
Module - ROOT 0,0..6,6
  .body[1]
   0] If - 0,0..6,6
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] ImportFrom - 1,2..5,3
        .module 'mod'
        .names[1]
         0] alias - 2,2..4,3
           .name 'b'
           .asname 'y'
        .level 0
      1] Pass - 6,2..6,6
''', r'''
a

''', r'''
_aliases - ROOT 0,0..1,0
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

(7, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  from mod import (a
  ,
  b
  as
  y  # blah
  )  # comment
  pass
'''),
'if 1:\n  from mod import (a\n  \n  )  # comment\n  pass', r'''
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
''', r'''

b
as
y  # blah

''', r'''
_aliases - ROOT 0,0..4,0
  .names[1]
   0] alias - 1,0..3,1
     .name 'b'
     .asname 'y'
'''),

(8, '', 0, 3, None, {}, (None,
r'''from mod import a, b, c'''),
r'''**ValueError('cannot cut all ImportFrom.names without norm_self=False')**''',
r'''a, b, c''', r'''
_aliases - ROOT 0,0..0,7
  .names[3]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
   2] alias - 0,6..0,7
     .name 'c'
'''),

(9, '', 0, 3, None, {'norm_self': False, '_verify_self': False}, (None, r'''
from mod import (a
,
b
as
y
,
c  # blah
)  # comment
'''), r'''
from mod import (
)  # comment
''', r'''
ImportFrom - ROOT 0,0..1,1
  .module 'mod'
  .level 0
''', r'''
a
,
b
as
y
,
c  # blah

''', r'''
_aliases - ROOT 0,0..7,0
  .names[3]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 2,0..4,1
     .name 'b'
     .asname 'y'
   2] alias - 6,0..6,1
     .name 'c'
'''),

(10, 'body[0]', 1, 2, None, {}, (None, r'''
if 1:
  from mod import (a, b);
'''), r'''
if 1:
  from mod import (a);
''', r'''
If - ROOT 0,0..1,22
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ImportFrom - 1,2..1,21
     .module 'mod'
     .names[1]
      0] alias - 1,19..1,20
        .name 'a'
     .level 0
''',
r'''b''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'b'
'''),
],

'Global_names': [  # ................................................................................

(0, 'body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''),
r'''global a, c  # comment''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] Global - 0,0..0,11
     .names[2]
      0] 'a'
      1] 'c'
''',
r'''b,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'b' Load - 0,0..0,1
  .ctx Load
'''),

(1, 'body[0]', 1, 3, None, {}, ('exec',
r'''global a, b, c  # comment'''),
r'''global a  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'a'
''',
r'''b, c''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 0,3..0,4
  .ctx Load
'''),

(2, 'body[0]', 0, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''),
r'''global c  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'c'
''',
r'''a, b''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
  .ctx Load
'''),

(3, 'body[0]', 1, 2, None, {}, ('exec', r'''
global a \
, \
b \
, \
c  # comment
'''), r'''
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
''', r'''
(
b \
, \
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
'''),

(4, 'body[0]', 0, 2, None, {}, ('exec', r'''
global a \
, \
b \
, \
c  # comment
'''), r'''
global \
c  # comment
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Global - 0,0..1,1
     .names[1]
      0] 'c'
''', r'''
a \
, \
b \
,
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(5, 'body[0]', 1, 3, None, {}, ('exec', r'''
global a \
, \
b \
, \
c  # comment
'''), r'''
global a \
 \
  # comment
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] Global - 0,0..0,8
     .names[1]
      0] 'a'
''', r'''
(
b \
, \
c)
''', r'''
Tuple - ROOT 0,0..3,2
  .elts[2]
   0] Name 'b' Load - 1,0..1,1
   1] Name 'c' Load - 3,0..3,1
  .ctx Load
'''),

(6, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  global a \
  , \
  b  # comment
  pass
'''), r'''
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
''', r'''
a \
,
''', r'''
Tuple - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

(7, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  global a \
  , \
  b  # comment
  pass
'''), r'''
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
''', r'''
(
b,)
''', r'''
Tuple - ROOT 0,0..1,3
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
'''),

(8, 'body[0]', None, None, None, {}, ('exec',
r'''global a, b, c  # comment'''),
r'''**ValueError('cannot cut all Global.names without norm_self=False')**''',
r'''a, b, c''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'c' Load - 0,6..0,7
  .ctx Load
'''),

(9, 'body[0]', None, None, None, {'norm_self': False, '_verify_self': False}, ('exec',
r'''global a, b, c  # comment'''),
r'''global   # comment''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] Global - 0,0..0,7
''',
r'''a, b, c''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'c' Load - 0,6..0,7
  .ctx Load
'''),

(10, 'body[0]', 1, 2, None, {}, (None, r'''
if 1:
  global a, b;
'''), r'''
if 1:
  global a;
''', r'''
If - ROOT 0,0..1,11
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Global - 1,2..1,10
     .names[1]
      0] 'a'
''',
r'''b,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'b' Load - 0,0..0,1
  .ctx Load
'''),
],

'Nonlocal_names': [  # ................................................................................

(0, 'body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''),
r'''nonlocal a, c  # comment''', r'''
Module - ROOT 0,0..0,24
  .body[1]
   0] Nonlocal - 0,0..0,13
     .names[2]
      0] 'a'
      1] 'c'
''',
r'''b,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'b' Load - 0,0..0,1
  .ctx Load
'''),

(1, 'body[0]', 1, 3, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''),
r'''nonlocal a  # comment''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'a'
''',
r'''b, c''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 0,3..0,4
  .ctx Load
'''),

(2, 'body[0]', 0, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''),
r'''nonlocal c  # comment''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'c'
''',
r'''a, b''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
  .ctx Load
'''),

(3, 'body[0]', 1, 2, None, {}, ('exec', r'''
nonlocal a \
, \
b \
, \
c  # comment
'''), r'''
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
''', r'''
(
b \
, \
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
'''),

(4, 'body[0]', 0, 2, None, {}, ('exec', r'''
nonlocal a \
, \
b \
, \
c  # comment
'''), r'''
nonlocal \
c  # comment
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Nonlocal - 0,0..1,1
     .names[1]
      0] 'c'
''', r'''
a \
, \
b \
,
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(5, 'body[0]', 1, 3, None, {}, ('exec', r'''
nonlocal a \
, \
b \
, \
c  # comment
'''), r'''
nonlocal a \
 \
  # comment
''', r'''
Module - ROOT 0,0..2,11
  .body[1]
   0] Nonlocal - 0,0..0,10
     .names[1]
      0] 'a'
''', r'''
(
b \
, \
c)
''', r'''
Tuple - ROOT 0,0..3,2
  .elts[2]
   0] Name 'b' Load - 1,0..1,1
   1] Name 'c' Load - 3,0..3,1
  .ctx Load
'''),

(6, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
  nonlocal a \
  , \
  b  # comment
  pass
'''), r'''
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
''', r'''
a \
,
''', r'''
Tuple - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

(7, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  nonlocal a \
  , \
  b  # comment
  pass
'''), r'''
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
''', r'''
(
b,)
''', r'''
Tuple - ROOT 0,0..1,3
  .elts[1]
   0] Name 'b' Load - 1,0..1,1
  .ctx Load
'''),

(8, 'body[0]', None, None, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''),
r'''**ValueError('cannot cut all Nonlocal.names without norm_self=False')**''',
r'''a, b, c''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'c' Load - 0,6..0,7
  .ctx Load
'''),

(9, 'body[0]', None, None, None, {'norm_self': False, '_verify_self': False}, ('exec',
r'''nonlocal a, b, c  # comment'''),
r'''nonlocal   # comment''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] Nonlocal - 0,0..0,9
''',
r'''a, b, c''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'c' Load - 0,6..0,7
  .ctx Load
'''),

(10, 'body[0]', 1, 2, None, {}, (None, r'''
if 1:
  nonlocal a, b;
'''), r'''
if 1:
  nonlocal a;
''', r'''
If - ROOT 0,0..1,13
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Nonlocal - 1,2..1,12
     .names[1]
      0] 'a'
''',
r'''b,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'b' Load - 0,0..0,1
  .ctx Load
'''),
],

'Call_args': [  # ................................................................................

(0, '', 0, 0, None, {}, (None,
r'''call(a, *b)'''),
r'''call(a, *b)''', r'''
Call - ROOT 0,0..0,11
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,8..0,10
     .value Name 'b' Load - 0,9..0,10
     .ctx Load
''',
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
'''),

(1, '', None, None, None, {}, (None,
r'''call(a, *b)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(2, '', 0, 1, None, {}, (None,
r'''call(a, *b)'''),
r'''call(*b)''', r'''
Call - ROOT 0,0..0,8
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,7
     .value Name 'b' Load - 0,6..0,7
     .ctx Load
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(3, '', 1, 2, None, {}, (None,
r'''call(a, *b)'''),
r'''call(a)''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(4, '', None, None, None, {}, (None,
r'''call(a, *b, c=d)'''),
r'''call(c=d)''', r'''
Call - ROOT 0,0..0,9
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,8
     .arg 'c'
     .value Name 'd' Load - 0,7..0,8
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(5, '', 0, 1, None, {}, (None,
r'''call(a, *b, c=d)'''),
r'''call(*b, c=d)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,7
     .value Name 'b' Load - 0,6..0,7
     .ctx Load
  .keywords[1]
   0] keyword - 0,9..0,12
     .arg 'c'
     .value Name 'd' Load - 0,11..0,12
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(6, '', 1, 2, None, {}, (None,
r'''call(a, *b, c=d)'''),
r'''call(a, c=d)''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'c'
     .value Name 'd' Load - 0,10..0,11
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(7, '', None, None, None, {}, (None,
r'''call(a, *b, **c)'''),
r'''call(**c)''', r'''
Call - ROOT 0,0..0,9
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,8
     .value Name 'c' Load - 0,7..0,8
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(8, '', 0, 1, None, {}, (None,
r'''call(a, *b, **c)'''),
r'''call(*b, **c)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,7
     .value Name 'b' Load - 0,6..0,7
     .ctx Load
  .keywords[1]
   0] keyword - 0,9..0,12
     .value Name 'c' Load - 0,11..0,12
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(9, '', 1, 2, None, {}, (None,
r'''call(a, *b, **c)'''),
r'''call(a, **c)''', r'''
Call - ROOT 0,0..0,12
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
  .keywords[1]
   0] keyword - 0,8..0,11
     .value Name 'c' Load - 0,10..0,11
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(10, '', 1, 2, None, {}, (None, r'''
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
'''), r'''
call( \
a \
, \
c \
, \
** \
d \
)
''', r'''
Call - ROOT 0,0..7,1
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'c' Load - 3,0..3,1
  .keywords[1]
   0] keyword - 5,0..6,1
     .value Name 'd' Load - 6,0..6,1
''', r'''
(
* \
b \
, \
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[1]
   0] Starred - 1,0..2,1
     .value Name 'b' Load - 2,0..2,1
     .ctx Load
  .ctx Load
'''),

(11, '', 0, 3, None, {}, (None, r'''
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
'''), r'''
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
''', r'''
(
a \
, \
* \
b \
, \
c \
 \
)
''', r'''
Tuple - ROOT 0,0..8,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'c' Load - 6,0..6,1
  .ctx Load
'''),

(12, '', 0, 3, None, {}, (None, r'''
call( \
a, \
* \
b, \
c, \
** \
d \
)
'''), r'''
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
''', r'''
(
a, \
* \
b, \
c \
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

(13, '', 1, 2, None, {}, (None, r'''
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
'''), r'''
call(
a
,
c
,
**
d
)
''', r'''
Call - ROOT 0,0..7,1
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'c' Load - 3,0..3,1
  .keywords[1]
   0] keyword - 5,0..6,1
     .value Name 'd' Load - 6,0..6,1
''', r'''
(
*
b
,
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[1]
   0] Starred - 1,0..2,1
     .value Name 'b' Load - 2,0..2,1
     .ctx Load
  .ctx Load
'''),

(14, '', 0, 3, None, {}, (None, r'''
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
'''), r'''
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
''', r'''
(
a
,
*
b
,
c

)
''', r'''
Tuple - ROOT 0,0..8,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'c' Load - 6,0..6,1
  .ctx Load
'''),

(15, '', 0, 3, None, {}, (None, r'''
call(
a,
*
b,
c,
**
d
)
'''), r'''
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
''', r'''
(
a,
*
b,
c
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

(16, '', 0, 2, None, {}, (None,
r'''call(a, b=c, *d)'''),
r'''**NodeError('cannot get this Call.args slice because it includes parts after a keyword')**'''),

(17, '', 1, 2, None, {}, (None,
r'''call(a, b=c, *d)'''),
r'''**NodeError('cannot get this Call.args slice because it includes parts after a keyword')**'''),

(18, '', 0, 1, None, {}, (None,
r'''call(a, b, c=d, *e)'''),
r'''call(b, c=d, *e)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'b' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'e' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'c'
     .value Name 'd' Load - 0,10..0,11
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(19, '', 1, 2, None, {}, (None,
r'''call(a, b, c=d, *e)'''),
r'''call(a, c=d, *e)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'e' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'c'
     .value Name 'd' Load - 0,10..0,11
''',
r'''(b,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(20, '', 1, 2, None, {}, (None,
r'''call(a, b, c=d, *e,)'''),
r'''call(a, c=d, *e,)''', r'''
Call - ROOT 0,0..0,17
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'e' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'c'
     .value Name 'd' Load - 0,10..0,11
''',
r'''(b,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(21, '', 0, 1, None, {}, (None,
r'''call(i for i in j)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''((i for i in j),)''', r'''
Tuple - ROOT 0,0..0,17
  .elts[1]
   0] GeneratorExp - 0,1..0,15
     .elt Name 'i' Load - 0,2..0,3
     .generators[1]
      0] comprehension - 0,4..0,14
        .target Name 'i' Store - 0,8..0,9
        .iter Name 'j' Load - 0,13..0,14
        .is_async 0
  .ctx Load
'''),

(22, '', None, None, None, {}, (None,
r'''call(*not a, b, *c or d, *e)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''(*(not a), b, *(c or d), *e)''', r'''
Tuple - ROOT 0,0..0,28
  .elts[4]
   0] Starred - 0,1..0,9
     .value UnaryOp - 0,3..0,8
       .op Not - 0,3..0,6
       .operand Name 'a' Load - 0,7..0,8
     .ctx Load
   1] Name 'b' Load - 0,11..0,12
   2] Starred - 0,14..0,23
     .value BoolOp - 0,16..0,22
       .op Or
       .values[2]
        0] Name 'c' Load - 0,16..0,17
        1] Name 'd' Load - 0,21..0,22
     .ctx Load
   3] Starred - 0,25..0,27
     .value Name 'e' Load - 0,26..0,27
     .ctx Load
  .ctx Load
'''),

(23, '', None, None, None, {'pars': False, '_verify_get': False}, (None,
r'''call(*not a, b, *c or d, *e)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''(*not a, b, *c or d, *e)''', r'''
Tuple - ROOT 0,0..0,24
  .elts[4]
   0] Starred - 0,1..0,7
     .value UnaryOp - 0,2..0,7
       .op Not - 0,2..0,5
       .operand Name 'a' Load - 0,6..0,7
     .ctx Load
   1] Name 'b' Load - 0,9..0,10
   2] Starred - 0,12..0,19
     .value BoolOp - 0,13..0,19
       .op Or
       .values[2]
        0] Name 'c' Load - 0,13..0,14
        1] Name 'd' Load - 0,18..0,19
     .ctx Load
   3] Starred - 0,21..0,23
     .value Name 'e' Load - 0,22..0,23
     .ctx Load
  .ctx Load
'''),
],

'ClassDef_bases': [  # ................................................................................

(0, '', 0, 0, 'bases', {}, (None,
r'''class cls(a, *b): pass'''),
r'''class cls(a, *b): pass''', r'''
ClassDef - ROOT 0,0..0,22
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,15
     .value Name 'b' Load - 0,14..0,15
     .ctx Load
  .body[1]
   0] Pass - 0,18..0,22
''',
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
'''),

(1, '', None, None, 'bases', {}, (None,
r'''class cls(a, *b): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(2, '', None, None, 'bases', {}, (None,
r'''class cls (a) : pass'''),
r'''class cls  : pass''', r'''
ClassDef - ROOT 0,0..0,17
  .name 'cls'
  .body[1]
   0] Pass - 0,13..0,17
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(3, '', None, None, 'bases', {}, (None, r'''
class cls (
a
) : pass
'''),
r'''class cls  : pass''', r'''
ClassDef - ROOT 0,0..0,17
  .name 'cls'
  .body[1]
   0] Pass - 0,13..0,17
''', r'''
(
a,
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 1,0..1,1
  .ctx Load
'''),

(4, '', None, None, 'bases', {}, (None, r'''
class cls \
(a) \
 : pass
'''), r'''
class cls \
 \
 : pass
''', r'''
ClassDef - ROOT 0,0..2,7
  .name 'cls'
  .body[1]
   0] Pass - 2,3..2,7
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(5, '', 0, 1, 'bases', {}, (None,
r'''class cls(a, *b): pass'''),
r'''class cls(*b): pass''', r'''
ClassDef - ROOT 0,0..0,19
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,12
     .value Name 'b' Load - 0,11..0,12
     .ctx Load
  .body[1]
   0] Pass - 0,15..0,19
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(6, '', 1, 2, 'bases', {}, (None,
r'''class cls(a, *b): pass'''),
r'''class cls(a): pass''', r'''
ClassDef - ROOT 0,0..0,18
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,10..0,11
  .body[1]
   0] Pass - 0,14..0,18
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(7, '', None, None, 'bases', {}, (None,
r'''class cls(a, *b, c=d): pass'''),
r'''class cls(c=d): pass''', r'''
ClassDef - ROOT 0,0..0,20
  .name 'cls'
  .keywords[1]
   0] keyword - 0,10..0,13
     .arg 'c'
     .value Name 'd' Load - 0,12..0,13
  .body[1]
   0] Pass - 0,16..0,20
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(8, '', 0, 1, 'bases', {}, (None,
r'''class cls(a, *b, c=d): pass'''),
r'''class cls(*b, c=d): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,12
     .value Name 'b' Load - 0,11..0,12
     .ctx Load
  .keywords[1]
   0] keyword - 0,14..0,17
     .arg 'c'
     .value Name 'd' Load - 0,16..0,17
  .body[1]
   0] Pass - 0,20..0,24
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(9, '', 1, 2, 'bases', {}, (None,
r'''class cls(a, *b, c=d): pass'''),
r'''class cls(a, c=d): pass''', r'''
ClassDef - ROOT 0,0..0,23
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,10..0,11
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'c'
     .value Name 'd' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,19..0,23
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(10, '', None, None, 'bases', {}, (None,
r'''class cls(a, *b, **c): pass'''),
r'''class cls(**c): pass''', r'''
ClassDef - ROOT 0,0..0,20
  .name 'cls'
  .keywords[1]
   0] keyword - 0,10..0,13
     .value Name 'c' Load - 0,12..0,13
  .body[1]
   0] Pass - 0,16..0,20
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(11, '', 0, 1, 'bases', {}, (None,
r'''class cls(a, *b, **c): pass'''),
r'''class cls(*b, **c): pass''', r'''
ClassDef - ROOT 0,0..0,24
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,12
     .value Name 'b' Load - 0,11..0,12
     .ctx Load
  .keywords[1]
   0] keyword - 0,14..0,17
     .value Name 'c' Load - 0,16..0,17
  .body[1]
   0] Pass - 0,20..0,24
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(12, '', 1, 2, 'bases', {}, (None,
r'''class cls(a, *b, **c): pass'''),
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
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(13, '', 1, 2, 'bases', {}, (None, r'''
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
'''), r'''
class cls( \
a \
, \
c \
, \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..7,7
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'c' Load - 3,0..3,1
  .keywords[1]
   0] keyword - 5,0..6,1
     .value Name 'd' Load - 6,0..6,1
  .body[1]
   0] Pass - 7,3..7,7
''', r'''
(
* \
b \
, \
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[1]
   0] Starred - 1,0..2,1
     .value Name 'b' Load - 2,0..2,1
     .ctx Load
  .ctx Load
'''),

(14, '', 0, 3, 'bases', {}, (None, r'''
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
'''), r'''
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
''', r'''
(
a \
, \
* \
b \
, \
c \
 \
)
''', r'''
Tuple - ROOT 0,0..8,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'c' Load - 6,0..6,1
  .ctx Load
'''),

(15, '', 0, 3, 'bases', {}, (None, r'''
class cls( \
a, \
* \
b, \
c, \
** \
d \
): pass
'''), r'''
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
''', r'''
(
a, \
* \
b, \
c \
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

(16, '', 1, 2, 'bases', {}, (None, r'''
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
'''), r'''
class cls(
a
,
c
,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..7,7
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'c' Load - 3,0..3,1
  .keywords[1]
   0] keyword - 5,0..6,1
     .value Name 'd' Load - 6,0..6,1
  .body[1]
   0] Pass - 7,3..7,7
''', r'''
(
*
b
,
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[1]
   0] Starred - 1,0..2,1
     .value Name 'b' Load - 2,0..2,1
     .ctx Load
  .ctx Load
'''),

(17, '', 0, 3, 'bases', {}, (None, r'''
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
'''), r'''
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
''', r'''
(
a
,
*
b
,
c

)
''', r'''
Tuple - ROOT 0,0..8,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'c' Load - 6,0..6,1
  .ctx Load
'''),

(18, '', 0, 3, 'bases', {}, (None, r'''
class cls(
a,
*
b,
c,
**
d
): pass
'''), r'''
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
''', r'''
(
a,
*
b,
c
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

(19, '', 0, 2, 'bases', {}, (None,
r'''class cls(a, b=c, *d): pass'''),
r'''**NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')**'''),

(20, '', 1, 2, 'bases', {}, (None,
r'''class cls(a, b=c, *d): pass'''),
r'''**NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')**'''),

(21, '', 0, 1, 'bases', {}, (None,
r'''class cls(a, b, c=d, *e): pass'''),
r'''class cls(b, c=d, *e): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[2]
   0] Name 'b' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'e' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'c'
     .value Name 'd' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,23..0,27
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(22, '', 1, 2, 'bases', {}, (None,
r'''class cls(a, b, c=d, *e): pass'''),
r'''class cls(a, c=d, *e): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'e' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'c'
     .value Name 'd' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,23..0,27
''',
r'''(b,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(23, '', 1, 2, 'bases', {}, (None,
r'''class cls(a, b, c=d, *e,): pass'''),
r'''class cls(a, c=d, *e,): pass''', r'''
ClassDef - ROOT 0,0..0,28
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'e' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'c'
     .value Name 'd' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,24..0,28
''',
r'''(b,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

(24, '', None, None, 'bases', {}, (None,
r'''class cls(*not a, b, *c or d, *e): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''(*(not a), b, *(c or d), *e)''', r'''
Tuple - ROOT 0,0..0,28
  .elts[4]
   0] Starred - 0,1..0,9
     .value UnaryOp - 0,3..0,8
       .op Not - 0,3..0,6
       .operand Name 'a' Load - 0,7..0,8
     .ctx Load
   1] Name 'b' Load - 0,11..0,12
   2] Starred - 0,14..0,23
     .value BoolOp - 0,16..0,22
       .op Or
       .values[2]
        0] Name 'c' Load - 0,16..0,17
        1] Name 'd' Load - 0,21..0,22
     .ctx Load
   3] Starred - 0,25..0,27
     .value Name 'e' Load - 0,26..0,27
     .ctx Load
  .ctx Load
'''),

(25, '', None, None, 'bases', {'pars': False, '_verify_get': False}, (None,
r'''class cls(*not a, b, *c or d, *e): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''(*not a, b, *c or d, *e)''', r'''
Tuple - ROOT 0,0..0,24
  .elts[4]
   0] Starred - 0,1..0,7
     .value UnaryOp - 0,2..0,7
       .op Not - 0,2..0,5
       .operand Name 'a' Load - 0,6..0,7
     .ctx Load
   1] Name 'b' Load - 0,9..0,10
   2] Starred - 0,12..0,19
     .value BoolOp - 0,13..0,19
       .op Or
       .values[2]
        0] Name 'c' Load - 0,13..0,14
        1] Name 'd' Load - 0,18..0,19
     .ctx Load
   3] Starred - 0,21..0,23
     .value Name 'e' Load - 0,22..0,23
     .ctx Load
  .ctx Load
'''),
],

'ClassDef_bases_w_type_params': [  # ................................................................................

(0, '', 0, 0, 'bases', {'_ver': 12}, (None,
r'''class cls[T](a, *b): pass'''),
r'''class cls[T](a, *b): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,13..0,14
   1] Starred - 0,16..0,18
     .value Name 'b' Load - 0,17..0,18
     .ctx Load
  .body[1]
   0] Pass - 0,21..0,25
  .type_params[1]
   0] TypeVar - 0,10..0,11
     .name 'T'
''',
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
'''),

(1, '', None, None, 'bases', {'_ver': 12}, (None,
r'''class cls[T, *U](a, *b): pass'''),
r'''class cls[T, *U]: pass''', r'''
ClassDef - ROOT 0,0..0,22
  .name 'cls'
  .body[1]
   0] Pass - 0,18..0,22
  .type_params[2]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,13..0,15
     .name 'U'
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(2, '', None, None, 'bases', {'_ver': 12}, (None, r'''
class cls [T,
*U] (a) : pass
'''), r'''
class cls [T,
*U]  : pass
''', r'''
ClassDef - ROOT 0,0..1,11
  .name 'cls'
  .body[1]
   0] Pass - 1,7..1,11
  .type_params[2]
   0] TypeVar - 0,11..0,12
     .name 'T'
   1] TypeVarTuple - 1,0..1,2
     .name 'U'
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(3, '', None, None, 'bases', {'_ver': 12}, (None, r'''
class cls [
T
] \
(
a
) : pass
'''), r'''
class cls [
T
] \
 : pass
''', r'''
ClassDef - ROOT 0,0..3,7
  .name 'cls'
  .body[1]
   0] Pass - 3,3..3,7
  .type_params[1]
   0] TypeVar - 1,0..1,1
     .name 'T'
''', r'''
(
a,
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[1]
   0] Name 'a' Load - 1,0..1,1
  .ctx Load
'''),

(4, '', None, None, 'bases', {'_ver': 12}, (None, r'''
class cls \
[T] \
(a) \
 : pass
'''), r'''
class cls \
[T] \
 \
 : pass
''', r'''
ClassDef - ROOT 0,0..3,7
  .name 'cls'
  .body[1]
   0] Pass - 3,3..3,7
  .type_params[1]
   0] TypeVar - 1,1..1,2
     .name 'T'
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(5, '', 0, 1, 'bases', {'_ver': 12}, (None, r'''
class cls[T, *U
](a, *b): pass
'''), r'''
class cls[T, *U
](*b): pass
''', r'''
ClassDef - ROOT 0,0..1,11
  .name 'cls'
  .bases[1]
   0] Starred - 1,2..1,4
     .value Name 'b' Load - 1,3..1,4
     .ctx Load
  .body[1]
   0] Pass - 1,7..1,11
  .type_params[2]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,13..0,15
     .name 'U'
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(6, '', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls \
[
T, *U
] \
(a, *b): pass
'''), r'''
class cls \
[
T, *U
] \
(a): pass
''', r'''
ClassDef - ROOT 0,0..4,9
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 4,1..4,2
  .body[1]
   0] Pass - 4,5..4,9
  .type_params[2]
   0] TypeVar - 2,0..2,1
     .name 'T'
   1] TypeVarTuple - 2,3..2,5
     .name 'U'
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(7, '', None, None, 'bases', {'_ver': 12}, (None,
r'''class cls[T, *U, **V](a, *b, c=d): pass'''),
r'''class cls[T, *U, **V](c=d): pass''', r'''
ClassDef - ROOT 0,0..0,32
  .name 'cls'
  .keywords[1]
   0] keyword - 0,22..0,25
     .arg 'c'
     .value Name 'd' Load - 0,24..0,25
  .body[1]
   0] Pass - 0,28..0,32
  .type_params[3]
   0] TypeVar - 0,10..0,11
     .name 'T'
   1] TypeVarTuple - 0,13..0,15
     .name 'U'
   2] ParamSpec - 0,17..0,20
     .name 'V'
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(8, '', 0, 1, 'bases', {'_ver': 12}, (None, r'''
class cls \
[T, *U, \
**V] \
(a, *b, c=d): pass
'''), r'''
class cls \
[T, *U, \
**V] \
(*b, c=d): pass
''', r'''
ClassDef - ROOT 0,0..3,15
  .name 'cls'
  .bases[1]
   0] Starred - 3,1..3,3
     .value Name 'b' Load - 3,2..3,3
     .ctx Load
  .keywords[1]
   0] keyword - 3,5..3,8
     .arg 'c'
     .value Name 'd' Load - 3,7..3,8
  .body[1]
   0] Pass - 3,11..3,15
  .type_params[3]
   0] TypeVar - 1,1..1,2
     .name 'T'
   1] TypeVarTuple - 1,4..1,6
     .name 'U'
   2] ParamSpec - 2,0..2,3
     .name 'V'
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(9, '', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls[
T, *U, **V] \
(a, *b, c=d): pass
'''), r'''
class cls[
T, *U, **V] \
(a, c=d): pass
''', r'''
ClassDef - ROOT 0,0..2,14
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 2,1..2,2
  .keywords[1]
   0] keyword - 2,4..2,7
     .arg 'c'
     .value Name 'd' Load - 2,6..2,7
  .body[1]
   0] Pass - 2,10..2,14
  .type_params[3]
   0] TypeVar - 1,0..1,1
     .name 'T'
   1] TypeVarTuple - 1,3..1,5
     .name 'U'
   2] ParamSpec - 1,7..1,10
     .name 'V'
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(10, '', None, None, 'bases', {'_ver': 12}, (None,
r'''class cls [T, *U, **V] (a, *b, **c): pass'''),
r'''class cls [T, *U, **V] (**c): pass''', r'''
ClassDef - ROOT 0,0..0,34
  .name 'cls'
  .keywords[1]
   0] keyword - 0,24..0,27
     .value Name 'c' Load - 0,26..0,27
  .body[1]
   0] Pass - 0,30..0,34
  .type_params[3]
   0] TypeVar - 0,11..0,12
     .name 'T'
   1] TypeVarTuple - 0,14..0,16
     .name 'U'
   2] ParamSpec - 0,18..0,21
     .name 'V'
''',
r'''(a, *b)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Starred - 0,4..0,6
     .value Name 'b' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(11, '', 0, 1, 'bases', {'_ver': 12}, (None, r'''
class cls [T,
*U,
**V,
] (a, *b, **c): pass
'''), r'''
class cls [T,
*U,
**V,
] (*b, **c): pass
''', r'''
ClassDef - ROOT 0,0..3,17
  .name 'cls'
  .bases[1]
   0] Starred - 3,3..3,5
     .value Name 'b' Load - 3,4..3,5
     .ctx Load
  .keywords[1]
   0] keyword - 3,7..3,10
     .value Name 'c' Load - 3,9..3,10
  .body[1]
   0] Pass - 3,13..3,17
  .type_params[3]
   0] TypeVar - 0,11..0,12
     .name 'T'
   1] TypeVarTuple - 1,0..1,2
     .name 'U'
   2] ParamSpec - 2,0..2,3
     .name 'V'
''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(12, '', 1, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T,](a, *b, **c): pass'''),
r'''class cls[T,](a, **c): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,14..0,15
  .keywords[1]
   0] keyword - 0,17..0,20
     .value Name 'c' Load - 0,19..0,20
  .body[1]
   0] Pass - 0,23..0,27
  .type_params[1]
   0] TypeVar - 0,10..0,11
     .name 'T'
''',
r'''(*b,)''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'b' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(13, '', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls[ \
T \
, \
* \
U \
, \
** \
V \
, \
]( \
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
'''), r'''
class cls[ \
T \
, \
* \
U \
, \
** \
V \
, \
]( \
a \
, \
c \
, \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..16,7
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 10,0..10,1
   1] Name 'c' Load - 12,0..12,1
  .keywords[1]
   0] keyword - 14,0..15,1
     .value Name 'd' Load - 15,0..15,1
  .body[1]
   0] Pass - 16,3..16,7
  .type_params[3]
   0] TypeVar - 1,0..1,1
     .name 'T'
   1] TypeVarTuple - 3,0..4,1
     .name 'U'
   2] ParamSpec - 6,0..7,1
     .name 'V'
''', r'''
(
* \
b \
, \
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[1]
   0] Starred - 1,0..2,1
     .value Name 'b' Load - 2,0..2,1
     .ctx Load
  .ctx Load
'''),

(14, '', 0, 3, 'bases', {'_ver': 12}, (None, r'''
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
'''), r'''
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
( \
** \
d \
): pass
''', r'''
ClassDef - ROOT 0,0..14,7
  .name 'cls'
  .keywords[1]
   0] keyword - 12,0..13,1
     .value Name 'd' Load - 13,0..13,1
  .body[1]
   0] Pass - 14,3..14,7
  .type_params[3]
   0] TypeVar - 2,0..2,1
     .name 'T'
   1] TypeVarTuple - 4,0..5,1
     .name 'U'
   2] ParamSpec - 7,0..8,1
     .name 'V'
''', r'''
(
a \
, \
* \
b \
, \
c \
 \
)
''', r'''
Tuple - ROOT 0,0..8,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'c' Load - 6,0..6,1
  .ctx Load
'''),

(15, '', 0, 3, 'bases', {'_ver': 12}, (None, r'''
class cls[ \
T] \
( \
a, \
* \
b, \
c, \
** \
d \
): pass
'''), r'''
class cls[ \
T] \
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
   0] TypeVar - 1,0..1,1
     .name 'T'
''', r'''
(
a, \
* \
b, \
c \
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

(16, '', 1, 2, 'bases', {'_ver': 12}, (None, r'''
class cls[
T
,
*
U
,
**
V
,
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
'''), r'''
class cls[
T
,
*
U
,
**
V
,
](
a
,
c
,
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..16,7
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 10,0..10,1
   1] Name 'c' Load - 12,0..12,1
  .keywords[1]
   0] keyword - 14,0..15,1
     .value Name 'd' Load - 15,0..15,1
  .body[1]
   0] Pass - 16,3..16,7
  .type_params[3]
   0] TypeVar - 1,0..1,1
     .name 'T'
   1] TypeVarTuple - 3,0..4,1
     .name 'U'
   2] ParamSpec - 6,0..7,1
     .name 'V'
''', r'''
(
*
b
,
)
''', r'''
Tuple - ROOT 0,0..4,1
  .elts[1]
   0] Starred - 1,0..2,1
     .value Name 'b' Load - 2,0..2,1
     .ctx Load
  .ctx Load
'''),

(17, '', 0, 3, 'bases', {'_ver': 12}, (None, r'''
class cls[
T
,
*
U
,
**
V
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
'''), r'''
class cls[
T
,
*
U
,
**
V
] \
(
**
d
): pass
''', r'''
ClassDef - ROOT 0,0..12,7
  .name 'cls'
  .keywords[1]
   0] keyword - 10,0..11,1
     .value Name 'd' Load - 11,0..11,1
  .body[1]
   0] Pass - 12,3..12,7
  .type_params[3]
   0] TypeVar - 1,0..1,1
     .name 'T'
   1] TypeVarTuple - 3,0..4,1
     .name 'U'
   2] ParamSpec - 6,0..7,1
     .name 'V'
''', r'''
(
a
,
*
b
,
c

)
''', r'''
Tuple - ROOT 0,0..8,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 3,0..4,1
     .value Name 'b' Load - 4,0..4,1
     .ctx Load
   2] Name 'c' Load - 6,0..6,1
  .ctx Load
'''),

(18, '', 0, 3, 'bases', {'_ver': 12}, (None, r'''
class cls[ T, *U ](
a,
*
b,
c,
**
d
): pass
'''), r'''
class cls[ T, *U ](
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
  .type_params[2]
   0] TypeVar - 0,11..0,12
     .name 'T'
   1] TypeVarTuple - 0,14..0,16
     .name 'U'
''', r'''
(
a,
*
b,
c
)
''', r'''
Tuple - ROOT 0,0..5,1
  .elts[3]
   0] Name 'a' Load - 1,0..1,1
   1] Starred - 2,0..3,1
     .value Name 'b' Load - 3,0..3,1
     .ctx Load
   2] Name 'c' Load - 4,0..4,1
  .ctx Load
'''),

(19, '', 0, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T](a, b=c, *d): pass'''),
r'''**NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')**'''),

(20, '', 1, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T](a, b=c, *d): pass'''),
r'''**NodeError('cannot get this ClassDef.bases slice because it includes parts after a keyword')**'''),
],

'type_params': [  # ................................................................................

(0, 'body[0]', 1, 2, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T, *U, **V](): pass'''),
r'''def f[T, **V](): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] FunctionDef - 0,0..0,21
     .name 'f'
     .body[1]
      0] Pass - 0,17..0,21
     .type_params[2]
      0] TypeVar - 0,6..0,7
        .name 'T'
      1] ParamSpec - 0,9..0,12
        .name 'V'
''',
r'''*U''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVarTuple - 0,0..0,2
     .name 'U'
'''),

(1, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T, *U, **V](): pass'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
''',
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

(2, 'body[0]', 1, 2, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T, *U, **V](): pass'''),
r'''async def f[T, **V](): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
   0] AsyncFunctionDef - 0,0..0,27
     .name 'f'
     .body[1]
      0] Pass - 0,23..0,27
     .type_params[2]
      0] TypeVar - 0,12..0,13
        .name 'T'
      1] ParamSpec - 0,15..0,18
        .name 'V'
''',
r'''*U''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVarTuple - 0,0..0,2
     .name 'U'
'''),

(3, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T, *U, **V](): pass'''),
r'''async def f(): pass''', r'''
Module - ROOT 0,0..0,19
  .body[1]
   0] AsyncFunctionDef - 0,0..0,19
     .name 'f'
     .body[1]
      0] Pass - 0,15..0,19
''',
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

(4, 'body[0]', 1, 2, 'type_params', {'_ver': 12}, ('exec',
r'''class cls[T, *U, **V]: pass'''),
r'''class cls[T, **V]: pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] ClassDef - 0,0..0,23
     .name 'cls'
     .body[1]
      0] Pass - 0,19..0,23
     .type_params[2]
      0] TypeVar - 0,10..0,11
        .name 'T'
      1] ParamSpec - 0,13..0,16
        .name 'V'
''',
r'''*U''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVarTuple - 0,0..0,2
     .name 'U'
'''),

(5, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''class cls[T, *U, **V]: pass'''),
r'''class cls: pass''', r'''
Module - ROOT 0,0..0,15
  .body[1]
   0] ClassDef - 0,0..0,15
     .name 'cls'
     .body[1]
      0] Pass - 0,11..0,15
''',
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

(6, 'body[0]', 1, 2, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T, *U, **V] = ...'''),
r'''type t[T, **V] = ...''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] TypeAlias - 0,0..0,20
     .name Name 't' Store - 0,5..0,6
     .type_params[2]
      0] TypeVar - 0,7..0,8
        .name 'T'
      1] ParamSpec - 0,10..0,13
        .name 'V'
     .value Constant Ellipsis - 0,17..0,20
''',
r'''*U''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVarTuple - 0,0..0,2
     .name 'U'
'''),

(7, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T, *U, **V] = ...'''),
r'''type t = ...''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] TypeAlias - 0,0..0,12
     .name Name 't' Store - 0,5..0,6
     .value Constant Ellipsis - 0,9..0,12
''',
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

(8, '', 1, 2, 'type_params', {'_ver': 12}, ('_type_params',
r'''T, *U, **V'''),
r'''T, **V''', r'''
_type_params - ROOT 0,0..0,6
  .type_params[2]
   0] TypeVar - 0,0..0,1
     .name 'T'
   1] ParamSpec - 0,3..0,6
     .name 'V'
''',
r'''*U''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVarTuple - 0,0..0,2
     .name 'U'
'''),

(9, '', 0, 3, 'type_params', {'_ver': 12}, ('_type_params',
r'''T, *U, **V'''),
r'''''',
r'''_type_params - ROOT 0,0..0,0''',
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
],

}
