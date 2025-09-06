DATA_PUT_SLICE = {
'old_stmtish': [  # ................................................................................

(0, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(1, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(2, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(3, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(4, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(5, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(6, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(7, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(8, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(9, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(10, 'body[0]', 1, 1, 'body', {}, ('exec',
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

(11, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(12, 'body[0]', 2, 2, 'body', {}, ('exec', r'''
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

(13, 'body[0]', 2, 2, 'body', {}, ('exec',
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

(14, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i
'''), (None,
r'''k'''), r'''
if 1:
    i
    k

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
'''),

(15, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
if 1:
    i  # post
'''), (None,
r'''k'''), r'''
if 1:
    i  # post
    k

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
'''),

(16, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(17, 'body[0]', 1, 1, 'body', {}, ('exec',
r'''if 1: i'''), (None,
r'''k'''), r'''
if 1:
    i
    k

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
'''),

(18, 'body[0]', 1, 1, 'body', {}, ('exec',
r'''if 1: i  # post'''), (None,
r'''k'''), r'''
if 1:
    i  # post
    k

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'k' Load - 2,4..2,5
'''),

(19, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(20, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(21, 'body[0]', 1, 1, 'body', {}, ('exec', r'''
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

(22, 'body[0]', 0, 0, 'body', {}, ('exec', r'''
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

(23, 'body[0]', 0, 0, 'body', {}, ('exec', r'''
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

(24, 'body[0]', 0, 0, 'body', {}, ('exec', r'''
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

(25, 'body[0]', 0, 0, 'body', {}, ('exec', r'''
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

(26, 'body[0]', 0, 0, 'body', {}, ('exec', r'''
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

(27, 'body[0]', 0, 0, 'body', {}, ('exec',
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

(28, 'body[0]', 0, 0, 'body', {}, ('exec', r'''
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

(29, 'body[0].body[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(30, 'body[0].body[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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

(31, 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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

(32, 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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
    # post-elif-continue-3
    # post-line
''', r'''
Module - ROOT 0,0..5,15
  .body[1]
  0] FunctionDef - 0,0..2,12
    .name 'f'
    .body[1]
    0] If - 1,4..2,12
      .test Constant 1 - 1,7..1,8
      .body[1]
      0] Pass - 2,8..2,12
'''),

(33, 'body[0].body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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
# post-elif-continue-3
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

(34, 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': True, 'pep8space': False}, ('exec', r'''
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

(35, 'body[0].body[0]', 0, 1, 'orelse', {'precomms': True, 'postcomms': True}, ('exec', r'''
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

(36, 'body[0].body[0].orelse[0]', 0, 1, 'orelse', {'precomms': 'all', 'postcomms': True, 'pep8space': False, 'prespace': True}, ('exec', r'''
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

(37, None, 0, 0, None, {}, ('exec',
r''''''), (None,
r'''i'''), r'''
i

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
'''),

(38, None, 0, 0, None, {}, ('exec',
r''''''), (None,
r'''i'''), r'''
i

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
'''),

(39, None, 0, 0, None, {}, ('exec',
r''''''), (None,
r'''i'''), r'''
i

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
'''),

(40, None, 0, 0, None, {}, ('exec',
r'''# comment'''), (None,
r'''i'''), r'''
# comment
i

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
  0] Expr - 1,0..1,1
    .value Name 'i' Load - 1,0..1,1
'''),

(41, None, 0, 0, None, {}, ('exec', r'''
# comment

# another comment
'''), (None,
r'''i'''), r'''
# comment

# another comment
i

''', r'''
Module - ROOT 0,0..4,0
  .body[1]
  0] Expr - 3,0..3,1
    .value Name 'i' Load - 3,0..3,1
'''),

(42, None, 0, 0, None, {}, ('exec', r'''
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

(43, None, 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 3,0..3,1
    .value Name 'i' Load - 3,0..3,1
  1] Expr - 4,0..4,1
    .value Name 'j' Load - 4,0..4,1
'''),

(44, 'body[0].body[0]', 0, 0, 'orelse', {}, ('exec', r'''
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

(45, 'body[0].body[0]', 1, 1, 'orelse', {}, ('exec', r'''
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
Module - ROOT 0,0..5,0
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

(46, 'body[0].body[0]', 0, 0, 'orelse', {}, ('exec', r'''
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

(47, 'body[0].body[0]', 1, 1, 'orelse', {}, ('exec', r'''
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
Module - ROOT 0,0..6,0
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

(48, 'body[0].body[0]', 0, 0, 'orelse', {}, ('exec', r'''
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

(49, 'body[0].body[0]', 1, 1, 'orelse', {}, ('exec', r'''
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
Module - ROOT 0,0..6,0
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

(50, 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {}, ('exec', r'''
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

(51, 'body[0].body[0].orelse[0]', 1, 1, 'orelse', {}, ('exec', r'''
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
Module - ROOT 0,0..6,0
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

(52, 'body[0]', 0, 0, None, {}, ('exec', r'''
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

(53, 'body[0]', 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..3,0
  .body[1]
  0] FunctionDef - 0,0..1,5
    .name 'f'
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
'''),

(54, 'body[0]', 0, 0, None, {}, ('exec', r'''
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

(55, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(56, 'body[0]', 2, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..3,0
  .body[1]
  0] FunctionDef - 0,0..1,9
    .name 'f'
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 1,8..1,9
      .value Name 'j' Load - 1,8..1,9
'''),

(57, 'body[0]', 0, 0, None, {}, ('exec', r'''
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

(58, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(59, 'body[0]', 2, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..6,0
  .body[1]
  0] FunctionDef - 0,0..4,3
    .name 'f'
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 4,2..4,3
      .value Name 'j' Load - 4,2..4,3
'''),

(60, '', 0, 0, None, {'pep8space': True}, ('exec',
r''''''), (None,
r'''def func(): pass'''), r'''
def func(): pass

''', r'''
def func():
    pass

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] FunctionDef - 0,0..0,16
    .name 'func'
    .body[1]
    0] Pass - 0,12..0,16
'''),

(61, '', 0, 0, None, {'pep8space': True}, ('exec',
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

(62, '', 1, 1, None, {'pep8space': True}, ('exec', r'''
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
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..1,15
    .value Constant 'Module\n   docstring' - 0,0..1,15
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
'''),

(63, '', 1, 1, None, {'pep8space': True}, ('exec', r'''
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
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..1,15
    .value Constant 'Module\n   docstring' - 0,0..1,15
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
'''),

(64, '', 1, 1, None, {'pep8space': True}, ('exec', r'''
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
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..1,15
    .value Constant 'Module\n   docstring' - 0,0..1,15
  1] FunctionDef - 3,0..3,16
    .name 'func'
    .body[1]
    0] Pass - 3,12..3,16
'''),

(65, '', 1, 1, None, {'pep8space': True}, ('exec', r'''
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
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 0,0..1,15
    .value Constant 'Module\n   docstring' - 0,0..1,15
  1] FunctionDef - 4,0..4,16
    .name 'func'
    .body[1]
    0] Pass - 4,12..4,16
'''),

(66, '', 1, 1, None, {'pep8space': True}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass

''', r'''
def prefunc(): pass


def func():
    pass

''', r'''
Module - ROOT 0,0..4,0
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

(67, '', 1, 1, None, {'pep8space': 1}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass

def func(): pass

''', r'''
def prefunc(): pass

def func():
    pass

''', r'''
Module - ROOT 0,0..3,0
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

(68, '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass
def func(): pass

''', r'''
def prefunc(): pass
def func():
    pass

''', r'''
Module - ROOT 0,0..2,0
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

(69, '', 1, 1, None, {'pep8space': True}, ('exec',
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
Module - ROOT 0,0..4,0
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

(70, '', 1, 1, None, {'pep8space': 1}, ('exec',
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
Module - ROOT 0,0..3,0
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

(71, '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass
def func(): pass

''', r'''
def prefunc(): pass
def func():
    pass

''', r'''
Module - ROOT 0,0..2,0
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

(72, '', 1, 1, None, {'pep8space': True}, ('exec',
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
Module - ROOT 0,0..4,0
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

(73, '', 1, 1, None, {'pep8space': 1}, ('exec',
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
Module - ROOT 0,0..4,0
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

(74, '', 1, 1, None, {'pep8space': True}, ('exec',
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
Module - ROOT 0,0..5,0
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

(75, '', 1, 1, None, {'pep8space': True}, ('exec',
r'''import stuff'''), (None,
r'''def func(): pass'''), r'''
import stuff


def func(): pass

''', r'''
import stuff


def func():
    pass

''', r'''
Module - ROOT 0,0..4,0
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

(76, '', 1, 1, None, {'pep8space': True}, ('exec',
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
Module - ROOT 0,0..4,0
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

(77, '', 1, 1, None, {'pep8space': True}, ('exec',
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
Module - ROOT 0,0..4,0
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

(78, '', 1, 1, None, {'pep8space': True}, ('exec',
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
Module - ROOT 0,0..4,0
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

(79, '', 0, 0, None, {}, ('exec',
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

(80, '', 0, 0, None, {'pep8space': 1}, ('exec',
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

(81, '', 0, 0, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec',
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

(82, '', 0, 0, None, {}, ('exec',
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

(83, '', 0, 0, None, {}, ('exec',
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

(84, '', 0, 0, None, {}, ('exec',
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

(85, '', 0, 0, None, {}, ('exec',
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

(86, '', 1, 1, None, {}, ('exec', r'''
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

(87, '', 1, 1, None, {}, ('exec', r'''
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

(88, '', 1, 1, None, {}, ('exec', r'''
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

(89, '', 1, 1, None, {}, ('exec', r'''
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

(90, '', 1, 1, None, {}, ('exec', r'''
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

(91, '', 1, 1, None, {'pep8space': 1}, ('exec', r'''
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

(92, '', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(93, '', 1, 1, None, {}, ('exec', r'''
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

(94, '', 1, 1, None, {}, ('exec', r'''
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

(95, 'body[0]', 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..5,0
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

(96, 'body[0]', 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..5,0
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

(97, 'body[0]', 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..6,0
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

(98, 'body[0]', 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(99, 'body[0]', 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(100, 'body[0]', 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..5,0
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

(101, 'body[0]', 0, 0, None, {}, ('exec', r'''
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

(102, 'body[0]', 0, 0, None, {}, ('exec', r'''
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

(103, 'body[0]', 0, 0, None, {}, ('exec', r'''
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

(104, 'body[0]', 0, 0, None, {}, ('exec', r'''
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

(105, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(106, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(107, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(108, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(109, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(110, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(111, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(112, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(113, 'body[0]', 1, 2, None, {'precomms': False}, ('exec', r'''
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

(114, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(115, '', 1, 1, None, {}, ('exec', r'''
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

(116, '', 1, 2, None, {}, ('exec', r'''
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

(117, '', 1, 2, None, {}, ('exec', r'''
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

(118, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(119, '', 1, 2, None, {}, ('exec', r'''
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

(120, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(121, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(122, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(123, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(124, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(125, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(126, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(127, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(128, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(129, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(130, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(131, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(132, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(133, '', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(134, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(135, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(136, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(137, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(138, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(139, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(140, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(141, 'body[0]', 1, 2, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(142, '', 0, 1, None, {}, ('exec',
r'''i'''), (None,
r'''l'''), r'''
l

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(143, '', 0, 1, None, {}, ('exec', r'''
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

(144, '', 1, 2, None, {}, ('exec', r'''
i
j
'''), (None,
r'''l'''), r'''
i
l

''', r'''
Module - ROOT 0,0..2,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
'''),

(145, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i
'''), (None,
r'''l'''), r'''
if 1:
    l

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(146, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(147, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i
    j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
'''),

(148, '', 1, 2, None, {}, ('exec', r'''
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

(149, '', 1, 2, None, {}, ('exec', r'''
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

(150, '', 1, 2, None, {}, ('exec', r'''
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

(151, '', 1, 2, None, {}, ('exec', r'''
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

(152, '', 1, 2, None, {}, ('exec', r'''
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

(153, '', 1, 2, None, {}, ('exec', r'''
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

(154, '', 1, 2, None, {}, ('exec', r'''
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

(155, '', 1, 2, None, {}, ('exec', r'''
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

(156, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(157, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(158, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(159, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(160, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(161, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(162, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(163, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(164, '', 1, 2, None, {}, ('exec',
r'''i ; j'''), (None,
r'''l'''), r'''
i
l

''', r'''
Module - ROOT 0,0..2,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
'''),

(165, '', 1, 2, None, {}, ('exec', r'''
i \
 ; j
'''), (None,
r'''l'''), r'''
i
l

''', r'''
Module - ROOT 0,0..2,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
'''),

(166, '', 1, 2, None, {}, ('exec', r'''
i ; \
 j
'''), (None,
r'''l'''), r'''
i
l

''', r'''
Module - ROOT 0,0..2,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
'''),

(167, '', 1, 2, None, {}, ('exec', r'''
i \
; \
j
'''), (None,
r'''l'''), r'''
i
l

''', r'''
Module - ROOT 0,0..2,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] Expr - 1,0..1,1
    .value Name 'l' Load - 1,0..1,1
'''),

(168, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i ; j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
'''),

(169, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i \
    ; j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
'''),

(170, 'body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
    i ; \
    j
'''), (None,
r'''l'''), r'''
if 1:
    i
    l

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
'''),

(171, 'body[0]', 1, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,5
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Expr - 1,4..1,5
      .value Name 'i' Load - 1,4..1,5
    1] Expr - 2,4..2,5
      .value Name 'l' Load - 2,4..2,5
'''),

(172, '', 0, 1, None, {}, ('exec',
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

(173, '', 0, 1, None, {}, ('exec', r'''
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

(174, '', 0, 1, None, {}, ('exec', r'''
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

(175, '', 0, 1, None, {}, ('exec', r'''
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

(176, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(177, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(178, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(179, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(180, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(181, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(182, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(183, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(184, '', 0, 1, None, {}, ('exec',
r'''i ;'''), (None,
r'''l'''), r'''
l

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(185, '', 0, 1, None, {}, ('exec',
r'''i ;  # post'''), (None,
r'''l'''), r'''
l
# post
''', r'''
Module - ROOT 0,0..1,6
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(186, '', 0, 1, None, {}, ('exec', r'''
i ; \
 # post
'''), (None,
r'''l'''), r'''
l

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(187, '', 0, 1, None, {}, ('exec', r'''
i \
 ; \
 # post
'''), (None,
r'''l'''), r'''
l

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(188, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i ;
'''), (None,
r'''l'''), r'''
if 1:
    l

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(189, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i ;  # post
'''), (None,
r'''l'''), r'''
if 1:
    l
    # post
''', r'''
Module - ROOT 0,0..2,10
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(190, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i ; \
 # post
'''), (None,
r'''l'''), r'''
if 1:
    l

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(191, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    i \
 ; \
 # post
'''), (None,
r'''l'''), r'''
if 1:
    l

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(192, '', 0, 1, None, {}, ('exec', r'''
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

(193, '', 0, 1, None, {}, ('exec', r'''
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

(194, 'body[0]', 0, 1, 'orelse', {}, ('exec', r'''
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

(195, 'body[0]', 0, 1, 'orelse', {}, ('exec', r'''
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

(196, 'body[0]', 1, 2, 'orelse', {}, ('exec', r'''
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

(197, 'body[0]', 0, 1, 'orelse', {}, ('exec', r'''
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

(198, '', 0, 1, None, {}, ('exec', r'''
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

(199, '', 0, 1, None, {}, ('exec', r'''
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

(200, '', 0, 1, None, {}, ('exec', r'''
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

(201, '', 0, 1, None, {}, ('exec', r'''
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

(202, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(203, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(204, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(205, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(206, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(207, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(208, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(209, 'body[0]', 0, 1, None, {}, ('exec', r'''
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

(210, '', 0, 1, None, {}, ('exec', r'''
# pre
i ;
'''), (None,
r'''l'''), r'''
l

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(211, '', 0, 1, None, {}, ('exec', r'''
# pre
i ;  # post
'''), (None,
r'''l'''), r'''
l
# post
''', r'''
Module - ROOT 0,0..1,6
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(212, '', 0, 1, None, {}, ('exec', r'''
# pre
i ; \
 # post
'''), (None,
r'''l'''), r'''
l

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(213, '', 0, 1, None, {}, ('exec', r'''
# pre
i \
 ; \
 # post
'''), (None,
r'''l'''), r'''
l

''', r'''
Module - ROOT 0,0..1,0
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'l' Load - 0,0..0,1
'''),

(214, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i ;
'''), (None,
r'''l'''), r'''
if 1:
    l

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(215, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i ;  # post
'''), (None,
r'''l'''), r'''
if 1:
    l
# post
''', r'''
Module - ROOT 0,0..2,6
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(216, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i ; \
 # post
'''), (None,
r'''l'''), r'''
if 1:
    l

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(217, 'body[0]', 0, 1, None, {}, ('exec', r'''
if 1:
    # pre
    i \
 ; \
 # post
'''), (None,
r'''l'''), r'''
if 1:
    l

''', r'''
Module - ROOT 0,0..2,0
  .body[1]
  0] If - 0,0..1,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Expr - 1,4..1,5
      .value Name 'l' Load - 1,4..1,5
'''),

(218, '', 1, 2, None, {}, ('exec', r'''
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

(219, '', 1, 2, None, {}, ('exec', r'''
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

(220, '', 1, 2, None, {}, ('exec', r'''
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

(221, '', 2, 3, None, {}, ('exec', r'''
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

(222, '', 1, 2, None, {}, ('exec', r'''
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

(223, '', 2, 3, None, {}, ('exec', r'''
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

(224, '', 1, 1, None, {}, ('exec',
r'''def prefunc(): pass'''), (None,
r'''def func(): pass'''), r'''
def prefunc(): pass


def func(): pass

''', r'''
def prefunc(): pass


def func():
    pass

''', r'''
Module - ROOT 0,0..4,0
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

(225, '', 0, 0, None, {}, ('exec',
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

(226, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(227, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(228, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(229, 'body[0]', 2, 3, None, {}, ('exec', r'''
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

(230, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(231, 'body[0]', 2, 3, None, {}, ('exec', r'''
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

(232, 'body[0]', 1, 1, None, {}, ('exec', r'''
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
Module - ROOT 0,0..5,0
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

(233, 'body[0]', 0, 0, None, {}, ('exec', r'''
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

(234, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(235, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(236, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(237, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(238, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(239, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(240, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(241, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(242, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(243, 'body[0].cases[0]', 1, 1, None, {}, ('exec', r'''
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

(244, 'body[0]', 1, 1, None, {}, ('exec', r'''
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

(245, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(246, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(247, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(248, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(249, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(250, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(251, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(252, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(253, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(254, 'body[0].cases[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(255, 'body[0]', 1, 1, None, {'precomms': False, 'postcomms': False, 'pep8space': False}, ('exec', r'''
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

(256, 'body[0]', 1, 1, None, {'pep8space': 1}, ('exec', r'''
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

(257, '', 1, 2, None, {}, ('exec',
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

(258, '', 1, 2, None, {}, ('exec', r'''
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

(259, '', 1, 2, None, {}, ('exec', r'''
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

(260, '', 1, 2, None, {}, ('exec', r'''
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

(261, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(262, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(263, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(264, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(265, '', 1, 2, None, {}, ('exec',
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

(266, '', 1, 2, None, {}, ('exec', r'''
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

(267, '', 1, 2, None, {}, ('exec', r'''
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

(268, '', 1, 2, None, {}, ('exec', r'''
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

(269, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(270, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(271, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(272, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(273, '', 1, 2, None, {}, ('exec',
r'''i ; j ;'''), (None,
r'''def f(): pass'''), r'''
i


def f(): pass

''', r'''
i


def f():
    pass

''', r'''
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] FunctionDef - 3,0..3,13
    .name 'f'
    .body[1]
    0] Pass - 3,9..3,13
'''),

(274, '', 1, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] FunctionDef - 3,0..3,13
    .name 'f'
    .body[1]
    0] Pass - 3,9..3,13
'''),

(275, '', 1, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..4,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] FunctionDef - 3,0..3,13
    .name 'f'
    .body[1]
    0] Pass - 3,9..3,13
'''),

(276, '', 1, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..5,0
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
'''),

(277, 'body[0]', 1, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(278, 'body[0]', 1, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(279, 'body[0]', 1, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(280, 'body[0]', 1, 2, None, {}, ('exec', r'''
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
Module - ROOT 0,0..5,0
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

(281, '', 1, 2, None, {}, ('exec',
r'''i ; j ;  # post'''), (None,
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
Module - ROOT 0,0..4,6
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] FunctionDef - 3,0..3,13
    .name 'f'
    .body[1]
    0] Pass - 3,9..3,13
'''),

(282, '', 1, 2, None, {}, ('exec', r'''
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

(283, '', 1, 2, None, {}, ('exec', r'''
i \
 ; j ;  # post
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
Module - ROOT 0,0..5,6
  .body[2]
  0] Expr - 0,0..0,1
    .value Name 'i' Load - 0,0..0,1
  1] FunctionDef - 4,0..4,13
    .name 'f'
    .body[1]
    0] Pass - 4,9..4,13
'''),

(284, '', 1, 2, None, {}, ('exec', r'''
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

(285, 'body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i ; j ;  # post
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i ;

    def f(): pass
# post
''', r'''
class cls:
    i ;

    def f():
        pass
# post
''', r'''
Module - ROOT 0,0..4,6
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

(286, 'body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i ; \
 j ;  # post
'''), (None,
r'''def f(): pass'''), r'''
class cls:
    i ;

    def f(): pass
 # post
''', r'''
class cls:
    i ;

    def f():
        pass
 # post
''', r'''
Module - ROOT 0,0..4,7
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

(287, 'body[0]', 1, 2, None, {}, ('exec', r'''
class cls:
    i \
 ; j ;  # post
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
Module - ROOT 0,0..5,6
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

(288, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(289, 'body[0]', 0, 1, 'orelse', {}, ('exec', r'''
if 1: pass
elif 2:
    pass
'''), (None,
r'''break'''), r'''
if 1: pass
else:
    break

''', r'''
Module - ROOT 0,0..3,0
  .body[1]
  0] If - 0,0..2,9
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Pass - 0,6..0,10
    .orelse[1]
    0] Break - 2,4..2,9
'''),

(290, 'body[0]', 0, 1, 'orelse', {'elif_': False}, ('exec', r'''
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
Module - ROOT 0,0..3,0
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

(291, 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..2,0
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

(292, 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..2,0
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

(293, 'body[0].body[0]', 0, 1, 'orelse', {}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(294, 'body[0].body[0]', 0, 1, 'orelse', {'elif_': False}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(295, 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..3,0
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

(296, 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..3,0
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

(297, 'body[0]', 0, 1, 'orelse', {'elif_': False}, ('exec', r'''
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
Module - ROOT 0,0..5,0
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

(298, 'body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..4,0
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

(299, 'body[0].orelse[0]', 0, 0, 'orelse', {'elif_': False}, ('exec', r'''
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
Module - ROOT 0,0..7,0
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

(300, 'body[0].orelse[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..6,0
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

(301, 'body[0].body[0]', 0, 1, 'orelse', {'elif_': False}, ('exec', r'''
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
Module - ROOT 0,0..6,0
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

(302, 'body[0].body[0]', 0, 1, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..5,0
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

(303, 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {'elif_': False}, ('exec', r'''
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
Module - ROOT 0,0..8,0
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

(304, 'body[0].body[0].orelse[0]', 0, 0, 'orelse', {'precomms': False, 'postcomms': False, 'pep8space': False, 'elif_': True}, ('exec', r'''
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
Module - ROOT 0,0..7,0
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

(305, 'body[0]', 0, 0, 'orelse', {}, ('exec', r'''
if 1:
    pass;
'''), (None,
r'''i'''), r'''
if 1:
    pass;
else:
    i

''', r'''
Module - ROOT 0,0..4,0
  .body[1]
  0] If - 0,0..3,5
    .test Constant 1 - 0,3..0,4
    .body[1]
    0] Pass - 1,4..1,8
    .orelse[1]
    0] Expr - 3,4..3,5
      .value Name 'i' Load - 3,4..3,5
'''),

(306, 'body[0]', 0, 0, 'orelse', {}, ('exec', r'''
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

'old_exprish': [  # ................................................................................

(0, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(1, 'body[0].value', 0, 2, None, {}, ('exec',
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

(2, 'body[0].body[0].value', 0, 2, None, {}, ('exec', r'''
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

(3, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(4, 'body[0].value', 0, 1, None, {}, ('exec',
r'''{a: 1}'''), (None,
r'''{}'''),
r'''{}''', r'''
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Dict - 0,0..0,2
'''),

(5, 'body[0].value', 0, 1, None, {}, ('exec',
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

(6, 'body[0].value', 1, 2, None, {}, ('exec',
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

(7, 'body[0].value', 1, 2, None, {}, ('exec',
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

(8, 'body[0].value', 0, 2, None, {}, ('exec',
r'''1, 2'''), (None,
r'''()'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
'''),

(9, 'body[0].value', 1, 2, None, {}, ('exec',
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

(10, 'body[0].value', 1, 2, None, {}, ('exec',
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

(11, 'body[0].value', 0, 2, None, {}, ('exec',
r'''1, 2'''), (None,
r'''{*()}'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
'''),

(12, 'body[0].value', 0, 2, None, {}, ('exec', r'''
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

(13, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(14, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(15, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(16, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(17, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(18, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(19, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(20, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(21, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(22, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(23, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(24, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(25, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(26, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(27, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(28, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(29, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(30, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(31, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(32, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(33, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(34, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(35, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(36, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(37, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(38, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(39, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(40, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(41, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(42, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(43, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(44, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(45, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(46, 'body[0].value', 0, 1, None, {}, ('exec', r'''
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

(47, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(48, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(49, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(50, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(51, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(52, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(53, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(54, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(55, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(56, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(57, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(58, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(59, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(60, 'body[0].value', 2, 3, None, {}, ('exec', r'''
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

(61, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(62, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(63, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(64, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(65, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(66, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(67, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(68, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(69, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(70, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(71, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(72, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(73, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(74, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(75, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(76, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(77, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(78, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(79, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(80, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(81, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(82, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(83, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(84, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(85, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(86, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(87, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(88, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(89, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(90, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(91, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(92, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(93, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(94, 'body[0].value', 0, 0, None, {}, ('exec', r'''
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

(95, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(96, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(97, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(98, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(99, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(100, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(101, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(102, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(103, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(104, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(105, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(106, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(107, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(108, 'body[0].value', 2, 2, None, {}, ('exec', r'''
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

(109, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(110, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(111, 'body[0].value', 1, 1, None, {}, ('exec', r'''
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

(112, 'body[0].value', 2, 3, None, {}, ('exec',
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

(113, 'body[0].targets[0]', 2, 2, None, {}, ('exec',
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

(114, 'body[0].value', 0, 1, None, {}, ('exec',
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

(115, 'body[0].iter', 1, 2, None, {}, ('exec', r'''
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

(116, 'body[0].value', 0, 0, None, {}, ('exec',
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

(117, 'body[0].value', 0, 2, None, {}, ('exec',
r'''return (user if delim else None), host'''), (None,
r'''()'''),
r'''return ()''', r'''
Module - ROOT 0,0..0,9
  .body[1]
  0] Return - 0,0..0,9
    .value Tuple - 0,7..0,9
      .ctx Load
'''),

(118, 'body[0].value', 0, 2, None, {}, ('exec',
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

(119, 'body[0].value', 0, 0, None, {}, ('exec',
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

(120, 'body[0].value', 0, 0, None, {}, ('exec',
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

(121, 'body[0].value', 0, 0, None, {}, ('exec',
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

(122, 'body[0].value', 1, 1, None, {}, ('exec',
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

(123, 'body[0].value', 2, 2, None, {}, ('exec',
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

(124, 'body[0].value', 3, 3, None, {}, ('exec',
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

(125, 'body[0].value', 0, 1, None, {}, ('exec',
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

(126, 'body[0].value', 1, 2, None, {}, ('exec',
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

(127, 'body[0].value', 2, 3, None, {}, ('exec',
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

(128, 'body[0].value', 0, 2, None, {}, ('exec',
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

(129, 'body[0].value', 1, 3, None, {}, ('exec',
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

(130, 'body[0].value', 0, 3, None, {}, ('exec',
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

(131, 'body[0].value', 0, 2, None, {}, ('exec', r'''
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

(132, 'body[0].value', 0, 0, None, {}, ('exec',
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

(133, 'body[0].value', 1, 1, None, {}, ('exec',
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

(134, 'body[0].value', 2, 2, None, {}, ('exec',
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

(135, 'body[0].value', 3, 3, None, {}, ('exec',
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

(136, 'body[0].value', 0, 1, None, {}, ('exec',
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

(137, 'body[0].value', 1, 2, None, {}, ('exec',
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

(138, 'body[0].value', 2, 3, None, {}, ('exec',
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

(139, 'body[0].value', 0, 2, None, {}, ('exec',
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

(140, 'body[0].value', 1, 3, None, {}, ('exec',
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

(141, 'body[0].value', 0, 3, None, {}, ('exec',
r'''1, 2, 3,'''), (None,
r'''**DEL**'''),
r'''()''', r'''
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Tuple - 0,0..0,2
      .ctx Load
'''),

(142, 'body[0].body[0].value.elts[1]', 1, 2, None, {}, ('exec', r'''
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

(143, 'body[0].body[0].value.elts[1]', 2, 3, None, {}, ('exec', r'''
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

(144, 'body[0].body[0].value.elts[1]', 0, 2, None, {}, ('exec', r'''
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

(145, 'body[0].body[0].value.elts[1]', 0, 3, None, {}, ('exec', r'''
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

(146, 'body[0].body[0].value.elts[1]', 0, 3, None, {}, ('exec', r'''
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

(147, 'body[0].body[0].value.elts[1]', 1, 3, None, {}, ('exec', r'''
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

(148, 'body[0].body[0].value.elts[1]', 1, 2, None, {}, ('exec', r'''
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

(149, 'body[0].body[0].value.elts[1]', 2, 3, None, {}, ('exec', r'''
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

(150, 'body[0].body[0].value.elts[1]', 0, 2, None, {}, ('exec', r'''
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

(151, 'body[0].body[0].value.elts[1]', 0, 3, None, {}, ('exec', r'''
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

(152, 'body[0].body[0].value.elts[1]', 0, 3, None, {}, ('exec', r'''
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

(153, 'body[0].body[0].value.elts[1]', 1, 3, None, {}, ('exec', r'''
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

(154, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(155, 'body[0].value', 1, 2, None, {}, ('exec', r'''
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

(156, 'body[0].value.slice', 1, 2, None, {}, ('exec',
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

(157, 'body[0].cases[0].pattern.patterns[0].patterns[0].patterns[0].patterns[0].pattern', 0, 2, None, {}, ('exec', r'''
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

(0, 'body[0].value', 1, 2, None, {'raw': True}, ('exec',
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

(1, 'body[0].value', 0, 3, None, {'raw': True}, ('exec',
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

(2, 'body[0].value', 1, 2, None, {'raw': True}, ('exec',
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

(3, 'body[0].value', 0, 3, None, {'raw': True}, ('exec',
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

(4, 'body[0].value', 1, 2, None, {'raw': True}, ('exec',
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

(5, 'body[0].value', 0, 3, None, {'raw': True}, ('exec',
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

(6, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(7, 'body[0]', 1, 3, None, {'raw': True}, ('exec',
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

(8, 'body[0]', 1, 3, 'targets', {'raw': True}, ('exec',
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

(9, 'body[0]', 1, 3, None, {'raw': True}, ('exec',
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
      .asname
        'xyz'
'''),

(10, 'body[0]', 1, 3, None, {'raw': True}, ('exec',
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
      .asname
        'xyz'
    .level 0
'''),

(11, 'body[0]', 1, 3, 'items', {'raw': True}, ('exec',
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

(12, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(13, 'body[0].value', 1, 4, None, {'raw': True}, ('exec',
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

(14, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(15, 'body[0].value.generators[0]', 1, 3, None, {'raw': True}, ('exec',
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

(16, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(17, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(18, 'body[0]', 1, 3, 'decorator_list', {'raw': True}, ('exec', r'''
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

(19, 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, ('exec', r'''
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

(20, 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, ('exec', r'''
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

(21, 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, ('exec', r'''
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

(22, 'body[0].args', 0, 1, 'args', {'raw': True}, ('exec',
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

(23, 'body[0].args', 0, 1, 'args', {'raw': True}, ('exec',
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

(24, 'body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
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

(25, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(26, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(27, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(28, 'body[0].cases[0].pattern', 1, 3, None, {'raw': True}, ('exec', r'''
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

(29, 'body[0].value.generators[0]', 1, 3, None, {'raw': True}, ('exec',
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

(30, 'body[0]', 1, 3, 'decorator_list', {'raw': True}, ('exec', r'''
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

(31, 'body[0].value', 1, 3, None, {'raw': True}, ('exec',
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

(32, 'body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
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

(33, 'body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
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

(34, 'body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
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

(35, 'body[0].value', 0, 1, 'args', {'raw': True}, ('exec',
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

(36, 'body[0].value', 0, 2, 'args', {'raw': True}, ('exec',
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

(37, 'body[0]', 0, 2, None, {'raw': True}, ('exec',
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

(38, 'body[0]', None, None, None, {'raw': True}, ('exec',
r'''global a, b, c'''), (None,
r'''x'''),
r'''global x''', r'''
Module - ROOT 0,0..0,8
  .body[1]
  0] Global - 0,0..0,8
    .names[1]
    0] 'x'
'''),

(39, 'body[0]', 1, 2, None, {'raw': True}, ('exec',
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

(40, 'body[0]', 0, 2, None, {'raw': True}, ('exec',
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

(41, 'body[0]', None, None, None, {'raw': True}, ('exec',
r'''nonlocal a, b, c'''), (None,
r'''x'''),
r'''nonlocal x''', r'''
Module - ROOT 0,0..0,10
  .body[1]
  0] Nonlocal - 0,0..0,10
    .names[1]
    0] 'x'
'''),

(42, 'body[0]', 1, 2, None, {'raw': True}, ('exec',
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

(43, 'body[0].value', 1, 1, None, {'trivia': (None, False)}, ('exec', r'''
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

(44, 'body[0].value', 1, 1, None, {'trivia': (None, False)}, ('exec', r'''
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

(45, 'body[0].value', 1, 1, None, {'trivia': (None, False)}, ('exec', r'''
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

(46, 'body[0].value', 1, 1, None, {'trivia': (None, False)}, ('exec', r'''
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

(47, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(48, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(49, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(50, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(51, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(52, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(53, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(54, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(55, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(56, 'body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(57, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(58, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(59, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(60, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(61, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(62, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(63, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(64, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(65, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(66, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(67, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(68, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(69, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(70, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(71, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(72, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(73, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(74, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(75, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(76, 'body[0].body[0].value', 0, 0, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(77, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(78, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(79, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(80, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(81, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(82, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(83, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(84, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(85, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(86, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(87, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 0}, ('exec', r'''
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

(88, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 1}, ('exec', r'''
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

(89, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 2}, ('exec', r'''
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

(90, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 3}, ('exec', r'''
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

(91, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(92, 'body[0].body[0].value', 1, 1, None, {'trivia': (False, False), 'ins_ln': 4}, ('exec', r'''
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

(93, 'body[0].cases[0].pattern', 0, 1, None, {'fix_matchor_self': False, '_verify': False}, ('exec', r'''
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

(94, 'body[0].cases[0].pattern', 0, 2, None, {'fix_matchor_self': False, '_verify': False}, ('exec', r'''
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

(95, 'body[0].cases[0].pattern', 0, 1, None, {'fix_matchor_self': True, '_verify': False}, ('exec', r'''
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

(96, 'body[0].cases[0].pattern', 0, 2, None, {'fix_matchor_self': True, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), (None,
r'''**DEL**'''),
r'''**NodeError('cannot del MatchOr to empty without fix_matchor_self=False')**'''),

(97, 'body[0].cases[0].pattern', 0, 1, None, {'fix_matchor_self': False, '_verify': False}, ('exec', r'''
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

(98, 'body[0].cases[0].pattern', 0, 2, None, {'fix_matchor_self': False, '_verify': False}, ('exec', r'''
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

(99, 'body[0].cases[0].pattern', 0, 1, None, {'fix_matchor_self': True, '_verify': False}, ('exec', r'''
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

(100, 'body[0].cases[0].pattern', 0, 2, None, {'fix_matchor_self': True, '_verify': False}, ('exec', r'''
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

(101, 'body[0].cases[0].pattern', 0, 1, None, {'fix_matchor_self': 'strict', '_verify': False}, ('exec', r'''
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

(102, 'body[0].cases[0].pattern', 0, 1, None, {'fix_matchor_put': False, '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), ('pattern',
r'''z'''),
r'''**NodeError('slice being assigned to a MatchOr must be a MatchOr with fix_matchor_put=False, not a MatchAs')**'''),

(103, 'body[0].cases[0].pattern', 0, 2, None, {'fix_matchor_self': 'strict', '_verify': False}, ('exec', r'''
match a:
 case a | b: pass
'''), ('pattern',
r'''z'''),
r'''**NodeError("cannot put MatchOr to length 1 with fix_matchor_self='strict'")**'''),

(104, 'body[0].body[0].value', 'end', None, None, {'one': True}, ('exec', r'''
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

(105, 'body[0].body[0].value', 1, 1, None, {'one': True}, ('exec', r'''
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

(106, 'body[0].value.slice', 2, 2, None, {}, ('exec',
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

(107, 'body[0].value.slice', 2, 2, None, {'one': True}, ('exec',
r'''a[b:c:d, e:f:g]'''), (None,
r'''x:y:z,'''),
r'''**NodeError('cannot put tuple with Slices to tuple')**'''),

(108, 'body[0]', 0, 3, 'type_params', {'_ver': 13}, ('exec',
r'''def f[T, *U, **V](): pass'''), ('type_params',
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

(109, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
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

(110, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''def f(): pass'''), ('type_params',
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

(111, 'body[0]', 0, 3, 'type_params', {'_ver': 13}, ('exec',
r'''async def f[T, *U, **V](): pass'''), ('type_params',
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

(112, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
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

(113, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''async def f(): pass'''), ('type_params',
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

(114, 'body[0]', 0, 3, 'type_params', {'_ver': 13}, ('exec',
r'''class cls[T, *U, **V]: pass'''), ('type_params',
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

(115, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
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

(116, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''class cls: pass'''), ('type_params',
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

(117, 'body[0]', 0, 3, 'type_params', {'_ver': 13}, ('exec',
r'''type t[T, *U, **V] = ...'''), ('type_params',
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

(118, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T, *U, **V] = ...'''), (None,
r'''**DEL**'''),
r'''type t = ...''', r'''
Module - ROOT 0,0..0,12
  .body[1]
  0] TypeAlias - 0,0..0,12
    .name Name 't' Store - 0,5..0,6
    .value Constant Ellipsis - 0,9..0,12
'''),

(119, 'body[0]', 0, 3, 'type_params', {'_ver': 12}, ('exec',
r'''type t = ...'''), ('type_params',
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

(120, 'body[0]', 0, 0, 'type_params', {'_ver': 12}, ('exec',
r'''type t[**V]=...'''), ('type_params',
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

(121, 'body[0]', 1, 1, 'type_params', {'_ver': 12}, ('exec',
r'''type t[**V]=...'''), ('type_params',
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

(122, 'body[0]', 0, 3, 'type_params', {'_ver': 13, 'one': True}, ('exec',
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

(123, 'body[0]', 0, 3, 'type_params', {'_ver': 12, 'one': True}, ('exec',
r'''type t[T, *U, **V] = ...'''), (None,
r'''T, *U'''),
r'''**ParseError('expecting single type_param')**'''),

(124, 'body[0]', 0, 3, 'type_params', {'_ver': 12, 'one': True}, ('exec',
r'''type t[T, *U, **V] = ...'''), (None,
r'''T,'''),
r'''**ParseError('expecting single type_param, has trailing comma')**'''),

(125, 'body[0]', None, None, None, {}, ('exec',
r'''del a, b, c'''), (None,
r'''x,'''),
r'''del x''', r'''
Module - ROOT 0,0..0,5
  .body[1]
  0] Delete - 0,0..0,5
    .targets[1]
    0] Name 'x' Del - 0,4..0,5
'''),

(126, 'body[0]', None, None, None, {}, ('exec',
r'''del a, b, c'''), (None,
r'''x'''),
r'''del x''',
r'''**NodeError('slice being assigned to a Delete must be a Tuple, List or Set, not a Name')**''', r'''
Module - ROOT 0,0..0,5
  .body[1]
  0] Delete - 0,0..0,5
    .targets[1]
    0] Name 'x' Del - 0,4..0,5
'''),

(127, 'body[0]', None, None, None, {'one': True}, ('exec',
r'''del a, b, c'''), (None,
r'''x'''),
r'''del x''', r'''
Module - ROOT 0,0..0,5
  .body[1]
  0] Delete - 0,0..0,5
    .targets[1]
    0] Name 'x' Del - 0,4..0,5
'''),

(128, 'body[0]', 1, 2, None, {}, ('exec',
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

(129, 'body[0]', 1, 2, None, {}, ('exec',
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

(130, 'body[0]', 1, 2, None, {'one': True}, ('exec',
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

(131, 'body[0]', 1, 2, None, {'one': True}, ('exec',
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

(132, 'body[0]', 1, 2, None, {}, ('exec',
r'''del a, b, c'''), (None, r'''
x
.
y
'''), r'''
del a, x \
    . \
    y, c
''',
r'''**NodeError('slice being assigned to a Delete must be a Tuple, List or Set, not a Attribute')**''', r'''
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

(133, 'body[0]', 1, 2, None, {}, ('exec',
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

(134, 'body[0]', None, None, None, {}, ('exec',
r'''del a, b, c'''), (None, r'''
x \

'''),
r'''del x''',
r'''**NodeError('slice being assigned to a Delete must be a Tuple, List or Set, not a Name')**''', r'''
Module - ROOT 0,0..0,5
  .body[1]
  0] Delete - 0,0..0,5
    .targets[1]
    0] Name 'x' Del - 0,4..0,5
'''),

(135, 'body[0]', None, None, 'targets', {}, ('exec',
r'''a = b = c = d'''), ('Assign_targets',
r'''x'''),
r'''x = d''', r'''
Module - ROOT 0,0..0,5
  .body[1]
  0] Assign - 0,0..0,5
    .targets[1]
    0] Name 'x' Store - 0,0..0,1
    .value Name 'd' Load - 0,4..0,5
'''),

(136, 'body[0]', None, None, 'targets', {'one': True}, ('exec',
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

(137, 'body[0]', None, None, 'targets', {}, ('exec',
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

(138, 'body[0]', 1, 2, 'targets', {}, ('exec',
r'''a = b = c = d'''), ('Assign_targets', r'''
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
''', r'''
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

(139, 'body[0]', None, None, 'targets', {}, ('exec',
r'''a = b = c = d'''), ('Assign_targets', r'''
x \

'''), r'''
x = \
 d
''', r'''
Module - ROOT 0,0..1,2
  .body[1]
  0] Assign - 0,0..1,2
    .targets[1]
    0] Name 'x' Store - 0,0..0,1
    .value Name 'd' Load - 1,1..1,2
'''),

(140, 'body[0]', 1, 2, None, {}, ('exec',
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

(141, 'body[0]', 1, 3, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''global a  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
  0] Global - 0,0..0,8
    .names[1]
    0] 'a'
'''),

(142, 'body[0]', 0, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''global c  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
  0] Global - 0,0..0,8
    .names[1]
    0] 'c'
'''),

(143, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(144, 'body[0]', 0, 2, None, {}, ('exec', r'''
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

(145, 'body[0]', 1, 3, None, {}, ('exec', r'''
global a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''),
r'''global a  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
  0] Global - 0,0..0,8
    .names[1]
    0] 'a'
'''),

(146, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

(147, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  global a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  global a  # comment
  pass
''', r'''
Module - ROOT 0,0..2,6
  .body[1]
  0] If - 0,0..2,6
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Global - 1,2..1,10
      .names[1]
      0] 'a'
    1] Pass - 2,2..2,6
'''),

(148, 'body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  global a
  pass
'''), (None, r'''
(
    b \
    , \
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
Module - ROOT 0,0..3,6
  .body[1]
  0] If - 0,0..3,6
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Global - 1,2..2,10
      .names[2]
      0] 'a'
      1] 'b'
    1] Pass - 3,2..3,6
'''),

(149, 'body[0].body[0]', 0, 0, None, {}, ('exec', r'''
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

(150, 'body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''x'''),
r'''global a, x, c  # comment''',
r'''**NodeError('slice being assigned to a Global must be a Tuple, List or Set, not a Name')**''', r'''
Module - ROOT 0,0..0,25
  .body[1]
  0] Global - 0,0..0,14
    .names[3]
    0] 'a'
    1] 'x'
    2] 'c'
'''),

(151, 'body[0]', 1, 2, None, {}, ('exec',
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

(152, 'body[0]', 1, 2, None, {}, ('exec',
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

(153, 'body[0]', 1, 2, None, {}, ('exec',
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

(154, 'body[0]', 1, 2, None, {}, ('exec',
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

(155, 'body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''x.y,'''),
r'''**NodeError('cannot put Attribute to Global.names')**'''),

(156, 'body[0]', 1, 2, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None,
r'''(x),'''),
r'''**NodeError('cannot put parenthesized Name to Global.names')**'''),

(157, 'body[0]', None, None, None, {}, ('exec',
r'''global a, b, c  # comment'''), (None, r'''
x \

'''),
r'''global x  # comment''',
r'''**NodeError('slice being assigned to a Global must be a Tuple, List or Set, not a Name')**''', r'''
Module - ROOT 0,0..0,19
  .body[1]
  0] Global - 0,0..0,8
    .names[1]
    0] 'x'
'''),

(158, 'body[0]', 1, 2, None, {}, ('exec',
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

(159, 'body[0]', 1, 3, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''nonlocal a  # comment''', r'''
Module - ROOT 0,0..0,21
  .body[1]
  0] Nonlocal - 0,0..0,10
    .names[1]
    0] 'a'
'''),

(160, 'body[0]', 0, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''**DEL**'''),
r'''nonlocal c  # comment''', r'''
Module - ROOT 0,0..0,21
  .body[1]
  0] Nonlocal - 0,0..0,10
    .names[1]
    0] 'c'
'''),

(161, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(162, 'body[0]', 0, 2, None, {}, ('exec', r'''
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

(163, 'body[0]', 1, 3, None, {}, ('exec', r'''
nonlocal a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''),
r'''nonlocal a  # comment''', r'''
Module - ROOT 0,0..0,21
  .body[1]
  0] Nonlocal - 0,0..0,10
    .names[1]
    0] 'a'
'''),

(164, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

(165, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  nonlocal a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  nonlocal a  # comment
  pass
''', r'''
Module - ROOT 0,0..2,6
  .body[1]
  0] If - 0,0..2,6
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Nonlocal - 1,2..1,12
      .names[1]
      0] 'a'
    1] Pass - 2,2..2,6
'''),

(166, 'body[0].body[0]', 1, 1, None, {}, ('exec', r'''
if 1:
  nonlocal a
  pass
'''), (None, r'''
(
    b \
    , \
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
Module - ROOT 0,0..3,6
  .body[1]
  0] If - 0,0..3,6
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Nonlocal - 1,2..2,12
      .names[2]
      0] 'a'
      1] 'b'
    1] Pass - 3,2..3,6
'''),

(167, 'body[0].body[0]', 0, 0, None, {}, ('exec', r'''
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

(168, 'body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''x'''),
r'''nonlocal a, x, c  # comment''',
r'''**NodeError('slice being assigned to a Nonlocal must be a Tuple, List or Set, not a Name')**''', r'''
Module - ROOT 0,0..0,27
  .body[1]
  0] Nonlocal - 0,0..0,16
    .names[3]
    0] 'a'
    1] 'x'
    2] 'c'
'''),

(169, 'body[0]', 1, 2, None, {}, ('exec',
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

(170, 'body[0]', 1, 2, None, {}, ('exec',
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

(171, 'body[0]', 1, 2, None, {}, ('exec',
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

(172, 'body[0]', 1, 2, None, {}, ('exec',
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

(173, 'body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''x.y,'''),
r'''**NodeError('cannot put Attribute to Nonlocal.names')**'''),

(174, 'body[0]', 1, 2, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None,
r'''(x),'''),
r'''**NodeError('cannot put parenthesized Name to Nonlocal.names')**'''),

(175, 'body[0]', None, None, None, {}, ('exec',
r'''nonlocal a, b, c  # comment'''), (None, r'''
x \

'''),
r'''nonlocal x  # comment''',
r'''**NodeError('slice being assigned to a Nonlocal must be a Tuple, List or Set, not a Name')**''', r'''
Module - ROOT 0,0..0,21
  .body[1]
  0] Nonlocal - 0,0..0,10
    .names[1]
    0] 'x'
'''),

(176, 'body[0]', 1, 2, None, {}, ('exec',
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

(177, 'body[0]', 1, 3, None, {}, ('exec',
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

(178, 'body[0]', 0, 2, None, {}, ('exec',
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

(179, 'body[0]', 1, 2, None, {}, ('exec', r'''
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

(180, 'body[0]', 0, 2, None, {}, ('exec', r'''
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

(181, 'body[0]', 1, 3, None, {}, ('exec', r'''
import a \
, \
b \
, \
c  # comment
'''), (None,
r'''**DEL**'''),
r'''import a  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
  0] Import - 0,0..0,8
    .names[1]
    0] alias - 0,7..0,8
      .name 'a'
'''),

(182, 'body[0].body[0]', 0, 1, None, {}, ('exec', r'''
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

(183, 'body[0].body[0]', 1, 2, None, {}, ('exec', r'''
if 1:
  import a \
  , \
  b  # comment
  pass
'''), (None,
r'''**DEL**'''), r'''
if 1:
  import a  # comment
  pass
''', r'''
Module - ROOT 0,0..2,6
  .body[1]
  0] If - 0,0..2,6
    .test Constant 1 - 0,3..0,4
    .body[2]
    0] Import - 1,2..1,10
      .names[1]
      0] alias - 1,9..1,10
        .name 'a'
    1] Pass - 2,2..2,6
'''),

(184, 'body[0].body[0]', 0, 0, None, {}, ('exec', r'''
if 1:
  import a
  pass
'''), ('Import_names', r'''
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

(185, 'body[0]', 1, 2, None, {}, ('exec',
r'''import a, b, c  # comment'''), ('Import_names',
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

(186, 'body[0]', 1, 2, None, {}, ('exec',
r'''import a, b, c  # comment'''), ('Import_names',
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

(187, 'body[0]', None, None, None, {}, ('exec',
r'''import a, b, c  # comment'''), ('Import_names', r'''
x \

'''),
r'''import x  # comment''', r'''
Module - ROOT 0,0..0,19
  .body[1]
  0] Import - 0,0..0,8
    .names[1]
    0] alias - 0,7..0,8
      .name 'x'
'''),
],

}
