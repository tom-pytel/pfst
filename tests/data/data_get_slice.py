# (attr, start, stop, field, options, code | (parse_mode, code),
#
# code after cut,
# dump code after cut)
# - OR
# error)

DATA_GET_SLICE = {
'old_stmtlike': [  # ................................................................................

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
Module - ROOT 0,0..1,9
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
if 1:
    i
    # pre
    j ; # post
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
j ; # post
''', r'''
Module - ROOT 0,0..1,10
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
''',
r'''j  # post''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
Module - ROOT 0,0..1,9
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

('body[0]', 0, 1, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': 'block-1'}, ('exec', r'''
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

('body[0]', 1, 2, None, {'pep8space': True}, ('exec', r'''
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

('', 1, 2, None, {'pep8space': True}, ('exec', r'''
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

('', 1, 2, None, {'pep8space': True, 'trivia': 'block-3'}, ('exec', r'''
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

('', 1, 2, None, {'pep8space': True, 'trivia': 'block-4'}, ('exec', r'''
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

('', 1, 2, None, {'pep8space': True, 'trivia': 'block-5'}, ('exec', r'''
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

('', 1, 2, None, {'pep8space': True, 'trivia': 'block-6'}, ('exec', r'''
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

('', 1, 2, None, {'trivia': ('block-1', False), 'pep8space': False}, ('exec', r'''
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

('', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
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
j
''', r'''
Module - ROOT 0,0..2,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
   1] Expr - 2,0..2,1
     .value Name 'j' Load - 2,0..2,1
''', r'''
@deco1
@deco2
class cls:
  pass  # post
''', r'''
Module - ROOT 0,0..3,14
  .body[1]
   0] ClassDef - 2,0..3,6
     .name 'cls'
     .body[1]
      0] Pass - 3,2..3,6
     .decorator_list[2]
      0] Name 'deco1' Load - 0,1..0,6
      1] Name 'deco2' Load - 1,1..1,6
'''),

('', 1, 2, None, {'trivia': (True, True)}, ('exec', r'''
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
Module - ROOT 0,0..4,14
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

('', 0, 1, None, {'pep8space': True}, ('exec', r'''
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

('', 1, 2, None, {'pep8space': True}, ('exec', r'''
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

('', 0, 1, None, {'pep8space': 1}, ('exec', r'''
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

('', 1, 2, None, {'pep8space': 1}, ('exec', r'''
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

('body[0]', 0, 1, None, {'pep8space': True}, ('exec', r'''
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

('body[0]', 1, 2, None, {'pep8space': True}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (None, 'line-1')}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (None, 'line-2')}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (None, 'line-3')}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('body[0]', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('', 0, 1, None, {'trivia': (False, False), 'pep8space': False}, ('exec', r'''
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

('', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('body[0]', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('body[0]', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('body[0]', 0, 1, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('body[0]', 1, 2, None, {'trivia': (None, 'line-')}, ('exec', r'''
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

('', 0, 1, None, {'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 2, 3, None, {}, ('exec', r'''
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec',
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''

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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec',
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''

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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'norm': False, 'pep8space': False}, ('exec',
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'norm': False, 'pep8space': False}, ('exec', r'''

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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec',
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''

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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec',
r'''if 1: i ;  # post'''),
r'''if 1:''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] If - 0,0..0,5
     .test Constant 1 - 0,3..0,4
''',
r'''i ;  # post''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''

if 1: i ;  # post
'''), r'''

if 1:
''', r'''
Module - ROOT 0,0..1,5
  .body[1]
   0] If - 1,0..1,5
     .test Constant 1 - 1,3..1,4
''',
r'''i ;  # post''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'i' Load - 0,0..0,1
'''),

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'norm': False, 'pep8space': False}, ('exec',
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'norm': False, 'pep8space': False}, ('exec', r'''

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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': (True, False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('block-', False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('none-', False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('block-', False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('block-', True), 'pep8space': False}, ('exec', r'''
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
''',
r'''pass  # post''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,0..0,4
'''),

('body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': (False, False), 'norm': False, 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': (True, False), 'norm': False, 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': ('block-', False), 'norm': False, 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': ('none-', False), 'norm': False, 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': ('block-', False), 'norm': False, 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'finalbody', {'_verify': False, 'trivia': ('block-', True), 'norm': False, 'pep8space': False}, ('exec', r'''
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
''',
r'''pass  # post''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,0..0,4
'''),

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('all', False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': ('all-', False), 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''
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

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''
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
''',
r'''pass  # post''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,0..0,4
'''),

('body[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'norm': False, 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'orelse', {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'handlers', {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'handlers', {'_verify': False, 'trivia': (True, True)}, ('exec', r'''
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

('body[0]', 0, 1, 'handlers', {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
try: pass
except: pass  # post
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
r'''except: pass  # post''', r'''
_ExceptHandlers - ROOT 0,0..0,20
  .handlers[1]
   0] ExceptHandler - 0,0..0,12
     .body[1]
      0] Pass - 0,8..0,12
'''),

('body[0]', 0, 1, 'handlers', {'_verify': False, 'trivia': (False, False), 'pep8space': False}, ('exec', r'''
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

('body[0].handlers[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''
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

('body[0].handlers[0]', 0, 1, None, {'_verify': False, 'trivia': (True, True), 'norm': False}, ('exec', r'''
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

('body[0].handlers[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'norm': False, 'pep8space': False}, ('exec', r'''
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

('body[0].handlers[0]', 0, 1, None, {'_verify': False, 'trivia': (False, False), 'norm': False, 'pep8space': False}, ('exec', r'''
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

('body[0]', 0, 2, None, {'_verify': False, 'norm': False}, ('exec', r'''
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

('body[0]', 0, 2, None, {'_verify': False, 'norm': False}, ('exec', r'''
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

('body[0].value', 1, 3, None, {}, ('exec', r'''
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

('body[0].value', 0, 2, None, {}, ('exec', r'''
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

'old_exprlike': [  # ................................................................................

('body[0].value', 0, 0, None, {'norm': True}, ('exec',
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

('body[0].value', 0, 'end', None, {}, ('exec', r'''
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

('body[0].value', 0, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 2, 'end', None, {}, ('exec', r'''
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

('body[0].value', 0, 'end', None, {}, ('exec', r'''
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

('body[0].value', 0, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 2, 'end', None, {}, ('exec', r'''
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

('body[0].value', 1, 3, None, {}, ('exec',
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

('body[0].value', -1, 'end', None, {}, ('exec',
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

('body[0].value', 0, 'end', None, {}, ('exec',
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

('body[0].value', 1, 1, None, {}, ('exec',
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

('body[0].value', 1, 'end', None, {}, ('exec',
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

('body[0].value', 0, 3, None, {}, ('exec',
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].body[0].value', 0, 'end', None, {}, ('exec', r'''
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

('body[0].body[0].value', 0, 2, None, {}, ('exec', r'''
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

('body[0].body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].body[0].value', 2, 'end', None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec',
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

('body[0].value', 0, 'end', None, {}, ('exec',
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

('body[0].value', 2, 'end', None, {}, ('exec',
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

('body[0].value', 0, 'end', None, {}, ('exec', r'''
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

('body[0].value', 0, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 2, 'end', None, {}, ('exec', r'''
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

('body[0].value', 2, 3, None, {}, ('exec', r'''
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

('body[0].value', 2, 3, None, {}, ('exec', r'''
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

('body[0].value', 1, 3, None, {}, ('exec', r'''
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

('body[0].value', 1, 'end', None, {}, ('exec', r'''
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

('body[0].value', 0, 3, None, {}, ('exec', r'''
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

('body[0].value', 0, 1, None, {}, ('exec', r'''
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

('body[0].value', 0, 2, None, {}, ('exec', r'''
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

('body[0].value', 5, 7, None, {}, ('exec', r'''
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

('body[0].targets[0]', 1, 2, None, {}, ('exec',
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

('body[0].value', 1, 4, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec',
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

('body[0].decorator_list[0].args[0]', 0, 1, None, {}, ('exec', r'''
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

('body[0].body[0].targets[0]', 0, 2, None, {}, ('exec', r'''
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

('body[0].body[0].targets[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 0, 2, None, {'norm': True}, ('exec',
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

('body[0].value', 0, 0, None, {'norm': True}, ('exec',
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

('body[0].value', 0, 1, None, {}, ('exec',
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

('body[0].value', 1, 2, None, {}, ('exec',
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

('body[0].value', 2, 3, None, {}, ('exec',
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

('body[0].value', 0, 2, None, {}, ('exec',
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

('body[0].value', 1, 3, None, {}, ('exec',
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

('body[0].value', 0, 3, None, {}, ('exec',
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

('body[0].value', 1, 2, None, {'trivia': ('-1', '-1')}, ('exec', r'''
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

('body[0].value', 1, 2, None, {'trivia': ('block-1', 'line-1')}, ('exec', r'''
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

('body[0].value', 1, 2, None, {'trivia': ('block+1', 'line+1')}, ('exec', r'''
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

('body[0].value', 1, 2, None, {'trivia': ('all-1', 'block-1')}, ('exec', r'''
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

('body[0].value', 1, 2, None, {'trivia': ('all-1', 'all-1')}, ('exec', r'''
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

('body[0].value', 1, 2, None, {'trivia': ('all+1', 'all+1')}, ('exec', r'''
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

('body[0].value', 1, 2, None, {'trivia': ('all+1', 'all+1')}, ('exec', r'''
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

('body[0].value', 1, 2, None, {'trivia': (3, 5)}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec', r'''
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

('body[0].value', 1, 2, None, {'trivia': (False, 'block+1')}, ('exec', r'''
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

('body[0].value', 1, 2, None, {}, ('exec',
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

('body[0].cases[0].pattern', 0, 0, None, {'norm_get': False, '_verify': False}, ('exec', r'''
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

('body[0].cases[0].pattern', 0, 1, None, {'norm_get': False, 'norm_self': False, '_verify': False}, ('exec', r'''
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

('body[0].cases[0].pattern', 0, 2, None, {'norm_self': False, '_verify': False}, ('exec', r'''
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

('body[0].cases[0].pattern', 0, 1, None, {'norm_get': True, 'norm_self': True, '_verify': False}, ('exec', r'''
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

('body[0].cases[0].pattern', 1, 2, None, {'norm': True}, ('exec', r'''
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

('body[0].cases[0].pattern', 1, 3, None, {'trivia': (None, 'block')}, ('exec', r'''
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

('body[0]', 0, 2, None, {}, ('exec',
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

('body[0]', 1, 3, None, {}, ('exec',
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

('', 0, 4, None, {}, ('exec', r'''
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

('body[0]', 0, 4, None, {}, ('exec', r'''
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

('body[0]', 0, 4, None, {'docstr': 'strict'}, ('exec', r'''
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

('body[0]', 0, 4, None, {'docstr': False}, ('exec', r'''
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

('body[0]', 1, 4, None, {}, ('exec', r'''
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

('body[0]', 1, 4, None, {'docstr': 'strict'}, ('exec', r'''
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

('body[0]', 1, 4, None, {'docstr': False}, ('exec', r'''
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

'exprlike_trivia_leading': [  # ................................................................................

('', 1, 2, None, {'trivia': (False, False)}, (None, r'''
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

('', 1, 2, None, {'trivia': (False, False)}, (None, r'''
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

('', 1, 2, None, {'trivia': (False, False)}, (None, r'''
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

('', 1, 2, None, {'trivia': (False, False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
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

'exprlike_trivia_trailing': [  # ................................................................................

('', 0, 1, None, {'trivia': (False, False)}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, False)}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, False)}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, False)}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
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

'stmtlike_trivia_leading (currently not entirely to spec)': [  # ................................................................................

('', 1, 2, None, {'trivia': (False, False)}, (None, r'''
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

('', 1, 2, None, {'trivia': (False, False)}, (None, r'''
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

('', 1, 2, None, {'trivia': (False, False)}, (None, r'''
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

('', 1, 2, None, {'trivia': (False, False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
a

b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''

b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 1, 2, None, {'trivia': ('+1', False)}, (None, r'''
a
\
b
'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
''', r'''

b
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
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
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
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
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 1, 2, None, {'trivia': ('block+1', False)}, (None, r'''
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
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-1', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
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
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 3,0..3,1
     .value Name 'b' Load - 3,0..3,1
'''),

('', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
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
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 3,0..3,1
     .value Name 'b' Load - 3,0..3,1
'''),

('', 1, 2, None, {'trivia': ('block+', False)}, (None, r'''
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
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 3,0..3,1
     .value Name 'b' Load - 3,0..3,1
'''),

('', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('block-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
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
Module - ROOT 0,0..6,1
  .body[1]
   0] Expr - 6,0..6,1
     .value Name 'b' Load - 6,0..6,1
'''),

('', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
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
Module - ROOT 0,0..6,1
  .body[1]
   0] Expr - 6,0..6,1
     .value Name 'b' Load - 6,0..6,1
'''),

('', 1, 2, None, {'trivia': ('all+', False)}, (None, r'''
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
Module - ROOT 0,0..6,1
  .body[1]
   0] Expr - 6,0..6,1
     .value Name 'b' Load - 6,0..6,1
'''),

('', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
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

('', 1, 2, None, {'trivia': ('all-', False)}, (None, r'''
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

'stmtlike_trivia_trailing (currently not entirely to spec)': [  # ................................................................................

('', 0, 1, None, {'trivia': (False, False)}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, False)}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, False)}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, False)}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
a

b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, '+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
a # 1
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a # 1''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
a

b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''', r'''
a

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
a # 1
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a # 1''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line+1')}, (None, r'''
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
''',
r'''a  # 1''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
a # 1
b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a # 1''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
a  # 1

b
'''),
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
''',
r'''a  # 1''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'line-1')}, (None, r'''
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
''',
r'''a  # 1''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block+1')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block-1')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
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
Module - ROOT 0,0..3,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block+')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'block-')}, (None, r'''
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
Module - ROOT 0,0..1,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
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
Module - ROOT 0,0..6,0
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
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
Module - ROOT 0,0..4,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'all+')}, (None, r'''
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

('', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
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
Module - ROOT 0,0..4,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
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
Module - ROOT 0,0..4,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'trivia': (False, 'all-')}, (None, r'''
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
Module - ROOT 0,0..4,3
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),
],

'stmtlike_trailing_newline': [  # ................................................................................

('', 1, 2, None, {}, (None, r'''
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

('', 1, 2, None, {}, (None, r'''
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

('', 1, 2, None, {}, (None, r'''
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

('', 1, 2, None, {}, (None, r'''
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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
''',
r'''j = 2  # comment''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'j' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('', 1, 2, None, {}, ('exec', r'''
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

('', 1, 2, None, {}, ('exec', r'''
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

('', 0, 1, None, {}, ('exec',
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

('', 0, 1, None, {}, ('exec', r'''
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

('', 0, 1, None, {}, ('exec', r'''
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

'stmtlike_trailing_semicolon': [  # ................................................................................

('', 1, 2, None, {}, (None, r'''
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

('', 1, 2, None, {}, (None, r'''
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 2, None, {}, ('exec',
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

('', 1, 2, None, {}, (None, r'''
a = 1;
b = 2; \
c = 3
'''), r'''
a = 1;
c = 3
''', r'''
Module - ROOT 0,0..1,5
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 1,0..1,5
     .targets[1]
      0] Name 'c' Store - 1,0..1,1
     .value Constant 3 - 1,4..1,5
''',
r'''b = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('', 1, 2, None, {}, (None, r'''
if 1:
    a = 1;
    b = 2; \
    c = 3
'''), r'''
if 1:
    a = 1;
    c = 3
''', r'''
If - ROOT 0,0..2,9
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
''',
r'''b = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    a = 1;
    b = 2; \
    c = 3
'''), r'''
if 1:
    a = 1;
    c = 3
''', r'''
Module - ROOT 0,0..2,9
  .body[1]
   0] If - 0,0..2,9
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
''',
r'''b = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1: a = 1; b = 2; \
  c = 3
'''), r'''
if 1: a = 1; \
  c = 3
''', r'''
Module - ROOT 0,0..1,7
  .body[1]
   0] If - 0,0..1,7
     .test Constant 1 - 0,3..0,4
     .body[2]
      0] Assign - 0,6..0,11
        .targets[1]
         0] Name 'a' Store - 0,6..0,7
        .value Constant 1 - 0,10..0,11
      1] Assign - 1,2..1,7
        .targets[1]
         0] Name 'c' Store - 1,2..1,3
        .value Constant 3 - 1,6..1,7
''',
r'''b = 2''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('', 1, 2, None, {}, (None, r'''
a = 1;
b = 2;  # line
'''),
r'''a = 1;''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
''',
r'''b = 2;  # line''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('', 1, 2, None, {}, (None, r'''
if 1:
    a = 1;
    b = 2;  # line
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
r'''b = 2;  # line''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    a = 1;
    b = 2;  # line
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
r'''b = 2;  # line''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('body[0]', 1, 2, None, {}, ('exec',
r'''if 1: a = 1; b = 2;  # line'''),
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
r'''b = 2;  # line''', r'''
Module - ROOT 0,0..0,14
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'b' Store - 0,0..0,1
     .value Constant 2 - 0,4..0,5
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
try: pass
except: pass
else: truly_evil\
 ;
finally: pass
'''), r'''
try: pass
except: pass

finally: pass
''', r'''
Try - ROOT 0,0..3,13
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
  .finalbody[1]
   0] Pass - 3,9..3,13
''',
r'''truly_evil''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] Expr - 0,0..0,10
     .value Name 'truly_evil' Load - 0,0..0,10
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
try: pass
except: pass
else: beyond_truly_evil\
 ; \
\

\
finally: pass
'''), r'''
try: pass
except: pass
\

\
finally: pass
''', r'''
Try - ROOT 0,0..5,13
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
  .finalbody[1]
   0] Pass - 5,9..5,13
''',
r'''beyond_truly_evil''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] Expr - 0,0..0,17
     .value Name 'beyond_truly_evil' Load - 0,0..0,17
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
if 1: pass
else: oh_well\
 ; \
\

'''), r'''
if 1: pass
\

''', r'''
If - ROOT 0,0..0,10
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Pass - 0,6..0,10
''',
r'''oh_well''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Name 'oh_well' Load - 0,0..0,7
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
if 1: pass
else: oh_well\
 ; \
\
i = j
'''),
r'''if 1: pass''', r'''
If - ROOT 0,0..0,10
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Pass - 0,6..0,10
''', r'''
oh_well\
; \
\
i = j
''', r'''
Module - ROOT 0,0..3,5
  .body[2]
   0] Expr - 0,0..0,7
     .value Name 'oh_well' Load - 0,0..0,7
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'i' Store - 3,0..3,1
     .value Name 'j' Load - 3,4..3,5
'''),

('body[0]', 0, 'end', 'orelse', {}, ('exec', r'''
if 1: pass
else: oh_well\
 ; \
\

i = j
'''), r'''
if 1: pass
\

i = j
''', r'''
Module - ROOT 0,0..3,5
  .body[2]
   0] If - 0,0..0,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'i' Store - 3,0..3,1
     .value Name 'j' Load - 3,4..3,5
''',
r'''oh_well''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Name 'oh_well' Load - 0,0..0,7
'''),
],

'stmtlike_norm_self': [  # ................................................................................

('', 0, 'end', 'body', {}, ('exec',
r'''stmt'''),
r'''''',
r'''Module - ROOT 0,0..0,0''',
r'''stmt''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Name 'stmt' Load - 0,0..0,4
'''),

('', 0, 'end', 'body', {'norm': True}, ('single',
r'''stmt'''),
r'''**ValueError('cannot cut all elements from Interactive.body without norm_self=False')**''',
r'''stmt''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Name 'stmt' Load - 0,0..0,4
'''),

('', 0, 'end', 'body', {'norm_self': False, '_verify_self': False}, ('single',
r'''stmt'''),
r'''''',
r'''Interactive - ROOT 0,0..0,0''',
r'''stmt''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Name 'stmt' Load - 0,0..0,4
'''),

('', 0, 'end', 'body', {'norm': True}, (None,
r'''if 1: pass'''),
r'''**ValueError('cannot cut all elements from If.body without norm_self=False')**''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 'end', 'body', {'norm_self': False, '_verify_self': False}, (None,
r'''if 1: pass'''),
r'''if 1:''', r'''
If - ROOT 0,0..0,5
  .test Constant 1 - 0,3..0,4
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 'end', 'orelse', {}, (None, r'''
if 1: pass
else: pass
'''),
r'''if 1: pass''', r'''
If - ROOT 0,0..0,10
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] Pass - 0,6..0,10
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 'end', 'cases', {'norm': True}, (None, r'''
match a:
  case 1: pass
'''),
r'''**ValueError('cannot cut all elements from Match.cases without norm_self=False')**''',
r'''case 1: pass''', r'''
_match_cases - ROOT 0,0..0,12
  .cases[1]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
'''),

('', 0, 'end', 'cases', {'norm_self': False, '_verify_self': False}, (None, r'''
match a:
  case 1: pass
'''),
r'''match a:''', r'''
Match - ROOT 0,0..0,8
  .subject Name 'a' Load - 0,6..0,7
''',
r'''case 1: pass''', r'''
_match_cases - ROOT 0,0..0,12
  .cases[1]
   0] match_case - 0,0..0,12
     .pattern MatchValue - 0,5..0,6
       .value Constant 1 - 0,5..0,6
     .body[1]
      0] Pass - 0,8..0,12
'''),

('', 0, 'end', 'handlers', {'norm': True}, (None, r'''
try: pass
except: pass
'''),
r'''**ValueError('cannot cut all elements from Try.handlers without norm_self=False')**''',
r'''except: pass''', r'''
_ExceptHandlers - ROOT 0,0..0,12
  .handlers[1]
   0] ExceptHandler - 0,0..0,12
     .body[1]
      0] Pass - 0,8..0,12
'''),

('', 0, 'end', 'handlers', {'norm_self': False, '_verify_self': False}, (None, r'''
try: pass
except: pass
'''),
r'''try: pass''', r'''
Try - ROOT 0,0..0,9
  .body[1]
   0] Pass - 0,5..0,9
''',
r'''except: pass''', r'''
_ExceptHandlers - ROOT 0,0..0,12
  .handlers[1]
   0] ExceptHandler - 0,0..0,12
     .body[1]
      0] Pass - 0,8..0,12
'''),

('', 0, 'end', 'handlers', {}, (None, r'''
try: pass
except: pass
finally: pass
'''), r'''
try: pass
finally: pass
''', r'''
Try - ROOT 0,0..1,13
  .body[1]
   0] Pass - 0,5..0,9
  .finalbody[1]
   0] Pass - 1,9..1,13
''',
r'''except: pass''', r'''
_ExceptHandlers - ROOT 0,0..0,12
  .handlers[1]
   0] ExceptHandler - 0,0..0,12
     .body[1]
      0] Pass - 0,8..0,12
'''),

('', 0, 'end', 'finalbody', {'norm': True}, (None, r'''
try: pass
finally: pass
'''),
r'''**ValueError('cannot cut all elements from Try.finalbody without norm_self=False')**''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 'end', 'finalbody', {'norm_self': False, '_verify_self': False}, (None, r'''
try: pass
finally: pass
'''),
r'''try: pass''', r'''
Try - ROOT 0,0..0,9
  .body[1]
   0] Pass - 0,5..0,9
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 'end', 'finalbody', {}, (None, r'''
try: pass
except: pass
finally: pass
'''), r'''
try: pass
except: pass
''', r'''
Try - ROOT 0,0..1,12
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),
],

'stmtlike_bloc_trailing_comment': [  # ................................................................................

('', 1, 2, None, {'trivia': (False, False)}, ('exec', r'''
i = 1  # 1
# pre
if j:
    j = 2  # 2
# post
k = 1  # 3
'''), r'''
i = 1  # 1
# pre
# post
k = 1  # 3
''', r'''
Module - ROOT 0,0..3,10
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'k' Store - 3,0..3,1
     .value Constant 1 - 3,4..3,5
''', r'''
if j:
    j = 2  # 2
''', r'''
Module - ROOT 0,0..1,14
  .body[1]
   0] If - 0,0..1,9
     .test Name 'j' Load - 0,3..0,4
     .body[1]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'j' Store - 1,4..1,5
        .value Constant 2 - 1,8..1,9
'''),

('', 1, 2, None, {'trivia': (False, False)}, ('exec', r'''
i = 1  # 1
# pre
if j:
    j = 2 ;  # 2
# post
k = 1  # 3
'''), r'''
i = 1  # 1
# pre
# post
k = 1  # 3
''', r'''
Module - ROOT 0,0..3,10
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'k' Store - 3,0..3,1
     .value Constant 1 - 3,4..3,5
''', r'''
if j:
    j = 2 ;  # 2
''', r'''
Module - ROOT 0,0..1,16
  .body[1]
   0] If - 0,0..1,11
     .test Name 'j' Load - 0,3..0,4
     .body[1]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'j' Store - 1,4..1,5
        .value Constant 2 - 1,8..1,9
'''),

('', 1, 2, None, {'trivia': (False, False)}, ('exec', r'''
i = 1  # 1
# pre
if j: j = 2  # 2
# post
k = 1  # 3
'''), r'''
i = 1  # 1
# pre
# post
k = 1  # 3
''', r'''
Module - ROOT 0,0..3,10
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'k' Store - 3,0..3,1
     .value Constant 1 - 3,4..3,5
''',
r'''if j: j = 2  # 2''', r'''
Module - ROOT 0,0..0,16
  .body[1]
   0] If - 0,0..0,11
     .test Name 'j' Load - 0,3..0,4
     .body[1]
      0] Assign - 0,6..0,11
        .targets[1]
         0] Name 'j' Store - 0,6..0,7
        .value Constant 2 - 0,10..0,11
'''),

('', 1, 2, None, {'trivia': (False, False)}, ('exec', r'''
i = 1  # 1
# pre
if j: j = 2 ;  # 2
# post
k = 1  # 3
'''), r'''
i = 1  # 1
# pre
# post
k = 1  # 3
''', r'''
Module - ROOT 0,0..3,10
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'i' Store - 0,0..0,1
     .value Constant 1 - 0,4..0,5
   1] Assign - 3,0..3,5
     .targets[1]
      0] Name 'k' Store - 3,0..3,1
     .value Constant 1 - 3,4..3,5
''',
r'''if j: j = 2 ;  # 2''', r'''
Module - ROOT 0,0..0,18
  .body[1]
   0] If - 0,0..0,13
     .test Name 'j' Load - 0,3..0,4
     .body[1]
      0] Assign - 0,6..0,11
        .targets[1]
         0] Name 'j' Store - 0,6..0,7
        .value Constant 2 - 0,10..0,11
'''),
],

'trivia_stmtlike_by_ln': [  # ................................................................................

('', 0, 1, None, {'trivia': (6, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''), r'''
# ln 0

# ln 2

# ln 4
''',
r'''Module - ROOT 0,0..4,6''',
r'''pass  # ln 5''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (5, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''), r'''
# ln 0

# ln 2

# ln 4
''',
r'''Module - ROOT 0,0..4,6''',
r'''pass  # ln 5''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (4, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''), r'''
# ln 0

# ln 2

''',
r'''Module - ROOT 0,0..3,0''', r'''
# ln 4
pass  # ln 5
''', r'''
Module - ROOT 0,0..1,12
  .body[1]
   0] Pass - 1,0..1,4
'''),

('', 0, 1, None, {'trivia': (3, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''), r'''
# ln 0

# ln 2
''',
r'''Module - ROOT 0,0..2,6''', r'''

# ln 4
pass  # ln 5
''', r'''
Module - ROOT 0,0..2,12
  .body[1]
   0] Pass - 2,0..2,4
'''),

('', 0, 1, None, {'trivia': (2, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''), r'''
# ln 0

''',
r'''Module - ROOT 0,0..1,0''', r'''
# ln 2

# ln 4
pass  # ln 5
''', r'''
Module - ROOT 0,0..3,12
  .body[1]
   0] Pass - 3,0..3,4
'''),

('', 0, 1, None, {'trivia': (1, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''# ln 0''',
r'''Module - ROOT 0,0..0,6''', r'''

# ln 2

# ln 4
pass  # ln 5
''', r'''
Module - ROOT 0,0..4,12
  .body[1]
   0] Pass - 4,0..4,4
'''),

('', 0, 1, None, {'trivia': (0, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''''',
r'''Module - ROOT 0,0..0,0''', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
''', r'''
Module - ROOT 0,0..5,12
  .body[1]
   0] Pass - 5,0..5,4
'''),

('', 0, 1, None, {'trivia': (-1, 'line')}, ('exec', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
'''),
r'''''',
r'''Module - ROOT 0,0..0,0''', r'''
# ln 0

# ln 2

# ln 4
pass  # ln 5
''', r'''
Module - ROOT 0,0..5,12
  .body[1]
   0] Pass - 5,0..5,4
'''),

('', 0, 1, None, {'trivia': (False, 6)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''''',
r'''Module - ROOT 0,0..0,0''', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (False, 5)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''''',
r'''Module - ROOT 0,0..0,0''', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
''', r'''
Module - ROOT 0,0..5,6
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (False, 4)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''),
r'''# ln 5''',
r'''Module - ROOT 0,0..0,6''', r'''
pass  # ln 0
# ln 1

# ln 3

''', r'''
Module - ROOT 0,0..4,0
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (False, 3)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''), r'''

# ln 5
''',
r'''Module - ROOT 0,0..1,6''', r'''
pass  # ln 0
# ln 1

# ln 3
''', r'''
Module - ROOT 0,0..3,6
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (False, 2)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''), r'''
# ln 3

# ln 5
''',
r'''Module - ROOT 0,0..2,6''', r'''
pass  # ln 0
# ln 1

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (False, 1)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''), r'''

# ln 3

# ln 5
''',
r'''Module - ROOT 0,0..3,6''', r'''
pass  # ln 0
# ln 1
''', r'''
Module - ROOT 0,0..1,6
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (False, 0)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''), r'''
# ln 1

# ln 3

# ln 5
''',
r'''Module - ROOT 0,0..4,6''',
r'''pass  # ln 0''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (False, -1)}, ('exec', r'''
pass  # ln 0
# ln 1

# ln 3

# ln 5
'''), r'''
# ln 0
# ln 1

# ln 3

# ln 5
''',
r'''Module - ROOT 0,0..5,6''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (-1, 7)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''),
r'''''',
r'''Module - ROOT 0,0..0,0''', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
''', r'''
Module - ROOT 0,0..6,6
  .body[1]
   0] Pass - 3,0..3,4
'''),

('', 0, 1, None, {'trivia': (0, 6)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''),
r'''''',
r'''Module - ROOT 0,0..0,0''', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
''', r'''
Module - ROOT 0,0..6,6
  .body[1]
   0] Pass - 3,0..3,4
'''),

('', 0, 1, None, {'trivia': (1, 5)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 6
'''), r'''
# ln 0
# ln 6
''',
r'''Module - ROOT 0,0..1,6''', r'''

# ln 2
pass # ln 3
# ln 4

''', r'''
Module - ROOT 0,0..4,0
  .body[1]
   0] Pass - 2,0..2,4
'''),

('', 0, 1, None, {'trivia': (2, 4)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''), r'''
# ln 0


# ln 5
''',
r'''Module - ROOT 0,0..3,6''', r'''
# ln 2
pass # ln 3
# ln 4
''', r'''
Module - ROOT 0,0..2,6
  .body[1]
   0] Pass - 1,0..1,4
'''),

('', 0, 1, None, {'trivia': (3, 3)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''), r'''
# ln 0

# ln 2
# ln 4

# ln 5
''',
r'''Module - ROOT 0,0..5,6''',
r'''pass # ln 3''', r'''
Module - ROOT 0,0..0,11
  .body[1]
   0] Pass - 0,0..0,4
'''),

('', 0, 1, None, {'trivia': (4, 2)}, ('exec', r'''
# ln 0

# ln 2
pass # ln 3
# ln 4

# ln 5
'''), r'''
# ln 0

# ln 2
# ln 3
# ln 4

# ln 5
''',
r'''Module - ROOT 0,0..6,6''',
r'''pass''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Pass - 0,0..0,4
'''),
],

'trivia_exprlike_by_ln': [  # ................................................................................

('', 0, 1, None, {'trivia': (6, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''), r'''
[ # ln 0

# ln 2

# ln 4
]
''', r'''
List - ROOT 0,0..5,1
  .ctx Load
''', r'''
[
var,  # ln 5
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (5, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''), r'''
[ # ln 0

# ln 2

# ln 4
]
''', r'''
List - ROOT 0,0..5,1
  .ctx Load
''', r'''
[
var,  # ln 5
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (4, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''), r'''
[ # ln 0

# ln 2

]
''', r'''
List - ROOT 0,0..4,1
  .ctx Load
''', r'''
[
# ln 4
var,  # ln 5
]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Name 'var' Load - 2,0..2,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (3, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''), r'''
[ # ln 0

# ln 2
]
''', r'''
List - ROOT 0,0..3,1
  .ctx Load
''', r'''
[

# ln 4
var,  # ln 5
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'var' Load - 3,0..3,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (2, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''), r'''
[ # ln 0

]
''', r'''
List - ROOT 0,0..2,1
  .ctx Load
''', r'''
[
# ln 2

# ln 4
var,  # ln 5
]
''', r'''
List - ROOT 0,0..5,1
  .elts[1]
   0] Name 'var' Load - 4,0..4,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (1, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''), r'''
[ # ln 0
]
''', r'''
List - ROOT 0,0..1,1
  .ctx Load
''', r'''
[

# ln 2

# ln 4
var,  # ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'var' Load - 5,0..5,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (0, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''), r'''
[ # ln 0
]
''', r'''
List - ROOT 0,0..1,1
  .ctx Load
''', r'''
[

# ln 2

# ln 4
var,  # ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'var' Load - 5,0..5,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (-1, 'line')}, ('List', r'''
[ # ln 0

# ln 2

# ln 4
var,  # ln 5
]
'''), r'''
[ # ln 0
]
''', r'''
List - ROOT 0,0..1,1
  .ctx Load
''', r'''
[

# ln 2

# ln 4
var,  # ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'var' Load - 5,0..5,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 6)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''), r'''
[ # ln 0
]
''', r'''
List - ROOT 0,0..1,1
  .ctx Load
''', r'''
[
var,  # ln 1

# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 5)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''), r'''
[ # ln 0
]
''', r'''
List - ROOT 0,0..1,1
  .ctx Load
''', r'''
[
var,  # ln 1

# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 4)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''), r'''
[ # ln 0
# ln 5
]
''', r'''
List - ROOT 0,0..2,1
  .ctx Load
''', r'''
[
var,  # ln 1

# ln 3

]
''', r'''
List - ROOT 0,0..5,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 3)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''), r'''
[ # ln 0

# ln 5
]
''', r'''
List - ROOT 0,0..3,1
  .ctx Load
''', r'''
[
var,  # ln 1

# ln 3
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 2)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''), r'''
[ # ln 0
# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..4,1
  .ctx Load
''', r'''
[
var,  # ln 1

]
''', r'''
List - ROOT 0,0..3,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 1)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''), r'''
[ # ln 0

# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..5,1
  .ctx Load
''', r'''
[
var,  # ln 1
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, 0)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''), r'''
[ # ln 0
# ln 1

# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .ctx Load
''',
r'''[var,]''', r'''
List - ROOT 0,0..0,6
  .elts[1]
   0] Name 'var' Load - 0,1..0,4
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (False, -1)}, ('List', r'''
[ # ln 0
var,  # ln 1

# ln 3

# ln 5
]
'''), r'''
[ # ln 0
# ln 1

# ln 3

# ln 5
]
''', r'''
List - ROOT 0,0..6,1
  .ctx Load
''',
r'''[var,]''', r'''
List - ROOT 0,0..0,6
  .elts[1]
   0] Name 'var' Load - 0,1..0,4
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (-1, 7)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''), r'''
[ # ln 0
]
''', r'''
List - ROOT 0,0..1,1
  .ctx Load
''', r'''
[

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
''', r'''
List - ROOT 0,0..7,1
  .elts[1]
   0] Name 'var' Load - 3,0..3,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (0, 6)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''), r'''
[ # ln 0
]
''', r'''
List - ROOT 0,0..1,1
  .ctx Load
''', r'''
[

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
''', r'''
List - ROOT 0,0..7,1
  .elts[1]
   0] Name 'var' Load - 3,0..3,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (1, 5)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''), r'''
[ # ln 0
# ln 6
]
''', r'''
List - ROOT 0,0..2,1
  .ctx Load
''', r'''
[

# ln 2
var,  # ln 3
# ln 4

]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'var' Load - 3,0..3,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (2, 4)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''), r'''
[ # ln 0


# ln 6
]
''', r'''
List - ROOT 0,0..4,1
  .ctx Load
''', r'''
[
# ln 2
var,  # ln 3
# ln 4
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'var' Load - 2,0..2,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (3, 3)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''), r'''
[ # ln 0

# ln 2
# ln 4

# ln 6
]
''', r'''
List - ROOT 0,0..6,1
  .ctx Load
''', r'''
[
var,  # ln 3
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'var' Load - 1,0..1,3
  .ctx Load
'''),

('', 0, 1, None, {'trivia': (4, 2)}, ('List', r'''
[ # ln 0

# ln 2
var,  # ln 3
# ln 4

# ln 6
]
'''), r'''
[ # ln 0

# ln 2
# ln 3
# ln 4

# ln 6
]
''', r'''
List - ROOT 0,0..7,1
  .ctx Load
''',
r'''[var,]''', r'''
List - ROOT 0,0..0,6
  .elts[1]
   0] Name 'var' Load - 0,1..0,4
  .ctx Load
'''),

('', 1, 2, None, {'trivia': (1, 1)}, (None, r'''
a, # 0
b, # 1
c, # 2
'''), r'''
a, # 0
c, # 2
''', r'''
Module - ROOT 0,0..1,6
  .body[2]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Name 'a' Load - 0,0..0,1
       .ctx Load
   1] Expr - 1,0..1,2
     .value Tuple - 1,0..1,2
       .elts[1]
        0] Name 'c' Load - 1,0..1,1
       .ctx Load
''',
r'''b, # 1''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Name 'b' Load - 0,0..0,1
       .ctx Load
'''),

('', 1, 2, None, {'trivia': (0, 1)}, (None, r'''
a, # 0
b, # 1
c, # 2
'''), r'''
a, # 0
c, # 2
''', r'''
Module - ROOT 0,0..1,6
  .body[2]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Name 'a' Load - 0,0..0,1
       .ctx Load
   1] Expr - 1,0..1,2
     .value Tuple - 1,0..1,2
       .elts[1]
        0] Name 'c' Load - 1,0..1,1
       .ctx Load
''',
r'''b, # 1''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Name 'b' Load - 0,0..0,1
       .ctx Load
'''),

('', 1, 2, None, {'trivia': (1, 0)}, (None, r'''
a, # 0
b, # 1
c, # 2
'''), r'''
a, # 0
# 1
c, # 2
''', r'''
Module - ROOT 0,0..2,6
  .body[2]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Name 'a' Load - 0,0..0,1
       .ctx Load
   1] Expr - 2,0..2,2
     .value Tuple - 2,0..2,2
       .elts[1]
        0] Name 'c' Load - 2,0..2,1
       .ctx Load
''',
r'''b,''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Tuple - 0,0..0,2
       .elts[1]
        0] Name 'b' Load - 0,0..0,1
       .ctx Load
'''),
],

'Tuple_elts': [  # ................................................................................

('slice', 0, 'end', None, {'_ver': 11}, (None,
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

('slice', 0, 'end', None, {'_ver': 11, 'pars': False, '_verify_get': False}, (None,
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

('slice', 0, 'end', None, {'_ver': 11, 'pars': False, 'pars_arglike': None, '_verify_get': False}, (None,
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

('slice', 0, 'end', None, {'_ver': 11, 'pars_arglike': False, '_verify_get': False}, (None,
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

('', 1, 3, None, {'pars': 'auto'}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
d, # 3
'''), r'''
a, # 0
d, # 3
''', r'''
Tuple - ROOT 0,0..1,2
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'd' Load - 1,0..1,1
  .ctx Load
''', r'''
b, # 1
c, # 2
''', r'''
Tuple - ROOT 0,0..1,2
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 1,0..1,1
  .ctx Load
'''),

('', 1, 3, None, {'pars': True}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
d, # 3
'''), r'''
(a, # 0
d, # 3
)
''', r'''
Tuple - ROOT 0,0..2,1
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'd' Load - 1,0..1,1
  .ctx Load
''', r'''
(
b, # 1
c, # 2
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'b' Load - 1,0..1,1
   1] Name 'c' Load - 2,0..2,1
  .ctx Load
'''),

('', 1, 3, None, {'pars': False}, ('Tuple', r'''
a, # 0
b, # 1
c, # 2
d, # 3
'''), r'''
a, # 0
d, # 3
''', r'''
Tuple - ROOT 0,0..1,2
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'd' Load - 1,0..1,1
  .ctx Load
''', r'''
b, # 1
c, # 2
''', r'''
Tuple - ROOT 0,0..1,2
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 1,0..1,1
  .ctx Load
'''),

('', 1, 3, None, {'pars': 'auto'}, ('Tuple', r'''
(
    a, # 0
    b, # 1
    c, # 2
    d, # 3
)
'''), r'''
(
    a, # 0
    d, # 3
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'a' Load - 1,4..1,5
   1] Name 'd' Load - 2,4..2,5
  .ctx Load
''', r'''
(
    b, # 1
    c, # 2
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'b' Load - 1,4..1,5
   1] Name 'c' Load - 2,4..2,5
  .ctx Load
'''),

('', 1, 3, None, {'pars': True}, ('Tuple', r'''
(
    a, # 0
    b, # 1
    c, # 2
    d, # 3
)
'''), r'''
(
    a, # 0
    d, # 3
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'a' Load - 1,4..1,5
   1] Name 'd' Load - 2,4..2,5
  .ctx Load
''', r'''
(
    b, # 1
    c, # 2
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'b' Load - 1,4..1,5
   1] Name 'c' Load - 2,4..2,5
  .ctx Load
'''),

('', 1, 3, None, {'pars': False}, ('Tuple', r'''
(
    a, # 0
    b, # 1
    c, # 2
    d, # 3
)
'''), r'''
(
    a, # 0
    d, # 3
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'a' Load - 1,4..1,5
   1] Name 'd' Load - 2,4..2,5
  .ctx Load
''', r'''
(
    b, # 1
    c, # 2
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'b' Load - 1,4..1,5
   1] Name 'c' Load - 2,4..2,5
  .ctx Load
'''),

('value', 1, 3, None, {'pars': 'auto'}, (None,
r'''i = a, b, c, d'''),
r'''i = a, d''', r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,8
    .elts[2]
     0] Name 'a' Load - 0,4..0,5
     1] Name 'd' Load - 0,7..0,8
    .ctx Load
''',
r'''b, c''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 0,3..0,4
  .ctx Load
'''),

('value', 1, 3, None, {'pars': True}, (None,
r'''i = a, b, c, d'''),
r'''i = a, d''', r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,8
    .elts[2]
     0] Name 'a' Load - 0,4..0,5
     1] Name 'd' Load - 0,7..0,8
    .ctx Load
''',
r'''b, c''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 0,3..0,4
  .ctx Load
'''),

('value', 1, 3, None, {'pars': False}, (None,
r'''i = a, b, c, d'''),
r'''i = a, d''', r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..0,8
    .elts[2]
     0] Name 'a' Load - 0,4..0,5
     1] Name 'd' Load - 0,7..0,8
    .ctx Load
''',
r'''b, c''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 0,3..0,4
  .ctx Load
'''),

('value', 1, 3, None, {'pars': 'auto'}, (None, r'''
i = a, \
    b, \
    c, \
    d,
'''), r'''
i = a, \
    d,
''', r'''
Assign - ROOT 0,0..1,6
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..1,6
    .elts[2]
     0] Name 'a' Load - 0,4..0,5
     1] Name 'd' Load - 1,4..1,5
    .ctx Load
''', r'''
(
    b, \
    c, \
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'b' Load - 1,4..1,5
   1] Name 'c' Load - 2,4..2,5
  .ctx Load
'''),

('value', 1, 3, None, {'pars': True}, (None, r'''
i = a, \
    b, \
    c, \
    d,
'''), r'''
i = a, \
    d,
''', r'''
Assign - ROOT 0,0..1,6
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..1,6
    .elts[2]
     0] Name 'a' Load - 0,4..0,5
     1] Name 'd' Load - 1,4..1,5
    .ctx Load
''', r'''
(
    b, \
    c, \
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'b' Load - 1,4..1,5
   1] Name 'c' Load - 2,4..2,5
  .ctx Load
'''),

('value', 1, 3, None, {'pars': False}, (None, r'''
i = a, \
    b, \
    c, \
    d,
'''), r'''
i = a, \
    d,
''', r'''
Assign - ROOT 0,0..1,6
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..1,6
    .elts[2]
     0] Name 'a' Load - 0,4..0,5
     1] Name 'd' Load - 1,4..1,5
    .ctx Load
''', r'''
b, \
    c,
''', r'''
Tuple - ROOT 0,0..1,6
  .elts[2]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'c' Load - 1,4..1,5
  .ctx Load
'''),

('value', 1, 3, None, {'pars': False}, (None, r'''
i = (
    a, \
    b, \
    c, \
    d,
)
'''), r'''
i = (
    a, \
    d,
)
''', r'''
Assign - ROOT 0,0..3,1
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value Tuple - 0,4..3,1
    .elts[2]
     0] Name 'a' Load - 1,4..1,5
     1] Name 'd' Load - 2,4..2,5
    .ctx Load
''', r'''
(
    b, \
    c, \
)
''', r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Name 'b' Load - 1,4..1,5
   1] Name 'c' Load - 2,4..2,5
  .ctx Load
'''),
],

'Delete_targets': [  # ................................................................................

('body[0]', 1, 2, None, {}, ('exec',
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

('body[0]', 1, 3, None, {}, ('exec',
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

('body[0]', 0, 2, None, {}, ('exec',
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 0, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 3, None, {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
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

('', 0, 3, None, {'norm': True}, (None,
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

('', 0, 3, None, {'norm_self': False, '_verify_self': False}, (None, r'''
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

('body[0]', 1, 2, None, {}, (None, r'''
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

('', 0, 0, None, {}, (None,
r'''del a'''),
r'''del a''', r'''
Delete - ROOT 0,0..0,5
  .targets[1]
   0] Name 'a' Del - 0,4..0,5
''',
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
'''),
],

'Assign_targets': [  # ................................................................................

('body[0]', 0, 2, 'targets', {}, ('exec',
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

('body[0]', 1, 2, 'targets', {}, ('exec',
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

('body[0]', 1, 3, 'targets', {}, ('exec',
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

('body[0]', 2, 3, 'targets', {}, ('exec',
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

('body[0]', 3, 3, 'targets', {'_verify': False}, ('exec',
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

('body[0]', 0, 2, 'targets', {}, ('exec', r'''
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

('body[0]', 1, 2, 'targets', {}, ('exec', r'''
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

('body[0]', 1, 3, 'targets', {}, ('exec', r'''
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

('body[0]', 2, 3, 'targets', {}, ('exec', r'''
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

('body[0]', 3, 3, 'targets', {}, ('exec', r'''
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

('', 0, 2, 'targets', {}, ('_Assign_targets', r'''
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

('', 1, 2, 'targets', {}, ('_Assign_targets', r'''
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

('', 1, 3, 'targets', {}, ('_Assign_targets', r'''
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

('', 2, 3, 'targets', {}, ('_Assign_targets', r'''
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

('', 3, 3, 'targets', {}, ('_Assign_targets', r'''
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

('', 0, 3, 'targets', {'norm': True}, (None,
r'''a = b = c = z'''),
r'''**ValueError('cannot cut all Assign.targets without norm_self=False')**''',
r'''a = b = c =''', r'''
_Assign_targets - ROOT 0,0..0,11
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
   2] Name 'c' Store - 0,8..0,9
'''),

('', 0, 3, 'targets', {'norm_self': False, '_verify_self': False}, (None,
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

('body[0]', 1, 2, 'items', {}, ('exec',
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

('body[0]', 1, 3, 'items', {}, ('exec',
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

('body[0]', 0, 2, 'items', {}, ('exec',
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

('body[0]', 1, 2, 'items', {}, ('exec', r'''
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

('body[0]', 0, 2, 'items', {}, ('exec', r'''
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

('body[0]', 1, 3, 'items', {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
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

('', 0, 3, 'items', {'norm': True}, (None,
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

('', 0, 3, 'items', {'norm_self': False, '_verify_self': False}, (None, r'''
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

('body[0]', 1, 2, 'items', {}, (None, r'''
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

('body[0]', 1, 2, 'items', {}, ('exec',
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

('body[0]', 1, 3, 'items', {}, ('exec',
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

('body[0]', 0, 2, 'items', {}, ('exec',
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

('body[0]', 1, 2, 'items', {}, ('exec', r'''
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

('body[0]', 0, 2, 'items', {}, ('exec', r'''
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

('body[0]', 1, 3, 'items', {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
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

('', 0, 3, 'items', {'norm': True}, (None,
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

('', 0, 3, 'items', {'norm_self': False, '_verify_self': False}, (None, r'''
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

('body[0]', 1, 2, 'items', {}, (None, r'''
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

('body[0]', 1, 2, 'items', {}, ('exec',
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

('body[0]', 1, 3, 'items', {}, ('exec',
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

('body[0]', 0, 2, 'items', {}, ('exec',
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

('body[0]', 1, 2, 'items', {}, ('exec', r'''
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

('body[0]', 0, 2, 'items', {}, ('exec', r'''
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

('body[0]', 1, 3, 'items', {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
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

('', 0, 3, 'items', {'norm': True}, (None,
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

('', 0, 3, 'items', {'norm_self': False, '_verify_self': False}, (None, r'''
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

('body[0]', 1, 2, 'items', {}, (None, r'''
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

('body[0]', 1, 2, 'items', {}, ('exec',
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

('body[0]', 1, 3, 'items', {}, ('exec',
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

('body[0]', 0, 2, 'items', {}, ('exec',
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

('body[0]', 1, 2, 'items', {}, ('exec', r'''
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

('body[0]', 0, 2, 'items', {}, ('exec', r'''
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

('body[0]', 1, 3, 'items', {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, 'items', {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, 'items', {}, ('exec', r'''
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

('', 0, 3, 'items', {'norm': True}, (None,
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

('', 0, 3, 'items', {'norm_self': False, '_verify_self': False}, (None, r'''
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

('body[0]', 1, 2, 'items', {}, (None, r'''
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

('body[0]', 1, 2, None, {}, ('exec',
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

('body[0]', 1, 3, None, {}, ('exec',
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

('body[0]', 0, 2, None, {}, ('exec',
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 0, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 3, None, {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
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

('', 0, 3, None, {'norm': True}, (None,
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

('', 0, 3, None, {'norm_self': False, '_verify_self': False}, (None, r'''
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

('body[0]', 1, 2, None, {}, (None, r'''
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

('body[0]', 1, 2, None, {}, ('exec',
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

('body[0]', 1, 3, None, {}, ('exec',
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

('body[0]', 0, 2, None, {}, ('exec',
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 0, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 3, None, {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
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

('', 0, 3, None, {'norm': True}, (None,
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

('', 0, 3, None, {'norm_self': False, '_verify_self': False}, (None, r'''
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

('body[0]', 1, 2, None, {}, (None, r'''
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

('', 0, 0, None, {}, (None,
r'''from mod import a'''),
r'''from mod import a''', r'''
ImportFrom - ROOT 0,0..0,17
  .module 'mod'
  .names[1]
   0] alias - 0,16..0,17
     .name 'a'
  .level 0
''',
r'''''',
r'''_aliases - ROOT 0,0..0,0'''),
],

'ImportFrom_names_w_pars': [  # ................................................................................

('body[0]', 1, 2, None, {}, ('exec',
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

('body[0]', 1, 3, None, {}, ('exec',
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

('body[0]', 0, 2, None, {}, ('exec',
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 0, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 3, None, {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
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

('', 0, 3, None, {'norm': True}, (None,
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

('', 0, 3, None, {'norm_self': False, '_verify_self': False}, (None, r'''
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

('body[0]', 1, 2, None, {}, (None, r'''
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

('body[0]', 1, 2, None, {}, ('exec',
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

('body[0]', 1, 3, None, {}, ('exec',
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

('body[0]', 0, 2, None, {}, ('exec',
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 0, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 3, None, {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 0, 'end', None, {'norm': True}, ('exec',
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

('body[0]', 0, 'end', None, {'norm_self': False, '_verify_self': False}, ('exec',
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

('body[0]', 1, 2, None, {}, (None, r'''
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

('', 0, 0, None, {}, (None,
r'''global a'''),
r'''global a''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'a'
''',
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
'''),

('', 2, 'end', None, {}, (None,
r'''global a, b, c'''),
r'''global a, b''', r'''
Global - ROOT 0,0..0,11
  .names[2]
   0] 'a'
   1] 'b'
''',
r'''c,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'c' Load - 0,0..0,1
  .ctx Load
'''),
],

'Nonlocal_names': [  # ................................................................................

('body[0]', 1, 2, None, {}, ('exec',
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

('body[0]', 1, 3, None, {}, ('exec',
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

('body[0]', 0, 2, None, {}, ('exec',
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

('body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 0, 2, None, {}, ('exec', r'''
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

('body[0]', 1, 3, None, {}, ('exec', r'''
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

('body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

('body[0].body[0]', 1, 2, None, {}, ('exec', r'''
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

('body[0]', 0, 'end', None, {'norm': True}, ('exec',
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

('body[0]', 0, 'end', None, {'norm_self': False, '_verify_self': False}, ('exec',
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

('body[0]', 1, 2, None, {}, (None, r'''
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

'ClassDef_bases': [  # ................................................................................

('', 0, 0, 'bases', {}, (None,
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

('', 0, 'end', 'bases', {}, (None,
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

('', 0, 'end', 'bases', {}, (None,
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

('', 0, 'end', 'bases', {}, (None, r'''
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

('', 0, 'end', 'bases', {}, (None, r'''
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

('', 0, 1, 'bases', {}, (None,
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

('', 1, 2, 'bases', {}, (None,
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

('', 0, 'end', 'bases', {}, (None,
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

('', 0, 1, 'bases', {}, (None,
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

('', 1, 2, 'bases', {}, (None,
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

('', 0, 'end', 'bases', {}, (None,
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

('', 0, 1, 'bases', {}, (None,
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

('', 1, 2, 'bases', {}, (None,
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

('', 0, 3, 'bases', {}, (None, r'''
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

('', 0, 3, 'bases', {}, (None, r'''
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

('', 0, 2, 'bases', {}, (None,
r'''class cls(a, b=c, *d): pass'''),
r'''**NodeError("cannot get ClassDef.bases slice because it includes keywords, try the '_bases' field")**'''),

('', 1, 2, 'bases', {}, (None,
r'''class cls(a, b=c, *d): pass'''),
r'''**NodeError("cannot get ClassDef.bases slice because it includes keywords, try the '_bases' field")**'''),

('', 0, 1, 'bases', {}, (None,
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

('', 1, 2, 'bases', {}, (None,
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

('', 1, 2, 'bases', {}, (None,
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

('', 0, 'end', 'bases', {}, (None,
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

('', 0, 'end', 'bases', {'pars': False, '_verify_get': False}, (None,
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
],

'ClassDef_bases_w_type_params': [  # ................................................................................

('', 0, 0, 'bases', {'_ver': 12}, (None,
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

('', 0, 'end', 'bases', {'_ver': 12}, (None,
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

('', 0, 'end', 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 'end', 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 'end', 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 1, 'bases', {'_ver': 12}, (None, r'''
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

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 'end', 'bases', {'_ver': 12}, (None,
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

('', 0, 1, 'bases', {'_ver': 12}, (None, r'''
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

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 'end', 'bases', {'_ver': 12}, (None,
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

('', 0, 1, 'bases', {'_ver': 12}, (None, r'''
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

('', 1, 2, 'bases', {'_ver': 12}, (None,
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

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 3, 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 3, 'bases', {'_ver': 12}, (None, r'''
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

('', 1, 2, 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 3, 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 3, 'bases', {'_ver': 12}, (None, r'''
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

('', 0, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T](a, b=c, *d): pass'''),
r'''**NodeError("cannot get ClassDef.bases slice because it includes keywords, try the '_bases' field")**'''),

('', 1, 2, 'bases', {'_ver': 12}, (None,
r'''class cls[T](a, b=c, *d): pass'''),
r'''**NodeError("cannot get ClassDef.bases slice because it includes keywords, try the '_bases' field")**'''),
],

'ClassDef_keywords': [  # ................................................................................

('', 1, 'end', 'keywords', {}, (None,
r'''class cls(a, b=c, *d, **e): pass'''),
r'''class cls(a, b=c, *d): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'd' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'b'
     .value Name 'c' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,23..0,27
''',
r'''**e''', r'''
_arglikes - ROOT 0,0..0,3
  .arglikes[1]
   0] keyword - 0,0..0,3
     .value Name 'e' Load - 0,2..0,3
'''),

('', -1, 'end', 'keywords', {}, (None,
r'''class cls(a, b=c, *d, **e): pass'''),
r'''class cls(a, b=c, *d): pass''', r'''
ClassDef - ROOT 0,0..0,27
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'd' Load - 0,19..0,20
     .ctx Load
  .keywords[1]
   0] keyword - 0,13..0,16
     .arg 'b'
     .value Name 'c' Load - 0,15..0,16
  .body[1]
   0] Pass - 0,23..0,27
''',
r'''**e''', r'''
_arglikes - ROOT 0,0..0,3
  .arglikes[1]
   0] keyword - 0,0..0,3
     .value Name 'e' Load - 0,2..0,3
'''),

('', -2, 'end', 'keywords', {}, (None,
r'''class cls(a, b=c, *d, **e): pass'''),
r'''**NodeError("cannot get ClassDef.keywords slice because it includes bases, try the '_bases' field")**'''),
],

'ClassDef__bases': [  # ................................................................................

('', 0, 4, '_bases', {}, (None,
r'''class cls(a, *not b, c, e=f, *g, **h, i=j): pass'''),
r'''class cls(*g, **h, i=j): pass''', r'''
ClassDef - ROOT 0,0..0,29
  .name 'cls'
  .bases[1]
   0] Starred - 0,10..0,12
     .value Name 'g' Load - 0,11..0,12
     .ctx Load
  .keywords[2]
   0] keyword - 0,14..0,17
     .value Name 'h' Load - 0,16..0,17
   1] keyword - 0,19..0,22
     .arg 'i'
     .value Name 'j' Load - 0,21..0,22
  .body[1]
   0] Pass - 0,25..0,29
''',
r'''a, *not b, c, e=f''', r'''
_arglikes - ROOT 0,0..0,17
  .arglikes[4]
   0] Name 'a' Load - 0,0..0,1
   1] Starred - 0,3..0,9
     .value UnaryOp - 0,4..0,9
       .op Not - 0,4..0,7
       .operand Name 'b' Load - 0,8..0,9
     .ctx Load
   2] Name 'c' Load - 0,11..0,12
   3] keyword - 0,14..0,17
     .arg 'e'
     .value Name 'f' Load - 0,16..0,17
'''),

('', 1, 5, '_bases', {}, (None,
r'''class cls(a, *not b, c, e=f, *g, **h, i=j): pass'''),
r'''class cls(a, **h, i=j): pass''', r'''
ClassDef - ROOT 0,0..0,28
  .name 'cls'
  .bases[1]
   0] Name 'a' Load - 0,10..0,11
  .keywords[2]
   0] keyword - 0,13..0,16
     .value Name 'h' Load - 0,15..0,16
   1] keyword - 0,18..0,21
     .arg 'i'
     .value Name 'j' Load - 0,20..0,21
  .body[1]
   0] Pass - 0,24..0,28
''',
r'''*not b, c, e=f, *g''', r'''
_arglikes - ROOT 0,0..0,18
  .arglikes[4]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'b' Load - 0,5..0,6
     .ctx Load
   1] Name 'c' Load - 0,8..0,9
   2] keyword - 0,11..0,14
     .arg 'e'
     .value Name 'f' Load - 0,13..0,14
   3] Starred - 0,16..0,18
     .value Name 'g' Load - 0,17..0,18
     .ctx Load
'''),

('', 2, 6, '_bases', {}, (None,
r'''class cls(a, *not b, c, e=f, *g, **h, i=j): pass'''),
r'''class cls(a, *not b, i=j): pass''', r'''
ClassDef - ROOT 0,0..0,31
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,19
     .value UnaryOp - 0,14..0,19
       .op Not - 0,14..0,17
       .operand Name 'b' Load - 0,18..0,19
     .ctx Load
  .keywords[1]
   0] keyword - 0,21..0,24
     .arg 'i'
     .value Name 'j' Load - 0,23..0,24
  .body[1]
   0] Pass - 0,27..0,31
''',
r'''c, e=f, *g, **h''', r'''
_arglikes - ROOT 0,0..0,15
  .arglikes[4]
   0] Name 'c' Load - 0,0..0,1
   1] keyword - 0,3..0,6
     .arg 'e'
     .value Name 'f' Load - 0,5..0,6
   2] Starred - 0,8..0,10
     .value Name 'g' Load - 0,9..0,10
     .ctx Load
   3] keyword - 0,12..0,15
     .value Name 'h' Load - 0,14..0,15
'''),

('', 3, 7, '_bases', {}, (None,
r'''class cls(a, *not b, c, e=f, *g, **h, i=j): pass'''),
r'''class cls(a, *not b, c): pass''', r'''
ClassDef - ROOT 0,0..0,29
  .name 'cls'
  .bases[3]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,19
     .value UnaryOp - 0,14..0,19
       .op Not - 0,14..0,17
       .operand Name 'b' Load - 0,18..0,19
     .ctx Load
   2] Name 'c' Load - 0,21..0,22
  .body[1]
   0] Pass - 0,25..0,29
''',
r'''e=f, *g, **h, i=j''', r'''
_arglikes - ROOT 0,0..0,17
  .arglikes[4]
   0] keyword - 0,0..0,3
     .arg 'e'
     .value Name 'f' Load - 0,2..0,3
   1] Starred - 0,5..0,7
     .value Name 'g' Load - 0,6..0,7
     .ctx Load
   2] keyword - 0,9..0,12
     .value Name 'h' Load - 0,11..0,12
   3] keyword - 0,14..0,17
     .arg 'i'
     .value Name 'j' Load - 0,16..0,17
'''),

('', 0, 0, '_bases', {}, (None,
r'''class cls: pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''''',
r'''_arglikes - ROOT 0,0..0,0'''),

('', 0, 'end', '_bases', {}, (None,
r'''class cls(a, *not b, c, e=f, *g, **h, i=j): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''a, *not b, c, e=f, *g, **h, i=j''', r'''
_arglikes - ROOT 0,0..0,31
  .arglikes[7]
   0] Name 'a' Load - 0,0..0,1
   1] Starred - 0,3..0,9
     .value UnaryOp - 0,4..0,9
       .op Not - 0,4..0,7
       .operand Name 'b' Load - 0,8..0,9
     .ctx Load
   2] Name 'c' Load - 0,11..0,12
   3] keyword - 0,14..0,17
     .arg 'e'
     .value Name 'f' Load - 0,16..0,17
   4] Starred - 0,19..0,21
     .value Name 'g' Load - 0,20..0,21
     .ctx Load
   5] keyword - 0,23..0,26
     .value Name 'h' Load - 0,25..0,26
   6] keyword - 0,28..0,31
     .arg 'i'
     .value Name 'j' Load - 0,30..0,31
'''),
],

'BoolOp_values': [  # ................................................................................

('', 0, 0, None, {'_verify_get': False}, (None,
r'''a or b'''),
r'''a or b''', r'''
BoolOp - ROOT 0,0..0,6
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,5..0,6
''',
r'''''', r'''
BoolOp - ROOT 0,0..0,0
  .op Or
'''),

('', 0, 1, None, {'_verify': False}, (None,
r'''(a or b) or c'''),
r'''c''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'c' Load - 0,0..0,1
''',
r'''(a or b)''', r'''
BoolOp - ROOT 0,0..0,8
  .op Or
  .values[1]
   0] BoolOp - 0,1..0,7
     .op Or
     .values[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,6..0,7
'''),

('', 0, 1, None, {'norm': True}, (None,
r'''(a or b) or c'''),
r'''c''',
r'''Name 'c' Load - ROOT 0,0..0,1''',
r'''(a or b)''', r'''
BoolOp - ROOT 0,1..0,7
  .op Or
  .values[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,6..0,7
'''),

('', 1, 2, None, {'_verify': False}, (None,
r'''a or (b or c)'''),
r'''a''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
''',
r'''(b or c)''', r'''
BoolOp - ROOT 0,0..0,8
  .op Or
  .values[1]
   0] BoolOp - 0,1..0,7
     .op Or
     .values[2]
      0] Name 'b' Load - 0,1..0,2
      1] Name 'c' Load - 0,6..0,7
'''),

('', 1, 2, None, {'norm': True}, (None,
r'''a or (b or c)'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1''',
r'''(b or c)''', r'''
BoolOp - ROOT 0,1..0,7
  .op Or
  .values[2]
   0] Name 'b' Load - 0,1..0,2
   1] Name 'c' Load - 0,6..0,7
'''),

('', 0, 1, None, {'_verify_get': False}, (None,
r'''(a) or (b) or (c)'''),
r'''(b) or (c)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'b' Load - 0,1..0,2
   1] Name 'c' Load - 0,8..0,9
''',
r'''(a)''', r'''
BoolOp - ROOT 0,0..0,3
  .op Or
  .values[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, None, {'_verify_get': False}, (None,
r'''(a) or (b) or (c)'''),
r'''(a) or (c)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'c' Load - 0,8..0,9
''',
r'''(b)''', r'''
BoolOp - ROOT 0,0..0,3
  .op Or
  .values[1]
   0] Name 'b' Load - 0,1..0,2
'''),

('', 2, 3, None, {'_verify_get': False}, (None,
r'''(a) or (b) or (c)'''),
r'''(a) or (b)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,8..0,9
''',
r'''(c)''', r'''
BoolOp - ROOT 0,0..0,3
  .op Or
  .values[1]
   0] Name 'c' Load - 0,1..0,2
'''),

('', 0, 2, None, {'_verify_self': False}, (None,
r'''(a) or (b) or (c)'''),
r'''(c)''', r'''
BoolOp - ROOT 0,0..0,3
  .op Or
  .values[1]
   0] Name 'c' Load - 0,1..0,2
''',
r'''(a) or (b)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,8..0,9
'''),

('', 0, 2, None, {'_verify_self': False, 'norm_self': True}, (None,
r'''(a) or (b) or (c)'''),
r'''(c)''',
r'''Name 'c' Load - ROOT 0,1..0,2''',
r'''(a) or (b)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,8..0,9
'''),

('', 1, 3, None, {'_verify_self': False}, (None,
r'''(a) or (b) or (c)'''),
r'''(a)''', r'''
BoolOp - ROOT 0,0..0,3
  .op Or
  .values[1]
   0] Name 'a' Load - 0,1..0,2
''',
r'''(b) or (c)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'b' Load - 0,1..0,2
   1] Name 'c' Load - 0,8..0,9
'''),

('', 1, 3, None, {'_verify_self': False, 'norm_self': True}, (None,
r'''(a) or (b) or (c)'''),
r'''(a)''',
r'''Name 'a' Load - ROOT 0,1..0,2''',
r'''(b) or (c)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'b' Load - 0,1..0,2
   1] Name 'c' Load - 0,8..0,9
'''),

('', 0, 3, None, {'_verify_self': False}, (None,
r'''(a) or (b) or (c)'''),
r'''''', r'''
BoolOp - ROOT 0,0..0,0
  .op Or
''',
r'''(a) or (b) or (c)''', r'''
BoolOp - ROOT 0,0..0,17
  .op Or
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,8..0,9
   2] Name 'c' Load - 0,15..0,16
'''),

('', 0, 3, None, {'norm_self': True}, (None,
r'''(a) or (b) or (c)'''),
r'''**ValueError("cannot cut all BoolOp.values without 'norm_self=False'")**''',
r'''(a) or (b) or (c)''', r'''
BoolOp - ROOT 0,0..0,17
  .op Or
  .values[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,8..0,9
   2] Name 'c' Load - 0,15..0,16
'''),

('', 0, 1, None, {'norm': True}, (None,
r'''(a) or (b) or (c)'''),
r'''(b) or (c)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'b' Load - 0,1..0,2
   1] Name 'c' Load - 0,8..0,9
''',
r'''(a)''',
r'''Name 'a' Load - ROOT 0,1..0,2'''),

('', 1, 2, None, {'norm_get': True}, (None,
r'''(a) or (b) or (c)'''),
r'''(a) or (c)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'c' Load - 0,8..0,9
''',
r'''(b)''',
r'''Name 'b' Load - ROOT 0,1..0,2'''),

('', 2, 3, None, {'norm_get': True}, (None,
r'''(a) or (b) or (c)'''),
r'''(a) or (b)''', r'''
BoolOp - ROOT 0,0..0,10
  .op Or
  .values[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,8..0,9
''',
r'''(c)''',
r'''Name 'c' Load - ROOT 0,1..0,2'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, False)}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a # line
# post

# post post

or c
''', r'''
BoolOp - ROOT 0,0..5,4
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 5,3..5,4
''', r'''

# pre pre

# pre
b
''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, False)}, (None, r'''
a or

# pre pre

# pre
b or # line
# post

# post post

c
'''), r'''
a or # line
# post

# post post

c
''', r'''
BoolOp - ROOT 0,0..5,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 5,0..5,1
''', r'''

# pre pre

# pre
b
''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, 'line')}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a
# post

# post post

or c
''', r'''
BoolOp - ROOT 0,0..5,4
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 5,3..5,4
''', r'''

# pre pre

# pre
b # line

''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('block', 'block')}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a

# post post

or c
''', r'''
BoolOp - ROOT 0,0..4,4
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 4,3..4,4
''', r'''

# pre pre

# pre
b # line
# post

''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('block+', 'block+')}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a
# post post

or c
''', r'''
BoolOp - ROOT 0,0..3,4
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 3,3..3,4
''', r'''

# pre pre

# pre
b # line
# post


''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('all', 'all')}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a

or c
''', r'''
BoolOp - ROOT 0,0..2,4
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 2,3..2,4
''', r'''

# pre pre

# pre
b # line
# post

# post post

''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('all+', 'all+')}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a
or c
''', r'''
BoolOp - ROOT 0,0..1,4
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 1,3..1,4
''', r'''

# pre pre

# pre
b # line
# post

# post post


''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, False), 'op_side': 'right'}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a or

# pre pre

# pre
c
''', r'''
BoolOp - ROOT 0,0..5,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 5,0..5,1
''', r'''

b # line
# post

# post post


''', r'''
BoolOp - ROOT 1,0..1,1
  .op Or
  .values[1]
   0] Name 'b' Load - 1,0..1,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, False), 'op_side': 'right'}, (None, r'''
a or

# pre pre

# pre
b or # line
# post

# post post

c
'''), r'''
a or

# pre pre

# pre
# line
# post

# post post

c
''', r'''
BoolOp - ROOT 0,0..10,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 10,0..10,1
''',
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, 'line'), 'op_side': 'right'}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a or

# pre pre

# pre
c
''', r'''
BoolOp - ROOT 0,0..5,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 5,0..5,1
''', r'''

b # line
# post

# post post


''', r'''
BoolOp - ROOT 1,0..1,1
  .op Or
  .values[1]
   0] Name 'b' Load - 1,0..1,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('block', 'block'), 'op_side': 'right'}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a or

# pre pre

c
''', r'''
BoolOp - ROOT 0,0..4,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 4,0..4,1
''', r'''

# pre
b # line
# post

# post post


''', r'''
BoolOp - ROOT 2,0..2,1
  .op Or
  .values[1]
   0] Name 'b' Load - 2,0..2,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('block+', 'block+'), 'op_side': 'right'}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a or

# pre pre
c
''', r'''
BoolOp - ROOT 0,0..3,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 3,0..3,1
''', r'''


# pre
b # line
# post

# post post


''', r'''
BoolOp - ROOT 3,0..3,1
  .op Or
  .values[1]
   0] Name 'b' Load - 3,0..3,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('all', 'all'), 'op_side': 'right'}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a or

c
''', r'''
BoolOp - ROOT 0,0..2,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 2,0..2,1
''', r'''

# pre pre

# pre
b # line
# post

# post post


''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('all+', 'all+'), 'op_side': 'right'}, (None, r'''
a or

# pre pre

# pre
b # line
# post

# post post

or c
'''), r'''
a or
c
''', r'''
BoolOp - ROOT 0,0..1,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'c' Load - 1,0..1,1
''', r'''


# pre pre

# pre
b # line
# post

# post post


''', r'''
BoolOp - ROOT 5,0..5,1
  .op Or
  .values[1]
   0] Name 'b' Load - 5,0..5,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None,
r'''a or b'''),
r'''a''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None, r'''
a
# pre-op
or b
'''), r'''
a

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
''', r'''

# pre-op
b
''', r'''
BoolOp - ROOT 2,0..2,1
  .op Or
  .values[1]
   0] Name 'b' Load - 2,0..2,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None, r'''
a or
# pre-val
b
'''),
r'''a''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
''', r'''
# pre-val
b
''', r'''
BoolOp - ROOT 1,0..1,1
  .op Or
  .values[1]
   0] Name 'b' Load - 1,0..1,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None, r'''
a
# pre-op
or
# pre-val
b
'''), r'''
a

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
''', r'''

# pre-op
# pre-val
b
''', r'''
BoolOp - ROOT 3,0..3,1
  .op Or
  .values[1]
   0] Name 'b' Load - 3,0..3,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None, r'''
a
# pre-op
or \
# pre-val
b
'''), r'''
a

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
''', r'''

# pre-op
 \
# pre-val
b
''', r'''
BoolOp - ROOT 4,0..4,1
  .op Or
  .values[1]
   0] Name 'b' Load - 4,0..4,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None,
r'''a or b'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a or
# post-op
b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a
# post-op

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a
# post-val
or b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a
# post-val

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a
# post-val
or
# post-op
b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a
# post-val
# post-op

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a
# post-val
or \
# post-op
b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a
# post-val
 \
# post-op

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a or  # line
# post-op
b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a  # line
# post-op

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a  # line
# post-val
or b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a  # line
# post-val

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a  # line
# post-val
or
# post-op
b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a  # line
# post-val
# post-op

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a  # line
# post-val
or \
# post-op
b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a  # line
# post-val
 \
# post-op

''', r'''
BoolOp - ROOT 0,0..0,1
  .op Or
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, None, {'_verify': False}, (None,
r'''a and b'''),
r'''a and b''', r'''
BoolOp - ROOT 0,0..0,7
  .op And
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 0,6..0,7
''',
r'''''', r'''
BoolOp - ROOT 0,0..0,0
  .op And
'''),

('', 0, 1, None, {'_verify': False}, (None, r'''
a
and
b
'''),
r'''b''', r'''
BoolOp - ROOT 0,0..0,1
  .op And
  .values[1]
   0] Name 'b' Load - 0,0..0,1
''', r'''
a

''', r'''
BoolOp - ROOT 0,0..0,1
  .op And
  .values[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 1, 2, None, {'_verify': False}, (None, r'''
a
and
b
'''), r'''
a

''', r'''
BoolOp - ROOT 0,0..0,1
  .op And
  .values[1]
   0] Name 'a' Load - 0,0..0,1
''', r'''

b
''', r'''
BoolOp - ROOT 1,0..1,1
  .op And
  .values[1]
   0] Name 'b' Load - 1,0..1,1
'''),
],

'Compare__all': [  # ................................................................................

('', 0, 1, None, {'_verify': False}, (None,
r'''(a < b) < c'''),
r'''c''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'c' Load - 0,0..0,1
''',
r'''(a < b)''', r'''
Compare - ROOT 0,0..0,7
  .left Compare - 0,1..0,6
    .left Name 'a' Load - 0,1..0,2
    .ops[1]
     0] Lt - 0,3..0,4
    .comparators[1]
     0] Name 'b' Load - 0,5..0,6
'''),

('', 0, 1, None, {'norm': True}, (None,
r'''(a < b) < c'''),
r'''c''',
r'''Name 'c' Load - ROOT 0,0..0,1''',
r'''(a < b)''', r'''
Compare - ROOT 0,1..0,6
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] Lt - 0,3..0,4
  .comparators[1]
   0] Name 'b' Load - 0,5..0,6
'''),

('', 1, 2, None, {'_verify': False}, (None,
r'''a < (b < c)'''),
r'''a''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
''',
r'''(b < c)''', r'''
Compare - ROOT 0,0..0,7
  .left Compare - 0,1..0,6
    .left Name 'b' Load - 0,1..0,2
    .ops[1]
     0] Lt - 0,3..0,4
    .comparators[1]
     0] Name 'c' Load - 0,5..0,6
'''),

('', 1, 2, None, {'norm': True}, (None,
r'''a < (b < c)'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1''',
r'''(b < c)''', r'''
Compare - ROOT 0,1..0,6
  .left Name 'b' Load - 0,1..0,2
  .ops[1]
   0] Lt - 0,3..0,4
  .comparators[1]
   0] Name 'c' Load - 0,5..0,6
'''),

('', 0, 1, None, {'_verify_get': False}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(b) not in (c)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'b' Load - 0,1..0,2
  .ops[1]
   0] NotIn - 0,4..0,10
  .comparators[1]
   0] Name 'c' Load - 0,12..0,13
''',
r'''(a)''', r'''
Compare - ROOT 0,0..0,3
  .left Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, None, {'_verify_get': False}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(a) not in (c)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] NotIn - 0,4..0,10
  .comparators[1]
   0] Name 'c' Load - 0,12..0,13
''',
r'''(b)''', r'''
Compare - ROOT 0,0..0,3
  .left Name 'b' Load - 0,1..0,2
'''),

('', 1, 2, None, {'_verify_get': False, 'op_side': 'right'}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(a) is not (c)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] IsNot - 0,4..0,10
  .comparators[1]
   0] Name 'c' Load - 0,12..0,13
''',
r'''(b)''', r'''
Compare - ROOT 0,0..0,3
  .left Name 'b' Load - 0,1..0,2
'''),

('', 2, 3, None, {'_verify_get': False}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(a) is not (b)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] IsNot - 0,4..0,10
  .comparators[1]
   0] Name 'b' Load - 0,12..0,13
''',
r'''(c)''', r'''
Compare - ROOT 0,0..0,3
  .left Name 'c' Load - 0,1..0,2
'''),

('', 0, 2, None, {'_verify_self': False}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(c)''', r'''
Compare - ROOT 0,0..0,3
  .left Name 'c' Load - 0,1..0,2
''',
r'''(a) is not (b)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] IsNot - 0,4..0,10
  .comparators[1]
   0] Name 'b' Load - 0,12..0,13
'''),

('', 0, 2, None, {'_verify_self': False, 'norm_self': True}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(c)''',
r'''Name 'c' Load - ROOT 0,1..0,2''',
r'''(a) is not (b)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] IsNot - 0,4..0,10
  .comparators[1]
   0] Name 'b' Load - 0,12..0,13
'''),

('', 1, 3, None, {'_verify_self': False}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(a)''', r'''
Compare - ROOT 0,0..0,3
  .left Name 'a' Load - 0,1..0,2
''',
r'''(b) not in (c)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'b' Load - 0,1..0,2
  .ops[1]
   0] NotIn - 0,4..0,10
  .comparators[1]
   0] Name 'c' Load - 0,12..0,13
'''),

('', 1, 3, None, {'_verify_self': False, 'norm_self': True}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(a)''',
r'''Name 'a' Load - ROOT 0,1..0,2''',
r'''(b) not in (c)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'b' Load - 0,1..0,2
  .ops[1]
   0] NotIn - 0,4..0,10
  .comparators[1]
   0] Name 'c' Load - 0,12..0,13
'''),

('', 0, 3, None, {}, (None,
r'''(a) is not (b) not in (c)'''),
r'''**ValueError('cannot cut all nodes from Compare')**''',
r'''(a) is not (b) not in (c)''', r'''
Compare - ROOT 0,0..0,25
  .left Name 'a' Load - 0,1..0,2
  .ops[2]
   0] IsNot - 0,4..0,10
   1] NotIn - 0,15..0,21
  .comparators[2]
   0] Name 'b' Load - 0,12..0,13
   1] Name 'c' Load - 0,23..0,24
'''),

('', 0, 1, None, {'norm': True}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(b) not in (c)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'b' Load - 0,1..0,2
  .ops[1]
   0] NotIn - 0,4..0,10
  .comparators[1]
   0] Name 'c' Load - 0,12..0,13
''',
r'''(a)''',
r'''Name 'a' Load - ROOT 0,1..0,2'''),

('', 1, 2, None, {'norm_get': True}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(a) not in (c)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] NotIn - 0,4..0,10
  .comparators[1]
   0] Name 'c' Load - 0,12..0,13
''',
r'''(b)''',
r'''Name 'b' Load - ROOT 0,1..0,2'''),

('', 1, 2, None, {'norm_get': True, 'op_side': 'right'}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(a) is not (c)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] IsNot - 0,4..0,10
  .comparators[1]
   0] Name 'c' Load - 0,12..0,13
''',
r'''(b)''',
r'''Name 'b' Load - ROOT 0,1..0,2'''),

('', 2, 3, None, {'norm_get': True}, (None,
r'''(a) is not (b) not in (c)'''),
r'''(a) is not (b)''', r'''
Compare - ROOT 0,0..0,14
  .left Name 'a' Load - 0,1..0,2
  .ops[1]
   0] IsNot - 0,4..0,10
  .comparators[1]
   0] Name 'b' Load - 0,12..0,13
''',
r'''(c)''',
r'''Name 'c' Load - ROOT 0,1..0,2'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, False)}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a # line
# post

# post post

< c
''', r'''
Compare - ROOT 0,0..5,3
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 5,0..5,1
  .comparators[1]
   0] Name 'c' Load - 5,2..5,3
''', r'''

# pre pre

# pre
b
''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, False)}, (None, r'''
a <

# pre pre

# pre
b < # line
# post

# post post

c
'''), r'''
a < # line
# post

# post post

c
''', r'''
Compare - ROOT 0,0..5,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 5,0..5,1
''', r'''

# pre pre

# pre
b
''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, 'line')}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a
# post

# post post

< c
''', r'''
Compare - ROOT 0,0..5,3
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 5,0..5,1
  .comparators[1]
   0] Name 'c' Load - 5,2..5,3
''', r'''

# pre pre

# pre
b # line

''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('block', 'block')}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a

# post post

< c
''', r'''
Compare - ROOT 0,0..4,3
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 4,0..4,1
  .comparators[1]
   0] Name 'c' Load - 4,2..4,3
''', r'''

# pre pre

# pre
b # line
# post

''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('block+', 'block+')}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a
# post post

< c
''', r'''
Compare - ROOT 0,0..3,3
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 3,0..3,1
  .comparators[1]
   0] Name 'c' Load - 3,2..3,3
''', r'''

# pre pre

# pre
b # line
# post


''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('all', 'all')}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a

< c
''', r'''
Compare - ROOT 0,0..2,3
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 2,0..2,1
  .comparators[1]
   0] Name 'c' Load - 2,2..2,3
''', r'''

# pre pre

# pre
b # line
# post

# post post

''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('all+', 'all+')}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a
< c
''', r'''
Compare - ROOT 0,0..1,3
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 1,0..1,1
  .comparators[1]
   0] Name 'c' Load - 1,2..1,3
''', r'''

# pre pre

# pre
b # line
# post

# post post


''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, False), 'op_side': 'right'}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a <

# pre pre

# pre
c
''', r'''
Compare - ROOT 0,0..5,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 5,0..5,1
''', r'''

b # line
# post

# post post


''', r'''
Compare - ROOT 1,0..1,1
  .left Name 'b' Load - 1,0..1,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, False), 'op_side': 'right'}, (None, r'''
a <

# pre pre

# pre
b < # line
# post

# post post

c
'''), r'''
a <

# pre pre

# pre
# line
# post

# post post

c
''', r'''
Compare - ROOT 0,0..10,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 10,0..10,1
''',
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': (False, 'line'), 'op_side': 'right'}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a <

# pre pre

# pre
c
''', r'''
Compare - ROOT 0,0..5,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 5,0..5,1
''', r'''

b # line
# post

# post post


''', r'''
Compare - ROOT 1,0..1,1
  .left Name 'b' Load - 1,0..1,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('block', 'block'), 'op_side': 'right'}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a <

# pre pre

c
''', r'''
Compare - ROOT 0,0..4,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 4,0..4,1
''', r'''

# pre
b # line
# post

# post post


''', r'''
Compare - ROOT 2,0..2,1
  .left Name 'b' Load - 2,0..2,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('block+', 'block+'), 'op_side': 'right'}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a <

# pre pre
c
''', r'''
Compare - ROOT 0,0..3,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 3,0..3,1
''', r'''


# pre
b # line
# post

# post post


''', r'''
Compare - ROOT 3,0..3,1
  .left Name 'b' Load - 3,0..3,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('all', 'all'), 'op_side': 'right'}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a <

c
''', r'''
Compare - ROOT 0,0..2,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 2,0..2,1
''', r'''

# pre pre

# pre
b # line
# post

# post post


''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 1, 2, None, {'_verify_get': False, 'trivia': ('all+', 'all+'), 'op_side': 'right'}, (None, r'''
a <

# pre pre

# pre
b # line
# post

# post post

< c
'''), r'''
a <
c
''', r'''
Compare - ROOT 0,0..1,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 1,0..1,1
''', r'''


# pre pre

# pre
b # line
# post

# post post


''', r'''
Compare - ROOT 5,0..5,1
  .left Name 'b' Load - 5,0..5,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None,
r'''a is not b'''),
r'''a''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
''',
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None, r'''
a
# pre-op
is not b
'''), r'''
a

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
''', r'''

# pre-op
b
''', r'''
Compare - ROOT 2,0..2,1
  .left Name 'b' Load - 2,0..2,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None, r'''
a is not
# pre-val
b
'''),
r'''a''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
''', r'''
# pre-val
b
''', r'''
Compare - ROOT 1,0..1,1
  .left Name 'b' Load - 1,0..1,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None, r'''
a
# pre-op
is not
# pre-val
b
'''), r'''
a

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
''', r'''

# pre-op
# pre-val
b
''', r'''
Compare - ROOT 3,0..3,1
  .left Name 'b' Load - 3,0..3,1
'''),

('', 1, 2, None, {'_verify': False, 'trivia': ('all', False), 'op_side': 'left'}, (None, r'''
a
# pre-op
is not \
# pre-val
b
'''), r'''
a

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
''', r'''

# pre-op
 \
# pre-val
b
''', r'''
Compare - ROOT 4,0..4,1
  .left Name 'b' Load - 4,0..4,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None,
r'''a is not b'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''',
r'''a''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a is not
# post-op
b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a
# post-op

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a
# post-val
is not b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a
# post-val

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a
# post-val
is not
# post-op
b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a
# post-val
# post-op

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a
# post-val
is not \
# post-op
b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a
# post-val
 \
# post-op

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a is not  # line
# post-op
b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a  # line
# post-op

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a  # line
# post-val
is not b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a  # line
# post-val

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a  # line
# post-val
is not
# post-op
b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a  # line
# post-val
# post-op

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False, 'trivia': (False, 'all'), 'op_side': 'right'}, (None, r'''
a  # line
# post-val
is not \
# post-op
b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a  # line
# post-val
 \
# post-op

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, None, {'_verify': False}, (None, r'''
a
is
not
b
'''),
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
''', r'''
a

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
'''),

('', 1, 2, None, {'_verify': False}, (None, r'''
a
is
not
b
'''), r'''
a

''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'a' Load - 0,0..0,1
''', r'''

b
''', r'''
Compare - ROOT 1,0..1,1
  .left Name 'b' Load - 1,0..1,1
'''),
],

'Call_args': [  # ................................................................................

('', 0, 0, 'args', {}, (None,
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

('', 0, 'end', 'args', {}, (None,
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

('', 0, 1, 'args', {}, (None,
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

('', 1, 2, 'args', {}, (None,
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

('', 0, 'end', 'args', {}, (None,
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

('', 0, 1, 'args', {}, (None,
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

('', 1, 2, 'args', {}, (None,
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

('', 0, 'end', 'args', {}, (None,
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

('', 0, 1, 'args', {}, (None,
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

('', 1, 2, 'args', {}, (None,
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

('', 1, 2, 'args', {}, (None, r'''
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

('', 0, 3, 'args', {}, (None, r'''
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

('', 0, 3, 'args', {}, (None, r'''
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

('', 1, 2, 'args', {}, (None, r'''
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

('', 0, 3, 'args', {}, (None, r'''
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

('', 0, 3, 'args', {}, (None, r'''
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

('', 0, 2, 'args', {}, (None,
r'''call(a, b=c, *d)'''),
r'''**NodeError("cannot get Call.args slice because it includes keywords, try the '_args' field")**'''),

('', 1, 2, 'args', {}, (None,
r'''call(a, b=c, *d)'''),
r'''**NodeError("cannot get Call.args slice because it includes keywords, try the '_args' field")**'''),

('', 0, 1, 'args', {}, (None,
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

('', 1, 2, 'args', {}, (None,
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

('', 1, 2, 'args', {}, (None,
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

('', 0, 1, 'args', {}, (None,
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

('', 0, 'end', 'args', {}, (None,
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

('', 0, 'end', 'args', {'pars_arglike': False, '_verify_get': False}, (None,
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

('', 0, 'end', 'args', {'pars': False, '_verify_get': False}, (None,
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
],

'Call_keywords': [  # ................................................................................

('', 1, 'end', 'keywords', {}, (None,
r'''call(a, b=c, *d, **e)'''),
r'''call(a, b=c, *d)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'd' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'b'
     .value Name 'c' Load - 0,10..0,11
''',
r'''**e''', r'''
_arglikes - ROOT 0,0..0,3
  .arglikes[1]
   0] keyword - 0,0..0,3
     .value Name 'e' Load - 0,2..0,3
'''),

('', -1, 'end', 'keywords', {}, (None,
r'''call(a, b=c, *d, **e)'''),
r'''call(a, b=c, *d)''', r'''
Call - ROOT 0,0..0,16
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'd' Load - 0,14..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,8..0,11
     .arg 'b'
     .value Name 'c' Load - 0,10..0,11
''',
r'''**e''', r'''
_arglikes - ROOT 0,0..0,3
  .arglikes[1]
   0] keyword - 0,0..0,3
     .value Name 'e' Load - 0,2..0,3
'''),

('', -2, 'end', 'keywords', {}, (None,
r'''call(a, b=c, *d, **e)'''),
r'''**NodeError("cannot get Call.keywords slice because it includes args, try the '_args' field")**'''),
],

'Call__args': [  # ................................................................................

('', 0, 4, '_args', {}, (None,
r'''call(a, *not b, c, e=f, *g, **h, i=j)'''),
r'''call(*g, **h, i=j)''', r'''
Call - ROOT 0,0..0,18
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,5..0,7
     .value Name 'g' Load - 0,6..0,7
     .ctx Load
  .keywords[2]
   0] keyword - 0,9..0,12
     .value Name 'h' Load - 0,11..0,12
   1] keyword - 0,14..0,17
     .arg 'i'
     .value Name 'j' Load - 0,16..0,17
''',
r'''a, *not b, c, e=f''', r'''
_arglikes - ROOT 0,0..0,17
  .arglikes[4]
   0] Name 'a' Load - 0,0..0,1
   1] Starred - 0,3..0,9
     .value UnaryOp - 0,4..0,9
       .op Not - 0,4..0,7
       .operand Name 'b' Load - 0,8..0,9
     .ctx Load
   2] Name 'c' Load - 0,11..0,12
   3] keyword - 0,14..0,17
     .arg 'e'
     .value Name 'f' Load - 0,16..0,17
'''),

('', 1, 5, '_args', {}, (None,
r'''call(a, *not b, c, e=f, *g, **h, i=j)'''),
r'''call(a, **h, i=j)''', r'''
Call - ROOT 0,0..0,17
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'a' Load - 0,5..0,6
  .keywords[2]
   0] keyword - 0,8..0,11
     .value Name 'h' Load - 0,10..0,11
   1] keyword - 0,13..0,16
     .arg 'i'
     .value Name 'j' Load - 0,15..0,16
''',
r'''*not b, c, e=f, *g''', r'''
_arglikes - ROOT 0,0..0,18
  .arglikes[4]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'b' Load - 0,5..0,6
     .ctx Load
   1] Name 'c' Load - 0,8..0,9
   2] keyword - 0,11..0,14
     .arg 'e'
     .value Name 'f' Load - 0,13..0,14
   3] Starred - 0,16..0,18
     .value Name 'g' Load - 0,17..0,18
     .ctx Load
'''),

('', 2, 6, '_args', {}, (None,
r'''call(a, *not b, c, e=f, *g, **h, i=j)'''),
r'''call(a, *not b, i=j)''', r'''
Call - ROOT 0,0..0,20
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,8..0,14
     .value UnaryOp - 0,9..0,14
       .op Not - 0,9..0,12
       .operand Name 'b' Load - 0,13..0,14
     .ctx Load
  .keywords[1]
   0] keyword - 0,16..0,19
     .arg 'i'
     .value Name 'j' Load - 0,18..0,19
''',
r'''c, e=f, *g, **h''', r'''
_arglikes - ROOT 0,0..0,15
  .arglikes[4]
   0] Name 'c' Load - 0,0..0,1
   1] keyword - 0,3..0,6
     .arg 'e'
     .value Name 'f' Load - 0,5..0,6
   2] Starred - 0,8..0,10
     .value Name 'g' Load - 0,9..0,10
     .ctx Load
   3] keyword - 0,12..0,15
     .value Name 'h' Load - 0,14..0,15
'''),

('', 3, 7, '_args', {}, (None,
r'''call(a, *not b, c, e=f, *g, **h, i=j)'''),
r'''call(a, *not b, c)''', r'''
Call - ROOT 0,0..0,18
  .func Name 'call' Load - 0,0..0,4
  .args[3]
   0] Name 'a' Load - 0,5..0,6
   1] Starred - 0,8..0,14
     .value UnaryOp - 0,9..0,14
       .op Not - 0,9..0,12
       .operand Name 'b' Load - 0,13..0,14
     .ctx Load
   2] Name 'c' Load - 0,16..0,17
''',
r'''e=f, *g, **h, i=j''', r'''
_arglikes - ROOT 0,0..0,17
  .arglikes[4]
   0] keyword - 0,0..0,3
     .arg 'e'
     .value Name 'f' Load - 0,2..0,3
   1] Starred - 0,5..0,7
     .value Name 'g' Load - 0,6..0,7
     .ctx Load
   2] keyword - 0,9..0,12
     .value Name 'h' Load - 0,11..0,12
   3] keyword - 0,14..0,17
     .arg 'i'
     .value Name 'j' Load - 0,16..0,17
'''),
],

'decorator_list': [  # ................................................................................

('', 0, 1, 'decorator_list', {}, (None, r'''
@a
@ ( b )
@c()
class cls: pass
'''), r'''
@ ( b )
@c()
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'b' Load - 0,4..0,5
   1] Call - 1,1..1,4
     .func Name 'c' Load - 1,1..1,2
''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, 'decorator_list', {}, (None, r'''
@a
@ ( b )
@c()
class cls: pass
'''), r'''
@a
@c()
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Call - 1,1..1,4
     .func Name 'c' Load - 1,1..1,2
''',
r'''@ ( b )''', r'''
_decorator_list - ROOT 0,0..0,7
  .decorator_list[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', 2, 3, 'decorator_list', {}, (None, r'''
@a
@ ( b )
@c()
class cls: pass
'''), r'''
@a
@ ( b )
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,4..1,5
''',
r'''@c()''', r'''
_decorator_list - ROOT 0,0..0,4
  .decorator_list[1]
   0] Call - 0,1..0,4
     .func Name 'c' Load - 0,1..0,2
'''),

('', 0, 2, 'decorator_list', {}, (None, r'''
@a
@ ( b )
@c()
class cls: pass
'''), r'''
@c()
class cls: pass
''', r'''
ClassDef - ROOT 1,0..1,15
  .name 'cls'
  .body[1]
   0] Pass - 1,11..1,15
  .decorator_list[1]
   0] Call - 0,1..0,4
     .func Name 'c' Load - 0,1..0,2
''', r'''
@a
@ ( b )
''', r'''
_decorator_list - ROOT 0,0..1,7
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,4..1,5
'''),

('', 1, 3, 'decorator_list', {}, (None, r'''
@a
@ ( b )
@c()
class cls: pass
'''), r'''
@a
class cls: pass
''', r'''
ClassDef - ROOT 1,0..1,15
  .name 'cls'
  .body[1]
   0] Pass - 1,11..1,15
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''', r'''
@ ( b )
@c()
''', r'''
_decorator_list - ROOT 0,0..1,4
  .decorator_list[2]
   0] Name 'b' Load - 0,4..0,5
   1] Call - 1,1..1,4
     .func Name 'c' Load - 1,1..1,2
'''),

('', 0, 3, 'decorator_list', {}, (None, r'''
@a
@ ( b )
@c()
class cls: pass
'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''', r'''
@a
@ ( b )
@c()
''', r'''
_decorator_list - ROOT 0,0..2,4
  .decorator_list[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,4..1,5
   2] Call - 2,1..2,4
     .func Name 'c' Load - 2,1..2,2
'''),

('', 1, 2, 'decorator_list', {'trivia': ('all+', 'all+')}, (None, r'''
@a

# pre
@ ( b )  # line
# post

@c()
class cls: pass
'''), r'''
@a
@c()
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Call - 1,1..1,4
     .func Name 'c' Load - 1,1..1,2
''', r'''

# pre
@ ( b )  # line
# post

''', r'''
_decorator_list - ROOT 0,0..4,0
  .decorator_list[1]
   0] Name 'b' Load - 2,4..2,5
'''),

('', 1, 2, 'decorator_list', {'trivia': ('all+', 'all+')}, (None, r'''
@a


# pre
@ ( b )  # line
# post


@c()
class cls: pass
'''), r'''
@a
@c()
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Call - 1,1..1,4
     .func Name 'c' Load - 1,1..1,2
''', r'''


# pre
@ ( b )  # line
# post


''', r'''
_decorator_list - ROOT 0,0..6,0
  .decorator_list[1]
   0] Name 'b' Load - 3,4..3,5
'''),

('', 0, 2, 'decorator_list', {}, (None, r'''
\
@a
\
@ ( b )
\
@c()
\
class cls: pass
'''), r'''
\
\
@c()
\
class cls: pass
''', r'''
ClassDef - ROOT 4,0..4,15
  .name 'cls'
  .body[1]
   0] Pass - 4,11..4,15
  .decorator_list[1]
   0] Call - 2,1..2,4
     .func Name 'c' Load - 2,1..2,2
''', r'''
@a
\
@ ( b )
''', r'''
_decorator_list - ROOT 0,0..2,7
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 2,4..2,5
'''),

('body[0]', 0, 1, 'decorator_list', {}, (None, r'''
if 1:
  @a
  @ ( b )
  @c()
  class cls: pass
'''), r'''
if 1:
  @ ( b )
  @c()
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
      0] Name 'b' Load - 1,6..1,7
      1] Call - 2,3..2,6
        .func Name 'c' Load - 2,3..2,4
''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('body[0]', 1, 2, 'decorator_list', {}, (None, r'''
if 1:
  @a
  @ ( b )
  @c()
  class cls: pass
'''), r'''
if 1:
  @a
  @c()
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
      1] Call - 2,3..2,6
        .func Name 'c' Load - 2,3..2,4
''',
r'''@ ( b )''', r'''
_decorator_list - ROOT 0,0..0,7
  .decorator_list[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('body[0]', 2, 3, 'decorator_list', {}, (None, r'''
if 1:
  @a
  @ ( b )
  @c()
  class cls: pass
'''), r'''
if 1:
  @a
  @ ( b )
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
      1] Name 'b' Load - 2,6..2,7
''',
r'''@c()''', r'''
_decorator_list - ROOT 0,0..0,4
  .decorator_list[1]
   0] Call - 0,1..0,4
     .func Name 'c' Load - 0,1..0,2
'''),

('body[0]', 0, 2, 'decorator_list', {}, (None, r'''
if 1:
  @a
  @ ( b )
  @c()
  class cls: pass
'''), r'''
if 1:
  @c()
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
      0] Call - 1,3..1,6
        .func Name 'c' Load - 1,3..1,4
''', r'''
@a
@ ( b )
''', r'''
_decorator_list - ROOT 0,0..1,7
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,4..1,5
'''),

('body[0]', 1, 3, 'decorator_list', {}, (None, r'''
if 1:
  @a
  @ ( b )
  @c()
  class cls: pass
'''), r'''
if 1:
  @a
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
      0] Name 'a' Load - 1,3..1,4
''', r'''
@ ( b )
@c()
''', r'''
_decorator_list - ROOT 0,0..1,4
  .decorator_list[2]
   0] Name 'b' Load - 0,4..0,5
   1] Call - 1,1..1,4
     .func Name 'c' Load - 1,1..1,2
'''),

('body[0]', 0, 3, 'decorator_list', {}, (None, r'''
if 1:
  @a
  @ ( b )
  @c()
  class cls: pass
'''), r'''
if 1:
  class cls: pass
''', r'''
If - ROOT 0,0..1,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 1,2..1,17
     .name 'cls'
     .body[1]
      0] Pass - 1,13..1,17
''', r'''
@a
@ ( b )
@c()
''', r'''
_decorator_list - ROOT 0,0..2,4
  .decorator_list[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,4..1,5
   2] Call - 2,1..2,4
     .func Name 'c' Load - 2,1..2,2
'''),

('body[0]', 1, 2, 'decorator_list', {'trivia': ('all+', 'all+')}, (None, r'''
if 1:
  @a

  # pre
  @ ( b )  # line
  # post

  @c()
  class cls: pass
'''), r'''
if 1:
  @a
  @c()
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
      1] Call - 2,3..2,6
        .func Name 'c' Load - 2,3..2,4
''', r'''

# pre
@ ( b )  # line
# post

''', r'''
_decorator_list - ROOT 0,0..4,0
  .decorator_list[1]
   0] Name 'b' Load - 2,4..2,5
'''),

('body[0]', 1, 2, 'decorator_list', {'trivia': ('all+', 'all+')}, (None, r'''
if 1:
  @a


  # pre
  @ ( b )  # line
  # post


  @c()
  class cls: pass
'''), r'''
if 1:
  @a
  @c()
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
      1] Call - 2,3..2,6
        .func Name 'c' Load - 2,3..2,4
''', r'''


# pre
@ ( b )  # line
# post


''', r'''
_decorator_list - ROOT 0,0..6,0
  .decorator_list[1]
   0] Name 'b' Load - 3,4..3,5
'''),

('body[0]', 0, 2, 'decorator_list', {}, (None, r'''
if 1:
\
  @a
\
  @ ( b )
\
  @c()
\
  class cls: pass
'''), r'''
if 1:
\
\
  @c()
\
  class cls: pass
''', r'''
If - ROOT 0,0..5,17
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 5,2..5,17
     .name 'cls'
     .body[1]
      0] Pass - 5,13..5,17
     .decorator_list[1]
      0] Call - 3,3..3,6
        .func Name 'c' Load - 3,3..3,4
''', r'''
@a
\
@ ( b )
''', r'''
_decorator_list - ROOT 0,0..2,7
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 2,4..2,5
'''),

('body[0]', 0, 2, 'decorator_list', {}, (None, r'''
if 1:
  \
@a
  \
@ ( b )
  \
@c()
  \
class cls: pass
'''), r'''
if 1:
  \
  \
@c()
  \
class cls: pass
''', r'''
If - ROOT 0,0..5,15
  .test Constant 1 - 0,3..0,4
  .body[1]
   0] ClassDef - 5,0..5,15
     .name 'cls'
     .body[1]
      0] Pass - 5,11..5,15
     .decorator_list[1]
      0] Call - 3,1..3,4
        .func Name 'c' Load - 3,1..3,2
''', r'''
@a
\
@ ( b )
''', r'''
_decorator_list - ROOT 0,0..2,7
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 2,4..2,5
'''),

('', 0, 'end', 'decorator_list', {}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''),
r'''def f(): pass''', r'''
FunctionDef - ROOT 0,0..0,13
  .name 'f'
  .body[1]
   0] Pass - 0,9..0,13
''', r'''
@a

# pre
@b  # line

# post

@c
''', r'''
_decorator_list - ROOT 0,0..7,2
  .decorator_list[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 3,1..3,2
   2] Name 'c' Load - 7,1..7,2
'''),

('', 0, 1, 'decorator_list', {}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), r'''

# pre
@b  # line

# post

@c
def f(): pass
''', r'''
FunctionDef - ROOT 7,0..7,13
  .name 'f'
  .body[1]
   0] Pass - 7,9..7,13
  .decorator_list[2]
   0] Name 'b' Load - 2,1..2,2
   1] Name 'c' Load - 6,1..6,2
''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 1, 2, 'decorator_list', {}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), r'''
@a


# post

@c
def f(): pass
''', r'''
FunctionDef - ROOT 6,0..6,13
  .name 'f'
  .body[1]
   0] Pass - 6,9..6,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'c' Load - 5,1..5,2
''', r'''
# pre
@b  # line
''', r'''
_decorator_list - ROOT 0,0..1,10
  .decorator_list[1]
   0] Name 'b' Load - 1,1..1,2
'''),

('', 1, 2, 'decorator_list', {'trivia': ('all+', 'all+')}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), r'''
@a
@c
def f(): pass
''', r'''
FunctionDef - ROOT 2,0..2,13
  .name 'f'
  .body[1]
   0] Pass - 2,9..2,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'c' Load - 1,1..1,2
''', r'''

# pre
@b  # line

# post

''', r'''
_decorator_list - ROOT 0,0..5,0
  .decorator_list[1]
   0] Name 'b' Load - 2,1..2,2
'''),

('', 2, 3, 'decorator_list', {}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), r'''
@a

# pre
@b  # line

# post

def f(): pass
''', r'''
FunctionDef - ROOT 7,0..7,13
  .name 'f'
  .body[1]
   0] Pass - 7,9..7,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 3,1..3,2
''',
r'''@c''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'c' Load - 0,1..0,2
'''),

('', 2, 3, 'decorator_list', {'trivia': False}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), r'''
@a

# pre
@b  # line

# post

def f(): pass
''', r'''
FunctionDef - ROOT 7,0..7,13
  .name 'f'
  .body[1]
   0] Pass - 7,9..7,13
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 3,1..3,2
''',
r'''@c''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'c' Load - 0,1..0,2
'''),

('', 0, 2, 'decorator_list', {'trivia': (None, 'all+')}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), r'''
@c
def f(): pass
''', r'''
FunctionDef - ROOT 1,0..1,13
  .name 'f'
  .body[1]
   0] Pass - 1,9..1,13
  .decorator_list[1]
   0] Name 'c' Load - 0,1..0,2
''', r'''
@a

# pre
@b  # line

# post

''', r'''
_decorator_list - ROOT 0,0..6,0
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 3,1..3,2
'''),

('', 1, 3, 'decorator_list', {'trivia': 'all+'}, (None, r'''
@a

# pre
@b  # line

# post

@c
def f(): pass
'''), r'''
@a
def f(): pass
''', r'''
FunctionDef - ROOT 1,0..1,13
  .name 'f'
  .body[1]
   0] Pass - 1,9..1,13
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''', r'''

# pre
@b  # line

# post

@c
''', r'''
_decorator_list - ROOT 0,0..6,2
  .decorator_list[2]
   0] Name 'b' Load - 2,1..2,2
   1] Name 'c' Load - 6,1..6,2
'''),
],

'decorator_list_newlines': [  # ................................................................................

('', 0, 'end', None, {}, ('_decorator_list',
r'''@a'''),
r'''''',
r'''_decorator_list - ROOT 0,0..0,0''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 2, None, {}, ('_decorator_list', r'''
@a
@b
'''),
r'''''',
r'''_decorator_list - ROOT 0,0..0,0''', r'''
@a
@b
''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,1..1,2
'''),

('', 1, 2, None, {}, ('_decorator_list', r'''
@a
@b
'''),
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''',
r'''@b''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'b' Load - 0,1..0,2
'''),

('', 1, 2, None, {}, ('_decorator_list', r'''
@a

@b
'''), r'''
@a

''', r'''
_decorator_list - ROOT 0,0..1,0
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''',
r'''@b''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'b' Load - 0,1..0,2
'''),

('', 1, 2, None, {'trivia': '-'}, ('_decorator_list', r'''
@a

@b
'''),
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''',
r'''@b''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'b' Load - 0,1..0,2
'''),

('', 1, 2, None, {}, ('_decorator_list', r'''
@a
# comment
@b
'''),
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''', r'''
# comment
@b
''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[1]
   0] Name 'b' Load - 1,1..1,2
'''),

('', 1, 2, None, {'trivia': False}, ('_decorator_list', r'''
@a
# comment
@b
'''), r'''
@a
# comment
''', r'''
_decorator_list - ROOT 0,0..1,9
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''',
r'''@b''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'b' Load - 0,1..0,2
'''),

('', 1, 2, None, {}, ('_decorator_list', r'''
@a
# comment

@b
'''), r'''
@a
# comment

''', r'''
_decorator_list - ROOT 0,0..2,0
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''',
r'''@b''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'b' Load - 0,1..0,2
'''),

('', 1, 2, None, {'trivia': '-'}, ('_decorator_list', r'''
@a
# comment

@b
'''), r'''
@a
# comment
''', r'''
_decorator_list - ROOT 0,0..1,9
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
''',
r'''@b''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'b' Load - 0,1..0,2
'''),

('body[1]', 0, 1, 'decorator_list', {'trivia': '-'}, (None, r'''
pass

@a
class cls: pass
'''), r'''
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
''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('body[1]', 0, 1, 'decorator_list', {'trivia': '-'}, (None, r'''
if 1:
  pass

  @a
  class cls: pass
'''), r'''
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
''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 1, 'decorator_list', {}, (None, r'''

@a
@b
class cls: pass
'''), r'''

@b
class cls: pass
''', r'''
ClassDef - ROOT 2,0..2,15
  .name 'cls'
  .body[1]
   0] Pass - 2,11..2,15
  .decorator_list[1]
   0] Name 'b' Load - 1,1..1,2
''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 2, 'decorator_list', {}, (None, r'''

@a
@b
class cls: pass
'''), r'''

class cls: pass
''', r'''
ClassDef - ROOT 1,0..1,15
  .name 'cls'
  .body[1]
   0] Pass - 1,11..1,15
''', r'''
@a
@b
''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,1..1,2
'''),

('body[0]', 0, 1, 'decorator_list', {}, (None, r'''
if 1:

  @a
  @b
  class cls: pass
'''), r'''
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
''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('body[0]', 0, 2, 'decorator_list', {}, (None, r'''
if 1:

  @a
  @b
  class cls: pass
'''), r'''
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
''', r'''
@a
@b
''', r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,1..1,2
'''),
],

'generators': [  # ................................................................................

('', 0, 2, 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''[_ for c in c]''', r'''
ListComp - ROOT 0,0..0,14
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name 'c' Store - 0,7..0,8
     .iter Name 'c' Load - 0,12..0,13
     .is_async 0
''',
r'''for a in a for b in b''', r'''
_comprehensions - ROOT 0,0..0,21
  .generators[2]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'b' Store - 0,15..0,16
     .iter Name 'b' Load - 0,20..0,21
     .is_async 0
'''),

('', 1, 2, 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''[_ for a in a for c in c]''', r'''
ListComp - ROOT 0,0..0,25
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'c' Store - 0,18..0,19
     .iter Name 'c' Load - 0,23..0,24
     .is_async 0
''',
r'''for b in b''', r'''
_comprehensions - ROOT 0,0..0,10
  .generators[1]
   0] comprehension - 0,0..0,10
     .target Name 'b' Store - 0,4..0,5
     .iter Name 'b' Load - 0,9..0,10
     .is_async 0
'''),

('', 1, 3, 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''[_ for a in a]''', r'''
ListComp - ROOT 0,0..0,14
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
''',
r'''for b in b for c in c''', r'''
_comprehensions - ROOT 0,0..0,21
  .generators[2]
   0] comprehension - 0,0..0,10
     .target Name 'b' Store - 0,4..0,5
     .iter Name 'b' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'c' Store - 0,15..0,16
     .iter Name 'c' Load - 0,20..0,21
     .is_async 0
'''),

('', 2, 3, 'generators', {}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''[_ for a in a for b in b]''', r'''
ListComp - ROOT 0,0..0,25
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'b' Store - 0,18..0,19
     .iter Name 'b' Load - 0,23..0,24
     .is_async 0
''',
r'''for c in c''', r'''
_comprehensions - ROOT 0,0..0,10
  .generators[1]
   0] comprehension - 0,0..0,10
     .target Name 'c' Store - 0,4..0,5
     .iter Name 'c' Load - 0,9..0,10
     .is_async 0
'''),

('', 3, 3, 'generators', {'_verify': False}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''[_ for a in a for b in b for c in c]''', r'''
ListComp - ROOT 0,0..0,36
  .elt Name '_' Load - 0,1..0,2
  .generators[3]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name 'a' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,14..0,24
     .target Name 'b' Store - 0,18..0,19
     .iter Name 'b' Load - 0,23..0,24
     .is_async 0
   2] comprehension - 0,25..0,35
     .target Name 'c' Store - 0,29..0,30
     .iter Name 'c' Load - 0,34..0,35
     .is_async 0
''',
r'''''',
r'''_comprehensions - ROOT 0,0..0,0'''),

('', 0, 2, 'generators', {}, (None, r'''
[_
for a in a \
for b in b \
for c in c \
]
'''), r'''
[_
for c in c \
]
''', r'''
ListComp - ROOT 0,0..2,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 1,0..1,10
     .target Name 'c' Store - 1,4..1,5
     .iter Name 'c' Load - 1,9..1,10
     .is_async 0
''', r'''

for a in a \
for b in b \

''', r'''
_comprehensions - ROOT 0,0..3,0
  .generators[2]
   0] comprehension - 1,0..1,10
     .target Name 'a' Store - 1,4..1,5
     .iter Name 'a' Load - 1,9..1,10
     .is_async 0
   1] comprehension - 2,0..2,10
     .target Name 'b' Store - 2,4..2,5
     .iter Name 'b' Load - 2,9..2,10
     .is_async 0
'''),

('', 1, 2, 'generators', {}, (None, r'''
[_
for a in a \
for b in b \
for c in c \
]
'''), r'''
[_
for a in a \
for c in c \
]
''', r'''
ListComp - ROOT 0,0..3,1
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 1,0..1,10
     .target Name 'a' Store - 1,4..1,5
     .iter Name 'a' Load - 1,9..1,10
     .is_async 0
   1] comprehension - 2,0..2,10
     .target Name 'c' Store - 2,4..2,5
     .iter Name 'c' Load - 2,9..2,10
     .is_async 0
''', r'''

for b in b \

''', r'''
_comprehensions - ROOT 0,0..2,0
  .generators[1]
   0] comprehension - 1,0..1,10
     .target Name 'b' Store - 1,4..1,5
     .iter Name 'b' Load - 1,9..1,10
     .is_async 0
'''),

('', 1, 3, 'generators', {}, (None, r'''
[_
for a in a \
for b in b \
for c in c \
]
'''), r'''
[_
for a in a \
]
''', r'''
ListComp - ROOT 0,0..2,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 1,0..1,10
     .target Name 'a' Store - 1,4..1,5
     .iter Name 'a' Load - 1,9..1,10
     .is_async 0
''', r'''

for b in b \
for c in c \

''', r'''
_comprehensions - ROOT 0,0..3,0
  .generators[2]
   0] comprehension - 1,0..1,10
     .target Name 'b' Store - 1,4..1,5
     .iter Name 'b' Load - 1,9..1,10
     .is_async 0
   1] comprehension - 2,0..2,10
     .target Name 'c' Store - 2,4..2,5
     .iter Name 'c' Load - 2,9..2,10
     .is_async 0
'''),

('', 2, 3, 'generators', {}, (None, r'''
[_
for a in a \
for b in b \
for c in c \
]
'''), r'''
[_
for a in a \
for b in b \
]
''', r'''
ListComp - ROOT 0,0..3,1
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 1,0..1,10
     .target Name 'a' Store - 1,4..1,5
     .iter Name 'a' Load - 1,9..1,10
     .is_async 0
   1] comprehension - 2,0..2,10
     .target Name 'b' Store - 2,4..2,5
     .iter Name 'b' Load - 2,9..2,10
     .is_async 0
''', r'''

for c in c \

''', r'''
_comprehensions - ROOT 0,0..2,0
  .generators[1]
   0] comprehension - 1,0..1,10
     .target Name 'c' Store - 1,4..1,5
     .iter Name 'c' Load - 1,9..1,10
     .is_async 0
'''),

('', 3, 3, 'generators', {}, (None, r'''
[_
for a in a \
for b in b \
for c in c \
]
'''), r'''
[_
for a in a \
for b in b \
for c in c \
]
''', r'''
ListComp - ROOT 0,0..4,1
  .elt Name '_' Load - 0,1..0,2
  .generators[3]
   0] comprehension - 1,0..1,10
     .target Name 'a' Store - 1,4..1,5
     .iter Name 'a' Load - 1,9..1,10
     .is_async 0
   1] comprehension - 2,0..2,10
     .target Name 'b' Store - 2,4..2,5
     .iter Name 'b' Load - 2,9..2,10
     .is_async 0
   2] comprehension - 3,0..3,10
     .target Name 'c' Store - 3,4..3,5
     .iter Name 'c' Load - 3,9..3,10
     .is_async 0
''',
r'''''',
r'''_comprehensions - ROOT 0,0..0,0'''),

('', 0, 2, None, {}, ('_comprehensions', r'''
for a in a \
for b in b \
for c in c \

'''), r'''
for c in c \

''', r'''
_comprehensions - ROOT 0,0..1,0
  .generators[1]
   0] comprehension - 0,0..0,10
     .target Name 'c' Store - 0,4..0,5
     .iter Name 'c' Load - 0,9..0,10
     .is_async 0
''', r'''
for a in a \
for b in b \

''', r'''
_comprehensions - ROOT 0,0..2,0
  .generators[2]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 1,0..1,10
     .target Name 'b' Store - 1,4..1,5
     .iter Name 'b' Load - 1,9..1,10
     .is_async 0
'''),

('', 1, 2, None, {}, ('_comprehensions', r'''
for a in a \
for b in b \
for c in c \

'''), r'''
for a in a \
for c in c \

''', r'''
_comprehensions - ROOT 0,0..2,0
  .generators[2]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 1,0..1,10
     .target Name 'c' Store - 1,4..1,5
     .iter Name 'c' Load - 1,9..1,10
     .is_async 0
''', r'''

for b in b \

''', r'''
_comprehensions - ROOT 0,0..2,0
  .generators[1]
   0] comprehension - 1,0..1,10
     .target Name 'b' Store - 1,4..1,5
     .iter Name 'b' Load - 1,9..1,10
     .is_async 0
'''),

('', 1, 3, None, {}, ('_comprehensions', r'''
for a in a \
for b in b \
for c in c \

'''), r'''
for a in a \

''', r'''
_comprehensions - ROOT 0,0..1,0
  .generators[1]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
''', r'''

for b in b \
for c in c \

''', r'''
_comprehensions - ROOT 0,0..3,0
  .generators[2]
   0] comprehension - 1,0..1,10
     .target Name 'b' Store - 1,4..1,5
     .iter Name 'b' Load - 1,9..1,10
     .is_async 0
   1] comprehension - 2,0..2,10
     .target Name 'c' Store - 2,4..2,5
     .iter Name 'c' Load - 2,9..2,10
     .is_async 0
'''),

('', 2, 3, None, {}, ('_comprehensions', r'''
for a in a \
for b in b \
for c in c \

'''), r'''
for a in a \
for b in b \

''', r'''
_comprehensions - ROOT 0,0..2,0
  .generators[2]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 1,0..1,10
     .target Name 'b' Store - 1,4..1,5
     .iter Name 'b' Load - 1,9..1,10
     .is_async 0
''', r'''

for c in c \

''', r'''
_comprehensions - ROOT 0,0..2,0
  .generators[1]
   0] comprehension - 1,0..1,10
     .target Name 'c' Store - 1,4..1,5
     .iter Name 'c' Load - 1,9..1,10
     .is_async 0
'''),

('', 3, 3, None, {}, ('_comprehensions', r'''
for a in a \
for b in b \
for c in c \

'''), r'''
for a in a \
for b in b \
for c in c \

''', r'''
_comprehensions - ROOT 0,0..3,0
  .generators[3]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 1,0..1,10
     .target Name 'b' Store - 1,4..1,5
     .iter Name 'b' Load - 1,9..1,10
     .is_async 0
   2] comprehension - 2,0..2,10
     .target Name 'c' Store - 2,4..2,5
     .iter Name 'c' Load - 2,9..2,10
     .is_async 0
''',
r'''''',
r'''_comprehensions - ROOT 0,0..0,0'''),

('', 0, 3, 'generators', {'norm': True}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''**ValueError('cannot cut all ListComp.generators without norm_self=False')**''',
r'''for a in a for b in b for c in c''', r'''
_comprehensions - ROOT 0,0..0,32
  .generators[3]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'b' Store - 0,15..0,16
     .iter Name 'b' Load - 0,20..0,21
     .is_async 0
   2] comprehension - 0,22..0,32
     .target Name 'c' Store - 0,26..0,27
     .iter Name 'c' Load - 0,31..0,32
     .is_async 0
'''),

('', 0, 3, 'generators', {'norm_self': False, '_verify_self': False}, (None,
r'''[_ for a in a for b in b for c in c]'''),
r'''[_]''', r'''
ListComp - ROOT 0,0..0,3
  .elt Name '_' Load - 0,1..0,2
''',
r'''for a in a for b in b for c in c''', r'''
_comprehensions - ROOT 0,0..0,32
  .generators[3]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'a' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,21
     .target Name 'b' Store - 0,15..0,16
     .iter Name 'b' Load - 0,20..0,21
     .is_async 0
   2] comprehension - 0,22..0,32
     .target Name 'c' Store - 0,26..0,27
     .iter Name 'c' Load - 0,31..0,32
     .is_async 0
'''),
],

'comprehension_ifs': [  # ................................................................................

('generators[0]', 0, 2, 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''),
r'''[_ for _ in _ if c]''', r'''
ListComp - ROOT 0,0..0,19
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,18
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'c' Load - 0,17..0,18
     .is_async 0
''',
r'''if a if b''', r'''
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[2]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'b' Load - 0,8..0,9
'''),

('generators[0]', 1, 2, 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''),
r'''[_ for _ in _ if a if c]''', r'''
ListComp - ROOT 0,0..0,24
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,23
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 0,17..0,18
      1] Name 'c' Load - 0,22..0,23
     .is_async 0
''',
r'''if b''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'b' Load - 0,3..0,4
'''),

('generators[0]', 1, 3, 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''),
r'''[_ for _ in _ if a]''', r'''
ListComp - ROOT 0,0..0,19
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,18
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'a' Load - 0,17..0,18
     .is_async 0
''',
r'''if b if c''', r'''
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[2]
   0] Name 'b' Load - 0,3..0,4
   1] Name 'c' Load - 0,8..0,9
'''),

('generators[0]', 2, 3, 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c]'''),
r'''[_ for _ in _ if a if b]''', r'''
ListComp - ROOT 0,0..0,24
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,23
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 0,17..0,18
      1] Name 'b' Load - 0,22..0,23
     .is_async 0
''',
r'''if c''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'c' Load - 0,3..0,4
'''),

('generators[0]', 3, 3, 'ifs', {'_verify': False}, (None,
r'''[_ for _ in _ if a if b if c]'''),
r'''[_ for _ in _ if a if b if c]''', r'''
ListComp - ROOT 0,0..0,29
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,28
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[3]
      0] Name 'a' Load - 0,17..0,18
      1] Name 'b' Load - 0,22..0,23
      2] Name 'c' Load - 0,27..0,28
     .is_async 0
''',
r'''''',
r'''_comprehension_ifs - ROOT 0,0..0,0'''),

('generators[0]', 0, 2, 'ifs', {}, (None, r'''
[_ for _ in _
if a \
if b \
if c \
]
'''), r'''
[_ for _ in _
if c \
]
''', r'''
ListComp - ROOT 0,0..2,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..1,4
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'c' Load - 1,3..1,4
     .is_async 0
''', r'''

if a \
if b \

''', r'''
_comprehension_ifs - ROOT 0,0..3,0
  .ifs[2]
   0] Name 'a' Load - 1,3..1,4
   1] Name 'b' Load - 2,3..2,4
'''),

('generators[0]', 1, 2, 'ifs', {}, (None, r'''
[_ for _ in _
if a \
if b \
if c \
]
'''), r'''
[_ for _ in _
if a \
if c \
]
''', r'''
ListComp - ROOT 0,0..3,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..2,4
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 1,3..1,4
      1] Name 'c' Load - 2,3..2,4
     .is_async 0
''', r'''

if b \

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[1]
   0] Name 'b' Load - 1,3..1,4
'''),

('generators[0]', 1, 3, 'ifs', {}, (None, r'''
[_ for _ in _
if a \
if b \
if c \
]
'''), r'''
[_ for _ in _
if a \
]
''', r'''
ListComp - ROOT 0,0..2,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..1,4
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[1]
      0] Name 'a' Load - 1,3..1,4
     .is_async 0
''', r'''

if b \
if c \

''', r'''
_comprehension_ifs - ROOT 0,0..3,0
  .ifs[2]
   0] Name 'b' Load - 1,3..1,4
   1] Name 'c' Load - 2,3..2,4
'''),

('generators[0]', 2, 3, 'ifs', {}, (None, r'''
[_ for _ in _
if a \
if b \
if c \
]
'''), r'''
[_ for _ in _
if a \
if b \
]
''', r'''
ListComp - ROOT 0,0..3,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..2,4
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 1,3..1,4
      1] Name 'b' Load - 2,3..2,4
     .is_async 0
''', r'''

if c \

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[1]
   0] Name 'c' Load - 1,3..1,4
'''),

('generators[0]', 2, 3, 'ifs', {}, (None, r'''
[_ for _ in _
if a \
if b \
if c \
for _ in _ \
]
'''), r'''
[_ for _ in _
if a \
if b \
for _ in _ \
]
''', r'''
ListComp - ROOT 0,0..4,1
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..2,4
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 1,3..1,4
      1] Name 'b' Load - 2,3..2,4
     .is_async 0
   1] comprehension - 3,0..3,10
     .target Name '_' Store - 3,4..3,5
     .iter Name '_' Load - 3,9..3,10
     .is_async 0
''', r'''

if c \

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[1]
   0] Name 'c' Load - 1,3..1,4
'''),

('generators[0]', 2, 3, 'ifs', {}, (None, r'''
[_ for _ in _
if a
if b
if c
]
'''), r'''
[_ for _ in _
if a
if b
]
''', r'''
ListComp - ROOT 0,0..3,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..2,4
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 1,3..1,4
      1] Name 'b' Load - 2,3..2,4
     .is_async 0
''', r'''

if c

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[1]
   0] Name 'c' Load - 1,3..1,4
'''),

('generators[0]', 2, 3, 'ifs', {}, (None, r'''
[_ for _ in _
if a
if b
if c
for _ in _
]
'''), r'''
[_ for _ in _
if a
if b
for _ in _
]
''', r'''
ListComp - ROOT 0,0..4,1
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..2,4
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 1,3..1,4
      1] Name 'b' Load - 2,3..2,4
     .is_async 0
   1] comprehension - 3,0..3,10
     .target Name '_' Store - 3,4..3,5
     .iter Name '_' Load - 3,9..3,10
     .is_async 0
''', r'''

if c

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[1]
   0] Name 'c' Load - 1,3..1,4
'''),

('generators[0]', 3, 3, 'ifs', {}, (None, r'''
[_ for _ in _
if a \
if b \
if c \
]
'''), r'''
[_ for _ in _
if a \
if b \
if c \
]
''', r'''
ListComp - ROOT 0,0..4,1
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..3,4
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[3]
      0] Name 'a' Load - 1,3..1,4
      1] Name 'b' Load - 2,3..2,4
      2] Name 'c' Load - 3,3..3,4
     .is_async 0
''',
r'''''',
r'''_comprehension_ifs - ROOT 0,0..0,0'''),

('', 0, 2, None, {}, ('_comprehension_ifs', r'''
if a \
if b \
if c \

'''), r'''
if c \

''', r'''
_comprehension_ifs - ROOT 0,0..1,0
  .ifs[1]
   0] Name 'c' Load - 0,3..0,4
''', r'''
if a \
if b \

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[2]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'b' Load - 1,3..1,4
'''),

('', 1, 2, None, {}, ('_comprehension_ifs', r'''
if a \
if b \
if c \

'''), r'''
if a \
if c \

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[2]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'c' Load - 1,3..1,4
''', r'''

if b \

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[1]
   0] Name 'b' Load - 1,3..1,4
'''),

('', 1, 3, None, {}, ('_comprehension_ifs', r'''
if a \
if b \
if c \

'''), r'''
if a \

''', r'''
_comprehension_ifs - ROOT 0,0..1,0
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
''', r'''

if b \
if c \

''', r'''
_comprehension_ifs - ROOT 0,0..3,0
  .ifs[2]
   0] Name 'b' Load - 1,3..1,4
   1] Name 'c' Load - 2,3..2,4
'''),

('', 2, 3, None, {}, ('_comprehension_ifs', r'''
if a \
if b \
if c \

'''), r'''
if a \
if b \

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[2]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'b' Load - 1,3..1,4
''', r'''

if c \

''', r'''
_comprehension_ifs - ROOT 0,0..2,0
  .ifs[1]
   0] Name 'c' Load - 1,3..1,4
'''),

('', 3, 3, None, {}, ('_comprehension_ifs', r'''
if a \
if b \
if c \

'''), r'''
if a \
if b \
if c \

''', r'''
_comprehension_ifs - ROOT 0,0..3,0
  .ifs[3]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'b' Load - 1,3..1,4
   2] Name 'c' Load - 2,3..2,4
''',
r'''''',
r'''_comprehension_ifs - ROOT 0,0..0,0'''),

('', 0, 3, 'ifs', {}, (None,
r'''for _ in _ if a if b if c'''),
r'''for _ in _''', r'''
comprehension - ROOT 0,0..0,10
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .is_async 0
''',
r'''if a if b if c''', r'''
_comprehension_ifs - ROOT 0,0..0,14
  .ifs[3]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'b' Load - 0,8..0,9
   2] Name 'c' Load - 0,13..0,14
'''),

('generators[0]', 2, 3, 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c  ]'''),
r'''[_ for _ in _ if a if b  ]''', r'''
ListComp - ROOT 0,0..0,26
  .elt Name '_' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,23
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 0,17..0,18
      1] Name 'b' Load - 0,22..0,23
     .is_async 0
''',
r'''if c''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'c' Load - 0,3..0,4
'''),

('generators[0]', 2, 3, 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c  for x in x]'''),
r'''[_ for _ in _ if a if b  for x in x]''', r'''
ListComp - ROOT 0,0..0,36
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..0,23
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .ifs[2]
      0] Name 'a' Load - 0,17..0,18
      1] Name 'b' Load - 0,22..0,23
     .is_async 0
   1] comprehension - 0,25..0,35
     .target Name 'x' Store - 0,29..0,30
     .iter Name 'x' Load - 0,34..0,35
     .is_async 0
''',
r'''if c''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'c' Load - 0,3..0,4
'''),

('generators[0]', 0, 3, 'ifs', {}, (None,
r'''[_ for _ in _ if a if b if c  for x in x]'''),
r'''[_ for _ in _  for x in x]''', r'''
ListComp - ROOT 0,0..0,26
  .elt Name '_' Load - 0,1..0,2
  .generators[2]
   0] comprehension - 0,3..0,13
     .target Name '_' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .is_async 0
   1] comprehension - 0,15..0,25
     .target Name 'x' Store - 0,19..0,20
     .iter Name 'x' Load - 0,24..0,25
     .is_async 0
''',
r'''if a if b if c''', r'''
_comprehension_ifs - ROOT 0,0..0,14
  .ifs[3]
   0] Name 'a' Load - 0,3..0,4
   1] Name 'b' Load - 0,8..0,9
   2] Name 'c' Load - 0,13..0,14
'''),
],

'arguments': [  # ................................................................................

('', 1, 1, None, {}, ('arguments',
r'''a, b'''),
r'''a, b''', r'''
arguments - ROOT 0,0..0,4
  .args[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
''',
r'''''',
r'''arguments - ROOT 0,0..0,0'''),

('', 0, 'end', None, {}, ('arguments',
r'''a: int = ( 1 ), b: str = ( '2' ), c: float = ( 3.0 ), d: bytes = ( b'z' ), e: complex = ( 1j )'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a: int = ( 1 ), b: str = ( '2' ), c: float = ( 3.0 ), d: bytes = ( b'z' ), e: complex = ( 1j )''', r'''
arguments - ROOT 0,0..0,94
  .args[5]
   0] arg - 0,0..0,6
     .arg 'a'
     .annotation Name 'int' Load - 0,3..0,6
   1] arg - 0,16..0,22
     .arg 'b'
     .annotation Name 'str' Load - 0,19..0,22
   2] arg - 0,34..0,42
     .arg 'c'
     .annotation Name 'float' Load - 0,37..0,42
   3] arg - 0,54..0,62
     .arg 'd'
     .annotation Name 'bytes' Load - 0,57..0,62
   4] arg - 0,75..0,85
     .arg 'e'
     .annotation Name 'complex' Load - 0,78..0,85
  .defaults[5]
   0] Constant 1 - 0,11..0,12
   1] Constant '2' - 0,27..0,30
   2] Constant 3.0 - 0,47..0,50
   3] Constant b'z' - 0,67..0,71
   4] Constant 1j - 0,90..0,92
'''),

('', 1, -1, None, {}, ('arguments',
r'''a: int = ( 1 ), b: str = ( '2' ), c: float = ( 3.0 ), d: bytes = ( b'z' ), e: complex = ( 1j )'''),
r'''a: int = ( 1 ), e: complex = ( 1j )''', r'''
arguments - ROOT 0,0..0,35
  .args[2]
   0] arg - 0,0..0,6
     .arg 'a'
     .annotation Name 'int' Load - 0,3..0,6
   1] arg - 0,16..0,26
     .arg 'e'
     .annotation Name 'complex' Load - 0,19..0,26
  .defaults[2]
   0] Constant 1 - 0,11..0,12
   1] Constant 1j - 0,31..0,33
''',
r'''b: str = ( '2' ), c: float = ( 3.0 ), d: bytes = ( b'z' )''', r'''
arguments - ROOT 0,0..0,57
  .args[3]
   0] arg - 0,0..0,6
     .arg 'b'
     .annotation Name 'str' Load - 0,3..0,6
   1] arg - 0,18..0,26
     .arg 'c'
     .annotation Name 'float' Load - 0,21..0,26
   2] arg - 0,38..0,46
     .arg 'd'
     .annotation Name 'bytes' Load - 0,41..0,46
  .defaults[3]
   0] Constant '2' - 0,11..0,14
   1] Constant 3.0 - 0,31..0,34
   2] Constant b'z' - 0,51..0,55
'''),

('', 2, -2, None, {}, ('arguments',
r'''a: int = ( 1 ), b: str = ( '2' ), c: float = ( 3.0 ), d: bytes = ( b'z' ), e: complex = ( 1j )'''),
r'''a: int = ( 1 ), b: str = ( '2' ), d: bytes = ( b'z' ), e: complex = ( 1j )''', r'''
arguments - ROOT 0,0..0,74
  .args[4]
   0] arg - 0,0..0,6
     .arg 'a'
     .annotation Name 'int' Load - 0,3..0,6
   1] arg - 0,16..0,22
     .arg 'b'
     .annotation Name 'str' Load - 0,19..0,22
   2] arg - 0,34..0,42
     .arg 'd'
     .annotation Name 'bytes' Load - 0,37..0,42
   3] arg - 0,55..0,65
     .arg 'e'
     .annotation Name 'complex' Load - 0,58..0,65
  .defaults[4]
   0] Constant 1 - 0,11..0,12
   1] Constant '2' - 0,27..0,30
   2] Constant b'z' - 0,47..0,51
   3] Constant 1j - 0,70..0,72
''',
r'''c: float = ( 3.0 )''', r'''
arguments - ROOT 0,0..0,18
  .args[1]
   0] arg - 0,0..0,8
     .arg 'c'
     .annotation Name 'float' Load - 0,3..0,8
  .defaults[1]
   0] Constant 3.0 - 0,13..0,16
'''),

('args', 0, 'end', '_all', {}, (None,
r'''def f(a, b, c): pass'''),
r'''def f(): pass''', r'''
FunctionDef - ROOT 0,0..0,13
  .name 'f'
  .body[1]
   0] Pass - 0,9..0,13
''',
r'''a, b, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('args', 0, 'end', '_all', {}, (None,
r'''lambda a, b, c: None'''),
r'''lambda: None''', r'''
Lambda - ROOT 0,0..0,12
  .body Constant None - 0,8..0,12
''',
r'''a, b, c''', r'''
arguments - ROOT 0,0..0,7
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
   2] arg - 0,6..0,7
     .arg 'c'
'''),

('', 2, 3, '_all', {}, (None,
r'''config:ConfigDict,/, d, e'''),
r'''config:ConfigDict,/, d''', r'''
arguments - ROOT 0,0..0,22
  .posonlyargs[1]
   0] arg - 0,0..0,17
     .arg 'config'
     .annotation Name 'ConfigDict' Load - 0,7..0,17
  .args[1]
   0] arg - 0,21..0,22
     .arg 'd'
''',
r'''e''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'e'
'''),

('', 0, 1, '_all', {}, (None,
r'''param,/'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''param,/''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[1]
   0] arg - 0,0..0,5
     .arg 'param'
'''),

('', 1, 3, '_all', {}, (None, r'''
func:PropertyT,/,
                   *,
                   repr:bool=_Unset,
                   init:bool|None=ά中o文кκц
'''), r'''
func:PropertyT,/

''', r'''
arguments - ROOT 0,0..1,0
  .posonlyargs[1]
   0] arg - 0,0..0,14
     .arg 'func'
     .annotation Name 'PropertyT' Load - 0,5..0,14
''', r'''

                   *,
                   repr:bool=_Unset,
                   init:bool|None=ά中o文кκц
''', r'''
arguments - ROOT 0,0..3,41
  .kwonlyargs[2]
   0] arg - 2,19..2,28
     .arg 'repr'
     .annotation Name 'bool' Load - 2,24..2,28
   1] arg - 3,19..3,33
     .arg 'init'
     .annotation BinOp - 3,24..3,33
       .left Name 'bool' Load - 3,24..3,28
       .op BitOr - 3,28..3,29
       .right Constant None - 3,29..3,33
  .kw_defaults[2]
   0] Name '_Unset' Load - 2,29..2,35
   1] Name 'ά中o文кκц' Load - 3,34..3,41
'''),

('value.args', 0, 2, '_all', {}, (None, r'''
a =\
 lambda a, \
*args, \
b,: 0
'''),
'a =\\\n (lambda \n*,\nb,: 0)', r'''
Assign - ROOT 0,0..3,6
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Lambda - 1,2..3,5
    .args arguments - 1,9..3,2
      .kwonlyargs[1]
       0] arg - 3,0..3,1
         .arg 'b'
      .kw_defaults[1]
       0] None
    .body Constant 0 - 3,4..3,5
''', r'''
a, \
*args, \

''', r'''
arguments - ROOT 0,0..2,0
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 1,1..1,5
    .arg 'args'
'''),
],

'arguments_markers': [  # ................................................................................

('', 0, 1, None, {}, ('arguments',
r'''a,b,/,*,c'''),
r'''b,/,*,c''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,6..0,7
     .arg 'c'
  .kw_defaults[1]
   0] None
''',
r'''a, /''', r'''
arguments - ROOT 0,0..0,4
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 1, None, {}, ('arguments', r'''
a,
b, /
'''),
r'''b, /''', r'''
arguments - ROOT 0,0..0,4
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
''', r'''
a,
/

''', r'''
arguments - ROOT 0,0..2,0
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 1, None, {}, ('arguments',
r'''a, b, /'''),
r'''b, /''', r'''
arguments - ROOT 0,0..0,4
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
''',
r'''a, /''', r'''
arguments - ROOT 0,0..0,4
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 1, None, {}, ('arguments', r'''
a,  # a
b,  # b
/,  # /
'''), r'''
b,  # b
/,  # /
''', r'''
arguments - ROOT 0,0..1,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
''', r'''
a,  # a
/,

''', r'''
arguments - ROOT 0,0..2,0
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 2, None, {}, ('arguments', r'''
a, b, # b
c, /
'''),
r'''c, /''', r'''
arguments - ROOT 0,0..0,4
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'c'
''', r'''
a, b, /, # b

''', r'''
arguments - ROOT 0,0..1,0
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
'''),

('', 0, 2, None, {}, ('arguments', r'''
a,  # a
b,  # b
c,  # c
/,  # /
'''), r'''
c,  # c
/,  # /
''', r'''
arguments - ROOT 0,0..1,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'c'
''', r'''
a,  # a
b,  # b
/,

''', r'''
arguments - ROOT 0,0..3,0
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 1,0..1,1
     .arg 'b'
'''),

('', 0, 2, None, {}, ('arguments',
r'''a, b, /, c'''),
r'''c''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'c'
''',
r'''a, b, /''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
'''),

('', 0, 2, None, {}, ('arguments', r'''
a,  # a
b,  # b
/,  # /
c,  # c
'''),
r'''c,  # c''', r'''
arguments - ROOT 0,0..0,7
  .args[1]
   0] arg - 0,0..0,1
     .arg 'c'
''', r'''
a,  # a
b,  # b
/,  # /

''', r'''
arguments - ROOT 0,0..3,0
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 1,0..1,1
     .arg 'b'
'''),

('', 0, 2, None, {}, ('arguments', r'''
  a,  # a
  b,  # b
  /,  # /
  c,  # c
'''),
r'''  c,  # c''', r'''
arguments - ROOT 0,0..0,9
  .args[1]
   0] arg - 0,2..0,3
     .arg 'c'
''', r'''
  a,  # a
  b,  # b
  /,  # /

''', r'''
arguments - ROOT 0,0..3,0
  .posonlyargs[2]
   0] arg - 0,2..0,3
     .arg 'a'
   1] arg - 1,2..1,3
     .arg 'b'
'''),

('', 0, 1, None, {}, ('arguments',
r'''a, b, /, c'''),
r'''b, /, c''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'c'
''',
r'''a, /''', r'''
arguments - ROOT 0,0..0,4
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 1, 3, None, {}, ('arguments',
r'''a, b, /, c'''),
r'''a, /''', r'''
arguments - ROOT 0,0..0,4
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
''',
r'''b, /, c''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, 3, None, {}, ('arguments', r'''
  a,  # a
  b,  # b
  /,  # /
  c,  # c
'''), r'''
  a,  # a
  /,

''', r'''
arguments - ROOT 0,0..2,0
  .posonlyargs[1]
   0] arg - 0,2..0,3
     .arg 'a'
''', r'''

  b,  # b
  /,  # /
  c,  # c
''', r'''
arguments - ROOT 0,0..3,9
  .posonlyargs[1]
   0] arg - 1,2..1,3
     .arg 'b'
  .args[1]
   0] arg - 3,2..3,3
     .arg 'c'
'''),

('', 1, 3, None, {}, ('arguments', r'''
  a,  # a
  b,  # b
  /,  # /
  c,  # c

'''), r'''
  a,  # a
  /,

''', r'''
arguments - ROOT 0,0..2,0
  .posonlyargs[1]
   0] arg - 0,2..0,3
     .arg 'a'
''', r'''

  b,  # b
  /,  # /
  c,  # c

''', r'''
arguments - ROOT 0,0..4,0
  .posonlyargs[1]
   0] arg - 1,2..1,3
     .arg 'b'
  .args[1]
   0] arg - 3,2..3,3
     .arg 'c'
'''),

('', 1, 3, None, {}, ('arguments',
r'''a, b, /, c, d'''),
r'''a, /, d''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'd'
''',
r'''b, /, c''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, 3, None, {}, ('arguments',
r'''a, b, /, c, d'''),
r'''a, /, d''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'd'
''',
r'''b, /, c''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'c'
'''),

('', 1, 3, None, {}, ('arguments', r'''
  a,  # a
  b,  # b
  /,  # /
  c,  # c
  d,  # d
'''), r'''
  a,  # a
  /,
  d,  # d
''', r'''
arguments - ROOT 0,0..2,9
  .posonlyargs[1]
   0] arg - 0,2..0,3
     .arg 'a'
  .args[1]
   0] arg - 2,2..2,3
     .arg 'd'
''', r'''

  b,  # b
  /,  # /
  c,  # c

''', r'''
arguments - ROOT 0,0..4,0
  .posonlyargs[1]
   0] arg - 1,2..1,3
     .arg 'b'
  .args[1]
   0] arg - 3,2..3,3
     .arg 'c'
'''),

('', 0, 'end', None, {}, ('arguments',
r'''*a, b, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*a, b, c''', r'''
arguments - ROOT 0,0..0,8
  .vararg arg - 0,1..0,2
    .arg 'a'
  .kwonlyargs[2]
   0] arg - 0,4..0,5
     .arg 'b'
   1] arg - 0,7..0,8
     .arg 'c'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 1, 'end', None, {}, ('arguments',
r'''*a, b, c'''),
r'''*a''', r'''
arguments - ROOT 0,0..0,2
  .vararg arg - 0,1..0,2
    .arg 'a'
''',
r'''*, b, c''', r'''
arguments - ROOT 0,0..0,7
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'b'
   1] arg - 0,6..0,7
     .arg 'c'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 2, 'end', None, {}, ('arguments',
r'''*a, b, c'''),
r'''*a, b''', r'''
arguments - ROOT 0,0..0,5
  .vararg arg - 0,1..0,2
    .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,4..0,5
     .arg 'b'
  .kw_defaults[1]
   0] None
''',
r'''*, c''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 'end', None, {}, ('arguments', r'''
*a,
b,
c
'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''', r'''
*a,
b,
c
''', r'''
arguments - ROOT 0,0..2,1
  .vararg arg - 0,1..0,2
    .arg 'a'
  .kwonlyargs[2]
   0] arg - 1,0..1,1
     .arg 'b'
   1] arg - 2,0..2,1
     .arg 'c'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 1, 'end', None, {}, ('arguments', r'''
*a,
b,
c
'''), r'''
*a

''', r'''
arguments - ROOT 0,0..1,0
  .vararg arg - 0,1..0,2
    .arg 'a'
''', r'''

*,
b,
c
''', r'''
arguments - ROOT 0,0..3,1
  .kwonlyargs[2]
   0] arg - 2,0..2,1
     .arg 'b'
   1] arg - 3,0..3,1
     .arg 'c'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 2, 'end', None, {}, ('arguments', r'''
*a,
b,
c
'''), r'''
*a,
b

''', r'''
arguments - ROOT 0,0..2,0
  .vararg arg - 0,1..0,2
    .arg 'a'
  .kwonlyargs[1]
   0] arg - 1,0..1,1
     .arg 'b'
  .kw_defaults[1]
   0] None
''',
r'''*, c''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 'end', None, {}, ('arguments',
r'''*, b, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, b, c''', r'''
arguments - ROOT 0,0..0,7
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'b'
   1] arg - 0,6..0,7
     .arg 'c'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 0, 'end', None, {}, ('arguments', r'''
*,
b,
c
'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''', r'''
*,
b,
c
''', r'''
arguments - ROOT 0,0..2,1
  .kwonlyargs[2]
   0] arg - 1,0..1,1
     .arg 'b'
   1] arg - 2,0..2,1
     .arg 'c'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 0, 'end', None, {}, ('arguments', r'''
  *,  # *
  b,  # b
  c  # c
'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''', r'''
  *,  # *
  b,  # b
  c  # c
''', r'''
arguments - ROOT 0,0..2,8
  .kwonlyargs[2]
   0] arg - 1,2..1,3
     .arg 'b'
   1] arg - 2,2..2,3
     .arg 'c'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 1, 'end', None, {}, ('arguments',
r'''*, b, c'''),
r'''*, b''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'b'
  .kw_defaults[1]
   0] None
''',
r'''*, c''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 'end', None, {}, ('arguments', r'''
*,
b,
c
'''), r'''
*,
b

''', r'''
arguments - ROOT 0,0..2,0
  .kwonlyargs[1]
   0] arg - 1,0..1,1
     .arg 'b'
  .kw_defaults[1]
   0] None
''',
r'''*, c''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 'end', None, {}, ('arguments', r'''
a,
*,
b,
'''), r'''
a

''', r'''
arguments - ROOT 0,0..1,0
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
''', r'''

*,
b,
''', r'''
arguments - ROOT 0,0..2,2
  .kwonlyargs[1]
   0] arg - 2,0..2,1
     .arg 'b'
  .kw_defaults[1]
   0] None
'''),

('', 2, 'end', None, {}, ('arguments',
r'''a, b, *, c,'''),
r'''a, b''', r'''
arguments - ROOT 0,0..0,4
  .args[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
''',
r'''*, c,''', r'''
arguments - ROOT 0,0..0,5
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 2, 'end', None, {}, ('arguments', r'''
  a,  # a
  b,  # b
  *,  # *
  c,  # c
'''), r'''
  a,  # a
  b,  # b

''', r'''
arguments - ROOT 0,0..2,0
  .args[2]
   0] arg - 0,2..0,3
     .arg 'a'
   1] arg - 1,2..1,3
     .arg 'b'
''', r'''

  *,  # *
  c,  # c
''', r'''
arguments - ROOT 0,0..2,9
  .kwonlyargs[1]
   0] arg - 2,2..2,3
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 2, 'end', None, {}, ('arguments', r'''
  a,  # a
  b, *,  # *
  c,  # c
'''), r'''
  a,  # a
  b
''', r'''
arguments - ROOT 0,0..1,3
  .args[2]
   0] arg - 0,2..0,3
     .arg 'a'
   1] arg - 1,2..1,3
     .arg 'b'
''', r'''
*,  # *
  c,  # c
''', r'''
arguments - ROOT 0,0..1,9
  .kwonlyargs[1]
   0] arg - 1,2..1,3
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 2, 'end', None, {}, ('arguments', r'''
  a,  # a
  b, *, c,  # c
'''), r'''
  a,  # a
  b
''', r'''
arguments - ROOT 0,0..1,3
  .args[2]
   0] arg - 0,2..0,3
     .arg 'a'
   1] arg - 1,2..1,3
     .arg 'b'
''',
r'''*, c,  # c''', r'''
arguments - ROOT 0,0..0,10
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 'end', None, {}, ('arguments',
r'''  b, *, c,  # c'''),
r'''  b''', r'''
arguments - ROOT 0,0..0,3
  .args[1]
   0] arg - 0,2..0,3
     .arg 'b'
''',
r'''*, c,  # c''', r'''
arguments - ROOT 0,0..0,10
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 'end', None, {}, ('arguments',
r'''  *, c,  # c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, c,  # c''', r'''
arguments - ROOT 0,0..0,10
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 'end', None, {}, ('arguments', r'''
  b,
  *, c,  # c
'''), r'''
  b

''', r'''
arguments - ROOT 0,0..1,0
  .args[1]
   0] arg - 0,2..0,3
     .arg 'b'
''',
r'''*, c,  # c''', r'''
arguments - ROOT 0,0..0,10
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 'end', None, {}, ('arguments', r'''
  b,  # b
  *, c,  # c
'''), r'''
  b,  # b

''', r'''
arguments - ROOT 0,0..1,0
  .args[1]
   0] arg - 0,2..0,3
     .arg 'b'
''',
r'''*, c,  # c''', r'''
arguments - ROOT 0,0..0,10
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 'end', None, {}, ('arguments', r'''
  b, \
  *, c,  # c
'''), r'''
  b, \

''', r'''
arguments - ROOT 0,0..1,0
  .args[1]
   0] arg - 0,2..0,3
     .arg 'b'
''',
r'''*, c,  # c''', r'''
arguments - ROOT 0,0..0,10
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 2, None, {}, ('arguments',
r'''*, c, d, # d'''),
r'''*, c''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
''',
r'''*, d, # d''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'd'
  .kw_defaults[1]
   0] None
'''),

('', 1, 2, None, {}, ('arguments', r'''
  *, # *
  c, # c
  d, # d
'''), r'''
  *, # *
  c, # c

''', r'''
arguments - ROOT 0,0..2,0
  .kwonlyargs[1]
   0] arg - 1,2..1,3
     .arg 'c'
  .kw_defaults[1]
   0] None
''',
r'''*, d, # d''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'd'
  .kw_defaults[1]
   0] None
'''),

('', 1, 3, None, {}, ('arguments',
r'''a, b, *, c, d, # d'''),
r'''a, *, d, # d''', r'''
arguments - ROOT 0,0..0,12
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,6..0,7
     .arg 'd'
  .kw_defaults[1]
   0] None
''',
r'''b, *, c''', r'''
arguments - ROOT 0,0..0,7
  .args[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,6..0,7
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 3, None, {}, ('arguments', r'''
  a, # a
  b, # b
  *, # *
  c, # c
  d, # d
'''), r'''
  a, # a
  *,
  d, # d
''', r'''
arguments - ROOT 0,0..2,8
  .args[1]
   0] arg - 0,2..0,3
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 2,2..2,3
     .arg 'd'
  .kw_defaults[1]
   0] None
''', r'''

  b, # b
  *, # *
  c, # c

''', r'''
arguments - ROOT 0,0..4,0
  .args[1]
   0] arg - 1,2..1,3
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 3,2..3,3
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 2, None, {}, ('arguments',
r'''*, c, d, e # e'''),
r'''*, c, e # e''', r'''
arguments - ROOT 0,0..0,11
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'c'
   1] arg - 0,6..0,7
     .arg 'e'
  .kw_defaults[2]
   0] None
   1] None
''',
r'''*, d''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'd'
  .kw_defaults[1]
   0] None
'''),

('', 1, 2, None, {}, ('arguments', r'''
  *, # *
  c, # c
  d, # d
  e, # e
'''), r'''
  *, # *
  c, # c
  e, # e
''', r'''
arguments - ROOT 0,0..2,8
  .kwonlyargs[2]
   0] arg - 1,2..1,3
     .arg 'c'
   1] arg - 2,2..2,3
     .arg 'e'
  .kw_defaults[2]
   0] None
   1] None
''', r'''

  *,
  d, # d

''', r'''
arguments - ROOT 0,0..3,0
  .kwonlyargs[1]
   0] arg - 2,2..2,3
     .arg 'd'
  .kw_defaults[1]
   0] None
'''),

('', 1, 3, None, {}, ('arguments',
r'''a, b, *, c, d, e # e'''),
r'''a, *, d, e # e''', r'''
arguments - ROOT 0,0..0,14
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[2]
   0] arg - 0,6..0,7
     .arg 'd'
   1] arg - 0,9..0,10
     .arg 'e'
  .kw_defaults[2]
   0] None
   1] None
''',
r'''b, *, c''', r'''
arguments - ROOT 0,0..0,7
  .args[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,6..0,7
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 3, None, {}, ('arguments', r'''
  a, # a
  b, # b
  *, # *
  c, # c
  d, # d
  e, # e
'''), r'''
  a, # a
  *,
  d, # d
  e, # e
''', r'''
arguments - ROOT 0,0..3,8
  .args[1]
   0] arg - 0,2..0,3
     .arg 'a'
  .kwonlyargs[2]
   0] arg - 2,2..2,3
     .arg 'd'
   1] arg - 3,2..3,3
     .arg 'e'
  .kw_defaults[2]
   0] None
   1] None
''', r'''

  b, # b
  *, # *
  c, # c

''', r'''
arguments - ROOT 0,0..4,0
  .args[1]
   0] arg - 1,2..1,3
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 3,2..3,3
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 1, None, {}, ('arguments',
r'''*, c, **d # **d'''),
r'''**d # **d''', r'''
arguments - ROOT 0,0..0,9
  .kwarg arg - 0,2..0,3
    .arg 'd'
''',
r'''*, c''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 1, None, {}, ('arguments', r'''
  *, # *
  c, # c
  **d, # **d
'''),
r'''  **d, # **d''', r'''
arguments - ROOT 0,0..0,12
  .kwarg arg - 0,4..0,5
    .arg 'd'
''', r'''
  *, # *
  c, # c

''', r'''
arguments - ROOT 0,0..2,0
  .kwonlyargs[1]
   0] arg - 1,2..1,3
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 2, None, {}, ('arguments',
r'''*, c, d, **e # **e'''),
r'''*, c, **e # **e''', r'''
arguments - ROOT 0,0..0,15
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'c'
  .kw_defaults[1]
   0] None
  .kwarg arg - 0,8..0,9
    .arg 'e'
''',
r'''*, d''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'd'
  .kw_defaults[1]
   0] None
'''),

('', 1, 2, None, {}, ('arguments', r'''
  *, # *
  c, # c
  d, # d
  **e, # **e
'''), r'''
  *, # *
  c, # c
  **e, # **e
''', r'''
arguments - ROOT 0,0..2,12
  .kwonlyargs[1]
   0] arg - 1,2..1,3
     .arg 'c'
  .kw_defaults[1]
   0] None
  .kwarg arg - 2,4..2,5
    .arg 'e'
''', r'''

  *,
  d, # d

''', r'''
arguments - ROOT 0,0..3,0
  .kwonlyargs[1]
   0] arg - 2,2..2,3
     .arg 'd'
  .kw_defaults[1]
   0] None
'''),

('', 1, 3, None, {}, ('arguments',
r'''a, b, *, c, d, **e # **e'''),
r'''a, *, d, **e # **e''', r'''
arguments - ROOT 0,0..0,18
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,6..0,7
     .arg 'd'
  .kw_defaults[1]
   0] None
  .kwarg arg - 0,11..0,12
    .arg 'e'
''',
r'''b, *, c''', r'''
arguments - ROOT 0,0..0,7
  .args[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,6..0,7
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 3, None, {}, ('arguments', r'''
  a, # a
  b, # b
  *, # *
  c, # c
  d, # d
  **e, # **e
'''), r'''
  a, # a
  *,
  d, # d
  **e, # **e
''', r'''
arguments - ROOT 0,0..3,12
  .args[1]
   0] arg - 0,2..0,3
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 2,2..2,3
     .arg 'd'
  .kw_defaults[1]
   0] None
  .kwarg arg - 3,4..3,5
    .arg 'e'
''', r'''

  b, # b
  *, # *
  c, # c

''', r'''
arguments - ROOT 0,0..4,0
  .args[1]
   0] arg - 1,2..1,3
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 3,2..3,3
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 3, None, {}, ('arguments',
r'''a, b, /, *, c, d'''),
r'''a, /, *, d''', r'''
arguments - ROOT 0,0..0,10
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,9..0,10
     .arg 'd'
  .kw_defaults[1]
   0] None
''',
r'''b, /, *, c''', r'''
arguments - ROOT 0,0..0,10
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,9..0,10
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 1, 3, None, {}, ('arguments', r'''
  a, # a
  b, # b
  /, # /
  *, # *
  c, # c
  d, # d
'''), r'''
  a, # a
  /,
  *,
  d, # d
''', r'''
arguments - ROOT 0,0..3,8
  .posonlyargs[1]
   0] arg - 0,2..0,3
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 3,2..3,3
     .arg 'd'
  .kw_defaults[1]
   0] None
''', r'''

  b, # b
  /, # /
  *, # *
  c, # c

''', r'''
arguments - ROOT 0,0..5,0
  .posonlyargs[1]
   0] arg - 1,2..1,3
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 4,2..4,3
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 2, None, {}, ('arguments',
r'''a, b, /, *, c, d'''),
r'''*, c, d''', r'''
arguments - ROOT 0,0..0,7
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'c'
   1] arg - 0,6..0,7
     .arg 'd'
  .kw_defaults[2]
   0] None
   1] None
''',
r'''a, b, /''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
'''),

('', 0, 2, None, {}, ('arguments', r'''
  a, # a
  b, # b
  /, # /
  *, # *
  c, # c
  d, # d
'''), r'''
  *, # *
  c, # c
  d, # d
''', r'''
arguments - ROOT 0,0..2,8
  .kwonlyargs[2]
   0] arg - 1,2..1,3
     .arg 'c'
   1] arg - 2,2..2,3
     .arg 'd'
  .kw_defaults[2]
   0] None
   1] None
''', r'''
  a, # a
  b, # b
  /, # /

''', r'''
arguments - ROOT 0,0..3,0
  .posonlyargs[2]
   0] arg - 0,2..0,3
     .arg 'a'
   1] arg - 1,2..1,3
     .arg 'b'
'''),

('', 2, 4, None, {}, ('arguments',
r'''a, b, /, *, c, d'''),
r'''a, b, /''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
''',
r'''*, c, d''', r'''
arguments - ROOT 0,0..0,7
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'c'
   1] arg - 0,6..0,7
     .arg 'd'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 2, 4, None, {}, ('arguments', r'''
  a, # a
  b, # b
  /, # /
  *, # *
  c, # c
  d, # d
'''), r'''
  a, # a
  b, # b
  /, # /

''', r'''
arguments - ROOT 0,0..3,0
  .posonlyargs[2]
   0] arg - 0,2..0,3
     .arg 'a'
   1] arg - 1,2..1,3
     .arg 'b'
''', r'''

  *, # *
  c, # c
  d, # d
''', r'''
arguments - ROOT 0,0..3,8
  .kwonlyargs[2]
   0] arg - 2,2..2,3
     .arg 'c'
   1] arg - 3,2..3,3
     .arg 'd'
  .kw_defaults[2]
   0] None
   1] None
'''),
],

'arguments_as': [  # ................................................................................

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''*a, b'''),
r'''**NodeError("cannot have keywords following vararg for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''*a, **b'''),
r'''**NodeError("cannot have kwarg for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''*a'''),
r'''**NodeError("cannot have vararg for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''*a'''),
r'''**NodeError("cannot have vararg for args_as='kw'")**'''),

('', 0, 'end', None, {'args_as': 'arg_only', '_del': False}, ('arguments',
r'''*a'''),
r'''**NodeError("cannot have vararg for args_as='arg_only'")**'''),

('', 0, 'end', None, {'args_as': 'kw_only', '_del': False}, ('arguments',
r'''*a'''),
r'''**NodeError("cannot have vararg for args_as='kw_only'")**'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''**a'''),
r'''**NodeError("cannot have kwarg for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''**a'''),
r'''**NodeError("cannot have kwarg for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'arg_only', '_del': False}, ('arguments',
r'''**a'''),
r'''**NodeError("cannot have kwarg for args_as='arg_only'")**'''),

('', 0, 'end', None, {'args_as': 'kw_only', '_del': False}, ('arguments',
r'''**a'''),
r'''**NodeError("cannot have kwarg for args_as='kw_only'")**'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, /'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, /''', r'''
arguments - ROOT 0,0..0,6
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a=1, /, *b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, /, *b''', r'''
arguments - ROOT 0,0..0,10
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 0,9..0,10
    .arg 'b'
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a=1, /, **b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, /, **b''', r'''
arguments - ROOT 0,0..0,11
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwarg arg - 0,10..0,11
    .arg 'b'
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, /, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, /''', r'''
arguments - ROOT 0,0..0,11
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, /, *, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, /''', r'''
arguments - ROOT 0,0..0,11
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, c=3, /''', r'''
arguments - ROOT 0,0..0,16
  .posonlyargs[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
   2] arg - 0,10..0,11
     .arg 'c'
  .defaults[3]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
   2] Constant 3 - 0,12..0,13
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, /''', r'''
arguments - ROOT 0,0..0,6
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''*, a=1'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, /''', r'''
arguments - ROOT 0,0..0,6
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, *, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, /''', r'''
arguments - ROOT 0,0..0,11
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, /, b=2, *d, c=3'''),
r'''**NodeError("cannot have vararg for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c=3, **d'''),
r'''**NodeError("cannot have kwarg for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a=1, /, b=2, *d, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, /, *d, c=3''', r'''
arguments - ROOT 0,0..0,20
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
  .vararg arg - 0,14..0,15
    .arg 'd'
  .kwonlyargs[1]
   0] arg - 0,17..0,18
     .arg 'c'
  .kw_defaults[1]
   0] Constant 3 - 0,19..0,20
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c=3, **d'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, c=3, /, **d''', r'''
arguments - ROOT 0,0..0,21
  .posonlyargs[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
   2] arg - 0,10..0,11
     .arg 'c'
  .kwarg arg - 0,20..0,21
    .arg 'd'
  .defaults[3]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
   2] Constant 3 - 0,12..0,13
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a, *b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, *b''', r'''
arguments - ROOT 0,0..0,5
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 0,4..0,5
    .arg 'b'
'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a, *b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, *b''', r'''
arguments - ROOT 0,0..0,5
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 0,4..0,5
    .arg 'b'
'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a, *b, **c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, *b, **c''', r'''
arguments - ROOT 0,0..0,10
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 0,4..0,5
    .arg 'b'
  .kwarg arg - 0,9..0,10
    .arg 'c'
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a=1, /, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2''', r'''
arguments - ROOT 0,0..0,8
  .args[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''b=2, *, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''b=2, c=3''', r'''
arguments - ROOT 0,0..0,8
  .args[2]
   0] arg - 0,0..0,1
     .arg 'b'
   1] arg - 0,5..0,6
     .arg 'c'
  .defaults[2]
   0] Constant 2 - 0,2..0,3
   1] Constant 3 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, c=3''', r'''
arguments - ROOT 0,0..0,13
  .args[3]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
   2] arg - 0,10..0,11
     .arg 'c'
  .defaults[3]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
   2] Constant 3 - 0,12..0,13
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''b=2, *d, c=3'''),
r'''**NodeError("cannot have keywords following vararg for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''b=2, *, c=3, **d'''),
r'''**NodeError("cannot have kwarg for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''b=2, *d, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''b=2, *d, c=3''', r'''
arguments - ROOT 0,0..0,12
  .args[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .vararg arg - 0,6..0,7
    .arg 'd'
  .kwonlyargs[1]
   0] arg - 0,9..0,10
     .arg 'c'
  .kw_defaults[1]
   0] Constant 3 - 0,11..0,12
  .defaults[1]
   0] Constant 2 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''b=2, *, c=3, **d'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''b=2, c=3, **d''', r'''
arguments - ROOT 0,0..0,13
  .args[2]
   0] arg - 0,0..0,1
     .arg 'b'
   1] arg - 0,5..0,6
     .arg 'c'
  .kwarg arg - 0,12..0,13
    .arg 'd'
  .defaults[2]
   0] Constant 2 - 0,2..0,3
   1] Constant 3 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''*, a'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a''', r'''
arguments - ROOT 0,0..0,4
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'a'
  .kw_defaults[1]
   0] None
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''*, a, **b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a, **b''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'a'
  .kw_defaults[1]
   0] None
  .kwarg arg - 0,8..0,9
    .arg 'b'
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''**a'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''**a''', r'''
arguments - ROOT 0,0..0,3
  .kwarg arg - 0,2..0,3
    .arg 'a'
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''b=2, *, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, b=2, c=3''', r'''
arguments - ROOT 0,0..0,11
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'b'
   1] arg - 0,8..0,9
     .arg 'c'
  .kw_defaults[2]
   0] Constant 2 - 0,5..0,6
   1] Constant 3 - 0,10..0,11
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /, *, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, c=3''', r'''
arguments - ROOT 0,0..0,11
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'c'
  .kw_defaults[2]
   0] Constant 1 - 0,5..0,6
   1] Constant 3 - 0,10..0,11
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, b=2, c=3''', r'''
arguments - ROOT 0,0..0,16
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'b'
   2] arg - 0,13..0,14
     .arg 'c'
  .kw_defaults[3]
   0] Constant 1 - 0,5..0,6
   1] Constant 2 - 0,10..0,11
   2] Constant 3 - 0,15..0,16
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''b=2, **d'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, b=2, **d''', r'''
arguments - ROOT 0,0..0,11
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'b'
  .kw_defaults[1]
   0] Constant 2 - 0,5..0,6
  .kwarg arg - 0,10..0,11
    .arg 'd'
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /, **d'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, **d''', r'''
arguments - ROOT 0,0..0,11
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'a'
  .kw_defaults[1]
   0] Constant 1 - 0,5..0,6
  .kwarg arg - 0,10..0,11
    .arg 'd'
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /, b=2, **d'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, b=2, **d''', r'''
arguments - ROOT 0,0..0,16
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'b'
  .kw_defaults[2]
   0] Constant 1 - 0,5..0,6
   1] Constant 2 - 0,10..0,11
  .kwarg arg - 0,15..0,16
    .arg 'd'
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''b=2, *d, c=3'''),
r'''**NodeError("cannot have vararg for args_as='kw'")**'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /, *d, c=3'''),
r'''**NodeError("cannot have vararg for args_as='kw'")**'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /, b=2, *d, c=3'''),
r'''**NodeError("cannot have vararg for args_as='kw'")**'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''b=2, *d, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''b=2, *d, c=3''', r'''
arguments - ROOT 0,0..0,12
  .args[1]
   0] arg - 0,0..0,1
     .arg 'b'
  .vararg arg - 0,6..0,7
    .arg 'd'
  .kwonlyargs[1]
   0] arg - 0,9..0,10
     .arg 'c'
  .kw_defaults[1]
   0] Constant 3 - 0,11..0,12
  .defaults[1]
   0] Constant 2 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a=1, /, *d, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, *d, c=3''', r'''
arguments - ROOT 0,0..0,12
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 0,6..0,7
    .arg 'd'
  .kwonlyargs[1]
   0] arg - 0,9..0,10
     .arg 'c'
  .kw_defaults[1]
   0] Constant 3 - 0,11..0,12
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a=1, /, b=2, *d, c=3'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, *d, c=3''', r'''
arguments - ROOT 0,0..0,17
  .args[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
  .vararg arg - 0,11..0,12
    .arg 'd'
  .kwonlyargs[1]
   0] arg - 0,14..0,15
     .arg 'c'
  .kw_defaults[1]
   0] Constant 3 - 0,16..0,17
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, /, *, b'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a=1, /, *, b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, /, *, b''', r'''
arguments - ROOT 0,0..0,12
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,11..0,12
     .arg 'b'
  .kw_defaults[1]
   0] None
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a=1, /, *, b'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a=1, /, *, b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, *, b''', r'''
arguments - ROOT 0,0..0,9
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,8..0,9
     .arg 'b'
  .kw_defaults[1]
   0] None
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /, *, b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, b''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'b'
  .kw_defaults[2]
   0] Constant 1 - 0,5..0,6
   1] None
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a=1, /, *, b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, b''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'b'
  .kw_defaults[2]
   0] Constant 1 - 0,5..0,6
   1] None
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, *, b'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a=1, *, b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, /, *, b''', r'''
arguments - ROOT 0,0..0,12
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,11..0,12
     .arg 'b'
  .kw_defaults[1]
   0] None
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a=1, *, b'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a=1, *, b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, *, b''', r'''
arguments - ROOT 0,0..0,9
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,8..0,9
     .arg 'b'
  .kw_defaults[1]
   0] None
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, *, b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, b''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'b'
  .kw_defaults[2]
   0] Constant 1 - 0,5..0,6
   1] None
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a=1, *, b'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, b''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'b'
  .kw_defaults[2]
   0] Constant 1 - 0,5..0,6
   1] None
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, /, *, c''', r'''
arguments - ROOT 0,0..0,17
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,16..0,17
     .arg 'c'
  .kw_defaults[1]
   0] None
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, b=2, *, c''', r'''
arguments - ROOT 0,0..0,14
  .args[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,5..0,6
     .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,13..0,14
     .arg 'c'
  .kw_defaults[1]
   0] None
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,7..0,8
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, b=2, c''', r'''
arguments - ROOT 0,0..0,14
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'b'
   2] arg - 0,13..0,14
     .arg 'c'
  .kw_defaults[3]
   0] Constant 1 - 0,5..0,6
   1] Constant 2 - 0,10..0,11
   2] None
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a=1, /, b=2, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1, b=2, c''', r'''
arguments - ROOT 0,0..0,14
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,8..0,9
     .arg 'b'
   2] arg - 0,13..0,14
     .arg 'c'
  .kw_defaults[3]
   0] Constant 1 - 0,5..0,6
   1] Constant 2 - 0,10..0,11
   2] None
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a, /, b=2, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a, b=2, c''', r'''
arguments - ROOT 0,0..0,12
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,6..0,7
     .arg 'b'
   2] arg - 0,11..0,12
     .arg 'c'
  .kw_defaults[3]
   0] None
   1] Constant 2 - 0,8..0,9
   2] None
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a, /, b=2, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a, b=2, c''', r'''
arguments - ROOT 0,0..0,12
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,6..0,7
     .arg 'b'
   2] arg - 0,11..0,12
     .arg 'c'
  .kw_defaults[3]
   0] None
   1] Constant 2 - 0,8..0,9
   2] None
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a, /, *, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, b=2, /''', r'''
arguments - ROOT 0,0..0,9
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
  .defaults[1]
   0] Constant 2 - 0,5..0,6
'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a, /, *, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, b=2, /''', r'''
arguments - ROOT 0,0..0,9
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
  .defaults[1]
   0] Constant 2 - 0,5..0,6
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a, /, *, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, b=2''', r'''
arguments - ROOT 0,0..0,6
  .args[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
  .defaults[1]
   0] Constant 2 - 0,5..0,6
'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a, /, *, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, b=2''', r'''
arguments - ROOT 0,0..0,6
  .args[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'b'
  .defaults[1]
   0] Constant 2 - 0,5..0,6
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a, /, *, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a, b=2''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,6..0,7
     .arg 'b'
  .kw_defaults[2]
   0] None
   1] Constant 2 - 0,8..0,9
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a, /, *, b=2'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a, b=2''', r'''
arguments - ROOT 0,0..0,9
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,6..0,7
     .arg 'b'
  .kw_defaults[2]
   0] None
   1] Constant 2 - 0,8..0,9
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a, /, *, b=2, c'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a, /, *, b=2, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, /, *, b=2, c''', r'''
arguments - ROOT 0,0..0,15
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[2]
   0] arg - 0,9..0,10
     .arg 'b'
   1] arg - 0,14..0,15
     .arg 'c'
  .kw_defaults[2]
   0] Constant 2 - 0,11..0,12
   1] None
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a, /, *, b=2, c'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a, /, *, b=2, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, *, b=2, c''', r'''
arguments - ROOT 0,0..0,12
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .kwonlyargs[2]
   0] arg - 0,6..0,7
     .arg 'b'
   1] arg - 0,11..0,12
     .arg 'c'
  .kw_defaults[2]
   0] Constant 2 - 0,8..0,9
   1] None
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a, /, *, b=2, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a, b=2, c''', r'''
arguments - ROOT 0,0..0,12
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,6..0,7
     .arg 'b'
   2] arg - 0,11..0,12
     .arg 'c'
  .kw_defaults[3]
   0] None
   1] Constant 2 - 0,8..0,9
   2] None
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a, /, *, b=2, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a, b=2, c''', r'''
arguments - ROOT 0,0..0,12
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,6..0,7
     .arg 'b'
   2] arg - 0,11..0,12
     .arg 'c'
  .kw_defaults[3]
   0] None
   1] Constant 2 - 0,8..0,9
   2] None
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a=1, /'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a=1''', r'''
arguments - ROOT 0,0..0,6
  .kwonlyargs[1]
   0] arg - 0,3..0,4
     .arg 'a'
  .kw_defaults[1]
   0] Constant 1 - 0,5..0,6
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''*, a=1'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a=1, /''', r'''
arguments - ROOT 0,0..0,6
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .defaults[1]
   0] Constant 1 - 0,2..0,3
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, c, /''', r'''
arguments - ROOT 0,0..0,7
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'c'
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, c''', r'''
arguments - ROOT 0,0..0,4
  .args[2]
   0] arg - 0,0..0,1
     .arg 'a'
   1] arg - 0,3..0,4
     .arg 'c'
'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a, *, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''*, a, c''', r'''
arguments - ROOT 0,0..0,7
  .kwonlyargs[2]
   0] arg - 0,3..0,4
     .arg 'a'
   1] arg - 0,6..0,7
     .arg 'c'
  .kw_defaults[2]
   0] None
   1] None
'''),

('', 0, 'end', None, {'args_as': 'pos', '_del': False}, ('arguments',
r'''a, *b, c'''),
r'''**NodeError("cannot have vararg for args_as='pos'")**'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False}, ('arguments',
r'''a, *b, c'''),
r'''**NodeError("cannot have keywords following vararg for args_as='arg'")**'''),

('', 0, 'end', None, {'args_as': 'kw', '_del': False}, ('arguments',
r'''a, *b, c'''),
r'''**NodeError("cannot have vararg for args_as='kw'")**'''),

('', 0, 'end', None, {'args_as': 'pos_maybe', '_del': False}, ('arguments',
r'''a, *b, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, /, *b, c''', r'''
arguments - ROOT 0,0..0,11
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 0,7..0,8
    .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,10..0,11
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 'end', None, {'args_as': 'arg_maybe', '_del': False}, ('arguments',
r'''a, *b, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, *b, c''', r'''
arguments - ROOT 0,0..0,8
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 0,4..0,5
    .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,7..0,8
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 'end', None, {'args_as': 'kw_maybe', '_del': False}, ('arguments',
r'''a, *b, c'''),
r'''''',
r'''arguments - ROOT 0,0..0,0''',
r'''a, *b, c''', r'''
arguments - ROOT 0,0..0,8
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .vararg arg - 0,4..0,5
    .arg 'b'
  .kwonlyargs[1]
   0] arg - 0,7..0,8
     .arg 'c'
  .kw_defaults[1]
   0] None
'''),

('', 0, 'end', None, {'args_as': 'arg', '_del': False, '_verify': False}, ('arguments', r'''
    config=None,
    *,
    etype,
    long_version: bool = False,
    config=None
'''),
r'''**NodeError("cannot have args with defaults following args without defaults for args_as='arg'")**'''),
],

'MatchMapping': [  # ................................................................................

('', 0, 0, None, {}, ('pattern',
r'''{0: x, **rest}'''),
r'''{0: x, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
''',
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2'''),

('', 0, 1, None, {}, ('pattern',
r'''{0: x, **rest}'''),
r'''{**rest}''', r'''
MatchMapping - ROOT 0,0..0,8
  .rest 'rest'
''',
r'''{0: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 2, None, {}, ('pattern',
r'''{0: x, **rest}'''),
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2''',
r'''{0: x, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
'''),

('', 1, 2, None, {}, ('pattern',
r'''{0: x, **rest}'''),
r'''{0: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
''',
r'''{**rest}''', r'''
MatchMapping - ROOT 0,0..0,8
  .rest 'rest'
'''),

('', 2, 2, None, {}, ('pattern',
r'''{0: x, **rest}'''),
r'''{0: x, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
''',
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2'''),

('', 0, 1, None, {}, ('pattern',
r'''{0: x, 1: y, **rest}'''),
r'''{1: y, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'y'
  .rest 'rest'
''',
r'''{0: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
'''),

('', 0, 2, None, {}, ('pattern',
r'''{0: x, 1: y, **rest}'''),
r'''{**rest}''', r'''
MatchMapping - ROOT 0,0..0,8
  .rest 'rest'
''',
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

('', 0, 3, None, {}, ('pattern',
r'''{0: x, 1: y, **rest}'''),
r'''{}''',
r'''MatchMapping - ROOT 0,0..0,2''',
r'''{0: x, 1: y, **rest}''', r'''
MatchMapping - ROOT 0,0..0,20
  .keys[2]
   0] Constant 0 - 0,1..0,2
   1] Constant 1 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'x'
   1] MatchAs - 0,10..0,11
     .name 'y'
  .rest 'rest'
'''),

('', 1, 2, None, {}, ('pattern',
r'''{0: x, 1: y, **rest}'''),
r'''{0: x, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
  .rest 'rest'
''',
r'''{1: y}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'y'
'''),

('', 1, 3, None, {}, ('pattern',
r'''{0: x, 1: y, **rest}'''),
r'''{0: x}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 0 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'x'
''',
r'''{1: y, **rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'y'
  .rest 'rest'
'''),

('', 2, 3, None, {}, ('pattern',
r'''{0: x, 1: y, **rest}'''),
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
''',
r'''{**rest}''', r'''
MatchMapping - ROOT 0,0..0,8
  .rest 'rest'
'''),
],

'MatchClass_patterns': [  # ................................................................................

('', 0, 0, 'patterns', {}, ('pattern',
r'''call(a)'''),
r'''call(a)''', r'''
MatchClass - ROOT 0,0..0,7
  .cls Name 'call' Load - 0,0..0,4
  .patterns[1]
   0] MatchAs - 0,5..0,6
     .name 'a'
''',
r'''[]''',
r'''MatchSequence - ROOT 0,0..0,2'''),

('', 0, 'end', 'patterns', {}, ('pattern',
r'''call(a)'''),
r'''call()''', r'''
MatchClass - ROOT 0,0..0,6
  .cls Name 'call' Load - 0,0..0,4
''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 'end', 'patterns', {}, ('pattern',
r'''call(a, c=d)'''),
r'''call(c=d)''', r'''
MatchClass - ROOT 0,0..0,9
  .cls Name 'call' Load - 0,0..0,4
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 0,7..0,8
     .name 'd'
''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 1, 'patterns', {}, ('pattern',
r'''call(a, c=d)'''),
r'''call(c=d)''', r'''
MatchClass - ROOT 0,0..0,9
  .cls Name 'call' Load - 0,0..0,4
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 0,7..0,8
     .name 'd'
''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 1, 'patterns', {}, ('pattern', r'''
call( \
a \
, \
b \
, \
c \
= \
d \
)
'''), r'''
call( \
b \
, \
c \
= \
d \
)
''', r'''
MatchClass - ROOT 0,0..6,1
  .cls Name 'call' Load - 0,0..0,4
  .patterns[1]
   0] MatchAs - 1,0..1,1
     .name 'b'
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 5,0..5,1
     .name 'd'
''', r'''
[
a \
 \
]
''', r'''
MatchSequence - ROOT 0,0..3,1
  .patterns[1]
   0] MatchAs - 1,0..1,1
     .name 'a'
'''),

('', 0, 2, 'patterns', {}, ('pattern', r'''
call( \
a \
, \
b \
, \
c \
= \
d \
)
'''), r'''
call( \
c \
= \
d \
)
''', r'''
MatchClass - ROOT 0,0..4,1
  .cls Name 'call' Load - 0,0..0,4
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 3,0..3,1
     .name 'd'
''', r'''
[
a \
, \
b \
 \
]
''', r'''
MatchSequence - ROOT 0,0..5,1
  .patterns[2]
   0] MatchAs - 1,0..1,1
     .name 'a'
   1] MatchAs - 3,0..3,1
     .name 'b'
'''),

('', 0, 2, 'patterns', {}, ('pattern', r'''
call( \
a, \
b, \
c \
= \
d \
)
'''), r'''
call( \
c \
= \
d \
)
''', r'''
MatchClass - ROOT 0,0..4,1
  .cls Name 'call' Load - 0,0..0,4
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 3,0..3,1
     .name 'd'
''', r'''
[
a, \
b \
]
''', r'''
MatchSequence - ROOT 0,0..3,1
  .patterns[2]
   0] MatchAs - 1,0..1,1
     .name 'a'
   1] MatchAs - 2,0..2,1
     .name 'b'
'''),

('', 1, 2, 'patterns', {}, ('pattern', r'''
call(
a
,
b
,
c
,
d
=
e
)
'''), r'''
call(
a
,
c
,
d
=
e
)
''', r'''
MatchClass - ROOT 0,0..8,1
  .cls Name 'call' Load - 0,0..0,4
  .patterns[2]
   0] MatchAs - 1,0..1,1
     .name 'a'
   1] MatchAs - 3,0..3,1
     .name 'c'
  .kwd_attrs[1]
   0] 'd'
  .kwd_patterns[1]
   0] MatchAs - 7,0..7,1
     .name 'e'
''', r'''
[
b

]
''', r'''
MatchSequence - ROOT 0,0..3,1
  .patterns[1]
   0] MatchAs - 1,0..1,1
     .name 'b'
'''),

('', 0, 3, 'patterns', {}, ('pattern', r'''
call(
a
,
b
,
c
=
d
)
'''), r'''
call(
c
=
d
)
''', r'''
MatchClass - ROOT 0,0..4,1
  .cls Name 'call' Load - 0,0..0,4
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 3,0..3,1
     .name 'd'
''', r'''
[
a
,
b

]
''', r'''
MatchSequence - ROOT 0,0..5,1
  .patterns[2]
   0] MatchAs - 1,0..1,1
     .name 'a'
   1] MatchAs - 3,0..3,1
     .name 'b'
'''),

('', 0, 3, 'patterns', {}, ('pattern', r'''
call(
a,
b,
c,
d
=
e
)
'''), r'''
call(
d
=
e
)
''', r'''
MatchClass - ROOT 0,0..4,1
  .cls Name 'call' Load - 0,0..0,4
  .kwd_attrs[1]
   0] 'd'
  .kwd_patterns[1]
   0] MatchAs - 3,0..3,1
     .name 'e'
''', r'''
[
a,
b,
c
]
''', r'''
MatchSequence - ROOT 0,0..4,1
  .patterns[3]
   0] MatchAs - 1,0..1,1
     .name 'a'
   1] MatchAs - 2,0..2,1
     .name 'b'
   2] MatchAs - 3,0..3,1
     .name 'c'
'''),

('', 0, 1, 'patterns', {}, ('pattern',
r'''call(a, b, c=d)'''),
r'''call(b, c=d)''', r'''
MatchClass - ROOT 0,0..0,12
  .cls Name 'call' Load - 0,0..0,4
  .patterns[1]
   0] MatchAs - 0,5..0,6
     .name 'b'
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 0,10..0,11
     .name 'd'
''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 1, 2, 'patterns', {}, ('pattern',
r'''call(a, b, c=d)'''),
r'''call(a, c=d)''', r'''
MatchClass - ROOT 0,0..0,12
  .cls Name 'call' Load - 0,0..0,4
  .patterns[1]
   0] MatchAs - 0,5..0,6
     .name 'a'
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 0,10..0,11
     .name 'd'
''',
r'''[b]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'b'
'''),

('', 1, 2, 'patterns', {}, ('pattern',
r'''call(a, b,)'''),
r'''call(a)''', r'''
MatchClass - ROOT 0,0..0,7
  .cls Name 'call' Load - 0,0..0,4
  .patterns[1]
   0] MatchAs - 0,5..0,6
     .name 'a'
''',
r'''[b]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'b'
'''),

('', 1, 2, 'patterns', {}, ('pattern',
r'''call(a, b, c=d,)'''),
r'''call(a, c=d,)''', r'''
MatchClass - ROOT 0,0..0,13
  .cls Name 'call' Load - 0,0..0,4
  .patterns[1]
   0] MatchAs - 0,5..0,6
     .name 'a'
  .kwd_attrs[1]
   0] 'c'
  .kwd_patterns[1]
   0] MatchAs - 0,10..0,11
     .name 'd'
''',
r'''[b]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'b'
'''),
],

'MatchOr': [  # ................................................................................

('', 0, 0, None, {'_verify_get': False}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
''',
r'''''',
r'''MatchOr - ROOT 0,0..0,0'''),

('', 0, 1, None, {'_verify': False}, ('MatchOr',
r'''a | b'''),
r'''b''', r'''
MatchOr - ROOT 0,0..0,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'b'
''',
r'''a''', r'''
MatchOr - ROOT 0,0..0,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('', 0, 2, None, {'_verify_self': False}, ('MatchOr',
r'''a | b'''),
r'''''',
r'''MatchOr - ROOT 0,0..0,0''',
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', 0, 0, None, {'_verify_get': False, 'norm_self': True}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
''',
r'''''',
r'''MatchOr - ROOT 0,0..0,0'''),

('', 0, 1, None, {'_verify_get': False, 'norm_self': True}, ('MatchOr',
r'''a | b'''),
r'''b''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'b'
''',
r'''a''', r'''
MatchOr - ROOT 0,0..0,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('', 0, 2, None, {'norm_self': True}, ('MatchOr',
r'''a | b'''),
r'''**ValueError('cannot cut all MatchOr.patterns without norm_self=False')**''',
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', 0, 0, None, {'norm_get': True, '_del': False}, ('MatchOr',
r'''a | b'''),
r'''**ValueError('cannot get empty slice from MatchOr without norm_get=False')**'''),

('', 0, 1, None, {'_verify_self': False, 'norm_get': True}, ('MatchOr',
r'''a | b'''),
r'''b''', r'''
MatchOr - ROOT 0,0..0,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'b'
''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 2, None, {'_verify_self': False, 'norm_get': True}, ('MatchOr',
r'''a | b'''),
r'''''',
r'''MatchOr - ROOT 0,0..0,0''',
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', 0, 0, None, {'norm': True, '_del': False}, ('MatchOr',
r'''a | b'''),
r'''**ValueError('cannot get empty slice from MatchOr without norm_get=False')**'''),

('', 0, 1, None, {'norm': True}, ('MatchOr',
r'''a | b'''),
r'''b''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'b'
''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 2, None, {'norm': True}, ('MatchOr',
r'''a | b'''),
r'''**ValueError('cannot cut all MatchOr.patterns without norm_self=False')**''',
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),
],

'type_params': [  # ................................................................................

('body[0]', 1, 2, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 1, 2, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 1, 2, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 1, 2, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
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

('', 1, 2, 'type_params', {'_ver': 12}, ('_type_params',
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

('', 0, 3, 'type_params', {'_ver': 12}, ('_type_params',
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

'virtual_field__all': [  # ................................................................................

('', 1, 2, '_all', {}, ('Dict',
r'''{1: a, 2: b, 3: c}'''),
r'''{1: a, 3: c}''', r'''
Dict - ROOT 0,0..0,12
  .keys[2]
   0] Constant 1 - 0,1..0,2
   1] Constant 3 - 0,7..0,8
  .values[2]
   0] Name 'a' Load - 0,4..0,5
   1] Name 'c' Load - 0,10..0,11
''',
r'''{2: b}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .values[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', 1, 2, '_all', {}, ('MatchMapping',
r'''{1: a, 2: b, 3: c}'''),
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
''',
r'''{2: b}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 2 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', 1, 2, '_all', {'_verify_get': False}, ('Compare',
r'''a < b > c'''),
r'''a > c''', r'''
Compare - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Gt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 0,4..0,5
''',
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
'''),

('', 1, 2, '_all', {'_verify_get': False, 'op_side': 'right'}, ('Compare',
r'''a < b > c'''),
r'''a < c''', r'''
Compare - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 0,2..0,3
  .comparators[1]
   0] Name 'c' Load - 0,4..0,5
''',
r'''b''', r'''
Compare - ROOT 0,0..0,1
  .left Name 'b' Load - 0,0..0,1
'''),
],

'virtual_field__body': [  # ................................................................................

('', 0, 'end', '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''"""doc"""''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
''', r'''
a
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('Interactive',
r'''"""non-doc"""; a; b'''),
r'''''',
r'''Interactive - ROOT 0,0..0,0''',
r'''"""non-doc"""; a; b''', r'''
Module - ROOT 0,0..0,19
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 0,15..0,16
     .value Name 'a' Load - 0,15..0,16
   2] Expr - 0,18..0,19
     .value Name 'b' Load - 0,18..0,19
'''),

('', 0, 'end', '_body', {}, ('FunctionDef', r'''
def f():
    """doc"""
    a
    b
'''), r'''
def f():
    """doc"""
''', r'''
FunctionDef - ROOT 0,0..1,13
  .name 'f'
  .body[1]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
''', r'''
a
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 0, 'end', '_body', {}, ('AsyncFunctionDef', r'''
async def f():
    """doc"""
    a
    b
'''), r'''
async def f():
    """doc"""
''', r'''
AsyncFunctionDef - ROOT 0,0..1,13
  .name 'f'
  .body[1]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
''', r'''
a
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 0, 'end', '_body', {}, ('ClassDef', r'''
class cls:
    """doc"""
    a
    b
'''), r'''
class cls:
    """doc"""
''', r'''
ClassDef - ROOT 0,0..1,13
  .name 'cls'
  .body[1]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
''', r'''
a
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('For', r'''
for _ in _:
    """non-doc"""
    a
    b
'''),
r'''for _ in _:''', r'''
For - ROOT 0,0..0,11
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('AsyncFor', r'''
async for _ in _:
    """non-doc"""
    a
    b
'''),
r'''async for _ in _:''', r'''
AsyncFor - ROOT 0,0..0,17
  .target Name '_' Store - 0,10..0,11
  .iter Name '_' Load - 0,15..0,16
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('While', r'''
while _:
    """non-doc"""
    a
    b
'''),
r'''while _:''', r'''
While - ROOT 0,0..0,8
  .test Name '_' Load - 0,6..0,7
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('If', r'''
if _:
    """non-doc"""
    a
    b
'''),
r'''if _:''', r'''
If - ROOT 0,0..0,5
  .test Name '_' Load - 0,3..0,4
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('With', r'''
with _:
    """non-doc"""
    a
    b
'''),
r'''with _:''', r'''
With - ROOT 0,0..0,7
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name '_' Load - 0,5..0,6
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('AsyncWith', r'''
async with _:
    """non-doc"""
    a
    b
'''),
r'''async with _:''', r'''
AsyncWith - ROOT 0,0..0,13
  .items[1]
   0] withitem - 0,11..0,12
     .context_expr Name '_' Load - 0,11..0,12
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('Try', r'''
try:
    """non-doc"""
    a
    b
except: pass
'''), r'''
try:
except: pass
''', r'''
Try - ROOT 0,0..1,12
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False, '_ver': 11}, ('TryStar', r'''
try:
    """non-doc"""
    a
    b
except* Exception: pass
'''), r'''
try:
except* Exception: pass
''', r'''
TryStar - ROOT 0,0..1,23
  .handlers[1]
   0] ExceptHandler - 1,0..1,23
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Pass - 1,19..1,23
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('ExceptHandler', r'''
except:
    """non-doc"""
    a
    b
'''),
r'''except:''',
r'''ExceptHandler - ROOT 0,0..0,7''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 'end', '_body', {'_verify': False}, ('match_case', r'''
case _:
    """non-doc"""
    a
    b
'''),
r'''case _:''', r'''
match_case - ROOT 0,0..0,7
  .pattern MatchAs - 0,5..0,6
''', r'''
"""non-doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,13
     .value Constant 'non-doc' - 0,0..0,13
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
'''),

('', 0, 0, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''',
r'''''',
r'''Module - ROOT 0,0..0,0'''),

('', 0, 1, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 2, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''"""doc"""''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
''', r'''
a
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 0, 3, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''"""doc"""''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
''', r'''
a
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 1, 0, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''**IndexError('start index must precede stop index')**'''),

('', 1, 1, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''',
r'''''',
r'''Module - ROOT 0,0..0,0'''),

('', 1, 2, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

('', 1, 3, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
''',
r'''b''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'b' Load - 0,0..0,1
'''),

('', 2, 3, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''',
r'''''',
r'''Module - ROOT 0,0..0,0'''),

('', 3, 3, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''',
r'''''',
r'''Module - ROOT 0,0..0,0'''),

('', 0, -1, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, -2, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''',
r'''''',
r'''Module - ROOT 0,0..0,0'''),

('', 0, -3, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
b
''', r'''
Module - ROOT 0,0..2,1
  .body[3]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
   2] Expr - 2,0..2,1
     .value Name 'b' Load - 2,0..2,1
''',
r'''''',
r'''Module - ROOT 0,0..0,0'''),

('', -2, -1, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', -3, -1, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', -3, 2, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''"""doc"""''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
''', r'''
a
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
'''),

('', 0, 1, '_body', {'trivia': False}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''), r'''
def f():
    """doc"""

    # pre-2

    # pre-1
''', r'''
FunctionDef - ROOT 0,0..1,13
  .name 'f'
  .body[1]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
''',
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 1, '_body', {'trivia': 'block'}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''), r'''
def f():
    """doc"""

    # pre-2

''', r'''
FunctionDef - ROOT 0,0..1,13
  .name 'f'
  .body[1]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
''', r'''
# pre-1
a
''', r'''
Module - ROOT 0,0..1,1
  .body[1]
   0] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
'''),

('', 0, 1, '_body', {'trivia': 'block+'}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''), r'''
def f():
    """doc"""

    # pre-2
''', r'''
FunctionDef - ROOT 0,0..1,13
  .name 'f'
  .body[1]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
''', r'''

# pre-1
a
''', r'''
Module - ROOT 0,0..2,1
  .body[1]
   0] Expr - 2,0..2,1
     .value Name 'a' Load - 2,0..2,1
'''),

('', 0, 1, '_body', {'trivia': 'all'}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''), r'''
def f():
    """doc"""

''', r'''
FunctionDef - ROOT 0,0..1,13
  .name 'f'
  .body[1]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
''', r'''
# pre-2

# pre-1
a
''', r'''
Module - ROOT 0,0..3,1
  .body[1]
   0] Expr - 3,0..3,1
     .value Name 'a' Load - 3,0..3,1
'''),

('', 0, 1, '_body', {'trivia': 'all+'}, ('FunctionDef', r'''
def f():
    """doc"""

    # pre-2

    # pre-1
    a
'''), r'''
def f():
    """doc"""
''', r'''
FunctionDef - ROOT 0,0..1,13
  .name 'f'
  .body[1]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
''', r'''

# pre-2

# pre-1
a
''', r'''
Module - ROOT 0,0..4,1
  .body[1]
   0] Expr - 4,0..4,1
     .value Name 'a' Load - 4,0..4,1
'''),
],

'misc': [  # ................................................................................

('', 1, 2, None, {'trivia': 'all'}, (None, r'''
[a
,
# 0
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
# 0
b]
''', r'''
List - ROOT 0,0..2,2
  .elts[1]
   0] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

('', 0, 1, None, {}, ('exec', r'''

if 1: pass
'''),
r'''''',
r'''Module - ROOT 0,0..0,0''',
r'''if 1: pass''', r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] If - 0,0..0,10
     .test Constant 1 - 0,3..0,4
     .body[1]
      0] Pass - 0,6..0,10
'''),
],

}
