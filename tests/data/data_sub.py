# (attr, None, None, None, sub_call_params, code | (parse_mode, code),
#
# 'pattern',
# repl | (repl_mode, repl),
# ((code after sub,
# dump code after sub,)
# - OR
# (error,))
# )

DATA_SUB = {
'basic_mod': [  # ................................................................................

('', None, None, None, {}, ('exec', r'''
a = b
call()
'''),
r'''MModule(body=M(b=...))''', ('exec',
r'''__FST_b'''), r'''
a = b
call()
''', r'''
Module - ROOT 0,0..1,6
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Name 'b' Load - 0,4..0,5
   1] Expr - 1,0..1,6
     .value Call - 1,0..1,6
       .func Name 'call' Load - 1,0..1,4
'''),

('', None, None, None, {}, ('exec', r'''
a = b
call()
'''),
r'''MModule(body=[MQSTAR, M(b=Assign), MQSTAR])''', ('exec',
r'''__FST_b'''),
r'''a = b''', r'''
Module - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Name 'b' Load - 0,4..0,5
'''),

('', None, None, None, {}, ('Interactive',
r'''a = b; call()'''),
r'''MInteractive(body=M(b=...))''', ('Interactive',
r'''__FST_b'''),
r'''a = b; call()''', r'''
Interactive - ROOT 0,0..0,13
  .body[2]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Name 'b' Load - 0,4..0,5
   1] Expr - 0,7..0,13
     .value Call - 0,7..0,13
       .func Name 'call' Load - 0,7..0,11
'''),

('', None, None, None, {}, ('Interactive',
r'''a = b; call()'''),
r'''MInteractive(body=[MQSTAR, M(b=Assign), MQSTAR])''', ('Interactive',
r'''__FST_b'''),
r'''a = b''', r'''
Interactive - ROOT 0,0..0,5
  .body[1]
   0] Assign - 0,0..0,5
     .targets[1]
      0] Name 'a' Store - 0,0..0,1
     .value Name 'b' Load - 0,4..0,5
'''),

('', None, None, None, {}, ('Expression',
r'''call()'''),
r'''MExpression(body=M(b=...))''', ('Expression',
r'''__FST_b'''),
r'''call()''', r'''
Expression - ROOT 0,0..0,6
  .body Call - 0,0..0,6
    .func Name 'call' Load - 0,0..0,4
'''),
],

'basic_FunctionDef': [  # ................................................................................

('', None, None, None, {}, ('Name',
r'''newdeco'''),
r'''Name''', ('exec', r'''
@__FST_
def f(): pass
'''), r'''
@newdeco
def f(): pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] FunctionDef - 1,0..1,13
     .name 'f'
     .body[1]
      0] Pass - 1,9..1,13
     .decorator_list[1]
      0] Name 'newdeco' Load - 0,1..0,8
'''),

('', None, None, None, {}, ('FunctionDef', r'''
@newdeco1
@newdeco2()
def g(): pass
'''),
r'''MFunctionDef(decorator_list=M(decos=...))''', ('exec', r'''
@__FST_decos
def f(): pass
'''), r'''
@newdeco1
@newdeco2()
def f(): pass
''', r'''
Module - ROOT 0,0..2,13
  .body[1]
   0] FunctionDef - 2,0..2,13
     .name 'f'
     .body[1]
      0] Pass - 2,9..2,13
     .decorator_list[2]
      0] Name 'newdeco1' Load - 0,1..0,9
      1] Call - 1,1..1,11
        .func Name 'newdeco2' Load - 1,1..1,9
'''),

('', None, None, None, {}, ('FunctionDef', r'''
@newdeco1
@newdeco2()
@newdeco3
def g(): pass
'''),
r'''MFunctionDef(decorator_list=[..., M(deco=...), ...])''', ('exec', r'''
@__FST_deco
def f(): pass
'''), r'''
@newdeco2()
def f(): pass
''', r'''
Module - ROOT 0,0..1,13
  .body[1]
   0] FunctionDef - 1,0..1,13
     .name 'f'
     .body[1]
      0] Pass - 1,9..1,13
     .decorator_list[1]
      0] Call - 0,1..0,11
        .func Name 'newdeco2' Load - 0,1..0,9
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def funcname(): pass'''),
r'''MFunctionDef(name=M(fname=...))''', ('exec',
r'''def __FST_fname(): pass'''),
r'''def funcname(): pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'funcname'
     .body[1]
      0] Pass - 0,16..0,20
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def g[T: int](): pass'''),
r'''MFunctionDef(type_params=M(tparams=...))''', ('exec',
r'''def f[__FST_tparams](): pass'''),
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
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def g[T: int](): pass'''),
r'''MFunctionDef''', ('exec',
r'''def f[__FST_tparams](): pass'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def g[T: int, *U, **V](): pass'''),
r'''MFunctionDef(type_params=M(tparams=...))''', ('exec',
r'''def f[__FST_tparams](): pass'''),
r'''def f[T: int, *U, **V](): pass''', r'''
Module - ROOT 0,0..0,30
  .body[1]
   0] FunctionDef - 0,0..0,30
     .name 'f'
     .body[1]
      0] Pass - 0,26..0,30
     .type_params[3]
      0] TypeVar - 0,6..0,12
        .name 'T'
        .bound Name 'int' Load - 0,9..0,12
      1] TypeVarTuple - 0,14..0,16
        .name 'U'
      2] ParamSpec - 0,18..0,21
        .name 'V'
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def g[T: int, *U, **V](): pass'''),
r'''MFunctionDef(type_params=[..., M(tparam=...), ...])''', ('exec',
r'''def f[__FST_tparam](): pass'''),
r'''def f[*U](): pass''', r'''
Module - ROOT 0,0..0,17
  .body[1]
   0] FunctionDef - 0,0..0,17
     .name 'f'
     .body[1]
      0] Pass - 0,13..0,17
     .type_params[1]
      0] TypeVarTuple - 0,6..0,8
        .name 'U'
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def g(a: int, /, b=2, *c, d: bool = True, **e: Any): pass'''),
r'''MFunctionDef(args=M(fargs=...))''', ('exec',
r'''def f(__FST_fargs): pass'''),
r'''def f(a: int, /, b=2, *c, d: bool = True, **e: Any): pass''', r'''
Module - ROOT 0,0..0,57
  .body[1]
   0] FunctionDef - 0,0..0,57
     .name 'f'
     .args arguments - 0,6..0,50
       .posonlyargs[1]
        0] arg - 0,6..0,12
          .arg 'a'
          .annotation Name 'int' Load - 0,9..0,12
       .args[1]
        0] arg - 0,17..0,18
          .arg 'b'
       .vararg arg - 0,23..0,24
         .arg 'c'
       .kwonlyargs[1]
        0] arg - 0,26..0,33
          .arg 'd'
          .annotation Name 'bool' Load - 0,29..0,33
       .kw_defaults[1]
        0] Constant True - 0,36..0,40
       .kwarg arg - 0,44..0,50
         .arg 'e'
         .annotation Name 'Any' Load - 0,47..0,50
       .defaults[1]
        0] Constant 2 - 0,19..0,20
     .body[1]
      0] Pass - 0,53..0,57
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def g(): pass'''),
r'''MFunctionDef(args=M(fargs=...))''', ('exec',
r'''def f(__FST_fargs): pass'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def g(a, b): pass'''),
r'''MFunctionDef(args=M(fargs=...))''', ('exec',
r'''def f(x, __FST_fargs, y): pass'''),
r'''def f(x, a, b, y): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] FunctionDef - 0,0..0,23
     .name 'f'
     .args arguments - 0,6..0,16
       .args[4]
        0] arg - 0,6..0,7
          .arg 'x'
        1] arg - 0,9..0,10
          .arg 'a'
        2] arg - 0,12..0,13
          .arg 'b'
        3] arg - 0,15..0,16
          .arg 'y'
     .body[1]
      0] Pass - 0,19..0,23
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def g(a, b, /): pass'''),
r'''MFunctionDef(args=M(fargs=...))''', ('exec',
r'''def f(x, __FST_fargs, y): pass'''),
r'''def f(x, a, b, y): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] FunctionDef - 0,0..0,23
     .name 'f'
     .args arguments - 0,6..0,16
       .args[4]
        0] arg - 0,6..0,7
          .arg 'x'
        1] arg - 0,9..0,10
          .arg 'a'
        2] arg - 0,12..0,13
          .arg 'b'
        3] arg - 0,15..0,16
          .arg 'y'
     .body[1]
      0] Pass - 0,19..0,23
'''),

('', None, None, None, {'args_as': 'arg'}, ('FunctionDef',
r'''def g(a, b, /): pass'''),
r'''MFunctionDef(args=M(fargs=...))''', ('exec',
r'''def f(x, __FST_fargs, y): pass'''),
r'''def f(x, a, b, y): pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] FunctionDef - 0,0..0,23
     .name 'f'
     .args arguments - 0,6..0,16
       .args[4]
        0] arg - 0,6..0,7
          .arg 'x'
        1] arg - 0,9..0,10
          .arg 'a'
        2] arg - 0,12..0,13
          .arg 'b'
        3] arg - 0,15..0,16
          .arg 'y'
     .body[1]
      0] Pass - 0,19..0,23
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def g(a, b, c): pass'''),
r'''MFunctionDef(args=Marguments(_all=[..., M(fargs=...), ...]))''', ('exec',
r'''def f(x, __FST_fargs, y): pass'''),
r'''def f(x, b, y): pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .args arguments - 0,6..0,13
       .args[3]
        0] arg - 0,6..0,7
          .arg 'x'
        1] arg - 0,9..0,10
          .arg 'b'
        2] arg - 0,12..0,13
          .arg 'y'
     .body[1]
      0] Pass - 0,16..0,20
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def g() -> int: pass'''),
r'''MFunctionDef(returns=M(fret=...))''', ('exec',
r'''def f() -> __FST_fret: pass'''),
r'''def f() -> int: pass''', r'''
Module - ROOT 0,0..0,20
  .body[1]
   0] FunctionDef - 0,0..0,20
     .name 'f'
     .body[1]
      0] Pass - 0,16..0,20
     .returns Name 'int' Load - 0,11..0,14
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def g(): pass'''),
r'''MFunctionDef(returns=M(fret=...))''', ('exec',
r'''def f() -> __FST_fret: pass'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('', None, None, None, {}, ('FunctionDef', r'''
def g():
    a = b
    call()
    return
'''),
r'''MFunctionDef(body=M(fbody=...))''', ('exec',
r'''def f(): __FST_fbody'''), r'''
def f():
    a = b
    call()
    return
''', r'''
Module - ROOT 0,0..3,10
  .body[1]
   0] FunctionDef - 0,0..3,10
     .name 'f'
     .body[3]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'a' Store - 1,4..1,5
        .value Name 'b' Load - 1,8..1,9
      1] Expr - 2,4..2,10
        .value Call - 2,4..2,10
          .func Name 'call' Load - 2,4..2,8
      2] Return - 3,4..3,10
'''),

('', None, None, None, {}, ('FunctionDef', r'''
def g():
    a = b
    call()
    return
'''),
r'''MFunctionDef(body=M(fbody=...))''', ('exec', r'''
def f():
    pre()
    __FST_fbody
    post()
'''), r'''
def f():
    pre()
    a = b
    call()
    return
    post()
''', r'''
Module - ROOT 0,0..5,10
  .body[1]
   0] FunctionDef - 0,0..5,10
     .name 'f'
     .body[5]
      0] Expr - 1,4..1,9
        .value Call - 1,4..1,9
          .func Name 'pre' Load - 1,4..1,7
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'a' Store - 2,4..2,5
        .value Name 'b' Load - 2,8..2,9
      2] Expr - 3,4..3,10
        .value Call - 3,4..3,10
          .func Name 'call' Load - 3,4..3,8
      3] Return - 4,4..4,10
      4] Expr - 5,4..5,10
        .value Call - 5,4..5,10
          .func Name 'post' Load - 5,4..5,8
'''),

('', None, None, None, {}, ('FunctionDef', r'''
def g():
    a = b
    call()
    return
'''),
r'''MFunctionDef(body=[..., M(fbody=...), ...])''', ('exec',
r'''def f(): __FST_fbody'''), r'''
def f():
    call()
''', r'''
Module - ROOT 0,0..1,10
  .body[1]
   0] FunctionDef - 0,0..1,10
     .name 'f'
     .body[1]
      0] Expr - 1,4..1,10
        .value Call - 1,4..1,10
          .func Name 'call' Load - 1,4..1,8
'''),

('', None, None, None, {}, ('FunctionDef', r'''
def g():
    a = b
    call()
    return
'''),
r'''MFunctionDef(body=[..., M(fbody=...), ...])''', ('exec', r'''
def f():
    pre()
    __FST_fbody
    post()
'''), r'''
def f():
    pre()
    call()
    post()
''', r'''
Module - ROOT 0,0..3,10
  .body[1]
   0] FunctionDef - 0,0..3,10
     .name 'f'
     .body[3]
      0] Expr - 1,4..1,9
        .value Call - 1,4..1,9
          .func Name 'pre' Load - 1,4..1,7
      1] Expr - 2,4..2,10
        .value Call - 2,4..2,10
          .func Name 'call' Load - 2,4..2,8
      2] Expr - 3,4..3,10
        .value Call - 3,4..3,10
          .func Name 'post' Load - 3,4..3,8
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(a, b=1, /, c=2, *d, **e): a ; b ; c ; d ; e'''),
r'''MFunctionDef(args=Marguments(_all=[..., MQSTAR(a=...), ...]), body=[..., MQSTAR(b=...), ...])''', ('FunctionDef',
r'''def g(x, /, __FST_a): x; __FST_b; y'''), r'''
def g(x, /, b=1, c=2, *d):
    x
    b ; c ; d
    y
''', r'''
FunctionDef - ROOT 0,0..3,5
  .name 'g'
  .args arguments - 0,6..0,24
    .posonlyargs[1]
     0] arg - 0,6..0,7
       .arg 'x'
    .args[2]
     0] arg - 0,12..0,13
       .arg 'b'
     1] arg - 0,17..0,18
       .arg 'c'
    .vararg arg - 0,23..0,24
      .arg 'd'
    .defaults[2]
     0] Constant 1 - 0,14..0,15
     1] Constant 2 - 0,19..0,20
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
'''),

('', None, None, None, {'args_as': None}, ('FunctionDef',
r'''def f(a, b=1, /, c=2, *d, **e): a ; b ; c ; d ; e'''),
r'''MFunctionDef(args=Marguments(_all=[..., MQSTAR(a=...), ...]), body=[..., MQSTAR(b=...), ...])''', ('FunctionDef',
r'''def g(x, /, __FST_a): x; __FST_b; y'''), r'''
def g(x, b=1, /, c=2, *d):
    x
    b ; c ; d
    y
''', r'''
FunctionDef - ROOT 0,0..3,5
  .name 'g'
  .args arguments - 0,6..0,24
    .posonlyargs[2]
     0] arg - 0,6..0,7
       .arg 'x'
     1] arg - 0,9..0,10
       .arg 'b'
    .args[1]
     0] arg - 0,17..0,18
       .arg 'c'
    .vararg arg - 0,23..0,24
      .arg 'd'
    .defaults[2]
     0] Constant 1 - 0,11..0,12
     1] Constant 2 - 0,19..0,20
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
'''),
],

'basic_AsyncFunctionDef': [  # ................................................................................

('', None, None, None, {}, ('FunctionDef',
r'''def funcname(): pass'''),
r'''MFunctionDef(name=M(fname=...))''', ('exec',
r'''async def __FST_fname(): pass'''),
r'''async def funcname(): pass''', r'''
Module - ROOT 0,0..0,26
  .body[1]
   0] AsyncFunctionDef - 0,0..0,26
     .name 'funcname'
     .body[1]
      0] Pass - 0,22..0,26
'''),

('', None, None, None, {}, ('AsyncFunctionDef',
r'''async def f(a, b=1, /, c=2, *d, **e): a ; b ; c ; d ; e'''),
r'''MAsyncFunctionDef(args=Marguments(_all=[..., MQSTAR(a=...), ...]), body=[..., MQSTAR(b=...), ...])''', ('AsyncFunctionDef',
r'''async def g(x, /, __FST_a): x; __FST_b; y'''), r'''
async def g(x, /, b=1, c=2, *d):
    x
    b ; c ; d
    y
''', r'''
AsyncFunctionDef - ROOT 0,0..3,5
  .name 'g'
  .args arguments - 0,12..0,30
    .posonlyargs[1]
     0] arg - 0,12..0,13
       .arg 'x'
    .args[2]
     0] arg - 0,18..0,19
       .arg 'b'
     1] arg - 0,23..0,24
       .arg 'c'
    .vararg arg - 0,29..0,30
      .arg 'd'
    .defaults[2]
     0] Constant 1 - 0,20..0,21
     1] Constant 2 - 0,25..0,26
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
'''),

('', None, None, None, {'args_as': None}, ('AsyncFunctionDef',
r'''async def f(a, b=1, /, c=2, *d, **e): a ; b ; c ; d ; e'''),
r'''MAsyncFunctionDef(args=Marguments(_all=[..., MQSTAR(a=...), ...]), body=[..., MQSTAR(b=...), ...])''', ('AsyncFunctionDef',
r'''async def g(x, /, __FST_a): x; __FST_b; y'''), r'''
async def g(x, b=1, /, c=2, *d):
    x
    b ; c ; d
    y
''', r'''
AsyncFunctionDef - ROOT 0,0..3,5
  .name 'g'
  .args arguments - 0,12..0,30
    .posonlyargs[2]
     0] arg - 0,12..0,13
       .arg 'x'
     1] arg - 0,15..0,16
       .arg 'b'
    .args[1]
     0] arg - 0,23..0,24
       .arg 'c'
    .vararg arg - 0,29..0,30
      .arg 'd'
    .defaults[2]
     0] Constant 1 - 0,17..0,18
     1] Constant 2 - 0,25..0,26
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
'''),
],

'basic_ClassDef': [  # ................................................................................

('', None, None, None, {}, ('Name',
r'''newdeco'''),
r'''Name''', ('exec', r'''
@__FST_
class cls: pass
'''), r'''
@newdeco
class cls: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] ClassDef - 1,0..1,15
     .name 'cls'
     .body[1]
      0] Pass - 1,11..1,15
     .decorator_list[1]
      0] Name 'newdeco' Load - 0,1..0,8
'''),

('', None, None, None, {}, ('AsyncFunctionDef', r'''
@newdeco1
@newdeco2()
async def g(): pass
'''),
r'''MAsyncFunctionDef(decorator_list=M(decos=...))''', ('exec', r'''
@__FST_decos
class cls: pass
'''), r'''
@newdeco1
@newdeco2()
class cls: pass
''', r'''
Module - ROOT 0,0..2,15
  .body[1]
   0] ClassDef - 2,0..2,15
     .name 'cls'
     .body[1]
      0] Pass - 2,11..2,15
     .decorator_list[2]
      0] Name 'newdeco1' Load - 0,1..0,9
      1] Call - 1,1..1,11
        .func Name 'newdeco2' Load - 1,1..1,9
'''),

('', None, None, None, {}, ('FunctionDef', r'''
@newdeco1
@newdeco2()
@newdeco3
def g(): pass
'''),
r'''MTYPES((FunctionDef, AsyncFunctionDef), decorator_list=[..., M(deco=...), ...])''', ('exec', r'''
@__FST_deco
class cls: pass
'''), r'''
@newdeco2()
class cls: pass
''', r'''
Module - ROOT 0,0..1,15
  .body[1]
   0] ClassDef - 1,0..1,15
     .name 'cls'
     .body[1]
      0] Pass - 1,11..1,15
     .decorator_list[1]
      0] Call - 0,1..0,11
        .func Name 'newdeco2' Load - 0,1..0,9
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def funcname(): pass'''),
r'''MFunctionDef(name=M(fname=...))''', ('exec',
r'''class __FST_fname(): pass'''),
r'''class funcname(): pass''', r'''
Module - ROOT 0,0..0,22
  .body[1]
   0] ClassDef - 0,0..0,22
     .name 'funcname'
     .body[1]
      0] Pass - 0,18..0,22
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def g[T: int](): pass'''),
r'''MFunctionDef(type_params=M(tparams=...))''', ('exec',
r'''class cls[__FST_tparams]: pass'''),
r'''class cls[T: int]: pass''', r'''
Module - ROOT 0,0..0,23
  .body[1]
   0] ClassDef - 0,0..0,23
     .name 'cls'
     .body[1]
      0] Pass - 0,19..0,23
     .type_params[1]
      0] TypeVar - 0,10..0,16
        .name 'T'
        .bound Name 'int' Load - 0,13..0,16
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def g[T: int](): pass'''),
r'''MFunctionDef''', ('exec',
r'''def f[__FST_tparams](): pass'''),
r'''def f(): pass''', r'''
Module - ROOT 0,0..0,13
  .body[1]
   0] FunctionDef - 0,0..0,13
     .name 'f'
     .body[1]
      0] Pass - 0,9..0,13
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def g[T: int, *U, **V](): pass'''),
r'''MFunctionDef(type_params=M(tparams=...))''', ('exec',
r'''class cls[__FST_tparams](): pass'''),
r'''class cls[T: int, *U, **V](): pass''', r'''
Module - ROOT 0,0..0,34
  .body[1]
   0] ClassDef - 0,0..0,34
     .name 'cls'
     .body[1]
      0] Pass - 0,30..0,34
     .type_params[3]
      0] TypeVar - 0,10..0,16
        .name 'T'
        .bound Name 'int' Load - 0,13..0,16
      1] TypeVarTuple - 0,18..0,20
        .name 'U'
      2] ParamSpec - 0,22..0,25
        .name 'V'
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def g[T: int, *U, **V](): pass'''),
r'''MFunctionDef(type_params=[..., M(tparam=...), ...])''', ('exec',
r'''class cls[__FST_tparam](): pass'''),
r'''class cls[*U](): pass''', r'''
Module - ROOT 0,0..0,21
  .body[1]
   0] ClassDef - 0,0..0,21
     .name 'cls'
     .body[1]
      0] Pass - 0,17..0,21
     .type_params[1]
      0] TypeVarTuple - 0,10..0,12
        .name 'U'
'''),

('', None, None, None, {}, ('ClassDef',
r'''class sup(a, *b, c=d, **e): pass'''),
r'''MClassDef''', (None,
r'''class cls(__FST_DEL): pass'''),
r'''class cls: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'cls'
  .body[1]
   0] Pass - 0,11..0,15
'''),

('', None, None, None, {}, ('ClassDef',
r'''class sup(a, *b, c=d, **e): pass'''),
r'''MClassDef(bases=M(cbases=...))''', (None,
r'''class cls(__FST_cbases): pass'''),
r'''class cls(a, *b): pass''', r'''
ClassDef - ROOT 0,0..0,22
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,15
     .value Name 'b' Load - 0,14..0,15
     .ctx Load
  .body[1]
   0] Pass - 0,18..0,22
'''),

('', None, None, None, {}, ('ClassDef',
r'''class sup(a, *b, c=d, **e): pass'''),
r'''MClassDef(keywords=M(ckeywords=...))''', (None,
r'''class cls(__FST_ckeywords): pass'''),
r'''class cls(c=d, **e): pass''', r'''
ClassDef - ROOT 0,0..0,25
  .name 'cls'
  .keywords[2]
   0] keyword - 0,10..0,13
     .arg 'c'
     .value Name 'd' Load - 0,12..0,13
   1] keyword - 0,15..0,18
     .value Name 'e' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', None, None, None, {}, ('ClassDef',
r'''class sup(a, *b, c=d, **e): pass'''),
r'''MClassDef(_bases=M(c_bases=...))''', (None,
r'''class cls(__FST_c_bases): pass'''),
r'''class cls(a, *b, c=d, **e): pass''', r'''
ClassDef - ROOT 0,0..0,32
  .name 'cls'
  .bases[2]
   0] Name 'a' Load - 0,10..0,11
   1] Starred - 0,13..0,15
     .value Name 'b' Load - 0,14..0,15
     .ctx Load
  .keywords[2]
   0] keyword - 0,17..0,20
     .arg 'c'
     .value Name 'd' Load - 0,19..0,20
   1] keyword - 0,22..0,25
     .value Name 'e' Load - 0,24..0,25
  .body[1]
   0] Pass - 0,28..0,32
'''),

('', None, None, None, {}, ('ClassDef',
r'''class sup(a, *b, c=d, **e): pass'''),
r'''MClassDef(_bases=[..., ..., M(c_base=...), ...])''', (None,
r'''class cls(__FST_c_base): pass'''),
r'''class cls(c=d): pass''', r'''
ClassDef - ROOT 0,0..0,20
  .name 'cls'
  .keywords[1]
   0] keyword - 0,10..0,13
     .arg 'c'
     .value Name 'd' Load - 0,12..0,13
  .body[1]
   0] Pass - 0,16..0,20
'''),

('', None, None, None, {}, ('ClassDef',
r'''class sup(a, *b, c=d, **e): pass'''),
r'''MClassDef(_bases=[MQN(c_base=..., n=2), ..., ...])''', (None,
r'''class cls(x, __FSO_c_base, **y): pass'''),
r'''class cls(x, (a, *b), **y): pass''', r'''
ClassDef - ROOT 0,0..0,32
  .name 'cls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Tuple - 0,13..0,20
     .elts[2]
      0] Name 'a' Load - 0,14..0,15
      1] Starred - 0,17..0,19
        .value Name 'b' Load - 0,18..0,19
        .ctx Load
     .ctx Load
  .keywords[1]
   0] keyword - 0,22..0,25
     .value Name 'y' Load - 0,24..0,25
  .body[1]
   0] Pass - 0,28..0,32
'''),

('', None, None, None, {}, ('FunctionDef', r'''
def g():
    a = b
    call()
    return
'''),
r'''MFunctionDef(body=M(fbody=...))''', ('exec',
r'''class cls: __FST_fbody'''), r'''
class cls:
    a = b
    call()
    return
''', r'''
Module - ROOT 0,0..3,10
  .body[1]
   0] ClassDef - 0,0..3,10
     .name 'cls'
     .body[3]
      0] Assign - 1,4..1,9
        .targets[1]
         0] Name 'a' Store - 1,4..1,5
        .value Name 'b' Load - 1,8..1,9
      1] Expr - 2,4..2,10
        .value Call - 2,4..2,10
          .func Name 'call' Load - 2,4..2,8
      2] Return - 3,4..3,10
'''),

('', None, None, None, {}, ('FunctionDef', r'''
def g():
    a = b
    call()
    return
'''),
r'''MFunctionDef(body=M(fbody=...))''', ('exec', r'''
class cls:
    pre()
    __FST_fbody
    post()
'''), r'''
class cls:
    pre()
    a = b
    call()
    return
    post()
''', r'''
Module - ROOT 0,0..5,10
  .body[1]
   0] ClassDef - 0,0..5,10
     .name 'cls'
     .body[5]
      0] Expr - 1,4..1,9
        .value Call - 1,4..1,9
          .func Name 'pre' Load - 1,4..1,7
      1] Assign - 2,4..2,9
        .targets[1]
         0] Name 'a' Store - 2,4..2,5
        .value Name 'b' Load - 2,8..2,9
      2] Expr - 3,4..3,10
        .value Call - 3,4..3,10
          .func Name 'call' Load - 3,4..3,8
      3] Return - 4,4..4,10
      4] Expr - 5,4..5,10
        .value Call - 5,4..5,10
          .func Name 'post' Load - 5,4..5,8
'''),

('', None, None, None, {}, ('FunctionDef', r'''
def g():
    a = b
    call()
    return
'''),
r'''MFunctionDef(body=[..., M(fbody=...), ...])''', ('exec',
r'''class cls: __FST_fbody'''), r'''
class cls:
    call()
''', r'''
Module - ROOT 0,0..1,10
  .body[1]
   0] ClassDef - 0,0..1,10
     .name 'cls'
     .body[1]
      0] Expr - 1,4..1,10
        .value Call - 1,4..1,10
          .func Name 'call' Load - 1,4..1,8
'''),

('', None, None, None, {}, ('FunctionDef', r'''
def g():
    a = b
    call()
    return
'''),
r'''MFunctionDef(body=[..., M(fbody=...), ...])''', ('exec', r'''
class cls:
    pre()
    __FST_fbody
    post()
'''), r'''
class cls:
    pre()
    call()
    post()
''', r'''
Module - ROOT 0,0..3,10
  .body[1]
   0] ClassDef - 0,0..3,10
     .name 'cls'
     .body[3]
      0] Expr - 1,4..1,9
        .value Call - 1,4..1,9
          .func Name 'pre' Load - 1,4..1,7
      1] Expr - 2,4..2,10
        .value Call - 2,4..2,10
          .func Name 'call' Load - 2,4..2,8
      2] Expr - 3,4..3,10
        .value Call - 3,4..3,10
          .func Name 'post' Load - 3,4..3,8
'''),

('', None, None, None, {}, ('ClassDef',
r'''class cls(a, c=c, *b, **d, **e): a ; b ; c ; d ; e'''),
r'''MClassDef(_bases=[..., MQSTAR(a=...), ...], body=[..., MQSTAR(b=...), ...])''', ('ClassDef',
r'''class kls(x, __FST_a, **y): x; __FST_b; y'''), r'''
class kls(x, c=c, *b, **d, **y):
    x
    b ; c ; d
    y
''', r'''
ClassDef - ROOT 0,0..3,5
  .name 'kls'
  .bases[2]
   0] Name 'x' Load - 0,10..0,11
   1] Starred - 0,18..0,20
     .value Name 'b' Load - 0,19..0,20
     .ctx Load
  .keywords[3]
   0] keyword - 0,13..0,16
     .arg 'c'
     .value Name 'c' Load - 0,15..0,16
   1] keyword - 0,22..0,25
     .value Name 'd' Load - 0,24..0,25
   2] keyword - 0,27..0,30
     .value Name 'y' Load - 0,29..0,30
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
'''),
],

'basic_Return': [  # ................................................................................

('', None, None, None, {}, (None,
r'''return a'''),
r'''MReturn(value=M(v=...))''',
r'''return __FST_v  # new''',
r'''return a  # new''', r'''
Return - ROOT 0,0..0,8
  .value Name 'a' Load - 0,7..0,8
'''),
],

'basic_Delete': [  # ................................................................................

('', None, None, None, {}, (None,
r'''del a'''),
r'''MDelete(targets=M(v=...))''',
r'''del __FST_v''',
r'''del a''', r'''
Delete - ROOT 0,0..0,5
  .targets[1]
   0] Name 'a' Del - 0,4..0,5
'''),

('', None, None, None, {}, (None,
r'''del a, b, c'''),
r'''MDelete(targets=M(v=...))''',
r'''del __FST_v''',
r'''del a, b, c''', r'''
Delete - ROOT 0,0..0,11
  .targets[3]
   0] Name 'a' Del - 0,4..0,5
   1] Name 'b' Del - 0,7..0,8
   2] Name 'c' Del - 0,10..0,11
'''),

('', None, None, None, {}, (None,
r'''del a'''),
r'''MDelete(targets=M(v=...))''',
r'''del x, __FST_v, y''',
r'''del x, a, y''', r'''
Delete - ROOT 0,0..0,11
  .targets[3]
   0] Name 'x' Del - 0,4..0,5
   1] Name 'a' Del - 0,7..0,8
   2] Name 'y' Del - 0,10..0,11
'''),

('', None, None, None, {}, (None,
r'''del a, b, c'''),
r'''MDelete(targets=[..., M(v=...), ...])''',
r'''del x, __FST_v, y''',
r'''del x, b, y''', r'''
Delete - ROOT 0,0..0,11
  .targets[3]
   0] Name 'x' Del - 0,4..0,5
   1] Name 'b' Del - 0,7..0,8
   2] Name 'y' Del - 0,10..0,11
'''),

('', None, None, None, {}, ('Delete',
r'''del a, b, c, d, e'''),
r'''MDelete(targets=[..., MQSTAR(t=...), ...])''', ('Delete',
r'''del x, __FST_t, y'''),
r'''del x, b, c, d, y''', r'''
Delete - ROOT 0,0..0,17
  .targets[5]
   0] Name 'x' Del - 0,4..0,5
   1] Name 'b' Del - 0,7..0,8
   2] Name 'c' Del - 0,10..0,11
   3] Name 'd' Del - 0,13..0,14
   4] Name 'y' Del - 0,16..0,17
'''),
],

'basic_Assign': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''',
r'''u = __FST_v  # new''',
r'''u = b  # new''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'u' Store - 0,0..0,1
  .value Name 'b' Load - 0,4..0,5
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(targets=M(t=...))''',
r'''__FST_t = z''',
r'''a = z''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'z' Load - 0,4..0,5
'''),

('', None, None, None, {}, (None,
r'''a = b = c = d'''),
r'''MAssign(targets=M(t=...))''',
r'''__FST_t = z''',
r'''a = b = c = z''', r'''
Assign - ROOT 0,0..0,13
  .targets[3]
   0] Name 'a' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
   2] Name 'c' Store - 0,8..0,9
  .value Name 'z' Load - 0,12..0,13
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(targets=M(t=...))''',
r'''x = __FST_t = y = z''',
r'''x = a = y = z''', r'''
Assign - ROOT 0,0..0,13
  .targets[3]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'a' Store - 0,4..0,5
   2] Name 'y' Store - 0,8..0,9
  .value Name 'z' Load - 0,12..0,13
'''),

('', None, None, None, {}, (None,
r'''a = b = c = d'''),
r'''MAssign(targets=M(t=...))''',
r'''x = __FST_t = y = z''',
r'''x = a = b = c = y = z''', r'''
Assign - ROOT 0,0..0,21
  .targets[5]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'a' Store - 0,4..0,5
   2] Name 'b' Store - 0,8..0,9
   3] Name 'c' Store - 0,12..0,13
   4] Name 'y' Store - 0,16..0,17
  .value Name 'z' Load - 0,20..0,21
'''),

('', None, None, None, {}, (None,
r'''a = b = c = d'''),
r'''MAssign(targets=[..., M(t=...), ...])''',
r'''x = __FST_t = y = z''',
r'''x = b = y = z''', r'''
Assign - ROOT 0,0..0,13
  .targets[3]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
   2] Name 'y' Store - 0,8..0,9
  .value Name 'z' Load - 0,12..0,13
'''),

('', None, None, None, {}, (None,
r'''[a, b, c]'''),
r'''MList(elts=M(t=...))''',
r'''x = __FST_t = y = z''',
r'''x = a = b = c = y = z''', r'''
Assign - ROOT 0,0..0,21
  .targets[5]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'a' Store - 0,4..0,5
   2] Name 'b' Store - 0,8..0,9
   3] Name 'c' Store - 0,12..0,13
   4] Name 'y' Store - 0,16..0,17
  .value Name 'z' Load - 0,20..0,21
'''),

('', None, None, None, {}, ('Assign',
r'''a = b = c = d = e = u'''),
r'''MAssign(targets=[..., MQSTAR(t=...), ...])''', ('Assign',
r'''x = __FST_t = y'''),
r'''x = b = c = d = y''', r'''
Assign - ROOT 0,0..0,17
  .targets[4]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
   2] Name 'c' Store - 0,8..0,9
   3] Name 'd' Store - 0,12..0,13
  .value Name 'y' Load - 0,16..0,17
'''),
],

'basic_TypeAlias': [  # ................................................................................

('', None, None, None, {'_ver': 12}, (None,
r'''a'''),
r'''Name''',
r'''type __FST_[T] = ...''',
r'''type a[T] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 'a' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'T'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', None, None, None, {'_ver': 12}, ('_type_params',
r'''T: int, *U, **V'''),
r'''M_type_params(type_params=M(tp=...))''',
r'''type t[__FST_tp] = ...''',
r'''type t[T: int, *U, **V] = ...''', r'''
TypeAlias - ROOT 0,0..0,29
  .name Name 't' Store - 0,5..0,6
  .type_params[3]
   0] TypeVar - 0,7..0,13
     .name 'T'
     .bound Name 'int' Load - 0,10..0,13
   1] TypeVarTuple - 0,15..0,17
     .name 'U'
   2] ParamSpec - 0,19..0,22
     .name 'V'
  .value Constant Ellipsis - 0,26..0,29
'''),

('', None, None, None, {'_ver': 12}, (None,
r'''a = b'''),
r'''MAssign(value=M(t=...))''',
r'''type t[T] = __FST_t''',
r'''type t[T] = b''', r'''
TypeAlias - ROOT 0,0..0,13
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'T'
  .value Name 'b' Load - 0,12..0,13
'''),

('', None, None, None, {'_ver': 12}, ('TypeAlias',
r'''type t[a, b, c, d, e] = ...'''),
r'''MTypeAlias(type_params=[..., MQSTAR(t=...), ...])''', ('TypeAlias',
r'''type t[x, __FST_t, y] = z'''),
r'''type t[x, b, c, d, y] = z''', r'''
TypeAlias - ROOT 0,0..0,25
  .name Name 't' Store - 0,5..0,6
  .type_params[5]
   0] TypeVar - 0,7..0,8
     .name 'x'
   1] TypeVar - 0,10..0,11
     .name 'b'
   2] TypeVar - 0,13..0,14
     .name 'c'
   3] TypeVar - 0,16..0,17
     .name 'd'
   4] TypeVar - 0,19..0,20
     .name 'y'
  .value Name 'z' Load - 0,24..0,25
'''),
],

'basic_AugAssign': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', ('AugAssign',
r'''u += __FST_v  # new'''),
r'''u += b  # new''', r'''
AugAssign - ROOT 0,0..0,6
  .target Name 'u' Store - 0,0..0,1
  .op Add - 0,2..0,3
  .value Name 'b' Load - 0,5..0,6
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(targets=[M(t=...)])''',
r'''__FST_t += z''',
r'''a += z''', r'''
AugAssign - ROOT 0,0..0,6
  .target Name 'a' Store - 0,0..0,1
  .op Add - 0,2..0,3
  .value Name 'z' Load - 0,5..0,6
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''',
r'''u += __FST_v''',
r'''u += b''', r'''
AugAssign - ROOT 0,0..0,6
  .target Name 'u' Store - 0,0..0,1
  .op Add - 0,2..0,3
  .value Name 'b' Load - 0,5..0,6
'''),

('', None, None, None, {}, (None,
r'''[a]'''),
r'''MList(elts=[M(t=...)])''',
r'''u *= z''',
r'''u *= z''', r'''
AugAssign - ROOT 0,0..0,6
  .target Name 'u' Store - 0,0..0,1
  .op Mult - 0,2..0,3
  .value Name 'z' Load - 0,5..0,6
'''),
],

'basic_AnnAssign': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', ('AnnAssign',
r'''u: int = __FST_v  # new'''),
r'''u: int = b  # new''', r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'u' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Name 'b' Load - 0,9..0,10
  .simple 1
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(targets=[M(t=...)])''',
r'''__FST_t: int = z''',
r'''a: int = z''', r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'a' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Name 'z' Load - 0,9..0,10
  .simple 1
'''),

('', None, None, None, {}, (None,
r'''int'''),
r'''Name''', (None,
r'''u: __FST_ = z'''),
r'''u: int = z''', r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'u' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Name 'z' Load - 0,9..0,10
  .simple 1
'''),

('', None, None, None, {}, (None,
r'''[a]'''),
r'''MList(elts=[M(t=...)])''',
r'''__FST_t: int = z''',
r'''a: int = z''', r'''
AnnAssign - ROOT 0,0..0,10
  .target Name 'a' Store - 0,0..0,1
  .annotation Name 'int' Load - 0,3..0,6
  .value Name 'z' Load - 0,9..0,10
  .simple 1
'''),
],

'basic_For': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None,
r'''for __FST_v in _: pass'''),
r'''for b in _: pass''', r'''
For - ROOT 0,0..0,16
  .target Name 'b' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .body[1]
   0] Pass - 0,12..0,16
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(targets=[M(t=...)])''',
r'''for __FST_t in _: pass''',
r'''for a in _: pass''', r'''
For - ROOT 0,0..0,16
  .target Name 'a' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .body[1]
   0] Pass - 0,12..0,16
'''),

('', None, None, None, {}, (None,
r'''call()'''),
r'''Mexpr''',
r'''for _ in __FST_: pass''',
r'''for _ in call(): pass''', r'''
For - ROOT 0,0..0,21
  .target Name '_' Store - 0,4..0,5
  .iter Call - 0,9..0,15
    .func Name 'call' Load - 0,9..0,13
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(body=M(b=...))''', r'''
for _ in _:
    __FST_b
''', r'''
for _ in _:
    pass
''', r'''
For - ROOT 0,0..1,8
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .body[1]
   0] Pass - 1,4..1,8
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(body=M(b=...))''', r'''
for _ in _:
    call()
else:
    __FST_b
''', r'''
for _ in _:
    call()
else:
    pass
''', r'''
For - ROOT 0,0..3,8
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .body[1]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'call' Load - 1,4..1,8
  .orelse[1]
   0] Pass - 3,4..3,8
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf''', r'''
for _ in _:
    call()
else:
    __FST_DEL
''', r'''
for _ in _:
    call()
''', r'''
For - ROOT 0,0..1,10
  .target Name '_' Store - 0,4..0,5
  .iter Name '_' Load - 0,9..0,10
  .body[1]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'call' Load - 1,4..1,8
'''),

('', None, None, None, {}, ('For',
r'''for x in x: a ; b ; c ; d ; e'''),
r'''MFor(body=[..., MQSTAR(b=...), ...])''', ('For', r'''
for y in y: x; __FST_b; y
else: __FST_b
'''), r'''
for y in y:
    x
    b ; c ; d
    y
else:
    b ; c ; d
''', r'''
For - ROOT 0,0..5,13
  .target Name 'y' Store - 0,4..0,5
  .iter Name 'y' Load - 0,9..0,10
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
  .orelse[3]
   0] Expr - 5,4..5,5
     .value Name 'b' Load - 5,4..5,5
   1] Expr - 5,8..5,9
     .value Name 'c' Load - 5,8..5,9
   2] Expr - 5,12..5,13
     .value Name 'd' Load - 5,12..5,13
'''),
],

'basic_AsyncFor': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a, b'''),
r'''Mexpr''',
r'''async for _ in __FST_: pass''',
r'''async for _ in (a, b): pass''', r'''
AsyncFor - ROOT 0,0..0,27
  .target Name '_' Store - 0,10..0,11
  .iter Tuple - 0,15..0,21
    .elts[2]
     0] Name 'a' Load - 0,16..0,17
     1] Name 'b' Load - 0,19..0,20
    .ctx Load
  .body[1]
   0] Pass - 0,23..0,27
'''),

('', None, None, None, {}, ('AsyncFor',
r'''async for x in x: a ; b ; c ; d ; e'''),
r'''MAsyncFor(body=[..., MQSTAR(b=...), ...])''', ('AsyncFor', r'''
async for y in y: x; __FST_b; y
else: __FST_b
'''), r'''
async for y in y:
    x
    b ; c ; d
    y
else:
    b ; c ; d
''', r'''
AsyncFor - ROOT 0,0..5,13
  .target Name 'y' Store - 0,10..0,11
  .iter Name 'y' Load - 0,15..0,16
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
  .orelse[3]
   0] Expr - 5,4..5,5
     .value Name 'b' Load - 5,4..5,5
   1] Expr - 5,8..5,9
     .value Name 'c' Load - 5,8..5,9
   2] Expr - 5,12..5,13
     .value Name 'd' Load - 5,12..5,13
'''),
],

'basic_While': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None,
r'''while __FST_v: pass'''),
r'''while b: pass''', r'''
While - ROOT 0,0..0,13
  .test Name 'b' Load - 0,6..0,7
  .body[1]
   0] Pass - 0,9..0,13
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(targets=[M(t=...)])''',
r'''while __FST_t: pass''',
r'''while a: pass''', r'''
While - ROOT 0,0..0,13
  .test Name 'a' Load - 0,6..0,7
  .body[1]
   0] Pass - 0,9..0,13
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(body=M(b=...))''', r'''
while _:
    __FST_b
''', r'''
while _:
    pass
''', r'''
While - ROOT 0,0..1,8
  .test Name '_' Load - 0,6..0,7
  .body[1]
   0] Pass - 1,4..1,8
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(body=M(b=...))''', r'''
while _:
    call()
else:
    __FST_b
''', r'''
while _:
    call()
else:
    pass
''', r'''
While - ROOT 0,0..3,8
  .test Name '_' Load - 0,6..0,7
  .body[1]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'call' Load - 1,4..1,8
  .orelse[1]
   0] Pass - 3,4..3,8
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf''', r'''
while _:
    call()
else:
    __FST_DEL
''', r'''
while _:
    call()
''', r'''
While - ROOT 0,0..1,10
  .test Name '_' Load - 0,6..0,7
  .body[1]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'call' Load - 1,4..1,8
'''),

('', None, None, None, {}, ('While',
r'''while x: a ; b ; c ; d ; e'''),
r'''MWhile(body=[..., MQSTAR(b=...), ...])''', ('While', r'''
while y: x; __FST_b; y
else: __FST_b
'''), r'''
while y:
    x
    b ; c ; d
    y
else:
    b ; c ; d
''', r'''
While - ROOT 0,0..5,13
  .test Name 'y' Load - 0,6..0,7
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
  .orelse[3]
   0] Expr - 5,4..5,5
     .value Name 'b' Load - 5,4..5,5
   1] Expr - 5,8..5,9
     .value Name 'c' Load - 5,8..5,9
   2] Expr - 5,12..5,13
     .value Name 'd' Load - 5,12..5,13
'''),
],

'basic_If': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None,
r'''if __FST_v: pass'''),
r'''if b: pass''', r'''
If - ROOT 0,0..0,10
  .test Name 'b' Load - 0,3..0,4
  .body[1]
   0] Pass - 0,6..0,10
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(targets=[M(t=...)])''',
r'''if __FST_t: pass''',
r'''if a: pass''', r'''
If - ROOT 0,0..0,10
  .test Name 'a' Load - 0,3..0,4
  .body[1]
   0] Pass - 0,6..0,10
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(body=M(b=...))''', r'''
if _:
    __FST_b
''', r'''
if _:
    pass
''', r'''
If - ROOT 0,0..1,8
  .test Name '_' Load - 0,3..0,4
  .body[1]
   0] Pass - 1,4..1,8
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(body=M(b=...))''', r'''
if _:
    call()
else:
    __FST_b
''', r'''
if _:
    call()
else:
    pass
''', r'''
If - ROOT 0,0..3,8
  .test Name '_' Load - 0,3..0,4
  .body[1]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'call' Load - 1,4..1,8
  .orelse[1]
   0] Pass - 3,4..3,8
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf''', r'''
if _:
    call()
else:
    __FST_DEL
''', r'''
if _:
    call()
''', r'''
If - ROOT 0,0..1,10
  .test Name '_' Load - 0,3..0,4
  .body[1]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'call' Load - 1,4..1,8
'''),

('', None, None, None, {}, ('If',
r'''if x: a ; b ; c ; d ; e'''),
r'''MIf(body=[..., MQSTAR(b=...), ...])''', ('If', r'''
if y: x; __FST_b; y
else: __FST_b
'''), r'''
if y:
    x
    b ; c ; d
    y
else:
    b ; c ; d
''', r'''
If - ROOT 0,0..5,13
  .test Name 'y' Load - 0,3..0,4
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
  .orelse[3]
   0] Expr - 5,4..5,5
     .value Name 'b' Load - 5,4..5,5
   1] Expr - 5,8..5,9
     .value Name 'c' Load - 5,8..5,9
   2] Expr - 5,12..5,13
     .value Name 'd' Load - 5,12..5,13
'''),
],

'basic_With': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None,
r'''with __FST_v: pass'''),
r'''with b: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'b' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(targets=[M(t=...)])''',
r'''with __FST_t: pass''',
r'''with a: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'a' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', None, None, None, {}, (None,
r'''a'''),
r'''MName''',
r'''with x, __FST_DEL: pass''',
r'''with x: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', None, None, None, {}, ('withitem',
r'''a'''),
r'''Mwithitem''',
r'''with __FST_: pass''',
r'''with a: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'a' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', None, None, None, {}, ('withitem',
r'''a as b'''),
r'''Mwithitem''',
r'''with __FST_: pass''',
r'''with a as b: pass''', r'''
With - ROOT 0,0..0,17
  .items[1]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'b' Store - 0,10..0,11
  .body[1]
   0] Pass - 0,13..0,17
'''),

('', None, None, None, {}, ('withitem',
r'''a as b'''),
r'''Mwithitem(context_expr=M(ce=...))''',
r'''with __FST_ce: pass''',
r'''with a: pass''', r'''
With - ROOT 0,0..0,12
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name 'a' Load - 0,5..0,6
  .body[1]
   0] Pass - 0,8..0,12
'''),

('', None, None, None, {}, ('_withitems',
r'''a, b, c'''),
r'''M_withitems''',
r'''with __FST_: pass''',
r'''with a, b, c: pass''', r'''
With - ROOT 0,0..0,18
  .items[3]
   0] withitem - 0,5..0,6
     .context_expr Name 'a' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'b' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'c' Load - 0,11..0,12
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', None, None, None, {}, ('_withitems',
r'''a, b, c'''),
r'''M_withitems(items=M(wi=...))''',
r'''with __FST_wi: pass''',
r'''with a, b, c: pass''', r'''
With - ROOT 0,0..0,18
  .items[3]
   0] withitem - 0,5..0,6
     .context_expr Name 'a' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'b' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'c' Load - 0,11..0,12
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', None, None, None, {}, ('_withitems',
r'''a, x as y, c'''),
r'''M_withitems(items=[..., M(wi=...), ...])''',
r'''with __FST_wi: pass''',
r'''with x as y: pass''', r'''
With - ROOT 0,0..0,17
  .items[1]
   0] withitem - 0,5..0,11
     .context_expr Name 'x' Load - 0,5..0,6
     .optional_vars Name 'y' Store - 0,10..0,11
  .body[1]
   0] Pass - 0,13..0,17
'''),

('', None, None, None, {}, (None,
r'''a, b, c'''),
r'''MTuple''',
r'''with __FST_: pass''',
r'''with a, b, c: pass''', r'''
With - ROOT 0,0..0,18
  .items[3]
   0] withitem - 0,5..0,6
     .context_expr Name 'a' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'b' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'c' Load - 0,11..0,12
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', None, None, None, {}, (None,
r'''a'''),
r'''M(MName, t='a as b')''',
r'''with __FST_t: pass''',
r'''with a as b: pass''', r'''
With - ROOT 0,0..0,17
  .items[1]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'b' Store - 0,10..0,11
  .body[1]
   0] Pass - 0,13..0,17
'''),

('', None, None, None, {}, (None,
r'''a'''),
r'''M(MName, t='a as b, c as d')''',
r'''with __FST_t: pass''',
r'''with a as b, c as d: pass''', r'''
With - ROOT 0,0..0,25
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'b' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'c' Load - 0,13..0,14
     .optional_vars Name 'd' Store - 0,18..0,19
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', None, None, None, {}, (None,
r'''a'''),
r'''M(MName, t='a as b')''',
r'''with __FST_t, x as y: pass''',
r'''with a as b, x as y: pass''', r'''
With - ROOT 0,0..0,25
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'b' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'x' Load - 0,13..0,14
     .optional_vars Name 'y' Store - 0,18..0,19
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', None, None, None, {}, (None,
r'''a'''),
r'''M(MName, t='a as b, c as d')''',
r'''with __FST_t, x as y: pass''',
r'''with a as b, c as d, x as y: pass''', r'''
With - ROOT 0,0..0,33
  .items[3]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'b' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'c' Load - 0,13..0,14
     .optional_vars Name 'd' Store - 0,18..0,19
   2] withitem - 0,21..0,27
     .context_expr Name 'x' Load - 0,21..0,22
     .optional_vars Name 'y' Store - 0,26..0,27
  .body[1]
   0] Pass - 0,29..0,33
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(body=M(b=...))''', r'''
with _:
    __FST_b
''', r'''
with _:
    pass
''', r'''
With - ROOT 0,0..1,8
  .items[1]
   0] withitem - 0,5..0,6
     .context_expr Name '_' Load - 0,5..0,6
  .body[1]
   0] Pass - 1,4..1,8
'''),

('', None, None, None, {}, ('With',
r'''with a, b, c, d, e: a ; b ; c ; d ; e'''),
r'''MWith(items=[..., MQSTAR(i=...), ...], body=[..., MQSTAR(b=...), ...])''', ('With',
r'''with x, __FST_i, y: x; __FST_b; y'''), r'''
with x, b, c, d, y:
    x
    b ; c ; d
    y
''', r'''
With - ROOT 0,0..3,5
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'b' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'c' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'd' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'y' Load - 0,17..0,18
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
'''),
],

'basic_AsyncWith': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None,
r'''async with __FST_v: pass'''),
r'''async with b: pass''', r'''
AsyncWith - ROOT 0,0..0,18
  .items[1]
   0] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', None, None, None, {}, ('AsyncWith',
r'''async with a, b, c, d, e: a ; b ; c ; d ; e'''),
r'''MAsyncWith(items=[..., MQSTAR(i=...), ...], body=[..., MQSTAR(b=...), ...])''', ('AsyncWith',
r'''async with x, __FST_i, y: x; __FST_b; y'''), r'''
async with x, b, c, d, y:
    x
    b ; c ; d
    y
''', r'''
AsyncWith - ROOT 0,0..3,5
  .items[5]
   0] withitem - 0,11..0,12
     .context_expr Name 'x' Load - 0,11..0,12
   1] withitem - 0,14..0,15
     .context_expr Name 'b' Load - 0,14..0,15
   2] withitem - 0,17..0,18
     .context_expr Name 'c' Load - 0,17..0,18
   3] withitem - 0,20..0,21
     .context_expr Name 'd' Load - 0,20..0,21
   4] withitem - 0,23..0,24
     .context_expr Name 'y' Load - 0,23..0,24
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
'''),
],

'basic_Match': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None, r'''
match __FST_v:
    case _: pass
'''), r'''
match b:
    case _: pass
''', r'''
Match - ROOT 0,0..1,16
  .subject Name 'b' Load - 0,6..0,7
  .cases[1]
   0] match_case - 1,4..1,16
     .pattern MatchAs - 1,9..1,10
     .body[1]
      0] Pass - 1,12..1,16
'''),

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(body=M(b=...))''', (None, r'''
match x:
    case _: __FST_b
'''), r'''
match x:
    case _:
        pass
''', r'''
Match - ROOT 0,0..2,12
  .subject Name 'x' Load - 0,6..0,7
  .cases[1]
   0] match_case - 1,4..2,12
     .pattern MatchAs - 1,9..1,10
     .body[1]
      0] Pass - 2,8..2,12
'''),

('', None, None, None, {}, ('Match', r'''
match old:
    case a if b:  # blah
        a = b  # bloh
'''),
r'''MMatch(cases=M(m=...))''', ('Match', r'''
match new:
    case '...': __FST_m
    case '...': __FST_m
'''), r'''
match new:
    case a if b:  # blah
        a = b  # bloh
    case a if b:  # blah
        a = b  # bloh
''', r'''
Match - ROOT 0,0..4,13
  .subject Name 'new' Load - 0,6..0,9
  .cases[2]
   0] match_case - 1,4..2,13
     .pattern MatchAs - 1,9..1,10
       .name 'a'
     .guard Name 'b' Load - 1,14..1,15
     .body[1]
      0] Assign - 2,8..2,13
        .targets[1]
         0] Name 'a' Store - 2,8..2,9
        .value Name 'b' Load - 2,12..2,13
   1] match_case - 3,4..4,13
     .pattern MatchAs - 3,9..3,10
       .name 'a'
     .guard Name 'b' Load - 3,14..3,15
     .body[1]
      0] Assign - 4,8..4,13
        .targets[1]
         0] Name 'a' Store - 4,8..4,9
        .value Name 'b' Load - 4,12..4,13
'''),

('', None, None, None, {}, ('Match', r'''
match old:
    case a if b: pass
    case b as a: pass
'''),
r'''MMatch(cases=M(m=...))''', ('Match', r'''
match new:
    case '...': __FST_m
    case '...': __FST_m
'''), r'''
match new:
    case a if b: pass
    case b as a: pass
    case a if b: pass
    case b as a: pass
''', r'''
Match - ROOT 0,0..4,21
  .subject Name 'new' Load - 0,6..0,9
  .cases[4]
   0] match_case - 1,4..1,21
     .pattern MatchAs - 1,9..1,10
       .name 'a'
     .guard Name 'b' Load - 1,14..1,15
     .body[1]
      0] Pass - 1,17..1,21
   1] match_case - 2,4..2,21
     .pattern MatchAs - 2,9..2,15
       .pattern MatchAs - 2,9..2,10
         .name 'b'
       .name 'a'
     .body[1]
      0] Pass - 2,17..2,21
   2] match_case - 3,4..3,21
     .pattern MatchAs - 3,9..3,10
       .name 'a'
     .guard Name 'b' Load - 3,14..3,15
     .body[1]
      0] Pass - 3,17..3,21
   3] match_case - 4,4..4,21
     .pattern MatchAs - 4,9..4,15
       .pattern MatchAs - 4,9..4,10
         .name 'b'
       .name 'a'
     .body[1]
      0] Pass - 4,17..4,21
'''),

('', None, None, None, {}, ('Match', r'''
match old:
    case a: pass
    case b: pass
    case c: pass
    case d: pass
    case e: pass
'''),
r'''MMatch(cases=[..., MQSTAR(m=...), ...])''', ('Match', r'''
match new:
    case x: pass
    case '...': __FST_m
    case y: pass
'''), r'''
match new:
    case x: pass
    case b: pass
    case c: pass
    case d: pass
    case y: pass
''', r'''
Match - ROOT 0,0..5,16
  .subject Name 'new' Load - 0,6..0,9
  .cases[5]
   0] match_case - 1,4..1,16
     .pattern MatchAs - 1,9..1,10
       .name 'x'
     .body[1]
      0] Pass - 1,12..1,16
   1] match_case - 2,4..2,16
     .pattern MatchAs - 2,9..2,10
       .name 'b'
     .body[1]
      0] Pass - 2,12..2,16
   2] match_case - 3,4..3,16
     .pattern MatchAs - 3,9..3,10
       .name 'c'
     .body[1]
      0] Pass - 3,12..3,16
   3] match_case - 4,4..4,16
     .pattern MatchAs - 4,9..4,10
       .name 'd'
     .body[1]
      0] Pass - 4,12..4,16
   4] match_case - 5,4..5,16
     .pattern MatchAs - 5,9..5,10
       .name 'y'
     .body[1]
      0] Pass - 5,12..5,16
'''),

('', None, None, None, {}, ('Match', r'''
match old:
    case a: pass
'''),
r'''MMatch(cases=M(m=...))''', ('Match', r'''
match new:
    case x: pass
    case '...': __FST_DEL
    case y: pass
'''), r'''
match new:
    case x: pass
    case y: pass
''', r'''
Match - ROOT 0,0..2,16
  .subject Name 'new' Load - 0,6..0,9
  .cases[2]
   0] match_case - 1,4..1,16
     .pattern MatchAs - 1,9..1,10
       .name 'x'
     .body[1]
      0] Pass - 1,12..1,16
   1] match_case - 2,4..2,16
     .pattern MatchAs - 2,9..2,10
       .name 'y'
     .body[1]
      0] Pass - 2,12..2,16
'''),
],

'basic_Raise': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None,
r'''raise __FST_v'''),
r'''raise b''', r'''
Raise - ROOT 0,0..0,7
  .exc Name 'b' Load - 0,6..0,7
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None,
r'''raise __FST_v from None'''),
r'''raise b from None''', r'''
Raise - ROOT 0,0..0,17
  .exc Name 'b' Load - 0,6..0,7
  .cause Constant None - 0,13..0,17
'''),

('', None, None, None, {}, (None,
r'''a = b'''),
r'''MAssign(value=M(v=...))''', (None,
r'''raise exc from __FST_v'''),
r'''raise exc from b''', r'''
Raise - ROOT 0,0..0,16
  .exc Name 'exc' Load - 0,6..0,9
  .cause Name 'b' Load - 0,15..0,16
'''),

('', None, None, None, {}, (None,
r'''raise a from b'''),
r'''MRaise(exc=M(e=...), cause=M(c=...))''', (None,
r'''raise __FST_e from __FST_c'''),
r'''raise a from b''', r'''
Raise - ROOT 0,0..0,14
  .exc Name 'a' Load - 0,6..0,7
  .cause Name 'b' Load - 0,13..0,14
'''),

('', None, None, None, {}, (None,
r'''raise a'''),
r'''MRaise(exc=M(e=...), cause=M(c=...))''', (None,
r'''raise __FST_e from __FST_c'''),
r'''raise a''', r'''
Raise - ROOT 0,0..0,7
  .exc Name 'a' Load - 0,6..0,7
'''),

('', None, None, None, {}, (None,
r'''raise'''),
r'''MRaise(exc=M(e=...), cause=M(c=...))''', (None,
r'''raise __FST_e from __FST_c'''),
r'''raise''',
r'''Raise - ROOT 0,0..0,5'''),

('', None, None, None, {}, (None,
r'''raise a from b'''),
r'''MRaise(exc=M(e=...), cause=M(c=...))''', (None,
r'''raise __FST__DEL from __FST_c'''),
r'''raise''',
r'''Raise - ROOT 0,0..0,5'''),
],

'basic_Try': [  # ................................................................................

('', None, None, None, {}, ('expr',
r'''call()'''),
r'''Mexpr''', ('Try', r'''
try: __FST_
finally: pass
'''), r'''
try: call()
finally: pass
''', r'''
Try - ROOT 0,0..1,13
  .body[1]
   0] Expr - 0,5..0,11
     .value Call - 0,5..0,11
       .func Name 'call' Load - 0,5..0,9
  .finalbody[1]
   0] Pass - 1,9..1,13
'''),

('', None, None, None, {}, ('expr',
r'''call()'''),
r'''Mexpr''', ('Try', r'''
try: pass
except: __FST_
'''), r'''
try: pass
except: call()
''', r'''
Try - ROOT 0,0..1,14
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,14
     .body[1]
      0] Expr - 1,8..1,14
        .value Call - 1,8..1,14
          .func Name 'call' Load - 1,8..1,12
'''),

('', None, None, None, {}, ('expr',
r'''call()'''),
r'''Mexpr''', ('Try', r'''
try: pass
except: pass
else: __FST_
'''), r'''
try: pass
except: pass
else: call()
''', r'''
Try - ROOT 0,0..2,12
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
  .orelse[1]
   0] Expr - 2,6..2,12
     .value Call - 2,6..2,12
       .func Name 'call' Load - 2,6..2,10
'''),

('', None, None, None, {}, ('expr',
r'''call()'''),
r'''Mexpr''', ('Try', r'''
try: pass
except: pass
else: __FST_DEL
'''), r'''
try: pass
except: pass
''', r'''
Try - ROOT 0,0..1,12
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', None, None, None, {}, ('expr',
r'''call()'''),
r'''Mexpr''', ('Try', r'''
try: pass
finally: __FST_
'''), r'''
try: pass
finally: call()
''', r'''
Try - ROOT 0,0..1,15
  .body[1]
   0] Pass - 0,5..0,9
  .finalbody[1]
   0] Expr - 1,9..1,15
     .value Call - 1,9..1,15
       .func Name 'call' Load - 1,9..1,13
'''),

('', None, None, None, {}, ('expr',
r'''call()'''),
r'''Mexpr''', ('Try', r'''
try: pass
except: pass
finally: __FST_DEL
'''), r'''
try: pass
except: pass
''', r'''
Try - ROOT 0,0..1,12
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,12
     .body[1]
      0] Pass - 1,8..1,12
'''),

('', None, None, None, {}, ('Try', r'''
try: a ; b ; c ; d ; e
finally: pass
'''),
r'''MTry(body=[..., MQSTAR(b=...), ...])''', ('Try', r'''
try: x; __FST_b; y
except: __FST_b
else: __FST_b
finally: __FST_b
'''), r'''
try:
    x
    b ; c ; d
    y
except:
    b ; c ; d

else:
    b ; c ; d
finally:
    b ; c ; d
''', r'''
Try - ROOT 0,0..10,13
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
  .handlers[1]
   0] ExceptHandler - 4,0..5,13
     .body[3]
      0] Expr - 5,4..5,5
        .value Name 'b' Load - 5,4..5,5
      1] Expr - 5,8..5,9
        .value Name 'c' Load - 5,8..5,9
      2] Expr - 5,12..5,13
        .value Name 'd' Load - 5,12..5,13
  .orelse[3]
   0] Expr - 8,4..8,5
     .value Name 'b' Load - 8,4..8,5
   1] Expr - 8,8..8,9
     .value Name 'c' Load - 8,8..8,9
   2] Expr - 8,12..8,13
     .value Name 'd' Load - 8,12..8,13
  .finalbody[3]
   0] Expr - 10,4..10,5
     .value Name 'b' Load - 10,4..10,5
   1] Expr - 10,8..10,9
     .value Name 'c' Load - 10,8..10,9
   2] Expr - 10,12..10,13
     .value Name 'd' Load - 10,12..10,13
'''),

('', None, None, None, {}, ('Try', r'''
try: old
except a as b:  # blah
    a = b  # bloh
'''),
r'''MTry(handlers=M(m=...))''', ('Try', r'''
try: new
except '...': __FST_m
except '...': __FST_m
'''), r'''
try: new
except a as b:  # blah
    a = b  # bloh
except a as b:  # blah
    a = b  # bloh
''', r'''
Try - ROOT 0,0..4,9
  .body[1]
   0] Expr - 0,5..0,8
     .value Name 'new' Load - 0,5..0,8
  .handlers[2]
   0] ExceptHandler - 1,0..2,9
     .type Name 'a' Load - 1,7..1,8
     .name 'b'
     .body[1]
      0] Assign - 2,4..2,9
        .targets[1]
         0] Name 'a' Store - 2,4..2,5
        .value Name 'b' Load - 2,8..2,9
   1] ExceptHandler - 3,0..4,9
     .type Name 'a' Load - 3,7..3,8
     .name 'b'
     .body[1]
      0] Assign - 4,4..4,9
        .targets[1]
         0] Name 'a' Store - 4,4..4,5
        .value Name 'b' Load - 4,8..4,9
'''),

('', None, None, None, {}, ('Try', r'''
try: old
except a as b: pass
except b as a: pass
'''),
r'''MTry(handlers=M(m=...))''', ('Try', r'''
try: new
except '...': __FST_m
except '...': __FST_m
'''), r'''
try: new
except a as b: pass
except b as a: pass
except a as b: pass
except b as a: pass
''', r'''
Try - ROOT 0,0..4,19
  .body[1]
   0] Expr - 0,5..0,8
     .value Name 'new' Load - 0,5..0,8
  .handlers[4]
   0] ExceptHandler - 1,0..1,19
     .type Name 'a' Load - 1,7..1,8
     .name 'b'
     .body[1]
      0] Pass - 1,15..1,19
   1] ExceptHandler - 2,0..2,19
     .type Name 'b' Load - 2,7..2,8
     .name 'a'
     .body[1]
      0] Pass - 2,15..2,19
   2] ExceptHandler - 3,0..3,19
     .type Name 'a' Load - 3,7..3,8
     .name 'b'
     .body[1]
      0] Pass - 3,15..3,19
   3] ExceptHandler - 4,0..4,19
     .type Name 'b' Load - 4,7..4,8
     .name 'a'
     .body[1]
      0] Pass - 4,15..4,19
'''),

('', None, None, None, {}, ('Try', r'''
try: old
except a: pass
except b: pass
except c: pass
except d: pass
except e: pass
'''),
r'''MTry(handlers=[..., MQSTAR(m=...), ...])''', ('Try', r'''
try: new
except x: pass
except '...': __FST_m
except y: pass
'''), r'''
try: new
except x: pass
except b: pass
except c: pass
except d: pass
except y: pass
''', r'''
Try - ROOT 0,0..5,14
  .body[1]
   0] Expr - 0,5..0,8
     .value Name 'new' Load - 0,5..0,8
  .handlers[5]
   0] ExceptHandler - 1,0..1,14
     .type Name 'x' Load - 1,7..1,8
     .body[1]
      0] Pass - 1,10..1,14
   1] ExceptHandler - 2,0..2,14
     .type Name 'b' Load - 2,7..2,8
     .body[1]
      0] Pass - 2,10..2,14
   2] ExceptHandler - 3,0..3,14
     .type Name 'c' Load - 3,7..3,8
     .body[1]
      0] Pass - 3,10..3,14
   3] ExceptHandler - 4,0..4,14
     .type Name 'd' Load - 4,7..4,8
     .body[1]
      0] Pass - 4,10..4,14
   4] ExceptHandler - 5,0..5,14
     .type Name 'y' Load - 5,7..5,8
     .body[1]
      0] Pass - 5,10..5,14
'''),

('', None, None, None, {}, ('Try', r'''
try: old
except a: pass
'''),
r'''MTry(handlers=M(m=...))''', ('Try', r'''
try: new
except x: pass
except '...': __FST_DEL
except y: pass
'''), r'''
try: new
except x: pass
except y: pass
''', r'''
Try - ROOT 0,0..2,14
  .body[1]
   0] Expr - 0,5..0,8
     .value Name 'new' Load - 0,5..0,8
  .handlers[2]
   0] ExceptHandler - 1,0..1,14
     .type Name 'x' Load - 1,7..1,8
     .body[1]
      0] Pass - 1,10..1,14
   1] ExceptHandler - 2,0..2,14
     .type Name 'y' Load - 2,7..2,8
     .body[1]
      0] Pass - 2,10..2,14
'''),
],

'basic_TryStar': [  # ................................................................................

('', None, None, None, {'_ver': 11}, ('expr',
r'''call()'''),
r'''Mexpr''', ('TryStar', r'''
try: __FST_
except* Exception: pass
finally: pass
'''), r'''
try: call()
except* Exception: pass
finally: pass
''', r'''
TryStar - ROOT 0,0..2,13
  .body[1]
   0] Expr - 0,5..0,11
     .value Call - 0,5..0,11
       .func Name 'call' Load - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,23
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Pass - 1,19..1,23
  .finalbody[1]
   0] Pass - 2,9..2,13
'''),

('', None, None, None, {'_ver': 11}, ('expr',
r'''call()'''),
r'''Mexpr''', ('TryStar', r'''
try: pass
except* Exception: __FST_
'''), r'''
try: pass
except* Exception: call()
''', r'''
TryStar - ROOT 0,0..1,25
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,25
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Expr - 1,19..1,25
        .value Call - 1,19..1,25
          .func Name 'call' Load - 1,19..1,23
'''),

('', None, None, None, {'_ver': 11}, ('expr',
r'''call()'''),
r'''Mexpr''', ('TryStar', r'''
try: pass
except* Exception: pass
else: __FST_
'''), r'''
try: pass
except* Exception: pass
else: call()
''', r'''
TryStar - ROOT 0,0..2,12
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,23
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Pass - 1,19..1,23
  .orelse[1]
   0] Expr - 2,6..2,12
     .value Call - 2,6..2,12
       .func Name 'call' Load - 2,6..2,10
'''),

('', None, None, None, {'_ver': 11}, ('expr',
r'''call()'''),
r'''Mexpr''', ('TryStar', r'''
try: pass
except* Exception: pass
else: __FST_DEL
'''), r'''
try: pass
except* Exception: pass
''', r'''
TryStar - ROOT 0,0..1,23
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,23
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Pass - 1,19..1,23
'''),

('', None, None, None, {'_ver': 11}, ('expr',
r'''call()'''),
r'''Mexpr''', ('TryStar', r'''
try: pass
except* Exception: pass
finally: __FST_
'''), r'''
try: pass
except* Exception: pass
finally: call()
''', r'''
TryStar - ROOT 0,0..2,15
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,23
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Pass - 1,19..1,23
  .finalbody[1]
   0] Expr - 2,9..2,15
     .value Call - 2,9..2,15
       .func Name 'call' Load - 2,9..2,13
'''),

('', None, None, None, {'_ver': 11}, ('expr',
r'''call()'''),
r'''Mexpr''', ('TryStar', r'''
try: pass
except* Exception: pass
finally: __FST_DEL
'''), r'''
try: pass
except* Exception: pass
''', r'''
TryStar - ROOT 0,0..1,23
  .body[1]
   0] Pass - 0,5..0,9
  .handlers[1]
   0] ExceptHandler - 1,0..1,23
     .type Name 'Exception' Load - 1,8..1,17
     .body[1]
      0] Pass - 1,19..1,23
'''),

('', None, None, None, {'_ver': 11}, ('TryStar', r'''
try: a ; b ; c ; d ; e
except* Exception: pass
'''),
r'''MTryStar(body=[..., MQSTAR(b=...), ...])''', ('TryStar', r'''
try: x; __FST_b; y
except* Exception: __FST_b
else: __FST_b
finally: __FST_b
'''), r'''
try:
    x
    b ; c ; d
    y
except* Exception:
    b ; c ; d

else:
    b ; c ; d
finally:
    b ; c ; d
''', r'''
TryStar - ROOT 0,0..10,13
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
  .handlers[1]
   0] ExceptHandler - 4,0..5,13
     .type Name 'Exception' Load - 4,8..4,17
     .body[3]
      0] Expr - 5,4..5,5
        .value Name 'b' Load - 5,4..5,5
      1] Expr - 5,8..5,9
        .value Name 'c' Load - 5,8..5,9
      2] Expr - 5,12..5,13
        .value Name 'd' Load - 5,12..5,13
  .orelse[3]
   0] Expr - 8,4..8,5
     .value Name 'b' Load - 8,4..8,5
   1] Expr - 8,8..8,9
     .value Name 'c' Load - 8,8..8,9
   2] Expr - 8,12..8,13
     .value Name 'd' Load - 8,12..8,13
  .finalbody[3]
   0] Expr - 10,4..10,5
     .value Name 'b' Load - 10,4..10,5
   1] Expr - 10,8..10,9
     .value Name 'c' Load - 10,8..10,9
   2] Expr - 10,12..10,13
     .value Name 'd' Load - 10,12..10,13
'''),

('', None, None, None, {'_ver': 11}, ('TryStar', r'''
try: old
except* a as b:  # blah
    a = b  # bloh
'''),
r'''MTryStar(handlers=M(m=...))''', ('TryStar', r'''
try: new
except* '...': __FST_m
except* '...': __FST_m
'''), r'''
try: new
except* a as b:  # blah
    a = b  # bloh
except* a as b:  # blah
    a = b  # bloh
''', r'''
TryStar - ROOT 0,0..4,9
  .body[1]
   0] Expr - 0,5..0,8
     .value Name 'new' Load - 0,5..0,8
  .handlers[2]
   0] ExceptHandler - 1,0..2,9
     .type Name 'a' Load - 1,8..1,9
     .name 'b'
     .body[1]
      0] Assign - 2,4..2,9
        .targets[1]
         0] Name 'a' Store - 2,4..2,5
        .value Name 'b' Load - 2,8..2,9
   1] ExceptHandler - 3,0..4,9
     .type Name 'a' Load - 3,8..3,9
     .name 'b'
     .body[1]
      0] Assign - 4,4..4,9
        .targets[1]
         0] Name 'a' Store - 4,4..4,5
        .value Name 'b' Load - 4,8..4,9
'''),

('', None, None, None, {'_ver': 11}, ('TryStar', r'''
try: old
except* a as b: pass
except* b as a: pass
'''),
r'''MTryStar(handlers=M(m=...))''', ('TryStar', r'''
try: new
except* '...': __FST_m
except* '...': __FST_m
'''), r'''
try: new
except* a as b: pass
except* b as a: pass
except* a as b: pass
except* b as a: pass
''', r'''
TryStar - ROOT 0,0..4,20
  .body[1]
   0] Expr - 0,5..0,8
     .value Name 'new' Load - 0,5..0,8
  .handlers[4]
   0] ExceptHandler - 1,0..1,20
     .type Name 'a' Load - 1,8..1,9
     .name 'b'
     .body[1]
      0] Pass - 1,16..1,20
   1] ExceptHandler - 2,0..2,20
     .type Name 'b' Load - 2,8..2,9
     .name 'a'
     .body[1]
      0] Pass - 2,16..2,20
   2] ExceptHandler - 3,0..3,20
     .type Name 'a' Load - 3,8..3,9
     .name 'b'
     .body[1]
      0] Pass - 3,16..3,20
   3] ExceptHandler - 4,0..4,20
     .type Name 'b' Load - 4,8..4,9
     .name 'a'
     .body[1]
      0] Pass - 4,16..4,20
'''),

('', None, None, None, {'_ver': 11}, ('TryStar', r'''
try: old
except* a: pass
except* b: pass
except* c: pass
except* d: pass
except* e: pass
'''),
r'''MTryStar(handlers=[..., MQSTAR(m=...), ...])''', ('TryStar', r'''
try: new
except* x: pass
except* '...': __FST_m
except* y: pass
'''), r'''
try: new
except* x: pass
except* b: pass
except* c: pass
except* d: pass
except* y: pass
''', r'''
TryStar - ROOT 0,0..5,15
  .body[1]
   0] Expr - 0,5..0,8
     .value Name 'new' Load - 0,5..0,8
  .handlers[5]
   0] ExceptHandler - 1,0..1,15
     .type Name 'x' Load - 1,8..1,9
     .body[1]
      0] Pass - 1,11..1,15
   1] ExceptHandler - 2,0..2,15
     .type Name 'b' Load - 2,8..2,9
     .body[1]
      0] Pass - 2,11..2,15
   2] ExceptHandler - 3,0..3,15
     .type Name 'c' Load - 3,8..3,9
     .body[1]
      0] Pass - 3,11..3,15
   3] ExceptHandler - 4,0..4,15
     .type Name 'd' Load - 4,8..4,9
     .body[1]
      0] Pass - 4,11..4,15
   4] ExceptHandler - 5,0..5,15
     .type Name 'y' Load - 5,8..5,9
     .body[1]
      0] Pass - 5,11..5,15
'''),

('', None, None, None, {'_ver': 11}, ('TryStar', r'''
try: old
except* a: pass
'''),
r'''MTryStar(handlers=M(m=...))''', ('TryStar', r'''
try: new
except* x: pass
except* '...': __FST_DEL
except* y: pass
'''), r'''
try: new
except* x: pass
except* y: pass
''', r'''
TryStar - ROOT 0,0..2,15
  .body[1]
   0] Expr - 0,5..0,8
     .value Name 'new' Load - 0,5..0,8
  .handlers[2]
   0] ExceptHandler - 1,0..1,15
     .type Name 'x' Load - 1,8..1,9
     .body[1]
      0] Pass - 1,11..1,15
   1] ExceptHandler - 2,0..2,15
     .type Name 'y' Load - 2,8..2,9
     .body[1]
      0] Pass - 2,11..2,15
'''),
],

'basic_Assert': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a == b'''),
r'''Compare''', (None,
r'''assert __FST_'''),
r'''assert a == b''', r'''
Assert - ROOT 0,0..0,13
  .test Compare - 0,7..0,13
    .left Name 'a' Load - 0,7..0,8
    .ops[1]
     0] Eq - 0,9..0,11
    .comparators[1]
     0] Name 'b' Load - 0,12..0,13
'''),

('', None, None, None, {}, (None,
r'''"msg"'''),
r'''Constant''', (None,
r'''assert __FST_, __FST_'''),
r'''assert "msg", "msg"''', r'''
Assert - ROOT 0,0..0,19
  .test Constant 'msg' - 0,7..0,12
  .msg Constant 'msg' - 0,14..0,19
'''),
],

'basic_Import': [  # ................................................................................

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=M(n=...))''', (None,
r'''import __FST_n  # new'''),
r'''import a, b.c, d as e  # new''', r'''
Import - ROOT 0,0..0,21
  .names[3]
   0] alias - 0,7..0,8
     .name 'a'
   1] alias - 0,10..0,13
     .name 'b.c'
   2] alias - 0,15..0,21
     .name 'd'
     .asname 'e'
'''),

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=[..., M(n=...), ...])''', (None,
r'''import __FST_n  # new'''),
r'''import b.c  # new''', r'''
Import - ROOT 0,0..0,10
  .names[1]
   0] alias - 0,7..0,10
     .name 'b.c'
'''),

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=[..., M(n=...), ...])''', (None,
r'''import __FST_n as z  # new'''),
r'''import b.c as z  # new''', r'''
Import - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,7..0,15
     .name 'b.c'
     .asname 'z'
'''),

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=[M(n=...), MQSTAR])''', (None,
r'''import x as __FST_n  # new'''),
r'''import x as a  # new''', r'''
Import - ROOT 0,0..0,13
  .names[1]
   0] alias - 0,7..0,13
     .name 'x'
     .asname 'a'
'''),

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=[..., M(n=...), ...])''', (None,
r'''import x as __FST_n  # new'''),
r'''**ParseError("expecting identifier, got 'b.c'")**'''),

('', None, None, None, {}, ('ImportFrom',
r'''from . import *'''),
r'''MImportFrom(names=M(n=...))''', (None,
r'''import __FST_n  # new'''),
r'''**NodeError("'*' star alias not allowed")**'''),

('', None, None, None, {}, ('Import',
r'''import a, b, c, d, e'''),
r'''MImport(names=[..., MQSTAR(i=...), ...])''', ('Import',
r'''import x, __FST_i, y'''),
r'''import x, b, c, d, y''', r'''
Import - ROOT 0,0..0,20
  .names[5]
   0] alias - 0,7..0,8
     .name 'x'
   1] alias - 0,10..0,11
     .name 'b'
   2] alias - 0,13..0,14
     .name 'c'
   3] alias - 0,16..0,17
     .name 'd'
   4] alias - 0,19..0,20
     .name 'y'
'''),
],

'basic_ImportFrom': [  # ................................................................................

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=M(n=...))''', (None,
r'''from . import __FST_n  # new'''),
r'''**NodeError("'.' dotted alias not allowed")**'''),

('', None, None, None, {}, ('Import',
r'''import a, d as e'''),
r'''MImport(names=M(n=...))''', (None,
r'''from . import __FST_n  # new'''),
r'''from . import a, d as e  # new''', r'''
ImportFrom - ROOT 0,0..0,23
  .names[2]
   0] alias - 0,14..0,15
     .name 'a'
   1] alias - 0,17..0,23
     .name 'd'
     .asname 'e'
  .level 1
'''),

('', None, None, None, {}, ('Import',
r'''import a.b, c, d as e'''),
r'''MImport(names=[..., M(n=...), ...])''', (None,
r'''from . import __FST_n  # new'''),
r'''from . import c  # new''', r'''
ImportFrom - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,14..0,15
     .name 'c'
  .level 1
'''),

('', None, None, None, {}, ('Import',
r'''import a.b, c, d as e'''),
r'''MImport(names=[..., M(n=...), ...])''', (None,
r'''from . import __FST_n as z  # new'''),
r'''from . import c as z  # new''', r'''
ImportFrom - ROOT 0,0..0,20
  .names[1]
   0] alias - 0,14..0,20
     .name 'c'
     .asname 'z'
  .level 1
'''),

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=[M(n=...), MQSTAR])''', (None,
r'''from . import x as __FST_n  # new'''),
r'''from . import x as a  # new''', r'''
ImportFrom - ROOT 0,0..0,20
  .names[1]
   0] alias - 0,14..0,20
     .name 'x'
     .asname 'a'
  .level 1
'''),

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=[..., M(n=...), ...])''', (None,
r'''from . import x as __FST_n  # new'''),
r'''**ParseError("expecting identifier, got 'b.c'")**'''),

('', None, None, None, {}, ('Import',
r'''import a'''),
r'''MImport(names=[M(n=...)])''', (None,
r'''from . import x, __FST_DEL  # new'''),
r'''from . import x  # new''', r'''
ImportFrom - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,14..0,15
     .name 'x'
  .level 1
'''),

('', None, None, None, {}, ('ImportFrom',
r'''from . import *'''),
r'''MImportFrom(names=M(n=...))''', (None,
r'''from . import __FST_n  # new'''),
r'''from . import *  # new''', r'''
ImportFrom - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,14..0,15
     .name '*'
  .level 1
'''),

('', None, None, None, {}, ('ImportFrom',
r'''from . import *'''),
r'''MImportFrom(names=M(n=...))''', (None,
r'''from . import __FST_n as z  # new'''),
r'''**ParseError("expecting identifier, got '*'")**'''),

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=M(n=...))''', (None,
r'''from .__FST_n import *'''),
r'''**ParseError("expecting dotted identifier, got 'a, b.c, d as e'")**'''),

('', None, None, None, {}, ('Import',
r'''import a'''),
r'''MImport(names=M(n=...))''', (None,
r'''from .__FST_n import *'''),
r'''from .a import *''', r'''
ImportFrom - ROOT 0,0..0,16
  .module 'a'
  .names[1]
   0] alias - 0,15..0,16
     .name '*'
  .level 1
'''),

('', None, None, None, {}, ('Import',
r'''import a.b'''),
r'''MImport(names=M(n=...))''', (None,
r'''from .__FST_n import *'''),
r'''from .a.b import *''', r'''
ImportFrom - ROOT 0,0..0,18
  .module 'a.b'
  .names[1]
   0] alias - 0,17..0,18
     .name '*'
  .level 1
'''),

('', None, None, None, {}, ('Import',
r'''import a.b'''),
r'''MImport(names=M(n=...))''', (None,
r'''from .__FST_DEL import *'''),
r'''from . import *''', r'''
ImportFrom - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,14..0,15
     .name '*'
  .level 1
'''),

('', None, None, None, {}, ('ImportFrom',
r'''from . import a, b, c, d, e'''),
r'''MImportFrom(names=[..., MQSTAR(i=...), ...])''', ('ImportFrom',
r'''from . import x, __FST_i, y'''),
r'''from . import x, b, c, d, y''', r'''
ImportFrom - ROOT 0,0..0,27
  .names[5]
   0] alias - 0,14..0,15
     .name 'x'
   1] alias - 0,17..0,18
     .name 'b'
   2] alias - 0,20..0,21
     .name 'c'
   3] alias - 0,23..0,24
     .name 'd'
   4] alias - 0,26..0,27
     .name 'y'
  .level 1
'''),
],

'basic_Global': [  # ................................................................................

('', None, None, None, {}, ('Global',
r'''global a'''),
r'''MGlobal(names=M(n=...))''', (None,
r'''global __FST_n  # new'''),
r'''global a  # new''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'a'
'''),

('', None, None, None, {}, ('Global',
r'''global a, b, c'''),
r'''MGlobal(names=M(n=...))''', (None,
r'''global __FST_n  # new'''),
r'''global a, b, c  # new''', r'''
Global - ROOT 0,0..0,14
  .names[3]
   0] 'a'
   1] 'b'
   2] 'c'
'''),

('', None, None, None, {}, ('Global',
r'''global a, b, c'''),
r'''MGlobal(names=[..., M(n=...), ...])''', (None,
r'''global __FST_n  # new'''),
r'''global b  # new''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'b'
'''),

('', None, None, None, {}, ('Global',
r'''global a, b, c'''),
r'''MGlobal(names=[..., M(n=...), ...])''', (None,
r'''global x, __FST_DEL'''),
r'''global x''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'x'
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c]'''),
r'''MList(elts=M(n=...))''', (None,
r'''global __FST_n  # new'''),
r'''global a, b, c  # new''', r'''
Global - ROOT 0,0..0,14
  .names[3]
   0] 'a'
   1] 'b'
   2] 'c'
'''),

('', None, None, None, {}, ('Global',
r'''global a, b, c, d, e'''),
r'''MGlobal(names=[..., MQSTAR(i=...), ...])''', ('Global',
r'''global x, __FST_i, y'''),
r'''global x, b, c, d, y''', r'''
Global - ROOT 0,0..0,20
  .names[5]
   0] 'x'
   1] 'b'
   2] 'c'
   3] 'd'
   4] 'y'
'''),
],

'basic_Nonlocal': [  # ................................................................................

('', None, None, None, {}, ('Nonlocal',
r'''nonlocal a, b, c'''),
r'''MNonlocal(names=M(n=...))''', (None,
r'''nonlocal __FST_n  # new'''),
r'''nonlocal a, b, c  # new''', r'''
Nonlocal - ROOT 0,0..0,16
  .names[3]
   0] 'a'
   1] 'b'
   2] 'c'
'''),

('', None, None, None, {}, ('Nonlocal',
r'''nonlocal a, b, c, d, e'''),
r'''MNonlocal(names=[..., MQSTAR(i=...), ...])''', ('Nonlocal',
r'''nonlocal x, __FST_i, y'''),
r'''nonlocal x, b, c, d, y''', r'''
Nonlocal - ROOT 0,0..0,22
  .names[5]
   0] 'x'
   1] 'b'
   2] 'c'
   3] 'd'
   4] 'y'
'''),
],

'basic_Expr': [  # ................................................................................

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''MName''', (None,
r'''__FST_'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''MName''', (None,
r'''__FST_; __FST_'''),
r'''**NodeError('expecting expression (standard), got Module, could not coerce, multiple statements')**'''),

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''M(MName, src='call()')''', (None,
r'''__FST_src'''),
r'''call()''', r'''
Expr - ROOT 0,0..0,6
  .value Call - 0,0..0,6
    .func Name 'call' Load - 0,0..0,4
'''),

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''M(MName, src='call(); pass')''', (None,
r'''__FST_src'''),
r'''**NodeError('expecting expression (standard), got Module, could not coerce, multiple statements')**'''),

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''MExpr''', (None,
r'''__FST_'''),
r'''a''', r'''
Expr - ROOT 0,0..0,1
  .value Name 'a' Load - 0,0..0,1
'''),

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''MExpr''', (None,
r'''__FST_; __FST_'''), r'''
a
a
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
'''),

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''M(MExpr, src='call()')''', (None,
r'''__FST_src'''),
r'''call()''', r'''
Call - ROOT 0,0..0,6
  .func Name 'call' Load - 0,0..0,4
'''),

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''M(MExpr, fst=FST('call()', 'stmt'))''', (None,
r'''__FST_fst'''),
r'''call()''', r'''
Expr - ROOT 0,0..0,6
  .value Call - 0,0..0,6
    .func Name 'call' Load - 0,0..0,4
'''),

('', None, None, None, {}, ('Expr',
r'''a'''),
r'''M(MExpr, src='call(); pass')''', (None,
r'''__FST_src'''),
r'''call(); pass''', r'''
Module - ROOT 0,0..0,12
  .body[2]
   0] Expr - 0,0..0,6
     .value Call - 0,0..0,6
       .func Name 'call' Load - 0,0..0,4
   1] Pass - 0,8..0,12
'''),

('', None, None, None, {}, ('Module',
r'''a'''),
r'''MExpr''', (None,
r'''__FST_'''),
r'''a''', r'''
Module - ROOT 0,0..0,1
  .body[1]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
'''),

('', None, None, None, {}, ('Module',
r'''a'''),
r'''MExpr''', (None,
r'''__FST_; __FST_'''), r'''
a
a
''', r'''
Module - ROOT 0,0..1,1
  .body[2]
   0] Expr - 0,0..0,1
     .value Name 'a' Load - 0,0..0,1
   1] Expr - 1,0..1,1
     .value Name 'a' Load - 1,0..1,1
'''),

('', None, None, None, {}, ('Module',
r'''a'''),
r'''M(MExpr, src='call()')''', (None,
r'''__FST_src'''),
r'''call()''', r'''
Module - ROOT 0,0..0,6
  .body[1]
   0] Expr - 0,0..0,6
     .value Call - 0,0..0,6
       .func Name 'call' Load - 0,0..0,4
'''),

('', None, None, None, {}, ('Module',
r'''a'''),
r'''M(MExpr, src='call(); pass')''', (None,
r'''__FST_src'''),
r'''call(); pass''', r'''
Module - ROOT 0,0..0,12
  .body[2]
   0] Expr - 0,0..0,6
     .value Call - 0,0..0,6
       .func Name 'call' Load - 0,0..0,4
   1] Pass - 0,8..0,12
'''),
],

'basic_BoolOp': [  # ................................................................................

('', None, None, None, {}, ('BoolOp',
r'''a and b'''),
r'''MBoolOp''', (None,
r'''x and __FST_ and y'''),
r'''x and a and b and y''', r'''
BoolOp - ROOT 0,0..0,19
  .op And
  .values[4]
   0] Name 'x' Load - 0,0..0,1
   1] Name 'a' Load - 0,6..0,7
   2] Name 'b' Load - 0,12..0,13
   3] Name 'y' Load - 0,18..0,19
'''),

('', None, None, None, {}, ('BoolOp',
r'''a and b'''),
r'''MBoolOp(values=M(v=...))''', (None,
r'''x and __FST_v and y'''),
r'''x and a and b and y''', r'''
BoolOp - ROOT 0,0..0,19
  .op And
  .values[4]
   0] Name 'x' Load - 0,0..0,1
   1] Name 'a' Load - 0,6..0,7
   2] Name 'b' Load - 0,12..0,13
   3] Name 'y' Load - 0,18..0,19
'''),

('', None, None, None, {}, ('BoolOp',
r'''a and b'''),
r'''MBoolOp''', (None,
r'''x or __FST_ or y'''),
r'''x or a and b or y''', r'''
BoolOp - ROOT 0,0..0,17
  .op Or
  .values[3]
   0] Name 'x' Load - 0,0..0,1
   1] BoolOp - 0,5..0,12
     .op And
     .values[2]
      0] Name 'a' Load - 0,5..0,6
      1] Name 'b' Load - 0,11..0,12
   2] Name 'y' Load - 0,16..0,17
'''),

('', None, None, None, {}, ('BoolOp',
r'''a and b'''),
r'''MBoolOp(values=M(v=...))''', (None,
r'''x or __FST_v or y'''),
r'''x or a and b or y''', r'''
BoolOp - ROOT 0,0..0,17
  .op Or
  .values[3]
   0] Name 'x' Load - 0,0..0,1
   1] BoolOp - 0,5..0,12
     .op And
     .values[2]
      0] Name 'a' Load - 0,5..0,6
      1] Name 'b' Load - 0,11..0,12
   2] Name 'y' Load - 0,16..0,17
'''),

('', None, None, None, {}, ('BoolOp',
r'''a or b'''),
r'''MBoolOp''', (None,
r'''x and __FST_ and y'''),
r'''x and (a or b) and y''', r'''
BoolOp - ROOT 0,0..0,20
  .op And
  .values[3]
   0] Name 'x' Load - 0,0..0,1
   1] BoolOp - 0,7..0,13
     .op Or
     .values[2]
      0] Name 'a' Load - 0,7..0,8
      1] Name 'b' Load - 0,12..0,13
   2] Name 'y' Load - 0,19..0,20
'''),

('', None, None, None, {}, ('BoolOp',
r'''a or b'''),
r'''MBoolOp(values=M(v=...))''', (None,
r'''x and __FST_v and y'''),
r'''x and (a or b) and y''', r'''
BoolOp - ROOT 0,0..0,20
  .op And
  .values[3]
   0] Name 'x' Load - 0,0..0,1
   1] BoolOp - 0,7..0,13
     .op Or
     .values[2]
      0] Name 'a' Load - 0,7..0,8
      1] Name 'b' Load - 0,12..0,13
   2] Name 'y' Load - 0,19..0,20
'''),

('', None, None, None, {}, ('BoolOp',
r'''a or b or c or d or e'''),
r'''MBoolOp(values=[..., MQSTAR(i=...), ...])''', ('BoolOp',
r'''x or __FST_i or y'''),
r'''x or b or c or d or y''', r'''
BoolOp - ROOT 0,0..0,21
  .op Or
  .values[5]
   0] Name 'x' Load - 0,0..0,1
   1] Name 'b' Load - 0,5..0,6
   2] Name 'c' Load - 0,10..0,11
   3] Name 'd' Load - 0,15..0,16
   4] Name 'y' Load - 0,20..0,21
'''),
],

'basic_NamedExpr': [  # ................................................................................

('', None, None, None, {}, ('NamedExpr',
r'''a := b'''),
r'''MNamedExpr(target=M(t=...))''', (None,
r'''__FST_t := y'''),
r'''a := y''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'a' Store - 0,0..0,1
  .value Name 'y' Load - 0,5..0,6
'''),

('', None, None, None, {}, ('NamedExpr',
r'''a := b'''),
r'''MNamedExpr(target=M(t=...))''', (None,
r'''x := __FST_'''),
r'''x := (a := b)''', r'''
NamedExpr - ROOT 0,0..0,13
  .target Name 'x' Store - 0,0..0,1
  .value NamedExpr - 0,6..0,12
    .target Name 'a' Store - 0,6..0,7
    .value Name 'b' Load - 0,11..0,12
'''),

('', None, None, None, {}, ('NamedExpr',
r'''a := b'''),
r'''MNamedExpr(target=M(t=...))''', (None,
r'''x := __FST_t'''),
r'''x := a''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'x' Store - 0,0..0,1
  .value Name 'a' Load - 0,5..0,6
'''),

('', None, None, None, {}, ('NamedExpr',
r'''a := b'''),
r'''MNamedExpr(value=M(v=...))''', (None,
r'''x := __FST_v'''),
r'''x := b''', r'''
NamedExpr - ROOT 0,0..0,6
  .target Name 'x' Store - 0,0..0,1
  .value Name 'b' Load - 0,5..0,6
'''),
],

'basic_BinOp': [  # ................................................................................

('', None, None, None, {}, ('BinOp',
r'''a + b'''),
r'''MBinOp(left=M(l=...), right=M(r=...))''', (None,
r'''__FST_r + __FST_l'''),
r'''b + a''', r'''
BinOp - ROOT 0,0..0,5
  .left Name 'b' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right Name 'a' Load - 0,4..0,5
'''),

('', None, None, None, {}, ('BinOp',
r'''a + b'''),
r'''MBinOp(left=M(l=...), right=M(r=...))''', (None,
r'''__FST_r + __FST_'''),
r'''b + (a + b)''', r'''
BinOp - ROOT 0,0..0,11
  .left Name 'b' Load - 0,0..0,1
  .op Add - 0,2..0,3
  .right BinOp - 0,5..0,10
    .left Name 'a' Load - 0,5..0,6
    .op Add - 0,7..0,8
    .right Name 'b' Load - 0,9..0,10
'''),

('', None, None, None, {}, ('BinOp',
r'''a + b'''),
r'''MBinOp(left=M(l=...), right=M(r=...))''', (None,
r'''__FST_ + __FST_l'''),
r'''a + b + a''', r'''
BinOp - ROOT 0,0..0,9
  .left BinOp - 0,0..0,5
    .left Name 'a' Load - 0,0..0,1
    .op Add - 0,2..0,3
    .right Name 'b' Load - 0,4..0,5
  .op Add - 0,6..0,7
  .right Name 'a' Load - 0,8..0,9
'''),
],

'basic_UnaryOp': [  # ................................................................................

('', None, None, None, {}, ('UnaryOp',
r'''~a'''),
r'''MUnaryOp(operand=M(o=...))''', (None,
r'''-__FST_'''),
r'''-~a''', r'''
UnaryOp - ROOT 0,0..0,3
  .op USub - 0,0..0,1
  .operand UnaryOp - 0,1..0,3
    .op Invert - 0,1..0,2
    .operand Name 'a' Load - 0,2..0,3
'''),

('', None, None, None, {}, ('UnaryOp',
r'''~a'''),
r'''MUnaryOp(operand=M(o=...))''', (None,
r'''-__FST_o'''),
r'''-a''', r'''
UnaryOp - ROOT 0,0..0,2
  .op USub - 0,0..0,1
  .operand Name 'a' Load - 0,1..0,2
'''),
],

'basic_Lambda': [  # ................................................................................

('', None, None, None, {}, ('Lambda',
r'''lambda: None'''),
r'''MLambda(body=M(b=...))''', (None,
r'''lambda: not __FST_b'''),
r'''lambda: not None''', r'''
Lambda - ROOT 0,0..0,16
  .body UnaryOp - 0,8..0,16
    .op Not - 0,8..0,11
    .operand Constant None - 0,12..0,16
'''),

('', None, None, None, {}, ('Lambda',
r'''lambda a, /, b, *, c: None'''),
r'''MLambda(args=M(a=...))''', (None,
r'''lambda __FST_a: True'''),
r'''lambda a, /, b, *, c: True''', r'''
Lambda - ROOT 0,0..0,26
  .args arguments - 0,7..0,20
    .posonlyargs[1]
     0] arg - 0,7..0,8
       .arg 'a'
    .args[1]
     0] arg - 0,13..0,14
       .arg 'b'
    .kwonlyargs[1]
     0] arg - 0,19..0,20
       .arg 'c'
    .kw_defaults[1]
     0] None
  .body Constant True - 0,22..0,26
'''),

('', None, None, None, {}, ('Lambda',
r'''lambda a, /, b, *, c: None'''),
r'''MLambda(args=M(a=...))''', (None,
r'''lambda __FST_DEL: True'''),
r'''lambda: True''', r'''
Lambda - ROOT 0,0..0,12
  .body Constant True - 0,8..0,12
'''),

('', None, None, None, {}, ('Lambda',
r'''lambda a, b=1, /, c=2, *d, **e: None'''),
r'''MLambda(args=Marguments(_all=[..., MQSTAR(a=...), ...]))''', ('Lambda',
r'''lambda x, /, __FST_a: True'''),
r'''lambda x, /, b=1, c=2, *d: True''', r'''
Lambda - ROOT 0,0..0,31
  .args arguments - 0,7..0,25
    .posonlyargs[1]
     0] arg - 0,7..0,8
       .arg 'x'
    .args[2]
     0] arg - 0,13..0,14
       .arg 'b'
     1] arg - 0,18..0,19
       .arg 'c'
    .vararg arg - 0,24..0,25
      .arg 'd'
    .defaults[2]
     0] Constant 1 - 0,15..0,16
     1] Constant 2 - 0,20..0,21
  .body Constant True - 0,27..0,31
'''),

('', None, None, None, {'args_as': None}, ('Lambda',
r'''lambda a, b=1, /, c=2, *d, **e: None'''),
r'''MLambda(args=Marguments(_all=[..., MQSTAR(a=...), ...]))''', ('Lambda',
r'''lambda x, /, __FST_a: True'''),
r'''lambda x, b=1, /, c=2, *d: True''', r'''
Lambda - ROOT 0,0..0,31
  .args arguments - 0,7..0,25
    .posonlyargs[2]
     0] arg - 0,7..0,8
       .arg 'x'
     1] arg - 0,10..0,11
       .arg 'b'
    .args[1]
     0] arg - 0,18..0,19
       .arg 'c'
    .vararg arg - 0,24..0,25
      .arg 'd'
    .defaults[2]
     0] Constant 1 - 0,12..0,13
     1] Constant 2 - 0,20..0,21
  .body Constant True - 0,27..0,31
'''),
],

'basic_IfExp': [  # ................................................................................

('', None, None, None, {}, ('IfExp',
r'''a if b else c'''),
r'''MIfExp(body=M(b=...), test=M(t=...), orelse=M(o=...))''', (None,
r'''__FST_t if __FST_o else __FST_b'''),
r'''b if c else a''', r'''
IfExp - ROOT 0,0..0,13
  .test Name 'c' Load - 0,5..0,6
  .body Name 'b' Load - 0,0..0,1
  .orelse Name 'a' Load - 0,12..0,13
'''),

('', None, None, None, {}, ('IfExp',
r'''a if b else c'''),
r'''MIfExp(body=M(b=...), test=M(t=...), orelse=M(o=...))''', (None,
r'''__FST_ if __FST_ else __FST_'''),
r'''(a if b else c) if (a if b else c) else a if b else c''', r'''
IfExp - ROOT 0,0..0,53
  .test IfExp - 0,20..0,33
    .test Name 'b' Load - 0,25..0,26
    .body Name 'a' Load - 0,20..0,21
    .orelse Name 'c' Load - 0,32..0,33
  .body IfExp - 0,1..0,14
    .test Name 'b' Load - 0,6..0,7
    .body Name 'a' Load - 0,1..0,2
    .orelse Name 'c' Load - 0,13..0,14
  .orelse IfExp - 0,40..0,53
    .test Name 'b' Load - 0,45..0,46
    .body Name 'a' Load - 0,40..0,41
    .orelse Name 'c' Load - 0,52..0,53
'''),
],

'basic_Dict': [  # ................................................................................

('', None, None, None, {}, ('Dict',
r'''{a: b}'''),
r'''MDict(keys=[M(k=...)], values=[M(v=...)])''', (None,
r'''{__FST_v: __FST_k}'''),
r'''{b: a}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'b' Load - 0,1..0,2
  .values[1]
   0] Name 'a' Load - 0,4..0,5
'''),

('', None, None, None, {}, ('Dict',
r'''{a: b}'''),
r'''MDict(_all=[M(e=...)])''', (None,
r'''__FST_e'''),
r'''{a: b}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'a' Load - 0,1..0,2
  .values[1]
   0] Name 'b' Load - 0,4..0,5
'''),

('', None, None, None, {}, ('Dict',
r'''{a: b, c: d, e: f}'''),
r'''MDict(_all=[..., M(e=...), ...])''', (None,
r'''__FST_e'''),
r'''{c: d}''', r'''
Dict - ROOT 0,0..0,6
  .keys[1]
   0] Name 'c' Load - 0,1..0,2
  .values[1]
   0] Name 'd' Load - 0,4..0,5
'''),

('', None, None, None, {}, ('Dict',
r'''{a: b, c: d, e: f}'''),
r'''MDict(_all=M(e=...))''', (None,
r'''__FST_e'''),
r'''{a: b, c: d, e: f}''', r'''
Dict - ROOT 0,0..0,18
  .keys[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'c' Load - 0,7..0,8
   2] Name 'e' Load - 0,13..0,14
  .values[3]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'd' Load - 0,10..0,11
   2] Name 'f' Load - 0,16..0,17
'''),

('', None, None, None, {}, ('Dict',
r'''{a: b}'''),
r'''MDict(keys=[M(k=...)], values=[M(v=...)])''', (None,
r'''{__FST_DEL: __FST_v, __FST_DEL: __FST_k}'''),
r'''{**b, **a}''', r'''
Dict - ROOT 0,0..0,10
  .keys[2]
   0] None
   1] None
  .values[2]
   0] Name 'b' Load - 0,3..0,4
   1] Name 'a' Load - 0,8..0,9
'''),

('', None, None, None, {}, ('Dict',
r'''{1: a, 2: b, 3: c}'''),
r'''MDict(_all=[..., M(d=...), ...])''', (None,
r'''{'...': __FST_d, '...': __FST_d}'''),
r'''{2: b, 2: b}''', r'''
Dict - ROOT 0,0..0,12
  .keys[2]
   0] Constant 2 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .values[2]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'b' Load - 0,10..0,11
'''),

('', None, None, None, {}, ('Dict',
r'''{1: a, **b, 3: c}'''),
r'''MDict(_all=[..., M(d=...), ...])''', (None,
r'''{'...': __FST_d, '...': __FST_d}'''),
r'''{**b, **b}''', r'''
Dict - ROOT 0,0..0,10
  .keys[2]
   0] None
   1] None
  .values[2]
   0] Name 'b' Load - 0,3..0,4
   1] Name 'b' Load - 0,8..0,9
'''),

('', None, None, None, {}, ('Dict',
r'''{1: a, 2: b, **c, 4: d, 5: e}'''),
r'''MDict(_all=[..., MQSTAR(d=...), ...])''', ('Dict',
r'''{-1: x, '...': __FST_d, -2: y}'''),
r'''{-1: x, 2: b, **c, 4: d, -2: y}''', r'''
Dict - ROOT 0,0..0,31
  .keys[5]
   0] UnaryOp - 0,1..0,3
     .op USub - 0,1..0,2
     .operand Constant 1 - 0,2..0,3
   1] Constant 2 - 0,8..0,9
   2] None
   3] Constant 4 - 0,19..0,20
   4] UnaryOp - 0,25..0,27
     .op USub - 0,25..0,26
     .operand Constant 2 - 0,26..0,27
  .values[5]
   0] Name 'x' Load - 0,5..0,6
   1] Name 'b' Load - 0,11..0,12
   2] Name 'c' Load - 0,16..0,17
   3] Name 'd' Load - 0,22..0,23
   4] Name 'y' Load - 0,29..0,30
'''),
],

'basic_Set': [  # ................................................................................

('', None, None, None, {}, ('Set',
r'''{a, b, c}'''),
r'''MSet''', (None,
r'''[__FST_, __FST_]'''),
r'''[{a, b, c}, {a, b, c}]''', r'''
List - ROOT 0,0..0,22
  .elts[2]
   0] Set - 0,1..0,10
     .elts[3]
      0] Name 'a' Load - 0,2..0,3
      1] Name 'b' Load - 0,5..0,6
      2] Name 'c' Load - 0,8..0,9
   1] Set - 0,12..0,21
     .elts[3]
      0] Name 'a' Load - 0,13..0,14
      1] Name 'b' Load - 0,16..0,17
      2] Name 'c' Load - 0,19..0,20
  .ctx Load
'''),

('', None, None, None, {}, ('Set',
r'''{a, b, c}'''),
r'''MSet(elts=M(e=...))''', (None,
r'''{__FST_e}'''),
r'''{a, b, c}''', r'''
Set - ROOT 0,0..0,9
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
'''),

('', None, None, None, {}, ('Set',
r'''{a, b, c}'''),
r'''MSet(elts=[..., M(e=...), ...])''', (None,
r'''{__FST_e}'''),
r'''{b}''', r'''
Set - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
'''),

('', None, None, None, {}, ('Set',
r'''{a, b, c}'''),
r'''MSet(elts=M(e=...))''', (None,
r'''{x, __FST_e, y}'''),
r'''{x, a, b, c, y}''', r'''
Set - ROOT 0,0..0,15
  .elts[5]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'a' Load - 0,4..0,5
   2] Name 'b' Load - 0,7..0,8
   3] Name 'c' Load - 0,10..0,11
   4] Name 'y' Load - 0,13..0,14
'''),

('', None, None, None, {}, ('Set',
r'''{a, b, c}'''),
r'''MSet(elts=[..., M(e=...), ...])''', (None,
r'''{x, __FST_e, y}'''),
r'''{x, b, y}''', r'''
Set - ROOT 0,0..0,9
  .elts[3]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'y' Load - 0,7..0,8
'''),

('', None, None, None, {}, ('Set',
r'''{a, b, c, d, e}'''),
r'''MSet(elts=[..., MQSTAR(a=...), ...])''', ('Set',
r'''{x, __FST_a, y}'''),
r'''{x, b, c, d, y}''', r'''
Set - ROOT 0,0..0,15
  .elts[5]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
   3] Name 'd' Load - 0,10..0,11
   4] Name 'y' Load - 0,13..0,14
'''),

('', None, None, None, {}, ('Set',
r'''{a, b, c, d, e}'''),
r'''MSet(elts=[..., MQSTAR(a=...), ...])''', ('Set',
r'''{x, __FSO_a, y}'''),
r'''{x, {b, c, d}, y}''', r'''
Set - ROOT 0,0..0,17
  .elts[3]
   0] Name 'x' Load - 0,1..0,2
   1] Set - 0,4..0,13
     .elts[3]
      0] Name 'b' Load - 0,5..0,6
      1] Name 'c' Load - 0,8..0,9
      2] Name 'd' Load - 0,11..0,12
   2] Name 'y' Load - 0,15..0,16
'''),
],

'basic_ListComp': [  # ................................................................................

('', None, None, None, {}, ('ListComp',
r'''[a for a in b]'''),
r'''MListComp(elt=M(e=...))''', (None,
r'''{__FST_e for __FST_e in _}'''),
r'''{a for a in _}''', r'''
SetComp - ROOT 0,0..0,14
  .elt Name 'a' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('ListComp',
r'''[*a for a in b]'''),
r'''MListComp(elt=M(e=...))''', (None,
r'''{__FST_e for __FST_e in _}'''),
r'''{*a for *a in _}''', r'''
SetComp - ROOT 0,0..0,16
  .elt Starred - 0,1..0,3
    .value Name 'a' Load - 0,2..0,3
    .ctx Load
  .generators[1]
   0] comprehension - 0,4..0,15
     .target Starred - 0,8..0,10
       .value Name 'a' Store - 0,9..0,10
       .ctx Store
     .iter Name '_' Load - 0,14..0,15
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('ListComp',
r'''[*a for a in b]'''),
r'''MListComp(elt=MStarred(value=M(e=...)))''', (None,
r'''{*__FST_e for __FST_e in _}'''),
r'''{*a for a in _}''', r'''
SetComp - ROOT 0,0..0,15
  .elt Starred - 0,1..0,3
    .value Name 'a' Load - 0,2..0,3
    .ctx Load
  .generators[1]
   0] comprehension - 0,4..0,14
     .target Name 'a' Store - 0,8..0,9
     .iter Name '_' Load - 0,13..0,14
     .is_async 0
'''),
],

'basic_SetComp': [  # ................................................................................

('', None, None, None, {}, ('SetComp',
r'''{a for a in b}'''),
r'''MSetComp(elt=M(e=...))''', (None,
r'''[__FST_e for __FST_e in _]'''),
r'''[a for a in _]''', r'''
ListComp - ROOT 0,0..0,14
  .elt Name 'a' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('SetComp',
r'''{*a for a in b}'''),
r'''MSetComp(elt=M(e=...))''', (None,
r'''[__FST_e for __FST_e in _]'''),
r'''[*a for *a in _]''', r'''
ListComp - ROOT 0,0..0,16
  .elt Starred - 0,1..0,3
    .value Name 'a' Load - 0,2..0,3
    .ctx Load
  .generators[1]
   0] comprehension - 0,4..0,15
     .target Starred - 0,8..0,10
       .value Name 'a' Store - 0,9..0,10
       .ctx Store
     .iter Name '_' Load - 0,14..0,15
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('SetComp',
r'''{*a for a in b}'''),
r'''MSetComp(elt=MStarred(value=M(e=...)))''', (None,
r'''[*__FST_e for __FST_e in _]'''),
r'''[*a for a in _]''', r'''
ListComp - ROOT 0,0..0,15
  .elt Starred - 0,1..0,3
    .value Name 'a' Load - 0,2..0,3
    .ctx Load
  .generators[1]
   0] comprehension - 0,4..0,14
     .target Name 'a' Store - 0,8..0,9
     .iter Name '_' Load - 0,13..0,14
     .is_async 0
'''),
],

'basic_DictComp': [  # ................................................................................

('', None, None, None, {}, ('DictComp',
r'''{a: b for a, b in c}'''),
r'''MDictComp(key=M(k=...), value=M(v=...))''', (None,
r'''{__FST_v: __FST_k for __FST_v, __FST_k in _}'''),
r'''{b: a for b, a in _}''', r'''
DictComp - ROOT 0,0..0,20
  .key Name 'b' Load - 0,1..0,2
  .value Name 'a' Load - 0,4..0,5
  .generators[1]
   0] comprehension - 0,6..0,19
     .target Tuple - 0,10..0,14
       .elts[2]
        0] Name 'b' Store - 0,10..0,11
        1] Name 'a' Store - 0,13..0,14
       .ctx Store
     .iter Name '_' Load - 0,18..0,19
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('DictComp',
r'''{**a for a in c}'''),
r'''MDictComp(key=M(k=...))''', (None,
r'''{__FST_k for __FST_k in _}'''),
r'''{a for a in _}''', r'''
SetComp - ROOT 0,0..0,14
  .elt Name 'a' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('DictComp',
r'''{**a for a in c}'''),
r'''MDictComp(key=M(k=...))''', (None,
r'''{**__FST_k for __FST_k in _}'''),
r'''{**a for a in _}''', r'''
DictComp - ROOT 0,0..0,16
  .key Name 'a' Load - 0,3..0,4
  .generators[1]
   0] comprehension - 0,5..0,15
     .target Name 'a' Store - 0,9..0,10
     .iter Name '_' Load - 0,14..0,15
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('DictComp',
r'''{a: b for a, b in c}'''),
r'''MDictComp(key=M(k=...), value=M(v=...))''', (None,
r'''{__FST_k: __FST_v for __FST_k, __FST_v in _}'''),
r'''{a: b for a, b in _}''', r'''
DictComp - ROOT 0,0..0,20
  .key Name 'a' Load - 0,1..0,2
  .value Name 'b' Load - 0,4..0,5
  .generators[1]
   0] comprehension - 0,6..0,19
     .target Tuple - 0,10..0,14
       .elts[2]
        0] Name 'a' Store - 0,10..0,11
        1] Name 'b' Store - 0,13..0,14
       .ctx Store
     .iter Name '_' Load - 0,18..0,19
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('DictComp',
r'''{**a for a in c}'''),
r'''MDictComp(key=M(k=...), value=M(v=...))''', (None,
r'''{__FST_k: __FST_v for __FST_k, __FST_v in _}'''),
r'''{**a for a, in _}''', r'''
DictComp - ROOT 0,0..0,17
  .key Name 'a' Load - 0,3..0,4
  .generators[1]
   0] comprehension - 0,5..0,16
     .target Tuple - 0,9..0,11
       .elts[1]
        0] Name 'a' Store - 0,9..0,10
       .ctx Store
     .iter Name '_' Load - 0,15..0,16
     .is_async 0
'''),
],

'basic_GeneratorExp': [  # ................................................................................

('', None, None, None, {}, ('GeneratorExp',
r'''(a for a in b)'''),
r'''MGeneratorExp(elt=M(e=...))''', (None,
r'''(__FST_e for __FST_e in _)'''),
r'''(a for a in _)''', r'''
GeneratorExp - ROOT 0,0..0,14
  .elt Name 'a' Load - 0,1..0,2
  .generators[1]
   0] comprehension - 0,3..0,13
     .target Name 'a' Store - 0,7..0,8
     .iter Name '_' Load - 0,12..0,13
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('GeneratorExp',
r'''(*a for a in b)'''),
r'''MGeneratorExp(elt=M(e=...))''', (None,
r'''(__FST_e for __FST_e in _)'''),
r'''(*a for *a in _)''', r'''
GeneratorExp - ROOT 0,0..0,16
  .elt Starred - 0,1..0,3
    .value Name 'a' Load - 0,2..0,3
    .ctx Load
  .generators[1]
   0] comprehension - 0,4..0,15
     .target Starred - 0,8..0,10
       .value Name 'a' Store - 0,9..0,10
       .ctx Store
     .iter Name '_' Load - 0,14..0,15
     .is_async 0
'''),

('', None, None, None, {'_ver': 15}, ('GeneratorExp',
r'''(*a for a in b)'''),
r'''MGeneratorExp(elt=MStarred(value=M(e=...)))''', (None,
r'''(*__FST_e for __FST_e in _)'''),
r'''(*a for a in _)''', r'''
GeneratorExp - ROOT 0,0..0,15
  .elt Starred - 0,1..0,3
    .value Name 'a' Load - 0,2..0,3
    .ctx Load
  .generators[1]
   0] comprehension - 0,4..0,14
     .target Name 'a' Store - 0,8..0,9
     .iter Name '_' Load - 0,13..0,14
     .is_async 0
'''),
],

'basic_Await': [  # ................................................................................

('', None, None, None, {}, (None,
r'''await a'''),
r'''MAwait(value=M(v=...))''',
r'''await __FST_v  # new''',
r'''await a  # new''', r'''
Await - ROOT 0,0..0,7
  .value Name 'a' Load - 0,6..0,7
'''),
],

'basic_Yield': [  # ................................................................................

('', None, None, None, {}, (None,
r'''yield a'''),
r'''MYield(value=M(v=...))''',
r'''yield __FST_v  # new''',
r'''yield a  # new''', r'''
Yield - ROOT 0,0..0,7
  .value Name 'a' Load - 0,6..0,7
'''),
],

'basic_YieldFrom': [  # ................................................................................

('', None, None, None, {}, (None,
r'''yield from a'''),
r'''MYieldFrom(value=M(v=...))''',
r'''yield from __FST_v  # new''',
r'''yield from a  # new''', r'''
YieldFrom - ROOT 0,0..0,12
  .value Name 'a' Load - 0,11..0,12
'''),
],

'basic_Compare': [  # ................................................................................

('', None, None, None, {}, ('Compare',
r'''a < b > c'''),
r'''MCompare''', (None,
r'''__FST_'''),
r'''a < b > c''', r'''
Compare - ROOT 0,0..0,9
  .left Name 'a' Load - 0,0..0,1
  .ops[2]
   0] Lt - 0,2..0,3
   1] Gt - 0,6..0,7
  .comparators[2]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'c' Load - 0,8..0,9
'''),

('', None, None, None, {}, ('Compare',
r'''a < b > c'''),
r'''M(t=MCompare(_all=...))''', (None,
r'''__FST_t'''),
r'''a < b > c''', r'''
Compare - ROOT 0,0..0,9
  .left Name 'a' Load - 0,0..0,1
  .ops[2]
   0] Lt - 0,2..0,3
   1] Gt - 0,6..0,7
  .comparators[2]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'c' Load - 0,8..0,9
'''),

('', None, None, None, {}, ('Compare',
r'''a < b > c'''),
r'''MCompare(_all=M(t=...))''', (None,
r'''__FST_t'''),
r'''a < b > c''', r'''
Compare - ROOT 0,0..0,9
  .left Name 'a' Load - 0,0..0,1
  .ops[2]
   0] Lt - 0,2..0,3
   1] Gt - 0,6..0,7
  .comparators[2]
   0] Name 'b' Load - 0,4..0,5
   1] Name 'c' Load - 0,8..0,9
'''),

('', None, None, None, {}, ('Compare',
r'''a < b > c'''),
r'''MCompare(_all=[..., M(t=...), ...])''', (None,
r'''__FST_t'''),
r'''b''',
r'''Name 'b' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, ('Compare',
r'''a < b > c'''),
r'''MCompare''', (None,
r'''x == __FST_ != y'''),
r'''x == (a < b > c) != y''', r'''
Compare - ROOT 0,0..0,21
  .left Name 'x' Load - 0,0..0,1
  .ops[2]
   0] Eq - 0,2..0,4
   1] NotEq - 0,17..0,19
  .comparators[2]
   0] Compare - 0,6..0,15
     .left Name 'a' Load - 0,6..0,7
     .ops[2]
      0] Lt - 0,8..0,9
      1] Gt - 0,12..0,13
     .comparators[2]
      0] Name 'b' Load - 0,10..0,11
      1] Name 'c' Load - 0,14..0,15
   1] Name 'y' Load - 0,20..0,21
'''),

('', None, None, None, {}, ('Compare',
r'''a < b > c'''),
r'''MCompare(_all=M(t=...))''', (None,
r'''x == __FST_t != y'''),
r'''x == a < b > c != y''', r'''
Compare - ROOT 0,0..0,19
  .left Name 'x' Load - 0,0..0,1
  .ops[4]
   0] Eq - 0,2..0,4
   1] Lt - 0,7..0,8
   2] Gt - 0,11..0,12
   3] NotEq - 0,15..0,17
  .comparators[4]
   0] Name 'a' Load - 0,5..0,6
   1] Name 'b' Load - 0,9..0,10
   2] Name 'c' Load - 0,13..0,14
   3] Name 'y' Load - 0,18..0,19
'''),

('', None, None, None, {}, ('Compare',
r'''a < b > c'''),
r'''MCompare(_all=M(t=...))''', (None,
r'''x == __FSO_t != y'''),
r'''x == (a < b > c) != y''', r'''
Compare - ROOT 0,0..0,21
  .left Name 'x' Load - 0,0..0,1
  .ops[2]
   0] Eq - 0,2..0,4
   1] NotEq - 0,17..0,19
  .comparators[2]
   0] Compare - 0,6..0,15
     .left Name 'a' Load - 0,6..0,7
     .ops[2]
      0] Lt - 0,8..0,9
      1] Gt - 0,12..0,13
     .comparators[2]
      0] Name 'b' Load - 0,10..0,11
      1] Name 'c' Load - 0,14..0,15
   1] Name 'y' Load - 0,20..0,21
'''),

('', None, None, None, {}, ('Compare',
r'''a < b > c'''),
r'''MCompare(_all=[..., M(t=...), ...])''', (None,
r'''x == __FST_t != y'''),
r'''x == b != y''', r'''
Compare - ROOT 0,0..0,11
  .left Name 'x' Load - 0,0..0,1
  .ops[2]
   0] Eq - 0,2..0,4
   1] NotEq - 0,7..0,9
  .comparators[2]
   0] Name 'b' Load - 0,5..0,6
   1] Name 'y' Load - 0,10..0,11
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c]'''),
r'''MList(elts=M(e=...))''', (None,
r'''x < __FST_ > y'''),
r'''x < [a, b, c] > y''', r'''
Compare - ROOT 0,0..0,17
  .left Name 'x' Load - 0,0..0,1
  .ops[2]
   0] Lt - 0,2..0,3
   1] Gt - 0,14..0,15
  .comparators[2]
   0] List - 0,4..0,13
     .elts[3]
      0] Name 'a' Load - 0,5..0,6
      1] Name 'b' Load - 0,8..0,9
      2] Name 'c' Load - 0,11..0,12
     .ctx Load
   1] Name 'y' Load - 0,16..0,17
'''),

('', None, None, None, {}, ('Compare',
r'''a < b <= c >= d > e'''),
r'''MCompare(_all=[..., MQSTAR(a=...), ...])''', ('Compare',
r'''__FST_a != y'''),
r'''b <= c >= d != y''', r'''
Compare - ROOT 0,0..0,16
  .left Name 'b' Load - 0,0..0,1
  .ops[3]
   0] LtE - 0,2..0,4
   1] GtE - 0,7..0,9
   2] NotEq - 0,12..0,14
  .comparators[3]
   0] Name 'c' Load - 0,5..0,6
   1] Name 'd' Load - 0,10..0,11
   2] Name 'y' Load - 0,15..0,16
'''),
],

'basic_Call': [  # ................................................................................

('', None, None, None, {}, ('Call',
r'''call(a, *b, c=d, **e)'''),
r'''MCall(_args=M(t=...))''', (None,
r'''__FST_t'''),
r'''a, *b, c=d, **e''', r'''
_arglikes - ROOT 0,0..0,15
  .arglikes[4]
   0] Name 'a' Load - 0,0..0,1
   1] Starred - 0,3..0,5
     .value Name 'b' Load - 0,4..0,5
     .ctx Load
   2] keyword - 0,7..0,10
     .arg 'c'
     .value Name 'd' Load - 0,9..0,10
   3] keyword - 0,12..0,15
     .value Name 'e' Load - 0,14..0,15
'''),

('', None, None, None, {}, ('Call',
r'''call(a, *b, c=d, **e)'''),
r'''MCall(_args=M(t=...))''', (None,
r'''call2(__FST_DEL)'''),
r'''call2()''', r'''
Call - ROOT 0,0..0,7
  .func Name 'call2' Load - 0,0..0,5
'''),

('', None, None, None, {}, ('Call',
r'''call(a, *b, c=d, **e)'''),
r'''MCall(_args=M(t=...))''', (None,
r'''call2(__FST_t)'''),
r'''call2(a, *b, c=d, **e)''', r'''
Call - ROOT 0,0..0,22
  .func Name 'call2' Load - 0,0..0,5
  .args[2]
   0] Name 'a' Load - 0,6..0,7
   1] Starred - 0,9..0,11
     .value Name 'b' Load - 0,10..0,11
     .ctx Load
  .keywords[2]
   0] keyword - 0,13..0,16
     .arg 'c'
     .value Name 'd' Load - 0,15..0,16
   1] keyword - 0,18..0,21
     .value Name 'e' Load - 0,20..0,21
'''),

('', None, None, None, {}, ('Call',
r'''call(a, *b, c=d, **e)'''),
r'''MCall(_args=M(t=...))''', (None,
r'''call2(x, __FST_t, **y)'''),
r'''call2(x, a, *b, c=d, **e, **y)''', r'''
Call - ROOT 0,0..0,30
  .func Name 'call2' Load - 0,0..0,5
  .args[3]
   0] Name 'x' Load - 0,6..0,7
   1] Name 'a' Load - 0,9..0,10
   2] Starred - 0,12..0,14
     .value Name 'b' Load - 0,13..0,14
     .ctx Load
  .keywords[3]
   0] keyword - 0,16..0,19
     .arg 'c'
     .value Name 'd' Load - 0,18..0,19
   1] keyword - 0,21..0,24
     .value Name 'e' Load - 0,23..0,24
   2] keyword - 0,26..0,29
     .value Name 'y' Load - 0,28..0,29
'''),

('', None, None, None, {}, ('Call',
r'''call(a, *b, c=d, **e)'''),
r'''MCall(args=M(t=...))''', (None,
r'''call2(x, __FST_t, **y)'''),
r'''call2(x, a, *b, **y)''', r'''
Call - ROOT 0,0..0,20
  .func Name 'call2' Load - 0,0..0,5
  .args[3]
   0] Name 'x' Load - 0,6..0,7
   1] Name 'a' Load - 0,9..0,10
   2] Starred - 0,12..0,14
     .value Name 'b' Load - 0,13..0,14
     .ctx Load
  .keywords[1]
   0] keyword - 0,16..0,19
     .value Name 'y' Load - 0,18..0,19
'''),

('', None, None, None, {}, ('Call',
r'''call(a, *b, c=d, **e)'''),
r'''MCall(keywords=M(t=...))''', (None,
r'''call2(x, __FST_t, **y)'''),
r'''call2(x, c=d, **e, **y)''', r'''
Call - ROOT 0,0..0,23
  .func Name 'call2' Load - 0,0..0,5
  .args[1]
   0] Name 'x' Load - 0,6..0,7
  .keywords[3]
   0] keyword - 0,9..0,12
     .arg 'c'
     .value Name 'd' Load - 0,11..0,12
   1] keyword - 0,14..0,17
     .value Name 'e' Load - 0,16..0,17
   2] keyword - 0,19..0,22
     .value Name 'y' Load - 0,21..0,22
'''),

('', None, None, None, {}, ('Call',
r'''call(a, *b, c=d, **e)'''),
r'''MCall(_args=[..., ..., M(t=...), ...])''', (None,
r'''call2(x, __FST_t, **y)'''),
r'''call2(x, c=d, **y)''', r'''
Call - ROOT 0,0..0,18
  .func Name 'call2' Load - 0,0..0,5
  .args[1]
   0] Name 'x' Load - 0,6..0,7
  .keywords[2]
   0] keyword - 0,9..0,12
     .arg 'c'
     .value Name 'd' Load - 0,11..0,12
   1] keyword - 0,14..0,17
     .value Name 'y' Load - 0,16..0,17
'''),

('', None, None, None, {}, ('Call',
r'''call(a, *b, c=d, **e)'''),
r'''MCall(_args=[MQN(t=..., n=2), ..., ...])''', (None,
r'''call2(x, __FSO_t, **y)'''),
r'''call2(x, (a, *b), **y)''', r'''
Call - ROOT 0,0..0,22
  .func Name 'call2' Load - 0,0..0,5
  .args[2]
   0] Name 'x' Load - 0,6..0,7
   1] Tuple - 0,9..0,16
     .elts[2]
      0] Name 'a' Load - 0,10..0,11
      1] Starred - 0,13..0,15
        .value Name 'b' Load - 0,14..0,15
        .ctx Load
     .ctx Load
  .keywords[1]
   0] keyword - 0,18..0,21
     .value Name 'y' Load - 0,20..0,21
'''),

('', None, None, None, {}, ('Call',
r'''call(a, c=c, *b, **d, **e)'''),
r'''MCall(_args=[..., MQSTAR(a=...), ...])''', ('Call',
r'''kall(x, __FST_a, **y)'''),
r'''kall(x, c=c, *b, **d, **y)''', r'''
Call - ROOT 0,0..0,26
  .func Name 'kall' Load - 0,0..0,4
  .args[2]
   0] Name 'x' Load - 0,5..0,6
   1] Starred - 0,13..0,15
     .value Name 'b' Load - 0,14..0,15
     .ctx Load
  .keywords[3]
   0] keyword - 0,8..0,11
     .arg 'c'
     .value Name 'c' Load - 0,10..0,11
   1] keyword - 0,17..0,20
     .value Name 'd' Load - 0,19..0,20
   2] keyword - 0,22..0,25
     .value Name 'y' Load - 0,24..0,25
'''),
],

'basic_FormattedValue': [  # ................................................................................

('', None, None, None, {'_ver': 12}, ('JoinedStr',
r'''f"{a}"'''),
r'''MJoinedStr(values=[MFormattedValue(value=M(v=...))])''', (None,
r'''f"{__FST_v}"'''),
r'''f"{a}"''', r'''
JoinedStr - ROOT 0,0..0,6
  .values[1]
   0] FormattedValue - 0,2..0,5
     .value Name 'a' Load - 0,3..0,4
     .conversion -1
'''),
],

'basic_Interpolation': [  # ................................................................................

('', None, None, None, {'_ver': 14}, ('TemplateStr',
r'''t"{a}"'''),
r'''MTemplateStr(values=[MInterpolation(value=M(v=...))])''', (None,
r'''t"{__FST_v}"'''),
r'''t"{a}"''', r'''
TemplateStr - ROOT 0,0..0,6
  .values[1]
   0] Interpolation - 0,2..0,5
     .value Name 'a' Load - 0,3..0,4
     .str 'a'
     .conversion -1
'''),
],

'basic_Constant': [  # ................................................................................

('', None, None, None, {}, ('Constant',
r'''"a"'''),
r'''MConstant(value=M(v=...))''', (None,
r'''__FST_v'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, ('Constant',
r'''"a"'''),
r'''MConstant(value=M(v=...))''', (None,
r'''global __FST_v'''),
r'''global a''', r'''
Global - ROOT 0,0..0,8
  .names[1]
   0] 'a'
'''),
],

'basic_Attribute': [  # ................................................................................

('', None, None, None, {}, ('Attribute',
r'''a.b'''),
r'''MAttribute(value=M(v=...))''', (None,
r'''__FST_v'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, ('Attribute',
r'''a.b'''),
r'''MAttribute(value=M(v=...))''', (None,
r'''__FST_v.x'''),
r'''a.x''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'x'
  .ctx Load
'''),

('', None, None, None, {}, ('Attribute',
r'''a.b'''),
r'''MAttribute(value=M(v=...))''', (None,
r'''__FST_v.__FST_v'''),
r'''a.a''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'a' Load - 0,0..0,1
  .attr 'a'
  .ctx Load
'''),

('', None, None, None, {}, ('Attribute',
r'''a.b'''),
r'''MAttribute(value=M(v=...), attr=M(a=...))''', (None,
r'''__FST_a.__FST_v'''),
r'''b.a''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'b' Load - 0,0..0,1
  .attr 'a'
  .ctx Load
'''),

('', None, None, None, {}, ('Attribute',
r'''a.b'''),
r'''MAttribute(attr=M(a=...))''', (None,
r'''__FST_a'''),
r'''b''',
r'''Name 'b' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, ('Attribute',
r'''a.b'''),
r'''MAttribute(attr=M(a=...))''', (None,
r'''__FST_a.__FST_a'''),
r'''b.b''', r'''
Attribute - ROOT 0,0..0,3
  .value Name 'b' Load - 0,0..0,1
  .attr 'b'
  .ctx Load
'''),
],

'basic_Subscript': [  # ................................................................................

('', None, None, None, {}, ('Subscript',
r'''a[b]'''),
r'''MSubscript(value=M(v=...))''', (None,
r'''__FST_v'''),
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, ('Subscript',
r'''a[b]'''),
r'''MSubscript(value=M(v=...))''', (None,
r'''__FST_v[x]'''),
r'''a[x]''', r'''
Subscript - ROOT 0,0..0,4
  .value Name 'a' Load - 0,0..0,1
  .slice Name 'x' Load - 0,2..0,3
  .ctx Load
'''),

('', None, None, None, {}, ('Subscript',
r'''a[b]'''),
r'''MSubscript(value=M(v=...))''', (None,
r'''__FST_v[__FST_v]'''),
r'''a[a]''', r'''
Subscript - ROOT 0,0..0,4
  .value Name 'a' Load - 0,0..0,1
  .slice Name 'a' Load - 0,2..0,3
  .ctx Load
'''),

('', None, None, None, {}, ('Subscript',
r'''a[b]'''),
r'''MSubscript(value=M(v=...), slice=M(s=...))''', (None,
r'''__FST_s[__FST_v]'''),
r'''b[a]''', r'''
Subscript - ROOT 0,0..0,4
  .value Name 'b' Load - 0,0..0,1
  .slice Name 'a' Load - 0,2..0,3
  .ctx Load
'''),

('', None, None, None, {}, ('Subscript',
r'''a[b]'''),
r'''MSubscript(slice=M(s=...))''', (None,
r'''__FST_s'''),
r'''b''',
r'''Name 'b' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, ('Subscript',
r'''a[b]'''),
r'''MSubscript(slice=M(s=...))''', (None,
r'''__FST_s[__FST_s]'''),
r'''b[b]''', r'''
Subscript - ROOT 0,0..0,4
  .value Name 'b' Load - 0,0..0,1
  .slice Name 'b' Load - 0,2..0,3
  .ctx Load
'''),
],

'basic_Starred': [  # ................................................................................

('', None, None, None, {}, (None,
r'''*a'''),
r'''MStarred(value=M(v=...))''',
r'''*__FST_v  # new''',
r'''*a  # new''', r'''
Starred - ROOT 0,0..0,2
  .value Name 'a' Load - 0,1..0,2
  .ctx Load
'''),
],

'basic_Name': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a'''),
r'''MName''',
r'''__FST_  # new''',
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, (None,
r'''a'''),
r'''MName(id=M(i=...))''',
r'''__FST_i  # new''',
r'''a''',
r'''Name 'a' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, (None,
r'''a'''),
r'''MName(id=M(i=...))''',
r'''[__FST_i, __FST_i]''',
r'''[a, a]''', r'''
List - ROOT 0,0..0,6
  .elts[2]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'a' Load - 0,4..0,5
  .ctx Load
'''),

('', None, None, None, {}, (None,
r'''a'''),
r'''MName(id=M(i=...))''',
r'''global __FST_i, __FST_i''',
r'''global a, a''', r'''
Global - ROOT 0,0..0,11
  .names[2]
   0] 'a'
   1] 'a'
'''),
],

'basic_List': [  # ................................................................................

('', None, None, None, {}, ('List',
r'''[a, b, c]'''),
r'''MList''', (None,
r'''[__FST_, __FST_]'''),
r'''[[a, b, c], [a, b, c]]''', r'''
List - ROOT 0,0..0,22
  .elts[2]
   0] List - 0,1..0,10
     .elts[3]
      0] Name 'a' Load - 0,2..0,3
      1] Name 'b' Load - 0,5..0,6
      2] Name 'c' Load - 0,8..0,9
     .ctx Load
   1] List - 0,12..0,21
     .elts[3]
      0] Name 'a' Load - 0,13..0,14
      1] Name 'b' Load - 0,16..0,17
      2] Name 'c' Load - 0,19..0,20
     .ctx Load
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c]'''),
r'''MList(elts=M(e=...))''', (None,
r'''[__FST_e]'''),
r'''[a, b, c]''', r'''
List - ROOT 0,0..0,9
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c]'''),
r'''MList(elts=[..., M(e=...), ...])''', (None,
r'''[__FST_e]'''),
r'''[b]''', r'''
List - ROOT 0,0..0,3
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c]'''),
r'''MList(elts=M(e=...))''', (None,
r'''[x, __FST_e, y]'''),
r'''[x, a, b, c, y]''', r'''
List - ROOT 0,0..0,15
  .elts[5]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'a' Load - 0,4..0,5
   2] Name 'b' Load - 0,7..0,8
   3] Name 'c' Load - 0,10..0,11
   4] Name 'y' Load - 0,13..0,14
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c]'''),
r'''MList(elts=[..., M(e=...), ...])''', (None,
r'''[x, __FST_e, y]'''),
r'''[x, b, y]''', r'''
List - ROOT 0,0..0,9
  .elts[3]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'y' Load - 0,7..0,8
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c, d, e]'''),
r'''MList(elts=[..., MQSTAR(a=...), ...])''', ('List',
r'''[x, __FST_a, y]'''),
r'''[x, b, c, d, y]''', r'''
List - ROOT 0,0..0,15
  .elts[5]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
   3] Name 'd' Load - 0,10..0,11
   4] Name 'y' Load - 0,13..0,14
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c, d, e]'''),
r'''MList(elts=[..., MQSTAR(a=...), ...])''', ('List',
r'''[x, __FSO_a, y]'''),
r'''[x, [b, c, d], y]''', r'''
List - ROOT 0,0..0,17
  .elts[3]
   0] Name 'x' Load - 0,1..0,2
   1] List - 0,4..0,13
     .elts[3]
      0] Name 'b' Load - 0,5..0,6
      1] Name 'c' Load - 0,8..0,9
      2] Name 'd' Load - 0,11..0,12
     .ctx Load
   2] Name 'y' Load - 0,15..0,16
  .ctx Load
'''),
],

'basic_Tuple': [  # ................................................................................

('', None, None, None, {}, ('Tuple',
r'''(a, b, c)'''),
r'''MTuple''', (None,
r'''(__FST_, __FST_)'''),
r'''((a, b, c), (a, b, c))''', r'''
Tuple - ROOT 0,0..0,22
  .elts[2]
   0] Tuple - 0,1..0,10
     .elts[3]
      0] Name 'a' Load - 0,2..0,3
      1] Name 'b' Load - 0,5..0,6
      2] Name 'c' Load - 0,8..0,9
     .ctx Load
   1] Tuple - 0,12..0,21
     .elts[3]
      0] Name 'a' Load - 0,13..0,14
      1] Name 'b' Load - 0,16..0,17
      2] Name 'c' Load - 0,19..0,20
     .ctx Load
  .ctx Load
'''),

('', None, None, None, {}, ('Tuple',
r'''(a, b, c)'''),
r'''MTuple(elts=M(e=...))''', (None,
r'''(__FST_e)'''),
r'''(a, b, c)''', r'''
Tuple - ROOT 0,0..0,9
  .elts[3]
   0] Name 'a' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
  .ctx Load
'''),

('', None, None, None, {}, ('Tuple',
r'''(a, b, c)'''),
r'''MTuple(elts=[..., M(e=...), ...])''', (None,
r'''(__FST_e)'''),
r'''b''',
r'''Name 'b' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, ('Tuple',
r'''(a, b, c)'''),
r'''MTuple(elts=[..., M(e=...), ...])''', (None,
r'''(__FST_e,)'''),
r'''(b,)''', r'''
Tuple - ROOT 0,0..0,4
  .elts[1]
   0] Name 'b' Load - 0,1..0,2
  .ctx Load
'''),

('', None, None, None, {}, ('Tuple',
r'''(a, b, c)'''),
r'''MTuple(elts=M(e=...))''', (None,
r'''(x, __FST_e, y)'''),
r'''(x, a, b, c, y)''', r'''
Tuple - ROOT 0,0..0,15
  .elts[5]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'a' Load - 0,4..0,5
   2] Name 'b' Load - 0,7..0,8
   3] Name 'c' Load - 0,10..0,11
   4] Name 'y' Load - 0,13..0,14
  .ctx Load
'''),

('', None, None, None, {}, ('Tuple',
r'''(a, b, c)'''),
r'''MTuple(elts=[..., M(e=...), ...])''', (None,
r'''(x, __FST_e, y)'''),
r'''(x, b, y)''', r'''
Tuple - ROOT 0,0..0,9
  .elts[3]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'y' Load - 0,7..0,8
  .ctx Load
'''),

('', None, None, None, {}, ('Tuple',
r'''(a, b, c, d, e)'''),
r'''MTuple(elts=[..., MQSTAR(a=...), ...])''', ('Tuple',
r'''(x, __FST_a, y)'''),
r'''(x, b, c, d, y)''', r'''
Tuple - ROOT 0,0..0,15
  .elts[5]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'c' Load - 0,7..0,8
   3] Name 'd' Load - 0,10..0,11
   4] Name 'y' Load - 0,13..0,14
  .ctx Load
'''),

('', None, None, None, {}, ('Tuple',
r'''(a, b, c, d, e)'''),
r'''MTuple(elts=[..., MQSTAR(a=...), ...])''', ('Tuple',
r'''(x, __FSO_a, y)'''),
r'''(x, (b, c, d), y)''', r'''
Tuple - ROOT 0,0..0,17
  .elts[3]
   0] Name 'x' Load - 0,1..0,2
   1] Tuple - 0,4..0,13
     .elts[3]
      0] Name 'b' Load - 0,5..0,6
      1] Name 'c' Load - 0,8..0,9
      2] Name 'd' Load - 0,11..0,12
     .ctx Load
   2] Name 'y' Load - 0,15..0,16
  .ctx Load
'''),
],

'basic_Slice': [  # ................................................................................

('', None, None, None, {}, ('Slice',
r'''a:b:c'''),
r'''MSlice''', (None,
r'''__FST_'''),
r'''a:b:c''', r'''
Slice - ROOT 0,0..0,5
  .lower Name 'a' Load - 0,0..0,1
  .upper Name 'b' Load - 0,2..0,3
  .step Name 'c' Load - 0,4..0,5
'''),

('', None, None, None, {}, ('Slice',
r'''a:b:c'''),
r'''MSlice(lower=M(l=...), upper=M(u=...), step=M(s=...))''', (None,
r'''__FST_s:__FST_l:__FST_u'''),
r'''c:a:b''', r'''
Slice - ROOT 0,0..0,5
  .lower Name 'c' Load - 0,0..0,1
  .upper Name 'a' Load - 0,2..0,3
  .step Name 'b' Load - 0,4..0,5
'''),
],

'basic_comprehension': [  # ................................................................................

('', None, None, None, {}, ('comprehension',
r'''for a in b if c if d'''),
r'''Mcomprehension''', (None,
r'''__FST_'''),
r'''for a in b if c if d''', r'''
comprehension - ROOT 0,0..0,20
  .target Name 'a' Store - 0,4..0,5
  .iter Name 'b' Load - 0,9..0,10
  .ifs[2]
   0] Name 'c' Load - 0,14..0,15
   1] Name 'd' Load - 0,19..0,20
  .is_async 0
'''),

('', None, None, None, {}, ('comprehension',
r'''for a in b if c if d'''),
r'''Mcomprehension(target=M(t=...), iter=M(i=...), ifs=M(f=...))''', (None,
r'''for __FST_t in __FST_i if __FST_f if __FST_f'''),
r'''for a in b if c if d if c if d''', r'''
comprehension - ROOT 0,0..0,30
  .target Name 'a' Store - 0,4..0,5
  .iter Name 'b' Load - 0,9..0,10
  .ifs[4]
   0] Name 'c' Load - 0,14..0,15
   1] Name 'd' Load - 0,19..0,20
   2] Name 'c' Load - 0,24..0,25
   3] Name 'd' Load - 0,29..0,30
  .is_async 0
'''),

('', None, None, None, {}, ('comprehension',
r'''for a in b if c if d'''),
r'''Mcomprehension(target=M(t=...), iter=M(i=...), ifs=M(f=...))''', (None,
r'''for __FST_i in __FST_t if x if __FST_f if y if __FST_f if z'''),
r'''for b in a if x if c if d if y if c if d if z''', r'''
comprehension - ROOT 0,0..0,45
  .target Name 'b' Store - 0,4..0,5
  .iter Name 'a' Load - 0,9..0,10
  .ifs[7]
   0] Name 'x' Load - 0,14..0,15
   1] Name 'c' Load - 0,19..0,20
   2] Name 'd' Load - 0,24..0,25
   3] Name 'y' Load - 0,29..0,30
   4] Name 'c' Load - 0,34..0,35
   5] Name 'd' Load - 0,39..0,40
   6] Name 'z' Load - 0,44..0,45
  .is_async 0
'''),
],

'basic_ExceptHandler': [  # ................................................................................

('', None, None, None, {}, ('ExceptHandler',
r'''except: pass'''),
r'''MExceptHandler(type=M(t=...), name=M(n=...), body=M(b=...))''', (None,
r'''except __FST_t as __FST_n: __FST_b; return'''), r'''
except:
    pass
    return
''', r'''
ExceptHandler - ROOT 0,0..2,10
  .body[2]
   0] Pass - 1,4..1,8
   1] Return - 2,4..2,10
'''),

('', None, None, None, {}, ('ExceptHandler',
r'''except: pass'''),
r'''MExceptHandler(type=M(t=...), name=M(n=...), body=M(b=...))''', (None,
r'''except __FST_t: __FST_b; return'''), r'''
except:
    pass
    return
''', r'''
ExceptHandler - ROOT 0,0..2,10
  .body[2]
   0] Pass - 1,4..1,8
   1] Return - 2,4..2,10
'''),

('', None, None, None, {}, ('ExceptHandler',
r'''except Exception as exc: pass'''),
r'''MExceptHandler(type=M(t=...), name=M(n=...), body=M(b=...))''', (None,
r'''except __FST_t as __FST_n: __FST_b; __FST_b'''), r'''
except Exception as exc:
    pass
    pass
''', r'''
ExceptHandler - ROOT 0,0..2,8
  .type Name 'Exception' Load - 0,7..0,16
  .name 'exc'
  .body[2]
   0] Pass - 1,4..1,8
   1] Pass - 2,4..2,8
'''),

('', None, None, None, {}, ('ExceptHandler',
r'''except Exception as exc: pass'''),
r'''MExceptHandler(type=M(t=...), name=M(n=...), body=M(b=...))''', (None,
r'''except __FST_n: __FST_b; __FST_b'''), r'''
except exc:
    pass
    pass
''', r'''
ExceptHandler - ROOT 0,0..2,8
  .type Name 'exc' Load - 0,7..0,10
  .body[2]
   0] Pass - 1,4..1,8
   1] Pass - 2,4..2,8
'''),

('', None, None, None, {}, ('ExceptHandler',
r'''except Exception as exc: pass'''),
r'''MExceptHandler(type=M(t=...), name=M(n=...), body=M(b=...))''', (None,
r'''except __FST_n as __FST_t: __FST_b; __FST_b'''), r'''
except exc as Exception:
    pass
    pass
''', r'''
ExceptHandler - ROOT 0,0..2,8
  .type Name 'exc' Load - 0,7..0,10
  .name 'Exception'
  .body[2]
   0] Pass - 1,4..1,8
   1] Pass - 2,4..2,8
'''),
],

'basic_arguments': [  # ................................................................................

('', None, None, None, {}, ('FunctionDef',
r'''def f(a, b): pass'''),
r'''Marg''', ('arg',
r'''__FST_: int'''),
r'''def f(a: int, b: int): pass''', r'''
FunctionDef - ROOT 0,0..0,27
  .name 'f'
  .args arguments - 0,6..0,20
    .args[2]
     0] arg - 0,6..0,12
       .arg 'a'
       .annotation Name 'int' Load - 0,9..0,12
     1] arg - 0,14..0,20
       .arg 'b'
       .annotation Name 'int' Load - 0,17..0,20
  .body[1]
   0] Pass - 0,23..0,27
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(a, b): pass'''),
r'''Marg''', ('arguments',
r'''__FST_: int = 1'''),
r'''**NodeError('expecting arg, got arguments, could not coerce')**'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(a, b): pass'''),
r'''Marguments''', ('arguments',
r'''__FST_'''),
r'''def f(a, b): pass''', r'''
FunctionDef - ROOT 0,0..0,17
  .name 'f'
  .args arguments - 0,6..0,10
    .args[2]
     0] arg - 0,6..0,7
       .arg 'a'
     1] arg - 0,9..0,10
       .arg 'b'
  .body[1]
   0] Pass - 0,13..0,17
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(a, b): pass'''),
r'''Marguments(_all=[M(t=...), MQSTAR])''', ('arguments',
r'''__FST_t'''),
r'''def f(a): pass''', r'''
FunctionDef - ROOT 0,0..0,14
  .name 'f'
  .args arguments - 0,6..0,7
    .args[1]
     0] arg - 0,6..0,7
       .arg 'a'
  .body[1]
   0] Pass - 0,10..0,14
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(a, /, b=1, *c, d=2, **e): pass'''),
r'''MFunctionDef(args=M(a=arguments))''', ('FunctionDef',
r'''def g(__FST_a): pass'''),
r'''def g(a, /, b=1, *c, d=2, **e): pass''', r'''
FunctionDef - ROOT 0,0..0,36
  .name 'g'
  .args arguments - 0,6..0,29
    .posonlyargs[1]
     0] arg - 0,6..0,7
       .arg 'a'
    .args[1]
     0] arg - 0,12..0,13
       .arg 'b'
    .vararg arg - 0,18..0,19
      .arg 'c'
    .kwonlyargs[1]
     0] arg - 0,21..0,22
       .arg 'd'
    .kw_defaults[1]
     0] Constant 2 - 0,23..0,24
    .kwarg arg - 0,28..0,29
      .arg 'e'
    .defaults[1]
     0] Constant 1 - 0,14..0,15
  .body[1]
   0] Pass - 0,32..0,36
'''),

('', None, None, None, {}, ('arguments',
r'''a, /, b=1, *c, d=2, **e'''),
r'''Marguments''', ('arguments',
r'''x, __FST_DEL, z'''),
r'''x, z''', r'''
arguments - ROOT 0,0..0,4
  .args[2]
   0] arg - 0,0..0,1
     .arg 'x'
   1] arg - 0,3..0,4
     .arg 'z'
'''),

('', None, None, None, {}, ('arguments',
r'''a=0, /, b=1, *, c=2'''),
r'''Marguments(posonlyargs=[M(pos=...)], args=[M(arg=...)], kwonlyargs=[M(kw=...)], defaults=[M(d0=...), M(d1=...)], kw_defaults=[M(dk=...)])''', ('arguments',
r'''__FST_kw=__FST_d1, /, __FST_pos=__FST_dk, *, __FST_arg=__FST_d0'''),
r'''c=1, /, a=2, *, b=0''', r'''
arguments - ROOT 0,0..0,19
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'c'
  .args[1]
   0] arg - 0,8..0,9
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,16..0,17
     .arg 'b'
  .kw_defaults[1]
   0] Constant 0 - 0,18..0,19
  .defaults[2]
   0] Constant 1 - 0,2..0,3
   1] Constant 2 - 0,10..0,11
'''),

('', None, None, None, {}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, *, __FST_a1'''),
r'''c=3, /, a=1, *, b=2''', r'''
arguments - ROOT 0,0..0,19
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'c'
  .args[1]
   0] arg - 0,8..0,9
     .arg 'a'
  .kwonlyargs[1]
   0] arg - 0,16..0,17
     .arg 'b'
  .kw_defaults[1]
   0] Constant 2 - 0,18..0,19
  .defaults[2]
   0] Constant 3 - 0,2..0,3
   1] Constant 1 - 0,10..0,11
'''),

('', None, None, None, {'args_as': None}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, *, __FST_a1'''),
r'''**NodeError('posonlyargs cannot follow kwonlyargs')**'''),

('', None, None, None, {'args_as': 'arg'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, *, __FST_a1'''),
r'''c=3, a=1, b=2''', r'''
arguments - ROOT 0,0..0,13
  .args[3]
   0] arg - 0,0..0,1
     .arg 'c'
   1] arg - 0,5..0,6
     .arg 'a'
   2] arg - 0,10..0,11
     .arg 'b'
  .defaults[3]
   0] Constant 3 - 0,2..0,3
   1] Constant 1 - 0,7..0,8
   2] Constant 2 - 0,12..0,13
'''),

('', None, None, None, {'args_as': 'pos'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, *, __FST_a1'''),
r'''**NodeError('posonlyargs cannot follow args')**'''),

('', None, None, None, {'args_as': 'pos'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, __FST_a0, __FST_a1'''),
r'''**NodeError('posonlyargs cannot follow args')**'''),

('', None, None, None, {'args_as': 'pos'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, __FST_a0, __FST_a1, /'''),
r'''c=3, a=1, b=2, /''', r'''
arguments - ROOT 0,0..0,16
  .posonlyargs[3]
   0] arg - 0,0..0,1
     .arg 'c'
   1] arg - 0,5..0,6
     .arg 'a'
   2] arg - 0,10..0,11
     .arg 'b'
  .defaults[3]
   0] Constant 3 - 0,2..0,3
   1] Constant 1 - 0,7..0,8
   2] Constant 2 - 0,12..0,13
'''),

('', None, None, None, {'args_as': 'arg'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, *, __FST_a1'''),
r'''c=3, a=1, b=2''', r'''
arguments - ROOT 0,0..0,13
  .args[3]
   0] arg - 0,0..0,1
     .arg 'c'
   1] arg - 0,5..0,6
     .arg 'a'
   2] arg - 0,10..0,11
     .arg 'b'
  .defaults[3]
   0] Constant 3 - 0,2..0,3
   1] Constant 1 - 0,7..0,8
   2] Constant 2 - 0,12..0,13
'''),

('', None, None, None, {'args_as': 'arg'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, *, __FST_a1, __FST_a1'''),
r'''**NodeError('args cannot follow kwonlyargs')**'''),

('', None, None, None, {'args_as': 'arg'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, __FST_a1, __FST_a1'''),
r'''c=3, a=1, b=2, b=2''', r'''
arguments - ROOT 0,0..0,18
  .args[4]
   0] arg - 0,0..0,1
     .arg 'c'
   1] arg - 0,5..0,6
     .arg 'a'
   2] arg - 0,10..0,11
     .arg 'b'
   3] arg - 0,15..0,16
     .arg 'b'
  .defaults[4]
   0] Constant 3 - 0,2..0,3
   1] Constant 1 - 0,7..0,8
   2] Constant 2 - 0,12..0,13
   3] Constant 2 - 0,17..0,18
'''),

('', None, None, None, {'args_as': 'kw'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, *, __FST_a1'''),
r'''*, c=3, a=1, b=2''', r'''
arguments - ROOT 0,0..0,16
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'c'
   1] arg - 0,8..0,9
     .arg 'a'
   2] arg - 0,13..0,14
     .arg 'b'
  .kw_defaults[3]
   0] Constant 3 - 0,5..0,6
   1] Constant 1 - 0,10..0,11
   2] Constant 2 - 0,15..0,16
'''),

('', None, None, None, {'args_as': 'kw'}, ('arguments',
r'''a=1, /, b=2, *, c=3'''),
r'''Marguments(_all=[M(a0=...), M(a1=...), M(a2=...)])''', ('arguments',
r'''__FST_a2, /, __FST_a0, *, __FST_a1'''),
r'''*, c=3, a=1, b=2''', r'''
arguments - ROOT 0,0..0,16
  .kwonlyargs[3]
   0] arg - 0,3..0,4
     .arg 'c'
   1] arg - 0,8..0,9
     .arg 'a'
   2] arg - 0,13..0,14
     .arg 'b'
  .kw_defaults[3]
   0] Constant 3 - 0,5..0,6
   1] Constant 1 - 0,10..0,11
   2] Constant 2 - 0,15..0,16
'''),

('', None, None, None, {}, ('arguments',
r'''a, b=1, /, c=2, *d, **e'''),
r'''Marguments(_all=[..., MQSTAR(a=...), ...])''', ('arguments',
r'''x, /, __FST_a'''),
r'''x, /, b=1, c=2, *d''', r'''
arguments - ROOT 0,0..0,18
  .posonlyargs[1]
   0] arg - 0,0..0,1
     .arg 'x'
  .args[2]
   0] arg - 0,6..0,7
     .arg 'b'
   1] arg - 0,11..0,12
     .arg 'c'
  .vararg arg - 0,17..0,18
    .arg 'd'
  .defaults[2]
   0] Constant 1 - 0,8..0,9
   1] Constant 2 - 0,13..0,14
'''),

('', None, None, None, {'args_as': None}, ('arguments',
r'''a, b=1, /, c=2, *d, **e'''),
r'''Marguments(_all=[..., MQSTAR(a=...), ...])''', ('arguments',
r'''x, /, __FST_a'''),
r'''x, b=1, /, c=2, *d''', r'''
arguments - ROOT 0,0..0,18
  .posonlyargs[2]
   0] arg - 0,0..0,1
     .arg 'x'
   1] arg - 0,3..0,4
     .arg 'b'
  .args[1]
   0] arg - 0,11..0,12
     .arg 'c'
  .vararg arg - 0,17..0,18
    .arg 'd'
  .defaults[2]
   0] Constant 1 - 0,5..0,6
   1] Constant 2 - 0,13..0,14
'''),
],

'basic_arg': [  # ................................................................................

('', None, None, None, {}, ('arg',
r'''a: int'''),
r'''Marg(arg=M(a=...), annotation=M(n=...))''',
r'''__FST_a = __FST_n''',
r'''a = int''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'int' Load - 0,4..0,7
'''),

('', None, None, None, {}, ('arg',
r'''a: int'''),
r'''Marg(arg=M(a=...), annotation=M(n=...))''', ('arg',
r'''__FST_a: __FST_n'''),
r'''a: int''', r'''
arg - ROOT 0,0..0,6
  .arg 'a'
  .annotation Name 'int' Load - 0,3..0,6
'''),

('', None, None, None, {}, ('arg',
r'''a: int'''),
r'''Marg(arg=M(a=...), annotation=M(n=...))''', ('arg',
r'''__FST_a: __FST_DEL'''),
r'''a''', r'''
arg - ROOT 0,0..0,1
  .arg 'a'
'''),

('', None, None, None, {}, ('arg',
r'''a: int'''),
r'''Marg(arg=M(a=...), annotation=M(n=...))''', ('arg',
r'''__FST_n: __FST_a'''),
r'''int: a''', r'''
arg - ROOT 0,0..0,6
  .arg 'int'
  .annotation Name 'a' Load - 0,5..0,6
'''),
],

'basic_keyword': [  # ................................................................................

('', None, None, None, {}, ('keyword',
r'''k=w'''),
r'''Mkeyword(arg=M(a=...), value=M(v=...))''',
r'''__FST_a = __FST_v''',
r'''k = w''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'k' Store - 0,0..0,1
  .value Name 'w' Load - 0,4..0,5
'''),

('', None, None, None, {}, ('keyword',
r'''k=w'''),
r'''Mkeyword(arg=M(a=...), value=M(v=...))''', ('keyword',
r'''__FST_a=__FST_v'''),
r'''k=w''', r'''
keyword - ROOT 0,0..0,3
  .arg 'k'
  .value Name 'w' Load - 0,2..0,3
'''),

('', None, None, None, {}, ('keyword',
r'''k=w'''),
r'''Mkeyword(arg=M(a=...), value=M(v=...))''', ('keyword',
r'''**__FST_v'''),
r'''**w''', r'''
keyword - ROOT 0,0..0,3
  .value Name 'w' Load - 0,2..0,3
'''),

('', None, None, None, {}, ('keyword',
r'''k=w'''),
r'''Mkeyword(arg=M(a=...), value=M(v=...))''', ('keyword',
r'''__FST_v=__FST_a'''),
r'''w=k''', r'''
keyword - ROOT 0,0..0,3
  .arg 'w'
  .value Name 'k' Load - 0,2..0,3
'''),
],

'basic_alias': [  # ................................................................................

('', None, None, None, {}, ('alias',
r'''name as asname'''),
r'''Malias(name=M(n=...), asname=M(a=...))''',
r'''__FST_n = __FST_a''',
r'''name = asname''', r'''
Assign - ROOT 0,0..0,13
  .targets[1]
   0] Name 'name' Store - 0,0..0,4
  .value Name 'asname' Load - 0,7..0,13
'''),

('', None, None, None, {}, ('alias',
r'''name as asname'''),
r'''Malias(name=M(n=...), asname=M(a=...))''', ('alias',
r'''__FST_a as __FST_n'''),
r'''asname as name''', r'''
alias - ROOT 0,0..0,14
  .name 'asname'
  .asname 'name'
'''),

('', None, None, None, {}, ('alias',
r'''name as asname'''),
r'''Malias(name=M(n=...), asname=M(a=...))''', ('alias',
r'''__FST_n as __FST_a'''),
r'''name as asname''', r'''
alias - ROOT 0,0..0,14
  .name 'name'
  .asname 'asname'
'''),

('', None, None, None, {}, ('alias',
r'''name as asname'''),
r'''Malias(name=M(n=...), asname=M(a=...))''', ('alias',
r'''__FST_n as __FST_DEL'''),
r'''name''', r'''
alias - ROOT 0,0..0,4
  .name 'name'
'''),

('', None, None, None, {}, ('alias',
r'''name as asname'''),
r'''Malias(name=M(n=...), asname=M(a=...))''', ('alias',
r'''__FST_a'''),
r'''asname''',
r'''Name 'asname' Load - ROOT 0,0..0,6'''),

('', None, None, None, {}, ('alias',
r'''name as asname'''),
r'''Malias(name=M(n=...), asname=M(a=...))''', ('alias',
r'''__FST_n'''),
r'''name''',
r'''Name 'name' Load - ROOT 0,0..0,4'''),

('', None, None, None, {}, ('alias',
r'''name as asname'''),
r'''Malias(name=M(n=...), asname=M(a=...))''', (None,
r'''import __FST_a'''),
r'''import asname''', r'''
Import - ROOT 0,0..0,13
  .names[1]
   0] alias - 0,7..0,13
     .name 'asname'
'''),

('', None, None, None, {}, ('alias',
r'''name as asname'''),
r'''Malias(name=M(n=...), asname=M(a=...))''', (None,
r'''import __FST_n'''),
r'''import name''', r'''
Import - ROOT 0,0..0,11
  .names[1]
   0] alias - 0,7..0,11
     .name 'name'
'''),
],

'basic_withitem': [  # ................................................................................

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''',
r'''__FST_n = __FST_a''',
r'''context_expr = optional_vars''', r'''
Assign - ROOT 0,0..0,28
  .targets[1]
   0] Name 'context_expr' Store - 0,0..0,12
  .value Name 'optional_vars' Load - 0,15..0,28
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', ('withitem',
r'''__FST_a as __FST_n'''),
r'''optional_vars as context_expr''', r'''
withitem - ROOT 0,0..0,29
  .context_expr Name 'optional_vars' Load - 0,0..0,13
  .optional_vars Name 'context_expr' Store - 0,17..0,29
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', ('withitem',
r'''__FST_n as __FST_a'''),
r'''context_expr as optional_vars''', r'''
withitem - ROOT 0,0..0,29
  .context_expr Name 'context_expr' Load - 0,0..0,12
  .optional_vars Name 'optional_vars' Store - 0,16..0,29
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', ('withitem',
r'''__FST_n as __FST_DEL'''),
r'''context_expr''', r'''
withitem - ROOT 0,0..0,12
  .context_expr Name 'context_expr' Load - 0,0..0,12
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', ('withitem',
r'''__FST_a'''),
r'''optional_vars''', r'''
withitem - ROOT 0,0..0,13
  .context_expr Name 'optional_vars' Load - 0,0..0,13
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', ('withitem',
r'''__FST_n'''),
r'''context_expr''', r'''
withitem - ROOT 0,0..0,12
  .context_expr Name 'context_expr' Load - 0,0..0,12
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', (None,
r'''with __FST_a: pass'''),
r'''with optional_vars: pass''', r'''
With - ROOT 0,0..0,24
  .items[1]
   0] withitem - 0,5..0,18
     .context_expr Name 'optional_vars' Load - 0,5..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', (None,
r'''with __FST_n: pass'''),
r'''with context_expr: pass''', r'''
With - ROOT 0,0..0,23
  .items[1]
   0] withitem - 0,5..0,17
     .context_expr Name 'context_expr' Load - 0,5..0,17
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', (None,
r'''with __FST_: pass'''),
r'''with context_expr as optional_vars: pass''', r'''
With - ROOT 0,0..0,40
  .items[1]
   0] withitem - 0,5..0,34
     .context_expr Name 'context_expr' Load - 0,5..0,17
     .optional_vars Name 'optional_vars' Store - 0,21..0,34
  .body[1]
   0] Pass - 0,36..0,40
'''),

('', None, None, None, {}, ('withitem',
r'''context_expr as optional_vars'''),
r'''Mwithitem(context_expr=M(n=...), optional_vars=M(a=...))''', (None,
r'''with __FST_a as __FST_n: pass'''),
r'''with optional_vars as context_expr: pass''', r'''
With - ROOT 0,0..0,40
  .items[1]
   0] withitem - 0,5..0,34
     .context_expr Name 'optional_vars' Load - 0,5..0,18
     .optional_vars Name 'context_expr' Store - 0,22..0,34
  .body[1]
   0] Pass - 0,36..0,40
'''),
],

'basic_match_case': [  # ................................................................................

('', None, None, None, {}, ('match_case',
r'''case _ if a: pass'''),
r'''Mmatch_case(pattern=M(p=...), guard=M(g=...), body=M(b=...))''',
r'''__FST_''',
r'''case _ if a: pass''', r'''
match_case - ROOT 0,0..0,17
  .pattern MatchAs - 0,5..0,6
  .guard Name 'a' Load - 0,10..0,11
  .body[1]
   0] Pass - 0,13..0,17
'''),

('', None, None, None, {}, ('match_case',
r'''case _ if a: pass'''),
r'''Mmatch_case(pattern=M(p=...), guard=M(g=...), body=M(b=...))''',
r'''case __FST_g if __FST_p: __FST_b; __FST_p; __FST_g''', r'''
case a if _:
    pass
    _; a
''', r'''
match_case - ROOT 0,0..2,8
  .pattern MatchAs - 0,5..0,6
    .name 'a'
  .guard Name '_' Load - 0,10..0,11
  .body[3]
   0] Pass - 1,4..1,8
   1] Expr - 2,4..2,5
     .value Name '_' Load - 2,4..2,5
   2] Expr - 2,7..2,8
     .value Name 'a' Load - 2,7..2,8
'''),

('', None, None, None, {}, ('match_case',
r'''case [a, b]: pass'''),
r'''Mmatch_case(pattern=MMatchSequence(patterns=[M(p0=...), M(p1=...)]), guard=M(g=...), body=M(b=...))''',
r'''case __FST_p1 as __FST_p0 if __FST_g: __FST_b; __FST_b''', r'''
case b as a:
    pass
    pass
''', r'''
match_case - ROOT 0,0..2,8
  .pattern MatchAs - 0,5..0,11
    .pattern MatchAs - 0,5..0,6
      .name 'b'
    .name 'a'
  .body[2]
   0] Pass - 1,4..1,8
   1] Pass - 2,4..2,8
'''),

('', None, None, None, {}, ('match_case',
r'''case _: a ; b ; c ; d ; e'''),
r'''Mmatch_case(body=[..., MQSTAR(b=...), ...])''', ('match_case',
r'''case x: x; __FST_b; y'''), r'''
case x:
    x
    b ; c ; d
    y
''', r'''
match_case - ROOT 0,0..3,5
  .pattern MatchAs - 0,5..0,6
    .name 'x'
  .body[5]
   0] Expr - 1,4..1,5
     .value Name 'x' Load - 1,4..1,5
   1] Expr - 2,4..2,5
     .value Name 'b' Load - 2,4..2,5
   2] Expr - 2,8..2,9
     .value Name 'c' Load - 2,8..2,9
   3] Expr - 2,12..2,13
     .value Name 'd' Load - 2,12..2,13
   4] Expr - 3,4..3,5
     .value Name 'y' Load - 3,4..3,5
'''),
],

'basic_MatchValue': [  # ................................................................................

('', None, None, None, {}, ('pattern',
r'''1'''),
r'''MMatchValue(value=M(v=...))''',
r'''a = __FST_v''',
r'''a = 1''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

('', None, None, None, {}, ('pattern',
r'''1'''),
r'''MMatchValue''',
r'''a = __FST_''',
r'''a = 1''', r'''
Assign - ROOT 0,0..0,5
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Constant 1 - 0,4..0,5
'''),

('', None, None, None, {}, ('pattern',
r'''1'''),
r'''MMatchValue''', ('pattern',
r'''[__FST_DEL]'''),
r'''[]''',
r'''MatchSequence - ROOT 0,0..0,2'''),

('', None, None, None, {}, ('pattern',
r'''1'''),
r'''MMatchValue''', ('pattern',
r'''[__FST_, __FST_DEL, __FST_]'''),
r'''[1, 1]''', r'''
MatchSequence - ROOT 0,0..0,6
  .patterns[2]
   0] MatchValue - 0,1..0,2
     .value Constant 1 - 0,1..0,2
   1] MatchValue - 0,4..0,5
     .value Constant 1 - 0,4..0,5
'''),

('', None, None, None, {}, ('pattern',
r'''1'''),
r'''MMatchValue(value=M(v=...))''', ('pattern',
r'''[__FST_v, __FST_v]'''),
r'''[1, 1]''', r'''
MatchSequence - ROOT 0,0..0,6
  .patterns[2]
   0] MatchValue - 0,1..0,2
     .value Constant 1 - 0,1..0,2
   1] MatchValue - 0,4..0,5
     .value Constant 1 - 0,4..0,5
'''),
],

'basic_MatchSequence': [  # ................................................................................

('', None, None, None, {}, ('pattern',
r'''[a, b]'''),
r'''MMatchSequence(patterns=M(p=...))''', ('pattern',
r'''__FST_'''),
r'''[a, b]''', r'''
MatchSequence - ROOT 0,0..0,6
  .patterns[2]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', None, None, None, {}, ('pattern',
r'''[a, b]'''),
r'''MMatchSequence(patterns=M(p=...))''', ('pattern',
r'''[__FST_]'''),
r'''[[a, b]]''', r'''
MatchSequence - ROOT 0,0..0,8
  .patterns[1]
   0] MatchSequence - 0,1..0,7
     .patterns[2]
      0] MatchAs - 0,2..0,3
        .name 'a'
      1] MatchAs - 0,5..0,6
        .name 'b'
'''),

('', None, None, None, {}, ('pattern',
r'''[a, b]'''),
r'''MMatchSequence(patterns=M(p=...))''', ('pattern',
r'''[__FST_p]'''),
r'''[a, b]''', r'''
MatchSequence - ROOT 0,0..0,6
  .patterns[2]
   0] MatchAs - 0,1..0,2
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
'''),

('', None, None, None, {}, ('pattern',
r'''[a, b]'''),
r'''MMatchSequence(patterns=M(p=...))''', ('pattern',
r'''[x, __FST_, y]'''),
r'''[x, [a, b], y]''', r'''
MatchSequence - ROOT 0,0..0,14
  .patterns[3]
   0] MatchAs - 0,1..0,2
     .name 'x'
   1] MatchSequence - 0,4..0,10
     .patterns[2]
      0] MatchAs - 0,5..0,6
        .name 'a'
      1] MatchAs - 0,8..0,9
        .name 'b'
   2] MatchAs - 0,12..0,13
     .name 'y'
'''),

('', None, None, None, {}, ('pattern',
r'''[a, b]'''),
r'''MMatchSequence(patterns=M(p=...))''', ('pattern',
r'''[x, __FST_p, y]'''),
r'''[x, a, b, y]''', r'''
MatchSequence - ROOT 0,0..0,12
  .patterns[4]
   0] MatchAs - 0,1..0,2
     .name 'x'
   1] MatchAs - 0,4..0,5
     .name 'a'
   2] MatchAs - 0,7..0,8
     .name 'b'
   3] MatchAs - 0,10..0,11
     .name 'y'
'''),

('', None, None, None, {}, ('pattern',
r'''[a, b]'''),
r'''MMatchSequence(patterns=[M(p0=...), M(p1=...)])''', ('pattern',
r'''[__FST_p1, x, y, __FST_p0,]'''),
r'''[b, x, y, a,]''', r'''
MatchSequence - ROOT 0,0..0,13
  .patterns[4]
   0] MatchAs - 0,1..0,2
     .name 'b'
   1] MatchAs - 0,4..0,5
     .name 'x'
   2] MatchAs - 0,7..0,8
     .name 'y'
   3] MatchAs - 0,10..0,11
     .name 'a'
'''),

('', None, None, None, {}, ('MatchSequence',
r'''[a, b, c, d, e]'''),
r'''MMatchSequence(patterns=[..., MQSTAR(a=...), ...])''', ('MatchSequence',
r'''[x, __FST_a, y]'''),
r'''[x, b, c, d, y]''', r'''
MatchSequence - ROOT 0,0..0,15
  .patterns[5]
   0] MatchAs - 0,1..0,2
     .name 'x'
   1] MatchAs - 0,4..0,5
     .name 'b'
   2] MatchAs - 0,7..0,8
     .name 'c'
   3] MatchAs - 0,10..0,11
     .name 'd'
   4] MatchAs - 0,13..0,14
     .name 'y'
'''),
],

'basic_MatchMapping': [  # ................................................................................

('', None, None, None, {}, ('MatchMapping',
r'''{a.b: c.d}'''),
r'''MMatchMapping(keys=[M(k=...)], patterns=[M(v=...)])''', ('pattern',
r'''{__FST_v.x: __FST_k}'''),
r'''{c.d.x: a.b}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[1]
   0] Attribute - 0,1..0,6
     .value Attribute - 0,1..0,4
       .value Name 'c' Load - 0,1..0,2
       .attr 'd'
       .ctx Load
     .attr 'x'
     .ctx Load
  .patterns[1]
   0] MatchValue - 0,8..0,11
     .value Attribute - 0,8..0,11
       .value Name 'a' Load - 0,8..0,9
       .attr 'b'
       .ctx Load
'''),

('', None, None, None, {}, ('MatchMapping',
r'''{a.b: c.d}'''),
r'''MMatchMapping(_all=[M(e=...)])''', ('pattern',
r'''__FST_e'''),
r'''{a.b: c.d}''', r'''
MatchMapping - ROOT 0,0..0,10
  .keys[1]
   0] Attribute - 0,1..0,4
     .value Name 'a' Load - 0,1..0,2
     .attr 'b'
     .ctx Load
  .patterns[1]
   0] MatchValue - 0,6..0,9
     .value Attribute - 0,6..0,9
       .value Name 'c' Load - 0,6..0,7
       .attr 'd'
       .ctx Load
'''),

('', None, None, None, {}, ('MatchMapping',
r'''{1: u, a.b: c.d, 2: v}'''),
r'''MMatchMapping(_all=[..., M(e=...), ...])''', ('pattern',
r'''__FST_e'''),
r'''{a.b: c.d}''', r'''
MatchMapping - ROOT 0,0..0,10
  .keys[1]
   0] Attribute - 0,1..0,4
     .value Name 'a' Load - 0,1..0,2
     .attr 'b'
     .ctx Load
  .patterns[1]
   0] MatchValue - 0,6..0,9
     .value Attribute - 0,6..0,9
       .value Name 'c' Load - 0,6..0,7
       .attr 'd'
       .ctx Load
'''),

('', None, None, None, {}, ('MatchMapping',
r'''{1: u, a.b: c.d, 2: v}'''),
r'''MMatchMapping(_all=M(e=...))''', ('pattern',
r'''__FST_e'''),
r'''{1: u, a.b: c.d, 2: v}''', r'''
MatchMapping - ROOT 0,0..0,22
  .keys[3]
   0] Constant 1 - 0,1..0,2
   1] Attribute - 0,7..0,10
     .value Name 'a' Load - 0,7..0,8
     .attr 'b'
     .ctx Load
   2] Constant 2 - 0,17..0,18
  .patterns[3]
   0] MatchAs - 0,4..0,5
     .name 'u'
   1] MatchValue - 0,12..0,15
     .value Attribute - 0,12..0,15
       .value Name 'c' Load - 0,12..0,13
       .attr 'd'
       .ctx Load
   2] MatchAs - 0,20..0,21
     .name 'v'
'''),

('', None, None, None, {}, ('MatchMapping',
r'''{a.b: c.d, **rest}'''),
r'''MMatchMapping(keys=[M(k=...)], patterns=[M(v=...)], rest=M(r=...))''', ('pattern',
r'''{__FST_r.x: __FST_r, **__FST_r}'''),
r'''{rest.x: rest, **rest}''', r'''
MatchMapping - ROOT 0,0..0,22
  .keys[1]
   0] Attribute - 0,1..0,7
     .value Name 'rest' Load - 0,1..0,5
     .attr 'x'
     .ctx Load
  .patterns[1]
   0] MatchAs - 0,9..0,13
     .name 'rest'
  .rest 'rest'
'''),

('', None, None, None, {}, ('MatchMapping',
r'''{a.b: c.d, **rest}'''),
r'''MMatchMapping(keys=[M(k=...)], patterns=[M(v=...)], rest=M(r=...))''', ('pattern',
r'''{__FST_r.x: __FST_r, **__FST_DEL}'''),
r'''{rest.x: rest}''', r'''
MatchMapping - ROOT 0,0..0,14
  .keys[1]
   0] Attribute - 0,1..0,7
     .value Name 'rest' Load - 0,1..0,5
     .attr 'x'
     .ctx Load
  .patterns[1]
   0] MatchAs - 0,9..0,13
     .name 'rest'
'''),

('', None, None, None, {}, ('MatchMapping',
r'''{1: a, 2: b, 3: c}'''),
r'''MMatchMapping(_all=[..., M(d=...), ...])''', ('MatchMapping',
r'''{'...': __FST_d, '...': __FST_d}'''),
r'''{2: b, 2: b}''', r'''
MatchMapping - ROOT 0,0..0,12
  .keys[2]
   0] Constant 2 - 0,1..0,2
   1] Constant 2 - 0,7..0,8
  .patterns[2]
   0] MatchAs - 0,4..0,5
     .name 'b'
   1] MatchAs - 0,10..0,11
     .name 'b'
'''),

('', None, None, None, {}, ('MatchMapping',
r'''{1: a, **b}'''),
r'''MMatchMapping(_all=[..., M(d=...)])''', ('MatchMapping',
r'''{'...': __FST_d}'''),
r'''{**b}''', r'''
MatchMapping - ROOT 0,0..0,5
  .rest 'b'
'''),

('', None, None, None, {}, ('MatchMapping',
r'''{1: a, 2: b, 3: c, 4: d, 5: e}'''),
r'''MMatchMapping(_all=[..., MQSTAR(d=...), ...])''', ('MatchMapping',
r'''{-1: x, '...': __FST_d, -2: y}'''),
r'''{-1: x, 2: b, 3: c, 4: d, -2: y}''', r'''
MatchMapping - ROOT 0,0..0,32
  .keys[5]
   0] UnaryOp - 0,1..0,3
     .op USub - 0,1..0,2
     .operand Constant 1 - 0,2..0,3
   1] Constant 2 - 0,8..0,9
   2] Constant 3 - 0,14..0,15
   3] Constant 4 - 0,20..0,21
   4] UnaryOp - 0,26..0,28
     .op USub - 0,26..0,27
     .operand Constant 2 - 0,27..0,28
  .patterns[5]
   0] MatchAs - 0,5..0,6
     .name 'x'
   1] MatchAs - 0,11..0,12
     .name 'b'
   2] MatchAs - 0,17..0,18
     .name 'c'
   3] MatchAs - 0,23..0,24
     .name 'd'
   4] MatchAs - 0,30..0,31
     .name 'y'
'''),
],

'basic_MatchClass': [  # ................................................................................

('', None, None, None, {}, ('MatchClass',
r'''cls(a, b)'''),
r'''MMatchClass(cls=M(c=...), patterns=M(p=...))''', ('pattern',
r'''newcls(__FST_c, __FST_p)'''),
r'''newcls(cls, a, b)''', r'''
MatchClass - ROOT 0,0..0,17
  .cls Name 'newcls' Load - 0,0..0,6
  .patterns[3]
   0] MatchAs - 0,7..0,10
     .name 'cls'
   1] MatchAs - 0,12..0,13
     .name 'a'
   2] MatchAs - 0,15..0,16
     .name 'b'
'''),

('', None, None, None, {}, ('MatchClass',
r'''cls(a=b)'''),
r'''MMatchClass(kwd_attrs=[M(a=...)], kwd_patterns=[M(p=...)])''', ('pattern',
r'''__FST_a(__FST_p=__FST_a)'''),
r'''a(b=a)''', r'''
MatchClass - ROOT 0,0..0,6
  .cls Name 'a' Load - 0,0..0,1
  .kwd_attrs[1]
   0] 'b'
  .kwd_patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
'''),

('', None, None, None, {}, ('MatchClass',
r'''cls(a, b, c, d, e)'''),
r'''MMatchClass(patterns=[..., MQSTAR(a=...), ...])''', ('MatchClass',
r'''kls(x, __FST_a, y)'''),
r'''kls(x, b, c, d, y)''', r'''
MatchClass - ROOT 0,0..0,18
  .cls Name 'kls' Load - 0,0..0,3
  .patterns[5]
   0] MatchAs - 0,4..0,5
     .name 'x'
   1] MatchAs - 0,7..0,8
     .name 'b'
   2] MatchAs - 0,10..0,11
     .name 'c'
   3] MatchAs - 0,13..0,14
     .name 'd'
   4] MatchAs - 0,16..0,17
     .name 'y'
'''),
],

'basic_MatchStar': [  # ................................................................................

('', None, None, None, {}, ('MatchStar',
r'''*s'''),
r'''MMatchStar(name=M(n=...))''', ('MatchStar',
r'''*__FST_n'''),
r'''*s''', r'''
MatchStar - ROOT 0,0..0,2
  .name 's'
'''),

('', None, None, None, {}, ('MatchStar',
r'''*s'''),
r'''MMatchStar(name=M(n=...))''', ('pattern',
r'''__FST_'''),
r'''*s''', r'''
MatchStar - ROOT 0,0..0,2
  .name 's'
'''),
],

'basic_MatchAs': [  # ................................................................................

('', None, None, None, {}, ('pattern',
r'''a as b'''),
r'''MMatchAs(pattern=M(p=...), name=M(n=...))''', ('pattern',
r'''__FST_n as __FST_p'''),
r'''b as a''', r'''
MatchAs - ROOT 0,0..0,6
  .pattern MatchAs - 0,0..0,1
    .name 'b'
  .name 'a'
'''),

('', None, None, None, {}, ('pattern',
r'''a as b'''),
r'''MMatchAs(pattern=M(p=...), name=M(n=...))''', ('pattern',
r'''__FST_DEL as __FST_p'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),

('', None, None, None, {}, ('pattern',
r'''a'''),
r'''MMatchAs(name=M(n=...))''', ('pattern',
r'''__FST_n as __FST_n'''),
r'''a as a''', r'''
MatchAs - ROOT 0,0..0,6
  .pattern MatchAs - 0,0..0,1
    .name 'a'
  .name 'a'
'''),

('', None, None, None, {}, ('pattern',
r'''a as b'''),
r'''MMatchAs(pattern=M(p=...))''', ('pattern',
r'''__FST_p'''),
r'''a''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'a'
'''),
],

'basic_MatchOr': [  # ................................................................................

('', None, None, None, {}, ('pattern',
r'''a | b | c'''),
r'''MMatchOr''', ('pattern',
r'''[__FST_, __FST_]'''),
r'''[a | b | c, a | b | c]''', r'''
MatchSequence - ROOT 0,0..0,22
  .patterns[2]
   0] MatchOr - 0,1..0,10
     .patterns[3]
      0] MatchAs - 0,1..0,2
        .name 'a'
      1] MatchAs - 0,5..0,6
        .name 'b'
      2] MatchAs - 0,9..0,10
        .name 'c'
   1] MatchOr - 0,12..0,21
     .patterns[3]
      0] MatchAs - 0,12..0,13
        .name 'a'
      1] MatchAs - 0,16..0,17
        .name 'b'
      2] MatchAs - 0,20..0,21
        .name 'c'
'''),

('', None, None, None, {}, ('pattern',
r'''a | b | c'''),
r'''MMatchOr(patterns=[..., M(p=...), ...])''', ('pattern',
r'''__FST_'''),
r'''a | b | c''', r'''
MatchOr - ROOT 0,0..0,9
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'a'
   1] MatchAs - 0,4..0,5
     .name 'b'
   2] MatchAs - 0,8..0,9
     .name 'c'
'''),

('', None, None, None, {}, ('pattern',
r'''a | b | c'''),
r'''MMatchOr(patterns=[..., M(p=...), ...])''', ('pattern',
r'''__FST_p'''),
r'''b''', r'''
MatchAs - ROOT 0,0..0,1
  .name 'b'
'''),

('', None, None, None, {}, ('pattern',
r'''a | b | c'''),
r'''MMatchOr''', ('pattern',
r'''x | __FST_ | y'''),
r'''x | (a | b | c) | y''', r'''
MatchOr - ROOT 0,0..0,19
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'x'
   1] MatchOr - 0,5..0,14
     .patterns[3]
      0] MatchAs - 0,5..0,6
        .name 'a'
      1] MatchAs - 0,9..0,10
        .name 'b'
      2] MatchAs - 0,13..0,14
        .name 'c'
   2] MatchAs - 0,18..0,19
     .name 'y'
'''),

('', None, None, None, {}, ('pattern',
r'''a | b | c'''),
r'''MMatchOr(patterns=M(p=...))''', ('pattern',
r'''x | __FST_p | y'''),
r'''x | a | b | c | y''', r'''
MatchOr - ROOT 0,0..0,17
  .patterns[5]
   0] MatchAs - 0,0..0,1
     .name 'x'
   1] MatchAs - 0,4..0,5
     .name 'a'
   2] MatchAs - 0,8..0,9
     .name 'b'
   3] MatchAs - 0,12..0,13
     .name 'c'
   4] MatchAs - 0,16..0,17
     .name 'y'
'''),

('', None, None, None, {}, ('MatchOr',
r'''a | b | c | d | e'''),
r'''MMatchOr(patterns=[..., MQSTAR(a=...), ...])''', ('MatchOr',
r'''x | __FST_a | y'''),
r'''x | b | c | d | y''', r'''
MatchOr - ROOT 0,0..0,17
  .patterns[5]
   0] MatchAs - 0,0..0,1
     .name 'x'
   1] MatchAs - 0,4..0,5
     .name 'b'
   2] MatchAs - 0,8..0,9
     .name 'c'
   3] MatchAs - 0,12..0,13
     .name 'd'
   4] MatchAs - 0,16..0,17
     .name 'y'
'''),

('', None, None, None, {}, ('MatchOr',
r'''a | b | c | d | e'''),
r'''MMatchOr(patterns=[..., MQSTAR(a=...), ...])''', ('MatchOr',
r'''x | __FSO_a | y'''),
r'''x | (b | c | d) | y''', r'''
MatchOr - ROOT 0,0..0,19
  .patterns[3]
   0] MatchAs - 0,0..0,1
     .name 'x'
   1] MatchOr - 0,5..0,14
     .patterns[3]
      0] MatchAs - 0,5..0,6
        .name 'b'
      1] MatchAs - 0,9..0,10
        .name 'c'
      2] MatchAs - 0,13..0,14
        .name 'd'
   2] MatchAs - 0,18..0,19
     .name 'y'
'''),
],

'basic_TypeVar': [  # ................................................................................

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''T: int'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...))''',
r'''__FST_b = __FST_n''',
r'''int = T''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'int' Store - 0,0..0,3
  .value Name 'T' Load - 0,6..0,7
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''T: int'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...))''', ('TypeVar',
r'''__FST_n: __FST_b'''),
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''T: int'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...))''', ('TypeVar',
r'''__FST_b: __FST_n'''),
r'''int: T''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'int'
  .bound Name 'T' Load - 0,5..0,6
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''T'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...))''', ('TypeVar',
r'''__FST_n: __FST_b'''),
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''T: int'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...))''', ('TypeVar',
r'''__FST_'''),
r'''T: int''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''T: int'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...))''', ('TypeAlias',
r'''type t[__FST_n] = ...'''),
r'''type t[T] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'T'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', None, None, None, {'_ver': 13}, ('TypeVar',
r'''T: int = bool'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...), default_value=M(d=...))''', ('TypeVar',
r'''__FST_n: __FST_b = __FST_d'''),
r'''T: int = bool''', r'''
TypeVar - ROOT 0,0..0,13
  .name 'T'
  .bound Name 'int' Load - 0,3..0,6
  .default_value Name 'bool' Load - 0,9..0,13
'''),

('', None, None, None, {'_ver': 13}, ('TypeVar',
r'''T'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...), default_value=M(d=...))''', ('TypeVar',
r'''__FST_n: __FST_b = __FST_d'''),
r'''T''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'T'
'''),

('', None, None, None, {'_ver': 13}, ('TypeVar',
r'''T: int = bool'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...), default_value=M(d=...))''', ('type_param',
r'''*__FST_n = __FST_d'''),
r'''*T = bool''', r'''
TypeVarTuple - ROOT 0,0..0,9
  .name 'T'
  .default_value Name 'bool' Load - 0,5..0,9
'''),

('', None, None, None, {'_ver': 13}, ('TypeVar',
r'''T: int = bool'''),
r'''MTypeVar(name=M(n=...), bound=M(b=...), default_value=M(d=...))''', ('type_param',
r'''**__FST_n = __FST_d'''),
r'''**T = bool''', r'''
ParamSpec - ROOT 0,0..0,10
  .name 'T'
  .default_value Name 'bool' Load - 0,6..0,10
'''),
],

'basic_ParamSpec': [  # ................................................................................

('', None, None, None, {'_ver': 12}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...))''', ('type_param',
r'''__FST_'''),
r'''**V''', r'''
ParamSpec - ROOT 0,0..0,3
  .name 'V'
'''),

('', None, None, None, {'_ver': 12}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...))''', ('type_param',
r'''**__FST_n'''),
r'''**V''', r'''
ParamSpec - ROOT 0,0..0,3
  .name 'V'
'''),

('', None, None, None, {'_ver': 12}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...))''', ('type_param',
r'''*__FST_n'''),
r'''*V''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'V'
'''),

('', None, None, None, {'_ver': 12}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...))''', ('type_param',
r'''*__FST_'''),
r'''**ParseError("expecting identifier, got '**V'")**'''),

('', None, None, None, {'_ver': 12}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...))''', ('type_param',
r'''__FST_n'''),
r'''V''',
r'''Name 'V' Load - ROOT 0,0..0,1'''),

('', None, None, None, {'_ver': 12}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...))''', ('TypeAlias',
r'''type t[__FST_n] = ...'''),
r'''type t[V] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'V'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', None, None, None, {'_ver': 12}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...))''', ('TypeAlias',
r'''type t[__FST_] = ...'''),
r'''type t[**V] = ...''', r'''
TypeAlias - ROOT 0,0..0,17
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] ParamSpec - 0,7..0,10
     .name 'V'
  .value Constant Ellipsis - 0,14..0,17
'''),

('', None, None, None, {'_ver': 13}, ('ParamSpec',
r'''**V = ()'''),
r'''MParamSpec(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''__FST_n = __FST_d'''),
r'''V = ()''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'V'
  .default_value Tuple - 0,4..0,6
    .ctx Load
'''),

('', None, None, None, {'_ver': 13}, ('ParamSpec',
r'''**V = ()'''),
r'''MParamSpec(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''**__FST_n = __FST_d'''),
r'''**V = ()''', r'''
ParamSpec - ROOT 0,0..0,8
  .name 'V'
  .default_value Tuple - 0,6..0,8
    .ctx Load
'''),

('', None, None, None, {'_ver': 13}, ('ParamSpec',
r'''**V = ()'''),
r'''MParamSpec(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''*__FST_n = __FST_d'''),
r'''*V = ()''', r'''
TypeVarTuple - ROOT 0,0..0,7
  .name 'V'
  .default_value Tuple - 0,5..0,7
    .ctx Load
'''),

('', None, None, None, {'_ver': 13}, ('ParamSpec',
r'''**V = ()'''),
r'''MParamSpec(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''__FST_n'''),
r'''V''',
r'''Name 'V' Load - ROOT 0,0..0,1'''),

('', None, None, None, {'_ver': 13}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''__FST_n = __FST_d'''),
r'''V''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'V'
'''),

('', None, None, None, {'_ver': 13}, ('ParamSpec',
r'''**V'''),
r'''MParamSpec(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''*__FST_n = __FST_d'''),
r'''*V''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'V'
'''),
],

'basic_TypeVarTuple': [  # ................................................................................

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...))''', ('type_param',
r'''__FST_'''),
r'''*U''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'U'
'''),

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...))''', ('type_param',
r'''*__FST_n'''),
r'''*U''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'U'
'''),

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...))''', ('type_param',
r'''*__FST_'''),
r'''**ParseError("expecting identifier, got '*U'")**'''),

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...))''', ('type_param',
r'''**__FST_n'''),
r'''**U''', r'''
ParamSpec - ROOT 0,0..0,3
  .name 'U'
'''),

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...))''', ('type_param',
r'''**__FST_'''),
r'''**ParseError("expecting identifier, got '*U'")**'''),

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...))''', ('type_param',
r'''__FST_n'''),
r'''U''',
r'''Name 'U' Load - ROOT 0,0..0,1'''),

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...))''', ('TypeAlias',
r'''type t[__FST_n] = ...'''),
r'''type t[U] = ...''', r'''
TypeAlias - ROOT 0,0..0,15
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,8
     .name 'U'
  .value Constant Ellipsis - 0,12..0,15
'''),

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...))''', ('TypeAlias',
r'''type t[__FST_] = ...'''),
r'''type t[*U] = ...''', r'''
TypeAlias - ROOT 0,0..0,16
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVarTuple - 0,7..0,9
     .name 'U'
  .value Constant Ellipsis - 0,13..0,16
'''),

('', None, None, None, {'_ver': 13}, ('TypeVarTuple',
r'''*U = ()'''),
r'''MTypeVarTuple(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''__FST_n = __FST_d'''),
r'''U = ()''', r'''
TypeVar - ROOT 0,0..0,6
  .name 'U'
  .default_value Tuple - 0,4..0,6
    .ctx Load
'''),

('', None, None, None, {'_ver': 13}, ('TypeVarTuple',
r'''*U = ()'''),
r'''MTypeVarTuple(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''**__FST_n = __FST_d'''),
r'''**U = ()''', r'''
ParamSpec - ROOT 0,0..0,8
  .name 'U'
  .default_value Tuple - 0,6..0,8
    .ctx Load
'''),

('', None, None, None, {'_ver': 13}, ('TypeVarTuple',
r'''*U = ()'''),
r'''MTypeVarTuple(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''*__FST_n = __FST_d'''),
r'''*U = ()''', r'''
TypeVarTuple - ROOT 0,0..0,7
  .name 'U'
  .default_value Tuple - 0,5..0,7
    .ctx Load
'''),

('', None, None, None, {'_ver': 13}, ('TypeVarTuple',
r'''*U = ()'''),
r'''MTypeVarTuple(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''__FST_n'''),
r'''U''',
r'''Name 'U' Load - ROOT 0,0..0,1'''),

('', None, None, None, {'_ver': 13}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''__FST_n = __FST_d'''),
r'''U''', r'''
TypeVar - ROOT 0,0..0,1
  .name 'U'
'''),

('', None, None, None, {'_ver': 13}, ('TypeVarTuple',
r'''*U'''),
r'''MTypeVarTuple(name=M(n=...), default_value=M(d=...))''', ('type_param',
r'''*__FST_n = __FST_d'''),
r'''*U''', r'''
TypeVarTuple - ROOT 0,0..0,2
  .name 'U'
'''),
],

'basic__Assign_targets': [  # ................................................................................

('', None, None, None, {}, ('_Assign_targets',
r'''a = b = c ='''),
r'''M_Assign_targets(targets=M(t=...))''', ('_Assign_targets',
r'''x = __FST_t = y ='''),
r'''x = a = b = c = y =''', r'''
_Assign_targets - ROOT 0,0..0,19
  .targets[5]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'a' Store - 0,4..0,5
   2] Name 'b' Store - 0,8..0,9
   3] Name 'c' Store - 0,12..0,13
   4] Name 'y' Store - 0,16..0,17
'''),

('', None, None, None, {}, ('_Assign_targets',
r'''a = b = c = d = e ='''),
r'''M_Assign_targets(targets=[..., MQSTAR(t=...), ...])''', ('_Assign_targets',
r'''x = __FST_t = y ='''),
r'''x = b = c = d = y =''', r'''
_Assign_targets - ROOT 0,0..0,19
  .targets[5]
   0] Name 'x' Store - 0,0..0,1
   1] Name 'b' Store - 0,4..0,5
   2] Name 'c' Store - 0,8..0,9
   3] Name 'd' Store - 0,12..0,13
   4] Name 'y' Store - 0,16..0,17
'''),
],

'basic__decorator_list': [  # ................................................................................

('', None, None, None, {}, ('_decorator_list', r'''
@newdeco1
@newdeco2()
@newdeco3
'''),
r'''M_decorator_list(decorator_list=[..., M(deco=...), ...])''', ('_decorator_list', r'''
@x
@__FST_deco
@y
'''), r'''
@x
@newdeco2()
@y
''', r'''
_decorator_list - ROOT 0,0..2,2
  .decorator_list[3]
   0] Name 'x' Load - 0,1..0,2
   1] Call - 1,1..1,11
     .func Name 'newdeco2' Load - 1,1..1,9
   2] Name 'y' Load - 2,1..2,2
'''),

('', None, None, None, {}, ('_decorator_list', r'''
@newdeco1
@newdeco2()
@newdeco4
@newdeco3
'''),
r'''M_decorator_list(decorator_list=[..., MQSTAR(decos=...), ...])''', ('_decorator_list', r'''
@x
@__FST_decos
@y
'''), r'''
@x
@newdeco2()
@newdeco4
@y
''', r'''
_decorator_list - ROOT 0,0..3,2
  .decorator_list[4]
   0] Name 'x' Load - 0,1..0,2
   1] Call - 1,1..1,11
     .func Name 'newdeco2' Load - 1,1..1,9
   2] Name 'newdeco4' Load - 2,1..2,9
   3] Name 'y' Load - 3,1..3,2
'''),
],

'basic__arglikes': [  # ................................................................................

('', None, None, None, {}, ('_arglikes',
r'''a, *b, c=d, **e'''),
r'''M_arglikes(arglikes=M(t=...))''', ('_arglikes',
r'''x, __FST_t, **y'''),
r'''x, a, *b, c=d, **e, **y''', r'''
_arglikes - ROOT 0,0..0,23
  .arglikes[6]
   0] Name 'x' Load - 0,0..0,1
   1] Name 'a' Load - 0,3..0,4
   2] Starred - 0,6..0,8
     .value Name 'b' Load - 0,7..0,8
     .ctx Load
   3] keyword - 0,10..0,13
     .arg 'c'
     .value Name 'd' Load - 0,12..0,13
   4] keyword - 0,15..0,18
     .value Name 'e' Load - 0,17..0,18
   5] keyword - 0,20..0,23
     .value Name 'y' Load - 0,22..0,23
'''),

('', None, None, None, {}, ('_arglikes',
r'''a, *b, c=d, **e'''),
r'''M_arglikes(arglikes=[..., MQSTAR(t=...), ...])''', ('_arglikes',
r'''x, __FST_t, **y'''),
r'''x, *b, c=d, **y''', r'''
_arglikes - ROOT 0,0..0,15
  .arglikes[4]
   0] Name 'x' Load - 0,0..0,1
   1] Starred - 0,3..0,5
     .value Name 'b' Load - 0,4..0,5
     .ctx Load
   2] keyword - 0,7..0,10
     .arg 'c'
     .value Name 'd' Load - 0,9..0,10
   3] keyword - 0,12..0,15
     .value Name 'y' Load - 0,14..0,15
'''),
],

'basic__comprehensions': [  # ................................................................................

('', None, None, None, {}, ('_comprehensions',
r'''for a in b async for c in d if c'''),
r'''M_comprehensions(generators=M(f=...))''', ('_comprehensions',
r'''for __FST_f in "..." for __FST_f in "..."'''),
r'''for a in b async for c in d if c for a in b async for c in d if c''', r'''
_comprehensions - ROOT 0,0..0,65
  .generators[4]
   0] comprehension - 0,0..0,10
     .target Name 'a' Store - 0,4..0,5
     .iter Name 'b' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,32
     .target Name 'c' Store - 0,21..0,22
     .iter Name 'd' Load - 0,26..0,27
     .ifs[1]
      0] Name 'c' Load - 0,31..0,32
     .is_async 1
   2] comprehension - 0,33..0,43
     .target Name 'a' Store - 0,37..0,38
     .iter Name 'b' Load - 0,42..0,43
     .is_async 0
   3] comprehension - 0,44..0,65
     .target Name 'c' Store - 0,54..0,55
     .iter Name 'd' Load - 0,59..0,60
     .ifs[1]
      0] Name 'c' Load - 0,64..0,65
     .is_async 1
'''),

('', None, None, None, {}, ('_comprehensions',
r'''for a in b async for c in d if c for e in f if e if c if a for g in h'''),
r'''M_comprehensions(generators=[..., MQSTAR(f=...), ...])''', ('_comprehensions',
r'''for x in x for __FST_f in '...' for y in y'''),
r'''for x in x async for c in d if c for e in f if e if c if a for y in y''', r'''
_comprehensions - ROOT 0,0..0,69
  .generators[4]
   0] comprehension - 0,0..0,10
     .target Name 'x' Store - 0,4..0,5
     .iter Name 'x' Load - 0,9..0,10
     .is_async 0
   1] comprehension - 0,11..0,32
     .target Name 'c' Store - 0,21..0,22
     .iter Name 'd' Load - 0,26..0,27
     .ifs[1]
      0] Name 'c' Load - 0,31..0,32
     .is_async 1
   2] comprehension - 0,33..0,58
     .target Name 'e' Store - 0,37..0,38
     .iter Name 'f' Load - 0,42..0,43
     .ifs[3]
      0] Name 'e' Load - 0,47..0,48
      1] Name 'c' Load - 0,52..0,53
      2] Name 'a' Load - 0,57..0,58
     .is_async 0
   3] comprehension - 0,59..0,69
     .target Name 'y' Store - 0,63..0,64
     .iter Name 'y' Load - 0,68..0,69
     .is_async 0
'''),
],

'basic__comprehension_ifs': [  # ................................................................................

('', None, None, None, {}, ('_comprehension_ifs',
r'''if c if d'''),
r'''M_comprehension_ifs(ifs=M(f=...))''', ('_comprehension_ifs',
r'''if __FST_f if __FST_f'''),
r'''if c if d if c if d''', r'''
_comprehension_ifs - ROOT 0,0..0,19
  .ifs[4]
   0] Name 'c' Load - 0,3..0,4
   1] Name 'd' Load - 0,8..0,9
   2] Name 'c' Load - 0,13..0,14
   3] Name 'd' Load - 0,18..0,19
'''),

('', None, None, None, {}, ('_comprehension_ifs',
r'''if c if d if e if f if g'''),
r'''M_comprehension_ifs(ifs=[..., MQSTAR(f=...), ...])''', ('_comprehension_ifs',
r'''if x if __FST_f if y'''),
r'''if x if d if e if f if y''', r'''
_comprehension_ifs - ROOT 0,0..0,24
  .ifs[5]
   0] Name 'x' Load - 0,3..0,4
   1] Name 'd' Load - 0,8..0,9
   2] Name 'e' Load - 0,13..0,14
   3] Name 'f' Load - 0,18..0,19
   4] Name 'y' Load - 0,23..0,24
'''),
],

'basic__aliases': [  # ................................................................................

('', None, None, None, {}, ('_aliases',
r'''a, b.c, d as e'''),
r'''M_aliases(names=M(n=...))''', ('_aliases',
r'''x, __FST_n, y'''),
r'''x, a, b.c, d as e, y''', r'''
_aliases - ROOT 0,0..0,20
  .names[5]
   0] alias - 0,0..0,1
     .name 'x'
   1] alias - 0,3..0,4
     .name 'a'
   2] alias - 0,6..0,9
     .name 'b.c'
   3] alias - 0,11..0,17
     .name 'd'
     .asname 'e'
   4] alias - 0,19..0,20
     .name 'y'
'''),

('', None, None, None, {}, ('_aliases',
r'''a, b, c, d, e'''),
r'''M_aliases(names=[..., MQSTAR(i=...), ...])''', ('_aliases',
r'''x, __FST_i, y'''),
r'''x, b, c, d, y''', r'''
_aliases - ROOT 0,0..0,13
  .names[5]
   0] alias - 0,0..0,1
     .name 'x'
   1] alias - 0,3..0,4
     .name 'b'
   2] alias - 0,6..0,7
     .name 'c'
   3] alias - 0,9..0,10
     .name 'd'
   4] alias - 0,12..0,13
     .name 'y'
'''),
],

'basic__withitems': [  # ................................................................................

('', None, None, None, {}, ('_withitems',
r'''a, b, c'''),
r'''M_withitems(items=M(wi=...))''', ('_withitems',
r'''x as x, __FST_wi, y as y'''),
r'''x as x, a, b, c, y as y''', r'''
_withitems - ROOT 0,0..0,23
  .items[5]
   0] withitem - 0,0..0,6
     .context_expr Name 'x' Load - 0,0..0,1
     .optional_vars Name 'x' Store - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,23
     .context_expr Name 'y' Load - 0,17..0,18
     .optional_vars Name 'y' Store - 0,22..0,23
'''),

('', None, None, None, {}, ('_withitems',
r'''a, b, c, d, e'''),
r'''M_withitems(items=[..., MQSTAR(i=...), ...])''', ('_withitems',
r'''x, __FST_i, y'''),
r'''x, b, c, d, y''', r'''
_withitems - ROOT 0,0..0,13
  .items[5]
   0] withitem - 0,0..0,1
     .context_expr Name 'x' Load - 0,0..0,1
   1] withitem - 0,3..0,4
     .context_expr Name 'b' Load - 0,3..0,4
   2] withitem - 0,6..0,7
     .context_expr Name 'c' Load - 0,6..0,7
   3] withitem - 0,9..0,10
     .context_expr Name 'd' Load - 0,9..0,10
   4] withitem - 0,12..0,13
     .context_expr Name 'y' Load - 0,12..0,13
'''),
],

'basic__type_params': [  # ................................................................................

('', None, None, None, {'_ver': 12}, ('_type_params',
r'''T: int, *U, **V'''),
r'''M_type_params(type_params=M(tparams=...))''', ('_type_params',
r'''X: float, __FST_tparams, **Y'''),
r'''X: float, T: int, *U, **V, **Y''', r'''
_type_params - ROOT 0,0..0,30
  .type_params[5]
   0] TypeVar - 0,0..0,8
     .name 'X'
     .bound Name 'float' Load - 0,3..0,8
   1] TypeVar - 0,10..0,16
     .name 'T'
     .bound Name 'int' Load - 0,13..0,16
   2] TypeVarTuple - 0,18..0,20
     .name 'U'
   3] ParamSpec - 0,22..0,25
     .name 'V'
   4] ParamSpec - 0,27..0,30
     .name 'Y'
'''),

('', None, None, None, {'_ver': 12}, ('_type_params',
r'''**A, T: int, *U, **V, B'''),
r'''M_type_params(type_params=[..., MQSTAR(tparams=...), ...])''', ('_type_params',
r'''X: float, __FST_tparams, **Y'''),
r'''X: float, T: int, *U, **V, **Y''', r'''
_type_params - ROOT 0,0..0,30
  .type_params[5]
   0] TypeVar - 0,0..0,8
     .name 'X'
     .bound Name 'float' Load - 0,3..0,8
   1] TypeVar - 0,10..0,16
     .name 'T'
     .bound Name 'int' Load - 0,13..0,16
   2] TypeVarTuple - 0,18..0,20
     .name 'U'
   3] ParamSpec - 0,22..0,25
     .name 'V'
   4] ParamSpec - 0,27..0,30
     .name 'Y'
'''),
],

'Call': [  # ................................................................................

('', None, None, None, {}, ('exec', r'''
logger.info(a, cid=-1)
logger.info(a, cid=1)
other_logger.info(cid=-1, **b)
logger.info(a)
'''), r'''
MCall(
    func=Attribute(M(func=expr), 'info'),
    keywords=[MQSTAR, Mkeyword('cid', MUnaryOp(USub)), MQSTAR],
    _args=M(all_args=...),
)
''', ('Call',
r'''__FST_func.warning(__FST_all_args)'''), r'''
logger.warning(a, cid=-1)
logger.info(a, cid=1)
other_logger.warning(cid=-1, **b)
logger.info(a)
''', r'''
Module - ROOT 0,0..3,14
  .body[4]
   0] Expr - 0,0..0,25
     .value Call - 0,0..0,25
       .func Attribute - 0,0..0,14
         .value Name 'logger' Load - 0,0..0,6
         .attr 'warning'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 0,15..0,16
       .keywords[1]
        0] keyword - 0,18..0,24
          .arg 'cid'
          .value UnaryOp - 0,22..0,24
            .op USub - 0,22..0,23
            .operand Constant 1 - 0,23..0,24
   1] Expr - 1,0..1,21
     .value Call - 1,0..1,21
       .func Attribute - 1,0..1,11
         .value Name 'logger' Load - 1,0..1,6
         .attr 'info'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 1,12..1,13
       .keywords[1]
        0] keyword - 1,15..1,20
          .arg 'cid'
          .value Constant 1 - 1,19..1,20
   2] Expr - 2,0..2,33
     .value Call - 2,0..2,33
       .func Attribute - 2,0..2,20
         .value Name 'other_logger' Load - 2,0..2,12
         .attr 'warning'
         .ctx Load
       .keywords[2]
        0] keyword - 2,21..2,27
          .arg 'cid'
          .value UnaryOp - 2,25..2,27
            .op USub - 2,25..2,26
            .operand Constant 1 - 2,26..2,27
        1] keyword - 2,29..2,32
          .value Name 'b' Load - 2,31..2,32
   3] Expr - 3,0..3,14
     .value Call - 3,0..3,14
       .func Attribute - 3,0..3,11
         .value Name 'logger' Load - 3,0..3,6
         .attr 'info'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 3,12..3,13
'''),

('', None, None, None, {}, ('exec', r'''
logger.info(a, cid=-1)
logger.info(a, cid=1)
other_logger.info(cid=-1, **b)
logger.info(a)
'''), r'''
MCall(
    func=Attribute(M(func=expr), 'info'),
    keywords=[MQSTAR, M(kw=Mkeyword('cid', MUnaryOp(USub))), MQSTAR],
)
''', ('Call',
r'''__FST_func.warning(__FST_kw)'''), r'''
logger.warning(cid=-1)
logger.info(a, cid=1)
other_logger.warning(cid=-1)
logger.info(a)
''', r'''
Module - ROOT 0,0..3,14
  .body[4]
   0] Expr - 0,0..0,22
     .value Call - 0,0..0,22
       .func Attribute - 0,0..0,14
         .value Name 'logger' Load - 0,0..0,6
         .attr 'warning'
         .ctx Load
       .keywords[1]
        0] keyword - 0,15..0,21
          .arg 'cid'
          .value UnaryOp - 0,19..0,21
            .op USub - 0,19..0,20
            .operand Constant 1 - 0,20..0,21
   1] Expr - 1,0..1,21
     .value Call - 1,0..1,21
       .func Attribute - 1,0..1,11
         .value Name 'logger' Load - 1,0..1,6
         .attr 'info'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 1,12..1,13
       .keywords[1]
        0] keyword - 1,15..1,20
          .arg 'cid'
          .value Constant 1 - 1,19..1,20
   2] Expr - 2,0..2,28
     .value Call - 2,0..2,28
       .func Attribute - 2,0..2,20
         .value Name 'other_logger' Load - 2,0..2,12
         .attr 'warning'
         .ctx Load
       .keywords[1]
        0] keyword - 2,21..2,27
          .arg 'cid'
          .value UnaryOp - 2,25..2,27
            .op USub - 2,25..2,26
            .operand Constant 1 - 2,26..2,27
   3] Expr - 3,0..3,14
     .value Call - 3,0..3,14
       .func Attribute - 3,0..3,11
         .value Name 'logger' Load - 3,0..3,6
         .attr 'info'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 3,12..3,13
'''),

('', None, None, None, {}, ('exec', r'''
logger.info(a, cid=-1)
logger.info(a, cid=1)
other_logger.info(cid=-1, **b)
logger.info(a)
'''), r'''
MCall(
    func=Attribute(M(func=expr), 'info'),
    args=[MQSTAR, M(arg='a'), MQSTAR],
)
''', ('Call',
r'''__FST_func.warning(__FST_arg)'''), r'''
logger.warning(a)
logger.warning(a)
other_logger.info(cid=-1, **b)
logger.warning(a)
''', r'''
Module - ROOT 0,0..3,17
  .body[4]
   0] Expr - 0,0..0,17
     .value Call - 0,0..0,17
       .func Attribute - 0,0..0,14
         .value Name 'logger' Load - 0,0..0,6
         .attr 'warning'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 0,15..0,16
   1] Expr - 1,0..1,17
     .value Call - 1,0..1,17
       .func Attribute - 1,0..1,14
         .value Name 'logger' Load - 1,0..1,6
         .attr 'warning'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 1,15..1,16
   2] Expr - 2,0..2,30
     .value Call - 2,0..2,30
       .func Attribute - 2,0..2,17
         .value Name 'other_logger' Load - 2,0..2,12
         .attr 'info'
         .ctx Load
       .keywords[2]
        0] keyword - 2,18..2,24
          .arg 'cid'
          .value UnaryOp - 2,22..2,24
            .op USub - 2,22..2,23
            .operand Constant 1 - 2,23..2,24
        1] keyword - 2,26..2,29
          .value Name 'b' Load - 2,28..2,29
   3] Expr - 3,0..3,17
     .value Call - 3,0..3,17
       .func Attribute - 3,0..3,14
         .value Name 'logger' Load - 3,0..3,6
         .attr 'warning'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 3,15..3,16
'''),

('', None, None, None, {}, ('exec', r'''
logger.info(a, cid=-1)
logger.info(a, cid=1)
other_logger.info(cid=-1, **b)
logger.info(a)
'''), r'''
MCall(
    func=Attribute(M(func=expr), 'info'),
    _args=[MQSTAR, M(arg='a'), MQSTAR],
)
''', ('Call',
r'''__FST_func.warning(__FST_arg)'''), r'''
logger.warning(a)
logger.warning(a)
other_logger.info(cid=-1, **b)
logger.warning(a)
''', r'''
Module - ROOT 0,0..3,17
  .body[4]
   0] Expr - 0,0..0,17
     .value Call - 0,0..0,17
       .func Attribute - 0,0..0,14
         .value Name 'logger' Load - 0,0..0,6
         .attr 'warning'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 0,15..0,16
   1] Expr - 1,0..1,17
     .value Call - 1,0..1,17
       .func Attribute - 1,0..1,14
         .value Name 'logger' Load - 1,0..1,6
         .attr 'warning'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 1,15..1,16
   2] Expr - 2,0..2,30
     .value Call - 2,0..2,30
       .func Attribute - 2,0..2,17
         .value Name 'other_logger' Load - 2,0..2,12
         .attr 'info'
         .ctx Load
       .keywords[2]
        0] keyword - 2,18..2,24
          .arg 'cid'
          .value UnaryOp - 2,22..2,24
            .op USub - 2,22..2,23
            .operand Constant 1 - 2,23..2,24
        1] keyword - 2,26..2,29
          .value Name 'b' Load - 2,28..2,29
   3] Expr - 3,0..3,17
     .value Call - 3,0..3,17
       .func Attribute - 3,0..3,14
         .value Name 'logger' Load - 3,0..3,6
         .attr 'warning'
         .ctx Load
       .args[1]
        0] Name 'a' Load - 3,15..3,16
'''),

('', None, None, None, {'pep8space': False}, ('exec', r'''
class info(a, cid=-1): pass
class info(a, cid=1): pass
class other_info(cid=-1, **b): pass
class info(a): pass
'''), r'''
MClassDef(
    'info',
    keywords=[MQSTAR, Mkeyword('cid', MUnaryOp(USub)), MQSTAR],
    _bases=M(all_bases=...),
)
''', ('ClassDef',
r'''class warning(__FST_all_bases): pass'''), r'''
class warning(a, cid=-1): pass
class info(a, cid=1): pass
class other_info(cid=-1, **b): pass
class info(a): pass
''', r'''
Module - ROOT 0,0..3,19
  .body[4]
   0] ClassDef - 0,0..0,30
     .name 'warning'
     .bases[1]
      0] Name 'a' Load - 0,14..0,15
     .keywords[1]
      0] keyword - 0,17..0,23
        .arg 'cid'
        .value UnaryOp - 0,21..0,23
          .op USub - 0,21..0,22
          .operand Constant 1 - 0,22..0,23
     .body[1]
      0] Pass - 0,26..0,30
   1] ClassDef - 1,0..1,26
     .name 'info'
     .bases[1]
      0] Name 'a' Load - 1,11..1,12
     .keywords[1]
      0] keyword - 1,14..1,19
        .arg 'cid'
        .value Constant 1 - 1,18..1,19
     .body[1]
      0] Pass - 1,22..1,26
   2] ClassDef - 2,0..2,35
     .name 'other_info'
     .keywords[2]
      0] keyword - 2,17..2,23
        .arg 'cid'
        .value UnaryOp - 2,21..2,23
          .op USub - 2,21..2,22
          .operand Constant 1 - 2,22..2,23
      1] keyword - 2,25..2,28
        .value Name 'b' Load - 2,27..2,28
     .body[1]
      0] Pass - 2,31..2,35
   3] ClassDef - 3,0..3,19
     .name 'info'
     .bases[1]
      0] Name 'a' Load - 3,11..3,12
     .body[1]
      0] Pass - 3,15..3,19
'''),
],

'withitem': [  # ................................................................................

('', None, None, None, {}, ('withitem',
r'''a as b'''),
r'''Mwithitem''', ('withitem',
r'''__FST_'''),
r'''a as b''', r'''
withitem - ROOT 0,0..0,6
  .context_expr Name 'a' Load - 0,0..0,1
  .optional_vars Name 'b' Store - 0,5..0,6
'''),

('', None, None, None, {}, ('_withitems',
r'''a as b, c as d'''),
r'''M_withitems''', ('withitem',
r'''__FST_'''),
r'''a as b, c as d''', r'''
_withitems - ROOT 0,0..0,14
  .items[2]
   0] withitem - 0,0..0,6
     .context_expr Name 'a' Load - 0,0..0,1
     .optional_vars Name 'b' Store - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'c' Load - 0,8..0,9
     .optional_vars Name 'd' Store - 0,13..0,14
'''),

('', None, None, None, {}, ('withitem',
r'''a as b'''),
r'''Mwithitem''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a as b, z: pass''', r'''
With - ROOT 0,0..0,23
  .items[3]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'a' Load - 0,8..0,9
     .optional_vars Name 'b' Store - 0,13..0,14
   2] withitem - 0,16..0,17
     .context_expr Name 'z' Load - 0,16..0,17
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', None, None, None, {}, ('_withitems',
r'''a as b, c as d'''),
r'''M_withitems''', ('With',
r'''with __FST_: pass'''),
r'''with a as b, c as d: pass''', r'''
With - ROOT 0,0..0,25
  .items[2]
   0] withitem - 0,5..0,11
     .context_expr Name 'a' Load - 0,5..0,6
     .optional_vars Name 'b' Store - 0,10..0,11
   1] withitem - 0,13..0,19
     .context_expr Name 'c' Load - 0,13..0,14
     .optional_vars Name 'd' Store - 0,18..0,19
  .body[1]
   0] Pass - 0,21..0,25
'''),

('', None, None, None, {}, ('_withitems',
r'''a as b, c as d'''),
r'''M_withitems''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a as b, c as d, z: pass''', r'''
With - ROOT 0,0..0,31
  .items[4]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,14
     .context_expr Name 'a' Load - 0,8..0,9
     .optional_vars Name 'b' Store - 0,13..0,14
   2] withitem - 0,16..0,22
     .context_expr Name 'c' Load - 0,16..0,17
     .optional_vars Name 'd' Store - 0,21..0,22
   3] withitem - 0,24..0,25
     .context_expr Name 'z' Load - 0,24..0,25
  .body[1]
   0] Pass - 0,27..0,31
'''),

('', None, None, None, {}, ('Set',
r'''{a, b, c}'''),
r'''MSet''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c]'''),
r'''MList''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('Tuple',
r'''(a, b, c)'''),
r'''MTuple''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('MatchSequence',
r'''[a, b, c]'''),
r'''MMatchSequence''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('_Assign_targets',
r'''a = b = c ='''),
r'''M_Assign_targets''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('_decorator_list', r'''
@a
@b
@c
'''),
r'''M_decorator_list''', ('With',
r'''with x, __FST_, z: pass'''), r'''
with (x, a,
     b,
     c, z): pass
''', r'''
With - ROOT 0,0..2,16
  .items[5]
   0] withitem - 0,6..0,7
     .context_expr Name 'x' Load - 0,6..0,7
   1] withitem - 0,9..0,10
     .context_expr Name 'a' Load - 0,9..0,10
   2] withitem - 1,5..1,6
     .context_expr Name 'b' Load - 1,5..1,6
   3] withitem - 2,5..2,6
     .context_expr Name 'c' Load - 2,5..2,6
   4] withitem - 2,8..2,9
     .context_expr Name 'z' Load - 2,8..2,9
  .body[1]
   0] Pass - 2,12..2,16
'''),

('', None, None, None, {}, ('_arglikes',
r'''a, b, c'''),
r'''M_arglikes''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('_comprehension_ifs',
r'''if a if b if c'''),
r'''M_comprehension_ifs''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('_aliases',
r'''a, b, c'''),
r'''M_aliases''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {'_ver': 12}, ('_type_params',
r'''a, b, c'''),
r'''M_type_params''', ('With',
r'''with x, __FST_, z: pass'''),
r'''with x, a, b, c, z: pass''', r'''
With - ROOT 0,0..0,24
  .items[5]
   0] withitem - 0,5..0,6
     .context_expr Name 'x' Load - 0,5..0,6
   1] withitem - 0,8..0,9
     .context_expr Name 'a' Load - 0,8..0,9
   2] withitem - 0,11..0,12
     .context_expr Name 'b' Load - 0,11..0,12
   3] withitem - 0,14..0,15
     .context_expr Name 'c' Load - 0,14..0,15
   4] withitem - 0,17..0,18
     .context_expr Name 'z' Load - 0,17..0,18
  .body[1]
   0] Pass - 0,20..0,24
'''),
],

'stmts': [  # ................................................................................

('', None, None, None, {}, (None,
r'''if something(): pass'''),
r'''MIf(test=M(test=...), body=M(body=...))''',
r'''while __FST_test: __FST_body''', r'''
while something():
    pass
''', r'''
While - ROOT 0,0..1,8
  .test Call - 0,6..0,17
    .func Name 'something' Load - 0,6..0,15
  .body[1]
   0] Pass - 1,4..1,8
'''),

('', None, None, None, {}, (None,
r'''if something(): this(); that()'''),
r'''MIf(test=M(test=...), body=M(body=...))''',
r'''while __FST_test: __FST_body''', r'''
while something():
    this(); that()
''', r'''
While - ROOT 0,0..1,18
  .test Call - 0,6..0,17
    .func Name 'something' Load - 0,6..0,15
  .body[2]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'this' Load - 1,4..1,8
   1] Expr - 1,12..1,18
     .value Call - 1,12..1,18
       .func Name 'that' Load - 1,12..1,16
'''),

('', None, None, None, {}, (None, r'''
if something():
  this()
  that()
'''),
r'''MIf(test=M(test=...), body=M(body=...))''',
r'''while __FST_test: __FST_body''', r'''
while something():
    this()
    that()
''', r'''
While - ROOT 0,0..2,10
  .test Call - 0,6..0,17
    .func Name 'something' Load - 0,6..0,15
  .body[2]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'this' Load - 1,4..1,8
   1] Expr - 2,4..2,10
     .value Call - 2,4..2,10
       .func Name 'that' Load - 2,4..2,8
'''),

('', None, None, None, {}, (None, r'''
if something():
  this()
  that()
  the_other()
'''),
r'''MIf(test=M(test=...), body=[MQSTAR, M(that=MExpr(MCall('that'))), MQSTAR])''',
r'''while __FST_test: __FST_that''', r'''
while something():
    that()
''', r'''
While - ROOT 0,0..1,10
  .test Call - 0,6..0,17
    .func Name 'something' Load - 0,6..0,15
  .body[1]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'that' Load - 1,4..1,8
'''),

('', None, None, None, {}, (None, r'''
if something():
  this()
  that()
  the_other()
'''),
r'''MIf(test=M(test=...), body=[MQSTAR, M(that=MExpr(MCall('that'))), MQSTAR])''', r'''
while __FST_test:
    __FST_that
''', r'''
while something():
    that()
''', r'''
While - ROOT 0,0..1,10
  .test Call - 0,6..0,17
    .func Name 'something' Load - 0,6..0,15
  .body[1]
   0] Expr - 1,4..1,10
     .value Call - 1,4..1,10
       .func Name 'that' Load - 1,4..1,8
'''),

('', None, None, None, {}, (None, r'''
if a:
    call()
if c := b():
    while c:
        c = c()
if not d:
    e ; f
    g
'''),
r'''MIf(test=M(test=...), body=M(body=...))''', r'''
if not __FST_test:
    __FST_body
''', r'''
if not a:
    call()
if not (c := b()):
    while c:
        c = c()
if not not d:
    e ; f
    g
''', r'''
Module - ROOT 0,0..7,5
  .body[3]
   0] If - 0,0..1,10
     .test UnaryOp - 0,3..0,8
       .op Not - 0,3..0,6
       .operand Name 'a' Load - 0,7..0,8
     .body[1]
      0] Expr - 1,4..1,10
        .value Call - 1,4..1,10
          .func Name 'call' Load - 1,4..1,8
   1] If - 2,0..4,15
     .test UnaryOp - 2,3..2,17
       .op Not - 2,3..2,6
       .operand NamedExpr - 2,8..2,16
         .target Name 'c' Store - 2,8..2,9
         .value Call - 2,13..2,16
           .func Name 'b' Load - 2,13..2,14
     .body[1]
      0] While - 3,4..4,15
        .test Name 'c' Load - 3,10..3,11
        .body[1]
         0] Assign - 4,8..4,15
           .targets[1]
            0] Name 'c' Store - 4,8..4,9
           .value Call - 4,12..4,15
             .func Name 'c' Load - 4,12..4,13
   2] If - 5,0..7,5
     .test UnaryOp - 5,3..5,12
       .op Not - 5,3..5,6
       .operand UnaryOp - 5,7..5,12
         .op Not - 5,7..5,10
         .operand Name 'd' Load - 5,11..5,12
     .body[3]
      0] Expr - 6,4..6,5
        .value Name 'e' Load - 6,4..6,5
      1] Expr - 6,8..6,9
        .value Name 'f' Load - 6,8..6,9
      2] Expr - 7,4..7,5
        .value Name 'g' Load - 7,4..7,5
'''),
],

'downgrade_slice_to_one': [  # ................................................................................

('', None, None, None, {}, ('List',
r'''[a, b, c, d, e]'''),
r'''MList(elts=[..., MQSTAR(a=...), ...])''', ('Assign',
r'''i = __FST_a'''),
r'''i = [b, c, d]''', r'''
Assign - ROOT 0,0..0,13
  .targets[1]
   0] Name 'i' Store - 0,0..0,1
  .value List - 0,4..0,13
    .elts[3]
     0] Name 'b' Load - 0,5..0,6
     1] Name 'c' Load - 0,8..0,9
     2] Name 'd' Load - 0,11..0,12
    .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, b, c, d, e]'''),
r'''MList(elts=[..., MQSTAR(a=...), ...])''', ('Assign',
r'''i = __FSS_a'''),
r'''**ValueError('cannot replace Assign.value with slice')**'''),
],

'nested': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a + b.c + d[e]'''),
r'''MOR(Name, Attribute, Subscript)''',
r'''log(__FST_)''',
r'''log(a) + log(b.c) + log(d[e])''', r'''
BinOp - ROOT 0,0..0,29
  .left BinOp - 0,0..0,17
    .left Call - 0,0..0,6
      .func Name 'log' Load - 0,0..0,3
      .args[1]
       0] Name 'a' Load - 0,4..0,5
    .op Add - 0,7..0,8
    .right Call - 0,9..0,17
      .func Name 'log' Load - 0,9..0,12
      .args[1]
       0] Attribute - 0,13..0,16
         .value Name 'b' Load - 0,13..0,14
         .attr 'c'
         .ctx Load
  .op Add - 0,18..0,19
  .right Call - 0,20..0,29
    .func Name 'log' Load - 0,20..0,23
    .args[1]
     0] Subscript - 0,24..0,28
       .value Name 'd' Load - 0,24..0,25
       .slice Name 'e' Load - 0,26..0,27
       .ctx Load
'''),

('', None, None, None, {}, (None,
r'''a + b.c + d[e]'''),
r'''M(top=MOR(Name, Attribute, Subscript))''',
r'''log(__FST_top)''',
r'''log(a) + log(b.c) + log(d[e])''', r'''
BinOp - ROOT 0,0..0,29
  .left BinOp - 0,0..0,17
    .left Call - 0,0..0,6
      .func Name 'log' Load - 0,0..0,3
      .args[1]
       0] Name 'a' Load - 0,4..0,5
    .op Add - 0,7..0,8
    .right Call - 0,9..0,17
      .func Name 'log' Load - 0,9..0,12
      .args[1]
       0] Attribute - 0,13..0,16
         .value Name 'b' Load - 0,13..0,14
         .attr 'c'
         .ctx Load
  .op Add - 0,18..0,19
  .right Call - 0,20..0,29
    .func Name 'log' Load - 0,20..0,23
    .args[1]
     0] Subscript - 0,24..0,28
       .value Name 'd' Load - 0,24..0,25
       .slice Name 'e' Load - 0,26..0,27
       .ctx Load
'''),

('', None, None, None, {'nested': True}, (None,
r'''a + b.c + d[e]'''),
r'''MOR(Name, Attribute, Subscript)''',
r'''log(__FST_)''',
r'''log(a) + log(log(b).c) + log(log(d)[log(e)])''', r'''
BinOp - ROOT 0,0..0,44
  .left BinOp - 0,0..0,22
    .left Call - 0,0..0,6
      .func Name 'log' Load - 0,0..0,3
      .args[1]
       0] Name 'a' Load - 0,4..0,5
    .op Add - 0,7..0,8
    .right Call - 0,9..0,22
      .func Name 'log' Load - 0,9..0,12
      .args[1]
       0] Attribute - 0,13..0,21
         .value Call - 0,13..0,19
           .func Name 'log' Load - 0,13..0,16
           .args[1]
            0] Name 'b' Load - 0,17..0,18
         .attr 'c'
         .ctx Load
  .op Add - 0,23..0,24
  .right Call - 0,25..0,44
    .func Name 'log' Load - 0,25..0,28
    .args[1]
     0] Subscript - 0,29..0,43
       .value Call - 0,29..0,35
         .func Name 'log' Load - 0,29..0,32
         .args[1]
          0] Name 'd' Load - 0,33..0,34
       .slice Call - 0,36..0,42
         .func Name 'log' Load - 0,36..0,39
         .args[1]
          0] Name 'e' Load - 0,40..0,41
       .ctx Load
'''),

('', None, None, None, {'nested': True}, (None,
r'''a + b.c + d[e]'''),
r'''M(top=MOR(Name, Attribute, Subscript))''',
r'''log(__FST_top)''',
r'''log(a) + log(log(b).c) + log(log(d)[log(e)])''', r'''
BinOp - ROOT 0,0..0,44
  .left BinOp - 0,0..0,22
    .left Call - 0,0..0,6
      .func Name 'log' Load - 0,0..0,3
      .args[1]
       0] Name 'a' Load - 0,4..0,5
    .op Add - 0,7..0,8
    .right Call - 0,9..0,22
      .func Name 'log' Load - 0,9..0,12
      .args[1]
       0] Attribute - 0,13..0,21
         .value Call - 0,13..0,19
           .func Name 'log' Load - 0,13..0,16
           .args[1]
            0] Name 'b' Load - 0,17..0,18
         .attr 'c'
         .ctx Load
  .op Add - 0,23..0,24
  .right Call - 0,25..0,44
    .func Name 'log' Load - 0,25..0,28
    .args[1]
     0] Subscript - 0,29..0,43
       .value Call - 0,29..0,35
         .func Name 'log' Load - 0,29..0,32
         .args[1]
          0] Name 'd' Load - 0,33..0,34
       .slice Call - 0,36..0,42
         .func Name 'log' Load - 0,36..0,39
         .args[1]
          0] Name 'e' Load - 0,40..0,41
       .ctx Load
'''),

('', None, None, None, {}, (None,
r'''a + (b + c)'''),
r'''MBinOp(M(a=...), ..., M(b=...))''',
r'''(BinOp(__FST_a, __FST_b), __FST_)[1]''',
r'''(BinOp(a, b + c), a + (b + c))[1]''', r'''
Subscript - ROOT 0,0..0,33
  .value Tuple - 0,0..0,30
    .elts[2]
     0] Call - 0,1..0,16
       .func Name 'BinOp' Load - 0,1..0,6
       .args[2]
        0] Name 'a' Load - 0,7..0,8
        1] BinOp - 0,10..0,15
          .left Name 'b' Load - 0,10..0,11
          .op Add - 0,12..0,13
          .right Name 'c' Load - 0,14..0,15
     1] BinOp - 0,18..0,29
       .left Name 'a' Load - 0,18..0,19
       .op Add - 0,20..0,21
       .right BinOp - 0,23..0,28
         .left Name 'b' Load - 0,23..0,24
         .op Add - 0,25..0,26
         .right Name 'c' Load - 0,27..0,28
    .ctx Load
  .slice Constant 1 - 0,31..0,32
  .ctx Load
'''),

('', None, None, None, {}, (None,
r'''a + (b + c)'''),
r'''M(top=MBinOp(M(a=...), ..., M(b=...)))''',
r'''(BinOp(__FST_a, __FST_b), __FST_top)[1]''',
r'''(BinOp(a, b + c), a + (b + c))[1]''', r'''
Subscript - ROOT 0,0..0,33
  .value Tuple - 0,0..0,30
    .elts[2]
     0] Call - 0,1..0,16
       .func Name 'BinOp' Load - 0,1..0,6
       .args[2]
        0] Name 'a' Load - 0,7..0,8
        1] BinOp - 0,10..0,15
          .left Name 'b' Load - 0,10..0,11
          .op Add - 0,12..0,13
          .right Name 'c' Load - 0,14..0,15
     1] BinOp - 0,18..0,29
       .left Name 'a' Load - 0,18..0,19
       .op Add - 0,20..0,21
       .right BinOp - 0,23..0,28
         .left Name 'b' Load - 0,23..0,24
         .op Add - 0,25..0,26
         .right Name 'c' Load - 0,27..0,28
    .ctx Load
  .slice Constant 1 - 0,31..0,32
  .ctx Load
'''),

('', None, None, None, {'nested': True}, (None,
r'''a + (b + c)'''),
r'''MBinOp(M(a=...), ..., M(b=...))''',
r'''(BinOp(__FST_a, __FST_b), __FST_)[1]''',
r'''(BinOp(a, (BinOp(b, c), b + c)[1]), a + (BinOp(b, c), b + c)[1])[1]''', r'''
Subscript - ROOT 0,0..0,67
  .value Tuple - 0,0..0,64
    .elts[2]
     0] Call - 0,1..0,34
       .func Name 'BinOp' Load - 0,1..0,6
       .args[2]
        0] Name 'a' Load - 0,7..0,8
        1] Subscript - 0,10..0,33
          .value Tuple - 0,10..0,30
            .elts[2]
             0] Call - 0,11..0,22
               .func Name 'BinOp' Load - 0,11..0,16
               .args[2]
                0] Name 'b' Load - 0,17..0,18
                1] Name 'c' Load - 0,20..0,21
             1] BinOp - 0,24..0,29
               .left Name 'b' Load - 0,24..0,25
               .op Add - 0,26..0,27
               .right Name 'c' Load - 0,28..0,29
            .ctx Load
          .slice Constant 1 - 0,31..0,32
          .ctx Load
     1] BinOp - 0,36..0,63
       .left Name 'a' Load - 0,36..0,37
       .op Add - 0,38..0,39
       .right Subscript - 0,40..0,63
         .value Tuple - 0,40..0,60
           .elts[2]
            0] Call - 0,41..0,52
              .func Name 'BinOp' Load - 0,41..0,46
              .args[2]
               0] Name 'b' Load - 0,47..0,48
               1] Name 'c' Load - 0,50..0,51
            1] BinOp - 0,54..0,59
              .left Name 'b' Load - 0,54..0,55
              .op Add - 0,56..0,57
              .right Name 'c' Load - 0,58..0,59
           .ctx Load
         .slice Constant 1 - 0,61..0,62
         .ctx Load
    .ctx Load
  .slice Constant 1 - 0,65..0,66
  .ctx Load
'''),

('', None, None, None, {'nested': True}, (None,
r'''a + (b + c)'''),
r'''M(top=MBinOp(M(a=...), ..., M(b=...)))''',
r'''(BinOp(__FST_a, __FST_b), __FST_top)[1]''',
r'''(BinOp(a, (BinOp(b, c), b + c)[1]), a + (BinOp(b, c), b + c)[1])[1]''', r'''
Subscript - ROOT 0,0..0,67
  .value Tuple - 0,0..0,64
    .elts[2]
     0] Call - 0,1..0,34
       .func Name 'BinOp' Load - 0,1..0,6
       .args[2]
        0] Name 'a' Load - 0,7..0,8
        1] Subscript - 0,10..0,33
          .value Tuple - 0,10..0,30
            .elts[2]
             0] Call - 0,11..0,22
               .func Name 'BinOp' Load - 0,11..0,16
               .args[2]
                0] Name 'b' Load - 0,17..0,18
                1] Name 'c' Load - 0,20..0,21
             1] BinOp - 0,24..0,29
               .left Name 'b' Load - 0,24..0,25
               .op Add - 0,26..0,27
               .right Name 'c' Load - 0,28..0,29
            .ctx Load
          .slice Constant 1 - 0,31..0,32
          .ctx Load
     1] BinOp - 0,36..0,63
       .left Name 'a' Load - 0,36..0,37
       .op Add - 0,38..0,39
       .right Subscript - 0,40..0,63
         .value Tuple - 0,40..0,60
           .elts[2]
            0] Call - 0,41..0,52
              .func Name 'BinOp' Load - 0,41..0,46
              .args[2]
               0] Name 'b' Load - 0,47..0,48
               1] Name 'c' Load - 0,50..0,51
            1] BinOp - 0,54..0,59
              .left Name 'b' Load - 0,54..0,55
              .op Add - 0,56..0,57
              .right Name 'c' Load - 0,58..0,59
           .ctx Load
         .slice Constant 1 - 0,61..0,62
         .ctx Load
    .ctx Load
  .slice Constant 1 - 0,65..0,66
  .ctx Load
'''),
],

'count': [  # ................................................................................

('', None, None, None, {}, (None,
r'''a, a, a'''),
r'''Name''',
r'''b''',
r'''b, b, b''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'b' Load - 0,6..0,7
  .ctx Load
'''),

('', None, None, None, {'count': 2}, (None,
r'''a, a, a'''),
r'''Name''',
r'''b''',
r'''b, b, a''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'a' Load - 0,6..0,7
  .ctx Load
'''),

('', None, None, None, {'count': 1}, (None,
r'''a, a, a'''),
r'''Name''',
r'''b''',
r'''b, a, a''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'a' Load - 0,3..0,4
   2] Name 'a' Load - 0,6..0,7
  .ctx Load
'''),

('', None, None, None, {'count': 0}, (None,
r'''a, a, a'''),
r'''Name''',
r'''b''',
r'''b, b, b''', r'''
Tuple - ROOT 0,0..0,7
  .elts[3]
   0] Name 'b' Load - 0,0..0,1
   1] Name 'b' Load - 0,3..0,4
   2] Name 'b' Load - 0,6..0,7
  .ctx Load
'''),
],

'loop': [  # ................................................................................

('', None, None, None, {}, (None,
r'''[a, b, c, d, e]'''),
r'''MList(elts=[M(a=...), M(b=...), MQSTAR(tail=...)])''',
r'''[__FST_a + __FST_b, __FST_tail]''',
r'''[a + b, c, d, e]''', r'''
List - ROOT 0,0..0,16
  .elts[4]
   0] BinOp - 0,1..0,6
     .left Name 'a' Load - 0,1..0,2
     .op Add - 0,3..0,4
     .right Name 'b' Load - 0,5..0,6
   1] Name 'c' Load - 0,8..0,9
   2] Name 'd' Load - 0,11..0,12
   3] Name 'e' Load - 0,14..0,15
  .ctx Load
'''),

('', None, None, None, {'loop': 1}, (None,
r'''[a, b, c, d, e]'''),
r'''MList(elts=[M(a=...), M(b=...), MQSTAR(tail=...)])''',
r'''[__FST_a + __FST_b, __FST_tail]''',
r'''[a + b, c, d, e]''', r'''
List - ROOT 0,0..0,16
  .elts[4]
   0] BinOp - 0,1..0,6
     .left Name 'a' Load - 0,1..0,2
     .op Add - 0,3..0,4
     .right Name 'b' Load - 0,5..0,6
   1] Name 'c' Load - 0,8..0,9
   2] Name 'd' Load - 0,11..0,12
   3] Name 'e' Load - 0,14..0,15
  .ctx Load
'''),

('', None, None, None, {'loop': 2}, (None,
r'''[a, b, c, d, e]'''),
r'''MList(elts=[M(a=...), M(b=...), MQSTAR(tail=...)])''',
r'''[__FST_a + __FST_b, __FST_tail]''',
r'''[a + b + c, d, e]''', r'''
List - ROOT 0,0..0,17
  .elts[3]
   0] BinOp - 0,1..0,10
     .left BinOp - 0,1..0,6
       .left Name 'a' Load - 0,1..0,2
       .op Add - 0,3..0,4
       .right Name 'b' Load - 0,5..0,6
     .op Add - 0,7..0,8
     .right Name 'c' Load - 0,9..0,10
   1] Name 'd' Load - 0,12..0,13
   2] Name 'e' Load - 0,15..0,16
  .ctx Load
'''),

('', None, None, None, {'loop': 0}, (None,
r'''[a, b, c, d, e]'''),
r'''MList(elts=[M(a=...), M(b=...), MQSTAR(tail=...)])''',
r'''[__FST_a + __FST_b, __FST_tail]''',
r'''[a + b + c + d + e]''', r'''
List - ROOT 0,0..0,19
  .elts[1]
   0] BinOp - 0,1..0,18
     .left BinOp - 0,1..0,14
       .left BinOp - 0,1..0,10
         .left BinOp - 0,1..0,6
           .left Name 'a' Load - 0,1..0,2
           .op Add - 0,3..0,4
           .right Name 'b' Load - 0,5..0,6
         .op Add - 0,7..0,8
         .right Name 'c' Load - 0,9..0,10
       .op Add - 0,11..0,12
       .right Name 'd' Load - 0,13..0,14
     .op Add - 0,15..0,16
     .right Name 'e' Load - 0,17..0,18
  .ctx Load
'''),

('', None, None, None, {'loop': True}, (None,
r'''[a, b, c, d, e]'''),
r'''MList(elts=[M(a=...), M(b=...), MQSTAR(tail=...)])''',
r'''[__FST_a + __FST_b, __FST_tail]''',
r'''[a + b + c + d + e]''', r'''
List - ROOT 0,0..0,19
  .elts[1]
   0] BinOp - 0,1..0,18
     .left BinOp - 0,1..0,14
       .left BinOp - 0,1..0,10
         .left BinOp - 0,1..0,6
           .left Name 'a' Load - 0,1..0,2
           .op Add - 0,3..0,4
           .right Name 'b' Load - 0,5..0,6
         .op Add - 0,7..0,8
         .right Name 'c' Load - 0,9..0,10
       .op Add - 0,11..0,12
       .right Name 'd' Load - 0,13..0,14
     .op Add - 0,15..0,16
     .right Name 'e' Load - 0,17..0,18
  .ctx Load
'''),

('', None, None, None, {}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b:
    if c:
        if d:
            if e:
                pass
''', r'''
If - ROOT 0,0..4,20
  .test BoolOp - 0,3..0,10
    .op And
    .values[2]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
  .body[1]
   0] If - 1,4..4,20
     .test Name 'c' Load - 1,7..1,8
     .body[1]
      0] If - 2,8..4,20
        .test Name 'd' Load - 2,11..2,12
        .body[1]
         0] If - 3,12..4,20
           .test Name 'e' Load - 3,15..3,16
           .body[1]
            0] Pass - 4,16..4,20
'''),

('', None, None, None, {'loop': 1}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b:
    if c:
        if d:
            if e:
                pass
''', r'''
If - ROOT 0,0..4,20
  .test BoolOp - 0,3..0,10
    .op And
    .values[2]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
  .body[1]
   0] If - 1,4..4,20
     .test Name 'c' Load - 1,7..1,8
     .body[1]
      0] If - 2,8..4,20
        .test Name 'd' Load - 2,11..2,12
        .body[1]
         0] If - 3,12..4,20
           .test Name 'e' Load - 3,15..3,16
           .body[1]
            0] Pass - 4,16..4,20
'''),

('', None, None, None, {'loop': 1, 'nested': True}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b:
    if c and d:
        if e:
            pass
''', r'''
If - ROOT 0,0..3,16
  .test BoolOp - 0,3..0,10
    .op And
    .values[2]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
  .body[1]
   0] If - 1,4..3,16
     .test BoolOp - 1,7..1,14
       .op And
       .values[2]
        0] Name 'c' Load - 1,7..1,8
        1] Name 'd' Load - 1,13..1,14
     .body[1]
      0] If - 2,8..3,16
        .test Name 'e' Load - 2,11..2,12
        .body[1]
         0] Pass - 3,12..3,16
'''),

('', None, None, None, {'loop': 2}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c:
    if d:
        if e:
            pass
''', r'''
If - ROOT 0,0..3,16
  .test BoolOp - 0,3..0,16
    .op And
    .values[3]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
  .body[1]
   0] If - 1,4..3,16
     .test Name 'd' Load - 1,7..1,8
     .body[1]
      0] If - 2,8..3,16
        .test Name 'e' Load - 2,11..2,12
        .body[1]
         0] Pass - 3,12..3,16
'''),

('', None, None, None, {'loop': 2, 'nested': True}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c:
    if d and e:
        pass
''', r'''
If - ROOT 0,0..2,12
  .test BoolOp - 0,3..0,16
    .op And
    .values[3]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
  .body[1]
   0] If - 1,4..2,12
     .test BoolOp - 1,7..1,14
       .op And
       .values[2]
        0] Name 'd' Load - 1,7..1,8
        1] Name 'e' Load - 1,13..1,14
     .body[1]
      0] Pass - 2,8..2,12
'''),

('', None, None, None, {'loop': 3}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c and d:
    if e:
        pass
''', r'''
If - ROOT 0,0..2,12
  .test BoolOp - 0,3..0,22
    .op And
    .values[4]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
     3] Name 'd' Load - 0,21..0,22
  .body[1]
   0] If - 1,4..2,12
     .test Name 'e' Load - 1,7..1,8
     .body[1]
      0] Pass - 2,8..2,12
'''),

('', None, None, None, {'loop': 4}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c and d and e:
    pass
''', r'''
If - ROOT 0,0..1,8
  .test BoolOp - 0,3..0,28
    .op And
    .values[5]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
     3] Name 'd' Load - 0,21..0,22
     4] Name 'e' Load - 0,27..0,28
  .body[1]
   0] Pass - 1,4..1,8
'''),

('', None, None, None, {'loop': 5}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c and d and e:
    pass
''', r'''
If - ROOT 0,0..1,8
  .test BoolOp - 0,3..0,28
    .op And
    .values[5]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
     3] Name 'd' Load - 0,21..0,22
     4] Name 'e' Load - 0,27..0,28
  .body[1]
   0] Pass - 1,4..1,8
'''),

('', None, None, None, {'nested': True, 'count': 2}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    if f:
                        pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b:
    if c and d:
        if e:
            if f:
                pass
''', r'''
If - ROOT 0,0..4,20
  .test BoolOp - 0,3..0,10
    .op And
    .values[2]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
  .body[1]
   0] If - 1,4..4,20
     .test BoolOp - 1,7..1,14
       .op And
       .values[2]
        0] Name 'c' Load - 1,7..1,8
        1] Name 'd' Load - 1,13..1,14
     .body[1]
      0] If - 2,8..4,20
        .test Name 'e' Load - 2,11..2,12
        .body[1]
         0] If - 3,12..4,20
           .test Name 'f' Load - 3,15..3,16
           .body[1]
            0] Pass - 4,16..4,20
'''),

('', None, None, None, {'nested': True, 'count': 2, 'loop': 2}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c:
    if d and e:
        pass
''', r'''
If - ROOT 0,0..2,12
  .test BoolOp - 0,3..0,16
    .op And
    .values[3]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
  .body[1]
   0] If - 1,4..2,12
     .test BoolOp - 1,7..1,14
       .op And
       .values[2]
        0] Name 'd' Load - 1,7..1,8
        1] Name 'e' Load - 1,13..1,14
     .body[1]
      0] Pass - 2,8..2,12
'''),

('', None, None, None, {'nested': True, 'count': 2, 'loop': 2}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    if f:
                        if g:
                            pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c:
    if d and e and f:
        if g:
            pass
''', r'''
If - ROOT 0,0..3,16
  .test BoolOp - 0,3..0,16
    .op And
    .values[3]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
  .body[1]
   0] If - 1,4..3,16
     .test BoolOp - 1,7..1,20
       .op And
       .values[3]
        0] Name 'd' Load - 1,7..1,8
        1] Name 'e' Load - 1,13..1,14
        2] Name 'f' Load - 1,19..1,20
     .body[1]
      0] If - 2,8..3,16
        .test Name 'g' Load - 2,11..2,12
        .body[1]
         0] Pass - 3,12..3,16
'''),

('', None, None, None, {'nested': True, 'count': 2, 'loop': 3}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    if f:
                        if g:
                            pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c and d:
    if e and f and g:
        pass
''', r'''
If - ROOT 0,0..2,12
  .test BoolOp - 0,3..0,22
    .op And
    .values[4]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
     3] Name 'd' Load - 0,21..0,22
  .body[1]
   0] If - 1,4..2,12
     .test BoolOp - 1,7..1,20
       .op And
       .values[3]
        0] Name 'e' Load - 1,7..1,8
        1] Name 'f' Load - 1,13..1,14
        2] Name 'g' Load - 1,19..1,20
     .body[1]
      0] Pass - 2,8..2,12
'''),

('', None, None, None, {'nested': True, 'count': 2, 'loop': 4}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    if f:
                        if g:
                            pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FST_outt and __FST_int:
    __FST_inb
''', r'''
if a and b and c and d and e:
    if f and g:
        pass
''', r'''
If - ROOT 0,0..2,12
  .test BoolOp - 0,3..0,28
    .op And
    .values[5]
     0] Name 'a' Load - 0,3..0,4
     1] Name 'b' Load - 0,9..0,10
     2] Name 'c' Load - 0,15..0,16
     3] Name 'd' Load - 0,21..0,22
     4] Name 'e' Load - 0,27..0,28
  .body[1]
   0] If - 1,4..2,12
     .test BoolOp - 1,7..1,14
       .op And
       .values[2]
        0] Name 'f' Load - 1,7..1,8
        1] Name 'g' Load - 1,13..1,14
     .body[1]
      0] Pass - 2,8..2,12
'''),

('', None, None, None, {'nested': True, 'count': 2, 'loop': 4}, (None, r'''
if a:
    if b:
        if c:
            if d:
                if e:
                    if f:
                        if g:
                            pass
'''),
r'''MIf(test=M(outt=...), body=[MIf(test=M(int=...), body=M(inb=...))])''', r'''
if __FSO_outt and __FST_int:
    __FST_inb
''', r'''
if (((a and b) and c) and d) and e:
    if f and g:
        pass
''', r'''
If - ROOT 0,0..2,12
  .test BoolOp - 0,3..0,34
    .op And
    .values[2]
     0] BoolOp - 0,4..0,27
       .op And
       .values[2]
        0] BoolOp - 0,5..0,20
          .op And
          .values[2]
           0] BoolOp - 0,6..0,13
             .op And
             .values[2]
              0] Name 'a' Load - 0,6..0,7
              1] Name 'b' Load - 0,12..0,13
           1] Name 'c' Load - 0,19..0,20
        1] Name 'd' Load - 0,26..0,27
     1] Name 'e' Load - 0,33..0,34
  .body[1]
   0] If - 1,4..2,12
     .test BoolOp - 1,7..1,14
       .op And
       .values[2]
        0] Name 'f' Load - 1,7..1,8
        1] Name 'g' Load - 1,13..1,14
     .body[1]
      0] Pass - 2,8..2,12
'''),
],

'identifier': [  # ................................................................................

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''',
r'''def __FST_name(): pass''',
r'''def SUB(): pass''', r'''
FunctionDef - ROOT 0,0..0,15
  .name 'SUB'
  .body[1]
   0] Pass - 0,11..0,15
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''',
r'''async def __FST_name(): pass''',
r'''async def SUB(): pass''', r'''
AsyncFunctionDef - ROOT 0,0..0,21
  .name 'SUB'
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''',
r'''class __FST_name: pass''',
r'''class SUB: pass''', r'''
ClassDef - ROOT 0,0..0,15
  .name 'SUB'
  .body[1]
   0] Pass - 0,11..0,15
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(mod=Name)''',
r'''from .__FST_mod import *''',
r'''from .SUB import *''', r'''
ImportFrom - ROOT 0,0..0,18
  .module 'SUB'
  .names[1]
   0] alias - 0,17..0,18
     .name '*'
  .level 1
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(Name)''',
r'''from .__FST_DEL import *''',
r'''from . import *''', r'''
ImportFrom - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,14..0,15
     .name '*'
  .level 1
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(mod=Name)''',
r'''from . import *''',
r'''from . import *''', r'''
ImportFrom - ROOT 0,0..0,15
  .names[1]
   0] alias - 0,14..0,15
     .name '*'
  .level 1
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(mod=Name)''',
r'''from .NOSUB import *''',
r'''from .NOSUB import *''', r'''
ImportFrom - ROOT 0,0..0,20
  .module 'NOSUB'
  .names[1]
   0] alias - 0,19..0,20
     .name '*'
  .level 1
'''),

('', None, None, None, {}, (None,
r'''SUB.ATTR'''),
r'''M(attr=Attribute)''',
r'''from .__FST_attr import *''',
r'''from .SUB.ATTR import *''', r'''
ImportFrom - ROOT 0,0..0,23
  .module 'SUB.ATTR'
  .names[1]
   0] alias - 0,22..0,23
     .name '*'
  .level 1
'''),

('', None, None, None, {}, (None,
r'''SUB1 = SUB2'''),
r'''MAssign([M(name1=Name)], M(name2=Name))''',
r'''global __FST_name1, __FST_DEL, __FST_name2''',
r'''global SUB1, SUB2''', r'''
Global - ROOT 0,0..0,17
  .names[2]
   0] 'SUB1'
   1] 'SUB2'
'''),

('', None, None, None, {}, (None,
r'''SUB1 = SUB2'''),
r'''MAssign([M(name1=Name)], M(name2=Name))''',
r'''nonlocal a, __FST_name1, __FST_name2, __FST_DEL''',
r'''nonlocal a, SUB1, SUB2''', r'''
Nonlocal - ROOT 0,0..0,22
  .names[3]
   0] 'a'
   1] 'SUB1'
   2] 'SUB2'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(attr=Name)''',
r'''value.__FST_attr''',
r'''value.SUB''', r'''
Attribute - ROOT 0,0..0,9
  .value Name 'value' Load - 0,0..0,5
  .attr 'SUB'
  .ctx Load
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''',
r'''__FST_name''',
r'''SUB''',
r'''Name 'SUB' Load - ROOT 0,0..0,3'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''',
r'''except Exception as __FST_name: pass''',
r'''except Exception as SUB: pass''', r'''
ExceptHandler - ROOT 0,0..0,29
  .type Name 'Exception' Load - 0,7..0,16
  .name 'SUB'
  .body[1]
   0] Pass - 0,25..0,29
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(Name)''',
r'''except Exception as __FST_DEL: pass''',
r'''except Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,22
  .type Name 'Exception' Load - 0,7..0,16
  .body[1]
   0] Pass - 0,18..0,22
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''',
r'''except Exception: pass''',
r'''except Exception: pass''', r'''
ExceptHandler - ROOT 0,0..0,22
  .type Name 'Exception' Load - 0,7..0,16
  .body[1]
   0] Pass - 0,18..0,22
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''',
r'''except Exception as NOSUB: pass''',
r'''except Exception as NOSUB: pass''', r'''
ExceptHandler - ROOT 0,0..0,31
  .type Name 'Exception' Load - 0,7..0,16
  .name 'NOSUB'
  .body[1]
   0] Pass - 0,27..0,31
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(arg=Name)''', ('arg',
r'''__FST_arg'''),
r'''SUB''',
r'''Name 'SUB' Load - ROOT 0,0..0,3'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(arg=Name)''', ('arg',
r'''__FST_arg: int'''),
r'''SUB: int''', r'''
arg - ROOT 0,0..0,8
  .arg 'SUB'
  .annotation Name 'int' Load - 0,5..0,8
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(kw=Name)''',
r'''call(__FST_kw=value)''',
r'''call(SUB=value)''', r'''
Call - ROOT 0,0..0,15
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,14
     .arg 'SUB'
     .value Name 'value' Load - 0,9..0,14
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(Name)''',
r'''call(__FST_DEL=value)''',
r'''call(**value)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,12
     .value Name 'value' Load - 0,7..0,12
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(kw=Name)''',
r'''call(**value)''',
r'''call(**value)''', r'''
Call - ROOT 0,0..0,13
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,12
     .value Name 'value' Load - 0,7..0,12
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(kw=Name)''',
r'''call(NOSUB=value)''',
r'''call(NOSUB=value)''', r'''
Call - ROOT 0,0..0,17
  .func Name 'call' Load - 0,0..0,4
  .keywords[1]
   0] keyword - 0,5..0,16
     .arg 'NOSUB'
     .value Name 'value' Load - 0,11..0,16
'''),

('', None, None, None, {}, (None,
r'''SUB1 = SUB2'''),
r'''MAssign([M(name1=Name)], M(name2=Name))''',
r'''import __FST_name1 as __FST_name2''',
r'''import SUB1 as SUB2''', r'''
Import - ROOT 0,0..0,19
  .names[1]
   0] alias - 0,7..0,19
     .name 'SUB1'
     .asname 'SUB2'
'''),

('', None, None, None, {}, (None,
r'''SUB1 = SUB2'''),
r'''MAssign([M(name1=Name)], M(name2=Name))''',
r'''from . import __FST_name1 as __FST_name2''',
r'''from . import SUB1 as SUB2''', r'''
ImportFrom - ROOT 0,0..0,26
  .names[1]
   0] alias - 0,14..0,26
     .name 'SUB1'
     .asname 'SUB2'
  .level 1
'''),

('', None, None, None, {}, (None,
r'''SUB.ATTR'''),
r'''M(attr=Attribute)''',
r'''import __FST_attr as asname''',
r'''import SUB.ATTR as asname''', r'''
Import - ROOT 0,0..0,25
  .names[1]
   0] alias - 0,7..0,25
     .name 'SUB.ATTR'
     .asname 'asname'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('pattern',
r'''{1: a, **__FST_name}'''),
r'''{1: a, **SUB}''', r'''
MatchMapping - ROOT 0,0..0,13
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'SUB'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(Name)''', ('pattern',
r'''{1: a, **__FST_DEL}'''),
r'''{1: a}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('pattern',
r'''{1: a}'''),
r'''{1: a}''', r'''
MatchMapping - ROOT 0,0..0,6
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('pattern',
r'''{1: a, **NOSUB}'''),
r'''{1: a, **NOSUB}''', r'''
MatchMapping - ROOT 0,0..0,15
  .keys[1]
   0] Constant 1 - 0,1..0,2
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .rest 'NOSUB'
'''),

('', None, None, None, {}, (None,
r'''SUB1 = SUB2'''),
r'''MAssign([M(name1=Name)], M(name2=Name))''', ('pattern',
r'''cls(a, __FST_name1=c, __FST_name2=e)'''),
r'''cls(a, SUB1=c, SUB2=e)''', r'''
MatchClass - ROOT 0,0..0,22
  .cls Name 'cls' Load - 0,0..0,3
  .patterns[1]
   0] MatchAs - 0,4..0,5
     .name 'a'
  .kwd_attrs[2]
   0] 'SUB1'
   1] 'SUB2'
  .kwd_patterns[2]
   0] MatchAs - 0,12..0,13
     .name 'c'
   1] MatchAs - 0,20..0,21
     .name 'e'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(st=Name)''', ('pattern',
r'''*__FST_st'''),
r'''*SUB''', r'''
MatchStar - ROOT 0,0..0,4
  .name 'SUB'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(Name)''', ('pattern',
r'''*__FST_DEL'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2'''),

('', None, None, None, {}, (None,
r'''_'''),
r'''M(st=Name)''', ('pattern',
r'''*__FST_st'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(st=Name)''', ('pattern',
r'''*_'''),
r'''*_''',
r'''MatchStar - ROOT 0,0..0,2'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(st=Name)''', ('pattern',
r'''*NOSUB'''),
r'''*NOSUB''', r'''
MatchStar - ROOT 0,0..0,6
  .name 'NOSUB'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('pattern',
r'''a as __FST_name'''),
r'''a as SUB''', r'''
MatchAs - ROOT 0,0..0,8
  .pattern MatchAs - 0,0..0,1
    .name 'a'
  .name 'SUB'
'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('pattern',
r'''__FST_name'''),
r'''SUB''',
r'''Name 'SUB' Load - ROOT 0,0..0,3'''),

('', None, None, None, {}, (None,
r'''_'''),
r'''M(name=Name)''', ('pattern',
r'''__FST_name'''),
r'''_''',
r'''Name '_' Load - ROOT 0,0..0,1'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(Name)''', ('pattern',
r'''__FST_DEL'''),
r'''**ValueError('cannot delete root node')**'''),

('', None, None, None, {'_ver': 12}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('TypeVar',
r'''__FST_name'''),
r'''SUB''',
r'''Name 'SUB' Load - ROOT 0,0..0,3'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=Name)''', ('TypeVar',
r'''__FST_name'''),
r'''SUB''', r'''
TypeVar - ROOT 0,0..0,3
  .name 'SUB'
'''),

('', None, None, None, {'_ver': 12}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('TypeVar',
r'''__FST_name: int'''),
r'''SUB: int''', r'''
TypeVar - ROOT 0,0..0,8
  .name 'SUB'
  .bound Name 'int' Load - 0,5..0,8
'''),

('', None, None, None, {'_ver': 12}, ('TypeVarTuple',
r'''*SUB'''),
r'''M(name=Name)''', ('TypeVar',
r'''__FST_name'''),
r'''*SUB''', r'''
TypeVarTuple - ROOT 0,0..0,4
  .name 'SUB'
'''),

('', None, None, None, {'_ver': 12}, ('ParamSpec',
r'''**SUB'''),
r'''M(name=Name)''', ('TypeVar',
r'''__FST_name'''),
r'''**SUB''', r'''
ParamSpec - ROOT 0,0..0,5
  .name 'SUB'
'''),

('', None, None, None, {'_ver': 12}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('ParamSpec',
r'''**__FST_name'''),
r'''**SUB''', r'''
ParamSpec - ROOT 0,0..0,5
  .name 'SUB'
'''),

('', None, None, None, {'_ver': 12}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('TypeVarTuple',
r'''*__FST_name'''),
r'''*SUB''', r'''
TypeVarTuple - ROOT 0,0..0,4
  .name 'SUB'
'''),

('', None, None, None, {'_ver': 13}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('TypeVar',
r'''__FST_name = bool'''),
r'''SUB = bool''', r'''
TypeVar - ROOT 0,0..0,10
  .name 'SUB'
  .default_value Name 'bool' Load - 0,6..0,10
'''),

('', None, None, None, {'_ver': 13}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('TypeVar',
r'''__FST_name: int = bool'''),
r'''SUB: int = bool''', r'''
TypeVar - ROOT 0,0..0,15
  .name 'SUB'
  .bound Name 'int' Load - 0,5..0,8
  .default_value Name 'bool' Load - 0,11..0,15
'''),

('', None, None, None, {'_ver': 13}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('ParamSpec',
r'''**__FST_name = bool'''),
r'''**SUB = bool''', r'''
ParamSpec - ROOT 0,0..0,12
  .name 'SUB'
  .default_value Name 'bool' Load - 0,8..0,12
'''),

('', None, None, None, {'_ver': 13}, (None,
r'''SUB'''),
r'''M(name=Name)''', ('TypeVarTuple',
r'''*__FST_name = bool'''),
r'''*SUB = bool''', r'''
TypeVarTuple - ROOT 0,0..0,11
  .name 'SUB'
  .default_value Name 'bool' Load - 0,7..0,11
'''),
],

'cross_type': [  # ................................................................................

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(__FST_, /): pass''',
r'''def f(SUB, /): pass''', r'''
FunctionDef - ROOT 0,0..0,19
  .name 'f'
  .args arguments - 0,6..0,12
    .posonlyargs[1]
     0] arg - 0,6..0,9
       .arg 'SUB'
  .body[1]
   0] Pass - 0,15..0,19
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(__FST_): pass''',
r'''def f(SUB): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'f'
  .args arguments - 0,6..0,9
    .args[1]
     0] arg - 0,6..0,9
       .arg 'SUB'
  .body[1]
   0] Pass - 0,12..0,16
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(*__FST_): pass''',
r'''def f(*SUB): pass''', r'''
FunctionDef - ROOT 0,0..0,17
  .name 'f'
  .args arguments - 0,6..0,10
    .vararg arg - 0,7..0,10
      .arg 'SUB'
  .body[1]
   0] Pass - 0,13..0,17
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(*, __FST_): pass''',
r'''def f(*, SUB): pass''', r'''
FunctionDef - ROOT 0,0..0,19
  .name 'f'
  .args arguments - 0,6..0,12
    .kwonlyargs[1]
     0] arg - 0,9..0,12
       .arg 'SUB'
    .kw_defaults[1]
     0] None
  .body[1]
   0] Pass - 0,15..0,19
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(**__FST_): pass''',
r'''def f(**SUB): pass''', r'''
FunctionDef - ROOT 0,0..0,18
  .name 'f'
  .args arguments - 0,6..0,11
    .kwarg arg - 0,8..0,11
      .arg 'SUB'
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(__FST_: int, /): pass''',
r'''def f(SUB: int, /): pass''', r'''
FunctionDef - ROOT 0,0..0,24
  .name 'f'
  .args arguments - 0,6..0,17
    .posonlyargs[1]
     0] arg - 0,6..0,14
       .arg 'SUB'
       .annotation Name 'int' Load - 0,11..0,14
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(__FST_: int): pass''',
r'''def f(SUB: int): pass''', r'''
FunctionDef - ROOT 0,0..0,21
  .name 'f'
  .args arguments - 0,6..0,14
    .args[1]
     0] arg - 0,6..0,14
       .arg 'SUB'
       .annotation Name 'int' Load - 0,11..0,14
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(*__FST_: int): pass''',
r'''def f(*SUB: int): pass''', r'''
FunctionDef - ROOT 0,0..0,22
  .name 'f'
  .args arguments - 0,6..0,15
    .vararg arg - 0,7..0,15
      .arg 'SUB'
      .annotation Name 'int' Load - 0,12..0,15
  .body[1]
   0] Pass - 0,18..0,22
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(*, __FST_: int): pass''',
r'''def f(*, SUB: int): pass''', r'''
FunctionDef - ROOT 0,0..0,24
  .name 'f'
  .args arguments - 0,6..0,17
    .kwonlyargs[1]
     0] arg - 0,9..0,17
       .arg 'SUB'
       .annotation Name 'int' Load - 0,14..0,17
    .kw_defaults[1]
     0] None
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''def f(**__FST_: int): pass''',
r'''def f(**SUB: int): pass''', r'''
FunctionDef - ROOT 0,0..0,23
  .name 'f'
  .args arguments - 0,6..0,16
    .kwarg arg - 0,8..0,16
      .arg 'SUB'
      .annotation Name 'int' Load - 0,13..0,16
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(SUB, /): pass'''),
r'''MFunctionDef(args=Marguments(posonlyargs=[M(arg=arg)]))''',
r'''a = __FST_arg''',
r'''a = SUB''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'SUB' Load - 0,4..0,7
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(SUB): pass'''),
r'''MFunctionDef(args=Marguments(args=[M(arg=arg)]))''',
r'''a = __FST_arg''',
r'''a = SUB''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'SUB' Load - 0,4..0,7
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(*SUB): pass'''),
r'''MFunctionDef(args=Marguments(vararg=M(arg=arg)))''',
r'''a = __FST_arg''',
r'''a = SUB''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'SUB' Load - 0,4..0,7
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(*, SUB): pass'''),
r'''MFunctionDef(args=Marguments(kwonlyargs=[M(arg=arg)]))''',
r'''a = __FST_arg''',
r'''a = SUB''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'SUB' Load - 0,4..0,7
'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(**SUB): pass'''),
r'''MFunctionDef(args=Marguments(kwarg=M(arg=arg)))''',
r'''a = __FST_arg''',
r'''a = SUB''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'SUB' Load - 0,4..0,7
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(__FST_, /): pass''',
r'''def f(SUB, /): pass''', r'''
FunctionDef - ROOT 0,0..0,19
  .name 'f'
  .args arguments - 0,6..0,12
    .posonlyargs[1]
     0] arg - 0,6..0,9
       .arg 'SUB'
  .body[1]
   0] Pass - 0,15..0,19
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(__FST_): pass''',
r'''def f(SUB): pass''', r'''
FunctionDef - ROOT 0,0..0,16
  .name 'f'
  .args arguments - 0,6..0,9
    .args[1]
     0] arg - 0,6..0,9
       .arg 'SUB'
  .body[1]
   0] Pass - 0,12..0,16
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(*__FST_): pass''',
r'''def f(*SUB): pass''', r'''
FunctionDef - ROOT 0,0..0,17
  .name 'f'
  .args arguments - 0,6..0,10
    .vararg arg - 0,7..0,10
      .arg 'SUB'
  .body[1]
   0] Pass - 0,13..0,17
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(*, __FST_): pass''',
r'''def f(*, SUB): pass''', r'''
FunctionDef - ROOT 0,0..0,19
  .name 'f'
  .args arguments - 0,6..0,12
    .kwonlyargs[1]
     0] arg - 0,9..0,12
       .arg 'SUB'
    .kw_defaults[1]
     0] None
  .body[1]
   0] Pass - 0,15..0,19
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(**__FST_): pass''',
r'''def f(**SUB): pass''', r'''
FunctionDef - ROOT 0,0..0,18
  .name 'f'
  .args arguments - 0,6..0,11
    .kwarg arg - 0,8..0,11
      .arg 'SUB'
  .body[1]
   0] Pass - 0,14..0,18
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(__FST_: int, /): pass''',
r'''def f(SUB: int, /): pass''', r'''
FunctionDef - ROOT 0,0..0,24
  .name 'f'
  .args arguments - 0,6..0,17
    .posonlyargs[1]
     0] arg - 0,6..0,14
       .arg 'SUB'
       .annotation Name 'int' Load - 0,11..0,14
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(__FST_: int): pass''',
r'''def f(SUB: int): pass''', r'''
FunctionDef - ROOT 0,0..0,21
  .name 'f'
  .args arguments - 0,6..0,14
    .args[1]
     0] arg - 0,6..0,14
       .arg 'SUB'
       .annotation Name 'int' Load - 0,11..0,14
  .body[1]
   0] Pass - 0,17..0,21
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(*__FST_: int): pass''',
r'''def f(*SUB: int): pass''', r'''
FunctionDef - ROOT 0,0..0,22
  .name 'f'
  .args arguments - 0,6..0,15
    .vararg arg - 0,7..0,15
      .arg 'SUB'
      .annotation Name 'int' Load - 0,12..0,15
  .body[1]
   0] Pass - 0,18..0,22
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(*, __FST_: int): pass''',
r'''def f(*, SUB: int): pass''', r'''
FunctionDef - ROOT 0,0..0,24
  .name 'f'
  .args arguments - 0,6..0,17
    .kwonlyargs[1]
     0] arg - 0,9..0,17
       .arg 'SUB'
       .annotation Name 'int' Load - 0,14..0,17
    .kw_defaults[1]
     0] None
  .body[1]
   0] Pass - 0,20..0,24
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''def f(**__FST_: int): pass''',
r'''def f(**SUB: int): pass''', r'''
FunctionDef - ROOT 0,0..0,23
  .name 'f'
  .args arguments - 0,6..0,16
    .kwarg arg - 0,8..0,16
      .arg 'SUB'
      .annotation Name 'int' Load - 0,13..0,16
  .body[1]
   0] Pass - 0,19..0,23
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def f(SUB, /): pass'''),
r'''MFunctionDef(args=Marguments(posonlyargs=[M(arg=arg)]))''',
r'''type t[__FST_arg] = ...''',
r'''type t[SUB] = ...''', r'''
TypeAlias - ROOT 0,0..0,17
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,10
     .name 'SUB'
  .value Constant Ellipsis - 0,14..0,17
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def f(SUB): pass'''),
r'''MFunctionDef(args=Marguments(args=[M(arg=arg)]))''',
r'''type t[__FST_arg] = ...''',
r'''type t[SUB] = ...''', r'''
TypeAlias - ROOT 0,0..0,17
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,10
     .name 'SUB'
  .value Constant Ellipsis - 0,14..0,17
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def f(*SUB): pass'''),
r'''MFunctionDef(args=Marguments(vararg=M(arg=arg)))''',
r'''type t[__FST_arg] = ...''',
r'''type t[SUB] = ...''', r'''
TypeAlias - ROOT 0,0..0,17
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,10
     .name 'SUB'
  .value Constant Ellipsis - 0,14..0,17
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def f(*, SUB): pass'''),
r'''MFunctionDef(args=Marguments(kwonlyargs=[M(arg=arg)]))''',
r'''type t[__FST_arg] = ...''',
r'''type t[SUB] = ...''', r'''
TypeAlias - ROOT 0,0..0,17
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,10
     .name 'SUB'
  .value Constant Ellipsis - 0,14..0,17
'''),

('', None, None, None, {'_ver': 12}, ('FunctionDef',
r'''def f(**SUB): pass'''),
r'''MFunctionDef(args=Marguments(kwarg=M(arg=arg)))''',
r'''type t[__FST_arg] = ...''',
r'''type t[SUB] = ...''', r'''
TypeAlias - ROOT 0,0..0,17
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,10
     .name 'SUB'
  .value Constant Ellipsis - 0,14..0,17
'''),

('', None, None, None, {'_ver': 12}, ('Name',
r'''SUB'''),
r'''M(name=Name)''',
r'''type t[__FST_] = ...''',
r'''type t[SUB] = ...''', r'''
TypeAlias - ROOT 0,0..0,17
  .name Name 't' Store - 0,5..0,6
  .type_params[1]
   0] TypeVar - 0,7..0,10
     .name 'SUB'
  .value Constant Ellipsis - 0,14..0,17
'''),

('', None, None, None, {'_ver': 12}, ('TypeVar',
r'''SUB'''),
r'''M(name=TypeVar)''',
r'''a = __FST_''',
r'''a = SUB''', r'''
Assign - ROOT 0,0..0,7
  .targets[1]
   0] Name 'a' Store - 0,0..0,1
  .value Name 'SUB' Load - 0,4..0,7
'''),
],

'stringify': [  # ................................................................................

('', None, None, None, {}, ('Name',
r'''a'''),
r'''Name''',
r'''log(__FST_, "__FST_")''',
r'''log(a, "a")''', r'''
Call - ROOT 0,0..0,11
  .func Name 'log' Load - 0,0..0,3
  .args[2]
   0] Name 'a' Load - 0,4..0,5
   1] Constant '__FST_' - 0,7..0,10
'''),

('', None, None, None, {}, ('exec', r'''
pass
if a:
    pass
pass
'''),
r'''Module(body=[..., M(t=...), ...])''',
r'''middle = "__FST_t"''',
r'''middle = "if a:\n    pass"''', r'''
Assign - ROOT 0,0..0,26
  .targets[1]
   0] Name 'middle' Store - 0,0..0,6
  .value Constant '__FST_t' - 0,9..0,26
'''),

('', None, None, None, {}, ('exec', r'''
pass
if a: \
    pass
call('str')
pass
'''),
r'''Module(body=[..., MQSTAR(t=...), ...])''', r'''
middle = "__FST_t"
__FST_t
''', r'''
middle = "if a: \\\n    pass\ncall(\'str\')"
if a: \
    pass
call('str')
''', r'''
Module - ROOT 0,0..3,11
  .body[3]
   0] Assign - 0,0..0,44
     .targets[1]
      0] Name 'middle' Store - 0,0..0,6
     .value Constant '__FST_t' - 0,9..0,44
   1] If - 1,0..2,8
     .test Name 'a' Load - 1,3..1,4
     .body[1]
      0] Pass - 2,4..2,8
   2] Expr - 3,0..3,11
     .value Call - 3,0..3,11
       .func Name 'call' Load - 3,0..3,4
       .args[1]
        0] Constant 'str' - 3,5..3,10
'''),

('', None, None, None, {}, ('exec', r'''
pass
if a: \
    pass
call('str')
pass
'''),
r'''Module(body=[..., MQSTAR(t=...), ...])''', r'''
middle = """__FST_t
__FST_t
__FST_t"""
''', r'''
middle = """if a: \\\n    pass\ncall(\'str\')
if a: \\\n    pass\ncall(\'str\')
if a: \\\n    pass\ncall(\'str\')"""
''', r'''
Assign - ROOT 0,0..2,36
  .targets[1]
   0] Name 'middle' Store - 0,0..0,6
  .value Constant '__FST_t\n__FST_t\n__FST_t' - 0,9..2,36
'''),

('', None, None, None, {}, (None,
r'''a + b.c + d[e]'''),
r'''M(t=MOR(Name, Attribute, Subscript))''',
r'''log(__FST_t, '__FST_t')''',
r'''log(a, 'a') + log(b.c, 'b.c') + log(d[e], 'd[e]')''', r'''
BinOp - ROOT 0,0..0,49
  .left BinOp - 0,0..0,29
    .left Call - 0,0..0,11
      .func Name 'log' Load - 0,0..0,3
      .args[2]
       0] Name 'a' Load - 0,4..0,5
       1] Constant '__FST_t' - 0,7..0,10
    .op Add - 0,12..0,13
    .right Call - 0,14..0,29
      .func Name 'log' Load - 0,14..0,17
      .args[2]
       0] Attribute - 0,18..0,21
         .value Name 'b' Load - 0,18..0,19
         .attr 'c'
         .ctx Load
       1] Constant '__FST_t' - 0,23..0,28
  .op Add - 0,30..0,31
  .right Call - 0,32..0,49
    .func Name 'log' Load - 0,32..0,35
    .args[2]
     0] Subscript - 0,36..0,40
       .value Name 'd' Load - 0,36..0,37
       .slice Name 'e' Load - 0,38..0,39
       .ctx Load
     1] Constant '__FST_t' - 0,42..0,48
'''),

('', None, None, None, {'nested': True}, (None,
r'''a + b.c + d[e]'''),
r'''M(t=MOR(Name, Attribute, Subscript))''',
r'''log(__FST_t, '__FST_t')''',
r'''log(a, 'a') + log(log(b, 'b').c, 'b.c') + log(log(d, 'd')[log(e, 'e')], 'd[e]')''', r'''
BinOp - ROOT 0,0..0,79
  .left BinOp - 0,0..0,39
    .left Call - 0,0..0,11
      .func Name 'log' Load - 0,0..0,3
      .args[2]
       0] Name 'a' Load - 0,4..0,5
       1] Constant '__FST_t' - 0,7..0,10
    .op Add - 0,12..0,13
    .right Call - 0,14..0,39
      .func Name 'log' Load - 0,14..0,17
      .args[2]
       0] Attribute - 0,18..0,31
         .value Call - 0,18..0,29
           .func Name 'log' Load - 0,18..0,21
           .args[2]
            0] Name 'b' Load - 0,22..0,23
            1] Constant '__FST_t' - 0,25..0,28
         .attr 'c'
         .ctx Load
       1] Constant '__FST_t' - 0,33..0,38
  .op Add - 0,40..0,41
  .right Call - 0,42..0,79
    .func Name 'log' Load - 0,42..0,45
    .args[2]
     0] Subscript - 0,46..0,70
       .value Call - 0,46..0,57
         .func Name 'log' Load - 0,46..0,49
         .args[2]
          0] Name 'd' Load - 0,50..0,51
          1] Constant '__FST_t' - 0,53..0,56
       .slice Call - 0,58..0,69
         .func Name 'log' Load - 0,58..0,61
         .args[2]
          0] Name 'e' Load - 0,62..0,63
          1] Constant '__FST_t' - 0,65..0,68
       .ctx Load
     1] Constant '__FST_t' - 0,72..0,78
'''),

('', None, None, None, {'nested': True, 'count': 2}, (None,
r'''a + b.c + d[e]'''),
r'''M(t=MOR(Name, Attribute, Subscript))''',
r'''log(__FST_t, '__FST_t')''',
r'''log(a, 'a') + log(b.c, 'b.c') + d[e]''', r'''
BinOp - ROOT 0,0..0,36
  .left BinOp - 0,0..0,29
    .left Call - 0,0..0,11
      .func Name 'log' Load - 0,0..0,3
      .args[2]
       0] Name 'a' Load - 0,4..0,5
       1] Constant '__FST_t' - 0,7..0,10
    .op Add - 0,12..0,13
    .right Call - 0,14..0,29
      .func Name 'log' Load - 0,14..0,17
      .args[2]
       0] Attribute - 0,18..0,21
         .value Name 'b' Load - 0,18..0,19
         .attr 'c'
         .ctx Load
       1] Constant '__FST_t' - 0,23..0,28
  .op Add - 0,30..0,31
  .right Subscript - 0,32..0,36
    .value Name 'd' Load - 0,32..0,33
    .slice Name 'e' Load - 0,34..0,35
    .ctx Load
'''),
],

'trivia_all_options_stmt': [  # ................................................................................

('', None, None, None, {}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre ORG

# pre-pre REPL

# pre ORG
statement  # line ORG
# post REPL

# post-post REPL
# post ORG

# post-post ORG
''', r'''
Module - ROOT 0,0..11,15
  .body[1]
   0] Expr - 5,0..5,9
     .value Name 'statement' Load - 5,0..5,9
'''),

('', None, None, None, {'trivia': ('all', 'all')}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
''', r'''
Module - ROOT 0,0..6,15
  .body[1]
   0] Expr - 3,0..3,9
     .value Name 'statement' Load - 3,0..3,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''),
r'''statement''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Name 'statement' Load - 0,0..0,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': ()}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre REPL

# pre REPL
statement
# line REPL
# post REPL

# post-post REPL
''', r'''
Module - ROOT 0,0..7,16
  .body[1]
   0] Expr - 3,0..3,9
     .value Name 'statement' Load - 3,0..3,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': (False, True)}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre REPL

# pre REPL
statement
# post REPL

# post-post REPL
''', r'''
Module - ROOT 0,0..6,16
  .body[1]
   0] Expr - 3,0..3,9
     .value Name 'statement' Load - 3,0..3,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': ('block', 'block')}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre REPL

statement

# post-post REPL
''', r'''
Module - ROOT 0,0..4,16
  .body[1]
   0] Expr - 2,0..2,9
     .value Name 'statement' Load - 2,0..2,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': ('block+', 'block+')}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre REPL
statement
# post-post REPL
''', r'''
Module - ROOT 0,0..2,16
  .body[1]
   0] Expr - 1,0..1,9
     .value Name 'statement' Load - 1,0..1,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': ('all', 'all')}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''),
r'''statement''', r'''
Module - ROOT 0,0..0,9
  .body[1]
   0] Expr - 0,0..0,9
     .value Name 'statement' Load - 0,0..0,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': (False, False)}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre REPL

# pre REPL
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
# line REPL
# post REPL

# post-post REPL
''', r'''
Module - ROOT 0,0..13,16
  .body[1]
   0] Expr - 6,0..6,9
     .value Name 'statement' Load - 6,0..6,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': (False, 'line')}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre REPL

# pre REPL
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
# post REPL

# post-post REPL
''', r'''
Module - ROOT 0,0..12,16
  .body[1]
   0] Expr - 6,0..6,9
     .value Name 'statement' Load - 6,0..6,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': ('block', 'block')}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre REPL

# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG

# post-post REPL
''', r'''
Module - ROOT 0,0..10,16
  .body[1]
   0] Expr - 5,0..5,9
     .value Name 'statement' Load - 5,0..5,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': ('block+', 'block+')}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre REPL
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
# post-post REPL
''', r'''
Module - ROOT 0,0..8,16
  .body[1]
   0] Expr - 4,0..4,9
     .value Name 'statement' Load - 4,0..4,9
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': ('all', 'all')}}, ('exec', r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
'''),
r'''Mstmt''', ('exec', r'''
# pre-pre REPL

# pre REPL
__FST_  # line REPL
# post REPL

# post-post REPL
'''), r'''
# pre-pre ORG

# pre ORG
statement  # line ORG
# post ORG

# post-post ORG
''', r'''
Module - ROOT 0,0..6,15
  .body[1]
   0] Expr - 3,0..3,9
     .value Name 'statement' Load - 3,0..3,9
'''),
],

'trivia_all_options_expr_slice': [  # ................................................................................

('', None, None, None, {}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL

# pre ORG
statement,  # line ORG
# post REPL

# post-post REPL
]
''', r'''
List - ROOT 0,0..8,1
  .elts[1]
   0] Name 'statement' Load - 4,0..4,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all')}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
''', r'''
List - ROOT 0,0..8,1
  .elts[1]
   0] Name 'statement' Load - 4,0..4,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
statement
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'statement' Load - 1,0..1,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': ()}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL

# pre REPL
statement, # line REPL
# post REPL

# post-post REPL
]
''', r'''
List - ROOT 0,0..8,1
  .elts[1]
   0] Name 'statement' Load - 4,0..4,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': (False, True)}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL

# pre REPL
statement
# post REPL

# post-post REPL
]
''', r'''
List - ROOT 0,0..8,1
  .elts[1]
   0] Name 'statement' Load - 4,0..4,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': ('block', 'block')}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL

statement

# post-post REPL
]
''', r'''
List - ROOT 0,0..6,1
  .elts[1]
   0] Name 'statement' Load - 3,0..3,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': ('block+', 'block+')}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL
statement
# post-post REPL
]
''', r'''
List - ROOT 0,0..4,1
  .elts[1]
   0] Name 'statement' Load - 2,0..2,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ()}, 'repl_options': {'trivia': ('all', 'all')}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
statement
]
''', r'''
List - ROOT 0,0..2,1
  .elts[1]
   0] Name 'statement' Load - 1,0..1,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': (False, False)}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL

# pre REPL
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
# line REPL
# post REPL

# post-post REPL
]
''', r'''
List - ROOT 0,0..15,1
  .elts[1]
   0] Name 'statement' Load - 7,0..7,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': (False, 'line')}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL

# pre REPL
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
# post REPL

# post-post REPL
]
''', r'''
List - ROOT 0,0..14,1
  .elts[1]
   0] Name 'statement' Load - 7,0..7,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': ('block', 'block')}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL

# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG

# post-post REPL
]
''', r'''
List - ROOT 0,0..12,1
  .elts[1]
   0] Name 'statement' Load - 6,0..6,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': ('block+', 'block+')}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre REPL
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
# post-post REPL
]
''', r'''
List - ROOT 0,0..10,1
  .elts[1]
   0] Name 'statement' Load - 5,0..5,9
  .ctx Load
'''),

('', None, None, None, {'trivia': ('all', 'all'), 'copy_options': {'trivia': ('all', 'all')}, 'repl_options': {'trivia': ('all', 'all')}}, ('List', r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
'''),
r'''MList(elts=M(e=...))''', ('List', r'''
[
# pre-pre REPL

# pre REPL
__FST_e,  # line REPL
# post REPL

# post-post REPL
]
'''), r'''
[
# pre-pre ORG

# pre ORG
statement,  # line ORG
# post ORG

# post-post ORG
]
''', r'''
List - ROOT 0,0..8,1
  .elts[1]
   0] Name 'statement' Load - 4,0..4,9
  .ctx Load
'''),
],

'nested_quantifier_lists': [  # ................................................................................

('', None, None, None, {}, ('List',
r'''[a, a, b, b, c, c, d, d]'''),
r'''MList([MQPLUS.NG, MQMIN(t=[M(u=...), MTAG('u')], min=1), MQPLUS])''', ('List',
r'''[x, __FST_t, y]'''),
r'''[x, b, b, c, c, y]''', r'''
List - ROOT 0,0..0,18
  .elts[6]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'b' Load - 0,7..0,8
   3] Name 'c' Load - 0,10..0,11
   4] Name 'c' Load - 0,13..0,14
   5] Name 'y' Load - 0,16..0,17
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, a, b, b, b, c, c, c, c, d, d]'''),
r'''MList([MQPLUS.NG, MQMIN(t=[M(u=...), MQPLUS([MTAG('u')])], min=1), MQPLUS])''', ('List',
r'''[x, __FST_t, y]'''),
r'''[x, b, b, b, c, c, c, c, y]''', r'''
List - ROOT 0,0..0,27
  .elts[9]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'b' Load - 0,7..0,8
   3] Name 'b' Load - 0,10..0,11
   4] Name 'c' Load - 0,13..0,14
   5] Name 'c' Load - 0,16..0,17
   6] Name 'c' Load - 0,19..0,20
   7] Name 'c' Load - 0,22..0,23
   8] Name 'y' Load - 0,25..0,26
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, a, b, b, b, b, c, c, c, c, d, d]'''),
r'''MList([MQPLUS.NG, MQMIN(t=[MQ([M(u=...), MQPLUS([MTAG('u')])], min=1, max=2)], min=1), MQPLUS])''', ('List',
r'''[x, __FST_t, y]'''),
r'''[x, b, b, b, b, c, c, c, c, y]''', r'''
List - ROOT 0,0..0,30
  .elts[10]
   0] Name 'x' Load - 0,1..0,2
   1] Name 'b' Load - 0,4..0,5
   2] Name 'b' Load - 0,7..0,8
   3] Name 'b' Load - 0,10..0,11
   4] Name 'b' Load - 0,13..0,14
   5] Name 'c' Load - 0,16..0,17
   6] Name 'c' Load - 0,19..0,20
   7] Name 'c' Load - 0,22..0,23
   8] Name 'c' Load - 0,25..0,26
   9] Name 'y' Load - 0,28..0,29
  .ctx Load
'''),

('', None, None, None, {}, ('List',
r'''[a, a, b, b, b, b, c, c, c, c, d, d]'''),
r'''MList([MQPLUS.NG, MQMIN(t=[MQ([M(u=...), MQPLUS([MTAG('u')])], min=1, max=2)], min=1), MQPLUS])''', ('List',
r'''[x, __FSO_t, y]'''),
r'''[x, [b, b, b, b, c, c, c, c], y]''', r'''
List - ROOT 0,0..0,32
  .elts[3]
   0] Name 'x' Load - 0,1..0,2
   1] List - 0,4..0,28
     .elts[8]
      0] Name 'b' Load - 0,5..0,6
      1] Name 'b' Load - 0,8..0,9
      2] Name 'b' Load - 0,11..0,12
      3] Name 'b' Load - 0,14..0,15
      4] Name 'c' Load - 0,17..0,18
      5] Name 'c' Load - 0,20..0,21
      6] Name 'c' Load - 0,23..0,24
      7] Name 'c' Load - 0,26..0,27
     .ctx Load
   2] Name 'y' Load - 0,30..0,31
  .ctx Load
'''),
],

'misc': [  # ................................................................................

('', None, None, None, {}, ('FunctionDef',
r'''def f(a: int): pass'''),
r'''MFunctionDef(args=M(a=...))''', (None,
r'''lambda __FST_a: None'''),
r'''**NodeError('lambda arguments cannot have annotations')**'''),

('', None, None, None, {}, ('FunctionDef',
r'''def f(**kwargs): pass'''),
r'''MFunctionDef(args=M(a=...))''', (None,
r'''def g(__FST_a, k=w): pass'''),
r'''**NodeError('args cannot follow kwarg')**'''),
],

}
