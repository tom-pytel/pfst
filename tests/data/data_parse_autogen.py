# (case idx, 'parse_function', NOT_USED, NOT_USED, 'expected_class', NOT_USED, (parse_mode, code),
#
# code,
# dump code)
# - OR
# error)

from fst.asttypes import *

DATA_PARSE_AUTOGEN = {
'autogen': [  # ................................................................................

(0, 'parse_stmts', 0, 0, 'Module', {}, ('all', r'''
i: int = 1
j
'''), r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(1, 'parse__ExceptHandlers', 0, 0, '_ExceptHandlers', {}, ('all', r'''
except Exception: pass
except: pass
'''), r'''
_ExceptHandlers - ROOT 0,0..1,12
  .handlers[2]
   0] ExceptHandler - 0,0..0,22
     .type Name 'Exception' Load - 0,7..0,16
     .body[1]
      0] Pass - 0,18..0,22
   1] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
'''),

(2, 'parse__match_cases', 0, 0, '_match_cases', {}, ('all', r'''
case None: pass
case 1: pass
'''), r'''
_match_cases - ROOT 0,0..1,12
  .cases[2]
   0] match_case - 0,0..0,15
     .pattern MatchSingleton None - 0,5..0,9
     .body[1]
      0] Pass - 0,11..0,15
   1] match_case - 1,0..1,12
     .pattern MatchValue - 1,5..1,6
       .value Constant 1 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

(3, 'parse_stmt', 0, 0, 'AnnAssign', {}, ('all',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

(4, 'parse_ExceptHandler', 0, 0, 'ExceptHandler', {}, ('all',
r'''except: pass'''), r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
'''),

(5, 'parse_match_case', 0, 0, 'match_case', {}, ('all',
r'''case None: pass'''), r'''
match_case - ROOT 0,0..0,15
  .pattern MatchSingleton None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

(6, 'parse_stmts', 0, 0, 'Module', {}, ('all', r'''
i: int = 1
j
'''), r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(7, 'parse_stmt', 0, 0, 'AnnAssign', {}, ('all',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

(8, 'parse__ExceptHandlers', 0, 0, '_ExceptHandlers', {}, ('all', r'''
except Exception: pass
except: pass
'''), r'''
_ExceptHandlers - ROOT 0,0..1,12
  .handlers[2]
   0] ExceptHandler - 0,0..0,22
     .type Name 'Exception' Load - 0,7..0,16
     .body[1]
      0] Pass - 0,18..0,22
   1] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
'''),

(9, 'parse_ExceptHandler', 0, 0, 'ExceptHandler', {}, ('all',
r'''except: pass'''), r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
'''),

(10, 'parse__match_cases', 0, 0, '_match_cases', {}, ('all', r'''
case None: pass
case 1: pass
'''), r'''
_match_cases - ROOT 0,0..1,12
  .cases[2]
   0] match_case - 0,0..0,15
     .pattern MatchSingleton None - 0,5..0,9
     .body[1]
      0] Pass - 0,11..0,15
   1] match_case - 1,0..1,12
     .pattern MatchValue - 1,5..1,6
       .value Constant 1 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

(11, 'parse_match_case', 0, 0, 'match_case', {}, ('all',
r'''case None: pass'''), r'''
match_case - ROOT 0,0..0,15
  .pattern MatchSingleton None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

(12, 'parse_expr', 0, 0, 'Name', {}, ('all',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(13, 'parse_expr', 0, 0, 'Starred', {}, ('all',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

(14, 'parse_expr_all', 0, 0, 'Starred', {}, ('all',
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(15, 'parse_stmt', 0, 0, 'AnnAssign', {}, ('all',
r'''a:b'''), r'''
AnnAssign - ROOT 0,0..0,3
  .target Name 'a' Store - 0,0..0,1
  .annotation Name 'b' Load - 0,2..0,3
  .simple 1
'''),

(16, 'parse_expr_all', 0, 0, 'Slice', {}, ('all',
r'''a:b:c'''), r'''
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5
'''),

(17, 'parse_pattern', 0, 0, 'MatchAs', {}, ('all',
r'''1 as a'''), r'''
MatchAs - ROOT 0,0..0,6
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'a'
'''),

(18, 'parse_arguments', 0, 0, 'arguments', {}, ('all',
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''), r'''
arguments - ROOT 0,0..0,43
  .posonlyargs[1]
   0] arg - 0,0..0,12
     .arg 'a'
     .annotation Subscript - 0,3..0,12
       .value Name 'list' Load - 0,3..0,7
       .slice Name 'str' Load - 0,8..0,11
       .ctx Load
  .args[1]
   0] arg - 0,17..0,23
     .arg 'b'
     .annotation Name 'int' Load - 0,20..0,23
  .vararg arg - 0,30..0,31
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 0,33..0,34
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 0,35..0,38
  .kwarg arg - 0,42..0,43
    .arg 'e'
  .defaults[1]
   0] Constant 1 - 0,26..0,27
'''),

(19, 'parse_arguments_lambda', 0, 0, 'arguments', {}, ('all',
r'''a, /, b, *c, d=100, **e'''), r'''
arguments - ROOT 0,0..0,23
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'b'
  .vararg arg - 0,10..0,11
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 0,13..0,14
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 0,15..0,18
  .kwarg arg - 0,22..0,23
    .arg 'e'
'''),

(20, 'parse_arguments', 0, 0, 'arguments', {}, ('all',
r'''**a: dict'''), r'''
arguments - ROOT 0,0..0,9
  .kwarg arg - 0,2..0,9
    .arg 'a'
    .annotation Name 'dict' Load - 0,5..0,9
'''),

(21, 'parse_pattern', 0, 0, 'MatchSequence', {}, ('all',
r'''*a, b as c'''), r'''
MatchSequence - ROOT 0,0..0,10
  .patterns[2]
   0] MatchStar - 0,0..0,2
     .name 'a'
   1] MatchAs - 0,4..0,10
     .pattern MatchAs - 0,4..0,5
       .name 'b'
     .name 'c'
'''),

(22, 'parse_comprehension', 0, 0, 'comprehension', {}, ('all',
r'''for i in range(5) if i'''), r'''
comprehension - ROOT 0,0..0,22
  .target Name 'i' Store - 0,4..0,5
  .iter Call - 0,9..0,17
    .func Name 'range' Load - 0,9..0,14
    .args[1]
     0] Constant 5 - 0,15..0,16
  .ifs[1]
   0] Name 'i' Load - 0,21..0,22
  .is_async 0
'''),

(23, 'parse_withitem', 0, 0, 'withitem', {}, ('all',
r'''f(**a) as b'''), r'''
withitem - ROOT 0,0..0,11
  .context_expr Call - 0,0..0,6
    .func Name 'f' Load - 0,0..0,1
    .keywords[1]
     0] keyword - 0,2..0,5
       .value Name 'a' Load - 0,4..0,5
  .optional_vars Name 'b' Store - 0,10..0,11
'''),

(24, 'parse_operator', 0, 0, 'Mult', {}, ('all',
r'''*'''),
r'''Mult - ROOT 0,0..0,1'''),

(25, 'parse_augop', 0, 0, 'Mult', {}, ('all',
r'''*='''),
r'''Mult - ROOT 0,0..0,2'''),

(26, 'parse_cmpop', 0, 0, 'Gt', {}, ('all',
r'''>'''),
r'''Gt - ROOT 0,0..0,1'''),

(27, 'parse_boolop', 0, 0, 'And', {}, ('all',
r'''and'''),
r'''And - ROOT 0,0..0,3'''),

(28, 'parse_unaryop', 0, 0, 'Invert', {}, ('all',
r'''~'''),
r'''Invert - ROOT 0,0..0,1'''),

(29, 'parse_stmts', 0, 0, 'Module', {}, ('strict', r'''
i: int = 1
j
'''), r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(30, 'parse__ExceptHandlers', 0, 0, 'SyntaxError', {}, ('strict', r'''
except Exception: pass
except: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

(31, 'parse__match_cases', 0, 0, 'SyntaxError', {}, ('strict', r'''
case None: pass
case 1: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

(32, 'parse_stmt', 0, 0, 'AnnAssign', {}, ('strict',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

(33, 'parse_ExceptHandler', 0, 0, 'SyntaxError', {}, ('strict',
r'''except: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

(34, 'parse_match_case', 0, 0, 'SyntaxError', {}, ('strict',
r'''case None: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

(35, 'parse_stmts', 0, 0, 'Module', {}, ('strict', r'''
i: int = 1
j
'''), r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(36, 'parse_stmt', 0, 0, 'AnnAssign', {}, ('strict',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

(37, 'parse__ExceptHandlers', 0, 0, 'SyntaxError', {}, ('strict', r'''
except Exception: pass
except: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

(38, 'parse_ExceptHandler', 0, 0, 'SyntaxError', {}, ('strict',
r'''except: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

(39, 'parse__match_cases', 0, 0, 'SyntaxError', {}, ('strict', r'''
case None: pass
case 1: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

(40, 'parse_match_case', 0, 0, 'SyntaxError', {}, ('strict',
r'''case None: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

(41, 'parse_expr', 0, 0, 'Name', {}, ('strict',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(42, 'parse_expr', 0, 0, 'Starred', {}, ('strict',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

(43, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''*not a'''),
r'''**SyntaxError('invalid syntax')**'''),

(44, 'parse_stmt', 0, 0, 'AnnAssign', {}, ('strict',
r'''a:b'''), r'''
AnnAssign - ROOT 0,0..0,3
  .target Name 'a' Store - 0,0..0,1
  .annotation Name 'b' Load - 0,2..0,3
  .simple 1
'''),

(45, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''a:b:c'''),
r'''**SyntaxError('invalid syntax')**'''),

(46, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''1 as a'''),
r'''**SyntaxError('invalid syntax')**'''),

(47, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''**SyntaxError('invalid syntax')**'''),

(48, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''a, /, b, *c, d=100, **e'''),
r'''**SyntaxError('invalid syntax')**'''),

(49, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''*not a'''),
r'''**SyntaxError('invalid syntax')**'''),

(50, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''for i in range(5) if i'''),
r'''**SyntaxError("expected 'else' after 'if' expression")**'''),

(51, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''f(**a) as b'''),
r'''**SyntaxError('invalid syntax')**'''),

(52, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''*'''),
r'''**SyntaxError('invalid syntax')**'''),

(53, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''*='''),
r'''**SyntaxError('invalid syntax')**'''),

(54, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''>'''),
r'''**SyntaxError('invalid syntax')**'''),

(55, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''and'''),
r'''**SyntaxError('invalid syntax')**'''),

(56, 'parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''~'''),
r'''**SyntaxError('invalid syntax')**'''),

(57, 'parse_Module', 0, 0, 'Module', {}, ('exec',
r'''i: int = 1'''), r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
'''),

(58, 'parse_Expression', 0, 0, 'Expression', {}, ('eval',
r'''None'''), r'''
Expression - ROOT 0,0..0,4
  .body Constant None - 0,0..0,4
'''),

(59, 'parse_Interactive', 0, 0, 'Interactive', {}, ('single',
r'''i: int = 1'''), r'''
Interactive - ROOT 0,0..0,10
  .body[1]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
'''),

(60, 'parse_stmts', 0, 0, 'Module', {}, ('stmts', r'''
i: int = 1
j
'''), r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
   1] Expr - 1,0..1,1
     .value Name 'j' Load - 1,0..1,1
'''),

(61, 'parse_stmts', 0, 0, 'SyntaxError', {}, ('stmts', r'''
except Exception: pass
except: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

(62, 'parse_stmt', 0, 0, 'AnnAssign', {}, ('stmt',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

(63, 'parse_stmt', 0, 0, 'Expr', {}, ('stmt',
r'''j'''), r'''
Expr - ROOT 0,0..0,1
  .value Name 'j' Load - 0,0..0,1
'''),

(64, 'parse_stmt', 0, 0, 'ParseError', {}, ('stmt', r'''
i: int = 1
j
'''),
r'''**ParseError('expecting single stmt')**'''),

(65, 'parse_stmt', 0, 0, 'SyntaxError', {}, ('stmt',
r'''except: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

(66, 'parse__ExceptHandlers', 0, 0, '_ExceptHandlers', {}, ('_ExceptHandlers', r'''
except Exception: pass
except: pass
'''), r'''
_ExceptHandlers - ROOT 0,0..1,12
  .handlers[2]
   0] ExceptHandler - 0,0..0,22
     .type Name 'Exception' Load - 0,7..0,16
     .body[1]
      0] Pass - 0,18..0,22
   1] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
'''),

(67, 'parse__ExceptHandlers', 0, 0, 'IndentationError', {}, ('_ExceptHandlers', r'''
 except Exception: pass
except: pass
'''),
r'''**IndentationError('unexpected indent')**'''),

(68, 'parse__ExceptHandlers', 0, 0, 'ParseError', {}, ('_ExceptHandlers', r'''
except Exception: pass
except: pass
else: pass
'''),
r'''**ParseError("not expecting 'else' block")**'''),

(69, 'parse__ExceptHandlers', 0, 0, 'ParseError', {}, ('_ExceptHandlers', r'''
except Exception: pass
except: pass
finally: pass
'''),
r'''**ParseError("not expecting 'finally' block")**'''),

(70, 'parse__ExceptHandlers', 0, 0, 'SyntaxError', {}, ('_ExceptHandlers', r'''
i: int = 1
j
'''),
r'''**SyntaxError("expected 'except' or 'finally' block")**'''),

(71, 'parse_ExceptHandler', 0, 0, 'ExceptHandler', {}, ('ExceptHandler',
r'''except: pass'''), r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
'''),

(72, 'parse_ExceptHandler', 0, 0, 'ParseError', {}, ('ExceptHandler', r'''
except Exception: pass
except: pass
'''),
r'''**ParseError('expecting single ExceptHandler')**'''),

(73, 'parse_ExceptHandler', 0, 0, 'SyntaxError', {}, ('ExceptHandler',
r'''i: int = 1'''),
r'''**SyntaxError("expected 'except' or 'finally' block")**'''),

(74, 'parse__match_cases', 0, 0, '_match_cases', {}, ('_match_cases', r'''
case None: pass
case 1: pass
'''), r'''
_match_cases - ROOT 0,0..1,12
  .cases[2]
   0] match_case - 0,0..0,15
     .pattern MatchSingleton None - 0,5..0,9
     .body[1]
      0] Pass - 0,11..0,15
   1] match_case - 1,0..1,12
     .pattern MatchValue - 1,5..1,6
       .value Constant 1 - 1,5..1,6
     .body[1]
      0] Pass - 1,8..1,12
'''),

(75, 'parse__match_cases', 0, 0, 'IndentationError', {}, ('_match_cases', r'''
 case None: pass
case 1: pass
'''),
r'''**IndentationError('unexpected indent')**'''),

(76, 'parse__match_cases', 0, 0, 'SyntaxError', {}, ('_match_cases',
r'''i: int = 1'''),
r'''**SyntaxError('invalid syntax')**'''),

(77, 'parse_match_case', 0, 0, 'match_case', {}, ('match_case',
r'''case None: pass'''), r'''
match_case - ROOT 0,0..0,15
  .pattern MatchSingleton None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

(78, 'parse_match_case', 0, 0, 'ParseError', {}, ('match_case', r'''
case None: pass
case 1: pass
'''),
r'''**ParseError('expecting single match_case')**'''),

(79, 'parse_match_case', 0, 0, 'SyntaxError', {}, ('match_case',
r'''i: int = 1'''),
r'''**SyntaxError('invalid syntax')**'''),

(80, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r''''''),
r'''_Assign_targets - ROOT 0,0..0,0'''),

(81, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a'''), r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

(82, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a ='''), r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

(83, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a = b'''), r'''
_Assign_targets - ROOT 0,0..0,5
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
'''),

(84, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a = b ='''), r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
'''),

(85, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets', r'''
\
a\
 = \

'''), r'''
_Assign_targets - ROOT 0,0..3,0
  .targets[1]
   0] Name 'a' Store - 1,0..1,1
'''),

(86, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r''' a'''), r'''
_Assign_targets - ROOT 0,0..0,2
  .targets[1]
   0] Name 'a' Store - 0,1..0,2
'''),

(87, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets', r'''

a
'''), r'''
_Assign_targets - ROOT 0,0..1,1
  .targets[1]
   0] Name 'a' Store - 1,0..1,1
'''),

(88, 'parse__Assign_targets', 0, 0, 'SyntaxError', {}, ('_Assign_targets', r'''


a
'''),
r'''**SyntaxError('invalid Assign targets slice')**'''),

(89, 'parse__Assign_targets', 0, 0, 'SyntaxError', {}, ('_Assign_targets', r'''
a
=
'''),
r'''**SyntaxError('invalid Assign targets slice')**'''),

(90, 'parse__Assign_targets', 0, 0, 'SyntaxError', {}, ('_Assign_targets',
r'''a =  # tail'''),
r'''**SyntaxError('invalid Assign targets slice')**'''),

(91, 'parse__Assign_targets', 0, 0, 'SyntaxError', {}, ('_Assign_targets', r'''
# head
a =
'''),
r'''**SyntaxError('invalid Assign targets slice')**'''),

(92, 'parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('all',
r'''a = b ='''), r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
'''),

(93, 'parse_expr', 0, 0, 'Name', {}, ('expr',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(94, 'parse_expr', 0, 0, 'Starred', {}, ('expr',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

(95, 'parse_expr', 0, 0, 'Starred', {}, ('expr', r'''
*
s
'''), r'''
Starred - ROOT 0,0..1,1
  .value Name 's' Load - 1,0..1,1
  .ctx Load
'''),

(96, 'parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
*
s,
'''), r'''
Tuple - ROOT 0,0..1,2
  .elts[1]
   0] Starred - 0,0..1,1
     .value Name 's' Load - 1,0..1,1
     .ctx Load
  .ctx Load
'''),

(97, 'parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
1
,
2
,
'''), r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Constant 1 - 0,0..0,1
   1] Constant 2 - 2,0..2,1
  .ctx Load
'''),

(98, 'parse_expr', 0, 0, 'SyntaxError', {}, ('expr',
r'''*not a'''),
r'''**SyntaxError('invalid expression')**'''),

(99, 'parse_expr', 0, 0, 'SyntaxError', {}, ('expr',
r'''a:b'''),
r'''**SyntaxError('invalid expression')**'''),

(100, 'parse_expr', 0, 0, 'SyntaxError', {}, ('expr',
r'''a:b:c'''),
r'''**SyntaxError('invalid expression')**'''),

(101, 'parse_expr_all', 0, 0, 'Name', {}, ('expr_all',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(102, 'parse_expr_all', 0, 0, 'Starred', {}, ('expr_all',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

(103, 'parse_expr_all', 0, 0, 'Starred', {}, ('expr_all', r'''
*
s
'''), r'''
Starred - ROOT 0,0..1,1
  .value Name 's' Load - 1,0..1,1
  .ctx Load
'''),

(104, 'parse_expr_all', 0, 0, 'Tuple', {}, ('expr_all', r'''
*
s,
'''), r'''
Tuple - ROOT 0,0..1,2
  .elts[1]
   0] Starred - 0,0..1,1
     .value Name 's' Load - 1,0..1,1
     .ctx Load
  .ctx Load
'''),

(105, 'parse_expr_all', 0, 0, 'Tuple', {}, ('expr_all', r'''
1
,
2
,
'''), r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Constant 1 - 0,0..0,1
   1] Constant 2 - 2,0..2,1
  .ctx Load
'''),

(106, 'parse_expr_all', 0, 0, 'Slice', {}, ('expr_all',
r'''a:b'''), r'''
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
'''),

(107, 'parse_expr_all', 0, 0, 'Slice', {}, ('expr_all',
r'''a:b:c'''), r'''
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5
'''),

(108, 'parse_expr_all', 0, 0, 'Tuple', {}, ('expr_all',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

(109, 'parse_expr_all', 0, 0, 'Tuple', {}, ('expr_all',
r'''a:b:c, x:y:z'''), r'''
Tuple - ROOT 0,0..0,12
  .elts[2]
   0] Slice - 0,0..0,5
     .lower Name 'a' Load - 0,0..0,1
     .upper Name 'b' Load - 0,2..0,3
     .step Name 'c' Load - 0,4..0,5
   1] Slice - 0,7..0,12
     .lower Name 'x' Load - 0,7..0,8
     .upper Name 'y' Load - 0,9..0,10
     .step Name 'z' Load - 0,11..0,12
  .ctx Load
'''),

(110, 'parse_expr_arglike', 0, 0, 'Name', {}, ('expr_arglike',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(111, 'parse_expr_arglike', 0, 0, 'Starred', {}, ('expr_arglike',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

(112, 'parse_expr_arglike', 0, 0, 'Tuple', {}, ('expr_arglike',
r'''*s,'''), r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 's' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

(113, 'parse_expr_arglike', 0, 0, 'Starred', {}, ('expr_arglike',
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(114, 'parse_expr_arglike', 0, 0, 'SyntaxError', {}, ('expr_arglike',
r'''*not a,'''),
r'''**SyntaxError('invalid argument-like expression')**'''),

(115, 'parse_expr_arglike', 0, 0, 'Tuple', {}, ('expr_arglike',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

(116, 'parse_expr_arglike', 0, 0, 'ParseError', {}, ('expr_arglike',
r'''i=1'''),
r'''**ParseError('expecting single argumnent-like expression')**'''),

(117, 'parse_expr_arglike', 0, 0, 'SyntaxError', {}, ('expr_arglike',
r'''a:b'''),
r'''**SyntaxError('invalid argument-like expression')**'''),

(118, 'parse_expr_arglike', 0, 0, 'SyntaxError', {}, ('expr_arglike',
r'''a:b:c'''),
r'''**SyntaxError('invalid argument-like expression')**'''),

(119, 'parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''j'''), r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'j' Load - 0,0..0,1
  .ctx Load
'''),

(120, 'parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''*s'''), r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 's' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

(121, 'parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''*s,'''), r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 's' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

(122, 'parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''*not a'''), r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'a' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(123, 'parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''*not a,'''), r'''
Tuple - ROOT 0,0..0,7
  .elts[1]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'a' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(124, 'parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''*not a, *b or c'''), r'''
Tuple - ROOT 0,0..0,15
  .elts[2]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'a' Load - 0,5..0,6
     .ctx Load
   1] Starred - 0,8..0,15
     .value BoolOp - 0,9..0,15
       .op Or
       .values[2]
        0] Name 'b' Load - 0,9..0,10
        1] Name 'c' Load - 0,14..0,15
     .ctx Load
  .ctx Load
'''),

(125, 'parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

(126, 'parse__expr_arglikes', 0, 0, 'ParseError', {}, ('_expr_arglikes',
r'''i=1'''),
r'''**ParseError('expecting only argumnent-like expression(s), got keyword')**'''),

(127, 'parse__expr_arglikes', 0, 0, 'SyntaxError', {}, ('_expr_arglikes',
r'''a:b'''),
r'''**SyntaxError('invalid argument-like expression(s)')**'''),

(128, 'parse__expr_arglikes', 0, 0, 'SyntaxError', {}, ('_expr_arglikes',
r'''a:b:c'''),
r'''**SyntaxError('invalid argument-like expression(s)')**'''),

(129, 'parse_expr_slice', 0, 0, 'Name', {}, ('expr_slice',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(130, 'parse_expr_slice', 0, 0, 'Slice', {}, ('expr_slice',
r'''a:b'''), r'''
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
'''),

(131, 'parse_expr_slice', 0, 0, 'Tuple', {}, ('expr_slice',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

(132, 'parse_expr_slice', 0, 0, 'Tuple', {}, ('expr_slice',
r'''a:b:c, x:y:z'''), r'''
Tuple - ROOT 0,0..0,12
  .elts[2]
   0] Slice - 0,0..0,5
     .lower Name 'a' Load - 0,0..0,1
     .upper Name 'b' Load - 0,2..0,3
     .step Name 'c' Load - 0,4..0,5
   1] Slice - 0,7..0,12
     .lower Name 'x' Load - 0,7..0,8
     .upper Name 'y' Load - 0,9..0,10
     .step Name 'z' Load - 0,11..0,12
  .ctx Load
'''),

(133, 'parse_expr_sliceelt', 0, 0, 'Name', {}, ('expr_sliceelt',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(134, 'parse_expr_sliceelt', 0, 0, 'Slice', {}, ('expr_sliceelt',
r'''a:b'''), r'''
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
'''),

(135, 'parse_expr_sliceelt', 0, 0, 'Tuple', {}, ('expr_sliceelt',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

(136, 'parse_expr_sliceelt', 0, 0, 'SyntaxError', {}, ('expr_sliceelt',
r'''a:b:c, x:y:z'''),
r'''**SyntaxError('invalid expression')**'''),

(137, 'parse_boolop', 0, 0, 'And', {}, ('boolop',
r'''and'''),
r'''And - ROOT 0,0..0,3'''),

(138, 'parse_boolop', 0, 0, 'ParseError', {}, ('boolop',
r'''*'''),
r'''**ParseError("expecting boolop, got '*'")**'''),

(139, 'parse_operator', 0, 0, 'Mult', {}, ('operator',
r'''*'''),
r'''Mult - ROOT 0,0..0,1'''),

(140, 'parse_operator', 0, 0, 'Mult', {}, ('operator',
r'''*='''),
r'''Mult - ROOT 0,0..0,2'''),

(141, 'parse_operator', 0, 0, 'ParseError', {}, ('operator',
r'''and'''),
r'''**ParseError("expecting operator, got 'and'")**'''),

(142, 'parse_binop', 0, 0, 'Mult', {}, ('binop',
r'''*'''),
r'''Mult - ROOT 0,0..0,1'''),

(143, 'parse_binop', 0, 0, 'SyntaxError', {}, ('binop',
r'''*='''),
r'''**SyntaxError('invalid syntax')**'''),

(144, 'parse_augop', 0, 0, 'ParseError', {}, ('augop',
r'''*'''),
r'''**ParseError("expecting augmented operator, got '*'")**'''),

(145, 'parse_augop', 0, 0, 'Mult', {}, ('augop',
r'''*='''),
r'''Mult - ROOT 0,0..0,2'''),

(146, 'parse_unaryop', 0, 0, 'UAdd', {}, ('unaryop',
r'''+'''),
r'''UAdd - ROOT 0,0..0,1'''),

(147, 'parse_unaryop', 0, 0, 'SyntaxError', {}, ('unaryop',
r'''and'''),
r'''**SyntaxError('invalid syntax')**'''),

(148, 'parse_cmpop', 0, 0, 'GtE', {}, ('cmpop',
r'''>='''),
r'''GtE - ROOT 0,0..0,2'''),

(149, 'parse_cmpop', 0, 0, 'IsNot', {}, ('cmpop', r'''
is
not
'''),
r'''IsNot - ROOT 0,0..1,3'''),

(150, 'parse_cmpop', 0, 0, 'ParseError', {}, ('cmpop',
r'''>= a >='''),
r'''**ParseError('expecting single cmpop')**'''),

(151, 'parse_cmpop', 0, 0, 'ParseError', {}, ('cmpop',
r'''and'''),
r'''**ParseError("expecting cmpop, got 'and'")**'''),

(152, 'parse_comprehension', 0, 0, 'comprehension', {}, ('comprehension',
r'''for u in v'''), r'''
comprehension - ROOT 0,0..0,10
  .target Name 'u' Store - 0,4..0,5
  .iter Name 'v' Load - 0,9..0,10
  .is_async 0
'''),

(153, 'parse_comprehension', 0, 0, 'comprehension', {}, ('comprehension',
r'''for u in v if w'''), r'''
comprehension - ROOT 0,0..0,15
  .target Name 'u' Store - 0,4..0,5
  .iter Name 'v' Load - 0,9..0,10
  .ifs[1]
   0] Name 'w' Load - 0,14..0,15
  .is_async 0
'''),

(154, 'parse_comprehension', 0, 0, 'ParseError', {}, ('comprehension',
r'''for u in v for s in t'''),
r'''**ParseError('expecting single comprehension')**'''),

(155, 'parse_arguments', 0, 0, 'arguments', {}, ('arguments',
r''''''),
r'''arguments - ROOT'''),

(156, 'parse_arguments', 0, 0, 'arguments', {}, ('arguments',
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''), r'''
arguments - ROOT 0,0..0,43
  .posonlyargs[1]
   0] arg - 0,0..0,12
     .arg 'a'
     .annotation Subscript - 0,3..0,12
       .value Name 'list' Load - 0,3..0,7
       .slice Name 'str' Load - 0,8..0,11
       .ctx Load
  .args[1]
   0] arg - 0,17..0,23
     .arg 'b'
     .annotation Name 'int' Load - 0,20..0,23
  .vararg arg - 0,30..0,31
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 0,33..0,34
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 0,35..0,38
  .kwarg arg - 0,42..0,43
    .arg 'e'
  .defaults[1]
   0] Constant 1 - 0,26..0,27
'''),

(157, 'parse_arguments_lambda', 0, 0, 'arguments', {}, ('arguments_lambda',
r''''''),
r'''arguments - ROOT'''),

(158, 'parse_arguments_lambda', 0, 0, 'arguments', {}, ('arguments_lambda',
r'''a, /, b, *c, d=100, **e'''), r'''
arguments - ROOT 0,0..0,23
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'b'
  .vararg arg - 0,10..0,11
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 0,13..0,14
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 0,15..0,18
  .kwarg arg - 0,22..0,23
    .arg 'e'
'''),

(159, 'parse_arguments_lambda', 0, 0, 'arguments', {}, ('arguments_lambda', r'''
a,
/,
b,
*c,
d=100,
**e
'''), r'''
arguments - ROOT 0,0..5,3
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .args[1]
   0] arg - 2,0..2,1
     .arg 'b'
  .vararg arg - 3,1..3,2
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 4,0..4,1
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 4,2..4,5
  .kwarg arg - 5,2..5,3
    .arg 'e'
'''),

(160, 'parse_arguments_lambda', 0, 0, 'SyntaxError', {}, ('arguments_lambda',
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''**SyntaxError('invalid syntax')**'''),

(161, 'parse_arg', 0, 0, 'arg', {}, ('arg',
r'''a: b'''), r'''
arg - ROOT 0,0..0,4
  .arg 'a'
  .annotation Name 'b' Load - 0,3..0,4
'''),

(162, 'parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''a: b = c'''),
r'''**ParseError('expecting single argument without default')**'''),

(163, 'parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''a, b'''),
r'''**ParseError('expecting single argument without default')**'''),

(164, 'parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''a, /'''),
r'''**ParseError('expecting single argument without default')**'''),

(165, 'parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''*, a'''),
r'''**ParseError('expecting single argument without default')**'''),

(166, 'parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''*a'''),
r'''**ParseError('expecting single argument without default')**'''),

(167, 'parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''**a'''),
r'''**ParseError('expecting single argument without default')**'''),

(168, 'parse_keyword', 0, 0, 'keyword', {}, ('keyword',
r'''a=1'''), r'''
keyword - ROOT 0,0..0,3
  .arg 'a'
  .value Constant 1 - 0,2..0,3
'''),

(169, 'parse_keyword', 0, 0, 'keyword', {}, ('keyword',
r'''**a'''), r'''
keyword - ROOT 0,0..0,3
  .value Name 'a' Load - 0,2..0,3
'''),

(170, 'parse_keyword', 0, 0, 'ParseError', {}, ('keyword',
r'''1'''),
r'''**ParseError('expecting single keyword')**'''),

(171, 'parse_keyword', 0, 0, 'ParseError', {}, ('keyword',
r'''a'''),
r'''**ParseError('expecting single keyword')**'''),

(172, 'parse_keyword', 0, 0, 'ParseError', {}, ('keyword',
r'''a=1, b=2'''),
r'''**ParseError('expecting single keyword')**'''),

(173, 'parse_alias', 0, 0, 'SyntaxError', {}, ('alias',
r''''''),
r'''**SyntaxError("Expected one or more names after 'import'")**'''),

(174, 'parse_alias', 0, 0, 'alias', {}, ('alias',
r'''a'''), r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

(175, 'parse_alias', 0, 0, 'alias', {}, ('alias',
r'''a.b'''), r'''
alias - ROOT 0,0..0,3
  .name 'a.b'
'''),

(176, 'parse_alias', 0, 0, 'alias', {}, ('alias',
r'''*'''), r'''
alias - ROOT 0,0..0,1
  .name '*'
'''),

(177, 'parse_alias', 0, 0, 'ParseError', {}, ('alias',
r'''a, b'''),
r'''**ParseError('expecting single name')**'''),

(178, 'parse_alias', 0, 0, 'alias', {}, ('alias',
r'''a as c'''), r'''
alias - ROOT 0,0..0,6
  .name 'a'
  .asname 'c'
'''),

(179, 'parse_alias', 0, 0, 'alias', {}, ('alias',
r'''a.b as c'''), r'''
alias - ROOT 0,0..0,8
  .name 'a.b'
  .asname 'c'
'''),

(180, 'parse_alias', 0, 0, 'SyntaxError', {}, ('alias',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(181, 'parse_alias', 0, 0, 'ParseError', {}, ('alias',
r'''a as x, b as y'''),
r'''**ParseError('expecting single name')**'''),

(182, 'parse_alias', 0, 0, 'ParseError', {}, ('alias',
r'''a as x, a.b as y'''),
r'''**ParseError('expecting single name')**'''),

(183, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r''''''),
r'''_aliases - ROOT 0,0..0,0'''),

(184, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

(185, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a.b'''), r'''
_aliases - ROOT 0,0..0,3
  .names[1]
   0] alias - 0,0..0,3
     .name 'a.b'
'''),

(186, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''*'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name '*'
'''),

(187, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a, b'''), r'''
_aliases - ROOT 0,0..0,4
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
'''),

(188, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a as c'''), r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'c'
'''),

(189, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a.b as c'''), r'''
_aliases - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,0..0,8
     .name 'a.b'
     .asname 'c'
'''),

(190, 'parse__aliases', 0, 0, 'SyntaxError', {}, ('_aliases',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(191, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a as x, b as y'''), r'''
_aliases - ROOT 0,0..0,14
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'x'
   1] alias - 0,8..0,14
     .name 'b'
     .asname 'y'
'''),

(192, 'parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a as x, a.b as y'''), r'''
_aliases - ROOT 0,0..0,16
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'x'
   1] alias - 0,8..0,16
     .name 'a.b'
     .asname 'y'
'''),

(193, 'parse_Import_name', 0, 0, 'SyntaxError', {}, ('Import_name',
r''''''),
r'''**SyntaxError("Expected one or more names after 'import'")**'''),

(194, 'parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r'''a'''), r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

(195, 'parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r'''a.b'''), r'''
alias - ROOT 0,0..0,3
  .name 'a.b'
'''),

(196, 'parse_Import_name', 0, 0, 'SyntaxError', {}, ('Import_name',
r'''*'''),
r'''**SyntaxError('invalid syntax')**'''),

(197, 'parse_Import_name', 0, 0, 'ParseError', {}, ('Import_name',
r'''a, b'''),
r'''**ParseError('expecting single name')**'''),

(198, 'parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r'''a as c'''), r'''
alias - ROOT 0,0..0,6
  .name 'a'
  .asname 'c'
'''),

(199, 'parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r'''a.b as c'''), r'''
alias - ROOT 0,0..0,8
  .name 'a.b'
  .asname 'c'
'''),

(200, 'parse_Import_name', 0, 0, 'SyntaxError', {}, ('Import_name',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(201, 'parse_Import_name', 0, 0, 'ParseError', {}, ('Import_name',
r'''a as x, b as y'''),
r'''**ParseError('expecting single name')**'''),

(202, 'parse_Import_name', 0, 0, 'ParseError', {}, ('Import_name',
r'''a as x, a.b as y'''),
r'''**ParseError('expecting single name')**'''),

(203, 'parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r''''''),
r'''_aliases - ROOT 0,0..0,0'''),

(204, 'parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

(205, 'parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a.b'''), r'''
_aliases - ROOT 0,0..0,3
  .names[1]
   0] alias - 0,0..0,3
     .name 'a.b'
'''),

(206, 'parse__Import_names', 0, 0, 'SyntaxError', {}, ('_Import_names',
r'''*'''),
r'''**SyntaxError('invalid syntax')**'''),

(207, 'parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a, b'''), r'''
_aliases - ROOT 0,0..0,4
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
'''),

(208, 'parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a as c'''), r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'c'
'''),

(209, 'parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a.b as c'''), r'''
_aliases - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,0..0,8
     .name 'a.b'
     .asname 'c'
'''),

(210, 'parse__Import_names', 0, 0, 'SyntaxError', {}, ('_Import_names',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(211, 'parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a as x, b as y'''), r'''
_aliases - ROOT 0,0..0,14
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'x'
   1] alias - 0,8..0,14
     .name 'b'
     .asname 'y'
'''),

(212, 'parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a as x, a.b as y'''), r'''
_aliases - ROOT 0,0..0,16
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'x'
   1] alias - 0,8..0,16
     .name 'a.b'
     .asname 'y'
'''),

(213, 'parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r''''''),
r'''**SyntaxError("Expected one or more names after 'import'")**'''),

(214, 'parse_ImportFrom_name', 0, 0, 'alias', {}, ('ImportFrom_name',
r'''a'''), r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

(215, 'parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''a.b'''),
r'''**SyntaxError('invalid syntax')**'''),

(216, 'parse_ImportFrom_name', 0, 0, 'alias', {}, ('ImportFrom_name',
r'''*'''), r'''
alias - ROOT 0,0..0,1
  .name '*'
'''),

(217, 'parse_ImportFrom_name', 0, 0, 'ParseError', {}, ('ImportFrom_name',
r'''a, b'''),
r'''**ParseError('expecting single name')**'''),

(218, 'parse_ImportFrom_name', 0, 0, 'alias', {}, ('ImportFrom_name',
r'''a as c'''), r'''
alias - ROOT 0,0..0,6
  .name 'a'
  .asname 'c'
'''),

(219, 'parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''a.b as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(220, 'parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(221, 'parse_ImportFrom_name', 0, 0, 'ParseError', {}, ('ImportFrom_name',
r'''a as x, b as y'''),
r'''**ParseError('expecting single name')**'''),

(222, 'parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''a as x, a.b as y'''),
r'''**SyntaxError('invalid syntax')**'''),

(223, 'parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r''''''),
r'''_aliases - ROOT 0,0..0,0'''),

(224, 'parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''a'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

(225, 'parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''a.b'''),
r'''**SyntaxError('invalid syntax')**'''),

(226, 'parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''*'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name '*'
'''),

(227, 'parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''a, b'''), r'''
_aliases - ROOT 0,0..0,4
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
'''),

(228, 'parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''a as c'''), r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'c'
'''),

(229, 'parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''a.b as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(230, 'parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(231, 'parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''a as x, b as y'''), r'''
_aliases - ROOT 0,0..0,14
  .names[2]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'x'
   1] alias - 0,8..0,14
     .name 'b'
     .asname 'y'
'''),

(232, 'parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''a as x, a.b as y'''),
r'''**SyntaxError('invalid syntax')**'''),

(233, 'parse_withitem', 0, 0, 'SyntaxError', {}, ('withitem',
r''''''),
r'''**SyntaxError('expecting withitem')**'''),

(234, 'parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''a'''), r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

(235, 'parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''a, b'''), r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[2]
     0] Name 'a' Load - 0,0..0,1
     1] Name 'b' Load - 0,3..0,4
    .ctx Load
'''),

(236, 'parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''(a, b)'''), r'''
withitem - ROOT 0,0..0,6
  .context_expr Tuple - 0,0..0,6
    .elts[2]
     0] Name 'a' Load - 0,1..0,2
     1] Name 'b' Load - 0,4..0,5
    .ctx Load
'''),

(237, 'parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''()'''), r'''
withitem - ROOT 0,0..0,2
  .context_expr Tuple - 0,0..0,2
    .ctx Load
'''),

(238, 'parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''a as b'''), r'''
withitem - ROOT 0,0..0,6
  .context_expr Name 'a' Load - 0,0..0,1
  .optional_vars Name 'b' Store - 0,5..0,6
'''),

(239, 'parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''(a) as (b)'''), r'''
withitem - ROOT 0,0..0,10
  .context_expr Name 'a' Load - 0,1..0,2
  .optional_vars Name 'b' Store - 0,8..0,9
'''),

(240, 'parse_withitem', 0, 0, 'ParseError', {}, ('withitem',
r'''a, b as c'''),
r'''**ParseError('expecting single withitem')**'''),

(241, 'parse_withitem', 0, 0, 'ParseError', {}, ('withitem',
r'''a as b, x as y'''),
r'''**ParseError('expecting single withitem')**'''),

(242, 'parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''(a)'''), r'''
withitem - ROOT 0,0..0,3
  .context_expr Name 'a' Load - 0,1..0,2
'''),

(243, 'parse_withitem', 0, 0, 'SyntaxError', {}, ('withitem',
r'''(a as b)'''),
r'''**SyntaxError('invalid syntax')**'''),

(244, 'parse_withitem', 0, 0, 'SyntaxError', {}, ('withitem',
r'''(a as b, x as y)'''),
r'''**SyntaxError('invalid syntax')**'''),

(245, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r''''''),
r'''_withitems - ROOT 0,0..0,0'''),

(246, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a'''), r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

(247, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a, b'''), r'''
_withitems - ROOT 0,0..0,4
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,4
     .context_expr Name 'b' Load - 0,3..0,4
'''),

(248, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''(a, b)'''), r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Tuple - 0,0..0,6
       .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
       .ctx Load
'''),

(249, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''()'''), r'''
_withitems - ROOT 0,0..0,2
  .items[1]
   0] withitem - 0,0..0,2
     .context_expr Tuple - 0,0..0,2
       .ctx Load
'''),

(250, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a as b'''), r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'b' Store - 0,5..0,6
'''),

(251, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''(a) as (b)'''), r'''
_withitems - ROOT 0,0..0,10
  .items[1]
   0] withitem - 0,0..0,10
     .context_expr Name 'a' Load - 0,1..0,2
     .optional_vars Name 'b' Store - 0,8..0,9
'''),

(252, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a, b as c'''), r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,9
     .context_expr Name 'b' Load - 0,3..0,4
     .optional_vars Name 'c' Store - 0,8..0,9
'''),

(253, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a as b, x as y'''), r'''
_withitems - ROOT 0,0..0,14
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'b' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'x' Load - 0,8..0,9
     .optional_vars Name 'y' Store - 0,13..0,14
'''),

(254, 'parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''(a)'''), r'''
_withitems - ROOT 0,0..0,3
  .items[1]
   0] withitem - 0,0..0,3
     .context_expr Name 'a' Load - 0,1..0,2
'''),

(255, 'parse__withitems', 0, 0, 'SyntaxError', {}, ('_withitems',
r'''(a as b)'''),
r'''**SyntaxError('invalid syntax')**'''),

(256, 'parse__withitems', 0, 0, 'SyntaxError', {}, ('_withitems',
r'''(a as b, x as y)'''),
r'''**SyntaxError('invalid syntax')**'''),

(257, 'parse_pattern', 0, 0, 'MatchValue', {}, ('pattern',
r'''42'''), r'''
MatchValue - ROOT 0,0..0,2
  .value Constant 42 - 0,0..0,2
'''),

(258, 'parse_pattern', 0, 0, 'MatchSingleton', {}, ('pattern',
r'''None'''),
r'''MatchSingleton None - ROOT 0,0..0,4'''),

(259, 'parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
r'''[a, *_]'''), r'''
MatchSequence - ROOT 0,0..0,7
  .patterns[2]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchStar - 0,4..0,6
'''),

(260, 'parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
r'''[]'''),
r'''MatchSequence - ROOT 0,0..0,2'''),

(261, 'parse_pattern', 0, 0, 'MatchMapping', {}, ('pattern',
r'''{"key": _}'''), r'''
MatchMapping - ROOT 0,0..0,10
  .keys[1]
   0] Constant 'key' - 0,1..0,6
  .patterns[1]
   0] MatchAs - 0,8..0,9
'''),

(262, 'parse_pattern', 0, 0, 'MatchMapping', {}, ('pattern',
r'''{}'''),
r'''MatchMapping - ROOT 0,0..0,2'''),

(263, 'parse_pattern', 0, 0, 'MatchClass', {}, ('pattern',
r'''SomeClass()'''), r'''
MatchClass - ROOT 0,0..0,11
  .cls Name 'SomeClass' Load - 0,0..0,9
'''),

(264, 'parse_pattern', 0, 0, 'MatchClass', {}, ('pattern',
r'''SomeClass(attr=val)'''), r'''
MatchClass - ROOT 0,0..0,19
  .cls Name 'SomeClass' Load - 0,0..0,9
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 0,15..0,18
     .name 'val'
'''),

(265, 'parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
r'''as_var'''), r'''
MatchAs - ROOT 0,0..0,6
  .name 'as_var'
'''),

(266, 'parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
r'''1 as as_var'''), r'''
MatchAs - ROOT 0,0..0,11
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'as_var'
'''),

(267, 'parse_pattern', 0, 0, 'MatchOr', {}, ('pattern',
r'''1 | 2 | 3'''), r'''
MatchOr - ROOT 0,0..0,9
  .patterns[3]
   0] MatchValue - 0,0..0,1
     .value Constant 1 - 0,0..0,1
   1] MatchValue - 0,4..0,5
     .value Constant 2 - 0,4..0,5
   2] MatchValue - 0,8..0,9
     .value Constant 3 - 0,8..0,9
'''),

(268, 'parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
r'''_'''),
r'''MatchAs - ROOT 0,0..0,1'''),

(269, 'parse_pattern', 0, 0, 'MatchStar', {}, ('pattern',
r'''*a'''), r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

(270, 'parse_pattern', 0, 0, 'SyntaxError', {}, ('pattern',
r''''''),
r'''**SyntaxError('empty pattern')**'''),

(271, 'parse_expr', 0, 0, 'BoolOp', {}, ('expr', r'''
a
or
b
'''), r'''
BoolOp - ROOT 0,0..2,1
  .op Or
  .values[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 2,0..2,1
'''),

(272, 'parse_expr', 0, 0, 'NamedExpr', {}, ('expr', r'''
a
:=
b
'''), r'''
NamedExpr - ROOT 0,0..2,1
  .target Name 'a' Store - 0,0..0,1
  .value Name 'b' Load - 2,0..2,1
'''),

(273, 'parse_expr', 0, 0, 'BinOp', {}, ('expr', r'''
a
|
b
'''), r'''
BinOp - ROOT 0,0..2,1
  .left Name 'a' Load - 0,0..0,1
  .op BitOr - 1,0..1,1
  .right Name 'b' Load - 2,0..2,1
'''),

(274, 'parse_expr', 0, 0, 'BinOp', {}, ('expr', r'''
a
**
b
'''), r'''
BinOp - ROOT 0,0..2,1
  .left Name 'a' Load - 0,0..0,1
  .op Pow - 1,0..1,2
  .right Name 'b' Load - 2,0..2,1
'''),

(275, 'parse_expr', 0, 0, 'UnaryOp', {}, ('expr', r'''
not
a
'''), r'''
UnaryOp - ROOT 0,0..1,1
  .op Not - 0,0..0,3
  .operand Name 'a' Load - 1,0..1,1
'''),

(276, 'parse_expr', 0, 0, 'UnaryOp', {}, ('expr', r'''
~
a
'''), r'''
UnaryOp - ROOT 0,0..1,1
  .op Invert - 0,0..0,1
  .operand Name 'a' Load - 1,0..1,1
'''),

(277, 'parse_expr', 0, 0, 'Lambda', {}, ('expr', r'''
lambda
:
None
'''), r'''
Lambda - ROOT 0,0..2,4
  .body Constant None - 2,0..2,4
'''),

(278, 'parse_expr', 0, 0, 'IfExp', {}, ('expr', r'''
a
if
b
else
c
'''), r'''
IfExp - ROOT 0,0..4,1
  .test Name 'b' Load - 2,0..2,1
  .body Name 'a' Load - 0,0..0,1
  .orelse Name 'c' Load - 4,0..4,1
'''),

(279, 'parse_expr', 0, 0, 'Dict', {}, ('expr', r'''
{
a
:
b
}
'''), r'''
Dict - ROOT 0,0..4,1
  .keys[1]
   0] Name 'a' Load - 1,0..1,1
  .values[1]
   0] Name 'b' Load - 3,0..3,1
'''),

(280, 'parse_expr', 0, 0, 'Set', {}, ('expr', r'''
{
a
,
b
}
'''), r'''
Set - ROOT 0,0..4,1
  .elts[2]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'b' Load - 3,0..3,1
'''),

(281, 'parse_expr', 0, 0, 'ListComp', {}, ('expr', r'''
[
a
for
a
in
b
]
'''), r'''
ListComp - ROOT 0,0..6,1
  .elt Name 'a' Load - 1,0..1,1
  .generators[1]
   0] comprehension - 2,0..5,1
     .target Name 'a' Store - 3,0..3,1
     .iter Name 'b' Load - 5,0..5,1
     .is_async 0
'''),

(282, 'parse_expr', 0, 0, 'SetComp', {}, ('expr', r'''
{
a
for
a
in
b
}
'''), r'''
SetComp - ROOT 0,0..6,1
  .elt Name 'a' Load - 1,0..1,1
  .generators[1]
   0] comprehension - 2,0..5,1
     .target Name 'a' Store - 3,0..3,1
     .iter Name 'b' Load - 5,0..5,1
     .is_async 0
'''),

(283, 'parse_expr', 0, 0, 'DictComp', {}, ('expr', r'''
{
a
:
c
for
a
,
c
in
b
}
'''), r'''
DictComp - ROOT 0,0..10,1
  .key Name 'a' Load - 1,0..1,1
  .value Name 'c' Load - 3,0..3,1
  .generators[1]
   0] comprehension - 4,0..9,1
     .target Tuple - 5,0..7,1
       .elts[2]
        0] Name 'a' Store - 5,0..5,1
        1] Name 'c' Store - 7,0..7,1
       .ctx Store
     .iter Name 'b' Load - 9,0..9,1
     .is_async 0
'''),

(284, 'parse_expr', 0, 0, 'GeneratorExp', {}, ('expr', r'''
(
a
for
a
in
b
)
'''), r'''
GeneratorExp - ROOT 0,0..6,1
  .elt Name 'a' Load - 1,0..1,1
  .generators[1]
   0] comprehension - 2,0..5,1
     .target Name 'a' Store - 3,0..3,1
     .iter Name 'b' Load - 5,0..5,1
     .is_async 0
'''),

(285, 'parse_expr', 0, 0, 'Await', {}, ('expr', r'''
await
a
'''), r'''
Await - ROOT 0,0..1,1
  .value Name 'a' Load - 1,0..1,1
'''),

(286, 'parse_expr', 0, 0, 'Yield', {}, ('expr',
r'''yield'''),
r'''Yield - ROOT 0,0..0,5'''),

(287, 'parse_expr', 0, 0, 'Yield', {}, ('expr', r'''
yield
a
'''), r'''
Yield - ROOT 0,0..1,1
  .value Name 'a' Load - 1,0..1,1
'''),

(288, 'parse_expr', 0, 0, 'YieldFrom', {}, ('expr', r'''
yield
from
a
'''), r'''
YieldFrom - ROOT 0,0..2,1
  .value Name 'a' Load - 2,0..2,1
'''),

(289, 'parse_expr', 0, 0, 'Compare', {}, ('expr', r'''
a
<
b
'''), r'''
Compare - ROOT 0,0..2,1
  .left Name 'a' Load - 0,0..0,1
  .ops[1]
   0] Lt - 1,0..1,1
  .comparators[1]
   0] Name 'b' Load - 2,0..2,1
'''),

(290, 'parse_expr', 0, 0, 'Call', {}, ('expr', r'''
f
(
a
)
'''), r'''
Call - ROOT 0,0..3,1
  .func Name 'f' Load - 0,0..0,1
  .args[1]
   0] Name 'a' Load - 2,0..2,1
'''),

(291, 'parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
"\nf'{a}'\n"), r'''
JoinedStr - ROOT
  .values[1]
   0] FormattedValue
     .value Name 'a' Load
     .conversion -1
'''),

(292, 'parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
r'''f"{a}"'''), r'''
JoinedStr - ROOT
  .values[1]
   0] FormattedValue
     .value Name 'a' Load
     .conversion -1
'''),

(293, 'parse_expr', 0, 0, 'JoinedStr', {}, ('expr', r"""
f'''
{
a
}
'''
"""), r'''
JoinedStr - ROOT
  .values[3]
   0] Constant '\n'
   1] FormattedValue
     .value Name 'a' Load
     .conversion -1
   2] Constant '\n'
'''),

(294, 'parse_expr', 0, 0, 'JoinedStr', {}, ('expr', r'''
f"""
{
a
}
"""
'''), r'''
JoinedStr - ROOT
  .values[3]
   0] Constant '\n'
   1] FormattedValue
     .value Name 'a' Load
     .conversion -1
   2] Constant '\n'
'''),

(295, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''...'''),
r'''Constant Ellipsis - ROOT 0,0..0,3'''),

(296, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''None'''),
r'''Constant None - ROOT 0,0..0,4'''),

(297, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''True'''),
r'''Constant True - ROOT 0,0..0,4'''),

(298, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''False'''),
r'''Constant False - ROOT 0,0..0,5'''),

(299, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''1'''),
r'''Constant 1 - ROOT 0,0..0,1'''),

(300, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''1.0'''),
r'''Constant 1.0 - ROOT 0,0..0,3'''),

(301, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''1j'''),
r'''Constant 1j - ROOT 0,0..0,2'''),

(302, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n'a'\n"),
r'''Constant 'a' - ROOT 0,0..0,3'''),

(303, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''"a"'''),
r'''Constant 'a' - ROOT 0,0..0,3'''),

(304, 'parse_expr', 0, 0, 'Constant', {}, ('expr', r"""
'''
a
'''
"""),
r'''Constant '\na\n' - ROOT 0,0..2,3'''),

(305, 'parse_expr', 0, 0, 'Constant', {}, ('expr', r'''
"""
a
"""
'''),
r'''Constant '\na\n' - ROOT 0,0..2,3'''),

(306, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
"\nb'a'\n"),
r'''Constant b'a' - ROOT 0,0..0,4'''),

(307, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''b"a"'''),
r'''Constant b'a' - ROOT 0,0..0,4'''),

(308, 'parse_expr', 0, 0, 'Constant', {}, ('expr', r"""
b'''
a
'''
"""),
r'''Constant b'\na\n' - ROOT 0,0..2,3'''),

(309, 'parse_expr', 0, 0, 'Constant', {}, ('expr', r'''
b"""
a
"""
'''),
r'''Constant b'\na\n' - ROOT 0,0..2,3'''),

(310, 'parse_expr', 0, 0, 'Attribute', {}, ('expr', r'''
a
.
b
'''), r'''
Attribute - ROOT 0,0..2,1
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),

(311, 'parse_expr', 0, 0, 'Subscript', {}, ('expr', r'''
a
[
b
]
'''), r'''
Subscript - ROOT 0,0..3,1
  .value Name 'a' Load - 0,0..0,1
  .slice Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(312, 'parse_expr', 0, 0, 'Starred', {}, ('expr', r'''
*
a
'''), r'''
Starred - ROOT 0,0..1,1
  .value Name 'a' Load - 1,0..1,1
  .ctx Load
'''),

(313, 'parse_expr', 0, 0, 'List', {}, ('expr', r'''
[
a
,
b
]
'''), r'''
List - ROOT 0,0..4,1
  .elts[2]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'b' Load - 3,0..3,1
  .ctx Load
'''),

(314, 'parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
(
a
,
b
)
'''), r'''
Tuple - ROOT 0,0..4,1
  .elts[2]
   0] Name 'a' Load - 1,0..1,1
   1] Name 'b' Load - 3,0..3,1
  .ctx Load
'''),

(315, 'parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
a
,
'''), r'''
Tuple - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

(316, 'parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
a
,
b
'''), r'''
Tuple - ROOT 0,0..2,1
  .elts[2]
   0] Name 'a' Load - 0,0..0,1
   1] Name 'b' Load - 2,0..2,1
  .ctx Load
'''),

(317, 'parse_pattern', 0, 0, 'MatchValue', {}, ('pattern',
r'''42'''), r'''
MatchValue - ROOT 0,0..0,2
  .value Constant 42 - 0,0..0,2
'''),

(318, 'parse_pattern', 0, 0, 'MatchSingleton', {}, ('pattern',
r'''None'''),
r'''MatchSingleton None - ROOT 0,0..0,4'''),

(319, 'parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern', r'''
[
a
,
*
b
]
'''), r'''
MatchSequence - ROOT 0,0..5,1
  .patterns[2]
   0] MatchAs - 1,0..1,1
     .name 'a'
   1] MatchStar - 3,0..4,1
     .name 'b'
'''),

(320, 'parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern', r'''

a
,
*
b

'''), r'''
MatchSequence - ROOT 0,0..4,1
  .patterns[2]
   0] MatchAs - 1,0..1,1
     .name 'a'
   1] MatchStar - 3,0..4,1
     .name 'b'
'''),

(321, 'parse_pattern', 0, 0, 'MatchMapping', {}, ('pattern', r'''
{
"key"
:
_
}
'''), r'''
MatchMapping - ROOT 0,0..4,1
  .keys[1]
   0] Constant 'key' - 1,0..1,5
  .patterns[1]
   0] MatchAs - 3,0..3,1
'''),

(322, 'parse_pattern', 0, 0, 'MatchClass', {}, ('pattern', r'''
SomeClass
(
attr
=
val
)
'''), r'''
MatchClass - ROOT 0,0..5,1
  .cls Name 'SomeClass' Load - 0,0..0,9
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 4,0..4,3
     .name 'val'
'''),

(323, 'parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
r'''as_var'''), r'''
MatchAs - ROOT 0,0..0,6
  .name 'as_var'
'''),

(324, 'parse_pattern', 0, 0, 'MatchAs', {}, ('pattern', r'''
1
as
as_var
'''), r'''
MatchAs - ROOT 0,0..2,6
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'as_var'
'''),

(325, 'parse_pattern', 0, 0, 'MatchOr', {}, ('pattern', r'''
1
|
2
'''), r'''
MatchOr - ROOT 0,0..2,1
  .patterns[2]
   0] MatchValue - 0,0..0,1
     .value Constant 1 - 0,0..0,1
   1] MatchValue - 2,0..2,1
     .value Constant 2 - 2,0..2,1
'''),

(326, 'parse_expr', 0, 0, 'BoolOp', {}, ('expr',
'\n a\n or\n b\n         '), r'''
BoolOp - ROOT 1,1..3,2
  .op Or
  .values[2]
   0] Name 'a' Load - 1,1..1,2
   1] Name 'b' Load - 3,1..3,2
'''),

(327, 'parse_expr', 0, 0, 'NamedExpr', {}, ('expr',
'\n a\n :=\n b\n         '), r'''
NamedExpr - ROOT 1,1..3,2
  .target Name 'a' Store - 1,1..1,2
  .value Name 'b' Load - 3,1..3,2
'''),

(328, 'parse_expr', 0, 0, 'BinOp', {}, ('expr',
'\n a\n |\n b\n         '), r'''
BinOp - ROOT 1,1..3,2
  .left Name 'a' Load - 1,1..1,2
  .op BitOr - 2,1..2,2
  .right Name 'b' Load - 3,1..3,2
'''),

(329, 'parse_expr', 0, 0, 'BinOp', {}, ('expr',
'\n a\n **\n b\n         '), r'''
BinOp - ROOT 1,1..3,2
  .left Name 'a' Load - 1,1..1,2
  .op Pow - 2,1..2,3
  .right Name 'b' Load - 3,1..3,2
'''),

(330, 'parse_expr', 0, 0, 'UnaryOp', {}, ('expr',
'\n not\n a\n         '), r'''
UnaryOp - ROOT 1,1..2,2
  .op Not - 1,1..1,4
  .operand Name 'a' Load - 2,1..2,2
'''),

(331, 'parse_expr', 0, 0, 'UnaryOp', {}, ('expr',
'\n ~\n a\n         '), r'''
UnaryOp - ROOT 1,1..2,2
  .op Invert - 1,1..1,2
  .operand Name 'a' Load - 2,1..2,2
'''),

(332, 'parse_expr', 0, 0, 'Lambda', {}, ('expr',
'\n lambda\n :\n None\n         '), r'''
Lambda - ROOT 1,1..3,5
  .body Constant None - 3,1..3,5
'''),

(333, 'parse_expr', 0, 0, 'IfExp', {}, ('expr',
'\n a\n if\n b\n else\n c\n         '), r'''
IfExp - ROOT 1,1..5,2
  .test Name 'b' Load - 3,1..3,2
  .body Name 'a' Load - 1,1..1,2
  .orelse Name 'c' Load - 5,1..5,2
'''),

(334, 'parse_expr', 0, 0, 'Dict', {}, ('expr',
'\n {\n a\n :\n b\n }\n         '), r'''
Dict - ROOT 1,1..5,2
  .keys[1]
   0] Name 'a' Load - 2,1..2,2
  .values[1]
   0] Name 'b' Load - 4,1..4,2
'''),

(335, 'parse_expr', 0, 0, 'Set', {}, ('expr',
'\n {\n a\n ,\n b\n }\n         '), r'''
Set - ROOT 1,1..5,2
  .elts[2]
   0] Name 'a' Load - 2,1..2,2
   1] Name 'b' Load - 4,1..4,2
'''),

(336, 'parse_expr', 0, 0, 'ListComp', {}, ('expr',
'\n [\n a\n for\n a\n in\n b\n ]\n         '), r'''
ListComp - ROOT 1,1..7,2
  .elt Name 'a' Load - 2,1..2,2
  .generators[1]
   0] comprehension - 3,1..6,2
     .target Name 'a' Store - 4,1..4,2
     .iter Name 'b' Load - 6,1..6,2
     .is_async 0
'''),

(337, 'parse_expr', 0, 0, 'SetComp', {}, ('expr',
'\n {\n a\n for\n a\n in\n b\n }\n         '), r'''
SetComp - ROOT 1,1..7,2
  .elt Name 'a' Load - 2,1..2,2
  .generators[1]
   0] comprehension - 3,1..6,2
     .target Name 'a' Store - 4,1..4,2
     .iter Name 'b' Load - 6,1..6,2
     .is_async 0
'''),

(338, 'parse_expr', 0, 0, 'DictComp', {}, ('expr',
'\n {\n a\n :\n c\n for\n a\n ,\n c\n in\n b\n }\n         '), r'''
DictComp - ROOT 1,1..11,2
  .key Name 'a' Load - 2,1..2,2
  .value Name 'c' Load - 4,1..4,2
  .generators[1]
   0] comprehension - 5,1..10,2
     .target Tuple - 6,1..8,2
       .elts[2]
        0] Name 'a' Store - 6,1..6,2
        1] Name 'c' Store - 8,1..8,2
       .ctx Store
     .iter Name 'b' Load - 10,1..10,2
     .is_async 0
'''),

(339, 'parse_expr', 0, 0, 'GeneratorExp', {}, ('expr',
'\n (\n a\n for\n a\n in\n b\n )\n         '), r'''
GeneratorExp - ROOT 1,1..7,2
  .elt Name 'a' Load - 2,1..2,2
  .generators[1]
   0] comprehension - 3,1..6,2
     .target Name 'a' Store - 4,1..4,2
     .iter Name 'b' Load - 6,1..6,2
     .is_async 0
'''),

(340, 'parse_expr', 0, 0, 'Await', {}, ('expr',
'\n await\n a\n         '), r'''
Await - ROOT 1,1..2,2
  .value Name 'a' Load - 2,1..2,2
'''),

(341, 'parse_expr', 0, 0, 'Yield', {}, ('expr',
'\n yield\n         '),
r'''Yield - ROOT 1,1..1,6'''),

(342, 'parse_expr', 0, 0, 'Yield', {}, ('expr',
'\n yield\n a\n         '), r'''
Yield - ROOT 1,1..2,2
  .value Name 'a' Load - 2,1..2,2
'''),

(343, 'parse_expr', 0, 0, 'YieldFrom', {}, ('expr',
'\n yield\n from\n a\n         '), r'''
YieldFrom - ROOT 1,1..3,2
  .value Name 'a' Load - 3,1..3,2
'''),

(344, 'parse_expr', 0, 0, 'Compare', {}, ('expr',
'\n a\n <\n b\n         '), r'''
Compare - ROOT 1,1..3,2
  .left Name 'a' Load - 1,1..1,2
  .ops[1]
   0] Lt - 2,1..2,2
  .comparators[1]
   0] Name 'b' Load - 3,1..3,2
'''),

(345, 'parse_expr', 0, 0, 'Call', {}, ('expr',
'\n f\n (\n a\n )\n         '), r'''
Call - ROOT 1,1..4,2
  .func Name 'f' Load - 1,1..1,2
  .args[1]
   0] Name 'a' Load - 3,1..3,2
'''),

(346, 'parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
"\n f'{a}'\n "), r'''
JoinedStr - ROOT
  .values[1]
   0] FormattedValue
     .value Name 'a' Load
     .conversion -1
'''),

(347, 'parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
'\n f"{a}"\n         '), r'''
JoinedStr - ROOT
  .values[1]
   0] FormattedValue
     .value Name 'a' Load
     .conversion -1
'''),

(348, 'parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
"\n f'''\n {\n a\n }\n         '''\n "), r'''
JoinedStr - ROOT
  .values[3]
   0] Constant '\n '
   1] FormattedValue
     .value Name 'a' Load
     .conversion -1
   2] Constant '\n         '
'''),

(349, 'parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
'\n f"""\n {\n a\n }\n """\n         '), r'''
JoinedStr - ROOT
  .values[3]
   0] Constant '\n '
   1] FormattedValue
     .value Name 'a' Load
     .conversion -1
   2] Constant '\n '
'''),

(350, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n ...\n         '),
r'''Constant Ellipsis - ROOT 1,1..1,4'''),

(351, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n None\n         '),
r'''Constant None - ROOT 1,1..1,5'''),

(352, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n True\n         '),
r'''Constant True - ROOT 1,1..1,5'''),

(353, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n False\n         '),
r'''Constant False - ROOT 1,1..1,6'''),

(354, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n 1\n         '),
r'''Constant 1 - ROOT 1,1..1,2'''),

(355, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n 1.0\n         '),
r'''Constant 1.0 - ROOT 1,1..1,4'''),

(356, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n 1j\n         '),
r'''Constant 1j - ROOT 1,1..1,3'''),

(357, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n         'a'\n "),
r'''Constant 'a' - ROOT 1,9..1,12'''),

(358, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n "a"\n         '),
r'''Constant 'a' - ROOT 1,1..1,4'''),

(359, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n         '''\n a\n         '''\n "),
r'''Constant '\n a\n         ' - ROOT 1,9..3,12'''),

(360, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n """\n a\n """\n         '),
r'''Constant '\n a\n ' - ROOT 1,1..3,4'''),

(361, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n b'a'\n "),
r'''Constant b'a' - ROOT 1,1..1,5'''),

(362, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n b"a"\n         '),
r'''Constant b'a' - ROOT 1,1..1,5'''),

(363, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n b'''\n a\n         '''\n "),
r'''Constant b'\n a\n         ' - ROOT 1,1..3,12'''),

(364, 'parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n b"""\n a\n """\n         '),
r'''Constant b'\n a\n ' - ROOT 1,1..3,4'''),

(365, 'parse_expr', 0, 0, 'Attribute', {}, ('expr',
'\n a\n .\n b\n         '), r'''
Attribute - ROOT 1,1..3,2
  .value Name 'a' Load - 1,1..1,2
  .attr 'b'
  .ctx Load
'''),

(366, 'parse_expr', 0, 0, 'Subscript', {}, ('expr',
'\n a\n [\n b\n ]\n         '), r'''
Subscript - ROOT 1,1..4,2
  .value Name 'a' Load - 1,1..1,2
  .slice Name 'b' Load - 3,1..3,2
  .ctx Load
'''),

(367, 'parse_expr', 0, 0, 'Starred', {}, ('expr',
'\n *\n a\n         '), r'''
Starred - ROOT 1,1..2,2
  .value Name 'a' Load - 2,1..2,2
  .ctx Load
'''),

(368, 'parse_expr', 0, 0, 'List', {}, ('expr',
'\n [\n a\n ,\n b\n ]\n         '), r'''
List - ROOT 1,1..5,2
  .elts[2]
   0] Name 'a' Load - 2,1..2,2
   1] Name 'b' Load - 4,1..4,2
  .ctx Load
'''),

(369, 'parse_expr', 0, 0, 'Tuple', {}, ('expr',
'\n (\n a\n ,\n b\n )\n         '), r'''
Tuple - ROOT 1,1..5,2
  .elts[2]
   0] Name 'a' Load - 2,1..2,2
   1] Name 'b' Load - 4,1..4,2
  .ctx Load
'''),

(370, 'parse_expr', 0, 0, 'Tuple', {}, ('expr',
'\n a\n ,\n         '), r'''
Tuple - ROOT 1,1..2,2
  .elts[1]
   0] Name 'a' Load - 1,1..1,2
  .ctx Load
'''),

(371, 'parse_expr', 0, 0, 'Tuple', {}, ('expr',
'\n a\n ,\n b\n         '), r'''
Tuple - ROOT 1,1..3,2
  .elts[2]
   0] Name 'a' Load - 1,1..1,2
   1] Name 'b' Load - 3,1..3,2
  .ctx Load
'''),

(372, 'parse_pattern', 0, 0, 'MatchValue', {}, ('pattern',
'\n 42\n         '), r'''
MatchValue - ROOT 1,1..1,3
  .value Constant 42 - 1,1..1,3
'''),

(373, 'parse_pattern', 0, 0, 'MatchSingleton', {}, ('pattern',
'\n None\n         '),
r'''MatchSingleton None - ROOT 1,1..1,5'''),

(374, 'parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
'\n [\n a\n ,\n *\n b\n ]\n         '), r'''
MatchSequence - ROOT 1,1..6,2
  .patterns[2]
   0] MatchAs - 2,1..2,2
     .name 'a'
   1] MatchStar - 4,1..5,2
     .name 'b'
'''),

(375, 'parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
'\n \n a\n ,\n *\n b\n \n         '), r'''
MatchSequence - ROOT 0,0..5,2
  .patterns[2]
   0] MatchAs - 2,1..2,2
     .name 'a'
   1] MatchStar - 4,1..5,2
     .name 'b'
'''),

(376, 'parse_pattern', 0, 0, 'MatchMapping', {}, ('pattern',
'\n {\n "key"\n :\n _\n }\n         '), r'''
MatchMapping - ROOT 1,1..5,2
  .keys[1]
   0] Constant 'key' - 2,1..2,6
  .patterns[1]
   0] MatchAs - 4,1..4,2
'''),

(377, 'parse_pattern', 0, 0, 'MatchClass', {}, ('pattern',
'\n SomeClass\n (\n attr\n =\n val\n )\n         '), r'''
MatchClass - ROOT 1,1..6,2
  .cls Name 'SomeClass' Load - 1,1..1,10
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 5,1..5,4
     .name 'val'
'''),

(378, 'parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
'\n as_var\n         '), r'''
MatchAs - ROOT 1,1..1,7
  .name 'as_var'
'''),

(379, 'parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
'\n 1\n as\n as_var\n         '), r'''
MatchAs - ROOT 1,1..3,7
  .pattern MatchValue - 1,1..1,2
    .value Constant 1 - 1,1..1,2
  .name 'as_var'
'''),

(380, 'parse_pattern', 0, 0, 'MatchOr', {}, ('pattern',
'\n 1\n |\n 2\n         '), r'''
MatchOr - ROOT 1,1..3,2
  .patterns[2]
   0] MatchValue - 1,1..1,2
     .value Constant 1 - 1,1..1,2
   1] MatchValue - 3,1..3,2
     .value Constant 2 - 3,1..3,2
'''),

(381, 'parse_Module', 0, 0, 'Module', {}, (mod,
r'''j'''), r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(382, 'parse_Module', 0, 0, 'Module', {}, (Module,
r'''j'''), r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(383, 'parse_Expression', 0, 0, 'Expression', {}, (Expression,
r'''None'''), r'''
Expression - ROOT 0,0..0,4
  .body Constant None - 0,0..0,4
'''),

(384, 'parse_Interactive', 0, 0, 'Interactive', {}, (Interactive,
r'''j'''), r'''
Interactive - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

(385, 'parse_stmt', 0, 0, 'AnnAssign', {}, (stmt,
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

(386, 'parse_stmt', 0, 0, 'Expr', {}, (stmt,
r'''j'''), r'''
Expr - ROOT 0,0..0,1
  .value Name 'j' Load - 0,0..0,1
'''),

(387, 'parse_stmt', 0, 0, 'ParseError', {}, (stmt, r'''
i: int = 1
j
'''),
r'''**ParseError('expecting single stmt')**'''),

(388, 'parse_stmt', 0, 0, 'SyntaxError', {}, (stmt,
r'''except: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

(389, 'parse_stmt', 0, 0, 'AnnAssign', {}, (AnnAssign,
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

(390, 'parse_stmt', 0, 0, 'Expr', {}, (Expr,
r'''j'''), r'''
Expr - ROOT 0,0..0,1
  .value Name 'j' Load - 0,0..0,1
'''),

(391, 'parse_ExceptHandler', 0, 0, 'ExceptHandler', {}, (ExceptHandler,
r'''except: pass'''), r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
'''),

(392, 'parse_ExceptHandler', 0, 0, 'ParseError', {}, (ExceptHandler, r'''
except Exception: pass
except: pass
'''),
r'''**ParseError('expecting single ExceptHandler')**'''),

(393, 'parse_ExceptHandler', 0, 0, 'SyntaxError', {}, (ExceptHandler,
r'''i: int = 1'''),
r'''**SyntaxError("expected 'except' or 'finally' block")**'''),

(394, 'parse_match_case', 0, 0, 'match_case', {}, (match_case,
r'''case None: pass'''), r'''
match_case - ROOT 0,0..0,15
  .pattern MatchSingleton None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

(395, 'parse_match_case', 0, 0, 'ParseError', {}, (match_case, r'''
case None: pass
case 1: pass
'''),
r'''**ParseError('expecting single match_case')**'''),

(396, 'parse_match_case', 0, 0, 'SyntaxError', {}, (match_case,
r'''i: int = 1'''),
r'''**SyntaxError('invalid syntax')**'''),

(397, 'parse_expr', 0, 0, 'Name', {}, (expr,
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(398, 'parse_expr', 0, 0, 'Starred', {}, (expr,
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

(399, 'parse_expr', 0, 0, 'Starred', {}, (expr, r'''
*
s
'''), r'''
Starred - ROOT 0,0..1,1
  .value Name 's' Load - 1,0..1,1
  .ctx Load
'''),

(400, 'parse_expr', 0, 0, 'Tuple', {}, (expr, r'''
*
s,
'''), r'''
Tuple - ROOT 0,0..1,2
  .elts[1]
   0] Starred - 0,0..1,1
     .value Name 's' Load - 1,0..1,1
     .ctx Load
  .ctx Load
'''),

(401, 'parse_expr', 0, 0, 'Tuple', {}, (expr, r'''
1
,
2
,
'''), r'''
Tuple - ROOT 0,0..3,1
  .elts[2]
   0] Constant 1 - 0,0..0,1
   1] Constant 2 - 2,0..2,1
  .ctx Load
'''),

(402, 'parse_expr', 0, 0, 'SyntaxError', {}, (expr,
r'''*not a'''),
r'''**SyntaxError('invalid expression')**'''),

(403, 'parse_expr', 0, 0, 'SyntaxError', {}, (expr,
r'''a:b'''),
r'''**SyntaxError('invalid expression')**'''),

(404, 'parse_expr', 0, 0, 'SyntaxError', {}, (expr,
r'''a:b:c'''),
r'''**SyntaxError('invalid expression')**'''),

(405, 'parse_expr', 0, 0, 'Name', {}, (Name,
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

(406, 'parse_expr', 0, 0, 'Starred', {}, (Starred,
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

(407, 'parse_expr_arglike', 0, 0, 'Starred', {}, (Starred,
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(408, 'parse_expr_slice', 0, 0, 'Slice', {}, (Slice,
r'''a:b'''), r'''
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
'''),

(409, 'parse_boolop', 0, 0, 'And', {}, (boolop,
r'''and'''),
r'''And - ROOT 0,0..0,3'''),

(410, 'parse_boolop', 0, 0, 'ParseError', {}, (boolop,
r'''*'''),
r'''**ParseError("expecting boolop, got '*'")**'''),

(411, 'parse_operator', 0, 0, 'Mult', {}, (operator,
r'''*'''),
r'''Mult - ROOT 0,0..0,1'''),

(412, 'parse_operator', 0, 0, 'Mult', {}, (operator,
r'''*='''),
r'''Mult - ROOT 0,0..0,2'''),

(413, 'parse_operator', 0, 0, 'ParseError', {}, (operator,
r'''and'''),
r'''**ParseError("expecting operator, got 'and'")**'''),

(414, 'parse_unaryop', 0, 0, 'UAdd', {}, (unaryop,
r'''+'''),
r'''UAdd - ROOT 0,0..0,1'''),

(415, 'parse_unaryop', 0, 0, 'SyntaxError', {}, (unaryop,
r'''and'''),
r'''**SyntaxError('invalid syntax')**'''),

(416, 'parse_cmpop', 0, 0, 'GtE', {}, (cmpop,
r'''>='''),
r'''GtE - ROOT 0,0..0,2'''),

(417, 'parse_cmpop', 0, 0, 'IsNot', {}, (cmpop, r'''
is
not
'''),
r'''IsNot - ROOT 0,0..1,3'''),

(418, 'parse_cmpop', 0, 0, 'ParseError', {}, (cmpop,
r'''>= a >='''),
r'''**ParseError('expecting single cmpop')**'''),

(419, 'parse_cmpop', 0, 0, 'ParseError', {}, (cmpop,
r'''and'''),
r'''**ParseError("expecting cmpop, got 'and'")**'''),

(420, 'parse_comprehension', 0, 0, 'comprehension', {}, (comprehension,
r'''for u in v'''), r'''
comprehension - ROOT 0,0..0,10
  .target Name 'u' Store - 0,4..0,5
  .iter Name 'v' Load - 0,9..0,10
  .is_async 0
'''),

(421, 'parse_comprehension', 0, 0, 'comprehension', {}, (comprehension,
r'''for u in v if w'''), r'''
comprehension - ROOT 0,0..0,15
  .target Name 'u' Store - 0,4..0,5
  .iter Name 'v' Load - 0,9..0,10
  .ifs[1]
   0] Name 'w' Load - 0,14..0,15
  .is_async 0
'''),

(422, 'parse_comprehension', 0, 0, 'ParseError', {}, (comprehension,
r'''()'''),
r'''**ParseError('expecting comprehension')**'''),

(423, 'parse_arguments', 0, 0, 'arguments', {}, (arguments,
r''''''),
r'''arguments - ROOT'''),

(424, 'parse_arguments', 0, 0, 'arguments', {}, (arguments,
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''), r'''
arguments - ROOT 0,0..0,43
  .posonlyargs[1]
   0] arg - 0,0..0,12
     .arg 'a'
     .annotation Subscript - 0,3..0,12
       .value Name 'list' Load - 0,3..0,7
       .slice Name 'str' Load - 0,8..0,11
       .ctx Load
  .args[1]
   0] arg - 0,17..0,23
     .arg 'b'
     .annotation Name 'int' Load - 0,20..0,23
  .vararg arg - 0,30..0,31
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 0,33..0,34
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 0,35..0,38
  .kwarg arg - 0,42..0,43
    .arg 'e'
  .defaults[1]
   0] Constant 1 - 0,26..0,27
'''),

(425, 'parse_arguments_lambda', 0, 0, 'arguments', {}, (arguments,
r'''a, /, b, *c, d=100, **e'''), r'''
arguments - ROOT 0,0..0,23
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'a'
  .args[1]
   0] arg - 0,6..0,7
     .arg 'b'
  .vararg arg - 0,10..0,11
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 0,13..0,14
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 0,15..0,18
  .kwarg arg - 0,22..0,23
    .arg 'e'
'''),

(426, 'parse_arg', 0, 0, 'arg', {}, (arg,
r'''a: b'''), r'''
arg - ROOT 0,0..0,4
  .arg 'a'
  .annotation Name 'b' Load - 0,3..0,4
'''),

(427, 'parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''a: b = c'''),
r'''**ParseError('expecting single argument without default')**'''),

(428, 'parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''a, b'''),
r'''**ParseError('expecting single argument without default')**'''),

(429, 'parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''a, /'''),
r'''**ParseError('expecting single argument without default')**'''),

(430, 'parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''*, a'''),
r'''**ParseError('expecting single argument without default')**'''),

(431, 'parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''*a'''),
r'''**ParseError('expecting single argument without default')**'''),

(432, 'parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''**a'''),
r'''**ParseError('expecting single argument without default')**'''),

(433, 'parse_keyword', 0, 0, 'keyword', {}, (keyword,
r'''a=1'''), r'''
keyword - ROOT 0,0..0,3
  .arg 'a'
  .value Constant 1 - 0,2..0,3
'''),

(434, 'parse_keyword', 0, 0, 'keyword', {}, (keyword,
r'''**a'''), r'''
keyword - ROOT 0,0..0,3
  .value Name 'a' Load - 0,2..0,3
'''),

(435, 'parse_keyword', 0, 0, 'ParseError', {}, (keyword,
r'''1'''),
r'''**ParseError('expecting single keyword')**'''),

(436, 'parse_keyword', 0, 0, 'ParseError', {}, (keyword,
r'''a'''),
r'''**ParseError('expecting single keyword')**'''),

(437, 'parse_keyword', 0, 0, 'ParseError', {}, (keyword,
r'''a=1, b=2'''),
r'''**ParseError('expecting single keyword')**'''),

(438, 'parse_alias', 0, 0, 'alias', {}, (alias,
r'''a'''), r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

(439, 'parse_alias', 0, 0, 'alias', {}, (alias,
r'''a.b'''), r'''
alias - ROOT 0,0..0,3
  .name 'a.b'
'''),

(440, 'parse_alias', 0, 0, 'alias', {}, (alias,
r'''*'''), r'''
alias - ROOT 0,0..0,1
  .name '*'
'''),

(441, 'parse_alias', 0, 0, 'ParseError', {}, (alias,
r'''a, b'''),
r'''**ParseError('expecting single name')**'''),

(442, 'parse_alias', 0, 0, 'alias', {}, (alias,
r'''a as c'''), r'''
alias - ROOT 0,0..0,6
  .name 'a'
  .asname 'c'
'''),

(443, 'parse_alias', 0, 0, 'alias', {}, (alias,
r'''a.b as c'''), r'''
alias - ROOT 0,0..0,8
  .name 'a.b'
  .asname 'c'
'''),

(444, 'parse_alias', 0, 0, 'SyntaxError', {}, (alias,
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

(445, 'parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''a'''), r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

(446, 'parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''a, b'''), r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[2]
     0] Name 'a' Load - 0,0..0,1
     1] Name 'b' Load - 0,3..0,4
    .ctx Load
'''),

(447, 'parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''(a, b)'''), r'''
withitem - ROOT 0,0..0,6
  .context_expr Tuple - 0,0..0,6
    .elts[2]
     0] Name 'a' Load - 0,1..0,2
     1] Name 'b' Load - 0,4..0,5
    .ctx Load
'''),

(448, 'parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''a as b'''), r'''
withitem - ROOT 0,0..0,6
  .context_expr Name 'a' Load - 0,0..0,1
  .optional_vars Name 'b' Store - 0,5..0,6
'''),

(449, 'parse_withitem', 0, 0, 'ParseError', {}, (withitem,
r'''a as b, x as y'''),
r'''**ParseError('expecting single withitem')**'''),

(450, 'parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''(a)'''), r'''
withitem - ROOT 0,0..0,3
  .context_expr Name 'a' Load - 0,1..0,2
'''),

(451, 'parse_withitem', 0, 0, 'SyntaxError', {}, (withitem,
r'''(a as b)'''),
r'''**SyntaxError('invalid syntax')**'''),

(452, 'parse_withitem', 0, 0, 'SyntaxError', {}, (withitem,
r'''(a as b, x as y)'''),
r'''**SyntaxError('invalid syntax')**'''),

(453, 'parse_pattern', 0, 0, 'MatchValue', {}, (pattern,
r'''42'''), r'''
MatchValue - ROOT 0,0..0,2
  .value Constant 42 - 0,0..0,2
'''),

(454, 'parse_pattern', 0, 0, 'MatchSingleton', {}, (pattern,
r'''None'''),
r'''MatchSingleton None - ROOT 0,0..0,4'''),

(455, 'parse_pattern', 0, 0, 'MatchSequence', {}, (pattern,
r'''[a, *_]'''), r'''
MatchSequence - ROOT 0,0..0,7
  .patterns[2]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchStar - 0,4..0,6
'''),

(456, 'parse_pattern', 0, 0, 'MatchSequence', {}, (pattern,
r'''[]'''),
r'''MatchSequence - ROOT 0,0..0,2'''),

(457, 'parse_pattern', 0, 0, 'MatchMapping', {}, (pattern,
r'''{"key": _}'''), r'''
MatchMapping - ROOT 0,0..0,10
  .keys[1]
   0] Constant 'key' - 0,1..0,6
  .patterns[1]
   0] MatchAs - 0,8..0,9
'''),

(458, 'parse_pattern', 0, 0, 'MatchMapping', {}, (pattern,
r'''{}'''),
r'''MatchMapping - ROOT 0,0..0,2'''),

(459, 'parse_pattern', 0, 0, 'MatchClass', {}, (pattern,
r'''SomeClass()'''), r'''
MatchClass - ROOT 0,0..0,11
  .cls Name 'SomeClass' Load - 0,0..0,9
'''),

(460, 'parse_pattern', 0, 0, 'MatchClass', {}, (pattern,
r'''SomeClass(attr=val)'''), r'''
MatchClass - ROOT 0,0..0,19
  .cls Name 'SomeClass' Load - 0,0..0,9
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 0,15..0,18
     .name 'val'
'''),

(461, 'parse_pattern', 0, 0, 'MatchAs', {}, (pattern,
r'''as_var'''), r'''
MatchAs - ROOT 0,0..0,6
  .name 'as_var'
'''),

(462, 'parse_pattern', 0, 0, 'MatchAs', {}, (pattern,
r'''1 as as_var'''), r'''
MatchAs - ROOT 0,0..0,11
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'as_var'
'''),

(463, 'parse_pattern', 0, 0, 'MatchOr', {}, (pattern,
r'''1 | 2 | 3'''), r'''
MatchOr - ROOT 0,0..0,9
  .patterns[3]
   0] MatchValue - 0,0..0,1
     .value Constant 1 - 0,0..0,1
   1] MatchValue - 0,4..0,5
     .value Constant 2 - 0,4..0,5
   2] MatchValue - 0,8..0,9
     .value Constant 3 - 0,8..0,9
'''),

(464, 'parse_pattern', 0, 0, 'MatchAs', {}, (pattern,
r'''_'''),
r'''MatchAs - ROOT 0,0..0,1'''),

(465, 'parse_pattern', 0, 0, 'MatchStar', {}, (pattern,
r'''*a'''), r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

(466, 'parse_pattern', 0, 0, 'SyntaxError', {}, (pattern,
r''''''),
r'''**SyntaxError('empty pattern')**'''),

(467, 'parse_pattern', 0, 0, 'MatchValue', {}, (MatchValue,
r'''42'''), r'''
MatchValue - ROOT 0,0..0,2
  .value Constant 42 - 0,0..0,2
'''),

(468, 'parse_pattern', 0, 0, 'MatchSingleton', {}, (MatchSingleton,
r'''None'''),
r'''MatchSingleton None - ROOT 0,0..0,4'''),

(469, 'parse_pattern', 0, 0, 'MatchSequence', {}, (MatchSequence,
r'''[a, *_]'''), r'''
MatchSequence - ROOT 0,0..0,7
  .patterns[2]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchStar - 0,4..0,6
'''),

(470, 'parse_pattern', 0, 0, 'MatchSequence', {}, (MatchSequence,
r'''[]'''),
r'''MatchSequence - ROOT 0,0..0,2'''),

(471, 'parse_pattern', 0, 0, 'MatchMapping', {}, (MatchMapping,
r'''{"key": _}'''), r'''
MatchMapping - ROOT 0,0..0,10
  .keys[1]
   0] Constant 'key' - 0,1..0,6
  .patterns[1]
   0] MatchAs - 0,8..0,9
'''),

(472, 'parse_pattern', 0, 0, 'MatchMapping', {}, (MatchMapping,
r'''{}'''),
r'''MatchMapping - ROOT 0,0..0,2'''),

(473, 'parse_pattern', 0, 0, 'MatchClass', {}, (MatchClass,
r'''SomeClass()'''), r'''
MatchClass - ROOT 0,0..0,11
  .cls Name 'SomeClass' Load - 0,0..0,9
'''),

(474, 'parse_pattern', 0, 0, 'MatchClass', {}, (MatchClass,
r'''SomeClass(attr=val)'''), r'''
MatchClass - ROOT 0,0..0,19
  .cls Name 'SomeClass' Load - 0,0..0,9
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 0,15..0,18
     .name 'val'
'''),

(475, 'parse_pattern', 0, 0, 'MatchAs', {}, (MatchAs,
r'''as_var'''), r'''
MatchAs - ROOT 0,0..0,6
  .name 'as_var'
'''),

(476, 'parse_pattern', 0, 0, 'MatchAs', {}, (MatchAs,
r'''1 as as_var'''), r'''
MatchAs - ROOT 0,0..0,11
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'as_var'
'''),

(477, 'parse_pattern', 0, 0, 'MatchOr', {}, (MatchOr,
r'''1 | 2 | 3'''), r'''
MatchOr - ROOT 0,0..0,9
  .patterns[3]
   0] MatchValue - 0,0..0,1
     .value Constant 1 - 0,0..0,1
   1] MatchValue - 0,4..0,5
     .value Constant 2 - 0,4..0,5
   2] MatchValue - 0,8..0,9
     .value Constant 3 - 0,8..0,9
'''),

(478, 'parse_pattern', 0, 0, 'MatchAs', {}, (MatchAs,
r'''_'''),
r'''MatchAs - ROOT 0,0..0,1'''),

(479, 'parse_pattern', 0, 0, 'MatchStar', {}, (MatchStar,
r'''*a'''), r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

(480, 'parse_expr', 0, 0, 'Tuple', {}, ('expr',
r''' *a,  # tail'''), r'''
Tuple - ROOT 0,1..0,4
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'a' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

(481, 'parse_expr_arglike', 0, 0, 'Starred', {}, ('expr_arglike',
r''' *not a  # tail'''), r'''
Starred - ROOT 0,1..0,7
  .value UnaryOp - 0,2..0,7
    .op Not - 0,2..0,5
    .operand Name 'a' Load - 0,6..0,7
  .ctx Load
'''),

(482, 'parse_expr_slice', 0, 0, 'Slice', {}, ('expr_slice',
r''' a:b:c  # tail'''), r'''
Slice - ROOT 0,1..0,6
  .lower Name 'a' Load - 0,1..0,2
  .upper Name 'b' Load - 0,3..0,4
  .step Name 'c' Load - 0,5..0,6
'''),

(483, 'parse_expr_slice', 0, 0, 'Yield', {}, ('expr_slice',
r''' yield  # tail'''),
r'''Yield - ROOT 0,1..0,6'''),

(484, 'parse_boolop', 0, 0, 'And', {}, ('boolop',
r''' and  # tail'''),
r'''And - ROOT 0,1..0,4'''),

(485, 'parse_binop', 0, 0, 'RShift', {}, ('binop',
r''' >>  # tail'''),
r'''RShift - ROOT 0,1..0,3'''),

(486, 'parse_augop', 0, 0, 'SyntaxError', {}, ('augop',
r''' >>=  # tail'''),
r'''**SyntaxError('invalid syntax')**'''),

(487, 'parse_unaryop', 0, 0, 'Invert', {}, ('unaryop',
r''' ~  # tail'''),
r'''Invert - ROOT 0,1..0,2'''),

(488, 'parse_cmpop', 0, 0, 'GtE', {}, ('cmpop',
r''' >=  # tail'''),
r'''GtE - ROOT 0,1..0,3'''),

(489, 'parse_comprehension', 0, 0, 'comprehension', {}, ('comprehension',
r''' for i in j  # tail'''), r'''
comprehension - ROOT 0,1..0,11
  .target Name 'i' Store - 0,5..0,6
  .iter Name 'j' Load - 0,10..0,11
  .is_async 0
'''),

(490, 'parse_arguments', 0, 0, 'arguments', {}, ('arguments',
r''' a: list[str], /, b: int = 1, *c, d=100, **e  # tail'''), r'''
arguments - ROOT 0,1..0,44
  .posonlyargs[1]
   0] arg - 0,1..0,13
     .arg 'a'
     .annotation Subscript - 0,4..0,13
       .value Name 'list' Load - 0,4..0,8
       .slice Name 'str' Load - 0,9..0,12
       .ctx Load
  .args[1]
   0] arg - 0,18..0,24
     .arg 'b'
     .annotation Name 'int' Load - 0,21..0,24
  .vararg arg - 0,31..0,32
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 0,34..0,35
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 0,36..0,39
  .kwarg arg - 0,43..0,44
    .arg 'e'
  .defaults[1]
   0] Constant 1 - 0,27..0,28
'''),

(491, 'parse_arguments_lambda', 0, 0, 'arguments', {}, ('arguments_lambda',
r''' a, /, b, *c, d=100, **e  # tail'''), r'''
arguments - ROOT 0,1..0,24
  .posonlyargs[1]
   0] arg - 0,1..0,2
     .arg 'a'
  .args[1]
   0] arg - 0,7..0,8
     .arg 'b'
  .vararg arg - 0,11..0,12
    .arg 'c'
  .kwonlyargs[1]
   0] arg - 0,14..0,15
     .arg 'd'
  .kw_defaults[1]
   0] Constant 100 - 0,16..0,19
  .kwarg arg - 0,23..0,24
    .arg 'e'
'''),

(492, 'parse_arg', 0, 0, 'arg', {}, ('arg',
r''' a: b  # tail'''), r'''
arg - ROOT 0,1..0,5
  .arg 'a'
  .annotation Name 'b' Load - 0,4..0,5
'''),

(493, 'parse_keyword', 0, 0, 'keyword', {}, ('keyword',
r''' a=1  # tail'''), r'''
keyword - ROOT 0,1..0,4
  .arg 'a'
  .value Constant 1 - 0,3..0,4
'''),

(494, 'parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r''' a.b  # tail'''), r'''
alias - ROOT 0,1..0,4
  .name 'a.b'
'''),

(495, 'parse_ImportFrom_name', 0, 0, 'alias', {}, ('ImportFrom_name',
r''' *  # tail'''), r'''
alias - ROOT 0,1..0,2
  .name '*'
'''),

(496, 'parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r''' a as b,  # tail'''), r'''
withitem - ROOT 0,1..0,7
  .context_expr Name 'a' Load - 0,1..0,2
  .optional_vars Name 'b' Store - 0,6..0,7
'''),

(497, 'parse_pattern', 0, 0, 'MatchOr', {}, ('pattern',
r''' 1 | 2 | 3  # tail'''), r'''
MatchOr - ROOT 0,1..0,10
  .patterns[3]
   0] MatchValue - 0,1..0,2
     .value Constant 1 - 0,1..0,2
   1] MatchValue - 0,5..0,6
     .value Constant 2 - 0,5..0,6
   2] MatchValue - 0,9..0,10
     .value Constant 3 - 0,9..0,10
'''),

(498, 'parse_pattern', 0, 0, 'MatchStar', {}, ('pattern',
r''' *a  # tail'''), r'''
MatchStar - ROOT 0,1..0,3
  .name 'a'
'''),

(499, 'parse_ExceptHandler', 0, 0, 'ExceptHandler', {'_ver': 11}, ('ExceptHandler',
r'''except* Exception: pass'''), r'''
ExceptHandler - ROOT 0,0..0,23
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
   0] Pass - 0,19..0,23
'''),

(500, 'parse_expr_all', 0, 0, 'Starred', {'_ver': 11}, ('expr_all',
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(501, 'parse_expr_slice', 0, 0, 'Tuple', {'_ver': 11}, ('expr_slice',
r'''*s'''), r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 's' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

(502, 'parse_expr_slice', 0, 0, 'Tuple', {'_ver': 11}, ('expr_slice',
r'''*not a'''), r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
   0] Starred - 0,0..0,6
     .value UnaryOp - 0,1..0,6
       .op Not - 0,1..0,4
       .operand Name 'a' Load - 0,5..0,6
     .ctx Load
  .ctx Load
'''),

(503, 'parse_expr_sliceelt', 0, 0, 'Starred', {'_ver': 11}, ('expr_sliceelt',
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(504, 'parse_expr_sliceelt', 0, 0, 'SyntaxError', {'_ver': 11}, ('expr_sliceelt',
r'''*not a, *b or c'''),
r'''**SyntaxError('invalid expression')**'''),

(505, 'parse_ExceptHandler', 0, 0, 'ExceptHandler', {'_ver': 11}, (ExceptHandler,
r'''except* Exception: pass'''), r'''
ExceptHandler - ROOT 0,0..0,23
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
   0] Pass - 0,19..0,23
'''),

(506, 'parse_arg', 0, 0, 'arg', {'_ver': 11}, ('arg',
r''' a: *b  # tail'''), r'''
arg - ROOT 0,1..0,6
  .arg 'a'
  .annotation Starred - 0,4..0,6
    .value Name 'b' Load - 0,5..0,6
    .ctx Load
'''),

(507, 'parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('all',
r'''*U, **V, **Z'''), r'''
_type_params - ROOT 0,0..0,12
  .type_params[3]
   0] TypeVarTuple - 0,0..0,2
     .name 'U'
   1] ParamSpec - 0,4..0,7
     .name 'V'
   2] ParamSpec - 0,9..0,12
     .name 'Z'
'''),

(508, 'parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('all',
r'''T: int, *U, **V, **Z'''), r'''
_type_params - ROOT 0,0..0,20
  .type_params[4]
   0] TypeVar - 0,0..0,6
     .name 'T'
     .bound Name 'int' Load - 0,3..0,6
   1] TypeVarTuple - 0,8..0,10
     .name 'U'
   2] ParamSpec - 0,12..0,15
     .name 'V'
   3] ParamSpec - 0,17..0,20
     .name 'Z'
'''),

(509, 'parse_type_param', 0, 0, 'TypeVar', {'_ver': 12}, ('type_param',
r'''a: int'''), r'''
TypeVar - ROOT 0,0..0,6
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
'''),

(510, 'parse_type_param', 0, 0, 'ParamSpec', {'_ver': 12}, ('type_param',
r'''**a'''), r'''
ParamSpec - ROOT 0,0..0,3
  .name 'a'
'''),

(511, 'parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 12}, ('type_param',
r'''*a'''), r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

(512, 'parse_type_param', 0, 0, 'ParseError', {'_ver': 12}, ('type_param',
r'''a: int,'''),
r'''**ParseError('expecting single type_param, has trailing comma')**'''),

(513, 'parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r''''''),
r'''_type_params - ROOT 0,0..0,0'''),

(514, 'parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r'''a: int'''), r'''
_type_params - ROOT 0,0..0,6
  .type_params[1]
   0] TypeVar - 0,0..0,6
     .name 'a'
     .bound Name 'int' Load - 0,3..0,6
'''),

(515, 'parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r'''a: int,'''), r'''
_type_params - ROOT 0,0..0,7
  .type_params[1]
   0] TypeVar - 0,0..0,6
     .name 'a'
     .bound Name 'int' Load - 0,3..0,6
'''),

(516, 'parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r'''a: int, *b, **c'''), r'''
_type_params - ROOT 0,0..0,15
  .type_params[3]
   0] TypeVar - 0,0..0,6
     .name 'a'
     .bound Name 'int' Load - 0,3..0,6
   1] TypeVarTuple - 0,8..0,10
     .name 'b'
   2] ParamSpec - 0,12..0,15
     .name 'c'
'''),

(517, 'parse_type_param', 0, 0, 'TypeVar', {'_ver': 12}, (type_param,
r'''a: int'''), r'''
TypeVar - ROOT 0,0..0,6
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
'''),

(518, 'parse_type_param', 0, 0, 'TypeVar', {'_ver': 12}, (TypeVar,
r'''a: int'''), r'''
TypeVar - ROOT 0,0..0,6
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
'''),

(519, 'parse_type_param', 0, 0, 'ParamSpec', {'_ver': 12}, (type_param,
r'''**a'''), r'''
ParamSpec - ROOT 0,0..0,3
  .name 'a'
'''),

(520, 'parse_type_param', 0, 0, 'ParamSpec', {'_ver': 12}, (ParamSpec,
r'''**a'''), r'''
ParamSpec - ROOT 0,0..0,3
  .name 'a'
'''),

(521, 'parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 12}, (type_param,
r'''*a'''), r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

(522, 'parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 12}, (TypeVarTuple,
r'''*a'''), r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

(523, 'parse_type_param', 0, 0, 'TypeVar', {'_ver': 12}, ('type_param',
r''' a: int  # tail'''), r'''
TypeVar - ROOT 0,1..0,7
  .name 'a'
  .bound Name 'int' Load - 0,4..0,7
'''),

(524, 'parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r''' a: int, *b, **c  # tail'''), r'''
_type_params - ROOT 0,0..0,24
  .type_params[3]
   0] TypeVar - 0,1..0,7
     .name 'a'
     .bound Name 'int' Load - 0,4..0,7
   1] TypeVarTuple - 0,9..0,11
     .name 'b'
   2] ParamSpec - 0,13..0,16
     .name 'c'
'''),

(525, 'parse_type_param', 0, 0, 'ParamSpec', {'_ver': 13}, ('all',
r'''**a = {T: int, U: str}'''), r'''
ParamSpec - ROOT 0,0..0,22
  .name 'a'
  .default_value Dict - 0,6..0,22
    .keys[2]
     0] Name 'T' Load - 0,7..0,8
     1] Name 'U' Load - 0,15..0,16
    .values[2]
     0] Name 'int' Load - 0,10..0,13
     1] Name 'str' Load - 0,18..0,21
'''),

(526, 'parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 13}, ('all',
r'''*a = (int, str)'''), r'''
TypeVarTuple - ROOT 0,0..0,15
  .name 'a'
  .default_value Tuple - 0,5..0,15
    .elts[2]
     0] Name 'int' Load - 0,6..0,9
     1] Name 'str' Load - 0,11..0,14
    .ctx Load
'''),

(527, 'parse_type_param', 0, 0, 'TypeVar', {'_ver': 13}, ('type_param',
r'''a: int = int'''), r'''
TypeVar - ROOT 0,0..0,12
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
  .default_value Name 'int' Load - 0,9..0,12
'''),

(528, 'parse_type_param', 0, 0, 'ParamSpec', {'_ver': 13}, ('type_param',
r'''**a = {T: int, U: str}'''), r'''
ParamSpec - ROOT 0,0..0,22
  .name 'a'
  .default_value Dict - 0,6..0,22
    .keys[2]
     0] Name 'T' Load - 0,7..0,8
     1] Name 'U' Load - 0,15..0,16
    .values[2]
     0] Name 'int' Load - 0,10..0,13
     1] Name 'str' Load - 0,18..0,21
'''),

(529, 'parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 13}, ('type_param',
r'''*a = (int, str)'''), r'''
TypeVarTuple - ROOT 0,0..0,15
  .name 'a'
  .default_value Tuple - 0,5..0,15
    .elts[2]
     0] Name 'int' Load - 0,6..0,9
     1] Name 'str' Load - 0,11..0,14
    .ctx Load
'''),

(530, 'parse_type_param', 0, 0, 'TypeVar', {'_ver': 13}, (type_param,
r'''a: int = int'''), r'''
TypeVar - ROOT 0,0..0,12
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
  .default_value Name 'int' Load - 0,9..0,12
'''),

(531, 'parse_type_param', 0, 0, 'TypeVar', {'_ver': 13}, (TypeVar,
r'''a: int = int'''), r'''
TypeVar - ROOT 0,0..0,12
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
  .default_value Name 'int' Load - 0,9..0,12
'''),

(532, 'parse_type_param', 0, 0, 'ParamSpec', {'_ver': 13}, (type_param,
r'''**a = {T: int, U: str}'''), r'''
ParamSpec - ROOT 0,0..0,22
  .name 'a'
  .default_value Dict - 0,6..0,22
    .keys[2]
     0] Name 'T' Load - 0,7..0,8
     1] Name 'U' Load - 0,15..0,16
    .values[2]
     0] Name 'int' Load - 0,10..0,13
     1] Name 'str' Load - 0,18..0,21
'''),

(533, 'parse_type_param', 0, 0, 'ParamSpec', {'_ver': 13}, (ParamSpec,
r'''**a = {T: int, U: str}'''), r'''
ParamSpec - ROOT 0,0..0,22
  .name 'a'
  .default_value Dict - 0,6..0,22
    .keys[2]
     0] Name 'T' Load - 0,7..0,8
     1] Name 'U' Load - 0,15..0,16
    .values[2]
     0] Name 'int' Load - 0,10..0,13
     1] Name 'str' Load - 0,18..0,21
'''),

(534, 'parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 13}, (type_param,
r'''*a = (int, str)'''), r'''
TypeVarTuple - ROOT 0,0..0,15
  .name 'a'
  .default_value Tuple - 0,5..0,15
    .elts[2]
     0] Name 'int' Load - 0,6..0,9
     1] Name 'str' Load - 0,11..0,14
    .ctx Load
'''),

(535, 'parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 13}, (TypeVarTuple,
r'''*a = (int, str)'''), r'''
TypeVarTuple - ROOT 0,0..0,15
  .name 'a'
  .default_value Tuple - 0,5..0,15
    .elts[2]
     0] Name 'int' Load - 0,6..0,9
     1] Name 'str' Load - 0,11..0,14
    .ctx Load
'''),
],

}
