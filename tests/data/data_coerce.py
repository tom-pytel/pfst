# ('', NOT_USED, NOT_USED, 'coerce_to_class', NOT_USED, (parse_mode, code),
#
# code,
# dump code)
# - OR
# error)

from fst.asttypes import *

DATA_COERCE = {
'matrix_stmt': [  # ................................................................................

('', 0, 0, 'stmt', {}, ('Module',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('Expression',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('Expr',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('_Assign_targets',
r'''a ='''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('_decorator_list',
r'''@a'''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('_arglikes',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('expr_arglike',
r'''*not a'''),
r'''*(not a)''',
r'''*(not a)''', r'''
Expr - ROOT 0,0..0,8
  .value Starred - 0,0..0,8
    .value UnaryOp - 0,2..0,7
      .op Not - 0,2..0,5
      .operand Name 'a' Load - 0,6..0,7
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting stmt, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting stmt, got Tuple, could not coerce')**'''),

('', 0, 0, 'stmt', {}, ('NamedExpr',
r'''a := b'''),
r'''(a := b)''',
r'''(a := b)''', r'''
Expr - ROOT 0,0..0,8
  .value NamedExpr - 0,1..0,7
    .target Name 'a' Store - 0,1..0,2
    .value Name 'b' Load - 0,6..0,7
'''),

('', 0, 0, 'stmt', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
Expr - ROOT 0,0..0,5
  .value BinOp - 0,0..0,5
    .left Name 'a' Load - 0,0..0,1
    .op Add - 0,2..0,3
    .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'stmt', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
Expr - ROOT 0,0..0,2
  .value UnaryOp - 0,0..0,2
    .op USub - 0,0..0,1
    .operand Name 'a' Load - 0,1..0,2
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

('', 0, 0, 'stmt', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Expr - ROOT 0,0..0,6
  .value Dict - 0,0..0,6
    .keys[1]
     0] Name 'a' Load - 0,1..0,2
    .values[1]
     0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'stmt', {}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Expr - ROOT 0,0..0,7
  .value Yield - 0,0..0,7
    .value Name 'a' Load - 0,6..0,7
'''),

('', 0, 0, 'stmt', {}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
Expr - ROOT 0,0..0,12
  .value YieldFrom - 0,0..0,12
    .value Name 'a' Load - 0,11..0,12
'''),

('', 0, 0, 'stmt', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
Expr - ROOT 0,0..0,3
  .value Set - 0,0..0,3
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'stmt', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
Expr - ROOT 0,0..0,3
  .value Call - 0,0..0,3
    .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('Constant',
r'''1'''),
r'''1''', r'''
Expr - ROOT 0,0..0,1
  .value Constant 1 - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Expr - ROOT 0,0..0,3
  .value Attribute - 0,0..0,3
    .value Name 'a' Load - 0,0..0,1
    .attr 'b'
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Expr - ROOT 0,0..0,2
  .value Starred - 0,0..0,2
    .value Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('Name',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
Expr - ROOT 0,0..0,3
  .value List - 0,0..0,3
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('Tuple',
r'''a,'''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting stmt, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting stmt, got Slice, could not coerce')**'''),

('', 0, 0, 'stmt', {}, ('_comprehension_ifs',
r'''if a'''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('arguments',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('arg',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('alias',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('_aliases',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('withitem',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('_withitems',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('MatchValue',
r'''1'''),
r'''1''', r'''
Expr - ROOT 0,0..0,1
  .value Constant 1 - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('MatchSingleton',
r'''True'''),
r'''True''', r'''
Expr - ROOT 0,0..0,4
  .value Constant True - 0,0..0,4
'''),

('', 0, 0, 'stmt', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
Expr - ROOT 0,0..0,3
  .value List - 0,0..0,3
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Expr - ROOT 0,0..0,6
  .value Dict - 0,0..0,6
    .keys[1]
     0] Constant 1 - 0,1..0,2
    .values[1]
     0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, 'stmt', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Expr - ROOT 0,0..0,3
  .value Call - 0,0..0,3
    .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
Expr - ROOT 0,0..0,2
  .value Starred - 0,0..0,2
    .value Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
Expr - ROOT 0,0..0,5
  .value BinOp - 0,0..0,5
    .left Name 'a' Load - 0,0..0,1
    .op BitOr - 0,2..0,3
    .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'stmt', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmt', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
Expr - ROOT 0,0..0,2
  .value Starred - 0,0..0,2
    .value Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmt', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Expr - ROOT 0,0..0,4
  .value Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),
],

'matrix_stmts': [  # ................................................................................

('', 0, 0, 'stmts', {}, ('Module',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('Expression',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('Expr',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('_Assign_targets',
r'''a ='''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('_decorator_list',
r'''@a'''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('_arglikes',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('expr_arglike',
r'''*not a'''),
r'''*(not a)''',
r'''*(not a)''', r'''
Module - ROOT 0,0..0,8
  .body[1]
   0] Expr - 0,0..0,8
     .value Starred - 0,0..0,8
       .value UnaryOp - 0,2..0,7
         .op Not - 0,2..0,5
         .operand Name 'a' Load - 0,6..0,7
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting zero or more stmts, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting zero or more stmts, got Tuple, could not coerce')**'''),

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

('', 0, 0, 'stmts', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value BinOp - 0,0..0,5
       .left Name 'a' Load - 0,0..0,1
       .op Add - 0,2..0,3
       .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'stmts', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value UnaryOp - 0,0..0,2
       .op USub - 0,0..0,1
       .operand Name 'a' Load - 0,1..0,2
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

('', 0, 0, 'stmts', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Dict - 0,0..0,6
       .keys[1]
        0] Name 'a' Load - 0,1..0,2
       .values[1]
        0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'stmts', {}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Module - ROOT 0,0..0,7
  .body[1]
   0] Expr - 0,0..0,7
     .value Yield - 0,0..0,7
       .value Name 'a' Load - 0,6..0,7
'''),

('', 0, 0, 'stmts', {}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
Module - ROOT 0,0..0,12
  .body[1]
   0] Expr - 0,0..0,12
     .value YieldFrom - 0,0..0,12
       .value Name 'a' Load - 0,11..0,12
'''),

('', 0, 0, 'stmts', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Set - 0,0..0,3
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'stmts', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Call - 0,0..0,3
       .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('Constant',
r'''1'''),
r'''1''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Constant 1 - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Attribute - 0,0..0,3
       .value Name 'a' Load - 0,0..0,1
       .attr 'b'
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Starred - 0,0..0,2
       .value Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('Name',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value List - 0,0..0,3
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('Tuple',
r'''a,'''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting zero or more stmts, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting zero or more stmts, got Slice, could not coerce')**'''),

('', 0, 0, 'stmts', {}, ('_comprehension_ifs',
r'''if a'''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('arguments',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('arg',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('alias',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('_aliases',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('withitem',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('_withitems',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('MatchValue',
r'''1'''),
r'''1''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Constant 1 - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('MatchSingleton',
r'''True'''),
r'''True''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Constant True - 0,0..0,4
'''),

('', 0, 0, 'stmts', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value List - 0,0..0,3
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Dict - 0,0..0,6
       .keys[1]
        0] Constant 1 - 0,1..0,2
       .values[1]
        0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, 'stmts', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Module - ROOT 0,0..0,3
  .body[1]
   0] Expr - 0,0..0,3
     .value Call - 0,0..0,3
       .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Starred - 0,0..0,2
       .value Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Expr - 0,0..0,5
     .value BinOp - 0,0..0,5
       .left Name 'a' Load - 0,0..0,1
       .op BitOr - 0,2..0,3
       .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'stmts', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'stmts', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Starred - 0,0..0,2
       .value Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmts', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Module - ROOT 0,0..0,4
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),
],

'matrix_expr': [  # ................................................................................

('', 0, 0, 'expr', {}, ('Module',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('Interactive',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('Expression',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('Expr',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('_Assign_targets',
r'''a ='''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('_decorator_list',
r'''@a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('_arglikes',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('expr_arglike',
r'''*not a'''),
r'''*not a''',
r'''*(not a)''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting expression (standard), got Tuple with a Slice in it')**''',
r'''AST: **SyntaxError('invalid syntax')**'''),

('', 0, 0, 'expr', {}, ('NamedExpr',
r'''a := b'''),
r'''a := b''',
r'''(a := b)''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'a' Store - 0,0..0,1
  .value Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, 'expr', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
UnaryOp - ROOT 0,0..0,2
  .op USub - 0,0..0,1
  .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'expr', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
IfExp - ROOT 0,0..0,13
  .test Name 'b' Load - 0,5..0,6
  .body Name 'a' Load - 0,0..0,1
  .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, 'expr', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'a' Load - 0,1..0,2
  .values[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr', {}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Yield - ROOT 0,0..0,7
  .value Name 'a' Load - 0,6..0,7
'''),

('', 0, 0, 'expr', {}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
YieldFrom - ROOT 0,0..0,12
  .value Name 'a' Load - 0,11..0,12
'''),

('', 0, 0, 'expr', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'expr', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'expr', {}, ('Constant',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('Name',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting expression (standard), got Slice')**''',
r'''AST: **SyntaxError('invalid syntax')**'''),

('', 0, 0, 'expr', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('arguments',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('arg',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('alias',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('_aliases',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('withitem',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('_withitems',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('MatchValue',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('MatchSingleton',
r'''True'''),
r'''True''',
r'''Constant True - ROOT 0,0..0,4'''),

('', 0, 0, 'expr', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .values[1]
   0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, 'expr', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'expr', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr', {}, ('MatchAs',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op BitOr - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),
],

'matrix_expr_all': [  # ................................................................................

('', 0, 0, 'expr_all', {}, ('Module',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('Interactive',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('Expression',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('Expr',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('_Assign_targets',
r'''a ='''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('_decorator_list',
r'''@a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('_arglikes',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('expr_arglike',
r'''*not a'''),
r'''*not a''',
r'''*(not a)''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''a:b, c:d''', r'''
Tuple - ROOT 0,0..0,8
  .elts[2]
   0] Slice - 0,0..0,3
     .lower Name 'a' Load - 0,0..0,1
     .upper Name 'b' Load - 0,2..0,3
   1] Slice - 0,5..0,8
     .lower Name 'c' Load - 0,5..0,6
     .upper Name 'd' Load - 0,7..0,8
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('NamedExpr',
r'''a := b'''),
r'''a := b''',
r'''(a := b)''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'a' Store - 0,0..0,1
  .value Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, 'expr_all', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_all', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
UnaryOp - ROOT 0,0..0,2
  .op USub - 0,0..0,1
  .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'expr_all', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
IfExp - ROOT 0,0..0,13
  .test Name 'b' Load - 0,5..0,6
  .body Name 'a' Load - 0,0..0,1
  .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, 'expr_all', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'a' Load - 0,1..0,2
  .values[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_all', {}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Yield - ROOT 0,0..0,7
  .value Name 'a' Load - 0,6..0,7
'''),

('', 0, 0, 'expr_all', {}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
YieldFrom - ROOT 0,0..0,12
  .value Name 'a' Load - 0,11..0,12
'''),

('', 0, 0, 'expr_all', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'expr_all', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'expr_all', {}, ('Constant',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('Name',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('Slice',
r'''a:b:c'''),
r'''a:b:c''', r'''
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_all', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('arguments',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('arg',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('alias',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('_aliases',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('withitem',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('_withitems',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('MatchValue',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('MatchSingleton',
r'''True'''),
r'''True''',
r'''Constant True - ROOT 0,0..0,4'''),

('', 0, 0, 'expr_all', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .values[1]
   0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_all', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'expr_all', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_all', {}, ('MatchAs',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op BitOr - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_all', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_all', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_all', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),
],

'matrix_expr_arglike': [  # ................................................................................

('', 0, 0, 'expr_arglike', {}, ('Module',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('Interactive',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('Expression',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('Expr',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('_Assign_targets',
r'''a ='''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('_decorator_list',
r'''@a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('_arglikes',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('expr_arglike',
r'''*not a'''),
r'''*not a''',
r'''*(not a)''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting expression (arglike), got Tuple with a Slice in it')**''',
r'''AST: **SyntaxError('invalid syntax')**'''),

('', 0, 0, 'expr_arglike', {}, ('NamedExpr',
r'''a := b'''),
r'''a := b''',
r'''(a := b)''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'a' Store - 0,0..0,1
  .value Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, 'expr_arglike', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_arglike', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
UnaryOp - ROOT 0,0..0,2
  .op USub - 0,0..0,1
  .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'expr_arglike', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
IfExp - ROOT 0,0..0,13
  .test Name 'b' Load - 0,5..0,6
  .body Name 'a' Load - 0,0..0,1
  .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, 'expr_arglike', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'a' Load - 0,1..0,2
  .values[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_arglike', {}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Yield - ROOT 0,0..0,7
  .value Name 'a' Load - 0,6..0,7
'''),

('', 0, 0, 'expr_arglike', {}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
YieldFrom - ROOT 0,0..0,12
  .value Name 'a' Load - 0,11..0,12
'''),

('', 0, 0, 'expr_arglike', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'expr_arglike', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'expr_arglike', {}, ('Constant',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('Name',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting expression (arglike), got Slice')**''',
r'''AST: **SyntaxError('invalid syntax')**'''),

('', 0, 0, 'expr_arglike', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('arguments',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('arg',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('alias',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('_aliases',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('withitem',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('_withitems',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('MatchValue',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('MatchSingleton',
r'''True'''),
r'''True''',
r'''Constant True - ROOT 0,0..0,4'''),

('', 0, 0, 'expr_arglike', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .values[1]
   0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_arglike', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'expr_arglike', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {}, ('MatchAs',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op BitOr - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_arglike', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_arglike', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_arglike', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),
],

'matrix_expr_slice': [  # ................................................................................

('', 0, 0, 'expr_slice', {}, ('Module',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('Interactive',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('Expression',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('Expr',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('_Assign_targets',
r'''a ='''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('_decorator_list',
r'''@a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('_arglikes',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting expression (slice), got Starred, must be in sequence')**''',
r'''AST: **NodeError('expecting expression (slice), got Starred, must be in sequence')**'''),

('', 0, 0, 'expr_slice', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''a:b, c:d''', r'''
Tuple - ROOT 0,0..0,8
  .elts[2]
   0] Slice - 0,0..0,3
     .lower Name 'a' Load - 0,0..0,1
     .upper Name 'b' Load - 0,2..0,3
   1] Slice - 0,5..0,8
     .lower Name 'c' Load - 0,5..0,6
     .upper Name 'd' Load - 0,7..0,8
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('NamedExpr',
r'''a := b'''),
r'''a := b''',
r'''(a := b)''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'a' Store - 0,0..0,1
  .value Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, 'expr_slice', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_slice', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
UnaryOp - ROOT 0,0..0,2
  .op USub - 0,0..0,1
  .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'expr_slice', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
IfExp - ROOT 0,0..0,13
  .test Name 'b' Load - 0,5..0,6
  .body Name 'a' Load - 0,0..0,1
  .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, 'expr_slice', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'a' Load - 0,1..0,2
  .values[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_slice', {}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Yield - ROOT 0,0..0,7
  .value Name 'a' Load - 0,6..0,7
'''),

('', 0, 0, 'expr_slice', {}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
YieldFrom - ROOT 0,0..0,12
  .value Name 'a' Load - 0,11..0,12
'''),

('', 0, 0, 'expr_slice', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'expr_slice', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'expr_slice', {}, ('Constant',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting expression (slice), got Starred, must be in sequence')**''',
r'''AST: **NodeError('expecting expression (slice), got Starred, must be in sequence')**'''),

('', 0, 0, 'expr_slice', {}, ('Name',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('Slice',
r'''a:b:c'''),
r'''a:b:c''', r'''
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_slice', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('arguments',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('arg',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('alias',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('_aliases',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('withitem',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('_withitems',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('MatchValue',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('MatchSingleton',
r'''True'''),
r'''True''',
r'''Constant True - ROOT 0,0..0,4'''),

('', 0, 0, 'expr_slice', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'expr_slice', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .values[1]
   0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_slice', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'expr_slice', {'_ver': 11}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting expression (slice), got MatchStar, coerced to Starred, must be in a sequence')**''',
r'''AST: **NodeError('expecting expression (slice), got MatchStar, coerced to Starred, must be in a sequence')**'''),

('', 0, 0, 'expr_slice', {}, ('MatchAs',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op BitOr - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'expr_slice', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'expr_slice', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting expression (slice), got TypeVarTuple, coerced to Starred, must be in a sequence')**''',
r'''AST: **NodeError('expecting expression (slice), got TypeVarTuple, coerced to Starred, must be in a sequence')**'''),

('', 0, 0, 'expr_slice', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),
],

'matrix_Tuple_elt': [  # ................................................................................

('', 0, 0, 'Tuple_elt', {}, ('Module',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('Interactive',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('Expression',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('Expr',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('_Assign_targets',
r'''a ='''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('_decorator_list',
r'''@a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('_arglikes',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('expr_arglike',
r'''*not a'''),
r'''*not a''',
r'''*(not a)''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting expression (tuple element), got Tuple with a Slice in it')**''',
r'''AST: **SyntaxError('invalid syntax')**'''),

('', 0, 0, 'Tuple_elt', {}, ('NamedExpr',
r'''a := b'''),
r'''a := b''',
r'''(a := b)''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'a' Store - 0,0..0,1
  .value Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, 'Tuple_elt', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'Tuple_elt', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
UnaryOp - ROOT 0,0..0,2
  .op USub - 0,0..0,1
  .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'Tuple_elt', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
IfExp - ROOT 0,0..0,13
  .test Name 'b' Load - 0,5..0,6
  .body Name 'a' Load - 0,0..0,1
  .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, 'Tuple_elt', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'a' Load - 0,1..0,2
  .values[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'Tuple_elt', {}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Yield - ROOT 0,0..0,7
  .value Name 'a' Load - 0,6..0,7
'''),

('', 0, 0, 'Tuple_elt', {}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
YieldFrom - ROOT 0,0..0,12
  .value Name 'a' Load - 0,11..0,12
'''),

('', 0, 0, 'Tuple_elt', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'Tuple_elt', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'Tuple_elt', {}, ('Constant',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('Name',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('Slice',
r'''a:b:c'''),
r'''a:b:c''', r'''
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5
'''),

('', 0, 0, 'Tuple_elt', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('arguments',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('arg',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('alias',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('_aliases',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('withitem',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('_withitems',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('MatchValue',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('MatchSingleton',
r'''True'''),
r'''True''',
r'''Constant True - ROOT 0,0..0,4'''),

('', 0, 0, 'Tuple_elt', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .values[1]
   0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, 'Tuple_elt', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'Tuple_elt', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {}, ('MatchAs',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op BitOr - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'Tuple_elt', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, 'Tuple_elt', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'Tuple_elt', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),
],

'matrix_Tuple': [  # ................................................................................

('', 0, 0, 'Tuple', {}, ('Module',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got Module, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Module, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Interactive',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got Interactive, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Interactive, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Expression',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got Expression, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Expression, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Expr',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got Expr, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Expr, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('_Assign_targets',
r'''a ='''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('_decorator_list',
r'''@a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('_arglikes',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting Tuple, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Starred, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''a:b, c:d''', r'''
Tuple - ROOT 0,0..0,8
  .elts[2]
   0] Slice - 0,0..0,3
     .lower Name 'a' Load - 0,0..0,1
     .upper Name 'b' Load - 0,2..0,3
   1] Slice - 0,5..0,8
     .lower Name 'c' Load - 0,5..0,6
     .upper Name 'd' Load - 0,7..0,8
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting Tuple, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got NamedExpr, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting Tuple, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got BinOp, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting Tuple, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting Tuple, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got IfExp, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting Tuple, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Dict, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting Tuple, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Yield, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting Tuple, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got YieldFrom, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Set',
r'''{a}'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting Tuple, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Call, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting Tuple, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Constant, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Attribute',
r'''a.b'''),
r'''FST: **NodeError('expecting Tuple, got Attribute, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Attribute, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting Tuple, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Starred, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Name',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got Name, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Name, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('List',
r'''[a]'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting Tuple, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Slice, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('arguments',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('arg',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got arg, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got arg, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('alias',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got alias, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got alias, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('_aliases',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('withitem',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got withitem, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got withitem, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('_withitems',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting Tuple, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got MatchValue, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting Tuple, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got MatchSingleton, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('MatchSequence',
r'''[a]'''),
r'''AST: **AttributeError("'MatchSequence' object has no attribute 'f'")**''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, 'Tuple', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting Tuple, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got MatchMapping, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting Tuple, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got MatchClass, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting Tuple, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got MatchStar, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('MatchAs',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got MatchAs, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got MatchAs, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting Tuple, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got MatchOr, could not coerce')**'''),

('', 0, 0, 'Tuple', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got TypeVar, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got TypeVar, could not coerce')**'''),

('', 0, 0, 'Tuple', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting Tuple, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, 'Tuple', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),
],

'matrix__Assign_targets': [  # ................................................................................

('', 0, 0, '_Assign_targets', {}, ('Module',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('Expression',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('Expr',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a ='''),
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('_decorator_list',
r'''@a'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('_arglikes',
r'''a'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting _Assign_targets, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got Starred, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _Assign_targets, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got Tuple, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting _Assign_targets, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got NamedExpr, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting _Assign_targets, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got BinOp, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting _Assign_targets, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got UnaryOp, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting _Assign_targets, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got IfExp, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting _Assign_targets, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got Dict, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting _Assign_targets, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got Yield, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting _Assign_targets, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got YieldFrom, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('Set',
r'''{a}'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting _Assign_targets, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got Call, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting _Assign_targets, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got Constant, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Attribute - 0,0..0,3
     .value Name 'a' Load - 0,0..0,1
     .attr 'b'
     .ctx Store
'''),

('', 0, 0, '_Assign_targets', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
_Assign_targets - ROOT 0,0..0,2
  .targets[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Store - 0,1..0,2
     .ctx Store
'''),

('', 0, 0, '_Assign_targets', {}, ('Name',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('List',
r'''[a]'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('Tuple',
r'''a,'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _Assign_targets, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got Slice, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('arguments',
r'''a'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('arg',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('alias',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('_aliases',
r'''a'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('withitem',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('_withitems',
r'''a'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting _Assign_targets, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got MatchValue, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting _Assign_targets, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got MatchSingleton, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('MatchSequence',
r'''[a]'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting _Assign_targets, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got MatchMapping, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting _Assign_targets, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got MatchClass, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
_Assign_targets - ROOT 0,0..0,2
  .targets[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Store - 0,1..0,2
     .ctx Store
'''),

('', 0, 0, '_Assign_targets', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting _Assign_targets, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting _Assign_targets, got MatchOr, could not coerce')**'''),

('', 0, 0, '_Assign_targets', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('', 0, 0, '_Assign_targets', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
_Assign_targets - ROOT 0,0..0,2
  .targets[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Store - 0,1..0,2
     .ctx Store
'''),

('', 0, 0, '_Assign_targets', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a =''',
r'''a =''', r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),
],

'matrix__decorator_list': [  # ................................................................................

('', 0, 0, '_decorator_list', {}, ('Module',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('Interactive',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('Expression',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('Expr',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('_Assign_targets',
r'''a ='''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('_decorator_list',
r'''@a'''),
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('_arglikes',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting _decorator_list, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _decorator_list, got Starred, could not coerce')**'''),

('', 0, 0, '_decorator_list', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _decorator_list, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _decorator_list, got Tuple, could not coerce')**'''),

('', 0, 0, '_decorator_list', {}, ('NamedExpr',
r'''a := b'''),
r'''@(a := b)''',
r'''@(a := b)''', r'''
_decorator_list - ROOT 0,0..0,9
  .decorator_list[1]
   0] NamedExpr - 0,2..0,8
     .target Name 'a' Store - 0,2..0,3
     .value Name 'b' Load - 0,7..0,8
'''),

('', 0, 0, '_decorator_list', {}, ('BinOp',
r'''a + b'''),
r'''@a + b''',
r'''@a + b''', r'''
_decorator_list - ROOT 0,0..0,6
  .decorator_list[1]
   0] BinOp - 0,1..0,6
     .left Name 'a' Load - 0,1..0,2
     .op Add - 0,3..0,4
     .right Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, '_decorator_list', {}, ('UnaryOp',
r'''-a'''),
r'''@-a''',
r'''@-a''', r'''
_decorator_list - ROOT 0,0..0,3
  .decorator_list[1]
   0] UnaryOp - 0,1..0,3
     .op USub - 0,1..0,2
     .operand Name 'a' Load - 0,2..0,3
'''),

('', 0, 0, '_decorator_list', {}, ('IfExp',
r'''a if b else c'''),
r'''@a if b else c''',
r'''@a if b else c''', r'''
_decorator_list - ROOT 0,0..0,14
  .decorator_list[1]
   0] IfExp - 0,1..0,14
     .test Name 'b' Load - 0,6..0,7
     .body Name 'a' Load - 0,1..0,2
     .orelse Name 'c' Load - 0,13..0,14
'''),

('', 0, 0, '_decorator_list', {}, ('Dict',
r'''{a: b}'''),
r'''@{a: b}''',
r'''@{a: b}''', r'''
_decorator_list - ROOT 0,0..0,7
  .decorator_list[1]
   0] Dict - 0,1..0,7
     .keys[1]
      0] Name 'a' Load - 0,2..0,3
     .values[1]
      0] Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, '_decorator_list', {}, ('Yield',
r'''yield a'''),
r'''@(yield a)''',
r'''@(yield a)''', r'''
_decorator_list - ROOT 0,0..0,10
  .decorator_list[1]
   0] Yield - 0,2..0,9
     .value Name 'a' Load - 0,8..0,9
'''),

('', 0, 0, '_decorator_list', {}, ('YieldFrom',
r'''yield from a'''),
r'''@(yield from a)''',
r'''@(yield from a)''', r'''
_decorator_list - ROOT 0,0..0,15
  .decorator_list[1]
   0] YieldFrom - 0,2..0,14
     .value Name 'a' Load - 0,13..0,14
'''),

('', 0, 0, '_decorator_list', {}, ('Set',
r'''{a}'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('Call',
r'''a()'''),
r'''@a()''',
r'''@a()''', r'''
_decorator_list - ROOT 0,0..0,4
  .decorator_list[1]
   0] Call - 0,1..0,4
     .func Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('Constant',
r'''1'''),
r'''@1''',
r'''@1''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Constant 1 - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('Attribute',
r'''a.b'''),
r'''@a.b''',
r'''@a.b''', r'''
_decorator_list - ROOT 0,0..0,4
  .decorator_list[1]
   0] Attribute - 0,1..0,4
     .value Name 'a' Load - 0,1..0,2
     .attr 'b'
     .ctx Load
'''),

('', 0, 0, '_decorator_list', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting _decorator_list, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _decorator_list, got Starred, could not coerce')**'''),

('', 0, 0, '_decorator_list', {}, ('Name',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('List',
r'''[a]'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('Tuple',
r'''a,'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _decorator_list, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _decorator_list, got Slice, could not coerce')**'''),

('', 0, 0, '_decorator_list', {}, ('_comprehension_ifs',
r'''if a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('arguments',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('arg',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('alias',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('_aliases',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('withitem',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('_withitems',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('MatchValue',
r'''1'''),
r'''@1''',
r'''@1''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Constant 1 - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('MatchSingleton',
r'''True'''),
r'''@True''',
r'''@True''', r'''
_decorator_list - ROOT 0,0..0,5
  .decorator_list[1]
   0] Constant True - 0,1..0,5
'''),

('', 0, 0, '_decorator_list', {}, ('MatchSequence',
r'''[a]'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('MatchMapping',
r'''{1: a}'''),
r'''@{1: a}''',
r'''@{1: a}''', r'''
_decorator_list - ROOT 0,0..0,7
  .decorator_list[1]
   0] Dict - 0,1..0,7
     .keys[1]
      0] Constant 1 - 0,2..0,3
     .values[1]
      0] Name 'a' Load - 0,5..0,6
'''),

('', 0, 0, '_decorator_list', {}, ('MatchClass',
r'''a()'''),
r'''@a()''',
r'''@a()''', r'''
_decorator_list - ROOT 0,0..0,4
  .decorator_list[1]
   0] Call - 0,1..0,4
     .func Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting _decorator_list, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting _decorator_list, got MatchStar, could not coerce')**'''),

('', 0, 0, '_decorator_list', {}, ('MatchAs',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {}, ('MatchOr',
r'''a | b'''),
r'''@a | b''',
r'''@a | b''', r'''
_decorator_list - ROOT 0,0..0,6
  .decorator_list[1]
   0] BinOp - 0,1..0,6
     .left Name 'a' Load - 0,1..0,2
     .op BitOr - 0,3..0,4
     .right Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, '_decorator_list', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_decorator_list', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting _decorator_list, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting _decorator_list, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, '_decorator_list', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''@a''',
r'''@a''', r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),
],

'matrix__arglike': [  # ................................................................................

('', 0, 0, '_arglike', {}, ('Module',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('Interactive',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('Expression',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('Expr',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('_Assign_targets',
r'''a ='''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('_decorator_list',
r'''@a'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('_arglikes',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('expr_arglike',
r'''*not a'''),
r'''*not a''',
r'''*(not a)''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting expression (arglike), got Tuple with a Slice in it')**''',
r'''AST: **SyntaxError('invalid syntax')**'''),

('', 0, 0, '_arglike', {}, ('NamedExpr',
r'''a := b'''),
r'''a := b''',
r'''(a := b)''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'a' Store - 0,0..0,1
  .value Name 'b' Load - 0,5..0,6
'''),

('', 0, 0, '_arglike', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_arglike', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
UnaryOp - ROOT 0,0..0,2
  .op USub - 0,0..0,1
  .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_arglike', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
IfExp - ROOT 0,0..0,13
  .test Name 'b' Load - 0,5..0,6
  .body Name 'a' Load - 0,0..0,1
  .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, '_arglike', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'a' Load - 0,1..0,2
  .values[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_arglike', {}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Yield - ROOT 0,0..0,7
  .value Name 'a' Load - 0,6..0,7
'''),

('', 0, 0, '_arglike', {}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
YieldFrom - ROOT 0,0..0,12
  .value Name 'a' Load - 0,11..0,12
'''),

('', 0, 0, '_arglike', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_arglike', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglike', {}, ('Constant',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('Name',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting expression (arglike), got Slice')**''',
r'''AST: **SyntaxError('invalid syntax')**'''),

('', 0, 0, '_arglike', {}, ('_comprehension_ifs',
r'''if a'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('arguments',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('arg',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('alias',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('_aliases',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('withitem',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('_withitems',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('MatchValue',
r'''1'''),
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('MatchSingleton',
r'''True'''),
r'''True''',
r'''Constant True - ROOT 0,0..0,4'''),

('', 0, 0, '_arglike', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .values[1]
   0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, '_arglike', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Call - ROOT 0,0..0,3
  .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglike', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {}, ('MatchAs',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'a' Load - 0,0..0,1
  .op BitOr - 0,2..0,3
  .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_arglike', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', 0, 0, '_arglike', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_arglike', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'a' Load - 0,1..0,2
  .ctx Load
'''),
],

'matrix__arglikes': [  # ................................................................................

('', 0, 0, '_arglikes', {}, ('Module',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('Expression',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('Expr',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('_Assign_targets',
r'''a ='''),
r'''a''',
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('_decorator_list',
r'''@a'''),
r'''a''',
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('_arglikes',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('expr_arglike',
r'''*not a'''),
r'''*not a''',
r'''*(not a)''', r'''
_arglikes - ROOT 0,0..0,6
  .arglikes[1]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'a' Load - 0,5..0,6
     .ctx Load
'''),

('', 0, 0, '_arglikes', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _arglikes, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _arglikes, got Tuple, could not coerce')**'''),

('', 0, 0, '_arglikes', {}, ('NamedExpr',
r'''a := b'''),
r'''(a := b)''',
r'''(a := b)''', r'''
_arglikes - ROOT 0,0..0,8
  .arglikes[1]
   0] NamedExpr - 0,1..0,7
     .target Name 'a' Store - 0,1..0,2
     .value Name 'b' Load - 0,6..0,7
'''),

('', 0, 0, '_arglikes', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
_arglikes - ROOT 0,0..0,5
  .arglikes[1]
   0] BinOp - 0,0..0,5
     .left Name 'a' Load - 0,0..0,1
     .op Add - 0,2..0,3
     .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_arglikes', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
_arglikes - ROOT 0,0..0,2
  .arglikes[1]
   0] UnaryOp - 0,0..0,2
     .op USub - 0,0..0,1
     .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_arglikes', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
_arglikes - ROOT 0,0..0,13
  .arglikes[1]
   0] IfExp - 0,0..0,13
     .test Name 'b' Load - 0,5..0,6
     .body Name 'a' Load - 0,0..0,1
     .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, '_arglikes', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
_arglikes - ROOT 0,0..0,6
  .arglikes[1]
   0] Dict - 0,0..0,6
     .keys[1]
      0] Name 'a' Load - 0,1..0,2
     .values[1]
      0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_arglikes', {}, ('Yield',
r'''yield a'''),
r'''(yield a)''',
r'''(yield a)''', r'''
_arglikes - ROOT 0,0..0,9
  .arglikes[1]
   0] Yield - 0,1..0,8
     .value Name 'a' Load - 0,7..0,8
'''),

('', 0, 0, '_arglikes', {}, ('YieldFrom',
r'''yield from a'''),
r'''(yield from a)''',
r'''(yield from a)''', r'''
_arglikes - ROOT 0,0..0,14
  .arglikes[1]
   0] YieldFrom - 0,1..0,13
     .value Name 'a' Load - 0,12..0,13
'''),

('', 0, 0, '_arglikes', {}, ('Set',
r'''{a}'''),
r'''a''',
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
_arglikes - ROOT 0,0..0,3
  .arglikes[1]
   0] Call - 0,0..0,3
     .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('Constant',
r'''1'''),
r'''1''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Constant 1 - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
_arglikes - ROOT 0,0..0,3
  .arglikes[1]
   0] Attribute - 0,0..0,3
     .value Name 'a' Load - 0,0..0,1
     .attr 'b'
     .ctx Load
'''),

('', 0, 0, '_arglikes', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
_arglikes - ROOT 0,0..0,2
  .arglikes[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Load - 0,1..0,2
     .ctx Load
'''),

('', 0, 0, '_arglikes', {}, ('Name',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('List',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''a''', r'''
_arglikes - ROOT 0,0..0,2
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _arglikes, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _arglikes, got Slice, could not coerce')**'''),

('', 0, 0, '_arglikes', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a''',
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('arguments',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('arg',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('alias',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('_aliases',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('withitem',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('_withitems',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('MatchValue',
r'''1'''),
r'''1''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Constant 1 - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('MatchSingleton',
r'''True'''),
r'''True''', r'''
_arglikes - ROOT 0,0..0,4
  .arglikes[1]
   0] Constant True - 0,0..0,4
'''),

('', 0, 0, '_arglikes', {}, ('MatchSequence',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
_arglikes - ROOT 0,0..0,6
  .arglikes[1]
   0] Dict - 0,0..0,6
     .keys[1]
      0] Constant 1 - 0,1..0,2
     .values[1]
      0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, '_arglikes', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
_arglikes - ROOT 0,0..0,3
  .arglikes[1]
   0] Call - 0,0..0,3
     .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
_arglikes - ROOT 0,0..0,2
  .arglikes[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Load - 0,1..0,2
     .ctx Load
'''),

('', 0, 0, '_arglikes', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
_arglikes - ROOT 0,0..0,5
  .arglikes[1]
   0] BinOp - 0,0..0,5
     .left Name 'a' Load - 0,0..0,1
     .op BitOr - 0,2..0,3
     .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_arglikes', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_arglikes', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
_arglikes - ROOT 0,0..0,2
  .arglikes[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Load - 0,1..0,2
     .ctx Load
'''),

('', 0, 0, '_arglikes', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a''', r'''
_arglikes - ROOT 0,0..0,1
  .arglikes[1]
   0] Name 'a' Load - 0,0..0,1
'''),
],

'matrix__comprehension_ifs': [  # ................................................................................

('', 0, 0, '_comprehension_ifs', {}, ('Module',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Interactive',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Expression',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Expr',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('_Assign_targets',
r'''a ='''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('_decorator_list',
r'''@a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('_arglikes',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting _comprehension_ifs, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _comprehension_ifs, got Starred, could not coerce')**'''),

('', 0, 0, '_comprehension_ifs', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _comprehension_ifs, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _comprehension_ifs, got Tuple, could not coerce')**'''),

('', 0, 0, '_comprehension_ifs', {}, ('NamedExpr',
r'''a := b'''),
r'''if (a := b)''',
r'''if (a := b)''', r'''
_comprehension_ifs - ROOT 0,0..0,11
  .ifs[1]
   0] NamedExpr - 0,4..0,10
     .target Name 'a' Store - 0,4..0,5
     .value Name 'b' Load - 0,9..0,10
'''),

('', 0, 0, '_comprehension_ifs', {}, ('BinOp',
r'''a + b'''),
r'''if a + b''',
r'''if a + b''', r'''
_comprehension_ifs - ROOT 0,0..0,8
  .ifs[1]
   0] BinOp - 0,3..0,8
     .left Name 'a' Load - 0,3..0,4
     .op Add - 0,5..0,6
     .right Name 'b' Load - 0,7..0,8
'''),

('', 0, 0, '_comprehension_ifs', {}, ('UnaryOp',
r'''-a'''),
r'''if -a''',
r'''if -a''', r'''
_comprehension_ifs - ROOT 0,0..0,5
  .ifs[1]
   0] UnaryOp - 0,3..0,5
     .op USub - 0,3..0,4
     .operand Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, '_comprehension_ifs', {}, ('IfExp',
r'''a if b else c'''),
r'''if (a if b else c)''',
r'''if (a if b else c)''', r'''
_comprehension_ifs - ROOT 0,0..0,18
  .ifs[1]
   0] IfExp - 0,4..0,17
     .test Name 'b' Load - 0,9..0,10
     .body Name 'a' Load - 0,4..0,5
     .orelse Name 'c' Load - 0,16..0,17
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Dict',
r'''{a: b}'''),
r'''if {a: b}''',
r'''if {a: b}''', r'''
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[1]
   0] Dict - 0,3..0,9
     .keys[1]
      0] Name 'a' Load - 0,4..0,5
     .values[1]
      0] Name 'b' Load - 0,7..0,8
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Yield',
r'''yield a'''),
r'''if (yield a)''',
r'''if (yield a)''', r'''
_comprehension_ifs - ROOT 0,0..0,12
  .ifs[1]
   0] Yield - 0,4..0,11
     .value Name 'a' Load - 0,10..0,11
'''),

('', 0, 0, '_comprehension_ifs', {}, ('YieldFrom',
r'''yield from a'''),
r'''if (yield from a)''',
r'''if (yield from a)''', r'''
_comprehension_ifs - ROOT 0,0..0,17
  .ifs[1]
   0] YieldFrom - 0,4..0,16
     .value Name 'a' Load - 0,15..0,16
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Set',
r'''{a}'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Call',
r'''a()'''),
r'''if a()''',
r'''if a()''', r'''
_comprehension_ifs - ROOT 0,0..0,6
  .ifs[1]
   0] Call - 0,3..0,6
     .func Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Constant',
r'''1'''),
r'''if 1''',
r'''if 1''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Constant 1 - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Attribute',
r'''a.b'''),
r'''if a.b''',
r'''if a.b''', r'''
_comprehension_ifs - ROOT 0,0..0,6
  .ifs[1]
   0] Attribute - 0,3..0,6
     .value Name 'a' Load - 0,3..0,4
     .attr 'b'
     .ctx Load
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting _comprehension_ifs, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _comprehension_ifs, got Starred, could not coerce')**'''),

('', 0, 0, '_comprehension_ifs', {}, ('Name',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('List',
r'''[a]'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Tuple',
r'''a,'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _comprehension_ifs, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _comprehension_ifs, got Slice, could not coerce')**'''),

('', 0, 0, '_comprehension_ifs', {}, ('_comprehension_ifs',
r'''if a'''),
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('arguments',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('arg',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('alias',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('_aliases',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('withitem',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('_withitems',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('MatchValue',
r'''1'''),
r'''if 1''',
r'''if 1''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Constant 1 - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('MatchSingleton',
r'''True'''),
r'''if True''',
r'''if True''', r'''
_comprehension_ifs - ROOT 0,0..0,7
  .ifs[1]
   0] Constant True - 0,3..0,7
'''),

('', 0, 0, '_comprehension_ifs', {}, ('MatchSequence',
r'''[a]'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('MatchMapping',
r'''{1: a}'''),
r'''if {1: a}''',
r'''if {1: a}''', r'''
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[1]
   0] Dict - 0,3..0,9
     .keys[1]
      0] Constant 1 - 0,4..0,5
     .values[1]
      0] Name 'a' Load - 0,7..0,8
'''),

('', 0, 0, '_comprehension_ifs', {}, ('MatchClass',
r'''a()'''),
r'''if a()''',
r'''if a()''', r'''
_comprehension_ifs - ROOT 0,0..0,6
  .ifs[1]
   0] Call - 0,3..0,6
     .func Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting _comprehension_ifs, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting _comprehension_ifs, got MatchStar, could not coerce')**'''),

('', 0, 0, '_comprehension_ifs', {}, ('MatchAs',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {}, ('MatchOr',
r'''a | b'''),
r'''if a | b''',
r'''if a | b''', r'''
_comprehension_ifs - ROOT 0,0..0,8
  .ifs[1]
   0] BinOp - 0,3..0,8
     .left Name 'a' Load - 0,3..0,4
     .op BitOr - 0,5..0,6
     .right Name 'b' Load - 0,7..0,8
'''),

('', 0, 0, '_comprehension_ifs', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),

('', 0, 0, '_comprehension_ifs', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting _comprehension_ifs, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting _comprehension_ifs, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, '_comprehension_ifs', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''if a''',
r'''if a''', r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'a' Load - 0,3..0,4
'''),
],

'matrix_arguments': [  # ................................................................................

('', 0, 0, 'arguments', {}, ('Module',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('Expression',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('Expr',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('_Assign_targets',
r'''a ='''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('_decorator_list',
r'''@a'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('_arglikes',
r'''a'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting arguments, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Starred, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting arguments, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Tuple, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting arguments, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got NamedExpr, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting arguments, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got BinOp, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting arguments, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting arguments, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got IfExp, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting arguments, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Dict, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting arguments, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Yield, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting arguments, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got YieldFrom, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('Set',
r'''{a}'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting arguments, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Call, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting arguments, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Constant, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('Attribute',
r'''a.b'''),
r'''FST: **NodeError('expecting arguments, got Attribute, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Attribute, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting arguments, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Starred, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('Name',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('List',
r'''[a]'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('Tuple',
r'''a,'''),
r'''a,''', r'''
arguments - ROOT 0,0..0,2
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting arguments, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got Slice, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('arguments',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('arg',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('alias',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('_aliases',
r'''a'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('withitem',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('_withitems',
r'''a'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting arguments, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got MatchValue, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting arguments, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got MatchSingleton, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('MatchSequence',
r'''[a]'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting arguments, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got MatchMapping, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting arguments, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got MatchClass, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting arguments, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got MatchStar, could not coerce')**'''),

('', 0, 0, 'arguments', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting arguments, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got MatchOr, could not coerce')**'''),

('', 0, 0, 'arguments', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),

('', 0, 0, 'arguments', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting arguments, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting arguments, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, 'arguments', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a''',
r'''a,''', r'''
arguments - ROOT 0,0..0,1
  .args[1]
   0] arg - 0,0..0,1
     .arg 'a'
'''),
],

'matrix_arg': [  # ................................................................................

('', 0, 0, 'arg', {}, ('Module',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('Expression',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('Expr',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('_Assign_targets',
r'''a ='''),
r'''FST: **NodeError('expecting arg, got _Assign_targets, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got _Assign_targets, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('_decorator_list',
r'''@a'''),
r'''FST: **NodeError('expecting arg, got _decorator_list, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got _decorator_list, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('_arglikes',
r'''a'''),
r'''FST: **NodeError('expecting arg, got _arglikes, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got _arglikes, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting arg, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Starred, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting arg, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Tuple, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting arg, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got NamedExpr, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting arg, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got BinOp, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting arg, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting arg, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got IfExp, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting arg, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Dict, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting arg, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Yield, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting arg, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got YieldFrom, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Set',
r'''{a}'''),
r'''FST: **NodeError('expecting arg, got Set, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Set, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting arg, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Call, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting arg, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Constant, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Attribute',
r'''a.b'''),
r'''FST: **NodeError('expecting arg, got Attribute, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Attribute, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting arg, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Starred, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Name',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('List',
r'''[a]'''),
r'''FST: **NodeError('expecting arg, got List, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got List, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Tuple',
r'''a,'''),
r'''FST: **NodeError('expecting arg, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Tuple, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting arg, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got Slice, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('_comprehension_ifs',
r'''if a'''),
r'''FST: **NodeError('expecting arg, got _comprehension_ifs, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got _comprehension_ifs, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('arguments',
r'''a'''),
r'''FST: **NodeError('expecting arg, got arguments, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got arguments, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('arg',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('alias',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('_aliases',
r'''a'''),
r'''FST: **NodeError('expecting arg, got _aliases, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got _aliases, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('withitem',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('_withitems',
r'''a'''),
r'''FST: **NodeError('expecting arg, got _withitems, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got _withitems, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting arg, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got MatchValue, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting arg, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got MatchSingleton, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('MatchSequence',
r'''[a]'''),
r'''FST: **NodeError('expecting arg, got MatchSequence, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got MatchSequence, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting arg, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got MatchMapping, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting arg, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got MatchClass, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting arg, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got MatchStar, could not coerce')**'''),

('', 0, 0, 'arg', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting arg, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got MatchOr, could not coerce')**'''),

('', 0, 0, 'arg', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, 0, 'arg', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting arg, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, 'arg', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''FST: **NodeError('expecting arg, got _type_params, could not coerce')**''',
r'''AST: **NodeError('expecting arg, got _type_params, could not coerce')**'''),
],

'matrix_alias': [  # ................................................................................

('', 0, 0, 'alias', {}, ('Module',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('Expression',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('Expr',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('_Assign_targets',
r'''a ='''),
r'''FST: **NodeError('expecting alias, got _Assign_targets, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _Assign_targets, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('_decorator_list',
r'''@a'''),
r'''FST: **NodeError('expecting alias, got _decorator_list, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _decorator_list, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('_arglikes',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _arglikes, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _arglikes, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting alias, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Starred, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting alias, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Tuple, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting alias, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got NamedExpr, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting alias, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got BinOp, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting alias, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting alias, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got IfExp, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting alias, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Dict, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting alias, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Yield, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting alias, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got YieldFrom, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Set',
r'''{a}'''),
r'''FST: **NodeError('expecting alias, got Set, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Set, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting alias, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Call, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting alias, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Constant, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
alias - ROOT 0,0..0,3
  .name 'a.b'
'''),

('', 0, 0, 'alias', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Starred, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Name',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('List',
r'''[a]'''),
r'''FST: **NodeError('expecting alias, got List, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got List, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Tuple',
r'''a,'''),
r'''FST: **NodeError('expecting alias, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Tuple, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting alias, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Slice, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('_comprehension_ifs',
r'''if a'''),
r'''FST: **NodeError('expecting alias, got _comprehension_ifs, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _comprehension_ifs, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('arguments',
r'''a'''),
r'''FST: **NodeError('expecting alias, got arguments, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got arguments, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('arg',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('alias',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('_aliases',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _aliases, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _aliases, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('withitem',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('_withitems',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _withitems, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _withitems, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting alias, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchValue, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting alias, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchSingleton, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('MatchSequence',
r'''[a]'''),
r'''FST: **NodeError('expecting alias, got MatchSequence, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchSequence, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting alias, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchMapping, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting alias, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchClass, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchStar, could not coerce')**'''),

('', 0, 0, 'alias', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting alias, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchOr, could not coerce')**'''),

('', 0, 0, 'alias', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'alias', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, 'alias', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _type_params, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _type_params, could not coerce')**'''),
],

'matrix__aliases': [  # ................................................................................

('', 0, 0, '_aliases', {}, ('Module',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('Expression',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('Expr',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('_Assign_targets',
r'''a ='''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('_decorator_list',
r'''@a'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('_arglikes',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting _aliases, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Starred, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _aliases, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Tuple, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting _aliases, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got NamedExpr, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting _aliases, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got BinOp, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting _aliases, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got UnaryOp, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting _aliases, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got IfExp, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting _aliases, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Dict, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting _aliases, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Yield, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting _aliases, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got YieldFrom, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('Set',
r'''{a}'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting _aliases, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Call, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting _aliases, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Constant, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
_aliases - ROOT 0,0..0,3
  .names[1]
   0] alias - 0,0..0,3
     .name 'a.b'
'''),

('', 0, 0, '_aliases', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Starred, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('Name',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('List',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('Tuple',
r'''a,'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _aliases, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Slice, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('arguments',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('arg',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('alias',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('_aliases',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('withitem',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('_withitems',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting _aliases, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchValue, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting _aliases, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchSingleton, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('MatchSequence',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting _aliases, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchMapping, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting _aliases, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchClass, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchStar, could not coerce')**'''),

('', 0, 0, '_aliases', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting _aliases, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchOr, could not coerce')**'''),

('', 0, 0, '_aliases', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_aliases', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, '_aliases', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),
],

'matrix_Import_name': [  # ................................................................................

('', 0, 0, 'Import_name', {}, ('Module',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('Expression',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('Expr',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('_Assign_targets',
r'''a ='''),
r'''FST: **NodeError('expecting alias, got _Assign_targets, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _Assign_targets, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('_decorator_list',
r'''@a'''),
r'''FST: **NodeError('expecting alias, got _decorator_list, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _decorator_list, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('_arglikes',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _arglikes, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _arglikes, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting alias, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Starred, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting alias, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Tuple, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting alias, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got NamedExpr, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting alias, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got BinOp, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting alias, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting alias, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got IfExp, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting alias, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Dict, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting alias, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Yield, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting alias, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got YieldFrom, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Set',
r'''{a}'''),
r'''FST: **NodeError('expecting alias, got Set, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Set, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting alias, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Call, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting alias, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Constant, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
alias - ROOT 0,0..0,3
  .name 'a.b'
'''),

('', 0, 0, 'Import_name', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Starred, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Name',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('List',
r'''[a]'''),
r'''FST: **NodeError('expecting alias, got List, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got List, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Tuple',
r'''a,'''),
r'''FST: **NodeError('expecting alias, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Tuple, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting alias, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Slice, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('_comprehension_ifs',
r'''if a'''),
r'''FST: **NodeError('expecting alias, got _comprehension_ifs, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _comprehension_ifs, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('arguments',
r'''a'''),
r'''FST: **NodeError('expecting alias, got arguments, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got arguments, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('arg',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('alias',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('_aliases',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _aliases, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _aliases, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('withitem',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('_withitems',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _withitems, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _withitems, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting alias, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchValue, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting alias, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchSingleton, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('MatchSequence',
r'''[a]'''),
r'''FST: **NodeError('expecting alias, got MatchSequence, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchSequence, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting alias, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchMapping, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting alias, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchClass, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchStar, could not coerce')**'''),

('', 0, 0, 'Import_name', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting alias, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchOr, could not coerce')**'''),

('', 0, 0, 'Import_name', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'Import_name', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, 'Import_name', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _type_params, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _type_params, could not coerce')**'''),
],

'matrix__Import_names': [  # ................................................................................

('', 0, 0, '_Import_names', {}, ('Module',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('Expression',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('Expr',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('_Assign_targets',
r'''a ='''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('_decorator_list',
r'''@a'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('_arglikes',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting _aliases, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Starred, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _aliases, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Tuple, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting _aliases, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got NamedExpr, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting _aliases, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got BinOp, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting _aliases, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got UnaryOp, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting _aliases, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got IfExp, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting _aliases, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Dict, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting _aliases, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Yield, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting _aliases, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got YieldFrom, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('Set',
r'''{a}'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting _aliases, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Call, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting _aliases, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Constant, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
_aliases - ROOT 0,0..0,3
  .names[1]
   0] alias - 0,0..0,3
     .name 'a.b'
'''),

('', 0, 0, '_Import_names', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Starred, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('Name',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('List',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('Tuple',
r'''a,'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _aliases, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Slice, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('arguments',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('arg',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('alias',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('_aliases',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('withitem',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('_withitems',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting _aliases, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchValue, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting _aliases, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchSingleton, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('MatchSequence',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting _aliases, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchMapping, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting _aliases, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchClass, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchStar, could not coerce')**'''),

('', 0, 0, '_Import_names', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting _aliases, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchOr, could not coerce')**'''),

('', 0, 0, '_Import_names', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_Import_names', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, '_Import_names', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),
],

'matrix_ImportFrom_name': [  # ................................................................................

('', 0, 0, 'ImportFrom_name', {}, ('Module',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('Expression',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('Expr',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('_Assign_targets',
r'''a ='''),
r'''FST: **NodeError('expecting alias, got _Assign_targets, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _Assign_targets, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('_decorator_list',
r'''@a'''),
r'''FST: **NodeError('expecting alias, got _decorator_list, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _decorator_list, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('_arglikes',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _arglikes, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _arglikes, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting alias, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Starred, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting alias, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Tuple, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting alias, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got NamedExpr, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting alias, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got BinOp, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting alias, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting alias, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got IfExp, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting alias, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Dict, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting alias, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Yield, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting alias, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got YieldFrom, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Set',
r'''{a}'''),
r'''FST: **NodeError('expecting alias, got Set, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Set, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting alias, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Call, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting alias, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Constant, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Attribute',
r'''a.b'''),
r'''FST: **NodeError('expecting alias, got Attribute, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Attribute, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Starred, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Name',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('List',
r'''[a]'''),
r'''FST: **NodeError('expecting alias, got List, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got List, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Tuple',
r'''a,'''),
r'''FST: **NodeError('expecting alias, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Tuple, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting alias, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got Slice, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('_comprehension_ifs',
r'''if a'''),
r'''FST: **NodeError('expecting alias, got _comprehension_ifs, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _comprehension_ifs, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('arguments',
r'''a'''),
r'''FST: **NodeError('expecting alias, got arguments, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got arguments, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('arg',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('alias',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('_aliases',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _aliases, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _aliases, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('withitem',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('_withitems',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _withitems, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _withitems, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting alias, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchValue, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting alias, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchSingleton, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('MatchSequence',
r'''[a]'''),
r'''FST: **NodeError('expecting alias, got MatchSequence, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchSequence, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting alias, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchMapping, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting alias, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchClass, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchStar, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting alias, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got MatchOr, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'ImportFrom_name', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting alias, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, 'ImportFrom_name', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''FST: **NodeError('expecting alias, got _type_params, could not coerce')**''',
r'''AST: **NodeError('expecting alias, got _type_params, could not coerce')**'''),
],

'matrix__ImportFrom_names': [  # ................................................................................

('', 0, 0, '_ImportFrom_names', {}, ('Module',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('Expression',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('Expr',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('_Assign_targets',
r'''a ='''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('_decorator_list',
r'''@a'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('_arglikes',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting _aliases, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Starred, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _aliases, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Tuple, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting _aliases, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got NamedExpr, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting _aliases, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got BinOp, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting _aliases, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got UnaryOp, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting _aliases, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got IfExp, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting _aliases, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Dict, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting _aliases, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Yield, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting _aliases, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got YieldFrom, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('Set',
r'''{a}'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting _aliases, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Call, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting _aliases, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Constant, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('Attribute',
r'''a.b'''),
r'''FST: **NodeError('expecting _aliases, got Attribute, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Attribute, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Starred, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('Name',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('List',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('Tuple',
r'''a,'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _aliases, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got Slice, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('arguments',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('arg',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('alias',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('_aliases',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('withitem',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('_withitems',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting _aliases, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchValue, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting _aliases, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchSingleton, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('MatchSequence',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting _aliases, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchMapping, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting _aliases, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchClass, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchStar, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting _aliases, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got MatchOr, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_ImportFrom_names', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting _aliases, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting _aliases, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, '_ImportFrom_names', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a''', r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),
],

'matrix_withitem': [  # ................................................................................

('', 0, 0, 'withitem', {}, ('Module',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('Expression',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('Expr',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('_Assign_targets',
r'''a ='''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('_decorator_list',
r'''@a'''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('_arglikes',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting withitem, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting withitem, got Starred, could not coerce')**'''),

('', 0, 0, 'withitem', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting withitem, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting withitem, got Tuple, could not coerce')**'''),

('', 0, 0, 'withitem', {}, ('NamedExpr',
r'''a := b'''),
r'''(a := b)''',
r'''(a := b)''', r'''
withitem - ROOT 0,0..0,8
  .context_expr NamedExpr - 0,1..0,7
    .target Name 'a' Store - 0,1..0,2
    .value Name 'b' Load - 0,6..0,7
'''),

('', 0, 0, 'withitem', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
withitem - ROOT 0,0..0,5
  .context_expr BinOp - 0,0..0,5
    .left Name 'a' Load - 0,0..0,1
    .op Add - 0,2..0,3
    .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'withitem', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
withitem - ROOT 0,0..0,2
  .context_expr UnaryOp - 0,0..0,2
    .op USub - 0,0..0,1
    .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'withitem', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
withitem - ROOT 0,0..0,13
  .context_expr IfExp - 0,0..0,13
    .test Name 'b' Load - 0,5..0,6
    .body Name 'a' Load - 0,0..0,1
    .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, 'withitem', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
withitem - ROOT 0,0..0,6
  .context_expr Dict - 0,0..0,6
    .keys[1]
     0] Name 'a' Load - 0,1..0,2
    .values[1]
     0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'withitem', {}, ('Yield',
r'''yield a'''),
r'''(yield a)''',
r'''(yield a)''', r'''
withitem - ROOT 0,0..0,9
  .context_expr Yield - 0,1..0,8
    .value Name 'a' Load - 0,7..0,8
'''),

('', 0, 0, 'withitem', {}, ('YieldFrom',
r'''yield from a'''),
r'''(yield from a)''',
r'''(yield from a)''', r'''
withitem - ROOT 0,0..0,14
  .context_expr YieldFrom - 0,1..0,13
    .value Name 'a' Load - 0,12..0,13
'''),

('', 0, 0, 'withitem', {}, ('Set',
r'''{a}'''),
r'''{a}''', r'''
withitem - ROOT 0,0..0,3
  .context_expr Set - 0,0..0,3
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, 'withitem', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
withitem - ROOT 0,0..0,3
  .context_expr Call - 0,0..0,3
    .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('Constant',
r'''1'''),
r'''1''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Constant 1 - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
withitem - ROOT 0,0..0,3
  .context_expr Attribute - 0,0..0,3
    .value Name 'a' Load - 0,0..0,1
    .attr 'b'
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting withitem, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting withitem, got Starred, could not coerce')**'''),

('', 0, 0, 'withitem', {}, ('Name',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
withitem - ROOT 0,0..0,3
  .context_expr List - 0,0..0,3
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('Tuple',
r'''a,'''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting withitem, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting withitem, got Slice, could not coerce')**'''),

('', 0, 0, 'withitem', {}, ('_comprehension_ifs',
r'''if a'''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('arguments',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('arg',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('alias',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('_aliases',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('withitem',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('_withitems',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('MatchValue',
r'''1'''),
r'''1''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Constant 1 - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('MatchSingleton',
r'''True'''),
r'''True''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Constant True - 0,0..0,4
'''),

('', 0, 0, 'withitem', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
withitem - ROOT 0,0..0,3
  .context_expr List - 0,0..0,3
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'withitem', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
withitem - ROOT 0,0..0,6
  .context_expr Dict - 0,0..0,6
    .keys[1]
     0] Constant 1 - 0,1..0,2
    .values[1]
     0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, 'withitem', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
withitem - ROOT 0,0..0,3
  .context_expr Call - 0,0..0,3
    .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting withitem, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting withitem, got MatchStar, could not coerce')**'''),

('', 0, 0, 'withitem', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
withitem - ROOT 0,0..0,5
  .context_expr BinOp - 0,0..0,5
    .left Name 'a' Load - 0,0..0,1
    .op BitOr - 0,2..0,3
    .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, 'withitem', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'withitem', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting withitem, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting withitem, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, 'withitem', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''(a,)''',
r'''(a,)''', r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[1]
     0] Name 'a' Load - 0,1..0,2
    .ctx Load
'''),
],

'matrix__withitems': [  # ................................................................................

('', 0, 0, '_withitems', {}, ('Module',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('Expression',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('Expr',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('_Assign_targets',
r'''a ='''),
r'''a''',
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('_decorator_list',
r'''@a'''),
r'''a''',
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('_arglikes',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting _withitems, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _withitems, got Starred, could not coerce')**'''),

('', 0, 0, '_withitems', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _withitems, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _withitems, got Tuple, could not coerce')**'''),

('', 0, 0, '_withitems', {}, ('NamedExpr',
r'''a := b'''),
r'''(a := b)''',
r'''(a := b)''', r'''
_withitems - ROOT 0,0..0,8
  .items[1]
   0] withitem - 0,0..0,8
     .context_expr NamedExpr - 0,1..0,7
       .target Name 'a' Store - 0,1..0,2
       .value Name 'b' Load - 0,6..0,7
'''),

('', 0, 0, '_withitems', {}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
_withitems - ROOT 0,0..0,5
  .items[1]
   0] withitem - 0,0..0,5
     .context_expr BinOp - 0,0..0,5
       .left Name 'a' Load - 0,0..0,1
       .op Add - 0,2..0,3
       .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_withitems', {}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
_withitems - ROOT 0,0..0,2
  .items[1]
   0] withitem - 0,0..0,2
     .context_expr UnaryOp - 0,0..0,2
       .op USub - 0,0..0,1
       .operand Name 'a' Load - 0,1..0,2
'''),

('', 0, 0, '_withitems', {}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
_withitems - ROOT 0,0..0,13
  .items[1]
   0] withitem - 0,0..0,13
     .context_expr IfExp - 0,0..0,13
       .test Name 'b' Load - 0,5..0,6
       .body Name 'a' Load - 0,0..0,1
       .orelse Name 'c' Load - 0,12..0,13
'''),

('', 0, 0, '_withitems', {}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Dict - 0,0..0,6
       .keys[1]
        0] Name 'a' Load - 0,1..0,2
       .values[1]
        0] Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_withitems', {}, ('Yield',
r'''yield a'''),
r'''(yield a)''',
r'''(yield a)''', r'''
_withitems - ROOT 0,0..0,9
  .items[1]
   0] withitem - 0,0..0,9
     .context_expr Yield - 0,1..0,8
       .value Name 'a' Load - 0,7..0,8
'''),

('', 0, 0, '_withitems', {}, ('YieldFrom',
r'''yield from a'''),
r'''(yield from a)''',
r'''(yield from a)''', r'''
_withitems - ROOT 0,0..0,14
  .items[1]
   0] withitem - 0,0..0,14
     .context_expr YieldFrom - 0,1..0,13
       .value Name 'a' Load - 0,12..0,13
'''),

('', 0, 0, '_withitems', {}, ('Set',
r'''{a}'''),
r'''a''',
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
_withitems - ROOT 0,0..0,3
  .items[1]
   0] withitem - 0,0..0,3
     .context_expr Call - 0,0..0,3
       .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('Constant',
r'''1'''),
r'''1''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Constant 1 - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
_withitems - ROOT 0,0..0,3
  .items[1]
   0] withitem - 0,0..0,3
     .context_expr Attribute - 0,0..0,3
       .value Name 'a' Load - 0,0..0,1
       .attr 'b'
       .ctx Load
'''),

('', 0, 0, '_withitems', {}, ('Starred',
r'''*a'''),
r'''FST: **NodeError('expecting _withitems, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _withitems, got Starred, could not coerce')**'''),

('', 0, 0, '_withitems', {}, ('Name',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('List',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''a''', r'''
_withitems - ROOT 0,0..0,2
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _withitems, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _withitems, got Slice, could not coerce')**'''),

('', 0, 0, '_withitems', {}, ('_comprehension_ifs',
r'''if a'''),
r'''a''',
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('arguments',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('arg',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('alias',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('_aliases',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('withitem',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('_withitems',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('MatchValue',
r'''1'''),
r'''1''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Constant 1 - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('MatchSingleton',
r'''True'''),
r'''True''', r'''
_withitems - ROOT 0,0..0,4
  .items[1]
   0] withitem - 0,0..0,4
     .context_expr Constant True - 0,0..0,4
'''),

('', 0, 0, '_withitems', {}, ('MatchSequence',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Dict - 0,0..0,6
       .keys[1]
        0] Constant 1 - 0,1..0,2
       .values[1]
        0] Name 'a' Load - 0,4..0,5
'''),

('', 0, 0, '_withitems', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
_withitems - ROOT 0,0..0,3
  .items[1]
   0] withitem - 0,0..0,3
     .context_expr Call - 0,0..0,3
       .func Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('MatchStar',
r'''*a'''),
r'''FST: **NodeError('expecting _withitems, got MatchStar, could not coerce')**''',
r'''AST: **NodeError('expecting _withitems, got MatchStar, could not coerce')**'''),

('', 0, 0, '_withitems', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
_withitems - ROOT 0,0..0,5
  .items[1]
   0] withitem - 0,0..0,5
     .context_expr BinOp - 0,0..0,5
       .left Name 'a' Load - 0,0..0,1
       .op BitOr - 0,2..0,3
       .right Name 'b' Load - 0,4..0,5
'''),

('', 0, 0, '_withitems', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, '_withitems', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''FST: **NodeError('expecting _withitems, got TypeVarTuple, could not coerce')**''',
r'''AST: **NodeError('expecting _withitems, got TypeVarTuple, could not coerce')**'''),

('', 0, 0, '_withitems', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a''', r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),
],

'matrix_pattern': [  # ................................................................................

('', 0, 0, 'pattern', {}, ('Module',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('Interactive',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('Expression',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('Expr',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('_Assign_targets',
r'''a ='''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('_decorator_list',
r'''@a'''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('_arglikes',
r'''a'''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting pattern, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Starred, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting pattern, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Tuple, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting pattern, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got NamedExpr, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting pattern, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got IfExp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting pattern, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Dict, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting pattern, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Yield, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting pattern, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got YieldFrom, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('Set',
r'''{a}'''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('Call',
r'''a()'''),
r'''a()''', r'''
MatchClass - ROOT 0,0..0,3
  .cls Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'pattern', {}, ('Constant',
r'''1'''),
r'''1''', r'''
MatchValue - ROOT 0,0..0,1
  .value Constant 1 - 0,0..0,1
'''),

('', 0, 0, 'pattern', {}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
MatchValue - ROOT 0,0..0,3
  .value Attribute - 0,0..0,3
    .value Name 'a' Load - 0,0..0,1
    .attr 'b'
    .ctx Load
'''),

('', 0, 0, 'pattern', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('Name',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('List',
r'''[a]'''),
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,2
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting pattern, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Slice, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('_comprehension_ifs',
r'''if a'''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('arguments',
r'''a'''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('arg',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('alias',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('_aliases',
r'''a'''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('withitem',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('_withitems',
r'''a'''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('MatchValue',
r'''1'''),
r'''1''', r'''
MatchValue - ROOT 0,0..0,1
  .value Constant 1 - 0,0..0,1
'''),

('', 0, 0, 'pattern', {}, ('MatchSingleton',
r'''True'''),
r'''True''',
r'''MatchSingleton True - ROOT 0,0..0,4'''),

('', 0, 0, 'pattern', {}, ('MatchSequence',
r'''[a]'''),
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
MatchClass - ROOT 0,0..0,3
  .cls Name 'a' Load - 0,0..0,1
'''),

('', 0, 0, 'pattern', {}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('MatchAs',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''[a]''',
r'''[a]''', r'''
MatchSequence - ROOT 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,1..0,2
     .name 'a'
'''),
],

'matrix_type_param': [  # ................................................................................

('', 0, 0, 'type_param', {'_ver': 12}, ('Module',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Interactive',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Expression',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Expr',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('_Assign_targets',
r'''a ='''),
r'''FST: **NodeError('expecting type_param, got _Assign_targets, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got _Assign_targets, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('_decorator_list',
r'''@a'''),
r'''FST: **NodeError('expecting type_param, got _decorator_list, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got _decorator_list, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('_arglikes',
r'''a'''),
r'''FST: **NodeError('expecting type_param, got _arglikes, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got _arglikes, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting type_param, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Starred, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting type_param, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Tuple, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting type_param, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got NamedExpr, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting type_param, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got BinOp, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting type_param, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting type_param, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got IfExp, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting type_param, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Dict, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting type_param, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Yield, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting type_param, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got YieldFrom, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Set',
r'''{a}'''),
r'''FST: **NodeError('expecting type_param, got Set, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Set, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting type_param, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Call, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting type_param, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Constant, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Attribute',
r'''a.b'''),
r'''FST: **NodeError('expecting type_param, got Attribute, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Attribute, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Starred',
r'''*a'''),
r'''*a''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Name',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('List',
r'''[a]'''),
r'''FST: **NodeError('expecting type_param, got List, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got List, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Tuple',
r'''a,'''),
r'''FST: **NodeError('expecting type_param, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Tuple, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting type_param, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got Slice, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('_comprehension_ifs',
r'''if a'''),
r'''FST: **NodeError('expecting type_param, got _comprehension_ifs, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got _comprehension_ifs, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('arguments',
r'''a'''),
r'''FST: **NodeError('expecting type_param, got arguments, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got arguments, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('arg',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('alias',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('_aliases',
r'''a'''),
r'''FST: **NodeError('expecting type_param, got _aliases, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got _aliases, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('withitem',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('_withitems',
r'''a'''),
r'''FST: **NodeError('expecting type_param, got _withitems, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got _withitems, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting type_param, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got MatchValue, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting type_param, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got MatchSingleton, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('MatchSequence',
r'''[a]'''),
r'''FST: **NodeError('expecting type_param, got MatchSequence, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got MatchSequence, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting type_param, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got MatchMapping, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting type_param, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got MatchClass, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('MatchAs',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting type_param, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got MatchOr, could not coerce')**'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

('', 0, 0, 'type_param', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''FST: **NodeError('expecting type_param, got _type_params, could not coerce')**''',
r'''AST: **NodeError('expecting type_param, got _type_params, could not coerce')**'''),
],

'matrix__type_params': [  # ................................................................................

('', 0, 0, '_type_params', {'_ver': 12}, ('Module',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Interactive',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Expression',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Expr',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('_Assign_targets',
r'''a ='''),
r'''a''',
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('_decorator_list',
r'''@a'''),
r'''a''',
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('_arglikes',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('expr_arglike',
r'''*not a'''),
r'''FST: **NodeError('expecting _type_params, got Starred, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got Starred, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting _type_params, got Tuple, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got Tuple, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('NamedExpr',
r'''a := b'''),
r'''FST: **NodeError('expecting _type_params, got NamedExpr, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got NamedExpr, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('BinOp',
r'''a + b'''),
r'''FST: **NodeError('expecting _type_params, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got BinOp, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting _type_params, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got UnaryOp, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('IfExp',
r'''a if b else c'''),
r'''FST: **NodeError('expecting _type_params, got IfExp, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got IfExp, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Dict',
r'''{a: b}'''),
r'''FST: **NodeError('expecting _type_params, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got Dict, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Yield',
r'''yield a'''),
r'''FST: **NodeError('expecting _type_params, got Yield, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got Yield, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('YieldFrom',
r'''yield from a'''),
r'''FST: **NodeError('expecting _type_params, got YieldFrom, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got YieldFrom, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Set',
r'''{a}'''),
r'''a''',
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Call',
r'''a()'''),
r'''FST: **NodeError('expecting _type_params, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got Call, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Constant',
r'''1'''),
r'''FST: **NodeError('expecting _type_params, got Constant, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got Constant, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Attribute',
r'''a.b'''),
r'''FST: **NodeError('expecting _type_params, got Attribute, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got Attribute, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Starred',
r'''*a'''),
r'''*a''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVarTuple - 0,0..0,2
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Name',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('List',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Tuple',
r'''a,'''),
r'''a,''',
r'''a''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting _type_params, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got Slice, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('_comprehension_ifs',
r'''if a'''),
r'''a''',
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('arguments',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('arg',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('alias',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('_aliases',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('withitem',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('_withitems',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('MatchValue',
r'''1'''),
r'''FST: **NodeError('expecting _type_params, got MatchValue, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got MatchValue, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('MatchSingleton',
r'''True'''),
r'''FST: **NodeError('expecting _type_params, got MatchSingleton, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got MatchSingleton, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('MatchSequence',
r'''[a]'''),
r'''a''',
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('MatchMapping',
r'''{1: a}'''),
r'''FST: **NodeError('expecting _type_params, got MatchMapping, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got MatchMapping, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('MatchClass',
r'''a()'''),
r'''FST: **NodeError('expecting _type_params, got MatchClass, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got MatchClass, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVarTuple - 0,0..0,2
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('MatchAs',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('MatchOr',
r'''a | b'''),
r'''FST: **NodeError('expecting _type_params, got MatchOr, could not coerce')**''',
r'''AST: **NodeError('expecting _type_params, got MatchOr, could not coerce')**'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('TypeVar',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
_type_params - ROOT 0,0..0,2
  .type_params[1]
   0] TypeVarTuple - 0,0..0,2
     .name 'a'
'''),

('', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r'''a'''),
r'''a''', r'''
_type_params - ROOT 0,0..0,1
  .type_params[1]
   0] TypeVar - 0,0..0,1
     .name 'a'
'''),
],

'matrix__expr_arglikes': [  # ................................................................................

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Module',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Interactive',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Expression',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Expr',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('_Assign_targets',
r'''a ='''),
r'''a''',
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('_decorator_list',
r'''@a'''),
r'''a''',
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('_arglikes',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('expr_arglike',
r'''*not a'''),
r'''*not a''',
r'''*(not a)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'a' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('expr_slice',
r'''a:b, c:d'''),
r'''FST: **NodeError('expecting non-Slice expressions (arglike), found Slice')**''',
r'''AST: **SyntaxError('invalid expression(s) (arglike)')**'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('NamedExpr',
r'''a := b'''),
r'''a := b''',
r'''(a := b)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] NamedExpr - 0,0..0,6
     .target Name 'a' Store - 0,0..0,1
     .value Name 'b' Load - 0,5..0,6
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('BinOp',
r'''a + b'''),
r'''a + b''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] BinOp - 0,0..0,5
     .left Name 'a' Load - 0,0..0,1
     .op Add - 0,2..0,3
     .right Name 'b' Load - 0,4..0,5
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('UnaryOp',
r'''-a'''),
r'''-a''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] UnaryOp - 0,0..0,2
     .op USub - 0,0..0,1
     .operand Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('IfExp',
r'''a if b else c'''),
r'''a if b else c''', r'''
Tuple - ROOT 0,0..0,13
  .elts[1]
   0] IfExp - 0,0..0,13
     .test Name 'b' Load - 0,5..0,6
     .body Name 'a' Load - 0,0..0,1
     .orelse Name 'c' Load - 0,12..0,13
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Dict',
r'''{a: b}'''),
r'''{a: b}''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Dict - 0,0..0,6
     .keys[1]
      0] Name 'a' Load - 0,1..0,2
     .values[1]
      0] Name 'b' Load - 0,4..0,5
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Yield',
r'''yield a'''),
r'''yield a''',
r'''(yield a)''', r'''
Tuple - ROOT 0,0..0,7
  .elts[1]
   0] Yield - 0,0..0,7
     .value Name 'a' Load - 0,6..0,7
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('YieldFrom',
r'''yield from a'''),
r'''yield from a''',
r'''(yield from a)''', r'''
Tuple - ROOT 0,0..0,12
  .elts[1]
   0] YieldFrom - 0,0..0,12
     .value Name 'a' Load - 0,11..0,12
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Set',
r'''{a}'''),
r'''a''',
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Call',
r'''a()'''),
r'''a()''', r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Call - 0,0..0,3
     .func Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Constant',
r'''1'''),
r'''1''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Constant 1 - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Attribute',
r'''a.b'''),
r'''a.b''', r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Attribute - 0,0..0,3
     .value Name 'a' Load - 0,0..0,1
     .attr 'b'
     .ctx Load
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Name',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('List',
r'''[a]'''),
r'''a''',
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Tuple',
r'''a,'''),
r'''a,''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting Tuple, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Slice, could not coerce')**'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('_comprehension_ifs',
r'''if a'''),
r'''a''',
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('arguments',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('arg',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('alias',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('_aliases',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('withitem',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('_withitems',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('MatchValue',
r'''1'''),
r'''1''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Constant 1 - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('MatchSingleton',
r'''True'''),
r'''True''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Constant True - 0,0..0,4
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('MatchSequence',
r'''[a]'''),
r'''a''',
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('MatchMapping',
r'''{1: a}'''),
r'''{1: a}''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Dict - 0,0..0,6
     .keys[1]
      0] Constant 1 - 0,1..0,2
     .values[1]
      0] Name 'a' Load - 0,4..0,5
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('MatchClass',
r'''a()'''),
r'''a()''', r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Call - 0,0..0,3
     .func Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('MatchStar',
r'''*a'''),
r'''*a''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('MatchAs',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_verify': False}, ('MatchOr',
r'''a | b'''),
r'''a | b''', r'''
Tuple - ROOT 0,0..0,5
  .elts[1]
   0] BinOp - 0,0..0,5
     .left Name 'a' Load - 0,0..0,1
     .op BitOr - 0,2..0,3
     .right Name 'b' Load - 0,4..0,5
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_ver': 12, '_verify': False}, ('TypeVar',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_ver': 12, '_verify': False}, ('TypeVarTuple',
r'''*a'''),
r'''*a''', r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 'a' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('', 0, 0, '_expr_arglikes', {'_ver': 12, '_verify': False}, ('_type_params',
r'''a'''),
r'''a''', r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),
],

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

'_withitems': [  # ................................................................................

('', 0, 0, '_withitems', {}, ('Tuple',
r'''a := b, (yield), (yield from a)'''),
r'''(a := b), (yield), (yield from a)''',
r'''(a := b), (yield), (yield from a)''', r'''
_withitems - ROOT 0,0..0,33
  .items[3]
   0] withitem - 0,0..0,8
     .context_expr NamedExpr - 0,1..0,7
       .target Name 'a' Store - 0,1..0,2
       .value Name 'b' Load - 0,6..0,7
   1] withitem - 0,10..0,17
     .context_expr Yield - 0,11..0,16
   2] withitem - 0,19..0,33
     .context_expr YieldFrom - 0,20..0,32
       .value Name 'a' Load - 0,31..0,32
'''),
],

'expr_context': [  # ................................................................................

('', 0, 0, 'Load', {}, ('Load',
r''''''),
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('', 0, 0, 'Load', {}, ('Del',
r''''''),
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('', 0, 0, 'Load', {}, ('Name',
r'''a'''),
r'''FST: **NodeError('expecting Load, got Name, could not coerce')**''',
r'''AST: **NodeError('expecting Load, got Name, could not coerce')**'''),

('', 0, 0, 'Store', {}, ('Store',
r''''''),
r'''''',
r'''Store - ROOT 0,0..0,0'''),

('', 0, 0, 'Store', {}, ('Del',
r''''''),
r'''''',
r'''Store - ROOT 0,0..0,0'''),

('', 0, 0, 'Store', {}, ('Name',
r'''a'''),
r'''FST: **NodeError('expecting Store, got Name, could not coerce')**''',
r'''AST: **NodeError('expecting Store, got Name, could not coerce')**'''),

('', 0, 0, 'Del', {}, ('Del',
r''''''),
r'''''',
r'''Del - ROOT 0,0..0,0'''),

('', 0, 0, 'Del', {}, ('Load',
r''''''),
r'''''',
r'''Del - ROOT 0,0..0,0'''),

('', 0, 0, 'Del', {}, ('Name',
r'''a'''),
r'''FST: **NodeError('expecting Del, got Name, could not coerce')**''',
r'''AST: **NodeError('expecting Del, got Name, could not coerce')**'''),
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

('', 0, 0, 'pattern', {}, ('UnaryOp',
r'''-a'''),
r'''FST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('UnaryOp',
r'''-(1+1j)'''),
r'''FST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got UnaryOp, could not coerce')**'''),

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

('', 0, 0, 'pattern', {}, ('BinOp',
r'''a+1j'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),
],

'pattern_underscore': [  # ................................................................................

('', 0, 0, 'pattern', {}, ('Attribute',
r'''_.b'''),
r'''FST: **NodeError('expecting pattern, got Attribute, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Attribute, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('Starred',
r'''*_'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2'''),

('', 0, 0, 'pattern', {}, ('Name',
r'''_'''),
r'''_''',
r'''MatchAs - ROOT 0,0..0,1'''),

('', 0, 0, 'pattern', {}, ('arg',
r'''_'''),
r'''_''',
r'''MatchAs - ROOT 0,0..0,1'''),

('', 0, 0, 'pattern', {}, ('alias',
r'''_'''),
r'''_''',
r'''MatchAs - ROOT 0,0..0,1'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('TypeVar',
r'''_'''),
r'''_''',
r'''MatchAs - ROOT 0,0..0,1'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('TypeVarTuple',
r'''*_'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('Dict',
r'''{_: a}'''),
r'''FST: **NodeError('expecting pattern, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Dict, could not coerce')**'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('Dict',
r'''{**_}'''),
r'''FST: **NodeError('expecting pattern, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Dict, could not coerce')**'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('Dict',
r'''{**a, 1: b}'''),
r'''FST: **NodeError('expecting pattern, got Dict, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Dict, could not coerce')**'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('Call',
r'''_()'''),
r'''FST: **NodeError('expecting pattern, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Call, could not coerce')**'''),

('', 0, 0, 'pattern', {'_ver': 12}, ('Call',
r'''_.b()'''),
r'''FST: **NodeError('expecting pattern, got Call, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got Call, could not coerce')**'''),
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

('', 0, 0, '_Assign_targets', {}, ('Attribute', r'''
a.
 b
'''), r'''
a. \
 b
''',
r'''a.b''', r'''
_Assign_targets - ROOT 0,0..1,2
  .targets[1]
   0] Attribute - 0,0..1,2
     .value Name 'a' Load - 0,0..0,1
     .attr 'b'
     .ctx Store
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

('', 0, 0, 'exec', {}, ('_Import_names', r'''
\
a \

'''), r'''
(a,) \

''',
r'''(a,)''', r'''
Module - ROOT 0,0..1,0
  .body[1]
   0] Expr - 0,0..0,4
     .value Tuple - 0,0..0,4
       .elts[1]
        0] Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'stmt', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting stmt, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting stmt, got Slice, could not coerce')**'''),

('', 0, 0, 'stmt', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Expr - ROOT 0,0..0,2
  .value Starred - 0,0..0,2
    .value Name 'a' Load - 0,1..0,2
    .ctx Load
'''),

('', 0, 0, 'stmts', {}, ('Slice',
r'''a:b:c'''),
r'''FST: **NodeError('expecting zero or more stmts, got Slice, could not coerce')**''',
r'''AST: **NodeError('expecting zero or more stmts, got Slice, could not coerce')**'''),

('', 0, 0, 'stmts', {}, ('Starred',
r'''*a'''),
r'''*a''', r'''
Module - ROOT 0,0..0,2
  .body[1]
   0] Expr - 0,0..0,2
     .value Starred - 0,0..0,2
       .value Name 'a' Load - 0,1..0,2
       .ctx Load
'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''{**_} | a'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),

('', 0, 0, 'pattern', {}, ('BinOp',
r'''a | {**_}'''),
r'''FST: **NodeError('expecting pattern, got BinOp, could not coerce')**''',
r'''AST: **NodeError('expecting pattern, got BinOp, could not coerce')**'''),

('', 0, 0, 'List', {}, ('_expr_arglikes',
r'''*not a,'''),
r'''[*(not a),]''',
r'''[*(not a)]''', r'''
List - ROOT 0,0..0,11
  .elts[1]
   0] Starred - 0,1..0,9
     .value UnaryOp - 0,3..0,8
       .op Not - 0,3..0,6
       .operand Name 'a' Load - 0,7..0,8
     .ctx Load
  .ctx Load
'''),

('', 0, 0, 'match_case', {}, ('_match_cases',
r'''case _: pass'''),
r'''FST: **NodeError('expecting match_case, got _match_cases, could not coerce')**''',
r'''AST: **NodeError('expecting match_case, got _match_cases, could not coerce')**'''),

('', 0, 0, '_match_cases', {}, ('ExceptHandler',
r'''except: pass'''),
r'''FST: **NodeError('expecting _match_cases, got ExceptHandler, could not coerce')**''',
r'''AST: **NodeError('expecting _match_cases, got ExceptHandler, could not coerce')**'''),

('', 0, 0, 'List', {}, ('pattern',
r'''a'''),
r'''FST: **NodeError('expecting List, got MatchAs, could not coerce')**''',
r'''AST: **NodeError('expecting List, got MatchAs, could not coerce')**'''),

('', 0, 0, 'Set', {}, ('pattern',
r'''a'''),
r'''FST: **NodeError('expecting Set, got MatchAs, could not coerce')**''',
r'''AST: **NodeError('expecting Set, got MatchAs, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('pattern',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got MatchAs, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got MatchAs, could not coerce')**'''),

('', 0, 0, 'Tuple', {}, ('Name',
r'''a'''),
r'''FST: **NodeError('expecting Tuple, got Name, could not coerce')**''',
r'''AST: **NodeError('expecting Tuple, got Name, could not coerce')**'''),

('', 0, 0, 'List', {}, ('Name',
r'''a'''),
r'''FST: **NodeError('expecting List, got Name, could not coerce')**''',
r'''AST: **NodeError('expecting List, got Name, could not coerce')**'''),

('', 0, 0, 'Set', {}, ('Name',
r'''a'''),
r'''FST: **NodeError('expecting Set, got Name, could not coerce')**''',
r'''AST: **NodeError('expecting Set, got Name, could not coerce')**'''),
],

}
