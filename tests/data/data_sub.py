# (attr, None, None, None, sub_call_params, code | (parse_mode, code),
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
r'''**NodeError('posonlyargs cannot follow args')**'''),

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
r'''a, b, c'''),
r'''MTuple''',
r'''with __FST_: pass''',
r'''with ((a, b, c)): pass''', r'''
With - ROOT 0,0..0,22
  .items[1]
   0] withitem - 0,5..0,16
     .context_expr Tuple - 0,6..0,15
       .elts[3]
        0] Name 'a' Load - 0,7..0,8
        1] Name 'b' Load - 0,10..0,11
        2] Name 'c' Load - 0,13..0,14
       .ctx Load
  .body[1]
   0] Pass - 0,18..0,22
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
r'''with ((a, b, c)): pass''', r'''
With - ROOT 0,0..0,22
  .items[1]
   0] withitem - 0,5..0,16
     .context_expr Tuple - 0,6..0,15
       .elts[3]
        0] Name 'a' Load - 0,7..0,8
        1] Name 'b' Load - 0,10..0,11
        2] Name 'c' Load - 0,13..0,14
       .ctx Load
  .body[1]
   0] Pass - 0,18..0,22
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
r'''**TypeError("unsupported operand type(s) for +: 'NoneType' and 'int'")**'''),

('', None, None, None, {}, ('Import',
r'''import a, b.c, d as e'''),
r'''MImport(names=M(n=...))''', (None,
r'''from .__FST_n import *'''),
r'''**TypeError("unsupported operand type(s) for +: 'NoneType' and 'int'")**'''),

('', None, None, None, {}, ('Import',
r'''import a'''),
r'''MImport(names=M(n=...))''', (None,
r'''from .__FST_n import *'''),
r'''**TypeError("unsupported operand type(s) for +: 'NoneType' and 'int'")**'''),

('', None, None, None, {}, ('Import',
r'''import a.b'''),
r'''MImport(names=M(n=...))''', (None,
r'''from .__FST_n import *'''),
r'''**TypeError("unsupported operand type(s) for +: 'NoneType' and 'int'")**'''),

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
r'''x and (a and b) and y''', r'''
BoolOp - ROOT 0,0..0,21
  .op And
  .values[3]
   0] Name 'x' Load - 0,0..0,1
   1] BoolOp - 0,7..0,14
     .op And
     .values[2]
      0] Name 'a' Load - 0,7..0,8
      1] Name 'b' Load - 0,13..0,14
   2] Name 'y' Load - 0,20..0,21
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
r'''SUB''', r'''
MatchAs - ROOT 0,0..0,3
  .name 'SUB'
'''),

('', None, None, None, {}, (None,
r'''_'''),
r'''M(name=Name)''', ('pattern',
r'''__FST_name'''),
r'''_''',
r'''MatchAs - ROOT 0,0..0,1'''),

('', None, None, None, {}, (None,
r'''SUB'''),
r'''M(Name)''', ('pattern',
r'''__FST_DEL'''),
r'''_''',
r'''MatchAs - ROOT 0,0..0,1'''),

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

}
