# (case idx, attr, start, False, field, options, code | (parse_mode, code),
#
# code after cut,
# dump code after cut)
# - OR
# error)

from fst.asttypes import *

DATA_GET_ONE = {
'all_basic': [  # ................................................................................

(0, '', 0, False, 'body', {}, (Module,
r'''a = 1'''),
r'''''',
r'''Module - ROOT 0,0..0,0''',
r'''a = 1''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
  0] Name 'a' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

(1, '', 0, False, 'body', {'_verify_self': False}, (Interactive,
r'''a = 1'''),
r'''''',
r'''Interactive - ROOT 0,0..0,0''',
r'''a = 1''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
  0] Name 'a' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

(2, '', None, False, 'body', {}, (Expression,
r'''a'''),
r'''**ValueError('cannot delete Expression.body')**''',
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

(3, '', None, False, 'decorator_list', {}, (FunctionDef, r'''
@deco
def func(): pass

'''),
r'''**NotImplementedError('this is not implemented yet')**'''),

(4, '', None, False, 'name', {}, (FunctionDef,
r'''def func(): pass'''),
r'''**ValueError('cannot delete FunctionDef.name')**''',
"\n'func'\n",
r'''<class 'str'>'''),

(5, '', 0, False, 'type_params', {'_ver': 12}, (FunctionDef,
r'''def func[T](): pass'''),
r'''def func(): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
  0] Pass - 0,12..0,16
''',
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
'''),

(6, '', None, False, 'args', {}, (FunctionDef,
r'''def func(a, /, b: int = 1, *c, d=2, **e): pass'''),
r'''def func(): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
  0] Pass - 0,12..0,16
''',
r'''a, /, b: int = 1, *c, d=2, **e''', r'''
arguments - ROOT 0,0..0,30
  .posonlyargs[1]
  0] arg - 0,0..0,1
    .arg 'a'
  .args[1]
  0] arg - 0,6..0,12
    .arg 'b'
    .annotation Name 'int' Load - 0,9..0,12
  .vararg arg - 0,19..0,20
    .arg 'c'
  .kwonlyargs[1]
  0] arg - 0,22..0,23
    .arg 'd'
  .kw_defaults[1]
  0] Constant 2 - 0,24..0,25
  .kwarg arg - 0,29..0,30
    .arg 'e'
  .defaults[1]
  0] Constant 1 - 0,15..0,16
'''),

(7, '', None, False, 'args', {}, (FunctionDef,
r'''def func(): pass'''),
r'''def func(): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
  0] Pass - 0,12..0,16
''',
r'''''',
r'''arguments - ROOT'''),

(8, '', None, False, 'returns', {}, (FunctionDef,
r'''def func() -> int: pass'''),
r'''def func(): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
  0] Pass - 0,12..0,16
''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

(9, '', None, False, 'returns', {}, (FunctionDef,
r'''def func(): pass'''),
r'''def func(): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
  0] Pass - 0,12..0,16
''',
r'''**None**'''),

(10, '', 0, False, 'body', {'_verify_self': False}, (FunctionDef,
r'''def func(): pass'''),
r'''def func():''', r'''
FunctionDef - ROOT 0,0..0,11
  .name 'func'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(11, '', 0, False, 'decorator_list', {}, (AsyncFunctionDef, r'''
@deco
async def func(): pass

'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''deco''',
r'''Name 'deco' Load - ROOT 0,0..0,4'''),

(12, '', None, False, 'name', {}, (AsyncFunctionDef,
r'''async def func(): pass'''),
r'''**ValueError('cannot delete AsyncFunctionDef.name')**''',
"\n'func'\n",
r'''<class 'str'>'''),

(13, '', 0, False, 'type_params', {'_ver': 12}, (AsyncFunctionDef,
r'''async def func[T](): pass'''),
r'''async def func(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
  0] Pass - 0,18..0,22
''',
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
'''),

(14, '', None, False, 'args', {}, (AsyncFunctionDef,
r'''async def func(a, /, b: int = 1, *c, d=2, **e): pass'''),
r'''async def func(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
  0] Pass - 0,18..0,22
''',
r'''a, /, b: int = 1, *c, d=2, **e''', r'''
arguments - ROOT 0,0..0,30
  .posonlyargs[1]
  0] arg - 0,0..0,1
    .arg 'a'
  .args[1]
  0] arg - 0,6..0,12
    .arg 'b'
    .annotation Name 'int' Load - 0,9..0,12
  .vararg arg - 0,19..0,20
    .arg 'c'
  .kwonlyargs[1]
  0] arg - 0,22..0,23
    .arg 'd'
  .kw_defaults[1]
  0] Constant 2 - 0,24..0,25
  .kwarg arg - 0,29..0,30
    .arg 'e'
  .defaults[1]
  0] Constant 1 - 0,15..0,16
'''),

(15, '', None, False, 'args', {}, (AsyncFunctionDef,
r'''async def func(): pass'''),
r'''async def func(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
  0] Pass - 0,18..0,22
''',
r'''''',
r'''arguments - ROOT'''),

(16, '', None, False, 'returns', {}, (AsyncFunctionDef,
r'''async def func() -> int: pass'''),
r'''async def func(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
  0] Pass - 0,18..0,22
''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

(17, '', None, False, 'returns', {}, (AsyncFunctionDef,
r'''async def func(): pass'''),
r'''async def func(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
  0] Pass - 0,18..0,22
''',
r'''**None**'''),

(18, '', 0, False, 'body', {'_verify_self': False}, (AsyncFunctionDef,
r'''async def func(): pass'''),
r'''async def func():''', r'''
AsyncFunctionDef - ROOT 0,0..0,17
  .name 'func'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(19, '', 0, False, 'decorator_list', {}, (ClassDef, r'''
@deco
class cls: pass

'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''deco''',
r'''Name 'deco' Load - ROOT 0,0..0,4'''),

(20, '', None, False, 'name', {}, (ClassDef,
r'''class cls: pass'''),
r'''**ValueError('cannot delete ClassDef.name')**''',
"\n'cls'\n",
r'''<class 'str'>'''),

(21, '', 0, False, 'type_params', {'_ver': 12}, (ClassDef,
r'''class cls[T](): pass'''),
r'''class cls(): pass''', r'''
ClassDef - ROOT 0,0..0,17
  .name 'cls'
  .body[1]
  0] Pass - 0,13..0,17
''',
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
'''),

(22, '', 0, False, 'bases', {}, (ClassDef,
r'''class cls(base): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
  0] Pass - 0,11..0,15
''',
r'''base''',
r'''Name 'base' Load - ROOT 0,0..0,4'''),

(23, '', 0, False, 'keywords', {}, (ClassDef,
r'''class cls(key=val): pass'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''key=val''', r'''
keyword - ROOT 0,0..0,7
  .arg 'key'
  .value Name 'val' Load - 0,4..0,7
'''),

(24, '', 0, False, 'body', {'_verify_self': False}, (ClassDef,
r'''class cls(): pass'''),
r'''class cls():''', r'''
ClassDef - ROOT 0,0..0,12
  .name 'cls'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(25, '', None, False, 'value', {}, (Return,
r'''return ret'''),
r'''return''',
r'''Return - ROOT 0,0..0,6''',
r'''ret''',
r'''Name 'ret' Load - ROOT 0,0..0,3'''),

(26, '', 0, False, 'targets', {}, (Delete,
r'''del var'''),
r'''**ValueError('cannot delete all Delete.targets without fix_delete_self=False')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(27, '', 0, False, 'targets', {'_verify_self': False, 'fix_delete_self': False}, (Delete,
r'''del var'''),
r'''del ''',
r'''Delete - ROOT 0,0..0,4''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(28, '', 0, False, 'targets', {}, (Assign,
r'''var = val'''),
r'''**ValueError('cannot cut all Assign.targets without fix_assign_self=False')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(29, '', 0, False, 'targets', {'_verify_self': False, 'fix_assign_self': False}, (Assign,
r'''var = val'''),
r''' val''', r'''
Assign - ROOT 0,0..0,4
  .value Name 'val' Load - 0,1..0,4
''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(30, '', None, False, 'value', {}, (Assign,
r'''var = val'''),
r'''**ValueError('cannot delete Assign.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(31, '', None, False, 'name', {'_ver': 12}, (TypeAlias,
r'''type t[T] = ...'''),
r'''**ValueError('cannot delete TypeAlias.name')**''',
r'''t''',
r'''Name 't' Load - ROOT 0,0..0,1'''),

(32, '', 0, False, 'type_params', {'_ver': 12}, (TypeAlias,
r'''type t[T] = ...'''),
r'''type t = ...''', r'''
TypeAlias - ROOT 0,0..0,12
  .name Name 't' Store - 0,5..0,6
  .value Constant Ellipsis - 0,9..0,12
''',
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
'''),

(33, '', None, False, 'value', {'_ver': 12}, (TypeAlias,
r'''type t[T] = ...'''),
r'''**ValueError('cannot delete TypeAlias.value')**''',
r'''...''',
r'''Constant Ellipsis - ROOT 0,0..0,3'''),

(34, '', None, False, 'target', {}, (AugAssign,
r'''var += 123'''),
r'''**ValueError('cannot delete AugAssign.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(35, '', None, False, 'op', {}, (AugAssign,
r'''var += 123'''),
r'''**ValueError('cannot delete AugAssign.op')**''',
r'''+=''',
r'''Add - ROOT 0,0..0,2'''),

(36, '', None, False, 'value', {}, (AugAssign,
r'''var += 123'''),
r'''**ValueError('cannot delete AugAssign.value')**''',
r'''123''',
r'''Constant 123 - ROOT 0,0..0,3'''),

(37, '', None, False, 'target', {}, (AnnAssign,
r'''var: int = 123'''),
r'''**ValueError('cannot delete AnnAssign.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(38, '', None, False, 'annotation', {}, (AnnAssign,
r'''var: int = 123'''),
r'''**ValueError('cannot delete AnnAssign.annotation')**''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

(39, '', None, False, 'value', {}, (AnnAssign,
r'''var: int = 123'''),
r'''var: int''', r'''
AnnAssign - ROOT 0,0..0,8
  .target Name 'var' Store - 0,0..0,3
  .annotation Name 'int' Load - 0,5..0,8
  .simple 1
''',
r'''123''',
r'''Constant 123 - ROOT 0,0..0,3'''),

(40, '', None, False, 'simple', {}, (AnnAssign,
r'''var: int = 123'''),
r'''**ValueError('cannot delete AnnAssign.simple')**''',
r'''1''',
r'''<class 'int'>'''),

(41, '', None, False, 'target', {}, (For,
r'''for var in iter(): pass'''),
r'''**ValueError('cannot delete For.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(42, '', None, False, 'iter', {}, (For,
r'''for var in iter(): pass'''),
r'''**ValueError('cannot delete For.iter')**''',
r'''iter()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'iter' Load - 0,0..0,4
'''),

(43, '', 0, False, 'body', {'_verify_self': False}, (For,
r'''for var in iter(): pass'''),
r'''for var in iter():''', r'''
For - ROOT 0,0..0,18
  .target Name 'var' Store - 0,4..0,7
  .iter Call - 0,11..0,17
    .func Name 'iter' Load - 0,11..0,15
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(44, '', 0, False, 'orelse', {}, (For, r'''
for var in iter(): pass
else: continue
'''), r'''
for var in iter(): pass

''', r'''
For - ROOT 0,0..0,23
  .target Name 'var' Store - 0,4..0,7
  .iter Call - 0,11..0,17
    .func Name 'iter' Load - 0,11..0,15
  .body[1]
  0] Pass - 0,19..0,23
''',
r'''continue''',
r'''Continue - ROOT 0,0..0,8'''),

(45, '', None, False, 'target', {}, (AsyncFor,
r'''async for var in iter(): pass'''),
r'''**ValueError('cannot delete AsyncFor.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(46, '', None, False, 'iter', {}, (AsyncFor,
r'''async for var in iter(): pass'''),
r'''**ValueError('cannot delete AsyncFor.iter')**''',
r'''iter()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'iter' Load - 0,0..0,4
'''),

(47, '', 0, False, 'body', {'_verify_self': False}, (AsyncFor,
r'''async for var in iter(): pass'''),
r'''async for var in iter():''', r'''
AsyncFor - ROOT 0,0..0,24
  .target Name 'var' Store - 0,10..0,13
  .iter Call - 0,17..0,23
    .func Name 'iter' Load - 0,17..0,21
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(48, '', 0, False, 'orelse', {}, (AsyncFor, r'''
async for var in iter(): pass
else: continue
'''), r'''
async for var in iter(): pass

''', r'''
AsyncFor - ROOT 0,0..0,29
  .target Name 'var' Store - 0,10..0,13
  .iter Call - 0,17..0,23
    .func Name 'iter' Load - 0,17..0,21
  .body[1]
  0] Pass - 0,25..0,29
''',
r'''continue''',
r'''Continue - ROOT 0,0..0,8'''),

(49, '', None, False, 'test', {}, (While,
r'''while var: pass'''),
r'''**ValueError('cannot delete While.test')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(50, '', 0, False, 'body', {'_verify_self': False}, (While,
r'''while var: pass'''),
r'''while var:''', r'''
While - ROOT 0,0..0,10
  .test Name 'var' Load - 0,6..0,9
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(51, '', 0, False, 'orelse', {}, (While, r'''
while var: pass
else: continue
'''), r'''
while var: pass

''', r'''
While - ROOT 0,0..0,15
  .test Name 'var' Load - 0,6..0,9
  .body[1]
  0] Pass - 0,11..0,15
''',
r'''continue''',
r'''Continue - ROOT 0,0..0,8'''),

(52, '', None, False, 'test', {}, (If,
r'''if var: pass'''),
r'''**ValueError('cannot delete If.test')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(53, '', 0, False, 'body', {'_verify_self': False}, (If,
r'''if var: pass'''),
r'''if var:''', r'''
If - ROOT 0,0..0,7
  .test Name 'var' Load - 0,3..0,6
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(54, '', 0, False, 'orelse', {}, (If, r'''
if var: pass
else: continue
'''), r'''
if var: pass

''', r'''
If - ROOT 0,0..0,12
  .test Name 'var' Load - 0,3..0,6
  .body[1]
  0] Pass - 0,8..0,12
''',
r'''continue''',
r'''Continue - ROOT 0,0..0,8'''),

(55, '', 0, False, 'items', {'_verify_self': False}, (With,
r'''with var: pass'''),
r'''**ValueError('cannot delete all With.items without fix_with_self=False')**''',
r'''var''', r'''
withitem - ROOT 0,0..0,3
  .context_expr Name 'var' Load - 0,0..0,3
'''),

(56, '', 0, False, 'body', {'_verify_self': False}, (With,
r'''with var: pass'''),
r'''with var:''', r'''
With - ROOT 0,0..0,9
  .items[1]
  0] withitem - 0,5..0,8
    .context_expr Name 'var' Load - 0,5..0,8
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(57, '', 0, False, 'items', {'_verify_self': False}, (AsyncWith,
r'''async with var: pass'''),
r'''**ValueError('cannot delete all AsyncWith.items without fix_with_self=False')**''',
r'''var''', r'''
withitem - ROOT 0,0..0,3
  .context_expr Name 'var' Load - 0,0..0,3
'''),

(58, '', 0, False, 'body', {'_verify_self': False}, (AsyncWith,
r'''async with var: pass'''),
r'''async with var:''', r'''
AsyncWith - ROOT 0,0..0,15
  .items[1]
  0] withitem - 0,11..0,14
    .context_expr Name 'var' Load - 0,11..0,14
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(59, '', None, False, 'subject', {}, (Match, r'''
match var:
  case 1: pass
'''),
r'''**ValueError('cannot delete Match.subject')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(60, '', 0, False, 'cases', {'_verify_self': False}, (Match, r'''
match var:
  case 1: pass
'''), r'''
match var:

''', r'''
Match - ROOT 0,0..0,10
  .subject Name 'var' Load - 0,6..0,9
''',
r'''case 1: pass''', r'''
match_case - ROOT 0,0..0,12
  .pattern MatchValue - 0,5..0,6
    .value Constant 1 - 0,5..0,6
  .body[1]
  0] Pass - 0,8..0,12
'''),

(61, '', None, False, 'exc', {}, (Raise,
r'''raise exc'''),
r'''raise''',
r'''Raise - ROOT 0,0..0,5''',
r'''exc''',
r'''Name 'exc' Load - ROOT 0,0..0,3'''),

(62, '', None, False, 'exc', {}, (Raise,
r'''raise exc from cause'''),
r'''**ValueError('cannot delete Raise.exc in this state')**''',
r'''exc''',
r'''Name 'exc' Load - ROOT 0,0..0,3'''),

(63, '', None, False, 'cause', {}, (Raise,
r'''raise exc from cause'''),
r'''raise exc''', r'''
Raise - ROOT 0,0..0,9
  .exc Name 'exc' Load - 0,6..0,9
''',
r'''cause''',
r'''Name 'cause' Load - ROOT 0,0..0,5'''),

(64, '', None, False, 'cause', {}, (Raise,
r'''raise exc'''),
r'''raise exc''', r'''
Raise - ROOT 0,0..0,9
  .exc Name 'exc' Load - 0,6..0,9
''',
r'''**None**'''),

(65, '', 0, False, 'body', {'_verify_self': False}, (Try, r'''
try: pass
except Exception: continue
'''),
r'''try:except Exception: continue''', r'''
Try - ROOT 0,0..0,30
  .handlers[1]
  0] ExceptHandler - 0,4..0,30
    .type Name 'Exception' Load - 0,11..0,20
    .body[1]
    0] Continue - 0,22..0,30
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(66, '', 0, False, 'handlers', {'_verify_self': False}, (Try, r'''
try: pass
except Exception: continue
'''), r'''
try: pass

''', r'''
Try - ROOT 0,0..0,9
  .body[1]
  0] Pass - 0,5..0,9
''',
r'''except Exception: continue''', r'''
ExceptHandler - ROOT 0,0..0,26
  .type Name 'Exception' Load - 0,7..0,16
  .body[1]
  0] Continue - 0,18..0,26
'''),

(67, '', 0, False, 'orelse', {}, (Try, r'''
try: pass
except Exception: continue
else: break
'''), r'''
try: pass
except Exception: continue

''', r'''
Try - ROOT 0,0..1,26
  .body[1]
  0] Pass - 0,5..0,9
  .handlers[1]
  0] ExceptHandler - 1,0..1,26
    .type Name 'Exception' Load - 1,7..1,16
    .body[1]
    0] Continue - 1,18..1,26
''',
r'''break''',
r'''Break - ROOT 0,0..0,5'''),

(68, '', 0, False, 'finalbody', {}, (Try, r'''
try: pass
except Exception: continue
finally: ...
'''), r'''
try: pass
except Exception: continue

''', r'''
Try - ROOT 0,0..1,26
  .body[1]
  0] Pass - 0,5..0,9
  .handlers[1]
  0] ExceptHandler - 1,0..1,26
    .type Name 'Exception' Load - 1,7..1,16
    .body[1]
    0] Continue - 1,18..1,26
''',
r'''...''', r'''
Expr - ROOT 0,0..0,3
  .value Constant Ellipsis - 0,0..0,3
'''),

(69, '', 0, False, 'body', {'_ver': 11, '_verify_self': False}, (TryStar, r'''
try: pass
except* Exception: continue
'''),
r'''try:except* Exception: continue''', r'''
TryStar - ROOT 0,0..0,31
  .handlers[1]
  0] ExceptHandler - 0,4..0,31
    .type Name 'Exception' Load - 0,12..0,21
    .body[1]
    0] Continue - 0,23..0,31
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(70, '', 0, False, 'handlers', {'_ver': 11, '_verify_self': False}, (TryStar, r'''
try: pass
except* Exception: continue
'''), r'''
try: pass

''', r'''
TryStar - ROOT 0,0..0,9
  .body[1]
  0] Pass - 0,5..0,9
''',
r'''except* Exception: continue''', r'''
ExceptHandler - ROOT 0,0..0,27
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
  0] Continue - 0,19..0,27
'''),

(71, '', 0, False, 'orelse', {'_ver': 11}, (TryStar, r'''
try: pass
except* Exception: continue
else: break
'''), r'''
try: pass
except* Exception: continue

''', r'''
TryStar - ROOT 0,0..1,27
  .body[1]
  0] Pass - 0,5..0,9
  .handlers[1]
  0] ExceptHandler - 1,0..1,27
    .type Name 'Exception' Load - 1,8..1,17
    .body[1]
    0] Continue - 1,19..1,27
''',
r'''break''',
r'''Break - ROOT 0,0..0,5'''),

(72, '', 0, False, 'finalbody', {'_ver': 11}, (TryStar, r'''
try: pass
except* Exception: continue
finally: ...
'''), r'''
try: pass
except* Exception: continue

''', r'''
TryStar - ROOT 0,0..1,27
  .body[1]
  0] Pass - 0,5..0,9
  .handlers[1]
  0] ExceptHandler - 1,0..1,27
    .type Name 'Exception' Load - 1,8..1,17
    .body[1]
    0] Continue - 1,19..1,27
''',
r'''...''', r'''
Expr - ROOT 0,0..0,3
  .value Constant Ellipsis - 0,0..0,3
'''),

(73, '', None, False, 'test', {}, (Assert,
r'''assert condition, message'''),
r'''**ValueError('cannot delete Assert.test')**''',
r'''condition''',
r'''Name 'condition' Load - ROOT 0,0..0,9'''),

(74, '', None, False, 'msg', {}, (Assert,
r'''assert condition, message'''),
r'''assert condition''', r'''
Assert - ROOT 0,0..0,16
  .test Name 'condition' Load - 0,7..0,16
''',
r'''message''',
r'''Name 'message' Load - ROOT 0,0..0,7'''),

(75, '', None, False, 'msg', {}, (Assert,
r'''assert condition'''),
r'''assert condition''', r'''
Assert - ROOT 0,0..0,16
  .test Name 'condition' Load - 0,7..0,16
''',
r'''**None**'''),

(76, '', 0, False, 'names', {}, (Import,
r'''import mod'''),
r'''**ValueError('cannot delete all Import.names without fix_import_self=False')**''',
r'''mod''', r'''
alias - ROOT 0,0..0,3
  .name 'mod'
'''),

(77, '', 0, False, 'names', {'_verify_self': False, 'fix_import_self': False}, (Import,
r'''import mod'''),
r'''import ''',
r'''Import - ROOT 0,0..0,7''',
r'''mod''', r'''
alias - ROOT 0,0..0,3
  .name 'mod'
'''),

(78, '', None, False, 'module', {}, (ImportFrom,
r'''from mod import name'''),
r'''**ValueError('cannot delete ImportFrom.module in this state')**''',
"\n'mod'\n",
r'''<class 'str'>'''),

(79, '', None, False, 'module', {}, (ImportFrom,
r'''from . import name'''),
r'''from . import name''', r'''
ImportFrom - ROOT 0,0..0,18
  .names[1]
  0] alias - 0,14..0,18
    .name 'name'
  .level 1
''',
r'''**None**'''),

(80, '', None, False, 'module', {}, (ImportFrom,
r'''from .mod import name'''),
r'''from . import name''', r'''
ImportFrom - ROOT 0,0..0,18
  .names[1]
  0] alias - 0,14..0,18
    .name 'name'
  .level 1
''',
"\n'mod'\n",
r'''<class 'str'>'''),

(81, '', 0, False, 'names', {}, (ImportFrom,
r'''from mod import name'''),
r'''**ValueError('cannot delete all ImportFrom.names without fix_import_self=False')**''',
r'''name''', r'''
alias - ROOT 0,0..0,4
  .name 'name'
'''),

(82, '', 0, False, 'names', {'_verify_self': False, 'fix_import_self': False}, (ImportFrom,
r'''from mod import name'''),
r'''from mod import ''', r'''
ImportFrom - ROOT 0,0..0,16
  .module 'mod'
  .level 0
''',
r'''name''', r'''
alias - ROOT 0,0..0,4
  .name 'name'
'''),

(83, '', None, False, 'level', {}, (ImportFrom,
r'''from mod import name'''),
r'''**ValueError('cannot delete ImportFrom.level')**''',
r'''0''',
r'''<class 'int'>'''),

(84, '', 0, False, 'names', {}, (Global,
r'''global var'''),
r'''**ValueError('cannot delete all Global.names without fix_global_self=False')**''',
"\n'var'\n",
r'''<class 'str'>'''),

(85, '', 0, False, 'names', {'_verify_self': False, 'fix_global_self': False}, (Global,
r'''global var'''),
r'''global ''',
r'''Global - ROOT 0,0..0,7''',
"\n'var'\n",
r'''<class 'str'>'''),

(86, '', 0, False, 'names', {}, (Nonlocal,
r'''nonlocal var'''),
r'''**ValueError('cannot delete all Nonlocal.names without fix_global_self=False')**''',
"\n'var'\n",
r'''<class 'str'>'''),

(87, '', 0, False, 'names', {'_verify_self': False, 'fix_global_self': False}, (Nonlocal,
r'''nonlocal var'''),
r'''nonlocal ''',
r'''Nonlocal - ROOT 0,0..0,9''',
"\n'var'\n",
r'''<class 'str'>'''),

(88, '', None, False, 'value', {}, (Expr,
r'''val'''),
r'''**ValueError('cannot delete Expr.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(89, '', None, False, 'op', {}, (BoolOp,
r'''val1 and val2'''),
r'''**ValueError('cannot delete BoolOp.op')**''',
r'''and''',
r'''And - ROOT 0,0..0,3'''),

(90, '', 0, False, 'values', {}, (BoolOp,
r'''val1 and val2'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''val1''',
r'''Name 'val1' Load - ROOT 0,0..0,4'''),

(91, '', None, False, 'target', {}, (NamedExpr,
r'''(var := val)'''),
r'''**ValueError('cannot delete NamedExpr.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

(92, '', None, False, 'value', {}, (NamedExpr,
r'''(var := val)'''),
r'''**ValueError('cannot delete NamedExpr.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(93, '', None, False, 'left', {}, (BinOp,
r'''val1 + val2'''),
r'''**ValueError('cannot delete BinOp.left')**''',
r'''val1''',
r'''Name 'val1' Load - ROOT 0,0..0,4'''),

(94, '', None, False, 'op', {}, (BinOp,
r'''val1 + val2'''),
r'''**ValueError('cannot delete BinOp.op')**''',
r'''+''',
r'''Add - ROOT 0,0..0,1'''),

(95, '', None, False, 'right', {}, (BinOp,
r'''val1 + val2'''),
r'''**ValueError('cannot delete BinOp.right')**''',
r'''val2''',
r'''Name 'val2' Load - ROOT 0,0..0,4'''),

(96, '', None, False, 'op', {}, (UnaryOp,
r'''-val'''),
r'''**ValueError('cannot delete UnaryOp.op')**''',
r'''-''',
r'''USub - ROOT 0,0..0,1'''),

(97, '', None, False, 'operand', {}, (UnaryOp,
r'''-val'''),
r'''**ValueError('cannot delete UnaryOp.operand')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(98, '', None, False, 'args', {}, (Lambda,
r'''lambda a, /, b=1, *c, d=2, **e: None'''),
r'''lambda: None''', r'''
Lambda - ROOT 0,0..0,12
  .body Constant None - 0,8..0,12
''',
r'''a, /, b=1, *c, d=2, **e''', r'''
arguments - ROOT 0,0..0,23
  .posonlyargs[1]
  0] arg - 0,0..0,1
    .arg 'a'
  .args[1]
  0] arg - 0,6..0,7
    .arg 'b'
  .vararg arg - 0,12..0,13
    .arg 'c'
  .kwonlyargs[1]
  0] arg - 0,15..0,16
    .arg 'd'
  .kw_defaults[1]
  0] Constant 2 - 0,17..0,18
  .kwarg arg - 0,22..0,23
    .arg 'e'
  .defaults[1]
  0] Constant 1 - 0,8..0,9
'''),

(99, '', None, False, 'args', {}, (Lambda,
r'''lambda: None'''),
r'''lambda: None''', r'''
Lambda - ROOT 0,0..0,12
  .body Constant None - 0,8..0,12
''',
r'''''',
r'''arguments - ROOT'''),

(100, '', None, False, 'body', {}, (Lambda,
r'''lambda: None'''),
r'''**ValueError('cannot delete Lambda.body')**''',
r'''None''',
r'''Constant None - ROOT 0,0..0,4'''),

(101, '', None, False, 'body', {}, (IfExp,
r'''body if test else orelse'''),
r'''**ValueError('cannot delete IfExp.body')**''',
r'''body''',
r'''Name 'body' Load - ROOT 0,0..0,4'''),

(102, '', None, False, 'test', {}, (IfExp,
r'''body if test else orelse'''),
r'''**ValueError('cannot delete IfExp.test')**''',
r'''test''',
r'''Name 'test' Load - ROOT 0,0..0,4'''),

(103, '', None, False, 'orelse', {}, (IfExp,
r'''body if test else orelse'''),
r'''**ValueError('cannot delete IfExp.orelse')**''',
r'''orelse''',
r'''Name 'orelse' Load - ROOT 0,0..0,6'''),

(104, '', 0, False, 'keys', {}, (Dict,
r'''{key: val}'''),
r'''{**val}''', r'''
Dict - ROOT 0,0..0,7
  .keys[1]
  0] None
  .values[1]
  0] Name 'val' Load - 0,3..0,6
''',
r'''key''',
r'''Name 'key' Load - ROOT 0,0..0,3'''),

(105, '', 0, False, 'keys', {}, (Dict,
r'''{**val}'''),
r'''{**val}''', r'''
Dict - ROOT 0,0..0,7
  .keys[1]
  0] None
  .values[1]
  0] Name 'val' Load - 0,3..0,6
''',
r'''**None**'''),

(106, '', 0, False, 'values', {}, (Dict,
r'''{key: val}'''),
r'''**ValueError('cannot delete from Dict.values')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(107, '', 0, False, None, {}, (Dict,
r'''{key: val}'''),
r'''**ValueError('cannot get single element from combined field of Dict')**'''),

(108, '', 0, False, 'elts', {}, (Set,
r'''{elt0, elt1}'''),
r'''{elt1}''', r'''
Set - ROOT 0,0..0,6
  .elts[1]
  0] Name 'elt1' Load - 0,1..0,5
''',
r'''elt0''',
r'''Name 'elt0' Load - ROOT 0,0..0,4'''),

(109, '', 0, False, 'elts', {}, (Set,
r'''{elt}'''),
r'''{*()}''', r'''
Set - ROOT 0,0..0,5
  .elts[1]
  0] Starred - 0,1..0,4
    .value Tuple - 0,2..0,4
      .ctx Load
    .ctx Load
''',
r'''elt''',
r'''Name 'elt' Load - ROOT 0,0..0,3'''),

(110, '', None, False, 'elt', {}, (ListComp,
r'''[val for val in iter]'''),
r'''**ValueError('cannot delete ListComp.elt')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(111, '', 0, False, 'generators', {}, (ListComp,
r'''[val for val in iter]'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''for val in iter''', r'''
comprehension - ROOT 0,0..0,15
  .target Name 'val' Store - 0,4..0,7
  .iter Name 'iter' Load - 0,11..0,15
  .is_async 0
'''),

(112, '', None, False, 'elt', {}, (SetComp,
r'''{val for val in iter}'''),
r'''**ValueError('cannot delete SetComp.elt')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(113, '', 0, False, 'generators', {}, (SetComp,
r'''{val for val in iter}'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''for val in iter''', r'''
comprehension - ROOT 0,0..0,15
  .target Name 'val' Store - 0,4..0,7
  .iter Name 'iter' Load - 0,11..0,15
  .is_async 0
'''),

(114, '', None, False, 'key', {}, (DictComp,
r'''{key: val for key, val in iter}'''),
r'''**ValueError('cannot delete DictComp.key')**''',
r'''key''',
r'''Name 'key' Load - ROOT 0,0..0,3'''),

(115, '', None, False, 'value', {}, (DictComp,
r'''{key: val for key, val in iter}'''),
r'''**ValueError('cannot delete DictComp.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(116, '', 0, False, 'generators', {}, (DictComp,
r'''{key: val for key, val in iter}'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''for key, val in iter''', r'''
comprehension - ROOT 0,0..0,20
  .target Tuple - 0,4..0,12
    .elts[2]
    0] Name 'key' Store - 0,4..0,7
    1] Name 'val' Store - 0,9..0,12
    .ctx Store
  .iter Name 'iter' Load - 0,16..0,20
  .is_async 0
'''),

(117, '', None, False, 'elt', {}, (GeneratorExp,
r'''(val for val in iter)'''),
r'''**ValueError('cannot delete GeneratorExp.elt')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(118, '', 0, False, 'generators', {}, (GeneratorExp,
r'''(val for val in iter)'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''for val in iter''', r'''
comprehension - ROOT 0,0..0,15
  .target Name 'val' Store - 0,4..0,7
  .iter Name 'iter' Load - 0,11..0,15
  .is_async 0
'''),

(119, '', None, False, 'value', {}, (Await,
r'''await val'''),
r'''**ValueError('cannot delete Await.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(120, '', None, False, 'value', {}, (Yield,
r'''yield val'''),
r'''yield''',
r'''Yield - ROOT 0,0..0,5''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(121, '', None, False, 'value', {}, (Yield,
r'''yield'''),
r'''yield''',
r'''Yield - ROOT 0,0..0,5''',
r'''**None**'''),

(122, '', None, False, 'value', {}, (YieldFrom,
r'''yield from val'''),
r'''**ValueError('cannot delete YieldFrom.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(123, '', None, False, 'left', {}, (Compare,
r'''val0 < val1'''),
r'''**ValueError('cannot delete Compare.left')**''',
r'''val0''',
r'''Name 'val0' Load - ROOT 0,0..0,4'''),

(124, '', 0, False, 'ops', {}, (Compare,
r'''val0 < val1'''),
r'''**ValueError('cannot delete from Compare.ops')**''',
r'''<''',
r'''Lt - ROOT 0,0..0,1'''),

(125, '', 0, False, 'comparators', {}, (Compare,
r'''val0 < val1'''),
r'''**ValueError('cannot delete from Compare.comparators')**''',
r'''val1''',
r'''Name 'val1' Load - ROOT 0,0..0,4'''),

(126, '', 0, False, None, {'_verify': False}, (Compare,
r'''val0 < val1'''),
r'''**NotImplementedError('still need to decide how to handle this case')**''',
r'''val0''',
r'''Name 'val0' Load - ROOT 0,0..0,4'''),

(127, '', 0, False, None, {}, (Compare,
r'''val0 < val1'''),
r'''**NotImplementedError('still need to decide how to handle this case')**''',
r'''val0''',
r'''Name 'val0' Load - ROOT 0,0..0,4'''),

(128, '', 1, False, None, {}, (Compare,
r'''val0 < val1'''),
r'''**NotImplementedError('still need to decide how to handle this case')**''',
r'''val1''',
r'''Name 'val1' Load - ROOT 0,0..0,4'''),

(129, '', 2, False, None, {}, (Compare,
r'''val0 < val1'''),
r'''**IndexError('index out of range')**'''),

(130, '', None, False, 'func', {}, (Call,
r'''call()'''),
r'''**ValueError('cannot delete Call.func')**''',
r'''call''',
r'''Name 'call' Load - ROOT 0,0..0,4'''),

(131, '', 0, False, 'args', {}, (Call,
r'''call(arg)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''arg''',
r'''Name 'arg' Load - ROOT 0,0..0,3'''),

(132, '', 0, False, 'keywords', {}, (Call,
r'''call(key=val)'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''key=val''', r'''
keyword - ROOT 0,0..0,7
  .arg 'key'
  .value Name 'val' Load - 0,4..0,7
'''),

(133, 'values[1]', None, False, 'value', {'_ver': 12}, (None,
r'''f"a{val:<16!r}c"'''),
r'''**ValueError('cannot delete FormattedValue.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(134, 'values[1]', None, False, 'conversion', {'_ver': 12}, (None,
r'''f"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
r'''**None**'''),

(135, 'values[1]', None, False, 'format_spec', {'_ver': 12}, (None,
r'''f"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
"\nf'<16!r'\n", r'''
JoinedStr - ROOT 0,0..0,8
  .values[1]
  0] Constant '<16!r' - 0,2..0,7
'''),

(136, '', 0, False, 'values', {'_ver': 12}, (JoinedStr,
r'''f"a{val:<16!r}c"'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
"\n'a'\n",
r'''Constant 'a' - ROOT 0,0..0,3'''),

(137, '', 1, False, 'values', {'_ver': 12}, (JoinedStr,
r'''f"a{val:<16!r}c"'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''f"{val:<16!r}"''', r'''
JoinedStr - ROOT 0,0..0,14
  .values[1]
  0] FormattedValue - 0,2..0,13
    .value Name 'val' Load - 0,3..0,6
    .conversion -1
    .format_spec JoinedStr - 0,6..0,12
      .values[1]
      0] Constant '<16!r' - 0,7..0,12
'''),

(138, 'values[1]', None, False, 'value', {'_ver': 14}, (None,
r'''t"a{val:<16!r}c"'''),
r'''**ValueError('cannot delete Interpolation.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(139, 'values[1]', None, False, 'str', {'_ver': 14}, (None,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
"\n'val'\n",
r'''<class 'str'>'''),

(140, 'values[1]', None, False, 'conversion', {'_ver': 14}, (None,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
r'''**None**'''),

(141, 'values[1]', None, False, 'format_spec', {'_ver': 14}, (None,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
"\nf'<16!r'\n", r'''
JoinedStr - ROOT 0,0..0,8
  .values[1]
  0] Constant '<16!r' - 0,2..0,7
'''),

(142, '', 0, False, 'values', {'_ver': 14}, (TemplateStr,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
"\n'a'\n",
r'''Constant 'a' - ROOT 0,0..0,3'''),

(143, '', 1, False, 'values', {'_ver': 14}, (TemplateStr,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''t"{val:<16!r}"''', r'''
TemplateStr - ROOT 0,0..0,14
  .values[1]
  0] Interpolation - 0,2..0,13
    .value Name 'val' Load - 0,3..0,6
    .str 'val'
    .conversion -1
    .format_spec JoinedStr - 0,6..0,12
      .values[1]
      0] Constant '<16!r' - 0,7..0,12
'''),

(144, '', None, False, 'value', {}, (Constant,
r'''...'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''Ellipsis''',
r'''<class 'ellipsis'>'''),

(145, '', None, False, 'value', {}, (Constant,
r'''123'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''123''',
r'''<class 'int'>'''),

(146, '', None, False, 'value', {}, (Constant,
r'''1.23'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''1.23''',
r'''<class 'float'>'''),

(147, '', None, False, 'value', {}, (Constant,
r'''123j'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''123j''',
r'''<class 'complex'>'''),

(148, '', None, False, 'value', {}, (Constant,
r'''"str"'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
"\n'str'\n",
r'''<class 'str'>'''),

(149, '', None, False, 'value', {}, (Constant,
r'''b"123"'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
"\nb'123'\n",
r'''<class 'bytes'>'''),

(150, '', None, False, 'value', {}, (Constant,
r'''True'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''True''',
r'''<class 'bool'>'''),

(151, '', None, False, 'value', {}, (Constant,
r'''False'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''False''',
r'''<class 'bool'>'''),

(152, '', None, False, 'value', {}, (Constant,
r'''None'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''**None**'''),

(153, '', None, False, 'kind', {}, (Constant,
r'''1'''),
r'''**ValueError('cannot set kind of non-str Constant')**''',
r'''**None**'''),

(154, '', None, False, 'kind', {}, (Constant,
r'''"str"'''),
r'''"str"''',
r'''Constant 'str' - ROOT 0,0..0,5''',
r'''**None**'''),

(155, '', None, False, 'kind', {}, (Constant,
r'''u"str"'''),
r'''"str"''',
r'''Constant 'str' - ROOT 0,0..0,5''',
"\n'u'\n",
r'''<class 'str'>'''),

(156, '', None, False, 'value', {}, (Attribute,
r'''val.attr'''),
r'''**ValueError('cannot delete Attribute.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(157, '', None, False, 'attr', {}, (Attribute,
r'''val.attr'''),
r'''**ValueError('cannot delete Attribute.attr')**''',
"\n'attr'\n",
r'''<class 'str'>'''),

(158, '', None, False, 'ctx', {}, (Attribute,
r'''val.attr'''),
r'''**ValueError('cannot delete Attribute.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

(159, 'targets[0]', None, False, 'ctx', {}, (None,
r'''val.attr = 1'''),
r'''**ValueError('cannot delete Attribute.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

(160, 'targets[0]', None, False, 'ctx', {}, (None,
r'''del val.attr'''),
r'''**ValueError('cannot delete Attribute.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

(161, '', None, False, 'value', {}, (Subscript,
r'''val[slice]'''),
r'''**ValueError('cannot delete Subscript.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(162, '', None, False, 'slice', {}, (Subscript,
r'''val[slice]'''),
r'''**ValueError('cannot delete Subscript.slice')**''',
r'''slice''',
r'''Name 'slice' Load - ROOT 0,0..0,5'''),

(163, '', None, False, 'ctx', {}, (Subscript,
r'''val[slice]'''),
r'''**ValueError('cannot delete Subscript.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

(164, 'targets[0]', None, False, 'ctx', {}, (None,
r'''val[slice] = 1'''),
r'''**ValueError('cannot delete Subscript.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

(165, 'targets[0]', None, False, 'ctx', {}, (None,
r'''del val[slice]'''),
r'''**ValueError('cannot delete Subscript.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

(166, '', None, False, 'value', {}, (Starred,
r'''*st'''),
r'''**ValueError('cannot delete Starred.value')**''',
r'''st''',
r'''Name 'st' Load - ROOT 0,0..0,2'''),

(167, '', None, False, 'ctx', {}, (Starred,
r'''*st'''),
r'''**ValueError('cannot delete Starred.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

(168, 'targets[0].elts[0]', None, False, 'ctx', {}, (None,
r'''*st, = 1'''),
r'''**ValueError('cannot delete Starred.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

(169, '', None, False, 'id', {}, (Name,
r'''name'''),
r'''**ValueError('cannot delete Name.id')**''',
"\n'name'\n",
r'''<class 'str'>'''),

(170, '', None, False, 'ctx', {}, (Name,
r'''name'''),
r'''**ValueError('cannot delete Name.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

(171, 'targets[0]', None, False, 'ctx', {}, (None,
r'''name = 1'''),
r'''**ValueError('cannot delete Name.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

(172, 'targets[0]', None, False, 'ctx', {}, (None,
r'''del name'''),
r'''**ValueError('cannot delete Name.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

(173, '', None, False, 'elts', {}, (List,
r'''[val]'''),
r'''[]''', r'''
List - ROOT 0,0..0,2
  .ctx Load
''',
r'''[val]''', r'''
List - ROOT 0,0..0,5
  .elts[1]
  0] Name 'val' Load - 0,1..0,4
  .ctx Load
'''),

(174, '', None, False, 'ctx', {}, (List,
r'''[val]'''),
r'''**ValueError('cannot delete List.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

(175, 'targets[0]', None, False, 'ctx', {}, (None,
r'''[val] = 1'''),
r'''**ValueError('cannot delete List.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

(176, 'targets[0]', None, False, 'ctx', {}, (None,
r'''del [val]'''),
r'''**ValueError('cannot delete List.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

(177, '', None, False, 'elts', {}, (Tuple,
r'''(val,)'''),
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
''',
r'''(val,)''', r'''
Tuple - ROOT 0,0..0,6
  .elts[1]
  0] Name 'val' Load - 0,1..0,4
  .ctx Load
'''),

(178, '', None, False, 'ctx', {}, (Tuple,
r'''(val,)'''),
r'''**ValueError('cannot delete Tuple.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

(179, '', None, False, 'elts', {}, (Tuple,
r'''val,'''),
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
''',
r'''val,''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
  0] Name 'val' Load - 0,0..0,3
  .ctx Load
'''),

(180, '', None, False, 'ctx', {}, (Tuple,
r'''val,'''),
r'''**ValueError('cannot delete Tuple.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

(181, 'targets[0]', None, False, 'ctx', {}, (None,
r'''val, = 1'''),
r'''**ValueError('cannot delete Tuple.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

(182, 'targets[0]', None, False, 'ctx', {}, (None,
r'''del val,'''),
r'''**ValueError('cannot delete Name.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

(183, '', None, False, 'lower', {}, (Slice,
r'''lower:upper:step'''),
r''':upper:step''', r'''
Slice - ROOT 0,0..0,11
  .upper Name 'upper' Load - 0,1..0,6
  .step Name 'step' Load - 0,7..0,11
''',
r'''lower''',
r'''Name 'lower' Load - ROOT 0,0..0,5'''),

(184, '', None, False, 'lower', {}, (Slice,
r''':'''),
r''':''',
r'''Slice - ROOT 0,0..0,1''',
r'''**None**'''),

(185, '', None, False, 'upper', {}, (Slice,
r'''lower:upper:step'''),
r'''lower::step''', r'''
Slice - ROOT 0,0..0,11
  .lower Name 'lower' Load - 0,0..0,5
  .step Name 'step' Load - 0,7..0,11
''',
r'''upper''',
r'''Name 'upper' Load - ROOT 0,0..0,5'''),

(186, '', None, False, 'upper', {}, (Slice,
r''':'''),
r''':''',
r'''Slice - ROOT 0,0..0,1''',
r'''**None**'''),

(187, '', None, False, 'step', {}, (Slice,
r'''lower:upper:step'''),
r'''lower:upper:''', r'''
Slice - ROOT 0,0..0,12
  .lower Name 'lower' Load - 0,0..0,5
  .upper Name 'upper' Load - 0,6..0,11
''',
r'''step''',
r'''Name 'step' Load - ROOT 0,0..0,4'''),

(188, '', None, False, 'step', {}, (Slice,
r''':'''),
r''':''',
r'''Slice - ROOT 0,0..0,1''',
r'''**None**'''),

(189, '', None, False, 'target', {}, (comprehension,
r'''for val in iter if not val'''),
r'''**ValueError('cannot delete comprehension.target')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(190, '', None, False, 'iter', {}, (comprehension,
r'''for val in iter if not val'''),
r'''**ValueError('cannot delete comprehension.iter')**''',
r'''iter''',
r'''Name 'iter' Load - ROOT 0,0..0,4'''),

(191, '', 0, False, 'ifs', {}, (comprehension,
r'''for val in iter if not val'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''not val''', r'''
UnaryOp - ROOT 0,0..0,7
  .op Not - 0,0..0,3
  .operand Name 'val' Load - 0,4..0,7
'''),

(192, '', None, False, 'is_async', {}, (comprehension,
r'''for val in iter if not val'''),
r'''**ValueError('cannot delete comprehension.is_async')**''',
r'''0''',
r'''<class 'int'>'''),

(193, '', None, False, 'is_async', {}, (comprehension,
r'''async for val in iter if not val'''),
r'''**ValueError('cannot delete comprehension.is_async')**''',
r'''1''',
r'''<class 'int'>'''),

(194, '', None, False, 'type', {}, (ExceptHandler,
r'''except Exception: pass'''),
r'''except: pass''', r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
  0] Pass - 0,8..0,12
''',
r'''Exception''',
r'''Name 'Exception' Load - ROOT 0,0..0,9'''),

(195, '', None, False, 'type', {}, (ExceptHandler,
r'''except Exception as exc: pass'''),
r'''**ValueError('cannot delete ExceptHandler.type in this state')**''',
r'''Exception''',
r'''Name 'Exception' Load - ROOT 0,0..0,9'''),

(196, '', None, False, 'name', {}, (ExceptHandler,
r'''except Exception as exc: pass'''),
r'''except Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,22
  .type Name 'Exception' Load - 0,7..0,16
  .body[1]
  0] Pass - 0,18..0,22
''',
"\n'exc'\n",
r'''<class 'str'>'''),

(197, '', None, False, 'name', {}, (ExceptHandler,
r'''except Exception: pass'''),
r'''except Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,22
  .type Name 'Exception' Load - 0,7..0,16
  .body[1]
  0] Pass - 0,18..0,22
''',
r'''**None**'''),

(198, '', 0, False, 'body', {'_verify_self': False}, (ExceptHandler,
r'''except Exception as exc: pass'''),
r'''except Exception as exc:''', r'''
ExceptHandler - ROOT 0,0..0,24
  .type Name 'Exception' Load - 0,7..0,16
  .name 'exc'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(199, '', None, False, 'type', {'_ver': 11}, (ExceptHandler,
r'''except* Exception: pass'''),
r'''**ValueError('cannot delete ExceptHandler.type in this state')**''',
r'''Exception''',
r'''Name 'Exception' Load - ROOT 0,0..0,9'''),

(200, '', None, False, 'type', {'_ver': 11}, (ExceptHandler,
r'''except* Exception as exc: pass'''),
r'''**ValueError('cannot delete ExceptHandler.type in this state')**''',
r'''Exception''',
r'''Name 'Exception' Load - ROOT 0,0..0,9'''),

(201, '', None, False, 'name', {'_ver': 11}, (ExceptHandler,
r'''except* Exception as exc: pass'''),
r'''except* Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,23
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
  0] Pass - 0,19..0,23
''',
"\n'exc'\n",
r'''<class 'str'>'''),

(202, '', None, False, 'name', {'_ver': 11}, (ExceptHandler,
r'''except* Exception: pass'''),
r'''except* Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,23
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
  0] Pass - 0,19..0,23
''',
r'''**None**'''),

(203, '', 0, False, 'body', {'_ver': 11, '_verify_self': False}, (ExceptHandler,
r'''except* Exception as exc: pass'''),
r'''except* Exception as exc:''', r'''
ExceptHandler - ROOT 0,0..0,25
  .type Name 'Exception' Load - 0,8..0,17
  .name 'exc'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(204, '', 0, False, 'posonlyargs', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''**ValueError('cannot delete from arguments.posonlyargs')**''',
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

(205, '', 0, False, 'args', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''**ValueError('cannot delete from arguments.args')**''',
r'''b: int''', r'''
arg - ROOT 0,0..0,6
  .arg 'b'
  .annotation Name 'int' Load - 0,3..0,6
'''),

(206, '', 0, False, 'defaults', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''**ValueError('cannot delete from arguments.defaults')**''',
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

(207, '', None, False, 'vararg', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''a, /, b: int = 1, *, d=2, **e''', r'''
arguments - ROOT 0,0..0,29
  .posonlyargs[1]
  0] arg - 0,0..0,1
    .arg 'a'
  .args[1]
  0] arg - 0,6..0,12
    .arg 'b'
    .annotation Name 'int' Load - 0,9..0,12
  .kwonlyargs[1]
  0] arg - 0,21..0,22
    .arg 'd'
  .kw_defaults[1]
  0] Constant 2 - 0,23..0,24
  .kwarg arg - 0,28..0,29
    .arg 'e'
  .defaults[1]
  0] Constant 1 - 0,15..0,16
''',
r'''c''', r'''
arg - ROOT 0,0..0,1
  .arg 'c'
'''),

(208, '', None, False, 'vararg', {}, (arguments,
r'''a, /, b: int = 1, d=2, **e'''),
r'''a, /, b: int = 1, d=2, **e''', r'''
arguments - ROOT 0,0..0,26
  .posonlyargs[1]
  0] arg - 0,0..0,1
    .arg 'a'
  .args[2]
  0] arg - 0,6..0,12
    .arg 'b'
    .annotation Name 'int' Load - 0,9..0,12
  1] arg - 0,18..0,19
    .arg 'd'
  .kwarg arg - 0,25..0,26
    .arg 'e'
  .defaults[2]
  0] Constant 1 - 0,15..0,16
  1] Constant 2 - 0,20..0,21
''',
r'''**None**'''),

(209, '', 0, False, 'kwonlyargs', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''**ValueError('cannot delete from arguments.kwonlyargs')**''',
r'''d''', r'''
arg - ROOT 0,0..0,1
  .arg 'd'
'''),

(210, '', 0, False, 'kw_defaults', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''a, /, b: int = 1, *c, d, **e''', r'''
arguments - ROOT 0,0..0,28
  .posonlyargs[1]
  0] arg - 0,0..0,1
    .arg 'a'
  .args[1]
  0] arg - 0,6..0,12
    .arg 'b'
    .annotation Name 'int' Load - 0,9..0,12
  .vararg arg - 0,19..0,20
    .arg 'c'
  .kwonlyargs[1]
  0] arg - 0,22..0,23
    .arg 'd'
  .kw_defaults[1]
  0] None
  .kwarg arg - 0,27..0,28
    .arg 'e'
  .defaults[1]
  0] Constant 1 - 0,15..0,16
''',
r'''2''',
r'''Constant 2 - ROOT 0,0..0,1'''),

(211, '', None, False, 'kwarg', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''a, /, b: int = 1, *c, d=2''', r'''
arguments - ROOT 0,0..0,25
  .posonlyargs[1]
  0] arg - 0,0..0,1
    .arg 'a'
  .args[1]
  0] arg - 0,6..0,12
    .arg 'b'
    .annotation Name 'int' Load - 0,9..0,12
  .vararg arg - 0,19..0,20
    .arg 'c'
  .kwonlyargs[1]
  0] arg - 0,22..0,23
    .arg 'd'
  .kw_defaults[1]
  0] Constant 2 - 0,24..0,25
  .defaults[1]
  0] Constant 1 - 0,15..0,16
''',
r'''e''', r'''
arg - ROOT 0,0..0,1
  .arg 'e'
'''),

(212, '', None, False, 'kwarg', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2'''),
r'''a, /, b: int = 1, *c, d=2''', r'''
arguments - ROOT 0,0..0,25
  .posonlyargs[1]
  0] arg - 0,0..0,1
    .arg 'a'
  .args[1]
  0] arg - 0,6..0,12
    .arg 'b'
    .annotation Name 'int' Load - 0,9..0,12
  .vararg arg - 0,19..0,20
    .arg 'c'
  .kwonlyargs[1]
  0] arg - 0,22..0,23
    .arg 'd'
  .kw_defaults[1]
  0] Constant 2 - 0,24..0,25
  .defaults[1]
  0] Constant 1 - 0,15..0,16
''',
r'''**None**'''),

(213, '', None, False, 'arg', {}, (arg,
r'''arg: ann'''),
r'''**ValueError('cannot delete arg.arg')**''',
"\n'arg'\n",
r'''<class 'str'>'''),

(214, '', None, False, 'annotation', {}, (arg,
r'''arg: ann'''),
r'''arg''', r'''
arg - ROOT 0,0..0,3
  .arg 'arg'
''',
r'''ann''',
r'''Name 'ann' Load - ROOT 0,0..0,3'''),

(215, '', None, False, 'annotation', {}, (arg,
r'''arg'''),
r'''arg''', r'''
arg - ROOT 0,0..0,3
  .arg 'arg'
''',
r'''**None**'''),

(216, '', None, False, 'arg', {}, (keyword,
r'''key=val'''),
r'''**val''', r'''
keyword - ROOT 0,0..0,5
  .value Name 'val' Load - 0,2..0,5
''',
"\n'key'\n",
r'''<class 'str'>'''),

(217, '', None, False, 'value', {}, (keyword,
r'''key=val'''),
r'''**ValueError('cannot delete keyword.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

(218, '', None, False, 'name', {}, (alias,
r'''name as asname'''),
r'''**ValueError('cannot delete alias.name')**''',
"\n'name'\n",
r'''<class 'str'>'''),

(219, '', None, False, 'asname', {}, (alias,
r'''name as asname'''),
r'''name''', r'''
alias - ROOT 0,0..0,4
  .name 'name'
''',
"\n'asname'\n",
r'''<class 'str'>'''),

(220, '', None, False, 'asname', {}, (alias,
r'''name'''),
r'''name''', r'''
alias - ROOT 0,0..0,4
  .name 'name'
''',
r'''**None**'''),

(221, '', None, False, 'context_expr', {}, (withitem,
r'''context as optional'''),
r'''**ValueError('cannot delete withitem.context_expr in this state')**''',
r'''context''',
r'''Name 'context' Load - ROOT 0,0..0,7'''),

(222, '', None, False, 'optional_vars', {}, (withitem,
r'''context as optional'''),
r'''context''', r'''
withitem - ROOT 0,0..0,7
  .context_expr Name 'context' Load - 0,0..0,7
''',
r'''optional''',
r'''Name 'optional' Load - ROOT 0,0..0,8'''),

(223, '', None, False, 'optional_vars', {}, (withitem,
r'''context'''),
r'''context''', r'''
withitem - ROOT 0,0..0,7
  .context_expr Name 'context' Load - 0,0..0,7
''',
r'''**None**'''),

(224, '', None, False, 'pattern', {}, (match_case,
r'''case 1 as a if not a: pass'''),
r'''**ValueError('cannot delete match_case.pattern')**''',
r'''1 as a''', r'''
MatchAs - ROOT 0,0..0,6
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'a'
'''),

(225, '', None, False, 'guard', {}, (match_case,
r'''case 1 as a if not a: pass'''),
r'''case 1 as a: pass''', r'''
match_case - ROOT 0,0..0,17
  .pattern MatchAs - 0,5..0,11
    .pattern MatchValue - 0,5..0,6
      .value Constant 1 - 0,5..0,6
    .name 'a'
  .body[1]
  0] Pass - 0,13..0,17
''',
r'''not a''', r'''
UnaryOp - ROOT 0,0..0,5
  .op Not - 0,0..0,3
  .operand Name 'a' Load - 0,4..0,5
'''),

(226, '', None, False, 'guard', {}, (match_case,
r'''case 1 as a: pass'''),
r'''case 1 as a: pass''', r'''
match_case - ROOT 0,0..0,17
  .pattern MatchAs - 0,5..0,11
    .pattern MatchValue - 0,5..0,6
      .value Constant 1 - 0,5..0,6
    .name 'a'
  .body[1]
  0] Pass - 0,13..0,17
''',
r'''**None**'''),

(227, '', 0, False, 'body', {'_verify_self': False}, (match_case,
r'''case 1 as a if not a: pass'''),
r'''case 1 as a if not a:''', r'''
match_case - ROOT 0,0..0,21
  .pattern MatchAs - 0,5..0,11
    .pattern MatchValue - 0,5..0,6
      .value Constant 1 - 0,5..0,6
    .name 'a'
  .guard UnaryOp - 0,15..0,20
    .op Not - 0,15..0,18
    .operand Name 'a' Load - 0,19..0,20
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

(228, '', None, False, 'value', {}, (MatchValue,
r'''123'''),
r'''**ValueError('cannot delete MatchValue.value')**''',
r'''123''',
r'''Constant 123 - ROOT 0,0..0,3'''),

(229, '', None, False, 'value', {}, (MatchSingleton,
r'''True'''),
r'''None''',
r'''MatchSingleton - ROOT 0,0..0,4''',
r'''True''',
r'''<class 'bool'>'''),

(230, '', None, False, 'value', {}, (MatchSingleton,
r'''False'''),
r'''None''',
r'''MatchSingleton - ROOT 0,0..0,4''',
r'''False''',
r'''<class 'bool'>'''),

(231, '', None, False, 'value', {}, (MatchSingleton,
r'''None'''),
r'''None''',
r'''MatchSingleton - ROOT 0,0..0,4''',
r'''**None**'''),

(232, '', 0, False, 'patterns', {}, (MatchSequence,
r'''[a]'''),
r'''[]''',
r'''MatchSequence - ROOT 0,0..0,2''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

(233, '', 0, False, 'keys', {}, (MatchMapping,
r'''{1: a, **rest}'''),
r'''**ValueError('cannot delete from MatchMapping.keys')**''',
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

(234, '', 0, False, 'patterns', {}, (MatchMapping,
r'''{1: a, **rest}'''),
r'''**ValueError('cannot delete from MatchMapping.patterns')**''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

(235, '', None, False, 'rest', {}, (MatchMapping,
r'''{1: a, **rest}'''),
r'''{1: a}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
  0] Constant 1 - 0,1..0,2
  .patterns[1]
  0] MatchAs - 0,4..0,5
    .name 'a'
''',
"\n'rest'\n",
r'''<class 'str'>'''),

(236, '', None, False, 'rest', {}, (MatchMapping,
r'''{1: a}'''),
r'''{1: a}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
  0] Constant 1 - 0,1..0,2
  .patterns[1]
  0] MatchAs - 0,4..0,5
    .name 'a'
''',
r'''**None**'''),

(237, '', 0, False, None, {}, (MatchMapping,
r'''{1: a, **rest}'''),
r'''**ValueError('cannot get single element from combined field of MatchMapping')**'''),

(238, '', None, False, 'cls', {}, (MatchClass,
r'''cls(a, b=c)'''),
r'''**ValueError('cannot delete MatchClass.cls')**''',
r'''cls''',
r'''Name 'cls' Load - ROOT 0,0..0,3'''),

(239, '', 0, False, 'patterns', {}, (MatchClass,
r'''cls(a, b=c)'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

(240, '', 0, False, 'kwd_attrs', {}, (MatchClass,
r'''cls(a, b=c)'''),
r'''**ValueError('cannot delete from MatchClass.kwd_attrs')**''',
"\n'b'\n",
r'''<class 'str'>'''),

(241, '', 0, False, 'kwd_patterns', {}, (MatchClass,
r'''cls(a, b=c)'''),
r'''**ValueError('cannot delete from MatchClass.kwd_patterns')**''',
r'''c''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'c'
'''),

(242, '', None, False, 'name', {}, (MatchStar,
r'''*st'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2''',
"\n'st'\n",
r'''<class 'str'>'''),

(243, '', None, False, 'name', {}, (MatchStar,
r'''*_'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2''',
r'''**None**'''),

(244, '', None, False, 'pattern', {}, (MatchAs,
r'''pat as name'''),
r'''name''', r'''
MatchAs - ROOT 0,0..0,4
  .name 'name'
''',
r'''pat''', r'''
MatchAs - ROOT 0,0..0,3
  .name 'pat'
'''),

(245, '', None, False, 'pattern', {}, (MatchAs,
r'''name'''),
r'''name''', r'''
MatchAs - ROOT 0,0..0,4
  .name 'name'
''',
r'''**None**'''),

(246, '', None, False, 'name', {}, (MatchAs,
r'''pat as name'''),
r'''**ValueError("cannot change MatchAs with pattern into wildcard '_'")**''',
"\n'name'\n",
r'''<class 'str'>'''),

(247, '', 0, False, 'patterns', {}, (MatchOr,
r'''a | b | c'''),
r'''b | c''', r'''
MatchOr - ROOT 0,0..0,5
  .patterns[2]
  0] MatchAs - 0,0..0,1
    .name 'b'
  1] MatchAs - 0,4..0,5
    .name 'c'
''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

(248, '', 0, False, 'patterns', {}, (MatchOr,
r'''a | b'''),
r'''b''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'b'
''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

(249, '', None, False, 'name', {'_ver': 12}, (TypeVar,
r'''T'''),
r'''**ValueError('cannot delete TypeVar.name')**''',
"\n'T'\n",
r'''<class 'str'>'''),

(250, '', None, False, 'bound', {'_ver': 12}, (TypeVar,
r'''T: int'''),
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

(251, '', None, False, 'bound', {'_ver': 12}, (TypeVar,
r'''T'''),
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
''',
r'''**None**'''),

(252, '', None, False, 'default_value', {'_ver': 13}, (TypeVar,
r'''T: int = bool'''),
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
''',
r'''bool''',
r'''Name 'bool' Load - ROOT 0,0..0,4'''),

(253, '', None, False, 'default_value', {'_ver': 13}, (TypeVar,
r'''T'''),
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
''',
r'''**None**'''),

(254, '', None, False, 'name', {'_ver': 12}, (ParamSpec,
r'''**V'''),
r'''**ValueError('cannot delete ParamSpec.name')**''',
"\n'V'\n",
r'''<class 'str'>'''),

(255, '', None, False, 'default_value', {'_ver': 13}, (ParamSpec,
r'''**V = {}'''),
r'''**V''', r'''
ParamSpec - ROOT 0,0..0,3
  .name 'V'
''',
r'''{}''',
r'''Dict - ROOT 0,0..0,2'''),

(256, '', None, False, 'default_value', {'_ver': 13}, (ParamSpec,
r'''**V'''),
r'''**V''', r'''
ParamSpec - ROOT 0,0..0,3
  .name 'V'
''',
r'''**None**'''),

(257, '', None, False, 'name', {'_ver': 12}, (TypeVarTuple,
r'''*U'''),
r'''**ValueError('cannot delete TypeVarTuple.name')**''',
"\n'U'\n",
r'''<class 'str'>'''),

(258, '', None, False, 'default_value', {'_ver': 13}, (TypeVarTuple,
r'''*U = ()'''),
r'''*U''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'U'
''',
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
'''),

(259, '', None, False, 'default_value', {'_ver': 13}, (TypeVarTuple,
r'''*U'''),
r'''*U''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'U'
''',
r'''**None**'''),
],

'arglike': [  # ................................................................................

(0, '', 0, False, 'bases', {}, (ClassDef,
r'''class cls(*a): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
  0] Pass - 0,11..0,15
''',
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(1, '', 0, False, 'bases', {}, (ClassDef,
r'''class cls(*not a): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
  0] Pass - 0,11..0,15
''',
r'''*(not a)''', r'''
Starred - ROOT 0,0..0,8
  .value UnaryOp - 0,2..0,7
    .op Not - 0,2..0,5
    .operand Name 'a' Load - 0,6..0,7
  .ctx Load
'''),

(2, '', 0, False, 'bases', {'pars': False}, (ClassDef,
r'''class cls(*not a): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
  0] Pass - 0,11..0,15
''',
r'''*not a''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(3, '', 0, False, 'bases', {'pars_arglike': False}, (ClassDef,
r'''class cls(*not a): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
  0] Pass - 0,11..0,15
''',
r'''*not a''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(4, '', 0, False, 'args', {}, (Call,
r'''call(*a)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(5, '', 0, False, 'args', {}, (Call,
r'''call(*not a)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''*(not a)''', r'''
Starred - ROOT 0,0..0,8
  .value UnaryOp - 0,2..0,7
    .op Not - 0,2..0,5
    .operand Name 'a' Load - 0,6..0,7
  .ctx Load
'''),

(6, '', 0, False, 'args', {'pars': False}, (Call,
r'''call(*not a)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''*not a''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(7, 'slice', 0, False, 'elts', {'_ver': 11}, (Subscript,
r'''sub[*a]'''),
r'''sub[()]''', r'''
Subscript - ROOT 0,0..0,7
  .value Name 'sub' Load - 0,0..0,3
  .slice Tuple - 0,4..0,6
    .ctx Load
  .ctx Load
''',
r'''*a''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),

(8, 'slice', 0, False, 'elts', {'_ver': 11}, (Subscript,
r'''sub[*not a]'''),
r'''sub[()]''', r'''
Subscript - ROOT 0,0..0,7
  .value Name 'sub' Load - 0,0..0,3
  .slice Tuple - 0,4..0,6
    .ctx Load
  .ctx Load
''',
r'''*(not a)''', r'''
Starred - ROOT 0,0..0,8
  .value UnaryOp - 0,2..0,7
    .op Not - 0,2..0,5
    .operand Name 'a' Load - 0,6..0,7
  .ctx Load
'''),

(9, 'slice', 0, False, 'elts', {'_ver': 11, 'pars': False}, (Subscript,
r'''sub[*not a]'''),
r'''sub[()]''', r'''
Subscript - ROOT 0,0..0,7
  .value Name 'sub' Load - 0,0..0,3
  .slice Tuple - 0,4..0,6
    .ctx Load
  .ctx Load
''',
r'''*not a''', r'''
Starred - ROOT 0,0..0,6
  .value UnaryOp - 0,1..0,6
    .op Not - 0,1..0,4
    .operand Name 'a' Load - 0,5..0,6
  .ctx Load
'''),

(10, '', None, False, 'slice', {'_ver': 11}, (Subscript,
r'''sub[*not a, b, *c or d, *e]'''),
r'''**ValueError('cannot delete Subscript.slice')**''',
r'''*(not a), b, *(c or d), *e''', r'''
Tuple - ROOT 0,0..0,26
  .elts[4]
  0] Starred - 0,0..0,8
    .value UnaryOp - 0,2..0,7
      .op Not - 0,2..0,5
      .operand Name 'a' Load - 0,6..0,7
    .ctx Load
  1] Name 'b' Load - 0,10..0,11
  2] Starred - 0,13..0,22
    .value BoolOp - 0,15..0,21
      .op Or
      .values[2]
      0] Name 'c' Load - 0,15..0,16
      1] Name 'd' Load - 0,20..0,21
    .ctx Load
  3] Starred - 0,24..0,26
    .value Name 'e' Load - 0,25..0,26
    .ctx Load
  .ctx Load
'''),

(11, '', None, False, 'slice', {'_ver': 11, 'pars': False}, (Subscript,
r'''sub[*not a, b, *c or d, *e]'''),
r'''**ValueError('cannot delete Subscript.slice')**''',
r'''*not a, b, *c or d, *e''', r'''
Tuple - ROOT 0,0..0,22
  .elts[4]
  0] Starred - 0,0..0,6
    .value UnaryOp - 0,1..0,6
      .op Not - 0,1..0,4
      .operand Name 'a' Load - 0,5..0,6
    .ctx Load
  1] Name 'b' Load - 0,8..0,9
  2] Starred - 0,11..0,18
    .value BoolOp - 0,12..0,18
      .op Or
      .values[2]
      0] Name 'c' Load - 0,12..0,13
      1] Name 'd' Load - 0,17..0,18
    .ctx Load
  3] Starred - 0,20..0,22
    .value Name 'e' Load - 0,21..0,22
    .ctx Load
  .ctx Load
'''),
],

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
