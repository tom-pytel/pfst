# ('', NOT_USED, NOT_USED, 'coerce_to_class', NOT_USED, (parse_mode, code),
#
# code,
# dump code)
# - OR
# error)

from fst.asttypes import *

DATA_COERCE = {
'stmt': [  # ................................................................................

('', 0, 0, 'stmt', {}, ('stmt',
r'''a;'''),
r'''a;''',
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('stmts',
r'''a;'''),
r'''a''',
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

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

('', 0, 0, 'stmts', {}, ('stmt',
r'''a;'''),
r'''a;''',
r'''a''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('stmts',
r'''a;'''),
r'''a;''',
r'''a''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

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
r'''-True'''),
r'''FST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**'''),

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

('', 0, 0, 'pattern', {}, ('BinOp',
r'''True+1j'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''-True+1j'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),
],

'misc': [  # ................................................................................

('', 0, 0, '_decorator_list', {'_ver': 12}, ('List', r'''
[
        '^unconverted data remains when parsing with format ".*": ".*"'
        f", at position 0. {PARSING_ERR_MSG}$",
        f'^time data ".*" doesn\'t match format ".*", at position 0. '
        f"{PARSING_ERR_MSG}$",
    ]
'''),
'\n@(\'^unconverted data remains when parsing with format ".*": ".*"\'\n        f", at position 0. {PARSING_ERR_MSG}$")\n@(f\'^time data ".*" doesn\\\'t match format ".*", at position 0. \'\n        f"{PARSING_ERR_MSG}$")\n    ', r'''
@f'^unconverted data remains when parsing with format ".*": ".*", at position 0. {PARSING_ERR_MSG}$'
@f"""^time data ".*" doesn't match format ".*", at position 0. {PARSING_ERR_MSG}$"""
''', r'''
_decorator_list - ROOT 0,0..5,4
  .decorator_list[2]
   0] JoinedStr - 1,2..2,46
     .values[3]
      0] Constant '^unconverted data remains when parsing with format ".*": ".*", at position 0. ' - 1,2..2,27
      1] FormattedValue - 2,27..2,44
        .value Name 'PARSING_ERR_MSG' Load - 2,28..2,43
        .conversion -1
      2] Constant '$' - 2,44..2,45
   1] JoinedStr - 3,2..4,29
     .values[3]
      0] Constant '^time data ".*" doesn\'t match format ".*", at position 0. ' - 3,4..3,63
      1] FormattedValue - 4,10..4,27
        .value Name 'PARSING_ERR_MSG' Load - 4,11..4,26
        .conversion -1
      2] Constant '$' - 4,27..4,28
'''),

('', 0, 0, '_decorator_list', {}, ('Tuple',
r'''((10, 110, 3), ((10, 100, 3)))'''), r'''
@(10, 110, 3)
@((10, 100, 3))
''', r'''
@(10, 110, 3)
@(10, 100, 3)
''', r'''
_decorator_list - ROOT 0,0..1,15
  .decorator_list[2]
   0] Tuple - 0,1..0,13
     .elts[3]
      0] Constant 10 - 0,2..0,4
      1] Constant 110 - 0,6..0,9
      2] Constant 3 - 0,11..0,12
     .ctx Load
   1] Tuple - 1,2..1,14
     .elts[3]
      0] Constant 10 - 1,3..1,5
      1] Constant 100 - 1,7..1,10
      2] Constant 3 - 1,12..1,13
     .ctx Load
'''),

('', 0, 0, '_Assign_targets', {}, ('List', r'''
[a,#0
b]
'''), r'''
a = \
b =
''',
r'''a = b =''', r'''
_Assign_targets - ROOT 0,0..1,3
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 1,0..1,1
'''),

('', 0, 0, '_Assign_targets', {}, ('List', r'''
[a,#0
b, #1
]
'''), r'''
a = \
b = \

''',
r'''a = b =''', r'''
_Assign_targets - ROOT 0,0..2,0
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 1,0..1,1
'''),

('', 0, 0, '_Assign_targets', {}, ('List', r'''
[a#0
]
'''), r'''
a = \

''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..1,0
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Tuple', r'''
(a \
or b,c)
'''), r'''
if a \
or b if c
''',
r'''if a or b if c''', r'''
_comprehension_ifs - ROOT 0,0..1,9
  .ifs[2]
   0] BoolOp - 0,3..1,4
     .op Or
     .values[2]
      0] Name 'a' Load - 0,3..0,4
      1] Name 'b' Load - 1,3..1,4
   1] Name 'c' Load - 1,8..1,9
'''),

('', 0, 0, 'Call', {}, ('MatchClass',
r'''a(c(d=(e)))'''),
r'''a(c(d=(e)))''',
r'''a(c(d=e))''', r'''
Call - ROOT 0,0..0,11
  .func Name 'a' Load - 0,0..0,1
  .args[1]
   0] Call - 0,2..0,10
     .func Name 'c' Load - 0,2..0,3
     .keywords[1]
      0] keyword - 0,4..0,9
        .arg 'd'
        .value Name 'e' Load - 0,7..0,8
'''),

('', 0, 0, 'expr', {}, ('MatchStar',
r'''*ά日本بμرةаб'''),
r'''*ά日本بμرةаб''', r'''
Starred - ROOT 0,0..0,10
  .value Name 'ά日本بμرةаб' Load - 0,1..0,10
  .ctx Load
'''),

('', 0, 0, 'expr', {'_ver': 12}, ('TypeVarTuple',
r'''*ά日本بμرةаб'''),
r'''*ά日本بμرةаб''', r'''
Starred - ROOT 0,0..0,10
  .value Name 'ά日本بμرةаб' Load - 0,1..0,10
  .ctx Load
'''),

('', 0, 0, 'expr', {'_ver': 12}, ('_type_params',
r'''*ά日本بμرةаб'''),
r'''*ά日本بμرةаб,''',
r'''(*ά日本بμرةаб,)''', r'''
Tuple - ROOT 0,0..0,11
  .elts[1]
   0] Starred - 0,0..0,10
     .value Name 'ά日本بμرةаб' Load - 0,1..0,10
     .ctx Load
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('arguments',
r'''x'''),
r'''x,''',
r'''(x,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'x' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('arguments',
r'''x,*y'''),
r'''x,*y''',
r'''(x, *y)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'x' Load - 0,0..0,1
   1] Starred - 0,2..0,4
     .value Name 'y' Load - 0,3..0,4
     .ctx Load
  .ctx Load
'''),

('', 0, 0, 'MatchSequence', {}, ('_Assign_targets',
r'''(()) = [] ='''),
r'''[(()), []]''',
r'''[[], []]''', r'''
MatchSequence - ROOT 0,0..0,10
  .patterns[2]
   0] MatchSequence - 0,2..0,4
   1] MatchSequence - 0,7..0,9
'''),

('', 0, 0, '_Assign_targets', {}, ('_decorator_list',
r'''@a  # b'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),
],

}
