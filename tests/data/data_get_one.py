# (attr, start, False, field, options, code | (parse_mode, code),
#
# code after cut,
# dump code after cut)
# - OR
# error)

from fst.asttypes import *

DATA_GET_ONE = {
'all_basic': [  # ................................................................................

('', 0, None, 'body', {}, (Module,
r'''a = 1'''),
r'''''',
r'''Module - ROOT 0,0..0,0''',
r'''a = 1''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (Interactive,
r'''a = 1'''),
r'''''',
r'''Interactive - ROOT 0,0..0,0''',
r'''a = 1''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

('', None, None, 'body', {}, (Expression,
r'''a'''),
r'''**ValueError('cannot delete Expression.body')**''',
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', None, None, 'decorator_list', {}, (FunctionDef, r'''
@deco
def func(): pass

'''), r'''
def func(): pass

''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
   0] Pass - 0,12..0,16
''',
r'''@deco''', r'''
_decorator_list - ROOT 0,0..0,5
  .decorator_list[1]
   0] Name 'deco' Load - 0,1..0,5
'''),

('', None, None, 'name', {}, (FunctionDef,
r'''def func(): pass'''),
r'''**ValueError('cannot delete FunctionDef.name')**''',
"\n'func'\n",
r'''<class 'str'>'''),

('', 0, None, 'type_params', {'_ver': 12}, (FunctionDef,
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

('', None, None, 'args', {}, (FunctionDef,
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

('', None, None, 'args', {}, (FunctionDef,
r'''def func(): pass'''),
r'''def func(): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
   0] Pass - 0,12..0,16
''',
r'''''',
r'''arguments - ROOT 0,0..0,0'''),

('', None, None, 'returns', {}, (FunctionDef,
r'''def func() -> int: pass'''),
r'''def func(): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
   0] Pass - 0,12..0,16
''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

('', None, None, 'returns', {}, (FunctionDef,
r'''def func(): pass'''),
r'''def func(): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'func'
  .body[1]
   0] Pass - 0,12..0,16
''',
r'''**None**'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (FunctionDef,
r'''def func(): pass'''),
r'''def func():''', r'''
FunctionDef - ROOT 0,0..0,11
  .name 'func'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', 0, None, 'decorator_list', {}, (AsyncFunctionDef, r'''
@deco
async def func(): pass

'''), r'''
async def func(): pass

''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
   0] Pass - 0,18..0,22
''',
r'''deco''',
r'''Name 'deco' Load - ROOT 0,0..0,4'''),

('', None, None, 'name', {}, (AsyncFunctionDef,
r'''async def func(): pass'''),
r'''**ValueError('cannot delete AsyncFunctionDef.name')**''',
"\n'func'\n",
r'''<class 'str'>'''),

('', 0, None, 'type_params', {'_ver': 12}, (AsyncFunctionDef,
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

('', None, None, 'args', {}, (AsyncFunctionDef,
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

('', None, None, 'args', {}, (AsyncFunctionDef,
r'''async def func(): pass'''),
r'''async def func(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
   0] Pass - 0,18..0,22
''',
r'''''',
r'''arguments - ROOT 0,0..0,0'''),

('', None, None, 'returns', {}, (AsyncFunctionDef,
r'''async def func() -> int: pass'''),
r'''async def func(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
   0] Pass - 0,18..0,22
''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

('', None, None, 'returns', {}, (AsyncFunctionDef,
r'''async def func(): pass'''),
r'''async def func(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,22
  .name 'func'
  .body[1]
   0] Pass - 0,18..0,22
''',
r'''**None**'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (AsyncFunctionDef,
r'''async def func(): pass'''),
r'''async def func():''', r'''
AsyncFunctionDef - ROOT 0,0..0,17
  .name 'func'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', 0, None, 'decorator_list', {}, (ClassDef, r'''
@deco
class cls: pass

'''), r'''
class cls: pass

''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''deco''',
r'''Name 'deco' Load - ROOT 0,0..0,4'''),

('', None, None, 'name', {}, (ClassDef,
r'''class cls: pass'''),
r'''**ValueError('cannot delete ClassDef.name')**''',
"\n'cls'\n",
r'''<class 'str'>'''),

('', 0, None, 'type_params', {'_ver': 12}, (ClassDef,
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

('', 0, None, 'bases', {}, (ClassDef,
r'''class cls(base): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''base''',
r'''Name 'base' Load - ROOT 0,0..0,4'''),

('', 0, None, 'keywords', {}, (ClassDef,
r'''class cls(key=val): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''key=val''', r'''
keyword - ROOT 0,0..0,7
  .arg 'key'
  .value Name 'val' Load - 0,4..0,7
'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (ClassDef,
r'''class cls(): pass'''),
r'''class cls():''', r'''
ClassDef - ROOT 0,0..0,12
  .name 'cls'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', None, None, 'value', {}, (Return,
r'''return ret'''),
r'''return''',
r'''Return - ROOT 0,0..0,6''',
r'''ret''',
r'''Name 'ret' Load - ROOT 0,0..0,3'''),

('', 0, None, 'targets', {'norm': True}, (Delete,
r'''del var'''),
r'''**ValueError('cannot delete all Delete.targets without norm_self=False')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', 0, None, 'targets', {'_verify_self': False, 'norm_self': False}, (Delete,
r'''del var'''),
r'''del ''',
r'''Delete - ROOT 0,0..0,4''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', 0, None, 'targets', {'norm': True}, (Assign,
r'''var = val'''),
r'''**ValueError('cannot delete all Assign.targets without norm_self=False')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', 0, None, 'targets', {'_verify_self': False, 'norm_self': False}, (Assign,
r'''var = val'''),
r''' val''', r'''
Assign - ROOT 0,0..0,4
  .value Name 'val' Load - 0,1..0,4
''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', None, None, 'value', {}, (Assign,
r'''var = val'''),
r'''**ValueError('cannot delete Assign.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'name', {'_ver': 12}, (TypeAlias,
r'''type t[T] = ...'''),
r'''**ValueError('cannot delete TypeAlias.name')**''',
r'''t''',
r'''Name 't' Load - ROOT 0,0..0,1'''),

('', 0, None, 'type_params', {'_ver': 12}, (TypeAlias,
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

('', None, None, 'value', {'_ver': 12}, (TypeAlias,
r'''type t[T] = ...'''),
r'''**ValueError('cannot delete TypeAlias.value')**''',
r'''...''',
r'''Constant Ellipsis - ROOT 0,0..0,3'''),

('', None, None, 'target', {}, (AugAssign,
r'''var += 123'''),
r'''**ValueError('cannot delete AugAssign.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', None, None, 'op', {}, (AugAssign,
r'''var += 123'''),
r'''**ValueError('cannot delete AugAssign.op')**''',
r'''+''',
r'''Add - ROOT 0,0..0,1'''),

('', None, None, 'value', {}, (AugAssign,
r'''var += 123'''),
r'''**ValueError('cannot delete AugAssign.value')**''',
r'''123''',
r'''Constant 123 - ROOT 0,0..0,3'''),

('', None, None, 'target', {}, (AnnAssign,
r'''var: int = 123'''),
r'''**ValueError('cannot delete AnnAssign.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', None, None, 'annotation', {}, (AnnAssign,
r'''var: int = 123'''),
r'''**ValueError('cannot delete AnnAssign.annotation')**''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

('', None, None, 'value', {}, (AnnAssign,
r'''var: int = 123'''),
r'''var: int''', r'''
AnnAssign - ROOT 0,0..0,8
  .target Name 'var' Store - 0,0..0,3
  .annotation Name 'int' Load - 0,5..0,8
  .simple 1
''',
r'''123''',
r'''Constant 123 - ROOT 0,0..0,3'''),

('', None, None, 'simple', {}, (AnnAssign,
r'''var: int = 123'''),
r'''**ValueError('cannot delete AnnAssign.simple')**''',
r'''1''',
r'''<class 'int'>'''),

('', None, None, 'target', {}, (For,
r'''for var in iter(): pass'''),
r'''**ValueError('cannot delete For.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', None, None, 'iter', {}, (For,
r'''for var in iter(): pass'''),
r'''**ValueError('cannot delete For.iter')**''',
r'''iter()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'iter' Load - 0,0..0,4
'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (For,
r'''for var in iter(): pass'''),
r'''for var in iter():''', r'''
For - ROOT 0,0..0,18
  .target Name 'var' Store - 0,4..0,7
  .iter Call - 0,11..0,17
    .func Name 'iter' Load - 0,11..0,15
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', 0, None, 'orelse', {}, (For, r'''
for var in iter(): pass
else: continue
'''),
r'''for var in iter(): pass''', r'''
For - ROOT 0,0..0,23
  .target Name 'var' Store - 0,4..0,7
  .iter Call - 0,11..0,17
    .func Name 'iter' Load - 0,11..0,15
  .body[1]
   0] Pass - 0,19..0,23
''',
r'''continue''',
r'''Continue - ROOT 0,0..0,8'''),

('', None, None, 'target', {}, (AsyncFor,
r'''async for var in iter(): pass'''),
r'''**ValueError('cannot delete AsyncFor.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', None, None, 'iter', {}, (AsyncFor,
r'''async for var in iter(): pass'''),
r'''**ValueError('cannot delete AsyncFor.iter')**''',
r'''iter()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'iter' Load - 0,0..0,4
'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (AsyncFor,
r'''async for var in iter(): pass'''),
r'''async for var in iter():''', r'''
AsyncFor - ROOT 0,0..0,24
  .target Name 'var' Store - 0,10..0,13
  .iter Call - 0,17..0,23
    .func Name 'iter' Load - 0,17..0,21
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', 0, None, 'orelse', {}, (AsyncFor, r'''
async for var in iter(): pass
else: continue
'''),
r'''async for var in iter(): pass''', r'''
AsyncFor - ROOT 0,0..0,29
  .target Name 'var' Store - 0,10..0,13
  .iter Call - 0,17..0,23
    .func Name 'iter' Load - 0,17..0,21
  .body[1]
   0] Pass - 0,25..0,29
''',
r'''continue''',
r'''Continue - ROOT 0,0..0,8'''),

('', None, None, 'test', {}, (While,
r'''while var: pass'''),
r'''**ValueError('cannot delete While.test')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (While,
r'''while var: pass'''),
r'''while var:''', r'''
While - ROOT 0,0..0,10
  .test Name 'var' Load - 0,6..0,9
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', 0, None, 'orelse', {}, (While, r'''
while var: pass
else: continue
'''),
r'''while var: pass''', r'''
While - ROOT 0,0..0,15
  .test Name 'var' Load - 0,6..0,9
  .body[1]
   0] Pass - 0,11..0,15
''',
r'''continue''',
r'''Continue - ROOT 0,0..0,8'''),

('', None, None, 'test', {}, (If,
r'''if var: pass'''),
r'''**ValueError('cannot delete If.test')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (If,
r'''if var: pass'''),
r'''if var:''', r'''
If - ROOT 0,0..0,7
  .test Name 'var' Load - 0,3..0,6
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', 0, None, 'orelse', {}, (If, r'''
if var: pass
else: continue
'''),
r'''if var: pass''', r'''
If - ROOT 0,0..0,12
  .test Name 'var' Load - 0,3..0,6
  .body[1]
   0] Pass - 0,8..0,12
''',
r'''continue''',
r'''Continue - ROOT 0,0..0,8'''),

('', 0, None, 'items', {'_verify_self': False, 'norm': True}, (With,
r'''with var: pass'''),
r'''**ValueError('cannot delete all With.items without norm_self=False')**''',
r'''var''', r'''
withitem - ROOT 0,0..0,3
  .context_expr Name 'var' Load - 0,0..0,3
'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (With,
r'''with var: pass'''),
r'''with var:''', r'''
With - ROOT 0,0..0,9
  .items[1]
   0] withitem - 0,5..0,8
     .context_expr Name 'var' Load - 0,5..0,8
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', 0, None, 'items', {'_verify_self': False, 'norm': True}, (AsyncWith,
r'''async with var: pass'''),
r'''**ValueError('cannot delete all AsyncWith.items without norm_self=False')**''',
r'''var''', r'''
withitem - ROOT 0,0..0,3
  .context_expr Name 'var' Load - 0,0..0,3
'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (AsyncWith,
r'''async with var: pass'''),
r'''async with var:''', r'''
AsyncWith - ROOT 0,0..0,15
  .items[1]
   0] withitem - 0,11..0,14
     .context_expr Name 'var' Load - 0,11..0,14
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', None, None, 'subject', {}, (Match, r'''
match var:
  case 1: pass
'''),
r'''**ValueError('cannot delete Match.subject')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', 0, None, 'cases', {'_verify_self': False, 'norm': False}, (Match, r'''
match var:
  case 1: pass
'''),
r'''match var:''', r'''
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

('', None, None, 'exc', {}, (Raise,
r'''raise exc'''),
r'''raise''',
r'''Raise - ROOT 0,0..0,5''',
r'''exc''',
r'''Name 'exc' Load - ROOT 0,0..0,3'''),

('', None, None, 'exc', {}, (Raise,
r'''raise exc from cause'''),
r'''**ValueError('cannot delete Raise.exc in this state')**''',
r'''exc''',
r'''Name 'exc' Load - ROOT 0,0..0,3'''),

('', None, None, 'cause', {}, (Raise,
r'''raise exc from cause'''),
r'''raise exc''', r'''
Raise - ROOT 0,0..0,9
  .exc Name 'exc' Load - 0,6..0,9
''',
r'''cause''',
r'''Name 'cause' Load - ROOT 0,0..0,5'''),

('', None, None, 'cause', {}, (Raise,
r'''raise exc'''),
r'''raise exc''', r'''
Raise - ROOT 0,0..0,9
  .exc Name 'exc' Load - 0,6..0,9
''',
r'''**None**'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (Try, r'''
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

('', 0, None, 'handlers', {'_verify_self': False, 'norm': False}, (Try, r'''
try: pass
except Exception: continue
'''),
r'''try: pass''', r'''
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

('', 0, None, 'orelse', {}, (Try, r'''
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

('', 0, None, 'finalbody', {}, (Try, r'''
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

('', 0, None, 'body', {'_ver': 11, '_verify_self': False, 'norm': False}, (TryStar, r'''
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

('', 0, None, 'handlers', {'_ver': 11, '_verify_self': False, 'norm': False}, (TryStar, r'''
try: pass
except* Exception: continue
'''),
r'''try: pass''', r'''
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

('', 0, None, 'orelse', {'_ver': 11}, (TryStar, r'''
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

('', 0, None, 'finalbody', {'_ver': 11}, (TryStar, r'''
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

('', None, None, 'test', {}, (Assert,
r'''assert condition, message'''),
r'''**ValueError('cannot delete Assert.test')**''',
r'''condition''',
r'''Name 'condition' Load - ROOT 0,0..0,9'''),

('', None, None, 'msg', {}, (Assert,
r'''assert condition, message'''),
r'''assert condition''', r'''
Assert - ROOT 0,0..0,16
  .test Name 'condition' Load - 0,7..0,16
''',
r'''message''',
r'''Name 'message' Load - ROOT 0,0..0,7'''),

('', None, None, 'msg', {}, (Assert,
r'''assert condition'''),
r'''assert condition''', r'''
Assert - ROOT 0,0..0,16
  .test Name 'condition' Load - 0,7..0,16
''',
r'''**None**'''),

('', 0, None, 'names', {'norm': True}, (Import,
r'''import mod'''),
r'''**ValueError('cannot delete all Import.names without norm_self=False')**''',
r'''mod''', r'''
alias - ROOT 0,0..0,3
  .name 'mod'
'''),

('', 0, None, 'names', {'_verify_self': False, 'norm_self': False}, (Import,
r'''import mod'''),
r'''import ''',
r'''Import - ROOT 0,0..0,7''',
r'''mod''', r'''
alias - ROOT 0,0..0,3
  .name 'mod'
'''),

('', None, None, 'module', {}, (ImportFrom,
r'''from mod import name'''),
r'''**ValueError('cannot delete ImportFrom.module in this state')**''',
"\n'mod'\n",
r'''<class 'str'>'''),

('', None, None, 'module', {}, (ImportFrom,
r'''from . import name'''),
r'''from . import name''', r'''
ImportFrom - ROOT 0,0..0,18
  .names[1]
   0] alias - 0,14..0,18
     .name 'name'
  .level 1
''',
r'''**None**'''),

('', None, None, 'module', {}, (ImportFrom,
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

('', 0, None, 'names', {'norm': True}, (ImportFrom,
r'''from mod import name'''),
r'''**ValueError('cannot delete all ImportFrom.names without norm_self=False')**''',
r'''name''', r'''
alias - ROOT 0,0..0,4
  .name 'name'
'''),

('', 0, None, 'names', {'_verify_self': False, 'norm_self': False}, (ImportFrom,
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

('', None, None, 'level', {}, (ImportFrom,
r'''from mod import name'''),
r'''**ValueError('cannot delete ImportFrom.level')**''',
r'''0''',
r'''<class 'int'>'''),

('', 0, None, 'names', {'norm': True}, (Global,
r'''global var'''),
r'''**ValueError('cannot delete all Global.names without norm_self=False')**''',
"\n'var'\n",
r'''<class 'str'>'''),

('', 0, None, 'names', {'_verify_self': False, 'norm_self': False}, (Global,
r'''global var'''),
r'''global ''',
r'''Global - ROOT 0,0..0,7''',
"\n'var'\n",
r'''<class 'str'>'''),

('', 0, None, 'names', {'norm': True}, (Nonlocal,
r'''nonlocal var'''),
r'''**ValueError('cannot delete all Nonlocal.names without norm_self=False')**''',
"\n'var'\n",
r'''<class 'str'>'''),

('', 0, None, 'names', {'_verify_self': False, 'norm_self': False}, (Nonlocal,
r'''nonlocal var'''),
r'''nonlocal ''',
r'''Nonlocal - ROOT 0,0..0,9''',
"\n'var'\n",
r'''<class 'str'>'''),

('', None, None, 'value', {}, (Expr,
r'''val'''),
r'''**ValueError('cannot delete Expr.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'op', {}, (BoolOp,
r'''val1 and val2'''),
r'''**ValueError('cannot delete BoolOp.op')**''',
r'''and''',
r'''And - ROOT 0,0..0,3'''),

('', 0, None, 'values', {'norm': True}, (BoolOp,
r'''val1 and val2'''),
r'''val2''',
r'''Name 'val2' Load - ROOT 0,0..0,4''',
r'''val1''',
r'''Name 'val1' Load - ROOT 0,0..0,4'''),

('', 0, None, 'values', {'_verify_self': False, 'norm_self': False}, (BoolOp,
r'''val1 and val2'''),
r'''val2''', r'''
BoolOp - ROOT 0,0..0,4
  .op And
  .values[1]
   0] Name 'val2' Load - 0,0..0,4
''',
r'''val1''',
r'''Name 'val1' Load - ROOT 0,0..0,4'''),

('', None, None, 'target', {}, (NamedExpr,
r'''(var := val)'''),
r'''**ValueError('cannot delete NamedExpr.target')**''',
r'''var''',
r'''Name 'var' Load - ROOT 0,0..0,3'''),

('', None, None, 'value', {}, (NamedExpr,
r'''(var := val)'''),
r'''**ValueError('cannot delete NamedExpr.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'left', {}, (BinOp,
r'''val1 + val2'''),
r'''**ValueError('cannot delete BinOp.left')**''',
r'''val1''',
r'''Name 'val1' Load - ROOT 0,0..0,4'''),

('', None, None, 'op', {}, (BinOp,
r'''val1 + val2'''),
r'''**ValueError('cannot delete BinOp.op')**''',
r'''+''',
r'''Add - ROOT 0,0..0,1'''),

('', None, None, 'right', {}, (BinOp,
r'''val1 + val2'''),
r'''**ValueError('cannot delete BinOp.right')**''',
r'''val2''',
r'''Name 'val2' Load - ROOT 0,0..0,4'''),

('', None, None, 'op', {}, (UnaryOp,
r'''-val'''),
r'''**ValueError('cannot delete UnaryOp.op')**''',
r'''-''',
r'''USub - ROOT 0,0..0,1'''),

('', None, None, 'operand', {}, (UnaryOp,
r'''-val'''),
r'''**ValueError('cannot delete UnaryOp.operand')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'args', {}, (Lambda,
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

('', None, None, 'args', {}, (Lambda,
r'''lambda: None'''),
r'''lambda: None''', r'''
Lambda - ROOT 0,0..0,12
  .body Constant None - 0,8..0,12
''',
r'''''',
r'''arguments - ROOT 0,0..0,0'''),

('', None, None, 'body', {}, (Lambda,
r'''lambda: None'''),
r'''**ValueError('cannot delete Lambda.body')**''',
r'''None''',
r'''Constant None - ROOT 0,0..0,4'''),

('', None, None, 'body', {}, (IfExp,
r'''body if test else orelse'''),
r'''**ValueError('cannot delete IfExp.body')**''',
r'''body''',
r'''Name 'body' Load - ROOT 0,0..0,4'''),

('', None, None, 'test', {}, (IfExp,
r'''body if test else orelse'''),
r'''**ValueError('cannot delete IfExp.test')**''',
r'''test''',
r'''Name 'test' Load - ROOT 0,0..0,4'''),

('', None, None, 'orelse', {}, (IfExp,
r'''body if test else orelse'''),
r'''**ValueError('cannot delete IfExp.orelse')**''',
r'''orelse''',
r'''Name 'orelse' Load - ROOT 0,0..0,6'''),

('', 0, None, 'keys', {}, (Dict,
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

('', 0, None, 'keys', {}, (Dict,
r'''{**val}'''),
r'''{**val}''', r'''
Dict - ROOT 0,0..0,7
  .keys[1]
   0] None
  .values[1]
   0] Name 'val' Load - 0,3..0,6
''',
r'''**None**'''),

('', 0, None, 'values', {}, (Dict,
r'''{key: val}'''),
r'''**ValueError('cannot delete from Dict.values')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', 0, None, None, {}, (Dict,
r'''{key: val}'''),
r'''**ValueError('cannot get single element from Dict._all')**'''),

('', 0, None, 'elts', {}, (Set,
r'''{elt0, elt1}'''),
r'''{elt1}''', r'''
Set - ROOT 0,0..0,6
  .elts[1]
   0] Name 'elt1' Load - 0,1..0,5
''',
r'''elt0''',
r'''Name 'elt0' Load - ROOT 0,0..0,4'''),

('', 0, None, 'elts', {'norm': True}, (Set,
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

('', None, None, 'elt', {}, (ListComp,
r'''[val for val in iter]'''),
r'''**ValueError('cannot delete ListComp.elt')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', 0, None, 'generators', {'norm': True}, (ListComp,
r'''[val for val in iter]'''),
r'''**ValueError('cannot delete all ListComp.generators without norm_self=False')**''',
r'''for val in iter''', r'''
comprehension - ROOT 0,0..0,15
  .target Name 'val' Store - 0,4..0,7
  .iter Name 'iter' Load - 0,11..0,15
  .is_async 0
'''),

('', None, None, 'elt', {}, (SetComp,
r'''{val for val in iter}'''),
r'''**ValueError('cannot delete SetComp.elt')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', 0, None, 'generators', {'norm': True}, (SetComp,
r'''{val for val in iter}'''),
r'''**ValueError('cannot delete all SetComp.generators without norm_self=False')**''',
r'''for val in iter''', r'''
comprehension - ROOT 0,0..0,15
  .target Name 'val' Store - 0,4..0,7
  .iter Name 'iter' Load - 0,11..0,15
  .is_async 0
'''),

('', None, None, 'key', {}, (DictComp,
r'''{key: val for key, val in iter}'''),
r'''**ValueError('cannot delete DictComp.key')**''',
r'''key''',
r'''Name 'key' Load - ROOT 0,0..0,3'''),

('', None, None, 'value', {'_ver': -15}, (DictComp,
r'''{key: val for key, val in iter}'''),
r'''**ValueError('cannot delete DictComp.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'value', {'_ver': 15}, (DictComp,
r'''{key: val for key, val in iter}'''),
r'''{**key for key, val in iter}''', r'''
DictComp - ROOT 0,0..0,28
  .key Name 'key' Load - 0,3..0,6
  .generators[1]
   0] comprehension - 0,7..0,27
     .target Tuple - 0,11..0,19
       .elts[2]
        0] Name 'key' Store - 0,11..0,14
        1] Name 'val' Store - 0,16..0,19
       .ctx Store
     .iter Name 'iter' Load - 0,23..0,27
     .is_async 0
''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', 0, None, 'generators', {'norm': True}, (DictComp,
r'''{key: val for key, val in iter}'''),
r'''**ValueError('cannot delete all DictComp.generators without norm_self=False')**''',
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

('', None, None, 'elt', {}, (GeneratorExp,
r'''(val for val in iter)'''),
r'''**ValueError('cannot delete GeneratorExp.elt')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', 0, None, 'generators', {'norm': True}, (GeneratorExp,
r'''(val for val in iter)'''),
r'''**ValueError('cannot delete all GeneratorExp.generators without norm_self=False')**''',
r'''for val in iter''', r'''
comprehension - ROOT 0,0..0,15
  .target Name 'val' Store - 0,4..0,7
  .iter Name 'iter' Load - 0,11..0,15
  .is_async 0
'''),

('', None, None, 'value', {}, (Await,
r'''await val'''),
r'''**ValueError('cannot delete Await.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'value', {}, (Yield,
r'''yield val'''),
r'''yield''',
r'''Yield - ROOT 0,0..0,5''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'value', {}, (Yield,
r'''yield'''),
r'''yield''',
r'''Yield - ROOT 0,0..0,5''',
r'''**None**'''),

('', None, None, 'value', {}, (YieldFrom,
r'''yield from val'''),
r'''**ValueError('cannot delete YieldFrom.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'left', {}, (Compare,
r'''val0 < val1'''),
r'''**ValueError('cannot delete Compare.left')**''',
r'''val0''',
r'''Name 'val0' Load - ROOT 0,0..0,4'''),

('', 0, None, 'ops', {}, (Compare,
r'''val0 < val1'''),
r'''**ValueError('cannot delete from Compare.ops')**''',
r'''<''',
r'''Lt - ROOT 0,0..0,1'''),

('', 0, None, 'comparators', {}, (Compare,
r'''val0 < val1'''),
r'''**ValueError('cannot delete from Compare.comparators')**''',
r'''val1''',
r'''Name 'val1' Load - ROOT 0,0..0,4'''),

('', None, None, 'func', {}, (Call,
r'''call()'''),
r'''**ValueError('cannot delete Call.func')**''',
r'''call''',
r'''Name 'call' Load - ROOT 0,0..0,4'''),

('', 0, None, 'args', {}, (Call,
r'''call(arg)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''arg''',
r'''Name 'arg' Load - ROOT 0,0..0,3'''),

('', 0, None, 'keywords', {}, (Call,
r'''call(key=val)'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
''',
r'''key=val''', r'''
keyword - ROOT 0,0..0,7
  .arg 'key'
  .value Name 'val' Load - 0,4..0,7
'''),

('values[1]', None, None, 'value', {'_ver': 12}, (None,
r'''f"a{val:<16!r}c"'''),
r'''**ValueError('cannot delete FormattedValue.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('values[1]', None, None, 'conversion', {'_ver': 12}, (None,
r'''f"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
r'''**None**'''),

('values[1]', None, None, 'format_spec', {'_ver': 12}, (None,
r'''f"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
"\nf'<16!r'\n", r'''
JoinedStr - ROOT 0,0..0,8
  .values[1]
   0] Constant '<16!r' - 0,2..0,7
'''),

('', 0, None, 'values', {'_ver': 12}, (JoinedStr,
r'''f"a{val:<16!r}c"'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
"\n'a'\n",
r'''Constant 'a' - ROOT 0,0..0,3'''),

('', 1, None, 'values', {'_ver': 12}, (JoinedStr,
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

('values[1]', None, None, 'value', {'_ver': 14}, (None,
r'''t"a{val:<16!r}c"'''),
r'''**ValueError('cannot delete Interpolation.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('values[1]', None, None, 'str', {'_ver': 14}, (None,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
"\n'val'\n",
r'''<class 'str'>'''),

('values[1]', None, None, 'conversion', {'_ver': 14}, (None,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
r'''**None**'''),

('values[1]', None, None, 'format_spec', {'_ver': 14}, (None,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError('this is not implemented yet')**''',
"\nf'<16!r'\n", r'''
JoinedStr - ROOT 0,0..0,8
  .values[1]
   0] Constant '<16!r' - 0,2..0,7
'''),

('', 0, None, 'values', {'_ver': 14}, (TemplateStr,
r'''t"a{val:<16!r}c"'''),
r'''**NotImplementedError("not implemented yet, try with option raw='auto'")**''',
"\n'a'\n",
r'''Constant 'a' - ROOT 0,0..0,3'''),

('', 1, None, 'values', {'_ver': 14}, (TemplateStr,
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

('', None, None, 'value', {}, (Constant,
r'''...'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''Ellipsis''',
r'''<class 'ellipsis'>'''),

('', None, None, 'value', {}, (Constant,
r'''123'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''123''',
r'''<class 'int'>'''),

('', None, None, 'value', {}, (Constant,
r'''1.23'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''1.23''',
r'''<class 'float'>'''),

('', None, None, 'value', {}, (Constant,
r'''123j'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''123j''',
r'''<class 'complex'>'''),

('', None, None, 'value', {}, (Constant,
r'''"str"'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
"\n'str'\n",
r'''<class 'str'>'''),

('', None, None, 'value', {}, (Constant,
r'''b"123"'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
"\nb'123'\n",
r'''<class 'bytes'>'''),

('', None, None, 'value', {}, (Constant,
r'''True'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''True''',
r'''<class 'bool'>'''),

('', None, None, 'value', {}, (Constant,
r'''False'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''False''',
r'''<class 'bool'>'''),

('', None, None, 'value', {}, (Constant,
r'''None'''),
r'''None''',
r'''Constant None - ROOT 0,0..0,4''',
r'''**None**'''),

('', None, None, 'kind', {}, (Constant,
r'''1'''),
r'''**ValueError('cannot set kind of non-str Constant')**''',
r'''**None**'''),

('', None, None, 'kind', {}, (Constant,
r'''"str"'''),
r'''"str"''',
r'''Constant 'str' - ROOT 0,0..0,5''',
r'''**None**'''),

('', None, None, 'kind', {}, (Constant,
r'''u"str"'''),
r'''"str"''',
r'''Constant 'str' - ROOT 0,0..0,5''',
"\n'u'\n",
r'''<class 'str'>'''),

('', None, None, 'value', {}, (Attribute,
r'''val.attr'''),
r'''**ValueError('cannot delete Attribute.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'attr', {}, (Attribute,
r'''val.attr'''),
r'''**ValueError('cannot delete Attribute.attr')**''',
"\n'attr'\n",
r'''<class 'str'>'''),

('', None, None, 'ctx', {}, (Attribute,
r'''val.attr'''),
r'''**ValueError('cannot delete Attribute.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''val.attr = 1'''),
r'''**ValueError('cannot delete Attribute.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''del val.attr'''),
r'''**ValueError('cannot delete Attribute.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

('', None, None, 'value', {}, (Subscript,
r'''val[slice]'''),
r'''**ValueError('cannot delete Subscript.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'slice', {}, (Subscript,
r'''val[slice]'''),
r'''**ValueError('cannot delete Subscript.slice')**''',
r'''slice''',
r'''Name 'slice' Load - ROOT 0,0..0,5'''),

('', None, None, 'ctx', {}, (Subscript,
r'''val[slice]'''),
r'''**ValueError('cannot delete Subscript.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''val[slice] = 1'''),
r'''**ValueError('cannot delete Subscript.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''del val[slice]'''),
r'''**ValueError('cannot delete Subscript.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

('', None, None, 'value', {}, (Starred,
r'''*st'''),
r'''**ValueError('cannot delete Starred.value')**''',
r'''st''',
r'''Name 'st' Load - ROOT 0,0..0,2'''),

('', None, None, 'ctx', {}, (Starred,
r'''*st'''),
r'''**ValueError('cannot delete Starred.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('targets[0].elts[0]', None, None, 'ctx', {}, (None,
r'''*st, = 1'''),
r'''**ValueError('cannot delete Starred.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

('', None, None, 'id', {}, (Name,
r'''name'''),
r'''**ValueError('cannot delete Name.id')**''',
"\n'name'\n",
r'''<class 'str'>'''),

('', None, None, 'ctx', {}, (Name,
r'''name'''),
r'''**ValueError('cannot delete Name.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''name = 1'''),
r'''**ValueError('cannot delete Name.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''del name'''),
r'''**ValueError('cannot delete Name.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

('', None, None, 'elts', {}, (List,
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

('', None, None, 'ctx', {}, (List,
r'''[val]'''),
r'''**ValueError('cannot delete List.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''[val] = 1'''),
r'''**ValueError('cannot delete List.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''del [val]'''),
r'''**ValueError('cannot delete List.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

('', None, None, 'elts', {}, (Tuple,
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

('', None, None, 'ctx', {}, (Tuple,
r'''(val,)'''),
r'''**ValueError('cannot delete Tuple.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('', None, None, 'elts', {}, (Tuple,
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

('', None, None, 'ctx', {}, (Tuple,
r'''val,'''),
r'''**ValueError('cannot delete Tuple.ctx')**''',
r'''''',
r'''Load - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''val, = 1'''),
r'''**ValueError('cannot delete Tuple.ctx')**''',
r'''''',
r'''Store - ROOT 0,0..0,0'''),

('targets[0]', None, None, 'ctx', {}, (None,
r'''del val,'''),
r'''**ValueError('cannot delete Name.ctx')**''',
r'''''',
r'''Del - ROOT 0,0..0,0'''),

('', None, None, 'lower', {}, (Slice,
r'''lower:upper:step'''),
r''':upper:step''', r'''
Slice - ROOT 0,0..0,11
  .upper Name 'upper' Load - 0,1..0,6
  .step Name 'step' Load - 0,7..0,11
''',
r'''lower''',
r'''Name 'lower' Load - ROOT 0,0..0,5'''),

('', None, None, 'lower', {}, (Slice,
r''':'''),
r''':''',
r'''Slice - ROOT 0,0..0,1''',
r'''**None**'''),

('', None, None, 'upper', {}, (Slice,
r'''lower:upper:step'''),
r'''lower::step''', r'''
Slice - ROOT 0,0..0,11
  .lower Name 'lower' Load - 0,0..0,5
  .step Name 'step' Load - 0,7..0,11
''',
r'''upper''',
r'''Name 'upper' Load - ROOT 0,0..0,5'''),

('', None, None, 'upper', {}, (Slice,
r''':'''),
r''':''',
r'''Slice - ROOT 0,0..0,1''',
r'''**None**'''),

('', None, None, 'step', {}, (Slice,
r'''lower:upper:step'''),
r'''lower:upper:''', r'''
Slice - ROOT 0,0..0,12
  .lower Name 'lower' Load - 0,0..0,5
  .upper Name 'upper' Load - 0,6..0,11
''',
r'''step''',
r'''Name 'step' Load - ROOT 0,0..0,4'''),

('', None, None, 'step', {}, (Slice,
r''':'''),
r''':''',
r'''Slice - ROOT 0,0..0,1''',
r'''**None**'''),

('', None, None, 'target', {}, (comprehension,
r'''for val in iter if not val'''),
r'''**ValueError('cannot delete comprehension.target')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'iter', {}, (comprehension,
r'''for val in iter if not val'''),
r'''**ValueError('cannot delete comprehension.iter')**''',
r'''iter''',
r'''Name 'iter' Load - ROOT 0,0..0,4'''),

('', 0, None, 'ifs', {}, (comprehension,
r'''for val in iter if not val'''),
r'''for val in iter''', r'''
comprehension - ROOT 0,0..0,15
  .target Name 'val' Store - 0,4..0,7
  .iter Name 'iter' Load - 0,11..0,15
  .is_async 0
''',
r'''not val''', r'''
UnaryOp - ROOT 0,0..0,7
  .op Not - 0,0..0,3
  .operand Name 'val' Load - 0,4..0,7
'''),

('', None, None, 'is_async', {}, (comprehension,
r'''for val in iter if not val'''),
r'''**ValueError('cannot delete comprehension.is_async')**''',
r'''0''',
r'''<class 'int'>'''),

('', None, None, 'is_async', {}, (comprehension,
r'''async for val in iter if not val'''),
r'''**ValueError('cannot delete comprehension.is_async')**''',
r'''1''',
r'''<class 'int'>'''),

('', None, None, 'type', {}, (ExceptHandler,
r'''except Exception: pass'''),
r'''except: pass''', r'''
ExceptHandler - ROOT 0,0..0,12
  .body[1]
   0] Pass - 0,8..0,12
''',
r'''Exception''',
r'''Name 'Exception' Load - ROOT 0,0..0,9'''),

('', None, None, 'type', {}, (ExceptHandler,
r'''except Exception as exc: pass'''),
r'''**ValueError('cannot delete ExceptHandler.type in this state')**''',
r'''Exception''',
r'''Name 'Exception' Load - ROOT 0,0..0,9'''),

('', None, None, 'name', {}, (ExceptHandler,
r'''except Exception as exc: pass'''),
r'''except Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,22
  .type Name 'Exception' Load - 0,7..0,16
  .body[1]
   0] Pass - 0,18..0,22
''',
"\n'exc'\n",
r'''<class 'str'>'''),

('', None, None, 'name', {}, (ExceptHandler,
r'''except Exception: pass'''),
r'''except Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,22
  .type Name 'Exception' Load - 0,7..0,16
  .body[1]
   0] Pass - 0,18..0,22
''',
r'''**None**'''),

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (ExceptHandler,
r'''except Exception as exc: pass'''),
r'''except Exception as exc:''', r'''
ExceptHandler - ROOT 0,0..0,24
  .type Name 'Exception' Load - 0,7..0,16
  .name 'exc'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', None, None, 'type', {'_ver': 11}, (ExceptHandler,
r'''except* Exception: pass'''),
r'''**ValueError('cannot delete ExceptHandler.type in this state')**''',
r'''Exception''',
r'''Name 'Exception' Load - ROOT 0,0..0,9'''),

('', None, None, 'type', {'_ver': 11}, (ExceptHandler,
r'''except* Exception as exc: pass'''),
r'''**ValueError('cannot delete ExceptHandler.type in this state')**''',
r'''Exception''',
r'''Name 'Exception' Load - ROOT 0,0..0,9'''),

('', None, None, 'name', {'_ver': 11}, (ExceptHandler,
r'''except* Exception as exc: pass'''),
r'''except* Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,23
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
   0] Pass - 0,19..0,23
''',
"\n'exc'\n",
r'''<class 'str'>'''),

('', None, None, 'name', {'_ver': 11}, (ExceptHandler,
r'''except* Exception: pass'''),
r'''except* Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,23
  .type Name 'Exception' Load - 0,8..0,17
  .body[1]
   0] Pass - 0,19..0,23
''',
r'''**None**'''),

('', 0, None, 'body', {'_ver': 11, '_verify_self': False, 'norm': False}, (ExceptHandler,
r'''except* Exception as exc: pass'''),
r'''except* Exception as exc:''', r'''
ExceptHandler - ROOT 0,0..0,25
  .type Name 'Exception' Load - 0,8..0,17
  .name 'exc'
''',
r'''pass''',
r'''Pass - ROOT 0,0..0,4'''),

('', 0, None, 'posonlyargs', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''**ValueError('cannot delete from arguments.posonlyargs')**''',
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', 0, None, 'args', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''**ValueError('cannot delete from arguments.args')**''',
r'''b: int''', r'''
arg - ROOT 0,0..0,6
  .arg 'b'
  .annotation Name 'int' Load - 0,3..0,6
'''),

('', 0, None, 'defaults', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''**ValueError('cannot delete from arguments.defaults')**''',
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', None, None, 'vararg', {}, (arguments,
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

('', None, None, 'vararg', {}, (arguments,
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

('', 0, None, 'kwonlyargs', {}, (arguments,
r'''a, /, b: int = 1, *c, d=2, **e'''),
r'''**ValueError('cannot delete from arguments.kwonlyargs')**''',
r'''d''', r'''
arg - ROOT 0,0..0,1
  .arg 'd'
'''),

('', 0, None, 'kw_defaults', {}, (arguments,
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

('', None, None, 'kwarg', {}, (arguments,
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

('', None, None, 'kwarg', {}, (arguments,
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

('', None, None, 'arg', {}, (arg,
r'''arg: ann'''),
r'''**ValueError('cannot delete arg.arg')**''',
"\n'arg'\n",
r'''<class 'str'>'''),

('', None, None, 'annotation', {}, (arg,
r'''arg: ann'''),
r'''arg''', r'''
arg - ROOT 0,0..0,3
  .arg 'arg'
''',
r'''ann''',
r'''Name 'ann' Load - ROOT 0,0..0,3'''),

('', None, None, 'annotation', {}, (arg,
r'''arg'''),
r'''arg''', r'''
arg - ROOT 0,0..0,3
  .arg 'arg'
''',
r'''**None**'''),

('', None, None, 'arg', {}, (keyword,
r'''key=val'''),
r'''**val''', r'''
keyword - ROOT 0,0..0,5
  .value Name 'val' Load - 0,2..0,5
''',
"\n'key'\n",
r'''<class 'str'>'''),

('', None, None, 'value', {}, (keyword,
r'''key=val'''),
r'''**ValueError('cannot delete keyword.value')**''',
r'''val''',
r'''Name 'val' Load - ROOT 0,0..0,3'''),

('', None, None, 'name', {}, (alias,
r'''name as asname'''),
r'''**ValueError('cannot delete alias.name')**''',
"\n'name'\n",
r'''<class 'str'>'''),

('', None, None, 'asname', {}, (alias,
r'''name as asname'''),
r'''name''', r'''
alias - ROOT 0,0..0,4
  .name 'name'
''',
"\n'asname'\n",
r'''<class 'str'>'''),

('', None, None, 'asname', {}, (alias,
r'''name'''),
r'''name''', r'''
alias - ROOT 0,0..0,4
  .name 'name'
''',
r'''**None**'''),

('', None, None, 'context_expr', {}, (withitem,
r'''context as optional'''),
r'''**ValueError('cannot delete withitem.context_expr in this state')**''',
r'''context''',
r'''Name 'context' Load - ROOT 0,0..0,7'''),

('', None, None, 'optional_vars', {}, (withitem,
r'''context as optional'''),
r'''context''', r'''
withitem - ROOT 0,0..0,7
  .context_expr Name 'context' Load - 0,0..0,7
''',
r'''optional''',
r'''Name 'optional' Load - ROOT 0,0..0,8'''),

('', None, None, 'optional_vars', {}, (withitem,
r'''context'''),
r'''context''', r'''
withitem - ROOT 0,0..0,7
  .context_expr Name 'context' Load - 0,0..0,7
''',
r'''**None**'''),

('', None, None, 'pattern', {}, (match_case,
r'''case 1 as a if not a: pass'''),
r'''**ValueError('cannot delete match_case.pattern')**''',
r'''1 as a''', r'''
MatchAs - ROOT 0,0..0,6
  .pattern MatchValue - 0,0..0,1
    .value Constant 1 - 0,0..0,1
  .name 'a'
'''),

('', None, None, 'guard', {}, (match_case,
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

('', None, None, 'guard', {}, (match_case,
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

('', 0, None, 'body', {'_verify_self': False, 'norm': False}, (match_case,
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

('', None, None, 'value', {}, (MatchValue,
r'''123'''),
r'''**ValueError('cannot delete MatchValue.value')**''',
r'''123''',
r'''Constant 123 - ROOT 0,0..0,3'''),

('', None, None, 'value', {}, (MatchSingleton,
r'''True'''),
r'''None''',
r'''MatchSingleton None - ROOT 0,0..0,4''',
r'''True''',
r'''<class 'bool'>'''),

('', None, None, 'value', {}, (MatchSingleton,
r'''False'''),
r'''None''',
r'''MatchSingleton None - ROOT 0,0..0,4''',
r'''False''',
r'''<class 'bool'>'''),

('', None, None, 'value', {}, (MatchSingleton,
r'''None'''),
r'''None''',
r'''MatchSingleton None - ROOT 0,0..0,4''',
r'''**None**'''),

('', 0, None, 'patterns', {}, (MatchSequence,
r'''[a]'''),
r'''[]''',
r'''MatchSequence - ROOT 0,0..0,2''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, None, 'keys', {}, (MatchMapping,
r'''{1: a, **rest}'''),
r'''**ValueError('cannot delete from MatchMapping.keys')**''',
r'''1''',
r'''Constant 1 - ROOT 0,0..0,1'''),

('', 0, None, 'patterns', {}, (MatchMapping,
r'''{1: a, **rest}'''),
r'''**ValueError('cannot delete from MatchMapping.patterns')**''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', None, None, 'rest', {}, (MatchMapping,
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

('', None, None, 'rest', {}, (MatchMapping,
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

('', 0, None, None, {}, (MatchMapping,
r'''{1: a, **rest}'''),
r'''**ValueError('cannot get single element from MatchMapping._all')**'''),

('', None, None, 'cls', {}, (MatchClass,
r'''cls(a, b=c)'''),
r'''**ValueError('cannot delete MatchClass.cls')**''',
r'''cls''',
r'''Name 'cls' Load - ROOT 0,0..0,3'''),

('', 0, None, 'patterns', {}, (MatchClass,
r'''cls(a, b=c)'''),
r'''cls(b=c)''', r'''
MatchClass - ROOT 0,0..0,8
  .cls Name 'cls' Load - 0,0..0,3
  .kwd_attrs[1]
   0] 'b'
  .kwd_patterns[1]
   0] MatchAs - 0,6..0,7
     .name 'c'
''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', 0, None, 'kwd_attrs', {}, (MatchClass,
r'''cls(a, b=c)'''),
r'''**ValueError('cannot delete from MatchClass.kwd_attrs')**''',
"\n'b'\n",
r'''<class 'str'>'''),

('', 0, None, 'kwd_patterns', {}, (MatchClass,
r'''cls(a, b=c)'''),
r'''**ValueError('cannot delete from MatchClass.kwd_patterns')**''',
r'''c''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'c'
'''),

('', None, None, 'name', {}, (MatchStar,
r'''*st'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2''',
"\n'st'\n",
r'''<class 'str'>'''),

('', None, None, 'name', {}, (MatchStar,
r'''*_'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2''',
r'''**None**'''),

('', None, None, 'pattern', {}, (MatchAs,
r'''pat as name'''),
r'''name''', r'''
MatchAs - ROOT 0,0..0,4
  .name 'name'
''',
r'''pat''', r'''
MatchAs - ROOT 0,0..0,3
  .name 'pat'
'''),

('', None, None, 'pattern', {}, (MatchAs,
r'''name'''),
r'''name''', r'''
MatchAs - ROOT 0,0..0,4
  .name 'name'
''',
r'''**None**'''),

('', None, None, 'name', {}, (MatchAs,
r'''pat as name'''),
r'''**ValueError("cannot change MatchAs with pattern into wildcard '_'")**''',
"\n'name'\n",
r'''<class 'str'>'''),

('', 0, None, 'patterns', {}, (MatchOr,
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

('', 0, None, 'patterns', {'norm': True}, (MatchOr,
r'''a | b'''),
r'''b''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'b'
''',
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', None, None, 'name', {'_ver': 12}, (TypeVar,
r'''T'''),
r'''**ValueError('cannot delete TypeVar.name')**''',
"\n'T'\n",
r'''<class 'str'>'''),

('', None, None, 'bound', {'_ver': 12}, (TypeVar,
r'''T: int'''),
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

('', None, None, 'bound', {'_ver': 12}, (TypeVar,
r'''T'''),
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
''',
r'''**None**'''),

('', None, None, 'default_value', {'_ver': 13}, (TypeVar,
r'''T: int = bool'''),
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
''',
r'''bool''',
r'''Name 'bool' Load - ROOT 0,0..0,4'''),

('', None, None, 'default_value', {'_ver': 13}, (TypeVar,
r'''T'''),
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
''',
r'''**None**'''),

('', None, None, 'name', {'_ver': 12}, (ParamSpec,
r'''**V'''),
r'''**ValueError('cannot delete ParamSpec.name')**''',
"\n'V'\n",
r'''<class 'str'>'''),

('', None, None, 'default_value', {'_ver': 13}, (ParamSpec,
r'''**V = {}'''),
r'''**V''', r'''
ParamSpec - ROOT 0,0..0,3
  .name 'V'
''',
r'''{}''',
r'''Dict - ROOT 0,0..0,2'''),

('', None, None, 'default_value', {'_ver': 13}, (ParamSpec,
r'''**V'''),
r'''**V''', r'''
ParamSpec - ROOT 0,0..0,3
  .name 'V'
''',
r'''**None**'''),

('', None, None, 'name', {'_ver': 12}, (TypeVarTuple,
r'''*U'''),
r'''**ValueError('cannot delete TypeVarTuple.name')**''',
"\n'U'\n",
r'''<class 'str'>'''),

('', None, None, 'default_value', {'_ver': 13}, (TypeVarTuple,
r'''*U = ()'''),
r'''*U''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'U'
''',
r'''()''', r'''
Tuple - ROOT 0,0..0,2
  .ctx Load
'''),

('', None, None, 'default_value', {'_ver': 13}, (TypeVarTuple,
r'''*U'''),
r'''*U''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'U'
''',
r'''**None**'''),
],

'arglike': [  # ................................................................................

('', 0, None, 'bases', {}, (ClassDef,
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

('', 0, None, 'bases', {}, (ClassDef,
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

('', 0, None, 'bases', {'pars': False}, (ClassDef,
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

('', 0, None, 'bases', {'pars': False, 'pars_arglike': None}, (ClassDef,
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

('', 0, None, 'bases', {'pars_arglike': False}, (ClassDef,
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

('', 0, None, 'args', {}, (Call,
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

('', 0, None, 'args', {}, (Call,
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

('', 0, None, 'args', {'pars_arglike': False}, (Call,
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

('slice', 0, None, 'elts', {'_ver': 11}, (Subscript,
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

('slice', 0, None, 'elts', {'_ver': 11}, (Subscript,
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

('slice', 0, None, 'elts', {'_ver': 11, 'pars_arglike': False}, (Subscript,
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

('', None, None, 'slice', {'_ver': 11}, (Subscript,
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

('', None, None, 'slice', {'_ver': 11, 'pars': False}, (Subscript,
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

('', None, None, 'slice', {'_ver': 11, 'pars': False, 'pars_arglike': None}, (Subscript,
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

('', None, None, 'slice', {'_ver': 11, 'pars_arglike': False}, (Subscript,
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

('body[0]', 0, None, 'targets', {}, ('exec',
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

('body[0]', 1, None, 'targets', {}, ('exec',
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

('body[0]', 2, None, 'targets', {}, ('exec',
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

('body[0]', -1, None, 'targets', {}, ('exec',
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

('body[0]', -4, None, 'targets', {}, ('exec',
r'''a = (b, c) = d = z'''),
r'''**IndexError('index out of range')**'''),

('', 1, None, 'targets', {}, (None, r'''
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

('', 2, None, 'targets', {}, (None, r'''
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

('', 1, None, 'targets', {}, ('_Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
a = \
c \
= \

''', r'''
_Assign_targets - ROOT 0,0..3,0
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'c' Store - 1,0..1,1
''',
r'''b''',
r'''Name 'b' Load - ROOT 0,0..0,1'''),

('', 2, None, 'targets', {}, ('_Assign_targets', r'''
a = \
b = \
c \
= \

'''), r'''
a = \
b = \

''', r'''
_Assign_targets - ROOT 0,0..2,0
  .targets[2]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 1,0..1,1
''',
r'''c''',
r'''Name 'c' Load - ROOT 0,0..0,1'''),
],

'ClassDef__bases': [  # ................................................................................

('', 0, None, '_bases', {}, (None,
r'''class cls(base, meta=cls, *bases, **kws): pass'''),
r'''class cls(meta=cls, *bases, **kws): pass''', r'''
ClassDef - ROOT 0,0..0,40
  .name 'cls'
  .bases[1]
   0] Starred - 0,20..0,26
     .value Name 'bases' Load - 0,21..0,26
     .ctx Load
  .keywords[2]
   0] keyword - 0,10..0,18
     .arg 'meta'
     .value Name 'cls' Load - 0,15..0,18
   1] keyword - 0,28..0,33
     .value Name 'kws' Load - 0,30..0,33
  .body[1]
   0] Pass - 0,36..0,40
''',
r'''base''',
r'''Name 'base' Load - ROOT 0,0..0,4'''),

('', 1, None, '_bases', {}, (None,
r'''class cls(base, meta=cls, *bases, **kws): pass'''),
r'''class cls(base, *bases, **kws): pass''', r'''
ClassDef - ROOT 0,0..0,36
  .name 'cls'
  .bases[2]
   0] Name 'base' Load - 0,10..0,14
   1] Starred - 0,16..0,22
     .value Name 'bases' Load - 0,17..0,22
     .ctx Load
  .keywords[1]
   0] keyword - 0,24..0,29
     .value Name 'kws' Load - 0,26..0,29
  .body[1]
   0] Pass - 0,32..0,36
''',
r'''meta=cls''', r'''
keyword - ROOT 0,0..0,8
  .arg 'meta'
  .value Name 'cls' Load - 0,5..0,8
'''),

('', 2, None, '_bases', {}, (None,
r'''class cls(base, meta=cls, *bases, **kws): pass'''),
r'''class cls(base, meta=cls, **kws): pass''', r'''
ClassDef - ROOT 0,0..0,38
  .name 'cls'
  .bases[1]
   0] Name 'base' Load - 0,10..0,14
  .keywords[2]
   0] keyword - 0,16..0,24
     .arg 'meta'
     .value Name 'cls' Load - 0,21..0,24
   1] keyword - 0,26..0,31
     .value Name 'kws' Load - 0,28..0,31
  .body[1]
   0] Pass - 0,34..0,38
''',
r'''*bases''', r'''
Starred - ROOT 0,0..0,6
  .value Name 'bases' Load - 0,1..0,6
  .ctx Load
'''),

('', 3, None, '_bases', {}, (None,
r'''class cls(base, meta=cls, *bases, **kws): pass'''),
r'''class cls(base, meta=cls, *bases): pass''', r'''
ClassDef - ROOT 0,0..0,39
  .name 'cls'
  .bases[2]
   0] Name 'base' Load - 0,10..0,14
   1] Starred - 0,26..0,32
     .value Name 'bases' Load - 0,27..0,32
     .ctx Load
  .keywords[1]
   0] keyword - 0,16..0,24
     .arg 'meta'
     .value Name 'cls' Load - 0,21..0,24
  .body[1]
   0] Pass - 0,35..0,39
''',
r'''**kws''', r'''
keyword - ROOT 0,0..0,5
  .value Name 'kws' Load - 0,2..0,5
'''),
],

'Call__args': [  # ................................................................................

('', 0, None, '_args', {}, (None,
r'''call(arg, key=word, *args, **keywords)'''),
r'''call(key=word, *args, **keywords)''', r'''
Call - ROOT 0,0..0,33
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Starred - 0,15..0,20
     .value Name 'args' Load - 0,16..0,20
     .ctx Load
  .keywords[2]
   0] keyword - 0,5..0,13
     .arg 'key'
     .value Name 'word' Load - 0,9..0,13
   1] keyword - 0,22..0,32
     .value Name 'keywords' Load - 0,24..0,32
''',
r'''arg''',
r'''Name 'arg' Load - ROOT 0,0..0,3'''),

('', 1, None, '_args', {}, (None,
r'''call(arg, key=word, *args, **keywords)'''),
r'''call(arg, *args, **keywords)''', r'''
Call - ROOT 0,0..0,28
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'arg' Load - 0,5..0,8
   1] Starred - 0,10..0,15
     .value Name 'args' Load - 0,11..0,15
     .ctx Load
  .keywords[1]
   0] keyword - 0,17..0,27
     .value Name 'keywords' Load - 0,19..0,27
''',
r'''key=word''', r'''
keyword - ROOT 0,0..0,8
  .arg 'key'
  .value Name 'word' Load - 0,4..0,8
'''),

('', 2, None, '_args', {}, (None,
r'''call(arg, key=word, *args, **keywords)'''),
r'''call(arg, key=word, **keywords)''', r'''
Call - ROOT 0,0..0,31
  .func Name 'call' Load - 0,0..0,4
  .args[1]
   0] Name 'arg' Load - 0,5..0,8
  .keywords[2]
   0] keyword - 0,10..0,18
     .arg 'key'
     .value Name 'word' Load - 0,14..0,18
   1] keyword - 0,20..0,30
     .value Name 'keywords' Load - 0,22..0,30
''',
r'''*args''', r'''
Starred - ROOT 0,0..0,5
  .value Name 'args' Load - 0,1..0,5
  .ctx Load
'''),

('', 3, None, '_args', {}, (None,
r'''call(arg, key=word, *args, **keywords)'''),
r'''call(arg, key=word, *args)''', r'''
Call - ROOT 0,0..0,26
  .func Name 'call' Load - 0,0..0,4
  .args[2]
   0] Name 'arg' Load - 0,5..0,8
   1] Starred - 0,20..0,25
     .value Name 'args' Load - 0,21..0,25
     .ctx Load
  .keywords[1]
   0] keyword - 0,10..0,18
     .arg 'key'
     .value Name 'word' Load - 0,14..0,18
''',
r'''**keywords''', r'''
keyword - ROOT 0,0..0,10
  .value Name 'keywords' Load - 0,2..0,10
'''),
],

'arguments__all': [  # ................................................................................

('', 0, None, '_all', {}, ('arguments',
r'''a: int = ( 1 ), /, b: str = ( '2' ), *c: tuple, d: bytes = ( b'z' ), **e: dict'''),
r'''b: str = ( '2' ), *c: tuple, d: bytes = ( b'z' ), **e: dict''', r'''
arguments - ROOT 0,0..0,59
  .args[1]
   0] arg - 0,0..0,6
     .arg 'b'
     .annotation Name 'str' Load - 0,3..0,6
  .vararg arg - 0,19..0,27
    .arg 'c'
    .annotation Name 'tuple' Load - 0,22..0,27
  .kwonlyargs[1]
   0] arg - 0,29..0,37
     .arg 'd'
     .annotation Name 'bytes' Load - 0,32..0,37
  .kw_defaults[1]
   0] Constant b'z' - 0,42..0,46
  .kwarg arg - 0,52..0,59
    .arg 'e'
    .annotation Name 'dict' Load - 0,55..0,59
  .defaults[1]
   0] Constant '2' - 0,11..0,14
''',
r'''a: int = ( 1 ), /''', r'''
arguments - ROOT 0,0..0,17
  .posonlyargs[1]
   0] arg - 0,0..0,6
     .arg 'a'
     .annotation Name 'int' Load - 0,3..0,6
  .defaults[1]
   0] Constant 1 - 0,11..0,12
'''),

('', 1, None, '_all', {}, ('arguments',
r'''a: int = ( 1 ), /, b: str = ( '2' ), *c: tuple, d: bytes = ( b'z' ), **e: dict'''),
r'''a: int = ( 1 ), /, *c: tuple, d: bytes = ( b'z' ), **e: dict''', r'''
arguments - ROOT 0,0..0,60
  .posonlyargs[1]
   0] arg - 0,0..0,6
     .arg 'a'
     .annotation Name 'int' Load - 0,3..0,6
  .vararg arg - 0,20..0,28
    .arg 'c'
    .annotation Name 'tuple' Load - 0,23..0,28
  .kwonlyargs[1]
   0] arg - 0,30..0,38
     .arg 'd'
     .annotation Name 'bytes' Load - 0,33..0,38
  .kw_defaults[1]
   0] Constant b'z' - 0,43..0,47
  .kwarg arg - 0,53..0,60
    .arg 'e'
    .annotation Name 'dict' Load - 0,56..0,60
  .defaults[1]
   0] Constant 1 - 0,11..0,12
''',
r'''b: str = ( '2' )''', r'''
arguments - ROOT 0,0..0,16
  .args[1]
   0] arg - 0,0..0,6
     .arg 'b'
     .annotation Name 'str' Load - 0,3..0,6
  .defaults[1]
   0] Constant '2' - 0,11..0,14
'''),

('', 2, None, '_all', {}, ('arguments',
r'''a: int = ( 1 ), /, b: str = ( '2' ), *c: tuple, d: bytes = ( b'z' ), **e: dict'''),
r'''a: int = ( 1 ), /, b: str = ( '2' ), *, d: bytes = ( b'z' ), **e: dict''', r'''
arguments - ROOT 0,0..0,70
  .posonlyargs[1]
   0] arg - 0,0..0,6
     .arg 'a'
     .annotation Name 'int' Load - 0,3..0,6
  .args[1]
   0] arg - 0,19..0,25
     .arg 'b'
     .annotation Name 'str' Load - 0,22..0,25
  .kwonlyargs[1]
   0] arg - 0,40..0,48
     .arg 'd'
     .annotation Name 'bytes' Load - 0,43..0,48
  .kw_defaults[1]
   0] Constant b'z' - 0,53..0,57
  .kwarg arg - 0,63..0,70
    .arg 'e'
    .annotation Name 'dict' Load - 0,66..0,70
  .defaults[2]
   0] Constant 1 - 0,11..0,12
   1] Constant '2' - 0,30..0,33
''',
r'''*c: tuple''', r'''
arguments - ROOT 0,0..0,9
  .vararg arg - 0,1..0,9
    .arg 'c'
    .annotation Name 'tuple' Load - 0,4..0,9
'''),

('', 3, None, '_all', {}, ('arguments',
r'''a: int = ( 1 ), /, b: str = ( '2' ), *c: tuple, d: bytes = ( b'z' ), **e: dict'''),
r'''a: int = ( 1 ), /, b: str = ( '2' ), *c: tuple, **e: dict''', r'''
arguments - ROOT 0,0..0,57
  .posonlyargs[1]
   0] arg - 0,0..0,6
     .arg 'a'
     .annotation Name 'int' Load - 0,3..0,6
  .args[1]
   0] arg - 0,19..0,25
     .arg 'b'
     .annotation Name 'str' Load - 0,22..0,25
  .vararg arg - 0,38..0,46
    .arg 'c'
    .annotation Name 'tuple' Load - 0,41..0,46
  .kwarg arg - 0,50..0,57
    .arg 'e'
    .annotation Name 'dict' Load - 0,53..0,57
  .defaults[2]
   0] Constant 1 - 0,11..0,12
   1] Constant '2' - 0,30..0,33
''',
r'''*, d: bytes = ( b'z' )''', r'''
arguments - ROOT 0,0..0,22
  .kwonlyargs[1]
   0] arg - 0,3..0,11
     .arg 'd'
     .annotation Name 'bytes' Load - 0,6..0,11
  .kw_defaults[1]
   0] Constant b'z' - 0,16..0,20
'''),

('', 4, None, '_all', {}, ('arguments',
r'''a: int = ( 1 ), /, b: str = ( '2' ), *c: tuple, d: bytes = ( b'z' ), **e: dict'''),
r'''a: int = ( 1 ), /, b: str = ( '2' ), *c: tuple, d: bytes = ( b'z' )''', r'''
arguments - ROOT 0,0..0,67
  .posonlyargs[1]
   0] arg - 0,0..0,6
     .arg 'a'
     .annotation Name 'int' Load - 0,3..0,6
  .args[1]
   0] arg - 0,19..0,25
     .arg 'b'
     .annotation Name 'str' Load - 0,22..0,25
  .vararg arg - 0,38..0,46
    .arg 'c'
    .annotation Name 'tuple' Load - 0,41..0,46
  .kwonlyargs[1]
   0] arg - 0,48..0,56
     .arg 'd'
     .annotation Name 'bytes' Load - 0,51..0,56
  .kw_defaults[1]
   0] Constant b'z' - 0,61..0,65
  .defaults[2]
   0] Constant 1 - 0,11..0,12
   1] Constant '2' - 0,30..0,33
''',
r'''**e: dict''', r'''
arguments - ROOT 0,0..0,9
  .kwarg arg - 0,2..0,9
    .arg 'e'
    .annotation Name 'dict' Load - 0,5..0,9
'''),
],

'type_params': [  # ................................................................................

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 1, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -1, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -2, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -4, None, 'type_params', {'_ver': 12}, ('exec',
r'''def f[T: int, U: (str)](): pass'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 1, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -1, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -2, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -4, None, 'type_params', {'_ver': 12}, ('exec',
r'''async def f[T: int, U: (str)](): pass'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 1, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -1, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -2, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -4, None, 'type_params', {'_ver': 12}, ('exec',
r'''class c[T: int, U: (str)]: pass'''),
r'''**IndexError('index out of range')**'''),

('body[0]', 0, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', 1, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -1, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -2, None, 'type_params', {'_ver': 12}, ('exec',
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

('body[0]', -4, None, 'type_params', {'_ver': 12}, ('exec',
r'''type t[T: int, U: (str)] = ...'''),
r'''**IndexError('index out of range')**'''),

('', 0, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''),
r'''U: (str)''', r'''
_type_params - ROOT 0,0..0,8
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

('', 1, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''),
r'''T: int''', r'''
_type_params - ROOT 0,0..0,6
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

('', -1, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''),
r'''T: int''', r'''
_type_params - ROOT 0,0..0,6
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

('', -2, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''),
r'''U: (str)''', r'''
_type_params - ROOT 0,0..0,8
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

('', -4, None, 'type_params', {'_ver': 12}, ('_type_params',
r'''T: int, U: (str)'''),
r'''**IndexError('index out of range')**'''),
],

'virtual_field__body': [  # ................................................................................

('', 0, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, None, '_body', {}, ('Interactive',
r'''"""non-doc"""; a; b'''),
r'''a; b''', r'''
Interactive - ROOT 0,0..0,4
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 0,3..0,4
     .value Name 'b' Load - 0,3..0,4
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('FunctionDef', r'''
def f():
    """doc"""
    a
    b
'''), r'''
def f():
    """doc"""
    b
''', r'''
FunctionDef - ROOT 0,0..2,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, None, '_body', {}, ('AsyncFunctionDef', r'''
async def f():
    """doc"""
    a
    b
'''), r'''
async def f():
    """doc"""
    b
''', r'''
AsyncFunctionDef - ROOT 0,0..2,5
  .name 'f'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, None, '_body', {}, ('ClassDef', r'''
class cls:
    """doc"""
    a
    b
'''), r'''
class cls:
    """doc"""
    b
''', r'''
ClassDef - ROOT 0,0..2,5
  .name 'cls'
  .body[2]
   0] Expr - 1,4..1,13
     .value Constant 'doc' - 1,4..1,13
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', 0, None, '_body', {}, ('For', r'''
for _ in _:
    """non-doc"""
    a
    b
'''), r'''
for _ in _:
    a
    b
''', r'''
For - ROOT 0,0..2,5
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('AsyncFor', r'''
async for _ in _:
    """non-doc"""
    a
    b
'''), r'''
async for _ in _:
    a
    b
''', r'''
AsyncFor - ROOT 0,0..2,5
  .target Name '_' Store - 0,10..0,11
  .iter Name '_' Load - 0,15..0,16
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('While', r'''
while _:
    """non-doc"""
    a
    b
'''), r'''
while _:
    a
    b
''', r'''
While - ROOT 0,0..2,5
  .test Name '_' Load - 0,6..0,7
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('If', r'''
if _:
    """non-doc"""
    a
    b
'''), r'''
if _:
    a
    b
''', r'''
If - ROOT 0,0..2,5
  .test Name '_' Load - 0,3..0,4
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('With', r'''
with _:
    """non-doc"""
    a
    b
'''), r'''
with _:
    a
    b
''', r'''
With - ROOT 0,0..2,5
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name '_' Load - 0,5..0,6
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('AsyncWith', r'''
async with _:
    """non-doc"""
    a
    b
'''), r'''
async with _:
    a
    b
''', r'''
AsyncWith - ROOT 0,0..2,5
  .items[1]
   0] withitem - 0,11..0,12
     .context_expr Name '_' Load - 0,11..0,12
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('Try', r'''
try:
    """non-doc"""
    a
    b
except: pass
'''), r'''
try:
    a
    b
except: pass
''', r'''
Try - ROOT 0,0..3,12
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
  .handlers[1]
   0] ExceptHandler - 3,0..3,12
     .body[1]
      0] Pass - 3,8..3,12
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {'_ver': 11}, ('TryStar', r'''
try:
    """non-doc"""
    a
    b
except* Exception: pass
'''), r'''
try:
    a
    b
except* Exception: pass
''', r'''
TryStar - ROOT 0,0..3,23
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
  .handlers[1]
   0] ExceptHandler - 3,0..3,23
     .type Name 'Exception' Load - 3,8..3,17
     .body[1]
      0] Pass - 3,19..3,23
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('ExceptHandler', r'''
except:
    """non-doc"""
    a
    b
'''), r'''
except:
    a
    b
''', r'''
ExceptHandler - ROOT 0,0..2,5
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 0, None, '_body', {}, ('match_case', r'''
case _:
    """non-doc"""
    a
    b
'''), r'''
case _:
    a
    b
''', r'''
match_case - ROOT 0,0..2,5
  .pattern MatchAs - 0,5..0,6
  .body[2]
   0] Expr - 1,4..1,5
     .value Name 'a' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
''',
r'''"""non-doc"""''', r'''
Expr - ROOT 0,0..0,13
  .value Constant 'non-doc' - 0,0..0,13
'''),

('', 1, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
''',
r'''b''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'b' Load - 0,0..0,1
'''),

('', 2, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''**IndexError('index out of range')**'''),

('', -1, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
a
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
''',
r'''b''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'b' Load - 0,0..0,1
'''),

('', -2, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''), r'''
"""doc"""
b
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,9
     .value Constant 'doc' - 0,0..0,9
   1] Expr - 1,0..1,1
     .value Name 'b' Load - 1,0..1,1
''',
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', -3, None, '_body', {}, ('Module', r'''
"""doc"""
a
b
'''),
r'''**IndexError('index out of range')**'''),
],

}
