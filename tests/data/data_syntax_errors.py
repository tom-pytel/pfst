DATA_SYNTAX_ERRORS = {

('all', 'elif'): [
    '    elif',
    '    ^^^^',
    'SyntaxError: invalid syntax',
],

('all', 'else'): [
    '    else',
    '    ^^^^',
    'SyntaxError: invalid syntax',
],

('all', 'finally'): [
    '    finally',
    '    ^^^^^^^',
    'SyntaxError: invalid syntax',
],

('all', 'as'): [
    '    as',
    '    ^^',
    'SyntaxError: invalid syntax',
],

('strict', 'except Exception: pass\nexcept: pass'): [
    '    except Exception: pass',
    '    ^^^^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'case None: pass\ncase 1: pass'): [
    '    case None: pass',
    '         ^^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'except: pass'): [
    '    except: pass',
    '    ^^^^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'case None: pass'): [
    '    case None: pass',
    '         ^^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'except Exception: pass\nexcept: pass'): [
    '    except Exception: pass',
    '    ^^^^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'except: pass'): [
    '    except: pass',
    '    ^^^^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'case None: pass\ncase 1: pass'): [
    '    case None: pass',
    '         ^^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'case None: pass'): [
    '    case None: pass',
    '         ^^^^',
    'SyntaxError: invalid syntax',
],

('strict', '*not a'): [
    '    *not a',
    '     ^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'a:b:c'): [
    '    a:b:c',
    '       ^',
    'SyntaxError: invalid syntax',
],

('strict', '1 as a'): [
    '    1 as a',
    '      ^^',
    'SyntaxError: invalid syntax',
],

('strict', 'a: list[str], /, b: int = 1, *c, d=100, **e'): [
    '    a: list[str], /, b: int = 1, *c, d=100, **e',
    '                ^',
    'SyntaxError: invalid syntax',
],

('strict', 'a, /, b, *c, d=100, **e'): [
    '    a, /, b, *c, d=100, **e',
    '       ^',
    'SyntaxError: invalid syntax',
],

('strict', '*not a'): [
    '    *not a',
    '     ^^^',
    'SyntaxError: invalid syntax',
],

('strict', 'for i in range(5) if i'): [
    '    for i in range(5) if i',
    '             ^^^^^^^^^^^^^',
    "SyntaxError: expected 'else' after 'if' expression",
],

('strict', 'f(**a) as b'): [
    '    f(**a) as b',
    '           ^^',
    'SyntaxError: invalid syntax',
],

('strict', '*'): [
    '    *',
    '     ^',
    'SyntaxError: invalid syntax',
],

('strict', '*='): [
    '    *=',
    '    ^^',
    'SyntaxError: invalid syntax',
],

('strict', '>'): [
    '    >',
    '    ^',
    'SyntaxError: invalid syntax',
],

('strict', 'and'): [
    '    and',
    '    ^^^',
    'SyntaxError: invalid syntax',
],

('strict', '~'): [
    '    ~',
    '     ^',
    'SyntaxError: invalid syntax',
],

('eval', '#'): [
    '    #',
    'SyntaxError: invalid syntax',
],

('single', '#'): [
    '    #',
    'SyntaxError: invalid syntax',
],

('stmts', 'except Exception: pass\nexcept: pass'): [
    '    except Exception: pass',
    '    ^^^^^^',
    'SyntaxError: invalid syntax',
],

('stmt', 'except: pass'): [
    '    except: pass',
    '    ^^^^^^',
    'SyntaxError: invalid syntax',
],

('_ExceptHandlers', 'i: int = 1\nj'): [
    '    i: int = 1',
    '    ^',
    "SyntaxError: expected 'except' or 'finally' block",
],

('ExceptHandler', 'else: pass'): [
    '    else: pass',
    '    ^^^^',
    "SyntaxError: expected 'except' or 'finally' block",
],

('ExceptHandler', 'i: int = 1'): [
    '    i: int = 1',
    '    ^',
    "SyntaxError: expected 'except' or 'finally' block",
],

('_match_cases', 'i: int = 1'): [
    '    i: int = 1',
    '    ^',
    'SyntaxError: invalid syntax',
],

('match_case', 'i: int = 1'): [
    '    i: int = 1',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_Assign_targets', '#'): [
    '    #\\',
    '    ^^',
    'SyntaxError: invalid syntax',
],

('_Assign_targets', '\n\na'): [
    '',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_Assign_targets', 'a\n='): [
    '    =\\',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_Assign_targets', 'a =  # tail'): [
    '    a =  # tail\\',
    '         ^^^^^^^',
    'SyntaxError: invalid syntax',
],

('_Assign_targets', '# head\na ='): [
    '    # head',
    '    ^^^^^^',
    'SyntaxError: invalid syntax',
],

('_Assign_targets', 'f()'): [
    '    f()\\',
    '    ^^^',
    'SyntaxError: cannot assign to function call',
],

('_Assign_targets', 'pass'): [
    '    pass\\',
    '    ^^^^',
    'SyntaxError: invalid syntax',
],

('_Assign_targets', 'a; b'): [
    'SyntaxError: invalid Assign targets slice',
],

('_decorator_list', 'pass'): [
    'SyntaxError: unexpected multiple statements',
],

('_decorator_list', 'f()'): [
    'SyntaxError: unexpected multiple statements',
],

('expr', '*not a'): [
    '    *not a',
    '     ^^^',
    'SyntaxError: invalid syntax',
],

('expr', '*not a'): [
    '    *not a',
    '     ^^^',
    'SyntaxError: invalid syntax',
],

('expr', 'a:b'): [
    '    a:b',
    '     ^',
    'SyntaxError: invalid syntax',
],

('expr', 'a:b:c'): [
    '    a:b:c',
    '     ^',
    'SyntaxError: invalid syntax',
],

('expr', 'i for i in j'): [
    'SyntaxError: expecting expression, got unparenthesized GeneratorExp',
],

('expr', '* *a'): [
    '    * *a',
    '      ^',
    'SyntaxError: Invalid star expression',
],

('expr', 'pass'): [
    'SyntaxError: invalid expression (standard)',
],

('expr', '#'): [
    'SyntaxError: expecting expression, got nothing',
],

('expr', ''): [
    'SyntaxError: expecting expression, got nothing',
],

('expr_all', '* *a'): [
    '    * *a',
    '      ^',
    'SyntaxError: Invalid star expression',
],

('expr_all', 'pass'): [
    '    pass',
    '    ^^^^',
    'SyntaxError: invalid syntax',
],

('expr_all', '#'): [
    'SyntaxError: invalid expression (all types)',
],

('expr_all', ''): [
    'SyntaxError: invalid expression (all types)',
],

('expr_arglike', '*not a,'): [
    '    *not a,',
    '     ^^^',
    'SyntaxError: invalid syntax',
],

('expr_arglike', 'a:b'): [
    '    a:b',
    '     ^',
    'SyntaxError: invalid syntax',
],

('expr_arglike', 'a:b:c'): [
    '    a:b:c',
    '     ^',
    'SyntaxError: invalid syntax',
],

('expr_arglike', '* *a'): [
    '    * *a',
    '      ^',
    'SyntaxError: Invalid star expression',
],

('expr_arglike', 'pass'): [
    '    pass',
    '    ^^^^',
    'SyntaxError: invalid syntax',
],

('expr_arglike', '#'): [
    'SyntaxError: invalid expression (arglike)',
],

('expr_arglike', ''): [
    'SyntaxError: invalid expression (arglike)',
],

('_expr_arglikes', 'a:b'): [
    'SyntaxError: invalid expression(s) (arglike)',
],

('_expr_arglikes', 'a:b:c'): [
    'SyntaxError: invalid expression(s) (arglike)',
],

('expr_slice', ''): [
    'SyntaxError: expecting expression (slice), got nothing',
],

('expr_slice', 'i for i in j'): [
    'SyntaxError: expecting expression (slice), got unparenthesized GeneratorExp',
],

('expr_slice', '* *a'): [
    '    * *a',
    '      ^',
    'SyntaxError: Invalid star expression',
],

('expr_slice', 'pass'): [
    '    pass',
    '    ^^^^',
    'SyntaxError: invalid syntax',
],

('expr_slice', '#'): [
    'SyntaxError: expecting expression (slice), got nothing',
],

('expr_slice', ''): [
    'SyntaxError: expecting expression (slice), got nothing',
],

('Tuple_elt', 'a:b:c, x:y:z'): [
    '    a:b:c, x:y:z',
    '     ^',
    'SyntaxError: invalid syntax',
],

('Tuple_elt', '* *a'): [
    '    * *a',
    '      ^',
    'SyntaxError: Invalid star expression',
],

('Tuple_elt', 'pass'): [
    'SyntaxError: invalid expression (standard)',
],

('Tuple_elt', '#'): [
    'SyntaxError: expecting expression, got nothing',
],

('Tuple_elt', ''): [
    'SyntaxError: expecting expression, got nothing',
],

('Tuple', '~'): [
    '    ~',
    '     ^',
    'SyntaxError: invalid syntax',
],

('Tuple', '* *a'): [
    '    * *a',
    '      ^',
    'SyntaxError: Invalid star expression',
],

('Tuple', 'pass'): [
    '    pass',
    '    ^^^^',
    'SyntaxError: invalid syntax',
],

('Tuple', '#'): [
    'SyntaxError: invalid tuple',
],

('Tuple', ''): [
    'SyntaxError: invalid tuple',
],

('_arglike', 'a=b, c'): [
    'SyntaxError: invalid arglike',
],

('_arglike', '**a, *b'): [
    '    **a, *b',
    '       ^^^^',
    'SyntaxError: iterable argument unpacking follows keyword argument unpacking',
],

('_arglike', 'a:b'): [
    '    a:b',
    '     ^',
    'SyntaxError: invalid syntax',
],

('_arglike', 'a:b:c'): [
    '    a:b:c',
    '     ^',
    'SyntaxError: invalid syntax',
],

('_arglikes', 'a=b, c'): [
    'SyntaxError: invalid arglikes',
],

('_arglikes', '**a, *b'): [
    '    **a, *b',
    '       ^^^^',
    'SyntaxError: iterable argument unpacking follows keyword argument unpacking',
],

('_arglikes', 'a:b'): [
    '    a:b',
    '     ^',
    'SyntaxError: invalid syntax',
],

('_arglikes', 'a:b:c'): [
    '    a:b:c',
    '     ^',
    'SyntaxError: invalid syntax',
],

('boolop', 'and 1'): [
    "SyntaxError: unexpected code after boolop, '1'",
],

('boolop', '*'): [
    "SyntaxError: expecting boolop, got '*'",
],

('boolop', ''): [
    'SyntaxError: expecting boolop, got nothing',
],

('operator', '* 1'): [
    "SyntaxError: unexpected code after operator, '1'",
],

('operator', '*='): [
    "SyntaxError: expecting operator, got '*='",
],

('operator', 'and'): [
    "SyntaxError: expecting operator, got 'and'",
],

('operator', ''): [
    'SyntaxError: expecting operator, got nothing',
],

('unaryop', '+ 1'): [
    "SyntaxError: unexpected code after unaryop, '1'",
],

('unaryop', 'and'): [
    "SyntaxError: expecting unaryop, got 'and'",
],

('unaryop', ''): [
    'SyntaxError: expecting unaryop, got nothing',
],

('cmpop', '+='): [
    "SyntaxError: expecting cmpop, got '+='",
],

('cmpop', '>= a >='): [
    "SyntaxError: unexpected code after cmpop, 'a'",
],

('cmpop', 'and'): [
    "SyntaxError: expecting cmpop, got 'and'",
],

('cmpop', ''): [
    'SyntaxError: expecting cmpop, got nothing',
],

('_comprehension_ifs', 'if 1 else 2'): [
    '    if 1 else 2',
    '         ^^^^',
    'SyntaxError: invalid syntax',
],

('arguments_lambda', 'a: list[str], /, b: int = 1, *c, d=100, **e'): [
    '    a: list[str], /, b: int = 1, *c, d=100, **e',
    '                  ^',
    'SyntaxError: invalid syntax',
],

('arg', ','): [
    '    ,',
    '    ^',
    'SyntaxError: invalid syntax',
],

('arg', ')'): [
    'SyntaxError: invalid arg',
],

('alias', ''): [
    '',
    '    ^',
    "SyntaxError: Expected one or more names after 'import'",
],

('alias', '* as c'): [
    '    * as c',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_aliases', '* as c'): [
    '    * as c',
    '    ^',
    'SyntaxError: invalid syntax',
],

('Import_name', ''): [
    '',
    '    ^',
    "SyntaxError: Expected one or more names after 'import'",
],

('Import_name', '*'): [
    '    *',
    '    ^',
    'SyntaxError: invalid syntax',
],

('Import_name', '* as c'): [
    '    * as c',
    '    ^',
    'SyntaxError: invalid syntax',
],

('Import_name', '(a)'): [
    '    (a)',
    '    ^',
    'SyntaxError: invalid syntax',
],

('Import_name', ')'): [
    '    )',
    '    ^',
    "SyntaxError: unmatched ')'",
],

('Import_name', ','): [
    '    ,',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_Import_names', '*'): [
    '    *',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_Import_names', '* as c'): [
    '    * as c',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_Import_names', '(a, b)'): [
    '    (a, b)',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_Import_names', ')'): [
    '    )',
    '    ^',
    "SyntaxError: unmatched ')'",
],

('_Import_names', ','): [
    '    ,',
    '    ^',
    'SyntaxError: invalid syntax',
],

('ImportFrom_name', ''): [
    '',
    '    ^',
    "SyntaxError: Expected one or more names after 'import'",
],

('ImportFrom_name', 'a.b'): [
    '    a.b',
    '     ^',
    'SyntaxError: invalid syntax',
],

('ImportFrom_name', 'a.b as c'): [
    '    a.b as c',
    '     ^',
    'SyntaxError: invalid syntax',
],

('ImportFrom_name', '* as c'): [
    '    * as c',
    '      ^^',
    'SyntaxError: invalid syntax',
],

('ImportFrom_name', 'a as x, a.b as y'): [
    '    a as x, a.b as y',
    '             ^',
    'SyntaxError: invalid syntax',
],

('ImportFrom_name', '(a)'): [
    'SyntaxError: ImportFrom.names cannot have explicit parentheses',
],

('ImportFrom_name', ')'): [
    '    )',
    '    ^',
    "SyntaxError: unmatched ')'",
],

('ImportFrom_name', ','): [
    '    ,',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_ImportFrom_names', 'a.b'): [
    '    a.b',
    '     ^',
    'SyntaxError: invalid syntax',
],

('_ImportFrom_names', 'a.b as c'): [
    '    a.b as c',
    '     ^',
    'SyntaxError: invalid syntax',
],

('_ImportFrom_names', '* as c'): [
    '    * as c',
    '      ^^',
    'SyntaxError: invalid syntax',
],

('_ImportFrom_names', 'a as x, a.b as y'): [
    '    a as x, a.b as y',
    '             ^',
    'SyntaxError: invalid syntax',
],

('_ImportFrom_names', '(a, b)'): [
    'SyntaxError: ImportFrom.names cannot have explicit parentheses',
],

('_ImportFrom_names', ')'): [
    '    )',
    '    ^',
    "SyntaxError: unmatched ')'",
],

('_ImportFrom_names', ','): [
    '    ,',
    '    ^',
    'SyntaxError: invalid syntax',
],

('withitem', ''): [
    'SyntaxError: expecting withitem, got nothing',
],

('withitem', '(a as b)'): [
    '    (a as b)',
    '       ^^',
    'SyntaxError: invalid syntax',
],

('withitem', '(a as b, x as y)'): [
    '    (a as b, x as y)',
    '       ^^',
    'SyntaxError: invalid syntax',
],

('withitem', ')'): [
    '    ): pass',
    '    ^',
    "SyntaxError: unmatched ')'",
],

('withitem', ','): [
    '    ,',
    '    ^',
    'SyntaxError: invalid syntax',
],

('_withitems', '(a as b)'): [
    '    (a as b)',
    '       ^^',
    'SyntaxError: invalid syntax',
],

('_withitems', '(a as b, x as y)'): [
    '    (a as b, x as y)',
    '       ^^',
    'SyntaxError: invalid syntax',
],

('_withitems', 'i for i in j'): [
    'SyntaxError: expecting withitems, got unparenthesized GeneratorExp',
],

('_withitems', ')'): [
    '    ): pass',
    '    ^',
    "SyntaxError: unmatched ')'",
],

('_withitems', ','): [
    '    ,',
    '    ^',
    'SyntaxError: invalid syntax',
],

('pattern', ''): [
    'SyntaxError: empty pattern',
],

('pattern', ')'): [
    '    ): pass',
    '    ^',
    "SyntaxError: unmatched ')'",
],

('pattern', ','): [
    '    ,',
    '    ^',
    'SyntaxError: invalid syntax',
],

('pattern', 'i: pass\n case 2'): [
    '    i: pass',
    '     ^',
    'SyntaxError: invalid syntax',
],

('Tuple_elt', '*not a, *b or c'): [
    '    *not a, *b or c',
    '     ^^^',
    'SyntaxError: invalid syntax',
],

('arg', 'a: *(,)'): [
    '    a: *(,)',
    '         ^',
    'SyntaxError: invalid syntax',
],

('arg', 'a: *+'): [
    '    a: *+',
    '       ^',
    'SyntaxError: invalid syntax',
],
}