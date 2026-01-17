# ('', NOT_USED, NOT_USED, 'coerce_to_class', NOT_USED, (parse_mode, code),
#
# code,
# dump code)
# - OR
# error)

from fst.asttypes import *

DATA_COERCE = {
'stmt': [  # ................................................................................

('', 0, 0, 'stmt', {}, ('Module', r'''
# 0
a # 1
# 2
'''), r'''
# 0
a # 1
# 2
''',
r'''a''', r'''
Expr - ROOT 1,0..1,1
  .value Name 'a' Load - 1,0..1,1
'''),

('', 0, 0, 'stmt', {}, ('Expression',
r'''( a )'''),
r'''( a )''',
r'''a''', r'''
Expr - ROOT 0,0..0,5
  .value Name 'a' Load - 0,2..0,3
'''),

('', 0, 0, 'stmt', {}, ('Name',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('Name',
r''' ( a ) '''),
r'''( a ) ''',
r'''a''', r'''
Expr - ROOT 0,0..0,5
  .value Name 'a' Load - 0,2..0,3
'''),

('', 0, 0, 'stmt', {}, ('Name', r'''
\
  (
  a
  )
'''), r'''
(
  a
  )
''',
r'''a''', r'''
Expr - ROOT 0,0..2,3
  .value Name 'a' Load - 1,2..1,3
'''),

('', 0, 0, 'stmt', {}, ('Name',
' \\\n  (\n  a\n  )\n  '),
'(\n  a\n  )\n  ',
r'''a''', r'''
Expr - ROOT 0,0..2,3
  .value Name 'a' Load - 1,2..1,3
'''),
],

'stmts': [  # ................................................................................

('', 0, 0, 'stmts', {}, ('Interactive',
r'''a; b'''),
r'''a; b''', r'''
Module - ROOT 0,0..0,4
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 0,3..0,4
     .value Name 'b' Load - 0,3..0,4
'''),

('', 0, 0, 'stmts', {}, ('Expression',
r'''( a )'''),
r'''( a )''',
r'''a''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Name 'a' Load - 0,2..0,3
'''),

('', 0, 0, 'stmts', {}, ('Name',
' \\\n  (\n  a\n  )\n  '),
'(\n  a\n  )\n  ',
r'''a''', r'''
Module - ROOT 0,0..3,2
  .body[1]
   0] Expr - 0,0..2,3
     .value Name 'a' Load - 1,2..1,3
'''),
],

}
