# ('parse_function', NOT_USED, NOT_USED, 'expected_class', NOT_USED, (parse_mode, code),
#
# code,
# dump code)
# - OR
# error)

from fst.asttypes import *

DATA_PARSE_AUTOGEN = {
'autogen': [  # ................................................................................

('parse_stmts', 0, 0, 'Module', {}, ('all', r'''
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

('parse__ExceptHandlers', 0, 0, '_ExceptHandlers', {}, ('all', r'''
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

('parse__match_cases', 0, 0, '_match_cases', {}, ('all', r'''
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

('parse_stmt', 0, 0, 'AnnAssign', {}, ('all',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

('parse_ExceptHandler', 0, 0, 'ExceptHandler', {}, ('all',
r'''except: pass'''), r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
'''),

('parse_match_case', 0, 0, 'match_case', {}, ('all',
r'''case None: pass'''), r'''
match_case - ROOT 0,0..0,15
  .pattern MatchSingleton None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

('parse_stmts', 0, 0, 'Module', {}, ('all', r'''
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

('parse_stmt', 0, 0, 'AnnAssign', {}, ('all',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

('parse__ExceptHandlers', 0, 0, '_ExceptHandlers', {}, ('all', r'''
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

('parse_ExceptHandler', 0, 0, 'ExceptHandler', {}, ('all',
r'''except: pass'''), r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
'''),

('parse__match_cases', 0, 0, '_match_cases', {}, ('all', r'''
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

('parse_match_case', 0, 0, 'match_case', {}, ('all',
r'''case None: pass'''), r'''
match_case - ROOT 0,0..0,15
  .pattern MatchSingleton None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

('parse_expr', 0, 0, 'Name', {}, ('all',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_expr', 0, 0, 'Starred', {}, ('all',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

('parse_expr_all', 0, 0, 'Starred', {}, ('all',
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('parse_stmt', 0, 0, 'AnnAssign', {}, ('all',
r'''a:b'''), r'''
AnnAssign - ROOT 0,0..0,3
  .target Name 'a' Store - 0,0..0,1
  .annotation Name 'b' Load - 0,2..0,3
  .simple 1
'''),

('parse_expr_all', 0, 0, 'Slice', {}, ('all',
r'''a:b:c'''), r'''
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5
'''),

('parse_expr_all', 0, 0, 'Slice', {}, ('all',
r''':b:c'''), r'''
Slice - ROOT 0,0..0,4
  .upper Name 'b' Load - 0,1..0,2
  .step Name 'c' Load - 0,3..0,4
'''),

('parse_expr_all', 0, 0, 'Slice', {}, ('all',
r'''::'''),
r'''Slice - ROOT 0,0..0,2'''),

('parse_expr_all', 0, 0, 'Slice', {}, ('all',
r''':'''),
r'''Slice - ROOT 0,0..0,1'''),

('parse_pattern', 0, 0, 'MatchAs', {}, ('all',
r'''1 as a'''), r'''
MatchAs - ROOT 0,0..0,6
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'a'
'''),

('parse_arguments', 0, 0, 'arguments', {}, ('all',
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

('parse_arguments_lambda', 0, 0, 'arguments', {}, ('all',
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

('parse_arguments', 0, 0, 'arguments', {}, ('all',
r'''**a: dict'''), r'''
arguments - ROOT 0,0..0,9
  .kwarg arg - 0,2..0,9
    .arg 'a'
    .annotation Name 'dict' Load - 0,5..0,9
'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, ('all',
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

('parse_comprehension', 0, 0, 'comprehension', {}, ('all',
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

('parse__comprehensions', 0, 0, '_comprehensions', {}, ('all',
r'''for j in k if j async for i in j if i'''), r'''
_comprehensions - ROOT 0,0..0,37
  .generators[2]
   0] comprehension - 0,0..0,15
     .target Name 'j' Store - 0,4..0,5
     .iter Name 'k' Load - 0,9..0,10
     .ifs[1]
      0] Name 'j' Load - 0,14..0,15
     .is_async 0
   1] comprehension - 0,16..0,37
     .target Name 'i' Store - 0,26..0,27
     .iter Name 'j' Load - 0,31..0,32
     .ifs[1]
      0] Name 'i' Load - 0,36..0,37
     .is_async 1
'''),

('parse__comprehension_ifs', 0, 0, '_comprehension_ifs', {}, ('all',
r'''if u'''), r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'u' Load - 0,3..0,4
'''),

('parse__comprehension_ifs', 0, 0, '_comprehension_ifs', {}, ('all',
r'''if u if v'''), r'''
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[2]
   0] Name 'u' Load - 0,3..0,4
   1] Name 'v' Load - 0,8..0,9
'''),

('parse_withitem', 0, 0, 'withitem', {}, ('all',
r'''f(**a) as b'''), r'''
withitem - ROOT 0,0..0,11
  .context_expr Call - 0,0..0,6
    .func Name 'f' Load - 0,0..0,1
    .keywords[1]
     0] keyword - 0,2..0,5
       .value Name 'a' Load - 0,4..0,5
  .optional_vars Name 'b' Store - 0,10..0,11
'''),

('parse__withitems', 0, 0, '_withitems', {}, ('all',
r'''f(**a) as b,'''), r'''
_withitems - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,0..0,11
     .context_expr Call - 0,0..0,6
       .func Name 'f' Load - 0,0..0,1
       .keywords[1]
        0] keyword - 0,2..0,5
          .value Name 'a' Load - 0,4..0,5
     .optional_vars Name 'b' Store - 0,10..0,11
'''),

('parse__withitems', 0, 0, '_withitems', {}, ('all',
r'''f(**a) as b, c as d'''), r'''
_withitems - ROOT 0,0..0,19
  .items[2]
   0] withitem - 0,0..0,11
     .context_expr Call - 0,0..0,6
       .func Name 'f' Load - 0,0..0,1
       .keywords[1]
        0] keyword - 0,2..0,5
          .value Name 'a' Load - 0,4..0,5
     .optional_vars Name 'b' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'c' Load - 0,13..0,14
     .optional_vars Name 'd' Store - 0,18..0,19
'''),

('parse_operator', 0, 0, 'Mult', {}, ('all',
r'''*'''),
r'''Mult - ROOT 0,0..0,1'''),

('parse_cmpop', 0, 0, 'Gt', {}, ('all',
r'''>'''),
r'''Gt - ROOT 0,0..0,1'''),

('parse_boolop', 0, 0, 'And', {}, ('all',
r'''and'''),
r'''And - ROOT 0,0..0,3'''),

('parse_unaryop', 0, 0, 'Invert', {}, ('all',
r'''~'''),
r'''Invert - ROOT 0,0..0,1'''),

('parse_operator', 0, 0, 'LShift', {}, ('all',
r'''<<'''),
r'''LShift - ROOT 0,0..0,2'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('all',
r'''a = '''), r'''
_Assign_targets - ROOT 0,0..0,4
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('all',
r'''a = b ='''), r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
'''),

('parse__decorator_list', 0, 0, '_decorator_list', {}, ('all',
r'''@a'''), r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('parse__decorator_list', 0, 0, '_decorator_list', {}, ('all', r'''
@a
@b
'''), r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,1..1,2
'''),

('parse_stmt', 0, 0, 'Assign', {}, ('all',
r'''_ = 1'''), r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name '_' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

('parse_stmt', 0, 0, 'Assign', {}, ('all',
r'''case = 1'''), r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'case' Store - 0,0..0,4
  .value Constant 1 - 0,7..0,8
'''),

('parse_stmt', 0, 0, 'Assign', {}, ('all',
r'''match = 1'''), r'''
Assign - ROOT 0,0..0,9
  .targets[1]
   0] Name 'match' Store - 0,0..0,5
  .value Constant 1 - 0,8..0,9
'''),

('parse_stmt', 0, 0, 'Assign', {}, ('all',
r'''type = 1'''), r'''
Assign - ROOT 0,0..0,8
  .targets[1]
   0] Name 'type' Store - 0,0..0,4
  .value Constant 1 - 0,7..0,8
'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('all',
r'''elif'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('all',
r'''else'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('all',
r'''finally'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('all',
r'''as'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_stmts', 0, 0, 'Module', {}, ('strict', r'''
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

('parse__ExceptHandlers', 0, 0, 'SyntaxError', {}, ('strict', r'''
except Exception: pass
except: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__match_cases', 0, 0, 'SyntaxError', {}, ('strict', r'''
case None: pass
case 1: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_stmt', 0, 0, 'AnnAssign', {}, ('strict',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

('parse_ExceptHandler', 0, 0, 'SyntaxError', {}, ('strict',
r'''except: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_match_case', 0, 0, 'SyntaxError', {}, ('strict',
r'''case None: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_stmts', 0, 0, 'Module', {}, ('strict', r'''
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

('parse_stmt', 0, 0, 'AnnAssign', {}, ('strict',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

('parse__ExceptHandlers', 0, 0, 'SyntaxError', {}, ('strict', r'''
except Exception: pass
except: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_ExceptHandler', 0, 0, 'SyntaxError', {}, ('strict',
r'''except: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__match_cases', 0, 0, 'SyntaxError', {}, ('strict', r'''
case None: pass
case 1: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_match_case', 0, 0, 'SyntaxError', {}, ('strict',
r'''case None: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_expr', 0, 0, 'Name', {}, ('strict',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_expr', 0, 0, 'Starred', {}, ('strict',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''*not a'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_stmt', 0, 0, 'AnnAssign', {}, ('strict',
r'''a:b'''), r'''
AnnAssign - ROOT 0,0..0,3
  .target Name 'a' Store - 0,0..0,1
  .annotation Name 'b' Load - 0,2..0,3
  .simple 1
'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''a:b:c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''1 as a'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''a, /, b, *c, d=100, **e'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''*not a'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''for i in range(5) if i'''),
r'''**SyntaxError("expected 'else' after 'if' expression")**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''f(**a) as b'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''*'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''*='''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''>'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''and'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_all', 0, 0, 'SyntaxError', {}, ('strict',
r'''~'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_Module', 0, 0, 'Module', {}, ('exec',
r'''i: int = 1'''), r'''
Module - ROOT 0,0..0,10
  .body[1]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
'''),

('parse_Expression', 0, 0, 'Expression', {}, ('eval',
r'''None'''), r'''
Expression - ROOT 0,0..0,4
  .body Constant None - 0,0..0,4
'''),

('parse_Interactive', 0, 0, 'Interactive', {}, ('single',
r'''i: int = 1'''), r'''
Interactive - ROOT 0,0..0,10
  .body[1]
   0] AnnAssign - 0,0..0,10
     .target Name 'i' Store - 0,0..0,1
     .annotation Name 'int' Load - 0,3..0,6
     .value Constant 1 - 0,9..0,10
     .simple 1
'''),

('parse_stmts', 0, 0, 'Module', {}, ('stmts', r'''
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

('parse_stmts', 0, 0, 'SyntaxError', {}, ('stmts', r'''
except Exception: pass
except: pass
'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_stmt', 0, 0, 'AnnAssign', {}, ('stmt',
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

('parse_stmt', 0, 0, 'Expr', {}, ('stmt',
r'''j'''), r'''
Expr - ROOT 0,0..0,1
  .value Name 'j' Load - 0,0..0,1
'''),

('parse_stmt', 0, 0, 'ParseError', {}, ('stmt', r'''
i: int = 1
j
'''),
r'''**ParseError('expecting single stmt')**'''),

('parse_stmt', 0, 0, 'SyntaxError', {}, ('stmt',
r'''except: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__ExceptHandlers', 0, 0, '_ExceptHandlers', {}, ('_ExceptHandlers', r'''
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

('parse__ExceptHandlers', 0, 0, 'IndentationError', {}, ('_ExceptHandlers', r'''
 except Exception: pass
except: pass
'''),
r'''**IndentationError('unexpected indent')**'''),

('parse__ExceptHandlers', 0, 0, 'ParseError', {}, ('_ExceptHandlers', r'''
except Exception: pass
except: pass
else: pass
'''),
r'''**ParseError("not expecting 'else' block")**'''),

('parse__ExceptHandlers', 0, 0, 'ParseError', {}, ('_ExceptHandlers', r'''
except Exception: pass
except: pass
finally: pass
'''),
r'''**ParseError("not expecting 'finally' block")**'''),

('parse__ExceptHandlers', 0, 0, 'SyntaxError', {}, ('_ExceptHandlers', r'''
i: int = 1
j
'''),
r'''**SyntaxError("expected 'except' or 'finally' block")**'''),

('parse_ExceptHandler', 0, 0, 'ExceptHandler', {}, ('ExceptHandler',
r'''except: pass'''), r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
'''),

('parse_ExceptHandler', 0, 0, 'ParseError', {}, ('ExceptHandler', r'''
except Exception: pass
except: pass
'''),
r'''**ParseError('expecting single ExceptHandler')**'''),

('parse_ExceptHandler', 0, 0, 'IndentationError', {}, ('ExceptHandler', r'''
except:
  pass
    pass
'''),
r'''**IndentationError('unexpected indent')**'''),

('parse_ExceptHandler', 0, 0, 'IndentationError', {}, ('ExceptHandler',
r'''  except: pass'''),
r'''**IndentationError('unexpected indent')**'''),

('parse_ExceptHandler', 0, 0, 'ParseError', {}, ('ExceptHandler',
r'''finally: pass'''),
r'''**ParseError("not expecting 'finally' block")**'''),

('parse_ExceptHandler', 0, 0, 'SyntaxError', {}, ('ExceptHandler',
r'''else: pass'''),
r'''**SyntaxError("expected 'except' or 'finally' block")**'''),

('parse_ExceptHandler', 0, 0, 'SyntaxError', {}, ('ExceptHandler',
r'''i: int = 1'''),
r'''**SyntaxError("expected 'except' or 'finally' block")**'''),

('parse__match_cases', 0, 0, '_match_cases', {}, ('_match_cases', r'''
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

('parse__match_cases', 0, 0, 'IndentationError', {}, ('_match_cases', r'''
 case None: pass
case 1: pass
'''),
r'''**IndentationError('unexpected indent')**'''),

('parse__match_cases', 0, 0, 'SyntaxError', {}, ('_match_cases',
r'''i: int = 1'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_match_case', 0, 0, 'match_case', {}, ('match_case',
r'''case None: pass'''), r'''
match_case - ROOT 0,0..0,15
  .pattern MatchSingleton None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

('parse_match_case', 0, 0, 'ParseError', {}, ('match_case', r'''
case None: pass
case 1: pass
'''),
r'''**ParseError('expecting single match_case')**'''),

('parse_match_case', 0, 0, 'SyntaxError', {}, ('match_case',
r'''i: int = 1'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r''''''),
r'''_Assign_targets - ROOT 0,0..0,0'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a'''), r'''
_Assign_targets - ROOT 0,0..0,1
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a ='''), r'''
_Assign_targets - ROOT 0,0..0,3
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a = b'''), r'''
_Assign_targets - ROOT 0,0..0,5
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r'''a = b ='''), r'''
_Assign_targets - ROOT 0,0..0,7
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets', r'''
\
a\
 = \

'''), r'''
_Assign_targets - ROOT 0,0..3,0
  .targets[1]
   0] Name 'a' Store - 1,0..1,1
'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets',
r''' a'''), r'''
_Assign_targets - ROOT 0,0..0,2
  .targets[1]
   0] Name 'a' Store - 0,1..0,2
'''),

('parse__Assign_targets', 0, 0, '_Assign_targets', {}, ('_Assign_targets', r'''

a
'''), r'''
_Assign_targets - ROOT 0,0..1,1
  .targets[1]
   0] Name 'a' Store - 1,0..1,1
'''),

('parse__Assign_targets', 0, 0, 'SyntaxError', {}, ('_Assign_targets', r'''


a
'''),
r'''**SyntaxError('invalid Assign targets slice')**'''),

('parse__Assign_targets', 0, 0, 'SyntaxError', {}, ('_Assign_targets', r'''
a
=
'''),
r'''**SyntaxError('invalid Assign targets slice')**'''),

('parse__Assign_targets', 0, 0, 'SyntaxError', {}, ('_Assign_targets',
r'''a =  # tail'''),
r'''**SyntaxError('invalid Assign targets slice')**'''),

('parse__Assign_targets', 0, 0, 'SyntaxError', {}, ('_Assign_targets', r'''
# head
a =
'''),
r'''**SyntaxError('invalid Assign targets slice')**'''),

('parse__decorator_list', 0, 0, '_decorator_list', {}, ('_decorator_list',
r''''''),
r'''_decorator_list - ROOT 0,0..0,0'''),

('parse__decorator_list', 0, 0, '_decorator_list', {}, ('_decorator_list',
r'''@a'''), r'''
_decorator_list - ROOT 0,0..0,2
  .decorator_list[1]
   0] Name 'a' Load - 0,1..0,2
'''),

('parse__decorator_list', 0, 0, '_decorator_list', {}, ('_decorator_list', r'''
@a
@b
'''), r'''
_decorator_list - ROOT 0,0..1,2
  .decorator_list[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 1,1..1,2
'''),

('parse_expr', 0, 0, 'Name', {}, ('expr',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_expr', 0, 0, 'Starred', {}, ('expr',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

('parse_expr', 0, 0, 'Starred', {}, ('expr', r'''
*
s
'''), r'''
Starred - ROOT 0,0..1,1
  .value Name 's' Load - 1,0..1,1
  .ctx Load
'''),

('parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'SyntaxError', {}, ('expr',
r'''*not a'''),
r'''**SyntaxError('invalid expression (standard)')**'''),

('parse_expr', 0, 0, 'SyntaxError', {}, ('expr',
r'''a:b'''),
r'''**SyntaxError('invalid expression (standard)')**'''),

('parse_expr', 0, 0, 'SyntaxError', {}, ('expr',
r'''a:b:c'''),
r'''**SyntaxError('invalid expression (standard)')**'''),

('parse_expr', 0, 0, 'SyntaxError', {}, ('expr',
r''''''),
r'''**SyntaxError('expecting expression')**'''),

('parse_expr_all', 0, 0, 'Name', {}, ('expr_all',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_expr_all', 0, 0, 'Starred', {}, ('expr_all',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

('parse_expr_all', 0, 0, 'Starred', {}, ('expr_all', r'''
*
s
'''), r'''
Starred - ROOT 0,0..1,1
  .value Name 's' Load - 1,0..1,1
  .ctx Load
'''),

('parse_expr_all', 0, 0, 'Tuple', {}, ('expr_all', r'''
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

('parse_expr_all', 0, 0, 'Tuple', {}, ('expr_all', r'''
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

('parse_expr_all', 0, 0, 'Slice', {}, ('expr_all',
r'''a:b'''), r'''
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
'''),

('parse_expr_all', 0, 0, 'Slice', {}, ('expr_all',
r'''a:b:c'''), r'''
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5
'''),

('parse_expr_all', 0, 0, 'Tuple', {}, ('expr_all',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

('parse_expr_all', 0, 0, 'Tuple', {}, ('expr_all',
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

('parse_expr_arglike', 0, 0, 'Name', {}, ('expr_arglike',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_expr_arglike', 0, 0, 'Starred', {}, ('expr_arglike',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

('parse_expr_arglike', 0, 0, 'Tuple', {}, ('expr_arglike',
r'''*s,'''), r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 's' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('parse_expr_arglike', 0, 0, 'Starred', {}, ('expr_arglike',
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('parse_expr_arglike', 0, 0, 'SyntaxError', {}, ('expr_arglike',
r'''*not a,'''),
r'''**SyntaxError('invalid argument-like expression')**'''),

('parse_expr_arglike', 0, 0, 'Tuple', {}, ('expr_arglike',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

('parse_expr_arglike', 0, 0, 'ParseError', {}, ('expr_arglike',
r'''i=1'''),
r'''**ParseError('expecting single argumnent-like expression')**'''),

('parse_expr_arglike', 0, 0, 'SyntaxError', {}, ('expr_arglike',
r'''a:b'''),
r'''**SyntaxError('invalid argument-like expression')**'''),

('parse_expr_arglike', 0, 0, 'SyntaxError', {}, ('expr_arglike',
r'''a:b:c'''),
r'''**SyntaxError('invalid argument-like expression')**'''),

('parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''j'''), r'''
Tuple - ROOT 0,0..0,1
  .elts[1]
   0] Name 'j' Load - 0,0..0,1
  .ctx Load
'''),

('parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''*s'''), r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 's' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''*s,'''), r'''
Tuple - ROOT 0,0..0,3
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 's' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
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

('parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
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

('parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
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

('parse__expr_arglikes', 0, 0, 'Tuple', {}, ('_expr_arglikes',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

('parse__expr_arglikes', 0, 0, 'ParseError', {}, ('_expr_arglikes',
r'''i=1'''),
r'''**ParseError('expecting only argumnent-like expression(s), got keyword')**'''),

('parse__expr_arglikes', 0, 0, 'SyntaxError', {}, ('_expr_arglikes',
r'''a:b'''),
r'''**SyntaxError('invalid argument-like expression(s)')**'''),

('parse__expr_arglikes', 0, 0, 'SyntaxError', {}, ('_expr_arglikes',
r'''a:b:c'''),
r'''**SyntaxError('invalid argument-like expression(s)')**'''),

('parse_expr_slice', 0, 0, 'Name', {}, ('expr_slice',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_expr_slice', 0, 0, 'Slice', {}, ('expr_slice',
r'''a:b'''), r'''
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
'''),

('parse_expr_slice', 0, 0, 'Tuple', {}, ('expr_slice',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

('parse_expr_slice', 0, 0, 'Tuple', {}, ('expr_slice',
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

('parse_expr_slice', 0, 0, 'SyntaxError', {}, ('expr_slice',
r''''''),
r'''**SyntaxError('expecting slice expression')**'''),

('parse_Tuple_elt', 0, 0, 'Name', {}, ('Tuple_elt',
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_Tuple_elt', 0, 0, 'Starred', {}, ('Tuple_elt',
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

('parse_Tuple_elt', 0, 0, 'Slice', {}, ('Tuple_elt',
r'''a:b'''), r'''
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
'''),

('parse_Tuple_elt', 0, 0, 'Tuple', {}, ('Tuple_elt',
r'''j, k'''), r'''
Tuple - ROOT 0,0..0,4
  .elts[2]
   0] Name 'j' Load - 0,0..0,1
   1] Name 'k' Load - 0,3..0,4
  .ctx Load
'''),

('parse_Tuple_elt', 0, 0, 'SyntaxError', {}, ('Tuple_elt',
r'''a:b:c, x:y:z'''),
r'''**SyntaxError('invalid expression (standard)')**'''),

('parse_Tuple', 0, 0, 'ParseError', {}, ('Tuple',
r'''1'''),
r'''**ParseError('expecting Tuple, got Constant')**'''),

('parse_Tuple', 0, 0, 'ParseError', {}, ('Tuple',
r'''*st'''),
r'''**ParseError('expecting Tuple, got Starred')**'''),

('parse_boolop', 0, 0, 'And', {}, ('boolop',
r'''and'''),
r'''And - ROOT 0,0..0,3'''),

('parse_boolop', 0, 0, 'SyntaxError', {}, ('boolop',
r'''and 1'''),
r'''**SyntaxError("unexpected code after boolop, '1'")**'''),

('parse_boolop', 0, 0, 'SyntaxError', {}, ('boolop',
r'''*'''),
r'''**SyntaxError("expecting boolop, got '*'")**'''),

('parse_boolop', 0, 0, 'SyntaxError', {}, ('boolop',
r''''''),
r'''**SyntaxError('expecting boolop, got nothing')**'''),

('parse_operator', 0, 0, 'Mult', {}, ('operator',
r'''*'''),
r'''Mult - ROOT 0,0..0,1'''),

('parse_operator', 0, 0, 'SyntaxError', {}, ('operator',
r'''* 1'''),
r'''**SyntaxError("unexpected code after operator, '1'")**'''),

('parse_operator', 0, 0, 'SyntaxError', {}, ('operator',
r'''*='''),
r'''**SyntaxError("expecting operator, got '*='")**'''),

('parse_operator', 0, 0, 'SyntaxError', {}, ('operator',
r'''and'''),
r'''**SyntaxError("expecting operator, got 'and'")**'''),

('parse_operator', 0, 0, 'SyntaxError', {}, ('operator',
r''''''),
r'''**SyntaxError('expecting operator, got nothing')**'''),

('parse_unaryop', 0, 0, 'UAdd', {}, ('unaryop',
r'''+'''),
r'''UAdd - ROOT 0,0..0,1'''),

('parse_unaryop', 0, 0, 'SyntaxError', {}, ('unaryop',
r'''+ 1'''),
r'''**SyntaxError("unexpected code after unaryop, '1'")**'''),

('parse_unaryop', 0, 0, 'SyntaxError', {}, ('unaryop',
r'''and'''),
r'''**SyntaxError("expecting unaryop, got 'and'")**'''),

('parse_unaryop', 0, 0, 'SyntaxError', {}, ('unaryop',
r''''''),
r'''**SyntaxError('expecting unaryop, got nothing')**'''),

('parse_cmpop', 0, 0, 'GtE', {}, ('cmpop',
r'''>='''),
r'''GtE - ROOT 0,0..0,2'''),

('parse_cmpop', 0, 0, 'IsNot', {}, ('cmpop', r'''
is
not
'''),
r'''IsNot - ROOT 0,0..1,3'''),

('parse_cmpop', 0, 0, 'SyntaxError', {}, ('cmpop',
r'''+='''),
r'''**SyntaxError("expecting cmpop, got '+='")**'''),

('parse_cmpop', 0, 0, 'SyntaxError', {}, ('cmpop',
r'''>= a >='''),
r'''**SyntaxError("unexpected code after cmpop, 'a'")**'''),

('parse_cmpop', 0, 0, 'SyntaxError', {}, ('cmpop',
r'''and'''),
r'''**SyntaxError("expecting cmpop, got 'and'")**'''),

('parse_cmpop', 0, 0, 'SyntaxError', {}, ('cmpop',
r''''''),
r'''**SyntaxError('expecting cmpop, got nothing')**'''),

('parse_comprehension', 0, 0, 'comprehension', {}, ('comprehension',
r'''for u in v'''), r'''
comprehension - ROOT 0,0..0,10
  .target Name 'u' Store - 0,4..0,5
  .iter Name 'v' Load - 0,9..0,10
  .is_async 0
'''),

('parse_comprehension', 0, 0, 'comprehension', {}, ('comprehension',
r'''async for u in v'''), r'''
comprehension - ROOT 0,0..0,16
  .target Name 'u' Store - 0,10..0,11
  .iter Name 'v' Load - 0,15..0,16
  .is_async 1
'''),

('parse_comprehension', 0, 0, 'comprehension', {}, ('comprehension',
r'''for u in v if w'''), r'''
comprehension - ROOT 0,0..0,15
  .target Name 'u' Store - 0,4..0,5
  .iter Name 'v' Load - 0,9..0,10
  .ifs[1]
   0] Name 'w' Load - 0,14..0,15
  .is_async 0
'''),

('parse_comprehension', 0, 0, 'ParseError', {}, ('comprehension',
r'''for u in v async for s in t'''),
r'''**ParseError('expecting single comprehension')**'''),

('parse__comprehensions', 0, 0, '_comprehensions', {}, ('_comprehensions',
r''''''),
r'''_comprehensions - ROOT 0,0..0,0'''),

('parse__comprehensions', 0, 0, '_comprehensions', {}, ('_comprehensions',
r'''for u in v'''), r'''
_comprehensions - ROOT 0,0..0,10
  .generators[1]
   0] comprehension - 0,0..0,10
     .target Name 'u' Store - 0,4..0,5
     .iter Name 'v' Load - 0,9..0,10
     .is_async 0
'''),

('parse__comprehensions', 0, 0, '_comprehensions', {}, ('_comprehensions',
r'''async for u in v'''), r'''
_comprehensions - ROOT 0,0..0,16
  .generators[1]
   0] comprehension - 0,0..0,16
     .target Name 'u' Store - 0,10..0,11
     .iter Name 'v' Load - 0,15..0,16
     .is_async 1
'''),

('parse__comprehensions', 0, 0, '_comprehensions', {}, ('_comprehensions',
r'''for u in v if w async for s in t'''), r'''
_comprehensions - ROOT 0,0..0,32
  .generators[2]
   0] comprehension - 0,0..0,15
     .target Name 'u' Store - 0,4..0,5
     .iter Name 'v' Load - 0,9..0,10
     .ifs[1]
      0] Name 'w' Load - 0,14..0,15
     .is_async 0
   1] comprehension - 0,16..0,32
     .target Name 's' Store - 0,26..0,27
     .iter Name 't' Load - 0,31..0,32
     .is_async 1
'''),

('parse__comprehensions', 0, 0, 'ParseError', {}, ('_comprehensions',
r'''if i'''),
r'''**ParseError('expecting comprehensions, got comprehension ifs')**'''),

('parse__comprehensions', 0, 0, 'ParseError', {}, ('_comprehensions',
r''']+['''),
r'''**ParseError('expecting comprehensions, got BinOp')**'''),

('parse__comprehension_ifs', 0, 0, '_comprehension_ifs', {}, ('_comprehension_ifs',
r''''''),
r'''_comprehension_ifs - ROOT 0,0..0,0'''),

('parse__comprehension_ifs', 0, 0, '_comprehension_ifs', {}, ('_comprehension_ifs',
r'''if u'''), r'''
_comprehension_ifs - ROOT 0,0..0,4
  .ifs[1]
   0] Name 'u' Load - 0,3..0,4
'''),

('parse__comprehension_ifs', 0, 0, '_comprehension_ifs', {}, ('_comprehension_ifs',
r'''if u if v'''), r'''
_comprehension_ifs - ROOT 0,0..0,9
  .ifs[2]
   0] Name 'u' Load - 0,3..0,4
   1] Name 'v' Load - 0,8..0,9
'''),

('parse__comprehension_ifs', 0, 0, 'ParseError', {}, ('_comprehension_ifs',
r'''(a)'''),
r'''**ParseError('expecting comprehension ifs')**'''),

('parse__comprehension_ifs', 0, 0, 'ParseError', {}, ('_comprehension_ifs',
r'''.b'''),
r'''**ParseError('expecting comprehension ifs')**'''),

('parse__comprehension_ifs', 0, 0, 'ParseError', {}, ('_comprehension_ifs',
r'''+b'''),
r'''**ParseError('expecting comprehension ifs')**'''),

('parse_arguments', 0, 0, 'arguments', {}, ('arguments',
r''''''),
r'''arguments - ROOT'''),

('parse_arguments', 0, 0, 'arguments', {}, ('arguments',
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

('parse_arguments_lambda', 0, 0, 'arguments', {}, ('arguments_lambda',
r''''''),
r'''arguments - ROOT'''),

('parse_arguments_lambda', 0, 0, 'arguments', {}, ('arguments_lambda',
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

('parse_arguments_lambda', 0, 0, 'arguments', {}, ('arguments_lambda', r'''
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

('parse_arguments_lambda', 0, 0, 'SyntaxError', {}, ('arguments_lambda',
r'''a: list[str], /, b: int = 1, *c, d=100, **e'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_arg', 0, 0, 'arg', {}, ('arg',
r'''a: b'''), r'''
arg - ROOT 0,0..0,4
  .arg 'a'
  .annotation Name 'b' Load - 0,3..0,4
'''),

('parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''a: b = c'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''a, b'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''a, /'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''*, a'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''*a'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''**a'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, ('arg',
r'''a, b'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_keyword', 0, 0, 'keyword', {}, ('keyword',
r'''a=1'''), r'''
keyword - ROOT 0,0..0,3
  .arg 'a'
  .value Constant 1 - 0,2..0,3
'''),

('parse_keyword', 0, 0, 'keyword', {}, ('keyword',
r'''**a'''), r'''
keyword - ROOT 0,0..0,3
  .value Name 'a' Load - 0,2..0,3
'''),

('parse_keyword', 0, 0, 'ParseError', {}, ('keyword',
r'''1'''),
r'''**ParseError('expecting single keyword')**'''),

('parse_keyword', 0, 0, 'ParseError', {}, ('keyword',
r'''a'''),
r'''**ParseError('expecting single keyword')**'''),

('parse_keyword', 0, 0, 'ParseError', {}, ('keyword',
r'''a=1, b=2'''),
r'''**ParseError('expecting single keyword')**'''),

('parse_alias', 0, 0, 'SyntaxError', {}, ('alias',
r''''''),
r'''**SyntaxError("Expected one or more names after 'import'")**'''),

('parse_alias', 0, 0, 'alias', {}, ('alias',
r'''a'''), r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('parse_alias', 0, 0, 'alias', {}, ('alias',
r'''a.b'''), r'''
alias - ROOT 0,0..0,3
  .name 'a.b'
'''),

('parse_alias', 0, 0, 'alias', {}, ('alias',
r'''*'''), r'''
alias - ROOT 0,0..0,1
  .name '*'
'''),

('parse_alias', 0, 0, 'ParseError', {}, ('alias',
r'''a, b'''),
r'''**ParseError('expecting single name')**'''),

('parse_alias', 0, 0, 'alias', {}, ('alias',
r'''a as c'''), r'''
alias - ROOT 0,0..0,6
  .name 'a'
  .asname 'c'
'''),

('parse_alias', 0, 0, 'alias', {}, ('alias',
r'''a.b as c'''), r'''
alias - ROOT 0,0..0,8
  .name 'a.b'
  .asname 'c'
'''),

('parse_alias', 0, 0, 'SyntaxError', {}, ('alias',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_alias', 0, 0, 'ParseError', {}, ('alias',
r'''a as x, b as y'''),
r'''**ParseError('expecting single name')**'''),

('parse_alias', 0, 0, 'ParseError', {}, ('alias',
r'''a as x, a.b as y'''),
r'''**ParseError('expecting single name')**'''),

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r''''''),
r'''_aliases - ROOT 0,0..0,0'''),

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a.b'''), r'''
_aliases - ROOT 0,0..0,3
  .names[1]
   0] alias - 0,0..0,3
     .name 'a.b'
'''),

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''*'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name '*'
'''),

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a, b'''), r'''
_aliases - ROOT 0,0..0,4
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
'''),

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a as c'''), r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'c'
'''),

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
r'''a.b as c'''), r'''
_aliases - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,0..0,8
     .name 'a.b'
     .asname 'c'
'''),

('parse__aliases', 0, 0, 'SyntaxError', {}, ('_aliases',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
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

('parse__aliases', 0, 0, '_aliases', {}, ('_aliases',
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

('parse_Import_name', 0, 0, 'SyntaxError', {}, ('Import_name',
r''''''),
r'''**SyntaxError("Expected one or more names after 'import'")**'''),

('parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r'''a'''), r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r'''a.b'''), r'''
alias - ROOT 0,0..0,3
  .name 'a.b'
'''),

('parse_Import_name', 0, 0, 'SyntaxError', {}, ('Import_name',
r'''*'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_Import_name', 0, 0, 'ParseError', {}, ('Import_name',
r'''a, b'''),
r'''**ParseError('expecting single name')**'''),

('parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r'''a as c'''), r'''
alias - ROOT 0,0..0,6
  .name 'a'
  .asname 'c'
'''),

('parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r'''a.b as c'''), r'''
alias - ROOT 0,0..0,8
  .name 'a.b'
  .asname 'c'
'''),

('parse_Import_name', 0, 0, 'SyntaxError', {}, ('Import_name',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_Import_name', 0, 0, 'ParseError', {}, ('Import_name',
r'''a as x, b as y'''),
r'''**ParseError('expecting single name')**'''),

('parse_Import_name', 0, 0, 'ParseError', {}, ('Import_name',
r'''a as x, a.b as y'''),
r'''**ParseError('expecting single name')**'''),

('parse_Import_name', 0, 0, 'SyntaxError', {}, ('Import_name',
r'''(a)'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r''''''),
r'''_aliases - ROOT 0,0..0,0'''),

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a.b'''), r'''
_aliases - ROOT 0,0..0,3
  .names[1]
   0] alias - 0,0..0,3
     .name 'a.b'
'''),

('parse__Import_names', 0, 0, 'SyntaxError', {}, ('_Import_names',
r'''*'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a, b'''), r'''
_aliases - ROOT 0,0..0,4
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
'''),

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a as c'''), r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'c'
'''),

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
r'''a.b as c'''), r'''
_aliases - ROOT 0,0..0,8
  .names[1]
   0] alias - 0,0..0,8
     .name 'a.b'
     .asname 'c'
'''),

('parse__Import_names', 0, 0, 'SyntaxError', {}, ('_Import_names',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
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

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names',
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

('parse__Import_names', 0, 0, '_aliases', {}, ('_Import_names', r'''
a,
b
'''), r'''
_aliases - ROOT 0,0..1,1
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 1,0..1,1
     .name 'b'
'''),

('parse__Import_names', 0, 0, 'SyntaxError', {}, ('_Import_names',
r'''(a, b)'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r''''''),
r'''**SyntaxError("Expected one or more names after 'import'")**'''),

('parse_ImportFrom_name', 0, 0, 'alias', {}, ('ImportFrom_name',
r'''a'''), r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''a.b'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_ImportFrom_name', 0, 0, 'alias', {}, ('ImportFrom_name',
r'''*'''), r'''
alias - ROOT 0,0..0,1
  .name '*'
'''),

('parse_ImportFrom_name', 0, 0, 'ParseError', {}, ('ImportFrom_name',
r'''a, b'''),
r'''**ParseError('expecting single name')**'''),

('parse_ImportFrom_name', 0, 0, 'alias', {}, ('ImportFrom_name',
r'''a as c'''), r'''
alias - ROOT 0,0..0,6
  .name 'a'
  .asname 'c'
'''),

('parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''a.b as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_ImportFrom_name', 0, 0, 'ParseError', {}, ('ImportFrom_name',
r'''a as x, b as y'''),
r'''**ParseError('expecting single name')**'''),

('parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''a as x, a.b as y'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_ImportFrom_name', 0, 0, 'SyntaxError', {}, ('ImportFrom_name',
r'''(a)'''),
r'''**SyntaxError('ImportFrom.names cannot have explicit parentheses')**'''),

('parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r''''''),
r'''_aliases - ROOT 0,0..0,0'''),

('parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''a'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name 'a'
'''),

('parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''a.b'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''*'''), r'''
_aliases - ROOT 0,0..0,1
  .names[1]
   0] alias - 0,0..0,1
     .name '*'
'''),

('parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''a, b'''), r'''
_aliases - ROOT 0,0..0,4
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 0,3..0,4
     .name 'b'
'''),

('parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
r'''a as c'''), r'''
_aliases - ROOT 0,0..0,6
  .names[1]
   0] alias - 0,0..0,6
     .name 'a'
     .asname 'c'
'''),

('parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''a.b as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names',
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

('parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''a as x, a.b as y'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__ImportFrom_names', 0, 0, '_aliases', {}, ('_ImportFrom_names', r'''
a,
b
'''), r'''
_aliases - ROOT 0,0..1,1
  .names[2]
   0] alias - 0,0..0,1
     .name 'a'
   1] alias - 1,0..1,1
     .name 'b'
'''),

('parse__ImportFrom_names', 0, 0, 'SyntaxError', {}, ('_ImportFrom_names',
r'''(a, b)'''),
r'''**SyntaxError('ImportFrom.names cannot have explicit parentheses')**'''),

('parse_withitem', 0, 0, 'SyntaxError', {}, ('withitem',
r''''''),
r'''**SyntaxError('expecting withitem')**'''),

('parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''a'''), r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''a, b'''), r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[2]
     0] Name 'a' Load - 0,0..0,1
     1] Name 'b' Load - 0,3..0,4
    .ctx Load
'''),

('parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''(a, b)'''), r'''
withitem - ROOT 0,0..0,6
  .context_expr Tuple - 0,0..0,6
    .elts[2]
     0] Name 'a' Load - 0,1..0,2
     1] Name 'b' Load - 0,4..0,5
    .ctx Load
'''),

('parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''()'''), r'''
withitem - ROOT 0,0..0,2
  .context_expr Tuple - 0,0..0,2
    .ctx Load
'''),

('parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''a as b'''), r'''
withitem - ROOT 0,0..0,6
  .context_expr Name 'a' Load - 0,0..0,1
  .optional_vars Name 'b' Store - 0,5..0,6
'''),

('parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''(a) as (b)'''), r'''
withitem - ROOT 0,0..0,10
  .context_expr Name 'a' Load - 0,1..0,2
  .optional_vars Name 'b' Store - 0,8..0,9
'''),

('parse_withitem', 0, 0, 'ParseError', {}, ('withitem',
r'''a, b as c'''),
r'''**ParseError('expecting single withitem')**'''),

('parse_withitem', 0, 0, 'ParseError', {}, ('withitem',
r'''a as b, x as y'''),
r'''**ParseError('expecting single withitem')**'''),

('parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r'''(a)'''), r'''
withitem - ROOT 0,0..0,3
  .context_expr Name 'a' Load - 0,1..0,2
'''),

('parse_withitem', 0, 0, 'SyntaxError', {}, ('withitem',
r'''(a as b)'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_withitem', 0, 0, 'SyntaxError', {}, ('withitem',
r'''(a as b, x as y)'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r''''''),
r'''_withitems - ROOT 0,0..0,0'''),

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a'''), r'''
_withitems - ROOT 0,0..0,1
  .items[1]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
'''),

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a, b'''), r'''
_withitems - ROOT 0,0..0,4
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,4
     .context_expr Name 'b' Load - 0,3..0,4
'''),

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
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

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''()'''), r'''
_withitems - ROOT 0,0..0,2
  .items[1]
   0] withitem - 0,0..0,2
     .context_expr Tuple - 0,0..0,2
       .ctx Load
'''),

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a as b'''), r'''
_withitems - ROOT 0,0..0,6
  .items[1]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'b' Store - 0,5..0,6
'''),

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''(a) as (b)'''), r'''
_withitems - ROOT 0,0..0,10
  .items[1]
   0] withitem - 0,0..0,10
     .context_expr Name 'a' Load - 0,1..0,2
     .optional_vars Name 'b' Store - 0,8..0,9
'''),

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''a, b as c'''), r'''
_withitems - ROOT 0,0..0,9
  .items[2]
   0] withitem - 0,0..0,1
     .context_expr Name 'a' Load - 0,0..0,1
   1] withitem - 0,3..0,9
     .context_expr Name 'b' Load - 0,3..0,4
     .optional_vars Name 'c' Store - 0,8..0,9
'''),

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
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

('parse__withitems', 0, 0, '_withitems', {}, ('_withitems',
r'''(a)'''), r'''
_withitems - ROOT 0,0..0,3
  .items[1]
   0] withitem - 0,0..0,3
     .context_expr Name 'a' Load - 0,1..0,2
'''),

('parse__withitems', 0, 0, 'SyntaxError', {}, ('_withitems',
r'''(a as b)'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__withitems', 0, 0, 'SyntaxError', {}, ('_withitems',
r'''(a as b, x as y)'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse__withitems', 0, 0, 'SyntaxError', {}, ('_withitems',
r'''i for i in j'''),
r'''**SyntaxError('expecting withitem, got unparenthesized GeneratorExp')**'''),

('parse_pattern', 0, 0, 'MatchValue', {}, ('pattern',
r'''42'''), r'''
MatchValue - ROOT 0,0..0,2
  .value Constant 42 - 0,0..0,2
'''),

('parse_pattern', 0, 0, 'MatchSingleton', {}, ('pattern',
r'''None'''),
r'''MatchSingleton None - ROOT 0,0..0,4'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
r'''[a, *_]'''), r'''
MatchSequence - ROOT 0,0..0,7
  .patterns[2]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchStar - 0,4..0,6
'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
r'''[]'''),
r'''MatchSequence - ROOT 0,0..0,2'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
r'''a,'''), r'''
MatchSequence - ROOT 0,0..0,2
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern', r'''
a
,
'''), r'''
MatchSequence - ROOT 0,0..1,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('parse_pattern', 0, 0, 'MatchMapping', {}, ('pattern',
r'''{"key": _}'''), r'''
MatchMapping - ROOT 0,0..0,10
  .keys[1]
   0] Constant 'key' - 0,1..0,6
  .patterns[1]
   0] MatchAs - 0,8..0,9
'''),

('parse_pattern', 0, 0, 'MatchMapping', {}, ('pattern',
r'''{}'''),
r'''MatchMapping - ROOT 0,0..0,2'''),

('parse_pattern', 0, 0, 'MatchClass', {}, ('pattern',
r'''SomeClass()'''), r'''
MatchClass - ROOT 0,0..0,11
  .cls Name 'SomeClass' Load - 0,0..0,9
'''),

('parse_pattern', 0, 0, 'MatchClass', {}, ('pattern',
r'''SomeClass(attr=val)'''), r'''
MatchClass - ROOT 0,0..0,19
  .cls Name 'SomeClass' Load - 0,0..0,9
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 0,15..0,18
     .name 'val'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
r'''as_var'''), r'''
MatchAs - ROOT 0,0..0,6
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
r'''1 as as_var'''), r'''
MatchAs - ROOT 0,0..0,11
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchOr', {}, ('pattern',
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

('parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
r'''_'''),
r'''MatchAs - ROOT 0,0..0,1'''),

('parse_pattern', 0, 0, 'MatchStar', {}, ('pattern',
r'''*a'''), r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

('parse_pattern', 0, 0, 'SyntaxError', {}, ('pattern',
r''''''),
r'''**SyntaxError('empty pattern')**'''),

('parse_pattern', 0, 0, 'SyntaxError', {}, ('pattern', r'''
i: pass
 case 2
'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_expr', 0, 0, 'BoolOp', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'NamedExpr', {}, ('expr', r'''
a
:=
b
'''), r'''
NamedExpr - ROOT 0,0..2,1
  .target Name 'a' Store - 0,0..0,1
  .value Name 'b' Load - 2,0..2,1
'''),

('parse_expr', 0, 0, 'BinOp', {}, ('expr', r'''
a
|
b
'''), r'''
BinOp - ROOT 0,0..2,1
  .left Name 'a' Load - 0,0..0,1
  .op BitOr - 1,0..1,1
  .right Name 'b' Load - 2,0..2,1
'''),

('parse_expr', 0, 0, 'BinOp', {}, ('expr', r'''
a
**
b
'''), r'''
BinOp - ROOT 0,0..2,1
  .left Name 'a' Load - 0,0..0,1
  .op Pow - 1,0..1,2
  .right Name 'b' Load - 2,0..2,1
'''),

('parse_expr', 0, 0, 'UnaryOp', {}, ('expr', r'''
not
a
'''), r'''
UnaryOp - ROOT 0,0..1,1
  .op Not - 0,0..0,3
  .operand Name 'a' Load - 1,0..1,1
'''),

('parse_expr', 0, 0, 'UnaryOp', {}, ('expr', r'''
~
a
'''), r'''
UnaryOp - ROOT 0,0..1,1
  .op Invert - 0,0..0,1
  .operand Name 'a' Load - 1,0..1,1
'''),

('parse_expr', 0, 0, 'Lambda', {}, ('expr', r'''
lambda
:
None
'''), r'''
Lambda - ROOT 0,0..2,4
  .body Constant None - 2,0..2,4
'''),

('parse_expr', 0, 0, 'IfExp', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Dict', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Set', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'ListComp', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'SetComp', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'DictComp', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'GeneratorExp', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Await', {}, ('expr', r'''
await
a
'''), r'''
Await - ROOT 0,0..1,1
  .value Name 'a' Load - 1,0..1,1
'''),

('parse_expr', 0, 0, 'Yield', {}, ('expr',
r'''yield'''),
r'''Yield - ROOT 0,0..0,5'''),

('parse_expr', 0, 0, 'Yield', {}, ('expr', r'''
yield
a
'''), r'''
Yield - ROOT 0,0..1,1
  .value Name 'a' Load - 1,0..1,1
'''),

('parse_expr', 0, 0, 'YieldFrom', {}, ('expr', r'''
yield
from
a
'''), r'''
YieldFrom - ROOT 0,0..2,1
  .value Name 'a' Load - 2,0..2,1
'''),

('parse_expr', 0, 0, 'Compare', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Call', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
"\nf'{a}'\n"), r'''
JoinedStr - ROOT
  .values[1]
   0] FormattedValue
     .value Name 'a' Load
     .conversion -1
'''),

('parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
r'''f"{a}"'''), r'''
JoinedStr - ROOT
  .values[1]
   0] FormattedValue
     .value Name 'a' Load
     .conversion -1
'''),

('parse_expr', 0, 0, 'JoinedStr', {}, ('expr', r"""
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

('parse_expr', 0, 0, 'JoinedStr', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''...'''),
r'''Constant Ellipsis - ROOT 0,0..0,3'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''None'''),
r'''Constant None - ROOT 0,0..0,4'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''True'''),
r'''Constant True - ROOT 0,0..0,4'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''False'''),
r'''Constant False - ROOT 0,0..0,5'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''1'''),
r'''Constant 1 - ROOT 0,0..0,1'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''1.0'''),
r'''Constant 1.0 - ROOT 0,0..0,3'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''1j'''),
r'''Constant 1j - ROOT 0,0..0,2'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n'a'\n"),
r'''Constant 'a' - ROOT 0,0..0,3'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''"a"'''),
r'''Constant 'a' - ROOT 0,0..0,3'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr', r"""
'''
a
'''
"""),
r'''Constant '\na\n' - ROOT 0,0..2,3'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr', r'''
"""
a
"""
'''),
r'''Constant '\na\n' - ROOT 0,0..2,3'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
"\nb'a'\n"),
r'''Constant b'a' - ROOT 0,0..0,4'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
r'''b"a"'''),
r'''Constant b'a' - ROOT 0,0..0,4'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr', r"""
b'''
a
'''
"""),
r'''Constant b'\na\n' - ROOT 0,0..2,3'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr', r'''
b"""
a
"""
'''),
r'''Constant b'\na\n' - ROOT 0,0..2,3'''),

('parse_expr', 0, 0, 'Attribute', {}, ('expr', r'''
a
.
b
'''), r'''
Attribute - ROOT 0,0..2,1
  .value Name 'a' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),

('parse_expr', 0, 0, 'Subscript', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Starred', {}, ('expr', r'''
*
a
'''), r'''
Starred - ROOT 0,0..1,1
  .value Name 'a' Load - 1,0..1,1
  .ctx Load
'''),

('parse_expr', 0, 0, 'List', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
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

('parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
a
,
'''), r'''
Tuple - ROOT 0,0..1,1
  .elts[1]
   0] Name 'a' Load - 0,0..0,1
  .ctx Load
'''),

('parse_expr', 0, 0, 'Tuple', {}, ('expr', r'''
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

('parse_pattern', 0, 0, 'MatchValue', {}, ('pattern',
r'''42'''), r'''
MatchValue - ROOT 0,0..0,2
  .value Constant 42 - 0,0..0,2
'''),

('parse_pattern', 0, 0, 'MatchSingleton', {}, ('pattern',
r'''None'''),
r'''MatchSingleton None - ROOT 0,0..0,4'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern', r'''
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

('parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern', r'''

a
,
*
b

'''), r'''
MatchSequence - ROOT 1,0..4,1
  .patterns[2]
   0] MatchAs - 1,0..1,1
     .name 'a'
   1] MatchStar - 3,0..4,1
     .name 'b'
'''),

('parse_pattern', 0, 0, 'MatchMapping', {}, ('pattern', r'''
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

('parse_pattern', 0, 0, 'MatchClass', {}, ('pattern', r'''
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

('parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
r'''as_var'''), r'''
MatchAs - ROOT 0,0..0,6
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, ('pattern', r'''
1
as
as_var
'''), r'''
MatchAs - ROOT 0,0..2,6
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchOr', {}, ('pattern', r'''
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

('parse_expr', 0, 0, 'BoolOp', {}, ('expr',
'\n a\n or\n b\n         '), r'''
BoolOp - ROOT 1,1..3,2
  .op Or
  .values[2]
   0] Name 'a' Load - 1,1..1,2
   1] Name 'b' Load - 3,1..3,2
'''),

('parse_expr', 0, 0, 'NamedExpr', {}, ('expr',
'\n a\n :=\n b\n         '), r'''
NamedExpr - ROOT 1,1..3,2
  .target Name 'a' Store - 1,1..1,2
  .value Name 'b' Load - 3,1..3,2
'''),

('parse_expr', 0, 0, 'BinOp', {}, ('expr',
'\n a\n |\n b\n         '), r'''
BinOp - ROOT 1,1..3,2
  .left Name 'a' Load - 1,1..1,2
  .op BitOr - 2,1..2,2
  .right Name 'b' Load - 3,1..3,2
'''),

('parse_expr', 0, 0, 'BinOp', {}, ('expr',
'\n a\n **\n b\n         '), r'''
BinOp - ROOT 1,1..3,2
  .left Name 'a' Load - 1,1..1,2
  .op Pow - 2,1..2,3
  .right Name 'b' Load - 3,1..3,2
'''),

('parse_expr', 0, 0, 'UnaryOp', {}, ('expr',
'\n not\n a\n         '), r'''
UnaryOp - ROOT 1,1..2,2
  .op Not - 1,1..1,4
  .operand Name 'a' Load - 2,1..2,2
'''),

('parse_expr', 0, 0, 'UnaryOp', {}, ('expr',
'\n ~\n a\n         '), r'''
UnaryOp - ROOT 1,1..2,2
  .op Invert - 1,1..1,2
  .operand Name 'a' Load - 2,1..2,2
'''),

('parse_expr', 0, 0, 'Lambda', {}, ('expr',
'\n lambda\n :\n None\n         '), r'''
Lambda - ROOT 1,1..3,5
  .body Constant None - 3,1..3,5
'''),

('parse_expr', 0, 0, 'IfExp', {}, ('expr',
'\n a\n if\n b\n else\n c\n         '), r'''
IfExp - ROOT 1,1..5,2
  .test Name 'b' Load - 3,1..3,2
  .body Name 'a' Load - 1,1..1,2
  .orelse Name 'c' Load - 5,1..5,2
'''),

('parse_expr', 0, 0, 'Dict', {}, ('expr',
'\n {\n a\n :\n b\n }\n         '), r'''
Dict - ROOT 1,1..5,2
  .keys[1]
   0] Name 'a' Load - 2,1..2,2
  .values[1]
   0] Name 'b' Load - 4,1..4,2
'''),

('parse_expr', 0, 0, 'Set', {}, ('expr',
'\n {\n a\n ,\n b\n }\n         '), r'''
Set - ROOT 1,1..5,2
  .elts[2]
   0] Name 'a' Load - 2,1..2,2
   1] Name 'b' Load - 4,1..4,2
'''),

('parse_expr', 0, 0, 'ListComp', {}, ('expr',
'\n [\n a\n for\n a\n in\n b\n ]\n         '), r'''
ListComp - ROOT 1,1..7,2
  .elt Name 'a' Load - 2,1..2,2
  .generators[1]
   0] comprehension - 3,1..6,2
     .target Name 'a' Store - 4,1..4,2
     .iter Name 'b' Load - 6,1..6,2
     .is_async 0
'''),

('parse_expr', 0, 0, 'SetComp', {}, ('expr',
'\n {\n a\n for\n a\n in\n b\n }\n         '), r'''
SetComp - ROOT 1,1..7,2
  .elt Name 'a' Load - 2,1..2,2
  .generators[1]
   0] comprehension - 3,1..6,2
     .target Name 'a' Store - 4,1..4,2
     .iter Name 'b' Load - 6,1..6,2
     .is_async 0
'''),

('parse_expr', 0, 0, 'DictComp', {}, ('expr',
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

('parse_expr', 0, 0, 'GeneratorExp', {}, ('expr',
'\n (\n a\n for\n a\n in\n b\n )\n         '), r'''
GeneratorExp - ROOT 1,1..7,2
  .elt Name 'a' Load - 2,1..2,2
  .generators[1]
   0] comprehension - 3,1..6,2
     .target Name 'a' Store - 4,1..4,2
     .iter Name 'b' Load - 6,1..6,2
     .is_async 0
'''),

('parse_expr', 0, 0, 'Await', {}, ('expr',
'\n await\n a\n         '), r'''
Await - ROOT 1,1..2,2
  .value Name 'a' Load - 2,1..2,2
'''),

('parse_expr', 0, 0, 'Yield', {}, ('expr',
'\n yield\n         '),
r'''Yield - ROOT 1,1..1,6'''),

('parse_expr', 0, 0, 'Yield', {}, ('expr',
'\n yield\n a\n         '), r'''
Yield - ROOT 1,1..2,2
  .value Name 'a' Load - 2,1..2,2
'''),

('parse_expr', 0, 0, 'YieldFrom', {}, ('expr',
'\n yield\n from\n a\n         '), r'''
YieldFrom - ROOT 1,1..3,2
  .value Name 'a' Load - 3,1..3,2
'''),

('parse_expr', 0, 0, 'Compare', {}, ('expr',
'\n a\n <\n b\n         '), r'''
Compare - ROOT 1,1..3,2
  .left Name 'a' Load - 1,1..1,2
  .ops[1]
   0] Lt - 2,1..2,2
  .comparators[1]
   0] Name 'b' Load - 3,1..3,2
'''),

('parse_expr', 0, 0, 'Call', {}, ('expr',
'\n f\n (\n a\n )\n         '), r'''
Call - ROOT 1,1..4,2
  .func Name 'f' Load - 1,1..1,2
  .args[1]
   0] Name 'a' Load - 3,1..3,2
'''),

('parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
"\n f'{a}'\n "), r'''
JoinedStr - ROOT
  .values[1]
   0] FormattedValue
     .value Name 'a' Load
     .conversion -1
'''),

('parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
'\n f"{a}"\n         '), r'''
JoinedStr - ROOT
  .values[1]
   0] FormattedValue
     .value Name 'a' Load
     .conversion -1
'''),

('parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
"\n f'''\n {\n a\n }\n         '''\n "), r'''
JoinedStr - ROOT
  .values[3]
   0] Constant '\n '
   1] FormattedValue
     .value Name 'a' Load
     .conversion -1
   2] Constant '\n         '
'''),

('parse_expr', 0, 0, 'JoinedStr', {}, ('expr',
'\n f"""\n {\n a\n }\n """\n         '), r'''
JoinedStr - ROOT
  .values[3]
   0] Constant '\n '
   1] FormattedValue
     .value Name 'a' Load
     .conversion -1
   2] Constant '\n '
'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n ...\n         '),
r'''Constant Ellipsis - ROOT 1,1..1,4'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n None\n         '),
r'''Constant None - ROOT 1,1..1,5'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n True\n         '),
r'''Constant True - ROOT 1,1..1,5'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n False\n         '),
r'''Constant False - ROOT 1,1..1,6'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n 1\n         '),
r'''Constant 1 - ROOT 1,1..1,2'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n 1.0\n         '),
r'''Constant 1.0 - ROOT 1,1..1,4'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n 1j\n         '),
r'''Constant 1j - ROOT 1,1..1,3'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n         'a'\n "),
r'''Constant 'a' - ROOT 1,9..1,12'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n "a"\n         '),
r'''Constant 'a' - ROOT 1,1..1,4'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n         '''\n a\n         '''\n "),
r'''Constant '\n a\n         ' - ROOT 1,9..3,12'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n """\n a\n """\n         '),
r'''Constant '\n a\n ' - ROOT 1,1..3,4'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n b'a'\n "),
r'''Constant b'a' - ROOT 1,1..1,5'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n b"a"\n         '),
r'''Constant b'a' - ROOT 1,1..1,5'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
"\n b'''\n a\n         '''\n "),
r'''Constant b'\n a\n         ' - ROOT 1,1..3,12'''),

('parse_expr', 0, 0, 'Constant', {}, ('expr',
'\n b"""\n a\n """\n         '),
r'''Constant b'\n a\n ' - ROOT 1,1..3,4'''),

('parse_expr', 0, 0, 'Attribute', {}, ('expr',
'\n a\n .\n b\n         '), r'''
Attribute - ROOT 1,1..3,2
  .value Name 'a' Load - 1,1..1,2
  .attr 'b'
  .ctx Load
'''),

('parse_expr', 0, 0, 'Subscript', {}, ('expr',
'\n a\n [\n b\n ]\n         '), r'''
Subscript - ROOT 1,1..4,2
  .value Name 'a' Load - 1,1..1,2
  .slice Name 'b' Load - 3,1..3,2
  .ctx Load
'''),

('parse_expr', 0, 0, 'Starred', {}, ('expr',
'\n *\n a\n         '), r'''
Starred - ROOT 1,1..2,2
  .value Name 'a' Load - 2,1..2,2
  .ctx Load
'''),

('parse_expr', 0, 0, 'List', {}, ('expr',
'\n [\n a\n ,\n b\n ]\n         '), r'''
List - ROOT 1,1..5,2
  .elts[2]
   0] Name 'a' Load - 2,1..2,2
   1] Name 'b' Load - 4,1..4,2
  .ctx Load
'''),

('parse_expr', 0, 0, 'Tuple', {}, ('expr',
'\n (\n a\n ,\n b\n )\n         '), r'''
Tuple - ROOT 1,1..5,2
  .elts[2]
   0] Name 'a' Load - 2,1..2,2
   1] Name 'b' Load - 4,1..4,2
  .ctx Load
'''),

('parse_expr', 0, 0, 'Tuple', {}, ('expr',
'\n a\n ,\n         '), r'''
Tuple - ROOT 1,1..2,2
  .elts[1]
   0] Name 'a' Load - 1,1..1,2
  .ctx Load
'''),

('parse_expr', 0, 0, 'Tuple', {}, ('expr',
'\n a\n ,\n b\n         '), r'''
Tuple - ROOT 1,1..3,2
  .elts[2]
   0] Name 'a' Load - 1,1..1,2
   1] Name 'b' Load - 3,1..3,2
  .ctx Load
'''),

('parse_pattern', 0, 0, 'MatchValue', {}, ('pattern',
'\n 42\n         '), r'''
MatchValue - ROOT 1,1..1,3
  .value Constant 42 - 1,1..1,3
'''),

('parse_pattern', 0, 0, 'MatchSingleton', {}, ('pattern',
'\n None\n         '),
r'''MatchSingleton None - ROOT 1,1..1,5'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
'\n [\n a\n ,\n *\n b\n ]\n         '), r'''
MatchSequence - ROOT 1,1..6,2
  .patterns[2]
   0] MatchAs - 2,1..2,2
     .name 'a'
   1] MatchStar - 4,1..5,2
     .name 'b'
'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, ('pattern',
'\n \n a\n ,\n *\n b\n \n         '), r'''
MatchSequence - ROOT 2,1..5,2
  .patterns[2]
   0] MatchAs - 2,1..2,2
     .name 'a'
   1] MatchStar - 4,1..5,2
     .name 'b'
'''),

('parse_pattern', 0, 0, 'MatchMapping', {}, ('pattern',
'\n {\n "key"\n :\n _\n }\n         '), r'''
MatchMapping - ROOT 1,1..5,2
  .keys[1]
   0] Constant 'key' - 2,1..2,6
  .patterns[1]
   0] MatchAs - 4,1..4,2
'''),

('parse_pattern', 0, 0, 'MatchClass', {}, ('pattern',
'\n SomeClass\n (\n attr\n =\n val\n )\n         '), r'''
MatchClass - ROOT 1,1..6,2
  .cls Name 'SomeClass' Load - 1,1..1,10
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 5,1..5,4
     .name 'val'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
'\n as_var\n         '), r'''
MatchAs - ROOT 1,1..1,7
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, ('pattern',
'\n 1\n as\n as_var\n         '), r'''
MatchAs - ROOT 1,1..3,7
  .pattern MatchValue - 1,1..1,2
    .value Constant 1 - 1,1..1,2
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchOr', {}, ('pattern',
'\n 1\n |\n 2\n         '), r'''
MatchOr - ROOT 1,1..3,2
  .patterns[2]
   0] MatchValue - 1,1..1,2
     .value Constant 1 - 1,1..1,2
   1] MatchValue - 3,1..3,2
     .value Constant 2 - 3,1..3,2
'''),

('parse_Module', 0, 0, 'Module', {}, (mod,
r'''j'''), r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('parse_Module', 0, 0, 'Module', {}, (Module,
r'''j'''), r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('parse_Expression', 0, 0, 'Expression', {}, (Expression,
r'''None'''), r'''
Expression - ROOT 0,0..0,4
  .body Constant None - 0,0..0,4
'''),

('parse_Interactive', 0, 0, 'Interactive', {}, (Interactive,
r'''j'''), r'''
Interactive - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'j' Load - 0,0..0,1
'''),

('parse_stmt', 0, 0, 'AnnAssign', {}, (stmt,
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

('parse_stmt', 0, 0, 'Expr', {}, (stmt,
r'''j'''), r'''
Expr - ROOT 0,0..0,1
  .value Name 'j' Load - 0,0..0,1
'''),

('parse_stmt', 0, 0, 'ParseError', {}, (stmt, r'''
i: int = 1
j
'''),
r'''**ParseError('expecting single stmt')**'''),

('parse_stmt', 0, 0, 'SyntaxError', {}, (stmt,
r'''except: pass'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_stmt', 0, 0, 'AnnAssign', {}, (AnnAssign,
r'''i: int = 1'''), r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'i' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Constant 1 - 0,9..0,10
  .simple 1
'''),

('parse_stmt', 0, 0, 'Expr', {}, (Expr,
r'''j'''), r'''
Expr - ROOT 0,0..0,1
  .value Name 'j' Load - 0,0..0,1
'''),

('parse_ExceptHandler', 0, 0, 'ExceptHandler', {}, (ExceptHandler,
r'''except: pass'''), r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
'''),

('parse_ExceptHandler', 0, 0, 'ParseError', {}, (ExceptHandler, r'''
except Exception: pass
except: pass
'''),
r'''**ParseError('expecting single ExceptHandler')**'''),

('parse_ExceptHandler', 0, 0, 'SyntaxError', {}, (ExceptHandler,
r'''i: int = 1'''),
r'''**SyntaxError("expected 'except' or 'finally' block")**'''),

('parse_match_case', 0, 0, 'match_case', {}, (match_case,
r'''case None: pass'''), r'''
match_case - ROOT 0,0..0,15
  .pattern MatchSingleton None - 0,5..0,9
  .body[1]
   0] Pass - 0,11..0,15
'''),

('parse_match_case', 0, 0, 'ParseError', {}, (match_case, r'''
case None: pass
case 1: pass
'''),
r'''**ParseError('expecting single match_case')**'''),

('parse_match_case', 0, 0, 'SyntaxError', {}, (match_case,
r'''i: int = 1'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_expr', 0, 0, 'Name', {}, (expr,
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_expr', 0, 0, 'Starred', {}, (expr,
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

('parse_expr', 0, 0, 'Starred', {}, (expr, r'''
*
s
'''), r'''
Starred - ROOT 0,0..1,1
  .value Name 's' Load - 1,0..1,1
  .ctx Load
'''),

('parse_expr', 0, 0, 'Tuple', {}, (expr, r'''
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

('parse_expr', 0, 0, 'Tuple', {}, (expr, r'''
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

('parse_expr', 0, 0, 'SyntaxError', {}, (expr,
r'''*not a'''),
r'''**SyntaxError('invalid expression (standard)')**'''),

('parse_expr', 0, 0, 'SyntaxError', {}, (expr,
r'''a:b'''),
r'''**SyntaxError('invalid expression (standard)')**'''),

('parse_expr', 0, 0, 'SyntaxError', {}, (expr,
r'''a:b:c'''),
r'''**SyntaxError('invalid expression (standard)')**'''),

('parse_expr', 0, 0, 'Name', {}, (Name,
r'''j'''),
r'''Name 'j' Load - ROOT 0,0..0,1'''),

('parse_expr', 0, 0, 'Starred', {}, (Starred,
r'''*s'''), r'''
Starred - ROOT 0,0..0,2
  .value Name 's' Load - 0,1..0,2
  .ctx Load
'''),

('parse_expr_arglike', 0, 0, 'Starred', {}, (Starred,
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('parse_expr_slice', 0, 0, 'Slice', {}, (Slice,
r'''a:b'''), r'''
Slice - ROOT 0,0..0,3
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
'''),

('parse_boolop', 0, 0, 'And', {}, (boolop,
r'''and'''),
r'''And - ROOT 0,0..0,3'''),

('parse_boolop', 0, 0, 'SyntaxError', {}, (boolop,
r'''*'''),
r'''**SyntaxError("expecting boolop, got '*'")**'''),

('parse_operator', 0, 0, 'Mult', {}, (operator,
r'''*'''),
r'''Mult - ROOT 0,0..0,1'''),

('parse_operator', 0, 0, 'SyntaxError', {}, (operator,
r'''*='''),
r'''**SyntaxError("expecting operator, got '*='")**'''),

('parse_operator', 0, 0, 'SyntaxError', {}, (operator,
r'''and'''),
r'''**SyntaxError("expecting operator, got 'and'")**'''),

('parse_unaryop', 0, 0, 'UAdd', {}, (unaryop,
r'''+'''),
r'''UAdd - ROOT 0,0..0,1'''),

('parse_unaryop', 0, 0, 'SyntaxError', {}, (unaryop,
r'''and'''),
r'''**SyntaxError("expecting unaryop, got 'and'")**'''),

('parse_cmpop', 0, 0, 'GtE', {}, (cmpop,
r'''>='''),
r'''GtE - ROOT 0,0..0,2'''),

('parse_cmpop', 0, 0, 'IsNot', {}, (cmpop, r'''
is
not
'''),
r'''IsNot - ROOT 0,0..1,3'''),

('parse_cmpop', 0, 0, 'SyntaxError', {}, (cmpop,
r'''>= a >='''),
r'''**SyntaxError("unexpected code after cmpop, 'a'")**'''),

('parse_cmpop', 0, 0, 'SyntaxError', {}, (cmpop,
r'''and'''),
r'''**SyntaxError("expecting cmpop, got 'and'")**'''),

('parse_comprehension', 0, 0, 'comprehension', {}, (comprehension,
r'''for u in v'''), r'''
comprehension - ROOT 0,0..0,10
  .target Name 'u' Store - 0,4..0,5
  .iter Name 'v' Load - 0,9..0,10
  .is_async 0
'''),

('parse_comprehension', 0, 0, 'comprehension', {}, (comprehension,
r'''for u in v if w'''), r'''
comprehension - ROOT 0,0..0,15
  .target Name 'u' Store - 0,4..0,5
  .iter Name 'v' Load - 0,9..0,10
  .ifs[1]
   0] Name 'w' Load - 0,14..0,15
  .is_async 0
'''),

('parse_comprehension', 0, 0, 'ParseError', {}, (comprehension,
r'''()'''),
r'''**ParseError('expecting comprehension')**'''),

('parse_arguments', 0, 0, 'arguments', {}, (arguments,
r''''''),
r'''arguments - ROOT'''),

('parse_arguments', 0, 0, 'arguments', {}, (arguments,
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

('parse_arguments_lambda', 0, 0, 'arguments', {}, (arguments,
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

('parse_arg', 0, 0, 'arg', {}, (arg,
r'''a: b'''), r'''
arg - ROOT 0,0..0,4
  .arg 'a'
  .annotation Name 'b' Load - 0,3..0,4
'''),

('parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''a: b = c'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''a, b'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''a, /'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''*, a'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''*a'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_arg', 0, 0, 'ParseError', {}, (arg,
r'''**a'''),
r'''**ParseError('expecting single argument without default')**'''),

('parse_keyword', 0, 0, 'keyword', {}, (keyword,
r'''a=1'''), r'''
keyword - ROOT 0,0..0,3
  .arg 'a'
  .value Constant 1 - 0,2..0,3
'''),

('parse_keyword', 0, 0, 'keyword', {}, (keyword,
r'''**a'''), r'''
keyword - ROOT 0,0..0,3
  .value Name 'a' Load - 0,2..0,3
'''),

('parse_keyword', 0, 0, 'ParseError', {}, (keyword,
r'''1'''),
r'''**ParseError('expecting single keyword')**'''),

('parse_keyword', 0, 0, 'ParseError', {}, (keyword,
r'''a'''),
r'''**ParseError('expecting single keyword')**'''),

('parse_keyword', 0, 0, 'ParseError', {}, (keyword,
r'''a=1, b=2'''),
r'''**ParseError('expecting single keyword')**'''),

('parse_alias', 0, 0, 'alias', {}, (alias,
r'''a'''), r'''
alias - ROOT 0,0..0,1
  .name 'a'
'''),

('parse_alias', 0, 0, 'alias', {}, (alias,
r'''a.b'''), r'''
alias - ROOT 0,0..0,3
  .name 'a.b'
'''),

('parse_alias', 0, 0, 'alias', {}, (alias,
r'''*'''), r'''
alias - ROOT 0,0..0,1
  .name '*'
'''),

('parse_alias', 0, 0, 'ParseError', {}, (alias,
r'''a, b'''),
r'''**ParseError('expecting single name')**'''),

('parse_alias', 0, 0, 'alias', {}, (alias,
r'''a as c'''), r'''
alias - ROOT 0,0..0,6
  .name 'a'
  .asname 'c'
'''),

('parse_alias', 0, 0, 'alias', {}, (alias,
r'''a.b as c'''), r'''
alias - ROOT 0,0..0,8
  .name 'a.b'
  .asname 'c'
'''),

('parse_alias', 0, 0, 'SyntaxError', {}, (alias,
r'''* as c'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''a'''), r'''
withitem - ROOT 0,0..0,1
  .context_expr Name 'a' Load - 0,0..0,1
'''),

('parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''a, b'''), r'''
withitem - ROOT 0,0..0,4
  .context_expr Tuple - 0,0..0,4
    .elts[2]
     0] Name 'a' Load - 0,0..0,1
     1] Name 'b' Load - 0,3..0,4
    .ctx Load
'''),

('parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''(a, b)'''), r'''
withitem - ROOT 0,0..0,6
  .context_expr Tuple - 0,0..0,6
    .elts[2]
     0] Name 'a' Load - 0,1..0,2
     1] Name 'b' Load - 0,4..0,5
    .ctx Load
'''),

('parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''a as b'''), r'''
withitem - ROOT 0,0..0,6
  .context_expr Name 'a' Load - 0,0..0,1
  .optional_vars Name 'b' Store - 0,5..0,6
'''),

('parse_withitem', 0, 0, 'ParseError', {}, (withitem,
r'''a as b, x as y'''),
r'''**ParseError('expecting single withitem')**'''),

('parse_withitem', 0, 0, 'withitem', {}, (withitem,
r'''(a)'''), r'''
withitem - ROOT 0,0..0,3
  .context_expr Name 'a' Load - 0,1..0,2
'''),

('parse_withitem', 0, 0, 'SyntaxError', {}, (withitem,
r'''(a as b)'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_withitem', 0, 0, 'SyntaxError', {}, (withitem,
r'''(a as b, x as y)'''),
r'''**SyntaxError('invalid syntax')**'''),

('parse_pattern', 0, 0, 'MatchValue', {}, (pattern,
r'''42'''), r'''
MatchValue - ROOT 0,0..0,2
  .value Constant 42 - 0,0..0,2
'''),

('parse_pattern', 0, 0, 'MatchSingleton', {}, (pattern,
r'''None'''),
r'''MatchSingleton None - ROOT 0,0..0,4'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, (pattern,
r'''[a, *_]'''), r'''
MatchSequence - ROOT 0,0..0,7
  .patterns[2]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchStar - 0,4..0,6
'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, (pattern,
r'''[]'''),
r'''MatchSequence - ROOT 0,0..0,2'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, (pattern,
r'''a,'''), r'''
MatchSequence - ROOT 0,0..0,2
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, (pattern, r'''
a
,
'''), r'''
MatchSequence - ROOT 0,0..1,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('parse_pattern', 0, 0, 'MatchMapping', {}, (pattern,
r'''{"key": _}'''), r'''
MatchMapping - ROOT 0,0..0,10
  .keys[1]
   0] Constant 'key' - 0,1..0,6
  .patterns[1]
   0] MatchAs - 0,8..0,9
'''),

('parse_pattern', 0, 0, 'MatchMapping', {}, (pattern,
r'''{}'''),
r'''MatchMapping - ROOT 0,0..0,2'''),

('parse_pattern', 0, 0, 'MatchClass', {}, (pattern,
r'''SomeClass()'''), r'''
MatchClass - ROOT 0,0..0,11
  .cls Name 'SomeClass' Load - 0,0..0,9
'''),

('parse_pattern', 0, 0, 'MatchClass', {}, (pattern,
r'''SomeClass(attr=val)'''), r'''
MatchClass - ROOT 0,0..0,19
  .cls Name 'SomeClass' Load - 0,0..0,9
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 0,15..0,18
     .name 'val'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, (pattern,
r'''as_var'''), r'''
MatchAs - ROOT 0,0..0,6
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, (pattern,
r'''1 as as_var'''), r'''
MatchAs - ROOT 0,0..0,11
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchOr', {}, (pattern,
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

('parse_pattern', 0, 0, 'MatchAs', {}, (pattern,
r'''_'''),
r'''MatchAs - ROOT 0,0..0,1'''),

('parse_pattern', 0, 0, 'MatchStar', {}, (pattern,
r'''*a'''), r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

('parse_pattern', 0, 0, 'SyntaxError', {}, (pattern,
r''''''),
r'''**SyntaxError('empty pattern')**'''),

('parse_pattern', 0, 0, 'MatchValue', {}, (MatchValue,
r'''42'''), r'''
MatchValue - ROOT 0,0..0,2
  .value Constant 42 - 0,0..0,2
'''),

('parse_pattern', 0, 0, 'MatchSingleton', {}, (MatchSingleton,
r'''None'''),
r'''MatchSingleton None - ROOT 0,0..0,4'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, (MatchSequence,
r'''[a, *_]'''), r'''
MatchSequence - ROOT 0,0..0,7
  .patterns[2]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchStar - 0,4..0,6
'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, (MatchSequence,
r'''[]'''),
r'''MatchSequence - ROOT 0,0..0,2'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, (MatchSequence,
r'''a,'''), r'''
MatchSequence - ROOT 0,0..0,2
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('parse_pattern', 0, 0, 'MatchSequence', {}, (MatchSequence, r'''
a
,
'''), r'''
MatchSequence - ROOT 0,0..1,1
  .patterns[1]
   0] MatchAs - 0,0..0,1
     .name 'a'
'''),

('parse_pattern', 0, 0, 'MatchMapping', {}, (MatchMapping,
r'''{"key": _}'''), r'''
MatchMapping - ROOT 0,0..0,10
  .keys[1]
   0] Constant 'key' - 0,1..0,6
  .patterns[1]
   0] MatchAs - 0,8..0,9
'''),

('parse_pattern', 0, 0, 'MatchMapping', {}, (MatchMapping,
r'''{}'''),
r'''MatchMapping - ROOT 0,0..0,2'''),

('parse_pattern', 0, 0, 'MatchClass', {}, (MatchClass,
r'''SomeClass()'''), r'''
MatchClass - ROOT 0,0..0,11
  .cls Name 'SomeClass' Load - 0,0..0,9
'''),

('parse_pattern', 0, 0, 'MatchClass', {}, (MatchClass,
r'''SomeClass(attr=val)'''), r'''
MatchClass - ROOT 0,0..0,19
  .cls Name 'SomeClass' Load - 0,0..0,9
  .kwd_attrs[1]
   0] 'attr'
  .kwd_patterns[1]
   0] MatchAs - 0,15..0,18
     .name 'val'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, (MatchAs,
r'''as_var'''), r'''
MatchAs - ROOT 0,0..0,6
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchAs', {}, (MatchAs,
r'''1 as as_var'''), r'''
MatchAs - ROOT 0,0..0,11
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'as_var'
'''),

('parse_pattern', 0, 0, 'MatchOr', {}, (MatchOr,
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

('parse_pattern', 0, 0, 'MatchAs', {}, (MatchAs,
r'''_'''),
r'''MatchAs - ROOT 0,0..0,1'''),

('parse_pattern', 0, 0, 'MatchStar', {}, (MatchStar,
r'''*a'''), r'''
MatchStar - ROOT 0,0..0,2
  .name 'a'
'''),

('parse_expr', 0, 0, 'Tuple', {}, ('expr',
r''' *a,  # tail'''), r'''
Tuple - ROOT 0,1..0,4
  .elts[1]
   0] Starred - 0,1..0,3
     .value Name 'a' Load - 0,2..0,3
     .ctx Load
  .ctx Load
'''),

('parse_expr_arglike', 0, 0, 'Starred', {}, ('expr_arglike',
r''' *not a  # tail'''), r'''
Starred - ROOT 0,1..0,7
  .value UnaryOp - 0,2..0,7
    .op Not - 0,2..0,5
    .operand Name 'a' Load - 0,6..0,7
  .ctx Load
'''),

('parse_expr_slice', 0, 0, 'Slice', {}, ('expr_slice',
r''' a:b:c  # tail'''), r'''
Slice - ROOT 0,1..0,6
  .lower Name 'a' Load - 0,1..0,2
  .upper Name 'b' Load - 0,3..0,4
  .step Name 'c' Load - 0,5..0,6
'''),

('parse_expr_slice', 0, 0, 'Yield', {}, ('expr_slice',
r''' yield  # tail'''),
r'''Yield - ROOT 0,1..0,6'''),

('parse_boolop', 0, 0, 'And', {}, ('boolop',
r''' and  # tail'''),
r'''And - ROOT 0,1..0,4'''),

('parse_operator', 0, 0, 'RShift', {}, ('operator',
r''' >>  # tail'''),
r'''RShift - ROOT 0,1..0,3'''),

('parse_unaryop', 0, 0, 'Invert', {}, ('unaryop',
r''' ~  # tail'''),
r'''Invert - ROOT 0,1..0,2'''),

('parse_cmpop', 0, 0, 'GtE', {}, ('cmpop',
r''' >=  # tail'''),
r'''GtE - ROOT 0,1..0,3'''),

('parse_comprehension', 0, 0, 'comprehension', {}, ('comprehension',
r''' for i in j  # tail'''), r'''
comprehension - ROOT 0,1..0,11
  .target Name 'i' Store - 0,5..0,6
  .iter Name 'j' Load - 0,10..0,11
  .is_async 0
'''),

('parse_arguments', 0, 0, 'arguments', {}, ('arguments',
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

('parse_arguments_lambda', 0, 0, 'arguments', {}, ('arguments_lambda',
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

('parse_arg', 0, 0, 'arg', {}, ('arg',
r''' a: b  # tail'''), r'''
arg - ROOT 0,1..0,5
  .arg 'a'
  .annotation Name 'b' Load - 0,4..0,5
'''),

('parse_keyword', 0, 0, 'keyword', {}, ('keyword',
r''' a=1  # tail'''), r'''
keyword - ROOT 0,1..0,4
  .arg 'a'
  .value Constant 1 - 0,3..0,4
'''),

('parse_Import_name', 0, 0, 'alias', {}, ('Import_name',
r''' a.b  # tail'''), r'''
alias - ROOT 0,1..0,4
  .name 'a.b'
'''),

('parse_ImportFrom_name', 0, 0, 'alias', {}, ('ImportFrom_name',
r''' *  # tail'''), r'''
alias - ROOT 0,1..0,2
  .name '*'
'''),

('parse_withitem', 0, 0, 'withitem', {}, ('withitem',
r''' a as b,  # tail'''), r'''
withitem - ROOT 0,1..0,7
  .context_expr Name 'a' Load - 0,1..0,2
  .optional_vars Name 'b' Store - 0,6..0,7
'''),

('parse_pattern', 0, 0, 'MatchOr', {}, ('pattern',
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

('parse_pattern', 0, 0, 'MatchStar', {}, ('pattern',
r''' *a  # tail'''), r'''
MatchStar - ROOT 0,1..0,3
  .name 'a'
'''),

('parse_ExceptHandler', 0, 0, 'ExceptHandler', {'_ver': 11}, ('ExceptHandler',
r'''except* Exception: pass'''), r'''
ExceptHandler - ROOT 0,0..0,23
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
   0] Pass - 0,19..0,23
'''),

('parse_expr_all', 0, 0, 'Starred', {'_ver': 11}, ('expr_all',
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('parse_expr_slice', 0, 0, 'Tuple', {'_ver': 11}, ('expr_slice',
r'''*s'''), r'''
Tuple - ROOT 0,0..0,2
  .elts[1]
   0] Starred - 0,0..0,2
     .value Name 's' Load - 0,1..0,2
     .ctx Load
  .ctx Load
'''),

('parse_expr_slice', 0, 0, 'Tuple', {'_ver': 11}, ('expr_slice',
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

('parse_Tuple_elt', 0, 0, 'Starred', {'_ver': 11}, ('Tuple_elt',
r'''*not a'''), r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

('parse_Tuple_elt', 0, 0, 'SyntaxError', {'_ver': 11}, ('Tuple_elt',
r'''*not a, *b or c'''),
r'''**SyntaxError('invalid expression (standard)')**'''),

('parse_ExceptHandler', 0, 0, 'ExceptHandler', {'_ver': 11}, (ExceptHandler,
r'''except* Exception: pass'''), r'''
ExceptHandler - ROOT 0,0..0,23
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
   0] Pass - 0,19..0,23
'''),

('parse_arg', 0, 0, 'arg', {'_ver': 11}, ('arg',
r''' a: *b  # tail'''), r'''
arg - ROOT 0,1..0,6
  .arg 'a'
  .annotation Starred - 0,4..0,6
    .value Name 'b' Load - 0,5..0,6
    .ctx Load
'''),

('parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('all',
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

('parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('all',
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

('parse_type_param', 0, 0, 'TypeVar', {'_ver': 12}, ('type_param',
r'''a: int'''), r'''
TypeVar - ROOT 0,0..0,6
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
'''),

('parse_type_param', 0, 0, 'ParamSpec', {'_ver': 12}, ('type_param',
r'''**a'''), r'''
ParamSpec - ROOT 0,0..0,3
  .name 'a'
'''),

('parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 12}, ('type_param',
r'''*a'''), r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

('parse_type_param', 0, 0, 'ParseError', {'_ver': 12}, ('type_param',
r'''a: int,'''),
r'''**ParseError('expecting single type_param, has trailing comma')**'''),

('parse_type_param', 0, 0, 'ParseError', {'_ver': 12}, ('type_param',
r'''T, U'''),
r'''**ParseError('expecting single type_param')**'''),

('parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r''''''),
r'''_type_params - ROOT 0,0..0,0'''),

('parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r'''a: int'''), r'''
_type_params - ROOT 0,0..0,6
  .type_params[1]
   0] TypeVar - 0,0..0,6
     .name 'a'
     .bound Name 'int' Load - 0,3..0,6
'''),

('parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
r'''a: int,'''), r'''
_type_params - ROOT 0,0..0,7
  .type_params[1]
   0] TypeVar - 0,0..0,6
     .name 'a'
     .bound Name 'int' Load - 0,3..0,6
'''),

('parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
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

('parse_type_param', 0, 0, 'TypeVar', {'_ver': 12}, (type_param,
r'''a: int'''), r'''
TypeVar - ROOT 0,0..0,6
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
'''),

('parse_type_param', 0, 0, 'TypeVar', {'_ver': 12}, (TypeVar,
r'''a: int'''), r'''
TypeVar - ROOT 0,0..0,6
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
'''),

('parse_type_param', 0, 0, 'ParamSpec', {'_ver': 12}, (type_param,
r'''**a'''), r'''
ParamSpec - ROOT 0,0..0,3
  .name 'a'
'''),

('parse_type_param', 0, 0, 'ParamSpec', {'_ver': 12}, (ParamSpec,
r'''**a'''), r'''
ParamSpec - ROOT 0,0..0,3
  .name 'a'
'''),

('parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 12}, (type_param,
r'''*a'''), r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

('parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 12}, (TypeVarTuple,
r'''*a'''), r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'a'
'''),

('parse_type_param', 0, 0, 'TypeVar', {'_ver': 12}, ('type_param',
r''' a: int  # tail'''), r'''
TypeVar - ROOT 0,1..0,7
  .name 'a'
  .bound Name 'int' Load - 0,4..0,7
'''),

('parse__type_params', 0, 0, '_type_params', {'_ver': 12}, ('_type_params',
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

('parse_type_param', 0, 0, 'ParamSpec', {'_ver': 13}, ('all',
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

('parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 13}, ('all',
r'''*a = (int, str)'''), r'''
TypeVarTuple - ROOT 0,0..0,15
  .name 'a'
  .default_value Tuple - 0,5..0,15
    .elts[2]
     0] Name 'int' Load - 0,6..0,9
     1] Name 'str' Load - 0,11..0,14
    .ctx Load
'''),

('parse__type_params', 0, 0, '_type_params', {'_ver': 13}, ('all',
r'''**a = {T: int, U: str},'''), r'''
_type_params - ROOT 0,0..0,23
  .type_params[1]
   0] ParamSpec - 0,0..0,22
     .name 'a'
     .default_value Dict - 0,6..0,22
       .keys[2]
        0] Name 'T' Load - 0,7..0,8
        1] Name 'U' Load - 0,15..0,16
       .values[2]
        0] Name 'int' Load - 0,10..0,13
        1] Name 'str' Load - 0,18..0,21
'''),

('parse__type_params', 0, 0, '_type_params', {'_ver': 13}, ('all',
r'''**a = {T: int, U: str}, *b'''), r'''
_type_params - ROOT 0,0..0,26
  .type_params[2]
   0] ParamSpec - 0,0..0,22
     .name 'a'
     .default_value Dict - 0,6..0,22
       .keys[2]
        0] Name 'T' Load - 0,7..0,8
        1] Name 'U' Load - 0,15..0,16
       .values[2]
        0] Name 'int' Load - 0,10..0,13
        1] Name 'str' Load - 0,18..0,21
   1] TypeVarTuple - 0,24..0,26
     .name 'b'
'''),

('parse_type_param', 0, 0, 'TypeVar', {'_ver': 13}, ('type_param',
r'''a: int = int'''), r'''
TypeVar - ROOT 0,0..0,12
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
  .default_value Name 'int' Load - 0,9..0,12
'''),

('parse_type_param', 0, 0, 'ParamSpec', {'_ver': 13}, ('type_param',
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

('parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 13}, ('type_param',
r'''*a = (int, str)'''), r'''
TypeVarTuple - ROOT 0,0..0,15
  .name 'a'
  .default_value Tuple - 0,5..0,15
    .elts[2]
     0] Name 'int' Load - 0,6..0,9
     1] Name 'str' Load - 0,11..0,14
    .ctx Load
'''),

('parse_type_param', 0, 0, 'TypeVar', {'_ver': 13}, (type_param,
r'''a: int = int'''), r'''
TypeVar - ROOT 0,0..0,12
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
  .default_value Name 'int' Load - 0,9..0,12
'''),

('parse_type_param', 0, 0, 'TypeVar', {'_ver': 13}, (TypeVar,
r'''a: int = int'''), r'''
TypeVar - ROOT 0,0..0,12
  .name 'a'
  .bound Name 'int' Load - 0,3..0,6
  .default_value Name 'int' Load - 0,9..0,12
'''),

('parse_type_param', 0, 0, 'ParamSpec', {'_ver': 13}, (type_param,
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

('parse_type_param', 0, 0, 'ParamSpec', {'_ver': 13}, (ParamSpec,
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

('parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 13}, (type_param,
r'''*a = (int, str)'''), r'''
TypeVarTuple - ROOT 0,0..0,15
  .name 'a'
  .default_value Tuple - 0,5..0,15
    .elts[2]
     0] Name 'int' Load - 0,6..0,9
     1] Name 'str' Load - 0,11..0,14
    .ctx Load
'''),

('parse_type_param', 0, 0, 'TypeVarTuple', {'_ver': 13}, (TypeVarTuple,
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
