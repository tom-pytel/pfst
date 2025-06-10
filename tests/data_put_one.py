PUT_ONE_DATA = [
(r"""i = 1
j = 2
k = 3""", '', 1, None, {}, r"""l = 4""", r"""i = 1
l = 4
k = 3""", r"""
Module - ROOT 0,0..2,5
  .body[3]
  0] Assign - 0,0..0,5
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value Constant 1 - 0,4..0,5
  1] Assign - 1,0..1,5
    .targets[1]
    0] Name 'l' Store - 1,0..1,1
    .value Constant 4 - 1,4..1,5
  2] Assign - 2,0..2,5
    .targets[1]
    0] Name 'k' Store - 2,0..2,1
    .value Constant 3 - 2,4..2,5
"""),

(r"""i = 1
j = 2
k = 3""", '', -1, None, {}, r"""l = 4""", r"""i = 1
j = 2
l = 4
""", r"""
Module - ROOT 0,0..3,0
  .body[3]
  0] Assign - 0,0..0,5
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value Constant 1 - 0,4..0,5
  1] Assign - 1,0..1,5
    .targets[1]
    0] Name 'j' Store - 1,0..1,1
    .value Constant 2 - 1,4..1,5
  2] Assign - 2,0..2,5
    .targets[1]
    0] Name 'l' Store - 2,0..2,1
    .value Constant 4 - 2,4..2,5
"""),

(r"""i = 1
j = 2
k = 3""", '', -3, None, {}, r"""l = 4""", r"""l = 4
j = 2
k = 3""", r"""
Module - ROOT 0,0..2,5
  .body[3]
  0] Assign - 0,0..0,5
    .targets[1]
    0] Name 'l' Store - 0,0..0,1
    .value Constant 4 - 0,4..0,5
  1] Assign - 1,0..1,5
    .targets[1]
    0] Name 'j' Store - 1,0..1,1
    .value Constant 2 - 1,4..1,5
  2] Assign - 2,0..2,5
    .targets[1]
    0] Name 'k' Store - 2,0..2,1
    .value Constant 3 - 2,4..2,5
"""),

(r"""i = 1
j = 2
k = 3""", '', -4, None, {}, r"""l = 4""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""(1, 2, 3)""", 'body[0].value', 1, None, {}, r"""4""", r"""(1, 4, 3)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Tuple - 0,0..0,9
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 4 - 0,4..0,5
      2] Constant 3 - 0,7..0,8
      .ctx Load
"""),

(r"""(1, 2, 3)""", 'body[0].value', -1, None, {}, r"""4""", r"""(1, 2, 4)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Tuple - 0,0..0,9
      .elts[3]
      0] Constant 1 - 0,1..0,2
      1] Constant 2 - 0,4..0,5
      2] Constant 4 - 0,7..0,8
      .ctx Load
"""),

(r"""(1, 2, 3)""", 'body[0].value', -3, None, {}, r"""4""", r"""(4, 2, 3)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Tuple - 0,0..0,9
      .elts[3]
      0] Constant 4 - 0,1..0,2
      1] Constant 2 - 0,4..0,5
      2] Constant 3 - 0,7..0,8
      .ctx Load
"""),

(r"""(1, 2, 3)""", 'body[0].value', -4, None, {}, r"""4""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""i = j""", 'body[0]', None, None, {}, r"""**DEL**""", r"""**ValueError('cannot delete Assign.value')**""", r"""
"""),

(r"""i = j""", 'body[0]', None, None, {}, r"""k""", r"""i = k""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Assign - 0,0..0,5
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value Name 'k' Load - 0,4..0,5
"""),

(r"""i = j""", 'body[0]', None, None, {'raw': False}, r"""a, b""", r"""i = (a, b)""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Assign - 0,0..0,10
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value Tuple - 0,4..0,10
      .elts[2]
      0] Name 'a' Load - 0,5..0,6
      1] Name 'b' Load - 0,8..0,9
      .ctx Load
"""),

(r"""i = j""", 'body[0]', None, None, {'pars': False}, r"""a, b""", r"""i = a, b""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Assign - 0,0..0,8
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value Tuple - 0,4..0,8
      .elts[2]
      0] Name 'a' Load - 0,4..0,5
      1] Name 'b' Load - 0,7..0,8
      .ctx Load
"""),

(r"""i = (j)""", 'body[0]', None, None, {}, r"""(a := b)""", r"""i = (a := b)""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Assign - 0,0..0,12
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value NamedExpr - 0,5..0,11
      .target Name 'a' Store - 0,5..0,6
      .value Name 'b' Load - 0,10..0,11
"""),

(r"""i = (j)""", 'body[0]', None, None, {'pars': False}, r"""(a := b)""", r"""i = ((a := b))""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Assign - 0,0..0,14
    .targets[1]
    0] Name 'i' Store - 0,0..0,1
    .value NamedExpr - 0,6..0,12
      .target Name 'a' Store - 0,6..0,7
      .value Name 'b' Load - 0,11..0,12
"""),

(r"""i""", 'body[0]', None, None, {}, r"""j""", r"""j""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""i""", 'body[0]', None, None, {'raw': False}, r"""a, b""", r"""(a, b)""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value Tuple - 0,0..0,6
      .elts[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,4..0,5
      .ctx Load
"""),

(r"""( # 1
i
# 2
)""", 'body[0]', None, None, {'pars': False}, r"""( # 3
j
# 4
)""", r"""( # 1
( # 3
j
# 4
)
# 2
)""", r"""
Module - ROOT 0,0..6,1
  .body[1]
  0] Expr - 0,0..6,1
    .value Name 'j' Load - 2,0..2,1
"""),

(r"""( # 1
i
# 2
)""", 'body[0]', None, None, {'pars': True}, r"""( # 3
j
# 4
)""", r"""( # 3
j
# 4
)""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value Name 'j' Load - 1,0..1,1
"""),

(r"""( # 1
i
# 2
)""", 'body[0]', None, None, {'raw': False, 'pars': 'auto'}, r"""( # 3
j
# 4
)""", r"""j""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Name 'j' Load - 0,0..0,1
"""),

(r"""( # 1
i
# 2
)""", 'body[0]', None, None, {'pars': False, '_verify': False, 'comment': 'will wind up with wrong unreparsable tuple position'}, r"""a, b""", r"""( # 1
a, b
# 2
)""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Expr - 0,0..3,1
    .value Tuple - 1,0..1,4
      .elts[2]
      0] Name 'a' Load - 1,0..1,1
      1] Name 'b' Load - 1,3..1,4
      .ctx Load
"""),

(r"""( # 1
i
# 2
)""", 'body[0]', None, None, {'raw': False, 'pars': True}, r"""a, b""", r"""(a, b)""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value Tuple - 0,0..0,6
      .elts[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,4..0,5
      .ctx Load
"""),

(r"""( # 1
i
# 2
)""", 'body[0]', None, None, {'raw': False, 'pars': 'auto'}, r"""a, b""", r"""(a, b)""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value Tuple - 0,0..0,6
      .elts[2]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,4..0,5
      .ctx Load
"""),

(r"""(f())""", 'body[0]', None, None, {'pars': False}, r"""g()""", r"""(g())""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Call - 0,1..0,4
      .func Name 'g' Load - 0,1..0,2
"""),

(r"""(f())""", 'body[0]', None, None, {'pars': True}, r"""g()""", r"""g()""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value Call - 0,0..0,3
      .func Name 'g' Load - 0,0..0,1
"""),

(r"""(f())""", 'body[0]', None, None, {'pars': False}, r"""(g())""", r"""((g()))""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Call - 0,2..0,5
      .func Name 'g' Load - 0,2..0,3
"""),

(r"""(f())""", 'body[0]', None, None, {'pars': True}, r"""(g())""", r"""(g())""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Call - 0,1..0,4
      .func Name 'g' Load - 0,1..0,2
"""),

(r"""i += j""", 'body[0]', None, None, {'raw': False}, r"""a, b""", r"""i += (a, b)""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] AugAssign - 0,0..0,11
    .target Name 'i' Store - 0,0..0,1
    .op Add - 0,2..0,4
    .value Tuple - 0,5..0,11
      .elts[2]
      0] Name 'a' Load - 0,6..0,7
      1] Name 'b' Load - 0,9..0,10
      .ctx Load
"""),

(r"""for i in j: pass""", 'body[0]', None, 'iter', {'raw': False}, r"""a, b""", r"""for i in (a, b): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] For - 0,0..0,21
    .target Name 'i' Store - 0,4..0,5
    .iter Tuple - 0,9..0,15
      .elts[2]
      0] Name 'a' Load - 0,10..0,11
      1] Name 'b' Load - 0,13..0,14
      .ctx Load
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""async for i in j: pass""", 'body[0]', None, 'iter', {'raw': False}, r"""a, b""", r"""async for i in (a, b): pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] AsyncFor - 0,0..0,27
    .target Name 'i' Store - 0,10..0,11
    .iter Tuple - 0,15..0,21
      .elts[2]
      0] Name 'a' Load - 0,16..0,17
      1] Name 'b' Load - 0,19..0,20
      .ctx Load
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""while i: pass""", 'body[0]', None, 'test', {'raw': False}, r"""a, b""", r"""while (a, b): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] While - 0,0..0,18
    .test Tuple - 0,6..0,12
      .elts[2]
      0] Name 'a' Load - 0,7..0,8
      1] Name 'b' Load - 0,10..0,11
      .ctx Load
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""if i: pass""", 'body[0]', None, 'test', {'raw': False}, r"""a, b""", r"""if (a, b): pass""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] If - 0,0..0,15
    .test Tuple - 0,3..0,9
      .elts[2]
      0] Name 'a' Load - 0,4..0,5
      1] Name 'b' Load - 0,7..0,8
      .ctx Load
    .body[1]
    0] Pass - 0,11..0,15
"""),

(r"""match i:
  case 1: pass""", 'body[0]', None, 'subject', {'raw': False}, r"""a, b""", r"""match (a, b):
  case 1: pass""", r"""
Module - ROOT 0,0..1,14
  .body[1]
  0] Match - 0,0..1,14
    .subject Tuple - 0,6..0,12
      .elts[2]
      0] Name 'a' Load - 0,7..0,8
      1] Name 'b' Load - 0,10..0,11
      .ctx Load
    .cases[1]
    0] match_case - 1,2..1,14
      .pattern MatchValue - 1,7..1,8
        .value Constant 1 - 1,7..1,8
      .body[1]
      0] Pass - 1,10..1,14
"""),

(r"""assert i""", 'body[0]', None, None, {'raw': False}, r"""a, b""", r"""assert (a, b)""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Assert - 0,0..0,13
    .test Tuple - 0,7..0,13
      .elts[2]
      0] Name 'a' Load - 0,8..0,9
      1] Name 'b' Load - 0,11..0,12
      .ctx Load
"""),

(r"""(i := j)""", 'body[0].value', None, None, {'raw': False}, r"""a, b""", r"""(i := (a, b))""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Expr - 0,0..0,13
    .value NamedExpr - 0,1..0,12
      .target Name 'i' Store - 0,1..0,2
      .value Tuple - 0,6..0,12
        .elts[2]
        0] Name 'a' Load - 0,7..0,8
        1] Name 'b' Load - 0,10..0,11
        .ctx Load
"""),

(r"""i * j""", 'body[0].value', None, 'left', {'raw': False}, r"""a + b""", r"""(a + b) * j""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value BinOp - 0,0..0,11
      .left BinOp - 0,1..0,6
        .left Name 'a' Load - 0,1..0,2
        .op Add - 0,3..0,4
        .right Name 'b' Load - 0,5..0,6
      .op Mult - 0,8..0,9
      .right Name 'j' Load - 0,10..0,11
"""),

(r"""i * j""", 'body[0].value', None, 'right', {'raw': False}, r"""a + b""", r"""i * (a + b)""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value BinOp - 0,0..0,11
      .left Name 'i' Load - 0,0..0,1
      .op Mult - 0,2..0,3
      .right BinOp - 0,5..0,10
        .left Name 'a' Load - 0,5..0,6
        .op Add - 0,7..0,8
        .right Name 'b' Load - 0,9..0,10
"""),

(r"""-i""", 'body[0].value', None, None, {'raw': False}, r"""a + b""", r"""-(a + b)""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value UnaryOp - 0,0..0,8
      .op USub - 0,0..0,1
      .operand BinOp - 0,2..0,7
        .left Name 'a' Load - 0,2..0,3
        .op Add - 0,4..0,5
        .right Name 'b' Load - 0,6..0,7
"""),

(r"""lambda: i""", 'body[0].value', None, None, {'raw': False}, r"""a, b""", r"""lambda: (a, b)""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Expr - 0,0..0,14
    .value Lambda - 0,0..0,14
      .body Tuple - 0,8..0,14
        .elts[2]
        0] Name 'a' Load - 0,9..0,10
        1] Name 'b' Load - 0,12..0,13
        .ctx Load
"""),

(r"""i if j else k""", 'body[0].value', None, 'body', {'raw': False}, r"""a if b else c""", r"""(a if b else c) if j else k""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] Expr - 0,0..0,27
    .value IfExp - 0,0..0,27
      .test Name 'j' Load - 0,19..0,20
      .body IfExp - 0,1..0,14
        .test Name 'b' Load - 0,6..0,7
        .body Name 'a' Load - 0,1..0,2
        .orelse Name 'c' Load - 0,13..0,14
      .orelse Name 'k' Load - 0,26..0,27
"""),

(r"""i if j else k""", 'body[0].value', None, 'test', {'raw': False}, r"""a if b else c""", r"""i if (a if b else c) else k""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] Expr - 0,0..0,27
    .value IfExp - 0,0..0,27
      .test IfExp - 0,6..0,19
        .test Name 'b' Load - 0,11..0,12
        .body Name 'a' Load - 0,6..0,7
        .orelse Name 'c' Load - 0,18..0,19
      .body Name 'i' Load - 0,0..0,1
      .orelse Name 'k' Load - 0,26..0,27
"""),

(r"""i if j else k""", 'body[0].value', None, 'orelse', {}, r"""a if b else c""", r"""i if j else a if b else c""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] Expr - 0,0..0,25
    .value IfExp - 0,0..0,25
      .test Name 'j' Load - 0,5..0,6
      .body Name 'i' Load - 0,0..0,1
      .orelse IfExp - 0,12..0,25
        .test Name 'b' Load - 0,17..0,18
        .body Name 'a' Load - 0,12..0,13
        .orelse Name 'c' Load - 0,24..0,25
"""),

(r"""[i for i in j]""", 'body[0].value', None, 'elt', {'raw': False}, r"""a, b""", r"""[(a, b) for i in j]""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] Expr - 0,0..0,19
    .value ListComp - 0,0..0,19
      .elt Tuple - 0,1..0,7
        .elts[2]
        0] Name 'a' Load - 0,2..0,3
        1] Name 'b' Load - 0,5..0,6
        .ctx Load
      .generators[1]
      0] comprehension - 0,8..0,18
        .target Name 'i' Store - 0,12..0,13
        .iter Name 'j' Load - 0,17..0,18
        .is_async 0
"""),

(r"""{i for i in j}""", 'body[0].value', None, 'elt', {'raw': False}, r"""a, b""", r"""{(a, b) for i in j}""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] Expr - 0,0..0,19
    .value SetComp - 0,0..0,19
      .elt Tuple - 0,1..0,7
        .elts[2]
        0] Name 'a' Load - 0,2..0,3
        1] Name 'b' Load - 0,5..0,6
        .ctx Load
      .generators[1]
      0] comprehension - 0,8..0,18
        .target Name 'i' Store - 0,12..0,13
        .iter Name 'j' Load - 0,17..0,18
        .is_async 0
"""),

(r"""{k: v for i in j}""", 'body[0].value', None, 'key', {'raw': False}, r"""a, b""", r"""{(a, b): v for i in j}""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value DictComp - 0,0..0,22
      .key Tuple - 0,1..0,7
        .elts[2]
        0] Name 'a' Load - 0,2..0,3
        1] Name 'b' Load - 0,5..0,6
        .ctx Load
      .value Name 'v' Load - 0,9..0,10
      .generators[1]
      0] comprehension - 0,11..0,21
        .target Name 'i' Store - 0,15..0,16
        .iter Name 'j' Load - 0,20..0,21
        .is_async 0
"""),

(r"""{k: v for i in j}""", 'body[0].value', None, 'value', {'raw': False}, r"""a, b""", r"""{k: (a, b) for i in j}""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value DictComp - 0,0..0,22
      .key Name 'k' Load - 0,1..0,2
      .value Tuple - 0,4..0,10
        .elts[2]
        0] Name 'a' Load - 0,5..0,6
        1] Name 'b' Load - 0,8..0,9
        .ctx Load
      .generators[1]
      0] comprehension - 0,11..0,21
        .target Name 'i' Store - 0,15..0,16
        .iter Name 'j' Load - 0,20..0,21
        .is_async 0
"""),

(r"""(i for i in j)""", 'body[0].value', None, 'elt', {'raw': False}, r"""a, b""", r"""((a, b) for i in j)""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] Expr - 0,0..0,19
    .value GeneratorExp - 0,0..0,19
      .elt Tuple - 0,1..0,7
        .elts[2]
        0] Name 'a' Load - 0,2..0,3
        1] Name 'b' Load - 0,5..0,6
        .ctx Load
      .generators[1]
      0] comprehension - 0,8..0,18
        .target Name 'i' Store - 0,12..0,13
        .iter Name 'j' Load - 0,17..0,18
        .is_async 0
"""),

(r"""await i""", 'body[0].value', None, None, {'raw': False}, r"""a, b""", r"""await (a, b)""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Expr - 0,0..0,12
    .value Await - 0,0..0,12
      .value Tuple - 0,6..0,12
        .elts[2]
        0] Name 'a' Load - 0,7..0,8
        1] Name 'b' Load - 0,10..0,11
        .ctx Load
"""),

(r"""yield from i""", 'body[0].value', None, None, {'raw': False}, r"""a, b""", r"""yield from (a, b)""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value YieldFrom - 0,0..0,17
      .value Tuple - 0,11..0,17
        .elts[2]
        0] Name 'a' Load - 0,12..0,13
        1] Name 'b' Load - 0,15..0,16
        .ctx Load
"""),

(r"""f'{i}'""", 'body[0].value.values[0]', None, None, {'raw': False, '_verdump': 12}, r"""a, b""", r"""f'{(a, b)}'""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value JoinedStr - 0,0..0,11
      .values[1]
      0] FormattedValue - 0,2..0,10
        .value Tuple - 0,3..0,9
          .elts[2]
          0] Name 'a' Load - 0,4..0,5
          1] Name 'b' Load - 0,7..0,8
          .ctx Load
        .conversion -1
"""),

(r"""t'{i}'""", 'body[0].value.values[0]', None, None, {'raw': False, '_ver': 14}, r"""a, b""", r"""t'{(a, b)}'""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value TemplateStr - 0,0..0,11
      .values[1]
      0] Interpolation - 0,2..0,10
        .value Tuple - 0,3..0,9
          .elts[2]
          0] Name 'a' Load - 0,4..0,5
          1] Name 'b' Load - 0,7..0,8
          .ctx Load
        .str '(a, b)'
        .conversion -1
"""),

(r"""i.j""", 'body[0].value', None, None, {'raw': False}, r"""a, b""", r"""(a, b).j""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Attribute - 0,0..0,8
      .value Tuple - 0,0..0,6
        .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
        .ctx Load
      .attr 'j'
      .ctx Load
"""),

(r"""i[j]""", 'body[0].value', None, None, {'raw': False}, r"""a, b""", r"""(a, b)[j]""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Subscript - 0,0..0,9
      .value Tuple - 0,0..0,6
        .elts[2]
        0] Name 'a' Load - 0,1..0,2
        1] Name 'b' Load - 0,4..0,5
        .ctx Load
      .slice Name 'j' Load - 0,7..0,8
      .ctx Load
"""),

(r"""i[j]""", 'body[0].value', None, 'slice', {}, r"""a, b""", r"""i[a, b]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'i' Load - 0,0..0,1
      .slice Tuple - 0,2..0,6
        .elts[2]
        0] Name 'a' Load - 0,2..0,3
        1] Name 'b' Load - 0,5..0,6
        .ctx Load
      .ctx Load
"""),

(r"""i[j]""", 'body[0].value', None, 'slice', {}, r"""x:y:z""", r"""i[x:y:z]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'i' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .lower Name 'x' Load - 0,2..0,3
        .upper Name 'y' Load - 0,4..0,5
        .step Name 'z' Load - 0,6..0,7
      .ctx Load
"""),

(r"""i[a:b:c]""", 'body[0].value', None, 'slice', {}, r"""a, b""", r"""i[a, b]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'i' Load - 0,0..0,1
      .slice Tuple - 0,2..0,6
        .elts[2]
        0] Name 'a' Load - 0,2..0,3
        1] Name 'b' Load - 0,5..0,6
        .ctx Load
      .ctx Load
"""),

(r"""i[a:b:c]""", 'body[0].value', None, 'slice', {}, r"""z""", r"""i[z]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'i' Load - 0,0..0,1
      .slice Name 'z' Load - 0,2..0,3
      .ctx Load
"""),

(r"""[*i]""", 'body[0].value.elts[0]', None, None, {'raw': False}, r"""a, b""", r"""[*(a, b)]""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value List - 0,0..0,9
      .elts[1]
      0] Starred - 0,1..0,8
        .value Tuple - 0,2..0,8
          .elts[2]
          0] Name 'a' Load - 0,3..0,4
          1] Name 'b' Load - 0,6..0,7
          .ctx Load
        .ctx Load
      .ctx Load
"""),

(r"""[i for i in j]""", 'body[0].value.generators[0]', None, 'iter', {'raw': False}, r"""a, b""", r"""[i for i in (a, b)]""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] Expr - 0,0..0,19
    .value ListComp - 0,0..0,19
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,18
        .target Name 'i' Store - 0,7..0,8
        .iter Tuple - 0,12..0,18
          .elts[2]
          0] Name 'a' Load - 0,13..0,14
          1] Name 'b' Load - 0,16..0,17
          .ctx Load
        .is_async 0
"""),

(r"""[i for i in j]""", 'body[0].value.generators[0]', None, 'iter', {'raw': False}, r"""a, b""", r"""[i for i in (a, b)]""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] Expr - 0,0..0,19
    .value ListComp - 0,0..0,19
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,18
        .target Name 'i' Store - 0,7..0,8
        .iter Tuple - 0,12..0,18
          .elts[2]
          0] Name 'a' Load - 0,13..0,14
          1] Name 'b' Load - 0,16..0,17
          .ctx Load
        .is_async 0
"""),

(r"""f(i=j)""", 'body[0].value.keywords[0]', None, None, {'raw': False}, r"""a, b""", r"""f(i=(a, b))""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Call - 0,0..0,11
      .func Name 'f' Load - 0,0..0,1
      .keywords[1]
      0] keyword - 0,2..0,10
        .arg 'i'
        .value Tuple - 0,4..0,10
          .elts[2]
          0] Name 'a' Load - 0,5..0,6
          1] Name 'b' Load - 0,8..0,9
          .ctx Load
"""),

(r"""class cls(i=j): pass""", 'body[0].keywords[0]', None, None, {'raw': False}, r"""a, b""", r"""class cls(i=(a, b)): pass""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] ClassDef - 0,0..0,25
    .name 'cls'
    .keywords[1]
    0] keyword - 0,10..0,18
      .arg 'i'
      .value Tuple - 0,12..0,18
        .elts[2]
        0] Name 'a' Load - 0,13..0,14
        1] Name 'b' Load - 0,16..0,17
        .ctx Load
    .body[1]
    0] Pass - 0,21..0,25
"""),

(r"""with i as j: pass""", 'body[0].items[0]', None, None, {'raw': False}, r"""a, b""", r"""with (a, b) as j: pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] With - 0,0..0,22
    .items[1]
    0] withitem - 0,5..0,16
      .context_expr Tuple - 0,5..0,11
        .elts[2]
        0] Name 'a' Load - 0,6..0,7
        1] Name 'b' Load - 0,9..0,10
        .ctx Load
      .optional_vars Name 'j' Store - 0,15..0,16
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""with i: pass""", 'body[0].items[0]', None, None, {'raw': False}, r"""a, b""", r"""with ((a, b)): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] With - 0,0..0,19
    .items[1]
    0] withitem - 0,5..0,13
      .context_expr Tuple - 0,6..0,12
        .elts[2]
        0] Name 'a' Load - 0,7..0,8
        1] Name 'b' Load - 0,10..0,11
        .ctx Load
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""def oldname(): pass""", 'body[0]', None, 'name', {}, r"""**DEL**""", r"""**ValueError('cannot delete FunctionDef.name')**""", r"""
"""),

(r"""def oldname(): pass""", 'body[0]', None, 'name', {}, r"""new""", r"""def new(): pass""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] FunctionDef - 0,0..0,15
    .name 'new'
    .body[1]
    0] Pass - 0,11..0,15
"""),

(r"""async def oldname(): pass""", 'body[0]', None, 'name', {}, r"""new""", r"""async def new(): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] AsyncFunctionDef - 0,0..0,21
    .name 'new'
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""class oldname: pass""", 'body[0]', None, 'name', {}, r"""new""", r"""class new: pass""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] ClassDef - 0,0..0,15
    .name 'new'
    .body[1]
    0] Pass - 0,11..0,15
"""),

(r"""oldname""", 'body[0].value', None, 'id', {}, r"""new""", r"""new""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value Name 'new' Load - 0,0..0,3
"""),

(r"""def f(oldarg=val): pass""", 'body[0].args.args[0]', None, 'arg', {}, r"""new""", r"""def f(new=val): pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] FunctionDef - 0,0..0,20
    .name 'f'
    .args arguments - 0,6..0,13
      .args[1]
      0] arg - 0,6..0,9
        .arg 'new'
      .defaults[1]
      0] Name 'val' Load - 0,10..0,13
    .body[1]
    0] Pass - 0,16..0,20
"""),

(r"""import oldname as thing""", 'body[0].names[0]', None, 'name', {}, r"""new""", r"""import new as thing""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] Import - 0,0..0,19
    .names[1]
    0] alias - 0,7..0,19
      .name 'new'
      .asname
        'thing'
"""),

(r"""def f[T](): pass""", 'body[0].type_params[0]', None, 'name', {'_ver': 12}, r"""new""", r"""def f[new](): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] FunctionDef - 0,0..0,18
    .name 'f'
    .body[1]
    0] Pass - 0,14..0,18
    .type_params[1]
    0] TypeVar - 0,6..0,9
      .name 'new'
"""),

(r"""def f[*T](): pass""", 'body[0].type_params[0]', None, 'name', {'_ver': 12}, r"""new""", r"""def f[*new](): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] FunctionDef - 0,0..0,19
    .name 'f'
    .body[1]
    0] Pass - 0,15..0,19
    .type_params[1]
    0] TypeVarTuple - 0,6..0,10
      .name 'new'
"""),

(r"""def f[**T](): pass""", 'body[0].type_params[0]', None, 'name', {'_ver': 12}, r"""new""", r"""def f[**new](): pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] FunctionDef - 0,0..0,20
    .name 'f'
    .body[1]
    0] Pass - 0,16..0,20
    .type_params[1]
    0] ParamSpec - 0,6..0,11
      .name 'new'
"""),

(r"""i += j""", 'body[0]', None, 'target', {}, r"""1""", r"""**NodeError('expecting one of (Name, Attribute, Subscript) for AugAssign.target, got Constant')**""", r"""
"""),

(r"""i += j""", 'body[0]', None, 'target', {}, r"""new""", r"""new += j""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] AugAssign - 0,0..0,8
    .target Name 'new' Store - 0,0..0,3
    .op Add - 0,4..0,6
    .value Name 'j' Load - 0,7..0,8
"""),

(r"""i += j""", 'body[0]', None, 'target', {}, r"""new.to""", r"""new.to += j""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] AugAssign - 0,0..0,11
    .target Attribute - 0,0..0,6
      .value Name 'new' Load - 0,0..0,3
      .attr 'to'
      .ctx Store
    .op Add - 0,7..0,9
    .value Name 'j' Load - 0,10..0,11
"""),

(r"""i += j""", 'body[0]', None, 'target', {}, r"""new[to]""", r"""new[to] += j""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] AugAssign - 0,0..0,12
    .target Subscript - 0,0..0,7
      .value Name 'new' Load - 0,0..0,3
      .slice Name 'to' Load - 0,4..0,6
      .ctx Store
    .op Add - 0,8..0,10
    .value Name 'j' Load - 0,11..0,12
"""),

(r"""i: j = 1""", 'body[0]', None, 'target', {}, r"""new""", r"""new: j = 1""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] AnnAssign - 0,0..0,10
    .target Name 'new' Store - 0,0..0,3
    .annotation Name 'j' Load - 0,5..0,6
    .value Constant 1 - 0,9..0,10
    .simple 1
"""),

(r"""i: j""", 'body[0]', None, 'target', {}, r"""new""", r"""new: j""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] AnnAssign - 0,0..0,6
    .target Name 'new' Store - 0,0..0,3
    .annotation Name 'j' Load - 0,5..0,6
    .simple 1
"""),

(r"""i: j""", 'body[0]', None, 'annotation', {}, r"""(yield 1)""", r"""i: (yield 1)""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] AnnAssign - 0,0..0,12
    .target Name 'i' Store - 0,0..0,1
    .annotation Yield - 0,4..0,11
      .value Constant 1 - 0,10..0,11
    .simple 1
"""),

(r"""i: j""", 'body[0]', None, 'annotation', {}, r"""new""", r"""i: new""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] AnnAssign - 0,0..0,6
    .target Name 'i' Store - 0,0..0,1
    .annotation Name 'new' Load - 0,3..0,6
    .simple 1
"""),

(r"""for i in j: pass""", 'body[0]', None, 'target', {}, r"""new""", r"""for new in j: pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] For - 0,0..0,18
    .target Name 'new' Store - 0,4..0,7
    .iter Name 'j' Load - 0,11..0,12
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""for i in j: pass""", 'body[0]', None, 'target', {}, r"""(new, to)""", r"""for (new, to) in j: pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] For - 0,0..0,24
    .target Tuple - 0,4..0,13
      .elts[2]
      0] Name 'new' Store - 0,5..0,8
      1] Name 'to' Store - 0,10..0,12
      .ctx Store
    .iter Name 'j' Load - 0,17..0,18
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""for i in j: pass""", 'body[0]', None, 'target', {}, r"""[new, to]""", r"""for [new, to] in j: pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] For - 0,0..0,24
    .target List - 0,4..0,13
      .elts[2]
      0] Name 'new' Store - 0,5..0,8
      1] Name 'to' Store - 0,10..0,12
      .ctx Store
    .iter Name 'j' Load - 0,17..0,18
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""(i := j)""", 'body[0].value', None, 'target', {}, r"""1""", r"""**NodeError('expecting a Name for NamedExpr.target, got Constant')**""", r"""
"""),

(r"""(i := j)""", 'body[0].value', None, 'target', {}, r"""new""", r"""(new := j)""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value NamedExpr - 0,1..0,9
      .target Name 'new' Store - 0,1..0,4
      .value Name 'j' Load - 0,8..0,9
"""),

(r"""[i for i in j]""", 'body[0].value.generators[0]', None, 'target', {}, r"""new""", r"""[i for new in j]""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] Expr - 0,0..0,16
    .value ListComp - 0,0..0,16
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,15
        .target Name 'new' Store - 0,7..0,10
        .iter Name 'j' Load - 0,14..0,15
        .is_async 0
"""),

(r"""[i for i in j]""", 'body[0].value.generators[0]', None, 'target', {}, r"""(new, to)""", r"""[i for (new, to) in j]""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value ListComp - 0,0..0,22
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,21
        .target Tuple - 0,7..0,16
          .elts[2]
          0] Name 'new' Store - 0,8..0,11
          1] Name 'to' Store - 0,13..0,15
          .ctx Store
        .iter Name 'j' Load - 0,20..0,21
        .is_async 0
"""),

(r"""[i for i in j]""", 'body[0].value.generators[0]', None, 'target', {}, r"""[new, to]""", r"""[i for [new, to] in j]""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value ListComp - 0,0..0,22
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,21
        .target List - 0,7..0,16
          .elts[2]
          0] Name 'new' Store - 0,8..0,11
          1] Name 'to' Store - 0,13..0,15
          .ctx Store
        .iter Name 'j' Load - 0,20..0,21
        .is_async 0
"""),

(r"""type i = j""", 'body[0]', None, 'name', {'_ver': 12}, r"""1""", r"""**NodeError('expecting a Name for TypeAlias.name, got Constant')**""", r"""
"""),

(r"""type i = j""", 'body[0]', None, 'name', {'_ver': 12}, r"""new""", r"""type new = j""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] TypeAlias - 0,0..0,12
    .name Name 'new' Store - 0,5..0,8
    .value Name 'j' Load - 0,11..0,12
"""),

(r"""type i = j""", 'body[0]', None, None, {'_ver': 12}, r"""new""", r"""type i = new""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] TypeAlias - 0,0..0,12
    .name Name 'i' Store - 0,5..0,6
    .value Name 'new' Load - 0,9..0,12
"""),

(r"""i < j""", 'body[0].value', None, 'left', {'raw': False}, r"""new, to""", r"""(new, to) < j""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Expr - 0,0..0,13
    .value Compare - 0,0..0,13
      .left Tuple - 0,0..0,9
        .elts[2]
        0] Name 'new' Load - 0,1..0,4
        1] Name 'to' Load - 0,6..0,8
        .ctx Load
      .ops[1]
      0] Lt - 0,10..0,11
      .comparators[1]
      0] Name 'j' Load - 0,12..0,13
"""),

(r"""call()""", 'body[0].value', None, 'func', {'raw': False}, r"""new, to""", r"""(new, to)()""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Call - 0,0..0,11
      .func Tuple - 0,0..0,9
        .elts[2]
        0] Name 'new' Load - 0,1..0,4
        1] Name 'to' Load - 0,6..0,8
        .ctx Load
"""),

(r"""match a:
 case c(): pass""", 'body[0].cases[0].pattern', None, 'cls', {'raw': False}, r"""new, to""", r"""**NodeError('cannot put Tuple to pattern expression')**""", r"""
"""),

(r"""match a:
 case c(): pass""", 'body[0].cases[0].pattern', None, 'cls', {}, r"""new""", r"""match a:
 case new(): pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchClass - 1,6..1,11
        .cls Name 'new' Load - 1,6..1,9
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case c(): pass""", 'body[0].cases[0].pattern', None, 'cls', {}, r"""new.to""", r"""match a:
 case new.to(): pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchClass - 1,6..1,14
        .cls Attribute - 1,6..1,12
          .value Name 'new' Load - 1,6..1,9
          .attr 'to'
          .ctx Load
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""{i: j}""", 'body[0].value', 0, 'keys', {'raw': False}, r"""yield 1""", r"""{(yield 1): j}""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Expr - 0,0..0,14
    .value Dict - 0,0..0,14
      .keys[1]
      0] Yield - 0,2..0,9
        .value Constant 1 - 0,8..0,9
      .values[1]
      0] Name 'j' Load - 0,12..0,13
"""),

(r"""{i: j}""", 'body[0].value', 0, 'values', {'raw': False}, r"""yield 1""", r"""{i: (yield 1)}""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Expr - 0,0..0,14
    .value Dict - 0,0..0,14
      .keys[1]
      0] Name 'i' Load - 0,1..0,2
      .values[1]
      0] Yield - 0,5..0,12
        .value Constant 1 - 0,11..0,12
"""),

(r"""{**i}""", 'body[0].value', 0, 'keys', {'raw': False}, r"""yield 1""", r"""{(yield 1): i}""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Expr - 0,0..0,14
    .value Dict - 0,0..0,14
      .keys[1]
      0] Yield - 0,2..0,9
        .value Constant 1 - 0,8..0,9
      .values[1]
      0] Name 'i' Load - 0,12..0,13
"""),

(r"""{(yield 1): i}""", 'body[0].value', 0, 'keys', {}, r"""**DEL**""", r"""{**i}""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Dict - 0,0..0,5
      .keys[1]
      0] None
      .values[1]
      0] Name 'i' Load - 0,3..0,4
"""),

(r"""a < b""", 'body[0].value', 0, 'comparators', {'raw': False}, r"""yield 1""", r"""a < (yield 1)""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Expr - 0,0..0,13
    .value Compare - 0,0..0,13
      .left Name 'a' Load - 0,0..0,1
      .ops[1]
      0] Lt - 0,2..0,3
      .comparators[1]
      0] Yield - 0,5..0,12
        .value Constant 1 - 0,11..0,12
"""),

(r"""a < b < c""", 'body[0].value', 0, None, {'raw': False}, r"""yield 1""", r"""(yield 1) < b < c""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Compare - 0,0..0,17
      .left Yield - 0,1..0,8
        .value Constant 1 - 0,7..0,8
      .ops[2]
      0] Lt - 0,10..0,11
      1] Lt - 0,14..0,15
      .comparators[2]
      0] Name 'b' Load - 0,12..0,13
      1] Name 'c' Load - 0,16..0,17
"""),

(r"""a < b < c""", 'body[0].value', 1, None, {'raw': False}, r"""yield 1""", r"""a < (yield 1) < c""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Compare - 0,0..0,17
      .left Name 'a' Load - 0,0..0,1
      .ops[2]
      0] Lt - 0,2..0,3
      1] Lt - 0,14..0,15
      .comparators[2]
      0] Yield - 0,5..0,12
        .value Constant 1 - 0,11..0,12
      1] Name 'c' Load - 0,16..0,17
"""),

(r"""a < b < c""", 'body[0].value', 2, None, {'raw': False}, r"""yield 1""", r"""a < b < (yield 1)""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Compare - 0,0..0,17
      .left Name 'a' Load - 0,0..0,1
      .ops[2]
      0] Lt - 0,2..0,3
      1] Lt - 0,6..0,7
      .comparators[2]
      0] Name 'b' Load - 0,4..0,5
      1] Yield - 0,9..0,16
        .value Constant 1 - 0,15..0,16
"""),

(r"""a < b < c""", 'body[0].value', 3, None, {}, r"""yield 1""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""a < b < c""", 'body[0].value', -1, None, {'raw': False}, r"""yield 1""", r"""a < b < (yield 1)""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Compare - 0,0..0,17
      .left Name 'a' Load - 0,0..0,1
      .ops[2]
      0] Lt - 0,2..0,3
      1] Lt - 0,6..0,7
      .comparators[2]
      0] Name 'b' Load - 0,4..0,5
      1] Yield - 0,9..0,16
        .value Constant 1 - 0,15..0,16
"""),

(r"""a < b < c""", 'body[0].value', -2, None, {'raw': False}, r"""yield 1""", r"""a < (yield 1) < c""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Compare - 0,0..0,17
      .left Name 'a' Load - 0,0..0,1
      .ops[2]
      0] Lt - 0,2..0,3
      1] Lt - 0,14..0,15
      .comparators[2]
      0] Yield - 0,5..0,12
        .value Constant 1 - 0,11..0,12
      1] Name 'c' Load - 0,16..0,17
"""),

(r"""a < b < c""", 'body[0].value', -3, None, {'raw': False}, r"""yield 1""", r"""(yield 1) < b < c""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Compare - 0,0..0,17
      .left Yield - 0,1..0,8
        .value Constant 1 - 0,7..0,8
      .ops[2]
      0] Lt - 0,10..0,11
      1] Lt - 0,14..0,15
      .comparators[2]
      0] Name 'b' Load - 0,12..0,13
      1] Name 'c' Load - 0,16..0,17
"""),

(r"""a < b < c""", 'body[0].value', -4, None, {}, r"""yield 1""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""def f(a, b=1, c=2): pass""", 'body[0].args', 0, 'defaults', {'raw': False}, r"""yield 1""", r"""def f(a, b=(yield 1), c=2): pass""", r"""
Module - ROOT 0,0..0,32
  .body[1]
  0] FunctionDef - 0,0..0,32
    .name 'f'
    .args arguments - 0,6..0,25
      .args[3]
      0] arg - 0,6..0,7
        .arg 'a'
      1] arg - 0,9..0,10
        .arg 'b'
      2] arg - 0,22..0,23
        .arg 'c'
      .defaults[2]
      0] Yield - 0,12..0,19
        .value Constant 1 - 0,18..0,19
      1] Constant 2 - 0,24..0,25
    .body[1]
    0] Pass - 0,28..0,32
"""),

(r"""match a:
 case {1: i}: pass""", 'body[0].cases[0].pattern', 0, 'keys', {}, r"""a.b""", r"""match a:
 case {a.b: i}: pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchMapping - 1,6..1,14
        .keys[1]
        0] Attribute - 1,7..1,10
          .value Name 'a' Load - 1,7..1,8
          .attr 'b'
          .ctx Load
        .patterns[1]
        0] MatchAs - 1,12..1,13
          .name 'i'
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""return a""", 'body[0]', None, None, {}, r"""new""", r"""return new""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Return - 0,0..0,10
    .value Name 'new' Load - 0,7..0,10
"""),

(r"""return (a)""", 'body[0]', None, None, {}, r"""new""", r"""return new""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Return - 0,0..0,10
    .value Name 'new' Load - 0,7..0,10
"""),

(r"""return a""", 'body[0]', None, None, {}, r"""**DEL**""", r"""return""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Return - 0,0..0,6
"""),

(r"""return (a)""", 'body[0]', None, None, {}, r"""**DEL**""", r"""return""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Return - 0,0..0,6
"""),

(r"""return""", 'body[0]', None, None, {}, r"""**DEL**""", r"""return""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Return - 0,0..0,6
"""),

(r"""return""", 'body[0]', None, None, {}, r"""new""", r"""return new""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Return - 0,0..0,10
    .value Name 'new' Load - 0,7..0,10
"""),

(r"""a: b = c""", 'body[0]', None, None, {}, r"""new""", r"""a: b = new""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] AnnAssign - 0,0..0,10
    .target Name 'a' Store - 0,0..0,1
    .annotation Name 'b' Load - 0,3..0,4
    .value Name 'new' Load - 0,7..0,10
    .simple 1
"""),

(r"""a: b = (c)""", 'body[0]', None, None, {}, r"""new""", r"""a: b = new""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] AnnAssign - 0,0..0,10
    .target Name 'a' Store - 0,0..0,1
    .annotation Name 'b' Load - 0,3..0,4
    .value Name 'new' Load - 0,7..0,10
    .simple 1
"""),

(r"""a: b = c""", 'body[0]', None, None, {}, r"""**DEL**""", r"""a: b""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] AnnAssign - 0,0..0,4
    .target Name 'a' Store - 0,0..0,1
    .annotation Name 'b' Load - 0,3..0,4
    .simple 1
"""),

(r"""a: b = (c)""", 'body[0]', None, None, {}, r"""**DEL**""", r"""a: b""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] AnnAssign - 0,0..0,4
    .target Name 'a' Store - 0,0..0,1
    .annotation Name 'b' Load - 0,3..0,4
    .simple 1
"""),

(r"""a: b""", 'body[0]', None, None, {}, r"""**DEL**""", r"""a: b""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] AnnAssign - 0,0..0,4
    .target Name 'a' Store - 0,0..0,1
    .annotation Name 'b' Load - 0,3..0,4
    .simple 1
"""),

(r"""a: b""", 'body[0]', None, None, {}, r"""new""", r"""a: b = new""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] AnnAssign - 0,0..0,10
    .target Name 'a' Store - 0,0..0,1
    .annotation Name 'b' Load - 0,3..0,4
    .value Name 'new' Load - 0,7..0,10
    .simple 1
"""),

(r"""raise e""", 'body[0]', None, None, {}, r"""new""", r"""raise new""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Raise - 0,0..0,9
    .exc Name 'new' Load - 0,6..0,9
"""),

(r"""raise (e)""", 'body[0]', None, None, {}, r"""new""", r"""raise new""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Raise - 0,0..0,9
    .exc Name 'new' Load - 0,6..0,9
"""),

(r"""raise e""", 'body[0]', None, None, {}, r"""**DEL**""", r"""raise""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Raise - 0,0..0,5
"""),

(r"""raise (e)""", 'body[0]', None, None, {}, r"""**DEL**""", r"""raise""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Raise - 0,0..0,5
"""),

(r"""raise e from cause""", 'body[0]', None, None, {}, r"""**DEL**""", r"""**ValueError('cannot delete Raise.exc in this state')**""", r"""
"""),

(r"""raise""", 'body[0]', None, None, {}, r"""**DEL**""", r"""raise""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Raise - 0,0..0,5
"""),

(r"""raise""", 'body[0]', None, None, {}, r"""new""", r"""raise new""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Raise - 0,0..0,9
    .exc Name 'new' Load - 0,6..0,9
"""),

(r"""raise e from cause""", 'body[0]', None, None, {}, r"""new""", r"""raise new from cause""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Raise - 0,0..0,20
    .exc Name 'new' Load - 0,6..0,9
    .cause Name 'cause' Load - 0,15..0,20
"""),

(r"""raise (e) from cause""", 'body[0]', None, None, {}, r"""new""", r"""raise new from cause""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Raise - 0,0..0,20
    .exc Name 'new' Load - 0,6..0,9
    .cause Name 'cause' Load - 0,15..0,20
"""),

(r"""raise e from c""", 'body[0]', None, 'cause', {}, r"""new""", r"""raise e from new""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] Raise - 0,0..0,16
    .exc Name 'e' Load - 0,6..0,7
    .cause Name 'new' Load - 0,13..0,16
"""),

(r"""raise e from (c)""", 'body[0]', None, 'cause', {}, r"""new""", r"""raise e from new""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] Raise - 0,0..0,16
    .exc Name 'e' Load - 0,6..0,7
    .cause Name 'new' Load - 0,13..0,16
"""),

(r"""raise e from c""", 'body[0]', None, 'cause', {}, r"""**DEL**""", r"""raise e""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Raise - 0,0..0,7
    .exc Name 'e' Load - 0,6..0,7
"""),

(r"""raise e from (c)""", 'body[0]', None, 'cause', {}, r"""**DEL**""", r"""raise e""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Raise - 0,0..0,7
    .exc Name 'e' Load - 0,6..0,7
"""),

(r"""raise (e) from c""", 'body[0]', None, 'cause', {}, r"""**DEL**""", r"""raise (e)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Raise - 0,0..0,9
    .exc Name 'e' Load - 0,7..0,8
"""),

(r"""raise""", 'body[0]', None, 'cause', {'raw': False}, r"""**DEL**""", r"""raise""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Raise - 0,0..0,5
"""),

(r"""raise e""", 'body[0]', None, 'cause', {}, r"""**DEL**""", r"""raise e""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Raise - 0,0..0,7
    .exc Name 'e' Load - 0,6..0,7
"""),

(r"""raise""", 'body[0]', None, 'cause', {}, r"""c""", r"""**ValueError('cannot create Raise.cause in this state')**""", r"""
"""),

(r"""raise e""", 'body[0]', None, 'cause', {}, r"""c""", r"""raise e from c""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Raise - 0,0..0,14
    .exc Name 'e' Load - 0,6..0,7
    .cause Name 'c' Load - 0,13..0,14
"""),

(r"""raise (e)""", 'body[0]', None, 'cause', {}, r"""c""", r"""raise (e) from c""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] Raise - 0,0..0,16
    .exc Name 'e' Load - 0,7..0,8
    .cause Name 'c' Load - 0,15..0,16
"""),

(r"""assert a, b""", 'body[0]', None, None, {}, r"""new""", r"""assert new, b""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Assert - 0,0..0,13
    .test Name 'new' Load - 0,7..0,10
    .msg Name 'b' Load - 0,12..0,13
"""),

(r"""assert a, (b)""", 'body[0]', None, None, {}, r"""new""", r"""assert new, (b)""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Assert - 0,0..0,15
    .test Name 'new' Load - 0,7..0,10
    .msg Name 'b' Load - 0,13..0,14
"""),

(r"""assert a, b""", 'body[0]', None, None, {}, r"""**DEL**""", r"""**ValueError('cannot delete Assert.test')**""", r"""
"""),

(r"""assert a, b""", 'body[0]', None, 'msg', {}, r"""new""", r"""assert a, new""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Assert - 0,0..0,13
    .test Name 'a' Load - 0,7..0,8
    .msg Name 'new' Load - 0,10..0,13
"""),

(r"""assert a, (b)""", 'body[0]', None, 'msg', {}, r"""new""", r"""assert a, new""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Assert - 0,0..0,13
    .test Name 'a' Load - 0,7..0,8
    .msg Name 'new' Load - 0,10..0,13
"""),

(r"""assert a, b""", 'body[0]', None, 'msg', {}, r"""**DEL**""", r"""assert a""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Assert - 0,0..0,8
    .test Name 'a' Load - 0,7..0,8
"""),

(r"""assert a, (b)""", 'body[0]', None, 'msg', {}, r"""**DEL**""", r"""assert a""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Assert - 0,0..0,8
    .test Name 'a' Load - 0,7..0,8
"""),

(r"""assert a""", 'body[0]', None, 'msg', {}, r"""**DEL**""", r"""assert a""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Assert - 0,0..0,8
    .test Name 'a' Load - 0,7..0,8
"""),

(r"""assert a""", 'body[0]', None, 'msg', {}, r"""new""", r"""assert a, new""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Assert - 0,0..0,13
    .test Name 'a' Load - 0,7..0,8
    .msg Name 'new' Load - 0,10..0,13
"""),

(r"""yield a""", 'body[0].value', None, None, {}, r"""new""", r"""yield new""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Yield - 0,0..0,9
      .value Name 'new' Load - 0,6..0,9
"""),

(r"""yield (a)""", 'body[0].value', None, None, {}, r"""new""", r"""yield new""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Yield - 0,0..0,9
      .value Name 'new' Load - 0,6..0,9
"""),

(r"""yield a""", 'body[0].value', None, None, {}, r"""**DEL**""", r"""yield""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Yield - 0,0..0,5
"""),

(r"""yield (a)""", 'body[0].value', None, None, {}, r"""**DEL**""", r"""yield""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Yield - 0,0..0,5
"""),

(r"""yield""", 'body[0].value', None, None, {}, r"""**DEL**""", r"""yield""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Yield - 0,0..0,5
"""),

(r"""yield""", 'body[0].value', None, None, {}, r"""new""", r"""yield new""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Yield - 0,0..0,9
      .value Name 'new' Load - 0,6..0,9
"""),

(r"""def f(a: b): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""new""", r"""def f(a: new): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] FunctionDef - 0,0..0,19
    .name 'f'
    .args arguments - 0,6..0,12
      .args[1]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'new' Load - 0,9..0,12
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""def f(a: (b)): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""new""", r"""def f(a: new): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] FunctionDef - 0,0..0,19
    .name 'f'
    .args arguments - 0,6..0,12
      .args[1]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'new' Load - 0,9..0,12
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""def f(a: b): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""**DEL**""", r"""def f(a): pass""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] FunctionDef - 0,0..0,14
    .name 'f'
    .args arguments - 0,6..0,7
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
    .body[1]
    0] Pass - 0,10..0,14
"""),

(r"""def f(a: (b)): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""**DEL**""", r"""def f(a): pass""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] FunctionDef - 0,0..0,14
    .name 'f'
    .args arguments - 0,6..0,7
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
    .body[1]
    0] Pass - 0,10..0,14
"""),

(r"""def f(a): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""**DEL**""", r"""def f(a): pass""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] FunctionDef - 0,0..0,14
    .name 'f'
    .args arguments - 0,6..0,7
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
    .body[1]
    0] Pass - 0,10..0,14
"""),

(r"""def f(a): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""new""", r"""def f(a: new): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] FunctionDef - 0,0..0,19
    .name 'f'
    .args arguments - 0,6..0,12
      .args[1]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'new' Load - 0,9..0,12
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""def f(a): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""lambda: x""", r"""def f(a: lambda: x): pass""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] FunctionDef - 0,0..0,25
    .name 'f'
    .args arguments - 0,6..0,18
      .args[1]
      0] arg - 0,6..0,18
        .arg 'a'
        .annotation Lambda - 0,9..0,18
          .body Name 'x' Load - 0,17..0,18
    .body[1]
    0] Pass - 0,21..0,25
"""),

(r"""def f(a :  ( b ) ): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""new""", r"""def f(a :  new ): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] FunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,6..0,14
      .args[1]
      0] arg - 0,6..0,14
        .arg 'a'
        .annotation Name 'new' Load - 0,11..0,14
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""def f(a   :  ( b ) ): pass""", 'body[0].args.args[0]', None, 'annotation', {}, r"""**DEL**""", r"""def f(a ): pass""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] FunctionDef - 0,0..0,15
    .name 'f'
    .args arguments - 0,6..0,7
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
    .body[1]
    0] Pass - 0,11..0,15
"""),

(r"""with a as b: pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""new""", r"""with a as new: pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] With - 0,0..0,19
    .items[1]
    0] withitem - 0,5..0,13
      .context_expr Name 'a' Load - 0,5..0,6
      .optional_vars Name 'new' Store - 0,10..0,13
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""with a as (b): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""new""", r"""with a as new: pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] With - 0,0..0,19
    .items[1]
    0] withitem - 0,5..0,13
      .context_expr Name 'a' Load - 0,5..0,6
      .optional_vars Name 'new' Store - 0,10..0,13
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""with (a as (b)): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""new""", r"""with (a as new): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] With - 0,0..0,21
    .items[1]
    0] withitem - 0,6..0,14
      .context_expr Name 'a' Load - 0,6..0,7
      .optional_vars Name 'new' Store - 0,11..0,14
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""with a as b: pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""**DEL**""", r"""with a: pass""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] With - 0,0..0,12
    .items[1]
    0] withitem - 0,5..0,6
      .context_expr Name 'a' Load - 0,5..0,6
    .body[1]
    0] Pass - 0,8..0,12
"""),

(r"""with a as (b): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""**DEL**""", r"""with a: pass""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] With - 0,0..0,12
    .items[1]
    0] withitem - 0,5..0,6
      .context_expr Name 'a' Load - 0,5..0,6
    .body[1]
    0] Pass - 0,8..0,12
"""),

(r"""with (a as (b)): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""**DEL**""", r"""with (a): pass""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] With - 0,0..0,14
    .items[1]
    0] withitem - 0,5..0,8
      .context_expr Name 'a' Load - 0,6..0,7
    .body[1]
    0] Pass - 0,10..0,14
"""),

(r"""with (a as b): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""new""", r"""with (a as new): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] With - 0,0..0,21
    .items[1]
    0] withitem - 0,6..0,14
      .context_expr Name 'a' Load - 0,6..0,7
      .optional_vars Name 'new' Store - 0,11..0,14
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""with (a as b): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""**DEL**""", r"""with (a): pass""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] With - 0,0..0,14
    .items[1]
    0] withitem - 0,5..0,8
      .context_expr Name 'a' Load - 0,6..0,7
    .body[1]
    0] Pass - 0,10..0,14
"""),

(r"""with a: pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""**DEL**""", r"""with a: pass""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] With - 0,0..0,12
    .items[1]
    0] withitem - 0,5..0,6
      .context_expr Name 'a' Load - 0,5..0,6
    .body[1]
    0] Pass - 0,8..0,12
"""),

(r"""with a: pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""new""", r"""with a as new: pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] With - 0,0..0,19
    .items[1]
    0] withitem - 0,5..0,13
      .context_expr Name 'a' Load - 0,5..0,6
      .optional_vars Name 'new' Store - 0,10..0,13
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""with (a): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""new""", r"""with (a) as new: pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] With - 0,0..0,21
    .items[1]
    0] withitem - 0,5..0,15
      .context_expr Name 'a' Load - 0,6..0,7
      .optional_vars Name 'new' Store - 0,12..0,15
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""with (a): pass""", 'body[0].items[0]', None, 'optional_vars', {'raw': False}, r"""new, to""", r"""with (a) as (new, to): pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] With - 0,0..0,27
    .items[1]
    0] withitem - 0,5..0,21
      .context_expr Name 'a' Load - 0,6..0,7
      .optional_vars Tuple - 0,12..0,21
        .elts[2]
        0] Name 'new' Store - 0,13..0,16
        1] Name 'to' Store - 0,18..0,20
        .ctx Store
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""with (a): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""[new, to]""", r"""with (a) as [new, to]: pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] With - 0,0..0,27
    .items[1]
    0] withitem - 0,5..0,21
      .context_expr Name 'a' Load - 0,6..0,7
      .optional_vars List - 0,12..0,21
        .elts[2]
        0] Name 'new' Store - 0,13..0,16
        1] Name 'to' Store - 0,18..0,20
        .ctx Store
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""with (a): pass""", 'body[0].items[0]', None, 'optional_vars', {}, r"""f()""", r"""**NodeError('expecting one of (Name, Tuple, List, Attribute, Subscript) for withitem.optional_vars, got Call')**""", r"""
"""),

(r"""match a:
 case 1 if b: pass""", 'body[0].cases[0]', None, 'guard', {}, r"""new""", r"""match a:
 case 1 if new: pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .guard Name 'new' Load - 1,11..1,14
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""match a:
 case 1 if (b): pass""", 'body[0].cases[0]', None, 'guard', {}, r"""new""", r"""match a:
 case 1 if new: pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .guard Name 'new' Load - 1,11..1,14
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""match a:
 case 1 if b: pass""", 'body[0].cases[0]', None, 'guard', {}, r"""**DEL**""", r"""match a:
 case 1: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case 1 if (b): pass""", 'body[0].cases[0]', None, 'guard', {}, r"""**DEL**""", r"""match a:
 case 1: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0]', None, 'guard', {}, r"""**DEL**""", r"""match a:
 case 1: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0]', None, 'guard', {}, r"""new""", r"""match a:
 case 1 if new: pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .guard Name 'new' Load - 1,11..1,14
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""match a:
 case (1): pass""", 'body[0].cases[0]', None, 'guard', {}, r"""new""", r"""match a:
 case (1) if new: pass""", r"""
Module - ROOT 0,0..1,22
  .body[1]
  0] Match - 0,0..1,22
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,22
      .pattern MatchValue - 1,7..1,8
        .value Constant 1 - 1,7..1,8
      .guard Name 'new' Load - 1,13..1,16
      .body[1]
      0] Pass - 1,18..1,22
"""),

(r"""match a:
 case 1 if b  : pass""", 'body[0].cases[0]', None, 'guard', {}, r"""**DEL**""", r"""match a:
 case 1: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case 1 if (b)  : pass""", 'body[0].cases[0]', None, 'guard', {}, r"""**DEL**""", r"""match a:
 case 1: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case 1  : pass""", 'body[0].cases[0]', None, 'guard', {}, r"""new""", r"""match a:
 case 1 if new: pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchValue - 1,6..1,7
        .value Constant 1 - 1,6..1,7
      .guard Name 'new' Load - 1,11..1,14
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""match a:
 case (1)  : pass""", 'body[0].cases[0]', None, 'guard', {}, r"""new""", r"""match a:
 case (1) if new: pass""", r"""
Module - ROOT 0,0..1,22
  .body[1]
  0] Match - 0,0..1,22
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,22
      .pattern MatchValue - 1,7..1,8
        .value Constant 1 - 1,7..1,8
      .guard Name 'new' Load - 1,13..1,16
      .body[1]
      0] Pass - 1,18..1,22
"""),

(r"""type t[T: a] = ...""", 'body[0].type_params[0]', None, 'bound', {'_ver': 13}, r"""new""", r"""type t[T: new] = ...""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] TypeAlias - 0,0..0,20
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,13
      .name 'T'
      .bound Name 'new' Load - 0,10..0,13
    .value Constant Ellipsis - 0,17..0,20
"""),

(r"""type t[T: (a)] = ...""", 'body[0].type_params[0]', None, 'bound', {'_ver': 13}, r"""new""", r"""type t[T: new] = ...""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] TypeAlias - 0,0..0,20
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,13
      .name 'T'
      .bound Name 'new' Load - 0,10..0,13
    .value Constant Ellipsis - 0,17..0,20
"""),

(r"""type t[T: a] = ...""", 'body[0].type_params[0]', None, 'bound', {'_ver': 13}, r"""**DEL**""", r"""type t[T] = ...""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] TypeAlias - 0,0..0,15
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,8
      .name 'T'
    .value Constant Ellipsis - 0,12..0,15
"""),

(r"""type t[T: (a)] = ...""", 'body[0].type_params[0]', None, 'bound', {'_ver': 13}, r"""**DEL**""", r"""type t[T] = ...""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] TypeAlias - 0,0..0,15
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,8
      .name 'T'
    .value Constant Ellipsis - 0,12..0,15
"""),

(r"""type t[T] = ...""", 'body[0].type_params[0]', None, 'bound', {'_ver': 13}, r"""**DEL**""", r"""type t[T] = ...""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] TypeAlias - 0,0..0,15
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,8
      .name 'T'
    .value Constant Ellipsis - 0,12..0,15
"""),

(r"""type t[T] = ...""", 'body[0].type_params[0]', None, 'bound', {'_ver': 13}, r"""new""", r"""type t[T: new] = ...""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] TypeAlias - 0,0..0,20
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,13
      .name 'T'
      .bound Name 'new' Load - 0,10..0,13
    .value Constant Ellipsis - 0,17..0,20
"""),

(r"""type t[T = a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[T = new] = ...""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] TypeAlias - 0,0..0,21
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,14
      .name 'T'
      .default_value Name 'new' Load - 0,11..0,14
    .value Constant Ellipsis - 0,18..0,21
"""),

(r"""type t[T = (a)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[T = new] = ...""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] TypeAlias - 0,0..0,21
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,14
      .name 'T'
      .default_value Name 'new' Load - 0,11..0,14
    .value Constant Ellipsis - 0,18..0,21
"""),

(r"""type t[T = a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[T] = ...""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] TypeAlias - 0,0..0,15
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,8
      .name 'T'
    .value Constant Ellipsis - 0,12..0,15
"""),

(r"""type t[T = (a)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[T] = ...""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] TypeAlias - 0,0..0,15
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,8
      .name 'T'
    .value Constant Ellipsis - 0,12..0,15
"""),

(r"""type t[T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[T] = ...""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] TypeAlias - 0,0..0,15
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,8
      .name 'T'
    .value Constant Ellipsis - 0,12..0,15
"""),

(r"""type t[T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[T = new] = ...""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] TypeAlias - 0,0..0,21
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,14
      .name 'T'
      .default_value Name 'new' Load - 0,11..0,14
    .value Constant Ellipsis - 0,18..0,21
"""),

(r"""type t[T: int = a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[T: int = new] = ...""", r"""
Module - ROOT 0,0..0,26
  .body[1]
  0] TypeAlias - 0,0..0,26
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,19
      .name 'T'
      .bound Name 'int' Load - 0,10..0,13
      .default_value Name 'new' Load - 0,16..0,19
    .value Constant Ellipsis - 0,23..0,26
"""),

(r"""type t[T: (int) = (a)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[T: (int) = new] = ...""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] TypeAlias - 0,0..0,28
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,21
      .name 'T'
      .bound Name 'int' Load - 0,11..0,14
      .default_value Name 'new' Load - 0,18..0,21
    .value Constant Ellipsis - 0,25..0,28
"""),

(r"""type t[T: int = a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[T: int] = ...""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] TypeAlias - 0,0..0,20
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,13
      .name 'T'
      .bound Name 'int' Load - 0,10..0,13
    .value Constant Ellipsis - 0,17..0,20
"""),

(r"""type t[T: (int) = (a)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[T: (int)] = ...""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] TypeAlias - 0,0..0,22
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,15
      .name 'T'
      .bound Name 'int' Load - 0,11..0,14
    .value Constant Ellipsis - 0,19..0,22
"""),

(r"""type t[T: int] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[T: int] = ...""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] TypeAlias - 0,0..0,20
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,13
      .name 'T'
      .bound Name 'int' Load - 0,10..0,13
    .value Constant Ellipsis - 0,17..0,20
"""),

(r"""type t[T: int] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[T: int = new] = ...""", r"""
Module - ROOT 0,0..0,26
  .body[1]
  0] TypeAlias - 0,0..0,26
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,19
      .name 'T'
      .bound Name 'int' Load - 0,10..0,13
      .default_value Name 'new' Load - 0,16..0,19
    .value Constant Ellipsis - 0,23..0,26
"""),

(r"""type t[T: (int)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[T: (int) = new] = ...""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] TypeAlias - 0,0..0,28
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVar - 0,7..0,21
      .name 'T'
      .bound Name 'int' Load - 0,11..0,14
      .default_value Name 'new' Load - 0,18..0,21
    .value Constant Ellipsis - 0,25..0,28
"""),

(r"""type t[**T = a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[**T = new] = ...""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] TypeAlias - 0,0..0,23
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,7..0,16
      .name 'T'
      .default_value Name 'new' Load - 0,13..0,16
    .value Constant Ellipsis - 0,20..0,23
"""),

(r"""type t[**T = (a)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[**T = new] = ...""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] TypeAlias - 0,0..0,23
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,7..0,16
      .name 'T'
      .default_value Name 'new' Load - 0,13..0,16
    .value Constant Ellipsis - 0,20..0,23
"""),

(r"""type t[**T = a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[**T] = ...""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] TypeAlias - 0,0..0,17
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,7..0,10
      .name 'T'
    .value Constant Ellipsis - 0,14..0,17
"""),

(r"""type t[**T = (a)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[**T] = ...""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] TypeAlias - 0,0..0,17
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,7..0,10
      .name 'T'
    .value Constant Ellipsis - 0,14..0,17
"""),

(r"""type t[**T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[**T] = ...""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] TypeAlias - 0,0..0,17
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,7..0,10
      .name 'T'
    .value Constant Ellipsis - 0,14..0,17
"""),

(r"""type t[**T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[**T = new] = ...""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] TypeAlias - 0,0..0,23
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,7..0,16
      .name 'T'
      .default_value Name 'new' Load - 0,13..0,16
    .value Constant Ellipsis - 0,20..0,23
"""),

(r"""type t[**T=a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[**T] = ...""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] TypeAlias - 0,0..0,17
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,7..0,10
      .name 'T'
    .value Constant Ellipsis - 0,14..0,17
"""),

(r"""type t[**T=a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[**T=new] = ...""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] TypeAlias - 0,0..0,21
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,7..0,14
      .name 'T'
      .default_value Name 'new' Load - 0,11..0,14
    .value Constant Ellipsis - 0,18..0,21
"""),

(r"""type t[ ** T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[ ** T = new] = ...""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] TypeAlias - 0,0..0,25
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 0,8..0,18
      .name 'T'
      .default_value Name 'new' Load - 0,15..0,18
    .value Constant Ellipsis - 0,22..0,25
"""),

(r"""type t[ \
 ** \
 T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[ \
 ** \
 T = new] = ...""", r"""
Module - ROOT 0,0..2,15
  .body[1]
  0] TypeAlias - 0,0..2,15
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] ParamSpec - 1,1..2,8
      .name 'T'
      .default_value Name 'new' Load - 2,5..2,8
    .value Constant Ellipsis - 2,12..2,15
"""),

(r"""type t[*T = a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[*T = new] = ...""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] TypeAlias - 0,0..0,22
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,7..0,15
      .name 'T'
      .default_value Name 'new' Load - 0,12..0,15
    .value Constant Ellipsis - 0,19..0,22
"""),

(r"""type t[*T = (a)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[*T = new] = ...""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] TypeAlias - 0,0..0,22
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,7..0,15
      .name 'T'
      .default_value Name 'new' Load - 0,12..0,15
    .value Constant Ellipsis - 0,19..0,22
"""),

(r"""type t[*T = a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[*T] = ...""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] TypeAlias - 0,0..0,16
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,7..0,9
      .name 'T'
    .value Constant Ellipsis - 0,13..0,16
"""),

(r"""type t[*T = (a)] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[*T] = ...""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] TypeAlias - 0,0..0,16
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,7..0,9
      .name 'T'
    .value Constant Ellipsis - 0,13..0,16
"""),

(r"""type t[*T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[*T] = ...""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] TypeAlias - 0,0..0,16
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,7..0,9
      .name 'T'
    .value Constant Ellipsis - 0,13..0,16
"""),

(r"""type t[*T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[*T = new] = ...""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] TypeAlias - 0,0..0,22
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,7..0,15
      .name 'T'
      .default_value Name 'new' Load - 0,12..0,15
    .value Constant Ellipsis - 0,19..0,22
"""),

(r"""type t[*T=a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""**DEL**""", r"""type t[*T] = ...""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] TypeAlias - 0,0..0,16
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,7..0,9
      .name 'T'
    .value Constant Ellipsis - 0,13..0,16
"""),

(r"""type t[*T=a] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[*T=new] = ...""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] TypeAlias - 0,0..0,20
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,7..0,13
      .name 'T'
      .default_value Name 'new' Load - 0,10..0,13
    .value Constant Ellipsis - 0,17..0,20
"""),

(r"""type t[ * T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[ * T = new] = ...""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] TypeAlias - 0,0..0,24
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 0,8..0,17
      .name 'T'
      .default_value Name 'new' Load - 0,14..0,17
    .value Constant Ellipsis - 0,21..0,24
"""),

(r"""type t[ \
 * \
 T] = ...""", 'body[0].type_params[0]', None, 'default_value', {'_ver': 13}, r"""new""", r"""type t[ \
 * \
 T = new] = ...""", r"""
Module - ROOT 0,0..2,15
  .body[1]
  0] TypeAlias - 0,0..2,15
    .name Name 't' Store - 0,5..0,6
    .type_params[1]
    0] TypeVarTuple - 1,1..2,8
      .name 'T'
      .default_value Name 'new' Load - 2,5..2,8
    .value Constant Ellipsis - 2,12..2,15
"""),

(r"""def f() -> a: pass""", 'body[0]', None, 'returns', {}, r"""new""", r"""def f() -> new: pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] FunctionDef - 0,0..0,20
    .name 'f'
    .body[1]
    0] Pass - 0,16..0,20
    .returns Name 'new' Load - 0,11..0,14
"""),

(r"""def f() -> (a): pass""", 'body[0]', None, 'returns', {}, r"""new""", r"""def f() -> new: pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] FunctionDef - 0,0..0,20
    .name 'f'
    .body[1]
    0] Pass - 0,16..0,20
    .returns Name 'new' Load - 0,11..0,14
"""),

(r"""def f() -> a: pass""", 'body[0]', None, 'returns', {}, r"""**DEL**""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f() -> (a): pass""", 'body[0]', None, 'returns', {}, r"""**DEL**""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f(): pass""", 'body[0]', None, 'returns', {}, r"""**DEL**""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f(): pass""", 'body[0]', None, 'returns', {}, r"""new""", r"""def f() -> new: pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] FunctionDef - 0,0..0,20
    .name 'f'
    .body[1]
    0] Pass - 0,16..0,20
    .returns Name 'new' Load - 0,11..0,14
"""),

(r"""def f() -> (a)  : pass""", 'body[0]', None, 'returns', {}, r"""**DEL**""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f()  : pass""", 'body[0]', None, 'returns', {}, r"""new""", r"""def f() -> new: pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] FunctionDef - 0,0..0,20
    .name 'f'
    .body[1]
    0] Pass - 0,16..0,20
    .returns Name 'new' Load - 0,11..0,14
"""),

(r"""async def f(**b) -> a: pass""", 'body[0]', None, 'returns', {}, r"""new""", r"""async def f(**b) -> new: pass""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] AsyncFunctionDef - 0,0..0,29
    .name 'f'
    .args arguments - 0,12..0,15
      .kwarg arg - 0,14..0,15
        .arg 'b'
    .body[1]
    0] Pass - 0,25..0,29
    .returns Name 'new' Load - 0,20..0,23
"""),

(r"""async def f(**b) -> (a): pass""", 'body[0]', None, 'returns', {}, r"""new""", r"""async def f(**b) -> new: pass""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] AsyncFunctionDef - 0,0..0,29
    .name 'f'
    .args arguments - 0,12..0,15
      .kwarg arg - 0,14..0,15
        .arg 'b'
    .body[1]
    0] Pass - 0,25..0,29
    .returns Name 'new' Load - 0,20..0,23
"""),

(r"""async def f(**b) -> a: pass""", 'body[0]', None, 'returns', {}, r"""**DEL**""", r"""async def f(**b): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] AsyncFunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,12..0,15
      .kwarg arg - 0,14..0,15
        .arg 'b'
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""async def f(**b) -> (a): pass""", 'body[0]', None, 'returns', {}, r"""**DEL**""", r"""async def f(**b): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] AsyncFunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,12..0,15
      .kwarg arg - 0,14..0,15
        .arg 'b'
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""async def f(**b): pass""", 'body[0]', None, 'returns', {}, r"""**DEL**""", r"""async def f(**b): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] AsyncFunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,12..0,15
      .kwarg arg - 0,14..0,15
        .arg 'b'
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""async def f(**b): pass""", 'body[0]', None, 'returns', {}, r"""new""", r"""async def f(**b) -> new: pass""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] AsyncFunctionDef - 0,0..0,29
    .name 'f'
    .args arguments - 0,12..0,15
      .kwarg arg - 0,14..0,15
        .arg 'b'
    .body[1]
    0] Pass - 0,25..0,29
    .returns Name 'new' Load - 0,20..0,23
"""),

(r"""a += b""", 'body[0]', None, 'op', {}, r"""new""", r"""**NodeError("expecting operator, got 'new'")**""", r"""
"""),

(r"""a and b""", 'body[0].value', None, 'op', {}, r"""new""", r"""**NodeError("expecting boolop, got 'new'")**""", r"""
"""),

(r"""a + b""", 'body[0].value', None, 'op', {}, r"""new""", r"""**NodeError("expecting operator, got 'new'")**""", r"""
"""),

(r"""-a""", 'body[0].value', None, 'op', {'raw': False}, r"""new""", r"""**NodeError("expecting unaryop, got 'new'")**""", r"""
"""),

(r"""a < b""", 'body[0].value', 0, 'ops', {}, r"""new""", r"""**NodeError("expecting cmpop, got 'new'")**""", r"""
"""),

(r"""def f(*, a=b): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a=new): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .args arguments - 0,6..0,14
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'a'
      .kw_defaults[1]
      0] Name 'new' Load - 0,11..0,14
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""def f(*, a=(b)): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a=new): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .args arguments - 0,6..0,14
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'a'
      .kw_defaults[1]
      0] Name 'new' Load - 0,11..0,14
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""def f(*, a=b): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""**DEL**""", r"""def f(*, a): pass""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] FunctionDef - 0,0..0,17
    .name 'f'
    .args arguments - 0,6..0,10
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'a'
      .kw_defaults[1]
      0] None
    .body[1]
    0] Pass - 0,13..0,17
"""),

(r"""def f(*, a=(b)): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""**DEL**""", r"""def f(*, a): pass""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] FunctionDef - 0,0..0,17
    .name 'f'
    .args arguments - 0,6..0,10
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'a'
      .kw_defaults[1]
      0] None
    .body[1]
    0] Pass - 0,13..0,17
"""),

(r"""def f(*, a): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""**DEL**""", r"""def f(*, a): pass""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] FunctionDef - 0,0..0,17
    .name 'f'
    .args arguments - 0,6..0,10
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'a'
      .kw_defaults[1]
      0] None
    .body[1]
    0] Pass - 0,13..0,17
"""),

(r"""def f(*, a): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a=new): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .args arguments - 0,6..0,14
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'a'
      .kw_defaults[1]
      0] Name 'new' Load - 0,11..0,14
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""def f(*, a, c=d): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a=new, c=d): pass""", r"""
Module - ROOT 0,0..0,26
  .body[1]
  0] FunctionDef - 0,0..0,26
    .name 'f'
    .args arguments - 0,6..0,19
      .kwonlyargs[2]
      0] arg - 0,9..0,10
        .arg 'a'
      1] arg - 0,16..0,17
        .arg 'c'
      .kw_defaults[2]
      0] Name 'new' Load - 0,11..0,14
      1] Name 'd' Load - 0,18..0,19
    .body[1]
    0] Pass - 0,22..0,26
"""),

(r"""def f(*, a: (int), c=d): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a: (int) = new, c=d): pass""", r"""
Module - ROOT 0,0..0,35
  .body[1]
  0] FunctionDef - 0,0..0,35
    .name 'f'
    .args arguments - 0,6..0,28
      .kwonlyargs[2]
      0] arg - 0,9..0,17
        .arg 'a'
        .annotation Name 'int' Load - 0,13..0,16
      1] arg - 0,25..0,26
        .arg 'c'
      .kw_defaults[2]
      0] Name 'new' Load - 0,20..0,23
      1] Name 'd' Load - 0,27..0,28
    .body[1]
    0] Pass - 0,31..0,35
"""),

(r"""def f(*, a=b, c=d): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""**DEL**""", r"""def f(*, a, c=d): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] FunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,6..0,15
      .kwonlyargs[2]
      0] arg - 0,9..0,10
        .arg 'a'
      1] arg - 0,12..0,13
        .arg 'c'
      .kw_defaults[2]
      0] None
      1] Name 'd' Load - 0,14..0,15
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""def f(*, a, **c): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a=new, **c): pass""", r"""
Module - ROOT 0,0..0,26
  .body[1]
  0] FunctionDef - 0,0..0,26
    .name 'f'
    .args arguments - 0,6..0,19
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'a'
      .kw_defaults[1]
      0] Name 'new' Load - 0,11..0,14
      .kwarg arg - 0,18..0,19
        .arg 'c'
    .body[1]
    0] Pass - 0,22..0,26
"""),

(r"""def f(*, a: (int), **c): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a: (int) = new, **c): pass""", r"""
Module - ROOT 0,0..0,35
  .body[1]
  0] FunctionDef - 0,0..0,35
    .name 'f'
    .args arguments - 0,6..0,28
      .kwonlyargs[1]
      0] arg - 0,9..0,17
        .arg 'a'
        .annotation Name 'int' Load - 0,13..0,16
      .kw_defaults[1]
      0] Name 'new' Load - 0,20..0,23
      .kwarg arg - 0,27..0,28
        .arg 'c'
    .body[1]
    0] Pass - 0,31..0,35
"""),

(r"""def f(*, a=b, **c): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""**DEL**""", r"""def f(*, a, **c): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] FunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,6..0,15
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'a'
      .kw_defaults[1]
      0] None
      .kwarg arg - 0,14..0,15
        .arg 'c'
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""def f(*, a: int = b): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a: int = new): pass""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] FunctionDef - 0,0..0,28
    .name 'f'
    .args arguments - 0,6..0,21
      .kwonlyargs[1]
      0] arg - 0,9..0,15
        .arg 'a'
        .annotation Name 'int' Load - 0,12..0,15
      .kw_defaults[1]
      0] Name 'new' Load - 0,18..0,21
    .body[1]
    0] Pass - 0,24..0,28
"""),

(r"""def f(*, a: (int) = (b)): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a: (int) = new): pass""", r"""
Module - ROOT 0,0..0,30
  .body[1]
  0] FunctionDef - 0,0..0,30
    .name 'f'
    .args arguments - 0,6..0,23
      .kwonlyargs[1]
      0] arg - 0,9..0,17
        .arg 'a'
        .annotation Name 'int' Load - 0,13..0,16
      .kw_defaults[1]
      0] Name 'new' Load - 0,20..0,23
    .body[1]
    0] Pass - 0,26..0,30
"""),

(r"""def f(*, a: int = b): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""**DEL**""", r"""def f(*, a: int): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] FunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,6..0,15
      .kwonlyargs[1]
      0] arg - 0,9..0,15
        .arg 'a'
        .annotation Name 'int' Load - 0,12..0,15
      .kw_defaults[1]
      0] None
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""def f(*, a: (int) = (b)): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""**DEL**""", r"""def f(*, a: (int)): pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] FunctionDef - 0,0..0,24
    .name 'f'
    .args arguments - 0,6..0,17
      .kwonlyargs[1]
      0] arg - 0,9..0,17
        .arg 'a'
        .annotation Name 'int' Load - 0,13..0,16
      .kw_defaults[1]
      0] None
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""def f(*, a: int): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""**DEL**""", r"""def f(*, a: int): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] FunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,6..0,15
      .kwonlyargs[1]
      0] arg - 0,9..0,15
        .arg 'a'
        .annotation Name 'int' Load - 0,12..0,15
      .kw_defaults[1]
      0] None
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""def f(*, a: int): pass""", 'body[0].args', 0, 'kw_defaults', {}, r"""new""", r"""def f(*, a: int = new): pass""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] FunctionDef - 0,0..0,28
    .name 'f'
    .args arguments - 0,6..0,21
      .kwonlyargs[1]
      0] arg - 0,9..0,15
        .arg 'a'
        .annotation Name 'int' Load - 0,12..0,15
      .kw_defaults[1]
      0] Name 'new' Load - 0,18..0,21
    .body[1]
    0] Pass - 0,24..0,28
"""),

(r"""class c(a=b): pass""", 'body[0].keywords[0]', None, 'arg', {}, r"""new""", r"""class c(new=b): pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] ClassDef - 0,0..0,20
    .name 'c'
    .keywords[1]
    0] keyword - 0,8..0,13
      .arg 'new'
      .value Name 'b' Load - 0,12..0,13
    .body[1]
    0] Pass - 0,16..0,20
"""),

(r"""class c(a=b): pass""", 'body[0].keywords[0]', None, 'arg', {}, r"""**DEL**""", r"""class c(**b): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ClassDef - 0,0..0,18
    .name 'c'
    .keywords[1]
    0] keyword - 0,8..0,11
      .value Name 'b' Load - 0,10..0,11
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""class c(**b): pass""", 'body[0].keywords[0]', None, 'arg', {}, r"""**DEL**""", r"""class c(**b): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ClassDef - 0,0..0,18
    .name 'c'
    .keywords[1]
    0] keyword - 0,8..0,11
      .value Name 'b' Load - 0,10..0,11
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""class c(**b): pass""", 'body[0].keywords[0]', None, 'arg', {}, r"""new""", r"""class c(new=b): pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] ClassDef - 0,0..0,20
    .name 'c'
    .keywords[1]
    0] keyword - 0,8..0,13
      .arg 'new'
      .value Name 'b' Load - 0,12..0,13
    .body[1]
    0] Pass - 0,16..0,20
"""),

(r"""class c( a
 =
 b
 ): pass""", 'body[0].keywords[0]', None, 'arg', {}, r"""new""", r"""class c( new
 =
 b
 ): pass""", r"""
Module - ROOT 0,0..3,8
  .body[1]
  0] ClassDef - 0,0..3,8
    .name 'c'
    .keywords[1]
    0] keyword - 0,9..2,2
      .arg 'new'
      .value Name 'b' Load - 2,1..2,2
    .body[1]
    0] Pass - 3,4..3,8
"""),

(r"""class c( a
 =
 b
 ): pass""", 'body[0].keywords[0]', None, 'arg', {}, r"""**DEL**""", r"""class c( **b
 ): pass""", r"""
Module - ROOT 0,0..1,8
  .body[1]
  0] ClassDef - 0,0..1,8
    .name 'c'
    .keywords[1]
    0] keyword - 0,9..0,12
      .value Name 'b' Load - 0,11..0,12
    .body[1]
    0] Pass - 1,4..1,8
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""a.b""", r"""match a:
 case a.b: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchValue - 1,6..1,9
        .value Attribute - 1,6..1,9
          .value Name 'a' Load - 1,6..1,7
          .attr 'b'
          .ctx Load
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""2""", r"""match a:
 case 2: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchValue - 1,6..1,7
        .value Constant 2 - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""2.0""", r"""match a:
 case 2.0: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchValue - 1,6..1,9
        .value Constant 2.0 - 1,6..1,9
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""2j""", r"""match a:
 case 2j: pass""", r"""
Module - ROOT 0,0..1,14
  .body[1]
  0] Match - 0,0..1,14
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,14
      .pattern MatchValue - 1,6..1,8
        .value Constant 2j - 1,6..1,8
      .body[1]
      0] Pass - 1,10..1,14
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""'2'""", r"""match a:
 case '2': pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchValue - 1,6..1,9
        .value Constant '2' - 1,6..1,9
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0].pattern', None, None, {'raw': False}, r"""b""", r"""**NodeError('invalid value for MatchValue.value')**""", r"""
"""),

(r"""match a:
 case 1: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""1+2j""", r"""match a:
 case 1+2j: pass""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] Match - 0,0..1,16
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,16
      .pattern MatchValue - 1,6..1,10
        .value BinOp - 1,6..1,10
          .left Constant 1 - 1,6..1,7
          .op Add - 1,7..1,8
          .right Constant 2j - 1,8..1,10
      .body[1]
      0] Pass - 1,12..1,16
"""),

(r"""match a:
 case (1): pass""", 'body[0].cases[0].pattern', None, None, {}, r"""2""", r"""match a:
 case (2): pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchValue - 1,7..1,8
        .value Constant 2 - 1,7..1,8
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case (1): pass""", 'body[0].cases[0].pattern', None, None, {}, r"""1+2j""", r"""match a:
 case (1+2j): pass""", r"""
Module - ROOT 0,0..1,18
  .body[1]
  0] Match - 0,0..1,18
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,18
      .pattern MatchValue - 1,7..1,11
        .value BinOp - 1,7..1,11
          .left Constant 1 - 1,7..1,8
          .op Add - 1,8..1,9
          .right Constant 2j - 1,9..1,11
      .body[1]
      0] Pass - 1,14..1,18
"""),

(r"""match a:
 case (1+2j): pass""", 'body[0].cases[0].pattern', None, None, {}, r"""3""", r"""match a:
 case (3): pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchValue - 1,7..1,8
        .value Constant 3 - 1,7..1,8
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""a[b:]""", 'body[0].value.slice', None, 'lower', {}, r"""new""", r"""a[new:]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .lower Name 'new' Load - 0,2..0,5
      .ctx Load
"""),

(r"""a[(b):]""", 'body[0].value.slice', None, 'lower', {}, r"""new""", r"""a[new:]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .lower Name 'new' Load - 0,2..0,5
      .ctx Load
"""),

(r"""a[b:]""", 'body[0].value.slice', None, 'lower', {}, r"""**DEL**""", r"""a[:]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,3
      .ctx Load
"""),

(r"""a[(b):]""", 'body[0].value.slice', None, 'lower', {}, r"""**DEL**""", r"""a[:]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,3
      .ctx Load
"""),

(r"""a[:]""", 'body[0].value.slice', None, 'lower', {}, r"""**DEL**""", r"""a[:]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,3
      .ctx Load
"""),

(r"""a[:]""", 'body[0].value.slice', None, 'lower', {}, r"""new""", r"""a[new:]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .lower Name 'new' Load - 0,2..0,5
      .ctx Load
"""),

(r"""a[::]""", 'body[0].value.slice', None, 'lower', {}, r"""new""", r"""a[new::]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .lower Name 'new' Load - 0,2..0,5
      .ctx Load
"""),

(r"""a[:(b):]""", 'body[0].value.slice', None, 'lower', {}, r"""new""", r"""a[new:(b):]""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Subscript - 0,0..0,11
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,10
        .lower Name 'new' Load - 0,2..0,5
        .upper Name 'b' Load - 0,7..0,8
      .ctx Load
"""),

(r"""a[ : ]""", 'body[0].value.slice', None, 'lower', {}, r"""new""", r"""a[ new: ]""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Subscript - 0,0..0,9
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,7
        .lower Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[ b : ]""", 'body[0].value.slice', None, 'lower', {}, r"""**DEL**""", r"""a[ : ]""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value Subscript - 0,0..0,6
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,4
      .ctx Load
"""),

(r"""a[':':]""", 'body[0].value.slice', None, 'lower', {}, r"""new""", r"""a[new:]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .lower Name 'new' Load - 0,2..0,5
      .ctx Load
"""),

(r"""a[':':]""", 'body[0].value.slice', None, 'lower', {}, r"""**DEL**""", r"""a[:]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,3
      .ctx Load
"""),

(r"""a[:b]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[:new]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .upper Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[:(b)]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[:new]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .upper Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[:b]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[:]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,3
      .ctx Load
"""),

(r"""a[:(b)]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[:]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,3
      .ctx Load
"""),

(r"""a[:]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[:]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,3
      .ctx Load
"""),

(r"""a[:]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[:new]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .upper Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[::]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[:new:]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .upper Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[ : ]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[ :new ]""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Subscript - 0,0..0,9
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,7
        .upper Name 'new' Load - 0,4..0,7
      .ctx Load
"""),

(r"""a[ : b ]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[ : ]""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value Subscript - 0,0..0,6
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,4
      .ctx Load
"""),

(r"""a[ : : ]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[ :new: ]""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Subscript - 0,0..0,10
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,8
        .upper Name 'new' Load - 0,4..0,7
      .ctx Load
"""),

(r"""a[ : b : ]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[ :: ]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,5
      .ctx Load
"""),

(r"""a[:b:]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[:new:]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .upper Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[:(b):]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[:new:]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .upper Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[:b:]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[::]""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Subscript - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,4
      .ctx Load
"""),

(r"""a[:(b):]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[::]""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Subscript - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,4
      .ctx Load
"""),

(r"""a[:':']""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[:new]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .upper Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[:':']""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[:]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,3
      .ctx Load
"""),

(r"""a[:':':]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[:new:]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .upper Name 'new' Load - 0,3..0,6
      .ctx Load
"""),

(r"""a[:':':]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[::]""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Subscript - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,4
      .ctx Load
"""),

(r"""a[":":':']""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[":":new]""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Subscript - 0,0..0,10
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,9
        .lower Constant ':' - 0,2..0,5
        .upper Name 'new' Load - 0,6..0,9
      .ctx Load
"""),

(r"""a[":":':']""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[":":]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .lower Constant ':' - 0,2..0,5
      .ctx Load
"""),

(r"""a[":":':':]""", 'body[0].value.slice', None, 'upper', {}, r"""new""", r"""a[":":new:]""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Subscript - 0,0..0,11
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,10
        .lower Constant ':' - 0,2..0,5
        .upper Name 'new' Load - 0,6..0,9
      .ctx Load
"""),

(r"""a[":":':':]""", 'body[0].value.slice', None, 'upper', {}, r"""**DEL**""", r"""a[":"::]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .lower Constant ':' - 0,2..0,5
      .ctx Load
"""),

(r"""a[::b]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[::new]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .step Name 'new' Load - 0,4..0,7
      .ctx Load
"""),

(r"""a[::(b)]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[::new]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .step Name 'new' Load - 0,4..0,7
      .ctx Load
"""),

(r"""a[::b]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[::]""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Subscript - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,4
      .ctx Load
"""),

(r"""a[::(b)]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[::]""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Subscript - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,4
      .ctx Load
"""),

(r"""a[::]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[::]""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Subscript - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,4
      .ctx Load
"""),

(r"""a[::]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[::new]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .step Name 'new' Load - 0,4..0,7
      .ctx Load
"""),

(r"""a[:]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[::new]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .step Name 'new' Load - 0,4..0,7
      .ctx Load
"""),

(r"""a[ :: ]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[ ::new ]""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Subscript - 0,0..0,10
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,8
        .step Name 'new' Load - 0,5..0,8
      .ctx Load
"""),

(r"""a[ : ]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[ ::new ]""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Subscript - 0,0..0,10
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,8
        .step Name 'new' Load - 0,5..0,8
      .ctx Load
"""),

(r"""a[ :: b ]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[ :: ]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,5
      .ctx Load
"""),

(r"""a[ : : ]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[ : :new ]""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Subscript - 0,0..0,11
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,9
        .step Name 'new' Load - 0,6..0,9
      .ctx Load
"""),

(r"""a[ : b : ]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[ : b : ]""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Subscript - 0,0..0,10
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,3..0,8
        .upper Name 'b' Load - 0,5..0,6
      .ctx Load
"""),

(r"""a[:b]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[:b:new]""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Subscript - 0,0..0,9
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,8
        .upper Name 'b' Load - 0,3..0,4
        .step Name 'new' Load - 0,5..0,8
      .ctx Load
"""),

(r"""a[:(b)]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[:(b):new]""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Subscript - 0,0..0,11
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,10
        .upper Name 'b' Load - 0,4..0,5
        .step Name 'new' Load - 0,7..0,10
      .ctx Load
"""),

(r"""a[:b]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[:b]""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Subscript - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,4
        .upper Name 'b' Load - 0,3..0,4
      .ctx Load
"""),

(r"""a[:(b)]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[:(b)]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .upper Name 'b' Load - 0,4..0,5
      .ctx Load
"""),

(r"""a[:':']""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[:':':new]""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Subscript - 0,0..0,11
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,10
        .upper Constant ':' - 0,3..0,6
        .step Name 'new' Load - 0,7..0,10
      .ctx Load
"""),

(r"""a[:':']""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[:':']""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,6
        .upper Constant ':' - 0,3..0,6
      .ctx Load
"""),

(r"""a[:':':]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[:':':new]""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Subscript - 0,0..0,11
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,10
        .upper Constant ':' - 0,3..0,6
        .step Name 'new' Load - 0,7..0,10
      .ctx Load
"""),

(r"""a[:':':]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[:':':]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .upper Constant ':' - 0,3..0,6
      .ctx Load
"""),

(r"""a[::':']""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[::new]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .step Name 'new' Load - 0,4..0,7
      .ctx Load
"""),

(r"""a[::':']""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[::]""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Subscript - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,4
      .ctx Load
"""),

(r"""a[":":':']""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[":":':':new]""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Expr - 0,0..0,14
    .value Subscript - 0,0..0,14
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,13
        .lower Constant ':' - 0,2..0,5
        .upper Constant ':' - 0,6..0,9
        .step Name 'new' Load - 0,10..0,13
      .ctx Load
"""),

(r"""a[":":':']""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[":":':']""", r"""
Module - ROOT 0,0..0,10
  .body[1]
  0] Expr - 0,0..0,10
    .value Subscript - 0,0..0,10
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,9
        .lower Constant ':' - 0,2..0,5
        .upper Constant ':' - 0,6..0,9
      .ctx Load
"""),

(r"""a[":":':':]""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[":":':':new]""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Expr - 0,0..0,14
    .value Subscript - 0,0..0,14
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,13
        .lower Constant ':' - 0,2..0,5
        .upper Constant ':' - 0,6..0,9
        .step Name 'new' Load - 0,10..0,13
      .ctx Load
"""),

(r"""a[":":':':]""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[":":':':]""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Subscript - 0,0..0,11
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,10
        .lower Constant ':' - 0,2..0,5
        .upper Constant ':' - 0,6..0,9
      .ctx Load
"""),

(r"""a[":"::':']""", 'body[0].value.slice', None, 'step', {}, r"""new""", r"""a[":"::new]""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value Subscript - 0,0..0,11
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,10
        .lower Constant ':' - 0,2..0,5
        .step Name 'new' Load - 0,7..0,10
      .ctx Load
"""),

(r"""a[":"::':']""", 'body[0].value.slice', None, 'step', {}, r"""**DEL**""", r"""a[":"::]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .lower Constant ':' - 0,2..0,5
      .ctx Load
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""**DEL**""", r"""**ValueError('cannot delete Constant.value')**""", r"""
"""),

(r"""...""", 'body[0].value', None, None, {'raw': False}, r"""new""", r"""**NodeError('expecting a Constant for Constant.value, got Name')**""", r"""
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""...""", r"""...""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value Constant Ellipsis - 0,0..0,3
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""1""", r"""1""", r"""
Module - ROOT 0,0..0,1
  .body[1]
  0] Expr - 0,0..0,1
    .value Constant 1 - 0,0..0,1
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""1.0""", r"""1.0""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value Constant 1.0 - 0,0..0,3
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""1j""", r"""1j""", r"""
Module - ROOT 0,0..0,2
  .body[1]
  0] Expr - 0,0..0,2
    .value Constant 1j - 0,0..0,2
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""'str'""", r"""'str'""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Constant 'str' - 0,0..0,5
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""b'bytes'""", r"""b'bytes'""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Constant b'bytes' - 0,0..0,8
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""True""", r"""True""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Constant True - 0,0..0,4
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""False""", r"""False""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Constant False - 0,0..0,5
"""),

(r"""...""", 'body[0].value', None, None, {}, r"""None""", r"""None""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Constant None - 0,0..0,4
"""),

(r"""None""", 'body[0].value', None, None, {}, r"""...""", r"""...""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value Constant Ellipsis - 0,0..0,3
"""),

(r"""a.b""", 'body[0].value', None, 'attr', {}, r"""new""", r"""a.new""", r"""
Module - ROOT 0,0..0,5
  .body[1]
  0] Expr - 0,0..0,5
    .value Attribute - 0,0..0,5
      .value Name 'a' Load - 0,0..0,1
      .attr 'new'
      .ctx Load
"""),

(r"""(a).b""", 'body[0].value', None, 'attr', {}, r"""new""", r"""(a).new""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Attribute - 0,0..0,7
      .value Name 'a' Load - 0,1..0,2
      .attr 'new'
      .ctx Load
"""),

(r"""(a) . b""", 'body[0].value', None, 'attr', {}, r"""new""", r"""(a) . new""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Attribute - 0,0..0,9
      .value Name 'a' Load - 0,1..0,2
      .attr 'new'
      .ctx Load
"""),

(r"""a.b""", 'body[0].value', None, 'attr', {}, r"""**DEL**""", r"""**ValueError('cannot delete Attribute.attr')**""", r"""
"""),

(r"""a""", 'body[0].value', None, None, {}, r"""new""", r"""new""", r"""
Module - ROOT 0,0..0,3
  .body[1]
  0] Expr - 0,0..0,3
    .value Name 'new' Load - 0,0..0,3
"""),

(r"""a""", 'body[0].value', None, None, {}, r"""**DEL**""", r"""**ValueError('cannot delete Name.id')**""", r"""
"""),

(r"""try: pass
except e: pass""", 'body[0].handlers[0]', None, 'type', {}, r"""new""", r"""try: pass
except new: pass""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] Try - 0,0..1,16
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,16
      .type Name 'new' Load - 1,7..1,10
      .body[1]
      0] Pass - 1,12..1,16
"""),

(r"""try: pass
except (e): pass""", 'body[0].handlers[0]', None, 'type', {}, r"""new""", r"""try: pass
except new: pass""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] Try - 0,0..1,16
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,16
      .type Name 'new' Load - 1,7..1,10
      .body[1]
      0] Pass - 1,12..1,16
"""),

(r"""try: pass
except e: pass""", 'body[0].handlers[0]', None, 'type', {}, r"""**DEL**""", r"""try: pass
except: pass""", r"""
Module - ROOT 0,0..1,12
  .body[1]
  0] Try - 0,0..1,12
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,12
      .body[1]
      0] Pass - 1,8..1,12
"""),

(r"""try: pass
except (e): pass""", 'body[0].handlers[0]', None, 'type', {}, r"""**DEL**""", r"""try: pass
except: pass""", r"""
Module - ROOT 0,0..1,12
  .body[1]
  0] Try - 0,0..1,12
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,12
      .body[1]
      0] Pass - 1,8..1,12
"""),

(r"""try: pass
except e as n: pass""", 'body[0].handlers[0]', None, 'type', {}, r"""**DEL**""", r"""**ValueError('cannot delete ExceptHandler.type in this state')**""", r"""
"""),

(r"""try: pass
except: pass""", 'body[0].handlers[0]', None, 'type', {}, r"""**DEL**""", r"""try: pass
except: pass""", r"""
Module - ROOT 0,0..1,12
  .body[1]
  0] Try - 0,0..1,12
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,12
      .body[1]
      0] Pass - 1,8..1,12
"""),

(r"""try: pass
except: pass""", 'body[0].handlers[0]', None, 'type', {}, r"""new""", r"""try: pass
except new: pass""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] Try - 0,0..1,16
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,16
      .type Name 'new' Load - 1,7..1,10
      .body[1]
      0] Pass - 1,12..1,16
"""),

(r"""try: pass
except e as n: pass""", 'body[0].handlers[0]', None, 'type', {}, r"""new""", r"""try: pass
except new as n: pass""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Try - 0,0..1,21
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,21
      .type Name 'new' Load - 1,7..1,10
      .name 'n'
      .body[1]
      0] Pass - 1,17..1,21
"""),

(r"""try: pass
except (e) as n: pass""", 'body[0].handlers[0]', None, 'type', {}, r"""new""", r"""try: pass
except new as n: pass""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Try - 0,0..1,21
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,21
      .type Name 'new' Load - 1,7..1,10
      .name 'n'
      .body[1]
      0] Pass - 1,17..1,21
"""),

(r"""try: pass
except e as n: pass""", 'body[0].handlers[0]', None, 'name', {}, r"""new""", r"""try: pass
except e as new: pass""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Try - 0,0..1,21
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,21
      .type Name 'e' Load - 1,7..1,8
      .name 'new'
      .body[1]
      0] Pass - 1,17..1,21
"""),

(r"""try: pass
except (e) as a: pass""", 'body[0].handlers[0]', None, 'name', {}, r"""new""", r"""try: pass
except (e) as new: pass""", r"""
Module - ROOT 0,0..1,23
  .body[1]
  0] Try - 0,0..1,23
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,23
      .type Name 'e' Load - 1,8..1,9
      .name 'new'
      .body[1]
      0] Pass - 1,19..1,23
"""),

(r"""try: pass
except e as n: pass""", 'body[0].handlers[0]', None, 'name', {}, r"""**DEL**""", r"""try: pass
except e: pass""", r"""
Module - ROOT 0,0..1,14
  .body[1]
  0] Try - 0,0..1,14
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,14
      .type Name 'e' Load - 1,7..1,8
      .body[1]
      0] Pass - 1,10..1,14
"""),

(r"""try: pass
except (e) as n: pass""", 'body[0].handlers[0]', None, 'name', {}, r"""**DEL**""", r"""try: pass
except (e): pass""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] Try - 0,0..1,16
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,16
      .type Name 'e' Load - 1,8..1,9
      .body[1]
      0] Pass - 1,12..1,16
"""),

(r"""try: pass
except e: pass""", 'body[0].handlers[0]', None, 'name', {}, r"""**DEL**""", r"""try: pass
except e: pass""", r"""
Module - ROOT 0,0..1,14
  .body[1]
  0] Try - 0,0..1,14
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,14
      .type Name 'e' Load - 1,7..1,8
      .body[1]
      0] Pass - 1,10..1,14
"""),

(r"""try: pass
except (e): pass""", 'body[0].handlers[0]', None, 'name', {}, r"""**DEL**""", r"""try: pass
except (e): pass""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] Try - 0,0..1,16
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,16
      .type Name 'e' Load - 1,8..1,9
      .body[1]
      0] Pass - 1,12..1,16
"""),

(r"""try: pass
except e: pass""", 'body[0].handlers[0]', None, 'name', {}, r"""new""", r"""try: pass
except e as new: pass""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Try - 0,0..1,21
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,21
      .type Name 'e' Load - 1,7..1,8
      .name 'new'
      .body[1]
      0] Pass - 1,17..1,21
"""),

(r"""try: pass
except e, f: pass""", 'body[0].handlers[0]', None, 'name', {'raw': False, '_ver': 14}, r"""new""", r"""try: pass
except (e, f) as new: pass""", r"""
Module - ROOT 0,0..1,26
  .body[1]
  0] Try - 0,0..1,26
    .body[1]
    0] Pass - 0,5..0,9
    .handlers[1]
    0] ExceptHandler - 1,0..1,26
      .type Tuple - 1,7..1,13
        .elts[2]
        0] Name 'e' Load - 1,8..1,9
        1] Name 'f' Load - 1,11..1,12
        .ctx Load
      .name 'new'
      .body[1]
      0] Pass - 1,22..1,26
"""),

(r"""try: pass
except: pass""", 'body[0].handlers[0]', None, 'name', {}, r"""new""", r"""**ValueError('cannot create ExceptHandler.name in this state')**""", r"""
"""),

(r"""from a import *""", 'body[0]', None, 'module', {}, r"""new""", r"""from new import *""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] ImportFrom - 0,0..0,17
    .module 'new'
    .names[1]
    0] alias - 0,16..0,17
      .name '*'
    .level 0
"""),

(r"""from a import *""", 'body[0]', None, 'module', {}, r"""x.y""", r"""from x.y import *""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] ImportFrom - 0,0..0,17
    .module 'x.y'
    .names[1]
    0] alias - 0,16..0,17
      .name '*'
    .level 0
"""),

(r"""from a import *""", 'body[0]', None, 'module', {}, r"""**DEL**""", r"""**ValueError('cannot delete ImportFrom.module in this state')**""", r"""
"""),

(r"""from .a import *""", 'body[0]', None, 'module', {}, r"""new""", r"""from .new import *""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ImportFrom - 0,0..0,18
    .module 'new'
    .names[1]
    0] alias - 0,17..0,18
      .name '*'
    .level 1
"""),

(r"""from .a import *""", 'body[0]', None, 'module', {}, r"""x.y""", r"""from .x.y import *""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ImportFrom - 0,0..0,18
    .module 'x.y'
    .names[1]
    0] alias - 0,17..0,18
      .name '*'
    .level 1
"""),

(r"""from .a import *""", 'body[0]', None, 'module', {}, r"""**DEL**""", r"""from . import *""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] ImportFrom - 0,0..0,15
    .names[1]
    0] alias - 0,14..0,15
      .name '*'
    .level 1
"""),

(r"""from . a import *""", 'body[0]', None, 'module', {}, r"""new""", r"""from . new import *""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] ImportFrom - 0,0..0,19
    .module 'new'
    .names[1]
    0] alias - 0,18..0,19
      .name '*'
    .level 1
"""),

(r"""from . a import *""", 'body[0]', None, 'module', {}, r"""x.y""", r"""from . x.y import *""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] ImportFrom - 0,0..0,19
    .module 'x.y'
    .names[1]
    0] alias - 0,18..0,19
      .name '*'
    .level 1
"""),

(r"""from . a import *""", 'body[0]', None, 'module', {}, r"""**DEL**""", r"""from .  import *""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] ImportFrom - 0,0..0,16
    .names[1]
    0] alias - 0,15..0,16
      .name '*'
    .level 1
"""),

(r"""from . import *""", 'body[0]', None, 'module', {}, r"""new""", r"""from .new import *""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ImportFrom - 0,0..0,18
    .module 'new'
    .names[1]
    0] alias - 0,17..0,18
      .name '*'
    .level 1
"""),

(r"""from . \
 .\
a import *""", 'body[0]', None, 'module', {}, r"""new""", r"""from . \
 .\
new import *""", r"""
Module - ROOT 0,0..2,12
  .body[1]
  0] ImportFrom - 0,0..2,12
    .module 'new'
    .names[1]
    0] alias - 2,11..2,12
      .name '*'
    .level 2
"""),

(r"""from . \
.\
  a import *""", 'body[0]', None, 'module', {}, r"""**DEL**""", r"""from . \
.\
   import *""", r"""
Module - ROOT 0,0..2,11
  .body[1]
  0] ImportFrom - 0,0..2,11
    .names[1]
    0] alias - 2,10..2,11
      .name '*'
    .level 2
"""),

(r"""from . \
 . \
 import *""", 'body[0]', None, 'module', {}, r"""new""", r"""from . \
 .new \
 import *""", r"""
Module - ROOT 0,0..2,9
  .body[1]
  0] ImportFrom - 0,0..2,9
    .module 'new'
    .names[1]
    0] alias - 2,8..2,9
      .name '*'
    .level 2
"""),

(r"""from a.b import c""", 'body[0]', None, 'module', {}, r"""**DEL**""", r"""**ValueError('cannot delete ImportFrom.module in this state')**""", r"""
"""),

(r"""from a.b import c""", 'body[0]', None, 'module', {}, r"""new""", r"""from new import c""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] ImportFrom - 0,0..0,17
    .module 'new'
    .names[1]
    0] alias - 0,16..0,17
      .name 'c'
    .level 0
"""),

(r"""from a.b import c""", 'body[0]', None, 'module', {}, r"""x.y""", r"""from x.y import c""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] ImportFrom - 0,0..0,17
    .module 'x.y'
    .names[1]
    0] alias - 0,16..0,17
      .name 'c'
    .level 0
"""),

(r"""from .a.b import c""", 'body[0]', None, 'module', {}, r"""**DEL**""", r"""from . import c""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] ImportFrom - 0,0..0,15
    .names[1]
    0] alias - 0,14..0,15
      .name 'c'
    .level 1
"""),

(r"""from .a.b import c""", 'body[0]', None, 'module', {}, r"""new""", r"""from .new import c""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ImportFrom - 0,0..0,18
    .module 'new'
    .names[1]
    0] alias - 0,17..0,18
      .name 'c'
    .level 1
"""),

(r"""from .a.b import c""", 'body[0]', None, 'module', {}, r"""x.y""", r"""from .x.y import c""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ImportFrom - 0,0..0,18
    .module 'x.y'
    .names[1]
    0] alias - 0,17..0,18
      .name 'c'
    .level 1
"""),

(r"""from ..a.b import c""", 'body[0]', None, 'module', {}, r"""**DEL**""", r"""from .. import c""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] ImportFrom - 0,0..0,16
    .names[1]
    0] alias - 0,15..0,16
      .name 'c'
    .level 2
"""),

(r"""from ..a.b import c""", 'body[0]', None, 'module', {}, r"""new""", r"""from ..new import c""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] ImportFrom - 0,0..0,19
    .module 'new'
    .names[1]
    0] alias - 0,18..0,19
      .name 'c'
    .level 2
"""),

(r"""from ..a.b import c""", 'body[0]', None, 'module', {}, r"""x.y""", r"""from ..x.y import c""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] ImportFrom - 0,0..0,19
    .module 'x.y'
    .names[1]
    0] alias - 0,18..0,19
      .name 'c'
    .level 2
"""),

(r"""import a as b""", 'body[0].names[0]', None, 'asname', {}, r"""new""", r"""import a as new""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Import - 0,0..0,15
    .names[1]
    0] alias - 0,7..0,15
      .name 'a'
      .asname
        'new'
"""),

(r"""import a as b""", 'body[0].names[0]', None, 'asname', {}, r"""**DEL**""", r"""import a""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Import - 0,0..0,8
    .names[1]
    0] alias - 0,7..0,8
      .name 'a'
"""),

(r"""import a""", 'body[0].names[0]', None, 'asname', {}, r"""new""", r"""import a as new""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Import - 0,0..0,15
    .names[1]
    0] alias - 0,7..0,15
      .name 'a'
      .asname
        'new'
"""),

(r"""import a""", 'body[0].names[0]', None, 'asname', {}, r"""**DEL**""", r"""import a""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Import - 0,0..0,8
    .names[1]
    0] alias - 0,7..0,8
      .name 'a'
"""),

(r"""import a as b, c""", 'body[0].names[0]', None, 'asname', {}, r"""new""", r"""import a as new, c""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Import - 0,0..0,18
    .names[2]
    0] alias - 0,7..0,15
      .name 'a'
      .asname
        'new'
    1] alias - 0,17..0,18
      .name 'c'
"""),

(r"""import a as b, c""", 'body[0].names[0]', None, 'asname', {}, r"""**DEL**""", r"""import a, c""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Import - 0,0..0,11
    .names[2]
    0] alias - 0,7..0,8
      .name 'a'
    1] alias - 0,10..0,11
      .name 'c'
"""),

(r"""import a, c""", 'body[0].names[0]', None, 'asname', {}, r"""new""", r"""import a as new, c""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Import - 0,0..0,18
    .names[2]
    0] alias - 0,7..0,15
      .name 'a'
      .asname
        'new'
    1] alias - 0,17..0,18
      .name 'c'
"""),

(r"""import a, c""", 'body[0].names[0]', None, 'asname', {}, r"""**DEL**""", r"""import a, c""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Import - 0,0..0,11
    .names[2]
    0] alias - 0,7..0,8
      .name 'a'
    1] alias - 0,10..0,11
      .name 'c'
"""),

(r"""import c, a as b""", 'body[0].names[1]', None, 'asname', {}, r"""new""", r"""import c, a as new""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Import - 0,0..0,18
    .names[2]
    0] alias - 0,7..0,8
      .name 'c'
    1] alias - 0,10..0,18
      .name 'a'
      .asname
        'new'
"""),

(r"""import c, a as b""", 'body[0].names[1]', None, 'asname', {}, r"""**DEL**""", r"""import c, a""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Import - 0,0..0,11
    .names[2]
    0] alias - 0,7..0,8
      .name 'c'
    1] alias - 0,10..0,11
      .name 'a'
"""),

(r"""import c, a""", 'body[0].names[1]', None, 'asname', {}, r"""new""", r"""import c, a as new""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Import - 0,0..0,18
    .names[2]
    0] alias - 0,7..0,8
      .name 'c'
    1] alias - 0,10..0,18
      .name 'a'
      .asname
        'new'
"""),

(r"""import c, a""", 'body[0].names[1]', None, 'asname', {}, r"""**DEL**""", r"""import c, a""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Import - 0,0..0,11
    .names[2]
    0] alias - 0,7..0,8
      .name 'c'
    1] alias - 0,10..0,11
      .name 'a'
"""),

(r"""from z import (a as b)""", 'body[0].names[0]', None, 'asname', {}, r"""new""", r"""from z import (a as new)""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] ImportFrom - 0,0..0,24
    .module 'z'
    .names[1]
    0] alias - 0,15..0,23
      .name 'a'
      .asname
        'new'
    .level 0
"""),

(r"""from z import (a as b)""", 'body[0].names[0]', None, 'asname', {}, r"""**DEL**""", r"""from z import (a)""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] ImportFrom - 0,0..0,17
    .module 'z'
    .names[1]
    0] alias - 0,15..0,16
      .name 'a'
    .level 0
"""),

(r"""from z import (a)""", 'body[0].names[0]', None, 'asname', {}, r"""new""", r"""from z import (a as new)""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] ImportFrom - 0,0..0,24
    .module 'z'
    .names[1]
    0] alias - 0,15..0,23
      .name 'a'
      .asname
        'new'
    .level 0
"""),

(r"""from z import (a)""", 'body[0].names[0]', None, 'asname', {}, r"""**DEL**""", r"""from z import (a)""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] ImportFrom - 0,0..0,17
    .module 'z'
    .names[1]
    0] alias - 0,15..0,16
      .name 'a'
    .level 0
"""),

(r"""from z import (a as b, c)""", 'body[0].names[0]', None, 'asname', {}, r"""new""", r"""from z import (a as new, c)""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] ImportFrom - 0,0..0,27
    .module 'z'
    .names[2]
    0] alias - 0,15..0,23
      .name 'a'
      .asname
        'new'
    1] alias - 0,25..0,26
      .name 'c'
    .level 0
"""),

(r"""from z import (a as b, c)""", 'body[0].names[0]', None, 'asname', {}, r"""**DEL**""", r"""from z import (a, c)""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] ImportFrom - 0,0..0,20
    .module 'z'
    .names[2]
    0] alias - 0,15..0,16
      .name 'a'
    1] alias - 0,18..0,19
      .name 'c'
    .level 0
"""),

(r"""from z import (a, c)""", 'body[0].names[0]', None, 'asname', {}, r"""new""", r"""from z import (a as new, c)""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] ImportFrom - 0,0..0,27
    .module 'z'
    .names[2]
    0] alias - 0,15..0,23
      .name 'a'
      .asname
        'new'
    1] alias - 0,25..0,26
      .name 'c'
    .level 0
"""),

(r"""from z import (a, c)""", 'body[0].names[0]', None, 'asname', {}, r"""**DEL**""", r"""from z import (a, c)""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] ImportFrom - 0,0..0,20
    .module 'z'
    .names[2]
    0] alias - 0,15..0,16
      .name 'a'
    1] alias - 0,18..0,19
      .name 'c'
    .level 0
"""),

(r"""from z import (c, b as a)""", 'body[0].names[1]', None, 'asname', {}, r"""new""", r"""from z import (c, b as new)""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] ImportFrom - 0,0..0,27
    .module 'z'
    .names[2]
    0] alias - 0,15..0,16
      .name 'c'
    1] alias - 0,18..0,26
      .name 'b'
      .asname
        'new'
    .level 0
"""),

(r"""from z import (c, a as b)""", 'body[0].names[1]', None, 'asname', {}, r"""**DEL**""", r"""from z import (c, a)""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] ImportFrom - 0,0..0,20
    .module 'z'
    .names[2]
    0] alias - 0,15..0,16
      .name 'c'
    1] alias - 0,18..0,19
      .name 'a'
    .level 0
"""),

(r"""from z import (c, a)""", 'body[0].names[1]', None, 'asname', {}, r"""new""", r"""from z import (c, a as new)""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] ImportFrom - 0,0..0,27
    .module 'z'
    .names[2]
    0] alias - 0,15..0,16
      .name 'c'
    1] alias - 0,18..0,26
      .name 'a'
      .asname
        'new'
    .level 0
"""),

(r"""from z import (c, a)""", 'body[0].names[1]', None, 'asname', {}, r"""**DEL**""", r"""from z import (c, a)""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] ImportFrom - 0,0..0,20
    .module 'z'
    .names[2]
    0] alias - 0,15..0,16
      .name 'c'
    1] alias - 0,18..0,19
      .name 'a'
    .level 0
"""),

(r"""match a:
 case None: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""True""", r"""match a:
 case True: pass""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] Match - 0,0..1,16
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,16
      .pattern MatchSingleton - 1,6..1,10
        .value True
      .body[1]
      0] Pass - 1,12..1,16
"""),

(r"""match a:
 case None: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""False""", r"""match a:
 case False: pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchSingleton - 1,6..1,11
        .value False
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case None: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""None""", r"""match a:
 case None: pass""", r"""
Module - ROOT 0,0..1,16
  .body[1]
  0] Match - 0,0..1,16
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,16
      .pattern MatchSingleton - 1,6..1,10
      .body[1]
      0] Pass - 1,12..1,16
"""),

(r"""match a:
 case None: pass""", 'body[0].cases[0].pattern', None, None, {'raw': False}, r"""new""", r"""**NodeError('invalid value for MatchSingleton.value')**""", r"""
"""),

(r"""match a:
 case None: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""**DEL**""", r"""**ValueError('cannot delete MatchSingleton.value')**""", r"""
"""),

(r"""match a:
 case 1 as a: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""new""", r"""match a:
 case 1 as new: pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchAs - 1,6..1,14
        .pattern MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        .name 'new'
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""match a:
 case (1) as a: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""new""", r"""match a:
 case (1) as new: pass""", r"""
Module - ROOT 0,0..1,22
  .body[1]
  0] Match - 0,0..1,22
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,22
      .pattern MatchAs - 1,6..1,16
        .pattern MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        .name 'new'
      .body[1]
      0] Pass - 1,18..1,22
"""),

(r"""match a:
 case (1 as a): pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""new""", r"""match a:
 case (1 as new): pass""", r"""
Module - ROOT 0,0..1,22
  .body[1]
  0] Match - 0,0..1,22
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,22
      .pattern MatchAs - 1,7..1,15
        .pattern MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        .name 'new'
      .body[1]
      0] Pass - 1,18..1,22
"""),

(r"""match a:
 case 1 | 2 as a: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""new""", r"""match a:
 case 1 | 2 as new: pass""", r"""
Module - ROOT 0,0..1,24
  .body[1]
  0] Match - 0,0..1,24
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,24
      .pattern MatchAs - 1,6..1,18
        .pattern MatchOr - 1,6..1,11
          .patterns[2]
          0] MatchValue - 1,6..1,7
            .value Constant 1 - 1,6..1,7
          1] MatchValue - 1,10..1,11
            .value Constant 2 - 1,10..1,11
        .name 'new'
      .body[1]
      0] Pass - 1,20..1,24
"""),

(r"""match a:
 case 1 | (2 as a): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {}, r"""new""", r"""match a:
 case 1 | (2 as new): pass""", r"""
Module - ROOT 0,0..1,26
  .body[1]
  0] Match - 0,0..1,26
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,26
      .pattern MatchOr - 1,6..1,20
        .patterns[2]
        0] MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        1] MatchAs - 1,11..1,19
          .pattern MatchValue - 1,11..1,12
            .value Constant 2 - 1,11..1,12
          .name 'new'
      .body[1]
      0] Pass - 1,22..1,26
"""),

(r"""match a:
 case (1 | 2 as a): pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""new""", r"""match a:
 case (1 | 2 as new): pass""", r"""
Module - ROOT 0,0..1,26
  .body[1]
  0] Match - 0,0..1,26
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,26
      .pattern MatchAs - 1,7..1,19
        .pattern MatchOr - 1,7..1,12
          .patterns[2]
          0] MatchValue - 1,7..1,8
            .value Constant 1 - 1,7..1,8
          1] MatchValue - 1,11..1,12
            .value Constant 2 - 1,11..1,12
        .name 'new'
      .body[1]
      0] Pass - 1,22..1,26
"""),

(r"""match a:
 case (1 | (2 as a)): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {}, r"""new""", r"""match a:
 case (1 | (2 as new)): pass""", r"""
Module - ROOT 0,0..1,28
  .body[1]
  0] Match - 0,0..1,28
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,28
      .pattern MatchOr - 1,7..1,21
        .patterns[2]
        0] MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        1] MatchAs - 1,12..1,20
          .pattern MatchValue - 1,12..1,13
            .value Constant 2 - 1,12..1,13
          .name 'new'
      .body[1]
      0] Pass - 1,24..1,28
"""),

(r"""match a:
 case (1 as a) | 2: pass""", 'body[0].cases[0].pattern.patterns[0]', None, 'name', {}, r"""new""", r"""match a:
 case (1 as new) | 2: pass""", r"""
Module - ROOT 0,0..1,26
  .body[1]
  0] Match - 0,0..1,26
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,26
      .pattern MatchOr - 1,6..1,20
        .patterns[2]
        0] MatchAs - 1,7..1,15
          .pattern MatchValue - 1,7..1,8
            .value Constant 1 - 1,7..1,8
          .name 'new'
        1] MatchValue - 1,19..1,20
          .value Constant 2 - 1,19..1,20
      .body[1]
      0] Pass - 1,22..1,26
"""),

(r"""match a:
 case ((1 as a) | 2): pass""", 'body[0].cases[0].pattern.patterns[0]', None, 'name', {}, r"""new""", r"""match a:
 case ((1 as new) | 2): pass""", r"""
Module - ROOT 0,0..1,28
  .body[1]
  0] Match - 0,0..1,28
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,28
      .pattern MatchOr - 1,7..1,21
        .patterns[2]
        0] MatchAs - 1,8..1,16
          .pattern MatchValue - 1,8..1,9
            .value Constant 1 - 1,8..1,9
          .name 'new'
        1] MatchValue - 1,20..1,21
          .value Constant 2 - 1,20..1,21
      .body[1]
      0] Pass - 1,24..1,28
"""),

(r"""match a:
 case 1 as a: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""_""", r"""**ValueError("cannot change MatchAs with pattern into wildcard '_'")**""", r"""
"""),

(r"""match a:
 case 1 as a: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""**DEL**""", r"""**ValueError("cannot change MatchAs with pattern into wildcard '_'")**""", r"""
"""),

(r"""match a:
 case a: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""new""", r"""match a:
 case new: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchAs - 1,6..1,9
        .name 'new'
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case a: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""_""", r"""match a:
 case _: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case a: pass""", 'body[0].cases[0].pattern', None, 'name', {'raw': False}, r"""**DEL**""", r"""match a:
 case _: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case _: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""new""", r"""match a:
 case new: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchAs - 1,6..1,9
        .name 'new'
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case _: pass""", 'body[0].cases[0].pattern', None, 'name', {}, r"""_""", r"""match a:
 case _: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case _: pass""", 'body[0].cases[0].pattern', None, 'name', {'raw': False}, r"""**DEL**""", r"""match a:
 case _: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case 1 | (a): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {'raw': False}, r"""**DEL**""", r"""match a:
 case 1 | (_): pass""", r"""
Module - ROOT 0,0..1,19
  .body[1]
  0] Match - 0,0..1,19
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,19
      .pattern MatchOr - 1,6..1,13
        .patterns[2]
        0] MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        1] MatchAs - 1,11..1,12
      .body[1]
      0] Pass - 1,15..1,19
"""),

(r"""match a:
 case (1 | (a)): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {'raw': False}, r"""**DEL**""", r"""match a:
 case (1 | (_)): pass""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Match - 0,0..1,21
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,21
      .pattern MatchOr - 1,7..1,14
        .patterns[2]
        0] MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        1] MatchAs - 1,12..1,13
      .body[1]
      0] Pass - 1,17..1,21
"""),

(r"""match a:
 case 1 | (_): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {}, r"""new""", r"""match a:
 case 1 | (new): pass""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Match - 0,0..1,21
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,21
      .pattern MatchOr - 1,6..1,15
        .patterns[2]
        0] MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        1] MatchAs - 1,11..1,14
          .name 'new'
      .body[1]
      0] Pass - 1,17..1,21
"""),

(r"""match a:
 case (1 | (_)): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {}, r"""new""", r"""match a:
 case (1 | (new)): pass""", r"""
Module - ROOT 0,0..1,23
  .body[1]
  0] Match - 0,0..1,23
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,23
      .pattern MatchOr - 1,7..1,16
        .patterns[2]
        0] MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        1] MatchAs - 1,12..1,15
          .name 'new'
      .body[1]
      0] Pass - 1,19..1,23
"""),

(r"""match a:
 case 1, *b: pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {}, r"""new""", r"""match a:
 case 1, *new: pass""", r"""
Module - ROOT 0,0..1,19
  .body[1]
  0] Match - 0,0..1,19
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,19
      .pattern MatchSequence - 1,6..1,13
        .patterns[2]
        0] MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        1] MatchStar - 1,9..1,13
          .name 'new'
      .body[1]
      0] Pass - 1,15..1,19
"""),

(r"""match a:
 case 1, *b: pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {}, r"""_""", r"""match a:
 case 1, *_: pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchSequence - 1,6..1,11
        .patterns[2]
        0] MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        1] MatchStar - 1,9..1,11
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case 1, *b: pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {'raw': False}, r"""**DEL**""", r"""match a:
 case 1, *_: pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchSequence - 1,6..1,11
        .patterns[2]
        0] MatchValue - 1,6..1,7
          .value Constant 1 - 1,6..1,7
        1] MatchStar - 1,9..1,11
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case (1, *b): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {}, r"""new""", r"""match a:
 case (1, *new): pass""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Match - 0,0..1,21
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,21
      .pattern MatchSequence - 1,6..1,15
        .patterns[2]
        0] MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        1] MatchStar - 1,10..1,14
          .name 'new'
      .body[1]
      0] Pass - 1,17..1,21
"""),

(r"""match a:
 case (1, *b): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {}, r"""_""", r"""match a:
 case (1, *_): pass""", r"""
Module - ROOT 0,0..1,19
  .body[1]
  0] Match - 0,0..1,19
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,19
      .pattern MatchSequence - 1,6..1,13
        .patterns[2]
        0] MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        1] MatchStar - 1,10..1,12
      .body[1]
      0] Pass - 1,15..1,19
"""),

(r"""match a:
 case (1, *b): pass""", 'body[0].cases[0].pattern.patterns[1]', None, 'name', {'raw': False}, r"""**DEL**""", r"""match a:
 case (1, *_): pass""", r"""
Module - ROOT 0,0..1,19
  .body[1]
  0] Match - 0,0..1,19
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,19
      .pattern MatchSequence - 1,6..1,13
        .patterns[2]
        0] MatchValue - 1,7..1,8
          .value Constant 1 - 1,7..1,8
        1] MatchStar - 1,10..1,12
      .body[1]
      0] Pass - 1,15..1,19
"""),

(r"""match a:
 case *b,: pass""", 'body[0].cases[0].pattern.patterns[0]', None, 'name', {}, r"""new""", r"""match a:
 case *new,: pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchSequence - 1,6..1,11
        .patterns[1]
        0] MatchStar - 1,6..1,10
          .name 'new'
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case *b,: pass""", 'body[0].cases[0].pattern.patterns[0]', None, 'name', {}, r"""_""", r"""match a:
 case *_,: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchSequence - 1,6..1,9
        .patterns[1]
        0] MatchStar - 1,6..1,8
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case *b,: pass""", 'body[0].cases[0].pattern.patterns[0]', None, 'name', {'raw': False}, r"""**DEL**""", r"""match a:
 case *_,: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchSequence - 1,6..1,9
        .patterns[1]
        0] MatchStar - 1,6..1,8
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case *_,: pass""", 'body[0].cases[0].pattern.patterns[0]', None, 'name', {}, r"""new""", r"""match a:
 case *new,: pass""", r"""
Module - ROOT 0,0..1,17
  .body[1]
  0] Match - 0,0..1,17
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,17
      .pattern MatchSequence - 1,6..1,11
        .patterns[1]
        0] MatchStar - 1,6..1,10
          .name 'new'
      .body[1]
      0] Pass - 1,13..1,17
"""),

(r"""match a:
 case *_,: pass""", 'body[0].cases[0].pattern.patterns[0]', None, 'name', {}, r"""_""", r"""match a:
 case *_,: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchSequence - 1,6..1,9
        .patterns[1]
        0] MatchStar - 1,6..1,8
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case *_,: pass""", 'body[0].cases[0].pattern.patterns[0]', None, 'name', {'raw': False}, r"""**DEL**""", r"""match a:
 case *_,: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchSequence - 1,6..1,9
        .patterns[1]
        0] MatchStar - 1,6..1,8
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case {}: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""new""", r"""match a:
 case {**new}: pass""", r"""
Module - ROOT 0,0..1,19
  .body[1]
  0] Match - 0,0..1,19
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,19
      .pattern MatchMapping - 1,6..1,13
        .rest 'new'
      .body[1]
      0] Pass - 1,15..1,19
"""),

(r"""match a:
 case {1: a}: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""new""", r"""match a:
 case {1: a, **new}: pass""", r"""
Module - ROOT 0,0..1,25
  .body[1]
  0] Match - 0,0..1,25
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,25
      .pattern MatchMapping - 1,6..1,19
        .keys[1]
        0] Constant 1 - 1,7..1,8
        .patterns[1]
        0] MatchAs - 1,10..1,11
          .name 'a'
        .rest 'new'
      .body[1]
      0] Pass - 1,21..1,25
"""),

(r"""match a:
 case {1: a, }: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""new""", r"""match a:
 case {1: a, **new}: pass""", r"""
Module - ROOT 0,0..1,25
  .body[1]
  0] Match - 0,0..1,25
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,25
      .pattern MatchMapping - 1,6..1,19
        .keys[1]
        0] Constant 1 - 1,7..1,8
        .patterns[1]
        0] MatchAs - 1,10..1,11
          .name 'a'
        .rest 'new'
      .body[1]
      0] Pass - 1,21..1,25
"""),

(r"""match a:
 case {**b}: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""new""", r"""match a:
 case {**new}: pass""", r"""
Module - ROOT 0,0..1,19
  .body[1]
  0] Match - 0,0..1,19
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,19
      .pattern MatchMapping - 1,6..1,13
        .rest 'new'
      .body[1]
      0] Pass - 1,15..1,19
"""),

(r"""match a:
 case {1: a, **b}: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""new""", r"""match a:
 case {1: a, **new}: pass""", r"""
Module - ROOT 0,0..1,25
  .body[1]
  0] Match - 0,0..1,25
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,25
      .pattern MatchMapping - 1,6..1,19
        .keys[1]
        0] Constant 1 - 1,7..1,8
        .patterns[1]
        0] MatchAs - 1,10..1,11
          .name 'a'
        .rest 'new'
      .body[1]
      0] Pass - 1,21..1,25
"""),

(r"""match a:
 case {1: a,  ** b }: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""new""", r"""match a:
 case {1: a,  ** new }: pass""", r"""
Module - ROOT 0,0..1,28
  .body[1]
  0] Match - 0,0..1,28
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,28
      .pattern MatchMapping - 1,6..1,22
        .keys[1]
        0] Constant 1 - 1,7..1,8
        .patterns[1]
        0] MatchAs - 1,10..1,11
          .name 'a'
        .rest 'new'
      .body[1]
      0] Pass - 1,24..1,28
"""),

(r"""match a:
 case {**b}: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""**DEL**""", r"""match a:
 case {}: pass""", r"""
Module - ROOT 0,0..1,14
  .body[1]
  0] Match - 0,0..1,14
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,14
      .pattern MatchMapping - 1,6..1,8
      .body[1]
      0] Pass - 1,10..1,14
"""),

(r"""match a:
 case {1: a, **b}: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""**DEL**""", r"""match a:
 case {1: a}: pass""", r"""
Module - ROOT 0,0..1,18
  .body[1]
  0] Match - 0,0..1,18
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,18
      .pattern MatchMapping - 1,6..1,12
        .keys[1]
        0] Constant 1 - 1,7..1,8
        .patterns[1]
        0] MatchAs - 1,10..1,11
          .name 'a'
      .body[1]
      0] Pass - 1,14..1,18
"""),

(r"""match a:
 case {1: a,  ** b }: pass""", 'body[0].cases[0].pattern', None, 'rest', {}, r"""**DEL**""", r"""match a:
 case {1: a}: pass""", r"""
Module - ROOT 0,0..1,18
  .body[1]
  0] Match - 0,0..1,18
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,18
      .pattern MatchMapping - 1,6..1,12
        .keys[1]
        0] Constant 1 - 1,7..1,8
        .patterns[1]
        0] MatchAs - 1,10..1,11
          .name 'a'
      .body[1]
      0] Pass - 1,14..1,18
"""),

(r"""match a:
 case cls(a=b): pass""", 'body[0].cases[0].pattern', 0, 'kwd_attrs', {}, r"""new""", r"""match a:
 case cls(new=b): pass""", r"""
Module - ROOT 0,0..1,22
  .body[1]
  0] Match - 0,0..1,22
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,22
      .pattern MatchClass - 1,6..1,16
        .cls Name 'cls' Load - 1,6..1,9
        .kwd_attrs[1]
        0] 'new'
        .kwd_patterns[1]
        0] MatchAs - 1,14..1,15
          .name 'b'
      .body[1]
      0] Pass - 1,18..1,22
"""),

(r"""match a:
 case cls(a=b): pass""", 'body[0].cases[0].pattern', 0, 'kwd_attrs', {}, r"""**DEL**""", r"""**ValueError('cannot delete MatchClass.kwd_attrs[0]')**""", r"""
"""),

(r"""match a:
 case cls(a=b): pass""", 'body[0].cases[0].pattern', 0, 'kwd_attrs', {}, r"""1""", r"""**NodeError("expecting identifier, got '1'")**""", r"""
"""),

(r"""match a:
 case cls(a=b, c=d): pass""", 'body[0].cases[0].pattern', 1, 'kwd_attrs', {}, r"""new""", r"""match a:
 case cls(a=b, new=d): pass""", r"""
Module - ROOT 0,0..1,27
  .body[1]
  0] Match - 0,0..1,27
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,27
      .pattern MatchClass - 1,6..1,21
        .cls Name 'cls' Load - 1,6..1,9
        .kwd_attrs[2]
        0] 'a'
        1] 'new'
        .kwd_patterns[2]
        0] MatchAs - 1,12..1,13
          .name 'b'
        1] MatchAs - 1,19..1,20
          .name 'd'
      .body[1]
      0] Pass - 1,23..1,27
"""),

(r"""match a:
 case cls(a=(b), c=d): pass""", 'body[0].cases[0].pattern', 1, 'kwd_attrs', {}, r"""new""", r"""match a:
 case cls(a=(b), new=d): pass""", r"""
Module - ROOT 0,0..1,29
  .body[1]
  0] Match - 0,0..1,29
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,29
      .pattern MatchClass - 1,6..1,23
        .cls Name 'cls' Load - 1,6..1,9
        .kwd_attrs[2]
        0] 'a'
        1] 'new'
        .kwd_patterns[2]
        0] MatchAs - 1,13..1,14
          .name 'b'
        1] MatchAs - 1,21..1,22
          .name 'd'
      .body[1]
      0] Pass - 1,25..1,29
"""),

(r"""match a:
 case cls( a = ( b ) , c=d): pass""", 'body[0].cases[0].pattern', 0, 'kwd_attrs', {}, r"""new""", r"""match a:
 case cls( new = ( b ) , c=d): pass""", r"""
Module - ROOT 0,0..1,35
  .body[1]
  0] Match - 0,0..1,35
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,35
      .pattern MatchClass - 1,6..1,29
        .cls Name 'cls' Load - 1,6..1,9
        .kwd_attrs[2]
        0] 'new'
        1] 'c'
        .kwd_patterns[2]
        0] MatchAs - 1,19..1,20
          .name 'b'
        1] MatchAs - 1,27..1,28
          .name 'd'
      .body[1]
      0] Pass - 1,31..1,35
"""),

(r"""match a:
 case cls(a=(b),  c = d): pass""", 'body[0].cases[0].pattern', 1, 'kwd_attrs', {}, r"""new""", r"""match a:
 case cls(a=(b),  new = d): pass""", r"""
Module - ROOT 0,0..1,32
  .body[1]
  0] Match - 0,0..1,32
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,32
      .pattern MatchClass - 1,6..1,26
        .cls Name 'cls' Load - 1,6..1,9
        .kwd_attrs[2]
        0] 'a'
        1] 'new'
        .kwd_patterns[2]
        0] MatchAs - 1,13..1,14
          .name 'b'
        1] MatchAs - 1,24..1,25
          .name 'd'
      .body[1]
      0] Pass - 1,28..1,32
"""),

(r"""del a, (b), c""", 'body[0]', 0, None, {}, r"""**DEL**""", r"""**ValueError('cannot put slice to Delete.targets')**""", r"""
"""),

(r"""del a, (b), c""", 'body[0]', 0, None, {}, r"""new""", r"""del new, (b), c""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Delete - 0,0..0,15
    .targets[3]
    0] Name 'new' Del - 0,4..0,7
    1] Name 'b' Del - 0,10..0,11
    2] Name 'c' Del - 0,14..0,15
"""),

(r"""del a, (b), c""", 'body[0]', 1, None, {}, r"""new""", r"""del a, new, c""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Delete - 0,0..0,13
    .targets[3]
    0] Name 'a' Del - 0,4..0,5
    1] Name 'new' Del - 0,7..0,10
    2] Name 'c' Del - 0,12..0,13
"""),

(r"""del a, (b), c""", 'body[0]', 2, None, {}, r"""new""", r"""del a, (b), new""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Delete - 0,0..0,15
    .targets[3]
    0] Name 'a' Del - 0,4..0,5
    1] Name 'b' Del - 0,8..0,9
    2] Name 'new' Del - 0,12..0,15
"""),

(r"""del a, (b), c""", 'body[0]', -1, None, {}, r"""new""", r"""del a, (b), new""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Delete - 0,0..0,15
    .targets[3]
    0] Name 'a' Del - 0,4..0,5
    1] Name 'b' Del - 0,8..0,9
    2] Name 'new' Del - 0,12..0,15
"""),

(r"""del a, (b), c""", 'body[0]', -1, None, {'raw': False}, r"""x, y""", r"""del a, (b), (x, y)""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Delete - 0,0..0,18
    .targets[3]
    0] Name 'a' Del - 0,4..0,5
    1] Name 'b' Del - 0,8..0,9
    2] Tuple - 0,12..0,18
      .elts[2]
      0] Name 'x' Del - 0,13..0,14
      1] Name 'y' Del - 0,16..0,17
      .ctx Del
"""),

(r"""del a, (b), c""", 'body[0]', -1, None, {}, r"""f()""", r"""**NodeError('expecting one of (Name, Attribute, Subscript, Tuple, List) for Delete.targets[-1], got Call')**""", r"""
"""),

(r"""del a, (b), c""", 'body[0]', -4, None, {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""a = (b, c) = d = z""", 'body[0]', 0, 'targets', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to Assign.targets')**""", r"""
"""),

(r"""a = (b, c) = d = z""", 'body[0]', 0, 'targets', {}, r"""new""", r"""new = (b, c) = d = z""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Assign - 0,0..0,20
    .targets[3]
    0] Name 'new' Store - 0,0..0,3
    1] Tuple - 0,6..0,12
      .elts[2]
      0] Name 'b' Store - 0,7..0,8
      1] Name 'c' Store - 0,10..0,11
      .ctx Store
    2] Name 'd' Store - 0,15..0,16
    .value Name 'z' Load - 0,19..0,20
"""),

(r"""a = (b, c) = d = z""", 'body[0]', 1, 'targets', {}, r"""new""", r"""a = new = d = z""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Assign - 0,0..0,15
    .targets[3]
    0] Name 'a' Store - 0,0..0,1
    1] Name 'new' Store - 0,4..0,7
    2] Name 'd' Store - 0,10..0,11
    .value Name 'z' Load - 0,14..0,15
"""),

(r"""a = (b, c) = d = z""", 'body[0]', 2, 'targets', {}, r"""new""", r"""a = (b, c) = new = z""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Assign - 0,0..0,20
    .targets[3]
    0] Name 'a' Store - 0,0..0,1
    1] Tuple - 0,4..0,10
      .elts[2]
      0] Name 'b' Store - 0,5..0,6
      1] Name 'c' Store - 0,8..0,9
      .ctx Store
    2] Name 'new' Store - 0,13..0,16
    .value Name 'z' Load - 0,19..0,20
"""),

(r"""a = (b, c) = d = z""", 'body[0]', -1, 'targets', {}, r"""new""", r"""a = (b, c) = new = z""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Assign - 0,0..0,20
    .targets[3]
    0] Name 'a' Store - 0,0..0,1
    1] Tuple - 0,4..0,10
      .elts[2]
      0] Name 'b' Store - 0,5..0,6
      1] Name 'c' Store - 0,8..0,9
      .ctx Store
    2] Name 'new' Store - 0,13..0,16
    .value Name 'z' Load - 0,19..0,20
"""),

(r"""a = (b, c) = d = z""", 'body[0]', -1, 'targets', {}, r"""x, y""", r"""a = (b, c) = x, y = z""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] Assign - 0,0..0,21
    .targets[3]
    0] Name 'a' Store - 0,0..0,1
    1] Tuple - 0,4..0,10
      .elts[2]
      0] Name 'b' Store - 0,5..0,6
      1] Name 'c' Store - 0,8..0,9
      .ctx Store
    2] Tuple - 0,13..0,17
      .elts[2]
      0] Name 'x' Store - 0,13..0,14
      1] Name 'y' Store - 0,16..0,17
      .ctx Store
    .value Name 'z' Load - 0,20..0,21
"""),

(r"""del a, (b, c), d""", 'body[0]', -1, 'targets', {}, r"""f()""", r"""**NodeError('expecting one of (Name, Attribute, Subscript, Tuple, List) for Delete.targets[-1], got Call')**""", r"""
"""),

(r"""del a, (b, c), d""", 'body[0]', -4, 'targets', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""@a
@(b)
def c(): pass""", 'body[0]', 0, 'decorator_list', {'raw': False}, r"""**DEL**""", r"""**ValueError('cannot put slice to FunctionDef.decorator_list')**""", r"""
"""),

(r"""@a
@(b)
def c(): pass""", 'body[0]', 0, 'decorator_list', {}, r"""new""", r"""@new
@(b)
def c(): pass""", r"""
Module - ROOT 0,0..2,13
  .body[1]
  0] FunctionDef - 2,0..2,13
    .name 'c'
    .body[1]
    0] Pass - 2,9..2,13
    .decorator_list[2]
    0] Name 'new' Load - 0,1..0,4
    1] Name 'b' Load - 1,2..1,3
"""),

(r"""@a
@(b)
def c(): pass""", 'body[0]', 1, 'decorator_list', {}, r"""new""", r"""@a
@new
def c(): pass""", r"""
Module - ROOT 0,0..2,13
  .body[1]
  0] FunctionDef - 2,0..2,13
    .name 'c'
    .body[1]
    0] Pass - 2,9..2,13
    .decorator_list[2]
    0] Name 'a' Load - 0,1..0,2
    1] Name 'new' Load - 1,1..1,4
"""),

(r"""@a
@(b)
def c(): pass""", 'body[0]', -1, 'decorator_list', {}, r"""new""", r"""@a
@new
def c(): pass""", r"""
Module - ROOT 0,0..2,13
  .body[1]
  0] FunctionDef - 2,0..2,13
    .name 'c'
    .body[1]
    0] Pass - 2,9..2,13
    .decorator_list[2]
    0] Name 'a' Load - 0,1..0,2
    1] Name 'new' Load - 1,1..1,4
"""),

(r"""@a
@(b)
def c(): pass""", 'body[0]', -2, 'decorator_list', {}, r"""f()""", r"""@f()
@(b)
def c(): pass""", r"""
Module - ROOT 0,0..2,13
  .body[1]
  0] FunctionDef - 2,0..2,13
    .name 'c'
    .body[1]
    0] Pass - 2,9..2,13
    .decorator_list[2]
    0] Call - 0,1..0,4
      .func Name 'f' Load - 0,1..0,2
    1] Name 'b' Load - 1,2..1,3
"""),

(r"""@a
@(b)
def c(): pass""", 'body[0]', -4, 'decorator_list', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""@a
@(b)
async def c(): pass""", 'body[0]', 0, 'decorator_list', {'raw': False}, r"""**DEL**""", r"""**ValueError('cannot put slice to AsyncFunctionDef.decorator_list')**""", r"""
"""),

(r"""@a
@(b)
async def c(): pass""", 'body[0]', 0, 'decorator_list', {}, r"""new""", r"""@new
@(b)
async def c(): pass""", r"""
Module - ROOT 0,0..2,19
  .body[1]
  0] AsyncFunctionDef - 2,0..2,19
    .name 'c'
    .body[1]
    0] Pass - 2,15..2,19
    .decorator_list[2]
    0] Name 'new' Load - 0,1..0,4
    1] Name 'b' Load - 1,2..1,3
"""),

(r"""@a
@(b)
async def c(): pass""", 'body[0]', 1, 'decorator_list', {}, r"""new""", r"""@a
@new
async def c(): pass""", r"""
Module - ROOT 0,0..2,19
  .body[1]
  0] AsyncFunctionDef - 2,0..2,19
    .name 'c'
    .body[1]
    0] Pass - 2,15..2,19
    .decorator_list[2]
    0] Name 'a' Load - 0,1..0,2
    1] Name 'new' Load - 1,1..1,4
"""),

(r"""@a
@(b)
async def c(): pass""", 'body[0]', -1, 'decorator_list', {}, r"""new""", r"""@a
@new
async def c(): pass""", r"""
Module - ROOT 0,0..2,19
  .body[1]
  0] AsyncFunctionDef - 2,0..2,19
    .name 'c'
    .body[1]
    0] Pass - 2,15..2,19
    .decorator_list[2]
    0] Name 'a' Load - 0,1..0,2
    1] Name 'new' Load - 1,1..1,4
"""),

(r"""@a
@(b)
async def c(): pass""", 'body[0]', -2, 'decorator_list', {}, r"""f()""", r"""@f()
@(b)
async def c(): pass""", r"""
Module - ROOT 0,0..2,19
  .body[1]
  0] AsyncFunctionDef - 2,0..2,19
    .name 'c'
    .body[1]
    0] Pass - 2,15..2,19
    .decorator_list[2]
    0] Call - 0,1..0,4
      .func Name 'f' Load - 0,1..0,2
    1] Name 'b' Load - 1,2..1,3
"""),

(r"""@a
@(b)
async def c(): pass""", 'body[0]', -4, 'decorator_list', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""@a
@(b)
class c: pass""", 'body[0]', 0, 'decorator_list', {'raw': False}, r"""**DEL**""", r"""**ValueError('cannot put slice to ClassDef.decorator_list')**""", r"""
"""),

(r"""@a
@(b)
class c: pass""", 'body[0]', 0, 'decorator_list', {}, r"""new""", r"""@new
@(b)
class c: pass""", r"""
Module - ROOT 0,0..2,13
  .body[1]
  0] ClassDef - 2,0..2,13
    .name 'c'
    .body[1]
    0] Pass - 2,9..2,13
    .decorator_list[2]
    0] Name 'new' Load - 0,1..0,4
    1] Name 'b' Load - 1,2..1,3
"""),

(r"""@a
@(b)
class c: pass""", 'body[0]', 1, 'decorator_list', {}, r"""new""", r"""@a
@new
class c: pass""", r"""
Module - ROOT 0,0..2,13
  .body[1]
  0] ClassDef - 2,0..2,13
    .name 'c'
    .body[1]
    0] Pass - 2,9..2,13
    .decorator_list[2]
    0] Name 'a' Load - 0,1..0,2
    1] Name 'new' Load - 1,1..1,4
"""),

(r"""@a
@(b)
class c: pass""", 'body[0]', -1, 'decorator_list', {}, r"""new""", r"""@a
@new
class c: pass""", r"""
Module - ROOT 0,0..2,13
  .body[1]
  0] ClassDef - 2,0..2,13
    .name 'c'
    .body[1]
    0] Pass - 2,9..2,13
    .decorator_list[2]
    0] Name 'a' Load - 0,1..0,2
    1] Name 'new' Load - 1,1..1,4
"""),

(r"""@a
@(b)
class c: pass""", 'body[0]', -2, 'decorator_list', {}, r"""f()""", r"""@f()
@(b)
class c: pass""", r"""
Module - ROOT 0,0..2,13
  .body[1]
  0] ClassDef - 2,0..2,13
    .name 'c'
    .body[1]
    0] Pass - 2,9..2,13
    .decorator_list[2]
    0] Call - 0,1..0,4
      .func Name 'f' Load - 0,1..0,2
    1] Name 'b' Load - 1,2..1,3
"""),

(r"""@a
@(b)
class c: pass""", 'body[0]', -4, 'decorator_list', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""class c(a, (b)): pass""", 'body[0]', 0, 'bases', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to ClassDef.bases')**""", r"""
"""),

(r"""class c(a, (b)): pass""", 'body[0]', 0, 'bases', {}, r"""new""", r"""class c(new, (b)): pass""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] ClassDef - 0,0..0,23
    .name 'c'
    .bases[2]
    0] Name 'new' Load - 0,8..0,11
    1] Name 'b' Load - 0,14..0,15
    .body[1]
    0] Pass - 0,19..0,23
"""),

(r"""class c(a, (b)): pass""", 'body[0]', 1, 'bases', {}, r"""new""", r"""class c(a, new): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] ClassDef - 0,0..0,21
    .name 'c'
    .bases[2]
    0] Name 'a' Load - 0,8..0,9
    1] Name 'new' Load - 0,11..0,14
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""class c(a, (b)): pass""", 'body[0]', -1, 'bases', {}, r"""new""", r"""class c(a, new): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] ClassDef - 0,0..0,21
    .name 'c'
    .bases[2]
    0] Name 'a' Load - 0,8..0,9
    1] Name 'new' Load - 0,11..0,14
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""class c(a, (b)): pass""", 'body[0]', -2, 'bases', {}, r"""f()""", r"""class c(f(), (b)): pass""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] ClassDef - 0,0..0,23
    .name 'c'
    .bases[2]
    0] Call - 0,8..0,11
      .func Name 'f' Load - 0,8..0,9
    1] Name 'b' Load - 0,14..0,15
    .body[1]
    0] Pass - 0,19..0,23
"""),

(r"""class c(a, (b)): pass""", 'body[0]', -4, 'bases', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""class c(a): pass""", 'body[0]', 0, 'bases', {'raw': False}, r"""**DEL**""", r"""**ValueError('cannot put slice to ClassDef.bases')**""", r"""
"""),

(r"""class c(a): pass""", 'body[0]', 0, 'bases', {}, r"""new""", r"""class c(new): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ClassDef - 0,0..0,18
    .name 'c'
    .bases[1]
    0] Name 'new' Load - 0,8..0,11
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""class c(a,): pass""", 'body[0]', 0, 'bases', {}, r"""new""", r"""class c(new,): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] ClassDef - 0,0..0,19
    .name 'c'
    .bases[1]
    0] Name 'new' Load - 0,8..0,11
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""class c((a)): pass""", 'body[0]', 0, 'bases', {'raw': False}, r"""**DEL**""", r"""**ValueError('cannot put slice to ClassDef.bases')**""", r"""
"""),

(r"""class c((a)): pass""", 'body[0]', 0, 'bases', {}, r"""new""", r"""class c(new): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] ClassDef - 0,0..0,18
    .name 'c'
    .bases[1]
    0] Name 'new' Load - 0,8..0,11
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""class c((a),): pass""", 'body[0]', 0, 'bases', {}, r"""new""", r"""class c(new,): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] ClassDef - 0,0..0,19
    .name 'c'
    .bases[1]
    0] Name 'new' Load - 0,8..0,11
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""a and (b) and c""", 'body[0].value', 0, None, {'raw': False}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""a and (b) and c""", 'body[0].value', 0, None, {}, r"""new""", r"""new and (b) and c""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value BoolOp - 0,0..0,17
      .op And
      .values[3]
      0] Name 'new' Load - 0,0..0,3
      1] Name 'b' Load - 0,9..0,10
      2] Name 'c' Load - 0,16..0,17
"""),

(r"""a and (b) and c""", 'body[0].value', 1, None, {}, r"""new""", r"""a and new and c""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Expr - 0,0..0,15
    .value BoolOp - 0,0..0,15
      .op And
      .values[3]
      0] Name 'a' Load - 0,0..0,1
      1] Name 'new' Load - 0,6..0,9
      2] Name 'c' Load - 0,14..0,15
"""),

(r"""a and (b) and c""", 'body[0].value', -1, None, {}, r"""new""", r"""a and (b) and new""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value BoolOp - 0,0..0,17
      .op And
      .values[3]
      0] Name 'a' Load - 0,0..0,1
      1] Name 'b' Load - 0,7..0,8
      2] Name 'new' Load - 0,14..0,17
"""),

(r"""a and (b) and c""", 'body[0].value', -2, None, {}, r"""f()""", r"""a and f() and c""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Expr - 0,0..0,15
    .value BoolOp - 0,0..0,15
      .op And
      .values[3]
      0] Name 'a' Load - 0,0..0,1
      1] Call - 0,6..0,9
        .func Name 'f' Load - 0,6..0,7
      2] Name 'c' Load - 0,14..0,15
"""),

(r"""a and (b) and c""", 'body[0].value', -4, None, {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""[i for i in j if a if (b)]""", 'body[0].value.generators[0]', 0, 'ifs', {'raw': False}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""[i for i in j if a if (b)]""", 'body[0].value.generators[0]', 0, 'ifs', {}, r"""new""", r"""[i for i in j if new if (b)]""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] Expr - 0,0..0,28
    .value ListComp - 0,0..0,28
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,27
        .target Name 'i' Store - 0,7..0,8
        .iter Name 'j' Load - 0,12..0,13
        .ifs[2]
        0] Name 'new' Load - 0,17..0,20
        1] Name 'b' Load - 0,25..0,26
        .is_async 0
"""),

(r"""[i for i in j if a if (b)]""", 'body[0].value.generators[0]', 1, 'ifs', {}, r"""new""", r"""[i for i in j if a if new]""", r"""
Module - ROOT 0,0..0,26
  .body[1]
  0] Expr - 0,0..0,26
    .value ListComp - 0,0..0,26
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,25
        .target Name 'i' Store - 0,7..0,8
        .iter Name 'j' Load - 0,12..0,13
        .ifs[2]
        0] Name 'a' Load - 0,17..0,18
        1] Name 'new' Load - 0,22..0,25
        .is_async 0
"""),

(r"""[i for i in j if a if (b)]""", 'body[0].value.generators[0]', -1, 'ifs', {}, r"""new""", r"""[i for i in j if a if new]""", r"""
Module - ROOT 0,0..0,26
  .body[1]
  0] Expr - 0,0..0,26
    .value ListComp - 0,0..0,26
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,25
        .target Name 'i' Store - 0,7..0,8
        .iter Name 'j' Load - 0,12..0,13
        .ifs[2]
        0] Name 'a' Load - 0,17..0,18
        1] Name 'new' Load - 0,22..0,25
        .is_async 0
"""),

(r"""[i for i in j if a if (b)]""", 'body[0].value.generators[0]', -2, 'ifs', {}, r"""f()""", r"""[i for i in j if f() if (b)]""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] Expr - 0,0..0,28
    .value ListComp - 0,0..0,28
      .elt Name 'i' Load - 0,1..0,2
      .generators[1]
      0] comprehension - 0,3..0,27
        .target Name 'i' Store - 0,7..0,8
        .iter Name 'j' Load - 0,12..0,13
        .ifs[2]
        0] Call - 0,17..0,20
          .func Name 'f' Load - 0,17..0,18
        1] Name 'b' Load - 0,25..0,26
        .is_async 0
"""),

(r"""[i for i in j if a if (b)]""", 'body[0].value.generators[0]', -4, 'ifs', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""call(a, (b))""", 'body[0].value', 0, None, {}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""call(a, (b))""", 'body[0].value', 0, None, {}, r"""new""", r"""call(new, (b))""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Expr - 0,0..0,14
    .value Call - 0,0..0,14
      .func Name 'call' Load - 0,0..0,4
      .args[2]
      0] Name 'new' Load - 0,5..0,8
      1] Name 'b' Load - 0,11..0,12
"""),

(r"""call(a, (b))""", 'body[0].value', 1, None, {}, r"""new""", r"""call(a, new)""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Expr - 0,0..0,12
    .value Call - 0,0..0,12
      .func Name 'call' Load - 0,0..0,4
      .args[2]
      0] Name 'a' Load - 0,5..0,6
      1] Name 'new' Load - 0,8..0,11
"""),

(r"""call(a, (b))""", 'body[0].value', -1, None, {}, r"""new""", r"""call(a, new)""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Expr - 0,0..0,12
    .value Call - 0,0..0,12
      .func Name 'call' Load - 0,0..0,4
      .args[2]
      0] Name 'a' Load - 0,5..0,6
      1] Name 'new' Load - 0,8..0,11
"""),

(r"""call(a, (b))""", 'body[0].value', -2, None, {}, r"""f()""", r"""call(f(), (b))""", r"""
Module - ROOT 0,0..0,14
  .body[1]
  0] Expr - 0,0..0,14
    .value Call - 0,0..0,14
      .func Name 'call' Load - 0,0..0,4
      .args[2]
      0] Call - 0,5..0,8
        .func Name 'f' Load - 0,5..0,6
      1] Name 'b' Load - 0,11..0,12
"""),

(r"""call(a, (b))""", 'body[0].value', -4, None, {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""call(i for i in j)""", 'body[0].value', 0, None, {}, r"""new""", r"""call(new)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Call - 0,0..0,9
      .func Name 'call' Load - 0,0..0,4
      .args[1]
      0] Name 'new' Load - 0,5..0,8
"""),

(r"""call((i for i in j))""", 'body[0].value', 0, None, {}, r"""new""", r"""call(new)""", r"""
Module - ROOT 0,0..0,9
  .body[1]
  0] Expr - 0,0..0,9
    .value Call - 0,0..0,9
      .func Name 'call' Load - 0,0..0,4
      .args[1]
      0] Name 'new' Load - 0,5..0,8
"""),

(r"""call(i for i in j)""", 'body[0].value', 0, None, {}, r"""(a for a in b)""", r"""call((a for a in b))""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Expr - 0,0..0,20
    .value Call - 0,0..0,20
      .func Name 'call' Load - 0,0..0,4
      .args[1]
      0] GeneratorExp - 0,5..0,19
        .elt Name 'a' Load - 0,6..0,7
        .generators[1]
        0] comprehension - 0,8..0,18
          .target Name 'a' Store - 0,12..0,13
          .iter Name 'b' Load - 0,17..0,18
          .is_async 0
"""),

(r"""call((i for i in j))""", 'body[0].value', 0, None, {}, r"""(a for a in b)""", r"""call((a for a in b))""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Expr - 0,0..0,20
    .value Call - 0,0..0,20
      .func Name 'call' Load - 0,0..0,4
      .args[1]
      0] GeneratorExp - 0,5..0,19
        .elt Name 'a' Load - 0,6..0,7
        .generators[1]
        0] comprehension - 0,8..0,18
          .target Name 'a' Store - 0,12..0,13
          .iter Name 'b' Load - 0,17..0,18
          .is_async 0
"""),

(r"""match a:
 case 1 as b, (2): pass""", 'body[0].cases[0].pattern', 0, None, {}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""match a:
 case 1 as b, (2): pass""", 'body[0].cases[0].pattern', 0, None, {}, r"""new""", r"""match a:
 case new, (2): pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchSequence - 1,6..1,14
        .patterns[2]
        0] MatchAs - 1,6..1,9
          .name 'new'
        1] MatchValue - 1,12..1,13
          .value Constant 2 - 1,12..1,13
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""match a:
 case 1 as b, (2): pass""", 'body[0].cases[0].pattern', 1, None, {}, r"""new""", r"""match a:
 case 1 as b, new: pass""", r"""
Module - ROOT 0,0..1,23
  .body[1]
  0] Match - 0,0..1,23
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,23
      .pattern MatchSequence - 1,6..1,17
        .patterns[2]
        0] MatchAs - 1,6..1,12
          .pattern MatchValue - 1,6..1,7
            .value Constant 1 - 1,6..1,7
          .name 'b'
        1] MatchAs - 1,14..1,17
          .name 'new'
      .body[1]
      0] Pass - 1,19..1,23
"""),

(r"""match a:
 case 1 as b, (2): pass""", 'body[0].cases[0].pattern', -1, None, {}, r"""{1: c, **d}""", r"""match a:
 case 1 as b, {1: c, **d}: pass""", r"""
Module - ROOT 0,0..1,31
  .body[1]
  0] Match - 0,0..1,31
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,31
      .pattern MatchSequence - 1,6..1,25
        .patterns[2]
        0] MatchAs - 1,6..1,12
          .pattern MatchValue - 1,6..1,7
            .value Constant 1 - 1,6..1,7
          .name 'b'
        1] MatchMapping - 1,14..1,25
          .keys[1]
          0] Constant 1 - 1,15..1,16
          .patterns[1]
          0] MatchAs - 1,18..1,19
            .name 'c'
          .rest 'd'
      .body[1]
      0] Pass - 1,27..1,31
"""),

(r"""match a:
 case 1 as b, (2): pass""", 'body[0].cases[0].pattern', -2, None, {}, r"""f(c=d)""", r"""match a:
 case f(c=d), (2): pass""", r"""
Module - ROOT 0,0..1,23
  .body[1]
  0] Match - 0,0..1,23
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,23
      .pattern MatchSequence - 1,6..1,17
        .patterns[2]
        0] MatchClass - 1,6..1,12
          .cls Name 'f' Load - 1,6..1,7
          .kwd_attrs[1]
          0] 'c'
          .kwd_patterns[1]
          0] MatchAs - 1,10..1,11
            .name 'd'
        1] MatchValue - 1,15..1,16
          .value Constant 2 - 1,15..1,16
      .body[1]
      0] Pass - 1,19..1,23
"""),

(r"""match a:
 case 1 as b, (2): pass""", 'body[0].cases[0].pattern', -4, None, {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""match a:
 case {1: a, 2: (b), **rest}: pass""", 'body[0].cases[0].pattern', 0, 'patterns', {}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""match a:
 case {1: a, 2: (b), **rest}: pass""", 'body[0].cases[0].pattern', 0, 'patterns', {}, r"""new""", r"""match a:
 case {1: new, 2: (b), **rest}: pass""", r"""
Module - ROOT 0,0..1,36
  .body[1]
  0] Match - 0,0..1,36
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,36
      .pattern MatchMapping - 1,6..1,30
        .keys[2]
        0] Constant 1 - 1,7..1,8
        1] Constant 2 - 1,15..1,16
        .patterns[2]
        0] MatchAs - 1,10..1,13
          .name 'new'
        1] MatchAs - 1,19..1,20
          .name 'b'
        .rest 'rest'
      .body[1]
      0] Pass - 1,32..1,36
"""),

(r"""match a:
 case {1: a, 2: (b), **rest}: pass""", 'body[0].cases[0].pattern', 1, 'patterns', {}, r"""new""", r"""match a:
 case {1: a, 2: new, **rest}: pass""", r"""
Module - ROOT 0,0..1,34
  .body[1]
  0] Match - 0,0..1,34
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,34
      .pattern MatchMapping - 1,6..1,28
        .keys[2]
        0] Constant 1 - 1,7..1,8
        1] Constant 2 - 1,13..1,14
        .patterns[2]
        0] MatchAs - 1,10..1,11
          .name 'a'
        1] MatchAs - 1,16..1,19
          .name 'new'
        .rest 'rest'
      .body[1]
      0] Pass - 1,30..1,34
"""),

(r"""match a:
 case {1: a, 2: (b), **rest}: pass""", 'body[0].cases[0].pattern', -1, 'patterns', {}, r"""{1: c, **d}""", r"""match a:
 case {1: a, 2: {1: c, **d}, **rest}: pass""", r"""
Module - ROOT 0,0..1,42
  .body[1]
  0] Match - 0,0..1,42
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,42
      .pattern MatchMapping - 1,6..1,36
        .keys[2]
        0] Constant 1 - 1,7..1,8
        1] Constant 2 - 1,13..1,14
        .patterns[2]
        0] MatchAs - 1,10..1,11
          .name 'a'
        1] MatchMapping - 1,16..1,27
          .keys[1]
          0] Constant 1 - 1,17..1,18
          .patterns[1]
          0] MatchAs - 1,20..1,21
            .name 'c'
          .rest 'd'
        .rest 'rest'
      .body[1]
      0] Pass - 1,38..1,42
"""),

(r"""match a:
 case {1: a, 2: (b), **rest}: pass""", 'body[0].cases[0].pattern', -2, 'patterns', {}, r"""f(c=d)""", r"""match a:
 case {1: f(c=d), 2: (b), **rest}: pass""", r"""
Module - ROOT 0,0..1,39
  .body[1]
  0] Match - 0,0..1,39
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,39
      .pattern MatchMapping - 1,6..1,33
        .keys[2]
        0] Constant 1 - 1,7..1,8
        1] Constant 2 - 1,18..1,19
        .patterns[2]
        0] MatchClass - 1,10..1,16
          .cls Name 'f' Load - 1,10..1,11
          .kwd_attrs[1]
          0] 'c'
          .kwd_patterns[1]
          0] MatchAs - 1,14..1,15
            .name 'd'
        1] MatchAs - 1,22..1,23
          .name 'b'
        .rest 'rest'
      .body[1]
      0] Pass - 1,35..1,39
"""),

(r"""match a:
 case {1: a, 2: (b), **rest}: pass""", 'body[0].cases[0].pattern', -4, 'patterns', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""match a:
 case c(a, (b)): pass""", 'body[0].cases[0].pattern', 0, 'patterns', {}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""match a:
 case c(a, (b)): pass""", 'body[0].cases[0].pattern', 0, 'patterns', {}, r"""new""", r"""match a:
 case c(new, (b)): pass""", r"""
Module - ROOT 0,0..1,23
  .body[1]
  0] Match - 0,0..1,23
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,23
      .pattern MatchClass - 1,6..1,17
        .cls Name 'c' Load - 1,6..1,7
        .patterns[2]
        0] MatchAs - 1,8..1,11
          .name 'new'
        1] MatchAs - 1,14..1,15
          .name 'b'
      .body[1]
      0] Pass - 1,19..1,23
"""),

(r"""match a:
 case c(a, (b)): pass""", 'body[0].cases[0].pattern', 1, 'patterns', {}, r"""new""", r"""match a:
 case c(a, new): pass""", r"""
Module - ROOT 0,0..1,21
  .body[1]
  0] Match - 0,0..1,21
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,21
      .pattern MatchClass - 1,6..1,15
        .cls Name 'c' Load - 1,6..1,7
        .patterns[2]
        0] MatchAs - 1,8..1,9
          .name 'a'
        1] MatchAs - 1,11..1,14
          .name 'new'
      .body[1]
      0] Pass - 1,17..1,21
"""),

(r"""match a:
 case c(a, (b)): pass""", 'body[0].cases[0].pattern', -1, 'patterns', {}, r"""{1: c, **d}""", r"""match a:
 case c(a, {1: c, **d}): pass""", r"""
Module - ROOT 0,0..1,29
  .body[1]
  0] Match - 0,0..1,29
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,29
      .pattern MatchClass - 1,6..1,23
        .cls Name 'c' Load - 1,6..1,7
        .patterns[2]
        0] MatchAs - 1,8..1,9
          .name 'a'
        1] MatchMapping - 1,11..1,22
          .keys[1]
          0] Constant 1 - 1,12..1,13
          .patterns[1]
          0] MatchAs - 1,15..1,16
            .name 'c'
          .rest 'd'
      .body[1]
      0] Pass - 1,25..1,29
"""),

(r"""match a:
 case c(a, (b)): pass""", 'body[0].cases[0].pattern', -2, 'patterns', {}, r"""f(c=d)""", r"""match a:
 case c(f(c=d), (b)): pass""", r"""
Module - ROOT 0,0..1,26
  .body[1]
  0] Match - 0,0..1,26
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,26
      .pattern MatchClass - 1,6..1,20
        .cls Name 'c' Load - 1,6..1,7
        .patterns[2]
        0] MatchClass - 1,8..1,14
          .cls Name 'f' Load - 1,8..1,9
          .kwd_attrs[1]
          0] 'c'
          .kwd_patterns[1]
          0] MatchAs - 1,12..1,13
            .name 'd'
        1] MatchAs - 1,17..1,18
          .name 'b'
      .body[1]
      0] Pass - 1,22..1,26
"""),

(r"""match a:
 case c(a, (b)): pass""", 'body[0].cases[0].pattern', -4, 'patterns', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""match a:
 case c(a={1: c}, b=(d())): pass""", 'body[0].cases[0].pattern', 0, 'kwd_patterns', {}, r"""**DEL**""", r"""**ValueError('cannot delete MatchClass.kwd_patterns[0]')**""", r"""
"""),

(r"""match a:
 case c(a={1: c}, b=(d())): pass""", 'body[0].cases[0].pattern', 0, 'kwd_patterns', {}, r"""new""", r"""match a:
 case c(a=new, b=(d())): pass""", r"""
Module - ROOT 0,0..1,29
  .body[1]
  0] Match - 0,0..1,29
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,29
      .pattern MatchClass - 1,6..1,23
        .cls Name 'c' Load - 1,6..1,7
        .kwd_attrs[2]
        0] 'a'
        1] 'b'
        .kwd_patterns[2]
        0] MatchAs - 1,10..1,13
          .name 'new'
        1] MatchClass - 1,18..1,21
          .cls Name 'd' Load - 1,18..1,19
      .body[1]
      0] Pass - 1,25..1,29
"""),

(r"""match a:
 case c(a={1: c}, b=(d())): pass""", 'body[0].cases[0].pattern', 1, 'kwd_patterns', {}, r"""new""", r"""match a:
 case c(a={1: c}, b=new): pass""", r"""
Module - ROOT 0,0..1,30
  .body[1]
  0] Match - 0,0..1,30
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,30
      .pattern MatchClass - 1,6..1,24
        .cls Name 'c' Load - 1,6..1,7
        .kwd_attrs[2]
        0] 'a'
        1] 'b'
        .kwd_patterns[2]
        0] MatchMapping - 1,10..1,16
          .keys[1]
          0] Constant 1 - 1,11..1,12
          .patterns[1]
          0] MatchAs - 1,14..1,15
            .name 'c'
        1] MatchAs - 1,20..1,23
          .name 'new'
      .body[1]
      0] Pass - 1,26..1,30
"""),

(r"""match a:
 case c(a={1: c}, b=(d())): pass""", 'body[0].cases[0].pattern', -1, 'kwd_patterns', {}, r"""{1: c, **d}""", r"""match a:
 case c(a={1: c}, b={1: c, **d}): pass""", r"""
Module - ROOT 0,0..1,38
  .body[1]
  0] Match - 0,0..1,38
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,38
      .pattern MatchClass - 1,6..1,32
        .cls Name 'c' Load - 1,6..1,7
        .kwd_attrs[2]
        0] 'a'
        1] 'b'
        .kwd_patterns[2]
        0] MatchMapping - 1,10..1,16
          .keys[1]
          0] Constant 1 - 1,11..1,12
          .patterns[1]
          0] MatchAs - 1,14..1,15
            .name 'c'
        1] MatchMapping - 1,20..1,31
          .keys[1]
          0] Constant 1 - 1,21..1,22
          .patterns[1]
          0] MatchAs - 1,24..1,25
            .name 'c'
          .rest 'd'
      .body[1]
      0] Pass - 1,34..1,38
"""),

(r"""match a:
 case c(a={1: c}, b=(d())): pass""", 'body[0].cases[0].pattern', -2, 'kwd_patterns', {}, r"""f(c=d)""", r"""match a:
 case c(a=f(c=d), b=(d())): pass""", r"""
Module - ROOT 0,0..1,32
  .body[1]
  0] Match - 0,0..1,32
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,32
      .pattern MatchClass - 1,6..1,26
        .cls Name 'c' Load - 1,6..1,7
        .kwd_attrs[2]
        0] 'a'
        1] 'b'
        .kwd_patterns[2]
        0] MatchClass - 1,10..1,16
          .cls Name 'f' Load - 1,10..1,11
          .kwd_attrs[1]
          0] 'c'
          .kwd_patterns[1]
          0] MatchAs - 1,14..1,15
            .name 'd'
        1] MatchClass - 1,21..1,24
          .cls Name 'd' Load - 1,21..1,22
      .body[1]
      0] Pass - 1,28..1,32
"""),

(r"""match a:
 case c(a={1: c}, b=(d())): pass""", 'body[0].cases[0].pattern', -4, 'kwd_patterns', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""match a:
 case {1: c} | (d()): pass""", 'body[0].cases[0].pattern', 0, None, {}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""match a:
 case {1: c} | (d()): pass""", 'body[0].cases[0].pattern', 0, None, {}, r"""new""", r"""match a:
 case new | (d()): pass""", r"""
Module - ROOT 0,0..1,23
  .body[1]
  0] Match - 0,0..1,23
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,23
      .pattern MatchOr - 1,6..1,17
        .patterns[2]
        0] MatchAs - 1,6..1,9
          .name 'new'
        1] MatchClass - 1,13..1,16
          .cls Name 'd' Load - 1,13..1,14
      .body[1]
      0] Pass - 1,19..1,23
"""),

(r"""match a:
 case {1: c} | (d()): pass""", 'body[0].cases[0].pattern', 1, None, {}, r"""new""", r"""match a:
 case {1: c} | new: pass""", r"""
Module - ROOT 0,0..1,24
  .body[1]
  0] Match - 0,0..1,24
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,24
      .pattern MatchOr - 1,6..1,18
        .patterns[2]
        0] MatchMapping - 1,6..1,12
          .keys[1]
          0] Constant 1 - 1,7..1,8
          .patterns[1]
          0] MatchAs - 1,10..1,11
            .name 'c'
        1] MatchAs - 1,15..1,18
          .name 'new'
      .body[1]
      0] Pass - 1,20..1,24
"""),

(r"""match a:
 case {1: c} | (d()): pass""", 'body[0].cases[0].pattern', -1, None, {}, r"""{1: c, **d}""", r"""match a:
 case {1: c} | {1: c, **d}: pass""", r"""
Module - ROOT 0,0..1,32
  .body[1]
  0] Match - 0,0..1,32
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,32
      .pattern MatchOr - 1,6..1,26
        .patterns[2]
        0] MatchMapping - 1,6..1,12
          .keys[1]
          0] Constant 1 - 1,7..1,8
          .patterns[1]
          0] MatchAs - 1,10..1,11
            .name 'c'
        1] MatchMapping - 1,15..1,26
          .keys[1]
          0] Constant 1 - 1,16..1,17
          .patterns[1]
          0] MatchAs - 1,19..1,20
            .name 'c'
          .rest 'd'
      .body[1]
      0] Pass - 1,28..1,32
"""),

(r"""match a:
 case {1: c} | (d()): pass""", 'body[0].cases[0].pattern', -2, None, {}, r"""f(c=d)""", r"""match a:
 case f(c=d) | (d()): pass""", r"""
Module - ROOT 0,0..1,26
  .body[1]
  0] Match - 0,0..1,26
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,26
      .pattern MatchOr - 1,6..1,20
        .patterns[2]
        0] MatchClass - 1,6..1,12
          .cls Name 'f' Load - 1,6..1,7
          .kwd_attrs[1]
          0] 'c'
          .kwd_patterns[1]
          0] MatchAs - 1,10..1,11
            .name 'd'
        1] MatchClass - 1,16..1,19
          .cls Name 'd' Load - 1,16..1,17
      .body[1]
      0] Pass - 1,22..1,26
"""),

(r"""match a:
 case {1: c} | (d()): pass""", 'body[0].cases[0].pattern', -4, None, {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""match a:
 case {1: c} | (d()): pass""", 'body[0].cases[0]', None, 'pattern', {}, r"""**DEL**""", r"""**ValueError('cannot delete match_case.pattern')**""", r"""
"""),

(r"""match a:
 case c(a={1: c}, b=(d())): pass""", 'body[0].cases[0]', None, 'pattern', {}, r"""new""", r"""match a:
 case new: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchAs - 1,6..1,9
        .name 'new'
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case c(a, (b)): pass""", 'body[0].cases[0]', None, 'pattern', {}, r"""new""", r"""match a:
 case new: pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchAs - 1,6..1,9
        .name 'new'
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case {1: a, 2: (b), **rest}: pass""", 'body[0].cases[0]', None, 'pattern', {}, r"""{1: c, **d}""", r"""match a:
 case {1: c, **d}: pass""", r"""
Module - ROOT 0,0..1,23
  .body[1]
  0] Match - 0,0..1,23
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,23
      .pattern MatchMapping - 1,6..1,17
        .keys[1]
        0] Constant 1 - 1,7..1,8
        .patterns[1]
        0] MatchAs - 1,10..1,11
          .name 'c'
        .rest 'd'
      .body[1]
      0] Pass - 1,19..1,23
"""),

(r"""match a:
 case 1 as b, (2): pass""", 'body[0].cases[0]', None, 'pattern', {}, r"""f(c=d)""", r"""match a:
 case f(c=d): pass""", r"""
Module - ROOT 0,0..1,18
  .body[1]
  0] Match - 0,0..1,18
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,18
      .pattern MatchClass - 1,6..1,12
        .cls Name 'f' Load - 1,6..1,7
        .kwd_attrs[1]
        0] 'c'
        .kwd_patterns[1]
        0] MatchAs - 1,10..1,11
          .name 'd'
      .body[1]
      0] Pass - 1,14..1,18
"""),

(r"""match a:
 case {1: c} | (d()): pass""", 'body[0].cases[0]', 0, 'pattern', {}, r"""new""", r"""**IndexError('match_case.pattern does not take an index')**""", r"""
"""),

(r"""match a:
 case 1 as b: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""c.d""", r"""match a:
 case c.d as b: pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchAs - 1,6..1,14
        .pattern MatchValue - 1,6..1,9
          .value Attribute - 1,6..1,9
            .value Name 'c' Load - 1,6..1,7
            .attr 'd'
            .ctx Load
        .name 'b'
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""match a:
 case (1) as b: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""c.d""", r"""match a:
 case c.d as b: pass""", r"""
Module - ROOT 0,0..1,20
  .body[1]
  0] Match - 0,0..1,20
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,20
      .pattern MatchAs - 1,6..1,14
        .pattern MatchValue - 1,6..1,9
          .value Attribute - 1,6..1,9
            .value Name 'c' Load - 1,6..1,7
            .attr 'd'
            .ctx Load
        .name 'b'
      .body[1]
      0] Pass - 1,16..1,20
"""),

(r"""match a:
 case ((1) as b): pass""", 'body[0].cases[0].pattern', None, None, {}, r"""c.d""", r"""match a:
 case (c.d as b): pass""", r"""
Module - ROOT 0,0..1,22
  .body[1]
  0] Match - 0,0..1,22
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,22
      .pattern MatchAs - 1,7..1,15
        .pattern MatchValue - 1,7..1,10
          .value Attribute - 1,7..1,10
            .value Name 'c' Load - 1,7..1,8
            .attr 'd'
            .ctx Load
        .name 'b'
      .body[1]
      0] Pass - 1,18..1,22
"""),

(r"""match a:
 case 1 as b: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""**DEL**""", r"""match a:
 case b: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
        .name 'b'
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case (1) as b: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""**DEL**""", r"""match a:
 case b: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
        .name 'b'
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case ((1) as b): pass""", 'body[0].cases[0].pattern', None, None, {}, r"""**DEL**""", r"""match a:
 case (b): pass""", r"""
Module - ROOT 0,0..1,15
  .body[1]
  0] Match - 0,0..1,15
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,15
      .pattern MatchAs - 1,7..1,8
        .name 'b'
      .body[1]
      0] Pass - 1,11..1,15
"""),

(r"""match a:
 case b: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""**DEL**""", r"""match a:
 case b: pass""", r"""
Module - ROOT 0,0..1,13
  .body[1]
  0] Match - 0,0..1,13
    .subject Name 'a' Load - 0,6..0,7
    .cases[1]
    0] match_case - 1,1..1,13
      .pattern MatchAs - 1,6..1,7
        .name 'b'
      .body[1]
      0] Pass - 1,9..1,13
"""),

(r"""match a:
 case _: pass""", 'body[0].cases[0].pattern', None, None, {}, r"""c.d""", r"""**ValueError('cannot create MatchAs.pattern in this state')**""", r"""
"""),

(r"""def f[T: int, U: (str)](): pass""", 'body[0]', 0, 'type_params', {'_ver': 12}, r"""**DEL**""", r"""**ValueError('cannot put slice to FunctionDef.type_params')**""", r"""
"""),

(r"""def f[T: int, U: (str)](): pass""", 'body[0]', 0, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""def f[V: list[int], U: (str)](): pass""", r"""
Module - ROOT 0,0..0,37
  .body[1]
  0] FunctionDef - 0,0..0,37
    .name 'f'
    .body[1]
    0] Pass - 0,33..0,37
    .type_params[2]
    0] TypeVar - 0,6..0,18
      .name 'V'
      .bound Subscript - 0,9..0,18
        .value Name 'list' Load - 0,9..0,13
        .slice Name 'int' Load - 0,14..0,17
        .ctx Load
    1] TypeVar - 0,20..0,28
      .name 'U'
      .bound Name 'str' Load - 0,24..0,27
"""),

(r"""def f[T: int, U: (str)](): pass""", 'body[0]', 1, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""def f[T: int, V: list[int]](): pass""", r"""
Module - ROOT 0,0..0,35
  .body[1]
  0] FunctionDef - 0,0..0,35
    .name 'f'
    .body[1]
    0] Pass - 0,31..0,35
    .type_params[2]
    0] TypeVar - 0,6..0,12
      .name 'T'
      .bound Name 'int' Load - 0,9..0,12
    1] TypeVar - 0,14..0,26
      .name 'V'
      .bound Subscript - 0,17..0,26
        .value Name 'list' Load - 0,17..0,21
        .slice Name 'int' Load - 0,22..0,25
        .ctx Load
"""),

(r"""def f[T: int, U: (str)](): pass""", 'body[0]', -1, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""def f[T: int, V: list[int]](): pass""", r"""
Module - ROOT 0,0..0,35
  .body[1]
  0] FunctionDef - 0,0..0,35
    .name 'f'
    .body[1]
    0] Pass - 0,31..0,35
    .type_params[2]
    0] TypeVar - 0,6..0,12
      .name 'T'
      .bound Name 'int' Load - 0,9..0,12
    1] TypeVar - 0,14..0,26
      .name 'V'
      .bound Subscript - 0,17..0,26
        .value Name 'list' Load - 0,17..0,21
        .slice Name 'int' Load - 0,22..0,25
        .ctx Load
"""),

(r"""def f[T: int, U: (str)](): pass""", 'body[0]', -2, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""def f[V: list[int], U: (str)](): pass""", r"""
Module - ROOT 0,0..0,37
  .body[1]
  0] FunctionDef - 0,0..0,37
    .name 'f'
    .body[1]
    0] Pass - 0,33..0,37
    .type_params[2]
    0] TypeVar - 0,6..0,18
      .name 'V'
      .bound Subscript - 0,9..0,18
        .value Name 'list' Load - 0,9..0,13
        .slice Name 'int' Load - 0,14..0,17
        .ctx Load
    1] TypeVar - 0,20..0,28
      .name 'U'
      .bound Name 'str' Load - 0,24..0,27
"""),

(r"""def f[T: int, U: (str)](): pass""", 'body[0]', -4, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""async def f[T: int, U: (str)](): pass""", 'body[0]', 0, 'type_params', {'_ver': 12}, r"""**DEL**""", r"""**ValueError('cannot put slice to AsyncFunctionDef.type_params')**""", r"""
"""),

(r"""async def f[T: int, U: (str)](): pass""", 'body[0]', 0, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""async def f[V: list[int], U: (str)](): pass""", r"""
Module - ROOT 0,0..0,43
  .body[1]
  0] AsyncFunctionDef - 0,0..0,43
    .name 'f'
    .body[1]
    0] Pass - 0,39..0,43
    .type_params[2]
    0] TypeVar - 0,12..0,24
      .name 'V'
      .bound Subscript - 0,15..0,24
        .value Name 'list' Load - 0,15..0,19
        .slice Name 'int' Load - 0,20..0,23
        .ctx Load
    1] TypeVar - 0,26..0,34
      .name 'U'
      .bound Name 'str' Load - 0,30..0,33
"""),

(r"""async def f[T: int, U: (str)](): pass""", 'body[0]', 1, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""async def f[T: int, V: list[int]](): pass""", r"""
Module - ROOT 0,0..0,41
  .body[1]
  0] AsyncFunctionDef - 0,0..0,41
    .name 'f'
    .body[1]
    0] Pass - 0,37..0,41
    .type_params[2]
    0] TypeVar - 0,12..0,18
      .name 'T'
      .bound Name 'int' Load - 0,15..0,18
    1] TypeVar - 0,20..0,32
      .name 'V'
      .bound Subscript - 0,23..0,32
        .value Name 'list' Load - 0,23..0,27
        .slice Name 'int' Load - 0,28..0,31
        .ctx Load
"""),

(r"""async def f[T: int, U: (str)](): pass""", 'body[0]', -1, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""async def f[T: int, V: list[int]](): pass""", r"""
Module - ROOT 0,0..0,41
  .body[1]
  0] AsyncFunctionDef - 0,0..0,41
    .name 'f'
    .body[1]
    0] Pass - 0,37..0,41
    .type_params[2]
    0] TypeVar - 0,12..0,18
      .name 'T'
      .bound Name 'int' Load - 0,15..0,18
    1] TypeVar - 0,20..0,32
      .name 'V'
      .bound Subscript - 0,23..0,32
        .value Name 'list' Load - 0,23..0,27
        .slice Name 'int' Load - 0,28..0,31
        .ctx Load
"""),

(r"""async def f[T: int, U: (str)](): pass""", 'body[0]', -2, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""async def f[V: list[int], U: (str)](): pass""", r"""
Module - ROOT 0,0..0,43
  .body[1]
  0] AsyncFunctionDef - 0,0..0,43
    .name 'f'
    .body[1]
    0] Pass - 0,39..0,43
    .type_params[2]
    0] TypeVar - 0,12..0,24
      .name 'V'
      .bound Subscript - 0,15..0,24
        .value Name 'list' Load - 0,15..0,19
        .slice Name 'int' Load - 0,20..0,23
        .ctx Load
    1] TypeVar - 0,26..0,34
      .name 'U'
      .bound Name 'str' Load - 0,30..0,33
"""),

(r"""async def f[T: int, U: (str)](): pass""", 'body[0]', -4, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""class c[T: int, U: (str)]: pass""", 'body[0]', 0, 'type_params', {'_ver': 12}, r"""**DEL**""", r"""**ValueError('cannot put slice to ClassDef.type_params')**""", r"""
"""),

(r"""class c[T: int, U: (str)]: pass""", 'body[0]', 0, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""class c[V: list[int], U: (str)]: pass""", r"""
Module - ROOT 0,0..0,37
  .body[1]
  0] ClassDef - 0,0..0,37
    .name 'c'
    .body[1]
    0] Pass - 0,33..0,37
    .type_params[2]
    0] TypeVar - 0,8..0,20
      .name 'V'
      .bound Subscript - 0,11..0,20
        .value Name 'list' Load - 0,11..0,15
        .slice Name 'int' Load - 0,16..0,19
        .ctx Load
    1] TypeVar - 0,22..0,30
      .name 'U'
      .bound Name 'str' Load - 0,26..0,29
"""),

(r"""class c[T: int, U: (str)]: pass""", 'body[0]', 1, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""class c[T: int, V: list[int]]: pass""", r"""
Module - ROOT 0,0..0,35
  .body[1]
  0] ClassDef - 0,0..0,35
    .name 'c'
    .body[1]
    0] Pass - 0,31..0,35
    .type_params[2]
    0] TypeVar - 0,8..0,14
      .name 'T'
      .bound Name 'int' Load - 0,11..0,14
    1] TypeVar - 0,16..0,28
      .name 'V'
      .bound Subscript - 0,19..0,28
        .value Name 'list' Load - 0,19..0,23
        .slice Name 'int' Load - 0,24..0,27
        .ctx Load
"""),

(r"""class c[T: int, U: (str)]: pass""", 'body[0]', -1, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""class c[T: int, V: list[int]]: pass""", r"""
Module - ROOT 0,0..0,35
  .body[1]
  0] ClassDef - 0,0..0,35
    .name 'c'
    .body[1]
    0] Pass - 0,31..0,35
    .type_params[2]
    0] TypeVar - 0,8..0,14
      .name 'T'
      .bound Name 'int' Load - 0,11..0,14
    1] TypeVar - 0,16..0,28
      .name 'V'
      .bound Subscript - 0,19..0,28
        .value Name 'list' Load - 0,19..0,23
        .slice Name 'int' Load - 0,24..0,27
        .ctx Load
"""),

(r"""class c[T: int, U: (str)]: pass""", 'body[0]', -2, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""class c[V: list[int], U: (str)]: pass""", r"""
Module - ROOT 0,0..0,37
  .body[1]
  0] ClassDef - 0,0..0,37
    .name 'c'
    .body[1]
    0] Pass - 0,33..0,37
    .type_params[2]
    0] TypeVar - 0,8..0,20
      .name 'V'
      .bound Subscript - 0,11..0,20
        .value Name 'list' Load - 0,11..0,15
        .slice Name 'int' Load - 0,16..0,19
        .ctx Load
    1] TypeVar - 0,22..0,30
      .name 'U'
      .bound Name 'str' Load - 0,26..0,29
"""),

(r"""class c[T: int, U: (str)]: pass""", 'body[0]', -4, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""type t[T: int, U: (str)] = ...""", 'body[0]', 0, 'type_params', {'_ver': 12}, r"""**DEL**""", r"""**ValueError('cannot put slice to TypeAlias.type_params')**""", r"""
"""),

(r"""type t[T: int, U: (str)] = ...""", 'body[0]', 0, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""type t[V: list[int], U: (str)] = ...""", r"""
Module - ROOT 0,0..0,36
  .body[1]
  0] TypeAlias - 0,0..0,36
    .name Name 't' Store - 0,5..0,6
    .type_params[2]
    0] TypeVar - 0,7..0,19
      .name 'V'
      .bound Subscript - 0,10..0,19
        .value Name 'list' Load - 0,10..0,14
        .slice Name 'int' Load - 0,15..0,18
        .ctx Load
    1] TypeVar - 0,21..0,29
      .name 'U'
      .bound Name 'str' Load - 0,25..0,28
    .value Constant Ellipsis - 0,33..0,36
"""),

(r"""type t[T: int, U: (str)] = ...""", 'body[0]', 1, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""type t[T: int, V: list[int]] = ...""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] TypeAlias - 0,0..0,34
    .name Name 't' Store - 0,5..0,6
    .type_params[2]
    0] TypeVar - 0,7..0,13
      .name 'T'
      .bound Name 'int' Load - 0,10..0,13
    1] TypeVar - 0,15..0,27
      .name 'V'
      .bound Subscript - 0,18..0,27
        .value Name 'list' Load - 0,18..0,22
        .slice Name 'int' Load - 0,23..0,26
        .ctx Load
    .value Constant Ellipsis - 0,31..0,34
"""),

(r"""type t[T: int, U: (str)] = ...""", 'body[0]', -1, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""type t[T: int, V: list[int]] = ...""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] TypeAlias - 0,0..0,34
    .name Name 't' Store - 0,5..0,6
    .type_params[2]
    0] TypeVar - 0,7..0,13
      .name 'T'
      .bound Name 'int' Load - 0,10..0,13
    1] TypeVar - 0,15..0,27
      .name 'V'
      .bound Subscript - 0,18..0,27
        .value Name 'list' Load - 0,18..0,22
        .slice Name 'int' Load - 0,23..0,26
        .ctx Load
    .value Constant Ellipsis - 0,31..0,34
"""),

(r"""type t[T: int, U: (str)] = ...""", 'body[0]', -2, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""type t[V: list[int], U: (str)] = ...""", r"""
Module - ROOT 0,0..0,36
  .body[1]
  0] TypeAlias - 0,0..0,36
    .name Name 't' Store - 0,5..0,6
    .type_params[2]
    0] TypeVar - 0,7..0,19
      .name 'V'
      .bound Subscript - 0,10..0,19
        .value Name 'list' Load - 0,10..0,14
        .slice Name 'int' Load - 0,15..0,18
        .ctx Load
    1] TypeVar - 0,21..0,29
      .name 'U'
      .bound Name 'str' Load - 0,25..0,28
    .value Constant Ellipsis - 0,33..0,36
"""),

(r"""type t[T: int, U: (str)] = ...""", 'body[0]', -4, 'type_params', {'_ver': 12}, r"""V: list[int]""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""[i for j in k async for (i) in j]""", 'body[0].value', 0, 'generators', {'raw': False}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""[i for j in k async for (i) in j]""", 'body[0].value', 0, 'generators', {}, r"""async for a in b""", r"""[i async for a in b async for (i) in j]""", r"""
Module - ROOT 0,0..0,39
  .body[1]
  0] Expr - 0,0..0,39
    .value ListComp - 0,0..0,39
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,19
        .target Name 'a' Store - 0,13..0,14
        .iter Name 'b' Load - 0,18..0,19
        .is_async 1
      1] comprehension - 0,20..0,38
        .target Name 'i' Store - 0,31..0,32
        .iter Name 'j' Load - 0,37..0,38
        .is_async 1
"""),

(r"""[i for j in k async for (i) in j]""", 'body[0].value', 1, 'generators', {}, r"""async for a in b""", r"""[i for j in k async for a in b]""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] Expr - 0,0..0,31
    .value ListComp - 0,0..0,31
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,13
        .target Name 'j' Store - 0,7..0,8
        .iter Name 'k' Load - 0,12..0,13
        .is_async 0
      1] comprehension - 0,14..0,30
        .target Name 'a' Store - 0,24..0,25
        .iter Name 'b' Load - 0,29..0,30
        .is_async 1
"""),

(r"""[i for j in k async for (i) in j]""", 'body[0].value', -1, 'generators', {}, r"""async for a in b""", r"""[i for j in k async for a in b]""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] Expr - 0,0..0,31
    .value ListComp - 0,0..0,31
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,13
        .target Name 'j' Store - 0,7..0,8
        .iter Name 'k' Load - 0,12..0,13
        .is_async 0
      1] comprehension - 0,14..0,30
        .target Name 'a' Store - 0,24..0,25
        .iter Name 'b' Load - 0,29..0,30
        .is_async 1
"""),

(r"""[i for j in k async for (i) in j]""", 'body[0].value', -2, 'generators', {}, r"""async for a in b""", r"""[i async for a in b async for (i) in j]""", r"""
Module - ROOT 0,0..0,39
  .body[1]
  0] Expr - 0,0..0,39
    .value ListComp - 0,0..0,39
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,19
        .target Name 'a' Store - 0,13..0,14
        .iter Name 'b' Load - 0,18..0,19
        .is_async 1
      1] comprehension - 0,20..0,38
        .target Name 'i' Store - 0,31..0,32
        .iter Name 'j' Load - 0,37..0,38
        .is_async 1
"""),

(r"""[i for j in k async for (i) in j]""", 'body[0].value', -4, 'generators', {}, r"""async for a in b""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""{i for j in k async for (i) in j}""", 'body[0].value', 0, 'generators', {'raw': False}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""{i for j in k async for (i) in j}""", 'body[0].value', 0, 'generators', {}, r"""async for a in b""", r"""{i async for a in b async for (i) in j}""", r"""
Module - ROOT 0,0..0,39
  .body[1]
  0] Expr - 0,0..0,39
    .value SetComp - 0,0..0,39
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,19
        .target Name 'a' Store - 0,13..0,14
        .iter Name 'b' Load - 0,18..0,19
        .is_async 1
      1] comprehension - 0,20..0,38
        .target Name 'i' Store - 0,31..0,32
        .iter Name 'j' Load - 0,37..0,38
        .is_async 1
"""),

(r"""{i for j in k async for (i) in j}""", 'body[0].value', 1, 'generators', {}, r"""async for a in b""", r"""{i for j in k async for a in b}""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] Expr - 0,0..0,31
    .value SetComp - 0,0..0,31
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,13
        .target Name 'j' Store - 0,7..0,8
        .iter Name 'k' Load - 0,12..0,13
        .is_async 0
      1] comprehension - 0,14..0,30
        .target Name 'a' Store - 0,24..0,25
        .iter Name 'b' Load - 0,29..0,30
        .is_async 1
"""),

(r"""{i for j in k async for (i) in j}""", 'body[0].value', -1, 'generators', {}, r"""async for a in b""", r"""{i for j in k async for a in b}""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] Expr - 0,0..0,31
    .value SetComp - 0,0..0,31
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,13
        .target Name 'j' Store - 0,7..0,8
        .iter Name 'k' Load - 0,12..0,13
        .is_async 0
      1] comprehension - 0,14..0,30
        .target Name 'a' Store - 0,24..0,25
        .iter Name 'b' Load - 0,29..0,30
        .is_async 1
"""),

(r"""{i for j in k async for (i) in j}""", 'body[0].value', -2, 'generators', {}, r"""async for a in b""", r"""{i async for a in b async for (i) in j}""", r"""
Module - ROOT 0,0..0,39
  .body[1]
  0] Expr - 0,0..0,39
    .value SetComp - 0,0..0,39
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,19
        .target Name 'a' Store - 0,13..0,14
        .iter Name 'b' Load - 0,18..0,19
        .is_async 1
      1] comprehension - 0,20..0,38
        .target Name 'i' Store - 0,31..0,32
        .iter Name 'j' Load - 0,37..0,38
        .is_async 1
"""),

(r"""{i for j in k async for (i) in j}""", 'body[0].value', -4, 'generators', {}, r"""async for a in b""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""{i: i for j in k async for (i) in j}""", 'body[0].value', 0, 'generators', {'raw': False}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""{i: i for j in k async for (i) in j}""", 'body[0].value', 0, 'generators', {}, r"""async for a in b""", r"""{i: i async for a in b async for (i) in j}""", r"""
Module - ROOT 0,0..0,42
  .body[1]
  0] Expr - 0,0..0,42
    .value DictComp - 0,0..0,42
      .key Name 'i' Load - 0,1..0,2
      .value Name 'i' Load - 0,4..0,5
      .generators[2]
      0] comprehension - 0,6..0,22
        .target Name 'a' Store - 0,16..0,17
        .iter Name 'b' Load - 0,21..0,22
        .is_async 1
      1] comprehension - 0,23..0,41
        .target Name 'i' Store - 0,34..0,35
        .iter Name 'j' Load - 0,40..0,41
        .is_async 1
"""),

(r"""{i: i for j in k async for (i) in j}""", 'body[0].value', 1, 'generators', {}, r"""async for a in b""", r"""{i: i for j in k async for a in b}""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] Expr - 0,0..0,34
    .value DictComp - 0,0..0,34
      .key Name 'i' Load - 0,1..0,2
      .value Name 'i' Load - 0,4..0,5
      .generators[2]
      0] comprehension - 0,6..0,16
        .target Name 'j' Store - 0,10..0,11
        .iter Name 'k' Load - 0,15..0,16
        .is_async 0
      1] comprehension - 0,17..0,33
        .target Name 'a' Store - 0,27..0,28
        .iter Name 'b' Load - 0,32..0,33
        .is_async 1
"""),

(r"""{i: i for j in k async for (i) in j}""", 'body[0].value', -1, 'generators', {}, r"""async for a in b""", r"""{i: i for j in k async for a in b}""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] Expr - 0,0..0,34
    .value DictComp - 0,0..0,34
      .key Name 'i' Load - 0,1..0,2
      .value Name 'i' Load - 0,4..0,5
      .generators[2]
      0] comprehension - 0,6..0,16
        .target Name 'j' Store - 0,10..0,11
        .iter Name 'k' Load - 0,15..0,16
        .is_async 0
      1] comprehension - 0,17..0,33
        .target Name 'a' Store - 0,27..0,28
        .iter Name 'b' Load - 0,32..0,33
        .is_async 1
"""),

(r"""{i: i for j in k async for (i) in j}""", 'body[0].value', -2, 'generators', {}, r"""async for a in b""", r"""{i: i async for a in b async for (i) in j}""", r"""
Module - ROOT 0,0..0,42
  .body[1]
  0] Expr - 0,0..0,42
    .value DictComp - 0,0..0,42
      .key Name 'i' Load - 0,1..0,2
      .value Name 'i' Load - 0,4..0,5
      .generators[2]
      0] comprehension - 0,6..0,22
        .target Name 'a' Store - 0,16..0,17
        .iter Name 'b' Load - 0,21..0,22
        .is_async 1
      1] comprehension - 0,23..0,41
        .target Name 'i' Store - 0,34..0,35
        .iter Name 'j' Load - 0,40..0,41
        .is_async 1
"""),

(r"""{i: i for j in k async for (i) in j}""", 'body[0].value', -4, 'generators', {}, r"""async for a in b""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""(i for j in k async for (i) in j)""", 'body[0].value', 0, 'generators', {'raw': False}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""(i for j in k async for (i) in j)""", 'body[0].value', 0, 'generators', {}, r"""async for a in b""", r"""(i async for a in b async for (i) in j)""", r"""
Module - ROOT 0,0..0,39
  .body[1]
  0] Expr - 0,0..0,39
    .value GeneratorExp - 0,0..0,39
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,19
        .target Name 'a' Store - 0,13..0,14
        .iter Name 'b' Load - 0,18..0,19
        .is_async 1
      1] comprehension - 0,20..0,38
        .target Name 'i' Store - 0,31..0,32
        .iter Name 'j' Load - 0,37..0,38
        .is_async 1
"""),

(r"""(i for j in k async for (i) in j)""", 'body[0].value', 1, 'generators', {}, r"""async for a in b""", r"""(i for j in k async for a in b)""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] Expr - 0,0..0,31
    .value GeneratorExp - 0,0..0,31
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,13
        .target Name 'j' Store - 0,7..0,8
        .iter Name 'k' Load - 0,12..0,13
        .is_async 0
      1] comprehension - 0,14..0,30
        .target Name 'a' Store - 0,24..0,25
        .iter Name 'b' Load - 0,29..0,30
        .is_async 1
"""),

(r"""(i for j in k async for (i) in j)""", 'body[0].value', -1, 'generators', {}, r"""async for a in b""", r"""(i for j in k async for a in b)""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] Expr - 0,0..0,31
    .value GeneratorExp - 0,0..0,31
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,13
        .target Name 'j' Store - 0,7..0,8
        .iter Name 'k' Load - 0,12..0,13
        .is_async 0
      1] comprehension - 0,14..0,30
        .target Name 'a' Store - 0,24..0,25
        .iter Name 'b' Load - 0,29..0,30
        .is_async 1
"""),

(r"""(i for j in k async for (i) in j)""", 'body[0].value', -2, 'generators', {}, r"""async for a in b""", r"""(i async for a in b async for (i) in j)""", r"""
Module - ROOT 0,0..0,39
  .body[1]
  0] Expr - 0,0..0,39
    .value GeneratorExp - 0,0..0,39
      .elt Name 'i' Load - 0,1..0,2
      .generators[2]
      0] comprehension - 0,3..0,19
        .target Name 'a' Store - 0,13..0,14
        .iter Name 'b' Load - 0,18..0,19
        .is_async 1
      1] comprehension - 0,20..0,38
        .target Name 'i' Store - 0,31..0,32
        .iter Name 'j' Load - 0,37..0,38
        .is_async 1
"""),

(r"""(i for j in k async for (i) in j)""", 'body[0].value', -4, 'generators', {}, r"""async for a in b""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""def f(a: int = 1, b: (str)='', /): pass""", 'body[0].args', 0, 'posonlyargs', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to arguments.posonlyargs')**""", r"""
"""),

(r"""def f(a: int = 1, b: (str)='', /): pass""", 'body[0].args', 0, 'posonlyargs', {}, r"""new""", r"""def f(new = 1, b: (str)='', /): pass""", r"""
Module - ROOT 0,0..0,36
  .body[1]
  0] FunctionDef - 0,0..0,36
    .name 'f'
    .args arguments - 0,6..0,29
      .posonlyargs[2]
      0] arg - 0,6..0,9
        .arg 'new'
      1] arg - 0,15..0,23
        .arg 'b'
        .annotation Name 'str' Load - 0,19..0,22
      .defaults[2]
      0] Constant 1 - 0,12..0,13
      1] Constant '' - 0,24..0,26
    .body[1]
    0] Pass - 0,32..0,36
"""),

(r"""def f(a: int = 1, b: (str)='', /): pass""", 'body[0].args', 1, 'posonlyargs', {}, r"""new""", r"""def f(a: int = 1, new='', /): pass""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] FunctionDef - 0,0..0,34
    .name 'f'
    .args arguments - 0,6..0,27
      .posonlyargs[2]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'int' Load - 0,9..0,12
      1] arg - 0,18..0,21
        .arg 'new'
      .defaults[2]
      0] Constant 1 - 0,15..0,16
      1] Constant '' - 0,22..0,24
    .body[1]
    0] Pass - 0,30..0,34
"""),

(r"""def f(a: int = 1, b: (str)='', /): pass""", 'body[0].args', -1, 'posonlyargs', {}, r"""new""", r"""def f(a: int = 1, new='', /): pass""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] FunctionDef - 0,0..0,34
    .name 'f'
    .args arguments - 0,6..0,27
      .posonlyargs[2]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'int' Load - 0,9..0,12
      1] arg - 0,18..0,21
        .arg 'new'
      .defaults[2]
      0] Constant 1 - 0,15..0,16
      1] Constant '' - 0,22..0,24
    .body[1]
    0] Pass - 0,30..0,34
"""),

(r"""def f(a: int = 1, b: (str)='', /): pass""", 'body[0].args', -2, 'posonlyargs', {}, r"""new""", r"""def f(new = 1, b: (str)='', /): pass""", r"""
Module - ROOT 0,0..0,36
  .body[1]
  0] FunctionDef - 0,0..0,36
    .name 'f'
    .args arguments - 0,6..0,29
      .posonlyargs[2]
      0] arg - 0,6..0,9
        .arg 'new'
      1] arg - 0,15..0,23
        .arg 'b'
        .annotation Name 'str' Load - 0,19..0,22
      .defaults[2]
      0] Constant 1 - 0,12..0,13
      1] Constant '' - 0,24..0,26
    .body[1]
    0] Pass - 0,32..0,36
"""),

(r"""def f(a: int = 1, b: (str)='', /): pass""", 'body[0].args', -4, 'posonlyargs', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""def f(a: int = 1, b: (str)=''): pass""", 'body[0].args', 0, 'args', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to arguments.args')**""", r"""
"""),

(r"""def f(a: int = 1, b: (str)=''): pass""", 'body[0].args', 0, 'args', {}, r"""new""", r"""def f(new = 1, b: (str)=''): pass""", r"""
Module - ROOT 0,0..0,33
  .body[1]
  0] FunctionDef - 0,0..0,33
    .name 'f'
    .args arguments - 0,6..0,26
      .args[2]
      0] arg - 0,6..0,9
        .arg 'new'
      1] arg - 0,15..0,23
        .arg 'b'
        .annotation Name 'str' Load - 0,19..0,22
      .defaults[2]
      0] Constant 1 - 0,12..0,13
      1] Constant '' - 0,24..0,26
    .body[1]
    0] Pass - 0,29..0,33
"""),

(r"""def f(a: int = 1, b: (str)=''): pass""", 'body[0].args', 1, 'args', {}, r"""new""", r"""def f(a: int = 1, new=''): pass""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] FunctionDef - 0,0..0,31
    .name 'f'
    .args arguments - 0,6..0,24
      .args[2]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'int' Load - 0,9..0,12
      1] arg - 0,18..0,21
        .arg 'new'
      .defaults[2]
      0] Constant 1 - 0,15..0,16
      1] Constant '' - 0,22..0,24
    .body[1]
    0] Pass - 0,27..0,31
"""),

(r"""def f(a: int = 1, b: (str)=''): pass""", 'body[0].args', -1, 'args', {}, r"""new""", r"""def f(a: int = 1, new=''): pass""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] FunctionDef - 0,0..0,31
    .name 'f'
    .args arguments - 0,6..0,24
      .args[2]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'int' Load - 0,9..0,12
      1] arg - 0,18..0,21
        .arg 'new'
      .defaults[2]
      0] Constant 1 - 0,15..0,16
      1] Constant '' - 0,22..0,24
    .body[1]
    0] Pass - 0,27..0,31
"""),

(r"""def f(a: int = 1, b: (str)=''): pass""", 'body[0].args', -2, 'args', {}, r"""new""", r"""def f(new = 1, b: (str)=''): pass""", r"""
Module - ROOT 0,0..0,33
  .body[1]
  0] FunctionDef - 0,0..0,33
    .name 'f'
    .args arguments - 0,6..0,26
      .args[2]
      0] arg - 0,6..0,9
        .arg 'new'
      1] arg - 0,15..0,23
        .arg 'b'
        .annotation Name 'str' Load - 0,19..0,22
      .defaults[2]
      0] Constant 1 - 0,12..0,13
      1] Constant '' - 0,24..0,26
    .body[1]
    0] Pass - 0,29..0,33
"""),

(r"""def f(a: int = 1, b: (str)=''): pass""", 'body[0].args', -4, 'args', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""def f(*, a: int = 1, b: (str)=''): pass""", 'body[0].args', 0, 'kwonlyargs', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to arguments.kwonlyargs')**""", r"""
"""),

(r"""def f(*, a: int = 1, b: (str)=''): pass""", 'body[0].args', 0, 'kwonlyargs', {}, r"""new""", r"""def f(*, new = 1, b: (str)=''): pass""", r"""
Module - ROOT 0,0..0,36
  .body[1]
  0] FunctionDef - 0,0..0,36
    .name 'f'
    .args arguments - 0,6..0,29
      .kwonlyargs[2]
      0] arg - 0,9..0,12
        .arg 'new'
      1] arg - 0,18..0,26
        .arg 'b'
        .annotation Name 'str' Load - 0,22..0,25
      .kw_defaults[2]
      0] Constant 1 - 0,15..0,16
      1] Constant '' - 0,27..0,29
    .body[1]
    0] Pass - 0,32..0,36
"""),

(r"""def f(*, a: int = 1, b: (str)=''): pass""", 'body[0].args', 1, 'kwonlyargs', {}, r"""new""", r"""def f(*, a: int = 1, new=''): pass""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] FunctionDef - 0,0..0,34
    .name 'f'
    .args arguments - 0,6..0,27
      .kwonlyargs[2]
      0] arg - 0,9..0,15
        .arg 'a'
        .annotation Name 'int' Load - 0,12..0,15
      1] arg - 0,21..0,24
        .arg 'new'
      .kw_defaults[2]
      0] Constant 1 - 0,18..0,19
      1] Constant '' - 0,25..0,27
    .body[1]
    0] Pass - 0,30..0,34
"""),

(r"""def f(*, a: int = 1, b: (str)=''): pass""", 'body[0].args', -1, 'kwonlyargs', {}, r"""new""", r"""def f(*, a: int = 1, new=''): pass""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] FunctionDef - 0,0..0,34
    .name 'f'
    .args arguments - 0,6..0,27
      .kwonlyargs[2]
      0] arg - 0,9..0,15
        .arg 'a'
        .annotation Name 'int' Load - 0,12..0,15
      1] arg - 0,21..0,24
        .arg 'new'
      .kw_defaults[2]
      0] Constant 1 - 0,18..0,19
      1] Constant '' - 0,25..0,27
    .body[1]
    0] Pass - 0,30..0,34
"""),

(r"""def f(*, a: int = 1, b: (str)=''): pass""", 'body[0].args', -2, 'kwonlyargs', {}, r"""new""", r"""def f(*, new = 1, b: (str)=''): pass""", r"""
Module - ROOT 0,0..0,36
  .body[1]
  0] FunctionDef - 0,0..0,36
    .name 'f'
    .args arguments - 0,6..0,29
      .kwonlyargs[2]
      0] arg - 0,9..0,12
        .arg 'new'
      1] arg - 0,18..0,26
        .arg 'b'
        .annotation Name 'str' Load - 0,22..0,25
      .kw_defaults[2]
      0] Constant 1 - 0,15..0,16
      1] Constant '' - 0,27..0,29
    .body[1]
    0] Pass - 0,32..0,36
"""),

(r"""def f(*, a: int = 1, b: (str)=''): pass""", 'body[0].args', -4, 'kwonlyargs', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""class c(a=1, b = (2)): pass""", 'body[0]', 0, 'keywords', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to ClassDef.keywords')**""", r"""
"""),

(r"""class c(a=1, b = (2)): pass""", 'body[0]', 0, 'keywords', {}, r"""new=(3)""", r"""class c(new=(3), b = (2)): pass""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] ClassDef - 0,0..0,31
    .name 'c'
    .keywords[2]
    0] keyword - 0,8..0,15
      .arg 'new'
      .value Constant 3 - 0,13..0,14
    1] keyword - 0,17..0,24
      .arg 'b'
      .value Constant 2 - 0,22..0,23
    .body[1]
    0] Pass - 0,27..0,31
"""),

(r"""class c(a=1, b = (2)): pass""", 'body[0]', 1, 'keywords', {}, r"""new=(3)""", r"""class c(a=1, new=(3)): pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] ClassDef - 0,0..0,27
    .name 'c'
    .keywords[2]
    0] keyword - 0,8..0,11
      .arg 'a'
      .value Constant 1 - 0,10..0,11
    1] keyword - 0,13..0,20
      .arg 'new'
      .value Constant 3 - 0,18..0,19
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""class c(a=1, b = (2)): pass""", 'body[0]', -1, 'keywords', {}, r"""new=(3)""", r"""class c(a=1, new=(3)): pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] ClassDef - 0,0..0,27
    .name 'c'
    .keywords[2]
    0] keyword - 0,8..0,11
      .arg 'a'
      .value Constant 1 - 0,10..0,11
    1] keyword - 0,13..0,20
      .arg 'new'
      .value Constant 3 - 0,18..0,19
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""class c(a=1, b = (2)): pass""", 'body[0]', -2, 'keywords', {}, r"""new=(3)""", r"""class c(new=(3), b = (2)): pass""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] ClassDef - 0,0..0,31
    .name 'c'
    .keywords[2]
    0] keyword - 0,8..0,15
      .arg 'new'
      .value Constant 3 - 0,13..0,14
    1] keyword - 0,17..0,24
      .arg 'b'
      .value Constant 2 - 0,22..0,23
    .body[1]
    0] Pass - 0,27..0,31
"""),

(r"""class c(a=1, b = (2)): pass""", 'body[0]', -4, 'keywords', {}, r"""new=(3)""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""call(a=1, b = (2))""", 'body[0].value', 0, 'keywords', {}, r"""**DEL**""", r"""**NodeError('not implemented yet')**""", r"""
"""),

(r"""call(a=1, b = (2))""", 'body[0].value', 0, 'keywords', {}, r"""new=(3)""", r"""call(new=(3), b = (2))""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value Call - 0,0..0,22
      .func Name 'call' Load - 0,0..0,4
      .keywords[2]
      0] keyword - 0,5..0,12
        .arg 'new'
        .value Constant 3 - 0,10..0,11
      1] keyword - 0,14..0,21
        .arg 'b'
        .value Constant 2 - 0,19..0,20
"""),

(r"""call(a=1, b = (2))""", 'body[0].value', 1, 'keywords', {}, r"""new=(3)""", r"""call(a=1, new=(3))""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Expr - 0,0..0,18
    .value Call - 0,0..0,18
      .func Name 'call' Load - 0,0..0,4
      .keywords[2]
      0] keyword - 0,5..0,8
        .arg 'a'
        .value Constant 1 - 0,7..0,8
      1] keyword - 0,10..0,17
        .arg 'new'
        .value Constant 3 - 0,15..0,16
"""),

(r"""call(a=1, b = (2))""", 'body[0].value', -1, 'keywords', {}, r"""new=(3)""", r"""call(a=1, new=(3))""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Expr - 0,0..0,18
    .value Call - 0,0..0,18
      .func Name 'call' Load - 0,0..0,4
      .keywords[2]
      0] keyword - 0,5..0,8
        .arg 'a'
        .value Constant 1 - 0,7..0,8
      1] keyword - 0,10..0,17
        .arg 'new'
        .value Constant 3 - 0,15..0,16
"""),

(r"""call(a=1, b = (2))""", 'body[0].value', -2, 'keywords', {}, r"""new=(3)""", r"""call(new=(3), b = (2))""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value Call - 0,0..0,22
      .func Name 'call' Load - 0,0..0,4
      .keywords[2]
      0] keyword - 0,5..0,12
        .arg 'new'
        .value Constant 3 - 0,10..0,11
      1] keyword - 0,14..0,21
        .arg 'b'
        .value Constant 2 - 0,19..0,20
"""),

(r"""call(a=1, b = (2))""", 'body[0].value', -4, 'keywords', {}, r"""new=(3)""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""with (a as b, (f()) as d): pass""", 'body[0]', 0, 'items', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to With.items')**""", r"""
"""),

(r"""with (a as b, (f()) as d): pass""", 'body[0]', 0, 'items', {}, r"""g() as new""", r"""with (g() as new, (f()) as d): pass""", r"""
Module - ROOT 0,0..0,35
  .body[1]
  0] With - 0,0..0,35
    .items[2]
    0] withitem - 0,6..0,16
      .context_expr Call - 0,6..0,9
        .func Name 'g' Load - 0,6..0,7
      .optional_vars Name 'new' Store - 0,13..0,16
    1] withitem - 0,18..0,28
      .context_expr Call - 0,19..0,22
        .func Name 'f' Load - 0,19..0,20
      .optional_vars Name 'd' Store - 0,27..0,28
    .body[1]
    0] Pass - 0,31..0,35
"""),

(r"""with (a as b, (f()) as d): pass""", 'body[0]', 1, 'items', {}, r"""g() as new""", r"""with (a as b, g() as new): pass""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] With - 0,0..0,31
    .items[2]
    0] withitem - 0,6..0,12
      .context_expr Name 'a' Load - 0,6..0,7
      .optional_vars Name 'b' Store - 0,11..0,12
    1] withitem - 0,14..0,24
      .context_expr Call - 0,14..0,17
        .func Name 'g' Load - 0,14..0,15
      .optional_vars Name 'new' Store - 0,21..0,24
    .body[1]
    0] Pass - 0,27..0,31
"""),

(r"""with (a as b, (f()) as d): pass""", 'body[0]', -1, 'items', {}, r"""g() as new""", r"""with (a as b, g() as new): pass""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] With - 0,0..0,31
    .items[2]
    0] withitem - 0,6..0,12
      .context_expr Name 'a' Load - 0,6..0,7
      .optional_vars Name 'b' Store - 0,11..0,12
    1] withitem - 0,14..0,24
      .context_expr Call - 0,14..0,17
        .func Name 'g' Load - 0,14..0,15
      .optional_vars Name 'new' Store - 0,21..0,24
    .body[1]
    0] Pass - 0,27..0,31
"""),

(r"""with (a as b, (f()) as d): pass""", 'body[0]', -2, 'items', {}, r"""g() as new""", r"""with (g() as new, (f()) as d): pass""", r"""
Module - ROOT 0,0..0,35
  .body[1]
  0] With - 0,0..0,35
    .items[2]
    0] withitem - 0,6..0,16
      .context_expr Call - 0,6..0,9
        .func Name 'g' Load - 0,6..0,7
      .optional_vars Name 'new' Store - 0,13..0,16
    1] withitem - 0,18..0,28
      .context_expr Call - 0,19..0,22
        .func Name 'f' Load - 0,19..0,20
      .optional_vars Name 'd' Store - 0,27..0,28
    .body[1]
    0] Pass - 0,31..0,35
"""),

(r"""with (a as b, (f()) as d): pass""", 'body[0]', -4, 'items', {}, r"""g() as new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""async with (a as b, (f()) as d): pass""", 'body[0]', 0, 'items', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to AsyncWith.items')**""", r"""
"""),

(r"""async with (a as b, (f()) as d): pass""", 'body[0]', 0, 'items', {}, r"""g() as new""", r"""async with (g() as new, (f()) as d): pass""", r"""
Module - ROOT 0,0..0,41
  .body[1]
  0] AsyncWith - 0,0..0,41
    .items[2]
    0] withitem - 0,12..0,22
      .context_expr Call - 0,12..0,15
        .func Name 'g' Load - 0,12..0,13
      .optional_vars Name 'new' Store - 0,19..0,22
    1] withitem - 0,24..0,34
      .context_expr Call - 0,25..0,28
        .func Name 'f' Load - 0,25..0,26
      .optional_vars Name 'd' Store - 0,33..0,34
    .body[1]
    0] Pass - 0,37..0,41
"""),

(r"""async with (a as b, (f()) as d): pass""", 'body[0]', 1, 'items', {}, r"""g() as new""", r"""async with (a as b, g() as new): pass""", r"""
Module - ROOT 0,0..0,37
  .body[1]
  0] AsyncWith - 0,0..0,37
    .items[2]
    0] withitem - 0,12..0,18
      .context_expr Name 'a' Load - 0,12..0,13
      .optional_vars Name 'b' Store - 0,17..0,18
    1] withitem - 0,20..0,30
      .context_expr Call - 0,20..0,23
        .func Name 'g' Load - 0,20..0,21
      .optional_vars Name 'new' Store - 0,27..0,30
    .body[1]
    0] Pass - 0,33..0,37
"""),

(r"""async with (a as b, (f()) as d): pass""", 'body[0]', -1, 'items', {}, r"""g() as new""", r"""async with (a as b, g() as new): pass""", r"""
Module - ROOT 0,0..0,37
  .body[1]
  0] AsyncWith - 0,0..0,37
    .items[2]
    0] withitem - 0,12..0,18
      .context_expr Name 'a' Load - 0,12..0,13
      .optional_vars Name 'b' Store - 0,17..0,18
    1] withitem - 0,20..0,30
      .context_expr Call - 0,20..0,23
        .func Name 'g' Load - 0,20..0,21
      .optional_vars Name 'new' Store - 0,27..0,30
    .body[1]
    0] Pass - 0,33..0,37
"""),

(r"""async with (a as b, (f()) as d): pass""", 'body[0]', -2, 'items', {}, r"""g() as new""", r"""async with (g() as new, (f()) as d): pass""", r"""
Module - ROOT 0,0..0,41
  .body[1]
  0] AsyncWith - 0,0..0,41
    .items[2]
    0] withitem - 0,12..0,22
      .context_expr Call - 0,12..0,15
        .func Name 'g' Load - 0,12..0,13
      .optional_vars Name 'new' Store - 0,19..0,22
    1] withitem - 0,24..0,34
      .context_expr Call - 0,25..0,28
        .func Name 'f' Load - 0,25..0,26
      .optional_vars Name 'd' Store - 0,33..0,34
    .body[1]
    0] Pass - 0,37..0,41
"""),

(r"""async with (a as b, (f()) as d): pass""", 'body[0]', -4, 'items', {}, r"""g() as new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""import a, c.d as e""", 'body[0]', 0, 'names', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to Import.names')**""", r"""
"""),

(r"""import a, c.d as e""", 'body[0]', 0, 'names', {}, r"""f as g""", r"""import f as g, c.d as e""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] Import - 0,0..0,23
    .names[2]
    0] alias - 0,7..0,13
      .name 'f'
      .asname
        'g'
    1] alias - 0,15..0,23
      .name 'c.d'
      .asname
        'e'
"""),

(r"""import a, c.d as e""", 'body[0]', 1, 'names', {}, r"""f as g""", r"""import a, f as g""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] Import - 0,0..0,16
    .names[2]
    0] alias - 0,7..0,8
      .name 'a'
    1] alias - 0,10..0,16
      .name 'f'
      .asname
        'g'
"""),

(r"""import a, c.d as e""", 'body[0]', -1, 'names', {}, r"""f as g""", r"""import a, f as g""", r"""
Module - ROOT 0,0..0,16
  .body[1]
  0] Import - 0,0..0,16
    .names[2]
    0] alias - 0,7..0,8
      .name 'a'
    1] alias - 0,10..0,16
      .name 'f'
      .asname
        'g'
"""),

(r"""import a, c.d as e""", 'body[0]', -2, 'names', {}, r"""f as g""", r"""import f as g, c.d as e""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] Import - 0,0..0,23
    .names[2]
    0] alias - 0,7..0,13
      .name 'f'
      .asname
        'g'
    1] alias - 0,15..0,23
      .name 'c.d'
      .asname
        'e'
"""),

(r"""import a, c.d as e""", 'body[0]', -4, 'names', {}, r"""f as g""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""import a, c.d as e""", 'body[0]', 0, 'names', {}, r"""x.y as z""", r"""import x.y as z, c.d as e""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] Import - 0,0..0,25
    .names[2]
    0] alias - 0,7..0,15
      .name 'x.y'
      .asname
        'z'
    1] alias - 0,17..0,25
      .name 'c.d'
      .asname
        'e'
"""),

(r"""from z import (a, c as d)""", 'body[0]', 0, 'names', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to ImportFrom.names')**""", r"""
"""),

(r"""from z import (a, c as d)""", 'body[0]', 0, 'names', {}, r"""f as g""", r"""from z import (f as g, c as d)""", r"""
Module - ROOT 0,0..0,30
  .body[1]
  0] ImportFrom - 0,0..0,30
    .module 'z'
    .names[2]
    0] alias - 0,15..0,21
      .name 'f'
      .asname
        'g'
    1] alias - 0,23..0,29
      .name 'c'
      .asname
        'd'
    .level 0
"""),

(r"""from z import (a, c as d)""", 'body[0]', 1, 'names', {}, r"""f as g""", r"""from z import (a, f as g)""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] ImportFrom - 0,0..0,25
    .module 'z'
    .names[2]
    0] alias - 0,15..0,16
      .name 'a'
    1] alias - 0,18..0,24
      .name 'f'
      .asname
        'g'
    .level 0
"""),

(r"""from z import (a, c as d)""", 'body[0]', -1, 'names', {}, r"""f as g""", r"""from z import (a, f as g)""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] ImportFrom - 0,0..0,25
    .module 'z'
    .names[2]
    0] alias - 0,15..0,16
      .name 'a'
    1] alias - 0,18..0,24
      .name 'f'
      .asname
        'g'
    .level 0
"""),

(r"""from z import (a, c as d)""", 'body[0]', -2, 'names', {}, r"""f as g""", r"""from z import (f as g, c as d)""", r"""
Module - ROOT 0,0..0,30
  .body[1]
  0] ImportFrom - 0,0..0,30
    .module 'z'
    .names[2]
    0] alias - 0,15..0,21
      .name 'f'
      .asname
        'g'
    1] alias - 0,23..0,29
      .name 'c'
      .asname
        'd'
    .level 0
"""),

(r"""from z import (a, c as d)""", 'body[0]', -4, 'names', {}, r"""f as g""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""a[b:c:d]""", 'body[0].value', None, 'slice', {}, r"""**DEL**""", r"""**ValueError('cannot delete Subscript.slice')**""", r"""
"""),

(r"""a[b:c:d]""", 'body[0].value', None, 'slice', {}, r"""e, f""", r"""a[e, f]""", r"""
Module - ROOT 0,0..0,7
  .body[1]
  0] Expr - 0,0..0,7
    .value Subscript - 0,0..0,7
      .value Name 'a' Load - 0,0..0,1
      .slice Tuple - 0,2..0,6
        .elts[2]
        0] Name 'e' Load - 0,2..0,3
        1] Name 'f' Load - 0,5..0,6
        .ctx Load
      .ctx Load
"""),

(r"""a[b,c,d]""", 'body[0].value', None, 'slice', {}, r"""g""", r"""a[g]""", r"""
Module - ROOT 0,0..0,4
  .body[1]
  0] Expr - 0,0..0,4
    .value Subscript - 0,0..0,4
      .value Name 'a' Load - 0,0..0,1
      .slice Name 'g' Load - 0,2..0,3
      .ctx Load
"""),

(r"""a[b:c:d]""", 'body[0].value', 0, 'slice', {}, r"""h""", r"""**IndexError('Subscript.slice does not take an index')**""", r"""
"""),

(r"""a[b]""", 'body[0].value', None, 'slice', {}, r"""h:i:j""", r"""a[h:i:j]""", r"""
Module - ROOT 0,0..0,8
  .body[1]
  0] Expr - 0,0..0,8
    .value Subscript - 0,0..0,8
      .value Name 'a' Load - 0,0..0,1
      .slice Slice - 0,2..0,7
        .lower Name 'h' Load - 0,2..0,3
        .upper Name 'i' Load - 0,4..0,5
        .step Name 'j' Load - 0,6..0,7
      .ctx Load
"""),

(r"""global a, b""", 'body[0]', 0, 'names', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to Global.names')**""", r"""
"""),

(r"""global a, b""", 'body[0]', 0, 'names', {}, r"""new""", r"""global new, b""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Global - 0,0..0,13
    .names[2]
    0] 'new'
    1] 'b'
"""),

(r"""global a, b""", 'body[0]', 1, 'names', {}, r"""new""", r"""global a, new""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Global - 0,0..0,13
    .names[2]
    0] 'a'
    1] 'new'
"""),

(r"""global a, b""", 'body[0]', -1, 'names', {}, r"""new""", r"""global a, new""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Global - 0,0..0,13
    .names[2]
    0] 'a'
    1] 'new'
"""),

(r"""global \
a \
,\
b""", 'body[0]', -2, 'names', {}, r"""new""", r"""global \
new \
,\
b""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Global - 0,0..3,1
    .names[2]
    0] 'new'
    1] 'b'
"""),

(r"""global a, b""", 'body[0]', -4, 'names', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""nonlocal a, b""", 'body[0]', 0, 'names', {}, r"""**DEL**""", r"""**ValueError('cannot put slice to Nonlocal.names')**""", r"""
"""),

(r"""nonlocal a, b""", 'body[0]', 0, 'names', {}, r"""new""", r"""nonlocal new, b""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Nonlocal - 0,0..0,15
    .names[2]
    0] 'new'
    1] 'b'
"""),

(r"""nonlocal a, b""", 'body[0]', 1, 'names', {}, r"""new""", r"""nonlocal a, new""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Nonlocal - 0,0..0,15
    .names[2]
    0] 'a'
    1] 'new'
"""),

(r"""nonlocal a, b""", 'body[0]', -1, 'names', {}, r"""new""", r"""nonlocal a, new""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Nonlocal - 0,0..0,15
    .names[2]
    0] 'a'
    1] 'new'
"""),

(r"""nonlocal \
a \
,\
b""", 'body[0]', -2, 'names', {}, r"""new""", r"""nonlocal \
new \
,\
b""", r"""
Module - ROOT 0,0..3,1
  .body[1]
  0] Nonlocal - 0,0..3,1
    .names[2]
    0] 'new'
    1] 'b'
"""),

(r"""nonlocal a, b""", 'body[0]', -4, 'names', {}, r"""new""", r"""**IndexError('index out of range')**""", r"""
"""),

(r"""def f(a=1): pass""", 'body[0]', None, 'args', {}, r"""**DEL**""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f(a=1): pass""", 'body[0]', None, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass""", r"""
Module - ROOT 0,0..0,56
  .body[1]
  0] FunctionDef - 0,0..0,56
    .name 'f'
    .args arguments - 0,6..0,49
      .posonlyargs[1]
      0] arg - 0,6..0,18
        .arg 'a'
        .annotation Subscript - 0,9..0,18
          .value Name 'list' Load - 0,9..0,13
          .slice Name 'str' Load - 0,14..0,17
          .ctx Load
      .args[1]
      0] arg - 0,23..0,29
        .arg 'b'
        .annotation Name 'int' Load - 0,26..0,29
      .vararg arg - 0,36..0,37
        .arg 'c'
      .kwonlyargs[1]
      0] arg - 0,39..0,40
        .arg 'd'
      .kw_defaults[1]
      0] Constant 100 - 0,41..0,44
      .kwarg arg - 0,48..0,49
        .arg 'e'
      .defaults[1]
      0] Constant 1 - 0,32..0,33
    .body[1]
    0] Pass - 0,52..0,56
"""),

(r"""def f(): pass""", 'body[0]', None, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass""", r"""
Module - ROOT 0,0..0,56
  .body[1]
  0] FunctionDef - 0,0..0,56
    .name 'f'
    .args arguments - 0,6..0,49
      .posonlyargs[1]
      0] arg - 0,6..0,18
        .arg 'a'
        .annotation Subscript - 0,9..0,18
          .value Name 'list' Load - 0,9..0,13
          .slice Name 'str' Load - 0,14..0,17
          .ctx Load
      .args[1]
      0] arg - 0,23..0,29
        .arg 'b'
        .annotation Name 'int' Load - 0,26..0,29
      .vararg arg - 0,36..0,37
        .arg 'c'
      .kwonlyargs[1]
      0] arg - 0,39..0,40
        .arg 'd'
      .kw_defaults[1]
      0] Constant 100 - 0,41..0,44
      .kwarg arg - 0,48..0,49
        .arg 'e'
      .defaults[1]
      0] Constant 1 - 0,32..0,33
    .body[1]
    0] Pass - 0,52..0,56
"""),

(r"""def f(\
\
): pass""", 'body[0]', None, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass""", r"""
Module - ROOT 0,0..0,56
  .body[1]
  0] FunctionDef - 0,0..0,56
    .name 'f'
    .args arguments - 0,6..0,49
      .posonlyargs[1]
      0] arg - 0,6..0,18
        .arg 'a'
        .annotation Subscript - 0,9..0,18
          .value Name 'list' Load - 0,9..0,13
          .slice Name 'str' Load - 0,14..0,17
          .ctx Load
      .args[1]
      0] arg - 0,23..0,29
        .arg 'b'
        .annotation Name 'int' Load - 0,26..0,29
      .vararg arg - 0,36..0,37
        .arg 'c'
      .kwonlyargs[1]
      0] arg - 0,39..0,40
        .arg 'd'
      .kw_defaults[1]
      0] Constant 100 - 0,41..0,44
      .kwarg arg - 0,48..0,49
        .arg 'e'
      .defaults[1]
      0] Constant 1 - 0,32..0,33
    .body[1]
    0] Pass - 0,52..0,56
"""),

(r"""def f(a=1): pass""", 'body[0]', 0, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""**IndexError('FunctionDef.args does not take an index')**""", r"""
"""),

(r"""def f(a=1): pass""", 'body[0]', None, 'args', {}, r"""""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""async def f(a=1): pass""", 'body[0]', None, 'args', {}, r"""**DEL**""", r"""async def f(): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] AsyncFunctionDef - 0,0..0,19
    .name 'f'
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""async def f(a=1): pass""", 'body[0]', None, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""async def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass""", r"""
Module - ROOT 0,0..0,62
  .body[1]
  0] AsyncFunctionDef - 0,0..0,62
    .name 'f'
    .args arguments - 0,12..0,55
      .posonlyargs[1]
      0] arg - 0,12..0,24
        .arg 'a'
        .annotation Subscript - 0,15..0,24
          .value Name 'list' Load - 0,15..0,19
          .slice Name 'str' Load - 0,20..0,23
          .ctx Load
      .args[1]
      0] arg - 0,29..0,35
        .arg 'b'
        .annotation Name 'int' Load - 0,32..0,35
      .vararg arg - 0,42..0,43
        .arg 'c'
      .kwonlyargs[1]
      0] arg - 0,45..0,46
        .arg 'd'
      .kw_defaults[1]
      0] Constant 100 - 0,47..0,50
      .kwarg arg - 0,54..0,55
        .arg 'e'
      .defaults[1]
      0] Constant 1 - 0,38..0,39
    .body[1]
    0] Pass - 0,58..0,62
"""),

(r"""async def f(): pass""", 'body[0]', None, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""async def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass""", r"""
Module - ROOT 0,0..0,62
  .body[1]
  0] AsyncFunctionDef - 0,0..0,62
    .name 'f'
    .args arguments - 0,12..0,55
      .posonlyargs[1]
      0] arg - 0,12..0,24
        .arg 'a'
        .annotation Subscript - 0,15..0,24
          .value Name 'list' Load - 0,15..0,19
          .slice Name 'str' Load - 0,20..0,23
          .ctx Load
      .args[1]
      0] arg - 0,29..0,35
        .arg 'b'
        .annotation Name 'int' Load - 0,32..0,35
      .vararg arg - 0,42..0,43
        .arg 'c'
      .kwonlyargs[1]
      0] arg - 0,45..0,46
        .arg 'd'
      .kw_defaults[1]
      0] Constant 100 - 0,47..0,50
      .kwarg arg - 0,54..0,55
        .arg 'e'
      .defaults[1]
      0] Constant 1 - 0,38..0,39
    .body[1]
    0] Pass - 0,58..0,62
"""),

(r"""async def f(\
\
): pass""", 'body[0]', None, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""async def f(a: list[str], /, b: int = 1, *c, d=100, **e): pass""", r"""
Module - ROOT 0,0..0,62
  .body[1]
  0] AsyncFunctionDef - 0,0..0,62
    .name 'f'
    .args arguments - 0,12..0,55
      .posonlyargs[1]
      0] arg - 0,12..0,24
        .arg 'a'
        .annotation Subscript - 0,15..0,24
          .value Name 'list' Load - 0,15..0,19
          .slice Name 'str' Load - 0,20..0,23
          .ctx Load
      .args[1]
      0] arg - 0,29..0,35
        .arg 'b'
        .annotation Name 'int' Load - 0,32..0,35
      .vararg arg - 0,42..0,43
        .arg 'c'
      .kwonlyargs[1]
      0] arg - 0,45..0,46
        .arg 'd'
      .kw_defaults[1]
      0] Constant 100 - 0,47..0,50
      .kwarg arg - 0,54..0,55
        .arg 'e'
      .defaults[1]
      0] Constant 1 - 0,38..0,39
    .body[1]
    0] Pass - 0,58..0,62
"""),

(r"""async def f(a=1): pass""", 'body[0]', 0, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""**IndexError('AsyncFunctionDef.args does not take an index')**""", r"""
"""),

(r"""async def f(a=1): pass""", 'body[0]', None, 'args', {}, r"""""", r"""async def f(): pass""", r"""
Module - ROOT 0,0..0,19
  .body[1]
  0] AsyncFunctionDef - 0,0..0,19
    .name 'f'
    .body[1]
    0] Pass - 0,15..0,19
"""),

(r"""lambda a=1: None""", 'body[0].value', None, 'args', {}, r"""**DEL**""", r"""lambda: None""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Expr - 0,0..0,12
    .value Lambda - 0,0..0,12
      .body Constant None - 0,8..0,12
"""),

(r"""lambda a=1: None""", 'body[0].value', None, 'args', {}, r"""a: list[str], /, b: int = 1, *c, d=100, **e""", r"""**SyntaxError**""", r"""
"""),

(r"""lambda a=1: None""", 'body[0].value', None, 'args', {}, r"""a, /, b=1, *c, d=100, **e""", r"""lambda a, /, b=1, *c, d=100, **e: None""", r"""
Module - ROOT 0,0..0,38
  .body[1]
  0] Expr - 0,0..0,38
    .value Lambda - 0,0..0,38
      .args arguments - 0,7..0,32
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .args[1]
        0] arg - 0,13..0,14
          .arg 'b'
        .vararg arg - 0,19..0,20
          .arg 'c'
        .kwonlyargs[1]
        0] arg - 0,22..0,23
          .arg 'd'
        .kw_defaults[1]
        0] Constant 100 - 0,24..0,27
        .kwarg arg - 0,31..0,32
          .arg 'e'
        .defaults[1]
        0] Constant 1 - 0,15..0,16
      .body Constant None - 0,34..0,38
"""),

(r"""lambda: None""", 'body[0].value', None, 'args', {}, r"""a, /, b=1, *c, d=100, **e""", r"""lambda a, /, b=1, *c, d=100, **e: None""", r"""
Module - ROOT 0,0..0,38
  .body[1]
  0] Expr - 0,0..0,38
    .value Lambda - 0,0..0,38
      .args arguments - 0,7..0,32
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .args[1]
        0] arg - 0,13..0,14
          .arg 'b'
        .vararg arg - 0,19..0,20
          .arg 'c'
        .kwonlyargs[1]
        0] arg - 0,22..0,23
          .arg 'd'
        .kw_defaults[1]
        0] Constant 100 - 0,24..0,27
        .kwarg arg - 0,31..0,32
          .arg 'e'
        .defaults[1]
        0] Constant 1 - 0,15..0,16
      .body Constant None - 0,34..0,38
"""),

(r"""lambda\
\
: None""", 'body[0].value', None, 'args', {}, r"""a, /, b=1, *c, d=100, **e""", r"""lambda a, /, b=1, *c, d=100, **e: None""", r"""
Module - ROOT 0,0..0,38
  .body[1]
  0] Expr - 0,0..0,38
    .value Lambda - 0,0..0,38
      .args arguments - 0,7..0,32
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .args[1]
        0] arg - 0,13..0,14
          .arg 'b'
        .vararg arg - 0,19..0,20
          .arg 'c'
        .kwonlyargs[1]
        0] arg - 0,22..0,23
          .arg 'd'
        .kw_defaults[1]
        0] Constant 100 - 0,24..0,27
        .kwarg arg - 0,31..0,32
          .arg 'e'
        .defaults[1]
        0] Constant 1 - 0,15..0,16
      .body Constant None - 0,34..0,38
"""),

(r"""lambda a=1: None""", 'body[0].value', 0, 'args', {}, r"""a, /, b=1, *c, d=100, **e""", r"""**IndexError('Lambda.args does not take an index')**""", r"""
"""),

(r"""lambda a=1: None""", 'body[0].value', None, 'args', {}, r"""""", r"""lambda: None""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Expr - 0,0..0,12
    .value Lambda - 0,0..0,12
      .body Constant None - 0,8..0,12
"""),

(r"""a and b""", 'body[0].value', None, 'op', {'raw': False}, r"""or""", r"""a or b""", r"""
Module - ROOT 0,0..0,6
  .body[1]
  0] Expr - 0,0..0,6
    .value BoolOp - 0,0..0,6
      .op Or
      .values[2]
      0] Name 'a' Load - 0,0..0,1
      1] Name 'b' Load - 0,5..0,6
"""),

(r"""a and b""", 'body[0].value', None, 'op', {}, r"""+""", r"""**NodeError("expecting boolop, got '+'")**""", r"""
"""),

(r"""a and b and c""", 'body[0].value', None, 'op', {'raw': False}, r"""or""", r"""a or b or c""", r"""
Module - ROOT 0,0..0,11
  .body[1]
  0] Expr - 0,0..0,11
    .value BoolOp - 0,0..0,11
      .op Or
      .values[3]
      0] Name 'a' Load - 0,0..0,1
      1] Name 'b' Load - 0,5..0,6
      2] Name 'c' Load - 0,10..0,11
"""),

(r"""(a) or ( b ) or (
c
)""", 'body[0].value', None, 'op', {'raw': False}, r"""and""", r"""(a) and ( b ) and (
c
)""", r"""
Module - ROOT 0,0..2,1
  .body[1]
  0] Expr - 0,0..2,1
    .value BoolOp - 0,0..2,1
      .op And
      .values[3]
      0] Name 'a' Load - 0,1..0,2
      1] Name 'b' Load - 0,10..0,11
      2] Name 'c' Load - 1,0..1,1
"""),

(r"""a\
and\
b \
  and \
 c""", 'body[0].value', None, 'op', {'raw': False}, r"""or""", r"""a\
or\
b \
  or \
 c""", r"""
Module - ROOT 0,0..4,2
  .body[1]
  0] Expr - 0,0..4,2
    .value BoolOp - 0,0..4,2
      .op Or
      .values[3]
      0] Name 'a' Load - 0,0..0,1
      1] Name 'b' Load - 2,0..2,1
      2] Name 'c' Load - 4,1..4,2
"""),

(r"""def f(): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f(*b): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f(*b): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(*new): pass""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] FunctionDef - 0,0..0,17
    .name 'f'
    .args arguments - 0,6..0,10
      .vararg arg - 0,7..0,10
        .arg 'new'
    .body[1]
    0] Pass - 0,13..0,17
"""),

(r"""def f(a=(1), *b): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(a=(1)): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] FunctionDef - 0,0..0,18
    .name 'f'
    .args arguments - 0,6..0,11
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""def f(a=(1), *b): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(a=(1), *new): pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] FunctionDef - 0,0..0,24
    .name 'f'
    .args arguments - 0,6..0,17
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .vararg arg - 0,14..0,17
        .arg 'new'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""def f(a=(1), /, *b): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(a=(1), /): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .args arguments - 0,6..0,14
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""def f(a=(1), * \
 b \
 ): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(a=(1) \
 ): pass""", r"""
Module - ROOT 0,0..1,8
  .body[1]
  0] FunctionDef - 0,0..1,8
    .name 'f'
    .args arguments - 0,6..0,11
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 1,4..1,8
"""),

(r"""def f(*b, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(*, c=(1)): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .args arguments - 0,6..0,14
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,12..0,13
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""def f(*b, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(*new, c=(1)): pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] FunctionDef - 0,0..0,24
    .name 'f'
    .args arguments - 0,6..0,17
      .vararg arg - 0,7..0,10
        .arg 'new'
      .kwonlyargs[1]
      0] arg - 0,12..0,13
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,15..0,16
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""def f(*b, ** c): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(** c): pass""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] FunctionDef - 0,0..0,17
    .name 'f'
    .args arguments - 0,6..0,10
      .kwarg arg - 0,9..0,10
        .arg 'c'
    .body[1]
    0] Pass - 0,13..0,17
"""),

(r"""def f(*\
b\
, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(*, c=(1)): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .args arguments - 0,6..0,14
      .kwonlyargs[1]
      0] arg - 0,9..0,10
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,12..0,13
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""def f(a, *b, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(a, *new, c=(1)): pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] FunctionDef - 0,0..0,27
    .name 'f'
    .args arguments - 0,6..0,20
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .vararg arg - 0,10..0,13
        .arg 'new'
      .kwonlyargs[1]
      0] arg - 0,15..0,16
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,18..0,19
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""def f(a, *b, ** c): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(a, ** c): pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] FunctionDef - 0,0..0,20
    .name 'f'
    .args arguments - 0,6..0,13
      .args[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .kwarg arg - 0,12..0,13
        .arg 'c'
    .body[1]
    0] Pass - 0,16..0,20
"""),

(r"""def f(a, /, *b, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(a, /, *new, c=(1)): pass""", r"""
Module - ROOT 0,0..0,30
  .body[1]
  0] FunctionDef - 0,0..0,30
    .name 'f'
    .args arguments - 0,6..0,23
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .vararg arg - 0,13..0,16
        .arg 'new'
      .kwonlyargs[1]
      0] arg - 0,18..0,19
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,21..0,22
    .body[1]
    0] Pass - 0,26..0,30
"""),

(r"""def f(a, /, *b, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(a, /, *, c=(1)): pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] FunctionDef - 0,0..0,27
    .name 'f'
    .args arguments - 0,6..0,20
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .kwonlyargs[1]
      0] arg - 0,15..0,16
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,18..0,19
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""def f(a, /, *b, ** c): pass""", 'body[0].args', None, 'vararg', {}, r"""**DEL**""", r"""def f(a, /, ** c): pass""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] FunctionDef - 0,0..0,23
    .name 'f'
    .args arguments - 0,6..0,16
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .kwarg arg - 0,15..0,16
        .arg 'c'
    .body[1]
    0] Pass - 0,19..0,23
"""),

(r"""lambda: None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda: None""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Expr - 0,0..0,12
    .value Lambda - 0,0..0,12
      .body Constant None - 0,8..0,12
"""),

(r"""lambda *b: None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda: None""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Expr - 0,0..0,12
    .value Lambda - 0,0..0,12
      .body Constant None - 0,8..0,12
"""),

(r"""lambda *b: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda *new: None""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Lambda - 0,0..0,17
      .args arguments - 0,7..0,11
        .vararg arg - 0,8..0,11
          .arg 'new'
      .body Constant None - 0,13..0,17
"""),

(r"""lambda a=(1), *b: None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda a=(1): None""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Expr - 0,0..0,18
    .value Lambda - 0,0..0,18
      .args arguments - 0,7..0,12
        .args[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,14..0,18
"""),

(r"""lambda a=(1), *b: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda a=(1), *new: None""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] Expr - 0,0..0,24
    .value Lambda - 0,0..0,24
      .args arguments - 0,7..0,18
        .args[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .vararg arg - 0,15..0,18
          .arg 'new'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,20..0,24
"""),

(r"""lambda a=(1), /, *b: None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda a=(1), /: None""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] Expr - 0,0..0,21
    .value Lambda - 0,0..0,21
      .args arguments - 0,7..0,15
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,17..0,21
"""),

(r"""lambda a=(1), * \
 b \
 : None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda a=(1) \
 : None""", r"""
Module - ROOT 0,0..1,7
  .body[1]
  0] Expr - 0,0..1,7
    .value Lambda - 0,0..1,7
      .args arguments - 0,7..0,12
        .args[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 1,3..1,7
"""),

(r"""lambda *b, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda *, c=(1): None""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] Expr - 0,0..0,21
    .value Lambda - 0,0..0,21
      .args arguments - 0,7..0,15
        .kwonlyargs[1]
        0] arg - 0,10..0,11
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,13..0,14
      .body Constant None - 0,17..0,21
"""),

(r"""lambda *b, ** c: None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda ** c: None""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Lambda - 0,0..0,17
      .args arguments - 0,7..0,11
        .kwarg arg - 0,10..0,11
          .arg 'c'
      .body Constant None - 0,13..0,17
"""),

(r"""lambda *b, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda *new, c=(1): None""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] Expr - 0,0..0,24
    .value Lambda - 0,0..0,24
      .args arguments - 0,7..0,18
        .vararg arg - 0,8..0,11
          .arg 'new'
        .kwonlyargs[1]
        0] arg - 0,13..0,14
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,16..0,17
      .body Constant None - 0,20..0,24
"""),

(r"""lambda *\
b\
, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda *, c=(1): None""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] Expr - 0,0..0,21
    .value Lambda - 0,0..0,21
      .args arguments - 0,7..0,15
        .kwonlyargs[1]
        0] arg - 0,10..0,11
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,13..0,14
      .body Constant None - 0,17..0,21
"""),

(r"""lambda a, *b, ** c: None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda a, ** c: None""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Expr - 0,0..0,20
    .value Lambda - 0,0..0,20
      .args arguments - 0,7..0,14
        .args[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .kwarg arg - 0,13..0,14
          .arg 'c'
      .body Constant None - 0,16..0,20
"""),

(r"""lambda a, *b, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda a, *new, c=(1): None""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] Expr - 0,0..0,27
    .value Lambda - 0,0..0,27
      .args arguments - 0,7..0,21
        .args[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .vararg arg - 0,11..0,14
          .arg 'new'
        .kwonlyargs[1]
        0] arg - 0,16..0,17
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,19..0,20
      .body Constant None - 0,23..0,27
"""),

(r"""lambda a, /, *b, ** c: None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda a, /, ** c: None""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] Expr - 0,0..0,23
    .value Lambda - 0,0..0,23
      .args arguments - 0,7..0,17
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .kwarg arg - 0,16..0,17
          .arg 'c'
      .body Constant None - 0,19..0,23
"""),

(r"""lambda a, /, *b, c=(2), ** d: None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda a, /, *, c=(2), ** d: None""", r"""
Module - ROOT 0,0..0,33
  .body[1]
  0] Expr - 0,0..0,33
    .value Lambda - 0,0..0,33
      .args arguments - 0,7..0,27
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .kwonlyargs[1]
        0] arg - 0,16..0,17
          .arg 'c'
        .kw_defaults[1]
        0] Constant 2 - 0,19..0,20
        .kwarg arg - 0,26..0,27
          .arg 'd'
      .body Constant None - 0,29..0,33
"""),

(r"""lambda a, /, *b, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda a, /, *new, c=(1): None""", r"""
Module - ROOT 0,0..0,30
  .body[1]
  0] Expr - 0,0..0,30
    .value Lambda - 0,0..0,30
      .args arguments - 0,7..0,24
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .vararg arg - 0,14..0,17
          .arg 'new'
        .kwonlyargs[1]
        0] arg - 0,19..0,20
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,22..0,23
      .body Constant None - 0,26..0,30
"""),

(r"""lambda a, /, *b, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""**DEL**""", r"""lambda a, /, *, c=(1): None""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] Expr - 0,0..0,27
    .value Lambda - 0,0..0,27
      .args arguments - 0,7..0,21
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .kwonlyargs[1]
        0] arg - 0,16..0,17
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,19..0,20
      .body Constant None - 0,23..0,27
"""),

(r"""def f(*, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(*new, c=(1)): pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] FunctionDef - 0,0..0,24
    .name 'f'
    .args arguments - 0,6..0,17
      .vararg arg - 0,7..0,10
        .arg 'new'
      .kwonlyargs[1]
      0] arg - 0,12..0,13
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,15..0,16
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""def f(**d): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(*new, **d): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] FunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,6..0,15
      .vararg arg - 0,7..0,10
        .arg 'new'
      .kwarg arg - 0,14..0,15
        .arg 'd'
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""def f(b=(2), **d): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(b=(2), *new, **d): pass""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] FunctionDef - 0,0..0,29
    .name 'f'
    .args arguments - 0,6..0,22
      .args[1]
      0] arg - 0,6..0,7
        .arg 'b'
      .vararg arg - 0,14..0,17
        .arg 'new'
      .kwarg arg - 0,21..0,22
        .arg 'd'
      .defaults[1]
      0] Constant 2 - 0,9..0,10
    .body[1]
    0] Pass - 0,25..0,29
"""),

(r"""def f(b=(2)): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(b=(2), *new): pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] FunctionDef - 0,0..0,24
    .name 'f'
    .args arguments - 0,6..0,17
      .args[1]
      0] arg - 0,6..0,7
        .arg 'b'
      .vararg arg - 0,14..0,17
        .arg 'new'
      .defaults[1]
      0] Constant 2 - 0,9..0,10
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""def f(b=(2),): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(b=(2), *new,): pass""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] FunctionDef - 0,0..0,25
    .name 'f'
    .args arguments - 0,6..0,18
      .args[1]
      0] arg - 0,6..0,7
        .arg 'b'
      .vararg arg - 0,14..0,17
        .arg 'new'
      .defaults[1]
      0] Constant 2 - 0,9..0,10
    .body[1]
    0] Pass - 0,21..0,25
"""),

(r"""def f(b): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(b, *new): pass""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] FunctionDef - 0,0..0,20
    .name 'f'
    .args arguments - 0,6..0,13
      .args[1]
      0] arg - 0,6..0,7
        .arg 'b'
      .vararg arg - 0,10..0,13
        .arg 'new'
    .body[1]
    0] Pass - 0,16..0,20
"""),

(r"""def f(a=(3), /): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(a=(3), /, *new): pass""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] FunctionDef - 0,0..0,27
    .name 'f'
    .args arguments - 0,6..0,20
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .vararg arg - 0,17..0,20
        .arg 'new'
      .defaults[1]
      0] Constant 3 - 0,9..0,10
    .body[1]
    0] Pass - 0,23..0,27
"""),

(r"""def f(a, /): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(a, /, *new): pass""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] FunctionDef - 0,0..0,23
    .name 'f'
    .args arguments - 0,6..0,16
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .vararg arg - 0,13..0,16
        .arg 'new'
    .body[1]
    0] Pass - 0,19..0,23
"""),

(r"""def f(): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(*new): pass""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] FunctionDef - 0,0..0,17
    .name 'f'
    .args arguments - 0,6..0,10
      .vararg arg - 0,7..0,10
        .arg 'new'
    .body[1]
    0] Pass - 0,13..0,17
"""),

(r"""def f(b=(2), *, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(b=(2), *new, c=(1)): pass""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] FunctionDef - 0,0..0,31
    .name 'f'
    .args arguments - 0,6..0,24
      .args[1]
      0] arg - 0,6..0,7
        .arg 'b'
      .vararg arg - 0,14..0,17
        .arg 'new'
      .kwonlyargs[1]
      0] arg - 0,19..0,20
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,22..0,23
      .defaults[1]
      0] Constant 2 - 0,9..0,10
    .body[1]
    0] Pass - 0,27..0,31
"""),

(r"""def f(a=(1), /, *, c=(1)): pass""", 'body[0].args', None, 'vararg', {}, r"""new""", r"""def f(a=(1), /, *new, c=(1)): pass""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] FunctionDef - 0,0..0,34
    .name 'f'
    .args arguments - 0,6..0,27
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .vararg arg - 0,17..0,20
        .arg 'new'
      .kwonlyargs[1]
      0] arg - 0,22..0,23
        .arg 'c'
      .kw_defaults[1]
      0] Constant 1 - 0,25..0,26
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,30..0,34
"""),

(r"""lambda *, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda *new, c=(1): None""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] Expr - 0,0..0,24
    .value Lambda - 0,0..0,24
      .args arguments - 0,7..0,18
        .vararg arg - 0,8..0,11
          .arg 'new'
        .kwonlyargs[1]
        0] arg - 0,13..0,14
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,16..0,17
      .body Constant None - 0,20..0,24
"""),

(r"""lambda **d: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda *new, **d: None""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value Lambda - 0,0..0,22
      .args arguments - 0,7..0,16
        .vararg arg - 0,8..0,11
          .arg 'new'
        .kwarg arg - 0,15..0,16
          .arg 'd'
      .body Constant None - 0,18..0,22
"""),

(r"""lambda b=(2), **d: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda b=(2), *new, **d: None""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] Expr - 0,0..0,29
    .value Lambda - 0,0..0,29
      .args arguments - 0,7..0,23
        .args[1]
        0] arg - 0,7..0,8
          .arg 'b'
        .vararg arg - 0,15..0,18
          .arg 'new'
        .kwarg arg - 0,22..0,23
          .arg 'd'
        .defaults[1]
        0] Constant 2 - 0,10..0,11
      .body Constant None - 0,25..0,29
"""),

(r"""lambda b=(2): None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda b=(2), *new: None""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] Expr - 0,0..0,24
    .value Lambda - 0,0..0,24
      .args arguments - 0,7..0,18
        .args[1]
        0] arg - 0,7..0,8
          .arg 'b'
        .vararg arg - 0,15..0,18
          .arg 'new'
        .defaults[1]
        0] Constant 2 - 0,10..0,11
      .body Constant None - 0,20..0,24
"""),

(r"""lambda b=(2),: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda b=(2), *new,: None""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] Expr - 0,0..0,25
    .value Lambda - 0,0..0,25
      .args arguments - 0,7..0,19
        .args[1]
        0] arg - 0,7..0,8
          .arg 'b'
        .vararg arg - 0,15..0,18
          .arg 'new'
        .defaults[1]
        0] Constant 2 - 0,10..0,11
      .body Constant None - 0,21..0,25
"""),

(r"""lambda b: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda b, *new: None""", r"""
Module - ROOT 0,0..0,20
  .body[1]
  0] Expr - 0,0..0,20
    .value Lambda - 0,0..0,20
      .args arguments - 0,7..0,14
        .args[1]
        0] arg - 0,7..0,8
          .arg 'b'
        .vararg arg - 0,11..0,14
          .arg 'new'
      .body Constant None - 0,16..0,20
"""),

(r"""lambda a=(2), /: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda a=(2), /, *new: None""", r"""
Module - ROOT 0,0..0,27
  .body[1]
  0] Expr - 0,0..0,27
    .value Lambda - 0,0..0,27
      .args arguments - 0,7..0,21
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .vararg arg - 0,18..0,21
          .arg 'new'
        .defaults[1]
        0] Constant 2 - 0,10..0,11
      .body Constant None - 0,23..0,27
"""),

(r"""lambda a, /: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda a, /, *new: None""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] Expr - 0,0..0,23
    .value Lambda - 0,0..0,23
      .args arguments - 0,7..0,17
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .vararg arg - 0,14..0,17
          .arg 'new'
      .body Constant None - 0,19..0,23
"""),

(r"""lambda a, /: None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda a, /, *new: None""", r"""
Module - ROOT 0,0..0,23
  .body[1]
  0] Expr - 0,0..0,23
    .value Lambda - 0,0..0,23
      .args arguments - 0,7..0,17
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .vararg arg - 0,14..0,17
          .arg 'new'
      .body Constant None - 0,19..0,23
"""),

(r"""lambda b=(2), *, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda b=(2), *new, c=(1): None""", r"""
Module - ROOT 0,0..0,31
  .body[1]
  0] Expr - 0,0..0,31
    .value Lambda - 0,0..0,31
      .args arguments - 0,7..0,25
        .args[1]
        0] arg - 0,7..0,8
          .arg 'b'
        .vararg arg - 0,15..0,18
          .arg 'new'
        .kwonlyargs[1]
        0] arg - 0,20..0,21
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,23..0,24
        .defaults[1]
        0] Constant 2 - 0,10..0,11
      .body Constant None - 0,27..0,31
"""),

(r"""lambda a=(1), /, *, c=(1): None""", 'body[0].value.args', None, 'vararg', {}, r"""new""", r"""lambda a=(1), /, *new, c=(1): None""", r"""
Module - ROOT 0,0..0,34
  .body[1]
  0] Expr - 0,0..0,34
    .value Lambda - 0,0..0,34
      .args arguments - 0,7..0,28
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .vararg arg - 0,18..0,21
          .arg 'new'
        .kwonlyargs[1]
        0] arg - 0,23..0,24
          .arg 'c'
        .kw_defaults[1]
        0] Constant 1 - 0,26..0,27
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,30..0,34
"""),

(r"""def f(**e): pass""", 'body[0].args', None, 'kwarg', {}, r"""**DEL**""", r"""def f(): pass""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] FunctionDef - 0,0..0,13
    .name 'f'
    .body[1]
    0] Pass - 0,9..0,13
"""),

(r"""def f(**e): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(**new): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] FunctionDef - 0,0..0,18
    .name 'f'
    .args arguments - 0,6..0,11
      .kwarg arg - 0,8..0,11
        .arg 'new'
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""def f(d=(1), **e): pass""", 'body[0].args', None, 'kwarg', {}, r"""**DEL**""", r"""def f(d=(1)): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] FunctionDef - 0,0..0,18
    .name 'f'
    .args arguments - 0,6..0,11
      .args[1]
      0] arg - 0,6..0,7
        .arg 'd'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""def f(d=(1), **e): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(d=(1), **new): pass""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] FunctionDef - 0,0..0,25
    .name 'f'
    .args arguments - 0,6..0,18
      .args[1]
      0] arg - 0,6..0,7
        .arg 'd'
      .kwarg arg - 0,15..0,18
        .arg 'new'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,21..0,25
"""),

(r"""def f(*c, **e): pass""", 'body[0].args', None, 'kwarg', {}, r"""**DEL**""", r"""def f(*c): pass""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] FunctionDef - 0,0..0,15
    .name 'f'
    .args arguments - 0,6..0,8
      .vararg arg - 0,7..0,8
        .arg 'c'
    .body[1]
    0] Pass - 0,11..0,15
"""),

(r"""def f(*c, **e): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(*c, **new): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] FunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,6..0,15
      .vararg arg - 0,7..0,8
        .arg 'c'
      .kwarg arg - 0,12..0,15
        .arg 'new'
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""def f(a, /, **e): pass""", 'body[0].args', None, 'kwarg', {}, r"""**DEL**""", r"""def f(a, /): pass""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] FunctionDef - 0,0..0,17
    .name 'f'
    .args arguments - 0,6..0,10
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
    .body[1]
    0] Pass - 0,13..0,17
"""),

(r"""def f(a=(2), /, **e): pass""", 'body[0].args', None, 'kwarg', {}, r"""**DEL**""", r"""def f(a=(2), /): pass""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] FunctionDef - 0,0..0,21
    .name 'f'
    .args arguments - 0,6..0,14
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .defaults[1]
      0] Constant 2 - 0,9..0,10
    .body[1]
    0] Pass - 0,17..0,21
"""),

(r"""def f(a: int, /, **e): pass""", 'body[0].args', None, 'kwarg', {}, r"""**DEL**""", r"""def f(a: int, /): pass""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] FunctionDef - 0,0..0,22
    .name 'f'
    .args arguments - 0,6..0,15
      .posonlyargs[1]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'int' Load - 0,9..0,12
    .body[1]
    0] Pass - 0,18..0,22
"""),

(r"""def f(a, /, **e): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(a, /, **new): pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] FunctionDef - 0,0..0,24
    .name 'f'
    .args arguments - 0,6..0,17
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .kwarg arg - 0,14..0,17
        .arg 'new'
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""lambda **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""**DEL**""", r"""lambda: None""", r"""
Module - ROOT 0,0..0,12
  .body[1]
  0] Expr - 0,0..0,12
    .value Lambda - 0,0..0,12
      .body Constant None - 0,8..0,12
"""),

(r"""lambda **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda **new: None""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Expr - 0,0..0,18
    .value Lambda - 0,0..0,18
      .args arguments - 0,7..0,12
        .kwarg arg - 0,9..0,12
          .arg 'new'
      .body Constant None - 0,14..0,18
"""),

(r"""lambda d=(1), **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""**DEL**""", r"""lambda d=(1): None""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Expr - 0,0..0,18
    .value Lambda - 0,0..0,18
      .args arguments - 0,7..0,12
        .args[1]
        0] arg - 0,7..0,8
          .arg 'd'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,14..0,18
"""),

(r"""lambda d=(1), **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda d=(1), **new: None""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] Expr - 0,0..0,25
    .value Lambda - 0,0..0,25
      .args arguments - 0,7..0,19
        .args[1]
        0] arg - 0,7..0,8
          .arg 'd'
        .kwarg arg - 0,16..0,19
          .arg 'new'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,21..0,25
"""),

(r"""lambda *c, **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""**DEL**""", r"""lambda *c: None""", r"""
Module - ROOT 0,0..0,15
  .body[1]
  0] Expr - 0,0..0,15
    .value Lambda - 0,0..0,15
      .args arguments - 0,7..0,9
        .vararg arg - 0,8..0,9
          .arg 'c'
      .body Constant None - 0,11..0,15
"""),

(r"""lambda *c, **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda *c, **new: None""", r"""
Module - ROOT 0,0..0,22
  .body[1]
  0] Expr - 0,0..0,22
    .value Lambda - 0,0..0,22
      .args arguments - 0,7..0,16
        .vararg arg - 0,8..0,9
          .arg 'c'
        .kwarg arg - 0,13..0,16
          .arg 'new'
      .body Constant None - 0,18..0,22
"""),

(r"""lambda a, /, **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""**DEL**""", r"""lambda a, /: None""", r"""
Module - ROOT 0,0..0,17
  .body[1]
  0] Expr - 0,0..0,17
    .value Lambda - 0,0..0,17
      .args arguments - 0,7..0,11
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
      .body Constant None - 0,13..0,17
"""),

(r"""lambda a=(2), /, **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""**DEL**""", r"""lambda a=(2), /: None""", r"""
Module - ROOT 0,0..0,21
  .body[1]
  0] Expr - 0,0..0,21
    .value Lambda - 0,0..0,21
      .args arguments - 0,7..0,15
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .defaults[1]
        0] Constant 2 - 0,10..0,11
      .body Constant None - 0,17..0,21
"""),

(r"""lambda a, /, **e: None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda a, /, **new: None""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] Expr - 0,0..0,24
    .value Lambda - 0,0..0,24
      .args arguments - 0,7..0,18
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .kwarg arg - 0,15..0,18
          .arg 'new'
      .body Constant None - 0,20..0,24
"""),

(r"""def f(): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(**new): pass""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] FunctionDef - 0,0..0,18
    .name 'f'
    .args arguments - 0,6..0,11
      .kwarg arg - 0,8..0,11
        .arg 'new'
    .body[1]
    0] Pass - 0,14..0,18
"""),

(r"""def f(c=(1)): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(c=(1), **new): pass""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] FunctionDef - 0,0..0,25
    .name 'f'
    .args arguments - 0,6..0,18
      .args[1]
      0] arg - 0,6..0,7
        .arg 'c'
      .kwarg arg - 0,15..0,18
        .arg 'new'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,21..0,25
"""),

(r"""def f(c=(1),): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(c=(1), **new): pass""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] FunctionDef - 0,0..0,25
    .name 'f'
    .args arguments - 0,6..0,18
      .args[1]
      0] arg - 0,6..0,7
        .arg 'c'
      .kwarg arg - 0,15..0,18
        .arg 'new'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,21..0,25
"""),

(r"""def f(a=(1), /): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(a=(1), /, **new): pass""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] FunctionDef - 0,0..0,28
    .name 'f'
    .args arguments - 0,6..0,21
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .kwarg arg - 0,18..0,21
        .arg 'new'
      .defaults[1]
      0] Constant 1 - 0,9..0,10
    .body[1]
    0] Pass - 0,24..0,28
"""),

(r"""def f(a: int, /): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(a: int, /, **new): pass""", r"""
Module - ROOT 0,0..0,29
  .body[1]
  0] FunctionDef - 0,0..0,29
    .name 'f'
    .args arguments - 0,6..0,22
      .posonlyargs[1]
      0] arg - 0,6..0,12
        .arg 'a'
        .annotation Name 'int' Load - 0,9..0,12
      .kwarg arg - 0,19..0,22
        .arg 'new'
    .body[1]
    0] Pass - 0,25..0,29
"""),

(r"""def f(a, /): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(a, /, **new): pass""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] FunctionDef - 0,0..0,24
    .name 'f'
    .args arguments - 0,6..0,17
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .kwarg arg - 0,14..0,17
        .arg 'new'
    .body[1]
    0] Pass - 0,20..0,24
"""),

(r"""def f(a, /, ): pass""", 'body[0].args', None, 'kwarg', {}, r"""new""", r"""def f(a, /, **new ): pass""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] FunctionDef - 0,0..0,25
    .name 'f'
    .args arguments - 0,6..0,17
      .posonlyargs[1]
      0] arg - 0,6..0,7
        .arg 'a'
      .kwarg arg - 0,14..0,17
        .arg 'new'
    .body[1]
    0] Pass - 0,21..0,25
"""),

(r"""lambda: None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda **new: None""", r"""
Module - ROOT 0,0..0,18
  .body[1]
  0] Expr - 0,0..0,18
    .value Lambda - 0,0..0,18
      .args arguments - 0,7..0,12
        .kwarg arg - 0,9..0,12
          .arg 'new'
      .body Constant None - 0,14..0,18
"""),

(r"""lambda c=(1): None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda c=(1), **new: None""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] Expr - 0,0..0,25
    .value Lambda - 0,0..0,25
      .args arguments - 0,7..0,19
        .args[1]
        0] arg - 0,7..0,8
          .arg 'c'
        .kwarg arg - 0,16..0,19
          .arg 'new'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,21..0,25
"""),

(r"""lambda c=(1),: None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda c=(1), **new: None""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] Expr - 0,0..0,25
    .value Lambda - 0,0..0,25
      .args arguments - 0,7..0,19
        .args[1]
        0] arg - 0,7..0,8
          .arg 'c'
        .kwarg arg - 0,16..0,19
          .arg 'new'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,21..0,25
"""),

(r"""lambda a=(1), /: None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda a=(1), /, **new: None""", r"""
Module - ROOT 0,0..0,28
  .body[1]
  0] Expr - 0,0..0,28
    .value Lambda - 0,0..0,28
      .args arguments - 0,7..0,22
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .kwarg arg - 0,19..0,22
          .arg 'new'
        .defaults[1]
        0] Constant 1 - 0,10..0,11
      .body Constant None - 0,24..0,28
"""),

(r"""lambda a, /: None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda a, /, **new: None""", r"""
Module - ROOT 0,0..0,24
  .body[1]
  0] Expr - 0,0..0,24
    .value Lambda - 0,0..0,24
      .args arguments - 0,7..0,18
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .kwarg arg - 0,15..0,18
          .arg 'new'
      .body Constant None - 0,20..0,24
"""),

(r"""lambda a, /, : None""", 'body[0].value.args', None, 'kwarg', {}, r"""new""", r"""lambda a, /, **new : None""", r"""
Module - ROOT 0,0..0,25
  .body[1]
  0] Expr - 0,0..0,25
    .value Lambda - 0,0..0,25
      .args arguments - 0,7..0,18
        .posonlyargs[1]
        0] arg - 0,7..0,8
          .arg 'a'
        .kwarg arg - 0,15..0,18
          .arg 'new'
      .body Constant None - 0,21..0,25
"""),

(r"""f'{-0.:.1f}'""", 'body[0].value.values[0].value', None, 'operand', {'_ver': 12}, r"""0.0""", r"""f'{-0.0:.1f}'""", r"""
Module - ROOT 0,0..0,13
  .body[1]
  0] Expr - 0,0..0,13
    .value JoinedStr - 0,0..0,13
      .values[1]
      0] FormattedValue - 0,2..0,12
        .value UnaryOp - 0,3..0,7
          .op USub - 0,3..0,4
          .operand Constant 0.0 - 0,4..0,7
        .conversion -1
        .format_spec JoinedStr - 0,7..0,11
          .values[1]
          0] Constant '.1f' - 0,8..0,11
"""),

]  # END OF PUT_ONE_DATA
