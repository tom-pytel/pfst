DATA_GET = {
'test': [  # ................................................................................

(0, '', -1, None, False, {}, ('exec', r'''
i = 1
j = 2
k = 3
'''), ('exec',
r'''l = 4'''), r'''
i = 1
j = 2
l = 4

''', r'''
i = 1
j = 2
l = 4

''', r'''
i = 1
j = 2
l = 4

''', r'''
Module - ROOT 0,0..3,0
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

(1, '', -1, None, False, {}, ('exec', r'''
i = 1
j = 2
k = 3
'''),
r'''**DEL**''', r'''
i = 1
j = 2

''', r'''
Module - ROOT 0,0..2,0
  .body[2]
  0] Assign - 0,0..0,5
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value Constant 1 - 0,4..0,5
  1] Assign - 1,0..1,5
    .targets[1]
    0] Name 'j' Store - 1,0..1,1
    .value Constant 2 - 1,4..1,5
'''),
],

}
