# (case idx, attr, start, False, field, options, code | (parse_mode, code),
#
# code after cut,
# dump code after cut)
# - OR
# error)

DATA_GET_ONE = {
'Assign_targets': [  # ................................................................................

(0, 'body[0]', 0, False, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''),
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
''',
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

(1, 'body[0]', 1, False, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''),
r'''a = d = z''', r'''
Module - ROOT 0,0..0,9
  .body[1]
  0] Assign - 0,0..0,9
    .targets[2]
    0] Name 'a' Store - 0,0..0,1
    1] Name 'd' Store - 0,4..0,5
    .value Name 'z' Load - 0,8..0,9
''',
r'''(b, c)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[2]
  0] Name 'b' Load - 0,1..0,2
  1] Name 'c' Load - 0,4..0,5
  .ctx Load
'''),

(2, 'body[0]', 2, False, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''),
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
''',
r'''d''',
r'''Name 'd' Load - ROOT 0,0..0,1'''),

(3, 'body[0]', -1, False, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''),
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
''',
r'''d''',
r'''Name 'd' Load - ROOT 0,0..0,1'''),

(4, 'body[0]', -4, False, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''),
r'''**IndexError('index out of range')**'''),

(5, '', 1, False, 'targets', {}, (None, r'''
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
Assign - ROOT 0,0..3,1
  .targets[2]
  0] Name 'a' Store - 0,0..0,1
  1] Name 'c' Store - 1,0..1,1
  .value Name 'z' Load - 3,0..3,1
''',
r'''b''',
r'''Name 'b' Load - ROOT 0,0..0,1'''),

(6, '', 2, False, 'targets', {}, (None, r'''
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
Assign - ROOT 0,0..2,1
  .targets[2]
  0] Name 'a' Store - 0,0..0,1
  1] Name 'b' Store - 1,0..1,1
  .value Name 'z' Load - 2,0..2,1
''',
r'''c''',
r'''Name 'c' Load - ROOT 0,0..0,1'''),

(7, '', 1, False, 'targets', {}, ('Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
a = \
c \
= \

''', r'''
_slice_Assign_targets - ROOT 0,0..3,0
  .targets[2]
  0] Name 'a' Store - 0,0..0,1
  1] Name 'c' Store - 1,0..1,1
''',
r'''b''',
r'''Name 'b' Load - ROOT 0,0..0,1'''),

(8, '', 2, False, 'targets', {}, ('Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
a = \
b = \

''', r'''
_slice_Assign_targets - ROOT 0,0..2,0
  .targets[2]
  0] Name 'a' Store - 0,0..0,1
  1] Name 'b' Store - 1,0..1,1
''',
r'''c''',
r'''Name 'c' Load - ROOT 0,0..0,1'''),
],

}
