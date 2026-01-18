# ('', NOT_USED, NOT_USED, 'coerce_to_class', NOT_USED, (parse_mode, code),
#
# code,
# dump code)
# - OR
# error)

from fst.asttypes import *

DATA_COERCE = {
'stmt': [  # ................................................................................

('', 0, 0, 'stmt', {}, ('NamedExpr',
r'''a := b'''),
r'''(a := b)''',
r'''(a := b)''', r'''
Expr - ROOT 0,0..0,8
  .value NamedExpr - 0,1..0,7
    .target Name 'a' Store - 0,1..0,2
    .value Name 'b' Load - 0,6..0,7
'''),

('', 0, 0, 'stmt', {}, ('Yield',
r'''yield'''),
r'''yield''',
r'''(yield)''', r'''
Expr - ROOT 0,0..0,5
  .value Yield - 0,0..0,5
'''),

('', 0, 0, 'stmt', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
Expr - ROOT 0,0..0,13
  .value IfExp - 0,0..0,13
    .test Name 'b' Load - 0,5..0,6
    .body Name 'a' Load - 0,0..0,1
    .orelse Name 'c' Load - 0,12..0,13
'''),

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

('', 0, 0, 'stmts', {}, ('NamedExpr',
r'''a := b'''),
r'''(a := b)''',
r'''(a := b)''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value NamedExpr - 0,1..0,7
       .target Name 'a' Store - 0,1..0,2
       .value Name 'b' Load - 0,6..0,7
'''),

('', 0, 0, 'stmts', {}, ('Yield',
r'''yield'''),
r'''yield''',
r'''(yield)''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value Yield - 0,0..0,5
'''),

('', 0, 0, 'stmts', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] Expr - 0,0..0,13
     .value IfExp - 0,0..0,13
       .test Name 'b' Load - 0,5..0,6
       .body Name 'a' Load - 0,0..0,1
       .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, 'stmts', {'_ver': 14}, ('Interactive',
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

'pattern_from_number': [  # ................................................................................

('', 0, 0, 'pattern', {}, ('Constant',
r'''(1)'''),
r'''(1)''',
r'''1''', r'''
MatchValue - ROOT 0,1..0,2
  .value Constant 1 - 0,1..0,2
'''),

('', 0, 0, 'pattern', {}, ('UnaryOp',
r'''+1'''),
r'''FST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('UnaryOp',
r'''(-1)'''),
r'''(-1)''',
r'''-1''', r'''
MatchValue - ROOT 0,1..0,3
  .value UnaryOp - 0,1..0,3
    .op USub - 0,1..0,2
    .operand Constant 1 - 0,2..0,3
'''),

('', 0, 0, 'pattern', {}, ('UnaryOp',
r'''-(1)'''),
r'''-1''',
r'''-1''', r'''
MatchValue - ROOT 0,0..0,2
  .value UnaryOp - 0,0..0,2
    .op USub - 0,0..0,1
    .operand Constant 1 - 0,1..0,2
'''),

('', 0, 0, 'pattern', {}, ('UnaryOp',
r'''(-1j)'''),
r'''(-1j)''',
r'''-1j''', r'''
MatchValue - ROOT 0,1..0,4
  .value UnaryOp - 0,1..0,4
    .op USub - 0,1..0,2
    .operand Constant 1j - 0,2..0,4
'''),

('', 0, 0, 'pattern', {}, ('UnaryOp',
r'''-(1j)'''),
r'''-1j''',
r'''-1j''', r'''
MatchValue - ROOT 0,0..0,3
  .value UnaryOp - 0,0..0,3
    .op USub - 0,0..0,1
    .operand Constant 1j - 0,1..0,3
'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''(1)+(1j)'''),
r'''1+1j''',
r'''1 + 1j''', r'''
MatchValue - ROOT 0,0..0,4
  .value BinOp - 0,0..0,4
    .left Constant 1 - 0,0..0,1
    .op Add - 0,1..0,2
    .right Constant 1j - 0,2..0,4
'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''(1)-(1j)'''),
r'''1-1j''',
r'''1 - 1j''', r'''
MatchValue - ROOT 0,0..0,4
  .value BinOp - 0,0..0,4
    .left Constant 1 - 0,0..0,1
    .op Sub - 0,1..0,2
    .right Constant 1j - 0,2..0,4
'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''(1)+(-1j)'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''-(1)+(1j)'''),
r'''-1+1j''',
r'''-1 + 1j''', r'''
MatchValue - ROOT 0,0..0,5
  .value BinOp - 0,0..0,5
    .left UnaryOp - 0,0..0,2
      .op USub - 0,0..0,1
      .operand Constant 1 - 0,1..0,2
    .op Add - 0,2..0,3
    .right Constant 1j - 0,3..0,5
'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''(-1)+(1j)'''),
r'''-1+1j''',
r'''-1 + 1j''', r'''
MatchValue - ROOT 0,0..0,5
  .value BinOp - 0,0..0,5
    .left UnaryOp - 0,0..0,2
      .op USub - 0,0..0,1
      .operand Constant 1 - 0,1..0,2
    .op Add - 0,2..0,3
    .right Constant 1j - 0,3..0,5
'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''+1+(1j)'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''1+(-1j)'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),
],

}
