DATA_GET = {
'test': [  # ................................................................................

(0, '', None, False, 'returns', {}, r'''
def f() -> int:
    pass
''', r'''
def f():
    pass
''', r'''
FunctionDef - ROOT 0,0..1,8
  .name 'f'
  .body[1]
  0] Pass - 1,4..1,8
''',
r'''int''',
r'''Name 'int' Load - ROOT 0,0..0,3'''),

(1, '', None, False, None, {},
r'''a = b''',
r'''**ValueError('cannot delete Assign.value')**''',
r'''b''',
r'''Name 'b' Load - ROOT 0,0..0,1'''),

(2, '', None, False, None, {},
"\ni = 'j'\n",
r'''**ValueError('cannot delete Assign.value')**''',
"\n'j'\n",
r'''Constant 'j' - ROOT 0,0..0,3'''),

(3, '', None, False, None, {},
'i = (j, \n"j"\n)',
r'''**ValueError('cannot delete Assign.value')**''',
'(j, \n"j"\n)', r'''
Tuple - ROOT 0,0..2,1
  .elts[2]
  0] Name 'j' Load - 0,1..0,2
  1] Constant 'j' - 1,0..1,3
  .ctx Load
'''),
],

}
