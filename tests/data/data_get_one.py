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

'type_params': [  # ................................................................................

(0, 'body[0]', 0, False, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''),
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
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(1, 'body[0]', 1, False, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''),
r'''def f[T: int](): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .body[1]
    0] Pass - 0,17..0,21
    .type_params[1]
    0] TypeVar - 0,6..0,12
      .name 'T'
      .bound Name 'int' Load - 0,9..0,12
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(2, 'body[0]', -1, False, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''),
r'''def f[T: int](): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .body[1]
    0] Pass - 0,17..0,21
    .type_params[1]
    0] TypeVar - 0,6..0,12
      .name 'T'
      .bound Name 'int' Load - 0,9..0,12
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(3, 'body[0]', -2, False, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''),
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
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(4, 'body[0]', -4, False, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''),
r'''**IndexError('index out of range')**'''),

(5, 'body[0]', 0, False, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''),
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
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(6, 'body[0]', 1, False, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''),
r'''async def f[T: int](): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
  0] AsyncFunctionDef - 0,0..0,27
    .name 'f'
    .body[1]
    0] Pass - 0,23..0,27
    .type_params[1]
    0] TypeVar - 0,12..0,18
      .name 'T'
      .bound Name 'int' Load - 0,15..0,18
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(7, 'body[0]', -1, False, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''),
r'''async def f[T: int](): pass''', r'''
Module - ROOT 0,0..0,27
  .body[1]
  0] AsyncFunctionDef - 0,0..0,27
    .name 'f'
    .body[1]
    0] Pass - 0,23..0,27
    .type_params[1]
    0] TypeVar - 0,12..0,18
      .name 'T'
      .bound Name 'int' Load - 0,15..0,18
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(8, 'body[0]', -2, False, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''),
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
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(9, 'body[0]', -4, False, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''),
r'''**IndexError('index out of range')**'''),

(10, 'body[0]', 0, False, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''),
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
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(11, 'body[0]', 1, False, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''),
r'''class c[T: int]: pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
  0] ClassDef - 0,0..0,21
    .name 'c'
    .body[1]
    0] Pass - 0,17..0,21
    .type_params[1]
    0] TypeVar - 0,8..0,14
      .name 'T'
      .bound Name 'int' Load - 0,11..0,14
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(12, 'body[0]', -1, False, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''),
r'''class c[T: int]: pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
  0] ClassDef - 0,0..0,21
    .name 'c'
    .body[1]
    0] Pass - 0,17..0,21
    .type_params[1]
    0] TypeVar - 0,8..0,14
      .name 'T'
      .bound Name 'int' Load - 0,11..0,14
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(13, 'body[0]', -2, False, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''),
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
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(14, 'body[0]', -4, False, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''),
r'''**IndexError('index out of range')**'''),

(15, 'body[0]', 0, False, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''),
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
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(16, 'body[0]', 1, False, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''),
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
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(17, 'body[0]', -1, False, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''),
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
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(18, 'body[0]', -2, False, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''),
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
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(19, 'body[0]', -4, False, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''),
r'''**IndexError('index out of range')**'''),

(20, '', 0, False, 'type_params', {'_ver': 12}, ('type_params',
r'''T: int, U: (str)'''),
r'''U: (str)''', r'''
_slice_type_params - ROOT 0,0..0,8
  .type_params[1]
  0] TypeVar - 0,0..0,8
    .name 'U'
    .bound Name 'str' Load - 0,4..0,7
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(21, '', 1, False, 'type_params', {'_ver': 12}, ('type_params',
r'''T: int, U: (str)'''),
r'''T: int''', r'''
_slice_type_params - ROOT 0,0..0,6
  .type_params[1]
  0] TypeVar - 0,0..0,6
    .name 'T'
    .bound Name 'int' Load - 0,3..0,6
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(22, '', -1, False, 'type_params', {'_ver': 12}, ('type_params',
r'''T: int, U: (str)'''),
r'''T: int''', r'''
_slice_type_params - ROOT 0,0..0,6
  .type_params[1]
  0] TypeVar - 0,0..0,6
    .name 'T'
    .bound Name 'int' Load - 0,3..0,6
''',
r'''U: (str)''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'U'
  .bound Name 'str' Load - 0,4..0,7
'''),

(23, '', -2, False, 'type_params', {'_ver': 12}, ('type_params',
r'''T: int, U: (str)'''),
r'''U: (str)''', r'''
_slice_type_params - ROOT 0,0..0,8
  .type_params[1]
  0] TypeVar - 0,0..0,8
    .name 'U'
    .bound Name 'str' Load - 0,4..0,7
''',
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

(24, '', -4, False, 'type_params', {'_ver': 12}, ('type_params',
r'''T: int, U: (str)'''),
r'''**IndexError('index out of range')**'''),
],

}
