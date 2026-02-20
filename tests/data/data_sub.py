# (attr, None, None, None, sub_call_params, code | (parse_mode, code),
# 'pattern',
# repl | (repl_mode, repl),
# ((code after sub,
# dump code after sub,)
# - OR
# (error,))
# )

DATA_SUB = {
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
